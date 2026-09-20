#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_zone_direct_answer() catches the defect
classes REVIEW-DISCOVERY-2026-09-07.md D1 exists to hold: a page still
opening with the old purpose-only lede (the regression this row fixed), a
page whose opening paragraph has been replaced by the kit disclosure text
(so the page opens with a supply list rather than an answer, the exact
shape D1's own acceptance forbids), and an opening paragraph that has grown
past a sane word ceiling.

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit or a regeneration that silently drops D1's
opening paragraph fails this test directly.

Run:  python ops/tests/test_gate_zone_direct_answer_current.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bzp                                 # noqa: E402


def _page(lede_html):
    return ('<div class="head"><h1>The Landing Spot</h1>'
           '<p class="lede">%s</p></div>'
           '<h2>The six passes, in order</h2></main>' % lede_html)


def main() -> int:
    fails = []

    zone = {"purpose": "The spot where pockets empty on the way in and "
                       "refill on the way out.",
            "done_looks_like": "One tray holding keys and sunglasses, "
                               "bare surface on both sides of the tray."}
    want = bzp.direct_answer("Entryway", "drop zone", zone)
    import html as _html
    want_html = _html.escape(want, quote=True)

    # 1. Clean page: rendered lede matches the derived answer exactly. No
    #    problems.
    pages = {"p1.html": _page(want_html)}
    problems = preflight.check_zone_direct_answer({"p1.html": want}, pages)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. Regression: the old purpose-only opening, D1 never applied or
    #    reverted.
    old_only = _html.escape(zone["purpose"], quote=True)
    regressed = {"p1.html": _page(old_only)}
    problems = preflight.check_zone_direct_answer({"p1.html": want}, regressed)
    if not problems:
        fails.append("purpose-only regression (pre-D1 shape) NOT caught")

    # 3. The opening paragraph has been replaced by the kit disclosure
    #    text, the exact "opens with a supply list" shape D1's acceptance
    #    forbids.
    disclosure = {"p1.html": _page(
        "Only if your drop zone has one, a tray and a folder.")}
    problems = preflight.check_zone_direct_answer({"p1.html": want}, disclosure)
    if not problems:
        fails.append("opening paragraph replaced by a disclosure NOT caught")

    # 4. No <p class="lede"> at all (e.g. a template regression dropping
    #    the block entirely).
    no_lede = {"p1.html": "<h1>The Landing Spot</h1><h2>The six passes"
                          "</h2></main>"}
    problems = preflight.check_zone_direct_answer({"p1.html": want}, no_lede)
    if not problems:
        fails.append("missing <p class=\"lede\"> entirely NOT caught")

    # 5. Opening paragraph has grown past the word ceiling.
    bloated_text = "The drop zone, in the Entryway. " + ("word " * 150)
    bloated = {"p1.html": _page(_html.escape(bloated_text, quote=True))}
    problems = preflight.check_zone_direct_answer(
        {"p1.html": bloated_text}, bloated)
    if not problems:
        fails.append("oversized opening paragraph NOT caught")

    # 6. A page in the corpus with no built file at all.
    problems = preflight.check_zone_direct_answer(
        {"p1.html": want, "missing.html": want}, pages)
    if not problems:
        fails.append("zone page missing from the built site NOT caught")

    # 7. Against the real, committed corpus and site/zones/*.html: proves
    #    all 114 zone pages actually ship D1's opening paragraph today.
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    real_map = {}
    for r in rooms:
        for z in r.get("zones", []):
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            thing = bzp.searchable(r["room"], z["zone"], name)
            real_map["%s-%s.html" % (rs, zs)] = bzp.direct_answer(
                r["room"], thing, z)
    if len(real_map) != 114:
        fails.append("expected 114 zone pages in the real corpus, found %d "
                     "(has the corpus changed? update this test's "
                     "expectation deliberately if so)" % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_zone_direct_answer(real_map, real_pages)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: %d cases" % 7)
    return 0


if __name__ == "__main__":
    sys.exit(main())
