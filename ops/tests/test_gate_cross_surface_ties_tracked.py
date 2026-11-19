#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_cross_surface_ties_tracked() (and its pure
helper, cross_surface_tie_count()) correctly counts partial-tier rows where
the title and heading surfaces score an exact tie but credit two different
pages, the shape at least five same-day cycles on 2026-11-19 each traced by
hand (A74, A82, A114, A197 and its own further instances, "bags of spices",
"gear toolbox organization ideas") before correctly declining to force a fix.

Run:  python ops/tests/test_gate_cross_surface_ties_tracked.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _row(coverage, heading_coverage, best_page, heading_page):
    return {"coverage": coverage, "heading_coverage": heading_coverage,
            "best_page": best_page, "heading_page": heading_page}


def main() -> int:
    fails = []

    # 1. Empty input: nothing to count.
    n = preflight.cross_surface_tie_count([])
    if n:
        fails.append("empty rows wrongly counted a tie: %r" % n)

    # 2. Same score, same page: not a tie worth naming (nothing is
    #    arbitrary when both surfaces agree on the page).
    rows = [_row(0.667, 0.667, "/zones/a.html", "/zones/a.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n:
        fails.append("same-page tie wrongly counted: %r" % n)

    # 3. Different scores, different pages: not a tie, one surface won
    #    outright, score_rows() has a decisive signal.
    rows = [_row(0.667, 0.5, "/zones/a.html", "/zones/b.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n:
        fails.append("a non-tie (different scores) wrongly counted: %r" % n)

    # 4. A score tie below the partial floor (0.333 == 0.333 but < 0.5):
    #    the row is still 'gap', crediting either page barely matters, and
    #    this shape has never been the one five cycles traced by hand.
    rows = [_row(0.333, 0.333, "/zones/a.html", "/zones/b.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n:
        fails.append("a sub-partial tie wrongly counted: %r" % n)

    # 5. A score tie exactly at 1.0 ("covered" on both surfaces): both
    #    pages already fully answer the query, so which one is credited is
    #    cosmetic, not the ambiguity this gate names.
    rows = [_row(1.0, 1.0, "/zones/a.html", "/zones/b.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n:
        fails.append("a fully-covered tie wrongly counted: %r" % n)

    # 6. The real shape: partial-tier, exact tie, two different pages. Must
    #    count exactly one, and the wrapper must warn naming it.
    rows = [_row(0.667, 0.667, "/zones/toy-storage.html",
                 "/zones/clothing-closet.html"),
            _row(1.0, 1.0, "/zones/a.html", "/zones/a.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n != 1:
        fails.append("the real tie shape counted %r, expected 1" % n)

    # 7. Several ties in one corpus sum correctly.
    rows = [_row(0.5, 0.5, "/zones/a.html", "/zones/b.html"),
            _row(0.667, 0.667, "/zones/c.html", "/zones/d.html"),
            _row(0.667, 0.5, "/zones/e.html", "/zones/f.html")]
    n = preflight.cross_surface_tie_count(rows)
    if n != 2:
        fails.append("several ties summed to %r, expected 2" % n)

    # 8. The wrapper, monkeypatched to a synthetic file pair with 0 ties,
    #    must stay silent.
    import json
    import tempfile
    real_root = preflight.ROOT
    tmpdir = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmpdir, "ops"), exist_ok=True)
        empty = {"rows": [_row(1.0, 1.0, "/a.html", "/a.html")]}
        for name in ("keyword-demand.json", "keyword-demand-global.json"):
            with open(os.path.join(tmpdir, "ops", name), "w",
                      encoding="utf-8") as f:
                json.dump(empty, f)
        preflight.ROOT = tmpdir
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_cross_surface_ties_tracked()
        if preflight.WARN:
            fails.append("a 0-tie synthetic pair wrongly warned: %r"
                         % preflight.WARN)
    finally:
        preflight.ROOT = real_root

    # 9. The wrapper, monkeypatched to a synthetic file pair with a real
    #    tie, must warn and name the count.
    tmpdir2 = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmpdir2, "ops"), exist_ok=True)
        with_tie = {"rows": [_row(0.667, 0.667, "/zones/a.html",
                                   "/zones/b.html")]}
        empty = {"rows": []}
        with open(os.path.join(tmpdir2, "ops", "keyword-demand.json"), "w",
                  encoding="utf-8") as f:
            json.dump(with_tie, f)
        with open(os.path.join(tmpdir2, "ops",
                                "keyword-demand-global.json"), "w",
                  encoding="utf-8") as f:
            json.dump(empty, f)
        preflight.ROOT = tmpdir2
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_cross_surface_ties_tracked()
        if not preflight.WARN:
            fails.append("a real synthetic tie did not warn")
        elif "1" not in preflight.WARN[0][1]:
            fails.append("warning did not name the count: %r"
                         % preflight.WARN)
    finally:
        preflight.ROOT = real_root

    # 10. The real committed keyword-demand files, as they stand today:
    #     the real wrapper must warn, proving today's actual corpus still
    #     carries this shape (confirmed live, 2026-11-19: 37 in the US
    #     corpus alone).
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_cross_surface_ties_tracked()
    if not preflight.WARN:
        fails.append("the real committed files did not warn; either the "
                     "shape has genuinely disappeared from the corpus "
                     "(update this test) or the wrapper is broken")

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_cross_surface_ties_tracked: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
