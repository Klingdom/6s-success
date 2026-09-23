#!/usr/bin/env python3
"""
Prove ops/retire_stripe_skus.py's --apply run records EVERY retired SKU as
Stripe-clean, not only the ones it had to deactivate this run.

WHY THIS EXISTS
---------------
Found 2026-09-22 cold-reading the script the same day gate_retired_skus_
stripe_archived was added to read its ledger. `main()`'s apply path built
`touched` from only the SKUs it actually posted a deactivation for. A SKU
already carrying zero active Stripe objects (already archived earlier, or
never had one under this tag) is correctly absent from `links`/`prods`
(both are filtered from the live-active set), so it was never added to
`touched` either, and so it was never recorded in
ops/retired-skus-stripe-status.json even though Stripe already agrees it
is clean.

That is not cosmetic: gate_retired_skus_stripe_archived's warning is by
SKU name, and it would keep naming an already-clean SKU as "never
confirmed" forever, because a SKU with zero active objects can never
re-enter `links`/`prods` on any future run either. The only path that ever
recorded such a SKU was the separate all-clean-at-once branch a few lines
above, which requires every retired SKU to be simultaneously clean, an
all-or-nothing condition a mixed run never satisfies.

This test simulates a mixed run: three retired SKUs, one ("KIT-B") still
carrying an active Stripe link, the other two already clean. `--apply`
should deactivate KIT-B and record all three as confirmed clean.

Run:  python ops/tests/test_retire_stripe_skus_partial_ledger.py
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import stripe_catalog                                            # noqa: E402
import retire_stripe_skus as R                                   # noqa: E402

bad = []

with tempfile.TemporaryDirectory() as d:
    status_fp = os.path.join(d, "retired-skus-stripe-status.json")

    skus = {"KIT-A", "KIT-B", "KIT-C"}
    posted = []

    def fake_list_all(kind, params=None):
        if kind == "payment_links":
            return [{"id": "plink_b", "url": "https://buy.stripe.com/xyz",
                      "metadata": {"sku": "KIT-B"}}]
        if kind == "products":
            return []
        return []

    def fake_call(method, path, params=None):
        posted.append((method, path, params))
        return {"data": []}

    stripe_catalog.list_all = fake_list_all
    stripe_catalog.call = fake_call
    R.retired_skus = lambda: skus
    R.live_is_clean = lambda skus, link_ids: (True, "0 references, fake")
    R.STATUS_PATH = status_fp

    os.environ["STRIPE_ALLOW_LIVE"] = "1"
    old_argv = sys.argv
    sys.argv = ["retire_stripe_skus.py", "--apply"]
    try:
        rc = R.main()
    finally:
        sys.argv = old_argv
        del os.environ["STRIPE_ALLOW_LIVE"]

    if rc != 0:
        bad.append("main() returned %r, expected 0" % rc)

    deactivated = [p for p in posted
                   if p[1] == "payment_links/plink_b"
                   and (p[2] or {}).get("active") is False]
    if len(deactivated) != 1:
        bad.append("KIT-B's live link was not deactivated: %r" % posted)

    if not os.path.exists(status_fp):
        bad.append("no ledger was written at all")
    else:
        recorded = set(json.load(io.open(status_fp, encoding="utf-8"))
                       .get("archived", {}).keys())
        missing = skus - recorded
        if missing:
            bad.append("already-clean SKU(s) never recorded as archived "
                       "in a mixed run: %s (recorded only %s)"
                       % (sorted(missing), sorted(recorded)))

if bad:
    for b in bad:
        print("  FAIL %s" % b)
    raise SystemExit(1)
print("  ok  a mixed --apply run (one SKU deactivated, two already clean) "
      "records all three as confirmed clean in the ledger")
