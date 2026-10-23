#!/usr/bin/env python3
"""
"Where it is": a room's plan with one micro zone filled in, for its zone page.

WHY
---
Each zone page has a "Where it is" panel that lists the room's zones and
marks this one. A list says which zones exist; it cannot say where this one
is. The thirteen rooms with a plan drawn by ops/build_room_maps.py can, so
their zone pages show that plan with this zone filled in.

It carries no words. The panel is about 300 pixels wide on a phone, where
the full labelled plan's type would shrink to nothing, and the numbered list
underneath already names every zone. The picture answers one question only:
where in the room is this.

Drawn from the same layout functions as the room plans, at build time, so a
change to a room's drawing reaches its zone pages on the next build and
cannot drift from it. Nothing here is a photograph of a real home.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_room_maps as B                                    # noqa: E402
from room_map_assemble import PLAN_SCALE, CX, TOP              # noqa: E402
from room_map_draw import PAPER, SLATE, esc                    # noqa: E402

ZONE_RECT = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" '
    r'height="([-\d.]+)" rx="10" fill="#E2D6BF" fill-opacity="0.32" '
    r'stroke="[^"]+" stroke-width="1.6" stroke-dasharray="7 5"/>')
SHAPES = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"')


class _Targets(B.Labels):
    """Labels that draw nothing and remember where each leader points."""

    def __init__(self, names, start):
        super().__init__(names, start)
        self.to = {}

    def add(self, i, x, y, to=None, align="left"):
        if to is not None:
            self.to[i] = to

    def svg(self):
        return ""


def _zone_for(body, point):
    """The smallest dashed zone outline containing a leader's end point."""
    px, py = point
    best = None
    for m in ZONE_RECT.finditer(body):
        x, y, w, h = (float(v) for v in m.groups())
        if x <= px <= x + w and y <= py <= y + h:
            if best is None or w * h < best[1]:
                best = (m, w * h)
    return best[0] if best else None


def locator_svg(room, index, zone_name):
    """The plan of `room` with zone `index` (0-based, page order) filled in.

    Returns None when the room has no plan or the zone cannot be found in
    it, so the caller keeps the list alone rather than show a wrong place.
    """
    spec = B.ROOMS.get(room)
    if not spec:
        return None
    fn, start, noun, names, strap, kind = spec
    if not 0 <= index < len(names):
        return None
    T = _Targets(names, start)
    body, detail, height = fn(T)
    if index not in T.to:
        return None
    hit = _zone_for(body, T.to[index])
    if hit is None:
        return None
    x, y, w, h = (float(v) for v in hit.groups())
    fade = lambda m: m.group(0).replace(
        'fill-opacity="0.32"', 'fill-opacity="0.12" opacity="0.55"')
    # The zone's own outline becomes a solid fill where it already sits in
    # the drawing, so the furniture drawn after it stays on top and legible;
    # a strong outline is drawn last, over everything. Every other zone
    # fades back, so the one that matters is the only strong shape here.
    fill = ('<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="%s" '
            'fill-opacity="0.38"/>' % (hit.group(1), hit.group(2),
                                        hit.group(3), hit.group(4), SLATE))
    ring = ('<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="none" '
            'stroke="%s" stroke-width="6"/>' % (hit.group(1), hit.group(2),
                                                 hit.group(3), hit.group(4),
                                                 SLATE))
    body = (ZONE_RECT.sub(fade, body[:hit.start()]) + fill
            + ZONE_RECT.sub(fade, body[hit.end():]) + ring)
    # The plan's small notes ("into the house") would be about three pixels
    # tall in a phone-width panel; the aria-label carries the meaning.
    body = re.sub(r"<text[^>]*>.*?</text>", "", body, flags=re.S)
    # Crop to the drawing: every rect's extent, padded, in plan coordinates.
    xs, ys = [], []
    for m in SHAPES.finditer(body):
        rx, ry, rw, rh = (float(v) for v in m.groups())
        xs += [rx, rx + rw]
        ys += [ry, ry + rh]
    pad = 26
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    label = ("A plan of the %s with the %s filled in, to show where in the "
             "room it is." % (noun, zone_name))
    return ('<svg class="zd-plan-svg" viewBox="%.0f %.0f %.0f %.0f" '
            'role="img" aria-label="%s">'
            '<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="%s"/>'
            % (x0, y0, x1 - x0, y1 - y0, esc(label),
               x0, y0, x1 - x0, y1 - y0, PAPER)
            + body + "</svg>")
