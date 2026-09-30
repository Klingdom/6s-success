#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_product_schema_url_honest() catches a Product
JSON-LD graph whose `url` disagrees with the catalogue's own `href` for
that item.

Found live 2026-09-30: `ops/build_product_schema.py` builds every graph's
`url` from `p.get("href", "shop.html")`. CN-VIRTUAL and CN-INHOME had no
`href` in data.js even though `consulting.html` is where each one's real
"Book and pay" button lives (id="virtual", id="in-home"), so both
products' Product schema, even the copy embedded IN consulting.html
itself, told a crawler the product's real page was the generic shop grid.

Tests the pure logic (check_product_schema_url_honest) with synthetic
catalogue/page data, so it never touches the real committed site, then
separately checks the real committed shop.html/consulting.html directly.

Run:  python ops/tests/test_gate_product_schema_url_honest.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CAT = {
    "CN-VIRTUAL": {"sku": "CN-VIRTUAL", "href": "consulting.html#virtual"},
    "CN-INHOME": {"sku": "CN-INHOME", "href": "consulting.html#in-home"},
    "PACK-HOUSE": {"sku": "PACK-HOUSE"},  # no href: nothing to check
}


def page(graphs) -> str:
    body = json.dumps(graphs if len(graphs) > 1 else graphs[0], indent=1)
    return ("<head>\n<!-- PRODUCT-SCHEMA:BEGIN -->\n"
            '<script type="application/ld+json">\n' + body +
            "\n</script>\n<!-- PRODUCT-SCHEMA:END -->\n</head>")


def graph(sku, url):
    return {"@type": "Product", "sku": sku, "url": url}


def main() -> int:
    fails = []

    # 1. Clean: every graph's url matches its own catalogue href.
    clean = {
        "shop.html": page([
            graph("CN-VIRTUAL", "https://6s-success.com/consulting.html#virtual"),
            graph("CN-INHOME", "https://6s-success.com/consulting.html#in-home"),
            graph("PACK-HOUSE", "https://6s-success.com/shop.html"),
        ]),
    }
    problems = preflight.check_product_schema_url_honest(CAT, clean)
    if problems:
        fails.append("the clean synthetic case was flagged: %s" % problems)

    # 2. The real, live defect: an item with an href still points at
    #    shop.html, the fallback that fires when href is missing/ignored.
    fallback = {
        "shop.html": page([
            graph("CN-VIRTUAL", "https://6s-success.com/shop.html"),
            graph("CN-INHOME", "https://6s-success.com/consulting.html#in-home"),
        ]),
    }
    problems = preflight.check_product_schema_url_honest(CAT, fallback)
    if not any("CN-VIRTUAL" in p and "consulting.html#virtual" in p
               for p in problems):
        fails.append("CN-VIRTUAL falling back to shop.html was NOT caught: "
                      "%s" % problems)

    # 3. Same defect, found on a second page (the exact live shape: the
    #    stale url shipped on BOTH shop.html and consulting.html at once).
    two_pages = {
        "shop.html": page([graph("CN-INHOME", "https://6s-success.com/shop.html")]),
        "consulting.html": page([graph("CN-INHOME", "https://6s-success.com/shop.html")]),
    }
    problems = preflight.check_product_schema_url_honest(CAT, two_pages)
    if sum("CN-INHOME" in p for p in problems) != 2:
        fails.append("the same stale url on two separate pages should "
                      "produce two findings, got: %s" % problems)

    # 4. An item with no href in the catalogue is never checked (nothing
    #    honest to compare against; gate_bundle_maths-style scope, not this
    #    gate's job).
    no_href = {"shop.html": page([graph("PACK-HOUSE", "https://anything.example/")])}
    problems = preflight.check_product_schema_url_honest(CAT, no_href)
    if problems:
        fails.append("an item with no catalogue href should never be "
                      "flagged: %s" % problems)

    # 5. Against the real thing: the actual committed shop.html and
    #    consulting.html, not synthetic stand-ins.
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    real_cat = {i["sku"]: i for i in json.loads(js[js.index("["):js.rindex("]") + 1])}
    real_pages = {}
    for fname in ("shop.html", "consulting.html"):
        path = os.path.join(ROOT, "site", fname)
        if os.path.exists(path):
            real_pages[fname] = io.open(path, encoding="utf-8").read()
    if len(real_pages) != 2:
        fails.append("shop.html/consulting.html missing; the real-site "
                      "case could not run: found %s" % sorted(real_pages))
    problems = preflight.check_product_schema_url_honest(real_cat, real_pages)
    if problems:
        fails.append("the real committed pages have a live product-schema "
                      "url problem: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_product_schema_url_honest: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
