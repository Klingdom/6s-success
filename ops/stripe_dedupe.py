#!/usr/bin/env python3
"""
Collapse duplicate Stripe products down to one per SKU.

WHY THEY EXIST
--------------
ops/stripe_catalog.py looked up existing objects with a single unpaginated
call that took the first hundred as the whole account. Once the catalogue
passed a hundred SKUs, the idempotency check stopped finding things that
already existed, so a second --apply created a second Product, a second Price
and a second Payment Link for every SKU.

The duplicate links were cleaned up when they were found. The duplicate
products were not, and they cause a subtler failure: find_by_sku returns
product A while the live payment link sells a price belonging to product B.
Every run then decides the link charges an unrecognised price and replaces
it, so nothing is ever idempotent and the site's buy links change on every
run, going dead in between.

WHAT THIS KEEPS
---------------
For each SKU, the product whose active price matches the catalogue price. If
several qualify, the oldest, because it is the one with any purchase history
attached. Everything else is archived.

ARCHIVED, NOT DELETED. Stripe keeps archived products and they can be
restored. Deleting a product with a payment history is not something to do to
recover from a pagination bug.

Run:  python ops/stripe_dedupe.py --check
      STRIPE_ALLOW_LIVE=1 python ops/stripe_dedupe.py --apply
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_catalog as sc                                    # noqa: E402


def catalogue_prices() -> dict:
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    arr = json.loads(js[js.index("["):js.rindex("]") + 1])
    return {i["sku"]: int(round((i.get("price") or 0) * 100)) for i in arr}


def duplicates() -> dict:
    """SKUs with more than one ACTIVE product, as {sku: [products]}.

    Extracted so preflight can ask the question without running the fix or
    printing anything. Raises rather than returning {} when Stripe cannot be
    reached, because an empty dict means "checked, none found" and a caller
    that cannot tell those apart will report a clean account it never read.
    """
    by = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            by.setdefault(s, []).append(p)
    if not by:
        raise RuntimeError("no active products with a sku came back from "
                           "Stripe, which is not a believable account state")
    return {k: v for k, v in by.items() if len(v) > 1}


def main(apply_it: bool) -> int:
    if apply_it and sc.live() and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        sys.exit("Refusing to write to a LIVE account without STRIPE_ALLOW_LIVE=1")

    want = catalogue_prices()
    by = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            by.setdefault(s, []).append(p)

    dupes = {k: v for k, v in by.items() if len(v) > 1}
    print(f"  {sum(len(v) for v in by.values())} active products across "
          f"{len(by)} skus, {len(dupes)} duplicated")
    if not dupes:
        print("  nothing to do")
        return 0

    archived = 0
    for sku, prods in sorted(dupes.items()):
        target = want.get(sku)
        scored = []
        for p in prods:
            prices = [x for x in sc.list_all("prices", {"product": p["id"]})
                      if x.get("active")]
            match = any(x["unit_amount"] == target for x in prices) if target else False
            scored.append((not match, p.get("created") or 0, p["id"], p))

        # A product carrying the right price wins. Among equals the oldest,
        # because it is the one any purchase history hangs off.
        scored.sort()
        keep = scored[0][3]
        drop = [x[3] for x in scored[1:]]

        if not apply_it:
            print(f"  {sku:24} keep {keep['id'][-8:]}, "
                  f"archive {[d['id'][-8:] for d in drop]}")
            continue

        for d in drop:
            sc.call("POST", f"products/{d['id']}", {"active": "false"})
            archived += 1
    sc.invalidate("products")

    if not apply_it:
        print("\n  --check only, nothing written. Re-run with --apply.")
        return 0

    print(f"  archived {archived} duplicate products")

    left = {}
    for p in sc.list_all("products"):
        s = (p.get("metadata") or {}).get("sku")
        if s and p.get("active"):
            left.setdefault(s, []).append(p)
    still = {k: v for k, v in left.items() if len(v) > 1}
    assert not still, f"still duplicated after the pass: {list(still)[:4]}"
    print(f"  every sku now resolves to exactly one active product")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
