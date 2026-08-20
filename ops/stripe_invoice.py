#!/usr/bin/env python3
"""
Raise a Stripe invoice for quoted work.

Corporate Lean 6S has no fixed price: it is scoped per engagement, so a payment
link is the wrong instrument. An invoice is the right one. It also covers any
consulting sold off the site, a bespoke scope, or a follow up session.

This is the only monetised path that needed building. Everything else either
has a payment link already or cannot be delivered yet, and a buy path in front
of something undeliverable is worse than no buy path at all.

Safety properties, deliberate:
  It never finalises or sends without --send. Draft is the default, so the
  worst case of a mistake is a draft nobody sees.
  It refuses to run against a live key unless STRIPE_ALLOW_LIVE=1, the same
  guard the product and link scripts use, because a script that can bill a real
  customer on a first run will eventually bill one by accident.
  It matches an existing customer by email rather than creating duplicates.

Run:
  python ops/stripe_invoice.py --draft  --email a@b.com --name "Acme" \
      --item "Corporate Lean 6S, one day onsite" --amount 3500
  python ops/stripe_invoice.py --send ...same args...
"""
import argparse
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
# Matches the published refund terms in site/terms.html. If those change, this
# must change with them, or the invoice promises something the site does not.
FOOTER = ("Cancel more than 7 days before the session for a full refund, or "
          "between 2 and 7 days for half. Inside 48 hours we cannot refund but "
          "you may reschedule once at no charge. If we cancel, you are refunded "
          "in full. If the session was not useful, tell us within 7 days and we "
          "will refund it. Questions: support@6s-success.com")


def key():
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = {k: v.strip() for k, v in
                   re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M)}
    k = (os.environ.get("STRIPE_SECRET_KEY") or env.get("STRIPE_SECRET_KEY", "")).strip()
    if not k:
        raise SystemExit("No Stripe secret key.")
    return k


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
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main(a):
    k = key()
    live = k.startswith(("sk_live_", "rk_live_"))
    print(f"  mode: {'LIVE, real money' if live else 'test'}")
    if live and a.send and os.environ.get("STRIPE_ALLOW_LIVE") != "1":
        print("  Refusing to send a live invoice without STRIPE_ALLOW_LIVE=1 set.")
        return 1

    code, found = call("customers", k, {"email": a.email, "limit": "1"})
    if code == 200 and found.get("data"):
        cust = found["data"][0]
        print(f"  customer: existing {cust['id']}")
    else:
        code, cust = call("customers", k,
                          {"email": a.email, "name": a.name}, "POST")
        if code != 200:
            print("  FAILED customer:", cust.get("error", {}).get("message")); return 1
        print(f"  customer: created {cust['id']}")

    code, inv = call("invoices", k, {
        "customer": cust["id"],
        "collection_method": "send_invoice",
        "days_until_due": str(a.days),
        "description": a.item,
        "footer": FOOTER,
        "auto_advance": "false",
        "metadata[source]": "ops/stripe_invoice.py",
    }, "POST")
    if code != 200:
        print("  FAILED invoice:", inv.get("error", {}).get("message")); return 1

    code, item = call("invoiceitems", k, {
        "customer": cust["id"], "invoice": inv["id"],
        "amount": str(int(round(a.amount * 100))), "currency": "usd",
        "description": a.item,
    }, "POST")
    if code != 200:
        print("  FAILED line item:", item.get("error", {}).get("message")); return 1

    print(f"  invoice: {inv['id']} draft, ${a.amount:,.2f}, due in {a.days} days")
    if not a.send:
        print(f"  Draft only. Review at https://dashboard.stripe.com/invoices/{inv['id']}")
        print("  Rerun with --send to finalise and email it.")
        return 0

    code, sent = call(f"invoices/{inv['id']}/send", k, {}, "POST")
    if code != 200:
        print("  FAILED send:", sent.get("error", {}).get("message")); return 1
    print(f"  sent to {a.email}")
    print(f"  hosted page: {sent.get('hosted_invoice_url')}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--draft", action="store_true")
    p.add_argument("--send", action="store_true")
    p.add_argument("--email", required=True)
    p.add_argument("--name", default="")
    p.add_argument("--item", required=True)
    p.add_argument("--amount", type=float, required=True)
    p.add_argument("--days", type=int, default=14)
    args = p.parse_args()
    if not (args.draft or args.send):
        sys.exit("Pass --draft or --send.")
    sys.exit(main(args))
