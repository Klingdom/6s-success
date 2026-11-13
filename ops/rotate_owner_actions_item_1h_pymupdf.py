#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's item 1h ("Add one line to the cloud
environment's setup script") first two occurrence narratives into
OWNER-ACTIONS-ARCHIVE.md, leaving the third, current occurrence live.

Found 2026-11-13, scheduled operator cycle: gate_living_docs_total_size_
tripwire warned OWNER-ACTIONS.md at 119326 bytes against its 110000-byte
ceiling. The 2026-11-03 rotation (ops/rotate_owner_actions_item_history.py)
checked items 1, 1b and 4 directly and found each still live and cited
elsewhere, not safely archivable; item 1h was not yet oversized that day,
because its third occurrence paragraph (2026-11-09) had not been written
yet. It has grown the exact same "found again, found worse, found a third
time" chain those three items were deliberately NOT given this treatment
for avoiding, except item 1h's chain genuinely is self-contained: each of
its three occurrence paragraphs restates the same root cause (`pymupdf`
missing on a cold container) and the same fix (one line in the cloud
environment's setup script, or an approved `create_environment` call), and
the third paragraph alone already carries the current, settled account,
including the one thing that changed since the first two (a ready, tested
setup script and a concrete two-way close). Nothing in the first two
paragraphs is cited by name anywhere else in this repository (checked:
`grep -rn` across `*.py`, `*.md` for their distinguishing phrases finds
only this row).

Deliberately NOT touched: the third occurrence paragraph itself (the live,
current ask), the row's "Do"/"Time" columns (matched by name elsewhere:
`gate_send_questions_covers_top_owner_actions`, `dashboard.py`'s
`top_owner_actions()`).

Usage:
    python ops/rotate_owner_actions_item_1h_pymupdf.py --check
    python ops/rotate_owner_actions_item_1h_pymupdf.py --apply
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

SPAN_START_AFTER = "cloud environment's setup script | 2 min | "
SPAN_END_BEFORE = (
    "**Third occurrence, 2026-11-09, scheduled operator cycle, and this "
    "time an actual fix was attempted rather than only logged a third "
    "time.**")

REPLACEMENT = (
    "**First two occurrences of this cold-container `pymupdf` gap "
    "(2026-10-15, 2026-10-20), archived %s by "
    "`ops/rotate_owner_actions_item_1h_pymupdf.py`: same root cause and "
    "the same fix as the occurrence below, which is current and still "
    "open.** ")

# A WARNING-not-FAIL buffer, same reasoning as every sibling gate: this
# comfortably fits REPLACEMENT itself (currently ~300 bytes) plus normal
# whitespace drift from a future handoff note.
SIZE_BUFFER_BYTES = 200


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


def replacement_text(today: str = None) -> str:
    today = today or datetime.date.today().isoformat()
    return REPLACEMENT % today


def plan_rotation(text: str, today: str = None):
    """Pure function. Returns (new_text, archived_blocks)."""
    before, region, after = region_between(
        text, SPAN_START_AFTER, SPAN_END_BEFORE)
    archived_blocks = []
    # A span already rotated starts with "**First two occurrences" rather
    # than "**Found 2026-10-15"; compare on that rather than an exact
    # string match so a re-run with a different "today" stays CLEAN.
    if region.strip().startswith("**Found 2026-10-15"):
        archived_blocks.append(("Item 1h, first two pymupdf occurrences "
                                 "(2026-10-15, 2026-10-20)", region.strip()))
        text = before + replacement_text(today) + after
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
              "ops/rotate_owner_actions_item_1h_pymupdf.py. Nothing here "
              "was edited on the way over; CLAUDE.md section 54 says the "
              "record must survive.\n\n---\n")
    return header + "\n" + block + "\n"


def region_size(text: str) -> int:
    """Bytes of live content still sitting in the span, for the preflight
    gate. Raises ValueError if an anchor is missing.
    """
    _, region, _ = region_between(text, SPAN_START_AFTER, SPAN_END_BEFORE)
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
        print("CLEAN: item 1h's first two occurrences are already "
              "rotated.")
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
