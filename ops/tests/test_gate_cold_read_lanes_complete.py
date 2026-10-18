#!/usr/bin/env python3
"""
Prove ops/cold_read_ledger.py's lane_coverage_gaps() catches a
hand-authored *.py/*.js file sitting in a directory no LANES entry
covers, the exact shape that let photos/, ops/cardtext/ and
build/listings/ (and then 13 more lanes, 39 files) sit undiscovered for
weeks each, found only when a cycle chose to list every candidate file
by hand and compare it against the lane list. gate_cold_read_lanes_
complete (ops/preflight.py) now runs that same sweep every cycle; this
test proves the pure logic behind it can actually fail, with a
synthetic file list, not just pass on whatever the repository happens
to look like today.

Run:  python ops/tests/test_gate_cold_read_lanes_complete.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import cold_read_ledger as crl                                    # noqa: E402


def main() -> int:
    fails = []

    # 1. A file in a genuinely uncovered directory IS a gap.
    gaps = crl.lane_coverage_gaps(["some/new/directory/script.py"])
    if gaps != ["some/new/directory/script.py"]:
        fails.append("an uncovered directory's file was not flagged a "
                      "gap: %r" % gaps)

    # 2. The same file, once its directory matches a real LANES entry
    #    and pattern, is no longer a gap.
    gaps = crl.lane_coverage_gaps(["ops/some_new_module.py"])
    if gaps:
        fails.append("ops/some_new_module.py should be covered by the "
                      "('ops', '*.py') lane: %r" % gaps)

    # 3. A wrong-extension match in a covered directory (pattern is
    #    *.py, file is .js) stays a gap: directory alone is not enough.
    gaps = crl.lane_coverage_gaps(["ops/stray.ini"])
    if gaps:
        fails.append("a non-.py/.js file must never be reported, "
                      "covered or not: %r" % gaps)
    gaps = crl.lane_coverage_gaps(["ops/cardtext/stray.js"])
    if gaps != ["ops/cardtext/stray.js"]:
        fails.append("ops/cardtext's lane is *.py only; a .js file "
                      "there should still be a gap: %r" % gaps)

    # 4. ops/tests/** is excluded (read with the module it tests).
    gaps = crl.lane_coverage_gaps(["ops/tests/test_something.py"])
    if gaps:
        fails.append("ops/tests/** must be excluded, not flagged: %r"
                      % gaps)

    # 5. *.test.js anywhere is excluded, even outside a JS lane.
    gaps = crl.lane_coverage_gaps(["some/new/directory/widget.test.js"])
    if gaps:
        fails.append("*.test.js must be excluded everywhere, not just "
                      "inside a known lane: %r" % gaps)

    # 6. A basename in GENERATED_JS is excluded even in an uncovered
    #    directory (the same generated-output rule LANES itself applies).
    gaps = crl.lane_coverage_gaps(["some/new/directory/data.js"])
    if gaps:
        fails.append("a GENERATED_JS basename must be excluded "
                      "regardless of directory: %r" % gaps)

    # 7. A path in NON_LANE_GENERATED is excluded.
    real_non_lane = next(iter(crl.NON_LANE_GENERATED))
    gaps = crl.lane_coverage_gaps([real_non_lane])
    if gaps:
        fails.append("a NON_LANE_GENERATED path must be excluded: %r"
                      % gaps)

    # 8. Mixed list: only the genuine gap is returned, sorted.
    gaps = crl.lane_coverage_gaps([
        "ops/preflight.py",                  # covered
        "zzz/uncovered/two.py",              # gap
        "aaa/uncovered/one.py",              # gap
        "ops/tests/test_x.py",               # excluded
    ])
    if gaps != ["aaa/uncovered/one.py", "zzz/uncovered/two.py"]:
        fails.append("mixed list did not return exactly the two real "
                      "gaps, sorted: %r" % gaps)

    # 9. Every real file this repository currently tracks must have zero
    #    gaps as of this commit: the whole point of landing this gate is
    #    that the sweep it runs is clean right now. If this ever fails,
    #    it means a real new directory needs a LANES entry (or a
    #    NON_LANE_GENERATED exclusion with a reason), not that the test
    #    is wrong.
    real_gaps = crl.lane_coverage_gaps(crl.git_tracked_py_js())
    if real_gaps:
        fails.append("the real repository has %d un-laned file(s) as of "
                      "this commit: %s" % (len(real_gaps), real_gaps))

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  cold_read_ledger lane_coverage_gaps: 9/9 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
