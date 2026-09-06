#!/usr/bin/env python3
"""
Prove stripe_fulfil.deliver()'s dry-run branch actually runs, without a
Stripe key or a real order.

Found 2026-09-06: deliver()'s `if not send:` preview line referenced a
variable named `path`, which this function never defines (only `paths`, the
list, and `p`, the loop variable from building it). Every real order ever
processed here has been either already fulfilled or delivered with --send,
which skips this line entirely, so the crash has never been seen: the
"what would happen" preview mode named first in the module's own usage
docstring has never actually run to completion in this repository. Same
"branch nothing has ever exercised" shape this log has already found and
fixed twice this week (check_live_links.check(), dashboard.status_of()),
one file further down the money path: this is the function a paying
customer's delivery depends on.

Run:  python ops/tests/test_stripe_fulfil.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_fulfil as sf                                    # noqa: E402


def session(email="buyer@example.com", name="Buyer", sku="BK-EB"):
    return {"customer_details": {"email": email, "name": name},
            "amount_total": 999, "metadata": {"sku": sku}}


def main() -> int:
    fails = []

    # The dry-run preview for a single-file product must not raise, and must
    # actually name the file rather than crash on the undefined `path`.
    try:
        r = sf.deliver(session(), "BK-EB", sf.DELIVERY["BK-EB"], send=False)
    except Exception as e:
        fails.append(f"single-file dry run raised {type(e).__name__}: {e}")
    else:
        if not r.startswith("WOULD SEND"):
            fails.append(f"single-file dry run did not preview: {r!r}")
        elif "6S-Success-Home-Edition.epub" not in r:
            fails.append(f"single-file dry run did not name its file: {r!r}")

    # A bundle ships several files in one order. The preview has to name all
    # of them, or a shortfall here is invisible until the real send.
    try:
        r = sf.deliver(session(sku="BK-BUNDLE"), "BK-BUNDLE",
                        sf.DELIVERY["BK-BUNDLE"], send=False)
    except Exception as e:
        fails.append(f"bundle dry run raised {type(e).__name__}: {e}")
    else:
        want = ["6S-Success-Home-Edition.epub", "micro-zone-manual-publishable.html",
                "6S-Whole-House-Print-Pack.html"]
        missing = [f for f in want if f not in r]
        if missing:
            fails.append(f"bundle dry run did not name every file, missing "
                         f"{missing}: {r!r}")

    # No email on the order must return the "cannot deliver" message rather
    # than reaching the mailer at all, dry run or not.
    r = sf.deliver(session(email=""), "BK-EB", sf.DELIVERY["BK-EB"], send=False)
    if "no customer email" not in r:
        fails.append(f"a blank customer email did not refuse cleanly: {r!r}")

    # A missing deliverable must refuse by name, not attempt to attach a file
    # that is not there.
    fake_spec = dict(sf.DELIVERY["BK-EB"], file="build/does-not-exist.epub")
    r = sf.deliver(session(), "BK-EB", fake_spec, send=False)
    if "file missing" not in r or "does-not-exist.epub" not in r:
        fails.append(f"a missing deliverable did not refuse by name: {r!r}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print(f"stripe_fulfil.deliver() dry-run branch: {4} case(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
