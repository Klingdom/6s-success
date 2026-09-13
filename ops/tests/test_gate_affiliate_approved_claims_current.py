#!/usr/bin/env python3
"""
Prove gate_affiliate_approved_claims_current actually fires the day
ops/affiliate-accounts.json records an approved programme while
how-we-make-money.html or affiliate-disclosure.html still say none has been
approved, and that it stays honestly quiet (UNCHECKED, not clean) whenever it
cannot read the ledger at all.

Found 2026-09-13, this operator, cold-reading site/how-we-make-money.html per
step 5d: both pages hand-type "no programme has been approved" with nothing
tying that sentence to ops/affiliate-accounts.json, the file a real approval
actually lands in. Amazon's own account is already mid-application, so this
is not hypothetical.

Run:  python ops/tests/test_gate_affiliate_approved_claims_current.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402
import affiliate as A                                           # noqa: E402

REAL_EXISTS = os.path.exists
ACCOUNTS_PATH = os.path.join(ROOT, "ops", "affiliate-accounts.json")

STALE_HWMM = (
    "<p>Many sites in this category earn a commission when you buy "
    "a recommended product elsewhere. We do not, today. We have applied "
    "to a few retailer programmes and none has been approved, so there "
    "is not a single link on this site that earns us anything when you "
    "click it.</p>"
)
STALE_DISCLOSURE = (
    "<p><b>Today, nothing on this site earns us a commission.</b> We have "
    "applied to a handful of retailer affiliate programmes and none of them "
    "has been approved, so there is not one link here that pays us when you "
    "click it or buy through it.</p>"
)
FIXED = "<p>Approved retailer links are marked where you see them.</p>"


def run(approved_fn, site_dir):
    real_approved = A.approved
    real_site = P.SITE
    A.approved = approved_fn
    P.SITE = site_dir
    P.FAIL.clear()
    P.WARN.clear()
    try:
        P.gate_affiliate_approved_claims_current()
    finally:
        A.approved = real_approved
        P.SITE = real_site
    return list(P.FAIL), list(P.WARN)


def make_site(hwmm_text, disclosure_text):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "how-we-make-money.html"), "w", encoding="utf-8") as f:
        f.write(hwmm_text)
    with open(os.path.join(d, "affiliate-disclosure.html"), "w", encoding="utf-8") as f:
        f.write(disclosure_text)
    return d


def main() -> int:
    fails = []
    stale_site = make_site(STALE_HWMM, STALE_DISCLOSURE)
    fixed_site = make_site(FIXED, FIXED)
    mixed_site = make_site(FIXED, STALE_DISCLOSURE)

    # Case 1: nothing approved yet, pages still stale. Today's real state.
    # Must stay clean: the claim is still true.
    f, w = run(lambda: {}, stale_site)
    if f or w:
        fails.append(f"nothing approved must be clean, got FAIL={f} WARN={w}")

    # Case 2: a programme is approved, both pages still carry the stale
    # sentence. The exact regression this gate exists to catch.
    f, w = run(lambda: {"amazon": {"publisher_id": "x"}}, stale_site)
    if not any(g == "affiliate-approved-claims-current"
               and "how-we-make-money.html" in m and "affiliate-disclosure.html" in m
               and "amazon" in m for g, m in f):
        fails.append(f"an approved programme with two stale pages must FAIL "
                     f"naming both and the programme, got {f}")

    # Case 3: a programme is approved, both pages already fixed. No false
    # positive once the real content stops matching the stale phrase.
    f, w = run(lambda: {"amazon": {"publisher_id": "x"}}, fixed_site)
    if f or w:
        fails.append(f"already-fixed pages must not trip the gate, got FAIL={f} WARN={w}")

    # Case 4: only one of the two pages was fixed. Must name only the one
    # still stale, not the one already corrected.
    f, w = run(lambda: {"amazon": {"publisher_id": "x"}}, mixed_site)
    matches = [m for g, m in f if g == "affiliate-approved-claims-current"]
    if not matches or "affiliate-disclosure.html" not in matches[0] or "how-we-make-money.html" in matches[0]:
        fails.append(f"a partially-fixed pair must name only the stale page, got {f}")

    # Case 5: approved() itself raises (a broken ledger read). Must warn
    # UNCHECKED, never pass silently and never crash the run.
    def boom():
        raise RuntimeError("corrupt affiliate-accounts.json")
    f, w = run(boom, stale_site)
    if f:
        fails.append(f"a raised approved() must not FAIL, got {f}")
    if not any(g == "affiliate-approved-claims-current" and "raised" in m for g, m in w):
        fails.append(f"a raised approved() must WARN by name, got {w}")

    # Case 6: the real accounts file is missing. Must warn UNCHECKED.
    real_exists = os.path.exists
    def fake_exists(path):
        if path == ACCOUNTS_PATH:
            return False
        return real_exists(path)
    P.os.path.exists = fake_exists
    P.FAIL.clear()
    P.WARN.clear()
    try:
        P.gate_affiliate_approved_claims_current()
        f, w = list(P.FAIL), list(P.WARN)
    finally:
        P.os.path.exists = real_exists
    if f:
        fails.append(f"a missing accounts file must not FAIL, got {f}")
    if not any(g == "affiliate-approved-claims-current" and "missing" in m for g, m in w):
        fails.append(f"a missing accounts file must WARN by name, got {w}")

    # Case 7: the real, live repository today. 0 of 10 programmes approved,
    # so the real pages (still carrying the honest sentence) must stay clean.
    P.FAIL.clear()
    P.WARN.clear()
    P.gate_affiliate_approved_claims_current()
    if P.FAIL:
        fails.append(f"the real, current repository must be clean today, got {P.FAIL}")

    if fails:
        print(f"FAIL: {len(fails)} of 7 cases")
        for msg in fails:
            print(" -", msg)
        return 1
    print("PASS: 7 of 7 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
