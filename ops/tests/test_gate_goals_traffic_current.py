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

DS_AGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures (68 "
    "visitors/161 visits, `GOALS.md` O1) were read directly | x | x | x |\n"
)

DS_DISAGREES = (
    "| Web analytics | Umami | VERIFIED: real traffic figures (60 "
    "visitors/140 visits, `GOALS.md` O1) were read directly | x | x | x |\n"
)

DS_NO_LINE = "Nothing resembling that phrase appears anywhere in this file.\n"


def _run(goals: str, owner_actions: str, data_sources: str = None):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "GOALS.md"), "w", encoding="utf-8").write(goals)
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w", encoding="utf-8").write(owner_actions)
    if data_sources is not None:
        io.open(os.path.join(tmp, "DATA-SOURCES.md"), "w", encoding="utf-8").write(data_sources)
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

    # 4b. Widened 2026-09-23: DATA-SOURCES.md's own "N visitors/M visits,
    #     GOALS.md O1" citation must be checked the same way. Agreement: no
    #     failure.
    r = _run(GOALS, OA_AGREES, DS_AGREES)
    if r:
        fails.append("DATA-SOURCES.md agreement wrongly flagged: %r" % (r,))

    # 4c. DATA-SOURCES.md carries a stale figure: caught, naming both
    #     numbers. This is the real 2026-09-23 regression shape: 75/196 sat
    #     in DATA-SOURCES.md after GOALS.md O1 had already moved to 76/190.
    r = _run(GOALS, OA_AGREES, DS_DISAGREES)
    if not r or "60" not in r[0][1] or "68" not in r[0][1]:
        fails.append("DATA-SOURCES.md disagreement not caught: %r" % (r,))

    # 4d. DATA-SOURCES.md carries no such line at all: must not crash, must
    #     not invent a finding.
    r = _run(GOALS, OA_AGREES, DS_NO_LINE)
    if r:
        fails.append("DATA-SOURCES.md missing line wrongly flagged: %r" % (r,))

    # 4e. DATA-SOURCES.md absent entirely (older checkouts, other repos):
    #     must not crash, must not invent a finding.
    r = _run(GOALS, OA_AGREES)
    if r:
        fails.append("absent DATA-SOURCES.md wrongly flagged: %r" % (r,))

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
    print("OK: gate_goals_traffic_current (OWNER-ACTIONS.md + DATA-SOURCES.md "
          "cross-check), 9/9 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
