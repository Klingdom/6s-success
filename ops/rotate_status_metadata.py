#!/usr/bin/env python3
"""Move STATUS.md section 1 ("Status Metadata")'s own cycle-report chain
into STATUS-ARCHIVE.md, keeping live only the entry (or entries, if more
than one carries the same, most recent date) that is actually current.

Named by name across five consecutive cycles (2026-10-27, 14:0x through
17:1x) as the one `rotate_status_history.py`-style sibling never built:
section 1 had grown to an 11-entry, 67KB chain inside a 170KB file, the
identical "a living document grows unbounded" shape sections 10/28/29/30/
32/41/45 of BACKLOG-2026-09-07.md already fixed for every other field this
file and its siblings carry (Production Knowledge, Immediate Focus,
BLOCKER-001, the Production Status table rows, CHECKIN-LOG.md, OWNER-
ACTIONS.md, the backlog's own Done table). `gate_living_docs_total_size_
tripwire` already flags STATUS.md's total size without naming which field
is responsible; nothing had ever narrowed in on this one.

The shape here is messier than any sibling chain `rotate_status_history.py`
already handles: entries are not one bold line each (Production Knowledge),
not one bold paragraph each (BLOCKER-001), and not one table-cell segment
each (Production Status rows); they are variable-length runs of one or more
paragraphs, most bold-led but with the longer ones (OPEN LOOP, Prior) also
carrying several internal bold sub-points ("Why, precisely.", "Also killed
mid-run and therefore NOT a result:", "1. Half of 'we cannot see queries'
...") that are continuations, not entries of their own. So entry starts
here are identified by an explicit allow-list of the literal labels this
section has actually used ("**Last Updated:**", "**Earlier, ", "**Latest,
", "**CLOSED ", "**OPEN LOOP AS AT ", "**Prior ("), the same style
FOCUS_MARKER_RE in rotate_status_history.py uses to pick dated corrections
out of a line that also contains other bold text; anything else folds into
the entry above it.

A second, genuine defect surfaced while building this: the chain is NOT
reliably newest-first by file position. Two entries dated 2026-10-26 (the
most recent work in the chain when this was built) sit well below entries
dated 2026-10-23 and 2026-10-24, because at least one session prepended its
own new entry at the wrong anchor point (inside the middle of an older,
already-closed 2026-10-01 entry instead of at the very top of the
section). Keeping "whatever is physically first" live, the rule every
sibling rotator uses, would have archived the two genuinely newest entries
while leaving a 2026-10-24 entry live labelled as current: the exact "copy
and a control disagree" P0 shape CLAUDE.md's own verification rules name,
made worse rather than fixed. So this rotator keeps live every entry
carrying the maximum date found anywhere in the chain (usually exactly
one; here, two, because two 2026-10-26 entries tie), not simply the first
physical entry, and archives the rest verbatim, in their existing file
order, into STATUS-ARCHIVE.md via rotate_status_history.py's own
apply_archive() (same archive file, same "new material on top" shape;
only that one pure function is reused, not its path-coupled I/O, since
this script needs its own ROOT/STATUS_PATH/ARCHIVE_PATH for testing).

Nothing is deleted. The one-paragraph pointer note this section already
carries ("Older entries (...) live in STATUS-ARCHIVE.md") is kept and its
own count updated, rather than archived as if it were itself a dated cycle
entry.

Usage:
    python ops/rotate_status_metadata.py --check   report only, exit 1 if more than the max-date entries are live
    python ops/rotate_status_metadata.py --apply   rotate now
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_PATH = os.path.join(ROOT, "STATUS.md")
ARCHIVE_PATH = os.path.join(ROOT, "STATUS-ARCHIVE.md")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rotate_status_history as rsh  # noqa: E402  (reuse apply_archive())

SECTION_HEADING = "# 1. Status Metadata"
SECTION_END_BEFORE = "# 2. Executive Snapshot"
POINTER_MARKER = "**Older entries ("

ENTRY_START_RE = re.compile(
    r"^\*\*(?:Last Updated:\*\*|Earlier, |Latest, |CLOSED |"
    r"OPEN LOOP AS AT |Prior \()"
)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

_PARA_SPLIT_RE = re.compile(r"(\n[ \t]*\n)")


def split_metadata_chain(text: str):
    """Return (before, entries, pointer_note, after).

    entries: list of entry texts (each one or more paragraphs), in file
    order, between the section heading and the pointer note.
    pointer_note: the "Older entries (...)" paragraph's own text.
    Raises ValueError if the heading or pointer note is missing or
    duplicated, or the first paragraph in the span is not a recognised
    entry start (refuse to guess at a shape this was not built to read).
    """
    start_idx = text.find(SECTION_HEADING)
    if start_idx == -1:
        raise ValueError("heading not found: %r" % SECTION_HEADING)
    if text.find(SECTION_HEADING, start_idx + 1) != -1:
        raise ValueError("heading appears more than once: %r"
                          % SECTION_HEADING)
    heading_line_end = text.find("\n", start_idx)
    if heading_line_end == -1:
        raise ValueError("no newline after %r" % SECTION_HEADING)

    end_idx = text.find(SECTION_END_BEFORE, heading_line_end)
    if end_idx == -1:
        raise ValueError("heading not found: %r" % SECTION_END_BEFORE)
    if text.find(SECTION_END_BEFORE, end_idx + 1) != -1:
        raise ValueError("heading appears more than once: %r"
                          % SECTION_END_BEFORE)

    pointer_idx = text.find(POINTER_MARKER, heading_line_end, end_idx)
    if pointer_idx == -1:
        raise ValueError("pointer note not found: %r" % POINTER_MARKER)
    if text.find(POINTER_MARKER, pointer_idx + 1, end_idx) != -1:
        raise ValueError("pointer note appears more than once: %r"
                          % POINTER_MARKER)
    pointer_end = text.find("\n\n", pointer_idx)
    if pointer_end == -1 or pointer_end > end_idx:
        pointer_end = end_idx

    # Consume the full blank line after the heading into `before`, not
    # just the heading line's own newline: the heading line contributes
    # one newline and the blank line contributes a second, and leaving
    # the second one dangling at the start of `span` meant it was
    # neither a recognised blank-line separator (which needs two in a
    # row) nor part of any entry's own text, so it silently vanished on
    # the first .strip() and reappeared as an extra blank line on
    # reconstruction. Doing this also means `span` starts exactly on the
    # first entry's own text, with nothing stray to strip.
    content_start = heading_line_end + 1
    while content_start < pointer_idx and text[content_start] == "\n":
        content_start += 1

    before = text[:content_start]
    span = text[content_start:pointer_idx]
    pointer_note = text[pointer_idx:pointer_end]
    after = text[pointer_end:]

    parts = _PARA_SPLIT_RE.split(span)
    paras = parts[0::2]
    if not paras or not paras[0].strip():
        raise ValueError("span is empty or has no first paragraph")
    if not ENTRY_START_RE.match(paras[0].strip()):
        raise ValueError("first paragraph is not a recognised entry "
                          "start, refusing to guess: %r" % paras[0][:80])

    bounds = []
    cur_start = None
    for i, p in enumerate(paras):
        if not p.strip():
            continue
        if ENTRY_START_RE.match(p.strip()):
            if cur_start is not None:
                bounds.append((cur_start, i - 1))
            cur_start = i
    if cur_start is not None:
        bounds.append((cur_start, len(paras) - 1))

    entries = ["".join(parts[2 * a:2 * b + 1]).strip() for a, b in bounds]

    # Prove the split is lossless before trusting it with --apply.
    recon_pieces = []
    for i, (a, b) in enumerate(bounds):
        recon_pieces.append("".join(parts[2 * a:2 * b + 1]))
        if i < len(bounds) - 1:
            recon_pieces.append(parts[2 * b + 1])
    if "".join(recon_pieces) != span:
        raise ValueError("entry split did not reconstruct the span "
                          "exactly, refusing to guess")

    return before, entries, pointer_note, after


def _entry_date(entry: str) -> str:
    m = DATE_RE.search(entry)
    if not m:
        raise ValueError("entry carries no recognisable date, refusing "
                          "to guess: %r" % entry[:80])
    return m.group(0)


_POINTER_COUNT_RE = re.compile(r"^\*\*Older entries \((\d+) of them")


def _updated_pointer_note(pointer_note: str, newly_archived: int,
                           newest_kept_date: str, apply_date: str) -> str:
    m = _POINTER_COUNT_RE.match(pointer_note)
    if not m:
        raise ValueError("pointer note does not match the expected count "
                          "format, refusing to guess: %r" % pointer_note[:80])
    new_count = int(m.group(1)) + newly_archived
    return (
        "**Older entries (%d of them, 2026-08 to %s) live in "
        "`STATUS-ARCHIVE.md`.** Rotated %s by `ops/rotate_status_metadata."
        "py --apply`: kept live only the entry (or entries, where more "
        "than one shares the same most recent date) carrying %s, the "
        "actual most recent date found in the chain, not simply whichever "
        "entry happened to sit physically first (the chain had drifted "
        "out of newest-first order); %d more entries moved to the "
        "archive. Nothing is deleted, and the gates that scan this file "
        "for stale claims (`gate_no_stale_session_label`, "
        "`gate_no_stale_checkout_count`, `gate_no_stale_listmonk_blocker`, "
        "`gate_corporate_buy_path_current`, `gate_critical_risks_"
        "escalated`) scan the archive too, so an archived claim is no "
        "less checked than a current one."
        % (new_count, newest_kept_date, apply_date, newest_kept_date,
           newly_archived)
    )


def plan_rotation(text: str, apply_date: str):
    """Keep live every entry carrying the maximum date found in the
    chain (in file order); archive the rest, also in file order.
    Returns (new_status_text, archived_entries), or (text, []) if there
    is nothing to rotate (one entry, or every entry already tied at the
    same date). Pure function of its input; does no I/O.
    """
    before, entries, pointer_note, after = split_metadata_chain(text)
    if len(entries) <= 1:
        return text, []
    dates = [_entry_date(e) for e in entries]
    max_date = max(dates)
    keep = [e for e, d in zip(entries, dates) if d == max_date]
    archived = [e for e, d in zip(entries, dates) if d != max_date]
    if not archived:
        return text, []

    new_pointer = _updated_pointer_note(pointer_note, len(archived),
                                         max_date, apply_date)
    new_text = before + "\n\n".join(keep) + "\n\n" + new_pointer + after
    return new_text, archived


def _write_rotated(new_status_text: str, archived, status_text: str) -> None:
    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = rsh.apply_archive(archived, existing_archive_text)

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
                     help="report whether rotation is due; makes no "
                          "changes.")
    ap.add_argument("--apply", action="store_true",
                     help="rotate now: keep the most-recently-dated "
                          "entry/entries live, archive the rest.")
    args = ap.parse_args()
    if sum(bool(m) for m in (args.check, args.apply)) != 1:
        ap.error("pass exactly one of --check, --apply")

    status_text = io.open(STATUS_PATH, encoding="utf-8").read()
    apply_date = datetime.date.today().isoformat()

    try:
        _, entries, _, _ = split_metadata_chain(status_text)
    except ValueError as exc:
        print("REFUSING: %s" % exc)
        return 2

    if args.check:
        try:
            dates = [_entry_date(e) for e in entries]
        except ValueError as exc:
            print("REFUSING: %s" % exc)
            return 2
        max_date = max(dates) if dates else None
        extra = sum(1 for d in dates if d != max_date)
        if extra:
            print("DUE: %d entries live, only %d carry the most recent "
                  "date (%s); %d would move to %s on --apply."
                  % (len(entries), len(entries) - extra, max_date, extra,
                     ARCHIVE_PATH))
            return 1
        print("CLEAN: %d entry/entries live, all at the same most recent "
              "date. Nothing to rotate." % len(entries))
        return 0

    # --apply
    new_status_text, archived = plan_rotation(status_text, apply_date)
    if not archived:
        print("Already down to the most-recently-dated entry/entries; no "
              "change made.")
        return 0
    _write_rotated(new_status_text, archived, status_text)
    print("STATUS.md section 1 keeps only the most-recently-dated "
          "entry/entries live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
