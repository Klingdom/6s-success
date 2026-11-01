#!/usr/bin/env python3
"""Archive old resolved/done/closed paragraph groups out of
BACKLOG-2026-09-07.md section 1b, "Measured this week, awaiting a
decision".

Found 2026-11-01, scheduled operator cycle: gate_living_docs_total_size_
tripwire flagged BACKLOG-2026-09-07.md at 167,753 bytes against its
150,000-byte ceiling, after rotate_backlog.py, rotate_backlog_closed.py
and rotate_backlog_section2_items.py were all already run clean the same
cycle. Section 1b alone was 12,106 bytes, every paragraph in it already
RESOLVED, Done or CLOSED (dated 2026-09-15 through 2026-10-14, all more
than two weeks old), and no rotation tool covered it: ops/rotate_
backlog.py's docstring only ever claimed section 1's flat table, ops/
rotate_backlog_section2_items.py only section 2's `| **A<N>` rows. This
is the same unbounded-growth shape, just a third section and a third
paragraph shape (free prose, not a table row), so it gets the same
rotate_*.py/gate_*_not_oversized treatment rather than a one-off hand
edit that leaves the next "awaiting a decision" item with nowhere to
land once it, too, gets resolved.

Section 1b's prose does not use section 2's one-row-per-item shape.
A single topic can run across several bold-led paragraphs (the
basement/attic item is five: a RESOLVED summary, then "why", "the
honest counter-argument" and "checked and not escalated", none of the
last three carrying their own date). Splitting strictly on dated
paragraphs would cut a topic's reasoning away from its own conclusion.
Instead this groups paragraphs: a paragraph whose own bold lead carries
a resolvable YYYY-MM-DD date starts a new group and sets that group's
date; a paragraph with no date in its lead is a continuation of
whichever group is currently open, carried with it either way. A
paragraph already carrying ARCHIVED_MARKER is a fixed, already-rotated
pointer: it is never grouped, never re-dated, never re-archived, and it
closes whatever group was open before it (a pointer cannot be a
continuation target).

Only a group whose date is older than the retention window moves.
Nothing is deleted: the whole group (every paragraph in it, verbatim)
moves into BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md, newest group first,
and the live file keeps a single pointer paragraph built from the
group's own first bold lead, the same convention ops/rotate_backlog_
section2_items.py already uses for its own rows.

Usage:
    python ops/rotate_backlog_section1b_items.py --check
    python ops/rotate_backlog_section1b_items.py --check --days N
    python ops/rotate_backlog_section1b_items.py --apply   (default 14-day window)
    python ops/rotate_backlog_section1b_items.py --apply --days N
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md")

DEFAULT_RETENTION_DAYS = 14

SECTION_START_RE = re.compile(r"(?m)^## 1b\. Measured this week, awaiting a decision")
NEXT_SECTION_RE = re.compile(r"(?m)^## 2\. ")
PARA_START_RE = re.compile(r"(?m)^\*\*")

ARCHIVE_HEADER_FIRST_LINE = "# BACKLOG-2026-09-07.md section 1b archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Resolved/Done/Closed paragraph groups older than ops/rotate_"
    "backlog_section1b_items.py's retention window, moved here verbatim "
    "from BACKLOG-2026-09-07.md section 1b by that script. Never hand-"
    "edited. Newest group first.\n"
)

ARCHIVED_MARKER = "Archived; see `BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md`."


def find_section1b(text: str):
    """Return (start, end) of section 1b's span in `text`, end exclusive
    (the start of section 2, or len(text) if section 2 is not found,
    kept live rather than guessed)."""
    m = SECTION_START_RE.search(text)
    if not m:
        return None, None
    start = m.start()
    nm = NEXT_SECTION_RE.search(text, m.end())
    end = nm.start() if nm else len(text)
    return start, end


def find_paragraphs(text: str, start: int, end: int):
    """Return a list of dicts, one per bold-led paragraph in [start,
    end): {lead, date, archived, para_start, para_end}. `lead` is the
    text of the paragraph's own leading bold span, or None if the
    paragraph has no closing `**` on its own starting line (kept out of
    grouping, never guessed). `date` is the first YYYY-MM-DD found in
    `lead`, or None. `archived` is True if the paragraph already carries
    ARCHIVED_MARKER anywhere in it (a fixed pointer, never re-grouped).
    """
    starts = [m.start() for m in PARA_START_RE.finditer(text, start, end)]
    paras = []
    for i, para_start in enumerate(starts):
        para_end = starts[i + 1] if i + 1 < len(starts) else end
        para_text = text[para_start:para_end]
        bm = re.match(r"^\*\*(.*?)\*\*", para_text, re.DOTALL)
        lead = bm.group(1) if bm else None
        archived = ARCHIVED_MARKER in para_text
        date = None
        if lead and not archived:
            dm = re.search(r"(\d{4}-\d{2}-\d{2})", lead)
            if dm:
                try:
                    date = datetime.date.fromisoformat(dm.group(1))
                except ValueError:
                    date = None
        paras.append({
            "lead": lead,
            "date": date,
            "archived": archived,
            "para_start": para_start,
            "para_end": para_end,
        })
    return paras


def group_paragraphs(paras):
    """Group paragraphs into a list of dicts: {date, paras}. A dated
    paragraph starts a new group; an undated, non-archived paragraph
    joins the currently open group (or is left ungrouped, kept live,
    if nothing is open yet). An archived pointer paragraph is always
    its own standalone, already-settled group and closes whatever was
    open before it."""
    groups = []
    current = None
    for p in paras:
        if p["archived"]:
            if current is not None:
                groups.append(current)
                current = None
            groups.append({"date": None, "paras": [p], "fixed": True})
        elif p["date"] is not None:
            if current is not None:
                groups.append(current)
            current = {"date": p["date"], "paras": [p], "fixed": False}
        else:
            if current is not None:
                current["paras"].append(p)
            else:
                groups.append({"date": None, "paras": [p], "fixed": False})
    if current is not None:
        groups.append(current)
    return groups


def plan_rotation(text: str, cutoff: datetime.date):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_blocks_newest_first). A group with no resolvable date, or
    a date not yet past the cutoff, is kept live, never guessed into
    the archive."""
    start, end = find_section1b(text)
    if start is None:
        return text, []
    paras = find_paragraphs(text, start, end)
    groups = group_paragraphs(paras)
    due = [g for g in groups if (not g["fixed"]) and g["date"] is not None
           and g["date"] < cutoff]
    if not due:
        return text, []
    due_para_starts = {p["para_start"] for g in due for p in g["paras"]}
    pieces = []
    pos = 0
    for g in groups:
        g_paras = g["paras"]
        if g_paras[0]["para_start"] in due_para_starts:
            pieces.append(text[pos:g_paras[0]["para_start"]])
            pointer_line = "**%s** %s\n\n" % (g_paras[0]["lead"], ARCHIVED_MARKER)
            pieces.append(pointer_line)
            pos = g_paras[-1]["para_end"]
    pieces.append(text[pos:])
    new_text = "".join(pieces)
    due_sorted = sorted(due, key=lambda g: g["date"], reverse=True)
    archived_blocks = []
    for g in due_sorted:
        block_start = g["paras"][0]["para_start"]
        block_end = g["paras"][-1]["para_end"]
        block = text[block_start:block_end].rstrip("\n") + "\n"
        archived_blocks.append(block)
    return new_text, archived_blocks


