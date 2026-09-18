#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_srt_captions_current() catches a caption
sidecar drifting from the beats() its own video renders from, and that it
does so in an environment with zero local .mp4 files, the shape every
cloud run and this sandbox are actually in.

Found 2026-09-18: the previous version gated the whole check on at least
one build/video/zones/*.mp4 existing locally ("if not have_mp4: return").
The .mp4s are gitignored and never present outside a machine that has run
the video renderer, so the check had silently no-op'd in every environment
it has ever been run in since it was written, the same "a gate that cannot
fail is theatre" shape gate_deck_count already found and fixed for
build/cards-rendered/*.png. Proof it was not theoretical: fixing the gate
to check the 114 committed .srt files directly (present in every
environment) immediately found 16 of them had drifted from live beats()
output, real content changes nobody had re-run ops/video_srt.py to pick up.

Run:  python ops/tests/test_gate_srt_captions_current.py
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import video_srt                                               # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_srt_captions_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []

    # 0. Check #1 below is meant to prove the gate runs with no .mp4 beside
    #    the captions, which is every CI checkout. On the machine that
    #    actually renders the videos they are all present, and that is the
    #    normal state there, not a fault: failing on it made this test
    #    unrunnable on the one machine where the corpus is produced.
    #
    #    Corrected 2026-09-18: say the sub-case was not exercised, and carry
    #    on with the rest. Reporting "unchecked" is the honest move; failing
    #    on a healthy machine teaches people to ignore the suite.
    mp4s = [f for f in os.listdir(video_srt.OUT) if f.endswith(".mp4")]
    if mp4s:
        print("  UNCHECKED: %d local .mp4(s) present, so check #1 does not "
              "prove the mp4-free path here. Run this where the videos have "
              "not been rendered to exercise it." % len(mp4s))

    # 1. The real, committed captions: clean.
    f, w = _run()
    if f:
        fails.append("the real committed .srt corpus failed: %r" % (f,))

    # 2. A stale caption (hand-edited, no longer matching beats()) must fail,
    #    named by its own slug.
    target = os.path.join(video_srt.OUT, "entryway--coat-and-outerwear-zone.srt")
    backup = target + ".bak"
    shutil.copy2(target, backup)
    try:
        real = io.open(target, encoding="utf-8").read()
        stale = real.replace("One coat per person", "One coat per ghost")
        io.open(target, "w", encoding="utf-8", newline="").write(stale)
        f, w = _run()
        if not f or "srt-captions-current" not in f[0][0]:
            fails.append("a stale, hand-edited caption was not caught: %r"
                          % (f,))
        elif "entryway--coat-and-outerwear-zone" not in f[0][1]:
            fails.append("the stale caption was caught but not named: %r"
                          % (f[0][1],))
    finally:
        shutil.copy2(backup, target)
        os.remove(backup)

    # 3. A missing caption must fail as "(missing)", not silently skip.
    moved = target + ".moved"
    os.rename(target, moved)
    try:
        f, w = _run()
        if not f or "(missing)" not in f[0][1]:
            fails.append("a missing caption file was not caught: %r" % (f,))
    finally:
        os.rename(moved, target)

    # 4. Re-verify the real corpus is clean after both drift tests, not left
    #    dirty by the swap/move above.
    f, w = _run()
    if f:
        fails.append("the real .srt corpus was left dirty after the drift "
                      "tests: %r" % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print("  " + x)
        return 1
    print("PASS  4 of 4 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
