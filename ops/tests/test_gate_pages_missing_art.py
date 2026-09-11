#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_pages_missing_art() detects a missing ZONE
HERO specifically, not merely the absence of any <img> tag on the page.

Found 2026-09-11: withdrawing the kitchen--primary-prep-counter hero (a
real content defect: the approved image contradicted the zone's own
done_looks_like, see ops/hero-verdicts.json) left that page with no hero
but still one <img>, its "Watch this zone" video thumbnail, because it is
one of the 12 zones with a published video. The old check, "no <img\b
anywhere on the page", went on reporting the page as pictured, undercounting
the exact thing this gate's own docstring says it measures ("zones whose
hero was rejected") the day that measure first became untrue for any zone
with both a rejected hero and a published video.

Run:  python ops/tests/test_gate_pages_missing_art.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                  # noqa: E402

HERO_FIGURE = (
    '<figure class="zone-hero" id="zone-hero">'
    '<img src="../assets/zones/x-lg.jpg" alt=""></figure>'
)
VIDEO_IMG = (
    '<button class="video-play"><img src="../assets/img/video/x.png" '
    'alt="" loading="lazy"></button>'
)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def run(zone_pages, room_pages):
    tmp_dir = tempfile.mkdtemp()
    try:
        for name, body in zone_pages.items():
            write(os.path.join(tmp_dir, "site", "zones", name),
                  "<html><body>" + body + "</body></html>")
        for name, body in room_pages.items():
            write(os.path.join(tmp_dir, "site", "rooms", name),
                  "<html><body>" + body + "</body></html>")
        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.WARN)
        try:
            preflight.gate_pages_missing_art()
        finally:
            preflight.ROOT = real_root
        return preflight.WARN[before:]
    finally:
        shutil.rmtree(tmp_dir)


def main():
    fails = []

    # Case 1: a zone page has a hero AND an unrelated video thumbnail.
    # Must NOT be counted as missing art.
    w = run({"has-hero.html": "<p>Intro</p>" + HERO_FIGURE + VIDEO_IMG,
              "index.html": "<p>ignored</p>"}, {})
    msg = " ".join(m for _, m in w)
    if "has-hero" in msg:
        fails.append("a zone with a real hero and a video thumbnail was "
                      "wrongly counted as missing art")

    # Case 2: the real regression. No hero, but a video thumbnail <img> IS
    # present. Old code (bare = no <img\b anywhere) missed this.
    w = run({"rejected-but-has-video.html": "<p>Intro</p>" + VIDEO_IMG}, {})
    msg = " ".join(m for _, m in w)
    if "rejected-but-has-video" not in msg:
        fails.append("a zone with a rejected hero but a video thumbnail "
                      "was not counted as missing art")

    # Case 3: no hero, no image at all (the shape all 7 previously-known
    # rejected zones have). Must still be caught, matching old behavior.
    w = run({"no-picture-at-all.html": "<p>Intro</p><h2>More</h2>"}, {})
    msg = " ".join(m for _, m in w)
    if "no-picture-at-all" not in msg:
        fails.append("a zone with no picture at all was not counted as "
                      "missing art")

    # Case 4: room pages keep the old, unchanged behavior (any <img> counts,
    # since rooms have no per-zone hero marker at all).
    w = run({}, {"room-with-plain-img.html": "<p>Intro</p>"
                 '<img src="x.jpg" alt="">',
                 "room-with-nothing.html": "<p>Intro</p>"})
    msg = " ".join(m for _, m in w)
    if "room-with-plain-img" in msg:
        fails.append("a room page with a plain <img> was wrongly counted "
                      "as missing art (room behavior regressed)")
    if "room-with-nothing" not in msg:
        fails.append("a room page with no image at all was not counted as "
                      "missing art (room behavior regressed)")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 4 case(s), zone pages are checked for the hero figure "
          "specifically, a video thumbnail no longer masks a rejected "
          "hero, and room-page behavior is unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
