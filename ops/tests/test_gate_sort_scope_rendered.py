#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_sort_scope_rendered() catches the defect
classes this field's own gate guards against: a page carrying the
sort-scope block the corpus never authorised, a zone whose page never got
regenerated after a content.json edit (missing block), a rendered list
that drifted from what the corpus actually says (stale or paraphrased),
and a half (belongs or strays) rendered despite the corpus naming it empty.

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit that is never regenerated, or a regeneration that
silently drops the block, fails this test directly rather than waiting for
someone to notice on the live page.

Run:  python ops/tests/test_gate_sort_scope_rendered.py
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


def _block(belongs, strays):
    out = ['<h2>What belongs, and what strays in</h2>']
    if belongs:
        rows = "".join("<li>%s</li>" % bzp.esc(i) for i in belongs)
        out.append('<p>Belongs here:</p><ul class="sort-scope-belongs">%s</ul>' % rows)
    if strays:
        rows = "".join("<li>%s</li>" % bzp.esc(i) for i in strays)
        out.append('<p>Strays in and should leave:</p><ul class="sort-scope-strays">%s</ul>' % rows)
    return "".join(out)


GOOD_BELONGS = ["Keys and sunglasses, in the tray", "One wallet and one phone per adult"]
GOOD_STRAYS = ["Keys that open nothing", "Dead batteries"]


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    scope_map = {}
    for r in rooms:
        for z in r.get("zones", []):
            scope = z.get("sort_scope")
            if not scope:
                continue
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            scope_map["%s-%s.html" % (rs, zs)] = scope
    return scope_map


def main() -> int:
    fails = []

    # 1. Clean synthetic page: no problems.
    pages = {"z1.html": _block(GOOD_BELONGS, GOOD_STRAYS)}
    smap = {"z1.html": {"belongs": GOOD_BELONGS, "strays": GOOD_STRAYS}}
    problems = preflight.check_sort_scope_rendered(smap, pages)
    if problems:
        fails.append("clean synthetic page wrongly flagged: %s" % problems)

    # 2. A page renders the block but the corpus never authorised it.
    problems = preflight.check_sort_scope_rendered({}, pages)
    if not problems:
        fails.append("un-authorised sort-scope block NOT caught")

    # 3. A zone has sort_scope in the corpus but its page carries none
    #    (never regenerated).
    problems = preflight.check_sort_scope_rendered(smap, {"z1.html": "<p>stale</p>"})
    if not problems:
        fails.append("missing sort-scope block on an authored zone NOT caught")

    # 4. Stale/paraphrased belongs item: the page's text no longer matches
    #    the corpus's own words.
    stale_belongs = ["Stale tray item", "One wallet and one phone per adult"]
    stale_pages = {"z1.html": _block(stale_belongs, GOOD_STRAYS)}
    problems = preflight.check_sort_scope_rendered(smap, stale_pages)
    if not problems:
        fails.append("paraphrased/stale belongs item NOT caught")

    # 5. Corpus names an empty strays list for a zone, but the page renders
    #    a strays block anyway (generator bug, not a content gap).
    empty_strays_map = {"z1.html": {"belongs": GOOD_BELONGS, "strays": []}}
    problems = preflight.check_sort_scope_rendered(
        empty_strays_map, {"z1.html": _block(GOOD_BELONGS, GOOD_STRAYS)})
    if not problems:
        fails.append("strays block rendered despite an empty corpus list NOT caught")

    # 6. Against the real, committed corpus and site/zones/*.html: proves
    #    the authored pilot cohort (Entryway's 5 zones) actually ships what
    #    content.json says, today. The cohort GROWS one room at a time; a
    #    floor catches the real regression, which is the cohort silently
    #    shrinking, not its correct growth.
    real_map = _load_real()
    if len(real_map) < 5:
        fails.append("expected at least the 5 original Entryway zones with "
                     "sort_scope in the real corpus, found %d: the cohort "
                     "has SHRUNK, which is a regression" % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_sort_scope_rendered(real_map, real_pages)
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
