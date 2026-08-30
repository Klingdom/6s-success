#!/usr/bin/env python3
"""
Web sized variants for the 41 room photographs.

WHAT WAS WRONG
--------------
The 20 room pages are the heaviest real content on the site and the only page
type that never went through the image pipeline the 110 zone pages already
use. All 41 photographs were served as a bare <img>: no srcset, no webp, no
width or height. They are 1402x1122 and 1536x1024, averaging 260 KB, so a
phone at 390 CSS pixels downloads roughly three and a half times the pixels it
can show, and every one of them shifts the layout as it arrives because the
browser has no dimensions to reserve space with.

10.4 MB across twenty pages, most of it thrown away on the device that matters
most.

WHAT THIS DOES
--------------
Makes webp and jpg at three widths, and records each image's intrinsic size so
the generator can write real width and height attributes. It touches nothing
else: the originals stay exactly where they are, and a page that has not been
regenerated still works.

Idempotent, and it skips an image whose variants are already newer than the
source, so re-running it costs nothing.

Run:  python ops/room_image_variants.py
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "site", "assets", "img", "rooms")
OUT = os.path.join(ROOT, "site", "assets", "img", "rooms", "w")
INDEX = os.path.join(ROOT, "ops", "room-image-sizes.json")

# 420 covers a phone at 2x, 840 a phone at 3x or a tablet, 1280 a desktop
# column. Above that the source itself is barely larger, so a fourth size
# would cost storage and save nobody anything.
WIDTHS = (420, 840, 1280)


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print("  PIL is not installed")
        return 1

    os.makedirs(OUT, exist_ok=True)
    sources = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
    if not sources:
        print("  no room images found")
        return 0

    sizes, made, skipped = {}, 0, 0
    for f in sources:
        stem = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f)
        sizes[os.path.basename(f)] = list(im.size)

        for w in WIDTHS:
            if w > im.width:
                continue
            h = round(im.height * w / im.width)
            for ext, kw in (("webp", dict(quality=80, method=6)),
                            ("jpg", dict(quality=80, optimize=True,
                                         progressive=True))):
                p = os.path.join(OUT, f"{stem}-{w}.{ext}")
                if (os.path.exists(p)
                        and os.path.getmtime(p) >= os.path.getmtime(f)):
                    skipped += 1
                    continue
                im.convert("RGB").resize((w, h), Image.LANCZOS).save(p, **kw)
                made += 1

    json.dump(sizes, io.open(INDEX, "w", encoding="utf-8", newline=""),
              indent=1, sort_keys=True)

    src_bytes = sum(os.path.getsize(f) for f in sources)
    # What a phone actually fetches now: the smallest webp per image.
    small = sum(os.path.getsize(p) for p in
                glob.glob(os.path.join(OUT, f"*-{WIDTHS[0]}.webp")))
    print(f"  {len(sources)} source images, {src_bytes/1024/1024:.1f} MB")
    print(f"  wrote {made} variant(s), skipped {skipped} already current")
    print(f"  a phone now fetches {small/1024/1024:.1f} MB across all 20 room "
          f"pages instead of {src_bytes/1024/1024:.1f} MB, "
          f"{100 - round(small / src_bytes * 100)}% less")
    print(f"  intrinsic sizes recorded for {len(sizes)} image(s) in "
          f"{os.path.relpath(INDEX, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
