#!/usr/bin/env python3
"""
What people actually type, read from the engines themselves, with no account.

WHY THIS EXISTS
---------------
GOALS.md has said the same thing for a month: "What we still cannot see is
impressions and queries, and that needs Search Console, which is
OWNER-ACTIONS.md 1a." Half of that is true and half of it is not, and the
difference decides whether a cycle can do useful discovery work today.

Search Console is the only way to see OUR impressions: which of our pages were
shown, for what, and how often they were clicked. Nothing here replaces that,
and this file does not try to.

But the other half, WHAT PEOPLE TYPE, is public. Google and Bing both expose
their autocomplete endpoints without a key, without an account and without a
referrer check. That is the half that decides what to write, and we have never
once looked at it. Every search term this site targets was invented by reading
the Micro Zone Manual, which is why 115 pages carry internal vocabulary like
"coats and outerwear" and "landing zone" while the suggestion list for the same
room is full of "cubbies", "lockers", "small mudroom" and "shoes".

This tool harvests those suggestions for every room and zone in the real
corpus, then asks one question of each: do we have a page for this, and does
its title use these words?

WHAT THIS DATA IS, AND WHAT IT IS NOT
-------------------------------------
It is NOT search volume. Nothing here reports a number of searches per month
and nothing here may be presented as one. An autocomplete suggestion proves
only that an engine considers the phrase a likely completion, which means real
people type it often enough to be worth predicting. That is weaker than volume
and much stronger than the nothing we have today.

The client=chrome response carries google:suggestrelevance, which orders the
suggestions against each other within one response. It is a relative rank
inside one seed result, not a cross-seed quantity, so this file keeps only the
rank (1 is the top suggestion) and refuses to add relevance across seeds.
Summing them would produce a confident-looking number that means nothing, which
is the failure mode CLAUDE.md section 25 names.

HOW IT REFUSES TO LIE
---------------------
The dominant defect class in this repository is a check that could not fail,
and a harvester is an easy place to reproduce it: an engine that rate-limits
returns a valid, empty, HTTP 200 response, and a naive run would write
"0 gaps found" and exit 0. So:

  * every seed outcome is recorded individually as ok, empty or error
  * an empty 200 is NOT counted as a success, and NOT counted as a failure
    either. The first version of this file called it a failure, and the very
    first run proved that wrong: "why is my entryway always messy" genuinely
    has no completions, and calling that a failure would have voided an
    otherwise clean harvest. Blocking and a genuine zero look identical in one
    response, so they are told apart across the run instead
  * a CANARY seed with completions nobody doubts is fetched first and again
    last. If either canary comes back empty, the endpoint is answering 200
    with nothing and the whole run is void, however many other rows arrived
  * nothing is written if the error rate exceeds MAX_ERROR_RATE, or the empty
    rate exceeds MAX_EMPTY_RATE, or a canary is empty. A partial harvest must
    never overwrite a complete one, because the diff would read as
    "demand collapsed"
  * the output records checked_at, the sources, the seed count and the full
    failure list, so a reader can always tell what was not looked at

Run:  python ops/keyword_demand.py                 harvest Google, write outputs
      python ops/keyword_demand.py --source bing   harvest Bing instead
      python ops/keyword_demand.py --source both   harvest both, union the queries
      python ops/keyword_demand.py --dry-run       first 6 seeds only, write nothing
      python ops/keyword_demand.py --status        read the last harvest, write nothing
"""
import datetime
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CONTENT = os.path.join(ROOT, "mcp", "content.json")
ZONE_TERMS = os.path.join(ROOT, "ops", "zone-search-terms.json")
OUT_JSON = os.path.join(ROOT, "ops", "keyword-demand.json")
OUT_MD = os.path.join(ROOT, "ops", "KEYWORD-DEMAND.md")

