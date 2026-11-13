#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's item 1 ("Authorise YouTube uploads") two
closed-narrative spans into OWNER-ACTIONS-ARCHIVE.md, leaving the live
ask (the five OAuth steps, the scope reminder, the quota expectation,
the two separate open re-upload asks) exactly as it stands.

Found 2026-11-13, PM check-in: the 04:4x check-in handed off item 1
(10103 bytes, OWNER-ACTIONS.md's largest remaining section) as the next
prunable span once gate_living_docs_total_size_tripwire kept warning
(115974 of 110000 bytes) and all five sibling rotation gates read
clean, because none of them reads item 1. Two spans inside item 1 are
the same already-settled, no-longer-cited-elsewhere narrative shape
those gates were each built for:

1. The "what this looked like yesterday" paragraph pair: the 2026-09-15
   done_items() caption/narration bug and its 2026-09-18 overnight fix
   are closed history, fully covered in STATUS-ARCHIVE.md, LEARNINGS.md
   and ops/NIGHTLY-LOG-ARCHIVE.md; nothing here is a live instruction.
2. The "two things that were missing" setup-fix pair (.gitignore rule,
   missing client libraries): both fixed and verified 2026-09-27,
   cited nowhere else, and not needed to perform the live OAuth steps.

Checked for citations before touching: `grep -rn` across `*.py`, `*.md`
for "What this looked like yesterday", "had nowhere safe to land" and
"client libraries were not installed" finds only this file for the
setup-fix pair, and STATUS-ARCHIVE.md/LEARNINGS.md/NIGHTLY-LOG-ARCHIVE.md
(not this file) already carry the full done_items() account independently.

Deliberately NOT touched: the "Tracked... issue #46" line, the numbered
OAuth steps, "On step 3, add both scopes", the quota-expectation
paragraph, "Already built and waiting", "Why it matters", and both
still-open re-upload asks (stale titles; the 11-of-12 wrong-checklist
videos), all live and some matched by name elsewhere
(`ops/youtube_upload.py`, `confirm_right_channel()`).

Usage:
    python ops/rotate_owner_actions_item1_youtube.py --check
    python ops/rotate_owner_actions_item1_youtube.py --apply
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

# Block A: the "what this looked like yesterday" paragraph pair, between
# the live "Resolved overnight" sentence and the live traffic-snapshot
# pointer that a previous rotation already left in place.
A_START_AFTER = "one of them agrees with the page it links to.**\n\n"
A_END_BEFORE = "\n\n**A 2026-09-29 traffic snapshot"
A_REPLACEMENT = (
    "**The 2026-09-15 done_items() caption/narration bug and its "
    "2026-09-18 overnight fix (100 of 114 videos re-rendered, 0 "
    "failures) are closed history; archived %s by `ops/rotate_"
    "owner_actions_item1_youtube.py`. Full account in `STATUS-ARCHIVE."
    "md`, `LEARNINGS.md` and `ops/NIGHTLY-LOG-ARCHIVE.md`.**")

# Block B: the "two things that were missing" setup-fix pair, between
# the live step-5 instruction and the live scope reminder.
B_START_AFTER = "`ops/youtube-client-secret.json`.\n\n"
B_END_BEFORE = "\n\n**On step 3, add both scopes**"
B_REPLACEMENT = (
    "**Two setup gaps (a missing `.gitignore` rule for the credential "
    "and token files, and two missing client libraries) were found and "
    "fixed 2026-09-27, verified, and cited nowhere else; archived %s by "
    "`ops/rotate_owner_actions_item1_youtube.py`.**")

# A WARNING-not-FAIL buffer, same reasoning as every sibling gate: this
# comfortably fits both replacements (currently under 500 bytes
# combined) plus normal whitespace drift from a future handoff note.
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
    if region.strip().startswith("What this looked like yesterday"):
        archived_blocks.append(("Item 1, the what-this-looked-like-"
                                 "yesterday done_items() bug narrative",
                                 region.strip()))
        text = before + (A_REPLACEMENT % today) + after

    before, region, after = region_between(text, B_START_AFTER, B_END_BEFORE)
    if region.strip().startswith("**Two things that were missing"):
        archived_blocks.append(("Item 1, the two-things-that-were-"
                                 "missing setup-fix narrative",
                                 region.strip()))
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
              "ops/rotate_owner_actions_item1_youtube.py. Nothing here "
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
        print("CLEAN: item 1's closed narratives are already rotated.")
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
