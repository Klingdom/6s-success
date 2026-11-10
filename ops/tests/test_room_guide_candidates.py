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

# Found 2026-11-10 (Garage pass): "car organiser diy" (British spelling) was
# leaking through as a false on-topic match, the exact twin of the already-
# excluded z-spelling "car organizer ideas diy", because ON_TOPIC's
# 2026-11-06 "organi[sz]" broadening was never mirrored onto this exclusion.
_car_organiser_gb = {"query": "car organiser diy", "best_page": "/test-room-deck.html", "status": "covered"}
_result_car_organiser_gb = rgc.score_room([_car_organiser_gb], [], _room)
check("the British-spelling 'car organiser diy' off-topic-context row is excluded",
      _result_car_organiser_gb["on_topic_rows"] == 0)
_car_organisation_essentials = {"query": "car organisation essentials", "best_page": "/test-room-deck.html", "status": "partial"}
_result_car_organisation_essentials = rgc.score_room([_car_organisation_essentials], [], _room)
check("'car organisation essentials' (the activity, not the product) is NOT excluded",
      _result_car_organisation_essentials["on_topic_rows"] == 1)

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

# Found 2026-11-10 (scheduled operator cycle, Garage's 74-row partial
# tier): 89 on-topic rows across 16 rooms score partial/gap for exactly one
# reason, naming a retailer, a content platform, or a country/language
# ("pinterest", "ikea", "reddit", "dollar tree", "canada", "australia",
# "tamil"). CLAUDE.md section 5 ("Product types, never brand names") means
# this site will never honestly earn these words in a heading, so they are
# not a content gap a synonym can close.
_pinterest = {"query": "test room organization ideas pinterest", "best_page": "/test-room-deck.html", "status": "partial"}
_result_pinterest = rgc.score_room([_pinterest], [], _room)
check("a 'pinterest' brand-noise row is excluded",
      _result_pinterest["on_topic_rows"] == 0)
_dollar_tree = {"query": "test room organization dollar tree", "best_page": "/test-room-deck.html", "status": "gap"}
_result_dollar_tree = rgc.score_room([_dollar_tree], [], _room)
check("a 'dollar tree' brand-noise row is excluded",
      _result_dollar_tree["on_topic_rows"] == 0)
_canada = {"query": "test room storage organizer canada", "best_page": "/test-room-deck.html", "status": "partial"}
_result_canada = rgc.score_room([_canada], [], _room)
check("a 'canada' geo-noise row is excluded",
      _result_canada["on_topic_rows"] == 0)
_home_office = {"query": "how to organize a home office", "best_page": "/test-room-deck.html", "status": "partial"}
_result_home_office = rgc.score_room([_home_office], [], _room)
check("a genuine 'home office' row is NOT excluded by the 'home depot' two-word phrase",
      _result_home_office["on_topic_rows"] == 1)
_amazon_shopping = {"query": "amazon shopping car organizer", "best_page": "/test-room-deck.html", "status": "partial"}
_result_amazon_shopping = rgc.score_room([_amazon_shopping], [], _room)
check("'amazon shopping car organizer' stays excluded (already caught by the car-organizer pattern too)",
      _result_amazon_shopping["on_topic_rows"] == 0)

# Found 2026-11-10 (scheduled operator cycle, finally executing the
# Garage/Hall Closet zone-level mining four prior cycles had named but
# deferred). Three more word-overlap collisions: a garage-sale-event
# homonym, a kitchen-appliance query reaching the garage article on
# "storage" alone, and a B2B cleaning-services-equipment-list query
# reordering the words the existing \bequipment list\b pattern expects.
_garage_sale = {"query": "how to organize a garage sale without tables", "best_page": "/test-room-deck.html", "status": "partial"}
_result_garage_sale = rgc.score_room([_garage_sale], [], _room)
check("a 'garage sale' off-topic-context row is excluded",
      _result_garage_sale["on_topic_rows"] == 0)
_back_of_stove = {"query": "back of stove storage", "best_page": "/test-room-deck.html", "status": "partial"}
_result_back_of_stove = rgc.score_room([_back_of_stove], [], _room)
check("a 'back of stove' off-topic-context row is excluded",
      _result_back_of_stove["on_topic_rows"] == 0)
