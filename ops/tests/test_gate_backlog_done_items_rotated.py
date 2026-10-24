#!/usr/bin/env python3
"""
Prove gate_backlog_done_items_rotated() can actually fail (warn) on an
unrotated whitelisted row and stays silent on a freshly rotated one, on
a row restructured out from under the tool, and on a file with none of
the 17 whitelisted ids present at all. A gate that cannot go red is
theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_backlog_done_items_rotated.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

PREFIX = "# Backlog\n\n## 1. Done this week\n\nnothing here.\n\n"
SUFFIX = "\n## 5. Hold\n\nnothing here either.\n"


def _file(body):
    return PREFIX + "## 2. Now: micro zones and the web app\n\n" + body + SUFFIX


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "BACKLOG-2026-09-07.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_backlog_done_items_rotated()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []

    # 1. A whitelisted row still carrying its original narrative must
    #    warn, not fail.
    unrotated = _file(
        "| **A1** | ~~Build the thing~~ | why | effort | a long "
        "accept-when narrative that should have moved to the archive "
        "by now |\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        f1, w1 = _run_gate(tmp, unrotated)
    if f1:
        fails.append("gate should WARN, not FAIL, on an unrotated row: "
                      "%r" % (f1,))
    if not any(g == "backlog-done-items-rotated" for g, _ in w1):
        fails.append("gate did not warn on an unrotated whitelisted "
                      "row: %r" % (w1,))

    # 2. A freshly rotated row (pointer text in the rest-cell) stays
    #    silent.
    rotated = _file(
        "| **A1** | ~~Build the thing~~ | Archived; see "
        "`BACKLOG-2026-09-07-ITEMS-ARCHIVE.md`. |\n"
    )
    with tempfile.TemporaryDirectory() as tmp2:
        f2, w2 = _run_gate(tmp2, rotated)
    if f2 or any(g == "backlog-done-items-rotated" for g, _ in w2):
        fails.append("gate warned on an already-rotated row: fails=%r "
                      "warns=%r" % (f2, w2))

    # 3. A file with none of the 17 whitelisted ids present (e.g. a
    #    document mid-restructure) stays silent rather than crash.
    with tempfile.TemporaryDirectory() as tmp3:
        f3, w3 = _run_gate(tmp3, _file("nothing to see here\n"))
    if f3 or w3:
        fails.append("gate did not stay silent on a file with no "
                      "whitelisted rows at all: fails=%r warns=%r"
                      % (f3, w3))

    # 4. A duplicate match for the same id (the underlying tool's own
    #    refusal case) is surfaced as a WARN naming the problem, not an
    #    uncaught crash.
    duplicate = _file(
        "| **A1** | ~~first~~ | one |\n"
        "| **A1** | ~~second~~ | two |\n"
    )
    with tempfile.TemporaryDirectory() as tmp4:
        f4, w4 = _run_gate(tmp4, duplicate)
    if f4:
        fails.append("gate should WARN, not FAIL, on a duplicate "
                      "whitelisted row: %r" % (f4,))
    if not any(g == "backlog-done-items-rotated" for g, _ in w4):
        fails.append("gate did not warn on a duplicate whitelisted row "
                      "instead of crashing: %r" % (w4,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_backlog_done_items_rotated, fail-then-pass proved, "
          "4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
