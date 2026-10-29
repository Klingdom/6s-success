#!/usr/bin/env python3
"""Archive old free-form journal rows (A7 onward) out of
BACKLOG-2026-09-07.md section 2, "Now: micro zones and the web app".

ops/rotate_backlog_done_items.py already rotates the original, dated-
2026-09-07/08 table rows (A1-A6, B1-B4, B6, B8, B9, C1-C3, C7) whose Item
cell is unambiguously `| **ID** | ~~struck title~~ | ...`, and its own
docstring explicitly defers every "ID, date, ..." free-form journal row
(A7 onward in section 2; B5/B7 and C4-C6's later notes in sections 3-4)
as "the larger job the sibling tools already deferred."

Found 2026-10-29, scheduled operator cycle: gate_living_docs_total_size_
tripwire flagged BACKLOG-2026-09-07.md at 332KB against its 150KB
tripwire, after ops/rotate_backlog.py and ops/rotate_backlog_closed.py
were both already run clean this same cycle (they rotate section 1's
"Done this week" table and the numbered "## N. Closed" sections 8+, and
left nothing further due). Section 2 alone is 72KB of the file, and 22
of its 23 A7-A29 journal rows carry a resolvable date more than 14 days
old. This is the next prunable chain gate_living_docs_total_size_
tripwire's own docstring asks for: "the same rotate_*.py/gate_*_not_
oversized treatment this file's siblings already got."

Deliberately scoped to section 2 only. Sections 3-4 (B5/B7, C4-C6) reuse
the same free-form shape but reuse ids within one section (B4 and B8
each appear twice, C6/C7 interleave across four separate rows, per
rotate_backlog_done_items.py's own docstring), which this script's
single-row-per-id assumption does not safely cover; left for a future
cycle with its own dedicated pass, the same kind of explicit deferral
rotate_backlog.py and rotate_backlog_closed.py already made for this
exact section before this script existed.

Each A7+ row is confirmed (by direct scan, not assumed) to be exactly
one line: `| **A<N>, <lead sentence ending in a closing "**">** <long
narrative> |`. Only the trailing narrative moves; the bold lead sentence
(id, date, byline, one-line summary) stays live as the pointer, the same
convention ops/rotate_backlog_done_items.py uses for its own rows. A row
with no resolvable date (A1-A6, already pointers) is left untouched,
never guessed into the archive, the same safeguard ops/rotate_backlog_
closed.py uses.

Nothing is deleted. Archived narrative moves verbatim into
BACKLOG-2026-09-07-SECTION2-ARCHIVE.md, newest first, a dedicated file
rather than reusing BACKLOG-2026-09-07-ITEMS-ARCHIVE.md: that file's own
header and ops/rotate_backlog_done_items.py's strict header match would
both be put at risk by a second writer with a different row shape.

Usage:
    python ops/rotate_backlog_section2_items.py --check
    python ops/rotate_backlog_section2_items.py --check --days N
    python ops/rotate_backlog_section2_items.py --apply   (default 14-day window)
    python ops/rotate_backlog_section2_items.py --apply --days N
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-SECTION2-ARCHIVE.md")

DEFAULT_RETENTION_DAYS = 14

SECTION_START_RE = re.compile(r"(?m)^## 2\. Now: micro zones and the web app")
NEXT_SECTION_RE = re.compile(r"(?m)^## 3\. ")
ROW_START_RE = re.compile(r"(?m)^\| \*\*(A\d+)")

ARCHIVE_HEADER_FIRST_LINE = "# BACKLOG-2026-09-07.md section 2 journal-row archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Free-form \"A<N>, date, ...\" journal rows older than ops/rotate_"
    "backlog_section2_items.py's retention window, moved here verbatim "
    "from BACKLOG-2026-09-07.md section 2 by that script. Never hand-"
    "edited. Newest first.\n"
)

ARCHIVED_MARKER = "Archived; see `BACKLOG-2026-09-07-SECTION2-ARCHIVE.md`."


def find_section2(text: str):
    """Return (start, end) of section 2's span in `text`, end exclusive
    (the start of section 3, or len(text) if section 3 is not found,
    kept live rather than guessed)."""
    m = SECTION_START_RE.search(text)
    if not m:
        return None, None
    start = m.start()
    nm = NEXT_SECTION_RE.search(text, m.end())
    end = nm.start() if nm else len(text)
    return start, end


def find_rows(text: str, start: int, end: int):
    """Return a list of dicts, one per `| **A<N>...` row line within
    [start, end): {id, lead, date, row_start, row_end, line}. `lead` is
    the text of the row's own leading bold span (between the first pair
    of `**`), or None if the row has no closing `**` on its own line
    (kept live, never guessed). `date` is the first YYYY-MM-DD found in
    `lead`, or None if the row names no date (A1-A6's own pointer rows,
    OR a row this script has already rotated: its pointer keeps the
    original lead sentence, date and all, for a human skimming the
    table, so a rotated row is recognised by its own ARCHIVED_MARKER
    body and excluded here rather than re-archived on every later run).
    `row_end` is the start of the next matched row or `end`.
    """
    starts = [m.start() for m in ROW_START_RE.finditer(text, start, end)]
    rows = []
    for i, row_start in enumerate(starts):
        row_end = starts[i + 1] if i + 1 < len(starts) else end
        nl = text.find("\n", row_start, row_end)
        line_end = nl if nl != -1 else row_end
        line = text[row_start:line_end]
        bm = re.match(r"^\| \*\*(.*?)\*\*(.*)$", line)
        lead = bm.group(1) if bm else None
        rest = bm.group(2) if bm else ""
        already_archived = ARCHIVED_MARKER in rest
        date = None
        if lead and not already_archived:
            dm = re.search(r"(\d{4}-\d{2}-\d{2})", lead)
            if dm:
                try:
                    date = datetime.date.fromisoformat(dm.group(1))
                except ValueError:
                    date = None
        idm = re.match(r"^\| \*\*(A\d+)", line)
        rows.append({
            "id": idm.group(1) if idm else None,
            "lead": lead,
            "date": date,
            "row_start": row_start,
            "row_end": row_end,
        })
    return rows


def plan_rotation(text: str, cutoff: datetime.date):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_blocks_newest_first). A row with no resolvable date is kept
    live, never guessed into the archive.
    """
    start, end = find_section2(text)
    if start is None:
        return text, []
    rows = find_rows(text, start, end)
    archived = [r for r in rows if r["date"] is not None and r["date"] < cutoff]
    if not archived:
        return text, []
    archive_starts = {r["row_start"] for r in archived}
    pieces = []
    pos = 0
    for r in rows:
        if r["row_start"] in archive_starts:
            pieces.append(text[pos:r["row_start"]])
            pointer_line = "| **%s** %s |\n" % (r["lead"], ARCHIVED_MARKER)
            pieces.append(pointer_line)
            pos = r["row_end"]
    pieces.append(text[pos:])
    new_text = "".join(pieces)
    archived_sorted = sorted(archived, key=lambda r: r["date"], reverse=True)
    archived_blocks = []
    for r in archived_sorted:
        block = text[r["row_start"]:r["row_end"]].rstrip("\n") + "\n"
        archived_blocks.append(block)
    return new_text, archived_blocks


