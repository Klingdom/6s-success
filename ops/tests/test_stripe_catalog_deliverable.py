"""Prove deliverable() refuses BK-BUNDLE if any one of its three files is
missing, not just the print pack.

ops/stripe_fulfil.py's DELIVERY["BK-BUNDLE"] sends three files (the EPUB, the
manual and the print pack) and refuses to ship unless every one exists. Until
this fix, ops/stripe_catalog.py's SELLABLE["BK-BUNDLE"]["deliverable"] named
only the print pack, so deliverable() (the gate on creating or keeping a live
payment link) would call the SKU deliverable while the EPUB or manual was
missing, and an order would stall at fulfilment time instead of the link
being refused or pulled first. Found by a 2026-09-22 PM check-in cold-reading
the newest paid SKU's fulfilment path; no live defect at the time (all three
files existed), but the gap was real and latent.

Run:  python ops/tests/test_stripe_catalog_deliverable.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import stripe_catalog                                           # noqa: E402


def _spec(deliverable):
    return dict(kind="digital", deliverable=deliverable)


def case_single_path_existing_file():
    ok, why = stripe_catalog.deliverable("X", {}, _spec(__file__))
    assert ok and why == "", (ok, why)


def case_single_path_missing_file():
    ok, why = stripe_catalog.deliverable("X", {}, _spec("/no/such/file.html"))
    assert not ok and "file not built" in why, (ok, why)


def case_list_all_present():
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "a.html")
        b = os.path.join(d, "b.epub")
        open(a, "w").close()
        open(b, "w").close()
        ok, why = stripe_catalog.deliverable("X", {}, _spec([a, b]))
        assert ok and why == "", (ok, why)


def case_list_one_missing_refuses():
    """The regression case: a bundle SKU must refuse if ANY of its files is
    gone, not just when all are gone or only the first is checked."""
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "a.html")
        open(a, "w").close()
        missing = os.path.join(d, "b-missing.epub")
        ok, why = stripe_catalog.deliverable("X", {}, _spec([a, missing]))
        assert not ok, "a missing second file must refuse the SKU as deliverable"
        assert "b-missing.epub" in why, why


def case_bk_bundle_matches_stripe_fulfil_exactly():
    """The real, live SELLABLE entry must name the same files, in the same
    order, as stripe_fulfil.DELIVERY actually sends. A generator/sibling
    drift here is exactly the class this fix exists to prevent."""
    import stripe_fulfil
    catalog_files = stripe_catalog.SELLABLE["BK-BUNDLE"]["deliverable"]
    assert isinstance(catalog_files, list), \
        "BK-BUNDLE must name a list of files, not a single path"
    fulfil_files = stripe_fulfil.DELIVERY["BK-BUNDLE"]["files"]
    assert catalog_files == fulfil_files, (catalog_files, fulfil_files)


def case_bk_bundle_currently_deliverable():
    """Live check against the real repo tree: all three files exist today."""
    spec = stripe_catalog.SELLABLE["BK-BUNDLE"]
    ok, why = stripe_catalog.deliverable("BK-BUNDLE", {}, spec)
    assert ok, why


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
    print("stripe_catalog.deliverable(): %d case(s) passed" % len(cases))
    return 0


if __name__ == "__main__":
    sys.exit(main())
