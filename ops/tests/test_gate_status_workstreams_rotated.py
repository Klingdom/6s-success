#!/usr/bin/env python3
"""
Prove gate_status_workstreams_rotated() can actually fail (warn) on a
real unarchived Workstream 3 narrative, stays silent once it has been
rotated down to the pointer, and warns again if new text is appended
after the pointer. A gate that cannot go red is theatre (ops/preflight.py's
own stated rule).

Run:  python ops/tests/test_gate_status_workstreams_rotated.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                          # noqa: E402
import rotate_status_workstreams as rsw                    # noqa: E402

NARRATIVE = (
    "**First done, 2026-09-07.** Some real build-log entry.\n\n"
    "**Nineteenth done, 2026-09-29.** Another real build-log entry."
)

UNROTATED_DOC = (
    "# STATUS.md\n\n"
    "# 14. Active Major Workstreams\n\n"
    "Workstream 3 is closed, and ship the free unillustrated Kitchen "
    "deck.\n\n" + NARRATIVE + "\n\n---\n\n# 15. Current Experiments\n\n"
    "Nothing else here.\n"
)


def _run_gate(tmp, text):
    io.open(os.path.join(tmp, "STATUS.md"), "w",
            encoding="utf-8").write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_status_workstreams_rotated()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []

    # 1. A real, unarchived narrative must warn, not fail.
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, UNROTATED_DOC)
    if fails1:
        fails.append("gate should WARN, not FAIL, on an unarchived "
                      "narrative: %r" % fails1)
    if not warns1:
        fails.append("gate stayed silent on a real unarchived narrative")

    # 2. Once rotated (the real tool's own output), the same document
    #    stays silent.
    rotated_text, archived = rsw.plan_rotation(UNROTATED_DOC)
    if not archived:
        fails.append("plan_rotation did not archive anything on the "
                      "unrotated fixture; test fixture itself is wrong")
    with tempfile.TemporaryDirectory() as tmp:
        fails2, warns2 = _run_gate(tmp, rotated_text)
    if fails2 or warns2:
        fails.append("gate fired on a freshly rotated document: "
                      "fail=%r warn=%r" % (fails2, warns2))

    # 3. Running plan_rotation a second time on the rotated text is a
    #    no-op (idempotent), matching the live --apply behaviour.
    rotated_again, archived_again = rsw.plan_rotation(rotated_text)
    if archived_again is not None or rotated_again != rotated_text:
        fails.append("plan_rotation is not idempotent on already-"
                      "rotated text")

    # 4. New narrative appended after the pointer (the regrowth case
    #    this gate exists to catch) must warn again.
    regrown_text = rotated_text.replace(
        "\n\n---\n\n# 15. Current Experiments",
        "\n\n**Twentieth done, 2026-10-24.** A new entry landed back "
        "under the closure summary.\n\n---\n\n# 15. Current Experiments",
    )
    with tempfile.TemporaryDirectory() as tmp:
        fails4, warns4 = _run_gate(tmp, regrown_text)
    if fails4:
        fails.append("gate should WARN, not FAIL, on regrown "
                      "narrative: %r" % fails4)
    if not warns4:
        fails.append("gate stayed silent on narrative regrown after "
                      "the pointer")

    # 5. A missing anchor (the section restructured out from under the
    #    tool) warns rather than crashing.
    no_anchor_text = UNROTATED_DOC.replace(
        "and ship the free unillustrated Kitchen deck.", "rewritten")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            fails5, warns5 = _run_gate(tmp, no_anchor_text)
        except Exception as e:
            fails.append("gate crashed on a missing anchor instead of "
                          "warning: %r" % e)
        else:
            if fails5:
                fails.append("gate should WARN, not FAIL, on a missing "
                              "anchor: %r" % fails5)
            if not warns5:
                fails.append("gate stayed silent with its anchor "
                              "missing")

    # 6. A missing STATUS.md is a silent no-op, not a crash.
    with tempfile.TemporaryDirectory() as tmp:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_status_workstreams_rotated()
        except Exception as e:
            fails.append("gate crashed with no STATUS.md present: %r" % e)
        finally:
            preflight.ROOT = old_root

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 6/6 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
