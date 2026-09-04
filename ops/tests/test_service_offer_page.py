"""The two service offers must be buyable from plain HTML, at catalogue prices.

WHY THIS EXISTS
---------------
REVENUE-REVIEW-2026-09-04.md put the arithmetic plainly: 97% of the 159 products
are priced $4 to $19, and at a 2% conversion the $19 pack would need 52,632
visitors a month to reach the goal, about a thousand times today's traffic. The
only mix that is arithmetic rather than fantasy is services, eight in-home days
plus forty two virtual consults. So CN-VIRTUAL and CN-INHOME are the two SKUs
this business's target actually depends on, and site/consulting.html is the one
page that sells them.

Before 2026-09-04 that page's offer existed only after JavaScript ran: the grid
was rendered from window.CATALOG, so a client that does not execute script read
the page and found no price and no way to pay. That is the same defect
gate_shop_prerendered() exists for on shop.html, on a page with ten times the
revenue riding on it. The fix was to write both offers into the page as static
HTML, which trades a runtime read of the catalogue for two prices typed into
prose, and a typed price is exactly the thing that goes stale. The book once
showed $9.99 on every surface while its payment link charged $18.

So this asserts the trade is safe:

    both SKUs have a buy button in HTML that survives scripts being off;
    each href is byte-identical to the catalogue's payment link;
    each visible price equals the catalogue price;
    each button carries data-sku, so measure.js files the click correctly;
    the Treasure Valley restriction on CN-INHOME is stated on the page.

The last one is not decoration. CN-INHOME is deliverable in seven named towns
in Idaho, and taking $1,200 from somebody in Ohio because the page did not say
so is a refund and a broken promise, not a sale.

Nothing here touches Stripe. The catalogue file is the authority, exactly as it
is for the shop.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, "site", "consulting.html")
DATA = os.path.join(ROOT, "site", "assets", "js", "data.js")

# Every town CN-INHOME can actually be delivered in. If the offer's reach
# changes, this list and the page change together or this fails, which is the
# point: the geography is part of the price.
TOWNS = ["Boise", "Meridian", "Eagle", "Nampa", "Kuna", "Star", "Garden City"]


def catalogue() -> dict:
    js = io.open(DATA, encoding="utf-8").read()
    items = json.loads(js[js.index("["):js.rindex("]") + 1])
    return {p["sku"]: p for p in items}


def money(v) -> str:
    """$1,200 and $250, the way the page writes them."""
    return "$" + format(int(v), ",") if float(v) == int(v) else "$%.2f" % v


def main() -> int:
    bad = []

    if not os.path.exists(PAGE):
        print("  site/consulting.html is missing. NOT VERIFIED.")
        return 0

    html = io.open(PAGE, encoding="utf-8").read()
    # What a client with no JavaScript actually reads. Scripts stripped, so a
    # buy link that only exists inside one cannot satisfy any assertion below.
    plain = re.sub(r"(?is)<script.*?</script>", " ", html)

    cat = catalogue()
    for sku in ("CN-VIRTUAL", "CN-INHOME"):
        item = cat.get(sku)
        if not item:
            bad.append("%s is not in the catalogue at all" % sku)
            continue

        links = re.findall(
            r'<a[^>]*data-sku="%s"[^>]*href="([^"]+)"[^>]*>(.*?)</a>' % sku,
            plain, re.S)
        if not links:
            # Attribute order is not guaranteed, so try the other way round
            # before calling it missing.
            links = re.findall(
                r'<a[^>]*href="([^"]+)"[^>]*data-sku="%s"[^>]*>(.*?)</a>' % sku,
                plain, re.S)
        if not links:
            bad.append("%s has no buy button in plain HTML on consulting.html. "
                       "A visitor without JavaScript cannot pay." % sku)
            continue

        href, label = links[0]
        want = item.get("buy")
        if not want:
            bad.append("%s carries no payment link in the catalogue, so the "
                       "page must not offer one" % sku)
        elif href != want:
            bad.append("%s buy link on the page is %r, catalogue says %r"
                       % (sku, href, want))

        price = money(item["price"])
        if price not in re.sub(r"<[^>]+>", " ", label):
            bad.append("%s button reads %r, which does not state the catalogue "
                       "price %s" % (sku, re.sub(r"\s+", " ", label).strip(), price))
        if price not in re.sub(r"<[^>]+>", " ", plain):
            bad.append("%s price %s appears nowhere in the page text" % (sku, price))

    # The geography, which is a term of the $1,200 offer and not marketing.
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", plain))
    missing = [t for t in TOWNS if t not in text]
    if "Treasure Valley" not in text:
        bad.append("consulting.html does not say Treasure Valley, so the only "
                   "place the In-Home Reset Day can be delivered is unstated")
    if missing:
        bad.append("the In-Home service area omits %s, so a buyer there cannot "
                   "tell whether they are covered" % ", ".join(missing))

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  both services are buyable from plain HTML at catalogue "
              "prices, and the In-Home service area is stated")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
