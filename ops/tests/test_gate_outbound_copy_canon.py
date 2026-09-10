#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_outbound_copy_canon() catches a banned canon
term in hand-written outbound copy, and that the real files are clean.

Found 2026-09-10 cold-reading ops/linkedin_posts.py: POST 2 ("Safety is the
fourth S, not a bolt-on") named the conventional 5S ordering as "Sort, Set
in Order, Shine, Standardize, Sustain," the retired term for the second S,
in a file whose whole purpose is to be copied verbatim onto a public
LinkedIn feed. gate_card_corpus already bans this term inside the card
text corpus; nothing checked the other place hand-written public copy
lives, and ops/dashboard.py's own canon count does not scan this file
either (it reads only the deck's HTML documents and the card corpus, the
same narrow-scope shape gate_card_corpus's own docstring already names as
a defect once). Fixed the one live instance in linkedin_posts.py by hand;
this test proves the new gate's detection logic actually fires on a
planted regression, not just on the one string that happened to be wrong,
and that both real files are clean today.

Run:  python ops/tests/test_gate_outbound_copy_canon.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    failures = []

    # Pure-logic proof: a planted banned term must be caught, by name.
    hit = preflight.scan_banned_copy(
        "fake.py", [("Title", "Sort, Set in Order, Shine, Standardize, Sustain.")])
    if len(hit) != 1 or "Set in Order" not in hit[0] or "fake.py" not in hit[0]:
        failures.append(f"scan_banned_copy did not catch a planted term: {hit!r}")

    # A clean entry must not be flagged.
    clean = preflight.scan_banned_copy(
        "fake.py", [("Title", "Sort, Straighten, Shine, Standardize, Sustain.")])
    if clean:
        failures.append(f"scan_banned_copy flagged clean text: {clean!r}")

    # Multiple banned terms in one body are all reported.
    multi = preflight.scan_banned_copy(
        "fake.py", [("Title", "Set in Order next to an Amazon box and a Gridfinity bin.")])
    if len(multi) != 3:
        failures.append(f"scan_banned_copy missed a term in a multi-hit body: {multi!r}")

    # Live-file proof: the real files, after this cycle's fix, report clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_outbound_copy_canon()
    if preflight.FAIL:
        failures.append(
            "gate_outbound_copy_canon fails against the real, committed "
            f"files: {preflight.FAIL}")

    # The live POSTS/CORPUS content itself must not carry the term (in case
    # the gate's own scan logic and this test happen to share a blind spot).
    for title, body in preflight.linkedin_posts_entries():
        if "Set in Order" in body:
            failures.append(f"linkedin_posts.py '{title}' still says 'Set in Order'")
    for _audience, title, body in preflight.linkedin_drafts_entries():
        if "Set in Order" in body:
            failures.append(f"linkedin_drafts.py '{title}' still says 'Set in Order'")

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print("ok: gate_outbound_copy_canon catches a planted banned term and "
          "the real outbound copy is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