_cleaning_services = {"query": "list of equipment for cleaning services", "best_page": "/test-room-deck.html", "status": "partial"}
_result_cleaning_services = rgc.score_room([_cleaning_services], [], _room)
check("a 'cleaning services' equipment-list off-topic-context row is excluded",
      _result_cleaning_services["on_topic_rows"] == 0)
_organize_car_boot = {"query": "how to organise a test room boot", "best_page": "/test-room-deck.html", "status": "partial"}
_result_organize_car_boot = rgc.score_room([_organize_car_boot], [], _room)
check("a genuine on-topic 'organise a car boot' row is NOT excluded by the garage-sale pattern",
      _result_organize_car_boot["on_topic_rows"] == 1)

# Found 2026-11-10 (Mudroom/Patio or Deck pass, both tied top at 28%
# uncovered): 61 on-topic gap/partial rows across at least 10 rooms ask how
# to BUILD a physical structure from raw materials (a railing, a walkway, a
# staircase, mudroom/bench/outdoor storage, a wall tool organizer...)
# rather than how to ORGANIZE one that already exists. This site has no
# carpentry/construction content and cannot honestly close these.
_build_storage = {"query": "how to build mudroom storage", "best_page": "/test-room-deck.html", "status": "partial"}
_result_build_storage = rgc.score_room([_build_storage], [], _room)
check("a 'how to build storage' construction-intent row is excluded",
      _result_build_storage["on_topic_rows"] == 0)
_build_organizer = {"query": "how to build a wall tool organizer", "best_page": "/test-room-deck.html", "status": "partial"}
_result_build_organizer = rgc.score_room([_build_organizer], [], _room)
check("a 'how to build a ... organizer' construction-intent row is excluded",
      _result_build_organizer["on_topic_rows"] == 0)
_building_storage_box = {"query": "building an outdoor storage box", "best_page": "/test-room-deck.html", "status": "partial"}
_result_building_storage_box = rgc.score_room([_building_storage_box], [], _room)
check("a 'building an outdoor storage box' construction-intent row is excluded",
      _result_building_storage_box["on_topic_rows"] == 0)
