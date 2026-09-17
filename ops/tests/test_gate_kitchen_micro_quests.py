#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_micro_quests() catches a shipped
Kitchen deck page that has lost the 1 to 3 minute micro quest tier
DECK-GAME-DESIGN.md section 2 found missing and section 4.1 put on the 7
STANDARD card backs.

ops/cardtext/build_kitchen_deck.py's own gate() proves the corpus is
internally consistent (3 per standard card, no duplicate line). It says
nothing about whether site/kitchen-deck.html actually carries them: a hand
edit to the page template, or a generator that stops reading
`micro_quest`, would not trip that gate at all. This tests the pure logic
(check_kitchen_micro_quests) with synthetic cards and page text, so it
never touches the real committed page.

Run:  python ops/tests/test_gate_kitchen_micro_quests.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def standards(quests=None):
    """7 STANDARD CARDs, each carrying its own 3 distinct micro quests
    unless `quests` overrides a specific card's list by id."""
    quests = quests or {}
    out = []
    for i in range(1, 8):
        cid = f"KS-{i:03d}"
        mq = quests.get(cid, [f"Move thing {i}a into place.",
                              f"Wipe thing {i}b clean.",
                              f"Put thing {i}c back where it lives."])
        out.append({"id": cid, "type": "STANDARD CARD", "micro_quest": mq})
    return out


def page_html(cards) -> str:
    """A minimal page carrying every card's micro quests, verbatim."""
    import html as _html
    parts = []
    for c in cards:
        items = "".join(f"<li>{_html.escape(q, quote=True)}</li>"
                        for q in c.get("micro_quest", []))
        parts.append(f'<article class="kcard" id="{c["id"]}">'
                     f'<ul class="kmicro">{items}</ul></article>')
    return "".join(parts)


def main() -> int:
    fails = []

    # 1. Clean: every standard card has 3 micro quests, all on the page,
    #    none repeated.
    cards = standards()
    problems = preflight.check_kitchen_micro_quests(cards, page_html(cards))
    if problems:
        fails.append("clean deck wrongly flagged: %s" % problems)

    # 2. A standard card missing one of its 3 (the corpus itself regressed,
    #    not just the page).
    bad = standards({"KS-003": ["Only one quest here."]})
    problems = preflight.check_kitchen_micro_quests(bad, page_html(bad))
    if not any("KS-003" in p for p in problems):
        fails.append("a standard card with 1 micro quest was NOT caught: %s"
                     % problems)

    # 3. The page was never regenerated after a corpus edit, so a real
    #    micro quest line is missing from the rendered HTML.
    cards = standards()
    stale_page = page_html(standards({"KS-005": [
        "A completely different line.",
        "Another different line.",
        "A third different line."]}))
    problems = preflight.check_kitchen_micro_quests(cards, stale_page)
    if not any("KS-005" in p for p in problems):
        fails.append("a micro quest missing from the rendered page was NOT "
                     "caught: %s" % problems)

    # 4. The same micro quest line used on two different zones (a copy/paste
    #    that silently duplicates rather than authors a new one).
    dup = standards({"KS-002": ["Move thing 1a into place.",
                                "Wipe thing 2b clean.",
                                "Put thing 2c back where it lives."]})
    problems = preflight.check_kitchen_micro_quests(dup, page_html(dup))
    if not any("repeats" in p for p in problems):
        fails.append("a repeated micro quest line was NOT caught: %s"
                     % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_micro_quests: 4/4 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
