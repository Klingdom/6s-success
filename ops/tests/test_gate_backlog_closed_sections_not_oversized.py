#!/usr/bin/env python3
"""
Prove gate_backlog_closed_sections_not_oversized() can actually fail
(warn) on a real oversized set of numbered "## N. Closed/Done ..."
sections and stays silent when nothing is past the buffered retention
window. A gate that cannot go red is theatre (ops/preflight.py's own
stated rule).

Run:  python ops/tests/test_gate_backlog_closed_sections_not_oversized.py
"""
import datetime
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
import rotate_backlog_closed as rbc                              # noqa: E402

PREFIX = (
    "# Backlog\n\n## 7. What I would tell you if you only read one line\n\n"
    "nothing rotated here.\n\n---\n\n"
)


def _section(num, date_str, title):
    return "## %d. Closed %s: %s\n\nbody text for section %d.\n\n---\n\n" \
        % (num, date_str, title, num)


def _file(sections_md):
    return PREFIX + "".join(sections_md)


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_backlog_closed_sections_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. A section well past the buffered window (retention 14 + 7 day
    #    buffer = 21 days) must warn.
    stale_text = _file([_section(8, d(40), "long overdue")])
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate_backlog_closed_sections_not_oversized() should "
                      "WARN, not FAIL, on an oversized file: %r" % (fails1,))
    if not any(g == "backlog-closed-sections-not-oversized"
               for g, _ in warns1):
        fails.append("gate did not warn on a section 40 days old: %r"
                      % (warns1,))

    # 2. A file entirely within the buffered window stays silent.
    fresh_text = _file([_section(8, d(1), "recent")])
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, fresh_text)
    if fails2 or any(g == "backlog-closed-sections-not-oversized"
                      for g, _ in warns2):
        fails.append("gate warned on a file with nothing past the "
                      "buffered window: fails=%r warns=%r" % (fails2, warns2))

    # 3. A section just inside the buffer (retention + buffer, minus a
    #    day) must not warn: the buffer exists specifically so rotation
    #    does not need to run the instant a section crosses the bare
    #    14-day line.
    buffered_text = _file([_section(8, d(20), "inside the buffer")])
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, buffered_text)
    if fails3 or any(g == "backlog-closed-sections-not-oversized"
                      for g, _ in warns3):
        fails.append("gate warned on a section inside the retention "
                      "buffer: fails=%r warns=%r" % (fails3, warns3))

    # 4. A mix: one section overdue, one recent. Must warn, counting only
    #    the overdue one, and must not crash on sections 2-7 numbering
    #    (not touched by this gate at all).
    mixed_text = _file([_section(8, d(40), "overdue"),
                         _section(9, d(1), "recent")])
    with tempfile.TemporaryDirectory() as tmp4:
        fails4, warns4 = _run_gate(tmp4, mixed_text)
    if fails4:
        fails.append("gate FAILed instead of WARNed on a mixed file: %r"
                      % (fails4,))
    if not any(g == "backlog-closed-sections-not-oversized"
               for g, _ in warns4):
        fails.append("gate did not warn on a file with one overdue "
                      "section among two: %r" % (warns4,))

    # 5. A file present but with no numbered sections at all (e.g.
    #    mid-edit, or a different document entirely): must not crash.
    with tempfile.TemporaryDirectory() as tmp5:
        fails5, warns5 = _run_gate(tmp5, "# Not the real shape\n\nbody\n")
    if fails5 or warns5:
        fails.append("gate did not stay silent on a file with no "
                      "numbered sections: fails=%r warns=%r"
                      % (fails5, warns5))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_closed_sections_not_oversized, fail-then-pass "
          "proved, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
