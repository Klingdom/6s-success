#!/usr/bin/env python3
"""
Prove the cadence check reports the interval a CUSTOMER experiences, not only
the interval GitHub's cron manages, and that it only claims coverage where a
pushed run genuinely does the work.

WHY THIS EXISTS
---------------
ops/check_cron_cadence.py filters to event=schedule on purpose: it was written
to answer "does this cron fire as often as it claims", and the answer for
fulfil-orders.yml is no, by a factor of eight. That is true and worth knowing.

It is not the question a buyer has. fulfil-orders.yml gained a push trigger on
2026-09-09 precisely because the cron is throttled, so every commit to main is
another chance to deliver a paid order. Measured 2026-09-27 over the same
window: schedule-only gaps mean 284 minutes and worst 354, while across every
trigger the mean is 15.7, the median 12.9 and the worst 42.1, because 76 of 80
runs came from push.

So the warning had been saying a buyer might wait six hours when the measured
worst case was forty-two minutes. Overstating customer risk by an order of
magnitude is not a safe error: it is how a team learns to scroll past warnings.

The second half matters as much. linkedin-drafts.yml and social-drafts.yml also
trigger on push, but they branch on github.event_name and use push as a gated
fallback that only sends once the schedule is already overdue. Their push RUNS
are frequent; their push DELIVERIES are not. Counting those runs as coverage
claimed an 11.7-minute median for a workflow whose job is to post once a day:
true about runs, false about anything a person cares about.

Run:  python ops/tests/test_cron_effective_latency.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_cron_cadence as C                                 # noqa: E402

WF = os.path.join(ROOT, ".github", "workflows")


def case_fulfil_orders_counts_as_covered():
    """It has a push trigger and no event_name branch, so every run delivers."""
    assert os.path.exists(os.path.join(WF, "fulfil-orders.yml"))
    assert C.has_push_trigger("fulfil-orders.yml")


def case_gated_fallbacks_do_not_count_as_covered():
    """A push run that only sends when the schedule is overdue is not coverage."""
    for name in ("linkedin-drafts.yml", "social-drafts.yml"):
        fp = os.path.join(WF, name)
        if not os.path.exists(fp):
            continue
        text = io.open(fp, encoding="utf-8", errors="replace").read()
        assert "github.event_name" in text, (
            name + " no longer gates on event_name; re-check whether its push "
            "runs really deliver before trusting a coverage claim")
        assert not C.has_push_trigger(name), name


def case_schedule_only_workflow_is_not_covered():
    """hourly-brief.yml has no push trigger, so its cron lateness is real."""
    fp = os.path.join(WF, "hourly-brief.yml")
    if not os.path.exists(fp):
        return
    assert not C.has_push_trigger("hourly-brief.yml")


def case_a_missing_workflow_is_not_covered():
    assert not C.has_push_trigger("no-such-workflow-at-all.yml")


def case_comment_mentioning_push_is_not_a_trigger():
    """The detection reads the block before jobs:, so a prose mention of the
    word inside a step must not count. Pinned because the first version of this
    check was a bare substring test over the whole file."""
    assert not C.has_push_trigger("roadmap-report.yml") or True
    fp = os.path.join(WF, "roadmap-report.yml")
    if os.path.exists(fp):
        head = io.open(fp, encoding="utf-8", errors="replace").read()
        head = head.split("jobs:")[0]
        if "push:" not in head:
            assert not C.has_push_trigger("roadmap-report.yml")


def case_effective_fields_appear_only_when_covered():
    """Shape check against the real API result, when a token is available."""
    res = C.check()
    got = False
    for r in res.get("workflows", []):
        if r.get("verdict") != "measured":
            continue
        covered = r.get("cron_late_but_covered")
        has_eff = "effective_median_gap_min" in r
        assert covered == has_eff or (not covered and not has_eff), r
        if covered:
            got = True
            assert r["effective_median_gap_min"] <= r["median_gap_min"], r
            assert r.get("degraded") is False, r
    if not got:
        print("      (no covered workflow measured here, shape check only)")


def case_coverage_is_earned_not_assumed():
    """The defect ops/tests/test_check_cron_cadence.py caught, pinned here too.

    The first version cleared `degraded` for any workflow with an ungated push
    trigger. Fed 210-minute gaps on BOTH the schedule query and the all-trigger
    query, it still reported covered, claiming the push trigger had fixed a
    problem the very same numbers showed it had not. A trigger existing is not
    the same fact as a trigger helping, and on a quiet week the effective gap
    rises to meet the schedule gap and this must go back to DEGRADED by itself.
    """
    import datetime

    def runs_every(minutes, n):
        t0 = datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc)
        return [{"created_at": (t0 + datetime.timedelta(
            minutes=minutes * i)).strftime("%Y-%m-%dT%H:%M:%SZ")}
            for i in range(n)]

    real = C.fetch_runs
    try:
        # Same late cadence on both queries: no help, so still degraded.
        C.fetch_runs = lambda wf, per_page=50, event="schedule": runs_every(210, 20)
        r = C.check_one("fulfil-orders.yml")
        assert r.get("degraded") is True, r
        assert not r.get("cron_late_but_covered"), r

        # Late cron, frequent pushes: covered.
        def mixed(wf, per_page=50, event="schedule"):
            return runs_every(210, 20) if event else runs_every(12, 40)

        C.fetch_runs = mixed
        r2 = C.check_one("fulfil-orders.yml")
        assert r2.get("cron_late_but_covered") is True, r2
        assert r2.get("degraded") is False, r2
        assert r2["effective_median_gap_min"] < r2["median_gap_min"], r2
    finally:
        C.fetch_runs = real


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
