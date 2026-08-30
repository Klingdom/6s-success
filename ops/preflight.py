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
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))):
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
        warn("generator-ownership",
             "skipped: the working tree has uncommitted changes, so a diff "
             "would not mean anything. Commit first, then run this.")
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
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))):
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
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))
                    + [os.path.join(SITE, "assets", "js", "data.js")]):
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
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))
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
    """A known trademark defect in card art must not be live on the site.

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

    ops/split_deck_cards.py now excludes BRAND_EXCLUDE at the source, but
    that only holds if every regeneration goes through it. This checks the
    output that actually ships, independent of how it was produced, so a
    hand edit, a partial re-run, or a future script that writes this same
    index.json some other way cannot silently put either code back.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "split_deck_cards", os.path.join(ROOT, "ops", "split_deck_cards.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    excluded = mod.BRAND_EXCLUDE
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
                 f"own BRAND_EXCLUDE for a real trademark in the pixels")

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
    gate_tests()
    gate_conflict_markers()
    gate_deck_art_withheld()
    gate_deploy_fresh()
    gate_sitemap_complete()
    gate_room_images_stable()
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
