#!/usr/bin/env python3
"""Check the Etsy listing package against the form limits and the real files.

WHAT IT CAN AND CANNOT KNOW
---------------------------
Etsy blocks automated access. Every request to etsy.com/legal/fees and to the
seller pages of help.etsy.com returned HTTP 403 on 2026-09-03, so the limits
below were not read from Etsy today and are marked accordingly. They are the
limits the listing form has long enforced, and the copy is written well inside
them, so the package survives being wrong about them.

What this script does know for certain is the part that matters most and is
usually got wrong anyway: whether the files each listing promises actually
exist, whether the page and card counts quoted in the titles match the finished
PDFs, and whether any file is too big to upload.

Run:  python build/listings/check_etsy.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import pymupdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
ETSY = os.path.join(HERE, "etsy")

TITLE_MAX = 140        # UNVERIFIED 2026-09-03, Etsy blocks automated reads
TAG_MAX_CHARS = 20     # UNVERIFIED
TAG_SLOTS = 13         # UNVERIFIED
FILES_PER_LISTING = 5  # UNVERIFIED
FILE_MAX_MB = 20       # UNVERIFIED
CARD_MARK = re.compile(r"\b\d+ / \d+\b")

ok, fail, unchecked = [], [], []


def main() -> int:
    data = json.load(open(os.path.join(HERE, "etsy-listings.json"),
                          encoding="utf-8"))
    for item in data["listings"]:
        slug = item["slug"]
        title = item["title"]

        if len(title) <= TITLE_MAX:
            ok.append("%s title is %d characters" % (slug, len(title)))
        else:
            fail.append("%s title is %d characters, over %d"
                        % (slug, len(title), TITLE_MAX))

        tags = item["tags"]
        if len(tags) == TAG_SLOTS:
            ok.append("%s uses all %d tag slots" % (slug, TAG_SLOTS))
        else:
            fail.append("%s has %d tags, the form gives %d"
                        % (slug, len(tags), TAG_SLOTS))
        long_tags = [t for t in tags if len(t) > TAG_MAX_CHARS]
        if long_tags:
            fail.append("%s tags over %d characters: %s"
                        % (slug, TAG_MAX_CHARS, long_tags))
        else:
            ok.append("%s longest tag is %d characters"
                      % (slug, max(len(t) for t in tags)))
        if len(set(tags)) != len(tags):
            fail.append("%s repeats a tag" % slug)

        # A tag that only repeats words already in the title is a wasted slot
        # in a shop with thirteen of them.
        title_words = set(re.findall(r"[a-z]+", title.lower()))
        redundant = [t for t in tags
                     if set(re.findall(r"[a-z]+", t.lower())) <= title_words]
        if redundant:
            unchecked.append("%s tags whose every word is already in the "
                             "title, which may still be worth keeping because "
                             "Etsy matches tags as whole phrases: %s"
                             % (slug, redundant))

        # ---- the files -----------------------------------------------------
        fdir = os.path.join(ETSY, slug, "files")
        missing = [f for f in item["files"]
                   if not os.path.exists(os.path.join(fdir, f))]
        if missing:
            fail.append("%s promises files that do not exist: %s"
                        % (slug, missing))
            continue
        if len(item["files"]) > FILES_PER_LISTING:
            fail.append("%s attaches %d files, the form allows %d"
                        % (slug, len(item["files"]), FILES_PER_LISTING))

        pages, cards, oversize = 0, 0, []
        for name in item["files"]:
            path = os.path.join(fdir, name)
            mb = os.path.getsize(path) / (1024 * 1024)
            if mb > FILE_MAX_MB:
                oversize.append("%s %.1f MB" % (name, mb))
            doc = pymupdf.open(path)
            pages += doc.page_count
            for page in doc:
                cards += len(CARD_MARK.findall(page.get_text()))
            doc.close()
        if oversize:
            fail.append("%s has files over the %d MB cap: %s"
                        % (slug, FILE_MAX_MB, oversize))
        else:
            ok.append("%s delivers %d files, all under the %d MB cap"
                      % (slug, len(item["files"]), FILE_MAX_MB))

        for label, measured, claimed in (("pages", pages, item["pages"]),
                                         ("cards", cards, item["cards"])):
            if measured == claimed:
                ok.append("%s really does contain %d %s" % (slug, measured, label))
            else:
                fail.append("%s claims %d %s, the files contain %d"
                            % (slug, claimed, label, measured))

        images = os.path.join(ETSY, slug, "listing-images")
        n_images = len(os.listdir(images)) if os.path.isdir(images) else 0
        if n_images:
            ok.append("%s has %d listing images ready" % (slug, n_images))
        else:
            fail.append("%s has no listing images" % slug)

        # Etsy forbids using a listing to send buyers off Etsy to transact.
        # A branded footer is not that, but it is worth knowing it is there.
        for name in item["files"]:
            doc = pymupdf.open(os.path.join(fdir, name))
            body = "".join(p.get_text() for p in doc)
            doc.close()
            if "6s-success.com" in body.lower():
                unchecked.append("%s/%s carries the 6s-success.com footer. "
                                 "That is branding on a delivered file, not a "
                                 "solicitation in a listing, but Etsy's policy "
                                 "on it was not readable today." % (slug, name))

    unchecked.append("Etsy's fee schedule: not fetched, HTTP 403. Read it off "
                     "the fee page and run build/listings/etsy_economics.py "
                     "with the real numbers before trusting any margin.")
    unchecked.append("Etsy's category taxonomy: not fetched. The category path "
                     "in MARKETPLACE-LISTINGS.md is a best guess at the "
                     "picker's wording.")
    unchecked.append("Comparable listings, their prices and their tags: not "
                     "fetched, and nothing in this package should be read as "
                     "evidence about what competitors charge or sell.")
    unchecked.append("Listing image aspect ratio: Etsy's recommended crop was "
                     "not readable. The images are 2000x1500 with wide "
                     "margins, so a square or 4:3 crop keeps the content.")

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
