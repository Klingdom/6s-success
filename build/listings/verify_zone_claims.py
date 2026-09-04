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

Run it after any change to the listing copy in MARKETPLACE-LISTINGS.md and read
the output against what the copy says.

Run:  python build/listings/verify_zone_claims.py
"""
from __future__ import annotations

import os
import re
import sys

import pymupdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ETSY = os.path.join(ROOT, "build", "listings", "etsy")

FILES = [
    ("L2  Kitchen Pack", "L2-kitchen/files/6S-Kitchen-Pack.pdf"),
    ("L3  Entryway Pack", "L3-entryway/files/6S-Entryway-Pack.pdf"),
    ("L4  Moving In Kit", "L4-moving-in/files/6S-Moving-In-Kit.pdf"),
    ("L5  Holiday Hosting Kit",
     "L5-holiday-hosting/files/6S-Holiday-Hosting-Kit.pdf"),
    ("L1  Whole House Print Pack",
     "L1-whole-house/files/6S-Whole-House-Print-Pack.pdf"),
]

ZONE = re.compile(r"\b\d+ / \d+\n([A-Z][A-Z &,\-']+)\n(.+)")


def main() -> int:
    for label, rel in FILES:
        path = os.path.join(ETSY, rel)
        if not os.path.exists(path):
            print(label + ": MISSING, run build_etsy_assets.py first")
            continue
        doc = pymupdf.open(path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        zones, rooms = [], []
        for match in ZONE.finditer(text):
            pair = (match.group(1).strip(), match.group(2).strip())
            if pair not in zones:
                zones.append(pair)
            if pair[0] not in rooms:
                rooms.append(pair[0])
        print("")
        print(label + ": " + str(len(zones)) + " zones across "
              + str(len(rooms)) + " rooms, standards sheet "
              + ("present" if "standards that keep" in text.lower() else "ABSENT"))
        for room, zone in zones:
            print("    " + room + "  |  " + zone)
    print("")
    print("Zone titles are read from the card faces, so a zone whose name wraps "
          "across two lines shows here truncated at the wrap. Check the PDF "
          "before quoting one of those in copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
