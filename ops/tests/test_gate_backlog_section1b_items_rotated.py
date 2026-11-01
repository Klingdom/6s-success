#!/usr/bin/env python3
"""
Prove gate_backlog_section1b_items_rotated() can actually fail (warn) on
a real oversized set of section-1b resolved/done/closed paragraph
groups and stays silent when nothing is past the buffered retention
window. A gate that cannot go red is theatre (ops/preflight.py's own
stated rule).

Run:  python ops/tests/test_gate_backlog_section1b_items_rotated.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                 # noqa: E402

PREFIX = "# Backlog\n\n## 1. Done this week, for the record\n\nnothing.\n\n---\n\n"
HEADER = "## 1b. Measured this week, awaiting a decision\n\n"
NEXT_SECTION = "\n---\n\n## 2. Now: micro zones and the web app\n\nnothing here.\n"


def _group(date_str, body, n_continuations=0):
    lead = "RESOLVED %s, operator: a short summary." % date_str
    out = "**%s** %s\n\n" % (lead, body)
    for i in range(n_continuations):
        out += "**A continuation paragraph %d.** More narrative.\n\n" % i
    return out


def _file(groups_md):
    return PREFIX + HEADER + "".join(groups_md) + NEXT_SECTION


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_backlog_section1b_items_rotated()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A dated group well past the buffered window (retention 14 + 7
    #    day buffer = 21 days) must warn.
    stale_text = _file([_group(d(40), "a long narrative body " * 20,
                                n_continuations=2)])
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_backlog_section1b_items_rotated() should "
                      "WARN, not FAIL, on an oversized file: %r" % (fails1,))
    if not any(g == "backlog-section1b-items-rotated" for g, _ in warns1):
        fails.append("gate did not warn on a group 40 days old: %r"
                      % (warns1,))

    # 2. A file entirely within the buffered window stays silent.
    fresh_text = _file([_group(d(1), "a recent narrative body")])
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "backlog-section1b-items-rotated"
                      for g, _ in warns2):
        fails.append("gate warned on a file with nothing past the "
                      "buffered window: fails=%r warns=%r" % (fails2, warns2))

    # 3. A group just inside the buffer (retention + buffer, minus a
    #    day) must not warn.
    buffered_text = _file([_group(d(20), "inside the buffer")])
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "backlog-section1b-items-rotated"
                      for g, _ in warns3):
        fails.append("gate warned on a group inside the retention "
                      "buffer: fails=%r warns=%r" % (fails3, warns3))

    # 4. A mix: one group overdue, one recent. Must warn.
    mixed_text = _file([_group(d(40), "overdue"), _group(d(1), "recent")])
    with tempfile.TemporaryDirectory() as tmp4:
        fails4, warns4 = _run_gate(tmp4, mixed_text)
    if fails4:
        fails.append("gate FAILed instead of WARNed on a mixed file: %r"
                      % (fails4,))
    if not any(g == "backlog-section1b-items-rotated" for g, _ in warns4):
        fails.append("gate did not warn on a file with one overdue "
                      "group among two: %r" % (warns4,))

    # 5. A freshly rotated file (pointer paragraphs only, no dated
    #    groups left) stays silent, confirming this gate recognises its
    #    own tool's output rather than re-flagging it.
    rotated_text = _file([
        "**RESOLVED %s, operator: a short summary.** Archived; see "
        "`BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md`.\n\n" % d(40)])
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
    print("OK: gate_backlog_section1b_items_rotated, fail-then-pass "
          "proved, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
