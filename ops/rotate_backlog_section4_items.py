#!/usr/bin/env python3
"""Archive old free-form journal rows (C6/C7 onward) out of
BACKLOG-2026-09-07.md section 4, "Now: images and video".

See ops/rotate_backlog_journal_core.py's own docstring for the full
account of why this needed its own module. Section 4 is where the real
hazard lives, confirmed by direct scan rather than assumed: two un-id'd
"Corrected 2026-10-14" paragraphs sit physically after the "C7
fourth-wave" row (dated 2026-10-27) but actually amend the different,
earlier "C7 second wave" entry (dated 2026-10-09). A parser that
archives "from one matched row up to the next" would file those
corrections under the fourth-wave row's byline, the exact
misattribution rotate_backlog_done_items.py's own docstring warned
about. This module's core never does that: it removes only a matched
row's own single physical line and leaves everything after it,
including that orphan pair, live and untouched. The two live Phil-gated
rows this section carries today, C5 (Gemini billing) and C6 (YouTube
OAuth), have no date in their own lead and are excluded the same way
every dateless row is, not by special-casing their ids.

Usage:
    python ops/rotate_backlog_section4_items.py --check
    python ops/rotate_backlog_section4_items.py --check --days N
    python ops/rotate_backlog_section4_items.py --apply   (default 14-day window)
    python ops/rotate_backlog_section4_items.py --apply --days N
"""
import argparse
import datetime
import io
import os
import sys

import rotate_backlog_journal_core as core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKLOG_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07.md")
ARCHIVE_PATH = os.path.join(ROOT, "BACKLOG-2026-09-07-SECTION4-ARCHIVE.md")

DEFAULT_RETENTION_DAYS = 14

START_RE = r"^## 4\. Now: images and video"
END_RE = r"^## 5\. "
ID_PATTERN = r"C\d+"

ARCHIVE_HEADER = (
    "# BACKLOG-2026-09-07.md section 4 journal-row archive\n\n"
    "Free-form \"C<N>, date, ...\" journal rows older than ops/rotate_"
    "backlog_section4_items.py's retention window, moved here verbatim "
    "from BACKLOG-2026-09-07.md section 4 by that script. Never hand-"
    "edited. Newest first.\n"
)

ARCHIVED_MARKER = "Archived; see `BACKLOG-2026-09-07-SECTION4-ARCHIVE.md`."


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
        print("CLEAN: all section-4 journal rows with a resolvable date "
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
