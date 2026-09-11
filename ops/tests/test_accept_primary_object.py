#!/usr/bin/env python3
"""
Prove the accept test fails on a missing OBJECT and only advises on a
missing condition.

WHY
---
Until 2026-09-11 ops/accept_image.py score() failed on any unmet must_show
item. The "(hard fail, primary object)" label on item 0 was decoration: the
return was (len(reasons) == 0, reasons), so every clause was equally fatal.

Measured that day against three zone heroes marked ok in hero-verdicts.json,
then judged by eye:

  entryway--coat-and-outerwear-zone   FAIL "One coat per person on the rail"
      The image shows two hung coats, three grouped hats, a basket and boots.
      The verdict is wrong. No photograph can show a PER PERSON count, so
      that clause could only ever fail, including on a perfectly good image.

  dining-room--beverage-or-coffee-station   FAIL "Machine"
      The image shows a table, stools and a shelf of crockery, and no coffee
      equipment of any kind. The verdict is right and must stay right.

  family-room--blanket-and-comfort-zone   FAIL "One basket holding four
  throws folded to the same rectangle"
      Baskets and throws are present, heaped rather than folded alike. The
      objects are there and the STANDARD is not, which is worth reporting
      and is not the same thing as the picture being off-brief.

A gate that cannot separate those three cannot gate anything, and wiring it
into shipping as it stood would have rejected the good image with the bad.

Nothing is dropped by the split. The full clause is still asked and still
reported; it moves from fatal to advisory. That is the property most worth
protecting here, so it is asserted explicitly below.

Run:  python ops/tests/test_accept_primary_object.py
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

spec = importlib.util.spec_from_file_location(
    "accept_image", os.path.join(ROOT, "ops", "accept_image.py"))
AI = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AI)


OBJECTS = [
    ("One coat per person on the rail", "coat"),
    ("One basket holding four throws folded to the same rectangle", "basket"),
    ("mugs capped at the number of daily drinkers plus two", "mugs"),
    ("One tray holding keys and sunglasses", "tray"),
    ("Machine", "Machine"),
]


def main() -> int:
    fails = []

    for clause, want in OBJECTS:
        got = AI._object_only(clause)
        if got != want:
            fails.append("object of %r was %r, expected %r"
                         % (clause[:46], got, want))

    # 1. Object present, condition not met: PASS, with the clause reported.
    cl = {"must_show": ["One coat per person on the rail"],
          "primary": "coat", "must_not_show": [], "contradicts": []}
    answers = {AI.question_key("primary", "coat"): True,
               AI.question_key("must_show",
                               "One coat per person on the rail"): False}
    passed, reasons = AI.score(cl, answers)
    if not passed:
        fails.append("a coat visible in frame still failed: %r. This is the "
                     "entryway image, and it is a good image." % reasons)
    if not any("One coat per person" in r for r in reasons):
        fails.append("the unmet clause vanished from the report: %r. "
                     "Advisory must mean reported, not discarded." % reasons)

    # 2. Object absent: FAIL. The beverage station with no machine.
    cl = {"must_show": ["Machine", "grounds"], "primary": "Machine",
          "must_not_show": [], "contradicts": []}
    answers = {AI.question_key("primary", "Machine"): False,
               AI.question_key("must_show", "Machine"): False,
               AI.question_key("must_show", "grounds"): False}
    passed, reasons = AI.score(cl, answers)
    if passed:
        fails.append("a beverage station with no beverage equipment passed")

    # 3. A forbidden object still fails on its own, whatever the objects do.
    cl = {"must_show": ["a tray"], "primary": "tray",
          "must_not_show": ["a malformed object"], "contradicts": []}
    answers = {AI.question_key("primary", "tray"): True,
               AI.question_key("must_show", "a tray"): True,
               AI.question_key("must_not_show", "a malformed object"): True}
    passed, _ = AI.score(cl, answers)
    if passed:
        fails.append("a malformed object passed because the tray was there")

    # 4. Unanswered is still not a pass, even with no primary in the dict.
    passed, reasons = AI.score(
        {"must_show": ["a tray"], "must_not_show": [], "contradicts": []}, {})
    if passed or not reasons:
        fails.append("an entirely unanswered checklist scored as a pass")

    for f in fails:
        print("  FAIL  %s" % f)
    if fails:
        print("  %d problem(s)" % len(fails))
    else:
        print("  ok  the object is fatal, the condition is advisory and "
              "still reported, a forbidden object still fails alone, and "
              "unanswered is not a pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
