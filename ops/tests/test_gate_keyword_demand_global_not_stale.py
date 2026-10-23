#!/usr/bin/env python3
"""
Prove ops/preflight.py's keyword_demand_global_staleness_problem() catches a
stale or missing ops/keyword-demand-global.json, the only reading this
business has of what people outside the US actually type (GOALS.md O1,
the 2026-10-23 owner direction to attract more global visitors).

Same shape as test_gate_keyword_demand_not_stale.py, 14 days not 10, and the
missing-file message points at ops/keyword_demand_global.py instead.

Run:  python ops/tests/test_gate_keyword_demand_global_not_stale.py
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def main() -> int:
    fails = []
    now = dt.datetime(2026, 10, 23, 12, 0, 0, tzinfo=dt.timezone.utc)

    # 1. Missing file (None payload): must fire, by name, and point at the
    #    tool that exists to fix it.
    problem = preflight.keyword_demand_global_staleness_problem(None, now)
    if "keyword-demand-global.json does not exist" not in problem:
        fails.append("missing payload did not report a missing file: %r" % problem)
    if "keyword_demand_global.py" not in problem:
        fails.append("missing-file problem did not point at the fix: %r" % problem)

    # 2. Three weeks stale: must fire.
    old = {"checked_at": "2026-10-02T08:00:00Z"}
    problem = preflight.keyword_demand_global_staleness_problem(old, now)
    if "days old" not in problem:
        fails.append("21-day-old reading did not report stale: %r" % problem)

    # 3. Exactly at the real first harvest's own date, two weeks on: must
    #    still fire (regression guard for the real file this gate reads).
    first_reading = {"checked_at": "2026-10-23T17:21:09Z"}
    problem = preflight.keyword_demand_global_staleness_problem(
        first_reading, now + dt.timedelta(days=15))
    if not problem:
        fails.append("a 15-day-old real-shaped reading did not fire")

    # 4. Two days old: must NOT fire.
    fresh = {"checked_at": "2026-10-21T08:00:00Z"}
    problem = preflight.keyword_demand_global_staleness_problem(fresh, now)
    if problem:
        fails.append("a 2-day-old reading wrongly fired: %r" % problem)

    # 5. No checked_at field at all: must fire, not crash.
    problem = preflight.keyword_demand_global_staleness_problem({}, now)
    if "checked_at" not in problem:
        fails.append("payload with no checked_at did not report it: %r" % problem)

    # 6. Unparseable checked_at: must fire, not crash.
    problem = preflight.keyword_demand_global_staleness_problem(
        {"checked_at": "not-a-date"}, now)
    if "does not parse" not in problem:
        fails.append("unparseable checked_at did not report it: %r" % problem)

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_keyword_demand_global_not_stale: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