_organize_storage_genuine = {"query": "how to organize mudroom storage", "best_page": "/test-room-deck.html", "status": "partial"}
_result_organize_storage_genuine = rgc.score_room([_organize_storage_genuine], [], _room)
check("a genuine 'how to organize ... storage' row is NOT excluded by the build-construction pattern",
      _result_organize_storage_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, this operator cycle (Workshop pass): "workshop" collides
# with the professional seminar/class/meeting sense (a dance workshop, a
# training workshop, a writing workshop, "organize meditation workshop",
# "organize negotiation workshop", "organize logistics for a workshop", "how
# to organize a workshop presentation", "how to organize a successful
# workshop"), none of which concern a home garage workshop. Two more
# collisions in the same room's tier: "how to organize power tools in truck"
# (vehicle-interior storage, the same mismatched-physical-space shape the
# car-organizer branch already excludes for Garage) and "how to store
# paintings in storage" (fine-art paintings, not the Finishing and Chemical
# Zone's own paint cans). "woodworking workshop" was checked and left alone:
# it is genuinely ambiguous (a home workshop used for woodworking is common
# usage too), so excluding it would risk suppressing a real match on weak
# evidence (CLAUDE.md 5d).
_dance_workshop = {"query": "how to organize a dance workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_dance_workshop = rgc.score_room([_dance_workshop], [], _room)
check("a 'dance workshop' off-topic-context row is excluded",
      _result_dance_workshop["on_topic_rows"] == 0)
_training_workshop = {"query": "how to organize a training workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_training_workshop = rgc.score_room([_training_workshop], [], _room)
check("a 'training workshop' off-topic-context row is excluded",
      _result_training_workshop["on_topic_rows"] == 0)
_writing_workshop = {"query": "how to organize a writing workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_writing_workshop = rgc.score_room([_writing_workshop], [], _room)
check("a 'writing workshop' off-topic-context row is excluded",
      _result_writing_workshop["on_topic_rows"] == 0)
_successful_workshop = {"query": "how to organize a successful workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_successful_workshop = rgc.score_room([_successful_workshop], [], _room)
check("a 'successful workshop' off-topic-context row is excluded",
      _result_successful_workshop["on_topic_rows"] == 0)
_workshop_presentation = {"query": "how to organize a workshop presentation", "best_page": "/test-room-deck.html", "status": "partial"}
_result_workshop_presentation = rgc.score_room([_workshop_presentation], [], _room)
check("a 'workshop presentation' off-topic-context row is excluded",
      _result_workshop_presentation["on_topic_rows"] == 0)
_meditation_workshop = {"query": "organize meditation workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_meditation_workshop = rgc.score_room([_meditation_workshop], [], _room)
check("an 'organize meditation workshop' off-topic-context row is excluded",
      _result_meditation_workshop["on_topic_rows"] == 0)
_negotiation_workshop = {"query": "organize negotiation workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_negotiation_workshop = rgc.score_room([_negotiation_workshop], [], _room)
check("an 'organize negotiation workshop' off-topic-context row is excluded",
      _result_negotiation_workshop["on_topic_rows"] == 0)
_logistics_workshop = {"query": "organize logistics for a workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_logistics_workshop = rgc.score_room([_logistics_workshop], [], _room)
check("an 'organize logistics for a workshop' off-topic-context row is excluded",
      _result_logistics_workshop["on_topic_rows"] == 0)
_truck_tools = {"query": "how to organize power tools in truck", "best_page": "/test-room-deck.html", "status": "partial"}
_result_truck_tools = rgc.score_room([_truck_tools], [], _room)
check("a 'power tools in truck' vehicle-storage off-topic-context row is excluded",
      _result_truck_tools["on_topic_rows"] == 0)
_paintings_storage = {"query": "how to store paintings in storage", "best_page": "/test-room-deck.html", "status": "partial"}
_result_paintings_storage = rgc.score_room([_paintings_storage], [], _room)
check("a 'store paintings in storage' fine-art off-topic-context row is excluded",
      _result_paintings_storage["on_topic_rows"] == 0)
_home_workshop_genuine = {"query": "how to organize a home workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_home_workshop_genuine = rgc.score_room([_home_workshop_genuine], [], _room)
check("a genuine 'home workshop' row is NOT excluded by the workshop-event pattern",
      _result_home_workshop_genuine["on_topic_rows"] == 1)
_woodworking_workshop_left_alone = {"query": "how to organize a woodworking workshop", "best_page": "/test-room-deck.html", "status": "partial"}
_result_woodworking_workshop_left_alone = rgc.score_room([_woodworking_workshop_left_alone], [], _room)
check("the ambiguous 'woodworking workshop' row is deliberately left on-topic, not excluded",
      _result_woodworking_workshop_left_alone["on_topic_rows"] == 1)

# Found 2026-11-10 (scheduled operator cycle, mining Garage's remaining
# 54-row partial tier). "sports card storage ideas" collides with the
# Sports and Recreation Zone's title on "sports" alone; that zone's real
# content is bikes, bins, cleats and helmets for sports a household plays,
# nothing about collectible trading cards. "organize tool adobe" collides
# with the Hand Tool Wall and Cabinets zone on "tool" alone; "adobe" names
# design software or a construction material, neither addressed by a
# pegboard-and-hand-tool zone. "toolganize power tool organiser" is a
# single Bing-sourced scrape/autosuggest artifact ("toolganize" is not an
# English word), not a real query a page could honestly answer.
_sports_card = {"query": "sports card storage ideas", "best_page": "/test-room-deck.html", "status": "partial"}
_result_sports_card = rgc.score_room([_sports_card], [], _room)
check("a 'sports card' off-topic-context row is excluded",
      _result_sports_card["on_topic_rows"] == 0)
_organize_tool_adobe = {"query": "organize tool adobe", "best_page": "/test-room-deck.html", "status": "partial"}
_result_organize_tool_adobe = rgc.score_room([_organize_tool_adobe], [], _room)
check("an 'organize tool adobe' off-topic-context row is excluded",
      _result_organize_tool_adobe["on_topic_rows"] == 0)
_toolganize = {"query": "toolganize power tool organiser", "best_page": "/test-room-deck.html", "status": "partial"}
_result_toolganize = rgc.score_room([_toolganize], [], _room)
check("a 'toolganize' scrape-artifact row is excluded",
      _result_toolganize["on_topic_rows"] == 0)
_card_games_genuine = {"query": "card games organizer storage", "best_page": "/test-room-deck.html", "status": "partial"}
_result_card_games_genuine = rgc.score_room([_card_games_genuine], [], _room)
check("a genuine 'card games organizer storage' row is NOT excluded by the sports-card pattern",
      _result_card_games_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, mining Kids Bedroom's single gap-tier row. "building
# beds for kids organization" asks how to construct a bed frame, not how to
# organize a bedroom. "how to organize a clothing drive" / "organizing a
# clothing drive" ask how to run a charity clothing collection event, not
# how to arrange clothes in storage.
_building_beds = {"query": "building beds for kids organization", "best_page": "/test-room-deck.html", "status": "gap"}
_result_building_beds = rgc.score_room([_building_beds], [], _room)
check("a 'building beds' off-topic-context row is excluded",
      _result_building_beds["on_topic_rows"] == 0)
_clothing_drive_1 = {"query": "how to organize a clothing drive", "best_page": "/test-room-deck.html", "status": "partial"}
_result_clothing_drive_1 = rgc.score_room([_clothing_drive_1], [], _room)
check("a 'how to organize a clothing drive' off-topic-context row is excluded",
      _result_clothing_drive_1["on_topic_rows"] == 0)
_clothing_drive_2 = {"query": "organizing a clothing drive", "best_page": "/test-room-deck.html", "status": "partial"}
_result_clothing_drive_2 = rgc.score_room([_clothing_drive_2], [], _room)
check("an 'organizing a clothing drive' off-topic-context row is excluded",
      _result_clothing_drive_2["on_topic_rows"] == 0)
_clothing_genuine = {"query": "how to organize clothing", "best_page": "/test-room-deck.html", "status": "partial"}
_result_clothing_genuine = rgc.score_room([_clothing_genuine], [], _room)
check("a genuine 'how to organize clothing' row is NOT excluded by the clothing-drive pattern",
      _result_clothing_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, mining Living Room's 12-row partial tier. "how to
# organize/organise a seating chart" is the event-planning sense (assigning
# guests to seats), not arranging the room's own furniture. "how to organize
# billy bookcase" is IKEA's own product-line name, a brand-name query this
# site cannot honestly chase (CLAUDE.md section 5).
_seating_chart_1 = {"query": "how to organize a seating chart", "best_page": "/test-room-deck.html", "status": "partial"}
_result_seating_chart_1 = rgc.score_room([_seating_chart_1], [], _room)
check("a 'how to organize a seating chart' off-topic-context row is excluded",
      _result_seating_chart_1["on_topic_rows"] == 0)
_seating_chart_2 = {"query": "how to organise a seating chart", "best_page": "/test-room-deck.html", "status": "partial"}
_result_seating_chart_2 = rgc.score_room([_seating_chart_2], [], _room)
check("a 'how to organise a seating chart' off-topic-context row is excluded",
      _result_seating_chart_2["on_topic_rows"] == 0)
_billy_bookcase = {"query": "how to organize billy bookcase", "best_page": "/test-room-deck.html", "status": "partial"}
_result_billy_bookcase = rgc.score_room([_billy_bookcase], [], _room)
check("a 'how to organize billy bookcase' off-topic-context row is excluded",
      _result_billy_bookcase["on_topic_rows"] == 0)
_bookcase_genuine = {"query": "how to organize a bookcase", "best_page": "/test-room-deck.html", "status": "covered"}
_result_bookcase_genuine = rgc.score_room([_bookcase_genuine], [], _room)
check("a genuine 'how to organize a bookcase' row is NOT excluded by the billy-bookcase pattern",
      _result_bookcase_genuine["on_topic_rows"] == 1)
_seating_genuine = {"query": "organize outdoor seating", "best_page": "/test-room-deck.html", "status": "covered"}
_result_seating_genuine = rgc.score_room([_seating_genuine], [], _room)
check("a genuine 'organize outdoor seating' row is NOT excluded by the seating-chart pattern",
      _result_seating_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, mining Family Room's 21-row partial tier. "how to
# organize a games night" is the event-planning sense (deciding who to
# invite, what to play), not storing the games themselves; the Board Game
# and Puzzle Zone's own content.json purpose is about keeping game
# components complete in storage, never about planning the event.
_games_night = {"query": "how to organize a games night", "best_page": "/test-room-deck.html", "status": "partial"}
_result_games_night = rgc.score_room([_games_night], [], _room)
check("a 'how to organize a games night' off-topic-context row is excluded",
      _result_games_night["on_topic_rows"] == 0)
_game_night_genuine_title = {"query": "how to organize stardew valley board game", "best_page": "/test-room-deck.html", "status": "partial"}
_result_game_night_genuine_title = rgc.score_room([_game_night_genuine_title], [], _room)
check("a genuine specific-board-game-title row is NOT excluded by the games-night pattern",
      _result_game_night_genuine_title["on_topic_rows"] == 1)

# Found 2026-11-10, mining Guest Bathroom's 20-row partial tier.
# "linen cupboard organisation bunnings" names Bunnings, an Australian
# hardware retailer, the same no-brand-names shape the pinterest/ikea/
# target/etc branch above already excludes, just one brand that list
# missed. "how to organise middle class room" and "how to organize your
# room middle class" are a socioeconomic descriptor with no connection to
# any room, zone or activity this site addresses.
_bunnings = {"query": "linen cupboard organisation bunnings", "best_page": "/test-room-deck.html", "status": "partial"}
_result_bunnings = rgc.score_room([_bunnings], [], _room)
check("a 'bunnings' off-topic-context row is excluded",
      _result_bunnings["on_topic_rows"] == 0)
_linen_genuine = {"query": "linen cupboard organisation ideas", "best_page": "/test-room-deck.html", "status": "partial"}
_result_linen_genuine = rgc.score_room([_linen_genuine], [], _room)
check("a genuine 'linen cupboard organisation ideas' row is NOT excluded by the bunnings pattern",
      _result_linen_genuine["on_topic_rows"] == 1)
_middle_class_1 = {"query": "how to organise middle class room", "best_page": "/test-room-deck.html", "status": "partial"}
_result_middle_class_1 = rgc.score_room([_middle_class_1], [], _room)
check("a 'how to organise middle class room' off-topic-context row is excluded",
      _result_middle_class_1["on_topic_rows"] == 0)
_middle_class_2 = {"query": "how to organize your room middle class", "best_page": "/test-room-deck.html", "status": "partial"}
_result_middle_class_2 = rgc.score_room([_middle_class_2], [], _room)
check("a 'how to organize your room middle class' off-topic-context row is excluded",
      _result_middle_class_2["on_topic_rows"] == 0)
_room_genuine = {"query": "how to organize your room", "best_page": "/test-room-deck.html", "status": "covered"}
_result_room_genuine = rgc.score_room([_room_genuine], [], _room)
check("a genuine 'how to organize your room' row is NOT excluded by the middle-class pattern",
      _result_room_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, PM check-in mining Patio or Deck's 6-row partial tier.
# "how to organize anking step deck" lands on the patio-or-deck article
# purely on "step"/"deck"; AnKing is the name of a widely used Anki
# flashcard deck for medical exam study (the "AnKing Step deck"), nothing
# to do with outdoor furniture. "outdoor storage rental tips" lands on the
# Outdoor Storage Zone purely on "outdoor"/"storage"; it asks about renting
# space at a self-storage facility, not organizing the household's own
# patio storage, the same different-domain shape "adobe" and "toolganize"
# already exclude elsewhere.
_anking = {"query": "how to organize anking step deck", "best_page": "/test-room-deck.html", "status": "partial"}
_result_anking = rgc.score_room([_anking], [], _room)
check("a 'how to organize anking step deck' off-topic-context row is excluded",
      _result_anking["on_topic_rows"] == 0)
_deck_genuine = {"query": "how to organize a deck", "best_page": "/test-room-deck.html", "status": "covered"}
_result_deck_genuine = rgc.score_room([_deck_genuine], [], _room)
check("a genuine 'how to organize a deck' row is NOT excluded by the anking pattern",
      _result_deck_genuine["on_topic_rows"] == 1)
_storage_rental = {"query": "outdoor storage rental tips", "best_page": "/test-room-deck.html", "status": "partial"}
_result_storage_rental = rgc.score_room([_storage_rental], [], _room)
check("an 'outdoor storage rental tips' off-topic-context row is excluded",
      _result_storage_rental["on_topic_rows"] == 0)
_storage_genuine = {"query": "outdoor storage ideas cheap", "best_page": "/test-room-deck.html", "status": "partial"}
_result_storage_genuine = rgc.score_room([_storage_genuine], [], _room)
check("a genuine 'outdoor storage ideas cheap' row is NOT excluded by the rental pattern",
      _result_storage_genuine["on_topic_rows"] == 1)

# Found 2026-11-10, PM check-in mining Family Room's 20-row partial tier.
# "how to organize/organise a craft fair" and "how to organise a craft
# market" land on the Craft and Activity Zone purely on "craft"; a craft
# fair or market is the event-planning sense (running a sale event), not
# storing craft supplies at home.
_craft_fair_us = {"query": "how to organize a craft fair", "best_page": "/test-room-deck.html", "status": "partial"}
_result_craft_fair_us = rgc.score_room([_craft_fair_us], [], _room)
check("a 'how to organize a craft fair' off-topic-context row is excluded",
      _result_craft_fair_us["on_topic_rows"] == 0)
_craft_fair_gl = {"query": "how to organise a craft fair", "best_page": "/test-room-deck.html", "status": "partial"}
_result_craft_fair_gl = rgc.score_room([_craft_fair_gl], [], _room)
check("a 'how to organise a craft fair' off-topic-context row is excluded",
      _result_craft_fair_gl["on_topic_rows"] == 0)
_craft_market = {"query": "how to organise a craft market", "best_page": "/test-room-deck.html", "status": "partial"}
_result_craft_market = rgc.score_room([_craft_market], [], _room)
check("a 'how to organise a craft market' off-topic-context row is excluded",
      _result_craft_market["on_topic_rows"] == 0)
_craft_genuine = {"query": "how to organize craft room", "best_page": "/test-room-deck.html", "status": "partial"}
_result_craft_genuine = rgc.score_room([_craft_genuine], [], _room)
check("a genuine 'how to organize craft room' row is NOT excluded by the craft-fair pattern",
      _result_craft_genuine["on_topic_rows"] == 1)

# Same Family Room pass: "how to organize game files" and "how to organize
# game systems" land on the Board Game and Puzzle Zone purely on
# "organize"/"game"; "game files" and "game systems" are the video-game-
# console sense (a save file, a PS5 or Xbox console), the same digital-
# library confusion DIGITAL already excludes for "hard drive"/"pc"/
# "steam", not a question about board games.
_game_files = {"query": "how to organize game files", "best_page": "/test-room-deck.html", "status": "partial"}
_result_game_files = rgc.score_room([_game_files], [], _room)
check("a 'how to organize game files' digital-context row is excluded",
      _result_game_files["on_topic_rows"] == 0)
_game_systems = {"query": "how to organize game systems", "best_page": "/test-room-deck.html", "status": "partial"}
_result_game_systems = rgc.score_room([_game_systems], [], _room)
check("a 'how to organize game systems' digital-context row is excluded",
      _result_game_systems["on_topic_rows"] == 0)
_video_game_genuine = {"query": "video game storage ideas", "best_page": "/test-room-deck.html", "status": "partial"}
_result_video_game_genuine = rgc.score_room([_video_game_genuine], [], _room)
check("a genuine 'video game storage ideas' row is NOT excluded by the game-files/systems pattern",
      _result_video_game_genuine["on_topic_rows"] == 1)
_game_library_genuine = {"query": "how to organize game library", "best_page": "/test-room-deck.html", "status": "partial"}
_result_game_library_genuine = rgc.score_room([_game_library_genuine], [], _room)
check("a genuine 'how to organize game library' row is NOT excluded by the game-files/systems pattern",
      _result_game_library_genuine["on_topic_rows"] == 1)

if failures:
    print("\n%d FAILED: %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("\n%d/%d passed" % (total[0], total[0]))
