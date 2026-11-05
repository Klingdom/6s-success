#!/usr/bin/env python3
"""
Prove ops/room_guide_underperformance.py's extra routing rule (matching a
room's own guide article, not just its deck/zone pages) actually fires, and
that its shortfall ranking and double-count guard behave the same way
room_guide_candidates.py's own tested ones do. Fail-then-pass: reverting the
guide_path() match in room_rows() makes the second check below fail (the
guide-routed row would no longer count), confirmed by running this file
against that reverted state before writing it this way.

Run:  python ops/tests/test_room_guide_underperformance.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_zone_pages as bzp                      # noqa: E402
import room_guide_underperformance as rgu            # noqa: E402

failures = []
total = [0]


def check(name, cond):
    total[0] += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


content_rooms = sorted({r["room"] for r in
                         json.loads(open(os.path.join(ROOT, "content/manual/source/content.json")).read())["rooms"]})
real_rooms = rgu.all_rooms()
check("all_rooms() returns exactly the rooms in content.json, derived live not hand-copied",
      real_rooms == content_rooms)
check("every room with a shipped guide has a resolvable guide_path",
      all(rgu.guide_path(r) is not None for r in bzp.ROOM_GUIDES))
check("a room with no guide has no guide_path",
      rgu.guide_path("Nonexistent Test Room") is None)

_room = "Test Room"
_guide_row = {"query": "organize test room the long way", "best_page": "/articles/how-to-test-a-room.html",
              "status": "gap"}
bzp.ROOM_GUIDES["Test Room"] = [("../articles/how-to-test-a-room.html", "x", "x")]
try:
    check("room_rows matches a row whose best_page is the room's own guide article",
          len(rgu.room_rows([_guide_row], _room)) == 1)

    _zone_row = {"query": "organize test room zone", "best_page": "/zones/test-room-the-desk.html", "status": "covered"}
    _deck_row = {"query": "organize test room deck", "best_page": "/test-room-deck.html", "status": "partial"}
    check("room_rows still matches the zone-prefix and deck routes too",
          len(rgu.room_rows([_guide_row, _zone_row, _deck_row], _room)) == 3)

    _room_page_row = {"query": "organize test room lockers", "best_page": "/rooms/test-room.html", "status": "covered"}
    check("room_rows matches a row whose best_page is the bare room page itself, "
          "found 2026-11-05: a room-level also-called synonym (ops/build_zone_pages.py's "
          "also_called_html) renders onto exactly this path, and a query routed there "
          "was being dropped from the room's count entirely rather than credited",
          len(rgu.room_rows([_guide_row, _zone_row, _deck_row, _room_page_row], _room)) == 4)

    _dup = {"query": "organize test room shared", "best_page": "/articles/how-to-test-a-room.html", "status": "gap"}
    _result = rgu.score_room([_dup], [_dup], _room)
    check("a query tracked in both tiers is not double-counted",
          _result["on_topic_rows"] == 1 and len(_result["gap"]) == 1)

    _off_topic = {"query": "test room price comparison", "best_page": "/articles/how-to-test-a-room.html",
                  "status": "gap"}
    _result2 = rgu.score_room([_off_topic], [], _room)
    check("a routed row with no organize/declutter/clean/storage/stock word is excluded as off-topic",
          _result2["on_topic_rows"] == 0)

    _digital = {"query": "how to organize steam game storage", "best_page": "/articles/how-to-test-a-room.html",
                "status": "gap"}
    _result3 = rgu.score_room([_digital], [], _room)
    check("a digital-context on-topic row is excluded from the ranked gap/partial count",
          _result3["on_topic_rows"] == 0)

    _hard_drive = {"query": "how to organize hard drive files", "best_page": "/articles/how-to-test-a-room.html",
                   "status": "gap"}
    _result3b = rgu.score_room([_hard_drive], [], _room)
    check("a 'hard drive' digital-context row is excluded too, not just the single-word DIGITAL terms",
          _result3b["on_topic_rows"] == 0)

    _covered_only = {"query": "organize test room fully", "best_page": "/articles/how-to-test-a-room.html",
                      "status": "covered"}
    _result4 = rgu.score_room([_covered_only], [], _room)
    check("shortfall is 0 when every on-topic row is already covered",
          _result4["shortfall"] == 0.0 and _result4["uncovered_count"] == 0)

    _car_organizer = {"query": "car organizer canadian tire", "best_page": "/articles/how-to-test-a-room.html",
                       "status": "gap"}
    _result5 = rgu.score_room([_car_organizer], [], _room)
    check("an 'off-topic context' row (car organizer product, not garage storage) is excluded",
          _result5["on_topic_rows"] == 0)

    _car_maint = {"query": "organize car maintenance tips", "best_page": "/articles/how-to-test-a-room.html",
                  "status": "partial"}
    _result6 = rgu.score_room([_car_maint], [], _room)
    check("a genuine on-topic car-maintenance row is NOT excluded by that same pattern",
          _result6["on_topic_rows"] == 1)

    _diamond_painting = {"query": "storage organizer for painting with diamonds",
                          "best_page": "/articles/how-to-test-a-room.html", "status": "gap"}
    _result7 = rgu.score_room([_diamond_painting], [], _room)
    check("a 'diamond painting' off-topic-context row is excluded",
          _result7["on_topic_rows"] == 0)

    _benchmark = {"query": "how to organize benchmark advance materials",
                  "best_page": "/articles/how-to-test-a-room.html", "status": "gap"}
    _result8 = rgu.score_room([_benchmark], [], _room)
    check("a 'benchmark advance' (curriculum brand) off-topic-context row is excluded",
          _result8["on_topic_rows"] == 0)

    _pricing_model = {"query": "organize seasonal pricing model",
                       "best_page": "/articles/how-to-test-a-room.html", "status": "gap"}
    _result9 = rgu.score_room([_pricing_model], [], _room)
    check("a 'pricing model' off-topic-context row is excluded",
          _result9["on_topic_rows"] == 0)

    _cleaning_business = {"query": "how to start an outdoor storage business",
                           "best_page": "/articles/how-to-test-a-room.html", "status": "partial"}
    _result10 = rgu.score_room([_cleaning_business], [], _room)
    check("a 'start a business' off-topic-context row is excluded",
          _result10["on_topic_rows"] == 0)

    _cleaning_supplies = {"query": "best way to organize cleaning supplies",
                           "best_page": "/articles/how-to-test-a-room.html", "status": "partial"}
    _result11 = rgu.score_room([_cleaning_supplies], [], _room)
    check("a genuine on-topic 'organize cleaning supplies' row is NOT excluded by the business pattern",
          _result11["on_topic_rows"] == 1)
finally:
    del bzp.ROOM_GUIDES["Test Room"]

if failures:
    print("\n%d FAILED: %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("\n%d/%d passed" % (total[0], total[0]))
