#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_ops_test_suite_matches_gate_tests() catches
checks.yml's "The ops test suite" step losing SIXS_UNDER_PREFLIGHT, and
leaves a correct file alone.

Found 2026-09-13, run 917, the very next real CI run after the same day's
`timeout 700` fix to this exact step landed. test_generator_ownership.py
failed by name at exactly 700s: not hung, not a real regression. Its own
main() drives a full `preflight.py --own` in a throwaway git worktree
(that inner call alone allows up to 1800s) specifically when it cannot
see SIXS_UNDER_PREFLIGHT in its environment, and skips straight to
"skipped: preflight is the caller" and returns 0 when it can, which is
exactly the variable gate_tests() in preflight.py already sets before
running these same test files, for the identical recursion reason.
checks.yml's shell loop calls python3 on each file directly, mirroring
gate_tests()'s invocation in every other respect, but never set this one
variable, so it always took the slow, standalone path instead of skipping,
and failed the step's own 700s bound. Fixed by exporting
SIXS_UNDER_PREFLIGHT=1 before the loop; this test protects that fix from
silently regressing.

Run:  python ops/tests/test_gate_ops_test_suite_env.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CORRECT = """\
      - name: The ops test suite
        run: |
          set -e
          export SIXS_UNDER_PREFLIGHT=1
          for t in ops/tests/test_*.py; do
            echo "--- $t"
            timeout 700 python3 "$t" && rc=0 || rc=$?
            if [ "$rc" -eq 124 ]; then
              echo "::error::$t did not finish within 700s"
            fi
            if [ "$rc" -ne 0 ]; then
              exit "$rc"
            fi
          done

      - name: Product copy has not drifted from the catalogue
        run: python3 ops/audit_catalog.py
"""

MISSING_VAR = """\
      - name: The ops test suite
        run: |
          set -e
          for t in ops/tests/test_*.py; do
            echo "--- $t"
            timeout 700 python3 "$t" && rc=0 || rc=$?
            if [ "$rc" -eq 124 ]; then
              echo "::error::$t did not finish within 700s"
            fi
            if [ "$rc" -ne 0 ]; then
              exit "$rc"
            fi
          done

      - name: Product copy has not drifted from the catalogue
        run: python3 ops/audit_catalog.py
"""

NO_STEP = """\
      - name: Something else entirely
        run: echo hello
"""


def _run(text: str):
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "checks.yml")
        io.open(path, "w", encoding="utf-8").write(text)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_ops_test_suite_matches_gate_tests(wf_path=path)
        return list(preflight.FAIL)
    finally:
        shutil.rmtree(tmp)


def test_correct_step_passes():
    fails = _run(CORRECT)
    assert not fails, "a step that exports SIXS_UNDER_PREFLIGHT should pass: %r" % (fails,)


def test_missing_var_fails_by_name():
    fails = _run(MISSING_VAR)
    assert fails, "a step missing SIXS_UNDER_PREFLIGHT should fail"
    msg = fails[0][1]
    assert "SIXS_UNDER_PREFLIGHT" in msg


def test_no_step_at_all_is_a_different_failure():
    """If the step is renamed or removed entirely, that is a bigger
    regression than this gate exists to catch, but it must still fail
    loudly rather than silently pass because there was nothing to check."""
    fails = _run(NO_STEP)
    assert fails, "a checks.yml missing the step entirely should fail"


def test_real_repository_is_clean():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_ops_test_suite_matches_gate_tests()
    fails = list(preflight.FAIL)
    assert not fails, "the real checks.yml should be clean: %r" % (fails,)


TESTS = [test_correct_step_passes, test_missing_var_fails_by_name,
         test_no_step_at_all_is_a_different_failure,
         test_real_repository_is_clean]


def main():
    n = 0
    for t in TESTS:
        t()
        n += 1
    print("  %d of %d cases pass" % (n, len(TESTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
