#!/usr/bin/env python3
"""
Prove ops/diagnosis.py's schema check actually catches the four defects it
names (PLAN-MICROZONES-DECKS-APP.md M2's acceptance criteria), rather than
trusting a clean validate.py run once.

Run:  python ops/tests/test_diagnosis_schema.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import diagnosis                                               # noqa: E402


GOOD_ZONE = {
    "zone": "Test Zone",
    "diagnosis": {
        "frictions": [
            {"symptom": "a", "cause": "KC-001", "start_pass": "sort"},
            {"symptom": "b", "cause": "KC-002", "start_pass": "straighten"},
            {"symptom": "c", "cause": "KC-003", "start_pass": "straighten"},
        ],
        "first_15": {
            "action": "Tip the tray onto the table.",
            "victory": "The tray holds keys and nothing else.",
        },
    },
}


def _copy_with(zone_diagnosis_edits, friction_index=None, friction_edits=None):
    import copy
    z = copy.deepcopy(GOOD_ZONE)
    if friction_edits is not None:
        z["diagnosis"]["frictions"][friction_index].update(friction_edits)
    z["diagnosis"].update(zone_diagnosis_edits)
    return z


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
    z = _copy_with({"frictions": GOOD_ZONE["diagnosis"]["frictions"][:2]})
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("needs >= 3" in p for p in problems):
        fails.append("2 frictions was not caught: %s" % problems)

    # 3. A branch naming an unknown cause fails.
    z = _copy_with({}, friction_index=0, friction_edits={"cause": "KC-999"})
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("not a known root cause" in p for p in problems):
        fails.append("unknown cause id was not caught: %s" % problems)

    # 4. A first_15 without a victory fails.
    import copy
    z = copy.deepcopy(GOOD_ZONE)
    del z["diagnosis"]["first_15"]["victory"]
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("missing a victory" in p for p in problems):
        fails.append("missing victory was not caught: %s" % problems)

    # 5. A victory with no verb of state fails (an instruction, not an
    #    observable end state).
    z = copy.deepcopy(GOOD_ZONE)
    z["diagnosis"]["first_15"]["victory"] = "Tip the tray onto the table."
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("not observable" in p for p in problems):
        fails.append("unobservable victory was not caught: %s" % problems)

    # 6. An unknown start_pass fails.
    z = _copy_with({}, friction_index=0, friction_edits={"start_pass": "polish"})
    problems = diagnosis.check_zone_diagnosis(z)
    if not any("not one of" in p for p in problems):
        fails.append("bad start_pass was not caught: %s" % problems)

    # 7. victory_is_observable() itself, both directions.
    if not diagnosis.victory_is_observable("The tray holds keys and nothing else."):
        fails.append("victory_is_observable false negative on a state verb")
    if diagnosis.victory_is_observable("Tip the tray onto the table."):
        fails.append("victory_is_observable false positive on an instruction")

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 8 cases (root causes: %d known)" % len(diagnosis.root_causes.BY_ID))
    return 0


if __name__ == "__main__":
    sys.exit(main())
