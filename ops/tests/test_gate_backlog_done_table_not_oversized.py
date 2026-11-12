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

    # 1. A table with a row well past the buffered window (retention +
    #    7 day buffer) must warn. This is the real defect found
    #    2026-10-23: nothing before this gate ever caught it. Offset is
    #    relative to rb.DEFAULT_RETENTION_DAYS, not hardcoded, so this
    #    stays correct however that constant is tuned later.
    buffer_days = rb.DEFAULT_RETENTION_DAYS + 7
    stale_text = _table([_row(d(buffer_days + 19), "long overdue")])
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
    #    not need to run the instant a row crosses the retention line.
    buffered_text = _table([_row(d(buffer_days - 1), "inside the buffer")])
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "backlog-done-table-not-oversized"
                      for g, _ in warns3):
        fails.append("gate warned on a row still inside the retention+"
                      "buffer window: fails=%r warns=%r" % (fails3, warns3))

    # 3b. All-today table, nothing overdue by date, but past the buffered
    #     row cap (DEFAULT_MAX_ROWS + 10): must warn on the row-count
    #     trigger alone. Found 2026-11-12: a purely date-based check
    #     stayed silent on exactly this real shape (28 same-day rows,
    #     9155 bytes over the live-docs size tripwire).
    buffered_rows = rb.DEFAULT_MAX_ROWS + 10
    many_today_rows = [_row(d(0), "today-%d" % i)
                        for i in range(buffered_rows + 3)]
    many_today_text = _table(many_today_rows)
    with tempfile.TemporaryDirectory() as tmp3b:
        fails3b, warns3b = _run_gate(tmp3b, many_today_text)
    if fails3b:
        fails.append("gate should WARN, not FAIL, on an all-today "
                      "over-cap table: %r" % (fails3b,))
    if not any(g == "backlog-done-table-not-oversized" for g, _ in warns3b):
        fails.append("gate did not warn on an all-today table past the "
                      "buffered row cap: %r" % (warns3b,))

    # 3c. An all-today table at or under the buffered row cap stays
    #     silent (the buffer exists so a normal day's cadence does not
    #     fire this the moment it crosses DEFAULT_MAX_ROWS itself).
    few_today_rows = [_row(d(0), "today-%d" % i) for i in range(buffered_rows)]
    few_today_text = _table(few_today_rows)
    with tempfile.TemporaryDirectory() as tmp3c:
        fails3c, warns3c = _run_gate(tmp3c, few_today_text)
    if fails3c or any(g == "backlog-done-table-not-oversized"
                       for g, _ in warns3c):
        fails.append("gate warned on an all-today table still inside the "
                      "buffered row cap: fails=%r warns=%r"
                      % (fails3c, warns3c))

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
          "proved, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
