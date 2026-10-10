#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_cron_cadence_workflows_registry_current()
catches ops/check_cron_cadence.py's WORKFLOWS list drifting from the real
.github/workflows/*.yml files that carry a cron line.

This exact gap recurred four times by hand (social-drafts.yml, then
indexation-check.yml and keyword-demand.yml together, then owner-questions.yml,
2026-10-10), each caught days late because the one check that already existed
for it, ops/tests/test_check_cron_cadence.py, lives inside gate_tests, the
slow battery this sandbox has never watched finish in the same cycle a new
workflow shipped. This test proves the fast, standalone promotion of that
same logic actually fails and actually passes, the same way
test_gate_architecture_workflow_count_current.py already does for the
sibling ARCHITECTURE.md drift.

Run:  python ops/tests/test_gate_cron_cadence_workflows_registry_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import check_cron_cadence as C                                 # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_cron_cadence_workflows_registry_current()
    return preflight.FAIL


def main() -> int:
    fails = []
    real = list(C.WORKFLOWS)

    # 1. The real, committed registry against the real, committed
    #    directory: clean.
    r = _run()
    if r:
        fails.append("the real committed WORKFLOWS list wrongly failed: %r"
                     % (r,))

    # 2. Drop a real cron-scheduled file from the registry (the actual
    #    2026-10-10 regression shape): must fail, naming the file.
    C.WORKFLOWS = [w for w in real if w != "owner-questions.yml"]
    r = _run()
    if not r:
        fails.append("dropping owner-questions.yml from WORKFLOWS was "
                      "wrongly passed")
    elif "owner-questions.yml" not in r[0][1]:
        fails.append("the failure did not name the missing file: %r" % (r,))
    C.WORKFLOWS = list(real)

    # 3. A stale name that no longer exists (or never carried a cron line)
    #    must also fail, naming it.
    C.WORKFLOWS = real + ["retired-ghost-workflow.yml"]
    r = _run()
    if not r:
        fails.append("a stale, nonexistent workflow name in WORKFLOWS was "
                      "wrongly passed")
    elif "retired-ghost-workflow.yml" not in r[0][1]:
        fails.append("the failure did not name the stale entry: %r" % (r,))
    C.WORKFLOWS = list(real)

    # 4. Restored: clean again.
    r = _run()
    if r:
        fails.append("WORKFLOWS was not fully restored: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_cron_cadence_workflows_registry_current, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
