#!/usr/bin/env python3
"""
Prove check_etsy.py's stale_economics_entries() catches
build/listings/etsy_economics.py drifting from the real listing package and
the real site catalogue.

Found and fixed 2026-09-27, this operator, cold-reading DECISIONS.md D-023,
which had already flagged the second defect below and left it open ("if Etsy
goes live before the underlying kit content is either restored or re-priced
independently of the site"). Two live instances existed at once:

1. etsy_economics.py's own LISTINGS table still priced "L2  Kitchen Pack"
   three days after L2 was withdrawn from etsy-listings.json and its files
   removed (DECISIONS.md D-024, 2026-09-23): running the script would price
   a listing that no longer exists.
2. etsy_economics.py's own DIRECT_PRICE table still priced "L4  Moving In
   Kit" and "L5  Holiday Hosting Kit" against a $14 site checkout, five days
   after DECISIONS.md D-023 (2026-09-22) retired their source SKUs
   (KIT-MOVING-IN, KIT-HOLIDAY-HOST) from the site's own paid catalogue and
   archived the matching Stripe payment links: there is no longer a $14
   direct alternative to compare against, or any direct alternative at all.

Neither listing is a free duplicate (the check free_duplicate_skus() already
covers), so this is a distinct defect class: a hardcoded economics table that
was never re-derived after the source it depends on changed, exactly the
"source corrected, artifact never re-derived" shape BACKLOG-2026-09-07.md
section 7 names as dominant here.

This test proves both real, pre-fix shapes fail by name, a live SKU (L1 /
PACK-HOUSE) is never flagged, and the real committed files (post-fix) are
clean. It does not touch the real etsy_economics.py module state longer than
one case: every stub is saved and restored.

Run:  python ops/tests/test_check_etsy_stale_economics.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LISTINGS_DIR = os.path.join(ROOT, "build", "listings")
sys.path.insert(0, os.path.join(ROOT, "ops"))
sys.path.insert(0, LISTINGS_DIR)

import check_etsy                                              # noqa: E402
import etsy_economics as ee                                     # noqa: E402


REAL_LISTINGS = [
    {"slug": "L1-whole-house", "source_sku": "PACK-HOUSE"},
    {"slug": "L4-moving-in", "source_sku": "KIT-MOVING-IN"},
    {"slug": "L5-holiday-hosting", "source_sku": "KIT-HOLIDAY-HOST"},
]


def with_stub(listings_table, direct_price_table, fn):
    """Run fn() with etsy_economics.LISTINGS/DIRECT_PRICE swapped out, then
    restore them unconditionally, even if fn() raises."""
    old_listings, old_direct = ee.LISTINGS, ee.DIRECT_PRICE
    try:
        ee.LISTINGS = listings_table
        ee.DIRECT_PRICE = direct_price_table
        return fn()
    finally:
        ee.LISTINGS = old_listings
        ee.DIRECT_PRICE = old_direct


def main() -> int:
    fails = []

    # 1. The withdrawn-listing shape: LISTINGS names a listing not present in
    #    the current package at all (L2, withdrawn 2026-09-23).
    problems = with_stub(
        [("L1  Whole House Print Pack", 22.00), ("L2  Kitchen Pack", 10.00)],
        {"L1  Whole House Print Pack": 19.00},
        lambda: check_etsy.stale_economics_entries(REAL_LISTINGS))
    if not any("L2" in p and "Kitchen Pack" in p for p in problems):
        fails.append("a LISTINGS entry for a withdrawn listing (L2) was not "
                     "flagged: %r" % (problems,))

    # 2. The retired-source-SKU shape: DIRECT_PRICE prices a listing whose
    #    real source_sku is retired from the site's own catalogue (L4 /
    #    KIT-MOVING-IN, D-023).
    problems = with_stub(
        [("L1  Whole House Print Pack", 22.00), ("L4  Moving In Kit", 16.00)],
        {"L1  Whole House Print Pack": 19.00, "L4  Moving In Kit": 14.00},
        lambda: check_etsy.stale_economics_entries(REAL_LISTINGS))
    if not any("L4" in p and "Moving In Kit" in p and "KIT-MOVING-IN" in p
               for p in problems):
        fails.append("a DIRECT_PRICE entry for a retired source SKU "
                     "(KIT-MOVING-IN) was not flagged: %r" % (problems,))

    # 3. A DIRECT_PRICE entry for a listing whose source SKU is genuinely
    #    still live and sold on the site (L1 / PACK-HOUSE) must never be
    #    flagged: this is the one legitimate comparison the tables should
    #    keep making.
    problems = with_stub(
        [("L1  Whole House Print Pack", 22.00)],
        {"L1  Whole House Print Pack": 19.00},
        lambda: check_etsy.stale_economics_entries(REAL_LISTINGS))
    if problems:
        fails.append("a live, correctly-priced direct comparison (L1 / "
                     "PACK-HOUSE) was flagged: %r" % (problems,))

    # 4. main() itself must turn a stale_economics_entries() finding into a
    #    FAIL line, not just a returned list nobody reads.
    old_see = check_etsy.stale_economics_entries
    try:
        check_etsy.stale_economics_entries = lambda listings: [
            "synthetic stale-economics finding"]
        rc = check_etsy.main()
        if rc == 0 or not any("synthetic stale-economics finding" in f
                              for f in check_etsy.fail):
            fails.append("main() did not fail-by-name on a stale-economics "
                         "finding: rc=%r fail=%r" % (rc, check_etsy.fail))
    finally:
        check_etsy.stale_economics_entries = old_see
        check_etsy.ok.clear()
        check_etsy.fail.clear()
        check_etsy.unchecked.clear()

    # 5. The real, committed files today: clean, no stubbing at all.
    rc = check_etsy.main()
    if rc != 0:
        fails.append("the real, committed Etsy package fails: %r"
                     % (check_etsy.fail,))
    check_etsy.ok.clear()
    check_etsy.fail.clear()
    check_etsy.unchecked.clear()

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: check_etsy stale-economics check, 5/5 cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
