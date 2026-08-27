#!/usr/bin/env python3
"""
Generate the full product catalogue from the content spine.

WHAT THIS BUILDS, AND WHY EACH TIER IS A REAL PRODUCT
-----------------------------------------------------
Everything here is generated from content/manual/source/content.json, so no
product can describe something the method does not contain, and every one can be
delivered the moment somebody pays: the file already exists.

  ZONE PACK, 114 of them, $4
      One micro zone: its six cards, its standard, its trigger, its hazards and
      its cleaning detail, on two printable pages. For somebody with exactly one
      problem. Nobody with a bad garage workbench wants 684 cards.

  ROOM PACK, 20 of them, $9
      Every zone in one room. Between 18 and 42 cards depending on the room,
      plus that room's standards sheet.

  SITUATION KIT, 15 of them, $14
      The zones a specific life event actually touches, in the order they
      matter. Moving in, a new baby, going back to school. These are curated
      rather than mechanical: a person facing a move does not think in rooms,
      they think in the move.

  AREA BUNDLE, 6 of them, $24
      Several rooms that get worked together. Wet rooms, sleeping areas,
      storage.

WHY NOT CHEAPER THAN $4
-----------------------
Stripe takes 30 cents plus 2.9 percent. At $3 that is 13 percent to fees. At $4
it is 10. Below that the transaction costs more to process than it is worth
running.

WHY THIS IS NOT PADDING
-----------------------
Each tier is a genuinely different unit of work, and the same relationship the
existing $19 Whole House Print Pack already has to the free zone pages: the
method is free to read, the printable artifact you carry into the room is the
product. That precedent is established and has sold.

A tier that could not be delivered would not be here. There are no physical
goods, no print runs, no suppliers.

Run:  python ops/build_catalog.py --check
      python ops/build_catalog.py --build
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(ROOT, "build", "products")

sys.path.insert(0, os.path.join(ROOT, "ops"))

SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]
COLOUR = {"sort": "#CB4B36", "straighten": "#BC4B2A", "shine": "#D98A2B",
          "safety": "#DDA63A", "standardize": "#6E8B5B", "sustain": "#4E7A57"}

# The whole house print pack is $19 and contains all 684 cards, so it is a
# strict superset of every product below. Any tier priced at or above $19 is
# therefore a worse deal than something already on the same shop page, and
# selling it would be indefensible whatever the curation is worth. The area
# bundle was $24. It is $16: above the situation kit, below the superset.
#
# This ceiling is not decoration. If the whole house pack is ever repriced,
# WHOLE_HOUSE below has to move with it, and the assert in main() fails until
# it does.
WHOLE_HOUSE = 19
PRICE = {"zone": 4, "room": 9, "situation": 14, "area": 16}

# Curated. A person facing a move does not think in rooms, they think in the
# move, and the zones that matter are not the ones a room list would give them.
# Every zone named here is checked against the spine at build time.
SITUATIONS = [
    ("moving-in", "Moving In",
     "The order to unpack in, so the first week works before the boxes are gone.",
     [("Entryway", None), ("Kitchen", ["Primary Prep Counter", "Sink and Dishwashing Zone",
                                        "Upper Cabinet Zone", "Lower Cabinet and Cookware Zone"]),
      ("Primary Bedroom", ["Bed and Bedding Zone", "Primary Closet"]),
      ("Primary Bathroom", ["Vanity Counter", "Under-Sink Cabinet"])]),

    ("moving-out", "Moving Out",
     "What to empty, in what order, so the last day is not the hard one.",
     [("Garage", None), ("Hall Closet", None), ("Pantry", ["Backstock and Bulk Zone"]),
      ("Primary Bathroom", ["Medicine Cabinet or Wall Storage", "Under-Sink Cabinet"])]),

    ("new-baby", "A New Baby",
     "The rooms that change, set up so the tired version of you can still find things.",
     [("Nursery", None), ("Laundry Room", ["Sorting and Hamper Zone", "Folding Surface"]),
      ("Kitchen", ["Sink and Dishwashing Zone"])]),

    ("back-to-school", "Back to School",
     "The morning routine, built once in September so it holds until June.",
     [("Kids Bedroom", ["School and Activity Launch Zone", "Study Desk", "Clothing Closet"]),
      ("Entryway", ["Landing Zone", "Coat and Outerwear Zone", "Shoe and Boot Zone"]),
      ("Mudroom", ["Family Hook Zone"]), ("Laundry Room", ["Sorting and Hamper Zone"])]),

    ("holiday-hosting", "Holiday Hosting",
     "The guest facing rooms, in the week before rather than the morning of.",
     [("Guest Bedroom", None), ("Guest Bathroom", None), ("Dining Room", None),
      ("Entryway", ["Coat and Outerwear Zone"])]),

    ("downsizing", "Downsizing",
     "The zones that hold the most and give up the least, worked in the right order.",
     [("Garage", None), ("Hall Closet", None),
      ("Primary Bedroom", ["Primary Closet", "Dresser Drawers"]),
      ("Dining Room", ["China or Display Cabinet", "Buffet or Sideboard Storage"])]),

    ("spring-reset", "The Spring Reset",
     "One pass through the rooms that carry a winter's worth of accumulation.",
     [("Mudroom", None), ("Hall Closet", None), ("Laundry Room", None),
      ("Patio or Deck", None)]),

    ("small-apartment", "The Small Apartment",
     "Every zone that exists when there is no garage, no basement and no spare room.",
     [("Entryway", ["Landing Zone", "Coat and Outerwear Zone", "Shoe and Boot Zone"]),
      ("Kitchen", None), ("Primary Bathroom", ["Vanity Counter", "Vanity Drawers",
                                                "Under-Sink Cabinet", "Shower or Tub"]),
      ("Living Room", None)]),

    ("working-from-home", "Working From Home",
     "The desk and everything that quietly competes with it.",
     [("Home Office", None), ("Living Room", ["Side Tables and Lighting"]),
      ("Dining Room", ["Beverage or Coffee Station"])]),

    ("pet-household", "A Household With Pets",
     "The zones a dog or a cat actually changes, including the ones nobody expects.",
     [("Mudroom", None), ("Laundry Room", ["Utility and Cleaning Zone"]),
      ("Entryway", ["Door, Mat, and Immediate Floor"]),
      ("Hall Closet", ["Cleaning Supply Zone", "Cleaning Equipment Zone"])]),

    ("ageing-in-place", "Ageing In Place",
     "The reach, the light and the floor, room by room, with Safety leading.",
     [("Primary Bathroom", None), ("Stair Landing", None),
      ("Kitchen", ["Lower Cabinet and Cookware Zone", "Upper Cabinet Zone"]),
      ("Primary Bedroom", ["Bed and Bedding Zone"])]),

    ("post-renovation", "After the Builders Leave",
     "Putting a room back, when everything was in boxes and nothing has a home yet.",
     [("Kitchen", None), ("Garage", ["Primary Workbench", "Hand Tool Wall and Cabinets"]),
      ("Hall Closet", ["Cleaning Supply Zone"])]),

    ("first-home", "Your First Home",
     "The eight zones worth building properly before any of the others.",
     [("Entryway", ["Landing Zone"]), ("Kitchen", ["Primary Prep Counter",
                                                    "Sink and Dishwashing Zone"]),
      ("Primary Bedroom", ["Bed and Bedding Zone", "Primary Closet"]),
      ("Primary Bathroom", ["Vanity Counter"]),
      ("Laundry Room", ["Sorting and Hamper Zone", "Folding Surface"])]),

    ("shared-house", "A Shared House",
     "The zones more than one adult uses, where a standard has to be agreed rather than imposed.",
     [("Kitchen", ["Refrigerator and Freezer", "Sink and Dishwashing Zone",
                   "Upper Cabinet Zone"]),
      ("Guest Bathroom", None), ("Laundry Room", None),
      ("Entryway", ["Landing Zone", "Shoe and Boot Zone"])]),

    ("rental-handover", "The Rental Handover",
     "What a deposit actually turns on, zone by zone, with the cleaning detail in full.",
     [("Kitchen", None), ("Primary Bathroom", None), ("Guest Bathroom", None),
      ("Entryway", ["Door, Mat, and Immediate Floor"])]),
]

AREAS = [
    ("wet-rooms", "Every Wet Room",
     "Bathrooms and the laundry: the rooms where water, chemicals and electricity meet.",
     ["Primary Bathroom", "Guest Bathroom", "Laundry Room"]),
    ("sleeping", "Every Sleeping Room",
     "All four bedrooms and the nursery, worked as one set.",
     ["Primary Bedroom", "Guest Bedroom", "Kids Bedroom", "Nursery"]),
    ("storage", "Every Storage Space",
     "The garage, the workshop, the hall closet and the pantry.",
     ["Garage", "Workshop", "Hall Closet", "Pantry"]),
    ("living", "Every Living Space",
     "The rooms people sit in, and the surfaces that collect what they carry.",
     ["Living Room", "Family Room", "Dining Room"]),
    ("thresholds", "Every Threshold",
     "Entryway, mudroom and the stair landing: where the house meets outside.",
     ["Entryway", "Mudroom", "Stair Landing"]),
    ("food", "Everywhere Food Lives",
     "The kitchen, the pantry and the dining room, as one continuous system.",
     ["Kitchen", "Pantry", "Dining Room"]),
]


def esc(t):
    return html.escape(str(t or ""), quote=True)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def load():
    return json.load(io.open(SRC, encoding="utf-8"))


def zones_of(d, room_name, only=None):
    r = next((x for x in d["rooms"] if x["room"] == room_name), None)
    if not r:
        return []
    if only is None:
        return [(r["room"], z) for z in r["zones"]]
    out = []
    for name in only:
        z = next((x for x in r["zones"] if x["zone"] == name), None)
        if z:
            out.append((r["room"], z))
    return out


def catalogue(d) -> list:
    """Every product this content supports, as data. No files written."""
    items = []

    for r in d["rooms"]:
        rs = slug(r["room"])
        for z in r["zones"]:
            n = sum(1 for k in SIX if (z.get("passes") or {}).get(k))
            items.append({
                # Truncating room and zone to fixed widths collided on five
                # pairs, for example both primary and kids bedroom dresser
                # drawers. A short hash of the full pair guarantees uniqueness
                # while the readable prefix survives for anybody reading a
                # Stripe dashboard.
                "sku": (f"ZP-{rs.upper()[:6]}-{slug(z['zone']).upper()[:8]}-"
                        + hashlib.sha256(
                            f"{r['room']}|{z['zone']}".encode()).hexdigest()[:4].upper()),
                "kind": "zone", "price": PRICE["zone"],
                "name": f"{z['zone']} Pack",
                "room": r["room"], "zones": [(r["room"], z)],
                "cards": n,
                "blurb": (f"{z['zone']} in the {r['room']}, on two printable "
                          f"pages: {n} cards, the standard that keeps it, and "
                          "the hazards to check first."),
            })

        cards = sum(1 for z in r["zones"] for k in SIX if (z.get("passes") or {}).get(k))
        items.append({
            "sku": f"RP-{rs.upper()[:10]}", "kind": "room", "price": PRICE["room"],
            "name": f"The {r['room']} Pack",
            "room": r["room"], "zones": zones_of(d, r["room"]),
            "cards": cards,
            "blurb": (f"Every zone in the {r['room'].lower()}: {len(r['zones'])} "
                      f"zones, {cards} printable cards, and the room's standards "
                      "sheet."),
        })

    for key, title, blurb, spec in SITUATIONS:
        zs = []
        for room, only in spec:
            zs += zones_of(d, room, only)
        cards = sum(1 for _, z in zs for k in SIX if (z.get("passes") or {}).get(k))
        items.append({
            "sku": f"KIT-{key.upper()[:12]}", "kind": "situation",
            "price": PRICE["situation"], "name": title, "room": None,
            "zones": zs, "cards": cards,
            "blurb": f"{blurb} {len(zs)} zones, {cards} cards.",
        })

    for key, title, blurb, rooms in AREAS:
        zs = []
        for room in rooms:
            zs += zones_of(d, room)
        cards = sum(1 for _, z in zs for k in SIX if (z.get("passes") or {}).get(k))
        items.append({
            "sku": f"AB-{key.upper()[:12]}", "kind": "area",
            "price": PRICE["area"], "name": title, "room": None,
            "zones": zs, "cards": cards,
            "blurb": f"{blurb} {len(rooms)} rooms, {len(zs)} zones, {cards} cards.",
        })

    return items


CSS = """
@page { size: letter; margin: 0.4in; }
*{box-sizing:border-box}
body{margin:0;background:#EFE7D6;color:#2B2622;
  font-family:"Newsreader",Georgia,serif;-webkit-print-color-adjust:exact;
  print-color-adjust:exact}
