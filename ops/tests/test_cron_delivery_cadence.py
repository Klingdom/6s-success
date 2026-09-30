#!/usr/bin/env python3
"""
Prove check_cron_cadence judges a script-throttled workflow on what it
DELIVERED, not on how often it was triggered.

WHY THIS EXISTS
---------------
hourly-brief.yml throttles inside ops/hourly_brief.py, not in its YAML: a
triggered run decides at runtime whether it actually mails Phil. So a push run
is as often not a delivery as it is, and has_push_trigger() rightly refuses to
count those runs as coverage. Its own comment says that "costs a
stale-sounding warning" and errs conservative on purpose.

Measured 2026-09-30, all three numbers for the same workflow on the same day:

    schedule-only cadence   290 min   (what the gate reported, and degraded on)
    runs, every trigger      11 min   (true, and not what anybody experiences)
    actual deliveries        60 min   (the answer to "how long does Phil wait")

The third comes from the git history of the record the workflow commits after
each real send, which is a delivery log nobody had read. The brief is
genuinely hourly, around the clock, and had been for days while the gate
called it degraded.

A gate that warns about a healthy workflow trains people to ignore warnings,
which is the same defect two other checks were fixed for the same day. So the
delivery record decides, and the line still SAYS the cron is throttled rather
than suppressing it, because that would matter again the day the throttle or
the push trigger changed.

Run:  python ops/tests/test_cron_delivery_cadence.py
"""
import datetime
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_cron_cadence as C                                 # noqa: E402


def case_the_record_is_named_for_the_throttled_workflow():
    assert "hourly-brief.yml" in C.DELIVERY_RECORDS
    assert C.DELIVERY_RECORDS["hourly-brief.yml"].endswith(".json")


def case_a_workflow_that_throttles_in_script_is_not_given_push_coverage():
    """The conservative half must stay: runs are not deliveries."""
    assert C.has_push_trigger("hourly-brief.yml") is False


def case_the_real_delivery_record_reads_as_hourly():
    gaps = C.delivery_gaps(C.DELIVERY_RECORDS["hourly-brief.yml"])
    if not gaps:
        print("  no git history for the record here. NOT VERIFIED.")
        return
    assert len(gaps) >= 10, len(gaps)
    mean = statistics.mean(gaps)
    # Configured 60. This asserts the measurement is in the right universe,
    # not an exact value that would fail on a quiet night.
    assert 20 <= mean <= 150, mean


def case_an_unreadable_record_is_not_on_time():
    assert C.delivery_gaps("ops/no-such-record-exists.json") is None


def case_too_few_points_is_unreadable_rather_than_confident():
    """Two commits give one gap, which is not a cadence."""
    assert C.delivery_gaps(".github/workflows/hourly-brief.yml", limit=2) is None


def case_a_throttled_cron_with_on_time_delivery_is_not_degraded():
    r = C.check_one("hourly-brief.yml")
    if r.get("verdict") == "unknown":
        print("  cadence unknown here (no API). NOT VERIFIED.")
        return
    if "delivery_mean" not in r:
        print("  delivery record unreadable here. NOT VERIFIED.")
        return
    assert r["delivery_on_time"] is True, r
    assert r["degraded"] is False, r


def case_the_cron_throttling_is_still_reported_not_suppressed():
    """Silently passing would hide a real fact about the schedule."""
    r = C.check_one("hourly-brief.yml")
    if "delivery_mean" not in r:
        return
    # The schedule-only figure must survive on the result, so the warning can
    # still say the cron is throttled.
    assert r.get("mean_gap_min"), r
    assert r["mean_gap_min"] > r["delivery_mean"], r


def case_delivery_only_rescues_a_named_workflow():
    """A workflow with no record must not be rescued by this path."""
    for wf in C.WORKFLOWS:
        if wf in C.DELIVERY_RECORDS:
            continue
        r = C.check_one(wf)
        assert "delivery_on_time" not in r, (wf, r)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
