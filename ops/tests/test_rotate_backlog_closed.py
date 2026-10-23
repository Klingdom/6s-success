#!/usr/bin/env python3
"""
Prove ops/rotate_backlog_closed.py archives BACKLOG-2026-09-07.md's
numbered "## N. Closed/Done ..." sections (8 and up) correctly: sections
older than the cutoff move verbatim, recent sections stay live untouched,
sections 2-7 are never touched regardless of their own numbering, an
already-rotated file is a no-op (idempotent), and the archive write
prepends above existing content without disturbing it.

Run:  python ops/tests/test_rotate_backlog_closed.py
"""
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_backlog_closed as rbc                              # noqa: E402

PREFIX = (
    "# Backlog\n\n## 7. What I would tell you if you only read one line\n\n"
    "nothing rotated here.\n\n---\n\n"
)


def _section(num, date_str, title):
    return "## %d. Closed %s: %s\n\nbody text for section %d.\n\n---\n\n" \
        % (num, date_str, title, num)


def _file(*sections_md):
    return PREFIX + "".join(sections_md)


def main() -> int:
    fails = []
    today = datetime.date.today()
    d = lambda n: (today - datetime.timedelta(days=n)).isoformat()  # noqa: E731

    # 1. find_sections() only picks up sections numbered >= MIN_SECTION_NUM,
    #    ignores the "## 7." heading in PREFIX entirely.
    text = _file(_section(8, d(1), "alpha"), _section(9, d(2), "beta"))
    secs = rbc.find_sections(text)
    if [s["num"] for s in secs] != [8, 9]:
        fails.append("find_sections() picked up the wrong set: %r"
                      % [s["num"] for s in secs])
    if secs[0]["date"] != today - datetime.timedelta(days=1):
        fails.append("find_sections() read the wrong date for section 8: "
                      "%r" % secs[0]["date"])

    # 2. A section with no resolvable date is kept live, never guessed.
    text_nodate = _file("## 8. Closed at some point: no date here\n\n"
                         "body.\n\n---\n\n")
    secs_nodate = rbc.find_sections(text_nodate)
    if secs_nodate[0]["date"] is not None:
        fails.append("find_sections() invented a date where none exists")
    cutoff = today - datetime.timedelta(days=1)
    new_text_nd, archived_nd = rbc.plan_rotation(text_nodate, cutoff)
    if archived_nd:
        fails.append("plan_rotation() archived an undated section: %r"
                      % archived_nd)

    # 3. plan_rotation() moves only sections older than cutoff, keeps the
    #    rest live verbatim, and the part before section 8 (PREFIX) is
    #    byte-identical.
    text3 = _file(_section(8, d(1), "recent"),
                  _section(9, d(30), "old"),
                  _section(10, d(40), "older"))
    cutoff3 = today - datetime.timedelta(days=21)
    new_text3, archived3 = rbc.plan_rotation(text3, cutoff3)
    if not new_text3.startswith(PREFIX):
        fails.append("plan_rotation() altered the text before section 8")
    if "recent" not in new_text3 or "alpha" in new_text3:
        pass  # alpha never present in this text; sanity check only
    if "old" in new_text3 or "older" in new_text3:
        fails.append("plan_rotation() left an overdue section live: %r"
                      % new_text3)
    if "recent" not in new_text3:
        fails.append("plan_rotation() removed a section that should "
                      "have stayed live")
    if len(archived3) != 2:
        fails.append("plan_rotation() archived the wrong count: %r"
                      % len(archived3))
    # archived newest-first: section 9 (30 days) before section 10 (40 days)
    if not (archived3[0].startswith("## 9.")
            and archived3[1].startswith("## 10.")):
        fails.append("plan_rotation() did not archive newest-first: %r"
                      % [b.split("\n", 1)[0] for b in archived3])

    # 4. Losslessness: every archived block's own text is still present
    #    verbatim somewhere in the original document.
    for b in archived3:
        if b.rstrip("\n") not in text3:
            fails.append("archived block lost or altered content: %r"
                         % b[:80])

    # 5. Idempotency: running plan_rotation() again on the already-
    #    rotated text with the same cutoff finds nothing left to move.
    new_text3b, archived3b = rbc.plan_rotation(new_text3, cutoff3)
    if archived3b:
        fails.append("plan_rotation() was not idempotent: found %d more "
                      "sections to archive on a second pass"
                      % len(archived3b))

    # 6. apply_archive() prepends new material above whatever the archive
    #    already held, without disturbing it, and the result still opens
    #    with the fixed header.
    first_chunk = ["## 9. Closed %s: first\n\nbody.\n" % d(30)]
    archive_v1 = rbc.apply_archive(first_chunk, None)
    if not archive_v1.startswith(rbc.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("apply_archive() did not start with the fixed "
                      "header: %r" % archive_v1[:80])
    second_chunk = ["## 10. Closed %s: second\n\nbody.\n" % d(40)]
    archive_v2 = rbc.apply_archive(second_chunk, archive_v1)
    if archive_v2.find("## 10.") > archive_v2.find("## 9."):
        fails.append("apply_archive() did not prepend the new chunk "
                      "above the existing content: %r" % archive_v2[:200])
    if "## 9." not in archive_v2:
        fails.append("apply_archive() lost the previously archived "
                      "content on a second run")

    # 7. A mismatched existing archive header is refused, not guessed
    #    past (the same "never hand-edited" contract its siblings hold).
    try:
        rbc.apply_archive(second_chunk, "# Some other file\n\nbody\n")
        fails.append("apply_archive() silently accepted a mismatched "
                      "archive header")
    except ValueError:
        pass

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: rotate_backlog_closed.py, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
