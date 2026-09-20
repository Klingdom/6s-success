#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_kit_compact_rendered() catches the defect
classes REVIEW-DISCOVERY-2026-09-07.md D5 exists to hold: a pilot zone
whose kit list still renders before the six passes (never regenerated, or
regressed back), a non-pilot zone whose kit list wrongly moved after the
six passes (D5 is scoped to the 12-zone pilot cohort only, not all 114),
and a compact block that has grown back past the word ceiling "compact"
is supposed to mean.

Also runs against the real, committed corpus and site/zones/*.html, so a
future content.json edit or a regeneration that silently drops the D5
placement fails this test directly.

Run:  python ops/tests/test_gate_kit_compact_rendered.py
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


def _passes_then_kit(compact=True, over_ceiling=False):
    """A synthetic pilot page: six passes, then the kit block after them."""
    body = ["<h2>The six passes, in order</h2>",
            '<section id="sort"><h3>Sort</h3><p>Sort text.</p></section>',
            '<section id="sustain"><h3>Sustain</h3><p>Sustain text.</p></section>']
    words = "word " * (350 if over_ceiling else 40)
    cls = "kit-item kit-compact" if compact else "kit-item"
    body.append('<h2 id="what-you-need">The kit this zone called for</h2>'
               '<p>%s</p><ul class="kit-list %s"><li class="%s">one item'
               '</li></ul>' % (words, "kit-compact" if compact else "",
                               cls))
    body.append("</main>")
    return "".join(body)


def _kit_then_passes():
    """A synthetic non-pilot page: kit list before the six passes, as
    render() (not render_compact()) has always placed it."""
    return ('<h2 id="what-you-need">What to have on hand before you start'
           '</h2><p>kit words here</p><ul class="kit-list">'
           '<li class="kit-item">one item</li></ul>'
           '<h2>The six passes, in order</h2>'
           '<section id="sort"><h3>Sort</h3></section>'
           '<section id="sustain"><h3>Sustain</h3></section></main>')


def main() -> int:
    fails = []

    # 1. Clean pilot page: kit list after the passes, compact class present,
    #    under the word ceiling. No problems.
    pages = {"p1.html": _passes_then_kit()}
    problems = preflight.check_kit_compact_rendered(["p1.html"], [], pages)
    if problems:
        fails.append("clean pilot page wrongly flagged: %s" % problems)

    # 2. Clean non-pilot page: kit list before the passes, unchanged. No
    #    problems.
    other_pages = {"o1.html": _kit_then_passes()}
    problems = preflight.check_kit_compact_rendered([], ["o1.html"], other_pages)
    if problems:
        fails.append("clean non-pilot page wrongly flagged: %s" % problems)

    # 3. A pilot zone regressed: kit list still before the passes (D5 never
    #    applied, or reverted).
    regressed = {"p1.html": _kit_then_passes()}
    problems = preflight.check_kit_compact_rendered(["p1.html"], [], regressed)
    if not problems:
        fails.append("pilot zone with kit list before the passes NOT caught")

    # 4. A non-pilot zone wrongly moved: D5 must stay scoped to the 12-zone
    #    cohort, not spread to all 114.
    overreach = {"o1.html": _passes_then_kit()}
    problems = preflight.check_kit_compact_rendered([], ["o1.html"], overreach)
    if not problems:
        fails.append("non-pilot zone with kit list after the passes "
                     "(D5 scope creep) NOT caught")

    # 5. A pilot page's kit block has grown back past the word ceiling.
    bloated = {"p1.html": _passes_then_kit(over_ceiling=True)}
    problems = preflight.check_kit_compact_rendered(["p1.html"], [], bloated)
    if not problems:
        fails.append("oversized (no-longer-compact) kit block NOT caught")

    # 6. A pilot page's kit block is positioned correctly but never used
    #    render_compact()'s own kit-compact class (e.g. a future edit wires
    #    the wrong function back in).
    wrong_fn = {"p1.html": _passes_then_kit(compact=False)}
    problems = preflight.check_kit_compact_rendered(["p1.html"], [], wrong_fn)
    if not problems:
        fails.append("pilot page not using render_compact()'s kit-compact "
                     "class NOT caught")

    # 7. Against the real, committed corpus and site/zones/*.html: proves
    #    the 12 pilot zones actually ship D5's placement today, and the
    #    other 102 are untouched.
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    real_pilot, real_other = [], []
    for r in rooms:
        for z in r.get("zones", []):
            name = bzp.display(r["room"], z["zone"])
            rs, zs = bzp.slug(r["room"]), bzp.slug(name)
            fname = "%s-%s.html" % (rs, zs)
            (real_pilot if z.get("diagnosis") else real_other).append(fname)
    if len(real_pilot) != 12:
        fails.append("expected 12 pilot zones in the real corpus, found %d "
                     "(has the pilot cohort changed? update this test's "
                     "expectation deliberately if so)" % len(real_pilot))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_kit_compact_rendered(
        sorted(real_pilot), sorted(real_other), real_pages)
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
