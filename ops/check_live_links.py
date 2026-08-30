#!/usr/bin/env python3
"""
Every buy button on the LIVE site must point at a payment link Stripe will honour.

THE OUTAGE THIS EXISTS FOR
--------------------------
On 2026-08-30, every buy button on 6s-success.com pointed at Stripe payment
link 9B66oAgYedoC4ZA6VW0kE04, which the Stripe API reports as active=false.
The repository's link for the same product, 00wdR223kfwK9fQ9440kF28, is
active=true. Production was serving a build old enough to carry the previous
generation of links, and the account holds 464 links of which 309 are
deactivated.

So the business could not take money, and had not been able to for days.

WHY NOTHING CAUGHT IT
---------------------
Because every check that existed was true. The page returned 200. The link
returned 200 as well: a deactivated Stripe link serves the same 550 KB
JavaScript shell as a working one and only resolves to "this link is no longer
active" in the browser, client side. An HTTP status check cannot tell the two
apart, and ops/check_sellable.py checks the repository, where the links are
correct.

The only thing that can tell them apart is the API's active flag, checked
against the links the live site is actually serving.

WHAT IT CHECKS
--------------
The live pages, not the repository. That is the whole point: the repository
being right is what made this invisible.

Run:  python ops/check_live_links.py
      python ops/check_live_links.py --json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://6s-success.com"

# A spread of page types rather than all 189: the buy links are generated, so
# one of each kind proves the generation, and a sample keeps this fast enough
# to run in a gate.
PAGES = [
    "/",
    "/shop.html",
    "/book.html",
    "/deck-gallery.html",
    "/zones/entryway-the-landing-spot.html",
    "/rooms/kitchen.html",
]

SLUG = re.compile(r"buy\.stripe\.com/([A-Za-z0-9]+)")


def secret() -> str | None:
    p = os.path.join(ROOT, ".env.secrets")
    if not os.path.exists(p):
        return os.environ.get("STRIPE_SECRET_KEY")
    for line in io.open(p, encoding="utf-8", errors="replace"):
        if line.startswith("STRIPE_SECRET_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("STRIPE_SECRET_KEY")


def fetch(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "6s-linkcheck"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:                                         # noqa: BLE001
        return None


def all_links(key: str) -> dict:
    """slug -> active, for every payment link on the account.

    Paginated deliberately. An earlier bug in this repository listed with
    limit=100 and no pagination, silently saw only the first hundred of 464,
    and created duplicates for everything it could not see.
    """
    out, url = {}, "https://api.stripe.com/v1/payment_links?limit=100"
    while True:
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        for l in d["data"]:
            out[l["url"].rsplit("/", 1)[-1]] = bool(l.get("active"))
        if not d.get("has_more"):
            return out
        url = ("https://api.stripe.com/v1/payment_links?limit=100"
               "&starting_after=" + d["data"][-1]["id"])


def check() -> dict:
    r = {"reachable": None, "checked_pages": 0, "slugs": {}, "dead": [],
         "unknown": [], "verdict": "unknown", "note": ""}
    key = secret()
    if not key:
        r["note"] = "no Stripe credential in this environment"
        return r

    try:
        active = all_links(key)
    except Exception as e:                                    # noqa: BLE001
        r["note"] = f"Stripe could not be read: {type(e).__name__}"
        return r

    found = {}
    for path in PAGES:
        body = fetch(BASE + path)
        if body is None:
            continue
        r["checked_pages"] += 1
        for slug in set(SLUG.findall(body)):
            found.setdefault(slug, []).append(path)

    r["reachable"] = r["checked_pages"] > 0
    if not r["reachable"]:
        r["note"] = "the live site could not be reached"
        return r

    for slug, pages in sorted(found.items()):
        state = active.get(slug)
        r["slugs"][slug] = {"active": state, "pages": pages}
        if state is False:
            r["dead"].append((slug, pages))
        elif state is None:
            r["unknown"].append((slug, pages))

    r["verdict"] = "dead" if r["dead"] else ("unknown" if r["unknown"] else "ok")
    return r


def main() -> int:
    r = check()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=1, default=str))
        return 0

    if r["verdict"] == "unknown" and not r["slugs"]:
        print(f"  UNKNOWN  {r['note']}. This is not the same as the buttons "
              f"working.")
        return 0

    # Say what was looked at, always.
    print(f"  looked at: {r['checked_pages']} live page(s) on {BASE}, "
          f"{len(r['slugs'])} distinct payment link(s) found on them")
    for slug, d in r["slugs"].items():
        state = {True: "active", False: "DEACTIVATED", None: "not in account"}[d["active"]]
        print(f"    {slug:26} {state:16} on {len(d['pages'])} page(s)")

    if r["verdict"] == "ok":
        print(f"\n  OK       every payment link the live site serves is active "
              f"in Stripe.")
        return 0
    if r["dead"]:
        print(f"\n  OUTAGE   {len(r['dead'])} payment link(s) on the live site "
              f"are deactivated in Stripe. Anybody clicking buy reaches a dead "
              f"link. A deactivated link still answers HTTP 200, so no status "
              f"check can see this.")
        return 1
    print(f"\n  UNKNOWN  {len(r['unknown'])} link(s) are not in this Stripe "
          f"account at all, which is worse than deactivated, not better.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
