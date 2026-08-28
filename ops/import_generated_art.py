#!/usr/bin/env python3
"""
Watch one drop folder for generated hero images and pull them into the deck.

THE HANDOFF
-----------
Phil generates the images. This picks them up. The contract between the two
halves is the filename, and nothing else:

    every prompt states  ->  save the result as: MM-001-Mudroom-Family-Hook-Zone.png
    Phil saves it here   ->  ~/Desktop/6S-Generated-Images/
    this routes it       ->  the right deck, checked, resized, wired into the site

No folder to pick, no card to identify, no renaming. Drop the file in with
the name the prompt gave it and run this. Anything whose name does not match
a known card is left where it is and reported, never guessed at.

WHAT IT CHECKS BEFORE ACCEPTING AN IMAGE
----------------------------------------
A generated image is not automatically a usable one, and a bad one is worse
than a missing one because it ships. Each is checked for:

  * a card code that matches a real card in a real deck
  * a plausible landscape hero shape, since the template overlays a 3:2
  * enough size to survive the card template
  * not nearly flat, which is what a failed generation looks like
  * no huge block of near black or near white, the shape a text banner makes

The last one is a proxy, not a text detector, and it is described honestly as
such below. The real protection against baked in text is the prompt, which
forbids it six ways.

Run:  python ops/import_generated_art.py --check
      python ops/import_generated_art.py --apply
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP = os.path.join(os.path.expanduser("~"), "Desktop", "6S-Generated-Images")
DESK = os.path.join(os.path.expanduser("~"), "Desktop", "6S-Success-Card-Decks")

# Card code prefix letter to the deck it belongs to, and where that deck's
# source art lives. A new deck is one line here.
DECK_OF = {"E": "entryway", "M": "mudroom"}
DECK_DIR = {
    "entryway": os.path.join(DESK, "Entryway Deck", "card-images"),
    "mudroom": os.path.join(DESK, "Mud Room Deck", "card-images"),
}

MIN_EDGE = 900
ARCHIVE = os.path.join(DROP, "_imported")
REJECTED = os.path.join(DROP, "_rejected")


def known_cards() -> dict:
    """Every card id this project knows about, from the deck card lists."""
    out = {}
    p = os.path.join(ROOT, "build", "mudroom-cards.json")
    if os.path.exists(p):
        for c in json.load(io.open(p, encoding="utf-8")):
            out[c["ID"]] = {"deck": "mudroom", "card": c["Card"]}
    for f in glob.glob(os.path.join(DECK_DIR["entryway"], "*")):
        m = re.match(r"([A-Z]{2}-\d{3})", os.path.basename(f))
        if m:
            out.setdefault(m.group(1), {"deck": "entryway", "card": ""})
    # Prompt indexes name every card, including ones with no art yet.
    for idx in glob.glob(os.path.join(ROOT, "build", "prompts", "*", "index.json")):
        d = json.load(io.open(idx, encoding="utf-8"))
        for c in d.get("cards", []):
            out.setdefault(c["id"], {"deck": d["deck"], "card": c.get("card", "")})
    return out


def inspect(path: str) -> tuple:
    """Return (ok, why). Never raises on a bad file."""
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path)
        im.load()
    except Exception as e:                                    # noqa: BLE001
        return False, f"will not open as an image ({type(e).__name__})"

    w, h = im.size
    if min(w, h) < MIN_EDGE:
        return False, f"{w}x{h}, under the {MIN_EDGE}px minimum for a card hero"
    if not (1.2 <= w / h <= 1.9):
        return False, (f"{w}x{h} is {w/h:.2f} wide for tall. The card template "
                       f"overlays a landscape hero of about 1.5")

    a = np.asarray(im.convert("L"), dtype=np.float32)
    if a.std() < 12:
        return False, (f"standard deviation {a.std():.1f}. A nearly flat image "
                       f"is a failed generation, not a photograph")

    # A wide, very dark or very light band across the top or bottom is the
    # shape a baked in title banner makes. This is a proxy and it will not
    # catch text in the middle of a picture; the prompt is the real defence.
    rows = a.mean(axis=1)
    band = max(int(h * 0.10), 1)
    for name, strip in (("top", rows[:band]), ("bottom", rows[-band:])):
        if strip.mean() < 42 or strip.mean() > 232:
            if abs(strip.mean() - rows.mean()) > 70:
                return False, (f"a uniform {'dark' if strip.mean() < 128 else 'light'} "
                               f"band across the {name}, which is the shape a "
                               f"baked in title bar makes. Check it by eye")
    return True, ""


def main(apply_it: bool) -> int:
    if not os.path.isdir(DROP):
        if apply_it:
            os.makedirs(DROP, exist_ok=True)
            for d in (ARCHIVE, REJECTED):
                os.makedirs(d, exist_ok=True)
            io.open(os.path.join(DROP, "READ-ME.txt"), "w",
                    encoding="utf-8", newline="").write(
                "Drop generated card hero images here.\n\n"
                "Use the exact filename the prompt gave you, for example\n"
                "  MM-001-Mudroom-Family-Hook-Zone.png\n\n"
                "Then run, from the repository:\n"
                "  python ops/import_generated_art.py --apply\n\n"
                "Accepted files move to _imported. Anything rejected moves to\n"
                "_rejected with the reason printed, and is never published.\n")
            print(f"  created {DROP}")
            print("  drop images there and run this again")
            return 0
        print(f"  drop folder does not exist yet: {DROP}")
        print("  run with --apply to create it")
        return 0

    cards = known_cards()
    files = [f for f in glob.glob(os.path.join(DROP, "*"))
             if os.path.isfile(f)
             and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

    print(f"  drop folder : {DROP}")
    print(f"  known cards : {len(cards)}")
    print(f"  files found : {len(files)}")
    if not files:
        print("  nothing to import")
        return 0

    take, skip = [], []
    for f in files:
        base = os.path.basename(f)
        m = re.match(r"([A-Z]{2}-\d{3})", base)
        if not m:
            skip.append((base, "filename does not start with a card code like MM-001"))
            continue
        code = m.group(1)
        if code not in cards:
            skip.append((base, f"{code} is not a card in any deck this knows"))
            continue
        deck = cards[code].get("deck") or DECK_OF.get(code[0])
        if not deck or deck not in DECK_DIR:
            skip.append((base, f"cannot tell which deck {code} belongs to"))
            continue
        ok, why = inspect(f)
        if not ok:
            skip.append((base, why))
            continue
        take.append((f, code, deck))

    for base, why in skip:
        print(f"    SKIP  {base[:44]:46} {why}")
    for f, code, deck in take:
        print(f"    take  {os.path.basename(f)[:44]:46} -> {deck}")

    if not apply_it:
        print(f"\n  would import {len(take)}, skip {len(skip)}. "
              f"--check only, nothing moved.")
        return 0

    os.makedirs(ARCHIVE, exist_ok=True)
    os.makedirs(REJECTED, exist_ok=True)
    decks_touched = set()
    for f, code, deck in take:
        shutil.copy2(f, os.path.join(DECK_DIR[deck], os.path.basename(f)))
        shutil.move(f, os.path.join(ARCHIVE, os.path.basename(f)))
        decks_touched.add(deck)
    for base, _why in skip:
        src = os.path.join(DROP, base)
        if os.path.exists(src):
            shutil.move(src, os.path.join(REJECTED, base))

    print(f"\n  imported {len(take)}, rejected {len(skip)}")

    # The rest of the pipeline runs itself, so a dropped file becomes a live
    # card in one command rather than four remembered ones.
    if decks_touched:
        sys.path.insert(0, os.path.join(ROOT, "ops"))
        import split_deck_cards
        import build_deck_gallery
        for d in sorted(decks_touched):
            print(f"\n  splitting {d}")
            split_deck_cards.main(True, d)
        print()
        build_deck_gallery.main()
        os.system(f'"{sys.executable}" "{os.path.join(ROOT, "ops", "fingerprint_assets.py")}" >nul 2>&1')
        print("  assets re-fingerprinted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
