#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_rendered() catches a shipped
Kitchen deck page that has drifted from the real cardtext corpus.

ops/cardtext/build_kitchen_deck.py's own gate() proves the 72 cards are
internally consistent (no orphan root cause, every friction routes
somewhere real). It says nothing about whether site/kitchen-deck.html
actually carries that content: a hand edit to the page, or a half-finished
regeneration, would not trip that gate at all. This tests the pure logic
(check_kitchen_deck_rendered) with synthetic cards and page text, so it
never touches the real committed page.

Run:  python ops/tests/test_gate_kitchen_deck_rendered.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CARDS = [
    {"id": "KR-001", "type": "ROOM CARD", "objective": "The room card text."},
    {"id": "KZ-001", "type": "ZONE CARD", "objective": "The zone card text."},
    {"id": "KF-001", "type": "FRICTION CARD", "objective": "The friction text."},
    {"id": "KC-001", "type": "ROOT CAUSE CARD", "objective": "The cause text."},
    {"id": "KA-001", "type": "ACTION CARD", "goal": "The action goal text."},
    {"id": "KS-001", "type": "STANDARD CARD", "objective": "The standard text."},
    {"id": "KE-001", "type": "EVENT CARD", "objective": "The event text."},
]


def page_html(ids=None, drift_id=None) -> str:
    """A minimal page carrying one <article> per card, verbatim text, unless
    a ROOM ids are overridden (missing/extra) or drift_id's text is mangled."""
    ids = CARDS if ids is None else ids
    parts = []
    for c in ids:
        text = c.get("objective", c.get("goal", ""))
        if c["id"] == drift_id:
            text = "This corpus text has drifted from the source."
        parts.append(f'<article class="kcard" id="{c["id"]}">'
                     f'<p class="klede">{text}</p></article>')
    return "".join(parts)


def main() -> int:
    fails = []

    # 1. Clean: every card id present, every sampled field verbatim.
    problems = preflight.check_kitchen_deck_rendered(CARDS, page_html())
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. A card missing from the page entirely (a half-regenerated build).
    short = [c for c in CARDS if c["id"] != "KE-001"]
    problems = preflight.check_kitchen_deck_rendered(CARDS, page_html(short))
    if not any("KE-001" in p for p in problems):
        fails.append("a card missing from the page was NOT caught: %s"
                      % problems)

    # 3. An id on the page that does not exist in the corpus (stale content
    #    left behind after a card was renamed or removed upstream).
    ghost = CARDS + [{"id": "KZ-999", "type": "ZONE CARD",
                       "objective": "A zone that no longer exists."}]
    problems = preflight.check_kitchen_deck_rendered(CARDS, page_html(ghost))
    if not any("KZ-999" in p for p in problems):
        fails.append("a stale extra card id was NOT caught: %s" % problems)

    # 4. Content drift: the corpus changed but the page was never
    #    regenerated, so the rendered text no longer matches word for word.
    problems = preflight.check_kitchen_deck_rendered(
        CARDS, page_html(drift_id="KR-001"))
    if not any("KR-001" in p for p in problems):
        fails.append("drifted Room-card text was NOT caught: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_deck_rendered: 4/4 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
