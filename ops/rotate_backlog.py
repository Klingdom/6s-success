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
    python ops/rotate_backlog.py --check                report only, exit 1 if over the window or the row cap
    python ops/rotate_backlog.py --check --days N        use a different retention window
    python ops/rotate_backlog.py --apply                 rotate now (default: 2-day window, 15-row cap)
    python ops/rotate_backlog.py --apply --days N
    python ops/rotate_backlog.py --apply --max-rows N    use a different row-count cap (0 disables it)
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

DEFAULT_RETENTION_DAYS = 2

# Found 2026-11-12: at 14 days this constant made the gate's own suggested
# remedy, a bare `--apply` with no --days flag, a no-op against a table that
# was genuinely 97KB over budget. Entry size per row has grown with the
# FORMAT_WORDS/zone-also-called mining cadence (each day's own rows now run
# several KB apiece), so a 14-day window kept the whole week live no matter
# how badly BACKLOG-2026-09-07.md had crossed gate_living_docs_total_size_
# tripwire's 150000-byte ceiling. Lowered to 2 days so the bare command this
# file's own gate message tells a cold-reading cycle to run actually shrinks
# the table when that cycle runs it, the same reasoning ops/rotate_backlog_
# closed.py's own history already used twice for the same symptom.

# Found again 2026-11-12, same cold-read, a few hours later: lowering the
# days did not actually fix the root cause. The current hourly/sub-hourly
# cadence writes 10-20+ rows in a single calendar day, so a purely date-
# based window of ANY length keeps every one of today's own rows live no
# matter how small --days is set, once --days >= 1. `--check` reported
# CLEAN (0 overdue, cutoff respected) on a table that was still 88717 bytes
# across 28 rows, every single one dated today or yesterday, 9155 bytes
# over gate_living_docs_total_size_tripwire's ceiling. A second, row-count-
# based cap closes that gap: once more than MAX_ROWS rows are live,
# regardless of date, the oldest-by-position rows (this table's own
# newest-first convention puts them at the end) rotate out too. Nothing
# about date-based retention changes; this is purely an additional trigger
# for the exact same archive-verbatim action, so a row that is both recent
# and over the row cap still moves, unreworded, to the same archive file.
DEFAULT_MAX_ROWS = 15


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


def plan_rotation(text: str, cutoff: datetime.date, max_rows: int = None):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_rows_in_original_order, kept_count). Rows with no resolvable
    date are kept live, never guessed into the archive, by the date check
    alone; the row-count cap below can still archive an undated row if it
    is old enough by position, same as any other overflow row.

    Two independent triggers decide the archive set, unioned together:
    date (any row older than `cutoff`) and, if `max_rows` is given,
    position (once more than `max_rows` rows remain live after the date
    filter, the oldest-by-position among them, i.e. the ones nearest the
    end of this newest-first table, archive too). Found 2026-11-12: a
    purely date-based window cannot bound this table's size at the
    current cadence, because a single day's own cycles can write more
    rows than any sane retention window would ever exclude; see the
    constant comment above DEFAULT_MAX_ROWS.
    """
    body_start, body_end = locate_section(text)
    body = text[body_start:body_end]
    rows = parse_rows(body)
    normalized = [normalize_row(r) for r in rows]
    archive_idx = set(
        i for i, r in enumerate(rows)
        if (d := row_date(r)) is not None and d < cutoff
    )
    if max_rows is not None:
        remaining_in_order = [i for i in range(len(rows)) if i not in archive_idx]
        if len(remaining_in_order) > max_rows:
            archive_idx.update(remaining_in_order[max_rows:])
    if not archive_idx:
        return text, [], len(rows)
    archived = [normalized[i] for i in sorted(archive_idx)]
    keep = [normalized[i] for i in range(len(rows)) if i not in archive_idx]
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


def count_stats(text: str, cutoff: datetime.date, max_rows: int = None):
    body_start, body_end = locate_section(text)
    rows = parse_rows(text[body_start:body_end])
    overdue = sum(1 for r in rows if (d := row_date(r)) is not None and d < cutoff)
    over_cap = max(0, len(rows) - max_rows) if max_rows is not None else 0
    return len(rows), overdue, over_cap, len((text[body_start:body_end]).encode("utf-8"))


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
    ap.add_argument("--max-rows", type=int, default=DEFAULT_MAX_ROWS,
                     help="Row-count cap, independent of date: once more "
                          "than this many rows are live, the oldest-by-"
                          "position overflow rotates too (default %d). "
                          "Pass 0 to disable the cap and rotate by date "
                          "alone." % DEFAULT_MAX_ROWS)
    args = ap.parse_args()
    if not args.check and not args.apply:
        ap.error("pass --check or --apply")
    max_rows = args.max_rows if args.max_rows > 0 else None

    text = io.open(BACKLOG_PATH, encoding="utf-8").read()
    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    n_rows, overdue, over_cap, n_bytes = count_stats(text, cutoff, max_rows)

    if args.check:
        if overdue or over_cap:
            print("DUE: %d of %d rows are older than %s (retention %d "
                  "days), %d rows are past the %s-row cap, %d bytes in "
                  "the table. Would move to %s on --apply."
                  % (overdue, n_rows, cutoff.isoformat(), args.days,
                     over_cap, max_rows, n_bytes, ARCHIVE_PATH))
            return 1
        print("CLEAN: all %d rows (%d bytes in the table) are within the "
              "%d-day retention window (cutoff %s) and the %s-row cap. "
              "Nothing to rotate."
              % (n_rows, n_bytes, args.days, cutoff.isoformat(), max_rows))
        return 0

    # --apply
    new_text, archived, kept = plan_rotation(text, cutoff, max_rows)
    if not archived:
        print("Nothing older than %s (retention %d days) and nothing past "
              "the %s-row cap; no change made."
              % (cutoff.isoformat(), args.days, max_rows))
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
