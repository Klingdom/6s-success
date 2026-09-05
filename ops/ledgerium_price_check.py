"""Check Ledgerium's live prices and webhook. Runs ON THE VPS, where its key lives.

Shipped to the server and executed there by ops/check_ledgerium.py, rather than
embedded as an escaped string in an ssh command. The escaped-string version was
written twice and mangled twice, because a heredoc eats a backslash level and
turns a literal newline escape into a real newline. A file needs no escapes.

This is the single source of truth for EXPECTED/WEBHOOK/WEBHOOK_EVENTS.
ops/check_ledgerium.py imports these rather than keeping its own copy, because
this file is the one that actually runs against Ledgerium's real key in every
realistic invocation: check_ledgerium.check() only checks locally when the
ambient Stripe key IS Ledgerium's own, which never happens by design (that key
lives only at /docker/ledgerium/.env on the VPS, never in this repository's
environment). A local key mismatch here would have gone unnoticed for as long
as nobody compared the two files by hand.
"""
import json
import re
import urllib.parse
import urllib.request

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


def _read_key(path="/docker/ledgerium/.env"):
    key = None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^STRIPE_SECRET_KEY=(.*)$", line.strip())
        if m:
            key = m.group(1)
    return key


def _api(key, path, params=None):
    url = "https://api.stripe.com/v1/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def check(key) -> list:
    """Returns a list of problem strings. Empty means everything checked out.

    Covers the same ground as check_ledgerium.py's own direct-key branch
    (prices, their products, the webhook): this is the path that actually
    runs with Ledgerium's real key, so it cannot afford to check less.
    """
    problems = []
    if not key:
        problems.append("no STRIPE_SECRET_KEY in /docker/ledgerium/.env")
        return problems

    for name, (pid, amount, interval) in EXPECTED.items():
        try:
            d = _api(key, "prices/" + pid)
        except Exception:                                        # noqa: BLE001
            problems.append(name + " could not be read from Stripe")
            continue
        if not d.get("active"):
            problems.append(name + " is ARCHIVED, so that plan cannot be bought")
        if d.get("unit_amount") != amount:
            problems.append("%s charges %s, expected %s"
                            % (name, d.get("unit_amount"), amount))
        if (d.get("recurring") or {}).get("interval") != interval:
            problems.append("%s renews on the wrong interval" % name)
        try:
            prod = _api(key, "products/" + d["product"])
            if not prod.get("active"):
                problems.append("the product behind %s is archived" % name)
        except Exception:                                        # noqa: BLE001
            problems.append(name + "'s product could not be read from Stripe")

    try:
        hooks = _api(key, "webhook_endpoints", {"limit": 100})["data"]
    except Exception:                                            # noqa: BLE001
        problems.append("the Ledgerium webhook endpoints could not be read "
                        "from Stripe")
        hooks = None
    if hooks is not None:
        live = [h for h in hooks if h["url"] == WEBHOOK]
        if not live:
            problems.append("the Ledgerium webhook endpoint is missing, so "
                            "subscriptions would be paid for and never "
                            "activated")
        else:
            h = live[0]
            if h.get("status") != "enabled":
                problems.append("the Ledgerium webhook is %s" % h.get("status"))
            missing = WEBHOOK_EVENTS - set(h.get("enabled_events", []))
            if missing:
                problems.append("webhook missing events: %s" % sorted(missing))

    return problems


def main():
    print(json.dumps(check(_read_key())))


if __name__ == "__main__":
    main()
