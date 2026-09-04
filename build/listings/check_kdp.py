#!/usr/bin/env python3
"""Check the KDP listing package against the rules and against the real files.

Every rule marked VERIFIED below was read off kdp.amazon.com on 2026-09-03 and
the help page it came from is named, so when Amazon changes one, the check that
goes stale is findable. Anything this script cannot test says UNCHECKED rather
than passing quietly, because a green run that skipped a gate is the failure
mode that has cost this repository the most.

Run:  python build/listings/check_kdp.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))

ALLOWED_TAGS = {"br", "p", "b", "em", "i", "u", "h4", "h5", "h6", "ol", "ul", "li"}
DESC_LIMIT = 4000          # VERIFIED: Write a Book Description, G201189630
KEYWORD_SLOTS = 7          # VERIFIED: Make Your Book More Discoverable, G201298500
CATEGORY_SLOTS = 3         # VERIFIED: KDP Categories, G200652170
COVER_MIN = (625, 1000)    # VERIFIED: cover criteria, G200645690
COVER_MAX = 10000
COVER_RATIO = 1.6
COVER_MAX_BYTES = 50 * 1024 * 1024
ROYALTY_70_BAND = (2.99, 12.99)   # VERIFIED: eBook List Price Requirements,
                                  # G200634560, band widened 2026-07-07
DELIVERY_PER_MB_USD = 0.15        # VERIFIED: Digital Book Pricing Page, G200634500

ok, fail, unchecked = [], [], []


def check(condition, good, bad):
    (ok if condition else fail).append(good if condition else bad)


def main() -> int:
    fields = json.load(open(os.path.join(HERE, "kdp", "fields.json"),
                            encoding="utf-8"))
    desc = open(os.path.join(HERE, "kdp", "description.html"),
                encoding="utf-8").read().strip()

    # ---- description -------------------------------------------------------
    check(len(desc) <= DESC_LIMIT,
          "description is %d characters including tags, under the %d limit"
          % (len(desc), DESC_LIMIT),
          "description is %d characters, over the %d limit"
          % (len(desc), DESC_LIMIT))
    tags = {t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", desc)}
    bad_tags = sorted(tags - ALLOWED_TAGS)
    check(not bad_tags,
          "description uses only tags KDP supports: " + ", ".join(sorted(tags)),
          "description uses tags KDP rejects: " + ", ".join(bad_tags)
          + ". h1, h2 and h3 are explicitly unsupported.")
    urls = re.findall(r"https?://|www\.|\.com\b|\.org\b|\.net\b", desc)
    check(not urls,
          "description contains no URL, which KDP forbids there",
          "description contains something that reads as a URL: " + str(set(urls)))
    check(all(ord(c) < 128 for c in desc),
          "description is plain ASCII, so no character can arrive mangled",
          "description contains non-ASCII characters: "
          + str(sorted({c for c in desc if ord(c) > 127})))

    # ---- keywords ----------------------------------------------------------
    kw = fields["keywords"]
    check(len(kw) == KEYWORD_SLOTS,
          "%d keyword slots filled" % len(kw),
          "%d keywords, KDP gives %d slots" % (len(kw), KEYWORD_SLOTS))
    long_kw = [k for k in kw if len(k) > 50]
    check(not long_kw,
          "every keyword slot is 50 characters or fewer, longest is %d"
          % max(len(k) for k in kw),
          "keyword slots over 50 characters: " + str(long_kw))
    quoted = [k for k in kw if '"' in k or "'" in k]
    check(not quoted,
          "no keyword uses quotation marks, which KDP says narrows the match",
          "keywords contain quotation marks: " + str(quoted))

    # A keyword that repeats a word already in the title or subtitle spends a
    # slot on a token Amazon has indexed anyway.
    titled = set(re.findall(r"[a-z0-9]+",
                            (fields["book_title"] + " "
                             + fields["subtitle"]).lower()))
    wasted = sorted({w for k in kw for w in re.findall(r"[a-z0-9]+", k.lower())}
                    & titled - {"a", "the", "and", "for", "your", "in", "of",
                                "at", "one", "you", "when", "it", "to"})
    check(not wasted,
          "no keyword repeats a content word from the title or subtitle",
          "keywords repeat words already indexed from the title or subtitle, "
          "which spends a slot for nothing: " + ", ".join(wasted))

    # ---- categories --------------------------------------------------------
    cats = fields["categories_to_enter"]
    check(len(cats) == CATEGORY_SLOTS,
          "%d categories chosen, matching the %d the form accepts"
          % (len(cats), CATEGORY_SLOTS),
          "%d categories chosen, the form accepts %d"
          % (len(cats), CATEGORY_SLOTS))

    # ---- price -------------------------------------------------------------
    price = fields["list_price_usd"]
    if fields["royalty_plan"] == "70%":
        check(ROYALTY_70_BAND[0] <= price <= ROYALTY_70_BAND[1],
              "$%.2f is inside the 70%% royalty band $%.2f to $%.2f"
              % (price, *ROYALTY_70_BAND),
              "$%.2f is outside the 70%% royalty band $%.2f to $%.2f"
              % (price, *ROYALTY_70_BAND))

    # ---- cover -------------------------------------------------------------
    cover = os.path.join(ROOT, fields["cover"])
    check(os.path.splitext(cover)[1].lower() in (".jpg", ".jpeg", ".tif", ".tiff"),
          "cover file is a format KDP accepts",
          "cover file is not JPEG or TIFF, the only formats KDP accepts")
    try:
        from PIL import Image
        img = Image.open(cover)
        w, h = img.size
        check(w >= COVER_MIN[0] and h >= COVER_MIN[1],
              "cover is %dx%d, above the %dx%d minimum" % (w, h, *COVER_MIN),
              "cover is %dx%d, below the %dx%d minimum" % (w, h, *COVER_MIN))
        check(w <= COVER_MAX and h <= COVER_MAX,
              "cover is within the %d pixel maximum" % COVER_MAX,
              "cover exceeds the %d pixel maximum" % COVER_MAX)
        check(h / w >= COVER_RATIO - 1e-9,
              "cover height/width is %.4f, meeting the ideal %.1f:1"
              % (h / w, COVER_RATIO),
              "cover height/width is %.4f, below the ideal %.1f:1"
              % (h / w, COVER_RATIO))
        check(img.mode == "RGB",
              "cover colour mode is RGB as required",
              "cover colour mode is %s, KDP wants RGB" % img.mode)
        check(os.path.getsize(cover) < COVER_MAX_BYTES,
              "cover is %.0f KB, well under the 50 MB cap"
              % (os.path.getsize(cover) / 1024),
              "cover is over the 50 MB cap")
        if (w, h) == (1600, 2560):
            ok.append("cover is exactly the 1600x2560 KDP calls ideal")
    except ImportError:
        unchecked.append("cover geometry: Pillow not installed")

    # ---- manuscript --------------------------------------------------------
    epub = os.path.join(ROOT, fields["manuscript"])
    check(os.path.exists(epub), "manuscript file is present at " + fields["manuscript"],
          "manuscript file is missing at " + fields["manuscript"])
    if os.path.exists(epub):
        size = os.path.getsize(epub)
        zf = zipfile.ZipFile(epub)
        opf = [n for n in zf.namelist() if n.endswith(".opf")]
        meta = zf.read(opf[0]).decode("utf-8") if opf else ""
        for field, tag in (("book_title", "title"), ("author_first", "creator")):
            value = fields[field]
            check(value in meta,
                  "EPUB metadata carries the %s that goes in the form" % tag,
                  "EPUB %s does not match the form value %r" % (tag, value))
        delivery = size / (1024 * 1024) * DELIVERY_PER_MB_USD
        royalty = 0.70 * (price - delivery)
        ok.append("at $%.2f on the 70%% plan, and taking the EPUB's own %.2f MB "
                  "as a stand-in for the converted file, delivery is about "
                  "$%.2f and the royalty about $%.2f a copy"
                  % (price, size / (1024 * 1024), delivery, royalty))
        ok.append("at $%.2f on the 35%% plan the royalty would be $%.2f, so the "
                  "70%% plan is worth $%.2f more per copy"
                  % (price, 0.35 * price, royalty - 0.35 * price))
        unchecked.append("the real delivery cost: Amazon charges on the size of "
                         "its own converted file, not the EPUB. KDP shows that "
                         "number on the pricing screen before you publish.")

    unchecked.append("epubcheck conformance: no JRE on this machine. "
                     "build/listings/verify_epub.py covers what a zip and XML "
                     "reader can see and says what it cannot.")
    unchecked.append("how the book renders on a device: only Kindle Previewer "
                     "or Amazon's own converter can answer that.")
    unchecked.append("whether the category paths still read exactly as written: "
                     "the browse nodes were confirmed on Amazon on 2026-09-03, "
                     "but the KDP picker phrases some of them differently.")
    unchecked.append("the character limit on the title and subtitle fields: not "
                     "stated on any help page fetched. Both are short enough "
                     "that it does not matter.")

    print("PASS")
    for line in ok:
        print("  [ok] " + line)
    print("")
    print("FAIL")
    for line in fail:
        print("  [FAIL] " + line)
    if not fail:
        print("  (none)")
    print("")
    print("UNCHECKED")
    for line in unchecked:
        print("  [??] " + line)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
