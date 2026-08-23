#!/usr/bin/env python3
"""
Draw the app icons from the brand mark.

WHY THIS EXISTS
---------------
The site had no icon of any kind: no favicon, no apple-touch-icon, nothing a
phone could put on a home screen. That is fine for a page you read once and
fatal for a thing you want somebody to install, and installing is the whole
point of the work this supports.

WHY DRAWN RATHER THAN EXPORTED
------------------------------
The mark is the friction gauge, and it exists only as inline SVG inside the site
header. Exporting it by hand would create a second copy that drifts the first
time the palette changes. This redraws it from the same six numbers the rest of
the system uses, so the icon and the header cannot disagree.

THE MASKABLE VARIANT MATTERS
----------------------------
Android crops icons to whatever shape the launcher uses, circle on some phones,
squircle on others. An icon drawn to the edges loses its edges. The maskable
version draws the same mark inside the 80 percent safe zone the spec defines, so
it survives any crop.

Run:  python ops/build_icons.py
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "assets", "img")

DEEP = (34, 50, 60)        # #22323C, the site's deep ground
CREAM = (237, 228, 210)    # #EDE4D2, the needle
# The gauge sweep, left to right: friction through to calm. Same six colours the
# method uses everywhere else, collapsed to four segments because below 192px
# six bands stop being distinguishable and just read as mud.
SWEEP = [(188, 75, 42), (217, 138, 43), (221, 166, 58), (110, 139, 91)]

SIZES = [
    ("icon-192.png", 192, False),
    ("icon-512.png", 512, False),
    ("icon-maskable-512.png", 512, True),
    ("apple-touch-icon.png", 180, False),
]


def draw(size: int, maskable: bool) -> Image.Image:
    # Supersample and downscale: Pillow's arc has no antialiasing, and at icon
    # sizes the stair-stepping on a 22px stroke is the first thing you see.
    S = 4
    n = size * S
    img = Image.new("RGBA", (n, n), DEEP + (255,))
    d = ImageDraw.Draw(img)

    # Maskable icons must survive a circular crop, so the art lives inside the
    # middle 80 percent. A plain icon can use the full square.
    inset = 0.20 if maskable else 0.11
    pad = n * inset
    box_w = n - 2 * pad

    # The gauge sits slightly low in the square: a semicircle's visual centre is
    # below its geometric one, and centring the bounding box makes it look like
    # it is falling out of the top.
    r = box_w / 2
    cx = n / 2
    cy = n / 2 + r * 0.34
    stroke = max(2, int(r * 0.30))

    bb = [cx - r, cy - r, cx + r, cy + r]
    seg = 180 / len(SWEEP)
    for i, col in enumerate(SWEEP):
        start = 180 + i * seg
        # Overlap each segment by a degree so no seam shows through the stroke.
        d.arc(bb, start - (0 if i == 0 else 1), start + seg, fill=col + (255,),
              width=stroke)

    # The needle rests in the calm band, which is the state the method is for.
    import math
    ang = math.radians(180 + 157)
    nr = r * 0.80
    d.line([cx, cy, cx + nr * math.cos(ang), cy + nr * math.sin(ang)],
           fill=CREAM + (255,), width=max(2, int(r * 0.10)))
    hub = r * 0.13
    d.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], fill=CREAM + (255,))

    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    for name, size, maskable in SIZES:
        img = draw(size, maskable)
        img.save(os.path.join(OUT, name), "PNG", optimize=True)
        kb = os.path.getsize(os.path.join(OUT, name)) / 1024
        print(f"  {name:26} {size}x{size}  {kb:5.1f} KB"
              + ("  maskable, art inside the 80% safe zone" if maskable else ""))

    # A favicon a browser will actually use in a tab, at the three sizes it asks
    # for. ICO rather than SVG because the site already ships no icon at all and
    # ICO is the one format every browser and every crawler understands.
    ico = os.path.join(OUT, "favicon.ico")
    draw(64, False).save(ico, "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  {'favicon.ico':26} 16/32/48   {os.path.getsize(ico)/1024:5.1f} KB")

    # The icon must not be a flat square: that is what a failed draw looks like,
    # and it would ship silently.
    px = draw(192, False).convert("RGB")
    colours = {px.getpixel((x, y)) for x in range(0, 192, 7) for y in range(0, 192, 7)}
    assert len(colours) > 12, f"icon has only {len(colours)} colours, the draw failed"
    print(f"  checked: {len(colours)} distinct colours sampled, so the mark drew")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