def apply_archive(archived_blocks, existing_archive_text):
    """Build the new archive file text: the fixed header, then the
    newly archived blocks (already newest first), then whatever the
    archive already held, same prepend-above-existing convention this
    file's sibling rotate_*.py tools use."""
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
    """Return (n_groups, overdue, n_bytes, overdue_bytes) for section
    1b's dated, non-fixed paragraph groups, for use by the paired
    preflight gate."""
    start, end = find_section1b(text)
    if start is None:
        return 0, 0, 0, 0
    paras = find_paragraphs(text, start, end)
    groups = [g for g in group_paragraphs(paras)
              if (not g["fixed"]) and g["date"] is not None]
    n_groups = len(groups)
    n_bytes = sum(g["paras"][-1]["para_end"] - g["paras"][0]["para_start"]
                  for g in groups)
    overdue_groups = [g for g in groups if g["date"] < cutoff]
    overdue = len(overdue_groups)
    overdue_bytes = sum(g["paras"][-1]["para_end"] - g["paras"][0]["para_start"]
                         for g in overdue_groups)
    return n_groups, overdue, n_bytes, overdue_bytes


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
        print("CLEAN: all section-1b paragraph groups with a resolvable "
              "date are within the %d-day retention window (cutoff %s). "
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
        print("Moved %d groups (%d bytes) to %s. Live file shrank from %d "
              "to %d bytes." % (len(archived_blocks), total_bytes, ARCHIVE_PATH,
                                 len(text.encode("utf-8")),
                                 len(new_text.encode("utf-8"))))
    else:
        print("DUE: %d groups (%d bytes) are older than %s (retention %d "
              "days) and would move to %s on --apply." %
              (len(archived_blocks), total_bytes, cutoff.isoformat(),
               args.days, ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
