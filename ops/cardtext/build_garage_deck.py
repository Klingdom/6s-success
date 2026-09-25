#!/usr/bin/env python3
"""
Build the Garage deck: 80 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
`content/manual/source/content.json`, the same corpus the 114 zone pages
already read. `ops/cardtext/build_kitchen_deck.py`,
`ops/cardtext/build_entryway_deck.py`, `ops/cardtext/build_laundry_room_deck.py`,
`ops/cardtext/build_home_office_deck.py` and
`ops/cardtext/build_primary_bathroom_deck.py` proved the pattern for the
first four rooms; this is the fifth and last. Purpose, done_looks_like, the
standard, the trigger, the first-15 action and its victory condition are
quoted from the Manual, not rewritten, and `gate()` at the bottom asserts
they are still character-for-character identical.

Garage's own diagnosis layer does not split evenly at three frictions per
zone the way every prior room's did: three of the seven zones (Primary
Workbench, Hand Tool Wall and Cabinets, Power Tool and Battery Zone) carry
three, and the other four (Automotive Care, Sports and Recreation, Lawn and
Garden Tool, Bulk and Overhead Storage) carry four, for 25 frictions in
total, not 21. That count is read directly off the real corpus at build
time, never assumed, and `gate()` checks each zone's own friction count
against its own diagnosis data rather than a single hardcoded number.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the three
whole-room action cards (the Manual gives one 15-minute reset per zone in
`first_15`; the 30-minute rebuild per zone and the three whole-room actions
are authored here), the event cards, the micro quests, and the room card.
The root causes are not reauthored: they are the same frozen vocabulary in
`ops/root_causes.py` that every prior room deck already uses, so a
household owning more than one deck keeps one diagnosis pile rather than
several (DECK-GAME-DESIGN.md 4.3). This room's own diagnosis data reaches
sixteen of the shared vocabulary's seventeen causes (every one except
KC-011, poor replenishment, which no Garage friction branches to), confirmed
against content/manual/source/content.json before this file was written,
not assumed from any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Garage deck to disclose against: no free Garage product exists on the site
yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_garage_deck.py
Out:  ops/cardtext/garage-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "garage-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Garage"

# This room ships as a free typeset page, the same stage every prior room
# deck shipped at before any print-on-demand decision existed, so the
# budget here is the honest count of what this room's own corpus,
# diagnosis layer and a proportionate amount of new authorship produce:
# seven real zones, twenty-five real frictions (not the usual twenty-one,
# because four of the seven zones carry four diagnosed frictions rather
# than three), sixteen reachable root causes, two actions per zone plus
# three whole-room ones.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 7, "FRICTION CARD": 25,
          "ROOT CAUSE CARD": 16, "ACTION CARD": 17, "STANDARD CARD": 7,
          "EVENT CARD": 7}
TOTAL = sum(BUDGET.values())

# Same palette family as every prior room deck so a mixed pile of cards
# from any room still reads as one product line.
TYPE_COLOUR = {
    "ROOM CARD": "#2B2622", "ZONE CARD": "#2F5233",
    "FRICTION CARD": "#BC4B2A", "ROOT CAUSE CARD": "#6E5B8B",
    "ACTION CARD": "#3C5A6B", "STANDARD CARD": "#4E7A57",
    "EVENT CARD": "#8C5A2B",
}

# Root causes this room's real diagnosis branches actually reach, derived
# below from the Manual and asserted (in gate()) to be exactly this set:
# not a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written: every
# one of the seven zones' diagnosis branches (25 frictions, 75 branches)
# was read and its "cause" field copied here verbatim.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-012", "RC-013",
             "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior room generator uses: every
# numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Primary Workbench": {
  "id": "GAZ-001", "order": 1, "difficulty": 3,
  "tagline": "BARE TOP. ONE TRAY. SWEPT CONCRETE BENEATH.",
  "callouts": [
   "A bare bench top holding only the vise and the task light",
   "One tray holding the current job, nothing else",
   "Clamps racked on the rail within reach",
   "Swept concrete visible under the bench",
   "No cord crossing the strip of floor you stand on",
   "No chisel or blade resting edge-up on the top",
  ],
  "art": ("a garage workbench with a bare top holding only a vise and a "
          "task light, one tray holding a single current job, clamps "
          "racked on a rail within reach, swept concrete visible "
          "underneath, no cord crossing the floor, and no blade resting "
          "edge-up on the top"),
 },
 "Hand Tool Wall and Cabinets": {
  "id": "GAZ-002", "order": 2, "difficulty": 3,
  "tagline": "EVERY TOOL ON ITS OUTLINE. NOTHING BLANK.",
  "callouts": [
   "Every hand tool hanging on its own drawn outline",
   "No blank silhouette anywhere on the board",
   "One hammer at chest height nearest the door",
   "One adjustable wrench at chest height nearest the door",
   "Saw teeth sheathed",
   "The cabinet door latched",
  ],
  "art": ("a garage pegboard wall where every hand tool hangs over its "
          "own drawn outline with no blank silhouette, one hammer and "
          "one adjustable wrench at chest height nearest the door, a "
          "handsaw with its teeth sheathed, and a low cabinet door shown "
          "latched"),
 },
 "Power Tool and Battery Zone": {
  "id": "GAZ-003", "order": 3, "difficulty": 3,
  "tagline": "ONE SHELF PER SYSTEM. NO PACK LEFT CHARGING.",
  "callouts": [
   "One shelf per battery system",
   "A charger mounted at the front edge of each shelf",
   "No battery pack sitting on any charger",
   "Every drill and saw in its case or on a labelled hook",
   "Every blade guard down",
   "Bits, blades and sanding discs in the shallow drawer underneath",
  ],
  "art": ("a garage shelf system with one shelf per battery platform, a "
          "charger mounted at the front edge of each shelf with no pack "
          "sitting on it, drills and saws stored in their cases or on "
          "labelled hooks with blade guards down, and a shallow drawer "
          "underneath holding bits, blades and sanding discs"),
 },
 "Automotive Care Zone": {
  "id": "GAZ-004", "order": 4, "difficulty": 2,
  "tagline": "UPRIGHT. DATED. ONLY THIS DRIVEWAY'S CARS.",
  "callouts": [
   "Every fluid bottle standing upright on a clean drip tray",
   "Each opened bottle dated on its shoulder",
   "Jumper cables and tyre gauge together in one bag by the door",
   "Oily rags sealed inside a closed metal can",
   "Not a single bottle for a car nobody here drives",
   "A dry, ring-free drip tray under every bottle",
  ],
  "art": ("a garage automotive shelf holding fluid bottles standing "
          "upright on a clean drip tray, jumper cables and a tyre gauge "
          "together in one bag by the door, oily rags sealed inside a "
          "closed metal can, and no bottle left over for a car that no "
          "longer parks here"),
 },
 "Sports and Recreation Zone": {
  "id": "GAZ-005", "order": 5, "difficulty": 2,
  "tagline": "BIKES UP. BARE FLOOR. HELMETS THAT STILL FIT.",
  "callouts": [
   "Bikes hanging on wall hooks",
   "Bare floor visible beneath the hanging bikes",
   "One labelled bin per activity",
   "This season's kit sitting at the front of the shelf",
   "Every helmet belonging to a head that still wears it",
   "Off-season kit pushed to the back of the shelf",
  ],
  "art": ("a garage sports corner with bikes hanging on wall hooks over "
          "bare floor, one labelled bin for each activity, this season's "
          "kit at the front of the shelf and last season's pushed behind "
          "it, and a row of helmets each sized to a head that still "
          "wears it"),
 },
 "Lawn and Garden Tool Zone": {
  "id": "GAZ-006", "order": 6, "difficulty": 3,
  "tagline": "HEAD-UP ON THE RAIL. CHEMICALS LATCHED HIGH.",
  "callouts": [
   "Every long-handled tool hanging head-up on the rail",
   "No tool leaning in a corner",
   "The hose coiled on its reel",
   "The reel positioned beside the door the hose goes out of",
   "Garden chemicals in their original labelled containers",
   "The chemical shelf latched above head height",
  ],
  "art": ("a garage garden corner with every long-handled tool hanging "
          "head-up on a wall rail, nothing leaning in a corner, a hose "
          "coiled on its reel beside the door it goes out of, and garden "
          "chemicals standing in their original labelled containers "
          "behind a latched shelf above head height"),
 },
 "Bulk and Overhead Storage": {
  "id": "GAZ-007", "order": 7, "difficulty": 3,
  "tagline": "LABELLED. DATED. HEAVIEST BINS DOWN LOW.",
  "callouts": [
   "Every overhead bin labelled large enough to read from the slab",
   "A last-opened month and year marked on the end of each bin",
   "The heaviest bins on the lowest rack",
   "Lighter bulky items on the highest rack",
   "Nothing overhanging the parking bay",
   "A small map taped beside the light switch",
  ],
  "art": ("a garage overhead storage rack with large labels on every bin "
          "readable from the slab below, the heaviest bins on the lowest "
          "rack and light bulky items highest, nothing overhanging the "
          "parking bay, and a small map taped beside the light switch"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine already
# shipped on the 114 zone pages. Three or four per zone, matching that data
# exactly (see the module docstring for why this room is not a flat three).
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Primary Workbench", "GAF-001", "CLEAR AT NOON, BURIED BY FIVE",
  "a garage workbench half buried under bottles, boxes and unfinished "
  "tools by the end of the day, only a corner of bare wood still "
  "showing"),
 ("Primary Workbench", "GAF-002", "THE FIVE-MINUTE HUNT BEFORE EVERY JOB",
  "a hand searching across a cluttered garage workbench and a nearby "
  "shelf for one tool while a half-started job waits untouched"),
 ("Primary Workbench", "GAF-003", "TRIPPING OVER THE JOB ITSELF",
  "a coiled extension cord crossing a garage walkway in front of a "
  "workbench, boxes stacked directly beneath where a broom should reach"),

 ("Hand Tool Wall and Cabinets", "GAF-004", "GONE, AND NOBODY SAW IT LEAVE",
  "a bare patch of pegboard on a garage tool wall with no drawn outline "
  "behind it, tools hanging on either side"),
 ("Hand Tool Wall and Cabinets", "GAF-005",
  "THE THIRD WRENCH IN AS MANY DRAWERS",
  "three identical adjustable wrenches scattered between a garage "
  "pegboard, a cabinet shelf and a loose toolbox"),
 ("Hand Tool Wall and Cabinets", "GAF-006", "A REACH THAT COULD DRAW BLOOD",
  "a hand reaching into a crowded garage cabinet past an unsheathed saw "
  "blade toward a tool at the back"),

 ("Power Tool and Battery Zone", "GAF-007", "DEAD ON ARRIVAL, EVERY TIME",
  "a cordless drill lifted from a garage shelf with its battery "
  "indicator showing empty, a charger sitting unused nearby"),
 ("Power Tool and Battery Zone", "GAF-008", "STILL ON THE CHARGER AT DAWN",
  "a battery pack glowing on a charger overnight on a garage shelf "
  "beside a fuel can and a bin of oily rags"),
 ("Power Tool and Battery Zone", "GAF-009",
  "THE DRAWER THAT NEVER HOLDS AN EDGE",
  "a shallow garage drawer holding a jumble of loose drill bits and saw "
  "blades of mixed sharpness, none guarded"),

 ("Automotive Care Zone", "GAF-010", "FLUID FOR A CAR THAT LEFT YEARS AGO",
  "a shelf of automotive fluid bottles in a garage, one clearly for a "
  "make of car no longer parked on the driveway outside"),
 ("Automotive Care Zone", "GAF-011", "THE PUDDLE NOBODY CAN EXPLAIN",
  "a dark sticky puddle spreading across bare garage concrete beneath a "
  "shelf of automotive fluid bottles with no drip tray under them"),
 ("Automotive Care Zone", "GAF-012", "DEAD BATTERY, NO CABLES IN SIGHT",
  "a car with its bonnet raised on a driveway at dusk while a hand "
  "searches through boxes at the back of a dark garage for jumper "
  "cables"),
 ("Automotive Care Zone", "GAF-013", "ONE SHELF AWAY FROM A BAD NIGHT",
  "a fuel can standing directly beside a bag of garden fertiliser on a "
  "low garage shelf, an unlabelled bottle nearby"),

 ("Sports and Recreation Zone", "GAF-014",
  "THREE THINGS MOVED BEFORE ONE BIKE COMES OUT",
  "a bicycle standing on a cluttered garage floor surrounded by boxes "
  "and bins that have to be shifted before it can roll free"),
 ("Sports and Recreation Zone", "GAF-015",
  "THIS MONTH'S GEAR, BURIED AT THE BACK",
  "a garage shelf where this season's sports kit sits crammed behind "
  "bins of off-season gear stacked in front of it"),
 ("Sports and Recreation Zone", "GAF-016",
  "THE SHELF FOR A SPORT NOBODY PLAYS NOW",
  "a dusty set of skis and a golf bag standing untouched in the corner "
  "of a garage behind newer, obviously used gear"),
 ("Sports and Recreation Zone", "GAF-017", "A HELMET NOBODY CAN VOUCH FOR",
  "a row of bicycle helmets on a garage shelf, one visibly cracked at "
  "the shell, none marked with a date anyone can check"),

 ("Lawn and Garden Tool Zone", "GAF-018", "EVERY FORK LEANING, NONE HANGING",
  "a rake and a garden fork leaning together in the corner of a garage, "
  "an empty wall rail with open hooks a few feet away"),
 ("Lawn and Garden Tool Zone", "GAF-019",
  "THE HOSE THAT FIGHTS BACK EVERY TIME",
  "a garden hose tangled in loose coils on a garage floor near the "
  "door, a thin stream of water leaking from a split near one end"),
 ("Lawn and Garden Tool Zone", "GAF-020", "A BOTTLE NOBODY CAN NAME",
  "an unlabelled spray bottle sitting on a garage shelf among garden "
  "chemicals, its faded original container long gone"),
 ("Lawn and Garden Tool Zone", "GAF-021", "WITHIN REACH OF A CURIOUS HAND",
  "a bag of granular garden feed sitting on an open, unlatched garage "
  "shelf at a small child's standing height"),

 ("Bulk and Overhead Storage", "GAF-022", "THREE BINS DOWN BEFORE THE RIGHT ONE",
  "a person on a ladder in a garage lowering a third overhead bin to "
  "the floor, two already opened and abandoned beside it"),
 ("Bulk and Overhead Storage", "GAF-023", "UNTOUCHED SINCE THE MOVE-IN DAY",
  "a heavily dust-coated overhead storage bin on a garage rack, "
  "visibly undisturbed for years beside newer, cleaner bins"),
 ("Bulk and Overhead Storage", "GAF-024",
  "A TWO-PERSON LIFT FOR A ONE-PERSON JOB",
  "two people straining together to lower one heavy overhead bin from "
  "a high garage rack, a wobbling ladder beneath them"),
 ("Bulk and Overhead Storage", "GAF-025", "HANGING OVER WHERE THE CAR PARKS",
  "an overhead garage rack loaded with bins that extend out past its "
  "own frame, directly above where a car's roof would sit"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, garage-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use, so this deck composes with every other
# room deck rather than forking its own copy (DECK-GAME-DESIGN.md 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a garage shelf crowded with far more of the same tool or "
           "fluid than one household could use before the older ones "
           "fail",
 "KC-002": "a coiled extension cord and a loose tape measure lying on a "
           "garage floor with no hook or drawer assigned to either",
 "KC-003": "a can of fuel stored on a garage workbench shelf instead of "
           "anywhere near the mower it actually feeds",
 "KC-004": "a hand lifting three stacked bins off a garage shelf just to "
           "reach the one tool at the very back",
 "KC-005": "a row of unlabelled garage bins on a rack with no way to "
           "tell what any one of them holds without climbing up and "
           "opening it",
 "KC-006": "a garage shelf mounted out of easy reach, a wobbling step "
           "stool standing on bare concrete beneath it",
 "KC-007": "a single garage tool rail with more long handles than "
           "hooks, one rake leaning loose against the wall beside it",
 "KC-008": "a garage shelf with two completely different storage "
           "systems visible side by side, one divided neatly and the "
           "other loose",
 "KC-009": "a garage workbench with no reminder anywhere nearby, dust "
           "visibly settled across an untouched row of tools",
 "KC-010": "an unguarded saw blade lying loose on an open garage shelf "
           "within a child's reach",
 "KC-012": "two overlapping sets of tools pushed together at one end of "
           "a shared garage workbench, no clear boundary between them",
 "RC-013": "an empty tool hook on a garage wall with nobody visibly "
           "responsible for noticing the tool never came back",
 "RC-014": "a dusty set of skis standing untouched in a garage corner, "
           "kept long after the sport that used them stopped",
 "RC-015": "a half-finished project sitting untouched on a garage "
           "workbench for months, its parts still spread across the "
           "surface",
 "RC-016": "a hand reaching into the deep back corner of a garage shelf "
           "where a spill has sat unreached for a long time",
 "RC-017": "an overloaded garage shelf that has clearly sat unchanged "
           "for years, so ordinary to the eye that it no longer "
           "registers",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded
# in that zone's own Manual passes, the same contract every prior room
# generator's MICRO_QUESTS already meets (DECK-GAME-DESIGN.md section 2).
# Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Primary Workbench": [
  "Lift everything off the bench top and confirm bare wood shows edge "
  "to edge.",
  "Rack every clamp on the rail and confirm none are left on the bench "
  "top.",
  "Vacuum the bench dog holes and confirm no sawdust or filings remain.",
 ],
 "Hand Tool Wall and Cabinets": [
  "Pick one hand tool off the wall and confirm it has its own drawn "
  "outline behind it.",
  "Check the low cabinet door and confirm the latch actually catches.",
  "Confirm the hammer and adjustable wrench nearest the door sit at "
  "chest height.",
 ],
 "Power Tool and Battery Zone": [
  "Check every charger on the shelf and confirm no battery pack is "
  "still sitting on one.",
  "Open the shallow drawer and confirm the bits and blades are sorted, "
  "not loose.",
  "Confirm every blade guard springs back on its own when released.",
 ],
 "Automotive Care Zone": [
  "Lift one fluid bottle and confirm the opened date sits on its "
  "shoulder.",
  "Check the drip tray under the bottles for a fresh ring.",
  "Confirm the jumper cables and tyre gauge sit together in one bag by "
  "the door.",
 ],
 "Sports and Recreation Zone": [
  "Lift a bike off its wall hook and confirm the floor beneath it is "
  "bare.",
  "Check one labelled bin and confirm the name on it matches a person "
  "who still plays that sport.",
  "Try on one helmet and confirm it still fits the head that wears it.",
 ],
 "Lawn and Garden Tool Zone": [
  "Hang one long-handled tool head-up on the rail and confirm nothing "
  "leans in the corner.",
  "Coil the hose onto its reel and confirm it sits beside the door it "
  "goes out of.",
  "Check the chemical shelf latch and confirm it sits above head "
  "height.",
 ],
 "Bulk and Overhead Storage": [
  "Check the last-opened date on one bin and confirm it is less than "
  "two years old.",
  "Confirm the heaviest bins sit on the lowest rack, not the highest.",
  "Read the map beside the light switch and confirm it still names "
  "what is where.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-room actions, the same shape every prior room deck's
# whole-room cards keep: no zone or standard invented for them, only their
# real root causes, this time grounded in the room's own stated hazards
# (fuel, chemicals and lithium packs a few feet apart, heavy overhead
# loads, and the postponed decisions the room's own "trap" tip names)
# rather than a generic sweep.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "GAA-001", "zone": "Primary Workbench",
  "title": "CLEAR THE BENCH TO THE VISE AND THE LIGHT", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the bench top down to the vise and the task light, put "
          "the current job in one tray, rack the clamps, and sweep until "
          "concrete shows underneath.",
  "why": "A bench with no boundary on what belongs there is why the "
         "next job never gets a clear surface to start on, and 'I might "
         "need it later' is not the same test as 'this is today's job.'",
  "inputs": ["a tray for the current job", "a broom",
             "nothing else beyond fifteen minutes"],
  "steps": [
   "Clear the bench top down to the vise and the task light, put the "
   "current job in one tray, rack the clamps on the rail, and sweep "
   "until you can see concrete under the bench.",
   "Wipe the vise screw and give it a drop of oil before you close up.",
   "Check the bench outlet and task light cord for nicks while you're "
   "down there."],
  "causes": ["KC-009", "KC-002"],
  "victory": "A bare bench, one tray holding one job, and swept concrete "
             "visible underneath.",
  "next": "GAS-001",
  "art": "a garage workbench with a bare top holding only a vise and a "
         "task light, one tray holding the current job, clamps racked "
         "on the rail, and swept concrete visible beneath it"},

 {"id": "GAA-002", "zone": "Primary Workbench",
  "title": "GIVE EVERY BENCH TOOL ITS OWN CORNER", "minutes": 30,
  "players": "1", "six_s": "Straighten",
  "goal": "Settle where the vise, the current-job tray and the clamp "
          "rail each live permanently, and move anything that isn't a "
          "bench tool off the top for good.",
  "why": "The largest flat surface in the house collects everything "
         "with nowhere else to go, and a tool with no fixed corner on "
         "the bench is a tool that drifts back into the middle of it by "
         "next week.",
  "inputs": ["a marker or tape for corners",
             "a box for anything relocated"],
  "steps": [
   "Mark or tape off the vise's own corner with a full arm's length of "
   "open top in front of it.",
   "Confirm fasteners have a fixed drawer directly beneath where "
   "they're used, not a jar lid on the top.",
   "Carry anything that isn't a bench tool, like a parcel or a paint "
   "tin, to the zone it actually belongs to.",
   "Agree who ends each session with the sweep, tied to unplugging the "
   "bench outlet."],
  "causes": ["KC-008", "KC-003", "KC-012"],
  "victory": "The vise, the tray and the clamp rail each have a fixed "
             "corner, and nothing that isn't a bench tool is resting on "
             "the top.",
  "next": "GAA-001",
  "art": "a garage workbench with a vise clearly settled in its own "
         "marked corner, a clamp rail fixed to one wall, and a parcel "
         "and a paint tin being carried away through the door"},

 {"id": "GAA-003", "zone": "Hand Tool Wall and Cabinets",
  "title": "OUTLINE EVERY TOOL AND SHEATH THE EDGES", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Draw an outline behind every hand tool, move the two you "
          "reach for most to chest height by the door, and sheath "
          "everything sharp.",
  "why": "A blank outline tells you a tool is missing before you go "
         "looking for it, and an unsheathed blade at hand height is one "
         "careless reach away from a cut.",
  "inputs": ["a marker or paint pen",
             "sheaths or blade guards for saws and chisels"],
  "steps": [
   "Draw an outline behind every hand tool that hangs, move one hammer "
   "and one adjustable wrench to chest height nearest the door, sheath "
   "every saw and chisel, and latch the cabinet.",
   "Seat every pegboard hook firmly so nothing heavy sits on a loose "
   "one.",
   "Fit a latch on the low cabinet if children ever come into the "
   "garage."],
  "causes": ["KC-005", "KC-010"],
  "victory": "Every tool on its own outline with no blank silhouettes, "
             "the two you reach for most at chest height by the door, "
             "and nothing sharp left unsheathed.",
  "next": "GAS-002",
  "art": "a garage pegboard with every hand tool hanging over its own "
         "drawn outline, a hammer and adjustable wrench at chest height "
         "by the door, a handsaw sheathed, and a low cabinet door "
         "latched shut"},

 {"id": "GAA-004", "zone": "Hand Tool Wall and Cabinets",
  "title": "SETTLE THE DUPLICATE HAMMERS AND WRENCHES", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Work through every duplicate hand tool on the wall and in "
          "the cabinet, and keep only the one your hand actually "
          "reaches for plus one deliberate spare.",
  "why": "Owning three claw hammers because each one still works is "
         "not the same as needing three, and every duplicate is taking "
         "the hook that would make the one you love findable from the "
         "door.",
  "inputs": ["a bag for tools leaving the house",
             "a box for the one deliberate spare"],
  "steps": [
   "Pull every duplicate hammer, wrench and driver into one pile on "
   "the bench.",
   "Test which one your hand actually reaches for, and keep that one "
   "plus exactly one deliberate spare parked elsewhere in the house.",
   "Give every remaining duplicate to a friend, a tool library or the "
   "metal skip today.",
   "Confirm the tools left on the wall are spread by how often your "
   "hand reaches, not grouped by family."],
  "causes": ["KC-002", "KC-004"],
  "victory": "Only one of each hand tool hangs on the wall, plus one "
             "named deliberate spare kept somewhere else.",
  "next": "GAA-003",
  "art": "three identical claw hammers laid out on a garage bench, one "
         "moved back to a wall outline and the other two set aside in "
         "a bag heading to the door"},

 {"id": "GAA-005", "zone": "Power Tool and Battery Zone",
  "title": "ONE SHELF PER SYSTEM, EVERY GUARD DOWN", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Give each battery system its own shelf, pull every pack off "
          "its charger, and settle every tool into its case or hook "
          "with the guard down.",
  "why": "A pack left sleeping on a charger is the one habit in this "
         "room whose failure cannot be undone by tidying afterward, and "
         "mixing platforms on one shelf is why the wrong pack keeps "
         "going to the wrong tool.",
  "inputs": ["labelled hooks or bins for each system",
             "nothing else beyond fifteen minutes"],
  "steps": [
   "Give each battery system one shelf, mount its charger at the front "
   "edge, take every pack off every charger, put each tool in its case "
   "or on a labelled hook with guards down, and put the bits and blades "
   "in the shallow drawer.",
   "Brush or blow the motor vents clear on the tool you use most "
   "before it goes back.",
   "Confirm no charger sits directly on the slab where meltwater runs "
   "off a car."],
  "causes": ["KC-009", "KC-005"],
  "victory": "One shelf per system, no pack sitting on a charger, every "
             "guard down, and bits and blades in one drawer.",
  "next": "GAS-003",
  "art": "a garage shelf system with a charger mounted at the front "
         "edge of each shelf and no battery pack sitting on any of "
         "them, tools in their cases with guards down"},

 {"id": "GAA-006", "zone": "Power Tool and Battery Zone",
  "title": "FIX THE MOMENT A FULL PACK COMES OFF", "minutes": 30,
  "players": "1", "six_s": "Standardize",
  "goal": "Agree out loud who takes a pack off the charger once it's "
          "full, and tie that moment to something that already happens "
          "every day.",
  "why": "Nothing prompts a pack to come off the charger once it's "
         "full, and the shelf being crowded is exactly why a full pack "
         "has nowhere to move to once it's done.",
  "inputs": ["nothing beyond thirty minutes", "a label for the shelf "
             "edge"],
  "steps": [
   "Agree who checks the charger shelf, and tie it to locking the side "
   "door for the night since that route already passes it.",
   "Label each shelf with its battery system so a pack never lands on "
   "the wrong platform's charger.",
   "Clear enough shelf space that a full pack has somewhere to move to, "
   "off the charger.",
   "Test the new habit tonight: lock up, and confirm nothing is left "
   "sitting on a charger."],
  "causes": ["KC-008", "KC-007"],
  "victory": "Everyone in the house can say when a full pack comes off "
             "the charger, and the shelf has room for it to move to.",
  "next": "GAA-005",
  "art": "a hand lifting a fully charged battery pack off a garage "
         "charger on the way to a side door at night, the shelf beside "
         "it labelled by system"},

 {"id": "GAA-007", "zone": "Automotive Care Zone",
  "title": "STAND, DATE, AND MATCH TO THE DRIVEWAY", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Stand every fluid bottle upright on one tray, date every "
          "opened one, and clear anything that fits no car parked "
          "outside.",
  "why": "A bottle you can't date is a bottle nobody can judge, and the "
         "only real test for keeping one is whether it matches a car "
         "actually on the driveway today.",
  "inputs": ["a wipeable tray", "a marker",
             "a metal can with a lid for rags"],
  "steps": [
   "Stand every bottle upright on one wipeable tray, write today's date "
   "on the shoulder of each one you have opened, bin anything that fits "
   "no car on this driveway, and put the oily rags in a metal can with "
   "a lid.",
   "Check the tray itself for a fresh ring before you set the bottles "
   "back on it.",
   "Coil the jumper cables and put them, with the tyre gauge, in one "
   "bag by the door."],
  "causes": ["RC-015", "KC-009"],
  "victory": "Every bottle upright and dated on one tray, nothing for a "
             "car you do not own, and the rags in a closed metal can.",
  "next": "GAS-004",
  "art": "a garage shelf holding automotive fluid bottles standing "
         "upright and dated on a clean tray, jumper cables coiled in a "
         "bag by the door, oily rags sealed in a metal can"},

 {"id": "GAA-008", "zone": "Automotive Care Zone",
  "title": "SEPARATE WHAT COULD MIX AND SEAL WHAT LEAKS", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Move anything corrosive or flammable off a shared shelf, "
          "patch or replace anything visibly seeping, and confirm the "
          "tray actually catches a drip.",
  "why": "A puddle under the shelf is the sign that something is "
         "already seeping, and a fire or poisoning risk here does not "
         "wait for you to notice it on your own schedule.",
  "inputs": ["oil-absorbent granules",
             "a replacement container for anything decanted"],
  "steps": [
   "Check every container for a weeping cap or a spreading stain "
   "underneath it.",
   "Move petrol, or any can that has ever held it, well clear of the "
   "water heater's pilot flame.",
   "Confirm nothing has been decanted into an unlabelled bottle, and "
   "relabel anything that has.",
   "Work oil-absorbent granules into any fresh stain on the slab and "
   "sweep it clean."],
  "causes": ["KC-008", "RC-016", "KC-010"],
  "victory": "No container is seeping, nothing flammable sits near a "
             "flame, and every bottle is labelled for what it actually "
             "holds.",
  "next": "GAA-007",
  "art": "a garage automotive shelf with a fuel can stored well away "
         "from a water heater, oil-absorbent granules worked into a "
         "stain on the concrete floor nearby"},

 {"id": "GAA-009", "zone": "Sports and Recreation Zone",
  "title": "HANG THE BIKES AND LABEL BY WHO PLAYS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Hang every bike on its hook, label one bin per sport this "
          "household actually plays, and confirm every helmet fits the "
          "head wearing it.",
  "why": "A bike standing on the floor is why three things have to "
         "move before it comes out, and a helmet nobody can vouch for "
         "is the one piece of gear here that genuinely protects "
         "nobody.",
  "inputs": ["wall hooks rated for the bike weight",
             "labels for each bin"],
  "steps": [
   "Hang the bikes on wall hooks and clear the floor beneath them, "
   "label one bin per activity this household currently plays, move "
   "this season's kit to the front of the shelf, and try every helmet "
   "on the head it belongs to.",
   "Retire any helmet that has taken a real impact or is past the date "
   "moulded inside it, even if the shell looks fine.",
   "Confirm the bike hooks are driven into studs, not drywall."],
  "causes": ["KC-004", "KC-008"],
  "victory": "Bikes hanging over bare floor, one labelled bin per sport "
             "still played, this season's kit at the front, and every "
             "helmet fitting a head that still wears it.",
  "next": "GAS-005",
  "art": "garage bikes hanging on wall hooks over bare floor, a row of "
         "labelled bins for different sports, this season's kit sitting "
         "at the front of the shelf"},

 {"id": "GAA-010", "zone": "Sports and Recreation Zone",
  "title": "RETIRE THE SPORT NOBODY PLAYS ANY MORE", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Judge every piece of equipment against two full seasons of "
          "no use, and let go of the gear from a sport that has "
          "actually stopped.",
  "why": "Skis and a good tent each still work and each stands for a "
         "version of the week that has not happened in years, and no "
         "amount of restacking settles that; only a real season count "
         "does.",
  "inputs": ["nothing beyond thirty minutes", "a bag for whatever "
             "leaves"],
  "steps": [
   "For each piece of stored-away gear, name the sport and ask if two "
   "full seasons of the right weather have passed with no use.",
   "If you can finish the sentence 'I will use this on ___', keep it "
   "and write that date on the bin.",
   "If you cannot finish the sentence, sell it or hand it to somebody "
   "just starting out this month.",
   "Move the bins that survive to the back of the shelf, behind this "
   "season's kit."],
  "causes": ["RC-014", "RC-015", "RC-017"],
  "victory": "Every piece of gear kept for a sport nobody plays has "
             "either a named date on its bin or has left the garage.",
  "next": "GAA-009",
  "art": "a pair of skis and a tent bag being carried out of a garage "
         "door, a bin on the shelf behind them carrying a strip of tape "
         "marked with a date"},

 {"id": "GAA-011", "zone": "Lawn and Garden Tool Zone",
  "title": "HANG THE HANDLES AND LATCH THE CHEMICALS", "minutes": 15,
  "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Hang every long-handled tool head-up on the rail, coil the "
          "hose onto its reel, and move every garden chemical behind a "
          "latch above head height.",
  "why": "A rake leaning in a corner falls on somebody eventually, and "
         "a decanted weed killer in an unlabelled bottle within reach "
         "is the single most dangerous ordinary object most garages "
         "hold.",
  "inputs": ["a wall rail with enough hooks",
             "a latched cupboard above head height"],
  "steps": [
   "Hang every long handle head-up on the rail, coil the hose onto its "
   "reel beside the door it goes out of, and move every garden chemical "
   "into a latched cupboard above head height, binning anything whose "
   "label you cannot read.",
   "Scrape and oil the spade and hoe blades before they go back on the "
   "rail.",
   "Confirm the string trimmer and hedge shears hang with their "
   "cutting ends pointing away from the aisle."],
  "causes": ["KC-007", "KC-002"],
  "victory": "Nothing leaning in a corner, a hose on its reel by the "
             "right door, and every chemical labelled, latched and "
             "above head height.",
  "next": "GAS-006",
  "art": "a garage tool rail holding every long-handled garden tool "
         "head-up, a hose coiled on its reel beside a door, a latched "
         "cupboard above head height holding labelled chemical "
         "containers"},

 {"id": "GAA-012", "zone": "Lawn and Garden Tool Zone",
  "title": "NAME THE UNLABELLED BOTTLE AND SET THE SEASON RULE",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Settle every chemical container you cannot confidently name, "
          "and apply a one-season rule to everything else on the "
          "shelf.",
  "why": "You cannot safely use what you cannot name, and a chemical "
         "kept 'just in case' past one growing season is a poison "
         "stored above a child's head for no working reason.",
  "inputs": ["a hazardous waste bag", "a marker for relabelling"],
  "steps": [
   "Start with anything unlabelled or unreadable and take it straight "
   "to household hazardous waste this month, unopened again.",
   "For everything else, ask honestly whether it will genuinely be "
   "used before the next growing season ends.",
   "Offer anything you won't use to a neighbour in its own original "
   "container.",
   "Confirm the chemical shelf carries nothing but garden chemicals, "
   "nothing else stored alongside them."],
  "causes": ["KC-005", "RC-013", "KC-010"],
  "victory": "Every remaining chemical is named, in date for one "
             "growing season, and stored on a shelf holding nothing "
             "else.",
  "next": "GAA-011",
  "art": "a hazardous waste bag beside a garden chemical shelf in a "
         "garage, one relabelled bottle standing clearly apart from an "
         "unlabelled one being carried out"},

 {"id": "GAA-013", "zone": "Bulk and Overhead Storage",
  "title": "RELABEL, DATE, AND MAP THE OVERHEAD RACK", "minutes": 15,
  "players": "1", "six_s": "Standardize", "from_first_15": True,
  "goal": "Relabel every overhead bin to read from the slab, date the "
          "ones you open, move the heaviest to the lowest rack, and map "
          "the rack by the light switch.",
  "why": "A bin nobody can read from the floor is a bin that costs a "
         "ladder just to find out what's in it, and the heaviest bins "
         "belong low, not high, long before anyone climbs for them.",
  "inputs": ["a large marker", "tape for the map"],
  "steps": [
   "Relabel every overhead bin in letters you can read standing on the "
   "slab, write the month and year on the end of each one you open, "
   "move the heaviest bins to the lowest rack, and tape a map of what "
   "is where beside the light switch.",
   "Confirm the rack bolts land in a joist, not just plasterboard.",
   "Check that nothing on the rack overhangs the parking bay."],
  "causes": ["KC-005", "KC-004"],
  "victory": "Labels readable from the floor, a date on every bin, the "
             "heaviest ones lowest, and a map by the light switch.",
  "next": "GAS-007",
  "art": "a garage overhead rack with large readable labels on every "
         "bin, the heaviest bins on the lowest level, a small map taped "
         "beside a light switch nearby"},

 {"id": "GAA-014", "zone": "Bulk and Overhead Storage",
  "title": "OPEN THE BIN NOBODY HAS TOUCHED IN YEARS", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Bring down the bin with the oldest last-opened date, and "
          "give everything inside it a real owner or a real ending.",
  "why": "Height protects the drift up here, because checking costs a "
         "ladder, so a bin can hold an unmade decision for years "
         "without anyone feeling it; the only fix is opening it on "
         "purpose.",
  "inputs": ["a rubbish sack", "a donation box", "one empty container"],
  "steps": [
   "Bring the oldest-dated bin down to the floor before judging "
   "anything in it.",
   "Open it beside a rubbish sack, a donation box and one empty "
   "container.",
   "Keep only what fits in that one container and has a living "
   "person's name attached to it.",
   "Write today's date on the bin before it goes back up, whatever is "
   "left inside it."],
  "causes": ["KC-009", "RC-014", "KC-001", "KC-006"],
  "victory": "The oldest bin in the garage has a fresh date on it, and "
             "everything inside it now has either a name or an ending.",
  "next": "GAA-013",
  "art": "an overhead storage bin lowered onto a garage floor beside a "
         "rubbish sack, a donation box and one small empty container"},

 {"id": "GAA-015", "zone": None, "title": "THE FUEL-AND-CHEMISTRY WALK",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Walk every zone once, checking that nothing flammable sits "
          "near a spark or pilot flame, and that no two chemicals "
          "stored close together could ever mix.",
  "why": "This is the one room in the house where petrol, lithium "
         "batteries, oily rags, fertiliser and weed killer all live "
         "within a few feet of each other, and none of them announce "
         "themselves as dangerous until the day they combine.",
  "inputs": ["nothing beyond thirty minutes",
             "a high latched shelf for anything relocated"],
  "steps": [
   "Check the workbench for oil-soaked rags balled loose in an open "
   "bin, and move them to a metal can with a lid.",
   "Confirm no battery pack is charging beside the fuel can or the rag "
   "bin.",
   "Check the automotive shelf and the garden chemical shelf for "
   "anything that could react if it spilled onto the other.",
   "Confirm petrol, or anything that has ever held it, is capped "
   "tight and stored away from the water heater's pilot flame."],
  "causes": ["KC-010", "KC-003"],
  "victory": "You can name, out loud, that nothing flammable in this "
             "garage sits near a spark or flame, and no two chemicals "
             "are stored close enough to mix.",
  "next": "GAA-016",
  "art": "a metal can with a lid holding oily rags in a garage, a fuel "
         "can standing well clear of a battery charger and a "
         "fertiliser bag on a separate latched shelf"},

 {"id": "GAA-016", "zone": None, "title": "THE OVERHEAD-AND-HOOK LOAD CHECK",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Walk every wall hook, rail and overhead rack in the garage "
          "once, and confirm each one is rated and anchored for what's "
          "actually hanging or stacked on it.",
  "why": "A bike hook, a tool rail and an overhead bin rack all fail "
         "the same way, quietly, into a drywall anchor instead of a "
         "stud, until the day a full load comes down on a car roof or "
         "a person underneath.",
  "inputs": ["a step ladder", "nothing else beyond thirty minutes"],
  "steps": [
   "Check that bike hooks and the tool rail are driven into studs, not "
   "drywall anchors, and that no bike hangs where a car door swings "
   "open into it.",
   "Confirm the overhead rack's heaviest bins sit on the lowest rack, "
   "not the highest.",
   "Confirm nothing on the overhead rack overhangs the parking bay.",
   "Check that nothing overhead needs two hands and a wobble to bring "
   "down safely."],
  "causes": ["KC-006", "KC-001", "KC-007"],
  "victory": "Every hook, rail and rack in the garage has been checked "
             "for what it actually carries, and nothing overhangs the "
             "parking bay.",
  "next": "GAA-017",
  "art": "a stable step ladder beneath a garage overhead rack, heavy "
         "bins sitting on its lowest level, nothing extending past the "
         "rack's own frame above a parked car"},

 {"id": "GAA-017", "zone": None, "title": "THE VERDICT SWEEP", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Walk every zone once and give a real verdict, today, to "
          "anything that has been sitting there postponed rather than "
          "stored.",
  "why": "The garage is where the rest of the house sends what it "
         "could not decide about, and anything carried in with no "
         "rail, shelf or bin already waiting for it either gets a "
         "verdict the same day or quietly becomes part of the floor.",
  "inputs": ["a rubbish sack", "a donation box",
             "nothing else beyond thirty minutes"],
  "steps": [
   "Name the half-finished project on the workbench and give it a "
   "weekend, a breakdown back to stock, or the skip.",
   "Check the automotive shelf for a bottle that matches no car on the "
   "driveway, and the sports shelf for gear nobody plays any more.",
   "Open one overhead bin that has not been touched this year and give "
   "everything in it a name and an owner, or let it go.",
   "Carry out anything with no rail, shelf or bin waiting for it right "
   "now, rather than setting it down on the floor."],
  "causes": ["RC-015", "RC-017"],
  "victory": "Nothing in the garage is sitting there postponed. Every "
             "item has either a real home or has left the building "
             "today.",
  "next": "GAA-015",
  "art": "a rubbish sack and a donation box open on a garage floor, a "
         "half-finished project on the workbench carrying a strip of "
         "tape marked with a weekend date"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Seven ordinary hard days that test a garage, one per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("GAE-001", "THE FRIDAY-NIGHT REPAIR",
  "A hinge breaks on the back door at nine at night and you need the "
  "bench clear enough to fix it right now, with the one tool you need "
  "somewhere findable.",
  ["GAZ-001"],
  "The bench top is bare enough to lay the door flat, and the tool you "
  "need is exactly where the outline says it is.",
  "If you had to shift someone else's half-finished project first, the "
  "bench's own bare standard was not being kept. Draw GAA-001 or "
  "GAA-002.",
  "a garage workbench cleared to bare wood at night under a task "
  "light, a door hinge and one hand tool laid out ready to work"),
 ("GAE-002", "THE BORROWED-DRILL SATURDAY",
  "A neighbour asks to borrow exactly one screwdriver for twenty "
  "minutes, and you need to hand it over and get it back without "
  "emptying a drawer.",
  ["GAZ-002"],
  "You find the driver on its outline in one glance, hand it over, and "
  "its outline tells you the moment it has not come back.",
  "If you had to hunt for it, or didn't notice it was still out three "
  "days later, the outline standard was not being kept. Draw GAA-003 "
  "or GAA-004.",
  "a hand lifting a single screwdriver off its drawn outline on a "
  "garage pegboard wall, the outline plainly visible"),
 ("GAE-003", "THE CORDLESS-EVERYTHING WEEKEND",
  "You've got three jobs lined up this weekend and need every "
  "cordless tool charged and ready before the first one starts.",
  ["GAZ-003"],
  "Every pack on the shelf reads full at a glance, and no tool waits "
  "behind a dead battery.",
  "If a pack was still on the charger from last week, or flat when "
  "you reached for it, the one-shelf standard was not being kept. Draw "
  "GAA-005 or GAA-006.",
  "a garage shelf of cordless tools with fully charged battery packs "
  "standing ready beside each one, no charger occupied"),
 ("GAE-004", "THE ROADSIDE BREAKDOWN CALL",
  "A family member calls from the roadside with a dead battery and "
  "needs you to grab the jump leads and go within five minutes.",
  ["GAZ-004"],
  "The jumper cables and tyre gauge come off the shelf in one motion, "
  "already together in their bag by the door.",
  "If you had to search two shelves for the cables, the automotive "
  "standard was not being kept. Draw GAA-007 or GAA-008.",
  "a hand lifting one bag holding jumper cables and a tyre gauge off "
  "a hook by a garage door, ready to leave immediately"),
 ("GAE-005", "THE SUDDEN INVITE TO PLAY",
  "A friend calls with two spare tickets to play this afternoon, and "
  "you need the right kit and a helmet that actually fits, in the "
  "next ten minutes.",
  ["GAZ-005"],
  "The labelled bin for that sport is at the front of the shelf, and "
  "the helmet fits without a second thought.",
  "If you had to dig past off-season bins or question the helmet, the "
  "sports standard was not being kept. Draw GAA-009 or GAA-010.",
  "a hand pulling one labelled sports bin from the front of a garage "
  "shelf, a helmet resting on top of it"),
 ("GAE-006", "THE FIRST FROST OF THE SEASON",
  "The forecast turns to frost overnight and you need the hose "
  "drained and put away, and the mower's fuel dealt with, before "
  "dark.",
  ["GAZ-006"],
  "The hose comes straight off its reel by the door, and every long "
  "tool is already off the wet ground and on the rail.",
  "If a tool was found leaning in a corner, or the hose was tangled "
  "on the slab, the lawn and garden standard was not being kept. Draw "
  "GAA-011 or GAA-012.",
  "a garden hose coiled on its reel beside a garage door at dusk, "
  "long-handled tools hanging head-up on a rail nearby"),
 ("GAE-007", "THE NEIGHBOUR'S ROOF-LEAK SCARE",
  "A neighbour's roof leaked and you want to check your own overhead "
  "bins for water damage tonight, without a ladder mishap in the "
  "dark.",
  ["GAZ-007"],
  "Every label reads from the slab, the map by the light switch says "
  "exactly which bay to check first, and the heaviest bins are "
  "already low enough to check without climbing.",
  "If you had to climb blind or guess which bin was which, the "
  "overhead standard was not being kept. Draw GAA-013 or GAA-014.",
  "a person reading a small map taped beside a garage light switch, "
  "pointing up at one clearly labelled overhead bin"),
]


# ---------------------------------------------------------------------------
# ASSEMBLY
# ---------------------------------------------------------------------------

def manual_zones() -> dict:
    src = json.load(io.open(SRC, encoding="utf-8"))
    room = [r for r in src["rooms"] if r["room"] == ROOM]
    if not room:
        raise SystemExit(f"{ROOM} not found in {SRC}")
    return {z["zone"]: z for z in room[0]["zones"]}


def zone_card(name: str, z: dict, spec: dict) -> dict:
    watch = [{"question": w["question"], "text": w["text"]}
             for w in z.get("watch_for", [])][:2]
    return {
        "id": spec["id"], "title": name.upper(), "type": "ZONE CARD",
        "room": ROOM, "zone": name, "order": spec["order"],
        "difficulty": spec["difficulty"], "tagline": spec["tagline"],
        "objective": z["purpose"],
        "callouts": spec["callouts"],
        "done_looks_like": z["done_looks_like"],
        "session": z["session"],
        "safety_checks": watch,
        "the_call": {"title": z["the_call"]["title"],
                     "text": z["the_call"]["text"]},
        "supplies": z["shine_detail"]["products_used"],
        "draw_next": ["the FRICTION cards for this zone"],
        "related": {"standard": f"GAS-{spec['order']:03d}",
                    "actions": [a["id"] for a in ACTIONS
                                if a["zone"] == name]},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Zone",
                "subject": spec["art"],
                "must_show": spec["callouts"],
                "must_show_kind": "objects",
                "accept_test": "Count the six callouts in the picture. If "
                               "any one of them is not a visible object, "
                               "the image is rejected."},
    }


def friction_card(meta: tuple, src_friction: dict, zone_spec: dict) -> dict:
    zone, cid, title, art = meta
    branches = [{"answer": b["answer"], "root_cause": b["cause"]}
                for b in src_friction.get("branches") or []]
    return {
        "id": cid, "title": title, "type": "FRICTION CARD", "room": ROOM,
        "zone": zone, "difficulty": 1,
        "tagline": "WHAT IT LOOKS LIKE. THEN WHY.",
        "objective": src_friction["symptom"],
        "prompt": "Why does this happen here?",
        "branches": branches,
        "instruction": "Pick the answer that is true in your garage, "
                       "then turn to that root cause card. If two are "
                       "true, take the one you could change this week.",
        "related": {"zone": zone_spec["id"],
                    "root_causes": [b["root_cause"] for b in branches]},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Friction",
                "subject": art,
                "must_show": [src_friction["symptom"]],
                "must_show_kind": "condition",
                "accept_test": "The problem has to be visible, and it has "
                               "to look like a real Tuesday rather than a "
                               "disaster. A tidy picture on a friction "
                               "card is a rejection: if a stranger could "
                               "not say what is wrong, it failed."},
    }


def cause_card(cid: str) -> dict:
    c = RC.BY_ID[cid]
    return {
        "id": cid, "title": c["name"], "type": "ROOT CAUSE CARD",
        "room": ROOM, "zone": None, "difficulty": 2, "six_s": c["six_s"],
        "tagline": f"{c['six_s'].upper()} FIXES THIS ONE.",
        "objective": c["meaning"],
        "confirm_in_30_seconds": c["confirm_30s"],
        "instruction": f"This is a {c['six_s']} problem. Draw one of the "
                       f"action cards listed and do it now, at the length "
                       f"you actually have.",
        "related": {"frictions": [], "actions": []},  # filled in build()
        "source": "ops/root_causes.py, the shared vocabulary",
        "art": {"framing": "Root Cause",
                "subject": CAUSE_ART[cid],
                "must_show": [c["meaning"]],
                "must_show_kind": "condition",
                "accept_test": "One idea, one object, no room tour. If "
                               "the picture could illustrate three "
                               "different causes it is rejected."},
    }


def action_card(a: dict) -> dict:
    zone_id = ZONES[a["zone"]]["id"] if a.get("zone") else None
    standard_id = (f"GAS-{ZONES[a['zone']]['order']:03d}"
                   if a.get("zone") else None)
    related = {"root_causes": a["causes"]}
    if zone_id:
        related["zone"] = zone_id
    if standard_id:
        related["standard"] = standard_id
    card = {
        "id": a["id"], "title": a["title"], "type": "ACTION CARD",
        "room": ROOM, "zone": a["zone"],
        "difficulty": 2 if a["minutes"] <= 15 else 3,
        "six_s": a["six_s"],
        "tagline": f"{a['minutes']} MINUTES. {a['players'].upper()}.",
        "objective": a["goal"],
        "why_it_matters": a["why"],
        "time_target_minutes": a["minutes"],
        "players": a["players"],
        "inputs": a["inputs"],
        "steps": a["steps"],
        "root_causes": a["causes"],
        "related": related,
        "victory_condition": a["victory"],
        "next_card": a["next"],
        "source": ("content/manual/source/content.json, first_15"
                    if a.get("from_first_15")
                    else "hand authored, steps grounded in the Manual "
                         "passes"),
        "art": {"framing": "Action",
                "subject": a["art"],
                "must_show": [a["victory"]],
                "must_show_kind": "condition",
                "accept_test": "The picture shows the finished state the "
                               "victory condition describes, not the "
                               "work in progress and not a person doing "
                               "it."},
    }
    return card


def standard_card(name: str, z: dict, spec: dict) -> dict:
    return {
        "id": f"GAS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
        "type": "STANDARD CARD", "room": ROOM, "zone": name,
        "difficulty": 1, "six_s": "Standardize",
        "tagline": "WRITE IT. SIGN IT. PUT IT WHERE IT HAPPENS.",
        "objective": z["leave_behind"]["standard"],
        "trigger": z["leave_behind"]["trigger"],
        "write_on": [
            "Who agreed this: ______________  and  ______________",
            "Date: ____ / ____ / ______",
            "Where this card lives: ______________________________",
        ],
        "instruction": "This is a write on card. Fill it in with a pen, "
                       "in your own words if the printed sentence is not "
                       "yours, and put it where the zone is. A standard "
                       "nobody signed is a preference.",
        "micro_quest": MICRO_QUESTS[name],
        "related": {"zone": spec["id"],
                    "actions": [a["id"] for a in ACTIONS
                                if a["zone"] == name]},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Standard",
                "subject": f"{spec['art']}, photographed plainly with a "
                           f"generous area of empty calm surface across "
                           f"the lower half for the write on lines",
                "must_show": ["the zone holding its standard"],
                "must_show_kind": "condition",
                "accept_test": "The lower half of the frame must be "
                               "visually quiet enough to print three "
                               "blank lines over it and still read."},
    }


def event_card(rec) -> dict:
    cid, title, setup, zones, holds, repair, art = rec
    return {
        "id": cid, "title": title, "type": "EVENT CARD", "room": ROOM,
        "zone": None, "difficulty": 3,
        "tagline": "THE DAY THAT TESTS IT.",
        "objective": setup,
        "tests_zones": zones,
        "held_if": holds,
        "if_it_failed": repair,
        "instruction": "Do not do anything to prepare. Live the day, "
                       "then read the two lines below and be honest "
                       "about which one you are.",
        "related": {"zones": zones},
        "source": "hand authored, not in the Manual",
        "art": {"framing": "Event",
                "subject": art,
                "must_show": [setup],
                "must_show_kind": "condition",
                "accept_test": "The pressure has to be visible in the "
                               "objects. No people, so the load has to "
                               "be shown by what is on the surfaces."},
    }


def room_card(intro: str, tips: list) -> dict:
    order = [(n, ZONES[n]) for n in ZONE_ORDER]
    start_tip = next((t for t in tips if t.get("label") == "Where to start"),
                      None)
    return {
        "id": "GAR-001", "title": "THE GARAGE", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SEVEN ZONES. START WITH THE BENCH.",
        "objective": "The garage takes what every other room in the "
                     "house evicts, and it carries three problems no "
                     "other room has all at once: fuel and garden "
                     "chemicals stored a few feet from where a car "
                     "parks, heavy bins stacked overhead above where "
                     "people walk and park, and edged power tools "
                     "within reach of a child's hand. This card is the "
                     "map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"GAZ-001 Primary Workbench. {start_tip['text']}" if start_tip
            else "GAZ-001 Primary Workbench. Clearing it changes what "
                 "the whole garage looks like from the doorway."),
        "how_to_play": [
            "1. Deal the seven ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's FRICTION cards. Keep the ones that "
            "are true in your garage. Put the rest back.",
            "3. Turn a friction card over and pick the answer that is "
            "true. It names a ROOT CAUSE.",
            "4. The root cause card names the ACTION cards that fix "
            "that cause. Pick the one that matches the time you "
            "actually have: fifteen or thirty minutes.",
            "5. Do it standing up, with the card in your hand.",
            "6. Read the victory condition out loud. If it is not true "
            "yet, you are not finished, and that is the whole scoring "
            "system.",
            "7. Fill in the zone's STANDARD card with a pen and put it "
            "where the zone is.",
            "8. Draw an EVENT card when an ordinary hard day happens, "
            "and see whether the standard held.",
        ],
        "players": "1 to 4. With more than one, split the chain: one "
                   "clears the bench and tool wall, another works the "
                   "power tools and the overhead rack.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do GAA-015 The Fuel-and-Chemistry Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "what makes this room different from every "
                        "other: fuel, lithium packs and garden chemicals "
                        "a few feet from where the car parks.",
        "related": {"contents": "GAZ-001 to GAZ-007, GAF-001 to "
                                 "GAF-025, the shared root causes in "
                                 "ops/root_causes.py, GAA-001 to "
                                 "GAA-017, GAS-001 to GAS-007, GAE-001 "
                                 "to GAE-007"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "garage in its settled state, a cleared "
                           "workbench, a hand tool wall, a power tool "
                           "shelf, an automotive shelf, a sports corner "
                           "and an overhead rack all visible in one "
                           "frame, everything put away",
                "must_show": ["all seven zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the seven zones is. If two are "
                               "not in frame, reshoot."},
    }


def build() -> dict:
    zmap = manual_zones()
    missing = [z for z in ZONES if z not in zmap]
    if missing:
        raise SystemExit(
            f"these zones are not in the Manual and would be invented: "
            f"{missing}. The deck's zone list must be the Manual's zone "
            f"list.")

    room_src = [r for r in json.load(io.open(SRC, encoding="utf-8"))["rooms"]
                if r["room"] == ROOM][0]

    cards = [room_card(room_src.get("intro", ""), room_src.get("tips", []))]
    for name, spec in sorted(ZONES.items(), key=lambda kv: kv[1]["order"]):
        cards.append(zone_card(name, zmap[name], spec))

    # Frictions: derived positionally from each zone's own diagnosis.frictions,
    # in Manual order, zipped against the hand-authored title/art metadata for
    # that same zone, in the same order. A count mismatch fails loudly rather
    # than silently pairing the wrong symptom with the wrong title.
    friction_cards = []
    fmeta_by_zone: dict = {}
    for meta in FRICTION_META:
        fmeta_by_zone.setdefault(meta[0], []).append(meta)
    for name in ZONE_ORDER:
        diag_frictions = (zmap[name].get("diagnosis") or {}).get(
            "frictions") or []
        metas = fmeta_by_zone.get(name, [])
        if len(diag_frictions) != len(metas):
            raise SystemExit(
                f"{name}: Manual has {len(diag_frictions)} diagnosed "
                f"frictions, this file authored titles for {len(metas)}. "
                f"They must match exactly.")
        for src_friction, meta in zip(diag_frictions, metas):
            friction_cards.append(
                friction_card(meta, src_friction, ZONES[name]))
    cards += friction_cards

    cause_cards = [cause_card(cid) for cid in CAUSE_IDS]
    # related.frictions / related.actions are filled here, once both lists
    # exist, the same two-pass shape every prior room generator uses.
    for cc in cause_cards:
        cc["related"]["frictions"] = [
            f["id"] for f in friction_cards
            if cc["id"] in [b["root_cause"] for b in f["branches"]]]
        cc["related"]["actions"] = [
            a["id"] for a in ACTIONS if cc["id"] in a["causes"]]
    cards += cause_cards

    cards += [action_card(a) for a in ACTIONS]
    for name, spec in sorted(ZONES.items(), key=lambda kv: kv[1]["order"]):
        cards.append(standard_card(name, zmap[name], spec))
    cards += [event_card(e) for e in EVENTS]

    gate(cards, zmap)
    return {"deck": "garage", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (build_kitchen_deck.py,
    build_entryway_deck.py, build_laundry_room_deck.py,
    build_home_office_deck.py, build_primary_bathroom_deck.py)."""
    ids = [c["id"] for c in cards]
    assert len(ids) == len(set(ids)), "duplicate card id"
    assert len(cards) == TOTAL, f"{len(cards)} cards, budget says {TOTAL}"

    got = {}
    for c in cards:
        got[c["type"]] = got.get(c["type"], 0) + 1
    assert got == BUDGET, f"type counts {got} do not match budget {BUDGET}"

    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["objective"] == zmap[c["zone"]]["purpose"]
            assert c["done_looks_like"] == zmap[c["zone"]]["done_looks_like"]
        if c["type"] == "STANDARD CARD":
            lb = zmap[c["zone"]]["leave_behind"]
            assert c["objective"] == lb["standard"]
            assert c["trigger"] == lb["trigger"]
        if c["type"] == "FRICTION CARD":
            diag = (zmap[c["zone"]].get("diagnosis") or {}).get(
                "frictions") or []
            match = [f for f in diag if f["symptom"] == c["objective"]]
            assert match, f"{c['id']} symptom not found verbatim in the Manual"

    # The zone-linked 15-minute actions per zone must quote the Manual's own
    # first_15 action and victory condition, not paraphrase them: this is
    # the exact "derived, not invented" contract the room's own ZONE and
    # STANDARD cards already keep.
    for a_spec in ACTIONS:
        if not a_spec.get("from_first_15"):
            continue
        fi = zmap[a_spec["zone"]]["diagnosis"]["first_15"]
        card = next(c for c in cards if c["id"] == a_spec["id"])
        assert fi["action"] in card["steps"], (
            f"{card['id']} does not quote the Manual's first_15 action "
            f"verbatim")
        assert card["victory_condition"] == fi["victory"], (
            f"{card['id']} victory condition does not match the Manual's "
            f"first_15 victory verbatim")

    all_micro_quests = []
    for c in cards:
        if c["type"] != "STANDARD CARD":
            continue
        mq = c.get("micro_quest") or []
        assert len(mq) == 3, f"{c['id']} has {len(mq)} micro quests, needs 3"
        for q in mq:
            assert q and q.strip() == q, (
                f"{c['id']} has a blank/untrimmed micro quest")
            assert len(q.split()) <= 30, (
                f"{c['id']} micro quest too long for a card back: {q!r}")
        all_micro_quests.extend(mq)
    assert len(all_micro_quests) == len(set(all_micro_quests)), (
        "a micro quest line repeats across zones")

    known = {c["id"] for c in cards}
    for c in cards:
        for ref in (c.get("related", {}).get("root_causes", [])
                    + c.get("root_causes", [])
                    + c.get("related", {}).get("actions", [])
                    + c.get("tests_zones", [])):
            assert ref in known, f"{c['id']} points at unknown card {ref}"
        nxt = c.get("next_card")
        assert not nxt or nxt in known, f"{c['id']} next_card {nxt} unknown"

    for c in cards:
        assert c.get("related"), f"{c['id']} has no related field"
        if c["type"] != "ACTION CARD":
            continue
        rel = c["related"]
        z, s = rel.get("zone"), rel.get("standard")
        assert not z or z in known, f"{c['id']} related.zone {z} unknown"
        assert not s or s in known, (
            f"{c['id']} related.standard {s} unknown")
        assert (z is None) == (s is None), (
            f"{c['id']} has a zone without a standard or a standard "
            f"without a zone: {rel}")

    reachable = set()
    for c in cards:
        if c["type"] == "FRICTION CARD":
            reachable |= {b["root_cause"] for b in c["branches"]}
    orphan = [c["id"] for c in cards
              if c["type"] == "ROOT CAUSE CARD" and c["id"] not in reachable]
    assert not orphan, f"root causes no friction routes to: {orphan}"
    assert reachable == set(CAUSE_IDS), (
        f"CAUSE_IDS {sorted(CAUSE_IDS)} does not match what the frictions "
        f"actually reach {sorted(reachable)}")

    treated = set()
    for c in cards:
        treated |= set(c.get("root_causes", []))
    untreated = [c["id"] for c in cards
                 if c["type"] == "ROOT CAUSE CARD" and c["id"] not in treated]
    assert not untreated, f"root causes no action addresses: {untreated}"

    # Each zone's own friction and action counts must match its own real
    # diagnosis data, not a single hardcoded number: unlike every prior
    # room, Garage does not split evenly at three frictions per zone (see
    # the module docstring), so this checks each zone against itself.
    for name in ZONES:
        expected_frictions = len(
            (zmap[name].get("diagnosis") or {}).get("frictions") or [])
        assert sum(1 for c in cards if c["type"] == "FRICTION CARD"
                   and c["zone"] == name) == expected_frictions, (
            f"{name} needs {expected_frictions} frictions, matching its "
            f"own diagnosis data")
        assert sum(1 for c in cards if c["type"] == "ACTION CARD"
                   and c["zone"] == name) == 2, f"{name} needs 2 actions"

    for c in cards:
        art = c.get("art") or {}
        assert art.get("subject"), f"{c['id']} has no art subject"
        assert art.get("accept_test"), f"{c['id']} has no art accept test"
        assert art.get("must_show_kind") in ("objects", "condition"), (
            f"{c['id']} does not say whether must_show is a list of "
            f"things to count or a condition to satisfy.")
        low = art["subject"].lower()
        for bad in ("label reading", "sign saying", "written", "text",
                    "logo", "brand"):
            assert bad not in low, f"{c['id']} art asks for {bad}"

    assert any(c["id"] == "GAA-015" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This room's zone list must be exactly the Manual's seven, in the
    # Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 7, (
        "this room's zone count moved in the Manual; ZONES above must be "
        "re-derived, not assumed")
    assert sum(len((zmap[n].get("diagnosis") or {}).get("frictions") or [])
               for n in ZONES) == 25, (
        "this room's total friction count moved in the Manual; "
        "FRICTION_META above must be re-derived, not assumed")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        garage ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
