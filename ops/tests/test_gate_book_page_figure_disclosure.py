#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_book_page_figure_disclosure() catches a
missing or stale figure-format disclosure on site/book.html.

Found 2026-09-07 (REVIEW-QA-2026-09-07.md, "CONFIRMED, P2: the free HTML
book has none of the book's pictures"): book.html offered "Read chapters 1
to 30 free" (HTML) beside "Download... (PDF, 31 MB)" with nothing telling a
reader they differ. ops/build_sample_html.py degrades every figure whose
source image is not in this repository to a text description; 172 of 231
figures degrade this way in the live sample, while the PDF carries all 172
as embedded image objects. Fixed 2026-09-17 with a one-sentence disclosure
in book.html's hero, and this gate, which re-derives both counts from the
real shipped files rather than trusting the sentence to stay true.

Uses small synthetic fixtures, not the real 1 MB HTML / 32 MB PDF, so this
runs fast and does not depend on either binary being present.

Run:  python ops/tests/test_gate_book_page_figure_disclosure.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

PASS = FAIL = 0


def check(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok    {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}")


def sample_html(n_figure, n_described):
    parts = ["<html><body>"]
    for i in range(n_described):
        parts.append("<figure>Figure description ...</figure>")
    for i in range(n_figure - n_described):
        parts.append("<figure><svg></svg></figure>")
    parts.append("</body></html>")
    return "".join(parts)


def sample_pdf_bytes(n_images):
    return b"\n".join([b"/Subtype /Image"] * n_images)


def book_html_with(described, total):
    return (
        '<p class="fulfil-note">The two formats are not identical. The '
        f"online HTML edition shows {described} of its {total} figures as "
        "a text description instead of the picture; the PDF carries every "
        "one. Read online for speed, download the PDF to see the "
        "pictures.</p>"
    )


def main():
    fn = preflight.check_book_page_figure_disclosure

    # 1. No disclosure at all on book.html.
    problem = fn("<p>no disclosure here</p>", sample_html(231, 172),
                 sample_pdf_bytes(172))
    check("missing disclosure fails", problem is not None)
    check("missing disclosure names the review",
          problem is not None and "REVIEW-QA-2026-09-07.md" in problem)

    # 2. Disclosure present, but its numbers no longer match the real
    #    sample HTML (e.g. more chapters/images added upstream).
    stale = book_html_with(172, 231)
    problem = fn(stale, sample_html(240, 180), sample_pdf_bytes(180))
    check("stale counts fail", problem is not None)

    # 3. Disclosure claims the PDF is complete, but the live PDF actually
    #    has fewer embedded images than the HTML degrades.
    current = book_html_with(172, 231)
    problem = fn(current, sample_html(231, 172), sample_pdf_bytes(100))
    check("pdf regression fails", problem is not None)

    # 4. The real, current, correct state: numbers match on both sides.
    problem = fn(current, sample_html(231, 172), sample_pdf_bytes(172))
    check("accurate disclosure passes", problem is None)

    # 5. The real committed files, if present in this checkout.
    book_path = os.path.join(preflight.SITE, "book.html")
    html_path = os.path.join(ROOT, preflight.SAMPLE_HTML_REL)
    pdf_path = os.path.join(ROOT, preflight.SAMPLE_PDF_REL)
    if os.path.exists(book_path) and os.path.exists(html_path) \
            and os.path.exists(pdf_path):
        import io
        import re
        book_text = io.open(book_path, encoding="utf-8", errors="replace").read()
        html_text = io.open(html_path, encoding="utf-8", errors="replace").read()
        pdf_bytes = open(pdf_path, "rb").read()
        problem = fn(book_text, html_text, pdf_bytes)
        check("real committed files clean", problem is None)
    else:
        print("  skip  real committed files not present in this checkout")

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