.intro{max-width:7.3in;margin:0 auto;padding:32px 20px 8px}
.intro h1{font-family:"Fraunces",Georgia,serif;font-size:30px;margin:0 0 8px;
  letter-spacing:-.015em;line-height:1.1}
.intro p{color:#584f46;margin:0 0 9px;font-size:14.5px;line-height:1.55;max-width:76ch}
.intro .k{font-size:12px;color:#8C8478;font-family:"Inter",Arial,sans-serif}
.sheet{display:grid;grid-template-columns:repeat(3,2.5in);grid-auto-rows:3.5in;
  gap:0;justify-content:center;margin:0 auto}
.card{width:2.5in;height:3.5in;overflow:hidden;background:#FBF7EF;
  border:1px solid #E2D8C4;border-top:5px solid var(--c);
  padding:.16in .17in .14in;display:flex;flex-direction:column}
.chead{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.badge{font-family:"Inter",Arial,sans-serif;font-size:6.6pt;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--c);
  padding:2.5px 7px;border-radius:99px}
.no{font-family:"Inter",Arial,sans-serif;font-size:6pt;color:#8C8478;font-weight:600}
.where{font-family:"Inter",Arial,sans-serif;font-size:6.2pt;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;color:var(--c);margin:0 0 2px}
.zone{font-family:"Fraunces",Georgia,serif;font-size:11.5pt;line-height:1.12;
  margin:0 0 4px;letter-spacing:-.01em}
.do{font-size:7.6pt;line-height:1.36;margin:0 0 5px}
.foot{display:flex;gap:2px;align-items:center;margin-top:auto;padding-top:5px;
  border-top:1px solid #E2D8C4}
.foot i{width:9px;height:3px;border-radius:1px;display:block}
.foot span{margin-left:auto;font-family:"Inter",Arial,sans-serif;font-size:5pt;
  letter-spacing:.05em;text-transform:uppercase;color:#8C8478;font-weight:700}
.std{max-width:7.3in;margin:0 auto;padding:18px 20px;background:#FBF7EF;
  border-left:4px solid #6E8B5B;border-radius:0 10px 10px 0}
.std h2{font-family:"Fraunces",Georgia,serif;font-size:17px;margin:0 0 10px}
.std .z{margin:0 0 12px}
.std .zn{font-family:"Inter",Arial,sans-serif;font-size:8.5pt;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:#6E8B5B;margin:0 0 3px}
.std p{margin:0 0 4px;font-size:13px;line-height:1.45}
.std .tg{font-size:11.5px;color:#584f46;padding-left:9px;
  border-left:2px solid #DDA63A}
@media print{ body{background:#fff} .intro{display:none}
  .sheet{page-break-after:always;break-after:page}
  .sheet:last-of-type{page-break-after:auto} }
"""

DOTS = "".join(f'<i style="background:{COLOUR[s]}"></i>' for s in SIX)


def trim(t, n):
    t = " ".join(str(t or "").split())
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(" ,.;:") + " ..."


def render(item) -> str:
    """One product, as a printable HTML file a buyer opens and prints."""
    cards = []
    for room, z in item["zones"]:
        for s in SIX:
            body = (z.get("passes") or {}).get(s)
            if not body:
                continue
            cards.append((room, z["zone"], s, body))

    sheets = []
    for i in range(0, len(cards), 9):
        sheets.append('<div class="sheet">')
        for j, (room, zone, s, body) in enumerate(cards[i:i + 9], start=i + 1):
            sheets.append(
                f'<div class="card" style="--c:{COLOUR[s]}">'
                f'<div class="chead"><span class="badge">{s}</span>'
                f'<span class="no">{j} / {len(cards)}</span></div>'
                f'<p class="where">{esc(room)}</p>'
                f'<p class="zone">{esc(zone)}</p>'
                f'<p class="do">{esc(trim(body, 330))}</p>'
                f'<div class="foot">{DOTS}<span>Safety is the 4th S</span></div>'
                "</div>")
        sheets.append("</div>")

    stds = ['<div class="std"><h2>The standards that keep these zones</h2>']
    for room, z in item["zones"]:
        lb = z.get("leave_behind") or {}
        if not lb.get("standard"):
            continue
        stds.append(f'<div class="z"><p class="zn">{esc(room)} &middot; '
                    f'{esc(z["zone"])}</p>'
                    f'<p>{esc(lb["standard"])}</p>'
                    + (f'<p class="tg">{esc(lb["trigger"])}</p>'
                       if lb.get("trigger") else "") + "</div>")
    stds.append("</div>")

    intro = (f'<div class="intro"><h1>{esc(item["name"])}</h1>'
             f'<p>{esc(item["blurb"])}</p>'
             "<p>Print on card stock if you have it. Nine cards to a US Letter "
             "page at two and a half by three and a half inches, the same size "
             "as every other 6S Success deck, so they shuffle together.</p>"
             "<p>Work one card at a time, in order. Sorting after you have "
             "arranged things means arranging things you were about to remove."
             "</p>"
             '<p class="k">6S Success &middot; 6s-success.com &middot; '
             "Sort, Straighten, Shine, Safety, Standardize, Sustain. "
             "Safety is the fourth S.</p></div>")

    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{esc(item['name'])}</title><style>{CSS}</style></head>"
            "<body>" + intro + "".join(sheets) + "".join(stds) + "</body></html>")


def build_all(items) -> int:
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for item in items:
        html_doc = render(item)
        path = os.path.join(OUT, f"{item['sku']}.html")
        io.open(path, "w", encoding="utf-8", newline="").write(html_doc)
        total += len(html_doc.encode())
        # A product file that holds no cards is a listing for nothing.
        got = html_doc.count('class="card"')
        assert got == item["cards"], (
            f"{item['sku']} rendered {got} cards, expected {item['cards']}")
    return total


def main() -> int:
    d = load()
    items = catalogue(d)

    by = {}
    for i in items:
        by[i["kind"]] = by.get(i["kind"], 0) + 1
    print(f"  {len(items)} products the content supports\n")
    for k in ("zone", "room", "situation", "area"):
        print(f"    {k:11} {by.get(k,0):>4}  at ${PRICE[k]}")

    # Every product must contain something. A zero card product would be a
    # listing for nothing, which is the one thing this catalogue must never do.
    empty = [i["sku"] for i in items if not i["zones"] or i["cards"] == 0]
    assert not empty, f"products with no content: {empty[:5]}"

    # Nothing here may cost as much as the product that contains all of it.
    # This is the check that would have stopped six $24 bundles going live
    # above a $19 superset on the same page.
    over = [(i["sku"], i["price"]) for i in items if i["price"] >= WHOLE_HOUSE]
    assert not over, (
        f"{len(over)} products priced at or above the ${WHOLE_HOUSE} whole "
        f"house pack, which contains all of them: {over[:4]}. A customer who "
        f"noticed would be right to feel misled.")

    dupes = [s for s in {i["sku"] for i in items}
             if sum(1 for i in items if i["sku"] == s) > 1]
    assert not dupes, f"duplicate SKUs: {dupes[:5]}"

    # A curated kit that names a zone the spine does not have would ship a
    # product missing a piece somebody paid for.
    named = sum(len(only) for _, _, _, spec in SITUATIONS
                for _, only in spec if only)
    got = sum(len(zones_of(d, room, only)) for _, _, _, spec in SITUATIONS
              for room, only in spec if only)
    assert named == got, (
        f"{named - got} zone(s) named in a situation kit do not exist in "
        "content.json. Fix the name or the kit ships short.")

    print(f"\n  checked: no empty products, no duplicate SKUs, and all {named} "
          "hand named zones resolve")
    print(f"  existing catalogue adds 6 buyable and 3 free, so the shop would "
          f"carry {len(items) + 9}")

    if "--build" in sys.argv:
        total = build_all(items)
        avg = total // len(items) // 1024
        print("")
        print(f"  wrote {len(items)} product files to build/products/")
        print(f"  {total // 1024} KB total, {avg} KB average")
        print("  every file checked: card count matches its catalogue entry")
    else:
        print("  --check only. Re-run with --build to write the files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
