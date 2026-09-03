"""Render every zone video with narration, in both orientations.

228 outputs: 114 vertical for Shorts and Reels, 114 wide for YouTube, each with
a voice track and a caption file timed to that voice.

Skips before spawning, not after. An earlier silent batch spent ten minutes
producing nothing because it invoked the renderer for zones already done and
classified them afterwards, so the machine looked busy and the count never
moved.

Entryway first by default. It is the room being published, and a batch that
runs for hours should deliver what is needed next in its first minutes rather
than its last.

    python ops/render_all_narrated.py --room Entryway
    python ops/render_all_narrated.py            all rooms, Entryway first
    python ops/render_all_narrated.py --check    coverage only
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
OUT = os.path.join(ROOT, "build", "video", "zones-narrated")
PY = sys.executable
FIRST = "Entryway"


def slug(room: str, zone: str) -> str:
    import video_zone as vz
    return vz.zone_slug(room, zone)


def done(room: str, zone: str, wide: bool) -> bool:
    p = os.path.join(OUT, slug(room, zone) + ("-16x9" if wide else "") + ".mp4")
    # A file that exists but is tiny is a failed render, not a finished one.
    return os.path.exists(p) and os.path.getsize(p) > 200_000


def main() -> int:
    import video_zone as vz
    zs = vz.zones()
    want_room = (sys.argv[sys.argv.index("--room") + 1]
                 if "--room" in sys.argv else None)
    if want_room:
        zs = [(r, z) for r, z in zs if r == want_room]
    else:
        zs = ([(r, z) for r, z in zs if r == FIRST]
              + [(r, z) for r, z in zs if r != FIRST])

    jobs = [(r, z, w) for r, z in zs for w in (True, False)]

    if "--check" in sys.argv:
        have = len([f for f in os.listdir(OUT) if f.endswith(".mp4")]) \
            if os.path.isdir(OUT) else 0
        print("  narrated videos: %d of %d" % (have, len(jobs)))
        return 0 if have >= len(jobs) else 1

    made, skipped, failed = 0, 0, []
    t0 = time.time()
    for room, z, wide in jobs:
        if done(room, z["zone"], wide):
            skipped += 1
            continue
        cmd = [PY, os.path.join(ROOT, "ops", "video_narrated.py"),
               "--zone", z["zone"], "--room", room]
        if wide:
            cmd.append("--wide")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
            err = (p.stderr or p.stdout)[-160:].replace("\n", " ")
        except subprocess.TimeoutExpired:
            err = "timed out"
        if done(room, z["zone"], wide):
            made += 1
            print("  made  %-46s %s" % (slug(room, z["zone"])[:46],
                                        "16x9" if wide else "9x16"))
        else:
            # Record the reason. An earlier batch reported "failed: 38" with
            # empty stderr, which told me nothing and cost a whole cycle.
            failed.append((slug(room, z["zone"]), wide, err))
            print("  FAIL  %-46s %s" % (slug(room, z["zone"])[:46],
                                        "16x9" if wide else "9x16"))

    mins = (time.time() - t0) / 60
    print()
    print("  newly rendered : %d" % made)
    print("  already present: %d" % skipped)
    print("  failed         : %d" % len(failed))
    print("  on disk now    : %d of %d"
          % (len([f for f in os.listdir(OUT) if f.endswith(".mp4")])
             if os.path.isdir(OUT) else 0, len(jobs)))
    print("  elapsed        : %.1f min" % mins)
    for s, w, e in failed[:5]:
        print("     %s %s: %s" % (s, "16x9" if w else "9x16", e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
