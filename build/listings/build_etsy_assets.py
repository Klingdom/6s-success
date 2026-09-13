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
import tempfile
import time

import pymupdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "build", "listings")
OUT = os.path.join(HERE, "etsy")
TMP = os.path.join(OUT, "_tmp")

CARD_MARK = re.compile(r"\b\d+ / \d+\b")


def find_browser() -> str | None:
    """Locate a Chromium-family headless browser on whatever machine this
    runs on.

    Phil runs this on Windows, where Edge is Chromium underneath and takes
    the same --print-to-pdf flags. An operator sandbox has no Edge but often
    has a real Chromium (Playwright's own download, or a system package), and
    the render/audit logic here does not care which binary drew the PDF, so
    checking a short list beats hardcoding one path and leaving this whole
    file unrunnable anywhere but Phil's laptop. $ETSY_BROWSER overrides both.
    """
    override = os.environ.get("ETSY_BROWSER")
    if override and os.path.exists(override):
        return override
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/opt/pw-browsers/chromium",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ("chromium", "chromium-browser", "google-chrome",
                 "google-chrome-stable"):
        found = shutil.which(name)
        if found:
            return found
    return None


# listing slug, source html, delivered file name
#
# L3-entryway (build/products/RP-ENTRYWAY.html -> 6S-Entryway-Pack.pdf) was
# withdrawn 2026-09-09: that SKU is the exact one ops/generated_products.py
# already excludes from the site's own paid catalogue because the free
# Entryway deck covers it. Selling it on Etsy is the same defect on a
# different channel. See MARKETPLACE-LISTINGS.md section 3.1 and
# build/listings/check_etsy.py's free_duplicate_skus(), which now fails any
# listing that repeats this shape.
LISTINGS = [
    ("L1-whole-house", "build/6S-Whole-House-Print-Pack.html",
     "6S-Whole-House-Print-Pack.pdf"),
    ("L1-whole-house", "build/6S-Standards-Pack.html",
     "6S-Standards-Pack.pdf"),
    ("L2-kitchen", "build/products/RP-KITCHEN.html",
     "6S-Kitchen-Pack.pdf"),
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


def render(browser, src_rel, dest, apply_fix=True):
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
    # Every other headless-Chrome caller in this repository (render_cards.py,
    # prerender_shop.py, video_zone.py, build_thumbnails.py, build_social_
    # pins.py, product_links.py) passes its own --user-data-dir; this one
    # did not, until 2026-09-13. That was a real bug (a shared profile lock
    # between rapid successive launches) but not the one actually failing
    # CI, which kept failing after that fix landed.
    #
    # The real cause, found the same day after two diagnostic-only commits:
    # this used to add --no-sandbox only when `os.geteuid() == 0`, on the
    # theory that root (this operator's own sandbox, a container) was the
    # only place needing it. GitHub's own ubuntu-24.04 runner executes as
    # the unprivileged `runner` user, so that condition was always false
    # there and --no-sandbox was never added on the one machine that
    # actually needed it. Reproduced directly: running the real Chromium
    # binary as root with --no-sandbox omitted refuses outright ("Running as
    # root without --no-sandbox is not supported") and writes no PDF, the
    # exact "no PDF produced" shape CI reported; passing the flag fixes it.
    # This script only ever renders its own local file:// HTML, never
    # remote or user-supplied content, so the isolation --no-sandbox gives
    # up buys nothing here. Added unconditionally on non-Windows instead of
    # re-deriving who needs it from who is running it.
    #
    # A separate, real shape also showed up across CI's diagnostic pushes:
    # the third or fourth headless-Chrome invocation in one busy CI job
    # occasionally produced no PDF with a clean exit and no stderr, while
    # the first two invocations in the same job and every single real
    # single-render production run never failed. That is a transient
    # resource limit on a shared runner, not a wrong flag, and the
    # --no-sandbox fix above does not by itself rule it out recurring on a
    # busier runner. Kept the retry rather than assuming one fix explains
    # both symptoms.
    for attempt in range(3):
        with tempfile.TemporaryDirectory() as profile:
            # Found 2026-09-13, watching this gate hang past its own CI job's
            # 20-minute timeout on GitHub's runner while a local run of the
            # same script finished in 11 seconds flat. This was the one
            # headless-Chrome caller in the whole repository still on old
            # "--headless" with capture_output=True; every sibling
            # (ops/render_cards.py, ops/prerender_shop.py, and
            # ops/build_manual_print.py's own --print-to-pdf measure(),
            # doing the exact same operation this function does) already
            # uses "--headless=new" and DEVNULL streams. Old headless mode
            # is documented to sometimes leave a renderer/zygote child
            # holding the stdout/stderr pipe open after the parent exits,
            # which hangs subprocess.run() on the read even though the PDF
            # itself was already written; capture_output=True is also just
            # dead weight here, since neither stream was ever read. Matched
            # the already-proven convention rather than inventing a new one.
            flags = [browser, "--headless=new", "--disable-gpu",
                     "--no-pdf-header-footer", f"--user-data-dir={profile}",
                     "--print-to-pdf=" + dest, url]
            if os.name != "nt":
                flags.insert(1, "--no-sandbox")
            subprocess.run(flags, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=600)
        # Found 2026-09-13, the very next CI run after adding the retry
        # above: a plain os.path.exists(dest) check accepted a killed or
        # still-writing Chrome's own empty/partial file as success, so a
        # genuinely stale-content run got reported as current instead of
        # retried. Chrome opens the destination before it has anything to
        # write, so existence alone proves nothing; a real render is never
        # a handful of bytes.
        if os.path.exists(dest) and os.path.getsize(dest) > 1024:
            return
        time.sleep(1)


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
    browser = find_browser()
    if not browser:
        print("FAIL: no headless Chromium-family browser found (checked Edge "
              "on Windows, Playwright's Chromium, and PATH). Set $ETSY_BROWSER "
              "to a binary that supports --headless --print-to-pdf.")
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
        render(browser, src, dest)
        if not os.path.exists(dest) or os.path.getsize(dest) <= 1024:
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
        render(browser, INSTRUCTIONS[0], dest, apply_fix=False)
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
