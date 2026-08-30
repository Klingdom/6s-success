#!/usr/bin/env python3
"""
The Entryway deck as a print at home PDF.

WHY THIS AND NOT THE PNGs
-------------------------
88 PNG files is not a product. A person who wants this deck wants to press
print once, cut along the lines, and have cards. So this lays them nine to a
sheet at true trading card size on US Letter, with crop marks and a gutter
wide enough to cut through without shaving a card.

WHAT MAKES IT PRINTABLE RATHER THAN JUST A PDF
----------------------------------------------
Each card is placed at exactly 2.5 by 3.5 inches, which is the size a standard
card sleeve expects. The renderer produces 750x1050 px, so the images are
placed at 300 dpi with no resampling and no scaling error that would leave the
deck a millimetre out and unsleeveable.

Crop marks sit outside the card, in the gutter, so no mark is printed on a
card face. A half millimetre of slack between neighbours means a slightly
crooked cut takes the gutter rather than the artwork.

WHAT IT REFUSES TO DO
---------------------
Include a card whose hero was never reviewed. It builds from the same rendered
files the review gate governs, so a card that is not in build/cards-rendered
is not in the PDF, and it says how many that is rather than quietly printing
a shorter deck.

Run:  python ops/build_deck_pdf.py
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS = os.path.join(ROOT, "build", "cards-rendered")
CORPUS = os.path.join(ROOT, "build", "entryway-cardtext.json")
OUT = os.path.join(ROOT, "build", "6S-Entryway-Deck-PrintAndPlay.pdf")

PT = 72.0
CARD_W, CARD_H = 2.5 * PT, 3.5 * PT
PAGE_W, PAGE_H = 8.5 * PT, 11.0 * PT
COLS, ROWS = 3, 3
GUTTER = 0.06 * PT           # a hair of slack so a crooked cut takes the gap
MARK = 0.16 * PT             # crop mark length, drawn outside the card


def place(i: int, face: str) -> tuple:
    """Grid cell for card i on a front or back sheet.

    Backs mirror the columns. Paper flipped on its long edge reverses left and
    right, so a back printed in the same column as its front lands on a
    different card, and every card in the deck then lies about itself. It is
    not visible until somebody prints and cuts one, which is why this is a
    function with a test rather than two lines inside a loop.
    """
    col, row = i % COLS, i // COLS
    return (COLS - 1 - col if face == "back" else col), row


def jpeg(path: str, quality: int = 82):
    """The card as a print quality JPEG, in memory.

    Embedding the PNGs losslessly produced a 76 MB file, which is not a
    download anybody wants for a free print at home deck. These are
    photographs and flat type at 300 dpi; JPEG at 82 is indistinguishable on
    paper and roughly a fifth the size. The pixels are untouched otherwise: no
    resampling, so the card still lands at exactly 2.5 by 3.5 inches.
    """
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    buf = io.BytesIO()
    Image.open(path).convert("RGB").save(buf, "JPEG", quality=quality,
                                         optimize=True, subsampling=0)
    buf.seek(0)
    return ImageReader(buf)


def order() -> list:
    """Deck order from the corpus, so the printed deck is the deck's order."""
    d = json.load(io.open(CORPUS, encoding="utf-8"))
    return [c["id"] for c in d["cards"]]


def main() -> int:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
    except ImportError:
        print("  reportlab is not installed")
        return 1

    want = order()
    have = [c for c in want
            if os.path.exists(os.path.join(CARDS, f"{c}-front.png"))]
    missing = [c for c in want if c not in have]
    if not have:
        print("  no rendered cards. Run ops/render_cards.py first.")
        return 1

    grid_w = COLS * CARD_W + (COLS - 1) * GUTTER
    grid_h = ROWS * CARD_H + (ROWS - 1) * GUTTER
    x0 = (PAGE_W - grid_w) / 2
    y0 = (PAGE_H - grid_h) / 2

    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("6S Success: The Entryway Deck, print and play")
    c.setAuthor("Nova Consulting")

    per = COLS * ROWS
    sheets = 0
    for start in range(0, len(have), per):
        chunk = have[start:start + per]

        # Fronts, then the matching backs on the next sheet with the columns
        # mirrored. This is the whole correctness of a duplex print: paper
        # flipped on its long edge reverses left and right, so a back placed
        # in the same column as its front lands on a different card. Getting
        # this wrong produces a deck where every card lies about itself, and
        # it is not visible until somebody prints and cuts one.
        for face in ("front", "back"):
            for i, code in enumerate(chunk):
                col, row = place(i, face)
                png = os.path.join(CARDS, f"{code}-{face}.png")
                if not os.path.exists(png):
                    continue
                x = x0 + col * (CARD_W + GUTTER)
                y = y0 + (ROWS - 1 - row) * (CARD_H + GUTTER)
                c.drawImage(jpeg(png), x, y, width=CARD_W, height=CARD_H)
                c.setLineWidth(0.3)
                c.setStrokeColorRGB(0.6, 0.6, 0.6)
                for cx, cy in ((x, y), (x + CARD_W, y),
                               (x, y + CARD_H), (x + CARD_W, y + CARD_H)):
                    sx = -MARK if cx == x else MARK
                    sy = -MARK if cy == y else MARK
                    c.line(cx + sx, cy, cx + sx * 0.15, cy)
                    c.line(cx, cy + sy, cx, cy + sy * 0.15)
            sheets += 1
            c.setFont("Helvetica", 7)
            c.setFillColorRGB(0.55, 0.53, 0.5)
            c.drawString(x0, y0 - 14,
                         f"6S Success, the Entryway deck. "
                         f"{'Fronts' if face == 'front' else 'Backs'}, "
                         f"cards {start + 1} to {start + len(chunk)}. "
                         f"Print at 100 percent with no scaling, double sided, "
                         f"flipping on the long edge, then cut on the marks.")
            c.showPage()
    c.save()

    size = os.path.getsize(OUT) / 1024 / 1024
    print(f"  wrote {os.path.relpath(OUT, ROOT)}  {size:.1f} MB")
    backs = len([x for x in have
                 if os.path.exists(os.path.join(CARDS, f"{x}-back.png"))])
    print(f"  {len(have)} cards over {sheets} sheets, nine to a sheet at "
          f"2.5 by 3.5 inches, fronts and backs for duplex printing")
    print(f"  {backs} of {len(have)} cards have a back face")
    if missing:
        print(f"  {len(missing)} card(s) not rendered and therefore not in the "
              f"deck: {missing[:4]}")
    else:
        print(f"  every card in the corpus is in the deck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
