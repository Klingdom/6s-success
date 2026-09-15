#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_pricing_deck_ladder_current() can actually
fail, and that it stays quiet on the real, corrected file.

Found 2026-09-15: PRICING.md's card-deck section described a four-tier
ladder for a 46-card Entryway deck (free / $12 PDF / $29 printed / $34
bundle) for weeks after the deck actually shipped as an 88-card, free-only
deck (site/assets/js/data.js carries exactly one deck SKU, DECK-ENTRY,
price 0). GitHub issue #20, which the ladder answers, had sat open and
unchanged since 2026-08-20 asking for a decision that was no longer live.
Every sibling money-adjacent document already has a gate for this drift
shape; this is PRICING.md's.

Run:  python ops/tests/test_gate_pricing_deck_ladder_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. No staleness marker at all: the real defect shape found 2026-09-15,
    #    a stale ladder with nothing telling a reader it is stale. Must fire.
    stale_text = ("## 2. Card decks\n\n### The ladder\n\n"
                  "| 1 | Entryway Deck, print at home, 46 cards | Free |\n")
    problems = preflight.pricing_deck_ladder_problems(stale_text, "88")
    if not problems:
        fails.append("no staleness marker at all: expected a problem, got none")

    # 2. The real, corrected text (marker present, live count cited): must
    #    not fire. This is the actual committed state as of this fix.
    fixed_text = ("### 0.6 Section 2's whole card-deck ladder is stale, "
                  "found 2026-09-15\n\n"
                  "the live DECK-ENTRY catalogue entry says 88 cards.\n\n"
                  "**Stale, see section 0.6.** Tier 1 is now 88 cards.\n")
    problems = preflight.pricing_deck_ladder_problems(fixed_text, "88")
    if problems:
        fails.append("marker present and live count cited, but still "
                     "flagged: %r" % (problems,))

    # 3. Marker present, but the live count itself was edited out or the
    #    deck grew again and nobody updated section 0.6: must fire. This is
    #    the regression this gate exists to catch going forward, not just
    #    the one-time defect in case 1.
    drifted_text = ("### 0.6 Section 2's whole card-deck ladder is stale, "
                     "found 2026-09-15\n\n"
                     "the live DECK-ENTRY catalogue entry says 88 cards.\n")
    problems = preflight.pricing_deck_ladder_problems(drifted_text, "95")
    if not problems:
        fails.append("marker present but live count (95) not cited: "
                     "expected a problem, got none")

    # 4. Marker present as a case-insensitive match (a future edit might
    #    re-capitalise the heading): must not fire on casing alone.
    cased_text = ("### 0.6 Section 2's Whole Card-Deck Ladder Is Stale\n\n"
                  "88 cards.\n")
    problems = preflight.pricing_deck_ladder_problems(cased_text, "88")
    if problems:
        fails.append("case-insensitive marker match wrongly flagged: %r"
                     % (problems,))

    # 5. The real, currently committed PRICING.md, read from disk: must be
    #    clean against the real live DECK-ENTRY count. Ties this test to the
    #    actual repository state, not only to synthetic fixtures.
    import io
    import json
    import re
    pricing_path = os.path.join(ROOT, "PRICING.md")
    js_path = os.path.join(ROOT, "site", "assets", "js", "data.js")
    if os.path.exists(pricing_path) and os.path.exists(js_path):
        text = io.open(pricing_path, encoding="utf-8").read()
        js = io.open(js_path, encoding="utf-8").read()
        cat = json.loads(js[js.index("["):js.rindex("]") + 1])
        deck = next((p for p in cat if p.get("sku") == "DECK-ENTRY"), None)
        if deck:
            m = re.search(r"(\d+)\s+cards",
                          f"{deck.get('variant', '')} {deck.get('blurb', '')}")
            if m:
                problems = preflight.pricing_deck_ladder_problems(
                    text, m.group(1))
                if problems:
                    fails.append("the real, committed PRICING.md fails its "
                                 "own gate: %r" % (problems,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
