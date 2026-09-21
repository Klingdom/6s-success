#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_zone_relations_rendered() catches the defect
classes D9 (REVIEW-DISCOVERY-2026-09-07.md section 2, "route link equity
into the zone pages") depends on: a page carrying the same-job section
without a ZONE_RELATIONS entry to authorise it, a zone with a ZONE_RELATIONS
entry whose page never got regenerated, and a rendered link whose text or
target has drifted from what ZONE_RELATIONS actually says.

Also runs against the real, committed ZONE_RELATIONS and site/zones/*.html,
so a future edit to the relation groups that is never regenerated, or a
regeneration that silently drops or mangles the section, fails this test
directly.

Run:  python ops/tests/test_gate_zone_relations_rendered.py
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


def _block(links):
    out = ['<h2>Zones that do the same job, elsewhere in the house</h2>',
           '<p>filler</p><ul>']
    for slug, text in links:
        out.append('<li><a href="../zones/%s.html">%s</a></li>' % (slug, text))
    out.append("</ul>")
    return "".join(out)


GOOD_LINKS = [
    ("workshop-the-main-workbench", "The Main Workbench in the workshop"),
]


def _load_real():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    bzp._RELATIONS.clear()
    bzp._SIBLINGS.clear()
    idx = bzp._relation_index(rooms)
    sib = bzp._sibling_index(rooms)
    relation_map = {}
    for sl, entries in idx.items():
        already = {e[2] for e in (sib.get(sl, ("", []))[1])}
        want = [(osl, "%s in the %s" % (bzp.esc(onm), bzp.esc(orm.lower())))
                for _why, (orm, onm, osl) in entries if osl not in already]
        if want:
            relation_map["%s.html" % sl] = want
    return relation_map


def main() -> int:
    fails = []

    # 1. Clean synthetic page: no problems.
    pages = {"z1.html": _block(GOOD_LINKS)}
    rmap = {"z1.html": GOOD_LINKS}
    problems = preflight.check_zone_relations_rendered(rmap, pages)
    if problems:
        fails.append("clean synthetic page wrongly flagged: %s" % problems)

    # 2. A page renders the section but ZONE_RELATIONS never authorised it.
    problems = preflight.check_zone_relations_rendered({}, pages)
    if not problems:
        fails.append("un-authorised same-job section NOT caught")

    # 3. A zone has a ZONE_RELATIONS entry but its page carries no section
    #    (never regenerated).
    problems = preflight.check_zone_relations_rendered(
        rmap, {"z1.html": "<p>stale, no section here</p>"})
    if not problems:
        fails.append("missing same-job section on a related zone NOT caught")

    # 4. Stale link text: the page's rendered text no longer matches what
    #    ZONE_RELATIONS actually says (a content.json rename that never
    #    triggered a rebuild).
    stale_pages = {"z1.html": _block(
        [("workshop-the-main-workbench", "Something else entirely")])}
    problems = preflight.check_zone_relations_rendered(rmap, stale_pages)
    if not problems:
        fails.append("stale/mismatched link text NOT caught")

    # 5. Wrong count: ZONE_RELATIONS says 2 links, the page renders 1.
    two_map = {"z1.html": GOOD_LINKS + [
        ("garage-the-hand-tool-wall-and-cabinets",
         "The Hand Tool Wall and Cabinets in the garage")]}
    problems = preflight.check_zone_relations_rendered(two_map, pages)
    if not problems:
        fails.append("link count mismatch NOT caught")

    # 6. Against the real, committed ZONE_RELATIONS and site/zones/*.html:
    #    proves the shipped pages actually carry what the module says, today.
    real_map = _load_real()
    if len(real_map) < 40:
        fails.append("expected dozens of zones with real relations, found "
                      "%d (has ZONE_RELATIONS shrunk? confirm deliberately "
                      "if so)" % len(real_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_zone_relations_rendered(real_map, real_pages)
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
