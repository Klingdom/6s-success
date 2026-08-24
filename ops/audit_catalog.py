#!/usr/bin/env python3
"""
Check every published page's product claims against the two files that are
supposed to be the source of truth: site/assets/js/data.js, what is live and
what it costs, and ops/retired-skus.json, what was pulled and why.

WHY THIS EXISTS
---------------
Three cycles running, a factual claim on the live site drifted out of step
with those two files, and each time it was found by luck rather than by a
check: a fabricated testimonial on the consulting page, 21 August; the
Virtual Home Consult sold as ninety minutes when the catalogue, both Product
schema blocks, the homepage and an article all said one hour, 24 August; a
retired 49 dollar a year Pro tier still sold in the top nav of all 180
pages, also 24 August. See issue #24. A gate turns luck into arithmetic and
runs in the first minute of a cycle rather than the fortieth.

WHAT IT CHECKS
--------------
  retired-sold    a retired SKU's name, together with its own price or
                   variant text, or with buy-intent language nearby,
                   appearing on a live page. Tolerates the two known name
                   collisions (BK-HC and BK-EB both "6S Success: Home
                   Edition"; DECK-ENTRY-PDF and DECK-ENTRY-BOX both "The
                   Entryway Deck", shared with the live free DECK-ENTRY) by
                   requiring a signal specific to the retired configuration,
                   not the name alone. Skips the MPL-* product-type lists on
                   resources.html on purpose: those are kit contents we name
                   as types, never as an offer of ours.
  price-drift      a live SKU's name followed closely by a dollar figure
                   that is not that SKU's own price.
  dead-buy-link    a buy.stripe.com href on the site that is not any live
                   SKU's buy link in data.js. ops/stripe_catalog.py already
                   asserts the other direction, that every live SKU's link
                   works; this is the reverse.

This does not parse every possible phrasing of a price or a claim, only the
shapes that have actually broken. A page-copy fix is not this script's job;
finding the drift is.

Run:  python ops/audit_catalog.py
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DATA_JS = os.path.join(SITE, "assets", "js", "data.js")
RETIRED = os.path.join(ROOT, "ops", "retired-skus.json")

# The book sample is a 50 chapter export, not a page anybody authored or
# sells from directly; holding it to product-copy rules drowns real findings
# the same way it does in ops/audit_pages.py.
SKIP = ("downloads/",)

WINDOW = 200  # chars either side of a name match, wide enough for a sentence

BUY_INTENT = re.compile(
    r"\b(buy|add to cart|order now|order today|purchase|get it now|"
    r"shop now|upgrade to|upgrade now|checkout|buy now|subscribe)\b",
    re.I,
)

BUY_LINK = re.compile(r'https://buy\.stripe\.com/\S+?(?=["\'\s<])')

# Dollar figures that are not a claim about this product's own price: a
# bundle's blurb naming what its parts cost apart, or a badge naming the
# saving, both real content that must not read as drift.
PRICE_NOISE = re.compile(
    r"(save|separately|bought separately|compared to|was\s*\$)", re.I
)


def load_catalog() -> list[dict]:
    src = open(DATA_JS, encoding="utf-8").read()
    start = src.index("[")
    end = src.rindex("]") + 1
    return json.loads(src[start:end])


def load_retired() -> list[dict]:
    return json.load(open(RETIRED, encoding="utf-8"))["skus"]


def pages() -> list[str]:
    out = []
    for p in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        if not any(rel.startswith(s) for s in SKIP):
            out.append(p)
    return out


def text_of(html: str) -> str:
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))


def check_retired_sold(rel: str, html: str, text: str, retired: list[dict],
                        live_names: set[str]) -> list[str]:
    found = []
    for sku in retired:
        if sku["sku"].startswith("MPL-"):
            continue  # product-type reference lists, never an offer of ours
        name = sku["name"]
        variant = sku.get("variant", "")
        price = sku.get("price")
        shared_name = name.strip().lower() in live_names

        for m in re.finditer(re.escape(name), text, re.I):
            window = text[max(0, m.start() - WINDOW): m.end() + WINDOW]
            price_hit = price is not None and re.search(rf"\${price}\b", window)
            variant_hit = bool(variant) and variant.lower() in window.lower()
            buy_hit = BUY_INTENT.search(window) is not None
            sku_hit = sku["sku"] in html

            if shared_name:
                # The name alone is explained by the live sibling. Only flag
                # when something specific to the retired configuration, its
                # own price or variant text, sits next to buy-intent language.
                if (price_hit or variant_hit) and buy_hit:
                    found.append(
                        f"{sku['sku']} ({name}, {variant}): buy-intent text "
                        f"near a price or variant match for the retired SKU"
                    )
                    break
            else:
                if price_hit or variant_hit or buy_hit or sku_hit:
                    reason = ("its own SKU code" if sku_hit else
                              "its own price" if price_hit else
                              "its own variant text" if variant_hit else
                              "buy-intent language")
                    found.append(f"{sku['sku']} ({name}): name plus {reason}")
                    break
    return found


def check_price_drift(text: str, catalog: list[dict]) -> list[str]:
    found = []
    for sku in catalog:
        price = sku.get("price")
        if price is None:
            continue  # quoted engagement, no fixed price to drift from
        name = sku["name"]
        for m in re.finditer(re.escape(name), text, re.I):
            tail = text[m.end(): m.end() + 60]
            if PRICE_NOISE.search(tail):
                continue
            dm = re.search(r"\$(\d[\d,]*)", tail)
            if dm:
                seen = int(dm.group(1).replace(",", ""))
                if seen != price:
                    found.append(
                        f"{sku['sku']} ({name}): ${seen} shown, "
                        f"catalogue price is ${price}"
                    )
    return found


def check_dead_links(html: str, live_links: set[str]) -> list[str]:
    found = []
    for link in set(BUY_LINK.findall(html)):
        if link not in live_links:
            found.append(f"buy.stripe.com link not in data.js: {link}")
    return found


def main() -> int:
    catalog = load_catalog()
    retired = load_retired()
    live_names = {s["name"].strip().lower() for s in catalog}
    live_links = {s["buy"] for s in catalog if "buy" in s}

    per_page: dict[str, list[str]] = {}
    for p in pages():
        html = open(p, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(p, SITE).replace("\\", "/")
        text = text_of(html)
        f = (check_retired_sold(rel, html, text, retired, live_names)
             + check_price_drift(text, catalog)
             + check_dead_links(html, live_links))
        if f:
            per_page[rel] = f

    total = sum(len(v) for v in per_page.values())
    print(f"  {len(pages())} pages checked against {len(catalog)} live SKUs "
          f"and {len(retired)} retired SKUs")
    print(f"  {total} finding(s) across {len(per_page)} page(s)\n")

    if per_page:
        for rel, f in per_page.items():
            print(f"  {rel}")
            for line in f:
                print(f"    {line}")
        return 1

    print("  PASS  no retired SKU sold")
    print("  PASS  no price drift from the catalogue")
    print("  PASS  every buy.stripe.com link resolves to a live SKU")
    print("\n  Clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
