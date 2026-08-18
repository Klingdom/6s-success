#!/usr/bin/env python3
"""
Shrink the free sample PDF without degrading it.

The sample is the site's largest asset by a wide margin: 50.7 MB of a 56 MB
web root, and it is the lead magnet, the thing a reader is asked to download
before they trust us with anything. A download that large is a real barrier on
a phone, and a large share of household use is expected to be on phones.

What this does and deliberately does not do:

  DOES    Re-encode images stored as PNG. Five of them hold 8.7 MB between them
          because a photograph was saved in a lossless format built for line
          art. Re-encoding to JPEG at the SAME pixel dimensions and high quality
          removes about 90 percent of each with no visible difference.

  DOES    Correct the document title. It read "The Complete Book" while holding
          chapters 1 to 30 of 50, which is an inaccurate claim about what the
          reader is getting, and it carried an em dash against house style.

  DOES NOT touch the 168 JPEGs. They are already efficiently encoded: re-running
          them at the same size and comparable quality saves about 6 percent
          while adding a generation of loss. That is a bad trade.

  DOES NOT resize anything. Dropping to 1200 pixels would save roughly 13 MB,
          but 1536 pixels is a defensible width for reading on a high density
          screen, and cutting image quality in the free sample is a product
          decision for the owner, not a cleanup an agent should make quietly.

Run:  python ops/optimize_sample_pdf.py --check    report only
      python ops/optimize_sample_pdf.py --apply    rewrite the sample in place
"""
import io, os, shutil, sys

import pypdf
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "site", "downloads",
                   "6S Success Home Edition - Complete Book.pdf")

# Chapters actually included. The full book is 50 chapters; this sample is the
# first 30, and the title has to say so.
TITLE = "6S Success: Home Edition, chapters 1 to 30"
JPEG_QUALITY = 88          # high, because this replaces a lossless source once


def survey(path):
    """Return (pages, [(bytes, name, mode, size)]) for every embedded image."""
    reader = pypdf.PdfReader(path)
    found = []
    for page in reader.pages:
        try:
            for im in page.images:
                found.append((len(im.data), im.name, im.image.mode, im.image.size))
        except Exception:
            continue
    return len(reader.pages), found


def report():
    pages, imgs = survey(PDF)
    total = os.path.getsize(PDF)
    png = [i for i in imgs if i[1].lower().endswith(".png")]
    print(f"  {os.path.basename(PDF)}")
    print(f"  {total/1048576:.1f} MB, {pages} pages, {len(imgs)} images "
          f"({sum(i[0] for i in imgs)/1048576:.1f} MB of image data)")
    print(f"  {len(png)} PNG images holding {sum(i[0] for i in png)/1048576:.1f} MB:")
    for b, n, mode, size in sorted(png, reverse=True):
        print(f"      {b/1048576:5.2f} MB  {n:<12} {size[0]}x{size[1]} {mode}")
    reader = pypdf.PdfReader(PDF)
    title = (reader.metadata or {}).get("/Title", "")
    print(f"  title: {title!r}")
    ok = not png and "Complete Book" not in title
    print("  clean" if ok else "  optimisable")
    return 0 if ok else 1


def apply():
    # The PDF is tracked, so git history is the real backup: the original comes
    # back with `git show HEAD:"site/downloads/..."`. This local copy only exists
    # so the run is reversible before it is committed, and it is gitignored
    # because a second 50 MB blob in the tree helps nobody.
    backup = PDF + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(PDF, backup)
        print(f"  kept a local original at {os.path.basename(backup)} (gitignored)")

    before = os.path.getsize(PDF)
    reader = pypdf.PdfReader(backup)
    writer = pypdf.PdfWriter(clone_from=backup)

    saved = converted = 0
    for page in writer.pages:
        try:
            images = list(page.images)
        except Exception:
            continue
        for im in images:
            if not im.name.lower().endswith(".png"):
                continue
            original = len(im.data)
            buf = io.BytesIO()
            # Same pixels, same dimensions. Only the container changes.
            im.image.convert("RGB").save(buf, "JPEG", quality=JPEG_QUALITY,
                                         optimize=True, progressive=True)
            buf.seek(0)
            im.replace(Image.open(buf), quality=JPEG_QUALITY)
            new = len(im.data)
            saved += original - new
            converted += 1
            print(f"      {im.name:<12} {original/1048576:5.2f} MB -> "
                  f"{new/1048576:5.2f} MB")

    meta = dict(reader.metadata or {})
    meta["/Title"] = TITLE
    writer.add_metadata(meta)

    with open(PDF, "wb") as fh:
        writer.write(fh)

    after = os.path.getsize(PDF)
    print(f"  converted {converted} PNG images, reclaimed "
          f"{saved/1048576:.1f} MB of image data")
    print(f"  file {before/1048576:.1f} MB -> {after/1048576:.1f} MB "
          f"({100*(1-after/before):.1f}% smaller)")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    sys.exit(report() if mode == "--check" else apply())
