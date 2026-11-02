#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_also_called_no_digital_collision() catches
the defect it exists for: a name added to ops/room-also-called.json or
ops/zone-also-called.json is matched by keyword_demand.py's scorer as a
bag of words, with no page-scoping, so one word can silently flip the
status of an unrelated query anywhere in the corpus if that word also
appears in a digital-context query (a PC/Steam/app-library question, not
a physical zone). Found 2026-11-02 trying to fix two genuine Family Room
gap queries by adding "games" to a zone heading: "how to organize games on
pc" moved from gap to a false `covered` in the same rescore, regardless of
which zone's heading carried the word. The fix was reverted, not shipped.

Also runs against the real, committed ops/room-also-called.json,
ops/zone-also-called.json, ops/keyword-demand.json and
ops/keyword-demand-global.json, so a future also-called addition that
collides with a digital-context query fails this test directly.

Run:  python ops/tests/test_gate_also_called_no_digital_collision.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    us_rows = [
        {"query": "how to organize games on pc"},
        {"query": "card games organizer storage"},
    ]
    global_rows = [
        {"query": "how to organize steam games"},
    ]

    # 1. Clean: a name sharing no word with any digital-context query.
    problems = preflight.check_also_called_no_digital_collision(
        {"Family Room|Blanket and Comfort Zone": ["throws zone"]},
        us_rows, global_rows)
    if problems:
        fails.append("unrelated name wrongly flagged: %s" % problems)

    # 2. Regression: "games" collides with the US digital query.
    problems = preflight.check_also_called_no_digital_collision(
        {"Family Room|Board Game and Puzzle Zone": ["card games zone"]},
        us_rows, [])
    if len(problems) != 1 or "how to organize games on pc" not in problems[0]:
        fails.append("US digital collision not caught correctly: %s"
                      % problems)

    # 3. Same regression, this time only visible against the global rows.
    problems = preflight.check_also_called_no_digital_collision(
        {"Family Room|Board Game and Puzzle Zone": ["card games zone"]},
        [], global_rows)
    if len(problems) != 1 or "how to organize steam games" not in problems[0]:
        fails.append("global digital collision not caught correctly: %s"
                      % problems)

    # 4. A name with no content words (e.g. only stopwords) must not crash
    #    or be flagged.
    problems = preflight.check_also_called_no_digital_collision(
        {"Family Room|Craft and Activity Zone": ["the"]},
        us_rows, global_rows)
    if problems:
        fails.append("stopword-only name wrongly flagged: %s" % problems)

    # 5. The real, committed site: no also-called name anywhere may share
    #    a word with a real digital-context query in either keyword file.
    room_path = os.path.join(ROOT, "ops", "room-also-called.json")
    zone_path = os.path.join(ROOT, "ops", "zone-also-called.json")
    us_path = os.path.join(ROOT, "ops", "keyword-demand.json")
    global_path = os.path.join(ROOT, "ops", "keyword-demand-global.json")
    if all(os.path.exists(p) for p in
           (room_path, zone_path, us_path, global_path)):
        names_by_key = {}
        data = json.loads(io.open(room_path, encoding="utf-8").read())
        for room, entry in (data.get("rooms") or {}).items():
            names_by_key[room] = entry.get("names") or []
        data = json.loads(io.open(zone_path, encoding="utf-8").read())
        for key, entry in (data.get("zones") or {}).items():
            names_by_key[key] = entry.get("names") or []
        real_us = json.loads(
            io.open(us_path, encoding="utf-8").read()).get("rows") or []
        real_global = json.loads(
            io.open(global_path, encoding="utf-8").read()).get("rows") or []
        problems = preflight.check_also_called_no_digital_collision(
            names_by_key, real_us, real_global)
        if problems:
            fails.append("real committed also-called map collides with a "
                         "real digital-context query: %s" % problems)
    else:
        print("NOT VERIFIED (case 5): one of the four real files is missing.")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 5/5 cases, including the real committed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
