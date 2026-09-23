#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_goals_traffic_current() catches the
2026-09-14 regression shape: OWNER-ACTIONS.md item 1 carries a newer, real
visitor pull than GOALS.md's own baseline, and nothing had ever compared the
two directly (only GOALS.md against STATUS.md/roadmap_report.py/
experiments.json, all of which can agree with each other while all three sit
stale together).

Also proves the fix for a false positive found while building this: a bare
lazy ".*?" between "Measured DATE" and "Traffic is N visitors" can bridge two
unrelated paragraphs and pair the wrong date with the wrong count.

Run:  python ops/tests/test_gate_goals_traffic_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOALS = (
    "| Link | Baseline | What it means |\n"
    "|---|---|---|\n"
    "| Stranger to Visitor | **68 visitors / 161 visits / 30 days** | x |\n"
    "| Sessions from organic search | **2** | x |\n"
    "| Sessions, last 7 days | **21** | x |\n"
)

OA_AGREES = (
    "### 1. Authorise YouTube uploads.\n\n"
    "**Measured 2026-09-11, 30 days, and it makes the case better than the "
    "old\nline did.** Traffic is 68 visitors and 910 pageviews, 2.3 a day.\n"
)

OA_DISAGREES = (
    "### 1. Authorise YouTube uploads.\n\n"
    "**Measured 2026-09-11, 30 days, and it makes the case better than the "
    "old\nline did.** Traffic is 60 visitors and 800 pageviews, 2.0 a day.\n"
)

# The real false-positive shape: an unrelated "Measured" paragraph, then a
# blank-line-separated, unrelated later paragraph that happens to contain
# "Traffic is N visitors" for a *different* count than GOALS.md's own.
OA_UNRELATED_PARAGRAPHS = (
    "**Measured 2026-09-04, not assumed.** Something else entirely, with no "
    "traffic figure in it at all, going on for a while so a bare lazy match "
    "would have to cross a paragraph break to reach the real line below.\n\n"
    "### 1. Authorise YouTube uploads.\n\n"
    "**Measured 2026-09-11, 30 days, and it makes the case better than the "
    "old\nline did.** Traffic is 68 visitors and 910 pageviews, 2.3 a day.\n"
)

OA_NO_LINE = "Nothing resembling that phrase appears anywhere in this file.\n"

# Same-document shape, found 2026-09-23: GOALS.md's own "Weekly visitors" row
# and "Why it is first" narrative paragraph, both a few lines below the
# canonical table, drifted from it without any sibling file ever disagreeing.
GOALS_WEEKLY_AGREES = GOALS + "| Weekly visitors | **21/wk** | 500/wk |\n"
GOALS_WEEKLY_DISAGREES = GOALS + "| Weekly visitors | **14/wk (stale)** | 500/wk |\n"

GOALS_WHY_AGREES = GOALS + (
    "\n**Why it is first, now with numbers.** 68 visitors (read directly "
    "from the database) across 161 visits in thirty days, and so on.\n")
GOALS_WHY_DISAGREES = GOALS + (
    "\n**Why it is first, now with numbers.** 68 visitors (read directly "
    "from the database) across 193 visits in thirty days, and so on.\n")


def _run(goals: str, owner_actions: str):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals)
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w", encoding="utf-8").write(owner_actions)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_goals_traffic_current()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. GOALS.md and OWNER-ACTIONS.md agree (68 both places): no failure.
    r = _run(GOALS, OA_AGREES)
    if r:
        fails.append("agreement wrongly flagged: %r" % (r,))

    # 2. OWNER-ACTIONS.md's own newer pull disagrees with GOALS.md: caught,
    #    naming both numbers.
    r = _run(GOALS, OA_DISAGREES)
    if not r or "60" not in r[0][1] or "68" not in r[0][1]:
        fails.append("OWNER-ACTIONS.md disagreement not caught: %r" % (r,))

    # 3. An unrelated earlier "Measured" paragraph must not let a lazy regex
    #    bridge into a later, unrelated paragraph's own real figure. Here the
    #    real figure (68) DOES match GOALS.md, so this must pass, not fail
    #    with the wrong date attached to it.
    r = _run(GOALS, OA_UNRELATED_PARAGRAPHS)
    if r:
        fails.append("cross-paragraph false positive: %r" % (r,))

    # 4. OWNER-ACTIONS.md carries no such line at all: must not crash, must
    #    not invent a finding.
    r = _run(GOALS, OA_NO_LINE)
    if r:
        fails.append("missing line wrongly flagged: %r" % (r,))

    # 6. GOALS.md's own "Weekly visitors" row agrees with "Sessions, last 7
    #    days" above it (21 both places): no failure.
    r = _run(GOALS_WEEKLY_AGREES, OA_AGREES)
    if r:
        fails.append("Weekly visitors agreement wrongly flagged: %r" % (r,))

    # 7. It disagrees (14 vs. 21): caught, naming both numbers.
    r = _run(GOALS_WEEKLY_DISAGREES, OA_AGREES)
    if not r or "14" not in r[0][1] or "21" not in r[0][1]:
        fails.append("Weekly visitors disagreement not caught: %r" % (r,))

    # 8. GOALS.md's own "Why it is first" paragraph agrees with the
    #    "Stranger to Visitor" row above it (68/161 both places): no failure.
    r = _run(GOALS_WHY_AGREES, OA_AGREES)
    if r:
        fails.append("Why-it-is-first agreement wrongly flagged: %r" % (r,))

    # 9. It disagrees (193 visits vs. the table's own 161): caught, naming
    #    both numbers, the exact 2026-09-23 shape (a stale narrative citing
    #    the day-before pull after the table above it had already moved on).
    r = _run(GOALS_WHY_DISAGREES, OA_AGREES)
    if not r or "193" not in r[0][1] or "161" not in r[0][1]:
        fails.append("Why-it-is-first disagreement not caught: %r" % (r,))

    # 5. The real, committed files: clean today.
    real_goals = os.path.join(ROOT, "GOALS.md")
    real_oa = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_goals) and os.path.exists(real_oa):
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_goals_traffic_current()
        if preflight.FAIL:
            fails.append("real committed files failed: %r" % (preflight.FAIL,))
    else:
        print("  (skipped: real GOALS.md/OWNER-ACTIONS.md not found)")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_traffic_current (OWNER-ACTIONS.md and same-document checks), 9/9 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
