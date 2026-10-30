#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_table_rows_gap_count_current() can
actually fail, and that it clears once the "Public website" and
"Production traceability" table rows in STATUS.md section 1 both state a
commit count that matches a fresh recount.

Found live 2026-10-30, scheduled operator cycle: BLOCKER-001's own count
(gate_status_deploy_gap_count_current) and section 1's "Latest" paragraph
(gate_status_latest_entry_gap_current) each had a dedicated staleness
gate, but these two table rows, which restate the identical fact in their
own words ("REOPENED: 12 commits undeployed, 9 of them content"), had
none. A fresh recount put the real gap at 15 while both rows still said
12. status_table_rows_gap_count_problem() re-derives the real count from
a caller-supplied number (git work happens in the gate, not here, so this
test needs no repository state) and compares it against each row's own
claim.

Run:  python ops/tests/test_gate_status_table_rows_gap_count_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def doc(public_row: str, prod_row: str) -> str:
    return (
        "# STATUS\n\n"
        "# 1. Status Metadata\n\n"
        "| Area | Status | Evidence / Notes |\n"
        "|---|---|---|\n"
        "| Public website | %s | some evidence |\n"
        "| Application/API | N/A BY DESIGN | no backend |\n"
        "| Production traceability | %s | some evidence |\n"
        "| Repository hygiene | 10 open issues | notes |\n"
    ) % (public_row, prod_row)


def main() -> int:
    fails = []

    # 1. The real defect shape: both rows cite 12, real count is 15. Must
    #    fire, and must name both the stale rows and the real count.
    stale_doc = doc(
        "LIVE as of 2026-10-26T16:51:56Z, build `a0bbe5bb276ee21b`, "
        "**REOPENED: 12 commits undeployed, 9 of them content**",
        "Tracked, current build citation, **REOPENED: 12 commits "
        "undeployed, 9 content**, build `a0bbe5bb276ee21b`",
    )
    problem = preflight.status_table_rows_gap_count_problem(
        stale_doc, real_count=15)
    if not problem:
        fails.append("both rows cite 12, real 15: expected a problem, "
                     "got none")
    elif "Public website" not in problem or "Production traceability" \
            not in problem or "15" not in problem:
        fails.append("problem string did not name both rows and the real "
                     "count: %r" % problem)

    # 2. Both rows already state the real count: must not fire.
    ok_doc = doc(
        "LIVE as of 2026-10-26T16:51:56Z, build `a0bbe5bb276ee21b`, "
        "**REOPENED: 15 commits undeployed, 10 of them content**",
        "Tracked, current build citation, **REOPENED: 15 commits "
        "undeployed, 10 content**, build `a0bbe5bb276ee21b`",
    )
    problem = preflight.status_table_rows_gap_count_problem(
        ok_doc, real_count=15)
    if problem:
        fails.append("both rows cite 15, real 15: still flagged: %r"
                     % problem)

    # 3. Only one row has drifted (a half-finished correction): must name
    #    only that row, not the one already correct.
    half_doc = doc(
        "LIVE as of 2026-10-26T16:51:56Z, build `a0bbe5bb276ee21b`, "
        "**REOPENED: 15 commits undeployed, 10 of them content**",
        "Tracked, current build citation, **REOPENED: 12 commits "
        "undeployed, 9 content**, build `a0bbe5bb276ee21b`",
    )
    problem = preflight.status_table_rows_gap_count_problem(
        half_doc, real_count=15)
    if not problem:
        fails.append("one row still cites 12, real 15: expected a "
                     "problem, got none")
    elif "Production traceability" not in problem \
            or "Public website" in problem:
        fails.append("problem string did not isolate the one stale row: "
                     "%r" % problem)

    # 4. Neither row states a bare "<n> commits undeployed" count at all
    #    (e.g. a fully resolved gap worded differently): nothing to
    #    compare, must not fire rather than guess.
    no_number_doc = doc(
        "LIVE as of 2026-10-26T16:51:56Z, build `a0bbe5bb276ee21b`, "
        "production matches the repository",
        "Tracked, current build citation, production matches the "
        "repository, build `a0bbe5bb276ee21b`",
    )
    problem = preflight.status_table_rows_gap_count_problem(
        no_number_doc, real_count=0)
    if problem:
        fails.append("no parseable count in either row, but still "
                     "flagged: %r" % problem)

    # 5. Neither table row exists at all: must not fire.
    no_rows = "# STATUS\n\n# 1. Status Metadata\n\nnothing here.\n"
    problem = preflight.status_table_rows_gap_count_problem(
        no_rows, real_count=15)
    if problem:
        fails.append("no table rows at all, but still flagged: %r"
                     % problem)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
