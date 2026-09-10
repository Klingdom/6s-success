#!/usr/bin/env python3
"""
Create Stripe Payment Links for the offers that can be delivered.

SUPERSEDED, found 2026-09-10. The two consulting SKUs this file manages
(6s_consult_virtual / 6s_consult_inhome, matched by Stripe's lookup_key) have
been live on the site under a different identity since 2026-08-27: commit
`d5226967` moved the whole catalogue, consulting included, onto SKU-tagged
prices (metadata.sku = CN-VIRTUAL / CN-INHOME) managed by
`ops/stripe_catalog.py`, and `site/consulting.html`'s real buy buttons point
at those, not at anything this file has ever created. `ops/payment-links.json`,
this file's own output, has not been touched since 2026-08-19 and is stale by
the same margin; nothing else in the repository reads it. Left in place as a
record and because deleting a Stripe-writing tool is not a decision to make
solely on grep results, but do not run this expecting it to reflect, or to
manage, the live consulting checkout: that is `ops/stripe_catalog.py`'s job
now. Running `--apply` against the live key would create a second, orphaned
price and payment link under the old lookup_key scheme, parallel to and
untracked by the SKU catalogue, which is exactly the duplicate-checkout shape
that once left a live page charging $18 next to an advertised $9.99.

A payment link is the right instrument for a static site. It needs no server,
no secret key in the page, and no checkout code: it is an https address that
takes a card. That matters here because everything under site/ is served
verbatim to the public, so a secret key can never live there.

Idempotent: it finds an existing active link for the same price before making
another, so a rerun does not litter the account with duplicates. It refuses to
write to a live account without STRIPE_ALLOW_LIVE=1, the same guard every
other Stripe write tool in this repository carries; found missing here
2026-09-10, the one file of the five that could take a live write action with
no second look at all.

Run:  python ops/stripe_links.py --plan
      STRIPE_ALLOW_LIVE=1 python ops/stripe_links.py --apply
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
API = "https://api.stripe.com/v1"
OUT = os.path.join(ROOT, "ops", "payment-links.json")

# lookup_key of the price, and what the buyer is agreeing to.
WANT = [
    ("6s_consult_virtual", "Virtual Home Consult"),
    ("6s_consult_inhome", "In-Home Reset Day"),
]


def key():
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = {k: v.strip() for k, v in
                   re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M)}
    k = os.environ.get("STRIPE_SECRET_KEY") or env.get("STRIPE_SECRET_KEY", "")
    if not k.strip():
        raise SystemExit("No Stripe secret key in .env.secrets or the environment.")
    return k.strip()


def call(path, k, params=None, method="GET"):
    url = f"{API}/{path}"
    data = None
    if method == "POST":
        data = urllib.parse.urlencode(params or {}, doseq=True).encode()
    elif params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": {"message": body[:200]}}


def main(apply_it):
    k = key()
    live = k.startswith(("sk_live_", "rk_live_"))
    print(f"Mode: {'LIVE' if live else 'test, no real money'}")
    if live and apply_it and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        print("Refusing to write to a LIVE account without STRIPE_ALLOW_LIVE=1 "
              "set. This file is also superseded, see the module docstring: "
              "the live consulting checkout is managed by "
              "ops/stripe_catalog.py now.")
        return 1

    code, prices = call("prices", k, {"limit": "100"})
    if code != 200:
        raise SystemExit(prices.get("error", {}).get("message"))
    by_lookup = {p["lookup_key"]: p for p in prices["data"] if p.get("lookup_key")}

    code, links = call("payment_links", k, {"limit": "100"})
    existing = {}
    if code == 200:
        for pl in links["data"]:
            if not pl.get("active"):
                continue
            c, items = call(f"payment_links/{pl['id']}/line_items", k, {"limit": "5"})
            if c == 200:
                for li in items["data"]:
                    existing[li["price"]["id"]] = pl

    out = {}
    for lookup, name in WANT:
        price = by_lookup.get(lookup)
        if not price:
            print(f"  {name:<24} no price yet, run ops/stripe_setup.py first")
            continue
        if price["id"] in existing:
            pl = existing[price["id"]]
            out[lookup] = pl["url"]
            print(f"  {name:<24} exists  {pl['url']}")
            continue
        print(f"  {name:<24} MISSING a link")
        if not apply_it:
            continue
        c, pl = call("payment_links", k, {
            "line_items[0][price]": price["id"],
            "line_items[0][quantity]": "1",
            # A booking needs a way to reach the person and a note about the room.
            "after_completion[type]": "redirect",
            "after_completion[redirect][url]": "https://6s-success.com/contact",
            "custom_fields[0][key]": "room",
            "custom_fields[0][label][type]": "custom",
            "custom_fields[0][label][custom]": "Which room or micro zone",
            "custom_fields[0][type]": "text",
            "custom_fields[0][optional]": "false",
            "phone_number_collection[enabled]": "true",
            "metadata[offer]": lookup,
        }, "POST")
        if c != 200:
            print(f"      FAILED: {pl.get('error', {}).get('message')}")
            continue
        out[lookup] = pl["url"]
        print(f"      created {pl['url']}")

    if out:
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump({"mode": "live" if live else "test", "links": out}, fh, indent=1)
        print(f"\nwrote {os.path.relpath(OUT, ROOT)}")
        print("These are TEST links until the live account is onboarded. They take"
              if not live else "These are LIVE links. They take")
        print("test cards only." if not live else "real money.")
    return 0


if __name__ == "__main__":
    sys.exit(main(len(sys.argv) > 1 and sys.argv[1] == "--apply"))
