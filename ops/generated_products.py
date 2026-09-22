#!/usr/bin/env python3
"""
The one list of generated products, imported by everything that needs it.

WHY A SEPARATE MODULE
---------------------
Three files need to agree about these products: the site catalogue in
site/assets/js/data.js decides what a visitor sees, ops/stripe_catalog.py
decides what exists in Stripe, and ops/stripe_fulfil.py decides what an email
attaches after somebody pays. If those three lists are maintained separately
they drift, and every way they can drift hurts a customer: a product listed
and not sellable, sellable and not deliverable, or deliverable and not listed.

So the list is computed once, here, and the other three import it.

WHAT IS EXCLUDED, AND WHY
-------------------------
Not everything the generator can produce should be sold.

1. Anything the free Entryway deck already covers. That deck is advertised as
   free and carries all five entryway zones. A four dollar pack of the same
   cards is not gating free content, but it is selling somebody a strictly
   worse version of something they could have for nothing, and a customer who
   found out afterwards would be right to be angry. Six SKUs go.

2. Anything priced at or above the whole house pack. That pack is nineteen
   dollars and contains all 684 cards, so it is a superset of every product
   here. ops/build_catalog.py asserts this ceiling; this module trusts it and
   re-checks rather than assuming.

3. Explicitly retired SKUs (RETIRED below). Unlike 1 and 2, these are not
   computed: `REVIEW-COMMERCE-2026-09-07.md` sections 1.3 and 1.4 found the 6
   Area Bundles charging 84% of the $19 superset's price for 12-20% of its
   content, and the 15 Situation Kits charging 74% for 7-20%, both tiers with
   zero realised sales, no page, and no internal link. Retiring a hand-picked
   set has to be a hand-picked list; there is no property of the generated
   data that would derive it. Full definitions, prices and reasons preserved
   in `ops/retired-skus.json`, entries dated 2026-09-22; `DECISIONS.md` D-023
   records the Situation Kits' re-entry condition. This is the repository-side
   half only: the live shop still needs to be verified clear of these before
   the matching Stripe payment links are archived (`ops/stripe_catalog.py`'s
   `ensure_link` already refuses to retire a link production is still
   serving), and no sandbox this module has run in holds a Stripe credential.

The exclusion in 1 and 2 is computed from the free products actually in the
catalogue, not from a hand written list of SKUs, so adding another free deck
later removes the packs it duplicates without anybody remembering to. The
retired list in 3 is deliberately the exception: these are not superseded by
anything else in the catalogue, they are the products themselves in question.
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_catalog as bc                                     # noqa: E402

PRODUCT_DIR = os.path.join(ROOT, "build", "products")
DATA_JS = os.path.join(ROOT, "site", "assets", "js", "data.js")

# Hand-picked, not derived. See "WHAT IS EXCLUDED, AND WHY" point 3 above.
# Kept here, not in ops/retired-skus.json, because this is the list that
# actually controls what wire_generated_catalog.py writes; retired-skus.json
# is the historical record a human or an audit reads, not a second source of
# truth this module would have to stay in sync with.
RETIRED = {
    "AB-WET-ROOMS": "Area Bundle, $16 for 108 cards (16% of the $19 superset's "
                     "684), no page, no internal link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "AB-SLEEPING": "Area Bundle, $16 for 138 cards (20%), no page, no internal "
                    "link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "AB-STORAGE": "Area Bundle, $16 for 138 cards (20%), no page, no internal "
                   "link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "AB-LIVING": "Area Bundle, $16 for 102 cards (15%), no page, no internal "
                  "link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "AB-THRESHOLDS": "Area Bundle, $16 for 84 cards (12%), no page, no internal "
                      "link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "AB-FOOD": "Area Bundle, $16 for 102 cards (15%), no page, no internal "
                "link. REVIEW-COMMERCE-2026-09-07.md 1.3.",
    "KIT-MOVING-IN": "Situation Kit, $14 for 78 cards (11%), no page, no "
                      "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-MOVING-OUT": "Situation Kit, $14 for 90 cards (13%), no page, no "
                       "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-NEW-BABY": "Situation Kit, $14 for 54 cards (8%), no page, no "
                     "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-BACK-TO-SCHO": "Situation Kit, $14 for 48 cards (7%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-HOLIDAY-HOST": "Situation Kit, $14 for 96 cards (14%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-DOWNSIZING": "Situation Kit, $14 for 96 cards (14%), no page, no "
                       "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-SPRING-RESET": "Situation Kit, $14 for 138 cards (20%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-SMALL-APARTM": "Situation Kit, $14 for 120 cards (18%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-WORKING-FROM": "Situation Kit, $14 for 48 cards (7%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-PET-HOUSEHOL": "Situation Kit, $14 for 60 cards (9%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-AGEING-IN-PL": "Situation Kit, $14 for 78 cards (11%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-POST-RENOVAT": "Situation Kit, $14 for 60 cards (9%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-FIRST-HOME": "Situation Kit, $14 for 48 cards (7%), no page, no "
                       "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-SHARED-HOUSE": "Situation Kit, $14 for 96 cards (14%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
    "KIT-RENTAL-HANDO": "Situation Kit, $14 for 120 cards (18%), no page, no "
                         "internal link. REVIEW-COMMERCE-2026-09-07.md 1.4.",
}


def site_catalogue() -> list:
    js = io.open(DATA_JS, encoding="utf-8").read()
    return json.loads(js[js.index("["):js.rindex("]") + 1])


def free_zone_coverage() -> set:
    """Room and zone pairs a visitor can already print for nothing.

    Read from the free deck's own generator input rather than by scraping the
    rendered page, because the rendered page is a print layout and its headings
    are styled, not structured.
    """
    covered = set()
    free = {i["sku"] for i in site_catalogue() if not i.get("price")}
    # The only free product that carries zone cards today. Named explicitly
    # because the mapping from a SKU to the zones it covers is not derivable
    # from the catalogue entry, which holds marketing copy rather than zones.
    if "DECK-ENTRY" in free:
        d = bc.load()
        for r in d["rooms"]:
            if r["room"] == "Entryway":
                for z in r["zones"]:
                    covered.add((r["room"], z["zone"]))
    return covered


def products() -> list:
    """Every generated product that is honest to sell, with its file."""
    d = bc.load()
    items = bc.catalogue(d)
    free = free_zone_coverage()

    out, dropped = [], []
    for it in items:
        zones = {(room, z["zone"]) for room, z in it["zones"]}
        # A product whose every zone is already free is not a product.
        if zones and zones <= free:
            dropped.append((it["sku"], "already free in the Entryway deck"))
            continue
        if it["price"] >= bc.WHOLE_HOUSE:
            dropped.append((it["sku"], f"at or above the ${bc.WHOLE_HOUSE} superset"))
            continue
        if it["sku"] in RETIRED:
            dropped.append((it["sku"], "retired: " + RETIRED[it["sku"]]))
            continue
        it = dict(it)
        it["deliverable"] = f"build/products/{it['sku']}.html"
        out.append(it)

    return out, dropped


def check() -> int:
    keep, dropped = products()
    print(f"  {len(keep)} generated products are honest to sell")
    print(f"  {len(dropped)} excluded:")
    for sku, why in dropped:
        print(f"    {sku:24} {why}")

    missing = [p["sku"] for p in keep
               if not os.path.exists(os.path.join(ROOT, p["deliverable"]))]
    if missing:
        print(f"\n  {len(missing)} have no file built yet, run "
              f"ops/build_catalog.py --build: {missing[:3]}")
        return 1

    # A product nobody can receive must never reach a payment link. This is
    # the same rule ops/stripe_catalog.py enforces; checking twice is cheap
    # and the failure it prevents lands on somebody who has paid.
    empty = [p["sku"] for p in keep
             if os.path.getsize(os.path.join(ROOT, p["deliverable"])) < 4000]
    assert not empty, f"deliverable file suspiciously small for {empty[:4]}"
    print(f"  every one has a built file of a plausible size")

    by = {}
    for p in keep:
        by.setdefault(p["kind"], []).append(p)
    print()
    for k in ("zone", "room", "situation", "area"):
        if k in by:
            print(f"    {k:11} {len(by[k]):>4}  at ${by[k][0]['price']}")
    print(f"\n  gross if one of each sold: "
          f"${sum(p['price'] for p in keep):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
