#!/usr/bin/env python3
"""
Prove check_etsy.py's free_duplicate_skus() catches a listing that sells
content the site's own catalogue already excludes as free elsewhere.

Found and fixed 2026-09-09, this operator. L3-entryway was written, priced,
rendered and readied (build/listings/etsy/L3-entryway/), one owner action
(OWNER-ACTIONS.md item 15) away from a real Etsy shop. Its source file,
build/products/RP-ENTRYWAY.html, is the exact SKU ops/generated_products.py
already excludes from the site's own Stripe catalogue, with its own stated
reason: "the free Entryway deck already covers... a four dollar pack of the
same cards is not gating free content, but it is selling somebody a strictly
worse version of something they could have for nothing, and a customer who
found out afterwards would be right to be angry." Nothing had ever connected
that reasoning to the Etsy pipeline, a completely separate script
(build/listings/build_etsy_assets.py) that picked its five source files by
hand. Withdrawn the same day this was found: L3-entryway removed from
build/listings/etsy-listings.json, and every remaining listing there now
carries an explicit source_sku field so this check depends only on that
file, never on build_etsy_assets.py's own render table (which only runs on
Phil's own machine and could be edited, or left stale, independently).

This test proves two things: the real, pre-fix shape (a free-duplicate
listing present) fails by name, and the real, committed package (post-fix,
four listings) is clean. It does not touch the real etsy-listings.json; it
builds a synthetic listings list instead, so it does not depend on which
listings happen to exist on a given day.

Run:  python ops/tests/test_check_etsy_free_duplicate.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LISTINGS_DIR = os.path.join(ROOT, "build", "listings")
sys.path.insert(0, os.path.join(ROOT, "ops"))
sys.path.insert(0, LISTINGS_DIR)

import check_etsy                                              # noqa: E402


def main() -> int:
    fails = []

    # 1. The real regression shape: a listing whose source_sku is one
    #    ops/generated_products.py has dropped as free. RP-ENTRYWAY is
    #    dropped today (the free Entryway deck), so a listing naming it must
    #    fail, by name, whether or not L3-entryway itself is still in the
    #    real file.
    dup = check_etsy.free_duplicate_skus(
        [{"slug": "L3-entryway", "source_sku": "RP-ENTRYWAY"}])
    if not dup:
        fails.append("a listing sourced from RP-ENTRYWAY (dropped as free by "
                     "ops/generated_products.py) was not flagged at all: %r"
                     % (dup,))
    elif dup.get("L3-entryway") != {"RP-ENTRYWAY"}:
        fails.append("wrong SKU set flagged for L3-entryway: %r" % (dup,))

    # 2. A listing not present in the input list must never appear in the
    #    result, even if its underlying SKU is free-dropped: the function
    #    reports only on listings actually asked about.
    dup_absent = check_etsy.free_duplicate_skus(
        [{"slug": "L2-kitchen", "source_sku": "RP-KITCHEN"}])
    if "L3-entryway" in dup_absent:
        fails.append("a listing that was not asked about was reported anyway: "
                     "%r" % (dup_absent,))

    # 3. A listing whose SKU is honest to sell (not in the dropped-as-free
    #    set) must never be flagged. RP-KITCHEN is sold directly on the site,
    #    so L2-kitchen must come back clean.
    if dup_absent:
        fails.append("L2-kitchen, an honestly-sellable listing, was flagged: "
                     "%r" % (dup_absent,))

    # 3b. A listing with no source_sku at all (L1's bundle files do not map
    #     to a single per-zone SKU the same way) must never crash or be
    #     flagged.
    dup_none = check_etsy.free_duplicate_skus([{"slug": "L1-whole-house"}])
    if dup_none:
        fails.append("a listing with no source_sku was flagged: %r"
                     % (dup_none,))

    # 4. main() itself must turn a free-duplicate finding into a FAIL line
    #    naming the slug and the SKU, not just a returned dict nobody reads.
    #    Stub free_duplicate_skus() directly (never the shared json module,
    #    which build_catalog.py also imports and would silently break) so
    #    this exercises exactly the integration point: main() reporting
    #    whatever the real function found.
    old_fds = check_etsy.free_duplicate_skus
    try:
        check_etsy.free_duplicate_skus = lambda listings: {
            "L3-entryway": {"RP-ENTRYWAY"}}
        rc = check_etsy.main()
        if rc == 0 or not any("RP-ENTRYWAY" in f for f in check_etsy.fail):
            fails.append("main() did not fail-by-name on a free-duplicate "
                         "listing: rc=%r fail=%r" % (rc, check_etsy.fail))
    finally:
        check_etsy.free_duplicate_skus = old_fds
        check_etsy.ok.clear()
        check_etsy.fail.clear()
        check_etsy.unchecked.clear()

    # 5. The real, committed package today: clean, no stubbing at all.
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
    print("OK: check_etsy free-duplicate check, 6/6 cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
