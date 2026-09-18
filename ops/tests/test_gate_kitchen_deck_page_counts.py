#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_page_counts_current() catches
site/kitchen-deck.html stating a card/zone/root-cause count, or naming the
whole-kitchen action cards, in a way that no longer matches the real deck
in ops/cardtext/kitchen-deck.json.

Found 2026-09-18, cold-reading ops/build_kitchen_deck_page.py (3 mentions
in ops/NIGHTLY-LOG.md, per step 5d): its page copy stated "72 cards",
"Seven kitchen zones", "twelve root causes" and, naming the exact four
cards, "Four cards that are not one zone's job: the nightly close, the
safety walk..., the shopping list loop, and the conversation..." as plain
Python string literals, never read from the deck itself. All four numbers
matched the real 72-card deck today (verified directly), so this closes a
latent gap rather than a live defect. Fixed at the source (the generator
now derives every count from deck data) and gated here independently, the
same reason gate_kit_page_zone_counts_current re-derives rather than
trusts its own generator's arithmetic: a generator that computes a number
wrong would still agree with itself on every future regenerate-and-diff.

Tests the pure logic (check_kitchen_deck_page_counts) with synthetic data,
then checks the real committed site/kitchen-deck.html against the real
committed ops/cardtext/kitchen-deck.json, so a future regression (a hand
edit to the page, or the generator's own count logic breaking) is caught
either way.

Run:  python ops/tests/test_gate_kitchen_deck_page_counts.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def synthetic_cards(n_zones=2, n_causes=3, whole_ids=("KA-015", "KA-016",
                                                        "KA-017", "KA-018")):
    cards = [{"id": "KR-001", "type": "ROOM CARD"}]
    for i in range(n_zones):
        cards.append({"id": "KZ-%03d" % i, "type": "ZONE CARD",
                      "zone": "Zone %d" % i})
    for i in range(n_causes):
        cards.append({"id": "KC-%03d" % i, "type": "ROOT CAUSE CARD"})
    for wid in whole_ids:
        cards.append({"id": wid, "type": "ACTION CARD", "zone": None})
    return cards


def clean_page(n_total, n_zones, n_causes, n_whole):
    words = {2: "two", 3: "three", 4: "four", 5: "five"}
    return (
        "<title>The Kitchen Deck: %d cards</title>\n"
        "<meta name=\"description\" content=\"%s kitchen zones, ...\">\n"
        "<p>points at one of these %s.</p>\n"
        "<p>%s cards that are not one zone's job: the nightly close, the "
        "safety walk to do before any rebuild, the shopping list loop, and "
        "the conversation two cooks need to have once.</p>"
        % (n_total, words[n_zones].capitalize(), words[n_causes],
           words[n_whole].capitalize())
    )


def main() -> int:
    fails = []

    # 1. Clean: the page's own prose matches the real, freshly-derived counts.
    cards = synthetic_cards(n_zones=2, n_causes=3)
    page = clean_page(len(cards), 2, 3, 4)
    problems = preflight.check_kitchen_deck_page_counts(cards, page)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. The exact regression this gate exists for: the deck grew a third
    #    zone, but the shipped page still says "Two kitchen zones".
    cards3 = synthetic_cards(n_zones=3, n_causes=3)
    stale_page = clean_page(len(cards3), 2, 3, 4)
    problems = preflight.check_kitchen_deck_page_counts(cards3, stale_page)
    if not any("kitchen zones" in p for p in problems):
        fails.append("a stale zone count was NOT caught: %s" % problems)

    # 3. The root-cause count drifted (deck grew a cause, page still says
    #    the old number).
    cards4 = synthetic_cards(n_zones=2, n_causes=4)
    stale_page = clean_page(len(cards4), 2, 3, 4)
    problems = preflight.check_kitchen_deck_page_counts(cards4, stale_page)
    if not any("root-cause" in p for p in problems):
        fails.append("a stale root-cause count was NOT caught: %s" % problems)

    # 4. The whole-kitchen card SET changed (a card swapped for a new id)
    #    even though the count (4) stayed the same; the sentence naming the
    #    four specific cards is now describing the wrong cards.
    cards5 = synthetic_cards(whole_ids=("KA-015", "KA-016", "KA-017", "KA-099"))
    page5 = clean_page(len(cards5), 2, 3, 4)
    problems = preflight.check_kitchen_deck_page_counts(cards5, page5)
    if not any("KA-099" in p for p in problems):
        fails.append("a changed whole-kitchen card set was NOT caught: %s"
                     % problems)

    # 5. Real files: check the real committed site/kitchen-deck.html against
    #    the real committed ops/cardtext/kitchen-deck.json.
    kdeck_path = os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json")
    page_path = os.path.join(ROOT, "site", "kitchen-deck.html")
    if os.path.exists(kdeck_path) and os.path.exists(page_path):
        real_cards = json.load(io.open(kdeck_path, encoding="utf-8"))["cards"]
        real_page = io.open(page_path, encoding="utf-8", errors="replace").read()
        problems = preflight.check_kitchen_deck_page_counts(real_cards, real_page)
        if problems:
            fails.append("the real committed site/kitchen-deck.html does "
                        "not match a live re-derivation of the deck's own "
                        "counts: %s" % problems)
    else:
        print("  (skipped case 5: a real source file is missing here)")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_deck_page_counts: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
