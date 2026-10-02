#!/usr/bin/env python3
"""
Put the book's zone-map drawings on the eleven room pages that have no artwork.

WHAT WAS ACTUALLY WRONG
-----------------------
Nine of the twenty room pages carry a real figure from the book. The other
eleven carried a typographic panel: a dark slab quoting the room's own first
tip, added 2026-09-30 so the page had something to look at. Rendering one and
reading it showed what the markup could not. On site/rooms/garage.html the
panel's text is the same paragraph as the "Start here." callout a few hundred
pixels below it, and the lede above says the same thing a third time, so the
page opened by making one point three times and calling the third one a
picture. A third of the slab was empty because the text wraps at 46 characters
inside a 900-unit box.

Meanwhile every one of those eleven chapters already contains four finished
hand-drawn SVG figures, and one of them is exactly the right thing for a room
page: an overhead plan of the room as its numbered micro zones. It is real
artwork, it is first-party, it is vector so it costs about 2.7 KB and stays
sharp at any width, and it answers "what am I looking at" in a way no
restatement of the prose can.

So the eleven pages were not short of a picture. Nothing had ever gone and
got the one that was already drawn.

WHAT THIS REFUSES TO IMPORT
---------------------------
The site's own standard, written in ops/wire_zone_heroes.py, is that a figure
must never imply a photograph of a real home exists when it does not, on the
grounds that it is the same class of error as a fabricated testimonial. The
book speaks more loosely: chapter 50 calls one of these same typographic cards
"the left-hand photograph". That is the author's voice about a photograph the
reader is being asked to take, and it is not this file's business to rewrite
it, but it must not be carried onto the website either. So any figure whose
caption or accessible name calls itself a photograph is refused, loudly, and
the eleven zone maps are checked to be clear of it rather than assumed to be.

Every import is also checked against the corpus: the drawing's own accessible
name must name the room it is being imported for, and the zone count in its
heading must match the number of zones content.json says that room has. A
diagram that disagrees with the manual is not imported, which is the check
that would have caught the frozen laundry-room heading six chapters carried
until 2026-10-01 had it existed then.

Run:  python ops/import_room_diagrams.py --check
      python ops/import_room_diagrams.py --apply
"""
import glob
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, "content", "book")
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")
PHOTOS = os.path.join(ROOT, "ops", "room-images.json")
OUT = os.path.join(ROOT, "ops", "room-diagrams.json")

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10}

# The book's first room chapter. Room N in the corpus is chapter 31 + N.
FIRST_CHAPTER = 31


def corpus_rooms():
    data = json.load(io.open(CORPUS, encoding="utf-8"))
    return [(r["room"], len(r["zones"])) for r in data["rooms"]]


def photographed():
    if not os.path.exists(PHOTOS):
        return set()
    return set(json.load(io.open(PHOTOS, encoding="utf-8")).keys())


def zone_map_figure(chapter):
    """The chapter's zone-map figure, or None.

    Identified by a <text> reading "drawn as its N zones" inside the drawing.
    Deliberately not by position: the figures are not in the same order in
    every chapter, and an index would silently import the wrong picture.
    """
    files = glob.glob(os.path.join(BOOK, "*Chapter-%d" % chapter,
                                   "chapter_%d_final.html" % chapter))
    if not files:
        return None
    s = io.open(files[0], encoding="utf-8", errors="replace").read()
    for fig in re.findall(r"<figure[^>]*>.*?</figure>", s, re.S):
        if re.search(r"<text[^>]*>[^<]*drawn as its [a-z]+ zones", fig):
            return fig
    return None


def caption_of(fig):
    m = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def svg_of(fig):
    m = re.search(r"<svg.*?</svg>", fig, re.S)
    return m.group(0) if m else ""


def problems(room, zones, fig):
    """Everything wrong with importing this figure for this room."""
    out = []
    svg = svg_of(fig)
    if not svg:
        return ["no <svg> in the figure"]

    aria = re.search(r'aria-label="([^"]*)"', svg)
    if not aria:
        out.append("the drawing has no accessible name, so nothing states "
                   "which room it draws")
    else:
        m = re.search(r"of an? ([a-z ]+?) with its ([a-z]+) zones", aria.group(1))
        if not m:
            out.append("accessible name does not state a room and a zone "
                       "count: %r" % aria.group(1))
        else:
            drawn_room, count_word = m.group(1).strip(), m.group(2).strip()
            # "patio" for "Patio or Deck", "landing" for "Stair Landing": the
            # book shortens, which is fine, so this asks that the drawing's
            # room is a word of the corpus room rather than equal to it.
            words = set(re.findall(r"[a-z]+", room.lower()))
            if not (set(re.findall(r"[a-z]+", drawn_room)) & words):
                out.append("drawing says it is %r, which shares no word with "
                           "%r" % (drawn_room, room))
            want = WORDS.get(count_word)
            if want is None:
                out.append("unreadable zone count %r" % count_word)
            elif want != zones:
                out.append("drawing says %s zones, the manual says %d"
                           % (count_word, zones))

    heading = [re.sub(r"<[^>]+>", "", t)
               for t in re.findall(r"<text[^>]*>.*?</text>", svg, re.S)
               if "drawn as its" in t]
    if heading and aria:
        m = re.search(r"of an? ([a-z ]+?) with its ([a-z]+) zones", aria.group(1))
        if m and m.group(1).strip() not in heading[0].lower():
            out.append("visible heading %r does not name %r"
                       % (heading[0], m.group(1).strip()))

    # The site's own rule: never imply a photograph that does not exist.
    words = (caption_of(fig) + " " + (aria.group(1) if aria else "")).lower()
    if re.search(r"\bphotograph|\bphoto\b", words):
        out.append("calls itself a photograph, and it is a drawing "
                   "(ops/wire_zone_heroes.py's standard)")

    if re.search(r'(?:href|xlink:href)="[^"#]', svg):
        out.append("references something outside itself, so it would not be "
                   "self contained on the page")
    if re.search(r'<svg[^>]*\swidth="', svg):
        out.append("carries a fixed width, which overflows a phone viewport")
    if re.findall(r'\bid="', svg):
        out.append("carries an id, which can collide with the page's own")
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        out.append("is not well-formed XML: %s" % exc)
    return out


