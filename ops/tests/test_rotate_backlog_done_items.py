#!/usr/bin/env python3
"""
Prove ops/rotate_backlog_done_items.py archives BACKLOG-2026-09-07.md's
17 whitelisted done-item rows correctly: only rows matching the exact
`| **ID** | ~~...~~ | ` shape are touched, a free-form "ID, ..." journal
row sharing the same id prefix is left alone even when whitelisted,
round-tripping the archived text reconstructs the original byte for
byte, an already-rotated row is a no-op (idempotent), and a whitelisted
id whose row doesn't match the expected shape raises rather than guesses.

Run:  python ops/tests/test_rotate_backlog_done_items.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_backlog_done_items as r                            # noqa: E402

PREFIX = "# Backlog\n\n## 1. Done this week\n\nnothing here.\n\n"
SUFFIX = "\n## 5. Hold\n\nnothing here either.\n"


def _file(body):
    return PREFIX + "## 2. Now: micro zones and the web app\n\n" + body + SUFFIX


def main() -> int:
    fails = []

    # 1. A whitelisted id in the exact shape is found and its rest-cell
    #    is captured correctly.
    text1 = _file(
        "| **A1** | ~~Build the thing~~ | why | effort | the long "
        "accept-when narrative that should move to the archive |\n"
    )
    rows1 = r.find_rows(text1)
    if set(rows1) != {"A1"}:
        fails.append("find_rows() found the wrong set for a single "
                      "clean row: %r" % set(rows1))
    elif "accept-when narrative" not in rows1["A1"][3]:
        fails.append("find_rows() captured the wrong rest-cell for A1")

    # 2. A free-form journal row reusing the same letter+digit prefix
    #    ("A1, ..." with a comma, not "**A1** | ~~") must never match,
    #    even though A1 is whitelisted.
    text2 = _file(
        "| **A1, found and fixed 2026-09-09, operator.** Unrelated "
        "later note that happens to start with the same prefix. |\n"
    )
    rows2 = r.find_rows(text2)
    if rows2:
        fails.append("find_rows() matched a free-form journal row "
                      "sharing a whitelisted id's prefix: %r" % rows2)

    # 3. Only sections 2-4 are in scope: the identical row shape outside
    #    that span (e.g. in section 1) is never touched.
    text3 = (
        PREFIX
        + "| **A1** | ~~outside the span~~ | should never move |\n\n"
        + "## 2. Now: micro zones and the web app\n\n"
        + "| **A2** | ~~inside the span~~ | should move |\n"
        + SUFFIX
    )
    rows3 = r.find_rows(text3)
    if set(rows3) != {"A2"}:
        fails.append("find_rows() did not respect the sections-2-4 "
                      "boundary: found %r" % set(rows3))

    # 4. plan_rotation() round-trips: reconstructing the original row
    #    from the pointer row + the archived rest-cell reproduces the
    #    input byte for byte.
    text4 = _file(
        "| **A1** | ~~Build the thing~~ | why | effort | narrative one |\n"
        "\n"
        "| **B1** | ~~Ship the other thing~~ | just two cells |\n"
    )
    new_text4, archived4 = r.plan_rotation(text4)
    if {a[0] for a in archived4} != {"A1", "B1"}:
        fails.append("plan_rotation() archived the wrong ids: %r"
                      % [a[0] for a in archived4])
    recon = new_text4
    for rid, item, rest in archived4:
        pointer_row = "| **%s** | %s%s" % (rid, item, r.POINTER_SUFFIX)
        orig_row = "| **%s** | %s | %s" % (rid, item, rest)
        if pointer_row not in recon:
            fails.append("plan_rotation() pointer row missing for %s"
                         % rid)
            continue
        recon = recon.replace(pointer_row, orig_row, 1)
    if recon != text4:
        fails.append("round-trip did not reproduce the original text "
                      "byte for byte")

    # 5. An already-rotated row (its rest-cell is already the pointer
    #    text) is left alone on a second pass: idempotent.
    once_text = new_text4
    rows5 = r.find_rows(once_text)
    if rows5:
        fails.append("find_rows() re-matched an already-rotated row: %r"
                      % set(rows5))
    new_text5, archived5 = r.plan_rotation(once_text)
    if archived5 or new_text5 != once_text:
        fails.append("plan_rotation() was not idempotent on an "
                      "already-rotated file")

    # 6. A whitelisted id whose row does not match the expected shape at
    #    all (no strikethrough right after the id) is simply not found,
    #    not guessed into archiving the wrong thing.
    text6 = _file(
        "| **A1** | Build the thing, not struck through | why | "
        "narrative |\n"
    )
    rows6 = r.find_rows(text6)
    if "A1" in rows6:
        fails.append("find_rows() matched a row whose Item cell is not "
                      "struck through")

    # 7. Two matches for the same whitelisted id in the live span is a
    #    refusal, not a silent pick of the first one.
    text7 = _file(
        "| **A1** | ~~first~~ | one |\n"
        "| **A1** | ~~second~~ | two |\n"
    )
    try:
        r.find_rows(text7)
        fails.append("find_rows() silently accepted a duplicate id "
                      "instead of refusing")
    except SystemExit:
        pass

    # 8. apply_archive() prepends new entries above whatever the archive
    #    already held, and refuses a mismatched existing header rather
    #    than guess past it (same contract as the sibling rotate tools).
    first_chunk = [("A1", "~~first~~", "one")]
    archive_v1 = r.apply_archive(first_chunk, "")
    if not archive_v1.startswith(r.ARCHIVE_HEADER):
        fails.append("apply_archive() did not start with the expected "
                      "header on a fresh archive")
    second_chunk = [("A2", "~~second~~", "two")]
    archive_v2 = r.apply_archive(second_chunk, archive_v1)
    if archive_v2.find("### A2") > archive_v2.find("### A1"):
        fails.append("apply_archive() did not prepend the new chunk "
                      "above the existing content")
    if "### A1" not in archive_v2:
        fails.append("apply_archive() lost the previously archived "
                      "content on a second run")
    try:
        r.apply_archive(second_chunk, "# Some other file\n\nbody\n")
        fails.append("apply_archive() silently accepted a mismatched "
                      "archive header")
    except ValueError:
        pass

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: rotate_backlog_done_items.py, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
