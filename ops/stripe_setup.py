#!/usr/bin/env python3
"""
Create the 6S Success products and prices in Stripe.

Only what is genuinely deliverable is created. The catalogue lists 41 items;
three are deliverable today and all three are consulting. Creating Stripe
products for reset kits with no supplier, or courses with no platform, would put
a buy path in front of something that does not exist.

Everything here is idempotent. It looks up by a stable lookup_key before
creating, so running it twice does not produce duplicates, and running it after
a partial failure finishes the job rather than doubling it.

Run:  python ops/stripe_setup.py --plan      show what it would do, change nothing
      python ops/stripe_setup.py --apply     create anything missing
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

# Deliverable today. Prices in cents. CN-CORP is deliberately absent: it is
# quoted per engagement, so it is an invoice, not a fixed price product.
PRODUCTS = [
    {
        "key": "6s_consult_virtual",
        "name": "Virtual Home Consult",
        "description": ("A live one hour session on one room. We find the desired "
                        "function, the friction and the root cause, then leave you "
                        "with a written standard for that space."),
        "amount": 25000,
    },
    {
        "key": "6s_consult_inhome",
        "name": "In-Home Reset Day",
        "description": ("A full day in your home working the six-S method through "
                        "one room or a set of micro zones, finishing with standards "
                        "that hold after we leave."),
        "amount": 120000,
    },
]
CURRENCY = "usd"


def creds():
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = dict(re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M))
    key = os.environ.get("STRIPE_SECRET_KEY") or env.get("STRIPE_SECRET_KEY", "")
    if not key.strip():
        raise SystemExit(
            "No Stripe secret key. Paste it into .env.secrets, which is gitignored:\n"
            "  STRIPE_SECRET_KEY=sk_test_...\n"
            "Then run this again. The value never passes through a chat.")
    return key.strip()


def call(path, key, params=None, method="GET"):
    url = f"{API}/{path}"
    data = None
    if method == "POST":
        data = urllib.parse.urlencode(params or {}, doseq=True).encode()
    elif params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": {"message": body[:200]}}


def existing_prices(key):
    """lookup_key -> price, so a rerun recognises what it already made."""
    code, data = call("prices", key, {"limit": "100", "expand[]": "data.product"})
    if code != 200:
        raise SystemExit(f"Could not list prices: {data.get('error', {}).get('message')}")
    return {p["lookup_key"]: p for p in data.get("data", []) if p.get("lookup_key")}


def main(apply_it):
    key = creds()
    live = key.startswith(("sk_live_", "rk_live_"))
    print(f"Mode: {'LIVE, real money' if live else 'test, no real money'}")
    if live and apply_it:
        print("Refusing to create live products from a script without a second "
              "look. Run --plan against the live key, read it, and create them "
              "in the dashboard, or rerun with STRIPE_ALLOW_LIVE=1 set.")
        if os.environ.get("STRIPE_ALLOW_LIVE") != "1":
            return 1

    have = existing_prices(key)
    print(f"Existing prices with a lookup key: {len(have)}\n")

    todo = []
    for p in PRODUCTS:
        state = "exists" if p["key"] in have else "MISSING"
        print(f"  {p['name']:<26} ${p['amount']/100:>8,.2f}  {state}")
        if p["key"] not in have:
            todo.append(p)

    print(f"\n{len(todo)} to create.")
    print("\nNot created, deliberately:")
    print("  Corporate Lean 6S      quoted per engagement, so it is an invoice")
    print("  Reset kits, 4 SKUs     no supplier and no stock")
    print("  Courses, 4 SKUs        no platform and no schedule")
    print("  Tools, 24 SKUs         no supplier")
    print("  Book and manual        blocked on front matter, issue #3")

    if not apply_it:
        print("\nRun with --apply to create the missing ones.")
        return 0

    for p in todo:
        code, prod = call("products", key, {
            "name": p["name"], "description": p["description"],
            "metadata[source]": "ops/stripe_setup.py",
            "metadata[key]": p["key"],
        }, "POST")
        if code != 200:
            print(f"  FAILED product {p['name']}: {prod.get('error', {}).get('message')}")
            continue
        code, price = call("prices", key, {
            "product": prod["id"], "unit_amount": p["amount"],
            "currency": CURRENCY, "lookup_key": p["key"],
        }, "POST")
        if code != 200:
            print(f"  FAILED price {p['name']}: {price.get('error', {}).get('message')}")
            continue
        print(f"  created {p['name']}: {prod['id']} / {price['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(len(sys.argv) > 1 and sys.argv[1] == "--apply"))
