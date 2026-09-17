#!/usr/bin/env python3
"""
Prove gate_no_duplicate_stripe_product_names() catches a real name collision
and stays clean on the real catalogue, no Stripe credential involved either
way.

REVIEW-QA-2026-09-07.md found six live $4 zone packs sharing a bare Stripe
name ("Dresser Drawers Pack" on both Primary and Kids Bedroom, "Shower or Tub
Pack" and "Toilet Area Pack" each the same way across Primary and Guest
Bathroom), the room qualifier dropped from the exact text a buyer scans at
checkout. Its own acceptance criterion: "No two live Stripe products share a
name. A gate can assert this from the catalogue with no Stripe credential."
This is that gate; unlike its Stripe-account siblings, it needs no network
and no key, so it FAILs rather than warns.

Run:  python ops/tests/test_gate_no_duplicate_stripe_product_names.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402
import stripe_catalog as sc                                    # noqa: E402


def main() -> int:
    fails = []

    # Case 1: product_name() appends the variant exactly like ensure_product() did.
    named = sc.product_name({"name": "Dresser Drawers Pack, Primary Bedroom",
                              "variant": "6 cards, print at home"})
    if named != "Dresser Drawers Pack, Primary Bedroom (6 cards, print at home)":
        fails.append(f"product_name() built an unexpected string: {named!r}")

    # Case 2: no variant, name passes through unchanged.
    bare = sc.product_name({"name": "Corporate Lean 6S"})
    if bare != "Corporate Lean 6S":
        fails.append(f"product_name() changed a name with no variant: {bare!r}")

    # Case 3: duplicate_product_names() finds the real regression shape:
    # two SKUs whose catalogue name never got the room qualifier added.
    collision_cat = {
        "ZP-PRIMAR-DRESSER": {"name": "Dresser Drawers Pack",
                               "variant": "6 cards, print at home"},
        "ZP-KIDS-B-DRESSER": {"name": "Dresser Drawers Pack",
                               "variant": "6 cards, print at home"},
        "PACK-HOUSE": {"name": "The Whole House Print Pack",
                        "variant": "684 cards, print at home"},
    }
    dupes = sc.duplicate_product_names(collision_cat)
    if set(dupes.keys()) != {"Dresser Drawers Pack (6 cards, print at home)"}:
        fails.append(f"duplicate_product_names() missed or over-reported the "
                      f"planted collision: {dupes}")
    elif sorted(dupes["Dresser Drawers Pack (6 cards, print at home)"]) != \
            ["ZP-KIDS-B-DRESSER", "ZP-PRIMAR-DRESSER"]:
        fails.append(f"duplicate_product_names() named the wrong SKUs: {dupes}")

    # Case 4: the same collision fails the real gate.
    P.FAIL.clear()
    P.WARN.clear()
    real_dupe_fn = sc.duplicate_product_names
    sc.duplicate_product_names = lambda: {
        "Dresser Drawers Pack (6 cards, print at home)":
            ["ZP-KIDS-B-DRESSER", "ZP-PRIMAR-DRESSER"]}
    try:
        P.gate_no_duplicate_stripe_product_names()
    finally:
        sc.duplicate_product_names = real_dupe_fn
    if not P.FAIL or P.FAIL[0][0] != "dup-stripe-names":
        fails.append(f"a planted name collision did not fail the gate: "
                      f"FAIL={P.FAIL} WARN={P.WARN}")

    # Case 5: the real, committed catalogue has zero collisions today.
    P.FAIL.clear()
    P.WARN.clear()
    P.gate_no_duplicate_stripe_product_names()
    if P.FAIL:
        fails.append(f"the real committed catalogue reports a name "
                      f"collision: {P.FAIL}")

    for f in fails:
        print(f"  FAIL  {f}")
    n = 5
    print(f"  {n - len(fails)} of {n} cases pass" if fails
          else f"  {n} of {n} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
