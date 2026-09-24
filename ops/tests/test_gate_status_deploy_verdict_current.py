#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_deploy_verdict_current() can actually
fail, and that it clears once STATUS.md's BLOCKER-001 section cites the
real, current build_id.

Found 2026-09-23, this operator: STATUS.md's BLOCKER-001 was last edited
that same day and still quoted a 2026-09-20 deploy confirmation, a full day
after ops/deploy-verdict.json had already recorded a newer one. Nothing
checked BLOCKER-001's own prose against the one file whose whole job is to
record this fact, the same "source corrected, sibling never told" shape
gate_goals_traffic_current already guards for GOALS.md's traffic figure.

Widened 2026-09-24, PM check-in: found a second STATUS.md section,
"Production Knowledge" under "Current Overall Assessment", independently
citing its own "last confirmed current" build_id, four days stale while
BLOCKER-001 (fixed by the 2026-09-23 correction above) had already moved
on. The gate only ever checked BLOCKER-001, so this second citation drifted
unnoticed. status_deploy_verdict_problem() now checks both sections.

Run:  python ops/tests/test_gate_status_deploy_verdict_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    verdict = {"verdict": "current", "build_id": "a993020017bafe37",
               "checked_at": "2026-09-22T16:05:56Z"}

    # 1. BLOCKER-001 cites a different, stale build_id: must fire, and must
    #    name the real current build_id so the fix is obvious.
    stale = (
        "# STATUS\n\n"
        "## Some Other Section\n\nirrelevant text\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n\n"
        "the tracked verdict now reads current at 2026-09-20T17:46:50Z, "
        "build `d9fc700d0700972f`.\n\n"
        "## BLOCKER-002: something else\n\nmore text\n"
    )
    problem = preflight.status_deploy_verdict_problem(stale, verdict)
    if not problem:
        fails.append("stale build_id in BLOCKER-001: expected a problem, "
                     "got none")
    elif verdict["build_id"] not in problem:
        fails.append("problem string did not name the real build_id: %r"
                     % problem)

    # 2. BLOCKER-001 cites the real, current build_id: must not fire.
    current = stale.replace("d9fc700d0700972f", verdict["build_id"])
    problem = preflight.status_deploy_verdict_problem(current, verdict)
    if problem:
        fails.append("current build_id cited, but still flagged: %r"
                     % problem)

    # 3. No BLOCKER-001 section at all (a future rewrite, or a file this
    #    correction no longer applies to): must not fire. This gate only
    #    checks a section that exists, never invents one to complain about.
    no_section = "# STATUS\n\n## Some Other Section\n\nno blocker here.\n"
    problem = preflight.status_deploy_verdict_problem(no_section, verdict)
    if problem:
        fails.append("no BLOCKER-001 section present, but still flagged: %r"
                     % problem)

    # 4. verdict has no build_id (a malformed or half-written file): must
    #    not fire, since there is nothing real to compare against.
    problem = preflight.status_deploy_verdict_problem(stale, {})
    if problem:
        fails.append("verdict with no build_id, but still flagged: %r"
                     % problem)

    # 5. The real defect shape: BLOCKER-001 is current, but the separate
    #    "Production Knowledge" section under "Current Overall Assessment"
    #    independently cites a stale build_id. Must fire, and must name the
    #    stale section specifically, not just "BLOCKER-001" again.
    mixed = (
        "# STATUS\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n\n"
        "the tracked verdict now reads current at 2026-09-23T19:00:39Z, "
        "build `" + verdict["build_id"] + "`.\n\n"
        "# 30. Current Overall Assessment\n\n"
        "**Production Knowledge, corrected earlier:** LAST CONFIRMED "
        "CURRENT 2026-09-18T17:20:47Z (build `7c765b634045a89c`).\n\n"
        "**Business Data Knowledge:** unrelated paragraph.\n"
    )
    problem = preflight.status_deploy_verdict_problem(mixed, verdict)
    if not problem:
        fails.append("BLOCKER-001 current but Production Knowledge stale: "
                     "expected a problem, got none")
    elif "Production Knowledge" not in problem or "BLOCKER-001" in problem:
        fails.append("problem string did not correctly name only the "
                     "stale 'Production Knowledge' section: %r" % problem)

    # 6. Both sections current: must not fire.
    both_current = mixed.replace("7c765b634045a89c", verdict["build_id"])
    problem = preflight.status_deploy_verdict_problem(both_current, verdict)
    if problem:
        fails.append("both sections current, but still flagged: %r"
                     % problem)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 6 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
