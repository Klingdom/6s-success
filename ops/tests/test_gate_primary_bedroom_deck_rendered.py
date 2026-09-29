#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_primary_bedroom_deck_rendered() catches a
shipped Primary Bedroom deck page that has drifted from the real cardtext
corpus.

Same shape as ops/tests/test_gate_nursery_deck_rendered.py, for the
eighteenth room's deck (BACKLOG-2026-09-07.md B9). Tests the pure logic
(check_primary_bedroom_deck_rendered) with synthetic cards and page text,
so it never touches the real committed page except in case 6.

Run:  python ops/tests/test_gate_primary_bedroom_deck_rendered.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CARDS = [
    {"id": "PRR-001", "type": "ROOM CARD", "objective": "The room card text."},
    {"id": "PRZ-001", "type": "ZONE CARD", "objective": "The zone card text."},
    {"id": "PRF-001", "type": "FRICTION CARD", "objective": "The friction text."},
    {"id": "KC-001", "type": "ROOT CAUSE CARD", "objective": "The cause text."},
    {"id": "PRA-001", "type": "ACTION CARD", "objective": "The action goal text."},
    {"id": "PRS-001", "type": "STANDARD CARD", "objective": "The standard text.",
     "micro_quest": ["Do the first small physical thing.",
                      "Do the second small physical thing.",
                      "Do the third small physical thing."]},
    {"id": "PRE-001", "type": "EVENT CARD", "objective": "The event text."},
]


def page_html(ids=None, drift_id=None, drop_mq=False) -> str:
    """A minimal page carrying one <article> per card, verbatim text and
    verbatim micro quests, unless overridden."""
    ids = CARDS if ids is None else ids
    parts = []
    for c in ids:
        text = c.get("objective", "")
        if c["id"] == drift_id:
            text = "This corpus text has drifted from the source."
        body = f'<p class="klede">{text}</p>'
        if c.get("micro_quest") and not drop_mq:
            body += "".join(f"<li>{q}</li>" for q in c["micro_quest"])
        parts.append(f'<article class="kcard" id="{c["id"]}">{body}</article>')
    return "".join(parts)


def main() -> int:
    fails = []

    # 1. Clean: every card id present, every sampled field and every micro
    #    quest verbatim.
    problems = preflight.check_primary_bedroom_deck_rendered(CARDS, page_html())
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. A card missing from the page entirely (a half-regenerated build).
    short = [c for c in CARDS if c["id"] != "PRE-001"]
    problems = preflight.check_primary_bedroom_deck_rendered(
        CARDS, page_html(short))
    if not any("PRE-001" in p for p in problems):
        fails.append("a card missing from the page was NOT caught: %s"
                      % problems)

    # 3. An id on the page that does not exist in the corpus (stale content
    #    left behind after a card was renamed or removed upstream).
    ghost = CARDS + [{"id": "PRZ-999", "type": "ZONE CARD",
                       "objective": "A zone that no longer exists."}]
    problems = preflight.check_primary_bedroom_deck_rendered(
        CARDS, page_html(ghost))
    if not any("PRZ-999" in p for p in problems):
        fails.append("a stale extra card id was NOT caught: %s" % problems)

    # 4. Content drift: the corpus changed but the page was never
    #    regenerated, so the rendered text no longer matches word for word.
    problems = preflight.check_primary_bedroom_deck_rendered(
        CARDS, page_html(drift_id="PRR-001"))
    if not any("PRR-001" in p for p in problems):
        fails.append("drifted Room-card text was NOT caught: %s" % problems)

    # 5. A micro quest line missing from the page (this deck's own extra
    #    check beyond what check_kitchen_deck_rendered proves).
    problems = preflight.check_primary_bedroom_deck_rendered(
        CARDS, page_html(drop_mq=True))
    if not any("PRS-001" in p for p in problems):
        fails.append("a standard card's dropped micro quests were NOT "
                      "caught: %s" % problems)

    # 6. Against the real thing: the actual committed corpus and the actual
    #    committed page, not a synthetic stand-in for either. This is the
    #    check that would have caught the real defect the fail-then-pass
    #    proof planted directly on disk while building this gate.
    real_page_path = os.path.join(ROOT, "site", "primary-bedroom-deck.html")
    if os.path.exists(real_page_path):
        sys.path.insert(0, os.path.join(ROOT, "ops", "cardtext"))
        import build_primary_bedroom_deck as PR                 # noqa: E402
        real_cards = PR.build()["cards"]
        real_page = open(real_page_path, encoding="utf-8").read()
        problems = preflight.check_primary_bedroom_deck_rendered(
            real_cards, real_page)
        if problems:
            fails.append("the real committed site/primary-bedroom-deck.html "
                          "does not match the real corpus: %s" % problems)
    else:
        fails.append("site/primary-bedroom-deck.html does not exist; the "
                      "real-site case (6/6) could not run")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_primary_bedroom_deck_rendered: 6/6 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
