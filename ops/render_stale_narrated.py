"""Re-render exactly the narrated zone videos whose captions no longer match
content.json's own standard.

ops/check_video_standard.py already knows which zones are stale (its
`compare()` is the one place that walks every zone's rendered .srt against
`video_zone.done_items()` right now); this script never re-derives that
match, the exact single-source-of-truth gap this corpus has hit three times
already (video_narrated.py's dead slug fallback, render_all_narrated.py's own
copy, and check_video_standard.py's own first draft, named in its own
stem_for() docstring). It only adds the next step: for every stale zone, call
the real renderer, in both orientations, since the stale text is the same
`done_items()` call feeding both.

BACKLOG-2026-09-07.md's C7 "second wave" row named this fully: the
2026-10-02 British-to-American dialect fix in content.json landed after the
2026-09-20 full re-render, so 15 of 114 zones' captions still read
labelled/tyre against the page's own labeled/tire. Not customer-facing;
ops/youtube_upload.py already withholds anything check_video_standard.py
calls stale.

Needs edge-tts (to reach speech.platform.bing.com) and ffmpeg, neither
reachable from the cloud sandbox's egress proxy (confirmed directly:
video_narrated.py fails with a DNS-level connection failure to that host
specifically). Meant to run on a GitHub-hosted runner,
.github/workflows/render-narrated-videos.yml, the same shape
keyword_demand.py and indexation_check.py already use for the identical
sandbox-egress gap.

    python ops/render_stale_narrated.py           render every stale pair
    python ops/render_stale_narrated.py --check   report only, exit 1 if any
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
PY = sys.executable


def stale_pairs() -> list[tuple[str, str, str]]:
    """[(stem, room, zone)] for every zone whose rendered captions disagree
    with content.json's own standard right now."""
    import check_video_standard as cvs
    import video_zone as vz

    stale, _fresh, _unreadable = cvs.compare()
    stems = {stem for stem, _cur, _got in stale}
    if not stems:
        return []
    by_stem = {vz.zone_slug(room, z["zone"]): (room, z["zone"])
               for room, z in vz.zones()}
    return [(stem,) + by_stem[stem] for stem in sorted(stems) if stem in by_stem]


def main() -> int:
    pairs = stale_pairs()

    if "--check" in sys.argv:
        print("  stale narrated videos: %d" % len(pairs))
        for stem, _room, _zone in pairs:
            print("    %s" % stem)
        return 1 if pairs else 0

    if not pairs:
        print("  nothing stale, nothing to render")
        return 0

    failed = []
    for stem, room, zone in pairs:
        for wide in (True, False):
            cmd = [PY, os.path.join(ROOT, "ops", "video_narrated.py"),
                   "--zone", zone, "--room", room]
            if wide:
                cmd.append("--wide")
            print("  rendering %-46s %s" % (stem, "16x9" if wide else "9x16"))
            r = subprocess.run(cmd)
            if r.returncode != 0:
                failed.append((stem, wide))

    print()
    print("  re-rendered : %d of %d pairs" % (len(pairs) - len(failed), len(pairs)))
    print("  failed      : %d" % len(failed))
    for stem, wide in failed:
        print("     FAIL %s %s" % (stem, "16x9" if wide else "9x16"))

    # Trust the real artifact, not the subprocess exit code: re-run the same
    # comparison a second time rather than assume a 0 return means the SRT
    # now agrees with the standard.
    remaining = stale_pairs()
    if remaining:
        print("  still stale after render: %d (%s)"
              % (len(remaining), ", ".join(s for s, _, _ in remaining)))

    return 1 if (failed or remaining) else 0


if __name__ == "__main__":
    sys.exit(main())
