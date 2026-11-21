#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's item 23 ("Reduce the autonomous cadence...")
opening narrative paragraph into OWNER-ACTIONS-ARCHIVE.md, leaving the
live ask (the two numbered options, the "I cannot change this myself"
constraint, and the Addendum's Routine edit links) exactly as it stands.

Found 2026-11-21, scheduled operator cycle, cold-reading OWNER-ACTIONS.md
for the next prunable chunk a PM check-in handed off minutes earlier
(109,980 of its 110,000-byte tripwire, all seven existing rotate_owner_
actions*.py scripts CLEAN). Item 23's opening paragraph is a point-in-time
snapshot from 2026-10-17 ("Raised twice already... 206 commits in the 28
hours before this cycle started... All ten open GitHub issues..."). That
count is now stale on its face (30 open issues today, not ten) and the
question it describes has been kept current ever since in GitHub issue
#42's own comment thread instead: at least ten follow-up comments through
2026-11-20, each independently re-measuring the same cadence cost with
fresh numbers. A static copy of October's snapshot sitting ahead of a
live, continuously-updated issue thread is the same "source corrected,
artifact never re-derived" shape this file already treats as a defect
elsewhere (see the item 1/15/1h/gemini-billing rotations above), not new
content worth keeping twice.

Checked for citations before touching: grep across *.py/*.md for "206
commits in the 28 hours" and "All ten open GitHub issues are labelled"
finds only this one paragraph; nothing else in the repository depends on
its exact wording.

Deliberately NOT touched: the header line, "I cannot change this myself"
and its one-sentence reason, the two numbered options (still the live
ask), "Nothing else here is blocked on this", and the whole Addendum
paragraph including its three Routine edit links, which are the actual
one-click targets if Phil picks option 1.

Usage:
    python ops/rotate_owner_actions_item23_cadence.py --check
    python ops/rotate_owner_actions_item23_cadence.py --apply
"""
import argparse
import datetime
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OA_PATH = os.path.join(ROOT, "OWNER-ACTIONS.md")
ARCHIVE_PATH = os.path.join(ROOT, "OWNER-ACTIONS-ARCHIVE.md")

ARCHIVE_HEADER_FIRST_LINE = "# OWNER-ACTIONS.md archive"

# The span between item 23's header and the live "I cannot change this
# myself" sentence: the whole 2026-10-17 point-in-time narrative.
START_AFTER = (
    "### 23. Reduce the autonomous cadence, or clear a decision, so it "
    "stops burning usage on an unchanged state. About two minutes.\n\n")
END_BEFORE = "\n\n**I cannot change this myself.**"
REPLACEMENT = (
    "**Raised in issue #42 (and originally #40); not yet acted on.** "
    "This paragraph used to carry a 2026-10-17 snapshot (ten open issues, "
    "206 commits in 28 hours); that count is stale on its face today "
    "(30 open issues, not ten) and the live, continuously-updated account "
    "lives in GitHub issue #42's own comment thread instead, kept current "
    "every cycle since. Archived %s by `ops/rotate_owner_actions_"
    "item23_cadence.py`.")

# A WARNING-not-FAIL buffer, same reasoning as every sibling gate.
SIZE_BUFFER_BYTES = 300


def region_between(text: str, start_after: str, end_before: str):
    """Return (before, region, after). Raises ValueError if either anchor
    is missing, duplicated, or end_before does not follow start_after.
    """
    if text.count(start_after) != 1:
        raise ValueError("start anchor missing or duplicated: %r"
                          % start_after)
    if text.count(end_before) != 1:
        raise ValueError("end anchor missing or duplicated: %r" % end_before)
    start = text.find(start_after) + len(start_after)
    end = text.find(end_before, start)
    if end == -1:
        raise ValueError("end anchor does not follow start anchor")
    return text[:start], text[start:end], text[end:]


def plan_rotation(text: str, today: str = None):
    """Pure function. Returns (new_text, archived_blocks)."""
    today = today or datetime.date.today().isoformat()
    archived_blocks = []

    before, region, after = region_between(text, START_AFTER, END_BEFORE)
    if region.strip().startswith("**Raised twice already"):
        archived_blocks.append(("Item 23, the 2026-10-17 cadence-cost "
                                 "narrative", region.strip()))
        text = before + (REPLACEMENT % today) + after

    return text, archived_blocks


def format_archive_blocks(archived_blocks, today: str) -> str:
    parts = []
    for label, content in archived_blocks:
        parts.append("### %s, archived %s\n\n%s" % (label, today, content))
    return "\n\n".join(parts)


def apply_archive(archived_region: str, existing_archive_text) -> str:
    """Same prepend-above-existing-content shape as the sibling rotation
    scripts, so repeated rotations of different spans keep extending one
    growing archive instead of reordering it.
    """
    block = archived_region.strip() + "\n"
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER_FIRST_LINE):
            raise ValueError("OWNER-ACTIONS-ARCHIVE.md does not start with "
                              "the expected header; refusing to guess.")
        marker = "\n---\n"
        at = existing_archive_text.find(marker)
        if at == -1:
            raise ValueError("OWNER-ACTIONS-ARCHIVE.md has no '---' "
                              "divider after its header; refusing to guess.")
        head = existing_archive_text[:at + len(marker)]
        tail = existing_archive_text[at + len(marker):]
        return head + "\n" + block + "\n" + tail.lstrip("\n")
    header = (ARCHIVE_HEADER_FIRST_LINE + "\n\n"
              "> Historical entries moved here by "
              "ops/rotate_owner_actions_item23_cadence.py. Nothing here "
              "was edited on the way over; CLAUDE.md section 54 says the "
              "record must survive.\n\n---\n")
    return header + "\n" + block + "\n"


def region_size(text: str):
    """Bytes of live content still sitting in the span, for the
    preflight gate. Raises ValueError if an anchor is missing.
    """
    _, region, _ = region_between(text, START_AFTER, END_BEFORE)
    return len(region.strip().encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not (args.check or args.apply):
        print("pass --check or --apply")
        return 2

    text = io.open(OA_PATH, encoding="utf-8").read()
    today = datetime.date.today().isoformat()
    try:
        new_text, archived_blocks = plan_rotation(text, today)
    except ValueError as e:
        print("CANNOT ROTATE: %s" % e)
        return 1

    if not archived_blocks:
        print("CLEAN: item 23's closed narrative is already rotated.")
        return 0

    total = sum(len(c.encode("utf-8")) for _, c in archived_blocks)
    print("%d archivable block(s), %d bytes total:" %
          (len(archived_blocks), total))
    for label, content in archived_blocks:
        print("  - %s (%d bytes)" % (label, len(content.encode("utf-8"))))

    if args.check:
        return 1

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    archive_block = format_archive_blocks(archived_blocks, today)
    new_archive_text = apply_archive(archive_block, existing_archive_text)

    oa_tmp = OA_PATH + ".tmp"
    io.open(oa_tmp, "w", encoding="utf-8").write(new_text)
    os.replace(oa_tmp, OA_PATH)

    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    print("APPLIED: %d bytes archived to %s" % (total, ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
