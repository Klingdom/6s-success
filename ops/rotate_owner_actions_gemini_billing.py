#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's item 1b ("Turn on Gemini API billing") own
accumulated correction-on-correction history into OWNER-ACTIONS-ARCHIVE.md,
leaving the current, independently-verified state live.

Found 2026-10-25, scheduled operator cycle: gate_living_docs_total_size_
tripwire warns OWNER-ACTIONS.md is 131688 bytes against its 110000-byte
ceiling. ops/rotate_owner_actions.py and ops/rotate_owner_actions_closed_
items.py both report CLEAN against this file, because neither touches item
1b: the first tool's own docstring names this exact item as "correctly
left alone... splitting that safely is a different, larger job, left for a
future cycle exactly as this one was." This is that cycle.

Item 1b grew between 2026-09-04 and 2026-09-30 as a string of bold-prefixed
"Corrected"/"Correction to the correction"/"Superseded" paragraphs, each
narrating a changing count of broken card-hero and zone-hero images (12,
then 7 card heroes; 30, 8, 4, 7, then 3 zone heroes) as different review
tools and local retries ran. None of that counting history is newest-first
or even reliably date-ordered (one paragraph dated 2026-09-11 sits before
one dated "later on 9 September", i.e. 2026-09-09), the same non-ordering
ops/rotate_owner_actions.py's own REPLACEMENT constant already found in a
different span of this file. Checked against the live verdict files rather
than trusted: ops/card-hero-verdicts.json holds exactly the 7 card-hero
stems the item's own newest paragraph (2026-09-18) already names (EE-002,
EM-009, ES-007, ET-003, EU-002, EU-004, EU-009), and ops/hero-verdicts.json
holds exactly the 3 zone slugs the item's own "Current reading" sentence
already names. Both numbers are current and correct; the ~130 lines of
narration explaining how the count got there from 12/30 are not load-
bearing for anyone deciding what to do today.

