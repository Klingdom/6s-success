#!/usr/bin/env python3
"""Produce the cover that goes to KDP, which is the site cover minus the URL.

WHY THE URL COMES OFF
---------------------
build/cover.jpg carries "6s-success.com" across the foot. That is right for the
site, where it is a signature, and wrong for a Kindle store listing for three
reasons.

At the size the cover is actually seen, roughly 160 pixels wide in a search
result, a 40 pixel line of small type is a grey smudge. It costs a line of the
cover and returns nothing.

A URL on the cover reads as self-published in a category where the competition
does not do it, and the cover is the only thing a shopper judges before the
title.

And Amazon may simply reject it. Its book description rules explicitly forbid
website addresses, and the cover criteria page fetched on 2026-09-03 does not
say either way about covers. That is an unverified risk, and the cheapest
response to an unverified risk that costs nothing to avoid is to avoid it: a
rejected cover means a book stuck in review, and the URL was buying nothing.

WHAT THIS DOES NOT DO
---------------------
Re-run ops/build_cover.py. That script is owned elsewhere and re-rendering
could change the typography of a cover that is already approved and in use.
This paints the URL band out with the exact background colour sampled from the
image itself, so every other pixel is bit-identical to the cover the site uses.

Run:  python build/listings/build_kdp_cover.py
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "build", "cover.png")
OUT = os.path.join(ROOT, "build", "listings", "kdp", "cover-kdp.jpg")

# The URL sits on one line near the foot. ops/build_cover.py draws it at
# y = 2430 at 40px, so this band clears it with room either side and touches
# nothing above it: the strapline's second line is drawn at y = 2316.
BAND_TOP = 2395
BAND_BOTTOM = 2500


def main() -> int:
    if not os.path.exists(SRC):
        print("FAIL: no source cover at " + SRC)
        return 1
    img = Image.open(SRC).convert("RGB")
    width, height = img.size

    # Sample the background from a corner the design never draws in.
    background = img.getpixel((12, height - 12))

    before = img.crop((0, BAND_TOP, width, BAND_BOTTOM))
    if not ImageChops.difference(before, Image.new("RGB", before.size,
                                                   background)).getbbox():
        print("Nothing to remove: the band at y=%d to %d is already blank. "
              "Either the cover changed or the coordinates are wrong. Check "
              "before trusting this output." % (BAND_TOP, BAND_BOTTOM))
        return 1

    img.paste(Image.new("RGB", (width, BAND_BOTTOM - BAND_TOP), background),
              (0, BAND_TOP))

    # Everything outside the band must be untouched.
    original = Image.open(SRC).convert("RGB")
    top_diff = ImageChops.difference(img.crop((0, 0, width, BAND_TOP)),
                                     original.crop((0, 0, width, BAND_TOP)))
    bottom_diff = ImageChops.difference(
        img.crop((0, BAND_BOTTOM, width, height)),
        original.crop((0, BAND_BOTTOM, width, height)))
    if top_diff.getbbox() or bottom_diff.getbbox():
        print("FAIL: pixels changed outside the band. Not writing anything.")
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "JPEG", quality=92, optimize=True, progressive=True)

    check = Image.open(OUT)
    print("wrote " + OUT)
    print("  %dx%d  %s  height/width %.4f  %d KB"
          % (check.size[0], check.size[1], check.mode,
             check.size[1] / check.size[0], os.path.getsize(OUT) // 1024))
    print("  background sampled from the source: RGB%s" % (background,))
    print("  every pixel outside y=%d to %d is identical to build/cover.png"
          % (BAND_TOP, BAND_BOTTOM))
    return 0


if __name__ == "__main__":
    sys.exit(main())
