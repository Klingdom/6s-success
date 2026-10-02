#!/usr/bin/env python3
"""
Build the Patio or Deck deck: 68 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: eighteen rooms already carry a full diagnosis
layer and a shipped deck (Entryway, Kitchen, Pantry, Dining Room, Primary
Bathroom, Laundry Room, Home Office, Garage, Hall Closet, Stair Landing,
Guest Bedroom, Guest Bathroom, Family Room, Living Room, Mudroom, Nursery,
Kids Bedroom, Primary Bedroom, by the time this file was written). Patio
or Deck is the last of the Manual's 20 rooms still missing a diagnosis
layer and a deck (Workshop is the other, built independently and
concurrently, not depended on here), built the same way: rich,
hand-authored Manual content for all six zones
(purpose, done_looks_like, passes, the_call, watch_for, leave_behind,
shine_detail), and a diagnosis layer already authored into
content/manual/source/content.json (eighteen frictions, fifty-four
branches, six first_15 actions) by a separate pass this file does not
redo. This file only reads that layer and builds the deck straight off
it, the same shape ops/cardtext/build_primary_bedroom_deck.py already
uses for its own room.

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
real frictions, counted honestly from the branches actually written below,
not chosen first and filled in: KC-001, KC-002, KC-003, KC-004, KC-005,
KC-007, KC-008, KC-009, KC-010, KC-011, KC-012, RC-013, RC-014, RC-015,
RC-016, RC-017. One is not reachable, and that is a true statement about
this room's own frictions, not an oversight:

KC-006 (poor accessibility) is not reachable because nothing in the real
diagnosis branches is about a person who cannot physically reach
something stored correctly; every hazard in this room's own frictions is
about a thing placed somewhere unsafe (a rail post that gives, an
unlabeled chemical, a grease tray left too long) or a thing with no
agreed home, never a person unable to reach something that is already
stored the right way.

WHAT THE BUDGET IS AND WHY
---------------------------
Patio or Deck ships as a free typeset page, the same stage every prior
room in this line shipped at before any print-on-demand decision existed.
The budget below is six real zones, eighteen frictions (three per zone),
sixteen reachable root causes, fifteen action cards (two per zone plus
three whole-room), six standard cards and six event cards. 68 cards in
total, not padded or trimmed to match any other room's count: sixteen
causes is the room's own real number, arrived at from this room's own
real frictions, not copied from another room's.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_patio_or_deck_deck.py
Out:  ops/cardtext/patio-or-deck-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "patio-or-deck-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Patio or Deck"

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
# content/manual/source/content.json before this file was written.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-007",
             "KC-008", "KC-009", "KC-010", "KC-011", "KC-012", "RC-013",
             "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Outdoor Seating Zone": {
  "id": "PDZ-001", "order": 1, "difficulty": 2,
  "tagline": "FOUR CHAIRS YOU TRUST. EVERY CUSHION IN THE BOX BY NIGHTFALL.",
  "callouts": [
   "Four outdoor chairs set close enough to talk across without raising "
   "your voice",
   "Every seat cushion sitting inside the closed deck box rather than on "
   "a chair",
   "A furniture cover folded flat rather than crumpled on the ground "
   "behind a planter",
   "A bare walking route from the back door to the steps with nothing "
   "parked in it",
   "A deck box lid closing flat under its own weight",
   "A chair frame standing on its side, drying after a hose-down",
  ],
  "art": ("a patio seating area with four chairs set close enough to "
          "talk across, a closed deck box beside them, a furniture cover "
          "folded flat rather than crumpled behind a nearby planter, a "
          "bare walking route from the back door to the steps, and one "
          "chair frame standing on its side drying after being hosed "
          "down"),
 },
 "Grill and Outdoor Cooking Zone": {
  "id": "PDZ-002", "order": 2, "difficulty": 3,
  "tagline": "FOUR TOOLS ON THE HOOKS. THE TANK LEVEL MARKED ON THE "
             "COLLAR.",
  "callouts": [
   "Grates scraped bare of built-up residue",
   "An empty grease tray sitting back in its rails",
   "Exactly four tools hanging on the grill's own hooks, nothing extra",
   "A propane tank standing upright with its fuel level marked on the "
   "collar",
   "A clear arm's length of open air between the grill body and the "
   "siding",
   "No fifth tool anywhere near the hooks",
  ],
  "art": ("a backyard grill with bare scraped grates, an empty grease "
          "tray back in its rails, exactly four tools, tongs, a spatula, "
          "a thermometer and a basting brush, hanging from the grill's "
          "own hooks, a propane tank standing upright with its fuel "
          "level marked in grease pencil on its collar, and a clear "
          "arm's length of open space between the grill body and the "
          "house siding"),
 },
 "Outdoor Dining Zone": {
  "id": "PDZ-003", "order": 3, "difficulty": 2,
  "tagline": "BARE TABLE. ONE TRAY. THE UMBRELLA CRANKED DOWN EVERY "
             "NIGHT.",
  "callouts": [
   "A bare tabletop holding only the umbrella and one weighted tray",
   "Six chairs tucked fully under the table",
   "String lights clipped along the rail",
   "No cord crossing the deck floor",
   "A closed umbrella, cranked down",
   "Nothing stored in the open space beneath the table",
  ],
  "art": ("an outdoor dining table with a bare top holding only a "
          "closed, cranked-down umbrella and one weighted tray, six "
          "chairs tucked fully under, string lights clipped along a "
          "rail overhead with no cord crossing the deck floor, and "
          "nothing stored in the open space beneath the table"),
 },
 "Garden and Plant Care Zone": {
  "id": "PDZ-004", "order": 4, "difficulty": 2,
  "tagline": "EMPTY SAUCERS. THE CHEMICALS LATCHED UP HIGH.",
  "callouts": [
   "Every plant saucer sitting empty",
   "Pots nested by size along the wall",
   "Clear, unobstructed drain holes on the visible pots",
   "One tool caddy holding a trowel, pruners, and gloves",
   "A latched chemical box mounted above the tools",
   "A short row of labeled containers inside the latched box",
  ],
  "art": ("a patio garden corner with every plant saucer empty, pots "
          "nested by size along the wall with their drain holes visible "
          "and clear, one tool caddy holding a trowel, pruners and "
          "gloves, and a latched chemical box mounted above the tools "
          "holding only a short row of labeled containers"),
 },
 "Outdoor Storage Zone": {
  "id": "PDZ-005", "order": 5, "difficulty": 3,
  "tagline": "ONE LAYER OF CUSHIONS. THE LID CLOSES FLAT AND LATCHES.",
  "callouts": [
   "A deck box lid closing flat without anyone pressing down",
   "Cushions sitting in one layer on top",
   "Two labeled totes visible beneath the cushions",
   "The bare floor of the box showing once the cushions lift out",
   "A lid stay holding the open lid safely up",
   "A latch fastened across the closed lid",
  ],
  "art": ("an open deck box showing cushions sitting in a single layer "
          "on top, two totes labeled games and covers beneath them, "
          "the bare floor of the box visible underneath, a lid stay "
          "holding the open lid safely in place, and a latch ready to "
          "fasten across the lid once it closes flat"),
 },
 "Surface, Rail, and Safety Zone": {
  "id": "PDZ-006", "order": 6, "difficulty": 4,
  "tagline": "PUSH THE RAIL HARD. IF IT MOVES, NOBODY STANDS ON IT "
             "TONIGHT.",
  "callouts": [
   "Nothing on the deck surface that is not furniture",
   "Daylight visible through clear gaps between the boards",
   "No green film on the shaded stair treads",
   "A rail post standing immovable under a hard push",
   "A dated tag hanging just inside the back door",
   "Stair treads that rise the same height as the ones above and below",
  ],
  "art": ("a bare deck surface holding nothing but furniture, daylight "
          "visible through clear gaps between the boards, algae-free "
          "shaded stair treads, a hand pushing hard on a rail post that "
          "does not move, a dated tag hanging just inside the back "
          "door, and evenly rising stair treads"),
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
 "Outdoor Seating Zone": {
  "frictions": [
   {
    "symptom": "A resin or plastic chair with a wobble, a cracked arm, or a seat pan that flexes when you press it hard is still standing in the evening seating circle instead of at the curb.",
    "branches": [
     {"answer": "A chair failing under someone is a real fall risk, and that outranks how many of the other chairs still look fine standing there", "cause": "KC-010"},
     {"answer": "There is no agreed point where a chair officially fails the standard, so it stays in rotation until it actually gives out under someone", "cause": "KC-008"},
     {"answer": "It has creaked in that same spot for months, long enough that the sound stopped registering as a warning", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "A cushion is stacked on a seat under a towel that never actually dries out underneath it, or a furniture cover lies crumpled on the ground behind a planter instead of over the chairs.",
    "branches": [
     {"answer": "Carrying the cushions in only happens if someone remembers on the last trip with the glasses, and some nights nobody does", "cause": "KC-009"},
     {"answer": "The deck box already looks full of what else has migrated into it, so a returning cushion gets left on the chair instead of forced in", "cause": "KC-007"},
     {"answer": "Whoever is still outside when the weather turns assumes somebody else will grab the cushions before it rains", "cause": "RC-013"}
    ]
   },
   {
    "symptom": "A folded lounger or a stacked chair has ended up parked across the route from the door to the steps instead of against the rail.",
    "branches": [
     {"answer": "There is nowhere specific that a folded lounger is supposed to live when it is not in use, so it leans wherever there is a gap", "cause": "KC-002"},
     {"answer": "Its real spot is against the rail at the far end, but it is easier to fold it and lean it right where you are already standing", "cause": "KC-003"},
     {"answer": "Nobody has actually walked that route at night carrying something heavy, so it has never been obvious that it became the shortcut for temporary parking", "cause": "RC-017"}
    ]
   }
  ],
  "first_15": {
   "action": "Sit in every chair and press the seat pan hard with your palm, pull any chair that wobbles, cracks, or flexes out of the circle, and carry every cushion sitting anywhere except a chair into the deck box.",
   "victory": "Every remaining chair passes a hard press with no flex or crack, and every cushion is in the deck box."
  }
 },
 "Grill and Outdoor Cooking Zone": {
  "frictions": [
   {
    "symptom": "The shelf and the cabinet under the grill hold three sets of tongs, a thermometer with a dead battery, and a sauce bottle that has ridden through a whole summer of outdoor heat, while only one of each tool ever actually gets picked up mid-cook.",
    "branches": [
     {"answer": "A cook needs at least one of everything, and buying a backup without checking whether the first one still works is how the second and third arrived", "cause": "KC-001"},
     {"answer": "Nothing has ever forced a look at what is actually behind that closed cabinet door, so it just accumulates unseen", "cause": "KC-005"},
     {"answer": "Whoever is cooking grabs the tool that is already sitting out from last time and never has a reason to sort through the rest", "cause": "KC-009"}
    ]
   },
   {
    "symptom": "There are two or three propane tanks against the wall and nobody is sure which ones actually have gas left, so a fresh one gets bought before the tanks get checked.",
    "branches": [
     {"answer": "The collar has no level marked on it and nobody has weighed one on the bathroom scale, so guessing feels faster than checking", "cause": "KC-008"},
     {"answer": "An empty tank still looks and feels heavy enough to seem fine, so it runs out mid-cook instead of getting caught ahead of time", "cause": "KC-011"},
     {"answer": "Checking the real level means finding the scale, doing the subtraction, and marking the collar; buying a new one skips all of that", "cause": "KC-004"}
    ]
   },
   {
    "symptom": "The flame runs yellow and lazy along one side of the burner, and the grease tray under the grill has not been scraped out in longer than anyone can say.",
    "branches": [
     {"answer": "A grease tray that is overdue is exactly what turns a normal flare-up into a real fire, especially with the grill sitting close to the siding or the rail", "cause": "KC-010"},
     {"answer": "Nobody wants to reach up into the burner tubes or pull the flavorizer bars while they are still greasy, so that part gets skipped every time", "cause": "RC-016"},
     {"answer": "There is no tracked count of cooks between empties, so it only gets done whenever someone happens to notice the smell", "cause": "KC-009"}
    ]
   }
  ],
  "first_15": {
   "action": "Empty the side shelf and the cabinet completely, wipe the grease tray out, and hang the one tong, one spatula, one thermometer, and one basting brush you are keeping back on the grill's own hooks.",
   "victory": "The grill's own hooks hold exactly one tong, one spatula, one thermometer, and one basting brush, and the grease tray sits empty in its rails."
  }
 },
 "Outdoor Dining Zone": {
  "frictions": [
   {
    "symptom": "The table always has something standing on it besides the umbrella and the weighted tray: a citronella bucket burned down to the rim, a lighter that no longer sparks, or four faded plates and a mismatched tumbler from a set that never got completed.",
    "branches": [
     {"answer": "Buying the rest of a matching outdoor set felt like an unnecessary expense for a table you only eat at a handful of times a year", "cause": "RC-015"},
     {"answer": "Nobody has settled whether this table gets its own dishware or borrows from the kitchen, so a half-answer just sits here instead", "cause": "KC-008"},
     {"answer": "The table's job is to hold a meal, but every season adds one more not-quite-empty item that never actually leaves it", "cause": "KC-001"}
    ]
   },
   {
    "symptom": "The umbrella stays cranked up overnight, or a household extension lead runs out to the string lights across boards that stay wet with dew.",
    "branches": [
     {"answer": "An open umbrella catching wind, or a lead lying in a puddle, is a real hazard, and that outranks the extra step of cranking it down or running proper outdoor-rated cord", "cause": "KC-010"},
     {"answer": "Whoever strung the lights years ago used whatever cord was in the garage, and nobody has swapped it for outdoor-rated cord since", "cause": "RC-017"},
     {"answer": "Cranking the umbrella down is one more thing to remember on the way in, and it is easy to skip when your hands are already full of dishes", "cause": "KC-004"}
    ]
   },
   {
    "symptom": "A chair is pushed back at an angle instead of tucked fully under the table, or the umbrella and tray are still standing out well after the last plate went inside.",
    "branches": [
     {"answer": "Clearing the table is the very last thing before the evening actually ends, and skipping it feels like nothing because the mess is invisible from indoors", "cause": "RC-017"},
     {"answer": "There is no single person whose job it is to do the closing pass, so on a night with guests everyone assumes somebody else already did it", "cause": "RC-013"},
     {"answer": "There is nothing that reminds you the umbrella still needs cranking down until it is already dark and the evening has moved on", "cause": "KC-009"}
    ]
   }
  ],
  "first_15": {
   "action": "Clear the table down to bare surface, crank the umbrella down, and tuck every chair fully under.",
   "victory": "The table holds only the umbrella and the one weighted tray, the umbrella is cranked down, and every chair is tucked fully under."
  }
 },
 "Garden and Plant Care Zone": {
  "frictions": [
   {
    "symptom": "A saucer under a pot is holding standing water days after the last rain, or the upturned wheelbarrow has a puddle sitting in its well.",
    "branches": [
     {"answer": "Checking every saucer only takes ten seconds, but nothing about filling the watering can actually forces you to look down at them first", "cause": "KC-009"},
     {"answer": "A saucer that has been full for two days looks the same as one that just got filled, so the row never seems urgent enough to check", "cause": "RC-017"},
     {"answer": "Standing water breeding mosquitoes near a patio people actually sit on is a real health hazard, not just an eyesore to get to eventually", "cause": "KC-010"}
    ]
   },
   {
    "symptom": "There is a shelf of part-used weed killer, rooting hormone, and bug spray whose label has worn away, avoided rather than sorted for more than one season.",
    "branches": [
     {"answer": "An unlabeled garden chemical cannot be used safely by anyone who finds it later, which outranks just leaving it where it is", "cause": "KC-010"},
     {"answer": "There is no easy way to get rid of them, so avoiding the shelf entirely has been the actual plan for a while now", "cause": "RC-015"},
     {"answer": "The value-size container seemed smart when it was bought, and using it up before it goes stale never quite happened", "cause": "KC-001"}
    ]
   },
   {
    "symptom": "A long-handled tool leans blade down against the rail instead of hanging head up, or a pot with no drainage hole and last year's dead root ball is still nested in with the ones you will actually use.",
    "branches": [
     {"answer": "The plant in that pot came from a cutting off a family member's garden, and repotting it properly into something with a drain hole keeps getting put off", "cause": "RC-014"},
     {"answer": "Pots with no drainage hole or a dead root ball do not look any different from the ones you will use again once they are all nested together in a row", "cause": "RC-017"},
     {"answer": "Nested inside a stack, you cannot tell which ones even have a working drain hole until you are already planting into them", "cause": "KC-005"}
    ]
   }
  ],
  "first_15": {
   "action": "Walk the row of saucers, the wheelbarrow well, and any upturned pot lid tipping out standing water, then pull any pot with no drainage hole or last year's dead root ball out of the nested stack.",
   "victory": "No saucer, wheelbarrow well, or pot lid on the patio holds standing water, and every pot in the nested stack has a clear drain hole and nothing dead in it."
  }
 },
 "Outdoor Storage Zone": {
  "frictions": [
   {
    "symptom": "The deck box holds a croquet set missing two mallets, four covers for furniture you no longer own, and a bag of charcoal that drew moisture months ago and will never light properly again.",
    "branches": [
     {"answer": "None of it has anywhere else assigned to go, so it just keeps living in the one lidded space outside", "cause": "KC-002"},
     {"answer": "Getting rid of a game missing pieces feels like giving up on it turning up complete somehow", "cause": "RC-015"},
     {"answer": "Once it is under the cushions, nobody sees it again until the box gets fully emptied, so it never comes up for a decision", "cause": "KC-005"}
    ]
   },
   {
    "symptom": "The lid does not stay up on its own when you let go halfway, or a cushion pulled out from under the pile still smells faintly of mildew after a wash.",
    "branches": [
     {"answer": "A heavy lid dropping at exactly a child's hand height is a real crush risk, and that is worth a lid stay before anything else in this box gets sorted", "cause": "KC-010"},
     {"answer": "A cushion that went in damp last autumn had all winter for that smell to work into the foam, and no amount of washing this week reaches that", "cause": "RC-016"},
     {"answer": "Cushions only go in damp because they come in at the very end of a long evening, when checking each one properly is the last thing anyone wants to do", "cause": "KC-009"}
    ]
   },
   {
    "symptom": "Closing the lid takes leaning your weight on it, and the two totes underneath are buried instead of sitting in their own labeled place.",
    "branches": [
     {"answer": "There is no line drawn for what this box is actually for, so anything without another home defaults to going in here too", "cause": "KC-008"},
     {"answer": "Different people packing the box at each end of the season each have their own idea of what goes on top, so it never settles into the same layout twice", "cause": "KC-012"},
     {"answer": "The lid standing half open in the rain does not look urgent in the moment you are closing it, just heavier than usual", "cause": "RC-017"}
    ]
   }
  ],
  "first_15": {
   "action": "Empty the deck box completely onto the boards, and pull out anything that is mildewed past saving, missing half its pieces, or belongs to furniture you no longer own.",
   "victory": "The deck box floor is visible with only cushions and the two labeled totes waiting to go back in, and nothing else."
  }
 },
 "Surface, Rail, and Safety Zone": {
  "frictions": [
   {
    "symptom": "A planter has drifted into the path between the door and the steps, a hose is coiled across the top step, or a bag of paving sand leans against a rail post.",
    "branches": [
     {"answer": "None of it looks like it is blocking anything until you are actually carrying something with both arms and cannot see your feet", "cause": "RC-017"},
     {"answer": "The hose and the sand bag do not have anywhere else assigned to live, so the top step is just where they landed after the last job", "cause": "KC-002"},
     {"answer": "Whatever is leaning against the deck also holds damp against the wood underneath it, and that rot risk outranks the convenience of leaving it there", "cause": "KC-010"}
    ]
   },
   {
    "symptom": "Nobody has pushed the top rail hard at every post recently, and a board you step over daily flexes slightly or feels soft underfoot without anyone testing it with a screwdriver.",
    "branches": [
     {"answer": "A rail that gives under a stumble, or a board that is finished underneath, is a real fall-through risk, and that is worth the ten seconds it takes to check", "cause": "KC-010"},
     {"answer": "The check has no trigger attached to it, so it only happens if someone happens to think of it separately from any other job", "cause": "KC-009"},
     {"answer": "Nobody in the house has actually been assigned as the one who does the seasonal push-and-probe, so it depends on whether anyone remembers", "cause": "RC-013"}
    ]
   },
   {
    "symptom": "Green algae film has built up on the shaded boards and the stair treads, or the gaps between boards are packed with debris instead of clear.",
    "branches": [
     {"answer": "Getting into every gap with a putty knife and scrubbing the shaded boards is real work compared to the rest of a sweep, so it is the part that gets skipped", "cause": "RC-016"},
     {"answer": "The film only shows up as a slightly duller color in a corner that is already shaded, so it does not read as the slip hazard it actually is until it rains", "cause": "RC-017"},
     {"answer": "A blocked gap holding water against a board end is invisible unless you are down at board level looking for it, not just walking across the top", "cause": "KC-005"}
    ]
   }
  ],
  "first_15": {
   "action": "Walk the full route from the door to the steps to the gate carrying a full laundry basket in both arms, and pull off the route anything you have to step around.",
   "victory": "The full route from the door to the steps to the gate is clear enough to walk carrying a full laundry basket without stepping around anything."
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
 ("Outdoor Seating Zone", "PDF-001",
  "A CHAIR WITH A WOBBLE, A CRACKED ARM, OR A FLEXING SEAT IS STILL IN "
  "THE CIRCLE",
  "a resin patio chair with a visible hairline crack near a leg joint "
  "sitting among three other chairs arranged for conversation"),
 ("Outdoor Seating Zone", "PDF-002",
  "A CUSHION SITS UNDER A DAMP TOWEL, OR A COVER LIES CRUMPLED BEHIND A "
  "PLANTER",
  "a patio cushion stacked on a chair seat with a damp towel draped over "
  "it, and a furniture cover crumpled on the ground behind a large "
  "planter nearby"),
 ("Outdoor Seating Zone", "PDF-003",
  "A FOLDED LOUNGER OR STACKED CHAIR SITS ACROSS THE ROUTE FROM DOOR TO "
  "STEPS",
  "a folded lounge chair leaning across a narrow patio walkway between a "
  "back door and a short flight of steps"),

 ("Grill and Outdoor Cooking Zone", "PDF-004",
  "THE GRILL'S SHELF AND CABINET HOLD THREE SETS OF TONGS AND A DEAD "
  "THERMOMETER",
  "an open grill-side cabinet crowded with three sets of grilling tongs, "
  "a food thermometer with a cracked display, and a faded sauce bottle"),
 ("Grill and Outdoor Cooking Zone", "PDF-005",
  "TWO OR THREE PROPANE TANKS STAND AGAINST THE WALL WITH NO LEVEL "
  "MARKED ON ANY OF THEM",
  "three propane tanks of similar size lined up against a patio wall, "
  "their collars bare with no fuel level noted on any of them"),
 ("Grill and Outdoor Cooking Zone", "PDF-006",
  "THE FLAME RUNS YELLOW ALONG ONE SIDE AND THE GREASE TRAY IS OVERDUE",
  "a lit grill burner showing a yellow, lazy flame along one side, with "
  "a grease tray visibly crusted and overflowing beneath the grates"),

 ("Outdoor Dining Zone", "PDF-007",
  "A BURNED-DOWN CITRONELLA BUCKET AND FOUR FADED PLATES SIT ON THE "
  "TABLE",
  "an outdoor dining table holding a citronella candle bucket burned "
  "down to its rim, a broken lighter, and four sun-faded plastic plates "
  "in mismatched colors"),
 ("Outdoor Dining Zone", "PDF-008",
  "THE UMBRELLA STAYS UP OVERNIGHT AND AN INDOOR CORD RUNS TO THE "
  "STRING LIGHTS",
  "an open patio umbrella standing overnight above an empty table, a "
  "household extension cord running from an indoor outlet across wet "
  "deck boards to string lights along the rail"),
 ("Outdoor Dining Zone", "PDF-009",
  "A CHAIR SITS PUSHED BACK AT AN ANGLE WHILE THE UMBRELLA AND TRAY ARE "
  "STILL OUT",
  "an outdoor dining table late in the evening with one chair pushed "
  "back at an angle, the umbrella still open and the condiment tray "
  "still sitting out after the meal has ended"),

 ("Garden and Plant Care Zone", "PDF-010",
  "A PLANT SAUCER HOLDS STANDING WATER DAYS AFTER THE LAST RAIN",
  "a terracotta plant saucer holding a shallow pool of standing water, "
  "sitting beside an upturned wheelbarrow with a puddle collected in "
  "its well"),
 ("Garden and Plant Care Zone", "PDF-011",
  "A SHELF OF PART-USED CHEMICALS HAS LABELS TOO WORN TO READ",
  "a garden shelf holding several part-used spray bottles and a jug, "
  "their printed labels faded and peeling past legibility"),
 ("Garden and Plant Care Zone", "PDF-012",
  "A TOOL LEANS BLADE DOWN AND A DRAINLESS POT SITS NESTED WITH THE "
  "GOOD ONES",
  "a long-handled garden tool leaning blade-first against a patio rail "
  "beside a stack of nested terracotta pots, one of them clearly "
  "missing a drainage hole"),

 ("Outdoor Storage Zone", "PDF-013",
  "A CROQUET SET MISSING TWO MALLETS AND A DAMP BAG OF CHARCOAL SIT IN "
  "THE DECK BOX",
  "an open deck box revealing a croquet set with only two mallets, "
  "several old furniture covers, and a bag of charcoal visibly clumped "
  "with moisture"),
 ("Outdoor Storage Zone", "PDF-014",
  "THE LID DOESN'T STAY UP ON ITS OWN AND A CUSHION STILL SMELLS OF "
  "MILDEW",
  "a deck box lid caught mid-fall at a child's hand height beside a "
  "cushion pulled halfway out, faint gray speckling visible along its "
  "seam"),
 ("Outdoor Storage Zone", "PDF-015",
  "CLOSING THE LID TAKES LEANING YOUR WEIGHT ON IT",
  "a person's hand pressing down hard on an overstuffed deck box lid "
  "that will not close flat on its own"),

 ("Surface, Rail, and Safety Zone", "PDF-016",
  "A PLANTER, A COILED HOSE, AND A SAND BAG SIT ALONG THE WALKING ROUTE",
  "a large planter sitting in the middle of a deck walkway, a garden "
  "hose coiled across the top step nearby, and a bag of paving sand "
  "leaning against a rail post"),
 ("Surface, Rail, and Safety Zone", "PDF-017",
  "NOBODY HAS PUSHED THE RAIL OR PROBED THE SOFT BOARD IN A WHILE",
  "a hand pushing against a deck rail post that visibly leans, with a "
  "screwdriver resting nearby beside a board showing a faint soft spot"),
 ("Surface, Rail, and Safety Zone", "PDF-018",
  "GREEN ALGAE FILM COATS THE SHADED TREADS AND THE BOARD GAPS ARE "
  "PACKED",
  "a shaded wooden stair tread coated in a thin green algae film, with "
  "debris-packed gaps visible between the deck boards beside it"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, patio-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "three sets of grilling tongs and extra sauce bottles "
           "crowding a grill-side cabinet that was only ever meant to "
           "hold one of each",
 "KC-002": "a garden hose and a bag of paving sand leaning against a "
           "deck rail post with no shed or box ever assigned to either",
 "KC-003": "a folded lounge chair leaning by the back door instead of "
           "against the rail at the far end of the patio",
 "KC-004": "a hand reaching to buy a third propane tank rather than "
           "carrying the first two to a scale and marking the level on "
           "the collar",
 "KC-005": "a stack of nested terracotta pots hiding a drainage hole "
           "nobody can see until the pot is already lifted off the "
           "stack",
 "KC-007": "a deck box already packed with pool toys and old covers, "
           "leaving no room for the cushion trying to come in for the "
           "night",
 "KC-008": "a propane tank collar with no level ever marked on it, so "
           "every household member decides differently whether it "
           "needs replacing",
 "KC-009": "a grease tray sitting unemptied under a grill with no "
           "tracked count of cooks anywhere to say it is overdue",
 "KC-010": "a deck rail post that shifts under a hard push, right where "
           "a hand would grab it to keep from falling",
 "KC-011": "a propane tank that feels heavy enough to seem full, "
           "quietly running out mid-cook with nobody having weighed it "
           "first",
 "KC-012": "two different sets of hands packing the same deck box at "
           "each end of a season, neither agreeing on what goes on top",
 "RC-013": "an emptied patio table after dinner with nobody having "
           "claimed the job of cranking the umbrella down on the way "
           "inside",
 "RC-014": "a leggy plant grown from a cutting off a family member's "
           "garden, still sitting in a drainage-less pot nobody wants "
           "to disturb",
 "RC-015": "a shelf of half-used garden chemicals with worn labels, "
           "avoided rather than sorted for another season",
 "RC-016": "a burner tube packed with spider web, reachable only by "
           "pulling the flavorizer bars first",
 "RC-017": "a green film on a shaded stair tread that has been there "
           "long enough to stop looking like a hazard",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Outdoor Seating Zone": [
  "Hose each chair frame to float the loose grit off, then scrub the "
  "woven webbing across the weave with a stiff brush until the rinse "
  "water runs clear.",
  "Stand each washed chair on its side so water trapped inside the "
  "hollow leg tubing runs out instead of sitting there all summer.",
  "Sponge each cushion with mild soapy water, stand it on its edge with "
  "both faces open to the air, and check the underside for black "
  "speckling before it dries.",
 ],
 "Grill and Outdoor Cooking Zone": [
  "Run the burners hot for ten minutes to char residue to ash, then "
  "scrape the grates clean with the grill's own scraper, not a wire "
  "brush.",
  "Pull the flavorizer bars, scrape the baked-on crust into the bin, "
  "and look straight up into each burner tube for nest debris blocking "
  "the venturi.",
  "Slide the grease tray and drip pan out of their rails, wash both "
  "with degreaser and hot water, and dry them fully before they go "
  "back.",
 ],
 "Outdoor Dining Zone": [
  "Wash the tabletop along the grain, working extra suds into the "
  "collar where the umbrella pole passes through so no puddle sits in "
  "the joint.",
  "Open the umbrella canopy, brush off bird mess and cobwebs, sponge "
  "the fabric, and leave it open to dry fully before furling it closed.",
  "Wipe the underside lip of the tabletop where hands pull chairs in "
  "and wasps like to start a nest, clearing any early mud start you "
  "find.",
 ],
 "Garden and Plant Care Zone": [
  "Tip the standing water out of every saucer, then scrub the white "
  "mineral crust off the rims with a stiff brush and rinse clean.",
  "Tip each pot to check its drain hole is open, poking any clogged "
  "one clear with a stick before it goes back on the shelf.",
  "Scrape the caked soil off the trowel and pruner blades, dry them "
  "fully, and put a drop of tool oil on the pruner pivot.",
 ],
 "Outdoor Storage Zone": [
  "Empty the deck box completely, wipe the rubber sealing edge in its "
  "fold, then scrub the interior walls with warm soapy water and "
  "rinse.",
  "Prop the lid open on a dry, breezy day and leave it until the "
  "corners are genuinely dry to the touch, not just cool.",
  "Tip the box forward and sweep out the packed leaf mulch built up "
  "underneath it, then wipe the latch and handles clean.",
 ],
 "Surface, Rail, and Safety Zone": [
  "Rake each gap between the boards clear with a putty knife until you "
  "can see daylight through it, before water packs in and starts rot.",
  "Scrub the green algae film off the stair treads with a stiff brush, "
  "since that shaded film turns to grease and is the slipperiest "
  "surface here after rain.",
  "Wash the top rail where hands leave grime, then work down the "
  "balusters and into the gaps between the spindles where cobwebs "
  "gather unseen.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-patio actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "PDA-001", "zone": "Outdoor Seating Zone",
  "title": "PRESS EVERY CHAIR AND BOX THE CUSHIONS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Press every chair for a wobble, a crack, or a flex, and carry "
          "every cushion sitting anywhere except a chair into the deck "
          "box.",
  "why": "A chair that fails under someone fails suddenly, and a cushion "
         "left out is what turns one damp night into a week of drying "
         "or a replacement cost.",
  "inputs": ["the deck box"],
  "steps": [
   "Sit in every chair and press the seat pan hard with your palm, pull "
   "any chair that wobbles, cracks, or flexes out of the circle, and "
   "carry every cushion sitting anywhere except a chair into the deck "
   "box.",
   "Carry a failed chair straight to the curb rather than setting it "
   "back down in a corner of the patio."],
  "causes": ["KC-010", "KC-009"],
  "victory": "Every remaining chair passes a hard press with no flex or "
             "crack, and every cushion is in the deck box.",
  "next": "PDS-001",
  "art": "a hand pressing hard on a patio chair seat pan, a cushion "
         "being carried toward an open deck box behind it"},

 {"id": "PDA-002", "zone": "Outdoor Seating Zone",
  "title": "SET THE CHAIR COUNT AND CLEAR THE ROUTE",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Count who actually sits out here on an ordinary evening, "
          "settle that many chairs plus two as the standing rule, hang "
          "the furniture cover on its own hook, and clear anything "
          "parked in the route between the door and the steps.",
  "why": "A hazard chair only gets replaced once there is an agreed "
         "point where 'looks fine' stops being enough, a cover with "
         "nowhere of its own ends up crumpled on the ground, and a "
         "route nobody's specifically checking is the one people trip "
         "on carrying a tray in the dark.",
  "inputs": ["a wall hook for the cover"],
  "steps": [
   "Count who actually sits out here on an ordinary evening, settle "
   "that many chairs plus two as the standing rule, and move any extra "
   "chair off the patio.",
   "Fold and hang the furniture cover on its own hook, and carry "
   "anything parked in the route between the door and the steps back "
   "to where it belongs."],
  "causes": ["KC-008", "KC-007", "KC-002", "KC-003", "RC-013", "RC-017"],
  "victory": "The chair count matches how many people actually sit out "
             "here plus two, the cover hangs on its own hook, and the "
             "route from the door to the steps is bare.",
  "next": "PDA-001",
  "art": "a hand hanging a folded furniture cover on a wall hook beside "
         "a bare patio walkway, extra chairs stacked at the edge ready "
         "to leave"},

 {"id": "PDA-003", "zone": "Grill and Outdoor Cooking Zone",
  "title": "EMPTY THE CABINET AND HANG FOUR TOOLS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the side shelf and the cabinet completely, wipe the "
          "grease tray out, and hang exactly one tong, one spatula, one "
          "thermometer, and one basting brush back on the grill's own "
          "hooks.",
  "why": "A cabinet nobody's looked inside all season is how three sets "
         "of tongs and a dead thermometer accumulate, and the tools you "
         "actually need should be on the hooks, not buried behind them.",
  "inputs": ["a bin bag"],
  "steps": [
   "Empty the side shelf and the cabinet completely, wipe the grease "
   "tray out, and hang the one tong, one spatula, one thermometer, and "
   "one basting brush you are keeping back on the grill's own hooks.",
   "Bag the dried-out lighter cubes, the extra tongs, and any sauce "
   "bottle that spent the summer at outdoor temperature."],
  "causes": ["KC-001", "KC-005"],
  "victory": "The grill's own hooks hold exactly one tong, one spatula, "
             "one thermometer, and one basting brush, and the grease "
             "tray sits empty in its rails.",
  "next": "PDS-002",
  "art": "an emptied grill-side cabinet with a single tong, spatula, "
         "thermometer and basting brush hanging from the grill's own "
         "hooks nearby"},

 {"id": "PDA-004", "zone": "Grill and Outdoor Cooking Zone",
  "title": "WEIGH THE TANKS AND START THE COOK COUNT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Weigh each propane tank on a bathroom scale, subtract the "
          "tare weight, and mark the result on the collar; then start a "
          "tracked count of cooks on a card taped inside the cabinet "
          "door for when the grease tray gets emptied.",
  "why": "Guessing a tank's level by lifting it is slower and less "
         "honest than the five minutes weighing takes, and a grease "
         "tray with no tracked trigger only gets scraped once somebody "
         "notices the smell, by which point the flare-up risk has "
         "already been sitting there.",
  "inputs": ["a bathroom scale", "a marker", "an index card"],
  "steps": [
   "Weigh each tank, subtract the tare weight stamped on the collar as "
   "TW, and mark the remaining propane weight on the collar in marker.",
   "Tape a card inside the cabinet door and start a tally of cooks "
   "toward the next grease tray emptying, and brush soapy water on the "
   "hose and regulator to check for leaking bubbles while the tanks "
   "are out."],
  "causes": ["KC-008", "KC-011", "KC-004", "KC-009", "KC-010", "RC-016"],
  "victory": "Every tank's remaining level is marked on its collar, and "
             "a card inside the cabinet door is tracking cooks toward "
             "the next grease tray emptying.",
  "next": "PDA-003",
  "art": "a propane tank standing on a bathroom scale beside a hand "
         "marking a number on its collar, an index card taped inside a "
         "grill cabinet door nearby"},

 {"id": "PDA-005", "zone": "Outdoor Dining Zone",
  "title": "CLEAR THE TABLE AND CRANK THE UMBRELLA DOWN",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the table down to bare surface, crank the umbrella "
          "down, and tuck every chair fully under.",
  "why": "Everything else that lives on this table, the burned-down "
         "bucket, the dead lighter, the faded plates, is easier to face "
         "once the table is actually bare, and an open umbrella left up "
         "is a sail waiting for wind.",
  "inputs": ["a bin bag"],
  "steps": [
   "Clear the table down to bare surface, crank the umbrella down, and "
   "tuck every chair fully under.",
   "Bag the burned-down citronella bucket, the dead lighter, and any "
   "plate or tumbler from a set you are not keeping."],
  "causes": ["KC-001", "KC-010"],
  "victory": "The table holds only the umbrella and the one weighted "
             "tray, the umbrella is cranked down, and every chair is "
             "tucked fully under.",
  "next": "PDS-003",
  "art": "a bare outdoor dining tabletop holding only a weighted tray "
         "and a cranked-down umbrella, chairs tucked fully under on "
         "every side"},

 {"id": "PDA-006", "zone": "Outdoor Dining Zone",
  "title": "DECIDE THE DISHWARE AND NAME THE CLOSER",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Decide once whether this table gets its own stackable "
          "dishware set or borrows from the kitchen, swap any household "
          "extension cord running to the string lights for outdoor-"
          "rated cord, and agree who does the closing pass each night.",
  "why": "A half-answer on dishware is why the table always has "
         "something standing on it, an indoor cord across wet boards is "
         "a real shock risk, and a closing pass with no name attached "
         "depends on hoping somebody else already did it.",
  "inputs": ["a lidded tote", "outdoor-rated extension cord"],
  "steps": [
   "Count the meals you genuinely ate out here last season: if it was "
   "more than a handful, buy one stackable set for the seats and keep "
   "it in a lidded tote in the deck box; if it was two or three, carry "
   "the indoor plates out instead and let the orphaned half-set go.",
   "Swap any indoor extension cord running to the string lights for "
   "outdoor-rated cord on a proper outlet, and say out loud which one "
   "of you does the closing pass, cranking the umbrella and clearing "
   "the table, each night."],
  "causes": ["RC-015", "KC-008", "RC-017", "KC-004", "RC-013", "KC-009"],
  "victory": "The dishware decision is made and the orphaned half-set "
             "is gone, the string lights run on outdoor-rated cord, and "
             "one of you is named as the one who does the closing pass.",
  "next": "PDA-005",
  "art": "a stackable set of outdoor dishware in a lidded tote beside a "
         "coil of outdoor-rated cord, a patio table visible behind them"},

 {"id": "PDA-007", "zone": "Garden and Plant Care Zone",
  "title": "TIP OUT THE STANDING WATER AND PULL THE BAD POTS",
  "minutes": 15, "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Walk the row of saucers, the wheelbarrow well, and any "
          "upturned pot lid tipping out standing water, then pull any "
          "pot with no drainage hole or last year's dead root ball out "
          "of the nested stack.",
  "why": "Standing water breeding mosquitoes near a patio people "
         "actually sit on is a real health hazard, and a pot with no "
         "working drain hole is doing nothing for the plant it is "
         "supposedly housing.",
  "inputs": ["a rag"],
  "steps": [
   "Walk the row of saucers, the wheelbarrow well, and any upturned pot "
   "lid tipping out standing water, then pull any pot with no drainage "
   "hole or last year's dead root ball out of the nested stack.",
   "Wipe each emptied saucer dry before setting it back under its pot."],
  "causes": ["KC-009", "KC-010", "KC-005"],
  "victory": "No saucer, wheelbarrow well, or pot lid on the patio "
             "holds standing water, and every pot in the nested stack "
             "has a clear drain hole and nothing dead in it.",
  "next": "PDS-004",
  "art": "a hand tipping standing water out of a terracotta plant "
         "saucer, an upturned wheelbarrow with a dry well beside it"},

 {"id": "PDA-008", "zone": "Garden and Plant Care Zone",
  "title": "CLEAR THE CHEMICAL SHELF AND TAG EVERY POT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Read every bottle on the chemical shelf and take anything "
          "unlabeled or unused in the last two growing seasons to "
          "household hazardous waste, decide whether the pot with the "
          "family cutting gets repotted properly this week, and tag "
          "every remaining pot with what is in it and the month it "
          "went in.",
  "why": "An unlabeled concentrate cannot be used safely by whoever "
         "finds it later, an undecided cutting just occupies a "
         "drainage-less pot indefinitely, and a pot with no tag is a "
         "question you have to walk over and ask instead of read from "
         "the doorway.",
  "inputs": ["small tags and a marker", "a box for hazardous waste "
             "drop-off"],
  "steps": [
   "Read every bottle on the chemical shelf: anything with a label too "
   "worn to read, or anything you have not used in the last two "
   "growing seasons, goes into the hazardous waste box, and buy the "
   "smallest container the shop sells from now on.",
   "Decide whether the cutting from a family member's garden gets "
   "repotted into something with a drain hole this week or given away, "
   "and tag every pot you are keeping with what is in it and the month "
   "it went in."],
  "causes": ["KC-010", "RC-015", "KC-001", "RC-014", "RC-017"],
  "victory": "The chemical shelf holds only labeled containers you "
             "have used in the last two seasons, the family cutting has "
             "either been repotted or given away, and every remaining "
             "pot carries a tag.",
  "next": "PDA-007",
  "art": "a hand placing an unlabeled spray bottle into a hazardous "
         "waste box, a small tag being tied to a repotted plant nearby"},

 {"id": "PDA-009", "zone": "Outdoor Storage Zone",
  "title": "EMPTY THE BOX AND PULL THE ORPHANS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the deck box completely onto the boards, and pull out "
          "anything mildewed past saving, missing half its pieces, or "
          "belonging to furniture you no longer own.",
  "why": "None of it has anywhere else assigned to go, which is why a "
         "box meant for cushions has slowly filled with a croquet set "
         "missing two mallets and four covers for furniture that left "
         "years ago.",
  "inputs": ["a donation bag", "a bin bag"],
  "steps": [
   "Empty the deck box completely onto the boards, and pull out "
   "anything that is mildewed past saving, missing half its pieces, or "
   "belongs to furniture you no longer own.",
   "Sort what is left into what is actually cushions, and everything "
   "else waiting to go into the two labeled totes."],
  "causes": ["KC-002", "RC-015"],
  "victory": "The deck box floor is visible with only cushions and the "
             "two labeled totes waiting to go back in, and nothing "
             "else.",
  "next": "PDS-005",
  "art": "the contents of a deck box spread across patio boards, a "
         "croquet set with missing mallets and old furniture covers "
         "being sorted into a donation bag"},

 {"id": "PDA-010", "zone": "Outdoor Storage Zone",
  "title": "FIT THE LID STAY AND LATCH IT EVERY NIGHT",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Fit a lid stay so the lid cannot drop free at hand height, "
          "wash and fully dry anything worth saving from the sort, "
          "settle the box's single job as cushions only, and agree that "
          "cushions go in last, latched, every night.",
  "why": "An unsupported lid crushes fingers at exactly the height a "
         "child reaches, a cushion that still smells of mildew after "
         "washing has the growth inside the foam and no scrubbing "
         "reaches that, and a box with no agreed single job is why it "
         "never stays organized past the first week.",
  "inputs": ["a lid stay", "a screwdriver"],
  "steps": [
   "Fit a lid stay so the lid cannot drop free at hand height, and "
   "confirm it holds when you let go halfway.",
   "Wash and fully dry anything worth saving, discard any cushion that "
   "still smells of mildew once dry, settle that the box holds "
   "cushions and the two totes only, and agree that cushions go in "
   "last with the latch fastened every night."],
  "causes": ["KC-010", "RC-016", "KC-008", "KC-012", "KC-009", "RC-017",
             "KC-005"],
  "victory": "A lid stay holds the open lid safely, nothing mildewed "
             "went back in, the box holds only cushions and the two "
             "totes, and the lid is latched every night without anyone "
             "leaning on it to close.",
  "next": "PDA-009",
  "art": "a hand fitting a lid stay bracket to an open deck box, a "
         "latch visible on the closed lid beside it"},

 {"id": "PDA-011", "zone": "Surface, Rail, and Safety Zone",
  "title": "WALK THE ROUTE WITH A FULL LAUNDRY BASKET",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Walk the full route from the door to the steps to the gate "
          "carrying a full laundry basket in both arms, and pull off "
          "the route anything you have to step around.",
  "why": "A planter, a hose, or a sand bag does not look like it is "
         "blocking anything until you actually cannot see your feet, "
         "and each of them also holds damp against the wood it sits on.",
  "inputs": ["a laundry basket"],
  "steps": [
   "Walk the full route from the door to the steps to the gate "
   "carrying a full laundry basket in both arms, and pull off the "
   "route anything you have to step around.",
   "Carry each item to where it actually belongs rather than setting "
   "it down again somewhere else on the deck."],
  "causes": ["RC-017", "KC-002"],
  "victory": "The full route from the door to the steps to the gate is "
             "clear enough to walk carrying a full laundry basket "
             "without stepping around anything.",
  "next": "PDS-006",
  "art": "a person carrying a full laundry basket in both arms along a "
         "cleared deck walkway from a back door toward a short flight "
         "of steps"},

 {"id": "PDA-012", "zone": "Surface, Rail, and Safety Zone",
  "title": "PUSH THE RAIL, PROBE THE BOARD, SCRUB THE TREADS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Push the top rail hard, outward and down, at every post, "
          "probe any board that flexes or feels soft with a screwdriver "
          "at the joist and at the board end nearest the house, scrub "
          "the green algae film off every shaded board and stair tread, "
          "and mark today's date on the tag inside the back door.",
  "why": "A rail or board that fails does so suddenly and from "
         "underneath, algae on the shaded treads turns to grease after "
         "rain on the exact surface people cross barefoot, and a check "
         "with no dated record behind it is an argument waiting to "
         "happen about whether it happened at all.",
  "inputs": ["a screwdriver", "a stiff brush"],
  "steps": [
   "Push the top rail hard, outward and then down, at every post, and "
   "probe any board that flexes or feels soft with a screwdriver at "
   "the joist and at the board end nearest the house.",
   "Scrub the green algae film off every shaded board and stair tread, "
   "and mark today's date on the tag inside the back door."],
  "causes": ["KC-010", "KC-009", "RC-013", "RC-016", "RC-017", "KC-005"],
  "victory": "Every rail post holds firm under a hard push, any soft "
             "board has been dealt with, the shaded treads are free of "
             "algae film, and today's date is marked on the tag inside "
             "the back door.",
  "next": "PDA-011",
  "art": "a hand pushing hard against a deck rail post, a screwdriver "
         "resting on a nearby board, a dated tag visible just inside a "
         "back door"},

 {"id": "PDA-013", "zone": None, "title": "THE FULL PATIO HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking the rail and boards, the grease "
          "tray and tank, the chemical box latch, and the deck box lid "
          "stay in one pass.",
  "why": "This room's own hazards, a rail post that gives, an overdue "
         "grease tray next to the siding, an unlatched chemical box, a "
         "deck box lid with no stay, sit across four different zones "
         "and only get found together if someone walks the whole patio "
         "on purpose.",
  "inputs": ["a screwdriver"],
  "steps": [
   "Push the top rail hard at every post and probe any board that "
   "flexes underfoot, and check the grease tray is not overdue and the "
   "grill sits a clear arm's length from the siding and the rail.",
   "Confirm the chemical box is latched and every container inside it "
   "is labeled, and check the deck box lid holds itself up on its own "
   "stay rather than dropping free."],
  "causes": ["KC-010", "RC-016"],
  "victory": "No rail post moves under a hard push, no board is soft, "
             "the grease tray is not overdue, the chemical box is "
             "latched, and the deck box lid holds itself up on its own "
             "stay.",
  "next": "PDE-001",
  "art": "a hand checking a deck rail post beside a latched chemical "
         "box and an open deck box held safely up on its own lid stay"},

 {"id": "PDA-014", "zone": None,
  "title": "WHAT THE REST OF THE HOUSE OFFLOADED ONTO THE PATIO",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Walk the whole patio looking for anything that belongs to "
          "another part of the house or yard entirely, and move each "
          "thing back to where it is actually used.",
  "why": "This is the only dry lidded space outside, so anything with "
         "nowhere else assigned to it tries to live here too: a "
         "recycling bin waiting on pickup, a box of holiday lights, a "
         "tool that belongs in the garage.",
  "inputs": ["a hand truck for anything heavy"],
  "steps": [
   "Walk the whole patio and pull out anything that plainly belongs "
   "somewhere else: a recycling bin waiting past pickup day, a box "
   "meant for the garage, decor from a season that has already ended.",
   "Carry each item to where it is actually used today, not to a "
   "corner of the deck box, and if nowhere else in the house wants it, "
   "that is itself the answer."],
  "causes": ["KC-002", "KC-003"],
  "victory": "Nothing remains on the patio that plainly belongs to "
             "another room or the garage's own job, and every item "
             "pulled has either moved to where it is used or left the "
             "house.",
  "next": "PDA-015",
  "art": "a box of holiday decor and a recycling bin being carried off "
         "a patio toward a back door and a garage"},

 {"id": "PDA-015", "zone": None, "title": "THE LAST-ONE-OUTSIDE RESET",
  "minutes": 15, "players": "1 to 2", "six_s": "Sustain",
  "goal": "Whoever is last outside for the night carries the cushions "
          "in and latches the box, closes and scrapes the grill, cranks "
          "the umbrella down, and glances down the row of saucers.",
  "why": "Every standard on this patio is built to survive a bad "
         "evening, and the only way that holds is checking it against "
         "its own standard on the way inside, not noticing days later "
         "that it slipped.",
  "inputs": ["nothing, this is a walk-through"],
  "steps": [
   "Carry the cushions into the deck box and fasten the latch, and "
   "scrape the grill's hot grates before you close the lid.",
   "Crank the umbrella down and glance along the row of saucers on "
   "your way back to the door."],
  "causes": ["KC-009", "RC-017"],
  "victory": "The cushions are latched in the deck box, the grill "
             "grates are scraped and the lid closed, the umbrella is "
             "cranked down, and no saucer is holding standing water.",
  "next": "PDA-013",
  "art": "a hand latching a deck box lid at dusk, a cranked-down "
         "umbrella and a closed grill visible on the same patio"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a patio or deck, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("PDE-001", "THE NIGHT GUESTS SHOW UP UNANNOUNCED",
  "Neighbors text that they are coming over in twenty minutes for a "
  "last-minute evening on the patio, chairs and all.",
  ["PDZ-001"],
  "Every chair is trustworthy to sit in without checking it first, and "
  "the cushions come out of the deck box dry and ready in one trip.",
  "If you had to test a chair before offering it to a guest, or a "
  "cushion came out damp or missing, the reset never actually finished. "
  "Draw PDA-002.",
  "a small group of patio chairs with cushions being lifted from an "
  "open deck box just before guests arrive"),
 ("PDE-002", "THE COOKOUT WHERE THE FLAME GOES YELLOW MID-SEAR",
  "You light the grill for a full cookout and the flame on one side "
  "burns yellow and lazy instead of blue.",
  ["PDZ-002"],
  "The burner tubes were checked clear of debris last time the grates "
  "came off, so the flame lights evenly across every burner.",
  "If one side runs yellow and weak, a blocked venturi tube was never "
  "cleared last time. Draw PDA-004.",
  "a lit gas grill with one burner showing a yellow, uneven flame "
  "compared to the clean blue flame beside it"),
 ("PDE-003", "THE EVENING WIND PICKS UP MID-DINNER",
  "You are partway through dinner outside when the wind picks up hard "
  "enough to lift the corner of the tablecloth.",
  ["PDZ-003"],
  "The umbrella base is weighted to match the canopy, so cranking it "
  "down before the gusts get worse is a five-second job, not a "
  "scramble.",
  "If the umbrella lifted or the base could not hold it down, the base "
  "weight was never actually matched to the canopy. Draw PDA-006.",
  "a patio table with a tablecloth corner lifting in the wind, a hand "
  "reaching to crank the umbrella down"),
 ("PDE-004", "THE WEEK WITH NO RAIN AT ALL",
  "It has not rained in a week and every pot on the patio is relying "
  "entirely on you and the watering can.",
  ["PDZ-004"],
  "Every pot carries a tag naming what is in it and when it went in, "
  "so you can water the right amount without guessing or coming to "
  "find anyone.",
  "If you had to guess what a pot needed or ask someone else, the tag "
  "was never written. Draw PDA-008.",
  "a hand holding a watering can beside a row of tagged pots on a dry "
  "patio"),
 ("PDE-005", "THE STORM THAT ARRIVES WITHOUT WARNING",
  "A storm rolls in fast on an evening when the cushions are still out "
  "on the chairs.",
  ["PDZ-005"],
  "Every cushion goes into the deck box in one trip and the latch goes "
  "across before the first hard rain hits.",
  "If a cushion got left out, or the lid stood unlatched in the wind, "
  "the box was not holding to its one job. Draw PDA-010.",
  "hands lowering a cushion into an open deck box as dark clouds "
  "gather overhead"),
 ("PDE-006", "THE PARTY WHERE EVERYONE LEANS ON THE RAIL AT ONCE",
  "A party fills the patio and several people end up leaning on the "
  "rail together at the same time.",
  ["PDZ-006"],
  "Every post holds firm because the rail was pushed hard at every "
  "post and any soft board was already replaced.",
  "If a post gave even slightly under the weight, the seasonal "
  "push-and-probe check has slipped. Draw PDA-012.",
  "several people leaning against a deck rail at an evening gathering, "
  "the rail posts standing firm beneath them"),
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
        "related": {"standard": f"PDS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true on your patio, then "
                       "turn to that root cause card. If two are true, "
                       "take the one you could change this week.",
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
    standard_id = (f"PDS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"PDS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "PDR-001", "title": "THE PATIO OR DECK", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. THE SURFACE AND THE RAIL COME FIRST.",
        "objective": "A patio lives outdoors, on a clock the indoor "
                     "rooms never feel. This card is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"PDZ-006 Surface, Rail, and Safety Zone. {start_tip['text']}"
            if start_tip else
            "PDZ-006 Surface, Rail, and Safety Zone. If the boards and "
            "the railing are not sound, everything you arrange on top "
            "of them is decoration."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Start with the Surface, "
            "Rail, and Safety Zone on a dry morning, before you touch a "
            "single cushion.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true on your patio. Put the rest back.",
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
        "players": "1 to 2. Cleaning out here is how you inspect: you "
                   "will never spot a popped fastener, a soft board end, "
                   "or a spider web in a burner tube while sitting in a "
                   "chair.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do PDA-013 The Full Patio Hazard Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "the rail and boards, the grease tray and tank, "
                        "the chemical box latch, and the deck box lid "
                        "stay in one pass.",
        "related": {"contents": "PDZ-001 to PDZ-006, PDF-001 to "
                                 "PDF-018, the shared root causes in "
                                 "ops/root_causes.py, PDA-001 to "
                                 "PDA-015, PDS-001 to PDS-006, PDE-001 "
                                 "to PDE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole patio "
                           "in its settled state, four chairs set for "
                           "conversation with cushions visible, a grill "
                           "with its tools on the hooks, a dining table "
                           "holding only its umbrella and tray, a "
                           "closed deck box, and nested pots along the "
                           "wall, all visible in one frame",
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
    return {"deck": "patio-or-deck", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_nursery_deck.py)."""
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

    assert any(c["id"] == "PDA-013" for c in cards), "no safety walk card"
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
    print(f"  deck        patio-or-deck ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
