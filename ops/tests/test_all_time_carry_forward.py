#!/usr/bin/env python3
"""
An unmeasured run must not erase the all-time revenue/sale count.

revenue_all_time and sales_all_time (ops/dashboard.py's _stripe_all_time())
are append-only historical facts, the business's one $19 sale on
2026-08-21 does not stop having happened just because this run has no
Stripe credential. Found live 2026-10-13: running ops/dashboard.py in this
sandbox (no STRIPE_SECRET_KEY) regressed a committed "revenue_all_time":
19.0, "sales_all_time": 1 to null/null, and the printed summary line
changed from "$19 all time from 1 sale(s)" to "all time not measured",
exactly the "a business looks deader than it is" regression
_stripe_all_time()'s own docstring says it exists to prevent, reopened one
layer over because carry_forward_all_time() did not exist yet.

Cannot be run against the real dashboard without a credential, which is
exactly the condition being tested, so the rule lives in a pure function.

Run:  python ops/tests/test_all_time_carry_forward.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

# dashboard.py runs its whole pipeline at import, so the function is lifted
# out of the source rather than imported.
ns = {}
src = open(SRC, encoding="utf-8").read()
m = re.search(r"^def carry_forward_all_time.*?^S\.update", src, re.S | re.M)
exec(m.group(0).rsplit("\n\n", 1)[0], ns)
carry_forward_all_time = ns["carry_forward_all_time"]


def main() -> int:
    fails = []

    # The defect found live: a blind run must keep the previous figure.
    r = carry_forward_all_time(
        {"revenue_all_time": None, "sales_all_time": None},
        {"revenue_all_time": 19.0, "sales_all_time": 1,
         "generated": "2026-10-13 23:31"})
    if r.get("revenue_all_time") != 19.0:
        fails.append(f"an unmeasured run must keep the previous all-time "
                      f"revenue figure, got {r.get('revenue_all_time')!r}")
    if r.get("sales_all_time") != 1:
        fails.append(f"an unmeasured run must keep the previous sale count, "
                      f"got {r.get('sales_all_time')!r}")
    if not r.get("revenue_all_time_carried_from"):
        fails.append("a carried figure must say where it came from")

    # A measured run must not be overwritten and must not claim to be carried.
    r = carry_forward_all_time({"revenue_all_time": 42.0, "sales_all_time": 2,
                                "generated": "2026-10-14 00:00"},
                               {"revenue_all_time": 19.0, "sales_all_time": 1})
    if r.get("revenue_all_time_carried_from") is not None:
        fails.append("a measured run must not claim to be carried")
    if r.get("revenue_all_time_last_measured") != 42.0:
        fails.append("a measured run must record its own figure as the "
                      f"standing answer, got {r!r}")

    # With nothing to carry, ever, stay unmeasured rather than inventing a number.
    r = carry_forward_all_time({"revenue_all_time": None, "sales_all_time": None}, {})
    if r.get("revenue_all_time") is not None:
        fails.append("with nothing to carry, it must stay unmeasured rather "
                      "than inventing a number")

    # Zero is a real measurement (no sales yet) and must carry like any other.
    r = carry_forward_all_time({"revenue_all_time": None, "sales_all_time": None},
                               {"revenue_all_time": 0.0, "sales_all_time": 0,
                                "generated": "2026-08-20 00:00"})
    if r.get("revenue_all_time") != 0.0:
        fails.append(f"zero is a measurement and must carry, got {r!r}")

    # Second consecutive blind run: the first version of carry_forward()
    # (revenue_month) broke exactly here, carrying the previous run's bare
    # field and finding nothing left once that bare field was itself None.
    measured = carry_forward_all_time(
        {"revenue_all_time": 19.0, "sales_all_time": 1,
         "generated": "2026-08-21 10:00"}, {})
    blind1 = carry_forward_all_time({"revenue_all_time": None, "sales_all_time": None},
                                    measured)
    blind2 = carry_forward_all_time({"revenue_all_time": None, "sales_all_time": None},
                                    blind1)
    if blind2.get("revenue_all_time") != 19.0:
        fails.append("a second consecutive blind run must still carry the "
                     f"last measured figure, got {blind2.get('revenue_all_time')}")
    if blind2.get("sales_all_time") != 1:
        fails.append("a second consecutive blind run must still carry the "
                     f"sale count, got {blind2.get('sales_all_time')}")

    # Bootstrap from a committed file written before this fix existed: no
    # "_last_measured" sibling yet, the real figure sits in the plain field.
    r = carry_forward_all_time({"revenue_all_time": None, "sales_all_time": None},
                               {"revenue_all_time": 19.0, "sales_all_time": 1,
                                "generated": "2026-10-13 23:31"})
    if r.get("revenue_all_time") != 19.0 or r.get("sales_all_time") != 1:
        fails.append(f"must bootstrap from a pre-fix file's bare fields, got {r!r}")

    total = 10
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
