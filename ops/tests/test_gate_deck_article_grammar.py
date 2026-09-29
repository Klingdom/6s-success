#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_deck_article_grammar() catches a room deck
page whose JSON-LD abstract uses the wrong indefinite article for its own
card count.

Found live 2026-09-28: site/garage-deck.html's own Game JSON-LD abstract
read "A 80 card deck for the garage", wrong, because 80 is spoken "eighty"
and needs "An". All six room-deck generators hardcoded the literal word "A"
next to a card count only known at generation time, so any future count
whose spoken form starts with a vowel sound (eighty, eighteen, eleven,
eight itself) would have shipped the same mismatch silently. Fixed at the
source: build_kitchen_deck_page.article_for() now computes the real
article from the real count, and all six generators use it.

Tests the pure logic (check_deck_article_grammar) with synthetic page
text, so it never touches the real committed pages, then separately checks
the real committed pages directly.

Run:  python ops/tests/test_gate_deck_article_grammar.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_kitchen_deck_page as KDP                          # noqa: E402


def page(article: str, n: int, room: str = "the garage") -> str:
    return (f'  "abstract": "{article} {n} card deck for {room}, built '
            f'from the Manual\'s real seven zones..."\n')


CLEAN = {
    "kitchen-deck.html": page("A", 72, "the kitchen"),
    "entryway-deck.html": page("A", 57, "the entryway"),
    "laundry-room-deck.html": page("A", 67, "the laundry room"),
    "home-office-deck.html": page("A", 66, "the home office"),
    "primary-bathroom-deck.html": page("A", 76, "the primary bathroom"),
    "garage-deck.html": page("An", 80, "the garage"),
}


def main() -> int:
    fails = []

    # 1. Clean: every deck's own count-correct article, no false positive.
    problems = preflight.check_deck_article_grammar(CLEAN, KDP.article_for)
    if problems:
        fails.append("the clean synthetic case was flagged: %s" % problems)

    # 2. The real, live defect this gate exists to catch: "A 80" instead of
    #    "An 80", the exact shape found live on the Garage deck.
    wrong = dict(CLEAN)
    wrong["garage-deck.html"] = page("A", 80, "the garage")
    problems = preflight.check_deck_article_grammar(wrong, KDP.article_for)
    if not any("garage-deck.html" in p and "'An' 80" in p for p in problems):
        fails.append("'A 80 card deck' on the Garage deck was NOT caught: "
                      "%s" % problems)

    # 3. The opposite mistake: "An" in front of a count that does not need
    #    it (kitchen's real count, 72, is spoken "seventy-two").
    over_corrected = dict(CLEAN)
    over_corrected["kitchen-deck.html"] = page("An", 72, "the kitchen")
    problems = preflight.check_deck_article_grammar(over_corrected,
                                                      KDP.article_for)
    if not any("kitchen-deck.html" in p and "'A' 72" in p for p in problems):
        fails.append("an over-corrected 'An 72 card deck' was NOT caught: "
                      "%s" % problems)

    # 4. The "one" exception: a count whose spoken form starts with the
    #    vowel LETTER but not the vowel SOUND must still take "A".
    one_case = {"kitchen-deck.html": page("An", 1, "the kitchen")}
    problems = preflight.check_deck_article_grammar(one_case, KDP.article_for)
    if not any("'A' 1" in p for p in problems):
        fails.append("'An 1 card deck' (should be 'A 1') was NOT caught: "
                      "%s" % problems)

    # 5. Missing/reshaped abstract: reported, not silently skipped.
    no_abstract = {"kitchen-deck.html": "no abstract field here at all"}
    problems = preflight.check_deck_article_grammar(no_abstract,
                                                      KDP.article_for)
    if not any("no \"A/An" in p for p in problems):
        fails.append("a missing/reshaped abstract was NOT reported: %s"
                      % problems)

    # 6. Against the real thing: the actual six committed deck pages, not
    #    synthetic stand-ins. This is the check that would have caught the
    #    real defect this gate was built to fix.
    real_pages = {}
    for fname in CLEAN:
        path = os.path.join(ROOT, "site", fname)
        if os.path.exists(path):
            real_pages[fname] = open(path, encoding="utf-8").read()
    if len(real_pages) < len(CLEAN):
        fails.append("not all six real deck pages exist; the real-site "
                      "case could not run against all of them: found %s"
                      % sorted(real_pages))
    problems = preflight.check_deck_article_grammar(real_pages,
                                                      KDP.article_for)
    if problems:
        fails.append("the real committed deck pages have a live article "
                      "problem: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_deck_article_grammar: 6/6 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