def apply_archive(archived_blocks, existing_archive_text):
    """Build the new archive file text: the fixed header, then the newly
    archived blocks (already newest first), then whatever the archive
    already held, same prepend-above-existing convention this file's
    sibling rotate_*.py tools use.
    """
    new_chunk = "\n".join(archived_blocks)
    if existing_archive_text:
        if not existing_archive_text.startswith(ARCHIVE_HEADER):
            raise ValueError("%s does not start with the expected header; "
                              "refusing to guess." % ARCHIVE_PATH)
        old_body = existing_archive_text[len(ARCHIVE_HEADER):].lstrip("\n")
    else:
        old_body = ""
    body = new_chunk if not old_body else new_chunk + "\n" + old_body
    if not body.endswith("\n"):
        body += "\n"
    return ARCHIVE_HEADER + "\n" + body


def count_stats(text: str, cutoff: datetime.date):
    """Return (n_rows, overdue, n_bytes, overdue_bytes) for section 2's
    dated journal rows, for use by the paired preflight gate. `n_rows`
    counts only rows with a resolvable date (A1-A6's dateless pointers
    are not part of either count)."""
    start, end = find_section2(text)
    if start is None:
        return 0, 0, 0, 0
    rows = [r for r in find_rows(text, start, end) if r["date"] is not None]
    n_rows = len(rows)
    n_bytes = sum(r["row_end"] - r["row_start"] for r in rows)
    overdue_rows = [r for r in rows if r["date"] < cutoff]
    overdue = len(overdue_rows)
    overdue_bytes = sum(r["row_end"] - r["row_start"] for r in overdue_rows)
    return n_rows, overdue, n_bytes, overdue_bytes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--days", type=int, default=DEFAULT_RETENTION_DAYS)
    args = parser.parse_args()

    if not args.check and not args.apply:
        args.check = True

    with io.open(BACKLOG_PATH, encoding="utf-8") as f:
        text = f.read()

    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    new_text, archived_blocks = plan_rotation(text, cutoff)

    if not archived_blocks:
        print("CLEAN: all section-2 journal rows with a resolvable date "
              "are within the %d-day retention window (cutoff %s). "
              "Nothing to rotate." % (args.days, cutoff.isoformat()))
        return 0

    total_bytes = sum(len(b.encode("utf-8")) for b in archived_blocks)
    if args.apply:
        existing_archive_text = ""
        if os.path.exists(ARCHIVE_PATH):
            with io.open(ARCHIVE_PATH, encoding="utf-8") as f:
                existing_archive_text = f.read()
        new_archive_text = apply_archive(archived_blocks, existing_archive_text)
        with io.open(ARCHIVE_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_archive_text)
        with io.open(BACKLOG_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        print("Moved %d rows (%d bytes) to %s. Live file shrank from %d to "
              "%d bytes." % (len(archived_blocks), total_bytes, ARCHIVE_PATH,
                              len(text.encode("utf-8")),
                              len(new_text.encode("utf-8"))))
    else:
        print("DUE: %d rows (%d bytes) are older than %s (retention %d "
              "days) and would move to %s on --apply." %
              (len(archived_blocks), total_bytes, cutoff.isoformat(),
               args.days, ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
