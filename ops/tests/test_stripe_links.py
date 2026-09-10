#!/usr/bin/env python3
"""
Prove stripe_links.py refuses to write to a LIVE account without
STRIPE_ALLOW_LIVE=1.

Found 2026-09-10, cold-reading the money-domain ops/*.py tier per CLAUDE.md
step 5d rather than trusting the file on sight: every other Stripe write tool
in this repository (stripe_catalog.py, stripe_dedupe.py, stripe_invoice.py,
stripe_setup.py) refuses `--apply` against a live secret key unless
STRIPE_ALLOW_LIVE=1 is set. stripe_links.py had no such guard at all: `main()`
printed "Mode: LIVE" and went straight to creating a real payment link. This
is the exact duplicate-checkout shape that once left a live page charging $18
next to an advertised $9.99 (`ROADMAP-2026-2029.md`, `d5226967`): the module's
own two consulting SKUs are now managed under a different identity by
`ops/stripe_catalog.py` (metadata.sku, not this file's lookup_key), so an
`--apply` run against the live key would not update the live checkout, it
would create a second, orphaned one beside it. Fixed by adding the same
`if live and apply_it and STRIPE_ALLOW_LIVE != "1": refuse` guard every
sibling tool already carries, before any network call.

Run:  python ops/tests/test_stripe_links.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_links as sl                                     # noqa: E402


def main() -> int:
    fails = []
    calls = []

    def fake_call(path, k, params=None, method="GET"):
        calls.append(path)
        raise AssertionError("call() reached the network in a case the "
                              "guard should have stopped")

    orig_key, orig_call = sl.key, sl.call

    # --apply against a live key, no STRIPE_ALLOW_LIVE: must refuse before
    # any write, not create a live payment link.
    sl.key = lambda: "sk_live_abc123"
    sl.call = fake_call
    os.environ.pop("STRIPE_ALLOW_LIVE", None)
    try:
        rc = sl.main(True)
    except AssertionError as e:
        fails.append(f"--apply/live/unset reached the network: {e}")
    else:
        if rc == 0:
            fails.append("--apply/live/unset returned success; should refuse")
        if calls:
            fails.append(f"--apply/live/unset made API call(s): {calls}")

    # --plan (apply_it=False) against a live key still needs to be able to
    # read prices/links to report state; the guard must not block reads.
    calls.clear()

    def stub_call(path, k, params=None, method="GET"):
        calls.append(path)
        if path == "prices":
            return 200, {"data": []}
        if path == "payment_links":
            return 200, {"data": []}
        raise AssertionError(f"unexpected call: {path} {method}")

    sl.call = stub_call
    rc = sl.main(False)
    if rc != 0:
        fails.append("--plan/live/unset was refused; --plan changes nothing "
                      "and should still be able to read")
    if "prices" not in calls:
        fails.append(f"--plan/live/unset did not read prices: {calls}")

    # A test-mode key needs no flag at all.
    sl.key = lambda: "sk_test_abc123"
    calls.clear()
    rc = sl.main(True)
    if rc != 0:
        fails.append("--apply/test-mode with no STRIPE_ALLOW_LIVE was refused")
    if "prices" not in calls:
        fails.append(f"--apply/test-mode did not reach the API: {calls}")

    # STRIPE_ALLOW_LIVE=1 unblocks a live --apply run.
    sl.key = lambda: "sk_live_abc123"
    calls.clear()
    os.environ["STRIPE_ALLOW_LIVE"] = "1"
    try:
        rc = sl.main(True)
        if rc != 0:
            fails.append("--apply/live with STRIPE_ALLOW_LIVE=1 was refused")
        if "prices" not in calls:
            fails.append(f"--apply/live/allowed did not reach the API: {calls}")
    finally:
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        sl.key, sl.call = orig_key, orig_call

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_links.py live-account guard: 4 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
