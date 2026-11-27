#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nightly_log_cycle_saturation() (via its pure
logic, nightly_log_cycle_saturation()) can actually warn when today's
ops/NIGHTLY-LOG.md entries are mostly no-op "exhausted, no new work"
cycles, and stays quiet when they are not.

Found live 2026-11-27: a single calendar day had already produced over 40
log entries by mid-afternoon, roughly 30 of which independently
reconfirmed the same "backlog is exhausted" conclusion. Nothing mechanical
surfaced that pattern; a reader had to count by hand. This test proves the
gate's pure logic on synthetic entries, never the real 15,000+ line file,
so it stays fast and so it cannot pass by accident against whatever the
real log happens to contain today.

Run: python ops/tests/test_gate_nightly_log_cycle_saturation.py
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

NOW = dt.datetime(2026, 11, 27, 15, 0, 0, tzinfo=dt.timezone.utc)
TODAY = "2026-11-27"
YESTERDAY = "2026-11-26"


def no_op_entry(date: str, slot: str) -> str:
    return (
        "## %s, PM check-in (~%s slot): previous work confirmed finished, "
        "independently reconfirmed exhausted, no new work\n\n"
        "Nothing genuinely unblocked beyond the standing queue.\n\n"
        "HANDOFF-FILES: none\n" % (date, slot))


def real_work_entry(date: str, slot: str, what: str) -> str:
    return (
        "## %s, scheduled operator cycle (~%s slot): %s\n\n"
        "Shipped and verified, full account below.\n\n"
        "HANDOFF-FILES: none\n" % (date, slot, what))


def main() -> int:
    fails = []

    # 1. Eight consecutive no-op entries dated today: must warn, and the
    #    message must name the real count (8 of 8).
    log = "".join(no_op_entry(TODAY, "%02dx" % i) for i in range(8))
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if not problem or "8 of the 8" not in problem or TODAY not in problem:
        fails.append("8 consecutive no-op entries did not warn: %r" % problem)

    # 2. Seven consecutive no-op entries: below the threshold of 8, must
    #    NOT warn.
    log = "".join(no_op_entry(TODAY, "%02dx" % i) for i in range(7))
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if problem:
        fails.append("7 consecutive no-op entries wrongly warned: %r" % problem)

    # 3. Mostly real-work entries, dated today: must NOT warn even though
    #    there are many of them.
    log = "".join(
        real_work_entry(TODAY, "%02dx" % i, "closed a real content gap, done")
        for i in range(10))
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if problem:
        fails.append("real-work entries wrongly warned: %r" % problem)

    # 4. A mix: 9 no-op entries today, interleaved with 3 real-work
    #    entries today, then entries rolling over into yesterday that are
    #    also no-op-phrased. Only today's entries should count, and the
    #    real count must be 9 no-op of 12 total today, not inflated by
    #    yesterday's entries past the date rollover.
    todays = []
    for i in range(12):
        if i % 4 == 3:
            todays.append(real_work_entry(TODAY, "%02dx" % i, "shipped a fix"))
        else:
            todays.append(no_op_entry(TODAY, "%02dx" % i))
    yesterdays = "".join(no_op_entry(YESTERDAY, "%02dx" % i) for i in range(10))
    log = "".join(todays) + yesterdays
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if not problem or "9 of the 12" not in problem:
        fails.append("mixed day with rollover gave wrong count: %r" % problem)

    # 5. The newest entry omits an explicit date (a real, recurring shape
    #    in this file). It must be treated as today's, so a run of
    #    dateless no-op entries at the top still counts toward today.
    dateless_no_op = (
        "## PM check-in (~%s slot): previous work confirmed finished, "
        "independently reconfirmed exhausted, no new work\n\n"
        "HANDOFF-FILES: none\n")
    log = "".join(dateless_no_op % ("%02dx" % i) for i in range(8))
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if not problem or "8 of the 8" not in problem:
        fails.append("dateless newest entries not treated as today: %r" % problem)

    # 6. An empty log: must NOT warn (nothing to classify).
    problem = preflight.nightly_log_cycle_saturation("", NOW, threshold=8)
    if problem:
        fails.append("empty log wrongly warned: %r" % problem)

    # 7. Today's entries are all real work, followed by yesterday's being
    #    heavily no-op: yesterday's count must never leak into today's
    #    figure.
    log = "".join(
        real_work_entry(TODAY, "%02dx" % i, "fixed a real defect")
        for i in range(3))
    log += "".join(no_op_entry(YESTERDAY, "%02dx" % i) for i in range(20))
    problem = preflight.nightly_log_cycle_saturation(log, NOW, threshold=8)
    if problem:
        fails.append("yesterday's no-op entries leaked into today: %r" % problem)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 7/7 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
