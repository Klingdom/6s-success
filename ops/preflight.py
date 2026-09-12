#!/usr/bin/env python3
"""
One command that runs every gate. Lessons become enforcement, not memory.

WHY THIS EXISTS
---------------
This repository holds 46 learnings, 62 decisions and 207 nightly log entries.
That is a good record and it prevents almost nothing, because a lesson written
in prose is only as strong as whoever happens to remember it at the moment it
matters. The same classes of defect keep recurring:

    a generator silently overwriting hand added work        twice
    copy and a control disagreeing about a price            twice
    a claim that was true when written and rotted since     several times
    an unsourced statistic on a customer facing surface      four on the cards

Every one was caught by looking, not by a gate. So each is now a check that
runs before anything ships, and a new class of defect is supposed to end as a
new function here rather than as another paragraph nobody rereads.

THE RULE THIS FILE IS BUILT ON
------------------------------
A gate must be able to fail. A check that cannot go red on a real defect is
theatre and is worse than nothing, because it buys confidence it has not
earned. Every check below has been verified by breaking something and watching
it fail.

Run:  python ops/preflight.py            everything, fast checks only
      python ops/preflight.py --deep     adds the checks that hit the network

Every run first self-heals a fresh checkout (missing pymupdf, unbuilt
build/products/) before any gate runs; there is no separate --fix step to
remember to pass.
"""
from __future__ import annotations

import collections
import glob
import io
import json
import os
import re
import shutil
import datetime as dt
import subprocess
import sys
import traceback

import browser as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PY = sys.executable

FAIL, WARN = [], []


def fail(gate: str, msg: str) -> None:
    FAIL.append((gate, msg))


def warn(gate: str, msg: str) -> None:
    WARN.append((gate, msg))


def run_gate(fn, *args) -> None:
    """Call one gate function, and never let it take the rest of the run with it.

    Found 2026-09-02: gate_cover_author_current imported ops/build_cover.py,
    which did a top-level `from PIL import ...`. On any machine without
    Pillow (this sandbox, that day), the import raised ModuleNotFoundError
    at call time, and every gate before this in main()'s list had already
    run and been silently thrown away, because main() called each gate bare
    and let the exception propagate straight past `for g, m in FAIL` and
    out of the process. Preflight is "the single gate" this repository's
    own operating instructions name; a bug in gate #62 of 70 should not be
    able to make gates #1 through #61 report nothing at all. Fixed the one
    gate that actually crashed (build_cover.py now imports PIL lazily, only
    when it renders), and fixed the class: every gate call in main() now
    goes through here, so a future gate with the same shape of bug fails
    loudly, by name, with the real exception, and the run still finishes.

    Found 2026-09-06: gate_stripe_one_product_per_sku calls
    stripe_dedupe.duplicates(), which calls stripe_catalog.secret_key(),
    which reports a missing credential with sys.exit(...) rather than
    raising. sys.exit() raises SystemExit, which is not an Exception
    subclass, so it walked straight past this function's except clause the
    same way the PIL ImportError above used to walk past main()'s bare gate
    calls: preflight exited 1 with no summary at all, in the one credential
    state (no .env.secrets) every sandbox this project runs in has had for
    its entire history, and CI's own checks.yml run went red on it (run
    308, commit 524bcd0d). Widened the catch to also cover SystemExit, since
    a gate calling sys.exit() through a library it does not control is not
    hypothetical. KeyboardInterrupt is deliberately not caught, so Ctrl-C
    still works.
    """
    try:
        fn(*args)
    except (Exception, SystemExit) as e:
        fail(getattr(fn, "__name__", str(fn)),
             f"gate crashed and could not complete: {type(e).__name__}: {e}")
        if os.environ.get("PREFLIGHT_TRACEBACK"):
            traceback.print_exc()


def run(script: str, *args) -> tuple:
    p = subprocess.run([PY, os.path.join(ROOT, "ops", script), *args],
                       capture_output=True, text=True, cwd=ROOT,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# --------------------------------------------------------------- existing
def gate_existing(deep: bool) -> None:
    """The audits that already exist, run from one place instead of by memory."""
    checks = [
        ("pages", "audit_pages.py", ()),
        ("catalogue", "audit_catalog.py", ()),
        ("sellable", "check_sellable.py", ("--deep",) if deep else ()),
        ("dashes", "fix_dashes.py", ("--check",)),
        ("fingerprints", "fingerprint_assets.py", ("--check",)),
    ]
    for name, script, args in checks:
        if not os.path.exists(os.path.join(ROOT, "ops", script)):
            warn(name, f"{script} is missing")
            continue
        code, out = run(script, *args)
        if code != 0:
            last = [l for l in out.strip().splitlines() if l.strip()][-3:]
            fail(name, " / ".join(l.strip() for l in last))


# --------------------------------------------------------------- new gates
def gate_build_id_current() -> None:
    """site/build-id.txt must be a hash of the site as it stands.

    It is what ops/deploy.py compares against production to answer "is this
    build live". A stale stamp makes that answer confidently wrong in the
    dangerous direction: it would match a build that had already shipped and
    declare a newer one deployed.

    ops/build_id.py's own compute() hashes what `git ls-files -s` reports,
    the INDEX, not the working tree (deliberately, to avoid a CRLF/LF
    cross-platform mismatch its own docstring already names). That makes
    this gate's "current" verdict silently stale advice the moment a
    session regenerates site/ pages without staging them first: preflight
    passes clean because the index still matches the last commit, the
    session commits and pushes believing it, and CI hashes the real,
    now-different commit and fails. Found 2026-09-07, this operator, the
    hard way: exactly that sequence shipped a red push. Warn here, at the
    one place a session is likely to read the verdict and trust it, rather
    than only in a commit message after the fact.
    """
    import importlib.util as _u
    spec = _u.spec_from_file_location(
        "build_id", os.path.join(ROOT, "ops", "build_id.py"))
    if spec is None or spec.loader is None:
        warn("build-id", "ops/build_id.py not importable; not checked.")
        return
    m = _u.module_from_spec(spec)
    spec.loader.exec_module(m)
    have, want = m.current(), m.compute()
    if have != want:
        fail("build-id",
             "site/build-id.txt says %s, the site hashes to %s. Deploy "
             "verification compares this against production, so a stale value "
             "makes it answer wrongly. Run: python ops/build_id.py"
             % (have or "nothing", want))
        return

    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", "site"], cwd=ROOT,
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:                                           # noqa: BLE001
        dirty = ""
    if dirty:
        warn("build-id",
             "this verdict is current against the git INDEX, but site/ has "
             "uncommitted change(s) not yet staged. Stage them (git add) "
             "and rerun before trusting this as current, or a commit made "
             "now can still ship a stale build-id.txt: %s" %
             "; ".join(dirty.splitlines()[:3]))


def gate_downloads_current() -> None:
    """What the site serves must be what the build produced.

    Found 2026-09-04: ops/build_deck_pdf.py rebuilt the free Entryway deck with
    legible type, and site/downloads/ still held the previous file. The page
    offering the download was correct, the link worked, the file was the right
    size, and every customer taking the deck got the version whose body text
    printed at 3.1 points. Nothing compared the two copies, so nothing noticed.

    A build artifact that is also a customer deliverable exists twice, and the
    copy under site/ is the one that ships. This compares them by content.
    """
    import hashlib as _h
    pairs = [("build/6S-Entryway-Deck-PrintAndPlay.pdf",
              "site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf")]
    stale = []
    for b, w in pairs:
        bp, wp = os.path.join(ROOT, b), os.path.join(ROOT, w)
        if not (os.path.exists(bp) and os.path.exists(wp)):
            continue
        hb = _h.sha256(io.open(bp, "rb").read()).hexdigest()
        hw = _h.sha256(io.open(wp, "rb").read()).hexdigest()
        if hb != hw:
            stale.append(os.path.basename(w))
    if stale:
        fail("downloads-current",
             "the site serves a different file from the one the build "
             "produced, so customers get the old one: %s" % stale)


def gate_product_images_exist() -> None:
    """Every product tile's image must be a file that exists.

    Found 2026-09-04: DECK-ENTRY, the free Entryway deck that is the site's
    main lead magnet, pointed at assets/img/cards/entryway/... while the card
    art actually lives at assets/cards/entryway/. That URL returned 404 on
    production, so the one product we most want a stranger to take showed a
    broken image on the shop, and nothing noticed. 158 of the other 159 product
    images resolved fine, which is exactly why a single wrong one survives: the
    page looks right unless you check the tile that is broken.

    site/assets/js/site.js builds the URL as "assets/img/" + img, so that is
    what this checks. It is a file existence test, not a fetch, so it works in
    CI with no network.
    """
    import re as _re
    d = os.path.join(SITE, "assets", "js", "data.js")
    if not os.path.exists(d):
        warn("product-images", "site/assets/js/data.js is missing; not checked.")
        return
    src = io.open(d, encoding="utf-8", errors="replace").read()
    missing = []
    for v in sorted(set(_re.findall(r'"img":\s*"([^"]+)"', src))):
        if not os.path.exists(os.path.join(SITE, "assets", "img", v)):
            missing.append(v)
    if missing:
        fail("product-images",
             "%d product image(s) do not exist under site/assets/img/, so the "
             "tile shows a broken image: %s" % (len(missing), missing[:3]))


def gate_third_party() -> None:
    """The site promises no third party requests. Keep that true.

    It was false once: standards.html carried two preconnects to Google's font
    hosts while the privacy page promised none. The fonts were self hosted
    already, so the fix was deleting the lines rather than weakening the
    promise. Nothing should quietly put one back.
    """
    allowed = re.compile(r"6s-success\.com|schema\.org|buy\.stripe\.com|"
                         r"localhost|127\.0\.0\.1|example\.com|w3\.org")
    # A host is also permitted if privacy.html NAMES it. That is the whole
    # point of the gate: the rule is not "never touch anybody", it is "never
    # touch anybody the reader was not told about". Tying the allow-list to the
    # promise means the only way to add a third party is to disclose it, and
    # the only way to quietly undisclose one is to break the build.
    #
    # Added 2026-09-04, when twelve zone pages gained a YouTube video. The
    # embed is click-to-load, so the page contacts nobody until the reader
    # presses play, and privacy.html says exactly that in those words.
    disclosed = set()
    _priv = os.path.join(SITE, "privacy.html")
    if os.path.exists(_priv):
        _p = io.open(_priv, encoding="utf-8", errors="replace").read()
        _body = re.sub(r"(?is)<head>.*?</head>", " ", _p)
        disclosed = {h.lower() for h in
                     re.findall(r"\b((?:[a-z0-9-]+\.)+[a-z]{2,})\b", _body)}
    bad = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True) + \
            glob.glob(os.path.join(SITE, "assets", "**", "*.css"), recursive=True) + \
            glob.glob(os.path.join(SITE, "assets", "**", "*.js"), recursive=True):
        if os.sep + "downloads" + os.sep in f:
            continue          # the book sample is a shipped artefact, not a page
        s = io.open(f, encoding="utf-8", errors="replace").read()
        # A URL inside JSON-LD is metadata, not a request. schema.org's
        # VideoObject REQUIRES contentUrl and embedUrl to name where the video
        # actually lives, and naming youtube.com there causes the browser to
        # contact nobody. Scanning it anyway made this gate unable to tell a
        # real embed from a correct description of one, which is the difference
        # between a privacy leak and an accurate citation.
        s = re.sub(r'(?is)<script type="application/ld\+json">.*?</script>',
                   " ", s)
        # Likewise a comment ships to the reader but fetches nothing.
        s = re.sub(r"(?s)<!--.*?-->", " ", s)
        for host in set(re.findall(r"https?://([a-z0-9.-]+)", s)):
            h = host.lower()
            if allowed.search(h):
                continue
            # www.youtube-nocookie.com is disclosed as youtube-nocookie.com;
            # match on the registrable tail rather than demanding the exact
            # string, or the disclosure has to guess the subdomain.
            if any(h == d or h.endswith("." + d) for d in disclosed):
                continue
            bad.append((os.path.relpath(f, ROOT), host))
    if bad:
        fail("third-party", f"{len(bad)} reference(s) to outside hosts while the "
                            f"privacy page promises none: {bad[:3]}")


def all_pages() -> list:
    """Every page a visitor can reach, not the seventeen in the top directory.

    glob(SITE/*.html) sees only the files sitting directly in site/ and misses
    the 166 zone, room and article pages, which are the highest volume
    templates on the site. That narrow glob has now been found wrong four
    times here: twice in the dashboard's counters, where "not scanned" was
    reported as zero, once in the bundle maths gate, and once in each of the
    three gates below. Anything checking public copy should use this.

    downloads/ is excluded because the book sample is a shipped artefact
    rather than a page of the site.

    Deliberately NOT excluding site/**/_*.html here, even though that is the
    real convention for a scratch/probe file (gate_no_stray_probe_files):
    ops/tests/test_gates.py's own Planted() fixtures use that exact prefix to
    simulate a real page while gate_stale_claims, gate_unsourced_stats and
    gate_nav_current scan for it through this same function, on purpose,
    inside a `with` block. Excluding the prefix here once made all three
    tests blind to their own planted fault. A caller that specifically needs
    protection from a stray scratch file mid-flight (gate_roadmap_prices_
    current's page count, found 2026-09-06) filters it locally instead.
    """
    return sorted(f for f in glob.glob(os.path.join(SITE, "**", "*.html"),
                                       recursive=True)
                  if os.sep + "downloads" + os.sep not in f)


STAT = re.compile(
    r"\b(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*"
    r"(?:percent|%|hours?|minutes?|days?|weeks?|years?|times|x)\b", re.I)
# A thousands-separated number ("35,000 decisions a day") is the shape of a
# claim even when the unit sits after an intervening noun rather than glued
# to the digits, which is exactly the phrasing STAT above cannot see: "People
# make up to 35,000 decisions a day" sat on a shipped card back with nothing
# ever flagging it, because the number is followed by "decisions", not by
# "day". A plain comma-grouped number is rare in genuine product copy
# ("684 cards" has no comma at that size), so this needs no unit check of
# its own; CLAIMY below still has to match nearby before it counts, and
# already does for both real cases found this way ("up to 35,000...",
# "...1,000 pieces per year") without widening CLAIMY itself. Widening
# CLAIMY instead (adding a bare "a day"/"a week") was tried first and
# reverted: it flagged "20-30 minutes once a week" and "5 minutes each
# day", both instructions, not claims about people or results.
STAT_BIG = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")
# Phrases that make a number a claim about people or results rather than a
# specification of the product. "684 cards" is a spec; "saves 60 hours a year"
# is a claim and needs a source.
CLAIMY = re.compile(r"\b(average|typical|studies|research|most people|"
                    r"saves?|save you|up to|reduces?|increases?|"
                    r"on average|per year|each year|per day)\b", re.I)

# AN APPEAL TO AUTHORITY CARRIES NO NUMBER, so STAT above cannot see it and
# gate_unsourced_stats structurally could not fail on one. On 2026-09-07 a card
# read "Research shows that visible progress increases motivation and
# follow-through because our brains expect future success." The gate was green
# the entire time that sat there, because there was nothing to count.
#
# This is the worse half of the same defect. A fabricated statistic at least
# offers a number somebody could go and check. "Research shows" borrows the
# credibility of a study without naming one, and this one added a claim about
# what brains do on top of it. CLAUDE.md section 8 rules out fabricated
# statistics; section 15 rules out presenting a hypothesis as a validated
# finding. An uncited appeal to research is both.
#
# Naming a real source is the way through, so the same "source|according to|
# cite" escape the numeric branch already uses applies here too.
AUTHORITY = re.compile(
    r"\b(?:research (?:shows?|suggests?|finds?|proves?)|"
    r"studies? (?:show|suggest|find|have found)|science (?:says?|shows?)|"
    r"scientists? (?:say|agree|found)|experts? (?:say|agree|recommend)|"
    r"clinically proven|proven to|research(?:ers)? (?:say|found))\b", re.I)


def gate_unsourced_stats() -> None:
    """A statistic about people or results, with no source, on a public page.

    CLAUDE.md section 8 rules out fabricated statistics outright. Four turned
    up printed on the card deck, which is exactly where nobody was looking.
    This checks the surface that is easiest to fix and most read.
    """
    hits = []

    # THE CARD DECK'S OWN TEXT, not just the rendered pages.
    #
    # This gate's docstring already said four statistics "turned up printed on
    # the card deck, which is exactly where nobody was looking". They were
    # cleaned off the HTML and left in the deck source, so on 2026-09-04 twelve
    # were still there, including "7 times less likely to be targeted by
    # burglars", "421,000 bacteria per step" and one that invents its own
    # authority: "rated 23% more favorably by guests in hospitality studies".
    # Every one of them was baked into the printed card faces too, and that
    # deck is free to download, so the claim travels off the site entirely.
    # Checking the rendered page was checking the one surface that mattered
    # least.
    import glob as _glob
    import json as _json
    # THREE copies of the card corpus exist, and the first version of this gate
    # globbed two of them. ops/cardtext/*.json is the source,
    # build/*-cardtext.json is the merged deck, and build/cardtext/*.json is a
    # separate per-batch build copy that the second pattern does not match. The
    # statistics were stripped from two on 2026-09-06 and I reported them gone.
    # Fifteen were still sitting in the third, including "7 times less likely
    # to be targeted" and a "23% more favorably ... in hospitality studies" that
    # invents its own field of study. A gate that checks most of the places a
    # claim can live is a gate that certifies a claim it never read.
    for f in _glob.glob(os.path.join(ROOT, "ops", "cardtext", "*.json")) +             _glob.glob(os.path.join(ROOT, "build", "*-cardtext.json")) +             _glob.glob(os.path.join(ROOT, "build", "cardtext", "*.json")):
        try:
            d = _json.load(io.open(f, encoding="utf-8"))
        except ValueError:
            continue
        items = d if isinstance(d, list) else d.get("cards", d)
        if not isinstance(items, list):
            continue
        for c in items:
            if not isinstance(c, dict):
                continue
            for k, v in c.items():
                # A field can be a plain string ("did_you_know") or a list of
                # strings ("claims", "callouts"). The list shape used to be
                # invisible here: `isinstance(v, str)` on a list is False, so
                # every claim living in a list field passed with nothing ever
                # reading it, the same "certifies a claim it never read" gap
                # this gate's own history already found twice for file paths.
                strs = v if isinstance(v, list) else [v] if isinstance(v, str) else []
                # A challenge or a tracker states a rule: "go 7 days", "handle
                # every package within 24 hours". Those numbers are the
                # instruction, not an assertion about people or results, and
                # flagging them every run is how a gate stops being read.
                if k in ("home_quest_challenge", "progress_tracker",
                         "habit_builder", "challenge", "tracker"):
                    continue
                for v in strs:
                    if not isinstance(v, str):
                        continue
                    for m in list(STAT.finditer(v)) + list(STAT_BIG.finditer(v)):
                        w = v[max(0, m.start() - 110):m.end() + 60]
                        if CLAIMY.search(w) and not re.search(
                                r"source|according to|cite|\[\d\]", w, re.I):
                            hits.append(("%s %s" % (os.path.basename(f),
                                                    c.get("id", "?")),
                                         w.strip()[:96]))
                    for m in AUTHORITY.finditer(v):
                        w = v[max(0, m.start() - 90):m.end() + 110]
                        if not re.search(r"source|according to|cite", w, re.I):
                            hits.append(("%s %s" % (os.path.basename(f),
                                                    c.get("id", "?")),
                                         w.strip()[:96]))

    for f in all_pages():
        s = io.open(f, encoding="utf-8", errors="replace").read()
        body = s[s.index("<main"):s.index("</main>")] if "<main" in s else s
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
        for m in list(STAT.finditer(text)) + list(STAT_BIG.finditer(text)):
            window = text[max(0, m.start() - 110):m.end() + 60]
            if CLAIMY.search(window) and not re.search(
                    r"source|according to|cite|\[\d\]|footnote", window, re.I):
                hits.append((os.path.basename(f), window.strip()[:96]))
        for m in AUTHORITY.finditer(text):
            window = text[max(0, m.start() - 90):m.end() + 110]
            if not re.search(r"source|according to|cite|footnote",
                             window, re.I):
                hits.append((os.path.basename(f), window.strip()[:96]))
    if hits:
        warn("unsourced-stats",
             f"{len(hits)} claim(s) about people or results with no source "
             f"nearby: a statistic, or an appeal to research that names none. "
             f"First: "
             f"{hits[0][0]}: {hits[0][1]!r}")


def worktree_changes() -> list:
    """Files that really differ, compared by content rather than by timestamp.

    git status --porcelain calls a file modified as soon as its mtime moves,
    because what it consults is the index stat cache, and it only falls back to
    reading the file when it can. A generator that rewrites a page with byte
    identical content moves the mtime every time.

    This gate reruns eleven generators over 189 pages, so that is not an edge
    case. It reported 186 files as generator drift on a tree where git diff was
    empty and git add -A staged nothing whatsoever. Left alone it would have
    failed every preflight run from a clean checkout, which is the worst shape
    a gate can take: one that cries wolf until somebody stops reading it.

    git diff does a content comparison, so it cannot be fooled this way.
    """
    def names(*args) -> list:
        out = subprocess.run(["git"] + list(args), cwd=ROOT,
                             capture_output=True, text=True).stdout
        return [x for x in out.splitlines() if x.strip()]

    return sorted(set(names("diff", "--name-only")
                      + names("diff", "--cached", "--name-only")
                      + names("ls-files", "--others", "--exclude-standard")))


def _restore(paths: list) -> None:
    """git checkout only the given paths, in batches, never the whole tree.

    Batched because a checkout of several hundred paths can exceed the command
    line length limit on Windows, and a truncated restore would leave generator
    output behind while reporting success.
    """
    for i in range(0, len(paths), 100):
        batch = [p for p in paths[i:i + 100] if p]
        if batch:
            subprocess.run(["git", "checkout", "--", *batch], cwd=ROOT,
                           capture_output=True)


def gate_shop_prerendered() -> None:
    """The shop page must contain its products as HTML, not only as script.

    Measured against production 2026-09-03: /shop.html served 136 KB and a
    client that does not execute JavaScript read 1,218 characters of it with
    NOT ONE product in them. All 155 buy links sat inside a <script> block. The
    page carrying every product this business sells had, in plain HTML, no
    products on it: nothing for a search engine to rank, and an empty store on
    a slow phone until a 74 KB catalogue downloaded and ran.

    ops/prerender_shop.py fixes that by running the page's own renderProduct in
    a headless browser and writing the result into the file, so there is no
    second copy of the card markup to drift. This gate does not need a browser:
    it just checks the result is still there, because a regenerated shop.html
    would silently drop it and the page would look fine to anyone with
    JavaScript, which is everyone who tests it by eye.
    """
    page = os.path.join(ROOT, "site", "shop.html")
    if not os.path.exists(page):
        warn("shop-prerendered", "site/shop.html is missing; not checked.")
        return
    html = io.open(page, encoding="utf-8").read()
    body = re.sub(r"(?is)<script.*?</script>", " ", html)
    cards = len(re.findall(r'class="[^"]*product', body))
    if "prerendered-shop:start" not in html or cards < 100:
        fail("shop-prerendered",
             "site/shop.html carries %d product cards in plain HTML. The "
             "catalogue is script-only again, so a crawler sees an empty "
             "shop. Run: python ops/prerender_shop.py" % cards)


GENERATOR_OWNERSHIP_CHAIN = [
    "build_zone_pages.py", "build_resources.py",
    "wire_generated_catalog.py", "build_product_schema.py",
    "build_articles.py", "build_quest.py", "build_printpack.py",
    "build_standards.py", "build_deck_gallery.py",
    "build_sample_html.py", "build_standards_page.py", "build_zone_index.py",
    "build_kit_page.py", "build_corporate.py",
    "build_kitchen_deck_page.py",
    "build_youtube_metadata.py",
    "build_social_captions.py",
    "build_feed.py",
    "build_epub.py",
    "fingerprint_assets.py", "build_pwa.py",
    "build_avif.py",
]
# Module level, not local to gate_generator_ownership, so
# gate_every_generator_has_a_protection_plan() below can check the same list
# rather than a second copy of it drifting out of step with this one.

# Every ops/build_*.py NOT on the chain above must be named here, mapped to
# the gate(s) that were actually found, on inspection, to protect its output
# a different way (a dedicated regenerate-and-diff, a live-count check, a
# dashboard-visibility check, or similar). See
# gate_every_generator_has_a_protection_plan() and LEARNINGS.md LRN-0009: an
# 2026-09-10/11 audit found 15 generators sitting outside this chain, all 15
# already protected by a gate that happened to exist, but the coverage lived
# only in scattered docstrings and one operator's working notes, nowhere a
# future 35th generator would be forced to declare itself. This dict is that
# place now.
GENERATOR_PROTECTED_ELSEWHERE = {
    "build_all_prompts.py": ("gate_card_prompts_desktop_only",),
    "build_card_prompts.py": ("gate_card_prompts_desktop_only",),
    "build_card_template.py": ("gate_card_related_links", "gate_deck_art_withheld"),
    "build_catalog.py": ("gate_marketplace_fix_current", "gate_zone_heroes_stable"),
    "build_cover.py": ("gate_cover_author_current",),
    "build_deck_pdf.py": ("gate_deck_pdf_download_current",),
    "build_icons.py": ("gate_icons_current",),
    "build_id.py": ("gate_build_id_current",),
    "build_image_prompts.py": ("gate_image_prompts_tier0_count_honest",),
    "build_manual_print.py": ("gate_front_matter_filled",),
    "build_mobile_corpus.py": ("gate_mobile_corpus_current",),
    "build_seo.py": ("gate_sitemap_complete", "gate_indexable_pages_have_schema",
                      "gate_site_verification_declared",
                      "gate_sameas_backed_by_onsite_link"),
    "build_social_pins.py": ("gate_dashboard_social_pins_live",),
    "build_thumbnails.py": ("gate_dashboard_thumbnails_live",),
}


def gate_generator_ownership() -> None:
    """No file may be hand edited if a generator rewrites it.

    This is issue #26: five separate occurrences, each a generator that was
    one run away from deleting content its own template does not produce
    (ops/build_resources.py and the links to 134 pages; ops/build_zone_pages.py
    and the imported chapter figures; ops/build_resources.py again and the
    SEO/JSON-LD block only ops/build_seo.py writes; ops/build_articles.py and
    the PWA/measurement blocks on both live articles). All caught by luck or
    by a diff someone happened to read. This runs the generators against a
    clean tree and fails if any tracked file would change, which is the same
    thing as saying the file on disk is not what its generator produces.

    Only generators confirmed clean on a real, current checkout are listed
    here. ops/build_deck_gallery.py was the sixth data point (both gallery
    pages missing the PWA/measurement blocks, same shape as
    ops/build_articles.py); fixed and added below. ops/build_pwa.py was the
    seventh: a different shape of drift, not a missing block but a stale one.
    Its own docstring says "run this AFTER fingerprint_assets.py" because
    site/sw.js's precache list carries the same content hashes the
    fingerprinter stamps onto site/quest.html, but nothing enforced that
    order outside this gate, so a prior asset change re-fingerprinted
    quest.html without anyone re-running build_pwa.py afterward: the
    committed site/sw.js precached six asset URLs at hashes that no longer
    matched what quest.html actually requests. Offline that is a real
    outage, not a cosmetic drift: the fetch handler caches by exact request
    URL, so a stale precached hash never matches the live page's request and
    the asset falls through to network, which is the one thing that doesn't
    work in the garage this feature exists for. Fixed by regenerating
    site/sw.js and appending build_pwa.py to this list after
    fingerprint_assets.py, the one place order matters in this gate.
    ops/build_standards_page.py and ops/build_zone_index.py were the eighth
    and ninth data points, both fixed the same way: chaining wire_measure.py
    and wire_pwa.py into each generator's own main(), closing issue #26's
    last two open items. ops/build_standards_page.py's <head> template never
    carried the PWA block at all (its MEASURE block only survived by
    accident, copied verbatim from deck.html's footer by shell()); ops/
    build_zone_index.py's template carried neither block. Both now added
    below.

    ops/build_kit_page.py was the tenth data point, found 2026-09-01 by
    running it standalone to check its output rather than trusting that it
    had never been swept: its own head/body template carried none of the
    PWA icons, the progressive marker, measure.js, the skip link, the main
    landmark id, or aria-current, and it was simply missing from this list
    entirely, so a rebuild of kit.html was invisible to this gate no matter
    how much it stripped. Fixed the same way as the two data points above:
    the same seven wiring passes chained into its own main(), then added
    below.

    ops/build_printpack.py and ops/build_standards.py were the eleventh
    data point, found 2026-09-02 reading both files cold: unlike every
    generator above, these two do not write into site/, they write the
    committed build/6S-Whole-House-Print-Pack.html and
    build/6S-Standards-Pack.html, the $19 Print Pack and the free Standards
    Pack a buyer actually receives, both built from content.json. Neither
    generator appeared anywhere in this gate, so the next time content.json
    changed without someone remembering to rerun them by hand, the product a
    customer downloads would silently disagree with the book, the site and
    the Home Quest it is supposed to match, with nothing to catch it. Both
    read clean against the current tree (regenerating produced a
    byte-identical diff), so this closes a latent gap rather than a live
    one. Added below the same way as every other data point.

    ops/wire_generated_catalog.py was the twelfth data point, found
    2026-09-05 running it cold to check site/assets/js/data.js for defects,
    not because this gate flagged anything: it could not have, because the
    generator was never in the list below. A hand commit (9e7b1cd1) had
    added three consulting SKUs straight into data.js instead of through
    this script, leaving the array in an order the generator would never
    produce and nothing to notice. The reorder itself was harmless (every
    SKU, price and buy link identical, confirmed by diff before trusting
    it), but the gap that let it sit undetected is the same shape as every
    data point above: a generator that owns a file, and no gate that runs
    it. Fixed by adding it below; the fix also had to reach
    site/shop.html, which prerenders its grid from this same file in a
    headless browser ops/prerender_shop.py drives, not from another
    generator this gate could rerun, so that page needed a manual
    re-render this time rather than a place in this list.

    ops/build_youtube_metadata.py was the thirteenth data point, found
    2026-09-07 auditing every ops/build_*.py against this list by name rather
    than waiting for a live drift to surface one. It writes a title,
    description and tags for each of the 114 zone videos plus a playlists
    grouping, all committed under build/video/youtube/ (not gitignored,
    unlike build/heroes/), from nothing but video_zone.zones() and
    build_zone_pages.slug()/display(), neither of which needs a Desktop-only
    input. Confirmed no live drift before adding: ran it against the current
    checkout and diffed, byte-identical, so this closes the gap before it
    opens one rather than fixing a defect already shipped. Same shape as
    build_kit_page.py and build_deck_pdf.py's own dashboard-vs-served gap:
    a generator whose committed output nothing re-checked, so a future
    zone-content edit could leave 114 video descriptions pointing at stale
    text or a dead page slug with nothing to say so.

    ops/build_social_captions.py was the fourteenth data point, added
    2026-09-09 alongside the generator itself. It writes a Pinterest and
    Instagram caption, board and hashtag set for each of the 114 zone cards
    ops/build_social_pins.py already renders, plus a boards.json grouping,
    committed under build/social/captions/, built the same way as
    build_youtube_metadata.py: from video_zone.zones() and
    build_youtube_metadata's own title_for()/zone_page_slug(), no Desktop
    input needed. Added to this list on day one rather than waiting for a
    future content edit to drift it silently out of step with the site.

    ops/build_feed.py was the fifteenth data point, added 2026-09-10
    alongside the generator itself: it writes site/feed.xml, an Atom feed
    of the site's articles, read back off each article page's own title,
    description, canonical link and JSON-LD dates, so a new or edited
    article shipping without a feed rerun is exactly the same drift shape
    as every generator above. Added on day one rather than waiting for a
    live gap.

    ops/build_epub.py was the sixteenth data point, found 2026-09-11 cold
    reading it per this repository's own step 5d rather than trusting its
    own thorough internal verify() step, which checks structure, not
    currency. It writes build/6S-Success-Home-Edition.epub, the real file
    Amazon KDP publishing (OWNER-ACTIONS.md item 14, not yet done) uploads.
    It was previously claimed "protected elsewhere" by gate_no_stray_dashes,
    which only scans for forbidden characters and cannot see staleness at
    all. Regenerating it from the current tree and diffing against the
    committed file found real drift: the committed EPUB predates two real
    2026-09-05 accessibility fixes to content/book/assets/book.css (36
    heading-level jumps, 401 WCAG contrast failures), so the file waiting on
    Phil's own upload still shipped the pre-fix styling. The book text
    itself had not drifted (front matter and all 50 chapters byte-identical
    both ways), only the shared stylesheet and cover. Fixed by regenerating
    build/6S-Success-Home-Edition.epub and adding this generator to the
    chain. Doing that surfaced a second, independent bug the first diff
    would have made permanent: dc:modified was derived from source file
    mtimes, and every checkout in this repository's own sandboxes stamps
    every source file with the same checkout-time mtime (proven directly:
    every chapter file and the front matter file identical to the second),
    so a fresh regenerate-and-diff would have reported drift on every single
    run regardless of whether any real content had changed, the gate
    permanently red for a reason with nothing to do with content. Fixed by
    replacing the mtime read with an explicit EDITION_DATE constant in
    build_epub.py, bumped by hand in the same commit as a real content
    change, the same shape as build_feed.py's own depth=1-clone date fix a
    day earlier. Verified two consecutive builds are byte-identical before
    adding it here.
    """
    # preflight regenerates the command deck early in its own run, before it
    # reaches this gate, so by the time we get here the tree it is about to
    # inspect has three of preflight's own artefacts sitting modified in it.
    # They are not produced by any of the eleven site generators below and are
    # not what this gate asks about, so they cannot be evidence either way.
    # Excluding them by name rather than loosening the check: anything else
    # dirty still blocks, because it would make the diff afterwards meaningless.
    _own_output = {"EXECUTIVE-DASHBOARD-LIVE.md", "ops/dashboard.html",
                   "ops/state.json"}
    dirty = [f for f in worktree_changes() if f not in _own_output]
    if dirty:
        # A failure, not a warning. This gate only runs when it is explicitly
        # asked for, so "you asked me to check generator ownership and I could
        # not" is not a pass. It spent five cycles answering "skipped" because
        # build/shots was missing from .gitignore, and a warning among three
        # standing warnings is easy to read past, which is exactly what
        # happened. The same rule the deploy and link checks already follow: a
        # run that could not look must not report clean.
        fail("generator-ownership",
             "could not run: %d file(s) in the working tree differ, so a diff "
             "afterwards would not mean anything. Commit or stash first. "
             "First few: %s" % (len(dirty), dirty[:4]))
        return

    # fingerprint_assets.py runs last: every generator here writes bare asset
    # paths and the fingerprinter is the separate pass that stamps the ?v=
    # cache-busting hash committed on disk, so skipping it made this gate
    # fail on a clean, untouched checkout, on every asset reference, always.
    # build_seo.py is deliberately NOT run standalone here: its __main__ also
    # rewrites sitemap.xml, and that rewrite stamps today's date onto any page
    # that looks "changed since HEAD" at the moment it runs, including a page
    # another generator earlier in this same loop rewrote but fingerprint_
    # assets.py has not yet re-fingerprinted. Running it mid-chain manufactured
    # a same-day lastmod bump on over 100 untouched pages the first time this
    # was tried. build_resources.py already calls build_seo.build_pages()
    # itself (the actual fix for issue #26's fifth data point), so the one
    # page that needed checking is still covered without that hazard.
    gens = list(GENERATOR_OWNERSHIP_CHAIN)
    # build_avif.py --wire is the tenth data point: a real, later pass that
    # adds <source type="image/avif"> ahead of every <source type="image/
    # webp">, run once across the whole site after the page generators write
    # their webp markup. It was simply missing from this list, so this gate
    # reported the deck gallery pages (both real AVIF sources, both files on
    # disk) as hand-edited drift on every untouched checkout, always: caught
    # by test_generator_ownership.py's own first assertion, which failed on a
    # clean checkout rather than on a planted fault, meaning the gate itself
    # was the thing broken, not the pages it accused. Needs its own argument,
    # unlike every other generator here, which is why it is not just added to
    # the loop below unconditionally.
    _extra_args = {"build_avif.py": ("--wire",)}
    # build_zone_pages.py cannot reproduce its own output without the source
    # photographs in build/heroes/, which are gitignored and therefore absent
    # from every CI checkout. Its approval record is bound to each image's sha
    # on purpose, so a verdict cannot be trusted without the image it was given
    # for, and with no images approved() returns nothing and all 110 zone pages
    # regenerate pointing at the generic room map. That is the environment
    # lacking an input, not a generator drifting, and failing the build on it
    # would be the loudest possible false alarm.
    #
    # So it is skipped there, and the pages it owns are excluded from the
    # comparison, and the run says so. What it must never do is skip them and
    # still report the rest as a clean bill of health for the whole site.
    _heroes = os.path.join(ROOT, "build", "heroes", "zones")
    _no_heroes = not os.path.isdir(_heroes) or not os.listdir(_heroes)
    _unchecked = ""
    if _no_heroes:
        gens = [g for g in gens if g != "build_zone_pages.py"]
        _unchecked = ("build/heroes/ is absent here, so the 114 zone pages and "
                      "their generator were NOT checked. Run this where the "
                      "source photographs are.")

    for g in gens:
        if not os.path.exists(os.path.join(ROOT, "ops", g)):
            continue
        run(g, *_extra_args.get(g, ()))
    # Same exclusion as the pre-check above, and for the same reason: these
    # three are preflight's own deck output, already modified before this gate
    # started, and no generator in the list below writes them. Without this the
    # gate reports its own host as generator drift.
    changed = [f for f in worktree_changes() if f not in _own_output]
    if _no_heroes:
        changed = [f for f in changed if not f.startswith("site/zones/")]
    if changed:
        files = changed[:4]
        fail("generator-ownership",
             f"{len(changed)} file(s) differ from what their "
             f"generator produces, so hand edits there will be lost on the "
             f"next build: {files}")
    # The tree is restored either way, because the generators have written over
    # it whether they drifted or not.
    #
    # Restore ONLY the paths this gate is responsible for. It used to run
    # `git checkout -- .` across the whole repository, which discards every
    # uncommitted change in the working tree rather than just the generator
    # output written seconds earlier. The dirty-tree check above makes that
    # safe on a quiet machine, but not on a busy one: on 2026-09-03 six agents
    # were writing to this tree at once, and anything committed to disk between
    # that check and this line would have been destroyed with no record that it
    # ever existed. Two separate agents flagged it independently the same day.
    _restore(worktree_changes())

    # Said out loud whether the gate passed or failed. A partial check that
    # reports like a full one is the failure this whole week has been about:
    # a run that could not look must not read as a clean bill of health.
    if _unchecked:
        warn("generator-ownership", _unchecked)


def gate_every_generator_has_a_protection_plan() -> None:
    """Every ops/build_*.py must be accounted for, not just the ones this
    week happened to find drifting.

    This is the meta version of gate_generator_ownership. That gate has
    named fifteen separate data points since it was written (issue #26 and
    thirteen more found after it), each one a real generator whose committed
    output nobody was re-deriving and comparing. Every single one was found
    the same way: an operator cold-reading one more `ops/*.py` file and
    happening to notice it was not in the list. That method depends on
    someone doing it again, by hand, for the 35th generator and the 50th.

    Ran the audit properly instead of waiting for the sixteenth accident:
    globbed every `ops/build_*.py` file (34 of them, 2026-09-10/11) and
    checked each one against GENERATOR_OWNERSHIP_CHAIN above. 15 were
    outside it. All 15 turned out to already have a real, working gate
    protecting them a different way (a dashboard-visibility check, a live
    count, a dedicated byte-compare), found by grepping every OTHER gate's
    source for each generator's own filename. So today there is no live
    gap. GENERATOR_PROTECTED_ELSEWHERE above is that audit's result, made
    permanent: every name in it was checked, not assumed.

    What this gate actually buys is not today's clean bill of health, it is
    tomorrow's: the day a 35th `ops/build_*.py` is added with no entry in
    either list, this fails immediately, by name, instead of shipping
    unprotected until a future cold-read cycle happens to pick it. And if a
    cited gate is ever renamed or deleted without updating the dict here,
    this fails on that too, rather than silently citing a protection that no
    longer exists. See LEARNINGS.md LRN-0009.
    """
    all_builders = sorted(os.path.basename(p)
                           for p in glob.glob(os.path.join(ROOT, "ops", "build_*.py")))
    if not all_builders:
        fail("generator-protection-plan",
             "no ops/build_*.py files found at all; this check could not run")
        return

    chain = set(GENERATOR_OWNERSHIP_CHAIN)
    unprotected = []
    stale = []
    for f in all_builders:
        if f in chain:
            continue
        cited = GENERATOR_PROTECTED_ELSEWHERE.get(f)
        if not cited:
            unprotected.append(f)
            continue
        missing = [g for g in cited if not callable(globals().get(g))]
        if missing:
            stale.append((f, missing))

    if unprotected:
        fail("generator-protection-plan",
             "%d generator(s) have no protection anywhere, in the ownership "
             "chain or in GENERATOR_PROTECTED_ELSEWHERE: %s. Add the file to "
             "GENERATOR_OWNERSHIP_CHAIN if it can be regenerated and diffed "
             "here, or write a dedicated gate and cite it in "
             "GENERATOR_PROTECTED_ELSEWHERE."
             % (len(unprotected), ", ".join(unprotected)))
    if stale:
        fail("generator-protection-plan",
             "GENERATOR_PROTECTED_ELSEWHERE cites a gate that no longer "
             "exists, so the citation is not actually protecting anything: "
             "%s" % ["%s -> %s" % (f, m) for f, m in stale])


def gate_copy_vs_control() -> None:
    """Copy and the thing it sits next to must agree.

    The book showed $9.99 on every surface while its payment link charged $18,
    and a free offer once sat above a button asking for nineteen dollars. Both
    were found by accident. A price written into prose is checked against the
    catalogue here.
    """
    js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    prices = {round(float(i["price"]), 2) for i in cat
              if isinstance(i.get("price"), (int, float)) and i["price"] > 0}

    bad = []
    for f in all_pages():
        s = io.open(f, encoding="utf-8", errors="replace").read()
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", body)
        # Only a price presented AS the purchase price counts. The first
        # version flagged every dollar figure in prose and produced ten
        # warnings, every one of them legitimate: a bundle saving, a
        # comparison against two editions bought separately, a range on the
        # investor page. A warning that cries wolf trains the reader to skip
        # it, which is worse than not having the warning. So the figure has
        # to sit next to a word that means somebody is being asked to pay.
        buy = re.compile(r"\b(buy|get it|order|checkout|purchase|pay|"
                         r"for just|priced?|costs?)\b", re.I)
        # Thousands separators, because the pattern without them read
        # "$1,200" as "$1" and reported it as a price matching nothing in
        # the catalogue. Not hypothetical: shop.html has carried the
        # CN-INHOME card at $1,200 since the day it was prerendered, and
        # this gate has warned about a "$1" on it ever since. The first
        # $1,200 written in prose (consulting.html, 2026-09-04) produced
        # the same false hit. A standing wrong entry in a warning list is
        # how a warning list stops being read, which is the exact failure
        # this gate's own docstring warns about. `*` rather than `+`
        # covers both the comma-grouped and plain forms in one branch.
        for m in re.finditer(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b", text):
            v = round(float(m.group(1).replace(",", "")), 2)
            if v in prices or v in (0, 20000) or v % 100 == 0:
                continue
            before = text[max(0, m.start() - 55):m.start()]
            if not buy.search(before + text[m.end():m.end() + 55]):
                continue
            # A saving is arithmetic, not a price, and gate_bundle_maths
            # already checks it against the catalogue. Flagging it here too
            # puts a permanent false positive in the warning list, and a
            # warning list with a known-wrong entry is one nobody reads.
            if re.search(r"\bsaved?\b\s*$", before, re.I):
                continue
            # Same reasoning for "bought separately": the sum of real
            # catalogue items' prices, stated as a comparison rather than an
            # offer. gate_bundle_maths already verifies this arithmetic
            # against the live catalogue; flagging it here too is the same
            # permanent false positive as the saving case above.
            if re.search(r"\bseparately\s*(they\s*are|is|are)?\s*$", before, re.I):
                continue
            bad.append((os.path.basename(f), f"${m.group(1)}"))
    if bad:
        uniq = sorted({b for b in bad})[:5]
        warn("copy-vs-control",
             f"{len(bad)} price(s) written in prose that match nothing in the "
             f"catalogue: {uniq}")


def gate_bundle_maths() -> None:
    """The bundle's saving must equal its parts minus its price.

    "Save $17" and "bought separately they are $66" were both true until the
    ebook moved from $18 to $9.99, at which point they quietly became false
    and stayed on the page. Arithmetic printed as marketing copy rots the
    moment any input changes, so it is computed here rather than trusted.
    """
    js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = {i["sku"]: i for i in json.loads(js[js.index("["):js.rindex("]") + 1])}
    parts = ["BK-EB", "MZ-MANUAL", "PACK-HOUSE"]
    if not all(p in cat for p in parts) or "BK-BUNDLE" not in cat:
        return
    apart = round(sum(cat[p]["price"] for p in parts), 2)
    saving = round(apart - cat["BK-BUNDLE"]["price"], 2)

    def money(v):
        return f"${v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"${int(v)}"

    wrong = []
    # Every page, not just the seventeen sitting directly in site/. The same
    # narrow glob has already been found wrong twice in this repository, once
    # in the dashboard's page counters and once in its dead-link count, where
    # it silently skipped the 143 zone, room and article pages and reported
    # "not scanned" as zero. No subdirectory page states a saving today, so
    # this closes a gap rather than fixing a live fault, but a price claim on
    # a zone page would have been exactly as wrong and exactly as unchecked.
    _pages = [f for f in glob.glob(os.path.join(SITE, "**", "*.html"),
                                   recursive=True)
              if os.sep + "downloads" + os.sep not in f]
    for f in sorted(_pages + [os.path.join(SITE, "assets", "js", "data.js")]):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"[Ss]ave \$\s?(\d+(?:\.\d{2})?)", s):
            if abs(float(m.group(1)) - saving) > 0.01:
                wrong.append((os.path.basename(f), f"save ${m.group(1)}",
                              f"should be {money(saving)}"))
        for m in re.finditer(r"separately they are \$\s?(\d+(?:\.\d{2})?)", s):
            if abs(float(m.group(1)) - apart) > 0.01:
                wrong.append((os.path.basename(f), f"separately ${m.group(1)}",
                              f"should be {money(apart)}"))
    if wrong:
        fail("bundle-maths",
             f"{len(wrong)} stated figure(s) disagree with the catalogue: "
             f"{wrong[:3]}")


def gate_affiliate() -> None:
    """Affiliate rules that have a contract behind them, not a preference.

    Amazon's operating agreement prohibits affiliate links in any ebook, PDF
    or offline document. The FTC expects a clear disclosure before the links.
    Both are easy to breach by accident: the book already points readers at
    resource pages, and a page can gain a link long after its copy was
    written.
    """
    code, out = run("affiliate.py", "--check")
    if code != 0:
        first = [l.strip() for l in out.splitlines() if "FAIL" in l][:2]
        fail("affiliate", " / ".join(first) or "affiliate.py --check failed")


def gate_stale_claims() -> None:
    """Claims that were true when written and rot without anyone noticing.

    "Most of the range is still in development" survived on the homepage past
    the day 155 products went live, and it was my own copy. These phrases are
    the ones that go stale, so they are surfaced for a human read rather than
    failed, because any of them can still be legitimately true.
    """
    # UNAMBIGUOUS ROT. Nothing legitimately says these for long.
    rot = re.compile(r"in development|coming soon|not yet available|"
                     r"no analytics|nothing has been sent|"
                     r"still being built|launching soon", re.I)

    # "we have not" USED TO BE IN THAT LIST AND SHOULD NOT HAVE BEEN.
    #
    # It matched seven times on 2026-09-09 and every single hit was an honest
    # disclosure of the kind CLAUDE.md section 8 requires: "we have not run a
    # paid reset day yet, so there is no customer quote to put here", "we have
    # not tested this site with a screen reader", and, in a list of things this
    # business refuses to do, "Claim a result we have not observed". Those are
    # the copy working correctly. Most of them cannot go stale at all, because
    # they describe a standing policy rather than a temporary state.
    #
    # Seven permanent warnings a run is the same failure this gate's own
    # docstring already names about code comments: a warning that cries wolf is
    # one I start skimming, and this gate exists to catch the homepage saying
    # "still in development" the day 155 products went live.
    #
    # So the phrase is dropped, and the two disclosures that genuinely will
    # stop being true are watched by name, each with the event that ends it.
    WILL_CHANGE = [
        ("we have not run a paid reset day",
         "false the day somebody pays for one"),
        ("not tested this site with a screen reader",
         "false the day anybody runs that test"),
    ]
    hits = []
    watched = {}
    for f in all_pages():
        s = io.open(f, encoding="utf-8", errors="replace").read()
        # Strip script and style bodies and HTML comments before looking at
        # the words, because none of them are visitor copy. Without this the
        # gate read a JavaScript comment in contact.html explaining why the
        # form opens a mail client, quoted the words "nothing has been sent
        # yet" out of it, and reported them as a stale public claim. A warning
        # that cries wolf about code comments is a warning I will start
        # skimming, and this one exists to catch real rot on the homepage.
        visible = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", " ", s)
        visible = re.sub(r"(?s)<!--.*?-->", " ", visible)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", visible))
        for m in rot.finditer(text):
            hits.append((os.path.basename(f),
                         text[max(0, m.start() - 40):m.end() + 40].strip()))
        low = text.lower()
        for phrase, ends in WILL_CHANGE:
            if phrase in low:
                watched.setdefault(phrase, [ends, []])[1].append(
                    os.path.basename(f))
    if hits:
        warn("stale-claims",
             f"{len(hits)} phrase(s) that go stale and should be reread. "
             f"First: {hits[0][0]}: {hits[0][1][:90]!r}")
    if watched:
        warn("dated-disclosures",
             "%d honest disclosure(s) still standing, each true today and each "
             "with the event that ends it: %s"
             % (len(watched),
                "; ".join("%r on %d page(s), %s"
                          % (ph, len(v[1]), v[0])
                          for ph, v in sorted(watched.items()))))


def gate_pack_deck_distinct() -> None:
    """The Whole House Print Pack must never be sold as the deck's "same cards".

    B4 (2026-09-08) fixed exactly this false equivalence on deck.html and
    data.js: the Print Pack is the six-pass instruction set for all 114
    micro zones, the Entryway/Kitchen decks are a diagnostic game, and a
    buyer expecting one would be surprised by the other. That fix landed on
    those two surfaces but not on ops/build_deck_gallery.py's own "Getting
    it" copy, which kept shipping "the Whole House Print Pack is the same
    cards for all 114 micro zones" live on site/deck-gallery.html, found by
    an operator cycle reading GitHub issue #31 for an unrelated reason.
    Fixed the generator too. This gate scans every rendered page's visible
    text so a hand edit or a fresh generator cannot reintroduce the same
    false claim unnoticed. "684" is whitelisted nearby, because quest.html
    correctly says the printed pack "is the same 684 cards" as the Quest
    app on screen, which is true: same content, different medium, not the
    deck-vs-pack mismatch this gate exists to catch.
    """
    claim = re.compile(r"same cards", re.I)
    hits = []
    for f in all_pages():
        s = io.open(f, encoding="utf-8", errors="replace").read()
        visible = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", " ", s)
        visible = re.sub(r"(?s)<!--.*?-->", " ", visible)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", visible))
        for m in claim.finditer(text):
            window = text[max(0, m.start() - 150):m.end() + 150]
            if "684" in window:
                continue
            hits.append((os.path.basename(f),
                         text[max(0, m.start() - 60):m.end() + 60].strip()))
    if hits:
        fail("pack-deck-distinct",
             f"{len(hits)} page(s) claim two different products are "
             f"'the same cards', the exact false equivalence B4 fixed once "
             f"already. First: {hits[0][0]}: {hits[0][1][:120]!r}")


def gate_tests() -> None:
    """Run everything in ops/tests. A test nobody runs is not a test.

    Two test files were written this cycle to prove new checks can return more
    than the one verdict the environment happened to be in. Left unwired they
    would have been documentation: correct on the day, silently rotting after.
    """
    files = sorted(glob.glob(os.path.join(ROOT, "ops", "tests", "test_*.py")))
    if not files:
        return
    bad = []
    unverified = []
    # Marks the child as running underneath preflight. test_generator_ownership
    # drives `preflight.py --own` itself, in a throwaway worktree, so without
    # this it would be started here, start another preflight, which would start
    # it again, without bound. It terminated only because creating a worktree
    # inside a worktree happened to fail. A test that recurses into its own
    # runner needs to be told where it is, not left to be stopped by an
    # accident of the filesystem.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "SIXS_UNDER_PREFLIGHT": "1"}
    for f in files:
        r = subprocess.run([sys.executable, f], cwd=ROOT, capture_output=True,
                           text=True, timeout=900, env=env)
        out = r.stdout + r.stderr
        if r.returncode != 0:
            tail = out.strip().splitlines()
            bad.append(f"{os.path.basename(f)}: "
                       f"{tail[-1][:90] if tail else 'no output'}")
        elif "NOT VERIFIED" in out:
            unverified.append(os.path.basename(f))
    if bad:
        fail("tests", f"{len(bad)} of {len(files)} test file(s) failed: {bad[:3]}")
    elif len(files) < 2:
        warn("tests", f"only {len(files)} test file(s) exist")
    # A test that quietly returns 0 because it could not exercise anything
    # (no browser here, say) reads exactly like a test that ran and passed:
    # gate_tests() only ever counted nonzero exits as news. That is the same
    # shape of theatre gate_image_coverage was fixed for in 6.8: a check that
    # cannot tell "confirmed fine" from "never looked" is not a check. This
    # does not fail preflight, since not-verified is not the same claim as
    # broken, but it has to say so out loud rather than merge into "ok".
    if unverified:
        warn("tests-unverified",
             "%d of %d test file(s) ran but could not actually exercise "
             "anything in this environment: %s"
             % (len(unverified), len(files), ", ".join(unverified)))


def gate_conflict_markers() -> None:
    """No file may ship with an unresolved merge conflict in it.

    Written immediately after doing exactly that. A rebase against the cloud
    operator's work conflicted in three generated dashboard files, and resolving
    those with `git add -A` also staged ops/preflight.py, which was still
    conflicted and which nothing had asked about. The commit went through with
    three conflict markers inside the file that runs every other gate. Python
    would not even parse it, so every gate in this file was dead, and the
    commit that broke it was one that added a gate.

    Cheap, absolute, and it would have caught it before the commit.
    """
    pats = ("<" * 7 + " ", ">" * 7 + " ", "=" * 7 + chr(10))
    exts = ("*.py", "*.md", "*.json", "*.html", "*.css", "*.js", "*.yml")
    bad, looked = [], 0
    for ext in exts:
        for f in glob.glob(os.path.join(ROOT, "**", ext), recursive=True):
            rel = os.path.relpath(f, ROOT)
            if rel.startswith((".git", "build" + os.sep + "models")):
                continue
            looked += 1
            try:
                s = io.open(f, encoding="utf-8", errors="replace").read()
            except Exception:                                 # noqa: BLE001
                continue
            if any(s.startswith(p) or (chr(10) + p) in s for p in pats[:2]):
                bad.append(rel)
    if bad:
        fail("conflict-markers",
             f"{len(bad)} of {looked} files scanned contain an unresolved "
             f"merge conflict: {bad[:3]}")


def gate_no_windows_only_redirect() -> None:
    """A shell redirect to the Windows null device is a literal filename
    everywhere else.

    Found in ops/import_generated_art.py, a call that redirected output to
    that device by name to silence fingerprint_assets.py after promoting
    card art. On Linux or macOS, where every cloud session and the
    production VPS actually run, the shell treats that device name as a
    plain filename, so the call would have written a stray file into the
    repo root and the real command's exit code was never checked either
    way. The image route this file drives is Phil's own Windows machine
    today, so nothing has tripped this yet, but a script that only works
    on one contributor's OS is exactly the class of trap CLAUDE.md's own
    Windows/Linux warnings exist for, and it would fail silently rather
    than loudly the first time it runs anywhere else.

    Checked with a window rather than a single regex: the real call site
    spanned three lines with a nested, already-closed os.path.join(...)
    call in the middle, so a naive "os.system([^)]*nul)" stops at that
    inner close-paren and never reaches the redirect at all.
    """
    hits = []
    for f in glob.glob(os.path.join(ROOT, "ops", "*.py")):
        try:
            s = io.open(f, encoding="utf-8").read()
        except Exception:                                        # noqa: BLE001
            continue
        for m in re.finditer(r"os\.system\(", s):
            window = s[m.end():m.end() + 400]
            if re.search(r"[>\s]nul\b", window):
                hits.append(os.path.relpath(f, ROOT))
                break
    if hits:
        fail("windows-only-redirect",
             f"{len(hits)} file(s) redirect os.system() output to the "
             f"Windows-only null device by name, a literal filename on "
             f"Linux/macOS: {hits}")


def gate_browser_detection_portable() -> None:
    """A headless-browser tool that only looks for chrome.exe or msedge.exe
    can never verify anything in the cloud sandbox, silently, every run.

    ops/browser.py's find_browser() exists precisely so a tool can check for
    Edge (Phil's own Windows machine) and fall back to the sandbox's own
    pre-installed Chromium, one lookup covering both. ops/render_cards.py and
    ops/video_zone.py used to hardcode only the Windows paths, which is the
    same shape 6.14 already fixed for the test suite: a prior cycle's own
    reasoning dismissed both as blocked on Desktop-only source art, which is
    true of the card and book art pipelines but not of video_zone.py, whose
    entire input (content.json, the brand fonts) is already committed. Fixed
    both to call find_browser(); verified end to end in this sandbox, not
    just read: render_cards.py rendered and passed all 5 committed card
    fronts, and video_zone.py rendered a real, non-blank 1080x1920 beat.
    build_manual_print.py's own --measure page-count step had the same
    pattern with a softer failure (a print "skipping" line rather than a
    crash), fixed the same way and verified: it now reports real pagination
    (189/189/33/11 pages) instead of skipping every cloud run.

    Any new file reintroducing a hardcoded chrome.exe/msedge.exe path outside
    browser.py itself is this same regression again.
    """
    # browser.py legitimately names both paths, and this gate's own source
    # names them too in order to look for them, so both are self-references
    # rather than the regression being checked for.
    exempt = {"browser.py", "preflight.py"}
    hits = []
    for f in glob.glob(os.path.join(ROOT, "ops", "*.py")):
        if os.path.basename(f) in exempt:
            continue
        try:
            s = io.open(f, encoding="utf-8").read()
        except Exception:                                        # noqa: BLE001
            continue
        if "msedge.exe" in s or "chrome.exe" in s:
            hits.append(os.path.relpath(f, ROOT))
    if hits:
        fail("browser-detection-portable",
             f"{len(hits)} file(s) hardcode a Windows-only browser path "
             f"instead of ops/browser.py's find_browser(), which cannot "
             f"verify anything in the cloud sandbox: {hits}")


def gate_network_calls_have_timeout() -> None:
    """Every urllib.request.urlopen() call must carry an explicit timeout.

    Found 2026-09-06: five urlopen() calls (ops/hourly_brief.py's Stripe
    commerce() closure, ops/stripe_brand.py's call() and upload(),
    ops/stripe_catalog.py's call(), ops/stripe_fulfil.py's call()) had no
    timeout at all. Python's socket default is to wait forever, so a single
    stalled Stripe response would not fail fast, it would hold the job open
    until the workflow's own 20 minute ceiling, once an hour, on the exact
    script that delivers what a paying customer bought. This sandbox never
    caught it: every one of these calls only ever ran here with no credential
    and no route out, so they failed in microseconds and looked identical to
    a call that would have failed just as fast with a real, slow, live one.

    Checked with a paren-balance window rather than a single regex, the same
    lesson gate_no_windows_only_redirect already names: a real call site can
    span several lines with a nested, already-closed Request(...) in the
    middle, and a naive "urlopen([^)]*)" stops at that inner close-paren.

    preflight.py itself is exempt, the same way gate_browser_detection_portable
    exempts itself: this gate's own source names the pattern it looks for, in
    its docstring and in the regex literal, and both would otherwise flag
    themselves. Its one real call (gate_agents_in_sync's own urlopen) already
    carries a timeout.
    """
    hits = []
    for f in glob.glob(os.path.join(ROOT, "ops", "*.py")):
        if os.path.basename(f) == "preflight.py":
            continue
        try:
            s = io.open(f, encoding="utf-8").read()
        except Exception:                                        # noqa: BLE001
            continue
        for m in re.finditer(r"urlopen\(", s):
            depth, i = 1, m.end()
            while i < len(s) and depth > 0:
                if s[i] == "(":
                    depth += 1
                elif s[i] == ")":
                    depth -= 1
                i += 1
            if "timeout" not in s[m.end():i]:
                line = s[:m.start()].count("\n") + 1
                hits.append(f"{os.path.relpath(f, ROOT)}:{line}")
    if hits:
        fail("network-calls-have-timeout",
             f"{len(hits)} urlopen() call(s) with no timeout, which would "
             f"hang a scheduled job rather than fail fast on a stalled "
             f"remote server: {hits}")


def gate_stripe_price_claims() -> None:
    """No price stated in a Stripe product description may be invented.

    Found 2026-09-07 by QA opening the actual checkout page rather than the
    catalogue. The Complete Digital Bundle's Stripe description read "Bought
    separately they are $66." The three components are $9.99, $29 and $19,
    which is $57.99. So the saving was presented as $17.00 at the point of
    payment when it is $8.99, on a site whose how-we-make-money page promises
    never to use a manufactured discount. CLAUDE.md section 37 rules out
    fabricated price comparisons by name.

    The site's own copy was correct; only Stripe's was wrong, and nothing
    checked Stripe's, because every existing price check compares the
    catalogue to the payment link AMOUNT and never reads the words on the page
    the buyer is looking at.

    Every dollar figure in an active product description must be either a
    catalogue price or the exact sum of the bundle's components. Warns rather
    than fails: it describes the Stripe account and cannot run without a
    credential, and no credential reports UNCHECKED rather than clean.
    """
    import re as _re
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import stripe_catalog as sc
        prods = [p for p in sc.list_all("products") if p.get("active")]
        src = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                      encoding="utf-8").read()
    except (Exception, SystemExit) as e:                        # noqa: BLE001
        # secret_key() in stripe_catalog.py reports a missing credential with
        # sys.exit(), which raises SystemExit, not Exception. Found
        # 2026-09-07: this gate caught only Exception, the exact shape
        # gate_stripe_one_product_per_sku's own docstring already names and
        # fixed a few lines below, so the missing-credential case crashed to
        # a hard FAIL here instead of the documented warn/UNCHECKED. Catch
        # it explicitly, the same way.
        warn("stripe-price-claims",
             "could NOT read Stripe product descriptions (%s). Unchecked, not "
             "clean: a made-up saving sits on the checkout page, where the "
             "site's own copy checks cannot see it." % type(e).__name__)
        return
    prices = {float(x) for x in _re.findall(r'"price"\s*:\s*([0-9.]+)', src)}
    # A bundle may legitimately quote the sum of its parts.
    sums = {round(sum(c), 2) for c in
            [[a, b, c2] for a in prices for b in prices for c2 in prices]} if len(prices) < 40 else set()
    bad = []
    for p in prods:
        for amt in _re.findall(r"\$([0-9]+(?:\.[0-9]{2})?)", p.get("description") or ""):
            v = float(amt)
            if v not in prices and v not in sums:
                bad.append((p.get("name", "")[:36], v))
    if bad:
        warn("stripe-price-claims",
             "%d price figure(s) in Stripe product descriptions match no "
             "catalogue price and no sum of catalogue prices, so a buyer is "
             "reading a number we do not charge: %s" % (len(bad), bad[:3]))


def gate_stripe_one_product_per_sku() -> None:
    """Every SKU must resolve to exactly one active Stripe product.

    Found 2026-09-06 by reading checkout SESSIONS rather than the catalogue.
    Seven of the twenty sessions this business has ever had were for $18.00, an
    amount that appears nowhere in our price list. BK-EB had two active product
    objects, each with its own price and its own LIVE payment link: $9.99 on the
    one the site serves and $18.00 on a second one still purchasable by anyone
    holding the URL. Seven people opened that checkout, saw $18 where the page
    had promised $9.99, and left without typing an email.

    The cause was a pagination bug in stripe_catalog.py that created a duplicate
    product per SKU once the catalogue passed a hundred entries. The duplicate
    LINKS were cleaned up when they were found; the duplicate PRODUCTS were not,
    and one of them kept a live checkout at the wrong price for weeks.

    A duplicate is also why nothing is idempotent: find_by_sku returns product A
    while the live link sells a price belonging to product B, so every run
    decides the link is wrong and replaces it.

    Warns rather than fails: it describes the Stripe account, not this commit,
    and it cannot run at all without a credential. No credential reports
    UNCHECKED, never clean, because unchecked is not the same as one per SKU.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import stripe_dedupe
        dupes = stripe_dedupe.duplicates()
    except (Exception, SystemExit) as e:                        # noqa: BLE001
        # secret_key() in stripe_catalog.py reports a missing credential with
        # sys.exit(), which raises SystemExit, not Exception. This gate is
        # meant to warn on exactly that case, not join the crash: catch it
        # explicitly. See run_gate()'s own docstring for the wider fix.
        warn("stripe-one-per-sku",
             "could NOT check whether every SKU has one active Stripe product "
             "(%s: %s). Unchecked, not clean: a duplicate is a second live "
             "checkout at a price nobody approved."
             % (type(e).__name__, str(e)[:80]))
        return
    if dupes:
        warn("stripe-one-per-sku",
             "%d SKU(s) have more than one active Stripe product, so a second "
             "live checkout may exist at a different price: %s. Fix with "
             "STRIPE_ALLOW_LIVE=1 python ops/stripe_dedupe.py --apply"
             % (len(dupes), sorted(dupes)[:4]))


def gate_live_links() -> None:
    """The buy buttons on the LIVE site must point at links Stripe honours.

    On 2026-08-30 all six payment links the live site served were
    deactivated in Stripe. The business could not take money and had not
    been able to for days. Nothing caught it because every existing check
    was true: the page returned 200, and a deactivated Stripe link returns
    200 as well, serving the same JavaScript shell as a working one and
    resolving to "no longer active" only in the browser. ops/check_sellable.py
    checks the repository, where the links are correct, which is exactly
    what made this invisible.

    A warning rather than a failure, because it describes production rather
    than this commit, and a commit is not wrong because a deploy has not
    happened. But it is the loudest thing in the file when it fires.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import check_live_links
        r = check_live_links.check()
    except Exception as e:                                    # noqa: BLE001
        warn("live-links", f"the live payment link check could not run: "
                           f"{type(e).__name__}: {e}. Not the same as the "
                           f"buttons working.")
        return
    if r["verdict"] == "dead":
        warn("live-links",
             f"REVENUE OUTAGE: {len(r['dead'])} of {len(r['slugs'])} payment "
             f"link(s) on the live site are deactivated in Stripe. Anybody "
             f"clicking buy reaches a dead link. Deploying the current build "
             f"fixes it; the repository's links are active.")
    elif r["verdict"] == "unknown":
        warn("live-links", f"live payment links could not be verified: "
                           f"{r['note'] or 'unknown reason'}")


def gate_stripe_brand() -> None:
    """Issue #21: the live Stripe account's public identity must be 6S
    Success, not Ledgerium's, and must not preach the rejected "Set in
    Order" over this project's own "Straighten".

    Found 2026-08-21: the account's business_profile.url, .name and
    .product_description all read as Ledgerium AI's, an unrelated company
    sharing the same sole-proprietor Stripe legal entity (see CLAUDE.md
    36b). Backlog 2.8 verified .url, .name and .support_email fixed
    2026-09-06, but nothing had ever checked .product_description itself,
    the field the issue's own finding actually quoted in full ("Ledgerium
    AI's... workflow documentation platform"), and no gate existed to
    notice if any of the four drifted back. ops/stripe_brand.py's own
    check() only ever compared .url and .support_email; extended
    2026-09-07 to cover .name and .product_description too.

    Warns rather than fails, the same reasoning as gate_ledgerium and
    gate_stripe_one_product_per_sku: this describes the Stripe account,
    not this commit, and no sandbox this project has run in has ever held
    a Stripe credential.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import stripe_brand
        r = stripe_brand.check()
    except (Exception, SystemExit) as e:                          # noqa: BLE001
        warn("stripe-brand",
             "could NOT check the Stripe account's public business identity "
             "(%s: %s). Unchecked, not clean: this is the field issue #21's "
             "own Ledgerium finding lived in." % (type(e).__name__, str(e)[:80]))
        return
    if r["gaps"]:
        warn("stripe-brand",
             "%d business-identity gap(s) on the live Stripe account: %s. "
             "python ops/stripe_brand.py --check for detail."
             % (len(r["gaps"]), "; ".join(g[0] for g in r["gaps"][:4])))


def gate_stripe_write_tools_guarded() -> None:
    """Every Stripe tool that can write to a live account on --apply must
    refuse to do so without STRIPE_ALLOW_LIVE=1.

    Found 2026-09-10, cold-reading the money-domain ops/*.py tier per step
    5d: stripe_catalog.py, stripe_dedupe.py, stripe_invoice.py and
    stripe_setup.py all carry `if live and apply_it and
    os.environ.get("STRIPE_ALLOW_LIVE") != "1": refuse`, the guard CLAUDE.md
    37 exists for. stripe_links.py did not: `main()` printed "Mode: LIVE"
    and went straight to creating a real payment link on --apply with no
    second look at all, the one write tool of five with nothing standing
    between a live secret key and a real object. Its own two consulting
    SKUs are managed under a different identity by stripe_catalog.py since
    2026-08-27 (metadata.sku, not this file's lookup_key), so a live
    --apply run here would not fix or update the live checkout, it would
    create a second, orphaned one beside it: the same duplicate-checkout
    shape that once left a live page charging $18 next to an advertised
    $9.99. Fixed by adding the missing guard; this is what stops a future
    Stripe tool shipping the same gap unnoticed. Static: reads source only,
    no credential or network needed, so it runs in every sandbox.

    stripe_brand.py is deliberately exempt, checked directly rather than
    assumed from the pattern: it accepts `--apply` and defines an `upload()`
    that POSTs a file to Stripe, but `main()`'s own apply_it branch only
    draws and saves two PNGs under build/ and never calls upload() at all;
    its own printed output says the account-level POST is refused on your
    own account and that Phil uploads the icon by hand in the Dashboard.
    `--apply` here reaches no network write today. If that ever changes,
    this file becomes indistinguishable from the others by the same read
    and should stop being exempt.
    """
    EXEMPT = {
        "stripe_brand.py": "checked directly: --apply never reaches "
                            "upload(), the file's only live write",
    }
    for fname in sorted(os.listdir(os.path.join(ROOT, "ops"))):
        if not (fname.startswith("stripe_") and fname.endswith(".py")):
            continue
        if fname in EXEMPT:
            continue
        path = os.path.join(ROOT, "ops", fname)
        try:
            src = io.open(path, encoding="utf-8").read()
        except OSError:
            continue
        if "apply_it" not in src and "--apply" not in src:
            continue          # read-only tool, e.g. stripe_check.py
        if "STRIPE_ALLOW_LIVE" not in src:
            fail("stripe-write-tools-guarded",
                 "ops/%s can write with --apply but never checks "
                 "STRIPE_ALLOW_LIVE: a live secret key with nothing else "
                 "in the way. See ops/stripe_setup.py for the pattern to "
                 "copy." % fname)


def gate_dashboard_severity() -> None:
    """The dashboard's headline must escalate when the live site cannot take money.

    ops/dashboard.py's overall RED/YELLOW/GREEN verdict used to look only at
    whether the repository *could* take payment, never at whether
    check_live_links.py had actually confirmed the live site's payment links
    were dead. A confirmed revenue outage could sit under a YELLOW headline
    driven only by open P0 count, while the body two lines down already said
    "NO, live payment links are deactivated in Stripe": headline and copy
    disagreeing, which CLAUDE.md's own rule treats as a P0 trust defect, not
    a polish item. Found 2026-08-31 by reproducing it: monkeypatching
    check_live_links.check() to return "dead" left S["overall"] at YELLOW.

    Calls the real status_of() with synthetic inputs after dashboard.py has
    already run its own real import once, so this proves the decision logic
    itself escalates without re-triggering or corrupting the real generated
    files with fake data.

    status_of() has six distinct outcomes. Until 2026-09-06 only two were
    ever exercised anywhere (this gate's dead-links case, and
    gate_dashboard_live_links_carry_forward's carried-dead case): both are
    RED. The other four (no payment route at all, an unreachable GitHub,
    an open-P0 count, and the plain GREEN fallback) had never once been
    proven to return what their own name promises, on the single function
    that decides the one line an owner reads first. Added here rather than
    a separate gate, since it is the same pure function this gate already
    imports and the same synthetic-input pattern.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    status, why = dashboard.status_of(True, True, "dead", True, 0)
    if status != "RED":
        fail("dashboard-severity",
             f"dashboard.status_of() returned {status!r} for a confirmed "
             f"dead live-links verdict with 0 open P0s; must be RED, "
             f"because the live site cannot take money regardless of issue "
             f"count. Got why={why!r}")
    status, _ = dashboard.status_of(False, False, "unknown", True, 0)
    if status != "RED":
        fail("dashboard-severity",
             f"dashboard.status_of() returned {status!r} when there is no "
             f"revenue this month and the repository cannot take payment "
             f"at all; must be RED, because that is no route from customer "
             f"intent to payment.")
    status, why = dashboard.status_of(True, True, "unknown", False, 0)
    if status != "YELLOW" or "UNKNOWN" not in why.upper():
        fail("dashboard-severity",
             f"dashboard.status_of() returned {status!r}/{why!r} when "
             f"GitHub could not be reached; must be YELLOW and say issue "
             f"counts are unknown, never silently read as zero open issues.")
    status, why = dashboard.status_of(True, True, "unknown", True, 4)
    if status != "YELLOW" or "4" not in why:
        fail("dashboard-severity",
             f"dashboard.status_of() returned {status!r}/{why!r} for 4 open "
             f"P0 items with everything else healthy; must be YELLOW and "
             f"name the count.")
    status, why = dashboard.status_of(True, True, "unknown", True, 0)
    if status != "GREEN":
        fail("dashboard-severity",
             f"dashboard.status_of() returned {status!r} for a fully "
             f"healthy input (revenue exists, payment works, links not "
             f"known dead, GitHub reachable, 0 open P0s); must be GREEN. "
             f"Got why={why!r}. A function that cannot reach its own best "
             f"case cannot be trusted for its worst one.")


def gate_dashboard_live_links_carry_forward() -> None:
    """A confirmed dead live-links verdict must survive an unmeasured run.

    Found 2026-08-31 by direct observation, not by reasoning about it: this
    exact cycle's own preflight run flipped the committed ops/state.json's
    live_links_verdict from "dead" (measured 2026-08-30 19:23 by a session
    with real Stripe access) to "unknown", because ops/dashboard.py had no
    persistence for this value and no Stripe credential exists in this
    sandbox. status_of() then reported YELLOW instead of RED for a business
    whose live payment links were, as far as anyone had verified, still
    deactivated. Fixed with resolve_live_links_verdict(): only a run that
    actually reaches Stripe may overwrite the standing "dead" answer.

    Proves the pure function itself, with synthetic inputs, the same pattern
    gate_dashboard_severity uses for status_of().
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    out = dashboard.resolve_live_links_verdict(
        "unknown",
        {"live_links_last_verdict": "dead",
         "live_links_verified_at": "2026-08-30 19:23"},
        "2026-08-31 09:00")
    if out.get("live_links_verdict") != "dead":
        fail("dashboard-live-links-carry-forward",
             f"resolve_live_links_verdict() dropped a confirmed dead verdict "
             f"on an unmeasured run instead of carrying it forward; got "
             f"{out!r}")
    status, _ = dashboard.status_of(True, True, out.get("live_links_verdict"),
                                    True, 0, out.get("live_links_carried_from"))
    if status != "RED":
        fail("dashboard-live-links-carry-forward",
             f"carried-forward dead verdict did not escalate status_of() to "
             f"RED; got {status!r}")
    # An "ok" verdict must never be carried forward as if freshly reconfirmed.
    stale_ok = dashboard.resolve_live_links_verdict(
        "unknown",
        {"live_links_last_verdict": "ok",
         "live_links_verified_at": "2026-08-30 19:23"},
        "2026-08-31 09:00")
    if stale_ok.get("live_links_verdict") == "ok":
        fail("dashboard-live-links-carry-forward",
             f"resolve_live_links_verdict() borrowed a stale 'ok' verdict as "
             f"if it were fresh; got {stale_ok!r}")


def gate_dashboard_deploy_carry_forward() -> None:
    """A carried-forward deploy verdict must carry its own numbers with it.

    One layer under gate_dashboard_live_links_carry_forward, same shape of
    bug: dashboard.py already carried deploy_verdict ("stale") across an
    unmeasured run, but until 2026-08-31 left deploy["stale_assets"]/
    ["checked_assets"] at this run's own unmeasured 0/0 default, so the
    generated dashboard read "Production is serving an older build: 0 of 0
    assets on the live homepage differ" -- a still-stale verdict next to a
    number that says nothing differs. Found by reading that exact sentence,
    the same way 6.9/6.10/6.11 were each found by reading a sentence rather
    than trusting a word next to it.

    Proves the pure function itself, with synthetic inputs, the same pattern
    gate_dashboard_live_links_carry_forward uses for resolve_live_links_verdict.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    out = dashboard.resolve_deploy_verdict(
        {"verdict": "unknown", "stale_assets": 0, "checked_assets": 0},
        {"deploy_last_verdict": "stale", "deploy_verified_at": "2026-08-30 23:03",
         "deploy_stale_assets": 4, "deploy_checked_assets": 4},
        "2026-08-31 09:00")
    if out.get("deploy_verdict") != "stale":
        fail("dashboard-deploy-carry-forward",
             f"resolve_deploy_verdict() dropped a carried 'stale' verdict; "
             f"got {out!r}")
    if out.get("deploy_stale_assets") != 4 or out.get("deploy_checked_assets") != 4:
        fail("dashboard-deploy-carry-forward",
             f"resolve_deploy_verdict() carried the verdict word 'stale' but "
             f"not the asset counts behind it; an unmeasured run must not "
             f"report '0 of 0 differ' under a still-stale headline. Got "
             f"{out!r}")
    # A real measurement this run must always win over anything carried.
    fresh = dashboard.resolve_deploy_verdict(
        {"verdict": "current", "stale_assets": 0, "checked_assets": 4},
        {"deploy_last_verdict": "stale", "deploy_stale_assets": 4,
         "deploy_checked_assets": 4},
        "2026-08-31 09:00")
    if fresh.get("deploy_verdict") != "current" or fresh.get("deploy_stale_assets") != 0:
        fail("dashboard-deploy-carry-forward",
             f"resolve_deploy_verdict() let a stale carried value override a "
             f"fresh real measurement; got {fresh!r}")
    # The case that broke in production the first time this fix was merged:
    # a sibling session with real egress measured for real, but is running a
    # dashboard.py that predates this fix, so its state.json only ever holds
    # the number inside the nested "deploy" dict, never the flat keys.
    sibling = dashboard.resolve_deploy_verdict(
        {"verdict": "unknown", "stale_assets": 0, "checked_assets": 0},
        {"deploy_last_verdict": "stale", "deploy_verified_at": "2026-08-30 23:55",
         "deploy": {"verdict": "stale", "stale_assets": 4, "checked_assets": 4}},
        "2026-08-31 09:00")
    if sibling.get("deploy_stale_assets") != 4 or sibling.get("deploy_checked_assets") != 4:
        fail("dashboard-deploy-carry-forward",
             f"resolve_deploy_verdict() could not recover a real measurement "
             f"recorded only in the nested 'deploy' dict by a sibling session "
             f"running an older dashboard.py, and fell back to this run's own "
             f"unmeasured 0/0 instead. Got {sibling!r}")


def gate_dashboard_working_tree() -> None:
    """A failed git status/rev-list must never render as "clean, in sync".

    Same failure direction gate_dashboard_severity and
    gate_dashboard_live_links_carry_forward already guard against for other
    fields: dashboard.py's S["clean"] and S["ahead"] came from sh(), which
    swallows a nonzero exit or a raised exception into the same empty string
    a genuinely clean tree or a genuinely zero-ahead count produces. A git
    failure (no origin/main ref reachable, the exact "unrelated histories"
    checkout state issue #27 names) would then read as "clean and in sync"
    on the dashboard, the opposite of what actually happened. Found
    2026-08-31 by reading dashboard.py's own stated rule for GitHub issue
    counts ("a failed API call must never render as zero open issues") and
    checking whether the git block above it followed the same rule; it did
    not. Fixed with sh_checked(), which returns None on failure instead of
    "", and working_tree_status(), a pure function so this gate can prove
    the decision without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    # The mechanism: a git command that fails outright must come back as
    # None, distinguishable from a command that succeeds with genuinely
    # empty output. A bad ref is a deterministic, real failure, not a
    # simulated one.
    failed = dashboard.sh_checked(
        "git rev-list --count refs/heads/this-branch-does-not-exist..HEAD")
    if failed is not None:
        fail("dashboard-working-tree",
             f"sh_checked() on a command with no such ref returned "
             f"{failed!r} instead of None; a git failure would collapse "
             f"into the same value a real, empty success produces.")
    ok = dashboard.sh_checked("git rev-list --count HEAD..HEAD")
    if ok is None:
        fail("dashboard-working-tree",
             "sh_checked() on a command that genuinely succeeds with empty "
             "output returned None; the gate above would otherwise pass by "
             "sh_checked() always returning None.")
    # The formatting: unmeasured git state (None) must never render as
    # good news, and measured-clean state must still render as clean.
    for clean, ahead in [(None, "0"), (True, None), (None, None)]:
        status = dashboard.working_tree_status(clean, ahead)
        if status == "clean, in sync":
            fail("dashboard-working-tree",
                 f"working_tree_status({clean!r}, {ahead!r}) returned "
                 f"'clean, in sync'; an unmeasured git state must read as "
                 f"'could not be checked', not as good news.")
    if dashboard.working_tree_status(True, "0") != "clean, in sync":
        fail("dashboard-working-tree",
             "working_tree_status(True, '0') did not report clean when the "
             "tree genuinely is; the gate above would otherwise pass by "
             "always returning the same string.")


def gate_dashboard_shallow_commits() -> None:
    """A shallow clone must never report a truncated commit total as real.

    Found 2026-08-31: this environment's checkout is shallow on most cycles
    (issue #27), and `git log --format=%h | wc -l` does not fail on a
    shallow repo, it just silently stops at the shallow boundary. This
    cycle's own dashboard read "56 of 56 total" (implying every commit ever
    made happened in the last 7 days); unshallowing revealed the true total
    is 575. Same failure direction as every other dashboard field this week:
    a plausible wrong number standing in for one the run could not actually
    measure. Fixed by having dashboard.py attempt a best-effort unshallow
    before counting, and report the total as explicitly unknown, never the
    truncated figure, if unshallowing did not succeed.

    Proves the pure formatting function with a synthetic None, the same
    pattern working_tree_status uses above.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    unknown = dashboard.commits_total_text(None)
    if unknown.strip().isdigit():
        fail("dashboard-shallow-commits",
             f"commits_total_text(None) returned {unknown!r}, which reads "
             f"as a real count; an unresolved shallow clone must render as "
             f"an explicit unknown, not a number nobody measured.")
    real = dashboard.commits_total_text(575)
    if real != "575":
        fail("dashboard-shallow-commits",
             f"commits_total_text(575) returned {real!r} instead of '575'; "
             f"the gate above would otherwise pass by always returning the "
             f"same unknown string regardless of input.")


def gate_dashboard_shallow_commits_7d() -> None:
    """The same shallow-boundary undercount, one field over from the gate above.

    Found 2026-08-31 (cycle 18) as a single "52" against a real 397, dismissed
    that day as an unreproduced timing artifact. Reproduced identically the
    next cycle: dashboard.py computed commits_7d from `git log --since="7 days
    ago"` BEFORE its own unshallow attempt ran, one line below, which only
    ever protected commits_total. On this environment's normal shallow
    checkout (issue #27), that let commits_7d silently stop at the shallow
    boundary and print a plausible, wrong, small number instead of erroring
    or reporting unknown, exactly the failure direction 6.13 already fixed
    for the field next to it. Fixed by moving the unshallow attempt ahead of
    both counts and giving commits_7d the same None-means-unknown contract
    commits_total already had.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    unknown = dashboard.commits_7d_text(None)
    if unknown.strip().isdigit():
        fail("dashboard-shallow-commits-7d",
             f"commits_7d_text(None) returned {unknown!r}, which reads as a "
             f"real count; an unresolved shallow clone must render as an "
             f"explicit unknown, not a number nobody measured.")
    real = dashboard.commits_7d_text(52)
    if real != "52":
        fail("dashboard-shallow-commits-7d",
             f"commits_7d_text(52) returned {real!r} instead of '52'; the "
             f"gate above would otherwise pass by always returning the same "
             f"unknown string regardless of input.")


def gate_dashboard_deck_readiness() -> None:
    """The Entryway deck line must not read as broken when the PDF is shipped.

    Found regenerating the command deck 2026-08-31: this run's local
    build/cards-rendered/ cache (a gitignored, per-checkout artifact
    render_cards.py populates only with a real Chromium on hand) was empty,
    and the dashboard's own Entryway deck line hardcoded a stale total of 88
    and reported the bare result as "0/88 cards render clean from the
    template layer". Two problems stacked: 88 has not been the deck's real
    count since issue #29 withheld 16 defective cards on 2026-08-30 (the
    live gallery serves 72), and "0/88" reads exactly like the print product
    is broken when site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf is
    already built and shipped, this run simply never repopulated the local
    cache that feeds it. Same failure direction as every other carried field
    on this page. Fixed with dashboard.cards_total read from the live
    gallery's own index rather than a hardcoded number, and a pure
    deck_readiness_line() this gate proves directly.

    Proves both directions: an unshipped, unrendered deck must still read
    as a real "0/N" (not silently suppressed), and a shipped-but-locally-
    unrendered deck must not read as broken.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    broken = dashboard.deck_readiness_line(0, 72, False)
    if "0/72" not in broken:
        fail("dashboard-deck-readiness",
             f"deck_readiness_line(0, 72, False) returned {broken!r}; an "
             f"unshipped, unrendered deck must still report the real 0/N, "
             f"not be suppressed by the shipped-PDF exception.")
    shipped = dashboard.deck_readiness_line(0, 72, True)
    if "0/72" in shipped or "72" not in shipped:
        fail("dashboard-deck-readiness",
             f"deck_readiness_line(0, 72, True) returned {shipped!r}; a "
             f"deck whose PDF is already shipped must not read as broken "
             f"just because this run's local render cache is empty.")


def gate_deploy_fresh() -> None:
    """Warn when production is not serving what this repository contains.

    A warning rather than a failure, deliberately. Nothing in a commit is wrong
    because the last deploy has not happened, so failing the gate would block
    work for a reason the work did not cause. But it belongs here, because this
    is the file somebody reads before shipping, and "the last three things you
    shipped are not live" is exactly what you want to know at that moment.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import deploy_freshness
        r = deploy_freshness.check()
    except Exception as e:                                    # noqa: BLE001
        warn("deploy-fresh", f"the freshness check could not run: "
                             f"{type(e).__name__}: {e}. That is not the same "
                             f"as production being current.")
        return
    if r["verdict"] == "unknown":
        warn("deploy-fresh", "6s-success.com could not be reached from here, "
                             "so freshness was not measured. Not the same as "
                             "current.")
    elif r["verdict"] == "stale":
        warn("deploy-fresh",
             f"production is serving an older build: {r['stale_assets']} of "
             f"{r['checked_assets']} assets differ. Looked at "
             f"{'; '.join(r['probes'])}.")


def gate_scheduled_delivery_phase() -> None:
    '''A daily email must ARRIVE when it says, not merely fire every 24 hours.

    gate_scheduled_workflow_cadence watches the GAP between runs, which is the
    right check for an hourly job and blind to this one. A daily workflow can
    land three hours after its cron every single day and still show a perfect
    24 hour gap, because both ends of the gap slip together.

    Measured 2026-09-11 over 18 scheduled runs: linkedin-drafts.yml fired at a
    cron commented '08:19 America/Denver' and delivered at about 11:50 Denver,
    median 3.53 hours late, never early. That is the one email whose whole
    purpose is to be read before the day starts, and LinkedIn is the largest
    identifiable source of visitors this site has: 8 people in 30 days against
    1 from Google. It had been arriving at lunchtime for weeks, and the cadence
    check reported it healthy throughout, correctly, because it was.

    The cron is now set early on purpose to compensate. That compensation is
    fitted to GitHub's current queueing and goes stale when that changes, at
    which point the mail starts arriving at 04:47 Denver instead. So the
    promise is written in the workflow as `# lands-at: HH:MM UTC` and this
    re-measures it. A workflow making no such promise is not judged.
    '''
    try:
        sys.path.insert(0, os.path.join(ROOT, 'ops'))
        import check_cron_cadence as CC
        import statistics
    except Exception as e:                                    # noqa: BLE001
        warn('delivery-phase', 'the delivery-phase check could not run: '
             '%s: %s. Not the same as every daily mail arriving on time.'
             % (type(e).__name__, e))
        return

    for wf in CC.WORKFLOWS:
        want = CC.intended_landing(wf)
        if not want:
            continue
        times = CC.scheduled_times(wf)
        if not times:
            warn('delivery-phase',
                 '%s promises a landing time but has no cron naming an hour, '
                 'so the promise cannot be checked' % wf)
            continue
        runs = CC.fetch_runs(wf)
        if not runs:
            warn('delivery-phase',
                 'could not read run history for %s, so its promised landing '
                 'time of %02d:%02d UTC is UNVERIFIED. That is not the same '
                 'as verified on time.' % (wf, want[0], want[1]))
            continue
        # Only runs since the workflow last changed. A cron edit makes every
        # earlier run unrepresentative, and without this the gate warns for
        # days after a legitimate schedule change.
        changed = CC.last_changed(wf)
        fresh = CC.runs_since(runs, changed)
        # Display only, always UTC: `changed` is `git log --format=%cI`, the
        # committer's own local offset (Denver, currently -06:00). Printing
        # it verbatim and truncating away the offset, as this message did
        # until 2026-09-12, reads as UTC next to a message that states every
        # other time in UTC, and is off by up to 6 hours: this workflow's own
        # 09:11 local change looked like it landed before its 10:47 UTC cron
        # fire and briefly read as a missed run it was not, while an actual
        # miss beyond this comment's own escalation could equally read as
        # merely unverified. `runs_since`/`most_recent_due` compare the real
        # tz-aware instants and are unaffected; this only fixes what a human
        # or a future gate reads off the printed string.
        changed_utc = None
        if changed:
            try:
                changed_utc = dt.datetime.fromisoformat(changed).astimezone(
                    dt.timezone.utc).strftime('%Y-%m-%dT%H:%M UTC')
            except ValueError:
                changed_utc = None
        changed_display = changed_utc or 'unknown'
        if len(fresh) < 3:
            # A due moment can fall well after the cron changed and well
            # before now, with nothing landed against it. That is not the
            # same as "hasn't had its first chance yet" and needs a louder
            # message, or it reads as routine every single hour it is left.
            GRACE_MINUTES = 8 * 60  # comfortably above every measured
            # worst-case landing delay recorded for these workflows (about
            # 6.1 hours), so a real fire still inside normal queueing delay
            # is not mistaken for a miss.
            due = None
            if changed:
                try:
                    cut = dt.datetime.fromisoformat(changed)
                    due = CC.most_recent_due(times)
                    if due and due.tzinfo is None:
                        due = due.replace(tzinfo=dt.timezone.utc)
                    if not (due and due > cut):
                        due = None
                except ValueError:
                    due = None
            if due is not None:
                overdue_min = (dt.datetime.now(dt.timezone.utc)
                               - due).total_seconds() / 60.0
                if overdue_min > GRACE_MINUTES and not fresh:
                    warn('delivery-phase',
                         '%s changed at %s and was due to fire at %s UTC, '
                         '%.1f hours ago, with zero scheduled runs recorded '
                         'since: this looks like a MISSED cron fire, not '
                         'merely an unverified promise.'
                         % (wf, changed_display, due.strftime('%Y-%m-%d %H:%M'),
                            overdue_min / 60))
                    continue
            warn('delivery-phase',
                 '%s changed at %s and has only %d scheduled run(s) since, so its promised landing of %02d:%02d UTC is NOT YET VERIFIED. Re-check once it has run a few times.'
                 % (wf, changed_display, len(fresh),
                    want[0], want[1]))
            continue
        late = CC.landing_minutes(fresh, times)
        if not late:
            warn('delivery-phase',
                 'no scheduled run of %s could be matched to a cron time, so '
                 'its landing is UNVERIFIED' % wf)
            continue
        fire = times[0][0] * 60 + times[0][1]
        landed = int(fire + statistics.median(late)) % 1440
        target = want[0] * 60 + want[1]
        off = min((landed - target) % 1440, (target - landed) % 1440)
        if off > 90:
            msg = ('%s promises to land at %02d:%02d UTC and actually lands '
                   'at about %02d:%02d UTC, %d minutes off, measured over %d '
                   'run(s). Either the cron compensation has gone stale or '
                   'the promise has, and whoever reads that file is being '
                   'told the wrong time.')
            warn('delivery-phase', ''.join(msg)
                 % (wf, want[0], want[1], landed // 60, landed % 60,
                    off, len(late)))


def check_schedule_past_comments(workflow_texts: dict) -> list:
    """Find every 'NN past' comment claim that disagrees with the real cron minute.

    Found 2026-09-12, cold-reading status-email.yml: its cron minute moved
    from :10 to :23 on 2026-08-31 (f879787d), to dodge a congested minute,
    the same fix hourly-brief.yml and fulfil-orders.yml got the same day.
    The inline trailing comment on the cron line itself was updated to '23
    past', but the block comment three lines above still read 'Ten past',
    unnoticed because nothing had ever compared the two: the exact
    "source corrected, artifact never re-derived" class this repository's
    own gates already catch in dozens of other shapes, just not yet in a
    workflow's own schedule comment.

    The real regression used a spelled-out word ("Ten past"), not a digit, so
    this must parse both, reusing `_spelled_number` (already proved against
    `gate_deck_count`'s own cardinal-word cases) rather than a second,
    divergent word list.

    Pure function, no filesystem access, so it is testable directly: the
    caller passes {filename: raw text}.
    """
    phrase_re = re.compile(r"\b([A-Za-z]+(?:[\s-]+[A-Za-z]+)?|\d{1,2})"
                           r"\s+past\b", re.I)
    problems = []
    for name, text in workflow_texts.items():
        minutes = set()
        for line in re.findall(r"cron:\s*'([^']+)'", text):
            fields = line.split()
            if len(fields) == 5:
                minutes.update(int(m) for m in fields[0].split(",") if m.isdigit())
        if not minutes:
            continue
        for phrase in phrase_re.findall(text):
            n = int(phrase) if phrase.isdigit() else _spelled_number(phrase)
            if n is not None and n not in minutes:
                problems.append(
                    "%s: a comment says '%s past' but the real cron "
                    "minute(s) are %s" % (name, phrase, sorted(minutes)))
    return problems


def gate_schedule_comment_minute_current() -> None:
    """A workflow's own comment must name the minute its cron actually fires.

    See check_schedule_past_comments for the incident this exists to catch.
    Scans every file in .github/workflows/, not a fixed list, so a future
    scheduled workflow using this same 'NN past' phrasing is covered without
    anyone having to remember to edit this gate.
    """
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    texts = {}
    for fn in sorted(os.listdir(wf_dir)):
        if fn.endswith((".yml", ".yaml")):
            texts[fn] = io.open(os.path.join(wf_dir, fn), encoding="utf-8").read()
    problems = check_schedule_past_comments(texts)
    if problems:
        fail("schedule-comment-minute", "; ".join(problems))


def gate_scheduled_workflow_cadence() -> None:
    """Warn when a scheduled GitHub Actions workflow is not firing on schedule.

    fulfil-orders.yml is commented "every 30 minutes... chosen against the
    promise on thanks.html", and hourly-brief.yml's own report email tells
    Phil a reply "reaches the operator within the hour." Both are wall-clock
    claims nothing had ever checked against the Actions API's own run
    history. Measured 2026-09-09: fulfil-orders.yml's last 49 gaps averaged
    213 minutes against a configured 30, and hourly-brief.yml's averaged
    4 to 5 hours against a configured 60, sustained across 14+ days, not the
    one-off "GitHub-side incident" a same-day log entry had assumed. A
    warning, not a failure: the delay is GitHub's scheduler, not a defect a
    commit here caused, and thanks.html's own copy already hedges ("within a
    few hours... not instant"). But a future shorter promise, or a cron this
    gate does not know to distrust, could silently drift back into a real
    customer-facing lie with nothing else here positioned to catch it.

    Widened 2026-09-09, later the same day: `check_cron_cadence.py` only
    ever understood the "N times an hour, every hour" cron shape, so this
    gate covered 2 of the repository's 5 scheduled workflows and silently
    said nothing about the other three. The parser now handles a fixed
    daily hour, several fixed hours in one cron line, and several fixed
    hours across separate cron lines (refusing to guess at anything with a
    weekday/month/day-of-month restriction instead of getting the arithmetic
    quietly wrong). Measured the same way against all 5: linkedin-drafts.yml
    and roadmap-report.yml both run almost exactly on schedule (ratio 1.00
    and 0.98); status-email.yml runs a real 1.57x slower than its four-hour
    cycle, real drift but under this gate's 2.5x "degraded" line. So the
    sustained slowdown found above is specific to the two higher-frequency
    workflows, not a blanket fact about every scheduled job on this account.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import check_cron_cadence
        result = check_cron_cadence.check()
    except Exception as e:                                    # noqa: BLE001
        warn("cron-cadence", f"the schedule-cadence check could not run: "
                             f"{type(e).__name__}: {e}. Not the same as "
                             f"every scheduled workflow firing on time.")
        return
    for r in result["workflows"]:
        if r["verdict"] == "unknown":
            warn("cron-cadence",
                 f"{r['workflow']}: {r['reason']}, so its real firing "
                 f"cadence was NOT measured this run. Unchecked, not on time.")
        elif r.get("degraded"):
            warn("cron-cadence",
                 f"{r['workflow']} is configured for a "
                 f"{r['configured_interval_min']:.0f}-minute cycle but its "
                 f"last {r['sample_size']} real gaps averaged "
                 f"{r['mean_gap_min']:.0f} minutes (worst "
                 f"{r['worst_gap_min']:.0f}), {r['mean_over_configured']}x "
                 f"the configured interval.")


def gate_image_coverage() -> None:
    """Three counts about zone imagery must agree, and say so out loud.

    Last cycle produced two defects that no gate, linter or code review could
    see, and both were found only by printing two numbers next to each other
    and noticing they disagreed:

      110 zone pages carried a photograph.
      114 zone pages advertised their own photograph as the social preview.

    Four pages were therefore telling every social and answer engine preview
    about a picture that had been deliberately kept off the page, because a
    membership test was run against a helper that returns every judged stem
    mapped to its verdict rather than a set of approved ones.

    So the comparison becomes a gate. Pages with a hero, pages advertising a
    hero, and approved images should be the same number, and every advertised
    file must exist. It reports the three counts whether it passes or fails,
    because the whole lesson was that the numbers are only useful side by side.
    """
    zones = sorted(glob.glob(os.path.join(SITE, "zones", "*.html")))
    if not zones:
        return

    with_hero, advertising, missing, wired_stems = 0, 0, [], []
    for f in zones:
        page = io.open(f, encoding="utf-8").read()
        if 'id="zone-hero"' in page:
            with_hero += 1
        m = re.search(r'og:image" content="([^"]+/assets/zones/'
                      r'([^"/]+)-lg\.[a-z]+)"', page)
        if m:
            advertising += 1
            wired_stems.append(m.group(2))
            local = os.path.join(SITE, "assets",
                                 m.group(1).split("/assets/")[-1])
            if not os.path.exists(local):
                missing.append(os.path.basename(local))

    if missing:
        fail("image-coverage",
             f"{len(missing)} zone page(s) advertise a preview image that is "
             f"not on disk: {missing[:3]}")
        return

    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import wire_zone_heroes
    except Exception:                                         # noqa: BLE001
        return

    # A fourth count, same shape as the three above: web derivative files
    # for a zone whose verdict is not "ok". Found 2026-09-08: three zones
    # withdrawn 2026-09-04 (a lab analyser standing in for a printer, an
    # empty room, a malformed cot) had their <figure> pulled from the page
    # but left 27 image files in site/assets/zones/, shipped in the Docker
    # image, referenced by no page. wire_zone_heroes.orphan_derivatives()
    # now removes these on --apply; this gate keeps the class from coming
    # back silently.
    orphans = wire_zone_heroes.orphan_derivatives()
    if orphans:
        fail("image-coverage",
             f"{len(orphans)} zone image derivative file(s) on disk for a "
             f"verdict that is not \"ok\": {[os.path.basename(f) for f in orphans[:3]]}. "
             f"Run python ops/wire_zone_heroes.py --apply.")
        return

    # build/heroes/zones/ is gitignored on purpose: it holds generated
    # pictures nobody but Phil's own machine can produce, and a session here
    # never has them. When they are absent there is nothing to re-hash, so
    # falling through to "0 approved" would fail every fresh checkout
    # forever on a defect that does not exist. Verify what a checkout CAN
    # see instead: every wired stem must be recorded "ok" in the committed
    # verdicts file, which is the actual approval record and does not
    # depend on build/.
    have_sources = bool(glob.glob(os.path.join(wire_zone_heroes.HEROES,
                                                "*.png")))
    if have_sources:
        approved = sum(1 for v in wire_zone_heroes.approved().values()
                       if v == "ok")
        if not (with_hero == advertising == approved):
            fail("image-coverage",
                 f"these should be equal and are not: {with_hero} page(s) "
                 f"carry a photograph, {advertising} advertise one as their "
                 f"preview, {approved} images are approved. A page "
                 f"advertising a picture it does not show is publishing one "
                 f"that was withheld.")
        return

    verdicts = {}
    if os.path.exists(wire_zone_heroes.VERDICTS):
        verdicts = json.load(io.open(wire_zone_heroes.VERDICTS,
                                     encoding="utf-8"))
    unreviewed = [s for s in wired_stems
                  if not isinstance(verdicts.get(s), dict)
                  or verdicts[s].get("verdict") != "ok"]
    if unreviewed:
        fail("image-coverage",
             f"{len(unreviewed)} wired zone image(s) are not recorded as "
             f"reviewed and approved in "
             f"{os.path.basename(wire_zone_heroes.VERDICTS)}: "
             f"{unreviewed[:3]}. A page showing a picture nobody approved "
             f"is the exact defect this gate exists to catch.")
        return
    if with_hero != advertising:
        fail("image-coverage",
             f"{with_hero} page(s) carry a photograph but {advertising} "
             f"advertise one as their preview; those should match.")
        return
    warn("image-coverage",
         f"{len(wired_stems)} wired image(s) all verified against recorded "
         f"verdicts by name. Source pictures in build/heroes/ are not "
         f"present in this environment (gitignored, generated on Phil's "
         f"machine only), so sha freshness against the source could not be "
         f"re-checked here.")


def gate_unique_names() -> None:
    """No two buyable products may share a name.

    Six SKUs across three names were indistinguishable in the shop: two
    "Dresser Drawers Pack", two "Shower or Tub Pack", two "Toilet Area Pack".
    The room appeared only in the blurb, so a buyer scanning a grid of 109
    tiles could pick the wrong one, pay for it, and be entirely right to ask
    for a refund. Selling two different things under one name is a trust
    problem before it is a merchandising one.
    """
    js = os.path.join(SITE, "assets", "js", "data.js")
    if not os.path.exists(js):
        return
    src = io.open(js, encoding="utf-8").read()
    try:
        cat = json.loads(src[src.index("["):src.rindex("]") + 1])
    except Exception:                                         # noqa: BLE001
        return
    seen = {}
    clash = []
    for c in cat:
        # Only things somebody can actually buy. Two free downloads sharing a
        # name is untidy; two paid products sharing one is a refund.
        if not c.get("price"):
            continue
        n = c.get("name", "")
        if n in seen:
            clash.append(f"{n!r} is {seen[n]} and {c.get('sku')}")
        seen[n] = c.get("sku")
    if clash:
        fail("unique-names",
             f"{len(clash)} product name(s) are shared by two different SKUs, "
             f"checked across {len(seen)} priced items: {clash[:3]}")


_NUM_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
_NUM_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}


def _spelled_number(phrase):
    """Parse a plain-English cardinal ("forty six", "eighty-eight",
    "ninety") up to ninety nine. Returns None for anything else, including
    "one hundred..." forms, which this deliberately does not attempt.
    """
    words = [w for w in phrase.lower().replace("-", " ").split() if w]
    if len(words) == 1:
        if words[0] in _NUM_ONES:
            return _NUM_ONES[words[0]]
        return _NUM_TENS.get(words[0])
    if len(words) == 2 and words[0] in _NUM_TENS and words[1] in _NUM_ONES:
        return _NUM_TENS[words[0]] + _NUM_ONES[words[1]]
    return None


def check_deck_count(written, with_room_card, catalogue_text, pages):
    """Pure logic for gate_deck_count, testable without real files.

    written: the true corpus total (includes the one Room divider card,
    when with_room_card is True). sold: written minus that divider, which
    is what a buyer actually gets to use as a zone card, per the rule
    ops/build_deck_gallery.py's own DECKS table states and explains.

    catalogue_text: the DECK-ENTRY variant+blurb string from data.js.
    pages: {filename: full text} for every other page that may name a
    count. A page may honestly state either real number; it may also
    honestly state a THIRD number only when the same sentence also
    names one of the two real ones (an "X of Y drawn" style contrast).
    Anything else is a page disagreeing with the product about its own
    size.

    Returns a list of problem strings, empty when clean.
    """
    sold = written - 1 if with_room_card else written
    problems = []

    claimed = re.findall(r"(\d+)\s+cards", catalogue_text)
    wrong = [c for c in claimed if int(c) != sold]
    if wrong:
        problems.append(
            f"the catalogue advertises the Entryway deck as {wrong[0]} cards "
            f"and a buyer actually gets {sold} ({written} written, minus "
            f"the Room divider card). Checked the DECK-ENTRY entry.")

    for name, page in pages.items():
        for m in re.finditer(r"[^.<>]*?(\d+)\s+cards[^.<>]*", page):
            c, sentence = int(m.group(1)), m.group(0)
            if not (40 <= c <= 120) or c in (sold, written):
                continue
            # Built without a backslash literal: writing this patch
            # through a heredoc turned the word boundaries into actual
            # backspace bytes, 0x08, and the regex then matched
            # nothing at all while looking entirely correct in a diff.
            if (re.search(chr(92) + "b" + str(sold) + chr(92) + "b", sentence)
                    or re.search(chr(92) + "b" + str(written) + chr(92) + "b",
                                 sentence)):
                continue          # contrasted against a real total
            problems.append(
                f"{name} says {c} cards, and the deck is {written} written "
                f"/ {sold} sold")

        # A spelled-out count ("Forty six cards") carries no digit for the
        # scan above to see. This is not a hypothetical: the homepage
        # advertised the deck's retired 46-card mockup this exact way for
        # days after every digit-bearing page had already moved to 88/89,
        # because a check built to catch "46 on the homepage" (this
        # function's own docstring names it as the original 2026-08-30
        # defect) only ever looked for digits. A gate that cannot fail on
        # the shape of defect it was named for is theatre.
        for m in re.finditer(
                r"\b((?:[A-Za-z]+\s+){0,1}[A-Za-z]+)\s+cards\b", page):
            n = _spelled_number(m.group(1))
            if n is None or not (40 <= n <= 120) or n in (sold, written):
                continue
            # "eighty four" is also the tail of "six hundred and eighty
            # four", a real total elsewhere on this same homepage (the
            # 684-card Print Pack tile). A fixed lookback window cannot
            # tell the two apart by the captured words alone, so check
            # what precedes the match in the source instead.
            before = page[max(0, m.start(1) - 24):m.start(1)]
            if re.search(r"hundred\s+(and\s+)?$", before, re.I):
                continue
            # An honest retired-number notice ("this WAS 46 cards; it is
            # 88 now") names the real total nearby, just not inside the
            # same period-bounded clause the digit check above uses. A
            # spelled-out count with no real total anywhere near it, like
            # the homepage defect this gate was written for, has nothing
            # to find in this window and is correctly still caught.
            window = page[max(0, m.start() - 300):m.end() + 300]
            if re.search(r"\b(%d|%d)\b" % (sold, written), window):
                continue
            problems.append(
                f"{name} says \"{m.group(1)} cards\" ({n}), and the deck "
                f"is {written} written / {sold} sold")
    return problems


def gate_card_family_known() -> None:
    """Every card type must be a family the card renderer actually knows.

    card_spec.family_of() returns "Room" for any type string it does not
    recognise, and the card band prints the family WORD as well as taking its
    colour and glyph. So an unrecognised type does not render as a blank or a
    crash. It renders as a confident, wrong label.

    On 2026-09-07 that was 65 of the Kitchen deck's 72 cards. The deck is built
    on the chain this business teaches -- Zone, Friction, Root Cause, Action,
    Standard -- and not one of those five words was in the FAMILY map, which
    only knew the older Entryway vocabulary. A ROOT CAUSE card titled EXCESS
    printed the word "Room" across its top, in Room's ink, under Room's house
    glyph, and would have printed that way on paper. Nothing failed. Nothing
    warned. The renderer had a documented fallback and used it.

    That is this repository's most expensive defect class wearing a new hat: a
    default quietly written over a value nobody supplied. The fallback is worth
    keeping so a half-written deck still renders while it is being drafted, but
    it must not be able to reach a shop page in silence. This is the alarm.
    """
    import glob as _glob
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import card_spec as _cs
    except Exception as e:                      # pragma: no cover
        fail("card-family", "cannot import card_spec: %s" % e)
        return

    files = (_glob.glob(os.path.join(ROOT, "ops", "cardtext", "*.json"))
             + _glob.glob(os.path.join(ROOT, "build", "cardtext", "*.json"))
             + _glob.glob(os.path.join(ROOT, "build", "*-cardtext.json")))
    if not files:
        # Unchecked is not passing. If the corpus is not here, say so.
        fail("card-family", "no card corpus found; family labels UNCHECKED")
        return

    seen, bad = 0, {}
    for f in files:
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        cards = d if isinstance(d, list) else (d.get("cards") or [])
        if not isinstance(cards, list):
            continue
        for c in cards:
            if not isinstance(c, dict) or not c.get("type"):
                continue
            seen += 1
            t = c["type"]
            norm = t.upper().replace(" CARD", "").strip()
            if _cs.family_of(t) == "Room" and norm != "ROOM":
                bad.setdefault(t, 0)
                bad[t] += 1

    if not seen:
        fail("card-family", "card corpus present but held no typed cards; "
                            "family labels UNCHECKED")
        return
    if bad:
        fail("card-family",
             "%d of %d cards would print the wrong family word: %s"
             % (sum(bad.values()), seen,
                "; ".join("%s x%d" % (k, v) for k, v in sorted(bad.items()))))


def gate_deck_count() -> None:
    """The advertised card count must equal the number of cards that exist.

    The free Entryway deck was advertised on four surfaces with three
    different numbers: 46 on deck.html and the homepage, 88 on the gallery, and
    90 in the catalogue and therefore on every shop tile, before 2026-08-30.
    ops/build_deck_gallery.py's own DECKS table now names a real, deliberate
    rule instead: the deck is 89 written cards, one of them (ER-001) the Room
    divider, and 88 is that same deck with the divider left out, because you
    buy a room's worth of zone cards, not the divider. Both numbers are true;
    a page is only wrong if it states some THIRD number, or one of the two
    without acknowledging the other where they sit side by side.

    Counted off build/entryway-cardtext.json, the committed corpus (its own
    freshness against ops/cardtext/batch-*.json is gate_cardtext_corpus_
    integrity's job, not this one), not off locally rendered card-front
    PNGs. The old version counted build/cards-rendered/*-front.png, which is
    empty in every cloud run because the art needs a Desktop-only render
    step this sandbox does not have, so the entire check silently returned
    before ever comparing a single page: a gate that cannot fail is theatre.
    The corpus JSON is committed and real in every environment, so this now
    actually runs in CI, not only on a machine that has rendered art.

    Also checks ops/build_deck_gallery.py's own DECKS['entryway']['written']
    against the real corpus, so a hardcoded count can never quietly drift
    from what ops/cardtext/batch-*.json actually contains.
    """
    cardtext = os.path.join(ROOT, "build", "entryway-cardtext.json")
    if not os.path.exists(cardtext):
        return
    try:
        corpus = json.load(io.open(cardtext, encoding="utf-8"))
    except Exception:                                         # noqa: BLE001
        return
    written = corpus.get("count")
    if not written or written != len(corpus.get("cards") or []):
        return          # gate_cardtext_corpus_integrity owns this drift

    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    try:
        BDG = importlib.import_module("build_deck_gallery")
        importlib.reload(BDG)
        spec = BDG.DECKS.get("entryway")
    except Exception:                                         # noqa: BLE001
        return
    if not spec:
        return
    if spec.get("written") != written:
        fail("deck-count",
             f"ops/build_deck_gallery.py's DECKS['entryway']['written'] says "
             f"{spec.get('written')}, and the committed corpus "
             f"(build/entryway-cardtext.json) actually has {written} cards. "
             f"Update DECKS to match the real corpus.")
        return
    with_room_card = bool(spec.get("with_room_card"))

    js = os.path.join(SITE, "assets", "js", "data.js")
    if not os.path.exists(js):
        return
    src = io.open(js, encoding="utf-8").read()
    try:
        cat = json.loads(src[src.index("["):src.rindex("]") + 1])
    except Exception:                                         # noqa: BLE001
        return
    deck = [c for c in cat if c.get("sku") == "DECK-ENTRY"]
    if not deck:
        return
    catalogue_text = f"{deck[0].get('variant', '')} {deck[0].get('blurb', '')}"

    pages = {}
    for f in (os.path.join(SITE, "deck.html"),
              os.path.join(SITE, "deck-gallery.html"),
              os.path.join(SITE, "index.html"),
              os.path.join(SITE, "deck", "entryway-print-and-play.html")):
        if os.path.exists(f):
            text = io.open(f, encoding="utf-8").read()
            # CSS comments inside <style> are not a claim about the deck; a
            # UI note like "the only way to narrow 72 cards down to the
            # type of thing filtered" would otherwise read as a size claim
            # with no real total in the same sentence to excuse it.
            text = re.sub(r"<style\b[^>]*>.*?</style>", "", text,
                          flags=re.S)
            pages[os.path.basename(f)] = text

    problems = check_deck_count(written, with_room_card, catalogue_text, pages)
    if problems:
        fail("deck-count", "; ".join(problems[:4]))


def check_kitchen_deck_rendered(cards: list, page: str) -> list:
    """Pure logic for gate_kitchen_deck_rendered, testable without real
    files. `cards` is ops/cardtext/build_kitchen_deck.py's own card list;
    `page` is the full text of site/kitchen-deck.html.

    Returns a list of problem strings, empty when clean.
    """
    import html as _html

    corpus_ids = {c["id"] for c in cards}
    page_ids = set(re.findall(r'<article class="kcard" id="([^"]+)"', page))
    missing = sorted(corpus_ids - page_ids)
    extra = sorted(page_ids - corpus_ids)
    problems = []
    if missing:
        problems.append(f"{len(missing)} corpus card(s) missing from the "
                        f"page, e.g. {missing[:3]}")
    if extra:
        problems.append(f"{len(extra)} card id(s) on the page do not exist "
                        f"in the corpus, e.g. {extra[:3]}")

    # One card per type, spot-checked verbatim against the corpus. Escaped
    # the same way html.escape(str(v), quote=True) does in the page builder,
    # so a real edit to the corpus and a stale, un-regenerated page disagree
    # here even when both still contain plausible-looking English.
    by_type = {}
    for c in cards:
        by_type.setdefault(c["type"], c)
    field_by_type = {
        "ROOM CARD": "objective", "ZONE CARD": "objective",
        "ROOT CAUSE CARD": "objective", "STANDARD CARD": "objective",
        "EVENT CARD": "objective", "FRICTION CARD": "objective",
        "ACTION CARD": "goal",
    }
    drifted = []
    for t, field in field_by_type.items():
        c = by_type.get(t)
        if not c:
            continue
        raw = c.get(field)
        if not raw:
            continue
        needle = _html.escape(str(raw), quote=True)
        if needle not in page:
            drifted.append(c["id"])
    if drifted:
        problems.append(f"{len(drifted)} card(s) whose corpus text does not "
                        f"appear verbatim on the page, e.g. {drifted[:3]}. "
                        f"Re-run ops/build_kitchen_deck_page.py.")
    return problems


def gate_kitchen_deck_rendered() -> None:
    """BACKLOG-2026-09-07.md B1: the Kitchen deck's 72 cards, typeset and
    unillustrated, must actually be the ones on site/kitchen-deck.html, not
    just present in the gated cardtext corpus.

    ops/cardtext/build_kitchen_deck.py's own gate() already proves the 72
    cards are internally consistent (no orphan root cause, every friction
    routes somewhere real, every card carries art metadata even though
    nothing here draws it). None of that proves the shipped HTML actually
    carries what the corpus says: a hand edit to the page, or a generator
    edit that stops re-reading the corpus, would not trip that gate at all.

    Checks the shipped page against the real corpus (pure logic in
    check_kitchen_deck_rendered, proved to fail on two planted regressions
    in ops/tests/test_gate_kitchen_deck_rendered.py):
      * every corpus card id is present on the page and vice versa
      * a sample front sentence (Room, one Zone, one Friction, one Action,
        one Root Cause, one Standard, one Event) appears character for
        character, not paraphrased, so drift between the corpus and the
        page cannot ship quietly.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    sys.path.insert(0, os.path.join(ROOT, "ops", "cardtext"))
    try:
        import build_kitchen_deck as KD
        import importlib
        importlib.reload(KD)
        deck = KD.build()
    except Exception as e:                                      # noqa: BLE001
        warn("kitchen-deck-rendered",
             f"could not build the Kitchen cardtext corpus to check "
             f"against: {e}")
        return

    page_path = os.path.join(SITE, "kitchen-deck.html")
    if not os.path.exists(page_path):
        fail("kitchen-deck-rendered",
             "ops/cardtext/build_kitchen_deck.py's corpus exists but "
             "site/kitchen-deck.html does not. Run "
             "ops/build_kitchen_deck_page.py.")
        return
    page = io.open(page_path, encoding="utf-8", errors="replace").read()

    problems = check_kitchen_deck_rendered(deck["cards"], page)
    if problems:
        fail("kitchen-deck-rendered", "; ".join(problems))


def check_kitchen_deck_print_tracked(page: str) -> list:
    """Pure logic for gate_kitchen_deck_print_tracked, testable without real
    files. `page` is the full text of site/kitchen-deck.html.

    Returns a list of problem strings, empty when clean.
    """
    problems = []
    m = re.search(
        r'<button[^>]*onclick="([^"]*window\.print\(\)[^"]*)"[^>]*>'
        r'\s*Print the 72 fronts', page)
    if not m:
        problems.append("no 'Print the 72 fronts' button found on the page")
        return problems
    onclick = m.group(1)
    if "Measure" not in onclick or "track(" not in onclick:
        problems.append(
            "the print button calls window.print() but never calls "
            "window.Measure.track(), so taking the free Kitchen deck is "
            "invisible to analytics")
    elif "free-download" not in onclick:
        problems.append(
            "the print button's Measure.track call does not use the "
            "site's own 'free-download' event name, so it will not be "
            "counted alongside every other free artefact taken")
    return problems


def gate_kitchen_deck_print_tracked() -> None:
    """PLAN-MICROZONES-DECKS-APP.md K6: 'deck_full_download' must be
    emitted and readable in the analytics database. The Kitchen deck has
    no downloadable PDF (B1: HTML + print CSS, not a file under
    /downloads/), so measure.js's own href-based '/downloads/' pattern,
    which already counts the Entryway deck's PDF link, never fires for it.
    Before this gate, the 'Print the 72 fronts' button called only
    window.print() with no tracking at all: every Kitchen deck reader who
    took the free artefact was invisible, the exact gap K6 names.

    Fixed by wiring the button to the site's existing 'free-download'
    event (the same name the Entryway deck's PDF link already fires),
    rather than inventing a new event name nobody else reads.
    'deck_page_view' needs no separate event: Umami's own script already
    records a pageview for every load of /kitchen-deck.html, the same way
    every other page on the site is counted, with no per-page custom event.

    Checks the shipped page (pure logic in
    check_kitchen_deck_print_tracked, proved to fail on a planted
    regression in ops/tests/test_gate_kitchen_deck_print_tracked.py).
    """
    page_path = os.path.join(SITE, "kitchen-deck.html")
    if not os.path.exists(page_path):
        return
    page = io.open(page_path, encoding="utf-8", errors="replace").read()
    problems = check_kitchen_deck_print_tracked(page)
    if problems:
        fail("kitchen-deck-print-tracked", "; ".join(problems))


def gate_front_matter_filled() -> None:
    """A committed copyright page must not carry an answered placeholder.

    ops/build_manual_print.py's COPYRIGHT_PAGE is deliberately a bracketed
    template (a copyright page is legally material, so the source stays
    visibly unfilled until real values exist). ops/fill_front_matter.py
    fills the real answers from ops/front-matter.json back into the three
    committed manual files afterward. Running the print builder here
    without that second step regenerated all three with "[AUTHOR OR RIGHTS
    HOLDER]", "[PUBLISHER ADDRESS]" and the like in place of the real,
    already-answered "Philip Kling" and "Nova Consulting, 4328 North
    Morninggale Place, Boise, ID 83713", silently overwriting real content
    with legal-review placeholders. Caught in the diff before committing,
    reverted, and the fill chained into build_manual_print.py's own main()
    so this cannot regress by forgetting a second command.

    This checks the state actually on disk, not that anyone remembered to
    run the chain: any field with a real answer in ops/front-matter.json
    that still shows up bracketed in one of fill_front_matter.py's own
    TARGETS is exactly this regression, whether it came from this generator
    or by hand.
    """
    import importlib
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    FFM = importlib.import_module("fill_front_matter")
    ready = {k: v for k, v in FFM.expand(FFM.load_answers()).items() if v}
    if not ready:
        return
    found = FFM.scan()
    bad = {name: files for name, files in found.items() if name in ready}
    if bad:
        fail("front-matter-filled",
             f"{len(bad)} field(s) with a real answer in "
             f"ops/front-matter.json are still bracketed on disk: "
             f"{list(bad)[:5]}")


def _last_commit_epoch(path: str) -> int | None:
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return int(out) if out else None


def gate_cover_author_current() -> None:
    """The committed book cover art must not predate the author it should show.

    Found 2026-09-02: ops/build_cover.py's author_name() reads the front
    matter and only draws a byline once the field holds a real name rather
    than a bracketed placeholder (issue #3, closed 2026-08-25). The
    committed build/cover.png and build/cover.jpg were last generated
    2026-08-17, four days before ops/front-matter.json and
    FRONT_MATTER.md's author field were filled in (2026-08-21, "Make the
    book and the manual buyable"). Nobody reran the cover generator after
    that fill, so every store that has seen this cover has seen one with no
    author on it, and nothing caught it: the cover is not part of
    gate_generator_ownership's own regenerate-and-diff chain, on purpose,
    because this generator only ever renders correctly on the one machine
    that has the Windows fonts it names (confirmed here: on this sandbox
    every text element silently fell back to PIL's tiny default font before
    this fix, and the script now refuses to write that output rather than
    ship it).

    So this checks a fact a rendering diff cannot check portably: whether
    the committed image is older than the data it is supposed to contain.
    Not proof the pixels are right on every machine, proof the two have
    never been reconciled since the source data changed. Fixed 2026-09-03:
    build_cover.py now falls back to the Liberation fonts already installed
    in this sandbox (metric-compatible, OFL-licensed) when the named Windows
    faces are missing, so this environment can render and verify the cover
    too, not only Phil's; not folded into gate_generator_ownership's
    regenerate-and-diff chain, since that would require Pillow in CI, which
    ops/requirements.txt deliberately keeps out for reasons stated there.
    """
    cover = os.path.join(ROOT, "build", "cover.png")
    if not os.path.exists(cover):
        return
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    BC = importlib.import_module("build_cover")
    importlib.reload(BC)
    author = BC.author_name()
    if not author:
        return
    cover_ts = _last_commit_epoch("build/cover.png")
    source_ts = max(
        _last_commit_epoch("content/book/6S-Success-Front-Matter/FRONT_MATTER.md") or 0,
        _last_commit_epoch("ops/front-matter.json") or 0)
    if cover_ts is None or source_ts == 0:
        return
    if cover_ts < source_ts:
        # A confirmed defect, not an unmeasurable one (git history proves the
        # ordering), but not a live customer-facing outage either: no KDP
        # submission has happened yet, per STATUS.md, and the fix can only be
        # produced correctly on Phil's own machine (the Windows fonts this
        # generator needs). Blocking every future run on a prep-work item
        # only he can finish would be the same mistake the Stripe/mail/gh
        # checks avoid by warning instead of failing; filed as OWNER-ACTIONS
        # item 12 instead.
        warn("cover-author-current",
             f"build/cover.png was last committed before the front matter's "
             f"author field was, so the shipped cover is confirmed missing "
             f"'{author}''s byline. Run ops/build_cover.py and commit the "
             f"result: as of 2026-09-03 it also renders correctly here, via "
             f"the Liberation fallback fonts, not only on Phil's machine.")


def gate_icons_current() -> None:
    """The PWA/favicon icons must not silently drift from the generator that draws them.

    Found 2026-09-04: ops/build_icons.py draws the four PWA icons and the
    favicon from the site's own brand-mark constants and writes them to
    site/assets/img/, real customer-facing output referenced by both
    manifest.webmanifest and every page's own <head> (apple-touch-icon,
    favicon). It was in nobody's checklist: not gate_generator_ownership's
    regenerate-and-diff chain, and nothing else confirmed the shipped files
    still match what the generator and the pages that reference them expect.

    Not folded into gate_generator_ownership itself, for the same reason
    gate_cover_author_current above is not: that would need Pillow inside
    CI, which ops/requirements.txt deliberately keeps out, because that file
    installs beside STRIPE_SECRET_KEY and SMTP_PASS in fulfil-orders.yml (see
    its own header comment). Checked before writing this, not assumed:
    installed Pillow locally and ran ops/build_icons.py. The four PNGs came
    back pixel-identical to the committed ones (raw RGBA bytes, zero diffs
    across all four), but byte-different on disk, because PNG compression is
    not guaranteed reproducible across Pillow/zlib builds. A byte-diff gate
    here would fail on every environment with a different Pillow than
    whichever machine last committed these, regardless of whether the icon
    actually changed, the same false-alarm shape build_avif.py's own note in
    gate_generator_ownership already paid for once.

    So this checks what a byte-diff cannot check portably: that every file
    ops/build_icons.py's own SIZES list promises actually exists and decodes
    to the size that list, the manifest and the page <head> all claim (via
    the site's own no-Pillow PNG IHDR parse, the same technique
    build_social_pins.py's png_dims() already established and for the same
    reason), and that the generator has not been edited more recently than
    the icons it draws, the same staleness shape gate_cover_author_current
    checks for the book cover. SIZES is read out of build_icons.py's own
    source text rather than imported, since importing that module means
    importing PIL at module scope, which is exactly the crash
    run_gate's own docstring already fixed once for gate_cover_author_current.
    """
    src_path = os.path.join(ROOT, "ops", "build_icons.py")
    if not os.path.exists(src_path):
        return
    src = io.open(src_path, encoding="utf-8").read()
    m = re.search(r"SIZES\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        warn("icons-current", "ops/build_icons.py has no SIZES list to check against.")
        return
    sizes = re.findall(r'\("([^"]+)",\s*(\d+),\s*(True|False)\)', m.group(1))
    if not sizes:
        warn("icons-current", "could not parse ops/build_icons.py's SIZES list.")
        return
    img_dir = os.path.join(ROOT, "site", "assets", "img")
    missing, wrong_size = [], []
    for name, size, _maskable in sizes:
        size = int(size)
        path = os.path.join(img_dir, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        with open(path, "rb") as fh:
            head = fh.read(33)
        if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
            wrong_size.append(f"{name} (not a valid PNG)")
            continue
        w = int.from_bytes(head[16:20], "big")
        h = int.from_bytes(head[20:24], "big")
        if (w, h) != (size, size):
            wrong_size.append(f"{name} is {w}x{h}, expected {size}x{size}")
    favicon = os.path.join(img_dir, "favicon.ico")
    if not os.path.exists(favicon):
        missing.append("favicon.ico")
    if missing or wrong_size:
        fail("icons-current",
             "site/assets/img/ does not match ops/build_icons.py's own SIZES "
             "list. Run: python ops/build_icons.py. Missing: %s. Wrong size: "
             "%s." % (missing or "none", wrong_size or "none"))
        return
    gen_ts = _last_commit_epoch("ops/build_icons.py")
    icon_ts = min((_last_commit_epoch("site/assets/img/%s" % name) or 0)
                  for name, _size, _maskable in sizes)
    if gen_ts and icon_ts and gen_ts > icon_ts:
        warn("icons-current",
             "ops/build_icons.py was committed after the icons it draws, so "
             "the shipped icons may predate a generator change. Run: python "
             "ops/build_icons.py and commit the result if anything changed.")


def gate_hazard_icons_current() -> None:
    """Hazard icons can vanish from every zone page and nothing would notice.

    Found 2026-09-06, cold-reading ops/hazard_icons.py (a safety-domain file,
    P0 under CLAUDE.md's own priority order): ops/build_zone_pages.py imports
    its icon() inside a bare `try / except Exception: return ""` fallback, on
    purpose, so a build never crashes over a missing icon module. The cost of
    that safety net is that a broken hazard_icons.py, a moved content.json,
    or any future edit that makes the import fail would silently blank the
    safety icon on all 114 zone pages' hazard lists, with no error anywhere
    in the build. Nothing checked this: hazard_icons.py carries its own
    internal assertion but has no test file, and no preflight gate had ever
    run it or compared its promise against what the site actually ships.
    gate_icons_current, the only other icon gate, is the brand-mark PWA/
    favicon set and does not touch this file.

    Checks two things, because either alone could still pass while the
    fallback is silently active. First, that ops/hazard_icons.py itself
    still imports and its own coverage assertion holds (this alone would not
    catch a fallback triggered by something specific to build_zone_pages.py's
    import context, such as a sys.path difference). Second, and the real
    gap: that the total number of rendered `class="hz"` icons across every
    live site/zones/*.html file equals the total watch_for entries in
    content.json, computed independently here rather than trusted from
    hazard_icons.py's own count, so a fallback that makes every call return
    "" (module still imports fine, coverage assertion never runs) cannot
    pass silently either.
    """
    code, out = run("hazard_icons.py")
    if code != 0:
        fail("hazard-icons",
             "ops/hazard_icons.py failed its own coverage check: %s" %
             out.strip()[-300:])
        return

    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if not os.path.exists(src_path):
        warn("hazard-icons", "content.json not found, could not cross check.")
        return
    d = json.load(io.open(src_path, encoding="utf-8"))
    expected = sum(len(z.get("watch_for") or [])
                   for r in d["rooms"] for z in r["zones"])

    pages = glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))
    shipped = sum(io.open(f, encoding="utf-8").read().count('class="hz"')
                  for f in pages)

    if shipped != expected:
        fail("hazard-icons",
             "content.json has %d hazard entries but the live zone pages "
             "render %d hazard icons (class=\"hz\"). build_zone_pages.py's "
             "import fallback may have silently blanked them; run python "
             "ops/build_zone_pages.py and check for an import error." %
             (expected, shipped))


def gate_mobile_corpus_current() -> None:
    """The mobile app's card corpus must not silently drift from the web one.

    ops/build_mobile_corpus.py exists precisely because a copied-and-forgotten
    file already cost this project twelve days once (mcp/content.json against
    the manual, named in the generator's own docstring). It has its own
    ``--check`` mode for exactly this, but nothing ran it automatically: a
    change to site/assets/js/quest-data.js (which ops/build_quest.py owns)
    could ship without anyone regenerating mobile/quest-app/assets/quest-
    corpus.json, and the mobile app would keep serving a stale deck with no
    warning, the same "generator not chained to what reads it" shape as
    issue #26. This checks the real committed file against a fresh build,
    not that anyone remembered to run the second command.
    """
    import importlib
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    if not os.path.exists(os.path.join(ROOT, "site", "assets", "js",
                                       "quest-data.js")):
        return
    BMC = importlib.import_module("build_mobile_corpus")
    if not os.path.exists(BMC.OUT):
        warn("mobile-corpus-current",
             "the mobile app's card corpus has never been built. Run: "
             "python ops/build_mobile_corpus.py")
        return
    want = json.dumps(BMC.build(), ensure_ascii=False, indent=1) + "\n"
    have = io.open(BMC.OUT, encoding="utf-8").read()
    if have != want:
        fail("mobile-corpus-current",
             "mobile/quest-app/assets/quest-corpus.json is stale against "
             "site/assets/js/quest-data.js. Run: "
             "python ops/build_mobile_corpus.py")


def gate_mobile_finish_actions_distinct() -> None:
    """A button whose onPress is identical to another button's is not a
    second choice, it is the same choice with different words on it.

    Found 2026-09-02: App.js's "zone finished" screen offered "Draw the
    next card" and "Stop here, this counts" as two buttons, but both called
    the exact same handler (setSession([]); setSkipped({}); setFinished(null))
    with no way to tell them apart at runtime. The file's own header comment
    promises "stop without guilt or continue by choice"; the code never
    implemented the choice, so every tap forced the next card regardless of
    which button was pressed, and there was never a way to actually stop.
    Same shape as the "Not now" button gate_mobile_js_tests's own pickCard.js
    fix addressed one cycle earlier, one screen over: a control whose promise
    and its onPress handler had drifted apart.

    Checked by parsing App.js's own source for the two Pressable blocks by
    their accessibilityLabel and comparing each one's onPress body as text,
    not by rendering anything (no React Native test renderer exists in this
    project). A false negative is possible if a future rewrite changes the
    labels; this is a targeted regression check for the exact defect found,
    not a general "two buttons must differ" rule.
    """
    path = os.path.join(ROOT, "mobile", "quest-app", "App.js")
    if not os.path.exists(path):
        return
    src = io.open(path, encoding="utf-8").read()

    def on_press_after(label: str) -> str | None:
        i = src.find('accessibilityLabel="%s"' % label)
        if i == -1:
            return None
        j = src.find("onPress={", i)
        if j == -1:
            return None
        depth = 0
        k = j + len("onPress={") - 1
        for k in range(j + len("onPress={") - 1, len(src)):
            if src[k] == "{":
                depth += 1
            elif src[k] == "}":
                depth -= 1
                if depth == 0:
                    return src[j:k + 1]
        return None

    draw = on_press_after("Draw the next card")
    stop = on_press_after("Stop here, this counts")
    if draw is None or stop is None:
        warn("mobile-finish-actions",
             "could not find both finish-screen buttons in App.js by their "
             "accessibilityLabel; this gate could not check them.")
        return
    if draw == stop:
        fail("mobile-finish-actions",
             '"Draw the next card" and "Stop here, this counts" call the '
             "identical onPress handler in mobile/quest-app/App.js, so "
             "pressing either one does the same thing and there is no way "
             "to actually stop.")


def gate_mobile_no_bare_jsx_text_expr_break() -> None:
    """A line break between plain JSX text and a `{}` expression drops the
    space instead of collapsing it to one, and a source-only read cannot
    tell the difference from a correctly spaced sentence.

    Found 2026-09-05: App.js's zone-finish screen wrote
        {zonesHeld} of {CORPUS.zoneCount} zones in the house
        {zonesHeld === 1 ? "is" : "are"} holding.
    across two lines. Babel's JSX child-trimming drops a line that is only
    indentation between a text node and the next expression container
    rather than turning it into a space (it only collapses a break when
    both sides are plain text), so the compiled children array read
    [..., "zones in the house", "is", " holding."] with no separator
    between the first two: the screen shown after every single completed
    zone read "zones in the houseis holding." Confirmed by transpiling the
    exact source with @babel/preset-react and reading the literal children
    array, not by re-deriving the whitespace rule from memory.

    Checked with a source-level heuristic, not a real JSX parse (no
    @babel/core dependency in this project): flags a line inside
    mobile/quest-app/*.js (excluding node_modules and *.test.js) that ends
    in an ordinary text/punctuation character immediately followed by a
    line whose first non-whitespace content is `{`, unless that next line
    starts with the explicit `{" "}` spacer. This is deliberately narrow
    (it will not catch every whitespace-collapse mistake JSX can make) but
    it is the exact shape this defect took, and a bare regex is enough to
    catch a recurrence without adding a JS parser dependency this project
    has otherwise avoided.
    """
    mobile_dir = os.path.join(ROOT, "mobile", "quest-app")
    if not os.path.isdir(mobile_dir):
        return
    text_char = re.compile(r'[A-Za-z0-9.,!?:;)\"\']$')
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(mobile_dir):
        dirnames[:] = [d for d in dirnames if d != "node_modules"]
        for fn in filenames:
            if not fn.endswith(".js") or fn.endswith(".test.js"):
                continue
            path = os.path.join(dirpath, fn)
            lines = io.open(path, encoding="utf-8").readlines()
            for i in range(len(lines) - 1):
                a = lines[i].rstrip()
                b = lines[i + 1].strip()
                if not a or not b:
                    continue
                if not text_char.search(a):
                    continue
                if not b.startswith("{"):
                    continue
                if b.startswith('{" "}') or b.startswith("{/*"):
                    continue
                rel = os.path.relpath(path, ROOT)
                hits.append(f"{rel}:{i + 1}: {a.strip()!r} then {b!r}")
    if hits:
        fail("mobile-jsx-text-expr-break",
             f"{len(hits)} line break(s) in mobile/quest-app JSX sit "
             "between plain text and a `{}` expression with nothing "
             "explicit between them; Babel drops this space rather than "
             "keeping it, the exact shape of the 2026-09-05 finish-screen "
             "bug. First: " + hits[0])


def gate_mobile_diagnostics_promise_kept() -> None:
    """ON-DEVICE-TEST.md's own Diagnostics section, and App.js's own DIAG_KEY
    comment, promise the local event log records six things: cards drawn,
    done, skipped, zones finished, stops, and import attempts.

    Found 2026-09-05: "cards drawn" was never actually recorded anywhere in
    App.js. `card` recomputes on every done/skipped change regardless of
    which screen sits on top of it (the finished-zone recap, the stopping
    screen), so `card` being non-null is not the same as a card being drawn
    onto the screen, and nothing logged the moment one actually became
    visible. Fixed with lib/pickCard.js's isCardVisible() and a useEffect in
    App.js that calls record("card_drawn", ...) exactly when a card
    transitions to visible.

    Checked with a source-level string search rather than a real JS parse,
    the same trade-off gate_mobile_no_bare_jsx_text_expr_break makes: looks
    for a record("<type>") call for each of the six promised event
    categories inside App.js. A promise this specific belongs in code, not
    only in a paragraph a person has to remember to keep true by hand.
    """
    app_js = os.path.join(ROOT, "mobile", "quest-app", "App.js")
    if not os.path.isfile(app_js):
        return
    src = io.open(app_js, encoding="utf-8").read()
    logged_types = set(re.findall(r'record\(\s*"([a-zA-Z_]+)"', src))
    required = {
        "cards drawn": {"card_drawn"},
        "done": {"card_done"},
        "skipped": {"card_skipped"},
        "zones finished": {"zone_finished"},
        "stops": {"stopped"},
        "import attempts": {"import_ok", "import_failed"},
    }
    missing = [label for label, types in required.items() if not (types & logged_types)]
    if missing:
        fail("mobile-diagnostics-promise",
             "ON-DEVICE-TEST.md's Diagnostics section and App.js's own "
             "DIAG_KEY comment promise the local log records cards drawn, "
             "done, skipped, zones finished, stops and import attempts; "
             f"App.js never calls record() for: {', '.join(missing)}.")


def gate_mobile_js_tests() -> None:
    """Run the mobile app's own plain-node tests. A test nobody runs is not one.

    mobile/quest-app/lib/importProgress.test.js has existed since 2026-08-31
    and mobile/quest-app/lib/pickCard.test.js since 2026-09-01, both runnable
    with plain node and no device, and neither was ever wired into this gate:
    gate_tests() above only globs ops/tests/test_*.py, so a regression in
    either file would ship silently, the same "a check exists but nothing
    runs it" shape gate_mobile_corpus_current() was already written for one
    file over. pickCard.js exists because App.js's "Not now" button called
    setFinished(null) while finished was already null, a no-op React bails
    out of without a re-render: pressing it changed nothing on screen, ever.
    Runs every mobile/quest-app/lib/*.test.js file found, not just these two
    by name, so a future test file is picked up without touching this gate.
    """
    lib = os.path.join(ROOT, "mobile", "quest-app", "lib")
    files = sorted(glob.glob(os.path.join(lib, "*.test.js")))
    if not files:
        return
    node = shutil.which("node")
    if not node:
        warn("mobile-js-tests",
             "node is not installed here, so %d mobile app test file(s) "
             "could not be run. Unchecked, not passing." % len(files))
        return
    bad = []
    for f in files:
        r = subprocess.run([node, f], cwd=os.path.dirname(f),
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            tail = (r.stdout + r.stderr).strip().splitlines()
            bad.append(f"{os.path.basename(f)}: "
                       f"{tail[-1][:90] if tail else 'no output'}")
    if bad:
        fail("mobile-js-tests",
             f"{len(bad)} of {len(files)} mobile app test file(s) failed: {bad[:3]}")


def gate_mobile_npm_test_complete() -> None:
    """`npm test` has to run every lib/*.test.js file, not just the first one written.

    Found 2026-09-02: mobile/quest-app/package.json's own "test" script read
    "node lib/importProgress.test.js", written 2026-08-31 when that was the
    only test file. lib/pickCard.test.js was added 2026-09-01 and never added
    to the script, so a contributor running the project's own documented
    entry point, `npm test`, would silently miss any regression in it. Only
    gate_mobile_js_tests() above (which globs the directory directly, not
    package.json) was actually catching that class of bug; this is the same
    "a lesson fixed in one file, never carried to its sibling" shape named
    repeatedly in ops/NIGHTLY-LOG.md this week, one layer up: the sibling
    here is a package.json script rather than another generator.

    Checked by asserting every lib/*.test.js basename appears literally in
    the "test" script string, not by running anything (gate_mobile_js_tests
    already runs the files themselves).
    """
    pkg_path = os.path.join(ROOT, "mobile", "quest-app", "package.json")
    lib = os.path.join(ROOT, "mobile", "quest-app", "lib")
    files = sorted(glob.glob(os.path.join(lib, "*.test.js")))
    if not files or not os.path.exists(pkg_path):
        return
    try:
        pkg = json.loads(io.open(pkg_path, encoding="utf-8").read())
    except Exception as e:
        fail("mobile-npm-test-complete", f"package.json did not parse: {e}")
        return
    script = (pkg.get("scripts") or {}).get("test", "")
    missing = [os.path.basename(f) for f in files
               if os.path.basename(f) not in script]
    if missing:
        fail("mobile-npm-test-complete",
             f"mobile/quest-app/package.json's own \"test\" script does not "
             f"run {missing}, so `npm test` would silently skip it")


def gate_quest_restore_validates_timestamps() -> None:
    """Restoring a Quest backup must never erase progress already on this device.

    Found 2026-09-03, this operator, reading mobile/quest-app's own merge
    comment ("restoring a backup can never lose work done since it was
    taken") and checking it rather than trusting it. Both restore paths
    (site/assets/js/quest.js's restore() and the mobile app's
    lib/importProgress.js) merged an incoming card's timestamp with
    `(a && b) ? Math.min(a, b) : (a || b)` and never checked that either
    side was actually a number. A hand-edited or corrupted backup file
    carrying a string, zero or a negative value for one card still passes
    JSON.parse, and Math.min(a, b) with a non-numeric b returns NaN, which
    JSON.stringify serialises as null and which the app's own `done[cardId]`
    checks read as falsy: a card this browser or phone already had done is
    silently marked undone. Reproduced live against the served quest.html
    with a real headless-browser file-input restore before writing the fix,
    not assumed from reading the code. The mobile side already has this
    proven by lib/importProgress.test.js (gate_mobile_js_tests runs it); the
    web side has no equivalent JS test harness in this repository, so this
    is a static check on the source instead: it fails if restore()'s guard
    ever gets edited away, rather than nothing at all.

    Widened 2026-09-05, this operator. The 2026-09-03 fix's own commit
    message claimed to check "either side" but only ever validated the
    incoming value (b); the value already sitting in state.done (a) was
    still trusted unvalidated, and Math.min(a, b) with a corrupted a is
    exactly as able to produce NaN as a corrupted b, reproduced directly in
    node before writing the second half of the fix. Same widening applied
    to lib/importProgress.js's mergeDone(), proven there by two new cases
    in importProgress.test.js (gate_mobile_js_tests runs it), so this gate
    only needs to cover the web side, which still has no JS harness.
    """
    path = os.path.join(ROOT, "site", "assets", "js", "quest.js")
    if not os.path.exists(path):
        return
    src = io.open(path, encoding="utf-8").read()
    i = src.find("function restore(")
    if i == -1:
        warn("quest-restore-timestamps",
             "could not find restore() in site/assets/js/quest.js; this "
             "gate could not check it.")
        return
    j = src.find("\n  }", i)
    body = src[i:j if j != -1 else i + 1200]
    if not re.search(r"typeof\s+b\s*!==\s*[\"']number[\"']", body) or \
       "isFinite(b)" not in body:
        fail("quest-restore-timestamps",
             "site/assets/js/quest.js's restore() no longer validates that "
             "an incoming backup value is a real number before merging it. "
             "A corrupted or hand-edited backup entry (a string, zero, NaN "
             "or a negative value) would turn into NaN via Math.min, which "
             "JSON.stringify writes as null and the app reads as undone: "
             "restoring a bad backup would silently erase real progress.")
    if not re.search(r"typeof\s+rawA\s*===\s*[\"']number[\"']", body) or \
       "isFinite(rawA)" not in body:
        fail("quest-restore-timestamps",
             "site/assets/js/quest.js's restore() no longer validates the "
             "value already in state.done before merging it. A corrupted "
             "value already on this device (a hand-edited localStorage "
             "entry, a value some earlier bug wrote) is exactly as able to "
             "turn Math.min(a, b) into NaN as a corrupted incoming value, "
             "even when the incoming value is perfectly good, and would "
             "silently erase a card this browser already had done.")


def gate_quest_symptom_entry() -> None:
    """The symptom entry screen (BACKLOG-2026-09-07.md A5) must stay wired.

    PLAN-MICROZONES-DECKS-APP.md 4.3: a stranger's first screen in the Home
    Quest asks what is annoying them, not which room to pick. That depends
    on two things staying true at once: quest.html (hand-authored) keeps the
    #symptom-step/#cause-step markup quest.js drives, and quest-data.js
    (ops/build_quest.py owns it) keeps shipping real symptom entries. Either
    one silently regressing would leave a stranger back on the old screen,
    or a broken one, with nothing here to say so.

    ops/build_quest.py's own build already asserts the symptom count and
    every field at generation time (proven to fail on a planted bad branch
    index during authoring, an IndexError, not a silent short list); this
    gate is the second, independent check, against the files actually
    shipped, the same belt-and-braces relationship gate_deck_count has to
    its own generator's asserts.
    """
    html_path = os.path.join(ROOT, "site", "quest.html")
    data_path = os.path.join(ROOT, "site", "assets", "js", "quest-data.js")
    if not os.path.exists(html_path) or not os.path.exists(data_path):
        return
    html = io.open(html_path, encoding="utf-8").read()
    for marker in ('id="symptom-step"', 'id="cause-step"', 'id="sym-list"',
                   'id="cause-start"'):
        if marker not in html:
            fail("quest-symptom-entry",
                 "site/quest.html no longer carries %s, so the symptom entry "
                 "screen quest.js drives has nothing to render into. A "
                 "first-time visitor would fall back to the old single "
                 "button screen (or, if that markup is gone too, nothing at "
                 "all)." % marker)
            return
    src = io.open(data_path, encoding="utf-8").read()
    try:
        data = json.loads(src[src.index("{"):src.rindex(";")])
    except (ValueError, IndexError):
        fail("quest-symptom-entry",
             "site/assets/js/quest-data.js could not be parsed as the "
             "generated payload; the symptom entry screen cannot be checked "
             "and should be assumed broken until it is.")
        return
    symptoms = data.get("symptoms") or []
    if not symptoms:
        fail("quest-symptom-entry",
             "site/assets/js/quest-data.js carries no symptoms: the entry "
             "screen would show a question with nothing to answer it. Run "
             "python ops/build_quest.py.")
        return
    for i, s in enumerate(symptoms):
        missing = [k for k in ("symptom", "room", "zone", "why", "sixS",
                                "action", "victory")
                   if not (s.get(k) or "").strip()]
        if missing:
            fail("quest-symptom-entry",
                 "symptom entry %d (zone %r) is missing %s. Run "
                 "python ops/build_quest.py and check content.json's "
                 "diagnosis block for that zone." %
                 (i, s.get("zone"), ", ".join(missing)))
            return


def gate_quest_data_heroes_current() -> None:
    """Every hero image quest-data.js names must still be an approved one.

    Found 2026-09-11 chasing a withdrawn zone hero: the same afternoon
    kitchen--primary-prep-counter's "ok" verdict was withdrawn (it showed a
    counter covered in bowls and flowers, contradicting the zone's own
    done_looks_like), site/zones/ was regenerated to drop it, but
    site/assets/js/quest-data.js was not, because it is a separate generator
    (ops/build_quest.py) that nothing chains after a hero-verdicts.json
    change. The committed file kept shipping that exact withdrawn image on
    the Home Quest's own symptom-entry screen, the second most visited page
    on the site, for the same reason the zone page was wrong in the first
    place. `gate_generator_ownership` (--own) would eventually catch this by
    regenerating the whole chain, but that flag is opt-in and slow; this is
    the fast, always-on version scoped to the one file most likely to drift
    silently after a hero review, so it runs in the default `preflight.py`
    this repository's own step 2 treats as the single gate.

    Reads quest-data.js as shipped and compares every "img" value in it,
    rooms and symptoms alike, against ops/build_quest.py's own
    approved_and_published() intersected with heroes()'s on-disk check, the
    same ground truth that function uses when it writes the file. A stem
    the file names that is not in that set means the payload is stale, not
    that the picture is missing (a missing file is a different, existing
    gate's concern).

    The comparison itself lives in quest_data_stale_heroes(), pure, so a
    test can prove it against a synthetic payload and a fake allowed set
    without a real quest-data.js or a real build/heroes/ directory.
    """
    data_path = os.path.join(ROOT, "site", "assets", "js", "quest-data.js")
    if not os.path.exists(data_path):
        return
    src = io.open(data_path, encoding="utf-8").read()
    try:
        data = json.loads(src[src.index("{"):src.rindex(";")])
    except (ValueError, IndexError):
        return  # gate_quest_symptom_entry already fails this shape by name.

    import importlib
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    BQ = importlib.import_module("build_quest")
    allowed = BQ.heroes()

    stale = quest_data_stale_heroes(data, allowed)
    if stale:
        first = sorted(stale)[0]
        fail("quest-data-heroes-current",
             "site/assets/js/quest-data.js names %d hero stem(s) no longer "
             "approved and published, e.g. %r (shown for %s). A verdict was "
             "likely withdrawn after this file was last built. Run: python "
             "ops/build_quest.py." % (len(stale), first, ", ".join(stale[first])))


def quest_data_stale_heroes(data: dict, allowed: set) -> dict:
    """Every "img" stem in `data` (a parsed quest-data.js payload) that is
    not in `allowed`, mapped to where each one is shown. Pure: no file I/O,
    so gate_quest_data_heroes_current's own test can drive it directly."""
    shipped = {}
    for r in data.get("rooms") or []:
        for z in r.get("zones") or []:
            if z.get("img"):
                shipped.setdefault(z["img"], []).append(f"zone {z.get('zone')}")
    for s in data.get("symptoms") or []:
        if s.get("img"):
            shipped.setdefault(s["img"], []).append(
                f"symptom {s.get('symptom')!r}")
    return {stem: where for stem, where in shipped.items() if stem not in allowed}


def gate_quest_funnel_events() -> None:
    """BACKLOG-2026-09-07.md A5's funnel events must stay wired.

    A5's own reason: "we cannot tell whether people bounce at the ask or at
    the work" and nothing measured whether anybody ever comes back at all.
    quest-symptom-picked answers the ask; quest-cause-shown, added
    2026-09-09, marks the moment the cause step is actually shown rather
    than merely picked; quest-card-abandoned (added the same cycle) answers
    the work, firing only while a card's timer is genuinely running and the
    tab is hidden or closed, never on a normal Done; quest-return answers
    whether the browser has been here before. All three are simple
    string-presence checks against the shipped file rather than a browser
    test, the same tier as gate_quest_symptom_entry just above: cheap,
    and enough to catch a hand edit that silently drops one of them.
    """
    path = os.path.join(SITE, "assets", "js", "quest.js")
    if not os.path.exists(path):
        return
    src = io.open(path, encoding="utf-8").read()
    checks = [
        ('"quest-cause-shown"',
         "no longer fires quest-cause-shown when the cause step is shown, "
         "so a stranger who picks a symptom can no longer be told apart "
         "from one who saw the resulting cause screen"),
        ('"quest-card-abandoned"',
         "no longer fires quest-card-abandoned, so a card left mid-work "
         "can no longer be told apart from one nobody opened"),
        ('"quest-return"',
         "no longer fires quest-return, so a returning visitor can no "
         "longer be told apart from a first-time one"),
        ("visibilitychange",
         "no longer listens for visibilitychange, so quest-card-abandoned "
         "has nothing left to trigger it when a tab is hidden mid-card"),
        ("pagehide",
         "no longer listens for pagehide, so quest-card-abandoned would "
         "miss a card left mid-work by closing the tab or navigating away "
         "rather than switching tabs"),
    ]
    for marker, msg in checks:
        if marker not in src:
            fail("quest-funnel-events",
                 "site/assets/js/quest.js %s." % msg)
            return


def gate_quest_session_placement() -> None:
    """A2: the whole-zone session length must not be the first number a
    first-time visitor reads.

    PLAN-MICROZONES-DECKS-APP.md 4.4 A2: "'45 to 75 minutes' is the first
    number a first-timer reads" on card one, before they have done anything,
    making a single two-minute pass look like an afternoon. Fixed 2026-09-09
    by withholding #c-session on card one of a first run (run.i === 0 &&
    isFirstRun()), and adding it back to the finish screen instead (#f-session),
    so the number still exists, just not as the very first thing shown. The
    zone page already states it on its own (ops/build_zone_pages.py).

    A static source check, the same tier as gate_quest_funnel_events just
    above: cheap, and enough to catch a hand edit that silently drops either
    half of the fix (the withholding, or the finish-screen replacement).
    """
    js_path = os.path.join(SITE, "assets", "js", "quest.js")
    html_path = os.path.join(SITE, "quest.html")
    if not os.path.exists(js_path) or not os.path.exists(html_path):
        return
    js = io.open(js_path, encoding="utf-8").read()
    html = io.open(html_path, encoding="utf-8").read()

    if "withholdSession" not in js:
        fail("quest-session-placement",
             "site/assets/js/quest.js no longer withholds the whole-zone "
             "session length on card one of a first run, so \"45 to 75 "
             "minutes\" is once again the first number a first-timer reads.")
        return
    if "f-session" not in html:
        fail("quest-session-placement",
             "site/quest.html no longer carries #f-session, so the finish "
             "screen has nowhere to state the whole-zone session length that "
             "card one now withholds.")
        return
    if '$("#f-session")' not in js:
        fail("quest-session-placement",
             "site/assets/js/quest.js no longer populates #f-session, so the "
             "finish screen silently never states the whole-zone session "
             "length withheld from card one.")


def gate_quest_card_victory_honesty() -> None:
    """PLAN-MICROZONES-DECKS-APP.md M7/A1: a card must not claim a stop
    condition it cannot reach.

    Phil's own commit fa491b1a (2026-09-07) found the real defect: 570 of
    684 cards were headed "You can stop when" and then printed
    done_looks_like, the state of the zone AFTER all six passes, on a card
    that covers one sixth of the work. Fixed by relabelling the heading to
    say what the sentence actually is ("The whole zone is done when") and
    adding a second line placing the reader against it ("This card is pass
    N of 6, so you are not aiming for all of it right now"). That closes the
    honesty defect (nothing on the card claims an unreachable state any
    more); it does not deliver M7's full acceptance criteria, a genuinely
    distinct per-pass victory line for each of the 570 cards, which stays
    real, unstarted product work, correctly held behind the traffic
    constraint per GOALS.md rule 1 rather than started speculatively.

    This gate only re-asserts the honesty fix itself, the same tier as
    gate_quest_session_placement just above: cheap, and enough to catch a
    hand edit that silently brings the old heading back or drops the
    clarifying note that makes the relabelled heading true.
    """
    js_path = os.path.join(SITE, "assets", "js", "quest.js")
    if not os.path.exists(js_path):
        return
    js = io.open(js_path, encoding="utf-8").read()

    if "You can stop when" in js:
        fail("quest-card-victory-honesty",
             "site/assets/js/quest.js once again writes the heading \"You "
             "can stop when\" over the whole-zone done_looks_like text, "
             "which 570 of 684 cards cannot reach on their own.")
        return
    if "The whole zone is done when" not in js:
        fail("quest-card-victory-honesty",
             "site/assets/js/quest.js no longer relabels the done_looks_like "
             "heading to \"The whole zone is done when\", so the card no "
             "longer says what its own text actually is.")
        return
    if "you are not aiming for all of it right now" not in js:
        fail("quest-card-victory-honesty",
             "site/assets/js/quest.js no longer tells the reader which pass "
             "of 6 they are on relative to the whole-zone done_looks_like "
             "text, so the relabelled heading is true again but unexplained.")


def gate_on_device_check_count() -> None:
    """A check count quoted elsewhere has to match the script that defines it.

    Found 2026-09-02: OWNER-ACTIONS.md and APP-DEVELOPMENT-PLAN.md both said
    "Run the 12 on-device app checks," but mobile/quest-app/ON-DEVICE-TEST.md
    actually numbered 14 rows at the time (10 primary plus 4 "extra"), and
    still would have been wrong at 14 once a 15th check was added the same
    cycle. Nobody had counted the real rows; the number had just been copied
    forward each time a reference to it was written. The same "a fact quoted
    in prose drifts from the artifact it describes" shape as
    gate_mobile_npm_test_complete() above, one layer up: there the drift was
    a package.json script, here it is two sentences of English.

    Checked by counting the actual numbered rows in ON-DEVICE-TEST.md's own
    tables (lines matching "| N |") and asserting every "N on-device
    check(s)" phrase found elsewhere in the repo names that same number, not
    by trusting either document to describe the other correctly.
    """
    script_path = os.path.join(ROOT, "mobile", "quest-app", "ON-DEVICE-TEST.md")
    if not os.path.exists(script_path):
        return
    rows = re.findall(r"(?m)^\|\s*(\d+)\s*\|", io.open(script_path, encoding="utf-8").read())
    if not rows:
        warn("on-device-check-count",
             "could not find any numbered check rows in ON-DEVICE-TEST.md; "
             "this gate could not verify the count quoted elsewhere.")
        return
    real_count = len(rows)
    referrers = ["OWNER-ACTIONS.md", "APP-DEVELOPMENT-PLAN.md"]
    stale = []
    for name in referrers:
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding="utf-8").read()
        for m in re.finditer(r"(\d+)\s+on-device\s+(?:app\s+)?checks?", text, re.IGNORECASE):
            quoted = int(m.group(1))
            if quoted != real_count:
                stale.append(f"{name} says {quoted}")
    if stale:
        fail("on-device-check-count",
             f"ON-DEVICE-TEST.md defines {real_count} numbered checks, but "
             f"{stale}, disagrees with the file it is describing")


def _wcag_contrast(hex1: str, hex2: str) -> float:
    """WCAG 2.x relative-luminance contrast ratio between two #rrggbb colours."""
    def lin(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def lum(hexcol: str) -> float:
        hexcol = hexcol.lstrip("#")
        r, g, b = (int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    l1, l2 = lum(hex1), lum(hex2)
    l1, l2 = max(l1, l2), min(l1, l2)
    return (l1 + 0.05) / (l2 + 0.05)


def gate_mobile_badge_contrast() -> None:
    """The mobile app's pass badge text must clear WCAG 2.2 AA on its own background.

    Found 2026-09-03: App.js's badge text reused PASS_COLOUR, the same colour
    as the badge border, for the actual word ("sort", "safety", ...) at 12px
    bold. That is well under the WCAG large-text threshold (14pt/~18.7px bold
    or 18pt/24px regular), so the 4.5:1 normal-text floor applies, not the
    3:1 large-text or non-text-UI-component floor. Computed directly against
    the real hex values rather than assumed: four of six were short (sort
    3.35, safety 3.04, standardize 4.01, sustain 3.09). BACKLOG-2026-H2.md
    5B.9 had recorded "weakest 3.04:1 against a 3.0 floor" as passing, which
    was the wrong floor for this text size, and no gate had ever computed it,
    the same "a count stood in for a check" shape CLAUDE.md 5c warns about.
    Fixed by adding BADGE_TEXT_COLOUR, a separate mapping used only for the
    text, lightened along each colour's own hue until it clears 4.5:1 with
    real margin; PASS_COLOUR itself is untouched and still used for the
    border (a non-text UI component, 3:1 floor, already passing) and the
    decorative, accessibility-hidden finish-screen dots.

    This gate parses BADGE_TEXT_COLOUR straight out of App.js and computes
    the real ratio against C.deep, so a future colour change cannot silently
    reintroduce the defect without being read from the same source that
    ships.
    """
    app_js = os.path.join(ROOT, "mobile", "quest-app", "App.js")
    if not os.path.exists(app_js):
        return
    src = io.open(app_js, encoding="utf-8").read()

    m_bg = re.search(r'deep:\s*"(#[0-9A-Fa-f]{6})"', src)
    if not m_bg:
        warn("mobile-badge-contrast",
             "could not find C.deep in App.js; this gate could not verify "
             "badge text contrast.")
        return
    bg = m_bg.group(1)

    m_block = re.search(r"const BADGE_TEXT_COLOUR = \{(.*?)\};", src, re.S)
    if not m_block:
        warn("mobile-badge-contrast",
             "could not find BADGE_TEXT_COLOUR in App.js; this gate could "
             "not verify badge text contrast.")
        return
    entries = re.findall(r'(\w+):\s*"(#[0-9A-Fa-f]{6})"', m_block.group(1))
    if not entries:
        warn("mobile-badge-contrast",
             "BADGE_TEXT_COLOUR in App.js has no readable colour entries; "
             "this gate could not verify badge text contrast.")
        return

    short = []
    for name, hexcol in entries:
        ratio = _wcag_contrast(hexcol, bg)
        if ratio < 4.5:
            short.append(f"{name} {hexcol} is {ratio:.2f}:1 against {bg}")
    if short:
        fail("mobile-badge-contrast",
             f"{len(short)} badge text colour(s) below the WCAG 2.2 AA "
             f"4.5:1 normal-text floor: {'; '.join(short)}")


def gate_card_corpus() -> None:
    """The card text corpus is copy. Hold it to the same rules as a page.

    Two P0 issues sat open on the Entryway deck, both labelled blocked-on-art,
    and both were partly text problems nobody had checked for. The corpus that
    feeds ops/render_cards.py carried "Set in Order" in sixteen six_s_lesson
    lines and shipped the term onto finished cards, while EE-001's title was
    still "AMAZON DELIVERY" even though the file, the card list, the master
    proof and the ALT text had all been renamed to Delivery Day.

    The dashboard reported zero live uses of the rejected term the whole time.
    It was counting, honestly, in the deck's HTML documents, and never looked
    at the JSON the renderer actually reads. A count of the wrong files is
    indistinguishable on a dashboard from a clean result.

    brand_visible is skipped on purpose: it is a note recording a defect in the
    old artwork, not copy that renders onto anything.
    """
    banned = {
        "Set in Order": 'the second S is "Straighten"',
        "Amazon": "a third party trademark",
        "Gridfinity": "a third party name that needs checking before use",
    }
    bad = []
    for f in glob.glob(os.path.join(ROOT, "build", "*cardtext.json")) +             glob.glob(os.path.join(ROOT, "build", "cardtext", "*.json")):
        try:
            data = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            fail("card-corpus", f"{os.path.relpath(f, ROOT)} will not parse, so "
                                f"it cannot be checked. Treated as a failure "
                                f"rather than a pass.")
            return
        # The merged corpus is a dict with a "cards" key; the transcription
        # batches it is built from are bare lists. Both are checked, because
        # fixing only the merged file is the generator ownership trap: the
        # next ops/merge_cardtext.py run rebuilds it from the batches and puts
        # the defect straight back.
        cards = data["cards"] if isinstance(data, dict) else data
        for c in cards:
            copy = json.dumps({k: v for k, v in c.items()
                               if k != "brand_visible"}, ensure_ascii=False)
            for term, why in banned.items():
                if term in copy:
                    bad.append(f"{c.get('id', '?')} uses '{term}' ({why})")
    if bad:
        fail("card-corpus",
             f"{len(bad)} card field(s) carry text that must not ship: "
             f"{bad[:3]}")


CARD_ID = re.compile(r"^(E[A-Z]-\d{3})\b\s*(.*)$")


def _card_ref_codes(v):
    """Yield the card id(s) a next_card/related_path value points at.

    The field shows up in two shapes across the six batches: a bare code
    string ("EM-002"), a "CODE Title" string, or a list of either. All three
    have to be read the same way or a whole shape of reference goes
    unchecked, which is exactly how 47 dead references (mostly a cut
    "Experts" card family, EX-001 through EX-012, that was never built)
    shipped baked into the pixels of 20 already-rendered Entryway card
    backs without anything ever naming them.
    """
    if v is None:
        return
    for item in (v if isinstance(v, list) else [v]):
        if not isinstance(item, str):
            continue
        m = CARD_ID.match(item.strip())
        if m:
            yield m.group(1)


def gate_card_related_links() -> None:
    """next_card and related_path must point at a card that exists.

    ops/merge_cardtext.py already refuses to write the merged corpus when a
    reference is dangling, but that only runs when somebody remembers to run
    it. This re-derives the same check from the real source batches on every
    preflight, and also re-checks the merged file so a hand edit there (the
    generator-ownership trap gate_card_corpus's own docstring names) cannot
    reintroduce a dead reference either.

    next_card renders as printed text on the physical card back
    (ops/build_card_template.py); a dead one sends a reader looking for a
    card that is not in their deck. 46 of the 47 references found this way
    were related_path, which nothing currently renders, but build_card_
    template.py's own docstring notes did_you_know "still in build/entryway-
    cardtext.json for the site and the booklet" after being cut from the
    printed face, so a future field gaining a renderer is not a hypothetical.
    """
    import glob as _glob
    import json as _json

    batches = _glob.glob(os.path.join(ROOT, "ops", "cardtext", "batch-*.json"))
    valid_ids = set()
    for f in batches:
        try:
            data = _json.load(io.open(f, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            fail("card-related-links",
                 f"{os.path.relpath(f, ROOT)} will not parse, so references "
                 f"into it cannot be checked. Treated as a failure.")
            return
        for c in data:
            cid = (c.get("id") or "").strip().upper()
            if cid:
                valid_ids.add(cid)
    if not valid_ids:
        return   # no batches in this checkout; nothing to validate

    bad = []
    for f in batches + _glob.glob(os.path.join(ROOT, "build", "*-cardtext.json")):
        try:
            data = _json.load(io.open(f, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            continue
        cards = data["cards"] if isinstance(data, dict) else data
        if not isinstance(cards, list):
            continue
        for c in cards:
            if not isinstance(c, dict):
                continue
            cid = c.get("id", "?")
            nc = c.get("next_card")
            if isinstance(nc, dict) and nc.get("id"):
                for code in _card_ref_codes(nc["id"]):
                    if code not in valid_ids:
                        bad.append(f"{os.path.basename(f)} {cid} next_card -> {code}")
            for k, v in (c.get("related_path") or {}).items():
                for code in _card_ref_codes(v):
                    if code not in valid_ids:
                        bad.append(f"{os.path.basename(f)} {cid} "
                                   f"related_path.{k} -> {code}")
    if bad:
        fail("card-related-links",
             f"{len(bad)} next_card/related_path reference(s) point at a "
             f"card id that does not exist: {bad[:6]}")


def gate_outbound_copy_canon() -> None:
    """Ready-to-send LinkedIn copy is copy. Hold it to the same banned-term
    rule as the card corpus.

    Found 2026-09-10: ops/linkedin_posts.py's own POST 2 ("Safety is the
    fourth S, not a bolt-on") named the conventional 5S ordering as "Sort,
    Set in Order, Shine, Standardize, Sustain," the retired term for the
    second S, in a file whose own module docstring is titled "Ten LinkedIn
    posts, for Phil to publish" and whose print() output is meant to be
    copied verbatim onto a public feed. gate_card_corpus already catches
    this exact term inside the card corpus; nothing checked the other place
    hand-written public copy lives. ops/dashboard.py's own canon count has
    the identical history (it read only the deck's HTML documents and
    reported zero while the card corpus carried it, per gate_card_corpus's
    own docstring) and does not scan this file either, so a dashboard reading
    clean proves nothing here. Not yet sent (no record in OWNER-ACTIONS.md or
    any state file of a --send run), so this is a source fix, not a public
    correction, but the file remains live and reusable.

    Checks ops/linkedin_posts.py's POSTS and ops/linkedin_drafts.py's CORPUS,
    the two hand-written outbound-copy modules meant to be posted or sent
    with no further editing.
    """
    bad = []
    bad += scan_banned_copy(
        "linkedin_posts.py",
        ((title, body) for title, body in linkedin_posts_entries()))
    bad += scan_banned_copy(
        "linkedin_drafts.py",
        ((title, body) for _audience, title, body in linkedin_drafts_entries()))
    if bad:
        fail("outbound-copy-canon",
             f"{len(bad)} outbound post(s) carry text that must not ship: "
             f"{bad[:3]}")


OUTBOUND_COPY_BANNED_TERMS = {
    "Set in Order": 'the second S is "Straighten"',
    "Amazon": "a third party trademark",
    "Gridfinity": "a third party name that needs checking before use",
}


def scan_banned_copy(source: str, entries) -> list:
    """Pure logic: entries is an iterable of (title, body) pairs. Returns one
    string per (entry, banned term) hit, naming the source file so gate
    output points straight at the file to fix."""
    bad = []
    for title, body in entries:
        for term, why in OUTBOUND_COPY_BANNED_TERMS.items():
            if term in body:
                bad.append(f"{source} '{title}' uses '{term}' ({why})")
    return bad


def _load_ops_module(name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "ops", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def linkedin_posts_entries() -> list:
    return _load_ops_module("linkedin_posts").POSTS


def linkedin_drafts_entries() -> list:
    return _load_ops_module("linkedin_drafts").CORPUS


def gate_deck_art_withheld() -> None:
    """A known defect in card art must not be live on the site.

    Issue #1: EE-001 and EP-005's scanned card sheets carry a real Amazon
    smile-arrow logo baked into the pixels. A 2026-08-30 commit fixed this in
    ops/build_card_template.py, a newer print-rendering pipeline, and the
    GitHub issue was written up as resolved on the strength of that, but that
    pipeline is not what the live gallery serves: site/deck-gallery.html
    renders from site/assets/cards/entryway/index.json, built by
    ops/split_deck_cards.py from a different, untouched set of scanned
    sheets. The trademarked images were still live days after the issue read
    as closed, caught only by opening the served files directly rather than
    trusting the commit message.

    Issue #29, same shape, larger: 14 more sheets still say "Set in Order"
    in the 6S Lesson panel, the retired name for the second S, and a
    fifteenth (EP-004) is not a wording defect but the wrong scene entirely,
    a second Wet Shoes render under a Backpack Explosion label. The corpus
    fix that same day never reached these either, for the identical reason.

    ops/split_deck_cards.py now excludes WITHHOLD (BRAND_EXCLUDE union
    CANON_EXCLUDE) at the source, but that only holds if every regeneration
    goes through it. This checks the output that actually ships, independent
    of how it was produced, so a hand edit, a partial re-run, or a future
    script that writes this same index.json some other way cannot silently
    put any of them back.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "split_deck_cards", os.path.join(ROOT, "ops", "split_deck_cards.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    excluded = mod.WITHHOLD
    for f in glob.glob(os.path.join(ROOT, "site", "assets", "cards", "*",
                                     "index.json")):
        try:
            data = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            continue
        live = {c["code"] for c in data.get("cards", [])} & excluded
        if live:
            fail("deck-art-withheld",
                 f"{os.path.relpath(f, ROOT)} still lists "
                 f"{sorted(live)}, withheld in ops/split_deck_cards.py's "
                 f"own WITHHOLD set for a known defect in the pixels")

    # Delisting is not withholding. nginx serves any file under site/ whether
    # a page links to it or not, so an image absent from the index and present
    # on disk is still one URL away from anybody. Checked by hand once and
    # found clean, which is exactly the kind of check that should not need
    # doing by hand twice.
    on_disk = []
    for code in sorted(excluded):
        on_disk += [os.path.relpath(x, ROOT)
                    for x in glob.glob(os.path.join(ROOT, "site", "**",
                                                    code + "*"), recursive=True)]
    if on_disk:
        fail("deck-art-withheld",
             f"{len(on_disk)} withheld card file(s) would still ship and be "
             f"reachable by direct URL despite not being listed: {on_disk[:3]}")


def gate_accept_image_derivation() -> None:
    """The accept-test checklist must still derive for every card and zone.

    ops/accept_image.py is the mechanical checklist a generated image is
    supposed to be judged against before it ships (PLAN-MEDIA-2026-09-07.md
    section 4): must_show/must_not_show/contradicts, built from the same
    content.json and cardtext fields the card or zone page itself prints.
    Its own docstring says plainly it is not yet wired into anything, not
    even a check that runs unattended, and it was true: nothing in this
    file called it before this gate existed, so a future edit to
    content.json (a zone's done_looks_like text emptied, a card's callouts
    list dropped) could silently make the tool unable to derive a checklist
    for that record, and the first anyone would learn of it is a paid
    --all run failing mid-batch against real Gemini credits, or worse,
    quietly skipping the record instead of failing on it.

    This runs only the derivation half (checklist_for_card /
    checklist_for_zone against the real corpus), the same work
    ops/accept_image.py --check already does standalone: no network, no
    credential, so it can run in every environment including this one.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "accept_image", os.path.join(ROOT, "ops", "accept_image.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    bad = []
    cards = mod._cards()
    zones = mod._zones_by_stem()
    if not cards:
        fail("accept-image-derivation",
             "0 cards found in the entryway cardtext corpus; the accept "
             "test would silently check nothing")
        return
    if not zones:
        fail("accept-image-derivation",
             "0 zones found in content.json; the accept test would "
             "silently check nothing")
        return
    for cid, c in cards.items():
        try:
            mod.checklist_for_card(c)
        except Exception as e:                                # noqa: BLE001
            bad.append(f"card {cid}: {e}")
    for stem, z in zones.items():
        try:
            mod.checklist_for_zone(z)
        except Exception as e:                                # noqa: BLE001
            bad.append(f"zone {stem!r}: {e}")
    if bad:
        fail("accept-image-derivation",
             f"{len(bad)} record(s) can no longer derive an accept "
             f"checklist: {bad[:3]}")


def gate_sitemap_complete() -> None:
    """Every indexable page must actually be in sitemap.xml.

    `ops/build_seo.py` owns sitemap.xml and picks up any new page under
    site/ automatically, but only when someone remembers to run it. Phil's
    2026-08-30 kit.html commit landed with a title, meta description and
    canonical link, everything that marks a page meant for search, and sat
    unlisted in the sitemap because nothing forced a regeneration after it
    was added. A page nobody can find is the same defect whether the cause
    is a broken build or a build nobody reran.
    """
    exclude_dirs = {"assets", "nginx", "downloads"}
    sitemap_fp = os.path.join(SITE, "sitemap.xml")
    if not os.path.exists(sitemap_fp):
        return
    listed = set(re.findall(r"<loc>([^<]+)</loc>",
                             io.open(sitemap_fp, encoding="utf-8").read()))
    missing = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(root, fn)
            src = io.open(fp, encoding="utf-8", errors="replace").read()
            rm = re.search(r'<meta\s+name="robots"[^>]*content="([^"]*)"', src)
            if rm and "noindex" in rm.group(1):
                continue
            cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', src)
            if not cm:
                continue
            if cm.group(1) not in listed:
                missing.append(os.path.relpath(fp, SITE))
    if missing:
        fail("sitemap-complete",
             f"{len(missing)} indexable page(s) missing from sitemap.xml: "
             f"{missing[:5]}. Run python ops/build_seo.py.")


def gate_indexnow_current() -> None:
    """Every page in the sitemap should have been announced to IndexNow.

    Being in the sitemap only helps once a crawler fetches the sitemap. This
    domain had one search-engine visit in thirty days as of 2026-09-03, so
    waiting to be found is not working. IndexNow is the one channel that needs
    no account and pushes rather than waits, and `ops/indexnow.py --new` sends
    only what has not been sent.

    A warning, not a failure: an unannounced page is not broken, and this must
    never block a release. But it must be visible, because the old script kept
    no record at all and nobody could tell a page submitted a month ago from a
    page submitted never.
    """
    sitemap_fp = os.path.join(SITE, "sitemap.xml")
    log_fp = os.path.join(ROOT, "ops", "indexnow-log.json")
    if not os.path.exists(sitemap_fp):
        return
    listed = set(re.findall(r"<loc>([^<]+)</loc>",
                            io.open(sitemap_fp, encoding="utf-8").read()))
    if not os.path.exists(log_fp):
        warn("indexnow-current",
             f"no ops/indexnow-log.json, so none of the {len(listed)} sitemap "
             "URLs can be shown to have been announced. Run "
             "python ops/indexnow.py --new")
        return
    try:
        done = set(json.load(io.open(log_fp, encoding="utf-8")).get("submitted", []))
    except (ValueError, OSError) as e:
        # Unreadable is not zero, and it is not fine either.
        warn("indexnow-current",
             f"ops/indexnow-log.json unreadable ({e}); submission state UNKNOWN.")
        return
    never = sorted(listed - done)
    if never:
        warn("indexnow-current",
             f"{len(never)} sitemap URL(s) never announced to IndexNow, e.g. "
             f"{never[:3]}. Run python ops/indexnow.py --new")


def gate_site_verification_declared() -> None:
    """The ownership-token file must exist and must be readable.

    `ops/build_seo.py` reads it to decide whether to emit the Google, Bing,
    Pinterest and Yandex verification tags. If the file goes missing or turns
    into invalid JSON, the site silently reverts to claiming ownership to
    nobody, which looks exactly the same as never having set it up. That state
    is the reason Google Search Console has no data for this domain.
    """
    fp = os.path.join(ROOT, "ops", "site-verification.json")
    if not os.path.exists(fp):
        fail("site-verification",
             "ops/site-verification.json is missing. ops/build_seo.py needs it "
             "to emit ownership tags; without it the site can never be verified "
             "in Search Console. Restore it.")
        return
    try:
        cfg = json.load(io.open(fp, encoding="utf-8"))
    except ValueError as e:
        fail("site-verification",
             f"ops/site-verification.json is not valid JSON ({e}), so no "
             "verification tag is emitted and any pasted token is silently "
             "ignored.")
        return
    filled = [k for k in ("google_meta", "google_html", "bing", "pinterest",
                          "yandex")
              if isinstance(cfg.get(k), str) and cfg[k].strip()]
    if not filled:
        # Standing state, not a regression: this is Phil's gate, tracked in
        # OWNER-ACTIONS.md. Warn so it stays visible rather than forgotten.
        warn("site-verification",
             "no ownership token set, so the site is verified to no search "
             "engine and Google Search Console has no data for it. One paste "
             "from Phil fixes it: see OWNER-ACTIONS.md.")
        return
    # A token is set. Then the built output must actually carry it, or the
    # generator was never rerun and the paste did nothing.
    home = io.open(os.path.join(SITE, "index.html"), encoding="utf-8",
                   errors="replace").read()
    names = {"google_meta": "google-site-verification", "bing": "msvalidate.01",
             "pinterest": "p:domain_verify", "yandex": "yandex-verification"}
    for k in filled:
        if k == "google_html":
            name = os.path.basename(cfg[k].strip())
            if not os.path.exists(os.path.join(SITE, name)):
                fail("site-verification",
                     f"google_html is set to {name} but site/{name} does not "
                     "exist. Run python ops/build_seo.py.")
            continue
        if f'name="{names[k]}"' not in home:
            fail("site-verification",
                 f"{k} is set in ops/site-verification.json but site/index.html "
                 f"carries no {names[k]} tag. Run python ops/build_seo.py.")


def gate_deck_gallery_identity() -> None:
    """A deck gallery page must not describe itself as a different deck.

    `ops/build_deck_gallery.py` renders every `deck-gallery*.html` page from
    one shared template, keyed on room name. Wiring the new Entryway print
    and play PDF into that template put the Entryway link on the Mudroom
    page too: a visitor 2 of 90 cards into Mudroom was told to go print an
    Entryway deck. Caught only by reading the regenerated diff by eye before
    committing it, the same near miss as the meta description that had
    hardcoded "Entryway" regardless of which deck was building. Both are the
    same class of defect, a shared template leaking one variant's identity
    into another's page, so this checks it directly rather than trusting the
    next hand read to catch it too.
    """
    rooms = {"deck-gallery.html": "Entryway", "deck-gallery-mudroom.html": "Mudroom"}
    all_rooms = set(rooms.values())
    for fn, own in rooms.items():
        fp = os.path.join(SITE, fn)
        if not os.path.exists(fp):
            continue
        src = io.open(fp, encoding="utf-8", errors="replace").read()
        head = src[:src.find("</head>")] if "</head>" in src else src
        title_m = re.search(r"<title>(.*?)</title>", head, re.S)
        desc_m = re.search(r'name="description"\s+content="([^"]*)"', head)
        if title_m and own not in title_m.group(1):
            fail("deck-gallery-identity",
                 f"{fn}: <title> does not name its own deck ({own}): "
                 f"{title_m.group(1)!r}")
        for other in all_rooms - {own}:
            if title_m and other in title_m.group(1):
                fail("deck-gallery-identity",
                     f"{fn} (the {own} deck) names {other} in its own <title>")
            if desc_m and other in desc_m.group(1):
                fail("deck-gallery-identity",
                     f"{fn} (the {own} deck) names {other} in its own meta "
                     f"description")


def gate_deck_pdf_download_current() -> None:
    """The free deck PDF a visitor actually downloads must match the one
    ops/build_deck_pdf.py produced, not a stale copy nobody re-synced.

    ops/build_deck_pdf.py writes build/6S-Entryway-Deck-PrintAndPlay.pdf.
    That is not what deck.html and deck-gallery.html link: 5.8 (backlog)
    copied it once, by hand, into site/downloads/, because nginx serves
    site/ and the generator does not write there itself. Nothing since has
    checked the two stay in sync. A future regeneration of the build/ copy
    (new art, a corrected card, a withheld code removed) would silently
    leave every visitor downloading the old deck from site/downloads/,
    with no gate anywhere to say so; gate_generator_ownership cannot cover
    this file at all, because its own source renders in build/cards-rendered/,
    gitignored and Desktop-only, the same reason build_zone_pages.py is
    excluded from that chain when build/heroes/ is empty.

    This does not regenerate anything, so it runs the same in every
    environment: it only compares two files already in the repository.
    """
    gen_fp = os.path.join(ROOT, "build", "6S-Entryway-Deck-PrintAndPlay.pdf")
    served_fp = os.path.join(SITE, "downloads",
                              "6S-Entryway-Deck-PrintAndPlay.pdf")
    if not os.path.exists(gen_fp) or not os.path.exists(served_fp):
        return
    a = open(gen_fp, "rb").read()
    b = open(served_fp, "rb").read()
    if a != b:
        fail("deck-pdf-download-current",
             f"build/6S-Entryway-Deck-PrintAndPlay.pdf "
             f"({len(a)} bytes) and site/downloads/6S-Entryway-Deck-"
             f"PrintAndPlay.pdf ({len(b)} bytes) differ. Every zone/room "
             f"page and deck.html link the site/downloads copy; re-copy "
             f"it from build/ after any ops/build_deck_pdf.py run.")


def gate_room_images_stable() -> None:
    """ops/import_room_images.py must not be one --apply away from deleting a
    room's already-shipped photographs.

    Found this cycle, verified by actually running the script rather than
    reading its docstring: it derives ops/room-images.json from
    content/book/*/chapter_N_final.html, and every source file that
    determines every one of the 9 committed rooms is unreachable from
    wherever this file's true master (Phil's own machine, or a missing
    mirror) actually lives. A plain `--apply` run in an environment like
    this one, with none of those source images on disk, used to write an
    empty manifest over the real one and would have deleted all 41 already
    live figures across all 9 rooms on the next commit. The script itself
    now refuses to shrink a room (`reconcile()`), keeping whatever is
    already committed when the source has fewer figures than that. This
    gate checks the fix is actually wired in, the same way
    `gate_deck_art_withheld` checks a fix rather than trusting a comment
    that it landed.

    Found broken 2026-09-06, same day, this operator: this gate used to call
    reconcile(figures(), committed) directly. figures() keys by chapter
    number with (room, [(file, alt), ...]) values, not by room name with
    [{"file":..,"alt":..}, ...] the way reconcile() and committed both
    expect, so the shrunk-check below always compared against
    manifest.get(room_name) on a dict keyed by chapter number, which is
    always []. That happened to still read as "preserve everything" (the
    right answer) but for the wrong reason, and could not have failed on a
    genuinely broken reconcile(). Now calls the module's own
    fresh_manifest(), the one place that shape gets built, shared with
    main() so the two can no longer drift apart.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "import_room_images", os.path.join(ROOT, "ops", "import_room_images.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    committed = mod.load_committed()
    if not committed:
        return

    # Every referenced file must still exist, independent of the reconcile
    # logic below: a manifest entry pointing at a missing file is the same
    # defect by a different route (a hand edit, a partial rebuild).
    missing_files = []
    for room, entries in committed.items():
        for e in entries:
            if not os.path.exists(os.path.join(mod.OUT, e["file"])):
                missing_files.append(f"{room}/{e['file']}")
    if missing_files:
        fail("room-images-stable",
             f"{len(missing_files)} committed room image(s) missing from "
             f"disk: {missing_files[:5]}")

    # Prove the generator's own safety net still holds: reconciling the
    # committed manifest against whatever the source yields right now must
    # never produce fewer figures for any room than what is already
    # committed.
    manifest, _ = mod.reconcile(mod.fresh_manifest(mod.figures()), committed)
    shrunk = [room for room, entries in committed.items()
              if len(manifest.get(room, [])) < len(entries)]
    if shrunk:
        fail("room-images-stable",
             f"reconcile() would still ship fewer figures than committed "
             f"for {shrunk}; the safety net in import_room_images.py is "
             f"broken")


def gate_zone_heroes_stable() -> None:
    """A plain rebuild must not silently unpublish approved zone hero photos.

    Found 2026-09-01, the same class of defect gate_room_images_stable and
    gate_image_coverage (6.8) were each already fixed for once, in a third
    spot neither of them covers: `ops/wire_zone_heroes.py`'s own
    `approved()` required the source PNG in the gitignored, Phil-only
    build/heroes/zones/ to re-hash before trusting a verdict. In any
    environment without that folder, every stem failed the hash check with
    nothing to hash, so `approved()` returned empty, `_og_image()` in
    build_zone_pages.py fell back to the generic room-map picture for all
    110 previously approved zones, and the same full rebuild stripped the
    hero figure off every one of those pages, because the wiring loop had
    nothing to iterate either. Reproduced by actually running
    `build_zone_pages.py` in this sandbox, not by reading the code: hero
    count on disk went from 110 to 0 in one run. Fixed with a
    source-optional fallback in `approved()` (trust the committed verdict
    by name when there is nothing to re-hash, mirroring 6.8's own fix) and
    `ops/hero-fallback.json`, a committed record of the exact figure HTML
    for every zone that was approved when this gate was written, restored
    by a new `fallback_wire()` when no source PNGs exist. This gate proves
    that restoration actually holds, the same way gate_room_images_stable
    proves reconcile() holds rather than trusting a comment that it does.
    """
    verdicts_path = os.path.join(ROOT, "ops", "hero-verdicts.json")
    if not os.path.exists(verdicts_path):
        return
    verdicts = json.load(io.open(verdicts_path, encoding="utf-8"))
    approved_ok = {s for s, r in verdicts.items()
                   if isinstance(r, dict) and r.get("verdict") == "ok"}
    if not approved_ok:
        return

    have_sources = bool(glob.glob(os.path.join(
        ROOT, "build", "heroes", "zones", "*.png")))
    if have_sources:
        # Phil's own machine, mid review session: the strict path already
        # re-hashes every stem, and a stale fallback file is not this gate's
        # concern.
        return

    # Checked against the ground truth of hero-verdicts.json, not against
    # og:image alone: that was the actual gap. gate_image_coverage's own
    # no-source fallback (6.8) only checks the wired count and the
    # advertised count agree with EACH OTHER, so a rebuild that strips both
    # together, in lockstep, at the same time, passes it clean, exactly what
    # happened here. This gate checks both against a number neither of them
    # can silently drag down together: how many were actually approved.
    zones = sorted(glob.glob(os.path.join(SITE, "zones", "*.html")))
    with_hero, advertising = 0, 0
    for f in zones:
        page = io.open(f, encoding="utf-8").read()
        if 'id="zone-hero"' in page:
            with_hero += 1
        if re.search(r'og:image" content="[^"]+/assets/zones/'
                     r'[^"/]+-lg\.[a-z]+"', page):
            advertising += 1

    if with_hero < len(approved_ok) or advertising < len(approved_ok):
        fail("zone-heroes-stable",
             f"{len(approved_ok)} zone hero(es) are recorded approved, but "
             f"only {with_hero} page(s) show one and {advertising} "
             f"advertise one, with no source pictures present here to "
             f"explain the drop. A rebuild in an environment without "
             f"build/heroes/zones/ just unpublished approved photographs; "
             f"the fallback in wire_zone_heroes.py did not restore them.")


def _pymupdf_importable() -> bool:
    import importlib
    importlib.invalidate_caches()
    try:
        import pymupdf  # noqa: F401
        return True
    except ImportError:
        return False


def ensure_pymupdf(importable=_pymupdf_importable,
                    install=lambda: subprocess.run(
                        [PY, "-m", "pip", "install", "-q",
                         "--timeout", "60", "-r",
                         os.path.join(ROOT, "ops", "requirements.txt")],
                        cwd=ROOT),
                    attempts: int = 3) -> bool:
    """Install pymupdf, tolerating one slow/cold connection, and prove it.

    A cold sandbox's first HTTPS fetch through this session's tunnel has been
    observed to time out (ReadTimeoutError from files.pythonhosted.org) while
    a second attempt moments later succeeds immediately, the tunnel already
    warm. The old version fired one install and moved on regardless of its
    exit code, so a single slow connection left pymupdf missing for the rest
    of the run: every PDF in `affiliate.check()`'s `delivered_documents()`
    then reads as unreadable and fails closed (by design, correctly), and
    `test_affiliate.py` fails with it, both looking like a real content
    defect until someone reruns preflight cold and watches it pass. Retrying
    a plain network timeout (not a 403/407 policy denial) is the fix, and
    checking the real result with a fresh import each time, rather than
    trusting pip's exit code, is what makes the retry loop trustworthy.

    Returns True once `import pymupdf` actually succeeds in this process,
    False if it still cannot be imported after every attempt.
    """
    if importable():
        return True
    for attempt in range(1, attempts + 1):
        print(f"  bootstrap: installing ops/requirements.txt "
              f"(pymupdf missing, attempt {attempt}/{attempts})")
        install()
        if importable():
            return True
    print(f"  bootstrap: pymupdf still not importable after {attempts} "
          f"attempts. PDF-dependent checks (affiliate, tests) will fail "
          f"closed this run, correctly, but the cause is this install, "
          f"not a site defect.")
    return False


def bootstrap_fresh_sandbox() -> None:
    """Heal the two artifacts every fresh-checkout cycle has hit, on its own.

    This used to run only under `--fix`, which the STEP 2 operator
    instruction ("Run: python ops/preflight.py") never passes, so a bare run
    kept failing on a fresh checkout and every cycle re-diagnosed the same
    two causes by hand instead of running the flag that fixed them.
    `ops/NIGHTLY-LOG.md` shows this exact pair, missing `pymupdf` and an
    unbuilt `build/products/`, repeating across at least seven consecutive
    entries even with the flag already written, because nobody's first
    command passes it. Both fixes are idempotent and side-effect free (a pip
    install of one pinned package, a deterministic rebuild already proven
    byte-stable across reruns), so this now runs unconditionally, every
    invocation, fast or deep, `--fix` or not: there is no case where running
    it is wrong, only cases where it is a fast no-op.
    """
    ensure_pymupdf()
    if not os.path.isdir(os.path.join(ROOT, "build", "products")):
        print("  bootstrap: running ops/build_catalog.py --build (build/products/ missing)")
        subprocess.run([PY, os.path.join(ROOT, "ops", "build_catalog.py"),
                        "--build"], cwd=ROOT, capture_output=True, text=True)


def gate_mobile_overflow(deep: bool) -> None:
    """No page may scroll sideways on a phone. Deep runs only, it drives Edge.

    Four real defects shipped past every gate in this file because nothing here
    ever rendered a page: an unshrinkable button label that pushed 21px off the
    home page, the same floor climbing the grid to throw the whole book hero
    off the right edge, a cover image whose inline max-width outranked the
    stylesheet, and a revenue table with no scroll container that moved the
    entire document. Static checks cannot see any of that. A browser can.

    If there is no browser, this says so. It does not pass. A gate that reports
    "clean" when it could not look is the failure mode that has already cost
    this project several wrong all-clears.
    """
    if not deep:
        return
    tool = os.path.join(ROOT, "ops", "shoot_mobile.py")
    if not os.path.exists(tool):
        warn("mobile-overflow", "ops/shoot_mobile.py is missing, nothing rendered.")
        return
    if not B.find_browser():
        warn("mobile-overflow",
             "no browser on this machine, so no page was rendered. This is "
             "unchecked, not clean.")
        return
    # A zone page and a room page were added 2026-09-04. Those two templates
    # produce 134 of the site's 191 pages, the largest and longest thing on
    # it, and neither had ever been rendered by this gate: the list was the
    # six hand written pages, so the six that get eyeballed anyway were the
    # only six a browser ever measured. One page of each template is enough,
    # because every page of a template shares its markup; the point is that
    # the template is checked at all. Both verified clean at 390px on the day
    # they were added, so this is closing a blind spot rather than admitting
    # a known failure.
    pages = [os.path.join("site", n) for n in
             ("index.html", "book.html", "quest.html",
              "shop.html", "invest.html",
              os.path.join("zones", "garage-the-automotive-care-zone.html"),
              os.path.join("rooms", "kitchen.html"))]
    pages = [p for p in pages if os.path.exists(os.path.join(ROOT, p))]
    try:
        r = subprocess.run([sys.executable, tool] + pages, cwd=ROOT,
                           capture_output=True, text=True, timeout=900,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    except Exception as e:                                    # noqa: BLE001
        warn("mobile-overflow", "could not render: %s. Unchecked." % e)
        return
    out = (r.stdout or "") + (r.stderr or "")
    bad = [l.strip() for l in out.splitlines() if "OVERFLOWING" in l]
    blind = [l.strip() for l in out.splitlines()
             if "CANNOT MEASURE" in l or "WRONG VIEWPORT" in l]
    if blind:
        warn("mobile-overflow",
             "%d page(s) could not be measured at 390px: %s"
             % (len(blind), "; ".join(blind[:2])))
    if bad:
        fail("mobile-overflow",
             "%d page(s) overflow a 390px screen: %s. "
             "Run: python ops/shoot_mobile.py"
             % (len(bad), "; ".join(bad[:3])))
    elif not blind:
        pass


def gate_visual_audit(deep: bool) -> None:
    """All nine categories audit_visual.py computes, on the real rendered DOM.
    Deep only.

    ops/audit_visual.py exists (built 2026-09-01/02 after two real defects
    shipped that no static check could see: cream text inherited into a light
    card, and a hero image stretched by a height without height:auto) but
    nothing ran it automatically, so it caught nothing after the day it was
    written. Running it once for this gate found three more real, live
    defects immediately: site/deck.html and site/invest.html had text as low
    as 1.18:1 against a 4.5:1 floor (badge labels, legend chips, and text
    inheriting a light-panel muted colour inside a dark .deep-2 section that
    only had the override defined for its sibling .deep, the same
    "generator's sibling never got the fix" shape this file's own log has
    named a dozen times), and site/standards.html's generator
    (ops/build_standards_page.py) hardcoded two more instances of the exact
    same colours in its own hero mockup. All fixed at the source (CSS
    variables and the owning generator, not the generated HTML) and verified
    clean here before this gate was written.

    2026-09-02, this operator: the tool's own docstring claimed its no-arg
    default covered "every page", but the code only globbed site/*.html, the
    23 top-level pages, never site/zones/, site/rooms/ or site/articles/, 88
    per cent of the site. That gap is exactly where the next real defect was
    hiding: site/zones/index.html's .zroom, .zsession and .zchip span labels
    read #8C8478 and #6E8B5B on a #FBF7EF card, 3.46:1 and 3.57:1 against the
    4.5:1 floor, 233 failing text nodes on one page, live since the page was
    first generated. Fixed at the source (ops/build_zone_index.py) with
    colours already used elsewhere on the same page's own palette (#584f46,
    7.5:1; #3f6647, 6.14:1), both comfortably over the floor rather than
    barely clearing it. audit_visual.py's default now genuinely globs every
    page (site/**/*.html), matching its own docstring, and re-verified clean
    against the rebuilt page. The subprocess timeout below was raised from
    300s to 900s to give a full-site crawl a real chance to finish rather
    than degrade to "unchecked" on every deep run; a run that still cannot
    finish in that window still reports unchecked rather than a false pass.

    Deep only because it drives a real headless browser once per page; a
    fast run cannot verify anything it checks anyway.

    2026-09-05, this operator, found running audit_visual.py directly rather
    than trusting this gate's own clean history: it prints nine categories
    (contrast, image distortion, broken images, missing image dimensions,
    missing alt text, heading level jumps, unlabelled inputs, missing focus
    styles, and landmark/h1 problems), computed fresh on every run, and this
    gate had only ever parsed the first two. The other seven were silently
    discarded, so a regression in any of them could ship and preflight would
    still say clean. It was not theoretical: "landmark/h1 problems" was
    already 1, on site/downloads/6S Success Home Edition - Sample (Chapters
    1-30).html, the site's primary lead magnet, with h1=31 (a book-cover
    <h1> plus one <h1 class="title"> per chapter, each chapter having been
    authored as its own standalone document before being assembled into one
    combined download). To a screen reader, 31 same-level top headings carry
    no book/chapter hierarchy at all. Fixed at the source, not the shipped
    copy: content/book/.../Sample (Chapters 1-30).html's 30 per-chapter
    <h1 class="title"> demoted to <h2 class="title">, and
    content/book/assets/book.css's two h1.title rules generalised to
    .title (checked first that no other element on the page carries that
    class, so this could not collide with anything), so the same large
    display styling now applies regardless of tag. Regenerated via
    ops/build_sample_html.py --apply, the file's own owning generator, then
    re-fingerprinted; verified with a real headless screenshot that the
    demoted chapter title still renders at full size and weight, not a
    generic h2. audit_visual.py now reports 0 across all nine categories on
    all 193 pages. This gate now reads all nine rather than adding a second,
    narrower gate beside it.

    2026-09-10, this operator: this gate is a hard FAIL, and the tool it
    shells out to had a genuine, reproduced timing flake. Two back to back
    `audit_visual.py --all` runs on the same unchanged tree reported
    different contrast numbers for site/shop.html, some as low as 1.52:1;
    computing WCAG contrast by hand for the exact RGB pairs reported gave
    5.6:1 to 15:1, so the low numbers were not real. Cause: site.css fades
    every `.reveal` element in over a real, wall-clock-timed 0.7s CSS
    transition once JS marks it `.in`; audit_visual.py's own settle timer
    only waits 250ms after images finish loading, a variable amount of real
    time on a loaded machine, so the DOM dump can land mid-fade. Fixed in
    ops/audit_visual.py's audit() by adding `--force-prefers-reduced-motion`,
    which makes the browser apply site.css's own existing
    `@media (prefers-reduced-motion:reduce){.reveal{opacity:1}}` rule, a real
    state a visitor with that OS preference already gets, removing the race
    rather than out-waiting it. `ops/tests/test_audit_visual_reduced_motion.py`
    proves the flag is present and that it actually works on this machine's
    browser; a true fail/pass reproduction of the race itself was attempted
    and abandoned as impractical (a synthetic single-page test could not
    reproduce it: this browser's IntersectionObserver did not fire at all
    under `--dump-dom`, and a synchronous class change before first paint
    never triggers a CSS transition in the first place), recorded honestly
    rather than shipped as a test that would not actually prove the claim.
    """
    if not deep:
        return
    tool = os.path.join(ROOT, "ops", "audit_visual.py")
    if not os.path.exists(tool):
        warn("visual-audit", "ops/audit_visual.py is missing, nothing rendered.")
        return
    if not B.find_browser():
        warn("visual-audit",
             "no browser on this machine, so no page was rendered. This is "
             "unchecked, not clean.")
        return
    try:
        r = subprocess.run([sys.executable, tool, "--all"], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
    except Exception as e:                                    # noqa: BLE001
        warn("visual-audit", "could not render: %s. Unchecked." % e)
        return
    out = (r.stdout or "") + (r.stderr or "")
    # audit_visual.py's own audit() computes nine categories on the real
    # rendered DOM (2026-09-05: found by running the tool directly rather
    # than trusting a clean preflight, per this file's own step 5d). This
    # gate had only ever read two of them (text contrast, image distortion);
    # the other seven, including a genuine live defect (see below), were
    # computed every run and silently discarded, the exact "a check exists
    # but does not gate everything it measures" shape issue #26 already
    # names for generators. Reading all nine closes that gap rather than
    # adding a second, narrower gate next to this one.
    checks = [
        ("text below contrast", "text element(s) below WCAG contrast"),
        ("images distorted", "image(s) distorted"),
        ("images not loading", "image(s) not loading"),
        ("images without w/h", "image(s) missing width/height"),
        ("images without alt", "image(s) missing alt text"),
        ("heading level jumps", "heading level jump(s)"),
        ("inputs without label", "input(s) without a label"),
        ("no visible focus", "control(s) with no visible focus"),
        ("landmark/h1 problems", "page(s) with a missing main landmark or "
                                  "not exactly one h1"),
    ]
    m_unread = re.search(r"pages NOT measured\s*:\s*(\d+)", out)
    counts = {}
    missing = []
    for key, _ in checks:
        m = re.search(re.escape(key) + r"\s*:\s*(\d+)", out)
        if not m:
            missing.append(key)
        else:
            counts[key] = int(m.group(1))
    if missing:
        warn("visual-audit",
             "could not parse audit_visual.py's own output for %s, so "
             "nothing was confirmed either way: %s" % (missing, out[-300:]))
        return
    if m_unread and int(m_unread.group(1)):
        warn("visual-audit",
             "%s page(s) could not be rendered at all, unchecked not clean"
             % m_unread.group(1))
    bad = [(key, label, counts[key]) for key, label in checks if counts[key]]
    if bad:
        lines = [l.strip() for l in out.splitlines()
                 if l.strip().startswith("site/")]
        summary = ", ".join("%d %s" % (n, label) for _, label, n in bad)
        fail("visual-audit",
             "%s on the real rendered pages. Run: python ops/audit_visual.py "
             "--all. First: %s" % (summary, lines[:3]))


def gate_mobile_touch_targets(deep: bool) -> None:
    """Touch targets on a real phone, not a mouse. Deep only, same reason as
    gate_visual_audit: this drives a real headless browser per page.

    audit_visual.py --mobile computes three categories gate_visual_audit
    never reads, because that gate only ever runs the desktop pass:
    "targets under 44px", "targets under 24, crowded" and "pages scrolling
    sideways". A regression in any of them could ship with preflight fully
    green.

    Not theoretical. Found 2026-09-08, this operator, running
    audit_visual.py --all --mobile directly rather than trusting a clean
    gate_visual_audit result (CLAUDE.md 5d: verify a claim before acting on
    it; the claim here was "the deep audit already covers this"). Two real,
    live, previously ungated defects: site/corporate.html's seven
    qualifying-enquiry <input> fields measured 42px tall at a coarse
    pointer, because site.css's touch-target block lists
    input[type="text"] and five siblings but nothing matches an <input>
    with no type attribute at all, which every one of these seven is
    (browsers default an untyped input to text; the CSS attribute selector
    does not). And the free sample eBook's 30 chapter-contents links and
    four "Contents" back-links measured 41-43px, a rule that was simply
    never written for that page's own inline stylesheet. Both fixed at the
    source (site/assets/css/site.css and the book source's own <style>
    block, regenerated through ops/build_sample_html.py, its owning
    generator) and reproduced clean four times in isolation before being
    called fixed, because the first full-batch run also showed 30 contrast
    failures on site/shop.html that four isolated reruns never reproduced
    once, a timing flake in the .reveal fade-in transition versus the
    probe's fixed 250ms settle time, not a real defect: contrast is left
    off this gate's own list for that reason, filed as a known flake rather
    than gated, so a real regression there is not silently waved through
    either (gate_visual_audit's desktop pass already covers contrast on
    the same markup with no animation-timing exposure).
    """
    if not deep:
        return
    tool = os.path.join(ROOT, "ops", "audit_visual.py")
    if not os.path.exists(tool):
        return
    if not B.find_browser():
        warn("mobile-touch-targets",
             "no browser on this machine, so no page was rendered. This is "
             "unchecked, not clean.")
        return
    try:
        r = subprocess.run([sys.executable, tool, "--all", "--mobile"],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=900)
    except Exception as e:                                    # noqa: BLE001
        warn("mobile-touch-targets", "could not render: %s. Unchecked." % e)
        return
    out = (r.stdout or "") + (r.stderr or "")
    checks = [
        ("targets under 44px", "touch target(s) under the 44px minimum"),
        ("targets under 24, crowded",
         "touch target(s) under 24px with a neighbour close enough to "
         "mis-tap"),
        ("pages scrolling sideways", "page(s) that scroll sideways on a "
                                       "phone"),
    ]
    counts = {}
    missing = []
    for key, _ in checks:
        m = re.search(re.escape(key) + r"\s*:\s*(\d+)", out)
        if not m:
            missing.append(key)
        else:
            counts[key] = int(m.group(1))
    if missing:
        warn("mobile-touch-targets",
             "could not parse audit_visual.py --mobile's own output for "
             "%s, so nothing was confirmed either way: %s"
             % (missing, out[-300:]))
        return
    bad = [(key, label, counts[key]) for key, label in checks if counts[key]]
    if bad:
        lines = [l.strip() for l in out.splitlines()
                 if l.strip().startswith("site/")]
        summary = ", ".join("%d %s" % (n, label) for _, label, n in bad)
        fail("mobile-touch-targets",
             "%s on the real rendered pages at 390px. Run: python "
             "ops/audit_visual.py --all --mobile. First: %s"
             % (summary, lines[:3]))


def gate_sitemap_urls() -> None:
    """Every URL we hand to a search engine must actually resolve.

    Three directories answered 403 Forbidden on the live site for months and
    were found by accident, because nothing here had ever asked what a public
    URL returns. The sitemap is the list we promise is real, so it is the right
    list to check. Resolution follows nginx's own try_files order, on disk, so
    this needs no network and no running server.
    """
    tool = os.path.join(ROOT, "ops", "check_urls.py")
    if not os.path.exists(tool):
        warn("sitemap-urls", "ops/check_urls.py is missing, nothing was checked.")
        return
    r = subprocess.run([sys.executable, tool], cwd=ROOT, capture_output=True,
                       text=True, timeout=300,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        out = (r.stdout or "") + (r.stderr or "")
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        fail("sitemap-urls", " | ".join(lines[-3:])[:400]
             + "  Run: python ops/check_urls.py")


def gate_no_css_import() -> None:
    """No stylesheet may @import another one.

    Found 2026-09-05: site.css @import'd fonts.css, so the browser could not
    even start fetching fonts.css until it had downloaded and parsed the
    whole of site.css first, a full extra serial round trip on 183 of 191
    pages before any text could paint. Fixed by inlining fonts.css into
    site.css. Nothing stopped it coming back the same way, or a future
    stylesheet reintroducing the same chain some other way, so this checks
    every shipped .css file directly rather than trusting the one fix.
    """
    hit = []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.css"), recursive=True)):
        body = io.open(f, encoding="utf-8", errors="replace").read()
        # Strip comments first. This file's own explanation of why the last
        # @import was removed says "@import" three times in prose, and a
        # checker that cannot tell a comment from a rule reports fiction,
        # the exact shape audit_pages.py already names for HTML headings.
        code = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        if re.search(r"@import\b", code):
            hit.append(os.path.relpath(f, SITE).replace(os.sep, "/"))
    if hit:
        fail("no-css-import",
             "@import found in: %s. Inline the imported rules instead; an "
             "@import cannot be fetched in parallel with the file that "
             "contains it, so it serialises a request behind another on "
             "every page that loads it." % hit)


def gate_no_stray_dashes() -> None:
    """CLAUDE.md: zero em dashes and en dashes anywhere, including code
    comments. Two gates already exist for pieces of this (fix_dashes.py
    checks root *.md and claude/**/*.md; audit_pages.py checks shipped
    site/**/*.html), and neither ever looks at the source code itself:
    ops/*.py and mobile/**/*.js, the exact surface the rule names by name.

    Checked what a whole-tree version of this scan would find before writing
    it that way: 233 files, almost all of it content/**/*.html and
    content/**/*.md, pre-existing source archives, drafts and review notes
    (card prompt kits, editorial reviews, superprompt files) that were never
    subject to this rule and were never going to ship, not a live defect
    growing unnoticed. Gating those would make this fail permanently on day
    one over historical material, which is what CLAUDE.md itself calls
    theatre from the other direction: a gate nobody can make pass honestly
    gets bypassed instead of fixed. Scoped to the code surface the rule
    actually names, where a violation is cheap to prevent and there is no
    legitimate reason for prose to reach a comment or a string.

    A handful of files in this exact codebase legitimately contain the two
    characters as literal data, because their job is to detect or fix them
    (this file included, and fix_dashes.py, audit_pages.py, build_epub.py,
    dashboard.py, build_articles.py, import_chapter_svgs.py,
    merge_cardtext.py). Exempted by name, checked individually before being
    added: every one only ever uses the character as a pattern or dict key,
    never in a comment or message written as prose.
    """
    exempt_ops = {
        "preflight.py", "fix_dashes.py", "audit_pages.py", "build_epub.py",
        "dashboard.py", "build_articles.py", "import_chapter_svgs.py",
        "merge_cardtext.py",
    }
    dashes = (chr(0x2014), chr(0x2013))
    hit, looked = [], 0
    for f in sorted(glob.glob(os.path.join(ROOT, "ops", "*.py"))):
        if os.path.basename(f) in exempt_ops:
            continue
        looked += 1
        body = io.open(f, encoding="utf-8", errors="replace").read()
        em, en = body.count(dashes[0]), body.count(dashes[1])
        if em or en:
            hit.append(f"{os.path.relpath(f, ROOT)} ({em} em, {en} en)")
    mobile_src = os.path.join(ROOT, "mobile", "quest-app")
    for ext in ("*.js", "*.jsx"):
        for f in glob.glob(os.path.join(mobile_src, "**", ext), recursive=True):
            rel = os.path.relpath(f, ROOT)
            if (os.sep + "node_modules" + os.sep) in (os.sep + rel):
                continue
            looked += 1
            body = io.open(f, encoding="utf-8", errors="replace").read()
            em, en = body.count(dashes[0]), body.count(dashes[1])
            if em or en:
                hit.append(f"{rel} ({em} em, {en} en)")
    if hit:
        fail("no-stray-dashes",
             f"{len(hit)} of {looked} source files outside the exempt "
             f"detector tools carry an em or en dash: {hit[:5]}. CLAUDE.md: "
             f"zero, anywhere, including code comments.")


def gate_indexable_pages_have_schema() -> None:
    """A crawlable top-level page should carry structured data, or say why not.

    Found 2026-09-05: quest.html, the single most-engaged page on the site
    (53 views against 61 for the home page, per GOALS.md) is explicitly
    "index, follow" and carried zero application/ld+json, alongside
    kit.html and deck-gallery.html, both indexable with no robots tag at
    all. All three were hand-authored, not generator-owned, so nothing in
    ops/build_seo.py's page loop ever touched them. Fixed by adding
    WebApplication, CollectionPage and ImageGallery markup respectively,
    each describing only what the page actually is: no fabricated rating,
    price or review, matching the DECLINED section at the foot of
    ops/build_seo.py. This checks the top-level pages directly (not the
    room/zone/article pages build_seo.py already emits schema for) so the
    same gap cannot reopen unnoticed on a ninth hand-authored page.

    deck-gallery-mudroom.html is deliberately excluded: BACKLOG-2026-H2.md
    epic 2 records it as 2 of 90 cards illustrated and intentionally held
    back from promotion until the free Entryway deck has produced evidence,
    Phil's own explicit call. Adding schema to actively promote a 2%
    complete asset would work against that decision, not honour it.
    """
    exempt = {"deck-gallery-mudroom.html"}
    hit = []
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))):
        name = os.path.basename(f)
        if name in exempt:
            continue
        body = io.open(f, encoding="utf-8", errors="replace").read()
        if re.search(r'name="robots"[^>]*noindex', body):
            continue
        if "application/ld+json" not in body:
            hit.append(name)
    if hit:
        fail("indexable-pages-have-schema",
             "indexable top-level page(s) with no structured data: %s. Add "
             "an honest schema.org block (no fabricated rating, price or "
             "review) or add a documented exemption here." % ", ".join(hit))


def gate_checker_scope() -> None:
    """A checker's input list must still cover the thing it checks.

    deploy_freshness compares production against this repository by reading
    asset references off a fixed handful of pages. That list was the home page
    alone for months, so quest.js, quest-data.js, photos.js and shop.js were
    never compared, and "production matches this repository" could have been
    printed with the Quest arbitrarily out of date.

    Widening the list fixed that instance. This fixes the next one: if a page
    ever references a fingerprinted asset that none of the discovery pages
    mentions, freshness would silently stop covering it, and that now fails
    here instead.

    Deliberately about coverage, not correctness. It does not care whether the
    assets match, only that nothing the site ships is outside what the checker
    can see.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import deploy_freshness as DF
    except Exception:                                         # noqa: BLE001
        warn("checker-scope", "ops/deploy_freshness.py could not be imported, "
                              "so its coverage was not checked.")
        return

    pat = re.compile(r"assets/[A-Za-z0-9_./-]+\.(?:css|js)")

    # What the discovery pages can see, read from disk rather than the network
    # so this needs no egress.
    discovery = getattr(DF, "DISCOVERY_PAGES", None)
    if not discovery:
        warn("checker-scope", "deploy_freshness does not expose its discovery "
                              "page list, so coverage cannot be checked.")
        return

    seen = set()
    missing_pages = []
    for rel in discovery:
        fn = "index.html" if rel == "/" else rel.lstrip("/")
        fp = os.path.join(SITE, fn.replace("/", os.sep))
        if not os.path.exists(fp):
            missing_pages.append(rel)
            continue
        seen.update(pat.findall(io.open(fp, encoding="utf-8",
                                        errors="replace").read()))

    # Everything the site actually references anywhere.
    shipped = set()
    for f in all_pages():
        shipped.update(pat.findall(io.open(f, encoding="utf-8",
                                           errors="replace").read()))

    uncovered = sorted(a for a in shipped - seen
                       if os.path.exists(os.path.join(SITE,
                                                      *a.split("/"))))
    if missing_pages:
        fail("checker-scope",
             "deploy_freshness lists page(s) that do not exist: %s"
             % missing_pages)
    if uncovered:
        fail("checker-scope",
             "%d fingerprinted asset(s) are referenced by the site but by none "
             "of deploy_freshness's discovery pages, so production is never "
             "compared on them: %s. Add a page that references them to "
             "DISCOVERY_PAGES." % (len(uncovered), uncovered[:5]))


def gate_hooks_enabled() -> None:
    """.githooks exists; is it switched on, and will git actually run it?

    pre-commit refuses commits carrying control bytes, and refuses a commit
    that changes site/ or Dockerfile while site/build-id.txt still describes
    an older tree (added 2026-09-08, after that exact sequence shipped a red
    CI push twice in one day). pre-push refuses a push carrying an unresolved
    merge-conflict marker (added 2026-09-11, after one reached main because a
    merge was driven with plain git instead of ops/ship.py). Both are controls
    that catch a mistake at the moment it would enter or leave history rather
    than minutes later in CI. Git does not enable hooks on clone, so neither
    does anything until core.hooksPath is set, and separately, git silently
    skips a hooksPath hook that is not executable: it warns once on the
    commit or push that finds this ("hook was ignored because it's not set as
    executable") and otherwise behaves exactly like a passing hook, which is
    the same "looks clean, verified nothing" shape gate_tests() was fixed for.
    A hook file is committed as mode 100644 by default on most editors and by
    every Windows checkout, so this is not a one-time fix, it recurs: pre-push
    itself shipped that way the same day it was added, mode 100644 next to
    pre-commit's already-correct 100755, silently inert on every fresh clone
    including this one, until this gate learned to check it too.

    Warned, not failed: a fresh CI checkout will never have core.hooksPath
    set, and the build should not fall over a local setting. The point is
    that either failure mode stops being invisible.
    """
    hooks_dir = os.path.join(ROOT, ".githooks")
    hooks = [h for h in ("pre-commit", "pre-push")
             if os.path.exists(os.path.join(hooks_dir, h))]
    if not hooks:
        return
    try:
        got = subprocess.run(["git", "config", "core.hooksPath"], cwd=ROOT,
                             capture_output=True, text=True,
                             timeout=60).stdout.strip()
    except Exception:                                         # noqa: BLE001
        return
    if got != ".githooks":
        warn("hooks-enabled",
             "%s that %s is "
             "present but not enabled here (core.hooksPath is %r). Run: "
             "git config core.hooksPath .githooks"
             % (" and ".join(hooks),
                "refuse control bytes/conflict markers" if len(hooks) > 1
                else "refuses control bytes in source",
                got or "unset"))
        return
    not_exec = [h for h in hooks
                if not os.access(os.path.join(hooks_dir, h), os.X_OK)]
    if not_exec:
        warn("hooks-enabled",
             "core.hooksPath is set to .githooks, but %s not executable, "
             "so git silently skips %s on every commit/push (a one-line "
             "hint the first time, then no signal at all). Run: %s"
             % (" and ".join(".githooks/%s" % h for h in not_exec),
                "it" if len(not_exec) == 1 else "them",
                " && ".join(
                    "chmod +x .githooks/%s && git update-index --chmod=+x "
                    ".githooks/%s" % (h, h) for h in not_exec)))


def gate_agents_in_sync() -> None:
    """The versioned agent definitions must match the ones that actually run.

    claude/agents/ is the source of truth under version control; the copies
    under ~/.claude/agents/ are what Claude Code loads and executes. The README
    states they are byte-identical, and on 2026-08-31 all 14 of them were not.
    An agent you can diff in git is only useful if it is the agent that runs.

    Silent when the installed directory is absent, which is every CI checkout.
    A warning, never a failure: this is a fact about a workstation, and a build
    must not depend on one.
    """
    src = os.path.join(ROOT, "claude", "agents")
    if not os.path.isdir(src):
        return
    installed = os.path.join(os.path.expanduser("~"), ".claude", "agents")
    if not os.path.isdir(installed):
        return

    drifted, missing = [], []
    for f in sorted(glob.glob(os.path.join(src, "*.md"))):
        name = os.path.basename(f)
        other = os.path.join(installed, name)
        if not os.path.exists(other):
            missing.append(name)
            continue
        a = io.open(f, "rb").read().replace(b"\r\n", b"\n")
        b = io.open(other, "rb").read().replace(b"\r\n", b"\n")
        if a != b:
            drifted.append(name)

    if missing or drifted:
        bits = []
        if drifted:
            bits.append("%d differ (%s)" % (len(drifted), ", ".join(drifted[:3])))
        if missing:
            bits.append("%d not installed (%s)"
                        % (len(missing), ", ".join(missing[:3])))
        warn("agents-in-sync",
             "the agents that run are not the agents in git: %s. "
             "claude/README.md says they are byte-identical. "
             "Run: cp claude/agents/*.md ~/.claude/agents/"
             % "; ".join(bits))


def _workflow_run_via_api(token, name):
    """One workflow's most recent run on the default branch, over the REST
    API rather than the gh CLI.

    Returns (conclusion, created_at, error_kind); error_kind is one of None,
    "not-on-default-branch" (the file is not a workflow GitHub knows about:
    added locally and not pushed, or pushed to another branch) or "unknown"
    (a real query failure: network, auth, rate limit).
    """
    import urllib.request, urllib.error
    url = ("https://api.github.com/repos/klingdom/6s-success/actions/"
           f"workflows/{name}/runs?per_page=1")
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}",
                      "Accept": "application/vnd.github+json",
                      "User-Agent": "6s-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return None, None, "not-on-default-branch" if e.code == 404 else "unknown"
    except Exception:                                         # noqa: BLE001
        return None, None, "unknown"
    rows = data.get("workflow_runs") or []
    if not rows:
        return None, None, "never-run"
    row = rows[0]
    return row.get("conclusion"), row.get("created_at"), None


def _workflow_run_via_cli(name):
    """Same question, through an already-authenticated local gh CLI.

    Kept as the fallback for a human running preflight on a machine with
    `gh auth login` done but no GH_TOKEN/GITHUB_TOKEN in the environment,
    which is the opposite gap from the one the API path exists for.
    """
    try:
        r = subprocess.run(
            ["gh", "run", "list", "--workflow", name, "--limit", "1",
             "--json", "conclusion,createdAt"],
            cwd=ROOT, capture_output=True, text=True, timeout=90)
        out = (r.stdout or "").strip()
        if r.returncode != 0:
            err = (r.stderr or "").lower()
            if "404" in err and "not found on the default branch" in err:
                return None, None, "not-on-default-branch"
            return None, None, "unknown"
        rows = json.loads(out) if out else []
    except Exception:                                         # noqa: BLE001
        return None, None, "unknown"
    if not rows:
        return None, None, "never-run"
    row = rows[0]
    return row.get("conclusion"), row.get("createdAt"), None


def gate_workflows_healthy() -> None:
    """Is every workflow still running, and still passing?

    Publish MCP image spent twelve days failing on every run, unseen, because
    it triggers only on changes under mcp/ and nothing touched that directory.
    A pipeline can go quiet two ways: it runs and fails where only the Actions
    tab shows it, or it stops running at all, which looks exactly like health.

    This gate had never once actually run anywhere: this sandbox has no gh
    binary, and real CI's runner has gh but no GH_TOKEN/GITHUB_TOKEN exported
    to the step's environment, so `gh run list` always failed unauthenticated
    there too. "Warned rather than failed, and honest when it cannot look"
    covered for a check that could not look, ever, in either place it ran.
    Fixed the same way dashboard.py's own issue count already works around
    the same gap: call the REST API directly with a token from
    GH_TOKEN/GITHUB_TOKEN when one is in the environment (both this sandbox
    and, once wired into the workflow YAML, real CI); fall back to an
    already-authenticated local gh for a human running this by hand; only
    then warn unchecked.
    """
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    if not os.path.isdir(wf_dir):
        return
    names = sorted(os.path.basename(p)
                   for p in glob.glob(os.path.join(wf_dir, "*.yml")))
    if not names:
        return

    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    token = dashboard.gh_token()
    if not token and not shutil.which("gh"):
        warn("workflows-healthy",
             "no GH_TOKEN/GITHUB_TOKEN and gh is not installed here, so no "
             "workflow's health was checked. Unchecked, not healthy.")
        return

    failing, stale, unknown = [], [], []
    now = dt.datetime.now(dt.timezone.utc)
    for n in names:
        if token:
            conclusion, when, err = _workflow_run_via_api(token, n)
        else:
            conclusion, when, err = _workflow_run_via_cli(n)
        if err == "not-on-default-branch":
            stale.append("%s (not on the default branch)" % n)
            continue
        if err == "never-run":
            stale.append("%s (never run)" % n)
            continue
        if err:
            unknown.append(n)
            continue
        if conclusion == "failure":
            failing.append(n)
        try:
            age = (now - dt.datetime.fromisoformat(
                (when or "").replace("Z", "+00:00"))).days
            if age >= 7:
                stale.append("%s (%d days)" % (n, age))
        except ValueError:
            pass

    if unknown and len(unknown) == len(names):
        warn("workflows-healthy",
             "no workflow could be queried (unauthenticated or offline), so "
             "none was checked. Unchecked, not healthy.")
        return
    bits = []
    if failing:
        bits.append("failing: " + ", ".join(failing))
    if stale:
        bits.append("not running: " + ", ".join(stale[:4]))
    if unknown:
        bits.append("%d could not be queried" % len(unknown))
    if bits:
        warn("workflows-healthy", "; ".join(bits))


def _publish_image_runs(token, wf_name, extra_qs=""):
    """One page of publish-image.yml's own run history, newest first.

    Split out from gate_publish_image_current so a test can force its return
    value without real network access, the same shape as _workflow_run_via_api.
    """
    import urllib.request
    url = ("https://api.github.com/repos/klingdom/6s-success/actions/"
           f"workflows/{wf_name}/runs?per_page=1{extra_qs}")
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}",
                      "Accept": "application/vnd.github+json",
                      "User-Agent": "6s-preflight"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return data.get("workflow_runs") or []


def gate_publish_image_current() -> None:
    """Did the last publish-image.yml attempt actually publish what HEAD serves?

    Found 2026-09-07. Three real content fixes in one afternoon (the 114-zone
    Sustain rewrite, the Quest scroll-to-card fix, a generator-regeneration
    pass) landed on main, but the push that carried them failed
    publish-image.yml on two unrelated bugs: a stray em dash in a control doc
    and gate_stripe_price_claims catching Exception but not the SystemExit a
    missing credential raises. Both were fixed in the next few commits, but
    those fix commits touched no file under site/ or Dockerfile, so the
    path-filtered workflow never re-triggered. gate_workflows_healthy warned
    "failing: publish-image.yml" every cycle since, correctly, but a warning
    that does not say "and HEAD's site/ has never been in a successful build"
    reads as routine noise: three real fixes sat unpublished behind it with
    nobody connecting the two facts. This is the class CLAUDE.md 0.2 names
    directly: a correctly reported problem nobody acts on costs exactly as
    much as an undetected one.

    Checks the one thing that actually matters: does site/ or Dockerfile at
    HEAD differ from the commit the workflow last *successfully* published?
    If the latest run failed (or never ran) AND there is a real diff, that is
    not routine, it is undelivered work, and preflight should say so loudly
    enough that someone re-triggers the build rather than reading past it.
    """
    wf_name = "publish-image.yml"
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    if not os.path.isfile(os.path.join(wf_dir, wf_name)):
        return

    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    token = dashboard.gh_token()
    if not token:
        warn("publish-image-current",
             "no GH_TOKEN/GITHUB_TOKEN, so whether HEAD's site/ content has "
             "ever been successfully published could not be checked. "
             "Unchecked, not current.")
        return

    try:
        latest = _publish_image_runs(token, wf_name)
        goods = _publish_image_runs(token, wf_name, "&status=success")
    except Exception:                                          # noqa: BLE001
        warn("publish-image-current",
             "could not query publish-image.yml's run history. Unchecked, "
             "not current.")
        return

    if not latest:
        return  # never run at all; gate_workflows_healthy already covers this
    latest_conclusion = latest[0].get("conclusion")
    latest_status = latest[0].get("status")
    if latest_status != "completed" or latest_conclusion == "success":
        return  # currently building, or the latest attempt already succeeded

    if not goods:
        fail("publish-image-current",
             "publish-image.yml has never once succeeded, and its most "
             "recent attempt failed. Nothing under site/ has ever been "
             "published to the image the host pulls.")
        return

    good_sha = goods[0].get("head_sha")
    if not good_sha:
        return

    # The last successful build's commit may not be in a shallow local
    # history; fetch it by SHA rather than assuming it is present.
    have = subprocess.run(["git", "cat-file", "-e", f"{good_sha}^{{commit}}"],
                          cwd=ROOT, capture_output=True).returncode == 0
    if not have:
        fetched = subprocess.run(
            ["git", "fetch", "--depth=1", "origin", good_sha],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        have = fetched.returncode == 0
    if not have:
        warn("publish-image-current",
             f"publish-image.yml's last success ({good_sha[:8]}) is not "
             "fetchable here, so whether HEAD's site/ differs from it "
             "could not be checked. Unchecked, not current.")
        return

    diff = subprocess.run(
        ["git", "diff", "--quiet", good_sha, "HEAD", "--",
         "site/", "Dockerfile"],
        cwd=ROOT, capture_output=True)
    if diff.returncode != 0:
        fail("publish-image-current",
             f"publish-image.yml's most recent attempt ({latest_conclusion}) "
             f"never published: HEAD's site/ or Dockerfile differs from the "
             f"last commit it actually shipped ({good_sha[:8]}). Real "
             "content changes are sitting unpublished. Fix whatever failed "
             "and re-trigger the workflow (workflow_dispatch), or push a "
             "site/-touching commit so the path filter fires again.")


def gate_workflow_push_permissions(wf_dir=None) -> None:
    """A workflow that pushes to git must actually be allowed to.

    Found 2026-09-03, this operator, reading hourly-brief.yml's own real job
    logs rather than trusting its green checkmark: the job runs `git push
    origin HEAD:main` in its "Commit the check-in record" step but declared
    only `permissions: contents: read`, so every push failed with "Permission
    ... denied to github-actions[bot], 403". Both that step and the checkin
    step ahead of it set `continue-on-error: true`, so the job still reported
    success every single time. `git log --all --grep="Hourly check-in"`
    confirms zero such commits ever reached origin across the workflow's
    whole history: every hourly measurement this job ever took (including
    the real YouTube-published count gate_goals_published_videos_current
    depends on) was computed correctly on a real internet-connected runner
    and then silently discarded when the runner tore down. Fixed by granting
    `contents: write`. This gate is deliberately a static text check, not a
    live one: it does not need network or a token, so it catches the same
    shape in any future workflow the moment `git push` and `contents: write`
    stop appearing together, before a human ever has to notice a mysteriously
    static log file again.
    """
    d = wf_dir or os.path.join(ROOT, ".github", "workflows")
    if not os.path.isdir(d):
        return
    offenders = []
    for path in sorted(glob.glob(os.path.join(d, "*.yml"))):
        text = open(path, encoding="utf-8", errors="replace").read()
        if "git push" not in text:
            continue
        if not re.search(r"contents:\s*write", text):
            offenders.append(os.path.basename(path))
    if offenders:
        fail("workflow-push-permissions",
             f"{', '.join(offenders)} run(s) `git push` without "
             f"`contents: write` in permissions, so the push will 403 and "
             f"(if continue-on-error is set) fail silently")


def gate_workflow_no_raw_expr_in_run(wf_dir=None) -> None:
    """A run: step must never carry a bare ${{ }} expression.

    Found 2026-09-05, this operator, reading roadmap-report.yml cold.
    It interpolated a workflow_dispatch text field (github.event.inputs
    .edition, nothing validates its contents) directly into a run: block,
    and a derived step output into a second run: line, both in the same
    job that later holds the Stripe and SMTP secrets. GitHub Actions
    substitutes ${{ }} textually into the script before the shell ever
    sees it, so anything reachable there hands raw text straight to bash
    with none of YAML's or the shell's own quoting protecting it. The fix
    is always the same: put the value in env: and read it from a shell
    variable instead, which is what both call sites do now, plus one more
    of the same shape in publish-image.yml.

    This is a blanket rule, not a per-expression allowlist naming which
    inputs are "safe": a value that looks harmless today (a step output,
    a computed tag) is one workflow edit away from carrying something that
    is not, and the fix costs nothing extra to apply everywhere.

    Text-only, no PyYAML: ops/requirements.txt is deliberately stdlib-only,
    for exactly the reason fulfil-orders.yml's own comment gives (an
    unreviewed dependency running beside live credentials), so this walks
    block scalars by indentation rather than parsing the document.
    """
    d = wf_dir or os.path.join(ROOT, ".github", "workflows")
    if not os.path.isdir(d):
        return
    offenders = []
    for path in sorted(glob.glob(os.path.join(d, "*.yml"))):
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        i = 0
        while i < len(lines):
            m = re.match(r"^(\s*)run:\s*(.*)$", lines[i])
            if not m:
                i += 1
                continue
            indent, rest = m.groups()
            base = len(indent)
            rest = rest.strip()
            if rest and rest not in ("|", ">", "|-", ">-", "|+", ">+"):
                if "${{" in rest:
                    offenders.append("%s:%d" % (os.path.basename(path), i + 1))
                i += 1
                continue
            j = i + 1
            while j < len(lines):
                l2 = lines[j]
                if l2.strip() == "":
                    j += 1
                    continue
                if len(l2) - len(l2.lstrip(" ")) <= base:
                    break
                if "${{" in l2:
                    offenders.append("%s:%d" % (os.path.basename(path), j + 1))
                j += 1
            i = j
    if offenders:
        fail("workflow-run-expr-injection",
             "%s: a run: step interpolates a ${{ }} expression directly "
             "instead of going through env:, handing unescaped text to the "
             "shell in a job that may hold live secrets"
             % ", ".join(offenders))


def gate_integrations() -> None:
    """The proxied services must serve what only they could produce.

    Umami at /stats and Listmonk at /subscribe are reverse proxy hops, and a
    proxy can fail while still returning 200: an error page, a login redirect,
    an empty body with a success code. Nothing here asked them for more than a
    status code, which is the same gap that let a deactivated Stripe link and a
    twelve day MCP failure both read as healthy.

    Warned rather than failed, and silent about nothing: if the site cannot be
    reached it says the integrations were not checked, never that they work.
    """
    tool = os.path.join(ROOT, "ops", "check_integrations.py")
    if not os.path.exists(tool):
        return
    r = subprocess.run([sys.executable, tool], cwd=ROOT, capture_output=True,
                       text=True, timeout=300,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = (r.stdout or "") + (r.stderr or "")
    if "UNKNOWN" in out:
        warn("integrations",
             "the site could not be reached, so analytics and the mailing list "
             "proxy were not checked. Unchecked, not working.")
    elif "BROKEN" in out:
        bad = [l.strip() for l in out.splitlines() if "FAIL" in l]
        warn("integrations",
             "an integration answers but is not the service it should be: %s"
             % "; ".join(bad[:2]))
    elif "PARTIAL" in out:
        warn("integrations", "some integration checks could not be made.")


def gate_footer_consistent() -> None:
    """Every page's footer must match the canonical one on resources.html.

    On 2026-08-31 all 28 legacy article pages carried a footer missing "The
    Entryway Deck", so a product we sell was unlinked from every page search
    brings people to. Those pages are owned by no generator, so nothing would
    ever have corrected them and nothing was watching.

    resources.html is the source in practice already: build_articles.py,
    build_zone_pages.py and build_zone_index.py all lift their chrome from it.
    This makes that enforcement rather than convention.

    Pages one directory down legitimately carry a ../ prefix on relative links,
    so that is normalised away before comparing. Anything else is drift.
    """
    canon_path = os.path.join(SITE, "resources.html")
    if not os.path.exists(canon_path):
        warn("footer-consistent",
             "resources.html is missing, so no footer could be compared. "
             "Unchecked, not consistent.")
        return

    # Two pages deliberately carry no site footer, checked rather than assumed:
    # invest.html has its own minimal legal footer for an investor audience, and
    # the print and play page is a short notice saying the PDF has moved. Naming
    # them keeps this warning meaningful; a permanent complaint about two
    # intentional pages is how a check stops being read.
    no_footer_by_design = {"invest.html", "deck/entryway-print-and-play.html"}

    foot = re.compile(r'<footer class="site-footer">.*?</footer>', re.S)
    m = foot.search(io.open(canon_path, encoding="utf-8",
                            errors="replace").read())
    if not m:
        warn("footer-consistent",
             "resources.html has no footer, so there is nothing to compare to.")
        return
    canon = m.group(0)

    def norm(frag: str) -> str:
        # A page one level down writes ../about.html for the same link the root
        # writes as about.html. Same destination, different text.
        return frag.replace('href="../', 'href="').replace('src="../', 'src="')

    canon_n = norm(canon)
    drifted, missing = [], []
    for f in all_pages():
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        body = io.open(f, encoding="utf-8", errors="replace").read()
        mm = foot.search(body)
        if not mm:
            if rel not in no_footer_by_design:
                missing.append(rel)
            continue
        if norm(mm.group(0)) != canon_n:
            drifted.append(rel)

    if drifted:
        fail("footer-consistent",
             "%d page(s) carry a footer that differs from resources.html, so a "
             "link or an offer present on the rest of the site is absent there: "
             "%s" % (len(drifted), drifted[:4]))
    if missing:
        warn("footer-consistent",
             "%d page(s) have no site footer at all: %s"
             % (len(missing), missing[:4]))


def gate_legal_strip_current() -> None:
    """The footer legal strip must match ops/wire_legal_strip.py's own table.

    Found 2026-09-05, reading wire_legal_strip.py cold: it is never called by
    any generator, any gate, or any CI workflow, confirmed by grepping the
    whole repository for its name. Its own docstring already names the gap it
    leaves: gate_footer_consistent (above) only proves every page's strip
    matches resources.html's, so a strip that is consistently wrong across
    all 188 pages, or a strip missing the FTC affiliate disclosure link
    entirely, would still read "consistent." Nothing had ever checked the
    strip against the actual canonical table, on any page, ever.

    Currently clean (wire_legal_strip.py --check passes), so this is a
    coverage gap being closed before it produces a defect, not a live one
    being fixed.
    """
    code, out = run("wire_legal_strip.py", "--check")
    if code != 0:
        first = [l.strip() for l in out.splitlines() if "FAIL" in l][:2]
        fail("legal-strip-current",
             " / ".join(first) or "wire_legal_strip.py --check failed")


def gate_no_stray_probe_files() -> None:
    """A killed audit_visual.py or test_audit_catalog.py run must never leave
    a page-shaped file live.

    Found 2026-09-03: this operator's own preflight --deep run was killed by
    an outer 2 minute timeout while audit_visual.py's audit() was mid-flight.
    audit() writes site/<dir>/_visual_probe.html beside the page it measures
    and only removes it in a finally block; a SIGTERM that ends the interpreter
    outright does not run that finally, so the probe survived the run. The
    very next preflight pass found it: audit_pages.py flagged it as a page
    with no title or description, and gate_footer_consistent separately
    flagged it as a page with no footer, each an accidental side effect
    rather than a check built to catch this. Nothing was actually checking
    for "a probe file leaked past its own cleanup," which matters because
    site/**/_visual_probe.html is a real, committable path: a run that dies
    at the wrong moment and then gets `git add -A`'d would ship a bare,
    unstyled, titleless HTML file to production under a real site path.
    Now gitignored so it can never be committed by accident, and this gate
    fails loudly if one is ever found sitting in the tree regardless.

    Found 2026-09-05, same shape, third instance of it: test_audit_catalog.py
    writes site/_audit_catalog_fixture.html the same way, cleaned up only in
    a finally block, and a fixed name meant two overlapping runs (this
    operator's own preflight gate_tests() and a separately launched copy of
    the same file) could collide on one path, one process's write landing
    between another's write and its read. Fixed at the source by naming the
    fixture after the writing process's own pid so two runs can no longer
    share a path; this sweep is the second layer, for the file a kill signal
    still leaves behind.

    Found 2026-09-05, later the same cycle: naming each fixture by literal
    string here meant every new test that plants one needed its own patch to
    this gate, which is exactly the drift the two entries above already
    demonstrate happens. Checked every ops/tests/*.py that writes a scratch
    page and found six more, sharing none of the two names already swept:
    test_audit_links.py's _audit_link_fixture.html, test_gates.py's five
    _gate_fixture_*.html, test_measure_events.py's five
    zones/_measure_probe_*.html, test_mobile_overflow.py's three
    _fixture_*.html, test_quest_flow.py's _quest_flow_probe.html and
    test_web_to_mobile_import.py's _import_probe.html, every one cleaned up
    only in a finally block or a context manager's __exit__, so every one is
    exactly as exposed to a SIGTERM mid-run as the two already fixed. No real
    page anywhere in site/ starts with an underscore (checked: zero matches
    in `git ls-files site`), which is exactly why every one of these scripts
    picked that prefix, so the sweep now matches the convention itself
    rather than each name that currently uses it, and a script written next
    month needs no matching edit here as long as it keeps the convention.
    """
    stray = sorted(
        os.path.relpath(f, ROOT).replace(os.sep, "/")
        for f in glob.glob(os.path.join(SITE, "**", "_*.html"), recursive=True))
    if stray:
        fail("stray-probe-files",
             "%d leftover probe/fixture file(s) sitting in site/, left "
             "behind by a run that was killed mid-audit: %s. Deleting "
             "them now so the pages/tests/footer gates below do not fail on "
             "a symptom of this same cause." % (len(stray), stray[:4]))
        # Found 2026-09-10: this gate ran after gate_existing and gate_tests
        # in main()'s own order, so a stray file from an earlier killed run
        # was caught here only after audit_pages.py had already misread it as
        # a real page sharing a duplicate title, and a zone-page test had
        # already read it as a malformed zone page, both symptoms of the one
        # cause this gate exists to name. Moved to run first in main(), right
        # after bootstrap, and now deletes what it finds after reporting it,
        # so the run that hits this reports one clear failure instead of
        # three confusing ones, and the gates below get a clean tree.
        for f in stray:
            try:
                os.remove(os.path.join(ROOT, f))
            except OSError:
                pass


def gate_no_tracked_gitignored_dirs() -> None:
    """A file git tracks inside a directory `.gitignore` says is generated
    must never sit there, because a script that globs that directory cannot
    tell a real leftover from the fresh output it is about to produce.

    Found 2026-09-11 reading ops/render_cards.py cold: a bare run with no
    `--card`/`--all` flag globs `build/card-fronts/*.html` and renders
    whatever it finds. `.gitignore` lists `build/card-fronts/` so the
    directory is meant to hold only a checkout-local build; git ls-files
    showed 5 tracked files there anyway (EM-005, EM-006, EP-005, ET-007,
    ET-012), the fossil of a commit made before that gitignore line existed
    (245bdf87). A cold run in a sandbox with no other cards built (no
    reviewed hero photos here to build from) sees only those 5 and reports
    them as the whole deck, which happened live in this exact session: two
    genuine `overflows its box` failures printed, and both traced back to a
    hero photo the committed HTML references that the sandbox does not have
    on disk (`build/heroes/` is separately gitignored), not to a real card
    defect. Confirmed by planting a real placeholder PNG at that path and
    re-measuring the same committed file clean. The 5 files carry no other
    drift (regenerating fresh and diffing found only the image tag), so
    this is inert to production, but it cost real time to tell a stray
    fossil apart from a live defect, and the next reader should not have
    to redo that. `git rm --cached` clears tracking; the files stay on disk
    since `.gitignore` already covers the path.

    Checks all 22 directories `.gitignore` names, not just this one, since
    the failure mode (a script globbing a "generated, gitignored" directory
    and finding old committed debris mixed in with nothing else) applies to
    any of them equally.
    """
    ignored_dirs = []
    gi = io.open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read()
    for line in gi.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line.endswith("/"):
            ignored_dirs.append(line.rstrip("/"))
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                              capture_output=True, text=True, timeout=30)
        tracked = out.stdout.splitlines()
    except Exception as e:                                     # noqa: BLE001
        warn("tracked-gitignored", f"could not list git-tracked files: {e}")
        return
    stray = []
    for d in ignored_dirs:
        prefix = d + "/"
        stray.extend(t for t in tracked if t.startswith(prefix))
    if stray:
        fail("tracked-gitignored",
             "%d file(s) git tracks inside a directory .gitignore says is "
             "generated, so a fresh checkout and a script that globs that "
             "directory disagree about what is there: %s. Run "
             "`git rm --cached <path>` for each (the files themselves are "
             "fine to keep on disk)." % (len(stray), stray[:6]))


def gate_status_report_network_unknown() -> None:
    """A network probe this sandbox's own egress policy answers in the real
    destination's place, or that fails for any other reason, must never
    render as a specific "live" or "not configured" claim.

    Found 2026-09-01 running ops/status_report.py cold: it reported
    "6s-success.com  live" and "vhost for us  NO, falls through to
    default" in the same report whose own "THE ONE CONSTRAINT" paragraph
    said reachability could not be checked this run, a direct copy-vs-copy
    contradiction. Verified with curl, not assumed: the VPS probe's
    "HTTP Error 403: Forbidden" was not the production server, it was this
    sandbox's own proxy ("x-deny-reason: host_not_allowed", body "Host not
    in allowlist"). The domain check hit the same wall from a different
    angle (a failed HTTPS CONNECT, caught by a bare except that defaulted
    is_parked to False, i.e. "confirmed live"). Same defect class
    dashboard.py's own gates (6.9 to 6.17) already fixed nine times over;
    status_report.py had never been given the same treatment. Fixed with
    domain_state()/vhost_state(), pure functions so this gate can prove
    the decision without shelling out to the network.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import status_report as sr

    bad = []
    if sr.domain_state(None) != "unknown":
        bad.append("domain_state(None) returned %r, not 'unknown'"
                   % sr.domain_state(None))
    if sr.domain_state(True) != "parked":
        bad.append("domain_state(True) returned %r, not 'parked'"
                   % sr.domain_state(True))
    if sr.domain_state(False) != "live":
        bad.append("domain_state(False) returned %r, not 'live'"
                   % sr.domain_state(False))
    if sr.vhost_state(None) != "unknown":
        bad.append("vhost_state(None) returned %r, not 'unknown'"
                   % sr.vhost_state(None))
    if sr.vhost_state(True) != "yes":
        bad.append("vhost_state(True) returned %r, not 'yes'"
                   % sr.vhost_state(True))
    if sr.vhost_state(False) != "no":
        bad.append("vhost_state(False) returned %r, not 'no'"
                   % sr.vhost_state(False))
    if bad:
        fail("status-report-network-unknown",
             "an unmeasured network state would render as a specific "
             "claim rather than 'could not be checked': %s" % "; ".join(bad))


def gate_status_report_products_consistent() -> None:
    """The owner-facing status report must never hand-type a "how much of the
    catalogue can somebody actually buy" figure that can drift from the real
    one.

    Found 2026-09-01 reading ops/status_report.py and ops/status_pdf.py cold,
    the same read that produced the network-unknown fix just above this gate:
    both reports still described the catalogue's pre-launch MVP shape ("3 SKUs
    deliverable, 8 priced SKUs have nothing behind them", "test mode",
    "blocked by 13 unfilled front matter fields, issue #3", closed on
    2026-08-25) while ops/audit_catalog.py and ops/check_sellable.py both
    confirm 155 of 159 live catalogue items already have a working Stripe
    Payment Link today. The HTML summary table was the sharpest copy-vs-copy
    case: its own "Deliverable today" row read "consulting only" three lines
    below a "THE ONE CONSTRAINT" paragraph, built from the same d/S dict in
    the same function, that already said "158 of 159". Fixed by computing
    catalogue_buyable once in gather() from the live data.js catalogue (the
    same file ops/audit_catalog.py checks) and having every render site read
    it, rather than typing a number by hand at each one.

    This gate proves the wiring holds without touching the network: it
    builds a synthetic report with a known buyable count and asserts the
    plain text, the HTML table, and the subject-relevant total all agree
    with it, so a future hand-typed override at any one render site fails
    here instead of shipping.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import status_report as sr

    d = {
        "generated": "2026-01-01 00:00",
        "state": {
            "overall": "YELLOW", "overall_why": "test", "revenue_text": "$0",
            "customers_text": "0", "email_list": 0, "needs_phil": 0,
            "constraint": "synthetic constraint for gate_status_report_products_consistent",
        },
        "domain": {"status": 200, "title": "t", "parked": False,
                   "a_record": "0.0.0.0", "nameservers": [], "mx_working": True},
        "vps": {"ip": "0.0.0.0", "ports": {22: False, 80: True, 443: True,
                3000: False, 8973: False}, "default_title": "t",
                "as_domain_title": "t", "vhost_configured": True},
        "image_public": True,
        "experiments": {"designed": [], "executed": 0, "blocked_reason": "x"},
        "content": {"chapters": 50, "words": 1, "rooms": 20, "zones": 114,
                   "manual_kb": 1, "epub_mb": 1, "sample_pdf_mb": 1,
                   "site_pages": 190, "deck_rooms": 0, "video": "0/114",
                   "social_units": 1},
        "catalogue": {"Micro Zone Packs": 109}, "catalogue_total": 111,
        "catalogue_buyable": 107, "catalogue_free": 3,
        "catalogue_unready": ["Corporate Lean 6S"],
        "catalogue_buyable_other": 105,
        "decks": {"Entryway": 72}, "decks_withheld": {"Entryway": 18},
        "issues": [], "issues_available": True,
        "commits_7d": 1, "recent": [], "retros": [],
    }
    _, text, html = sr.render(d)
    bad = []
    if "BUYABLE NOW             107" not in text:
        bad.append("plain text does not report the computed buyable count (107)")
    if "Buyable today</td>" not in html or "107 of 111" not in html:
        bad.append("HTML summary table does not report '107 of 111' buyable")
    if "consulting only" in html.lower():
        bad.append("HTML summary still carries the old hardcoded "
                    "'consulting only' claim")
    if "18 of the Entryway deck's cards are withheld" not in text:
        bad.append("plain text does not report the computed withheld-card "
                    "count (18), same drift shape gate_status_report_"
                    "products_consistent already gates for the buyable count")
    if bad:
        fail("status-report-products-consistent",
             "the report's buyable-catalogue figure is not wired end to "
             "end from the computed count: %s" % "; ".join(bad))


def gate_roadmap_report_issues_unknown() -> None:
    """The four-times-daily roadmap report must never report zero open
    GitHub issues just because gh could not be reached.

    Found 2026-09-01 running ops/roadmap_report.py cold: gh is not installed
    in this sandbox, and repo()'s sh() call swallowed the resulting
    FileNotFoundError into "", which json.loads() then read the same way it
    reads a genuine empty issue list. The report sent to Phil printed "0
    open issues, 0 labelled decision" while GitHub actually had 9 open
    issues, 5 of them labelled decision. Same defect class dashboard.py's
    own gates (6.9 to 6.17) and status_report.py's network-unknown gate
    already fixed; roadmap_report.py had never been swept. Fixed with
    sh_checked(), returning None on any failure, and open_issues_text() /
    decisions_waiting_text(), pure functions so this gate can prove the
    render decision without shelling out to gh.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import roadmap_report as rr

    bad = []
    if rr.open_issues_text(None) == "0":
        bad.append("open_issues_text(None) renders as '0'")
    if rr.open_issues_text(3) != "3":
        bad.append("open_issues_text(3) renders as %r, not '3'" % rr.open_issues_text(3))
    if rr.decisions_waiting_text(None) == "0":
        bad.append("decisions_waiting_text(None) renders as '0'")
    if rr.decisions_waiting_text(2) != "2":
        bad.append("decisions_waiting_text(2) renders as %r, not '2'"
                    % rr.decisions_waiting_text(2))
    if bad:
        fail("roadmap-report-issues-unknown",
             "an unreachable gh would render as zero open issues rather than "
             "'could not be checked': %s" % "; ".join(bad))


def gate_roadmap_report_backlog_done() -> None:
    """A finished backlog row must never be offered to Phil as still waiting
    on him, or listed as next in the queue.

    Found 2026-09-01 reading ops/roadmap_report.py cold: backlog_next() had
    no done check at all, so the report was listing 2.9 (the Stripe payment
    outage, closed 2026-08-30) under "DECISIONS WAITING ON YOU" and 1.6
    (done 2026-08-29) under "NEXT IN THE QUEUE", both already finished work
    presented as open. Fixed with is_backlog_row_done(), checked against the
    real backlog rather than a synthetic one, since the whole point is that
    the real file's rows are classified correctly, not that some hypothetical
    row would be.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import roadmap_report as rr

    items = rr.backlog_next()
    ids = {i["id"] for i in items}
    bad = []
    if "2.9" in ids:
        bad.append("2.9 (done 2026-08-30) still appears in backlog_next()")
    if "1.6" in ids:
        bad.append("1.6 (done 2026-08-29) still appears in backlog_next()")
    still_open = next((i for i in items if i["id"] == "5.6"), None)
    if still_open is None:
        bad.append("5.6, which still has real open work, was wrongly dropped")
    still_open_9 = next((i for i in items if i["id"] == "5B.9"), None)
    if still_open_9 is None:
        bad.append("5B.9, whose on-device half is still open, was wrongly dropped")
    if bad:
        fail("roadmap-report-backlog-done",
             "backlog_next() misclassifies finished vs. open rows: %s"
             % "; ".join(bad))


def gate_hourly_brief_build_line() -> None:
    """The hourly brief's BUILD line must read the real measured fields.

    Found 2026-09-01 running ops/hourly_brief.py --preview cold, the same
    "run it, don't just read it" check that found the three defects in
    status_report.py, status_pdf.py and roadmap_report.py earlier this same
    day. ops/dashboard.py writes ops/state.json with keys open_p0 and
    commits_7d. The BUILD line instead read st.get('p0', '?') and
    st.get('commits7d', '?'), two names that never existed in that file, so
    every hourly mail this routine has ever sent has shown "P0 ?" and
    "commits 7d ?" regardless of the real numbers sitting right next to them
    in the same measured dict, including a run with a working Stripe key and
    real egress that measured both correctly. Fixed with a pure build_line(st)
    this gate proves directly, the same pattern the roadmap and status-report
    gates above already use.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import hourly_brief as hb
    line = hb.build_line({"overall": "YELLOW", "open_p0": 3, "needs_phil": 5,
                          "commits_7d": 403})
    bad = []
    if "P0 3" not in line:
        bad.append(f"open_p0=3 did not render as 'P0 3': {line!r}")
    if "commits 7d 403" not in line:
        bad.append(f"commits_7d=403 did not render as 'commits 7d 403': {line!r}")
    if bad:
        fail("hourly-brief-build-line",
             "the hourly brief's BUILD line does not read the real measured "
             "fields, so it would show '?' next to numbers dashboard.py "
             "already measured: %s" % "; ".join(bad))


def gate_hourly_brief_payment_links() -> None:
    """The hourly brief must surface check_live_links.py's verdict, not just
    the HTTP status of a handful of pages.

    Found 2026-09-09: check_live_links.py was written specifically to catch
    the 2026-08-30 outage (a deactivated Stripe payment link still answers
    HTTP 200, so no status check can tell it apart from a working one). It
    needs a Stripe credential AND real egress to the live site; this operator
    sandbox has never held either, so its dead/unknown branch has never fired
    against production. The one job that DOES hold both,
    .github/workflows/hourly-brief.yml, already carries STRIPE_SECRET_KEY and
    already proves real egress to 6s-success.com (it runs ops/indexnow.py in
    the same job), but never called check_live_links.py. hourly_brief.py's
    own SITE section only checked HTTP status, exactly the blind spot, and
    its COMMERCE "live payment links" line was a raw count of active links in
    the account, not a check that the live buttons point at them. So the one
    automated, credentialed, hourly mail Phil actually reads could have sat
    through a repeat of the exact outage this codebase is built around and
    still said "all pages 200".

    Fixed with hourly_brief.payment_link_summary(links), a pure function over
    check_live_links.check()'s own result shape. This proves its four real
    branches directly, without needing the network or a Stripe key, the same
    shape ops/tests/test_check_live_links.py already uses for check() itself.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import hourly_brief as hb

    cases = [
        ("ok", {"verdict": "ok", "slugs": {"a": {}}, "checked_pages": 9},
         False, "OK"),
        ("dead", {"verdict": "dead", "dead": [("abc123", ["/shop.html"])]},
         True, "OUTAGE"),
        ("unknown-with-slugs",
         {"verdict": "unknown", "slugs": {"a": {}}, "unknown": [("xyz", ["/"])]},
         True, "OUTAGE"),
        ("unreachable-no-slugs",
         {"verdict": "unknown", "slugs": {}, "note": "the live site could not be reached"},
         False, "UNCHECKED"),
        ("no-credential",
         {"verdict": "unknown", "slugs": {}, "note": "no Stripe credential in this environment"},
         False, "UNCHECKED"),
    ]
    bad = []
    for name, links, want_problem, want_word in cases:
        problem, lines = hb.payment_link_summary(links)
        text = "\n".join(lines)
        if problem != want_problem:
            bad.append(f"{name}: problem={problem}, wanted {want_problem}")
        if want_word not in text:
            bad.append(f"{name}: {want_word!r} missing from summary: {text!r}")
        if want_problem and "OK" in text.split()[0]:
            bad.append(f"{name}: a real problem must not open with OK")
    if bad:
        fail("hourly-brief-payment-links",
             "hourly_brief.payment_link_summary() does not distinguish a "
             "confirmed dead/unknown live payment link from a merely "
             "unchecked one: %s" % "; ".join(bad))

    # A dead link must reach the SUBJECT line too, not only the body, since a
    # reader scanning an inbox may never open the mail at all. Exercise the
    # real build() with everything else stubbed out and no network touched.
    real = (hb.commerce, hb.inbox, hb.site, hb.measured, hb.cll.check)
    hb.commerce = lambda: {"revenue_30d": 0, "paid_30d": 0,
                           "checkouts_started_30d": 0, "live_links": 3,
                           "balance_available": 0, "balance_pending": 0}
    hb.inbox = lambda: {"unread": []}
    hb.site = lambda: {"home": 200}
    hb.measured = lambda: {}
    hb.cll.check = lambda: {"verdict": "dead", "dead": [("abc123", ["/shop.html"])]}
    try:
        subject, _ = hb.build()
    finally:
        hb.commerce, hb.inbox, hb.site, hb.measured, hb.cll.check = real
    if "OUTAGE" not in subject:
        fail("hourly-brief-payment-links",
             "a confirmed dead live payment link does not reach the "
             "hourly brief's SUBJECT line: %r" % subject)


def gate_checkin_youtube_carry_forward() -> None:
    """The hourly self check-in must not let "could not reach YouTube" collapse
    into "the channel is empty."

    Found live 2026-09-02: a session with real egress measured
    youtube_published go from 0 to 1 at 15:02. The very next cycle, with no
    egress to YouTube, wrote None straight over that 1 in ops/state-checkin.json,
    and the old next_action() read youtube_published in (0, None) as one
    case, printing "the channel holds None" next to a "Publish" recommendation
    for a channel that was already known to hold a real video. Same failure
    direction as ops/dashboard.py's own carry_forward for revenue_month, in a
    file that function never touched. Fixed with checkin.carry_forward(),
    persisting the last MEASURED value under its own key, and rewriting
    next_action() to reason from the persisted state, not the raw
    measurement. The two hardcoded numbers in the old message ("228 videos
    and 114 caption files") are also gone, replaced with the real counts.

    Proves the fix directly against the real bug shape: a run that could not
    measure this time, sitting on a real prior "1", must neither claim the
    channel holds 0/None nor recommend publishing.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import checkin

    unmeasured_but_known_nonzero = {
        "youtube_published": None,
        "youtube_published_last_measured": 1,
        "youtube_published_measured_at": "2026-09-02 15:02",
        "videos_vertical": 114, "videos_wide": 114, "captions": 114,
        "products_live": 159,
    }
    msg = checkin.next_action(unmeasured_but_known_nonzero)
    bad = []
    if "holds None" in msg or "holds 0" in msg or "held 0" in msg:
        bad.append(f"an unmeasured-but-known-nonzero channel rendered as empty: {msg!r}")
    if "Publish." in msg:
        bad.append(f"recommended publishing to a channel already known to hold a video: {msg!r}")
    if "1" not in msg:
        bad.append(f"the last real measured count (1) is not stated: {msg!r}")

    never_measured = {
        "youtube_published": None, "youtube_published_last_measured": None,
        "videos_vertical": 114, "videos_wide": 114, "captions": 114,
    }
    msg2 = checkin.next_action(never_measured)
    if "Unknown" not in msg2:
        bad.append(f"a channel with no measurement on record did not say Unknown: {msg2!r}")
    if "0" in msg2.split("Unknown")[-1][:40]:
        bad.append(f"a never-measured channel was rendered with a specific count: {msg2!r}")

    fresh_empty = {
        "youtube_published": 0, "youtube_published_last_measured": 0,
        "youtube_published_measured_at": "now",
        "videos_vertical": 114, "videos_wide": 114, "captions": 114,
    }
    msg3 = checkin.next_action(fresh_empty)
    if "Publish." not in msg3:
        bad.append(f"a fresh, confirmed-empty channel with 100+ videos ready did not recommend publishing: {msg3!r}")

    if checkin.commits_24h_text(None).strip().isdigit():
        bad.append("commits_24h_text(None) rendered as a real number")
    if checkin.commits_24h_text(44) != "44":
        bad.append(f"commits_24h_text(44) did not render as '44': {checkin.commits_24h_text(44)!r}")

    if bad:
        fail("checkin-youtube-carry-forward",
             "ops/checkin.py's next_action() can collapse an unmeasured "
             "channel into a false claim, or a shallow-clone commit count "
             "into a truncated number: %s" % "; ".join(bad))


def gate_checkin_undelivered_media_not_fabricated() -> None:
    """checkin.py's undelivered_media must not fabricate a count when this
    environment has no Desktop delivery folder to compare against at all.

    Found live 2026-09-04, running ops/verify_media_delivery.py directly in
    this sandbox rather than trusting its own docstring: it reported 228
    narrated caption files "undelivered" against
    ~/Desktop/6s-success-videos, a path that can only ever exist on Phil's
    own machine. Every cloud sandbox and CI runner is in the identical
    state, so this false alarm would have run every single hour, and would
    have read as a growing reliability problem the moment the committed
    caption count next changed, when nothing was actually wrong: the
    checker simply cannot see Phil's real Desktop from here. Same "cannot
    check" collapsed into "confirmed bad" shape already fixed once in this
    exact file for youtube_published (gate_checkin_youtube_carry_forward),
    one field over, never carried to this sibling.

    Fixed by having verify_media_delivery.py's scan() report
    desktop_missing=True (and exit 2) when its Desktop root does not exist
    at all, and checkin.parse_undelivered() turn that into None (unmeasured)
    rather than a number; None is then carried forward under
    undelivered_media_last_measured the same way youtube_published already
    is, so a real prior reading (0, taken on Phil's own machine 2026-09-03)
    is not silently overwritten.

    Proves all three directions: no Desktop root anywhere must parse and
    scan as unmeasured, never a fabricated number; a real, confirmed-clean
    scan must still read 0; and a real reported gap must still read as a
    real number, so the check keeps its teeth on the machine it was
    written for.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import checkin
    import verify_media_delivery as vmd

    bad = []
    if checkin.parse_undelivered(2, "") is not None:
        bad.append("exit code 2 (no Desktop folder anywhere) did not parse as unmeasured (None)")
    clean = checkin.parse_undelivered(
        0, "\n  Every rendered file has a copy outside build/.\n")
    if clean != 0:
        bad.append(f"a real, confirmed-clean scan did not parse as 0: {clean!r}")
    real_gap = checkin.parse_undelivered(
        1, "\n  3 rendered file(s) exist only in build/, which is not "
           "backed up and is not in git. Run with --fix.\n")
    if real_gap != 3:
        bad.append(f"a real reported gap of 3 files did not parse correctly: {real_gap!r}")

    missing, rows, total, copied = vmd.scan("/definitely/does/not/exist/anywhere")
    if not (missing is True and total == 0 and rows == [] and copied == 0):
        bad.append("scanning a nonexistent Desktop root did not report "
                    "desktop_missing with zero total, rows and copies: "
                    f"got {(missing, rows, total, copied)!r}")

    if bad:
        fail("checkin-undelivered-media",
             "ops/checkin.py's undelivered_media can fabricate a false "
             "reliability count when no Desktop delivery folder exists "
             "here: %s" % "; ".join(bad))


# ROADMAP-2026-2029.md's own section 1 table, the arithmetic the whole
# document calls load-bearing, hand-types a price beside each SKU it names.
# Map the table's own product names to the SKU that has to keep agreeing
# with them.
ROADMAP_PRICE_SKUS = {
    "Home Edition eBook": "BK-EB",
    "Whole House Print Pack": "PACK-HOUSE",
    "Micro Zone Manual": "MZ-MANUAL",
    "Complete Digital Bundle": "BK-BUNDLE",
    "Virtual Home Consult": "CN-VIRTUAL",
    "In-Home Reset Day": "CN-INHOME",
}


def gate_dashboard_social_units_live() -> None:
    """The dashboard's "Social corpus" line must be a live count, not a guess.

    Found 2026-09-01 while fixing ops/corpus_index.py's own classifier (it was
    silently dropping 153 finished X-thread and newsletter files into "other",
    invisible to its own ready count): ops/dashboard.py's S["social_units"]
    was `2600  # corpus size established by audit; not re-counted each run`,
    a number hand typed once and never touched again while the real corpus
    the dashboard describes as "unused" changed under it. Fixed by importing
    corpus_index and computing the same ready-unit count its own CLI prints,
    with social_units_text() rendering "not measured" rather than a stale or
    fabricated number if that scan ever fails. Proves both branches: a real
    scan renders the live figure, and a failed one renders honestly rather
    than falling back to 2,600 or any other invented number.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    real = db.social_units_text(2721)
    if "2,721" not in real or "not measured" in real:
        fail("dashboard-social-units",
             f"a real unit count did not render as a live number: {real!r}")
    unknown = db.social_units_text(None)
    if "not measured" not in unknown or "~" in unknown:
        fail("dashboard-social-units",
             f"a failed scan did not render honestly as unmeasured: {unknown!r}")
    if "2600" in unknown or "2,600" in unknown:
        fail("dashboard-social-units",
             "the old hand typed 2,600 fallback is back")


def gate_affiliate_trigger() -> None:
    """Warn only when the one authorised affiliate application becomes allowed.

    PLAN-AFFILIATE-MONETISATION.md settles affiliate as an option rather than a
    revenue line, and authorises exactly one application, to Amazon Associates,
    when T2 fires: 60 outbound retailer clicks in a trailing 90 days with
    internal traffic excluded. It then says re-litigate when a trigger fires,
    not monthly, which is right and had nothing watching it.

    Silent below the threshold on purpose. A line saying "0 of 60" every run for
    a year is how a person learns to skip the warning that matters, and the
    reading is on the command deck for anyone who wants it. This speaks only
    when the answer changes, or when it could not be read at all: fired is
    None exactly when the database was unreachable, and `if fired:` alone
    treats that the same as a measured, below-threshold zero (silent), which
    is the "unknown is not unused" mistake this repository keeps re-finding,
    this time in the gate meant to guard against exactly that.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import check_affiliate_trigger as T
        fired, line = T.verdict(T.reading())
    except Exception as e:                                       # noqa: BLE001
        warn("affiliate-trigger",
             "could not evaluate the affiliate trigger (%s); UNCHECKED, which "
             "is not the same as not fired" % str(e)[:70])
        return
    if fired or fired is None:
        warn("affiliate-trigger", line)


def gate_every_payment_fulfilled() -> None:
    """Every succeeded payment must have been delivered, or somebody paid for
    nothing.

    This is the worst failure this business can have, and until now nothing
    checked it. The fulfilment workflow records delivery as `fulfilled_at` in
    the PaymentIntent's metadata, which is the right ledger: Stripe holds it, so
    two overlapping runs still deliver once. But the only thing that ever read
    that ledger was the job writing it. If a run failed, or the mailer bounced,
    or the schedule was delayed past the point anybody was watching, a paying
    customer would sit undelivered and no check anywhere would notice.

    Verified against the one real payment on 2026-09-10: $19 on 2026-08-21,
    fulfilled ten minutes later at 23:49:30Z, SKU PACK-HOUSE. So the pipeline
    has worked end to end for an actual buyer and not only for a test, which is
    worth knowing and was not written down anywhere either.

    The grace period is six hours because the fulfilment schedule does not fire
    when it is asked to: measured 2026-09-09, its real gaps average 216 minutes
    against a configured 30, worst 367. Failing at 30 minutes would fail on
    GitHub's scheduler rather than on a delivery problem. Six hours is past the
    worst observed gap and still well inside the "within a few hours" that
    thanks.html promises.

    No credential means UNCHECKED, never clean. In CI there is no Stripe key,
    and a silent pass here would be a check that reassures precisely when it
    cannot see.
    """
    import urllib.request
    import datetime as _dt

    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        path = os.path.join(ROOT, ".env.secrets")
        if os.path.exists(path):
            for line in io.open(path, encoding="utf-8"):
                if line.startswith("STRIPE_SECRET_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        warn("delivery",
             "no Stripe credential here, so whether every paying customer was "
             "delivered is UNCHECKED. That is not the same as delivered.")
        return

    try:
        req = urllib.request.Request(
            "https://api.stripe.com/v1/payment_intents?limit=100",
            headers={"Authorization": "Bearer " + key})
        data = json.load(urllib.request.urlopen(req, timeout=25))["data"]
    except Exception as e:                                       # noqa: BLE001
        warn("delivery", "could not read payments (%s); delivery UNCHECKED"
                         % str(e)[:80])
        return

    now = _dt.datetime.now(_dt.timezone.utc).timestamp()
    GRACE = 6 * 3600
    late, waiting, ok = [], 0, 0
    for p in data:
        if p.get("status") != "succeeded":
            continue
        md = p.get("metadata") or {}
        if md.get("fulfilled_at"):
            ok += 1
            continue
        age = now - (p.get("created") or now)
        if age > GRACE:
            late.append("%s (%.0f hours ago, %s)"
                        % (p.get("id", "?")[:20], age / 3600.0,
                           md.get("sku") or "no sku recorded"))
        else:
            waiting += 1

    if late:
        fail("delivery",
             "%d succeeded payment(s) have no fulfilled_at after %d hours, so "
             "somebody paid and may have received nothing: %s"
             % (len(late), GRACE // 3600, "; ".join(late[:3])))
    elif waiting:
        warn("delivery",
             "%d payment(s) are not yet delivered but are inside the %d hour "
             "grace period" % (waiting, GRACE // 3600))


def gate_pages_missing_art() -> None:
    """Count every customer-facing page that ships with no picture at all.

    Same shape as gate_deck_download_has_art, on the page surfaces. The art
    review system works: build_zone_pages refuses a hero marked "no", and a room
    page has no art until its book chapter is illustrated. What nothing recorded
    is how many pages that leaves with nothing to look at.

    Measured 2026-09-09: 7 of 114 zone pages and 11 of 20 room pages. The zone
    ones are zones whose hero was rejected. The room ones are exactly the eleven
    whose chapters, 40 to 50, have no finished images; the nine rooms that do
    have art are exactly the nine with chapters 31 to 39 illustrated.

    Together with the 12 blank cards in the free print-and-play deck, that is 30
    customer-facing surfaces with no picture, all behind one gate: image
    generation billing. A warning rather than a failure for that reason, and
    because a gate that holds unrelated work hostage to an owner gate stops
    being read.
    """
    import glob as _glob
    # Zone pages are checked for the hero figure specifically, not for "any
    # <img> anywhere": found 2026-09-11, withdrawing the
    # kitchen--primary-prep-counter hero (a real content defect, see
    # ops/hero-verdicts.json) left that page with no hero but still one
    # <img>, its "Watch this zone" video thumbnail, because it is one of the
    # 12 zones with a published video. A bare "<img\b" check went on
    # reporting the page as pictured, undercounting the very thing this
    # gate's own docstring says it measures ("zones whose hero was
    # rejected"), the day that measure first became untrue for any zone with
    # both a rejected hero and a published video.
    def _no_hero(f):
        return 'id="zone-hero"' not in _visible_html(f)

    def _no_img(f):
        return not re.search(r"<img\b", _visible_html(f))

    out = []
    for label, pattern, total_note, missing in (
            ("zone", os.path.join(ROOT, "site", "zones", "*.html"),
             "hero rejected", _no_hero),
            ("room", os.path.join(ROOT, "site", "rooms", "*.html"),
             "chapter not illustrated", _no_img)):
        pages = [f for f in _glob.glob(pattern) if not f.endswith("index.html")]
        if not pages:
            warn("page-art", "no %s pages found, so their artwork was NOT "
                             "checked" % label)
            continue
        bare = [os.path.basename(f)[:-5] for f in pages if missing(f)]
        if bare:
            out.append("%d of %d %s page(s) (%s): %s"
                       % (len(bare), len(pages), label, total_note,
                          ", ".join(sorted(bare)[:3])
                          + (", ..." if len(bare) > 3 else "")))
    if out:
        warn("page-art",
             "pages shipping with no image at all. " + " ".join(out)
             + " TWO blockers, not one: GENERATING a replacement needs free system RAM (the local model load dies at about 2 GB free of 15.8; run ops/generate_zone_heroes.py for the measured figures), and REVIEWING what it generates needs the vision billing in OWNER-ACTIONS.md 1b. Naming only the second made this read as owner-blocked when the first half needs no decision and no spend.")


def _visible_html(path: str) -> str:
    """Page markup with script and style bodies removed.

    An inline <svg> logo in the header is not artwork, and a <img> inside a
    <script> template is not on the page. Counting either would make this gate
    lie in the reassuring direction.
    """
    s = io.open(path, encoding="utf-8", errors="replace").read()
    return re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)


def gate_deck_download_has_art() -> None:
    """Cards with no artwork must not sit unnoticed in the free download.

    The verdict system works. approved_heroes() excludes any hero whose review
    said "no", which is right: a picture with a garbled label or a distorted
    object should not be printed. What nothing recorded is the CONSEQUENCE.
    A card whose hero is rejected still renders. It renders with a placeholder
    glyph where the photograph goes.

    Measured 2026-09-08: 12 of the 88 reviewed heroes are rejected, so 12 cards
    in build/cards-rendered carry a placeholder, and those cards are in
    site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf. EE-002 "Rainstorm" was
    confirmed on page 1 of that PDF by pixel-matching all 178 embedded images,
    at a distance of 0.02 out of 255.

    That download is free, ungated, linked from deck.html and deck-gallery.html,
    and it is the top of this funnel. On those same two pages the gallery shows
    Rainstorm as a photographic card with five numbered callouts, because the
    gallery is built from a completely separate source. So a visitor browses
    illustrated cards and downloads a deck in which one card in seven has no
    picture at all.

    This is a warning rather than a failure on purpose. The fix is to
    regenerate the twelve heroes, which needs image generation, which needs
    billing Phil has to enable. Failing here would hold every unrelated change
    hostage to an owner gate, which is how a gate stops being read. But it must
    be counted and named on every run, because "nobody noticed what actually
    shipped" is the defect class this repository keeps paying for.
    """
    verdicts = os.path.join(ROOT, "ops", "card-hero-verdicts.json")
    pdf = os.path.join(ROOT, "site", "downloads",
                       "6S-Entryway-Deck-PrintAndPlay.pdf")
    if not os.path.exists(verdicts):
        warn("deck-art", "no hero verdict file, so the free deck download was "
                         "NOT checked for missing artwork")
        return
    try:
        d = json.load(io.open(verdicts, encoding="utf-8"))
    except ValueError:
        warn("deck-art", "hero verdicts unreadable; deck artwork UNCHECKED")
        return
    missing = sorted(k for k, v in d.items()
                     if isinstance(v, dict) and v.get("verdict") != "ok")
    if not missing:
        return
    where = ("and they are in the free print-and-play download"
             if os.path.exists(pdf)
             else "(the print-and-play PDF is not in this checkout, so where "
                  "they ship was NOT confirmed here)")
    warn("deck-art",
         "%d of %d card heroes are rejected, so those cards render with a "
         "placeholder instead of a photograph, %s: %s. TWO blockers, not one: "
         "GENERATING replacements needs free system RAM (the local "
         "model load dies at about 2 GB free of 15.8), and REVIEWING "
         "them needs the vision billing in OWNER-ACTIONS.md. The "
         "first half needs no decision and no spend."
         % (len(missing), len(d), where, ", ".join(missing)))


def gate_caption_line_length() -> None:
    """No caption line may exceed the readable budget, in either caption set.

    There are two: build/video/zones, written by ops/video_srt.py and already
    guarded by gate_srt_captions_current, and build/video/zones-narrated,
    written by the render itself and guarded by nothing. The narrated ones take
    their timings from the real narration audio, so they cannot simply be
    regenerated, and that is exactly why they drift.

    Found 2026-09-10. A cycle fixed wrap_two_lines because captions were running
    past the budget, regenerated the canonical set, and the 228 narrated
    sidecars, the ones that actually ship beside the films, kept the old
    wrapping at up to 55 characters against a budget of 42. A caption that runs
    long is the wall of text the wrap exists to prevent, and it is worse on a
    phone held sideways, which is where these get watched.

    They were re-wrapped in place: same cues, same timings, same words, only the
    line breaks moved. This stops the next fix leaving them behind.
    """
    import glob as _glob
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import video_srt as _vs
        budget = _vs.LINE_CHARS
    except Exception as e:                                       # noqa: BLE001
        warn("caption-width", "cannot import video_srt (%s); UNCHECKED" % e)
        return
    folders = [os.path.join(ROOT, "build", "video", "zones"),
               os.path.join(ROOT, "build", "video", "zones-narrated")]
    looked, over = 0, []
    for folder in folders:
        for f in _glob.glob(os.path.join(folder, "*.srt")):
            looked += 1
            for line in io.open(f, encoding="utf-8", errors="replace"):
                t = line.rstrip()
                if not t or "-->" in t or t.strip().isdigit():
                    continue
                if len(t) > budget:
                    over.append("%s (%d chars)"
                                % (os.path.basename(f)[:-4], len(t)))
                    break
    if not looked:
        warn("caption-width",
             "no caption files present, so line width was NOT checked here")
        return
    if over:
        fail("caption-width",
             "%d of %d caption file(s) carry a line longer than the %d "
             "character budget: %s"
             % (len(over), looked, budget, ", ".join(sorted(over)[:4])))


def gate_films_teach_all_six_passes() -> None:
    """A film's captions must contain every pass its zone actually has.

    Until 2026-09-07 every one of the 114 films stopped after three passes and
    cut each instruction at 26 words, so Safety, Standardize and Sustain
    appeared in none of them. Safety is the fourth S precisely because it is not
    an afterthought, and a film of this method that never mentions it teaches
    the wrong method.

    That was fixed in beats() and the whole library re-rendered. Seven films
    came out of that re-render still teaching three, and every existing check
    passed them: the files were present, recent, the right length, with real
    audio and captions that matched their own video exactly. They were the first
    seven of a 7-hour batch, rendered in the minutes before the fix landed,
    and because the driver spawns a process per film the rest picked the new
    code up and these did not. Nothing compared a film against the CONTENT it
    was supposed to carry, only against itself, so a self-consistent stale film
    was indistinguishable from a correct one.

    The label words are stripped from both sides before matching. The renderer
    prints the pass name as its own caption cue, which can land in the middle of
    an instruction and split a phrase across two cues; without stripping them
    this check reported nine false positives, and a check that cries wolf nine
    times in 114 is a check that gets ignored.
    """
    import glob as _glob
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    folder = os.path.join(ROOT, "build", "video", "zones-narrated")
    if not os.path.isdir(folder) or not _glob.glob(os.path.join(folder, "*.srt")):
        warn("films-six-passes",
             "no narrated captions present, so film CONTENT was NOT checked "
             "here. Run where the films are.")
        return
    try:
        import video_zone as _vz
    except Exception as e:                                   # pragma: no cover
        warn("films-six-passes", "cannot import video_zone (%s); UNCHECKED" % e)
        return

    LABELS = ("sort", "straighten", "shine", "safety", "standardize", "sustain")
    LABEL_RE = re.compile(r"\b(?:%s)\b" % "|".join(LABELS))
    WS = re.compile(r"\s+")
    CUE_N = re.compile(r"^\d+\s*$", re.M)
    STAMP = re.compile(r"\d\d:\d\d:\d\d[,.]\d\d\d --> "
                       r"\d\d:\d\d:\d\d[,.]\d\d\d")

    def _norm(t):
        return WS.sub(" ", re.sub(r"[^a-z0-9 ]", " ", (t or "").lower())).strip()

    def _caption(path):
        raw = io.open(path, encoding="utf-8", errors="replace").read()
        raw = STAMP.sub(" ", CUE_N.sub(" ", raw))
        return WS.sub(" ", LABEL_RE.sub(" ", _norm(raw)))

    short, checked = [], 0
    for room, z in _vz.zones():
        slug = _vz.zone_slug(room, z["zone"])
        path = os.path.join(folder, slug + ".srt")
        if not os.path.exists(path):
            continue
        checked += 1
        cap = _caption(path)
        miss = []
        for k in LABELS:
            t = WS.sub(" ", LABEL_RE.sub(
                " ", _norm((z.get("passes") or {}).get(k) or ""))).strip()
            probe = " ".join(t.split()[:5])
            if probe and probe not in cap:
                miss.append(k)
        if miss:
            short.append("%s (no %s)" % (slug, ",".join(miss)))
    if not checked:
        warn("films-six-passes", "no zone matched a caption file; UNCHECKED")
        return
    if short:
        fail("films-six-passes",
             "%d of %d film(s) do not teach every pass their zone has, which "
             "is what the whole library was re-rendered to fix: %s"
             % (len(short), checked, "; ".join(short[:4])))


def gate_films_match_their_captions() -> None:
    """A narrated film must not be shorter than its own caption track.

    The 2026-09-07 re-render, the one that put Safety, Standardize and Sustain
    into films that had only ever taught three of the six S's, reported 187
    made and 17 failed. 227 of the 228 files were on disk afterwards with recent
    timestamps, plausible durations and real audio, so every signal a person
    looks at said the batch had worked. It had not. Six of those films were
    truncated, because the renderer writes the video and then fails while
    building narration, leaving a short file where a complete one used to be.
    The worst was the Workshop safety-and-PPE station at 98.6 seconds against
    263.4 seconds of captions: 37% of the film, and the missing 63% was the part
    about personal protective equipment.

    Nothing could have caught that by counting files, which is what the existing
    video gates do. A count cannot tell a finished film from a stump.

    The caption sidecar is the check, because it is written from the same beats
    the video is rendered from, so its last timestamp is what the film's length
    is SUPPOSED to be. If the video ends before its own captions do, the end of
    the instruction is missing.

    Three seconds of slack, because the final beat's audio can finish fractions
    before the caption cue it belongs to, and a gate that fires on rounding is a
    gate people learn to skip.
    """
    import glob as _glob
    import subprocess as _sub

    folder = os.path.join(ROOT, "build", "video", "zones-narrated")
    films = sorted(_glob.glob(os.path.join(folder, "*.mp4")))
    if not films:
        # Unchecked is not passing. The films are a build artifact and are not
        # committed, so in CI this gate has nothing to look at and must say so
        # rather than report a clean batch it never saw.
        warn("films-vs-captions",
             "no narrated films in build/video/zones-narrated, so film length "
             "was NOT checked against captions here. Run where the films are.")
        return
    try:
        _sub.run(["ffprobe", "-version"], capture_output=True, timeout=20)
    except Exception:
        warn("films-vs-captions",
             "ffprobe is not available, so %d film(s) were NOT checked against "
             "their captions" % len(films))
        return

    def _dur(path):
        r = _sub.run(["ffprobe", "-v", "quiet", "-show_entries",
                      "format=duration", "-of", "csv=p=0", path],
                     capture_output=True, text=True, timeout=60)
        try:
            return float(r.stdout.strip())
        except ValueError:
            return -1.0

    def _srt_end(path):
        t = re.findall(r"--> (\d\d):(\d\d):(\d\d)[,.](\d\d\d)",
                       io.open(path, encoding="utf-8", errors="replace").read())
        if not t:
            return 0.0
        h, m, sec, ms = t[-1]
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0

    short, unreadable, checked = [], 0, 0
    for mp4 in films:
        srt = mp4[:-4] + ".srt"
        if not os.path.exists(srt):
            continue
        d, e = _dur(mp4), _srt_end(srt)
        if d < 0:
            unreadable += 1
            continue
        checked += 1
        if e > 0 and d < e - 3:
            short.append("%s %.0fs of %.0fs"
                         % (os.path.basename(mp4)[:-4], d, e))
    if unreadable:
        warn("films-vs-captions",
             "%d film(s) could not be probed and were NOT checked" % unreadable)
    if short:
        fail("films-vs-captions",
             "%d of %d film(s) end before their own captions do, so the end of "
             "the instruction is missing: %s"
             % (len(short), checked, "; ".join(short[:4])))


def gate_srt_captions_current() -> None:
    """Every rendered zone video's caption sidecar must match its own beats.

    ops/video_srt.py writes an SRT sidecar for every zone video: the words
    are otherwise baked into the pixels of a typographic slide, which
    YouTube cannot index, a screen reader cannot speak, and a deaf viewer
    cannot read, so the captions are what makes the video reachable at all
    once it is posted. All 114 committed .mp4/.srt pairs already agree, but
    nothing chains or checks the two together: ops/video_zone.py's own
    main() renders one video per call and never touches captions, and
    ops/render_all_zone_videos.py, the batch driver, never calls
    video_srt.py either. A future edit to beats() (new zone content, a
    re-timed slide) could ship a video whose caption text or timing has
    silently drifted from what plays, the same "generator's real output
    nothing checks" shape issue #26 already names for a dozen other
    pipelines this week. Regenerates each committed caption from the same
    beats() the video itself renders from and compares text, not that
    anyone remembered to run video_srt.py a second time.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    VS = importlib.import_module("video_srt")
    import video_zone
    if not os.path.isdir(VS.OUT):
        return
    have_mp4 = {f[:-4] for f in os.listdir(VS.OUT) if f.endswith(".mp4")}
    if not have_mp4:
        return
    stale = []
    for room, z in video_zone.zones():
        slug = VS.slug(room, z["zone"])
        if slug not in have_mp4:
            continue
        path = os.path.join(VS.OUT, slug + ".srt")
        if not os.path.exists(path):
            stale.append(slug + " (missing)")
            continue
        want = VS.srt_for(room, z).strip()
        have = io.open(path, encoding="utf-8", newline="").read().strip()
        if have != want:
            stale.append(slug)
    if stale:
        fail("srt-captions-current",
             "%d caption file(s) do not match their own video's beats: %s. "
             "Run: python ops/video_srt.py" % (len(stale), stale[:5]))


def gate_dashboard_zone_videos_live() -> None:
    """The dashboard's video line must not hide a real, shipped video asset.

    Found 2026-09-01, the same cycle commit a44335a ffprobe-verified all 114
    short vertical zone-reset clips ops/video_zone.py renders: the executive
    dashboard's only "Video" line reads it off a separate tracker CSV for a
    different, unstarted long-form episode production, so it printed
    "0/114 episodes shot" the same day 114 real, committed videos existed,
    the copy-vs-control shape CLAUDE.md names, here in the direction of
    hiding finished work rather than overclaiming it. Fixed with a second,
    distinct line, zone_video_line(), matched by the exact slug the renderer
    itself builds filenames from. Proves the counting logic distinguishes a
    real build from a missing one, and that a wired (site-linked) video reads
    differently from a rendered-but-unposted one, without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.zone_video_line(114, 114, False)
    if "114/114" not in built or "posted" not in built or "not posted" not in built:
        fail("dashboard-zone-videos",
             f"a real full build did not render as built-but-unposted: {built!r}")
    wired = db.zone_video_line(114, 114, True)
    if "posted from the site" not in wired or "not posted" in wired:
        fail("dashboard-zone-videos",
             f"a site-linked build did not render as posted: {wired!r}")
    none_built = db.zone_video_line(0, 114, False)
    if "0/114" not in none_built:
        fail("dashboard-zone-videos",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")


def gate_dashboard_zone_photo_videos_live() -> None:
    """The dashboard must not hide the photo-led video product either.

    Found 2026-09-02, the same shape gate_dashboard_zone_videos_live already
    caught for the typographic format one cycle earlier: ops/video_zone_photo.py
    renders a second, distinct short zone-reset video, built from a zone's own
    approved hero photograph, with 2 already committed at build/video/zones-photo/.
    Nothing on the dashboard said this format existed at all until
    zone_photo_video_line() was added. Proves the counting logic distinguishes
    a real build from a missing one, that the eligible pool is zones with an
    approved photo rather than all 114, and that a wired build reads
    differently from a rendered-but-unposted one, without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.zone_photo_video_line(90, 110, False)
    if "90/110" not in built or "posted" not in built or "not posted" not in built:
        fail("dashboard-zone-photo-videos",
             f"a real partial build did not render as built-but-unposted: {built!r}")
    wired = db.zone_photo_video_line(90, 110, True)
    if "posted from the site" not in wired or "not posted" in wired:
        fail("dashboard-zone-photo-videos",
             f"a site-linked build did not render as posted: {wired!r}")
    none_built = db.zone_photo_video_line(0, 110, False)
    if "0/110" not in none_built:
        fail("dashboard-zone-photo-videos",
             f"a missing build did not render honestly as 0 of the eligible total: {none_built!r}")
    no_pool = db.zone_photo_video_line(0, 0, False)
    if "0/0" not in no_pool:
        fail("dashboard-zone-photo-videos",
             f"an empty eligible pool did not render honestly: {no_pool!r}")


def gate_dashboard_zone_video_16x9_live() -> None:
    """The dashboard must not hide the horizontal YouTube cut either.

    Found 2026-09-02, the same shape gate_dashboard_zone_videos_live and
    gate_dashboard_zone_photo_videos_live already caught for two other video
    formats: commit 1daea3d5 rendered all 114 zone-reset clips a second time
    at 1920x1080 for YouTube (the vertical format is the wrong shape for
    YouTube's own feed), ffprobe-verified, and nothing on this dashboard said
    the horizontal cut existed at all. Proves the counting logic distinguishes
    a real build from a missing one, that the eligible pool is all 114 zones
    (every vertical clip has a horizontal counterpart by construction), and
    that a wired build reads differently from a rendered-but-unposted one,
    without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.zone_video_16x9_line(114, 114, False)
    if "114/114" not in built or "posted" not in built or "not posted" not in built:
        fail("dashboard-zone-video-16x9",
             f"a real full build did not render as built-but-unposted: {built!r}")
    wired = db.zone_video_16x9_line(114, 114, True)
    if "posted from the site" not in wired or "not posted" in wired:
        fail("dashboard-zone-video-16x9",
             f"a site-linked build did not render as posted: {wired!r}")
    none_built = db.zone_video_16x9_line(0, 114, False)
    if "0/114" not in none_built:
        fail("dashboard-zone-video-16x9",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")


def gate_dashboard_social_pins_live() -> None:
    """The dashboard must not hide the Pinterest/Instagram cards either.

    Found 2026-09-02, the same shape gate_dashboard_zone_videos_live and
    gate_dashboard_zone_photo_videos_live already caught for two other video
    formats: ops/build_social_pins.py renders a static save-and-share card
    per zone for Pinterest (2:3) and Instagram feed (4:5), the two things
    GOALS.md names as unblocked distribution prep under the traffic
    constraint, with all 114 zones already built at the time this gate was
    written. Nothing on the dashboard said this asset existed until
    social_pin_line() was added. Proves the counting logic distinguishes a
    real build from a missing one and an empty pool from a partial one,
    without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.social_pin_line(114, 114)
    if "114/114" not in built or "ready" not in built:
        fail("dashboard-social-pins",
             f"a real full build did not render as ready: {built!r}")
    none_built = db.social_pin_line(0, 114)
    if "0/114" not in none_built:
        fail("dashboard-social-pins",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")
    no_pool = db.social_pin_line(0, 0)
    if "0/0" not in no_pool:
        fail("dashboard-social-pins",
             f"an empty pool did not render honestly: {no_pool!r}")


def gate_dashboard_youtube_metadata_live() -> None:
    """The dashboard must not hide the YouTube upload text either.

    Found 2026-09-02, ranking ops/*.py by zero mentions in
    ops/NIGHTLY-LOG.md: ops/build_youtube_metadata.py writes a title,
    description, tags and timestamps for every zone video (114/114, verified
    idempotent by running it and diffing against the committed output), and
    nothing on the dashboard said this text existed, the same
    hiding-finished-work shape gate_dashboard_zone_videos_live,
    gate_dashboard_zone_photo_videos_live, gate_dashboard_zone_video_16x9_live
    and gate_dashboard_social_pins_live already caught for the videos and
    cards it sits beside. Proves the counting logic distinguishes a real
    build from a missing one and an empty pool from a partial one, without
    shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.youtube_metadata_line(114, 114)
    if "114/114" not in built or "written" not in built:
        fail("dashboard-youtube-metadata",
             f"a real full build did not render as written: {built!r}")
    none_built = db.youtube_metadata_line(0, 114)
    if "0/114" not in none_built:
        fail("dashboard-youtube-metadata",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")
    no_pool = db.youtube_metadata_line(0, 0)
    if "0/0" not in no_pool:
        fail("dashboard-youtube-metadata",
             f"an empty pool did not render honestly: {no_pool!r}")


def gate_dashboard_thumbnails_live() -> None:
    """The dashboard must not hide the YouTube thumbnails either.

    Found 2026-09-04, ranking ops/*.py by mentions in ops/NIGHTLY-LOG.md:
    ops/build_thumbnails.py (a designed 1280x720 PNG per zone, read directly
    by ops/youtube_upload.py at upload time) had exactly one mention, its own
    build commit, and all 114 were already built with nothing on the
    dashboard saying so, the same hiding-finished-work shape
    gate_dashboard_zone_videos_live, gate_dashboard_social_pins_live and
    gate_dashboard_youtube_metadata_live already caught for the assets it
    sits beside. The same pass also found build_thumbnails.py had its own
    hand-copied slug function, identical in behaviour to
    video_zone.zone_slug() only by coincidence, the exact single-source-of-
    truth gap gate_video_slug_single_source already fixed for five other
    files; pointed it at the real function too. Proves the counting logic
    distinguishes a real build from a missing one and an empty pool from a
    partial one, without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.thumbnail_line(114, 114)
    if "114/114" not in built or "ready" not in built:
        fail("dashboard-thumbnails",
             f"a real full build did not render as ready: {built!r}")
    none_built = db.thumbnail_line(0, 114)
    if "0/114" not in none_built:
        fail("dashboard-thumbnails",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")
    no_pool = db.thumbnail_line(0, 0)
    if "0/0" not in no_pool:
        fail("dashboard-thumbnails",
             f"an empty pool did not render honestly: {no_pool!r}")


def gate_dashboard_narrated_videos_live() -> None:
    """The dashboard must not hide the narrated video product either.

    Found 2026-09-03, this operator, reading Phil's own same-day commits
    rather than trusting the standing "no commit from Phil" log line: a
    running batch (ops/render_all_narrated.py) renders each zone's clip a
    third way with real synthesised voice (edge_tts) and matching captions,
    17/114 zones already built and committed under
    build/video/zones-narrated/, five of them already posted live on the
    real YouTube channel per commit 42264b13. Nothing on the dashboard said
    this format existed at all, the same hiding-finished-work shape
    gate_dashboard_zone_videos_live, gate_dashboard_zone_photo_videos_live
    and gate_dashboard_zone_video_16x9_live already caught for three earlier
    video formats. Proves the counting logic distinguishes a real build from
    a missing one, that a wired build reads differently from a
    rendered-but-unposted one, and that an empty pool renders honestly,
    without shelling out.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard as db
    built = db.narrated_video_line(17, 114, False)
    if "17/114" not in built or "posted" not in built or "not posted" not in built:
        fail("dashboard-narrated-videos",
             f"a real partial build did not render as built-but-unposted: {built!r}")
    wired = db.narrated_video_line(17, 114, True)
    if "posted from the site" not in wired or "not posted" in wired:
        fail("dashboard-narrated-videos",
             f"a site-linked build did not render as posted: {wired!r}")
    none_built = db.narrated_video_line(0, 114, False)
    if "0/114" not in none_built:
        fail("dashboard-narrated-videos",
             f"a missing build did not render honestly as 0 of the total: {none_built!r}")
    no_pool = db.narrated_video_line(0, 0, False)
    if "0/0" not in no_pool:
        fail("dashboard-narrated-videos",
             f"an empty pool did not render honestly: {no_pool!r}")


def gate_dashboard_video_carry_forward() -> None:
    """A confirmed rendered-video count must survive a run that cannot see it.

    Found 2026-09-04, this operator, the same cycle Phil's own commits
    (6d0094dd, bb9ee6d) stopped tracking build/video/*.mp4 in git and
    delivered it to his own Desktop instead. Every one of the four video
    trackers (zone_video_line, zone_photo_video_line, zone_video_16x9_line,
    narrated_video_line) scans build/video/<format>/ directly with no
    persistence, so the very next credential-less cloud run after that
    commit read the whole directory as empty and reported "0/114, not yet
    rendered" for all four formats, on the same real, already-verified 114,
    2, 114 and 75 this exact sandbox had measured against real files less
    than an hour earlier. This is the same hiding-finished-work shape
    gate_dashboard_zone_videos_live and its three siblings already catch for
    a missing dashboard line; this is the sibling defect one layer under
    them, a real count silently regressing to zero because of where a file
    lives now, not because anyone re-measured it.

    Fixed with resolve_video_count(), mirroring resolve_deploy_verdict() and
    resolve_live_links_verdict(): a live scan of 0 falls back to the last
    positive count this same sandbox or a sibling committed, carried with
    the date it was actually measured, and a fresh scan finding real files
    always overrides the carried value unconditionally.

    Proves the pure function itself, with synthetic inputs, the same pattern
    gate_dashboard_live_links_carry_forward and
    gate_dashboard_deploy_carry_forward already use for their own
    resolve_*() functions.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import dashboard
    # A live scan of 0 must recover the last positive count on record.
    carried = dashboard.resolve_video_count(
        "zone_videos", 0,
        {"zone_videos_built": 114, "zone_videos_verified_at": "2026-09-04 00:49"},
        "2026-09-04 01:48")
    if carried.get("zone_videos_built") != 114:
        fail("dashboard-video-carry-forward",
             f"resolve_video_count() dropped a confirmed rendered count on a "
             f"run that could not see the files; got {carried!r}")
    if not carried.get("zone_videos_carried_from"):
        fail("dashboard-video-carry-forward",
             f"resolve_video_count() carried the count but not the date it "
             f"was actually measured, so a reader cannot tell it apart from "
             f"a fresh count; got {carried!r}")
    line = dashboard.zone_video_line(carried["zone_videos_built"], 114, False,
                                     carried["zone_videos_carried_from"])
    if "114/114" not in line or "carried forward" not in line:
        fail("dashboard-video-carry-forward",
             f"a carried count did not render with both the real number and "
             f"an honest carried-forward label: {line!r}")
    # An unmeasured run with nothing to carry must stay honestly at 0, never
    # invent a number, the same asymmetry resolve_live_links_verdict applies.
    nothing_to_carry = dashboard.resolve_video_count(
        "zone_videos", 0, {}, "2026-09-04 01:48")
    if nothing_to_carry.get("zone_videos_built") != 0:
        fail("dashboard-video-carry-forward",
             f"resolve_video_count() manufactured a count with nothing real "
             f"to carry forward; got {nothing_to_carry!r}")
    # A real measurement this run must always win over anything carried.
    fresh = dashboard.resolve_video_count(
        "zone_videos", 90,
        {"zone_videos_built": 114, "zone_videos_verified_at": "2026-09-04 00:49"},
        "2026-09-04 01:48")
    if fresh.get("zone_videos_built") != 90 or fresh.get("zone_videos_carried_from"):
        fail("dashboard-video-carry-forward",
             f"resolve_video_count() let a stale carried value override a "
             f"fresh real measurement; got {fresh!r}")


def gate_video_slug_single_source() -> None:
    """Every zone-video writer must build its filename stem from one shared
    function, not its own reimplementation.

    Found 2026-09-03, this operator, sweeping ops/video_narrated.py and
    ops/render_all_narrated.py, the two files with zero mentions anywhere in
    NIGHTLY-LOG.md. ops/video_narrated.py's build() checked
    `vz._slug(room) if hasattr(vz, "_slug") else <hand duplicate>`, but
    video_zone.py's own _slug was defined only inside
    `if __name__ == "__main__":`, so it was never a real module attribute on
    import and the hasattr check was always False: every narrated video's
    filename came from a separately hand-written fallback, not the canonical
    slug. ops/render_all_narrated.py's own slug() was a third, independent
    copy again. All three agreed on every one of the 114 real zone/room
    names only by coincidence, because none currently contains "/" or ",";
    proved live that they diverge otherwise (a synthetic "Guest/Powder"
    room produced "guest/powder--..." from the old fallback, a literal
    slash reaching a filename stem, which os.path.join silently turns into
    a wrong nested path instead of a flat file). This is the same
    single-source-of-truth gap that caused the YouTube metadata slug
    mismatch (backlog 3.10, 13 of 114 descriptions 404ing). Fixed by making
    video_zone.zone_slug() the one real implementation and pointing both
    call sites at it. This gate proves the two are still wired together,
    not just currently coincidentally equal.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    video_zone = importlib.import_module("video_zone")
    render_all_narrated = importlib.import_module("render_all_narrated")
    if not hasattr(video_zone, "zone_slug"):
        fail("video-slug-single-source",
             "video_zone.py has no zone_slug(); the canonical slug function is missing")
        return
    mismatches = []
    for room, z in video_zone.zones():
        canonical = video_zone.zone_slug(room, z["zone"])
        batch = render_all_narrated.slug(room, z["zone"])
        if canonical != batch:
            mismatches.append((room, z["zone"], canonical, batch))
    if mismatches:
        fail("video-slug-single-source",
             "%d zone(s) where render_all_narrated.slug() disagrees with "
             "video_zone.zone_slug(): %s" % (len(mismatches), mismatches[:3]))
        return
    synthetic_room, synthetic_zone = "Guest/Powder", "Towel Bar/Ring"
    canonical = video_zone.zone_slug(synthetic_room, synthetic_zone)
    batch = render_all_narrated.slug(synthetic_room, synthetic_zone)
    if canonical != batch or "/" in canonical:
        fail("video-slug-single-source",
             "a room/zone name with a slash produced disagreeing or unsafe "
             "slugs: zone_slug=%r render_all_narrated.slug=%r"
             % (canonical, batch))


def gate_roadmap_prices_current() -> None:
    """ROADMAP-2026-2029.md's section 1 table must keep matching the live
    catalogue it claims to be "divided against."

    Found 2026-09-01 running ops/revenue_model.py cold: the live price for
    the Home Edition eBook is $9.99 (set 2026-08-27 alongside the Amazon KDP
    listing), but the roadmap's own load-bearing arithmetic table still read
    $18 and 1,111 orders, a stale hand-typed figure the 2026-08-27 price
    change never carried back into. The same cold read found a second, older
    drift one section down: 3c's "6 area bundles at $24" against a live
    price of $16. Both are exactly the copy-vs-control shape CLAUDE.md calls
    a P0 trust defect, applied to the strategy document this whole
    autonomous routine takes its priorities from rather than to a status
    report. This gate parses the table's own six rows and fails if any
    no longer matches the live catalogue price for the SKU it names.
    """
    path = os.path.join(ROOT, "ROADMAP-2026-2029.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()

    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    live_price = {p["sku"]: p["price"] for p in cat if p.get("sku")}

    bad = []
    for name, sku in ROADMAP_PRICE_SKUS.items():
        m = re.search(r"\|\s*" + re.escape(name) + r"\s*\|\s*\$([\d,.]+)\s*\|", text)
        if not m:
            bad.append(f"{name}: no longer found in the section 1 table")
            continue
        table_price = float(m.group(1).replace(",", ""))
        real_price = live_price.get(sku)
        if real_price is None:
            bad.append(f"{name} ({sku}): not found in the live catalogue at all")
        elif abs(table_price - real_price) > 0.001:
            bad.append(f"{name} ({sku}): table says ${table_price:g}, "
                        f"live catalogue says ${real_price:g}")

    # Same class of drift, one field over: found 2026-09-01 remeasuring
    # section 2's own "known, measured" page count (176, written 2026-08-24)
    # against the live site (189, articles and generated pages shipped
    # since). Not a P0 (nobody transacts off a page count), but section 5 of
    # this same document promises a monthly review against measured numbers,
    # and a "known, measured" figure that nobody re-measures is exactly the
    # hand-typed-and-frozen shape this file's other gates already catch.
    #
    # Found 2026-09-06: this count needs its own filter against a stray
    # site/**/_*.html scratch file (audit_visual.py's probe, or any of the
    # test fixtures gate_no_stray_probe_files sweeps for), which all_pages()
    # deliberately does not exclude (see its own docstring: test_gates.py's
    # Planted() fixtures rely on that prefix being visible to other gates).
    # Reproduced directly: a stray site/zones/_repro_probe.html turned a
    # real 191 into 192 and this gate failed on the drift, a false alarm
    # from a file that was never a real page, not a real one. No real page
    # anywhere in site/ starts with an underscore, confirmed by
    # gate_no_stray_probe_files's own check (`git ls-files site`).
    pm = re.search(r"(\d+)\s+pages live", text)
    if pm:
        claimed_pages = int(pm.group(1))
        real_pages = len([p for p in all_pages()
                          if not os.path.basename(p).startswith("_")])
        if claimed_pages != real_pages:
            bad.append(f"page count: ROADMAP says {claimed_pages} pages "
                        f"live, the site has {real_pages}")

    if bad:
        fail("roadmap-prices-current",
             "ROADMAP-2026-2029.md's section 1 table has drifted from the "
             "live catalogue: %s" % "; ".join(bad))


def roadmap_site_age_drift(text: str, today: dt.date):
    """Pure logic behind gate_roadmap_site_age_current, kept separate so a
    test can drive it against synthetic text without touching the real file.

    Returns (fail_reasons, warn_reasons), both lists of strings.

    Found 2026-09-11: section 2 of ROADMAP-2026-2029.md carries a dated
    correction ("the site is not nine days old... eighteen days as of this
    review") right above section 3's Horizon 1 paragraph, which still read
    "the site is nine days old", the exact original, now-even-wronger claim
    the correction three lines above exists to retire. Nobody had reread the
    second sentence when the first was fixed, the same copy-vs-control shape
    gate_roadmap_prices_current already polices one section over in the same
    file. Fixed by dating the Horizon 1 sentence and citing the same first
    analytics day. This gate re-derives the arithmetic on every run instead
    of trusting the prose: it fails if the stated day count no longer equals
    (as-of date minus first analytics day), and warns if the as-of date
    itself has gone more than 35 days stale (the monthly review cadence
    row 6.3 already commits to, given some slack).
    """
    fails, warns = [], []
    m = re.search(r"First analytics day (\d{4}-\d{2}-\d{2})", text)
    if not m:
        return fails, warns
    analytics_start = dt.datetime.strptime(m.group(1), "%Y-%m-%d").date()

    m2 = re.search(r"(\d+)\s+days as of (\d{4}-\d{2}-\d{2})", text)
    if not m2:
        fails.append("no dated 'N days as of YYYY-MM-DD' claim found in "
                      "Horizon 1; the site-age sentence needs a real date "
                      "to check its own arithmetic against")
        return fails, warns

    claimed_days = int(m2.group(1))
    as_of = dt.datetime.strptime(m2.group(2), "%Y-%m-%d").date()
    real_days = (as_of - analytics_start).days
    if claimed_days != real_days:
        fails.append(f"claims {claimed_days} days old as of {as_of}, but "
                      f"{as_of} minus the stated first analytics day "
                      f"{analytics_start} is {real_days} days")

    stale_by = (today - as_of).days
    if stale_by > 35:
        warns.append(f"the site-age sentence is dated {as_of}, {stale_by} "
                      f"days ago; re-derive it against today's real age")
    return fails, warns


def gate_roadmap_site_age_current() -> None:
    """ROADMAP-2026-2029.md's own site-age arithmetic must add up and stay dated.

    See roadmap_site_age_drift's docstring for the regression this closes.
    """
    path = os.path.join(ROOT, "ROADMAP-2026-2029.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()
    fails, warns = roadmap_site_age_drift(text, dt.date.today())
    if fails:
        fail("roadmap-site-age-current",
             "ROADMAP-2026-2029.md's site-age claim has drifted: %s"
             % "; ".join(fails))
    for w in warns:
        warn("roadmap-site-age-current", w)


def gate_marketplace_fix_current() -> None:
    """MARKETPLACE-LISTINGS.md must stop claiming a shipped fix is missing.

    Found 2026-09-06: the file (written 2026-09-03, before Phil's own
    same-day commits 9e7b1cd1/f2885908) said the Whole House pack's
    print-geometry fix "belongs upstream in ops/build_catalog.py" and, until
    it lands there, the site edition ships 152 pages against the
    marketplace's correct 76. The fix landed that same evening. Three days
    of cycles read this file and none reread the claim against the code it
    was about, which is exactly the copy-vs-control drift
    gate_roadmap_prices_current already polices one document over. This
    checks the same shape here: if ops/build_catalog.py's CSS carries the
    fixed card height (3.4in, not the original 3.5in) but the marketplace
    doc still contains the sentence declaring the fix not yet landed, fail.
    """
    doc_path = os.path.join(ROOT, "MARKETPLACE-LISTINGS.md")
    css_path = os.path.join(ROOT, "ops", "build_catalog.py")
    if not os.path.exists(doc_path) or not os.path.exists(css_path):
        return
    doc = io.open(doc_path, encoding="utf-8").read()
    css = io.open(css_path, encoding="utf-8").read()

    fixed_upstream = ".card{width:2.5in;height:3.4in" in css
    stale_claim = "Until it lands there, the two differ in page count" in doc
    if fixed_upstream and stale_claim:
        fail("marketplace-fix-current",
             "MARKETPLACE-LISTINGS.md still says the Whole House pack's "
             "print-geometry fix has not landed in ops/build_catalog.py, "
             "but build_catalog.py's CSS already carries the fixed 3.4in "
             "card height. Reread and correct the doc.")


def gate_corporate_buy_path_current() -> None:
    """GOALS.md and STATUS.md must stop claiming Corporate Lean 6S has no
    buy path once site/corporate.html actually ships one.

    Found 2026-09-06: GOALS.md's own "the constraint is the first link"
    line was rewritten 2026-09-05 20:09 (a3ca85fe) to say "Corporate Lean
    6S is the one gap, no buy path yet," two full days after Phil's commit
    9e7b1cd1 (2026-09-03) shipped site/corporate.html's qualified-enquiry
    funnel and BACKLOG-2026-H2.md 4.5 recorded it done. STATUS.md carried
    the same claim from 2026-08-27, untouched by a 2026-09-05 pass that
    read build_corporate.py directly and still missed the cross-check.
    Same shape as gate_marketplace_fix_current one function up: a doc
    claiming a shipped fix is missing. Checks the same way: if
    site/corporate.html exists (the fix), neither doc may still carry the
    exact stale sentence.
    """
    corp_path = os.path.join(ROOT, "site", "corporate.html")
    if not os.path.exists(corp_path):
        return
    stale = "Corporate Lean 6S is the one gap, no buy path yet"
    for name in ("GOALS.md", "STATUS.md"):
        doc_path = os.path.join(ROOT, name)
        if not os.path.exists(doc_path):
            continue
        doc = io.open(doc_path, encoding="utf-8").read()
        if stale in doc:
            fail("corporate-buy-path-current",
                 f"{name} still says Corporate Lean 6S has no buy path, "
                 "but site/corporate.html already ships a qualified-enquiry "
                 "one (commit 9e7b1cd1). Reread and correct the doc.")


def gate_goals_traffic_current() -> None:
    """GOALS.md's traffic baseline must be the same number everywhere it is repeated.

    Found 2026-09-02: GOALS.md was rewritten that morning with a fresh, real
    analytics pull (the Umami API token is expired, so Phil read the
    database directly), but three other places that repeat the same two
    numbers had not been updated to match, and nothing checked that they
    should be. STATUS.md still said "no confirmed visitor count... cannot
    be answered yet" in two separate sections; BACKLOG-2026-H2.md's 1.1
    still read "Phil, 3 clicks" as if the baseline pull had not happened;
    and ops/roadmap_report.py's hardcoded TRAFFIC constant, which drives the
    "Visitors per day" line in the report Phil actually receives four times
    a day by email, was still stamped 2026-08-24 with a 9-day-old figure.
    All three were caught by reading GOALS.md's own numbers against them,
    not by any check, because none existed. This gate parses GOALS.md's own
    two traffic rows and fails if ops/roadmap_report.py's TRAFFIC constant or
    STATUS.md's section 9 table no longer agrees with them.

    Widened 2026-09-03: ops/experiments.json's own observed_daily_visitors
    (what ops/experiments.py uses to print how many days a comparison
    experiment would take at the traffic actually observed) still read 3.4,
    a 2026-08-24 reading, nine days after GOALS.md was corrected with a real
    2026-09-02 pull. Nothing checked that this file agreed either, the exact
    same "one document corrected, sibling never told" shape this gate was
    built to catch, one file over. Now also fails if observed_daily_visitors
    disagrees with GOALS.md's own 30-day average, rounded to 1 decimal place.
    """
    goals_path = os.path.join(ROOT, "GOALS.md")
    if not os.path.exists(goals_path):
        return
    goals = io.open(goals_path, encoding="utf-8").read()

    # Corrected 2026-09-03. The row used to read "N sessions / 30 days" and the
    # number in it was a VISITOR count: in Umami session_id is the visitor and
    # persists across days, while visit_id is the visit. Read straight from the
    # database that day: 52 visitors, 144 visits. So the business was planning
    # against a visits figure roughly three times too small, and the gate that
    # was supposed to keep these numbers honest was enforcing agreement on a
    # mislabelled one. Agreeing everywhere is not the same as being right.
    # The row now carries both numbers and this gate refuses the old wording.
    m30 = re.search(r"Stranger to Visitor\s*\|\s*\*\*(\d+) visitors / (\d+) "
                    r"visits / 30 days\*\*", goals)
    m7 = re.search(r"Sessions, last 7 days\s*\|\s*\*\*(\d+)\*\*", goals)
    if re.search(r"Stranger to Visitor\s*\|\s*\*\*\d+ sessions", goals):
        fail("goals-traffic-current",
             "GOALS.md's baseline says 'sessions' again. That word cost us a "
             "3x error: Umami's session_id is the visitor, not the visit. "
             "Record both, as 'N visitors / M visits / 30 days'.")
        return
    if not m30 or not m7:
        warn("goals-traffic-current",
             "GOALS.md's traffic baseline rows have changed shape or moved; "
             "this gate could not read them and needs updating to match.")
        return
    sessions_30, visits_30 = int(m30.group(1)), int(m30.group(2))
    sessions_7 = int(m7.group(1))

    bad = []

    # visits must never silently equal visitors again: that equality is what
    # made the conflation invisible for as long as it lasted.
    if visits_30 == sessions_30:
        bad.append("GOALS.md reports the same number for visitors and visits "
                   f"({visits_30}). That is what the old bug looked like; if "
                   "it is genuinely true now, say so explicitly in the row.")

    rr_path = os.path.join(ROOT, "ops", "roadmap_report.py")
    if os.path.exists(rr_path):
        rr = io.open(rr_path, encoding="utf-8").read()
        tm = re.search(r'TRAFFIC\s*=\s*\{"visitors":\s*(\d+),.*?"days":\s*(\d+)',
                       rr, re.S)
        if tm:
            rr_visitors, rr_days = int(tm.group(1)), int(tm.group(2))
            vm = re.search(r'TRAFFIC\s*=\s*\{[^}]*?"visits":\s*(\d+)', rr, re.S)
            if vm and int(vm.group(1)) != visits_30:
                bad.append("ops/roadmap_report.py TRAFFIC visits=%s, GOALS.md "
                           "says %s. This field held visitors-as-visits until "
                           "2026-09-03." % (vm.group(1), visits_30))
            if rr_days == 30 and rr_visitors != sessions_30:
                bad.append(f"ops/roadmap_report.py TRAFFIC visitors="
                           f"{rr_visitors} over {rr_days} days, GOALS.md says "
                           f"{sessions_30} over 30")
        else:
            bad.append("ops/roadmap_report.py: could not find the TRAFFIC "
                        "constant to check")

    status_path = os.path.join(ROOT, "STATUS.md")
    if os.path.exists(status_path):
        status = io.open(status_path, encoding="utf-8").read()
        if f"| Sessions | {sessions_30} | Last 30 days" not in status:
            bad.append(f"STATUS.md section 9 does not carry the "
                       f"{sessions_30}/30-day figure")
        if f"| Sessions | {sessions_7} | Last 7 days" not in status:
            bad.append(f"STATUS.md section 9 does not carry the "
                       f"{sessions_7}/7-day figure")

    exp_path = os.path.join(ROOT, "ops", "experiments.json")
    if os.path.exists(exp_path):
        exp = json.load(io.open(exp_path, encoding="utf-8"))
        expected_daily = round(sessions_30 / 30, 1)
        observed = exp.get("observed_daily_visitors")
        if observed is not None and round(float(observed), 1) != expected_daily:
            bad.append(f"ops/experiments.json observed_daily_visitors="
                       f"{observed}, GOALS.md's {sessions_30}/30 days implies "
                       f"{expected_daily}")

    if bad:
        fail("goals-traffic-current",
             "GOALS.md's traffic baseline has drifted from where it is "
             "repeated: %s" % "; ".join(bad))


def gate_goals_revenue_current() -> None:
    """GOALS.md's revenue baseline must not claim $0 in the last 30 days
    while STATUS.md's own measured revenue row says otherwise.

    Found 2026-09-10: GOALS.md's revenue baseline said "$19 lifetime, one
    customer, $0 in the last 30 days," written 2026-09-02, eleven days after
    the site's only sale (2026-08-21, ROADMAP-2026-2029.md). Any 30-day
    trailing window drawn from that date forward contains the sale, so the
    claim was wrong the day it was written, and STATUS.md's own measured
    revenue row has said "$19 gross / $18.15 net | Last 30 days" for the
    same transaction the entire time: two authoritative documents disagreed
    about the single number the main goal is measured against. Corrected in
    place.

    This does not hardcode the sale date, since that would go stale the
    moment a real second sale happens; it re-reads STATUS.md's own measured
    row instead, the same cross-document check gate_goals_traffic_current
    already makes for the two numbers above this one.
    """
    goals_path = os.path.join(ROOT, "GOALS.md")
    status_path = os.path.join(ROOT, "STATUS.md")
    if not os.path.exists(goals_path) or not os.path.exists(status_path):
        return
    goals = io.open(goals_path, encoding="utf-8").read()
    status = io.open(status_path, encoding="utf-8").read()

    sm = re.search(r"\|\s*Revenue\s*\|\s*([^|]+?)\s*\|\s*Last 30 days", status)
    if not sm:
        warn("goals-revenue-current",
             "STATUS.md's 'Last 30 days' revenue row could not be found; "
             "this gate needs updating to match.")
        return
    status_zero = bool(re.match(r"^\$?0(\.0+)?\b", sm.group(1).strip()))

    goals_claims_zero = bool(re.search(
        r"\$0(?:\.0+)? (?:of revenue )?(?:earned )?in the last 30 days",
        goals, re.I))

    if goals_claims_zero and not status_zero:
        fail("goals-revenue-current",
             f"GOALS.md claims '$0 in the last 30 days' but STATUS.md's own "
             f"measured revenue row says '{sm.group(1).strip()}' for the "
             f"same window.")


def gate_risks_register_current() -> None:
    """RISKS.md must not go stale against its own stated review cadence, and
    its section 8 summary must not drift from its own table.

    Found 2026-09-03: RISKS.md's own section 22 promises the CRITICAL
    entries get re-read every operating cycle and the whole register gets a
    full review monthly, but "Last reviewed" still read 2026-08-19, over
    two weeks and dozens of recorded cycles later. In that window four
    entries had been resolved by real, dated events (RISK-0001 by a real
    sale 2026-08-21, RISK-0006 by issue #3 closing 2026-08-25, RISK-0008 by
    the catalogue reaching 158 of 159 purchasable, RISK-0010 by
    .github/workflows/checks.yml existing since 2026-09-01) and the file
    kept stating the pre-resolution version of each, including its own
    single most load-bearing sentence: section 24's "the most likely cause
    is RISK-0001," two weeks after a real transaction made that claim
    false. This gate cannot judge whether any individual risk's prose is
    still accurate, that needs a real read, but it can catch the two
    mechanical failures that let this drift unnoticed: the review date
    going stale past the file's own monthly promise, and the section 8
    summary counts (open/mitigating/closed, and how many open risks are
    CRITICAL) disagreeing with the table beneath them.
    """
    path = os.path.join(ROOT, "RISKS.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()

    bad = []

    dm = re.search(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})", text)
    if not dm:
        warn("risks-register-current",
             "RISKS.md's 'Last reviewed' date could not be found; this "
             "gate needs updating to match.")
        return
    last_reviewed = dt.date.fromisoformat(dm.group(1))
    age_days = (dt.date.today() - last_reviewed).days
    if age_days > 31:
        bad.append(f"'Last reviewed: {last_reviewed}' is {age_days} days "
                    f"old, past the file's own monthly full-review promise "
                    f"(section 22)")

    rows = re.findall(
        r"\|\s*(RISK-\d+)\s*\|[^|]+\|\s*(CRITICAL|HIGH|MEDIUM|LOW)\s*\|\s*"
        r"(OPEN|MITIGATING|CLOSED|ACCEPTED|TRANSFERRED)\s*\|", text)
    if not rows:
        bad.append("section 8's table could not be parsed; format may have "
                    "changed")
    else:
        real_open = sum(1 for _, _, s in rows if s == "OPEN")
        real_mitigating = sum(1 for _, _, s in rows if s == "MITIGATING")
        real_closed = sum(1 for _, _, s in rows if s == "CLOSED")
        real_critical_open = sum(1 for _, sev, s in rows
                                  if sev == "CRITICAL" and s == "OPEN")

        cm = re.search(
            r"(\w[\w-]*)\s+risks are open,\s*(\w[\w-]*)\s+is mitigating,\s*"
            r"(\w[\w-]*)\s+(?:are|is) closed", text)
        crm = re.search(r"(\w[\w-]*)\s+open risks are `CRITICAL`", text)
        words = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                 "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
                 "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13}

        def as_int(w):
            w = w.lower()
            if w in words:
                return words[w]
            return int(w) if w.isdigit() else None

        if cm:
            said_open, said_mitigating, said_closed = (as_int(cm.group(1)),
                                                         as_int(cm.group(2)),
                                                         as_int(cm.group(3)))
            if said_open is not None and said_open != real_open:
                bad.append(f"summary says {cm.group(1)} open, table has "
                            f"{real_open}")
            if said_mitigating is not None and said_mitigating != real_mitigating:
                bad.append(f"summary says {cm.group(2)} mitigating, table "
                            f"has {real_mitigating}")
            if said_closed is not None and said_closed != real_closed:
                bad.append(f"summary says {cm.group(3)} closed, table has "
                            f"{real_closed}")
        if crm:
            said_crit = as_int(crm.group(1))
            if said_crit is not None and said_crit != real_critical_open:
                bad.append(f"summary says {crm.group(1)} open risks are "
                            f"CRITICAL, table has {real_critical_open}")

    if bad:
        fail("risks-register-current",
             "RISKS.md has drifted from its own stated state: %s" %
             "; ".join(bad))


def gate_risks_evidence_current() -> None:
    """Every `key=value` evidence line in RISKS.md that names an
    ops/state.json key must still match the live value.

    Found 2026-09-04: RISK-0012's own evidence cited `forms_dead=14` and
    `social_units=2600`, both from whenever that entry was last written,
    against a live ops/state.json of 188 and 4,408. Neither drift meant the
    underlying problem (email_list stuck at 0) was fixed; the catalogue and
    social corpus had simply both grown since. This is the identical
    one-document-corrected-sibling-never-told shape gate_goals_traffic_current
    already catches for GOALS.md's traffic numbers, just never checked here.
    Rather than fix these two lines and leave the same gap for the next
    number that drifts, this gate reads every `key=value` token in RISKS.md,
    keeps the ones whose key is a real ops/state.json key, and fails if the
    cited value no longer matches the live one, covering every existing
    citation (email_list, forms_dead, social_units, catalog_total,
    can_take_payment, chapters_with_disclaimer, and any added later) rather
    than just the two caught this cycle.
    """
    path = os.path.join(ROOT, "RISKS.md")
    state_path = os.path.join(ROOT, "ops", "state.json")
    if not os.path.exists(path) or not os.path.exists(state_path):
        return
    text = io.open(path, encoding="utf-8").read()
    state = json.load(io.open(state_path, encoding="utf-8"))

    bad = []
    for key, cited in re.findall(r"\b([a-z][a-z_0-9]*)=([A-Za-z0-9.]+)", text):
        if key not in state:
            continue
        live = state[key]
        if isinstance(live, bool):
            match = cited.lower() == str(live).lower()
        elif isinstance(live, (int, float)):
            try:
                match = float(cited) == float(live)
            except ValueError:
                match = False
        else:
            match = cited == str(live)
        if not match:
            bad.append(f"'{key}={cited}' cited, ops/state.json has "
                        f"{key}={live}")

    if bad:
        fail("risks-evidence-current",
             "RISKS.md cites a stale ops/state.json value: %s" %
             "; ".join(bad))


def gate_no_stale_session_label() -> None:
    """STATUS.md, RISKS.md and BACKLOG-2026-H2.md must not state GOALS.md's
    retired "N sessions" traffic wording as current fact, outside a quoted
    reference to what the retired wording was.

    Found 2026-09-04: GOALS.md corrected its own traffic baseline on
    2026-09-03 from a mislabelled "47 sessions / 30 days" (a visitor count
    wearing a sessions label, per gate_goals_traffic_current's own docstring)
    to the real "52 visitors / 144 visits / 30 days", and that gate already
    refuses the old wording from reappearing in GOALS.md itself. Nothing
    checked whether the documents that repeat this as CURRENT fact had been
    told: STATUS.md's own "why this is YELLOW" narrative and two RISKS.md
    evidence lists (RISK-0005, RISK-0013) all still asserted "47 sessions in
    the last 30 days" a full day after the correction landed, the same
    one-document-corrected-sibling-never-told shape gate_risks_evidence_current
    already catches for numeric state.json citations, just not for prose
    naming a retired traffic label. Fixed all three.

    Found again 2026-09-04, twelfth cycle today, in two more places the
    first fix's regex was too narrow to reach: it only matched the literal
    lowercase phrase "sessions in the last 30 days", so it missed STATUS.md
    section 30's own restatement in ALL CAPS ("47 SESSIONS AND 328
    PAGEVIEWS IN 30 DAYS") and BACKLOG-2026-H2.md item 1.1's "47
    sessions/30 days" (no "in the last", and BACKLOG-2026-H2.md was not
    even in the checked list). Both stated the retired figure as what
    GOALS.md currently says, a full day after GOALS.md stopped saying it.
    Fixed both files' text and widened the regex: case-insensitive, matches
    "sessions" followed within 40 characters by "30 days" in any of the
    "in the last", "/", or "and N pageviews in" phrasings actually found.

    Adding BACKLOG-2026-H2.md to the checked list at first reintroduced the
    exact false-positive this gate's own 6.68 entry is written to avoid:
    that entry, and STATUS.md's own "Updated By" changelog line, both quote
    the retired phrase in double quotes while narrating that it was fixed,
    which is the correction record CLAUDE.md's Decision/Learning Memory
    sections require preserving, not a live claim. Rather than exclude the
    whole file again, strip double-quoted spans before matching: a bare,
    unquoted "N sessions ... 30 days" is a live claim; the same words
    inside quotes are a citation of the retired wording, the convention
    every fix-narrating entry in these documents already uses. Proved this
    distinction holds against the real committed text of both files, not
    just synthetic cases: after quote-stripping, STATUS.md's changelog line
    and BACKLOG-2026-H2.md's 6.68 entry both stop matching, while a planted
    unquoted regression in either still fails.

    Deliberately still not added: ROADMAP.md and ops/NIGHTLY-LOG.md, which
    also carry the retired figure but as an explicitly-labelled historical
    record (ROADMAP.md's own banner: "kept rather than deleted so the
    record shows what was believed"; the log is a retrospective account)
    rather than a claim of current fact.
    """
    bad = []
    pattern = re.compile(r"\d+\s*sessions?\b(?:(?!\.).){0,40}?30[\s-]*days",
                          re.IGNORECASE)
    for name in ("STATUS.md", "RISKS.md", "BACKLOG-2026-H2.md"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding="utf-8").read()
        text = re.sub(r'"[^"]*"', "", text)
        if pattern.search(text):
            bad.append(name)
    if bad:
        fail("no-stale-session-label",
             "%s state the retired 'N sessions ... 30 days' wording "
             "GOALS.md's own gate already refuses; cite visitors/visits "
             "instead, per GOALS.md's 2026-09-03 correction." %
             " and ".join(bad))


def _status_material_path(f: str) -> bool:
    """Does a changed file matter enough that STATUS.md should mention it?

    Deliberately excludes the artifacts a routine, content-free pass
    produces on every run (the command deck, the log, STATUS.md itself),
    so a cycle that only regenerated those does not count as drift.
    """
    if f in ("STATUS.md", "ops/NIGHTLY-LOG.md", "EXECUTIVE-DASHBOARD-LIVE.md",
             "ops/dashboard.html", "ops/state.json", "site/build-id.txt"):
        return False
    if f.startswith("site/") or f.startswith("ops/build_"):
        return True
    if f == "ops/preflight.py":
        return True
    return f in ("BACKLOG-2026-09-07.md", "BACKLOG-2026-H2.md",
                 "ROADMAP-2026-2029.md", "GOALS.md")


def status_currency_gap(status_text, commits, threshold=8):
    """Pure logic for gate_status_currency: which commits STATUS.md never
    mentioned, and whether that pile has grown past a threshold worth a
    warning.

    commits: (full_hash, subject, files) tuples for every commit made after
    STATUS.md's own last edit, oldest first. A commit only counts if it
    touched a path _status_material_path calls material; a commit is
    "mentioned" if either the 7 or 8 character abbreviation of its hash
    appears anywhere in status_text, matching how this repository's own log
    and STATUS.md already cite commits in prose (backtick-quoted short
    hashes), so no new citation format is required of anyone.

    Returns the material, unmentioned commits, but only once there are at
    least `threshold` of them; a lag of a few commits is ordinary operation
    between check-ins, not the defect this exists to catch.
    """
    gap = []
    for full_hash, subject, files in commits:
        if not any(_status_material_path(f) for f in files):
            continue
        if full_hash[:7] in status_text or full_hash[:8] in status_text:
            continue
        gap.append((full_hash[:8], subject))
    return gap if len(gap) >= threshold else []


def gate_status_currency() -> None:
    """STATUS.md should not fall many commits behind reality, unnoticed.

    Found repeatedly this week, in ops/NIGHTLY-LOG.md, not once but on at
    least six separate PM check-ins ("STATUS.md was four commits stale",
    "...ten commits stale", "...one commit stale", "...three substantive
    commits stale", twice more on 2026-09-11 alone): STATUS.md's own "This
    pass" account describes work several commits old while real fixes,
    gates, or price/product changes landed after it and were never
    mentioned. That is the same "source corrected, sibling never told"
    shape gate_goals_traffic_current and gate_risks_evidence_current already
    catch for a numeric claim, just never built for the one document whose
    entire job is describing what is happening now.

    Prior cycles explicitly considered and declined to gate this ("STATUS.md's
    own prose is not mechanically diffable the way a generator's output is"),
    and that reasoning is still correct: prose has no single correct byte
    sequence to diff against. It does not follow that nothing mechanical is
    possible. A short lag (a handful of commits) is normal, ordinary
    operation the next check-in absorbs without anyone noticing a problem.
    What actually happened, repeatedly, is that lag compounding past the
    point any single check-in reasonably catches it, silently, until a human
    or a dedicated PM pass went looking. This is the backstop for that
    compounding, not a replacement for judgement about what is worth saying:
    a WARNING, never a failure, firing only once real, unmentioned, material
    commits pile up past a threshold wide enough not to trip on an ordinary
    short lag.

    Proof this can fail: ops/tests/test_gate_status_currency.py builds a
    synthetic run of 9 material commits none of which appear in a stub
    STATUS.md and asserts the warning fires by name, then trims it to 3 and
    asserts it does not.
    """
    last = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "STATUS.md"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    ).stdout.strip()
    if not last:
        return
    rng = subprocess.run(
        ["git", "log", "%s..HEAD" % last, "--format=%H%x01%s"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    ).stdout
    commits = []
    for line in rng.splitlines():
        if "\x01" not in line:
            continue
        full_hash, subject = line.split("\x01", 1)
        out = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r",
             full_hash],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        ).stdout
        files = [f for f in out.splitlines() if f.strip()]
        commits.append((full_hash, subject, files))
    if not commits:
        return
    status_text = io.open(os.path.join(ROOT, "STATUS.md"),
                          encoding="utf-8").read()
    gap = status_currency_gap(status_text, commits)
    if gap:
        warn("status-currency",
             "STATUS.md has not mentioned %d material commit(s) since it "
             "was last edited, including %s. Its own account may now "
             "describe an older state than the repository is actually in; "
             "read `git log %s..HEAD` and bring it current."
             % (len(gap), gap[:3], last[:8]))


def gate_changelog_current() -> None:
    """CHANGELOG.md must not go silent for weeks while material work ships,
    unnoticed, the same shape gate_status_currency and
    gate_risks_register_current already guard for their own files.

    Found 2026-09-12: CHANGELOG.md's own "Last updated" line still read
    2026-08-17, 26 days and roughly 40 shipped items behind (the diagnosis
    model, the Kitchen deck, the symptom-first quest entry, the RSS feed,
    the YouTube channel link, several trust fixes), silent through all of
    it despite section 102 promising per-material-change updates and a
    weekly review. Backfilled that gap with real, commit-grounded entries
    in section 105.

    CHANGELOG.md cites change IDs and prose, not commit hashes the way
    STATUS.md's own citation convention does, so this does not attempt a
    per-commit mention check the way gate_status_currency does for that
    file. It catches the mechanical half instead: the "Last updated" date
    itself falling stale past a calendar threshold generous enough not to
    trip on an ordinary short lag between deliberate backfills, the same
    age-based shape gate_risks_register_current already uses for RISKS.md's
    monthly promise.

    Warning, not failure: prose currency is a judgement call this gate
    cannot make, only flag for a human or the next cycle to look at.

    Proof this can fail: ops/tests/test_gate_changelog_current.py stubs a
    "Last updated" date 30 days old and asserts the warning fires by name,
    then 10 days old and asserts it does not.
    """
    path = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()
    gap = changelog_staleness(text, dt.date.today())
    if gap is None:
        warn("changelog-current",
             "CHANGELOG.md's 'Last updated' date could not be found; this "
             "gate needs updating to match.")
        return
    if gap > 21:
        warn("changelog-current",
             "CHANGELOG.md's 'Last updated' date is %d days old, past the "
             "21-day threshold for a file whose own section 102 promises "
             "per-material-change updates. Read `git log` for what shipped "
             "since and add real CHG entries (section 105), not just a "
             "date bump." % gap)


def changelog_staleness(text, today):
    """Pure logic for gate_changelog_current: days between CHANGELOG.md's
    own stated 'Last updated' date and today, or None if that date could
    not be parsed."""
    m = re.search(r"\*\*Last updated:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if not m:
        return None
    last_updated = dt.date.fromisoformat(m.group(1))
    return (today - last_updated).days


def gate_no_stale_checkout_count() -> None:
    """STATUS.md must not state the retired "seven checkout sessions"
    figure as current fact, outside a quoted or otherwise clearly historical
    citation.

    Found 2026-09-07, this operator, cross-checking ROADMAP-2026-2029.md's
    own 2026-09-07 correction against its siblings rather than trusting the
    correction alone to have propagated. The roadmap fixed "seven checkout
    sessions" to the real twenty (nineteen expired, one completed, seven of
    the nineteen quoted a phantom $18 duplicate price archived 2026-09-06),
    but STATUS.md still stated "Seven checkout sessions have existed in
    total; six were abandoned" in its funnel-status prose and "1 (7 checkout
    sessions started, 6 abandoned)" in its metrics table, both untouched
    since 2026-08-29, a full nine days after the real count was known. Same
    one-document-corrected-sibling-never-told shape gate_no_stale_session_label
    already catches for the visitor/session figure, just not for this one.
    Fixed both spots in STATUS.md; this gate holds the correction.
    """
    bad = []
    pattern = re.compile(r"\bseven\s+checkout\s+sessions?\b|"
                          r"\b7\s+checkout\s+sessions?\b", re.IGNORECASE)
    for name in ("STATUS.md", "RISKS.md", "GOALS.md"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding="utf-8").read()
        text = re.sub(r'"[^"]*"', "", text)
        if pattern.search(text):
            bad.append(name)
    if bad:
        fail("no-stale-checkout-count",
             "%s state the retired 'seven/7 checkout sessions' figure "
             "ROADMAP-2026-2029.md corrected to twenty on 2026-09-07; cite "
             "the real count instead." % " and ".join(bad))


def gate_no_stale_listmonk_blocker() -> None:
    """GOALS.md, STATUS.md and RISKS.md must not state the retired
    "Listmonk root URL and from-address" diagnosis as the current O2
    blocker, outside a quoted or clearly historical citation.

    Found 2026-09-09, this operator, reading a low-mention ops/*.py file
    cold (ops/wire_signup.py) and following where it led. GOALS.md's O2
    section has said "Blocked on: Listmonk root URL and from-address"
    unchanged since the file was first written 2026-09-02. OWNER-ACTIONS.md
    item 7a itself records that this was the 2026-08-23 diagnosis and says
    plainly it "is no longer what is wrong": the from-address was already
    fixed, and the real, still-open blocker (measured 2026-09-03 against
    the running Listmonk container's own logs) is an instance-wide SMTP
    credential shared with a different business, Compassion Benchmark,
    which 553s every 6S opt-in email. That is why the signup form
    ops/wire_signup.py built on 2026-08-23 was withdrawn the same day (see
    the SIGNUP:BEGIN/END comment on every page it touched) and why the
    footer's mailto fallback is what actually runs today. GitHub issue #15
    (P0, decision) is where Phil decides between a separate Listmonk
    instance for 6S or moving Compassion Benchmark off the shared one.
    GOALS.md repeated the retired diagnosis for a full week after
    OWNER-ACTIONS.md itself said it was wrong; fixed to name the real
    blocker and cite issue #15. Same one-document-corrected-sibling-never-
    told shape gate_no_stale_session_label and gate_no_stale_checkout_count
    already catch for other figures, just not yet for this one.
    """
    bad = []
    pattern = re.compile(
        r"listmonk\s+root\s+url\s+and\s+from-address", re.IGNORECASE)
    for name in ("GOALS.md", "STATUS.md", "RISKS.md"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding="utf-8").read()
        text = re.sub(r'"[^"]*"', "", text)
        if pattern.search(text):
            bad.append(name)
    if bad:
        fail("no-stale-listmonk-blocker",
             "%s state the retired 'Listmonk root URL and from-address' "
             "diagnosis as the current O2 blocker; OWNER-ACTIONS.md item "
             "7a says that stopped being true 2026-09-03, and the real "
             "blocker is the shared SMTP identity, issue #15." %
             " and ".join(bad))


def gate_no_stale_affiliate_blocker() -> None:
    """GOALS.md's O4 must not claim every affiliate application is still
    "waiting on us, not on the networks" once ops/affiliate-accounts.json
    itself records a declined one.

    Found 2026-09-09, this operator, the same read that found the Listmonk
    blocker stale (see gate_no_stale_listmonk_blocker). GOALS.md's O4 said
    "four verification emails from 29 August that were never actioned. The
    applications are waiting on us, not on the networks," unchanged since
    2026-09-02. ops/affiliate-accounts.json, read directly, shows 5 of the
    10 programmes (the ones routed through one shared Impact partner
    account) were declined by Impact on 29 August, and that decline sat
    unread in the inbox for eight days before this repository even knew
    about it (2026-09-06). "Waiting on us, not on the networks" stopped
    being true for those five the moment that mail was read; only 3
    programmes (Amazon, Office Depot, Etsy) are genuinely still stuck on an
    unconfirmed verification email today. Fixed GOALS.md to split the two
    situations apart rather than repeat the single stale sentence.

    This gate reads the real JSON rather than grepping for a stale figure,
    so it stays useful if the count of declined programmes changes again:
    it fails whenever GOALS.md's O4 asserts every application is still
    "waiting on us" (no acknowledgement of any decline) while the ledger
    itself already records one.
    """
    goals_path = os.path.join(ROOT, "GOALS.md")
    accounts_path = os.path.join(ROOT, "ops", "affiliate-accounts.json")
    if not os.path.exists(goals_path) or not os.path.exists(accounts_path):
        return
    goals = io.open(goals_path, encoding="utf-8").read()
    o4 = goals[goals.find("O4."):]
    o4 = o4[:o4.find("\n### ")] if "\n### " in o4 else o4
    accounts = json.loads(io.open(accounts_path, encoding="utf-8").read())
    declined = [k for k, v in accounts.items()
                if not k.startswith("_") and v.get("status") == "declined"]
    claims_all_waiting = bool(re.search(
        r"waiting on us,?\s*not on the networks", o4, re.IGNORECASE))
    acknowledges_decline = bool(re.search(
        r"declin", o4, re.IGNORECASE))
    if declined and claims_all_waiting and not acknowledges_decline:
        fail("no-stale-affiliate-blocker",
             "GOALS.md's O4 claims every affiliate application is 'waiting "
             "on us, not on the networks' with no mention of a decline, but "
             "ops/affiliate-accounts.json records %d declined (%s). "
             "Read the real ledger, not a 29-August diagnosis." %
             (len(declined), ", ".join(sorted(declined))))


def gate_architecture_doc_current() -> None:
    """ARCHITECTURE.md must not assert absences that have since become
    present, for the two claims that are cheap to verify by name.

    Found 2026-09-11, this operator, cold-reading the 8 governance docs
    never once cited in ops/NIGHTLY-LOG.md (per BACKLOG-2026-09-07.md's
    step-5d lane). ARCHITECTURE.md, last verified 2026-08-17, still said
    "no CI, no .github directory, no workflows" and "no payment
    processing" / "it cannot accept their money" as its closing line. Both
    were false the day this gate was written: 9 workflows exist under
    .github/workflows/, and Stripe Payment Links have been live on product
    pages long enough to clear one real sale (2026-08-21, see GOALS.md).
    RISKS.md already tracked both as CLOSED; ARCHITECTURE.md, the doc every
    agent is told to read first, never got the same correction and
    directly contradicted its own sibling document. Corrected the same
    cycle this gate was added.

    Checks two independent, cheap-to-verify facts rather than trusting a
    static count: that .github/workflows actually holds files whenever
    the doc still claims none exist, and that site/ actually links a real
    Stripe Payment Link whenever the doc still claims payment does not
    exist. Either check can fail in either direction, so a genuine future
    removal of CI or of Payment Links would also be caught here, not just
    the original false-negative shape.
    """
    doc_path = os.path.join(ROOT, "ARCHITECTURE.md")
    if not os.path.exists(doc_path):
        return
    text = io.open(doc_path, encoding="utf-8").read()

    workflows_dir = os.path.join(ROOT, ".github", "workflows")
    has_workflows = (os.path.isdir(workflows_dir) and
                      any(f.endswith((".yml", ".yaml"))
                          for f in os.listdir(workflows_dir)))
    claims_no_ci = bool(re.search(
        r"no CI,?\s*no [`\"']?\.github[`\"']? directory,?\s*no workflows",
        text)) and "~~no CI" not in text
    if has_workflows and claims_no_ci:
        fail("architecture-doc-current",
             "ARCHITECTURE.md still claims 'no CI, no .github directory, "
             "no workflows' but %s exists with workflow file(s). Correct "
             "the claim rather than repeat it." % workflows_dir)

    has_payment_link = False
    site_dir = os.path.join(ROOT, "site")
    if os.path.isdir(site_dir):
        for fn in os.listdir(site_dir):
            if not fn.endswith(".html"):
                continue
            try:
                page = io.open(os.path.join(site_dir, fn),
                                encoding="utf-8").read()
            except OSError:
                continue
            if "buy.stripe.com" in page:
                has_payment_link = True
                break
    claims_no_payment = ("no payment processing" in text and
                          "~~no payment processing~~" not in text)
    claims_cannot_accept_money = bool(re.search(
        r"it cannot accept their money\.?\s*$", text.rstrip())) and \
        "used to read" not in text[max(0, text.rfind(
            "it cannot accept their money") - 400):]
    if has_payment_link and (claims_no_payment or claims_cannot_accept_money):
        fail("architecture-doc-current",
             "ARCHITECTURE.md still claims the site has no payment "
             "processing / cannot accept money, but a real Stripe Payment "
             "Link (buy.stripe.com) is live in site/. Correct the claim; "
             "see GOALS.md for the one real sale this contradicts.")


def gate_visual_strategy_truncation_current() -> None:
    """PLAN-VISUAL-STRATEGY.md must not claim the video-truncation defect is
    live without also saying it was fixed, and the fix it names must still
    be in the code.

    The plan (written 2026-09-07, `ux-frontend`) measured that 341 of 342
    instruction slides across the 114 films were cut off mid-sentence and
    only 3 of 6 passes ever appeared, then stated in present tense "Today
    all 114 films fail V1 and V2." That was fixed in the same commit that
    introduced the document (`2d99fecb`, same day): `ops/video_zone.py`'s
    `beats()` now splits on sentence boundaries via `_sentence_chunks()`
    and renders all six passes. Found 2026-09-09: the plan's own claim was
    never updated to say so, so a future cycle reading it cold would either
    re-do already-shipped work or misjudge the film pipeline's real state.
    Corrected the same cycle this gate was added.

    This gate checks both halves rather than only the document: the claim
    must carry a correction, and the code the correction points to must
    actually still contain the fix, so a future revert of video_zone.py
    would be caught here too, not only by gate_films_teach_all_six_passes
    (which needs a real rendered batch present to run at all).
    """
    plan_path = os.path.join(ROOT, "PLAN-VISUAL-STRATEGY.md")
    if not os.path.exists(plan_path):
        return
    text = io.open(plan_path, encoding="utf-8").read()
    claim_m = re.search(r"[^\n]*fail V1 and V2[^\n]*", text)
    if claim_m and "fixed" not in claim_m.group(0).lower():
        fail("visual-strategy-truncation-current",
             "PLAN-VISUAL-STRATEGY.md's V1/V2 claim no longer carries the "
             "'fixed 2026-09-07' correction: %r" % claim_m.group(0)[:160])

    vz_path = os.path.join(ROOT, "ops", "video_zone.py")
    if not os.path.exists(vz_path):
        return
    vz = io.open(vz_path, encoding="utf-8").read()
    has_sentence_split = "_sentence_chunks" in vz
    six_passes = ("\"sort\", \"straighten\", \"shine\", \"safety\", "
                  "\"standardize\", \"sustain\"") in vz.replace("'", "\"")
    if not (has_sentence_split and six_passes):
        fail("visual-strategy-truncation-current",
             "ops/video_zone.py no longer matches what PLAN-VISUAL-STRATEGY.md "
             "says was fixed (sentence-boundary split present: %s, all six "
             "passes present: %s). Either the fix regressed or the document "
             "needs correcting again." % (has_sentence_split, six_passes))


def gate_goals_organic_search_row_current() -> None:
    """GOALS.md's own "Sessions from organic search" row, and any sibling
    document repeating it, must not contradict GOALS.md's later correction
    in the same file.

    Found 2026-09-09: the row read "1 in 30 days... one visit from Bing,
    none from Google" since the day it was first written, and was never
    touched again. Three lines below it, a "Corrected 2026-09-05" paragraph
    said the opposite as established fact: a Google referral landed on
    4 September, so "not one visit from Google" had already stopped being
    true. Both statements sat in the same file, one table row apart from
    the paragraph that retired it, and nothing checked that the row had
    been told. This is the same one-document-corrected-sibling-never-told
    shape gate_no_stale_session_label and gate_no_stale_affiliate_blocker
    already catch elsewhere in this file, just not for this row.

    Fixed the row to state the same two referrals (Bing 21 August, Google
    4 September) the paragraph already claims. Checking STATUS.md while
    fixing GOALS.md found the identical stale claim ("0 from Google" /
    "ZERO FROM GOOGLE") repeated in two more places, four days after
    GOALS.md's own correction, and nothing had checked STATUS.md against
    this specific correction either. Fixed both and widened this gate to
    STATUS.md too. This gate holds the agreement: it fails if either
    file's Google claim disagrees with GOALS.md's own correction again.

    Found 2026-09-10: RISKS.md's own RISK-0005 and RISK-0013 evidence
    lists both still cited "0 from Google" and the retired 52/144 traffic
    figure, seven days after GOALS.md moved to 60/161 and stated two real
    organic referrals. RISKS.md was never added to this gate's checked
    list, the same one-document-corrected-sibling-never-told shape as the
    STATUS.md fix above, just in a third file. Fixed both entries and
    widened the checked list to RISKS.md.
    """
    goals_path = os.path.join(ROOT, "GOALS.md")
    if not os.path.exists(goals_path):
        return
    goals_text = io.open(goals_path, encoding="utf-8").read()
    row_m = re.search(
        r"\|\s*Sessions from organic search\s*\|[^\n]*\|([^\n]*)\|",
        goals_text)
    if not row_m:
        return
    row_cell = row_m.group(1)
    row_cell_unquoted = re.sub(r'"[^"]*"', "", row_cell)
    row_google = "google" in row_cell_unquoted.lower()
    row_says_none_from_google = bool(
        re.search(r"none from google", row_cell_unquoted, re.IGNORECASE))
    correction_m = re.search(
        r"Corrected 2026-09-05:[^\n]*not one visit from Google[^\n]*",
        goals_text)
    if correction_m and row_says_none_from_google:
        fail("goals-organic-search-row-current",
             "GOALS.md's 'Sessions from organic search' row still says "
             "'none from Google', but the file's own 2026-09-05 correction "
             "three lines below says that stopped being true. Update the "
             "row to match the correction it sits next to.")
    elif correction_m and not row_google:
        fail("goals-organic-search-row-current",
             "GOALS.md's 'Sessions from organic search' row does not "
             "mention Google at all, but the file's own 2026-09-05 "
             "correction says a Google referral landed. Row and "
             "correction must agree.")

    if not correction_m:
        return
    zero_google_re = re.compile(
        r"(?:zero|0)\s+from\s+google", re.IGNORECASE)
    for name in ("STATUS.md", "RISKS.md"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        text = io.open(p, encoding="utf-8").read()
        text_unquoted = re.sub(r'"[^"]*"', "", text)
        if zero_google_re.search(text_unquoted):
            fail("goals-organic-search-row-current",
                 "%s claims zero visits from Google, but GOALS.md's own "
                 "2026-09-05 correction says a Google referral landed. "
                 "Read GOALS.md's current row, don't repeat the retired "
                 "claim." % name)


def gate_nightly_log_ordering() -> None:
    """The most recent calendar date in ops/NIGHTLY-LOG.md must appear
    only as a contiguous block at the top of the file, never again once
    the entry sequence has moved on to an older date.

    Found 2026-09-05, ninth cycle of the day: the cycle read the file's
    own top (cycles one through eight, correctly newest-first, per the
    file's own "newest first" header) but wrote its own entry by
    APPENDING to the end of the file instead of prepending, landing it
    after every 2026-09-04 entry, 15,000+ lines from where a newest-first
    reader would look. Its own title called itself "first today", which
    is the tell for how this happened: STEP 1 of the operating prompt
    says to read "the last four entries", and a session that takes
    "last" to mean the physical end of the file (a natural reading, and
    the one a plain `tail` gives) sees only 2026-09-04 entries, concludes
    today has not started yet, and appends rather than prepends. The
    next eight cycles that day read correctly from the top and prepended
    correctly, so the file ended up with one misplaced entry rather than
    a systemic reversal; without a check, this class of misplacement can
    recur every time the same misreading happens, and each occurrence
    buries a real cycle's findings exactly where "read the last four
    entries" will not find them.

    Deliberately narrower than "every date must be non-increasing
    top to bottom": most of this file predates the "newest first" rule
    and was written oldest-first, append-only, across weeks (many same-
    day entries even read "later", "still later again"). Rewriting that
    historical order would be reformatting a record CLAUDE.md's own
    Decision/Learning Memory sections say to preserve, not fixing a
    defect, and a gate checking strict non-increasing order fires 12
    times on that legacy section alone with nothing to actually fix.
    Checking only "does today's date ever reappear after the entries
    move on to an older date" isolates the one real, current-cycle
    defect (an entry landing after the day has already ended in the
    file) and leaves the legacy chronological section untouched.
    """
    path = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()
    raw_dates = re.findall(r"(?m)^## (\d{4}-\d{2}-\d{2})", text)
    if len(raw_dates) < 2:
        return
    dates = []
    for ds in raw_dates:
        try:
            dates.append(dt.date.fromisoformat(ds))
        except ValueError:
            dates.append(None)
    valid = [d for d in dates if d is not None]
    if not valid:
        return
    newest = max(valid)
    left_newest = False
    for i, d in enumerate(dates):
        if d is None:
            continue
        if d == newest:
            if left_newest:
                fail("nightly-log-ordering",
                     "ops/NIGHTLY-LOG.md entry #%d is dated %s (the "
                     "file's own most recent date) but appears after "
                     "the entry sequence had already moved on to an "
                     "older date; a cycle appended its entry to the "
                     "end of the file instead of prepending it to the "
                     "top. Move it above the other %s entries."
                     % (i + 1, newest.isoformat(), newest.isoformat()))
                return
        else:
            left_newest = True


def gate_send_questions_current() -> None:
    """ops/send_questions.py must not tell Phil something already false.

    Found 2026-09-05: this script drafts the owner-facing "things only you
    can do" email and had not been read since it was written. Two of its four
    BLOCKING items were stale to the point of being wrong. It still asked him
    to complete "Stripe live onboarding" because payment links were "test
    links", months after Stripe went live and took a real sale (verified
    against ROADMAP-2026-2029.md section 2: "$19, net $18.15, on 2026-08-21").
    It still asked him to fill in book front matter, months after this
    operator answered every field itself from facts already on file (commits
    139f92f7, 3e5248c7, 2026-08-27) with nothing left for Phil to decide. A
    third item asked for a Listmonk "list UUID" when the real, later-diagnosed
    blocker is a branding/SMTP identity decision (OWNER-ACTIONS.md item 7,
    issue #15). A DECISIONS entry separately hardcoded "2,600" social units
    long after ops/dashboard.py fixed the identical hardcode in itself and
    said so in its own comment, never propagated here. Sending any of this
    would have told Phil the opposite of true for two of the four "nothing I
    do can move this" claims, the exact class STEP 0.2 exists to prevent.

    Fixed by removing the two resolved items, correcting the Listmonk ask,
    and making the social-unit figure read live from corpus_index.build_index
    instead of a frozen number, mirroring gate_dashboard_social_units_live's
    own fix for the sibling copy. This gate does not re-verify the underlying
    facts each run (Stripe going live is a one-time historical fact, not a
    live signal this sandbox can poll); it only refuses the specific wrong
    phrasings from silently coming back, e.g. by a future edit reverting the
    file or copying the old wording from git history.

    Extended 2026-09-09: the SITE STATUS block hardcoded "10 of 10 checks
    passing, TLS valid" (never measured at send time) and "Deploys are
    automatic: push to main and the host pulls within five minutes," false
    against DEPLOYMENT.md's own canonical description (a Redeploy click, or
    a session holding the deploy key, is still required; no workflow here
    has either). Fixed by deriving that line from
    ops/deploy_freshness.py's live-checked verdict. Guards both the
    "automatic" claim and that the live-derived function is still actually
    called, so a future edit cannot quietly paste the hardcoded line back.
    """
    p = os.path.join(ROOT, "ops", "send_questions.py")
    if not os.path.exists(p):
        return
    src = io.open(p, encoding="utf-8").read()
    bad = []
    if re.search(r"test\s+link|test\s+mode", src, re.IGNORECASE):
        bad.append('claims the payment links are in test mode or are '
                    '"test links", which stopped being true 2026-08-21')
    if re.search(r"front matter.{0,60}bracketed|bracketed.{0,60}front matter",
                 src, re.IGNORECASE | re.DOTALL):
        bad.append("asks Phil for front matter fields already answered "
                   "2026-08-27")
    if re.search(r"\blist UUID\b", src, re.IGNORECASE):
        bad.append("asks for a Listmonk list UUID instead of the real "
                   "branding/SMTP decision (OWNER-ACTIONS.md item 7)")
    if re.search(r"2,?600", src):
        bad.append('hardcodes the retired "2,600" social-unit figure '
                   'instead of reading it live')
    if re.search(r"[Dd]eploys are automatic", src):
        bad.append('claims "deploys are automatic," false against '
                    'DEPLOYMENT.md: a Redeploy click or a session holding '
                    'the deploy key is still required')
    if re.search(r"10 of 10 checks passing", src):
        bad.append('hardcodes "10 of 10 checks passing" instead of a '
                    'live-checked verdict')
    if "deploy_freshness" not in src:
        bad.append("no longer derives site status from "
                   "ops/deploy_freshness.py's live verdict")
    if bad:
        fail("send-questions-current",
             "ops/send_questions.py: " + "; ".join(bad))


def gate_no_frozen_deck_link() -> None:
    """The owner-facing mail tools must not link a deck nothing here can update.

    Found 2026-09-12, cold-reading ops/send_brief.py (never read before):
    it, ops/send_questions.py and ops/status_report.py all pointed "Full
    deck"/"Full detail" at the same claude.ai artifact URL, a frozen
    snapshot this environment cannot republish (this run's own instructions
    say so: the Artifact tool needs an interactive approval no autonomous
    session here can give). Fetched the real page rather than assumed it was
    fine: it read "Generated 2026-09-01 07:46", eleven days stale, still
    claiming $0 revenue, "production is serving an old build" (fixed weeks
    ago), and issues #29/#27/#2/#1 as open that are since closed or
    reclassified. Anyone who clicked that link, including Phil, got a
    dashboard actively worse than not sending one, the exact "reported once
    and never revisited" shape CLAUDE.md 0.4 warns about.

    Fixed by pointing all three at the GitHub blob view of
    EXECUTIVE-DASHBOARD-LIVE.md on main, which ops/dashboard.py regenerates
    and this repository commits on every run (step 11b), so the link is
    never older than the last push. This gate fails if the frozen artifact
    URL ever comes back in any of the three, and separately fails if any of
    them stops linking a deck at all, so this cannot regress silently in
    either direction.
    """
    files = ["send_brief.py", "send_questions.py", "status_report.py"]
    bad = []
    for name in files:
        p = os.path.join(ROOT, "ops", name)
        if not os.path.exists(p):
            continue
        src = io.open(p, encoding="utf-8").read()
        if re.search(r"https://claude\.ai/\S*artifact", src):
            bad.append(f"{name} links a claude.ai artifact, a frozen "
                       "snapshot nothing here can republish")
        if "EXECUTIVE-DASHBOARD-LIVE.md" not in src:
            bad.append(f"{name} no longer links the live, self-updating "
                       "command deck")
    if bad:
        fail("no-frozen-deck-link", "; ".join(bad))


def gate_critical_risks_escalated() -> None:
    """Every CRITICAL, OPEN risk in RISKS.md must be named on a working list.

    Found 2026-09-03: RISKS.md section 23 states its own escalation rule
    plainly ("escalate to the owner when a CRITICAL risk has no mitigation
    in flight"), but RISK-0011 (the ~1.74 to 1.78 GB of product masters
    living only on Phil's Windows machine, no second copy known to exist)
    had sat at CRITICAL/OPEN since the register was written with no mention
    anywhere in OWNER-ACTIONS.md, BACKLOG-2026-H2.md or STATUS.md, the three
    documents an operator or Phil actually works from day to day. The
    register named the risk correctly; nothing carried it to any of the
    lists built for exactly this. Checked directly with grep rather than
    assumed: RISK-0007 (a Phil-free operator task, needs only the VPS
    deploy key this sandbox lacks) had the same gap and got its own new
    BACKLOG-2026-H2.md row (6.55); RISK-0013 was already named in
    BACKLOG-2026-H2.md. This gate does not require every risk to reach
    every document, only that each CRITICAL/OPEN risk's own ID appears on
    at least one of the three, so a real gap cannot silently sit in the
    register alone again.
    """
    risks_path = os.path.join(ROOT, "RISKS.md")
    other_paths = ["OWNER-ACTIONS.md", "BACKLOG-2026-H2.md", "STATUS.md"]
    if not os.path.exists(risks_path):
        return
    risks_text = io.open(risks_path, encoding="utf-8").read()
    combined = ""
    for name in other_paths:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            combined += io.open(p, encoding="utf-8").read()

    rows = re.findall(
        r"\|\s*(RISK-\d+)\s*\|[^|]+\|\s*(CRITICAL)\s*\|\s*(OPEN)\s*\|",
        risks_text)
    if not rows:
        return

    missing = [rid for rid, _, _ in rows if rid not in combined]
    if missing:
        fail("critical-risks-escalated",
             f"{', '.join(missing)} is CRITICAL and OPEN in RISKS.md but "
             f"not named in OWNER-ACTIONS.md, BACKLOG-2026-H2.md or "
             f"STATUS.md; section 23's own escalation rule requires a "
             f"CRITICAL risk with no visible mitigation to reach a working "
             f"list, not just sit in the register.")


def gate_roadmap_photo_asset_caveat() -> None:
    """ROADMAP-2026-2029.md must not describe the 94 shop-floor photographs
    as a usable asset without the consent restriction on them.

    Found 2026-09-04, this operator, reading ROADMAP-2026-2029.md cold as
    STEP 1 of an ordinary cycle rather than trusting it because preflight
    was clean. Section 3c called the photographs "the interesting set...
    documentation of genuine 6S work" and "mostly an import problem," with
    no mention that BACKLOG-2026-H2.md's own 2026-08-26 note (3.3b) found
    one frame with an unobscured human face beside a real company's sticker
    and another showing a second real, identifiable company's bin, no
    consent for public web use from either, filed as a RED band restriction
    under CLAUDE.md. That finding never reached the strategic document
    CLAUDE.md's own STEP 1 tells every cycle to read, which could read this
    as a ready differentiator rather than a permission problem. Fixed by
    adding the caveat in place. This gate fails if the 94-photograph
    sentence ever reappears without "consent" (or the equivalent RED-band
    wording) nearby, the same one-document-corrected-sibling-never-told
    shape gate_no_stale_session_label already catches for a different pair
    of documents.
    """
    p = os.path.join(ROOT, "ROADMAP-2026-2029.md")
    if not os.path.exists(p):
        return
    text = io.open(p, encoding="utf-8").read()
    if "94 photograph" not in text:
        return
    if "consent" not in text.lower():
        fail("roadmap-photo-asset-caveat",
             "ROADMAP-2026-2029.md mentions the 94 shop-floor photographs "
             "without the consent/RED-band restriction BACKLOG-2026-H2.md's "
             "3.3b note establishes; a reader of the roadmap alone would "
             "not know they cannot be published.")


def gate_goals_published_videos_current() -> None:
    """GOALS.md's O1 'Published videos' row must match the last measured count.

    Found 2026-09-02: ops/state-checkin.json recorded youtube_published going
    0 to 1 at 15:02 that day (a real video, published by Phil), but GOALS.md's
    O1 table still read "0 of 228" and its own narrative still said the
    distribution problem "has not been started" and was "blocked on channel
    accounts." All three were stale in a file whose own header says a stale
    number here is a defect in the file, and nothing had checked it. This
    gate parses ops/state-checkin.json's own persisted, measured count
    (never the possibly-null live field, the same carried-forward value
    checkin.py itself trusts) and fails if GOALS.md's row disagrees.
    """
    state_path = os.path.join(ROOT, "ops", "state-checkin.json")
    goals_path = os.path.join(ROOT, "GOALS.md")
    if not os.path.exists(state_path) or not os.path.exists(goals_path):
        return
    try:
        state = json.load(io.open(state_path, encoding="utf-8"))
    except (ValueError, OSError):
        warn("goals-published-videos-current",
             "ops/state-checkin.json could not be parsed; skipped.")
        return
    measured = state.get("youtube_published_last_measured")
    if measured is None:
        return

    goals = io.open(goals_path, encoding="utf-8").read()
    m = re.search(r"Published videos\s*\|\s*\*\*(\d+) of 228", goals)
    if not m:
        warn("goals-published-videos-current",
             "GOALS.md's 'Published videos' row has changed shape or moved; "
             "this gate could not read it and needs updating to match.")
        return
    claimed = int(m.group(1))
    if claimed != measured:
        fail("goals-published-videos-current",
             f"GOALS.md says {claimed} of 228 published videos, but "
             f"ops/state-checkin.json's last real measurement says "
             f"{measured} (as of "
             f"{state.get('youtube_published_measured_at', 'unknown time')})")


def gate_linkedin_drafts_price_current() -> None:
    """The daily LinkedIn draft email must not hand Phil a stale price as fact.

    Found 2026-09-01 while checking ops/linkedin_drafts.py's rotation logic
    per the prior cycle's own lead, the same day gate_roadmap_prices_current
    caught the identical drift one document over: the eBook price changed to
    $9.99 on 2026-08-27, but this file's own "WHAT IS TRUE TODAY, so nothing
    above overstates it" block still hardcoded "the 18 dollar eBook". This is
    the one file whose whole purpose, stated in its own docstring, is that
    every factual claim is read from the live catalogue at generation time,
    and it was emailed to Phil every morning (3.2, automated) telling him
    something false under a header that promises the opposite. Fixed to read
    the price from the live catalogue via a new facts()['ebook_price'] key.
    This calls the file's own pure facts() and ebook_line() rather than
    build(), which really consumes the LinkedIn post rotation (marks posts
    as served) on every call; a gate that runs every hour must not do that
    just to check a price string, or it would silently exhaust the corpus
    faster than any real morning send ever could.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import linkedin_drafts
    except Exception as e:
        warn("linkedin-drafts-price-current",
             "ops/linkedin_drafts.py could not be imported (%s), so its "
             "own price claim was not checked. Unchecked, not correct." % e)
        return

    try:
        f = linkedin_drafts.facts()
    except Exception as e:
        warn("linkedin-drafts-price-current",
             "ops/linkedin_drafts.py.facts() raised (%s), so today's draft's "
             "price claim could not be checked." % e)
        return

    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    ebook = next((p for p in cat if p.get("sku") == "BK-EB"), None)
    if ebook is None:
        warn("linkedin-drafts-price-current",
             "BK-EB is not in the live catalogue, so the eBook price claim "
             "in the daily draft could not be checked.")
        return
    real_price = ebook["price"]

    line = linkedin_drafts.ebook_line(f)
    expected = f"${real_price:g}"
    if expected not in line:
        fail("linkedin-drafts-price-current",
             "the daily LinkedIn draft's own \"WHAT IS TRUE TODAY\" block "
             "does not show the live eBook price (%s): %r. Either it "
             "drifted back to a hardcoded figure or facts() failed to find "
             "BK-EB, and either way Phil would be emailed a wrong price "
             "stated as fact." % (expected, line))


def gate_nav_current() -> None:
    """Every page must mark its own position in the header nav, and no other.

    Two failures live here and they point opposite ways. A page that is a nav
    destination and does not mark itself leaves a screen reader announcing six
    links with nothing to say which one the visitor is standing on. A page that
    is not a destination but carries a mark anyway is worse: it states a
    falsehood. Both are possible from the same cause, because the generators
    copy their header from resources.html and resources.html marks itself, so a
    rebuild without ops/wire_aria_current.py chained left 135 zone and room
    pages each claiming to be the Rooms page. Measured, not supposed.

    This delegates to the wiring pass instead of restating its rules. The
    footer rotted because the code that wrote it and the code that believed it
    was fine were different code.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import wire_aria_current
    except Exception as e:
        warn("nav-current",
             "ops/wire_aria_current.py could not be imported (%s), so no "
             "page's nav position was checked. Unchecked, not correct." % e)
        return

    stale = []
    for f in all_pages():
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        body = io.open(f, encoding="utf-8", errors="replace").read()
        m = wire_aria_current.HEADER.search(body)
        if not m:
            continue
        if wire_aria_current.mark(
                m.group(0), wire_aria_current.page_destination(rel)) != m.group(0):
            stale.append(rel)

    if stale:
        fail("nav-current",
             "%d page(s) do not mark their own nav position correctly, so the "
             "header either says nothing about where the visitor is or says "
             "something untrue: %s. Fix: python ops/wire_aria_current.py"
             % (len(stale), stale[:4]))


def gate_nav_canonical() -> None:
    """Every page's primary nav must offer exactly wire_nav.NAV, in order.

    Found 2026-09-10, reading ops/wire_nav.py cold (a 2-mention file) per
    step 5d. wire_nav.py holds the one canonical list of the five nav items
    the site cut down to from seven, but nothing calls it: not one other
    ops/build_*.py file, not preflight.py, not any CI workflow. Every page's
    nav in fact propagates correctly today only because it is scraped, at
    build time, from an already-committed sibling page (build_zone_pages.py
    reads resources.html; build_resources.py reads about.html; about.html
    itself has no generator and is edited directly), a chain that happens to
    still terminate on the same five items wire_nav.py would produce, not
    because anything ties the two together. One generator does not even
    scrape: ops/build_kitchen_deck_page.py hardcodes its own literal copy of
    the identical five links, a second, independent source of truth for the
    same string. No live drift exists today (checked directly against all
    189 rendered pages, not assumed), but nothing before this gate would have
    caught either a hand edit to about.html, a future generator that
    hardcodes a stale copy the way build_kitchen_deck_page.py already does,
    or wire_nav.py's own NAV list changing without every hardcoded copy
    following it. gate_nav_current (above) only checks the aria-current
    marker on whichever nav is already there; it says nothing about whether
    that nav's actual links and labels are the right five.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import wire_nav
    except Exception as e:                                         # noqa: BLE001
        warn("nav-canonical",
             "ops/wire_nav.py could not be imported (%s), so no page's nav "
             "content was checked. Unchecked, not correct." % e)
        return

    want = [(href, label) for href, label in wire_nav.NAV]
    link_re = re.compile(r'<a href="(?:\.\./)*([^"]+)"[^>]*>([^<]*)</a>')
    bad = []
    checked = 0
    for f in all_pages():
        rel = os.path.relpath(f, SITE).replace(os.sep, "/")
        if rel.startswith("deck/"):
            continue
        body = io.open(f, encoding="utf-8", errors="replace").read()
        m = re.search(r'<nav class="nav"[^>]*>(.*?)</nav>', body, re.S)
        if not m:
            continue
        checked += 1
        got = [(href, label.strip()) for href, label in link_re.findall(m.group(1))]
        if got != want:
            bad.append(rel)

    if checked == 0:
        warn("nav-canonical",
             "no page carried a <nav class=\"nav\"> block, so nothing was "
             "checked. Unchecked, not correct.")
        return
    if bad:
        fail("nav-canonical",
             "%d page(s) carry a primary nav whose links or labels do not "
             "match ops/wire_nav.py's own NAV list exactly, in order: %s. "
             "Fix: python ops/wire_nav.py, and if a generator hardcodes its "
             "own copy (ops/build_kitchen_deck_page.py does), bring that "
             "copy back in line with wire_nav.NAV by hand."
             % (len(bad), ", ".join(bad[:6])))


def gate_resources_page_wired() -> None:
    """resources.html must carry the whole-site wiring, not just its own copy.

    Found this cycle: ops/build_resources.py was the only generator in
    gate_generator_ownership's own chain that never called
    canonical_links.py, wire_landmarks.py, wire_progressive.py or
    wire_aria_current.py on itself, unlike every sibling generator. Running
    it standalone (the way an operator actually reaches for it, after a room
    or zone content edit) verifiably dropped id="main" (the skip link's own
    target, so "Skip to content" pointed at nothing), dropped the
    PROGRESSIVE:BEGIN block entirely (reintroducing the invisible-until-JS
    failure that block exists to prevent), and wrote ".html"-suffixed room
    and zone links against those same pages' own extensionless canonicals.
    gate_generator_ownership's own full-chain run never caught this, because
    later generators in that same chain run these same whole-site passes as
    a side effect and silently repaired resources.html's output after
    build_resources.py ran; nothing repairs it when this file regenerates on
    its own, which is the gap this checks directly against the committed
    page rather than trusting chain order to keep masking it.

    aria-current itself is already covered for every page by
    gate_nav_current; this checks the three properties that gate does not.
    """
    f = os.path.join(SITE, "resources.html")
    if not os.path.exists(f):
        return
    s = io.open(f, encoding="utf-8", errors="replace").read()
    problems = []
    if '<main id="main"' not in s:
        problems.append("no id=\"main\" on <main> (the skip link's own "
                         "target is missing)")
    if "PROGRESSIVE:BEGIN" not in s:
        problems.append("no PROGRESSIVE:BEGIN block (a slow or blocked "
                         "script would leave sections invisible)")
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import canonical_links
        _, (n, _miss) = canonical_links.rewrite(f, s)
        if n:
            problems.append("%d internal link(s) still use the .html form "
                             "these pages' own canonicals disown" % n)
    except Exception as e:
        warn("resources-page-wired",
             "ops/canonical_links.py could not be imported (%s), so the "
             "link form on resources.html was NOT checked." % e)
    if problems:
        fail("resources-page-wired",
             "site/resources.html is missing whole-site wiring it needs: "
             "%s. Fix: python ops/build_resources.py" % "; ".join(problems))


def gate_owner_waiting() -> None:
    """Unread instructions from the owner block the cycle.

    The owner manages by exception. A message from him is the highest priority
    input the system can receive, higher than any metric, because it is the one
    signal that is deliberate. Four of them went unread for five days while
    hundreds of commits landed, which is how a system ends up busy and useless
    at the same time.

    This reads the inbox rather than trusting that somebody looked.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import owner_inbox
        pending = owner_inbox.unread_from_owner()
    except Exception as e:                                      # noqa: BLE001
        warn("owner-waiting",
             "the owner's inbox could not be read (%s), so whether he is "
             "waiting is unknown. Unknown is not nothing." % type(e).__name__)
        return

    if pending is None:
        warn("owner-waiting",
             "no mail credential in this environment, so the owner's inbox "
             "was NOT checked. Unchecked is not empty.")
    elif pending:
        fail("owner-waiting",
             "%d unread message(s) from the owner. These are instructions and "
             "they outrank everything else in this run: %s"
             % (len(pending), [p[:60] for p in pending[:3]]))

    # Third-party mail that may need a decision: affiliate declines, disputes,
    # payouts, domain notices. Deliberately NOT behind an early return above:
    # unread_needing_action() needs four credentials, not the five (including
    # OWNER_EMAIL) unread_from_owner() needs, so a missing OWNER_EMAIL alone
    # must not skip this the way it once silently skipped the equivalent
    # check inside owner_inbox.py's own main() (fixed 038cf603, regression
    # test in test_owner_inbox.py). Returning early here would reintroduce
    # that exact bug one layer up.
    #
    # owner_inbox.unread_needing_action() was written for the incident named
    # above: Impact declined the affiliate application and the decline sat
    # unread for eight days while ops/affiliate-accounts.json said it was
    # still pending our own click (d5bde67c). It has its own test coverage in
    # ops/tests/test_owner_inbox.py and it works. What it never had is a
    # caller: nothing but owner_inbox.py's own bare main() invokes it, and
    # nothing runs that automatically. ops/inbox_agent.py, the tool STEP 8 of
    # the operating runbook actually instructs a cycle to run, has since grown
    # its own separate affiliate/billing classifier and never imports this
    # module at all. So the safety net built specifically to close that
    # incident could only ever fire if someone typed `python ops/owner_inbox.py`
    # by hand, which nothing has instructed anyone to do since inbox_agent.py
    # was written. Found reading this file cold in the epic 6 lane, the same
    # "written but never wired to what runs it" shape as issue #26 and the
    # mobile-corpus gate above. This does not replace inbox_agent.py, which
    # still does the real classifying and drafting; it means preflight itself,
    # which runs every cycle with no --apply step to remember, also notices.
    try:
        third = owner_inbox.unread_needing_action()
    except Exception as e:                                      # noqa: BLE001
        warn("owner-inbox-third-party",
             "third-party mail could not be checked (%s), so whether "
             "anything needs a decision is unknown. Unknown is not nothing."
             % type(e).__name__)
        return
    if third is None:
        return  # no IMAP credential at all; already warned above as owner-waiting
    if third:
        warn("owner-inbox-third-party",
             "%d unread third-party message(s) may need a decision (affiliate, "
             "payment, domain, dispute): %s. A subject line is not the "
             "message; open them." % (len(third), [t[:60] for t in third[:3]]))


def gate_sync_page_links_scans_js() -> None:
    """The dead-link repair tool must not scan HTML only.

    ops/check_live_links.py already learned that a hardcoded buy.stripe.com
    link hiding in a .js file is invisible to a checker reading HTML only:
    data.js alone carries 155 of them and quest.js carries the one offered
    at the end of a finished zone, the highest intent moment on the site.
    ops/sync_page_links.py is the tool that actually rewrites a stale link
    back to a live one, and until this cycle its own file glob was
    "*.html" only, so it would have repaired all 166 pages after a price
    rotation and left every .js file, data.js and quest.js included,
    pointing at the exact dead link it exists to retire. Needs no Stripe
    credential: this checks the file discovery only, not the live rewrite.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import sync_page_links
        files = sync_page_links.discover_files()
    except Exception as e:                                        # noqa: BLE001
        fail("sync-page-links-scope",
             "ops/sync_page_links.py's discover_files() could not run "
             "(%s), so nothing proves it covers .js files." % type(e).__name__)
        return
    js_files = [f for f in files if f.endswith(".js")]
    if not any(f.endswith("data.js") for f in js_files):
        fail("sync-page-links-scope",
             "ops/sync_page_links.py's discover_files() does not scan "
             "site/assets/js/data.js, the single file carrying the most "
             "hardcoded payment links on the site (155). A price rotation "
             "would leave it silently unrepaired.")
    if not any(f.endswith("quest.js") for f in js_files):
        fail("sync-page-links-scope",
             "ops/sync_page_links.py's discover_files() does not scan "
             "site/assets/js/quest.js, which carries the payment link "
             "offered at the end of a finished zone.")


def gate_generator_chains_fingerprint() -> None:
    """Every page generator that either chains build_avif.wire() or writes a
    bare (unfingerprinted) href to a .css/.js asset must also chain
    fingerprint_assets.main(), or a standalone run silently strips the
    ?v= cache-busting hash off whatever it ships.

    wire_measure.main() (chained by every single-page generator, for the
    unrelated reason of restoring the measurement snippet after a rewrite)
    rewrites the measurement script tag as a bare `assets/js/measure.js`,
    dropping whatever ?v= hash was committed there; canonical_links.py and
    wire_pwa.py do the same to other bare asset paths across all 190 site
    pages, not just the ones the generator itself writes. Inside a full
    `preflight.py --own` run this is invisible, because fingerprint_
    assets.py runs again later in that same gens list and repairs it as a
    side effect. Run one generator on its own, which is how an operator
    actually reaches for these files after a content.json edit, and every
    page on the site quietly loses its cache-busting fingerprint until the
    next full run happens to fix it.

    ops/build_corporate.py found this exact trap and chained fingerprint_
    assets.main(False) at the end of its own main() to close it, with a
    comment explaining why ("writing the order down was not enough three
    times running"). Verified live, 2026-09-09: six sibling generators
    (build_articles.py, build_deck_gallery.py, build_resources.py,
    build_standards_page.py, build_zone_index.py, build_zone_pages.py,
    the last of them the 114-zone-page generator, the single biggest
    surface on the site) chained build_avif.wire() without ever chaining
    the fingerprinter, confirmed by actually running each standalone on a
    clean tree and watching every asset reference in its own output lose
    its ?v= hash. All six fixed the same cycle this gate was written.

    Widened 2026-09-10, this operator: ops/build_sample_html.py never calls
    build_avif.wire() at all (it degrades every <img> to text, so it wires
    no pictures), which meant the gate as written could not see it, yet it
    writes two bare stylesheet hrefs (the free 30-chapter sample's own
    fonts.css and book.css) and never chained the fingerprinter either.
    Reproduced directly: ran it standalone and diffed the result against
    the committed, shipped file, the only difference was the missing ?v=
    on both links. This is the site's primary lead magnet. Fixed the same
    way as the six before it, and added a second, direct trigger here so
    the next generator with no build_avif.wire() call cannot slip through
    the same gap a second time: any ops/build_*.py whose source contains a
    literal href to an unversioned .css or .js under assets/ (checked, not
    guessed: this pattern hit exactly the 9 real page generators that write
    such a literal, all 9 already correctly chaining the fingerprinter
    after this fix, zero false positives against the rest of the tier).
    """
    ref = re.compile(r'href=["\'](?:\.\./)*assets/[A-Za-z0-9_./-]+\.(?:css|js)["\']')
    for fname in sorted(os.listdir(os.path.join(ROOT, "ops"))):
        if not (fname.startswith("build_") and fname.endswith(".py")):
            continue
        path = os.path.join(ROOT, "ops", fname)
        try:
            src = io.open(path, encoding="utf-8").read()
        except OSError:
            continue
        trigger = "build_avif.wire()" if "build_avif.wire()" in src \
            else ("a literal unversioned asset href" if ref.search(src) else None)
        if trigger is None:
            continue
        if "fingerprint_assets.main(" not in src:
            fail("generator-chains-fingerprint",
                 "ops/%s has %s but never chains "
                 "fingerprint_assets.main(): a standalone run of this "
                 "generator strips the ?v= cache-busting hash off whatever "
                 "it ships. See ops/build_corporate.py for the "
                 "pattern to copy." % (fname, trigger))


def gate_hero_prompt_budget_checked() -> None:
    """Every local image-hero generator must verify its own prompts fit.

    ops/generate_zone_heroes.py calls ops/image_style.check() on every
    subject before generating, because a prompt over CLIP's 77 token limit
    silently loses its subject and a well formed, on-palette photograph of
    the wrong thing comes back with nothing about it looking wrong. The
    docstring in ops/generate_card_heroes.py names this exact lesson
    ("Same lesson the zone heroes cost a full batch to learn") but the
    file never called check() at all, so the 88 Entryway card prompts,
    several of which run to 30+ words once the tidy/mess state and the
    location clause are added, had zero verification. Both files are
    Desktop/GPU-only and not run by this checker; this reads their source
    directly, so it fires everywhere, not only on a machine that can
    actually generate.
    """
    for name in ("generate_zone_heroes.py", "generate_card_heroes.py"):
        path = os.path.join(ROOT, "ops", name)
        try:
            src = io.open(path, encoding="utf-8").read()
        except OSError as e:
            fail("hero-prompt-budget", "%s could not be read (%s)" %
                 (name, type(e).__name__))
            continue
        if "image_style import check" not in src or "check(subject)" not in src:
            fail("hero-prompt-budget",
                 "%s does not call ops/image_style.check() on its own "
                 "subjects, so an over-budget prompt could reach the "
                 "model with nobody warned." % name)


def gate_zone_hero_rejects_have_subjects() -> None:
    """Every rejected zone hero needs a hand written subject, and
    OWNER-ACTIONS.md's own count of them must match reality.

    Found 2026-09-07, this operator, checking OWNER-ACTIONS.md's "Zone hero
    gaps, measured" row against ops/hero-verdicts.json directly rather than
    trusting the row. It had read 4 since 2026-09-04; the verdicts file
    holds 7 zones marked "no". Two of the seven
    (mudroom--family-hook-zone, nursery--crib-and-sleep-zone) had no entry
    in ops/hero-subjects.json at all, so working the old four-item list
    would have left three zones permanently textless with nothing to flag
    it. Both fixed the same cycle. This gate proves the verdicts file, the
    subjects file and the owner-facing count cannot drift apart again
    unnoticed.
    """
    verdicts_path = os.path.join(ROOT, "ops", "hero-verdicts.json")
    subjects_path = os.path.join(ROOT, "ops", "hero-subjects.json")
    owner_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if not all(os.path.exists(p) for p in (verdicts_path, subjects_path, owner_path)):
        return
    verdicts = json.load(io.open(verdicts_path, encoding="utf-8"))
    rejected = {s for s, r in verdicts.items()
                if isinstance(r, dict) and r.get("verdict") not in (None, "ok")}
    if not rejected:
        return

    subjects = json.load(io.open(subjects_path, encoding="utf-8"))
    missing = sorted(s for s in rejected if s not in subjects)
    if missing:
        fail("zone-hero-rejects-have-subjects",
             "%d rejected zone hero(es) have no hand written subject in "
             "ops/hero-subjects.json, so a regeneration run would silently "
             "leave them textless forever: %s" %
             (len(missing), ", ".join(missing)))

    owner = io.open(owner_path, encoding="utf-8").read()
    m = re.search(r"Zone hero gaps, measured \| (\d+) \|", owner)
    if not m:
        warn("zone-hero-rejects-have-subjects",
             "OWNER-ACTIONS.md's zone hero gaps row has changed shape or "
             "moved; this gate could not read it and needs updating to "
             "match.")
        return
    claimed = int(m.group(1))
    if claimed != len(rejected):
        fail("zone-hero-rejects-have-subjects",
             "OWNER-ACTIONS.md says %d zone hero gaps, but "
             "ops/hero-verdicts.json currently holds %d rejected zones." %
             (claimed, len(rejected)))


def gate_owner_actions_last_measured_current() -> None:
    """OWNER-ACTIONS.md's own "Last measured" header must not predate an
    item it lists.

    Found 2026-09-08, this operator, reading the file cold: the header read
    "Last measured: 2026-09-04" while item 16, added by a different cycle,
    was stamped "Added 2026-09-08, this operator" further down the same
    file. A blocked-task list whose own freshness claim is four days stale
    is the exact CLAUDE.md 0.4 shape ("unchecked is not passing," applied
    here to "uncorrected is not current"): Phil has no way to tell whether
    he has already seen everything on the list without reading all of it
    every time. Fixed by hand this cycle; this gate stops the header
    drifting silently behind the body again.
    """
    path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if not os.path.exists(path):
        return
    text = io.open(path, encoding="utf-8").read()
    m = re.search(r"\*\*Last measured:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if not m:
        warn("owner-actions-last-measured-current",
             "OWNER-ACTIONS.md's \"Last measured\" header has changed shape "
             "or gone missing; this gate could not read it and needs "
             "updating to match.")
        return
    header_date = m.group(1)
    body = text[m.end():]
    body_dates = re.findall(r"\b(202\d-\d{2}-\d{2})\b", body)
    if not body_dates:
        return
    newest = max(body_dates)
    if newest > header_date:
        fail("owner-actions-last-measured-current",
             "OWNER-ACTIONS.md's header says \"Last measured: %s\", but the "
             "file body carries a later date, %s. Update the header in the "
             "same edit that adds or resolves an item." %
             (header_date, newest))


def gate_experiment_owner_actions_surfaced() -> None:
    """Every experiment carrying an owner_action must be named in
    OWNER-ACTIONS.md, not just printed by ops/experiments.py.

    Found 2026-09-09, this operator, reading ops/experiments.py cold and
    running it. EXP-001's owner_action (visit
    https://6s-success.com/?6s-internal=1 once on each of Phil's own devices,
    so a future buy-click can finally be told apart from a stranger's) has
    existed in ops/experiments.json since 2026-09-03, and measure.js's own
    comment confirms it as of 2026-09-08 that not one event in the whole
    database carries the resulting `who` key, meaning the flag has never once
    been set. CLAUDE.md 0.5 is explicit: a blocker that needs the owner gets
    recorded in OWNER-ACTIONS.md so the owner's action is a single step. This
    one sat only in this file's own --offline output and in the JSON, six
    days and counting, because nothing carried it to the one file Phil
    actually reads for "what do I need to do." A correctly reported problem
    nobody is shown costs the same as one nobody found (CLAUDE.md 0.2).

    This does not re-litigate EXP-001 itself, permanently AMBIGUOUS for the
    nine clicks recorded before 2026-09-03 (BACKLOG-2026-H2.md 1.3, closed).
    It only guards that any *future* experiment owner_action gets surfaced
    where the owner will actually see it, by checking the experiment's own id
    appears in OWNER-ACTIONS.md's text.
    """
    reg = os.path.join(ROOT, "ops", "experiments.json")
    doc = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if not os.path.exists(reg) or not os.path.exists(doc):
        return
    data = json.loads(io.open(reg, encoding="utf-8").read())
    owner_text = io.open(doc, encoding="utf-8").read()
    missing = [exp["id"] for exp in data.get("experiments", [])
               if exp.get("owner_action") and exp.get("id") not in owner_text]
    if missing:
        fail("experiment-owner-actions-surfaced",
             "%d experiment(s) carry an owner_action in ops/experiments.json "
             "that OWNER-ACTIONS.md never mentions by id, so Phil has no "
             "single place to see it: %s" % (len(missing), missing))


def gate_image_prompts_tier0_count_honest() -> None:
    """The tier-0 image-prompt file must not tell Phil the wrong count.

    Found 2026-09-07 reading ops/build_image_prompts.py cold. The file used
    to generate a bespoke safety-illustration prompt for every hazard zone,
    so tier 0 was three before/after pairs plus three safety drawings, nine
    images, and main() hardcoded that word into the tier-0 file's own
    heading and opening line. The safety-drawing prompts were removed later
    (five coded hazard icons replaced them, same docstring, "the image
    programme shrank by a third") but the hardcoded "nine images" text in
    main() was never updated. The committed, live
    content/images/prompts/tier-0-prompts.md said "Start here: nine images"
    and "Nine images, one evening" directly above a list of 6 prompts and a
    line reading "6 images." two lines above that: the exact
    copy-vs-control disagreement CLAUDE.md STEP 6 calls a P0 trust defect,
    not a polish item, sitting in the one file Phil actually opens to do
    the work. Fixed by computing the count from len(group) instead of
    repeating a word. This reads the committed file rather than re-running
    the generator, so it catches the same drift again even if a future
    edit reintroduces a hardcoded number.
    """
    path = os.path.join(ROOT, "content", "images", "prompts",
                         "tier-0-prompts.md")
    try:
        text = io.open(path, encoding="utf-8").read()
    except OSError as e:
        warn("image-prompts-tier0-count",
             "%s could not be read (%s), so its own headline count was "
             "not checked." % (path, type(e).__name__))
        return

    m = re.search(r"^(\d+) images\. Style anchor", text, re.MULTILINE)
    if not m:
        fail("image-prompts-tier0-count",
             "tier-0-prompts.md no longer carries its own \"N images. "
             "Style anchor\" line, so its headline count cannot be "
             "checked against anything.")
        return
    real_count = int(m.group(1))

    for pattern, label in (
        (r"^# Start here: (\d+) images$", "its own top heading"),
        (r"whole first batch\.\*\* (\d+) images, one evening",
         "its own opening paragraph"),
    ):
        hm = re.search(pattern, text, re.MULTILINE)
        if not hm:
            fail("image-prompts-tier0-count",
                 "tier-0-prompts.md is missing the expected count text "
                 "(%s), so it may have drifted back to a hardcoded word." %
                 label)
            continue
        stated = int(hm.group(1))
        if stated != real_count:
            fail("image-prompts-tier0-count",
                 "tier-0-prompts.md's %s claims %d images but the file "
                 "actually lists %d. Phil reads this file to do the work; "
                 "a wrong count is a live trust defect, not a typo." %
                 (label, stated, real_count))

    # The fix above corrected the source file, content/images/prompts/
    # tier-0-prompts.md, but not the two operating documents that separately
    # narrate the same count in prose: STATUS.md's P3 action item and
    # BACKLOG-2026-H2.md's owner checklist both still read "the nine tier-0
    # images" days after the real count moved to 6, the same
    # source-corrected-artifact-never-re-derived shape this file's own gate
    # already catches in the prompt file itself, just one hop further away.
    # Found and fixed 2026-09-12, cold-reading STATUS.md's P3 section.
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
        "twelve": 12,
    }
    for doc in ("STATUS.md", "BACKLOG-2026-H2.md"):
        doc_path = os.path.join(ROOT, doc)
        try:
            doc_text = io.open(doc_path, encoding="utf-8").read()
        except OSError:
            continue
        # Strip quoted spans first: a status entry honestly narrating what
        # a prior, now-fixed claim used to say (as this very gate's own fix
        # does, quoting the old "nine tier-0 images" wording) must not read
        # as a live restatement of it, the same quote-aware precedent
        # gate_goals_organic_search_row_current already established.
        doc_text_unquoted = re.sub(r'"[^"]*"', "", doc_text)
        for wm in re.finditer(
                r"\b(%s) tier-0 images?\b" % "|".join(number_words),
                doc_text_unquoted, re.IGNORECASE):
            word = wm.group(1).lower()
            if number_words[word] != real_count:
                fail("image-prompts-tier0-count",
                     "%s says \"%s tier-0 images\" but the real count is "
                     "%d, per tier-0-prompts.md. This is a Phil-facing "
                     "action item; a wrong count sends him looking for "
                     "work that is not there." %
                     (doc, wm.group(1), real_count))


def gate_card_prompts_desktop_only() -> None:
    """The card-prompt writers must refuse when Phil's Desktop is unreachable.

    ops/build_card_prompts.py and ops/build_all_prompts.py both depend on two
    Desktop-only sources: generate_card_art.py's frozen Style Bible, and the
    Desktop images folder that says which cards already have art. Neither
    writer used to notice when both were missing (this environment, always):
    style_prefix() silently falls back to a generic prefix with a different
    hash, and the already-have set silently becomes empty, so a fresh run
    here claimed 0 of 2 real mudroom cards were illustrated and asked to
    redo them. Running python ops/build_all_prompts.py in this exact sandbox
    reproduced it: the committed build/prompts/ALL-PROMPTS.md would have
    gone from '2 illustrated' to '0 illustrated' with a different style
    hash, caught only because the diff was read before committing, not
    because anything caught it. Both writers now call
    require_desktop_sources() before writing and refuse with SystemExit
    instead of guessing.

    Checking that the string 'require_desktop_sources(' merely appears is not
    enough: build_card_prompts.py's own function definition line contains
    that exact substring, so a gate that only checked presence could never
    fail even with the call removed from main(). This checks the actual call
    site in each file's own main(), not the shared definition.
    """
    # Matched WITHOUT the closing paren, deliberately. The first version
    # demanded the exact string 'require_desktop_sources(spec["images"])' and
    # failed the build on 2026-09-04 when the call gained a second argument and
    # wrapped onto two lines. The guard was intact and in fact stronger; the
    # gate was asserting a formatting choice. A gate that fails on a legitimate
    # refactor teaches people to route around it, which costs more than the
    # defect it watches for. Still specific to the call site: the definition
    # line reads "def require_desktop_sources(images_dir: str", so neither of
    # these prefixes can match it.
    checks = {
        "build_card_prompts.py": 'require_desktop_sources(spec["images"]',
        "build_all_prompts.py": 'require_desktop_sources(DECKS[deck]["images"]',
    }
    for name, call in checks.items():
        path = os.path.join(ROOT, "ops", name)
        try:
            src = io.open(path, encoding="utf-8").read()
        except OSError as e:
            fail("card-prompts-desktop-only", "%s could not be read (%s)" %
                 (name, type(e).__name__))
            continue
        if call not in src:
            fail("card-prompts-desktop-only",
                 "%s no longer calls require_desktop_sources() before "
                 "writing, so it could silently write wrong prompts and a "
                 "wrong style hash again when Desktop is unreachable." % name)


def gate_style_src_in_repo() -> None:
    """generate_card_art.STYLE_SRC must resolve inside this repository, and
    to the exact frozen style every existing card was generated against.

    PLAN-MEDIA-2026-09-07.md item A10: STYLE_SRC used to be Desktop-only,
    unreachable from a cloud sandbox, so style_prefix() silently substituted
    a generic prefix with a different hash there. build_card_prompts.py's
    Kitchen deck (desktop_sources=False, meant to run unattended in a cloud
    sandbox once billing is enabled) was actually broken by this: it refused
    every run here with 'the frozen Style Bible is missing', even though the
    2026-08-16 estate mirror (commit 70eb830c) already carries that file's
    text into the repository at content/decks/prompts/. Fixed 2026-09-08 by
    pointing STYLE_SRC there first. This gate keeps it pointed there: a
    revert back to a Desktop-only path would silently reintroduce the same
    live block, and nothing else in this repository would notice, because
    gate_card_prompts_desktop_only only checks that the guard function is
    still CALLED, not what path it resolves.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import importlib
        import generate_card_art as gca
        importlib.reload(gca)
    except Exception as e:                                        # noqa: BLE001
        fail("style-src-in-repo",
             "could not import generate_card_art.py to check STYLE_SRC (%s)"
             % type(e).__name__)
        return

    if not gca.STYLE_SRC.startswith(ROOT + os.sep):
        fail("style-src-in-repo",
             "generate_card_art.STYLE_SRC is %r, outside the repository "
             "again. It must resolve inside content/decks/ so it is "
             "readable in every environment, not only Phil's own machine "
             "(PLAN-MEDIA-2026-09-07.md item A10)." % gca.STYLE_SRC)
        return
    if not os.path.exists(gca.STYLE_SRC):
        fail("style-src-in-repo",
             "generate_card_art.STYLE_SRC (%s) does not exist on this "
             "checkout at all, so every image generated here would fall "
             "back to a different, unflagged style." %
             os.path.relpath(gca.STYLE_SRC, ROOT))
        return

    _, sig = gca.style_prefix()
    recorded = set()
    for idx in glob.glob(os.path.join(ROOT, "build", "prompts", "*", "index.json")):
        try:
            d = json.load(io.open(idx, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        h = d.get("style_hash") if isinstance(d, dict) else None
        if h:
            recorded.add(h)
    if recorded and sig not in recorded:
        fail("style-src-in-repo",
             "generate_card_art.style_prefix() now hashes to %s, but every "
             "already-generated deck's prompt index recorded %s. The "
             "in-repo style source has drifted from the one the existing "
             "90+ approved cards were actually generated against; that is "
             "exactly the silent two-decks-look-different failure this "
             "file's own STYLE_SRC comment warns about." %
             (sig, ", ".join(sorted(recorded))))


def gate_cardtext_corpus_integrity() -> None:
    """The transcribed card corpus must not silently drop a real card.

    ops/merge_cardtext.py merges hand-transcribed card batches keyed by id,
    first occurrence wins. Found 2026-09-02: the "Sports Gear Explosion"
    card (the real EP-010, confirmed by EM-010's own related_path, EP-009's
    own next_card field, and content/decks/reviews/review-card-images-canon.md,
    all naming it EP-010) was transcribed with id "EP-009" in batch-02.json,
    the exact id already used by a real, different card (Mud Trail). The
    merge kept Mud Trail (it came first in the file) and silently dropped
    Sports Gear Explosion's entire transcription, no warning, exit code 0.
    EP-010 is withheld from the live gallery already (issue #29's
    CANON_EXCLUDE), so nothing customer-facing shipped wrong, but any future
    art-regeneration prompt for EP-010 (the same withheld-card work issues
    #1/#2/#29 are blocked on) would have built its prompt from nothing.

    Fixed by correcting the id in ops/cardtext/batch-02.json. This checks
    the corpus can never regress silently: any duplicate id whose two
    entries carry different titles (the dangerous shape: a real distinct
    card hiding behind another's code) fails unless explicitly named in
    merge_cardtext.KNOWN_AMBIGUOUS_DUPES, which is reserved for a genuine,
    documented, unresolved ambiguity (same title, conflicting wording,
    needs a human to read the physical card) rather than a silent escape
    hatch. Also fails if the committed build/entryway-cardtext.json has
    drifted from what the batches actually produce, so a hand edit to the
    output or a stale commit cannot go unnoticed either.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    MC = importlib.import_module("merge_cardtext")
    importlib.reload(MC)
    cards, dupes, unexplained, batches, error = MC.load_batches()
    if error:
        fail("cardtext-corpus-integrity", "could not read the card batches: %s" % error)
        return
    if unexplained:
        fail("cardtext-corpus-integrity",
             "duplicate id(s) with DIFFERENT titles, a real card is "
             "likely hiding behind another's code: %s. Read both entries "
             "in ops/cardtext/batch-*.json, fix the wrong id, or add to "
             "KNOWN_AMBIGUOUS_DUPES only if they are genuinely the same "
             "card transcribed twice." % unexplained)
        return
    committed = {}
    if os.path.exists(MC.OUT):
        try:
            committed = json.load(io.open(MC.OUT, encoding="utf-8"))
        except Exception as e:                                # noqa: BLE001
            fail("cardtext-corpus-integrity",
                 "build/entryway-cardtext.json will not parse: %s" % e)
            return
    fresh = {"deck": "entryway", "count": len(cards),
             "cards": [cards[k] for k in sorted(cards)]}
    if committed != fresh:
        fail("cardtext-corpus-integrity",
             "build/entryway-cardtext.json does not match a fresh rebuild "
             "from ops/cardtext/batch-*.json. Run python "
             "ops/merge_cardtext.py and commit the result.")


def gate_root_cause_vocabulary() -> None:
    """Every root-cause id used anywhere must be in the one frozen list.

    PLAN-MICROZONES-DECKS-APP.md item M1: the deck, the app and the
    articles must never teach two names for one cause. ops/root_causes.py
    is that one list (17 causes, 12 of them copied character-for-character
    from the Kitchen deck's own ROOT CAUSE cards). This scans every
    ops/cardtext/*.json batch for a KC-### or RC-### shaped string that is
    not in the list, which is the actual defect class this exists to catch:
    a new card referencing a cause id that was mistyped, retired, or never
    frozen in the first place.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    RCV = importlib.import_module("root_causes")
    importlib.reload(RCV)
    import glob
    unknown = set()
    checked = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "ops", "cardtext", "*.json"))):
        try:
            data = json.load(io.open(path, encoding="utf-8"))
        except Exception as e:                                  # noqa: BLE001
            fail("root-cause-vocabulary",
                 "%s will not parse: %s" % (os.path.basename(path), e))
            return
        checked += 1
        for cid in RCV.unknown_ids_in(data):
            unknown.add("%s (in %s)" % (cid, os.path.basename(path)))
    if unknown:
        fail("root-cause-vocabulary",
             "cause id(s) not in ops/root_causes.py's frozen list: %s. Add "
             "the cause to the list or fix the typo in the card." %
             "; ".join(sorted(unknown)))


def gate_root_cause_articles_current() -> None:
    """ops/build_zone_pages.py's cause_reading() names, by hand, which of
    root_causes.py's 17 frozen causes currently have no matching article.
    That claim went stale in exactly the shape every other docstring-
    currency gate in this file exists to catch: root_causes.py said EXCESS
    had no article from 2026-09-07, and "more-storage-wont-fix-clutter" (the
    container trap: excess, wrong location, no assigned home, unclear
    ownership) shipped the very next day, 2026-09-08, without anyone telling
    the mapping. Ten real friction branches across the diagnosed pilot zones
    were silently skipping a genuine, on-topic article for 2 days before this
    gate and the fix that made it necessary, 2026-09-10.

    This does not (and cannot) judge whether a new article is a good match
    for an unmapped cause; that is still a human or operator's read, same as
    the original fix. What it protects is narrower and fully mechanical: the
    set of causes cause_reading()'s own docstring names as unmapped must
    exactly match the set root_causes.py's `article` field actually leaves
    None, in both directions, so the two can never again silently drift the
    way they did here.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import importlib
    RCV = importlib.import_module("root_causes")
    importlib.reload(RCV)
    BZP = importlib.import_module("build_zone_pages")
    importlib.reload(BZP)

    real_unmapped = {c["name"] for c in RCV.CAUSES if not c.get("article")}
    doc = re.sub(r"\s+", " ", BZP.cause_reading.__doc__ or "")
    m = re.search(r"frozen causes?\s*\(([^)]*)\)\s+(?:has|have) no article",
                  doc)
    if not m:
        fail("root-cause-articles-current",
             "build_zone_pages.py's cause_reading() docstring no longer "
             "names which causes have no article (expected a sentence like "
             "'... frozen causes (X, Y) have no article yet'); update it to "
             "match root_causes.py's real unmapped set: %s" %
             (", ".join(sorted(real_unmapped)) or "(none)"))
        return
    named = {n.strip() for n in re.split(r",|\band\b", m.group(1))
             if n.strip()}

    missing = real_unmapped - named
    stale = named - real_unmapped
    problems = []
    if missing:
        problems.append(
            "root_causes.py leaves %s unmapped but the docstring does not "
            "name them" % ", ".join(sorted(missing)))
    if stale:
        problems.append(
            "the docstring still claims %s has no article, but "
            "root_causes.py now maps it to a real article" %
            ", ".join(sorted(stale)))

    # A cause can carry a real article slug in root_causes.py, so the check
    # above sees it as mapped, and still be unreachable: cause_reading()
    # resolves every mapped article through build_zone_pages.py's own
    # lookup table, and a slug missing from that table returns None there
    # and gets silently skipped, no error, no warning. Found 2026-09-11:
    # KC-004 (EXCESS MOTION) named why-you-have-to-dig-for-what-you-need
    # since this file was written, correctly seen as mapped by the check
    # above, and still never rendered on either of the two diagnosed pilot
    # zones (Kitchen Upper Cabinet Zone, Kitchen Lower Cabinet and Cookware
    # Zone) whose own frictions carry that exact cause, because the article
    # had been deliberately left out of ZONE_READING (to avoid duplicating
    # "too many steps" on the general 102-zone block) and the lookup table
    # cause_reading() actually reads was built from ZONE_READING alone.
    # This check is the narrower, mechanical half the docstring-comparison
    # above cannot do: it does not judge whether an article is a good
    # match, only whether cause_reading() can actually resolve every
    # article root_causes.py claims exists.
    lookup = getattr(BZP, "_CAUSE_ARTICLE_BY_SLUG", None)
    if lookup is None:
        lookup = BZP._ARTICLE_BY_SLUG
    unreachable = sorted(
        c["name"] for c in RCV.CAUSES
        if c.get("article") and c["article"] not in lookup)
    if unreachable:
        problems.append(
            "root_causes.py maps %s to a real article slug, but "
            "cause_reading()'s own lookup cannot resolve it, so it is "
            "silently skipped on every diagnosed zone page that carries "
            "that cause" % ", ".join(unreachable))

    if problems:
        fail("root-cause-articles-current", "; ".join(problems))


_CUSTOMER_CLAIM = re.compile(
    r"\b(customer|customers|reviewer|reviewers|client|clients|shopper|"
    r"shoppers|buyer|buyers)\b[^.]{0,40}\b(said|says?|told|wrote|reported|"
    r"claim(?:s|ed)?)\b", re.I)


def check_diagnosis_authoring(rooms, kdeck) -> tuple:
    """Pure check, unit-testable without touching the real files.

    Returns (claims, problems): claims are customer/reviewer-attribution
    hits (any room), problems are Kitchen pilot zones whose frictions
    diverge from kitchen-deck.json's real FRICTION CARDs.
    """
    kf_by_zone = {}
    for c in kdeck["cards"]:
        if c.get("type") == "FRICTION CARD":
            kf_by_zone.setdefault(c["zone"], []).append(c)

    problems = []
    claims = []
    for r in rooms:
        for z in r.get("zones", []):
            diag = z.get("diagnosis")
            if not diag:
                continue
            frictions = diag.get("frictions") or []
            for f in frictions:
                texts = [f.get("symptom", "")] + [
                    b.get("answer", "") for b in (f.get("branches") or [])]
                for t in texts:
                    if _CUSTOMER_CLAIM.search(t):
                        claims.append("%s: %r" % (z["zone"], t))
            if r.get("room") != "Kitchen":
                continue
            real = kf_by_zone.get(z["zone"])
            if not real:
                continue
            if len(frictions) != len(real):
                problems.append(
                    "%s: %d frictions authored, kitchen-deck.json has %d "
                    "FRICTION CARDs" % (z["zone"], len(frictions), len(real)))
                continue
            for f, c in zip(frictions, real):
                # "Character-for-character" means copied unmodified from
                # some real string field on the card, not paraphrased. Two
                # concurrent sessions independently authored this corpus
                # against the same real cards and picked different (both
                # legitimate) fields for "symptom": the card's own `title`
                # verbatim, or its `objective` verbatim. Either is a real,
                # unmodified reuse; a symptom matching neither is not.
                if f.get("symptom") not in (c.get("title"), c.get("objective")):
                    problems.append(
                        "%s: symptom does not match %s's title or "
                        "objective character-for-character"
                        % (z["zone"], c["id"]))
                got = [(b.get("answer"), b.get("cause"))
                       for b in (f.get("branches") or [])]
                want = [(b["answer"], b["root_cause"]) for b in c["branches"]]
                if got != want:
                    problems.append(
                        "%s: branches do not match %s character-for-character"
                        % (z["zone"], c["id"]))
    return claims, problems


def gate_diagnosis_authoring() -> None:
    """M3's own acceptance criteria (PLAN-MICROZONES-DECKS-APP.md): the 7
    Kitchen pilot zones' diagnosis.frictions must reuse the 21 real
    FRICTION CARDs in ops/cardtext/kitchen-deck.json character-for-character,
    and no friction sentence anywhere may claim a customer said anything
    (CLAUDE.md section 8: never fabricate a testimonial).

    Proved to fail on a planted mutation of each kind:
    ops/tests/test_diagnosis_authoring.py.
    """
    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    kdeck_path = os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json")
    if not os.path.exists(src_path) or not os.path.exists(kdeck_path):
        warn("diagnosis-authoring",
             "content.json or kitchen-deck.json not found, could not check.")
        return
    rooms = json.load(io.open(src_path, encoding="utf-8"))["rooms"]
    kdeck = json.load(io.open(kdeck_path, encoding="utf-8"))
    claims, problems = check_diagnosis_authoring(rooms, kdeck)

    if claims:
        fail("diagnosis-authoring",
             "friction text claims a customer/reviewer said something "
             "(never fabricate a testimonial, CLAUDE.md section 8): %s" %
             "; ".join(claims[:5]))
    if problems:
        fail("diagnosis-authoring",
             "Kitchen pilot zone(s) diverge from kitchen-deck.json's real "
             "FRICTION CARDs: %s" % "; ".join(problems[:5]))


def gate_diagnosis_schema() -> None:
    """ops/diagnosis.py is a real, working schema check for the `diagnosis`
    block (>= 3 frictions, every branch's `cause` a known root-cause id,
    first_15.action and .victory both present, victory an observable end
    state rather than an imperative instruction) but was never imported or
    called anywhere: not by this file, not by any generator. The Kitchen-
    specific checks in `gate_diagnosis_authoring` above check something
    different (character-for-character reuse of kitchen-deck.json's own
    FRICTION CARDs) and would not catch a malformed diagnosis block authored
    for a non-Kitchen zone, or a `cause` id that is not in root_causes.py at
    all. Same shape as accept_image.py, found and gated 2026-09-08: a real
    checklist tool sitting unwired into any check that runs unattended.

    Proved to fail on a planted regression: ops/tests/test_diagnosis_schema.py.
    """
    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if not os.path.exists(src_path):
        warn("diagnosis-schema", "content.json not found, could not check.")
        return
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import diagnosis as diag_mod
    rooms = json.load(io.open(src_path, encoding="utf-8"))["rooms"]
    problems = diag_mod.check_all(rooms)
    if problems:
        fail("diagnosis-schema", "; ".join(problems[:6]))


def gate_mcp_corpus_current() -> None:
    """mcp/content.json is a committed COPY of content/manual/source/content.json,
    kept only so the MCP server's Docker image stays self contained. Found
    2026-09-09, this operator: it had drifted from the manual for 114 of 114
    zones, missing every `diagnosis` block and still serving the old
    28-word-median Sustain text this week's rewrite replaced with a 94-word
    median (BACKLOG-2026-09-07.md item 1). The live server (deployed 2026-08-31,
    watchtower-updated on push) was answering real MCP queries with content the
    website itself had already superseded.

    Root cause: `.github/workflows/publish-mcp.yml` only triggers on changes
    under `mcp/**`, and its own "keep the corpus in step with the manual" diff
    check only runs inside that same triggered job. A manual edit that never
    touches `mcp/` (every zone-content edit this week) leaves both the trigger
    and the check silently unrun, so the drift accumulates with nothing red
    anywhere. Fixed the trigger to also fire on
    content/manual/source/content.json's own path, but a workflow trigger is
    not visible to a local run, so this gate re-asserts the same invariant here,
    in every environment, on every cycle, independent of what triggered CI.
    """
    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    copy_path = os.path.join(ROOT, "mcp", "content.json")
    if not os.path.exists(src_path) or not os.path.exists(copy_path):
        warn("mcp-corpus", "content.json missing at the manual source or the "
             "mcp/ copy, could not check.")
        return
    src = io.open(src_path, encoding="utf-8").read()
    copy = io.open(copy_path, encoding="utf-8").read()
    if src != copy:
        fail("mcp-corpus",
             "mcp/content.json differs from content/manual/source/content.json "
             "byte for byte. The MCP server ships a self-contained copy; a "
             "drifted one serves stale zones to every AI assistant query while "
             "the site serves current ones. Re-copy the manual's file into mcp/.")


def check_diagnosis_rendered(diagnosed_count, page_bodies, required_hrefs=None) -> list:
    """Pure check, unit-testable without touching the real site/ tree.

    page_bodies is {filename: html} for every site/zones/*.html file.
    Returns a list of problem strings, empty when M4's own acceptance
    criteria (PLAN-MICROZONES-DECKS-APP.md) hold: every zone carrying a
    `diagnosis` in the corpus ships the block on its page, its related
    reading is 3 to 5 links chosen by its own causes, no two diagnosed
    zones ship an identical reading set, no diagnosis-derived FAQ text
    carries a standalone lowercase "i" pronoun, and (found 2026-09-08) a
    zone-specific hand-authored article (ZONE_SPECIFIC_READING in
    ops/build_zone_pages.py) is not silently dropped by the cause-chosen
    swap: it happened to three articles the day M4 shipped, each falling to
    its single articles-index inbound link because cause_reading() replaced
    the whole block rather than adding to it.

    required_hrefs is {filename: [href, ...]} of zone-specific hrefs that
    must appear in that page's related-reading block if the page is
    diagnosed. Optional so existing callers/tests need no change.
    """
    problems = []
    required_hrefs = required_hrefs or {}
    rendered = {f: b for f, b in page_bodies.items() if 'id="diagnosis"' in b}
    if len(rendered) != diagnosed_count:
        problems.append(
            "%d zone(s) carry a diagnosis block in content.json but %d "
            "zone page(s) render one. Run ops/build_zone_pages.py." %
            (diagnosed_count, len(rendered)))
        return problems

    seen = {}
    for f, body in sorted(rendered.items()):
        m = re.search(r'<h2>Related reading</h2><ul>(.*?)</ul>', body, re.S)
        hrefs = tuple(sorted(re.findall(r'href="([^"]+)"', m.group(1)))) \
            if m else ()
        if not (3 <= len(hrefs) <= 5):
            problems.append(
                "%s: %d related-reading link(s), M4 requires 3 to 5" %
                (f, len(hrefs)))
        if hrefs in seen:
            problems.append(
                "%s and %s ship an identical related-reading set" %
                (seen[hrefs], f))
        seen[hrefs] = f

        want = required_hrefs.get(f, [])
        stems = {h.rsplit("/", 1)[-1].removesuffix(".html") for h in hrefs}
        for w in want:
            wstem = w.rsplit("/", 1)[-1].removesuffix(".html")
            if wstem not in stems:
                problems.append(
                    "%s: zone-specific reading link %r missing from its own "
                    "related-reading block (cause_reading() swapped it out "
                    "instead of adding to it)" % (f, wstem))

        # The defect this exists to catch: an earlier draft of
        # diagnosis_faq() in ops/build_zone_pages.py lowercased a whole
        # symptom sentence before embedding it in a question, turning "how
        # often I sort it" into "how often i sort it" in visible page text
        # and in the FAQPage structured data both. Valid JSON, valid
        # schema, wrong English; nothing upstream of the rendered HTML can
        # see it. Scoped to the diagnosis Q&A pairs specifically (not the
        # whole page) so an unrelated, legitimate lowercase "i" elsewhere
        # cannot trip this.
        for dt, dd in re.findall(
                r'<dt>(Why does the .*?do this:.*?)</dt><dd>(.*?)</dd>',
                body, re.S):
            if re.search(r'\bi\b', dt) or re.search(r'\bi\b', dd):
                problems.append(
                    "%s: standalone lowercase 'i' in diagnosis FAQ text: %r"
                    % (f, dt[:90]))
    return problems


def gate_diagnosis_rendered() -> None:
    """M4's own acceptance (PLAN-MICROZONES-DECKS-APP.md): the diagnosed
    zones' pages actually carry what M2/M3 authored, not just that the
    corpus holds it. `gate_diagnosis_authoring` above checks the corpus
    against the deck; this checks the shipped HTML against the corpus, the
    render step neither of the others touches.

    Proved to fail on five planted regressions, one per problem class:
    ops/tests/test_gate_diagnosis_rendered.py.
    """
    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if not os.path.exists(src_path):
        warn("diagnosis-rendered", "content.json not found, could not check.")
        return
    rooms = json.load(io.open(src_path, encoding="utf-8"))["rooms"]
    diagnosed = sum(1 for r in rooms for z in r.get("zones", [])
                     if z.get("diagnosis"))
    if not diagnosed:
        return

    page_bodies = {}
    for f in sorted(glob.glob(os.path.join(SITE, "zones", "*.html"))):
        page_bodies[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    if not page_bodies:
        warn("diagnosis-rendered", "no zone pages built yet, could not check.")
        return

    # ZONE_SPECIFIC_READING is keyed "<room-slug>-<zone-slug>", the same
    # string ops/build_zone_pages.py's own zone-page filenames use, so the
    # key plus ".html" is the page it must appear on.
    required_hrefs = {}
    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import build_zone_pages as bzp
        for key, entries in bzp.ZONE_SPECIFIC_READING.items():
            required_hrefs[key + ".html"] = [e[0] for e in entries]
    except Exception:
        warn("diagnosis-rendered",
             "could not import build_zone_pages.ZONE_SPECIFIC_READING, so "
             "the zone-specific-link check was skipped this run.")

    problems = check_diagnosis_rendered(diagnosed, page_bodies, required_hrefs)
    if problems:
        fail("diagnosis-rendered", "; ".join(problems[:6]))


def check_general_reading_picks(picks, diagnosed_usage, pool,
                                floor=3, cap_ceiling=35) -> list:
    """Pure check, unit-testable without touching the real site/ tree.

    `picks` is {zone_key: [article_slug, ...]} for the 102 zones with no
    `diagnosis` yet, as ops/build_zone_pages.py's general_reading()
    computes it (reduced to slugs). `diagnosed_usage` is a Counter of how
    many of the 12 diagnosed zones already link each article, from that
    same module's `_diagnosed_article_usage()`. `pool` is the set of
    article slugs general_reading() actually chooses among (ZONE_READING);
    the floor and ceiling only apply to those. A handful of other articles
    (ZONE_SPECIFIC_READING: the key article, the mail article, the junk-
    drawer article and similar) are deliberately linked from exactly the
    one zone they were written for, by design, long before M5, and are not
    part of what this gate differentiates.

    Returns problem strings, empty when M5's acceptance criteria
    (PLAN-MICROZONES-DECKS-APP.md) hold: every zone gets 3 to 5 links, no
    two zones share an identical set, and every article in `pool` keeps
    between `floor` and `cap_ceiling` site-wide inbound zone links,
    diagnosed and non-diagnosed usage counted together (the plan's own
    stated ceiling is 30; this gate allows a documented small margin above
    it, because general_reading()'s own de-duplication pass can
    occasionally need one to keep every zone's set unique when the two
    constraints briefly compete, and uniqueness is the harder requirement
    with no stated tolerance).
    """
    problems = []
    seen = {}
    for key, slugs in sorted(picks.items()):
        if not (3 <= len(slugs) <= 5):
            problems.append("%s: %d links, M5 requires 3 to 5"
                             % (key, len(slugs)))
        fs = tuple(sorted(slugs))
        if fs in seen:
            problems.append("%s and %s share an identical related-reading "
                             "set" % (seen[fs], key))
        else:
            seen[fs] = key
    counts = collections.Counter(diagnosed_usage)
    for slugs in picks.values():
        for s in slugs:
            counts[s] += 1
    for s in sorted(pool):
        c = counts.get(s, 0)
        if c < floor:
            problems.append("%s: only %d inbound zone link(s), floor is %d"
                             % (s, c, floor))
        if c > cap_ceiling:
            problems.append("%s: %d inbound zone links, ceiling is %d"
                             % (s, c, cap_ceiling))
    return problems


def check_general_reading_rendered(page_bodies, expected_hrefs) -> list:
    """Pure check: `page_bodies` is {filename: html}, `expected_hrefs` is
    {filename: set(href, ...)} computed the same way
    ops/build_zone_pages.py's zone_page() assembles the block
    (ZONE_SPECIFIC_READING first, general_reading() filling the rest,
    deduplicated and capped at 5). Confirms the shipped HTML actually
    carries what the corpus says it should, the render step neither this
    nor check_general_reading_picks touches on its own; `gate_diagnosis_
    rendered`'s own docstring names the same gap for M4, this is the M5
    half of it.
    """
    def _norm(h):
        # A whole-site wiring pass (ops/canonical_links.py) strips the
        # trailing .html off every internal link after this generator
        # writes the page, so the rendered href and the corpus href name
        # the same article without being the same string.
        return h[:-len(".html")] if h.endswith(".html") else h

    problems = []
    for f, want in sorted(expected_hrefs.items()):
        body = page_bodies.get(f)
        if body is None:
            problems.append("%s: page not built" % f)
            continue
        m = re.search(r'<h2>Related reading</h2><ul>(.*?)</ul>', body, re.S)
        got = ({_norm(h) for h in re.findall(r'href="([^"]+)"', m.group(1))}
               if m else set())
        want = {_norm(h) for h in want}
        if got != want:
            problems.append("%s: rendered %s, corpus computes %s"
                             % (f, sorted(got), sorted(want)))
    return problems


def gate_general_reading_differentiated() -> None:
    """PLAN-MICROZONES-DECKS-APP.md M5: the 102 zones with no `diagnosis`
    yet used to carry the identical 19-link related-reading block, byte
    for byte, on every one of them. ops/build_zone_pages.py's
    general_reading() differentiates it by scoring each zone's own
    already-published text (its passes, its judgement call, its hazards)
    against each article's own grounded keywords, real overlap, nothing
    invented for the purpose.

    This gate re-derives the same picks fresh from content.json and
    checks both halves M4's own gate above checks for diagnosis: that the
    corpus-level result satisfies M5's acceptance criteria
    (check_general_reading_picks) and that the shipped pages actually
    carry it (check_general_reading_rendered). A generator that scores
    correctly is not the same claim as a page that renders the score.

    Proved to fail on planted regressions:
    ops/tests/test_gate_general_reading.py.
    """
    src_path = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if not os.path.exists(src_path):
        warn("general-reading", "content.json not found, could not check.")
        return
    rooms = json.load(io.open(src_path, encoding="utf-8"))["rooms"]
    non_diagnosed = sum(1 for r in rooms for z in r.get("zones", [])
                        if not z.get("diagnosis"))
    if not non_diagnosed:
        return

    try:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import build_zone_pages as bzp
    except Exception as e:                                        # noqa: BLE001
        warn("general-reading",
             "could not import ops/build_zone_pages.py (%s), so M5's "
             "differentiation could not be checked." % e)
        return

    picks_raw = bzp.general_reading(rooms)
    picks = {k: [e[0].rsplit("/", 1)[-1][:-len(".html")] for e in v]
             for k, v in picks_raw.items()}
    diagnosed_usage = bzp._diagnosed_article_usage(rooms)
    pool = set(bzp._ARTICLE_BY_SLUG.keys())
    problems = check_general_reading_picks(picks, diagnosed_usage, pool)
    if problems:
        fail("general-reading", "; ".join(problems[:6]))
        return

    page_bodies = {}
    for f in sorted(glob.glob(os.path.join(SITE, "zones", "*.html"))):
        page_bodies[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    if not page_bodies:
        warn("general-reading", "no zone pages built yet, could not check.")
        return

    expected_hrefs = {}
    for key, links in picks_raw.items():
        specific = bzp.ZONE_SPECIFIC_READING.get(key, [])
        specific_hrefs = {e[0] for e in specific}
        combined = (specific + [e for e in links
                                if e[0] not in specific_hrefs])[:5]
        expected_hrefs[key + ".html"] = {e[0] for e in combined}

    render_problems = check_general_reading_rendered(page_bodies, expected_hrefs)
    if render_problems:
        fail("general-reading", "; ".join(render_problems[:6]))


def gate_zone_short_answer_above_fold() -> None:
    """Backlog A4 ("rebalance the zone page against its own query") asked for
    one measurable thing: the ~100-word answer to "how to organize X" has to
    render before the 471-word supply list, so a reader is not made to scroll
    past a materials list to reach the thing the page's own title promised.

    Found 2026-09-08, reading `BACKLOG-2026-09-07.md` cold rather than
    building anything: A4 was still listed open, but `short_answer()` (added
    by commit ccb8fdbc, the same day the backlog was written, several hours
    later) already renders this as the second content block on every zone
    page, ahead of the supply list. Checked live, not assumed: all 114
    `site/zones/*.html` pages carry `class="answer"` positioned before
    `id="what-you-need"`. A4 was done; nothing here had ever said so, and the
    next cycle to read the backlog cold would have redone finished work or,
    worse, moved the supply list later to "fix" a problem that no longer
    exists, undoing the deliberate placement `zone_page()`'s own comment
    explains (supply list before the six passes, so nobody discovers a
    missing product mid-task).

    This gate exists so a future edit to `zone_page()` cannot silently move
    the answer back below the supply list without a red preflight naming it.
    """
    pages = sorted(glob.glob(os.path.join(SITE, "zones", "*.html")))
    pages = [p for p in pages if os.path.basename(p) != "index.html"]
    if not pages:
        warn("zone-short-answer", "no zone pages built yet, could not check.")
        return
    missing, out_of_order = [], []
    for p in pages:
        name = os.path.basename(p)
        html_ = io.open(p, encoding="utf-8", errors="replace").read()
        a = html_.find('class="answer"')
        s = html_.find('id="what-you-need"')
        if a == -1:
            missing.append(name)
        elif s != -1 and a > s:
            out_of_order.append(name)
    problems = []
    if missing:
        problems.append("%d page(s) with no short answer at all, e.g. %s"
                         % (len(missing), missing[0]))
    if out_of_order:
        problems.append("%d page(s) where the supply list still comes first, "
                         "e.g. %s" % (len(out_of_order), out_of_order[0]))
    if problems:
        fail("zone-short-answer", "; ".join(problems))


def gate_zone_name_consistency() -> None:
    """One real-world zone, three different names, told to three different
    readers: the manual's internal key ("Landing Zone"), the site's own
    display name ("The Landing Spot"), and the SEO title's search phrase
    ("the entryway drop zone"). `build_zone_pages.py`'s own comment on
    `NAME_MAP` explains why the site never ships the internal key: "Shipping
    pages in the manual's vocabulary would put two names for one zone in
    front of the same reader."

    Found 2026-09-12, checking one zone end to end while tracing an unrelated
    lead: `build_youtube_metadata.py` did exactly what that comment warns
    against, because it built its title and description straight from the
    raw internal zone key instead of asking the page for its own name. A
    viewer who watched a video titled "How to organize the landing zone" and
    clicked through landed on a page titled "How to organize the entryway
    drop zone" headed "The Landing Spot": the same defect the site generator
    was written to prevent, reintroduced one file over. Fixed by having
    `title_for()`/`description_for()` call `build_zone_pages.zone_seo_title()`
    and `.display()` instead of reconstructing a name.

    The same read also found a live, shipped instance of the literal words
    colliding: 113 of 114 zone pages' own HowTo JSON-LD said "How to reset
    the The Landing Spot in the Entryway", because `NAME_MAP` already starts
    113 of 114 display names with "The" and `zone_page()` unconditionally
    prepended a second one. Fixed with a one-line conditional article.

    This gate re-checks both defect classes on every run so neither can
    silently return: no live zone page carries the literal double article,
    and, wherever YouTube metadata has been generated, its title and the
    identity line of its description agree with what the real page says.
    """
    import build_zone_pages as bz

    pages = sorted(glob.glob(os.path.join(SITE, "zones", "*.html")))
    pages = [p for p in pages if os.path.basename(p) != "index.html"]
    double_article = []
    for p in pages:
        html_ = io.open(p, encoding="utf-8", errors="replace").read()
        if re.search(r"reset the The\b", html_):
            double_article.append(os.path.basename(p))
    if double_article:
        fail("zone-name-consistency",
             "%d zone page(s) still say 'reset the The...' in their own "
             "HowTo schema, e.g. %s" % (len(double_article), double_article[0]))

    yt_dir = os.path.join(ROOT, "build", "video", "youtube")
    if not os.path.isdir(yt_dir):
        warn("zone-name-consistency",
             "no build/video/youtube/*.json to check; run "
             "build_youtube_metadata.py first.")
        return
    try:
        import video_zone
        zones = video_zone.zones()
    except Exception as e:                                    # noqa: BLE001
        warn("zone-name-consistency", "could not load the real zone corpus "
             "to check against: %s" % e)
        return

    title_mismatch, name_mismatch = [], []
    for room, z in zones:
        zone = z["zone"]
        s = video_zone.zone_slug(room, zone)
        fp = os.path.join(yt_dir, s + ".json")
        if not os.path.isfile(fp):
            continue
        meta = json.load(io.open(fp, encoding="utf-8"))
        want_title = bz.zone_seo_title(room, zone)
        if meta.get("title") != want_title:
            title_mismatch.append(s)
        want_name = bz.display(room, zone)
        if want_name != zone and want_name not in (meta.get("description") or ""):
            name_mismatch.append(s)
    if title_mismatch:
        fail("zone-name-consistency",
             "%d YouTube metadata file(s) have a title that does not match "
             "the real page's own SEO title, e.g. %s"
             % (len(title_mismatch), title_mismatch[0]))
    if name_mismatch:
        fail("zone-name-consistency",
             "%d YouTube metadata file(s) never mention the zone's real "
             "display name in the description, e.g. %s"
             % (len(name_mismatch), name_mismatch[0]))


def gate_ledgerium() -> None:
    """Ledgerium AI bills through this Stripe account. Do not break it.

    A second business's subscription revenue lives in the same account as the
    6S Success catalogue, and nothing else in this repository would notice if
    its prices were archived: they are absent from the catalogue, the
    dashboard and the backlog. The tooling here does archive things, so this
    watches the four prices and the webhook.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import check_ledgerium
        r = check_ledgerium.check()
    except Exception as e:                                      # noqa: BLE001
        warn("ledgerium",
             "Ledgerium billing could not be checked (%s). Unchecked is not "
             "intact." % type(e).__name__)
        return
    if r["state"] == "unchecked":
        warn("ledgerium",
             "Ledgerium billing was NOT checked: %s" % r["problems"][0])
        return
    if r["state"] != "ok":
        fail("ledgerium",
             "Ledgerium AI cannot bill correctly: %s" % "; ".join(r["problems"][:3]))


def gate_kdp_listing_valid() -> None:
    """The committed Amazon KDP listing package must still pass its own rules.

    Found 2026-09-08: two disconnected KDP-prep pipelines existed.
    `build/listings/check_kdp.py` reads the committed, hand-authored
    `build/listings/kdp/{fields.json,description.html,cover-kdp.jpg}`, is
    the one OWNER-ACTIONS.md item 14 actually tells Phil to paste from, and
    every rule in it is cited to a real KDP help page. The older
    `ops/kdp_package.py` (last touched 2026-08-27) generated its own,
    different description from a Python string literal that still used
    `<h2>` four times, a tag `check_kdp.py`'s own ALLOWED_TAGS list (added
    2026-09-03) already knows KDP rejects. Nothing pointed anyone at the
    stale file over the real one except it sitting under `ops/` where a
    "kdp" search finds it first, and three prior cycles called it "clean"
    by rerunning it and diffing against its own earlier output, never
    against the pipeline actually in use. Removed the stale generator
    rather than leave a landmine, and wired the real, already-written check
    in here so a hand edit to any of the three committed KDP files fails a
    cycle instead of waiting for Phil to hit the same wall a second time.
    Needs no credential and no network: local file, EPUB zip and cover
    checks only, so it runs on every pass, not just --deep.
    """
    listings_dir = os.path.join(ROOT, "build", "listings")
    if not os.path.isdir(listings_dir):
        return
    sys.path.insert(0, listings_dir)
    try:
        import check_kdp
        rc = check_kdp.main()
    except Exception as e:                                      # noqa: BLE001
        warn("kdp-listing",
             "could not run build/listings/check_kdp.py (%s: %s). "
             "Unchecked, not passing." % (type(e).__name__, e))
        return
    finally:
        sys.path.remove(listings_dir)
        sys.modules.pop("check_kdp", None)
    if rc != 0:
        fail("kdp-listing",
             "the KDP listing package fails its own check: %s"
             % "; ".join(check_kdp.fail[:3]))


def _epub_word_count(epub_path: str) -> int | None:
    """Recompute the EPUB's word count the same way
    build/listings/verify_epub.py does (strip tags from every spine XHTML
    document, count alpha/apostrophe runs), without importing that file as
    a module, since it runs top-level code and calls sys.exit on import.
    Returns None if the EPUB is missing or unreadable.
    """
    import zipfile
    import posixpath
    from xml.etree import ElementTree as ET
    from urllib.parse import unquote as _unq  # noqa: F401 (parity with verify_epub)

    if not os.path.exists(epub_path):
        return None
    try:
        z = zipfile.ZipFile(epub_path)
        cx = ET.fromstring(z.read("META-INF/container.xml"))
        opf_path = cx.find(
            ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
        ).get("full-path")
        opf = ET.fromstring(z.read(opf_path))
        opfns = "{http://www.idpf.org/2007/opf}"
        base = posixpath.dirname(opf_path)
        words = 0
        for it in opf.find(opfns + "manifest"):
            if it.get("media-type") != "application/xhtml+xml":
                continue
            full = posixpath.normpath(posixpath.join(base, it.get("href")))
            raw = z.read(full).decode("utf-8", "replace")
            words += len(re.findall(r"[A-Za-z']+", re.sub(r"<[^>]+>", " ", raw)))
        return words
    except Exception:                                            # noqa: BLE001
        return None


def gate_kdp_word_count_current() -> None:
    """The book's word count, quoted in MARKETPLACE-LISTINGS.md and
    OWNER-ACTIONS.md as a selling-price justification and an owner-facing
    fact, must still match the committed EPUB, not an old manuscript
    estimate.

    Found 2026-09-10: both documents said "262,000 word", a figure written
    2026-09-03 (`9e7b1cd1`) before later editing. Running
    `build/listings/verify_epub.py` against the current, committed
    `build/6S-Success-Home-Edition.epub` (same tool `gate_kdp_listing_valid`
    already trusts) counts 271,362 words, 3.5% higher. Not material to the
    price math in MARKETPLACE-LISTINGS.md 2.6, which prices delivery cost
    off the file's MB size rather than its word count, but it is exactly
    the "source corrected, artifact never re-derived" defect class this
    repository's own backlog names as its most common, this time in a
    number Phil is told to weigh a pricing decision against. Corrected
    both documents to 271,000 (rounded, matching their own convention) the
    same cycle.

    Recomputes the live count independently rather than trusting either
    document, and fails if a committed word-count claim drifts more than
    5% from the real EPUB, which is loose enough to tolerate normal
    rounding but tight enough to catch a stale figure surviving a real
    edit to the manuscript.

    Found 2026-09-11: the regex only matched singular "word", so
    MARKETPLACE-LISTINGS.md section 1's own "Verified on 2026-09-03" table
    row, "262,633 words excluding inline SVG, across 56 documents", never
    matched at all (`\b` does not break between the "d" of "word" and a
    following "s") and stayed silently stale the whole time this gate has
    existed, 3.2% off the real 271,362 and never caught. Widened to
    `words?` and the stale row corrected the same cycle.
    """
    epub_path = os.path.join(ROOT, "build", "6S-Success-Home-Edition.epub")
    live = _epub_word_count(epub_path)
    if live is None:
        warn("kdp-word-count",
             "could not recompute the EPUB's word count (missing or "
             "unreadable build/6S-Success-Home-Edition.epub). Unchecked, "
             "not passing.")
        return
    for doc in ("MARKETPLACE-LISTINGS.md", "OWNER-ACTIONS.md"):
        path = os.path.join(ROOT, doc)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding="utf-8").read()
        for m in re.finditer(r"([\d,]+)[ ‑-]*words?\b", text):
            claimed = int(m.group(1).replace(",", ""))
            if claimed < 10000:
                continue  # not a book-length claim (e.g. a card/keyword count)
            drift = abs(claimed - live) / live
            if drift > 0.05:
                fail("kdp-word-count",
                     "%s claims the book is %s words but the committed EPUB "
                     "measures %d (%.1f%% off): %r"
                     % (doc, m.group(1), live, drift * 100,
                        text[max(0, m.start() - 40):m.end() + 10]))


def gate_etsy_listing_valid() -> None:
    """The committed Etsy listing package must still pass its own rules.

    Same shape as gate_kdp_listing_valid, and the same gap: `check_etsy.py`
    has existed and passed clean for a while, and nothing ever wired it into
    a cycle that runs unattended, so a future edit to `etsy-listings.json` or
    the rendered PDFs under `build/listings/etsy/` could silently drift from
    what the form actually needs and nobody would see it until Phil hit the
    wall himself opening the Etsy form (`OWNER-ACTIONS.md` item 4).

    Found alongside this gate, 2026-09-09: `build/listings/verify_zone_claims.py`
    read only one hardcoded file per listing, so it never opened L1's second,
    separately delivered file (`6S-Standards-Pack.pdf`) and printed "standards
    sheet ABSENT" for the flagship listing on every run, a false claim about a
    real, correctly bundled file. Fixed there to read the real file list from
    `etsy-listings.json`, the same source this gate and `check_etsy.py` treat
    as authoritative, and to recognise the standalone Standards Pack's own
    "SHEET n OF 20" heading as well as the phrase the other four packs use.
    That script has no PASS/FAIL of its own to gate on (it is a print-and-read
    tool for a human to check against MARKETPLACE-LISTINGS.md), so this gate
    re-derives the one fact that matters mechanically, with its own copy of
    the marker patterns rather than importing verify_zone_claims.py's: every
    listing's file list resolves to a real file that actually contains
    standards content. A gate that instead reached into that script's own
    STANDARDS_MARKERS constant would silently stop checking anything, rather
    than fail, the moment that script's internals changed shape again (proved
    while writing this: pointed it at the pre-fix script, which has no such
    attribute, and it fell into the except clause and only warned).

    Needs no credential and no network: local files and a PDF read only.
    """
    listings_dir = os.path.join(ROOT, "build", "listings")
    if not os.path.isdir(listings_dir):
        return
    sys.path.insert(0, listings_dir)
    try:
        import check_etsy
        rc = check_etsy.main()
    except Exception as e:                                      # noqa: BLE001
        warn("etsy-listing",
             "could not run build/listings/check_etsy.py (%s: %s). "
             "Unchecked, not passing." % (type(e).__name__, e))
        return
    finally:
        sys.path.remove(listings_dir)
        sys.modules.pop("check_etsy", None)
    if rc != 0:
        fail("etsy-listing",
             "the Etsy listing package fails its own check: %s"
             % "; ".join(check_etsy.fail[:3]))
        return

    standards_markers = (re.compile(r"standards that keep", re.I),
                        re.compile(r"\bSHEET \d+ OF \d+\b", re.I))
    try:
        import pymupdf as _pymupdf
        data = json.load(open(os.path.join(listings_dir, "etsy-listings.json"),
                              encoding="utf-8"))
        problems = []
        for item in data["listings"]:
            texts = []
            for fname in item["files"]:
                path = os.path.join(listings_dir, "etsy", item["slug"],
                                     "files", fname)
                if not os.path.exists(path):
                    continue
                doc = _pymupdf.open(path)
                texts.append("\n".join(page.get_text() for page in doc))
                doc.close()
            if not texts:
                problems.append("%s: no deliverable found, run "
                                 "build_etsy_assets.py first" % item["slug"])
                continue
            text = "\n".join(texts)
            if not any(m.search(text) for m in standards_markers):
                problems.append("%s: standards content not found in any "
                                 "delivered file (%s)"
                                 % (item["slug"], ", ".join(item["files"])))
    except Exception as e:                                      # noqa: BLE001
        warn("etsy-listing",
             "could not verify Etsy standards-sheet claims (%s: %s). "
             "Unchecked, not passing." % (type(e).__name__, e))
        return
    if problems:
        fail("etsy-listing",
             "an Etsy listing's own delivered files do not back up its "
             "standards-sheet claim: %s" % "; ".join(problems[:3]))


# Every free, ungated asset llms.txt must name, so an AI crawler reading it
# (ClaudeBot, GPTBot and Googlebot already fetch this site directly; see
# GOALS.md O1) can find what a stranger can already reach with no account and
# no email. The mudroom deck is deliberately absent: BACKLOG-2026-H2.md 2.7
# records Phil's own decision to hold it back from promotion until the
# Entryway deck has produced evidence, and this file being a promotion
# surface, listing it here would undo that decision silently.
LLMS_TXT_MUST_NAME = ["/zones/", "/rooms/", "/articles/", "/quest.html",
                      "/deck.html", "/kitchen-deck.html", "/shop.html",
                      "/feed.xml"]


def gate_data_sources_current() -> None:
    """DATA-SOURCES.md's Section 116 must not claim a source is UNVERIFIED
    once this repository has real, repeated evidence otherwise.

    Found 2026-09-12: the file's own "Current Source State" section and
    Source Registry table had read a blanket UNVERIFIED for every source
    since the file's 2026-08-17 creation, unchanged even as GitHub (used
    every cycle via the API) and Analytics (real traffic figures read
    directly from the production Umami database, GOALS.md O1, three
    separate dated reads) were each verified repeatedly elsewhere in this
    repository. The same "source corrected, artifact never re-derived"
    class this repository's own log names as dominant, here in the one
    document whose purpose is to say which sources can be trusted.
    Corrected the same cycle. This gate does not try to re-derive every
    row (most are qualitative and would need a live credential this
    sandbox rarely holds); it only fails if the exact bootstrap claim for
    the two sources with clear, citable evidence (GitHub, Analytics)
    reappears, so the correction cannot silently regress back to the
    original blanket text.
    """
    f = os.path.join(ROOT, "DATA-SOURCES.md")
    if not os.path.exists(f):
        fail("data-sources-current", "DATA-SOURCES.md does not exist.")
        return
    src = io.open(f, encoding="utf-8", errors="replace").read()
    if re.search(r"\*\*GitHub:\*\*\s*UNVERIFIED", src):
        fail("data-sources-current",
             "DATA-SOURCES.md Section 116 again claims GitHub is "
             "UNVERIFIED. It is read and written every cycle via the "
             "GitHub API; correct the claim rather than reverting it.")
        return
    if re.search(r"\*\*Analytics:\*\*\s*UNVERIFIED", src):
        fail("data-sources-current",
             "DATA-SOURCES.md Section 116 again claims Analytics is "
             "UNVERIFIED. GOALS.md O1 records real traffic figures read "
             "directly from the production Umami database on three "
             "separate dates; correct the claim rather than reverting it.")
        return
    if "not been verified within this file" in src and \
       "Corrected 2026-09-12" not in src:
        fail("data-sources-current",
             "DATA-SOURCES.md Section 116 still reads as the original, "
             "never-updated 2026-08-17 bootstrap text.")


def gate_growth_playbook_linkedin_current() -> None:
    """GROWTH-PLAYBOOK.md must not describe LinkedIn as a blocked,
    one-time batch of drafts once it is a live, running channel.

    Found 2026-09-12, cold-reading a required-doc-list file nobody had
    content-checked since its 2026-08-24 creation: the channel table's
    LinkedIn row still said "posting blocked on Phil... Ten posts
    written and waiting in Phil's inbox for him to publish," describing
    the day the automation launched, not the channel since. It has run
    daily since, `GOALS.md` O1 already credits it with 17 real sessions
    (the largest identifiable source after direct arrivals), and it is
    not "blocked": Phil reads three fresh drafts every morning and sends
    the one that fits, an ongoing rhythm, not a stalled queue. Corrected
    the same cycle. This gate fails if either retired phrase reappears,
    so the correction cannot silently drift back.
    """
    f = os.path.join(ROOT, "GROWTH-PLAYBOOK.md")
    if not os.path.exists(f):
        fail("growth-playbook-linkedin-current", "GROWTH-PLAYBOOK.md does not exist.")
        return
    src = io.open(f, encoding="utf-8", errors="replace").read()
    if "Ten posts written and waiting" in src:
        fail("growth-playbook-linkedin-current",
             "GROWTH-PLAYBOOK.md again claims ten LinkedIn posts are "
             "waiting on a fixed batch. The real mechanism is three "
             "fresh drafts emailed every morning, correct the claim "
             "rather than reverting it.")
        return
    if "posting blocked on Phil" in src:
        fail("growth-playbook-linkedin-current",
             "GROWTH-PLAYBOOK.md again claims LinkedIn posting is "
             "blocked on Phil. GOALS.md O1 records 17 real sessions "
             "from this channel; it is live, not blocked.")


def gate_zone_supplies_docstring_current() -> None:
    """ops/zone_supplies.py's own module docstring must not claim the
    affiliate catalogue is unlinked when it is not.

    Found 2026-09-10, reading a low-mention ops file cold: the docstring
    said "Today every one of its 123 rows carries `Link Status: Unverified`
    and an empty `Affiliate URL`... the state all 123 rows are in right
    now", in the present tense, describing a state that ended 2026-09-04
    when `ops/product_links.py` verified 120 of 123 rows (confirmed live
    against `ops/affiliate-catalogue.csv` this cycle: 120 of 123 rows carry
    `Link Status: Verified search` and a real URL, and `zone_supplies.py`'s
    own `_report()` correctly renders 1,717 links from them). The code was
    never wrong; only the comment describing it was, the same "source
    corrected, artifact never re-derived" defect class named at the top of
    BACKLOG-2026-09-07.md, this time inside a docstring rather than a page.
    Corrected the same cycle. This gate re-derives the real verified count
    from the CSV on every run and fails if the docstring's own cited count
    drifts from it, so the fix cannot silently go stale again the way the
    claim it replaced did.
    """
    f = os.path.join(ROOT, "ops", "zone_supplies.py")
    if not os.path.exists(f):
        fail("zone-supplies-docstring", "ops/zone_supplies.py does not exist.")
        return
    src = io.open(f, encoding="utf-8", errors="replace").read()
    if re.search(r"(?i)all 123 rows are in right now", src) or \
       re.search(r"(?i)every one of its 123\s*\n?rows carries", src):
        fail("zone-supplies-docstring",
             "ops/zone_supplies.py's docstring still claims every "
             "catalogue row is unverified, in the present tense. "
             "ops/affiliate-catalogue.csv shows otherwise; re-read and "
             "correct the docstring rather than trusting its own account.")
        return
    m = re.search(r"As of 2026-09-04, (\d+) of\s*\n?its 123 rows carry a "
                  r"verified", src)
    if not m:
        warn("zone-supplies-docstring",
             "ops/zone_supplies.py's docstring no longer states a verified "
             "row count in the form this gate expects, so it could not be "
             "checked against the real catalogue. Not a failure, but "
             "re-verify by hand.")
        return
    claimed = int(m.group(1))
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import zone_supplies as zs
        cat = zs._catalogue()
    except Exception as e:                                      # noqa: BLE001
        warn("zone-supplies-docstring",
             "could not recompute the real verified-row count to check the "
             "docstring against (%s). Unchecked, not passing." % e)
        return
    real = sum(1 for r in cat.values()
               if (r.get("Link Status") or "").strip().lower()
               .startswith("verified"))
    if claimed != real:
        fail("zone-supplies-docstring",
             "ops/zone_supplies.py's docstring says %d of 123 rows are "
             "verified; ops/affiliate-catalogue.csv actually has %d. "
             "Update the docstring to the real count." % (claimed, real))


def gate_feed_current() -> None:
    """site/feed.xml must match what ops/build_feed.py would write right now.

    Added 2026-09-10. Traffic is the constraint (GOALS.md O1) and every
    unblocked SEO/internal-linking lever this week was already done or
    Phil-gated, so this cycle added a genuinely new, zero-cost distribution
    surface rather than another docstring fix: an Atom feed of the 29
    root-cause articles, needing no account only Phil can create (unlike
    YouTube, Search Console, Instagram, Etsy). Every field in it is read
    back off the article page's own title, description, canonical link and
    JSON-LD dates, so it can only drift the same way sitemap.xml can, a
    generator that exists but does not get rerun after a page changes. This
    mirrors gate_sitemap_complete/gate_downloads_current's own
    regenerate-and-diff pattern rather than inventing a new one.
    """
    f = os.path.join(SITE, "feed.xml")
    if not os.path.exists(f):
        fail("feed-current",
             "site/feed.xml does not exist. Run python ops/build_feed.py.")
        return
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import build_feed as bf
        import importlib
        importlib.reload(bf)
        want = bf.render(bf.entries())
    except Exception as e:                                       # noqa: BLE001
        warn("feed-current",
             "could not regenerate site/feed.xml to check it (%s). "
             "Unchecked, not passing." % e)
        return
    have = io.open(f, encoding="utf-8", errors="replace").read()
    if want != have:
        fail("feed-current",
             "site/feed.xml does not match what ops/build_feed.py would "
             "write right now. Run python ops/build_feed.py.")


def gate_llms_txt_current() -> None:
    """site/llms.txt must still name every free, ungated asset that exists.

    Found 2026-09-09: llms.txt (the file AI answer engines are meant to read
    to learn what a site offers) named /zones/, /rooms/, /articles/,
    /method.html, /quest.html and /shop.html, but not /deck.html (the
    Entryway deck, 88 cards, free to print, live since before this file was
    written) or /kitchen-deck.html (the Kitchen deck, 72 cards, shipped
    2026-09-08). Nothing generates this file and nothing checked it, so a
    major free lead magnet shipping was invisible to it by default rather
    than by any decision. Fixed by hand this cycle; this gate stops the same
    drift recurring the next time a promotable page ships without a matching
    edit here, the same "source corrected, artifact never re-derived" defect
    class named at the top of BACKLOG-2026-09-07.md.

    Widened 2026-09-11: the /articles/ bullet itself carried a stale count,
    "30 explanatory articles", read as still true two days after the file
    was written (2026-09-05, commit 11d42751) when site/articles/ actually
    holds 29 (checked directly: every *.html under site/articles/ except
    index.html, the same set ops/build_feed.py's own docstring cites as "the
    29 root-cause articles"). A stale count in the one file written for an AI
    crawler to cite is the same defect class the missing-decks fix above
    exists for, just a number instead of a missing bullet, so this gate now
    re-derives the real count from disk on every run instead of only
    checking that the word "articles" appears somewhere.
    """
    f = os.path.join(SITE, "llms.txt")
    if not os.path.exists(f):
        fail("llms-txt-current", "site/llms.txt does not exist.")
        return
    s = io.open(f, encoding="utf-8", errors="replace").read()
    missing = [p for p in LLMS_TXT_MUST_NAME if p not in s]
    if missing:
        fail("llms-txt-current",
             "site/llms.txt does not mention %s. An AI crawler reading it "
             "would not know these exist." % ", ".join(missing))
        return

    real = len([p for p in glob.glob(os.path.join(SITE, "articles", "*.html"))
               if os.path.basename(p) != "index.html"])
    m = re.search(r"/articles/\s*:\s*(\d+)\s+explanatory articles", s)
    if not m:
        warn("llms-txt-current",
             "site/llms.txt's /articles/ bullet no longer states a count in "
             "the form this gate expects, so it could not be checked "
             "against the real article count (%d). Not a failure, but "
             "re-verify by hand." % real)
        return
    claimed = int(m.group(1))
    if claimed != real:
        fail("llms-txt-current",
             "site/llms.txt says /articles/ holds %d explanatory articles; "
             "site/articles/ actually has %d *.html files (excluding "
             "index.html). Update the bullet to the real count." %
             (claimed, real))


def gate_breadcrumbs_current() -> None:
    """Every article's BreadcrumbList JSON-LD must match its own visible trail.

    Added 2026-09-10. ops/wire_breadcrumbs.py reads the visible breadcrumb
    nav each article page already renders and writes a matching
    BreadcrumbList, on the stated principle that structured data must never
    describe something a page does not visibly show (CLAUDE.md section 8).
    27 of 29 site/articles/*.html pages carry this today (the two
    ops/build_articles.py writes natively, what-is-6s.html and
    how-long-does-it-take-to-organise-a-room.html, are correctly left
    alone). Nothing regenerates these 27; they are hand-maintained, so
    nothing was silently stripping the markup, but nothing was checking it
    either, on any of GOALS.md O1's SEO/structured-data levers. A future
    hand edit to a page's visible breadcrumb trail, or a new article shipped
    without ever running the tool, would drift or go missing with no gate to
    catch either shape, the exact "source corrected, artifact never
    re-derived" defect class this backlog names as dominant, just not yet
    struck here. Reuses wire_breadcrumbs.trail()/block()/MARKED directly
    rather than re-deriving the trail-reading logic a second time.
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import wire_breadcrumbs as wb
        import importlib
        importlib.reload(wb)
    except Exception as e:                                       # noqa: BLE001
        warn("breadcrumbs-current",
             "could not import ops/wire_breadcrumbs.py to check it (%s). "
             "Unchecked, not passing." % e)
        return
    missing, drifted = [], []
    for f in sorted(glob.glob(os.path.join(SITE, "articles", "*.html"))):
        if f.endswith("index.html"):
            continue
        name = os.path.basename(f)
        s = io.open(f, encoding="utf-8", errors="replace").read()
        if "BreadcrumbList" in s and not wb.MARKED.search(s):
            continue  # native: ops/build_articles.py's own graph() owns this one
        items = wb.trail(f, s)
        if len(items) < 2:
            continue
        want = wb.block(items)
        m = wb.MARKED.search(s)
        if m:
            if m.group(0) != want:
                drifted.append(name)
        else:
            missing.append(name)
    if missing:
        fail("breadcrumbs-current",
             "%d article page(s) render a visible breadcrumb but carry no "
             "BreadcrumbList markup: %s. Run python ops/wire_breadcrumbs.py."
             % (len(missing), ", ".join(missing)))
    if drifted:
        fail("breadcrumbs-current",
             "%d article page(s)' BreadcrumbList JSON-LD no longer matches "
             "their own visible breadcrumb: %s. Run "
             "python ops/wire_breadcrumbs.py." % (len(drifted), ", ".join(drifted)))


def gate_sameas_backed_by_onsite_link() -> None:
    """Every sameAs URL in Organization JSON-LD must be a real link on the site.

    Added 2026-09-10. sameAs is the entity-recognition signal a search or
    answer engine uses to confirm an organisation is who it claims to be, and
    CLAUDE.md section 8 forbids fabricated authority signals. ops/build_seo.py
    left sameAs deliberately empty for months with a comment explaining why:
    "nothing in this repository or on this site references a social
    profile." That had gone stale, found this cycle: the live YouTube channel
    (12 real, narrated, captioned zone videos, confirmed against
    ops/youtube-published.json and ops/state-checkin.json) had no inbound
    link from the site anywhere, so site/method.html's own video section
    still read "none of it has been filmed yet," a live false claim on a
    customer-facing page. Fixed by adding an honest link on method.html and
    only then adding the channel to sameAs. This gate is the two-way lock
    the fix's own comment promises: a sameAs entry with no matching on-site
    href is exactly the fabricated-authority-signal risk section 8 warns
    against, whichever direction it happens (a sameAs added without the
    link, or the link quietly removed while sameAs still claims it).
    """
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    try:
        import build_seo as bs
        import importlib
        importlib.reload(bs)
        claimed = list(bs.ORGANIZATION.get("sameAs") or [])
    except Exception as e:                                         # noqa: BLE001
        warn("sameas-backed-by-onsite-link",
             "could not read ops/build_seo.py's ORGANIZATION dict (%s). "
             "Unchecked, not passing." % e)
        return
    if not claimed:
        return
    hrefs = set()
    for root_dir, _dirs, files in os.walk(SITE):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            p = os.path.join(root_dir, fn)
            try:
                s = io.open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            hrefs.update(re.findall(r'href="([^"]+)"', s))
    unbacked = [u for u in claimed if u not in hrefs]
    if unbacked:
        fail("sameas-backed-by-onsite-link",
             "Organization JSON-LD claims sameAs %s but no page on the site "
             "links to it with a real href. That is a fabricated authority "
             "signal (CLAUDE.md section 8): either add a real, visible "
             "on-site link to it, or remove it from ops/build_seo.py's "
             "ORGANIZATION dict." % ", ".join(unbacked))


def check_decisions_index(text) -> list:
    """Pure logic: return problem strings for DECISIONS.md's own index table.

    Section 43 of DECISIONS.md calls its own table "a compact index as the
    file grows," but nothing ever kept it growing with the file. Found
    2026-09-10, this operator, on the standing "cold-read DECISIONS.md for
    citation staleness" handoff several prior cycles today had each deferred
    as hours-sized: the table (section 43) indexes DEC-0001 through DEC-0037
    only. The eight later, evidence-based decisions appended after it
    (D-001, D-002, D-003, D-014 through D-018, including D-016 "the $9 room
    pack is the entry offer" and D-017 "the service is the product," two of
    the most consequential strategic calls in the file) were never added,
    so a future agent skimming the index for "what did we decide" would
    miss them entirely. This is the same "source shipped, artifact never
    re-derived" defect class BACKLOG-2026-09-07.md names as dominant, here
    in the decision registry rather than a generated page. Fixed by adding
    the eight rows. This function checks both directions: every `## D-NNN`
    / `## DEC-NNNN` heading in the body must have a matching index row, and
    every index row must have a matching body heading, so neither a new
    undocumented decision nor a stale index entry for a deleted one can
    recur unnoticed.
    """
    problems = []
    body_ids = set(re.findall(
        r"^##\s+(D-\d{3}|DEC-\d{4})\b", text, re.MULTILINE))
    index_m = re.search(
        r"# 43\. Decision Index.*?\n((?:\|.*\n)+)", text, re.DOTALL)
    if not index_m:
        problems.append("DECISIONS.md has no section 43 index table to check.")
        return problems
    index_ids = set(re.findall(
        r"^\|\s*(D-\d{3}|DEC-\d{4})\s*\|", index_m.group(1), re.MULTILINE))
    missing_from_index = sorted(body_ids - index_ids)
    stale_in_index = sorted(index_ids - body_ids)
    if missing_from_index:
        problems.append(
            "decided but not indexed: %s" % ", ".join(missing_from_index))
    if stale_in_index:
        problems.append(
            "indexed but no matching decision: %s" % ", ".join(stale_in_index))
    return problems


def gate_decisions_index_current() -> None:
    """DECISIONS.md's own section 43 index must name every decision the
    file actually records, in both directions. See check_decisions_index()
    for the finding this closes.
    """
    p = os.path.join(ROOT, "DECISIONS.md")
    if not os.path.exists(p):
        return
    text = io.open(p, encoding="utf-8", errors="replace").read()
    problems = check_decisions_index(text)
    if problems:
        fail("decisions-index-current",
             "DECISIONS.md section 43's index is out of step with the "
             "decisions actually recorded in the file: %s" %
             "; ".join(problems))


SIX_S_CANON = ["SORT", "STRAIGHTEN", "SHINE", "SAFETY", "STANDARDIZE", "SUSTAIN"]
SIX_S_WORDS = set(SIX_S_CANON)


def check_six_s_terms(text: str) -> list[str]:
    """Find the retired term used as a bare list item, or an out-of-order
    six-item 6S list.

    Two of Phil's own 2026-08-17 architecture docs (AUTONOMY-MEMORY-
    ARCHITECTURE.md, AUTONOMY-ORCHESTRATION.md) carried "SET IN ORDER" as a
    standalone list-item line instead of "STRAIGHTEN", and placed SAFETY last
    instead of fourth, contradicting D-014 (Safety is the fourth S, not an
    afterthought). ops/render_cards.py's corpus had the same "Set in Order"
    defect once already (gate_card_corpus), a different surface each time, so
    this checks every root-level operating document instead of waiting for a
    third surface to find it by hand.

    Only a BARE line reading just "Set in Order" (a list item, once stripped
    of markdown bullet/heading decoration) counts. This project's own style
    and history docs (CONTENT-STANDARDS.md, RISKS.md, STATUS.md, STRIPE.md
    among them) correctly quote or narrate the retired term in running prose
    to document the rule or record a past fix; a naive whole-document
    substring search flags all of those as false positives, which is why this
    checks line shape instead. A standalone six-item list is detected the
    same way: six lines, each naming exactly one of the six canonical words,
    anchored on SORT (every real list opens with it) so two separate,
    correctly-ordered lists sitting near each other cannot look like one list
    rotated out of order.

    A third surface, 6S_SUCCESS_PRODUCT-CATALOG.md, carried the same retired
    term as an underscore-joined enum token, "SET_IN_ORDER", inside a code
    block, with Safety placed sixth again. The plain-string compare above
    only matched a spaced phrase, so this normalizes internal underscores
    and hyphens to spaces before comparing, catching "SET_IN_ORDER" and
    "SET-IN-ORDER" the same way as "Set in Order" without touching any of
    the six canonical words, none of which contain either character.
    """
    problems = []
    for lineno, line in enumerate(text.splitlines(), 1):
        w = line.strip().strip("*_`-# ").upper()
        normalized = re.sub(r"[_-]+", " ", w).strip()
        if normalized == "SET IN ORDER":
            problems.append(
                f'line {lineno} uses the retired term "Set in Order" as a '
                f'bare list item (the second S is "Straighten")')

    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        w = line.strip().strip("*_`-# ").upper()
        if w in SIX_S_WORDS:
            hits.append((lineno, w))
    # Every real list opens on SORT, the first of the six. Anchor there and
    # take the next five hits that follow it (within a tight line span, so
    # a lone word many lines away cannot complete a false set), rather than
    # sliding an unanchored window: two correct, adjacent lists sitting a
    # few lines apart would otherwise look like one list rotated out of
    # order where each individual list is actually fine.
    for i, (lineno, word) in enumerate(hits):
        if word != "SORT":
            continue
        rest = hits[i + 1:i + 6]
        if len(rest) < 5 or rest[-1][0] - lineno > 25:
            continue
        words = [word] + [w for _, w in rest]
        if sorted(words) == sorted(SIX_S_CANON) and words != SIX_S_CANON:
            problems.append(
                f"a six item 6S list at line {lineno} is out of order: "
                f"{words} (should be {SIX_S_CANON}, Safety fourth per "
                f"D-014)")
    return problems


def gate_root_docs_six_s_terms() -> None:
    """Every root-level operating *.md document names the 6S steps correctly.

    See check_six_s_terms() for the finding this closes and why it exists.
    """
    bad = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.md"))):
        text = io.open(p, encoding="utf-8", errors="replace").read()
        for problem in check_six_s_terms(text):
            bad.append(f"{os.path.basename(p)}: {problem}")
    if bad:
        fail("root-docs-six-s-terms",
             f"{len(bad)} document(s) misname the 6S steps: {bad[:5]}")


def main() -> int:
    deep = "--deep" in sys.argv
    print(f"  preflight, {'deep' if deep else 'fast'}\n")

    bootstrap_fresh_sandbox()

    # Runs before every other gate: a stray probe/fixture file left by an
    # earlier killed run must be caught and cleared here, before
    # gate_existing/gate_tests below can misread it as a real page and fail
    # on a symptom of this cause instead of the cause itself.
    run_gate(gate_no_stray_probe_files)
    run_gate(gate_no_tracked_gitignored_dirs)

    run_gate(gate_existing, deep)
    run_gate(gate_third_party)
    run_gate(gate_unsourced_stats)
    run_gate(gate_copy_vs_control)
    run_gate(gate_bundle_maths)
    run_gate(gate_affiliate)
    run_gate(gate_stale_claims)
    run_gate(gate_pack_deck_distinct)
    run_gate(gate_front_matter_filled)
    run_gate(gate_mobile_corpus_current)
    run_gate(gate_mobile_js_tests)
    run_gate(gate_mobile_npm_test_complete)
    run_gate(gate_quest_restore_validates_timestamps)
    run_gate(gate_quest_symptom_entry)
    run_gate(gate_quest_data_heroes_current)
    run_gate(gate_quest_funnel_events)
    run_gate(gate_quest_session_placement)
    run_gate(gate_quest_card_victory_honesty)
    run_gate(gate_mobile_finish_actions_distinct)
    run_gate(gate_mobile_no_bare_jsx_text_expr_break)
    run_gate(gate_mobile_diagnostics_promise_kept)
    run_gate(gate_on_device_check_count)
    run_gate(gate_mobile_badge_contrast)
    run_gate(gate_card_corpus)
    run_gate(gate_card_related_links)
    run_gate(gate_outbound_copy_canon)
    run_gate(gate_card_family_known)
    run_gate(gate_deck_count)
    run_gate(gate_kitchen_deck_rendered)
    run_gate(gate_kitchen_deck_print_tracked)
    run_gate(gate_unique_names)
    run_gate(gate_image_coverage)
    run_gate(gate_tests)
    run_gate(gate_conflict_markers)
    run_gate(gate_no_windows_only_redirect)
    run_gate(gate_browser_detection_portable)
    run_gate(gate_network_calls_have_timeout)
    run_gate(gate_deck_art_withheld)
    run_gate(gate_deploy_fresh)
    run_gate(gate_scheduled_workflow_cadence)
    run_gate(gate_scheduled_delivery_phase)
    run_gate(gate_schedule_comment_minute_current)
    run_gate(gate_stripe_price_claims)
    run_gate(gate_stripe_one_product_per_sku)
    run_gate(gate_live_links)
    run_gate(gate_stripe_brand)
    run_gate(gate_stripe_write_tools_guarded)
    run_gate(gate_sitemap_urls)
    run_gate(gate_no_css_import)
    run_gate(gate_no_stray_dashes)
    run_gate(gate_indexable_pages_have_schema)
    run_gate(gate_checker_scope)
    run_gate(gate_hooks_enabled)
    run_gate(gate_agents_in_sync)
    run_gate(gate_workflows_healthy)
    run_gate(gate_publish_image_current)
    run_gate(gate_workflow_push_permissions)
    run_gate(gate_workflow_no_raw_expr_in_run)
    run_gate(gate_integrations)
    run_gate(gate_footer_consistent)
    run_gate(gate_legal_strip_current)
    run_gate(gate_nightly_log_ordering)
    run_gate(gate_nav_current)
    run_gate(gate_nav_canonical)
    run_gate(gate_resources_page_wired)
    run_gate(gate_owner_waiting)
    run_gate(gate_sync_page_links_scans_js)
    run_gate(gate_generator_chains_fingerprint)
    run_gate(gate_hero_prompt_budget_checked)
    run_gate(gate_zone_hero_rejects_have_subjects)
    run_gate(gate_owner_actions_last_measured_current)
    run_gate(gate_experiment_owner_actions_surfaced)
    run_gate(gate_image_prompts_tier0_count_honest)
    run_gate(gate_card_prompts_desktop_only)
    run_gate(gate_style_src_in_repo)
    run_gate(gate_cardtext_corpus_integrity)
    run_gate(gate_root_cause_vocabulary)
    run_gate(gate_root_cause_articles_current)
    run_gate(gate_diagnosis_authoring)
    run_gate(gate_diagnosis_schema)
    run_gate(gate_mcp_corpus_current)
    run_gate(gate_diagnosis_rendered)
    run_gate(gate_general_reading_differentiated)
    run_gate(gate_zone_short_answer_above_fold)
    run_gate(gate_zone_name_consistency)
    run_gate(gate_ledgerium)
    run_gate(gate_kdp_listing_valid)
    run_gate(gate_kdp_word_count_current)
    run_gate(gate_etsy_listing_valid)
    run_gate(gate_feed_current)
    run_gate(gate_llms_txt_current)
    run_gate(gate_breadcrumbs_current)
    run_gate(gate_sameas_backed_by_onsite_link)
    run_gate(gate_decisions_index_current)
    run_gate(gate_root_docs_six_s_terms)
    run_gate(gate_zone_supplies_docstring_current)
    run_gate(gate_data_sources_current)
    run_gate(gate_growth_playbook_linkedin_current)
    run_gate(gate_mobile_overflow, deep)
    run_gate(gate_visual_audit, deep)
    run_gate(gate_mobile_touch_targets, deep)
    run_gate(gate_dashboard_severity)
    run_gate(gate_dashboard_live_links_carry_forward)
    run_gate(gate_dashboard_deploy_carry_forward)
    run_gate(gate_dashboard_working_tree)
    run_gate(gate_dashboard_shallow_commits)
    run_gate(gate_dashboard_shallow_commits_7d)
    run_gate(gate_dashboard_deck_readiness)
    run_gate(gate_accept_image_derivation)
    run_gate(gate_sitemap_complete)
    run_gate(gate_indexnow_current)
    run_gate(gate_site_verification_declared)
    run_gate(gate_room_images_stable)
    run_gate(gate_zone_heroes_stable)
    run_gate(gate_deck_gallery_identity)
    run_gate(gate_deck_pdf_download_current)
    run_gate(gate_status_report_network_unknown)
    run_gate(gate_status_report_products_consistent)
    run_gate(gate_roadmap_report_issues_unknown)
    run_gate(gate_roadmap_report_backlog_done)
    run_gate(gate_hourly_brief_build_line)
    run_gate(gate_hourly_brief_payment_links)
    run_gate(gate_checkin_youtube_carry_forward)
    run_gate(gate_checkin_undelivered_media_not_fabricated)
    run_gate(gate_roadmap_prices_current)
    run_gate(gate_roadmap_site_age_current)
    run_gate(gate_marketplace_fix_current)
    run_gate(gate_corporate_buy_path_current)
    run_gate(gate_build_id_current)
    run_gate(gate_downloads_current)
    run_gate(gate_product_images_exist)
    run_gate(gate_shop_prerendered)
    run_gate(gate_goals_traffic_current)
    run_gate(gate_goals_revenue_current)
    run_gate(gate_risks_register_current)
    run_gate(gate_risks_evidence_current)
    run_gate(gate_no_stale_session_label)
    run_gate(gate_status_currency)
    run_gate(gate_changelog_current)
    run_gate(gate_no_stale_checkout_count)
    run_gate(gate_no_stale_listmonk_blocker)
    run_gate(gate_no_stale_affiliate_blocker)
    run_gate(gate_architecture_doc_current)
    run_gate(gate_visual_strategy_truncation_current)
    run_gate(gate_goals_organic_search_row_current)
    run_gate(gate_send_questions_current)
    run_gate(gate_no_frozen_deck_link)
    run_gate(gate_critical_risks_escalated)
    run_gate(gate_roadmap_photo_asset_caveat)
    run_gate(gate_goals_published_videos_current)
    run_gate(gate_linkedin_drafts_price_current)
    run_gate(gate_dashboard_social_units_live)
    run_gate(gate_affiliate_trigger)
    run_gate(gate_every_payment_fulfilled)
    run_gate(gate_pages_missing_art)
    run_gate(gate_deck_download_has_art)
    run_gate(gate_caption_line_length)
    run_gate(gate_films_teach_all_six_passes)
    run_gate(gate_films_match_their_captions)
    run_gate(gate_srt_captions_current)
    run_gate(gate_dashboard_zone_videos_live)
    run_gate(gate_dashboard_zone_photo_videos_live)
    run_gate(gate_dashboard_zone_video_16x9_live)
    run_gate(gate_dashboard_social_pins_live)
    run_gate(gate_dashboard_youtube_metadata_live)
    run_gate(gate_dashboard_thumbnails_live)
    run_gate(gate_dashboard_narrated_videos_live)
    run_gate(gate_dashboard_video_carry_forward)
    run_gate(gate_video_slug_single_source)
    run_gate(gate_cover_author_current)
    run_gate(gate_icons_current)
    run_gate(gate_hazard_icons_current)
    run_gate(gate_every_generator_has_a_protection_plan)
    if "--own" in sys.argv:
        run_gate(gate_generator_ownership)

    for g, m in FAIL:
        print(f"  FAIL  {g:22} {m[:150]}")
    for g, m in WARN:
        print(f"  warn  {g:22} {m[:150]}")

    print()
    if FAIL:
        print(f"  {len(FAIL)} gate(s) failed, {len(WARN)} warning(s). "
              f"Nothing should ship on this.")
        return 1
    print(f"  every gate passed" +
          (f", {len(WARN)} warning(s) worth a read" if WARN else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
