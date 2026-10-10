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
      python ops/keyword_demand.py --rescore       re-derive coverage against
                                                   the current site: no network,
                                                   no new demand data
      python ops/keyword_demand.py --help          print this and stop

An argument this file does not recognise is REFUSED, not ignored. Found
2026-10-03: --help was not a flag here, so it fell through every check above
and started a full live harvest of both engines, which is the one thing a
reader asking for help cannot have meant. Nothing that writes files or
touches the network may be reachable by a typo.
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
ROOM_ALSO_CALLED = os.path.join(ROOT, "ops", "room-also-called.json")
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


def room_synonyms():
    """Household words for a room, keyed back to the room's own real name.

    Reads ops/room-also-called.json, the same measured file
    gate_also_called_is_heading already holds current. Missing or malformed
    is read as "no synonyms", never an error: this file must still harvest
    and score without it.
    """
    try:
        with open(ROOM_ALSO_CALLED, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    out = {}
    for room, entry in data.get("rooms", {}).items():
        names = entry.get("names") if isinstance(entry, dict) else None
        if names:
            out[room] = [str(n).lower() for n in names]
    return out


def room_slug(room):
    return room.lower().replace(" ", "-")


def room_of(url, rooms):
    """Which real room a page belongs to, by its own URL slug, longest room
    name first so "Guest Bathroom" claims its pages before "Bathroom" would
    (no room here is literally named that, but the rule is the same one
    attribute_room already uses and for the same reason).

    Returns "" for a page that is not a room/deck/zone page at all (the
    homepage, articles, the shop), which is the common case and correctly
    carries no room signal.
    """
    base = url.rsplit("/", 1)[-1]
    if base.endswith(".html"):
        base = base[:-5]
    for room in sorted(rooms, key=len, reverse=True):
        slug = room_slug(room)
        if base == slug or base.startswith(slug + "-"):
            return room
    return ""


def household_room_signal(query, rooms, synonyms):
    """Which room a query is ABOUT, including a household synonym ("master
    bedroom", "foyer") the site itself never uses as a room name.

    Found 2026-10-10: attribute_room() alone only catches a query that uses
    our own room name literally. "master bedroom closet organization ideas"
    contains no room name of ours, so it returned "", best_page() and
    best_by() had no room signal to apply, and title/heading word-overlap
    tied between Guest Bedroom's and Primary Bedroom's near-identical zone
    pages ("...the guest closet" vs "...the primary closet"). The existing
    tie-break, alphabetically-earliest URL, then silently favoured Guest on
    every such query, which is how the identical "master bathroom vanity"
    shape first surfaced as A25 and was fixed only for that one zone. This
    closes the whole class: any query naming a room by its household word
    now carries the same room signal a literal room name would.
    """
    exact = attribute_room(query, rooms)
    if exact:
        return exact
    low = query.lower()
    best_room, best_len = "", 0
    for room, names in synonyms.items():
        for name in names:
            if name in low and len(name) > best_len:
                best_room, best_len = room, len(name)
    return best_room


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


def page_inventory(rooms=None):
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
    if rooms is None:
        rooms = room_names()
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
            url = "/" + os.path.relpath(path, SITE).replace(os.sep, "/")
            rows.append({"url": url,
                         "title": title,
                         "words": set(words(title)),
                         "head_words": set(words(title + " " + heads)),
                         "room": room_of(url, rooms)})
    return sorted(rows, key=lambda r: r["url"])


def _tie_break(page, best, room_signal):
    """True if `page` should replace `best` on an exact score tie.

    Found 2026-10-10: with no room signal, a tie always fell to the
    alphabetically-earliest URL, which silently favoured every "Guest X" page
    over its "Primary X" sibling (near-identical titles, "guest-" sorts before
    "primary-"). When the query carries a room signal (its own room name, or a
    household synonym like "master bedroom", see household_room_signal), a
    page that is actually IN that room now wins the tie instead; only when
    neither tied page matches the signal, or there is no signal at all, does
    url order still decide, which is what the pre-existing test for this
    function (a query naming no room) still checks.
    """
    if room_signal:
        want = page.get("room") == room_signal
        have = best.get("room") == room_signal
        if want and not have:
            return True
        if have and not want:
            return False
    return page["url"] < best["url"]


def best_page(query, inventory, room_signal=""):
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
                         and _tie_break(page, best, room_signal)):
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


def best_by(query, inventory, field, room_signal=""):
    """Best-matching page for a query against one surface of the inventory."""
    cw = content_words(query)
    if not cw:
        return None, 0.0
    best, score = None, -1.0
    for page in inventory:
        hit = sum(1 for w in cw if w in page[field])
        s = hit / len(cw)
        if s > score or (s == score and best is not None
                         and _tie_break(page, best, room_signal)):
            best, score = page, s
    return best, round(score, 3)


def score_rows(results, rooms, inventory):
    synonyms = room_synonyms()
    rows = []
    for q in sorted(results):
        row = dict(results[q])
        signal = household_room_signal(q, rooms, synonyms)
        page, score = best_page(q, inventory, signal)
        hpage, hscore = best_by(q, inventory, "head_words", signal)
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
    inventory = page_inventory(rooms)
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


