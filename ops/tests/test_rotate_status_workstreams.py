#!/usr/bin/env python3
"""
Prove ops/rotate_status_workstreams.py moves STATUS.md section 14's
closed Workstream 3 build-log narrative into STATUS-ARCHIVE.md, leaving
only the closure summary and a pointer live, and that it refuses rather
than guesses when the anchors it depends on go missing or duplicate.

Run:  python ops/tests/test_rotate_status_workstreams.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import rotate_status_workstreams as rsw                         # noqa: E402

BEFORE = (
    "## Workstream 3: The diagnostic layer, Sustain depth, and the "
    "Kitchen deck\n\n"
    "**Status:** CLOSED, 2026-10-03. Every item is done or gated.\n"
    "**Owner:** operator\n"
    "**Objective:** build the root-cause diagnostic layer the product "
    "currently lacks, fix the app's first thirty seconds, "
    "and ship the free unillustrated Kitchen deck."
)
AFTER = "\n\n---\n\n# 15. Current Experiments\n\nNo experiment is active.\n"
NARRATIVE = (
    "\n\n**Done:** M1, the frozen 17-cause vocabulary, shipped.\n\n"
    "**Done 2026-09-25:** B9's five room decks shipped."
)


def main() -> int:
    fails = []

    # 1. split_workstream3() finds exactly the narrative between the two
    #    anchors, and before/after reconstruct the original boundaries.
    text = BEFORE + NARRATIVE + AFTER
    before, narrative, after = rsw.split_workstream3(text)
    if "M1, the frozen 17-cause vocabulary" not in narrative:
        fails.append("narrative lost its first entry: %r" % narrative[:80])
    if "B9's five room decks shipped" not in narrative:
        fails.append("narrative lost its last entry: %r" % narrative[-80:])
    if not before.endswith("Kitchen deck."):
        fails.append("before boundary drifted: %r" % before[-40:])
    if not after.startswith("\n\n---\n\n# 15. Current Experiments"):
        fails.append("after boundary drifted: %r" % after[:60])

    # 2. A missing start anchor is refused, not guessed past.
    try:
        rsw.split_workstream3(text.replace("Kitchen deck.", "Kitchen dish."))
        fails.append("missing start anchor was silently accepted")
    except ValueError:
        pass

    # 3. A missing end anchor is refused.
    try:
        rsw.split_workstream3(text.replace("# 15. Current Experiments",
                                            "# 15. Something Else"))
        fails.append("missing end anchor was silently accepted")
    except ValueError:
        pass

    # 4. A duplicated start anchor is refused.
    dup_start = text + "\nand ship the free unillustrated Kitchen deck."
    try:
        rsw.split_workstream3(dup_start)
        fails.append("duplicated start anchor was silently accepted")
    except ValueError:
        pass

    # 5. A duplicated end anchor is refused.
    dup_end = text + "\n\n---\n\n# 15. Current Experiments"
    try:
        rsw.split_workstream3(dup_end)
        fails.append("duplicated end anchor was silently accepted")
    except ValueError:
        pass

    # 6. plan_rotation() replaces the narrative with the pointer and
    #    returns the archived narrative unchanged (verbatim, nothing
    #    reworded).
    new_text, archived = rsw.plan_rotation(text)
    if archived != narrative:
        fails.append("archived narrative was not returned verbatim")
    if "M1, the frozen 17-cause vocabulary" in new_text:
        fails.append("rotated STATUS.md text still carries the archived "
                      "narrative")
    if "Archived 2026-10-24" not in new_text:
        fails.append("rotated STATUS.md text is missing its own pointer")
    if not new_text.startswith(BEFORE):
        fails.append("rotation disturbed the closure summary it must "
                      "keep live")
    if not new_text.endswith(AFTER):
        fails.append("rotation disturbed section 15 that follows it")

    # 7. Already-rotated text (pointer in place, no narrative left) is a
    #    no-op: plan_rotation() returns the text unchanged and no archive.
    already_text, _ = rsw.plan_rotation(text)
    new_again, archived_again = rsw.plan_rotation(already_text)
    if new_again != already_text or archived_again is not None:
        fails.append("an already-rotated file was rotated again")

    # 8. apply_archive() with no existing archive writes a well-formed
    #    archive carrying the narrative under its own dated heading.
    fresh = rsw.apply_archive(narrative, None)
    if not fresh.startswith(rsw.ARCHIVE_HEADER_FIRST_LINE):
        fails.append("fresh archive missing its own header")
    if "M1, the frozen 17-cause vocabulary" not in fresh:
        fails.append("fresh archive lost the narrative")

    # 9. apply_archive() onto an existing archive puts the new block on
    #    top, keeps the old content, and does not touch the header.
    existing = (rsw.ARCHIVE_HEADER_FIRST_LINE + "\n\n> note.\n\n---\n\n"
                "**OLD:** already here.\n")
    combined = rsw.apply_archive(narrative, existing)
    if combined.index("M1, the frozen 17-cause vocabulary") > \
            combined.index("**OLD:** already here."):
        fails.append("new archive block was not placed above old content")
    if "> note." not in combined:
        fails.append("existing archive header was lost on a repeat run")

    # 10. apply_archive() refuses an existing archive file with the
    #     wrong header rather than prepending onto something else.
    try:
        rsw.apply_archive(narrative, "# Something else entirely\n")
        fails.append("a malformed existing archive was silently accepted")
    except ValueError:
        pass

    # 11. The CLI's own `--check`, run for real through main(), must use
    #     the same idempotency rule as plan_rotation(): a file already
    #     carrying just the pointer is CLEAN (exit 0), not DUE (exit 1).
    #     Real bug this cycle: main()'s --check branch tested bare
    #     `if narrative:` and reported DUE forever on an already-rotated
    #     file, because the pointer text itself is a non-empty narrative
    #     between the two anchors; only exercising main() itself, not
    #     just the pure functions it calls, caught it.
    import tempfile
    scratch_dir = tempfile.mkdtemp(prefix="rsw-test-")
    scratch_status = os.path.join(scratch_dir, "STATUS.md")
    scratch_archive = os.path.join(scratch_dir, "STATUS-ARCHIVE.md")
    already_rotated_text, _ = rsw.plan_rotation(text)
    io.open(scratch_status, "w", encoding="utf-8").write(already_rotated_text)
    real_status_path_attr, real_archive_path_attr = (rsw.STATUS_PATH,
                                                       rsw.ARCHIVE_PATH)
    real_argv = sys.argv
    try:
        rsw.STATUS_PATH, rsw.ARCHIVE_PATH = scratch_status, scratch_archive
        sys.argv = ["rotate_status_workstreams.py", "--check"]
        exit_code = rsw.main()
    finally:
        rsw.STATUS_PATH, rsw.ARCHIVE_PATH = (real_status_path_attr,
                                              real_archive_path_attr)
        sys.argv = real_argv
    if exit_code != 0:
        fails.append("main()'s --check reported an already-rotated file "
                      "as DUE (exit %d), not CLEAN" % exit_code)

    # 12. Round-trip proof against the real, committed STATUS.md (before
    #     this cycle's own --apply has run): split_workstream3() must
    #     either find real narrative to rotate, or confirm it has
    #     already been rotated, never raise, against the real file.
    real_status_path = os.path.join(ROOT, "STATUS.md")
    if os.path.exists(real_status_path):
        real_text = io.open(real_status_path, encoding="utf-8").read()
        try:
            rsw.split_workstream3(real_text)
        except ValueError as exc:
            fails.append("split_workstream3 refused the real, committed "
                          "STATUS.md: %s" % exc)

    if fails:
        print("FAILED (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("OK: all rotate_status_workstreams.py checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
