#!/usr/bin/env python3
"""Print the zones each Etsy deliverable really contains.

WHY
---
The listing descriptions name zones. A description that names a zone the pack
does not contain is a false claim about a product somebody paid for, and it is
the easiest kind of mistake to make, because the zone lists look plausible from
memory. The first draft of the Kitchen listing claimed a "small appliance zone"
the pack does not have; it has a utensil and utility drawer zone instead. This
script is what caught it.

WHY THE FILE LIST COMES FROM etsy-listings.json
------------------------------------------------
This used to hardcode one file per listing. L1 bundles its per-room standards
sheet as a second, separate PDF (`6S-Standards-Pack.pdf`, listed correctly in
`etsy-listings.json` and in `MARKETPLACE-LISTINGS.md`), which the hardcoded
single-file list never opened. So on every run this printed "standards sheet
ABSENT" for the flagship, highest-price listing, a false negative on the one
check that exists specifically to catch a false product claim: the standards
sheet is real, just delivered as its own file for that listing. Reading the
real file list from `etsy-listings.json`, the same source `check_etsy.py`
already treats as authoritative, means a listing can never again be checked
against a file it does not actually ship.

Standards content also does not always use the same wording: a listing whose
standards live inside the main pack PDF carries the header "The standards
that keep these zones", but L1's standalone Standards Pack is one sheet per
room headed "N ZONES - SHEET n OF 20" and never uses that phrase at all. Both
count as present.

Run it after any change to the listing copy in MARKETPLACE-LISTINGS.md and read
the output against what the copy says.

Run:  python build/listings/verify_zone_claims.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ETSY = os.path.join(HERE, "etsy")

ZONE = re.compile(r"\b\d+ / \d+\n([A-Z][A-Z &,\-']+)\n(.+)")
STANDARDS_MARKERS = (
    re.compile(r"standards that keep", re.I),
    re.compile(r"\bSHEET \d+ OF \d+\b", re.I),
)


def main() -> int:
    data = json.load(open(os.path.join(HERE, "etsy-listings.json"),
                          encoding="utf-8"))
    for item in data["listings"]:
        label = item["slug"] + "  " + item["title"].split(" - ")[0]
        texts = []
        missing = []
        for fname in item["files"]:
            path = os.path.join(ETSY, item["slug"], "files", fname)
            if not os.path.exists(path):
                missing.append(fname)
                continue
            doc = pymupdf.open(path)
            texts.append("\n".join(page.get_text() for page in doc))
            doc.close()
        if not texts:
            print(label + ": MISSING, run build_etsy_assets.py first")
            continue
        text = "\n".join(texts)
        zones, rooms = [], []
        for match in ZONE.finditer(text):
            pair = (match.group(1).strip(), match.group(2).strip())
            if pair not in zones:
                zones.append(pair)
            if pair[0] not in rooms:
                rooms.append(pair[0])
        has_standards = any(m.search(text) for m in STANDARDS_MARKERS)
        print("")
        print(label + ": " + str(len(zones)) + " zones across "
              + str(len(rooms)) + " rooms, standards sheet "
              + ("present" if has_standards else "ABSENT")
              + (" (missing: %s)" % ", ".join(missing) if missing else ""))
        for room, zone in zones:
            print("    " + room + "  |  " + zone)
    print("")
    print("Zone titles are read from the card faces, so a zone whose name wraps "
          "across two lines shows here truncated at the wrap. Check the PDF "
          "before quoting one of those in copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
