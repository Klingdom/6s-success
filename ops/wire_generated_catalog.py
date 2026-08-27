#!/usr/bin/env python3
"""
Put the 149 generated packs into the site catalogue, and keep them updatable.

HOW THE GENERATED ENTRIES ARE IDENTIFIED
----------------------------------------
site/assets/js/data.js is the one catalogue the shop page renders and
ops/stripe_catalog.py prices from, so the generated packs have to live in it
rather than in a parallel file. But 149 entries appended by hand rot the first
time a price or a blurb changes, and re-appending duplicates them.

The first version marked the block with JavaScript comments. That broke every
reader immediately: data.js is parsed with json.loads by this script, by
ops/stripe_catalog.py and by ops/audit_catalog.py, and JSON has no comments.
A file that is valid JavaScript is not necessarily readable by the things that
actually read it.

So the generated entries identify themselves instead. Every one carries
`"super": "PACK-HOUSE"`, which no hand written entry has, and a re-run drops
everything carrying it before writing the current set. The file stays valid
JSON, the block needs no delimiters, and running this twice changes nothing.

WHAT EACH ENTRY CARRIES THAT THE HAND WRITTEN ONES DO NOT
---------------------------------------------------------
A `super` field naming the whole house pack. Every one of these products is a
subset of that pack, and the shop is expected to say so on the product itself
rather than hoping the customer works it out. Somebody about to spend $16 on
six rooms should be able to see the $19 that covers twenty, on the same
screen, without hunting. That is the Diagnose, Recommend, Explain, Offer order
in CLAUDE.md section 12 rather than the interrupt and pressure one.

Run:  python ops/wire_generated_catalog.py
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_catalog as bc                                     # noqa: E402
from generated_products import products                        # noqa: E402

DATA_JS = os.path.join(ROOT, "site", "assets", "js", "data.js")
# The field that marks an entry as owned by this script. No hand written entry
# has it, and every generated one does, so it doubles as the delete key on a
# re-run and as the pointer the shop uses to show the cheaper superset.
OWNED = "super"
SUPERSET = "PACK-HOUSE"

CAT = {"zone": "Micro Zone Packs", "room": "Room Packs",
       "situation": "Situation Kits", "area": "Area Bundles"}

# No new artwork is invented for 149 products, so these are the photographs the
# site already has, mapped by room to the one that fits best. A single image
# reused across a tier put three identical pantry photographs side by side in
# the situation kits, which reads as a broken page rather than a restrained
# one. None of these claims to be a picture of the product; they are the same
# decorative method photography used everywhere else on the site.
ROOM_IMG = {
    "Entryway": "hero-entry.jpg", "Mudroom": "hero-entry.jpg",
    "Hall Closet": "hero-entry.jpg", "Stair Landing": "hero-entry.jpg",
    "Kitchen": "prepare.jpg", "Pantry": "prepare.jpg",
    "Dining Room": "prepare.jpg",
    "Living Room": "calm-living.jpg", "Family Room": "reset-together.jpg",
    "Primary Bedroom": "rhythm.jpg", "Guest Bedroom": "renewed.jpg",
    "Kids Bedroom": "family.jpg", "Nursery": "family.jpg",
    "Primary Bathroom": "shine.jpg", "Guest Bathroom": "shine.jpg",
    "Laundry Room": "shine.jpg",
    "Home Office": "standard.jpg", "Garage": "straighten.jpg",
    "Workshop": "straighten.jpg", "Patio or Deck": "reset.jpg",
}
# Situation kits and area bundles span rooms, so they cycle a fixed pool in
# SKU order. Deterministic, so the same product always shows the same photo
# and a rebuild does not reshuffle the whole shop.
SPAN_IMG = ["room-map.jpg", "reset.jpg", "renewed.jpg", "rhythm.jpg",
            "reset-together.jpg", "calm-living.jpg", "standard.jpg"]


def image_for(p: dict, i: int) -> str:
    if p["kind"] in ("zone", "room"):
        return ROOM_IMG.get(p.get("room"), "room-map.jpg")
    return SPAN_IMG[i % len(SPAN_IMG)]


def entry(p: dict, i: int = 0, prev: dict | None = None) -> dict:
    """One catalogue row.

    prev is the row this replaces, if there is one. Its buy link is carried
    across, because that link comes from Stripe rather than from anything
    computable here: rebuilding without it silently emptied the checkout on
    all 149 generated products, and only a later Stripe sync would have put
    them back. A rebuild must never be able to take the shop offline.
    """
    out = {
        "sku": p["sku"],
        "cat": CAT[p["kind"]],
        "name": p["name"],
        "variant": f"{p['cards']} cards, print at home",
        "price": p["price"],
        "blurb": p["blurb"],
        "img": image_for(p, i),
        "badge": "Print at home",
        "phase": "Standardize",
        "fulfil": "Emailed within the hour",
        # Named so the shop can show the cheaper superset beside the subset.
        "super": "PACK-HOUSE",
    }
    if prev and prev.get("buy"):
        out["buy"] = prev["buy"]
    return out


def main() -> int:
    keep, dropped = products()
    src = io.open(DATA_JS, encoding="utf-8").read()
    head, tail = src[:src.index("[")], src[src.rindex("]") + 1:]
    arr = json.loads(src[src.index("["):src.rindex("]") + 1])

    # Drop anything a previous run wrote, so this is a replacement.
    hand = [i for i in arr if not i.get(OWNED)]
    hand_skus = {i["sku"] for i in hand}

    clash = [p["sku"] for p in keep if p["sku"] in hand_skus]
    assert not clash, (
        f"generated SKUs collide with hand written catalogue entries: {clash}. "
        f"Overwriting one silently would change a price somebody set on "
        f"purpose.")

    was = {i["sku"]: i for i in arr}
    out = hand + [entry(p, i, was.get(p["sku"]))
                  for i, p in enumerate(keep)]
    body = ",\n".join(" " + json.dumps(i, ensure_ascii=False) for i in out)
    io.open(DATA_JS, "w", encoding="utf-8", newline="").write(
        head + "[\n" + body + "\n]" + tail)

    # Read it back exactly the way the browser and stripe_catalog.py will.
    back = io.open(DATA_JS, encoding="utf-8").read()
    got = json.loads(back[back.index("["):back.rindex("]") + 1])
    skus = [i["sku"] for i in got]
    assert len(skus) == len(set(skus)), "duplicate SKUs after writing"
    assert len(got) == len(hand) + len(keep), (
        f"expected {len(hand)} + {len(keep)}, got {len(got)}")

    over = [i["sku"] for i in got
            if i.get(OWNED) and (i.get("price") or 0) >= bc.WHOLE_HOUSE]
    assert not over, f"subset priced at or above its superset: {over[:4]}"

    assert any(i["sku"] == SUPERSET for i in got), (
        f"every generated entry points at {SUPERSET} as the cheaper superset, "
        f"and it is not in the catalogue. The pointer would be a dead end.")

    # A rebuild that empties the checkout is worse than no rebuild.
    lost = [i["sku"] for i in got
            if (i.get("price") or 0) > 0 and not i.get("buy")
            and was.get(i["sku"], {}).get("buy")]
    assert not lost, (
        f"{len(lost)} products had a buy link before this ran and do not now: "
        f"{lost[:4]}. Rebuilding the catalogue must never take the shop "
        f"offline.")

    priced = [i for i in got if (i.get("price") or 0) > 0]
    print(f"  catalogue now {len(got)} entries: {len(hand)} hand written, "
          f"{len(keep)} generated")
    print(f"  {len(priced)} are buyable, {len(got) - len(priced)} free")
    print(f"  {len(dropped)} generated products deliberately not listed")
    for k in ("zone", "room", "situation", "area"):
        n = [p for p in keep if p["kind"] == k]
        if n:
            print(f"    {CAT[k]:20} {len(n):>4}  at ${n[0]['price']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