# The two query clusters GOALS.md's O1 section names by hand, matched here
# by an explicit, reproducible rule rather than re-typed from memory. Found
# 2026-10-02: GOALS.md's own prose citation of these two counts went stale
# the same day it was written (A13/A14 shipped the pages that moved them,
# nobody told this sentence), and a concurrent session was misled by it into
# drafting a handoff for work already done, LRN-0032's "a stored status is a
# snapshot other sessions are changing" recurring against prose instead of
# the JSON file itself. CLUSTER_PATTERNS is the thing gate_goals_keyword_
# cluster_citation_current re-derives against, so this is provable, not
# asserted: "cheap/budget/DIY" as `\b(cheap|budget|diy)\b` reproduces the
# historical "of 99" denominator exactly; a plain substring check for "diy"
# (no word boundary) or an added "small" term would not.
CLUSTER_PATTERNS = {
    "small space": re.compile(r"small space", re.I),
    "cheap/budget/DIY": re.compile(r"\b(cheap|budget|diy)\b", re.I),
}


def cluster_counts(rows, pattern):
    """covered/partial/gap counts among the rows whose query matches pattern.

    Pure: takes rows already loaded from keyword-demand.json (or a rescore),
    never reads a file itself, so gate_goals_keyword_cluster_citation_
    current can prove it against a synthetic payload as well as the real one.
    """
    matched = [r for r in rows if pattern.search(r["query"])]
    counts = {"covered": 0, "partial": 0, "gap": 0}
    for r in matched:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    counts["total"] = len(matched)
    return counts


# The exact phrasing GOALS.md's O1 section uses to cite each cluster's
# coverage, so gate_goals_keyword_cluster_citation_current can check the
# live claim, not just whether the file mentions the cluster at all.
CLUSTER_CITATION_PATTERNS = {
    "small space": re.compile(
        r'"small space"\s+is\s+\*\*(\d+)\s+covered\s*/\s*(\d+)\s+partial'
        r'\s*/\s*(\d+)\s+gap\s+of\s+(\d+)\*\*'),
    "cheap/budget/DIY": re.compile(
        r'"cheap/budget/DIY"\s+is\s+\*\*(\d+)\s+covered\s*/\s*(\d+)\s+'
        r'partial\s*/\s*(\d+)\s+gap\s+of\s+(\d+)\*\*'),
}


def goals_cluster_citation_problems(text, live_counts):
    """Pure so gate_goals_keyword_cluster_citation_current can prove it
    without shelling out.

    live_counts maps a CLUSTER_PATTERNS name to a cluster_counts()-shaped
    dict freshly re-derived from the real keyword-demand.json. Returns one
    problem string per cluster whose cited covered/partial/gap/total in
    GOALS.md disagrees with the live count. A cluster GOALS.md does not
    currently cite in this exact phrasing is skipped, not flagged: a
    legitimate rewording of the sentence is not this function's business,
    only a citation that stayed in place and went stale underneath it,
    which is what happened 2026-10-02 (A13/A14 shipped the pages that moved
    both clusters; the sentence citing their old counts was never updated,
    and a concurrent session read it instead of re-deriving from the JSON).
    """
    problems = []
    for name, pat in CLUSTER_CITATION_PATTERNS.items():
        m = pat.search(text)
        if not m:
            continue
        cited = tuple(int(x) for x in m.groups())
        live = live_counts.get(name)
        if live is None:
            continue
        real = (live["covered"], live["partial"], live["gap"], live["total"])
        if cited != real:
            problems.append(
                "GOALS.md cites the %r cluster as %d covered / %d partial "
                "/ %d gap of %d, but the real keyword-demand.json currently "
                "scores it as %d covered / %d partial / %d gap of %d"
                % (name, cited[0], cited[1], cited[2], cited[3],
                   real[0], real[1], real[2], real[3]))
    return problems


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
    rooms = room_names()
    inventory = page_inventory(rooms)
    payload["rows"] = score_rows(results, rooms, inventory)
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
    # A FLAG THIS FILE DOES NOT KNOW MUST NOT START A LIVE HARVEST.
    #
    # Found 2026-10-03 by running it: `--help` was not recognised here, so it
    # matched none of the branches below and fell straight through to the
    # default action, which fetches both autocomplete endpoints for every seed
    # in the corpus and overwrites ops/keyword-demand.json. A reader asking a
    # tool how to use it cannot have meant that, and the same hole made every
    # typo (--statuss, --dry-ryn, --rescor) silently do the most expensive and
    # least reversible thing this file can do rather than say it did not
    # understand. Validate first, act second.
    FLAGS = {
        '--rescore', '--status', '--dry-run', '--source', '--help', '-h',
    }
    if '--help' in argv or '-h' in argv:
        print((__doc__ or '').strip())
        return 0
    unknown = []
    skip = False
    for arg in argv:
        if skip:
            skip = False          # the value belonging to --source
            continue
        if arg == '--source':
            skip = True
            continue
        if arg not in FLAGS:
            unknown.append(arg)
    if unknown:
        print('unknown argument(s): %s' % ', '.join(unknown))
        print('Refusing to harvest, because that is not what you asked for. '
              'Run with --help for what this accepts.')
        return 2
    if '--source' in argv and argv.index('--source') + 1 >= len(argv):
        print('--source needs a value: google, bing or both.')
        return 2
    if '--rescore' in argv:
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
