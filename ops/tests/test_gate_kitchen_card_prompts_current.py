#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_card_prompts_current() catches a
committed Kitchen image-prompt file that has drifted from the live
ops/cardtext/kitchen-deck.json corpus.

Found live 2026-09-30: KZ-002's committed prompt in
build/prompts/kitchen/KZ-002.txt still read "The step of space either side
of the burners...", the wrong word, after the corpus had already been
corrected to "The strip of space...". Nothing had regenerated the prompt
file since, and no gate checked the two against each other, the same
"source corrected, artifact never re-derived" shape this repository's own
log names as its dominant defect class. This tests the pure logic
(check_kitchen_card_prompts_current) with synthetic cards, so it never
touches the real committed prompt files.

Run:  python ops/tests/test_gate_kitchen_card_prompts_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
from build_card_prompts import prompt_for                       # noqa: E402

PREFIX = ("Photorealistic interior photograph, warm natural window light, "
          "eye-level 40mm lens, real modern kitchen, warm neutral palette, "
          "clean composition with empty calm areas reserved for later text "
          "overlay.")

CARDS = [
    {"ID": "KZ-001", "Card": "Primary Prep Counter", "Category": "Zone",
     "Objective / Behavior": "The strip of space beside the hob.",
     "Canonical text": "HANDS BUSY, HEAT ON", "art_subject": "",
     "art_must_show": [], "art_must_kind": "condition", "art_accept": ""},
    {"ID": "KF-001", "Card": "The counter fills up", "Category": "Friction",
     "Objective / Behavior": "Clutter creeps in during cooking.",
     "Canonical text": "NOWHERE TO SET THE PAN DOWN", "art_subject": "",
     "art_must_show": [], "art_must_kind": "condition", "art_accept": ""},
]


def committed(ids=None, drift_id=None, drop_id=None) -> dict:
    """The files dict gate_kitchen_card_prompts_current would build from
    disk: card ID -> committed text, matching build_card_prompts.py's own
    "header + body + newline" file shape unless drift_id's body is
    mangled or drop_id is missing entirely (a card added upstream with no
    prompt file ever generated for it)."""
    ids = CARDS if ids is None else ids
    out = {}
    for c in ids:
        if c["ID"] == drop_id:
            continue
        body = prompt_for(c, "Kitchen", PREFIX)
        if c["ID"] == drift_id:
            body = body.replace("strip of space", "step of space")
        out[c["ID"]] = f"CARD {c['ID']}  {c['Card']}\n" + "-" * 70 + "\n\n" \
            + body + "\n"
    return out


def main() -> int:
    fails = []

    # 1. Clean: every committed file matches what the live corpus produces.
    problems = preflight.check_kitchen_card_prompts_current(
        CARDS, PREFIX, committed())
    if problems:
        fails.append("clean prompts wrongly flagged: %s" % problems)

    # 2. The exact live defect: a corpus word corrected, the committed
    #    prompt file never regenerated to match.
    problems = preflight.check_kitchen_card_prompts_current(
        CARDS, PREFIX, committed(drift_id="KZ-001"))
    if not any("KZ-001" in p for p in problems):
        fails.append("a drifted committed prompt was NOT caught: %s"
                      % problems)

    # 3. A card with no committed prompt file at all (added upstream,
    #    never generated).
    problems = preflight.check_kitchen_card_prompts_current(
        CARDS, PREFIX, committed(drop_id="KF-001"))
    if not any("KF-001" in p for p in problems):
        fails.append("a missing committed prompt file was NOT caught: %s"
                      % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_card_prompts_current: 3/3 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
