#!/usr/bin/env python3
"""
Prove ops/revenue_model.py prints each price exactly, not rounded to a
whole dollar.

Found 2026-09-07 reading the file cold: the per-price table row formatted
price with `${price:>6,.0f}`, so the Home Edition eBook's real $9.99 (set
2026-08-27 alongside the Amazon KDP listing) printed as "$10". This is the
exact tool ROADMAP-2026-2029.md tells a reader to rerun for the live
numbers ("Reproduce with `python ops/revenue_model.py`"), and section 1's
own history already records one cycle spending real effort correcting a
stale $18 figure that drifted from this same SKU. A tool a reader is told
to trust for the real number should not itself round one away.

Fixed by printing price with two decimals (`.2f`) instead of zero. This
test runs main() for real against the live catalogue and checks that any
price with a fractional cents component appears in the output with those
cents intact, so a future reformat that rounds again is caught here
instead of by the next person copying "$10" into a strategy document by
hand.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import revenue_model as rm                                     # noqa: E402


def main() -> int:
    failures = []

    js = io.open(os.path.join(rm.ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    fractional = [p for p in cat if p.get("buy") and p.get("price")
                  and round(p["price"] * 100) % 100 != 0]

    if not fractional:
        print("ok: no fractional-cents price in the live catalogue to "
              "check against (nothing exercises the rounding path today)")
        return 0

    buf = io.StringIO()
    with redirect_stdout(buf):
        rm.main()
    out = buf.getvalue()

    for p in fractional:
        # The price column right-pads with spaces, so match "$" then
        # optional whitespace then the exact two-decimal figure, not a
        # literal substring.
        pattern = r"\$\s*" + re.escape(f"{p['price']:,.2f}") + r"\b"
        if not re.search(pattern, out):
            failures.append(
                f"{p['sku']} is ${p['price']:.2f} live but that exact "
                f"figure does not appear in revenue_model.py's own output; "
                f"a reader following ROADMAP-2026-2029.md's own "
                f"'reproduce with' instruction would see the wrong price")

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print(f"ok: revenue_model.py prints {len(fractional)} fractional "
          "price(s) exactly, none rounded to a whole dollar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
