#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_tests(skip=True) actually skips running the
suite (never globs or launches a single ops/tests/test_*.py file) and warns
by name, rather than silently passing or still paying the real cost; and
that main() both wires the new --skip-tests flag through to gate_tests()
and keeps its own end-of-run cycle_signal note honest about the narrower
scope, instead of letting a skipped suite masquerade as a genuinely clean
pass.

Found 2026-10-31: gate_build_id_current (and, on 2026-10-21,
gate_owner_actions_last_measured_current before it) each went red in CI
after a push that a local run never caught, because both are pure,
no-browser, no-network gates sitting after gate_tests in main()'s own
call order, and gate_tests itself costs roughly 90 minutes of real wall
time in this sandbox (ops/NIGHTLY-LOG.md, 2026-10-28), far longer than
any cycle's usual timeout. Each incident was fixed by relocating that one
gate ahead of gate_tests, but the same exposure still applies to the
roughly 300 other gates still sitting after gate_tests today. Relocating
one gate at a time only ever fixes the gate that already went red;
--skip-tests lets a run decline gate_tests' own cost on purpose and still
reach every gate after it in the same pass, so the next such incident is
caught locally before push instead of in CI after it.

Run:  python ops/tests/test_gate_tests_skip_flag.py
"""
import inspect
import os
import sys
import unittest.mock as mock

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                 # noqa: E402


def main() -> int:
    fails = []

    # 1. skip=True must WARN by name and must never touch glob.glob (i.e.
    #    never even look for test files, let alone run one). Patching
    #    glob.glob to raise proves this directly: if gate_tests(skip=True)
    #    globbed anyway, this call would raise and the test would error
    #    rather than quietly pass.
    preflight.FAIL.clear()
    preflight.WARN.clear()
    with mock.patch.object(preflight.glob, "glob",
                            side_effect=AssertionError(
                                "gate_tests(skip=True) must not glob for "
                                "test files at all")):
        preflight.gate_tests(skip=True)
    if preflight.FAIL:
        fails.append(f"skip=True must never FAIL, got {preflight.FAIL}")
    if len(preflight.WARN) != 1:
        fails.append(f"skip=True must record exactly 1 WARN, got {preflight.WARN}")
    elif "skip" not in preflight.WARN[0][1] and "skipped" not in preflight.WARN[0][1]:
        fails.append(f"the WARN must say the suite was skipped, got {preflight.WARN[0]}")

    # 2. The default (skip=False, and calling with no argument at all, the
    #    exact shape test_gate_tests_timeout_guarded.py and CI's own
    #    checks.yml both use) must still behave as before: no test files on
    #    a repo with none found is silently fine, not a WARN or FAIL, and it
    #    DOES call glob.glob rather than skip the lookup.
    preflight.FAIL.clear()
    preflight.WARN.clear()
    globbed = []

    def _fake_glob(pattern):
        globbed.append(pattern)
        return []

    with mock.patch.object(preflight.glob, "glob", side_effect=_fake_glob):
        preflight.gate_tests()
    if not globbed:
        fails.append("gate_tests() with no argument must still glob for "
                      "test files; default must stay the real suite, not skip")
    if preflight.FAIL or preflight.WARN:
        fails.append(f"gate_tests() with zero test files found must stay "
                      f"silent, got FAIL={preflight.FAIL} WARN={preflight.WARN}")

    # 3. main() itself must read a real --skip-tests flag from sys.argv and
    #    pass it through to gate_tests via run_gate, not just accept the
    #    parameter in isolation. Read main()'s own source rather than drive
    #    a real ~90-minute run.
    src = inspect.getsource(preflight.main)
    if '"--skip-tests" in sys.argv' not in src:
        fails.append("main() does not read a real --skip-tests flag from "
                      "sys.argv; the parameter exists but nothing sets it")
    if "run_gate(gate_tests, skip_tests)" not in src:
        fails.append("main() does not pass the parsed flag through to "
                      "run_gate(gate_tests, ...); gate_tests(skip=True) is "
                      "unreachable from the command line")

    # 4. The end-of-run cycle_signal note must stay honest when skip_tests
    #    was used: a run that explicitly declined gate_tests is not the
    #    "genuinely clean pass" cycle_signal.py's own docstring means, so
    #    main() must branch on skip_tests before recording, not call
    #    maybe_record_cycle_signal(FAIL) the same bare way it does for a
    #    real full pass.
    if "if skip_tests:" not in src or "near-full pass via --skip-tests" not in src:
        fails.append("main()'s end-of-run cycle_signal recording does not "
                      "visibly branch on skip_tests with an honest note; a "
                      "--skip-tests run risks being recorded as a genuinely "
                      "clean pass, which --check would then trust as SAME")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: gate_tests(skip=True) never globs and warns by name, "
          "gate_tests() with no argument is unchanged, main() wires "
          "--skip-tests through to the call site, and the end-of-run "
          "cycle_signal note stays honest about the narrower scope, 4/4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
