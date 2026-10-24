#!/usr/bin/env python3
"""
Prove gate_owner_actions_closed_items_rotated() can actually fail (warn)
on a real unarchived closed item and stays silent once it has been
rotated down to a pointer. A gate that cannot go red is theatre
(ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_owner_actions_closed_items_rotated.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                 # noqa: E402
import rotate_owner_actions_closed_items as roaci                # noqa: E402

DOC = (
    "# Owner actions\n\n"
    "## Open, ranked by what they unblock\n\n"
    "### T0. A genuinely open item, left alone.\n\n"
    "This one is still live.\n\n"
    "### ~~T1. A fully closed single-header item.~~\n\n"
    "Body text for T1, no longer needed.\n"
)

SYNTH_GROUPS = [["### ~~T1. A fully closed single-header item.~~"]]
SYNTH_POINTERS = {
    "### ~~T1. A fully closed single-header item.~~":
        "~~T1. A fully closed single-header item.~~ DONE. Full text "
        "archived to `OWNER-ACTIONS-ARCHIVE.md`.",
}


def _run_gate(tmp, oa_text):
    io.open(os.path.join(tmp, "OWNER-ACTIONS.md"), "w",
            encoding="utf-8").write(oa_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_owner_actions_closed_items_rotated()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    orig_groups, orig_pointers = roaci.GROUPS, roaci.POINTERS
    roaci.GROUPS, roaci.POINTERS = SYNTH_GROUPS, SYNTH_POINTERS
    try:
        # 1. A real, unarchived closed item must warn.
        with tempfile.TemporaryDirectory() as tmp:
            fails1, warns1 = _run_gate(tmp, DOC)
        if fails1:
            fails.append("gate should WARN, not FAIL, on an unarchived "
                          "closed item: %r" % fails1)
        if not warns1:
            fails.append("gate stayed silent on a real unarchived "
                          "closed item")

        # 2. The still-open item alone, with no closed item present,
        #    must stay clean.
        open_only = (
            "# Owner actions\n\n## Open, ranked by what they unblock\n\n"
            "### T0. A genuinely open item, left alone.\n\n"
            "This one is still live.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            fails2, warns2 = _run_gate(tmp, open_only)
        if fails2 or warns2:
            fails.append("gate fired with no closed item present: "
                          "fail=%r warn=%r" % (fails2, warns2))

        # 3. Once rotated, the same document stays silent.
        rotated_text, _, _ = roaci.plan_rotation(DOC, today="2026-01-01")
        with tempfile.TemporaryDirectory() as tmp:
            fails3, warns3 = _run_gate(tmp, rotated_text)
        if fails3 or warns3:
            fails.append("gate fired on a freshly rotated document: "
                          "fail=%r warn=%r" % (fails3, warns3))

        # 4. A missing OWNER-ACTIONS.md is a silent no-op, not a crash.
        with tempfile.TemporaryDirectory() as tmp:
            old_root = preflight.ROOT
            preflight.ROOT = tmp
            preflight.FAIL, preflight.WARN = [], []
            try:
                preflight.gate_owner_actions_closed_items_rotated()
            except Exception as e:
                fails.append("gate crashed with no OWNER-ACTIONS.md "
                              "present: %r" % e)
            finally:
                preflight.ROOT = old_root
    finally:
        roaci.GROUPS, roaci.POINTERS = orig_groups, orig_pointers

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 4/4 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
