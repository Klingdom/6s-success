#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_revenue_window_current() catches
GOALS.md still framing the one $19 sale as inside a trailing 30-day
window once the date it names for that window's own expiry has passed.

Found 2026-09-19: GOALS.md section 1 says the sale is "inside the trailing
30-day window until 2026-09-20, after which the 30-day figure genuinely
becomes zero unless a new sale lands first." That sentence is correct
today and, unwatched, would silently become wrong the day after: either a
second sale keeps it true (and the sentence should say so) or none landed
(and the prose should say the 30-day figure is now $0, not still describe
a window that has already closed). Nothing was checking the date itself.

Run:  python ops/tests/test_gate_goals_revenue_window_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

SENTENCE = ("one $19 sale, ever, which is inside the trailing 30-day "
            "window until %s, after which the 30-day figure genuinely "
            "becomes zero unless a new sale lands first.")


def _run(goals_text):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_revenue_window_current()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: the cited rollover date is in the past.
    #    Must fail.
    r, w = _run("Baseline: " + (SENTENCE % "2020-01-01"))
    if not r or "goals-revenue-window-current" != r[0][0]:
        fails.append("a past rollover date was not caught: %r" % (r,))

    # 2. The cited rollover date is far in the future: no failure.
    r, w = _run("Baseline: " + (SENTENCE % "2099-01-01"))
    if r:
        fails.append("a future rollover date was wrongly flagged: %r" % (r,))

    # 3. No such sentence at all (already rewritten past the rollover, or
    #    never written this way): no failure, nothing to check.
    r, w = _run("Baseline: one $19 sale, ever, no second sale yet.")
    if r:
        fails.append("silence on the window sentence wrongly flagged: %r"
                     % (r,))

    # 4. GOALS.md missing entirely: no crash, no failure.
    tmp = tempfile.mkdtemp()
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_revenue_window_current()
        r, w = list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)
    if r:
        fails.append("a missing GOALS.md was failed instead of skipped: "
                     "%r" % (r,))

    # 5. The real committed file: clean today (the cited date, 2026-09-20,
    #    has not yet passed).
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_goals_revenue_window_current()
    if preflight.FAIL:
        fails.append("the real committed GOALS.md failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_revenue_window_current, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
