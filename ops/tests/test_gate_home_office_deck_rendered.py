#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_home_office_deck_rendered() catches a shipped
Home Office deck page that has drifted from the real cardtext corpus.

Same shape as ops/tests/test_gate_entryway_deck_rendered.py, for the fourth
room's deck (BACKLOG-2026-09-07.md B9). Tests the pure logic
(check_home_office_deck_rendered) with synthetic cards and page text, so it
never touches the real committed page.

Run:  python ops/tests/test_gate_home_office_deck_rendered.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CARDS = [
    {"id": "HOR-001", "type": "ROOM CARD", "objective": "The room card text."},
    {"id": "HOZ-001", "type": "ZONE CARD", "objective": "The zone card text."},
    {"id": "HOF-001", "type": "FRICTION CARD", "objective": "The friction text."},
    {"id": "KC-001", "type": "ROOT CAUSE CARD", "objective": "The cause text."},
    {"id": "HOA-001", "type": "ACTION CARD", "objective": "The action goal text."},
    {"id": "HOS-001", "type": "STANDARD CARD", "objective": "The standard text.",
     "micro_quest": ["Do the first small physical thing.",
                      "Do the second small physical thing.",
                      "Do the third small physical thing."]},
    {"id": "HOE-001", "type": "EVENT CARD", "objective": "The event text."},
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
    problems = preflight.check_home_office_deck_rendered(CARDS, page_html())
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. A card missing from the page entirely (a half-regenerated build).
    short = [c for c in CARDS if c["id"] != "HOE-001"]
    problems = preflight.check_home_office_deck_rendered(CARDS, page_html(short))
    if not any("HOE-001" in p for p in problems):
        fails.append("a card missing from the page was NOT caught: %s"
                      % problems)

    # 3. An id on the page that does not exist in the corpus (stale content
    #    left behind after a card was renamed or removed upstream).
    ghost = CARDS + [{"id": "HOZ-999", "type": "ZONE CARD",
                       "objective": "A zone that no longer exists."}]
    problems = preflight.check_home_office_deck_rendered(CARDS, page_html(ghost))
    if not any("HOZ-999" in p for p in problems):
        fails.append("a stale extra card id was NOT caught: %s" % problems)

    # 4. Content drift: the corpus changed but the page was never
    #    regenerated, so the rendered text no longer matches word for word.
    problems = preflight.check_home_office_deck_rendered(
        CARDS, page_html(drift_id="HOR-001"))
    if not any("HOR-001" in p for p in problems):
        fails.append("drifted Room-card text was NOT caught: %s" % problems)

    # 5. A micro quest line missing from the page (this deck's own extra
    #    check beyond what check_kitchen_deck_rendered proves).
    problems = preflight.check_home_office_deck_rendered(
        CARDS, page_html(drop_mq=True))
    if not any("HOS-001" in p for p in problems):
        fails.append("a standard card's dropped micro quests were NOT "
                      "caught: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_home_office_deck_rendered: 5/5 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
