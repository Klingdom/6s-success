#!/usr/bin/env python3
"""
Prove stripe_fulfil.py refuses a live --send without STRIPE_ALLOW_LIVE=1.

Found 2026-10-02, second-pass cold-reading the 2026-09-26-dated ops/*.py
tier (ops/cold_read_ledger.py) per CLAUDE.md step 5d. Every other script
that can write to a live Stripe account (stripe_catalog.py, stripe_dedupe.py,
stripe_invoice.py, retire_stripe_skus.py) refuses a live run without
STRIPE_ALLOW_LIVE=1; stripe_fulfil.py had no such guard at all, despite
--send being able to email a real customer and stamp a real PaymentIntent
on the very first run against a live key. Fixed by adding the same
live()/STRIPE_ALLOW_LIVE check the sibling scripts already use, at the top
of main(), before paid_sessions() ever reaches the network.

Run:  python ops/tests/test_stripe_fulfil_live_guard.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_fulfil as sf                                      # noqa: E402


def main() -> int:
    fails = []
    orig_key, orig_paid = sf.key, sf.paid_sessions
    calls = []

    def fake_paid_sessions(days):
        calls.append(days)
        raise AssertionError("paid_sessions() reached the network in a "
                              "case the guard should have stopped")

    def stub_paid_sessions(days):
        calls.append(days)
        return []

    try:
        # live + --send, no STRIPE_ALLOW_LIVE: must refuse before ever
        # calling paid_sessions (so no network reach, no customer touched).
        sf.key = lambda: "sk_live_abc123"
        sf.paid_sessions = fake_paid_sessions
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        try:
            sf.main(True, 14)
            fails.append("--send/live/unset did not raise SystemExit")
        except AssertionError as e:
            fails.append(f"--send/live/unset reached the network: {e}")
        except SystemExit as e:
            if "Refusing" not in str(e.code):
                fails.append(f"--send/live/unset exit message wrong: {e.code!r}")
        if calls:
            fails.append(f"--send/live/unset made call(s): {calls}")

        # live + --send, STRIPE_ALLOW_LIVE=1: must proceed, no refusal.
        calls.clear()
        sf.paid_sessions = stub_paid_sessions
        os.environ["STRIPE_ALLOW_LIVE"] = "1"
        try:
            rc = sf.main(True, 14)
        except SystemExit as e:
            fails.append(f"--send/live/allowed was refused: {e.code!r}")
        else:
            if rc != 0:
                fails.append("--send/live/allowed did not return 0 on no orders")
            if 14 not in calls:
                fails.append(f"--send/live/allowed never called paid_sessions: {calls}")

        # --send against a TEST key, no STRIPE_ALLOW_LIVE: never refused,
        # since it is not a live account.
        calls.clear()
        sf.key = lambda: "sk_test_abc123"
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        try:
            sf.main(True, 14)
        except SystemExit as e:
            fails.append(f"--send/test/unset was refused: {e.code!r}")
        if 14 not in calls:
            fails.append(f"--send/test/unset never called paid_sessions: {calls}")

        # Dry run (no --send) against a live key, no STRIPE_ALLOW_LIVE:
        # never refused, since a dry run sends nothing.
        calls.clear()
        sf.key = lambda: "sk_live_abc123"
        try:
            sf.main(False, 14)
        except SystemExit as e:
            fails.append(f"dry-run/live/unset was refused: {e.code!r}")
        if 14 not in calls:
            fails.append(f"dry-run/live/unset never called paid_sessions: {calls}")
    finally:
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        sf.key, sf.paid_sessions = orig_key, orig_paid

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_fulfil.py live-send guard: 4 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
