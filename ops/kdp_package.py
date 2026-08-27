#!/usr/bin/env python3
"""
Build and verify the Amazon KDP submission package for the book.

WHY
---
The book has been finished for a long time and sold nowhere a book buyer
looks. The blocker was never the writing; it was that ops/build_epub.py wrote
"[AUTHOR NAME]" into the metadata and Amazon rejects a book with no author.
That is fixed. This assembles everything else a KDP listing needs, verifies
the file against Amazon's actual technical limits, and writes a single sheet
somebody can work straight down.

WHAT IT CANNOT DO, AND WHY
--------------------------
It does not upload. Publishing to KDP requires signing in to an Amazon
account and entering tax and bank details, which is account access and
financial credentials. That stays with Phil. Everything up to the sign in is
done here, so the upload is copy and paste rather than authorship.

THE PRICE, AND THE REASONING
----------------------------
$9.99. Amazon pays a 70 percent royalty between $2.99 and $9.99 and 35
percent outside it, so a cent more than this halves the rate: we would have
to charge about $20 to net the same. Less than this leaves margin on the
table without buying volume, because the constraint on a new title is
visibility rather than price resistance, and a 270,000 word reference priced
at $4.99 reads as thin rather than generous.

The site sells the identical file. It is matched to $9.99 rather than left at
$18, because the same product at two prices is indefensible the moment a
customer notices, and because Amazon's terms expect the list price not to be
undercut elsewhere. The $49 bundle is untouched: it carries the manual and
the print pack too, so it is a genuinely different thing.

Run:  python ops/kdp_package.py
"""
from __future__ import annotations

import io
import json
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPUB = os.path.join(ROOT, "build", "6S-Success-Home-Edition.epub")
COVER = os.path.join(ROOT, "build", "cover.jpg")
OUT = os.path.join(ROOT, "build", "kdp")

LIST_PRICE = 9.99
ROYALTY_RATE = 0.70
DELIVERY_PER_MB = 0.15          # Amazon's US delivery cost on the 70 pct plan

TITLE = "6S Success: Home Edition"
SUBTITLE = "A Six-Step Method for a Home That Works, Room by Room"
AUTHOR = "Philip Kling"
PUBLISHER = "Nova Consulting"

# Seven slots, fifty characters each. Deliberately none of these repeat a word
# already carried by the title or subtitle, because Amazon indexes those
# separately and a duplicated term buys nothing.
KEYWORDS = [
    "decluttering and tidying up for good",
    "cleaning schedule and daily routines",
    "declutter one small zone at a time",
    "chore system for busy families",
    "lean six sigma made practical",
    "organizing checklists and printables",
    "kitchen bathroom garage reset guide",
]

# KDP takes three. These are the shelves this book genuinely belongs on; a
# category chosen because it is easy to rank in is how a book ends up in front
# of readers who did not want it and rate it accordingly.
CATEGORIES = [
    "Crafts, Hobbies & Home > Home Improvement & Design > Cleaning, Caretaking & Relocating",
    "Self-Help > Personal Transformation",
    "Business & Money > Management & Leadership > Quality Control & Management",
]

# Amazon allows light HTML and caps this at 4,000 characters. No invented
# statistic, no testimonial, no claim about results this book has not earned.
DESCRIPTION = """\
<h2>Most home advice starts with a container. This one starts with a question.</h2>

<p>What is this space actually supposed to do?</p>

<p>Answer that honestly and most organizing problems change shape. The keys \
are not lost because you need a nicer tray. They are lost because the tray is \
in the wrong room, or there are four places keys could go, or the thing that \
should hold them is full of something else. A bin does not fix any of that.</p>

<p><b>6S Success: Home Edition</b> brings a method used on factory floors for \
decades into the house, in plain English, with no jargon and no lectures. Six \
passes, always in the same order:</p>

<ul>
<li><b>Sort</b> &mdash; decide what stays</li>
<li><b>Straighten</b> &mdash; give what stays a home where you actually use it</li>
<li><b>Shine</b> &mdash; clean it properly, and use the cleaning to notice what is wearing out</li>
<li><b>Safety</b> &mdash; remove what could hurt somebody</li>
<li><b>Standardize</b> &mdash; make the right state obvious at a glance</li>
<li><b>Sustain</b> &mdash; attach the reset to something you already do</li>
</ul>

<p>The order matters, and the book explains why: straightening before sorting \
is just rearranging things you were about to get rid of.</p>

<h2>Built around micro zones, not whole rooms</h2>

<p>Nobody finishes a kitchen on a Saturday. But almost anyone can finish the \
prep counter, or the drawer beside the stove, or the shelf by the door. This \
book maps <b>114 micro zones</b> across twenty rooms, and works each one the \
same way: what it is for, what usually goes wrong, the root cause underneath, \
the smallest useful fix, and the standard that holds it afterwards.</p>

<h2>What is inside</h2>

<ul>
<li>The full six-step method, one chapter at a time, with worked examples</li>
<li>Twenty room playbooks, from the entryway to the patio</li>
<li>114 micro zones with their functions, root causes and hazards</li>
<li>A standard and a sustain trigger for every zone, so the work holds</li>
<li>Guidance on shared households, accessibility, and small spaces</li>
</ul>

<h2>Who it is for</h2>

<p>People who have organized the same drawer three times. Households where \
one person keeps resetting what everybody else undoes. Anyone who suspects \
the problem is not willpower and is right about that.</p>

<p><i>Written by Philip Kling, a Lean Six Sigma practitioner who spent years \
applying 6S on real shop floors before turning it on his own house.</i></p>
"""


