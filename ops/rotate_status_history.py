#!/usr/bin/env python3
"""Move STATUS.md's superseded "Production Knowledge" and "Immediate Focus"
history into STATUS-ARCHIVE.md, keeping only the current statement live.

STATUS.md section 24 ("How to Update Status") already states the rule this
script enforces: "move historical detail to the appropriate long-term file.
Do not allow this document to become an archive." Nothing had ever carried
that rule out for either field. Section 30 ("Current Overall Assessment")
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

Found again, same date, same section: the "Immediate Focus" field grew the
identical way but in a different shape. Rather than separate bold-prefixed
lines (newest first), every correction since 2026-09-02 was appended as a
plain sentence onto the SAME single line (oldest first), because the field
has no per-entry line break to anchor a new bold paragraph against. By
2026-10-23 that one line read 15KB, and every correction in it did nothing
but re-state the deploy-gap figure the Production Knowledge paragraph two
fields above already tracks ("THIS LINE NEVER CAUGHT UP WITH THE PRODUCTION
KNOWLEDGE PARAGRAPH ABOVE OR BLOCKER-001" is the chain's own words for it).
So this field's rotation is not "keep the newest line", it is "keep the
base statement, point at the field that already owns deploy-gap detail, and
archive every dated correction", handled by split_focus_line/
plan_rotation_focus below, a parallel but separately-shaped operation from
split_chain/plan_rotation above. Both write to the same STATUS-ARCHIVE.md.

Nothing is deleted. Entries move verbatim, in their existing order, into
STATUS-ARCHIVE.md: CLAUDE.md section 54 ("Failure Is Information") and
STATUS-ARCHIVE.md's own header both say the record must survive.

Only the two named fields under section 30 are touched. A single, explicitly
superseding chain, where only the newest entry is ever current, is a
different shape from ops/NIGHTLY-LOG.md's dated-but-independent entries
(which stay useful for a retention window), so the right cut here is "keep
the newest one live", not a calendar window.

Usage:
    python ops/rotate_status_history.py --check         report only, exit 1 if more than one Production Knowledge entry is live
    python ops/rotate_status_history.py --apply         rotate Production Knowledge now
    python ops/rotate_status_history.py --check-focus    report only, exit 1 if Immediate Focus carries a dated correction chain
    python ops/rotate_status_history.py --apply-focus    rotate Immediate Focus now
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


FOCUS_LABEL = "**Immediate Focus:**"

# Every dated correction on the Immediate Focus line opens with one of
# these verbs immediately followed by a date (plain "2026-10-09", or with
# a time component: "2026-10-01T11:2x", "2026-10-03T15:43:15Z"). The verb
# plus the date digits is the one thing every correction has in common;
# matching only that much, rather than the free-text label after it
# ("SCHEDULED OPERATOR", "PM CHECK-IN (23:4x SLOT)", ...), is what keeps
# this from needing to be taught every new label this file invents.
FOCUS_MARKER_RE = re.compile(
    r"\b(?:UPDATED|CORRECTED|WIDENED|NARROWED|CLOSED(?: AGAIN)?|"
    r"SUPERSEDED|RE-CONFIRMED|REOPENED) \d{4}-\d{2}-\d{2}"
)


def split_focus_line(text: str):
    """Return (before, base_statement, dated_entries, after) for the
    single-line "Immediate Focus" field.

    Unlike split_chain above, this field has no per-entry line break: the
    base statement and every dated correction since sit on one physical
    line, oldest first. dated_entries is returned in that same oldest-
    first order. Raises ValueError if the label is missing, appears more
    than once, or has no newline to its own end (refuse to guess).
    """
    start_idx = text.find(FOCUS_LABEL)
    if start_idx == -1:
        raise ValueError("anchor not found: %r" % FOCUS_LABEL)
    if text.find(FOCUS_LABEL, start_idx + 1) != -1:
        raise ValueError("anchor appears more than once: %r" % FOCUS_LABEL)
    value_start = start_idx + len(FOCUS_LABEL)
    line_end = text.find("\n", value_start)
    if line_end == -1:
        raise ValueError("no newline after %r" % FOCUS_LABEL)

    before = text[:start_idx]
    value = text[value_start:line_end]
    after = text[line_end:]

    # A correction marker only starts a new entry when it opens a new
    # sentence. The base statement's own opening clause ("UNCHANGED IN
    # SUBSTANCE SINCE 2026-09-02, RE-CONFIRMED 2026-09-15: ...") also
    # matches FOCUS_MARKER_RE on "RE-CONFIRMED 2026-09-15", but that one
    # is introduced by a comma, not a sentence boundary, so it is not a
    # real entry; every genuine entry is preceded by sentence-ending
    # punctuation (".", "\"", ")") once trailing whitespace is stripped.
    matches = [m for m in FOCUS_MARKER_RE.finditer(value)
               if value[:m.start()].rstrip()[-1:] in (".", "\"", ")")]
    base = value[:matches[0].start()].strip() if matches else value.strip()
    entries = []
    for i, m in enumerate(matches):
        seg_end = matches[i + 1].start() if i + 1 < len(matches) else len(value)
        entry = value[m.start():seg_end].strip()
        if entry:
            entries.append(entry)
    return before, base, entries, after


def _focus_entry_for_archive(entry: str) -> str:
    """Format one dated correction for STATUS-ARCHIVE.md, bolding its
    "VERB date, label:" header the same way the Production Knowledge
    entries already bold theirs, so both read the same way in the
    archive. Falls back to an unbolded line if no ": " header boundary
    is found, rather than guessing at one.
    """
    marker = ": "
    at = entry.find(marker)
    if at == -1:
        return "**Immediate Focus** -- %s" % entry
    header, rest = entry[:at], entry[at + len(marker):]
    return "**Immediate Focus, %s:** %s" % (header, rest)


def plan_rotation_focus(text: str, replacement_tail: str):
    """Keep the base statement live, with `replacement_tail` appended in
    place of the dated correction chain, and archive every dated entry
    verbatim (reformatted only to bold its own header, never its
    content), oldest first -- this field's own natural order, the
    opposite of the Production Knowledge chain's newest-first convention
    above. Returns (new_status_text, archived_entries), or (text, []) if
    there is nothing to rotate. Pure function of its input; does no I/O.
    """
    before, base, entries, after = split_focus_line(text)
    if not entries:
        return text, []
    new_line = "%s %s %s" % (FOCUS_LABEL, base.rstrip(), replacement_tail)
    new_text = before + new_line + after
    # entries is oldest-first (this field's own order); STATUS-ARCHIVE.md's
    # own header promises newest-first throughout, matching the Production
    # Knowledge entries apply_archive() already writes, so reverse here
    # rather than make apply_archive() guess which convention its caller used.
    archived = [_focus_entry_for_archive(e) for e in reversed(entries)]
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


FOCUS_REPLACEMENT_TAIL = (
    "FOR CURRENT DEPLOY STATUS SEE THE PRODUCTION KNOWLEDGE PARAGRAPH "
    "ABOVE AND `BLOCKER-001`, NOT THIS LINE. ROTATED 2026-10-23, SCHEDULED "
    "OPERATOR, BY `ops/rotate_status_history.py --apply-focus`: THE DATED "
    "CORRECTION CHAIN THAT USED TO SIT HERE (2026-09-30 THROUGH 2026-10-23) "
    "DID NOTHING BUT RE-STATE THAT SAME DEPLOY FIGURE AND NEVER CAUGHT UP "
    "WITH IT; MOVED VERBATIM TO `STATUS-ARCHIVE.md`."
)


def _write_rotated(new_status_text: str, archived, status_text: str) -> None:
    """Shared write path for both --apply and --apply-focus: archive
    first, then the live file, so a crash between the two writes leaves
    an entry duplicated rather than lost.
    """
    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived, existing_archive_text)

    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    status_tmp = STATUS_PATH + ".tmp"
    io.open(status_tmp, "w", encoding="utf-8").write(new_status_text)
    os.replace(status_tmp, STATUS_PATH)

    print("Moved %d entries (%d bytes) to %s."
          % (len(archived),
             len(status_text.encode("utf-8"))
             - len(new_status_text.encode("utf-8")),
             ARCHIVE_PATH))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="Production Knowledge: report whether rotation "
                          "is due; makes no changes.")
    ap.add_argument("--apply", action="store_true",
                     help="Production Knowledge: rotate now, keep the "
                          "newest entry live, archive the rest.")
    ap.add_argument("--check-focus", action="store_true",
                     help="Immediate Focus: report whether a dated "
                          "correction chain has grown on the line; makes "
                          "no changes.")
    ap.add_argument("--apply-focus", action="store_true",
                     help="Immediate Focus: rotate now, keep the base "
                          "statement live, archive every dated correction.")
    args = ap.parse_args()
    modes = (args.check, args.apply, args.check_focus, args.apply_focus)
    if sum(bool(m) for m in modes) != 1:
        ap.error("pass exactly one of --check, --apply, --check-focus, "
                  "--apply-focus")

    status_text = io.open(STATUS_PATH, encoding="utf-8").read()

    if args.check or args.apply:
        try:
            _, chain_lines, _ = split_chain(status_text)
        except ValueError as exc:
            print("REFUSING: %s" % exc)
            return 2
        if args.check:
            if len(chain_lines) > 1:
                print("DUE: %d entries live, only the newest should stay; "
                      "%d would move to %s on --apply."
                      % (len(chain_lines), len(chain_lines) - 1,
                         ARCHIVE_PATH))
                return 1
            print("CLEAN: %d entry live. Nothing to rotate." % len(chain_lines))
            return 0
        # --apply
        new_status_text, archived = plan_rotation(status_text)
        if not archived:
            print("Already down to the newest entry; no change made.")
            return 0
        _write_rotated(new_status_text, archived, status_text)
        print("STATUS.md keeps 1 Production Knowledge entry live.")
        return 0

    # --check-focus or --apply-focus
    try:
        _, _, entries, _ = split_focus_line(status_text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2
    if args.check_focus:
        if entries:
            print("DUE: %d dated correction(s) live on the Immediate Focus "
                  "line; they would move to %s on --apply-focus."
                  % (len(entries), ARCHIVE_PATH))
            return 1
        print("CLEAN: no dated corrections on the Immediate Focus line.")
        return 0
    # --apply-focus
    new_status_text, archived = plan_rotation_focus(
        status_text, FOCUS_REPLACEMENT_TAIL)
    if not archived:
        print("No dated corrections on the Immediate Focus line; no "
              "change made.")
        return 0
    _write_rotated(new_status_text, archived, status_text)
    print("Immediate Focus line kept to its base statement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
