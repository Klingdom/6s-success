#!/usr/bin/env python3
"""
Build the Hall Closet deck: 58 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: eight rooms already carry a full diagnosis layer
and a shipped deck (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home
Office, Garage, Stair Landing, Pantry). Hall Closet is the next room built
the same way: rich, hand-authored Manual content for all five zones
(purpose, done_looks_like, passes, the_call, watch_for, leave_behind,
shine_detail), but no diagnosis layer and no deck until this file. It adds
that layer to content/manual/source/content.json (fifteen frictions,
forty-five branches, five first_15 actions) and builds the deck straight
off it, the same shape ops/cardtext/build_pantry_deck.py already uses for
its own five-zone room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
fifteen frictions (symptom and every branch to a root cause) are likewise
derived straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the ten
zone-linked action cards, the three whole-closet actions, the event cards,
the micro quests, and the room card. The root causes are not reauthored:
they are the same frozen vocabulary in ops/root_causes.py that every other
room's deck already uses, so a household owning more than one deck keeps one
diagnosis pile rather than several (DECK-GAME-DESIGN.md 4.3). Fourteen of
the seventeen shared ids are reachable from this room's real frictions,
counted honestly from the branches actually written below, not chosen first
and filled in: KC-001, KC-002, KC-003, KC-004, KC-005, KC-006, KC-008,
KC-009, KC-010, RC-013, RC-014, RC-015, RC-016, RC-017. KC-007, KC-011 and
KC-012 are not reachable because nothing in this room's real diagnosis
branches to them, and that is a true statement about this room's own
frictions, not an oversight; nothing pads the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Hall Closet ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). The budget
below is the same shape as Entryway and Pantry, the other five-zone rooms in
this line: five real zones, fifteen frictions (three per zone), fourteen
reachable root causes, thirteen action cards (two per zone plus three
whole-closet), five standard cards and five event cards. 58 cards in total,
not padded or trimmed to match any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_hall_closet_deck.py
Out:  ops/cardtext/hall-closet-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "hall-closet-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Hall Closet"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 5, "FRICTION CARD": 15,
          "ROOT CAUSE CARD": 14, "ACTION CARD": 13, "STANDARD CARD": 5,
          "EVENT CARD": 5}
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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-008", "KC-009", "KC-010", "RC-013", "RC-014", "RC-015",
             "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Linen Shelf Zone": {
  "id": "HCZ-001", "order": 1, "difficulty": 2,
  "tagline": "THREE SETS PER BED. ONE PILLOWCASE EACH. THE COUNT ON THE SHELF.",
  "callouts": [
   "Three sheet sets per bed, each bundled inside its own pillowcase",
   "The bed size and count written on the shelf edge underneath",
   "Everyday towels folded to one width in a stack no taller than a forearm",
   "Two spare blankets on the top shelf with nothing balanced on them",
   "Queen and king sets stored low, guest blankets on top",
   "No loose, unmatched sheet lying outside a bundle",
  ],
  "art": ("a hallway closet shelf holding pillowcase-bundled sheet sets "
          "grouped by bed size with a small dated count card on the "
          "shelf edge, a stack of folded towels no taller than a "
          "forearm beside them, and two spare blankets on the top "
          "shelf"),
 },
 "Cleaning Equipment Zone": {
  "id": "HCZ-002", "order": 2, "difficulty": 2,
  "tagline": "EVERY HANDLE ON THE RAIL. THE VACUUM INSIDE ITS OUTLINE.",
  "callouts": [
   "Broom, mop and duster hanging handle-down from wall clips",
   "Every head hanging clear of the closet floor",
   "The vacuum parked inside a taped floor outline",
   "Crevice tools and brush heads zipped in one bag clipped to the vacuum's handle",
   "The vacuum's cord wrapped, not trailing loose",
   "The closet door swinging fully open without touching anything",
  ],
  "art": ("a wall-mounted rail in a hallway closet holding a broom, mop "
          "and duster hanging handle-down with heads clear of the floor, "
          "a vacuum parked inside a taped floor outline with its "
          "attachment bag clipped to the handle"),
 },
 "Cleaning Supply Zone": {
  "id": "HCZ-003", "order": 3, "difficulty": 3,
  "tagline": "ONE CADDY PER ROOM. EVERY LABEL ORIGINAL. BLEACH APART FROM AMMONIA.",
  "callouts": [
   "Two or three caddies, each labeled on the end with the room it serves",
   "Every bottle wearing its original, legible label",
   "Bleach products and ammonia products on separate shelves",
   "Gloves and cloths riding inside each caddy with the sprays",
   "The whole zone up out of a small child's reach or behind a latch",
   "No sticky ring visible under any bottle",
  ],
  "art": ("labeled cleaning caddies standing on a hallway closet shelf, "
          "each bottle inside showing its own legible original label, "
          "bleach products visible on a separate shelf from "
          "ammonia-based products"),
 },
 "Paper and Household Backstock": {
  "id": "HCZ-004", "order": 4, "difficulty": 2,
  "tagline": "A MINIMUM AND MAXIMUM ON EVERY BIN. EVERY LABEL FACING THE DOOR.",
  "callouts": [
   "Toilet roll in one clear bin with a minimum and maximum on the shelf edge",
   "Bulbs in a labeled bin sorted by fitting",
   "Batteries standing upright in a shallow tray, sorted by size",
   "Every bin label facing the door",
   "The heaviest packs stored at waist height, not overhead",
   "Every pack dated with a marker, oldest at the front",
  ],
  "art": ("a hallway closet shelf holding a clear toilet-roll bin with a "
          "small dated count card on its shelf edge, a labeled bulb bin "
          "sorted by fitting, and a shallow tray of batteries standing "
          "upright sorted by size"),
 },
 "Seasonal and Guest Zone": {
  "id": "HCZ-005", "order": 5, "difficulty": 3,
  "tagline": "ONE BIN PER OCCASION. A DATE ON EVERY LID. A MAP ON THE DOOR.",
  "callouts": [
   "Three or four lidded bins on the upper shelf, each labeled with contents and a closing date",
   "A photograph of each bin's contents taped to its own lid",
   "Guest pillows sealed in a zip bag",
   "A shelf map taped inside the door showing which bin sits where",
   "Nothing overhead heavy enough to need both hands",
   "No bin marked only \"misc\"",
  ],
  "art": ("a hallway closet upper shelf holding lidded storage bins each "
          "labeled with contents and a closing date, a photograph taped "
          "to one lid, and a shelf map taped inside the closet door"),
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
 "Linen Shelf Zone": {
  "frictions": [
   {"symptom": "The flat sheet whose fitted half vanished months ago is "
               "still folded into the stack instead of already gone.",
    "branches": [
     {"answer": "I keep meaning to check if it's really orphaned before "
                "I get rid of it", "cause": "RC-015"},
     {"answer": "Nobody counts the pieces in a folded stack before it "
                "goes back on the shelf", "cause": "KC-008"},
     {"answer": "A folded stack hides a missing piece too well to notice "
                "at a glance", "cause": "KC-005"},
    ]},
   {"symptom": "A towel stack on this shelf stands taller than your "
               "forearm, and the bottom towel only comes out with a "
               "fight.",
    "branches": [
     {"answer": "Pulling from the bottom of a stack that tall is how the "
                "whole pile ends up on the floor", "cause": "KC-010"},
     {"answer": "Nobody ever agreed on how tall a stack here is allowed "
                "to get", "cause": "KC-008"},
     {"answer": "You stopped noticing how tall the stack had gotten, "
                "since it grew a little at a time", "cause": "RC-017"},
    ]},
   {"symptom": "The good sheet set still sits at the front of the shelf, "
               "unused, while the worn ones go back on the bed every "
               "week.",
    "branches": [
     {"answer": "It's too nice to use and too nice to give away, so "
                "nothing gets decided", "cause": "RC-015"},
     {"answer": "It matters more as a keepsake than as something to "
                "actually sleep on", "cause": "RC-014"},
     {"answer": "Nobody wants to be the one who finally decides to use "
                "it or let it go", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Pull every sheet set off the shelf, unfold each one fully, "
             "and check it's complete and still fits a bed you still "
             "own: the flat sheet with no fitted match, the elastic "
             "that's gone slack, and anything that smells sour after "
             "drying all leave today.",
   "victory": "Every remaining set is a complete, matching set that fits "
              "a real bed, and nothing waits folded that failed the "
              "check.",
  },
 },
 "Cleaning Equipment Zone": {
  "frictions": [
   {"symptom": "A broom with splayed, worn bristles is still hanging on "
               "the rail instead of already gone.",
    "branches": [
     {"answer": "It has hung in that exact spot so long you stopped "
                "seeing what its bristles actually look like",
      "cause": "RC-017"},
     {"answer": "There's no rule for when a broom counts as worn out "
                "and needs replacing", "cause": "KC-008"},
     {"answer": "The old vacuum kept for parts takes up the spot a "
                "working broom should have", "cause": "KC-001"},
    ]},
   {"symptom": "A mop handle is left standing against the wall instead "
               "of clipped to the rail, sliding down toward the "
               "doorway.",
    "branches": [
     {"answer": "It's heavier and more awkward to clip than to lean, so "
                "leaning wins in a hurry", "cause": "KC-004"},
     {"answer": "Nobody wrapped the cord and parked the vacuum in its "
                "outline last time, so the rail was never actually "
                "clear to reach", "cause": "KC-009"},
     {"answer": "A handle sliding down the wall and blocking the door "
                "has genuinely hurt someone opening it before",
      "cause": "KC-010"},
    ]},
   {"symptom": "The vacuum has a split hose and a dead brush roll, and "
               "it still stands where the working one needs to stand.",
    "branches": [
     {"answer": "Throwing out a machine that mostly works feels "
                "wasteful, so the decision keeps getting deferred",
      "cause": "RC-015"},
     {"answer": "Nobody in the house is the one who actually orders the "
                "part", "cause": "RC-013"},
     {"answer": "There's no separate spot for a broken tool waiting on "
                "a decision, so it just stays parked with the working "
                "ones", "cause": "KC-002"},
    ]},
  ],
  "first_15": {
   "action": "Stand every handle up and look at the working end: brooms "
             "with splayed bristles that push dust rather than gather "
             "it, a mop head that no longer twists off its plate, and "
             "the old vacuum you keep for parts you've never once "
             "harvested all go out this week.",
   "victory": "Only tools that actually do their job stand in this "
              "closet, and nothing broken is waiting on a repair that "
              "was never going to happen.",
  },
 },
 "Cleaning Supply Zone": {
  "frictions": [
   {"symptom": "Four half-used glass cleaners and three floor sprays "
               "crowd the shelf instead of one open bottle of each.",
    "branches": [
     {"answer": "A new one gets bought because you can't see how much "
                "is left in the old one", "cause": "KC-005"},
     {"answer": "Nobody's ever called four of one thing too many, it's "
                "just how the shelf fills up between shops",
      "cause": "KC-001"},
     {"answer": "There's no rule that only one bottle of a job stays "
                "open at a time", "cause": "KC-008"},
    ]},
   {"symptom": "A spray bottle on this shelf carries no legible "
               "original label, and nobody remembers what's actually "
               "inside it.",
    "branches": [
     {"answer": "It got decanted into a spare bottle at some point and "
                "the label never got copied over", "cause": "KC-008"},
     {"answer": "Bleach products and ammonia products end up stored "
                "close together instead of on separate shelves",
      "cause": "KC-010"},
     {"answer": "Nothing prompts anyone to check a bottle's label before "
                "it fades away completely", "cause": "KC-009"},
    ]},
   {"symptom": "A dried sticky ring has formed at the base of a bottle, "
               "right where the shelf liner should have caught it.",
    "branches": [
     {"answer": "The shelf has no wipeable liner, so a drip soaks "
                "straight into the wood before anyone notices",
      "cause": "RC-016"},
     {"answer": "Nobody wipes the base of the bottles when they go "
                "back, only when there's an obvious mess",
      "cause": "KC-009"},
     {"answer": "It's tucked at the back of a dense shelf where a small "
                "drip doesn't get noticed for weeks", "cause": "KC-005"},
    ]},
  ],
  "first_15": {
   "action": "Line every bottle up on the hallway floor. Anything "
             "decanted into an unmarked spray bottle is disposed of "
             "according to its own product's instructions, and the "
             "specialty cleaner bought for one old stain goes with it.",
   "victory": "Every bottle on the shelf carries its own legible "
              "original label, and only one open bottle of each job "
              "remains.",
  },
 },
 "Paper and Household Backstock": {
  "frictions": [
   {"symptom": "A loose battery rolls free in this bin, and nobody can "
               "vouch for whether it's still good or already dead.",
    "branches": [
     {"answer": "Batteries get emptied out of their packaging instead "
                "of staying in it, so there's no way to tell them apart "
                "by age", "cause": "KC-008"},
     {"answer": "A loose button cell at floor level is a real risk for "
                "a small child in the hallway", "cause": "KC-010"},
     {"answer": "Nobody sorts this tray by size until it's already a "
                "mess of mixed batteries", "cause": "KC-009"},
    ]},
   {"symptom": "The toilet roll bin is empty, and nobody mentioned it "
               "was close before the last one came out.",
    "branches": [
     {"answer": "Taking the last one and not saying anything is just "
                "what happens here, it's nobody's job to flag it",
      "cause": "RC-013"},
     {"answer": "There's no minimum written on the shelf edge to catch "
                "it before it runs out", "cause": "KC-008"},
     {"answer": "The bin is solid sided, so the level isn't visible "
                "until you actually lift the lid", "cause": "KC-005"},
    ]},
   {"symptom": "A shrink-wrapped bulk pack sits above head height, and "
               "the count already on the shelf below is well past any "
               "written maximum.",
    "branches": [
     {"answer": "The deal was good enough to buy even though there was "
                "nowhere left on the shelf for it", "cause": "KC-001"},
     {"answer": "Nothing this heavy should be stored above head height "
                "where a tug brings it down on you", "cause": "KC-010"},
     {"answer": "There's no maximum written on the shelf edge to say "
                "the deal doesn't fit this time", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Take the lot out. Loose batteries you cannot vouch for, "
             "bulbs for fittings you replaced when you went over to "
             "LED, and any bulk pack too big to lift down alone all "
             "leave now.",
   "victory": "Every battery is sorted by size in its tray, every bulb "
              "is boxed by fitting, and nothing left on the shelf is "
              "too heavy or too high to lift down alone.",
  },
 },
 "Seasonal and Guest Zone": {
  "frictions": [
   {"symptom": "A bin marked misc has moved through two closet "
               "reshuffles, and nobody can say what's actually inside "
               "it without opening it.",
    "branches": [
     {"answer": "Naming what's inside and deciding on each thing is a "
                "bigger job than just leaving the lid on",
      "cause": "RC-015"},
     {"answer": "A sealed bin on a high shelf is the easiest place in "
                "the house to defer a decision, out of sight and out of "
                "mind", "cause": "KC-005"},
     {"answer": "There's no label naming its contents or the date it "
                "was last opened", "cause": "KC-008"},
    ]},
   {"symptom": "Guest bedding comes back from the wash and lands on the "
               "everyday linen shelf instead of its own labeled bin.",
    "branches": [
     {"answer": "There's no separate labeled bin actually waiting for "
                "it, so it goes wherever there's room", "cause": "KC-002"},
     {"answer": "Whoever strips the guest bed isn't the one who knows "
                "where the seasonal bins live", "cause": "RC-013"},
     {"answer": "It's faster to drop it on the nearest shelf than to "
                "find and reopen the right bin", "cause": "KC-004"},
    ]},
   {"symptom": "Reaching a top-shelf bin means standing on a hallway "
               "chair, with a lid blocking the view of the step down.",
    "branches": [
     {"answer": "There's no stool kept near this closet, so a chair is "
                "what's nearest", "cause": "KC-006"},
     {"answer": "A bin of decorations is heavier than it looks once "
                "it's overhead and shifts weight coming down",
      "cause": "KC-010"},
     {"answer": "Nobody moved the heaviest bins down to a lower shelf "
                "when the closet was last reset", "cause": "KC-003"},
    ]},
  ],
  "first_15": {
   "action": "Take every lid off, on the floor, in daylight. "
             "Decorations for a tree you no longer put up, a guest "
             "pillow gone flat and yellow, and any bin marked misc "
             "whose contents you cannot name without looking all go.",
   "victory": "Every remaining bin holds one named occasion, and "
              "nothing sealed inside it is something you couldn't name "
              "from memory.",
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
 ("Linen Shelf Zone", "HCF-001", "THE SHEET THAT LOST ITS OTHER HALF",
  "a folded stack of bed sheets on a hallway closet shelf with one flat "
  "sheet lying loose and unmatched beside a neat folded set, no fitted "
  "sheet visible near it"),
 ("Linen Shelf Zone", "HCF-002", "A TOWEL STACK TALLER THAN YOUR FOREARM",
  "a hallway closet shelf holding a stack of folded towels taller than "
  "a forearm's length, the top towel wobbling slightly"),
 ("Linen Shelf Zone", "HCF-003", "THE GOOD SET NOBODY PUTS ON A BED",
  "a nicer, more decorative sheet set sitting untouched at the front of "
  "a hallway closet shelf ahead of visibly worn, faded sheet sets "
  "behind it"),

 ("Cleaning Equipment Zone", "HCF-004",
  "A BROOM THAT PUSHES DUST INSTEAD OF GATHERING IT",
  "a broom hanging from a hallway closet rail with its bristles "
  "visibly splayed outward instead of gathered in a point"),
 ("Cleaning Equipment Zone", "HCF-005",
  "A MOP HANDLE SLIDING TOWARD THE DOORWAY",
  "a mop handle leaning against a hallway closet wall, sliding down "
  "toward the closet doorway instead of hanging from a wall clip"),
 ("Cleaning Equipment Zone", "HCF-006",
  "THE VACUUM WAITING ON A REPAIR THAT NEVER COMES",
  "an upright vacuum cleaner standing in a hallway closet with a "
  "visibly split hose, a strip of masking tape wrapped around its "
  "handle"),

 ("Cleaning Supply Zone", "HCF-007",
  "FOUR HALF-USED BOTTLES OF THE SAME SPRAY",
  "four nearly identical spray bottles of glass cleaner crowded "
  "together on a hallway closet shelf, each only a third full"),
 ("Cleaning Supply Zone", "HCF-008",
  "A SPRAY BOTTLE WITH NO LABEL LEFT TO READ",
  "a spray bottle on a hallway closet shelf with its original label "
  "worn away to nothing, standing among other clearly labeled bottles"),
 ("Cleaning Supply Zone", "HCF-009", "A STICKY RING DRIED ONTO THE SHELF",
  "a dried sticky ring stain on a hallway closet shelf board where a "
  "cleaning bottle has been standing"),

 ("Paper and Household Backstock", "HCF-010",
  "A LOOSE BATTERY NOBODY CAN VOUCH FOR",
  "a shallow tray in a hallway closet holding a loose jumble of "
  "mismatched batteries with no packaging to identify them"),
 ("Paper and Household Backstock", "HCF-011",
  "THE LAST ROLL LEAVES WITH NO WARNING",
  "an open toilet-roll storage bin in a hallway closet sitting "
  "completely empty"),
 ("Paper and Household Backstock", "HCF-012",
  "A BULK PACK OVERHEAD, PAST ANY WRITTEN LIMIT",
  "a shrink-wrapped bulk pack of paper towels sitting on a hallway "
  "closet shelf above head height, stacked well past a marked "
  "shelf-edge limit"),

 ("Seasonal and Guest Zone", "HCF-013",
  "THE BIN MARKED MISC, MOVED THREE TIMES UNOPENED",
  "a plain storage bin on a high hallway closet shelf with no visible "
  "label, positioned among other clearly labeled bins"),
 ("Seasonal and Guest Zone", "HCF-014",
  "GUEST BEDDING STRAYS ONTO THE EVERYDAY SHELF",
  "folded guest bedding sitting on top of an everyday linen stack on a "
  "hallway closet shelf instead of inside its own separate bin"),
 ("Seasonal and Guest Zone", "HCF-015", "A CHAIR STANDING IN FOR A STOOL",
  "a hallway chair positioned beneath a high closet shelf, someone's "
  "feet visible standing on its seat reaching upward"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, hall-closet-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "four nearly identical spray bottles crowded together on a "
           "hallway closet shelf, far more than one open bottle of that "
           "job would ever need",
 "KC-002": "a stack of folded guest bedding sitting on top of the "
           "everyday linen shelf with no labeled bin nearby to hold it",
 "KC-003": "a heavy storage bin sitting on a high hallway closet shelf "
           "well above head height, with a lower empty shelf visible "
           "beneath it",
 "KC-004": "a mop leaning unclipped against a hallway closet wall "
           "instead of hanging from the rail within easy reach",
 "KC-005": "a solid-sided storage bin in a hallway closet with no way "
           "to see how full it is without lifting the lid",
 "KC-006": "a hallway chair standing in for a step stool beneath a high "
           "closet shelf, no stool anywhere in sight",
 "KC-008": "a bare hallway closet shelf edge with no count card or "
           "label anywhere on it, bins stacked with no visible rule",
 "KC-009": "an empty toilet-roll bin in a hallway closet with no "
           "shopping list nearby and no note that it needs restocking",
 "KC-010": "a heavy bulk pack sitting on a hallway closet shelf above "
           "head height, positioned to slide free at the slightest tug",
 "RC-013": "an unrefilled storage bin sitting empty in a hallway closet "
           "at the end of the day, no single person's name attached to "
           "restocking it",
 "RC-014": "a nicer sheet set kept folded and untouched at the front of "
           "a hallway closet shelf instead of ever going onto a bed",
 "RC-015": "a sealed storage bin marked vaguely, sitting untouched on a "
           "hallway closet shelf, clearly not yet decided about",
 "RC-016": "a hand reaching awkwardly behind a dense row of bottles on "
           "a hallway closet shelf toward a dried sticky ring that is "
           "hard to reach",
 "RC-017": "a worn broom with splayed bristles hanging in a hallway "
           "closet exactly where it has hung, unnoticed, for a long "
           "time",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Linen Shelf Zone": [
  "Run a hand along the shelf's front lip and check for the grey dust "
  "line before it thickens onto the clean stack below it.",
  "Wipe the shelf brackets and the underside of the board above with a "
  "dry cloth, catching the fluff that clings and drops onto the stack.",
  "Shake out one folded sheet set and refold it to the same width as "
  "its neighbors, checking for a musty note as you go.",
 ],
 "Cleaning Equipment Zone": [
  "Empty the vacuum canister into the bin and wipe it out before it "
  "goes back inside the taped outline.",
  "Comb the broom bristles clear of trapped hair and thread, letting "
  "nothing carry back onto the floor you just swept.",
  "Run each cord through a folded cloth along its whole length as you "
  "coil it, lifting off the dust that collects in the loops.",
 ],
 "Cleaning Supply Zone": [
  "Wipe the crusted ring off the base of one bottle and clean the "
  "dried run down its neck before it goes back on the shelf.",
  "Lift the shelf liner, rinse both faces, and lay it back flat so the "
  "next slow drip lands on something wipeable.",
  "Wipe the inside of a caddy's divider walls and its handle where "
  "product residue gathers most.",
 ],
 "Paper and Household Backstock": [
  "Lift the battery tray out, wipe the bottom clean, and watch for a "
  "white crust before it dries back before the batteries return.",
  "Press the underside of one paper pack stored against the outside "
  "wall to check for damp before it soaks through unnoticed.",
  "Tip the paper dust and cardboard flecks from the bottom corners of "
  "the toilet-roll bin before it goes back on the shelf.",
 ],
 "Seasonal and Guest Zone": [
  "Put your nose to the bottom of one open bin and check for the "
  "mustiness that means something went in damp.",
  "Wipe the dust off the top of a bin lid before you set it aside, so "
  "none of it tips down into the open bin below.",
  "Check the shelf map taped inside the closet door is still legible "
  "and still matches what's actually on each shelf.",
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
 {"id": "HCA-001", "zone": "Linen Shelf Zone",
  "title": "UNFOLD EVERY SET AND CHECK IT'S WHOLE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull every sheet set off the shelf, unfold each one fully, "
          "and check it is complete and still fits a bed in this "
          "house.",
  "why": "A set that's missing its match or gone slack at the elastic "
         "is impossible to use in the moment you actually reach for it.",
  "inputs": ["a bin bag", "the hallway floor"],
  "steps": [
   "Pull every sheet set off the shelf, unfold each one fully, and "
   "check it's complete and still fits a bed you still own: the flat "
   "sheet with no fitted match, the elastic that's gone slack, and "
   "anything that smells sour after drying all leave today.",
   "Set aside anything unopened and genuinely still useful to give "
   "away rather than binning it.",
   "Refold what stays to one width and group by bed size."],
  "causes": ["KC-005", "RC-014"],
  "victory": "Every remaining set is a complete, matching set that fits "
             "a real bed, and nothing waits folded that failed the "
             "check.",
  "next": "HCS-001",
  "art": "a hallway closet shelf mid-clear with unfolded sheet sets "
         "laid out on the floor, one incomplete set set apart from the "
         "rest"},

 {"id": "HCA-002", "zone": "Linen Shelf Zone",
  "title": "BUNDLE EACH SET AND LABEL THE SHELF EDGE",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Fold each set to one uniform footprint, bundle it inside its "
          "own pillowcase, and write the bed size and count on the "
          "shelf edge.",
  "why": "A shelf label that only names the size and not the count "
         "still leaves a laundry-day guess.",
  "inputs": ["pillowcases already on hand", "a permanent marker",
             "adhesive shelf-edge labels"],
  "steps": [
   "Fold each set to one uniform footprint and bundle it inside its "
   "own pillowcase so a bed change is one grab, not four.",
   "Group bundles by bed size: queen and king low, everyday towels at "
   "chest height, guest blankets on top.",
   "Write the size and count on the shelf edge underneath, not just "
   "the name."],
  "causes": ["KC-008", "RC-015"],
  "victory": "Every bed's sets are bundled inside their own "
             "pillowcases, and the shelf edge names both the size and "
             "the count.",
  "next": "HCA-001",
  "art": "a hand writing a bed size and a count onto a shelf-edge "
         "label beneath a shelf of pillowcase-bundled sheet sets"},

 {"id": "HCA-003", "zone": "Cleaning Equipment Zone",
  "title": "STAND UP EVERY TOOL AND CHECK THE WORKING END",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Stand every handle up and look at the working end, removing "
          "anything that no longer does its job.",
  "why": "A broom that pushes dust instead of gathering it, or a spare "
         "vacuum kept for parts never harvested, is taking up the spot "
         "a working tool needs.",
  "inputs": ["a bin bag"],
  "steps": [
   "Stand every handle up and look at the working end: brooms with "
   "splayed bristles that push dust rather than gather it, a mop head "
   "that no longer twists off its plate, and the old vacuum you keep "
   "for parts you've never once harvested all go out this week.",
   "Recycle what can be recycled, and clear the floor space they were "
   "taking."],
  "causes": ["KC-001", "RC-017"],
  "victory": "Only tools that actually do their job stand in this "
             "closet, and nothing broken is waiting on a repair that "
             "was never going to happen.",
  "next": "HCS-002",
  "art": "a row of cleaning tools standing upright in a hallway "
         "closet, one broom with splayed bristles set apart to be "
         "discarded"},

 {"id": "HCA-004", "zone": "Cleaning Equipment Zone",
  "title": "FIT THE RAIL AND TAPE THE VACUUM'S OUTLINE",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Fit a rail so each tool hangs with its head clear of the "
          "floor, and tape a floor outline for the vacuum with its "
          "attachments bagged on the handle.",
  "why": "A mop head left standing on the floor bends over and "
         "re-soils what you just cleaned, and an unclipped handle is "
         "what slides down across the doorway.",
  "inputs": ["a wall rail with hooks", "tape for the floor outline",
             "a small zip bag for attachments"],
  "steps": [
   "Fit a rail and hang each tool so bristles and mop heads swing "
   "free of the floor.",
   "Tape an outline for the vacuum's footprint on the closet floor.",
   "Zip the crevice tools and brush heads into one bag clipped to the "
   "vacuum's handle."],
  "causes": ["KC-004", "KC-009"],
  "victory": "Handles hang from the rail with heads clear of the "
             "floor, the vacuum parks inside its taped outline, and "
             "the attachment bag rides on its handle.",
  "next": "HCA-003",
  "art": "a wall-mounted rail in a hallway closet holding a broom, mop "
         "and duster hanging handle-down, a taped floor outline "
         "visible below with a vacuum parked inside it"},

 {"id": "HCA-005", "zone": "Cleaning Supply Zone",
  "title": "LINE UP EVERY BOTTLE AND CLEAR THE UNMARKED ONES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Line every bottle up on the hallway floor, and remove "
          "anything decanted into an unmarked spray bottle or bought "
          "for one old stain.",
  "why": "A bottle with no legible original label is a guess every "
         "time you reach for it, and pouring like into like is the "
         "only way to know what's actually here.",
  "inputs": ["the hallway floor", "a bin bag"],
  "steps": [
   "Line every bottle up on the hallway floor. Anything decanted into "
   "an unmarked spray bottle is disposed of according to its own "
   "product's instructions, and the specialty cleaner bought for one "
   "old stain goes with it.",
   "Pour only identical products together into one bottle.",
   "Set the survivors back with every label facing out."],
  "causes": ["RC-016", "KC-009"],
  "victory": "Every bottle on the shelf carries its own legible "
             "original label, and only one open bottle of each job "
             "remains.",
  "next": "HCS-003",
  "art": "cleaning bottles lined up on a hallway floor, one unmarked "
         "spray bottle set apart from a row of clearly labeled ones"},

 {"id": "HCA-006", "zone": "Cleaning Supply Zone",
  "title": "BUILD ONE CADDY PER ROOM",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Build a bathroom caddy and a kitchen caddy so the whole job "
          "for that room travels in one hand, and keep bleach and "
          "ammonia products on separate shelves.",
  "why": "Sending yourself back to this closet twice mid-clean is the "
         "walk this caddy exists to remove, and bleach beside ammonia "
         "is the one combination to refuse outright.",
  "inputs": ["two caddies", "adhesive labels for the caddy ends"],
  "steps": [
   "Build a bathroom caddy and a kitchen caddy, with gloves and "
   "cloths riding inside each one alongside the sprays.",
   "Label each caddy's end with the room it serves.",
   "Move bleach products and ammonia products onto separate shelves, "
   "out of a small child's reach or behind a latch."],
  "causes": ["KC-002", "KC-010"],
  "victory": "One caddy per room carries its own labeled sprays and "
             "cloths, and bleach and ammonia products sit on separate "
             "shelves.",
  "next": "HCA-005",
  "art": "two labeled cleaning caddies standing ready in a hallway "
         "closet, one marked for the bathroom and one for the kitchen, "
         "bleach and ammonia products visible on separate shelves "
         "behind them"},

 {"id": "HCA-007", "zone": "Paper and Household Backstock",
  "title": "TAKE THE LOT OUT AND SORT BY SIZE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take every battery, bulb, and paper pack out onto the "
          "hallway floor, removing anything you can't vouch for or "
          "can't lift safely alone.",
  "why": "A loose battery nobody can vouch for and a fitting you "
         "replaced months ago are both still costing this shelf "
         "space.",
  "inputs": ["the hallway floor", "a bin bag"],
  "steps": [
   "Take the lot out. Loose batteries you cannot vouch for, bulbs for "
   "fittings you replaced when you went over to LED, and any bulk "
   "pack too big to lift down alone all leave now.",
   "Sort surviving batteries upright in a shallow tray by size, and "
   "box bulbs together by fitting.",
   "Set the heaviest remaining packs at waist height, not overhead."],
  "causes": ["KC-010", "KC-003"],
  "victory": "Every battery is sorted by size in its tray, every bulb "
             "is boxed by fitting, and nothing left on the shelf is "
             "too heavy or too high to lift down alone.",
  "next": "HCS-004",
  "art": "batteries and bulbs spread out on a hallway floor being "
         "sorted into a shallow tray and a labeled bin, an oversized "
         "pack set apart to be moved"},

 {"id": "HCA-008", "zone": "Paper and Household Backstock",
  "title": "WRITE A MINIMUM AND MAXIMUM ON EVERY BIN",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Write a minimum and a maximum on the shelf edge in front of "
          "each bin, sized to what the bin can hold without stacking "
          "above its rim.",
  "why": "A number in your head is not a number anyone else can read, "
         "and an undated bulk pack is where a saving quietly expires.",
  "inputs": ["a marker", "adhesive shelf-edge labels"],
  "steps": [
   "Set the maximum for each bin as the count that fits inside it "
   "without stacking above the rim.",
   "Write both the minimum and maximum on the shelf edge in front of "
   "each bin.",
   "Date every pack with a marker as it goes back, oldest at the "
   "front."],
  "causes": ["KC-001", "KC-008"],
  "victory": "Every bin carries a minimum and maximum on its shelf "
             "edge, and every pack behind it is dated with the oldest "
             "at the front.",
  "next": "HCA-007",
  "art": "a hand writing a minimum and maximum onto a shelf-edge label "
         "in front of a hallway closet bin, dated packs visible behind "
         "it"},

 {"id": "HCA-009", "zone": "Seasonal and Guest Zone",
  "title": "OPEN EVERY LID ON THE FLOOR, IN DAYLIGHT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take every lid off, on the floor, in daylight, and remove "
          "anything you can't name from memory.",
  "why": "A sealed bin of unknowns is not storage, it is a decision "
         "you agreed to keep paying for.",
  "inputs": ["the hallway floor", "a bin bag"],
  "steps": [
   "Take every lid off, on the floor, in daylight. Decorations for a "
   "tree you no longer put up, a guest pillow gone flat and yellow, "
   "and any bin marked misc whose contents you cannot name without "
   "looking all go.",
   "For each remaining item, name the specific occasion in the next "
   "twelve months when it will be used.",
   "Anything with no named occasion does not get the lid back on."],
  "causes": ["RC-015", "KC-005"],
  "victory": "Every remaining bin holds one named occasion, and "
             "nothing sealed inside it is something you couldn't name "
             "from memory.",
  "next": "HCS-005",
  "art": "storage bins opened on a hallway floor in daylight, their "
         "contents spread out for sorting, one bin marked misc set "
         "apart"},

 {"id": "HCA-010", "zone": "Seasonal and Guest Zone",
  "title": "LABEL EVERY BIN, DATE THE LID, MAP THE SHELF",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Label each bin with its contents and the date it was last "
          "closed, photograph it packed, and tape a shelf map inside "
          "the door.",
  "why": "A photograph taped to the lid gives repacking a target "
         "instead of a guess, and a shelf map means someone else can "
         "find the guest bedding without unstacking the shelf.",
  "inputs": ["a marker", "a camera or phone", "tape",
             "paper for the shelf map"],
  "steps": [
   "Label each bin with what's inside and the date it was last "
   "closed.",
   "Photograph each bin packed and tape the picture to the lid.",
   "Tape a simple shelf map inside the closet door showing which bin "
   "sits where."],
  "causes": ["KC-002", "RC-013"],
  "victory": "Every bin is labeled with contents and a closing date, "
             "carries a photo of itself packed, and the door holds a "
             "shelf map that matches the shelves.",
  "next": "HCA-009",
  "art": "a labeled storage bin with a photograph taped to its lid, a "
         "shelf map taped inside a hallway closet door visible behind "
         "it"},

 {"id": "HCA-011", "zone": None,
  "title": "THE FULL SHELF WEIGHT AND REACH SAFETY WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every shelf checking what's stored above head height, "
          "whether a stool lives in reach, and that the brackets "
          "holding the heaviest loads are sound.",
  "why": "A heavy bin overhead and a hallway chair standing in for a "
         "stool both hide until someone tests for them on purpose.",
  "inputs": ["a step stool"],
  "steps": [
   "Check every shelf for anything heavy stored above head height, "
   "and move it down to a lower shelf.",
   "Confirm a real step stool lives near this closet, not a hallway "
   "chair standing in for one.",
   "Check the shelf brackets are screwed into studs, not just into "
   "plasterboard, under the heaviest loads."],
  "causes": ["KC-006", "KC-010", "KC-003"],
  "victory": "Nothing heavy sits above head height, a real stool lives "
             "within reach, and every loaded bracket is anchored into "
             "a stud.",
  "next": "HCA-010",
  "art": "a hand using a step stool to move a heavy storage bin down "
         "from a high hallway closet shelf to a lower one"},

 {"id": "HCA-012", "zone": None,
  "title": "THE WEEKLY BEFORE-THE-LIST CHECK",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "Walk the paper, battery, and bulb bins reading what's low "
          "before the shopping list gets written, and name who is "
          "doing it this week.",
  "why": "Everybody takes the last roll and almost nobody mentions it, "
         "so this zone fails silently unless somebody is actually "
         "assigned to look.",
  "inputs": ["the shopping list"],
  "steps": [
   "Walk the backstock bins and read each one against its written "
   "minimum before the list gets written.",
   "Say out loud, or write down, whose turn it is to do this pass "
   "this week.",
   "Add anything genuinely below its minimum to the list on the "
   "spot."],
  "causes": ["RC-013", "KC-009"],
  "victory": "The bins were read against their written minimums before "
             "this week's list was written, and one named person did "
             "it.",
  "next": "HCA-011",
  "art": "a hand writing an item onto a shopping list while standing "
         "in front of a hallway closet bin sitting below its own "
         "shelf-edge minimum"},

 {"id": "HCA-013", "zone": None,
  "title": "THE SEASONAL MAXIMUM AND LABEL AUDIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Once a season, check every written maximum and every bin "
          "label against what's actually on the shelves, correcting "
          "anything that has drifted.",
  "why": "A maximum or a label written once and never revisited stops "
         "meaning anything the first time a good deal or a quiet "
         "clear-out moves past it.",
  "inputs": ["a marker", "this season's receipts if you kept them"],
  "steps": [
   "Compare the count behind each bin against its written maximum, "
   "and note any line that has crept over.",
   "Relabel any bin whose contents or closing date no longer match "
   "what's inside it.",
   "Correct the shelf map inside the door if a bin has moved."],
  "causes": ["KC-008", "KC-001"],
  "victory": "Every bin sits at or under a maximum checked this "
             "season, and every label and the shelf map both match "
             "what's actually on the shelves.",
  "next": "HCA-012",
  "art": "a hand comparing a bin's count against a shelf-edge maximum "
         "label in a hallway closet, a shelf map taped inside the door "
         "beside it"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a hall closet, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("HCE-001", "THE MIDNIGHT SHEET CHANGE",
  "A child is sick at midnight and the bed needs fresh sheets right "
  "now, no time to hunt.",
  ["HCZ-001"],
  "The right size set comes off the shelf in one bundle, no digging "
  "through mismatched pieces.",
  "If you had to unfold three sets to find one complete match, the "
  "check-and-bundle habit slipped. Draw HCA-001.",
  "a hand pulling one bundled sheet set from a hallway closet shelf "
  "quickly at night"),
 ("HCE-002", "THE SPILL THAT NEEDS EVERYTHING AT ONCE",
  "Something spills across the kitchen floor and the mop, the bucket "
  "and gloves all have to come out together, right now.",
  ["HCZ-002"],
  "Every tool comes off the rail already working, with nothing "
  "missing from the bag on the handle.",
  "If a tool was broken or an attachment was missing from the bag, "
  "the stand-up check or the rail habit slipped. Draw HCA-003.",
  "a hand pulling a working mop from a hallway closet rail in a "
  "hurry, a bucket already in the other hand"),
 ("HCE-003", "THE GUEST ARRIVING IN AN HOUR",
  "Guests are due in an hour and the bathroom and kitchen both need a "
  "fast, real clean.",
  ["HCZ-003"],
  "Grabbing the bathroom caddy in one hand gets the whole job there "
  "without a second trip to this closet.",
  "If you had to come back for a bottle the caddy should have held, "
  "the one-caddy-per-room habit slipped. Draw HCA-006.",
  "a hand lifting a fully stocked bathroom caddy off a hallway closet "
  "shelf in one motion"),
 ("HCE-004", "THE POWER CUT THAT NEEDS A FLASHLIGHT NOW",
  "The power goes out at night and the flashlight needs batteries "
  "that actually work, immediately.",
  ["HCZ-004"],
  "The right size battery is standing upright in its tray, sorted and "
  "easy to find in the dark.",
  "If you had to feel around for a loose battery you couldn't vouch "
  "for, the sort-by-size habit slipped. Draw HCA-007.",
  "a hand reaching into a battery tray in a dark hallway closet, "
  "batteries standing upright and sorted by size"),
 ("HCE-005", "THE OVERNIGHT GUEST WITH NO WARNING",
  "Somebody needs the guest bed made up tonight, with no notice.",
  ["HCZ-005"],
  "The guest bedding is clean, in its own labeled bin, and the shelf "
  "map says exactly where to find it.",
  "If the bedding had drifted onto the everyday shelf or the bin had "
  "no date, the wash-and-return habit slipped. Draw HCA-010.",
  "a hand lifting a labeled bin of clean guest bedding off a hallway "
  "closet shelf, a shelf map visible taped inside the door"),
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
        "related": {"standard": f"HCS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your closet, "
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
    standard_id = (f"HCS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"HCS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "HCR-001", "title": "THE HALL CLOSET", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "FIVE SHELVES OF EVERYTHING WITH NOWHERE ELSE TO GO. "
                   "START WITH THE ONE YOU CAN'T SEE THE BACK OF.",
        "objective": "The hall closet is the darkest and deepest "
                     "storage in the house, and the only one nobody "
                     "owns. This card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"HCZ-001 Linen Shelf Zone. {start_tip['text']}"
            if start_tip else
            "HCZ-001 Linen Shelf Zone. Emptying it gives every other "
            "zone somewhere to put things."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your closet. Put the rest back.",
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
        "safety_first": "Do HCA-011 The Full Shelf Weight And Reach "
                        "Safety Walk before any rebuild. It takes thirty "
                        "minutes and covers every shelf's height, the "
                        "stool, and every loaded bracket.",
        "related": {"contents": "HCZ-001 to HCZ-005, HCF-001 to "
                                 "HCF-015, the shared root causes in "
                                 "ops/root_causes.py, HCA-001 to "
                                 "HCA-013, HCS-001 to HCS-005, HCE-001 "
                                 "to HCE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole "
                           "hallway closet in its settled state, linen "
                           "shelf, cleaning equipment on a rail, "
                           "cleaning supply caddies, paper and battery "
                           "backstock, and seasonal bins all visible in "
                           "one frame",
                "must_show": ["all five zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the five zones is. If one is "
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
    return {"deck": "hall-closet", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_pantry_deck.py)."""
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

    # The zone-linked 15-minute actions per zone must quote the Manual's
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

    assert any(c["id"] == "HCA-011" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This deck's zone list must be exactly the Manual's five, in the
    # Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 5, (
        "this room has five Manual zones; that count moved")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        hall-closet ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
