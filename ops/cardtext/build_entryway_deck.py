#!/usr/bin/env python3
"""
Build the Entryway deck: 57 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT THE OLD 89 CARD CORPUS
------------------------------------------------
BACKLOG-2026-09-07.md B7/B9: the shipped free deck (`DECK-ENTRY`, 88/89 cards,
`ops/build_deck_gallery.py`, `site/deck.html`) teaches TWELVE Entryway "Micro
Zone" cards. The Manual, the zone pages, the Home Quest and the $19 print
pack all teach FIVE Entryway zones. A household that owns both the free deck
and the paid pack is taught two different zone lists for one room, and that
gap is the reason this file exists rather than a rewrite of the old one:
`ops/build_kitchen_deck.py` proved the pattern (a deck built straight off
`content/manual/source/content.json`, so it cannot drift from the Manual),
and this room is the second one built that way. It does not replace or
retire the old free deck; that is a bigger, separate product decision
(a live SKU, a different visual pipeline, years of photographed art) and not
this file's call to make alone. It ships alongside it, at a different URL,
with the two decks disclosed to each other so nobody mistakes one for the
other.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
15 frictions (symptom and every branch to a root cause) are likewise derived
straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine
that already shipped on the 114 zone pages.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the eight
new action cards (the Manual gives one 15-minute reset per zone in
`first_15`; the 30-minute rebuild and the three whole-entryway actions are
authored here), the event cards, the micro quests, and the room card. The
twelve/thirteen root causes are not reauthored: they are the same frozen
vocabulary in `ops/root_causes.py` that the Kitchen deck already uses, so a
household owning both decks keeps one diagnosis pile rather than two
(DECK-GAME-DESIGN.md 4.3). Thirteen are reachable from this room's real
frictions (`ops/root_causes.py`'s 8 original plus 5 of its "RC-" set), one
more than Kitchen's twelve, because that is what this room's own diagnosis
data actually reaches, not a number chosen in advance.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
`ops/cardtext/build_kitchen_deck.py` keeps.

Run:  python ops/cardtext/build_entryway_deck.py
Out:  ops/cardtext/entryway-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "entryway-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Entryway"

# Not copied from the Kitchen deck's budget. Kitchen fixed 72 first (two
# independent print-economics constraints, DECK-GAME-DESIGN.md 4.1) and cut
# content to fit it. This room ships as a free typeset page, the same stage
# Kitchen shipped at before any print-on-demand decision was made, so the
# budget here is instead the honest count of what this room's own corpus,
# diagnosis layer and a proportionate amount of new authorship produce: five
# real zones, not seven; thirteen reachable root causes, not twelve; two
# actions per zone plus three whole-entryway ones, not eighteen. If this
# room becomes a paid printed product later, the print-tier question is
# real and unresolved, and belongs to that decision, not this one.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 5, "FRICTION CARD": 15,
          "ROOT CAUSE CARD": 13, "ACTION CARD": 13, "STANDARD CARD": 5,
          "EVENT CARD": 5}
TOTAL = sum(BUDGET.values())

# Same palette family as the Kitchen deck so a mixed pile of Entryway and
# Kitchen cards still reads as one product line.
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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-007", "KC-008", "KC-009",
             "KC-010", "KC-011", "RC-013", "RC-014", "RC-015", "RC-016",
             "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule ops/cardtext/build_kitchen_deck.py uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Landing Zone": {
  "id": "EYZ-001", "order": 1, "difficulty": 2,
  "tagline": "ONE VERDICT PER SHEET. NOTHING RETURNS UNDECIDED.",
  "callouts": [
   "One tray holding keys and sunglasses",
   "One wallet and one phone per adult",
   "A single folder standing upright, fewer than ten sheets",
   "Bare surface on both sides of the tray",
   "Charging dock clear of the drip line under the hooks",
   "No loose paper anywhere on the surface",
  ],
  "art": ("a narrow entryway console surface with one shallow tray holding "
          "two sets of keys and a pair of sunglasses, one wallet and one "
          "phone lying beside it, a slim upright folder holding a handful "
          "of papers standing at one end, and bare wood visible on both "
          "sides of the tray"),
 },
 "Coat and Outerwear Zone": {
  "id": "EYZ-002", "order": 2, "difficulty": 3,
  "tagline": "TWO EMPTY HOOKS, ALWAYS. COUNTED BY WEATHER, NOT BY NUMBER.",
  "callouts": [
   "One coat per person on the rail",
   "One bag hanging, not stacked on the floor",
   "Hats and gloves together in one labeled bin",
   "Umbrellas standing upright in the stand",
   "At least two hooks left empty",
   "Nothing weighty stored above head height",
  ],
  "art": ("a coat rail by a front door holding a small number of coats "
          "spaced apart with two hooks visibly empty at one end, a single "
          "bag hanging beside them, a labeled bin on the shelf above "
          "holding hats and gloves, and an umbrella stand with two "
          "umbrellas standing upright beside the rail"),
 },
 "Shoe and Boot Zone": {
  "id": "EYZ-003", "order": 3, "difficulty": 2,
  "tagline": "TWO PAIRS PER PERSON. THE SOLE DECIDES, NOT THE MEMORY.",
  "callouts": [
   "Two pairs per person on the rack, soles down",
   "Boots standing upright in the tray",
   "One pair of slippers per person",
   "A full stride of bare floor between door and rack",
   "Shoe care solvents stored up and out of reach",
   "Nothing loose on the floor beside the rack",
  ],
  "art": ("a shoe rack beside a front door holding pairs of shoes standing "
          "on their soles with visible gaps between pairs, a low boot tray "
          "in front of it holding two pairs of boots standing upright, and "
          "a clear stretch of bare floor between the door and the rack "
          "wide enough for a full stride"),
 },
 "Entry Console or Bench": {
  "id": "EYZ-004", "order": 4, "difficulty": 2,
  "tagline": "THREE ITEMS ON TOP. EMPTY SEAT. EVERY SECTION NAMED.",
  "callouts": [
   "Three items or fewer on the top surface",
   "The seat itself bare, nothing set down on it",
   "Drawer sections each holding one named category",
   "The base of the drawer visible between things",
   "Nothing stored here that is not needed at the door",
   "Bench strapped to the wall if it stands on narrow legs",
  ],
  "art": ("a narrow entry console with a bare wooden seat and exactly "
          "three small items sitting on its top surface, and a shallow "
          "open drawer below divided into sections, each holding one "
          "distinct kind of item with visible space around them"),
 },
 "Door, Mat, and Immediate Floor": {
  "id": "EYZ-005", "order": 5, "difficulty": 1,
  "tagline": "BOTH MATS FLAT. THE SWING STAYS BARE.",
  "callouts": [
   "Coarse mat outside the door, lying flat",
   "Absorbent mat inside the door, lying flat",
   "No curled corners on either mat",
   "Nothing on the floor inside the door's swing",
   "The door latches on the first push",
   "Hinge screws snug, not loose",
  ],
  "art": ("a front door seen from inside with a flat absorbent mat lying "
          "just inside it and a coarser mat visible through the glass "
          "outside, both mats lying flat with no curled corners, and a "
          "completely bare stretch of floor in the arc where the door "
          "swings open"),
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
 ("Landing Zone", "EYF-001", "THE FOLDER NEVER STAYS UNDER TEN",
  "a slim upright folder overflowing with loose papers on an entryway "
  "console, sheets fanned out well past its top edge"),
 ("Landing Zone", "EYF-002", "IT LANDS BESIDE THE TRAY, NOT IN IT",
  "an entryway console surface with a set of keys, a phone charger and a "
  "pair of sunglasses scattered beside an empty tray rather than inside "
  "it"),
 ("Landing Zone", "EYF-003", "THE DOCK SITS UNDER THE DRIP LINE",
  "a phone charging dock plugged in directly beneath a row of coat hooks "
  "holding a dripping wet umbrella, a damp patch visible on the console "
  "beneath it"),

 ("Coat and Outerwear Zone", "EYF-004", "THE RAIL IS FULL AND NO HOOK IS EMPTY",
  "a coat rail packed edge to edge with coats touching each other, every "
  "hook occupied, no gap visible anywhere along it"),
 ("Coat and Outerwear Zone", "EYF-005", "THE EXPENSIVE COAT NEVER GETS WORN",
  "a single tailored coat with the price tag still attached hanging "
  "untouched at the end of a rail among visibly worn everyday coats"),
 ("Coat and Outerwear Zone", "EYF-006", "THE COLD SNAP LAYER NEVER COMES OFF",
  "a coat rail crowded with heavy winter layers still hanging in what "
  "looks like mild weather light, coats pressed shoulder to shoulder"),

 ("Shoe and Boot Zone", "EYF-007", "A PAIR IS ALWAYS LOOSE ON THE FLOOR",
  "a shoe rack with visibly full shelves and a single pair of shoes "
  "lying separately on the floor in front of it rather than on a shelf"),
 ("Shoe and Boot Zone", "EYF-008", "THE SMOOTH-TREAD PAIR NEVER LEAVES",
  "a single worn shoe held sole-up, its tread rubbed completely smooth "
  "and flat, resting on top of a shoe rack among other pairs"),
 ("Shoe and Boot Zone", "EYF-009", "THE BOOT TRAY IS ALWAYS WET AND GRITTY",
  "a low boot tray holding a shallow pool of gritty water with visible "
  "sand and salt residue, sitting directly on a hallway floor with faint "
  "scratch marks around its edge"),

 ("Entry Console or Bench", "EYF-010", "THE DRAWER REFILLS WITHIN A MONTH",
  "an entryway drawer pulled open and crowded edge to edge with loose "
  "small objects of many different kinds, no visible dividers"),
 ("Entry Console or Bench", "EYF-011", "THE TOP HOLDS MORE THAN THREE AGAIN",
  "an entry console top crowded with more than half a dozen small items "
  "of different kinds pushed together with no clear surface visible"),
 ("Entry Console or Bench", "EYF-012", "SMALL THINGS ROLL INTO THE BACK CORNERS",
  "an open entryway drawer with loose batteries and coins scattered and "
  "gathered into its back corners, no container holding them"),

 ("Door, Mat, and Immediate Floor", "EYF-013", "GRIT GETS PAST THE MAT ANYWAY",
  "a doormat lying just inside a front door with a faint trail of gritty "
  "footprints continuing past it onto the hallway floor beyond"),
 ("Door, Mat, and Immediate Floor", "EYF-014", "SOMETHING IS STORED IN THE DOOR'S SWING",
  "a front door only partly open because a stack of boxes sits on the "
  "floor directly in the arc where it swings"),
 ("Door, Mat, and Immediate Floor", "EYF-015", "THE MAT CURLS OR THE DOOR WON'T LATCH",
  "a doormat with one corner curled sharply upward beside a front door "
  "standing very slightly ajar where the latch has not caught"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, entryway-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight from
# ops/root_causes.py, the one shared vocabulary the deck, the app and the
# articles all already use, so this deck composes with the Kitchen deck
# rather than forking its own copy (DECK-GAME-DESIGN.md 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a shoe rack shelf holding four nearly identical black shoes "
           "side by side with no others in sight",
 "KC-002": "an entryway console with a phone charger, a dog lead and a "
           "single loose sock lying on it, none of them near any drawer "
           "or hook",
 "KC-003": "a winter coat hanging on a hook in a hallway far from the "
           "front door, the door itself visible in the far background",
 "KC-007": "a coat hook holding two coats stacked on the same peg, the "
           "second one's sleeve trailing down to the floor",
 "KC-008": "an entry console surface at dusk, half of it bare and half "
           "of it still holding the day's shoes, bags and mail",
 "KC-009": "a front hallway at night lit only by a porch light through "
           "the glass, a coat still lying over the end of the rail where "
           "it was dropped that morning",
 "KC-010": "a narrow entry console with an open drawer of loose "
           "batteries and coins at exactly a toddler's reaching height",
 "KC-011": "an empty shoe polish tin standing on an otherwise bare "
           "entry console shelf beside a pair of dull leather shoes",
 "RC-013": "a front hallway floor with a pair of shoes, a school bag "
           "and a dog lead all left in the same spot, nobody's coat "
           "hook nearby claimed",
 "RC-014": "a single tailored coat with its price tag still attached "
           "hanging untouched at the end of an otherwise ordinary coat "
           "rail",
 "RC-015": "a slim folder standing upright on an entry console holding "
           "a handful of envelopes, one opened envelope with a form "
           "half pulled out",
 "RC-016": "the corner of a boot tray pushed hard against a wall, a "
           "build-up of dried grit visible in the angle where it meets "
           "the skirting board",
 "RC-017": "a coat rail with one coat hanging crookedly off a bent "
           "hook, everything around it otherwise orderly",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes, the same contract
# ops/cardtext/build_kitchen_deck.py's MICRO_QUESTS already meets
# (DECK-GAME-DESIGN.md section 2). Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Landing Zone": [
  "Lift the tray, wipe the ring of dust underneath it, and set it back "
  "exactly where your hand opens on the way in.",
  "Pull one sheet from the folder, give it its verdict right now, and "
  "write today's date on whatever goes back in.",
  "Move the charging dock two inches clear of the drip line under the "
  "hooks and coil its cable flat.",
 ],
 "Coat and Outerwear Zone": [
  "Count the coats on the rail, and if both hooks nearest the door are "
  "full, carry one coat to a bedroom closet right now.",
  "Straighten every coat hanger so shoulders sit square and no sleeve "
  "trails onto the floor.",
  "Check the shelf above the rail for anything heavier than a hat, and "
  "move it down to a low shelf.",
 ],
 "Shoe and Boot Zone": [
  "Turn every pair on the rack sole-down and stand any pair lying on "
  "its side back upright.",
  "Carry the boot tray outside, tip it out, and set it back down dry.",
  "Pull one pair that is not on anyone's feet this season off the rack "
  "and carry it to its real home.",
 ],
 "Entry Console or Bench": [
  "Count what is on the top right now, and carry anything past three "
  "items straight to where it actually belongs.",
  "Open the drawer and return one item that has drifted into the wrong "
  "named section.",
  "Wipe the seat completely bare, even if you are about to sit "
  "something on it for thirty seconds.",
 ],
 "Door, Mat, and Immediate Floor": [
  "Press both mats flat with your foot, corner by corner, checking for "
  "any edge starting to curl.",
  "Look at the floor inside the door's swing and carry off anything at "
  "all that has been set there.",
  "Push the door shut and pull the handle once to confirm the latch "
  "caught on the first try.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-entryway actions, the same shape as Kitchen's four
# whole-kitchen cards (KA-015 to KA-018): no zone or standard invented for
# them, only their real root causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "EYA-001", "zone": "Landing Zone", "title": "CLEAR THE TRAY AND THE FOLDER",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the tray and the paper stack, give every sheet a "
          "verdict, and put back only what belongs.",
  "why": "Paper with no verdict is the reason this surface fills back up "
         "faster than any other reset in the house.",
  "inputs": ["a bin bag", "the recycling bin", "a pen"],
  "steps": [
   "Empty the tray and the paper stack onto the surface, then give every "
   "sheet a verdict: act, file, or recycle, before anything goes back.",
   "Anything that needs action stands upright in the folder with the "
   "date written in the corner.",
   "Recycle what nobody is going to act on, honestly, rather than "
   "restack it.",
   "Return only the tray, holding keys and sunglasses, and the folder, "
   "to the bare surface."],
  "causes": ["RC-015", "KC-008"],
  "victory": "One tray holds only keys and sunglasses, and no loose "
             "paper sits anywhere on the surface.",
  "next": "EYS-001",
  "art": "an entryway console with one tray holding keys and sunglasses "
         "and a slim folder standing beside it, the rest of the surface "
         "completely bare"},

 {"id": "EYA-002", "zone": "Landing Zone", "title": "REBUILD THE LANDING SURFACE",
  "minutes": 30, "players": "1 to 2", "six_s": "Straighten",
  "goal": "Change the surface so a verdict happens in the moment, not "
          "the pile.",
  "why": "A pocket-emptying spot with no charging dock and no folder "
         "invites paper and cables to just sit there.",
  "inputs": ["a shallow tray", "a slim upright folder", "a pen",
             "a cable tie or clip"],
  "steps": [
   "Stand where your hands actually stop when you walk in, and put the "
   "tray there, not wherever it currently sits.",
   "Move the charging dock clear of the drip line under any hooks, onto "
   "the outlet nearest the tray.",
   "Set the folder upright at one end of the tray, and write today's "
   "date on a card inside it as the first entry.",
   "Coil and clip any charging cable so it lies flat rather than "
   "trailing across the surface.",
   "Count what has landed here in the past week that is not keys, "
   "sunglasses, a wallet, a phone, or paper, and give each item a home "
   "somewhere else in the house."],
  "causes": ["KC-003", "KC-002"],
  "victory": "The tray sits exactly where your hand opens on the way "
             "in, the dock is clear of the drip line, and everything on "
             "the surface is one of the five named things.",
  "next": "EYA-001",
  "art": "an entryway console with a shallow tray positioned right at "
         "hand height by the door, a charging dock plugged into an "
         "outlet well clear of the hooks above, its cable coiled flat"},

 {"id": "EYA-003", "zone": "Coat and Outerwear Zone", "title": "CLEAR TWO HOOKS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the two hooks nearest the door and confirm every coat "
          "still on the rail earns its place this season.",
  "why": "Two hooks that are never empty are the first sign the rail is "
         "carrying coats by number instead of by weather.",
  "inputs": ["a bin bag or box for coats leaving the room"],
  "steps": [
   "Take down every coat that did not go outside once this cold season, "
   "and clear the two hooks nearest the door.",
   "Carry each coat you took down to a bedroom closet or the giveaway "
   "pile, not to the floor.",
   "Space the coats that remain so shoulders do not touch."],
  "causes": ["KC-001", "KC-008"],
  "victory": "Two hooks stand empty nearest the door, and every coat "
             "still on the rail was worn this season.",
  "next": "EYS-002",
  "art": "a coat rail with two hooks nearest the door standing "
         "completely empty and the remaining coats spaced apart along "
         "the rest of the rail"},

 {"id": "EYA-004", "zone": "Coat and Outerwear Zone", "title": "REBUILD THE COAT RAIL",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Count coats by weather instead of by number, and fix what "
          "the rail can actually hold.",
  "why": "A rail loaded past its bracket weight sags and lets go, "
         "usually while somebody stands directly beneath it.",
  "inputs": ["a bin bag for the giveaway pile", "a step stool"],
  "steps": [
   "Take every coat off the rail and lay them out where you can see all "
   "of them at once.",
   "Sort into the weather categories your climate actually produces: "
   "wet, cold, and something in between.",
   "Keep one per person per category. A second coat in the same "
   "category has to name a specific day it beats the first, or it goes.",
   "Hang the kept coats back with a visible gap between each, heaviest "
   "nearest the door.",
   "Move anything heavy or bulky off the shelf above head height down "
   "to a low shelf instead."],
  "causes": ["KC-007", "RC-014"],
  "victory": "At least two hooks stand empty at all times, and nothing "
             "heavy sits above head height on the shelf.",
  "next": "EYA-003",
  "art": "a coat rail with a clear gap of bare space between each "
         "hanging coat, a shelf above holding only a labeled bin and "
         "light hats, nothing heavy visible on it"},

 {"id": "EYA-005", "zone": "Shoe and Boot Zone", "title": "PAIR UP AND CUT TO TWO",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pair every shoe up, and keep only two pairs per person on "
          "the rack.",
  "why": "A pair on the floor instead of the rack is usually a pair the "
         "rack was never told it needed to hold.",
  "inputs": ["nothing beyond fifteen minutes and floor space to sort on"],
  "steps": [
   "Pull every shoe off the rack, pair them up on the floor, and put "
   "back only two pairs per person, soles down.",
   "Set aside anything past two pairs per person for the giveaway pile "
   "or another room's closet.",
   "Stand the boot tray's pairs upright rather than laid on their "
   "sides."],
  "causes": ["KC-007", "RC-013"],
  "victory": "Two pairs per person stand on the rack, soles down, and "
             "the floor between the door and the rack is bare.",
  "next": "EYS-003",
  "art": "a shoe rack holding exactly two pairs of shoes per person, "
         "each standing sole-down with visible space between pairs, and "
         "a bare stretch of floor in front of it"},

 {"id": "EYA-006", "zone": "Shoe and Boot Zone", "title": "REBUILD THE SHOE RACK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Move shoe care solvents out of toddler reach and fix the "
          "rack so it cannot tip.",
  "why": "Polish and waterproofing spray sitting in an open basket at "
         "toddler height are a poisoning risk, and a top-heavy rack a "
         "child climbs is a fall risk.",
  "inputs": ["a shelf or high hook out of small hands' reach",
             "wall anchors if the rack is tall and narrow"],
  "steps": [
   "Take every polish, cleaner and waterproofing spray off the rack and "
   "move them to a shelf above reach or out of the room.",
   "Turn every shoe sole-down; nothing stands on its toe.",
   "Move the heaviest pairs to the bottom shelf and the lightest to the "
   "top.",
   "If the rack is tall and narrow, fix it to the wall so a climbing "
   "child cannot pull it forward.",
   "Clear the floor between the door and the rack down to bare boards, "
   "a full stride wide."],
  "causes": ["KC-010", "RC-016"],
  "victory": "Shoe care solvents sit out of a toddler's reach, the rack "
             "cannot tip, and the floor between door and rack is bare.",
  "next": "EYA-005",
  "art": "a shoe rack fixed flush against a wall with a bare stretch of "
         "floor in front of it, a shelf well above head height holding "
         "shoe polish and cleaning bottles, out of a small child's reach"},

 {"id": "EYA-007", "zone": "Entry Console or Bench",
  "title": "EMPTY THE DRAWER, KEEP THE DOOR TEST", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the drawer and keep only what you would want while "
          "wearing your outdoor shoes.",
  "why": "This drawer becomes the second junk drawer within a month of "
         "being emptied, every time, unless something is actually taken "
         "out rather than just tidied.",
  "inputs": ["a bin bag", "a box for things that belong in another room"],
  "steps": [
   "Tip the drawer out onto the bench and take out anything you would "
   "not want while wearing your outdoor shoes.",
   "Give each removed item a real home elsewhere in the house, or let "
   "it go.",
   "Wipe the seat and the top completely bare before putting the kept "
   "items back."],
  "causes": ["KC-002", "RC-015"],
  "victory": "Three items or fewer sit on the top, the seat is empty, "
             "and every drawer section holds one named category.",
  "next": "EYS-004",
  "art": "an entry console with a mostly empty drawer holding a small "
         "handful of items and a bare seat and top surface above it"},

 {"id": "EYA-008", "zone": "Entry Console or Bench",
  "title": "NAME THE DRAWER'S SECTIONS", "minutes": 30, "players": "1",
  "six_s": "Standardize",
  "goal": "Give every divided section of the drawer one named category "
          "so nothing new can drift in unchallenged.",
  "why": "A drawer with no named sections becomes the second junk "
         "drawer within a month, every time, because nothing tells the "
         "next loose item it does not belong.",
  "inputs": ["small dividers or boxes that fit the drawer",
             "a marker or labels", "a lidded tin for batteries and coins"],
  "steps": [
   "Take everything out of the drawer and group what earned its spot "
   "into like piles.",
   "Fit a divider or small box for each pile, sized to the drawer.",
   "Write one category name for each section, in your own words, and "
   "stick or write it where you will see it.",
   "Put loose batteries, coins and small magnets into a lidded tin, not "
   "loose in a corner.",
   "Wipe the seat and the top completely bare before putting the three "
   "kept items back."],
  "causes": ["KC-002", "KC-008"],
  "victory": "Every drawer section carries a name, batteries and coins "
             "sit inside a lidded tin, and the seat is completely bare.",
  "next": "EYA-007",
  "art": "an open entry console drawer divided into labeled sections "
         "each holding one kind of small item, a lidded tin standing in "
         "one section holding batteries and coins"},

 {"id": "EYA-009", "zone": "Door, Mat, and Immediate Floor",
  "title": "CLEAR THE SWING AND CHECK THE MATS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Vacuum under both mats and clear anything stored inside the "
          "door's swing.",
  "why": "A flattened mat and something stored in the door's own swing "
         "are the two everyday ways this zone quietly stops doing its "
         "job.",
  "inputs": ["a vacuum"],
  "steps": [
   "Lift both mats, vacuum the floor underneath, and check both faces "
   "of the inside mat for a flattened line where grit is riding across "
   "instead of catching.",
   "Set both mats back down flat, corners uncurled.",
   "Carry off anything at all sitting on the floor inside the door's "
   "swing."],
  "causes": ["KC-011", "RC-016"],
  "victory": "Both mats lie flat with no curled corners, and the floor "
             "inside the door's swing is bare.",
  "next": "EYS-005",
  "art": "a front hallway with two mats vacuumed and lying flat and a "
         "completely bare stretch of floor in the door's swing"},

 {"id": "EYA-010", "zone": "Door, Mat, and Immediate Floor",
  "title": "FIX THE DOOR AND TAPE THE OUTLINE", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Tighten what makes the door and mats fail, and mark where "
          "each mat belongs so it stops drifting.",
  "why": "A loose hinge screw catches fingers, and a curled mat edge "
         "catches toes; both are cheap to fix and expensive to ignore.",
  "inputs": ["a screwdriver", "low tack tape",
             "a stiff brush or hose for the outdoor mat"],
  "steps": [
   "Tighten every visible hinge screw on the door while you are down at "
   "floor level.",
   "Check the latch catches on the first push; adjust the strike plate "
   "if it does not.",
   "Mark each mat's position on the floor with low tack tape so it "
   "always goes back the same way.",
   "Brush or hose the outdoor mat clean and let it dry fully before it "
   "goes back down.",
   "Confirm nothing at all sits on the floor inside the door's full "
   "swing."],
  "causes": ["RC-017", "KC-011"],
  "victory": "The door latches on the first push, both mats sit flat "
             "inside their taped outline, and the swing is completely "
             "bare.",
  "next": "EYA-009",
  "art": "a front door with a faint strip of tape on the floor marking "
         "a mat's outline just inside it, the mat sitting flat inside "
         "the taped line"},

 {"id": "EYA-011", "zone": None, "title": "THE SEASONAL SWAP",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Move the outgoing season's coats, mats and gear out and the "
          "incoming season's in, on the day the weather actually turns.",
  "why": "Nothing marks the day the seasonal swap should happen, so it "
         "happens weeks late, wedged around what is already there.",
  "inputs": ["a storage bin or bag for the outgoing season's gear",
             "space in another room's closet"],
  "steps": [
   "On the first morning cold enough that you go looking for gloves, or "
   "warm enough that a coat feels wrong, do the swap standing there.",
   "Take down every coat, pair of boots and accessory for the season "
   "that is ending.",
   "Box or bag them and move them to storage in another room, not a "
   "shelf in this one.",
   "Bring the incoming season's coats and shoes in and hang or rack "
   "them in the cleared space.",
   "Swap the coarse outdoor mat for whichever grips better in the "
   "coming weather, if your entryway keeps two."],
  "causes": ["KC-009", "KC-003"],
  "victory": "Every coat and pair of shoes on display belongs to the "
             "current season, and last season's gear is stored "
             "elsewhere in the house.",
  "next": "EYA-004",
  "art": "a storage bin half packed with out-of-season coats sitting "
         "beside a coat rail that now holds only the current season's "
         "coats, spaced apart"},

 {"id": "EYA-012", "zone": None, "title": "THE FOURTEEN DAY PAPER RULE",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Clear the folder down to nothing older than fourteen days, "
          "and act on or recycle every sheet past that line.",
  "why": "Paper in the folder without a deadline becomes furniture; the "
         "fourteen day line is what turns it back into a decision.",
  "inputs": ["a pen", "the recycling bin",
             "your phone, to pay or call while you are standing there"],
  "steps": [
   "Take the folder off the landing surface and go through it sheet by "
   "sheet.",
   "Check the date written in the corner of each one against today.",
   "Anything past fourteen days gets done right now, standing there: "
   "paid, signed, called, or recycled.",
   "Write today's date on anything new that goes back in.",
   "Put the folder back with nothing in it older than fourteen days."],
  "causes": ["RC-015", "KC-009"],
  "victory": "No sheet in the folder is older than fourteen days, and "
             "the ones that were have all been acted on or recycled.",
  "next": "EYA-001",
  "art": "a slim folder held open on an entryway console showing a "
         "handful of papers, a pen resting across the top sheet"},

 {"id": "EYA-013", "zone": None, "title": "THE FULL REBUILD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk the whole entryway once, standing where you use it, "
          "and confirm nothing weighty, sharp, or wet is somewhere it "
          "could hurt someone.",
  "why": "The four things that hurt people in this room are height, "
         "weight, water and a door swing, and none of them show up "
         "unless you look on purpose.",
  "inputs": ["nothing beyond thirty minutes and a working set of hands"],
  "steps": [
   "Stand at the console and check nothing heavy is stored above head "
   "height that could come down on someone reaching for a coat.",
   "Check the charging dock and any lamp are clear of where a wet "
   "umbrella or coat would drip on them.",
   "Check the shoe rack for anything that could tip, and confirm "
   "solvents sit out of a small child's reach.",
   "Check both mats lie flat with no curled corner and the door "
   "latches on the first push.",
   "Fix anything you find right there, or write it on the folder's top "
   "sheet with today's date if it needs a tool you do not have to "
   "hand."],
  "causes": ["KC-010", "RC-016"],
  "victory": "You can name, out loud, that height, drip, tip and trip "
             "have each been checked today.",
  "next": "EYA-010",
  "art": "a wide view of a whole entryway with a hand pointing at a "
         "coat hook, a shoe rack and a floor mat in turn, everything in "
         "its settled, put-away state"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test an entryway.
# ---------------------------------------------------------------------------

EVENTS = [
 ("EYE-001", "THE SCHOOL MORNING RUSH",
  "Everyone needs shoes, a coat and a bag in the same four minutes, and "
  "someone is already late.",
  ["EYZ-003", "EYZ-002"],
  "Every pair of shoes and every coat is found without anyone asking "
  "where it is.",
  "If a shoe or a coat had to be hunted for, that item was not in its "
  "assigned spot. Draw EYA-006 or EYA-004.",
  "a front hallway with two pairs of small shoes and one adult pair "
  "being stepped into quickly beside an open door, a school bag already "
  "on a hook, morning light through the glass"),
 ("EYE-002", "THE WET DOG WALK RETURN",
  "A soaked dog, muddy leads and two pairs of wet boots come through "
  "the door at once.",
  ["EYZ-005", "EYZ-003"],
  "The mats catch the worst of it, and the boot tray takes the boots "
  "without a scramble for space.",
  "If mud reached the hallway floor past the mats, the mats have "
  "finished, or the swing was not clear. Draw EYA-010.",
  "a front doormat holding two pairs of muddy wet boots set down on it, "
  "a damp dog lead hanging on a hook beside the door, water beading on "
  "the mat's surface"),
 ("EYE-003", "THE MOVING BOX DROP",
  "A delivery of three flattened cardboard boxes and a parcel lands "
  "just inside the door and stays there.",
  ["EYZ-005", "EYZ-004"],
  "Nothing from the delivery is still on the floor inside the door's "
  "swing by that evening.",
  "If it is still there the next morning, the console drawer or "
  "another room's real home for it was never named. Draw EYA-008.",
  "a cardboard parcel and a stack of flattened boxes sitting just "
  "inside a front door, partly blocking the door's swing"),
 ("EYE-004", "GUESTS ARRIVE WITH THEIR OWN COATS",
  "Four extra coats and four extra pairs of shoes need somewhere to go "
  "for the evening, with no warning.",
  ["EYZ-002", "EYZ-003"],
  "A guest's coat finds an empty hook without anyone rearranging the "
  "rail first, and their shoes have a clear stretch of floor to stand "
  "on.",
  "If a hook had to be freed up on the spot, the two-empty-hooks "
  "standard was not being kept. Draw EYA-004.",
  "a coat rail with two coats added among the household's own, both "
  "hanging on hooks with space still visible on either side"),
 ("EYE-005", "THE FIRST FROST",
  "The temperature drops overnight and every glove, hat and scarf in "
  "the house is needed the same cold morning.",
  ["EYZ-002", "EYZ-001"],
  "Hats and gloves come out of the one labeled bin, together, and "
  "nobody is searching pockets or the car for a missing glove.",
  "If gloves turned up in three different places, the seasonal swap "
  "has not happened yet. Draw EYA-011.",
  "a labeled storage bin on a shelf above a coat rail, its lid off, "
  "hats and pairs of gloves visible inside sorted together"),
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
        "related": {"standard": f"EYS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your entryway, "
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
    frictions = [f[1] for f in FRICTION_META]  # filled precisely in build()
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
    standard_id = (f"EYS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"EYS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "EYR-001", "title": "THE ENTRYWAY", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "FIVE ZONES. START AT THE DOOR.",
        "objective": "The entryway is five small places, not one big "
                     "job. This card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"EYZ-005 Door, Mat, and Immediate Floor. "
            f"{start_tip['text']}" if start_tip else
            "EYZ-005 Door, Mat, and Immediate Floor. It is the shortest "
            "zone in the room."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your entryway. Put the rest back.",
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
        "safety_first": "Do EYA-013 The Full Rebuild Walk before any "
                        "rebuild. It takes thirty minutes and covers "
                        "every hook, shelf and door in the room.",
        "related": {"contents": "EYZ-001 to EYZ-005, EYF-001 to EYF-015, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, EYA-001 to EYA-013, "
                                 "EYS-001 to EYS-005, EYE-001 to EYE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "entryway in its settled state, front door, "
                           "coat rail, shoe rack, console and floor mats "
                           "all visible in one frame, everything put "
                           "away",
                "must_show": ["all five zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the five zones is. If two are "
                               "not in frame, reshoot."},
    }


def build() -> dict:
    zmap = manual_zones()
    missing = [z for z in ZONES if z not in zmap]
    if missing:
        raise SystemExit(
            f"these zones are not in the Manual and would be invented: "
            f"{missing}. The deck's zone list must be the Manual's zone "
            f"list, which is exactly what the old free Entryway deck got "
            f"wrong.")

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
    # exist, the same two-pass shape ops/cardtext/build_kitchen_deck.py uses.
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
    return {"deck": "entryway", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_kitchen_deck.py)."""
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

    # The two zone-linked 15-minute actions per zone must quote the Manual's
    # own first_15 action and victory condition, not paraphrase them: this
    # is the exact "derived, not invented" contract the room's own ZONE and
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

    assert any(c["id"] == "EYA-013" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This deck's whole reason for existing: the zone list must be exactly
    # the Manual's five, in the Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 5, (
        "this deck's whole reason for existing is that the Manual has "
        "five Entryway zones, not twelve; that count moved")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        entryway ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
