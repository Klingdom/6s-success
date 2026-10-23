#!/usr/bin/env python3
"""Move OWNER-ACTIONS.md's own superseded preamble history into
OWNER-ACTIONS-ARCHIVE.md, leaving one pointer sentence live.

Found 2026-10-23, scheduled operator cycle, the designated next cold-read
left by that day's section 30 fix (ops/rotate_checkin_log.py): the file
Phil reads directly to decide what needs him had the identical unbounded-
growth shape STATUS.md's "Production Knowledge" and "Immediate Focus"
fields had before ops/rotate_status_history.py rotated them. Between the
"List reviewed:" header and the "## Resolved today" table sat two distinct
chains, neither a standing owner action any more:

1. A deploy-gap narrative (2026-09-24/25): a sequence of bold-prefixed
   "Corrected"/"Widened"/"Reopened"/"RESOLVED"/"Added" paragraphs, each
   about a build-id/commit-count snapshot that is now tracked live by
   ops/deploy-verdict.json and STATUS.md's BLOCKER-001, not by this text.
   Unlike STATUS.md's own chain, this one is not reliably newest-first (a
   2026-09-24 entry follows a 2026-09-25 one), so "keep the newest, archive
   the rest" would risk keeping a stale paragraph live. Every entry in it
   is superseded regardless of position: the one fact worth keeping
   ("deploying is not Phil's job any more, item 0 below is") is already
   stated in the "Start here" table further down the file.
2. A one-sentence-per-item changelog ("Earlier: <date>, item N ...") going
   back to 2026-09-04, entirely narrating how individual numbered items
   changed over time. Every item it touches has its own live row in "Open,
   ranked by what they unblock" or the "Resolved today" table; this text
   adds nothing a cycle needs to read to decide what Phil should do today.

Both chains sit in the same bounded span (everything between the fixed
phrase that ends the "List reviewed" paragraph and the fixed "## Resolved
today" heading), so one rotation handles both at once: archive the whole
span verbatim, replace it with a short pointer. Nothing is deleted
(CLAUDE.md section 54); OWNER-ACTIONS-ARCHIVE.md keeps the full text.

Deliberately NOT touched: the "Last measured:" and "List reviewed:"
paragraphs above this span. Both are parsed by name for their first
sentence (ops/preflight.py's gate_goals_sessions_citations_current,
ops/dashboard.py's _owner_actions_traffic_citation), so rewriting them is a
different, higher-risk job than archiving an already-dead narrative, and is
left for a future cycle exactly as this file's own 2026-10-23 backlog entry
(section 30) deferred the "Resolved today"-style preamble work rather than
guess at it.

Usage:
    python ops/rotate_owner_actions.py --check   report only, exit 1 if due
    python ops/rotate_owner_actions.py --apply   rotate now
"""
import argparse
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OA_PATH = os.path.join(ROOT, "OWNER-ACTIONS.md")
ARCHIVE_PATH = os.path.join(ROOT, "OWNER-ACTIONS-ARCHIVE.md")

# The historical span sits strictly between these two anchors. Neither
# names a date, so both stay valid after rotation and keep working as the
# ongoing gate's bounds, unlike a marker tied to the specific chain found
# today. "it says nothing about traffic." is the last sentence of the
# untouched "List reviewed:" paragraph; "## Resolved today" is the next
# heading in the file. Both are currently unique; a script that cannot
# find exactly one of each refuses rather than guesses which text to move.
REGION_START_AFTER = "it says nothing about traffic."
REGION_END_BEFORE = "\n\n---\n\n## Resolved today"

ARCHIVE_HEADER_FIRST_LINE = "# OWNER-ACTIONS.md archive"

REPLACEMENT = (
    "**Deploy-gap and per-item history, 2026-09-04 through 2026-09-25, "
    "archived 2026-10-23 by `ops/rotate_owner_actions.py`:** none of it is "
    "a standing owner action any more. Current deploy status lives in "
    "`STATUS.md`'s `BLOCKER-001`; the one still-open ask this chain ever "
    "raised is item 0 below (`VPS_DEPLOY_KEY`). Moved verbatim to "
    "`OWNER-ACTIONS-ARCHIVE.md`."
)

# A WARNING-not-FAIL buffer, same reasoning as gate_status_immediate_focus_
# not_oversized: a long region wastes a future cycle's reading time, it
# does not ship anything broken to a customer. 400 bytes comfortably fits
# REPLACEMENT itself (currently ~370 bytes) plus normal whitespace drift.
SIZE_BUFFER_BYTES = 400


def region_between(text: str, start_after: str, end_before: str):
    """Return (before, region, after) where region is everything strictly
    between the end of start_after and the start of end_before. Raises
    ValueError if either anchor is missing, duplicated, or end_before does
    not follow start_after -- refuse to guess rather than move the wrong
    text.
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


def region_size(text: str) -> int:
    """Pure function used by the preflight gate: bytes of live history
    still sitting in the bounded span, stripped of surrounding whitespace.
    Raises ValueError if the anchors cannot be found (same refusal as
    region_between).
    """
    _, region, _ = region_between(text, REGION_START_AFTER, REGION_END_BEFORE)
    return len(region.strip().encode("utf-8"))


def plan_rotation(text: str):
    """Pure function. Returns (new_text, archived_region). archived_region
    is "" if the span already equals REPLACEMENT (nothing to move).
    """
    before, region, after = region_between(
        text, REGION_START_AFTER, REGION_END_BEFORE)
    if region.strip() == REPLACEMENT.strip():
        return text, ""
    new_text = before + "\n\n" + REPLACEMENT + after
    return new_text, region.strip()


def apply_archive(archived_region: str, existing_archive_text) -> str:
    """Same prepend-above-existing-content shape as
    ops/rotate_status_history.py's apply_archive, so repeated runs keep
    extending one growing archive instead of reordering it.
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
              "ops/rotate_owner_actions.py. Nothing here was edited on "
              "the way over; CLAUDE.md section 54 says the record must "
              "survive.\n\n---\n")
    return header + "\n" + block + "\n"


def _write_rotated(new_text: str, archived_region: str) -> None:
    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived_region, existing_archive_text)

    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    oa_tmp = OA_PATH + ".tmp"
    io.open(oa_tmp, "w", encoding="utf-8").write(new_text)
    os.replace(oa_tmp, OA_PATH)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="report whether rotation is due; makes no "
                          "changes.")
    ap.add_argument("--apply", action="store_true",
                     help="rotate now: archive the historical span, leave "
                          "the pointer sentence live.")
    args = ap.parse_args()
    if sum([args.check, args.apply]) != 1:
        ap.error("pass exactly one of --check, --apply")

    text = io.open(OA_PATH, encoding="utf-8").read()
    try:
        size = region_size(text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2

    replacement_size = len(REPLACEMENT.encode("utf-8"))
    due = size > replacement_size + SIZE_BUFFER_BYTES

    if args.check:
        if due:
            print("DUE: %d bytes of preamble history live (pointer alone "
                  "is %d); would move to %s on --apply."
                  % (size, replacement_size, ARCHIVE_PATH))
            return 1
        print("CLEAN: %d bytes live, at or near the pointer sentence's own "
              "size. Nothing to rotate." % size)
        return 0

    # --apply
    new_text, archived_region = plan_rotation(text)
    if not archived_region:
        print("Already rotated; no change made.")
        return 0
    _write_rotated(new_text, archived_region)
    print("Moved %d bytes of preamble history to %s."
          % (len(archived_region.encode("utf-8")), ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
