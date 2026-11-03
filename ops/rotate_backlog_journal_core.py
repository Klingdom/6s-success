#!/usr/bin/env python3
"""Shared logic for archiving old free-form journal rows out of
BACKLOG-2026-09-07.md sections 3 and 4, where ops/rotate_backlog_
section2_items.py's own docstring explicitly deferred: ids repeat
within a section (B4 and B8 each appear twice, C6/C7 interleave across
several rows), and rotate_backlog_done_items.py's docstring already
warned that "a generic find a line starting with **ID parser would
silently archive the wrong text... or the right text under the wrong
byline."

Found 2026-11-03, scheduled operator cycle, picking up the standing
handoff two prior PM check-ins named as real but "not urgent enough for
this slot": checked the actual byte shape of sections 3 and 4 directly
rather than assume section 2's row shape carries over. It does not,
fully. Two things differ:

1. Several rows are bare bold paragraphs with no leading pipe at all
   ("**B1 follow-on, found and fixed 2026-09-08...**", not inside the
   markdown table), interleaved with ordinary `| **ID** | ...` table
   rows. A parser that only matches `^\\| \\*\\*` misses these entirely.
2. The real misattribution hazard rotate_backlog_done_items.py warned
   about is concrete, not hypothetical: two un-id'd "Corrected 2026-10-
   14" paragraphs near the end of section 4 sit physically after the
   "C7 fourth-wave" row (dated 2026-10-27) but actually amend the
   different, earlier "C7 second wave" entry (dated 2026-10-09).
   Section 2's rule ("archive from one matched row up to the next") is
   safe there because that section's rows sit back-to-back with no
   orphan continuation text between them; it is NOT safe here.

This module's rule is therefore narrower than section 2's: archive ONLY
a matched row's own single physical line (id, date, byline and
narrative, confirmed by direct scan to be one line each, never more).
Never touch anything after that row's own trailing newline, no matter
what it is: blank line, "---" divider, or a substantial orphan
paragraph. Whatever follows stays live, unchanged, every time, so the
byline-misattribution hazard above is structurally impossible rather
than merely checked for. The cost is that an un-id'd orphan paragraph is
never itself rotated by this tool; that is the correct, conservative
answer, not a gap to close later by guessing which row it belongs to.

A row with no resolvable date (an already-struck pointer from
rotate_backlog_done_items.py, a live Phil-gated item with no date in
its own lead, or a row this module has already rotated, whose pointer
keeps the original lead sentence, date and all, for a human skimming
the table) is recognised by its own ARCHIVED_MARKER text and/or its
lack of a date, and is left live, never guessed into the archive.
"""
import datetime
import os
import re


def find_section(text: str, start_re: str, end_re: str):
    """Return (start, end) of the section's span in `text`, end
    exclusive (the start of the next named section, or len(text) if it
    is not found, kept live rather than guessed)."""
    m = re.search(start_re, text, re.M)
    if not m:
        return None, None
    start = m.start()
    nm = re.search(end_re, text[m.end():], re.M)
    end = m.end() + nm.start() if nm else len(text)
    return start, end


def find_rows(text: str, start: int, end: int, id_pattern: str,
              archived_marker: str):
    """Return a list of dicts, one per matched row within [start, end):
    {piped, lead, date, row_start, row_line_end, advance_to}.

    A row is `^\\| \\*\\*<id>` (an ordinary table row) or `^\\*\\*<id>`
    (a bare bold paragraph, no leading pipe); `piped` records which.
    `lead` is the row's own leading bold span (between the first pair of
    `**` on its own line); `date` is the first YYYY-MM-DD found in
    `lead`, or None if the row names no date or already carries this
    module's own ARCHIVED_MARKER (already rotated; its lead keeps the
    original date for a human skimming the table, so it is excluded by
    marker rather than re-derived). `row_line_end` is the row's own
    single physical line, exclusive of its trailing newline;
    `advance_to` is the position right after that newline, which is as
    far as this module will ever touch, regardless of what follows.
    """
    row_re = re.compile(r"(?m)^(\| )?\*\*(%s)" % id_pattern)
    rows = []
    for m in row_re.finditer(text, start, end):
        row_start = m.start()
        piped = m.group(1) is not None
        nl = text.find("\n", row_start, end)
        line_end = nl if nl != -1 else end
        line = text[row_start:line_end]
        bm = re.match(r"^(?:\| )?\*\*(.*?)\*\*(.*)$", line)
        lead = bm.group(1) if bm else None
        rest = bm.group(2) if bm else ""
        already_archived = bool(lead) and archived_marker in rest
        date = None
        if lead and not already_archived:
            dm = re.search(r"(\d{4}-\d{2}-\d{2})", lead)
            if dm:
                try:
                    date = datetime.date.fromisoformat(dm.group(1))
                except ValueError:
                    date = None
        rows.append({
            "piped": piped,
            "lead": lead,
            "date": date,
            "row_start": row_start,
            "row_line_end": line_end,
            "advance_to": (line_end + 1) if nl != -1 else end,
        })
    return rows


