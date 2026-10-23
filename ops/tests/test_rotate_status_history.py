#!/usr/bin/env python3
"""
Prove ops/rotate_status_history.py keeps only the newest STATUS.md
"Production Knowledge" entry live and moves the rest into the archive
correctly: every entry ends up on exactly one side, nothing is edited, and
a file that does not match the expected shape is refused rather than
guessed past.

Run:  python ops/tests/test_rotate_status_history.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_status_history as rsh                             # noqa: E402

BEFORE = (
    "# 30. Current Overall Assessment\n\n"
    "**Operating System:** OPERATING.\n\n"
    "**Autonomous Execution Readiness:** FULL FOR GREEN-BAND WORK, more "
    "prose on this same line.\n\n"
)
AFTER = (
    "**Business Data Knowledge, re-measured:** ONE SALE.\n\n"
    "**Executive Visibility:** LIVE.\n"
)


def _chain_text(n):
    entries = []
    for i in range(n):
        entries.append("**Production Knowledge, CLOSED day-%d:** body text "
                        "for entry %d, nothing interesting." % (i, i))
    return BEFORE + "\n\n".join(entries) + "\n\n" + AFTER


def main() -> int:
    fails = []

    # 1. split_chain() finds exactly the entries between the two anchors,
    #    in order, and reconstructing before+chain+after loses nothing.
    text = _chain_text(5)
    before, lines, after = rsh.split_chain(text)
    def _day(entry):
        return int(entry.split("day-")[1].split(":")[0])

    if len(lines) != 5:
        fails.append("expected 5 entries, got %d" % len(lines))
    if [_day(l) for l in lines] != list(range(5)):
        fails.append("entries came back out of order: %r" % lines)
    if not before.endswith("same line.") or not after.startswith(
            "**Business Data Knowledge"):
        fails.append("before/after boundaries drifted: %r / %r"
                      % (before[-40:], after[:40]))

    # 2. A missing anchor is refused, not guessed past.
    try:
        rsh.split_chain(BEFORE.replace("Autonomous Execution Readiness",
                                        "Something Else") + AFTER)
        fails.append("missing start anchor was silently accepted")
    except ValueError:
        pass

    # 3. A duplicated anchor is refused.
    try:
        rsh.split_chain(text + "\n\n**Autonomous Execution Readiness:** "
                         "again.\n")
        fails.append("duplicated start anchor was silently accepted")
    except ValueError:
        pass

    # 4. A line inside the span that is not a bold entry is refused
    #    rather than silently dropped or mis-split.
    bad = BEFORE + "not a bold entry at all\n\n" + AFTER
    try:
        rsh.split_chain(bad)
        fails.append("an unrecognised line inside the span was accepted")
    except ValueError:
        pass

    # 5. plan_rotation() keeps exactly the newest entry live and returns
    #    the rest as archived, in their original order, nothing lost or
    #    duplicated.
    text5 = _chain_text(5)
    new_text, archived = rsh.plan_rotation(text5)
    _, kept_lines, _ = rsh.split_chain(new_text)
    if len(kept_lines) != 1:
        fails.append("expected 1 entry to stay live, got %d" % len(kept_lines))
    if kept_lines and "day-0" not in kept_lines[0]:
        fails.append("the entry kept live was not the newest: %r"
                      % kept_lines[0][:60])
    if len(archived) != 4:
        fails.append("expected 4 archived entries, got %d" % len(archived))
    elif [_day(e) for e in archived] != [1, 2, 3, 4]:
        fails.append("archived entries were not entries 1-4 in order: %r"
                      % archived)

    # 6. A chain already down to one entry is a no-op: plan_rotation()
    #    returns the text unchanged and an empty archive list.
    text1 = _chain_text(1)
    new_text1, archived1 = rsh.plan_rotation(text1)
    if new_text1 != text1 or archived1:
        fails.append("a single-entry chain was rotated when it should "
                     "have been left alone")

    # 7. apply_archive() with no existing archive writes a well-formed
    #    archive carrying every entry it was given, in order.
    fresh = rsh.apply_archive(["**A:** one.", "**B:** two."], None)
    if not fresh.startswith(rsh.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive missing its own header")
    if "**A:** one." not in fresh or "**B:** two." not in fresh:
        fails.append("fresh archive lost an entry")
    if fresh.index("**A:** one.") > fresh.index("**B:** two."):
        fails.append("fresh archive did not preserve entry order")

    # 8. apply_archive() onto an existing archive puts the new entries on
    #    top, keeps the old ones, in order, and does not touch the header.
    existing = (rsh.ARCHIVE_HEADER_FIRST_LINE + "\n\n> note.\n\n---\n\n"
                "**OLD:** already here.\n")
    combined = rsh.apply_archive(["**NEW:** just archived."], existing)
    if combined.index("**NEW:** just archived.") > \
            combined.index("**OLD:** already here."):
        fails.append("new archive entries were not placed above old ones")
    if "> note." not in combined:
        fails.append("existing archive header was lost on a repeat run")

    # 9. apply_archive() refuses an existing archive file with the wrong
    #    header rather than prepending onto something else.
    try:
        rsh.apply_archive(["**NEW:** x."], "# Something else entirely\n")
        fails.append("a malformed existing archive was silently accepted")
    except ValueError:
        pass

    if fails:
        print("FAILED (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("OK: all rotate_status_history.py checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
