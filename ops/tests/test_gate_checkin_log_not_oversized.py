#!/usr/bin/env python3
"""
Prove gate_checkin_log_not_oversized() can actually fail (warn) on a real
oversized log and stays silent on a log already within the buffered
retention window. A gate that cannot go red is theatre (ops/preflight.py's
own stated rule).

Run:  python ops/tests/test_gate_checkin_log_not_oversized.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

HEADER = ("# Hourly check-in log\n\n"
          "What moved, what did not, and what is next. Written by "
          "ops/checkin.py so the record is measured rather than remembered.\n")


def _run_gate(tmp, log_text):
    io.open(os.path.join(tmp, "CHECKIN-LOG.md"), "w", encoding="utf-8").write(log_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_checkin_log_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A log with an entry well past the buffered window (retention 30
    #    + 7 day buffer = 37 days) must warn. This is the real defect
    #    found 2026-10-23: nothing before this gate ever caught it.
    stale_text = HEADER + "\n" + "## %s 09:00\n\nbody\n" % d(60)
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_checkin_log_not_oversized() should WARN, not "
                      "FAIL, on an oversized log: %r" % (fails1,))
    if not any(g == "checkin-log-not-oversized" for g, _ in warns1):
        fails.append("gate_checkin_log_not_oversized() did not warn on a "
                      "log with a 60-day-old entry: %r" % (warns1,))

    # 2. A log entirely within the buffered window stays silent.
    fresh_text = HEADER + "\n" + "## %s 09:00\n\nbody\n" % d(1)
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "checkin-log-not-oversized" for g, _ in warns2):
        fails.append("gate_checkin_log_not_oversized() warned on a log "
                      "with nothing past the buffered window: fails=%r "
                      "warns=%r" % (fails2, warns2))

    # 3. A log with an old entry just inside the buffer (retention +
    #    buffer, minus a day) must not warn.
    buffered_text = HEADER + "\n" + "## %s 09:00\n\nbody\n" % d(36)
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "checkin-log-not-oversized" for g, _ in warns3):
        fails.append("gate_checkin_log_not_oversized() warned on an entry "
                      "still inside the retention+buffer window: fails=%r "
                      "warns=%r" % (fails3, warns3))

    # 4. No CHECKIN-LOG.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_checkin_log_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no CHECKIN-LOG.md present: %r" % (exc,))
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_checkin_log_not_oversized, fail-then-pass proved, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
