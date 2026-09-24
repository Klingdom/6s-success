#!/usr/bin/env python3
"""
Prove preflight's check_diagnosis_branch_shape() goes non-empty on each real
defect shape it was written for, and stays silent on the corpus as it stands.

WHY THIS EXISTS
---------------
The gate was written on 2026-09-24 after a hand-authoring pass put wrong cause
IDs into two rooms. The semantic half of that mistake is not machine-checkable
and this gate does not pretend to catch it. The structural half is, and every
case below is a defect that was actually present in the corpus that morning,
not an invented one:

  - two branches of one friction reaching the same cause (two different
    labelling answers both assigned KC-005, and later three safety answers all
    assigned KC-010 by the very fix that was meant to correct the first);
  - two frictions in one zone repeating each other's branch answers (Linen and
    Towel Storage asked "I can never find a matching set" and "half of it is
    never used" with substantially the same answers);
  - a cause ID that does not exist, which renders a branch with no
    confirmation test at all.

A gate nobody has watched fail is a gate nobody knows works, so each case
below constructs the defect and asserts the specific sentence a reader needs.

Run:  python ops/tests/test_diagnosis_branch_shape.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402
from root_causes import CAUSES                                  # noqa: E402

VALID = {c["id"] for c in CAUSES}


def _zone(frictions, first_15=True):
    z = {"zone": "Test Zone", "diagnosis": {"frictions": frictions}}
    if first_15:
        z["diagnosis"]["first_15"] = {"action": "Do the thing.",
                                      "victory": "The thing is done."}
    return {"room": "Test Room", "zones": [z]}


def _friction(symptom, pairs):
    return {"symptom": symptom,
            "branches": [{"answer": a, "cause": c} for a, c in pairs]}


def _ok_frictions():
    return [
        _friction("One.", [("a", "KC-001"), ("b", "KC-002"), ("c", "KC-003")]),
        _friction("Two.", [("d", "KC-004"), ("e", "KC-005"), ("f", "KC-006")]),
        _friction("Three.", [("g", "KC-007"), ("h", "KC-008"), ("i", "KC-009")]),
    ]


def case_clean_block_is_silent():
    problems = preflight.check_diagnosis_branch_shape(
        [_zone(_ok_frictions())], VALID)
    assert problems == [], problems


def case_same_cause_twice_in_one_friction():
    fr = _ok_frictions()
    fr[0] = _friction("The unit rocks.", [
        ("not fixed to the wall", "KC-010"),
        ("heavy binders on top", "KC-010"),
        ("stands on carpet", "KC-007")])
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "same cause twice" in problems[0], problems[0]
    assert "KC-010" in problems[0], problems[0]
    assert "The unit rocks." in problems[0], problems[0]


def case_three_branches_all_one_cause_is_still_one_problem():
    fr = _ok_frictions()
    fr[0] = _friction("All the same.", [
        ("x", "KC-010"), ("y", "KC-010"), ("z", "KC-010")])
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "KC-010" in problems[0], problems[0]


def case_unknown_cause_id():
    fr = _ok_frictions()
    fr[0]["branches"][1]["cause"] = "KC-999"
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "not a real cause ID" in problems[0], problems[0]
    assert "KC-999" in problems[0], problems[0]
    assert "confirmation test" in problems[0], problems[0]


def case_two_frictions_repeating_each_others_answers():
    fr = _ok_frictions()
    fr[1] = _friction("Written twice.", [
        ("a", "KC-004"), ("b", "KC-005"), ("zzz", "KC-006")])
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "one friction written twice" in problems[0], problems[0]
    assert "2 identical branch answer" in problems[0], problems[0]


def case_one_shared_answer_is_tolerated():
    """Two frictions CAN legitimately share a single cause of their own.

    Only a second shared answer says the friction was written twice. Pinning
    this stops a future tightening from making the gate noisy enough to be
    ignored, which is how a gate stops being read.
    """
    fr = _ok_frictions()
    fr[1]["branches"][0]["answer"] = "a"
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert problems == [], problems


def case_too_few_frictions():
    fr = _ok_frictions()[:2]
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "2 friction(s)" in problems[0], problems[0]


def case_single_branch_is_not_a_diagnosis():
    fr = _ok_frictions()
    fr[2] = _friction("Only one way.", [("a", "KC-001")])
    problems = preflight.check_diagnosis_branch_shape([_zone(fr)], VALID)
    assert len(problems) == 1, problems
    assert "not a diagnosis" in problems[0], problems[0]


def case_first_15_must_carry_both_halves():
    for missing in ("action", "victory"):
        z = _zone(_ok_frictions())
        del z["zones"][0]["diagnosis"]["first_15"][missing]
        problems = preflight.check_diagnosis_branch_shape([z], VALID)
        assert len(problems) == 1, (missing, problems)
        assert "first_15" in problems[0], problems[0]


def case_zone_without_diagnosis_is_not_a_fault():
    """89 zones carry no diagnosis yet. That is D-026's backlog, not a defect
    this gate should shout about, or it would fail every run until all 114 are
    authored and would be switched off long before then."""
    rooms = [{"room": "R", "zones": [{"zone": "Bare"}]}]
    assert preflight.check_diagnosis_branch_shape(rooms, VALID) == []


def case_live_corpus_is_clean():
    """The real corpus, whatever it currently holds: re-derived, not pinned to
    a count that would fail as a reward for authoring the next room."""
    fp = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(fp, encoding="utf-8"))["rooms"]
    problems = preflight.check_diagnosis_branch_shape(rooms, VALID)
    assert problems == [], problems
    authored = sum(1 for r in rooms for z in r.get("zones", [])
                   if z.get("diagnosis"))
    assert authored >= 25, authored


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
