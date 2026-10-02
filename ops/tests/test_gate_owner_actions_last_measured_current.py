#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_owner_actions_last_measured_current() reads
the dedicated "List reviewed" marker, not "Last measured", and that it
genuinely catches a stale marker without ever touching the traffic
citation dashboard._owner_actions_traffic_citation() depends on.

Found 2026-10-02, PM check-in (issue #38): this gate used to key off
"**Last measured:**", the same paragraph dashboard.py parses for the real
traffic-measurement date. The established fix for a stale header (bump the
leading date) silently told the dashboard a fresh database read had
happened on a day it had not, confirmed live against the real committed
OWNER-ACTIONS.md before this split. Moved the gate onto a separate
"**List reviewed:**" marker so bumping it can never affect the traffic
citation again.

Run:  python ops/tests/test_gate_owner_actions_last_measured_current.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import dashboard                                                 # noqa: E402

STALE = ("# Owner actions\n\n**List reviewed:** 2026-09-04.\n\n"
         "Item 16, added 2026-09-08, this operator.\n")

CURRENT = ("# Owner actions\n\n**List reviewed:** 2026-09-08.\n\n"
           "Item 16, added 2026-09-08, this operator.\n")

NO_BODY_DATE = "# Owner actions\n\n**List reviewed:** 2026-09-08.\n\nNothing dated below.\n"

NO_MARKER = "# Owner actions\n\nNo List reviewed marker at all.\n"

OLD_SHAPE_ONLY = ("# Owner actions\n\n**Last measured:** 2026-09-04 UTC, "
                  "traffic re-measured by a direct database read: 10 "
                  "visitors/20 visits/30 days.\n\nItem 16, added "
                  "2026-09-08, this operator.\n")


def _write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def main() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as d:
        # 1. Stale marker: a later date sits in the body. Must FAIL.
        stale_fp = _write(d, "stale.md", STALE)
        preflight.FAIL.clear()
        preflight.gate_owner_actions_last_measured_current(stale_fp)
        if len(preflight.FAIL) != 1:
            fails.append(f"expected exactly 1 FAIL for a stale marker, "
                          f"got {preflight.FAIL!r}")
        elif "2026-09-04" not in preflight.FAIL[0][1] or \
                "2026-09-08" not in preflight.FAIL[0][1]:
            fails.append(f"FAIL message did not name both dates: "
                          f"{preflight.FAIL[0]!r}")

        # 2. The fix: marker bumped to match the newest body date. Must
        #    pass clean.
        current_fp = _write(d, "current.md", CURRENT)
        preflight.FAIL.clear()
        preflight.gate_owner_actions_last_measured_current(current_fp)
        if preflight.FAIL:
            fails.append(f"a current marker must not fail: {preflight.FAIL!r}")

        # 3. No date anywhere in the body: nothing to compare against,
        #    must not fail.
        nobody_fp = _write(d, "nobody.md", NO_BODY_DATE)
        preflight.FAIL.clear()
        preflight.gate_owner_actions_last_measured_current(nobody_fp)
        if preflight.FAIL:
            fails.append(f"a body with no date must not fail: {preflight.FAIL!r}")

        # 4. Marker missing entirely: warn, not fail (same convention as
        #    every other reshaped-anchor gate in this file).
        nomarker_fp = _write(d, "nomarker.md", NO_MARKER)
        preflight.FAIL.clear()
        preflight.WARN.clear()
        preflight.gate_owner_actions_last_measured_current(nomarker_fp)
        if preflight.FAIL:
            fails.append(f"a missing marker must warn, not fail: {preflight.FAIL!r}")
        if not preflight.WARN:
            fails.append("a missing marker must warn that the shape changed")

        # 5. Missing file entirely: must not fail.
        preflight.FAIL.clear()
        preflight.gate_owner_actions_last_measured_current(
            os.path.join(d, "does-not-exist.md"))
        if preflight.FAIL:
            fails.append(f"a missing file must not fail: {preflight.FAIL!r}")

        # 6. The exact regression this split fixes: a file carrying only
        #    the OLD "Last measured" shape, no "List reviewed" marker at
        #    all, must warn (shape changed/missing) rather than silently
        #    passing or reading the traffic paragraph's own date as if it
        #    were this gate's marker.
        oldshape_fp = _write(d, "oldshape.md", OLD_SHAPE_ONLY)
        preflight.FAIL.clear()
        preflight.WARN.clear()
        preflight.gate_owner_actions_last_measured_current(oldshape_fp)
        if preflight.FAIL:
            fails.append(f"old-shape-only file must warn, not fail: "
                          f"{preflight.FAIL!r}")
        if not preflight.WARN:
            fails.append("old-shape-only file must warn that the marker "
                          "is missing")

        # 7. The split itself: bumping this gate's marker on that same
        #    OLD_SHAPE_ONLY-style document must never change what
        #    dashboard._owner_actions_traffic_citation() reads from the
        #    "Last measured" paragraph. Build a document carrying both
        #    markers with different dates and confirm the traffic
        #    citation still comes from "Last measured" alone.
        both_fp = _write(d, "both.md", (
            "# Owner actions\n\n**Last measured:** 2026-09-23 12:50 UTC, "
            "traffic re-measured by a direct database read: 68 "
            "visitors/160 visits/30 days.\n\n"
            "**List reviewed:** 2026-10-02.\n\n"
            "Item 16, added 2026-10-02, this operator.\n"))
        preflight.FAIL.clear()
        preflight.gate_owner_actions_last_measured_current(both_fp)
        if preflight.FAIL:
            fails.append(f"a current List-reviewed marker next to an "
                          f"older Last-measured date must not fail: "
                          f"{preflight.FAIL!r}")
        got = dashboard._owner_actions_traffic_citation(both_fp)
        if got != ("2026-09-23 12:50", 68, 160):
            fails.append(f"bumping List reviewed must not change the "
                          f"traffic citation: got {got!r}, expected "
                          f"('2026-09-23 12:50', 68, 160)")

    # 8. The real, committed OWNER-ACTIONS.md must parse clean today.
    preflight.FAIL.clear()
    preflight.gate_owner_actions_last_measured_current()
    if preflight.FAIL:
        fails.append(f"the real committed OWNER-ACTIONS.md must parse "
                      f"clean: {preflight.FAIL!r}")

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 8/8 cases (fail-then-pass proved, traffic citation confirmed untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
