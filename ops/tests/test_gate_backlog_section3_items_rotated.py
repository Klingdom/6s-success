#!/usr/bin/env python3
"""
Prove gate_backlog_section3_items_rotated() can actually fail (warn) on
a real oversized set of section-3 "B<N>, date, ..." journal rows and
stays silent when nothing is past the buffered retention window. Also
proves the tool's real reason for existing: a bare bold paragraph with
no leading pipe is matched and archived too, not just ordinary table
rows. A gate that cannot go red is theatre (ops/preflight.py's own
stated rule).

Run:  python ops/tests/test_gate_backlog_section3_items_rotated.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                 # noqa: E402

PREFIX = "# Backlog\n\n## 2. Now: micro zones and the web app\n\nnothing.\n\n---\n\n"
HEADER = "## 3. Now: decks\n\n"
TABLE_HEAD = ("| # | Item | Why now | Effort | Accept when |\n"
              "|---|---|---|---|---|\n")
POINTERS = "".join(
    "| **B%d** | ~~title~~ | Archived; see `BACKLOG-2026-09-07-ITEMS-"
    "ARCHIVE.md`. |\n" % n for n in range(1, 5))
NEXT_SECTION = "\n---\n\n## 4. Now: images and video\n\nnothing here either.\n"


def _piped_row(id_, date_str, body):
    return "| **%s, %s, operator.** %s |\n" % (id_, date_str, body)


def _bare_row(id_, date_str, body):
    return "**%s, %s, operator.** %s\n" % (id_, date_str, body)


def _file(rows_md):
    return (PREFIX + HEADER + TABLE_HEAD + POINTERS + "".join(rows_md)
            + NEXT_SECTION)


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_backlog_section3_items_rotated()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A dated, piped row well past the buffered window (retention
    #    14 + 7 day buffer = 21 days) must warn.
    stale_text = _file([_piped_row("B5", d(40), "a long narrative body " * 20)])
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_backlog_section3_items_rotated() should WARN, "
                      "not FAIL, on an oversized file: %r" % (fails1,))
    if not any(g == "backlog-section3-items-rotated" for g, _ in warns1):
        fails.append("gate did not warn on a piped row 40 days old: %r"
                      % (warns1,))

    # 2. The real reason this tool exists: a BARE bold paragraph, no
    #    leading pipe, carrying the same id as an already-archived
    #    table row, must also be caught.
    bare_stale_text = _file([_bare_row("B1 follow-on", d(40),
                                        "a long narrative body " * 20)])
    with tempfile.TemporaryDirectory() as tmp_bare:
        fails_bare, warns_bare = _run_gate(tmp_bare, bare_stale_text)
    if fails_bare:
        fails.append("gate should WARN, not FAIL, on a stale bare "
                      "paragraph row: %r" % (fails_bare,))
    if not any(g == "backlog-section3-items-rotated" for g, _ in warns_bare):
        fails.append("gate did not warn on a bare (no-leading-pipe) "
                      "paragraph row 40 days old: %r" % (warns_bare,))

    # 3. A file entirely within the buffered window stays silent.
    fresh_text = _file([_piped_row("B5", d(1), "a recent narrative body")])
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "backlog-section3-items-rotated"
                      for g, _ in warns2):
        fails.append("gate warned on a file with nothing past the "
                      "buffered window: fails=%r warns=%r" % (fails2, warns2))

    # 4. A row just inside the buffer (retention + buffer, minus a day)
    #    must not warn.
    buffered_text = _file([_piped_row("B5", d(20), "inside the buffer")])
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "backlog-section3-items-rotated"
                      for g, _ in warns3):
        fails.append("gate warned on a row inside the retention buffer: "
                      "fails=%r warns=%r" % (fails3, warns3))

    # 5. A mix: one piped row overdue, one bare row recent. Must warn,
    #    and must not treat the dateless B1-B4 pointer rows as overdue.
    mixed_text = _file([_piped_row("B5", d(40), "overdue"),
                         _bare_row("B6 follow-on", d(1), "recent")])
    with tempfile.TemporaryDirectory() as tmp4:
        fails4, warns4 = _run_gate(tmp4, mixed_text)
    if fails4:
        fails.append("gate FAILed instead of WARNed on a mixed file: %r"
                      % (fails4,))
    if not any(g == "backlog-section3-items-rotated" for g, _ in warns4):
        fails.append("gate did not warn on a file with one overdue row "
                      "among two: %r" % (warns4,))

    # 6. A freshly rotated file (pointer rows only, no dated rows left)
    #    stays silent, confirming this gate recognises its own tool's
    #    output rather than re-flagging it.
    rotated_text = _file([])
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, rotated_text)
    if fails5 or warns5:
        fails.append("gate did not stay silent on a fully rotated file: "
                      "fails=%r warns=%r" % (fails5, warns5))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_section3_items_rotated, fail-then-pass "
          "proved, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
