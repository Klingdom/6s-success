#!/usr/bin/env python3
"""
Build the Primary Bathroom deck: 76 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
`content/manual/source/content.json`, the same corpus the 114 zone pages
already read. `ops/cardtext/build_kitchen_deck.py`,
`ops/cardtext/build_entryway_deck.py`, `ops/cardtext/build_laundry_room_deck.py`
and `ops/cardtext/build_home_office_deck.py` proved the pattern for the
first four rooms; this is the fifth. Purpose, done_looks_like, the standard,
the trigger, the first-15 action and its victory condition are quoted from
the Manual, not rewritten, and `gate()` at the bottom asserts they are still
character-for-character identical. The 21 frictions (three per zone) are
likewise derived straight from the Manual's own `diagnosis` layer, in zone
order, not retyped, so this deck cannot silently diverge from the
diagnostic engine already shipped on the site's zone pages.

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
RC-014, sentimental attachment, which no Primary Bathroom friction
branches to), confirmed against content/manual/source/content.json before
this file was written, not assumed from any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Primary Bathroom deck to disclose against: no free Primary Bathroom
product exists on the site yet, so this one ships as the first, at its
own URL.

Run:  python ops/cardtext/build_primary_bathroom_deck.py
Out:  ops/cardtext/primary-bathroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "primary-bathroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Primary Bathroom"

# This room ships as a free typeset page, the same stage every prior room
# deck shipped at before any print-on-demand decision existed, so the
# budget here is the honest count of what this room's own corpus,
# diagnosis layer and a proportionate amount of new authorship produce:
# seven real zones, sixteen reachable root causes, two actions per zone
# plus three whole-room ones.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 7, "FRICTION CARD": 21,
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
# one of the seven zones' diagnosis branches (21 frictions x 3 branches)
# was read and its "cause" field copied here verbatim.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011", "KC-012",
             "RC-013", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior room generator uses: every
# numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Vanity Counter": {
  "id": "PBZ-001", "order": 1, "difficulty": 2,
  "tagline": "ONE TRAY. FOUR PRODUCTS. BARE STONE EITHER SIDE.",
  "callouts": [
   "One tray small enough to lift with one hand",
   "Soap and the toothbrush holder inside the tray",
   "No more than four daily products in the tray",
   "Bare stone visible on both sides of the basin",
   "A mirror with no splatter",
   "No cord crossing the sink",
  ],
  "art": ("a bathroom vanity counter holding one small tray light enough "
          "to lift with one hand, containing soap, a toothbrush holder "
          "and no more than four daily products, bare stone visible on "
          "both sides of the basin, a clean mirror with no splatter, and "
          "no cord crossing the sink"),
 },
 "Vanity Drawers": {
  "id": "PBZ-002", "order": 2, "difficulty": 3,
  "tagline": "EVERY DRAWER DIVIDED. THE BLADES CAPPED.",
  "callouts": [
   "Every drawer split into divided compartments",
   "A dated strip on each opened jar's base",
   "Razor blades capped, in a lidded box in one corner",
   "Grooming tools sorted by time of day",
   "The top drawer readable in a single glance",
   "No item overlapping another in the tray",
  ],
  "art": ("an open bathroom vanity drawer divided into compartments, one "
          "dated strip visible on the base of an opened jar, razor "
          "blades capped and stored in a small lidded box in one corner, "
          "grooming tools sorted into groups by time of day, and the top "
          "drawer's contents all visible in a single glance with nothing "
          "overlapping"),
 },
 "Under-Sink Cabinet": {
  "id": "PBZ-003", "order": 3, "difficulty": 3,
  "tagline": "TWO BINS. A BARE TRAY. BOTH VALVES IN SIGHT.",
  "callouts": [
   "Two pull-out bins positioned clear of the P-trap",
   "A pale tray bare on the cabinet floor",
   "Nothing stacked on top of the tray",
   "One open bottle per cleaning job",
   "Both shut-off valves visible when the doors swing open",
   "The P-trap joint fully visible, nothing blocking it",
  ],
  "art": ("an open under-sink bathroom cabinet with two pull-out bins "
          "positioned clear of the visible P-trap, a bare pale tray on "
          "the cabinet floor with nothing stacked on it, one open bottle "
          "for each cleaning job, and both shut-off valves plainly "
          "visible with the doors swung open"),
 },
 "Medicine Cabinet or Wall Storage": {
  "id": "PBZ-004", "order": 4, "difficulty": 3,
  "tagline": "THREE BINS. IN DATE. ABOVE A CHILD'S REACH.",
  "callouts": [
   "Three labeled bins: pain relief, stomach and cold, first aid",
   "Only in-date items inside each bin",
   "Prescriptions grouped together by the name on the label",
   "A first aid bin small enough to carry one-handed",
   "The cabinet mounted above a child's reach",
   "A child safety catch fitted on the cabinet door",
  ],
  "art": ("an open medicine cabinet with three clearly labeled bins "
          "reading pain relief, stomach and cold, and first aid, "
          "prescription bottles grouped together by name, a small first "
          "aid bin sized to carry one-handed, the whole cabinet mounted "
          "above a child's reach, and a visible safety catch fitted to "
          "the door"),
 },
 "Shower or Tub": {
  "id": "PBZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE OF EACH. THE SQUEEGEE ON ITS HOOK.",
  "callouts": [
   "One shampoo, one conditioner, one wash and one bar per person",
   "All of them standing in the caddy",
   "A squeegee hanging on its hook inside the enclosure",
   "Grip strips or a mat with real suction on the floor",
   "No dark line where the wall meets the tray",
   "Clear glass with no soap film",
  ],
  "art": ("a shower enclosure caddy holding exactly one shampoo, one "
          "conditioner, one wash and one bar per person, a squeegee "
          "hanging on its hook inside the enclosure, a grip mat with "
          "real suction visible on the floor, no dark mold line where "
          "the wall meets the tray, and clear glass free of soap film"),
 },
 "Toilet Area": {
  "id": "PBZ-006", "order": 6, "difficulty": 1,
  "tagline": "TWO ROLLS WITHIN REACH. A BARE CISTERN LID.",
  "callouts": [
   "Two reserve toilet rolls within reach from the seat",
   "The rest of the pack stored in the cupboard",
   "The brush standing in an emptied, dried holder",
   "A lined bin with a lid",
   "A completely bare cistern lid",
   "No phone charger cord anywhere near the cistern",
  ],
  "art": ("a toilet area with two reserve rolls set within reach of a "
          "seated position, the rest of the pack visible stored in a "
          "cupboard, a toilet brush standing in an emptied and dried "
          "holder, a lined bin with a lid beside it, a completely bare "
          "cistern lid, and no charging cord anywhere near it"),
 },
 "Linen and Towel Storage": {
  "id": "PBZ-007", "order": 7, "difficulty": 2,
  "tagline": "THREE PER PERSON. EVERY GUEST SET NESTED.",
  "callouts": [
   "Three bath towels per person folded on the shelf",
   "Each guest set nested in its own pillowcase",
   "Hand towels in one labeled column",
   "Washcloths in a separate labeled column",
   "A spare bath mat rolled at the end of the shelf",
   "Shelf brackets visibly secure under the stack",
  ],
  "art": ("a linen shelf holding three folded bath towels per person, "
          "each guest towel set nested inside its own pillowcase, hand "
          "towels standing in one labeled column and washcloths in a "
          "separate labeled column, a spare bath mat rolled at the end "
          "of the shelf, and the shelf brackets visibly secure beneath "
          "the stack"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine already
# shipped on the 114 zone pages. Three per zone, matching that data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Vanity Counter", "PBF-001", "CLEAR MONDAY, COVERED BY WEDNESDAY",
  "a bathroom vanity counter covered edge to edge with loose bottles, "
  "hair tools and a phone charger, barely any bare stone visible around "
  "the basin"),
 ("Vanity Counter", "PBF-002", "WIPED CLEAN, STILL LOOKS DIRTY",
  "a hand wiping a bathroom counter around a cluttered row of bottles, a "
  "hazy line of dried splatter still visible across the mirror above"),
 ("Vanity Counter", "PBF-003", "SOMEBODY ELSE'S THINGS, AGAIN",
  "a shared bathroom vanity counter with two overlapping piles of "
  "personal items pushed together in the middle, no clear boundary "
  "between either side"),

 ("Vanity Drawers", "PBF-004", "DIGGING FOR THE SAME THING AGAIN",
  "a hand digging through a jumbled bathroom drawer of loose grooming "
  "items, searching past several other objects for the one thing "
  "needed"),
 ("Vanity Drawers", "PBF-005", "OPENED, FORGOTTEN, EXPIRED",
  "an open jar of skincare product with a visibly separated, "
  "discoloured surface sitting at the back of a crowded drawer"),
 ("Vanity Drawers", "PBF-006", "TIDY FOR A WEEK, THEN NOT",
  "a bathroom drawer with its dividers pushed out of position and small "
  "items scattered loose across the compartments"),

 ("Under-Sink Cabinet", "PBF-007", "THREE HALF-USED BOTTLES OF THE SAME THING",
  "three half-used bottles of the identical cleaning product standing "
  "side by side inside an open under-sink cabinet"),
 ("Under-Sink Cabinet", "PBF-008", "DAMAGED DOWN HERE, NOBODY NOTICED",
  "a water-stained cardboard box sitting directly on the bare floor of "
  "an under-sink cabinet, its bottom corner visibly soft and "
  "discoloured"),
 ("Under-Sink Cabinet", "PBF-009", "NO WAY TO TELL IF IT'S LEAKING",
  "a crowded under-sink cabinet with bins and boxes stacked directly "
  "over a dark, hidden pipe joint, no pale tray visible beneath it"),

 ("Medicine Cabinet or Wall Storage", "PBF-010",
  "CAN'T FIND IT WHEN IT MATTERS",
  "a hand searching through a jumbled medicine cabinet shelf where "
  "first aid supplies are mixed in among everyday medicine bottles with "
  "no visible bins"),
 ("Medicine Cabinet or Wall Storage", "PBF-011",
  "EXPIRED FOR YEARS, STILL HERE",
  "a medicine cabinet shelf holding a bottle with a faded, years-old "
  "expiry date printed on its label, sitting among current items"),
 ("Medicine Cabinet or Wall Storage", "PBF-012",
  "NOBODY CAN FIND IT WITHOUT ASKING",
  "an unlabeled medicine cabinet shelf crowded with mixed prescription "
  "and everyday medicine bottles, no bins or dividers visible"),

 ("Shower or Tub", "PBF-013", "THE DARK LINE KEEPS COMING BACK",
  "a shower enclosure with a dark mold line visible where the wall tile "
  "meets the tray, several bottles standing directly over that same "
  "strip"),
 ("Shower or Tub", "PBF-014", "CROWDED WITH BOTTLES NOBODY USES",
  "a shower caddy crowded with eight or more bottles of shampoo, wash "
  "and conditioner, several visibly near-empty and unused"),
 ("Shower or Tub", "PBF-015", "CLEANING TAKES FAR TOO LONG",
  "a hand lifting a crowded row of shower bottles off a caddy shelf "
  "before cleaning can even begin, a squeegee nowhere in sight"),

 ("Toilet Area", "PBF-016", "OUT OF PAPER, NOBODY NOTICED",
  "an empty toilet roll holder with no reserve roll anywhere visible "
  "nearby in the toilet area"),
 ("Toilet Area", "PBF-017", "STILL SMELLS, EVEN AFTER CLEANING",
  "a toilet brush sitting wet inside its closed holder beside a bin "
  "with no visible lid"),
 ("Toilet Area", "PBF-018", "THE CISTERN LID, COVERED AGAIN",
  "a cistern lid crowded with a phone, a candle and a drinking glass, "
  "no bare surface visible"),

 ("Linen and Towel Storage", "PBF-019", "OUT OF TOWELS BEFORE LAUNDRY DAY",
  "a nearly bare linen shelf holding only one damp-looking towel, "
  "laundry day still several days away by a calendar visible nearby"),
 ("Linen and Towel Storage", "PBF-020", "FULL SHELF, NO MATCHING SET",
  "a crowded linen shelf with towels of different colours and sizes "
  "stacked loosely together, no guest set visible nested separately"),
 ("Linen and Towel Storage", "PBF-021",
  "PULL ONE TOWEL, DOWN COMES THE STACK",
  "a tall, leaning stack of towels on a high shelf with one towel "
  "half-pulled from the middle, a step stool standing beneath it"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, primary-bathroom-scened art only. The name, meaning,
# six_s and confirm_in_30_seconds text are not reauthored: they are read
# straight from ops/root_causes.py, the one shared vocabulary the deck, the
# app and the articles all already use, so this deck composes with every
# other room deck rather than forking its own copy (DECK-GAME-DESIGN.md
# 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a shower caddy shelf crowded with far more bottles of "
           "shampoo and wash than one household could use before they "
           "expire",
 "KC-002": "a hairdryer cord and a hairbrush lying loose on a bathroom "
           "counter with no drawer or hook anywhere near them",
 "KC-003": "a bottle of toilet bowl cleaner standing on the bathroom "
           "counter instead of anywhere near the toilet itself",
 "KC-004": "a hand reaching past several stacked boxes to a bottle at "
           "the very back of a low cabinet shelf",
 "KC-005": "a row of unlabeled bins on a bathroom shelf with no way to "
           "tell what is inside any of them without opening each one",
 "KC-006": "a high bathroom shelf out of easy reach, a step stool "
           "standing on a wet tile floor beneath it",
 "KC-007": "a single small tray on a bathroom counter with towels and "
           "toiletries spilling over its edge because it is too small "
           "for what sits in it",
 "KC-008": "a bathroom drawer with several different systems of "
           "organization visible at once, one half divided and the "
           "other half loose",
 "KC-009": "a bathroom shelf with no calendar or reminder note nearby, "
           "dust visibly settled across an untouched row of bottles",
 "KC-010": "a razor blade lying loose and exposed in an open bathroom "
           "drawer within a child's reach",
 "KC-011": "an empty spot on a bathroom shelf where a consumable ran "
           "out with no backstock or reminder card visible nearby",
 "KC-012": "two separate, mismatched piles of personal items pushed "
           "together in the middle of one shared bathroom counter",
 "RC-013": "an empty toilet roll holder with nobody visibly responsible "
           "for restocking it, a full spare pack sitting untouched in a "
           "cupboard nearby",
 "RC-015": "a single half-used bottle sitting alone on an otherwise "
           "cleared bathroom shelf corner",
 "RC-016": "a hand reaching into the tight corner of a shower enclosure "
           "where the wall meets the tray, a visible dark line just out "
           "of easy reach",
 "RC-017": "a dried splatter mark on a bathroom mirror that has clearly "
           "gone unwiped through several cleaning passes",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded
# in that zone's own Manual passes, the same contract every prior room
# generator's MICRO_QUESTS already meets (DECK-GAME-DESIGN.md section 2).
# Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Vanity Counter": [
  "Lift the tray off the counter, count what's in it, and put back only "
  "what you touched today.",
  "Run a finger along both sides of the basin and confirm the stone is "
  "bare.",
  "Check nothing is plugged in within cord's reach of the basin, and "
  "coil anything that is.",
 ],
 "Vanity Drawers": [
  "Open the top drawer and read it in one glance: if anything makes you "
  "pause, move it to its own compartment now.",
  "Pull one product and check its open-jar window against today's "
  "date.",
  "Confirm every razor blade is capped or in its lidded box, not loose "
  "among the brushes.",
 ],
 "Under-Sink Cabinet": [
  "Open the cabinet doors and confirm both shut-off valves are visible "
  "without moving anything.",
  "Check the pale tray for any sign of standing water or staining.",
  "Confirm nothing heavier than the tray is stacked on top of it.",
 ],
 "Medicine Cabinet or Wall Storage": [
  "Pull one bin and check every item's date against today.",
  "Confirm the first aid bin can be carried one-handed.",
  "Check the cabinet catch or door still sits above a child's reach.",
 ],
 "Shower or Tub": [
  "Count the bottles in the caddy; if more than one of a kind, decide "
  "which stays.",
  "Confirm the squeegee is on its hook, not lying loose.",
  "Check the grip mat or strips still hold real suction underfoot.",
 ],
 "Toilet Area": [
  "Count the reserve rolls within reach of the seat; refill from the "
  "cupboard if under two.",
  "Empty and dry the brush holder.",
  "Clear anything sitting on the cistern lid, right now.",
 ],
 "Linen and Towel Storage": [
  "Count the bath towels per person on the shelf against the standard.",
  "Check each guest set is nested in its own pillowcase.",
  "Confirm hand towels and washcloths sit in separate columns, not "
  "mixed.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-room actions, the same shape every prior room deck's
# whole-room cards keep: no zone or standard invented for them, only their
# real root causes, this time grounded in the room's own stated three
# problems (standing moisture, open chemistry, dates that pass while you
# sleep) rather than a generic sweep.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "PBA-001", "zone": "Vanity Counter",
  "title": "CLEAR THE COUNTER TO THE DAILY FOUR", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the counter down to bare stone and put back only the "
          "tray with the soap, the toothbrush holder and the four "
          "products you actually touched today.",
  "why": "A counter with no boundary on what belongs is why it fills "
         "back up within two days, and 'I might use it' is not the same "
         "test as 'I used it today.'",
  "inputs": ["a cloth", "nothing else beyond fifteen minutes"],
  "steps": [
   "Take everything off the counter, wipe the bare stone and the "
   "mirror, then put back only the soap, the toothbrush holder and the "
   "four products you touched today.",
   "Coil or unplug any cord that crosses the basin.",
   "Move any glass bottle back off the counter edge to the row against "
   "the mirror.",
   "If this counter is shared, give each person their own tray rather "
   "than one merged pile."],
  "causes": ["KC-001", "KC-010", "KC-012"],
  "victory": "Bare stone on both sides of the basin, and one tray you "
             "can lift with one hand.",
  "next": "PBS-001",
  "art": "a bathroom vanity counter with bare stone on both sides of "
         "the basin, one small tray holding soap, a toothbrush holder "
         "and four daily products, no cord crossing the sink"},

 {"id": "PBA-002", "zone": "Vanity Counter",
  "title": "GIVE THE HEAT TOOL A DRAWER OR A WALL HOOK", "minutes": 30,
  "players": "1", "six_s": "Straighten",
  "goal": "Settle the tool that lives out on the counter by fitting it "
          "a heat-safe pouch in the drawer, or a wall-mounted holder if "
          "the drawer genuinely will not reach.",
  "why": "The straightener sitting out because the outlet is close is "
         "the single biggest reason the counter never stays clear, and "
         "stepping around that decision every day costs more than the "
         "few seconds a drawer costs.",
  "inputs": ["a heat-safe pouch",
             "or a wall-mounted holder if the drawer will not reach"],
  "steps": [
   "Decide honestly whether you use the tool three or four times a "
   "week, which is a drawer tool, or daily, which stays on the counter "
   "as the one item.",
   "If it's a drawer tool, buy or repurpose a heat-safe pouch and give "
   "it a fixed spot in the vanity drawer.",
   "If the drawer genuinely will not reach from where you stand to dry "
   "your hair, fit a wall-mounted holder beside the mirror instead.",
   "Confirm the tool has a rest it returns to every single time, on the "
   "counter or off it."],
  "causes": ["KC-002", "KC-003", "KC-008"],
  "victory": "The heat tool has one fixed home, either a labeled drawer "
             "pouch or a wall-mounted holder, and the counter no longer "
             "needs it to explain why it is not clear.",
  "next": "PBA-001",
  "art": "a heat-safe pouch holding a hair straightener inside an open "
         "bathroom drawer, or a wall-mounted holder beside a mirror, "
         "the counter beneath it bare"},

 {"id": "PBA-003", "zone": "Vanity Drawers",
  "title": "EMPTY THE TOP DRAWER AND CAP THE BLADES", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the top drawer, clear anything past its open-jar "
          "window, and give the blades one capped, lidded home.",
  "why": "A drawer you reach into without looking is the wrong place "
         "for a loose blade, and a jar past its window is a decision "
         "you have already made, just not acted on.",
  "inputs": ["a towel", "a lidded box for blades"],
  "steps": [
   "Empty the top drawer onto a towel, bin anything past its open-jar "
   "window, cap the blades into one lidded box, and put back only what "
   "you reach for daily, each in its own compartment.",
   "Wipe the drawer base before anything goes back in.",
   "Confirm no compartment holds more than one kind of item."],
  "causes": ["KC-005", "KC-010"],
  "victory": "The top drawer can be read in a single look without "
             "moving anything.",
  "next": "PBS-002",
  "art": "an open bathroom vanity drawer divided into compartments, "
         "razor blades capped inside a small lidded box in one corner, "
         "every compartment holding one kind of item, nothing "
         "overlapping"},

 {"id": "PBA-004", "zone": "Vanity Drawers",
  "title": "JUDGE THE EXPENSIVE SHADE BY THE THREE-STRIKE RULE",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Work through every open product against the "
          "reach-for-something-else test, and write the season on "
          "anything unopened you're keeping.",
  "why": "Keeping an expensive product you don't use is not thrift, "
         "it's paying storage on a decision that already went wrong, "
         "and skipping the drawer on every Sort pass only lets it "
         "happen again.",
  "inputs": ["a strip of tape and a marker", "a bin for what leaves"],
  "steps": [
   "Pull every open product in the drawers and ask: did I reach for "
   "something else the last three times instead of this?",
   "If yes and it's past its window, it leaves today, no exceptions for "
   "cost.",
   "If it's unopened and in date, write the season on a strip of tape "
   "stuck to the base so the clock is visible.",
   "Recheck any taped item at the next season's Sort pass and give it a "
   "real verdict then."],
  "causes": ["RC-015", "KC-001"],
  "victory": "Every open product in the drawers has been reached for in "
             "the last three uses, and every kept unopened one carries "
             "a visible season on tape.",
  "next": "PBA-003",
  "art": "a bathroom drawer with a bottle of skincare product carrying "
         "a strip of tape marked with a season, a small bin beside the "
         "drawer holding several discarded, unused products"},

 {"id": "PBA-005", "zone": "Under-Sink Cabinet",
  "title": "CLEAR THE CABINET FLOOR AND SET THE TRAY", "minutes": 15,
  "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Empty the cabinet, dry the floor, and return only two bins "
          "clear of the trap with a bare tray beneath them.",
  "why": "A joint that weeps unnoticed behind a tower of backstock "
         "turns a cheap washer into a rotted cabinet base, and you "
         "cannot catch a leak you cannot see.",
  "inputs": ["a pale tray", "a towel to dry the floor"],
  "steps": [
   "Pull everything out, wipe the cabinet floor dry, put a pale tray "
   "down bare, and return only two bins that clear the P-trap with one "
   "open bottle per job.",
   "Confirm both shut-off valves are visible when the doors swing "
   "open.",
   "Check nothing sits stacked on top of the tray."],
  "causes": ["KC-006", "KC-010"],
  "victory": "Both shut-off valves are in plain sight when the doors "
             "swing open, and nothing is stacked on the tray.",
  "next": "PBS-003",
  "art": "an open under-sink cabinet with a bare pale tray on the "
         "floor, two bins positioned clear of a visible P-trap, and "
         "both shut-off valves plainly visible"},

 {"id": "PBA-006", "zone": "Under-Sink Cabinet",
  "title": "MOVE THE BACKSTOCK OUT, NOT THE SIGHTLINE", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Move any backstock crowding the trap out of this cabinet "
          "entirely, to a linen cupboard or elsewhere, and cap what "
          "stays at two bottles.",
  "why": "If the backstock won't fit without blocking the trap, the "
         "arithmetic says the backstock leaves, not the sightline: a "
         "leak cannot live anywhere else, but spare shampoo can.",
  "inputs": ["boxes for the relocated backstock",
             "space identified in a linen cupboard"],
  "steps": [
   "Pull out everything beyond the two open-bottle bins.",
   "Sort what's left into 'this belongs in the linen cupboard' and "
   "'this is genuinely bathroom-only backstock.'",
   "Move the relocatable backstock out of this cabinet today.",
   "Cap whatever genuinely has to stay at two of any one item, never "
   "stacked on the tray."],
  "causes": ["KC-001", "KC-004"],
  "victory": "The cabinet holds only the two working bins and nothing "
             "else, and the relocated backstock has a real home "
             "elsewhere in the house.",
  "next": "PBA-005",
  "art": "an under-sink cabinet holding only two bins and a bare tray, "
         "a small stack of boxes being carried out through the "
         "bathroom door toward a linen cupboard"},

 {"id": "PBA-007", "zone": "Medicine Cabinet or Wall Storage",
  "title": "SORT INTO THREE LABELED BINS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the cabinet, clear anything expired, and sort what "
          "remains into three labeled bins.",
  "why": "A leftover prescription kept 'in case' is the single most "
         "common thing in here that shouldn't be, and expired pain "
         "relief mixed with first aid costs you time in the one moment "
         "you can't afford to lose any.",
  "inputs": ["three bins", "a marker for labels", "a take-back bag"],
  "steps": [
   "Take everything out, bin anything past its date, and sort what is "
   "left into three labeled bins: pain relief, stomach and cold, first "
   "aid.",
   "Group any prescriptions together by the name on the label.",
   "Confirm the first aid bin is light enough to carry one-handed."],
  "causes": ["KC-005", "RC-015"],
  "victory": "Three labeled bins of in-date items, and a first aid bin "
             "you can carry one-handed.",
  "next": "PBS-004",
  "art": "an open medicine cabinet with three labeled bins reading pain "
         "relief, stomach and cold, and first aid, prescription bottles "
         "grouped together, a small first aid bin light enough to "
         "carry one-handed"},

 {"id": "PBA-008", "zone": "Medicine Cabinet or Wall Storage",
  "title": "CONFIRM THE REACH AND FIT THE CATCH", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Measure the cabinet's real height against what a child can "
          "climb to reach, and fit a catch if children are ever in the "
          "house.",
  "why": "A leftover painkiller behind a mirror is the most likely "
         "thing in this room to seriously hurt a visiting child, and "
         "the reach test only works if you measure from what they can "
         "climb, not the floor.",
  "inputs": ["a catch or child lock if none is fitted",
             "a step stool to test the reach yourself"],
  "steps": [
   "Stand on the closed toilet lid yourself and check what you can "
   "reach: that is a child's real reach in this room, not the "
   "floor-to-shelf distance.",
   "Move anything glass or heavy off any shelf within that reach.",
   "Fit a catch or child lock on the cabinet door if children are ever "
   "in the house.",
   "Confirm the whole cabinet, catch included, is checked working "
   "before you close it."],
  "causes": ["KC-006", "KC-010"],
  "victory": "You have physically tested the child's-eye reach into "
             "this cabinet, and a catch is fitted if children are ever "
             "in the house.",
  "next": "PBA-007",
  "art": "a medicine cabinet mounted above a closed toilet lid, a "
         "visible safety catch fitted to its door, nothing glass or "
         "heavy sitting on the lowest reachable shelf"},

 {"id": "PBA-009", "zone": "Shower or Tub",
  "title": "DOWN TO ONE OF EACH, THEN SQUEEGEE DRY", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the caddy to one shampoo, one conditioner, one wash "
          "and one bar per person, and squeegee the whole enclosure "
          "dry.",
  "why": "Eight bottles sharing one caddy shelf is why it never dries "
         "out and grows a ring, and a squeegee not on its hook is a "
         "squeegee that doesn't get used.",
  "inputs": ["a bag for empties or recycling"],
  "steps": [
   "Take every bottle out, bin the empties, keep one shampoo, one "
   "conditioner, one wash and one bar per person in the caddy, then "
   "squeegee the walls and the tray dry.",
   "Hang the squeegee back on its hook inside the enclosure.",
   "Prop the door or window open to finish drying the space."],
  "causes": ["KC-001", "RC-016"],
  "victory": "Nothing stands on the shower floor, and the squeegee is "
             "back on its hook inside the enclosure.",
  "next": "PBS-005",
  "art": "a shower enclosure caddy holding exactly one shampoo, one "
         "conditioner, one wash and one bar per person, the squeegee "
         "hanging on its hook, the floor and tray completely bare and "
         "dry"},

 {"id": "PBA-010", "zone": "Shower or Tub",
  "title": "USE IT THIS WEEK OR POUR IT OUT", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Test every bottle against the two-week rule, and settle the "
          "inch in the bottom of anything you're keeping out of guilt.",
  "why": "The inch you can't bring yourself to pour away is what keeps "
         "mold on the shelf, and a gift gets no exemption for being a "
         "gift once it stops being used.",
  "inputs": ["nothing beyond thirty minutes", "a recycling bin"],
  "steps": [
   "Line up every bottle in the shower and ask: did I touch this in "
   "the last two weeks of showers?",
   "Anything you didn't touch leaves the enclosure today, gift or not.",
   "For anything you're keeping with an inch left in the bottom, commit "
   "to using it this week or pour it out and recycle the bottle now.",
   "Recheck the caddy count against the one-per-person standard once "
   "the pass is done."],
  "causes": ["RC-015", "KC-001"],
  "victory": "Every bottle remaining in the shower has been used in the "
             "last two weeks, and nothing is being kept purely out of "
             "guilt.",
  "next": "PBA-009",
  "art": "a shower caddy holding only bottles in current daily use, a "
         "small stack of unused bottles set aside near a recycling bin "
         "outside the enclosure"},

 {"id": "PBA-011", "zone": "Toilet Area",
  "title": "CLEAR THE LID AND SET THE RESERVE ROLLS", "minutes": 15,
  "players": "1", "six_s": "Straighten", "from_first_15": True,
  "goal": "Clear the cistern lid completely, dry the brush holder, and "
          "put two reserve rolls within seated reach.",
  "why": "The cistern lid is the most tempting shelf in the room, and "
         "every flush throws a fine mist across whatever is sitting on "
         "it, including your toothbrush if it's still there.",
  "inputs": ["a bin liner", "two spare rolls from the cupboard"],
  "steps": [
   "Clear the cistern lid completely, empty and dry the brush holder, "
   "put a liner and a lid on the bin, and set two reserve rolls within "
   "reach from the seat.",
   "Move anything that touches your face, mouth or food out of the "
   "room entirely.",
   "Confirm the brush holder is genuinely dry before the brush goes "
   "back in."],
  "causes": ["KC-007", "RC-017"],
  "victory": "A completely bare cistern lid, and two reserve rolls "
             "reachable without standing up.",
  "next": "PBS-006",
  "art": "a toilet area with a completely bare cistern lid, a toilet "
         "brush standing in a dry holder, a lined bin with a lid, two "
         "reserve rolls set within reach of a seated position"},

 {"id": "PBA-012", "zone": "Toilet Area",
  "title": "MOVE THE BOWL CLEANER UP AND SET THE RESTOCK TRIGGER",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Move any floor-level bowl cleaner to a high shelf, and fix "
          "the moment the reserve rolls get topped up.",
  "why": "Bowl cleaner at floor level next to the pedestal is one bad "
         "afternoon away from meeting bleach in the same bowl, and a "
         "reserve nobody restocks is a reserve that runs out exactly "
         "when it matters.",
  "inputs": ["a high shelf or cupboard", "nothing else beyond thirty "
             "minutes"],
  "steps": [
   "Move any bowl cleaner off the floor to a shelf stored high, away "
   "from any other bathroom chemical.",
   "Confirm only one product lives near the bowl at a time.",
   "Agree out loud who tops up the two reserve rolls, and when: on "
   "hanging the last roll, two more come from the cupboard on the next "
   "trip past.",
   "Write that trigger somewhere it will actually be seen, like inside "
   "the cupboard door."],
  "causes": ["KC-011", "RC-013"],
  "victory": "The bowl cleaner is stored high, away from other "
             "chemicals, and everyone in the house can say who "
             "restocks the rolls and when.",
  "next": "PBA-011",
  "art": "a bottle of toilet bowl cleaner stored on a high shelf away "
         "from other chemicals, a small note taped inside a cupboard "
         "door naming who restocks the reserve rolls"},

 {"id": "PBA-013", "zone": "Linen and Towel Storage",
  "title": "DOWN TO THREE PER PERSON, NESTED AND LABELED", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take the shelf down to three bath towels per person and "
          "nest every guest set in its own pillowcase.",
  "why": "A shelf running backwards, with the good towels saved and "
         "the worn ones in daily use, has been running backwards for "
         "years, and it only stops the day you rank what's actually "
         "there.",
  "inputs": ["pillowcases for guest sets", "labels for the columns"],
  "steps": [
   "Take the shelf down to three bath towels per person, nest each "
   "guest set in its own pillowcase, and put hand towels and washcloths "
   "into separate labeled columns.",
   "Rank the remaining bath towels and put the best-ranked ones into "
   "daily rotation.",
   "Set aside anything below the cut for rags or donation."],
  "causes": ["KC-005", "KC-007"],
  "victory": "Three bath towels per person on the shelf, and every "
             "guest set in its own pillowcase.",
  "next": "PBS-007",
  "art": "a linen shelf holding exactly three folded bath towels per "
         "person, one guest towel set visibly nested inside its own "
         "pillowcase, hand towels and washcloths in separate labeled "
         "columns"},

 {"id": "PBA-014", "zone": "Linen and Towel Storage",
  "title": "CHECK THE FIXINGS AND MOVE THE WEIGHT DOWN", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Check the shelf brackets can carry the stack, and move the "
          "heaviest towels to a shelf you can reach flat-footed.",
  "why": "An overloaded shelf on light brackets, or a stack tall enough "
         "to topple when you pull from the middle, is a fall risk "
         "hiding behind something as ordinary as folded laundry.",
  "inputs": ["a screwdriver to check the fixings",
             "nothing else beyond thirty minutes"],
  "steps": [
   "Check the shelf brackets are actually fixed to a stud or a proper "
   "anchor, not just drywall.",
   "Move the heaviest bath towels to the lowest shelf you can reach "
   "flat-footed.",
   "Reroll the spare bath mat and set it at the end of the shelf rather "
   "than stacked on top of towels.",
   "Confirm no step stool is needed for the everyday linens."],
  "causes": ["KC-006", "KC-010"],
  "victory": "The shelf fixings are confirmed secure, and every "
             "everyday towel is reachable flat-footed, with nothing "
             "needing a stool.",
  "next": "PBA-013",
  "art": "a linen shelf with its bracket visibly anchored to the wall, "
         "the heaviest bath towels stacked on the lowest reachable "
         "shelf, a spare bath mat rolled neatly at one end"},

 {"id": "PBA-015", "zone": None, "title": "THE STANDING-MOISTURE WALK",
  "minutes": 30, "players": "1", "six_s": "Shine",
  "goal": "Walk every zone in this room in one pass, checking for the "
          "single thing all seven have in common: something left wet "
          "that should be dry.",
  "why": "This room has water in it more hours a day than any other, "
         "and mold does not wait for a dedicated Shine day; it grows in "
         "whichever zone your Shine pass skipped this month.",
  "inputs": ["a squeegee", "a dry cloth",
             "nothing else beyond thirty minutes"],
  "steps": [
   "Squeegee the shower enclosure if it has not already been done "
   "today.",
   "Check the under-sink cabinet's tray and the base of every bottle in "
   "every zone for standing moisture.",
   "Dry the vanity counter around the basin and behind any bottle "
   "rings.",
   "Name, out loud, which zone was wettest: that is the one to squeegee "
   "or dry first next time."],
  "causes": ["RC-016", "KC-009"],
  "victory": "Every zone has been checked for standing moisture in one "
             "pass, and you can name which one collects it fastest.",
  "next": "PBA-016",
  "art": "a person's hand running a squeegee down a shower wall, a dry "
         "cloth wiping a bathroom counter nearby, both in the same room "
         "in one continuous pass"},

 {"id": "PBA-016", "zone": None, "title": "THE OPEN-CHEMISTRY CHECK",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Walk the room checking that no two products stored near "
          "each other could ever mix badly, and that nothing corrosive "
          "sits within a child's reach.",
  "why": "This is the one room in the house where bleach, drain opener "
         "and bowl cleaner all live within a few feet of each other, "
         "and open chemistry does not announce itself until it is "
         "already mixed.",
  "inputs": ["nothing beyond thirty minutes",
             "a high shelf or cupboard for anything relocated"],
  "steps": [
   "Check the under-sink cabinet, the toilet area and the vanity "
   "drawers for any two chemical products stored close enough to be "
   "grabbed by mistake.",
   "Move anything corrosive to a single high shelf, away from anything "
   "it could react with.",
   "Confirm nothing chemical sits within reach of a standing or "
   "climbing child anywhere in the room.",
   "Cap every open bottle fully before closing the cabinet."],
  "causes": ["KC-010", "KC-006"],
  "victory": "You can name, out loud, that no two chemical products in "
             "this room are stored close enough to mix, and nothing "
             "corrosive sits within a child's reach.",
  "next": "PBA-017",
  "art": "cleaning products stored together on one high shelf, well "
         "clear of a child's reach, each bottle capped closed"},

 {"id": "PBA-017", "zone": None, "title": "THE SLEEPING-DATES SWEEP",
  "minutes": 30, "players": "1", "six_s": "Sustain",
  "goal": "Read every expiry date in the room in one sitting, medicine, "
          "drawers and under-sink alike, and settle what has quietly "
          "gone out of date while nobody was checking.",
  "why": "This room holds more expiry dates than any other in the "
         "house, and every one of them passes at 3am with nobody "
         "watching; the only defense is reading them on purpose, on a "
         "schedule, rather than by accident.",
  "inputs": ["a bag for anything expired",
             "a pharmacy take-back bag for medicine"],
  "steps": [
   "Read the date on every open product in the vanity drawers, under "
   "the sink, and in the medicine cabinet in one sitting.",
   "Anything past its date goes in the bag now; medicine goes in the "
   "take-back bag, not the toilet or the trash.",
   "Confirm the medicine cabinet's three bins hold only in-date items.",
   "Set a reminder for the next full sweep, tied to a date you will "
   "actually notice, like a season change."],
  "causes": ["KC-009", "RC-015"],
  "victory": "Every expiry date in the room has been read in one "
             "sitting, and nothing past its date remains in any zone.",
  "next": "PBA-015",
  "art": "a small pile of expired products and a separate pharmacy "
         "take-back bag for medicine sitting on a cleared bathroom "
         "counter, a calendar reminder visible on a nearby phone"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Seven ordinary hard days that test a primary bathroom, one
# per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("PBE-001", "THE BOTH-OF-US-LATE MORNING",
  "Two people need this counter in the same ten minutes before leaving "
  "the house, with no time to clear anything out of each other's way.",
  ["PBZ-001"],
  "Both people find their own daily four products right where they "
  "left them, and the shared tray never has to be searched.",
  "If either of you pushed the other's things aside to make room, the "
  "counter's daily-four standard was not being kept. Draw PBA-001 or "
  "PBA-002.",
  "a bathroom vanity counter with two small daily trays sitting side by "
  "side, each holding its own four products, both clearly separate"),
 ("PBE-002", "THE FIRST DAY BACK AT WORK",
  "You are getting ready for an early meeting and need the drawer to "
  "give up exactly the tool you reach for, on the first try, in the "
  "dark.",
  ["PBZ-002"],
  "The top drawer reads in one glance, and the first pen or tool your "
  "hand meets is the one you wanted.",
  "If you had to dig, or met a capped blade before the tool you "
  "wanted, the drawer's divided standard was not being kept. Draw "
  "PBA-003 or PBA-004.",
  "a hand reaching into an open bathroom drawer and finding one tool "
  "immediately, in a compartment of its own, no searching visible"),
 ("PBE-003", "THE PLUMBER'S FIVE-MINUTE NOTICE",
  "A plumber calls to say they can come right now to look at a slow "
  "drain, and needs the shut-off valve pointed out in under a minute.",
  ["PBZ-003"],
  "The cabinet doors swing open and both shut-off valves are visible "
  "immediately, nothing to move first.",
  "If you had to pull bins and boxes out before the valve was visible, "
  "the under-sink standard was not being kept. Draw PBA-005 or "
  "PBA-006.",
  "an open under-sink cabinet with both shut-off valves immediately "
  "visible, nothing blocking them, a plumber's hand pointing at one"),
 ("PBE-004", "THE MIDDLE-OF-THE-NIGHT FEVER",
  "A household member wakes at 2am with a fever and needs the right "
  "medicine in the dark, fast, without waking anyone else to ask where "
  "it is.",
  ["PBZ-004"],
  "The pain relief bin is found by feel in the dark, and everything in "
  "it is in date.",
  "If the search took light, noise, or more than one bin, the "
  "labeled-bin standard was not being kept. Draw PBA-007 or PBA-008.",
  "a hand reaching into a dark medicine cabinet and finding one clearly "
  "labeled bin immediately by touch, a nightlight glowing faintly "
  "nearby"),
 ("PBE-005", "THE UNEXPECTED HOUSEGUEST'S FIRST SHOWER",
  "A guest arriving unannounced needs to shower within the hour, in an "
  "enclosure they have never seen before, with no explanation of which "
  "bottle is whose.",
  ["PBZ-005"],
  "One shampoo, one conditioner, one wash and one bar per person stand "
  "obviously in the caddy, and the floor is completely bare.",
  "If the guest had to guess which of eight bottles to use, or stepped "
  "around anything on the floor, the shower standard was not being "
  "kept. Draw PBA-009 or PBA-010.",
  "a shower caddy holding one clearly separated set of shampoo, "
  "conditioner, wash and bar per person, the floor completely bare "
  "beneath it"),
 ("PBE-006", "THE STOMACH BUG AT 3AM",
  "Someone is sick in the night and needs this area stocked and bare "
  "with no warning, no shopping trip possible until morning.",
  ["PBZ-006"],
  "Two reserve rolls are within reach from the seat, and the cistern "
  "lid is bare enough to actually be useful.",
  "If the reserve ran out or the lid was too cluttered to set anything "
  "down, the toilet area's own standard was not being kept. Draw "
  "PBA-011 or PBA-012.",
  "a toilet area at night with two reserve rolls visible within seated "
  "reach and a completely bare, usable cistern lid"),
 ("PBE-007", "THE SAME-DAY GUEST ANNOUNCEMENT",
  "A relative texts that they are arriving to stay tonight, and need a "
  "full guest towel set handed to them within the hour.",
  ["PBZ-007"],
  "One guest set, already nested in its own pillowcase, comes off the "
  "shelf in one motion with nothing else needing to be searched.",
  "If you had to hunt through mismatched towels for a full guest set, "
  "the linen standard was not being kept. Draw PBA-013 or PBA-014.",
  "a hand lifting one complete guest towel set nested in its own "
  "pillowcase off a linen shelf, the rest of the shelf undisturbed"),
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
        "related": {"standard": f"PBS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your bathroom, "
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
    standard_id = (f"PBS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"PBS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "PBR-001", "title": "THE PRIMARY BATHROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SEVEN ZONES. START WITH THE COUNTER.",
        "objective": "The primary bathroom is the smallest room you use "
                     "the most, and it carries three problems no other "
                     "room has all at once: standing moisture, open "
                     "chemistry, and dates that quietly pass while you "
                     "sleep. This card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"PBZ-001 Vanity Counter. {start_tip['text']}" if start_tip
            else "PBZ-001 Vanity Counter. Finishing it changes what the "
                 "room looks like from the doorway."),
        "how_to_play": [
            "1. Deal the seven ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your bathroom. Put the rest back.",
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
                   "clears the counter and drawers, another works the "
                   "cabinet and the shower.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do PBA-016 The Open-Chemistry Check before any "
                        "rebuild. It takes thirty minutes and covers what "
                        "makes this room different from every other: "
                        "chemicals, water and electricity, and dates that "
                        "pass while you sleep.",
        "related": {"contents": "PBZ-001 to PBZ-007, PBF-001 to "
                                 "PBF-021, the shared root causes in "
                                 "ops/root_causes.py, PBA-001 to "
                                 "PBA-017, PBS-001 to PBS-007, PBE-001 "
                                 "to PBE-007"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "primary bathroom in its settled state, a "
                           "cleared vanity counter, a shower enclosure, "
                           "a toilet area and a linen shelf all visible "
                           "in one frame, everything put away",
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
    return {"deck": "primary-bathroom", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (build_kitchen_deck.py,
    build_entryway_deck.py, build_laundry_room_deck.py,
    build_home_office_deck.py)."""
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

    assert any(c["id"] == "PBA-016" for c in cards), "no safety walk card"
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


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        primary-bathroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
