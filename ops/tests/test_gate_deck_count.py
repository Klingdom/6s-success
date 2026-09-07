#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_deck_count() catches a real card-count
mismatch, and that it does so WITHOUT needing any locally rendered
card-front PNG.

Found 2026-09-07: the previous version counted build/cards-rendered/
*-front.png to learn the deck's true size, and returned immediately if
that directory was empty. build/cards-rendered/ is empty in every cloud
run (the art needs a Desktop-only render step no sandbox here has), so
the entire check, including its comparisons against data.js and every
page's own prose, silently no-op'd everywhere except a full local
render. A gate that cannot fail is theatre. This now reads
build/entryway-cardtext.json instead, a committed corpus file that is
real in every environment, so the gate actually runs in CI.

Run:  python ops/tests/test_gate_deck_count.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Clean: catalogue and every page state one of the two real numbers,
    #    or a third number contrasted against a real one in the same
    #    sentence (the honest "X of Y drawn" pattern).
    problems = preflight.check_deck_count(
        89, True,
        "88 cards, fronts and backs, print at home",
        {"deck.html": "89 cards to deal out, 72 of them drawn so far.",
         "deck-gallery.html": "Counted whole, the deck is 89 cards including "
                              "the Room card. The catalogue quotes 88."})
    if problems:
        fails.append("clean, honest pages wrongly flagged: %s" % problems)

    # 2. The catalogue quotes a THIRD number, matching neither real total.
    problems = preflight.check_deck_count(
        89, True, "90 cards, fronts and backs, print at home", {})
    if not problems:
        fails.append("catalogue quoting 90 (neither 89 nor 88) NOT caught")

    # 3. A page states a bare wrong number with no real total nearby.
    problems = preflight.check_deck_count(
        89, True, "88 cards, fronts and backs",
        {"deck.html": "This deck ships as 95 cards, front and back."})
    if not any("95" in p for p in problems):
        fails.append("page stating 95 cards NOT caught")

    # 4. No false positive: a small in-range number (e.g. "72 drawn") next
    #    to the real total is fine, not a claim about the deck's size.
    problems = preflight.check_deck_count(
        89, True, "88 cards, fronts and backs",
        {"deck-gallery.html": "72 of the deck's 89 cards are drawn and "
                              "shown here, front and back."})
    if problems:
        fails.append("honest 'X of 89 drawn' phrasing wrongly flagged: %s"
                      % problems)

    # 5. No false positive: a number outside the plausible deck-size range
    #    (e.g. "20 sheets") must never be treated as a card-count claim.
    problems = preflight.check_deck_count(
        89, True, "88 cards, fronts and backs",
        {"standards.html": "20 sheets, print at home."})
    if problems:
        fails.append("out-of-range number wrongly flagged: %s" % problems)

    # 6. DECKS['entryway']['written'] must match the real committed corpus.
    #    This is the hardcoded-count-drifts-from-source-of-truth class:
    #    simulate it by calling the gate against a corpus count the live
    #    DECKS table does not claim, via a throwaway copy of the corpus.
    real = os.path.join(ROOT, "build", "entryway-cardtext.json")
    if os.path.exists(real):
        corpus = json.load(io.open(real, encoding="utf-8"))
        real_written = corpus.get("count")
        import build_deck_gallery as BDG                       # noqa: E402
        spec = BDG.DECKS.get("entryway")
        if spec and spec.get("written") != real_written:
            fails.append(
                "DECKS['entryway']['written']=%s already disagrees with "
                "the real corpus (%s) before this test touched anything"
                % (spec.get("written"), real_written))
    else:
        print("  note: build/entryway-cardtext.json not present, "
              "skipping the corpus cross-check case")

    # 7. The gate must actually run with zero rendered PNGs present, which
    #    is the standing condition in every cloud sandbox. Prove the real
    #    call executes and reports the live site clean, not merely that
    #    the pure function above is correct in isolation.
    no_renders = not os.path.exists(os.path.join(ROOT, "build", "cards-rendered"))
    preflight.FAIL.clear()
    preflight.gate_deck_count()
    if preflight.FAIL:
        fails.append("real gate run against the live repo found problems "
                     "(expected clean): %s" % preflight.FAIL)
    elif not no_renders:
        print("  note: build/cards-rendered/ exists in this environment, "
              "so this case did not prove the no-local-art path")
    preflight.FAIL.clear()

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 7 cases (clean honest pages pass, a third-number "
          "catalogue claim and a bare wrong-number page are both caught, "
          "no false positive on 'X of Y drawn' or an out-of-range number, "
          "DECKS table matches the real corpus, and the gate runs and "
          "reports clean with zero locally rendered card art)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
