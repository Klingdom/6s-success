#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_us_spelling_consistency() catches the real
defect found 2026-09-14 (REVIEW-DISCOVERY-2026-09-07.md D11): British
organis*/organiz* spellings ("organising", "organised", "organiser", ...)
mixed into US-English body copy. The site targets US English throughout
(prices in dollars, American room vocabulary), so this class of drift is a
consistency defect, not a matter of taste.

The one exception is real and deliberate: the site's own indexed article at
how-long-does-it-take-to-organise-a-room.html keeps its British-spelled
filename, because the URL is live and a redirect for a spelling preference
is not worth the risk (D11's own instruction). check_us_spelling() must
therefore ignore the British spelling only when it appears inside an href
pointing at that one page, and still catch it everywhere else, including in
the anchor TEXT of a link to that same page.

Run:  python ops/tests/test_gate_us_spelling_consistency.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as pf                                         # noqa: E402


def main() -> int:
    fails = []

    # 1. Plain body copy with a British spelling must be caught.
    hits = pf.check_us_spelling("<p>This is guidance for organising a home.</p>")
    if hits != ["organising"]:
        fails.append(f"plain body copy not caught: {hits!r}")

    # 2. Several distinct forms in one page are all named.
    hits = pf.check_us_spelling(
        "<p>Organised, organising, an organiser, and an organisation.</p>")
    if hits != ["organisation", "organised", "organiser", "organising"]:
        fails.append(f"multiple forms not all caught: {hits!r}")

    # 3. The one whitelisted href must not trip the gate on its own.
    clean = ('<a href="how-long-does-it-take-to-organise-a-room.html">'
             "How long a room takes</a>")
    hits = pf.check_us_spelling(clean)
    if hits:
        fails.append(f"whitelisted href wrongly flagged: {hits!r}")

    # 3b. Same whitelist, relative path and no .html extension, both real
    #     shapes seen in the live corpus.
    for href in ('href="../articles/how-long-does-it-take-to-organise-a-room.html"',
                 'href="how-long-does-it-take-to-organise-a-room"'):
        hits = pf.check_us_spelling(f"<a {href}>text</a>")
        if hits:
            fails.append(f"whitelisted href variant wrongly flagged "
                          f"({href!r}): {hits!r}")

    # 4. The exact real regression this gate exists to catch: the anchor
    #    TEXT of a link to the whitelisted page still uses the British
    #    spelling, which is not the URL and must still be caught.
    regressed = ('<a href="how-long-does-it-take-to-organise-a-room.html">'
                 "how long it takes to organise a room</a>")
    hits = pf.check_us_spelling(regressed)
    if hits != ["organise"]:
        fails.append(f"anchor text next to whitelisted href not caught: "
                      f"{hits!r}")

    # 5. Case insensitivity: a capitalised heading must still be caught.
    hits = pf.check_us_spelling("<h1>Organising the Garage</h1>")
    if hits != ["organising"]:
        fails.append(f"capitalised form not caught: {hits!r}")

    # 6. A clean, already-American page produces no hits.
    hits = pf.check_us_spelling(
        "<p>This is guidance for organizing and cleaning a home.</p>")
    if hits:
        fails.append(f"clean American copy wrongly flagged: {hits!r}")

    # 7. The real pre-fix defect this cycle found and fixed: reproduce it
    #    directly rather than only against synthetic text.
    real_pre_fix = ("Clean the other sleeper's side without reorganising "
                     "it. Work the lamp and the top.")
    hits = pf.check_us_spelling(real_pre_fix)
    if hits != ["organising"]:
        fails.append(f"real pre-fix nightstand text not caught: {hits!r}")

    if fails:
        print(f"FAIL: {len(fails)} case(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS: 7 of 7 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
