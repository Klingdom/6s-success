#!/usr/bin/env python3
"""
Draw the eleven room maps as real plans of the room, not a grid of empty boxes.

WHAT WAS WRONG
--------------
Eleven room pages have no photographic figure from the book, so since
2026-10-01 they lead on the chapter zone map (ops/import_room_diagrams.py).
Rendered, that map is a grid of identical cream rectangles with a number and a
name in the corner of each and nothing else: seven empty boxes for the garage,
under a heading that promises "the garage, drawn as its seven zones". It tells
the reader the zone names, which the list directly beneath it already does,
and nothing about the room: where the bench is relative to the car, that the
overhead racks hang above the hood, that the mower lives by the big door.

It also contradicted the page in three rooms. The book numbers zones in the
order it recommends doing them (Workshop starts at the PPE station, Patio at
the boards, Stair Landing at the flight), while every room page lists them in
the manual order. So on those three pages the "1" on the map and the "1" in
the list underneath were different zones.

WHAT THIS DRAWS
---------------
An overhead plan (a front elevation for the hall closet, which is one wall of
shelves) with walls, doors and the furniture each zone actually is, drawn
plainly enough to recognise: a car from above, a washer drum, crib slats,
treads on a flight. Every zone gets a dashed outline around what it covers and
a numbered label with a leader line to it.

Rules it keeps:

* Numbers follow content.json zone order, the order the room page lists them,
  so the map and the list agree. The zone the page tells you to start with
  carries a "start here" tag instead of being renumbered 1.
* No six-S hue is used as decoration (PLAN-VISUAL-STRATEGY.md section 8).
* The constraints the importer enforces: room and zone count in the accessible
  name, no id, no external reference, no fixed width, well-formed XML, never
  called a photograph.
* Labels are sized for the 1.4x enlargement DIAGRAM_CSS applies on phones;
  ops/tests/test_room_diagram_fits.py measures that in a real browser.

Output is ops/room-maps.json, which build_zone_pages.py reads in preference to
ops/room-diagrams.json. The importer and its book-derived file are untouched,
so the book drawings stay recoverable and diffable.

Run:  python ops/build_room_maps.py                 # build and check
      python ops/build_room_maps.py --apply         # write ops/room-maps.json
      python ops/build_room_maps.py --preview x.html
"""
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from room_map_draw import *          # noqa: E402,F401,F403
import room_map_draw as D            # noqa: E402,F401
import room_map_layouts as L         # noqa: E402
from room_map_assemble import to_canvas  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")
BOOK_DIAGRAMS = os.path.join(ROOT, "ops", "room-diagrams.json")
OUT = os.path.join(ROOT, "ops", "room-maps.json")

NUM_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


class Labels:
    """Numbered zone labels with leader lines, drawn after everything else.

    Last on purpose: ops/tests/test_room_diagram_fits.py assigns each piece
    of text to the last rect containing its start point, so a label chip must
    come after any furniture it sits over.
    """

    H = 34

    def __init__(self, names, start):
        self.names, self.start = names, start
        self.leaders, self.parts, self.placed = [], [], set()

    # Rough advance widths for Fraunces at the 21px the phone CSS sets, by
    # letter shape. A flat per-letter figure under-sized short labels full of
    # wide letters ("Workbench" missed by 3 units in the browser test) while
    # over-sizing long ones, so width is summed by shape instead.
    NARROW, WIDE = set("ijlt.,'-fr"), set("mwMW")

    def text_width(self, s):
        w = 0.0
        for ch in s:
            if ch == " ":
                w += 5.6
            elif ch in self.NARROW:
                w += 6.8
            elif ch in self.WIDE:
                w += 17.5
            elif ch.isupper():
                w += 14.5
            else:
                w += 11.6
        return w

    def width(self, i):
        return 37 + self.text_width(self.names[i]) + 22

    def add(self, i, x, y, to=None, align="left"):
        """Label zone i (0-based) with its chip at (x, y), leader to `to`."""
        w, h = self.width(i), self.H
        if align == "right":
            x -= w
        elif align == "center":
            x -= w / 2
        self.placed.add(i)
        if to is not None:
            tx, ty = to_canvas(*to)
            if y <= ty <= y + h:
                sx, sy = (x if tx < x else x + w), y + h / 2
            else:
                sx = min(max(tx, x + 16), x + w - 16)
                sy = y + h if ty > y + h else y
            self.leaders.append(line(sx, sy, tx, ty, stroke=SLATE, sw=1.5)
                                + circle(tx, ty, 4.2, fill=SLATE, sw=0))
        p = [rect(x, y, w, h, fill="#FFFDF8", stroke=SLATE, sw=1.4, rx=17),
             circle(x + 18, y + h / 2, 12, fill=SLATE, sw=0),
             '<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
             'font-size="13" font-weight="600" fill="%s">%d</text>'
             % (f(x + 18), f(y + h / 2 + 4.5), SANS, PAPER, i + 1),
             '<text x="%s" y="%s" font-family="%s" font-size="15" fill="%s">'
             '%s</text>' % (f(x + 37), f(y + h / 2 + 5), SERIF, INK,
                            esc(self.names[i]))]
        if i == self.start:
            tw = 96
            tx0 = x + w - tw - 4
            p.append(rect(tx0, y - 22, tw, 22, fill=SLATE, stroke=SLATE,
                          sw=1, rx=11))
            p.append('<text x="%s" y="%s" text-anchor="middle" '
                     'font-family="%s" font-size="13" font-weight="600" '
                     'fill="%s">start here</text>'
                     % (f(tx0 + tw / 2), f(y - 6.5), SANS, PAPER))
        self.parts.append("".join(p))

    def svg(self):
        return "".join(self.leaders) + "".join(self.parts)


