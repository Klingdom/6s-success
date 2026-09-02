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


def slug(room: str, zone: str) -> str:
    def one(t):
        return t.lower().replace(" ", "-").replace(",", "").replace("/", "-")
    return "%s--%s" % (one(room), one(zone))


def first_sentence(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    m = re.match(r"(.{20,%d}?[.!?])\s" % limit, text + " ")
    return (m.group(1) if m else text[:limit]).strip()


def title_for(room: str, zone: str) -> str:
    """The phrase somebody types, not the phrase we would choose.

    Nobody searches "Landing Zone". They search "how to organise the entryway
    drop zone". So lead with the task and the room, and keep the zone name as
    the qualifier. YouTube truncates around 60 characters in most surfaces, so
    anything essential goes first.
    """
    t = "How to organise the %s | %s" % (zone.lower(), room)
    if len(t) > 70:
        t = "How to organise the %s" % zone.lower()
    return t


def description_for(room: str, z: dict) -> str:
    zone = z["zone"]
    lines = []
    lines.append(first_sentence(z.get("purpose", "")))
    lines.append("")
    lines.append("This is the %s in the %s. About %s."
                 % (zone, room, z.get("session", "30 minutes")))
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
    r = room.lower().replace(" ", "-")
    z = re.sub(r"[^a-z0-9]+", "-", zone.lower()).strip("-")
    return "%s-the-%s" % (r, z)


def tags_for(room: str, zone: str) -> list:
    base = ["home organization", "declutter", "organizing", "6S", "5S at home",
            "home reset", "cleaning routine", "tidy home"]
    r = room.lower()
    z = zone.lower()
    out = base + [r, z, "%s organization" % r, "%s ideas" % r,
                  "how to organise %s" % z, "%s declutter" % r]
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
        s = slug(room, z["zone"])
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
