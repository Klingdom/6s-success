#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_routine_prompt_current() catches the real
defect found 2026-09-15: ops/routine-prompt.md, this repo's own committed
mirror of the live scheduled operator prompt, had silently dropped three
sentences that the live prompt this exact cycle received still carried
(two privacy rules and one operational lesson about a metric reading the
wrong source). This is the same drift class fixed once already on
2026-09-08 (R4 in OWNER-ACTIONS.md), recurring because nothing re-checked
it after that fix.

FAIL.append is monkeypatched here rather than calling preflight.main(), so
this test does not depend on every other gate in the file also passing in
this environment.

Run:  python ops/tests/test_gate_routine_prompt_current.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_PATH = os.path.join(ROOT, "ops", "routine-prompt.md")


def run_gate_against(path) -> list:
    """Point the gate at a given file path and return what it FAILed with."""
    original = preflight.FAIL
    preflight.FAIL = []
    real_join = os.path.join
    try:
        def fake_join(*parts):
            if len(parts) >= 2 and parts[-2] == "ops" \
                    and parts[-1] == "routine-prompt.md":
                return path
            return real_join(*parts)
        os.path.join = fake_join
        preflight.gate_routine_prompt_current()
        return list(preflight.FAIL)
    finally:
        os.path.join = real_join
        preflight.FAIL = original


def main() -> int:
    fails = []

    # 1. A file missing the two privacy sentences and the metric lesson,
    #    exactly the real 2026-09-15 drift shape, must fail.
    drifted = (
        "STEP 0. ATTACH TO A BRANCH.\n"
        "some other content\n"
        "STEP 13. ESCALATE, DO NOT DECIDE.\n"
    )
    missing = [l for l in preflight.ROUTINE_PROMPT_REQUIRED_LINES
               if l not in drifted]
    if not missing:
        fails.append("the drifted fixture was not detected as missing lines")

    # 2. The real, current committed file must read clean.
    text = io.open(REAL_PATH, encoding="utf-8").read()
    missing = [l for l in preflight.ROUTINE_PROMPT_REQUIRED_LINES
               if l not in text]
    if missing:
        fails.append(f"the real, current ops/routine-prompt.md is missing "
                     f"{missing}, so the fix did not actually land")

    # 3. A missing file must fail by name, not crash.
    result = run_gate_against(os.path.join(ROOT, "ops", "does-not-exist.md"))
    if not result or result[0][0] != "routine-prompt":
        fails.append("a missing routine-prompt.md was not failed by name")

    # 4. The real file, run through the actual gate function end to end
    #    (not just the substring check above), must pass clean.
    result = run_gate_against(REAL_PATH)
    if result:
        fails.append(f"the real file failed the real gate: {result}")

    # 5. A file missing just one required line must still fail, not just a
    #    file missing all of them.
    almost = io.open(REAL_PATH, encoding="utf-8").read().replace(
        "Never write a customer's name, email or address into this "
        "repository.", "")
    import tempfile
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(almost)
        tmp_path = fh.name
    try:
        result = run_gate_against(tmp_path)
        if not result:
            fails.append("a file missing exactly one required line still "
                         "passed")
    finally:
        os.unlink(tmp_path)

    total = 5
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
