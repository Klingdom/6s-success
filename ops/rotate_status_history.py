#!/usr/bin/env python3
"""Move STATUS.md's superseded "Production Knowledge" history into
STATUS-ARCHIVE.md, keeping only the single newest entry live.

STATUS.md section 24 ("How to Update Status") already states the rule this
script enforces: "move historical detail to the appropriate long-term file.
Do not allow this document to become an archive." Nothing has ever carried
that rule out for this one field. Section 30 ("Current Overall Assessment")
accumulated a chain of bold-prefixed paragraphs ("**Production Knowledge,
...", and under the older convention before that name existed, "**Prior
(...)" and "**Superseded entry, ..."), each one explicitly superseding the
entry right below it ("the gap below has reopened", "same standing limit as
every entry below"). Found 2026-10-23: 27 of these entries had piled up
back to 2026-09-24, 38KB of a 358KB file, read in full by every cycle's
STEP 1 and by every stale-claim gate that scans STATUS.md, for a field whose
own Final Rule says it must describe CURRENT reality, not history. The file
already has exactly this precedent once, by hand: STATUS-ARCHIVE.md's own
header records a 2026-09-17 move of section 1's history for the identical
reason ("does not cost every session 151 KB of superseded cycle notes").
This script makes that a repeatable, provable operation instead of a thing
someone remembers to do by hand, the same move ops/rotate_nightly_log.py
already made for ops/NIGHTLY-LOG.md.

Nothing is deleted. Entries move verbatim, in their existing order, into
STATUS-ARCHIVE.md: CLAUDE.md section 54 ("Failure Is Information") and
STATUS-ARCHIVE.md's own header both say the record must survive.

Only the chain under section 30 is touched. A single, explicitly superseding
chain, where only the newest entry is ever current, is a different shape
from ops/NIGHTLY-LOG.md's dated-but-independent entries (which stay useful
for a retention window), so the right cut here is "keep the newest one
live", not a calendar window.

Usage:
    python ops/rotate_status_history.py --check    report only, exit 1 if more than one entry is live
    python ops/rotate_status_history.py --apply    rotate now: keep the newest entry, archive the rest
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_PATH = os.path.join(ROOT, "STATUS.md")
ARCHIVE_PATH = os.path.join(ROOT, "STATUS-ARCHIVE.md")

# The chain sits between these two fixed, single-occurrence lines in
# section 30. Both have been stable field names since the section was
# written; if either stops matching, this script refuses to guess rather
# than silently archiving the wrong block.
CHAIN_START_AFTER = "**Autonomous Execution Readiness:**"
CHAIN_END_BEFORE = "**Business Data Knowledge,"

ARCHIVE_HEADER_FIRST_LINE = "# STATUS.md archive"
# Entries use several bold-label conventions adopted at different times
# ("**Production Knowledge, ...", "**Prior (...)", "**Superseded entry,
# ...", and a few bare "**WIDENED ...**"/"**REOPENED ...**" from before any
# label convention existed). All of them open with a bold run, so that is
# the one thing this checks; the anchors already bound the span tightly
# enough that anything in it is a chain entry by construction.
_ENTRY_LINE_RE = re.compile(r"^\*\*\S")


def split_chain(text: str):
    """Return (before, chain_lines, after) where chain_lines is the list
    of non-blank entry lines between the two anchors, in file order
    (newest first, matching the rest of STATUS.md). Raises ValueError if
    either anchor is missing or appears more than once, or if a non-
    blank, non-entry line is found inside the span (refuse to guess
    rather than archive something this script was not built to read).
    """
    start_idx = text.find(CHAIN_START_AFTER)
    if start_idx == -1:
        raise ValueError("anchor not found: %r" % CHAIN_START_AFTER)
    if text.find(CHAIN_START_AFTER, start_idx + 1) != -1:
        raise ValueError("anchor appears more than once: %r"
                          % CHAIN_START_AFTER)
    end_idx = text.find(CHAIN_END_BEFORE, start_idx)
    if end_idx == -1:
        raise ValueError("anchor not found: %r" % CHAIN_END_BEFORE)
    if text.find(CHAIN_END_BEFORE, end_idx + 1) != -1:
        raise ValueError("anchor appears more than once: %r"
                          % CHAIN_END_BEFORE)

    # The anchor only matches the bold label itself; the rest of that same
    # line (its value) is not part of the chain and must be skipped too.
    rest_of_line_end = text.find("\n", start_idx + len(CHAIN_START_AFTER))
    if rest_of_line_end == -1:
        raise ValueError("no newline after %r" % CHAIN_START_AFTER)

    before = text[:rest_of_line_end]
    span = text[rest_of_line_end:end_idx]
    after = text[end_idx:]

    lines = [ln for ln in span.split("\n") if ln.strip()]
    for ln in lines:
        if not _ENTRY_LINE_RE.match(ln):
            raise ValueError("unrecognised line inside the chain, "
                              "refusing to guess: %r" % ln[:80])
    return before, lines, after


def plan_rotation(text: str):
    """Keep the newest (first) chain entry live, archive the rest.
    Returns (new_status_text, archived_entries_in_original_order).
    Pure function of its input; does no I/O, so directly testable.
    """
    before, lines, after = split_chain(text)
    if len(lines) <= 1:
        return text, []
    keep, archived = lines[0], lines[1:]
    new_text = before + "\n\n" + keep + "\n\n" + after
    return new_text, archived


def apply_archive(archived_entries, existing_archive_text: str | None) -> str:
    """Prepend the newly-archived entries (still newest-first) above
    whatever the archive file already holds, the same "new material on
    top" shape ops/rotate_nightly_log.py uses, so repeated runs keep
    extending the same history rather than reordering it.
    """
    new_block = "\n\n".join(archived_entries)
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER_FIRST_LINE):
            raise ValueError("STATUS-ARCHIVE.md does not start with the "
                              "expected header; refusing to guess.")
        # Keep the existing header and separator rule exactly as they are;
        # insert the new block right after the first "---" divider.
        marker = "\n---\n"
        at = existing_archive_text.find(marker)
        if at == -1:
            raise ValueError("STATUS-ARCHIVE.md has no '---' divider "
                              "after its header; refusing to guess.")
        head = existing_archive_text[:at + len(marker)]
        tail = existing_archive_text[at + len(marker):]
        return head + "\n" + new_block + "\n\n" + tail.lstrip("\n")
    header = (ARCHIVE_HEADER_FIRST_LINE + "\n\n"
              "> Historical entries moved here by "
              "ops/rotate_status_history.py, newest first. Nothing here "
              "was edited on the way over.\n\n---\n")
    return header + "\n" + new_block + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="Report whether rotation is due; makes no "
                          "changes.")
    ap.add_argument("--apply", action="store_true",
                     help="Rotate now: keep the newest entry live, "
                          "archive the rest.")
    args = ap.parse_args()
    if not args.check and not args.apply:
        ap.error("pass --check or --apply")

    status_text = io.open(STATUS_PATH, encoding="utf-8").read()
    try:
        _, chain_lines, _ = split_chain(status_text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2

    if args.check:
        if len(chain_lines) > 1:
            print("DUE: %d entries live, only the newest should stay; "
                  "%d would move to %s on --apply."
                  % (len(chain_lines), len(chain_lines) - 1, ARCHIVE_PATH))
            return 1
        print("CLEAN: %d entry live. Nothing to rotate." % len(chain_lines))
        return 0

    # --apply
    new_status_text, archived = plan_rotation(status_text)
    if not archived:
        print("Already down to the newest entry; no change made.")
        return 0

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived, existing_archive_text)

    # Write-then-rename both files, archive first: if the process dies
    # between the two writes, the worst case is an entry that exists in
    # both the (unrotated) live file and the archive, never one that
    # exists in neither.
    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    status_tmp = STATUS_PATH + ".tmp"
    io.open(status_tmp, "w", encoding="utf-8").write(new_status_text)
    os.replace(status_tmp, STATUS_PATH)

    print("Moved %d entries (%d bytes) to %s. STATUS.md keeps 1 entry live."
          % (len(archived),
             len(status_text.encode("utf-8"))
             - len(new_status_text.encode("utf-8")),
             ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
