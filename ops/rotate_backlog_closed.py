#!/usr/bin/env python3
"""Move old "## N. Closed/Done ..." narrative sections out of
BACKLOG-2026-09-07.md into BACKLOG-2026-09-07-CLOSED-ARCHIVE.md.

ops/rotate_backlog.py already rotates section 1's flat "Done this week"
table and deliberately left sections 8 and up out of scope: its own
docstring calls that "a different, higher-risk job" because sections 2-4
mix open and closed rows under their own per-item ids (B9, D5, ...).
Sections 8+ are not that: each is a whole closed backlog item recorded as
its own numbered section, one per closed item, oldest first ("## 8. Closed
2026-10-11: ..." through "## 33. Closed 2026-10-23: ..." as of this
writing), and a repository-wide grep found nothing else that references
any of these section numbers by name, so a whole section can be lifted
out safely, the same way a NIGHTLY-LOG.md entry can.

Found 2026-10-23, the same cold-read lane that fixed NIGHTLY-LOG.md,
STATUS.md (twice), CHECKIN-LOG.md, OWNER-ACTIONS.md and this file's own
"Done this week" table for the identical shape earlier the same day:
sections 8-33 already account for 105KB of this file's 304KB, and STEP 1
of the operating prompt reads the whole file every cycle as "the CURRENT
queue... your work list". Nothing is yet far enough past the retention
window to be due (checked with --check, not assumed), so this adds the
tool and the gate before the gap is actually costing cycles, rather than
after, the way every rotation before it had to.

Nothing here deletes a word. Sections move verbatim into
BACKLOG-2026-09-07-CLOSED-ARCHIVE.md, newest first, the same convention
this file's sibling archives (BACKLOG-2026-09-07-ARCHIVE.md, STATUS-
ARCHIVE.md) already use.

Usage:
    python ops/rotate_backlog_closed.py --check
    python ops/rotate_backlog_closed.py --check --days N
    python ops/rotate_backlog_closed.py --apply   (default 4-day window)
    python ops/rotate_backlog_closed.py --apply --days N

Found 2026-10-31: at the closure rate the operator cadence has actually
produced (51 numbered sections in the 14 days before this edit, about
4300 bytes each), the 14-day default alone settles near 213KB of closed
sections, which combined with the file's other live content pushes the
whole file well past gate_living_docs_total_size_tripwire's 150,000-byte
ceiling even with nothing overdue by gate_backlog_closed_sections_not_
oversized's own (14+7)-day buffer. Lowered to 4 days, which leaves the
file under the tripwire with a few days' buffer; the archive keeps every
word, so this only changes how long a closed section stays in the file
STEP 1 of the operating prompt reads as "the CURRENT queue" before a
cold read has to open BACKLOG-2026-09-07-CLOSED-ARCHIVE.md instead.
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-CLOSED-ARCHIVE.md")

# Sections 2-7 mix open and closed rows under their own per-item ids;
# out of scope here, the same boundary ops/rotate_backlog.py's own
# docstring already drew for the same reason.
MIN_SECTION_NUM = 8

ARCHIVE_HEADER_FIRST_LINE = "# BACKLOG-2026-09-07.md closed-section archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Numbered \"## N. Closed/Done ...\" sections older than ops/rotate_"
    "backlog_closed.py's retention window, moved here verbatim from "
    "BACKLOG-2026-09-07.md by that script. Never hand-edited. Newest "
    "first.\n"
)

DEFAULT_RETENTION_DAYS = 4

SECTION_RE = re.compile(r"^## (\d+)\.", re.MULTILINE)


def find_sections(text: str):
    """Return a list of dicts, one per numbered '## N. ...' heading with
    N >= MIN_SECTION_NUM, in file order: {num, date, start, end, block}.
    `end` is the start of the next '## ' heading of any number, or
    len(text) for the last one; `block` is text[start:end]. `date` is the
    first YYYY-MM-DD found on the heading's own line (its one reliably
    dated token; the body below routinely cites unrelated dates), or
    None if that heading names no date, kept live rather than guessed.
    """
    starts = list(SECTION_RE.finditer(text))
    sections = []
    for i, m in enumerate(starts):
        num = int(m.group(1))
        if num < MIN_SECTION_NUM:
            continue
        start = m.start()
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        nl = text.find("\n", start)
        heading_line = text[start:nl if nl != -1 else len(text)]
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", heading_line)
        date = None
        if dm:
            try:
                date = datetime.date.fromisoformat(dm.group(1))
            except ValueError:
                date = None
        sections.append({"num": num, "date": date, "start": start,
                          "end": end, "block": text[start:end]})
    return sections


def plan_rotation(text: str, cutoff: datetime.date):
    """Pure function of its inputs; does no I/O. Returns (new_text,
    archived_blocks_newest_first). A section with no resolvable date is
    kept live, never guessed into the archive.
    """
    sections = find_sections(text)
    archived = [s for s in sections
                if s["date"] is not None and s["date"] < cutoff]
    if not archived:
        return text, []
    archive_starts = {s["start"] for s in archived}
    pieces = []
    pos = 0
    for s in sections:
        if s["start"] in archive_starts:
            pieces.append(text[pos:s["start"]])
            pos = s["end"]
    pieces.append(text[pos:])
    new_text = "".join(pieces)
    archived_sorted = sorted(
        archived, key=lambda s: (s["date"], s["num"]), reverse=True)
    archived_blocks = [s["block"].rstrip("\n") + "\n" for s in archived_sorted]
    return new_text, archived_blocks


def apply_archive(archived_blocks, existing_archive_text):
    """Build the new archive file text: the fixed header, then the newly
    archived blocks (already newest first), then whatever the archive
    already held. New material goes on top, same prepend-above-existing
    convention ops/rotate_nightly_log.py and ops/rotate_backlog.py use,
    so repeat runs keep extending one growing archive.
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
    """Returns (n_sections, n_overdue, n_bytes, overdue_bytes).

    n_bytes is every numbered section's size, the live corpus total.
    overdue_bytes is only the sections --apply would actually move. The
    two were collapsed into one `n_bytes` until found 2026-10-26: --check
    printed overdue_bytes's value as n_bytes's own ("1 of 41 numbered
    sections (180769 bytes) are older than ... and would move ... on
    --apply"), so a 2888-byte rotation read as a 180769-byte one, the
    entire corpus's size misquoted as the one overdue section's size.
    """
    sections = find_sections(text)
    overdue = [s for s in sections
               if s["date"] is not None and s["date"] < cutoff]
    n_bytes = sum(len(s["block"].encode("utf-8")) for s in sections)
    overdue_bytes = sum(len(s["block"].encode("utf-8")) for s in overdue)
    return len(sections), len(overdue), n_bytes, overdue_bytes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="Report current size and whether rotation is "
                          "due; makes no changes.")
    ap.add_argument("--apply", action="store_true",
                     help="Rotate now: move sections older than --days "
                          "into the archive.")
    ap.add_argument("--days", type=int, default=DEFAULT_RETENTION_DAYS,
                     help="Retention window in days (default %d)."
                          % DEFAULT_RETENTION_DAYS)
    args = ap.parse_args()
    if not args.check and not args.apply:
        ap.error("pass --check or --apply")

    text = io.open(BACKLOG_PATH, encoding="utf-8").read()
    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    n_sections, overdue, n_bytes, overdue_bytes = count_stats(text, cutoff)

    if args.check:
        if overdue:
            print("DUE: %d of %d numbered sections (%d bytes total live) "
                  "are older than %s (retention %d days); %d bytes would "
                  "move to %s on --apply."
                  % (overdue, n_sections, n_bytes, cutoff.isoformat(),
                     args.days, overdue_bytes, ARCHIVE_PATH))
            return 1
        print("CLEAN: all %d numbered sections (%d bytes) are within the "
              "%d-day retention window (cutoff %s). Nothing to rotate."
              % (n_sections, n_bytes, args.days, cutoff.isoformat()))
        return 0

    # --apply
    new_text, archived_blocks = plan_rotation(text, cutoff)
    if not archived_blocks:
        print("Nothing older than %s (retention %d days); no change made."
              % (cutoff.isoformat(), args.days))
        return 0

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived_blocks, existing_archive_text)

    # Write-then-rename both files, archive first: if the process dies
    # between the two writes, the worst case is a section that exists in
    # both the (unrotated) live file and the archive, never one that
    # exists in neither.
    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    backlog_tmp = BACKLOG_PATH + ".tmp"
    io.open(backlog_tmp, "w", encoding="utf-8").write(new_text)
    os.replace(backlog_tmp, BACKLOG_PATH)

    new_n_sections, _, new_n_bytes, _ = count_stats(new_text, cutoff)
    print("Moved %d sections to %s. Live file now carries %d numbered "
          "sections (%d bytes); was %d sections, %d bytes."
          % (len(archived_blocks), ARCHIVE_PATH, new_n_sections,
             new_n_bytes, n_sections, n_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
