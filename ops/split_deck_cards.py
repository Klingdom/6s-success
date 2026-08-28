#!/usr/bin/env python3
"""
Split the entryway card artwork into separate front and back faces, web sized.

WHY
---
89 finished card images sit on Phil's Desktop and none of them are on the
site. Each file is a single landscape sheet holding both faces of one card
side by side, under literal "FRONT" and "BACK" guide labels. That shape is
right for reviewing a card and wrong for everything else: a product page
wants one face, a print sheet wants fronts and backs separately, and 1.9 MB
per sheet is unusable on a phone.

An earlier audit looked at five of these and rejected all 89 as "trading card
mockups with game chrome". That was wrong, and worth writing down so it does
not get repeated: the chrome IS the product. These are game cards. The front
carries an annotated illustration with numbered callouts, an objective, a
quick win and the 6S lesson; the back carries symptoms, best practices, a
progress tracker and the card link graph. Hours of design went into them.

WHAT IT DOES
------------
Finds the white gutter between the two faces rather than cutting at 50
percent, because the gutter sits anywhere from 48 to 50 percent depending on
the image. Trims the guide labels and the surrounding page whitespace, then
writes three sizes of each face.

Every split is verified: two panels, each plausibly a portrait trading card,
neither mostly blank. A bad split is skipped and reported rather than shipped,
because a card cut through the middle looks like a broken site.

Run:  python ops/split_deck_cards.py --check
      python ops/split_deck_cards.py --apply
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.expanduser("~"), "Desktop", "6S-Success-Card-Decks",
                   "Entryway Deck", "card-images")
OUT = os.path.join(ROOT, "site", "assets", "cards", "entryway")

# Card faces are 2.5 by 3.5 inches, so 0.714 wide for tall. Anything far from
# that is not a card face and the split went wrong.
TARGET_RATIO = 2.5 / 3.5
RATIO_TOL = 0.16

# Three widths. 900 for a full card view, 420 for a grid tile, 160 for a
# thumbnail in a link path. WebP with a JPEG fallback, because a 1.9 MB PNG on
# a phone is the difference between a page that loads and one that does not.
SIZES = {"lg": 760, "md": 400, "sm": 150}

TYPES = {
    "EM": "Micro Zone", "EP": "Problem", "ET": "Tool", "ES": "Skill",
    "EH": "Habit", "EU": "Upgrade", "EE": "Event", "EW": "Win",
    "ER": "Room", "EX": "Expert",
}


def find_gutter(gray) -> int:
    """The centre of the widest run of near white columns near the middle."""
    import numpy as np
    col = gray.mean(axis=0)
    w = len(col)
    lo, hi = int(w * 0.40), int(w * 0.60)
    white = col > 245

    best, run_start, best_len = None, None, 0
    for x in range(lo, hi):
        if white[x]:
            if run_start is None:
                run_start = x
        else:
            if run_start is not None and x - run_start > best_len:
                best_len, best = x - run_start, (run_start + x) // 2
            run_start = None
    if run_start is not None and hi - run_start > best_len:
        best_len, best = hi - run_start, (run_start + hi) // 2
    return best if best is not None else w // 2


def trim(im):
    """Crop the page whitespace and the FRONT / BACK guide label above it."""
    import numpy as np
    from PIL import Image
    a = np.asarray(im.convert("L"), dtype=np.float32)
    ink = a < 242
    rows = np.where(ink.any(axis=1))[0]
    cols = np.where(ink.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return im
    t, b, l, r = rows[0], rows[-1], cols[0], cols[-1]

    # Drop the FRONT / BACK guide label above the card.
    #
    # Detecting it as "a short ink band followed by a gap" failed: the label
    # sits close enough to the card border that the two often merge into one
    # band, and the label shipped on every card.
    #
    # Width separates them cleanly instead. The label is a centred word
    # spanning maybe a fifth of the sheet; the card's top border spans nearly
    # all of it. So the card starts at the first row whose ink reaches across
    # most of the width.
    span = np.where(ink.any(axis=0))[0]
    full = span[-1] - span[0] + 1
    for y in range(t, min(b, t + int((b - t) * 0.18))):
        xs = np.where(ink[y])[0]
        if len(xs) and (xs[-1] - xs[0] + 1) > full * 0.80:
            t = y
            break

    pad = 2
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad + 1), min(im.height, b + pad + 1)))


def main(apply_it: bool) -> int:
    from PIL import Image
    import numpy as np

    if not os.path.isdir(SRC):
        print(f"  source not found: {SRC}")
        return 1
    files = sorted(glob.glob(os.path.join(SRC, "*.png"))
                   + glob.glob(os.path.join(SRC, "*.jpeg"))
                   + glob.glob(os.path.join(SRC, "*.jpg")))
    print(f"  {len(files)} source sheets in {os.path.basename(SRC)}")

    if apply_it:
        os.makedirs(OUT, exist_ok=True)

    made, skipped, index = 0, [], []
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        code = base.split("-")[0] + "-" + base.split("-")[1]      # EM-003
        im = Image.open(f).convert("RGB")
        g = np.asarray(im.convert("L"), dtype=np.float32)
        gut = find_gutter(g)

        front = trim(im.crop((0, 0, gut, im.height)))
        back = trim(im.crop((gut, 0, im.width, im.height)))

        bad = []
        for name, panel in (("front", front), ("back", back)):
            ratio = panel.width / panel.height
            if abs(ratio - TARGET_RATIO) > RATIO_TOL:
                bad.append(f"{name} ratio {ratio:.2f}, wanted "
                           f"{TARGET_RATIO:.2f}")
            arr = np.asarray(panel.convert("L"), dtype=np.float32)
            if (arr < 242).mean() < 0.04:
                bad.append(f"{name} is {100*(arr<242).mean():.1f}% ink, "
                           f"effectively blank")
        if bad:
            skipped.append((base, "; ".join(bad)))
            continue

        title = " ".join(base.split("-")[3:]) or base
        index.append({
            "code": code, "type": TYPES.get(code[:2], code[:2]),
            "title": title, "slug": base,
        })

        if apply_it:
            for name, panel in (("front", front), ("back", back)):
                for tag, w in SIZES.items():
                    h = round(panel.height * w / panel.width)
                    small = panel.resize((w, h), Image.LANCZOS)
                    stem = os.path.join(OUT, f"{base}-{name}-{tag}")
                    small.save(stem + ".webp", "WEBP", quality=78, method=6)
                    # A JPEG fallback only where one is actually reachable.
                    # WebP is supported by over 97 percent of browsers, and
                    # the full size JPEGs alone were 28 MB of Docker image for
                    # the small fraction that cannot read a webp. Those
                    # browsers get the medium JPEG through the srcset instead,
                    # which is a slightly smaller picture rather than none.
                    if tag != "lg":
                        small.save(stem + ".jpg", "JPEG", quality=78,
                                   optimize=True, progressive=True)
            made += 1

    print(f"  usable: {len(index)}   skipped: {len(skipped)}")
    for b, why in skipped[:6]:
        print(f"    {b[:40]:42} {why}")

    if not apply_it:
        print(f"\n  would write {len(index) * 2 * len(SIZES) * 2} files "
              f"({len(index)} cards x 2 faces x {len(SIZES)} sizes x webp+jpg)")
        print("  --check only, nothing written.")
        return 0

    by = {}
    for c in index:
        by.setdefault(c["type"], []).append(c)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8",
              newline="") as fh:
        json.dump({"deck": "Entryway", "count": len(index), "cards": index},
                  fh, indent=1, ensure_ascii=False)

    total = sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT, "*")))
    src_mb = sum(os.path.getsize(p) for p in files) / 1048576
    # Counted, not computed from the loop bounds. The formula said 1080 files
    # for a while after the large JPEGs were dropped and only 900 were written.
    n_files = len(glob.glob(os.path.join(OUT, "*")))
    print(f"\n  wrote {made} cards as {n_files} files")
    print(f"  {src_mb:.0f} MB of source became {total/1048576:.1f} MB of web assets")
    for t, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f"    {t:12} {len(v)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
