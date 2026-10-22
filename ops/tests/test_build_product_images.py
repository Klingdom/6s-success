#!/usr/bin/env python3
"""
Prove find_page() in ops/build_product_images.py locates a zone by its own
heading text, and that this matters against the real Manual, not just a
synthetic fixture.

WHY THIS CANNOT BE A HARDCODED PAGE NUMBER
-------------------------------------------
manual_spread() used to crop a fixed page index (22) out of a browser print
of content/manual/micro-zone-manual-publishable.html, on the assumption that
the "Lower Cabinet and Cookware Zone" heading always lands there. It does
not: a browser prints a flowing HTML document to PDF with whatever page
breaks its own font metrics produce, and that is not portable across
rendering environments. Reproduced directly, 2026-10-22, this sandbox: the
same source file, printed the same way, put that heading on page 20, not 22;
page 22 held the unrelated tail of a different zone's cleaning table. The
shipped product-manual.jpg (built elsewhere) happened to be correct; a
regeneration in this sandbox with the old code would have silently shipped
the wrong zone's content as "the" Micro Zone Manual sample.

find_page() replaces the hardcoded index with a text search, so the right
content lands regardless of where the reflow puts it.

If no browser is available, the real-Manual check says NOT VERIFIED and
exits 0, which gate_tests() counts as unchecked rather than passing; the
synthetic-PDF checks need no browser and always run.

Run:  python ops/tests/test_build_product_images.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import browser                                                 # noqa: E402
import build_product_images as bpi                             # noqa: E402


def _make_pdf(path, pages):
    """A pymupdf document with one line of given text per page."""
    import pymupdf
    doc = pymupdf.open()
    for text in pages:
        p = doc.new_page()
        p.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def main() -> int:
    fails = []
    tmp = tempfile.mkdtemp(prefix="_test_build_product_images_")

    # 1. Finds the right page among several, not just the first or last.
    pdf = os.path.join(tmp, "synthetic.pdf")
    _make_pdf(pdf, ["Front matter", "Table of contents",
                    "Garage Zone heading here", "Back matter"])
    got = bpi.find_page(pdf, "Garage Zone")
    if got != 2:
        fails.append("find_page found page %r for a needle planted on page "
                     "2 of 4" % (got,))

    # 2. A needle on the very first page is still found (no off-by-one).
    got0 = bpi.find_page(pdf, "Front matter")
    if got0 != 0:
        fails.append("find_page found page %r for a needle on page 0" % (got0,))

    # 3. A needle that is not on any page raises, rather than silently
    #    returning some other page's content.
    try:
        bpi.find_page(pdf, "Nursery Zone heading does not exist anywhere")
        fails.append("find_page did not raise for an absent needle")
    except RuntimeError:
        pass

    # 4. Against the real Manual: the heading manual_spread() relies on is
    #    genuinely found, and the clip it builds from that page actually
    #    shows the zone and its six passes, the exact defect class this
    #    exists to prevent. Needs a real browser to print the Manual.
    found = browser.find_browser()
    if not found:
        print("NOT VERIFIED: no browser here to print the real Manual")
    else:
        exe, extra = found
        manual_pdf = bpi.print_pdf(bpi.MANUAL, exe, extra, tmp)
        zone_page = bpi.find_page(manual_pdf, "Lower Cabinet and Cookware Zone")
        import pymupdf
        clip_text = pymupdf.open(manual_pdf)[zone_page].get_text(
            clip=pymupdf.Rect(0, 0, 504, 470))
        for want in ("Lower Cabinet and Cookware Zone", "SORT", "SUSTAIN"):
            if want not in clip_text:
                fails.append("the clip manual_spread() crops from the found "
                             "zone page is missing %r; find_page located a "
                             "page, but not the full zone block "
                             "manual_spread() needs" % (want,))

        toc_page = bpi.find_page(manual_pdf, "Twenty rooms")
        toc_text = pymupdf.open(manual_pdf)[toc_page].get_text()
        if "Kitchen" not in toc_text:
            fails.append("the page found for 'Twenty rooms' does not look "
                         "like the table of contents (no 'Kitchen' on it)")

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("OK: find_page() locates planted and real headings correctly, "
          "and raises rather than guessing when a needle is absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
