#!/usr/bin/env python3
"""
Prove ops/media_capability.py's "cheapest first" list is sorted by real
cost, not by comparing the cost strings as text.

Found 2026-09-09, reading the file cold: `sorted(working, key=lambda x:
x[1])` sorts the raw cost string. It read right only by coincidence, since
every PROVIDERS entry today starts "0.0...", so lexical order matched
numeric order. A cost of "10.00" sorts before "9.00" as text (leading "1"
beats leading "9"), which would silently misorder a real future provider.
Fixed with cost_key(), which reads the leading number and sorts on that,
falling back to infinity (sorts last) for a non-numeric cost like "high"
or "varies".

Run:  python ops/tests/test_media_capability.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import media_capability as mc                                    # noqa: E402


def main() -> int:
    fails = []

    # 1. The exact regression: a triple-digit-cent cost must not outrank a
    #    cheaper single-digit one just because "10" sorts before "9" as text.
    #    Goes through cheapest_first(), main()'s own call site, not cost_key()
    #    in isolation, so a future edit that stops calling cost_key still
    #    gets caught here.
    working = [("cheap", "9.00", "x"), ("pricier", "10.00", "y")]
    order = [n for n, c, u in mc.cheapest_first(working)]
    if order != ["cheap", "pricier"]:
        fails.append("numeric cost order wrong: %r" % order)

    # 2. A non-numeric cost ("high", "varies") sorts after every priced one.
    working = [("free_ish", "0.01", "x"), ("unknown", "varies", "y"),
               ("costly", "high", "z")]
    order = [n for n, c, u in mc.cheapest_first(working)]
    if order != ["free_ish", "unknown", "costly"]:
        fails.append("non-numeric cost did not sort last: %r" % order)

    # 3. A "low to high" range sorts on its low end.
    if mc.cost_key("0.001 to 0.01") >= mc.cost_key("0.03"):
        fails.append("range cost did not key off its low end")

    # 4. The real PROVIDERS costs, run through the real sort, come back in
    #    genuine cheapest-first order (proves the fix against the live data,
    #    not only a synthetic case).
    real = [(name, cost, use) for name, _, _, use, cost in mc.PROVIDERS]
    ordered = mc.cheapest_first(real)
    keys = [mc.cost_key(c) for _, c, _ in ordered]
    if keys != sorted(keys):
        fails.append("real PROVIDERS list not in ascending cost order: %r"
                     % [n for n, c, u in ordered])

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: media_capability cost sort, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
