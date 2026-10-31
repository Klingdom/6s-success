#!/usr/bin/env python3
"""
Prove main()'s cycle_signal recording checkpoint sits BEFORE gate_tests,
not after it.

Found 2026-10-25: maybe_record_cycle_signal(FAIL) was added 2026-10-19
(test_preflight_cycle_signal_record.py) right at the end of main(), after
gate_tests and roughly 150 more gates. gate_tests hangs on every sandbox
this project has run in and the process is SIGKILLed there (see the
comment above bootstrap_fresh_sandbox and gate_ci_conclusion_current's own
placement note, 2026-10-21), so that call has never once executed
locally since the day it shipped. The only visible symptom was a tool
that looked like it should be helping and quietly wasn't: fourteen
separate "exhaustion confirmation" cycles landed on 2026-10-25 alone,
each paying for cycle_signal.py's CHANGED path because no local run had
ever recorded a fresh snapshot after the 2026-10-19 fix, let alone the
58-cycle gap that fix itself was built to close.

The fix moved an identical checkpoint to right before gate_tests, same
idiom as the three not-oversized gates and gate_ci_conclusion_current /
gate_checks_yml_real_gap, all moved ahead of gate_tests for the exact
same "pure file work, no browser, no network, so it belongs where a
sandboxed run can actually reach it" reason.

This test does not re-prove maybe_record_cycle_signal()'s own FAIL/PASS
gating; test_preflight_cycle_signal_record.py already does that in
isolation. It proves the one thing that test cannot: ordering inside
main() itself, by reading main()'s real source text, so a future edit
that re-shuffles gate order cannot silently move the checkpoint back
behind gate_tests again without this test naming it.

Run:  python ops/tests/test_gate_tests_cycle_signal_checkpoint.py
"""
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402


def main() -> int:
    fails = []
    src = inspect.getsource(preflight.main)

    checkpoint_marker = "maybe_record_cycle_signal("
    # 2026-10-31: gate_tests() gained a skip parameter (see
    # test_gate_tests_skip_flag.py), so the real call site is now
    # "run_gate(gate_tests, skip_tests)". Matching only the open paren plus
    # comma, not the full call, so this marker survives if the parameter is
    # ever renamed.
    gate_tests_marker = "run_gate(gate_tests,"

    i_checkpoint = src.find(checkpoint_marker)
    i_gate_tests = src.find(gate_tests_marker)

    if i_checkpoint == -1:
        fails.append("no maybe_record_cycle_signal(...) call found inside main() "
                     "at all; the checkpoint was removed")
    if i_gate_tests == -1:
        fails.append("no run_gate(gate_tests) call found inside main(); "
                     "gate_tests itself was removed or renamed")
    if i_checkpoint != -1 and i_gate_tests != -1 and i_checkpoint > i_gate_tests:
        fails.append(
            "maybe_record_cycle_signal(...) is called AFTER run_gate(gate_tests) "
            "inside main(), reproducing the exact 2026-10-25 defect: gate_tests "
            "hangs in every sandbox this project runs in, the process is "
            "SIGKILLed there, and every call after it (including this one) "
            "never executes locally, so the snapshot never refreshes")

    # Fail-then-pass, proved against the real historical defect shape:
    # simulate the pre-fix ordering (checkpoint after gate_tests) and
    # confirm this same check would have caught it.
    broken_src = (
        "def main():\n"
        "    run_gate(gate_tests, skip_tests)\n"
        "    run_gate(gate_conflict_markers)\n"
        "    maybe_record_cycle_signal(FAIL)\n"
        "    return 0\n"
    )
    bi_checkpoint = broken_src.find(checkpoint_marker)
    bi_gate_tests = broken_src.find(gate_tests_marker)
    if not (bi_checkpoint != -1 and bi_gate_tests != -1
            and bi_checkpoint > bi_gate_tests):
        fails.append("the synthetic pre-fix ordering did not reproduce as "
                     "'checkpoint after gate_tests'; the fail-then-pass proof "
                     "itself is broken")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: cycle_signal checkpoint sits before run_gate(gate_tests) in "
          "main(), and the fail-then-pass proof against the historical "
          "ordering correctly flags it, 1/1 real + 1/1 synthetic case")
    return 0


if __name__ == "__main__":
    sys.exit(main())
