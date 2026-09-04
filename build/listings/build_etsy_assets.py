#!/usr/bin/env python3
"""Turn the finished print packs into the files an Etsy listing actually needs.

WHY THIS EXISTS
---------------
The packs in build/products are HTML with print CSS. That is the right source
format and the wrong delivery format: somebody who pays for a printable expects
a PDF that prints correctly on their own printer, not a web page they have to
open in a browser and hope prints the same way. This renders each chosen pack
through a headless browser, which honours the same print CSS the site uses, and
then measures the result rather than trusting it.

THE DEFECT IT CORRECTS ON THE WAY THROUGH
-----------------------------------------
Nine 3.5in cards is 10.5in of content, and the source sets a 0.4in page margin,
leaving 10.2in of printable height. Every pack therefore overflowed by 0.3in
and Chromium pushed that strip onto a page of its own: every second page of
every rendered pack was a near-empty sheet carrying three orphaned card
footers, and the card above it printed without its footer rule. A 152 page
Whole House PDF is really 76 pages of cards and 76 pages of litter.
print_fix.css corrects the geometry at render time. See that file for why the
fix is what it is, and fix it upstream in ops/build_catalog.py so the site
edition and the marketplace edition stay the same file.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
Invent a mockup. No hands, no wooden table, no printer, no styled desk. Those
photos sell, we do not have them, and faking one is a claim about a physical
object that does not exist. The listing images here are rendered from the
finished PDF, so what the shopper sees is exactly the file they receive.

Run:  python build/listings/build_etsy_assets.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

import pymupdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "build", "listings")
OUT = os.path.join(HERE, "etsy")
TMP = os.path.join(OUT, "_tmp")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CARD_MARK = re.compile(r"\b\d+ / \d+\b")

# listing slug, source html, delivered file name
LISTINGS = [
    ("L1-whole-house", "build/6S-Whole-House-Print-Pack.html",
     "6S-Whole-House-Print-Pack.pdf"),
    ("L1-whole-house", "build/6S-Standards-Pack.html",
     "6S-Standards-Pack.pdf"),
    ("L2-kitchen", "build/products/RP-KITCHEN.html",
     "6S-Kitchen-Pack.pdf"),
    ("L3-entryway", "build/products/RP-ENTRYWAY.html",
     "6S-Entryway-Pack.pdf"),
    ("L4-moving-in", "build/products/KIT-MOVING-IN.html",
     "6S-Moving-In-Kit.pdf"),
    ("L5-holiday-hosting", "build/products/KIT-HOLIDAY-HOST.html",
     "6S-Holiday-Hosting-Kit.pdf"),
]

# Goes into every listing. A printable that arrives without printing
# instructions is where the one star reviews come from: the buyer prints at
# Fit to Page, the cards come out 96% of trading card size, and the sleeves
# they already own no longer fit.
INSTRUCTIONS = ("build/listings/print-instructions.html",
                "How-to-print-these-cards.pdf")


def render(src_rel, dest, apply_fix=True):
    """Render one HTML to PDF, with the card-sheet geometry fix if it is a pack.

    The fix is not applied to the instruction sheet, which is ordinary prose and
    wants ordinary margins."""
    html = open(os.path.join(ROOT, src_rel), encoding="utf-8").read()
    patched = html
    if apply_fix:
        fix = open(os.path.join(HERE, "print_fix.css"), encoding="utf-8").read()
        patched = html.replace("</style>", "</style>\n<style>" + fix + "</style>", 1)
    tmp_html = os.path.join(TMP, os.path.basename(src_rel))
    with open(tmp_html, "w", encoding="utf-8") as fh:
        fh.write(patched)
    url = "file:///" + os.path.abspath(tmp_html).replace(os.sep, "/")
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=" + dest, url],
                   capture_output=True, timeout=600)


def audit(pdf_path):
    """Measure the PDF. Returns pages, page sizes, card count, near-empty pages."""
    doc = pymupdf.open(pdf_path)
    sizes = set()
    cards = 0
    junk = 0
    for page in doc:
        sizes.add((round(page.rect.width / 72, 2), round(page.rect.height / 72, 2)))
        text = page.get_text()
        found = len(CARD_MARK.findall(text))
        cards += found
        if len(text.strip()) < 120 and found == 0:
            junk += 1
    pages = doc.page_count
    doc.close()
    return pages, sizes, cards, junk


def preview(pdf_path, pages, dest, cols, width=2000, height=1500):
    """Lay selected PDF pages on a neutral card, generously margined so that
    whatever aspect ratio the marketplace crops the thumbnail to, the content
    survives the crop."""
    doc = pymupdf.open(pdf_path)
    count = len(pages)
    rows = (count + cols - 1) // cols
    margin = int(width * 0.07)
    gap = int(width * 0.022)
    cell_w = (width - 2 * margin - gap * (cols - 1)) / cols
    cell_h = (height - 2 * margin - gap * (rows - 1)) / rows
    scale = min(cell_w / 8.5, cell_h / 11.0)
    page_w = 8.5 * scale
    page_h = 11.0 * scale

    canvas = pymupdf.open()
    sheet = canvas.new_page(width=width, height=height)
    sheet.draw_rect(pymupdf.Rect(0, 0, width, height), color=None,
                    fill=(0.937, 0.906, 0.839))
    x0 = (width - (cols * page_w + (cols - 1) * gap)) / 2
    y0 = (height - (rows * page_h + (rows - 1) * gap)) / 2
    for i, pno in enumerate(pages):
        row, col = divmod(i, cols)
        x = x0 + col * (page_w + gap)
        y = y0 + row * (page_h + gap)
        rect = pymupdf.Rect(x, y, x + page_w, y + page_h)
        sheet.draw_rect(rect + (4, 4, 4, 4), color=None, fill=(0.78, 0.75, 0.70))
        sheet.show_pdf_page(rect, doc, pno)
    sheet.get_pixmap(dpi=150).save(dest)
    canvas.close()
    doc.close()


def main():
    if not os.path.exists(EDGE):
        print("FAIL: no headless browser at " + EDGE)
        return 1
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP, exist_ok=True)

    rows = []
    for slug, src, pdfname in LISTINGS:
        ddir = os.path.join(OUT, slug, "files")
        idir = os.path.join(OUT, slug, "listing-images")
        os.makedirs(ddir, exist_ok=True)
        os.makedirs(idir, exist_ok=True)
        dest = os.path.join(ddir, pdfname)
        render(src, dest)
        if not os.path.exists(dest):
            print("FAIL: no PDF produced for " + slug + " from " + src)
            return 1
        pages, sizes, cards, junk = audit(dest)
        rows.append((slug, pdfname, pages, cards, junk, sizes,
                     os.path.getsize(dest)))

        stem = os.path.join(idir, os.path.splitext(pdfname)[0])
        preview(dest, [0], stem + "-1-first-page.png", 1)
        if pages >= 4:
            preview(dest, [0, 1, 2, 3], stem + "-2-four-sheets.png", 4)
        preview(dest, [pages - 1], stem + "-3-last-page.png", 1)

    for slug in sorted({s for s, _, _ in LISTINGS}):
        dest = os.path.join(OUT, slug, "files", INSTRUCTIONS[1])
        render(INSTRUCTIONS[0], dest, apply_fix=False)
        pages, sizes, cards, junk = audit(dest)
        rows.append((slug, INSTRUCTIONS[1], pages, cards, junk, sizes,
                     os.path.getsize(dest)))

    shutil.rmtree(TMP, ignore_errors=True)

    header = "listing".ljust(20) + "delivered file".ljust(34)
    header += "pages".rjust(6) + "cards".rjust(7) + "junk".rjust(6) + "  bytes"
    print(header)
    for slug, pdfname, pages, cards, junk, sizes, nbytes in rows:
        print(slug.ljust(20) + pdfname.ljust(34) + str(pages).rjust(6)
              + str(cards).rjust(7) + str(junk).rjust(6)
              + "  " + format(nbytes, ",") + "  " + str(sorted(sizes)))

    problems = []
    for slug, pdfname, pages, cards, junk, sizes, nbytes in rows:
        if sizes != {(8.5, 11.0)}:
            problems.append(slug + "/" + pdfname + ": not US Letter, " + str(sizes))
        if junk:
            problems.append(slug + "/" + pdfname + ": " + str(junk)
                            + " near-empty pages")
        if nbytes > 20 * 1024 * 1024:
            problems.append(slug + "/" + pdfname + ": over 20 MB, check the "
                            "marketplace per-file size cap")
    if problems:
        print("")
        print("FAIL")
        for problem in problems:
            print("   " + problem)
        return 1
    print("")
    print("Every deliverable is US Letter with no near-empty pages. The page "
          "and card counts above are measured from the finished PDF, so the "
          "listing copy can quote them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
