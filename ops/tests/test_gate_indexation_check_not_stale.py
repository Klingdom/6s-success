#!/usr/bin/env python3
"""
Prove ops/preflight.py's indexation_check_staleness_problem() catches a
stale or missing ops/indexation.json, the only reading this business has
of which sections are actually indexed (GOALS.md O1).

Run:  python ops/tests/test_gate_indexation_check_not_stale.py
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def main() -> int:
    fails = []
    now = dt.datetime(2026, 10, 3, 12, 0, 0, tzinfo=dt.timezone.utc)

    # 1. Missing file (None payload): must fire, by name, and point at the
    #    workflow that exists to fix it.
    problem = preflight.indexation_check_staleness_problem(None, now)
    if "indexation.json does not exist" not in problem:
        fails.append("missing payload did not report a missing file: %r" % problem)
    if "indexation-check.yml" not in problem:
        fails.append("missing-file problem did not point at the fix: %r" % problem)

    # 2. Three weeks stale: must fire.
    old = {"checked_at": "2026-09-12T08:00:00Z"}
    problem = preflight.indexation_check_staleness_problem(old, now)
    if "days old" not in problem:
        fails.append("21-day-old reading did not report stale: %r" % problem)

    # 3. Two days old: must NOT fire.
    fresh = {"checked_at": "2026-10-01T08:00:00Z"}
    problem = preflight.indexation_check_staleness_problem(fresh, now)
    if problem:
        fails.append("a 2-day-old reading wrongly fired: %r" % problem)

    # 4. Exactly at the 14-day ceiling's edge, 13 days old: must NOT fire.
    edge = {"checked_at": "2026-09-20T12:00:00Z"}
    problem = preflight.indexation_check_staleness_problem(edge, now)
    if problem:
        fails.append("a 13-day-old reading wrongly fired: %r" % problem)

    # 5. No checked_at field at all: must fire, not crash.
    problem = preflight.indexation_check_staleness_problem({}, now)
    if "checked_at" not in problem:
        fails.append("payload with no checked_at did not report it: %r" % problem)

    # 6. Unparseable checked_at: must fire, not crash.
    problem = preflight.indexation_check_staleness_problem(
        {"checked_at": "not-a-date"}, now)
    if "does not parse" not in problem:
        fails.append("unparseable checked_at did not report it: %r" % problem)

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_indexation_check_not_stale: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
