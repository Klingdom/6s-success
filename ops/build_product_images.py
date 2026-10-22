#!/usr/bin/env python3
"""
One picture per hand-written shop product, made from the product itself.

WHAT WAS WRONG
--------------
Nine products at the top of the shop (the book, the Manual, the bundle, both
print packs, the Home Quest and the three consulting offers) shared seven
book figures. Each carried a "Figure 15-01" tab and a headline of its own
baked into the pixels, and none showed what was being sold: the eBook and the
Virtual Home Consult both read "Good Homes. No Shared Picture.", the In-Home
Reset Day read "The Power of the Timer", and Corporate Lean 6S showed a home
pantry (PLAN-VISUAL-STRATEGY.md 6.4).

WHAT THIS MAKES
---------------
site/assets/img/product-<name>.jpg at 1280x960 (the tile is 4:3), plus the
420 and 840 jpg and webp variants site.js's pictureSources() expects. Run
ops/build_avif.py --encode afterwards for the avif siblings.

The digital products are shown as their own pages, printed by a real browser
from the same files a buyer receives or downloads, then laid on paper:

* eBook: Chapter One's opening spread, from the free sample PDF.
* Micro Zone Manual: a real zone page over its list of the twenty rooms.
* Whole House Print Pack: three real cards from its first sheet.
* Standards Pack: two real room sheets.
* Bundle: the three products above, together.
* Home Quest: the app's own first screen, in a plain phone outline.

The consulting offers have no artefact to show, so they get a crop of an
existing illustration with no words in it (Virtual: a phone filming an
entryway; In-Home: a household resetting its entryway together), and Corporate
gets the site's real zone scoring and audit sheet. Nothing here is a
photograph of a real home or a real client, and nothing claims to be.

The old seven files are NOT overwritten: they are still used as og:image and
on other pages.

Run:  python ops/build_product_images.py          # make what is missing
      python ops/build_product_images.py --force  # remake all nine
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
import browser                                                 # noqa: E402
from build_pack_images import write, W, H                      # noqa: E402

SITE = os.path.join(ROOT, "site")
IMG = os.path.join(SITE, "assets", "img")
BUILD = os.path.join(ROOT, "build")
SAMPLE_PDF = os.path.join(SITE, "downloads",
                          "6S Success Home Edition - Sample (Chapters 1-30).pdf")
MANUAL = os.path.join(ROOT, "content", "manual",
                      "micro-zone-manual-publishable.html")
PRINTPACK = os.path.join(BUILD, "6S-Whole-House-Print-Pack.html")
STANDARDS = os.path.join(BUILD, "6S-Standards-Pack.html")
AUDIT = os.path.join(SITE, "downloads", "6S-Zone-Scoring-and-Audit-Template.html")
BG = (239, 231, 214)          # FLOOR, the same neutral the room plans use
INK = (43, 38, 34)

# sku -> output file. data.js points each row at its file.
PRODUCTS = {
    "BK-EB": "product-ebook.jpg",
    "MZ-MANUAL": "product-manual.jpg",
    "PACK-HOUSE": "product-print-pack.jpg",
    "PACK-STANDARDS": "product-standards.jpg",
    "BK-BUNDLE": "product-bundle.jpg",
    "APP-FREE": "product-home-quest.jpg",
    "CN-VIRTUAL": "product-consult-virtual.jpg",
    "CN-INHOME": "product-consult-in-home.jpg",
    "CN-CORP": "product-corporate.jpg",
}


def run_browser(args, exe, extra):
    subprocess.run([exe, "--headless=new", "--disable-gpu",
                    "--hide-scrollbars"] + list(extra) + args,
                   capture_output=True, timeout=240)


def print_pdf(html, exe, extra, tmp):
    """Print a document to PDF in a real browser, the way a buyer would."""
    out = os.path.join(tmp, os.path.basename(html) + ".pdf")
    run_browser(["--no-pdf-header-footer", "--virtual-time-budget=8000",
                 "--print-to-pdf=" + out,
                 "file:///" + html.replace("\\", "/")], exe, extra)
    if not os.path.exists(out):
        raise RuntimeError("browser printed no PDF for %s" % html)
    return out


def page(pdf, n, dpi=150, clip=None):
    """One PDF page (or a clip of it, in points) as a PIL image."""
    import pymupdf
    doc = pymupdf.open(pdf)
    if n >= len(doc):
        raise RuntimeError("%s has %d pages, wanted page %d"
                           % (os.path.basename(pdf), len(doc), n + 1))
    kw = {"dpi": dpi}
    if clip:
        kw["clip"] = pymupdf.Rect(*clip)
    pix = doc[n].get_pixmap(**kw)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def find_page(pdf, needle):
    """Index of the first page of pdf whose text contains needle.

    A browser prints a flowing HTML document to PDF with whatever page
    breaks its own text reflow lands on, which is not portable: the exact
    byte of text that falls on page N depends on font metrics, and two
    renders of the same source HTML on two machines (or even two runs on
    this one, with different fonts installed) can paginate differently.
    Reproduced directly: a hardcoded page 22 here once held the start of
    the "Lower Cabinet and Cookware" zone on the machine that built the
    shipped product-manual.jpg, and the unrelated tail end of a different
    zone's cleaning table in this sandbox's own render of the identical
    source file. Finding the page by its own heading text is immune to
    that drift; a hardcoded index is not.
    """
    import pymupdf
    doc = pymupdf.open(pdf)
    for i in range(len(doc)):
        if needle in doc[i].get_text():
            return i
    raise RuntimeError("no page in %s contains %r"
                       % (os.path.basename(pdf), needle))


def screenshot(url_path, width, height, exe, extra, tmp):
    shot = os.path.join(tmp, "shot.png")
    run_browser(["--force-device-scale-factor=2",
                 "--window-size=%d,%d" % (width, height),
                 "--virtual-time-budget=6000", "--screenshot=" + shot,
                 "file:///" + url_path.replace("\\", "/")], exe, extra)
    if not os.path.exists(shot):
        raise RuntimeError("browser wrote no screenshot of %s" % url_path)
    im = Image.open(shot).convert("RGB")
    im.load()
    os.remove(shot)
    return im


def fit(im, height=None, width=None):
    k = (height / im.height) if height else (width / im.width)
    return im.resize((round(im.width * k), round(im.height * k)),
                     Image.LANCZOS)


def lay(canvas, im, cx, cy, angle=0.0, border=True):
    """Set a sheet on the table: a hairline edge, a soft shadow, a tilt."""
    im = im.convert("RGBA")
    if border:
        ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1),
                                     outline=(214, 205, 188, 255), width=2)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    pad = 40
    shadow = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad),
                       (0, 0, 0, 0))
    alpha = im.split()[3].point(lambda a: int(a * 0.28))
    shadow.paste((60, 45, 30, 255), (pad, pad), alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    canvas.alpha_composite(shadow, (x - pad + 6, y - pad + 12))
    canvas.alpha_composite(im, (x, y))


def table():
    return Image.new("RGBA", (W, H), BG + (255,))


def done(canvas):
    return canvas.convert("RGB")


def trim(im, margin=24, bg=(255, 255, 255)):
    """Crop a printed page to its printed area, keeping a paper margin."""
    from PIL import ImageChops
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg))
    box = diff.convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box:
        raise RuntimeError("page is blank")
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - margin), max(0, y0 - margin),
                    min(im.width, x1 + margin), min(im.height, y1 + margin)))


# A Print Pack card, in PDF points: nine to a US Letter sheet, measured from
# the printed PDF's own drawing boxes (180 x 244.5 pt from 36.75, 21.75).
CARD_W, CARD_H, CARD_X0, CARD_Y0 = 180.0, 244.5, 36.75, 21.75


def card(pdf, sheet, col, row, dpi=220):
    x = CARD_X0 + col * CARD_W
    y = CARD_Y0 + row * CARD_H
    return page(pdf, sheet, dpi, clip=(x, y, x + CARD_W, y + CARD_H))


def spread(left, right, height=760):
    """Two pages side by side as an open spread, centred on the table."""
    c = table()
    a, b = fit(left, height=height), fit(right, height=height)
    total = a.width + b.width
    if total > W - 80:
        k = (W - 80) / total
        a = fit(a, height=round(a.height * k))
        b = fit(b, height=round(b.height * k))
    x = (W - a.width - b.width) // 2
    lay(c, a, x + a.width / 2, H / 2, angle=0)
    lay(c, b, x + a.width + b.width / 2, H / 2, angle=0)
    # the gutter: a faint fold line where the pages meet
    ImageDraw.Draw(c).line((x + a.width, (H - a.height) // 2,
                            x + a.width, (H + a.height) // 2),
                           fill=(200, 190, 172, 255), width=3)
    return done(c)


def fan(sheets, angles, height, gap):
    c = table()
    sheets = [fit(s, height=height) for s in sheets]
    n = len(sheets)
    span = sum(s.width for s in sheets) - gap * (n - 1)
    x = (W - span) / 2
    for s, a in zip(sheets, angles):
        lay(c, s, x + s.width / 2, H / 2 + 10, angle=a)
        x += s.width - gap
    return done(c)


def phone(screen):
    """A plain phone outline around a real screenshot. No brand, no notch art."""
    s = fit(screen, height=820)
    bez = 22
    body = Image.new("RGBA", (s.width + 2 * bez, s.height + 2 * bez),
                     (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, body.width - 1, body.height - 1), radius=58,
                        fill=INK + (255,))
    mask = Image.new("L", s.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s.width - 1, s.height - 1),
                                           radius=38, fill=255)
    body.paste(s, (bez, bez), mask)
    c = table()
    lay(c, body, W / 2, H / 2 + 6, border=False)
    return done(c)


def cover(im):
    """Centre-crop to 4:3, the way the tile itself would, then size it.

    Lives here, not in build_pack_images.py: that file's copy was removed as
    dead code on 2026-10-22 because nothing there called it any more."""
    target = W / H
    if im.width / im.height > target:
        nw = round(im.height * target)
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:
        nh = round(im.width / target)
        y = (im.height - nh) // 2
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((W, H), Image.LANCZOS)


def crop_frac(path, box):
    """A crop of an existing illustration, as fractions of its size."""
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = (round(v * d) for v, d in
                      zip(box, (im.width, im.height) * 2))
    return cover(im.crop((x0, y0, x1, y1)))


def build_all(exe, extra, tmp):
    """sku -> a zero-argument maker. Each is lazy, so one failure is local."""
    pdfs = {}

    def pdf(key):
        if key not in pdfs:
            src = {"pack": PRINTPACK, "std": STANDARDS, "man": MANUAL,
                   "audit": AUDIT}[key]
            pdfs[key] = print_pdf(src, exe, extra, tmp)
        return pdfs[key]

    def book_spread():
        # Sample pages 5 and 6: Chapter One's opener and its first page.
        return spread(page(SAMPLE_PDF, 4), page(SAMPLE_PDF, 5))

    def manual_spread():
        # A real zone page (Lower Cabinet and Cookware), its top two thirds
        # large enough that the zone name and the six passes read on a phone,
        # over the page that lists the twenty rooms. Both found by their own
        # text, not a hardcoded page number: see find_page()'s own docstring
        # for why a fixed index silently drifts onto the wrong zone.
        m = pdf("man")
        c = table()
        under = fit(page(m, find_page(m, "Twenty rooms")), width=760)
        lay(c, under, W / 2 - 170, H / 2 + 40, angle=4)
        zone = find_page(m, "Lower Cabinet and Cookware Zone")
        top = fit(page(m, zone, dpi=220, clip=(0, 0, 504, 470)), width=980)
        lay(c, top, W / 2 + 60, H / 2 + 20, angle=-1.5)
        return done(c)

    def cards():
        p = pdf("pack")
        return fan([card(p, 0, 0, 0), card(p, 0, 1, 0), card(p, 0, 2, 0)],
                   [4, 0, -4], height=640, gap=80)

    def standards():
        p = pdf("std")
        return fan([trim(page(p, 0)), trim(page(p, 1))], [3, -2],
                   height=700, gap=560)

    def bundle():
        p = pdf("pack")
        return fan([page(SAMPLE_PDF, 4), page(pdf("man"), 5),
                    card(p, 0, 0, 0)], [4, -1, -5], height=600, gap=90)

    def quest():
        return phone(screenshot(os.path.join(SITE, "quest.html"), 500, 1000,
                                exe, extra, tmp))

    def corporate():
        return fan([trim(page(pdf("audit"), 0))], [0], height=860, gap=0)

    return {
        "BK-EB": book_spread,
        "MZ-MANUAL": manual_spread,
        "PACK-HOUSE": cards,
        "PACK-STANDARDS": standards,
        "BK-BUNDLE": bundle,
        "APP-FREE": quest,
        # hero-entry.jpg: the phone filming an entryway, right of the type.
        "CN-VIRTUAL": lambda: crop_frac(os.path.join(IMG, "hero-entry.jpg"),
                                        (0.31, 0.12, 1.0, 0.89)),
        # renewed.jpg: the "Renewed" half, below its headline.
        "CN-INHOME": lambda: crop_frac(os.path.join(IMG, "renewed.jpg"),
                                       (0.5, 0.27, 0.997, 0.826)),
        "CN-CORP": corporate,
    }


def main(argv):
    force = "--force" in argv
    only = [a for a in argv if not a.startswith("--")]
    found = browser.find_browser()
    if not found:
        print("  no browser found: cannot print the product pages")
        return 1
    if not os.path.exists(PRINTPACK):
        subprocess.run([sys.executable, os.path.join(ROOT, "ops",
                        "build_printpack.py")], check=True,
                       capture_output=True)
    if not os.path.exists(STANDARDS):
        subprocess.run([sys.executable, os.path.join(ROOT, "ops",
                        "build_standards.py")], check=True,
                       capture_output=True)
    tmp = tempfile.mkdtemp(prefix="_product_images_")
    made, kept, failed = [], [], []
    try:
        makers = build_all(*found, tmp)
        for sku, name in PRODUCTS.items():
            if only and sku not in only:
                continue
            if os.path.exists(os.path.join(IMG, name)) and not force:
                kept.append(sku)
                continue
            try:
                im = makers[sku]()
                if im.size != (W, H):
                    raise RuntimeError("made %dx%d, not %dx%d"
                                       % (im.width, im.height, W, H))
                write(im, name)
                made.append(sku)
            except Exception as exc:      # reported, never silently skipped
                failed.append((sku, str(exc)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  made %d, already present %d, failed %d"
          % (len(made), len(kept), len(failed)))
    for sku, why in failed:
        print("  FAILED %s: %s" % (sku, why))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
