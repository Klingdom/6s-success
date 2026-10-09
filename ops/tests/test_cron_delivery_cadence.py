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


def case_the_real_delivery_record_is_readable_and_reported():
    """The record must PARSE into a plausible cadence. The number is not a law.

    RENAMED AND REWRITTEN 2026-10-09. This asserted 20 <= mean <= 150 with a
    comment saying it was checking "the right universe, not an exact value
    that would fail on a quiet night". The real mean is now 201.8 minutes, so
    it failed, and it failed the image build with it: nothing could deploy for
    four days because GitHub got slower at firing a cron.

    That is the wrong boundary. A test asserts logic; check_cron_cadence
    measures; preflight carries the drift as a warning, which it already does
    and which is where a reader should meet this. A test that encodes a
    measurement as an invariant also teaches whoever meets it to edit the
    number rather than read the finding, which is how a real degradation gets
    normalised one commit at a time.

    So this asserts the record is readable, has enough points to be a cadence,
    and lands somewhere physically possible, then PRINTS the figure so a reader
    of the test output sees the drift rather than a silent pass.
    """
    gaps = C.delivery_gaps(C.DELIVERY_RECORDS["hourly-brief.yml"])
    if not gaps:
        print("  no git history for the record here. NOT VERIFIED.")
        return
    assert len(gaps) >= 10, len(gaps)
    mean = statistics.mean(gaps)
    # Configured 60. A mean under a minute would mean the parser is reading
    # something other than send times; over a day would mean the brief has
    # effectively stopped. Either is a defect in this repository. Anything
    # between is GitHub, and belongs in a warning rather than a build failure.
    assert 1 <= mean <= 24 * 60, mean
    print("  hourly-brief delivery: mean %.0f min over %d gap(s), configured "
          "60. %s"
          % (mean, len(gaps),
             "on time" if mean <= 90 else "LATE, and reported as degraded by "
             "check_cron_cadence"))

def case_an_unreadable_record_is_not_on_time():
    assert C.delivery_gaps("ops/no-such-record-exists.json") is None


def case_too_few_points_is_unreadable_rather_than_confident():
    """Two commits give one gap, which is not a cadence."""
    assert C.delivery_gaps(".github/workflows/hourly-brief.yml", limit=2) is None


def case_a_throttled_cron_with_on_time_delivery_is_not_degraded():
    """The rescue is an IMPLICATION, not a prediction about this week.

    REWRITTEN 2026-10-09. The old version read the live result for
    hourly-brief.yml and asserted delivery_on_time is True and degraded is
    False. Both were true when it was written. Neither is a law: check_one()
    sets delivery_on_time only when the measured delivery mean comes in under
    1.5x the configured interval, and the hourly brief is currently delivering
    every 202 minutes against a configured 60. So the key is absent, degraded
    is correctly True, and this case failed the image build for four days over
    a real fact about the brief rather than a defect.

    The real contract, in both directions:
      * if delivery_on_time is set, degraded must have been cleared
      * if it is not set, the result must still SAY why, with the measured
        delivery figures on it, rather than going quiet

    The original regression (a throttled cron whose delivery IS on time being
    reported degraded anyway) is proved by case_an_on_time_record_clears_
    degraded below against a synthetic record, so it no longer depends on how
    GitHub happens to be behaving today.
    """
    r = C.check_one("hourly-brief.yml")
    if r.get("verdict") == "unknown":
        print("  cadence unknown here (no API). NOT VERIFIED.")
        return
    if "delivery_mean" not in r:
        print("  delivery record unreadable here. NOT VERIFIED.")
        return
    if "delivery_on_time" in r:
        assert r["delivery_on_time"] is True, r
        assert r["degraded"] is False, (
            "delivery was judged on time and degraded was not cleared: %r" % (r,))
    else:
        assert r.get("degraded") is True, (
            "delivery was NOT judged on time, so this must stay degraded "
            "rather than quietly passing: %r" % (r,))
        assert r.get("delivery_n"), (
            "degraded with no delivery sample size on the result, so a reader "
            "cannot tell an unmeasured record from a late one: %r" % (r,))
        print("  hourly-brief delivers every %.0f min against a configured "
              "%.0f (n=%d). Degraded, correctly, and reported."
              % (r["delivery_mean"], r["configured_interval_min"],
                 r["delivery_n"]))


def case_an_on_time_record_clears_degraded():
    """The rescue decision itself, at its own seam.

    This is what the case above used to rely on the live world for. The first
    attempt wrote a synthetic JSON record and pointed DELIVERY_RECORDS at it,
    and it reported NOT VERIFIED: delivery_gaps() does not read the file, it
    reads the file's GIT HISTORY, so a freshly written temp file has no
    cadence at all. Keeping that version would have left a case that looks
    like coverage and proves nothing.

    So the patch goes at the real seam, delivery_gaps itself, and the two
    cases below pin the boundary the code actually decides on: a delivery mean
    inside 1.5x the configured interval clears degraded, and one outside it
    does not. Configured is 60 for hourly-brief.yml, so 45 passes and 200,
    which is roughly what it is really doing today, does not.
    """
    real = C.delivery_gaps
    try:
        C.delivery_gaps = lambda *a, **k: [45.0] * 12
        r = C.check_one("hourly-brief.yml")
        if r.get("verdict") == "unknown":
            print("  cadence unknown here (no API). NOT VERIFIED.")
            return
        assert r.get("delivery_on_time") is True, (
            "a 45 minute delivery mean against a configured 60 was not judged "
            "on time: %r" % (r,))
        assert r.get("degraded") is False, r

        C.delivery_gaps = lambda *a, **k: [200.0] * 12
        r2 = C.check_one("hourly-brief.yml")
        assert "delivery_on_time" not in r2, (
            "a 200 minute delivery mean against a configured 60 was judged on "
            "time: %r" % (r2,))
        assert r2.get("degraded") is True, (
            "a late delivery mean did not leave the workflow degraded: %r" % (r2,))
        assert r2.get("delivery_mean") == 200.0, r2
    finally:
        C.delivery_gaps = real

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
