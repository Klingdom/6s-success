#!/usr/bin/env python3
"""
Generate the ebook cover.

A typographic cover, not an illustration. There is no image-generation capability
here, and a typographic cover is a legitimate and common choice for practical
nonfiction. It is built from the book's own design system so it belongs to the
same family as the site and the interior.

Output is 1600x2560 (the 1:1.6 ratio retailers ask for, comfortably above the
1000px minimum width).

Run: python ops/build_cover.py
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "cover.png")
W, H = 1600, 2560

# design system tokens, taken from site/assets/css/site.css
PAPER = (247, 242, 233)
INK = (43, 38, 34)
TERRA = (188, 75, 42)
SOFT = (106, 98, 90)
RULE = (226, 216, 196)

# The six S's in canonical order. Safety is the fourth. This ordering is the
# whole point of the book, so the cover states it.
#
# The colours are the site's own per-S ramp, --s1 to --s6, not a hand-picked set.
# An earlier draft of this cover used the general palette (terra, honey, slate,
# green), which put a blue on Safety where every other 6S surface shows amber.
# One book cover disagreeing with every page of the site is exactly the kind of
# drift that makes a brand look assembled rather than designed.
SIX = [("Sort",        (203, 75, 54)),   # --s1
       ("Straighten",  (188, 75, 42)),   # --s2
       ("Shine",       (217, 138, 43)),  # --s3
       ("Safety",      (221, 166, 58)),  # --s4
       ("Standardize", (110, 139, 91)),  # --s5
       ("Sustain",     (78, 122, 87))]   # --s6

WINDOWS_FONTS = r"C:\Windows\Fonts"
_MISSING_FONT = False
def font(names, size):
    """Georgia is the declared fallback for the book's display face, so the cover
    stays in family even without the woff2 files, which PIL cannot read.

    This only ever finds a real face on Windows, where WINDOWS_FONTS actually
    exists; every other machine falls through to PIL's own tiny fixed-size
    bitmap default, which produces a cover with a caption-sized "6S SUCCESS"
    on an otherwise blank sheet, not a smaller version of the real design.
    That is not a degraded cover, it is a broken one, and it looked exactly
    like a successful run (right dimensions, a PNG and JPEG on disk, a
    "wrote..." line) the one time this was tried outside Windows. Tracked
    here rather than silently accepted; see the refusal at the bottom of
    this file's __main__ block.
    """
    global _MISSING_FONT
    for n in names:
        p = os.path.join(WINDOWS_FONTS, n)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    _MISSING_FONT = True
    return ImageFont.load_default()

DISPLAY_B = ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"]
DISPLAY_I = ["georgiai.ttf", "timesi.ttf", "ariali.ttf"]
DISPLAY_R = ["georgia.ttf", "times.ttf", "arial.ttf"]
SANS_B = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"]

def author_name():
    """The author line, read from the front matter rather than typed here.

    Issue #3 closed 2026-08-25: the front matter carries the real answer,
    "Philip Kling", not a bracketed placeholder. A cover must never invent a
    byline, so this still returns None if the field is ever bracketed again
    (a store requires an author on the cover art, so a missing byline should
    block rather than guess), but the normal case now is a real name.
    """
    fm = os.path.join(ROOT, "content", "book", "6S-Success-Front-Matter",
                      "FRONT_MATTER.md")
    try:
        text = open(fm, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"^## Title page\s*$(.*?)^---", text, re.M | re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ">", "*", "-")):
            continue
        if "IMPRINT" in line or "PUBLISHER" in line:
            continue
        if line.startswith("[") and line.endswith("]"):
            return None            # still a placeholder, so no byline
        if "AUTHOR" in line.upper():
            return None
        if "6S SUCCESS" in line.upper() or "·" in line:
            continue
        return line.strip("*_ ")
    return None

AUTHOR = author_name()

# Rendering only happens when this file is run directly. It used to run at
# import time unconditionally, which meant merely importing author_name()
# elsewhere (as ops/preflight.py's staleness check below now does) silently
# regenerated the cover as a side effect, on whatever machine happened to
# import it.
if __name__ == "__main__":
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    def centre(text, f, y, fill):
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        d.text(((W - (r - l)) / 2 - l, y), text, font=f, fill=fill)
        return b - t

    # --- the six-S arc, the brand mark, drawn large and quiet at the top
    cx, cy, rad = W // 2, 820, 330
    seg = 180 / 6
    import math
    for i, (_, col) in enumerate(SIX):
        a0 = 180 + i * seg
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], a0 + 1.5, a0 + seg - 1.5,
              fill=col, width=34)
    # the needle, at the goal, which is where the book ends
    d.line([cx, cy, cx + int(rad * 0.62 * math.cos(math.radians(-58))),
            cy + int(rad * 0.62 * math.sin(math.radians(-58)))], fill=INK, width=13)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=INK)

    # --- title
    y = 1010
    d.line([300, y, W - 300, y], fill=RULE, width=3)
    y += 90
    h = centre("6S SUCCESS", font(DISPLAY_B, 178), y, INK); y += h + 46
    h = centre("Home Edition", font(DISPLAY_I, 116), y, TERRA); y += h + 74
    d.line([300, y, W - 300, y], fill=RULE, width=3); y += 96

    # --- subtitle
    sub = font(DISPLAY_R, 60)
    for line in ["A calm home, built one S at a time.",
                 "Fifty chapters. Twenty rooms.",
                 "One hundred and fourteen micro zones."]:
        h = centre(line, sub, y, SOFT); y += h + 30

    # --- the six S's, named in order, colour-coded, Safety fourth
    y = 1900
    f6 = font(SANS_B, 52)
    widths = [d.textbbox((0, 0), s, font=f6)[2] for s, _ in SIX]
    gap = 46
    total = sum(widths) + gap * (len(SIX) - 1)
    x = (W - total) / 2
    for (s, col), wd in zip(SIX, widths):
        d.text((x, y), s, font=f6, fill=col)
        d.line([x, y + 78, x + wd, y + 78], fill=col, width=7)
        x += wd + gap

    # --- foot
    if AUTHOR:
        centre(AUTHOR.upper(), font(SANS_B, 58), 2110, INK)
    centre("The Lean method that runs factories,", font(DISPLAY_R, 46), 2250, SOFT)
    centre("rebuilt for the room you are standing in.", font(DISPLAY_R, 46), 2316, SOFT)
    centre("6s-success.com", font(SANS_B, 40), 2430, TERRA)

    if _MISSING_FONT:
        # A cover this illegible must never reach build/, let alone a commit
        # or a KDP submission, just because the run technically completed.
        raise SystemExit(
            "refusing to write build/cover.png: none of the named Windows "
            "fonts (Georgia/Times/Arial) were found, so every text element "
            "fell back to PIL's tiny fixed-size default font. Run this on "
            "the machine that has them; do not commit what this run would "
            "have produced.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    jpg = OUT.replace(".png", ".jpg")
    img.convert("RGB").save(jpg, "JPEG", quality=90, optimize=True, progressive=True)
    print(f"wrote {OUT}  {W}x{H}  {os.path.getsize(OUT)//1024} KB")
    print(f"wrote {jpg}  {os.path.getsize(jpg)//1024} KB")
