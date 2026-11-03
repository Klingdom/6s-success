#!/usr/bin/env python3
"""Archive old free-form journal rows (B1 follow-on onward) out of
BACKLOG-2026-09-07.md section 3, "Now: decks".

See ops/rotate_backlog_journal_core.py's own docstring for the full
account of why this needed its own module rather than reusing ops/
rotate_backlog_section2_items.py directly: section 3 mixes ordinary
`| **ID** | ...` table rows with bare bold paragraphs that have no
leading pipe at all ("**B1 follow-on, found and fixed 2026-09-08...**"),
and ids repeat (B4 and B8 each appear twice: once as the original
struck table row rotate_backlog_done_items.py already archived, once as
a later, unrelated free-form note sharing the same prefix). This
module's core only ever removes a matched row's own single physical
line, never anything after it, so that reuse cannot cause one row's
narrative to be filed under a different row's byline.

Confirmed by direct scan, not assumed: every one of section 3's B1-B9
free-form journal rows is exactly one physical line, and every gap
between a row's own line and the next matched row is either empty or
pure whitespace/a "---" divider. Nothing in section 3 today has the
substantial-orphan-paragraph shape section 4 does; this module's
per-line safety rule holds regardless, so that remains true by
construction rather than by this observation alone.

Usage:
    python ops/rotate_backlog_section3_items.py --check
    python ops/rotate_backlog_section3_items.py --check --days N
    python ops/rotate_backlog_section3_items.py --apply   (default 14-day window)
    python ops/rotate_backlog_section3_items.py --apply --days N
"""
import argparse
import datetime
import io
import os
import sys

import rotate_backlog_journal_core as core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-SECTION3-ARCHIVE.md")

DEFAULT_RETENTION_DAYS = 14

START_RE = r"^## 3\. Now: decks"
END_RE = r"^## 4\. "
ID_PATTERN = r"B\d+"

ARCHIVE_HEADER = (
    "# BACKLOG-2026-09-07.md section 3 journal-row archive\n\n"
    "Free-form \"B<N>, date, ...\" journal rows older than ops/rotate_"
    "backlog_section3_items.py's retention window, moved here verbatim "
    "from BACKLOG-2026-09-07.md section 3 by that script. Never hand-"
    "edited. Newest first.\n"
)

ARCHIVED_MARKER = "Archived; see `BACKLOG-2026-09-07-SECTION3-ARCHIVE.md`."


def count_stats(text: str, cutoff: datetime.date):
    return core.count_stats(text, START_RE, END_RE, ID_PATTERN,
                             ARCHIVED_MARKER, cutoff)


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
    new_text, archived_blocks = core.plan_rotation(
        text, START_RE, END_RE, ID_PATTERN, ARCHIVED_MARKER, cutoff)

    if not archived_blocks:
        print("CLEAN: all section-3 journal rows with a resolvable date "
              "are within the %d-day retention window (cutoff %s). "
              "Nothing to rotate." % (args.days, cutoff.isoformat()))
        return 0

    total_bytes = sum(len(b.encode("utf-8")) for b in archived_blocks)
    if args.apply:
        new_archive_text = core.apply_archive(ARCHIVE_PATH, ARCHIVE_HEADER,
                                               archived_blocks)
        with io.open(ARCHIVE_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_archive_text)
        with io.open(BACKLOG_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        print("Moved %d row(s) (%d bytes) to %s. Live file shrank from %d "
              "to %d bytes." % (len(archived_blocks), total_bytes,
                                 ARCHIVE_PATH, len(text.encode("utf-8")),
                                 len(new_text.encode("utf-8"))))
    else:
        print("DUE: %d row(s) (%d bytes) are older than %s (retention %d "
              "days) and would move to %s on --apply." %
              (len(archived_blocks), total_bytes, cutoff.isoformat(),
               args.days, ARCHIVE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
