#!/usr/bin/env python3
"""
Build the Guest Bedroom deck: 57 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: ten rooms already carry a full diagnosis layer and
a shipped deck (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home
Office, Garage, Stair Landing, Pantry, Hall Closet, Dining Room). Guest
Bedroom is the next room built the same way: rich, hand-authored Manual
content for all five zones (purpose, done_looks_like, passes, the_call,
watch_for, leave_behind, shine_detail), but no diagnosis layer and no deck
until this file. It adds that layer to content/manual/source/content.json
(fifteen frictions, forty-five branches, five first_15 actions) and builds
the deck straight off it, the same shape ops/cardtext/build_pantry_deck.py
already uses for its own five-zone room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action and
its victory condition are quoted from the Manual, not rewritten, and `gate()`
at the bottom asserts they are still character-for-character identical. The
fifteen frictions (symptom and every branch to a root cause) are likewise
derived straight from the Manual's own `diagnosis` layer, in zone order, not
retyped, so this deck cannot silently diverge from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the ten
zone-linked action cards, the three whole-room actions, the event cards, the
micro quests, and the room card. The root causes are not reauthored: they
are the same frozen vocabulary in ops/root_causes.py that every other room's
deck already uses, so a household owning more than one deck keeps one
diagnosis pile rather than several (DECK-GAME-DESIGN.md 4.3). Thirteen of
the seventeen shared ids are reachable from this room's real frictions,
counted honestly from the branches actually written below, not chosen first
and filled in: KC-001, KC-002, KC-003, KC-005, KC-006, KC-007, KC-008,
KC-009, KC-010, RC-013, RC-014, RC-015, RC-017. KC-004, KC-011, KC-012 and
RC-016 are not reachable because nothing in this room's real diagnosis
branches to them, and that is a true statement about this room's own
frictions, not an oversight; nothing pads the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Guest Bedroom ships as a free typeset page, the same stage every prior room
in this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). The budget
below is the same shape as Entryway and Pantry, the other five-zone rooms
in this line: five real zones, fifteen frictions (three per zone), thirteen
reachable root causes, thirteen action cards (two per zone plus three
whole-room), five standard cards and five event cards. 57 cards in total,
not padded or trimmed to match any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_guest_bedroom_deck.py
Out:  ops/cardtext/guest-bedroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "guest-bedroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Guest Bedroom"

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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-005", "KC-006", "KC-007",
             "KC-008", "KC-009", "KC-010", "RC-013", "RC-014", "RC-015",
             "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Guest Bed and Linens": {
  "id": "GBZ-001", "order": 1, "difficulty": 2,
  "tagline": "ONE SET MADE UP. ONE SET TAGGED. NOTHING ELSE UNDER THE BED.",
  "callouts": [
   "A mattress protector fitted under the bottom sheet",
   "One complete sheet set made up on the bed",
   "A second complete set folded inside its own pillowcase, standing on "
   "the shelf",
   "Two pillows that spring back into shape when folded in half",
   "One empty suitcase lying flat under the bed",
   "A tag naming the bed size visible on the folded spare set",
  ],
  "art": ("a made-up guest bed with a mattress protector and one "
          "complete sheet set, a second folded set with a visible size "
          "tag standing on a shelf nearby, two pillows resting beside "
          "it, and one empty suitcase lying flat and visible under the "
          "bed"),
 },
 "Guest Nightstand": {
  "id": "GBZ-002", "order": 2, "difficulty": 1,
  "tagline": "TWO CABLES, TESTED TONIGHT. NOTHING OF YOURS IN THE DRAWER.",
  "callouts": [
   "A bedside lamp with its switch easy to find by feel",
   "One charging cable per common connector, plugged in and reaching "
   "the pillow",
   "A coaster sitting on the nightstand surface",
   "A box of tissues at least half full",
   "A drawer standing open and empty apart from one card",
   "A card printed with the wifi name and password sitting alone in the "
   "drawer",
  ],
  "art": ("a bedside nightstand with a lamp switch within easy reach, "
          "one charging cable of each common type reaching toward the "
          "pillow, a coaster and a half-full tissue box on the surface, "
          "and an open drawer showing only a single wifi card inside"),
 },
 "Guest Dresser": {
  "id": "GBZ-003", "order": 3, "difficulty": 3,
  "tagline": "TWO DRAWERS, ALWAYS EMPTY. THE STRAP FIXED. NOTHING BORROWED.",
  "callouts": [
   "The top two drawers standing completely empty and lined",
   "Spare linens in the lower drawers folded to one uniform footprint",
   "A label fixed to the inside front edge of a lower drawer",
   "An anti-tip strap fixed between the dresser and the wall",
   "A lamp or a mirror standing alone on the dresser top",
   "No second object crowding the dresser top beside the lamp or mirror",
  ],
  "art": ("a guest dresser with its top two drawers open and empty, a "
          "lower drawer showing folded linens at one uniform footprint "
          "with a visible label, an anti-tip strap fixed between the "
          "dresser back and the wall, and a lamp standing alone on the "
          "dresser top"),
 },
 "Guest Closet": {
  "id": "GBZ-004", "order": 4, "difficulty": 4,
  "tagline": "SIX HANGERS PAST THE TAPE. ONE CLEAR SQUARE. NOTHING SEALED "
             "SINCE THE MOVE.",
  "callouts": [
   "A forearm's width of clear closet rod",
   "Six matching empty hangers on the clear rod",
   "A clear floor square big enough for an open suitcase",
   "Household bins on the shelf inside labeled lidded boxes",
   "Nothing loose sitting above head height on the shelf",
   "A strip of tape on the rod marking where the guest section ends",
  ],
  "art": ("a guest closet with a clear stretch of rod holding six "
          "matching empty hangers past a strip of tape, an open floor "
          "square large enough for a suitcase, and a shelf of labeled "
          "lidded bins sitting below head height"),
 },
 "Guest Welcome and Work Surface": {
  "id": "GBZ-005", "order": 5, "difficulty": 3,
  "tagline": "ONE MARKED FOOTPRINT. ONE CLEAR DESK. NO CORD ACROSS THE "
             "FLOOR.",
  "callouts": [
   "A clear desk surface with a working lamp",
   "A chair pulled up to the desk",
   "A luggage rack or a taped floor square for the suitcase",
   "One labeled welcome bin standing on the desk",
   "A spare charger, wifi card, water glass, tissues and a folded "
   "blanket visible inside the open bin",
   "A reachable outlet with no cord crossing the floor",
  ],
  "art": ("a guest room desk with a working lamp, a chair pulled up to "
          "it, a luggage rack beside a taped floor square, one labeled "
          "bin open to show a charger, wifi card, water glass and "
          "tissues, and a wall outlet with no cord crossing the floor"),
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
 "Guest Bed and Linens": {
  "frictions": [
   {
    "symptom": "A guest crossing this room in the dark to find the bathroom would have to step around a suitcase, a footstool, or a looped blind cord near the bed.",
    "branches": [
     {"answer": "It's obvious to us because we live with this room, so nobody has actually walked it in the dark the way a stranger would", "cause": "RC-017"},
     {"answer": "Nobody is assigned to walk this room and check the path before a guest arrives", "cause": "RC-013"},
     {"answer": "This is a real fall and strangulation risk the moment a guest or a visiting child meets it, not a tidiness question", "cause": "KC-010"},
    ]},
   {
    "symptom": "Something that is not a suitcase is sitting under the guest bed when you finally look.",
    "branches": [
     {"answer": "It was easier to set it down here than decide where it actually belongs", "cause": "RC-015"},
     {"answer": "This room has no daily user, so whatever lands under that bed goes unnoticed until a guest is already arriving", "cause": "KC-009"},
     {"answer": "Nobody in the house has agreed this space is reserved for the suitcase and nothing else", "cause": "KC-008"},
    ]},
   {
    "symptom": "A fitted sheet's corner pops off the mattress while you are making up the bed, and it has been part of the guest set for years anyway.",
    "branches": [
     {"answer": "It's not really a spare anymore, it's linen I haven't admitted needs replacing", "cause": "RC-015"},
     {"answer": "I can't tell from the shelf how many complete sets we actually have without unfolding each one", "cause": "KC-005"},
     {"answer": "Nothing marks a set as failed the day it pops a corner, so it just goes back onto the shelf with the good ones", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Take every sheet set that has been demoted to this room and try each fitted sheet on the actual mattress. If a corner pops off while you are making the bed, it is a rag, not a spare. Fold each pillow in half and let go, and anything that stays folded goes out.",
   "victory": "Every remaining sheet set has passed the mattress test, and every remaining pillow springs back when folded in half.",
  },
 },
 "Guest Nightstand": {
  "frictions": [
   {
    "symptom": "The drawer holds dead batteries, a clock radio with the wrong time, or paperbacks nobody actually chose for this room.",
    "branches": [
     {"answer": "None of it has a real home elsewhere in the house, so it ends up in the one drawer nobody uses daily", "cause": "KC-002"},
     {"answer": "It's been in there for years, so it doesn't register as something to remove anymore", "cause": "RC-017"},
     {"answer": "Whoever last used this room for something else left it there, and nobody after them has looked", "cause": "RC-013"},
    ]},
   {
    "symptom": "A water glass and a charging cord are crowded on this small surface where a sleepy arm could sweep them, or a prescription is sitting in the drawer at the height a visiting toddler would explore first.",
    "branches": [
     {"answer": "This is a real shock, spill, or poisoning risk, which outranks how convenient the layout is", "cause": "KC-010"},
     {"answer": "Finding the lamp switch by feel in the dark has never actually been tested, so a guest fumbles for it instead", "cause": "KC-006"},
     {"answer": "We've walked past that cord crossing the surface so many times it stopped registering as a hazard", "cause": "RC-017"},
    ]},
   {
    "symptom": "A cable in this drawer has never actually been tested, and nobody could say whether it would charge anything tonight.",
    "branches": [
     {"answer": "It drifted in on the idea a guest might need it, not because anyone tested it", "cause": "RC-015"},
     {"answer": "There's no standard for what counts as guest-ready here, only whatever happened to end up in the drawer", "cause": "KC-008"},
     {"answer": "Nobody has a reason to open this drawer and test anything between one guest and the next", "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Open the drawer and take out what has been hiding in a room nobody uses: dead batteries, a clock radio that lost its time when the power blipped, three paperbacks nobody chose, cough drops fused into their tin. None of it belongs to a guest, and none of it belongs to you either.",
   "victory": "The drawer holds only what a guest needs: a lamp within reach, two tested cables, tissues, a coaster and the wifi card, nothing of the household's.",
  },
 },
 "Guest Dresser": {
  "frictions": [
   {
    "symptom": "A bag of outgrown baby clothes is still in this dresser, kept for a second child nobody has actually decided about.",
    "branches": [
     {"answer": "It's not clutter, it's a decision about whether we're having another child that I haven't made yet", "cause": "RC-015"},
     {"answer": "It's a keepsake from when they were tiny, and letting go of it feels bigger than the space it takes", "cause": "RC-014"},
     {"answer": "The lower drawers were never actually assigned to spare guest linens only, so the baby bag just moved in when there was room", "cause": "KC-002"},
    ]},
   {
    "symptom": "This dresser has no anti-tip strap, the heaviest linens sit in the bottom drawers, and a loose dry-cleaning bag is within a low drawer a small child could open.",
    "branches": [
     {"answer": "This is a real tip-over and suffocation risk the moment a visiting child is left playing in this room", "cause": "KC-010"},
     {"answer": "Nobody has checked this dresser's own weight distribution or its low drawers since it was set up", "cause": "RC-013"},
     {"answer": "We've walked past this same dresser for years without ever registering it isn't strapped down", "cause": "RC-017"},
    ]},
   {
    "symptom": "The guest dresser's top two drawers are holding off-season clothes, cables, or wrapping paper instead of standing empty for a guest.",
    "branches": [
     {"answer": "The room stands empty most of the year, so it felt like the space cost nothing to borrow", "cause": "RC-015"},
     {"answer": "Nobody has agreed these two drawers are reserved and never available for anything else", "cause": "KC-008"},
     {"answer": "There's no other place in the house these off-season things have an actual assigned spot", "cause": "KC-002"},
    ]},
  ],
  "first_15": {
   "action": "This is where the household's undecided things hide behind a closed front: off-season jumpers, a bin of cables, wrapping paper and ribbon, a bag of outgrown baby clothes waiting on a decision about a second child. The jumpers go to your own wardrobe, the cables to the drawer that already holds cables, and the baby clothes get the decision today rather than another year of storage.",
   "victory": "The top two drawers stand empty and lined, and the lower drawers hold only spare linens for this room's bed.",
  },
 },
 "Guest Closet": {
  "frictions": [
   {
    "symptom": "A box on this shelf has been sealed since a previous address, and nobody can say what's inside without opening it.",
    "branches": [
     {"answer": "Opening it feels like it could cost an afternoon, so it keeps getting put off", "cause": "RC-015"},
     {"answer": "This closet gets opened for a guest, not for a household chore, so nothing ever naturally prompts opening that box", "cause": "KC-009"},
     {"answer": "It's been sitting on that shelf so long it doesn't register as a task anymore, just part of the shelf", "cause": "RC-017"},
    ]},
   {
    "symptom": "A box of old phones or paperwork from a previous address is on this shelf with no named person or occasion attached to it.",
    "branches": [
     {"answer": "None of it has a next use, it's just here because nowhere else claimed it", "cause": "KC-002"},
     {"answer": "There's more of this kind of thing than any real future use could need", "cause": "KC-001"},
     {"answer": "Sorting it by who would actually use it takes a decision I keep deferring", "cause": "RC-015"},
    ]},
   {
    "symptom": "Heavy boxes sit on the shelf above the rod, or a suitcase and loose bins are left on the closet floor in the dark stretch a guest crosses barefoot.",
    "branches": [
     {"answer": "This is a real falling-object and trip risk the moment someone reaches for a hanger or walks this floor in the dark", "cause": "KC-010"},
     {"answer": "Nobody checks this shelf often enough to notice a bin has crept toward the edge", "cause": "RC-013"},
     {"answer": "The floor square for a suitcase was never actually marked, so bins spread into it by default", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Take everything out and put it on the bed. This closet is where the house keeps holiday decorations, a wedding dress in a zipped bag, a box of old phones, and paperwork from two addresses ago. Sort by whether a named person will use it in a named situation, and route the rest out.",
   "victory": "At least a forearm's width of clear rod carries six matching empty hangers, and the floor square for a suitcase is clear.",
  },
 },
 "Guest Welcome and Work Surface": {
  "frictions": [
   {
    "symptom": "The desk is holding gift wrap, an ironing pile that never made it back to the wardrobe, or a printer that hasn't been switched on all year.",
    "branches": [
     {"answer": "This room is doing a second job for the household, and nobody's decided how much of that job this desk can honestly keep", "cause": "RC-015"},
     {"answer": "None of this has a home somewhere else in the house, so the closest quiet surface holds it", "cause": "KC-002"},
     {"answer": "It's been sitting there long enough that it doesn't register as something to clear anymore", "cause": "RC-017"},
    ]},
   {
    "symptom": "An extension lead runs across the open floor to the only reachable outlet, or a hard case is balanced on the desk edge while cases are carried in and out.",
    "branches": [
     {"answer": "This is a real trip, fall, and crush risk the moment a guest walks this floor in the dark or a child is in the room while cases move", "cause": "KC-010"},
     {"answer": "The only reachable outlet sits on the far side of the room from the desk, so the lead has to cross the walking path to reach it", "cause": "KC-003"},
     {"answer": "It's the household's own habit to balance things on the desk edge, and nobody's re-checked that habit since a guest room started needing it clear", "cause": "RC-017"},
    ]},
   {
    "symptom": "Clearing this room's second job off the desk would take more than one trip, or something would need unplugging first.",
    "branches": [
     {"answer": "The second job was never given its own marked footprint, so it spread across the whole desk instead of staying in one bin", "cause": "KC-008"},
     {"answer": "This activity genuinely needs more room than a shared desk can honestly give it", "cause": "KC-007"},
     {"answer": "Nobody has actually run the one-trip test to find out; it's just assumed to be fine", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Clear the surface completely. It will be holding gift wrap, an ironing pile that never made it back, a printer that has not been switched on this year, and paperwork someone brought in here to deal with in peace. The ironing goes back to the wardrobe it came from, the printer either earns a desk somewhere it gets used or leaves the house, and the paperwork goes into the file it was always headed for.",
   "victory": "The desk stands clear with a working lamp, and no cord crosses the walking line to the outlet.",
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
 # Positional order matches content.json's own reordered frictions list
 # for this zone (see EXPECTED_DIAGNOSIS's own comment above): dark path,
 # then under-bed, then sheet corner. Card ids are arbitrary and unchanged
 # by the reorder.
 ("Guest Bed and Linens", "GBF-001", "THE DARK PATH FROM PILLOW TO DOOR",
  "a guest bedroom at night with a footstool and a looped blind cord "
  "sitting in the direct path between the bed and the door"),
 ("Guest Bed and Linens", "GBF-002", "SOMETHING UNDER THE BED THAT ISN'T "
  "THE SUITCASE",
  "a cardboard box visible under a made-up guest bed where only a flat "
  "empty suitcase should be"),
 ("Guest Bed and Linens", "GBF-003", "THE SET THAT POPS A CORNER EVERY TIME",
  "a fitted sheet's corner springing loose off a mattress mid-make on a "
  "guest bed, an otherwise ordinary bedroom in the background"),

 # Positional order matches content.json's own reordered frictions list
 # (see EXPECTED_DIAGNOSIS's own comment above): dead-batteries, then
 # water-glass-cord, then cable-untested last, moved there so it does not
 # crowd the shared "why-everyone-in-your-house-disagrees-about-clean"
 # article past its sitewide ceiling. Card ids unchanged by the reorder.
 ("Guest Nightstand", "GBF-004", "DEAD BATTERIES AND A CLOCK WITH THE "
  "WRONG TIME",
  "an open nightstand drawer holding loose dead batteries, a small "
  "clock radio showing the wrong time, and a couple of paperback books"),
 ("Guest Nightstand", "GBF-005", "THE CORD ACROSS THE SLEEPY-ARM SWEEP",
  "a water glass, a lamp base and a charging cord crowded together on a "
  "small nightstand surface with the cord crossing where a reaching arm "
  "would land"),
 ("Guest Nightstand", "GBF-006", "THE CABLE NOBODY HAS TESTED",
  "a loose charging cable coiled in an open nightstand drawer with no "
  "device attached to prove it works"),

 # Positional order matches content.json's own reordered frictions list:
 # baby-clothes-bag, then no-strap, then top-drawer last, for the same
 # article-ceiling reason as Nightstand above.
 ("Guest Dresser", "GBF-007", "THE BAG KEPT FOR A DECISION NOT YET MADE",
  "a sealed bag of outgrown baby clothes sitting in the bottom of a "
  "guest dresser drawer beside folded guest linens"),
 ("Guest Dresser", "GBF-008", "THE DRESSER WITH NO STRAP",
  "a bedroom dresser with no visible anti-tip strap between its back "
  "and the wall, a low drawer cracked open showing loose plastic "
  "dry-cleaning film"),
 ("Guest Dresser", "GBF-009", "THE TOP DRAWER THAT ISN'T EMPTY",
  "a dresser's top drawer half open, showing folded off-season jumpers "
  "and a tangle of cables instead of standing empty"),

 ("Guest Closet", "GBF-010", "THE BOX SEALED SINCE THE LAST ADDRESS",
  "a taped cardboard box sitting on a closet shelf with an old, "
  "unreadable address label still stuck to its side"),
 ("Guest Closet", "GBF-011", "PAPERWORK WITH NO NAME ATTACHED",
  "a stack of old paperwork and a box of outdated phones sitting on a "
  "closet shelf beside neatly hung clothes"),
 ("Guest Closet", "GBF-012", "BOXES ABOVE THE ROD, BINS ON THE DARK FLOOR",
  "heavy boxes stacked on a closet shelf directly above a hanging rod, "
  "with loose bins sitting on the closet floor below in dim light"),

 # Positional order matches content.json's own reordered frictions list:
 # desk-second-job (unchanged, first), then extension-lead, then
 # one-trip-test last, for the same article-ceiling reason as Nightstand
 # and Dresser above.
 ("Guest Welcome and Work Surface", "GBF-013", "THE DESK DOING THE ROOM'S "
  "SECOND JOB",
  "a guest room desk covered in gift wrap, an unfinished ironing pile "
  "and an unused printer instead of standing clear"),
 ("Guest Welcome and Work Surface", "GBF-014", "THE CORD ACROSS THE "
  "WALKING LINE",
  "an extension lead running across an open floor to a far wall "
  "outlet, a hard suitcase balanced on the edge of a desk nearby"),
 ("Guest Welcome and Work Surface", "GBF-015", "MORE THAN ONE TRIP TO "
  "CLEAR IT",
  "a cluttered desk corner with craft supplies spread past a single "
  "bin's worth of space"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, guest-bedroom-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a shelf of old phones and paperwork from a previous address "
           "filling a guest closet shelf, clearly more than any real "
           "future use would need",
 "KC-002": "loose household batteries, a clock radio and paperback "
           "books sitting inside an open guest nightstand drawer with "
           "nowhere else in the house to go",
 "KC-003": "an extension lead stretching across an open guest room "
           "floor to reach the one outlet on the far wall",
 "KC-005": "a stack of folded guest sheet sets on a shelf with no way "
           "to tell how many complete sets are inside without "
           "unfolding each one",
 "KC-006": "a hand fumbling in the dark for a bedside lamp switch that "
           "cannot be found by feel",
 "KC-007": "craft supplies spread across a guest room desk with far "
           "more than one bin's worth of space",
 "KC-008": "a guest dresser drawer half full of off-season clothes "
           "with no label or marking showing it should stand empty",
 "KC-009": "a sealed box sitting untouched on a guest closet shelf "
           "with nothing in the room's own routine to prompt opening "
           "it",
 "KC-010": "a looped blind cord hanging within reach of a guest bed, "
           "and an extension lead crossing the floor nearby",
 "RC-013": "a guest bedroom floor with an unremoved footstool in the "
           "walking path, no checklist or name attached to who should "
           "have walked it",
 "RC-014": "a small bag of outgrown baby clothes sitting untouched in "
           "the bottom of a guest dresser drawer",
 "RC-015": "a taped cardboard box sitting sealed on a guest closet "
           "shelf since a previous address, no name or date marked "
           "anywhere on it",
 "RC-017": "an unstrapped dresser standing in a guest bedroom exactly "
           "as it has for years, nothing about it flagged as unusual",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Guest Bed and Linens": [
  "Run the vacuum's upholstery tool along the mattress seams where "
  "dust settles between guests.",
  "Wipe the headboard's top edge with a dry microfiber cloth, the one "
  "strip nobody's arm ever reaches while sitting up.",
  "Pull the bed a stride from the wall and vacuum the strip of floor "
  "behind it.",
 ],
 "Guest Nightstand": [
  "Wipe the lamp base and switch with a barely damp cloth so a guest's "
  "first touch in the dark is clean.",
  "Vacuum the drawer's inside corners where dust settles behind the "
  "wifi card.",
  "Test both charging cables against a real phone and note the date on "
  "a card inside the drawer.",
 ],
 "Guest Dresser": [
  "Wipe the dresser top and the lamp or mirror on it until no smear "
  "remains.",
  "Vacuum inside each empty top drawer before closing it, corners "
  "included.",
  "Check the anti-tip strap's screws are still snug against the wall.",
 ],
 "Guest Closet": [
  "Vacuum the closet floor corner behind where suitcases usually sit.",
  "Wipe the rod itself with a dry cloth so a hanger slides on cleanly.",
  "Check the taped guest-section line is still stuck down and "
  "readable.",
 ],
 "Guest Welcome and Work Surface": [
  "Wipe the desk surface and lamp base with the neutral pH cleaner "
  "before the welcome bin goes back.",
  "Vacuum the chair seat and the floor square marked for the suitcase.",
  "Check the outlet and cord are still clear of the walking line.",
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
 {"id": "GBA-001", "zone": "Guest Bed and Linens",
  "title": "TEST EVERY GUEST SET, RAG THE FAILURES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take every sheet set that has been demoted to this room and "
          "try each fitted sheet on the actual mattress, so nothing "
          "that fails the test stays in the guest rotation.",
  "why": "A set that pops a corner mid-make is a rag, not a spare, and "
         "a guest has no way to know which one they were handed.",
  "inputs": ["a bin bag or rag pile"],
  "steps": [
   "Take every sheet set that has been demoted to this room and try "
   "each fitted sheet on the actual mattress. If a corner pops off "
   "while you are making the bed, it is a rag, not a spare. Fold each "
   "pillow in half and let go, and anything that stays folded goes "
   "out.",
   "Count what survives: you need exactly two complete sets for this "
   "bed, not however many happen to fit on the shelf."],
  "causes": ["RC-015", "KC-005"],
  "victory": "Every remaining sheet set has passed the mattress test, "
             "and every remaining pillow springs back when folded in "
             "half.",
  "next": "GBS-001",
  "art": "a hand testing a fitted sheet's corner against a bare "
         "mattress, a folded rejected set set apart on the floor beside "
         "it"},

 {"id": "GBA-002", "zone": "Guest Bed and Linens",
  "title": "CLEAR UNDER THE BED AND WALK THE DARK ROUTE",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Empty anything that is not the guest suitcase out from under "
          "the bed, tie up any loose blind cord, and walk the route "
          "from pillow to door with the lights off.",
  "why": "A guest crossing this room in the dark has never memorised "
         "where the footstool or the box lives; you have, which is "
         "exactly why you cannot see the hazard anymore.",
  "inputs": ["nothing beyond your own two feet and the lights switch"],
  "steps": [
   "Walk from the pillow to the door with the lights off, the way a "
   "guest will in the small hours in a room they do not know, and "
   "clear anything their shin will find.",
   "If the bed sits under a blind, tie the cord up out of reach of a "
   "visiting toddler.",
   "Remove anything from under the bed that is not the one folded-flat "
   "suitcase, and give it a real home elsewhere in the house."],
  "causes": ["KC-009", "KC-010"],
  "victory": "Nothing but one empty suitcase remains under the bed, and "
             "the dark walk from pillow to door meets no obstacle.",
  "next": "GBA-001",
  "art": "a hand tying up a blind cord above a guest bed at night, the "
         "floor path to the door visibly clear"},

 {"id": "GBA-003", "zone": "Guest Nightstand",
  "title": "CLEAR THE DRAWER OF EVERYTHING THAT ISN'T A GUEST'S",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take out everything that has been hiding in this drawer and "
          "leave only what a guest actually needs.",
  "why": "None of what collects here belongs to a guest, and none of "
         "it belongs to you either once you actually look at it.",
  "inputs": ["a bin bag"],
  "steps": [
   "Open the drawer and take out what has been hiding in a room nobody "
   "uses: dead batteries, a clock radio that lost its time when the "
   "power blipped, three paperbacks nobody chose, cough drops fused "
   "into their tin. None of it belongs to a guest, and none of it "
   "belongs to you either.",
   "Leave only a card with the wifi name and password inside the "
   "empty drawer."],
  "causes": ["KC-002", "RC-013"],
  "victory": "The drawer holds only what a guest needs: a lamp within "
             "reach, two tested cables, tissues, a coaster and the "
             "wifi card, nothing of the household's.",
  "next": "GBS-002",
  "art": "a hand clearing dead batteries and an old paperback out of a "
         "nightstand drawer, a single wifi card left inside"},

 {"id": "GBA-004", "zone": "Guest Nightstand",
  "title": "PROVE TWO CABLES AND MOVE THE HAZARDS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Keep exactly two cables here, one of each connector your "
          "visitors actually carry, and prove each one tonight by "
          "charging a real device. Move any prescription or medicine "
          "out of the drawer.",
  "why": "An untested cable is not hospitality, it is a trap with a "
         "bow on it, and medicine at toddler height is a poisoning "
         "risk the moment a visiting family uses this room.",
  "inputs": ["a real phone to test with", "the two cables you are "
             "keeping"],
  "steps": [
   "Charge a real device from each cable you plan to keep before a "
   "guest ever tries either one.",
   "Move anything of the household's, prescriptions and painkillers "
   "included, out of this drawer for good.",
   "Confirm the lamp switch can be found by feel with the room dark."],
  "causes": ["KC-008", "KC-010", "KC-006"],
  "victory": "Two tested cables reach the pillow, the lamp switch is "
             "findable by feel in the dark, and nothing of the "
             "household's remains in the drawer.",
  "next": "GBA-003",
  "art": "a hand charging a phone from a nightstand cable in a dim "
         "room, the charge indicator lit"},

 {"id": "GBA-005", "zone": "Guest Dresser",
  "title": "OPEN THE TOP DRAWERS AND MAKE THE DECISION",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the top two drawers of everything the household has "
          "been storing there, and make the one decision that has been "
          "avoided about the baby clothes.",
  "why": "This dresser is not free storage because the room stands "
         "empty most of the year; every week it holds the household's "
         "overflow is a week the guest room is not actually a guest "
         "room.",
  "inputs": ["a marker for the drawer label", "somewhere for the "
             "jumpers and cables to go"],
  "steps": [
   "This is where the household's undecided things hide behind a "
   "closed front: off-season jumpers, a bin of cables, wrapping paper "
   "and ribbon, a bag of outgrown baby clothes waiting on a decision "
   "about a second child. The jumpers go to your own wardrobe, the "
   "cables to the drawer that already holds cables, and the baby "
   "clothes get the decision today rather than another year of "
   "storage.",
   "Label the inside front edge of a lower drawer with what it now "
   "holds."],
  "causes": ["RC-015", "RC-014"],
  "victory": "The top two drawers stand empty and lined, and the lower "
             "drawers hold only spare linens for this room's bed.",
  "next": "GBS-003",
  "art": "a dresser's top drawer standing empty and lined, a bag of "
         "baby clothes set apart on the floor awaiting a decision"},

 {"id": "GBA-006", "zone": "Guest Dresser",
  "title": "STRAP THE DRESSER AND CLEAR THE LOW DRAWER",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Fix an anti-tip strap between the dresser and the wall, and "
          "remove any loose plastic or dry-cleaning film from a low "
          "drawer.",
  "why": "An unstrapped dresser with heavy linens low and light drawers "
          "high is a real tip-over risk in a room where a visiting "
          "child is often left to play.",
  "inputs": ["an anti-tip strap and its fixings", "a screwdriver"],
  "steps": [
   "Fix the anti-tip strap between the back of the dresser and the "
   "wall stud, not just the drywall.",
   "Remove any dry-cleaning film or loose plastic bags from a low "
   "drawer a small guest could open.",
   "Mark these two drawers reserved so nothing of the household's "
   "moves back in."],
  "causes": ["KC-010", "KC-008"],
  "victory": "An anti-tip strap is fixed between the dresser and the "
             "wall, and no low drawer holds loose plastic or film.",
  "next": "GBA-005",
  "art": "a hand fixing an anti-tip strap between the back of a "
         "dresser and a wall stud"},

 {"id": "GBA-007", "zone": "Guest Closet",
  "title": "OPEN THE SEALED BOX AND NAME A PERSON OR IT GOES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty this closet onto the bed and sort everything by "
          "whether a named person will use it in a named situation.",
  "why": "A box sealed since a previous address that nobody can name a "
         "use for is not storage, it is a decision wearing a use's "
         "clothes.",
  "inputs": ["a marker for dating anything you cannot yet decide on"],
  "steps": [
   "Take everything out and put it on the bed. This closet is where "
   "the house keeps holiday decorations, a wedding dress in a zipped "
   "bag, a box of old phones, and paperwork from two addresses ago. "
   "Sort by whether a named person will use it in a named situation, "
   "and route the rest out.",
   "For anything you truly cannot face today, write today's date on "
   "the lid and give yourself one year before it leaves unopened."],
  "causes": ["KC-002", "KC-001"],
  "victory": "At least a forearm's width of clear rod carries six "
             "matching empty hangers, and the floor square for a "
             "suitcase is clear.",
  "next": "GBS-004",
  "art": "a sealed cardboard box opened on a bed beside a closet, its "
         "contents being sorted into keep and go piles"},

 {"id": "GBA-008", "zone": "Guest Closet",
  "title": "TAPE THE GUEST SECTION AND CLEAR THE OVERHEAD SHELF",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Move heavy boxes off the shelf directly above the rod, clear "
          "loose bins from the closet floor, and mark the tape line "
          "where the guest section ends.",
  "why": "A heavy box above the rod is a falling-object risk the "
          "moment a hand reaches for a hanger, and a bin on the dark "
          "floor is what a barefoot guest finds first.",
  "inputs": ["tape for the rod line", "labeled lidded bins"],
  "steps": [
   "Move every heavy box off the shelf directly above the rod, and "
   "repack household storage into labeled lidded bins below head "
   "height.",
   "Clear the closet floor of loose bins so a suitcase has a real "
   "square to sit in.",
   "Stick a strip of tape on the rod marking exactly where the guest "
   "section ends."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No loose item sits above head height on the shelf, and a "
             "strip of tape on the rod marks the guest section clearly.",
  "next": "GBA-007",
  "art": "a hand moving a heavy box down from a closet shelf above the "
         "rod, a clear floor square visible below"},

 {"id": "GBA-009", "zone": "Guest Welcome and Work Surface",
  "title": "CLEAR THE DESK COMPLETELY",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the desk surface completely and send everything on it "
          "back to where it actually belongs.",
  "why": "Gift wrap, an ironing pile, and an unused printer are the "
          "household's second job spilling onto the one surface a "
          "guest needs clear.",
  "inputs": ["a bin for filing", "the wardrobe the ironing came from"],
  "steps": [
   "Clear the surface completely. It will be holding gift wrap, an "
   "ironing pile that never made it back, a printer that has not been "
   "switched on this year, and paperwork someone brought in here to "
   "deal with in peace. The ironing goes back to the wardrobe it came "
   "from, the printer either earns a desk somewhere it gets used or "
   "leaves the house, and the paperwork goes into the file it was "
   "always headed for."],
  "causes": ["KC-002", "RC-015"],
  "victory": "The desk stands clear with a working lamp, and no cord "
             "crosses the walking line to the outlet.",
  "next": "GBS-005",
  "art": "a desk being cleared of gift wrap and an ironing pile, a "
         "lamp and a clear surface emerging underneath"},

 {"id": "GBA-010", "zone": "Guest Welcome and Work Surface",
  "title": "GIVE THE SECOND JOB A MARKED FOOTPRINT AND MOVE THE CORD",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Name this room's second job out loud, give it a marked "
          "footprint you can clear in one trip, and route the "
          "extension lead away from the walking path.",
  "why": "Pretending this room has only one job is why hosting takes "
          "an afternoon; naming the second job honestly is what turns "
          "it back into a bed change.",
  "inputs": ["tape for the marked footprint", "one bin or cupboard for "
             "the second job"],
  "steps": [
   "Name the room's second job out loud, and test it: can the whole "
   "thing clear into one bin or one cupboard, in a single trip, "
   "without unplugging anything?",
   "Mark that footprint in tape so the boundary is visible, not "
   "assumed.",
   "Move the extension lead so it no longer crosses the floor a guest "
   "walks in the dark."],
  "causes": ["KC-007", "KC-003"],
  "victory": "The second job clears into its marked footprint in one "
             "trip, and no cord crosses the walking line to the "
             "outlet.",
  "next": "GBA-009",
  "art": "a taped floor footprint beside a desk, an extension lead "
         "rerouted away from the open walking path"},

 {"id": "GBA-011", "zone": None,
  "title": "THE FULL ROOM SAFETY AND ACCESS WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk the whole room testing what a guest cannot see for "
          "themselves: the lamp switch in the dark, every cord's "
          "route, and whether anything about this room's own habits "
          "has gone unnoticed for too long.",
  "why": "You know this room too well to see its own hazards; a guest "
          "meets all of them for the first time, in the dark, tonight.",
  "inputs": ["nothing beyond the lights switch and your own hands"],
  "steps": [
   "With the lights off, find the nightstand lamp switch by feel "
   "alone, the way a guest will.",
   "Walk every cord in the room and confirm none of them crosses a "
   "path a guest would take.",
   "Ask someone who does not live here to name one thing about this "
   "room that looks out of place to them; if they see it instantly "
   "and you had stopped noticing, fix that thing first."],
  "causes": ["KC-006", "RC-017"],
  "victory": "The lamp switch is findable by feel in the dark, no cord "
             "crosses a walking path, and nothing a fresh pair of eyes "
             "flagged remains unfixed.",
  "next": "GBA-010",
  "art": "a hand finding a bedside lamp switch by feel in a dark guest "
         "room, no cord visible crossing the floor"},

 {"id": "GBA-012", "zone": None, "title": "WHO WALKS THIS ROOM BEFORE A "
  "GUEST ARRIVES",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "Name one person whose job it is to walk this room and check "
          "it before every arrival, not whoever happens to remember.",
  "why": "This room has no daily user, so upkeep depends entirely on "
          "someone being named for it; without a name, it depends on "
          "luck.",
  "inputs": ["nothing beyond a decision"],
  "steps": [
   "Say out loud, or write down, whose job it is to walk this room "
   "before every guest arrives.",
   "Walk it once now, today, as a test of what that job actually "
   "involves."],
  "causes": ["RC-013"],
  "victory": "One named person has walked this room before this "
             "arrival, and everyone in the house knows whose job that "
             "is.",
  "next": "GBA-011",
  "art": "a hand writing a name onto a card taped inside a guest "
         "bedroom closet door"},

 {"id": "GBA-013", "zone": None, "title": "THE MONTHLY BORROWED-SPACE "
  "AUDIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Once a month, check that the reserved dresser drawers, the "
          "closet's guest section, and the desk's marked footprint "
          "have not been quietly recolonised by the household.",
  "why": "A boundary drawn once and never rechecked is exactly how a "
          "guest room turns back into a storage room with a bed in "
          "it.",
  "inputs": ["nothing beyond the boundaries you have already marked"],
  "steps": [
   "Check the top two dresser drawers are still empty and the closet's "
   "tape line still marks a real boundary.",
   "Check the desk's marked footprint still holds only what it was "
   "given.",
   "For anything that has crept back in, decide today where it "
   "actually belongs rather than let it stay."],
  "causes": ["KC-008", "KC-002"],
  "victory": "Every marked boundary in this room, the drawers, the "
             "closet line, and the desk footprint, still holds exactly "
             "what it was given, checked this month.",
  "next": "GBA-012",
  "art": "a hand checking an empty dresser drawer against its own "
         "label, a tape line visible on a closet rod behind it"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a guest bedroom, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("GBE-001", "THE LATE-NIGHT ARRIVAL",
  "A guest calls from the road an hour out, later than planned, and "
  "the bed has to be ready the moment they walk in.",
  ["GBZ-001"],
  "A complete set is already made up and the second set sits tagged "
  "and ready on the shelf, no laundry required.",
  "If a set had to come out of the wash or off another bed first, the "
  "sustain trigger slipped. Draw GBA-001.",
  "a hand smoothing a finished, made-up guest bed at night with a "
  "tagged spare set visible folded on a nearby shelf"),
 ("GBE-002", "THE PHONE THAT NEEDS TO CHARGE OVERNIGHT",
  "A guest's phone is nearly dead and they reach for whichever cable "
  "is on the nightstand without asking.",
  ["GBZ-002"],
  "Either cable on the nightstand charges the phone immediately, "
  "because both were tested this week.",
  "If the cable did nothing, an untested one had drifted back into the "
  "drawer. Draw GBA-004.",
  "a hand plugging a phone into a nightstand cable in a dimly lit "
  "guest room, the charge indicator lighting up immediately"),
 ("GBE-003", "THE WEEKEND GUEST WHO ACTUALLY UNPACKS",
  "A guest staying more than one night opens the top drawers to unpack "
  "a full suitcase.",
  ["GBZ-003"],
  "Both top drawers are already empty and lined, ready for a full "
  "suitcase with nothing to clear out first.",
  "If anything of the household's had to come out first, the "
  "reserved-drawer rule slipped. Draw GBA-005.",
  "a guest's folded clothes being placed into an already-empty, lined "
  "dresser drawer"),
 ("GBE-004", "THE COAT THAT NEEDS A HANGER IN THE DARK",
  "A guest arrives after dark and reaches into the closet for a hanger "
  "without a light on.",
  ["GBZ-004"],
  "Six matching hangers are exactly where the tape line says they are, "
  "and the floor square underneath is clear to step onto.",
  "If a hanger was missing or a bin was underfoot in the dark, the "
  "guest-section boundary slipped. Draw GBA-008.",
  "a hand reaching into a dark closet and finding an empty hanger "
  "exactly past a strip of tape on the rod"),
 ("GBE-005", "THE MORNING THE HOUSEHOLD'S OWN PROJECT SPILLS BACK IN",
  "Someone needs the desk for the room's other job the same week a "
  "guest is due to arrive.",
  ["GBZ-005"],
  "The whole project clears into its one marked bin in a single trip, "
  "no unplugging required, leaving the desk clear.",
  "If it took more than one trip or something needed unplugging, the "
  "marked footprint was never honestly set. Draw GBA-010.",
  "hands lifting a single labeled bin off a guest room desk to leave "
  "it completely clear"),
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
        "related": {"standard": f"GBS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your guest room, "
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
    standard_id = (f"GBS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"GBS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "GBR-001", "title": "THE GUEST BEDROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "THE ROOM WITH NO DAILY USER IS WHERE EVERYTHING "
                   "UNDECIDED HIDES.",
        "objective": "The guest bedroom is the only room in the house "
                     "with no daily user, which is why it quietly "
                     "absorbs whatever the rest of the house could not "
                     "decide about. This card is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"GBZ-004 Guest Closet. {start_tip['text']}"
            if start_tip else
            "GBZ-004 Guest Closet. The closet is where the overflow "
            "actually lives, and the bed goes quickly once the room "
            "around it is honest."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your guest room. Put the rest back.",
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
        "safety_first": "Do GBA-011 The Full Room Safety And Access "
                        "Walk before any rebuild. It takes thirty "
                        "minutes and covers the dark path, every cord, "
                        "and the dresser strap.",
        "related": {"contents": "GBZ-001 to GBZ-005, GBF-001 to GBF-015, "
                                 "the shared root causes in "
                                 "ops/root_causes.py, GBA-001 to GBA-013, "
                                 "GBS-001 to GBS-005, GBE-001 to GBE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole guest "
                           "bedroom in its settled state, the bed made "
                           "up, the nightstand, the dresser, the closet "
                           "door open onto six matching hangers, and the "
                           "welcome desk all visible in one frame",
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
    return {"deck": "guest-bedroom", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "GBA-011" for c in cards), "no safety walk card"
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
    print(f"  deck        guest-bedroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