# Polite by design. These endpoints are public but they are not ours, and a
# burst is how a client earns a block: the session that wrote this file lost
# DuckDuckGo for the rest of an hour by firing eight requests in twelve
# seconds, which is the whole reason the delay is here and not tunable.
DELAY = (0.9, 1.8)
TIMEOUT = 20
MAX_ERROR_RATE = 0.10
# Long complaint-style seeds often have no completions at all, so a high empty
# rate is normal. This ceiling is here to catch the other case: an endpoint
# that has started answering 200 with nothing for everything.
MAX_EMPTY_RATE = 0.50
# A phrase whose completions are not in doubt. If this one comes back empty we
# are being refused, whatever the rest of the run looks like.
CANARY = "how to organize a kitchen"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Four intents, because they are four different jobs and a room ranks for them
# separately: the how-to, the shopping-adjacent "ideas" phrasing, the
# decluttering entry point, and the complaint, which is how somebody searches
# before they know organising is the answer.
ROOM_TEMPLATES = (
    "how to organize a {room}",
    "{room} organization ideas",
    "how to declutter a {room}",
    "why is my {room} always messy",
)

# THE SEEDS DECIDE WHAT CAN BE FOUND, AND OURS CAME FROM OUR OWN VOCABULARY.
#
# Found 2026-10-01, after the first harvest. Every seed was built from the
# twenty room names in content.json plus the sixty hand-written zone search
# terms, so the harvest could only ever discover phrases that an engine
# suggests from words WE already use. "master bedroom" does not appear once in
# 2,622 queries, not because nobody types it, but because nothing asked. The
# same blind spot covers "foyer", "utility room", "den" and "larder".
#
# These are the probe seeds for that. They are not claims that anybody searches
# these phrases; they are the question, put to the engine, so the next harvest
# can answer it. Each is a word a household might use for a room this site
# names differently, and the thing worth reading in the result is whether the
# engine suggests MORE around the synonym than around our name for it.
VOCABULARY_PROBES = (
    "master bedroom organization",
    "master bathroom organization",
    "foyer organization ideas",
    "entrance hall organization",
    "utility room organization",
    "larder organization",
    "den organization ideas",
    "bonus room organization",
    "linen closet organization",
    "coat closet organization",
    "back porch organization",
    "basement organization ideas",
    "attic organization ideas",
    "walk in closet organization",
)

STOPWORDS = frozenset("""
a an and are at be best by can do does for from get good have how i ideas in
into is it its my of on or should so that the their there these this to too
what when where which who why will with you your
""".split())

# Words that describe the format of a query rather than its subject. Left out
# of coverage scoring because nearly every one of our titles carries one and
# the score would flatter itself.
FORMAT_WORDS = frozenset(("organize", "organizing", "organization", "organiser",
                          "organizer", "organizers", "organise", "organising"))


def room_names():
    with open(CONTENT, encoding="utf-8") as fh:
        data = json.load(fh)
    return [r["room"] for r in data["rooms"]]


def zone_terms():
    """The hand-written retailer search terms, reused as seeds.

    They were written for product search links, not for SEO, which is exactly
    what makes them useful here: they are the plain-English noun a person would
    reach for ("drop zone", "blanket storage") rather than the Manual internal
    zone name, so they seed the suggestion space from the human side.
    """
    if not os.path.exists(ZONE_TERMS):
        return []
    with open(ZONE_TERMS, encoding="utf-8") as fh:
        data = json.load(fh)
    seen, out = set(), []
    for term in data.values():
        t = str(term).strip().lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def build_seeds():
    seeds = []
    for room in room_names():
        low = room.lower()
        for tpl in ROOM_TEMPLATES:
            seeds.append(tpl.format(room=low))
    for term in zone_terms():
        seeds.append("how to organize " + term)
    seeds.extend(VOCABULARY_PROBES)
    # Deterministic order so two runs are comparable line by line.
    out, seen = [], set()
    for s in seeds:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def _parse_opensearch(body):
    """Both endpoints answer in the OpenSearch suggestions shape."""
    try:
        payload = json.loads(body)
    except ValueError:
        return None, "unparseable response"
    if not isinstance(payload, list) or len(payload) < 2:
        return None, "unexpected response shape"
    if not isinstance(payload[1], list):
        return None, "unexpected response shape"
    return [s for s in payload[1] if isinstance(s, str)], None


