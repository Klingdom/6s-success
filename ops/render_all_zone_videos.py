"""Render every zone video, and count only the files that actually appear.

The first attempt at this was a shell loop that printed "ok" 114 times and
produced one file. Its zone-name parsing collapsed "Entryway   Landing Zone"
to "Zone", every call succeeded in the sense of returning zero, and nothing
checked whether an mp4 had been written. That is the same defect that has cost
this repository more than any other: a run reporting a success it never
observed.

So this counts files on disk before and after each render, and a zone only
counts as done when its file exists and is non-trivial in size.

    python ops/render_all_zone_videos.py            all zones
    python ops/render_all_zone_videos.py --limit 5  first five
"""
from __future__ import annotations

import os
import subprocess
import time
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# --wide renders the 16:9 cut for YouTube into its own directory. The skip
# check must look in the same place the renderer writes, or every zone is
# rendered again on every run.
WIDE = "--wide" in sys.argv
OUT = os.path.join(ROOT, "build", "video",
                   "zones-16x9" if WIDE else "zones")
PY = sys.executable

sys.path.insert(0, os.path.join(ROOT, "ops"))
import video_zone


def zones() -> list:
    """Room, zone-name pairs read straight from video_zone.zones(), the same
    structured source the renderer itself reads, not scraped from its
    formatted --list-all text. The old version split that text on a run of
    2+ spaces, relying on the column being fixed to 18 characters; a room
    name reaching 18 characters or longer would leave only a single space
    before the zone name and silently misparse the pair, the exact
    "collapsed to the last word" shape this file's own docstring already
    names as the costliest defect class here. No room name is that long
    today (longest is Primary Bathroom, 16), so it never fired, but the
    fix is to stop depending on it staying true rather than to widen the
    column again."""
    return [(room, z["zone"]) for room, z in video_zone.zones()]


def mp4s() -> set:
    if not os.path.isdir(OUT):
        return set()
    return {f for f in os.listdir(OUT) if f.endswith(".mp4")
            and os.path.getsize(os.path.join(OUT, f)) > 50_000}


def main() -> int:
    z = zones()
    if "--limit" in sys.argv:
        z = z[:int(sys.argv[sys.argv.index("--limit") + 1])]
    print("  %d zone(s) to render" % len(z))

    made, skipped, failed = 0, 0, []
    slug_of = video_zone.zone_slug

    for room, zone in z:
        # Skip what is already rendered, BEFORE spawning the renderer. Without
        # this the batch re-rendered the first 66 zones on every run and never
        # reached the remaining 48: ten minutes of work, zero new files, and a
        # progress count that never moved.
        done_path = os.path.join(OUT, slug_of(room, zone) + ".mp4")
        if os.path.exists(done_path) and os.path.getsize(done_path) > 50_000:
            skipped += 1
            continue
        before = mp4s()
        # 0xC0000142 (STATUS_DLL_INIT_FAILED) is Windows refusing to start
        # another process because resources are exhausted, not the render
        # being wrong. It appeared 38 times in one run because AVIF encoding
        # was running alongside this, and every one of those zones rendered
        # correctly on a quiet machine. So a transient gets a pause and a
        # second attempt before it is called a failure.
        for attempt in (1, 2, 3):
            p = subprocess.run(
                [PY, os.path.join(ROOT, "ops", "video_zone.py"),
                 "--zone", zone, "--room", room] + (["--wide"] if WIDE else []),
                capture_output=True, text=True, timeout=900)
            if p.returncode != 3221225794:
                break
            print("  retry   %-46s resources exhausted, attempt %d"
                  % (zone[:46], attempt))
            time.sleep(20 * attempt)
        after = mp4s()
        new = after - before
        if new:
            made += 1
            print("  made    %-46s %s" % (zone[:46], list(new)[0]))
        elif len(after) > len(before):
            made += 1
        elif p.returncode == 0 and after == before:
            # The command succeeded and produced nothing new. Either the file
            # already existed, or it silently did nothing. Say which.
            skipped += 1
        else:
            # Record the exit code. An empty stderr with a non-zero exit
            # says nothing, and "failed: 48" with no reason is not a
            # diagnosis, it is a shrug.
            failed.append((zone, "rc=%s out=%r err=%r"
                           % (p.returncode, (p.stdout or "")[-90:],
                              (p.stderr or "")[-90:])))
            print("  FAILED  %-46s" % zone[:46])

    print()
    print("  newly rendered : %d" % made)
    print("  already present or no-op: %d" % skipped)
    print("  failed         : %d" % len(failed))
    print("  mp4 files on disk now: %d" % len(mp4s()))
    for zn, err in failed[:5]:
        print("     %s: %s" % (zn[:40], err.replace("\n", " ")[:110]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
