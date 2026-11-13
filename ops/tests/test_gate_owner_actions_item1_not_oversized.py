#!/usr/bin/env python3
"""
Prove gate_owner_actions_item1_not_oversized() can actually fail (warn)
on a real, unrotated item-1 closed narrative, and stays silent once it
has been rotated down. A gate that cannot go red is theatre (ops/
preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_item1_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                    # noqa: E402
import rotate_owner_actions_item1_youtube as roa1                   # noqa: E402


def _oa_text(a_body, b_body):
    return (
        "# Owner actions\n\n### 1. Authorise YouTube uploads\n\n"
        + roa1.A_START_AFTER + a_body + roa1.A_END_BEFORE
        + " more setup steps.\n\n"
        + roa1.B_START_AFTER + b_body + roa1.B_END_BEFORE
        + " youtube.upload and youtube.force-ssl.\n"
    )


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_item1_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    GATE = "owner-actions-item1-not-oversized"

    # 1. A real, unrotated two-block chain must warn. The actual shape
    #    found 2026-11-13.
    stale_text = _oa_text(
        "What this looked like yesterday is worth keeping, because it "
        "is why the item changed. A long paragraph about the old "
        "done_items() bug.",
        "**Two things that were missing and are now done, 2026-09-27, "
        "so step 5 is safe to perform.** A long paragraph about the "
        "setup fixes.")
    with tempfile.TemporaryDirectory() as tmp:
        fails1, warns1 = _run_gate(tmp, stale_text)
    if fails1:
        fails.append("gate should WARN, not FAIL, on an unrotated chain: "
                      "%r" % (fails1,))
    if not any(g == GATE for g, _ in warns1):
        fails.append("gate did not warn on a synthetic unrotated chain: %r"
                      % (warns1,))

    # 2. A freshly rotated file (both pointer replacements live) stays
    #    silent.
    clean_text = _oa_text(
        (roa1.A_REPLACEMENT % "2026-11-13").rstrip(),
        (roa1.B_REPLACEMENT % "2026-11-13").rstrip())
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
            preflight.gate_owner_actions_item1_not_oversized()
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
            _, archived = roa1.plan_rotation(real_text)
        except ValueError as e:
            fails.append("plan_rotation raised on the real committed "
                          "file: %s" % e)
        else:
            if archived:
                fails.append("the real committed OWNER-ACTIONS.md still "
                              "has an unrotated item-1 chain: %r" %
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
