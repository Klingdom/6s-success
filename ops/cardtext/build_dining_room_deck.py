#!/usr/bin/env python3
"""
Build the Dining Room deck: 61 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: nine rooms already carry a full diagnosis layer
and a shipped deck (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home
Office, Garage, Stair Landing, Pantry, Hall Closet). Dining Room is the
next room built the same way: rich, hand-authored Manual content for all
five zones (purpose, done_looks_like, passes, the_call, watch_for,
leave_behind, shine_detail), but no diagnosis layer and no deck until this
file. It adds that layer to content/manual/source/content.json (fifteen
frictions, forty-five branches, five first_15 actions) and builds the deck
straight off it, the same shape ops/cardtext/build_hall_closet_deck.py
already uses for its own five-zone room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
fifteen frictions (symptom and every branch to a root cause) are likewise
derived straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the ten
zone-linked action cards, the three whole-room actions, the event cards,
the micro quests, and the room card. The root causes are not reauthored:
they are the same frozen vocabulary in ops/root_causes.py that every other
room's deck already uses, so a household owning more than one deck keeps one
diagnosis pile rather than several (DECK-GAME-DESIGN.md 4.3). All seventeen
shared ids are reachable from this room's real frictions, counted honestly
from the branches actually written below, not chosen first and filled in:
this room's five zones (a shared table, a serving surface, a storage
cabinet, a display cabinet, and a consumables station) happen to cover the
full spread this business has diagnosed anywhere: excess, no assigned home,
wrong location, excess motion, poor visibility, poor accessibility,
insufficient capacity, missing standard, missing trigger, a real safety
constraint, poor replenishment, conflicting users, unclear ownership,
sentimental attachment, an unresolved decision, a surface that is genuinely
difficult to clean, and perceptual blindness. Nothing here pads the count;
every branch below is grounded in this room's own real Manual text (the_call,
passes, watch_for, shine_detail) and the mapping was checked against
ops/preflight.py's gate_diagnosis_branch_shape before this file was written.

WHAT THE BUDGET IS AND WHY
---------------------------
Dining Room ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). Five real
zones, fifteen frictions (three per zone), seventeen reachable root causes,
thirteen action cards (two per zone plus three whole-room), five standard
cards and five event cards. 61 cards in total, not padded or trimmed to
match any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_dining_room_deck.py
Out:  ops/cardtext/dining-room-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "dining-room-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Dining Room"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 5, "FRICTION CARD": 15,
          "ROOT CAUSE CARD": 17, "ACTION CARD": 13, "STANDARD CARD": 5,
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

# Every one of the 17 shared ids. Derived below from the Manual and
# asserted (in gate()) to be exactly this set: not a number chosen first
# and filled in. Confirmed against content/manual/source/content.json
# before this file was written.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011", "KC-012",
             "RC-013", "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Dining Table": {
  "id": "DRZ-001", "order": 1, "difficulty": 2,
  "tagline": "ONE CENTERPIECE. BARE WOOD. NOTHING ELSE ON IT.",
  "callouts": [
   "One centerpiece sitting alone on bare wood",
   "Every chair pushed fully in, nothing hanging off any chair back",
   "No paper anywhere on the tabletop",
   "A trivet visible just inside the nearest sideboard drawer",
   "Placemats stacked in that same drawer",
   "The chair rungs and legs clear of anything leaning against them",
  ],
  "art": ("a set dining table with one centerpiece on bare wood, every "
          "chair pushed fully in, and a sideboard drawer visible open "
          "nearby holding placemats and a trivet"),
 },
 "Buffet or Sideboard Surface": {
  "id": "DRZ-002", "order": 2, "difficulty": 2,
  "tagline": "ONE BARE RUN FOR SERVING. THREE PIECES FOR DISPLAY.",
  "callouts": [
   "A strip of tape marking a bare serving run at one end of the "
   "sideboard",
   "Three display objects grouped together at the lamp end",
   "A lamp standing among the display objects",
   "The lamp's cord the only cord visible",
   "No paper anywhere on the wood",
   "The serving run empty and clear of any object",
  ],
  "art": ("a sideboard with a taped bare wood run at one end and three "
          "display objects with a lamp grouped at the other end, no "
          "paper anywhere on the surface"),
 },
 "Buffet or Sideboard Storage": {
  "id": "DRZ-003", "order": 3, "difficulty": 3,
  "tagline": "TWO CLOTHS ROLLED WITH THEIR NAPKINS. A COUNT CARD INSIDE "
             "THE DOOR.",
  "callouts": [
   "Two rolled tablecloths sitting in one open drawer",
   "Napkins visible tucked inside each rolled cloth",
   "Serving bowls nested together by size in a separate drawer",
   "Large platters standing upright on edge behind a divider",
   "A latched drawer holding taper candles of matching length",
   "A count card taped to the inside of the door",
  ],
  "art": ("an open sideboard cabinet showing two rolled tablecloths with "
          "napkins in one drawer, nested serving bowls in another, and "
          "platters standing on edge behind a divider"),
 },
 "China or Display Cabinet": {
  "id": "DRZ-004", "order": 4, "difficulty": 3,
  "tagline": "EIGHT PLATES HIGH, WITH FELT BETWEEN THEM. STRAPPED TO THE "
             "WALL.",
  "callouts": [
   "A stack of plates no taller than eight, felt visible between each "
   "plate",
   "Cups standing single file in a row rather than nested together",
   "Glasses standing rim up on a clean shelf liner",
   "A tureen sitting on the cabinet's bottom shelf",
   "A visible strap securing the cabinet to the wall",
   "A small photo taped to the inside of the cabinet door",
  ],
  "art": ("a glass-fronted china cabinet with plates stacked no more "
          "than eight high with felt between them, cups standing single "
          "file, and a strap visible securing it to the wall"),
 },
 "Beverage or Coffee Station": {
  "id": "DRZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE TRAY. LEFT TO RIGHT. A LINE ON THE JAR.",
  "callouts": [
   "A coffee machine, grounds, mugs, and spoons arranged left to right "
   "on one tray",
   "The whole arrangement sitting on a single liftable tray",
   "A marked fill line visible on the bean jar",
   "A capped, limited number of mugs on the shelf",
   "A hand's width of clear space behind the kettle",
   "Spoons and sugar grouped together at one end of the tray",
  ],
  "art": ("a beverage station counter with a coffee machine, mugs, and "
          "spoons arranged left to right on one tray, a marked fill "
          "line visible on the bean jar"),
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
 "Dining Table": {
  "frictions": [
   {"symptom": "Homework, mail, or a craft project has been sitting on "
               "the table for days, migrating a few inches each evening "
               "but never actually leaving.",
    "branches": [
     {"answer": "That activity doesn't have anywhere else in the house "
                "to happen", "cause": "KC-002"},
     {"answer": "One person treats this as the family desk and everyone "
                "else wants it clear for dinner, and that's never "
                "actually been settled", "cause": "KC-012"},
     {"answer": "Clearing it before dinner isn't actually anyone's job, "
                "so it depends on who notices first", "cause": "RC-013"},
    ]},
   {"symptom": "A chair has started to wobble at the rungs, and everyone "
               "has quietly learned which one to avoid instead of "
               "getting it fixed.",
    "branches": [
     {"answer": "Nobody checks the chairs for looseness, it only gets "
                "noticed when one nearly gives way", "cause": "RC-013"},
     {"answer": "There's no agreed point at which a wobble becomes "
                "'needs fixing' instead of 'still fine'", "cause": "KC-008"},
     {"answer": "The wobble has gone on so long, people don't really "
                "register it as a problem to fix", "cause": "RC-017"},
    ]},
   {"symptom": "A hot dish has scorched the tabletop, or a candle has "
               "burned close to the runner, because the trivet was "
               "still in a drawer across the room when the food came "
               "out.",
    "branches": [
     {"answer": "The trivet doesn't live in the drawer nearest the "
                "table, so it's easier to skip than fetch",
      "cause": "KC-003"},
     {"answer": "There's no rule about candles and runners, so it's "
                "whatever looks nice that night", "cause": "KC-010"},
     {"answer": "Setting the table happens in a rush right before "
                "people sit down, so the trivet gets skipped",
      "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Clear the whole table onto the floor in one armful, then "
             "sort what came off by owner rather than by type. The "
             "homework, the unopened mail, and the half-finished craft "
             "project each go back to a person, not back to the table.",
   "victory": "The table holds nothing but its centerpiece, and every "
              "activity that was on it has gone home with the person "
              "who owns it.",
  },
 },
 "Buffet or Sideboard Surface": {
  "frictions": [
   {"symptom": "The mail lands on the sideboard the moment it comes "
               "through the door, and by the end of the week there's a "
               "loose stack where the bare wood used to be.",
    "branches": [
     {"answer": "Nothing tells the mail where else to go, so the "
                "nearest flat surface wins", "cause": "KC-002"},
     {"answer": "The mail pile isn't obviously wrong to look at "
                "anymore", "cause": "RC-017"},
     {"answer": "Opening the mail is its own decision nobody's made "
                "yet, so it just sits", "cause": "RC-015"},
    ]},
   {"symptom": "A lamp, a phone charger, and a warming tray all share "
               "one outlet behind the sideboard, and nobody has checked "
               "that plug in months.",
    "branches": [
     {"answer": "That plug is tucked behind heavy furniture where "
                "nobody ever looks", "cause": "KC-005"},
     {"answer": "There's no rule about how many things can share one "
                "outlet here", "cause": "KC-008"},
     {"answer": "Checking the cords back there isn't anyone's specific "
                "job", "cause": "RC-013"},
    ]},
   {"symptom": "More than three display pieces have collected at the "
               "lamp end, including a tall vase a small child could "
               "pull over reaching past it.",
    "branches": [
     {"answer": "There's no agreed limit on how many display pieces "
                "belong here", "cause": "KC-008"},
     {"answer": "Nice things keep getting added and nothing is ever "
                "removed to make room", "cause": "KC-001"},
     {"answer": "The vase has stood there long enough that its height "
                "at a child's reach stopped registering as a risk",
      "cause": "KC-010"},
    ]},
  ],
  "first_15": {
   "action": "Take everything off the wood, including the picture "
             "frames and the candlesticks, and give every piece of "
             "paper a verdict tonight: act on it, file it, or recycle "
             "it. Burnt-down candle stubs, dried flowers, and chargers "
             "belonging to other rooms leave now.",
   "victory": "The wood is bare, every piece of paper has a verdict, "
              "and nothing that belongs to another room is still "
              "sitting here.",
  },
 },
 "Buffet or Sideboard Storage": {
  "frictions": [
   {"symptom": "A tablecloth that doesn't actually fit the table "
               "anymore is still folded in this drawer, kept because "
               "letting go of good linen feels wasteful.",
    "branches": [
     {"answer": "Nobody's actually measured it against the table you "
                "own now", "cause": "RC-015"},
     {"answer": "It came from somebody else's table and giving it up "
                "feels like giving up the memory", "cause": "RC-014"},
     {"answer": "There's no rule that a cloth has to actually fit to "
                "earn a spot in the drawer", "cause": "KC-008"},
    ]},
   {"symptom": "The punch bowl and the heavy stoneware platters live on "
               "a shelf above shoulder height, and they only come down "
               "when your arms are already full of something else.",
    "branches": [
     {"answer": "Nobody thought about who'd actually have to lift it "
                "back down when it went up there", "cause": "KC-006"},
     {"answer": "Nobody's re-sorted this shelf by weight since it was "
                "first packed", "cause": "RC-013"},
     {"answer": "It's been stored that way so long it doesn't register "
                "as a reach risk anymore", "cause": "RC-017"},
    ]},
   {"symptom": "The everyday platters are stacked flat, so getting the "
               "one you actually need means lifting the two or three "
               "sitting on top of it first.",
    "branches": [
     {"answer": "There's no divider or system to stand them on edge, "
                "so reaching the one you want means moving the others "
                "every time", "cause": "KC-004"},
     {"answer": "It's only used a handful of times a year, so the "
                "extra effort never feels worth solving", "cause": "RC-017"},
     {"answer": "Reorganizing the platter shelf has never been "
                "anyone's assigned job", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Pull every tablecloth, runner, and napkin out and lay "
             "them across the table so you can see which sets are "
             "actually complete. Partial napkin sets, cloths with "
             "stains you have already tried and failed to lift, and "
             "serving pieces orphaned from sets you no longer own are "
             "finished.",
   "victory": "Every remaining linen set is complete, every serving "
              "piece belongs to a set you still own, and nothing "
              "carries a stain you've already failed to lift.",
  },
 },
 "China or Display Cabinet": {
  "frictions": [
   {"symptom": "There are twelve place settings of china from a "
               "relative behind this glass, more than the largest meal "
               "you've actually hosted in years, and deciding what to "
               "do with the rest feels impossible.",
    "branches": [
     {"answer": "It's not really china anymore, it's a person, and "
                "sorting it feels like a betrayal", "cause": "RC-014"},
     {"answer": "Nobody's actually counted the largest meal hosted "
                "against the number of settings kept", "cause": "RC-015"},
     {"answer": "Twelve settings genuinely doesn't fit this cabinet's "
                "shelves at eight plates high with felt between each, "
                "so stacks run taller than they should", "cause": "KC-007"},
    ]},
   {"symptom": "This cabinet has never been strapped to the wall, and "
               "its shelves are exactly the height a small child would "
               "use as a ladder.",
    "branches": [
     {"answer": "It's a bigger job than a quick tidy, so it keeps "
                "getting pushed to later", "cause": "KC-009"},
     {"answer": "Securing furniture like this has never been anyone's "
                "specific task", "cause": "RC-013"},
     {"answer": "It's stood there unstrapped so long, the risk doesn't "
                "register day to day", "cause": "RC-017"},
    ]},
   {"symptom": "The top of this cabinet, high and out of easy sight, "
               "has a visible layer of dust nobody's touched in a long "
               "time.",
    "branches": [
     {"answer": "Reaching up there means finding a stool first, so "
                "it's the last thing anyone bothers with",
      "cause": "RC-016"},
     {"answer": "It's high enough that you can't actually see it's "
                "dusty from normal eye level", "cause": "KC-005"},
     {"answer": "Nobody's assigned to check the top of this cabinet "
                "specifically", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Take every piece out and split it into three groups: "
             "complete sets, chipped or crazed pieces, and lone "
             "survivors of sets that are long gone. A chipped rim "
             "cannot be mended and is not safe to drink from, so that "
             "whole group leaves together.",
   "victory": "What's left behind the glass is complete sets and "
              "pieces without a chip or crack, nothing kept only out "
              "of habit.",
  },
 },
 "Beverage or Coffee Station": {
  "frictions": [
   {"symptom": "The bean jar has run below its own marked fill line "
               "more than once with nobody noticing until the machine "
               "sputtered out mid-pour.",
    "branches": [
     {"answer": "Topping the jar isn't tied to any specific moment, so "
                "it only happens when someone remembers",
      "cause": "KC-009"},
     {"answer": "The fill line is marked but nobody's actually "
                "assigned to check it", "cause": "RC-013"},
     {"answer": "This station runs low silently, nothing about it "
                "signals 'running out' before it's actually out",
      "cause": "KC-011"},
    ]},
   {"symptom": "There are two ways to make a hot drink on this "
               "counter, and one of them hasn't earned its counter "
               "space in months but nobody's tested that.",
    "branches": [
     {"answer": "Getting rid of a machine somebody might start using "
                "again feels premature", "cause": "RC-015"},
     {"answer": "It's been part of the counter so long it doesn't "
                "register as extra anymore", "cause": "RC-017"},
     {"answer": "There's no actual rule for how little use earns a "
                "machine its spot", "cause": "KC-008"},
    ]},
   {"symptom": "A bottle of wine and a couple of spirits sit open on a "
               "shelf at this station, within easy reach of a small "
               "child standing at the counter.",
    "branches": [
     {"answer": "There's no latch or high shelf assigned for alcohol "
                "at this station, only in the kitchen", "cause": "KC-002"},
     {"answer": "This station never got the same childproofing pass "
                "the kitchen did", "cause": "KC-010"},
     {"answer": "Moving the bottles higher keeps getting put off "
                "because it's a small job with no deadline",
      "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Line up every tea box, syrup bottle, and pod sleeve and "
             "check the dates, then open the travel mugs and match "
             "them to their lids. Anything past date, any mug missing "
             "its lid, and the promotional glassware you have never "
             "once poured into are out.",
   "victory": "Everything on the counter is in date, every travel mug "
              "has its matching lid, and no glassware sits here "
              "unused.",
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
 ("Dining Table", "DRF-001", "THE DESK THAT USED TO BE A TABLE",
  "a dining table with a laptop, a stack of mail, and a half-finished "
  "craft project spread across one end, the opposite end still set with "
  "a single centerpiece"),
 ("Dining Table", "DRF-002", "THE CHAIR EVERYONE QUIETLY AVOIDS",
  "a dining chair pulled slightly away from a table, visibly tilting on "
  "one leg, with place settings arranged at every other chair around "
  "it"),
 ("Dining Table", "DRF-003", "THE HOT DISH WITH NO TRIVET IN REACH",
  "a steaming dish set directly on bare dining table wood beside an "
  "unlit candle burned close to the edge of a table runner"),

 ("Buffet or Sideboard Surface", "DRF-004",
  "THE MAIL THAT NEVER LEFT THE SIDEBOARD",
  "a sideboard surface with a loose stack of unopened mail sitting "
  "where a bare serving run should be, a lamp and three display "
  "objects pushed aside"),
 ("Buffet or Sideboard Surface", "DRF-005",
  "THREE PLUGS BEHIND THE FURNITURE",
  "the back of a sideboard pulled slightly from the wall, revealing a "
  "single outlet crowded with a lamp plug, a phone charger, and a "
  "warming tray cord"),
 ("Buffet or Sideboard Surface", "DRF-006", "THE FOURTH DISPLAY PIECE",
  "a sideboard's display end crowded with four candlesticks and vases "
  "grouped together, one tall vase standing closest to the edge "
  "nearest a drawer"),

 ("Buffet or Sideboard Storage", "DRF-007",
  "THE TABLECLOTH FOR A TABLE YOU DON'T OWN",
  "an open sideboard drawer with a folded tablecloth clearly too small "
  "laid across a dining table, its edge falling short of the table's "
  "corners"),
 ("Buffet or Sideboard Storage", "DRF-008",
  "THE PLATTER ABOVE SHOULDER HEIGHT",
  "a stoneware platter and a punch bowl standing on a sideboard shelf "
  "above shoulder height, a hand reaching up toward them with both "
  "arms already full"),
 ("Buffet or Sideboard Storage", "DRF-009",
  "THREE PLATTERS TO REACH THE FOURTH",
  "a stack of flat serving platters inside a sideboard cupboard with "
  "the bottom platter partly pulled, the two platters above it lifted "
  "off to one side"),

 ("China or Display Cabinet", "DRF-010",
  "TWELVE SETTINGS FROM YOUR GRANDMOTHER",
  "a glass-fronted china cabinet packed with more full place settings "
  "than its shelves comfortably hold, stacks reaching close to the "
  "shelf above"),
 ("China or Display Cabinet", "DRF-011",
  "THE CABINET THAT'S NEVER BEEN STRAPPED DOWN",
  "a tall glass-fronted china cabinet standing away from the wall with "
  "no visible strap or bracket, a low stepped shelf at a small child's "
  "climbing height"),
 ("China or Display Cabinet", "DRF-012",
  "THE DUST ON TOP NOBODY'S TOUCHED IN YEARS",
  "the dusty top of a china cabinet seen from a raised angle, a "
  "visible layer of dust undisturbed across its surface, high above "
  "eye level"),

 ("Beverage or Coffee Station", "DRF-013",
  "THE BEAN JAR BELOW ITS OWN LINE",
  "a coffee bean jar on a counter with its contents sitting visibly "
  "below a marked fill line drawn on the glass"),
 ("Beverage or Coffee Station", "DRF-014", "THE SECOND MACHINE",
  "two coffee-making machines side by side on a counter, one with a "
  "sticky note and tally marks on it, the other bare and unused beside "
  "it"),
 ("Beverage or Coffee Station", "DRF-015",
  "THE WINE WITHIN A CHILD'S REACH",
  "an open shelf at a beverage station holding a wine bottle and two "
  "spirit bottles at the height of a small child standing at the "
  "counter"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, dining-room-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "more display objects crowded at one end of a sideboard than "
           "the space was ever meant to hold",
 "KC-002": "a stack of mail sitting on a dining table with no drawer or "
           "tray anywhere nearby assigned to catch it",
 "KC-003": "a trivet sitting in a drawer at the far side of a dining "
           "room, nowhere near the table it's meant to protect",
 "KC-004": "a stack of serving platters with the two top pieces lifted "
           "aside just to reach the one at the bottom",
 "KC-005": "a bean jar on a counter with its fill level impossible to "
           "see from a normal standing height",
 "KC-006": "a heavy stoneware platter sitting on a shelf above shoulder "
           "height with no step stool anywhere nearby",
 "KC-007": "a china cabinet shelf with plates stacked higher than the "
           "felt dividers between them were ever meant to allow",
 "KC-008": "a sideboard surface with no taped boundary anywhere to show "
           "where serving space ends and display space begins",
 "KC-009": "an unlit candle burned down close to a table runner with no "
           "marked moment that would have prompted moving it sooner",
 "KC-010": "a bottle of wine standing open on a shelf at exactly the "
           "height a small child would reach",
 "KC-011": "a coffee bean jar sitting visibly below its own marked fill "
           "line beside an empty mug",
 "KC-012": "a dining table with a laptop and papers spread across one "
           "end and a place setting arranged at the other",
 "RC-013": "a dining chair with a visibly loose rung, standing among "
           "other chairs with nobody having marked it for repair",
 "RC-014": "a full china cabinet of inherited place settings, far more "
           "than the table in front of it has ever been set for",
 "RC-015": "a folded tablecloth clearly too small for the dining table "
           "it's meant to cover, kept in the drawer anyway",
 "RC-016": "the dusty top of a tall china cabinet seen from below, well "
           "out of easy reach for a regular wipe",
 "RC-017": "a loose stack of mail on a sideboard that has clearly sat "
           "undisturbed long enough to look like it belongs there",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Dining Table": [
  "Run a fingernail down the leaf seam or extension joint and clear "
  "out any crumbs hiding in the gap.",
  "Wipe the underside lip and apron rail where hands grip to pull a "
  "chair in.",
  "Rock each chair once and flag any joint that has started to work "
  "loose.",
 ],
 "Buffet or Sideboard Surface": [
  "Lift the lamp and follow its cord the whole way to the outlet, "
  "checking for a cracked or chafed patch.",
  "Work any fresh wax drip off the wood with a plastic card before it "
  "hardens further.",
  "Dust behind each display object rather than around it.",
 ],
 "Buffet or Sideboard Storage": [
  "Smell one rolled tablecloth as you refold it, checking for a musty "
  "note that means it needs rewashing.",
  "Check the silver-plate serving pieces together for any spreading "
  "tarnish.",
  "Slide the drawer fully open and check it still runs flush on its "
  "runners.",
 ],
 "China or Display Cabinet": [
  "Dust the very top of the cabinet, high and out of sight, where "
  "this room's dust settles thickest.",
  "Check one glass shelf for a hairline crack or a bent support pin.",
  "Wipe the wall strap and its fixing point where the cabinet meets "
  "the wall.",
 ],
 "Beverage or Coffee Station": [
  "Lift the drip tray grate and check underneath it for mold before "
  "it spreads.",
  "Wipe the underside of the wall shelf above the kettle, where steam "
  "warps the board.",
  "Check the bean jar's fill line is still legible and matches what's "
  "actually in the jar.",
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
 {"id": "DRA-001", "zone": "Dining Table",
  "title": "CLEAR THE TABLE BY OWNER, NOT BY TYPE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the whole table onto the floor in one armful and sort "
          "what came off by the person it belongs to, so nothing stays "
          "homeless on a technicality.",
  "why": "A pile sorted by type just becomes three piles; sorting by "
         "owner means somebody actually carries it away.",
  "inputs": ["a basket for each person's things"],
  "steps": [
   "Clear the whole table onto the floor in one armful, then sort what "
   "came off by owner rather than by type. The homework, the unopened "
   "mail, and the half-finished craft project each go back to a "
   "person, not back to the table.",
   "Hand each pile to the person it belongs to, right now, rather than "
   "setting it back down anywhere else in the room.",
   "Wipe the bare table once everything is off it, then set the "
   "centerpiece back down alone."],
  "causes": ["KC-002", "KC-012"],
  "victory": "The table holds nothing but its centerpiece, and every "
             "activity that was on it has gone home with the person "
             "who owns it.",
  "next": "DRS-001",
  "art": "a dining table mid-clear with one basket holding homework and "
         "mail sitting on a chair beside it, the tabletop otherwise "
         "bare except the centerpiece going back down"},

 {"id": "DRA-002", "zone": "Dining Table",
  "title": "PHOTOGRAPH BOTH STATES AND TAPE THEM INSIDE THE DOOR",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Photograph the table both set for a meal and cleared to its "
          "standard, and tape both pictures inside the sideboard door "
          "so the standard isn't something anyone has to remember.",
  "why": "A standard living only in someone's head resets differently "
         "every night; a photo taped where people can see it resets "
         "the same way every time.",
  "inputs": ["a phone camera", "tape"],
  "steps": [
   "Set the table as if for a real meal and photograph it.",
   "Clear it to bare wood plus the centerpiece and photograph that "
   "too.",
   "Confirm the trivet and placemats live in the sideboard drawer "
   "nearest the table, not one further away, then tape both photos "
   "inside that door at eye level."],
  "causes": ["KC-008", "RC-013", "KC-003"],
  "victory": "Both photos are taped inside the sideboard door, and "
             "anyone in the house can point at them to say what "
             "'cleared' actually looks like.",
  "next": "DRA-001",
  "art": "a hand taping two photographs, one of a set table and one of "
         "a cleared table, to the inside of a sideboard door"},

 {"id": "DRA-003", "zone": "Buffet or Sideboard Surface",
  "title": "CLEAR THE WOOD AND GIVE EVERY PAPER A VERDICT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take everything off the sideboard's wood and give every "
          "piece of paper a real verdict tonight, so nothing sits "
          "there by default.",
  "why": "Paper left 'for now' is exactly how a serving surface turns "
         "into a filing cabinet.",
  "inputs": ["a recycling bin", "a folder for anything to file"],
  "steps": [
   "Take everything off the wood, including the picture frames and the "
   "candlesticks, and give every piece of paper a verdict tonight: act "
   "on it, file it, or recycle it. Burnt-down candle stubs, dried "
   "flowers, and chargers belonging to other rooms leave now.",
   "Return chargers and stray items to the room they actually belong "
   "to.",
   "Set only the lamp and the display group you're keeping back down "
   "at the far end."],
  "causes": ["KC-002", "RC-015"],
  "victory": "The wood is bare, every piece of paper has a verdict, "
             "and nothing that belongs to another room is still "
             "sitting here.",
  "next": "DRA-004",
  "art": "a sideboard cleared completely to bare wood with a small "
         "stack of mail sorted into an action pile, a file pile, and a "
         "recycling pile on the floor beside it"},

 {"id": "DRA-004", "zone": "Buffet or Sideboard Surface",
  "title": "TAPE THE SERVING RUN AND CAP THE DISPLAY AT THREE",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Mark the serving run with tape sized to your largest dish, "
          "and settle the display group at exactly three objects at "
          "the far end.",
  "why": "A run you can see is a run you'll actually keep clear; an "
         "unlimited display always grows until it swallows the space "
         "mail wants to claim.",
  "inputs": ["a large serving dish to measure with", "tape"],
  "steps": [
   "Set your largest serving dish where you'd really put it and mark "
   "that length with tape.",
   "Choose exactly three display objects for the far end and put "
   "everything else away or elsewhere.",
   "Pull the sideboard out and trace the lamp cord to the outlet so "
   "you can actually see what else shares that plug."],
  "causes": ["KC-008", "KC-001", "KC-005"],
  "victory": "The taped run stays bare, exactly three display objects "
             "sit at the far end, and you know what else shares the "
             "lamp's outlet.",
  "next": "DRA-003",
  "art": "a strip of tape marking a bare serving run at one end of a "
         "sideboard, exactly three display objects grouped at the far "
         "end beside a lamp"},

 {"id": "DRA-005", "zone": "Buffet or Sideboard Storage",
  "title": "LAY OUT EVERY LINEN AND CHECK EVERY SET",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull every tablecloth, runner, and napkin out and lay them "
          "across the table to see which sets are actually complete, "
          "so nothing partial keeps its drawer space.",
  "why": "A stained cloth or an orphaned napkin only reveals itself the "
         "night you actually need the full set.",
  "inputs": ["the dining table to lay things across", "a bin bag"],
  "steps": [
   "Pull every tablecloth, runner, and napkin out and lay them across "
   "the table so you can see which sets are actually complete. "
   "Partial napkin sets, cloths with stains you have already tried and "
   "failed to lift, and serving pieces orphaned from sets you no "
   "longer own are finished.",
   "Roll each surviving cloth with its matching napkins inside it "
   "before it goes back.",
   "Measure what's left against the table you actually own, including "
   "the leaf in."],
  "causes": ["RC-015", "RC-014"],
  "victory": "Every remaining linen set is complete, every serving "
             "piece belongs to a set you still own, and nothing "
             "carries a stain you've already failed to lift.",
  "next": "DRA-006",
  "art": "tablecloths, runners, and napkins spread across a dining "
         "table, one pile of complete matched sets and a smaller pile "
         "of stained or partial linens set apart"},

 {"id": "DRA-006", "zone": "Buffet or Sideboard Storage",
  "title": "MOVE THE HEAVY PIECES DOWN AND THE CANDLES UP",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Move the punch bowl and heavy platters to the lowest shelf, "
          "and move taper candles and matches into a latched drawer or "
          "high out of a child's reach.",
  "why": "Heavy stoneware overhead comes down while your hands are "
         "already full, and loose candles and matches in a low drawer "
         "are exactly at a small child's reach.",
  "inputs": ["a latch or a high shelf"],
  "steps": [
   "Move the punch bowl and heavy stoneware platters down to the "
   "bottom shelf.",
   "Move taper candles and matches into a latched drawer, or a shelf "
   "out of reach.",
   "Fit a divider and stand the large platters on edge behind it, so "
   "reaching one no longer means lifting the others off first."],
  "causes": ["KC-006", "KC-010", "KC-004"],
  "victory": "The heaviest pieces sit on the bottom shelf, candles and "
             "matches are latched or out of reach, and the platters "
             "stand on edge behind a divider.",
  "next": "DRA-005",
  "art": "a hand moving a heavy stoneware platter down onto a "
         "sideboard's bottom shelf, a latched drawer holding taper "
         "candles visible beside it"},

 {"id": "DRA-007", "zone": "China or Display Cabinet",
  "title": "SPLIT THE CHINA INTO THREE HONEST GROUPS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take every piece out and split it into complete sets, "
          "chipped or crazed pieces, and lone survivors, so nothing "
          "unsafe to drink from stays in rotation.",
  "why": "A chipped rim cannot be mended and is not safe to drink "
         "from, whatever the set it came from.",
  "inputs": ["a towel-lined table surface", "a box for pieces leaving"],
  "steps": [
   "Take every piece out and split it into three groups: complete "
   "sets, chipped or crazed pieces, and lone survivors of sets that "
   "are long gone. A chipped rim cannot be mended and is not safe to "
   "drink from, so that whole group leaves together.",
   "Hand-wash and dry each piece you're keeping before it goes back.",
   "Stack plates no more than eight high with felt between them as "
   "they return."],
  "causes": ["KC-007", "RC-017"],
  "victory": "What's left behind the glass is complete sets and pieces "
             "without a chip or crack, nothing kept only out of habit.",
  "next": "DRA-008",
  "art": "china laid out on a towel-covered table in three groups, one "
         "group of chipped pieces visibly set apart in a box"},

 {"id": "DRA-008", "zone": "China or Display Cabinet",
  "title": "STRAP THE CABINET AND PHOTOGRAPH THE SHELVES",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Strap the cabinet to a wall stud, and photograph the "
          "finished shelves to tape inside the door.",
  "why": "A tall glass-fronted case loaded with plates is this room's "
         "biggest tip-over risk, and a photo means a missing piece is "
         "found in December, not next December.",
  "inputs": ["a wall strap kit", "a stud finder", "a phone camera"],
  "steps": [
   "Find the stud and fit a wall strap between it and the cabinet.",
   "While you're up there, dust the top of the cabinet, high and out "
   "of easy sight, with a stool and a long-handled duster.",
   "Photograph the finished shelves and tape that photo inside the "
   "cabinet door."],
  "causes": ["KC-009", "RC-013", "RC-016"],
  "victory": "The cabinet is strapped to a wall stud, and a photo of "
             "the finished shelves is taped inside the door.",
  "next": "DRA-007",
  "art": "a wall strap fitted between the back of a tall china cabinet "
         "and a wall stud, a small photograph taped to the inside of "
         "the cabinet door"},

 {"id": "DRA-009", "zone": "Beverage or Coffee Station",
  "title": "CHECK EVERY DATE AND MATCH EVERY LID",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Check the date on every tea box, syrup bottle, and pod "
          "sleeve, and match every travel mug to its lid, so nothing "
          "past date or lidless keeps its spot.",
  "why": "A syrup you'll never use again and a mug with no lid are "
         "both taking up space the morning rush actually needs.",
  "inputs": ["a bin bag"],
  "steps": [
   "Line up every tea box, syrup bottle, and pod sleeve and check the "
   "dates, then open the travel mugs and match them to their lids. "
   "Anything past date, any mug missing its lid, and the promotional "
   "glassware you have never once poured into are out.",
   "Recycle or donate anything you kept only because it was a gift.",
   "Mark today's fill line on the bean jar with tape or a permanent "
   "marker."],
  "causes": ["KC-011", "RC-015"],
  "victory": "Everything on the counter is in date, every travel mug "
             "has its matching lid, and no glassware sits here unused.",
  "next": "DRA-010",
  "art": "tea boxes, syrup bottles, and travel mugs lined up on a "
         "counter, mugs matched to their lids, a bin bag beside "
         "expired items set apart"},

 {"id": "DRA-010", "zone": "Beverage or Coffee Station",
  "title": "GIVE THE MACHINE ITS OWN OUTLET AND LOCK UP THE BOTTLES",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Give the machine and kettle their own outlet, clear cords "
          "back from the edge, and move any wine or spirits behind a "
          "latch or high out of reach.",
  "why": "Water and electricity share this counter, and an open "
         "bottle at a child's eye level is a real hazard the kitchen "
         "version of this station wouldn't have.",
  "inputs": ["a latch or a high shelf", "cable clips"],
  "steps": [
   "Give the machine and the kettle their own outlet where possible.",
   "Clip cords back from the front edge where a sleeve can hook them.",
   "Move wine and spirits behind a latch or up out of a small child's "
   "reach."],
  "causes": ["KC-010", "KC-002"],
  "victory": "The machine and kettle have their own outlet, no cord "
             "sits at the front edge, and any alcohol is latched or "
             "out of reach.",
  "next": "DRA-009",
  "art": "a coffee machine and kettle each plugged into their own "
         "outlet on a counter, cords clipped back from the front edge, "
         "a latched cabinet visible below holding bottles"},

 {"id": "DRA-011", "zone": None,
  "title": "THE FULL DINING ROOM SAFETY WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking the chairs, the cabinet strap, the "
          "outlets, and anything within a small child's reach.",
  "why": "A wobbly chair, an unstrapped cabinet, and an open bottle of "
         "wine all hide until someone tests for them on purpose.",
  "inputs": ["a step stool"],
  "steps": [
   "Rock every chair to find a loose joint, and turn any that move to "
   "face the wall.",
   "Confirm the china cabinet is strapped to a wall stud.",
   "Confirm alcohol and candles are out of a small child's reach "
   "throughout the room."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No chair wobbles unmarked, the cabinet is strapped, and "
             "nothing hazardous sits within a small child's reach.",
  "next": "DRA-012",
  "art": "a hand rocking a dining chair to test its joints, a strapped "
         "china cabinet and a latched cabinet visible in the "
         "background"},

 {"id": "DRA-012", "zone": None,
  "title": "THE NIGHTLY CLEAR, ONE TRIP",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "When the plates go to the sink, carry out everything else "
          "on the table and the sideboard's bare run in the same trip.",
  "why": "Nothing in this room forces its own reset, so the only thing "
         "that works is tying it to a trip that was already happening.",
  "inputs": [],
  "steps": [
   "Carry the dishes to the sink.",
   "On the same trip, carry out anything that landed on the table or "
   "the sideboard's bare run that day.",
   "Notice whether the table matches its taped photo."],
  "causes": ["KC-009", "RC-013"],
  "victory": "The table and the sideboard's bare run match their "
             "standard before the kitchen light goes off.",
  "next": "DRA-013",
  "art": "a hand carrying a small stack of mail and a stray craft "
         "project away from a dining table in the same trip as dinner "
         "plates heading to the sink"},

 {"id": "DRA-013", "zone": None,
  "title": "THE MONTHLY LIMIT AND COUNT CHECK",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Once a month, check the sideboard's count card, the display "
          "limit, and the bean jar's fill line against what's actually "
          "there.",
  "why": "A limit written once and never revisited stops meaning "
         "anything the first time a good deal or a gift tempts you "
         "past it.",
  "inputs": ["a marker"],
  "steps": [
   "Compare the count card in the sideboard drawer against what's "
   "actually in it.",
   "Count the display objects on the sideboard surface; correct back "
   "to three if it's crept up.",
   "Check the bean jar's fill line is still legible and accurate."],
  "causes": ["KC-008", "KC-001"],
  "victory": "The count card matches the drawer, the display group is "
             "back to three, and the fill line still reads true.",
  "next": "DRA-011",
  "art": "a hand comparing a small card taped inside a sideboard door "
         "against tablecloths and serving pieces actually in the "
         "drawer"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a dining room, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("DRE-001", "THE UNEXPECTED DINNER GUEST",
  "A guest is staying for dinner tonight, unannounced, and the table "
  "has to seat one more person in the next ten minutes.",
  ["DRZ-001"],
  "The table clears to bare wood plus centerpiece in one trip, and an "
  "extra chair and place setting go down without hunting for anything.",
  "If clearing the table took more than one trip, or you had to search "
  "for a chair or a setting, the nightly clear slipped. Draw DRA-002.",
  "a dining table being reset for one more guest, an extra chair being "
  "pulled in and a place setting added quickly beside three already "
  "set"),
 ("DRE-002", "THE HOLIDAY SERVING RUSH",
  "Three serving dishes need to land on the sideboard at once, "
  "straight from the oven, with no time to move anything out of the "
  "way first.",
  ["DRZ-002"],
  "The taped run takes all three dishes without moving the display "
  "group first.",
  "If a display object had to move to fit a hot dish, the run isn't "
  "actually sized for your real serving load. Draw DRA-004.",
  "three hot serving dishes set down in a row along a bare taped run "
  "on a sideboard, three display objects undisturbed at the far end"),
 ("DRE-003", "THE TABLE THAT NEEDS SETTING FOR TWELVE",
  "A holiday meal for twelve is an hour away, and the good linens and "
  "serving pieces have to come out of storage complete and ready.",
  ["DRZ-003"],
  "The count card tells you exactly what's in the drawer before you "
  "open it, and every cloth, napkin, and serving piece pulled out is "
  "complete.",
  "If you had to hunt for a missing napkin or discover a stain "
  "mid-setup, the count card or the sort slipped. Draw DRA-005.",
  "linens and serving pieces being pulled from a sideboard drawer for "
  "a large table setting, a count card visible taped inside the open "
  "door"),
 ("DRE-004", "THE ACCIDENTAL KNOCK",
  "Someone bumps hard into the china cabinet while carrying a full "
  "tray, and it does not so much as rock.",
  ["DRZ-004"],
  "The cabinet stays put, strapped to its wall stud, and nothing "
  "inside shifts or falls.",
  "If the cabinet rocked or something shifted, the strap is missing "
  "or has failed. Draw DRA-008.",
  "a full serving tray passing close beside a tall, strapped china "
  "cabinet, the cabinet standing completely still against the wall"),
 ("DRE-005", "THE MORNING WITH A HOUSE FULL OF GUESTS",
  "Eight overnight guests all want coffee or tea in the same twenty "
  "minutes, with no time to hunt for a clean mug or discover the bean "
  "jar is empty.",
  ["DRZ-005"],
  "The tray has enough capped mugs, the bean jar is above its fill "
  "line, and everything runs left to right without anyone crossing "
  "into the kitchen.",
  "If the bean jar ran out or mugs ran short, the replenishment check "
  "slipped. Draw DRA-009.",
  "several mugs lined up on a single tray at a beverage station, a "
  "full bean jar above its marked fill line, guests' hands reaching "
  "for cups"),
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
        "related": {"standard": f"DRS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your dining "
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
    standard_id = (f"DRS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"DRS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "DRR-001", "title": "THE DINING ROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "ONE JOB. THE ONLY ROOM THAT CAN LOSE IT QUIETLY.",
        "objective": "The dining room has one job, and it is the only "
                     "room in the house that can quietly lose that job "
                     "without anyone noticing. This card is the map and "
                     "the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"DRZ-001 Dining Table. {start_tip['text']}"
            if start_tip else
            "DRZ-001 Dining Table. It is the quickest zone in the room "
            "and the only one whose result shows up at dinner the same "
            "evening."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your dining room. Put the rest back.",
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
        "safety_first": "Do DRA-011 The Full Dining Room Safety Walk "
                        "before any rebuild. It takes thirty minutes and "
                        "covers every chair, the cabinet strap, and "
                        "whether alcohol and candles are kept out of a "
                        "child's reach.",
        "related": {"contents": "DRZ-001 to DRZ-005, DRF-001 to DRF-015, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, DRA-001 to DRA-013, "
                                 "DRS-001 to DRS-005, DRE-001 to DRE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole dining "
                           "room in its settled state, the dining table, "
                           "a sideboard's serving surface and storage, a "
                           "china cabinet and a beverage station all "
                           "visible in one frame",
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
    return {"deck": "dining-room", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_hall_closet_deck.py,
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

    assert any(c["id"] == "DRA-011" for c in cards), "no safety walk card"
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
    print(f"  deck        dining-room ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