def check_epub() -> dict:
    """Verify the file against the limits Amazon actually enforces."""
    assert os.path.exists(EPUB), f"no EPUB at {EPUB}. Run ops/build_epub.py"
    size = os.path.getsize(EPUB)
    z = zipfile.ZipFile(EPUB)

    opf = [n for n in z.namelist() if n.endswith(".opf")]
    assert opf, "no OPF in the archive, this is not a valid EPUB"
    meta = z.read(opf[0]).decode("utf-8", errors="replace")

    def dc(tag):
        m = re.search(rf"<dc:{tag}[^>]*>(.*?)</dc:{tag}>", meta, re.S)
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""

    creator, pub = dc("creator"), dc("publisher")
    assert creator and not creator.startswith("["), (
        f"dc:creator is {creator!r}. Amazon rejects a book with no author.")
    assert pub and not pub.startswith("["), f"dc:publisher is {pub!r}"
    assert dc("title"), "no dc:title"
    assert dc("language"), "no dc:language, Amazon requires one"

    # A bracketed placeholder anywhere in the archive reaches the reader.
    leaks = []
    for n in z.namelist():
        if n.endswith((".xhtml", ".html", ".opf", ".ncx")):
            t = z.read(n).decode("utf-8", errors="replace")
            if re.search(r"\[(AUTHOR|IMPRINT|PUBLISHER|ISBN|YEAR|DESIGNER|"
                         r"ILLUSTRATOR|TERRITORY)[^\]]*\]", t):
                leaks.append(n)
    assert not leaks, f"bracketed placeholders still in {leaks[:3]}"

    assert "nav" in meta or any("nav" in n.lower() for n in z.namelist()), (
        "no navigation document. Amazon requires a working table of contents.")

    # 650 MB is the hard ceiling. Nowhere near it, but the number that
    # actually matters is delivery cost, which is charged per megabyte.
    mb = size / 1048576
    assert mb < 650, f"{mb:.0f} MB is over Amazon's 650 MB limit"

    docs = [n for n in z.namelist() if n.endswith((".xhtml", ".html"))]
    words = 0
    for n in docs:
        t = z.read(n).decode("utf-8", errors="replace")
        t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", t, flags=re.S)
        words += len(re.sub(r"<[^>]+>", " ", t).split())

    return {"size_mb": mb, "creator": creator, "publisher": pub,
            "title": dc("title"), "docs": len(docs), "words": words}


def check_cover() -> dict:
    from PIL import Image
    assert os.path.exists(COVER), f"no cover at {COVER}"
    w, h = Image.open(COVER).size
    ratio = h / w
    assert h >= 1000, f"cover is {h}px tall, Amazon wants at least 1000 and prefers 2560"
    assert 1.4 <= ratio <= 1.8, f"cover ratio {ratio:.2f}, Amazon wants 1.6"
    return {"w": w, "h": h, "ratio": ratio,
            "mb": os.path.getsize(COVER) / 1048576}


