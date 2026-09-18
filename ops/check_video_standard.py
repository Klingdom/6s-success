#!/usr/bin/env python3
"""
Does a rendered zone video still say what the zone's standard says?

WHY THIS EXISTS
---------------
The "What done looks like" checklist inside each video is produced by
video_zone.done_items(). That splitter was wrong twice, and the second fix
landed 2026-09-15. Every narrated video on disk was rendered 7 to 8 September,
before it.

Measured 2026-09-17, not assumed: 100 of the 114 rendered videos show a
checklist that no longer matches the zone's own standard. "One wallet and one
phone per adult" is on screen as "One phone per adult". "A clear stretch of
floor a full stride wide between the door and the rack" stops at "between the
door". Entryway's coat zone loses an item outright.

Twelve of those videos are already public and are OWNER-ACTIONS item 1's known
problem. The other 102 are not published yet, and they are the reason this
file exists: authorising the YouTube upload is meant to be a five minute win,
and without this check it would have published a hundred videos whose on-screen
text contradicts the page they link to. A YouTube video cannot be swapped for a
corrected file without changing its URL, so this is cheap to prevent and
expensive to undo.

WHAT IT COMPARES
----------------
The numbered items in the rendered .srt against video_zone.done_items() for
the same zone, right now. Text only: it cannot see the pixels, so a video
whose captions match but whose frames do not would pass. Said plainly rather
than implied, because "checked" and "checked completely" are different claims.

    python ops/check_video_standard.py            report every zone
    python ops/check_video_standard.py --stale    list the stale slugs only
"""
from __future__ import annotations

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
NARRATED = os.path.join(ROOT, "build", "video", "zones-narrated")

def blocks(text: str):
    """(index, text) for every subtitle block, each block's lines joined.

    An SRT block is an index line, a timing line, then one or more text lines.
    The text of a single checklist item is wrapped across those lines by the
    renderer, so anything that reads line by line sees "Hats and gloves
    together in a single" and stops. The first version of this file did
    exactly that and would have held back correctly re-rendered videos for
    ever, which is the failure mode a guard must not have.
    """
    out = []
    for raw in re.split(r"\r?\n\r?\n", text):
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        out.append((lines[0], " ".join(lines[2:]).strip()))
    return out


def stem_for(room: str, zone: str) -> str:
    """The one filename stem every zone-video writer and reader must agree
    on: video_zone.zone_slug(), not a local reimplementation.

    Found 2026-09-18. This file used to build the stem itself with its own
    regex-based slug(), the exact single-source-of-truth gap
    gate_video_slug_single_source already exists to catch and had already
    fixed twice (video_narrated.py's dead hasattr fallback,
    render_all_narrated.py's own copy), except that gate only checks those
    two files by name, so a third reimplementation added after it went
    unseen. Proved live on a synthetic case rather than assumed: for a zone
    named "Coats & Boots", video_zone.zone_slug() keeps the "&"
    ("kids-room--coats-&-boots") while the old local slug() collapsed it
    away ("kids-room--coats-boots"). The two agreed on all 114 real zone
    names today only because none currently contains "&" or similar
    punctuation, the identical coincidental-agreement trap the sibling
    gate's own docstring describes. A real divergence would have made
    ops/youtube_upload.py's stale-video hold-back silently match nothing,
    the one guard standing between a corrected re-render and a 102-video
    batch upload with the wrong captions and no way to swap the file after.
    """
    import video_zone as V
    return V.zone_slug(room, zone)


def rendered_segment(srt_path: str) -> str:
    """The checklist part of the captions, as one normalised string.

    Rewritten 2026-09-18, after the first version called 88 correctly
    re-rendered videos stale. It read the numbered items as one caption block
    each, and neither assumption survives contact with real narration:

      - a long item is split across several caption blocks, so the parser
        captured "... one named category and you can see the" and reported the
        rest missing;
      - the "+ N more on the zone page" line lands inside the last block, so
        the item came back as "Umbrellas standing in the stand + 1 more on the
        zone page" and failed an equality test.

    Both are the checker being naive about captions, not the video being
    wrong, and a guard that cries wolf on correct work is worse than none: it
    would have held every re-rendered video back from YouTube for ever.

    Comparing normalised text rather than parsed items keeps what matters. The
    defect this exists to catch DROPS WORDS ("One wallet and one phone per
    adult" became "One phone per adult"), and a dropped word still fails a
    substring test.
    """
    if not os.path.exists(srt_path):
        return ""
    text = io.open(srt_path, encoding="utf-8", errors="replace").read()
    body = []
    for _idx, chunk in blocks(text):
        body.append(chunk)
    joined = " ".join(body)
    m = re.search(r"What done looks like(.*?)(?:One session|The call|$)",
                  joined, re.S | re.I)
    seg = m.group(1) if m else ""
    return " ".join(seg.split())


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split())


def compare():
    """(stale, fresh, unreadable) lists of (stem, current, rendered)."""
    import video_zone as V
    stale, fresh, unreadable = [], [], []
    for room, z in V.zones():
        stem = stem_for(room, z["zone"])
        # The wide file is the one ops/youtube_upload.py posts, so it is the
        # one that decides whether publishing is safe. The vertical render is
        # only consulted when no wide caption exists.
        wide = os.path.join(NARRATED, stem + "-16x9.srt")
        srt_used = (wide if os.path.exists(wide)
                    else os.path.join(NARRATED, stem + ".srt"))
        current = [c.rstrip(".") for c in V.done_items(z)]
        expected = current[:4]
        seg = norm(rendered_segment(srt_used))
        if not seg:
            unreadable.append((stem, current, []))
            continue
        missing = [item for item in expected if norm(item) not in seg]
        if missing:
            stale.append((stem, current, ["MISSING: " + missing[0][:60]]))
        elif len(current) > 4 and ("%d more on the zone page"
                                   % (len(current) - 4)) not in seg:
            stale.append((stem, current, ["(no '+ N more' line)"]))
        else:
            fresh.append((stem, current, expected))
    return stale, fresh, unreadable


def main() -> int:
    stale, fresh, unreadable = compare()
    if "--stale" in sys.argv:
        for stem, _, _ in stale:
            print(stem)
        return 1 if stale else 0
    print("  videos compared     %d" % (len(stale) + len(fresh) + len(unreadable)))
    print("  match the standard  %d" % len(fresh))
    print("  STALE               %d" % len(stale))
    print("  no readable list    %d" % len(unreadable))
    for stem, cur, got in stale[:3]:
        print("\n    %s" % stem)
        print("      standard: %s" % cur[:4])
        print("      video   : %s" % got[:4])
    if stale:
        print("\n  These must be re-rendered before they are uploaded. Captions "
              "only were compared; the frames were not read.")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
