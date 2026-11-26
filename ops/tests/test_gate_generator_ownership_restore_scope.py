"""Prove gate_generator_ownership restores only the `changed` set it already
computed, not a fresh worktree_changes() query taken after that point.

Found live 2026-11-26: the gate used to end with `_restore(worktree_changes())`.
Its own surrounding comment claimed this "restores ONLY the paths this gate
is responsible for", but worktree_changes() is a fresh git diff/ls-files
query against whatever is dirty AT THAT LATER MOMENT, not the generator
output this gate itself wrote. A concurrent, unrelated, uncommitted hand
edit sitting in the tree while this gate ran (here: a fix to this very
preflight.py, made by a session running at the same time the gate's own
generators were executing) was silently discarded along with any real
generator drift, with no mention in the gate's output: exactly the
"anything committed to disk between that check and this line would have
been destroyed with no record that it ever existed" race the comment
believed it had already closed by switching from a whole-tree `git
checkout -- .` to batched per-path checkouts. Batching alone does not fix
scope: it still passed the same too-broad set.

This stubs worktree_changes() (with a call counter, since the bug is
specifically that the gate queries it twice, before and after running the
generators, and the second query can legitimately differ from the first),
GENERATOR_OWNERSHIP_CHAIN (empty, so no real generator subprocess runs) and
_restore() (captures the paths it is asked to check out, instead of running
real git) so this is fast and touches no real files.

Run:  python ops/tests/test_gate_generator_ownership_restore_scope.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main():
    fails = []

    calls = {"n": 0}
    restored = {"paths": None}

    def fake_worktree_changes():
        calls["n"] += 1
        if calls["n"] == 1:
            # The gate's own entry precondition: tree is clean, so it
            # proceeds past the "commit or stash first" early return.
            return []
        if calls["n"] == 2:
            # Computing `changed` after the (stubbed, instant) generator
            # loop: an unrelated concurrent edit to this very file landed
            # while the real generator subprocesses would have been busy.
            return ["ops/preflight.py"]
        # A third query should never happen under the fix: _restore() must
        # reuse the `changed` list from call 2, not ask again. If the old
        # buggy `_restore(worktree_changes())` is in place, it reaches here
        # and gets yet another, even-later snapshot.
        return ["ops/preflight.py", "ops/some_other_concurrent_edit.py"]

    def fake_restore(paths):
        restored["paths"] = list(paths)

    old_changes = preflight.worktree_changes
    old_chain = preflight.GENERATOR_OWNERSHIP_CHAIN
    old_restore = preflight._restore
    preflight.worktree_changes = fake_worktree_changes
    preflight.GENERATOR_OWNERSHIP_CHAIN = []
    preflight._restore = fake_restore
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_generator_ownership()
    finally:
        preflight.worktree_changes = old_changes
        preflight.GENERATOR_OWNERSHIP_CHAIN = old_chain
        preflight._restore = old_restore

    if restored["paths"] is None:
        fails.append("_restore() was never called at all")
    elif "ops/some_other_concurrent_edit.py" in restored["paths"]:
        fails.append(
            "_restore() was called with a THIRD, even-later "
            "worktree_changes() snapshot instead of reusing the `changed` "
            "list already computed right after the generator run. Got: %r"
            % restored["paths"])
    elif restored["paths"] != ["ops/preflight.py"]:
        fails.append(
            "_restore() was called with an unexpected path set: %r"
            % restored["paths"])
    if calls["n"] > 2:
        fails.append(
            "worktree_changes() was queried a third time (%d total); the "
            "restore step must reuse the `changed` snapshot from the "
            "second query, not ask again" % calls["n"])

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: restore is scoped to the generator run's own `changed` set, "
          "not a fresh, later worktree_changes() query")
    return 0


if __name__ == "__main__":
    sys.exit(main())
