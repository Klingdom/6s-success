#!/usr/bin/env python3
"""
A hero photograph for every micro zone, generated locally.

WHY THIS IS THE UNLOCK
----------------------
109 of the 114 micro zones have no imagery. That single gap forced the video
format to be typographic, left every zone page a wall of text, and made the
matched before and after pairs, which are the strongest proof this site could
carry, impossible to produce. One batch closes all three.

THE SUBJECT COMES FROM THE ZONE, NOT FROM ME
--------------------------------------------
Each prompt is built from that zone's own "done_looks_like" sentence in
content/manual/source/content.json, which is a specific description of the
finished state written by the person who wrote the method. That is why these
are pictures of the thing rather than generic tidy rooms, and it is also the
reason the pictures are honest: the image shows what the page promises.

The sentence is trimmed to fit CLIP's 77 token budget with the subject first,
because a prompt that overflows loses the subject and produces a plausible
photograph of something else, which is the failure this pipeline already had
once and did not notice.

RESUMABLE ON PURPOSE
--------------------
114 images at roughly half a minute each is a long run and it will be
interrupted. Anything already generated is skipped, so re-running continues
rather than restarting, and a seed derived from the zone name means a repeat
produces the identical picture rather than a different one.

Run:  python ops/generate_zone_heroes.py --plan
      python ops/generate_zone_heroes.py --run --limit 10
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HF_HOME", os.path.join(ROOT, "build", "models"))
sys.path.insert(0, os.path.join(ROOT, "ops"))

CONTENT = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "build", "heroes", "zones")

# Room words that carry a lot of visual meaning in very few tokens.
ROOM_HINT = {
    "Entryway": "entryway", "Mudroom": "mudroom", "Kitchen": "kitchen",
    "Pantry": "pantry", "Dining Room": "dining room",
    "Living Room": "living room", "Family Room": "family room",
    "Primary Bedroom": "bedroom", "Guest Bedroom": "guest bedroom",
    "Kids Bedroom": "child's bedroom", "Nursery": "nursery",
    "Primary Bathroom": "bathroom", "Guest Bathroom": "bathroom",
    "Laundry Room": "laundry room", "Home Office": "home office",
    "Garage": "garage", "Workshop": "workshop", "Hall Closet": "hall closet",
    "Stair Landing": "stair landing", "Patio or Deck": "patio",
}


def zones() -> list:
    d = json.load(io.open(CONTENT, encoding="utf-8"))
    rooms = d["rooms"] if isinstance(d, dict) and "rooms" in d else d
    return [(r["room"], z) for r in rooms for z in r["zones"]]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# Clauses that state a rule rather than describe a thing. "Five things or
# fewer", "a hand's width of empty space", "nothing on the floor": these are
# how a standard is written and there is no way to draw them. Fed to the model
# they contribute no subject, so it falls back on the room word and renders a
# generic tidy room, which is exactly what half of the first batch was.
RULE_WORDS = ("fewer", "empty", "nothing", "no ", "none", "within",
              "you can", "without", "at a glance", "by feel", "reach",
              "per person", "or less", "visible from", "hand's width")


def zone_noun(zone: str) -> str:
    """The zone name as a thing that can be photographed.

    The first batch never put the zone name in the prompt at all. It sent only
    the done_looks_like sentence, so "Board Game and Puzzle Zone" reached the
    model as a rule about shelf contents and came back as cardboard boxes in an
    empty room. The zone name is the single strongest piece of subject
    information available and it was the one thing being thrown away.
    """
    n = re.sub(r"\b(Zone|Area|Storage)$", "", zone).strip()
    return (n or zone).lower()


# Some zones cannot be described by a machine reading their own standard,
# because the standard names a rule or a place rather than a thing: "floor and
# circulation path", "paper and household backstock", "surface rail and safety
# zone". There is nothing there to draw, so the model renders the room and
# ignores the zone. Those 32 are written by hand in ops/hero-subjects.json.
OVERRIDES = json.load(io.open(os.path.join(ROOT, "ops", "hero-subjects.json"),
                              encoding="utf-8"))


def subject_for(room: str, z: dict, budget_words: int = 22) -> str:
    """Zone name first, then whatever concrete detail fits, then the scene."""
    stem = f"{slug(room)}--{slug(z['zone'])}"
    if stem in OVERRIDES:
        hint = ROOM_HINT.get(room, room.lower())
        where = f"in an {hint}" if hint[0] in "aeiou" else f"in a {hint}"
        return (f"{OVERRIDES[stem]}, {where}, "
                f"warm wood and painted wall, daylight")

    done = str(z.get("done_looks_like") or "").strip().rstrip(".")
    clauses = [c.strip() for c in re.split(r",| and (?=\w+ \w+)", done)
               if c.strip()]

    noun = zone_noun(z["zone"])
    parts, used = [], len(noun.split())
    for c in clauses:
        low = c.lower()
        if any(w in low for w in RULE_WORDS):
            continue
        n = len(c.split())
        if used + n > budget_words:
            break
        parts.append(c)
        used += n

    body = ", ".join([noun] + parts)
    # SCENE names a specific piece of furniture per room, which was right
    # when the prompt had no subject noun and wrong now that it does: the
    # shoe and boot zone was being asked for "on a console table by a front
    # door" and came back as neither. The room word alone gives the model
    # somewhere to stand without contradicting the subject.
    hint = ROOM_HINT.get(room, room.lower())
    where = f"in an {hint}" if hint[0] in "aeiou" else f"in a {hint}"
    return f"{body}, {where}, warm wood and painted wall, daylight"


def plan() -> list:
    from image_style import check
    out = []
    for room, z in zones():
        name = z["zone"]
        stem = f"{slug(room)}--{slug(name)}"
        subject = subject_for(room, z)
        out.append({"room": room, "zone": name, "stem": stem,
                    "subject": subject, "problems": check(subject),
                    "done": os.path.exists(os.path.join(OUT, stem + ".png"))})
    return out


def main() -> int:
    items = plan()
    todo = [i for i in items if not i["done"]]
    bad = [i for i in items if i["problems"]]

    print(f"  zones            {len(items)}")
    print(f"  already made     {len(items) - len(todo)}")
    print(f"  to generate      {len(todo)}")
    if bad:
        print(f"  prompt problems  {len(bad)}")
        for i in bad[:4]:
            print(f"    {i['zone'][:30]:32} {i['problems'][0][:70]}")

    if "--plan" in sys.argv:
        print()
        for i in items[:6]:
            print(f"    {i['room'][:14]:16} {i['zone'][:26]:28} {i['subject'][:78]}")
        return 0
    if "--run" not in sys.argv:
        print("\n  --plan to inspect, --run to generate")
        return 0

    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else len(todo)
    todo = todo[:limit]
    if not todo:
        print("  nothing to do")
        return 0

    os.makedirs(OUT, exist_ok=True)
    import image_local as L

    t0, made, failed = time.time(), 0, []
    for n, i in enumerate(todo, 1):
        try:
            im, meta = L.generate(i["subject"])
            problems = L.verify(im)
            if problems:
                failed.append((i["zone"], "; ".join(problems)))
                continue
            meta.update({"room": i["room"], "zone": i["zone"]})
            im.save(os.path.join(OUT, i["stem"] + ".png"))
            json.dump(meta, io.open(os.path.join(OUT, i["stem"] + ".json"),
                                    "w", encoding="utf-8", newline=""), indent=1)
            made += 1
            if n % 5 == 0 or n == len(todo):
                rate = (time.time() - t0) / n
                left = (len(todo) - n) * rate
                print(f"  {n}/{len(todo)}  {made} made  "
                      f"{rate:.0f}s each  about {left/60:.0f} min left",
                      flush=True)
        except Exception as e:                                # noqa: BLE001
            failed.append((i["zone"], f"{type(e).__name__}: {e}"))

    print(f"\n  generated {made} of {len(todo)} in {(time.time()-t0)/60:.0f} min")
    for z, why in failed[:6]:
        print(f"    FAILED {z[:30]:32} {why[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
