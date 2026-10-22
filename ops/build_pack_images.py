#!/usr/bin/env python3
"""
One picture per room pack, of that room, instead of a borrowed book figure.

WHAT WAS WRONG
--------------
The twenty room packs in the shop shared eleven decorative photographs, picked
by a lookup in ops/wire_generated_catalog.py. Opened, most did not show the
room on the label: the Laundry Room Pack showed a hand wiping a dining table,
the Home Office Pack a pantry shelf, the Patio Pack a kitchen timer, and three
of the eleven carried the words "FIGURE 16-04" and the like baked into their
pixels (PLAN-VISUAL-STRATEGY.md 6.4). A pack is "every zone in this room", so
the honest picture of it is the room with its zones marked.

WHAT THIS MAKES
---------------
site/assets/img/pack-<room>.jpg at 1280x960 (the shop tile is 4:3), plus the
420 and 840 wide jpg and webp variants in assets/img/w/ that site.js's
pictureSources() expects. Run ops/build_avif.py --encode afterwards for the
avif siblings, the same as every other webp on the site.

* Rooms with a plan in ops/room-maps.json: that plan, rendered in a real
  browser so its type is the site's own self-hosted fonts, set on paper.
* Entryway, Dining Room and Kids Bedroom: the book's own overhead zone plan
  of the room. Kitchen, Living Room and both bedrooms: the book's before and
  after pair of the whole room. Both are chosen by name in FIGURE below
  rather than by position, because the first figure on a room page is often
  one zone (the Family Room's is its media console) or one technique (the
  Pantry's is "Dry Before Wet"), not the room. Pantry and Family Room have no
  whole-room figure in the book, so they get a plan from ops/room-maps.json
  like the eleven rooms above.
* Book figures carry a "Figure 34-01" tab and a title band in their top
  strip, which is a page reference that means nothing on a shop tile. That
  strip is trimmed and the rest is set on paper, uncropped at the sides, so
  both halves of a before and after pair stay whole.

Nothing here is a photograph of a real home, and nothing claims to be.

Run:  python ops/build_pack_images.py          # make what is missing
      python ops/build_pack_images.py --force  # remake all twenty
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import browser                                                 # noqa: E402

SITE = os.path.join(ROOT, "site")
IMG = os.path.join(SITE, "assets", "img")
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")
MAPS = os.path.join(ROOT, "ops", "room-maps.json")
PHOTOS = os.path.join(ROOT, "ops", "room-images.json")
PAPER = (247, 242, 233)

# The whole-room figure per photographed room, and how much of its top to
# trim (the figure tab and title band), as a fraction of its height. Measured
# by opening each file, not guessed.
FIGURE = {
    # room: (file, top trim, tab patch as x0, y0, x1, y1 fractions or None)
    "Entryway": ("ch31-image02.jpg", 0.0, None),
    "Dining Room": ("ch34-image02.jpg", 0.0, (0.0, 0.0, 0.19, 0.075)),
    "Kids Bedroom": ("ch39-image02.jpg", 0.0, (0.0, 0.0, 0.19, 0.075)),
    # The kitchen tab sits on plain wall above the shelves; trimming it would
    # also clip the BEFORE and AFTER badges level with it.
    "Kitchen": ("ch32-image01.jpg", 0.0, (0.0, 0.0, 0.088, 0.068)),
    "Living Room": ("ch35-image01.jpg", 0.13, None),
    "Primary Bedroom": ("ch37-image01.jpg", 0.055, None),
    "Guest Bedroom": ("ch38-image01.jpg", 0.06, None),
}
W, H = 1280, 960


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def name_for(room):
    return "pack-%s.jpg" % slug(room)


def render_svg(svg, exe, extra):
    """The plan as a PIL image, drawn by a real browser at 2x."""
    m = re.search(r'viewBox="0 0 1000 (\d+)"', svg)
    height = int(m.group(1)) if m else 620
    page = ("<!doctype html><meta charset=utf-8>"
            "<link rel=stylesheet href=\"assets/css/site.css\">"
            "<style>html,body{margin:0;background:#F7F2E9}"
            "svg{display:block;width:1000px;height:auto}</style>" + svg)
    # Inside site/ so the stylesheet and its fonts resolve; removed after.
    fd, probe = tempfile.mkstemp(prefix="_pack_render_", suffix=".html",
                                 dir=SITE)
    os.close(fd)
    shot = probe[:-5] + ".png"
    try:
        io.open(probe, "w", encoding="utf-8").write(page)
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--window-size=1000,%d" % height,
                        "--virtual-time-budget=3000"] + list(extra)
                       + ["--screenshot=" + shot,
                          "file:///" + probe.replace("\\", "/")],
                       capture_output=True, timeout=120)
        if not os.path.exists(shot):
            raise RuntimeError("browser wrote no screenshot")
        im = Image.open(shot).convert("RGB")
        im.load()
        return im
    finally:
        for p in (probe, shot):
            if os.path.exists(p):
                os.remove(p)


def letterbox(im):
    """Fit inside 4:3 on paper, never cropping a drawing."""
    k = min(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    out = Image.new("RGB", (W, H), PAPER)
    out.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return out


def write(im, name):
    stem = name[:-4]
    im.save(os.path.join(IMG, name), "JPEG", quality=86, optimize=True,
            progressive=True)
    os.makedirs(os.path.join(IMG, "w"), exist_ok=True)
    for width in (420, 840):
        v = im.resize((width, round(width * H / W)), Image.LANCZOS)
        base = os.path.join(IMG, "w", "%s-%d" % (stem, width))
        v.save(base + ".jpg", "JPEG", quality=84, optimize=True,
               progressive=True)
        v.save(base + ".webp", "WEBP", quality=82, method=6)
        avif = base + ".avif"
        if os.path.exists(avif):      # stale now; build_avif.py remakes it
            os.remove(avif)


def main(argv):
    force = "--force" in argv
    rooms = [r["room"] for r in
             json.load(io.open(CORPUS, encoding="utf-8"))["rooms"]]
    maps = (json.load(io.open(MAPS, encoding="utf-8"))
            if os.path.exists(MAPS) else {})
    found = browser.find_browser()
    made, kept, failed = [], [], []
    for room in rooms:
        name = name_for(room)
        if os.path.exists(os.path.join(IMG, name)) and not force:
            kept.append(room)
            continue
        try:
            if room in maps:
                if not found:
                    raise RuntimeError("no browser here to draw the plan")
                im = letterbox(render_svg(maps[room]["svg"], *found))
            elif room in FIGURE:
                fname, trim, patch = FIGURE[room]
                src = Image.open(os.path.join(IMG, "rooms", fname))
                src = src.convert("RGB")
                if patch:
                    # The tab sits on plain paper or plain wall in these, so
                    # it is painted out with the colour right beside it.
                    x0, y0, x1, y1 = (round(v * d) for v, d in zip(
                        patch, (src.width, src.height) * 2))
                    fill = src.getpixel((min(x1 + 6, src.width - 1),
                                         max(y0 + 6, 0)))
                    src.paste(fill, (x0, y0, x1, y1))
                src = src.crop((0, round(src.height * trim), src.width,
                                src.height))
                im = letterbox(src)
            else:
                raise RuntimeError("no plan and no book figure")
            write(im, name)
            made.append(room)
        except Exception as exc:          # reported, never silently skipped
            failed.append((room, str(exc)))
    print("  made %d, already present %d, failed %d"
          % (len(made), len(kept), len(failed)))
    for room, why in failed:
        print("  FAIL %s: %s" % (room, why))
    if made:
        print("  now run: python ops/build_avif.py --encode")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
