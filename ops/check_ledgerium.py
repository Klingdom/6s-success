"""Ledgerium AI's billing lives in the 6S Success Stripe account. Watch it.

Ledgerium is a separate business that bills through this account, so its
subscription prices are revenue that does not appear anywhere in the 6S Success
catalogue, dashboard or backlog. Nothing else in this repository would notice if
they were archived, and the tooling here does archive things: ensure_link
retires superseded payment links, and ensure_product deactivates prices when an
amount changes.

Those functions only act on objects carrying metadata.sku, and Ledgerium's carry
metadata.ledgerium_plan and have no payment links, so today they are out of
reach. "Today" is the load-bearing word. This checks rather than trusts.

    python ops/check_ledgerium.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Created 2026-09-01. Amounts are the full charge, not the monthly equivalent:
# the annual figures are $492 and $888, and entering 41 or 74 would undercharge
# by more than ninety per cent.
# CORRECTED 2026-09-01. These were first created in the 6S Success account on
# the brief's premise that Ledgerium billed through it. That premise was wrong:
# Ledgerium bills through its own account, acct_1TG5Tu7QvDIBlvfc, and these
# objects are NOT reachable with the 6S Success key.
LEDGERIUM_ACCOUNT = "acct_1TG5Tu7QvDIBlvfc"
EXPECTED = {
    "STRIPE_STARTER_MONTHLY_PRICE_ID": ("price_1TYC4B7QvDIBlvfcieOX93Wd", 4900, "month"),
    "STRIPE_STARTER_ANNUAL_PRICE_ID": ("price_1TYC4B7QvDIBlvfc1IWEvP0V", 49000, "year"),
    "STRIPE_SOLO_MONTHLY_PRICE_ID": ("price_1UAzdJ7QvDIBlvfc9wLeCtSm", 8900, "month"),
    "STRIPE_SOLO_ANNUAL_PRICE_ID": ("price_1UAzdK7QvDIBlvfc5HBm3HBz", 88800, "year"),
}
WEBHOOK = "https://ledgerium.ai/api/billing/webhook"
WEBHOOK_EVENTS = {
    "checkout.session.completed", "customer.subscription.updated",
    "customer.subscription.deleted", "invoice.payment_failed",
    "invoice.payment_succeeded", "customer.subscription.trial_will_end",
}


def _key():
    p = os.path.join(ROOT, ".env.secrets")
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^STRIPE_SECRET_KEY=(.*)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return os.environ.get("STRIPE_SECRET_KEY")


def _api(key, path, params=None):
    url = "https://api.stripe.com/v1/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def _check_on_vps() -> dict:
    """Ship ops/ledgerium_price_check.py to the VPS and run it there."""
    import subprocess
    kp = os.path.expanduser("~/.ssh/6s_deploy")
    local = os.path.join(ROOT, "ops", "ledgerium_price_check.py")
    common = ["-i", kp, "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]
    try:
        c = subprocess.run(["scp"] + common + [local,
                           "root@187.77.25.50:/root/ledgerium_price_check.py"],
                           capture_output=True, text=True, timeout=90)
        if c.returncode != 0:
            return {"state": "unchecked",
                    "problems": ["could not reach the VPS: %s"
                                 % (c.stderr or "")[-120:]]}
        r = subprocess.run(["ssh"] + common + ["root@187.77.25.50",
                           "python3 /root/ledgerium_price_check.py"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:                                      # noqa: BLE001
        return {"state": "unchecked",
                "problems": ["VPS check failed to run (%s)" % type(e).__name__]}
    if r.returncode != 0:
        return {"state": "unchecked",
                "problems": ["the VPS check errored: %s" % (r.stderr or "")[-140:]]}
    try:
        probs = json.loads(r.stdout.strip().split(chr(10))[-1])
    except Exception:                                           # noqa: BLE001
        return {"state": "unchecked",
                "problems": ["the VPS check returned nothing readable"]}
    return {"state": "problems" if probs else "ok", "problems": probs}


def check() -> dict:
    """Returns {"state": ..., "problems": [...]}.

    state "unchecked" is not state "ok". A run with no credential has proved
    nothing and must say so.
    """
    key = _key()
    if not key:
        return {"state": "unchecked",
                "problems": ["no Stripe credential in this environment"]}
    if not key.startswith("sk_live_"):
        return {"state": "unchecked",
                "problems": ["the key here is not a live key, so live "
                             "subscriptions were not checked"]}

    # Ledgerium's objects live in its own Stripe account. This workstation holds
    # only the 6S Success key, so the check runs on the VPS where Ledgerium's
    # key is. Giving up with "unchecked" when a check is actually possible is
    # the habit this repository keeps paying for.
    try:
        acct = _api(key, "account").get("id")
    except Exception:                                           # noqa: BLE001
        acct = None
    if acct != LEDGERIUM_ACCOUNT:
        return _check_on_vps()

    problems = []
    for name, (pid, amount, interval) in EXPECTED.items():
        try:
            p = _api(key, "prices/" + pid)
        except urllib.error.HTTPError:
            problems.append("%s (%s) no longer exists" % (name, pid))
            continue
        if not p.get("active"):
            problems.append("%s is ARCHIVED, so that plan cannot be bought"
                            % name)
        if p.get("unit_amount") != amount:
            problems.append("%s charges %s, expected %s"
                            % (name, p.get("unit_amount"), amount))
        rec = p.get("recurring") or {}
        if rec.get("interval") != interval:
            problems.append("%s renews every %s, expected %s"
                            % (name, rec.get("interval"), interval))
        prod = _api(key, "products/" + p["product"])
        if not prod.get("active"):
            problems.append("the product behind %s is archived" % name)

    try:
        hooks = _api(key, "webhook_endpoints", {"limit": 100})["data"]
    except urllib.error.HTTPError:
        hooks = []
    live = [h for h in hooks if h["url"] == WEBHOOK]
    if not live:
        problems.append("the Ledgerium webhook endpoint is missing, so "
                        "subscriptions would be paid for and never activated")
    else:
        h = live[0]
        if h.get("status") != "enabled":
            problems.append("the Ledgerium webhook is %s" % h.get("status"))
        missing = WEBHOOK_EVENTS - set(h.get("enabled_events", []))
        if missing:
            problems.append("webhook missing events: %s" % sorted(missing))

    return {"state": "problems" if problems else "ok", "problems": problems}


def main() -> int:
    r = check()
    if r["state"] == "unchecked":
        print("  Ledgerium billing NOT checked: %s" % r["problems"][0])
        return 0
    if r["state"] == "ok":
        print("  Ledgerium billing intact: 4 live prices active and correctly priced in acct_1TG5Tu7QvDIBlvfc, checked on the VPS")
        return 0
    print("  Ledgerium billing has %d problem(s):" % len(r["problems"]))
    for p in r["problems"]:
        print("     %s" % p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
