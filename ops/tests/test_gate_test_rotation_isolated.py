#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_test_rotation_isolated() catches the real
defect found 2026-09-15: test_linkedin_drafts.py and test_social_drafts.py
both called build(..., record=True) against the real, git-tracked
ops/corpus-rotation.json, restoring it only in a `finally` block. A SIGTERM
sent to a Python process with no handler installed (exactly what a
`timeout`-bounded caller sends) skips `finally` entirely, so an interrupted
run left the real file permanently polluted with fake served posts.
Reproduced directly against the pre-fix code with a real subprocess and a
real SIGTERM before this gate was written.

This test uses ast-parsed synthetic file bodies rather than the real fixed
files, so it is not sensitive to future edits there, and it deliberately
includes a case shaped like THIS OWN TEST FILE: a fixture string containing
"import corpus_posts" and "record=True" as plain text data. A naive
text-scanning check would flag that shape as if it were real code; the real
gate parses the file as Python (ast) precisely so a string literal is never
mistaken for an import or a call.

Run:  python ops/tests/test_gate_test_rotation_isolated.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. The exact pre-fix shape: record=True with no ROTATION reassignment.
    unsafe = (
        "import corpus_posts as cp\n"
        "def main():\n"
        "    sd.build('facebook', record=True)\n"
    )
    problem = preflight.check_test_rotation_isolated(unsafe)
    if not problem:
        fails.append("the pre-fix shape (record=True, no ROTATION "
                     "reassignment) was not caught")

    # 2. The real, fixed shape: ROTATION reassigned to a temp path first.
    safe = (
        "import corpus_posts as cp\n"
        "def main():\n"
        "    cp.ROTATION = tmp_path\n"
        "    sd.build('facebook', record=True)\n"
    )
    problem = preflight.check_test_rotation_isolated(safe)
    if problem:
        fails.append(f"the fixed shape was wrongly flagged: {problem}")

    # 3. A file with no corpus_posts import at all must never be flagged.
    unrelated = "import os\ndef main():\n    pass\n"
    problem = preflight.check_test_rotation_isolated(unrelated)
    if problem:
        fails.append(f"an unrelated file was wrongly flagged: {problem}")

    # 4. record=True present but for an unrelated import (different alias,
    #    corpus_posts never imported) must never be flagged.
    different_kwarg = (
        "import something_else as se\n"
        "def main():\n"
        "    se.build(record=True)\n"
    )
    problem = preflight.check_test_rotation_isolated(different_kwarg)
    if problem:
        fails.append(f"an unrelated record=True call was wrongly flagged: "
                     f"{problem}")

    # 5. The false-positive risk this gate itself creates: a fixture STRING
    #    that merely contains the trigger text, not real code. Must not be
    #    flagged, or this gate would fail on its own test file forever.
    fixture_shaped = (
        "import preflight\n"
        "def main():\n"
        "    old_text = '''\n"
        "import corpus_posts as cp\n"
        "def main():\n"
        "    sd.build(\"facebook\", record=True)\n"
        "'''\n"
        "    print(preflight.check_test_rotation_isolated(old_text))\n"
    )
    problem = preflight.check_test_rotation_isolated(fixture_shaped)
    if problem:
        fails.append(f"a fixture string was mistaken for real code: "
                     f"{problem}")

    # 6. Direct proof against this gate's own two real, currently-fixed
    #    target files: both must read clean.
    for name in ("test_linkedin_drafts.py", "test_social_drafts.py"):
        p = os.path.join(ROOT, "ops", "tests", name)
        import io
        text = io.open(p, encoding="utf-8").read()
        problem = preflight.check_test_rotation_isolated(text)
        if problem:
            fails.append(f"the real, already-fixed {name} was flagged: "
                         f"{problem}")

    total = 6
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
