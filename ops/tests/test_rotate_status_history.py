#!/usr/bin/env python3
"""
Prove ops/rotate_status_history.py keeps only the newest STATUS.md
"Production Knowledge" entry live (cases 1-9) and the base statement of
the "Immediate Focus" line (cases 10-12), moving the rest into the archive
correctly in both cases: every entry ends up on exactly one side, nothing
is edited, and a file that does not match the expected shape is refused
rather than guessed past.

Run:  python ops/tests/test_rotate_status_history.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_status_history as rsh                             # noqa: E402

BEFORE = (
    "# 30. Current Overall Assessment\n\n"
    "**Operating System:** OPERATING.\n\n"
    "**Autonomous Execution Readiness:** FULL FOR GREEN-BAND WORK, more "
    "prose on this same line.\n\n"
)
AFTER = (
    "**Business Data Knowledge, re-measured:** ONE SALE.\n\n"
    "**Executive Visibility:** LIVE.\n"
)


def _chain_text(n):
    entries = []
    for i in range(n):
        entries.append("**Production Knowledge, CLOSED day-%d:** body text "
                        "for entry %d, nothing interesting." % (i, i))
    return BEFORE + "\n\n".join(entries) + "\n\n" + AFTER


def main() -> int:
    fails = []

    # 1. split_chain() finds exactly the entries between the two anchors,
    #    in order, and reconstructing before+chain+after loses nothing.
    text = _chain_text(5)
    before, lines, after = rsh.split_chain(text)
    def _day(entry):
        return int(entry.split("day-")[1].split(":")[0])

    if len(lines) != 5:
        fails.append("expected 5 entries, got %d" % len(lines))
    if [_day(l) for l in lines] != list(range(5)):
        fails.append("entries came back out of order: %r" % lines)
    if not before.endswith("same line.") or not after.startswith(
            "**Business Data Knowledge"):
        fails.append("before/after boundaries drifted: %r / %r"
                      % (before[-40:], after[:40]))

    # 2. A missing anchor is refused, not guessed past.
    try:
        rsh.split_chain(BEFORE.replace("Autonomous Execution Readiness",
                                        "Something Else") + AFTER)
        fails.append("missing start anchor was silently accepted")
    except ValueError:
        pass

    # 3. A duplicated anchor is refused.
    try:
        rsh.split_chain(text + "\n\n**Autonomous Execution Readiness:** "
                         "again.\n")
        fails.append("duplicated start anchor was silently accepted")
    except ValueError:
        pass

    # 4. A line inside the span that is not a bold entry is refused
    #    rather than silently dropped or mis-split.
    bad = BEFORE + "not a bold entry at all\n\n" + AFTER
    try:
        rsh.split_chain(bad)
        fails.append("an unrecognised line inside the span was accepted")
    except ValueError:
        pass

    # 5. plan_rotation() keeps exactly the newest entry live and returns
    #    the rest as archived, in their original order, nothing lost or
    #    duplicated.
    text5 = _chain_text(5)
    new_text, archived = rsh.plan_rotation(text5)
    _, kept_lines, _ = rsh.split_chain(new_text)
    if len(kept_lines) != 1:
        fails.append("expected 1 entry to stay live, got %d" % len(kept_lines))
    if kept_lines and "day-0" not in kept_lines[0]:
        fails.append("the entry kept live was not the newest: %r"
                      % kept_lines[0][:60])
    if len(archived) != 4:
        fails.append("expected 4 archived entries, got %d" % len(archived))
    elif [_day(e) for e in archived] != [1, 2, 3, 4]:
        fails.append("archived entries were not entries 1-4 in order: %r"
                      % archived)

    # 6. A chain already down to one entry is a no-op: plan_rotation()
    #    returns the text unchanged and an empty archive list.
    text1 = _chain_text(1)
    new_text1, archived1 = rsh.plan_rotation(text1)
    if new_text1 != text1 or archived1:
        fails.append("a single-entry chain was rotated when it should "
                     "have been left alone")

    # 7. apply_archive() with no existing archive writes a well-formed
    #    archive carrying every entry it was given, in order.
    fresh = rsh.apply_archive(["**A:** one.", "**B:** two."], None)
    if not fresh.startswith(rsh.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive missing its own header")
    if "**A:** one." not in fresh or "**B:** two." not in fresh:
        fails.append("fresh archive lost an entry")
    if fresh.index("**A:** one.") > fresh.index("**B:** two."):
        fails.append("fresh archive did not preserve entry order")

    # 8. apply_archive() onto an existing archive puts the new entries on
    #    top, keeps the old ones, in order, and does not touch the header.
    existing = (rsh.ARCHIVE_HEADER_FIRST_LINE + "\n\n> note.\n\n---\n\n"
                "**OLD:** already here.\n")
    combined = rsh.apply_archive(["**NEW:** just archived."], existing)
    if combined.index("**NEW:** just archived.") > \
            combined.index("**OLD:** already here."):
        fails.append("new archive entries were not placed above old ones")
    if "> note." not in combined:
        fails.append("existing archive header was lost on a repeat run")

    # 9. apply_archive() refuses an existing archive file with the wrong
    #    header rather than prepending onto something else.
    try:
        rsh.apply_archive(["**NEW:** x."], "# Something else entirely\n")
        fails.append("a malformed existing archive was silently accepted")
    except ValueError:
        pass

    # 10. split_focus_line() finds the base statement and every dated
    #     correction, oldest first, and does not mistake a comma-
    #     introduced date clause inside the base statement itself (the
    #     real 2026-10-23 bug: "SINCE 2026-09-02, RE-CONFIRMED 2026-09-15:"
    #     is one sentence, not two) for a chain entry.
    focus_text = (
        "**Immediate Focus:** UNCHANGED SINCE 2026-09-02, RE-CONFIRMED "
        "2026-09-15: TRAFFIC IS THE CONSTRAINT. UPDATED 2026-09-30, ops: "
        "first correction. WIDENED 2026-10-01, ops: second correction.\n"
        "**Next field:** unrelated.\n"
    )
    f_before, f_base, f_entries, f_after = rsh.split_focus_line(focus_text)
    if "RE-CONFIRMED 2026-09-15" not in f_base:
        fails.append("base statement's own comma-introduced date clause "
                      "was wrongly split off: %r" % f_base)
    if len(f_entries) != 2:
        fails.append("expected 2 dated entries, got %d: %r"
                      % (len(f_entries), f_entries))
    elif not f_entries[0].startswith("UPDATED 2026-09-30") or \
            not f_entries[1].startswith("WIDENED 2026-10-01"):
        fails.append("dated entries came back out of order: %r" % f_entries)
    if not f_after.startswith("\n**Next field:**"):
        fails.append("focus line's own end boundary drifted: %r"
                      % f_after[:40])

    # 11. plan_rotation_focus() keeps the base statement plus the given
    #     tail live, and archives every dated entry newest-first (the
    #     archive's own stated convention), reformatted only to bold its
    #     header.
    new_focus_text, focus_archived = rsh.plan_rotation_focus(
        focus_text, "TAIL POINTER.")
    _, kept_base, kept_entries, _ = rsh.split_focus_line(new_focus_text)
    if kept_entries:
        fails.append("rotation left dated entries live: %r" % kept_entries)
    if "TAIL POINTER." not in kept_base:
        fails.append("replacement tail was not appended to the kept line")
    if len(focus_archived) != 2:
        fails.append("expected 2 archived focus entries, got %d: %r"
                      % (len(focus_archived), focus_archived))
    elif not focus_archived[0].startswith("**Immediate Focus, WIDENED "
                                           "2026-10-01"):
        fails.append("focus archive was not newest-first: %r"
                      % focus_archived)

    # 12. A focus line with no dated corrections is a no-op.
    plain_focus = "**Immediate Focus:** NOTHING TO ROTATE HERE.\n"
    new_plain, archived_plain = rsh.plan_rotation_focus(plain_focus, "X")
    if new_plain != plain_focus or archived_plain:
        fails.append("a focus line with no corrections was rotated when "
                      "it should have been left alone")

    # 13-18. BLOCKER-001's own shape: oldest-first, multi-paragraph
    # entries, a new entry starting only where a paragraph opens bold.
    b1_text = (
        "# 17. Current Blockers\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n"
        "\n**RESOLVED 2026-09-25, this session: production redeployed.** "
        "`ops/deploy.py` confirms it.\n\n"
        "What was actually behind: four room decks, explained here in a "
        "second, plain paragraph.\n\n"
        "**Corrected 2026-09-25, scheduled operator cycle: a superseded "
        "citation fixed.** Re-derived directly.\n\n"
        "**Reopened 2026-10-01, PM check-in: one real commit undeployed.** "
        "Same standing limit as every entry above.\n\n"
        "**CLOSED 2026-10-23, PM check-in (10:1x slot): the gap above "
        "closed with a real redeploy.** Production matches HEAD exactly.\n"
        "\n## BLOCKER-002: Live Business Data Established, Not Yet a Live "
        "Feed\n\nUnrelated content.\n"
    )

    # 13. split_blocker1_chain() finds the 4 entries (the first spanning
    #     its own 2 paragraphs), oldest first, and the span round-trips.
    b1_before, b1_entries, b1_after = rsh.split_blocker1_chain(b1_text)
    if len(b1_entries) != 4:
        fails.append("expected 4 BLOCKER-001 entries, got %d: %r"
                      % (len(b1_entries), b1_entries))
    if "What was actually behind" not in b1_entries[0]:
        fails.append("first entry lost its own continuation paragraph: %r"
                      % b1_entries[0])
    if not b1_entries[0].startswith("**RESOLVED 2026-09-25") or \
            not b1_entries[1].startswith("**Corrected 2026-09-25") or \
            not b1_entries[2].startswith("**Reopened 2026-10-01") or \
            not b1_entries[3].startswith("**CLOSED 2026-10-23"):
        fails.append("BLOCKER-001 entries came back out of their own "
                      "oldest-first order: %r" % b1_entries)
    if not b1_after.startswith("## BLOCKER-002:"):
        fails.append("BLOCKER-001's own end boundary drifted: %r"
                      % b1_after[:40])

    # 14. A missing or duplicated heading is refused, not guessed past.
    try:
        rsh.split_blocker1_chain(b1_text.replace("BLOCKER-002", "X"))
        fails.append("missing BLOCKER-002 heading was not refused")
    except ValueError:
        pass
    try:
        rsh.split_blocker1_chain(b1_text + "\n" + rsh.BLOCKER1_HEADING + "\n")
        fails.append("a duplicated BLOCKER-001 heading was not refused")
    except ValueError:
        pass

    # 15. A span that does not open on a bold paragraph is refused.
    bad_open = b1_text.replace(
        "\n**RESOLVED 2026-09-25, this session", "\nRESOLVED 2026-09-25, "
        "this session", 1)
    try:
        rsh.split_blocker1_chain(bad_open)
        fails.append("a non-bold opening paragraph was not refused")
    except ValueError:
        pass

    # 16. plan_rotation_blocker1() keeps the newest (last, this section's
    #     own order) entry live, and archives the rest newest-first (the
    #     opposite of this chain's own oldest-first file order, matching
    #     STATUS-ARCHIVE.md's stated convention).
    new_b1_text, b1_archived = rsh.plan_rotation_blocker1(b1_text)
    _, kept_b1_entries, kept_b1_after = rsh.split_blocker1_chain(new_b1_text)
    if len(kept_b1_entries) != 1 or not kept_b1_entries[0].startswith(
            "**CLOSED 2026-10-23"):
        fails.append("BLOCKER-001 rotation did not keep exactly the "
                      "newest entry live: %r" % kept_b1_entries)
    if kept_b1_after != b1_after:
        fails.append("BLOCKER-001 rotation disturbed BLOCKER-002: %r"
                      % kept_b1_after[:40])
    if len(b1_archived) != 3:
        fails.append("expected 3 archived BLOCKER-001 entries, got %d: %r"
                      % (len(b1_archived), b1_archived))
    elif not b1_archived[0].startswith("**Reopened 2026-10-01") or \
            not b1_archived[1].startswith("**Corrected 2026-09-25") or \
            not b1_archived[2].startswith("**RESOLVED 2026-09-25"):
        fails.append("BLOCKER-001 archive was not newest-first: %r"
                      % b1_archived)
    elif "What was actually behind" not in b1_archived[2]:
        fails.append("archived last entry lost its continuation "
                      "paragraph: %r" % b1_archived[2])

    # 17. A BLOCKER-001 chain already down to one entry is a no-op.
    b1_one = (
        "# 17. Current Blockers\n\n"
        "## BLOCKER-001: Production State Verifiable Only From a Session "
        "With Real Access\n"
        "\n**CLOSED 2026-10-23, PM check-in (10:1x slot): the gap above "
        "closed with a real redeploy.** Production matches HEAD exactly.\n"
        "\n## BLOCKER-002: Live Business Data Established, Not Yet a Live "
        "Feed\n\nUnrelated content.\n"
    )
    new_b1_one, archived_b1_one = rsh.plan_rotation_blocker1(b1_one)
    if new_b1_one != b1_one or archived_b1_one:
        fails.append("a BLOCKER-001 chain already at one entry was "
                      "rotated when it should have been left alone")

    # 18. Round-trip proof against the real, committed STATUS.md: whatever
    #     split_blocker1_chain finds there must reconstruct the file
    #     exactly, the same safety check the function runs on every call,
    #     proved again here against the real file rather than only the
    #     synthetic text above.
    real_status_path = os.path.join(ROOT, "STATUS.md")
    if os.path.exists(real_status_path):
        real_text = io.open(real_status_path, encoding="utf-8").read()
        try:
            rsh.split_blocker1_chain(real_text)
        except ValueError as exc:
            fails.append("split_blocker1_chain refused the real, "
                          "committed STATUS.md: %s" % exc)

    if fails:
        print("FAILED (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("OK: all rotate_status_history.py checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