def google_suggest(seed):
    url = ("https://suggestqueries.google.com/complete/search"
           "?client=chrome&hl=en&gl=us&q=" + urllib.parse.quote(seed))
    try:
        status, body = _fetch(url)
    except Exception as exc:                      # reported, never hidden
        return [], "%s: %s" % (type(exc).__name__, exc)
    if status != 200:
        return [], "http %s" % status
    out, err = _parse_opensearch(body)
    return (out or []), err


def bing_suggest(seed):
    url = "https://api.bing.com/osjson.aspx?query=" + urllib.parse.quote(seed)
    try:
        status, body = _fetch(url)
    except Exception as exc:                      # reported, never hidden
        return [], "%s: %s" % (type(exc).__name__, exc)
    if status != 200:
        return [], "http %s" % status
    out, err = _parse_opensearch(body)
    return (out or []), err


SOURCES = {"google": google_suggest, "bing": bing_suggest}


def words(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w]


def content_words(query):
    """The words a coverage check should care about."""
    return [w for w in words(query)
            if w not in STOPWORDS and w not in FORMAT_WORDS and len(w) > 2]


def page_inventory():
    """Every published page as its title and its section headings.

    HEADINGS, ADDED 2026-10-01, AND WHY THEY ARE KEPT SEPARATE.

    The first reading scored a query against page titles only. That is the
    strictest reading and it understates real coverage in one specific way:
    a page can answer a question properly in an <h2> with its own id, which
    is a legitimate target for that query, and still score as a gap because
    the word is not in the title. The article shipped this same day is the
    example. It answers "why is my kitchen always messy" under exactly that
    heading, and reads as `partial` because its title says house.

    So headings are now read as well, and the two scores are kept APART
    rather than merged into one friendlier number. `coverage` stays
    title-only, so it is still comparable with the first reading, and the
    heading score is reported next to it with the surface that matched. A
    measurement that quietly got more generous would be the worse outcome
    here than one that was too strict.
    """
    rows = []
    for dirpath, _dirs, files in os.walk(SITE):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            if name.startswith("_") or name == "404.html":
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    whole = fh.read()
            except OSError:
                continue
            m = re.search(r"<title>(.*?)</title>", whole, re.S)
            if not m:
                continue
            title = re.sub(r"[ \n\t]+", " ", m.group(1)).strip()
            title = title.split("|")[0].strip()
            body = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", whole)
            heads = " ".join(
                re.sub(r"<[^>]+>", " ", h)
                for h in re.findall(r"(?is)<h[1-3][^>]*>(.*?)</h[1-3]>", body))
            rows.append({"url": "/" + os.path.relpath(path, SITE)
                                .replace(os.sep, "/"),
                         "title": title,
                         "words": set(words(title)),
                         "head_words": set(words(title + " " + heads))})
    return sorted(rows, key=lambda r: r["url"])


def best_page(query, inventory):
    """Best-matching page for a query, by share of its content words covered.

    Deliberately crude. It is a triage score for a human reading the report,
    not a ranking model, and the report says so: 1.0 means every meaningful
    word in the query appears in some page title, which is the weakest claim
    to coverage anybody can make without impression data.
    """
    cw = content_words(query)
    if not cw:
        return None, 0.0
    best, score = None, -1.0
    for page in inventory:
        hit = sum(1 for w in cw if w in page["words"])
        s = hit / len(cw)
        if s > score or (s == score and best is not None
                         and page["url"] < best["url"]):
            best, score = page, s
    return best, round(score, 3)


