#!/usr/bin/env python3
"""
Prove ops/build_card_template.py's fit_front() handles a one-line action.

Found cold-reading build_card_template.py 2026-09-26: fit_front()'s main
loop tried `for act_lines in range(need, 1, -1)`, which is empty whenever
`need` (the action's own natural line count) is 1. Every card whose action
text already fits on a single line therefore skipped the whole fitting loop
and fell straight to the "nothing fitted at a legible size" fallback,
which unconditionally sets trimmed=True (even though nothing was cut) and
drops the tagline entirely (tag=""), regardless of how much room the card
actually has. None of the 89 live Entryway cards currently has a one-line
action (checked directly against the real corpus), so this has shipped no
visible defect yet, but the next short quick_win/game_effect/objective
written for this deck would silently lose its tagline and be misreported
as trimmed in build_card_template.py's own summary line. Fixed by widening
the range to `range(need, 0, -1)` so a one-line action is tried like any
other line count.

Run:  python ops/tests/test_build_card_template_fit_front.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_card_template as T                                 # noqa: E402


def main() -> int:
    fails = []

    # 1. A card whose action fits on one line must not be reported as
    #    trimmed, and must keep a tagline that easily has room to fit.
    c = {
        "id": "ZZ-999", "title": "Test Card", "type": "action card",
        "quick_win": "Wipe it down.",
        "tagline": "Keep it simple.",
    }
    plan = T.fit_front(c, set())
    if plan["trimmed"] is not False:
        fails.append(f"one-line action falsely reported trimmed=True: {plan}")
    if plan["action"] != "Wipe it down.":
        fails.append(f"one-line action text was altered: {plan['action']!r}")
    if plan["tag"] != "Keep it simple.":
        fails.append(f"tagline was dropped despite ample room: {plan!r}")

    # 2. A card whose action genuinely needs several lines and does not fit
    #    at full length must still hit the real trimming path (not report
    #    trimmed=False and must still return non-empty action text).
    long_action = ("Clear every surface in the zone, sort what you find into "
                    "keep, donate and trash, wipe every shelf from back to "
                    "front, put every kept item back in a labelled spot, and "
                    "write today's date on the inside of the door so the next "
                    "reset has a baseline to compare against.")
    c2 = {"id": "ZZ-998", "title": "Long Card", "type": "action card",
          "quick_win": long_action, "tagline": "Deck flavour line."}
    plan2 = T.fit_front(c2, set())
    if not plan2["action"]:
        fails.append(f"long action produced no text at all: {plan2!r}")
    if len(plan2["action"]) >= len(long_action):
        fails.append(
            f"long action expected to be cut, was not: {plan2!r}")

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 2/2 cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
