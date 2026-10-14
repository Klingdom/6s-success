#!/usr/bin/env python3
"""
Prove gate_nightly_log_not_oversized() can actually fail (warn) on a real
oversized log and stays silent on a log already within the buffered
retention window. A gate that cannot go red is theatre (ops/preflight.py's
own stated rule).

Run:  python ops/tests/test_gate_nightly_log_not_oversized.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

HEADER = "# Nightly log\n\nOne entry per unattended pass, newest first. Written to be read half awake.\n"


def _run_gate(tmp, log_text):
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir, exist_ok=True)
    io.open(os.path.join(ops_dir, "NIGHTLY-LOG.md"), "w", encoding="utf-8").write(log_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_nightly_log_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A log with an entry well past the buffered window (retention 14
    #    + 7 day buffer = 21 days) must warn. This is the real defect
    #    found 2026-10-14: nothing before this gate ever caught it.
    stale_text = HEADER + "\n" + "## %s, long overdue\n\nbody\n" % d(40)
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_nightly_log_not_oversized() should WARN, not "
                      "FAIL, on an oversized log: %r" % (fails1,))
    if not any(g == "nightly-log-not-oversized" for g, _ in warns1):
        fails.append("gate_nightly_log_not_oversized() did not warn on a "
                      "log with a 40-day-old entry: %r" % (warns1,))

    # 2. A log entirely within the buffered window stays silent.
    fresh_text = HEADER + "\n" + "## %s, recent\n\nbody\n" % d(1)
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "nightly-log-not-oversized" for g, _ in warns2):
        fails.append("gate_nightly_log_not_oversized() warned on a log "
                      "with nothing past the buffered window: fails=%r "
                      "warns=%r" % (fails2, warns2))

    # 3. A log with an old entry just inside the buffer (retention +
    #    buffer, minus a day) must not warn: the buffer exists specifically
    #    so rotation does not need to run the instant an entry crosses the
    #    bare 14-day retention line.
    buffered_text = HEADER + "\n" + "## %s, inside the buffer\n\nbody\n" % d(20)
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "nightly-log-not-oversized" for g, _ in warns3):
        fails.append("gate_nightly_log_not_oversized() warned on an entry "
                      "still inside the retention+buffer window: fails=%r "
                      "warns=%r" % (fails3, warns3))

    # 4. No ops/NIGHTLY-LOG.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        os.makedirs(os.path.join(tmp4, "ops"), exist_ok=True)
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_nightly_log_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no NIGHTLY-LOG.md present: %r" % (exc,))
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_nightly_log_not_oversized, fail-then-pass proved, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