def classify(score):
    if score >= 0.999:
        return "covered"
    if score >= 0.5:
        return "partial"
    return "gap"


def attribute_room(query, rooms):
    """Which room a query belongs to, longest name first so Guest Bathroom
    wins over Bathroom and Kids Bedroom over Bedroom."""
    low = query.lower()
    for room in sorted(rooms, key=len, reverse=True):
        if room.lower() in low:
            return room
    return ""


def best_by(query, inventory, field):
    """Best-matching page for a query against one surface of the inventory."""
    cw = content_words(query)
    if not cw:
        return None, 0.0
    best, score = None, -1.0
    for page in inventory:
        hit = sum(1 for w in cw if w in page[field])
        s = hit / len(cw)
        if s > score or (s == score and best is not None
                         and page["url"] < best["url"]):
            best, score = page, s
    return best, round(score, 3)


def score_rows(results, rooms, inventory):
    rows = []
    for q in sorted(results):
        row = dict(results[q])
        page, score = best_page(q, inventory)
        hpage, hscore = best_by(q, inventory, "head_words")
        row["room"] = attribute_room(q, rooms)
        row["best_page"] = page["url"] if page else ""
        row["best_page_title"] = page["title"] if page else ""
        # Title-only, unchanged, so this column stays comparable with the
        # first reading taken before headings were read at all.
        row["coverage"] = score
        row["heading_coverage"] = hscore
        row["heading_page"] = hpage["url"] if hpage else ""
        # The status uses the better surface, because a question answered
        # under its own <h2> is genuinely answered, and names which surface
        # earned it so a reader can discount it if they disagree.
        row["matched_on"] = "title" if score >= hscore else "heading"
        row["status"] = classify(max(score, hscore))
        rows.append(row)
    return rows


def canary_ok(source, sleep=True):
    """Is this endpoint still answering with real content?

    Called before and after the harvest. An endpoint that has started refusing
    us returns a valid, empty, HTTP 200, which is indistinguishable from a
    genuine zero in any single response. It is distinguishable here, because
    this phrase has completions and always will.
    """
    suggestions, err = SOURCES[source](CANARY)
    if sleep:
        time.sleep(random.uniform(*DELAY))
    if err:
        return False, err
    if not suggestions:
        return False, "canary returned an empty 200: endpoint is refusing us"
    return True, ""


def harvest(sources, seeds, verbose=True, sleep=True):
    rooms = room_names()
    results = {}
    attempts, failures = [], []
    for i, seed in enumerate(seeds, 1):
        for source in sources:
            suggestions, err = SOURCES[source](seed)
            attempts.append({"seed": seed, "source": source,
                             "count": len(suggestions), "error": err,
                             "outcome": ("error" if err else
                                         "empty" if not suggestions else "ok")})
            if err:
                failures.append({"seed": seed, "source": source, "error": err})
                if verbose:
                    print("  [%d/%d] %s ERROR %s: %s"
                          % (i, len(seeds), source, seed, err))
            elif not suggestions:
                # A genuine zero, not a refusal. The canary decides which.
                if verbose:
                    print("  [%d/%d] %s  0  %s  (no completions)"
                          % (i, len(seeds), source, seed))
            else:
                for rank, s in enumerate(suggestions, 1):
                    q = re.sub(r"\s+", " ", s).strip().lower()
                    row = results.setdefault(q, {"query": q, "sources": [],
                                                 "best_rank": rank,
                                                 "seeds": []})
                    if source not in row["sources"]:
                        row["sources"].append(source)
                    row["best_rank"] = min(row["best_rank"], rank)
                    if seed not in row["seeds"]:
                        row["seeds"].append(seed)
                if verbose:
                    print("  [%d/%d] %s %2d  %s"
                          % (i, len(seeds), source, len(suggestions), seed))
            if sleep:
                time.sleep(random.uniform(*DELAY))
    inventory = page_inventory()
    return (score_rows(results, rooms, inventory), attempts, failures,
            len(inventory))


