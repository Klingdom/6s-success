#!/usr/bin/env python3
"""
Prove ops/rotate_nightly_log.py moves old ops/NIGHTLY-LOG.md entries into
the archive correctly and loses nothing: every entry that goes in on one
side or the other, never both, never neither, and never split apart.

Run:  python ops/tests/test_rotate_nightly_log.py
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

import rotate_nightly_log as rnl                                # noqa: E402

HEADER = "# Nightly log\n\nOne entry per unattended pass, newest first. Written to be read half awake.\n"


def _write(tmp, name, text):
    path = os.path.join(tmp, name)
    io.open(path, "w", encoding="utf-8").write(text)
    return path


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. split_header_and_entries() round-trips: header plus the joined
    #    entries reconstructs the original text exactly.
    text = HEADER + "\n" + "## %s, a\n\nbody a\n\n## %s, b\n\nbody b\n" % (d(0), d(1))
    header, entries = rnl.split_header_and_entries(
        text, rnl.HEADER_FIRST_LINE, rnl.HEADER_THIRD_PREFIX)
    if header + "\n\n" + "".join(entries) != text:
        fails.append("split_header_and_entries() did not round-trip: %r"
                      % ("".join(entries)[:200],))
    if len(entries) != 2:
        fails.append("expected 2 entries, got %d" % len(entries))

    # 2. A malformed header is refused, not guessed past.
    try:
        rnl.split_header_and_entries("# Wrong\n\nnope\n\n## x\nbody\n",
                                      rnl.HEADER_FIRST_LINE, rnl.HEADER_THIRD_PREFIX)
        fails.append("malformed header was silently accepted")
    except ValueError:
        pass

    # 3. leading_entry_date(): a heading opening with a date reads it; a
    #    heading with the date elsewhere (not the first token) still
    #    reads it, the real shape ~5% of this file's entries have; a
    #    heading with no date at all returns None.
    cases = [
        ("## 2026-10-02, scheduled cycle\n\nbody\n", datetime.date(2026, 10, 2)),
        ("## Scheduled operator cycle, 2026-10-02 (note)\n\nbody\n", datetime.date(2026, 10, 2)),
        ("## PM check-in (10:1x slot): no date here\n\nbody\n", None),
    ]
    for heading_text, expected in cases:
        got = rnl.leading_entry_date(heading_text)
        if got != expected:
            fails.append("leading_entry_date(%r) = %r, expected %r"
                          % (heading_text[:60], got, expected))

    # 4. effective_dates(): an undated entry inherits the nearest earlier
    #    (lower-index) entry's date; the very first entry, if undated,
    #    gets None rather than a guess.
    entries4 = [
        "## %s, a\n\nbody\n" % d(5),
        "## PM check-in: b\n\nbody\n",            # inherits d(5)
        "## %s, c\n\nbody\n" % d(3),
        "## Addendum: d\n\nbody\n",                 # inherits d(3)
        "## Addendum: e\n\nbody\n",                 # inherits d(3)
    ]
    got4 = rnl.effective_dates(entries4)
    want4 = [
        datetime.date.fromisoformat(d(5)), datetime.date.fromisoformat(d(5)),
        datetime.date.fromisoformat(d(3)), datetime.date.fromisoformat(d(3)),
        datetime.date.fromisoformat(d(3)),
    ]
    if got4 != want4:
        fails.append("effective_dates() inheritance wrong: got %r want %r" % (got4, want4))

    entries4b = ["## no date at all\n\nbody\n", "## %s, later\n\nbody\n" % d(0)]
    got4b = rnl.effective_dates(entries4b)
    if got4b[0] is not None:
        fails.append("an undated first entry with nothing to inherit from "
                      "must resolve to None, got %r" % (got4b[0],))

    # 5. plan_rotation(): entries older than cutoff move to archive, newer
    #    ones stay, nothing is lost, and the relative order within each
    #    group is preserved. An undated entry with no inheritable date
    #    stays live rather than being guessed into the archive.
    old_e = "## %s, old\n\nold body\n" % d(40)
    mid_e = "## %s, mid\n\nmid body\n" % d(10)
    new_e = "## %s, new\n\nnew body\n" % d(1)
    undated_e = "## undated, no date anywhere\n\nundated body\n"
    log_text = HEADER + "\n" + old_e + mid_e + new_e + undated_e
    cutoff = today - datetime.timedelta(days=20)
    new_log_text, archived = rnl.plan_rotation(log_text, cutoff)
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

    # 6. Nothing to rotate: every entry within the window returns the
    #    text unchanged and an empty archive list.
    all_new_text = HEADER + "\n" + new_e
    unchanged_text, unchanged_archived = rnl.plan_rotation(all_new_text, cutoff)
    if unchanged_archived != [] or unchanged_text != all_new_text:
        fails.append("plan_rotation() changed a file with nothing to rotate")

    # 7. apply_archive(): with no existing archive, the new chunk is
    #    written under the archive's own header. With an existing
    #    archive, the new chunk is prepended ABOVE the old content,
    #    which is itself preserved verbatim.
    arch_text_fresh = rnl.apply_archive([old_e], None)
    if not arch_text_fresh.startswith(rnl.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive text missing its own header")
    if old_e not in arch_text_fresh:
        fails.append("fresh archive text lost the entry being archived")

    existing_archive = rnl.ARCHIVE_HEADER + "\n" + "## %s, already archived\n\nbody\n" % d(90)
    arch_text_append = rnl.apply_archive([mid_e], existing_archive)
    pos_new = arch_text_append.find(mid_e.splitlines()[0])
    pos_old = arch_text_append.find("already archived")
    if pos_new == -1 or pos_old == -1 or pos_new > pos_old:
        fails.append("newly-archived entry did not land above the existing "
                      "archive content: %r" % (arch_text_append[:300],))
    if "already archived" not in arch_text_append:
        fails.append("apply_archive() lost pre-existing archive content")

    # 8. End-to-end via the CLI, against real temp files: --check reports
    #    exit 1 and makes no changes when something is due; --apply moves
    #    the old entry, leaves the archive carrying it, and a second
    #    --apply immediately after is a no-op (idempotent).
    with tempfile.TemporaryDirectory() as tmp:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir, exist_ok=True)
        log_path = os.path.join(ops_dir, "NIGHTLY-LOG.md")
        archive_path = os.path.join(ops_dir, "NIGHTLY-LOG-ARCHIVE.md")
        io.open(log_path, "w", encoding="utf-8").write(log_text)

        old_log_path, old_archive_path = rnl.LOG_PATH, rnl.ARCHIVE_PATH
        old_argv = sys.argv
        rnl.LOG_PATH, rnl.ARCHIVE_PATH = log_path, archive_path
        try:
            sys.argv = ["rotate_nightly_log.py", "--check", "--days", "20"]
            check_out = io.StringIO()
            with contextlib.redirect_stdout(check_out):
                rc_check = rnl.main()
            if rc_check != 1:
                fails.append("--check did not report exit 1 when rotation "
                              "was due (got %r)" % (rc_check,))
            if io.open(log_path, encoding="utf-8").read() != log_text:
                fails.append("--check modified the live log file")
            if os.path.exists(archive_path):
                fails.append("--check created an archive file")

            # The DUE message's byte count must describe the entries that
            # would actually move (old_e alone here), not the whole live
            # log's own size: a prior version reported n_bytes (the full
            # file) under a label implying it was the archived chunk's
            # size, which on the real file read "82 of 813 entries
            # (2302955 bytes)" where 2302955 was the entire file, not the
            # 82 entries.
            m = re.search(r"\((\d+) bytes\)", check_out.getvalue())
            if not m:
                fails.append("--check DUE message had no byte count to check: %r"
                              % (check_out.getvalue(),))
            else:
                reported_bytes = int(m.group(1))
                whole_file_bytes = len(log_text.encode("utf-8"))
                actual_removed_bytes = whole_file_bytes - len(
                    rnl.plan_rotation(log_text, today - datetime.timedelta(days=20))[0]
                    .encode("utf-8"))
                if reported_bytes != actual_removed_bytes:
                    fails.append(
                        "--check DUE byte count should be the archived "
                        "entries' own size (%d), got %d"
                        % (actual_removed_bytes, reported_bytes))
                if reported_bytes == whole_file_bytes:
                    fails.append(
                        "--check DUE byte count regressed to reporting the "
                        "whole live log's size (%d) instead of the smaller "
                        "archived chunk" % (whole_file_bytes,))

            sys.argv = ["rotate_nightly_log.py", "--apply", "--days", "20"]
            rc_apply = rnl.main()
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

            sys.argv = ["rotate_nightly_log.py", "--check", "--days", "20"]
            rc_check2 = rnl.main()
            if rc_check2 != 0:
                fails.append("--check after a clean --apply should report "
                              "exit 0, got %r" % (rc_check2,))

            before_second = io.open(log_path, encoding="utf-8").read()
            before_second_archive = io.open(archive_path, encoding="utf-8").read()
            sys.argv = ["rotate_nightly_log.py", "--apply", "--days", "20"]
            rnl.main()
            if io.open(log_path, encoding="utf-8").read() != before_second:
                fails.append("a second --apply with nothing due changed the live log")
            if io.open(archive_path, encoding="utf-8").read() != before_second_archive:
                fails.append("a second --apply with nothing due changed the archive")
        finally:
            rnl.LOG_PATH, rnl.ARCHIVE_PATH = old_log_path, old_archive_path
            sys.argv = old_argv

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: ops/rotate_nightly_log.py, checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
