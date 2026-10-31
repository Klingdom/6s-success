#!/usr/bin/env python3
"""Move old CHECKIN-LOG.md entries into CHECKIN-LOG-ARCHIVE.md.

Found 2026-10-23, while checking whether the shape ops/rotate_nightly_log.py
and ops/rotate_status_history.py were each built to fix (something grows
without bound because nothing ever rotates it, and every later cycle pays
to read the whole thing) also exists elsewhere. It does: CHECKIN-LOG.md is
written append-only, oldest first, by ops/checkin.py, once an hour, and
nothing has ever moved an old entry out of it. At 673 entries back to
2026-09-02 it is 288KB, not yet the 8.1MB ops/NIGHTLY-LOG.md had grown to
before that file's own rotation shipped, but it is the identical shape and
the identical trajectory: unbounded, one append at a time, forever. Fixing
it now is cheaper than fixing it once it is a measured cost the way that
file was.

Nothing here deletes a word. Entries move verbatim, in the exact order
they already have, into CHECKIN-LOG-ARCHIVE.md: CLAUDE.md's Decision/
Learning Memory sections say not to erase the record.

Unlike ops/NIGHTLY-LOG.md (newest first), this file is oldest first, so
rotation always removes from the TOP of the live log and the newly
archived block is always newer than whatever the archive already holds;
it is appended after the existing archive body, not placed before it, to
keep the whole archive oldest-first too.

Usage:
    python ops/rotate_checkin_log.py --check            report only, exit 1 if over the window
    python ops/rotate_checkin_log.py --check --days N   use a different retention window
    python ops/rotate_checkin_log.py --apply            rotate now (default 8-day window)
    python ops/rotate_checkin_log.py --apply --days N

Found 2026-10-31: the hourly cadence writes a steady ~440 bytes/entry,
24 entries/day, so the original 30-day default settles at roughly 316KB,
well past gate_living_docs_total_size_tripwire's 110,000-byte ceiling for
this file even with every entry inside the retention window and nothing
overdue by gate_checkin_log_not_oversized's own (30+7)-day buffer. Lowered
to 8 days, which settles at roughly 90-100KB: under the tripwire with a
buffer of about two days' growth before the next rotation is needed.
"""
import argparse
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "CHECKIN-LOG.md")
ARCHIVE_PATH = os.path.join(ROOT, "CHECKIN-LOG-ARCHIVE.md")

HEADER_FIRST_LINE = "# Hourly check-in log"
HEADER_THIRD_PREFIX = "What moved, what did not"
ARCHIVE_HEADER_FIRST_LINE = "# Hourly check-in log archive"
ARCHIVE_HEADER = (
    ARCHIVE_HEADER_FIRST_LINE + "\n\n"
    "Entries older than ops/rotate_checkin_log.py's retention window, "
    "moved here verbatim and in their original (oldest-first) order by "
    "that script. Never hand-edited. The live entries and the reasoning "
    "for this split are in CHECKIN-LOG.md.\n"
)

DEFAULT_RETENTION_DAYS = 8


def split_header_and_entries(text: str, first_line: str, third_prefix: str):
    """Return (header, entries) where header is the file's first three
    lines joined and entries is the list of '## ...' blocks (each with
    its own trailing blank line, if any) making up everything after it.
    Raises ValueError if the header does not match, so this refuses to
    guess where entries start rather than silently misreading the file.
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
    """The calendar date named anywhere in an entry's own one-line
    heading, or None if the heading names no date at all. Every entry
    ops/checkin.py writes opens "## YYYY-MM-DD HH:MM"; one historical
    heading in the real file reads "## YYYY-MM-DD HH:MM, PM check-in",
    the date still present but not the whole heading, so this searches
    the line rather than anchoring to its start.
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
    """One date per entry, inheriting forward from the nearest earlier
    (lower-index) entry that carries an explicit date. Every real entry
    in this file has its own explicit date, so this is defensive rather
    than load-bearing; kept for the same reason
    ops/rotate_nightly_log.py's identically-named function keeps it: an
    entry with no resolvable date at all, here or inherited, gets None
    and plan_rotation() below keeps it live rather than guess.
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
    date is on or after it stay live, entries dated strictly before it
    are archived. An entry with no resolvable date is kept live rather
    than guessed into the archive. Returns (new_log_text,
    archived_entries_in_original_order). Pure function of its inputs.
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
    whatever it already held, then the newly-archived entries. The live
    log is oldest-first and rotation always removes from its top, so the
    newly-archived block is always newer than the existing archive body;
    appending it after keeps the whole archive oldest-first throughout,
    the mirror image of ops/rotate_nightly_log.py's newest-on-top choice
    for its newest-first live log.
    """
    new_chunk = "".join(archived_entries)
    if existing_archive_text:
        _, old_entries = split_header_and_entries(
            existing_archive_text, ARCHIVE_HEADER_FIRST_LINE,
            "Entries older than")
        old_body = "".join(old_entries)
    else:
        old_body = ""
    body = new_chunk if not old_body else old_body + new_chunk
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
            _, new_n_bytes = count_stats(new_log_text)
            print("DUE: %d of %d entries (%d bytes) are older than %s "
                  "(retention %d days) and would move to %s on --apply."
                  % (len(archived), n_entries, n_bytes - new_n_bytes,
                     cutoff.isoformat(), args.days, ARCHIVE_PATH))
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
    # both the (unrotated) live log and the archive, never one that
    # exists in neither.
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
