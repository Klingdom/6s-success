#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's item 15 ("Create the Etsy shop and publish
three listings") two closed-narrative spans into OWNER-ACTIONS-ARCHIVE.md,
leaving the live ask (three listings, the steps, the open photograph
request) exactly as it stands.

Found 2026-11-13, scheduled PM check-in: gate_living_docs_total_size_
tripwire warned OWNER-ACTIONS.md at 117140 bytes against its 110000-byte
ceiling. Neither gate_owner_actions_history_not_oversized, gate_owner_
actions_closed_items_rotated, gate_owner_actions_gemini_billing_not_
oversized, gate_owner_actions_item_history_not_oversized nor gate_owner_
actions_item_1h_not_oversized touches item 15, because none of the four
rotations that produced them read it. Two spans inside item 15 are the
same already-settled, no-longer-cited-elsewhere narrative shape those
gates were each built for:

1. The withdrawal history (lines then numbered 1114-1129): the 2026-10-31
   correction already fixed the item's own heading and step 5 to say
   "three", so the two withdrawal paragraphs explaining how the count
   went five to four to three are closed history, not a live instruction;
   the full account they point to already lives in `MARKETPLACE-
   LISTINGS.md` section 3.1.
2. The print-defect narrative ("A print defect was found and fixed on
   the way through... Nothing further needed here."): a fix already
   landed and verified in the same commit that wrote the note, nothing
   left to do. The sentence before it ("Ready and checked... far under
   any upload cap.") is live status and stays.

Checked for citations before touching: `grep -rn` across `*.py`, `*.md`
for "it was five, then four", "second withdrawal", "near-empty page" and
"152 pages" finds only this row.

Deliberately NOT touched: the "Tracked... issue #44" line, the "What:"
paragraph, every numbered step, the "Then send me one photograph" ask,
and the "Ready and checked... upload cap" sentence, all still live and
some matched by name elsewhere (`gate_send_questions_covers_top_owner_
actions`, `dashboard.py`'s `top_owner_actions()`).

Usage:
    python ops/rotate_owner_actions_item15_etsy.py --check
    python ops/rotate_owner_actions_item15_etsy.py --apply
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

# Block A: the two withdrawal paragraphs, between the "What:" paragraph
# and the first numbered step.
A_START_AFTER = "their files are built and measured.\n\n"
A_END_BEFORE = "1. Go to `https://www.etsy.com/sell`"
A_REPLACEMENT = (
    "**Two earlier withdrawals brought the count from five to four to "
    "three (L3-entryway, 2026-09-09; L2-kitchen, 2026-09-23, both the "
    "same free-deck-duplication reason); archived %s by `ops/rotate_"
    "owner_actions_item15_etsy.py`. Full account in `MARKETPLACE-"
    "LISTINGS.md` section 3.1.**\n\n")

# Block B: the already-fixed print-defect narrative, between the live
# "Ready and checked" status sentence and the next numbered item header.
B_START_AFTER = "title claims, and is far under any upload cap. "
B_END_BEFORE = "\n\n### 16."
B_REPLACEMENT = (
    "A print-defect fix (a near-empty page between every card sheet, "
    "cutting the Whole House PDF from 152 pages to 76) landed and was "
    "verified in the same commit this note was written in; archived %s "
    "by `ops/rotate_owner_actions_item15_etsy.py`.")

# A WARNING-not-FAIL buffer, same reasoning as every sibling gate: this
# comfortably fits both replacements (currently ~500 bytes combined)
# plus normal whitespace drift from a future handoff note.
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

    before, region, after = region_between(text, A_START_AFTER, A_END_BEFORE)
    if region.strip().startswith("**Corrected 2026-09-09"):
        archived_blocks.append(("Item 15, the five-to-four-to-three "
                                 "withdrawal history", region.strip()))
        text = before + (A_REPLACEMENT % today) + after

    before, region, after = region_between(text, B_START_AFTER, B_END_BEFORE)
    if region.strip().startswith("A print defect was found"):
        archived_blocks.append(("Item 15, the already-fixed print-defect "
                                 "narrative", region.strip()))
        text = before + (B_REPLACEMENT % today) + after

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
              "ops/rotate_owner_actions_item15_etsy.py. Nothing here "
              "was edited on the way over; CLAUDE.md section 54 says the "
              "record must survive.\n\n---\n")
    return header + "\n" + block + "\n"


def region_sizes(text: str):
    """Bytes of live content still sitting in each span, for the
    preflight gate. Raises ValueError if an anchor is missing.
    """
    _, region_a, _ = region_between(text, A_START_AFTER, A_END_BEFORE)
    _, region_b, _ = region_between(text, B_START_AFTER, B_END_BEFORE)
    return (len(region_a.strip().encode("utf-8")),
            len(region_b.strip().encode("utf-8")))


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
        print("CLEAN: item 15's closed narratives are already rotated.")
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
