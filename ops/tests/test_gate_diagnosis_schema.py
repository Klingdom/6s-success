#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_diagnosis_schema() is actually wired to
ops/diagnosis.py's schema check, not just present as dead code.

ops/diagnosis.py's own logic (check_zone_diagnosis, victory_is_observable)
is already unit-tested in isolation by test_diagnosis_schema.py, on
synthetic fixtures. Nothing before this gate ever called it against the
real corpus, or from anywhere preflight.py runs unattended, the same gap
accept_image.py had (found and gated 2026-09-08). This test proves the
missing half: that gate_diagnosis_schema() reads content.json, calls
diagnosis.check_all(), and reports a real problem through preflight's own
fail() mechanism, using a temporary copy of the real content.json so the
repository file is never touched.

Run:  python ops/tests/test_gate_diagnosis_schema.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")


def _run_gate_against(rooms_doc):
    """Point gate_diagnosis_schema at a throwaway content.json holding
    rooms_doc, run it, restore preflight.ROOT, and return the FAIL list
    recorded during that one call.
    """
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_src_dir = os.path.join(tmp_dir, "content", "manual", "source")
        os.makedirs(tmp_src_dir)
        tmp_src = os.path.join(tmp_src_dir, "content.json")
        json.dump(rooms_doc, io.open(tmp_src, "w", encoding="utf-8"))

        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before = len(preflight.FAIL)
        try:
            preflight.gate_diagnosis_schema()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before:]
    finally:
        shutil.rmtree(tmp_dir)


GOOD_ROOMS = {"rooms": [{"room": "Test Room", "zones": [{
    "zone": "Test Zone",
    "diagnosis": {
        "frictions": [
            {"symptom": "a", "branches": [{"answer": "x", "cause": "KC-001"}]},
            {"symptom": "b", "branches": [{"answer": "x", "cause": "KC-002"}]},
            {"symptom": "c", "branches": [{"answer": "x", "cause": "KC-003"}]},
        ],
        "first_15": {
            "action": "Tip the tray onto the table.",
            "victory": "The tray holds keys and nothing else.",
        },
    },
}]}]}


def main() -> int:
    fails = []

    # 1. A well-formed corpus reports no failures through the gate.
    problems = _run_gate_against(GOOD_ROOMS)
    if problems:
        fails.append("well-formed corpus wrongly failed the gate: %s" % problems)

    # 2. An unknown cause id anywhere in the corpus fails the gate, naming
    #    the zone, the same defect class planted live against the real
    #    content.json (2026-09-08) and confirmed to turn preflight red.
    import copy
    bad = copy.deepcopy(GOOD_ROOMS)
    bad["rooms"][0]["zones"][0]["diagnosis"]["frictions"][0]["branches"][0]["cause"] = "NOT-A-REAL-CAUSE"
    problems = _run_gate_against(bad)
    if not any("Test Zone" in msg and "not a known root cause" in msg
               for _, msg in problems):
        fails.append("unknown cause id was not caught by the gate: %s" % problems)

    # 3. Too few frictions fails the gate.
    thin = copy.deepcopy(GOOD_ROOMS)
    thin["rooms"][0]["zones"][0]["diagnosis"]["frictions"] = \
        thin["rooms"][0]["zones"][0]["diagnosis"]["frictions"][:2]
    problems = _run_gate_against(thin)
    if not any("needs >= 3" in msg for _, msg in problems):
        fails.append("2 frictions was not caught by the gate: %s" % problems)

    # 4. The real, current content.json passes clean right now: 12 of 114
    #    zones carry a diagnosis block (M4/M6, PLAN-MICROZONES-DECKS-APP.md)
    #    and all of them already validate.
    real_rooms = json.load(io.open(REAL_SRC, encoding="utf-8"))
    problems = _run_gate_against(real_rooms)
    if problems:
        fails.append("the real, live content.json failed the gate: %s" % problems)

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 4 cases (gate_diagnosis_schema wired to ops/diagnosis.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
