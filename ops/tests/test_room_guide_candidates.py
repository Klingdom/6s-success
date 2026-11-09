#!/usr/bin/env python3
"""
Prove GUIDE_LESS_ROOMS in ops/room_guide_candidates.py is derived live from
ROOM_GUIDES rather than hand-copied. Found 2026-11-02: the hand-maintained
list still named "Kids Bedroom" the same cycle that room's guide shipped and
ROOM_GUIDES picked it up, so the tool kept scoring an already-answered room.
This test fails on a reintroduced hand-maintained list (it would list 20-12=8
rooms only by coincidence matching today's content; a stale manual list
drifts the next time a guide ships, this derived one cannot).

Run:  python ops/tests/test_room_guide_candidates.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_zone_pages as bzp                                   # noqa: E402
import room_guide_candidates as rgc                               # noqa: E402

failures = []
total = [0]


def check(name, cond):
    total[0] += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


all_rooms = {r["room"] for r in
             json.loads(open(os.path.join(ROOT, "content/manual/source/content.json")).read())["rooms"]}
guided = set(bzp.ROOM_GUIDES.keys())
expected = sorted(all_rooms - guided)

check("GUIDE_LESS_ROOMS matches content.json minus ROOM_GUIDES",
      rgc.GUIDE_LESS_ROOMS == expected)
check("a room with a shipped guide is never in GUIDE_LESS_ROOMS",
      guided.isdisjoint(set(rgc.GUIDE_LESS_ROOMS)))
check("every guide-less room is a real room", set(rgc.GUIDE_LESS_ROOMS) <= all_rooms)
check("guide_less_rooms() is re-callable and stable",
      rgc.guide_less_rooms() == rgc.GUIDE_LESS_ROOMS)

# Found 2026-11-02, cold-reading this file: 1069 real queries are tracked
# in both ops/keyword-demand.json and ops/keyword-demand-global.json.
# score_room() used to combine them with a plain `us + gl`, counting any
# query present in both tiers twice. Verified against the real corpus this
# inflated the printed partial count for every one of the 8 guide-less
# rooms (1-8 double-counted rows each); no duplicate gap row existed yet,
# but len(gap) is the sort key room_guide_candidates.py uses to rank the
# next room to ship, so a future duplicate gap row would silently pick
# the wrong room.
_room = "Test Room"
_us_only = {"query": "a organize test only in us", "best_page": "/test-room-deck.html", "status": "partial"}
_dup_us = {"query": "organize test shared row", "best_page": "/test-room-deck.html", "status": "gap"}
_dup_gl = {"query": "organize test shared row", "best_page": "/test-room-deck.html", "status": "gap"}
_result = rgc.score_room([_us_only, _dup_us], [_dup_gl], _room)
check("a query tracked in both tiers is not double-counted as two gap rows",
      len(_result["gap"]) == 1)
check("the deduped on-topic total counts the shared row once, not twice",
      _result["on_topic_rows"] == 2)

# Found 2026-11-03: Entryway ships a second deck URL shape,
# /deck/entryway-print-and-play.html, that room_rows() did not match,
# undercounting its real coverage (80 real rows missed, 30 on-topic, 0 gap).
_pap_row = {"query": "organize entryway closet", "best_page": "/deck/test-room-print-and-play.html", "status": "covered"}
check("room_rows matches a room's print-and-play deck URL, not just {room}-deck.html",
      len(rgc.room_rows([_pap_row], _room)) == 1)

# Found 2026-11-05 mining Mudroom: a room-level also-called synonym
# (ops/build_zone_pages.py's also_called_html) renders onto the bare room
# page, /rooms/<slug>.html, and room_rows() did not match that path either,
# so a query that newly routed there after the fix vanished from the room's
# count instead of being credited as covered.
_room_page_row = {"query": "organize test room lockers", "best_page": "/rooms/test-room.html", "status": "covered"}
check("room_rows matches the bare room page itself, not just deck/zone/print-and-play",
      len(rgc.room_rows([_room_page_row], _room)) == 1)

# Found 2026-11-03 (Garage pass): "car organizer"/"car trunk"/retailer
# queries route to the Automotive Care Zone on word overlap with
# "organize"/"car" alone but ask about a product for inside the vehicle,
# not the zone's own garage shelf (content.json's purpose names fluids,
# cables and a cleaning kit, nothing about the car's own interior).
_car_organizer = {"query": "amazon shopping car organizer", "best_page": "/test-room-deck.html", "status": "gap"}
_result_car = rgc.score_room([_car_organizer], [], _room)
check("an 'off-topic context' row (car organizer product, not garage storage) is excluded",
      _result_car["on_topic_rows"] == 0)
_car_maint = {"query": "organize car maintenance tips", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car2 = rgc.score_room([_car_maint], [], _room)
check("a genuine on-topic car-maintenance row is NOT excluded by that same pattern",
      _result_car2["on_topic_rows"] == 1)

# Found 2026-11-04 (Workshop pass): "craft paint"/"diamond painting" seeded
# from "how to organize paint and chemical storage" drift to a hobbyist
# audience the Finishing and Chemical Zone's own content.json purpose
# (fire-safe storage for wood finish, not craft acrylics) does not cover.
_craft_paint = {"query": "craft paint storage ideas", "best_page": "/test-room-deck.html", "status": "partial"}
_result_craft = rgc.score_room([_craft_paint], [], _room)
check("a 'craft paint' off-topic-context row is excluded",
      _result_craft["on_topic_rows"] == 0)
_chem_storage = {"query": "chemical storage best practices", "best_page": "/test-room-deck.html", "status": "partial"}
_result_chem = rgc.score_room([_chem_storage], [], _room)
check("a genuine on-topic chemical-storage row is NOT excluded by that same pattern",
      _result_chem["on_topic_rows"] == 1)

# Found 2026-11-04 (Pantry/Primary Bedroom/Family Room pass): three more
# seed-drift rows, same shape as "benchmark advance" above.
_gardening_series = {"query": "declutter gardening series lessons", "best_page": "/test-room-deck.html", "status": "gap"}
_result_gs = rgc.score_room([_gardening_series], [], _room)
check("a 'gardening series lessons' off-topic-context row is excluded",
      _result_gs["on_topic_rows"] == 0)
_dental = {"query": "dental organization ideas", "best_page": "/test-room-deck.html", "status": "gap"}
_result_dental = rgc.score_room([_dental], [], _room)
check("a 'dental organization' off-topic-context row is excluded",
      _result_dental["on_topic_rows"] == 0)
_reddit_life = {"query": "how to declutter my life reddit", "best_page": "/test-room-deck.html", "status": "gap"}
_result_reddit = rgc.score_room([_reddit_life], [], _room)
check("a 'declutter my life reddit' off-topic-context row is excluded",
      _result_reddit["on_topic_rows"] == 0)
_den = {"query": "den storage ideas", "best_page": "/test-room-deck.html", "status": "partial"}
_result_den = rgc.score_room([_den], [], _room)
check("a genuine on-topic 'den storage' row is NOT excluded by the dental pattern",
      _result_den["on_topic_rows"] == 1)

# Found 2026-11-04 (PM check-in, 01:4x slot): a commercial/B2B-intent
# cluster ("business", "equipment list", "pricing model") word-overlapping
# onto household zones purely on "cleaning", "equipment" or "organize".
_pricing_model = {"query": "organize seasonal pricing model", "best_page": "/test-room-deck.html", "status": "gap"}
_result_pricing = rgc.score_room([_pricing_model], [], _room)
check("a 'pricing model' off-topic-context row is excluded",
      _result_pricing["on_topic_rows"] == 0)
_cleaning_business = {"query": "equipment needed for cleaning business", "best_page": "/test-room-deck.html", "status": "partial"}
_result_cb = rgc.score_room([_cleaning_business], [], _room)
check("a 'cleaning business' off-topic-context row is excluded",
      _result_cb["on_topic_rows"] == 0)
_equipment_list = {"query": "office cleaning equipment list", "best_page": "/test-room-deck.html", "status": "partial"}
_result_el = rgc.score_room([_equipment_list], [], _room)
check("an 'equipment list' off-topic-context row is excluded",
      _result_el["on_topic_rows"] == 0)
_cleaning_supplies = {"query": "best way to organize cleaning supplies", "best_page": "/test-room-deck.html", "status": "partial"}
_result_cs = rgc.score_room([_cleaning_supplies], [], _room)
check("a genuine on-topic 'organize cleaning supplies' row is NOT excluded by the business pattern",
      _result_cs["on_topic_rows"] == 1)


# Found 2026-11-05 (Garage pass, top-ranked room by
# room_guide_underperformance.py): "cricut"/"prepping supplies" collide on
# the Automotive Care Zone's title alone (fluids/cables/rags content has
# nothing to do with a craft cutting machine or doomsday stockpiling);
# "pics/pictures on a wall" collide on the Hand Tool Wall and Cabinets
# zone's title alone (pegboard/tool content has nothing to do with hanging
# home-decor photographs).
_cricut = {"query": "how to organize cricut supplies", "best_page": "/test-room-deck.html", "status": "partial"}
_result_cricut = rgc.score_room([_cricut], [], _room)
check("a 'cricut' off-topic-context row is excluded",
      _result_cricut["on_topic_rows"] == 0)
_prepping = {"query": "how to organize prepping supplies", "best_page": "/test-room-deck.html", "status": "partial"}
_result_prepping = rgc.score_room([_prepping], [], _room)
check("a 'prepping supplies' off-topic-context row is excluded",
      _result_prepping["on_topic_rows"] == 0)
_pics_wall = {"query": "how to organize pics on wall", "best_page": "/test-room-deck.html", "status": "partial"}
_result_pics = rgc.score_room([_pics_wall], [], _room)
check("a 'pics on wall' off-topic-context row is excluded",
      _result_pics["on_topic_rows"] == 0)
_pictures_wall = {"query": "how to organize pictures on a wall", "best_page": "/test-room-deck.html", "status": "partial"}
_result_pictures = rgc.score_room([_pictures_wall], [], _room)
check("a 'pictures on a wall' off-topic-context row is excluded",
      _result_pictures["on_topic_rows"] == 0)
_wall_tool = {"query": "wall mounted tool organizer", "best_page": "/test-room-deck.html", "status": "partial"}
_result_wall_tool = rgc.score_room([_wall_tool], [], _room)
check("a genuine on-topic 'wall mounted tool organizer' row is NOT excluded by the wall pattern",
      _result_wall_tool["on_topic_rows"] == 1)

# Found 2026-11-05 (same Garage pass, the two remaining `gap`-status rows):
# "soap making supplies" collides on the Automotive Care Zone's title alone
# (a hobby craft, nothing to do with car fluids/cables/rags); "raised
# garden beds" collides via seed drift from "bed and bedding" onto the Lawn
# and Garden Tool Zone (a planting structure, not the zone's hose/tool/
# chemical storage).
_soap = {"query": "how to organize soap making supplies", "best_page": "/test-room-deck.html", "status": "gap"}
_result_soap = rgc.score_room([_soap], [], _room)
check("a 'soap making' off-topic-context row is excluded",
      _result_soap["on_topic_rows"] == 0)
_garden_bed = {"query": "how to organize raised garden beds", "best_page": "/test-room-deck.html", "status": "gap"}
_result_garden_bed = rgc.score_room([_garden_bed], [], _room)
check("a 'raised garden beds' off-topic-context row is excluded",
      _result_garden_bed["on_topic_rows"] == 0)
_garden_tool = {"query": "how to organize garden tools", "best_page": "/test-room-deck.html", "status": "partial"}
_result_garden_tool = rgc.score_room([_garden_tool], [], _room)
check("a genuine on-topic 'organize garden tools' row is NOT excluded by the garden-bed pattern",
      _result_garden_tool["on_topic_rows"] == 1)

# Found 2026-11-07 (Kitchen pass): "how to organise dressing table drawers"
# carries no room signal and lands on Kitchen's own declutter article by
# pure "organise"/"drawers" word overlap; a dressing table is bedroom
# furniture, already answered by Primary/Guest/Kids Bedroom's own dresser
# zones, not Kitchen's to claim.
_dressing = {"query": "how to organise dressing table drawers", "best_page": "/test-room-deck.html", "status": "partial"}
_result_dressing = rgc.score_room([_dressing], [], _room)
check("a 'dressing table' off-topic-context row is excluded",
      _result_dressing["on_topic_rows"] == 0)
_drawers = {"query": "how to organize dresser drawers", "best_page": "/test-room-deck.html", "status": "partial"}
_result_drawers = rgc.score_room([_drawers], [], _room)
check("a genuine on-topic 'organize dresser drawers' row is NOT excluded by the dressing-table pattern",
      _result_drawers["on_topic_rows"] == 1)

# Found 2026-11-09 (Garage pass, the 79-row partial tier): "how to organise
# a care package" collides on the Automotive Care Zone's title alone (a
# gift package for someone, nothing to do with car fluids/cables/rags);
# "how to organize bedazzling kit" is seed drift from "how to organize
# bed", nothing to do with a garage at all.
_care_package = {"query": "how to organise a care package", "best_page": "/test-room-deck.html", "status": "partial"}
_result_care = rgc.score_room([_care_package], [], _room)
check("a 'care package' off-topic-context row is excluded",
      _result_care["on_topic_rows"] == 0)
_bedazzling = {"query": "how to organize bedazzling kit", "best_page": "/test-room-deck.html", "status": "partial"}
_result_bedazzling = rgc.score_room([_bedazzling], [], _room)
check("a 'bedazzling kit' off-topic-context row is excluded",
      _result_bedazzling["on_topic_rows"] == 0)
_car_care = {"query": "how to organize car care products", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car_care = rgc.score_room([_car_care], [], _room)
check("a genuine on-topic 'car care products' row is NOT excluded by the care-package pattern",
      _result_car_care["on_topic_rows"] == 1)

# Found 2026-11-09 (Garage pass, closing the "car boot"/"interior car
# storage" cluster A78 twice left as "a closer call"): "car travel storage
# organizer" and "interior car storage organizers" are retail-product
# searches, the same shape \bcar organizers?\b already excludes, just with
# "storage" breaking the word adjacency those patterns require. "car boot"
# organizing queries and "organize in car interior" are a genuine content
# gap, not product noise, and must stay on-topic/uncovered rather than be
# swept away by the same fix.
_car_travel = {"query": "car travel storage organizer", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car_travel = rgc.score_room([_car_travel], [], _room)
check("a 'car travel storage organizer' off-topic-context row is excluded",
      _result_car_travel["on_topic_rows"] == 0)
_interior_car = {"query": "interior car storage organizers", "best_page": "/test-room-deck.html", "status": "partial"}
_result_interior_car = rgc.score_room([_interior_car], [], _room)
check("an 'interior car storage organizers' off-topic-context row is excluded",
      _result_interior_car["on_topic_rows"] == 0)
_car_boot = {"query": "how to organise a car boot", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car_boot = rgc.score_room([_car_boot], [], _room)
check("a genuine on-topic 'car boot' organizing row is NOT excluded by the car-storage-organizer pattern",
      _result_car_boot["on_topic_rows"] == 1)
_car_interior_organize = {"query": "organize in car interior", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car_interior_organize = rgc.score_room([_car_interior_organize], [], _room)
check("a genuine on-topic 'organize in car interior' row is NOT excluded by the car-storage-organizer pattern",
      _result_car_interior_organize["on_topic_rows"] == 1)

# Found 2026-11-09 (scheduled operator cycle): "declutter woodworking
# fundamentals tips" carries seed "how to declutter a workshop" but lands
# on Primary Bedroom's own declutter article by title-overlap fallback,
# since no "how-to-declutter-a-workshop" article exists. It is a
# woodworking-skills tutorial, not a household organizing query for any
# room.
_woodworking_fundamentals = {"query": "declutter woodworking fundamentals tips",
                              "best_page": "/test-room-deck.html", "status": "gap"}
_result_woodworking_fundamentals = rgc.score_room([_woodworking_fundamentals], [], _room)
check("a 'woodworking fundamentals' off-topic-context row is excluded",
      _result_woodworking_fundamentals["on_topic_rows"] == 0)
_woodworking_workshop = {"query": "how to organize a woodworking workshop",
                          "best_page": "/test-room-deck.html", "status": "partial"}
_result_woodworking_workshop = rgc.score_room([_woodworking_workshop], [], _room)
check("a genuine on-topic 'organize a woodworking workshop' row is NOT excluded by the woodworking-fundamentals pattern",
      _result_woodworking_workshop["on_topic_rows"] == 1)

if failures:
    print("\n%d FAILED: %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("\n%d/%d passed" % (total[0], total[0]))
