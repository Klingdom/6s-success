#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_youtube_sustain_anchor() catches a zone video
description that drops, or mis-slugs, the "#sustain" link description_for()
(ops/build_youtube_metadata.py) now writes for every zone with a real
Sustain pass. Added 2026-09-13 alongside the section it protects
(PLAN-MICROZONES-DECKS-APP.md's S5): the drift signal is useless if it is
only on a page, and the gate is the only thing that can tell whether the
generator still says so in the one channel that already has an audience.

Run:  python ops/tests/test_gate_youtube_sustain_anchor.py
"""
import glob
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bz                                  # noqa: E402
import video_zone                                               # noqa: E402

ROOM, ZONE = "Entryway", "Landing Zone"
SLUG = video_zone.zone_slug(ROOM, ZONE)
GOOD_URL = "https://6s-success.com/zones/%s-%s.html#sustain" % (
    bz.slug(ROOM), bz.slug(bz.display(ROOM, ZONE)))


def _run(yt_files):
    tmp = tempfile.mkdtemp()
    try:
        yt_dir = os.path.join(tmp, "build", "video", "youtube")
        os.makedirs(yt_dir)
        for name, meta in yt_files.items():
            io.open(os.path.join(yt_dir, name), "w", encoding="utf-8").write(
                json.dumps(meta))

        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_youtube_sustain_anchor()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. No build/video/youtube directory at all: silent, gate_zone_name_
    #    consistency already owns that warning.
    tmp = tempfile.mkdtemp()
    try:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_youtube_sustain_anchor()
            if preflight.FAIL or preflight.WARN:
                fails.append("missing yt dir should be silent here: %r/%r"
                             % (preflight.FAIL, preflight.WARN))
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)

    # 2. Correct metadata: no failure.
    good = {"description": "This is The Landing Spot in the Entryway.\n\n"
                            "KEEP IT THIS WAY\nThe Sustain habit:\n%s\n"
                            % GOOD_URL}
    f, _ = _run({SLUG + ".json": good})
    if f:
        fails.append("correct metadata wrongly flagged: %r" % (f,))

    # 3. The anchor is missing entirely: caught by name.
    missing = {"description": "This is The Landing Spot in the Entryway.\n"
                               "Full written steps: https://6s-success.com/"
                               "zones/entryway-the-landing-spot.html\n"}
    f, _ = _run({SLUG + ".json": missing})
    if not f or not any(SLUG in msg for _, msg in f):
        fails.append("missing-anchor regression not caught: %r" % (f,))

    # 4. The anchor points at the wrong slug: caught by name, distinctly
    #    from the missing case.
    wrong = {"description": "This is The Landing Spot in the Entryway.\n"
                             "KEEP IT THIS WAY\nThe Sustain habit:\n"
                             "https://6s-success.com/zones/"
                             "entryway-the-wrong-zone.html#sustain\n"}
    f, _ = _run({SLUG + ".json": wrong})
    if not f or not any(SLUG in msg for _, msg in f):
        fails.append("wrong-slug regression not caught: %r" % (f,))
    if f and "does not match" not in f[0][1]:
        fails.append("wrong-slug case should say so, not read as missing: %r"
                      % (f,))

    # 5. A zone with no sustain pass at all is never required to carry the
    #    anchor (skip, not caught as missing). Fabricate one that cannot
    #    collide with a real zone slug.
    class _FakeZones:
        @staticmethod
        def zones():
            return [("Entryway", {"zone": "Landing Zone", "passes": {}})]
    old_zones = video_zone.zones
    video_zone.zones = _FakeZones.zones
    try:
        f, _ = _run({SLUG + ".json": missing})
        if f:
            fails.append("a zone with no sustain pass should not be "
                         "required to carry the anchor: %r" % (f,))
    finally:
        video_zone.zones = old_zones

    # 6. The real, committed corpus: clean.
    real_yt = sorted(glob.glob(os.path.join(ROOT, "build", "video", "youtube",
                                             "*.json")))
    if len(real_yt) < 100:
        print("  (skipped: fewer than 100 real build/video/youtube/*.json "
              "found on disk)")
    else:
        old_fail, old_warn = preflight.FAIL, preflight.WARN
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_youtube_sustain_anchor()
            if preflight.FAIL:
                fails.append("real committed corpus FAILed: %r"
                             % (preflight.FAIL,))
        finally:
            preflight.FAIL, preflight.WARN = old_fail, old_warn

    if fails:
        print("FAIL")
        for f_ in fails:
            print("  - " + f_)
        return 1
    print("PASS (6 cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
