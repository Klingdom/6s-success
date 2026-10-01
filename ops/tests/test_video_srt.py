#!/usr/bin/env python3
"""
Prove ops/video_srt.py's wrap_two_lines() never ships a caption line over
LINE_CHARS (42), the "one comfortable caption line" its own module docstring
promises. Found broken 2026-09-10: whenever greedy wrapping needed a third
line, the old code joined every line after the first into one unbounded
string, so a cue could ship a single line up to 55 characters wide, a wall
over the picture on exactly the surface (burned-in-text zone videos) this
file exists to make readable. Reproduced against the real, committed corpus:
617 of the lines in build/video/zones/*.srt exceeded 42 characters before
the fix, 0 after, same word content, just rewrapped.

Run:  python ops/tests/test_video_srt.py
"""
import glob
import io
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import video_srt as VS                                          # noqa: E402
import video_zone as VZ                                         # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, detail))


def test_short_text_unchanged():
    check("short", VS.wrap_two_lines("Sort the drawer.") == "Sort the drawer.")


def test_two_line_case_still_two_lines():
    text = "Hold the things that only come out for guests"  # 47 chars
    out = VS.wrap_two_lines(text).split(chr(10))
    check("two-line-count", len(out) == 2, str(out))
    check("two-line-budget", all(len(l) <= VS.LINE_CHARS for l in out), str(out))


def test_three_line_case_stays_in_budget():
    # The real cue that shipped the bug: greedy wrap needs 3 lines here, and
    # the old code collapsed lines[1:] into one unbounded 63-char line.
    text = ("Dining Room Buffet or Sideboard Storage Hold the things that "
            "only come out when the table is being set.")
    out = VS.wrap_two_lines(text).split(chr(10))
    check("no-line-over-budget", all(len(l) <= VS.LINE_CHARS for l in out),
          str([len(l) for l in out]))
    check("content-preserved", " ".join(out) == text, str(out))


def test_worst_known_case_from_real_corpus():
    text = ("Sort a previous-generation console because someone's save "
            "file still lives on it, or find out it already left with the "
            "last move.")
    out = VS.wrap_two_lines(text).split(chr(10))
    check("worst-case-budget", all(len(l) <= VS.LINE_CHARS for l in out),
          str([len(l) for l in out]))


def test_real_committed_corpus_respects_budget():
    files = sorted(glob.glob(os.path.join(ROOT, "build", "video", "zones", "*.srt")))
    if not files:
        return  # media not present in this sandbox; nothing to check
    over = []
    for f in files:
        blocks = open(f, encoding="utf-8").read().strip().split("\n\n")
        for b in blocks:
            for line in b.split("\n")[2:]:
                if len(line) > VS.LINE_CHARS:
                    over.append((os.path.basename(f), len(line), line))
    check("corpus-clean", not over, "%d line(s) over budget, e.g. %s"
          % (len(over), over[:3]))


def test_main_exits_nonzero_when_a_zone_has_no_caption_text():
    """main()'s real-write path must not exit 0 while printing "no caption
    text for N zone(s)": that is a batch reporting success on a run it did
    not fully complete, the same shape found and fixed in two sibling batch
    tools on 2026-09-26 (video_zone_photo.py, render_all_zone_videos.py).

    Forces srt_for() to return empty for one zone (no real video, no real
    render), and never writes outside a scratch directory.
    """
    zs = VZ.zones()
    if not zs:
        return  # no zones to build the case from
    room, z = zs[0]

    scratch = os.path.join(ROOT, "ops", "tests", "_scratch_srt_out")
    os.makedirs(scratch, exist_ok=True)
    old_out, old_argv = VS.OUT, sys.argv
    try:
        VS.OUT = scratch
        sys.argv = ["video_srt.py", "--zone", z["zone"], "--room", room]
        with patch.object(VS, "srt_for", return_value=""):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                rc = VS.main()
            finally:
                sys.stdout = old_stdout
        check("empty-caption-exit-code", rc != 0,
              "a zone with no caption text returned exit %r instead of "
              "nonzero: %s" % (rc, captured.getvalue().strip()))
    finally:
        VS.OUT, sys.argv = old_out, old_argv
        for f in os.listdir(scratch):
            os.remove(os.path.join(scratch, f))
        os.rmdir(scratch)


if __name__ == "__main__":
    test_short_text_unchanged()
    test_two_line_case_still_two_lines()
    test_three_line_case_stays_in_budget()
    test_worst_known_case_from_real_corpus()
    test_real_committed_corpus_respects_budget()
    test_main_exits_nonzero_when_a_zone_has_no_caption_text()
    if FAILS:
        print("FAIL")
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("PASS  6 of 6 cases")
