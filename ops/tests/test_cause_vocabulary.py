#!/usr/bin/env python3
"""
Prove preflight's check_cause_vocabulary() holds the one root-cause
vocabulary shared by 16 decks, 114 zone pages and the root-cause articles.

WHY THIS EXISTS
---------------
On 2026-09-29, KC-008 MISSING STANDARD read:

    "Ask two people what this surface should look like at bedtime."

It shipped on 100 pages. Every garage page, every pantry page and every
kitchen page asked a household standing in that room to picture a surface at
bedtime. The text had been written from the bedside zone it was first drafted
against and then promoted into the SHARED model without being read anywhere
else.

Nothing could have caught it. All 16 deck sources agreed with each other and
with ops/root_causes.py, so every equality check passed. The fault was not
disagreement, it was an assumption inside text that 20 rooms have to share.
That is why one of the rules below is about vocabulary rather than equality.

The same pass found the opposite fault too, and did NOT gate it:
ops/root_causes.py's docstring claims its first 12 causes are "copied
character-for-character" from ops/cardtext/kitchen-deck.json. That was
already false for 7 of the 12 and correctly so, because the Kitchen pilot
speaks in a kitchen voice ("every time you cook", "load the dishwasher
together") while the shared model has to speak to every room. So the pilot is
exempted by name from the text rule, and still held to ids, titles and six-S
entry points.

Run:  python ops/tests/test_cause_vocabulary.py
"""
import copy
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402
from root_causes import CAUSES                                 # noqa: E402


def _model(**over):
    c = {"id": "KC-001", "name": "EXCESS", "six_s": "Sort",
         "confirm_30s": "Count what you used in the past month."}
    c.update(over)
    return [c]


def _card(**over):
    c = {"id": "KC-001", "type": "ROOT CAUSE CARD", "title": "EXCESS",
         "six_s": "Sort",
         "confirm_in_30_seconds": "Count what you used in the past month."}
    c.update(over)
    return c


def case_matching_deck_is_silent():
    assert P.check_cause_vocabulary({"a-deck.json": [_card()]}, _model()) == []


def case_room_word_in_the_shared_model_is_named():
    out = P.check_cause_vocabulary(
        {"a-deck.json": [_card(confirm_in_30_seconds="see it at bedtime")]},
        _model(confirm_30s="see it at bedtime"))
    assert any("bedtime" in line for line in out), out


def case_every_listed_room_word_is_caught():
    for word in P.ROOM_SPECIFIC_WORDS:
        text = "look at the %s now" % word
        out = P.check_cause_vocabulary(
            {"a-deck.json": [_card(confirm_in_30_seconds=text)]},
            _model(confirm_30s=text))
        assert any(word in line for line in out), word


def case_room_word_is_matched_case_insensitively():
    out = P.check_cause_vocabulary(
        {"a-deck.json": [_card(confirm_in_30_seconds="At Bedtime")]},
        _model(confirm_30s="At Bedtime"))
    assert any("bedtime" in line for line in out), out


def case_a_deck_left_stale_after_a_model_edit_is_named():
    out = P.check_cause_vocabulary(
        {"a-deck.json": [_card(confirm_in_30_seconds="the old wording")]},
        _model())
    assert len(out) == 1, out
    assert "drifted" in out[0], out


def case_the_named_pilot_may_keep_its_own_voice():
    deck = P.CAUSE_VOICE_EXEMPT_DECKS[0]
    out = P.check_cause_vocabulary(
        {deck: [_card(confirm_in_30_seconds="count it every time you cook")]},
        _model())
    assert out == [], out


def case_the_pilot_is_still_held_to_id_title_and_pass():
    deck = P.CAUSE_VOICE_EXEMPT_DECKS[0]
    out = P.check_cause_vocabulary({deck: [_card(six_s="Shine")]}, _model())
    assert len(out) == 1 and "two different passes" in out[0], out
    out = P.check_cause_vocabulary({deck: [_card(title="SURPLUS")]}, _model())
    assert len(out) == 1 and "two names" in out[0], out


def case_unknown_cause_id_is_named():
    out = P.check_cause_vocabulary({"a-deck.json": [_card(id="KC-999")]},
                                   _model())
    assert len(out) == 1 and "not in the shared model" in out[0], out


def case_root_cause_cards_are_found_at_any_depth():
    card = _card()
    doc = {"sections": [{"cards": [card, {"type": "ACTION CARD"}]}]}
    found = P._root_cause_cards(doc)
    assert found == [card], found


def case_the_real_tree_is_clean():
    decks = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "ops", "cardtext",
                                            "*-deck.json"))):
        doc = json.load(io.open(fp, encoding="utf-8"))
        decks[os.path.basename(fp)] = P._root_cause_cards(doc)
    assert decks, "no deck sources found at all"
    assert sum(len(v) for v in decks.values()) > 100, decks.keys()
    out = P.check_cause_vocabulary(decks, CAUSES)
    assert out == [], out


def case_the_original_defect_would_now_fail_the_real_tree():
    """The exact 2026-09-29 text, restored, must fail against real decks."""
    decks = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "ops", "cardtext",
                                            "*-deck.json"))):
        doc = json.load(io.open(fp, encoding="utf-8"))
        decks[os.path.basename(fp)] = P._root_cause_cards(doc)
    causes = copy.deepcopy(CAUSES)
    for c in causes:
        if c["id"] == "KC-008":
            c["confirm_30s"] = ("Ask two people what this surface should "
                                "look like at bedtime. Two answers means "
                                "there is no standard to keep.")
    out = P.check_cause_vocabulary(decks, causes)
    assert any("bedtime" in line for line in out), out


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
