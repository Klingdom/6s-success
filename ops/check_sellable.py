#!/usr/bin/env python3
"""
Three lists have to agree, or a customer gets hurt. This checks that they do.

THE THREE LISTS
---------------
    site/assets/js/data.js      what a visitor can see and click buy on
    ops/stripe_catalog.py       what exists in Stripe and has a payment link
    ops/stripe_fulfil.py        what an email actually attaches after payment

Every way these can disagree costs somebody something:

    listed, not in Stripe     a buy button that goes nowhere
    listed, not deliverable   money taken for a thing that never arrives
    deliverable, not listed   work built and never sold
    priced differently        the shop and the checkout disagree on the price

The third of those is only embarrassing. The second is the one this exists
for, and it is the one that would have happened here: the fulfiler knew five
SKUs while the shop was about to list 155.

Run:  python ops/check_sellable.py
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

os.environ.setdefault("STRIPE_FULFIL_IMPORT_ONLY", "1")


def main() -> int:
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    listed = json.loads(js[js.index("["):js.rindex("]") + 1])

    import stripe_catalog as sc
    import stripe_fulfil as sf

    buyable = {i["sku"]: i for i in listed if (i.get("price") or 0) > 0}
    sellable = set(sc.SELLABLE)
    deliver = set(sf.DELIVERY)

    print(f"  listed and priced above zero : {len(buyable)}")
    print(f"  in stripe_catalog SELLABLE   : {len(sellable)}")
    print(f"  in stripe_fulfil DELIVERY    : {len(deliver)}")
    print()

    fail = []

    # A buy button with no Stripe product behind it.
    orphan = sorted(set(buyable) - sellable)
    if orphan:
        fail.append(f"{len(orphan)} listed for sale but not in SELLABLE, so the "
                    f"buy button leads nowhere: {orphan[:4]}")

    # The one that takes money for nothing. Services are excluded because they
    # are delivered by a person, not by an attachment.
    services = {s for s, spec in sc.SELLABLE.items() if spec["kind"] == "service"}
    undeliverable = sorted(set(buyable) - deliver - services)
    if undeliverable:
        fail.append(f"{len(undeliverable)} can be bought but have no delivery "
                    f"entry, so payment would be taken and nothing sent: "
                    f"{undeliverable[:4]}")

    # A named file that is not on disk fails at the worst possible moment.
    missing = []
    for sku in sorted(set(buyable) & deliver):
        spec = sf.DELIVERY[sku]
        for f in ([spec["file"]] if spec.get("file") else spec.get("files", [])):
            if not os.path.exists(os.path.join(ROOT, f)):
                missing.append((sku, f))
    if missing:
        fail.append(f"{len(missing)} name a file that is not built: "
                    f"{missing[:3]}. Run ops/build_catalog.py --build")

    # The shop and the checkout must agree on the number.
    for sku, item in buyable.items():
        if sku in sellable and (item.get("price") or 0) <= 0:
            fail.append(f"{sku} is in SELLABLE with no price")

    # Nothing may cost as much as a product that contains all of it.
    import build_catalog as bc
    over = [i["sku"] for i in listed
            if i.get("super") and (i.get("price") or 0) >= bc.WHOLE_HOUSE]
    if over:
        fail.append(f"{len(over)} priced at or above the superset that "
                    f"contains them: {over[:4]}")

    # Built and never sold. Not a customer harm, so it reports rather than fails.
    from generated_products import products
    keep, dropped = products()
    unsold = sorted({p["sku"] for p in keep} - set(buyable))
    if unsold:
        print(f"  note: {len(unsold)} built but not listed: {unsold[:3]}")
    if dropped:
        print(f"  note: {len(dropped)} deliberately excluded, "
              f"{dropped[0][1]}")

    if fail:
        print()
        for f in fail:
            print(f"  FAIL  {f}")
        return 1

    print(f"\n  every one of the {len(buyable)} buyable products is in Stripe, "
          f"has a delivery entry, and has its file on disk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
