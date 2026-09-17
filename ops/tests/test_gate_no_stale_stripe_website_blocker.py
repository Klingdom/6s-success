#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_stale_stripe_website_blocker() catches
BACKLOG-2026-H2.md's "Items waiting on Phil, consolidated" list still
describing the Stripe business website field (row 2.8, issue #21) as
blocked once row 2.8 itself records it fixed.

Found 2026-09-17, this PM check-in, while re-reading issue #21 for a
triage decision. Row 2.8 said "verified fixed 2026-09-06 by reading the
live account... done, no longer needs anybody," but the consolidated
list's item 6 still read "only this one field was blocked by Stripe's
own safety check when the operator tried it," eleven days after the fix
landed, the same "source corrected, sibling document never told" shape
gate_no_stale_card_deck_decision and
gate_no_stale_affiliate_apply_instruction already protect elsewhere in
this file.

Run:  python ops/tests/test_gate_no_stale_stripe_website_blocker.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

ROW_DONE = ("| 2.8 | ~~Stripe business website field~~ | Verified fixed "
            "2026-09-06. | 0.1 | **done, no longer needs anybody** |\n")
ROW_OPEN = ("| 2.8 | Stripe business website field still reads Ledgerium "
            "(issue #21) | not yet checked | 0.1 | **open, waiting on "
            "Phil** |\n")

STALE_ITEM = (
    "6. **Stripe business website field** (2.8, issue #21). Settings, "
    "Business details, Public details, Edit. Everything else on the "
    "account is already fixed per account; only this one field was "
    "blocked by Stripe's own safety check when the operator tried it, "
    "because it can silently change Ledgerium's account too.\n")

FIXED_ITEM = (
    "6. **Stripe business website field** (2.8, issue #21). The field "
    "itself is fixed and no longer waiting on anybody: row 2.8 above "
    "records it verified live 2026-09-06. What is still Phil's actual "
    "call: the industry/MCC code and whether to keep Stripe Climate's "
    "1% contribution.\n")


def _run(h2_text):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "BACKLOG-2026-H2.md"), "w",
                encoding="utf-8").write(h2_text)
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_no_stale_stripe_website_blocker()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real regression shape: row 2.8 says done, item 6 still says
    #    blocked.
    r, w = _run(ROW_DONE + STALE_ITEM)
    if not r or "no-stale-stripe-website-blocker" != r[0][0]:
        fails.append("the stale-item regression was not caught: %r" % (r,))

    # 2. Row 2.8 not yet marked done: item 6 describing it as blocked is
    #    accurate, not stale. No failure.
    r, w = _run(ROW_OPEN + STALE_ITEM)
    if r:
        fails.append("an accurate blocked description was wrongly "
                      "flagged while row 2.8 is still open: %r" % (r,))

    # 3. Both corrected (the real fixed shape): no failure.
    r, w = _run(ROW_DONE + FIXED_ITEM)
    if r:
        fails.append("genuinely fixed documents wrongly flagged: %r" % (r,))

    # 4. Row 2.8 done, item 6 absent entirely: nothing to contradict.
    r, w = _run(ROW_DONE + "nothing else relevant\n")
    if r:
        fails.append("no item 6 present was wrongly flagged: %r" % (r,))

    # 5. The real, committed file: clean, now that it has been corrected
    #    in place.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_no_stale_stripe_website_blocker()
    if preflight.FAIL:
        fails.append("the real committed file failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_no_stale_stripe_website_blocker, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
