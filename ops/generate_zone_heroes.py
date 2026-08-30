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

import hashlib
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


def subject_for(room: str, z: dict, budget_words: int = 34) -> str:
    """The zone's own finished state, trimmed to fit the token budget.

    done_looks_like is one long sentence of clauses. The first two clauses
    carry the subject; the rest are refinements that would be truncated
    anyway, so they are dropped deliberately rather than by the encoder.
    """
    done = str(z.get("done_looks_like") or "").strip().rstrip(".")
    clauses = [c.strip() for c in re.split(r",| and (?=\w+ \w+)", done) if c.strip()]

    room_word = ROOM_HINT.get(room, room.lower())
    parts, used = [], 0
    for c in clauses:
        n = len(c.split())
        if used + n > budget_words:
            break
        parts.append(c)
        used += n
    if not parts and clauses:
        parts = [" ".join(clauses[0].split()[:budget_words])]

    body = ", ".join(parts)
    article = "An" if room_word[0] in "aeiou" else "A"
    return f"{article} {room_word}: {body}"


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
