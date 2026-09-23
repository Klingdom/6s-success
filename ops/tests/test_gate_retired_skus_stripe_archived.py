#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_retired_skus_stripe_archived() actually goes
non-empty when a repository-retired SKU has never been confirmed archived
in Stripe, and stays silent once ops/retire_stripe_skus.py's own ledger
says otherwise.

WHY THIS EXISTS
---------------
Commit 147179c6 retired 6 Area Bundles and 15 Situation Kits on the
repository side (2026-09-22) and said plainly that Stripe archival stayed
open. Nothing named that gap again anywhere a human would see it before
this gate: not OWNER-ACTIONS.md, not the dashboard, not a preflight
warning, only ops/retire_stripe_skus.py's own docstring. This test proves
the gate this cycle added can actually go red on the real shape of that
defect (a SKU present in ops/retired-skus.json with no matching entry in
ops/retired-skus-stripe-status.json) and clears once the ledger records it,
using temp files so it never touches the real repository ledger.

Run:  python ops/tests/test_gate_retired_skus_stripe_archived.py
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def _write(d, name, obj):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return p


def case_no_status_file_warns_for_every_sku():
    with tempfile.TemporaryDirectory() as d:
        skus_fp = _write(d, "retired-skus.json", {
            "skus": [{"sku": "AB-WET-ROOMS"}, {"sku": "KIT-NEW-BABY"}]})
        status_fp = os.path.join(d, "no-such-status.json")
        preflight.WARN.clear()
        preflight.gate_retired_skus_stripe_archived(skus_fp, status_fp)
        assert len(preflight.WARN) == 1, preflight.WARN
        gate, msg = preflight.WARN[0]
        assert gate == "retired-skus-stripe", gate
        assert "2 of 2" in msg, msg
        assert "AB-WET-ROOMS" in msg and "KIT-NEW-BABY" in msg, msg


def case_one_missing_names_only_that_one():
    with tempfile.TemporaryDirectory() as d:
        skus_fp = _write(d, "retired-skus.json", {
            "skus": [{"sku": "AB-WET-ROOMS"}, {"sku": "KIT-NEW-BABY"}]})
        status_fp = _write(d, "retired-skus-stripe-status.json", {
            "archived": {"AB-WET-ROOMS": "2026-09-22T00:00:00Z"}})
        preflight.WARN.clear()
        preflight.gate_retired_skus_stripe_archived(skus_fp, status_fp)
        assert len(preflight.WARN) == 1, preflight.WARN
        msg = preflight.WARN[0][1]
        assert "1 of 2" in msg, msg
        assert "KIT-NEW-BABY" in msg, msg
        assert "AB-WET-ROOMS" not in msg, msg


def case_all_archived_is_silent():
    with tempfile.TemporaryDirectory() as d:
        skus_fp = _write(d, "retired-skus.json", {
            "skus": [{"sku": "AB-WET-ROOMS"}, {"sku": "KIT-NEW-BABY"}]})
        status_fp = _write(d, "retired-skus-stripe-status.json", {"archived": {
            "AB-WET-ROOMS": "2026-09-22T00:00:00Z",
            "KIT-NEW-BABY": "2026-09-22T00:00:00Z",
        }})
        preflight.WARN.clear()
        preflight.gate_retired_skus_stripe_archived(skus_fp, status_fp)
        assert preflight.WARN == [], preflight.WARN


def case_no_retired_skus_file_is_silent():
    preflight.WARN.clear()
    preflight.gate_retired_skus_stripe_archived("/no/such/file.json", "/no/such/status.json")
    assert preflight.WARN == [], preflight.WARN


def case_record_archived_round_trips_through_retire_stripe_skus():
    import retire_stripe_skus as R
    with tempfile.TemporaryDirectory() as d:
        status_fp = os.path.join(d, "retired-skus-stripe-status.json")
        old = R.STATUS_PATH
        R.STATUS_PATH = status_fp
        try:
            R.record_archived({"AB-WET-ROOMS"})
            R.record_archived({"KIT-NEW-BABY"})
        finally:
            R.STATUS_PATH = old
        data = json.load(open(status_fp, encoding="utf-8"))
        assert set(data["archived"]) == {"AB-WET-ROOMS", "KIT-NEW-BABY"}, data


def case_live_repository_state_today():
    """The gate must agree with the two real files, whatever they currently say.

    This case used to assert "44 of 65 still pending", which was the true
    state on the morning it was written and became false hours later when a
    session with a Stripe credential archived the rest. A test that hardcodes
    a transient snapshot fails as a REWARD for finishing the work it was
    tracking, which trains people to edit the test rather than read it.

    So it re-derives the expectation from ops/retired-skus.json and
    ops/retired-skus-stripe-status.json instead: if anything is unconfirmed
    the gate must say so and name the count, and if nothing is it must stay
    silent. The fixed-number cases above still pin the arithmetic itself.
    """
    skus_fp = os.path.join(ROOT, "ops", "retired-skus.json")
    status_fp = os.path.join(ROOT, "ops", "retired-skus-stripe-status.json")

    retired = {x["sku"] for x in json.load(io.open(skus_fp, encoding="utf-8"))
               ["skus"] if isinstance(x, dict) and x.get("sku")}
    confirmed = set()
    if os.path.exists(status_fp):
        confirmed = set(json.load(io.open(status_fp, encoding="utf-8"))
                        .get("archived") or {})
    pending = retired - confirmed

    preflight.WARN.clear()
    preflight.gate_retired_skus_stripe_archived(skus_fp, status_fp)

    if pending:
        assert len(preflight.WARN) == 1, (pending, preflight.WARN)
        msg = preflight.WARN[0][1]
        assert "%d of %d" % (len(pending), len(retired)) in msg, msg
        assert "retire_stripe_skus.py --apply" in msg, msg
        for done in sorted(confirmed)[:3]:
            assert done not in msg, (done, msg)
    else:
        assert not preflight.WARN, (
            "every retired SKU is confirmed archived, so the gate should be "
            "silent, but it warned: %r" % preflight.WARN)

def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
