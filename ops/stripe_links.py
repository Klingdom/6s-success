#!/usr/bin/env python3
"""
Create Stripe Payment Links for the offers that can be delivered.

A payment link is the right instrument for a static site. It needs no server,
no secret key in the page, and no checkout code: it is an https address that
takes a card. That matters here because everything under site/ is served
verbatim to the public, so a secret key can never live there.

Only consulting gets a link. It is the only thing deliverable today. Creating a
link for a reset kit with no supplier would be taking money for something that
cannot ship.

Idempotent: it finds an existing active link for the same price before making
another, so a rerun does not litter the account with duplicates.

Run:  python ops/stripe_links.py --plan
      python ops/stripe_links.py --apply
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
