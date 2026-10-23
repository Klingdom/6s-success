#!/usr/bin/env python3
"""Move old rows out of BACKLOG-2026-09-07.md's "Done this week, for the
record" table into BACKLOG-2026-09-07-ARCHIVE.md.

Found 2026-10-23, the designated next cold-read left by that day's
ops/rotate_owner_actions.py fix: BACKLOG-2026-09-07.md itself has the
identical unbounded-growth shape its own section 7 names as this
repository's dominant defect class, and that STATUS.md, ops/NIGHTLY-LOG.md,
CHECKIN-LOG.md and OWNER-ACTIONS.md already got gated for. The file is
568KB; its own "## 1. Done this week, for the record" table alone is
282KB across 34 rows back to 2026-09-07, every row a completed item kept
only for the record, append-only, never rotated, because nothing before
this checked whether it needed to be. STEP 1 of the operating prompt reads
this file every single cycle as "the CURRENT queue... your work list",
so every cycle has been paying to load a month of closed history to find
the half-dozen still-open rows in sections 0 and 1b-7.

Two of the 34 rows (the oldest two, both from 2026-09-21/22) had also
degraded to bare paragraphs missing the table's leading "| " and trailing
" |" delimiters, which breaks table rendering for just those two rows; a
by-product of this rotation is that any row it touches is re-emitted with
the correct "| ... |" shape, live or archived.

Nothing here deletes a word. Rows move verbatim (reformatted to valid
table syntax where it had degraded, never reworded) into BACKLOG-2026-09-
07-ARCHIVE.md, newest-first, matching the live table's own order; CLAUDE.md's
Decision/Learning Memory sections say not to erase the record, and this
file's own "Failure Is Information" principle (CLAUDE.md section 54)
applies to a done-item ledger as much as to a mistake. Deliberately scoped
to section 1 alone: sections 2-4 and 8-31 mix open rows with closed ones
or use a different per-item numbering other code may reference by name
("B9", "D5"), which makes "archive anything closed" a different, higher-
risk job than lifting a flat, all-done table out whole. Left for a future
cycle, the same way this file's own section 30 deferred the OWNER-
ACTIONS.md preamble work rather than guess at it.

Usage:
    python ops/rotate_backlog.py --check            report only, exit 1 if over the window
    python ops/rotate_backlog.py --check --days N    use a different retention window
    python ops/rotate_backlog.py --apply             rotate now (default 14-day window)
    python ops/rotate_backlog.py --apply --days N
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-ARCHIVE.md")

SECTION_HEADING = "## 1. Done this week, for the record"
TABLE_HEADER = "| Item | Evidence |"
TABLE_SEP = "|---|---|"
NEXT_HEADING_ANCHOR = "\n\n---\n\n## 1b."

ARCHIVE_HEADER_FIRST_LINE = "# BACKLOG-2026-09-07.md archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Rows older than ops/rotate_backlog.py's retention window, moved here "
    "verbatim (reformatted to valid table syntax where the live row had "
    "degraded) from BACKLOG-2026-09-07.md's \"Done this week, for the "
    "record\" table by that script. Never hand-edited. Newest first, "
    "same convention as the live table.\n\n"
    + TABLE_HEADER + "\n" + TABLE_SEP + "\n"
)

DEFAULT_RETENTION_DAYS = 14


def locate_section(text: str):
    """Return (table_header_end, body_end) marking the table body: right
    after TABLE_HEADER's own line, up to (not including) the "---" divider
    before "## 1b.". Raises ValueError if any anchor is missing or
    duplicated, refusing to guess rather than move the wrong text.
    """
    if text.count(SECTION_HEADING) != 1:
        raise ValueError("SECTION_HEADING missing or duplicated")
    start = text.find(SECTION_HEADING)
    header_at = text.find(TABLE_HEADER, start)
    if header_at == -1:
        raise ValueError("TABLE_HEADER not found after SECTION_HEADING")
    body_start = header_at + len(TABLE_HEADER)
    if text.count(NEXT_HEADING_ANCHOR) != 1:
        raise ValueError("NEXT_HEADING_ANCHOR missing or duplicated")
    body_end = text.find(NEXT_HEADING_ANCHOR, body_start)
    if body_end == -1:
        raise ValueError("NEXT_HEADING_ANCHOR does not follow the table")
    return body_start, body_end


def parse_rows(body: str):
    """One entry per non-blank line that opens with (optionally) a
    leading pipe and then '**', in original order. Lines that are just a
    stray '|---|---|' separator (several accreted over past edits) are
    dropped; they carry no data. A real row's own text always opens with
    '**' because every entry's bold title is the first thing on its line,
    live or (as found 2026-10-23) missing its pipe delimiters.
    """
    rows = []
    for line in body.split("\n"):
        s = line.strip()
        if not s or s == TABLE_SEP:
            continue
        if re.match(r"^\|?\s*\*\*", s):
            rows.append(s)
    return rows


def normalize_row(row: str) -> str:
    """Re-wrap a row's content in exactly one leading '| ' and trailing
    ' |', regardless of whether it already had them. Idempotent, and
    fixes the two 2026-10-23-found rows that had neither.
    """
    s = row.strip()
    if s.startswith("|"):
        s = s[1:].strip()
    if s.endswith("|"):
        s = s[:-1].strip()
    return "| " + s + " |"


def row_date(row: str):
    """The first YYYY-MM-DD date inside the row's own bold title span
    (text between the first '**' pair). That span is always this row's
    own completion sentence ("...2026-10-14 scheduled operator."); any
    date the Evidence cell after it cites is an earlier reference, not
    this row's own, and sits later in the string regardless. Returns None
    if there is no bold span or no date in it, kept live rather than
    guessed, same convention as ops/rotate_nightly_log.py's leading_
    entry_date().
    """
    m = re.match(r"^\|?\s*\*\*(.*?)\*\*", row)
    if not m:
        return None
    dm = re.search(r"(\d{4}-\d{2}-\d{2})", m.group(1))
    if not dm:
        return None
    try:
        return datetime.date.fromisoformat(dm.group(1))
    except ValueError:
        return None


def plan_rotation(text: str, cutoff: datetime.date):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_rows_in_original_order, kept_count). Rows with no resolvable
    date are kept live, never guessed into the archive.
    """
    body_start, body_end = locate_section(text)
    body = text[body_start:body_end]
    rows = parse_rows(body)
    keep, archived = [], []
    for r in rows:
        d = row_date(r)
        if d is not None and d < cutoff:
            archived.append(normalize_row(r))
        else:
            keep.append(normalize_row(r))
    if not archived:
        return text, [], len(keep)
    new_body = "\n" + TABLE_SEP + "\n" + "\n".join(keep)
    new_body += "\n" if keep else ""
    new_text = text[:body_start] + new_body + text[body_end:]
    return new_text, archived, len(keep)


