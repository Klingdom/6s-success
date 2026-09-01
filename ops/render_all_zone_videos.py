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
import re
import subprocess
import time
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "video", "zones")
PY = sys.executable


def zones() -> list:
    """Zone names from --list, split on the run of spaces, not the last word."""
    # --list-all, not --list. --list prints "114 zones" and then shows six of
    # them, which reads as the whole list and is not. Driving a batch from it
    # rendered six zones and reported completion.
    p = subprocess.run([PY, os.path.join(ROOT, "ops", "video_zone.py"),
                        "--list-all"], capture_output=True, text=True,
                       timeout=300)
    out = []
    for line in p.stdout.split("\n")[1:]:
        if not line.strip():
            continue
        if line.strip().startswith("..."):
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 2:
            out.append((parts[0], parts[-1]))
    return out


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
    def slug_of(room: str, zone: str) -> str:
        # Must match video_zone.py exactly, or the skip check looks at the
        # wrong filename and every zone gets re-rendered. Room first, because
        # three zone names repeat across rooms.
        def one(t):
            return t.lower().replace(" ", "-").replace(",", "").replace("/", "-")
        return "%s--%s" % (one(room), one(zone))

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
                 "--zone", zone, "--room", room],
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
