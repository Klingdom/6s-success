#!/usr/bin/env python3
"""
Prove ops/preflight.py's keyword_demand_rescore_staleness_problem() catches
ops/keyword-demand.json's per-query statuses drifting stale against site/
between rescores (LRN-0032), distinct from gate_keyword_demand_not_stale,
which only watches the harvest's own age.

Run:  python ops/tests/test_gate_keyword_demand_rescored_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def main() -> int:
    fails = []

    # 1. No scored_against_commit at all: must fire, by name, pointing at
    #    the free fix.
    problem = preflight.keyword_demand_rescore_staleness_problem("", [])
    if "scored_against_commit" not in problem:
        fails.append("missing commit did not report it: %r" % problem)
    if "--rescore" not in problem:
        fails.append("missing-commit problem did not point at the fix: %r"
                      % problem)

    # 2. None, same as empty string: must fire too, not crash.
    problem = preflight.keyword_demand_rescore_staleness_problem(None, [])
    if "scored_against_commit" not in problem:
        fails.append("None commit did not report it: %r" % problem)

    # 3. 0 commits touching site/ since the last rescore: must NOT fire.
    problem = preflight.keyword_demand_rescore_staleness_problem("abc123", [])
    if problem:
        fails.append("0 commits since rescore wrongly fired: %r" % problem)

    # 4. 4 commits, one below the threshold: must NOT fire.
    problem = preflight.keyword_demand_rescore_staleness_problem(
        "abc123", ["a", "b", "c", "d"])
    if problem:
        fails.append("4 commits since rescore wrongly fired: %r" % problem)

    # 5. 5 commits, the real threshold: must fire, naming the commit and
    #    the count, and pointing at --rescore.
    problem = preflight.keyword_demand_rescore_staleness_problem(
        "abc123", ["a", "b", "c", "d", "e"])
    if "abc123" not in problem:
        fails.append("5-commit drift did not cite the stale commit: %r"
                      % problem)
    if "5 commit" not in problem:
        fails.append("5-commit drift did not cite the count: %r" % problem)
    if "--rescore" not in problem:
        fails.append("5-commit drift did not point at the fix: %r" % problem)

    # 6. 19 commits, the real shape found live 2026-10-19 (attic/basement
    #    scoring against a 5-day-stale corpus): must fire.
    problem = preflight.keyword_demand_rescore_staleness_problem(
        "deadbeef", list(range(19)))
    if not problem:
        fails.append("19-commit real-shaped drift did not fire")

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    print("test_gate_keyword_demand_rescored_current: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
