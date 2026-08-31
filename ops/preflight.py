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
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PY = sys.executable

FAIL, WARN = [], []


def fail(gate: str, msg: str) -> None:
    FAIL.append((gate, msg))


def warn(gate: str, msg: str) -> None:
    WARN.append((gate, msg))


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
def gate_third_party() -> None:
    """The site promises no third party requests. Keep that true.

    It was false once: standards.html carried two preconnects to Google's font
    hosts while the privacy page promised none. The fonts were self hosted
    already, so the fix was deleting the lines rather than weakening the
    promise. Nothing should quietly put one back.
    """
    allowed = re.compile(r"6s-success\.com|schema\.org|buy\.stripe\.com|"
                         r"localhost|127\.0\.0\.1|example\.com|w3\.org")
    bad = []
    for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True) + \
            glob.glob(os.path.join(SITE, "assets", "**", "*.css"), recursive=True) + \
            glob.glob(os.path.join(SITE, "assets", "**", "*.js"), recursive=True):
        if os.sep + "downloads" + os.sep in f:
            continue          # the book sample is a shipped artefact, not a page
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for host in set(re.findall(r"https?://([a-z0-9.-]+)", s)):
            if not allowed.search(host):
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
    """
    dirty = worktree_changes()
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
    gens = ["build_zone_pages.py", "build_resources.py", "build_product_schema.py",
            "build_articles.py", "build_quest.py", "build_deck_gallery.py",
            "build_sample_html.py", "build_standards_page.py", "build_zone_index.py",
            "fingerprint_assets.py", "build_pwa.py"]
    for g in gens:
        if not os.path.exists(os.path.join(ROOT, "ops", g)):
            continue
        run(g)
    changed = worktree_changes()
    if changed:
        files = changed[:4]
        fail("generator-ownership",
             f"{len(changed)} file(s) differ from what their "
             f"generator produces, so hand edits there will be lost on the "
             f"next build: {files}")
        subprocess.run(["git", "checkout", "--", "."], cwd=ROOT,
                       capture_output=True)


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
        for m in re.finditer(r"\$\s?(\d{1,4}(?:\.\d{2})?)\b", text):
            v = round(float(m.group(1)), 2)
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
    for f in files:
        r = subprocess.run([sys.executable, f], cwd=ROOT, capture_output=True,
                           text=True, timeout=300,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if r.returncode != 0:
            tail = (r.stdout + r.stderr).strip().splitlines()
            bad.append(f"{os.path.basename(f)}: "
                       f"{tail[-1][:90] if tail else 'no output'}")
    if bad:
        fail("tests", f"{len(bad)} of {len(files)} test file(s) failed: {bad[:3]}")
    elif len(files) < 2:
        warn("tests", f"only {len(files)} test file(s) exist")


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
    """
    fronts = glob.glob(os.path.join(ROOT, "build", "cards-rendered",
                                    "*-front.png"))
    if not fronts:
        return          # nothing built here, nothing to contradict
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
    if not any(os.path.exists(c) for c in (
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")):
        warn("mobile-overflow",
             "no Edge on this machine, so no page was rendered. This is "
             "unchecked, not clean.")
        return
    pages = [os.path.join("site", n) for n in
             ("index.html", "book.html", "quest.html", "cart.html",
              "shop.html", "invest.html")]
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


def main() -> int:
    deep = "--deep" in sys.argv
    print(f"  preflight, {'deep' if deep else 'fast'}\n")

    bootstrap_fresh_sandbox()

    gate_existing(deep)
    gate_third_party()
    gate_unsourced_stats()
    gate_copy_vs_control()
    gate_bundle_maths()
    gate_affiliate()
    gate_stale_claims()
    gate_card_corpus()
    gate_deck_count()
    gate_unique_names()
    gate_image_coverage()
    gate_tests()
    gate_conflict_markers()
    gate_deck_art_withheld()
    gate_deploy_fresh()
    gate_live_links()
    gate_sitemap_urls()
    gate_mobile_overflow(deep)
    gate_dashboard_severity()
    gate_dashboard_live_links_carry_forward()
    gate_dashboard_deploy_carry_forward()
    gate_dashboard_working_tree()
    gate_dashboard_shallow_commits()
    gate_sitemap_complete()
    gate_room_images_stable()
    gate_deck_gallery_identity()
    if "--own" in sys.argv:
        gate_generator_ownership()

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
