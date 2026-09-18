#!/usr/bin/env python3
"""
The micro zone, drawn. One SVG that says where a zone is, what it holds when
it is finished, and what brings it back.

WHY THIS EXISTS
---------------
The micro zone is the thing this project has that a shelf of organising books
does not: not "the kitchen", but the prep counter, the sink zone, the upper
cabinets, each with a job, a finish line and a trigger. Until now the pictures
on those pages were generated room photographs: pleasant, generic, and mute
about the very idea that makes the page worth reading. The local model also
could not reliably draw the one object a zone is about, which is why 3 zone
pages and 7 cards still carry no picture at all.

A diagram does what those photographs could not:
  - it shows the zone IN its room, beside its siblings, which is the model;
  - it prints the finish line as checkable items, which is the product;
  - it is generated from content.json, so it cannot drift from the page;
  - it costs nothing per image, renders identically every time, stays crisp
    at any size, and reads correctly in greyscale on a home printer.

Inlined into the page rather than linked as a file, so the site's own fonts
and colours apply, no extra request is made, and a screen reader gets the
title and description.

    python ops/zone_graphics.py --demo
"""
from __future__ import annotations

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

# The 6S colours in pass order, matching site.css --s1..--s6. Repeated here
# because an SVG on a print sheet has no stylesheet to inherit from.
S_COLOURS = ["#CB4B36", "#BC4B2A", "#D98A2B", "#DDA63A", "#6E8B5B", "#4E7A57"]
INK = "#2B2622"
SOFT = "#6A625A"
LINE = "#E2D8C4"
PANEL = "#FBF7EF"
PAPER = "#F7F2E9"
TERRA = "#BC4B2A"
GREEN = "#6E8B5B"
DEEP = "#22323C"

SANS = "Inter,-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
DISPLAY = "Fraunces,Georgia,serif"
SERIF = "Newsreader,Georgia,Times New Roman,serif"


