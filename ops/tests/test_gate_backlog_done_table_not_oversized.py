#!/usr/bin/env python3
"""
Prove gate_backlog_done_table_not_oversized() can actually fail (warn) on
a real oversized "Done this week" table and stays silent on a table
already within the buffered retention window. A gate that cannot go red
is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_backlog_done_table_not_oversized.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import rotate_backlog as rb                                     # noqa: E402

PREFIX = "# Backlog\n\n## 0. Some live section\n\nnothing rotated here.\n\n"
SUFFIX = "\n\n---\n\n## 1b. Next live section\n\nalso untouched.\n"


def _table(rows_md):
    return (PREFIX + rb.SECTION_HEADING + "\n\n" + rb.TABLE_HEADER + "\n"
            + rb.TABLE_SEP + "\n" + "\n".join(rows_md) + SUFFIX)


def _row(date_str, label):
    return "| **%s, done %s.** | evidence for %s |" % (label, date_str, label)


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_backlog_done_table_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A table with a row well past the buffered window (retention 14 +
    #    7 day buffer = 21 days) must warn. This is the real defect found
    #    2026-10-23: nothing before this gate ever caught it.
    stale_text = _table([_row(d(40), "long overdue")])
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_backlog_done_table_not_oversized() should "
                      "WARN, not FAIL, on an oversized table: %r" % (fails1,))
    if not any(g == "backlog-done-table-not-oversized" for g, _ in warns1):
        fails.append("gate did not warn on a table with a 40-day-old "
                      "row: %r" % (warns1,))

    # 2. A table entirely within the buffered window stays silent.
    fresh_text = _table([_row(d(1), "recent")])
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "backlog-done-table-not-oversized"
                      for g, _ in warns2):
        fails.append("gate warned on a table with nothing past the "
                      "buffered window: fails=%r warns=%r" % (fails2, warns2))

    # 3. A row just inside the buffer (retention + buffer, minus a day)
    #    must not warn: the buffer exists specifically so rotation does
    #    not need to run the instant a row crosses the bare 14-day line.
    buffered_text = _table([_row(d(20), "inside the buffer")])
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "backlog-done-table-not-oversized"
                      for g, _ in warns3):
        fails.append("gate warned on a row still inside the retention+"
                      "buffer window: fails=%r warns=%r" % (fails3, warns3))

    # 4. No BACKLOG-2026-09-07.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        old_root = preflight.ROOT
        preflight.ROOT = tmp4
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_backlog_done_table_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no BACKLOG-2026-09-07.md "
                         "present: %r" % (exc,))
        finally:
            preflight.ROOT = old_root

    # 5. A file present but missing the expected table anchors (e.g. mid-
    #    edit, or a different document entirely): must not crash.
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, "# Not the real shape\n\nbody\n")
    if fails5 or warns5:
        fails.append("gate did not stay silent on an unrecognisable file "
                      "shape: fails=%r warns=%r" % (fails5, warns5))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_done_table_not_oversized, fail-then-pass "
          "proved, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
