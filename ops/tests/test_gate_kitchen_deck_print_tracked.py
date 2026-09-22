#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_kitchen_deck_print_tracked() catches a missing
Kitchen deck download link, and a redundant onclick tracker that would
double-count it.

2026-09-22: the Kitchen deck gained a real downloadable PDF (GitHub issue
#34, ops/build_kitchen_deck_pdf.py), replacing the old window.print()-only
button. Its download is now tracked by measure.js's own global click
handler (the same one the Entryway deck's PDF link relies on), not by a
per-page onclick, so this test's job changed from "is tracking present" to
"is the real link present, and is a redundant tracker absent". This tests
the pure logic (check_kitchen_deck_print_tracked) with synthetic page text,
so it never touches the real committed page.

Run:  python ops/tests/test_gate_kitchen_deck_print_tracked.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def wrap(cta: str) -> str:
    return f'<div class="cta-row">{cta}<a href="#kitchen-cards">Read the deck</a></div>'


FIXED = wrap(
    '<a class="btn btn-primary btn-lg" '
    'href="downloads/6S-Kitchen-Deck-PrintAndPlay.pdf">'
    "Download the deck, free (PDF)</a>"
)

REGRESSION_NO_LINK = wrap(
    '<button class="btn btn-primary btn-lg" type="button" '
    'onclick="window.print()">Print the 72 fronts</button>'
)

REGRESSION_WRONG_HREF = wrap(
    '<a class="btn btn-primary btn-lg" href="downloads/kitchen.pdf">'
    "Download the deck</a>"
)

REGRESSION_DOUBLE_COUNTS = wrap(
    '<a class="btn btn-primary btn-lg" '
    'href="downloads/6S-Kitchen-Deck-PrintAndPlay.pdf" '
    "onclick=\"if(window.Measure){window.Measure.track('free-download',"
    "{what:'kitchen-deck-pdf',from:'kitchen-deck'});}\">"
    "Download the deck, free (PDF)</a>"
)


def main() -> int:
    fails = []

    # 1. Clean: a real link to the real PDF, no onclick.
    problems = preflight.check_kitchen_deck_print_tracked(FIXED)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. The pre-issue-#34 shape: no download link at all.
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_NO_LINK)
    if not any("no way to take the free Kitchen deck" in p for p in problems):
        fails.append("a missing download link was NOT caught: %s" % problems)

    # 3. A link exists but to the wrong file.
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_WRONG_HREF)
    if not any("no way to take the free Kitchen deck" in p for p in problems):
        fails.append("a wrong-href download link was NOT caught: %s" % problems)

    # 4. The double-count risk: a redundant onclick on top of the real link.
    problems = preflight.check_kitchen_deck_print_tracked(REGRESSION_DOUBLE_COUNTS)
    if not any("double-counts" in p for p in problems):
        fails.append("a redundant onclick tracker was NOT caught: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_kitchen_deck_print_tracked: 4/4 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
