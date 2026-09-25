#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_deploy_gap_count_current() can
actually fail, and that it clears once BLOCKER-001's own commit-count
claim matches a fresh recount.

Found live 2026-09-24, scheduled operator cycle: gate_status_deploy_
verdict_current only checks that BLOCKER-001 cites the real, current
build_id; it never checked whether the "(N commit)" gap count sitting next
to that citation was still accurate. The 21:2x-era entry correctly named
build_id `28ed2709194afab5` and said the gap was "(1 commit, `869d4e93`)".
Two more site-affecting commits (`29a84fa2`, `b8eca135`) landed after that
entry was written and neither was mentioned, so the citation stayed
technically correct (the build_id was right) while the count beside it was
already off by 3x. deploy_gap_count_problem() re-derives the real count
from a caller-supplied number (git work itself happens in the gate, not
here, so this test needs no repository state) and compares it against the
section's own claim.

Run:  python ops/tests/test_gate_status_deploy_gap_count_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

BUILD_ID = "28ed2709194afab5"


def section(latest_entry: str) -> str:
    return (
        "# STATUS\n\n"
        "## Some Other Section\n\nirrelevant text\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n\n"
        "**Status: an earlier entry, kept for history, citing a totally "
        "different build_id and a totally different count "
        "(9 commits).**\n\n"
        + latest_entry +
        "\n\n## BLOCKER-002: something else\n\nmore text\n"
    )


def main() -> int:
    fails = []

    # 1. The real defect shape: latest entry cites "(1 commit)" next to the
    #    current build_id, but a fresh recount says 3. Must fire, and must
    #    name both numbers.
    latest = (
        "**RESOLVED, later: a session with real access redeployed, then "
        "one more commit landed.** `ops/deploy-verdict.json` now records "
        "build `%s`; `git diff --quiet ... HEAD -- site/ Dockerfile` is "
        "dirty again (1 commit, `869d4e93`)." % BUILD_ID
    )
    problem = preflight.deploy_gap_count_problem(
        section(latest), real_count=3, build_id=BUILD_ID,
        checked_at="2026-09-24T21:10:12Z")
    if not problem:
        fails.append("cited 1, real 3: expected a problem, got none")
    elif "1 commit" not in problem or "3" not in problem:
        fails.append("problem string did not name both counts: %r" % problem)

    # 2. The count matches the real recount: must not fire.
    latest_ok = latest.replace("(1 commit,", "(3 commits,")
    problem = preflight.deploy_gap_count_problem(
        section(latest_ok), real_count=3, build_id=BUILD_ID,
        checked_at="2026-09-24T21:10:12Z")
    if problem:
        fails.append("cited 3, real 3: still flagged: %r" % problem)

    # 3. The older, superseded entry in the section cites a stale "9
    #    commits" figure, but that is deliberately kept history, not the
    #    standing claim; only the LATEST entry (already checked above)
    #    should ever be compared. Reusing the ok case here just confirms
    #    the older entry's own wrong number never leaks into the result.
    if "commits" not in section(latest_ok) or problem:
        pass  # covered by case 2; nothing further to assert here.

    # 4. No BLOCKER-001 section at all: must not fire.
    no_section = "# STATUS\n\n## Some Other Section\n\nno blocker here.\n"
    problem = preflight.deploy_gap_count_problem(
        no_section, real_count=3, build_id=BUILD_ID, checked_at="")
    if problem:
        fails.append("no BLOCKER-001 section, but still flagged: %r"
                     % problem)

    # 5. No build_id supplied (a malformed verdict file): must not fire.
    problem = preflight.deploy_gap_count_problem(
        section(latest), real_count=3, build_id="", checked_at="")
    if problem:
        fails.append("empty build_id, but still flagged: %r" % problem)

    # 6. The latest entry does not cite the current build_id at all (a
    #    fresher correction may be mid-write, or it is simply stale in a
    #    way gate_status_deploy_verdict_current already owns): must not
    #    fire here, to avoid double-reporting the same underlying gap.
    stale_build = latest.replace(BUILD_ID, "0000000000000000")
    problem = preflight.deploy_gap_count_problem(
        section(stale_build), real_count=3, build_id=BUILD_ID,
        checked_at="")
    if problem:
        fails.append("latest entry cites a different build_id, but still "
                     "flagged here: %r" % problem)

    # 7. The latest entry describes the gap with no bare "(N commit)"
    #    number at all (e.g. "the gap is real again, unmeasured"): nothing
    #    to compare, must not fire rather than guess.
    no_number = ("**Reopened: a real gap, not yet recounted.** build `%s` "
                 "confirmed; the repository has moved on." % BUILD_ID)
    problem = preflight.deploy_gap_count_problem(
        section(no_number), real_count=3, build_id=BUILD_ID, checked_at="")
    if problem:
        fails.append("no parseable count in latest entry, but still "
                     "flagged: %r" % problem)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 6 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
