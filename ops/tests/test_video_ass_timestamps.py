#!/usr/bin/env python3
"""
Prove ops/video.py's build_ass() never emits an invalid ASS timestamp at a
minute boundary.

Found 2026-09-21: the karaoke-caption timestamp helper computed seconds as a
float (t % 60) and formatted it with %05.2f. Formatting rounds independently
of the earlier floor division into hours and minutes, so any phrase whose
start or end landed within about 5ms of a whole minute produced a string
like "0:00:60.00" instead of "0:01:00.00" - not a valid ASS timestamp. Every
video rendered through this module (video_zone.py, video_zone_photo.py) uses
build_ass() for its burned-in captions, so a phrase boundary anywhere near a
minute mark corrupted that caption's timing.

Run:  python ops/tests/test_video_ass_timestamps.py
"""
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import video as V                                                # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, detail))


def _timestamps(path):
    text = open(path, encoding="utf-8").read()
    out = []
    for line in text.splitlines():
        if line.startswith("Dialogue:"):
            fields = line.split(",", 9)
            out.append(fields[1])  # Start
            out.append(fields[2])  # End
    return out


def test_no_timestamp_hits_sixty_seconds():
    # The exact failure shape: an end time 4ms short of a whole minute.
    with tempfile.TemporaryDirectory() as d:
        path = V.build_ass([(0.0, 59.999, "the drawer is finally empty")],
                            os.path.join(d, "case1.ass"))
        stamps = _timestamps(path)
        check("case1-no-sixty", all(":60." not in s for s in stamps), stamps)
        check("case1-rolled-over", "0:01:00.00" in stamps, stamps)


def test_hour_boundary_also_rolls_over():
    with tempfile.TemporaryDirectory() as d:
        path = V.build_ass([(3599.0, 3599.997, "one more second")],
                            os.path.join(d, "case2.ass"))
        stamps = _timestamps(path)
        check("case2-no-sixty", all(":60." not in s for s in stamps), stamps)
        check("case2-rolled-over", "1:00:00.00" in stamps, stamps)


def test_ordinary_timestamps_unaffected():
    with tempfile.TemporaryDirectory() as d:
        path = V.build_ass([(0.0, 3.2, "sort the mail"), (3.2, 7.5, "then the keys")],
                            os.path.join(d, "case3.ass"))
        stamps = _timestamps(path)
        check("case3-start", stamps[0] == "0:00:00.00", stamps)
        check("case3-mid", "0:00:03.20" in stamps, stamps)
        check("case3-end", stamps[-1] == "0:00:07.50", stamps)


if __name__ == "__main__":
    test_no_timestamp_hits_sixty_seconds()
    test_hour_boundary_also_rolls_over()
    test_ordinary_timestamps_unaffected()
    if FAILS:
        print("FAIL")
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("PASS  3 of 3 cases")
