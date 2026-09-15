#!/usr/bin/env python3
"""
Prove every zone and room pack in the shop links the free page that explains it,
and that the page is the right one.

Added 2026-09-15. The shop sold 109 zone packs and 19 room packs as a name, a
blurb and a buy button. The zone and room pages already hold the free steps
each pack prints, and already offer that pack. ops/wire_generated_catalog.py
now writes a `page` for each such pack and site/assets/js/site.js renders it
as "Read the free steps first", so the order is explain, then offer, from the
shop side too.

The strongest proof that a link points at the right page is not the file
name: it is that the page's own pack button carries the same Stripe payment
link as the shop card. A page for a different zone would carry a different
link.

Run:  python ops/tests/test_pack_pages.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")


def catalogue():
    js = io.open(os.path.join(SITE, "assets", "js", "data.js"), encoding="utf-8").read()
    return json.loads(js[js.index("["):js.rindex("]") + 1])


def page_problems(cat):
    """Every way a zone or room pack's page link can be wrong."""
    out = []
    for p in cat:
        if p.get("cat") not in ("Micro Zone Packs", "Room Packs"):
            if p.get("page"):
                out.append("%s is not a zone or room pack but links %s" % (p["sku"], p["page"]))
            continue
        page = p.get("page")
        if not page:
            out.append("%s has no page" % p["sku"])
            continue
        # page is the extensionless canonical path every internal link on the
        # site uses (ops/canonical_links.py); the file on disk still carries
        # .html.
        path = os.path.join(SITE, page + ".html")
        if not os.path.exists(path):
            out.append("%s links %s, which does not exist" % (p["sku"], page))
            continue
        want = "zones/" if p["cat"] == "Micro Zone Packs" else "rooms/"
        if not page.startswith(want):
            out.append("%s links %s, not a %s page" % (p["sku"], page, want.rstrip("/")))
            continue
        html = io.open(path, encoding="utf-8").read()
        if p.get("buy") and p["buy"] not in html:
            out.append("%s links %s, but that page does not offer this pack's buy link" % (p["sku"], page))
    return out


def main() -> int:
    fails = []
    cat = catalogue()
    packs = [p for p in cat if p.get("cat") in ("Micro Zone Packs", "Room Packs")]
    if len(packs) < 120:
        fails.append("expected about 128 zone and room packs, found %d" % len(packs))
    probs = page_problems(cat)
    if probs:
        fails.append("real catalogue: %d problem(s): %r" % (len(probs), probs[:3]))

    js = io.open(os.path.join(SITE, "assets", "js", "site.js"), encoding="utf-8").read()
    if not re.search(r"p\.page\s*\?\s*'<p class=\"fulfil\"><a href=\"' \+ p\.page", js):
        fails.append("site.js renderProduct no longer renders the pack's page link")

    # Planted regressions, in memory only.
    zone_packs = [dict(p) for p in packs if p["cat"] == "Micro Zone Packs"]
    if len(zone_packs) >= 2:
        a, b = zone_packs[0], zone_packs[1]
        a["page"], b["page"] = b["page"], a["page"]
        if not any("does not offer this pack's buy link" in x for x in page_problems([a, b])):
            fails.append("two zone packs with swapped pages were not caught")
    gone = dict(packs[0]); gone.pop("page", None)
    if not any("has no page" in x for x in page_problems([gone])):
        fails.append("a pack with no page was not caught")
    wrong_kind = dict(packs[0]); wrong_kind["cat"] = "Situation Kits"
    if not any("is not a zone or room pack" in x for x in page_problems([wrong_kind])):
        fails.append("a kit carrying a page was not caught")
    missing = dict(packs[0]); missing["page"] = "zones/not-a-real-zone"
    if not any("does not exist" in x for x in page_problems([missing])):
        fails.append("a page that does not exist was not caught")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: pack pages, %d zone and room packs each link the page that offers them; swapped, missing, "
          "nonexistent and wrong-kind links all caught" % len(packs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
