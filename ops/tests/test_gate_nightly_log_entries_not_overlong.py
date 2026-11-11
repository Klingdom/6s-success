#!/usr/bin/env python3
"""
Prove gate_nightly_log_entries_not_overlong() can actually fail (warn) on
a real overlong entry, and stays silent both on a short recent entry and
on a long entry that is already outside the retention+buffer window. A
gate that cannot go red is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_nightly_log_entries_not_overlong.py
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
        preflight.gate_nightly_log_entries_not_overlong()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731
    long_body = " ".join(["word"] * 900)

    # 1. A recent entry well past the 750-word threshold must warn. This
    #    is the real defect found 2026-11-11: room-guide keyword-mining
    #    entries routinely ran 1,500-6,000+ words against a 250-word
    #    budget, and nothing before this gate ever caught it.
    overlong_text = HEADER + "\n" + "## %s, scheduled operator cycle\n\n%s\n" % (d(0), long_body)
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, overlong_text)
    if fails1:
        fails.append("gate_nightly_log_entries_not_overlong() should WARN, "
                      "not FAIL, on an overlong entry: %r" % (fails1,))
    if not any(g == "nightly-log-entries-not-overlong" for g, _ in warns1):
        fails.append("gate_nightly_log_entries_not_overlong() did not warn "
                      "on a 900-word recent entry: %r" % (warns1,))

    # 2. A short recent entry, well inside budget, stays silent.
    short_text = HEADER + "\n" + "## %s, scheduled operator cycle\n\n**Did:** a short entry, well inside budget.\n" % d(0)
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, short_text)
    if fails2 or any(g == "nightly-log-entries-not-overlong" for g, _ in warns2):
        fails.append("gate_nightly_log_entries_not_overlong() warned on a "
                      "short recent entry: fails=%r warns=%r" % (fails2, warns2))

    # 3. A long entry that is already outside the retention+buffer window
    #    (21 days) stays silent: this gate is about new entries, not a
    #    second pass over history gate_nightly_log_not_oversized and
    #    ops/rotate_nightly_log.py already own.
    old_overlong_text = HEADER + "\n" + "## %s, long overdue and overlong\n\n%s\n" % (d(40), long_body)
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, old_overlong_text)
    if fails3 or any(g == "nightly-log-entries-not-overlong" for g, _ in warns3):
        fails.append("gate_nightly_log_entries_not_overlong() warned on an "
                      "overlong entry already outside the buffered window: "
                      "fails=%r warns=%r" % (fails3, warns3))

    # 4. No ops/NIGHTLY-LOG.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        os.makedirs(os.path.join(tmp4, "ops"), exist_ok=True)
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_nightly_log_entries_not_overlong()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no NIGHTLY-LOG.md present: %r" % (exc,))
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_nightly_log_entries_not_overlong, fail-then-pass proved, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
