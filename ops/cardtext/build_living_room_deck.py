#!/usr/bin/env python3
"""
Build the Living Room deck: 69 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
`content/manual/source/content.json`, the same corpus the zone pages already
read. This file follows `ops/cardtext/build_home_office_deck.py` and
`ops/cardtext/build_laundry_room_deck.py`, the two other six-zone rooms
already shipped this way. Purpose, done_looks_like, the standard, the
trigger, the first-15 action and its victory condition are quoted from the
Manual, not rewritten, and `gate()` at the bottom asserts they are still
character-for-character identical. The 18 frictions (three per zone) are
likewise derived straight from the Manual's own `diagnosis` layer, in zone
order, not retyped, so this deck cannot silently diverge from the
diagnostic engine already shipped on the six Living Room zone pages.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the nine new
action cards (the Manual gives one 15-minute reset per zone in `first_15`;
the 30-minute rebuild per zone and three whole-room actions are authored
here), the event cards, the micro quests, and the room card. The root
causes are not reauthored: they are the same frozen vocabulary in
`ops/root_causes.py` every other room deck already uses, so a household
owning more than one deck keeps one diagnosis pile rather than several
(DECK-GAME-DESIGN.md 4.3). This room's own diagnosis data reaches all
seventeen of the shared vocabulary's causes, confirmed against
content/manual/source/content.json before this file was written, not
assumed from any other room's count: six real, different zones (seating,
a shared surface, an electronics station, a display shelf, a personal
side table, and the floor itself) between them honestly cover the full
spread this business has diagnosed anywhere.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Living Room deck to disclose against: no free Living Room product exists on
the site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_living_room_deck.py
Out:  ops/cardtext/living-room-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "living-room-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Living Room"

# This room ships as a free typeset page, the same stage every prior room
# deck shipped at before any print-on-demand decision existed, so the
# budget here is the honest count of what this room's own corpus,
# diagnosis layer and a proportionate amount of new authorship produce: six
# real zones, all seventeen reachable root causes, two actions per zone plus
# three whole-room ones.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 17, "ACTION CARD": 15, "STANDARD CARD": 6,
          "EVENT CARD": 6}
TOTAL = sum(BUDGET.values())

# Same palette family as every prior room deck so a mixed pile of cards
# from any room still reads as one product line.
TYPE_COLOUR = {
    "ROOM CARD": "#2B2622", "ZONE CARD": "#2F5233",
    "FRICTION CARD": "#BC4B2A", "ROOT CAUSE CARD": "#6E5B8B",
    "ACTION CARD": "#3C5A6B", "STANDARD CARD": "#4E7A57",
    "EVENT CARD": "#8C5A2B",
}

# Every one of the 17 shared ids. Derived below from the Manual and
# asserted (in gate()) to be exactly this set: not a number chosen first
# and filled in. Confirmed against content/manual/source/content.json
# before this file was written: every one of the six zones' nine
# diagnosis branches (18 frictions x 3 branches) was read and its "cause"
# field copied here verbatim.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011", "KC-012",
             "RC-013", "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior room generator uses: every
# numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Sofa and Seating Zone": {
  "id": "LVZ-001", "order": 1, "difficulty": 2,
  "tagline": "EVERY SEAT SITTABLE. THROWS IN ONE BASKET. REMOTES IN ONE TRAY.",
  "callouts": [
   "Every seat cushion squared with nothing sitting on it",
   "Throws folded to one size, all in one basket at the end of the sofa",
   "At most one decorative cushion left per seat",
   "Both remotes standing in a tray on the near arm",
   "The recliner footrest fully lowered and clear",
   "Bare floor in front of the sofa, nothing tucked underneath",
  ],
  "art": ("a sofa and armchair with every seat clear and sittable, throws "
          "folded into one basket at the end of the sofa, one cushion "
          "per seat, and both remotes standing in a tray on the near "
          "arm"),
 },
 "Coffee Table": {
  "id": "LVZ-002", "order": 2, "difficulty": 1,
  "tagline": "ONE TRAY. FOUR COASTERS. THE WOOD SHOWING.",
  "callouts": [
   "One tray holding exactly four coasters",
   "The remote currently in use resting on the tray",
   "At most one book beside the tray",
   "At most one small plant beside the tray",
   "Bare wood or glass showing across most of the top",
   "No mug, cable, or piece of post anywhere on the surface",
  ],
  "art": ("a coffee table with one tray holding four coasters and a "
          "remote, a single book and a small plant beside it, bare wood "
          "showing across most of the surface"),
 },
 "Media Center": {
  "id": "LVZ-003", "order": 3, "difficulty": 3,
  "tagline": "EVERY CABLE LABELLED. ONE BIN FOR CONTROLLERS. CLEAR AIR ON "
             "THE VENTS.",
  "callouts": [
   "A cable bundle with a visible label at both ends",
   "One labeled power strip",
   "A hand's gap of clear air around the amplifier vents",
   "The same gap of clear air around the console vents",
   "One ventilated bin holding every controller and remote",
   "The television anchored to the wall or the unit",
  ],
  "art": ("a media console with a bundle of cables labeled at both ends "
          "running to one labeled power strip, a hand's gap of clear "
          "air around the amplifier and console vents, and one bin "
          "holding every controller and remote"),
 },
 "Bookshelves and Display": {
  "id": "LVZ-004", "order": 4, "difficulty": 2,
  "tagline": "A HAND'S WIDTH OF SPACE. A BOOKEND CLOSES EACH GROUP.",
  "callouts": [
   "A hand's width of empty shelf space at one end of a row",
   "Books standing upright between bookends",
   "Nothing stacked flat on top of the upright books",
   "Frames and objects gathered into two or three groups",
   "The unit visibly strapped to the wall",
   "Heavy or stone objects sitting on the lowest shelves",
  ],
  "art": ("a bookshelf unit strapped to the wall, books standing upright "
          "between bookends with a hand's width of empty space at one "
          "end of each shelf, frames and objects gathered into a few "
          "groups, heavy pieces on the lowest shelf"),
 },
 "Side Tables and Lighting": {
  "id": "LVZ-005", "order": 5, "difficulty": 2,
  "tagline": "FOUR ITEMS ON THE TRAY. THE CORD CLIPPED DOWN THE LEG.",
  "callouts": [
   "One small tray holding no more than four items",
   "A coaster sitting under a glass",
   "A lit, clean lamp bulb",
   "The lamp cord clipped down the table leg",
   "No cable crossing the floor toward the chair",
   "The tabletop otherwise bare",
  ],
  "art": ("a side table with a small tray holding four items including "
          "a coastered glass, a lit clean lamp with its cord clipped "
          "down the table leg, no cable crossing the floor"),
 },
 "Floor and Circulation Path": {
  "id": "LVZ-006", "order": 6, "difficulty": 2,
  "tagline": "FULL WIDTH, DOOR TO DOOR. NOTHING ON THE FLOOR BUT THE RUG.",
  "callouts": [
   "A continuous clear route from doorway to doorway",
   "The route wide enough for two people to pass",
   "Rug edges lying flat on a grippy pad",
   "No cord crossing the route",
   "Baskets pushed back against the wall, out of the route",
   "Nothing on the floor but furniture legs and the rug",
  ],
  "art": ("a living room floor with a continuous clear route from one "
          "doorway to another, rug edges lying flat on a grippy pad, no "
          "cord crossing the path, baskets pushed back against the "
          "wall"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine already
# shipped on the six Living Room zone pages. Three per zone, matching that
# data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Sofa and Seating Zone", "LVF-001", "THE LAUNDRY THAT LANDED ON THE SOFA",
  "a sofa cushion with a small pile of folded laundry and a magazine "
  "sitting on the seat, a second throw blanket bunched at the far end"),
 ("Sofa and Seating Zone", "LVF-002", "THE REMOTE DOWN THE CUSHION SEAM",
  "a hand reaching down into a sofa cushion seam searching for a remote, "
  "an empty tray sitting near the television at the far end of the "
  "room"),
 ("Sofa and Seating Zone", "LVF-003",
  "THE FOOTREST NOBODY CHECKS BEFORE CLOSING",
  "a recliner footrest partly lowered with a throw blanket draped over "
  "the arm covering the release lever, a small child's toy sitting on "
  "the floor just in front of it"),

 ("Coffee Table", "LVF-004", "THE COASTERS IN THE FAR CORNER",
  "a coffee table with a ring mark left by a mug set directly on the "
  "wood, four coasters sitting untouched in the corner of the tray "
  "furthest from the seats"),
 ("Coffee Table", "LVF-005",
  "THE MAGAZINES UNDER THE ONE BOOK YOU'RE READING",
  "a stack of old magazines and takeaway menus on a coffee table with a "
  "single bookmarked book sitting on top of the pile"),
 ("Coffee Table", "LVF-006", "THE CANDLE TOO CLOSE TO THE MAGAZINE PILE",
  "a lit candle burned close to its rim sitting on a coffee table right "
  "beside a stack of magazines and a folded throw blanket"),

 ("Media Center", "LVF-007", "THE CABLE NOBODY CAN NAME",
  "a tangled coil of cables behind a television unit, one cable clearly "
  "unplugged at both ends and coiled loose among the rest"),
 ("Media Center", "LVF-008", "THE CONTROLLER BEHIND THE UNIT AGAIN",
  "a game controller wedged in the gap behind a media unit, a second "
  "remote sitting loose on top of the console instead of in a bin"),
 ("Media Center", "LVF-009", "THE DUST PACKED BEHIND THE VENTS",
  "a thick layer of dust visible across the back vents of an amplifier "
  "and a television console, seen from behind the pulled-out unit"),

 ("Bookshelves and Display", "LVF-010",
  "THE MANUAL FOR AN APPLIANCE YOU DON'T OWN",
  "a bookshelf with a duplicate paperback, an old appliance instruction "
  "manual, and a water-stained book standing together among the other "
  "titles"),
 ("Bookshelves and Display", "LVF-011", "SCANNING EVERY SPINE FOR ONE BOOK",
  "a hand scanning a packed row of book spines arranged by color "
  "rather than subject, no bookend or divider breaking up the row"),
 ("Bookshelves and Display", "LVF-012",
  "THE BOOKCASE THAT'S NEVER BEEN STRAPPED DOWN",
  "a tall bookcase standing away from the wall with no visible strap or "
  "bracket, its lower shelves at the climbing height of a small child"),

 ("Side Tables and Lighting", "LVF-013",
  "THE DISH OF THINGS NOBODY'S TOUCHED IN MONTHS",
  "a small dish beside an armchair holding loose coins, a dried-out "
  "pen, and a phone charger with no matching phone anywhere in sight"),
 ("Side Tables and Lighting", "LVF-014", "THE TABLETS WITHIN A CHILD'S REACH",
  "an open dish holding loose tablets sitting on a side table at the "
  "exact height a small child standing beside the chair would reach"),
 ("Side Tables and Lighting", "LVF-015", "THE CORD CROSSING THE WALKED LINE",
  "a lamp cord and a phone charger cord both running loose across a "
  "floor between an armchair and a doorway, neither clipped to the "
  "table leg"),

 ("Floor and Circulation Path", "LVF-016",
  "THE BOX THAT'S SAT BESIDE THE SOFA FOR WEEKS",
  "a cardboard box sitting on the floor beside a sofa alongside a pair "
  "of shoes and a school bag, all three clearly settled in rather than "
  "just dropped"),
 ("Floor and Circulation Path", "LVF-017",
  "TURNING SIDEWAYS TO CARRY THE LAUNDRY BASKET THROUGH",
  "a person carrying a full laundry basket sideways through a narrow "
  "gap between a sofa and a side table, barely clearing both"),
 ("Floor and Circulation Path", "LVF-018",
  "THE RUG CORNER EVERYONE STEPS AROUND",
  "a curled-up rug corner on a living room floor with a lamp cord "
  "crossing directly over the walked route beside it"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, living-room-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use, so this deck composes with every other room
# deck rather than forking its own copy (DECK-GAME-DESIGN.md 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a media console with a tangle of extra cables coiled behind "
           "it, far more than the two devices sitting on the shelf "
           "could ever need",
 "KC-002": "a stray phone charger cord lying loose across a living room "
           "floor with no clip or tray anywhere near it",
 "KC-003": "a television remote sitting on a shelf across the room, out "
           "of reach of the sofa it controls",
 "KC-004": "a hand reaching down into a sofa cushion seam, feeling for "
           "something instead of finding it in a tray",
 "KC-005": "a section of bookshelf with book spines packed so tightly "
           "together that no single title stands out from the row",
 "KC-006": "a media unit pulled slightly from the wall, revealing a "
           "narrow gap behind it that a hand can barely fit into",
 "KC-007": "a living room floor with a narrow walking gap left between "
           "two pieces of furniture standing close together",
 "KC-008": "a coffee table with no tray or marked boundary anywhere to "
           "show where clutter is allowed to sit",
 "KC-009": "an unlit candle burned close to its rim on a coffee table "
           "with no clock or calendar anywhere nearby marking when it "
           "was last checked",
 "KC-010": "an open dish of loose tablets sitting on a low side table "
           "at the height of a small child standing beside a chair",
 "KC-011": "a television remote lying still on a shelf, its battery "
           "compartment door slightly open",
 "KC-012": "two game controllers left in two different spots on the "
           "same media console, neither in a shared bin",
 "RC-013": "a curled rug corner on a living room floor with nobody "
           "nearby and no mark showing whose job it is to fix it",
 "RC-014": "a shelf of inherited books and framed photographs crowding "
           "out the working reference titles beside them",
 "RC-015": "a small stack of old magazines sitting on a coffee table "
           "beside a single bookmarked book",
 "RC-016": "a hand reaching behind a media console into a narrow, "
           "dusty gap tight against the wall",
 "RC-017": "a room with a folded throw draped over a sofa arm and a box "
           "sitting on the floor beside it, both clearly long settled "
           "in",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded
# in that zone's own Manual passes, the same contract every prior room
# generator's MICRO_QUESTS already meets (DECK-GAME-DESIGN.md section 2).
# Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Sofa and Seating Zone": [
  "Lift each seat cushion and check the seam for coins, crumbs, or a "
  "stray remote before you vacuum, not after.",
  "Rotate and flip the seat cushions so the one nobody chooses takes "
  "its turn at the wear.",
  "Slowly lower the recliner footrest once, watching the floor the "
  "whole way down, and teach one other person to do the same.",
 ],
 "Coffee Table": [
  "Lift the tray and wipe the ring marks hiding underneath it, then "
  "dry the top with a second pass.",
  "Check the underside edge and the lower shelf for dust nobody sees "
  "at eye level.",
  "Confirm the candle has a hand's width of clear space on every side "
  "before you light it tonight.",
 ],
 "Media Center": [
  "Wipe the television screen with a dry microfiber cloth only, never "
  "a spray, working corner to corner.",
  "Follow one cable from the strip to its device and confirm the label "
  "at both ends still matches.",
  "Check the television is still anchored to the wall or the unit by "
  "giving the top edge a gentle push.",
 ],
 "Bookshelves and Display": [
  "Run a finger along the top edge of one row of books, not just the "
  "shelf board, and wipe what it picks up.",
  "Give the bookcase a gentle push partway up and confirm it does not "
  "rock or lean from the wall.",
  "Pick one book you have not opened this year and decide, out loud, "
  "whether it is reference or display.",
 ],
 "Side Tables and Lighting": [
  "Wipe the bulb and the inside of the shade while the lamp is off and "
  "cool.",
  "Count the items on one tray; if it is more than four, carry the "
  "extra one out right now.",
  "Follow the lamp cord from the base to the outlet and confirm it "
  "never crosses the walked path.",
 ],
 "Floor and Circulation Path": [
  "Press the rug's gripper pad at one corner and confirm it still "
  "holds the rug flat against the floor.",
  "Walk the full route once carrying something in both hands, and note "
  "the first spot that narrows.",
  "Check under the sofa and chair legs with the vacuum's crevice tool, "
  "where pet hair collects unseen.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-room actions, the same shape every prior room deck's whole-room
# cards keep: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "LVA-001", "zone": "Sofa and Seating Zone",
  "title": "CLEAR EVERY SEAT AND SORT BY WHERE IT GOES", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull everything off the seats and dig the seams out, sorting "
          "what comes off into leaves-the-room, goes-in-the-wash, and "
          "lives-here.",
  "why": "Laundry and stray paper never announce themselves as clutter "
         "here, they just read as warmth, so the sofa only clears when "
         "someone actually sorts by where each thing goes.",
  "inputs": ["a basket for lives-here items", "a laundry hamper"],
  "steps": [
   "Pull everything off the seats and dig the seams out: the laundry "
   "that migrated here, the second and third throw blanket, the "
   "magazines wedged behind the armrest, the coins and hair ties down "
   "the back. Sort into leaves-the-room, goes-in-the-wash, and "
   "lives-here.",
   "Carry the wash pile to the hamper and the leaves-the-room pile to "
   "its actual room, right now.",
   "Fold the throws to one size and set them in the basket at the end "
   "of the sofa."],
  "causes": ["KC-002", "RC-017"],
  "victory": "Every seat is sittable without moving anything, and the "
             "throws are folded in one basket.",
  "next": "LVS-001",
  "art": "a sofa with every cushion squared and sittable, folded throws "
         "sitting in a basket at the end, a small labeled laundry "
         "basket standing just outside the room"},

 {"id": "LVA-002", "zone": "Sofa and Seating Zone",
  "title": "MOVE THE REMOTE TRAY AND WRITE THE BASKET RULE",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Move the remote tray to the arm people actually reach from "
          "while sitting, and write the basket's own rule where it can "
          "be read.",
  "why": "A tray near the television instead of near the seat gets "
         "skipped every time, and a rule nobody wrote down is a "
         "preference the last person out has to guess at.",
  "inputs": ["a small tray", "a label or tag", "a marker"],
  "steps": [
   "Move the remote tray onto the arm nearest the seat people actually "
   "sit in, not the arm nearest the television.",
   "Write the standard on a tag and tie it to the throw basket: throws "
   "folded in, nothing stored on a seat.",
   "Say out loud who the nightly square-up belongs to: whoever turns "
   "the lamp off, every night, not the same person twice in a row."],
  "causes": ["KC-003", "KC-008", "RC-013"],
  "victory": "The remote tray sits on the arm people actually reach "
             "from, and the basket carries a written rule naming what "
             "belongs in it.",
  "next": "LVA-001",
  "art": "a remote tray sitting on the near arm of a sofa within easy "
         "reach of the seat, a small tag tied to a folded-throw basket "
         "beside it"},

 {"id": "LVA-003", "zone": "Coffee Table",
  "title": "CLEAR THE TOP TO WHAT YOU USED IN TWO DAYS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the whole coffee table top onto the floor and put back "
          "only what somebody used in the last two days.",
  "why": "A magazine or a burned-down candle stub never looks urgent on "
         "its own, so the only test that actually clears this table is "
         "judging the whole top at once.",
  "inputs": ["a recycling bin"],
  "steps": [
   "Clear the whole top onto the floor and put back only what somebody "
   "used in the last two days. The candle burned down to the foil, the "
   "coasters nobody uses because they sit on the far corner, the "
   "three-month-old magazines and the takeaway menus all go now.",
   "Recycle the paper pile and return the tray to its spot within reach "
   "of the sofa.",
   "Set back only the four coasters, the remote in use, and at most one "
   "book or plant."],
  "causes": ["RC-017", "RC-015"],
  "victory": "The table holds four coasters, the remote in use, and at "
             "most one book or plant, nothing else.",
  "next": "LVS-002",
  "art": "a coffee table cleared to a tray with four coasters, a remote, "
         "and a single book, a small pile of recycled magazines and "
         "menus set aside on the floor"},

 {"id": "LVA-004", "zone": "Coffee Table",
  "title": "SET THE FOUR-COASTER TRAY AND MOVE THE CANDLE", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Set the tray within reach of the sofa with exactly four "
          "coasters on it, and give the candle a hand's width of clear "
          "space on every side.",
  "why": "A coaster you have to lean across the table for gets skipped, "
         "and a candle surrounded by throws and magazines is the wrong "
         "neighborhood for an open flame.",
  "inputs": ["four coasters", "the tray", "a heatproof mat for the "
             "candle"],
  "steps": [
   "Set the tray on the side of the table nearest the sofa, with the "
   "four coasters sitting on it within an arm's reach of every seat.",
   "Move the candle onto its own mat with a clear hand's width of "
   "space on every side, away from the magazine pile.",
   "Agree the rule out loud: if it does not fit on the tray, it does "
   "not live on the table."],
  "causes": ["KC-004", "KC-010", "KC-009"],
  "victory": "Four coasters sit on the tray within reach of the sofa, "
             "and the candle burns with nothing flammable within a "
             "hand's reach.",
  "next": "LVA-003",
  "art": "a coffee table tray holding four coasters within arm's reach "
         "of a sofa, a candle sitting alone on its own mat with clear "
         "space on every side"},

 {"id": "LVA-005", "zone": "Media Center",
  "title": "NAME EVERY CABLE AND DECIDE ITS DISCS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Unplug and lay out every cable, name the device each one "
          "serves, and give every disc and game one decision.",
  "why": "A cable that cannot be named out loud is almost always "
         "feeding a device the house no longer owns, and it only leaves "
         "once someone actually asks.",
  "inputs": ["a bag for electronics recycling"],
  "steps": [
   "Unplug and lay out every cable, then name the device each one "
   "serves. The composite leads, the disc player nobody has loaded in "
   "a year, the streaming stick from two televisions ago and the "
   "charger with the old connector all leave. Discs and games get one "
   "decision each: sell, lend, or recycle.",
   "Bag anything leaving for electronics recycling.",
   "Reconnect only the cables that named a real device still in the "
   "room."],
  "causes": ["KC-001", "KC-008"],
  "victory": "Every remaining cable is labeled at both ends and runs "
             "to a device you can name.",
  "next": "LVS-003",
  "art": "a media unit with every cable laid out and reconnected only "
         "to devices still in use, a small bag of old leads and an "
         "unused disc player set aside for recycling"},

 {"id": "LVA-006", "zone": "Media Center",
  "title": "LABEL THE STRIP, BIN THE CONTROLLERS, CLEAR THE VENTS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Label the power strip to match every cable, move the "
          "controller bin to a reachable height, and clear the dust "
          "packed behind the vents.",
  "why": "Heat and power are the two hazards behind this unit, and a "
         "controller that slides behind it every time is a location "
         "problem, not a habit problem.",
  "inputs": ["labels or tape", "a marker", "a ventilated bin",
             "a vacuum with a crevice attachment"],
  "steps": [
   "Label each outlet on the power strip to match the cable plugged "
   "into it.",
   "Move the controller and remote bin down to the height of whoever "
   "actually plays, not on top of the unit where things slide off the "
   "back.",
   "Vacuum the dust off the console and amplifier vents and the back "
   "panel of the television, and confirm a hand's gap of clear air "
   "around both.",
   "Check the television is anchored to the wall or the unit."],
  "causes": ["KC-006", "RC-016", "KC-011", "KC-012"],
  "victory": "The power strip and every cable share a label, the "
             "controllers live in one bin at a reachable height, and a "
             "hand's gap of air surrounds the vents.",
  "next": "LVA-005",
  "art": "a media console with a labeled power strip, one ventilated "
         "bin holding every controller at a reachable height, and clear "
         "air visible around the amplifier vents"},

 {"id": "LVA-007", "zone": "Bookshelves and Display",
  "title": "TAKE ONE SHELF DOWN AT A TIME", "minutes": 15, "players": "1",
  "six_s": "Sort", "from_first_15": True,
  "goal": "Take one shelf down at a time so every book and object "
          "passes through your hands and gets a real decision.",
  "why": "A duplicate book or a dead plant never looks wrong sitting "
         "next to a hundred others, so the only way to actually see it "
         "is to take the whole shelf down and judge each piece alone.",
  "inputs": ["a box for books leaving the house"],
  "steps": [
   "Take one shelf down at a time so every book passes through your "
   "hands. Duplicates, the manuals for appliances you replaced, the "
   "free paperbacks from a conference and anything water-damaged go "
   "now. Empty frames, the dead plant and the souvenirs you stopped "
   "seeing years ago go with them.",
   "Box anything leaving for donation or resale.",
   "Wipe the shelf board before anything goes back onto it."],
  "causes": ["RC-017", "RC-014"],
  "victory": "Every shelf keeps a hand's width of empty space at one "
             "end, and nothing is stacked flat on top of the upright "
             "books.",
  "next": "LVS-004",
  "art": "a bookshelf with one shelf's contents laid out on the floor "
         "sorted into keep and leaving piles, a small box packed for "
         "donation nearby"},

 {"id": "LVA-008", "zone": "Bookshelves and Display",
  "title": "STRAP THE BOOKCASE AND GROUP BY SUBJECT", "minutes": 30,
  "players": "1 to 2", "six_s": "Safety",
  "goal": "Strap the bookcase to a wall stud, then regroup the books by "
          "subject with a bookend closing every group.",
  "why": "A tall bookcase loaded high is a tip-over risk the moment a "
         "child uses the shelves as a ladder, and a shelf grouped by "
         "color makes every search take longer than it should.",
  "inputs": ["a wall strap kit", "a stud finder", "bookends"],
  "steps": [
   "Find the stud and fit a wall strap between it and the bookcase.",
   "Regroup the books by subject, heaviest and stone objects on the "
   "bottom two shelves, and close each group with a bookend.",
   "Leave a hand's width of empty shelf at the end of every row."],
  "causes": ["KC-009", "RC-013", "KC-003", "KC-005"],
  "victory": "The bookcase is strapped to a wall stud, and every group "
             "of books sits behind its own bookend with a hand's width "
             "of space at the end.",
  "next": "LVA-007",
  "art": "a bookcase strapped to a wall stud, books regrouped by "
         "subject with a bookend closing each group, heavy objects "
         "sitting on the bottom two shelves"},

 {"id": "LVA-009", "zone": "Side Tables and Lighting",
  "title": "EMPTY THE DISH AND GIVE EVERYTHING A VERDICT", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the little dish and the drawer onto the seat of the "
          "chair, and give every small thing a real verdict.",
  "why": "A dish of odds and ends only grows because nobody ever judges "
         "the whole dish at once; one piece at a time it always looks "
         "too small to bother with.",
  "inputs": ["a small tray"],
  "steps": [
   "Empty the little dish and the drawer onto the seat of the chair. "
   "The reading glasses with the wrong prescription, the dried-out "
   "pens, the foreign coins, the loose tablets, the charger for a phone "
   "nobody in the house owns and the coasters that never made it back "
   "to the coffee table each get a verdict now.",
   "Return the coasters to the coffee table and the charger to whoever "
   "owns the matching phone, or recycle it.",
   "Set only the tray back down, holding no more than four items."],
  "causes": ["RC-013", "RC-015"],
  "victory": "Each table's tray holds at most four items, and nothing "
             "swallowable sits uncapped.",
  "next": "LVS-005",
  "art": "a side table tray holding four items, a small pile of coins "
         "and an orphaned charger set aside on a chair seat nearby"},

 {"id": "LVA-010", "zone": "Side Tables and Lighting",
  "title": "LID THE TABLETS AND CLIP THE CORDS DOWN", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Move loose tablets into a lidded case and clip both the lamp "
          "cord and the charger cord down the table leg.",
  "why": "An open dish of tablets sits at exactly a small child's reach "
         "height, and a cord crossing the walked line between the chair "
         "and the door is a trip nobody sees until it happens.",
  "inputs": ["a lidded pill case", "cable clips"],
  "steps": [
   "Move any loose tablets into a lidded case and put the case away in "
   "a cupboard, not back on the open tray.",
   "Clip the lamp cord and the phone charger cord down the table leg so "
   "neither crosses the floor toward the chair.",
   "Confirm the tray holds four items or fewer once both cords are "
   "clipped down."],
  "causes": ["KC-010", "KC-004", "KC-002", "KC-009"],
  "victory": "The dish holds no loose medicine, both cords are clipped "
             "to the table leg, and the tray holds four items or "
             "fewer.",
  "next": "LVA-009",
  "art": "a side table with a lidded pill case standing beside a chair, "
         "a lamp cord clipped neatly down the table leg with no cable "
         "crossing the floor"},

 {"id": "LVA-011", "zone": "Floor and Circulation Path",
  "title": "WALK THE ROUTE WITH A BASKET IN HAND", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Walk the whole route with a laundry basket and put every "
          "floor item into it, carrying anything from another room "
          "there first.",
  "why": "A box or a pair of shoes never looks like it is blocking "
         "anything on its own; walking the whole route with a basket is "
         "what actually reveals the floor's real job.",
  "inputs": ["a laundry basket"],
  "steps": [
   "Walk the route with a laundry basket and put every floor item in "
   "it: shoes, toys, yesterday's bag, the pile of post, the box that "
   "has sat beside the sofa for a month. Anything belonging to another "
   "room gets carried there before you let yourself sit down.",
   "Return each item to its real room on the same trip.",
   "Push any remaining basket back against the wall, clear of the "
   "route."],
  "causes": ["KC-002", "RC-015"],
  "victory": "The route from door to door is clear at full width, with "
             "nothing on the floor but furniture legs and the rug.",
  "next": "LVS-006",
  "art": "a living room floor cleared to a wide open route, a laundry "
         "basket sitting empty by the door after its trip round the "
         "room"},

 {"id": "LVA-012", "zone": "Floor and Circulation Path",
  "title": "WALK THE ROUTE WITH A FULL BASKET AND FIX THE RUG",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Walk the route carrying a full basket in both hands, fit a "
          "grippy pad under the curled rug corner, and clip down any "
          "crossing cord.",
  "why": "A route checked from the doorway always looks wider than it "
         "actually is; carrying something through it is the only test "
         "that tells the truth.",
  "inputs": ["a grippy rug pad", "cable clips", "a full laundry basket "
             "to test with"],
  "steps": [
   "Walk the route carrying a full basket in both hands and note the "
   "first spot that makes you turn sideways.",
   "Fit a grippy pad under the curled rug corner so it lies flat, and "
   "clip down any cord that crosses the route.",
   "If the route still fails the basket test, name the one piece of "
   "furniture that has to move or go."],
  "causes": ["KC-007", "KC-008", "RC-017", "RC-013", "KC-010"],
  "victory": "You can carry a full basket through the route without "
             "turning sideways, and no cord or rug edge crosses it.",
  "next": "LVA-011",
  "art": "a person carrying a full laundry basket easily through a wide "
         "clear route, a rug lying flat against a grippy pad beside "
         "them"},

 {"id": "LVA-013", "zone": None,
  "title": "FOLLOW ONE STRAY OBJECT ALL THE WAY HOME", "minutes": 30,
  "players": "1", "six_s": "Straighten",
  "goal": "Pick one real object currently out of place in this room and "
          "carry it through every decision until it has a real home.",
  "why": "This room belongs to everybody, which is exactly why nothing "
         "in it has an obvious owner; following one object all the way "
         "through shows where the whole system actually stalls.",
  "inputs": ["one real object currently out of place"],
  "steps": [
   "Pick up one object that is genuinely out of place in the room right "
   "now.",
   "Decide, out loud, where it actually lives: this room, another room, "
   "or nowhere anymore.",
   "Carry it there, on this trip, not later.",
   "Note which zone, if any, slowed the object down on its way: that "
   "zone is today's real job."],
  "causes": ["KC-002", "RC-015"],
  "victory": "The one object reaches its real home, and you can name "
             "which zone, if any, slowed it down.",
  "next": "LVA-014",
  "art": "a single object, a stray toy, being carried from a living "
         "room floor directly through a doorway toward the room it "
         "actually belongs in, no other clutter visible along the way"},

 {"id": "LVA-014", "zone": None, "title": "THE ONE-PERSON-ONE-OBJECT SWEEP",
  "minutes": 15, "players": "1 to 6", "six_s": "Sort",
  "goal": "Everyone in the house carries out exactly the one thing they "
          "personally left behind in this room, right now.",
  "why": "This room fails by donation, not by neglect: each person "
         "drops one thing and considers the room fine, so no single "
         "person ever sees the mess they caused alone.",
  "inputs": ["nothing beyond fifteen minutes and every person in the "
             "house"],
  "steps": [
   "Everyone in the house stands in the living room for one minute.",
   "Each person names, out loud, the one thing in the room that is "
   "theirs.",
   "Each person carries their own one thing out, at the same time.",
   "Whatever is left afterward belongs to nobody currently in the "
   "house and gets a decision on the spot."],
  "causes": ["KC-001", "RC-017"],
  "victory": "Every object left in the room belongs to whoever is in it "
             "right now, not to someone who left ten minutes ago.",
  "next": "LVA-015",
  "art": "several people each carrying one object out of a living room "
         "at the same time through different doorways, the room behind "
         "them left holding only shared furniture"},

 {"id": "LVA-015", "zone": None,
  "title": "THE QUARTERLY BEHIND-THE-FURNITURE SAFETY WALK",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Walk the whole room checking the anchors, the hinges, the "
          "outlets behind the media unit, and the walked route, in one "
          "pass.",
  "why": "An unstrapped bookcase, a recliner hinge, a crowded outlet and "
         "a curled rug corner all hide until someone checks for them on "
         "purpose, and this room hides more of them than any other.",
  "inputs": ["nothing beyond thirty minutes and a working set of "
             "hands"],
  "steps": [
   "Give the television and the bookcase a firm push and confirm "
   "neither rocks or leans away from the wall.",
   "Lower the recliner footrest and the sofa bed hinge slowly once, "
   "watching the floor the whole way down.",
   "Check every outlet behind the media unit for a frayed cable or one "
   "power strip chained into another.",
   "Walk the full route to every door checking for a curled rug edge, "
   "a crossing cord, or anything left on the floor."],
  "causes": ["RC-016", "KC-010", "KC-006"],
  "victory": "You can name, out loud, that the anchors, the hinges, the "
             "outlets and the walked route have each been checked "
             "today.",
  "next": "LVA-001",
  "art": "a hand checking a bookcase's wall strap, a recliner footrest "
         "being lowered slowly, and a media unit's outlets being "
         "inspected, all in the same room"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a living room, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("LVE-001", "THE MOVIE NIGHT WITH EIGHT PEOPLE",
  "Eight people are coming over for a movie tonight, and every seat "
  "needs to be sittable the moment they walk in.",
  ["LVZ-001"],
  "Every seat clears in one pass, with nothing to lift off a cushion "
  "before anyone sits down.",
  "If clearing the seats took more than one basket trip, the nightly "
  "reset slipped. Draw LVA-001 or LVA-002.",
  "a sofa and armchairs all cleared and ready for guests, a basket of "
  "folded throws sitting at the end of the sofa, remotes visible in "
  "their tray"),
 ("LVE-002", "THE SURPRISE VISITOR",
  "A neighbor knocks and is in the living room in under a minute, with "
  "no time to clear the coffee table first.",
  ["LVZ-002"],
  "The table already shows bare wood, four coasters, and nothing that "
  "needs explaining.",
  "If you had to sweep something out of sight before they sat down, the "
  "tray rule slipped. Draw LVA-003 or LVA-004.",
  "a coffee table already holding just a tray with four coasters and "
  "one book, bare wood visible around it, a doorbell visible in the "
  "background"),
 ("LVE-003", "THE NEW CONSOLE ARRIVES",
  "A new game console arrives today and needs plugging in, right in the "
  "middle of a unit already crowded with cables.",
  ["LVZ-003"],
  "The new cable gets labeled at both ends the moment it is plugged "
  "in, and it is obvious which outlet on the strip is free.",
  "If the new cable went in unlabeled, or you could not tell which "
  "outlet was free, the standard slipped the moment it was tested. "
  "Draw LVA-005 or LVA-006.",
  "a hand plugging in a new console cable at a labeled power strip, a "
  "marker resting nearby, the rest of the bundle already labeled at "
  "both ends"),
 ("LVE-004", "THE SCHOOL PROJECT RESEARCH NIGHT",
  "A child needs three reference books from this shelf for a project "
  "due tomorrow, and needs to find them alone.",
  ["LVZ-004"],
  "The right books sit grouped by subject at a reachable height, found "
  "without pulling down half the shelf.",
  "If a book had to be hunted for across the whole shelf, the grouping "
  "slipped. Draw LVA-007 or LVA-008.",
  "a child's hand pulling a reference book from a shelf grouped clearly "
  "by subject with a bookend closing the group"),
 ("LVE-005", "THE OVERNIGHT GUEST WITH A TODDLER",
  "A guest is staying over with a toddler, and every side table in the "
  "room needs to be safe at a small child's reach height by bedtime.",
  ["LVZ-005"],
  "No dish holds loose tablets, no cord crosses the floor, and every "
  "tray sits at four items or fewer.",
  "If a loose tablet or a trailing cord turned up during the safety "
  "walk, the side table standard slipped. Draw LVA-009 or LVA-010.",
  "a side table with a lidded pill case instead of an open dish, a lamp "
  "cord clipped neatly down the table leg, a toddler playing safely "
  "nearby on the floor"),
 ("LVE-006", "THE 2 A.M. FIRE ALARM",
  "The smoke alarm goes off at 2 a.m. and everyone has to get from the "
  "sofa to the front door in the dark, fast.",
  ["LVZ-006"],
  "The route is clear at full width the whole way, with no rug edge, "
  "cord, or toy to catch a foot.",
  "If anyone stumbled on the way out, the floor standard slipped, and "
  "it slipped somewhere specific. Draw LVA-011 or LVA-012.",
  "a dark living room floor with a clear wide route from a sofa to a "
  "front door, no obstruction visible along the path"),
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
        "related": {"standard": f"LVS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your living "
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
    standard_id = (f"LVS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"LVS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "LVR-001", "title": "THE LIVING ROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. EVERYBODY'S ROOM, NOBODY'S JOB YET.",
        "objective": "The living room belongs to everybody, which is "
                     "why nobody puts anything away in it by default. "
                     "This card is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"LVZ-006 Floor and Circulation Path. {start_tip['text']}"
            if start_tip else
            "LVZ-006 Floor and Circulation Path. Walk it with a laundry "
            "basket first, and you get an honest look at how much of "
            "this room's mess is just visiting from another room."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your living room. Put the rest back.",
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
        "players": "1 to 6. With more than one, give each person the "
                   "zone that annoys them most; this is the one room "
                   "every person in the house actually uses.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do LVA-015 The Quarterly Behind-the-Furniture "
                        "Safety Walk before any rebuild. It takes thirty "
                        "minutes and covers the anchors, the hinges, "
                        "the outlets and the walked route.",
        "related": {"contents": "LVZ-001 to LVZ-006, LVF-001 to "
                                 "LVF-018, the shared root causes in "
                                 "ops/root_causes.py, LVA-001 to "
                                 "LVA-015, LVS-001 to LVS-006, LVE-001 "
                                 "to LVE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "living room in its settled state, a sofa "
                           "and coffee table, a media center, a "
                           "bookshelf, a side table with a lamp, and a "
                           "clear floor route all visible in one frame",
                "must_show": ["all six zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the six zones is. If one is "
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
    return {"deck": "living-room", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (build_home_office_deck.py,
    build_laundry_room_deck.py)."""
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
                    f"{c['id']} branch cause {b['root_cause']!r} is not "
                    f"one of the 17 frozen root causes in "
                    f"ops/root_causes.py")

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

    assert any(c["id"] == "LVA-015" for c in cards), "no safety walk card"
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
    print(f"  deck        living-room ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
