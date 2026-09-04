#!/usr/bin/env python3
"""What a digital sale on Etsy is actually worth, once you know the fees.

WHY THIS TAKES THE RATES AS ARGUMENTS INSTEAD OF HARDCODING THEM
----------------------------------------------------------------
Etsy blocks automated access. Every request to etsy.com/legal/fees and to the
seller pages of help.etsy.com returned HTTP 403 on 2026-09-03, so no fee number
in this repository has been verified against Etsy today. Etsy has changed both
the listing fee and the payment processing schedule more than once, and the
processing rate varies by the seller's country. A number recalled from memory
and printed next to a dollar sign looks exactly like a measured one, which is
how a business ends up pricing against a rate that no longer exists.

So this asks for the rates. Read them off the fee page while you are signed in
to the seller account, pass them in, and the arithmetic is then yours rather
than a guess.

  python build/listings/etsy_economics.py \
      --listing-fee 0.20 --transaction-pct 6.5 \
      --processing-pct 3.0 --processing-fixed 0.25

Add --offsite-pct if the shop is enrolled in Offsite Ads and cannot opt out,
because that fee applies only to orders that came through an Etsy-purchased ad
and it changes the picture on the flagship listing more than on the cheap ones.
"""
from __future__ import annotations

import argparse
import sys

# The day-one listings, from MARKETPLACE-LISTINGS.md.
LISTINGS = [
    ("L1  Whole House Print Pack", 22.00),
    ("L2  Kitchen Pack", 10.00),
    ("L3  Entryway Pack", 10.00),
    ("L4  Moving In Kit", 16.00),
    ("L5  Holiday Hosting Kit", 16.00),
]

# What the same product nets through the site's own Stripe checkout, so the
# two channels can be compared rather than guessed at. Stripe's published US
# card rate is 2.9% + $0.30; that rate is not verified here either, but it is
# the one ops/build_catalog.py already reasons with.
DIRECT_PRICE = {
    "L1  Whole House Print Pack": 19.00,
    "L2  Kitchen Pack": 9.00,
    "L3  Entryway Pack": 9.00,
    "L4  Moving In Kit": 14.00,
    "L5  Holiday Hosting Kit": 14.00,
}
STRIPE_PCT = 2.9
STRIPE_FIXED = 0.30


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--listing-fee", type=float, required=True,
                    help="USD charged to publish one listing, and again each "
                         "time it renews")
    ap.add_argument("--transaction-pct", type=float, required=True,
                    help="percent of item price plus shipping")
    ap.add_argument("--processing-pct", type=float, required=True,
                    help="Etsy Payments percent, varies by seller country")
    ap.add_argument("--processing-fixed", type=float, required=True,
                    help="Etsy Payments fixed component per order, USD")
    ap.add_argument("--offsite-pct", type=float, default=0.0,
                    help="Offsite Ads percent, charged only on orders "
                         "attributed to an Etsy-bought ad")
    ap.add_argument("--renewals-per-year", type=int, default=3,
                    help="a listing that never sells renews on a fixed cycle; "
                         "confirm the cycle length on the fee page")
    args = ap.parse_args()

    print("Rates used, as supplied on the command line. Nothing here was "
          "fetched from Etsy.")
    print("  listing fee        $%.2f per publish and per renewal" % args.listing_fee)
    print("  transaction fee    %.2f%% of item price" % args.transaction_pct)
    print("  payment processing %.2f%% + $%.2f per order" %
          (args.processing_pct, args.processing_fixed))
    if args.offsite_pct:
        print("  offsite ads        %.2f%% on attributed orders only" % args.offsite_pct)
    print("")

    head = ("listing".ljust(28) + "price".rjust(8) + "fees".rjust(9)
            + "net".rjust(9) + "  take" + "direct net".rjust(12))
    if args.offsite_pct:
        head += "with ads".rjust(11)
    print(head)
    total_net = 0.0
    for name, price in LISTINGS:
        fees = (args.listing_fee
                + price * args.transaction_pct / 100
                + price * args.processing_pct / 100
                + args.processing_fixed)
        net = price - fees
        total_net += net
        direct = DIRECT_PRICE[name]
        direct_net = direct - (direct * STRIPE_PCT / 100 + STRIPE_FIXED)
        line = (name.ljust(28) + ("$%.2f" % price).rjust(8)
                + ("$%.2f" % fees).rjust(9) + ("$%.2f" % net).rjust(9)
                + ("  %.0f%%" % (fees / price * 100)).rjust(7)
                + ("$%.2f" % direct_net).rjust(12))
        if args.offsite_pct:
            line += ("$%.2f" % (net - price * args.offsite_pct / 100)).rjust(11)
        print(line)

    carry = args.listing_fee * len(LISTINGS) * args.renewals_per_year
    print("")
    print("The prices above are set by one rule: charge enough on Etsy that "
          "the money left after Etsy's cut is not less than the money left "
          "after Stripe's cut on the site. That keeps the site the cheaper "
          "place to buy, which is where we would rather the customer be, "
          "without making the marketplace unprofitable.")
    print("Standing cost of keeping these %d listings up for a year with no "
          "sales at all: $%.2f" % (len(LISTINGS), carry))
    print("Sales needed in a year just to cover that, at the average net of "
          "$%.2f: %.1f" % (total_net / len(LISTINGS),
                           carry / (total_net / len(LISTINGS))))
    print("")
    print("Not included, because they are not Etsy fees and not measured: "
          "income tax, the sales tax Etsy collects and remits on the buyer's "
          "behalf, currency conversion on non-USD orders, and the cost of "
          "Phil's time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
