#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_common_items_rendered() catches the defect
classes this field's own gate guards against: a page carrying the
common-items block the corpus never authorised, a zone whose page never
got regenerated after a content.json edit (missing block), and a rendered
list that drifted from what the corpus actually says (stale or
paraphrased).

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit that is never regenerated, or a regeneration that
silently drops the block, fails this test directly rather than waiting for
someone to notice on the live page.

Run:  python ops/tests/test_gate_common_items_rendered.py
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


def _block(items):
    rows = "".join("<li>%s</li>" % bzp.esc(i) for i in items)
    return "<h2>Common items here</h2><ul class=\"common-items\">%s</ul>" % rows


GOOD_ITEMS = ["Keys", "Sunglasses", "A folder for act-on paper"]


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    items_map = {}
    for r in rooms:
        for z in r.get("zones", []):
            items = z.get("common_items")
            if not items:
                continue
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            items_map["%s-%s.html" % (rs, zs)] = list(items)
    return items_map


def main() -> int:
    fails = []

    # 1. Clean synthetic page: no problems.
    pages = {"z1.html": _block(GOOD_ITEMS)}
    imap = {"z1.html": GOOD_ITEMS}
    problems = preflight.check_common_items_rendered(imap, pages)
    if problems:
        fails.append("clean synthetic page wrongly flagged: %s" % problems)

    # 2. A page renders the block but the corpus never authorised it.
    problems = preflight.check_common_items_rendered({}, pages)
    if not problems:
        fails.append("un-authorised common-items block NOT caught")

    # 3. A zone has common_items in the corpus but its page carries none
    #    (never regenerated).
    problems = preflight.check_common_items_rendered(imap, {"z1.html": "<p>stale</p>"})
    if not problems:
        fails.append("missing common-items block on an authored zone NOT caught")

    # 4. Stale/paraphrased item: the page's text no longer matches the
    #    corpus's own words.
    stale_items = ["Stale Keys", "Sunglasses", "A folder for act-on paper"]
    stale_pages = {"z1.html": _block(stale_items)}
    problems = preflight.check_common_items_rendered(imap, stale_pages)
    if not problems:
        fails.append("paraphrased/stale item NOT caught")

    # 5. Corpus names an empty list for a zone: a defect in the data itself,
    #    not just the render.
    empty_map = {"z1.html": []}
    problems = preflight.check_common_items_rendered(
        empty_map, {"z1.html": _block(GOOD_ITEMS)})
    if not problems:
        fails.append("empty common_items in the corpus NOT caught")

    # 6. Against the real, committed corpus and site/zones/*.html: proves
    #    the authored cohort (Entryway's 5 zones, as of this gate's own
    #    pilot) actually ships what content.json says, today. The cohort
    #    GROWS one room at a time; a floor catches the real regression,
    #    which is the cohort silently shrinking, not its correct growth.
    real_map = _load_real()
    if len(real_map) < 5:
        fails.append("expected at least the 5 original Entryway zones with "
                     "common_items in the real corpus, found %d: the cohort "
                     "has SHRUNK, which is a regression" % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_common_items_rendered(real_map, real_pages)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: %d cases" % 6)
    return 0


if __name__ == "__main__":
    sys.exit(main())
