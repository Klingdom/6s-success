#!/usr/bin/env python3
"""
Stop shipping the product catalogue to pages that never open it.

THE WASTE
---------
site/assets/js/data.js is 73 KB of catalogue and it was loaded by 179 pages.
Six of them use it: the shop grid, the homepage featured block, the consulting
grid, and a few that render a product card. The other 173 parse it and throw it
away, which is 73 KB per pageview on the 114 zone pages, the 20 room pages and
the 29 articles, the three page types organic traffic actually lands on.

It is not render blocking in the sense of blocking paint forever, but it is a
request and a parse on every one of those pages for a variable nothing reads.

WHY THIS IS SAFE
----------------
site/assets/js/site.js opens with `var CATALOG = window.CATALOG || []`, so it
already handles the catalogue being absent and simply builds an empty index.
Nothing else on a zone, room or article page touches it. That guard is why
this is a removal rather than a rewrite.

CONSERVATIVE ON PURPOSE
-----------------------
A page keeps the script if there is any sign it might need it: a product grid,
a featured block, the shop script, or any mention of CATALOG or renderProduct
in its own markup. When in doubt it keeps it, because a missing catalogue on a
page that renders products is an empty shop, and 73 KB is not worth that risk.

Idempotent. Run it twice and the second run reports nothing to do.

Run:  python ops/prune_catalog_js.py
      python ops/prune_catalog_js.py --check
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

TAG = re.compile(r'\s*<script[^>]*src="[^"]*assets/js/data\.js[^"]*"[^>]*>'
                 r'</script>')

# Any one of these means the page might render a product. The list is
# deliberately broad: a false positive costs 73 KB, a false negative costs an
# empty shop.
NEEDS = ('id="grid"', 'id="featured"', 'id="consulting-grid"',
         'shop.js', 'renderProduct', 'window.CATALOG', 'CATALOG[',
         # The cart renders from rows snapshotted at add time, so it survives
         # without the catalogue, but Cart.add resolves a SKU through it. A
         # commerce page is the wrong place to save 73 KB against a maybe, and
         # the first version of this script pruned it because its markup
         # happens not to mention CATALOG by name.
         'id="cart-lines"', 'window.Cart')


def needs_catalog(s: str) -> bool:
    # Ignore the script tag itself when looking for evidence of use.
    body = TAG.sub("", s)
    return any(k in body for k in NEEDS)


def main() -> int:
    check = "--check" in sys.argv
    kept, pruned, bytes_saved = [], 0, 0
    data = os.path.join(SITE, "assets", "js", "data.js")
    size = os.path.getsize(data) if os.path.exists(data) else 0

    for f in sorted(glob.glob(os.path.join(SITE, "**", "*.html"),
                              recursive=True)):
        rel = os.path.relpath(f, SITE)
        if rel.startswith(("downloads" + os.sep, "deck" + os.sep)):
            continue
        s = io.open(f, encoding="utf-8").read()
        if not TAG.search(s):
            continue
        if needs_catalog(s):
            kept.append(rel)
            continue
        if not check:
            io.open(f, "w", encoding="utf-8", newline="").write(TAG.sub("", s))
        pruned += 1
        bytes_saved += size

    print(f"  data.js is {size/1024:.0f} KB")
    print(f"  kept on {len(kept)} page(s) that render products: {kept[:4]}")
    print(f"  {'would remove' if check else 'removed'} from {pruned} page(s) "
          f"that never read it")
    if pruned:
        print(f"  {bytes_saved/1024/1024:.1f} MB of transfer saved across one "
              f"visit to every page")

    # site.js must keep its guard, or this becomes a breakage rather than a
    # saving. Checked rather than remembered.
    js = io.open(os.path.join(SITE, "assets", "js", "site.js"),
                 encoding="utf-8").read()
    if "window.CATALOG || []" not in js:
        print("  WARNING: site.js no longer defends against an absent "
              "catalogue, so removing the script would break these pages")
        return 1
    print("  site.js still falls back to an empty catalogue, so the pages "
          "without it behave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