def outcome_counts(attempts):
    counts = {"ok": 0, "empty": 0, "error": 0}
    for a in attempts:
        counts[a.get("outcome", "error" if a.get("error") else "ok")] += 1
    return counts


def refusal_reason(attempts, canaries):
    """Why this harvest must not be written, or an empty string if it may be.

    Separated from main() so a test can plant each condition and assert the
    refusal, rather than trusting that the three ceilings are wired up.
    """
    for source, (ok, why) in sorted(canaries.items()):
        if not ok:
            return "canary failed on %s: %s" % (source, why)
    counts = outcome_counts(attempts)
    total = sum(counts.values())
    if not total:
        return "no attempts were made at all"
    if counts["error"] / total > MAX_ERROR_RATE:
        return ("error rate %.0f%% is over the %.0f%% ceiling (%d of %d)"
                % (counts["error"] / total * 100, MAX_ERROR_RATE * 100,
                   counts["error"], total))
    if counts["empty"] / total > MAX_EMPTY_RATE:
        return ("empty rate %.0f%% is over the %.0f%% ceiling (%d of %d), "
                "which looks like an endpoint answering 200 with nothing"
                % (counts["empty"] / total * 100, MAX_EMPTY_RATE * 100,
                   counts["empty"], total))
    return ""


def write_outputs(payload):
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report(payload))


