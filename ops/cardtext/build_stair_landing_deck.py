#!/usr/bin/env python3
"""
Build the Stair Landing deck: 40 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: six rooms already carry a full diagnosis layer and
a shipped deck (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home
Office, Garage). Stair Landing is the smallest of the fourteen rooms that had
rich, hand-authored Manual content, purpose/done_looks_like/passes/the_call/
watch_for/leave_behind/shine_detail for all three zones, but no diagnosis
layer and no deck. This file adds that layer to
content/manual/source/content.json (nine frictions, twenty-seven branches,
three first_15 actions) and builds the deck straight off it, the same shape
ops/cardtext/build_entryway_deck.py and ops/cardtext/build_garage_deck.py
already use for their rooms.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
nine frictions (symptom and every branch to a root cause) are likewise
derived straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the six
zone-linked action cards, the three whole-room actions, the event cards, the
micro quests, and the room card. The root causes are not reauthored: they
are the same frozen vocabulary in ops/root_causes.py that every other room's
deck already uses, so a household owning more than one deck keeps one
diagnosis pile rather than several (DECK-GAME-DESIGN.md 4.3). Twelve of the
seventeen shared ids are reachable from this room's real frictions, counted
honestly from the branches actually written below, not chosen first and
filled in: KC-001, KC-002, KC-003, KC-006, KC-008, KC-009, KC-010, KC-011,
RC-013, RC-015, RC-016, RC-017. KC-004, KC-005, KC-007, KC-012 and RC-014
are not reachable because nothing in this room's real diagnosis branches to
them, and that is a true statement about this small three-zone room, not an
oversight; nothing pads the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Stair Landing ships as a free typeset page, the same stage every prior room
in this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here). The budget below is the honest count of what this
room's own three-zone corpus, diagnosis layer and a proportionate amount of
new authorship produce, scaled the same way Entryway scaled proportionally
to five zones: three real zones, nine frictions (three per zone, matching
every other room in this line), twelve reachable root causes, nine action
cards (two per zone plus three whole-room, the same "2 per zone + 3
whole-room" shape Entryway and Garage both use), three standard cards and
three event cards. 40 cards in total, not padded or trimmed to match any
other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_stair_landing_deck.py
Out:  ops/cardtext/stair-landing-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "stair-landing-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Stair Landing"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 3, "FRICTION CARD": 9,
          "ROOT CAUSE CARD": 12, "ACTION CARD": 9, "STANDARD CARD": 3,
          "EVENT CARD": 3}
TOTAL = sum(BUDGET.values())

# Same palette family as every other room's deck so a mixed pile of cards
# still reads as one product line.
TYPE_COLOUR = {
    "ROOM CARD": "#2B2622", "ZONE CARD": "#2F5233",
    "FRICTION CARD": "#BC4B2A", "ROOT CAUSE CARD": "#6E5B8B",
    "ACTION CARD": "#3C5A6B", "STANDARD CARD": "#4E7A57",
    "EVENT CARD": "#8C5A2B",
}

# Root causes this room's real diagnosis branches actually reach, derived
# below from the Manual and asserted (in gate()) to be exactly this set: not
# a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-006", "KC-008", "KC-009",
             "KC-010", "KC-011", "RC-013", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Landing Surface or Console": {
  "id": "SLZ-001", "order": 1, "difficulty": 2,
  "tagline": "THREE THINGS ON TOP. ONE BASKET ON THE FLOOR. BOTH EMPTY OF YESTERDAY.",
  "callouts": [
   "A lamp, a framed photo and one tray, three things on the console top",
   "The tray holding only keys and coins, nothing left from yesterday",
   "The lamp cord clipped down the back leg, clear of the walking side",
   "One stair basket standing on the floor at the end nearest the top step",
   "The stair basket empty",
   "Bare surface around all three permanent items, nothing overhanging the stair side",
  ],
  "art": ("a narrow console table standing beside a staircase holding a "
          "lamp, a framed photo and one shallow tray with visible bare "
          "wood around each, a woven basket sitting empty on the floor at "
          "the end nearest the bottom of the stairs, and a lamp cord "
          "running down the back leg clipped flat"),
 },
 "Wall and Display Zone": {
  "id": "SLZ-002", "order": 2, "difficulty": 3,
  "tagline": "EVERY FRAME LEVEL. TWO POINTS EACH. NOTHING A SHOULDER CAN CATCH.",
  "callouts": [
   "A row of frames climbing the wall on the stair's own diagonal, evenly spaced",
   "Every frame hanging level, none tilted",
   "Two visible hanging points on each frame, no single nail or sawtooth hanger",
   "The mirror at the turn sitting flat against the wall",
   "Nothing projecting more than a hand's width out from the wall at shoulder height",
   "A clean wall along the turn, no grey shoulder-height smear",
  ],
  "art": ("a stairway wall with a row of picture frames climbing on the "
          "same diagonal as the stairs, each frame hanging level and "
          "evenly spaced with two visible picture hooks behind each one, "
          "a flat mirror at the turn of the stairs showing no gap behind "
          "it, and a clean unmarked wall at shoulder height"),
 },
 "Stair and Floor Path": {
  "id": "SLZ-003", "order": 3, "difficulty": 3,
  "tagline": "BARE TREADS. CLEAR RAIL. LIT AT BOTH ENDS.",
  "callouts": [
   "Every tread bare from nose to riser, including the bottom three steps",
   "The runner lying flat with no lifted corner at the turn",
   "The handrail running clear and unobstructed, top newel to bottom",
   "No bag, coat or lead hung on either newel post",
   "The light lit over the top step",
   "The light lit over the bottom step",
  ],
  "art": ("a full flight of stairs seen from the bottom, every tread bare "
          "and visible from nose to riser, a runner lying completely flat "
          "down the centre with no lifted corner at the turn, an "
          "unobstructed handrail running the full length with nothing "
          "hung on either newel post, and light visibly falling on both "
          "the top step and the bottom step"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# DIAGNOSIS LAYER. Written into content/manual/source/content.json by this
# project (not this file): each zone's own "diagnosis" object holds
# "frictions" (symptom plus branches to a shared root-cause id) and
# "first_15" (a genuine fifteen-minute starting action and a checkable
# victory condition). This dict is this file's own record of what that
# layer is expected to hold, so build() can assert nothing has drifted
# between the two files.
# ---------------------------------------------------------------------------

EXPECTED_DIAGNOSIS = {
 "Landing Surface or Console": {
  "frictions": [
   {"symptom": "Things ride the stair basket for days without ever "
               "landing where they actually belong.",
    "branches": [
     {"answer": "Nothing marks the moment to carry it, so it waits for a "
                "trip that never comes on its own", "cause": "KC-009"},
     {"answer": "The item doesn't have a real home on the floor it's "
                "headed to", "cause": "KC-002"},
     {"answer": "It's not clutter, it's a decision I haven't made yet "
                "about where it goes", "cause": "RC-015"},
    ]},
   {"symptom": "A book, a phone or a set of keys ends up hanging over the "
               "stair side of the console instead of set back from it.",
    "branches": [
     {"answer": "Nobody agreed exactly what may and may not sit on this "
                "surface", "cause": "KC-008"},
     {"answer": "I stopped noticing the edge creep because I see this "
                "console every day", "cause": "RC-017"},
     {"answer": "The tray sits at the wrong end, so hands set things down "
                "closer to the stair side", "cause": "KC-003"},
    ]},
   {"symptom": "Loose screws, dry pens, keys to nothing and mail already "
               "read pile back into the drawer almost as soon as it is "
               "cleared.",
    "branches": [
     {"answer": "None of these things has anywhere else in the house to "
                "go", "cause": "KC-002"},
     {"answer": "I'm keeping more just-in-case odds and ends than this "
                "drawer was ever meant to hold", "cause": "KC-001"},
     {"answer": "Nobody in the house is assigned to clear this drift, so "
                "it's whoever notices first", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Clear the console top and drawer in one sweep: keep only "
             "what truly lives on this floor, drop anything headed to "
             "another floor straight into the stair basket, and bag up "
             "the loose screws, dead pens and read mail that have drifted "
             "in.",
   "victory": "The console top holds only its permanent items and an "
              "empty tray, and the stair basket on the floor is empty.",
  },
 },
 "Wall and Display Zone": {
  "frictions": [
   {"symptom": "At least one frame on this wall is still held up by a "
               "single nail or a sawtooth hanger instead of two rated "
               "points.",
    "branches": [
     {"answer": "Taking it down properly means finding a stud and "
                "patching a hole I've been putting off", "cause": "RC-015"},
     {"answer": "Nobody set a rule that every frame on this flight gets "
                "two hanging points", "cause": "KC-008"},
     {"answer": "A stair wall shakes with every footstep, and single-point "
                "hardware works loose here faster than anywhere else in "
                "the house", "cause": "KC-010"},
    ]},
   {"symptom": "The mirror or the biggest frame on the wall has some play "
               "in it when you push up and out on it.",
    "branches": [
     {"answer": "I've never actually press-tested it, so I don't know how "
                "loose it's gotten", "cause": "RC-017"},
     {"answer": "It's awkward to reach behind the mirror at the turn to "
                "check it, so nobody bothers", "cause": "RC-016"},
     {"answer": "Nobody is assigned to check hardware on this wall, so it "
                "only gets tested by accident", "cause": "RC-013"},
    ]},
   {"symptom": "A frame has drifted out of level, or something on the "
               "wall projects far enough to catch a shoulder or a bag "
               "going past.",
    "branches": [
     {"answer": "Nobody checks this wall on a schedule, so drift is only "
                "caught by accident", "cause": "KC-009"},
     {"answer": "Constant footfall vibration is working the hardware "
                "loose between checks", "cause": "KC-010"},
     {"answer": "The spacing was eyeballed rather than measured off the "
                "tread nose below it, so nothing caps how far a piece can "
                "sit out from the wall", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Walk the flight and take down every frame still hanging "
             "from a single nail or a sawtooth hanger, along with "
             "anything with cracked glass, and set them aside rather than "
             "rehanging them the same way.",
   "victory": "No frame on the wall hangs from a single nail or a "
              "sawtooth hanger, and nothing with cracked glass has gone "
              "back up.",
  },
 },
 "Stair and Floor Path": {
  "frictions": [
   {"symptom": "A lifted runner corner or a loose rod gets pressed back "
               "into place and left instead of actually refixed.",
    "branches": [
     {"answer": "Fixing it properly means clearing the whole flight and "
                "buying rods or tape, and that's a bigger job than the "
                "few minutes I have when I notice it", "cause": "RC-015"},
     {"answer": "Nothing prompts a proper refix, so pressing it down "
                "becomes the whole routine", "cause": "KC-009"},
     {"answer": "I've stopped seeing the lifted corner as a real hazard "
                "because it's been like that for a while",
      "cause": "RC-017"},
    ]},
   {"symptom": "A bulb lighting the top or bottom step burns out and "
               "nobody replaces it until someone nearly misses a step in "
               "the dark.",
    "branches": [
     {"answer": "There's no spare bulb kept on hand for this fitting, so "
                "a burnout turns into a multi-day wait", "cause": "KC-011"},
     {"answer": "Nobody checks the stairwell lighting on a schedule, it "
                "only gets noticed at night by accident", "cause": "KC-009"},
     {"answer": "Nobody in the house is the one who's supposed to notice "
                "or replace it", "cause": "RC-013"},
    ]},
   {"symptom": "Laundry, shoes or a delivery box gets set down on the "
               "bottom three steps instead of carried the rest of the "
               "way.",
    "branches": [
     {"answer": "The thing on the step has no assigned home on the floor "
                "it's actually headed to", "cause": "KC-002"},
     {"answer": "There's no agreed rule that stairs are never used as a "
                "shelf", "cause": "KC-008"},
     {"answer": "Carrying it needs a free hand, and the hand that should "
                "be on the rail is already full, so it gets set down "
                "instead", "cause": "KC-006"},
    ]},
  ],
  "first_15": {
   "action": "Clear every tread of anything sitting on it, laundry, "
             "shoes, a box, in one trip to where it actually belongs, "
             "then stand at the bottom of the flight and check that both "
             "the top and bottom lights actually come on.",
   "victory": "Every tread is bare from nose to riser, and both the top "
              "and bottom stair lights work.",
  },
 },
}


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine. Three per
# zone, matching that data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Landing Surface or Console", "SLF-001", "THE BASKET NEVER MAKES THE TRIP",
  "a woven basket sitting on a stair landing floor holding a stack of "
  "folded clothes, a paperback book and a single shoe, positioned at the "
  "top of a staircase as if waiting for a trip that keeps not happening"),
 ("Landing Surface or Console", "SLF-002", "SOMETHING CREEPS PAST THE STAIR-SIDE EDGE",
  "a narrow console table beside an open stairwell with a paperback book "
  "resting with its spine projecting just past the table's stair-side "
  "edge, the top of a staircase visible immediately below"),
 ("Landing Surface or Console", "SLF-003", "THE DRAWER REFILLS WITHIN DAYS",
  "an open shallow console drawer crowded with loose screws, a handful of "
  "pens, a single unlabeled key and a small stack of opened envelopes, no "
  "dividers separating any of it"),

 ("Wall and Display Zone", "SLF-004", "A FRAME STILL HANGS FROM ONE NAIL",
  "a single picture frame on a stairway wall hanging slightly crooked "
  "from one visible nail, a small gap of unhung wall space around it "
  "where a proper two-point mount would sit"),
 ("Wall and Display Zone", "SLF-005", "THE MIRROR MOVES WHEN YOU PUSH IT",
  "a hand pressed flat against the edge of a wall mirror at a stair turn, "
  "a thin sliver of shadow visible along one edge where the frame has "
  "lifted slightly away from the wall"),
 ("Wall and Display Zone", "SLF-006", "A FRAME DRIFTS OUT OF LEVEL",
  "a row of picture frames climbing a stairway wall with one frame "
  "visibly tilted out of level compared to its neighbors, its bottom "
  "corner sitting slightly further from the wall than the frames beside "
  "it"),

 ("Stair and Floor Path", "SLF-007", "THE RUNNER GETS PRESSED BACK DOWN, NOT FIXED",
  "a stair runner with one corner visibly lifted away from a tread at "
  "the turn of a staircase, a faint crease across the carpet where it "
  "has clearly been pressed flat before"),
 ("Stair and Floor Path", "SLF-008", "A DEAD BULB GOES UNNOTICED OVER THE TOP STEP",
  "a dark stairwell light fitting over a top step with no bulb glowing, "
  "the step below sitting in shadow while daylight from a nearby window "
  "lights the rest of the hallway"),
 ("Stair and Floor Path", "SLF-009", "SOMETHING GETS STAGED ON THE BOTTOM STEPS",
  "a small cardboard delivery box and a single shoe sitting on the "
  "bottom three steps of a staircase, the rest of the flight above "
  "completely bare"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, stair-landing-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a console drawer beside a staircase pulled open to show far "
           "more loose pens, screws and odd keys than the drawer was ever "
           "meant to hold",
 "KC-002": "a folded sweater sitting alone in a stair basket at the top "
           "of a flight with no obvious destination shelf or drawer "
           "anywhere nearby",
 "KC-003": "a shallow tray sitting at the far end of a narrow console "
           "table, well away from the end nearest the top of the stairs "
           "where a hand would actually land",
 "KC-006": "a person's one free hand pressed to a stair handrail while "
           "the other arm holds a stacked laundry basket too full to set "
           "anything else down on the steps",
 "KC-008": "a stairway console at dusk with one end completely bare and "
           "the other end crowded with a book, a phone and a set of keys, "
           "no visible line dividing the two",
 "KC-009": "a landing light switch beside an empty stair basket, the "
           "basket still sitting there untouched after the light has "
           "clearly already been switched off once that evening",
 "KC-010": "a heavy framed mirror at a stair turn with a hand pushing up "
           "on its lower edge, a thin sliver of shadow showing where it "
           "has lifted slightly off the wall",
 "KC-011": "an empty light fitting socket over a stairwell with no spare "
           "bulb visible anywhere nearby on the landing",
 "RC-013": "a stair landing at the end of the day with a basket still "
           "full and a wall switch untouched, no single person's coat or "
           "bag nearby to say whose job this was tonight",
 "RC-015": "a stack of opened envelopes sitting on a landing console "
           "tray, one half pulled out with a form visible but nothing "
           "filled in",
 "RC-016": "a vacuum attachment reaching awkwardly into the crevice where "
           "a stair tread meets its riser beside a runner tucked tight "
           "against the stringer",
 "RC-017": "a single picture frame hanging visibly crooked on a stairway "
           "wall among several other frames that all hang level and "
           "straight",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Landing Surface or Console": [
  "Wipe the top rim of the lamp shade where the stairwell draught keeps "
  "dropping a grey collar.",
  "Check the drawer runners for grit and brush them clear before you "
  "slide the drawer home.",
  "Press one corner of the console, and if it rocks, shim it before you "
  "set anything back down.",
 ],
 "Wall and Display Zone": [
  "Tilt each frame slightly as your hand leaves it and check the wire "
  "and hook behind for a kink or a bent lip.",
  "Wipe the grey shoulder-height smear along the turn where bags and "
  "baskets rub the wall.",
  "Dust the top rim of any sconce and lift cobwebs off its arm with a "
  "soft brush attachment.",
 ],
 "Stair and Floor Path": [
  "Vacuum the crevice where each tread meets its riser, where trapped "
  "grit polishes a runner slick.",
  "Test the smoke alarm on this landing by pressing and holding the "
  "button until it sounds a full tone.",
  "Wipe both newel post caps, where dust settles and set-down keys leave "
  "a film.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-room actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "SLA-001", "zone": "Landing Surface or Console",
  "title": "CLEAR THE CONSOLE AND THE BASKET",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the console top and drawer, route anything headed "
          "elsewhere straight into the stair basket, and carry the "
          "basket the rest of the way.",
  "why": "Paper, screws and pens with no verdict are why this surface "
         "fills back up faster than any reset here can outpace.",
  "inputs": ["a bin bag", "the recycling bin"],
  "steps": [
   "Clear the console top and drawer in one sweep: keep only what truly "
   "lives on this floor, drop anything headed to another floor straight "
   "into the stair basket, and bag up the loose screws, dead pens and "
   "read mail that have drifted in.",
   "Carry the stair basket up or down right now and bring it back empty "
   "rather than setting it down half done.",
   "Wipe the tray and set it back holding only keys and coins."],
  "causes": ["KC-009", "RC-015"],
  "victory": "The console top holds only its permanent items and an "
             "empty tray, and the stair basket on the floor is empty.",
  "next": "SLS-001",
  "art": "a console table beside a staircase with a bare top holding only "
         "a lamp, a photo and an empty tray, a woven basket sitting empty "
         "on the floor beside it"},

 {"id": "SLA-002", "zone": "Landing Surface or Console",
  "title": "GIVE THE CONSOLE A NAMED LIMIT",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Move the tray to where your hand actually lands, clip the "
          "lamp cord clear, and give the drawer named sections so drift "
          "stops routing back in.",
  "why": "A tray in the wrong spot and a drawer with no named sections "
         "is why keys land beside it and screws pile back up within "
         "days.",
  "inputs": ["a shallow tray", "small dividers or a tin for loose items",
             "a marker", "a cable clip for the lamp cord"],
  "steps": [
   "Move the tray to the end of the console nearest the top step, where "
   "your hand actually lands as you turn in.",
   "Clip the lamp cord down the back leg so it never lies across the "
   "side people walk.",
   "Fit a small tin or divider in the drawer for loose screws, pens and "
   "keys to nothing, and write what belongs in each section.",
   "Set a rule for the drift pile: anything that has sat in the tin two "
   "weeks without being claimed gets thrown out or moved to its real "
   "home."],
  "causes": ["KC-003", "KC-001"],
  "victory": "The tray sits at the end nearest the top step, the lamp "
             "cord is clipped clear of the walking side, and the "
             "drawer's sections each hold one named kind of item.",
  "next": "SLA-001",
  "art": "a narrow stairside console with a tray positioned at the end "
         "nearest the bottom of the stairs, a lamp cord visibly clipped "
         "down the back leg, and an open drawer below divided into small "
         "labeled sections"},

 {"id": "SLA-003", "zone": "Wall and Display Zone",
  "title": "TAKE DOWN WHAT HANGS FROM ONE NAIL",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take down every frame still hanging from a single nail or a "
          "sawtooth hanger, and anything with cracked glass.",
  "why": "A stair wall shakes with every footstep, and single-point "
         "hardware is the first thing that lets go here.",
  "inputs": ["nowhere to set frames down but a soft surface"],
  "steps": [
   "Walk the flight and take down every frame still hanging from a "
   "single nail or a sawtooth hanger, along with anything with cracked "
   "glass, and set them aside rather than rehanging them the same way.",
   "Sort what came down into two piles: worth rehanging properly, and "
   "honestly not looked at in years.",
   "Leave the wall bare where a piece came down rather than rehanging it "
   "the same way it just failed."],
  "causes": ["KC-010", "KC-008"],
  "victory": "No frame on the wall hangs from a single nail or a "
             "sawtooth hanger, and nothing with cracked glass has gone "
             "back up.",
  "next": "SLS-002",
  "art": "a stairway wall with one bare patch where a frame has just "
         "been taken down, the remaining frames all hanging level and "
         "undisturbed"},

 {"id": "SLA-004", "zone": "Wall and Display Zone",
  "title": "REHANG ON TWO POINTS AND PRESS-TEST",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Rehang everything on two rated points measured off the tread "
          "below it, and press-test the heaviest piece before trusting "
          "it again.",
  "why": "Stair walls take constant vibration, and single-point hardware "
         "works loose here faster than anywhere else in the house.",
  "inputs": ["two picture hooks or D-rings per frame",
             "a stud finder or wall anchors for the mirror",
             "a tape measure", "a dated sticker"],
  "steps": [
   "Measure from each frame's centre down to the tread nose beneath it, "
   "and hold that number constant up the flight.",
   "Rehang every frame on two hooks and a wire, never a single nail or a "
   "sawtooth hanger.",
   "Find a stud or fit a proper wall anchor for the mirror or the "
   "heaviest frame, never friction and gravity alone.",
   "Grip the mirror and push up and out on it; if it moves at all, refit "
   "it before you finish.",
   "Stick a dated sticker on the back of the lowest frame recording "
   "today as the last press-test."],
  "causes": ["KC-010", "RC-017"],
  "victory": "Every frame hangs from two rated points measured off the "
             "tread below it, the mirror is fixed to a stud or a proper "
             "anchor, and it does not move when pushed.",
  "next": "SLA-003",
  "art": "a stairway wall with a frame being lifted onto two picture "
         "hooks measured level with a tape, a heavy mirror at the turn "
         "anchored flush to the wall with no gap visible behind it"},

 {"id": "SLA-005", "zone": "Stair and Floor Path",
  "title": "CLEAR THE TREADS AND CHECK BOTH LIGHTS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear every tread of anything sitting on it, and confirm both "
          "the top and bottom stair lights actually work.",
  "why": "A dead bulb over the top step is the single most dangerous "
         "fault this room can hold, and it hides until someone finds it "
         "in the dark.",
  "inputs": ["a spare bulb if one is on hand"],
  "steps": [
   "Clear every tread of anything sitting on it, laundry, shoes, a box, "
   "in one trip to where it actually belongs, then stand at the bottom "
   "of the flight and check that both the top and bottom lights "
   "actually come on.",
   "If a bulb is out, switch the light off at the wall, let it cool, and "
   "replace it from a properly footed ladder on the landing, never "
   "balanced on a tread.",
   "Note the bottom three steps by name: they are stairs, not a shelf, "
   "and nothing goes back on them."],
  "causes": ["KC-009", "KC-011", "KC-006"],
  "victory": "Every tread is bare from nose to riser, and both the top "
             "and bottom stair lights work.",
  "next": "SLS-003",
  "art": "a staircase with every tread completely bare and light "
         "visibly falling on both the top step and the bottom step"},

 {"id": "SLA-006", "zone": "Stair and Floor Path",
  "title": "REFIX THE RUNNER OR TAKE IT UP",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Make the real decision on a runner that has already lifted "
          "once: refix it properly along its whole length or take it up "
          "entirely.",
  "why": "A runner corner pressed back down once has already told you "
         "what it will do again, and the half-fix is worse than either "
         "honest option.",
  "inputs": ["stair rods or full-width non-slip tape",
             "a staple gun or tack strip if refitting",
             "gloves for removal if taking it up"],
  "steps": [
   "Decide today, out loud: refix the whole runner properly, or take it "
   "up and live with bare treads.",
   "If refixing, resecure it the full length with rods or full-width "
   "tape on every tread, not a patch on the one failed corner.",
   "If removing, pull it up entirely, tread by tread, rather than "
   "leaving a half-removed strip.",
   "Vacuum the crevice where each tread meets its riser and along the "
   "stringer before anything goes back down.",
   "Tug every edge of the finished runner, or press every bare tread, to "
   "confirm nothing shifts underfoot."],
  "causes": ["RC-015", "RC-017"],
  "victory": "The runner lies flat and fixed the whole length with no "
             "corner left pressing back down, or the stairs are bare "
             "treads with no runner left half-attached.",
  "next": "SLA-005",
  "art": "a staircase runner being fixed flat along its whole length "
         "with a row of stair rods, no lifted corner visible anywhere "
         "down the flight"},

 {"id": "SLA-007", "zone": None, "title": "THE FULL FLIGHT SAFETY WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk the whole flight once, top to bottom, testing every "
          "tread, the rail, the runner and both lights before trusting "
          "any of it.",
  "why": "The falls that hurt people on a staircase never show up unless "
         "you test for them on purpose: a loose tread, a lifted runner, "
         "a dead bulb and a wall hanging that could come down all hide "
         "until someone finds them the hard way.",
  "inputs": ["nothing beyond thirty minutes and a working set of hands"],
  "steps": [
   "Press each tread nose for movement and tug every runner edge as you "
   "walk down the flight.",
   "Grip the handrail hard at the top, middle and bottom to find any "
   "bracket that has worked loose.",
   "Stand at the bottom in the dark and look at the top step, then stand "
   "at the top and look at the bottom, confirming both lights actually "
   "work.",
   "Push up and out on the mirror and the heaviest frame on the wall to "
   "confirm neither has any play.",
   "Fix what you find right there, or write it down with today's date if "
   "it needs a tool you do not have to hand."],
  "causes": ["KC-010", "RC-016"],
  "victory": "You can name, out loud, that the treads, the rail, the "
             "runner, both lights and the wall hangings have each been "
             "checked today.",
  "next": "SLA-006",
  "art": "a hand testing a stair tread with a foot's pressure partway "
         "down a flight, the handrail, a runner and a wall frame all "
         "visible along the same view"},

 {"id": "SLA-008", "zone": None, "title": "THE WEEKLY RAIL AND FRAME PASS",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "Wipe the handrail its full length and press-test the two "
          "nearest frames on the same pass, so the wall gets checked ten "
          "seconds at a time.",
  "why": "Handrail day is also frame day: footfall works stairway "
         "hardware loose constantly, and the only check that survives a "
         "busy week is one stitched onto a chore already being done.",
  "inputs": ["a microfiber cloth", "a neutral pH cleaner"],
  "steps": [
   "Wipe the handrail end to end, underside included, as you go up the "
   "flight.",
   "Push up and out on the two frames nearest your hand at each stop.",
   "Flag anything that moved, and note it on the dated sticker on the "
   "lowest frame."],
  "causes": ["KC-009", "RC-013"],
  "victory": "The rail is wiped its full length, and the two nearest "
             "frames were press-tested the same day.",
  "next": "SLA-004",
  "art": "a hand wiping a stair handrail with a cloth while the other "
         "hand rests briefly against a nearby picture frame on the wall"},

 {"id": "SLA-009", "zone": None, "title": "THE THREE-NIGHT VERDICT SWEEP",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Check the stair basket and the console tray for anything that "
          "has ridden along too many nights running, and give each one "
          "a real verdict tonight.",
  "why": "An item riding the basket three nights without landing "
         "anywhere does not have a pending trip, it has no home on the "
         "destination floor, and pretending otherwise is how the console "
         "and the bottom steps fill up.",
  "inputs": ["a pen to note tonight's date",
             "wherever the item's real home should be"],
  "steps": [
   "Check what has been sitting in the stair basket or the console tray, "
   "and note anything that has been there longer than two nights.",
   "For each one, give it a home on its destination floor tonight, or "
   "decide it does not belong in the house and remove it.",
   "Carry the basket the rest of the way and bring it back empty before "
   "you go to bed."],
  "causes": ["KC-002", "RC-015"],
  "victory": "Nothing in the basket or the tray has been sitting for "
             "more than two nights, and the basket goes to bed empty.",
  "next": "SLA-001",
  "art": "a stair basket being carried up a flight of stairs at night, "
         "the console tray visible below sitting completely empty"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Three ordinary hard days that test a stair landing.
# ---------------------------------------------------------------------------

EVENTS = [
 ("SLE-001", "THE LAUNDRY BASKET DESCENT",
  "Someone carries a full laundry basket down the flight with both "
  "hands, unable to see their own feet or hold the rail.",
  ["SLZ-003"],
  "Every tread is bare underfoot and both lights are already on, so the "
  "whole descent happens without a single glance down.",
  "If something on a tread had to be stepped around blind, the bottom "
  "three steps were being used as a shelf again. Draw SLA-005.",
  "a person's feet descending a staircase carrying a large laundry "
  "basket that blocks the view of the treads below, every step visible "
  "underneath bare and clear"),
 ("SLE-002", "THE GUEST WHO LEANS ON THE WALL",
  "A guest carrying bags up the stairs for the first time reaches out "
  "and grabs the nearest frame or the mirror at the turn for balance.",
  ["SLZ-002"],
  "Whatever they grabbed holds its full weight without shifting, "
  "because it was already hanging from two rated points.",
  "If a frame moved or came away from the wall under a stranger's grip, "
  "it was still resting on one nail or friction alone. Draw SLA-004.",
  "a hand gripping the edge of a picture frame on a stairway wall for "
  "balance, the frame staying perfectly level against the wall"),
 ("SLE-003", "THE BULB THAT PICKS TONIGHT TO DIE",
  "The bulb over the top step burns out the same night as an unplanned "
  "errand, and the flight goes dark exactly when the whole house is "
  "walking it before bed.",
  ["SLZ-003"],
  "A spare bulb is already on hand, so the fitting is relit within "
  "minutes and nobody takes the flight in the dark.",
  "If nobody had a spare and someone crossed the flight blind, the "
  "fitting had no backup stocked. Draw SLA-005 and keep a spare with the "
  "landing's own cleaning caddy from then on.",
  "a hand fitting a fresh light bulb into a stairwell fixture over the "
  "top step, the rest of the landing lit warmly around it"),
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
        "draw_next": ["the three FRICTION cards for this zone"],
        "related": {"standard": f"SLS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true on your landing, "
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
    standard_id = (f"SLS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"SLS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
                               "objects. No people's faces, so the load "
                               "has to be shown by what is on the "
                               "surfaces and, where unavoidable, by hands "
                               "and feet alone."},
    }


def room_card(intro: str, tips: list) -> dict:
    order = [(n, ZONES[n]) for n in ZONE_ORDER]
    start_tip = next((t for t in tips if t.get("label") == "Where to start"),
                      None)
    return {
        "id": "SLR-001", "title": "THE STAIR LANDING", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "THREE ZONES. START WITH THE STAIRS THEMSELVES.",
        "objective": "The stair landing belongs to nobody, and it is the "
                     "one route in the house where a small oversight "
                     "turns into a real injury. This card is the map and "
                     "the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"SLZ-003 Stair and Floor Path. {start_tip['text']}"
            if start_tip else
            "SLZ-003 Stair and Floor Path. Clearing the treads and the "
            "lighting sets the limit on what the console and the wall "
            "are allowed to hold."),
        "how_to_play": [
            "1. Deal the three ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true on your landing. Put the rest back.",
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
        "players": "1 to 6. With more than one, deal the friction cards "
                   "out and let each person keep the ones they believe. "
                   "Disagreement is the useful part, not a problem to "
                   "resolve before starting.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do SLA-007 The Full Flight Safety Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "every tread, the rail, the runner, both lights "
                        "and every wall hanging on the flight.",
        "related": {"contents": "SLZ-001 to SLZ-003, SLF-001 to SLF-009, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, SLA-001 to SLA-009, "
                                 "SLS-001 to SLS-003, SLE-001 to SLE-003"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole staircase "
                           "and landing in its settled state, a console "
                           "table, a wall of framed pictures and a full "
                           "flight of bare treads all visible in one "
                           "frame",
                "must_show": ["all three zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the three zones is. If one is "
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

    for name in ZONE_ORDER:
        diag = zmap[name].get("diagnosis")
        if not diag:
            raise SystemExit(
                f"{name} has no diagnosis layer in {SRC}. Add "
                f"EXPECTED_DIAGNOSIS[{name!r}] to content.json before "
                f"building this deck.")
        expected = EXPECTED_DIAGNOSIS[name]
        if diag != expected:
            raise SystemExit(
                f"{name}: content.json's diagnosis layer does not match "
                f"this file's own EXPECTED_DIAGNOSIS record. Reconcile "
                f"the two before building.")

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
    # exist, the same two-pass shape every prior generator in this line uses.
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
    return {"deck": "stair-landing", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_garage_deck.py)."""
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
            for b in c["branches"]:
                assert b["root_cause"] in RC.BY_ID, (
                    f"{c['id']} branch cause {b['root_cause']!r} is not one "
                    f"of the 17 frozen root causes in ops/root_causes.py")

    # The two zone-linked 15-minute actions per zone must quote the Manual's
    # own first_15 action and victory condition, not paraphrase them.
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

    for name in ZONES:
        assert sum(1 for c in cards if c["type"] == "FRICTION CARD"
                   and c["zone"] == name) == 3, f"{name} needs 3 frictions"
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

    assert any(c["id"] == "SLA-007" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This deck's zone list must be exactly the Manual's three, in the
    # Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 3, (
        "this room has three Manual zones; that count moved")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        stair-landing ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
