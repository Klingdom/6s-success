#!/usr/bin/env python3
"""
The Micro Zone Map: twenty printable sheets, one per room, every zone on it.

WHY THIS PRODUCT EXISTS
-----------------------
The micro zone is what this project has that a shelf of organising books does
not, and until now a household could only meet the idea one page at a time, by
browsing the site. There was nothing to put on the fridge that says: your
kitchen is seven small places, here they are, in this order, and here is how
long each one takes.

Built entirely from ops/zone_graphics.py, which draws from content.json, so a
sheet cannot claim a zone the site does not have. It is free, it prints on
plain paper, and it is deliberately a map rather than instructions: the
instructions are the zone pages, the deck and the book.

One room per page, twenty pages, checked by printing it rather than by
counting sections in the HTML.

    python ops/build_zone_map_pack.py
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

OUT_BUILD = os.path.join(ROOT, "build", "6S-Micro-Zone-Map.html")
OUT_SITE = os.path.join(ROOT, "site", "downloads", "6S-Micro-Zone-Map.html")

CSS = """
:root{--paper:#F7F2E9;--ink:#2B2622;--soft:#6A625A;--line:#E2D8C4;
  --terra:#BC4B2A}
*{box-sizing:border-box}
body{margin:0;background:#EFE8DC;color:var(--ink);
  font-family:Inter,-apple-system,Segoe UI,Helvetica,Arial,sans-serif}
.intro{max-width:7.3in;margin:26px auto;padding:22px 26px;background:#fff;
  border:1px solid var(--line);border-radius:12px}
.intro h1{font-family:Fraunces,Georgia,serif;font-size:30px;margin:0 0 10px}
.intro p{font-size:15px;line-height:1.6;color:#4a443d;margin:0 0 10px}
.sheet{width:7.9in;margin:0 auto 22px;background:var(--paper);
  border:1px solid var(--line);padding:0.42in;page-break-after:always;
  break-after:page}
.sheet:last-child{page-break-after:auto;break-after:auto}
.sheet svg{display:block;width:100%;height:auto}
.foot{display:flex;justify-content:space-between;align-items:center;
  margin-top:14px;font-size:11pt;color:var(--soft)}
.foot b{color:var(--terra);font-weight:700;letter-spacing:.04em}
@page{size:letter;margin:0.4in}
@media print{
  body{background:#fff}
  .intro{display:none}
  .sheet{width:auto;margin:0;border:0;padding:0}
}
"""


def main() -> int:
    import video_zone as V
    import zone_graphics as G

    rooms = {}
    for room, z in V.zones():
        rooms.setdefault(room, []).append(z)

    sheets = []
    for i, (room, zs) in enumerate(rooms.items(), 1):
        # One wide column, taller chips: a portrait page, filled.
        # Measured by printing rather than guessed: the two-column
        # map left the bottom third of every sheet blank.
        svg = G.room_map_svg(room, zs, uid=G.slug(room), cols=1,
                             cw=720, chh=104)
        sheets.append(
            '<section class="sheet">%s'
            '<div class="foot"><span><b>6S SUCCESS</b> &middot; '
            '6s-success.com/rooms/%s</span>'
            '<span>Sheet %d of %d &middot; %d micro zones</span></div>'
            '</section>' % (svg, G.slug(room), i, len(rooms), len(zs)))

    total_zones = sum(len(z) for z in rooms.values())
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>The 6S Success Micro Zone Map: every zone in twenty rooms'
        '</title>'
        '<meta name="description" content="Twenty printable sheets, one per '
        'room, naming every micro zone in the house and how long one session '
        'takes. Free to print.">'
        '<meta name="robots" content="noindex">'
        '<link rel="canonical" href="https://6s-success.com/downloads/'
        '6S-Micro-Zone-Map.html">'
        '<style>%s</style></head><body>'
        '<div class="intro"><h1>The Micro Zone Map</h1>'
        '<p>Twenty sheets, one per room. Every one of the %d micro zones in '
        'the house, numbered in the order to work them, with the time a '
        'single session takes.</p>'
        '<p>A micro zone is one small place with one job: the landing spot by '
        'the door, the prep counter, the shoe tray. It is small enough to '
        'finish, which is the whole point. Print the sheet for the room you '
        'are standing in and put it where the work happens.</p>'
        '<p>The steps for each zone are on its own page at '
        '6s-success.com/rooms, free, no account.</p></div>'
        '<main>%s</main></body></html>'
        % (CSS, total_zones, "".join(sheets)))

    for path in (OUT_BUILD, OUT_SITE):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print("  wrote %s" % os.path.relpath(OUT_BUILD, ROOT))
    print("  wrote %s" % os.path.relpath(OUT_SITE, ROOT))
    print("  %d rooms, %d micro zones, %d KB"
          % (len(rooms), total_zones, len(html) // 1024))
    assert len(rooms) == 20, "expected 20 rooms, got %d" % len(rooms)
    assert total_zones == 114, "expected 114 zones, got %d" % total_zones
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
