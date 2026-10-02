#!/usr/bin/env python3
"""
Prove no room chapter's zone map names a different room than the one it draws.

FOUND LIVE 2026-10-01, BY RENDERING THE ARTWORK AND LOOKING AT IT
-----------------------------------------------------------------
Chapters 44 to 49 of the book each carried, as the visible heading of their
zone-map figure, the string:

    "The laundry room, drawn as its six zones"

Chapter 43 is the Laundry Room, and it is correct there. The other six are the
Home Office, Garage, Workshop, Mudroom, Hall Closet and Stair Landing. Under
that heading each drew its own zones correctly, so chapter 45 announced a
laundry room and listed seven garage zones, and chapter 49 announced six zones
over the three a stair landing has. The strapline beneath, "one room, six small
jobs, and five of them wait on the machines", is about a washer and a dryer and
was sitting in a garage, a workshop and a hall closet.

Nothing could have caught it. Every chapter was internally consistent in every
respect a checker looks at: the figure's own aria-label, its figcaption and the
count of numbered zones inside the drawing all named the right room and the
right number in all twenty chapters. Only the two visible strings were copied,
which is the defect class this repository already knows by name: when you copy
a builder, diff its literal strings and not just its variables.

It was also an accessibility defect in an unusual direction. The aria-label
said "a garage with its seven zones" while the visible title said laundry room
with six, so a screen-reader user got the truth and a sighted reader did not.

WHAT THIS CHECKS, AND WHY IT NEEDS NO EXTERNAL DATA
---------------------------------------------------
The figure already contains its own answer twice over. The accessible name
carries the room and the count, and the drawing carries one numbered label per
zone. So the invariant is internal: the visible heading must agree with the
accessible name, and both must agree with the number of zones actually drawn.
A chapter cannot satisfy that by copying another chapter's string.

Run:  python ops/tests/test_book_zone_map_strings.py
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOK = os.path.join(ROOT, "content", "book")

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10}


# The heading form, and only the heading form. An earlier version of this
# selector matched any figure containing "drawn as", which also appears in
# ordinary caption prose across a dozen chapters ("drawn as a single run",
# and so on), so it reported 24 false problems on its first run. The zone map
# is identifiable by a <text> element inside the drawing that reads "drawn as
# its N zones", which no caption does.
HEADING = re.compile(r"<text[^>]*>[^<]*drawn as its [a-z]+ zones[^<]*</text>", re.I)


def zone_map_figures():
    """(path, figure html) for every zone-map figure in the book."""
    out = []
    pattern = os.path.join(BOOK, "*", "chapter_*_final.html")
    extra = os.path.join(BOOK, "*", "content-package", "chapter-*-publishable.html")
    for path in sorted(glob.glob(pattern)) + sorted(glob.glob(extra)):
        s = io.open(path, encoding="utf-8", errors="replace").read()
        for fig in re.findall(r"<figure[^>]*>.*?</figure>", s, re.S):
            if HEADING.search(fig):
                out.append((path, fig))
    return out


def heading_of(fig):
    for t in re.findall(r"<text[^>]*>.*?</text>", fig, re.S):
        if "drawn as" in t:
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()
    return ""


def main():
    fails = []
    figs = zone_map_figures()

    # 1. A test that found nothing would be worthless. 16 room chapters carry
    #    a zone map, in two packaged copies each, so 32 is the real figure and
    #    anything well under it means this stopped looking rather than stopped
    #    finding problems.
    if len(figs) < 30:
        fails.append("only %d zone-map figure(s) found under content/book, "
                     "against the 32 that exist, so this test stopped looking "
                     "rather than stopped finding problems" % len(figs))

    for path, fig in figs:
        rel = os.path.relpath(path, ROOT)
        heading = heading_of(fig)
        if not heading:
            fails.append("%s: a figure says 'drawn as' but has no heading "
                         "text element" % rel)
            continue

        aria = re.search(r'aria-label="([^"]*)"', fig)
        if not aria:
            fails.append("%s: zone map has no accessible name, so nothing "
                         "states the room it draws" % rel)
            continue
        m = re.search(r"of an? ([a-z ]+?) with its ([a-z]+) zones",
                      aria.group(1))
        if not m:
            fails.append("%s: accessible name does not state a room and a "
                         "zone count: %r" % (rel, aria.group(1)))
            continue
        room, count = m.group(1).strip(), m.group(2).strip()

        # 2. The visible heading must name the room the figure says it draws.
        if room not in heading.lower():
            fails.append("%s: heading %r does not name %r, which is the room "
                         "its own accessible name says it draws"
                         % (rel, heading, room))

        # 3. And the same zone count.
        if count not in heading.lower():
            fails.append("%s: heading %r does not carry the zone count %r "
                         "from its own accessible name" % (rel, heading, count))

        # 4. The count must match the zones actually drawn, so a chapter
        #    cannot be internally consistent and still wrong, which is how
        #    chapter 49 announced six zones over three.
        drawn = len({n for n in re.findall(r"<text[^>]*>([1-9])</text>", fig)})
        want = WORDS.get(count)
        if want and drawn and drawn != want:
            fails.append("%s: heading says %s zones, the drawing has %d "
                         "numbered zones" % (rel, count, drawn))

        # 5. The strapline must not describe a different room's equipment.
        #    "five of them wait on the machines" is about a washer and a
        #    dryer, and it shipped in a garage, a workshop and a hall closet.
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fig)).lower()
        if "wait on the machines" in flat and "laundry" not in room:
            fails.append("%s: a %s carries the laundry room's strapline about "
                         "waiting on the machines" % (rel, room))

    if fails:
        print("FAIL")
        for f in sorted(set(fails)):
            print(" -", f)
        return 1
    print("OK: %d zone-map figure(s), every heading agrees with its own "
          "accessible name and the zones it draws" % len(figs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
