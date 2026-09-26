#!/usr/bin/env python3
"""
Prove gate_stripe_orphan_link_active(), added 2026-09-26, does the job its
own docstring claims.

Companion to gate_stripe_link_dedup just above it in preflight.py, and the
other live half of the same 2026-09-26 finding: ensure_link()'s
orphan-adoption loop could tag a retired payment link with a live SKU's
metadata (fixed in stripe_catalog.py, see
test_stripe_catalog_orphan_link_active.py for that half). Once tagged,
find_by_sku() keeps returning the same inactive link forever, so this gate
is the live check for whether any SKU is already stuck that way, from
whatever cause.

Three cases, matching gate_stripe_link_dedup's own established shape: a
missing credential warns (never crashes or FAILs), a clean account is
silent, and a real stuck SKU warns by name.

Run:  python ops/tests/test_gate_stripe_orphan_link_active.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                           # noqa: E402
import stripe_catalog as sc                                     # noqa: E402


def main() -> int:
    fails = []

    # 1. No credential: skus_stuck_on_inactive_link() raises SystemExit deep
    #    inside (via secret_key()). Must warn, never crash or FAIL.
    P.FAIL.clear()
    P.WARN.clear()
    real_fn = sc.skus_stuck_on_inactive_link

    def raise_no_cred():
        raise SystemExit(".env.secrets not found. Nothing to authenticate with.")

    sc.skus_stuck_on_inactive_link = raise_no_cred
    try:
        P.gate_stripe_orphan_link_active()
    except SystemExit:
        fails.append("gate_stripe_orphan_link_active() let SystemExit escape "
                      "instead of catching it")
    finally:
        sc.skus_stuck_on_inactive_link = real_fn

    if P.FAIL:
        fails.append(f"a missing credential produced a FAIL, not a warn: {P.FAIL}")
    if not P.WARN or P.WARN[0][0] != "stripe-orphan-link-active":
        fails.append(f"no stripe-orphan-link-active warning was recorded: {P.WARN}")

    # 2. A clean account (no SKU stuck on an inactive link): silent.
    P.FAIL.clear()
    P.WARN.clear()
    sc.skus_stuck_on_inactive_link = lambda: []
    try:
        P.gate_stripe_orphan_link_active()
    finally:
        sc.skus_stuck_on_inactive_link = real_fn
    if P.FAIL or P.WARN:
        fails.append(f"a clean account still warned or failed: FAIL={P.FAIL} WARN={P.WARN}")

    # 3. A real stuck SKU: warns by name, still no FAIL (this describes the
    #    live Stripe account, not the commit under review).
    P.FAIL.clear()
    P.WARN.clear()
    sc.skus_stuck_on_inactive_link = lambda: ["PACK-HOUSE"]
    try:
        P.gate_stripe_orphan_link_active()
    finally:
        sc.skus_stuck_on_inactive_link = real_fn
    if P.FAIL:
        fails.append(f"a real stuck SKU produced a FAIL, not a warn: {P.FAIL}")
    if not P.WARN or P.WARN[0][0] != "stripe-orphan-link-active" or "PACK-HOUSE" not in P.WARN[0][1]:
        fails.append(f"a real stuck SKU was not named in the warning: {P.WARN}")

    P.FAIL.clear()
    P.WARN.clear()

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("gate_stripe_orphan_link_active(): 3 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
