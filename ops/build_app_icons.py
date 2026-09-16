#!/usr/bin/env python3
"""
Draw the phone app store art from the same brand mark the site uses.

WHY THIS EXISTS
---------------
The app shipped with no image of any kind: no icon, no splash, no store art.
Apple will not accept a submission without a 1024 icon, and Play needs a 512
icon, a feature graphic and screenshots. So the listing was blocked on art as
well as on the two developer accounts, and only one of those is Phil's to fix.

WHY IT IMPORTS THE DRAW RATHER THAN COPYING IT
----------------------------------------------
build_icons.py says plainly that a second hand-made copy of the mark drifts the
first time the palette changes. That applies doubly here, because store art is
the slowest thing in the system to correct: a wrong icon sits in a store listing
until a whole new build is reviewed. So this renders the same function at store
sizes rather than exporting and editing a picture.

WHAT EACH STORE ACTUALLY DEMANDS, AND WHY THE SHAPES DIFFER
-----------------------------------------------------------
Apple: 1024x1024, no alpha channel at all. A transparent pixel is a rejection,
not a warning, so the icon is flattened to RGB on the deep ground.
Play: 512x512 32-bit with alpha, plus a 1024x500 feature graphic.
Android adaptive: the launcher crops to a circle or a squircle and animates the
layers, so the foreground must be transparent outside the art and the art must
sit inside the safe zone. The maskable path already solves that geometry.

Screenshots are deliberately not generated here. Store screenshots must show the
real running app, there is no simulator on this machine, and a web capture
dressed as a phone screenshot would be a false claim to a review team.

Run:  python ops/build_app_icons.py
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

from build_icons import draw, DEEP, CREAM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "mobile", "quest-app", "assets")
LIST = os.path.join(ROOT, "build", "listings", "app")
FONTS = os.path.join(APP, "fonts")


def apple_icon(size: int = 1024) -> Image.Image:
    """Apple rejects any alpha channel, so flatten onto the deep ground."""
    return draw(size, False).convert("RGB")


def play_icon(size: int = 512) -> Image.Image:
    """Play wants 32-bit PNG, so alpha stays."""
    return draw(size, False)


def adaptive_foreground(size: int = 1024) -> Image.Image:
    """Transparent outside the mark, art inside the safe zone.

    The launcher supplies the background colour and animates the layers, so the
    deep ground has to come out. The maskable draw already keeps the art inside
    the 80 percent safe zone, which is tighter than the 66 percent Android
    requires, so the mark survives a circular crop with room to spare.
    """
    img = draw(size, True).convert("RGBA")
    px = img.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = px[x, y]
            # The ground is the only deep-slate area; the sweep and the needle
            # are far away in colour, so an exact-ish match is safe here.
            if abs(r - DEEP[0]) < 10 and abs(g - DEEP[1]) < 10 and abs(b - DEEP[2]) < 10:
                px[x, y] = (r, g, b, 0)
    return img


def splash(size: int = 2048, frac: float = 0.58) -> Image.Image:
    """The mark centred small on the deep ground.

    Expo scales this with resizeMode contain, which fits the whole image on the
    screen. A mark drawn edge to edge would therefore arrive as wide as the
    phone, which looks like a mistake rather than a brand. Drawing it at about a
    third of the canvas was measured and looked like a stamp adrift in a dark
    field, so the mark takes a little over half, which reads as a brand on a
    tall phone without crowding the edges.
    """
    img = Image.new("RGB", (size, size), DEEP)
    mark_px = int(size * frac)
    mark = draw(mark_px, False).convert("RGB")
    img.paste(mark, ((size - mark_px) // 2, (size - mark_px) // 2))
    return img


def _font(name: str, px: int):
    path = os.path.join(FONTS, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, px)
    return ImageFont.load_default()


def feature_graphic(w: int = 1024, h: int = 500) -> Image.Image:
    """The Play banner, set in the app's own faces.

    Play crops this differently across surfaces, so nothing load-bearing goes
    near the edges: the mark sits left, the words sit left of centre, and the
    right third is deliberately empty.
    """
    img = Image.new("RGB", (w, h), DEEP)
    mark_px = int(h * 0.62)
    img.paste(draw(mark_px, False).convert("RGB"), (int(h * 0.20), (h - mark_px) // 2))

    d = ImageDraw.Draw(img)
    x = int(h * 0.20) + mark_px + int(h * 0.16)
    d.text((x, h * 0.30), "6S Success", font=_font("Fraunces-600-normal.ttf", 62),
           fill=CREAM, anchor="ls")
    d.text((x, h * 0.46), "Home Quest", font=_font("Fraunces-600-normal.ttf", 62),
           fill=(221, 166, 58), anchor="ls")
    d.text((x, h * 0.64), "One zone. One job. Put it down.",
           font=_font("Inter-400-normal.ttf", 27), fill=(186, 178, 166), anchor="ls")
    return img


def _colours(img: Image.Image, step: int = 7) -> int:
    rgb = img.convert("RGB")
    w, h = rgb.size
    return len({rgb.getpixel((x, y)) for x in range(0, w, step) for y in range(0, h, step)})


def main() -> int:
    os.makedirs(APP, exist_ok=True)
    os.makedirs(LIST, exist_ok=True)

    icon = apple_icon(1024)
    assert icon.size == (1024, 1024), icon.size
    # An alpha channel here is an App Store rejection, not a warning.
    assert icon.mode == "RGB", "apple icon carries alpha: " + icon.mode
    assert _colours(icon) > 12, "apple icon looks flat, the draw failed"
    icon.save(os.path.join(APP, "icon.png"), "PNG", optimize=True)

    fg = adaptive_foreground(1024)
    assert fg.size == (1024, 1024), fg.size
    corners = [fg.getpixel(p)[3] for p in ((0, 0), (1023, 0), (0, 1023), (1023, 1023))]
    assert max(corners) == 0, "adaptive foreground corners are not transparent: %s" % corners
    # The gauge is an open arc: the middle of the square is hollow and is meant
    # to be transparent. The hub is what must survive, and it sits low, at the
    # same 0.602 of the canvas the draw computes. One lucky pixel is not proof,
    # so the opaque fraction is checked too.
    assert fg.getpixel((512, int(1024 * 0.602)))[3] > 0, "adaptive hub is transparent, art missing"
    step = 9
    pts = range(0, 1024, step)
    opaque = sum(1 for x in pts for y in pts if fg.getpixel((x, y))[3] > 0)
    frac = opaque / (len(pts) ** 2)
    assert 0.02 < frac < 0.60, "adaptive foreground opaque fraction %.3f looks wrong" % frac
    fg.save(os.path.join(APP, "adaptive-icon.png"), "PNG", optimize=True)

    sp = splash(2048)
    assert sp.size == (2048, 2048), sp.size
    assert _colours(sp, 11) > 8, "splash looks flat, the mark did not paste"
    sp.save(os.path.join(APP, "splash.png"), "PNG", optimize=True)

    play = play_icon(512)
    assert play.size == (512, 512), play.size
    play.save(os.path.join(LIST, "play-icon-512.png"), "PNG", optimize=True)

    fgx = feature_graphic()
    assert fgx.size == (1024, 500), fgx.size
    # Cream text pixels prove the fonts loaded and the words drew.
    cream = sum(1 for x in range(0, 1024, 3) for y in range(0, 500, 3)
                if fgx.getpixel((x, y))[0] > 200 and fgx.getpixel((x, y))[2] > 180)
    assert cream > 200, "feature graphic has almost no text pixels (%d), font missing?" % cream
    fgx.save(os.path.join(LIST, "feature-graphic-1024x500.png"), "PNG", optimize=True)

    for path in (os.path.join(APP, "icon.png"), os.path.join(APP, "adaptive-icon.png"),
                 os.path.join(APP, "splash.png"),
                 os.path.join(LIST, "play-icon-512.png"),
                 os.path.join(LIST, "feature-graphic-1024x500.png")):
        im = Image.open(path)
        print("  %-46s %-11s %s %6.1f KB" % (os.path.relpath(path, ROOT).replace(chr(92), "/"),
              "%dx%d" % im.size, im.mode, os.path.getsize(path) / 1024))
    print("  screenshots are NOT generated: they must show the real app on a real phone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
