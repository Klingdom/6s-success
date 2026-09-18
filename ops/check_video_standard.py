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


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def rendered_items(srt_path: str) -> list:
    """The numbered checklist as the video's own captions carry it.

    The renderer numbers each item ("1 One coat per person on the rail") and
    the list follows the "What done looks like" title card, so items are the
    numbered blocks after that card and before the next unnumbered one.
    """
    if not os.path.exists(srt_path):
        return []
    text = io.open(srt_path, encoding="utf-8", errors="replace").read()
    seen_title, items = False, []
    for _idx, body in blocks(text):
        if not seen_title:
            if body.lower().startswith("what done looks like"):
                seen_title = True
            continue
        m = re.match(r"^(\d+)\s+(.+)$", body)
        if not m:
            break
        if int(m.group(1)) != len(items) + 1:
            break
        items.append(m.group(2).strip().rstrip("."))
    return items


def compare():
    """(stale, fresh, unreadable) lists of (stem, current, rendered)."""
    import video_zone as V
    stale, fresh, unreadable = [], [], []
    for room, z in V.zones():
        stem = "%s--%s" % (slug(room), slug(z["zone"]))
        # The wide file is the one ops/youtube_upload.py posts, so it is the
        # one that decides whether publishing is safe. The vertical render is
        # only consulted when no wide caption exists.
        wide = os.path.join(NARRATED, stem + "-16x9.srt")
        got = rendered_items(wide if os.path.exists(wide)
                             else os.path.join(NARRATED, stem + ".srt"))
        current = [c.rstrip(".") for c in V.done_items(z)]
        if not got:
            unreadable.append((stem, current, []))
        elif got == current[:len(got)]:
            fresh.append((stem, current, got))
        else:
            stale.append((stem, current, got))
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
