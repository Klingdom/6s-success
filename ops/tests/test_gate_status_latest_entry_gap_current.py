#!/usr/bin/env python3
"""
Prove status_latest_entry_gap_problem() can actually fail, and that it
clears once STATUS.md section 1's "Latest" entry either states the real
commit count or points at BLOCKER-001 instead of restating it.

Found 2026-10-29, scheduled operator cycle: the "Latest" entry under
"# 1. Status Metadata" said "production now trails the repository by two
site commits" while a fresh recount (and BLOCKER-001's own latest entry)
put the real gap at four, three of them content. Neither
gate_status_deploy_verdict_current nor gate_status_deploy_gap_count_current
checks this paragraph: the first only matches sections that cite a
build_id (this one doesn't), the second only ever looks at BLOCKER-001.
This is the sixth section this exact "cites a fact, wrong number beside
it" shape has hit; full history in status_latest_entry_gap_problem()'s own
docstring.

Run:  python ops/tests/test_gate_status_latest_entry_gap_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. The real defect shape: "Latest" entry cites 2 commits, real gap
    #    is 4. Must fire, naming the real count.
    stale = (
        "# STATUS\n\n"
        "# 1. Status Metadata\n\n"
        "**Latest, 2026-10-28, owner-invoked CEO cycle: something "
        "shipped.** Production now trails the repository by two site "
        "commits (`840f3e11b` plus this one) until a redeploy.\n\n"
        "**Older entries (112 of them) live in STATUS-ARCHIVE.md.**\n\n"
        "# 2. Something Else\n\nirrelevant text\n"
    )
    problem = preflight.status_latest_entry_gap_problem(stale, 4)
    if not problem:
        fails.append("stale 'two commits' against real_count=4: expected "
                     "a problem, got none")
    elif "4" not in problem:
        fails.append("problem string did not name the real count: %r"
                     % problem)

    # 2. Same paragraph, count corrected to match: must not fire.
    corrected = stale.replace("two site commits", "four site commits")
    problem = preflight.status_latest_entry_gap_problem(corrected, 4)
    if problem:
        fails.append("corrected count agrees with real_count, but still "
                     "flagged: %r" % problem)

    # 3. Same paragraph, now pointing at BLOCKER-001 instead of restating
    #    the count at all (the structural fix, same as Immediate Focus):
    #    must not fire even though "two" is still a stale number in the
    #    text, since the pointer is present.
    pointed = stale.replace(
        "Production now trails the repository by two site commits "
        "(`840f3e11b` plus this one) until a redeploy.",
        "FOR THE CURRENT DEPLOY GAP SEE BLOCKER-001, NOT THIS LINE.")
    problem = preflight.status_latest_entry_gap_problem(pointed, 4)
    if problem:
        fails.append("entry points at BLOCKER-001, but still flagged: %r"
                     % problem)

    # 4. No "Latest," paragraph at all: must not fire.
    problem = preflight.status_latest_entry_gap_problem(
        "# STATUS\n\nnothing relevant here\n", 4)
    if problem:
        fails.append("no 'Latest,' paragraph present, but still flagged: "
                     "%r" % problem)

    # 5. "Latest," paragraph present but names no bare commit count at
    #    all (e.g. a cycle that did non-deploy work): must not fire.
    no_count = (
        "# 1. Status Metadata\n\n"
        "**Latest, 2026-10-29, scheduled operator: fixed a typo.** No "
        "deploy-relevant change this cycle.\n\n"
        "**Older entries live in STATUS-ARCHIVE.md.**\n"
    )
    problem = preflight.status_latest_entry_gap_problem(no_count, 4)
    if problem:
        fails.append("entry names no commit count at all, but still "
                     "flagged: %r" % problem)

    # 6. Zero-gap phrasing ("zero commits"), matching real_count=0: must
    #    not fire.
    zero_entry = (
        "# 1. Status Metadata\n\n"
        "**Latest, 2026-10-29, scheduled operator: redeployed.** "
        "Production matches the repository exactly, zero commits "
        "undeployed.\n\n"
        "**Older entries live in STATUS-ARCHIVE.md.**\n"
    )
    problem = preflight.status_latest_entry_gap_problem(zero_entry, 0)
    if problem:
        fails.append("'zero commits' agrees with real_count=0, but still "
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
