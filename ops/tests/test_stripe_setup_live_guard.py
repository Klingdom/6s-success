#!/usr/bin/env python3
"""
Prove stripe_setup.py's live-write guard message matches what it actually does.

Found 2026-09-30, cold-reading the 2026-09-25-dated ops/*.py tier
(ops/cold_read_ledger.py) per CLAUDE.md step 5d. `main()` printed "Refusing
to create live products..." on every live+--apply run, before checking
STRIPE_ALLOW_LIVE, then only returned 1 (actually refusing) when the flag
was unset. With STRIPE_ALLOW_LIVE=1 set, the same run printed the refusal
message and then proceeded to create the products anyway: the message and
the behaviour disagreed. Fixed by folding the flag check into the same `if`
that guards the print, the pattern ops/stripe_links.py already used
correctly (see test_stripe_links.py).

Run:  python ops/tests/test_stripe_setup_live_guard.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_setup as ss                                      # noqa: E402


def main() -> int:
    fails = []
    calls = []
    orig_creds, orig_call = ss.creds, ss.call

    def fake_call(path, key, params=None, method="GET"):
        calls.append(path)
        raise AssertionError("call() reached the network in a case the "
                              "guard should have stopped")

    def stub_call(path, key, params=None, method="GET"):
        calls.append(path)
        if path == "prices" and method == "GET":
            return 200, {"data": []}
        if path == "products":
            return 200, {"id": "prod_fake", "name": "fake"}
        if path == "prices":
            return 200, {"id": "price_fake"}
        raise AssertionError(f"unexpected call: {path} {method}")

    try:
        # live + --apply, no STRIPE_ALLOW_LIVE: must refuse, print the
        # refusal, and never touch the network.
        ss.creds = lambda: "sk_live_abc123"
        ss.call = fake_call
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        import io
        import contextlib
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = ss.main(True)
        except AssertionError as e:
            fails.append(f"--apply/live/unset reached the network: {e}")
        else:
            if rc != 1:
                fails.append("--apply/live/unset did not return 1")
            if "Refusing" not in buf.getvalue():
                fails.append("--apply/live/unset printed no refusal message")
            if calls:
                fails.append(f"--apply/live/unset made API call(s): {calls}")

        # live + --apply, STRIPE_ALLOW_LIVE=1: must NOT print the refusal
        # message, since it is not refusing.
        calls.clear()
        ss.call = stub_call
        os.environ["STRIPE_ALLOW_LIVE"] = "1"
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            ss.main(True)
        if "Refusing" in buf2.getvalue():
            fails.append("--apply/live/allowed still printed the refusal "
                         "message while proceeding to write")
        if "prices" not in calls:
            fails.append(f"--apply/live/allowed did not reach the API: {calls}")

        # --plan (apply_it=False) against a live key: read-only, never
        # refused, no refusal text either.
        calls.clear()
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        buf3 = io.StringIO()
        with contextlib.redirect_stdout(buf3):
            rc = ss.main(False)
        if rc != 0:
            fails.append("--plan/live/unset was refused; --plan changes nothing")
        if "Refusing" in buf3.getvalue():
            fails.append("--plan/live printed the live-apply refusal message")
    finally:
        os.environ.pop("STRIPE_ALLOW_LIVE", None)
        ss.creds, ss.call = orig_creds, orig_call

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("stripe_setup.py live-write guard message: 3 case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
