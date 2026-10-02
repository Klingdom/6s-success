#!/usr/bin/env python3
"""
Build the Pantry deck: 57 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: seven rooms already carry a full diagnosis layer
and a shipped deck (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home
Office, Garage, Stair Landing). Pantry is the next room built the same way:
rich, hand-authored Manual content for all five zones (purpose,
done_looks_like, passes, the_call, watch_for, leave_behind, shine_detail),
but no diagnosis layer and no deck until this file. It adds that layer to
content/manual/source/content.json (fifteen frictions, forty-five branches,
five first_15 actions) and builds the deck straight off it, the same shape
ops/cardtext/build_entryway_deck.py already uses for its own five-zone room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
fifteen frictions (symptom and every branch to a root cause) are likewise
derived straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the ten
zone-linked action cards, the three whole-pantry actions, the event cards,
the micro quests, and the room card. The root causes are not reauthored:
they are the same frozen vocabulary in ops/root_causes.py that every other
room's deck already uses, so a household owning more than one deck keeps one
diagnosis pile rather than several (DECK-GAME-DESIGN.md 4.3). Thirteen of
the seventeen shared ids are reachable from this room's real frictions,
counted honestly from the branches actually written below, not chosen first
and filled in: KC-001, KC-002, KC-003, KC-005, KC-006, KC-008, KC-009,
KC-010, KC-012, RC-013, RC-015, RC-016, RC-017. KC-004, KC-007, KC-011 and
RC-014 are not reachable because nothing in this room's real diagnosis
branches to them, and that is a true statement about this room's own
frictions, not an oversight; nothing pads the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Pantry ships as a free typeset page, the same stage every prior room in this
line shipped at before any print-on-demand decision existed (DECK-GAME-
DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it does not
apply here; D-027 already settled that trimming or filling a room's honest
count to chase a print tier is the wrong move). The budget below is the
same shape as Entryway, the other five-zone room in this line: five real
zones, fifteen frictions (three per zone), thirteen reachable root causes,
thirteen action cards (two per zone plus three whole-pantry), five standard
cards and five event cards. 57 cards in total, not padded or trimmed to
match any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_pantry_deck.py
Out:  ops/cardtext/pantry-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "pantry-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Pantry"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 5, "FRICTION CARD": 15,
          "ROOT CAUSE CARD": 13, "ACTION CARD": 13, "STANDARD CARD": 5,
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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-005", "KC-006", "KC-008",
             "KC-009", "KC-010", "KC-012", "RC-013", "RC-015", "RC-016",
             "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Dry Goods Shelves": {
  "id": "PNZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE BLOCK OF STAPLES. ONE LABEL EACH. READABLE FROM THE DOORWAY.",
  "callouts": [
   "Rice, pasta and oats standing together as one labeled block at chest height",
   "Breakfast cereal boxes standing together as their own block",
   "Every opened bag sealed inside a matching container",
   "A handwritten date visible on each container's label",
   "The fill level inside every container readable without lifting it",
   "A two-step stool standing inside the pantry beneath the top shelf",
  ],
  "art": ("a pantry shelf at chest height holding matching labeled "
          "containers of rice, pasta and oats standing together as one "
          "block, a separate block of cereal boxes beside them, each "
          "container's label showing a dated sticker, and a small "
          "two-step stool standing on the floor below"),
 },
 "Canned and Jarred Goods": {
  "id": "PNZ-002", "order": 2, "difficulty": 2,
  "tagline": "EVERY LABEL FACING OUT. NOTHING DENTED. THE OLDEST DATE UP FRONT.",
  "callouts": [
   "Cans standing in rows on a stepped riser, every label facing outward",
   "Tomatoes grouped in one row, beans in another, soup in a third",
   "No dented seam or domed lid visible on any can",
   "No jar standing hidden directly behind another jar",
   "The oldest-dated can or jar standing at the front of its row",
   "A clean, dry shelf edge with no sticky ring under any jar",
  ],
  "art": ("a pantry shelf with canned goods standing in labeled rows on "
          "a stepped riser, every label facing outward, tomatoes grouped "
          "separately from beans and soup, no can showing a dented seam "
          "or domed lid, and a clean dry shelf edge with no sticky "
          "residue"),
 },
 "Baking Zone": {
  "id": "PNZ-003", "order": 3, "difficulty": 3,
  "tagline": "ONE LIFT-OUT BIN. LEAVENERS DATED. THE ALLERGEN SHELF STANDS APART.",
  "callouts": [
   "Flour, sugar and brown sugar standing in sealed one-handed containers",
   "Baking powder, bicarbonate of soda and yeast together in one small dated box",
   "A single lift-out bin holding cutters, cases and piping tips",
   "A dedicated scoop and sealed container for nut flour standing apart at the end of the row",
   "No loose sprinkles rolling free on the shelf",
   "A washed scoop sitting inside the flour bin, not buried in the flour",
  ],
  "art": ("a pantry baking shelf with flour, sugar and brown sugar in "
          "sealed one-handed containers, a small dated box holding "
          "baking powder, bicarbonate of soda and yeast together, a "
          "lift-out bin of cutters and piping tips, and a separate "
          "sealed nut-flour container with its own scoop standing at "
          "the end of the row"),
 },
 "Snack and Lunch Zone": {
  "id": "PNZ-004", "order": 4, "difficulty": 2,
  "tagline": "ONE BIN AT CHILD HEIGHT. ONE LINE TO FILL IT TO. EVERY LID MATCHED.",
  "callouts": [
   "One open bin standing at child height",
   "A marked fill line visible inside the open bin",
   "A higher shelf holding the snacks that need an adult's yes",
   "Every reusable container with its own lid sitting on top of it",
   "Lunch bags and ice packs standing next to the containers",
   "No loose orphaned lid or lidless tub anywhere on the shelf",
  ],
  "art": ("a pantry shelf with an open snack bin at child height filled "
          "to a marked line, a higher shelf above holding snacks that "
          "need an adult, reusable lunch containers each with its own "
          "lid sitting on top, and lunch bags with ice packs standing "
          "beside them"),
 },
 "Backstock and Bulk Zone": {
  "id": "PNZ-005", "order": 5, "difficulty": 3,
  "tagline": "DATED ON ARRIVAL. A MAXIMUM ON THE EDGE. ONE ROW DEEP.",
  "callouts": [
   "Sacks of rice standing at or below waist height",
   "Cases of tinned tomatoes with the arrival month written on each one",
   "Packs of kitchen roll stored up high, off the floor",
   "A maximum number written on the shelf edge for each line",
   "The count on the shelf sitting at or under its written maximum",
   "Nothing stacked directly in front of anything else",
  ],
  "art": ("a pantry backstock area with sacks of rice and cases of "
          "tinned tomatoes standing at or below waist height, each case "
          "marked with its arrival month, light packs of kitchen roll "
          "stored higher up, a small dated sticker fixed to the shelf "
          "edge, and nothing stacked in front of anything else"),
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
 "Dry Goods Shelves": {
  "frictions": [
   {"symptom": "A bag you opened for one recipe two summers ago is still "
               "sitting up there, unlabeled, and you can't say when it "
               "was opened.",
    "branches": [
     {"answer": "It's not really clutter, it's a recipe I still mean to "
                "make again", "cause": "RC-015"},
     {"answer": "Nothing gets written on the bag the day it's opened, so "
                "there's no way to judge how old it really is",
      "cause": "KC-008"},
     {"answer": "I've walked past that shelf so many times it doesn't "
                "register as a problem anymore", "cause": "RC-017"},
    ]},
   {"symptom": "Two open bags of the same rice or oats turn up on the "
               "shelf at once, one pushed behind the other.",
    "branches": [
     {"answer": "New stock gets unpacked straight to the front instead of "
                "behind the open bag", "cause": "KC-009"},
     {"answer": "I buy a replacement before I actually check whether the "
                "open one is empty yet", "cause": "KC-005"},
     {"answer": "There's no rule everyone in the house follows for "
                "loading new stock in behind", "cause": "KC-008"},
    ]},
   {"symptom": "A glass grain jar sits above eye level on this shelf "
               "instead of at chest height where it belongs.",
    "branches": [
     {"answer": "There wasn't a clear place made for it at chest height "
                "so it ended up wherever there was room", "cause": "KC-002"},
     {"answer": "Reaching the top shelf safely means keeping a step stool "
                "in the pantry, and it's not there", "cause": "KC-006"},
     {"answer": "Nobody in the house is the one who checks this shelf for "
                "what's stored above eye level", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Bring down every bag and box on this shelf, open anything "
             "already opened, and smell the flour and the oats: stale, "
             "webbed, or bought for a recipe you have not cooked in "
             "months leaves today.",
   "victory": "Every opened bag is sealed in a labeled container or gone, "
              "and pasta, rice and oats stand together as one block.",
  },
 },
 "Canned and Jarred Goods": {
  "frictions": [
   {"symptom": "A can with a dented seam or a jar with a popped lid is "
               "still sitting on the shelf instead of already in the bin.",
    "branches": [
     {"answer": "I wasn't sure whether a small dent or a slightly domed "
                "lid really counts as spoiled", "cause": "KC-008"},
     {"answer": "It's tucked behind a row of other cans where nobody "
                "actually looks at it", "cause": "KC-005"},
     {"answer": "Nobody has checked this shelf for damaged cans in a "
                "long time; it's not really anyone's job", "cause": "RC-013"},
    ]},
   {"symptom": "Four jars of the same pasta sauce turn up when you "
               "finally take everything off the shelf.",
    "branches": [
     {"answer": "I keep buying it because I genuinely can't tell from a "
                "glance how many are already here", "cause": "KC-005"},
     {"answer": "Four of one thing is just how much ends up here between "
                "big shops, nobody's ever called it too many",
      "cause": "KC-001"},
     {"answer": "Whoever unpacks the shopping doesn't check the shelf "
                "before adding another one", "cause": "KC-009"},
    ]},
   {"symptom": "A shelf edge feels tacky where a honey jar or sauce lid "
               "has wept, and you only notice because of an ant.",
    "branches": [
     {"answer": "Reaching the sticky ring under that jar costs more "
                "effort than the rest of the shelf, so it gets skipped",
      "cause": "RC-016"},
     {"answer": "The sticky ring was there so long I stopped seeing it "
                "as something to fix", "cause": "RC-017"},
     {"answer": "Nothing tells you a jar has started weeping until the "
                "ants already have", "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Take every can and jar off the shelf, turn each one to "
             "find the date, and put anything dented, rusted, bulging or "
             "domed straight into the bin rather than back on the shelf.",
   "victory": "No dented, rusted, domed or bulging can or jar remains on "
              "the shelf, and every label faces out.",
  },
 },
 "Baking Zone": {
  "frictions": [
   {"symptom": "Baking powder or yeast has been sitting in the bin for a "
               "long time and nobody has actually tested whether it "
               "still works.",
    "branches": [
     {"answer": "There's no reminder built into anything that prompts a "
                "test before a bake", "cause": "KC-009"},
     {"answer": "The tin has no date on the lid, so there's no way to "
                "judge how old it really is", "cause": "KC-008"},
     {"answer": "I keep meaning to test it and use it up before I "
                "replace it, and never quite get to it", "cause": "RC-015"},
    ]},
   {"symptom": "The nut flour or sesame container shares a scoop with "
               "everything else on this shelf.",
    "branches": [
     {"answer": "Nobody ever agreed this container needs its own "
                "dedicated scoop", "cause": "KC-008"},
     {"answer": "It sits in the middle of the row instead of at the end "
                "where a hand would notice it's different",
      "cause": "KC-003"},
     {"answer": "Whoever's baking in a hurry just grabs whatever scoop "
                "is closest", "cause": "RC-013"},
    ]},
   {"symptom": "The lift-out baking bin comes back short a scoop, or the "
               "vanilla is missing, right when you're about to start a "
               "bake.",
    "branches": [
     {"answer": "Somebody borrowed from this bin for something that "
                "wasn't a bake, and it never got told to the person who "
                "baked", "cause": "RC-013"},
     {"answer": "There's no moment that resets the bin, it only gets "
                "noticed when a bake is already underway", "cause": "KC-009"},
     {"answer": "The bin holds more loose extras than a single bake "
                "actually needs, so something always drifts out of it",
      "cause": "KC-001"},
    ]},
  ],
  "first_15": {
   "action": "Test every leavener rather than guessing: a spoon of "
             "baking powder in hot water should fizz hard, and yeast in "
             "warm sugared water should foam. The dead ones go, along "
             "with any hardened brown sugar or grayed cocoa.",
   "victory": "Every leavener in the bin has been tested this week, and "
              "nothing dead or expired remains.",
  },
 },
 "Snack and Lunch Zone": {
  "frictions": [
   {"symptom": "The open snack bin sits below the marked fill line most "
               "mornings, well before the week is over.",
    "branches": [
     {"answer": "Nobody actually refills it to the line the evening "
                "before, it just gets remembered some nights and not "
                "others", "cause": "RC-013"},
     {"answer": "There's no clear rule for who tops it up when the "
                "lunchboxes come home", "cause": "KC-008"},
     {"answer": "Filling it happens whenever someone notices, not at a "
                "fixed moment in the evening", "cause": "KC-009"},
    ]},
   {"symptom": "A container comes back from the shelf with no matching "
               "lid, or a lid with nothing to close.",
    "branches": [
     {"answer": "Lids and containers get put away separately instead of "
                "paired the moment they're washed", "cause": "KC-002"},
     {"answer": "A stray lid or container has been sitting loose in the "
                "cupboard for a while and nobody's dealt with it",
      "cause": "RC-015"},
     {"answer": "It's been an orphaned lid for so long it just blends "
                "into the shelf now", "cause": "RC-017"},
    ]},
   {"symptom": "A hard sweet, a whole nut or a small round cheese sits "
               "in the open bin a two-year-old can reach.",
    "branches": [
     {"answer": "The bin's contents were chosen for the oldest child in "
                "the house, not the youngest who can actually reach it",
      "cause": "KC-012"},
     {"answer": "Nobody re-checked the bin's contents after a younger "
                "child started reaching the shelf", "cause": "RC-013"},
     {"answer": "It's a choking hazard at child height, which is a "
                "safety problem that outranks how convenient it is to "
                "grab", "cause": "KC-010"},
    ]},
  ],
  "first_15": {
   "action": "Match every lid to a container and bin the orphans in both "
             "directions, the lidless tubs and the lids for tubs that "
             "died. Pull any snack boxes with only a couple of bars "
             "rattling around and combine them.",
   "victory": "Every reusable container has its own lid sitting on it, "
              "and the open bin is filled to its marked line.",
  },
 },
 "Backstock and Bulk Zone": {
  "frictions": [
   {"symptom": "A second sack of rice or a twelve-pack nobody liked "
               "turns up when you finally clear the back of this zone.",
    "branches": [
     {"answer": "I bought it for the unit price without checking whether "
                "I'd actually used up the last one", "cause": "KC-001"},
     {"answer": "There's no written maximum for this item, so nothing "
                "stopped the extra one coming home", "cause": "KC-008"},
     {"answer": "It's a good deal I'm not ready to admit didn't work "
                "out, so it stays instead of moving on", "cause": "RC-015"},
    ]},
   {"symptom": "A case near the bottom of a stack shows a soft, damp "
               "corner instead of the crisp cardboard everything else "
               "has.",
    "branches": [
     {"answer": "Nobody has actually lifted and checked the underside of "
                "the bottom case in a while", "cause": "RC-013"},
     {"answer": "Checking underneath a stacked case means unstacking it "
                "first, so it doesn't happen often", "cause": "RC-016"},
     {"answer": "That corner is against an outside wall that sweats, and "
                "nothing routes stock away from it", "cause": "KC-003"},
    ]},
   {"symptom": "A case is stacked in front of another case of the same "
               "thing, so the older one at the back never gets pulled "
               "first.",
    "branches": [
     {"answer": "There's no arrangement that keeps this one row deep, so "
                "a new case just goes wherever there's floor space",
      "cause": "KC-008"},
     {"answer": "The gap left by the front case emptying isn't the "
                "trigger for pulling the one behind it forward, it just "
                "gets refilled from the front again", "cause": "KC-009"},
     {"answer": "I can't see behind the front row to know an older case "
                "is even back there", "cause": "KC-005"},
    ]},
  ],
  "first_15": {
   "action": "Open up the back of this zone and meet what you forgot "
             "you owned: any item you hold more than one genuine spare "
             "of moves forward into the working shelves this month or "
             "it leaves.",
   "victory": "Every remaining pack carries its arrival month, and "
              "nothing sits stacked in front of an older case of the "
              "same thing.",
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
 ("Dry Goods Shelves", "PNF-001", "THE BAG YOU OPENED TWO SUMMERS AGO",
  "an unlabeled half-used bag of flour pushed to the back of a pantry "
  "shelf behind a row of cereal boxes, no date or marking visible "
  "anywhere on it"),
 ("Dry Goods Shelves", "PNF-002", "TWO OPEN BAGS OF THE SAME THING",
  "two open bags of the same rice sitting side by side on a pantry "
  "shelf, one bag pushed behind the other instead of one finishing "
  "before the next begins"),
 ("Dry Goods Shelves", "PNF-003", "A GLASS JAR SITS ABOVE EYE LEVEL",
  "a glass grain jar sitting on a high pantry shelf well above eye "
  "level, no step stool visible anywhere nearby on the floor below"),

 ("Canned and Jarred Goods", "PNF-004", "A DENTED CAN NEVER MADE IT TO THE BIN",
  "a can with a visibly dented seam sitting upright in a row of "
  "otherwise ordinary canned goods on a pantry shelf"),
 ("Canned and Jarred Goods", "PNF-005", "FOUR JARS OF THE SAME SAUCE",
  "four identical jars of pasta sauce lined up together on a pantry "
  "shelf, clearly more than a single row would ever need"),
 ("Canned and Jarred Goods", "PNF-006", "THE STICKY RING UNDER THE HONEY JAR",
  "a honey jar sitting in a sticky ring of residue on a pantry shelf, a "
  "single ant visible following the edge of the sticky patch"),

 ("Baking Zone", "PNF-007", "THE UNTESTED TIN OF BAKING POWDER",
  "a tin of baking powder sitting in a baking bin with a bare, "
  "unmarked lid, positioned beside a mixing bowl as if a bake is "
  "about to start"),
 ("Baking Zone", "PNF-008", "ONE SCOOP FOR EVERYTHING, INCLUDING THE ALMOND FLOUR",
  "a single scoop resting inside an open bag of almond flour on a "
  "baking shelf, positioned in the middle of a row of ordinary baking "
  "ingredients rather than standing apart at the end"),
 ("Baking Zone", "PNF-009", "THE BIN COMES BACK SHORT A SCOOP",
  "an open lift-out baking bin on a pantry shelf with an empty slot "
  "where a scoop should be and a bottle of vanilla extract visibly "
  "missing from its usual spot"),

 ("Snack and Lunch Zone", "PNF-010", "THE BIN SITS BELOW ITS OWN LINE",
  "an open snack bin at child height in a pantry, its contents sitting "
  "visibly below a marked fill line painted or taped inside it"),
 ("Snack and Lunch Zone", "PNF-011", "A LID WITH NOTHING LEFT TO CLOSE",
  "a single plastic container lid sitting alone on a pantry shelf with "
  "no matching container anywhere nearby"),
 ("Snack and Lunch Zone", "PNF-012", "A HARD SWEET WITHIN A TODDLER'S REACH",
  "a small bowl of hard candies and whole nuts sitting inside an open "
  "snack bin positioned at a very low, child-reachable height in a "
  "pantry"),

 ("Backstock and Bulk Zone", "PNF-013", "THE SECOND SACK NOBODY NEEDED",
  "two full sacks of rice standing side by side in a pantry backstock "
  "area, one clearly still sealed and untouched behind the other "
  "already in use"),
 ("Backstock and Bulk Zone", "PNF-014", "THE SOFT CORNER ON THE BOTTOM CASE",
  "a cardboard case at the bottom of a stack in a pantry showing a "
  "visibly soft, darkened corner against a wall"),
 ("Backstock and Bulk Zone", "PNF-015", "THE CASE HIDING BEHIND THE CASE",
  "two identical cases of canned tomatoes standing one directly in "
  "front of the other on a pantry backstock shelf, the rear case's "
  "label barely visible"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, pantry-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "four identical jars of pasta sauce crowded together on a "
           "pantry shelf, far more than a single row of that item would "
           "ever need",
 "KC-002": "a glass grain jar sitting on whatever open pantry shelf had "
           "space, no chest-height spot cleared for it anywhere",
 "KC-003": "a nut-flour scoop sitting in the middle of a baking shelf "
           "row instead of standing apart at the end where a hand would "
           "notice it",
 "KC-005": "a second unopened bag of rice hidden directly behind an "
           "already-open bag on a pantry shelf, invisible from the "
           "doorway",
 "KC-006": "a high pantry shelf holding a glass jar with no step stool "
           "anywhere in reach below it",
 "KC-008": "a bare pantry shelf edge with no dated sticker or count "
           "marker anywhere on it, stock stacked with no visible rule",
 "KC-009": "a case of canned tomatoes emptying at the front of a pantry "
           "row with nothing behind it pulled forward to replace it",
 "KC-010": "a small bowl of hard candies and whole nuts sitting in an "
           "open bin at a toddler's exact reaching height",
 "KC-012": "an open snack bin stocked with items sized for an older "
           "child, sitting at a height a much younger child can also "
           "reach",
 "RC-013": "a pantry shelf with an unrefilled snack bin sitting below "
           "its marked line at the end of the day, no single person's "
           "name attached to the task",
 "RC-015": "an opened bag of specialty flour bought for one recipe "
           "sitting untouched on a pantry shelf, clearly not decided "
           "about yet",
 "RC-016": "a hand reaching awkwardly behind a dense row of jars on a "
           "pantry shelf toward a sticky ring that is hard to get to",
 "RC-017": "an orphaned lid sitting on a pantry shelf so long it blends "
           "in among the containers around it",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Dry Goods Shelves": [
  "Vacuum the front lip of the shelf where flour dust drifts forward "
  "and settles, a spot your eyes skip every time you reach in.",
  "Press a finger into the back corner where board meets upright and "
  "check for packed flour dust, then brush it clear.",
  "Check the level in each container from the doorway, without lifting "
  "a single one, and note which one is close to empty.",
 ],
 "Canned and Jarred Goods": [
  "Run a finger under the lid of the honey or syrup jar and wipe away "
  "any sticky drip before an ant finds it.",
  "Turn one row of cans so every label faces out and the oldest date "
  "stands at the front.",
  "Wipe the rim and top of one can as it goes back, where kitchen dust "
  "settles into a greasy film.",
 ],
 "Baking Zone": [
  "Wash the baking bin's scoop in warm soapy water and dry it fully "
  "before it goes back into the flour.",
  "Wipe the one-handed lid mechanism on the flour container clear of "
  "dust so it clicks fully shut again.",
  "Check the nut-flour container's own scoop is still sealed inside "
  "with it, not swapped for another.",
 ],
 "Snack and Lunch Zone": [
  "Turn one lunch bag inside out and shake any crumbs into the bin "
  "before it goes back on its hook.",
  "Wash a drink bottle's spout and screw thread where a sour film "
  "hides in the seam.",
  "Wipe the bin's exterior and the shelf edge where sticky hands land "
  "most often.",
 ],
 "Backstock and Bulk Zone": [
  "Lift the lowest case in one stack and feel its underside for damp "
  "before setting it back down.",
  "Sweep the floor just inside the pantry doorway where a case at "
  "shin height hides in the dark.",
  "Wipe one shelf edge label clean so its written maximum count stays "
  "readable from across the room.",
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
 {"id": "PNA-001", "zone": "Dry Goods Shelves",
  "title": "CLEAR THE SHELF AND SMELL-TEST IT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Bring down every bag and box on this shelf and smell-test "
          "every opened one, so nothing stale or forgotten survives on "
          "a technicality.",
  "why": "A bag with no date on it is impossible to judge honestly, so "
         "it just keeps not getting thrown out.",
  "inputs": ["a bin bag", "a marker"],
  "steps": [
   "Bring down every bag and box on this shelf, open anything "
   "already opened, and smell the flour and the oats: stale, webbed, "
   "or bought for a recipe you have not cooked in months leaves "
   "today.",
   "For anything unopened and still in date but unlikely to get used, "
   "set it aside to give away rather than binning it.",
   "Group what stays into two blocks on the shelf: rice, pasta and "
   "oats together, cereal together."],
  "causes": ["RC-015", "RC-017"],
  "victory": "Every opened bag is sealed in a labeled container or "
             "gone, and pasta, rice and oats stand together as one "
             "block.",
  "next": "PNS-001",
  "art": "a pantry shelf mid-clear with two clean blocks forming, one "
         "of grain containers and one of cereal boxes, a bin bag "
         "sitting on the floor beside it"},

 {"id": "PNA-002", "zone": "Dry Goods Shelves",
  "title": "LABEL EVERY CONTAINER AND MOVE THE GLASS DOWN",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Give every staple one container style with a written open "
          "date, and move any glass jar down to chest height or lower.",
  "why": "A missing label makes every container's age a guess, and a "
         "glass jar above eye level is a real fall and cut risk beside "
         "wet hands.",
  "inputs": ["matching containers", "a permanent marker",
             "adhesive labels"],
  "steps": [
   "Decant each staple into one container style, and write the item "
   "and today's date on the label the moment it is opened.",
   "Move every glass jar down to chest height or lower, and put "
   "lidded plastic containers up top instead.",
   "Keep a two-step stool inside the pantry for anything that still "
   "sits on the top shelf."],
  "causes": ["KC-008", "KC-002"],
  "victory": "Every staple sits in a labeled container with its "
             "opening date on it, and no glass container sits above "
             "eye level.",
  "next": "PNA-001",
  "art": "a hand writing today's date on a labeled pantry container "
         "at chest height, a glass jar visible lower down on the "
         "shelf than a set of plastic containers above it"},

 {"id": "PNA-003", "zone": "Canned and Jarred Goods",
  "title": "PULL EVERY DENTED OR DOMED CAN",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take every can and jar off the shelf, check each one for "
          "damage or a bad date, and remove anything spoiled without "
          "debate.",
  "why": "A dented seam or a domed lid is a spoilage warning, not a "
         "judgment call, and it does not get tasted or given away.",
  "inputs": ["a bin bag"],
  "steps": [
   "Take every can and jar off the shelf, turn each one to find the "
   "date, and put anything dented, rusted, bulging or domed straight "
   "into the bin rather than back on the shelf.",
   "Bag anything spoiled sealed before it goes in the bin, and wipe "
   "the shelf underneath where it stood.",
   "Set every surviving can and jar back with its label facing out."],
  "causes": ["KC-008", "KC-005"],
  "victory": "No dented, rusted, domed or bulging can or jar remains "
             "on the shelf, and every label faces out.",
  "next": "PNS-002",
  "art": "a hand pulling a dented can off a pantry shelf and setting "
         "it apart from a row of undamaged, label-out cans"},

 {"id": "PNA-004", "zone": "Canned and Jarred Goods",
  "title": "ROW BY MEAL, LABEL EACH ROW, RISER UP",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Rearrange cans and jars into rows by meal rather than by "
          "size, label each row, and put the back row up on a riser.",
  "why": "Four jars of the same sauce is what happens when nobody can "
         "see what is already on the shelf before buying another.",
  "inputs": ["a shelf riser", "adhesive labels", "a marker"],
  "steps": [
   "Group cans and jars by meal: tomatoes, coconut milk and stock "
   "together, beans and tuna together, tall jars behind short cans.",
   "Set the back row up on a riser so it sits visibly above the "
   "front row.",
   "Label each row with its category so a gap reads as a shopping "
   "list from the doorway."],
  "causes": ["KC-001", "KC-009"],
  "victory": "Every row holds one category, is labeled, and the back "
             "row sits visibly above the front row on a riser.",
  "next": "PNA-003",
  "art": "a pantry shelf with cans arranged in labeled rows by meal, a "
         "riser lifting the back row visibly above the front row"},

 {"id": "PNA-005", "zone": "Baking Zone",
  "title": "TEST EVERY LEAVENER, TOSS WHAT'S DEAD",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Test every leavener rather than guessing, and remove "
          "anything dead along with hardened brown sugar or grayed "
          "cocoa.",
  "why": "A cake that will not rise on the day is the only way most "
         "households ever find out a leavener died months ago.",
  "inputs": ["hot water", "warm sugared water", "a spoon"],
  "steps": [
   "Test every leavener rather than guessing: a spoon of baking "
   "powder in hot water should fizz hard, and yeast in warm sugared "
   "water should foam. The dead ones go, along with any hardened "
   "brown sugar or grayed cocoa.",
   "Write today's date on the lid of anything that survives, "
   "including anything freshly opened."],
  "causes": ["KC-009", "RC-015"],
  "victory": "Every leavener in the bin has been tested this week, "
             "and nothing dead or expired remains.",
  "next": "PNS-003",
  "art": "a spoon of baking powder fizzing in a glass of hot water on "
         "a pantry counter, a dated tin standing ready beside it"},

 {"id": "PNA-006", "zone": "Baking Zone",
  "title": "GIVE THE ALLERGEN SHELF ITS OWN SCOOP AND SPOT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Move nut flours and sesame to the end of the row with their "
          "own sealed container and their own scoop, never shared.",
  "why": "One shared scoop carries a trace of an allergen straight "
          "into a birthday cake, and nobody notices until somebody "
          "reacts.",
  "inputs": ["a sealed container per allergen", "a dedicated scoop "
             "per allergen", "a label"],
  "steps": [
   "Move every nut flour and sesame product to the end of the row, "
   "away from where a hand grabs by habit.",
   "Seal each one in its own container with its own scoop kept "
   "inside it, never shared with the rest of the shelf.",
   "Label the container clearly so anyone baking in a hurry sees the "
   "warning before the scoop."],
  "causes": ["KC-003", "KC-008"],
  "victory": "Every allergen container stands at the end of the row, "
             "sealed, labeled, with its own dedicated scoop inside it.",
  "next": "PNA-005",
  "art": "a sealed, labeled nut-flour container with its own scoop "
         "standing apart at the end of a pantry baking shelf"},

 {"id": "PNA-007", "zone": "Snack and Lunch Zone",
  "title": "MATCH LIDS, COMBINE THE RATTLING BOXES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Match every lid to a container, bin the orphans in both "
          "directions, and combine snack boxes that are nearly empty.",
  "why": "An orphaned lid or a lidless tub is why a container gets "
         "passed over at packing time instead of used.",
  "inputs": ["a bin bag"],
  "steps": [
   "Match every lid to a container and bin the orphans in both "
   "directions, the lidless tubs and the lids for tubs that died. "
   "Pull any snack boxes with only a couple of bars rattling around "
   "and combine them.",
   "Flatten and recycle the empty cartons."],
  "causes": ["KC-002", "RC-017"],
  "victory": "Every reusable container has its own lid sitting on it, "
             "and the open bin is filled to its marked line.",
  "next": "PNS-004",
  "art": "a hand matching a lid to its container on a pantry shelf, "
         "an orphaned lid and a lidless tub set apart to be binned"},

 {"id": "PNA-008", "zone": "Snack and Lunch Zone",
  "title": "SET THE BIN BY THE YOUNGEST REACH AND FIX THE LINE",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Choose the open bin's contents by the youngest child who "
          "can reach it, and mark a fill line a child can read.",
  "why": "A bin stocked for the oldest child in the house is a choke "
          "hazard for the youngest one who can also reach it.",
  "inputs": ["tape or a marker for the fill line", "the snacks you "
             "are choosing to allow"],
  "steps": [
   "Empty the bin and set aside anything that is a choking hazard for "
   "the youngest child who can reach this shelf.",
   "Refill it with only what you have said yes to, and mark a fill "
   "line inside the bin at the level it should sit at.",
   "Move anything that still needs an adult up to the higher shelf."],
  "causes": ["KC-010", "KC-012"],
  "victory": "The open bin holds only pre-approved, age-appropriate "
             "snacks, filled to a clearly marked line.",
  "next": "PNA-007",
  "art": "an open snack bin at child height with a clearly marked fill "
         "line, filled with age-appropriate snacks and no choking "
         "hazards"},

 {"id": "PNA-009", "zone": "Backstock and Bulk Zone",
  "title": "MOVE THE EXTRA FORWARD OR OUT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Meet what you forgot you owned in the backstock, and move "
          "any genuine extra forward into use this month or out of the "
          "house.",
  "why": "A warehouse pack was never a saving if it went stale before "
         "you reached the bottom of it.",
  "inputs": ["a marker for writing the arrival month"],
  "steps": [
   "Open up the back of this zone and meet what you forgot you owned: "
   "any item you hold more than one genuine spare of moves forward "
   "into the working shelves this month or it leaves.",
   "Write the arrival month on every remaining pack as it goes back."],
  "causes": ["KC-001", "RC-015"],
  "victory": "Every remaining pack carries its arrival month, and "
             "nothing sits stacked in front of an older case of the "
             "same thing.",
  "next": "PNS-005",
  "art": "a backstock shelf with a duplicate sack of rice set apart "
         "from the rest, ready to move forward into use or leave the "
         "house"},

 {"id": "PNA-010", "zone": "Backstock and Bulk Zone",
  "title": "DATE EVERY CASE AND WRITE THE MAXIMUM",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Write a maximum for each line on the shelf edge, and check "
          "every case is one row deep with nothing hidden behind it.",
  "why": "Undated bulk with no written limit is where a saving quietly "
          "expires out of sight, and a hidden case behind another one "
          "never gets pulled first.",
  "inputs": ["a marker", "adhesive shelf-edge labels"],
  "steps": [
   "Pull every case forward to check nothing is stacked directly in "
   "front of another one of the same thing.",
   "Write a maximum for each line on the shelf edge, based on the "
   "most you have genuinely used up before it turned.",
   "Mark every case with its arrival month as it goes back, oldest "
   "at the front."],
  "causes": ["KC-008", "KC-005"],
  "victory": "Every line has a maximum written on the shelf edge, "
             "every pack carries its arrival month, and nothing is "
             "stacked in front of anything else.",
  "next": "PNA-009",
  "art": "a shelf edge in a pantry backstock zone with a small dated "
         "sticker marking a count, cases arranged one row deep "
         "behind it"},

 {"id": "PNA-011", "zone": None, "title": "THE FULL SHELF SAFETY AND ACCESS WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every shelf checking what is stored above eye level, "
          "whether a stool is where it should be, and reaching the "
          "sticky spots nobody gets to on an ordinary pass.",
  "why": "A glass jar too high and a sticky ring too awkward to reach "
         "both hide until someone tests for them on purpose.",
  "inputs": ["a two-step stool", "a cloth for the awkward spots"],
  "steps": [
   "Check every shelf for glass or heavy items stored above eye "
   "level, and move them down to chest height or lower.",
   "Confirm a two-step stool actually lives inside the pantry, not "
   "somewhere else in the house.",
   "Reach behind the dense rows to find and wipe any sticky ring or "
   "hard-to-reach spot the ordinary Shine pass skips."],
  "causes": ["KC-006", "RC-016"],
  "victory": "Nothing heavy or glass sits above eye level, a working "
             "stool lives in the pantry, and no sticky spot remains "
             "unreached.",
  "next": "PNA-010",
  "art": "a hand using a two-step stool to move a glass jar down from "
         "a high pantry shelf to chest height"},

 {"id": "PNA-012", "zone": None, "title": "THE WEEKLY GAP-AND-DATE PASS",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "Walk every shelf reading the gaps before the shopping list "
          "gets written, and name who is doing it this week.",
  "why": "Cans and jars never force the issue by spoiling on schedule, "
         "so this zone fails silently unless somebody is actually "
         "assigned to look.",
  "inputs": ["the shopping list"],
  "steps": [
   "Walk the can rows and the staple blocks and read the gaps before "
   "the shopping list gets written.",
   "Say out loud, or write down, whose turn it is to do this pass "
   "this week.",
   "Add anything genuinely missing to the list on the spot."],
  "causes": ["RC-013"],
  "victory": "The shelves were read for gaps before this week's "
             "shopping list was written, and one named person did it.",
  "next": "PNA-011",
  "art": "a hand writing an item onto a shopping list while standing "
         "in front of a pantry shelf with a visible gap in one row"},

 {"id": "PNA-013", "zone": None, "title": "THE MONTHLY OVER-BUY AUDIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Once a month, check every written maximum and label against "
          "what is actually on the shelves, and correct any that have "
          "drifted.",
  "why": "A maximum written once and never revisited stops meaning "
          "anything the first time a genuinely good price tempts you "
          "past it.",
  "inputs": ["a marker", "this month's receipts if you kept them"],
  "steps": [
   "Compare the count on each backstock line against its written "
   "maximum, and note any line that has crept over.",
   "For any line over its maximum, decide today whether the number "
   "was wrong or the buying was: correct the label, or commit to "
   "pausing that purchase.",
   "Check that every open container still carries a legible date and "
   "relabel anything that has faded."],
  "causes": ["KC-008", "KC-009"],
  "victory": "Every backstock line sits at or under a maximum you "
             "checked this month, and every open container's date is "
             "legible.",
  "next": "PNA-012",
  "art": "a hand comparing a shelf's case count against a small "
         "dated sticker fixed to a pantry backstock shelf edge"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a pantry, one per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("PNE-001", "THE MIDWEEK EMPTY-SHELF SCRAMBLE",
  "You reach for pasta on a Tuesday night with no plan B, and the "
  "shelf has to answer honestly whether there's a full block of "
  "staples or a gap.",
  ["PNZ-001"],
  "A full, labeled block of rice, pasta and oats answers immediately, "
  "no hunting behind other boxes.",
  "If you had to dig behind cereal boxes to find a bag that might "
  "still be good, the loading-behind rule slipped. Draw PNA-002.",
  "a hand reaching confidently into a pantry shelf at dinner time and "
  "pulling out a labeled container of pasta from a tidy block of "
  "staples"),
 ("PNE-002", "THE EMPTY-FRIDGE-WEEK DINNER",
  "The fridge is bare and dinner has to come entirely from cans and "
  "jars tonight.",
  ["PNZ-002"],
  "Every can you reach for is legible, unspoiled and exactly where "
  "its row says it should be.",
  "If you pulled a can and found it dented or hidden behind another, "
  "the spoilage or visibility check lapsed. Draw PNA-003.",
  "a hand pulling a labeled, undamaged can from a well-organized "
  "pantry row to make a meal from pantry staples alone"),
 ("PNE-003", "THE UNPLANNED BIRTHDAY BAKE",
  "Someone asks for a cake with two hours' notice and the baking bin "
  "has to answer for itself.",
  ["PNZ-003"],
  "The bin has a working scoop, dated leaveners that still test "
  "fresh, and vanilla exactly where it belongs.",
  "If a leavener failed its fizz test or a tool was missing, the "
  "bin's own reset slipped. Draw PNA-005.",
  "a hand lifting a lift-out baking bin from a pantry shelf, a scoop, "
  "dated leaveners and vanilla all visibly in place"),
 ("PNE-004", "THE MORNING NOBODY PACKED LUNCH THE NIGHT BEFORE",
  "Lunches have to get packed in five rushed minutes before the bus, "
  "straight from whatever the bin already holds.",
  ["PNZ-004"],
  "The open bin is filled to its line with only pre-approved snacks, "
  "and every container has its matching lid.",
  "If the bin was empty or a container had no lid, the evening "
  "refill did not happen. Draw PNA-007.",
  "a hand packing a lunchbox quickly from a well-stocked open snack "
  "bin at child height, every container already matched with its "
  "lid"),
 ("PNE-005", "THE SURPRISE BULK DELIVERY",
  "A bulk order arrives unannounced and has to go somewhere in a "
  "backstock zone that is already at its stated limits.",
  ["PNZ-005"],
  "Every existing line sits at or under its written maximum, so the "
  "new delivery has an honest amount of room to go into.",
  "If there was nowhere to put it without exceeding a written "
  "maximum, the pull-forward-and-stop-buying rule slipped. Draw "
  "PNA-009.",
  "a delivery person setting down a new case of groceries beside "
  "neatly dated, labeled backstock cases each with visible room "
  "still left on their shelf"),
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
        "related": {"standard": f"PNS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true on your shelf, "
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
    standard_id = (f"PNS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"PNS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "PNR-001", "title": "THE PANTRY", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "FIVE SHELVES. START WITH THE ONE THAT HIDES THE "
                   "OLDEST BAG.",
        "objective": "The pantry is where you find out the difference "
                     "between what you buy and what you actually eat. "
                     "This card is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"PNZ-001 Dry Goods Shelves. {start_tip['text']}"
            if start_tip else
            "PNZ-001 Dry Goods Shelves. Emptying it gives every other "
            "zone somewhere to put things."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true on your shelf. Put the rest back.",
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
        "safety_first": "Do PNA-011 The Full Shelf Safety And Access "
                        "Walk before any rebuild. It takes thirty "
                        "minutes and covers every shelf's height, the "
                        "stool, and every hard-to-reach spot.",
        "related": {"contents": "PNZ-001 to PNZ-005, PNF-001 to PNF-015, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, PNA-001 to PNA-013, "
                                 "PNS-001 to PNS-005, PNE-001 to PNE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole pantry "
                           "in its settled state, dry goods shelves, "
                           "canned goods, a baking bin, a child-height "
                           "snack bin and a backstock area all visible "
                           "in one frame",
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
    return {"deck": "pantry", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_stair_landing_deck.py)."""
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

    assert any(c["id"] == "PNA-011" for c in cards), "no safety walk card"
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
    print(f"  deck        pantry ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