def plan_rotation(text: str, start_re: str, end_re: str, id_pattern: str,
                   archived_marker: str, cutoff: datetime.date):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_blocks_newest_first). A row with no resolvable date is kept
    live, never guessed into the archive. Only a matched row's own
    single line is ever removed from `text`; everything after its own
    newline is left exactly as it was.
    """
    start, end = find_section(text, start_re, end_re)
    if start is None:
        return text, []
    rows = find_rows(text, start, end, id_pattern, archived_marker)
    archived = [r for r in rows if r["date"] is not None and r["date"] < cutoff]
    if not archived:
        return text, []
    archive_starts = {r["row_start"] for r in archived}
    pieces = []
    pos = 0
    for r in rows:
        if r["row_start"] in archive_starts:
            pieces.append(text[pos:r["row_start"]])
            if r["piped"]:
                pointer = "| **%s** %s |\n" % (r["lead"], archived_marker)
            else:
                pointer = "**%s** %s\n" % (r["lead"], archived_marker)
            pieces.append(pointer)
            pos = r["advance_to"]
    pieces.append(text[pos:])
    new_text = "".join(pieces)
    archived_sorted = sorted(archived, key=lambda r: r["date"], reverse=True)
    archived_blocks = []
    for r in archived_sorted:
        block = text[r["row_start"]:r["row_line_end"]].rstrip("\n") + "\n"
        archived_blocks.append(block)
    return new_text, archived_blocks


def apply_archive(archive_path: str, archive_header: str, archived_blocks):
    """Build the new archive file text: the fixed header, then the
    newly archived blocks (already newest first), then whatever the
    archive already held, same prepend-above-existing convention this
    file's sibling rotate_*.py tools use."""
    existing_text = ""
    if os.path.exists(archive_path):
        with open(archive_path, encoding="utf-8") as f:
            existing_text = f.read()
    new_chunk = "\n".join(archived_blocks)
    if existing_text:
        if not existing_text.startswith(archive_header):
            raise ValueError("%s does not start with the expected header; "
                              "refusing to guess." % archive_path)
        old_body = existing_text[len(archive_header):].lstrip("\n")
    else:
        old_body = ""
    body = new_chunk if not old_body else new_chunk + "\n" + old_body
    if not body.endswith("\n"):
        body += "\n"
    return archive_header + "\n" + body


def count_stats(text: str, start_re: str, end_re: str, id_pattern: str,
                 archived_marker: str, cutoff: datetime.date):
    """Return (n_rows, overdue, n_bytes, overdue_bytes) for this
    section's dated journal rows, for use by the paired preflight gate.
    `n_rows` counts only rows with a resolvable date (dateless pointers
    and live Phil-gated rows are not part of either count)."""
    start, end = find_section(text, start_re, end_re)
    if start is None:
        return 0, 0, 0, 0
    rows = [r for r in find_rows(text, start, end, id_pattern, archived_marker)
            if r["date"] is not None]
    n_rows = len(rows)
    n_bytes = sum(r["row_line_end"] - r["row_start"] for r in rows)
    overdue_rows = [r for r in rows if r["date"] < cutoff]
    overdue = len(overdue_rows)
    overdue_bytes = sum(r["row_line_end"] - r["row_start"] for r in overdue_rows)
    return n_rows, overdue, n_bytes, overdue_bytes
