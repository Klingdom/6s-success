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
and filled in: KC-001, KC-002, KC-005, KC-006, KC-007, KC-008, KC-009,
KC-010, KC-011, KC-012, RC-013, RC-014, RC-015, RC-017. KC-003, KC-004 and
RC-016 are not reachable because nothing in this room's real diagnosis
branches to them, and that is a true statement about this room's own
frictions, not an oversight; nothing pads the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Hall Closet ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). The budget
below is the same shape as Entryway and Pantry, the other five-zone rooms
in this line: five real zones, fifteen frictions (three per zone), fourteen
reachable root causes (one more than Pantry's thirteen, because this room's
real frictions happen to reach EXCESS and POOR REPLENISHMENT where Pantry's
did not), thirteen action cards (two per zone plus three whole-closet), five
standard cards and five event cards. 58 cards in total, not padded or
trimmed to match any other room's count.

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
CAUSE_IDS = ["KC-001", "KC-002", "KC-005", "KC-006", "KC-007", "KC-008",
             "KC-009", "KC-010", "KC-011", "KC-012", "RC-013", "RC-014",
             "RC-015", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Linen Shelf Zone": {
  "id": "HCZ-001", "order": 1, "difficulty": 3,
  "tagline": "THREE SETS PER BED. ONE PILLOWCASE EACH. THE SIZE ON THE EDGE.",
  "callouts": [
   "Sheet sets nested inside their own matching pillowcases",
   "A bed-size label fixed to the shelf edge under each stack",
   "A stack of folded everyday towels no taller than a forearm",
   "Two spare blankets standing on the top shelf",
   "Clear space above the blankets with nothing stacked on them",
   "Queen and king sets sitting on a lower shelf than the guest blankets",
  ],
  "art": ("a linen shelf holding neatly folded sheet sets each nested "
          "inside its own matching pillowcase, a small dated label fixed "
          "to the shelf edge beneath each stack, a stack of folded "
          "towels no taller than a forearm, and two spare blankets "
          "standing on the top shelf with nothing stacked on them"),
 },
 "Cleaning Equipment Zone": {
  "id": "HCZ-002", "order": 2, "difficulty": 2,
  "tagline": "EVERYTHING HANGS. NOTHING TOUCHES THE FLOOR. THE DOOR SWINGS CLEAR.",
  "callouts": [
   "A vacuum standing inside a taped floor outline",
   "Its cord wrapped neatly around the body",
   "A zipped bag of attachments clipped to the vacuum's handle",
   "A broom hanging handle-down from a wall clip, head clear of the floor",
   "A mop and a duster hanging the same way, heads clear of the floor",
   "The closet door swinging fully open without touching anything",
  ],
  "art": ("a cleaning closet with a vacuum standing inside a taped floor "
          "outline, its cord wrapped and a zipped attachment bag clipped "
          "to its handle, a broom, mop and duster hanging handle-down "
          "from wall clips with their heads clear of the floor, and the "
          "closet door swinging fully open"),
 },
 "Cleaning Supply Zone": {
  "id": "HCZ-003", "order": 3, "difficulty": 3,
  "tagline": "ONE CADDY PER ROOM. BLEACH AND AMMONIA APART. OUT OF SMALL HANDS.",
  "callouts": [
   "Two or three caddies, each labeled with the room it serves",
   "Every bottle wearing its own original label",
   "Bleach products standing on one shelf",
   "Ammonia products standing on a separate shelf",
   "A latch or height barrier keeping the zone out of a small child's reach",
   "Gloves and cloths riding inside each caddy",
  ],
  "art": ("a cleaning supply shelf holding two or three caddies each "
          "with an end label naming its room, bleach products standing "
          "on one shelf and ammonia-based products on a separate shelf, "
          "and a latch fixed at the top of the closet door"),
 },
 "Paper and Household Backstock": {
  "id": "HCZ-004", "order": 4, "difficulty": 2,
  "tagline": "A MINIMUM AND A MAXIMUM ON EVERY BIN. DATED. FACING THE DOOR.",
  "callouts": [
   "Toilet roll sitting loose in one clear bin",
   "A card on the shelf edge reading a minimum and maximum count",
   "Bulbs in a labeled bin sorted by fitting",
   "Batteries standing upright in a shallow tray",
   "Battery sizes readable without lifting a single pack out",
   "Every bin label turned to face the door",
  ],
  "art": ("a household backstock shelf with toilet roll sitting loose "
          "in a clear bin, a small dated card fixed to the shelf edge, "
          "bulbs in a labeled bin sorted by fitting, and batteries "
          "standing upright in a shallow tray with their sizes visible "
          "without lifting one out"),
 },
 "Seasonal and Guest Zone": {
  "id": "HCZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE BIN PER OCCASION. LABELED. MAPPED ON THE DOOR.",
  "callouts": [
   "Three or four lidded bins standing on the upper shelf",
   "A label on each bin naming its contents",
   "The month each bin was last closed marked on its label",
   "Guest pillows sealed inside a zip bag",
   "A shelf map taped inside the closet door",
   "Nothing overhead heavy enough to need both hands to lift",
  ],
  "art": ("a closet upper shelf holding three or four lidded storage "
          "bins each with its own label, guest pillows sealed inside a "
          "zip bag, and a small paper map taped to the inside of the "
          "closet door"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# DIAGNOSIS LAYER. Written into content/manual/source/content.json by this
# project (not this file, see scratch patch script used to write it): each
# zone's own "diagnosis" object holds "frictions" (symptom plus branches to
# a shared root-cause id) and "first_15" (a genuine fifteen-minute starting
# action and a checkable victory condition). This dict is this file's own
# record of what that layer is expected to hold, so build() can assert
# nothing has drifted between the two files.
# ---------------------------------------------------------------------------

EXPECTED_DIAGNOSIS = {
 "Linen Shelf Zone": {
  "frictions": [
   {"symptom": "A sheet set too nice to use sits at the front of this "
               "shelf year after year while the beds get slept on with "
               "the worn ones.",
    "branches": [
     {"answer": "It's the nicest set we own and I don't want it to wear "
                "out", "cause": "RC-014"},
     {"answer": "It's not really a decision I've made, I just keep "
                "meaning to put it on a bed", "cause": "RC-015"},
     {"answer": "It's been at the front of the shelf so long I don't "
                "register it as odd anymore", "cause": "RC-017"},
    ]},
   {"symptom": "A towel stack on this shelf has grown taller than your "
               "forearm, and pulling one from the bottom risks bringing "
               "the whole stack down.",
    "branches": [
     {"answer": "Nobody checks stack height when folding laundry back "
                "onto this shelf", "cause": "RC-013"},
     {"answer": "The bracket holding this shelf has never been checked "
                "to see if it's screwed into a stud", "cause": "KC-010"},
     {"answer": "There's no agreed limit on how tall a stack is allowed "
                "to get", "cause": "KC-008"},
    ]},
   {"symptom": "A set sized for the guest bed is folded in among the "
               "everyday sets, so the wrong size gets grabbed at "
               "bedtime.",
    "branches": [
     {"answer": "There's no fixed spot per bed size, so sets get folded "
                "wherever there's room", "cause": "KC-002"},
     {"answer": "Two people fold the laundry differently, one groups by "
                "size and one by whoever's turn it is", "cause": "KC-012"},
     {"answer": "The shelf label only gives a count, not which edge "
                "belongs to which size", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Unfold every set and check it is complete and fits a bed "
             "you still own. The flat sheet whose fitted half vanished, "
             "fitted sheets with slack elastic that pop off a corner at "
             "three in the morning, and towels that smell sour an hour "
             "after drying all leave.",
   "victory": "Every set on the shelf is complete, fits a bed you still "
              "own, and no towel carries a sour smell.",
  },
 },
 "Cleaning Equipment Zone": {
  "frictions": [
   {"symptom": "The vacuum with the split hose has been standing here "
               "for months because throwing out a machine that mostly "
               "works feels wasteful.",
    "branches": [
     {"answer": "I keep meaning to order the part and never quite do it",
      "cause": "RC-015"},
     {"answer": "There's no date attached to the repair, so 'later' has "
                "no deadline", "cause": "KC-009"},
     {"answer": "It's stood there so long I've stopped seeing it as "
                "broken, just as 'the other vacuum'", "cause": "RC-017"},
    ]},
   {"symptom": "A broom handle has slid down the wall again and is "
               "lying across the doorway instead of hanging from its "
               "clip.",
    "branches": [
     {"answer": "The clip is the wrong size for this handle so it never "
                "really holds", "cause": "KC-007"},
     {"answer": "The clip sits at an awkward height, so leaning the "
                "handle in the corner is just easier", "cause": "KC-006"},
     {"answer": "Nobody agreed that leaning it in the corner still "
                "counts as put away", "cause": "KC-008"},
    ]},
   {"symptom": "A damp mop head is resting against the vacuum's own "
               "cord at the back of this closet, both shut behind a "
               "closed door.",
    "branches": [
     {"answer": "There's nowhere else in the closet a wet mop head can "
                "hang to dry first", "cause": "KC-002"},
     {"answer": "Nobody checks the cord for cracks before it goes back, "
                "wet or dry", "cause": "RC-013"},
     {"answer": "It goes back wet because nothing prompts letting it "
                "dry outside the closet first", "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Stand every handle up and look at the working end. Brooms "
             "with splayed bristles that push dust rather than gather "
             "it, the mop head that no longer twists off its plate, and "
             "the old vacuum you keep for parts you have never once "
             "harvested all go out this week.",
   "victory": "Every remaining tool has a working end, and nothing is "
              "being kept for parts that were never actually used.",
  },
 },
 "Cleaning Supply Zone": {
  "frictions": [
   {"symptom": "A bottle of bleach sits on the same shelf as an "
               "ammonia-based glass cleaner, both within reach from the "
               "hallway floor.",
    "branches": [
     {"answer": "Nobody sorted this shelf by what's safe to store "
                "together, only by what fits", "cause": "KC-010"},
     {"answer": "The latch that used to keep small kids out broke "
                "months ago and was never replaced", "cause": "RC-015"},
     {"answer": "The two bottles have sat side by side so long the "
                "mismatch doesn't register anymore", "cause": "RC-017"},
    ]},
   {"symptom": "A row of aerosol cans and a solvent-based spray sit "
               "against the closet wall that backs onto the boiler, on "
               "the same shelf they've always used.",
    "branches": [
     {"answer": "These cans have always gone on this shelf, so nobody "
                "questioned whether it's actually the safe spot",
      "cause": "RC-017"},
     {"answer": "Nobody's ever traced which wall of this closet backs "
                "onto the boiler", "cause": "RC-013"},
     {"answer": "The coolest shelf in this closet is already full of "
                "something else, so the aerosols default to whatever's "
                "left", "cause": "KC-007"},
    ]},
   {"symptom": "Four glass cleaners and three floor sprays, each bottle "
               "a third full, crowd this shelf because you can't tell "
               "what's already here before buying another.",
    "branches": [
     {"answer": "You can't see the fill level from the doorway, so a "
                "new one seems safer than trusting the old",
      "cause": "KC-005"},
     {"answer": "There's no rule that says one open bottle per job, so a "
                "new bottle just joins the others", "cause": "KC-008"},
     {"answer": "The shelf holds more of everything than any one job "
                "actually needs", "cause": "KC-001"},
    ]},
  ],
  "first_15": {
   "action": "Line every bottle up on the hallway floor. Anything "
             "decanted into an unmarked spray bottle gets disposed of "
             "according to its own instructions, and the specialty "
             "cleaner bought for one stain years ago goes with it. Only "
             "identical products get poured together.",
   "victory": "Every bottle on the shelf is in its own original, "
              "labeled container, and no two different products have "
              "been mixed.",
  },
 },
 "Paper and Household Backstock": {
  "frictions": [
   {"symptom": "A warehouse pack of paper towels bought on a deal is "
               "too big to fit in its bin, so it sits blocking the "
               "shelf instead.",
    "branches": [
     {"answer": "There was no written maximum before the deal, so "
                "nothing stopped you buying it", "cause": "KC-008"},
     {"answer": "The bulk price felt like a saving even though it's "
                "more than the shelf's job needs", "cause": "KC-001"},
     {"answer": "You can't see how much is already on the shelf before "
                "you buy more", "cause": "KC-005"},
    ]},
   {"symptom": "A pack of bulbs at the back of this shelf is for a "
               "fitting the house replaced with LED two years ago, and "
               "nobody noticed until now.",
    "branches": [
     {"answer": "Nothing gets dated or labeled with the fitting when it "
                "arrives, so an outdated pack looks the same as a "
                "current one", "cause": "KC-011"},
     {"answer": "The oldest stock is buried behind the newest because "
                "new stock goes in at the front", "cause": "KC-009"},
     {"answer": "This shelf gets restocked but never audited, so it "
                "just accumulates", "cause": "RC-013"},
    ]},
   {"symptom": "Loose AAA batteries have rolled off a low shelf and are "
               "sitting on the closet floor at a small child's eye "
               "level.",
    "branches": [
     {"answer": "Batteries get tipped in loose instead of standing "
                "upright in a tray, so a knock sends them rolling",
      "cause": "KC-008"},
     {"answer": "This bin sits low enough for a small child to reach "
                "without help", "cause": "KC-010"},
     {"answer": "Nobody's swept this shelf floor since the last time "
                "this happened", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Take the lot out. Loose batteries you cannot vouch for, "
             "bulbs for fittings you replaced when you went over to "
             "LED, and the bulk paper towel pack too big to lift down "
             "alone all leave now.",
   "victory": "Every battery is in its original pack, every bulb fits a "
              "fitting the house still uses, and nothing on the shelf "
              "is too heavy to lift down alone.",
  },
 },
 "Seasonal and Guest Zone": {
  "frictions": [
   {"symptom": "A sealed bin has survived a house move and two closet "
               "reshuffles, and nobody can say what's actually inside "
               "it without opening it.",
    "branches": [
     {"answer": "It's easier to keep moving it than to open it and "
                "decide", "cause": "RC-015"},
     {"answer": "It was labeled 'misc' when it was packed, and 'misc' "
                "hasn't been questioned since", "cause": "KC-008"},
     {"answer": "It's been sitting there so long it just reads as "
                "storage, not as a thing to deal with", "cause": "RC-017"},
    ]},
   {"symptom": "Getting the good decorations down means standing on a "
               "hallway chair and reaching overhead, because there's no "
               "step stool kept in this closet.",
    "branches": [
     {"answer": "There's nowhere in this closet a stool actually lives, "
                "so whatever's nearby gets used instead", "cause": "KC-006"},
     {"answer": "The heaviest bins ended up on the top shelf because "
                "that's where there was room when they were packed",
      "cause": "KC-002"},
     {"answer": "Nobody re-checked shelf heights after the last time "
                "someone needed a chair to reach one", "cause": "RC-013"},
    ]},
   {"symptom": "A guest pillow has gone flat and yellowed inside its "
               "bin, and nobody noticed until it came out for an actual "
               "guest.",
    "branches": [
     {"answer": "The bin only gets opened right before a guest arrives, "
                "so a tired pillow is never caught early", "cause": "KC-009"},
     {"answer": "There's no date on the bin telling you how long that "
                "pillow has actually been in there", "cause": "KC-008"},
     {"answer": "A flat, yellowed pillow still looks like a stored "
                "pillow from the outside of a sealed bin", "cause": "KC-005"},
    ]},
  ],
  "first_15": {
   "action": "Every lid comes off, on the floor, in daylight. "
             "Decorations for a tree you no longer put up, the guest "
             "pillow gone flat and yellow, and the bin marked \"misc\" "
             "whose contents you cannot name without looking all go.",
   "victory": "Every remaining bin can be named without opening it, and "
              "nothing inside is flat, yellowed, or for a tradition you "
              "no longer keep.",
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
 ("Linen Shelf Zone", "HCF-001", "THE GOOD SET YOU NEVER PUT ON A BED",
  "a noticeably nicer folded sheet set sitting at the very front of a "
  "linen shelf, visibly untouched compared to the worn everyday sets "
  "stacked behind it"),
 ("Linen Shelf Zone", "HCF-002", "THE STACK TALLER THAN YOUR FOREARM",
  "a folded towel stack on a linen shelf rising well above forearm "
  "height, the stack visibly leaning and about to topple"),
 ("Linen Shelf Zone", "HCF-003", "THE GUEST SIZE HIDING AMONG THE EVERYDAY SETS",
  "a folded sheet set of a different, larger size sitting wedged among "
  "a row of everyday-sized sheet sets on a linen shelf, no visible way "
  "to tell them apart at a glance"),

 ("Cleaning Equipment Zone", "HCF-004", "THE VACUUM YOU KEEP MEANING TO FIX",
  "an older vacuum cleaner with a visibly split hose standing in a "
  "cleaning closet corner, parked apart from a working vacuum inside "
  "its own taped outline"),
 ("Cleaning Equipment Zone", "HCF-005", "THE HANDLE ACROSS THE DOORWAY",
  "a broom handle fallen across the floor of an open closet doorway, "
  "its wall clip visible standing empty above it"),
 ("Cleaning Equipment Zone", "HCF-006", "THE DAMP MOP AGAINST THE CORD",
  "a damp mop head resting directly against a coiled vacuum cord at the "
  "back of a closed cleaning closet"),

 ("Cleaning Supply Zone", "HCF-008", "BLEACH BESIDE THE AMMONIA CLEANER",
  "a bottle of bleach standing directly beside an ammonia-based glass "
  "cleaner on a low cleaning supply shelf within reach from the hallway "
  "floor"),
 ("Cleaning Supply Zone", "HCF-009", "THE AEROSOLS AGAINST THE WARM WALL",
  "a row of aerosol cans and a solvent-based spray bottle standing "
  "against a closet wall, positioned close to a household boiler "
  "visible on the other side"),
 ("Cleaning Supply Zone", "HCF-007", "ELEVEN BOTTLES, EACH A THIRD FULL",
  "a crowded cleaning supply shelf holding several duplicate glass "
  "cleaner and floor spray bottles, each visibly only partly full"),

 ("Paper and Household Backstock", "HCF-010", "THE WAREHOUSE PACK THAT WON'T FIT THE BIN",
  "an oversized shrink-wrapped bulk pack of paper towels wedged "
  "sideways across a backstock shelf, blocking the bins around it"),
 ("Paper and Household Backstock", "HCF-011", "THE BULB PACK FOR A FITTING THAT'S GONE",
  "a dusty, undated pack of incandescent bulbs sitting at the back of a "
  "backstock shelf behind newer LED bulb packs"),
 ("Paper and Household Backstock", "HCF-012", "LOOSE BATTERIES AT A CHILD'S EYE LEVEL",
  "several loose AAA batteries scattered across a low closet floor near "
  "the doorway, at the exact height a small child would notice them"),

 ("Seasonal and Guest Zone", "HCF-013", "THE BIN YOU'VE MOVED THREE TIMES WITHOUT OPENING",
  "a sealed, unlabeled storage bin sitting on an upper closet shelf, "
  "visibly older and more battered than the bins around it"),
 ("Seasonal and Guest Zone", "HCF-014", "REACHING FROM A HALLWAY CHAIR",
  "a hallway chair pulled up beside an open closet, positioned beneath "
  "a heavy bin sitting on the topmost shelf with no step stool anywhere "
  "in view"),
 ("Seasonal and Guest Zone", "HCF-015", "THE PILLOW THAT WENT FLAT INSIDE THE BIN",
  "a visibly flat, yellowed pillow lying inside an open storage bin on "
  "a closet shelf, undated and indistinguishable from the sealed bins "
  "around it"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, hall-closet-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a cleaning supply shelf crowded with far more partly-used "
           "bottles than a single job would ever need",
 "KC-002": "a heavy storage bin sitting on whatever shelf had room when "
           "it was packed, no dedicated spot cleared for it",
 "KC-005": "a sealed opaque storage bin on a closet shelf giving no "
           "hint of what is inside it",
 "KC-006": "a hallway chair standing in for a step stool beneath a "
           "high closet shelf, no stool anywhere in the closet itself",
 "KC-007": "a wall clip too small for the broom handle it is meant to "
           "hold, the handle slipping free of it",
 "KC-008": "a bare shelf edge in a closet with no dated card or count "
           "marker anywhere on it",
 "KC-009": "a vacuum with a split hose standing untouched in a closet "
           "corner, no repair date marked anywhere on it",
 "KC-010": "a bottle of bleach standing directly beside an "
           "ammonia-based cleaner on a shelf within a small child's "
           "reach",
 "KC-011": "an undated pack of bulbs sitting at the back of a "
           "backstock shelf for a fitting the house no longer uses",
 "KC-012": "two differently folded stacks of the same linen sitting "
           "side by side on one shelf, one style clearly not matching "
           "the other",
 "RC-013": "an unrefilled bin sitting on a closet shelf at the end of "
           "the day, no single person's name attached to it",
 "RC-014": "a noticeably nicer sheet set sitting untouched at the "
           "front of a linen shelf, visibly never used",
 "RC-015": "a sealed, undated storage bin sitting on a closet shelf "
           "that has clearly been moved more than once without ever "
           "being opened",
 "RC-017": "a vacuum with a split hose standing so long in its closet "
           "corner that it now blends in among the working equipment "
           "around it",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Linen Shelf Zone": [
  "Run a hand along the shelf lip where dust drifts down onto the "
  "folded stacks and wipe it clear before it settles onto clean linen.",
  "Check the underside of one shelf bracket for dust that clings and "
  "drops onto the stack below it.",
  "Shake out one folded set and refold it to the same width as the "
  "rest, catching a musty note before it seals back into the stack.",
 ],
 "Cleaning Equipment Zone": [
  "Wipe the vacuum cord down its full length and check for a cracked "
  "patch of insulation near the plug.",
  "Take the mop head off its handle and rinse it clean before it hangs "
  "back up damp.",
  "Wipe the wall clips themselves where grime builds up behind the "
  "tool nobody moves to check.",
 ],
 "Cleaning Supply Zone": [
  "Wipe the outside of one caddy down where sprayed product drips and "
  "dries into a film nobody notices.",
  "Check the latch or barrier keeping this shelf out of reach still "
  "closes fully.",
  "Wipe the shelf edge under the bottles where a ring of residue "
  "collects unseen.",
 ],
 "Paper and Household Backstock": [
  "Check the fill level in the clear toilet roll bin against its own "
  "minimum card.",
  "Wipe the shelf edge label clean so its minimum and maximum stay "
  "legible from across the room.",
  "Turn the battery tray so every size is readable without lifting a "
  "single pack out.",
 ],
 "Seasonal and Guest Zone": [
  "Check one bin's label still names what's inside and when it was "
  "last closed.",
  "Wipe the shelf map taped inside the door so it stays legible for "
  "whoever opens this closet next.",
  "Feel the zip bag holding the guest pillows for any damp before it "
  "goes back on the shelf.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-closet actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "HCA-001", "zone": "Linen Shelf Zone",
  "title": "CLEAR THE SHELF AND CHECK EVERY SET",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Unfold every set and check it is complete and fits a bed you "
          "still own, so nothing half-usable survives on a technicality.",
  "why": "A set with a missing half or slack elastic only reveals "
         "itself at three in the morning, the worst possible time to "
         "find out.",
  "inputs": ["a bin bag"],
  "steps": [
   "Unfold every set and check it is complete and fits a bed you still "
   "own. The flat sheet whose fitted half vanished, fitted sheets with "
   "slack elastic that pop off a corner at three in the morning, and "
   "towels that smell sour an hour after drying all leave.",
   "Set aside anything still good but unlikely to get used, to give "
   "away rather than bin.",
   "Re-nest each surviving set inside its own matching pillowcase "
   "before it goes back."],
  "causes": ["RC-014", "RC-015"],
  "victory": "Every set on the shelf is complete, fits a bed you still "
             "own, and no towel carries a sour smell.",
  "next": "HCS-001",
  "art": "a linen shelf mid-clear with a matched set half-nested into "
         "its own pillowcase, a bin bag sitting on the floor beside it"},

 {"id": "HCA-002", "zone": "Linen Shelf Zone",
  "title": "LABEL EVERY STACK AND SET THE HEIGHT LIMIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Write each bed size on the shelf edge under its stack, and "
          "keep every stack no taller than a forearm.",
  "why": "A label-less stack forces a guess at bedtime, and a stack "
         "taller than a forearm is a fall waiting on the next towel "
         "pulled from the bottom.",
  "inputs": ["a marker", "adhesive shelf-edge labels"],
  "steps": [
   "Group sets by the bed they fit, queen and king low, guest blankets "
   "on top.",
   "Write the bed size and set count on the shelf edge under each "
   "stack.",
   "Split any stack taller than a forearm into two shorter ones."],
  "causes": ["KC-008", "KC-002", "KC-012"],
  "victory": "Every stack is labeled with its bed size, and no stack "
             "stands taller than a forearm.",
  "next": "HCA-001",
  "art": "a hand marking a bed size onto a shelf-edge label under a "
         "folded linen stack no taller than a forearm"},

 {"id": "HCA-003", "zone": "Cleaning Equipment Zone",
  "title": "STAND EVERY HANDLE UP AND CHECK THE WORKING END",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Stand every handle up and look at the working end, so "
          "nothing kept only for parts survives another season.",
  "why": "A splayed broom pushes dust instead of gathering it, and a "
         "vacuum kept for parts never harvested is just standing where "
         "the working one needs to stand.",
  "inputs": ["a bin bag"],
  "steps": [
   "Stand every handle up and look at the working end. Brooms with "
   "splayed bristles that push dust rather than gather it, the mop "
   "head that no longer twists off its plate, and the old vacuum you "
   "keep for parts you have never once harvested all go out this "
   "week.",
   "Wrap any surviving cord neatly and zip loose attachments into one "
   "bag.",
   "Recycle anything that goes, and note the repair each surviving "
   "tool actually needs."],
  "causes": ["RC-015", "RC-017"],
  "victory": "Every remaining tool has a working end, and nothing is "
             "being kept for parts that were never actually used.",
  "next": "HCS-002",
  "art": "a hand standing a broom up to check its bristles, a splayed "
         "broom set apart on the floor beside a bin bag"},

 {"id": "HCA-004", "zone": "Cleaning Equipment Zone",
  "title": "HANG EVERY HANDLE AND TAPE THE VACUUM'S SPOT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Fit a rail so every handle hangs bristles-up, and tape a "
          "floor outline for the vacuum with a repair date on anything "
          "still broken.",
  "why": "A handle left standing on the floor bends and re-soils what "
         "you just cleaned, and a repair with no date attached never "
         "actually happens.",
  "inputs": ["a wall rail or clips", "tape for the floor outline",
             "masking tape and a marker for the repair date"],
  "steps": [
   "Fit a rail or clips at a height that clears the floor, and hang "
   "every handle bristles or mop-head up.",
   "Tape a floor outline for the vacuum and park it there after every "
   "use.",
   "If anything still needs a repair, write the date on masking tape "
   "stuck to the body."],
  "causes": ["KC-006", "KC-009", "KC-007"],
  "victory": "Every handle hangs clear of the floor, the vacuum parks "
             "inside its taped outline, and any repair still needed "
             "carries a written date.",
  "next": "HCA-003",
  "art": "a broom, mop and duster hanging handle-down from wall clips "
         "above a taped floor outline holding a parked vacuum"},

 {"id": "HCA-005", "zone": "Cleaning Supply Zone",
  "title": "LINE UP EVERY BOTTLE AND DISPOSE OF THE UNMARKED",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Line every bottle up on the hallway floor and only pour "
          "identical products together, so nothing unmarked survives "
          "unidentified.",
  "why": "A decanted, unmarked bottle is a real hazard the moment "
         "somebody other than you reaches for it.",
  "inputs": ["gloves", "a bin bag"],
  "steps": [
   "Line every bottle up on the hallway floor. Anything decanted into "
   "an unmarked spray bottle gets disposed of according to its own "
   "instructions, and the specialty cleaner bought for one stain years "
   "ago goes with it. Only identical products get poured together.",
   "Group only identical products together before anything goes back.",
   "Set aside anything unlabeled for safe disposal per its own "
   "instructions."],
  "causes": ["KC-005", "KC-001"],
  "victory": "Every bottle on the shelf is in its own original, "
             "labeled container, and no two different products have "
             "been mixed.",
  "next": "HCS-003",
  "art": "a row of cleaning bottles lined up on a hallway floor, each "
         "one wearing its own original label"},

 {"id": "HCA-006", "zone": "Cleaning Supply Zone",
  "title": "BUILD TWO CADDIES AND SEPARATE BLEACH FROM AMMONIA",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Build a bathroom caddy and a kitchen caddy, and move bleach "
          "and ammonia products onto separate shelves out of a child's "
          "reach.",
  "why": "Bleach and ammonia stored together is a real hazard, and a "
         "caddy per room means carrying the whole job in one hand "
         "instead of walking back twice.",
  "inputs": ["two caddies", "adhesive end labels"],
  "steps": [
   "Sort bleach products onto one shelf and ammonia products onto a "
   "separate one.",
   "Build a bathroom caddy and a kitchen caddy, gloves and cloths "
   "riding inside each.",
   "Move the whole zone up out of a small child's reach, or fit a "
   "latch."],
  "causes": ["KC-010", "KC-008"],
  "victory": "Bleach and ammonia sit on separate shelves, two labeled "
             "caddies exist, and the zone sits out of a small child's "
             "reach.",
  "next": "HCA-005",
  "art": "two labeled cleaning caddies, one marked for the bathroom and "
         "one for the kitchen, standing on separate shelves from a row "
         "of bleach bottles"},

 {"id": "HCA-007", "zone": "Paper and Household Backstock",
  "title": "TAKE THE LOT OUT AND CHECK EVERY PACK",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take the lot out and check every battery, bulb and bulk "
          "pack, so nothing unusable keeps its shelf space.",
  "why": "A battery you cannot vouch for and a bulb for a fitting you "
         "no longer own are both taking up space a real reserve needs.",
  "inputs": ["a bin bag"],
  "steps": [
   "Take the lot out. Loose batteries you cannot vouch for, bulbs for "
   "fittings you replaced when you went over to LED, and the bulk "
   "paper towel pack too big to lift down alone all leave now.",
   "Recycle any pack for a fitting the house no longer uses.",
   "Set the bulk paper towel pack down at waist height, not overhead."],
  "causes": ["KC-011", "KC-001"],
  "victory": "Every battery is in its original pack, every bulb fits a "
             "fitting the house still uses, and nothing on the shelf "
             "is too heavy to lift down alone.",
  "next": "HCS-004",
  "art": "a backstock shelf cleared onto the floor, loose batteries set "
         "apart from bulb packs still in their original boxes"},

 {"id": "HCA-008", "zone": "Paper and Household Backstock",
  "title": "SET A MINIMUM AND MAXIMUM ON EVERY BIN",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Write a minimum and maximum on the shelf edge for toilet "
          "roll, bulbs and batteries, and date every pack as it "
          "arrives.",
  "why": "A shelf with no written limit is where an emergency trip or "
         "a shelf-blocking bulk buy both quietly happen.",
  "inputs": ["a marker", "adhesive shelf-edge cards"],
  "steps": [
   "Set a clear bin for toilet roll and write a minimum and maximum on "
   "the shelf edge.",
   "Sort bulbs into a labeled bin by fitting, and stand batteries "
   "upright in a shallow tray by size.",
   "Turn every bin label to face the door."],
  "causes": ["KC-008", "KC-005"],
  "victory": "Every bin carries a minimum and maximum on the shelf "
             "edge, and every label faces the door.",
  "next": "HCA-007",
  "art": "a small dated card fixed to a backstock shelf edge reading a "
         "minimum and maximum count, bin labels turned to face forward"},

 {"id": "HCA-009", "zone": "Seasonal and Guest Zone",
  "title": "OPEN EVERY LID ON THE FLOOR IN DAYLIGHT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Open every lid on the floor in daylight and name what's "
          "actually inside, so nothing unnamed keeps its bin.",
  "why": "A bin nobody can name without opening it is not storage, it "
         "is a decision that keeps getting postponed.",
  "inputs": ["a bin bag", "daylight or a bright lamp"],
  "steps": [
   "Every lid comes off, on the floor, in daylight. Decorations for a "
   "tree you no longer put up, the guest pillow gone flat and yellow, "
   "and the bin marked \"misc\" whose contents you cannot name without "
   "looking all go.",
   "For anything you keep, name the occasion in the next twelve months "
   "you'll use it.",
   "Reseal only what you named an occasion for."],
  "causes": ["RC-015", "RC-017"],
  "victory": "Every remaining bin can be named without opening it, and "
             "nothing inside is flat, yellowed, or for a tradition you "
             "no longer keep.",
  "next": "HCS-005",
  "art": "several storage bins opened on a closet floor in daylight, "
         "their lids set aside while contents are sorted into keep and "
         "go piles"},

 {"id": "HCA-010", "zone": "Seasonal and Guest Zone",
  "title": "LABEL EVERY BIN AND MAP THE SHELF",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Label each bin with its contents and the month it was last "
          "closed, and tape a shelf map inside the door.",
  "why": "A shelf map means someone else can find the guest bedding "
         "without unstacking the whole shelf to look.",
  "inputs": ["a marker", "adhesive labels", "tape",
             "paper for the map"],
  "steps": [
   "Seal guest pillows inside a zip bag.",
   "Label each bin with its contents and the month it was last "
   "closed.",
   "Tape a simple shelf map inside the closet door showing which bin "
   "sits where."],
  "causes": ["KC-002", "KC-006"],
  "victory": "Every bin is labeled with its contents and last-closed "
             "month, and a shelf map is taped inside the door.",
  "next": "HCA-009",
  "art": "a labeled storage bin standing on a shelf beside a small "
         "paper map taped to the inside of a closet door"},

 {"id": "HCA-011", "zone": None,
  "title": "THE FULL CLOSET SAFETY AND HEIGHT WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every shelf checking what sits above a safe reach, "
          "whether a stool actually lives in the closet, and whether "
          "bleach and ammonia are kept apart.",
  "why": "A heavy bin overhead and two chemicals stored together both "
         "hide until someone tests for them on purpose.",
  "inputs": ["a step stool", "a cloth for the awkward spots"],
  "steps": [
   "Check every shelf for anything a small child could reach that "
   "shouldn't be reachable.",
   "Confirm a step stool actually lives inside this closet, not "
   "somewhere else in the house.",
   "Confirm bleach and ammonia products sit on separate shelves."],
  "causes": ["KC-006", "KC-010"],
  "victory": "Nothing unsafe sits within a small child's reach, a "
             "working stool lives in the closet, and bleach and "
             "ammonia sit apart.",
  "next": "HCA-010",
  "art": "a step stool standing inside an open hall closet beneath a "
         "high shelf, bleach and ammonia products visible on separate "
         "shelves below it"},

 {"id": "HCA-012", "zone": None,
  "title": "THE WEEKLY GAP-AND-DATE PASS",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "Walk every bin and shelf reading what's low or undated "
          "before the shopping list gets written, and name who is "
          "doing it this week.",
  "why": "Nothing in this closet forces the issue by running out on "
         "schedule, so it fails silently unless somebody is actually "
         "assigned to look.",
  "inputs": ["the shopping list"],
  "steps": [
   "Walk the backstock and linen shelves and read the gaps before the "
   "list gets written.",
   "Say out loud, or write down, whose turn it is to do this pass this "
   "week.",
   "Add anything genuinely missing to the list on the spot."],
  "causes": ["RC-013"],
  "victory": "The shelves were read for gaps before this week's list "
             "was written, and one named person did it.",
  "next": "HCA-011",
  "art": "a hand writing an item onto a shopping list while standing "
         "in front of an open hall closet shelf with a visible gap"},

 {"id": "HCA-013", "zone": None,
  "title": "THE MONTHLY LABEL AND LIMIT AUDIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Once a month, check every written minimum, maximum and date "
          "against what's actually on the shelves, and correct any "
          "that have drifted.",
  "why": "A limit written once and never revisited stops meaning "
         "anything the first time a good deal tempts you past it.",
  "inputs": ["a marker", "this month's receipts if you kept them"],
  "steps": [
   "Compare the count on each backstock line against its written "
   "minimum and maximum.",
   "Check every stored date is still legible and relabel anything "
   "faded.",
   "Correct any label that has drifted from what's actually true."],
  "causes": ["KC-008", "KC-009"],
  "victory": "Every limit sits checked this month, and every date on "
             "the shelf is legible.",
  "next": "HCA-012",
  "art": "a hand comparing a shelf's item count against a small dated "
         "card fixed to a backstock shelf edge"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a hall closet, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("HCE-001", "THE LAST-MINUTE BED CHANGE",
  "A guest is arriving in twenty minutes and the right-sized bed linen "
  "has to answer immediately.",
  ["HCZ-001"],
  "A labeled, complete set for that exact bed size comes off the shelf "
  "in one grab, no unfolding others to check.",
  "If you had to unfold more than one stack to find a set that "
  "actually fit, the sizing and labeling slipped. Draw HCA-002.",
  "a hand pulling a labeled, complete sheet set from a linen shelf in "
  "one motion, a bed-size card visible on the shelf edge beneath it"),
 ("HCE-002", "THE SPILL THAT NEEDS THE VACUUM NOW",
  "Something breaks in the kitchen and the vacuum has to come out and "
  "work, right now, with no time for a fight.",
  ["HCZ-002"],
  "The vacuum rolls out of its outline, cord already wrapped, every "
  "attachment already in its bag.",
  "If you had to hunt for an attachment or untangle the cord first, "
  "the reset after the last use slipped. Draw HCA-004.",
  "a hand pulling a vacuum cleaner out of a taped floor outline in a "
  "cleaning closet, its cord already wrapped and an attachment bag "
  "already clipped to the handle"),
 ("HCE-003", "THE TODDLER LOOSE IN THE HALLWAY",
  "A toddler gets ten unsupervised seconds near this closet door "
  "before anyone notices.",
  ["HCZ-003"],
  "Nothing on this shelf is within their reach, and nothing unlabeled "
  "is within reach either.",
  "If a bottle was within reach or unlabeled, the height and labeling "
  "rules slipped. Draw HCA-006.",
  "a closet door standing open at child height with an empty lower "
  "shelf, cleaning products all visible only on a shelf well above "
  "reach"),
 ("HCE-004", "THE SURPRISE POWER CUT",
  "The power goes out at nine at night and the household needs "
  "working batteries, fast, with no time to test three dead ones "
  "first.",
  ["HCZ-004"],
  "The battery tray gives up the right size in one glance, no "
  "digging, and it works.",
  "If the battery you grabbed was already dead or the right size was "
  "impossible to find, the sorting and dating slipped. Draw HCA-008.",
  "a hand lifting a labeled battery pack from a shallow upright tray "
  "in a backstock shelf, sizes clearly visible without moving anything "
  "else"),
 ("HCE-005", "THE UNANNOUNCED OVERNIGHT GUEST",
  "A guest is staying tonight, unannounced, and the guest bedding has "
  "to come out of storage in under five minutes.",
  ["HCZ-005"],
  "The shelf map sends you straight to the right bin, and the pillow "
  "inside is sealed, plump and fresh.",
  "If you had to open two or three bins to find the right one, or the "
  "pillow was flat, the labeling and the map slipped. Draw HCA-010.",
  "a hand checking a small paper map taped inside a closet door, "
  "pointing directly at one labeled bin holding sealed guest pillows"),
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
        "tagline": "FIVE SHELVES OF EVERYTHING THAT HAD NOWHERE ELSE TO "
                   "GO.",
        "objective": "The hall closet is where everything that had to "
                     "go somewhere ended up. This card is the map and "
                     "the order.",
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
        "safety_first": "Do HCA-011 The Full Closet Safety And Height "
                        "Walk before any rebuild. It takes thirty "
                        "minutes and covers every shelf's height, the "
                        "stool, and whether bleach and ammonia are kept "
                        "apart.",
        "related": {"contents": "HCZ-001 to HCZ-005, HCF-001 to HCF-015, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, HCA-001 to HCA-013, "
                                 "HCS-001 to HCS-005, HCE-001 to HCE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole hall "
                           "closet in its settled state, linen shelves, "
                           "cleaning equipment, a cleaning supply "
                           "caddy, a backstock shelf and a seasonal "
                           "storage shelf all visible in one frame",
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