HOUSE_GAP = 40          # the breathing room every other diagram leaves


def tighten(svg):
    """Close a dead band under the last row of zones.

    Ten of the eleven drawings leave 25 to 40 units between the bottom of the
    last zone box and the strapline. The Stair Landing leaves 200, because it
    has three zones and the builder it was copied from lays out two rows. In
    the book that is a quiet oddity on a page of its own. On a room page it is
    a band of empty cream under a single row, and it reads as a rendering
    fault rather than a design.

    This moves the strapline up to the house gap and shrinks the canvas to
    match. It changes geometry only: no text, no colour, no element added or
    removed, and it does nothing at all when the gap is already normal, so ten
    of the eleven pass through untouched. Returns (svg, note) and the note goes
    into the manifest, so an edit to the book's own artwork is never silent.
    """
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not vb:
        return svg, ""
    width, height = int(vb.group(1)), int(vb.group(2))
    boxes = [(float(m.group(1)), float(m.group(2)))
             for m in re.finditer(r'<rect[^>]*y="([\d.]+)"[^>]*height="([\d.]+)"', svg)
             if 'width="%d"' % width not in m.group(0)]
    strap = re.search(r'<text[^>]*y="([\d.]+)"[^>]*font-size="17"[^>]*>', svg)
    if not boxes or not strap:
        return svg, ""
    bottom = max(y + h for y, h in boxes)
    strap_y = float(strap.group(1))
    gap = strap_y - bottom
    if gap <= HOUSE_GAP * 2:
        return svg, ""
    new_strap = int(bottom + HOUSE_GAP)
    below = height - strap_y            # whatever the canvas leaves beneath it
    new_height = int(new_strap + below)
    out = svg.replace(strap.group(0),
                      strap.group(0).replace('y="%s"' % strap.group(1),
                                             'y="%d"' % new_strap), 1)
    out = out.replace('viewBox="0 0 %d %d"' % (width, height),
                      'viewBox="0 0 %d %d"' % (width, new_height), 1)
    # The full-width background rect, so it stops where the canvas now does.
    out = re.sub(r'(<rect[^>]*width="%d"[^>]*height=")%d(")' % (width, height),
                 r'\g<1>%d\g<2>' % new_height, out, count=1)
    note = ("strapline moved from y=%d to y=%d and the canvas from %d to %d, "
            "closing a %d unit dead band under the last row"
            % (strap_y, new_strap, height, new_height, gap))
    return out, note


def collect():
    """(manifest, skipped) where skipped says why, for every room."""
    photos = photographed()
    manifest, skipped = {}, []
    for i, (room, zones) in enumerate(corpus_rooms()):
        if room in photos:
            skipped.append((room, "already has the book's own figures"))
            continue
        fig = zone_map_figure(FIRST_CHAPTER + i)
        if fig is None:
            skipped.append((room, "its chapter has no zone-map drawing"))
            continue
        bad = problems(room, zones, fig)
        if bad:
            skipped.append((room, "; ".join(bad)))
            continue
        svg, note = tighten(svg_of(fig))
        entry = {
            "chapter": FIRST_CHAPTER + i,
            "svg": svg,
            "caption": caption_of(fig),
        }
        if note:
            entry["layout_note"] = note
        manifest[room] = entry
    return manifest, skipped


def load_committed():
    if not os.path.exists(OUT):
        return {}
    return json.load(io.open(OUT, encoding="utf-8"))


def main(argv):
    manifest, skipped = collect()
    committed = load_committed()

    print("%d room(s) would carry the book's zone-map drawing:" % len(manifest))
    for room in sorted(manifest):
        e = manifest[room]
        print("    %-18s ch%-3d %5d bytes  %s"
              % (room, e["chapter"], len(e["svg"]), e["caption"][:60]))
    if skipped:
        print()
        print("%d room(s) skipped:" % len(skipped))
        for room, why in skipped:
            print("    %-18s %s" % (room, why))

    # NEVER SHRINK. The same rule ops/import_room_images.py learned: a rerun
    # that finds less than what already shipped must not act on it, because
    # the cause is far more often a broken source path than a deleted figure.
    lost = [r for r in committed if r not in manifest]
    if lost:
        print()
        print("REFUSING TO WRITE: %d room(s) already committed would be "
              "dropped by this run: %s. Investigate the source before "
              "trusting it." % (len(lost), ", ".join(sorted(lost))))
        return 1

    if "--apply" not in argv:
        print()
        print("Run with --apply to write %s" % os.path.relpath(OUT, ROOT))
        return 0

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print()
    print("wrote %s (%d rooms)" % (os.path.relpath(OUT, ROOT), len(manifest)))
    print("Now run: python ops/build_zone_pages.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
