#!/usr/bin/env python3
"""
Confirm the Stripe keys work, without ever revealing them.

This exists so a credential can be verified and used without its value passing
through a chat transcript, a log, or a commit. It prints what the key can reach
and a masked fingerprint, never the key.

It also refuses to continue if a secret key has leaked into the published site,
because site/ is served verbatim to anyone who asks.

Run:  python ops/stripe_check.py
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, ".env.secrets")
API = "https://api.stripe.com/v1"


def load():
    env = {}
    if os.path.exists(SECRETS):
        with open(SECRETS, encoding="utf-8") as fh:
            env = {k: v.strip() for k, v in
                   re.findall(r"^([A-Z_]+)=(.*)$", fh.read(), re.M)}
    for k in ("STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY", "STRIPE_MODE"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def mask(key):
    """Enough to tell two keys apart, not enough to use one."""
    if not key:
        return "(empty)"
    prefix = re.match(r"^[a-z]+_[a-z]+_", key)
    return (prefix.group(0) if prefix else key[:7]) + "..." + key[-4:]


def call(path, key, params=None):
    url = f"{API}/{path}"
    data = None
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url, data=data,
                                 headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": {"message": body[:200]}}
    except Exception as e:
        return None, {"error": {"message": str(e)}}


def leak_scan():
    """A secret key under site/ would be published to the world."""
    bad = []
    for f in glob.glob(os.path.join(ROOT, "site", "**", "*"), recursive=True):
        if not os.path.isfile(f):
            continue
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                if re.search(r"\b(sk|rk)_(live|test)_[A-Za-z0-9]", fh.read()):
                    bad.append(os.path.relpath(f, ROOT))
        except Exception:
            continue
    return bad


def main():
    env = load()
    sk = env.get("STRIPE_SECRET_KEY", "").strip()
    pk = env.get("STRIPE_PUBLISHABLE_KEY", "").strip()

    print("Keys found in .env.secrets")
    print(f"  publishable  {mask(pk)}")
    print(f"  secret       {mask(sk)}")
    if not sk:
        print("\nNo secret key yet. Paste it into .env.secrets and run this again.")
        return 1

    live = sk.startswith(("sk_live_", "rk_live_"))
    print(f"  mode         {'LIVE, real money' if live else 'test, no real money'}")
    if sk.startswith("rk_"):
        print("  type         restricted key (good, least privilege)")

    print("\nLeak scan")
    bad = leak_scan()
    if bad:
        print("  FAIL a secret key pattern appears in the published site:")
        for b in bad:
            print(f"       {b}")
        print("  Remove it before anything is deployed. site/ is public.")
        return 1
    print("  PASS no secret key pattern under site/")

    print("\nWhat the key can reach")
    code, acct = call("account", sk)
    if code != 200:
        print(f"  FAIL {acct.get('error', {}).get('message', code)}")
        return 1
    print(f"  PASS account {acct.get('id')}"
          f"  {acct.get('business_profile', {}).get('name') or '(no business name set)'}")
    print(f"       country {acct.get('country')}  "
          f"default currency {acct.get('default_currency')}")
    print(f"       charges enabled: {acct.get('charges_enabled')}   "
          f"payouts enabled: {acct.get('payouts_enabled')}")
    if not acct.get("charges_enabled"):
        print("       NOTE onboarding is incomplete, so this account cannot take money yet")

    for label, path in (("products", "products"), ("prices", "prices"),
                        ("invoices", "invoices"), ("customers", "customers")):
        code, data = call(path, sk, {"limit": "1"})
        if code == 200:
            n = len(data.get("data", []))
            print(f"  PASS {label:<10} readable"
                  + ("" if n else "  (none created yet)"))
        else:
            print(f"  ---- {label:<10} {data.get('error', {}).get('message', code)[:70]}")

    print("\nReady. Nothing here was printed that could be used to charge a card.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
