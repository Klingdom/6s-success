#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_diagnosis_authoring() actually catches the
two defects M3's own acceptance criteria names (PLAN-MICROZONES-DECKS-APP.md):
a Kitchen pilot zone whose frictions diverge from the real FRICTION CARDs in
ops/cardtext/kitchen-deck.json, and a friction sentence that claims a
customer said something (CLAUDE.md section 8: never fabricate a testimonial).

Run:  python ops/tests/test_diagnosis_authoring.py
"""
import copy
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _load():
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    kdeck_path = os.path.join(ROOT, "ops", "cardtext", "kitchen-deck.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    kdeck = json.load(io.open(kdeck_path, encoding="utf-8"))
    return rooms, kdeck


def main() -> int:
    fails = []
    rooms, kdeck = _load()

    # 1. The real, live corpus passes clean today.
    claims, problems = preflight.check_diagnosis_authoring(rooms, kdeck)
    if claims:
        fails.append("real corpus wrongly flagged a customer claim: %s" % claims)
    if problems:
        fails.append("real corpus wrongly flagged a Kitchen mismatch: %s" % problems)

    # 2. Mutate one Kitchen friction's answer text: must be caught as a
    #    character-for-character divergence, on an in-memory copy only.
    mutated = copy.deepcopy(rooms)
    kitchen_zone = None
    for r in mutated:
        if r.get("room") == "Kitchen":
            for z in r["zones"]:
                if z.get("diagnosis"):
                    kitchen_zone = z
                    break
    if kitchen_zone is None:
        fails.append("no diagnosed Kitchen zone found to mutate; is M3 still unauthored?")
    else:
        kitchen_zone["diagnosis"]["frictions"][0]["branches"][0]["answer"] = \
            "a rewritten answer not in kitchen-deck.json"
        claims2, problems2 = preflight.check_diagnosis_authoring(mutated, kdeck)
        if not problems2:
            fails.append("mutated Kitchen branch text was NOT caught")

    # 3. Plant a customer-attribution claim on an Entryway friction: must be
    #    caught regardless of room.
    mutated2 = copy.deepcopy(rooms)
    entryway_zone = None
    for r in mutated2:
        if r.get("room") == "Entryway":
            for z in r["zones"]:
                if z.get("diagnosis"):
                    entryway_zone = z
                    break
    if entryway_zone is None:
        fails.append("no diagnosed Entryway zone found to mutate; is M3 still unauthored?")
    else:
        entryway_zone["diagnosis"]["frictions"][0]["symptom"] = \
            "A customer told us the tray was always full."
        claims3, problems3 = preflight.check_diagnosis_authoring(mutated2, kdeck)
        if not claims3:
            fails.append("planted customer-attribution claim was NOT caught")

    # 4. The regex itself: real corpus sentences must not false-positive on
    #    ordinary words like "somebody" or a person's own report of a fact.
    if preflight._CUSTOMER_CLAIM.search("Nobody in particular clears what got left on a chair back"):
        fails.append("_CUSTOMER_CLAIM false positive on ordinary friction prose")

    # 5. content.json on disk must be untouched by any of the above (all
    #    mutation happened on deepcopy()s).
    rooms_after, _ = _load()
    if rooms_after != rooms:
        fails.append("content.json on disk changed during this test run")

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 5 cases (real corpus clean, both defect classes caught, "
          "no false positive, corpus untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
