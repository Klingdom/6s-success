#!/usr/bin/env python3
"""
Pinterest and Instagram captions, boards and tags for all 114 zone cards.

WHY THIS EXISTS
----------------
OWNER-ACTIONS.md item 16 asks Phil to create a Pinterest business account and
an Instagram business account, then post the 114 save-and-share cards
ops/build_social_pins.py already built. That item also names the next real
step, once the accounts exist: "build a per-zone caption/board-and-tag list
from the same content.json these cards render from, so pasting text alongside
each image is not a second research pass." Nothing technical about writing
that text needs the account to exist first, and GOALS.md's decision rule 1
is "distribution beats production": posting 228 images by hand is still a
research-and-writing job for every single one unless the words are ready
first. This closes that gap ahead of the account, so account creation plus
posting becomes the one remaining manual step, not account creation plus 228
captions written cold.

WHAT IT DOES NOT DO
--------------------
Post anywhere, or open an account. Same wall as build_social_pins.py itself.

EVERY CLAIM IS DERIVED, NOT INVENTED
--------------------------------------
Title text reuses ops/build_youtube_metadata.py's own title_for(), so the
three channels that will eventually carry this content (YouTube, Pinterest,
Instagram) say the same thing about the same zone rather than three separate
guesses. The zone-page link reuses that same file's zone_page_slug(), which
already fixed a 13-of-114 wrong-URL bug from reconstructing the slug by hand;
reusing it here means that fix protects this file too. Every other sentence
is built from content.json's purpose/done_looks_like/the_call fields, the
same corpus already live on the site, never a new fact typed in here.

Run:  python ops/build_social_captions.py --all
      python ops/build_social_captions.py --zone "Landing Zone"
      python ops/build_social_captions.py --check
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import build_youtube_metadata as YT   # noqa: E402  (title_for, zone_page_slug)
import build_social_pins as SP        # noqa: E402  (done_items)
import video_zone as VZ               # noqa: E402  (zones, zone_slug)

OUT = os.path.join(ROOT, "build", "social", "captions")
SITE = "https://6s-success.com"

# Instagram feed captions cannot carry a clickable link outside the bio, so
# the CTA says where to look rather than pretending the URL is tappable.
IG_CTA = "Free written steps for this zone, no signup: link in bio, or search 6S Success %s."


def board_for(room: str) -> str:
    """One Pinterest board per room reads better than one giant board: a
    saver who wants Kitchen ideas should not have to wade through Garage
    pins to find them, and Pinterest's own guidance favours specific boards
    over a single catch-all."""
    return "%s Organization Ideas" % room


def hashtags_for(room: str, zone: str, cap: int) -> list:
    """Room- and zone-specific tags first, generic ones after, capped so a
    caller can ask for Pinterest's shorter set or Instagram's longer one
    from the same list rather than maintaining two."""
    r = re.sub(r"[^a-z0-9]", "", room.lower())
    z = re.sub(r"[^a-z0-9]", "", zone.lower())
    out = ["#%sorganization" % r, "#%s" % z, "#homeorganization",
           "#declutter", "#organizingtips", "#6smethod", "#tidyhome",
           "#homereset", "#organizedhome", "#cleaninghacks"]
    # De-duplicate while keeping order: a short zone name can collide with
    # the room tag (e.g. "kitchen" zone in the "Kitchen" room).
    seen, keep = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            keep.append(t)
    return keep[:cap]


def pin_description(room: str, z: dict, url: str) -> str:
    purpose = re.sub(r"\s+", " ", (z.get("purpose") or "").strip())
    items = SP.done_items(z)
    lines = [purpose] if purpose else []
    if items:
        lines.append("Done looks like: " + "; ".join(i.rstrip(".") for i in items[:2]) + ".")
    lines.append("Free step-by-step for this zone: %s" % url)
    text = " ".join(lines).strip()
    # Pinterest truncates descriptions around 500 characters in most surfaces.
    if len(text) > 490:
        text = text[:490].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return text


def ig_caption(room: str, z: dict, url: str) -> str:
    zone = z["zone"]
    hook = ((z.get("the_call") or {}).get("title") or "").strip()
    purpose = re.sub(r"\s+", " ", (z.get("purpose") or "").strip())
    items = SP.done_items(z)
    lines = []
    if hook:
        lines.append(hook + ".")
    lines.append("The %s in the %s. %s" % (zone, room, purpose))
    if items:
        lines.append("")
        lines.append("What done looks like:")
        for i, d in enumerate(items[:4]):
            lines.append("%d. %s" % (i + 1, d.rstrip(".")))
    lines.append("")
    lines.append(IG_CTA % zone.lower())
    return "\n".join(lines).strip()


def alt_text(room: str, zone: str) -> str:
    return ("Save-and-share checklist card for the %s in the %s, from the "
            "6S Success method." % (zone, room))


def build_one(room: str, z: dict) -> dict:
    zone = z["zone"]
    slug = VZ.zone_slug(room, zone)
    url = "%s/zones/%s.html" % (SITE, YT.zone_page_slug(room, zone))
    return {
        "slug": slug,
        "room": room,
        "zone": zone,
        "url": url,
        "pinterest": {
            "image": "build/social/pinterest/%s.png" % slug,
            "title": YT.title_for(room, zone),
            "description": pin_description(room, z, url),
            "board": board_for(room),
            "link": url,
            "hashtags": hashtags_for(room, zone, 4),
            "alt_text": alt_text(room, zone),
        },
        "instagram": {
            "image": "build/social/instagram/%s.png" % slug,
            "caption": ig_caption(room, z, url),
            "hashtags": hashtags_for(room, zone, 12),
            "alt_text": alt_text(room, zone),
        },
    }


def main() -> int:
    zs = VZ.zones()

    if "--check" in sys.argv:
        n = len([f for f in os.listdir(OUT) if f.endswith(".json")]) \
            if os.path.isdir(OUT) else 0
        print("  caption files: %d" % n)
        return 0 if n >= len(zs) else 1

    want = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    targets = zs
    if want is not None:
        room_want = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else None
        targets = [(r, z) for r, z in zs if z["zone"] == want
                   and (room_want is None or r == room_want)]
        if len(targets) > 1:
            raise SystemExit("%r exists in %s. Pass --room to say which."
                              % (want, " and ".join(r for r, _ in targets)))
        if not targets:
            raise SystemExit("no zone named %r. %d zones are available."
                              % (want, len(zs)))

    os.makedirs(OUT, exist_ok=True)
    boards, made, warn = {}, 0, []
    for room, z in targets:
        entry = build_one(room, z)
        if len(entry["pinterest"]["title"]) > 100:
            warn.append("%s: pinterest title too long" % entry["slug"])
        if len(entry["pinterest"]["description"]) > 500:
            warn.append("%s: pinterest description too long" % entry["slug"])
        if len(entry["instagram"]["caption"]) > 2200:
            warn.append("%s: instagram caption too long" % entry["slug"])
        io.open(os.path.join(OUT, entry["slug"] + ".json"), "w",
                encoding="utf-8", newline="").write(
            json.dumps(entry, indent=1, ensure_ascii=False) + "\n")
        boards.setdefault(entry["pinterest"]["board"], []).append(entry["slug"])
        made += 1

    if targets is zs:
        io.open(os.path.join(OUT, "boards.json"), "w",
                encoding="utf-8", newline="").write(
            json.dumps(dict(sorted(boards.items())), indent=1,
                       ensure_ascii=False) + "\n")

    print("  captions written : %d" % made)
    if targets is zs:
        print("  pinterest boards : %d" % len(boards))
    if warn:
        print("  problems         : %d %s" % (len(warn), warn[:3]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
