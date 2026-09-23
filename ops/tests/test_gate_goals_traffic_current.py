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

Widened 2026-09-23 (two independent sessions, same day): DATA-SOURCES.md's
own "N visitors/M visits, GOALS.md O1" citation is now checked the same way,
and GOALS.md's own "Weekly visitors" row and "Why it is first" paragraph are
now checked against its own "Stranger to Visitor"/"Sessions, last 7 days"
rows, since every prior check compared GOALS.md against a sibling file but
never against itself.

Widened 2026-09-23, PM check-in: STATUS.md's own "Business Data Knowledge"
paragraph (section 29) carries a separate copy of the figure from the
section 9 table this gate already checked, and was found nine days and two
corrections stale.

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

DS_AGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures (68 "
    "visitors/161 visits, `GOALS.md` O1) were read directly | x | x | x |\n"
)

DS_DISAGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures (60 "
    "visitors/140 visits, `GOALS.md` O1) were read directly | x | x | x |\n"
)

DS_NO_LINE = "Nothing resembling that phrase appears anywhere in this file.\n"

# The real 2026-09-23 regression shape, found later the same day: a
# "**corrected**" annotation inserted between the figure and the citation
# broke the tight "visits,\s*`GOALS.md`" regex, so a row that had gone
# self-contradictory (a fresh figure glued onto a stale correction's own
# leftover prose) was silently exempted from this check instead of failing
# loud. The gate must now tolerate the inserted detail and still compare.
DS_ANNOTATED_AGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures "
    "(**corrected 2026-09-23**: 68 visitors/161 visits/30 days, "
    "`GOALS.md` O1, measured 2026-09-23) were read directly | x | x | x |\n"
)
DS_ANNOTATED_DISAGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures "
    "(**corrected 2026-09-23**: 75 visitors/196 visits/30 days, "
    "`GOALS.md` O1, measured 2026-09-14) were read directly | x | x | x |\n"
)

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

# STATUS.md's own "Business Data Knowledge" paragraph (section 29), found
# 2026-09-23, PM check-in: nine days and two corrections behind section 9's
# own table above it (75/196, the 2026-09-14 pull, while GOALS.md had moved
# to 68/160). A separate copy of the figure from the section-9 check above.
STATUS_SECTION_9 = (
    "| Sessions | 68 | Last 30 days | x |\n"
    "| Sessions | 21 | Last 7 days | x |\n"
)
STATUS_AGREES = STATUS_SECTION_9 + (
    "**Business Data Knowledge:** CURRENT TRAFFIC BASELINE: 68 VISITORS "
    "ACROSS 161 VISITS AND 900 PAGEVIEWS IN 30 DAYS.\n"
)
STATUS_DISAGREES = STATUS_SECTION_9 + (
    "**Business Data Knowledge:** CURRENT TRAFFIC BASELINE: 75 VISITORS "
    "ACROSS 196 VISITS AND 947 PAGEVIEWS IN 30 DAYS.\n"
)
STATUS_NO_LINE = STATUS_SECTION_9 + (
    "Nothing resembling that phrase appears anywhere in this file.\n")


