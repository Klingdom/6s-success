#!/usr/bin/env python3
"""Move two more of OWNER-ACTIONS.md's own stale narrative chains into
OWNER-ACTIONS-ARCHIVE.md: the "Start here" table's one-time 2026-09-18
end-to-end check list, and item -1's full incident investigation.

Found 2026-11-03, scheduled operator cycle, picking up the handoff three
PM check-ins the same day correctly deferred ("item 1's OAuth steps, item
1b's Gemini cost table, item 4's Amazon policy table... need a careful
hand-read, not a quick cut"). Reading those three sections directly found
each one's remaining length is live, cited-elsewhere narrative (cost
tables, policy checklists, a correction the item's own text says is
"worth keeping, because it is why the item changed"), not safely
archivable without a much larger rewrite. Two smaller spans nearby were
genuinely dead and self-contained, so this rotation does those instead
of re-deferring a fourth time:

  1. SPAN_CHECKLIST: the "**Every item here was checked end to end on
     2026-09-18, not just listed.**" paragraph and its six-item bullet
     list, sitting after the "Start here" table. It is a one-time audit
     log of six items as they stood six weeks ago; every live fact in it
     (99 videos re-rendered, two ports rewired, etc.) already has its own
     current-state sentence in that item's own numbered section further
     down the file. Confirmed unreferenced: no gate or script in ops/*.py
     or any other *.md parses this text by name.

  2. SPAN_ITEM_NEG1: the "-1" row's own "Why it is first" cell, a 2,695-
     byte blow-by-blow of a USAGE_LIMIT_REACHED stall (2026-10-04 to
     2026-10-09) and the failed attempts since to self-serve a fix.
     Verified directly before archiving, not assumed: `list_triggers`
     (Claude_Code_Remote MCP) shows all three Routines (:10 PM, :40 PM,
     :43 operator) with last_run.status SUCCEEDED or PENDING, nothing
     FAILED, since the 2026-10-09 recovery this paragraph itself already
     recorded, so "has not recurred" is still true 25 days later, not
     carried forward unchecked. The row's "Do" and "Time" columns are
     untouched (ops/preflight.py's gate_send_questions_covers_top_owner_
     actions and ops/dashboard.py's top_owner_actions() both match on
     those, never on the Why text), and the optional two-minute paste
     ask, with both Routine edit links, stays live in the replacement.

Usage:
    python ops/rotate_owner_actions_item_history.py --check
    python ops/rotate_owner_actions_item_history.py --apply
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

CHECKLIST_START_AFTER = "four things from it, do these."
CHECKLIST_END_BEFORE = "### ~~1f. The VPS disk"

CHECKLIST_REPLACEMENT = (
    "**Every item on this page was checked end to end on 2026-09-18, not "
    "just listed; full account archived to `OWNER-ACTIONS-ARCHIVE.md`.** "
    "One real trap and one real blocker were found that day (item 1's "
    "YouTube videos, item 8's two ports); both are fixed, and each item's "
    "own numbered section below carries the current state.")

NEG1_ROW_START_AFTER = (
    "| **-1** | Check your Claude Code usage limit or plan status | "
    "2 min | ")
NEG1_ROW_END_BEFORE = "| **0** | ~~Add"


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


NEG1_REPLACEMENT = (
    "**Resolved as a live incident 2026-10-09; unrecurred since, "
    "re-checked directly 2026-11-03 (`list_triggers`: all three "
    "Routines' last_run is SUCCEEDED or PENDING, none FAILED).** The "
    "autonomous PM and operator Routines went dark 2026-10-04 to "
    "2026-10-09 on `USAGE_LIMIT_REACHED`; full investigation archived to "
    "`OWNER-ACTIONS-ARCHIVE.md`, account also in `STATUS.md` "
    "INCIDENT-002 and GitHub issue #40. `update_trigger` still "
    "refuses a sandboxed session's self-edit on either PM Routine "
    "(\"created via http_api, not by an agent\"), so one optional ask "
    "stays open: paste a `list_triggers` sibling-health check into "
    "each PM Routine's edit page as a new STEP 0b, right after STEP 0 "
    "(https://claude.ai/code/routines/trig_01KYMpAJo7UHBMtUYmqXj25L "
    "for :10, "
    "https://claude.ai/code/routines/trig_01JCURkStiuxTMyZDNbVGumL "
    "for :40; paste text archived alongside the rest). Issue #40 "
    "stays open either way until you decide. |\n")


def neg1_replacement(today: str = None) -> str:
    return NEG1_REPLACEMENT


def plan_rotation(text: str, today: str = None):
    """Pure function. Returns (new_text, archived_blocks)."""
    today = today or datetime.date.today().isoformat()
    archived_blocks = []

    before1, region1, after1 = region_between(
        text, CHECKLIST_START_AFTER, CHECKLIST_END_BEFORE)
    if region1.strip() != CHECKLIST_REPLACEMENT.strip():
        archived_blocks.append(("Start here table, 2026-09-18 end-to-end "
                                 "check list", region1.strip()))
        text = before1 + "\n\n" + CHECKLIST_REPLACEMENT + "\n\n\n" + after1

    before2, region2, after2 = region_between(
        text, NEG1_ROW_START_AFTER, NEG1_ROW_END_BEFORE)
    replacement2 = neg1_replacement(today)
    if region2 != replacement2:
        archived_blocks.append(("Item -1, usage-limit stall investigation",
                                 region2.strip()))
        text = before2 + replacement2 + after2

    return text, archived_blocks


def format_archive_blocks(archived_blocks, today: str) -> str:
    parts = []
    for label, content in archived_blocks:
        parts.append("### %s, archived %s\n\n%s" % (label, today, content))
    return "\n\n".join(parts)


def apply_archive(archived_region: str, existing_archive_text) -> str:
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
              "ops/rotate_owner_actions_item_history.py. Nothing here "
              "was edited on the way over; CLAUDE.md section 54 says the "
              "record must survive.\n\n---\n")
    return header + "\n" + block + "\n"


def region_sizes(text: str):
    """Bytes of live content still sitting in each span, for the
    preflight gate. Raises ValueError if an anchor is missing.
    """
    _, region1, _ = region_between(text, CHECKLIST_START_AFTER,
                                    CHECKLIST_END_BEFORE)
    _, region2, _ = region_between(text, NEG1_ROW_START_AFTER,
                                    NEG1_ROW_END_BEFORE)
    return (len(region1.strip().encode("utf-8")),
            len(region2.strip().encode("utf-8")))


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
        print("CLEAN: the checklist and item -1 history are already "
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
