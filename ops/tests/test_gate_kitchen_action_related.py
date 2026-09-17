#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_action_related() catches a shipped
Kitchen deck page that has lost the `related` cross-references
DECK-GAME-DESIGN.md 4.2 asked for on all 72 cards (up from 53): the root
causes, zone and standard every ACTION card is now supposed to link to.

ops/cardtext/build_kitchen_deck.py's own gate() proves the corpus itself is
internally consistent (every related.zone/related.standard resolves to a
real card id). It says nothing about whether site/kitchen-deck.html
actually renders them as links: a hand edit to the page template, or a
generator that stops reading `related`, would not trip that gate at all.
This tests the pure logic (check_kitchen_action_related) with synthetic
cards and page text, so it never touches the real committed page.

Run:  python ops/tests/test_gate_kitchen_action_related.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def cards():
    """A minimal deck: one zone action, one whole-kitchen action, the
    root cause/zone/standard cards it points at, and one card missing
    `related` entirely. Every card carries some `related` value, real 72
    of 72 corpus shape, even the three that this test does not otherwise
    exercise (their own actual content is not what is under test here)."""
    return [
        {"id": "KC-001", "type": "ROOT CAUSE CARD", "title": "EXCESS",
         "related": {"actions": ["KA-001"]}},
        {"id": "KC-009", "type": "ROOT CAUSE CARD", "title": "MISSING TRIGGER",
         "related": {"actions": ["KA-015"]}},
        {"id": "KZ-001", "type": "ZONE CARD", "title": "PRIMARY PREP COUNTER",
         "related": {"standard": "KS-001", "actions": ["KA-001"]}},
        {"id": "KS-001", "type": "STANDARD CARD",
         "title": "PRIMARY PREP COUNTER STANDARD",
         "related": {"zone": "KZ-001", "actions": ["KA-001"]}},
        {"id": "KA-001", "type": "ACTION CARD", "title": "CLEAR THE RUN",
         "related": {"root_causes": ["KC-001"], "zone": "KZ-001",
                     "standard": "KS-001"}},
        {"id": "KA-015", "type": "ACTION CARD", "title": "THE FIVE MINUTE CLOSE",
         "related": {"root_causes": ["KC-009"]}},
    ]


def page_html(cards, drop=()) -> str:
    """A minimal page carrying every action card's related links as
    anchors, verbatim, except any (card id, target id) pair in `drop`."""
    import html as _html
    by_id = {c["id"]: c for c in cards}
    parts = []
    for c in cards:
        links = []
        if c["type"] == "ACTION CARD":
            rel = c.get("related") or {}
            targets = list(rel.get("root_causes", []))
            for k in ("zone", "standard"):
                if rel.get(k):
                    targets.append(rel[k])
            for t in targets:
                if (c["id"], t) in drop:
                    continue
                title = _html.escape(by_id[t]["title"], quote=True)
                links.append(f'<a href="#{t}">{title}</a>')
        parts.append(f'<article class="kcard" id="{c["id"]}">'
                     f'{"".join(links)}</article>')
    return "".join(parts)


def main() -> int:
    fails = []

    # 1. Clean: every action card's related links are all on the page.
    deck = cards()
    problems = preflight.check_kitchen_action_related(deck, page_html(deck))
    if problems:
        fails.append("clean deck wrongly flagged: %s" % problems)

    # 2. A card with no related field at all (the corpus itself regressed).
    regressed = cards()
    del regressed[4]["related"]
    problems = preflight.check_kitchen_action_related(
        regressed, page_html(regressed))
    if not any("KA-001" in p or "no related field" in p for p in problems):
        fails.append("a card missing the related field was NOT caught: %s"
                     % problems)

    # 3. The root cause link is real in the corpus but missing from the
    #    rendered page (page never regenerated after a corpus edit).
    deck = cards()
    stale_page = page_html(deck, drop={("KA-001", "KC-001")})
    problems = preflight.check_kitchen_action_related(deck, stale_page)
    if not any("KA-001" in p and "KC-001" in p for p in problems):
        fails.append("a root cause link missing from the rendered page was "
                     "NOT caught: %s" % problems)

    # 4. The zone/standard link is real in the corpus but missing from the
    #    rendered page.
    deck = cards()
    stale_page = page_html(deck, drop={("KA-001", "KZ-001")})
    problems = preflight.check_kitchen_action_related(deck, stale_page)
    if not any("KA-001" in p and "zone" in p for p in problems):
        fails.append("a zone link missing from the rendered page was NOT "
                     "caught: %s" % problems)

    # 5. A whole-kitchen action (no zone/standard) with only its root cause
    #    correctly rendered must not be flagged for a zone/standard it never
    #    had.
    deck = cards()
    problems = preflight.check_kitchen_action_related(deck, page_html(deck))
    if any("KA-015" in p for p in problems):
        fails.append("KA-015 (no zone/standard) was wrongly flagged: %s"
                     % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_action_related: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
