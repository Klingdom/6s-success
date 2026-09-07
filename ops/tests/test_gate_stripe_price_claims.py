#!/usr/bin/env python3
"""
Prove gate_stripe_price_claims() warns rather than crashes when no Stripe
credential exists, found 2026-09-07 in the same merge that added it.

stripe_catalog.py's secret_key() reports a missing credential with
sys.exit(), which raises SystemExit, not Exception. The gate's own
try/except caught only Exception, so the exact case its own docstring says
it "warns rather than fails" on ("no credential reports UNCHECKED rather
than clean") instead crashed to a hard FAIL in this sandbox, which has no
credential in every run. gate_stripe_one_product_per_sku, a few lines
below it in the same file, already names this shape in its own docstring
and catches (Exception, SystemExit); this gate simply missed the pattern.

Run:  python ops/tests/test_gate_stripe_price_claims.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402


def main() -> int:
    fails = []

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
        P.gate_stripe_price_claims()
    except SystemExit:
        fails.append("gate_stripe_price_claims() let SystemExit escape "
                      "instead of catching it, exactly the regression this "
                      "test exists for")
    finally:
        builtins.__import__ = real_builtin

    if not fails:
        if P.FAIL:
            fails.append(f"a missing credential produced a FAIL, not a "
                          f"warn: {P.FAIL}")
        if not P.WARN or P.WARN[0][0] != "stripe-price-claims":
            fails.append(f"no stripe-price-claims warning was recorded: {P.WARN}")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {1 - len(fails)} of 1 case pass" if len(fails) <= 1
          else f"  0 of 1 case pass ({len(fails)} problems)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
