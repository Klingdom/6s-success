#!/usr/bin/env python3
"""
A clean hero photograph for every Entryway card, generated locally.

WHAT THIS UNBLOCKS
------------------
Two P0 issues, both labelled blocked-on-art, both stuck on the same thing.
The existing 90 card images bake every word into the pixels: EE-001 carries
"AMAZON DELIVERY" at roughly 60pt on both faces and a smile arrow logo on the
box, and 17 more carry garbled lettering, a fake QR code, the retired friction
meter, or the rejected term "Set in Order". None of that is reachable by a text
sweep, because none of it is text.

The regeneration prompt kit already prescribed the fix and had never been run:
generate a hero photograph with NO text of any kind, and let the template layer
set the words as real type. That makes the deck editable forever. A price, a
term or a trademark then changes in a JSON file instead of in a picture.

WHY THE PROMPTS LOOK LIKE THIS
------------------------------
Same lesson the zone heroes cost a full batch to learn: the model draws nouns,
not rules. A card's own tagline is written to persuade a reader, so
"RESPOND TO CHANGING CONDITIONS" has nothing in it to photograph. The subject
is built from the card's concrete objects instead, taken from its callouts,
with the card title leading because it is the strongest single noun available.

Problem cards get a believable mess and everything else gets the settled state,
because a Problem card showing a tidy hallway is telling the reader the
opposite of what its own text says.

Run:  python ops/generate_card_heroes.py --plan
      python ops/generate_card_heroes.py --run --limit 10
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

CORPUS = os.path.join(ROOT, "build", "entryway-cardtext.json")
SUBJECTS = os.path.join(ROOT, "ops", "card-subjects.json")
OUT = os.path.join(ROOT, "build", "heroes", "entryway")

# Words that mean the clause is a rule, a benefit or an instruction rather than
# a thing in the room. Identical reasoning to ops/generate_zone_heroes.py.
RULE = ("keep", "avoid", "process", "never", "always", "make sure", "remember",
        "should", "helps", "prevents", "reduces", "means", "matters",
        "everyone", "family", "system", "routine", "habit", "minutes")


def cards() -> list:
    d = json.load(io.open(CORPUS, encoding="utf-8"))
    return d["cards"]


def overrides() -> dict:
    if not os.path.exists(SUBJECTS):
        return {}
    return {k: v for k, v in json.load(io.open(SUBJECTS, encoding="utf-8")).items()
            if not k.startswith("_")}


def nouns_from(c: dict, budget: int = 16) -> str:
    """Concrete objects out of the callouts, which are the only field that
    reliably names things rather than describing outcomes."""
    out, used = [], 0
    for line in (c.get("callouts") or []):
        body = line.split(":", 1)[-1].strip().rstrip(".")
        low = body.lower()
        if any(w in low for w in RULE):
            continue
        n = len(body.split())
        if used + n > budget:
            break
        out.append(body)
        used += n
    return ", ".join(out)


def subject_for(c: dict) -> str:
    ov = overrides()
    if c["id"] in ov:
        body = ov[c["id"]]
    else:
        title = c["title"].lower().strip()
        detail = nouns_from(c)
        body = f"{title}, {detail}" if detail else title

    # A Problem card that shows a calm hallway contradicts its own text.
    mess = "PROBLEM" in (c.get("type") or "").upper()
    state = ("cluttered and overflowing, believable everyday mess"
             if mess else "tidy and settled, everything in its place")
    return (f"{body}, {state}, in a home entryway, "
            f"warm wood and painted wall, daylight")


def plan() -> list:
    from image_style import check
    out = []
    for c in cards():
        stem = c["id"]
        subject = subject_for(c)
        out.append({"id": stem, "title": c["title"], "type": c.get("type"),
                    "subject": subject, "problems": check(subject),
                    "done": os.path.exists(os.path.join(OUT, stem + ".png"))})
    return out


def main() -> int:
    from image_style import is_unverified
    items = plan()
    todo = [i for i in items if not i["done"]]
    unverified = [i for i in items if is_unverified(i["problems"])]
    bad = [i for i in items if i["problems"] and not is_unverified(i["problems"])]
    print(f"  cards            {len(items)}")
    print(f"  already made     {len(items) - len(todo)}")
    print(f"  to generate      {len(todo)}")
    if unverified:
        print(f"  token budget unchecked on {len(unverified)} "
              f"({unverified[0]['problems'][0]})")
    if bad:
        print(f"  prompt problems  {len(bad)}")
        for i in bad[:4]:
            print(f"    {i['id']:8} {i['problems'][0][:70]}")

    if "--plan" in sys.argv:
        print()
        for i in items[:8]:
            print(f"    {i['id']:8} {i['subject'][:96]}")
        return 0
    if "--run" not in sys.argv:
        print("\n  --plan to inspect, --run to generate")
        return 0

    if "--limit" in sys.argv:
        todo = todo[:int(sys.argv[sys.argv.index("--limit") + 1])]
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
                failed.append((i["id"], "; ".join(problems)))
                continue
            meta.update({"card": i["id"], "title": i["title"]})
            im.save(os.path.join(OUT, i["id"] + ".png"))
            json.dump(meta, io.open(os.path.join(OUT, i["id"] + ".json"), "w",
                                    encoding="utf-8", newline=""), indent=1)
            made += 1
            if n % 10 == 0 or n == len(todo):
                rate = (time.time() - t0) / n
                print(f"  {n}/{len(todo)}  {made} made  "
                      f"about {(len(todo) - n) * rate / 60:.0f} min left",
                      flush=True)
        except Exception as e:                                # noqa: BLE001
            failed.append((i["id"], f"{type(e).__name__}: {e}"))

    print(f"\n  generated {made} of {len(todo)} in {(time.time()-t0)/60:.0f} min")
    for cid, why in failed[:6]:
        print(f"    FAILED {cid:8} {why[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
