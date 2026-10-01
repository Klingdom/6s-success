#!/usr/bin/env python3
"""
Build the Guest Bathroom deck: 60 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: eleven rooms already carry a full diagnosis layer
and a shipped deck (Entryway, Kitchen, Pantry, Dining Room, Primary
Bathroom, Laundry Room, Home Office, Garage, Hall Closet, Stair Landing,
Guest Bedroom). Guest Bathroom is the next room built the same way: rich,
hand-authored Manual content for all five zones (purpose, done_looks_like,
passes, the_call, watch_for, leave_behind, shine_detail), but no diagnosis
layer and no deck until this file. It adds that layer to
content/manual/source/content.json (fifteen frictions, forty-five
branches, five first_15 actions) and builds the deck straight off it, the
same shape ops/cardtext/build_pantry_deck.py already uses for its own
five-zone room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action
and its victory condition are quoted from the Manual, not rewritten, and
`gate()` at the bottom asserts they are still character-for-character
identical. The fifteen frictions (symptom and every branch to a root
cause) are likewise derived straight from the Manual's own `diagnosis`
layer, in zone order, not retyped, so this deck cannot silently diverge
from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked:
the all-caps titles and art briefs for the zone and friction cards, the
ten zone-linked action cards, the three whole-bathroom actions, the event
cards, the micro quests, and the room card. The root causes are not
reauthored: they are the same frozen vocabulary in ops/root_causes.py that
every other room's deck already uses, so a household owning more than one
deck keeps one diagnosis pile rather than several (DECK-GAME-DESIGN.md
4.3). Sixteen of the seventeen shared ids are reachable from this room's
real frictions, counted honestly from the branches actually written
below, not chosen first and filled in: KC-001, KC-002, KC-003, KC-004,
KC-005, KC-006, KC-008, KC-009, KC-010, KC-011, KC-012, RC-013, RC-014,
RC-015, RC-016, RC-017. KC-007 (insufficient capacity) is not reachable
because nothing in this room's real diagnosis branches to it: the guest
bathroom's whole design is a small, deliberately minimal set of items
(three counter things, one shampoo, one conditioner, one body wash, two
towel bundles), and nothing in the Manual's own text ever says a genuinely
right-sized space here cannot hold what belongs in it. That is a true
statement about this room's own frictions, not an oversight; nothing pads
the count to a rounder number.

WHAT THE BUDGET IS AND WHY
---------------------------
Guest Bathroom ships as a free typeset page, the same stage every prior
room in this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and
it does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). The budget
below is the same shape as Entryway, Pantry and Hall Closet, the other
five-zone rooms in this line: five real zones, fifteen frictions (three
per zone), sixteen reachable root causes (two more than Pantry's
thirteen, one more than Hall Closet's fourteen, because this room's real
frictions happen to reach WRONG LOCATION, EXCESS MOTION, POOR VISIBILITY,
POOR ACCESSIBILITY and SENTIMENTAL ATTACHMENT in combinations neither of
those rooms did), thirteen action cards (two per zone plus three
whole-bathroom), five standard cards and five event cards. 60 cards in
total, not padded or trimmed to match any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_guest_bathroom_deck.py
Out:  ops/cardtext/guest-bathroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "guest-bathroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Guest Bathroom"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 5, "FRICTION CARD": 15,
          "ROOT CAUSE CARD": 16, "ACTION CARD": 13, "STANDARD CARD": 5,
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
# below from the Manual and asserted (in gate()) to be exactly this set:
# not a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-008", "KC-009", "KC-010", "KC-011", "KC-012", "RC-013",
             "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Guest Vanity Counter": {
  "id": "GHZ-001", "order": 1, "difficulty": 2,
  "tagline": "THREE THINGS LIVE HERE: SOAP, TISSUES, A TOWEL. NOTHING ELSE.",
  "callouts": [
   "A soap pump standing above half full on the counter",
   "One folded hand towel hanging on a ring visible from the doorway",
   "A box of tissues sitting at the back corner clear of splash",
   "A clear stretch of bare counter wide enough for a phone and a pair "
   "of glasses",
   "No toothbrush cup or hair clips anywhere on the counter",
   "A dry, ring-free patch of counter under the soap dispenser",
  ],
  "art": ("a bathroom vanity counter holding a soap pump standing above "
          "half full, a single folded hand towel hanging on a ring by "
          "the door, a box of tissues at the back corner, and a clear "
          "stretch of bare counter with no toothbrush cup or hair clips "
          "in view"),
 },
 "Guest Vanity Storage": {
  "id": "GHZ-002", "order": 2, "difficulty": 3,
  "tagline": "TWO BINS. ONE LABELED GUEST, ONE LABELED CLEANING. THE BASE "
             "STAYS BARE.",
  "callouts": [
   "A bin labeled Guest Supplies holding a new toothbrush and a wrapped "
   "bar of soap",
   "A small dish holding four unopened travel toiletries inside that "
   "same bin",
   "A bin labeled Cleaning holding bowl cleaner, glass spray and cloths "
   "standing upright",
   "Four rolls of toilet paper stacked in plain view",
   "A bare cabinet base with nothing loose sitting on it",
   "Both bins standing light enough to lift out with one hand",
  ],
  "art": ("the inside of an open bathroom vanity cabinet holding two "
          "labeled lift-out bins, one marked Guest Supplies with a "
          "wrapped soap bar and travel toiletries in a small dish, one "
          "marked Cleaning with bottles standing upright on a tray, "
          "four rolls of toilet paper stacked beside them, and a bare "
          "cabinet base"),
 },
 "Shower or Tub": {
  "id": "GHZ-003", "order": 3, "difficulty": 4,
  "tagline": "THREE BOTTLES. ONE MAT. ONE THING BOLTED IN TO GRAB.",
  "callouts": [
   "Three bottles in a hanging caddy, shampoo, conditioner and body "
   "wash, each more than a third full",
   "A curtain liner or glass screen with no pink film along its bottom "
   "edge",
   "A bath mat folded over the tub rim rather than lying wet on the "
   "floor",
   "Grout the same even color in the corners as in the middle",
   "A non-slip surface visible on the tub floor",
   "One securely anchored grab point fixed to the wall, not a towel bar",
  ],
  "art": ("a guest bathroom shower with three bottles standing in a "
          "hanging caddy, a clean curtain liner with no pink film at "
          "its hem, a folded bath mat draped over the tub rim, evenly "
          "colored grout in every corner, a non-slip ridged tub "
          "floor, and one securely anchored grab bar fixed to the "
          "tiled wall"),
 },
 "Toilet Area": {
  "id": "GHZ-004", "order": 4, "difficulty": 2,
  "tagline": "ONE ROLL IN SIGHT. A DRY BRUSH. A LINER IN THE CAN.",
  "callouts": [
   "One spare toilet roll standing in a holder within reach of a "
   "seated person",
   "A dry toilet brush resting in its holder with no liquid pooled in "
   "the bottom",
   "A small trash can with a liner actually fitted inside it",
   "No ring visible at the bowl's water line",
   "A dry, dust-free floor behind the pedestal",
   "A bare tank top with nothing standing on it",
  ],
  "art": ("a guest bathroom toilet area with one spare roll standing in "
          "a holder within easy seated reach, a dry brush resting in "
          "its holder, a small lined trash can, a clean bowl with no "
          "ring at the water line, and a dust-free floor behind the "
          "pedestal"),
 },
 "Guest Linen Zone": {
  "id": "GHZ-005", "order": 5, "difficulty": 3,
  "tagline": "TWO BUNDLES. ONE LIFT EACH. THE MAT UNDERNEATH.",
  "callouts": [
   "Two complete towel bundles, each holding a bath towel, hand towel "
   "and washcloth folded together",
   "Both bundles matching in color with neither carrying a musty smell",
   "A clean bath mat folded flat beneath the bundles",
   "A hand's width of clear air above the stack",
   "No thin gray towel or dog towel sharing the shelf",
   "A hand's width of clearance kept around anything on the shelf that "
   "runs hot",
  ],
  "art": ("a linen closet shelf holding two matching complete towel "
          "bundles each with a bath towel, hand towel and washcloth "
          "folded together, a folded bath mat lying flat beneath them, "
          "a hand's width of clear air above the stack, and no thin "
          "gray towel sharing the shelf"),
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
 "Guest Vanity Counter": {
  "frictions": [
   {"symptom": "A cup on this counter is holding a toothbrush that "
               "clearly belongs to someone who lives here, not a "
               "visitor.",
    "branches": [
     {"answer": "Someone in this house genuinely brushes their teeth "
                "in here every day, and nobody's said that out loud "
                "yet", "cause": "KC-012"},
     {"answer": "Nobody ever decided this counter isn't for personal "
                "items, so whatever's nearby just lands here",
      "cause": "KC-002"},
     {"answer": "The main bathroom ran out of room, so the overflow "
                "came in here without anyone deciding to move it back",
      "cause": "RC-015"},
    ]},
   {"symptom": "The soap pump sits below half and the hand towel "
               "still smells faintly of the closet, and you only "
               "notice because someone is already at the door.",
    "branches": [
     {"answer": "Nobody is the one who walks in here between visits "
                "to check on it", "cause": "RC-013"},
     {"answer": "There's no trigger tied to a visit being confirmed, "
                "so topping it up depends on remembering",
      "cause": "KC-009"},
     {"answer": "A counter with no daily user is easy to stop seeing "
                "as something that needs checking at all",
      "cause": "RC-017"},
    ]},
   {"symptom": "A glass tumbler stands on a wet counter beside a hair "
               "dryer that is still plugged in next to a full basin.",
    "branches": [
     {"answer": "It's decorative, so it never occurred to anyone that "
                "a wet counter makes it a hazard", "cause": "RC-017"},
     {"answer": "The cord gets left plugged in and coiled on the "
                "counter because there's nowhere else near the basin "
                "to keep it", "cause": "KC-002"},
     {"answer": "It's a real fall and shock risk sitting there beside "
                "a full basin, and that outranks how it looks",
      "cause": "KC-010"},
    ]},
  ],
  "first_15": {
   "action": "Take everything off the counter and put back only what "
             "a visitor would use: soap, tissues, hand towel. The "
             "travel conditioner, the spare contact lens case, and "
             "the razor that ended up here because the main bathroom "
             "ran out of room all go back where they belong or into "
             "the trash.",
   "victory": "Only soap, tissues and a folded hand towel remain on "
              "the counter, with bare space enough for a phone and "
              "glasses, and nothing of the household's left behind.",
  },
 },
 "Guest Vanity Storage": {
  "frictions": [
   {"symptom": "A shelf in this cabinet is still holding shampoos and "
               "lotions from three different trips, most of them "
               "barely started.",
    "branches": [
     {"answer": "Throwing out free soap feels like waste, so it just "
                "never gets decided", "cause": "RC-015"},
     {"answer": "Every trip added one more and nobody's ever called "
                "the total too many", "cause": "KC-001"},
     {"answer": "They arrived from a different bathroom's overflow, "
                "not bought for this cabinet", "cause": "KC-003"},
    ]},
   {"symptom": "The toilet paper stack is already down to its last "
               "roll before anyone notices it's running low.",
    "branches": [
     {"answer": "There's no drawn line showing when the stack is "
                "getting low, so nobody notices until it's nearly "
                "gone", "cause": "KC-011"},
     {"answer": "It's stacked loose behind other things instead of "
                "standing in plain view", "cause": "KC-005"},
     {"answer": "Whoever raids this cabinet for the main bathroom "
                "never records that they did", "cause": "RC-013"},
    ]},
   {"symptom": "A bottle of bowl cleaner sits on the cabinet floor "
               "with its cap loose, at exactly the height a crawling "
               "child would reach.",
    "branches": [
     {"answer": "It's stored low because that's simply where the "
                "cabinet space was, not because it's safe",
      "cause": "KC-003"},
     {"answer": "It's within reach of hands the household doesn't "
                "usually think about, which is a safety problem that "
                "outranks convenience", "cause": "KC-010"},
     {"answer": "Nobody who opens this cabinet regularly is the one "
                "who'd notice a visiting child in the room",
      "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Pull everything out and be honest about the hotel "
             "miniatures: the shampoos from three trips, the lotion "
             "nobody opened, the free conditioner samples. Keep the "
             "unopened ones a guest would actually use, throw out the "
             "started ones, and send household backstock that "
             "drifted in here back to the bathroom it came from.",
   "victory": "Every started miniature and drifted household item is "
              "gone, and only unopened travel toiletries a guest "
              "would actually use remain.",
  },
 },
 "Shower or Tub": {
  "frictions": [
   {"symptom": "One grout line has been scrubbed three times, stayed "
               "the same gray, and you've quietly started calling "
               "that clean.",
    "branches": [
     {"answer": "It's mold grown into the grout or a failed silicone "
                "bead, not surface dirt, and no product lifts that",
      "cause": "RC-016"},
     {"answer": "Nobody's called it a repair job instead of a "
                "cleaning job, so it keeps costing a scrub every "
                "week", "cause": "RC-015"},
     {"answer": "It's stayed the same shade for so long it's stopped "
                "registering as stained rather than clean",
      "cause": "RC-017"},
    ]},
   {"symptom": "Three half-used bottles of shampoo and body wash "
               "nobody liked are welded to the tub floor by their own "
               "residue.",
    "branches": [
     {"answer": "They arrived because the household rejected them "
                "elsewhere, and this shower is where rejects retire",
      "cause": "RC-015"},
     {"answer": "There's no caddy or shelf, so anything set down "
                "stands directly on the tub floor", "cause": "KC-002"},
     {"answer": "It's more bottles than one person showering needs, "
                "they just never got cleared", "cause": "KC-001"},
    ]},
   {"symptom": "There's no mat on the tub floor and no grab bar on "
               "the wall, and a guest is about to step in here well "
               "after dark.",
    "branches": [
     {"answer": "A towel bar screwed into drywall isn't rated to take "
                "a person's weight, and nobody's added a proper "
                "anchor point", "cause": "KC-010"},
     {"answer": "The household showers here so rarely that a missing "
                "mat stopped registering as a problem",
      "cause": "RC-017"},
     {"answer": "Putting the mat out isn't anyone's specific job "
                "before a guest arrives", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Take out every bottle and turn it over. This is where "
             "the household's rejected products retire: the shampoo "
             "nobody liked, the body wash that smells wrong, the "
             "conditioner welded to the shelf. Keep one shampoo, one "
             "conditioner, one body wash, all readable and more than "
             "a third full. The rest go, along with the old razor and "
             "the disintegrating loofah.",
   "victory": "One shampoo, one conditioner and one body wash stand "
              "in the shower, each more than a third full and easy to "
              "read, with nothing else left welded to the shelf.",
  },
 },
 "Toilet Area": {
  "frictions": [
   {"symptom": "The reserve roll is mounted low on the wall, and a "
               "seated guest has to stand up to reach it.",
    "branches": [
     {"answer": "It went into whatever holder was already installed, "
                "never tested with someone actually seated",
      "cause": "KC-006"},
     {"answer": "Nobody's rechecked its placement since it was first "
                "fitted", "cause": "RC-013"},
     {"answer": "It's been in that spot so long nobody thinks to "
                "question the reach anymore", "cause": "RC-017"},
    ]},
   {"symptom": "The top of the tank and the floor behind the bowl "
               "have collected a pile: air fresheners, a second "
               "brush, old magazines, a box nobody can identify.",
    "branches": [
     {"answer": "None of it got a decision when it landed there, it "
                "just accumulated behind the door swing",
      "cause": "RC-015"},
     {"answer": "Nobody's specifically responsible for clearing this "
                "room's flat surfaces, so it just grows",
      "cause": "RC-013"},
     {"answer": "It's been building for so long that none of it reads "
                "as clutter to the household anymore", "cause": "RC-017"},
    ]},
   {"symptom": "The toilet brush has stood in an inch of gray water "
               "in its holder for years, bristles splayed.",
    "branches": [
     {"answer": "It's a consumable everyone's been treating like a "
                "fixture, so nobody's replaced it", "cause": "KC-008"},
     {"answer": "Cleaning properly under the rim and rinsing the "
                "brush after each flush takes an extra step nobody's "
                "built into the routine", "cause": "RC-016"},
     {"answer": "There's no trigger that says a brush this age gets "
                "replaced, so it just keeps going", "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Clear everything from the top of the tank and the floor "
             "behind the bowl: the collection of air fresheners, the "
             "second brush, the magazines, the box of something "
             "nobody has identified in years. One reserve roll stays "
             "in the open. Nothing else.",
   "victory": "The tank top and the floor behind the bowl are bare "
              "except for one reserve roll standing in the open.",
  },
 },
 "Guest Linen Zone": {
  "frictions": [
   {"symptom": "The best towels in the house are still folded in the "
               "closet years later, while guests dry off on ones that "
               "have gone thin and gray.",
    "branches": [
     {"answer": "Using the nice ones feels like using them up, so "
                "they get held back instead", "cause": "RC-014"},
     {"answer": "Nobody's decided the worn ones should actually "
                "retire, so they just keep getting reissued",
      "cause": "RC-015"},
     {"answer": "A towel that just sits folded doesn't look like it "
                "needs a decision, thin fold line and all",
      "cause": "RC-017"},
    ]},
   {"symptom": "A bundle taken from this shelf midweek for some other "
               "use is never the one that comes back.",
    "branches": [
     {"answer": "Nothing here tracks what left, so the gap is only "
                "found by the next guest", "cause": "KC-011"},
     {"answer": "There's no single person who restocks this shelf "
                "after it's been raided", "cause": "RC-013"},
     {"answer": "Taking a towel from here doesn't trigger anything "
                "that says to replace it", "cause": "KC-009"},
    ]},
   {"symptom": "Making up a guest set means grabbing a bath towel "
               "from one stack, a hand towel from a shelf across the "
               "closet, and a washcloth that matches neither.",
    "branches": [
     {"answer": "Towels are stored by type instead of as ready sets, "
                "so what should be one lift turns into three separate "
                "stops", "cause": "KC-004"},
     {"answer": "Nobody decided guest towels should be pre-bundled, "
                "so they default to being grouped by size instead",
      "cause": "KC-008"},
     {"answer": "It's always been sorted this way, so the extra "
                "hunting doesn't register as a real problem",
      "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Unfold every towel and look at it in daylight rather "
             "than closet light. Anything thin along the fold line, "
             "permanently gray, stiff from too much softener, or "
             "carrying a hair dye or nosebleed stain comes out of the "
             "guest stack. It becomes a rag or a car towel today. It "
             "does not go back just in case.",
   "victory": "Every towel remaining in the guest stack is free of "
              "thinning, graying, stiffness or stains, and none of it "
              "went back in just in case.",
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
 ("Guest Vanity Counter", "GHF-001", "A HOUSEMATE'S TOOTHBRUSH LIVES HERE TOO",
  "a cup on a bathroom vanity counter holding two mismatched toothbrushes "
  "standing among the guest soap and tissues"),
 ("Guest Vanity Counter", "GHF-002",
  "THE SOAP PUMP HASN'T BEEN TOPPED UP SINCE THE LAST VISIT",
  "a soap pump on a bathroom vanity counter sitting visibly below half "
  "full beside a hand towel that looks limp and long hung"),
 ("Guest Vanity Counter", "GHF-003",
  "A GLASS TUMBLER SITS ON A WET COUNTER BESIDE A PLUGGED-IN CORD",
  "a glass tumbler standing on a wet bathroom counter beside a hair "
  "dryer with its cord still plugged into a wall socket near the basin"),

 ("Guest Vanity Storage", "GHF-004",
  "A DRAWER FULL OF HOTEL MINIATURES FROM THREE TRIPS",
  "a cluttered vanity cabinet shelf crowded with a dozen mismatched "
  "hotel miniature shampoo and lotion bottles from different trips"),
 ("Guest Vanity Storage", "GHF-005",
  "THE TOILET PAPER STACK IS ALREADY DOWN TO ONE ROLL",
  "a single toilet paper roll standing alone on an otherwise bare "
  "vanity cabinet shelf"),
 ("Guest Vanity Storage", "GHF-006",
  "THE BOWL CLEANER SITS WHERE A CRAWLING CHILD CAN REACH IT",
  "a bottle of bowl cleaner with its cap loose sitting on the floor of "
  "an open vanity cabinet at a low, child-reachable height"),

 ("Shower or Tub", "GHF-007",
  "THE GROUT STAYS THE SAME GRAY NO MATTER HOW MANY TIMES YOU SCRUB IT",
  "a close view of grout lines in a shower corner showing an even gray "
  "tint against the surrounding tile despite a scrub brush resting "
  "nearby"),
 ("Shower or Tub", "GHF-008",
  "THREE REJECTED BOTTLES ARE WELDED TO THE TUB FLOOR",
  "three half-used shampoo and body wash bottles standing directly on "
  "a wet tub floor, each ringed with a sticky residue at its base"),
 ("Shower or Tub", "GHF-009",
  "NO MAT, NO GRAB BAR, AND A GUEST STEPPING IN AT NIGHT",
  "an empty tub floor with no bath mat and a towel bar mounted on the "
  "tiled wall, no dedicated grab bar anywhere in view"),

 ("Toilet Area", "GHF-010",
  "THE RESERVE ROLL IS MOUNTED WHERE A SEATED GUEST CAN'T REACH IT",
  "a toilet paper holder mounted low on a bathroom wall well behind "
  "and below where a seated person's hand would reach"),
 ("Toilet Area", "GHF-011",
  "A PILE OF AIR FRESHENERS AND OLD MAGAZINES BEHIND THE BOWL",
  "a cluttered toilet tank top holding air freshener cans, a second "
  "toilet brush and a stack of old magazines"),
 ("Toilet Area", "GHF-012", "THE BRUSH HAS STOOD IN GRAY WATER FOR YEARS",
  "a toilet brush standing in a holder with visibly gray, cloudy water "
  "pooled in its base, its bristles splayed outward"),

 ("Guest Linen Zone", "GHF-013", "THE GOOD TOWELS ARE STILL FOLDED IN THE CLOSET",
  "a linen closet shelf holding a pristine folded towel set clearly "
  "untouched at the back, beside a thin, graying towel set at the "
  "front"),
 ("Guest Linen Zone", "GHF-014",
  "A BUNDLE LEFT THIS SHELF MIDWEEK AND NEVER CAME BACK",
  "a linen closet shelf holding a single towel bundle where a matching "
  "second one should stand beside it, an obvious gap in the stack"),
 ("Guest Linen Zone", "GHF-015",
  "ONE GUEST SET MEANS THREE SEPARATE STOPS",
  "a hand reaching across three separate stacks in an open linen "
  "closet to gather one bath towel, one hand towel and one washcloth"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, guest-bathroom-scened art only. The name, meaning,
# six_s and confirm_in_30_seconds text are not reauthored: they are read
# straight from ops/root_causes.py, the one shared vocabulary the deck,
# the app and the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a small cluster of hotel miniature shampoo bottles crowded "
           "together on a bathroom vanity shelf, far more than a single "
           "guest stay would use",
 "KC-002": "a hair dryer's cord coiled loose on a bathroom vanity "
           "counter with no drawer or hook anywhere nearby to hold it",
 "KC-003": "a bottle of bowl cleaner standing on the floor behind a "
           "toilet pedestal instead of inside the cleaning cabinet "
           "across the room",
 "KC-004": "a hand reaching across three separate stacks in a linen "
           "closet to gather one bath towel, one hand towel and one "
           "washcloth",
 "KC-005": "a single roll of toilet paper stacked behind other items "
           "on a vanity cabinet shelf, barely visible from the door",
 "KC-006": "a toilet paper holder mounted low on a bathroom wall, out "
           "of easy reach for someone seated",
 "KC-008": "a worn toilet brush standing in its holder beside a spare "
           "one, with no sign either has ever been replaced on a "
           "schedule",
 "KC-009": "a bathroom vanity counter with a soap pump sitting below "
           "half full and no note or reminder anywhere nearby",
 "KC-010": "a glass tumbler standing on a wet bathroom counter beside "
           "a plugged-in appliance cord within reach of the basin",
 "KC-011": "an empty gap on a linen closet shelf where a second towel "
           "bundle should stand",
 "KC-012": "a toothbrush cup holding two personal toothbrushes "
           "standing among a guest soap pump and folded hand towel",
 "RC-013": "a bathroom vanity counter with a hand towel that has "
           "clearly hung untouched since an earlier visit, no note of "
           "whose turn it is to refresh it",
 "RC-014": "a pristine, never-used towel set folded at the back of a "
           "linen shelf behind the towels actually given to guests",
 "RC-015": "a half-used bottle of rejected shampoo standing on a "
           "shower shelf, clearly kept rather than thrown out",
 "RC-016": "a shower grout line showing the same even gray tone "
           "despite a scrub brush resting against the tile beside it",
 "RC-017": "a toilet brush standing in cloudy water in its holder, "
           "positioned in a corner nobody appears to have looked at in "
           "some time",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Guest Vanity Counter": [
  "Wipe the collar at the base of the tap where a chalky ring hides, "
  "working it with a folded cloth corner until it lifts.",
  "Lift the soap pump and wipe the sticky ring under its base before "
  "setting it back down.",
  "Wipe the towel ring and its mount clean before you rehang a fresh "
  "folded towel.",
 ],
 "Guest Vanity Storage": [
  "Wipe the neck and cap of one bottle in each bin where dried product "
  "has run down the side.",
  "Run a hand across the bare cabinet base, feeling for a dark ring or "
  "a soft patch near the trap.",
  "Wipe the inside face of the cabinet door and its handle before "
  "closing it.",
 ],
 "Shower or Tub": [
  "Spray the grout lines and the bottom band of the liner, then leave "
  "them to dwell while you finish elsewhere.",
  "Wipe the sticky ring left under each bottle on the caddy or shelf.",
  "Wipe the shower head and arm where scale has started to crust the "
  "spray holes.",
 ],
 "Toilet Area": [
  "Wipe the flush handle on every face, since it is the one thing "
  "every guest touches.",
  "Lift the seat and wipe its underside and the rim it sits on, the "
  "part most often missed.",
  "Rinse the brush holder so no liquid pools in its bottom before it "
  "goes back.",
 ],
 "Guest Linen Zone": [
  "Wipe the front lip of one shelf where hands grip to pull a towel "
  "stack out.",
  "Run a hand along the back wall of the closet, checking for damp.",
  "Refold one bundle so a hand's width of air sits above the finished "
  "stack.",
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
 {"id": "GHA-001", "zone": "Guest Vanity Counter",
  "title": "CLEAR THE COUNTER TO THREE THINGS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take everything off the counter and put back only what a "
          "visitor would use, so nothing of the household's is left in "
          "view.",
  "why": "A counter holding a housemate's toothbrush or a stray hair "
         "clip stops reading as a guest counter and starts reading as "
         "an argument about whose bathroom this is.",
  "inputs": ["a small box for anything going back to another room",
             "a bin bag"],
  "steps": [
   "Take everything off the counter and put back only what a visitor "
   "would use: soap, tissues, hand towel. The travel conditioner, the "
   "spare contact lens case, and the razor that ended up here because "
   "the main bathroom ran out of room all go back where they belong or "
   "into the trash.",
   "Set the soap, tissues and towel back in their usual spots, clear "
   "of the basin."],
  "causes": ["KC-012", "KC-002"],
  "victory": "Only soap, tissues and a folded hand towel remain on the "
             "counter, with bare space enough for a phone and glasses, "
             "and nothing of the household's left behind.",
  "next": "GHS-001",
  "art": "a bathroom vanity counter mid-clear, a small box of personal "
         "items being carried out and only soap, tissues and a folded "
         "towel remaining"},

 {"id": "GHA-002", "zone": "Guest Vanity Counter",
  "title": "SETTLE WHOSE BATHROOM THIS IS AND PHOTOGRAPH THE STANDARD",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Decide out loud whether this is a used bathroom or a guest "
          "bathroom, then photograph the three-item counter and post "
          "the picture inside the vanity door.",
  "why": "Holding a hotel standard against a resident who genuinely "
         "uses this room is aimed at the wrong room, and it gets reset "
         "twice a week until somebody decides.",
  "inputs": ["a phone camera", "tape"],
  "steps": [
   "Ask out loud whether anyone in the house actually uses this "
   "bathroom day to day.",
   "If yes, give that person one named drawer or caddy for their two "
   "items, alongside the guest three; if no, agree that nothing "
   "personal comes back to this counter, starting today.",
   "Photograph the counter holding exactly its agreed items and tape "
   "the picture inside the vanity door."],
  "causes": ["KC-012", "KC-008"],
  "victory": "One decision is made and photographed: either a named "
             "resident has their own labeled spot, or nothing personal "
             "returns to this counter.",
  "next": "GHA-001",
  "art": "a hand taping a photograph of a settled bathroom counter to "
         "the inside of a vanity cabinet door"},

 {"id": "GHA-003", "zone": "Guest Vanity Storage",
  "title": "CLEAR THE MINIATURES AND SEND BACKSTOCK HOME",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull everything out of the cabinet, be honest about years "
          "of hotel miniatures, and return anything that drifted in "
          "from another bathroom.",
  "why": "A miniature kept because throwing out free soap feels "
         "wasteful still takes up the same shelf as the four a guest "
         "would actually use.",
  "inputs": ["a donation bag", "a bin bag"],
  "steps": [
   "Pull everything out and be honest about the hotel miniatures: the "
   "shampoos from three trips, the lotion nobody opened, the free "
   "conditioner samples. Keep the unopened ones a guest would "
   "actually use, throw out the started ones, and send household "
   "backstock that drifted in here back to the bathroom it came from.",
   "Keep four unopened travel toiletries with the least battered "
   "labels in a small dish; bag the rest for donation or the bin."],
  "causes": ["RC-015", "KC-001", "KC-003"],
  "victory": "Every started miniature and drifted household item is "
             "gone, and only unopened travel toiletries a guest would "
             "actually use remain.",
  "next": "GHS-002",
  "art": "a hand sorting a pile of hotel miniature bottles into a keep "
         "dish of four and a donation bag of the rest"},

 {"id": "GHA-004", "zone": "Guest Vanity Storage",
  "title": "LABEL TWO BINS AND LATCH THE CLEANING SHELF",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Set up two labeled lift-out bins, draw a minimum line for "
          "toilet paper, and move or latch anything a crawling child "
          "could reach.",
  "why": "Bowl cleaner and bleach sitting under this sink are exactly "
         "at a visiting toddler's eye level, and a bare cabinet base "
         "is the only way a slow leak from the trap ever gets seen.",
  "inputs": ["two bins", "a marker", "labels", "a childproof latch"],
  "steps": [
   "Write two labels by hand, Guest Supplies and Cleaning, and load "
   "each bin accordingly.",
   "Draw a line on the shelf at the toilet paper minimum, and stack "
   "rolls in plain view above it.",
   "Fit the cabinet with a childproof latch or move the cleaning bin "
   "to a high shelf elsewhere, and never store bleach beside an acid "
   "bowl or limescale cleaner."],
  "causes": ["KC-011", "KC-010", "KC-005"],
  "victory": "Two labeled bins sit on a bare base, toilet paper stands "
             "visible above its drawn line, and the cleaning products "
             "are latched away from a child's reach.",
  "next": "GHA-003",
  "art": "two labeled lift-out bins standing in an open vanity cabinet "
         "beside a visible stack of toilet paper, a childproof latch "
         "fitted to the cabinet door"},

 {"id": "GHA-005", "zone": "Shower or Tub",
  "title": "CLEAR THE REJECTED BOTTLES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Take out every bottle, turn it over, and keep only one "
          "shampoo, one conditioner and one body wash, all more than "
          "a third full.",
  "why": "A bottle nobody liked does not improve by staying on the "
         "tub floor, it just collects a sticky ring underneath it.",
  "inputs": ["a bin bag"],
  "steps": [
   "Take out every bottle and turn it over. This is where the "
   "household's rejected products retire: the shampoo nobody liked, "
   "the body wash that smells wrong, the conditioner welded to the "
   "shelf. Keep one shampoo, one conditioner, one body wash, all "
   "readable and more than a third full. The rest go, along with the "
   "old razor and the disintegrating loofah.",
   "Wipe the sticky ring left on the tub floor or shelf under each "
   "bottle removed."],
  "causes": ["RC-015", "KC-002"],
  "victory": "One shampoo, one conditioner and one body wash stand in "
             "the shower, each more than a third full and easy to "
             "read, with nothing else left welded to the shelf.",
  "next": "GHS-003",
  "art": "a hand lifting a welded shampoo bottle off a tub floor, one "
         "shampoo, one conditioner and one body wash left standing in "
         "a hanging caddy"},

 {"id": "GHA-006", "zone": "Shower or Tub",
  "title": "TREAT THE GROUT, HANG THE MAT, ANCHOR A GRAB BAR",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Give a stained grout line one proper treatment with full "
          "dwell time, fit a non-slip mat, and install one solidly "
          "anchored grab point.",
  "why": "A guest steps into an unfamiliar tub at night on a surface "
         "they cannot judge, and a towel bar screwed into drywall "
         "tears out the moment it takes a person's weight.",
  "inputs": ["dedicated mildew remover", "a stiff grout brush",
             "a non-slip mat or adhesive strips",
             "a wall-anchored grab bar"],
  "steps": [
   "Spray the stained grout line with dedicated mildew remover, leave "
   "it for full dwell time, then work it with a stiff grout brush and "
   "rinse.",
   "If it darkens again within two weeks, stop cleaning it and move "
   "it to the repair list instead.",
   "Fit a non-slip mat or adhesive strips to the tub floor, and "
   "install one securely anchored grab bar, never relying on a towel "
   "bar."],
  "causes": ["RC-016", "KC-010"],
  "victory": "The treated grout line holds its color for two weeks, a "
             "non-slip mat sits on the tub floor, and one solidly "
             "anchored grab bar is fixed to the wall.",
  "next": "GHA-005",
  "art": "a hand pressing a stiff grout brush into a shower corner "
         "beside a freshly fitted non-slip mat and a securely "
         "anchored wall grab bar"},

 {"id": "GHA-007", "zone": "Toilet Area",
  "title": "CLEAR THE TANK TOP AND FLOOR BEHIND THE BOWL",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear everything from the top of the tank and the floor "
          "behind the bowl, leaving one reserve roll standing in the "
          "open.",
  "why": "A pile of air fresheners and old magazines behind the bowl "
         "is where a guest bathroom's clutter hides longest, because "
         "nobody but a guest ever looks there.",
  "inputs": ["a bin bag", "a box for anything worth keeping elsewhere"],
  "steps": [
   "Clear everything from the top of the tank and the floor behind "
   "the bowl: the collection of air fresheners, the second brush, the "
   "magazines, the box of something nobody has identified in years. "
   "One reserve roll stays in the open. Nothing else.",
   "Bin anything unidentifiable and rehome anything genuinely useful "
   "to where it is actually used."],
  "causes": ["RC-015", "RC-017"],
  "victory": "The tank top and the floor behind the bowl are bare "
             "except for one reserve roll standing in the open.",
  "next": "GHS-004",
  "art": "a bare toilet tank top and floor behind the bowl with a "
         "single reserve roll standing in the open, a bin bag sitting "
         "nearby"},

 {"id": "GHA-008", "zone": "Toilet Area",
  "title": "MOVE THE ROLL WITHIN SEATED REACH AND RETIRE THE BRUSH",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Remount the reserve roll where a seated person can reach "
          "it, and replace a splayed or standing-water brush with a "
          "fresh one.",
  "why": "A reserve roll nobody seated can reach defeats the entire "
         "point of having one, and a brush that has stood in gray "
         "water for years spreads more than it removes.",
  "inputs": ["a roll holder", "a new toilet brush and holder"],
  "steps": [
   "Remount or reposition the roll holder so a seated person can "
   "reach it without standing up.",
   "Replace a brush with splayed bristles or standing water in its "
   "holder with a fresh set.",
   "Agree the new routine: rinse the brush in the flush and prop it "
   "to drip under the closed seat before it goes back in the holder."],
  "causes": ["KC-006", "KC-008"],
  "victory": "The reserve roll is reachable from a seated position, "
             "and a fresh, dry brush stands in a dry holder.",
  "next": "GHA-007",
  "art": "a toilet paper holder remounted within easy seated reach, a "
         "fresh dry toilet brush standing in a clean holder beside it"},

 {"id": "GHA-009", "zone": "Guest Linen Zone",
  "title": "RETIRE THE THIN AND GRAY TOWELS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Unfold every towel in daylight and pull anything thin, "
          "gray, stiff or stained out of the guest stack for good.",
  "why": "A towel that looks fine folded in closet light shows its "
         "wear the moment it is unfolded in daylight, and a guest is "
         "the one who finds out first.",
  "inputs": ["daylight or a bright lamp", "a rag bin"],
  "steps": [
   "Unfold every towel and look at it in daylight rather than closet "
   "light. Anything thin along the fold line, permanently gray, stiff "
   "from too much softener, or carrying a hair dye or nosebleed stain "
   "comes out of the guest stack. It becomes a rag or a car towel "
   "today. It does not go back just in case.",
   "Move the household's best remaining towels into the guest stack "
   "to replace what left."],
  "causes": ["RC-014", "RC-015"],
  "victory": "Every towel remaining in the guest stack is free of "
             "thinning, graying, stiffness or stains, and none of it "
             "went back in just in case.",
  "next": "GHS-005",
  "art": "a hand unfolding a thin, graying towel in daylight beside a "
         "stack of newly promoted guest towels"},

 {"id": "GHA-010", "zone": "Guest Linen Zone",
  "title": "BUNDLE BY GUEST, MARK THE LINE, WASH THE STORED SET",
  "minutes": 30, "players": "1", "six_s": "Sustain",
  "goal": "Fold towels into complete guest bundles rather than stacks "
          "by type, mark the shelf at the second bundle's edge, and "
          "wash the stored set even though nobody has used it.",
  "why": "Gathering a bath towel from one stack and a washcloth from "
         "another turns one guest's setup into three separate "
         "searches, and a towel that sat folded all season carries a "
         "musty note the instant it gets wet.",
  "inputs": ["a marker", "the washing machine"],
  "steps": [
   "Fold each bath towel, hand towel and washcloth together into one "
   "bundle, so setting up for a guest is one lift.",
   "Mark the shelf edge where the second bundle should end.",
   "Wash the whole stored set and the bath mat on a hot cycle before "
   "refolding, even though nobody has used them."],
  "causes": ["KC-004", "KC-011"],
  "victory": "Two complete bundles sit on the shelf up to the marked "
             "line, freshly washed, with the bath mat folded beneath "
             "them.",
  "next": "GHA-009",
  "art": "two complete folded towel bundles on a linen shelf beside a "
         "marker line showing where the second bundle ends"},

 {"id": "GHA-011", "zone": None,
  "title": "THE FULL GUEST BATHROOM HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking for a plugged-in cord beside "
          "water, a chemical within a child's reach, a slick tub "
          "floor, and any textile stacked against the water heater.",
  "why": "A guest brings an unfamiliar body, sometimes a visiting "
         "child, into a room the household almost never uses, so the "
         "hazards a daily bathroom would surface get found here only "
         "if someone looks on purpose.",
  "inputs": ["a childproof latch", "a non-slip mat", "a cloth"],
  "steps": [
   "Check the counter for any cord plugged in beside the basin and "
   "any glass standing on a wet surface, and clear both.",
   "Check under the vanity for bowl cleaner or bleach within a "
   "child's reach, and latch the cabinet if it is not already.",
   "Check the tub for a non-slip mat and one securely anchored grab "
   "point, and check the linen closet for a hand's width of "
   "clearance around the water heater."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No cord sits beside water, no chemical sits within a "
             "child's reach, the tub has a non-slip surface and an "
             "anchored grab point, and nothing touches the water "
             "heater.",
  "next": "GHA-012",
  "art": "a hand checking a childproof latch on a vanity cabinet in a "
         "guest bathroom, a non-slip mat visible in the tub beyond"},

 {"id": "GHA-012", "zone": None, "title": "THE VISIT-CONFIRMED WALK-THROUGH",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "The moment a visit is confirmed, walk the whole room once: "
          "top up the soap, hang a fresh towel, check the reserve "
          "roll, and confirm two linen bundles are ready.",
  "why": "This room has no daily user, so nothing forces a check "
         "except someone deciding to do one before a guest arrives.",
  "inputs": ["a fresh hand towel", "a spare toilet roll"],
  "steps": [
   "Top up the soap and hang a fresh hand towel on the counter.",
   "Confirm the reserve roll is upright and a fresh liner is in the "
   "trash can.",
   "Confirm two complete towel bundles stand on the linen shelf up to "
   "the marked line."],
  "causes": ["KC-009", "RC-013"],
  "victory": "The whole room was checked the moment the visit was "
             "confirmed, and one named person did it.",
  "next": "GHA-013",
  "art": "a hand hanging a fresh folded towel on a guest bathroom "
         "counter ring, a full soap pump and a spare toilet roll "
         "visible nearby"},

 {"id": "GHA-013", "zone": None, "title": "THE DEPARTURE RESET",
  "minutes": 30, "players": "1", "six_s": "Sustain",
  "goal": "The moment a guest leaves, strip the bathroom the same way "
          "you strip the bed: run everything they used through one "
          "wash, and restock the linen shelf before you sit down.",
  "why": "A towel taken from this shelf midweek is never the one that "
         "comes back unless the departure itself is what triggers the "
         "reset.",
  "inputs": ["the washing machine"],
  "steps": [
   "Carry out whatever the guest left in the shower or on the counter "
   "to the laundry on the same trip as the bed sheets.",
   "Wash the used towels and bath mat together in one load.",
   "Refold and restock the linen shelf to two complete bundles before "
   "considering the room done."],
  "causes": ["KC-011", "KC-009"],
  "victory": "Everything the guest used is through the wash, and two "
             "complete bundles stand ready on the shelf again.",
  "next": "GHA-011",
  "art": "a laundry basket holding used guest towels and a bath mat "
         "beside a linen shelf being restocked to two bundles"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Five ordinary hard days that test a guest bathroom, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("GHE-001", "THE UNANNOUNCED DROP-IN",
  "A friend calls from the driveway, already parking, and the guest "
  "counter has to answer for itself with zero notice.",
  ["GHZ-001"],
  "The soap pump is full, a fresh hand towel hangs on the ring, and "
  "nothing personal is anywhere in sight.",
  "If a stray toothbrush or a half-empty soap pump greeted them "
  "instead, the visit-confirmed walk-through did not happen. Draw "
  "GHA-002.",
  "a hand towel hanging fresh on a guest bathroom counter ring moments "
  "before a doorbell rings"),
 ("GHE-002", "THE OVERNIGHT GUEST WHO FORGOT A TOOTHBRUSH",
  "A guest arrives without a toothbrush and has to ask, or hopes the "
  "cabinet already has one.",
  ["GHZ-002"],
  "The guest supplies bin opens to a new toothbrush, a wrapped soap "
  "and four fresh travel toiletries, no rummaging required.",
  "If the bin was empty or stuffed with old miniatures instead, the "
  "sort-and-restock pass slipped. Draw GHA-003.",
  "a hand lifting a labeled Guest Supplies bin from an open vanity "
  "cabinet, a new toothbrush and wrapped soap visible inside"),
 ("GHE-003", "THE GUEST WHO SHOWERS AT ELEVEN AT NIGHT",
  "A guest showers well after dark, in an unfamiliar tub, on a floor "
  "they cannot judge by feel alone.",
  ["GHZ-003"],
  "A non-slip mat grips the tub floor, one solidly anchored grab bar "
  "is exactly where a reaching hand finds it, and three full bottles "
  "are easy to read in dim light.",
  "If they reached for a towel bar instead of a grab bar, or found "
  "the floor slick, the safety pass slipped. Draw GHA-006.",
  "a hand gripping a securely anchored wall bar beside a non-slip tub "
  "floor in a dimly lit guest bathroom at night"),
 ("GHE-004", "THE MIDDLE-OF-THE-NIGHT ROLL CHANGE",
  "The roll runs out at two in the morning and a half-asleep guest "
  "has to find the reserve without turning on every light.",
  ["GHZ-004"],
  "The reserve roll stands in reach from the seat, in the same spot "
  "it always is.",
  "If they had to get up and hunt for it, the roll never got "
  "remounted within seated reach. Draw GHA-008.",
  "a hand reaching for a toilet paper holder mounted within easy "
  "seated reach in a dim bathroom"),
 ("GHE-005", "TWO GUESTS ARRIVE INSTEAD OF ONE",
  "A second guest turns up unannounced and the linen shelf has to "
  "produce a full second set on the spot.",
  ["GHZ-005"],
  "Two complete bundles already stand on the shelf up to the marked "
  "line, each one lift away.",
  "If only one bundle was ready, or towels had to be gathered from "
  "three different stacks, the departure reset or the bundling pass "
  "slipped. Draw GHA-010.",
  "two complete towel bundles being lifted together from a linen "
  "shelf for two arriving guests"),
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
        "related": {"standard": f"GHS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your bathroom, "
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
    standard_id = (f"GHS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"GHS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "GHR-001", "title": "THE GUEST BATHROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "FIVE ZONES. START WITH THE COUNTER THE VISITOR SEES "
                   "FIRST.",
        "objective": "The guest bathroom is the one room a visitor "
                     "spends time in alone, with the door shut and "
                     "nothing to look at but your standards. This card "
                     "is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"GHZ-001 Guest Vanity Counter. {start_tip['text']}"
            if start_tip else
            "GHZ-001 Guest Vanity Counter. It takes one trip and "
            "changes how the whole room reads."),
        "how_to_play": [
            "1. Deal the five ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your bathroom. Put the rest back.",
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
        "safety_first": "Do GHA-011 The Full Guest Bathroom Hazard Walk "
                        "before any rebuild. It takes thirty minutes and "
                        "covers the cord beside the basin, the "
                        "chemicals under the cabinet, the tub floor, "
                        "and the water heater in the linen closet.",
        "related": {"contents": "GHZ-001 to GHZ-005, GHF-001 to "
                                 "GHF-015, the shared root causes in "
                                 "ops/root_causes.py, GHA-001 to "
                                 "GHA-013, GHS-001 to GHS-005, GHE-001 "
                                 "to GHE-005"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole guest "
                           "bathroom in its settled state, a vanity "
                           "counter holding three items, a closed "
                           "cabinet, a shower with a hanging caddy, a "
                           "toilet area and a linen shelf all visible "
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
    return {"deck": "guest-bathroom", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "GHA-011" for c in cards), "no safety walk card"
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
    print(f"  deck        guest-bathroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
