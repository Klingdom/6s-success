#!/usr/bin/env python3
"""
An unmeasured run must not erase a measured figure.

Two agents regenerate the dashboard and only one can reach the network. The
cloud operator's sandbox has no Stripe credential, so its run honestly reports
"not measured", and committing that overwrote a figure the laptop had measured
an hour earlier. The committed dashboard alternated between $19 and "not
measured" every cycle, which reads as the business losing its revenue and
getting it back.

These cannot be run against the real dashboard without a credential, which is
exactly the condition being tested, so the rule lives in a pure function.

Run:  python ops/tests/test_carry_forward.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

# dashboard.py runs its whole pipeline at import, so the function is lifted out
# of the source rather than imported. Ugly, and better than the alternative of
# not testing it at all.
ns = {}
src = open(SRC, encoding="utf-8").read()
m = re.search(r"^def carry_forward.*?^S\.update", src, re.S | re.M)
exec(m.group(0).rsplit("\n\n", 1)[0], ns)
carry_forward = ns["carry_forward"]


def main() -> int:
    fails = []

    r = carry_forward({"revenue_month": None},
                      {"revenue_month": 19.0, "generated": "2026-08-30 11:20"})
    if r.get("revenue_month") != 19.0:
        fails.append("an unmeasured run must keep the previous figure")
    if not r.get("revenue_carried_from"):
        fails.append("a carried figure must say where it came from")

    r = carry_forward({"revenue_month": 42.0}, {"revenue_month": 19.0})
    if r.get("revenue_month") is not None:
        fails.append("a measured run must not be overwritten by the old value")
    if r.get("revenue_carried_from") is not None:
        fails.append("a measured run must not claim to be carried")

    r = carry_forward({"revenue_month": None}, {})
    if r.get("revenue_month") is not None:
        fails.append("with nothing to carry, it must stay unmeasured rather "
                     "than inventing a number")

    r = carry_forward({"revenue_month": None}, {"revenue_month": 0})
    if r.get("revenue_month") != 0:
        fails.append("zero is a measurement and must carry like any other")


    # The case that broke in production: a blind run, then another blind run.
    # The first version carried prev["revenue_month"], so the second blind run
    # found "not measured" sitting there and had nothing to carry.
    measured = carry_forward({"revenue_month": 19.0,
                              "generated": "2026-08-30 10:00"}, {})
    blind1 = carry_forward({"revenue_month": None}, measured)
    blind2 = carry_forward({"revenue_month": None}, blind1)
    if blind2.get("revenue_month") != 19.0:
        fails.append("a second consecutive blind run must still carry the "
                     f"last measured figure, got {blind2.get('revenue_month')}")
    if not blind2.get("revenue_measured_at"):
        fails.append("a carried figure must keep the date it was measured")

    # The customer count comes from the same Stripe read as revenue, so it is
    # known exactly when revenue is and must carry with it. It did not: the
    # carry wrote a "customers" key nothing reads, while the deck renders
    # "paying_customers", so every credential-less run showed carried revenue
    # of $19 above a customer count of None. Two headline figures on the same
    # card contradicting each other.
    m = carry_forward({"revenue_month": 19.0, "paying_customers": 1,
                       "generated": "2026-08-30 10:00"}, {})
    if m.get("customers_last_measured") != 1:
        fails.append("a measuring run must record the customer count as the "
                     f"standing answer, got {m.get('customers_last_measured')}")
    b1 = carry_forward({"revenue_month": None, "paying_customers": None}, m)
    if b1.get("paying_customers") != 1:
        fails.append("a blind run must carry the customer count under the key "
                     f"the deck reads, got {b1.get('paying_customers')}")
    b2 = carry_forward({"revenue_month": None, "paying_customers": None}, b1)
    if b2.get("paying_customers") != 1:
        fails.append("a second consecutive blind run must still carry the "
                     f"customer count, got {b2.get('paying_customers')}")
    if b2.get("revenue_month") == 19.0 and b2.get("paying_customers") is None:
        fails.append("carried revenue beside an unknown customer count is the "
                     "self-contradiction this exists to prevent")

    total = 10
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
