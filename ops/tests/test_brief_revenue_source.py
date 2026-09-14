#!/usr/bin/env python3
"""
The emailed briefs must read revenue from charges, like the dashboard does.

Found 2026-09-14 against the live Stripe account: ops/hourly_brief.py and
ops/roadmap_report.py still summed checkout sessions whose payment_status is
"paid". Payment Link sessions on this account are all "unpaid", including the
one real sale, so the four-hourly email reported "$0 / 30d, 0 sale(s)" while
a $19 charge sat inside the window. dashboard.py was fixed for the identical
defect on 2026-09-10 (ops/tests/test_revenue_source.py); these two readers
were never told.

Stubbed network, no key, no money.

Run:  python ops/tests/test_brief_revenue_source.py
"""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

SESSIONS = {"data": [{"payment_status": "unpaid", "amount_total": 1900},
                     {"payment_status": "unpaid", "amount_total": 900}]}
CHARGES = {"data": [
    {"status": "succeeded", "paid": True, "amount_captured": 1900, "amount_refunded": 0},
    {"status": "failed", "paid": False, "amount_captured": 9900, "amount_refunded": 0},
    {"status": "succeeded", "paid": True, "amount_captured": 5000, "amount_refunded": 5000},
]}


class Resp:
    def __init__(self, payload):
        self.b = json.dumps(payload).encode()

    def read(self):
        return self.b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_urlopen(req, timeout=None):
    url = req.full_url if hasattr(req, "full_url") else req
    path = url.split("/v1/", 1)[1]
    if path.startswith("checkout/sessions"):
        return Resp(SESSIONS)
    if path.startswith("charges"):
        return Resp(CHARGES)
    if path.startswith("payment_links"):
        return Resp({"data": [{"active": True}]})
    if path.startswith("payment_intents"):
        return Resp({"data": []})
    if path.startswith("balance"):
        return Resp({"available": [], "pending": []})
    raise AssertionError("unexpected Stripe path " + path)


def main() -> int:
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_stub"
    real = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    fails = []
    try:
        import hourly_brief as hb
        hb.env = lambda name, default="": os.environ.get(name, default)
        cm = hb.commerce()
        if cm.get("error"):
            fails.append("hourly_brief.commerce errored: %s" % cm["error"])
        else:
            if cm["revenue_30d"] != 19.0:
                fails.append("hourly_brief revenue_30d=%r, want 19.0" % cm["revenue_30d"])
            if cm["paid_30d"] != 1:
                fails.append("hourly_brief paid_30d=%r, want 1" % cm["paid_30d"])

        import roadmap_report as rr
        rr.env = lambda name, default="": os.environ.get(name, default)
        rm = rr.commerce()
        if rm.get("error"):
            fails.append("roadmap_report.commerce errored: %s" % rm["error"])
        else:
            if rm["month_revenue"] != 19.0:
                fails.append("roadmap_report month_revenue=%r, want 19.0" % rm["month_revenue"])
            if rm["month_orders"] != 1:
                fails.append("roadmap_report month_orders=%r, want 1" % rm["month_orders"])
    finally:
        urllib.request.urlopen = real
    for f in fails:
        print("FAIL", f)
    print("ok" if not fails else "%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
