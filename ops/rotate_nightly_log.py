#!/usr/bin/env python3
"""Move old ops/NIGHTLY-LOG.md entries into ops/NIGHTLY-LOG-ARCHIVE.md.

Found 2026-10-14: the live log had grown to 8.1MB / 57,105 lines / 2,094
entries spanning 2026-08-23 to 2026-10-14, never rotated since the file was
created, because nothing ever removed an entry and nothing was supposed to.
Four separate gates in ops/preflight.py (gate_nightly_log_ordering,
gate_nightly_log_no_duplicate_entries, gate_cold_read_handoff_not_stale, and
STEP 1 of the operating prompt itself, "read the last four entries") each
read this whole file into memory and regex it on every single preflight run,
most of a day's several dozen runs, to look at content from a month or more
ago that none of them use. That is a real, measured cost (this file alone
accounted for a large share of the 480s-to-580s preflight budget BACKLOG-
2026-09-07.md section 7 names as a recurring near-miss), it compounds every
day the log keeps growing, and it had never been named anywhere: not in
GOALS.md, not in RISKS.md, not in a nightly log entry about the log itself.

Nothing here deletes a word. Entries move verbatim, in the exact order they
already have, into ops/NIGHTLY-LOG-ARCHIVE.md: CLAUDE.md's Decision/Learning
Memory sections say not to erase the record, and ops/NIGHTLY-LOG.md's own
"Failure Is Information" principle (CLAUDE.md section 54) applies here too.
The live log keeps its exact three-line header and its newest-first
ordering; the file's own legacy oldest-first tail (entries from before
ops/nightly_log.py existed, 2026-08-24 through 2026-09-04) is moved as one
untouched block once it falls outside the retention window, preserving its
internal order rather than "fixing" it, the same choice
gate_nightly_log_ordering()'s own docstring already made.

Usage:
    python ops/rotate_nightly_log.py --check            report only, exit 1 if over the window
    python ops/rotate_nightly_log.py --check --days N   use a different retention window
    python ops/rotate_nightly_log.py --apply            rotate now (default 14-day window)
    python ops/rotate_nightly_log.py --apply --days N
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
ARCHIVE_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG-ARCHIVE.md")

HEADER_FIRST_LINE = "# Nightly log"
HEADER_THIRD_PREFIX = "One entry per unattended pass"
ARCHIVE_HEADER_FIRST_LINE = "# Nightly log archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Entries older than ops/rotate_nightly_log.py's retention window, moved "
    "here verbatim and in their original order by that script. Never hand-"
    "edited. The live entries and the reasoning for this split are in "
    "ops/NIGHTLY-LOG.md.\n"
)

DEFAULT_RETENTION_DAYS = 14


def split_header_and_entries(text: str, first_line: str, third_prefix: str):
    """Return (header, entries) where header is the file's first three
    lines joined and entries is the list of '## ...' blocks (each with its
    own trailing blank line, if any) making up everything after it. Raises
    ValueError if the header does not match, the same refuse-to-guess
    behaviour ops/nightly_log.py's prepend_entry() already uses.
    """
    lines = text.split("\n")
    if len(lines) < 3 or not lines[0].startswith(first_line) \
            or not lines[2].startswith(third_prefix):
        raise ValueError(
            "File does not start with the expected three-line header "
            "('%s', blank, '%s...'); refusing to guess where entries "
            "start." % (first_line, third_prefix))
    header = "\n".join(lines[:3])
    rest = "\n".join(lines[3:]).lstrip("\n")
    if not rest:
        return header, []
    starts = [m.start() for m in re.finditer(r"(?m)^## ", rest)]
    if not starts:
        return header, []
    starts.append(len(rest))
    entries = [rest[starts[i]:starts[i + 1]] for i in range(len(starts) - 1)]
    return header, entries


def leading_entry_date(entry: str):
    """The calendar date named in an entry's own one-line heading, or None
    if the heading names no date at all. Most headings open
    "## YYYY-MM-DD, ..."; a real, large minority instead read
    "## Scheduled operator cycle, YYYY-MM-DD (...)" or similar, the date
    present but not the first token. Checked directly against the real
    file (2026-10-14): taking only a LEADING date disagreed with a date
    named elsewhere in the same heading on 137 of 2,795 entries, always by
    exactly one day, because the heading's own real date got overridden by
    inheritance from the next entry up instead. Searching the whole
    heading line for the first YYYY-MM-DD pattern, not just its start,
    resolved every one of those 137 without introducing a new mismatch.
    Deliberately scoped to the heading line only, not the entry's full
    body: body prose routinely narrates other dates ("the 2026-08-21
    sale"), which is not this entry's own date.
    """
    heading = entry.split("\n", 1)[0]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", heading)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def effective_dates(entries):
    """One date per entry, inheriting forward through the list from the
    nearest earlier entry (lower index, i.e. appearing above it in the
    file) that carries an explicit leading date. Found 2026-10-14: a
    naive "archive only entries with their own leading date" rule would
    never archive roughly 700 of this file's 2,795 real entries (titles
    like "## PM check-in (10:1x slot): previous work finished...", which
    is a genuine, dated cycle's entry, just not repeating the date its
    immediate neighbours already state), so the file would keep growing
    almost as fast regardless of retention window. An entry with no
    explicit date and no earlier dated entry yet to inherit from (should
    not occur in the real file, whose first entry is always dated; kept
    as a defensive case rather than assumed away) gets None, and
    plan_rotation() below keeps a None-dated entry live rather than
    guess it into the archive.
    """
    dates = []
    current = None
    for e in entries:
        d = leading_entry_date(e)
        if d is not None:
            current = d
        dates.append(current)
    return dates


def plan_rotation(log_text: str, cutoff: datetime.date):
    """Split the live log's entries at `cutoff`: entries whose effective
    date (see effective_dates()) is on or after it stay live, entries
    dated strictly before it are archived. An entry with no resolvable
    date is kept live rather than guessed into the archive. Returns
    (new_log_text, archived_entries_in_original_order). Pure function of
    its inputs; does no I/O, so it is directly testable.
    """
    header, entries = split_header_and_entries(
        log_text, HEADER_FIRST_LINE, HEADER_THIRD_PREFIX)
    dates = effective_dates(entries)
    keep, archived = [], []
    for e, d in zip(entries, dates):
        if d is not None and d < cutoff:
            archived.append(e)
        else:
            keep.append(e)
    if not archived:
        return log_text, []
    new_log_text = header + "\n\n" + "".join(keep)
    if not new_log_text.endswith("\n"):
        new_log_text += "\n"
    return new_log_text, archived


def apply_archive(archived_entries, existing_archive_text: str | None) -> str:
    """Build the new archive file text: the archive's fixed header, then
    the newly-archived entries (still in their original, already-correct
    order), then whatever the archive already held. New material goes on
    top so the archive keeps the same newest-first-then-legacy-oldest-
    first shape the live log itself has, continuing where the live log's
    top leaves off each time this runs again.
    """
    new_chunk = "".join(archived_entries)
    if existing_archive_text:
        _, old_entries = split_header_and_entries(
            existing_archive_text, ARCHIVE_HEADER_FIRST_LINE,
            "Entries older than")
        old_body = "".join(old_entries)
    else:
        old_body = ""
    body = new_chunk if not old_body else new_chunk + old_body
    return ARCHIVE_HEADER + "\n" + body


def count_stats(text: str):
    header, entries = split_header_and_entries(
        text, HEADER_FIRST_LINE, HEADER_THIRD_PREFIX)
    return len(entries), len(text.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                     help="Report current size and whether rotation is due; "
                          "makes no changes.")
    ap.add_argument("--apply", action="store_true",
                     help="Rotate now: move entries older than --days into "
                          "the archive.")
    ap.add_argument("--days", type=int, default=DEFAULT_RETENTION_DAYS,
                     help="Retention window in days (default %d)."
                          % DEFAULT_RETENTION_DAYS)
    args = ap.parse_args()
    if not args.check and not args.apply:
        ap.error("pass --check or --apply")

    log_text = io.open(LOG_PATH, encoding="utf-8").read()
    n_entries, n_bytes = count_stats(log_text)
    cutoff = datetime.date.today() - datetime.timedelta(days=args.days)
    new_log_text, archived = plan_rotation(log_text, cutoff)

    if args.check:
        if archived:
            print("DUE: %d of %d entries (%d bytes) are older than %s "
                  "(retention %d days) and would move to %s on --apply."
                  % (len(archived), n_entries, n_bytes, cutoff.isoformat(),
                     args.days, ARCHIVE_PATH))
            return 1
        print("CLEAN: all %d entries (%d bytes) are within the %d-day "
              "retention window (cutoff %s). Nothing to rotate."
              % (n_entries, n_bytes, args.days, cutoff.isoformat()))
        return 0

    # --apply
    if not archived:
        print("Nothing older than %s (retention %d days); no change made."
              % (cutoff.isoformat(), args.days))
        return 0

    existing_archive_text = None
    if os.path.exists(ARCHIVE_PATH):
        existing_archive_text = io.open(ARCHIVE_PATH, encoding="utf-8").read()
    new_archive_text = apply_archive(archived, existing_archive_text)

    # Write-then-rename both files, archive first: if the process dies
    # between the two writes, the worst case is an entry that exists in
    # both the (unrotated) live log and the archive, never one that exists
    # in neither.
    archive_tmp = ARCHIVE_PATH + ".tmp"
    io.open(archive_tmp, "w", encoding="utf-8").write(new_archive_text)
    os.replace(archive_tmp, ARCHIVE_PATH)

    log_tmp = LOG_PATH + ".tmp"
    io.open(log_tmp, "w", encoding="utf-8").write(new_log_text)
    os.replace(log_tmp, LOG_PATH)

    new_n_entries, new_n_bytes = count_stats(new_log_text)
    print("Moved %d entries (%d bytes) to %s. Live log: %d entries, %d "
          "bytes (was %d entries, %d bytes)."
          % (len(archived), n_bytes - new_n_bytes, ARCHIVE_PATH,
             new_n_entries, new_n_bytes, n_entries, n_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
