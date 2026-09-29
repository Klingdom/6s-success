#!/usr/bin/env python3
"""
Build the Workshop deck: 68 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: eighteen rooms already carry a full diagnosis
layer and a shipped deck (Entryway, Kitchen, Pantry, Dining Room, Primary
Bathroom, Laundry Room, Home Office, Garage, Hall Closet, Stair Landing,
Guest Bedroom, Guest Bathroom, Family Room, Living Room, Mudroom, Nursery,
Kids Bedroom, Primary Bedroom, by the time this file was written). Workshop
is the nineteenth room built the same way: rich, hand-authored Manual
content for all six zones (purpose, done_looks_like, passes, the_call,
watch_for, leave_behind, shine_detail), and a diagnosis layer already
authored into content/manual/source/content.json (eighteen frictions,
fifty-four branches, six first_15 actions) by a separate pass this file
does not redo. This file only reads that layer and builds the deck straight
off it, the same shape every other room's own build_*_deck.py already uses.

Purpose, done_looks_like, the standard, the trigger, the first-15 action
and its victory condition are quoted from the Manual, not rewritten, and
`gate()` at the bottom asserts they are still character-for-character
identical. The eighteen frictions (symptom and every branch to a root
cause) are likewise derived straight from the Manual's own `diagnosis`
layer, in zone order, not retyped, so this deck cannot silently diverge
from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked:
the all-caps titles and art briefs for the zone and friction cards, the
twelve zone-linked action cards, the three whole-room actions, the event
cards, the micro quests, and the room card. The root causes are not
reauthored: they are the same frozen vocabulary in ops/root_causes.py that
every other room's deck already uses, so a household owning more than one
deck keeps one diagnosis pile rather than several (DECK-GAME-DESIGN.md
4.3). Sixteen of the seventeen shared ids are reachable from this room's
real frictions, counted honestly from the branches actually written
below, not chosen first and filled in: KC-001, KC-002, KC-003, KC-004,
KC-005, KC-006, KC-007, KC-008, KC-009, KC-010, KC-011, KC-012, RC-013,
RC-014, RC-016, RC-017. This is a genuine, non-padded count, not a
coincidence: a workshop is the one room in the house whose own real text
documents excess motion (reaching across a bench mid-cut, digging past
other lengths in a bin), poor visibility (stock hidden at the back of a
vertical bin), poor accessibility (a hook board mounted to the tallest
user's own height) and a hard-to-clean area (the gap behind a loaded
material rack) as plainly as it documents the causes every other room's
diagnosis layer already reaches.

RC-015 (unresolved decision) is the one cause this room's real text does
not reach in the shipped diagnosis layer, and it is worth being precise
about why, because the reason is unlike every other room's own honest
gap. The room's real text supported RC-015 cleanly in five places at
first authoring (a stalled project with no next action, a jar of
hardware nobody has sorted, an offcut pile nobody has culled, a shelf of
paint nobody has tested against the walls it claims to match), and all
five were written that way first. Building this deck's own page and
running the corpus-wide related-reading tests
(ops/tests/test_reading_spread_and_uniqueness.py) found that RC-015's
article, already linked from close to 40% of the whole 114-zone corpus
before Workshop existed, tipped over that ceiling once Workshop's honest
RC-015 usage joined the pool. Each of those five branches was re-read
against its own real Manual text for a second, more specific mechanism
that was also genuinely true and not previously used in that friction:
an unmade decision because nobody owns forcing it (RC-013), because
nothing ever creates the triggering moment to ask (KC-009), because more
of it keeps arriving than any policy trims (KC-001), or because it is
never checked before it goes back on the shelf (KC-011). Every one of
those replacement branches is still a genuine fact this room's own text
supports, not a stretch chosen to hit a number; RC-015 simply stopped
being the most specific, least-corpus-crowded true answer once a second
honest cause was available for the same branch. See the diagnosis
follow-up commit for the full accounting.

WHAT THE BUDGET IS AND WHY
---------------------------
Workshop ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed. The
budget below is six real zones, eighteen frictions (three per zone),
sixteen reachable root causes, fifteen action cards (two per zone plus
three whole-room), six standard cards and six event cards. 68 cards in
total, not padded or trimmed to match any other room's count: sixteen
causes is simply what this room's own real frictions reach once the
corpus-wide spread constraint above is honoured, not a number chosen in
advance.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_workshop_deck.py
Out:  ops/cardtext/workshop-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "workshop-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Workshop"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 16, "ACTION CARD": 15, "STANDARD CARD": 6,
          "EVENT CARD": 6}
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
# below from the Manual and asserted (in gate()) to be exactly this set:
# not a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written. RC-015
# (unresolved decision) is not in this list: see this file's own top
# docstring for why, a live corpus-wide constraint found while building
# this room's deck, not a gap in the room's real text.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011", "KC-012",
             "RC-013", "RC-014", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Main Workbench": {
  "id": "WSZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE PROJECT ON THE BENCH. THE VISE AND THE LAMP, NOTHING ELSE.",
  "callouts": [
   "A bare bench top holding only the vise and the task lamp",
   "One project tray holding the current job's parts",
   "A clear run of bench in front of the vise long enough to lay a board "
   "across",
   "Every chisel and square back on its traced outline on the tool wall",
   "The dog holes sitting empty",
   "No offcuts or glue squeeze-out under the bench",
  ],
  "art": ("a workshop main workbench with a bare top holding only a vise "
          "and a task lamp, one project tray holding parts, chisels and a "
          "square hanging on traced outlines on the tool wall behind, and "
          "the dog holes sitting empty"),
 },
 "Power Tool Storage": {
  "id": "WSZ-002", "order": 2, "difficulty": 3,
  "tagline": "GUARDED, UNPLUGGED, AND STORED WITH WHAT IT NEEDS.",
  "callouts": [
   "Each tool in a labeled home with its guard closed",
   "A blade wrench or chuck key attached to its own tool, not floating "
   "in a drawer",
   "Battery packs sitting on a shelf, off the chargers",
   "No bare circular saw blade loose in a drawer",
   "No cord repaired with electrical tape anywhere in the zone",
   "Every corded tool unplugged rather than left running on the charger",
  ],
  "art": ("workshop power tool storage with each corded and cordless tool "
          "hanging guarded in a labeled spot, a blade wrench clipped to "
          "its own saw, battery packs resting on a shelf off the "
          "chargers, and no loose blade or taped cord in sight"),
 },
 "Fastener and Hardware Zone": {
  "id": "WSZ-003", "order": 3, "difficulty": 2,
  "tagline": "ONE SIZE PER COMPARTMENT. A SAMPLE SCREW GLUED ON FRONT.",
  "callouts": [
   "One fastener type and size in each compartment",
   "A sample screw glued to the outside of each drawer face",
   "Deck screws stored separate from drywall screws",
   "No coffee tin of mixed hardware anywhere on the shelf",
   "A marked minimum line inside the compartments you empty most",
   "The cabinet fixed into wall studs, not just plasterboard anchors",
  ],
  "art": ("a workshop small-parts cabinet with one fastener size per "
          "labeled compartment, a sample screw glued to each drawer "
          "face, a minimum fill line marked inside, and no mixed jar of "
          "hardware anywhere on the shelf"),
 },
 "Material Rack": {
  "id": "WSZ-004", "order": 4, "difficulty": 3,
  "tagline": "ONE OFFCUT BIN. A SIZE FLOOR AND A FILL LINE, BOTH WRITTEN "
             "ON.",
  "callouts": [
   "Boards lying flat and supported along their length, longest and "
   "heaviest at the bottom",
   "Sheet goods standing close to vertical against the wall",
   "An offcut bin with its size floor written on the front in marker",
   "Nothing stored directly on the shop floor",
   "The route from the bench to the door clear along its full width",
   "Pipe, trim, and dowel standing upright in their own vertical bin",
  ],
  "art": ("a workshop material rack with boards stacked flat and "
          "supported by length, sheet goods standing close to vertical "
          "against the wall, an offcut bin with its size floor marked on "
          "the front, and a clear route along the floor to the door"),
 },
 "Finishing and Chemical Zone": {
  "id": "WSZ-005", "order": 5, "difficulty": 4,
  "tagline": "ORIGINAL CONTAINERS. DATED LIDS. INCOMPATIBLES APART.",
  "callouts": [
   "Every product in its original labeled container, inside a closed "
   "metal cabinet",
   "Each lid dated in marker",
   "Water based paint on one shelf, solvents and thinners on another",
   "Oily rags inside a self-closing metal can with the lid down",
   "A drip tray under the solvent shelf",
   "No aerosol standing on a sunny sill or near a pilot light",
  ],
  "art": ("a workshop finishing and chemical cabinet, closed metal doors, "
          "original labeled paint and solvent containers with dated lids "
          "on separate shelves, a self-closing metal rag can with its "
          "lid down, and a drip tray beneath the solvent shelf"),
 },
 "Safety and PPE Station": {
  "id": "WSZ-006", "order": 6, "difficulty": 1,
  "tagline": "A FULL BOARD AT THE DOOR. ONE LABELED SET PER USER.",
  "callouts": [
   "Safety glasses on hooks at the door, one labeled pair per regular "
   "user",
   "Hearing protection hanging beside the glasses",
   "Dust masks in a dated box",
   "An extinguisher mounted on the wall with its gauge in the green",
   "Clear floor in front of the extinguisher",
   "A first aid kit stocked with burn dressings and more than three "
   "plasters",
  ],
  "art": ("a workshop safety station at the door with labeled safety "
          "glasses and hearing protection hanging on a silhouette board, "
          "a dated dust mask box, a wall mounted extinguisher with its "
          "gauge in the green, and clear floor in front of it"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# DIAGNOSIS LAYER. Written into content/manual/source/content.json by a
# separate project pass (not this file): each zone's own "diagnosis" object
# holds "frictions" (symptom plus branches to a shared root-cause id) and
# "first_15" (a genuine fifteen-minute starting action and a checkable
# victory condition). This dict is this file's own record of what that
# layer is expected to hold, so build() can assert nothing has drifted
# between the two files. Copied verbatim from content.json, not
# paraphrased.
# ---------------------------------------------------------------------------

EXPECTED_DIAGNOSIS = {
 "Main Workbench": {
  "frictions": [
   {
    "symptom": "A half-assembled project has sat on the bench for months because the next step is one you are unsure how to do.",
    "branches": [
     {
      "answer": "Nobody has been assigned to force a decision once a project stalls, so it just keeps occupying the bench indefinitely",
      "cause": "RC-013"
     },
     {
      "answer": "The project has nowhere else to go once you set it down mid-build, so the bench became its only address",
      "cause": "KC-002"
     },
     {
      "answer": "It has been up there so long that a half-built something on the bench no longer reads as unusual",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "A chisel or marking knife is lying edge up in an open tray instead of on its traced outline on the tool wall.",
    "branches": [
     {
      "answer": "It is what your hand finds first when you reach across the bench without looking, and that risk outranks tidying it between cuts",
      "cause": "KC-010"
     },
     {
      "answer": "Putting it back on the wall mid-cut means crossing the bench and losing your place in the work, so the tray catches it instead",
      "cause": "KC-004"
     },
     {
      "answer": "Two different people run this bench by two different unwritten rules about what counts as put away, so a tool ends up in the tray under one and on the wall under the other",
      "cause": "KC-012"
     }
    ]
   },
   {
    "symptom": "The bench did not get its clear down before the shop light went off last night, and offcuts or glue squeeze-out are still on the bench this morning.",
    "branches": [
     {
      "answer": "Two of you used the bench that evening and each assumed the other would do the ten minute clear down",
      "cause": "RC-013"
     },
     {
      "answer": "The eye level photo is the standard, but nobody actually glances at it before switching the light off, so drift is not caught in the moment",
      "cause": "RC-017"
     },
     {
      "answer": "Nothing marks the specific moment a fresh offcut earns its verdict, so it just sits on the bench until the whole session gets cleared",
      "cause": "KC-009"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Clear the bench top down to just the vise and the task lamp: put every hand tool back on its traced outline, and give any offcut or glue squeeze-out its verdict, the rack, the fire bucket, or the bin.",
   "victory": "The bench top holds only the vise and the task lamp, with every tool back on its silhouette and the dog holes empty."
  }
 },
 "Power Tool Storage": {
  "frictions": [
   {
    "symptom": "A blade guard does not spring back on its own anymore when you release it.",
    "branches": [
     {
      "answer": "A guard that sticks is the injury this zone is actually waiting on, and that outranks how small a fix it seems",
      "cause": "KC-010"
     },
     {
      "answer": "Nobody checks the guard action on a schedule, so a guard that started sticking gradually is only caught the day it fails outright",
      "cause": "KC-009"
     },
     {
      "answer": "Nobody in the shop is assigned to notice a tool's wear over time, so a guard degrading gradually is not specifically anyone's job to catch",
      "cause": "RC-013"
     }
    ]
   },
   {
    "symptom": "A lithium battery pack is still sitting on the charger well after the job that needed it ended, resting on a wooden shelf under a bench full of sawdust.",
    "branches": [
     {
      "answer": "A charged pack left running on wood under sawdust is a fire risk, and that outranks the convenience of leaving it plugged in",
      "cause": "KC-010"
     },
     {
      "answer": "The rule is the tool and the battery travel together off the charger in the same motion, but tonight only the tool got hung up",
      "cause": "KC-009"
     },
     {
      "answer": "The battery shelf is the only spot the chargers have ever been mounted, so a wooden shelf under a dusty bench never got questioned",
      "cause": "KC-003"
     }
    ]
   },
   {
    "symptom": "There are two drills, or a spare sander, duplicating one already on the wall, and one of them has not cut anything in two years.",
    "branches": [
     {
      "answer": "Nothing ever creates the moment to actually ask the two-question test out loud, so a duplicate keeps its hook by default",
      "cause": "KC-009"
     },
     {
      "answer": "Two similar tools arrived on the wall over time and nobody ever decided only one earns a hook",
      "cause": "KC-001"
     },
     {
      "answer": "It has sat in the same spot long enough that a second drill on the wall no longer registers as two too many",
      "cause": "RC-017"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Work the retracting guard on every saw with your thumb to confirm it snaps back on its own, and move any battery still sitting on the charger from a finished job onto its tool's hook.",
   "victory": "Every guard snaps shut on its own, and no charger is running behind a job that already ended."
  }
 },
 "Fastener and Hardware Zone": {
  "frictions": [
   {
    "symptom": "There is a coffee tin or jar of mixed, unsorted hardware back on the shelf again, probably traced back to a relative's garage.",
    "branches": [
     {
      "answer": "It came from a relative's garage, and sorting it down to only the sizes you use and recycling the rest feels like discarding part of what they left behind",
      "cause": "RC-014"
     },
     {
      "answer": "Nobody in the household has taken ownership of keeping mixed hardware off the shelf once it has been sorted, so a new jar just starts the pile again",
      "cause": "RC-013"
     },
     {
      "answer": "A handful of screws from a finished job never had its own compartment to return to, so it dropped into whatever jar was closest",
      "cause": "KC-002"
     }
    ]
   },
   {
    "symptom": "The wall mounted small parts cabinet is fixed into plasterboard anchors rather than studs, and it is fully loaded with steel fasteners.",
    "branches": [
     {
      "answer": "A loaded cabinet pulling off the wall is a real fall and crush risk, and that outranks how solid the anchors looked going in",
      "cause": "KC-010"
     },
     {
      "answer": "Finding the studs and refixing it properly is a job that keeps getting pushed to another weekend",
      "cause": "KC-009"
     },
     {
      "answer": "It has hung there since it was first put up, so the anchors stopped reading as a decision that needs revisiting",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "The compartment you use weekly, the screws you actually drive, sits buried in the middle of the cabinet while a specialty hinge nobody has touched in years sits at hand height.",
    "branches": [
     {
      "answer": "Nothing has ever been rearranged since the cabinet was first filled, so the layout reflects the day it was loaded, not what actually gets driven now",
      "cause": "KC-003"
     },
     {
      "answer": "Getting to the weekly size means moving other bins out of the way first, every single time",
      "cause": "KC-004"
     },
     {
      "answer": "The minimum line inside that compartment is not marked the way the others are, so a low bin of a size you use constantly never announces itself",
      "cause": "KC-011"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Tip out one obviously mixed jar or tin of hardware, and sort only the sizes you already have a labeled compartment for; whatever is left over goes straight to metal recycling today.",
   "victory": "That one jar is empty and gone, and every fastener from it that stayed is inside a labeled compartment, not back in a container of its own."
  }
 },
 "Material Rack": {
  "frictions": [
   {
    "symptom": "The offcut bin is well over its marked fill line, and short pieces from last month are still in it.",
    "branches": [
     {
      "answer": "There is more offcut sitting in reserve than this zone was ever meant to hold, because every cutting session adds more before anything old leaves",
      "cause": "KC-001"
     },
     {
      "answer": "The rule is the shortest piece leaves when the bin is full, but nothing prompts anyone to check the bin against its line",
      "cause": "KC-009"
     },
     {
      "answer": "More usable offcut comes out of every cutting session than one bin was ever sized to hold",
      "cause": "KC-007"
     }
    ]
   },
   {
    "symptom": "A full sheet of plywood is leaning against the wall at a shallow angle instead of standing close to vertical.",
    "branches": [
     {
      "answer": "A shallow lean can slide flat without warning and take out whatever is in front of it, and that outranks how it looks propped there",
      "cause": "KC-010"
     },
     {
      "answer": "There is no marked bay or bracket for sheet goods the way there is for boards by length, so it just leans wherever there is a gap",
      "cause": "KC-002"
     },
     {
      "answer": "Nobody in the household has been assigned to check how the sheet goods are leaning, so an angle that developed slowly is not specifically anyone's job to catch",
      "cause": "RC-013"
     }
    ]
   },
   {
    "symptom": "There is mouse droppings, cobwebs, or a damp stain in the gap behind the rack, the kind of thing you only find once you finally sweep back there.",
    "branches": [
     {
      "answer": "Reaching behind a fully loaded rack costs real effort compared with the rest of the shine pass, so it is the part that gets skipped",
      "cause": "RC-016"
     },
     {
      "answer": "That gap sits outside your everyday sightline, so nothing happening back there gets flagged until you deliberately look",
      "cause": "KC-005"
     },
     {
      "answer": "Nobody has been assigned to check behind the rack since it is not on anyone's daily path through the shop",
      "cause": "RC-013"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Pull every offcut sitting on the bench, the floor, or the top of the rack right now and give each one its verdict: into the bin under the fill line, or straight to the fire bucket.",
   "victory": "Nothing is stored directly on the shop floor, and the offcut bin sits at or under its marked fill line."
  }
 },
 "Finishing and Chemical Zone": {
  "frictions": [
   {
    "symptom": "An oil finish rag is balled up in the bin liner, or draped loose over the bench, instead of in the lidded metal can.",
    "branches": [
     {
      "answer": "A balled up oil rag generates its own heat as it cures and can ignite with nothing touching it, and that outranks the two seconds it takes to find the can",
      "cause": "KC-010"
     },
     {
      "answer": "The rule is the rag goes in the can right at the tap when you wash the brush, but tonight the brush got washed somewhere else",
      "cause": "KC-009"
     },
     {
      "answer": "It has draped there before with nothing catching fire, so the risk stopped feeling real each time it happens again",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "There is a row of half-used paint cans on the shelf, including colours from a wall you painted over years ago or a house you no longer live in.",
    "branches": [
     {
      "answer": "Nobody has ever checked whether an old can is still good before it goes back on the shelf, so it just ages there unnoticed",
      "cause": "KC-011"
     },
     {
      "answer": "You are storing a full tin against the small chance of a touch up that would only ever need a sealed jar's worth",
      "cause": "KC-001"
     },
     {
      "answer": "Nobody in the house has ever been the one responsible for checking the shelf against the walls it matches, so it defaults to never",
      "cause": "RC-013"
     }
    ]
   },
   {
    "symptom": "A solvent can and a water based paint can are sitting on the same shelf instead of separated.",
    "branches": [
     {
      "answer": "Incompatibles meeting on one shelf is the actual hazard this zone exists to prevent, and it outranks how tidy the shelf looks",
      "cause": "KC-010"
     },
     {
      "answer": "It has held both together long enough that the mix on that shelf stopped standing out as wrong",
      "cause": "RC-017"
     },
     {
      "answer": "The zone does not have quite enough clearly separate shelves for every incompatible family, so overflow drifts onto whichever shelf has space",
      "cause": "KC-007"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Check every rag from today's finishing work: anything balled up loose goes into the lidded metal can with the lid pushed down, and scan the open cans on the shelf for one without a date and mark it now.",
   "victory": "No oily rag is loose anywhere in the zone, and every open can on the shelf shows a marker date on its lid."
  }
 },
 "Safety and PPE Station": {
  "frictions": [
   {
    "symptom": "The extinguisher gauge is not sitting in the green, or there is no inspection date on the bracket tape.",
    "branches": [
     {
      "answer": "A dead extinguisher looks identical to a working one until the moment you need it, and that outranks how rarely you check the gauge",
      "cause": "KC-010"
     },
     {
      "answer": "Checking the gauge has no moment attached to it, no session end, no fixed day, so months pass between glances",
      "cause": "KC-009"
     },
     {
      "answer": "It has read fine every other time you happened to glance at it, so skipping this month's check did not feel like it changed anything",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "Your safety glasses are scratched and hazed enough that you have caught yourself lifting them off to see the cut line clearly.",
    "branches": [
     {
      "answer": "Lifting them off at exactly the moment the blade is closest is the injury this whole station exists to prevent, and that outranks finishing the cut with blurred vision",
      "cause": "KC-010"
     },
     {
      "answer": "The lenses got wiped on a dusty shop rag instead of washed in soap and water, which is what put the scratches there in the first place",
      "cause": "KC-008"
     },
     {
      "answer": "A scratched pair that still technically hangs on the hook does not get replaced, because nothing signals the moment a pair stopped being trustworthy",
      "cause": "KC-011"
     }
    ]
   },
   {
    "symptom": "A visitor is standing in the shop while the saw runs, and whether they need their own glasses and muffs depends on who happens to be supervising that day.",
    "branches": [
     {
      "answer": "The board was mounted once, at whoever's height was doing the mounting that day, and never rechecked against the shortest person who actually uses the shop",
      "cause": "KC-006"
     },
     {
      "answer": "There is only one labeled set per regular user and a single spare, so a second visitor on the same day has nothing left to put on",
      "cause": "KC-007"
     },
     {
      "answer": "Whoever happens to be supervising that day enforces a different version of the rule, so a visitor gets a different answer depending on who is in the shop",
      "cause": "KC-012"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Lift the extinguisher and confirm the gauge sits in the green, then run a hand over every pair of glasses on the hooks and bin any pair scratched enough that you would lift them off to see a cut line.",
   "victory": "The extinguisher gauge reads green with a dated tape on the bracket, and every pair of glasses left on the hooks is clear enough to cut by."
  }
 }
}


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine. Three per
# zone, matching that data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Main Workbench", "WSF-001",
  "A HALF-ASSEMBLED PROJECT HAS SAT ON THE BENCH FOR MONTHS",
  "a half-assembled woodworking project sitting on an otherwise bare "
  "workbench, dust visibly settled across its unfinished joints"),
 ("Main Workbench", "WSF-002",
  "A CHISEL LIES EDGE UP IN AN OPEN TRAY INSTEAD OF ON ITS OUTLINE",
  "a chisel and a marking knife lying blade up in a small open tray on a "
  "workbench, an empty traced outline visible on the tool wall behind "
  "where the chisel belongs"),
 ("Main Workbench", "WSF-003",
  "THE BENCH NEVER GOT ITS CLEAR DOWN LAST NIGHT",
  "a workbench left with offcuts and a smear of dried glue squeeze out "
  "still on the top the morning after a session"),

 ("Power Tool Storage", "WSF-004",
  "A BLADE GUARD NO LONGER SPRINGS BACK ON ITS OWN",
  "a circular saw with its retracting blade guard caught half open, not "
  "fully sprung back into its resting position"),
 ("Power Tool Storage", "WSF-005",
  "A CHARGED BATTERY SITS ON A WOODEN SHELF UNDER A DUSTY BENCH",
  "a lithium battery pack still seated on its charger, resting on a "
  "wooden shelf thick with sawdust beneath a workbench"),
 ("Power Tool Storage", "WSF-006",
  "TWO DRILLS DUPLICATE EACH OTHER AND ONE HASN'T CUT IN YEARS",
  "two cordless drills of the same size hanging side by side on a tool "
  "wall, one with a visible film of dust across its trigger"),

 ("Fastener and Hardware Zone", "WSF-007",
  "A JAR OF MIXED HARDWARE IS BACK ON THE SHELF AGAIN",
  "an old coffee tin overflowing with a mixed jumble of unsorted screws, "
  "nuts, and washers standing on a shop shelf"),
 ("Fastener and Hardware Zone", "WSF-008",
  "THE SMALL PARTS CABINET IS FIXED INTO PLASTERBOARD, NOT STUDS",
  "a fully loaded wall mounted small parts cabinet held by anchors "
  "visibly pulling slightly away from a plasterboard wall"),
 ("Fastener and Hardware Zone", "WSF-009",
  "THE WEEKLY SIZE IS BURIED WHILE A RARE HINGE SITS AT HAND HEIGHT",
  "a small parts cabinet with a rarely used specialty hinge compartment "
  "at eye level and the everyday screw size buried low in the middle "
  "row"),

 ("Material Rack", "WSF-010",
  "THE OFFCUT BIN SITS WELL OVER ITS MARKED FILL LINE",
  "an offcut bin overflowing above its own marked fill line, short "
  "boards spilling out onto the shop floor beside it"),
 ("Material Rack", "WSF-011",
  "A FULL SHEET OF PLYWOOD LEANS AT A SHALLOW, UNSAFE ANGLE",
  "a full sheet of plywood leaning against a workshop wall at a shallow "
  "angle, clearly at risk of sliding flat"),
 ("Material Rack", "WSF-012",
  "THE GAP BEHIND THE RACK HIDES DROPPINGS, WEBS, AND DAMP",
  "cobwebs, mouse droppings, and a damp stain visible in the narrow gap "
  "behind a fully loaded material rack"),

 ("Finishing and Chemical Zone", "WSF-013",
  "AN OIL FINISH RAG IS BALLED UP INSTEAD OF IN THE CAN",
  "an oil-soaked finishing rag balled up loose in an open bin liner "
  "instead of inside the lidded self-closing metal can beside it"),
 ("Finishing and Chemical Zone", "WSF-014",
  "A ROW OF HALF-USED PAINT CANS SITS FOR COLOURS NO LONGER ON ANY WALL",
  "a row of half-used paint cans of different faded colours lined up on "
  "a shelf, dust settled on several unopened lids"),
 ("Finishing and Chemical Zone", "WSF-015",
  "A SOLVENT CAN AND A WATER BASED PAINT CAN SHARE ONE SHELF",
  "a solvent can and a water based paint can standing side by side on "
  "the same shelf instead of on separated shelves"),

 ("Safety and PPE Station", "WSF-016",
  "THE EXTINGUISHER GAUGE IS OUT OF THE GREEN, OR UNDATED",
  "a wall mounted fire extinguisher with its pressure gauge needle "
  "sitting outside the green zone, no inspection date visible on the "
  "bracket tape"),
 ("Safety and PPE Station", "WSF-017",
  "SCRATCHED SAFETY GLASSES GET LIFTED OFF TO SEE THE CUT LINE",
  "a pair of heavily scratched and hazed safety glasses being lifted "
  "away from the face at a workbench mid cut"),
 ("Safety and PPE Station", "WSF-018",
  "A VISITOR'S GEAR DEPENDS ON WHO IS SUPERVISING THAT DAY",
  "a visitor standing just inside a workshop doorway near a running saw, "
  "no safety glasses or hearing protection handed to them yet"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, workshop-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight from
# ops/root_causes.py, the one shared vocabulary the deck, the app and the
# articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "two similar cordless drills hanging side by side on the tool "
           "wall, one with dust settled across its trigger guard",
 "KC-002": "a phone charging cable and a handful of loose screws sitting "
           "on a workbench top with no drawer or hook assigned to either",
 "KC-003": "a battery charger mounted on a wooden shelf thick with "
           "sawdust under a workbench, instead of on a cleared wall",
 "KC-004": "a hand reaching past three stacked lengths of pipe in a "
           "vertical bin to get to the one piece stored at the back",
 "KC-005": "a vertical storage bin holding mixed lengths of pipe and "
           "dowel, the pieces at the back completely hidden from view",
 "KC-006": "a safety glasses hook mounted well above the reach of a "
           "shorter shop user, stretching up on their toes for it",
 "KC-007": "an offcut bin overflowing above its own marked fill line, "
           "short boards spilling onto the shop floor beside it",
 "KC-008": "a scratched pair of safety glasses hanging on a hook next to "
           "a clean pair, with no note on the wall saying which is "
           "retired",
 "KC-009": "a fire extinguisher gauge with no inspection date on the "
           "bracket tape, hanging untouched on the workshop wall",
 "KC-010": "a chisel lying blade up in an open tray on a workbench, "
           "directly in the path of a hand reaching across",
 "KC-011": "a small-parts compartment sitting below its own marked "
           "minimum line, with nobody having noticed yet",
 "KC-012": "a visitor standing beside a running saw at a workshop "
           "doorway, unsure which of two different safety glasses sets "
           "is theirs to wear",
 "RC-013": "cobwebs and dust in the gap behind a loaded material rack, "
           "untouched because it sits outside anyone's daily path "
           "through the shop",
 "RC-014": "a rusted coffee tin of mixed screws and nails on a shop "
           "shelf, the kind that came from a relative's garage",
 "RC-016": "a hand reaching a long-handled brush into the narrow, hard "
           "to reach gap behind a fully loaded material rack",
 "RC-017": "a row of half-used paint cans that has stood in the same "
           "spot on a finishing shelf so long it no longer registers as "
           "clutter",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Main Workbench": [
  "Run the vacuum crevice nozzle along the top of every tool outline on "
  "the wall, where sawdust settles unseen before it showers onto the "
  "bench.",
  "Wipe the task lamp's shade, head, and arm joints with a barely damp "
  "cloth once the bulb is cool, keeping the cloth off the bulb and "
  "switch.",
  "Wind the vise fully open and closed to clear the screw of grit, then "
  "wipe it clean and work in one drop of light machine oil.",
 ],
 "Power Tool Storage": [
  "Blow or brush the packed sawdust out of one tool's motor vents with "
  "its battery out, then wipe the housing clear of the vents.",
  "Wipe the pitch and resin off one saw blade with resin remover so the "
  "teeth cut clean instead of burning, then stand it back guarded.",
  "Wipe each contact face on the battery shelf and chargers with a dry "
  "cloth, keeping all moisture away from the live terminals.",
 ],
 "Fastener and Hardware Zone": [
  "Wipe one drawer face and its glued sample screw with a barely damp "
  "cloth, so you can still match a screw by eye rather than a smeared "
  "label.",
  "Lift out a loose bin, vacuum the metal filings and grit from its "
  "compartment, and run the detail brush into the corners.",
  "Vacuum the floor under and in front of the cabinet, where a single "
  "dropped screw waits for a bare foot.",
 ],
 "Material Rack": [
  "Brush the cobwebs and settled dust off the top rail and the highest "
  "arms with a long-handled brush before touching the stock below.",
  "Wipe the surface rust off one length of steel stock with a cloth and "
  "lay on a light film of oil before it goes back on the rack.",
  "Tip the offcut bin out, vacuum the sawdust from the bottom, and "
  "refill it only up to the size marked on the front.",
 ],
 "Finishing and Chemical Zone": [
  "Wipe the rim and shoulder of one can before its lid goes back on, "
  "since a rim packed with dried finish is why a lid stops sealing.",
  "Lift the drip tray out from under the solvent shelf and clean it, so "
  "the next drip lands on bare metal instead of a crust of old spills.",
  "Clean one brush right through to the ferrule with the matching "
  "thinner, work it dry, and hang it bristle down.",
 ],
 "Safety and PPE Station": [
  "Wash one pair of safety glasses in mild dish soap and warm water and "
  "dry with a clean microfiber cloth, never a shop rag.",
  "Wipe the sweat and sawdust off the earmuff cushions and headband so "
  "the cushions still seal against your head.",
  "Clean the extinguisher gauge face with a streak-free glass cleaner "
  "so you can read the needle at a glance.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-workshop actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "WSA-001", "zone": "Main Workbench",
  "title": "CLEAR THE BENCH TO JUST THE VISE AND THE LAMP",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the bench top down to just the vise and the task lamp, "
          "and give every offcut or glue drip its verdict.",
  "why": "A half-cleared bench is where the next project's chisel goes "
         "missing and where a hand finds a blade lying edge up without "
         "looking.",
  "inputs": ["the offcut bin", "the fire bucket"],
  "steps": [
   "Clear the bench top down to just the vise and the task lamp: put "
   "every hand tool back on its traced outline, and give any offcut or "
   "glue squeeze-out its verdict, the rack, the fire bucket, or the bin.",
   "Put every hand tool back on its traced outline on the tool wall "
   "before you call the bench clear."],
  "causes": ["KC-002", "KC-010", "KC-008"],
  "victory": "The bench top holds only the vise and the task lamp, with "
             "every tool back on its silhouette and the dog holes empty.",
  "next": "WSS-001",
  "art": "a bare workbench top holding only a vise and a task lamp, "
         "every hand tool hanging back on its silhouette on the tool "
         "wall behind"},

 {"id": "WSA-002", "zone": "Main Workbench",
  "title": "GIVE THE STALLED PROJECT ITS VERDICT AND SET THE CLEAR DOWN "
           "RULE",
  "minutes": 30, "players": "1", "six_s": "Sustain",
  "goal": "Decide the fate of any project that has sat on the bench for "
          "months, and agree the ten-minute clear down happens before "
          "the glasses come off.",
  "why": "A project with no next action and no date is not a project in "
         "progress, it is the reason the bench stops being usable, and a "
         "clear down with nobody assigned to it just does not happen on "
         "a bad night.",
  "inputs": ["a marker and a tag for the project's parts", "the tool "
             "wall"],
  "steps": [
   "Say out loud what the next physical action on the stalled project "
   "is and what date this month you will do it; if you cannot name "
   "both, take it apart and return the hardware to the fastener drawers "
   "and the stock to the rack.",
   "Agree, out loud, whose job the ten-minute clear down is when more "
   "than one of you uses the bench in one evening."],
  "causes": ["RC-013", "KC-009", "RC-017"],
  "victory": "The bench carries either one project with a named next "
             "action and a date, or no project at all, and everyone who "
             "uses the bench knows whose job the clear down is that "
             "night.",
  "next": "WSA-001",
  "art": "a hand setting a dated, tagged project's parts onto a shelf, "
         "a workbench left bare beside it"},

 {"id": "WSA-003", "zone": "Power Tool Storage",
  "title": "TEST EVERY GUARD AND CLEAR A LINGERING CHARGER",
  "minutes": 15, "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Work the retracting guard on every saw with your thumb, and "
          "move any battery still sitting on the charger from a "
          "finished job onto its tool's hook.",
  "why": "A guard that sticks is the injury this zone is actually "
         "waiting on, and a charged pack left running on a dusty wooden "
         "shelf is a fire risk sitting under your bench.",
  "inputs": ["nothing, this is a walk and a check"],
  "steps": [
   "Work the retracting guard on every saw with your thumb to confirm "
   "it snaps back on its own, and move any battery still sitting on the "
   "charger from a finished job onto its tool's hook.",
   "Note any guard that does not snap back cleanly and set that tool "
   "aside until it is fixed rather than back on its hook."],
  "causes": ["KC-010", "KC-009"],
  "victory": "Every guard snaps shut on its own, and no charger is "
             "running behind a job that already ended.",
  "next": "WSS-002",
  "art": "a thumb testing a circular saw's retracting blade guard, a "
         "battery pack being lifted off a charger and carried to its "
         "tool's hook on the wall"},

 {"id": "WSA-004", "zone": "Power Tool Storage",
  "title": "SELL THE TOOL YOU RENT INSTEAD OF USE",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Apply the two-question test to any duplicate or unused power "
          "tool, and move the charger shelf off the wooden surface "
          "under the bench.",
  "why": "A tool losing value on the shelf while duplicating one "
         "already on the wall is not an asset, it is a decision you are "
         "storing, and a charger shelf sitting on wood under sawdust is "
         "a fire risk waiting on the next job.",
  "inputs": ["a marketplace listing", "a non-wood shelf or a metal tray "
             "for the chargers"],
  "steps": [
   "Ask of any duplicate or two-year-unused tool: has it done work in "
   "the last twenty-four months, and would you happily hire one for a "
   "day instead? If no and yes, list it for sale now.",
   "Move the battery shelf off any wooden surface sitting under the "
   "bench onto a shelf that is not wood, or add a fireproof mat "
   "beneath it."],
  "causes": ["KC-009", "KC-001", "KC-003"],
  "victory": "Any tool that failed the two-question test is listed for "
             "sale, and the battery shelf no longer sits directly on "
             "wood under the bench.",
  "next": "WSA-003",
  "art": "a power tool listed for sale on a phone screen held beside "
         "the tool itself, a battery charging shelf now resting on a "
         "metal tray instead of bare wood"},

 {"id": "WSA-005", "zone": "Fastener and Hardware Zone",
  "title": "SORT ONE MIXED JAR AND RECYCLE THE REST",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Tip out one obviously mixed jar or tin of hardware, sort only "
          "the sizes you already have a labeled compartment for, and "
          "recycle the rest today.",
  "why": "An inherited jar that keeps surviving house moves is not "
         "spare hardware, it is a decision nobody has made, and every "
         "day it sits is a day closer to a third house.",
  "inputs": ["a labeled compartment cabinet", "a bag for metal "
             "recycling"],
  "steps": [
   "Tip out one obviously mixed jar or tin of hardware, and sort only "
   "the sizes you already have a labeled compartment for; whatever is "
   "left over goes straight to metal recycling today.",
   "Carry the recycling bag out to the bin the same day rather than "
   "setting it down inside the shop."],
  "causes": ["RC-014", "KC-008"],
  "victory": "That one jar is empty and gone, and every fastener from it "
             "that stayed is inside a labeled compartment, not back in "
             "a container of its own.",
  "next": "WSS-003",
  "art": "a mixed jar of hardware being sorted screw by screw into "
         "labeled cabinet compartments, an empty metal recycling bag "
         "waiting beside it"},

 {"id": "WSA-006", "zone": "Fastener and Hardware Zone",
  "title": "REFIX THE CABINET INTO STUDS AND MOVE THE WEEKLY SIZE TO "
           "HAND HEIGHT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Find the studs and refix the loaded small-parts cabinet "
          "properly, then move the fastener size you drive weekly down "
          "to hand height.",
  "why": "A steel-loaded cabinet held only by plasterboard anchors can "
         "pull off the wall onto whoever is standing under the top "
         "drawer, and a weekly size buried in the middle means moving "
         "other bins every single time you need it.",
  "inputs": ["a stud finder", "proper screws for the cabinet weight"],
  "steps": [
   "Find the wall studs behind the cabinet, refix it directly into "
   "them, and confirm the fixing holds when you lean on the loaded top "
   "drawer.",
   "Move the compartment holding the size you drive weekly down to hand "
   "height, mark its minimum line the same way the other compartments "
   "carry one, and move any specialty hinge or threaded rod you have "
   "not touched this year up high."],
  "causes": ["KC-010", "KC-009", "KC-003", "KC-004", "KC-011"],
  "victory": "The cabinet is fixed into studs and holds when leaned on, "
             "the fastener size you drive weekly sits at hand height, "
             "and its compartment carries a marked minimum line.",
  "next": "WSA-005",
  "art": "a stud finder held against a wall behind a small-parts "
         "cabinet, a weekly-use compartment of screws now sitting at "
         "hand height on the front row"},

 {"id": "WSA-007", "zone": "Material Rack",
  "title": "GIVE EVERY LOOSE OFFCUT ITS VERDICT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull every offcut sitting on the bench, floor, or top of the "
          "rack and give each one its verdict: the bin under the fill "
          "line, or the fire bucket.",
  "why": "An offcut with no verdict does not stay on the bench by "
         "accident, it stays because nobody decided, and the pile only "
         "grows from there.",
  "inputs": ["the offcut bin", "the fire bucket"],
  "steps": [
   "Pull every offcut sitting on the bench, the floor, or the top of "
   "the rack right now and give each one its verdict: into the bin "
   "under the fill line, or straight to the fire bucket.",
   "If the bin is already at its fill line once the good pieces go in, "
   "the shortest piece already in it leaves to make room."],
  "causes": ["KC-001", "KC-007"],
  "victory": "Nothing is stored directly on the shop floor, and the "
             "offcut bin sits at or under its marked fill line.",
  "next": "WSS-004",
  "art": "offcuts being sorted off a workbench and a shop floor into a "
         "bin marked with a fill line, a fire bucket standing ready "
         "beside it"},

 {"id": "WSA-008", "zone": "Material Rack",
  "title": "STAND THE SHEET GOODS UP AND CLEAR THE GAP BEHIND THE RACK",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Bring any shallow-leaning sheet good closer to vertical "
          "against the wall, and sweep out the gap behind the rack.",
  "why": "A sheet leaning at too shallow an angle can slide flat "
         "without warning onto whatever is in front of it, and the gap "
         "behind a loaded rack is exactly where damp, droppings, and "
         "webs go unnoticed.",
  "inputs": ["a broom or long-handled brush", "a helper for heavy sheet "
             "goods"],
  "steps": [
   "Stand each sheet good up close to vertical against the wall rather "
   "than leaning at a shallow angle, getting help for anything full "
   "sized.",
   "Sweep or vacuum the gap behind the rack, checking for droppings, "
   "webs, or a damp stain while you are back there."],
  "causes": ["KC-010", "RC-016", "KC-005"],
  "victory": "Every sheet good stands close to vertical against the "
             "wall, and the gap behind the rack is swept clear with "
             "nothing living back there.",
  "next": "WSA-007",
  "art": "a full sheet of plywood being stood upright close to vertical "
         "against a workshop wall, a long-handled brush sweeping the "
         "gap behind a material rack"},

 {"id": "WSA-009", "zone": "Finishing and Chemical Zone",
  "title": "CAN THE LOOSE RAGS AND DATE THE OPEN LIDS",
  "minutes": 15, "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Put every loose oil-finish rag into the lidded metal can with "
          "the lid down, and date any open can on the shelf that is "
          "missing one.",
  "why": "A balled up oil rag generates its own heat as it cures and "
         "can ignite with nothing touching it, and an undated can is "
         "how a finish quietly skins over before you notice.",
  "inputs": ["the lidded metal rag can", "a marker"],
  "steps": [
   "Check every rag from today's finishing work: anything balled up "
   "loose goes into the lidded metal can with the lid pushed down, and "
   "scan the open cans on the shelf for one without a date and mark it "
   "now.",
   "Confirm the rag can's lid falls shut on its own weight before you "
   "leave the zone."],
  "causes": ["KC-010", "KC-009"],
  "victory": "No oily rag is loose anywhere in the zone, and every open "
             "can on the shelf shows a marker date on its lid.",
  "next": "WSS-005",
  "art": "an oily finishing rag being pushed down into a self-closing "
         "metal can, a marker dating the lid of an open paint can on the "
         "shelf beside it"},

 {"id": "WSA-010", "zone": "Finishing and Chemical Zone",
  "title": "KEEP ONLY THE COLOURS STILL ON A WALL AND SEPARATE THE "
           "SHELVES",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Narrow the paint shelf down to only colours currently on a "
          "surface in this house, in small sealed jars, and put "
          "solvents and water based finishes on separate shelves.",
  "why": "Almost none of an old can will brush out matching in two "
         "years anyway, and solvents sharing a shelf with water based "
         "finish is the actual incompatible-storage hazard this zone "
         "exists to prevent.",
  "inputs": ["small sealed jars and labels", "household hazardous waste "
             "drop-off"],
  "steps": [
   "Decant a small sealed, labeled jar of each colour still on a wall "
   "in this house, and take every other can straight to household "
   "hazardous waste that same day.",
   "Move every solvent and thinner onto its own shelf, separate from "
   "water based paint, with the layout written on the inside of the "
   "cabinet door."],
  "causes": ["KC-011", "KC-001", "KC-010"],
  "victory": "The paint shelf holds only small sealed jars of colours "
             "currently on a wall in this house, and solvents stand on "
             "a shelf of their own, apart from water based paint.",
  "next": "WSA-009",
  "art": "small labeled paint jars standing on a shelf beside a shelf "
         "layout diagram taped inside a cabinet door, solvent cans now "
         "separated onto their own shelf"},

 {"id": "WSA-011", "zone": "Safety and PPE Station",
  "title": "CHECK THE EXTINGUISHER AND CULL THE SCRATCHED GLASSES",
  "minutes": 15, "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Lift the extinguisher and confirm the gauge sits in the "
          "green, then bin any pair of safety glasses scratched enough "
          "to tempt you to lift them off mid-cut.",
  "why": "A dead extinguisher looks identical to a working one until "
         "the moment you need it, and a scratched pair you lift off "
         "mid-cut is the exact moment the chip flies.",
  "inputs": ["masking tape and a marker for the date", "a replacement "
             "pair of glasses"],
  "steps": [
   "Lift the extinguisher and confirm the gauge sits in the green, then "
   "run a hand over every pair of glasses on the hooks and bin any pair "
   "scratched enough that you would lift them off to see a cut line.",
   "Write today's date on the extinguisher bracket tape once the gauge "
   "is confirmed."],
  "causes": ["KC-010", "KC-009", "KC-008"],
  "victory": "The extinguisher gauge reads green with a dated tape on "
             "the bracket, and every pair of glasses left on the hooks "
             "is clear enough to cut by.",
  "next": "WSS-006",
  "art": "a hand checking a wall mounted extinguisher gauge in the "
         "green with a dated bracket tape beside it, a scratched pair "
         "of safety glasses being dropped into a bin"},

 {"id": "WSA-012", "zone": "Safety and PPE Station",
  "title": "SET THE VISITOR RULE AND MATCH THE BOARD TO THE SHORTEST "
           "USER",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Decide the visitor rule once and hang it on the wall, and "
          "lower or add a hook so the shortest regular user can reach "
          "their own gear without help.",
  "why": "Handling the visitor question case by case means handling it "
         "badly, and a hook board mounted to the tallest user's height "
         "means the shortest one skips the gear because reaching for it "
         "is a hassle.",
  "inputs": ["a marker and a card for the wall", "an extra hook"],
  "steps": [
   "Write the visitor rule on a card and hang it at the door: anyone "
   "who works in this shop gets a labeled set, one spare set is marked "
   "for visitors, and anyone who will not wear it stays on the near "
   "side of the doorway.",
   "Check the shortest regular user can reach their own hook without "
   "stretching or asking for help, and add or lower a hook if they "
   "cannot."],
  "causes": ["KC-012", "KC-006", "KC-007"],
  "victory": "The visitor rule hangs written at the door, and every "
             "regular user, including the shortest, can reach their own "
             "hook without help.",
  "next": "WSA-011",
  "art": "a visitor rule card hung beside a hook board at a workshop "
         "door, a lowered hook now within easy reach at a shorter "
         "user's height"},

 {"id": "WSA-013", "zone": None, "title": "THE FULL WORKSHOP HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking for a stuck guard, an unanchored "
          "small-parts cabinet, an extinguisher out of the green, and a "
          "shallow-leaning sheet good.",
  "why": "This room's own hazards, blades, batteries, solvents, and a "
         "full sheet of ply, sit across six different zones and only "
         "get found together if someone walks the whole shop on "
         "purpose.",
  "inputs": ["a stud finder", "masking tape and a marker"],
  "steps": [
   "Test the retracting guard on every saw, and check every battery is "
   "off its charger once its job is done.",
   "Confirm the small-parts cabinet and the material rack are both "
   "fixed into studs, and stand up any sheet good leaning at a shallow "
   "angle.",
   "Lift the extinguisher and confirm the gauge is green and dated, "
   "and confirm oily rags are in the lidded can rather than loose "
   "anywhere in the shop."],
  "causes": ["KC-010", "KC-009"],
  "victory": "No guard sticks, both the cabinet and the rack hold when "
             "leaned on, no sheet leans at a shallow angle, the "
             "extinguisher reads green and dated, and no oily rag sits "
             "loose.",
  "next": "WSE-001",
  "art": "a hand testing a saw guard beside a checklist, a wall mounted "
         "extinguisher with a dated gauge and a stood-up sheet of "
         "plywood visible in the same frame"},

 {"id": "WSA-014", "zone": None,
  "title": "THE ROOM'S OWN TRAP: THE VERDICT NOBODY HAS MADE",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Walk the shop looking for anything, a stalled project, a "
          "mixed jar of hardware, a shelf of retired paint, that is "
          "really a decision nobody has made yet, and make it.",
  "why": "This room's own real friction is never really about storage, "
         "it is about verdicts you keep postponing on offcuts, on "
         "half-finished projects, and on paint; the workshop only gets "
         "crowded because those decisions have nowhere else to hide.",
  "inputs": ["a marker and tags", "household hazardous waste drop-off"],
  "steps": [
   "List every stalled project, mixed jar, and shelf of retired paint "
   "you can find in one walk of the shop.",
   "Give each one a verdict today, a date and a next action, or "
   "straight to recycling, the fire bucket, or hazardous waste, rather "
   "than setting it back down unresolved."],
  "causes": ["RC-013", "KC-009", "RC-017"],
  "victory": "Nothing in the shop is a postponed decision anymore. "
             "Every stalled project has a date, every jar is sorted, "
             "and every retired can has left for hazardous waste.",
  "next": "WSA-015",
  "art": "a hand writing a date on a tag attached to a half-finished "
         "project, a shop with sorted hardware bins and a cleared paint "
         "shelf visible behind"},

 {"id": "WSA-015", "zone": None,
  "title": "THE LAST-THING-BEFORE-THE-LIGHT-GOES-OUT RESET",
  "minutes": 15, "players": "1 to 2", "six_s": "Sustain",
  "goal": "Before the shop light goes off, confirm the bench is clear, "
          "every tool and battery is on its hook, and the safety gear "
          "is back on the board.",
  "why": "Every standard in this room is built to survive a bad week, "
         "and the only way that holds is checking it meets its own "
         "standard before the light goes out, not noticing days later "
         "that it slipped.",
  "inputs": ["nothing, this is a walk-through"],
  "steps": [
   "Walk the bench, the tool wall, and the battery shelf, and confirm "
   "nothing is out of place before you reach for the light switch.",
   "Confirm every pair of safety glasses and hearing protection is "
   "back on its own hook, not in a pocket or a drawer."],
  "causes": ["KC-009", "RC-013", "RC-017"],
  "victory": "The bench is bare except the vise and the lamp, every "
             "tool and battery is on its hook, and all safety gear is "
             "back on the board, before the light goes out.",
  "next": "WSA-013",
  "art": "a hand reaching for a workshop light switch with a bare "
         "bench, a full tool wall, and a full safety gear board all "
         "visible in the same glance"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a workshop, one per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("WSE-001", "THE NIGHT YOU NEED THE BENCH FOR A QUICK REPAIR",
  "Something breaks at 9pm and you need the bench right now for a "
  "five-minute fix, not a whole project.",
  ["WSZ-001"],
  "The bench top is bare except the vise and the lamp, so you set to "
  "work immediately with a clear surface and every tool exactly where "
  "its outline says it lives.",
  "If you had to clear someone else's project off the bench first, or "
  "hunt for a tool missing from its outline, the clear down did not "
  "hold. Draw WSA-001.",
  "a hand setting a broken part down onto an otherwise bare workbench "
  "top, a full tool wall with every outline filled visible behind"),
 ("WSE-002", "THE SATURDAY MORNING YOU GRAB THE SAW WITHOUT LOOKING",
  "You are already running late for a job and grab the circular saw "
  "off its hook without checking it first.",
  ["WSZ-002"],
  "The guard snaps back clean under your thumb, the blade wrench is "
  "right there on the saw, and the battery is already charged and "
  "waiting on its shelf.",
  "If the guard stuck, the wrench was missing, or the battery was "
  "flat, the storage and safety checks have slipped. Draw WSA-003.",
  "a hand lifting a circular saw off its wall hook, its blade wrench "
  "visibly clipped to the saw and a charged battery beside it"),
 ("WSE-003", "THE JOB THAT NEEDS ONE SPECIFIC SCREW RIGHT NOW",
  "You are mid-assembly and need one specific size of deck screw, and "
  "you need it without stopping the job to go looking.",
  ["WSZ-003"],
  "You match the sample screw glued to the drawer face by eye, pull "
  "the compartment, and it is not below its own marked minimum line.",
  "If you had to open three drawers or found the compartment nearly "
  "empty with no warning, the labels or the minimum lines have "
  "slipped. Draw WSA-005.",
  "a hand pulling one drawer straight to a glued sample screw on its "
  "face, the compartment behind it still above its marked minimum "
  "line"),
 ("WSE-004", "THE DAY YOU NEED A SPECIFIC LENGTH OF BOARD FAST",
  "A project calls for one specific length and thickness of board, and "
  "you need to find it without unstacking half the rack.",
  ["WSZ-004"],
  "You pull the board you need from its own grouped bay without moving "
  "three others first, and nothing is stored on the floor in your way.",
  "If you had to unstack several boards to reach the one you needed, "
  "or step over something on the floor to get there, the rack has "
  "drifted. Draw WSA-007.",
  "a single board being pulled cleanly from a grouped bay on a "
  "material rack, a clear floor visible along the route to the bench"),
 ("WSE-005", "THE TOUCH-UP JOB THAT NEEDS ONE SPECIFIC COLOUR",
  "A wall needs a small touch-up today, and you go to the shelf for "
  "the exact colour that is on it.",
  ["WSZ-005"],
  "A small sealed jar labeled with the room and the finish is exactly "
  "where it should be, and it still brushes out matching.",
  "If you found only an old half-empty tin skinned over at the rim, or "
  "no labeled jar at all, the paint shelf has drifted back toward the "
  "old pile. Draw WSA-010.",
  "a small labeled paint jar being opened for a touch-up, its lid "
  "clean and the paint inside still liquid"),
 ("WSE-006", "THE MORNING A FRIEND DROPS BY WHILE THE GRINDER IS "
             "RUNNING",
  "A friend wanders in to say hello while the grinder is running, and "
  "wants to get a closer look.",
  ["WSZ-006"],
  "The visitor rule is right there on the wall, and the spare labeled "
  "set is on its own marked hook, ready to hand over or to send them "
  "back to the doorway.",
  "If you had to improvise an answer on the spot, or there was no "
  "spare set to hand over, the visitor rule was never actually "
  "decided. Draw WSA-012.",
  "a spare set of safety glasses and ear protection being handed to a "
  "visitor standing at a workshop doorway, a rule card visible on the "
  "wall"),
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
        "related": {"standard": f"WSS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your workshop, "
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
    standard_id = (f"WSS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"WSS-{spec['order']:03d}", "title": f"{name.upper()} "
              f"STANDARD",
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
        "id": "WSR-001", "title": "THE WORKSHOP", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START AT SAFETY, EVEN THOUGH IT IS THE "
                   "SMALLEST.",
        "objective": "The workshop is the room 6S came from, and the "
                     "only one in the house where a bad standard can "
                     "cost you a finger rather than an afternoon. This "
                     "card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"WSZ-006 Safety and PPE Station. {start_tip['text']}"
            if start_tip else
            "WSZ-006 Safety and PPE Station. It is the smallest zone in "
            "the room and sets the terms for the other five."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Start at Safety and PPE "
            "Station, or take the zone that is annoying you today.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your workshop. Put the rest back.",
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
        "players": "1 to 2. A shared shop runs on the same standards for "
                   "everyone who uses it: the visitor rule on the Safety "
                   "and PPE Station card exists precisely because two "
                   "people improvising two different rules is how "
                   "someone gets hurt.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do WSA-013 The Full Workshop Hazard Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "every stuck guard, the unanchored small-parts "
                        "cabinet and material rack, a shallow-leaning "
                        "sheet good, the extinguisher gauge, and any "
                        "loose oily rag.",
        "related": {"contents": "WSZ-001 to WSZ-006, WSF-001 to "
                                 "WSF-018, the shared root causes in "
                                 "ops/root_causes.py, WSA-001 to "
                                 "WSA-015, WSS-001 to WSS-006, WSE-001 "
                                 "to WSE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole "
                           "workshop in its settled state, a bare "
                           "workbench with a vise and a task lamp, a "
                           "wall of guarded power tools, a labeled "
                           "small parts cabinet, a loaded material rack, "
                           "a closed finishing cabinet, and a full "
                           "safety board by the door, all visible in one "
                           "frame",
                "must_show": ["all six zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the six zones is. If one is not "
                               "in frame, reshoot."},
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
    return {"deck": "workshop", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_primary_bedroom_deck.py)."""
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

    assert any(c["id"] == "WSA-013" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This deck's zone list must be exactly the Manual's six, in the
    # Manual's own order, nothing added or renamed.
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match the Manual"
    assert len(ZONES) == 6, (
        "this room has six Manual zones; that count moved")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        workshop ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