def apply_archive(archived_rows, existing_archive_text):
    """Build the new archive file text: the fixed header, then the newly-
    archived rows (already newest-first), then whatever the archive
    already held. New material goes on top, same prepend-above-existing-
    content shape as ops/rotate_nightly_log.py's apply_archive, so repeat
    runs keep extending one growing archive instead of reordering it.
    """
    new_chunk = "\n".join(archived_rows)
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER_FIRST_LINE):
            raise ValueError("BACKLOG-2026-09-07-ARCHIVE.md does not start "
                              "with the expected header; refusing to guess.")
        header_end = existing_archive_text.find(TABLE_SEP)
        if header_end == -1:
            raise ValueError("BACKLOG-2026-09-07-ARCHIVE.md has no table "
                              "separator after its header; refusing to "
                              "guess.")
        old_body = existing_archive_text[header_end + len(TABLE_SEP):].lstrip("\n")
    else:
        old_body = ""
    body = new_chunk if not old_body else new_chunk + "\n" + old_body
    if not body.endswith("\n"):
        body += "\n"
    return ARCHIVE_HEADER + body


def count_stats(text: str, cutoff: datetime.date):
    body_start, body_end = locate_section(text)
    rows = parse_rows(text[body_start:body_end])
    overdue = sum(1 for r in rows if (d := row_date(r)) is not None and d < cutoff)
    return len(rows), overdue, len((text[body_start:body_end]).encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="Report current size and whether rotation is due; "
                          "makes no changes.")
    ap.add_argument("--apply", action="store_true",
                     help="Rotate now: move rows older than --days into "
                          "the archive.")
    ap.add_argument("--days", type=int, default=DEFAULT_RETENTION_DAYS,
                     help="Retention window in days (default %d)."
                          % DEFAULT_RETENTION_DAYS)
    args = ap.parse_args()
    if not args.check and not args.apply:
        ap.error("pass --check or --apply")

    text = io.open(BACKLOG_PATH, encoding="utf-8").read()
    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    n_rows, overdue, n_bytes = count_stats(text, cutoff)

    if args.check:
        if overdue:
            print("DUE: %d of %d rows (%d bytes in the table) are older "
                  "than %s (retention %d days) and would move to %s on "
                  "--apply." % (overdue, n_rows, n_bytes, cutoff.isoformat(),
                                 args.days, ARCHIVE_PATH))
            return 1
        print("CLEAN: all %d rows (%d bytes in the table) are within the "
              "%d-day retention window (cutoff %s). Nothing to rotate."
              % (n_rows, n_bytes, args.days, cutoff.isoformat()))
        return 0

    # --apply
    new_text, archived, kept = plan_rotation(text, cutoff)
    if not archived:
        print("Nothing older than %s (retention %d days); no change made."
              % (cutoff.isoformat(), args.days))
        return 0

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived, existing_archive_text)

    # Write-then-rename both files, archive first: if the process dies
    # between the two writes, the worst case is a row that exists in both
    # the (unrotated) live table and the archive, never one that exists
    # in neither.
    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    backlog_tmp = BACKLOG_PATH + ".tmp"
    io.open(backlog_tmp, "w", encoding="utf-8").write(new_text)
    os.replace(backlog_tmp, BACKLOG_PATH)

    _, new_bytes = len(archived), len(new_text[locate_section(new_text)[0]:locate_section(new_text)[1]].encode("utf-8"))
    print("Moved %d rows to %s. Live table: %d rows, %d bytes (was %d "
          "rows, %d bytes)." % (len(archived), ARCHIVE_PATH, kept,
                                 new_bytes, n_rows, n_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
