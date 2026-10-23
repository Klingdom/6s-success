#!/usr/bin/env python3
"""
Prove ops/rotate_backlog.py archives BACKLOG-2026-09-07.md's "Done this
week" table rows correctly: rows older than the cutoff move verbatim
(reformatted to valid '| ... |' syntax when the live row had degraded),
recent rows stay live, an already-rotated table is a no-op, a missing or
duplicated anchor is refused rather than guessed past, and the archive
write prepends above existing content without disturbing it.

Run:  python ops/tests/test_rotate_backlog.py
"""
import datetime
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_backlog as rb                                      # noqa: E402

PREFIX = "# Backlog\n\n## 0. Some live section\n\nnothing rotated here.\n\n"
SUFFIX_AFTER = "\n\n---\n\n## 1b. Next live section\n\nalso untouched.\n"


def _table(rows_md):
    return (PREFIX + rb.SECTION_HEADING + "\n\n" + rb.TABLE_HEADER + "\n"
            + rb.TABLE_SEP + "\n" + "\n".join(rows_md) + SUFFIX_AFTER)


def _row(date_str, label):
    return "| **%s, done %s.** | evidence for %s |" % (label, date_str, label)


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. locate_section() finds the table body between the header and the
    #    next-heading anchor.
    text = _table([_row(d(1), "recent"), _row(d(30), "old")])
    body_start, body_end = rb.locate_section(text)
    body = text[body_start:body_end]
    if "recent" not in body or "old" not in body:
        fails.append("locate_section() did not capture both rows: %r"
                      % body[:120])

    # 2. A missing SECTION_HEADING is refused, not guessed past.
    try:
        rb.locate_section(text.replace(rb.SECTION_HEADING, "## 1. Gone"))
        fails.append("missing section heading was silently accepted")
    except ValueError:
        pass

    # 3. A duplicated NEXT_HEADING_ANCHOR is refused.
    try:
        rb.locate_section(text + rb.NEXT_HEADING_ANCHOR)
        fails.append("duplicated next-heading anchor was silently accepted")
    except ValueError:
        pass

    # 4. parse_rows() finds a malformed row (no leading/trailing pipe,
    #    the real 2026-10-23-found shape) exactly as well as a proper one.
    malformed = "**Bare paragraph row, done %s.** evidence, no pipes" % d(2)
    text2 = _table([_row(d(1), "proper"), malformed])
    body2 = text2[rb.locate_section(text2)[0]:rb.locate_section(text2)[1]]
    rows2 = rb.parse_rows(body2)
    if len(rows2) != 2:
        fails.append("parse_rows() did not find both the proper and the "
                      "malformed row: %r" % rows2)

    # 5. normalize_row() wraps a bare row in exactly one '| ... |' and is
    #    idempotent on an already-correct row.
    norm = rb.normalize_row(malformed)
    if not (norm.startswith("| ") and norm.endswith(" |")
            and norm.count("|") == 2):
        fails.append("normalize_row() did not produce clean '| ... |' "
                      "syntax: %r" % norm)
    already_ok = "| **Proper row.** | evidence |"
    if rb.normalize_row(already_ok) != already_ok:
        fails.append("normalize_row() was not idempotent on a clean row: "
                      "%r" % rb.normalize_row(already_ok))

    # 6. row_date() reads the first date inside the row's own bold title,
    #    not a later date an Evidence cell might cite.
    mixed = "| **Fixed thing, done %s.** | mentions an earlier %s date too |" \
        % (d(1), d(50))
    rdate = rb.row_date(mixed)
    if rdate != today - datetime.timedelta(days=1):
        fails.append("row_date() picked the wrong date out of a mixed "
                      "row: %r" % rdate)
    if rb.row_date("| **No date here at all.** | evidence |") is not None:
        fails.append("row_date() invented a date for a row with none")

    # 7. plan_rotation() moves only rows older than cutoff, keeps the rest
    #    live (reformatted), and the rest of the document (PREFIX/SUFFIX)
    #    is byte-identical.
    text3 = _table([_row(d(1), "recent"), _row(d(30), "old"),
                     _row(d(40), "older")])
    cutoff = today - datetime.timedelta(days=14)
    new_text, archived, kept = rb.plan_rotation(text3, cutoff)
    if kept != 1:
        fails.append("plan_rotation() kept %d rows, expected 1" % kept)
    if len(archived) != 2:
        fails.append("plan_rotation() archived %d rows, expected 2"
                      % len(archived))
    if "recent" not in new_text or "old" in new_text or "older" in new_text:
        fails.append("plan_rotation() left stale content live or dropped "
                      "the recent row")
    if not new_text.startswith(PREFIX) or not new_text.endswith(SUFFIX_AFTER):
        fails.append("rotation disturbed text outside the table")
    if not any("old" in a for a in archived):
        fails.append("archived rows lost their content")

    # 8. A row with no resolvable date is kept live rather than guessed
    #    into the archive, same convention as ops/rotate_nightly_log.py.
    undated = "| **No date at all here.** | evidence |"
    text4 = _table([_row(d(40), "old"), undated])
    new_text4, archived4, kept4 = rb.plan_rotation(text4, cutoff)
    if "No date at all here" not in new_text4:
        fails.append("an undated row was archived instead of kept live")

    # 9. Already-rotated text is a no-op.
    new_text5, archived5, kept5 = rb.plan_rotation(new_text, cutoff)
    if archived5 or new_text5 != new_text:
        fails.append("an already-rotated table was rotated again")

    # 10. apply_archive() with no existing archive writes the header once;
    #     with existing content it prepends the new block above it,
    #     leaving old entries intact and in place (newest-first).
    fresh = rb.apply_archive(["| **First ever archived row.** | e |"], None)
    if not fresh.startswith(rb.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive did not start with the expected header")
    if "First ever archived row" not in fresh:
        fails.append("fresh archive lost its only row")
    grown = rb.apply_archive(["| **Second batch row.** | e |"], fresh)
    if "Second batch row" not in grown or "First ever archived row" not in grown:
        fails.append("growing the archive lost a row")
    if grown.find("Second batch row") > grown.find("First ever archived row"):
        fails.append("new archive content was not placed above older content")

    # 11. apply_archive() refuses an existing file with the wrong header.
    try:
        rb.apply_archive(["| **Row.** | e |"], "# Some Other Document\n\nbody\n")
        fails.append("a wrong-header archive file was silently accepted")
    except ValueError:
        pass

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 11/11 cases ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
