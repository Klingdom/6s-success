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

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {4 - len(fails)} of 4 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
