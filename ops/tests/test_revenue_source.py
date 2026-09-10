#!/usr/bin/env python3
"""
Prove the revenue number is read from where the money lands.

WHAT WENT WRONG
---------------
Both revenue readers in ops/dashboard.py asked Stripe for checkout sessions
whose payment_status is "paid". Measured against the live account on
2026-09-10: 100 checkout sessions exist, every one of them "unpaid" and
"expired", and not one within an hour of the real charge.

The money is in the charges endpoint: ch_3U722U6OlZmKL8mF1Hooe, 19.00 dollars,
succeeded, 2026-08-21. That is the only sale this business has ever made, and
the dashboard's revenue row could not see it and never would have. A Payment
Link's session is created when somebody opens the link and expires whether or
not they pay, so a catalogue sold entirely through Payment Links reports zero
forever while taking money.

Revenue is the number this repository is pointed at. An instrument reading the
wrong endpoint reports zero in exactly the situation where being right matters
most, and a wrong zero is indistinguishable from having made no sales.

Everything here runs against a stub: no key, no network, no money.

Run:  python ops/tests/test_revenue_source.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")

CHARGES = {"data": [
    {"id": "ch_ok", "status": "succeeded", "paid": True,
     "amount_captured": 1900, "amount_refunded": 0,
     "billing_details": {"email": "a@example.com"}},
    {"id": "ch_failed", "status": "failed", "paid": False,
     "amount_captured": 9900, "amount_refunded": 0,
     "billing_details": {"email": "b@example.com"}},
    {"id": "ch_refunded", "status": "succeeded", "paid": True,
     "amount_captured": 5000, "amount_refunded": 5000,
     "billing_details": {"email": "c@example.com"}},
]}


class FakeResponse:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def load_reader(src: str):
    """Execute only _stripe_charges, in its own namespace.

    dashboard.py is a script: importing it runs the whole thing and rewrites
    EXECUTIVE-DASHBOARD-LIVE.md. A test that regenerates the deck as a side
    effect of checking one function is a test that changes the thing it is
    inspecting, so only the function under test is compiled here.
    """
    start = src.index("def _stripe_charges")
    end = src.index(chr(10) + "def ", start + 1)
    ns = {"os": os, "json": json, "ROOT": ROOT}
    exec(compile(src[start:end], "dashboard._stripe_charges", "exec"), ns)
    return ns["_stripe_charges"], src[start:end]


def main() -> int:
    fails = []
    src = io.open(os.path.join(OPS, "dashboard.py"), encoding="utf-8").read()
    reader, body = load_reader(src)

    # 1. The URL it actually requests, not what its prose mentions. The
    #    docstring quotes the old endpoint on purpose, to explain the bug, so
    #    matching on prose would fail on the very comment that records it.
    urls = re.findall(r'"(https://api\.stripe\.com/[^"]+)"', body)
    if not urls:
        fails.append("no Stripe URL found in the revenue reader at all")
    for u in urls:
        if "/v1/charges" not in u:
            fails.append("the revenue reader requests %r. Every checkout "
                         "session on this account is unpaid and expired, so "
                         "reading anything but charges reports zero while the "
                         "account holds a real payment" % u)

    # 2. A succeeded charge counts, a failed one does not, a refund nets off.
    import urllib.request
    real_open = urllib.request.urlopen
    real_env = os.environ.get("STRIPE_SECRET_KEY")
    try:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_stub"
        urllib.request.urlopen = lambda *a, **k: FakeResponse(CHARGES)
        gross, payers, count = reader(None)
    finally:
        urllib.request.urlopen = real_open
        if real_env is None:
            os.environ.pop("STRIPE_SECRET_KEY", None)
        else:
            os.environ["STRIPE_SECRET_KEY"] = real_env

    if gross != 19.0:
        fails.append("gross was %r, expected 19.0: a failed charge or a "
                     "refunded one is being counted as revenue" % gross)
    if count != 2:
        fails.append("counted %r succeeded charges, expected 2. The refunded "
                     "one still happened; only its money came back" % count)
    if payers != 2:
        fails.append("counted %r distinct payers, expected 2" % payers)

    # 3. No credential gives None, never zero. Zero is a measurement and None
    #    is an admission, and CI has neither key nor secrets file.
    saved = os.environ.pop("STRIPE_SECRET_KEY", None)
    secrets = os.path.join(ROOT, ".env.secrets")
    moved = secrets + ".test-moved"
    had = os.path.exists(secrets)
    try:
        if had:
            os.rename(secrets, moved)
        blind = reader(None)
    finally:
        if had and os.path.exists(moved):
            os.rename(moved, secrets)
        if saved is not None:
            os.environ["STRIPE_SECRET_KEY"] = saved
    if blind != (None, None, None):
        fails.append("with no credential the reader returned %r. It must "
                     "return None, so the deck prints 'not measured' rather "
                     "than a zero nobody measured" % (blind,))

    for f in fails:
        print("  FAIL  %s" % f)
    if fails:
        print("  %d problem(s)" % len(fails))
    else:
        print("  ok  revenue is read from charges, a failed charge and a "
              "refund are excluded, and no credential reports None not zero")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
