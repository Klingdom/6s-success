#!/usr/bin/env python3
"""
What $20,000 a month actually requires, per product, from measured prices.

WHY THIS EXISTS
---------------
The target has been stated many times and never divided by a price. Doing the
division is the whole analysis: it turns "increase revenue" into a specific
number of visitors or a specific number of delivery days, and those two numbers
say different things about which products can carry the goal and which cannot.

Nothing here is forecast. It is arithmetic on the live catalogue and on stated
assumptions, each printed alongside its result so a reader can reject the
assumption rather than the conclusion.

WHAT IS MEASURED AND WHAT IS ASSUMED
------------------------------------
Measured: every price, read from the live catalogue. The checkout conversion
rate, read from Stripe: 1 paid of 7 sessions.

Assumed: the visit to checkout rate. There is no measured value, because the
site had no working analytics for most of its life and has had almost no
traffic since. Industry ecommerce sits near 1 to 3 percent, so the model prints
a range rather than a point, and labels it an assumption everywhere it appears.

Run:  python ops/revenue_model.py
"""
from __future__ import annotations

import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = 20_000.0

# Measured, from Stripe on 2026-08-23: 7 checkout sessions ever, 1 paid.
# n=7 is far too small to be a rate. It is carried because it is the only
# observed number of its kind, and it is labelled everywhere it is used.
CHECKOUT_PAID, CHECKOUT_TOTAL = 1, 7

# Assumed, not measured. The band ordinary ecommerce sites live in.
VISIT_TO_CHECKOUT = (0.01, 0.03)

# Hours of a person's time each sale consumes after the money arrives. Digital
# is zero: the file is already built and delivery is automated. Services are
# not, and that is the constraint that decides whether a service can scale.
DELIVERY_HOURS = {
    "CN-VIRTUAL": 2.0,     # 90 minutes plus the written standard afterwards
    "CN-INHOME": 9.0,      # a full day on site, plus travel
}

WORKING_HOURS_PER_MONTH = 160.0


def catalogue() -> list[dict]:
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    return json.loads(js[js.index("["):js.rindex("]") + 1])


def main() -> int:
    cat = [p for p in catalogue() if p.get("buy") and p.get("price")]
    cat.sort(key=lambda p: p["price"])

    lo, hi = VISIT_TO_CHECKOUT
    ck = CHECKOUT_PAID / CHECKOUT_TOTAL

    print(f"  Target ${TARGET:,.0f} a month. Every price below is read from the "
          "live catalogue.\n")
    print(f"  {'Product':40} {'Price':>7} {'Orders/mo':>10} {'Visits/mo, assumed':>20} {'Your hours':>11}")
    print(f"  {'-'*40} {'-'*7} {'-'*10} {'-'*20} {'-'*11}")

    # At a fixed target, every product at the same price needs the same
    # order count, so a plain per-product loop repeats the identical row
    # once per SKU. That was fine when this catalogue had a handful of
    # priced items; it produced 155 rows, 109 of them byte-identical $4
    # zone-pack lines, once 5.7 wired the full catalogue live on 2026-08-27.
    # Group by price instead, so the table stays exactly the size of the
    # number of decisions it actually contains.
    by_price: dict[float, list[dict]] = {}
    for p in cat:
        by_price.setdefault(p["price"], []).append(p)

    for price in sorted(by_price):
        group = by_price[price]
        orders = TARGET / price
        # visits -> checkout -> paid. The checkout step is the measured 1 in 7.
        v_hi = orders / (lo * ck)
        v_lo = orders / (hi * ck)
        per_order_hrs = {DELIVERY_HOURS.get(p["sku"], 0.0) for p in group}
        hrs = (per_order_hrs.pop() if len(per_order_hrs) == 1 else max(per_order_hrs)) * orders
        hr_s = "none" if hrs == 0 else f"{hrs:,.0f}"
        flag = "" if hrs <= WORKING_HOURS_PER_MONTH else "  IMPOSSIBLE"
        name = group[0]["name"][:39] if len(group) == 1 else f"{len(group)} products at this price"[:39]
        print(f"  {name:40} ${price:>6,.0f} {orders:>10,.0f} "
              f"{v_lo:>9,.0f} to {v_hi:>7,.0f} {hr_s:>11}{flag}")

    print(f"\n  Checkout conversion used: {CHECKOUT_PAID} of {CHECKOUT_TOTAL} "
          f"= {ck:.0%}. MEASURED, but n=7, so treat as a placeholder.")
    print(f"  Visit to checkout used: {lo:.0%} to {hi:.0%}. ASSUMED. "
          "No measured value exists.")
    print(f"  A month of one person's working time: {WORKING_HOURS_PER_MONTH:,.0f} hours.")

    # The comparison that matters: what a mixed month costs in traffic.
    print("\n  MIXED MONTHS, and what each needs arriving at the site:\n")
    mixes = [
        ("Digital only, at the blended digital price",
         [("PACK-HOUSE", None)]),
        ("Digital, plus 4 virtual consults a month",
         [("CN-VIRTUAL", 4), ("PACK-HOUSE", None)]),
        ("Digital, plus 4 consults and 8 in-home days",
         [("CN-VIRTUAL", 4), ("CN-INHOME", 8), ("PACK-HOUSE", None)]),
        ("Digital, plus 4 consults and 14 in-home days",
         [("CN-VIRTUAL", 4), ("CN-INHOME", 14), ("PACK-HOUSE", None)]),
    ]
    by_sku = {p["sku"]: p for p in cat}
    for label, parts in mixes:
        fixed = sum(by_sku[s]["price"] * n for s, n in parts if n)
        hrs = sum(DELIVERY_HOURS.get(s, 0) * n for s, n in parts if n)
        filler = next(s for s, n in parts if n is None)
        rest = max(0.0, TARGET - fixed)
        units = rest / by_sku[filler]["price"]
        v_hi = units / (lo * ck)
        v_lo = units / (hi * ck)
        over = "  OVER CAPACITY" if hrs > WORKING_HOURS_PER_MONTH else ""
        print(f"  {label}")
        print(f"    services ${fixed:>8,.0f}  your hours {hrs:>5,.0f}{over}")
        print(f"    leaves   ${rest:>8,.0f} to find in ${by_sku[filler]['price']:.0f} sales "
              f"= {units:,.0f} orders")
        print(f"    visitors needed, assumed rates: {v_lo:,.0f} to {v_hi:,.0f} a month\n")

    print("  Read the visitor column, not the revenue column. The revenue column\n"
          "  is arithmetic and always works. The visitor column is the business.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
