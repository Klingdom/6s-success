#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_corporate_linkedin_claims_current() catches
the corporate LinkedIn post track (C11, REVIEW-COMMERCE-2026-09-07.md
section 7) drifting away from the page it quotes.

ops/linkedin_drafts.py's corporate_block() adds a second, B2B-only post to
the daily draft email, sourced entirely from site/corporate.html. Every
anchor phrase it relies on is asserted present by corporate_facts(); this
gate calls that function the same way gate_linkedin_drafts_price_current
calls facts(), plus checks the corpus's own 130-word cap and the
zero-em/en-dash rule CLAUDE.md applies everywhere.

Run:  python ops/tests/test_gate_corporate_linkedin_claims_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import linkedin_drafts                                         # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_corporate_linkedin_claims_current()
    return list(preflight.FAIL), list(preflight.WARN)


def main() -> int:
    fails = []
    orig_corpus = linkedin_drafts.CORPORATE_CORPUS
    orig_anchors = linkedin_drafts._CORPORATE_ANCHORS

    # 1. The real committed files: clean today.
    r, w = _run()
    if r:
        fails.append("the real committed files failed: %r" % (r,))

    # 2. An anchor phrase the corpus relies on drifts out of corporate.html:
    #    must fail, naming the missing phrase.
    linkedin_drafts._CORPORATE_ANCHORS = orig_anchors + [
        "a phrase that does not exist on the real page 2026-09-21"]
    r, w = _run()
    linkedin_drafts._CORPORATE_ANCHORS = orig_anchors
    if not r or "corporate-linkedin-claims" != r[0][0]:
        fails.append("a missing anchor phrase was not caught: %r" % (r,))

    # 3. A corpus entry over the 130-word cap: must fail.
    linkedin_drafts.CORPORATE_CORPUS = list(orig_corpus) + [
        ("x", "over cap", "word " * 150)]
    r, w = _run()
    linkedin_drafts.CORPORATE_CORPUS = orig_corpus
    if not r or "corporate-linkedin-claims" != r[0][0]:
        fails.append("an over-cap corporate post was not caught: %r" % (r,))

    # 4. A corpus entry with an em dash: must fail.
    linkedin_drafts.CORPORATE_CORPUS = list(orig_corpus) + [
        ("x", "em dash", "a claim with an em—dash inside it")]
    r, w = _run()
    linkedin_drafts.CORPORATE_CORPUS = orig_corpus
    if not r or "corporate-linkedin-claims" != r[0][0]:
        fails.append("an em-dash corporate post was not caught: %r" % (r,))

    # 5. A corpus entry with an en dash: must fail.
    linkedin_drafts.CORPORATE_CORPUS = list(orig_corpus) + [
        ("x", "en dash", "a range like 2020–2026 should never ship")]
    r, w = _run()
    linkedin_drafts.CORPORATE_CORPUS = orig_corpus
    if not r or "corporate-linkedin-claims" != r[0][0]:
        fails.append("an en-dash corporate post was not caught: %r" % (r,))

    # 6. Restored to the real corpus and real anchors: clean again, proving
    #    the monkeypatches above did not leak state between cases.
    r, w = _run()
    if r:
        fails.append("state leaked between test cases: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_corporate_linkedin_claims_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
