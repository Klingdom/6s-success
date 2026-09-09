#!/usr/bin/env python3
"""
Prove the cron-cadence check can tell on-time from degraded from unmeasured.

Written the same cycle the check itself was, after the real Actions API
history showed fulfil-orders.yml and hourly-brief.yml both running at 4 to 7x
their configured interval, sustained across 14+ days. A check that has only
ever run once against the live account is a hypothesis; these exercise the
comparison against synthetic run histories instead.

Run:  python ops/tests/test_check_cron_cadence.py
"""
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_cron_cadence as C                                # noqa: E402


def runs_every(minutes: float, count: int) -> list:
    start = datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc)
    return [{"created_at": (start + datetime.timedelta(minutes=minutes * i))
              .strftime("%Y-%m-%dT%H:%M:%SZ")} for i in range(count)]


def with_runs(runs):
    real, C.fetch_runs = C.fetch_runs, (lambda wf, per_page=50: runs)
    try:
        return C.check_one("fulfil-orders.yml")
    finally:
        C.fetch_runs = real


def main() -> int:
    fails = []

    # Case 1: firing right on its configured 30-minute interval.
    r = with_runs(runs_every(30, 20))
    if r["verdict"] != "measured" or r.get("degraded"):
        fails.append(f"on-schedule runs should not be degraded, got {r}")

    # Case 2: the real shape found live, gaps averaging ~7x the configured
    # interval.
    r = with_runs(runs_every(210, 20))
    if r["verdict"] != "measured" or not r.get("degraded"):
        fails.append(f"213-minute gaps against a 30-minute cron must be "
                     f"degraded, got {r}")

    # Case 3: no token / unreachable API must be unknown, never a clean pass.
    r = with_runs(None)
    if r["verdict"] != "unknown":
        fails.append(f"an unreachable API must be unknown, got {r['verdict']}")

    # Case 4: too few completed runs on record to trust a gap measurement.
    r = with_runs(runs_every(30, 3))
    if r["verdict"] != "unknown":
        fails.append(f"3 runs is too few to measure cadence, got {r['verdict']}")

    # Case 5: the cron line itself parses to the right configured interval,
    # against the real committed workflow files, not a guessed number.
    thirty = C.configured_interval_minutes("fulfil-orders.yml")
    if thirty != 30.0:
        fails.append(f"fulfil-orders.yml's '7,37 * * * *' should parse to "
                     f"30 minutes, got {thirty}")
    sixty = C.configured_interval_minutes("hourly-brief.yml")
    if sixty != 60.0:
        fails.append(f"hourly-brief.yml's '23 * * * *' should parse to "
                     f"60 minutes, got {sixty}")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {6 - len(fails)} of 6 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
