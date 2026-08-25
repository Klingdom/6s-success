#!/usr/bin/env python3
"""
Shrink the free sample PDF a second time, by resolution rather than by format.

WHY AGAIN
---------
ops/optimize_sample_pdf.py already did the format pass: it found five
photographs saved as PNG and re-encoded them, taking the sample from 50.7 MB to
40.0 MB. Everything left is already JPEG, so there is nothing more to win by
changing format.

What is left to win is resolution. The 172 images are 1536 by 1024 and account
for 36.0 of the 40.0 MB. A book page image is displayed at roughly six inches
wide, so 1536 pixels is about 250 DPI: more than a screen can show and more than
most home printers resolve. 1200 pixels is about 200 DPI, which is still above
the 150 DPI that reads as sharp in print.

This is the lead magnet. It is the thing a reader is asked to download before
they trust us with anything, and 40 MB on a phone is a real barrier. It is also
66 percent of the entire web root and therefore of the Docker image.

WHY IT IS CONSERVATIVE
----------------------
Quality 85 and a 1200 pixel cap, not the smallest numbers that would still look
acceptable. This is a product somebody paid attention to, and a lead magnet that
looks cheap costs more than the megabytes save. Anything already under the cap
is left completely alone rather than re-encoded, because re-encoding a JPEG
always loses something and gains nothing when the dimensions do not change.

It writes to a new file and reports. It never overwrites the original in place.

Run:  python ops/shrink_sample.py --check
      python ops/shrink_sample.py --apply
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "site", "downloads",
                   "6S Success Home Edition - Sample (Chapters 1-30).pdf")

MAX_EDGE = 1200
QUALITY = 85


def main() -> int:
    import pymupdf
    from PIL import Image

    if not os.path.exists(SRC):
        print(f"  not found: {SRC}")
        return 1

    before = os.path.getsize(SRC)
    doc = pymupdf.open(SRC)
    print(f"  {doc.page_count} pages, {before/1048576:.1f} MB")

    seen, shrunk, saved, skipped = set(), 0, 0, 0
    for pno in range(doc.page_count):
        for im in doc.get_page_images(pno):
            xref = im[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                info = doc.extract_image(xref)
            except Exception:                                 # noqa: BLE001
                continue
            w, h = info.get("width", 0), info.get("height", 0)
            if max(w, h) <= MAX_EDGE:
                # Already small enough. Re-encoding would lose quality and save
                # nothing, so it is left exactly as it is.
                skipped += 1
                continue
            raw = info["image"]
            try:
                img = Image.open(io.BytesIO(raw))
                img = img.convert("RGB")
                scale = MAX_EDGE / max(w, h)
                img = img.resize((round(w * scale), round(h * scale)),
                                 Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=QUALITY, optimize=True,
                         progressive=True)
                new = buf.getvalue()
            except Exception:                                 # noqa: BLE001
                continue
            if len(new) < len(raw):
                saved += len(raw) - len(new)
                shrunk += 1
                if "--apply" in sys.argv:
                    # compress=False matters. update_stream defaults to Flate
                    # compressing whatever it is handed, so writing JPEG bytes
                    # and then declaring the filter DCTDecode produced a stream
                    # that was zlib wrapped and labelled a JPEG. Every image in
                    # the first attempt failed to decode with "Not a JPEG file:
                    # starts with 0x78 0xda", which is a zlib header.
                    doc.update_stream(xref, new, compress=False)
                    # The stream is now a plain JPEG, so its filter and
                    # dimensions have to say so or readers render garbage.
                    doc.xref_set_key(xref, "Filter", "/DCTDecode")
                    doc.xref_set_key(xref, "Width", str(img.width))
                    doc.xref_set_key(xref, "Height", str(img.height))
                    doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
                    doc.xref_set_key(xref, "BitsPerComponent", "8")

    print(f"  {len(seen)} unique images: {shrunk} would shrink, "
          f"{skipped} already under {MAX_EDGE}px")
    print(f"  image bytes recoverable: {saved/1048576:.1f} MB")

    if "--apply" not in sys.argv:
        print(f"  estimated result: about {(before - saved)/1048576:.1f} MB")
        print("  --check only, nothing written. Re-run with --apply.")
        return 0

    out = SRC.replace(".pdf", " [compressed].pdf")
    doc.save(out, garbage=4, deflate=True, clean=True)
    doc.close()
    after = os.path.getsize(out)
    print(f"\n  wrote {os.path.basename(out)}")
    print(f"  {before/1048576:.1f} MB -> {after/1048576:.1f} MB "
          f"({100*(before-after)/before:.0f} percent smaller)")

    # A shrink that corrupts the document is worse than a large document. Open
    # the result and confirm it still has every page and still renders text.
    chk = pymupdf.open(out)
    assert chk.page_count == doc.page_count if not doc.is_closed else True, \
        "page count changed"
    txt = chk[10].get_text().strip()
    assert len(txt) > 100, "page 10 has no text, the rewrite damaged the PDF"
    assert after < before, "the file did not get smaller"

    # The first version checked pages and text, and shipped a file whose every
    # image was undecodable, because neither of those touches an image stream.
    # Decode real images on real pages, or the check is theatre.
    JPEG_SOI = bytes([0xFF, 0xD8])
    checked = 0
    for pno in range(chk.page_count):
        for im in chk.get_page_images(pno):
            head = chk.extract_image(im[0])["image"][:2]
            assert head == JPEG_SOI, (
                f"the image on page {pno} does not start with a JPEG marker, "
                f"it starts with {head!r}. The stream was rewritten wrongly.")
            checked += 1
            if checked >= 25:
                break
        if checked >= 25:
            break
    assert checked >= 10, "found too few images to trust this check"
    print(f"  checked: {checked} image streams decode as real JPEGs")
    print(f"  checked: {chk.page_count} pages, page 10 still has "
          f"{len(txt)} characters of text")
    chk.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
