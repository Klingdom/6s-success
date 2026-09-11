#!/usr/bin/env python3
"""
Prove gate_quest_data_heroes_current() catches a hero withdrawn from
ops/hero-verdicts.json after site/assets/js/quest-data.js was last built.

Found 2026-09-11: kitchen--primary-prep-counter's "ok" verdict was withdrawn
(the photo contradicted the zone's own done_looks_like), site/zones/ was
regenerated to drop it, but quest-data.js was not, because it is a separate
generator (ops/build_quest.py) nothing chains after a hero-verdicts.json
change. The committed file kept shipping the withdrawn image on the Home
Quest's own symptom-entry screen. Reproduced directly: a real rebuild
(ops/build_quest.py) after the withdrawal changed exactly one field, that
symptom's own "img", from the withdrawn stem to null.

Run:  python ops/tests/test_gate_quest_data_heroes.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Pure function: a zone img and a symptom img both still approved.
    data = {
        "rooms": [{"zones": [{"zone": "Landing Zone", "img": "entryway--landing-zone"}]}],
        "symptoms": [{"symptom": "clutter", "img": "entryway--landing-zone"}],
    }
    stale = preflight.quest_data_stale_heroes(data, {"entryway--landing-zone"})
    if stale:
        fails.append(f"an approved stem was wrongly flagged stale: {stale}")

    # 2. The regression itself: a symptom names a stem no longer approved.
    data2 = {
        "rooms": [{"zones": [{"zone": "Primary Prep Counter",
                               "img": "kitchen--primary-prep-counter"}]}],
        "symptoms": [{"symptom": "counter chaos",
                      "img": "kitchen--primary-prep-counter"}],
    }
    stale2 = preflight.quest_data_stale_heroes(data2, set())
    if "kitchen--primary-prep-counter" not in stale2:
        fails.append(f"a withdrawn stem in both a zone and a symptom was "
                      f"not caught: {stale2}")
    elif not any("symptom" in w for w in stale2["kitchen--primary-prep-counter"]):
        fails.append(f"the symptom usage was not named, only the zone one: "
                      f"{stale2}")

    # 3. A zone with no img at all: never flagged, nothing to check.
    data3 = {"rooms": [{"zones": [{"zone": "No Picture Zone"}]}], "symptoms": []}
    stale3 = preflight.quest_data_stale_heroes(data3, set())
    if stale3:
        fails.append(f"a zone with no img was wrongly flagged: {stale3}")

    # 4. End to end against the real committed file, with heroes() stubbed
    # to prove the gate would have failed had the withdrawal not been
    # carried into a real rebuild of quest-data.js (this run's own fix).
    real_path = os.path.join(ROOT, "site", "assets", "js", "quest-data.js")
    if not os.path.exists(real_path):
        print("  (skipped: site/assets/js/quest-data.js not found)")
    else:
        import importlib
        BQ = importlib.import_module("build_quest")
        real_heroes = BQ.heroes
        try:
            BQ.heroes = lambda: set()  # nothing at all is approved
            preflight.FAIL, preflight.WARN = [], []
            preflight.gate_quest_data_heroes_current()
            if not preflight.FAIL:
                fails.append("stubbing heroes() to the empty set did not "
                             "fail the gate against the real file, so the "
                             "real file must carry no img fields at all, "
                             "which is not the shape the app ships")
            elif "quest-data-heroes-current" not in preflight.FAIL[0][0]:
                fails.append(f"wrong gate name: {preflight.FAIL}")
        finally:
            BQ.heroes = real_heroes

        # And the real file, against the real current approval set, is clean:
        # proves this run's own fix (rebuilding quest-data.js after the
        # withdrawal) actually holds.
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_quest_data_heroes_current()
        if preflight.FAIL:
            fails.append(f"real committed quest-data.js still names a "
                         f"withdrawn hero: {preflight.FAIL}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_quest_data_heroes_current, 4 case(s) pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