def report(payload):
    rows = payload["rows"]
    gaps = [r for r in rows if r["status"] == "gap"]
    partial = [r for r in rows if r["status"] == "partial"]
    covered = [r for r in rows if r["status"] == "covered"]
    lines = []
    w = lines.append
    w("# What people type, and whether we have a page for it\n")
    w("> Generated by `ops/keyword_demand.py`. Do not hand-edit: rerun it.\n")
    w("**Harvested:** %s from %s, %d seeds, %d attempts: %d returned "
      "completions, %d had none, %d errored. Canary: %s.\n"
      % (payload["checked_at"], ", ".join(payload["sources"]),
         payload["seeds"], payload["attempts"],
         payload.get("ok_attempts", 0), payload.get("empty_attempts", 0),
         payload["failed_attempts"],
         ", ".join("%s %s" % (k, "ok" if v["ok"] else "FAILED")
                   for k, v in sorted(payload.get("canaries", {}).items()))
         or "not recorded"))
    # TWO DATES, NOT ONE, AND THEY ARE DIFFERENT FACTS (LRN-0032).
    # When the queries were collected is a fact about the engines. When the
    # statuses were derived is a fact about this site, which changes several
    # times an hour, so a coverage number read without its scoring date is a
    # number about a corpus that no longer exists.
    w("**Scored:** %s against %d page(s)%s. Coverage below describes the "
      "site at THAT moment, not when the queries were harvested. Re-derive "
      "with `python ops/keyword_demand.py --rescore`, which needs no "
      "network.\n"
      % (payload.get("scored_at") or "not recorded, so treat every status "
         "here as of unknown age",
         payload.get("pages_checked", 0),
         (" at commit " + payload["scored_against_commit"])
         if payload.get("scored_against_commit") else ""))
    w("**Queries found:** %d. Checked against %d published page titles: "
      "%d covered, %d partial, %d gap.\n"
      % (len(rows), payload["pages_checked"], len(covered), len(partial),
         len(gaps)))
    w("**This is not search volume.** An autocomplete suggestion proves an "
      "engine predicts the phrase, which means people type it often enough to "
      "be worth predicting. It carries no count, and `rank` orders suggestions "
      "only within the one seed that produced them. Anything here presented "
      "as a monthly volume is a fabrication (CLAUDE.md section 8).\n")
    w("**Coverage is a triage score, not a ranking.** It is the share of a "
      "meaningful query word that appears in the best-matching page title. "
      "`covered` means every word appears somewhere, which is the weakest "
      "claim to coverage available without impression data, and a page can be "
      "`covered` here and invisible on a real result page.\n")
    w("\n---\n")
    w("## Gaps: nothing we publish is titled for these\n")
    w("Showing the top %d of %d, ordered by the best rank the phrase "
      "reached in any one seed suggestion list, so the top of this list is "
      "what an engine predicts first. The full set is in "
      "`keyword-demand.json`.\n" % (min(80, len(gaps)), len(gaps)))
    w("| Rank | Query | Room | Closest page we have |")
    w("|---|---|---|---|")
    for r in sorted(gaps, key=lambda r: (r["best_rank"], r["query"]))[:80]:
        w("| %d | %s | %s | %s (%.2f) |"
          % (r["best_rank"], r["query"], r["room"] or "-",
             r["best_page_title"] or "-", r["coverage"]))
    w("\n## Partial: we are close, and the title does not use their words\n")
    w("Showing the top %d of %d.\n" % (min(60, len(partial)), len(partial)))
    w("| Rank | Query | Our closest title | Coverage |")
    w("|---|---|---|---|")
    for r in sorted(partial, key=lambda r: (-r["coverage"], r["best_rank"]))[:60]:
        w("| %d | %s | %s | %.2f |"
          % (r["best_rank"], r["query"], r["best_page_title"], r["coverage"]))
    w("\n## By room\n")
    w("| Room | Queries | Gap | Partial | Covered |")
    w("|---|---|---|---|---|")
    for room in sorted({r["room"] for r in rows if r["room"]}):
        sub = [r for r in rows if r["room"] == room]
        w("| %s | %d | %d | %d | %d |"
          % (room, len(sub),
             sum(1 for r in sub if r["status"] == "gap"),
             sum(1 for r in sub if r["status"] == "partial"),
             sum(1 for r in sub if r["status"] == "covered")))
    unattributed = [r for r in rows if not r["room"]]
    w("\n%d queries name no room of ours. Those are either a different "
      "subject the engine wandered into, or a room-independent question, and "
      "the second kind is where an article earns its place.\n"
      % len(unattributed))
    if payload["failures"]:
        w("\n## Not checked\n")
        w("| Seed | Source | Why |")
        w("|---|---|---|")
        for f in payload["failures"][:40]:
            w("| %s | %s | %s |" % (f["seed"], f["source"], f["error"]))
    return "\n".join(lines) + "\n"


def status():
    if not os.path.exists(OUT_JSON):
        print("No harvest on record. Run: python ops/keyword_demand.py")
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = payload["rows"]
    print("last harvest : %s" % payload["checked_at"])
    print("sources      : %s" % ", ".join(payload["sources"]))
    print("seeds        : %d, %d attempts, %d ok, %d empty, %d errored"
          % (payload["seeds"], payload["attempts"],
             payload.get("ok_attempts", 0), payload.get("empty_attempts", 0),
             payload["failed_attempts"]))
    print("queries      : %d" % len(rows))
    for st in ("gap", "partial", "covered"):
        print("  %-8s   : %d" % (st, sum(1 for r in rows if r["status"] == st)))
    return 0


