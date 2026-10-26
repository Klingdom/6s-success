"""Prove gate_generator_ownership's own-output exclusion list does not block
on its own cycle_signal checkpoint file.

Found 2026-10-26: a clean publish-image.yml run (the one gate_ci_conclusion_
current's own self-reference demotion had just unblocked) failed anyway, one
gate further down the same chain. maybe_record_cycle_signal() writes
ops/cycle-signal.json earlier in this same preflight run, before gate_tests,
exactly the same shape as the dashboard trio (EXECUTIVE-DASHBOARD-LIVE.md,
ops/dashboard.html, ops/state.json) this gate already excludes by name, but
it had never been added to that set, so the gate saw a "dirty" tree that was
only its own sibling's bookkeeping and refused to run at all.

This stubs worktree_changes() and empties GENERATOR_OWNERSHIP_CHAIN so the
check below exercises only the dirty-tree precondition, not the (expensive,
20+ generator) real rebuild loop: fast and isolated, the same shape every
other gate test in this file uses stubs for.

Run:  python ops/tests/test_gate_generator_ownership_own_output.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run(changes):
    old_changes = preflight.worktree_changes
    old_chain = preflight.GENERATOR_OWNERSHIP_CHAIN
    preflight.worktree_changes = lambda: changes
    preflight.GENERATOR_OWNERSHIP_CHAIN = []
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_generator_ownership()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.worktree_changes = old_changes
        preflight.GENERATOR_OWNERSHIP_CHAIN = old_chain


def main():
    fails = []

    # 1. cycle-signal.json alone, dirty from this same run's own checkpoint,
    #    must not block the gate the way a real hand edit would.
    f, w = _run(["ops/cycle-signal.json"])
    if any(name == "generator-ownership" for name, _ in f):
        fails.append("ops/cycle-signal.json alone still failed the "
                      "dirty-tree precondition: %r" % f)

    # 2. The whole known-safe quartet together: still excused.
    f, w = _run(["EXECUTIVE-DASHBOARD-LIVE.md", "ops/dashboard.html",
                 "ops/state.json", "ops/cycle-signal.json"])
    if any(name == "generator-ownership" for name, _ in f):
        fails.append("the full own-output quartet still failed the "
                      "dirty-tree precondition: %r" % f)

    # 3. Any other file alongside them still blocks: this is an exclusion
    #    list, not a loosened check, and a real hand edit must still be
    #    caught even while the bookkeeping files sit modified too.
    f, w = _run(["ops/cycle-signal.json", "site/hand-edited.html"])
    if not any(name == "generator-ownership" for name, _ in f):
        fails.append("a real extra dirty file was excused along with the "
                      "known-safe ones, which should never happen: %r %r"
                      % (f, w))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: gate_generator_ownership own-output exclusion, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