Three spans are archived, each a self-contained paragraph run between two
fixed anchors (same technique as ops/rotate_owner_actions.py's REGION_
START_AFTER/REGION_END_BEFORE, just three pairs instead of one):

  1. SPAN_1: everything between the foundational billing-gate paragraph
     ("...and every picture on the roadmap.") and the paragraph that
     states the settled, current reading ("Corrected 2026-09-30, this
     operator: both \"eight\" and \"nothing..."). This is the bulk of the
     chain: the 12-card/30-zone/8-zone/4-zone narrative, one dead end at a
     time. Replaced with one pointer naming the settled state.
  2. SPAN_2: a single paragraph ("Corrected 2026-09-07, this operator,
     checked against...") that only restates a zone-hero count already
     superseded twice more since. Replaced with nothing; SPAN_1's pointer
     already covers it.
  3. SPAN_3: a single paragraph ("What is blocked behind it right now:
     card art for all 89 Entryway cards (that folder is empty...)") that
     is simply wrong today: ops/card-hero-verdicts.json shows 81 of 88
     card heroes already generated and live, not an empty folder. Found
     by checking the claim against the verdict file directly, not by
     trusting the correction chain's own later word for it. Replaced with
     nothing.

Deliberately NOT touched: the "Current reading" sentence itself
(gate_owner_actions_zone_art_citation_current parses it by name), the cost
table, "Your part"/"Already built and waiting", the 11-room-page list, and
the dangling-card-back-pixels note (a distinct, still-open problem this
rotation does not claim to have re-verified).

One mechanical, non-archival fix rides along in the same --apply, because
it is a direct consequence of SPAN_1's own settled numbers: the seven-row
"what the image must show" zone table still lists four zones already fixed
on 2026-09-17 (family room, mudroom, nursery, primary bathroom), confirmed
resolved against ops/hero-verdicts.json ("ok", not "no"). Those four rows
move to the archive alongside SPAN_1 (nothing deleted, CLAUDE.md 54), and
the table's own "Those seven pages are text only today" sentence becomes
"Those three pages", matching the three rows left (home office file
storage, home office printer station, workshop material rack) and the
"Current reading" sentence's own count. This one fix is not separately
gated: a future change to which zones are rejected would need a new
citation gate, the same way gate_owner_actions_zone_art_citation_current
already gates the "Current reading" sentence, left for a future cycle if
this table drifts again.

Usage:
    python ops/rotate_owner_actions_gemini_billing.py --check
    python ops/rotate_owner_actions_gemini_billing.py --apply
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

SPAN_1_START_AFTER = "and every picture on the roadmap."
SPAN_1_END_BEFORE = (
    "**Corrected 2026-09-30, this operator: both \"eight\" and \"nothing "
    "to look")

SPAN_2_START_AFTER = "photograph, not another retry."
SPAN_2_END_BEFORE = (
    "**Your part:** open <https://aistudio.google.com/api-keys>, select "
    "the project")

SPAN_3_START_AFTER = (
    "deck ends up looking like two decks, which has already happened "
    "once here.")
SPAN_3_END_BEFORE = "| Zone | Page | What the image must show |"

REPLACEMENT_1 = (
    "**Card-hero and zone-hero count history, 2026-09-04 through "
    "2026-09-11, archived 2026-10-25 by "
    "`ops/rotate_owner_actions_gemini_billing.py`.** The count moved "
    "12 then 7 card heroes, and 30 then 8 then 4 then 7 then 3 zone "
    "heroes, as different review passes and local retries ran; none of "
    "that is load-bearing today. Settled state, checked against the live "
    "verdict files rather than this paragraph's own prior word: card "
    "heroes and zone heroes are both free, local-model retries blocked "
    "on model capability, not this billing gate. Only the 11 room "
    "chapters below genuinely need Gemini billing.")

# Four table rows already resolved 2026-09-17 (ops/hero-verdicts.json
# verdict "ok", not "no"), moved to the archive alongside SPAN_1 rather
# than deleted outright.
RESOLVED_ZONE_ROWS = [
    "| Family Room, Board Game and Puzzle Zone | "
    "`/zones/family-room-the-board-game-and-puzzle-zone` | six board "
    "game boxes stacked flat on a wooden shelf. The rejected render is "
    "a bookshop wall of paperbacks, no game boxes at all |\n",
    "| Mudroom, Family Hook Zone | `/zones/mudroom-the-family-hook-zone` "
    "| two coats and one bag hung on a labelled wall hook column, "
    "mounted low, bare floor beneath |\n",
    "| Nursery, Crib and Sleep Zone | "
    "`/zones/nursery-the-crib-and-sleep-zone` | a crib with a bare "
    "white fitted sheet only, no blankets or toys, monitor cable "
    "clipped high on the wall |\n",
    "| Primary Bathroom, Under Sink Cabinet | "
    "`/zones/primary-bathroom-the-under-sink-cabinet` | an open "
    "cabinet under a sink with two plastic bins and a pipe |\n",
]

SEVEN_PAGES_OLD = "Those seven pages are text only today"
SEVEN_PAGES_NEW = "Those three pages are text only today"

# A WARNING-not-FAIL buffer, same reasoning as every sibling gate: this
# comfortably fits REPLACEMENT_1 itself (currently ~650 bytes) plus normal
# whitespace drift from a future handoff note.
SIZE_BUFFER_BYTES = 400


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


def _resolved_rows_present(text: str):
    return [row for row in RESOLVED_ZONE_ROWS if row in text]


def plan_rotation(text: str):
    """Pure function. Returns (new_text, archived_blocks) where
    archived_blocks is a list of (label, content) pairs for whatever
    still needs moving. An empty list means nothing left to rotate.
    """
    archived_blocks = []

    before1, region1, after1 = region_between(
        text, SPAN_1_START_AFTER, SPAN_1_END_BEFORE)
    if region1.strip() != REPLACEMENT_1.strip():
        archived_blocks.append(("Gemini billing, card/zone hero counts",
                                 region1.strip()))
        text = before1 + "\n\n" + REPLACEMENT_1 + "\n\n" + after1

    before2, region2, after2 = region_between(
        text, SPAN_2_START_AFTER, SPAN_2_END_BEFORE)
    if region2.strip():
        archived_blocks.append(("Gemini billing, zone hero row recount "
                                 "(2026-09-07)", region2.strip()))
        text = before2 + "\n\n" + after2

    before3, region3, after3 = region_between(
        text, SPAN_3_START_AFTER, SPAN_3_END_BEFORE)
    if region3.strip():
        archived_blocks.append(("Gemini billing, stale 'empty folder' "
                                 "claim", region3.strip()))
        text = before3 + "\n\n" + after3

    resolved_rows = _resolved_rows_present(text)
    if resolved_rows:
        archived_blocks.append(("Gemini billing, resolved zone table rows",
                                 "".join(resolved_rows).strip()))
        for row in resolved_rows:
            text = text.replace(row, "")
        text = text.replace(SEVEN_PAGES_OLD, SEVEN_PAGES_NEW)

    return text, archived_blocks


def format_archive_blocks(archived_blocks) -> str:
    today = datetime.date.today().isoformat()
    parts = []
    for label, content in archived_blocks:
        parts.append("### %s, archived %s\n\n%s" % (label, today, content))
    return "\n\n".join(parts)


def apply_archive(archived_region: str, existing_archive_text) -> str:
    """Same prepend-above-existing-content shape as
    ops/rotate_owner_actions.py's apply_archive, so repeated rotations of
    different spans keep extending one growing archive instead of
    reordering it.
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
              "ops/rotate_owner_actions_gemini_billing.py. Nothing here "
              "was edited on the way over; CLAUDE.md section 54 says the "
              "record must survive.\n\n---\n")
    return header + "\n" + block + "\n"


def region_sizes(text: str):
    """Bytes of live content still sitting in each of the three spans,
    for the preflight gate. Raises ValueError if an anchor is missing.
    """
    _, region1, _ = region_between(text, SPAN_1_START_AFTER,
                                    SPAN_1_END_BEFORE)
    _, region2, _ = region_between(text, SPAN_2_START_AFTER,
                                    SPAN_2_END_BEFORE)
    _, region3, _ = region_between(text, SPAN_3_START_AFTER,
                                    SPAN_3_END_BEFORE)
    return (len(region1.strip().encode("utf-8")),
            len(region2.strip().encode("utf-8")),
            len(region3.strip().encode("utf-8")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not (args.check or args.apply):
        print("pass --check or --apply")
        return 2

    text = io.open(OA_PATH, encoding="utf-8").read()
    try:
        new_text, archived_blocks = plan_rotation(text)
    except ValueError as e:
        print("CANNOT ROTATE: %s" % e)
        return 1

    if not archived_blocks:
        print("CLEAN: item 1b's history and resolved zone rows are "
              "already rotated.")
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
    archive_block = format_archive_blocks(archived_blocks)
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