def _run(goals: str, owner_actions: str, data_sources: str = None, status: str = None):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals)
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w", encoding="utf-8").write(owner_actions)
    if data_sources is not None:
        io.open(os.path.join(tmp, "DATA-SOURCES.md"), "w", encoding="utf-8").write(data_sources)
    if status is not None:
        io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(status)
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

    # 5. DATA-SOURCES.md's own "N visitors/M visits, GOALS.md O1" citation
    #    agrees (68/161 both places): no failure.
    r = _run(GOALS, OA_AGREES, DS_AGREES)
    if r:
        fails.append("DATA-SOURCES.md agreement wrongly flagged: %r" % (r,))

    # 6. DATA-SOURCES.md carries a stale figure: caught, naming both
    #    numbers. This is the real 2026-09-23 regression shape: 75/196 sat
    #    in DATA-SOURCES.md after GOALS.md O1 had already moved to 76/190.
    r = _run(GOALS, OA_AGREES, DS_DISAGREES)
    if not r or "60" not in r[0][1] or "68" not in r[0][1]:
        fails.append("DATA-SOURCES.md disagreement not caught: %r" % (r,))

    # 7. DATA-SOURCES.md carries no such line at all: must not crash, must
    #    not invent a finding.
    r = _run(GOALS, OA_AGREES, DS_NO_LINE)
    if r:
        fails.append("DATA-SOURCES.md missing line wrongly flagged: %r" % (r,))

    # 8. DATA-SOURCES.md absent entirely (older checkouts, other repos):
    #    must not crash, must not invent a finding.
    r = _run(GOALS, OA_AGREES)
    if r:
        fails.append("absent DATA-SOURCES.md wrongly flagged: %r" % (r,))

    # 9. GOALS.md's own "Weekly visitors" row agrees with "Sessions, last 7
    #    days" above it (21 both places): no failure.
    r = _run(GOALS_WEEKLY_AGREES, OA_AGREES)
    if r:
        fails.append("Weekly visitors agreement wrongly flagged: %r" % (r,))

    # 10. It disagrees (14 vs. 21): caught, naming both numbers.
    r = _run(GOALS_WEEKLY_DISAGREES, OA_AGREES)
    if not r or "14" not in r[0][1] or "21" not in r[0][1]:
        fails.append("Weekly visitors disagreement not caught: %r" % (r,))

    # 11. GOALS.md's own "Why it is first" paragraph agrees with the
    #     "Stranger to Visitor" row above it (68/161 both places): no failure.
    r = _run(GOALS_WHY_AGREES, OA_AGREES)
    if r:
        fails.append("Why-it-is-first agreement wrongly flagged: %r" % (r,))

    # 12. It disagrees (193 visits vs. the table's own 161): caught, naming
    #     both numbers, the exact 2026-09-23 shape (a stale narrative citing
    #     the day-before pull after the table above it had already moved on).
    r = _run(GOALS_WHY_DISAGREES, OA_AGREES)
    if not r or "193" not in r[0][1] or "161" not in r[0][1]:
        fails.append("Why-it-is-first disagreement not caught: %r" % (r,))

    # 13. The real, committed files: clean today.
    real_goals = os.path.join(ROOT, "GOALS.md")
    real_oa = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_goals) and os.path.exists(real_oa):
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_goals_traffic_current()
        if preflight.FAIL:
            fails.append("real committed files failed: %r" % (preflight.FAIL,))
    else:
        print("  (skipped: real GOALS.md/OWNER-ACTIONS.md not found)")

    # 14. DATA-SOURCES.md carries an inserted "**corrected**" annotation
    #     between the figure and the `GOALS.md` O1 citation, and the figure
    #     still agrees (68/161): no failure. Proves the widened regex still
    #     matches through the inserted detail rather than losing the row.
    r = _run(GOALS, OA_AGREES, DS_ANNOTATED_AGREES)
    if r:
        fails.append("annotated DATA-SOURCES.md agreement wrongly flagged: %r" % (r,))

    # 15. Same annotated shape, but the figure is stale (75/196): caught,
    #     naming both numbers. Before the 2026-09-23 widening this row would
    #     have silently escaped the check entirely (regex simply would not
    #     match), the exact live defect found that day.
    r = _run(GOALS, OA_AGREES, DS_ANNOTATED_DISAGREES)
    if not r or "75" not in r[0][1] or "68" not in r[0][1]:
        fails.append("annotated DATA-SOURCES.md disagreement not caught: %r" % (r,))

    # 16. STATUS.md's "Business Data Knowledge" paragraph agrees with
    #     GOALS.md (68/161 both places): no failure. Section 9's own rows
    #     are included so that separate, already-existing check stays quiet
    #     too, isolating this test to the new paragraph check alone.
    r = _run(GOALS, OA_AGREES, status=STATUS_AGREES)
    if r:
        fails.append("STATUS.md Business Data Knowledge agreement wrongly "
                      "flagged: %r" % (r,))

    # 17. It disagrees (75/196 vs. GOALS.md's 68/161): caught, naming both
    #     numbers. This is the real 2026-09-23 regression shape: the
    #     paragraph sat nine days and two corrections behind section 9's own
    #     table a thousand lines above it in the same file.
    r = _run(GOALS, OA_AGREES, status=STATUS_DISAGREES)
    if not r or "75" not in r[0][1] or "68" not in r[0][1]:
        fails.append("STATUS.md Business Data Knowledge disagreement not "
                      "caught: %r" % (r,))

    # 18. STATUS.md carries no such paragraph at all: must not crash, must
    #     not invent a finding.
    r = _run(GOALS, OA_AGREES, status=STATUS_NO_LINE)
    if r:
        fails.append("STATUS.md missing Business Data Knowledge paragraph "
                      "wrongly flagged: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_goals_traffic_current (OWNER-ACTIONS.md + DATA-SOURCES.md "
          "+ STATUS.md Business Data Knowledge + same-document checks), "
          "18/18 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
