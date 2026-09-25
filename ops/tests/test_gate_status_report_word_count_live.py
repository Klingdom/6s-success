#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_report_word_count_live() can actually
fail, and that it clears once the book's word count is measured from the
live EPUB rather than hand-typed.

Found 2026-09-25, this operator, cold-reading ops/status_report.py:
gather() hardcoded "words": 261876, never once recomputed since it was
written, while the real committed EPUB (the same file
gate_kdp_word_count_current already recomputes) carries 271,362 words,
3.6% higher. Every status report and PDF Phil received told him the book
was almost 10,000 words shorter than it actually is. Fixed by having
ops/dashboard.py measure the word count live into state.json["book_words"]
(None if the EPUB is missing or unreadable, never a guess), with
status_report.py and status_pdf.py reading it from there.

Run:  python ops/tests/test_gate_status_report_word_count_live.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import status_report as SR                                     # noqa: E402


def main() -> int:
    fails = []

    # 1. The real defect shape: a stale state.json disagrees with a fresh
    #    recompute of the real EPUB. Must fire, and must name both numbers.
    problem = preflight.check_status_report_word_count_stale(271362, 261876)
    if not problem:
        fails.append("live=271362, state=261876: expected a problem, got none")
    elif "271362" not in problem or "261876" not in problem:
        fails.append("problem string does not name both the live and stale "
                     "counts: %r" % problem)

    # 2. Agreement must not fire.
    if preflight.check_status_report_word_count_stale(271362, 271362):
        fails.append("live == state (271362 == 271362): expected no problem")

    # 3. Either side unmeasured (None) must never be treated as a mismatch:
    #    that is the exact "unknown collapsing into a specific claim" class
    #    this repository's other gates already exist to catch.
    if preflight.check_status_report_word_count_stale(None, 261876):
        fails.append("live=None should not fire (could not check), fired anyway")
    if preflight.check_status_report_word_count_stale(271362, None):
        fails.append("state=None should not fire (could not check), fired anyway")
    if preflight.check_status_report_word_count_stale(None, None):
        fails.append("live=None, state=None should not fire, fired anyway")

    # 4. render() must never collapse an unmeasured word count into a
    #    number, and must render a real count when one is known.
    base = {
        "generated": "2026-01-01 00:00",
        "state": {"overall": "YELLOW", "overall_why": "test",
                  "revenue_text": "$0", "customers_text": "0",
                  "email_list": 0, "needs_phil": 0, "constraint": "test"},
        "domain": {"status": 200, "title": "t", "parked": False,
                   "a_record": "0.0.0.0", "nameservers": [], "mx_working": True},
        "vps": {"ip": "0.0.0.0", "ports": {22: False, 80: True, 443: True,
                3000: False, 8973: False}, "default_title": "t",
                "as_domain_title": "t", "vhost_configured": True},
        "image_public": True,
        "experiments": {"designed": [], "executed": 0, "blocked_reason": "x"},
        "content": {"chapters": 50, "words": None, "rooms": 20, "zones": 114,
                   "manual_kb": 1, "epub_mb": 1, "sample_pdf_mb": 1,
                   "site_pages": 190, "deck_rooms": 0, "video": "0/114",
                   "social_units": 1},
        "catalogue": {"Micro Zone Packs": 109}, "catalogue_total": 111,
        "catalogue_buyable": 107, "catalogue_free": 3,
        "catalogue_unready": [],
        "catalogue_buyable_other": 105,
        "decks": {"Entryway": 72}, "decks_withheld": {"Entryway": 18},
        "issues": [], "issues_available": True,
        "commits_7d": 1, "recent": [], "retros": [],
    }
    _, text_none, _ = SR.render(base)
    if "words not measured this run" not in text_none:
        fails.append("render() with words=None does not say 'not measured'")
    if "271,362 words" in text_none:
        fails.append("render() with words=None still prints a specific count")

    with_words = dict(base)
    with_words["content"] = dict(base["content"], words=271362)
    _, text_num, _ = SR.render(with_words)
    if "271,362 words" not in text_num:
        fails.append("render() with words=271362 does not print '271,362 words'")

    # 5. Real committed state, end to end: gate must pass clean right now.
    preflight.FAIL[:] = []
    preflight.run_gate(preflight.gate_status_report_word_count_live)
    if preflight.FAIL:
        fails.append("gate_status_report_word_count_live failed against "
                     "the real committed tree: %r" % preflight.FAIL)

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 8 checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
