#!/usr/bin/env python3
"""
Prove ops/rotate_owner_actions.py archives OWNER-ACTIONS.md's historical
preamble span correctly: the span moves verbatim, the live file keeps only
the pointer sentence, repeated runs are a no-op, a missing or duplicated
anchor is refused rather than guessed past, and the archive write appends
above existing content without disturbing it.

Run:  python ops/tests/test_rotate_owner_actions.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_owner_actions as roa                               # noqa: E402

BEFORE = (
    "# Owner actions\n\n"
    "**Last measured:** some traffic sentence, untouched by this script.\n\n"
    "**List reviewed:** some review sentence, also untouched. "
    "it says nothing about traffic."
)
AFTER = "\n\n---\n\n## Resolved today\n\n| # | Action | Outcome |\n"


def _history_text(n):
    entries = []
    for i in range(n):
        entries.append("**Corrected day-%d:** body text for entry %d, "
                        "nothing anyone still needs to read." % (i, i))
    return BEFORE + "\n\n" + "\n\n".join(entries) + AFTER


def main() -> int:
    fails = []

    # 1. region_between() finds exactly the span between the two anchors,
    #    and before/after keep everything outside it untouched.
    text = _history_text(3)
    before, region, after = roa.region_between(
        text, roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
    if "day-0" not in region or "day-2" not in region:
        fails.append("region did not capture all synthetic entries: %r"
                     % region[:120])
    if not before.endswith("it says nothing about traffic."):
        fails.append("before boundary drifted: %r" % before[-50:])
    if not after.startswith("\n\n---\n\n## Resolved today"):
        fails.append("after boundary drifted: %r" % after[:50])

    # 2. A missing start anchor is refused, not guessed past.
    try:
        roa.region_between(
            BEFORE.replace("it says nothing about traffic.",
                            "something else entirely") + AFTER,
            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("missing start anchor was silently accepted")
    except ValueError:
        pass

    # 3. A duplicated start anchor is refused.
    try:
        roa.region_between(text + "\n\nit says nothing about traffic.\n",
                            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("duplicated start anchor was silently accepted")
    except ValueError:
        pass

    # 4. A missing end anchor is refused.
    try:
        roa.region_between(
            text.replace("## Resolved today", "## Something Else"),
            roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
        fails.append("missing end anchor was silently accepted")
    except ValueError:
        pass

    # 5. plan_rotation() replaces the whole span with REPLACEMENT and
    #    returns the original span, stripped, as the archived text; the
    #    rest of the document (before/after) is byte-identical.
    text3 = _history_text(3)
    new_text, archived = roa.plan_rotation(text3)
    if roa.REPLACEMENT not in new_text:
        fails.append("rotated text does not carry the pointer sentence")
    if "day-0" in new_text or "day-1" in new_text or "day-2" in new_text:
        fails.append("rotated text still carries archived content")
    if "day-0" not in archived or "day-2" not in archived:
        fails.append("archived text lost an entry: %r" % archived[:120])
    if not new_text.startswith(BEFORE) or not new_text.endswith(AFTER):
        fails.append("rotation disturbed text outside the span")

    # 6. Already-rotated text is a no-op: plan_rotation() returns the text
    #    unchanged and an empty archived string.
    already = BEFORE + "\n\n" + roa.REPLACEMENT + AFTER
    new_again, archived_again = roa.plan_rotation(already)
    if new_again != already or archived_again:
        fails.append("an already-rotated span was rotated again")

    # 7. region_size() matches the stripped byte length of the region,
    #    and is what --check's DUE/CLEAN decision is based on. Use enough
    #    synthetic entries to clear SIZE_BUFFER_BYTES, so this does not
    #    depend on how long REPLACEMENT happens to be today.
    text_big = _history_text(15)
    size = roa.region_size(text_big)
    _, region_big, _ = roa.region_between(
        text_big, roa.REGION_START_AFTER, roa.REGION_END_BEFORE)
    if size != len(region_big.strip().encode("utf-8")):
        fails.append("region_size() did not match the stripped region "
                     "length")
    if size <= len(roa.REPLACEMENT.encode("utf-8")) + roa.SIZE_BUFFER_BYTES:
        fails.append("synthetic 15-entry history did not register as DUE")

    already_size = roa.region_size(already)
    if already_size > len(roa.REPLACEMENT.encode("utf-8")) + roa.SIZE_BUFFER_BYTES:
        fails.append("already-rotated text registered as DUE")

    # 8. apply_archive() with no existing archive writes the header once
    #    and the new block below it.
    fresh = roa.apply_archive("**Corrected day-0:** first ever entry.",
                               None)
    if not fresh.startswith(roa.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive did not start with the expected header")
    if "first ever entry" not in fresh:
        fails.append("fresh archive lost its only entry")

    # 9. apply_archive() with existing content prepends the new block
    #    right after the header's own divider, leaving existing entries
    #    intact and in place.
    grown = roa.apply_archive("**Corrected day-1:** second batch entry.",
                               fresh)
    if "second batch entry" not in grown or "first ever entry" not in grown:
        fails.append("growing the archive lost an entry")
    if grown.find("second batch entry") > grown.find("first ever entry"):
        fails.append("new archive block was not placed above older content")

    # 10. apply_archive() refuses an existing file with the wrong header
    #     rather than guess where to insert.
    try:
        roa.apply_archive("**Corrected day-2:** entry.",
                           "# Some Other Document\n\n---\nbody\n")
        fails.append("a wrong-header archive file was silently accepted")
    except ValueError:
        pass

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 10/10 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