def esc(t):
    return html.escape(str(t or ""), quote=True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def wrap(text, width):
    """Greedy wrap by characters, because SVG has no text flow."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _txt(x, y, text, font, size, fill, weight=None, anchor=None, track=None):
    """One SVG text node. Kept in one place so every label is built the same."""
    bits = ['<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s"'
            % (x, y, font, size, fill)]
    if weight:
        bits.append(' font-weight="%s"' % weight)
    if anchor:
        bits.append(' text-anchor="%s"' % anchor)
    if track:
        bits.append(' letter-spacing="%s"' % track)
    bits.append('>%s</text>' % esc(text))
    return "".join(bits)


def _ribbon(pad, width, y):
    """The six passes as a colour ribbon: the method, in one glance."""
    seg = (width - pad * 2) / 6.0
    return "".join(
        '<rect x="%.1f" y="%s" width="%.1f" height="6" rx="3" fill="%s"/>'
        % (pad + i * seg, y, seg - 6, c) for i, c in enumerate(S_COLOURS))


def _chip(x, y, w, h, label, n, current):
    """One micro zone as a chip in the room strip."""
    fill = TERRA if current else "#FFFFFF"
    stroke = TERRA if current else LINE
    text_fill = "#FFFFFF" if current else SOFT
    num_fill = "#FFFFFF" if current else TERRA
    lines = wrap(label, 20)[:2]
    ty = y + (h / 2.0) - (len(lines) - 1) * 7 + 5
    out = ['<rect x="%s" y="%s" width="%s" height="%s" rx="9" fill="%s" '
           'stroke="%s" stroke-width="1.5"/>' % (x, y, w, h, fill, stroke),
           _txt(x + 14, y + 20, n, SANS, 11, num_fill, "700", track="0.06em")]
    for i, ln in enumerate(lines):
        out.append(_txt(x + 34, ty + i * 15, ln, SANS, 12.5, text_fill,
                        "700" if current else "500"))
    return "".join(out)


def zone_diagram_svg(room, zone, siblings, done_items, uid=""):
    """The zone, its place in its room, and its finish line.

    siblings is every zone name in the room, in working order, so the reader
    sees this zone as one of a set rather than as an isolated tip. That set is
    the micro zone model, and it is the part a photograph never showed.

    THE HEIGHT IS COMPUTED, NOT CHOSEN. The first version fixed it at 560px
    and truncated whatever did not fit: checklist items ended mid-sentence
    ("...holding only the board, the knife block or strip, and the") and the
    seventh zone chip disappeared behind the footer. That is the same defect
    class as the videos that dropped "One wallet and" from a standard, and it
    is worse in a diagram, because a diagram looks finished while lying.
    Nothing here truncates a sentence; the canvas grows instead.
    """
    name = zone.get("zone", "")
    session = zone.get("session", "")
    purpose = zone.get("purpose", "")
    trigger = (zone.get("leave_behind") or {}).get("trigger", "")

    W, pad, col = 1160, 34, 440
    ch, chip_gap = 46, 8

    # ---- measure before drawing --------------------------------------
    head_h = 92                                   # eyebrow, room, count
    left_h = head_h + len(siblings) * (ch + chip_gap)

    purpose_lines = wrap(purpose, 54)
    items = []
    for item in done_items[:4]:
        items.append(wrap(item, 46))
    more = max(0, len(done_items) - len(items))
    right_h = (head_h - 26) + len(purpose_lines) * 23 + 18
    for lines in items:
        right_h += 21 * len(lines) + 16
    if more:
        right_h += 22

    body_h = max(left_h, right_h)
    H = pad + 16 + body_h + 34 + 46 + pad        # body, gap, footer, padding

    out = ['<rect x="0" y="0" width="%s" height="%s" rx="18" fill="%s" '
           'stroke="%s" stroke-width="2"/>' % (W, H, PANEL, LINE),
           _ribbon(pad, W, pad - 14)]

    # ---- left: where it is -------------------------------------------
    y = pad + 16
    out.append(_txt(pad, y + 14, "WHERE IT IS", SANS, 11.5, TERRA, "700",
                    track="0.2em"))
    out.append(_txt(pad, y + 48, room, DISPLAY, 27, INK, "600"))
    out.append(_txt(pad, y + 70, "%d micro zones, one session each"
                    % len(siblings), SANS, 12.5, SOFT))
    chip_y = y + head_h - 4
    for i, sib in enumerate(siblings):
        out.append(_chip(pad, chip_y + i * (ch + chip_gap), col - 40, ch, sib,
                         i + 1, sib == name))

    # ---- right: what done looks like ---------------------------------
    rx = pad + col
    out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
               'stroke-width="1.5"/>' % (rx - 16, pad + 6, rx - 16,
                                         pad + 16 + body_h + 10, LINE))
    out.append(_txt(rx, y + 14, "WHAT DONE LOOKS LIKE", SANS, 11.5, GREEN,
                    "700", track="0.2em"))
    ty = y + 50
    for ln in purpose_lines:
        out.append(_txt(rx, ty, ln, SERIF, 17, SOFT))
        ty += 23
    ty += 18
    for lines in items:
        out.append('<circle cx="%s" cy="%s" r="11" fill="%s"/>'
                   % (rx + 11, ty - 5, GREEN))
        out.append('<path d="M%s %s l3.4 3.6 l6.2 -7" fill="none" '
                   'stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round" '
                   'stroke-linejoin="round"/>' % (rx + 6, ty - 5))
        for j, ln in enumerate(lines):
            out.append(_txt(rx + 32, ty + j * 21, ln, SERIF, 17.5, INK))
        ty += 21 * len(lines) + 16
    if more:
        out.append(_txt(rx + 32, ty, "+ %d more on this page" % more, SANS,
                        13, SOFT))

    # ---- footer: session and trigger ---------------------------------
    fy = H - pad - 46
    out.append('<rect x="%s" y="%s" width="%s" height="46" rx="10" fill="%s"/>'
               % (pad, fy, W - pad * 2, DEEP))
    tx = pad + 14
    if session:
        out.append('<rect x="%s" y="%s" width="104" height="22" rx="11" '
                   'fill="%s"/>' % (tx, fy + 12, TERRA))
        out.append(_txt(tx + 52, fy + 27, session, SANS, 11.5, "#FFFFFF",
                        "700", anchor="middle", track="0.04em"))
        tx += 124
    if trigger:
        out.append(_txt(tx, fy + 28, wrap("Reset trigger: " + trigger, 92)[0],
                        SANS, 13.5, "#EDE4D2"))

    t_id, d_id = "zmt" + uid, "zmd" + uid
    title = "%s in the %s" % (name, room)
    desc = ("A diagram of the %s, one of the %d micro zones in the %s. It "
            "shows where the zone sits among them and the %d things that are "
            "true when it is finished." % (name, len(siblings), room,
                                           len(done_items)))
    return ('<svg class="zone-map" viewBox="0 0 %s %s" role="img" '
            'aria-labelledby="%s %s" xmlns="http://www.w3.org/2000/svg">'
            '<title id="%s">%s</title><desc id="%s">%s</desc>%s</svg>'
            % (W, H, t_id, d_id, t_id, esc(title), d_id, esc(desc),
               "".join(out)))


def room_map_svg(room, zones, uid="", cols=None, cw=330, chh=84):
    """Every micro zone in one room, numbered, with the time each takes.

    cols, cw and chh are parameters because one map serves two shapes.
    On a room page it sits in a wide column, where two or three narrow
    columns read best. On a printed sheet it owns a portrait page, and
    the two-column version left the bottom third of the paper empty,
    which reads as something that failed to print. The printable pack
    passes one wide column with taller chips instead. Measured by
    printing the pack, not by eye.
    """
    n = len(zones)
    if cols is None:
        cols = 2 if n <= 8 else 3
    rowcount = (n + cols - 1) // cols
    gap, pad = 14, 34
    W = pad * 2 + cols * cw + (cols - 1) * gap
    H = pad * 2 + 104 + rowcount * (chh + gap)

    out = ['<rect x="0" y="0" width="%s" height="%s" rx="18" fill="%s" '
           'stroke="%s" stroke-width="2"/>' % (W, H, PAPER, LINE),
           _ribbon(pad, W, pad - 14)]
    out.append(_txt(pad, pad + 30, "THE MICRO ZONES OF THIS ROOM", SANS, 11.5,
                    TERRA, "700", track="0.2em"))
    out.append(_txt(pad, pad + 66, room, DISPLAY, 30, INK, "600"))
    out.append(_txt(pad, pad + 90, "%d zones. Finish one before you start the "
                    "next." % n, SANS, 12.5, SOFT))

    top = pad + 110
    for i, z in enumerate(zones):
        cx = pad + (i % cols) * (cw + gap)
        cy = top + (i // cols) * (chh + gap)
        out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="11" '
                   'fill="#FFFFFF" stroke="%s" stroke-width="1.5"/>'
                   % (cx, cy, cw, chh, LINE))
        out.append('<circle cx="%s" cy="%s" r="15" fill="%s"/>'
                   % (cx + 26, cy + 28, S_COLOURS[i % 6]))
        out.append(_txt(cx + 26, cy + 33, i + 1, SANS, 13, "#FFFFFF", "700",
                        anchor="middle"))
        for j, ln in enumerate(wrap(z.get("zone", ""), 26)[:2]):
            out.append(_txt(cx + 52, cy + 27 + j * 17, ln, DISPLAY, 16, INK,
                            "600"))
        if z.get("session"):
            out.append(_txt(cx + 52, cy + chh - 16, z["session"], SANS, 11.5,
                            SOFT, "600", track="0.04em"))

    t_id, d_id = "rmt" + uid, "rmd" + uid
    desc = ("A map of the %d micro zones in the %s, numbered in the order to "
            "work them, each with the time one session takes." % (n, room))
    return ('<svg class="room-map" viewBox="0 0 %s %s" role="img" '
            'aria-labelledby="%s %s" xmlns="http://www.w3.org/2000/svg">'
            '<title id="%s">The micro zones of the %s</title>'
            '<desc id="%s">%s</desc>%s</svg>'
            % (W, H, t_id, d_id, t_id, esc(room), d_id, esc(desc),
               "".join(out)))


def main():
    import video_zone as V
    zones = V.zones()
    rooms = {}
    for room, z in zones:
        rooms.setdefault(room, []).append(z)
    out_dir = os.path.join(ROOT, "build", "graphics")
    os.makedirs(out_dir, exist_ok=True)
    pick = [(r, z) for r, z in zones if z["zone"] == "Primary Prep Counter"][0]
    room, z = pick
    sibs = [x["zone"] for x in rooms[room]]
    pairs = (("zone-diagram-demo.svg",
              zone_diagram_svg(room, z, sibs, V.done_items(z))),
             ("room-map-demo.svg", room_map_svg(room, rooms[room])))
    for name, svg in pairs:
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("  wrote build/graphics/%s  %d bytes" % (name, len(svg)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
