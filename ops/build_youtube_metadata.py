"""Title, description and tags for every zone video, ready to upload.

A video with no title and no description is invisible even after it is
uploaded. YouTube is a search engine, and the 114 files we have carry no text
at all: the words are painted into the frames, so the only thing the index can
read is whatever we write here.

This is deliberately not clever. Each title answers the question a person
actually types, each description leads with what the zone is and what done
looks like rather than with the brand, and the timestamps let somebody jump
straight to the pass they care about.

Writes build/video/youtube/<slug>.json, one per zone, plus a playlists.json
grouping them by room.

    python ops/build_youtube_metadata.py
    python ops/build_youtube_metadata.py --check
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
OUT = os.path.join(ROOT, "build", "video", "youtube")
SITE = "https://6s-success.com"

# Order matters: it is the order the video presents them in.
PASSES = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]


def first_sentence(text: str, limit: int = 160) -> str:
    """The first WHOLE sentence, or nothing rather than half of one.

    The fallback used to be text[:limit], a hard character cut. When no
    sentence boundary fell inside the limit, and the six-pass lines are written
    at about 46 words so it usually did not, the description ended mid-word:
    "tape it inside the coat cu". Measured 2026-09-07: 428 lines across 113 of
    the 114 description files ended mid-clause, and these are the words a
    stranger reads on YouTube before deciding whether to watch.

    Now: take the first sentence if there is one, whatever its length, because
    a slightly long sentence is a smaller fault than a severed one. Only if the
    text contains no sentence ending at all does it fall back, and then it cuts
    at a WORD boundary and marks the cut with an ellipsis, so a truncation
    reads as a truncation instead of as a finished thought.
    """
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    m = re.match(r"(.{20,}?[.!?])(?:\s|$)", text)
    if m:
        return m.group(1).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return (cut + "…") if cut else text[:limit]


def title_for(room: str, zone: str) -> str:
    """The phrase somebody types, not the phrase we would choose.

    Ask build_zone_pages for its own title rather than reconstruct one: this
    function used to build "How to organize the %s | %s" % (zone.lower(),
    room) straight from the internal zone key, which is exactly the "Landing
    Zone" vocabulary that module's own comment says nobody searches, and it
    put a name on the video that the linked page never uses (the page shows
    "How to organize the entryway drop zone" and heads itself "The Landing
    Spot"). Found 2026-09-12 checking a random zone end to end: all three
    surfaces (video title, page <title>, page <h1>) named the same real-world
    zone three different ways. zone_seo_title() is the exact string the page
    itself uses, so the video and the page it links to now agree.
    """
    import build_zone_pages as bz
    return bz.zone_seo_title(room, zone)


def description_for(room: str, z: dict) -> str:
    import build_zone_pages as bz
    zone = z["zone"]
    name = bz.display(room, zone)
    lines = []
    lines.append(first_sentence(z.get("purpose", "")))
    lines.append("")
    # name, not the raw internal zone key: a viewer who reads "Landing Zone"
    # here then clicks through to a page headed "The Landing Spot" is being
    # told two names for the one thing. Found and fixed alongside title_for().
    lines.append("This is %s in the %s. About %s."
                 % (name, room, z.get("session", "30 minutes")))
    lines.append("")

    done = re.sub(r"\s+", " ", (z.get("done_looks_like") or "").strip())
    if done:
        lines.append("WHAT DONE LOOKS LIKE")
        lines.append(done if len(done) < 400 else done[:400].rsplit(" ", 1)[0] + "...")
        lines.append("")

    passes = z.get("passes") or {}
    have = [p for p in PASSES if passes.get(p)]
    if have:
        lines.append("THE SIX PASSES")
        for p in have:
            lines.append("%s: %s" % (p.capitalize(), first_sentence(passes[p], 110)))
        lines.append("")

    stand = (z.get("leave_behind") or {}).get("standard")
    if stand:
        lines.append("THE STANDARD YOU LEAVE BEHIND")
        lines.append(first_sentence(stand, 220))
        lines.append("")

    lines.append("Full written steps for this zone, free:")
    lines.append("%s/zones/%s.html" % (SITE, zone_page_slug(room, zone)))
    lines.append("")
    lines.append("6S Success turns Lean's six-S method into something you can "
                 "actually do in a house: Sort, Straighten, Shine, Safety, "
                 "Standardize, Sustain. One small zone at a time, finished in "
                 "one session, and it stays finished.")
    lines.append("")
    lines.append("#homeorganization #declutter #%s"
                 % re.sub(r"[^a-z]", "", room.lower()))
    return "\n".join(lines).strip()


def zone_page_slug(room: str, zone: str) -> str:
    """Ask the generator that writes those pages, do not reconstruct it.

    The first version guessed the pattern and got 13 of 114 wrong, because
    build_zone_pages.py runs the zone name through a NAME_MAP first: the
    Landing Zone's page is entryway-the-landing-spot.html, not
    entryway-the-landing-zone.html. Thirteen descriptions would have pointed
    at a 404, on the one link in each that sends a viewer to the site.
    """
    import build_zone_pages as bz
    return "%s-%s" % (bz.slug(room), bz.slug(bz.display(room, zone)))


def tags_for(room: str, zone: str) -> list:
    base = ["home organization", "declutter", "organizing", "6S", "5S at home",
            "home reset", "cleaning routine", "tidy home"]
    r = room.lower()
    z = zone.lower()
    out = base + [r, z, "%s organization" % r, "%s ideas" % r,
                  "how to organize %s" % z, "%s declutter" % r]
    # YouTube caps the tag field at 500 characters in total.
    keep, total = [], 0
    for t in out:
        if total + len(t) + 1 > 480:
            break
        keep.append(t)
        total += len(t) + 1
    return keep


def main() -> int:
    import video_zone

    if "--check" in sys.argv:
        n = len([f for f in os.listdir(OUT) if f.endswith(".json")]) \
            if os.path.isdir(OUT) else 0
        print("  metadata files: %d" % n)
        return 0 if n >= 114 else 1

    os.makedirs(OUT, exist_ok=True)
    playlists, made, warn = {}, 0, []
    for room, z in video_zone.zones():
        s = video_zone.zone_slug(room, z["zone"])
        title = title_for(room, z["zone"])
        desc = description_for(room, z)
        meta = {
            "slug": s,
            "room": room,
            "zone": z["zone"],
            "title": title,
            "description": desc,
            "tags": tags_for(room, z["zone"]),
            "categoryId": "26",          # Howto & Style
            "privacyStatus": "public",
            "captions": s + ".srt",
            "video_vertical": "build/video/zones/%s.mp4" % s,
            "video_wide": "build/video/zones-16x9/%s.mp4" % s,
        }
        if len(title) > 100:
            warn.append("%s: title too long" % s)
        if len(desc) > 5000:
            warn.append("%s: description too long" % s)
        io.open(os.path.join(OUT, s + ".json"), "w",
                encoding="utf-8", newline="").write(
            json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
        playlists.setdefault(room, []).append(s)
        made += 1

    io.open(os.path.join(OUT, "playlists.json"), "w",
            encoding="utf-8", newline="").write(
        json.dumps({"%s: every micro zone" % r: v
                    for r, v in sorted(playlists.items())},
                   indent=1, ensure_ascii=False) + "\n")

    print("  metadata written : %d" % made)
    print("  playlists        : %d rooms" % len(playlists))
    if warn:
        print("  problems         : %d %s" % (len(warn), warn[:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