def check_metadata() -> None:
    assert len(DESCRIPTION) <= 4000, (
        f"description is {len(DESCRIPTION)} characters, Amazon caps it at 4,000")
    assert len(KEYWORDS) <= 7, "Amazon takes seven keyword slots"
    long = [k for k in KEYWORDS if len(k) > 50]
    assert not long, f"keywords over 50 characters: {long}"
    assert len(CATEGORIES) <= 3, "Amazon takes three categories"

    # A keyword repeating a title word is a wasted slot: Amazon already
    # indexes the title and subtitle separately.
    titled = set(re.findall(r"[a-z]{4,}", (TITLE + " " + SUBTITLE).lower()))
    wasted = [k for k in KEYWORDS
              if set(re.findall(r"[a-z]{4,}", k.lower())) & titled]
    if wasted:
        print(f"  note: keywords sharing a word with the title: {wasted}")

    assert 2.99 <= LIST_PRICE <= 9.99, (
        f"${LIST_PRICE} falls outside Amazon's 70 percent royalty band, so the "
        f"rate drops to 35 percent. That is a deliberate choice if made, and "
        f"this is not it.")


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    e = check_epub()
    c = check_cover()
    check_metadata()

    delivery = e["size_mb"] * DELIVERY_PER_MB
    net = LIST_PRICE * ROYALTY_RATE - delivery

    print(f"  book    {e['words']:,} words, {e['docs']} documents, "
          f"{e['size_mb']:.2f} MB")
    print(f"  by      {e['creator']} / {e['publisher']}")
    print(f"  cover   {c['w']}x{c['h']}, ratio {c['ratio']:.2f}, "
          f"{c['mb']:.2f} MB")
    print(f"  price   ${LIST_PRICE} at {ROYALTY_RATE:.0%}, "
          f"less ${delivery:.2f} delivery, nets ${net:.2f} a copy")
    print(f"  meta    {len(DESCRIPTION)} of 4,000 description characters, "
          f"{len(KEYWORDS)} keywords, {len(CATEGORIES)} categories")

    pkg = {
        "title": TITLE, "subtitle": SUBTITLE, "author": AUTHOR,
        "publisher": PUBLISHER, "language": "English",
        "list_price_usd": LIST_PRICE, "royalty_plan": "70%",
        "net_per_copy_usd": round(net, 2),
        "keywords": KEYWORDS, "categories": CATEGORIES,
        "description_html": DESCRIPTION,
        "manuscript": os.path.relpath(EPUB, ROOT).replace(os.sep, "/"),
        "cover": os.path.relpath(COVER, ROOT).replace(os.sep, "/"),
        "drm": False,
        "_drm_note": ("No DRM. The same file is sold direct from the site "
                      "without it, and applying DRM only on Amazon would make "
                      "the Amazon edition the worse one."),
        "territories": "All (worldwide rights held)",
        "kindle_unlimited": False,
        "_ku_note": ("KDP Select requires 90 days of digital exclusivity, "
                     "which would mean pulling the book from 6s-success.com. "
                     "Not worth it while direct is the only channel that has "
                     "ever sold anything."),
    }
    with open(os.path.join(OUT, "listing.json"), "w", encoding="utf-8",
              newline="") as fh:
        json.dump(pkg, fh, indent=2, ensure_ascii=False)

    with open(os.path.join(OUT, "description.html"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(DESCRIPTION)

    lines = [
        "KDP LISTING, COPY AND PASTE",
        "=" * 62, "",
        f"Title            {TITLE}",
        f"Subtitle         {SUBTITLE}",
        f"Author           {AUTHOR}",
        f"Publisher        {PUBLISHER}",
        "Language         English",
        "ISBN             leave blank, Amazon issues a free ASIN",
        "",
        "Description      paste build/kdp/description.html",
        "",
        "Keywords         (seven slots)",
    ]
    lines += [f"  {i}. {k}" for i, k in enumerate(KEYWORDS, 1)]
    lines += ["", "Categories       (three)"]
    lines += [f"  {i}. {c}" for i, c in enumerate(CATEGORIES, 1)]
    lines += [
        "",
        f"Manuscript       {pkg['manuscript']}",
        f"Cover            {pkg['cover']}",
        "",
        "DRM              No",
        "KDP Select       No. It demands 90 days of exclusivity and would",
        "                 mean pulling the book off 6s-success.com.",
        "",
        f"Price            ${LIST_PRICE} USD, 70 percent royalty plan",
        f"                 nets about ${net:.2f} a copy after ${delivery:.2f} delivery",
        "Territories      All",
        "",
        "WHAT ONLY YOU CAN DO",
        "-" * 62,
        "Signing in, and the tax interview and bank details on first",
        "publish. Those are account and financial credentials, so they stay",
        "with you. Everything above is ready to paste.",
    ]
    with open(os.path.join(OUT, "UPLOAD.txt"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"\n  wrote build/kdp/: listing.json, description.html, UPLOAD.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
