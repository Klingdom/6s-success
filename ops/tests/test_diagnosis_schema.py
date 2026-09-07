#!/usr/bin/env python3
"""
Prove ops/diagnosis.py's schema check actually catches the four defects it
names (PLAN-MICROZONES-DECKS-APP.md M2's acceptance criteria), rather than
trusting a clean validate.py run once.

Run:  python ops/tests/test_diagnosis_schema.py
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import diagnosis                                               # noqa: E402


GOOD_ZONE = {
    "zone": "Test Zone",
    "diagnosis": {
        "frictions": [
            {"symptom": "a", "branches": [{"answer": "x", "cause": "KC-001"},
                                           {"answer": "y", "cause": "KC-002"}]},
            {"symptom": "b", "branches": [{"answer": "x", "cause": "KC-003"}]},
            {"symptom": "c", "branches": [{"answer": "x", "cause": "KC-004"}]},
        ],
        "first_15": {
            "action": "Tip the tray onto the table.",
            "victory": "The tray holds keys and nothing else.",
        },
    },
}


def main() -> int:
    fails = []

    # 0. A zone with no diagnosis key at all must pass (mid-migration).
    problems = diagnosis.check_zone_diagnosis({"zone": "Untouched"})
    if problems:
        fails.append("zone with no diagnosis key was flagged: %s" % problems)

    # 1. A well-formed zone passes.
    problems = diagnosis.check_zone_diagnosis(GOOD_ZONE)
    if problems:
        fails.append("well-formed zone was flagged: %s" % problems)

    # 2. Fewer than 3 frictions fails.
    z = copy.deepcopy(GOOD_ZONE)
    z["diagnosis"]["frictions"] = z["diagnosis"]["frictions"][:2]
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("needs >= 3" in p for p in problems):
        fails.append("2 frictions was not caught: %s" % problems)

    # 3. A branch naming an unknown cause fails.
    z = copy.deepcopy(GOOD_ZONE)
    z["diagnosis"]["frictions"][0]["branches"][0]["cause"] = "KC-999"
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("not a known root cause" in p for p in problems):
        fails.append("unknown cause id was not caught: %s" % problems)

    # 4. A friction with no branches at all fails.
    z = copy.deepcopy(GOOD_ZONE)
    z["diagnosis"]["frictions"][0]["branches"] = []
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("has no branches" in p for p in problems):
        fails.append("empty branches was not caught: %s" % problems)

    # 5. A first_15 without a victory fails.
    z = copy.deepcopy(GOOD_ZONE)
    del z["diagnosis"]["first_15"]["victory"]
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("missing a victory" in p for p in problems):
        fails.append("missing victory was not caught: %s" % problems)

    # 6. A victory that is really the instruction repeated (an imperative
    #    opening, the plan's own example) fails.
    z = copy.deepcopy(GOOD_ZONE)
    z["diagnosis"]["first_15"]["victory"] = "Tip the tray onto the table."
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("not observable" in p for p in problems):
        fails.append("unobservable victory was not caught: %s" % problems)

    # 7. victory_is_observable() itself, both directions.
    if not diagnosis.victory_is_observable("The tray holds keys and nothing else."):
        fails.append("victory_is_observable false negative on a real state description")
    if diagnosis.victory_is_observable("Tip the tray onto the table."):
        fails.append("victory_is_observable false positive on an instruction")

    # 8. The real Kitchen deck's own friction shape (branches with 2-3
    #    causes each) passes untouched, proving the schema actually fits the
    #    data M3 has to reuse rather than only a synthetic fixture.
    import json
    kd = json.load(open(os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json"),
                         encoding="utf-8"))
    kf = [c for c in kd["cards"] if c["type"] == "FRICTION CARD"]
    real_zone = {
        "zone": "Kitchen import check",
        "diagnosis": {
            "frictions": [
                {"symptom": f["title"],
                 "branches": [{"answer": b["answer"], "cause": b["root_cause"]}
                              for b in f["branches"]]}
                for f in kf[:3]
            ],
            "first_15": GOOD_ZONE["diagnosis"]["first_15"],
        },
    }
    problems = diagnosis.check_zone_diagnosis(real_zone)
    if problems:
        fails.append("real Kitchen friction cards did not pass the schema: %s"
                      % problems)

    # 9. Every real 15-minute ACTION CARD victory_condition in the Kitchen
    #    deck passes. This is the case that caught the first draft's
    #    state-verb whitelist rejecting 4 of these 9 real, already-shipped
    #    victories (e.g. "Dry basin, two tools standing, nothing lying in
    #    water."), before any zone was authored against that draft.
    real_victories = [c["victory_condition"] for c in kd["cards"]
                       if c["type"] == "ACTION CARD"
                       and c.get("time_target_minutes") == 15]
    if len(real_victories) < 5:
        fails.append("expected several real 15-minute victories, found %d"
                      % len(real_victories))
    bad = [v for v in real_victories if not diagnosis.victory_is_observable(v)]
    if bad:
        fails.append("real victory condition(s) wrongly flagged: %s" % bad)

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED %d cases (root causes: %d known, %d real victories checked)"
          % (10, len(diagnosis.root_causes.BY_ID), len(real_victories)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