# ------------------------------------------------------------- registry/main
#
# room: (draw, start-here zone index, noun, short labels in content.json
# order, strapline, kind of drawing). The start index comes from each room
# page "Start here." callout, so the tag and the prose agree.

ROOMS = {
    "Garage": (L.garage, 0, "garage",
               ["Workbench", "Hand tool wall", "Power tools",
                "Automotive care", "Sports and rec", "Lawn and garden",
                "Overhead storage"],
               "one room, seven small jobs", "overhead plan"),
    "Guest Bathroom": (L.guest_bathroom, 0, "guest bathroom",
                       ["Vanity counter", "Vanity storage", "Shower or tub",
                        "Toilet area", "Guest linen"],
                       "one room, five small jobs", "overhead plan"),
    "Hall Closet": (L.hall_closet, 0, "hall closet",
                    ["Linen shelf", "Cleaning equipment",
                     "Cleaning supplies", "Paper backstock",
                     "Seasonal and guest"],
                    "one closet, five small jobs", "front view"),
    "Home Office": (L.home_office, 0, "home office",
                    ["Primary desk", "Desk drawers", "File storage",
                     "Bookshelf", "Printer station", "Supply cabinet"],
                    "one room, six small jobs", "overhead plan"),
    "Laundry Room": (L.laundry_room, 0, "laundry room",
                     ["Washer and dryer", "Detergent shelf",
                      "Sorting hampers", "Folding surface", "Air-dry rack",
                      "Utility corner"],
                     "one room, six small jobs", "overhead plan"),
    "Mudroom": (L.mudroom, 0, "mudroom",
                ["Family hooks", "Bench", "Shoes and boots", "Pet station",
                 "Seasonal gear", "Cleaning corner"],
                "one room, six small jobs", "overhead plan"),
    "Nursery": (L.nursery, 0, "nursery",
                ["Crib and sleep", "Changing station", "Baby clothing",
                 "Feeding station", "Diaper backstock", "Books and play"],
                "one room, six small jobs", "overhead plan"),
    "Patio or Deck": (L.patio_or_deck, 5, "patio",
                      ["Outdoor seating", "Grill and cooking",
                       "Outdoor dining", "Garden and plants",
                       "Outdoor storage", "Surface and rail"],
                      "the boards come first, because everything else "
                      "stands on them", "overhead plan"),
    "Primary Bathroom": (L.primary_bathroom, 0, "primary bathroom",
                         ["Vanity counter", "Vanity drawers", "Under-sink",
                          "Medicine cabinet", "Shower or tub", "Toilet area",
                          "Linen storage"],
                         "one room, seven small jobs", "overhead plan"),
    "Stair Landing": (L.stair_landing, 2, "stair landing",
                      ["Landing console", "Wall and display",
                       "Stair and floor path"],
                      "the flight first: clear treads and working light "
                      "set the limit for the rest", "overhead plan"),
    # Pantry and Family Room lead on the book's photographs, so their room
    # pages never show these plans (a figure always wins in
    # build_zone_pages.py). They are drawn for their shop pack image, which
    # needs a picture of the whole room and the book has none.
    "Pantry": (L.pantry, 0, "pantry",
               ["Dry goods", "Canned and jarred", "Baking zone",
                "Snack and lunch", "Backstock and bulk"],
               "one room, five small jobs", "overhead plan"),
    "Family Room": (L.family_room, 0, "family room",
                    ["Media zone", "Toy and play", "Board games",
                     "Blanket basket", "Charging", "Craft table"],
                    "one room, six small jobs", "overhead plan"),
    "Workshop": (L.workshop, 5, "workshop",
                 ["Main workbench", "Power tools", "Fasteners",
                  "Material rack", "Finishing", "PPE station"],
                 "safety first: the smallest zone is the permission to begin",
                 "overhead plan"),
}


# Captions are the book's own words, carried over, except where they lean on
# the book's numbering. The book numbers the patio boards 1 ("the first one
# holds you"); this map numbers them 6 to match the page list, so that one
# sentence would now point at the seating.
CAPTIONS = {
    "Patio or Deck": "One zone is not like the others. Five of them hold "
                     "things. The boards and the rail hold you, which is why "
                     "they come first.",
}


def main(argv):
    import room_map_assemble as A
    names_by_room = A.corpus(CORPUS)
    book = json.load(io.open(BOOK_DIAGRAMS, encoding="utf-8"))
    manifest, bad = {}, []
    for room, spec in ROOMS.items():
        if room not in names_by_room:
            bad.append((room, "not a room in content.json"))
            continue
        svg, L = A.build(spec, Labels)
        p = A.problems(spec, len(names_by_room[room]), svg, L)
        if p:
            bad.append((room, "; ".join(p)))
            continue
        manifest[room] = {
            "caption": CAPTIONS.get(room)
                       or book.get(room, {}).get("caption", ""),
            "chapter": book.get(room, {}).get("chapter"),
            "source": "site",
            "svg": svg,
        }
        print("    %-18s %6d bytes" % (room, len(svg)))
    missing = sorted(set(book) - set(ROOMS))
    if missing:
        print("not yet drawn here, still on the book map: %s"
              % ", ".join(missing))
    for room, why in bad:
        print("FAIL %s: %s" % (room, why))
    if "--preview" in argv:
        A.write_preview(argv[argv.index("--preview") + 1], manifest)
    if bad:
        return 1
    if "--apply" in argv:
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(manifest, fh, indent=1, ensure_ascii=False,
                      sort_keys=True)
            fh.write("\n")
        print("wrote %s (%d rooms)" % (os.path.relpath(OUT, ROOT),
                                       len(manifest)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
