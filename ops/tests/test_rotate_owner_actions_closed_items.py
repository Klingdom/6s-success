#!/usr/bin/env python3
"""
Prove ops/rotate_owner_actions_closed_items.py archives OWNER-ACTIONS.md's
fully-closed numbered items correctly: a closed single-header item and a
closed multi-header item both move verbatim under one pointer each, a
still-open item (no "closed" marker in its header) is left untouched, a
repeated run is a no-op, and a group missing one of its own headers (a
partial, inconsistent archive) is refused rather than guessed past.

Run:  python ops/tests/test_rotate_owner_actions_closed_items.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_owner_actions_closed_items as m                    # noqa: E402

SYNTH_GROUPS = [
    ["### ~~T1. A fully closed single-header item.~~"],
    [
        "### ~~T2. A fully closed item with a superseded follow-up.~~",
        "### T2b. Superseded",
    ],
]
SYNTH_POINTERS = {
    "### ~~T1. A fully closed single-header item.~~":
        "~~T1. A fully closed single-header item.~~ DONE. Full text "
        "archived to `OWNER-ACTIONS-ARCHIVE.md`.",
    "### ~~T2. A fully closed item with a superseded follow-up.~~":
        "~~T2. A fully closed item with a superseded follow-up.~~ DONE. "
        "Full text archived to `OWNER-ACTIONS-ARCHIVE.md`.",
}

DOC = (
    "# Owner actions\n\n"
    "## Open, ranked by what they unblock\n\n"
    "### T0. A genuinely open item, left alone.\n\n"
    "This one is still live and must survive every run untouched.\n\n"
    "### ~~T1. A fully closed single-header item.~~\n\n"
    "Body text for T1, no longer needed.\n\n"
    "### ~~T2. A fully closed item with a superseded follow-up.~~\n\n"
    "Current state for T2.\n\n"
    "### T2b. Superseded\n\n"
    "Old, dead detail for T2.\n\n"
    "### T3. Another open item, after everything else.\n\n"
    "Also still live.\n"
)


def main() -> int:
    fails = []
    orig_groups, orig_pointers = m.GROUPS, m.POINTERS
    m.GROUPS, m.POINTERS = SYNTH_GROUPS, SYNTH_POINTERS
    try:
        # 1. A clean rotation moves both groups, leaves the open items
        #    untouched, and reports the correct total byte count.
        new_text, archive_entry, total = m.plan_rotation(DOC, today="2026-01-01")
        if "T0. A genuinely open item" not in new_text:
            fails.append("the untouched open item (T0) vanished")
        if "T3. Another open item" not in new_text:
            fails.append("the untouched open item (T3) vanished")
        if "Body text for T1" in new_text:
            fails.append("T1's body stayed in the live file")
        if "T2b. Superseded" in new_text or "Old, dead detail for T2" in new_text:
            fails.append("T2's superseded follow-up stayed in the live file")
        if SYNTH_POINTERS["### ~~T1. A fully closed single-header item.~~"] \
                not in new_text:
            fails.append("T1's pointer line is missing from the live file")
        if "Body text for T1" not in archive_entry:
            fails.append("T1's body did not reach the archive entry")
        if "Old, dead detail for T2" not in archive_entry:
            fails.append("T2's superseded follow-up did not reach the archive entry")
        if total <= 0:
            fails.append("a real rotation reported 0 due bytes")

        # 2. A second run against the already-rotated text is a no-op:
        #    same text back, no archive entry, 0 due bytes.
        again_text, again_entry, again_total = m.plan_rotation(
            new_text, today="2026-01-02")
        if again_text != new_text or again_entry or again_total:
            fails.append("re-running against already-rotated text was not a no-op")

        # 3. A group missing one of its own headers (T2's main header
        #    present, its T2b follow-up deleted by hand) is refused
        #    rather than silently archived as if complete.
        broken = DOC.replace(
            "### T2b. Superseded\n\n"
            "Old, dead detail for T2.\n\n", "")
        try:
            m.plan_rotation(broken, today="2026-01-01")
            fails.append("a partially-archived group was silently accepted")
        except SystemExit:
            pass

        # 4. A duplicated header for the same label is refused.
        dup = DOC + "\n### ~~T1. A fully closed single-header item.~~\n\nDup.\n"
        try:
            m.plan_rotation(dup, today="2026-01-01")
            fails.append("a duplicated header was silently accepted")
        except SystemExit:
            pass
    finally:
        m.GROUPS, m.POINTERS = orig_groups, orig_pointers

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 4/4 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
