#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_owner_actions_retired_sku_count_current()
actually fails when OWNER-ACTIONS.md item 1h's cited pending-SKU count
disagrees with the live count, and stays silent once they agree.

WHY THIS EXISTS
---------------
Item 1h (added 2026-09-22, the day gate_retired_skus_stripe_archived
shipped) told Phil to expect "36 SKUs from the original 2026-08-21
retirement". D-024 (commit acb343cb, 2026-09-23) retired 8 more SKUs, the
7 Kitchen zone packs and the Kitchen room pack, into the same
ops/retired-skus.json list; none of the 8 is Stripe-confirmed, so the real
pending count moved to 44 that day. D-024's own commit message says it
corrected the catalogue count everywhere it was cited, but OWNER-ACTIONS.md
item 1h was never one of the files it touched, because nothing checked this
specific number against the live ledger. Found cold-reading the same files
this test now covers; fixed the row and added this gate the same cycle so
the next SKU added to the same list cannot leave item 1h stale again
unnoticed.

Run:  python ops/tests/test_gate_owner_actions_retired_sku_count_current.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def _write_text(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def _write_json(d, name, obj):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return p


def _oa_text(n):
    return ("| **1h** | Run `...` for the %d SKUs still unconfirmed in "
            "Stripe | 2 min | filler |" % n)


def case_stale_count_fails():
    """The exact real shape: item 1h still says 36 after an 8-SKU addition."""
    with tempfile.TemporaryDirectory() as d:
        oa_fp = _write_text(d, "OWNER-ACTIONS.md", _oa_text(36))
        skus_fp = _write_json(d, "retired-skus.json", {
            "skus": [{"sku": "SKU-%d" % i} for i in range(44)]})
        status_fp = os.path.join(d, "no-such-status.json")
        preflight.FAIL.clear()
        preflight.gate_owner_actions_retired_sku_count_current(
            oa_fp, skus_fp, status_fp)
        assert len(preflight.FAIL) == 1, preflight.FAIL
        gate, msg = preflight.FAIL[0]
        assert gate == "owner-actions-sku-count-current", gate
        assert "says 36" in msg, msg
        assert "shows 44" in msg, msg


def case_correct_count_is_silent():
    with tempfile.TemporaryDirectory() as d:
        oa_fp = _write_text(d, "OWNER-ACTIONS.md", _oa_text(44))
        skus_fp = _write_json(d, "retired-skus.json", {
            "skus": [{"sku": "SKU-%d" % i} for i in range(44)]})
        status_fp = os.path.join(d, "no-such-status.json")
        preflight.FAIL.clear()
        preflight.gate_owner_actions_retired_sku_count_current(
            oa_fp, skus_fp, status_fp)
        assert preflight.FAIL == [], preflight.FAIL


def case_archived_skus_reduce_the_live_pending_count():
    with tempfile.TemporaryDirectory() as d:
        oa_fp = _write_text(d, "OWNER-ACTIONS.md", _oa_text(2))
        skus_fp = _write_json(d, "retired-skus.json", {
            "skus": [{"sku": "AB-WET-ROOMS"}, {"sku": "KIT-NEW-BABY"},
                      {"sku": "ZP-KITCHE-1"}]})
        status_fp = _write_json(d, "retired-skus-stripe-status.json", {
            "archived": {"AB-WET-ROOMS": "2026-09-22T00:00:00Z"}})
        preflight.FAIL.clear()
        preflight.gate_owner_actions_retired_sku_count_current(
            oa_fp, skus_fp, status_fp)
        # 2 SKUs (KIT-NEW-BABY, ZP-KITCHE-1) are actually pending, matching
        # the cited 2, so this must stay silent.
        assert preflight.FAIL == [], preflight.FAIL


def case_row_absent_is_silent():
    """A rewrite that drops the row entirely must not block preflight for a
    reason this gate cannot fix here, the same convention every sibling
    cross-document check uses."""
    with tempfile.TemporaryDirectory() as d:
        oa_fp = _write_text(d, "OWNER-ACTIONS.md", "nothing about SKUs here")
        skus_fp = _write_json(d, "retired-skus.json", {
            "skus": [{"sku": "SKU-1"}]})
        preflight.FAIL.clear()
        preflight.gate_owner_actions_retired_sku_count_current(oa_fp, skus_fp, "")
        assert preflight.FAIL == [], preflight.FAIL


def case_missing_files_is_silent():
    preflight.FAIL.clear()
    preflight.gate_owner_actions_retired_sku_count_current(
        "/no/such/OWNER-ACTIONS.md", "/no/such/retired-skus.json", "/no/such/status.json")
    assert preflight.FAIL == [], preflight.FAIL


def case_live_repository_state_today():
    """The real, honest state right now: item 1h says 44, and the live
    ledger (65 retired, 21 confirmed archived) also derives 44 pending. If a
    future SKU is added to ops/retired-skus.json without updating item 1h,
    this case documents the number that must move too."""
    oa_fp = os.path.join(ROOT, "OWNER-ACTIONS.md")
    skus_fp = os.path.join(ROOT, "ops", "retired-skus.json")
    status_fp = os.path.join(ROOT, "ops", "retired-skus-stripe-status.json")
    preflight.FAIL.clear()
    preflight.gate_owner_actions_retired_sku_count_current(oa_fp, skus_fp, status_fp)
    assert preflight.FAIL == [], preflight.FAIL


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
