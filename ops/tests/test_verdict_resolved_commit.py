#!/usr/bin/env python3
"""
Prove preflight.verdict_resolved_commit() prefers a verdict file's own
recorded "commit" field over the build_id text-search heuristic, and that
it still falls back correctly for an older verdict file that has no such
field.

Found live 2026-11-24, scheduled operator cycle: resolve_verdict_commit()
answers "which commit first produced this exact build_id text" via `git
log -S`. That silently understates the real deployed commit whenever a
later commit leaves site/build-id.txt's bytes unchanged. Confirmed this
exact shape in the real repository this cycle: build `38694f470174306e`
resolved (via the heuristic) to `b65f97ba0`, even though GitHub's own
deploy.yml run #468 (success, confirmed independently via the Actions
API) had since redeployed `a185a451`, two further material commits
along, because neither of the two intervening commits changed that one
file's bytes. ops/deploy.py now records the true commit directly
("commit") instead of leaving every reader to guess it. This test does
not need real git history: it only proves the preference order.

Run:  python ops/tests/test_verdict_resolved_commit.py
"""
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Verdict has a recorded "commit": must be used directly, without
    #    ever calling the text-search heuristic (patched to explode if
    #    called, so a silent fallback would fail loudly, not quietly).
    with mock.patch.object(
            preflight, "resolve_verdict_commit",
            side_effect=AssertionError("heuristic should not run")):
        got = preflight.verdict_resolved_commit(
            {"build_id": "38694f470174306e", "commit": "a185a451"})
    if got != "a185a451":
        fails.append("recorded commit present: expected 'a185a451', got %r"
                     % got)

    # 2. Verdict has no "commit" (an older verdict file, written before
    #    this fix): must fall back to the heuristic, called with the
    #    verdict's own build_id.
    with mock.patch.object(preflight, "resolve_verdict_commit",
                            return_value="b65f97ba0") as m:
        got = preflight.verdict_resolved_commit(
            {"build_id": "38694f470174306e"})
    if got != "b65f97ba0":
        fails.append("no recorded commit: expected fallback 'b65f97ba0', "
                     "got %r" % got)
    m.assert_called_once_with("38694f470174306e")

    # 3. Verdict has an empty-string "commit" (falsy, same as absent):
    #    must still fall back, not return the empty string.
    with mock.patch.object(preflight, "resolve_verdict_commit",
                            return_value="b65f97ba0"):
        got = preflight.verdict_resolved_commit(
            {"build_id": "38694f470174306e", "commit": ""})
    if got != "b65f97ba0":
        fails.append("empty-string commit: expected fallback, got %r" % got)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 3 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
