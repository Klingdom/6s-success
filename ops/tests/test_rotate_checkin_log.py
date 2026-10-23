#!/usr/bin/env python3
"""
Prove ops/rotate_checkin_log.py moves old CHECKIN-LOG.md entries into the
archive correctly and loses nothing: every entry that goes in on one side
or the other, never both, never neither, and never split apart. Also
proves the one real difference from ops/rotate_nightly_log.py: this file
is oldest-first, so a newly-archived chunk must land AFTER the existing
archive content, not before it.

Run:  python ops/tests/test_rotate_checkin_log.py
"""
import contextlib
import datetime
import io
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_checkin_log as rcl                                # noqa: E402

HEADER = ("# Hourly check-in log\n\n"
          "What moved, what did not, and what is next. Written by "
          "ops/checkin.py so the record is measured rather than remembered.\n")


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. split_header_and_entries() round-trips.
    text = HEADER + "\n" + "## %s 09:00\n\nbody a\n\n## %s 10:00\n\nbody b\n" % (d(1), d(0))
    header, entries = rcl.split_header_and_entries(
        text, rcl.HEADER_FIRST_LINE, rcl.HEADER_THIRD_PREFIX)
    if header + "\n\n" + "".join(entries) != text:
        fails.append("split_header_and_entries() did not round-trip: %r"
                      % ("".join(entries)[:200],))
    if len(entries) != 2:
        fails.append("expected 2 entries, got %d" % len(entries))

    # 2. A malformed header is refused, not guessed past.
    try:
        rcl.split_header_and_entries("# Wrong\n\nnope\n\n## x\nbody\n",
                                      rcl.HEADER_FIRST_LINE, rcl.HEADER_THIRD_PREFIX)
        fails.append("malformed header was silently accepted")
    except ValueError:
        pass

    # 3. leading_entry_date(): the normal "## YYYY-MM-DD HH:MM" heading
    #    reads it; the one real historical variant with trailing text
    #    after a comma still reads it; a heading with no date at all
    #    returns None.
    cases = [
        ("## %s 14:53\n\nbody\n" % d(0), datetime.date.fromisoformat(d(0))),
        ("## %s 14:30, PM check-in\n\nbody\n" % d(2), datetime.date.fromisoformat(d(2))),
        ("## no date here\n\nbody\n", None),
    ]
    for heading_text, expected in cases:
        got = rcl.leading_entry_date(heading_text)
        if got != expected:
            fails.append("leading_entry_date(%r) = %r, expected %r"
                          % (heading_text[:60], got, expected))

    # 4. plan_rotation(): entries older than cutoff move to archive, newer
    #    ones stay, nothing is lost, order preserved, undated entries kept
    #    live rather than guessed into the archive.
    old_e = "## %s 09:00\n\nold body\n" % d(40)
    mid_e = "## %s 09:00\n\nmid body\n" % d(10)
    new_e = "## %s 09:00\n\nnew body\n" % d(1)
    undated_e = "## undated, no date anywhere\n\nundated body\n"
    log_text = HEADER + "\n" + old_e + mid_e + new_e + undated_e
    cutoff = today - datetime.timedelta(days=20)
    new_log_text, archived = rcl.plan_rotation(log_text, cutoff)
    if archived != [old_e]:
        fails.append("expected only the 40-day-old entry archived, got %r"
                      % ([e.splitlines()[0] for e in archived],))
    for must_stay in (mid_e, new_e, undated_e):
        if must_stay not in new_log_text:
            fails.append("entry wrongly removed from the live log: %r"
                          % (must_stay.splitlines()[0],))
    if old_e in new_log_text:
        fails.append("archived entry was not actually removed from the live log")
    if not new_log_text.startswith(HEADER.split("\n\n")[0]):
        fails.append("rotated live log lost its own header")

    # 5. Nothing to rotate: unchanged text, empty archive list.
    all_new_text = HEADER + "\n" + new_e
    unchanged_text, unchanged_archived = rcl.plan_rotation(all_new_text, cutoff)
    if unchanged_archived != [] or unchanged_text != all_new_text:
        fails.append("plan_rotation() changed a file with nothing to rotate")

    # 6. apply_archive(): the real difference from ops/rotate_nightly_
    #    log.py. The live log here is oldest-first, so a newly-archived
    #    chunk (always newer than whatever is already archived) must
    #    land AFTER the existing archive body, not before it.
    arch_text_fresh = rcl.apply_archive([old_e], None)
    if not arch_text_fresh.startswith(rcl.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive text missing its own header")
    if old_e not in arch_text_fresh:
        fails.append("fresh archive text lost the entry being archived")

    existing_archive = rcl.ARCHIVE_HEADER + "\n" + "## %s 08:00, already archived\n\nbody\n" % d(90)
    arch_text_append = rcl.apply_archive([mid_e], existing_archive)
    pos_new = arch_text_append.find(mid_e.splitlines()[0])
    pos_old = arch_text_append.find("already archived")
    if pos_new == -1 or pos_old == -1 or pos_new < pos_old:
        fails.append("newly-archived (newer) entry did not land AFTER the "
                      "existing (older) archive content: %r"
                      % (arch_text_append[:300],))
    if "already archived" not in arch_text_append:
        fails.append("apply_archive() lost pre-existing archive content")

    # 7. End-to-end via the CLI, against real temp files.
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, "CHECKIN-LOG.md")
        archive_path = os.path.join(tmp, "CHECKIN-LOG-ARCHIVE.md")
        io.open(log_path, "w", encoding="utf-8").write(log_text)

        old_log_path, old_archive_path = rcl.LOG_PATH, rcl.ARCHIVE_PATH
        old_argv = sys.argv
        rcl.LOG_PATH, rcl.ARCHIVE_PATH = log_path, archive_path
        try:
            sys.argv = ["rotate_checkin_log.py", "--check", "--days", "20"]
            check_out = io.StringIO()
            with contextlib.redirect_stdout(check_out):
                rc_check = rcl.main()
            if rc_check != 1:
                fails.append("--check did not report exit 1 when rotation "
                              "was due (got %r)" % (rc_check,))
            if io.open(log_path, encoding="utf-8").read() != log_text:
                fails.append("--check modified the live log file")
            if os.path.exists(archive_path):
                fails.append("--check created an archive file")

            m = re.search(r"\((\d+) bytes\)", check_out.getvalue())
            if not m:
                fails.append("--check DUE message had no byte count to check: %r"
                              % (check_out.getvalue(),))
            else:
                reported_bytes = int(m.group(1))
                whole_file_bytes = len(log_text.encode("utf-8"))
                actual_removed_bytes = whole_file_bytes - len(
                    rcl.plan_rotation(log_text, today - datetime.timedelta(days=20))[0]
                    .encode("utf-8"))
                if reported_bytes != actual_removed_bytes:
                    fails.append(
                        "--check DUE byte count should be the archived "
                        "entries' own size (%d), got %d"
                        % (actual_removed_bytes, reported_bytes))
                if reported_bytes == whole_file_bytes:
                    fails.append(
                        "--check DUE byte count regressed to reporting the "
                        "whole live log's size instead of the smaller "
                        "archived chunk")

            sys.argv = ["rotate_checkin_log.py", "--apply", "--days", "20"]
            rc_apply = rcl.main()
            if rc_apply != 0:
                fails.append("--apply returned nonzero: %r" % (rc_apply,))
            after_log = io.open(log_path, encoding="utf-8").read()
            if old_e in after_log:
                fails.append("--apply left the old entry in the live log")
            if not os.path.exists(archive_path):
                fails.append("--apply did not create the archive file")
            else:
                after_archive = io.open(archive_path, encoding="utf-8").read()
                if old_e not in after_archive:
                    fails.append("--apply did not land the old entry in the archive")
            if os.path.exists(log_path + ".tmp") or os.path.exists(archive_path + ".tmp"):
                fails.append("--apply left a .tmp file behind")

            sys.argv = ["rotate_checkin_log.py", "--check", "--days", "20"]
            rc_check2 = rcl.main()
            if rc_check2 != 0:
                fails.append("--check after a clean --apply should report "
                              "exit 0, got %r" % (rc_check2,))

            before_second = io.open(log_path, encoding="utf-8").read()
            before_second_archive = io.open(archive_path, encoding="utf-8").read()
            sys.argv = ["rotate_checkin_log.py", "--apply", "--days", "20"]
            rcl.main()
            if io.open(log_path, encoding="utf-8").read() != before_second:
                fails.append("a second --apply with nothing due changed the live log")
            if io.open(archive_path, encoding="utf-8").read() != before_second_archive:
                fails.append("a second --apply with nothing due changed the archive")
        finally:
            rcl.LOG_PATH, rcl.ARCHIVE_PATH = old_log_path, old_archive_path
            sys.argv = old_argv

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ops/rotate_checkin_log.py, checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
