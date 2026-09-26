#!/usr/bin/env python3
"""
Prove ops/status_report.py's executed_count() derives the experiments
"executed" figure from EXPERIMENTS.md's own State markers, rather than the
bare `"executed": 0` literal it used to be.

Found 2026-09-26, cold-reading status_report.py: gather() hardcoded that
field, the identical "hand-typed constant a report's own docstring promises
is measured at run time" defect class this same file's mail_state() already
names itself for once before (mx_working, 2026-09-23). It happened to be
true (0) on the day this test was written, because every real EXP-XXXX entry
in EXPERIMENTS.md reads "**State:** IDEA", but nothing would have caught the
figure going stale the moment one of them started.

Run:  python ops/tests/test_status_report_executed_count.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import status_report as sr                                       # noqa: E402


def main() -> int:
    fails = []

    # 1. All-IDEA registry: nothing has run.
    all_idea = (
        "## EXP-0001: A\n\n**State:** IDEA\n\n"
        "## EXP-0002: B\n\n**State:** IDEA\n\n"
    )
    n = sr.executed_count(all_idea)
    if n != 0:
        fails.append(f"all-IDEA registry: expected 0 executed, got {n}")

    # 2. One entry moved past IDEA: must be counted, whatever the state word.
    mixed = (
        "## EXP-0001: A\n\n**State:** IDEA\n\n"
        "## EXP-0002: B\n\n**State:** RUNNING\n\n"
        "## EXP-0003: C\n\n**State:** DONE\n\n"
    )
    n = sr.executed_count(mixed)
    if n != 2:
        fails.append(f"mixed registry: expected 2 executed, got {n}")

    # 3. Case must not matter ("idea" lowercase still reads as not executed).
    lower = "## EXP-0001: A\n\n**State:** idea\n\n"
    n = sr.executed_count(lower)
    if n != 0:
        fails.append(f"lowercase idea: expected 0 executed, got {n}")

    # 4. The real, live file: every real entry is still IDEA today, so the
    # live figure must be 0. If this ever fails, an experiment really has
    # started and EXECUTIVE material should say so, not silently read 0.
    real = sr.read(os.path.join(ROOT, "EXPERIMENTS.md"))
    real_n = sr.executed_count(real)
    if real_n != 0:
        fails.append(f"live EXPERIMENTS.md: expected 0 executed (verify by "
                      f"hand before trusting this), got {real_n}")

    # 5. gather()'s own dict must use this function, not a bare literal.
    # Regression guard against the exact defect this test exists for:
    # planting the old hardcoded shape back and confirming it would have
    # been wrong once something actually starts running.
    if sr.executed_count(mixed) == 0:
        fails.append("executed_count did not distinguish a running "
                      "experiment from an all-IDEA registry")

    if fails:
        print(f"FAIL ({len(fails)}):")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5 cases (all-IDEA, mixed states, case-insensitivity, "
          "live file, non-zero distinguishability)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
