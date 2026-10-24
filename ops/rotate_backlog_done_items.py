#!/usr/bin/env python3
"""Archive the trailing narrative of BACKLOG-2026-09-07.md's done,
struck-through item rows in sections 2-4, leaving a one-line pointer.

ops/rotate_backlog.py and ops/rotate_backlog_closed.py both explicitly
leave sections 2-4 out of scope, calling it "a different, higher-risk
job" because those sections mix open and closed rows under free-form,
reused per-item ids. That reuse is real: "B4" the original table row is
a different thing from "B4 follow-on, found and fixed 2026-09-08..." a
later, unrelated note sharing the same prefix, and "C6/C7 adjacent,
thumbnail font defect..." reuses two ids in one journal entry. A generic
"find a line starting with **ID" parser would silently archive the
wrong text on that shape, or the right text under the wrong byline.

Found 2026-10-24, scheduled operator cycle, picking up the standing
handoff (sections 2-4 of this file still carry ~24KB of done-item
narrative, named by several prior cycles as real but out of scope for
every existing rotate_*.py): the only rows this file formats
UNAMBIGUOUSLY are the original, dated-2026-09-07/08 table rows whose
Item cell is itself wrapped in strikethrough immediately after the id,
`| **ID** | ~~...~~ | `. Exactly 17 of them exist (A1-A6, B1-B4, B6, B8,
B9, C1-C3, C7), confirmed by direct regex scan, none colliding with a
later free-form "ID, ..." journal row sharing the same letter+digit
prefix (that shape always has a comma right after the id, never `**ID**
| ~~`). This script touches only those 17, by a hardcoded whitelist, and
refuses if any whitelisted id's row does not match that exact shape
rather than guess. Every "ID, ..." journal-style row (A7 onward, B5/B7,
C4-C6's later notes) is left untouched: classifying those safely is the
larger job the sibling tools already deferred, and this script does not
attempt it.

Nothing is deleted. Each row's trailing cell(s) (everything after the
struck-through Item) move verbatim into BACKLOG-2026-09-07-ITEMS-
ARCHIVE.md, in file order, and the live row shrinks to id + struck title
+ a one-sentence pointer, the same convention BACKLOG-2026-09-07-B9-
ARCHIVE.md already set for this file's single largest row (B9's own
remaining ~3.2KB live cell was never covered by that one-off fix; this
script finishes it).

Usage:
    python ops/rotate_backlog_done_items.py --check
    python ops/rotate_backlog_done_items.py --apply
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-ITEMS-ARCHIVE.md")

SECTION_START = "## 2."
SECTION_END = "## 5."

# The only ids whose row this script will ever touch. Found by direct
# scan for `^\| \*\*ID\*\* \| ~~`, confirmed unique (one matching line
# each) within the sections-2-4 span as of 2026-10-24.
ROW_IDS = [
    "A1", "A2", "A3", "A4", "A5", "A6",
    "B1", "B2", "B3", "B4", "B6", "B8", "B9",
    "C1", "C2", "C3", "C7",
]

ROW_RE_TEMPLATE = r'^\| \*\*(%s)\*\* \| (~~.*?~~) \| (.*)$'

ARCHIVE_HEADER_FIRST_LINE = "# BACKLOG-2026-09-07.md done-item archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "The trailing narrative of sections 2-4's done, struck-through item "
    "rows, moved here verbatim from BACKLOG-2026-09-07.md by "
    "ops/rotate_backlog_done_items.py. Never hand-edited. One entry per "
    "id, in the order the live file listed them the day each was "
    "archived.\n"
)

ARCHIVED_MARKER = "Archived; see `BACKLOG-2026-09-07-ITEMS-ARCHIVE.md`."
POINTER_SUFFIX = " | %s |" % ARCHIVED_MARKER


def _section_span(text):
    start = text.find(SECTION_START)
    if start == -1:
        raise SystemExit("refusing: %r heading not found" % SECTION_START)
    end = text.find(SECTION_END, start)
    if end == -1:
        raise SystemExit("refusing: %r heading not found after section 2"
                          % SECTION_END)
    return start, end


def find_rows(text):
    """Return {id: (line_start, line_end, item_cell, rest_cell)} for
    every ROW_IDS entry whose unambiguous row is still live (i.e. not
    already rotated to the pointer form) within the sections-2-4 span.
    Raises if a whitelisted id's row exists but does not match the
    expected shape, or if more than one match is found.
    """
    sec_start, sec_end = _section_span(text)
    found = {}
    for rid in ROW_IDS:
        pat = re.compile(ROW_RE_TEMPLATE % re.escape(rid), re.MULTILINE)
        matches = [m for m in pat.finditer(text)
                   if sec_start <= m.start() < sec_end]
        if not matches:
            continue
        if len(matches) > 1:
            raise SystemExit(
                "refusing: %s matches %d rows in sections 2-4, expected "
                "at most 1" % (rid, len(matches)))
        m = matches[0]
        rest = m.group(3)
        if rest.strip().rstrip("|").strip() == ARCHIVED_MARKER:
            continue  # already rotated
        found[rid] = (m.start(), m.end(), m.group(2), rest)
    return found


def plan_rotation(text):
    """Pure function of its input. Returns (new_text, archived_entries)
    where archived_entries is a list of (id, item_cell, rest_cell) in
    file order. Empty list means nothing to do.
    """
    rows = find_rows(text)
    if not rows:
        return text, []
    ordered_ids = [rid for rid in ROW_IDS if rid in rows]
    pieces = []
    pos = 0
    archived = []
    # Replace in file order (rows dict values carry start offsets).
    by_start = sorted(rows.items(), key=lambda kv: kv[1][0])
    for rid, (start, end, item_cell, rest_cell) in by_start:
        pieces.append(text[pos:start])
        pieces.append("| **%s** | %s%s" % (rid, item_cell, POINTER_SUFFIX))
        pos = end
        archived.append((rid, item_cell, rest_cell))
    pieces.append(text[pos:])
    new_text = "".join(pieces)
    # Return archived entries in file order too (not pos-sorted twice).
    archived_by_id = {rid: (rid, item, rest) for rid, item, rest in archived}
    archived_ordered = [archived_by_id[rid] for rid in ordered_ids]
    return new_text, archived_ordered


def format_archive_entries(entries):
    blocks = []
    for rid, item_cell, rest_cell in entries:
        blocks.append("### %s\n\n| **%s** | %s | %s\n" % (
            rid, rid, item_cell, rest_cell))
    return "\n".join(blocks)


def apply_archive(entries, existing_archive_text):
    new_chunk = format_archive_entries(entries)
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


def count_stats(text):
    rows = find_rows(text)
    n_bytes = sum(len(("| **%s** | %s | %s" % (rid, item, rest))
                       .encode("utf-8"))
                  for rid, (_, _, item, rest) in rows.items())
    return len(rows), n_bytes


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = io.open(BACKLOG_PATH, encoding="utf-8").read()
    n_rows, n_bytes = count_stats(text)

    if args.check:
        if n_rows == 0:
            print("CLEAN: no unarchived done-item rows left in sections "
                  "2-4 among the %d tracked ids. Nothing to rotate."
                  % len(ROW_IDS))
            return
        print("%d of %d tracked done-item rows still carry live "
              "narrative (%d bytes). Run --apply to move them to %s."
              % (n_rows, len(ROW_IDS), n_bytes, ARCHIVE_PATH))
        return

    new_text, archived = plan_rotation(text)
    if not archived:
        print("CLEAN: nothing to rotate.")
        return

    existing_archive = ""
    if os.path.exists(ARCHIVE_PATH):
        existing_archive = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive = apply_archive(archived, existing_archive)

    with io.open(BACKLOG_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    with io.open(ARCHIVE_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_archive)

    print("Rotated %d rows (%d bytes) out of BACKLOG-2026-09-07.md into "
          "%s: %s" % (len(archived), n_bytes, ARCHIVE_PATH,
                       ", ".join(rid for rid, _, _ in archived)))


if __name__ == "__main__":
    main()
