#!/usr/bin/env python3
"""
Give the shop Product structured data, generated from the catalogue.

WHY
---
Six products can be bought and the site emitted zero Product markup, so as far
as a search engine or an answer engine was concerned this site sold nothing.
Price, availability and a buy URL are exactly the fields that let a result show
as a product rather than as a page, and they were all missing.

WHY IT IS GENERATED AND NOT WRITTEN
-----------------------------------
The shop renders its cards from window.CATALOG at runtime. Structured data
written by hand beside that would drift the first time a price changed, and the
drift would be invisible because nothing renders it. This reads the same
catalogue the page does, so the markup and the card can only ever agree.

It is emitted into the static HTML rather than injected by JavaScript, because
a crawler that does not execute scripts still has to see it.

HONESTY
-------
Only items with a real payment link get an Offer with a price. A free item is
marked as free, and the quoted engagement carries no Offer at all, because a
price it does not have would be a fabricated one.

Run:  python ops/build_product_schema.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"

MARK_OPEN = "<!-- PRODUCT-SCHEMA:BEGIN -->"
MARK_CLOSE = "<!-- PRODUCT-SCHEMA:END -->"

# Which page each product's structured data belongs on. A product described on
# two pages at once competes with itself.
PAGES = {
    "shop.html": None,                    # everything
    "consulting.html": "Consulting",      # just the services
}


def catalogue() -> list[dict]:
    js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                 encoding="utf-8").read()
    return json.loads(js[js.index("["):js.rindex("]") + 1])


def product_ld(p: dict) -> dict | None:
    """One Product graph, or None when there is nothing honest to say."""
    name = p["name"]
    if p.get("variant"):
        name = f"{name} ({p['variant']})"

    node = {
        "@context": "https://schema.org",
        "@type": "Product",
        "@id": f"{BASE}/shop.html#{p['sku']}",
        "name": name,
        "sku": p["sku"],
        "description": p["blurb"],
        "image": f"{BASE}/assets/img/{p['img']}",
        "brand": {"@type": "Brand", "name": "6S Success"},
        "url": f"{BASE}/{p.get('href', 'shop.html')}",
    }

    if p.get("buy"):
        node["offers"] = {
            "@type": "Offer",
            "price": f"{p['price']:.2f}",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": p["buy"],
            "seller": {"@type": "Organization", "name": "6S Success"},
        }
        return node

    if p.get("href") and p.get("price") == 0:
        node["offers"] = {
            "@type": "Offer",
            "price": "0.00",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": f"{BASE}/{p['href']}",
        }
        return node

    # Quoted work has no price, and inventing one to satisfy a schema would be
    # exactly the kind of fabricated claim the rest of this site avoids.
    return None


def render(items: list[dict]) -> str:
    graphs = [g for g in (product_ld(p) for p in items) if g]
    if not graphs:
        return MARK_OPEN + MARK_CLOSE
    body = json.dumps(graphs if len(graphs) > 1 else graphs[0], indent=1)
    return (MARK_OPEN + '\n<script type="application/ld+json">\n'
            + body + "\n</script>\n" + MARK_CLOSE)


def main() -> int:
    cat = catalogue()
    total = 0
    for page, only_cat in PAGES.items():
        path = os.path.join(SITE, page)
        if not os.path.exists(path):
            continue
        items = [p for p in cat if only_cat is None or p["cat"] == only_cat]
        block = render(items)
        s = io.open(path, encoding="utf-8").read()

        if MARK_OPEN in s:
            s = re.sub(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE),
                       block, s, flags=re.S)
        else:
            # Sits with the other structured data in the head, not in the body,
            # so it is found before a crawler decides how much of the page to
            # read.
            s = s.replace("</head>", block + "\n</head>", 1)
        io.open(path, "w", encoding="utf-8", newline="").write(s)

        n = sum(1 for p in items if product_ld(p))
        total += n
        skipped = len(items) - n
        print(f"  {page:18} {n} product graph(s)"
              + (f", {skipped} skipped with no honest price" if skipped else ""))

    # Anything claiming a price has to match the catalogue exactly, or the shop
    # and the search result disagree about what something costs.
    for page in PAGES:
        path = os.path.join(SITE, page)
        if not os.path.exists(path):
            continue
        s = io.open(path, encoding="utf-8").read()
        m = re.search(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE), s, re.S)
        if not m or "<script" not in m.group(0):
            continue
        raw = re.search(r"<script[^>]*>(.*?)</script>", m.group(0), re.S).group(1)
        graphs = json.loads(raw)
        graphs = graphs if isinstance(graphs, list) else [graphs]
        by_sku = {p["sku"]: p for p in cat}
        for g in graphs:
            want = by_sku[g["sku"]]
            got = float(g["offers"]["price"])
            assert got == float(want["price"]), \
                f"{g['sku']}: schema says {got}, catalogue says {want['price']}"
    print(f"  {total} products described, every price matches the catalogue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
