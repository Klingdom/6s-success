#!/usr/bin/env python3
"""
Prove gate_stripe_link_dedup(), added 2026-09-26, does the job its own
docstring claims.

gate_stripe_one_product_per_sku (a few lines above it in preflight.py) only
ever checked duplicate Stripe PRODUCTS. stripe_dedupe.py's own module
docstring names a second, quieter failure mode found the same day
(2026-09-23): five SKUs each had two active PAYMENT LINKS, and
dedupe_links()'s own docstring explains why that is dangerous the moment a
price changes, not today. That gap sat ungated until this cycle, even
though the fix (stripe_dedupe.py's dedupe_links()) already existed.

Three cases, matching gate_stripe_one_product_per_sku's own established
shape exactly: a missing credential warns (does not crash or FAIL), a clean
account is silent, and a real duplicate warns by name.

Run:  python ops/tests/test_gate_stripe_link_dedup.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402
import stripe_dedupe as sd                                     # noqa: E402


def main() -> int:
    fails = []

    # 1. No credential: stripe_catalog.secret_key() raises SystemExit, not
    #    Exception (the exact shape gate_stripe_price_claims once missed).
    #    Must warn, never crash or FAIL.
    P.FAIL.clear()
    P.WARN.clear()
    real_import = __import__

    def fake_import(name, *a, **kw):
        if name == "stripe_catalog":
            raise SystemExit(".env.secrets not found. Nothing to authenticate with.")
        return real_import(name, *a, **kw)

    import builtins
    real_builtin = builtins.__import__
    builtins.__import__ = fake_import
    try:
        P.gate_stripe_link_dedup()
    except SystemExit:
        fails.append("gate_stripe_link_dedup() let SystemExit escape instead "
                      "of catching it")
    finally:
        builtins.__import__ = real_builtin

    if P.FAIL:
        fails.append(f"a missing credential produced a FAIL, not a warn: {P.FAIL}")
    if not P.WARN or P.WARN[0][0] != "stripe-link-dedup":
        fails.append(f"no stripe-link-dedup warning was recorded: {P.WARN}")

    # 2. A clean account (no SKU has more than one active link): silent.
    P.FAIL.clear()
    P.WARN.clear()
    real_dupe = sd.duplicate_active_links
    sd.duplicate_active_links = lambda: {}
    try:
        P.gate_stripe_link_dedup()
    finally:
        sd.duplicate_active_links = real_dupe
    if P.FAIL or P.WARN:
        fails.append(f"a clean account still warned or failed: FAIL={P.FAIL} WARN={P.WARN}")

    # 3. A real duplicate: warns by name, still no FAIL (this describes the
    #    live Stripe account, not the commit under review).
    P.FAIL.clear()
    P.WARN.clear()
    real_dupe = sd.duplicate_active_links
    sd.duplicate_active_links = lambda: {"PACK-HOUSE": [{}, {}]}
    try:
        P.gate_stripe_link_dedup()
    finally:
        sd.duplicate_active_links = real_dupe
    if P.FAIL:
        fails.append(f"a real duplicate link produced a FAIL, not a warn: {P.FAIL}")
    if not P.WARN or P.WARN[0][0] != "stripe-link-dedup" or "PACK-HOUSE" not in P.WARN[0][1]:
        fails.append(f"a real duplicate link was not named in the warning: {P.WARN}")

    P.FAIL.clear()
    P.WARN.clear()

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("gate_stripe_link_dedup(): 3 case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
