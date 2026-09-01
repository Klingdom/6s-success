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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "video", "zones")
PY = sys.executable


def zones() -> list:
    """Zone names from --list, split on the run of spaces, not the last word."""
    p = subprocess.run([PY, os.path.join(ROOT, "ops", "video_zone.py"), "--list"],
                       capture_output=True, text=True, timeout=180)
    out = []
    for line in p.stdout.split("\n")[1:]:
        if not line.strip():
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
    for room, zone in z:
        before = mp4s()
        p = subprocess.run(
            [PY, os.path.join(ROOT, "ops", "video_zone.py"), "--zone", zone],
            capture_output=True, text=True, timeout=900)
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
            failed.append((zone, (p.stderr or p.stdout)[-160:]))
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
