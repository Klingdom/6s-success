#!/usr/bin/env python3
"""
Prove preflight's check_deck_print_tiers() names every deck that does not land
on the 18-card print step, and stays silent for one that does.

WHY THIS EXISTS
---------------
DECK-GAME-DESIGN.md 4.1 is explicit about the economics: "print-on-demand
prices in 18-card steps, and 72 is exactly eight US Letter sheets at nine-up.
75 is 90 with fifteen blanks paid for."

On 2026-09-25 five more decks shipped and only Kitchen landed on a tier.
Entryway 57 pays for 72, Home Office 66 pays for 72, Laundry 67 pays for 72,
and the two that matter most, Primary Bathroom 76 and Garage 80, cross into
the 90 tier for four and eight cards over 72.

Nothing existing could have caught it. Every deck matched its own declared
budget exactly, so an internal-consistency check passed; the budgets were set
per room without reference to the step. That is the shape of defect worth a
gate: correct everywhere you look, wrong only against a fact held in a
different file.

Run:  python ops/tests/test_deck_print_tiers.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402


def case_exact_tier_is_silent():
    for n in (18, 36, 54, 72, 90):
        assert P.check_deck_print_tiers({"D": n}) == [], n


def case_one_over_a_tier_costs_a_whole_tier():
    out = P.check_deck_print_tiers({"Garage": 73})
    assert len(out) == 1, out
    assert "prints at the 90 tier" in out[0], out[0]
    assert "17 slot(s)" in out[0], out[0]


def case_under_filled_tier_is_reported_too():
    """Unbought value, not just wasted money: Entryway could carry 15 more."""
    out = P.check_deck_print_tiers({"Entryway": 57})
    assert len(out) == 1, out
    assert "prints at the 72 tier" in out[0], out[0]
    assert "15 slot(s)" in out[0], out[0]


def case_worst_waste_is_named_first():
    out = P.check_deck_print_tiers({"A": 71, "B": 55, "C": 67})
    assert len(out) == 3, out
    assert out[0].startswith("B "), out       # 55 -> 72, wastes 17
    assert out[-1].startswith("A "), out      # 71 -> 72, wastes 1


def case_empty_and_zero_are_ignored():
    assert P.check_deck_print_tiers({}) == []
    assert P.check_deck_print_tiers({"D": 0}) == []


def case_the_real_decks_today():
    """Re-derived from the shipped decks, not pinned to today's counts.

    A test that hardcodes "5 of 6 are wrong" fails as a reward for fixing
    them, which trains people to edit the test rather than the deck.
    """
    decks = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "ops", "cardtext",
                                            "*-deck.json"))):
        d = json.load(io.open(fp, encoding="utf-8"))
        cards = d.get("cards")
        if isinstance(cards, list):
            decks[d.get("room") or os.path.basename(fp)] = len(cards)
    assert decks, "no built decks found at all"
    out = P.check_deck_print_tiers(decks)
    offenders = {n for n, c in decks.items()
                 if c % P.DECK_PRINT_STEP}
    assert len(out) == len(offenders), (out, offenders)
    for name in offenders:
        assert any(line.startswith(name + " ") for line in out), (name, out)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