def head_commit():
    """The commit the corpus was scored against, or an empty string."""
    try:
        r = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=20)
    except Exception:                                  # noqa: BLE001
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def rescore():
    """Re-derive every status against the corpus as it stands right now.

    LRN-0032, written 2026-10-02 after this cost a wasted investigation and nearly
    cost a duplicate article. A stored `status` is not a property of the query.
    It is the result of scoring that query against the site AS IT WAS when the
    harvest ran, and on this repository the site changes several times an hour
    because more than one session is working on it. Reading the stored file
    said the budget cluster was 121 queries with zero covered; re-scoring the
    identical queries against the corpus as it actually stood returned 29
    covered, because a concurrent session had added a room-by-room budget
    section in the interval.

    This is the cheap half of the tool: pure functions over files already on
    disk, no network, no seeds, nothing to rate-limit. There is no reason to
    read a stale status ever again.
    """
    if not os.path.exists(OUT_JSON):
        print("No harvest on record to re-score. Run: python "
              "ops/keyword_demand.py")
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    before = {}
    for row in payload["rows"]:
        before[row["status"]] = before.get(row["status"], 0) + 1
    results = {r["query"]: {"query": r["query"], "sources": r["sources"],
                            "best_rank": r["best_rank"], "seeds": r["seeds"]}
               for r in payload["rows"]}
    inventory = page_inventory()
    payload["rows"] = score_rows(results, room_names(), inventory)
    payload["pages_checked"] = len(inventory)
    payload["scored_at"] = (datetime.datetime.now(datetime.timezone.utc)
                            .strftime("%Y-%m-%dT%H:%M:%SZ"))
    payload["scored_against_commit"] = head_commit()
    after = {}
    for row in payload["rows"]:
        after[row["status"]] = after.get(row["status"], 0) + 1
    write_outputs(payload)
    print("re-scored %d quer(ies) against %d page(s) at commit %s"
          % (len(payload["rows"]), len(inventory),
             payload["scored_against_commit"] or "unknown"))
    for st in ("gap", "partial", "covered"):
        print("  %-8s %5d -> %5d" % (st, before.get(st, 0), after.get(st, 0)))
    return 0


def main(argv):
    if "--rescore" in argv:
        return rescore()
    if "--status" in argv:
        return status()
    source = "google"
    if "--source" in argv:
        source = argv[argv.index("--source") + 1]
    sources = ["google", "bing"] if source == "both" else [source]
    for s in sources:
        if s not in SOURCES:
            print("unknown source: %s" % s)
            return 2
    seeds = build_seeds()
    dry = "--dry-run" in argv
    if dry:
        seeds = seeds[:6]
    print("Harvesting %d seeds from %s%s"
          % (len(seeds), ", ".join(sources), " (dry run)" if dry else ""))
    canaries = {}
    for src in sources:
        ok, why = canary_ok(src)
        canaries[src] = (ok, why)
        print("  canary %s: %s" % (src, "ok" if ok else why))
    rows, attempts, failures, pages = harvest(sources, seeds)
    for src in sources:
        ok, why = canary_ok(src)
        if not ok:
            canaries[src] = (ok, why)
        print("  canary %s, after the run: %s" % (src, "ok" if ok else why))
    counts = outcome_counts(attempts)
    print()
    print("%d distinct queries from %d attempts: %d returned completions, "
          "%d had none, %d errored"
          % (len(rows), len(attempts), counts["ok"], counts["empty"],
             counts["error"]))
    reason = refusal_reason(attempts, canaries)
    if reason:
        print("UNCHECKED: %s. Nothing written. A partial harvest must "
              "not overwrite a complete one." % reason)
        return 1
    payload = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": sources,
        "seeds": len(seeds),
        "attempts": len(attempts),
        "ok_attempts": counts["ok"],
        "empty_attempts": counts["empty"],
        "failed_attempts": counts["error"],
        "canaries": {k: {"ok": v[0], "note": v[1]}
                     for k, v in sorted(canaries.items())},
        "pages_checked": pages,
        "failures": failures,
        "rows": rows,
    }
    if dry:
        print("dry run: nothing written")
        for r in rows[:15]:
            print("  %-8s %.2f  %s" % (r["status"], r["coverage"], r["query"]))
        return 0
    write_outputs(payload)
    print("wrote %s and %s" % (os.path.relpath(OUT_JSON, ROOT),
                               os.path.relpath(OUT_MD, ROOT)))
    for st in ("gap", "partial", "covered"):
        print("  %-8s: %d" % (st, sum(1 for r in rows if r["status"] == st)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
