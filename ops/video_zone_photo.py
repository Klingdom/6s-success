#!/usr/bin/env python3
"""
A photo led vertical video for every micro zone that has a reviewed picture.

WHY THIS REPLACES THE TYPOGRAPHIC FORMAT
----------------------------------------
ops/video_zone.py says, in its own docstring, that it is typographic because
"109 of the 114 micro zones have no photograph and there is no stock library
on this machine". That was true when it was written and it is not true now:
102 of the 114 zones carry a photograph that a person has looked at and
approved, generated locally.

So the constraint that chose the format is gone. A text slide holds attention
for about a second on a feed; a picture with a slow push and karaoke captions
is the format the card videos already use and it is visibly stronger. Nothing
about the words changes: every line still comes from that zone's own entry in
content.json, the same as before.

WHAT IT WILL NOT DO
-------------------
Use an unreviewed picture. It reads ops/hero-verdicts.json and builds only for
zones whose approval matches the sha of the image on disk, which is the same
gate the zone pages and the card deck use. A video is a louder publication
than a page, not a quieter one.

Run:  python ops/video_zone_photo.py --plan
      python ops/video_zone_photo.py --build --limit 3
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import video as V                                             # noqa: E402

CONTENT = os.path.join(ROOT, "content", "manual", "source", "content.json")
HEROES = os.path.join(ROOT, "build", "heroes", "zones")
VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")
OUT = os.path.join(ROOT, "build", "video", "zones-photo")

# How long each caption holds. Short phrases, because a viewer reads three
# words at a glance and a sentence needs a pause they will not give it.
HOLD = 2.05


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def approved() -> set:
    """Zone stems whose approval is about the image currently on disk."""
    if not os.path.exists(VERDICTS):
        return set()
    raw = json.load(io.open(VERDICTS, encoding="utf-8"))
    ok = set()
    for stem, rec in raw.items():
        png = os.path.join(HEROES, stem + ".png")
        if not isinstance(rec, dict) or rec.get("verdict") != "ok":
            continue
        if not os.path.exists(png):
            continue
        got = hashlib.sha256(io.open(png, "rb").read()).hexdigest()[:10]
        if rec.get("sha") == got:
            ok.add(stem)
    return ok


def zones() -> list:
    d = json.load(io.open(CONTENT, encoding="utf-8"))
    rooms = d["rooms"] if isinstance(d, dict) and "rooms" in d else d
    return [(r["room"], z) for r in rooms for z in r["zones"]]


def script_for(room: str, z: dict) -> list:
    """The lines on screen, all of them from the zone's own entry.

    Nothing is written to fill a beat. The shape is the method: name the zone,
    say what goes wrong, say what done looks like, give the one action.
    """
    name = z["zone"]
    done = str(z.get("done_looks_like") or "").strip().rstrip(".")
    why = str(z.get("purpose") or z.get("why") or "").strip().rstrip(".")

    lines = [f"The {name.lower()}."]
    if why:
        lines.append(why.split(".")[0].strip())
    lines.append("What done looks like:")
    for clause in [c.strip() for c in done.split(",") if c.strip()][:3]:
        lines.append(clause[0].upper() + clause[1:] if clause else clause)
    lines.append("Fifteen minutes. One zone.")
    return [l for l in lines if l][:8]


def timed(lines: list) -> list:
    """(start, end, text) triples, which is the shape build_ass expects.

    Got this wrong first time and produced pairs, which failed loudly on the
    first render rather than silently producing a mistimed video. That is the
    right way round for a bug to behave.
    """
    out, t = [], 0.0
    for line in lines:
        # A longer line needs longer on screen, but never so long the clip
        # stalls: a caption that outstays its welcome is a scroll.
        hold = min(HOLD + max(0, len(line) - 34) * 0.035, 3.6)
        out.append((round(t, 2), round(t + hold, 2), line))
        t += hold
    return out


def plan() -> list:
    ok = approved()
    items = []
    for room, z in zones():
        stem = f"{slug(room)}--{slug(z['zone'])}"
        if stem not in ok:
            continue
        lines = script_for(room, z)
        items.append({"room": room, "zone": z["zone"], "stem": stem,
                      "png": os.path.join(HEROES, stem + ".png"),
                      "lines": lines, "phrases": timed(lines),
                      "done": os.path.exists(os.path.join(OUT, stem + ".mp4"))})
    return items


def main() -> int:
    items = plan()
    total_zones = len(zones())
    print(f"  zones                {total_zones}")
    print(f"  with an approved picture {len(items)}")
    print(f"  held back            {total_zones - len(items)} "
          f"(no reviewed picture, so no video)")
    todo = [i for i in items if not i["done"]]
    print(f"  already built        {len(items) - len(todo)}")

    if "--plan" in sys.argv:
        print()
        for i in items[:3]:
            secs = i["phrases"][-1][1]
            print(f"    {i['zone'][:28]:30} {secs:4.1f}s")
            for _a, _b, line in i["phrases"]:
                print(f"        {line}")
        return 0
    if "--build" not in sys.argv:
        print("\n  --plan to inspect, --build to render")
        return 0

    if "--limit" in sys.argv:
        todo = todo[:int(sys.argv[sys.argv.index("--limit") + 1])]
    if not todo:
        print("  nothing to do")
        return 0

    os.makedirs(OUT, exist_ok=True)
    made, failed = 0, []
    for i in todo:
        out = os.path.join(OUT, i["stem"] + ".mp4")
        try:
            V.render(i["png"], i["phrases"], out)
            want = i["phrases"][-1][1] + 0.6
            problems = V.verify(out, want)
            if problems:
                failed.append((i["zone"], "; ".join(problems)))
                continue
            made += 1
        except Exception as e:                                # noqa: BLE001
            failed.append((i["zone"], f"{type(e).__name__}: {e}"))

    print(f"\n  built {made} of {len(todo)} into "
          f"{os.path.relpath(OUT, ROOT)}")
    for z, why in failed[:6]:
        print(f"    FAILED {z[:28]:30} {why[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
