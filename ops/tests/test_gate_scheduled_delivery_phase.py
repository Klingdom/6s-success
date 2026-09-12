#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_scheduled_delivery_phase() tells an overdue
cron miss apart from a schedule that simply has not had its first chance
yet, and displays the workflow's last-changed time in UTC.

Found live 2026-09-12: linkedin-drafts.yml's cron changed and, hours later,
still had zero scheduled runs recorded against it. The gate's only message
for "fewer than 3 fresh runs" was "NOT YET VERIFIED. Re-check once it has
run a few times," worded identically whether the change was one minute old
or well past its own due time with nothing landed. Reading that message
this cycle, the workflow's last-changed timestamp was printed as
"2026-09-11T09:11" with no timezone, which is `git log --format=%cI`'s own
committer-local offset (Denver, -06:00), silently truncated. Next to a
message stating every other time in UTC, that reads as UTC and is off by
up to 6 hours: this operator briefly concluded a real miss where none
existed, because the change actually landed at 15:11 UTC, after that day's
10:47 UTC cron opportunity had already passed.

Two fixes, two things to prove:
  1. `check_cron_cadence.most_recent_due()` finds the latest scheduled
     moment at or before now, and the gate only calls a workflow overdue
     when that moment falls AFTER the change and more than a grace period
     in the past with zero fresh runs. A due moment before the change (the
     real shape found live) must never be flagged as missed.
  2. The gate's printed "changed at ..." timestamp is always UTC, not the
     committer's local offset.

Run:  python ops/tests/test_gate_scheduled_delivery_phase.py
"""
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import check_cron_cadence as CC                                 # noqa: E402

WF = "linkedin-drafts.yml"


def run_gate_for(changed_iso, fetch_runs_result, times=((10, 47),),
                  landing=(14, 19)):
    """Call gate_scheduled_delivery_phase with everything but WF stubbed out."""
    real = {
        "WORKFLOWS": CC.WORKFLOWS,
        "intended_landing": CC.intended_landing,
        "scheduled_times": CC.scheduled_times,
        "fetch_runs": CC.fetch_runs,
        "last_changed": CC.last_changed,
    }
    CC.WORKFLOWS = [WF]
    CC.intended_landing = lambda wf: landing
    CC.scheduled_times = lambda wf: list(times)
    CC.fetch_runs = lambda wf, per_page=50: fetch_runs_result
    CC.last_changed = lambda wf: changed_iso
    preflight.WARN.clear()
    try:
        preflight.gate_scheduled_delivery_phase()
    finally:
        for k, v in real.items():
            setattr(CC, k, v)
    return [m for g, m in preflight.WARN if g == "delivery-phase"]


def main() -> int:
    fails = []
    now = datetime.datetime.now(datetime.timezone.utc)

    # Case 1: the exact live shape that must NOT be flagged as missed. The
    # cron changed at 15:11 UTC, after that day's 10:47 UTC opportunity, so
    # the next real due moment is tomorrow's 10:47 and has not arrived yet.
    changed = (now - datetime.timedelta(hours=1)).replace(
        hour=15, minute=11, second=0, microsecond=0).isoformat()
    old_run = {"created_at": (now - datetime.timedelta(days=5))
               .strftime("%Y-%m-%dT%H:%M:%SZ")}
    msgs = run_gate_for(changed, [old_run])
    if not msgs or any("MISSED" in m for m in msgs):
        fails.append(f"a change landing after its own day's cron slot must "
                     f"not read as a missed fire, got {msgs}")
    if not any("NOT YET VERIFIED" in m for m in msgs):
        fails.append(f"that case should still say NOT YET VERIFIED, got {msgs}")

    # Case 2: a due moment well after the change, long past, with zero
    # fresh runs: a genuine miss, and must say so plainly.
    changed_2 = (now - datetime.timedelta(hours=20)).isoformat()
    msgs2 = run_gate_for(changed_2, [old_run])
    if not any("MISSED" in m for m in msgs2):
        fails.append(f"a due moment 20h after the change with zero fresh "
                     f"runs must be flagged MISSED, got {msgs2}")

    # Case 3: the change happened minutes ago, nothing due yet: must read as
    # the routine, unescalated message, not a miss.
    changed_3 = (now - datetime.timedelta(minutes=5)).isoformat()
    msgs3 = run_gate_for(changed_3, [old_run])
    if any("MISSED" in m for m in msgs3):
        fails.append(f"a change made 5 minutes ago must never read as a "
                     f"missed fire, got {msgs3}")
    if not any("NOT YET VERIFIED" in m for m in msgs3):
        fails.append(f"a fresh change with no due moment yet should say "
                     f"NOT YET VERIFIED, got {msgs3}")

    # Case 4: the "changed at" timestamp in the message is always UTC, not
    # the committer's local offset, even when the source carries one.
    changed_4 = "2026-09-11T09:11:54-06:00"
    msgs4 = run_gate_for(changed_4, [old_run])
    if not any("2026-09-11T15:11 UTC" in m for m in msgs4):
        fails.append(f"a -06:00 offset changed-at time must display "
                     f"converted to UTC (15:11), got {msgs4}")
    if any("09-11T09:11" in m for m in msgs4):
        fails.append(f"the raw local-offset hour must not appear in the "
                     f"message, got {msgs4}")

    # Case 5: most_recent_due itself, the piece both fixes depend on.
    due = CC.most_recent_due([(10, 47)],
                             now=datetime.datetime(2026, 9, 12, 4, 50,
                                                    tzinfo=datetime.timezone.utc))
    if due != datetime.datetime(2026, 9, 11, 10, 47,
                                tzinfo=datetime.timezone.utc):
        fails.append(f"most_recent_due should find yesterday's 10:47 UTC "
                     f"when now is 04:50 UTC the next day, got {due}")

    total = 6
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
