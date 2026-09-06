#!/usr/bin/env python3
"""
Prove shrink_sample.verify_shrunk() actually checks the page count, instead
of silently agreeing with whatever it is handed.

Found 2026-09-06: the check read
`chk.page_count == doc.page_count if not doc.is_closed else True`, evaluated
after `doc.close()` had already run a few lines above it. Python ternary
precedence makes that `(chk.page_count == doc.page_count) if not
doc.is_closed else (True)`, and `doc.is_closed` was already True at that
point, so the expression always took the `else True` branch: the page-count
comparison itself never executed, for any input. A shrink that silently
dropped every page past 10 would have passed this assert. Fixed by capturing
`expected_pages = doc.page_count` before `doc.close()` and comparing against
that plain int instead of the closed document (accessing `.page_count` on a
closed pymupdf document raises `ValueError: document closed`, which is
exactly why the original guard existed, just written wrong).

Uses real pymupdf documents throughout, no PIL: verify_shrunk() only decodes,
it never re-encodes, so it needs no image library the sandbox lacks.

Run:  python ops/tests/test_shrink_sample.py
"""
from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import shrink_sample as ss                                    # noqa: E402


def build_fixture(path: str, pages: int, images_per_page: int = 1) -> None:
    """A real, valid PDF: enough pages for the page-10 text check, and at
    least 10 real JPEG image streams for the image-decode check."""
    import pymupdf

    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8))
    pix.set_rect(pix.irect, (255, 0, 0))
    jpeg_bytes = pix.tobytes("jpeg")

    doc = pymupdf.open()
    for i in range(pages):
        page = doc.new_page()
        if i == 10:
            page.insert_text((72, 72), "Sample text. " * 20)
        for _ in range(images_per_page):
            page.insert_image(pymupdf.Rect(0, 0, 50, 50), stream=jpeg_bytes)
    doc.save(path)
    doc.close()


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as tmp:
        good = os.path.join(tmp, "good.pdf")
        build_fixture(good, pages=11, images_per_page=1)

        # Matching page count: verify_shrunk must accept it and run to
        # completion (page-10 text and 10+ real JPEG streams both present).
        try:
            ss.verify_shrunk(good, expected_pages=11)
        except AssertionError as e:
            fails.append(f"verify_shrunk rejected a genuinely intact PDF: {e}")

        # Mismatched page count: this is the exact shape of a shrink that
        # silently dropped pages. Must raise, naming the page count.
        try:
            ss.verify_shrunk(good, expected_pages=30)
        except AssertionError as e:
            if "page count" not in str(e):
                fails.append(f"wrong assertion fired for a page-count "
                             f"mismatch: {e}")
        else:
            fails.append("verify_shrunk accepted a PDF with 11 pages when "
                         "30 were expected: the page-count check is inert, "
                         "the exact regression this test exists to catch")

        # The pre-fix expression, reproduced directly with a real closed
        # pymupdf document, must be shown to be the broken one: this is what
        # made the regression invisible in the first place.
        import pymupdf
        broken = os.path.join(tmp, "broken_check_src.pdf")
        build_fixture(broken, pages=3)
        doc = pymupdf.open(broken)
        doc.close()
        old_expr = (doc.page_count == 999) if not doc.is_closed else True
        if old_expr is not True:
            fails.append("sanity check on the pre-fix expression itself "
                         "did not reproduce as expected")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("shrink_sample.verify_shrunk(): page-count regression covered, "
          "3 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
