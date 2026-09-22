#!/usr/bin/env python3
"""
Close the Stripe half of a retirement: deactivate the links, archive the products.

WHY THIS EXISTS
---------------
Commit 147179c6 retired the 6 Area Bundles and 15 Situation Kits on the
repository side and said so plainly: "This is the repository-side half only.
Deploy, live-verification and Stripe archival stay open." The site no longer
lists them. Stripe still sold them.

That gap matters. A payment link stays live whatever the website says, so an
old bookmark, a link in an email, or a search result could still take somebody
money for a product we have decided not to sell. That is the wrong side of
CLAUDE.md section 8 to be on.

WHAT IT REFUSES TO DO
---------------------
It acts only on SKUs listed in ops/retired-skus.json, and it re-reads that
file rather than taking a list on the command line, so a typo cannot retire
something that is still for sale.

It refuses outright if any object it is about to touch carries
`metadata.ledgerium_plan`. Ledgerium AI bills through its own Stripe account
and none of its objects should ever be reachable from here (CLAUDE.md 36b),
but "should" is not a check.

It refuses to run at all unless the live site has been scanned first and found
clean, because the one failure this repository has actually paid for is a
payment link retired while a page was still serving it: eight days at $0 in
August. --check does that scan and changes nothing.

Run:  python ops/retire_stripe_skus.py --check
      STRIPE_ALLOW_LIVE=1 python ops/retire_stripe_skus.py --apply
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

BASE = "https://6s-success.com"


def retired_skus() -> set:
    fp = os.path.join(ROOT, "ops", "retired-skus.json")
    d = json.load(io.open(fp, encoding="utf-8"))
    return {s["sku"] for s in d["skus"] if isinstance(s, dict) and s.get("sku")}


def fetch(path: str):
    try:
        req = urllib.request.Request(BASE + path,
                                     headers={"User-Agent": "6s-retire-check"})
        return urllib.request.urlopen(req, timeout=30).read().decode(
            "utf-8", "replace")
    except Exception:                                          # noqa: BLE001
        return None


def live_is_clean(skus, link_ids) -> tuple:
    """Scan every URL in the live sitemap plus the catalogue scripts.

    Returns (clean, report). An unreadable page makes it NOT clean: a page we
    could not read is not a page we know is safe.
    """
    sm = fetch("/sitemap.xml")
    if not sm:
        return False, "could not read the live sitemap, so nothing was checked"
    paths = [u.replace(BASE, "") or "/"
             for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
    paths += ["/assets/js/data.js", "/assets/js/shop.js"]
    hits, unreadable = [], []
    for p in paths:
        body = fetch(p)
        if body is None:
            unreadable.append(p)
            continue
        for lid, sku in link_ids.items():
            if lid in body:
                hits.append("%s still links %s (%s)" % (p, sku, lid))
        for s in skus:
            if '"%s"' % s in body:
                hits.append("%s still names %s" % (p, s))
    if unreadable:
        return False, ("%d live page(s) could not be read, so this is "
                       "UNCHECKED, not clean: %s"
                       % (len(unreadable), unreadable[:5]))
    if hits:
        return False, "the live site still serves retired items: %s" % hits[:8]
    return True, "%d live URLs scanned, none references a retired SKU or link" % len(paths)


def main() -> int:
    import stripe_catalog as SC

    apply_it = "--apply" in sys.argv
    if apply_it and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        print("  refusing: --apply needs STRIPE_ALLOW_LIVE=1")
        return 1

    skus = retired_skus()
    print("  retired SKUs on record : %d" % len(skus))

    links = [L for L in SC.list_all("payment_links", {"active": "true"})
             if (L.get("metadata") or {}).get("sku") in skus]
    prods = [p for p in SC.list_all("products", {"active": "true"})
             if (p.get("metadata") or {}).get("sku") in skus]

    for obj in links + prods:
        if (obj.get("metadata") or {}).get("ledgerium_plan"):
            print("  REFUSING: %s carries metadata.ledgerium_plan. That is a "
                  "different business's billing (CLAUDE.md 36b)." % obj["id"])
            return 1

    print("  active payment links   : %d" % len(links))
    print("  active products        : %d" % len(prods))
    if not links and not prods:
        print("  nothing to do: Stripe already matches the retirement.")
        return 0

    link_ids = {}
    for L in links:
        m = re.search(r"buy\.stripe\.com/([A-Za-z0-9]+)", L.get("url", ""))
        if m:
            link_ids[m.group(1)] = L["metadata"]["sku"]

    clean, report = live_is_clean(skus, link_ids)
    print("  live check             : %s" % report)
    if not clean:
        print("  REFUSING to change anything. Retiring a link the live site "
              "still serves is the one mistake that has already cost this "
              "business eight days at $0.")
        return 1

    if not apply_it:
        print("\n  --check only, nothing written. %d link(s) and %d product(s) "
              "would be deactivated." % (len(links), len(prods)))
        return 0

    done = 0
    for L in links:
        SC.call("POST", "payment_links/" + L["id"], {"active": False})
        print("    link  deactivated  %s" % L["metadata"]["sku"])
        done += 1
    for p in prods:
        SC.call("POST", "products/" + p["id"], {"active": False})
        print("    product archived   %s" % p["metadata"]["sku"])
        done += 1
    print("\n  %d object(s) retired in Stripe." % done)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
