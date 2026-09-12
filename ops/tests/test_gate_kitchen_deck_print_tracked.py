#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_print_tracked() catches a Kitchen
deck print button that calls window.print() with no analytics tracking.

PLAN-MICROZONES-DECKS-APP.md K6 requires a 'deck_full_download' equivalent
to be emitted and readable. Before the fix this proves, the button read
plain onclick="window.print()": every reader who took the free deck was
invisible to analytics, the exact gap K6 names. This tests the pure logic
(check_kitchen_deck_print_tracked) with synthetic page text, so it never
touches the real committed page.

Run:  python ops/tests/test_gate_kitchen_deck_print_tracked.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def wrap(button: str) -> str:
    return f'<div class="cta-row">{button}<a href="#kitchen-cards">Read the deck</a></div>'


FIXED = wrap(
    '<button class="btn btn-primary btn-lg" type="button" '
    "onclick=\"if(window.Measure){window.Measure.track('free-download',"
    "{what:'kitchen-deck-print',from:'kitchen-deck'});}window.print()\">"
    "Print the 72 fronts</button>"
)

REGRESSION_NO_TRACKING = wrap(
    '<button class="btn btn-primary btn-lg" type="button" '
    'onclick="window.print()">Print the 72 fronts</button>'
)

REGRESSION_WRONG_EVENT = wrap(
    '<button class="btn btn-primary btn-lg" type="button" '
    "onclick=\"if(window.Measure){window.Measure.track('deck-print',{});}"
    'window.print()">Print the 72 fronts</button>'
)

REGRESSION_NO_BUTTON = wrap(
    '<a class="btn btn-primary btn-lg" href="downloads/kitchen.pdf">'
    "Download the deck</a>"
)


def main() -> int:
    fails = []

    # 1. Clean: the button calls window.Measure.track with 'free-download'.
    problems = preflight.check_kitchen_deck_print_tracked(FIXED)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. The original defect: window.print() with no tracking at all.
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_NO_TRACKING)
    if not any("invisible to analytics" in p for p in problems):
        fails.append("an untracked print button was NOT caught: %s" % problems)

    # 3. Tracked, but under a private event name nobody else reads.
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_WRONG_EVENT)
    if not any("free-download" in p for p in problems):
        fails.append("a wrong event name was NOT caught: %s" % problems)

    # 4. The button itself is missing entirely (a redesign that dropped it).
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_NO_BUTTON)
    if not any("no 'Print the 72 fronts' button" in p for p in problems):
        fails.append("a missing print button was NOT caught: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_deck_print_tracked: 4/4 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
