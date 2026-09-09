#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_etsy_listing_valid() catches a real defect and
passes clean on the real, committed Etsy listing package.

Found 2026-09-09: two gaps, fixed together.

1. Nothing wired check_etsy.py into any unattended cycle, the same shape
   gate_kdp_listing_valid already closed for the KDP package: a real check
   existed, passed clean, and nobody ran it.

2. build/listings/verify_zone_claims.py read one hardcoded file per listing,
   so it never opened L1's second, separately delivered file
   (6S-Standards-Pack.pdf) and printed "standards sheet ABSENT" for the
   flagship listing on every run, a false claim about a real, correctly
   bundled file. Fixed to read the real file list from etsy-listings.json and
   to recognise the standalone Standards Pack's own "SHEET n OF 20" heading.
   This gate re-derives that same fact independently, with its own copy of
   the marker patterns, so a future change to verify_zone_claims.py's
   internals cannot silently stop this check from checking anything (see
   case 2 below, which is exactly that regression shape, caught while
   writing this test: importing verify_zone_claims.py's own
   STANDARDS_MARKERS and calling the pre-fix script raised AttributeError,
   which fell into a bare except and only warned).

Run:  python ops/tests/test_gate_etsy_listing_valid.py
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


class _FakeDoc(list):
    def close(self):
        pass


class _FakePage:
    def __init__(self, text):
        self._t = text

    def get_text(self):
        return self._t


class _FakeCheckEtsy:
    fail = []

    @staticmethod
    def main():
        return 0


def _run(open_fn):
    """Run the gate with pymupdf.open and check_etsy.main() stubbed out, so
    only the standards-marker logic under test is exercised, not the real
    files or check_etsy.py's own independent page/card-count checks."""
    old_pymupdf = sys.modules.get("pymupdf")
    old_check_etsy = sys.modules.get("check_etsy")
    sys.modules["pymupdf"] = types.SimpleNamespace(open=open_fn)
    sys.modules["check_etsy"] = _FakeCheckEtsy
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_etsy_listing_valid()
        return list(preflight.FAIL)
    finally:
        if old_pymupdf is not None:
            sys.modules["pymupdf"] = old_pymupdf
        else:
            sys.modules.pop("pymupdf", None)
        if old_check_etsy is not None:
            sys.modules["check_etsy"] = old_check_etsy
        else:
            sys.modules.pop("check_etsy", None)


def main() -> int:
    fails = []

    # 1. Every delivered file carries a recognised standards marker, whether
    #    the "standards that keep" phrase (L2-L5's shape) or the standalone
    #    Standards Pack's own "SHEET n OF 20" heading (L1's shape): clean.
    def all_present(path):
        if path.endswith("6S-Standards-Pack.pdf"):
            return _FakeDoc([_FakePage("ENTRYWAY\n5 ZONES - SHEET 1 OF 20\ntext")])
        if path.endswith("How-to-print-these-cards.pdf"):
            return _FakeDoc([_FakePage("how to print instructions")])
        return _FakeDoc([_FakePage("The standards that keep these zones\ntext")])

    r = _run(all_present)
    if r:
        fails.append("every listing carrying a real standards marker was "
                     "wrongly flagged: %r" % (r,))

    # 2. The exact real-world regression: every delivered file exists, but
    #    none of them contains any recognised standards marker.
    def none_present(path):
        return _FakeDoc([_FakePage("irrelevant content, no marker here")])

    r = _run(none_present)
    if not r or "standards content not found" not in r[0][1]:
        fails.append("all-markers-absent regression not caught by name: %r"
                     % (r,))
    elif "L1-whole-house" not in r[0][1]:
        fails.append("the flagship listing was not named in the failure: %r"
                     % (r,))

    # 3. Only L1 lacks the marker anywhere in its bundle (matching reality:
    #    L1's own main pack file carries no marker either, unlike L2-L5's,
    #    which embed the "standards that keep" header inline). The rest are
    #    fine. Must still fail, and must name L1 specifically, not a
    #    different listing.
    def only_l1_missing(path):
        if path.endswith("6S-Whole-House-Print-Pack.pdf"):
            return _FakeDoc([_FakePage("684 cards, no standards header here")])
        if path.endswith("6S-Standards-Pack.pdf"):
            return _FakeDoc([_FakePage("irrelevant content, no marker here")])
        if path.endswith("How-to-print-these-cards.pdf"):
            return _FakeDoc([_FakePage("how to print instructions")])
        return _FakeDoc([_FakePage("The standards that keep these zones\ntext")])

    r = _run(only_l1_missing)
    if not r or "L1-whole-house" not in r[0][1]:
        fails.append("L1-only regression not caught by name: %r" % (r,))
    if r and any(x in r[0][1] for x in ("L2-kitchen: standards",
                                        "L3-entryway: standards",
                                        "L4-moving-in: standards",
                                        "L5-holiday-hosting: standards")):
        fails.append("a listing with a real marker was wrongly named: %r"
                     % (r,))

    # 4. The real, committed package: clean, with no stubbing at all. This is
    #    what would have caught the original bug: run against the real files,
    #    the pre-fix verify_zone_claims.py's own printed "ABSENT" for L1 was
    #    wrong, and this gate (which never reads that script's output) says
    #    so directly against the real, delivered 6S-Standards-Pack.pdf.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_etsy_listing_valid()
    if preflight.FAIL:
        fails.append("the real committed Etsy listing package failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_etsy_listing_valid, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
