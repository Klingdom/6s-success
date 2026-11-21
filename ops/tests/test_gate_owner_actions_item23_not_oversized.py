#!/usr/bin/env python3
"""
Prove gate_owner_actions_item23_not_oversized() can actually fail (warn)
on a real, unrotated item-23 cadence-cost narrative, and stays silent
once it has been rotated down. A gate that cannot go red is theatre
(ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_item23_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                    # noqa: E402
import rotate_owner_actions_item23_cadence as roa23                 # noqa: E402


def _oa_text(body):
    return (
        "# Owner actions\n\n"
        + roa23.START_AFTER
        + body
        + roa23.END_BEFORE
        + " `update_trigger` and the Routines page both belong to "
        "whoever created each Routine.\n"
    )


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_item23_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    GATE = "owner-actions-item23-not-oversized"

    # 1. A real, unrotated narrative must warn. The actual shape found
    #    2026-11-21.
    stale_text = _oa_text(
        "**Raised twice already (issue #40, issue #42) and not yet "
        "acted on.** A long paragraph about 206 commits in 28 hours "
        "and ten open GitHub issues.")
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate should WARN, not FAIL, on an unrotated "
                      "narrative: %r" % (fails1,))
    if not any(g == GATE for g, _ in warns1):
        fails.append("gate did not warn on a synthetic unrotated "
                      "narrative: %r" % (warns1,))

    # 2. A freshly rotated file (the pointer replacement live) stays
    #    silent.
    clean_text = _oa_text((roa23.REPLACEMENT % "2026-11-21").rstrip())
    with tempfile.TemporaryDirectory() as tmp:
        fails2, warns2 = _run_gate(tmp, clean_text)
    if fails2:
        fails.append("gate should not FAIL on a clean file: %r" % (fails2,))
    if any(g == GATE for g, _ in warns2):
        fails.append("gate warned on a freshly rotated file: %r" % (warns2,))

    # 3. No OWNER-ACTIONS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_owner_actions_item23_not_oversized()
        except Exception as exc:  # noqa: BLE001
            fails.append("gate crashed with no OWNER-ACTIONS.md present: "
                          "%r" % (exc,))
        finally:
            preflight.ROOT = old_root

    # 4. A file missing this item's anchors entirely (drifted past
    #    recognition) warns rather than silently passing: unchecked is
    #    not passing, CLAUDE.md 0.4.
    unrelated_text = "# Owner actions\n\nnothing recognisable here.\n"
    with tempfile.TemporaryDirectory() as tmp:
        fails4, warns4 = _run_gate(tmp, unrelated_text)
    if fails4:
        fails.append("gate should WARN, not FAIL, on a file missing its "
                      "anchors: %r" % (fails4,))
    if not any(g == GATE for g, _ in warns4):
        fails.append("gate stayed silent on a file missing its anchors "
                      "instead of warning unchecked: %r" % (warns4,))

    # 5. The real committed file, after this cycle's own --apply, stays
    #    silent too.
    real_path = os.path.join(ROOT, "OWNER-ACTIONS.md")
    if os.path.exists(real_path):
        real_text = io.open(real_path, encoding="utf-8").read()
        try:
            _, archived = roa23.plan_rotation(real_text)
        except ValueError as e:
            fails.append("plan_rotation raised on the real committed "
                          "file: %s" % e)
        else:
            if archived:
                fails.append("the real committed OWNER-ACTIONS.md still "
                              "has an unrotated item-23 narrative: %r" %
                              ([label for label, _ in archived],))

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5/5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
