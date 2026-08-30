#!/usr/bin/env python3
"""
Put each zone's hero photograph onto its zone page, web sized.

WHY THIS MATTERS MORE THAN IT SOUNDS
------------------------------------
The site audit's largest single content finding was that all 114 zone pages
are thorough and contain no image at all. Each is 1,200 to 1,600 words of
genuinely useful instruction with nothing to look at, which is why the action
and the offer arrive after a long read.

An image at the top answers "what am I aiming for" before the reader commits
to the text, and it is the same answer the page's own words give, because the
picture was generated from that zone's done_looks_like sentence.

WHAT IT DOES NOT DO
-------------------
It does not claim the picture is a photograph of a real home. Every image
carries a caption saying it shows the finished state, and the alt text
describes what is in it rather than asserting provenance. A generated image
presented as documentary evidence would be the same class of error as a
fabricated testimonial.

GENERATOR OWNERSHIP
-------------------
ops/build_zone_pages.py rewrites all 114 pages from scratch, so a hand added
image would be destroyed on the next build. This is chained into that
generator the same way the chapter figures are, and running it twice changes
nothing.

Run:  python ops/wire_zone_heroes.py --check
      python ops/wire_zone_heroes.py --apply
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
HEROES = os.path.join(ROOT, "build", "heroes", "zones")
WEB = os.path.join(SITE, "assets", "zones")

SIZES = {"lg": 1024, "md": 640, "sm": 320}


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pairs() -> list:
    """(hero png, meta, target page). Only where both actually exist."""
    out = []
    for png in sorted(glob.glob(os.path.join(HEROES, "*.png"))):
        mj = png.replace(".png", ".json")
        if not os.path.exists(mj):
            continue
        meta = json.load(io.open(mj, encoding="utf-8"))
        room, zone = meta.get("room"), meta.get("zone")
        if not room or not zone:
            continue
        # The page naming convention, taken from the files on disk rather
        # than reconstructed, because the zone display name and the file name
        # differ for several zones.
        cands = glob.glob(os.path.join(SITE, "zones", f"{slug(room)}-*.html"))
        want = slug(zone)
        hit = None
        for c in cands:
            base = os.path.basename(c)[:-5]
            tail = base[len(slug(room)) + 1:]
            if tail in (want, "the-" + want) or want in tail:
                hit = c
                break
        if hit:
            out.append((png, meta, hit))
    return out


def derivatives(png: str, stem: str) -> dict:
    from PIL import Image
    os.makedirs(WEB, exist_ok=True)
    im = Image.open(png).convert("RGB")
    made = {}
    for tag, w in SIZES.items():
        h = round(im.height * w / im.width)
        small = im.resize((w, h), Image.LANCZOS)
        for ext, kw in (("webp", dict(quality=80, method=6)),
                        ("jpg", dict(quality=80, optimize=True,
                                     progressive=True))):
            p = os.path.join(WEB, f"{stem}-{tag}.{ext}")
            small.save(p, **kw)
            made[f"{tag}.{ext}"] = p
    return made


def figure(stem: str, meta: dict, prefix: str = "../") -> str:
    zone = meta.get("zone", "")
    room = meta.get("room", "")
    subject = meta.get("subject", "")
    # The alt text describes the picture. It does not claim it is a real room.
    alt = (f"An illustration of {zone.lower()} in {room.lower()} in its "
           f"finished state: {subject.split(':', 1)[-1].strip()}")
    b = f"{prefix}assets/zones/{stem}"
    return (
        f'\n<figure class="zone-hero" id="zone-hero">\n'
        f'  <picture>\n'
        f'    <source type="image/webp" srcset="{b}-md.webp 640w, '
        f'{b}-lg.webp 1024w" sizes="(max-width:720px) 92vw, 680px">\n'
        f'    <img src="{b}-md.jpg" alt="{alt}" width="640" height="480" '
        f'loading="eager" fetchpriority="high" decoding="async">\n'
        f'  </picture>\n'
        f'  <figcaption>What done looks like in this zone. An illustration '
        f'of the finished state, not a photograph of a real home.</figcaption>\n'
        f'</figure>\n')


def main(apply_it: bool) -> int:
    ps = pairs()
    have = len(glob.glob(os.path.join(HEROES, "*.png")))
    print(f"  heroes generated  {have}")
    print(f"  matched to a page {len(ps)}")
    if have and not ps:
        print("  no hero matched a page, so the naming assumption is wrong")
        return 1
    if not apply_it:
        for _p, m, page in ps[:5]:
            print(f"    {m['zone'][:30]:32} -> {os.path.basename(page)}")
        print("\n  --check only, nothing written")
        return 0

    wired, skipped = 0, 0
    for png, meta, page in ps:
        stem = os.path.splitext(os.path.basename(png))[0]
        derivatives(png, stem)
        s = io.open(page, encoding="utf-8").read()
        if 'id="zone-hero"' in s:
            skipped += 1
            continue
        # Directly after the intro, before the long instruction, because the
        # point is to answer "what am I aiming for" before the reading starts.
        m = re.search(r"(</p>)(\s*<(?:section|h2|div class=\"card))", s, re.S)
        if not m:
            skipped += 1
            continue
        s = s[:m.end(1)] + figure(stem, meta) + s[m.end(1):]
        io.open(page, "w", encoding="utf-8", newline="").write(s)
        wired += 1

    print(f"  wired {wired}, already present {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
