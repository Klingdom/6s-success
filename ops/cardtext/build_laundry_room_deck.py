#!/usr/bin/env python3
"""
Build the Laundry Room deck: 67 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
`content/manual/source/content.json`, the same corpus the 114 zone pages
already read. `ops/cardtext/build_entryway_deck.py` proved the pattern for a
second room after Kitchen; this is the third, and the first with six zones
instead of five or seven. Purpose, done_looks_like, the standard, the
trigger, the first-15 action and its victory condition are quoted from the
Manual, not rewritten, and `gate()` at the bottom asserts they are still
character-for-character identical. The 18 frictions (three per zone) are
likewise derived straight from the Manual's own `diagnosis` layer, in zone
order, not retyped, so this deck cannot silently diverge from the
diagnostic engine already shipped on the site's zone pages.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the nine
new action cards (the Manual gives one 15-minute reset per zone in
`first_15`; the 30-minute rebuild per zone and three whole-room actions are
authored here), the event cards, the micro quests, and the room card. The
root causes are not reauthored: they are the same frozen vocabulary in
`ops/root_causes.py` that the Kitchen and Entryway decks already use, so a
household owning more than one deck keeps one diagnosis pile rather than
several (DECK-GAME-DESIGN.md 4.3). This room's own diagnosis data reaches
fifteen of the vocabulary's seventeen causes (every one except KC-011 and
RC-014, neither of which any Laundry Room friction branches to), more than
either Kitchen (twelve) or Entryway (thirteen), because six zones with a
"the machine, the chemistry, the sort, the fold, the dry, the tools" spread
touch more of the vocabulary than a smaller room does.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
ops/cardtext/build_kitchen_deck.py and ops/cardtext/build_entryway_deck.py
keep. There is no old, mismatched free Laundry Room deck to disclose
against (unlike Entryway's twelve-zone/five-zone conflict): no free Laundry
deck exists on the site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_laundry_room_deck.py
Out:  ops/cardtext/laundry-room-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "laundry-room-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Laundry Room"

# Not the Kitchen print-tier budget (DECK-GAME-DESIGN.md 4.1's 72, fixed by
# two print-economics constraints Kitchen chose to fit). This room ships as
# a free typeset page, the same stage Kitchen and Entryway shipped at
# before any print-on-demand decision existed, so the budget here is the
# honest count of what this room's own corpus, diagnosis layer and a
# proportionate amount of new authorship produce: six real zones, fifteen
# reachable root causes (not twelve or thirteen), two actions per zone plus
# three whole-room ones.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 15, "ACTION CARD": 15, "STANDARD CARD": 6,
          "EVENT CARD": 6}
TOTAL = sum(BUDGET.values())

# Same palette family as the Kitchen and Entryway decks so a mixed pile of
# cards from any room still reads as one product line.
TYPE_COLOUR = {
    "ROOM CARD": "#2B2622", "ZONE CARD": "#2F5233",
    "FRICTION CARD": "#BC4B2A", "ROOT CAUSE CARD": "#6E5B8B",
    "ACTION CARD": "#3C5A6B", "STANDARD CARD": "#4E7A57",
    "EVENT CARD": "#8C5A2B",
}

# Root causes this room's real diagnosis branches actually reach, derived
# below from the Manual and asserted (in gate()) to be exactly this set: not
# a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written: every
# one of the six zones' nine diagnosis branches (18 frictions x 3 branches
# minus overlap) was read and its "cause" field copied here verbatim.
# KC-011 and RC-014 are the only two of the shared seventeen this room's
# frictions never branch to.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-012",
             "RC-013", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule the Kitchen and Entryway generators use:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Washer and Dryer": {
  "id": "LRZ-001", "order": 1, "difficulty": 3,
  "tagline": "BOTH LIDS BARE. THE DUCT DATE ON THE TAPE.",
  "callouts": [
   "Washer door propped ajar, drum empty",
   "Dryer drum empty behind its door",
   "Bare surface across both lids",
   "Lint screen back in its slot",
   "A strip of masking tape on the dryer's side",
   "Nothing stacked on either machine",
  ],
  "art": ("a washer and dryer standing side by side, the washer door "
          "propped ajar with its drum empty, the dryer's door shut over an "
          "equally empty drum, both lids completely bare, a lint screen "
          "sitting clean in its slot on the dryer top, and a strip of "
          "masking tape stuck to the side of the dryer"),
 },
 "Detergent and Treatment Zone": {
  "id": "LRZ-002", "order": 2, "difficulty": 2,
  "tagline": "ONE OF EACH KIND. THE DOSE LINE INKED.",
  "callouts": [
   "One detergent bottle standing on the tray",
   "One bleach bottle beside it",
   "One tub of oxygen powder",
   "One stain treatment bottle",
   "The pod tub latched above shoulder height",
   "A dose line marked on the cap",
  ],
  "art": ("a wipeable tray on a laundry shelf holding one bottle of "
          "detergent, one bottle of bleach, one tub of oxygen powder and "
          "one stain treatment standing side by side, a latched pod tub "
          "sitting on a higher shelf above shoulder height, and a dark "
          "ink line marked around the neck of the detergent cap"),
 },
 "Sorting and Hamper Zone": {
  "id": "LRZ-003", "order": 3, "difficulty": 2,
  "tagline": "THREE BAGS. NEVER PAST HALF FULL.",
  "callouts": [
   "Three sorting bags standing upright",
   "Each bag below half full",
   "Bags standing clear of the walking line",
   "A small dish on the shelf",
   "The dish holding only today's pocket contents",
   "Bare floor in front of the washer door",
  ],
  "art": ("three laundry sorting bags standing upright against a wall, "
          "each no more than half full and clear of the open floor path "
          "to a washing machine, a small dish sitting on a shelf nearby "
          "holding a single coin and a receipt, and a bare stretch of "
          "floor visible in front of the washer door"),
 },
 "Folding Surface": {
  "id": "LRZ-004", "order": 4, "difficulty": 1,
  "tagline": "THE COUNTER IS BARE OR HOLDING ONE LOAD.",
  "callouts": [
   "Completely bare counter surface",
   "Empty baskets stacked underneath",
   "One basket per bedroom",
   "Six spare hangers on the rail",
   "No clean clothing left in the room",
   "A clear run of counter long enough to fold on",
  ],
  "art": ("a laundry folding counter completely bare, a stack of empty "
          "baskets underneath it, six spare hangers hanging on a rail at "
          "one end, and no clean clothing anywhere else in the room"),
 },
 "Hanging and Air-Dry Zone": {
  "id": "LRZ-005", "order": 5, "difficulty": 2,
  "tagline": "THE RACK IS FOLDED FLAT, OR IT IS WORKING.",
  "callouts": [
   "Drying rack folded flat against the wall",
   "Bars on the rack completely dry",
   "Drip tray wiped out and empty",
   "Six spare hangers on the rail",
   "Nothing hanging that is more than a day old",
   "Clear floor beneath where the rack stands",
  ],
  "art": ("a collapsible drying rack folded completely flat against a "
          "wall, its bars dry, an empty drip tray resting beneath it, six "
          "spare hangers on a rail beside it, and a clear stretch of "
          "floor where the rack usually stands open"),
 },
 "Utility and Cleaning Zone": {
  "id": "LRZ-006", "order": 6, "difficulty": 2,
  "tagline": "EVERY TOOL HANGS. THE OUTLINE SHOWS WHAT'S MISSING.",
  "callouts": [
   "Broom hanging heads up on the wall",
   "Mop hanging heads up beside it",
   "Dustpan hanging with the others",
   "A caddy holding every vacuum attachment",
   "The mop head fully dry",
   "An empty bucket standing in its taped floor square",
  ],
  "art": ("a broom, a mop and a dustpan hanging heads up on wall hooks "
          "with a painted outline visible behind each one, a caddy nearby "
          "holding every vacuum attachment in its place, the mop head "
          "hanging fully dry, and an empty bucket standing inside a taped "
          "square marked on the floor"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine already
# shipped. Three per zone, matching that data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Washer and Dryer", "LRF-001", "THE LOAD NOBODY MOVED",
  "a washing machine door standing open with a load of clothes visibly "
  "sitting still inside the drum, the room around it otherwise empty and "
  "undisturbed"),
 ("Washer and Dryer", "LRF-002", "ONE LOAD, THREE CYCLES",
  "a dryer control panel showing a cycle restarting for a second time, a "
  "lint screen sitting nearby still coated in a thick grey mat of lint"),
 ("Washer and Dryer", "LRF-003", "THE LIDS ARE NEVER BARE",
  "the tops of a washer and dryer cluttered with a stray sock, a box of "
  "dryer sheets and a bottle of softener crowded together across both "
  "lids"),

 ("Detergent and Treatment Zone", "LRF-004", "THREE HALF BOTTLES OF THE SAME THING",
  "a laundry shelf holding three nearly identical detergent bottles side "
  "by side, each filled to a different level"),
 ("Detergent and Treatment Zone", "LRF-005", "NOBODY POURS THE SAME DOSE TWICE",
  "a detergent cap held up to the light with a crusted ring of dried "
  "powder built up well above its moulded fill line"),
 ("Detergent and Treatment Zone", "LRF-006", "THE PODS SIT AT A CHILD'S EYE LEVEL",
  "a laundry shelf at knee height holding an open tub of colourful "
  "detergent pods, well below shoulder height"),

 ("Sorting and Hamper Zone", "LRF-007", "THE CLOTHES LAND ON THE FLOOR, NOT THE BAG",
  "a small pile of dirty clothes lying on a bedroom floor a short "
  "distance from a laundry bag standing mostly out of sight behind a "
  "door"),
 ("Sorting and Hamper Zone", "LRF-008", "EVERY LOAD GETS SORTED TWICE",
  "five unlabelled sorting bags standing in a row, clothes of mixed "
  "colours visible spilling from more than one of them"),
 ("Sorting and Hamper Zone", "LRF-009", "POCKETS EMPTY INTO THE DRUM, NOT THE DISH",
  "a washing machine drum holding a damp load with a few coins and a "
  "crumpled receipt caught among the clothes"),

 ("Folding Surface", "LRF-010", "THE CLEAN LOAD IS STILL HERE FROM MONDAY",
  "a laundry basket sitting full of neatly folded clothes on a counter, "
  "undisturbed, with dust visible settling faintly on the top layer"),
 ("Folding Surface", "LRF-011", "THE COUNTER HOLDS EVERYTHING BUT LAUNDRY",
  "a folding counter crowded with a stack of mail, a toolbox and a "
  "cardboard parcel, no clear space left for a basket of clothes"),
 ("Folding Surface", "LRF-012", "CLEARING THE COUNTER TAKES LONGER THAN FOLDING",
  "a hand pushing aside a stack of unrelated objects on a counter to make "
  "room for a single dry laundry basket set down beside them"),

 ("Hanging and Air-Dry Zone", "LRF-013", "THE RACK NEVER COMES DOWN",
  "a drying rack standing open and fully loaded with garments in a "
  "corner, its legs never folded flat against the wall behind it"),
 ("Hanging and Air-Dry Zone", "LRF-014", "DRY BY THE TAG, MUSTY BY THE NOSE",
  "garments hung tightly overlapping on a drying rack with almost no gap "
  "between them, a shallow tray of standing water visible underneath"),
 ("Hanging and Air-Dry Zone", "LRF-015", "THE DELICATE LOAD WENT IN THE DRYER ANYWAY",
  "a dryer door open with a single delicate garment visibly shrunken and "
  "misshapen lying among an otherwise ordinary load"),

 ("Utility and Cleaning Zone", "LRF-016", "THE BROOM ALWAYS ENDS UP ON THE FLOOR",
  "a broom and a mop leaning against a bare wall in a corner with no hook "
  "or rail above them, their heads resting directly on the floor"),
 ("Utility and Cleaning Zone", "LRF-017", "THE MOP MAKES THE FLOOR WORSE, NOT BETTER",
  "a mop head hanging with its bristles pointing downward, water still "
  "dripping from it onto the floor beneath, a bucket nearby holding "
  "stored items rather than water"),
 ("Utility and Cleaning Zone", "LRF-018", "AN ATTACHMENT IS ALWAYS MISSING",
  "a caddy of vacuum attachments with one visible gap where a nozzle "
  "should sit, the loose attachments scattered rather than seated in the "
  "caddy"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, laundry-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use (DECK-GAME-DESIGN.md 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "three nearly full bottles of the same fabric softener lined "
           "up on a laundry shelf with no other products beside them",
 "KC-002": "a single loose sock and a stray hair tie sitting on top of a "
           "washing machine with no tray or dish anywhere nearby",
 "KC-003": "a folded stack of clean towels sitting on a laundry room "
           "shelf far from the bathroom cupboard they are meant to fill",
 "KC-004": "a stepladder standing open in front of a laundry room wall "
           "cupboard, a single box of detergent visible on the shelf "
           "behind it",
 "KC-005": "an open laundry cupboard with a stain treatment bottle "
           "pushed to the very back, barely visible behind taller "
           "bottles in front",
 "KC-006": "a wall hook holding a broom mounted well above head height, "
           "a short step stool standing beneath it",
 "KC-007": "a narrow laundry shelf with bottles and bins pressed edge to "
           "edge, one bin lid unable to close flat",
 "KC-008": "a washing machine lid with a stray glove sitting on one half "
           "and bare surface on the other, no consistent state to either "
           "side",
 "KC-009": "a dryer sitting finished and silent with a load of clothes "
           "still resting untouched inside its open drum",
 "KC-010": "a bottle of drain cleaner sitting on a low shelf directly "
           "beside a stack of children's folded clothes",
 "KC-012": "two detergent scoops of different sizes sitting side by side "
           "on a laundry shelf, each showing a different dose line",
 "RC-013": "a laundry basket of dry folded clothes sitting untouched on "
           "a counter with no note or name attached to it",
 "RC-015": "a single unopened parcel sitting on an otherwise bare "
           "laundry folding counter, waiting",
 "RC-016": "a mop bucket wedged into a tight corner behind a washing "
           "machine, barely reachable without moving the machine first",
 "RC-017": "a stack of unmatched socks in a shoebox that has sat in the "
           "same corner of a laundry shelf long enough to gather a faint "
           "layer of dust",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes, the same contract
# ops/cardtext/build_kitchen_deck.py's MICRO_QUESTS already meets
# (DECK-GAME-DESIGN.md section 2). Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Washer and Dryer": [
  "Pull the dryer forward, check the duct for a soft grey buildup, and "
  "write this month on the tape strip if it is clear.",
  "Lift the folds of the washer door gasket and wipe out whatever has "
  "collected in the seal.",
  "Prop the washer door open a hand's width and check the lint screen is "
  "fully clear before you leave the room.",
 ],
 "Detergent and Treatment Zone": [
  "Ink the true dose line on the cap of whatever bottle you use next, "
  "right at the machine.",
  "Line up every bottle on the shelf and carry any second open jug of the "
  "same product to recycling.",
  "Check the pod tub is latched and standing above shoulder height, and "
  "move it if it is not.",
 ],
 "Sorting and Hamper Zone": [
  "Tip the fullest sorting bag out and start that load right now, even if "
  "it is not the usual day.",
  "Check the pocket dish on the shelf and empty anything sitting in it "
  "before the next load goes in.",
  "Straighten each sorting bag so none of them stand in the walking line "
  "to the machines.",
 ],
 "Folding Surface": [
  "Carry one basket to its bedroom right now, even if the rest are not "
  "folded yet.",
  "Clear anything off the counter that is not part of the load you are "
  "folding.",
  "Hang one item that should not be folded onto the rail instead of "
  "stacking it.",
 ],
 "Hanging and Air-Dry Zone": [
  "Touch every item on the rack and carry off anything that is already "
  "dry.",
  "Empty the drip tray and dry it before it goes back under the rack.",
  "Fold the rack flat against the wall the moment the last item comes off "
  "it.",
 ],
 "Utility and Cleaning Zone": [
  "Hang the broom and dustpan back on their outlines instead of leaning "
  "them for later.",
  "Rinse the mop head and hang it to dry before it goes back on the "
  "rail.",
  "Check every vacuum attachment is in the caddy, and go find the one "
  "that is not.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked) and an
# authored 30-minute rebuild. Three more whole-room actions, the same
# shape as Entryway's three whole-entryway cards: no zone or standard
# invented for them, only their real root causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "LRA-001", "zone": "Washer and Dryer",
  "title": "EMPTY THE DRUMS AND DATE THE DUCT", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty both drums, clear both lids, clear the lint screen, and "
          "write this month's date on the duct tape strip.",
  "why": "A drum you have to empty before you can fill is the single "
         "reason a household skips the last step of a wash day.",
  "inputs": ["masking tape and a pen",
             "the vent brush if the lint screen is due a clean"],
  "steps": [
   "Empty both drums, take everything off both lids, clear the lint "
   "screen and put it back, prop the washer door ajar, and write this "
   "month on a strip of tape on the side of the dryer.",
   "Check the tape already on the dryer: if the month reads more than a "
   "year ago, treat the duct itself as this cycle's real job, not next "
   "month's.",
   "Wipe down anything sticky left on either lid before you leave the "
   "room."],
  "causes": ["KC-009", "KC-008"],
  "victory": "Both drums empty, both lids bare, the door propped open, "
             "and a date on the dryer you can read from the doorway.",
  "next": "LRS-001",
  "art": "a washer and dryer standing side by side with both doors open "
         "and their drums empty, a fresh strip of masking tape visible on "
         "the side of the dryer, both lids completely bare"},

 {"id": "LRA-002", "zone": "Washer and Dryer",
  "title": "PULL THE DRYER AND CLEAR THE DUCT", "minutes": 30,
  "players": "1 to 2", "six_s": "Safety",
  "goal": "Disconnect the duct, clear what has built up behind the "
          "machine, and check the fill hoses while everything is already "
          "pulled out.",
  "why": "Lint packed behind the dryer is the highest fuel and the "
         "highest heat of any indoor room outside the kitchen, and a "
         "hose gone hard at the collar sprays without warning.",
  "inputs": ["a step stool or helper to ease the machine forward",
             "a vacuum with a hose attachment",
             "rigid metal duct if the current run is a foil accordion"],
  "steps": [
   "Unplug the dryer and ease it forward on its feet far enough to reach "
   "the duct connection.",
   "Disconnect the duct and vacuum out any soft grey packing built up at "
   "the bend behind the machine.",
   "If the duct is a flexible foil accordion, replace the run with rigid "
   "metal now rather than promising to do it later.",
   "Check both fill hoses for a hard or bulged collar while the machines "
   "are already pulled out, and replace either one that has gone stiff.",
   "Push both machines back, level on their feet, and reconnect the duct "
   "fully before running the next load."],
  "causes": ["KC-010", "KC-002"],
  "victory": "The duct is clear and rigid where it can be, both fill "
             "hoses are supple at the collar, and both machines sit "
             "level on their feet.",
  "next": "LRA-001",
  "art": "a dryer pulled away from the wall with its duct disconnected, "
         "a small pile of grey lint cleared from the bend, a coil of "
         "rigid metal duct ready beside it"},

 {"id": "LRA-003", "zone": "Detergent and Treatment Zone",
  "title": "ONE TRAY, ONE BOTTLE OF EACH", "minutes": 15, "players": "1",
  "six_s": "Sort", "from_first_15": True,
  "goal": "Bring every laundry product onto one tray, keep one working "
          "bottle of each kind, ink the true dose line, and latch the "
          "pod tub high.",
  "why": "A second open bottle of the same product almost always means "
         "the first one had gone invisible, and a low, unlatched pod tub "
         "is a poisoning risk in a house with children.",
  "inputs": ["a permanent marker", "a wipeable tray",
             "a high shelf or latch for the pod tub"],
  "steps": [
   "Bring every laundry product onto one wipeable tray. Keep one working "
   "bottle of each kind, ink the true dose line on each cap, and latch "
   "the pod tub above shoulder height.",
   "Recycle the empty or near-empty duplicate the moment the working "
   "bottle is confirmed.",
   "Wipe the shelf under the tray before anything goes back onto it."],
  "causes": ["KC-001", "KC-010"],
  "victory": "One of each kind standing on a wipeable tray, a dose line "
             "you can see on every cap, and nothing a child can reach.",
  "next": "LRS-002",
  "art": "a wipeable tray on a laundry shelf holding one bottle of each "
         "product with a marked dose line on each cap, an empty "
         "duplicate bottle set aside for recycling, a latched pod tub on "
         "a shelf above shoulder height"},

 {"id": "LRA-004", "zone": "Detergent and Treatment Zone",
  "title": "SEPARATE THE SHELF FROM THE FLOOR", "minutes": 30,
  "players": "1", "six_s": "Standardize",
  "goal": "Move bleach away from any ammonia-based cleaner, fix the "
          "shelf bracket if it is corroding, and give the tray a rinse.",
  "why": "Bleach and an ammonia-based cleaner sharing a shelf, or a "
         "bucket, can mix into a gas in a small room with the door "
         "shut.",
  "inputs": ["a spare shelf or bracket if the bleach shelf is corroding",
             "the drip tray", "a permanent marker"],
  "steps": [
   "Move bleach and any ammonia-based cleaner onto separate shelves, "
   "never sharing a tray or a bucket.",
   "Check the bracket under the bleach shelf for rust or corrosion from "
   "fumes, and replace it if it has started to give.",
   "Carry the drip tray to the sink, scrub the tacky corners, dry it, "
   "and set it back under the containers.",
   "Write the job on the tray edge under each bottle, wash, whites, "
   "stains, so a returned bottle lands in its own footprint."],
  "causes": ["KC-012", "RC-016"],
  "victory": "Bleach and any ammonia-based cleaner sit on separate "
             "shelves, the bracket underneath is sound, and the tray is "
             "clean and marked by job.",
  "next": "LRA-003",
  "art": "a laundry shelf with a bleach bottle standing well apart from "
         "an ammonia-based cleaner, a clean drip tray beneath them with "
         "each spot marked by its job"},

 {"id": "LRA-005", "zone": "Sorting and Hamper Zone",
  "title": "CUT TO THREE BAGS", "minutes": 15, "players": "1",
  "six_s": "Sort", "from_first_15": True,
  "goal": "Cut the sorting streams to three, label those bags, stand "
          "them clear of the walking line, and add a dish for pockets.",
  "why": "A bag that stays a third full for weeks is not sorting, it is "
         "clothes taken out of circulation.",
  "inputs": ["three bags", "a marker or labels", "a small dish"],
  "steps": [
   "Cut the sorting streams to the three this household will actually "
   "honour, label those three bags, stand them clear of the walking "
   "line, and put an empty dish on the shelf for pockets.",
   "Empty any spare hamper you were holding for a stream that never "
   "filled on its own.",
   "Check the floor in front of the washer door is bare before you "
   "leave."],
  "causes": ["KC-001", "KC-005"],
  "victory": "Three labelled bags, none above half full, bare floor in "
             "front of the washer door, and a dish holding only today's "
             "pocket contents.",
  "next": "LRS-003",
  "art": "three labelled laundry sorting bags standing against a wall "
         "clear of an open floor path, a small dish on a shelf nearby, "
         "bare floor visible in front of a washing machine"},

 {"id": "LRA-006", "zone": "Sorting and Hamper Zone",
  "title": "MOVE THE BAGS OUT OF THE WALKING LINE", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Reposition every sorting bag off the walking line and out of "
          "reach of a utility knife or blade riding home in a pocket.",
  "why": "A hamper in the walking line is a fall you take with your arms "
         "full, and reaching blind into a bag of work clothes is how a "
         "blade finds a hand.",
  "inputs": ["hooks or a low shelf for the bags",
             "a small parts tray for pocket finds"],
  "steps": [
   "Walk the path from the door to the machines and move any bag "
   "standing in that line to the side.",
   "Fix a hook or shelf for each bag so it has a real spot away from the "
   "walking line.",
   "Add a rule out loud: check every pocket by hand before it goes in "
   "the bag, not by reaching in blind later.",
   "Confirm the dish on the shelf catches what pockets hold, so nothing "
   "sharp waits at the bottom of a bag."],
  "causes": ["KC-003", "KC-006"],
  "victory": "Every bag sits clear of the walking line at a reachable "
             "height, and pockets are checked going in, not pulled out "
             "blind.",
  "next": "LRA-005",
  "art": "laundry sorting bags mounted on wall hooks well clear of a "
         "walking path between a door and washing machines"},

 {"id": "LRA-007", "zone": "Folding Surface",
  "title": "CLEAR THE COUNTER AND DELIVER THE BASKETS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the counter completely, set one empty basket per "
          "bedroom underneath, hang six spare hangers, and deliver every "
          "clean item in the room.",
  "why": "Clean clothes with nowhere to go are the reason a dry load "
         "goes back in for a second tumble.",
  "inputs": ["one basket per bedroom", "six spare hangers"],
  "steps": [
   "Clear the counter completely, put one empty basket per bedroom "
   "underneath it, hang six spare hangers on the rail at the end, and "
   "take every piece of clean clothing in this room to the bedroom it "
   "belongs in.",
   "Wipe the bare counter once it is cleared, before the next load lands "
   "on it.",
   "Confirm no basket is left sitting full on the floor instead of "
   "stacked under the counter."],
  "causes": ["KC-002", "RC-015"],
  "victory": "A counter bare enough to roll pastry on, an empty basket "
             "per bedroom beneath it, and no clean clothing left in the "
             "room.",
  "next": "LRS-004",
  "art": "a completely bare laundry folding counter with empty baskets "
         "stacked underneath it and six spare hangers on a rail at one "
         "end"},

 {"id": "LRA-008", "zone": "Folding Surface",
  "title": "NAME WHO DELIVERS THE BASKET", "minutes": 30, "players": "1",
  "six_s": "Standardize",
  "goal": "Split folding and delivery into two named jobs so the folder "
          "does not end up owning the whole chain.",
  "why": "One person folding and delivering for everybody is how the "
         "baskets quietly become where clean clothes live.",
  "inputs": ["nothing beyond a short conversation with the household"],
  "steps": [
   "Name the folder for this load and the deliverer for each basket, out "
   "loud, even if they are the same person today.",
   "Agree the delivery happens the same evening the basket is filled, "
   "not whenever there is time.",
   "Photograph the bare counter and keep the photo somewhere visible, so "
   "'clear' has one agreed picture rather than a guess.",
   "Check the wardrobes the baskets deliver to are not already full; if "
   "they are, that capacity problem belongs to the bedroom, not this "
   "counter."],
  "causes": ["RC-013", "KC-007"],
  "victory": "A named folder and a named deliverer for every load, and "
             "no basket sits full past the same evening it was filled.",
  "next": "LRA-007",
  "art": "an empty laundry folding counter with a small photograph taped "
         "inside a nearby cupboard door showing the counter in its bare "
         "state"},

 {"id": "LRA-009", "zone": "Hanging and Air-Dry Zone",
  "title": "STRIP THE RACK AND FOLD IT FLAT", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take off everything washed before today, put dry things away, "
          "empty the tray, and fold the rack flat.",
  "why": "A rack that never folds flat has become a second wardrobe, not "
         "a drying rack.",
  "inputs": ["nothing beyond fifteen minutes and the rack itself"],
  "steps": [
   "Take everything off the rack that was washed before today, put the "
   "dry things away, wipe out the drip tray, fold the rack flat against "
   "the wall, and put six spare hangers on the rail.",
   "Check the drip tray corners for standing water before you fold the "
   "rack away.",
   "Confirm nothing at all is left hanging when you are done."],
  "causes": ["KC-009", "KC-001"],
  "victory": "The rack folded flat with dry bars, an empty tray beneath "
             "it, and nothing hanging that was not washed today.",
  "next": "LRS-005",
  "art": "a drying rack folded completely flat against a wall with an "
         "empty drip tray resting beside it"},

 {"id": "LRA-010", "zone": "Hanging and Air-Dry Zone",
  "title": "GIVE THE RACK ROOM TO BREATHE", "minutes": 30,
  "players": "1", "six_s": "Shine",
  "goal": "Space items apart on the rack, add air movement if the room "
          "is damp, and move overflow to the wardrobes it belongs in.",
  "why": "Items hung overlapping never dry in the middle, and a room "
         "with no moving air turns the rack into a permanent fixture.",
  "inputs": ["a small fan, if the room has no window or extractor",
             "space in the household's wardrobes for what the rack is "
             "holding long-term"],
  "steps": [
   "Hang each item with a hand's width of space from the next, rather "
   "than pressed together.",
   "If the room has no window or extractor, point a small fan along the "
   "rack rather than reaching for a bigger rack.",
   "Sort what has been up longer than a week: if the wardrobe it belongs "
   "in is full, fix that capacity problem directly instead of leaving "
   "the item on the rack.",
   "Wipe the wall and floor behind the rack where splash marks have "
   "built up."],
  "causes": ["KC-003", "KC-007"],
  "victory": "Every item on the rack has visible space around it, air "
             "is moving through the room, and nothing has been up longer "
             "than a week without a reason.",
  "next": "LRA-009",
  "art": "garments hanging on a drying rack with a clear hand's width of "
         "space between each one, a small fan pointed along the length "
         "of the rack"},

 {"id": "LRA-011", "zone": "Utility and Cleaning Zone",
  "title": "HANG THE TOOLS AND OUTLINE THEIR HOMES", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Hang the broom, mop and dustpan heads up, mark an outline "
          "behind each, gather every attachment into one caddy, and "
          "empty the bucket into its taped square.",
  "why": "A tool that leans against a wall is a tool that will end up on "
         "the floor, and an outline is the only thing that reports a "
         "missing tool from the doorway.",
  "inputs": ["a marker, paint pen, or tape for the outlines",
             "a labelled caddy", "tape for the bucket's floor square"],
  "steps": [
   "Hang the broom, mop and dustpan heads up and mark an outline behind "
   "each one, gather every vacuum attachment into one labelled caddy, "
   "and empty the bucket and stand it inside a taped square on the "
   "floor.",
   "Knock any wound hair or lint off the dustpan and broom before you "
   "hang them.",
   "Confirm the outlines are visible from the doorway, not hidden behind "
   "the door swing."],
  "causes": ["KC-002", "KC-006"],
  "victory": "Three handles off the floor with outlines showing behind "
             "them, every attachment in one caddy, and an empty bucket "
             "standing in its square.",
  "next": "LRS-006",
  "art": "a broom, mop and dustpan hanging heads up on a wall with a "
         "painted outline behind each, a labelled caddy of vacuum "
         "attachments nearby, an empty bucket standing in a taped floor "
         "square"},

 {"id": "LRA-012", "zone": "Utility and Cleaning Zone",
  "title": "SEPARATE THE CHEMICALS FROM THE BUCKET", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Move drain cleaner and bleach up off the floor, away from the "
          "mop bucket, and confirm nothing leans behind the door.",
  "why": "Drain cleaner and bleach kept at floor level next to the mop "
         "bucket get knocked, decanted or mixed during a rinse, and "
         "anything leaned behind a door swings down at head height.",
  "inputs": ["a shelf above the bucket for chemicals",
             "wall hooks for anything currently leaning"],
  "steps": [
   "Move drain cleaner and bleach onto a shelf above the bucket, never "
   "inside or beside it.",
   "Walk the room for anything leaning against a wall behind a door, and "
   "hang or bin it instead.",
   "Check the shelf bracket under the chemicals for corrosion from "
   "fumes, and fix or replace it if it has started to give.",
   "Wipe the bottle exteriors and the shelf, keeping the cloth off the "
   "labels so they stay readable."],
  "causes": ["KC-010", "KC-005"],
  "victory": "Drain cleaner and bleach sit on a shelf above the bucket, "
             "nothing leans behind the door, and the shelf bracket is "
             "sound.",
  "next": "LRA-011",
  "art": "a laundry chemical shelf holding drain cleaner and bleach well "
         "above an empty mop bucket standing on the floor beneath"},

 {"id": "LRA-013", "zone": None, "title": "THE FULL LAUNDRY SAFETY WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk the whole room once, standing where you use it, and "
          "confirm nothing hot, wet, heavy or overlooked could hurt "
          "somebody.",
  "why": "The things that hurt people in this room, a blocked duct, a "
         "hard fill hose, a chemical within reach, a tool that swings "
         "down, do not show up unless you look on purpose, and a room "
         "used every week stops getting looked at.",
  "inputs": ["nothing beyond thirty minutes and a working set of hands"],
  "steps": [
   "Check the dryer duct and both fill hoses for the signs named in the "
   "Washer and Dryer zone: soft packing, a hard or bulged collar.",
   "Check the pod tub and any chemical shelf are latched or out of a "
   "child's reach, and that bleach sits apart from anything ammonia "
   "based.",
   "Check the drying rack and its drip tray are not standing in water on "
   "a hard floor.",
   "Check nothing leans against a wall behind a door, and every "
   "long-handled tool is hung.",
   "Fix anything you find right there, or write it down with today's "
   "date if it needs a part you do not have to hand."],
  "causes": ["KC-010", "RC-017"],
  "victory": "You can name, out loud, that the duct, the hoses, the "
             "chemicals, the rack and every leaning tool have each been "
             "checked today.",
  "next": "LRA-002",
  "art": "a wide view of a whole laundry room with a hand pointing in "
         "turn at a dryer duct, a chemical shelf and a wall-mounted "
         "broom, everything settled in its correct state"},

 {"id": "LRA-014", "zone": None, "title": "THE FIVE MINUTE FETCH TEST",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Fetch the item you use most in this room and count the "
          "movements it actually takes, then fix whichever one failed.",
  "why": "Extra steps to reach an everyday item are a cost paid every "
         "single time, and they hide in a room nobody times.",
  "inputs": ["nothing beyond five minutes standing in the room"],
  "steps": [
   "Fetch the everyday detergent, the broom, and one clean hanger, "
   "counting the movements each one actually takes.",
   "Anything past two movements, bending, unstacking, reaching overhead, "
   "moving something else first, gets a closer spot today.",
   "Confirm the shortest person who uses this room could fetch the same "
   "three items without climbing or asking for help."],
  "causes": ["KC-004", "KC-006"],
  "victory": "The three everyday items each take two movements or fewer "
             "to fetch, and the shortest household member can reach all "
             "three unaided.",
  "next": "LRA-013",
  "art": "a hand reaching directly for a bottle of detergent on an "
         "easily reached shelf, no stool or extra items in the way"},

 {"id": "LRA-015", "zone": None, "title": "NAME WHO RUNS LAUNDRY DAY",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Agree, out loud, who starts loads, who moves them, who folds "
          "and who delivers, so the room stops depending on whoever "
          "notices first.",
  "why": "Two people running one room by two designs is a permanent "
         "half-finished state, and a room with no named owner depends on "
         "whoever notices first.",
  "inputs": ["nothing beyond a short conversation with the household"],
  "steps": [
   "Name, out loud, who starts a load, who moves it to the dryer or the "
   "rack, who folds, and who delivers each basket.",
   "Agree on one dosing habit for the detergent cap, since two habits "
   "produce two different washes from the same jug.",
   "Confirm the agreement against the room's own standard cards rather "
   "than leaving it as a conversation nobody can point back to.",
   "Revisit the names the next time a load sits forgotten, rather than "
   "assuming the first agreement will hold forever."],
  "causes": ["RC-013", "KC-012"],
  "victory": "Every stage of a wash day has one named person, and both "
             "people who dose detergent use the same inked line.",
  "next": "LRA-014",
  "art": "a small chore board mounted on the wall beside the washing "
         "machine holding four tokens in a row, one for each stage of a "
         "wash day"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a laundry room.
# ---------------------------------------------------------------------------

EVENTS = [
 ("LRE-001", "LAUNDRY DAY WITH A SICK KID",
  "A child is sick overnight, and every sheet, towel and set of pyjamas "
  "in the house needs washing before the next round starts.",
  ["LRZ-001", "LRZ-003"],
  "Both drums were already empty when the first load went in, and the "
  "sorting bags had room to take the sudden extra without spilling onto "
  "the floor.",
  "If a load had to wait because the drum was already full, or the bags "
  "overflowed onto the floor, the machines or the sorting wall were not "
  "being kept at standard before this happened. Draw LRA-001 or LRA-005.",
  "a washing machine mid cycle with a full load of white bedding and "
  "pyjamas visible through the glass door, an empty laundry basket "
  "standing ready beside it"),
 ("LRE-002", "THE OVERNIGHT GUEST'S TOWELS",
  "A guest stays the night and leaves behind two extra towels and a hand "
  "wash only sweater that needs to dry before they collect it.",
  ["LRZ-004", "LRZ-005"],
  "The extra towels found space on the counter without displacing "
  "anything already there, and the rack had room for one more hand wash "
  "item without crowding what was already hanging.",
  "If the counter had to be cleared of other things first, or the rack "
  "was already full, the counter or the rack were not being kept clear "
  "as their own standard. Draw LRA-007 or LRA-009.",
  "two folded guest towels sitting on a laundry folding counter beside a "
  "single hand wash sweater hanging from a drying rack with visible "
  "space around it"),
 ("LRE-003", "THE MUDDY SPORTS KIT",
  "A sports kit comes home caked in mud and grass, tracking dirt across "
  "the laundry room floor on the way to the hamper.",
  ["LRZ-003", "LRZ-006"],
  "The kit went straight into its own bag without touching the floor "
  "for long, and the broom and dustpan were exactly where they belonged "
  "to clear the mess in under a minute.",
  "If the mud sat on the floor while you hunted for the broom, the "
  "cleaning tools were not hanging in their outlines where this event "
  "needed them. Draw LRA-011.",
  "a muddy sports kit bag sitting open beside a scattering of dried mud "
  "and grass on a laundry room floor, a broom visible hanging on a "
  "nearby wall hook"),
 ("LRE-004", "THE HOSE THAT LET GO",
  "A fill hose splits without warning and sprays water across the floor "
  "before anyone reaches the shutoff valve.",
  ["LRZ-001", "LRZ-006"],
  "The hoses had been checked recently enough that this was a surprise "
  "rather than an overdue warning, and the mop and bucket were within "
  "reach to clear the water fast.",
  "If the hose had already looked hard or bulged at the collar before it "
  "split, the machine's own safety check was overdue. Draw LRA-002. If "
  "the mop was not where it belonged, draw LRA-011.",
  "a burst rubber fill hose spraying water across a laundry room floor "
  "near a washing machine, a mop and bucket visible standing nearby "
  "against the wall"),
 ("LRE-005", "THE WEEK WITH NO TIME TO FOLD",
  "Three dry loads finish back to back during a busy week and nobody has "
  "ten minutes to fold any of them.",
  ["LRZ-004", "LRZ-003"],
  "The baskets from each load found a place under the counter without "
  "one being tipped onto the floor, and the sorting bags kept accepting "
  "new dirty clothes without backing up.",
  "If clean laundry ended up in a pile on the floor because the baskets "
  "were already full, the one-basket-per-bedroom delivery habit had "
  "already slipped before this week started. Draw LRA-008.",
  "three full laundry baskets of dry clothes stacked neatly under a "
  "folding counter, none of them tipped over or spilling onto the "
  "floor"),
 ("LRE-006", "THE COLD SNAP WOOL SURGE",
  "The temperature drops overnight and every wool jumper and hand wash "
  "item in the house needs washing and drying at once.",
  ["LRZ-002", "LRZ-005"],
  "A wool safe detergent was already on the shelf rather than needing an "
  "emergency trip to the shop, and the drying rack had room to take the "
  "sudden run of hand wash items.",
  "If there was no wool safe detergent in the house, or the rack was "
  "already full of things that should have come down days ago, draw "
  "LRA-003 or LRA-009.",
  "a row of wool jumpers laid flat to dry across a drying rack, a "
  "bottle of wool safe detergent standing on a nearby shelf"),
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
        "related": {"standard": f"LRS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your laundry "
                       "room, then turn to that root cause card. If two "
                       "are true, take the one you could change this "
                       "week.",
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
    standard_id = (f"LRS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"LRS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "LRR-001", "title": "THE LAUNDRY ROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START AT THE MACHINES.",
        "objective": "Laundry is the one job that arrives dirty, sits "
                     "wet, and only counts as finished once it is back "
                     "in a drawer. This card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"LRZ-001 Washer and Dryer. {start_tip['text']}" if start_tip
            else "LRZ-001 Washer and Dryer. Every other zone in this room "
                 "is waiting on the machines being ready to take a "
                 "load."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your laundry room. Put the rest back.",
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
        "safety_first": "Do LRA-013 The Full Laundry Safety Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "the duct, the hoses, the chemicals, the rack "
                        "and every hung tool in the room.",
        "related": {"contents": "LRZ-001 to LRZ-006, LRF-001 to LRF-018, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, LRA-001 to LRA-015, "
                                 "LRS-001 to LRS-006, LRE-001 to LRE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "laundry room in its settled state, washer, "
                           "dryer, detergent shelf, sorting bags, "
                           "folding counter, drying rack and cleaning "
                           "tools all visible in one frame, everything "
                           "put away",
                "must_show": ["all six zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the six zones is. If two are "
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
    # exist, the same two-pass shape the Kitchen and Entryway generators use.
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
    return {"deck": "laundry", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (build_kitchen_deck.py,
    build_entryway_deck.py)."""
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

    assert any(c["id"] == "LRA-013" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This room's zone list must be exactly the Manual's six, in the
    # Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 6, (
        "this room's zone count moved in the Manual; ZONES above must be "
        "re-derived, not assumed")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        laundry ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
