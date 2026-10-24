#!/usr/bin/env python3
"""Move STATUS.md section 14's closed Workstream 3 build-log narrative
into STATUS-ARCHIVE.md, keeping only the closure summary live.

Found 2026-10-24: `gate_living_docs_total_size_tripwire` fired on
STATUS.md (196738 of a 110000-byte ceiling), and the 09:4x PM check-in
named section 14 ("Active Major Workstreams") as the one named-but-unread
candidate three prior cycles had deferred without a closer read. Reading
it: Workstreams 1 and 2 are still BLOCKED and their short descriptions
are the live, current state. Workstream 3 was CLOSED 2026-10-03, and its
own closure paragraph already says so in one place, but underneath that
paragraph sit roughly 18 more dated "Done"/"Found"/"Corrected" entries
(2026-09-07 through 2026-09-25) documenting HOW it closed, M1 through
B9, each one a real build-log entry from a workstream that has been shut
for three weeks. Every later cycle's STEP 1 still reads all of it.

This is one candidate, not the whole fix: this narrative is ~13.5KB of
the file's ~87KB overage, so this script alone does not bring STATUS.md
back under the tripwire. It is still worth doing on its own terms (the
same "rotate the first closed thing you actually read" precedent as
every sibling rotate_*.py), and it narrows what the next cold-read of
this file needs to cover.

Nothing is deleted. The narrative moves verbatim into STATUS-ARCHIVE.md,
under its own dated heading, same "new material on top" convention
ops/rotate_status_history.py and ops/rotate_nightly_log.py already use.

Usage:
    python ops/rotate_status_workstreams.py --check   report only, exit 1 if narrative remains
    python ops/rotate_status_workstreams.py --apply   rotate now
"""
import argparse
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_PATH = os.path.join(ROOT, "STATUS.md")
ARCHIVE_PATH = os.path.join(ROOT, "STATUS-ARCHIVE.md")

# Workstream 3's closure paragraph ends on this sentence (the Objective
# line); everything after it, up to section 15, is the dated build-log
# narrative. Both anchors are plain strings checked for uniqueness before
# this script trusts them, so a future edit that removes or duplicates
# either one makes this script refuse rather than archive the wrong span.
START_AFTER = "and ship the free unillustrated Kitchen deck."
END_BEFORE = "\n\n---\n\n# 15. Current Experiments"

ARCHIVE_HEADER_FIRST_LINE = "# STATUS.md archive"

POINTER = (
    "\n\n**Archived 2026-10-24, scheduled operator, by "
    "`ops/rotate_status_workstreams.py --apply`:** the dated build-log "
    "narrative that used to sit here (2026-09-07 through 2026-09-25, M1 "
    "through B9, the full account of how this workstream reached the "
    "closure above) moved verbatim to `STATUS-ARCHIVE.md`. The closure "
    "summary above is the current, live statement; nothing below it was "
    "left unresolved.\n"
)


def split_workstream3(text: str):
    """Return (before, narrative, after). `narrative` is the dated
    build-log text between the two anchors, stripped of its own leading
    and trailing blank lines. Raises ValueError if either anchor is
    missing or appears more than once (refuse to guess rather than
    archive the wrong span).
    """
    start_idx = text.find(START_AFTER)
    if start_idx == -1:
        raise ValueError("anchor not found: %r" % START_AFTER)
    if text.find(START_AFTER, start_idx + 1) != -1:
        raise ValueError("anchor appears more than once: %r" % START_AFTER)
    span_start = start_idx + len(START_AFTER)

    end_idx = text.find(END_BEFORE, span_start)
    if end_idx == -1:
        raise ValueError("anchor not found: %r" % END_BEFORE)
    if text.find(END_BEFORE, end_idx + 1) != -1:
        raise ValueError("anchor appears more than once: %r" % END_BEFORE)

    before = text[:span_start]
    narrative = text[span_start:end_idx].strip("\n")
    after = text[end_idx:]
    return before, narrative, after


def plan_rotation(text: str):
    """Pure function of its input; does no I/O. Returns (new_status_text,
    archived_narrative_or_none). A narrative that is empty, or is already
    just the pointer this script itself leaves behind, is a no-op: this
    makes --apply idempotent instead of nesting a pointer inside a
    pointer on a second run.
    """
    before, narrative, after = split_workstream3(text)
    if not narrative or narrative.strip("\n") == POINTER.strip("\n"):
        return text, None
    new_text = before + POINTER + after
    return new_text, narrative


def apply_archive(narrative: str, existing_archive_text):
    """Prepend the archived narrative, under its own dated heading, right
    after STATUS-ARCHIVE.md's existing '---' divider, the same "new
    material on top" convention ops/rotate_status_history.py uses.
    Raises ValueError if the existing archive does not match the
    expected header/divider shape (refuse to guess).
    """
    block = ("**Archived 2026-10-24: STATUS.md section 14, Workstream "
              "3's closed build-log narrative (2026-09-07 through "
              "2026-09-25, M1 through B9).**\n\n" + narrative)
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER_FIRST_LINE):
            raise ValueError("STATUS-ARCHIVE.md does not start with the "
                              "expected header; refusing to guess.")
        marker = "\n---\n"
        at = existing_archive_text.find(marker)
        if at == -1:
            raise ValueError("STATUS-ARCHIVE.md has no '---' divider "
                              "after its header; refusing to guess.")
        head = existing_archive_text[:at + len(marker)]
        tail = existing_archive_text[at + len(marker):]
        return head + "\n" + block + "\n\n" + tail.lstrip("\n")
    header = ARCHIVE_HEADER_FIRST_LINE + "\n\n---\n"
    return header + "\n" + block + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="report whether rotation is due; makes no changes")
    ap.add_argument("--apply", action="store_true",
                     help="rotate now, archive the narrative, leave the "
                          "pointer in its place")
    args = ap.parse_args()
    if sum([args.check, args.apply]) != 1:
        ap.error("pass exactly one of --check, --apply")

    status_text = io.open(STATUS_PATH, encoding="utf-8").read()
    try:
        _, narrative, _ = split_workstream3(status_text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2
    already_rotated = narrative.strip("\n") == POINTER.strip("\n")

    if args.check:
        if narrative and not already_rotated:
            print("DUE: %d bytes of closed Workstream 3 narrative would "
                  "move to %s on --apply."
                  % (len(narrative.encode("utf-8")), ARCHIVE_PATH))
            return 1
        print("CLEAN: no narrative left to rotate.")
        return 0

    # --apply
    new_status_text, archived_narrative = plan_rotation(status_text)
    if not archived_narrative:
        print("Already rotated; no change made.")
        return 0

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived_narrative, existing_archive_text)

    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    status_tmp = STATUS_PATH + ".tmp"
    io.open(status_tmp, "w", encoding="utf-8").write(new_status_text)
    os.replace(status_tmp, STATUS_PATH)

    print("Moved %d bytes to %s."
          % (len(archived_narrative.encode("utf-8")), ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
