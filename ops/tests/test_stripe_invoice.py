#!/usr/bin/env python3
"""
Prove stripe_invoice.py's live-account guard covers --draft, not only --send.

Found 2026-09-06, cold-reading the money-domain ops/*.py tier: the module's
own docstring promises "It refuses to run against a live key unless
STRIPE_ALLOW_LIVE=1, the same guard the product and link scripts use", but
main()'s actual guard was `if live and a.send and ...`. stripe_catalog.py and
stripe_dedupe.py, the scripts the docstring names as using "the same guard",
gate on any write (apply_it), not on a final send step. A bare --draft run
against a live key with no STRIPE_ALLOW_LIVE set still POSTs a real customer,
a real invoice and a real invoice item to the live Stripe account; only the
email send was ever gated. Fixed by moving the guard above the send check so
it covers the whole function, matching the sibling scripts and the docstring.

Run:  python ops/tests/test_stripe_invoice.py
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_invoice as si                                   # noqa: E402


def args(**kw):
    base = dict(draft=True, send=False, email="a@b.com", name="Acme",
                item="Corporate Lean 6S, one day onsite", amount=3500.0,
                days=14)
    base.update(kw)
    return argparse.Namespace(**base)


def main() -> int:
    fails = []
    calls = []

    def fake_call(path, k, params=None, method="GET"):
        calls.append(path)
        raise AssertionError("call() reached the network in a case the "
                              "guard should have stopped")

    orig_key, orig_call = si.key, si.call

    # --draft against a live key, no STRIPE_ALLOW_LIVE: must refuse before
    # any write, not only before a send.
    si.key = lambda: "sk_live_abc123"
    si.call = fake_call
    os.environ.pop("STRIPE_ALLOW_LIVE", None)
    try:
        rc = si.main(args(draft=True, send=False))
    except AssertionError as e:
        fails.append(f"--draft/live/unset reached the network: {e}")
    else:
        if rc == 0:
            fails.append("--draft/live/unset returned success; should refuse")
        if calls:
            fails.append(f"--draft/live/unset made API call(s): {calls}")

    # --send against a live key, no STRIPE_ALLOW_LIVE: must still refuse
    # (this was already true before the fix; keep it proven).
    calls.clear()
    try:
        rc = si.main(args(draft=False, send=True))
    except AssertionError as e:
        fails.append(f"--send/live/unset reached the network: {e}")
    else:
        if rc == 0:
            fails.append("--send/live/unset returned success; should refuse")
        if calls:
            fails.append(f"--send/live/unset made API call(s): {calls}")

    # A test-mode key needs no flag at all, draft or send: the guard is only
    # about LIVE accounts.
    si.key = lambda: "sk_test_abc123"
    calls.clear()
    seen = {"customers": 0}

    def stub_call(path, k, params=None, method="GET"):
        calls.append(path)
        if path == "customers" and method == "GET":
            return 200, {"data": []}
        if path == "customers" and method == "POST":
            return 200, {"id": "cus_1"}
        if path == "invoices":
            return 200, {"id": "in_1"}
        if path == "invoiceitems":
            return 200, {"id": "ii_1"}
        raise AssertionError(f"unexpected call: {path} {method}")

    si.call = stub_call
    rc = si.main(args(draft=True, send=False))
    if rc != 0:
        fails.append("--draft/test-mode with no STRIPE_ALLOW_LIVE was refused")
    if "customers" not in calls or "invoices" not in calls:
        fails.append(f"--draft/test-mode did not reach the API: {calls}")

    # STRIPE_ALLOW_LIVE=1 unblocks a live run (draft still doesn't send).
    si.key = lambda: "sk_live_abc123"
    calls.clear()
    os.environ["STRIPE_ALLOW_LIVE"] = "1"
    try:
        rc = si.main(args(draft=True, send=False))
        if rc != 0:
            fails.append("--draft/live with STRIPE_ALLOW_LIVE=1 was refused")
        if "customers" not in calls:
            fails.append(f"--draft/live/allowed did not reach the API: {calls}")
    finally:
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        si.key, si.call = orig_key, orig_call

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_invoice.py live-account guard: 4 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
