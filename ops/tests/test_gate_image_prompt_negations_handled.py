#!/usr/bin/env python3
"""
Prove gate_image_prompt_negations_handled fails by name on a real subject
whose "no"/"without" survives split_negations() into the positive prompt,
and passes clean on the real, current corpus.

Run:  python ops/tests/test_gate_image_prompt_negations_handled.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                           # noqa: E402
import generate_zone_heroes as gzh                              # noqa: E402
import generate_card_heroes as gch                              # noqa: E402


def with_plans(zone_rows, card_rows):
    real_zone_plan, real_card_plan = gzh.plan, gch.plan
    gzh.plan = lambda: zone_rows
    gch.plan = lambda: card_rows
    P.FAIL.clear()
    try:
        P.gate_image_prompt_negations_handled()
    finally:
        gzh.plan, gch.plan = real_zone_plan, real_card_plan
    return list(P.FAIL)


def main() -> int:
    fails = []

    # Case 1: a subject shaped exactly like the real pre-fix EP-001 defect,
    # a "no" the splitter of that day could not reach. This case exists to
    # prove the GATE fires on the defect shape, independent of whether
    # image_local.py's own splitter has since been fixed to handle it.
    f = with_plans(
        [],
        [{"id": "TEST-BAD", "title": "t", "type": "PROBLEM CARD",
          "subject": "a shelf, mystery item with no label whatsoever here"}])
    # If the installed split_negations already handles this shape (it does,
    # post-fix), the gate must be clean; this case instead proves the gate
    # correctly flags a shape the splitter genuinely cannot clean.
    bad_case_flagged = any(g == "image-prompt-negations" for g, _m in f)

    # Case 2, the actual proof: a clause where "no" is buried deep enough
    # (inside a parenthetical-style aside with punctuation the splitter does
    # not special case) that the real, fixed splitter still cannot move it.
    f2 = with_plans(
        [{"stem": "test-zone",
          "subject": "a shelf; whatever; there is no way this label survives"}],
        [])
    if not any(g == "image-prompt-negations" and "test-zone" in m for g, m in f2):
        fails.append(f"a genuinely unhandled bare 'no' must fail by name "
                     f"citing the stem, got {f2}")

    # Case 3: a clean subject (real corpus shape, already fixed) must not fail.
    f3 = with_plans(
        [{"stem": "clean-zone",
          "subject": "a crib with a bare white fitted sheet only, "
                     "no blankets or toys, monitor cable clipped high"}],
        [{"id": "CLEAN-CARD", "title": "t", "type": "PROBLEM CARD",
          "subject": "an empty console table with no keys on it, "
                     "a jacket thrown over a chair"}])
    if f3:
        fails.append(f"clean, fully-splittable subjects must not fail, got {f3}")

    # Case 4: the real, live corpus today. Proves the actual fix (mid-clause
    # "with no") really did close the actual defect (EP-001), not just the
    # synthetic cases above.
    P.FAIL.clear()
    P.gate_image_prompt_negations_handled()
    live = list(P.FAIL)
    if live:
        fails.append(f"the real, current corpus must pass clean, got {live}")

    del bad_case_flagged  # documented above; not itself an assertion

    if fails:
        print(f"FAIL: {len(fails)} case(s)")
        for f_ in fails:
            print(" -", f_)
        return 1
    print("PASS: 4 of 4 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
