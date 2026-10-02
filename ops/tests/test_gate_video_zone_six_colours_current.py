#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_video_zone_six_colours_current() catches
ops/video_zone.py's SIX disagreeing with site.css's --s1..--s6.

Found 2026-10-02, second-pass cold-reading the 2026-09-26-dated ops/*.py
tier (ops/cold_read_ledger.py) per CLAUDE.md step 5d. SIX paired four of
the six passes with the wrong S's colour and invented two colours that do
not exist in the real palette at all (one was site.css's unrelated
--slate, the other appears nowhere in site.css). Every one of the 114 zone
videos renders its progress spine from SIX, so this would have shipped
silently on the next full re-render. Fixed by correcting SIX to match
site.css's --s1..--s6 exactly; this gate is what stops it drifting again.

Run:  python ops/tests/test_gate_video_zone_six_colours_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import video_zone                                              # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_video_zone_six_colours_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    orig_six = list(video_zone.SIX)

    # 1. The real committed state must pass clean.
    r, w = _run()
    if r:
        fails.append("the real committed SIX failed: %r" % (r,))

    # 2. The actual regression shape found 2026-10-02: an off-by-one
    #    rotation plus two invented colours.
    video_zone.SIX = [("Sort", "#BC4B2A"), ("Straighten", "#DDA63A"),
                       ("Shine", "#4E7A57"), ("Safety", "#CB4B36"),
                       ("Standardize", "#3C5A6B"), ("Sustain", "#6E5B8B")]
    r, w = _run()
    if not r or r[0][0] != "video-zone-six-colours-current":
        fails.append("the real historical defect shape was not caught: %r" % (r,))
    elif "Sort" not in r[0][1] or "#CB4B36" not in r[0][1]:
        fails.append("failure message did not name the real expected "
                      "colour: %r" % (r[0][1],))
    video_zone.SIX = orig_six

    # 3. A single wrong entry (not a full rotation) must also be caught.
    video_zone.SIX = [(n, "#000000" if n == "Sustain" else c) for n, c in orig_six]
    r, w = _run()
    if not r or r[0][0] != "video-zone-six-colours-current":
        fails.append("a single wrong colour was not caught: %r" % (r,))
    elif "Sustain" not in r[0][1]:
        fails.append("failure message did not name the wrong pass: %r" % (r[0][1],))
    video_zone.SIX = orig_six

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_video_zone_six_colours_current, 3/3 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
