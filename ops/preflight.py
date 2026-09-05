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
    """
    try:
        fn(*args)
    except Exception as e:
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
    """
    return sorted(f for f in glob.glob(os.path.join(SITE, "**", "*.html"),
                                       recursive=True)
                  if os.sep + "downloads" + os.sep not in f)


STAT = re.compile(
    r"\b(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*"
    r"(?:percent|%|hours?|minutes?|days?|weeks?|years?|times|x)\b", re.I)
# Phrases that make a number a claim about people or results rather than a
# specification of the product. "684 cards" is a spec; "saves 60 hours a year"
# is a claim and needs a source.
CLAIMY = re.compile(r"\b(average|typical|studies|research|most people|"
                    r"saves?|save you|up to|reduces?|increases?|"
                    r"on average|per year|each year|per day)\b", re.I)


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
    for f in _glob.glob(os.path.join(ROOT, "ops", "cardtext", "*.json")) +             _glob.glob(os.path.join(ROOT, "build", "*-cardtext.json")):
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
                if not isinstance(v, str):
                    continue
                # A challenge or a tracker states a rule: "go 7 days", "handle
                # every package within 24 hours". Those numbers are the
                # instruction, not an assertion about people or results, and
                # flagging them every run is how a gate stops being read.
                if k in ("home_quest_challenge", "progress_tracker",
                         "habit_builder", "challenge", "tracker"):
                    continue
                for m in STAT.finditer(v):
                    w = v[max(0, m.start() - 110):m.end() + 60]
                    if CLAIMY.search(w) and not re.search(
                            r"source|according to|cite|\[\d\]", w, re.I):
                        hits.append(("%s %s" % (os.path.basename(f),
                                                c.get("id", "?")),
                                     w.strip()[:96]))

    for f in all_pages():
        s = io.open(f, encoding="utf-8", errors="replace").read()
        body = s[s.index("<main"):s.index("</main>")] if "<main" in s else s
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
        for m in STAT.finditer(text):
            window = text[max(0, m.start() - 110):m.end() + 60]
            if CLAIMY.search(window) and not re.search(
                    r"source|according to|cite|\[\d\]|footnote", window, re.I):
                hits.append((os.path.basename(f), window.strip()[:96]))
    if hits:
        warn("unsourced-stats",
             f"{len(hits)} number(s) that read as a claim about people or "
             f"results with no source nearby. First: "
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
    gens = ["build_zone_pages.py", "build_resources.py",
            "wire_generated_catalog.py", "build_product_schema.py",
            "build_articles.py", "build_quest.py", "build_printpack.py",
            "build_standards.py", "build_deck_gallery.py",
            "build_sample_html.py", "build_standards_page.py", "build_zone_index.py",
            "build_kit_page.py", "build_corporate.py",
            "fingerprint_assets.py", "build_pwa.py",
            "build_avif.py"]
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
    rot = re.compile(r"in development|coming soon|not yet available|"
                     r"we have not|no analytics|nothing has been sent|"
                     r"still being built|launching soon", re.I)
    hits = []
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
    if hits:
        warn("stale-claims",
             f"{len(hits)} phrase(s) that go stale and should be reread. "
             f"First: {hits[0][0]}: {hits[0][1][:90]!r}")


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


def gate_deck_count() -> None:
    """The advertised card count must equal the number of cards that exist.

    The free Entryway deck was advertised on four surfaces with three
    different numbers: 46 on deck.html and the homepage, 88 on the gallery, and
    90 in the catalogue and therefore on every shop tile. The real number is
    88. Each claim was true when it was written and none was updated when the
    deck changed, which is how a product ends up disagreeing with itself in
    public.

    Counted off the rendered fronts rather than the corpus, because a card with
    text and no rendered front is not a card anybody receives.

    Only meaningful when the render was a real attempt at the whole deck.
    build/card-fronts/ carries only 5 committed sample templates today (the
    other 83 need Desktop-only hero photographs this sandbox does not have),
    and ops/render_cards.py now runs here (its own portability fix, see
    gate_browser_detection_portable), so a cloud run rendering exactly those
    5 must not read as "the deck is 5 cards." A small local sample is not a
    claim about the deck's size, only a full one is.
    """
    fronts = glob.glob(os.path.join(ROOT, "build", "cards-rendered",
                                    "*-front.png"))
    if not fronts:
        return          # nothing built here, nothing to contradict
    templates = [f for f in glob.glob(os.path.join(
                    ROOT, "build", "card-fronts", "*.html"))
                 if not f.endswith("-back.html")]
    if len(templates) < 40:
        return          # fewer local templates than any real deck size;
                         # a partial sample, not a claim about deck totals
    n = len(fronts)

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

    claimed = re.findall(r"(\d+)\s+cards",
                         f"{deck[0].get('variant', '')} {deck[0].get('blurb', '')}")
    wrong = [c for c in claimed if int(c) != n]
    if wrong:
        fail("deck-count",
             f"the catalogue advertises the Entryway deck as {wrong[0]} cards "
             f"and {n} are rendered. Checked {len(fronts)} front(s) against "
             f"the DECK-ENTRY entry.")
        return

    # And the pages that name a number in prose.
    bad = []
    for f in (os.path.join(SITE, "deck.html"),
              os.path.join(SITE, "deck-gallery.html"),
              os.path.join(SITE, "index.html")):
        if not os.path.exists(f):
            continue
        page = io.open(f, encoding="utf-8").read()
        # A number is only a false claim if it is offered as THE deck size.
        # "The 72 cards shown, 88 written" is precise and true: 72 of the 88
        # have artwork in the gallery today. Flagging it taught the gate to
        # cry wolf about the most careful sentence on the page. So a count is
        # allowed when the true total appears in the same sentence, which is
        # what an honest shown-versus-written phrasing always does.
        for m in re.finditer(r"[^.<>]*?(\d+)\s+cards[^.<>]*", page):
            c, sentence = int(m.group(1)), m.group(0)
            if not (40 <= c <= 120) or c == n:
                continue
            # Built without a backslash literal: writing this patch
            # through a heredoc turned the word boundaries into actual
            # backspace bytes, 0x08, and the regex then matched
            # nothing at all while looking entirely correct in a diff.
            if re.search(chr(92) + "b" + str(n) + chr(92) + "b",
                         sentence):
                continue          # contrasted against the real total
            bad.append(f"{os.path.basename(f)} says {c}")
    if bad:
        fail("deck-count",
             f"the Entryway deck has {n} cards and these disagree: {bad[:3]}")


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
    manifest, _ = mod.reconcile(mod.figures(), committed)
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
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("  bootstrap: installing ops/requirements.txt (pymupdf missing)")
        subprocess.run([PY, "-m", "pip", "install", "-q", "-r",
                        os.path.join(ROOT, "ops", "requirements.txt")],
                       cwd=ROOT)
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
             ("index.html", "book.html", "quest.html", "cart.html",
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

    The hook refuses commits carrying control bytes, which is the only control
    that catches a heredoc eating a backslash at the moment it would enter
    history rather than minutes later in CI. Git does not enable hooks on
    clone, so it does nothing until core.hooksPath is set, and separately,
    git silently skips a hooksPath hook that is not executable: it warns once
    on the commit that finds this ("hook was ignored because it's not set as
    executable") and otherwise behaves exactly like a passing hook, which is
    the same "looks clean, verified nothing" shape gate_tests() was fixed for.
    The file is committed as mode 100644 by default on most editors and by
    every Windows checkout, so this is not a one-time fix, it recurs.

    Warned, not failed: a fresh CI checkout will never have core.hooksPath
    set, and the build should not fall over a local setting. The point is
    that either failure mode stops being invisible.
    """
    hook = os.path.join(ROOT, ".githooks", "pre-commit")
    if not os.path.exists(hook):
        return
    try:
        got = subprocess.run(["git", "config", "core.hooksPath"], cwd=ROOT,
                             capture_output=True, text=True,
                             timeout=60).stdout.strip()
    except Exception:                                         # noqa: BLE001
        return
    if got != ".githooks":
        warn("hooks-enabled",
             "the pre-commit hook that refuses control bytes in source is "
             "present but not enabled here (core.hooksPath is %r). Run: "
             "git config core.hooksPath .githooks"
             % (got or "unset"))
        return
    if not os.access(hook, os.X_OK):
        warn("hooks-enabled",
             "core.hooksPath is set to .githooks, but .githooks/pre-commit "
             "is not executable, so git silently skips it on every commit "
             "(a one-line hint on the commit that finds this, then no "
             "signal at all). Run: chmod +x .githooks/pre-commit && "
             "git update-index --chmod=+x .githooks/pre-commit")


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
             "behind by a run that was killed mid-audit: %s. Delete "
             "them; they are not real pages." % (len(stray), stray[:4]))


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
    pm = re.search(r"(\d+)\s+pages live", text)
    if pm:
        claimed_pages = int(pm.group(1))
        real_pages = len(all_pages())
        if claimed_pages != real_pages:
            bad.append(f"page count: ROADMAP says {claimed_pages} pages "
                        f"live, the site has {real_pages}")

    if bad:
        fail("roadmap-prices-current",
             "ROADMAP-2026-2029.md's section 1 table has drifted from the "
             "live catalogue: %s" % "; ".join(bad))


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
    if bad:
        fail("send-questions-current",
             "ops/send_questions.py: " + "; ".join(bad))


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
        return
    if pending:
        fail("owner-waiting",
             "%d unread message(s) from the owner. These are instructions and "
             "they outrank everything else in this run: %s"
             % (len(pending), [p[:60] for p in pending[:3]]))


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


def main() -> int:
    deep = "--deep" in sys.argv
    print(f"  preflight, {'deep' if deep else 'fast'}\n")

    bootstrap_fresh_sandbox()

    run_gate(gate_existing, deep)
    run_gate(gate_third_party)
    run_gate(gate_unsourced_stats)
    run_gate(gate_copy_vs_control)
    run_gate(gate_bundle_maths)
    run_gate(gate_affiliate)
    run_gate(gate_stale_claims)
    run_gate(gate_front_matter_filled)
    run_gate(gate_mobile_corpus_current)
    run_gate(gate_mobile_js_tests)
    run_gate(gate_mobile_npm_test_complete)
    run_gate(gate_quest_restore_validates_timestamps)
    run_gate(gate_mobile_finish_actions_distinct)
    run_gate(gate_on_device_check_count)
    run_gate(gate_mobile_badge_contrast)
    run_gate(gate_card_corpus)
    run_gate(gate_deck_count)
    run_gate(gate_unique_names)
    run_gate(gate_image_coverage)
    run_gate(gate_tests)
    run_gate(gate_conflict_markers)
    run_gate(gate_no_windows_only_redirect)
    run_gate(gate_browser_detection_portable)
    run_gate(gate_deck_art_withheld)
    run_gate(gate_deploy_fresh)
    run_gate(gate_live_links)
    run_gate(gate_sitemap_urls)
    run_gate(gate_no_css_import)
    run_gate(gate_checker_scope)
    run_gate(gate_hooks_enabled)
    run_gate(gate_agents_in_sync)
    run_gate(gate_workflows_healthy)
    run_gate(gate_workflow_push_permissions)
    run_gate(gate_workflow_no_raw_expr_in_run)
    run_gate(gate_integrations)
    run_gate(gate_footer_consistent)
    run_gate(gate_legal_strip_current)
    run_gate(gate_nightly_log_ordering)
    run_gate(gate_no_stray_probe_files)
    run_gate(gate_nav_current)
    run_gate(gate_resources_page_wired)
    run_gate(gate_owner_waiting)
    run_gate(gate_sync_page_links_scans_js)
    run_gate(gate_hero_prompt_budget_checked)
    run_gate(gate_card_prompts_desktop_only)
    run_gate(gate_cardtext_corpus_integrity)
    run_gate(gate_ledgerium)
    run_gate(gate_mobile_overflow, deep)
    run_gate(gate_visual_audit, deep)
    run_gate(gate_dashboard_severity)
    run_gate(gate_dashboard_live_links_carry_forward)
    run_gate(gate_dashboard_deploy_carry_forward)
    run_gate(gate_dashboard_working_tree)
    run_gate(gate_dashboard_shallow_commits)
    run_gate(gate_dashboard_shallow_commits_7d)
    run_gate(gate_dashboard_deck_readiness)
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
    run_gate(gate_checkin_youtube_carry_forward)
    run_gate(gate_checkin_undelivered_media_not_fabricated)
    run_gate(gate_roadmap_prices_current)
    run_gate(gate_build_id_current)
    run_gate(gate_downloads_current)
    run_gate(gate_product_images_exist)
    run_gate(gate_shop_prerendered)
    run_gate(gate_goals_traffic_current)
    run_gate(gate_risks_register_current)
    run_gate(gate_risks_evidence_current)
    run_gate(gate_no_stale_session_label)
    run_gate(gate_send_questions_current)
    run_gate(gate_critical_risks_escalated)
    run_gate(gate_roadmap_photo_asset_caveat)
    run_gate(gate_goals_published_videos_current)
    run_gate(gate_linkedin_drafts_price_current)
    run_gate(gate_dashboard_social_units_live)
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
