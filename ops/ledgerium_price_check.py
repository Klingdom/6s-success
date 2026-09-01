"""Check Ledgerium's live prices. Runs ON THE VPS, where its key lives.

Shipped to the server and executed there by ops/check_ledgerium.py, rather than
embedded as an escaped string in an ssh command. The escaped-string version was
written twice and mangled twice, because a heredoc eats a backslash level and
turns a literal newline escape into a real newline. A file needs no escapes.
"""
import json
import re
import sys
import urllib.request

EXPECTED = {
    "STRIPE_STARTER_MONTHLY_PRICE_ID": ("price_1TYC4B7QvDIBlvfcieOX93Wd", 4900, "month"),
    "STRIPE_STARTER_ANNUAL_PRICE_ID": ("price_1TYC4B7QvDIBlvfc1IWEvP0V", 49000, "year"),
    "STRIPE_SOLO_MONTHLY_PRICE_ID": ("price_1UAzdJ7QvDIBlvfc9wLeCtSm", 8900, "month"),
    "STRIPE_SOLO_ANNUAL_PRICE_ID": ("price_1UAzdK7QvDIBlvfc5HBm3HBz", 88800, "year"),
}

key = None
for line in open("/docker/ledgerium/.env", encoding="utf-8"):
    m = re.match(r"^STRIPE_SECRET_KEY=(.*)$", line.strip())
    if m:
        key = m.group(1)

problems = []
if not key:
    problems.append("no STRIPE_SECRET_KEY in /docker/ledgerium/.env")
else:
    for name, (pid, amount, interval) in EXPECTED.items():
        try:
            req = urllib.request.Request(
                "https://api.stripe.com/v1/prices/" + pid,
                headers={"Authorization": "Bearer " + key})
            d = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            problems.append(name + " could not be read from Stripe")
            continue
        if not d.get("active"):
            problems.append(name + " is ARCHIVED, so that plan cannot be bought")
        if d.get("unit_amount") != amount:
            problems.append("%s charges %s, expected %s"
                            % (name, d.get("unit_amount"), amount))
        if (d.get("recurring") or {}).get("interval") != interval:
            problems.append("%s renews on the wrong interval" % name)

print(json.dumps(problems))
