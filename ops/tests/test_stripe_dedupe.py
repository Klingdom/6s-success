#!/usr/bin/env python3
"""
Prove stripe_dedupe.py's main() cannot report a clean account it never read.

Found 2026-09-18, PM cold-read of the money-domain ops/*.py tier.
duplicates() already raises when Stripe returns zero active products with a
sku, per its own docstring: "an empty dict means 'checked, none found' and a
caller that cannot tell those apart will report a clean account it never
read." main(), the --check/--apply CLI entry point, rebuilt the same
product-scanning loop inline without that guard, so the exact failure
duplicates() exists to catch (an unreachable or misbehaving account coming
back with nothing) printed "0 active products across 0 skus, 0 duplicated /
nothing to do" instead of surfacing as unchecked. Fixed by adding the same
raise to main()'s own loop.

Run:  python ops/tests/test_stripe_dedupe.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_dedupe as sd                                    # noqa: E402


def product(pid, sku, price_cents, active=True, created=0):
    return {"id": pid, "active": active, "created": created,
            "metadata": {"sku": sku}, "_price": price_cents}


def main() -> int:
    fails = []
    orig_live, orig_list_all, orig_call, orig_invalidate = (
        sd.sc.live, sd.sc.list_all, sd.sc.call, sd.sc.invalidate)

    def prices_for(pid, catalog):
        p = next(x for x in catalog if x["id"] == pid)
        return [{"id": "price_" + pid, "active": True,
                  "unit_amount": p["_price"]}]

    def fake_list_all_factory(products):
        def fake_list_all(kind, params=None):
            if kind == "products":
                return products
            if kind == "prices":
                pid = (params or {}).get("product")
                return prices_for(pid, products)
            raise AssertionError(f"unexpected kind: {kind}")
        return fake_list_all

    # Case 1: Stripe returns zero active products with a sku. This must not
    # look like a clean, deduplicated account; it must raise.
    sd.sc.live = lambda: False
    sd.sc.list_all = fake_list_all_factory([])
    try:
        sd.main(False)
    except RuntimeError:
        pass
    except SystemExit as e:
        fails.append(f"empty account raised SystemExit, not RuntimeError: {e}")
    else:
        fails.append("empty account returned normally instead of raising; "
                      "an unreachable/misbehaving account would report clean")

    # Case 2: one active product per sku, no duplicates: must report clean
    # for real, not raise.
    single = [product("prod_a", "BK-EB", 999, created=1)]
    sd.sc.list_all = fake_list_all_factory(single)
    try:
        rc = sd.main(False)
    except Exception as e:
        fails.append(f"single-product account raised unexpectedly: {e}")
    else:
        if rc != 0:
            fails.append(f"single-product --check returned {rc}, expected 0")

    # Case 3: a real duplicate, --check only, must not write and must pick
    # the product whose active price matches the catalogue, not merely the
    # oldest.
    want = sd.catalogue_prices()
    real_sku, real_price = next(iter(want.items()))
    dupes = [
        product("prod_old_wrong_price", real_sku, real_price + 100, created=1),
        product("prod_new_right_price", real_sku, real_price, created=2),
    ]
    sd.sc.list_all = fake_list_all_factory(dupes)
    calls = []
    sd.sc.call = lambda method, path, data=None: calls.append((method, path)) or {}
    sd.sc.invalidate = lambda kind: None
    try:
        rc = sd.main(False)
    except Exception as e:
        fails.append(f"--check on a real duplicate raised unexpectedly: {e}")
    else:
        if rc != 0:
            fails.append(f"--check on a real duplicate returned {rc}, expected 0")
        if calls:
            fails.append(f"--check made write call(s): {calls}")

    sd.sc.live, sd.sc.list_all, sd.sc.call, sd.sc.invalidate = (
        orig_live, orig_list_all, orig_call, orig_invalidate)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_dedupe.py empty-account guard: 3 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
