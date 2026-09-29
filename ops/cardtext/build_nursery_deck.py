#!/usr/bin/env python3
"""
Build the Nursery deck: 66 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: twelve rooms already carry a full diagnosis layer
and a shipped deck (Entryway, Kitchen, Pantry, Dining Room, Primary
Bathroom, Laundry Room, Home Office, Garage, Hall Closet, Stair Landing,
Guest Bedroom, Guest Bathroom, Family Room, Living Room, Mudroom -- fifteen
by the time this file was written). Nursery is the next room built the
same way: rich, hand-authored Manual content for all six zones (purpose,
done_looks_like, passes, the_call, watch_for, leave_behind, shine_detail),
and a diagnosis layer already authored into
content/manual/source/content.json (eighteen frictions, fifty-four
branches, six first_15 actions) by a separate pass this file does not
redo. This file only reads that layer and builds the deck straight off
it, the same shape ops/cardtext/build_guest_bathroom_deck.py already uses
for its own room.

Purpose, done_looks_like, the standard, the trigger, the first-15 action
and its victory condition are quoted from the Manual, not rewritten, and
`gate()` at the bottom asserts they are still character-for-character
identical. The eighteen frictions (symptom and every branch to a root
cause) are likewise derived straight from the Manual's own `diagnosis`
layer, in zone order, not retyped, so this deck cannot silently diverge
from the diagnostic engine.

The layers the Manual does not hold are hand authored below and marked:
the all-caps titles and art briefs for the zone and friction cards, the
twelve zone-linked action cards, the three whole-nursery actions, the
event cards, the micro quests, and the room card. The root causes are not
reauthored: they are the same frozen vocabulary in ops/root_causes.py that
every other room's deck already uses, so a household owning more than one
deck keeps one diagnosis pile rather than several (DECK-GAME-DESIGN.md
4.3). Fourteen of the seventeen shared ids are reachable from this room's
real frictions, counted honestly from the branches actually written below,
not chosen first and filled in: KC-001, KC-002, KC-003, KC-004, KC-005,
KC-008, KC-009, KC-010, KC-011, KC-012, RC-013, RC-014, RC-015, RC-017.
Three are not reachable, and each is a true statement about this room's
own frictions, not an oversight:

KC-006 (poor accessibility) is not reachable because nothing in the real
diagnosis branches is about a person who cannot physically reach
something safely; the room's real reach problems (the reserve roll, the
book ledge) belong to other rooms' decks, not this one's actual friction
text.

KC-007 (insufficient capacity) is not reachable because every zone's real
frictions are about the wrong things being kept, not too little room for
the right things: the crib, the changing station, the clothing chest, the
feeding bins, the backstock shelf and the book ledge are all sized by a
written rule (one sheet, two bins, one size a drawer, two packs deep,
twelve covers), and nothing in the Manual's own text ever says a
right-sized version of any of them cannot hold what belongs in it.

RC-016 (difficult to clean) is not reachable because, unlike Guest
Bathroom's grout or Kitchen's cooktop, nothing in the Nursery's real
frictions is a surface that resists being reached and wiped; the shine
layer is thorough (mattress supports, drawer runners, drying racks) but
the frictions branch to what is stored wrong or unchecked, not to what is
hard to clean.

WHAT THE BUDGET IS AND WHY
---------------------------
Nursery ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed. The
budget below is six real zones, eighteen frictions (three per zone),
fourteen reachable root causes, fifteen action cards (two per zone plus
three whole-nursery), six standard cards and six event cards. 66 cards in
total, not padded or trimmed to match any other room's count: fourteen
causes is fewer than Guest Bathroom's sixteen, because this room's real
frictions genuinely do not reach three of the seventeen, and that is
reported here rather than smoothed over.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_nursery_deck.py
Out:  ops/cardtext/nursery-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "nursery-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Nursery"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 14, "ACTION CARD": 15, "STANDARD CARD": 6,
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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-008",
             "KC-009", "KC-010", "KC-011", "KC-012", "RC-013", "RC-014",
             "RC-015", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Crib and Sleep Zone": {
  "id": "NUZ-001", "order": 1, "difficulty": 2,
  "tagline": "ONE SHEET. ONE SLEEP SACK. NOTHING CROSSES THE RAIL.",
  "callouts": [
   "A bare mattress holding one fitted sheet pulled tight to all four "
   "corners",
   "A folded sleep sack sitting on top of the dresser",
   "A monitor mounted on the wall with its cable clipped up and back from "
   "the rails",
   "A clear top rail with nothing draped over it",
   "No quilt, plush toy, or bumper anywhere inside the crib",
   "A clear arm's length of space between the mounted cable and the rails",
  ],
  "art": ("a nursery crib holding a bare mattress with one fitted sheet "
          "pulled tight to the corners, a folded sleep sack on the "
          "dresser beside it, a monitor mounted on the wall with its "
          "cable clipped high and back from the rails, and nothing "
          "draped over the top rail"),
 },
 "Changing Station": {
  "id": "NUZ-002", "order": 2, "difficulty": 3,
  "tagline": "EVERYTHING YOUR HAND TOUCHES IS INSIDE ONE ARM'S SWEEP.",
  "callouts": [
   "Diapers, wipes and cream all standing within arm's reach of the pad",
   "A lined pail sitting within one step of the pad",
   "Two spare outfits inside the drawer directly beneath the pad",
   "A pad surface holding nothing stacked on it",
   "No lamp, framed photo, or lotion bottle sitting on the dresser top",
   "No loose wipe refill bag or pail liner roll sitting out on the "
   "dresser",
  ],
  "art": ("a nursery changing station with diapers, wipes and cream "
          "standing within arm's reach of the pad, a lined pail within "
          "one step, two spare outfits visible in the open drawer "
          "beneath the pad, and a bare pad surface with nothing stacked "
          "on it"),
 },
 "Baby Clothing Zone": {
  "id": "NUZ-003", "order": 3, "difficulty": 4,
  "tagline": "ONE SIZE PER DRAWER. THE OUTGOING BAG ALREADY HAS SOMETHING "
             "IN IT.",
  "callouts": [
   "A drawer front carrying one size written large enough to read from a "
   "step back",
   "Sleepers and bodysuits filed upright so every collar reads from "
   "above",
   "A next-size bin standing on the closet shelf",
   "An outgoing bag hanging on the door hook with something already "
   "inside it",
   "No drawer holding two different sizes at once",
   "No tags-still-on outfit sitting in a drawer your baby has outgrown",
  ],
  "art": ("an open nursery dresser drawer labeled with one size in "
          "marker, sleepers and bodysuits filed upright so their collars "
          "read from above, a next-size bin visible on the closet shelf "
          "beyond, and an outgoing bag hanging on the door hook with a "
          "garment already inside it"),
 },
 "Feeding Station": {
  "id": "NUZ-004", "order": 4, "difficulty": 3,
  "tagline": "TWO BINS. CLEAN NEVER SHARES WITH USED.",
  "callouts": [
   "One bin of clean bottles standing fully assembled, teats and collars "
   "on",
   "A second, differently colored bin holding only used parts waiting to "
   "be washed",
   "An empty drying rack standing beside the bins",
   "A formula scoop sitting inside the tin with the lid shut",
   "A stack of burp cloths sitting where a hand finds them without "
   "looking",
   "No cord from the kettle, warmer, or sterilizer coiled loose on the "
   "counter",
  ],
  "art": ("a nursery feeding station with one bin of fully assembled "
          "clean bottles, teats and collars on, a second differently "
          "colored bin holding only used parts, an empty drying rack, a "
          "formula tin with its scoop inside and lid shut, and a stack "
          "of burp cloths beside them, with every appliance cord looped "
          "short behind it"),
 },
 "Diaper and Care Backstock": {
  "id": "NUZ-005", "order": 5, "difficulty": 3,
  "tagline": "ONE SIZE AHEAD. TWO PACKS DEEP. NOTHING STACKED ABOVE THE "
             "CRIB.",
  "callouts": [
   "One unopened pack of the current diaper size standing on the shelf",
   "No more than two packs of the next size standing behind it",
   "Each pack carrying its size written large in marker on the short end",
   "A wipes carton with its remaining count visible from the front",
   "Creams and a thermometer sitting together inside one lidded box",
   "A bare shelf above or beside the crib with nothing stored on it",
  ],
  "art": ("a nursery backstock shelf holding one unopened pack of the "
          "current diaper size at the front and no more than two packs "
          "of the next size behind it, each pack marked with its size in "
          "large marker, a wipes carton with its count visible, a lidded "
          "box holding creams and a thermometer, and a bare shelf above "
          "the crib in the background"),
 },
 "Books and Quiet Play Zone": {
  "id": "NUZ-006", "order": 6, "difficulty": 2,
  "tagline": "TWELVE COVERS OUT. ONE BASKET AT THE RIM.",
  "callouts": [
   "Twelve board books standing cover out along the low ledge",
   "One basket of soft toys filled level with its rim, no higher",
   "A rotation box visible on the closet shelf holding the rest",
   "A clear stretch of floor big enough for an adult to lie down on",
   "No paper-page book sitting on the low ledge",
   "No toy spilling onto the floor beside the basket",
  ],
  "art": ("a low nursery book ledge holding twelve board books standing "
          "cover out, one basket of soft toys filled level with its rim "
          "beside it, a rotation box visible on a closet shelf beyond, "
          "and a clear stretch of floor in front big enough for an adult "
          "to lie down on"),
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
 "Crib and Sleep Zone": {
  "frictions": [
   {
    "symptom": "There's a folded quilt or blanket draped over the crib rail, or a plush toy sitting at the foot of the mattress.",
    "branches": [
     {
      "answer": "Someone gave this as a gift and nobody has said yet, out loud, that it can't go in the crib",
      "cause": "RC-014"
     },
     {
      "answer": "Nobody has actually agreed that the crib rule is a fitted sheet and nothing else",
      "cause": "KC-008"
     },
     {
      "answer": "It's been in there long enough that a glance at bedtime doesn't register it anymore",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "The monitor cable runs down loose alongside the rail instead of being clipped up and back.",
    "branches": [
     {
      "answer": "It's a real strangling risk within reach of the rails, and that outranks how it looks",
      "cause": "KC-010"
     },
     {
      "answer": "It's been mounted that way since before your baby could reach, so it stopped reading as a risk",
      "cause": "RC-017"
     },
     {
      "answer": "The crib ended up close enough to the cable run that there was never a clean path to route it away from the rails",
      "cause": "KC-003"
     }
    ]
   },
   {
    "symptom": "The mattress is still set at the high position even though your baby can now pull up to stand.",
    "branches": [
     {
      "answer": "Nobody re-checked the setting once this new milestone made the old one unsafe",
      "cause": "KC-009"
     },
     {
      "answer": "It's a safety adjustment that outranks how much effort it takes to get to right now",
      "cause": "KC-010"
     },
     {
      "answer": "It's the kind of task each parent assumes the other one already handled",
      "cause": "RC-013"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Strip the crib down to the mattress and one fitted sheet. Anything else crossing the rail, a quilt, a plush toy, a muslin, a blanket, comes out now and goes to its real place: the keepsake box, the toy basket, or the wash.",
   "victory": "The crib holds a bare mattress with one fitted sheet pulled tight to the corners, and nothing else is inside the rails or draped over the top rail."
  }
 },
 "Changing Station": {
  "frictions": [
   {
    "symptom": "There's a lamp, a framed photo, or a mostly-full bottle of lotion sitting on the dresser top near the pad.",
    "branches": [
     {
      "answer": "Nobody ever decided this surface is only for what an actual change needs",
      "cause": "KC-008"
     },
     {
      "answer": "It has no assigned home of its own, so it lands on the nearest flat surface on the way past",
      "cause": "KC-002"
     },
     {
      "answer": "It's been sitting there so long it stopped registering as clutter on a work surface",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "There's a second, partial changing setup downstairs: a stack of diapers and no wipes, or wipes and no cream.",
    "branches": [
     {
      "answer": "Carrying the baby upstairs every time felt unbearable, so a shortcut version started without anyone deciding what it needed to include",
      "cause": "RC-015"
     },
     {
      "answer": "It doesn't restock on the same trigger as the real station, so it quietly drifts out of sync",
      "cause": "KC-009"
     },
     {
      "answer": "Whoever stocked it assumed someone else had already checked it matched the real station",
      "cause": "KC-012"
     }
    ]
   },
   {
    "symptom": "A wipe refill bag or the pail liner roll is sitting loose on top of the dresser instead of shut in a drawer.",
    "branches": [
     {
      "answer": "It's a real choking and suffocation risk sitting in reach, and that outranks convenience",
      "cause": "KC-010"
     },
     {
      "answer": "There's no assigned spot for the spare packaging once the drawer under the pad fills up with something else",
      "cause": "KC-002"
     },
     {
      "answer": "It only reads as clutter, not as a hazard, so it keeps getting deprioritized",
      "cause": "RC-017"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Clear the dresser top down to what your hand actually uses during a change: diapers, wipes, cream, a burp cloth. Everything else, and any loose plastic bag or roll sitting out, moves off the top or into a shut drawer.",
   "victory": "The pad surface and the dresser top around it hold only what a change needs, and nothing loose plastic is left where a hand could reach it."
  }
 },
 "Baby Clothing Zone": {
  "frictions": [
   {
    "symptom": "There's an outfit in the drawer with the tags still on, in a size your baby has already outgrown.",
    "branches": [
     {
      "answer": "It was a gift from someone who mattered, and letting it go feels like a small betrayal",
      "cause": "RC-014"
     },
     {
      "answer": "Nobody's applied the two-garments-per-size rule yet, so there's no limit forcing the choice",
      "cause": "KC-008"
     },
     {
      "answer": "The outgoing bag isn't within reach of the drawer, so it's an extra trip rather than a two-second drop-in",
      "cause": "KC-004"
     }
    ]
   },
   {
    "symptom": "Two different sizes are sitting in the same drawer, one of them from a few months back.",
    "branches": [
     {
      "answer": "The drawer front was labeled once and never treated as something to update, so it now describes last month, not today",
      "cause": "KC-008"
     },
     {
      "answer": "There's no specific moment that prompts a re-sort, so it happens whenever someone notices, which is later than the actual size change",
      "cause": "KC-009"
     },
     {
      "answer": "Whoever puts the laundry away isn't necessarily the one who would catch the sizing drift",
      "cause": "RC-013"
     }
    ]
   },
   {
    "symptom": "A hand-me-down cardigan or sleeper still has its decorative buttons, ribbon ties, or drawstring attached.",
    "branches": [
     {
      "answer": "Those trims are a real choking and strangling risk on anything a baby wears, and that comes off before the garment goes in a drawer, full stop",
      "cause": "KC-010"
     },
     {
      "answer": "On a hand-me-down, the trim reads as part of the garment rather than as something to remove",
      "cause": "RC-017"
     },
     {
      "answer": "There's no set moment, before it's washed, before it's filed, when anyone checks a hand-me-down for hazards",
      "cause": "KC-009"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Open every drawer, pull anything smaller than what your baby is wearing today, and put it straight into the outgoing bag on the door hook.",
   "victory": "Every drawer holds one size only, and the outgoing bag on the door has something in it."
  }
 },
 "Feeding Station": {
  "frictions": [
   {
    "symptom": "There are bottle parts or pump parts from a brand you've stopped using still sitting in the drawer or bin.",
    "branches": [
     {
      "answer": "There's never been an agreed test, a fixed number of tries before deciding, so 'give it a bit longer' never actually ends",
      "cause": "KC-008"
     },
     {
      "answer": "Trying every recommended option means the shelf now stores more systems than the household actually uses",
      "cause": "KC-001"
     },
     {
      "answer": "A brand that got refused once still hasn't been formally written off, so nobody feels safe throwing the spares out",
      "cause": "RC-015"
     }
    ]
   },
   {
    "symptom": "A used bottle or pump part is sitting in the same bin as the clean, assembled ones.",
    "branches": [
     {
      "answer": "There's no fixed moment, like the kitchen light going off, that this household has actually adopted yet for closing out the day's bottles",
      "cause": "KC-009"
     },
     {
      "answer": "Whoever closes the kitchen at night isn't always the one who fed the baby, so the two bins get crossed",
      "cause": "RC-013"
     },
     {
      "answer": "The two bins aren't different enough in color to catch a tired hand reaching for the wrong one",
      "cause": "KC-005"
     }
    ]
   },
   {
    "symptom": "A kettle, warmer, or sterilizer cord is coiled loosely on the counter instead of looped short and tucked behind the appliance.",
    "branches": [
     {
      "answer": "A cord within pulling reach next to boiling water is a real scald risk, ahead of anything about tidiness",
      "cause": "KC-010"
     },
     {
      "answer": "It's coiled that way every day, so the length of slack within reach stopped being something anyone notices",
      "cause": "RC-017"
     },
     {
      "answer": "Looping it short each time is one more step in an already one-handed routine, so it gets skipped under time pressure",
      "cause": "KC-004"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Sort every bottle, teat, and pump part on the counter. Anything cloudy, split, or from a brand you've stopped using goes in the bin, and the clean bin gets refilled with fully assembled, dry bottles.",
   "victory": "The clean bin holds only fully assembled, dry bottles and parts, and nothing used is mixed in with them."
  }
 },
 "Diaper and Care Backstock": {
  "frictions": [
   {
    "symptom": "There are more than two unopened packs of one diaper size on the shelf, in a size your baby is close to outgrowing.",
    "branches": [
     {
      "answer": "A deal made buying ahead feel like savings, so more came in than the two-pack ceiling allows",
      "cause": "KC-001"
     },
     {
      "answer": "There's no written cap on how many packs of one size to keep, so 'good deal' is the only rule currently operating",
      "cause": "KC-008"
     },
     {
      "answer": "Nobody's decided yet where the extra packs go, a friend, a diaper bank, so they just stay",
      "cause": "RC-015"
     }
    ]
   },
   {
    "symptom": "A heavy carton or pack is stored on a shelf above or beside the crib.",
    "branches": [
     {
      "answer": "Weight that can shift and fall into the sleep space outranks whatever convenience put it there",
      "cause": "KC-010"
     },
     {
      "answer": "The backstock shelf happens to be the closest flat surface to the crib, so overflow lands there by proximity, not by plan",
      "cause": "KC-003"
     },
     {
      "answer": "It's been stacked there since before the crib had a baby actually sleeping in it, so the arrangement never got re-examined",
      "cause": "RC-017"
     }
    ]
   },
   {
    "symptom": "A cream, teething gel, or infant medicine on the shelf is past its date, or its tube is split or swollen.",
    "branches": [
     {
      "answer": "Nothing prompts a date check except emptying the shelf to clean it, which doesn't happen often",
      "cause": "KC-009"
     },
     {
      "answer": "Consumables like this age out of use unseen, because nothing signals when one has gone past its date",
      "cause": "KC-011"
     },
     {
      "answer": "A lidded box that's rarely opened is also rarely looked at closely enough to catch a swollen tube",
      "cause": "RC-017"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Pull every pack off the shelf, read the printed size, and take anything smaller than today's size, opened or not, off the shelf. Move anything heavy off any shelf above or beside the crib.",
   "victory": "The shelf holds one unopened pack of the current size, no more than two packs of the next size, and nothing heavy sits above or beside the crib."
  }
 },
 "Books and Quiet Play Zone": {
  "frictions": [
   {
    "symptom": "A paper-page book or one of your own books is sitting on the low ledge within the baby's reach.",
    "branches": [
     {
      "answer": "It was chosen because you wanted to read it aloud, and moving it off the ledge can feel like giving up that plan",
      "cause": "RC-014"
     },
     {
      "answer": "Nobody's drawn the line yet that the low ledge is board-books-only, so anything book-shaped ends up there",
      "cause": "KC-008"
     },
     {
      "answer": "The split, your shelf versus the ledge, hasn't actually been made yet, so books default to wherever they were unpacked",
      "cause": "RC-015"
     }
    ]
   },
   {
    "symptom": "The soft toy basket is stacked well above its rim, with more spilling onto the floor beside it.",
    "branches": [
     {
      "answer": "There's no swap trigger, two out when two come in, so the basket only ever grows",
      "cause": "KC-009"
     },
     {
      "answer": "More toys keep arriving as gifts than the rotation system moves back out to the closet box",
      "cause": "KC-001"
     },
     {
      "answer": "Swapping toys into the rotation box isn't clearly anyone's job, so it only happens when someone happens to be tidying",
      "cause": "RC-013"
     }
    ]
   },
   {
    "symptom": "A light-up or musical toy's battery compartment opens without a screwdriver, or a soft toy has a loose stitched eye or a long ribbon tag.",
    "branches": [
     {
      "answer": "A battery compartment a baby can open, or a loose part that can detach, is a real choking risk that outranks keeping the toy",
      "cause": "KC-010"
     },
     {
      "answer": "A toy that's been on the shelf for months doesn't get re-inspected the way a brand-new one would",
      "cause": "RC-017"
     },
     {
      "answer": "There's no set check when a toy comes back from the wash the way there is for board books, so a loose eye can sit for a while before anyone notices",
      "cause": "KC-009"
     }
    ]
   }
  ],
  "first_15": {
   "action": "Move every paper-page book off the low ledge to a shelf in your own room, and swap the soft toy basket down to level with its rim, boxing the rest for the closet rotation.",
   "victory": "The low ledge holds only board books facing out, and the soft toy basket sits level with its rim, not above it."
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
 ("Crib and Sleep Zone", "NUF-001",
  "A QUILT IS DRAPED OVER THE RAIL, OR A PLUSH SITS AT THE FOOT OF THE "
  "MATTRESS",
  "a nursery crib with a folded quilt draped over the top rail and a "
  "plush toy sitting at the foot of an otherwise bare mattress"),
 ("Crib and Sleep Zone", "NUF-002",
  "THE MONITOR CABLE RUNS LOOSE ALONGSIDE THE RAIL",
  "a baby monitor cable hanging loose down the side of a crib rail "
  "instead of being clipped up and back against the wall"),
 ("Crib and Sleep Zone", "NUF-003",
  "THE MATTRESS IS STILL AT THE HIGH SETTING WHILE YOUR BABY PULLS UP TO "
  "STAND",
  "a nursery crib with its mattress fixed at the highest setting, the "
  "gap between the mattress top and the rail measuring only a hand's "
  "width"),

 ("Changing Station", "NUF-004",
  "A LAMP, A FRAMED PHOTO, OR A LOTION BOTTLE SITS ON THE DRESSER NEAR "
  "THE PAD",
  "a nursery dresser top beside a changing pad holding a lamp, a framed "
  "photo, and a mostly full lotion bottle crowding the surface"),
 ("Changing Station", "NUF-005",
  "A SECOND, PARTIAL CHANGING SETUP SITS DOWNSTAIRS",
  "a small stack of diapers sitting alone on a living room shelf with "
  "no wipes or cream anywhere nearby"),
 ("Changing Station", "NUF-006",
  "A WIPE REFILL BAG OR LINER ROLL SITS LOOSE ON TOP OF THE DRESSER",
  "a loose plastic wipe refill bag and a pail liner roll sitting out in "
  "the open on a nursery dresser top instead of shut inside a drawer"),

 ("Baby Clothing Zone", "NUF-007",
  "AN OUTFIT WITH THE TAGS STILL ON SITS IN AN OUTGROWN SIZE",
  "a baby outfit with its price tag still attached lying in an open "
  "dresser drawer among clothes in a noticeably smaller size"),
 ("Baby Clothing Zone", "NUF-008",
  "TWO DIFFERENT SIZES SHARE THE SAME DRAWER",
  "an open baby clothes drawer holding two visibly different sizes of "
  "sleepers filed together instead of separated by drawer"),
 ("Baby Clothing Zone", "NUF-009",
  "A HAND-ME-DOWN CARDIGAN STILL CARRIES ITS BUTTONS, TIES, OR "
  "DRAWSTRING",
  "a hand-me-down baby cardigan folded in a drawer still fitted with "
  "decorative buttons and a hood drawstring nobody has removed"),

 ("Feeding Station", "NUF-010",
  "BOTTLE OR PUMP PARTS FROM A RETIRED BRAND ARE STILL IN THE BIN",
  "a feeding station bin holding bottle and pump parts from three "
  "different makers crowded together, most of them unused for weeks"),
 ("Feeding Station", "NUF-011",
  "A USED PART SITS IN THE SAME BIN AS THE CLEAN, ASSEMBLED BOTTLES",
  "a bin of clean, fully assembled baby bottles with one visibly used, "
  "unwashed bottle part sitting mixed in among them"),
 ("Feeding Station", "NUF-012",
  "AN APPLIANCE CORD IS COILED LOOSE ON THE COUNTER INSTEAD OF TUCKED "
  "SHORT",
  "a kettle cord coiled loosely across a nursery feeding station counter "
  "within easy pulling reach instead of looped short behind the "
  "appliance"),

 ("Diaper and Care Backstock", "NUF-013",
  "MORE THAN TWO PACKS OF ONE SIZE CROWD THE SHELF",
  "a backstock shelf crowded with four or five unopened diaper packs "
  "all in the same size, stacked well past a two-pack depth"),
 ("Diaper and Care Backstock", "NUF-014",
  "A HEAVY CARTON SITS ON A SHELF ABOVE OR BESIDE THE CRIB",
  "a heavy diaper carton stacked on a shelf directly above a nursery "
  "crib, positioned to fall into the sleep space below"),
 ("Diaper and Care Backstock", "NUF-015",
  "A CREAM OR MEDICINE ON THE SHELF IS PAST ITS DATE, SPLIT, OR SWOLLEN",
  "a diaper cream tube sitting in a backstock box with its side visibly "
  "split and swollen, an expiry date stamped on its base"),

 ("Books and Quiet Play Zone", "NUF-016",
  "A PAPER-PAGE BOOK SITS ON THE LOW LEDGE WITHIN REACH",
  "a paper-page picture book standing on a low nursery book ledge among "
  "board books, its cover already showing a torn corner"),
 ("Books and Quiet Play Zone", "NUF-017",
  "THE TOY BASKET IS STACKED WELL ABOVE ITS RIM",
  "a soft toy basket overflowing well above its rim, toys spilling onto "
  "the floor around its base"),
 ("Books and Quiet Play Zone", "NUF-018",
  "A TOY'S BATTERY FLAP OPENS WITHOUT A SCREWDRIVER, OR A SOFT TOY HAS A "
  "LOOSE EYE",
  "a light-up nursery toy with its battery compartment flap hanging "
  "open beside a soft toy showing a loosened stitched eye"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, nursery-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a small cluster of bottle and pump parts from three "
           "different makers piled together in a nursery feeding bin, "
           "far more than the household still uses",
 "KC-002": "a lamp and a lotion bottle sitting on a nursery dresser top "
           "with no drawer or shelf assigned to either",
 "KC-003": "a heavy diaper carton sitting on a shelf close to a nursery "
           "crib because it was the nearest flat surface, not because "
           "it belongs there",
 "KC-004": "a hand reaching past a folded outfit toward a door hook bag "
           "on the far side of a nursery room to drop off an outgrown "
           "garment",
 "KC-005": "two nursery feeding bins standing side by side in nearly "
           "identical colors, easy to mix up at a glance",
 "KC-008": "a crib rail with a folded blanket draped over it, with no "
           "photograph or note anywhere nearby showing what the crib "
           "should look like",
 "KC-009": "a nursery mattress still bolted at its high setting, with "
           "no calendar mark or note anywhere nearby showing when to "
           "recheck it",
 "KC-010": "a monitor cable hanging loose within reach of a crib's "
           "rails, a real strangling risk sitting in plain view",
 "KC-011": "a nursery backstock shelf holding a single wipes carton "
           "with no visible count of what remains inside it",
 "KC-012": "a nursery changing station stocked halfway to two different "
           "standards, diapers arranged one way on one side and another "
           "way on the other",
 "RC-013": "a nursery mattress left at its old height setting, with no "
           "note anywhere showing which parent last checked it",
 "RC-014": "a hand-knitted baby quilt folded and kept on a shelf rather "
           "than inside the crib, clearly a keepsake rather than daily "
           "bedding",
 "RC-015": "three half-used bottles from different makers standing "
           "together on a nursery shelf, none of them thrown out and "
           "none of them in current use",
 "RC-017": "a folded blanket that has draped over the same crib rail "
           "for so long it blends into the room's everyday look",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Crib and Sleep Zone": [
  "Wipe the monitor housing and its bracket with a dry cloth, then run "
  "the same cloth down the clipped cable to lift the dust a still cord "
  "collects.",
  "Draw your palm down each crib slat, back and front, feeling for a "
  "rough edge or a split before you see one.",
  "Lift the mattress and wipe the support base and frame bolts "
  "underneath, the one moment they are actually visible.",
 ],
 "Changing Station": [
  "Wipe the changing pad into its contour seams, where wipe solution "
  "and cream pool out of sight.",
  "Pull the drawer beneath the pad all the way out and vacuum the sock "
  "lint and crusted cream lids from its corners.",
  "Wipe the lined pail's lid seal and hinge, where odor and a soft film "
  "build up unseen.",
 ],
 "Baby Clothing Zone": [
  "Empty one drawer completely and vacuum the sock lint and dried "
  "spit-up from its corners before anything goes back.",
  "Wipe both runners on an open drawer clean of lint and grit so it "
  "glides and closes flush again.",
  "Check the anti-tip strap where it meets the wall and the chest, and "
  "flag it if the screw has backed out.",
 ],
 "Feeding Station": [
  "Lift the drying rack off the counter and wipe underneath it, where "
  "drips pool and a ring of scale quietly forms.",
  "Run a cloth along each appliance cord, then coil it short again and "
  "set it back behind the appliance.",
  "Wipe the formula tin and its lid, and check the scoop is dry and "
  "shut inside before it goes back.",
 ],
 "Diaper and Care Backstock": [
  "Turn one carton over and check its underside for the damp softness "
  "that means a pack is wicking moisture from the floor.",
  "Wipe the sticky rings that cream tubes leave inside the lidded box "
  "before the tubes go back in.",
  "Run a dry hand along the wall behind the shelf, checking for the "
  "cold damp patch a sweating outside wall leaves.",
 ],
 "Books and Quiet Play Zone": [
  "Wipe each board book's chewed corners with a barely damp cloth, "
  "since this is a mouthing surface.",
  "Vacuum the soft-toy basket's interior and rim, where drool and dust "
  "collect in the weave.",
  "Vacuum under the low ledge and into the skirting behind it, the "
  "strip your baby rolls closest to.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-nursery actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "NUA-001", "zone": "Crib and Sleep Zone",
  "title": "STRIP THE CRIB TO ONE SHEET",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Strip the crib down to the mattress and one fitted sheet, "
          "sending everything else crossing the rail to its real place.",
  "why": "A crib loaded with a quilt, a plush toy, or a muslin is not "
         "decorated, it is a suffocation risk to a baby who cannot roll "
         "off any of them.",
  "inputs": ["the keepsake box", "the toy basket", "a laundry basket"],
  "steps": [
   "Strip the crib down to the mattress and one fitted sheet. Anything "
   "else crossing the rail, a quilt, a plush toy, a muslin, a blanket, "
   "comes out now and goes to its real place: the keepsake box, the toy "
   "basket, or the wash.",
   "Pull the fitted sheet tight to all four corners so nothing sits "
   "loose in the sleep space."],
  "causes": ["RC-014", "KC-008"],
  "victory": "The crib holds a bare mattress with one fitted sheet "
             "pulled tight to the corners, and nothing else is inside "
             "the rails or draped over the top rail.",
  "next": "NUS-001",
  "art": "a nursery crib mid-strip, a folded quilt and a plush toy being "
         "carried out in a laundry basket, one fitted sheet left pulled "
         "tight to the mattress corners"},

 {"id": "NUA-002", "zone": "Crib and Sleep Zone",
  "title": "DROP THE MATTRESS AND CLEAR THE CORD PATH",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Drop the mattress to its lowest setting and clear every cord "
          "reachable from inside the rails.",
  "why": "The day your baby can push up onto hands and knees, a high "
         "mattress puts the rail below chest height, and a blind or "
         "monitor cord within reach of the slats is a strangling risk "
         "that does not wait for a convenient time to fix.",
  "inputs": ["a screwdriver if the frame needs it", "cable clips",
             "a step stool"],
  "steps": [
   "Drop the mattress to its lowest setting the day your baby can push "
   "up onto hands and knees, because the next thing they learn is "
   "pulling to stand.",
   "Move the crib clear of the blind cord, the lamp flex, and the "
   "monitor cable; find any cord reachable from inside the rails and "
   "shorten or clip it out of reach today.",
   "Recheck the gap between the mattress top and the rail with your own "
   "hand, not by eye alone."],
  "causes": ["KC-010", "KC-009", "RC-013", "KC-003"],
  "victory": "The mattress sits at the lowest setting once your baby can "
             "push up onto hands and knees, and no cord is reachable "
             "from inside the rails.",
  "next": "NUA-001",
  "art": "a hand lowering a crib mattress to its base setting, a monitor "
         "cable clipped high and back against the wall well clear of "
         "the rails"},

 {"id": "NUA-003", "zone": "Changing Station",
  "title": "CLEAR THE DRESSER TOP TO WHAT A CHANGE NEEDS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the dresser top down to what your hand actually uses "
          "during a change, and shut away every loose bag or roll.",
  "why": "A lamp or a lotion bottle sitting near the pad is not decor, "
         "it is one more thing to knock into a full basin or a bare "
         "baby mid-change.",
  "inputs": ["a small box for items that belong elsewhere",
             "a drawer to shut loose plastic into"],
  "steps": [
   "Clear the dresser top down to what your hand actually uses during a "
   "change: diapers, wipes, cream, a burp cloth. Everything else, and "
   "any loose plastic bag or roll sitting out, moves off the top or "
   "into a shut drawer.",
   "Set diapers on the side your dominant hand lands, wipes beside "
   "them, and cream where your thumb can flip the cap without looking."],
  "causes": ["KC-008", "KC-002"],
  "victory": "The pad surface and the dresser top around it hold only "
             "what a change needs, and nothing loose plastic is left "
             "where a hand could reach it.",
  "next": "NUS-002",
  "art": "a nursery changing station dresser top mid-clear, a lamp and a "
         "lotion bottle being carried off, diapers, wipes and cream "
         "left standing within arm's reach of the pad"},

 {"id": "NUA-004", "zone": "Changing Station",
  "title": "ANCHOR THE DRESSER AND LOCK AWAY THE LOOSE PLASTIC",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Anchor the dresser to the wall and move every wipe refill bag "
          "and pail liner roll into a shut drawer.",
  "why": "A roll off an unanchored dresser is a fall from adult waist "
         "height, and a loose plastic bag within reach of a hand on the "
         "pad is a suffocation risk that has nothing to do with "
         "tidiness.",
  "inputs": ["an anti-tip wall strap", "a screwdriver",
             "a drawer to spare"],
  "steps": [
   "Fit the dresser with an anti-tip wall strap or bracket if it does "
   "not already have one, and check the fixing holds when you lean on "
   "the open pad.",
   "Move the wipe refill bags and the pail liner roll into a drawer "
   "that shuts, never left loose on top.",
   "If a second, partial changing setup exists elsewhere in the house, "
   "mirror this station's exact counts and restock trigger, or fold it "
   "into a single caddy carried down and back rather than running two "
   "different designs."],
  "causes": ["KC-010", "KC-002", "KC-012"],
  "victory": "The dresser is anchored to the wall, and no loose plastic "
             "bag or roll sits on top where a hand could reach it.",
  "next": "NUA-003",
  "art": "a hand fitting an anti-tip strap between a nursery dresser and "
         "the wall, a drawer beside it holding the wipe refill bags and "
         "liner roll shut away"},

 {"id": "NUA-005", "zone": "Baby Clothing Zone",
  "title": "PULL THE OUTGROWN SIZE INTO THE OUTGOING BAG",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Open every drawer, pull anything smaller than today's size, "
          "and put it straight into the outgoing bag on the door hook.",
  "why": "An outgrown outfit does not get smaller by staying in the "
         "drawer, and a full outgoing bag is the only sign this zone is "
         "actually working.",
  "inputs": ["the outgoing bag on the door hook", "the keepsake box"],
  "steps": [
   "Open every drawer, pull anything smaller than what your baby is "
   "wearing today, and put it straight into the outgoing bag on the "
   "door hook.",
   "Set aside no more than two garments per outgrown size for the "
   "keepsake box; everything else in that size leaves in the bag."],
  "causes": ["RC-014", "KC-008", "KC-004"],
  "victory": "Every drawer holds one size only, and the outgoing bag on "
             "the door has something in it.",
  "next": "NUS-003",
  "art": "an open baby dresser drawer holding one size only, a hand "
         "dropping a smaller outgrown outfit into an outgoing bag "
         "hanging on the door hook"},

 {"id": "NUA-006", "zone": "Baby Clothing Zone",
  "title": "ANCHOR THE CHEST AND STRIP THE HAZARD TRIMS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Bolt the chest of drawers to the wall and cut off every "
          "decorative button, ribbon tie, and drawstring from hand-me-"
          "down clothing before it goes in a drawer.",
  "why": "An unanchored chest with two drawers open is a ladder and a "
         "tip-over risk the moment your baby is climbing, and a hood "
         "drawstring or a decorative button comes off in a mouth or "
         "around a neck.",
  "inputs": ["an anti-tip strap or bracket", "a screwdriver",
             "small scissors"],
  "steps": [
   "Bolt the chest of drawers to the wall if it is not anchored "
   "already, and confirm you never leave two drawers open at once.",
   "Go through every hand-me-down cardigan or sleeper and cut off "
   "decorative buttons, ribbon ties, and hood drawstrings before the "
   "garment goes in a drawer.",
   "Re-check the next-size bin on the closet shelf for the same "
   "hazards, since gifts in bigger sizes skip the drawer entirely."],
  "causes": ["KC-010"],
  "victory": "The chest of drawers is anchored to the wall, and no "
             "hand-me-down garment in a drawer or the next-size bin "
             "still carries a decorative button, ribbon tie, or "
             "drawstring.",
  "next": "NUA-005",
  "art": "a hand bolting a chest of drawers to a nursery wall, a small "
         "pair of scissors beside a hand-me-down cardigan with its hood "
         "drawstring already removed"},

 {"id": "NUA-007", "zone": "Feeding Station",
  "title": "SORT THE BOTTLES AND REFILL THE CLEAN BIN",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Sort every bottle, teat, and pump part on the counter, and "
          "refill the clean bin with only fully assembled, dry bottles.",
  "why": "A cloudy, split teat or a part from a brand you have stopped "
         "using does not improve by staying in the drawer, it just "
         "takes up space the clean bin needs at 2 a.m.",
  "inputs": ["a bin bag", "the drying rack"],
  "steps": [
   "Sort every bottle, teat, and pump part on the counter. Anything "
   "cloudy, split, or from a brand you've stopped using goes in the "
   "bin, and the clean bin gets refilled with fully assembled, dry "
   "bottles.",
   "Set the two bins in visibly different colors, so a tired hand "
   "cannot mix up clean with used."],
  "causes": ["KC-008", "KC-001", "KC-005"],
  "victory": "The clean bin holds only fully assembled, dry bottles and "
             "parts, and nothing used is mixed in with them.",
  "next": "NUS-004",
  "art": "a nursery feeding station counter with cloudy and split "
         "bottle teats being sorted into a bin bag, a clean bin "
         "refilled with fully assembled, dry bottles beside an empty "
         "drying rack"},

 {"id": "NUA-008", "zone": "Feeding Station",
  "title": "SHORTEN THE CORDS AND SEPARATE WATER FROM POWER",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Loop every kettle, warmer, and sterilizer cord short behind "
          "the appliance, and keep water well clear of every socket and "
          "plug.",
  "why": "A kettle sits at roughly the changing pad's height, so a "
         "pulled cord brings scalding water down at child height, and a "
         "water jug standing beside a live socket puts current and "
         "water on the same surface.",
  "inputs": ["cable ties or clips", "a cloth for drying the surface"],
  "steps": [
   "Loop every kettle, warmer, and sterilizer cord short and run it "
   "behind the appliance, out of pulling reach.",
   "Move the water jug and the wet drying rack well clear of the "
   "sterilizer socket and the monitor plug.",
   "Wipe the counter dry under and around every appliance before you "
   "finish."],
  "causes": ["KC-010"],
  "victory": "Every appliance cord is looped short behind its "
             "appliance, and no water source stands beside a live "
             "socket or plug.",
  "next": "NUA-007",
  "art": "a kettle cord looped short and clipped behind a nursery "
         "feeding station appliance, a water jug standing well clear of "
         "the wall socket beside it"},

 {"id": "NUA-009", "zone": "Diaper and Care Backstock",
  "title": "PULL THE WRONG SIZES OFF THE SHELF",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull every pack off the shelf, read the printed size, and "
          "take anything smaller than today's size off, along with "
          "anything heavy stored above the crib.",
  "why": "A pack in a size your baby has already outgrown is not "
         "backstock, it is dead stock taking up the shelf the next size "
         "needs, and a heavy carton above the crib is a fall risk into "
         "the sleep space.",
  "inputs": ["a bag or box for the outgrown packs",
             "somewhere else to move heavy cartons"],
  "steps": [
   "Pull every pack off the shelf, read the printed size, and take "
   "anything smaller than today's size, opened or not, off the shelf. "
   "Move anything heavy off any shelf above or beside the crib.",
   "Decide today where the outgrown packs go: a friend, a diaper bank, "
   "or the bin, and get them out of the room."],
  "causes": ["KC-001", "KC-008"],
  "victory": "The shelf holds one unopened pack of the current size, no "
             "more than two packs of the next size, and nothing heavy "
             "sits above or beside the crib.",
  "next": "NUS-005",
  "art": "a nursery backstock shelf mid-sort, outgrown diaper packs "
         "being pulled off into a donation box, one unopened pack of "
         "the current size and two of the next left standing"},

 {"id": "NUA-010", "zone": "Diaper and Care Backstock",
  "title": "CLEAR THE SHELF ABOVE THE CRIB AND LOCK AWAY THE CREAMS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Move every heavy item off any shelf above or beside the crib "
          "for good, and box the creams, gels, and medicine where a "
          "standing toddler cannot open them.",
  "why": "A carton that works its way off a shelf above the crib lands "
         "exactly where your baby sleeps, and a swallowed diaper cream "
         "or teething gel is a poisoning risk the moment your baby can "
         "reach the surface edge.",
  "inputs": ["a lidded, latching box",
             "somewhere else to store heavy cartons"],
  "steps": [
   "Confirm nothing heavy sits on a shelf above or beside the crib, and "
   "move anything that does to a shelf well away from the sleep space.",
   "Put every cream, teething gel, and infant medicine into one closed "
   "box a standing toddler cannot open, and check the dates on each as "
   "you go.",
   "Bin anything past its date or showing a split or swollen tube."],
  "causes": ["KC-010", "KC-011", "KC-003"],
  "victory": "No shelf above or beside the crib holds anything heavy, "
             "and every cream, gel, and medicine sits inside a closed "
             "box out of a standing child's reach.",
  "next": "NUA-009",
  "art": "a hand closing a latching box holding diaper creams and a "
         "thermometer, a bare shelf visible above an empty nursery crib "
         "in the background"},

 {"id": "NUA-011", "zone": "Books and Quiet Play Zone",
  "title": "MOVE THE PAPER BOOKS OFF THE LEDGE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Move every paper-page book off the low ledge to a shelf in "
          "your own room, and swap the soft toy basket down to level "
          "with its rim.",
  "why": "A paper-page book on a low ledge gets chewed into pulp within "
         "a week, and a basket piled above its rim just means the "
         "overflow lands on the floor next.",
  "inputs": ["a shelf in another room for the paper books",
             "the rotation box in the closet"],
  "steps": [
   "Move every paper-page book off the low ledge to a shelf in your own "
   "room, and swap the soft toy basket down to level with its rim, "
   "boxing the rest for the closet rotation.",
   "Stand the twelve remaining board books cover out along the ledge so "
   "a pre-reader can choose by picture."],
  "causes": ["RC-014", "KC-008"],
  "victory": "The low ledge holds only board books facing out, and the "
             "soft toy basket sits level with its rim, not above it.",
  "next": "NUS-006",
  "art": "a low nursery book ledge mid-sort, a paper-page picture book "
         "being carried out to another room, twelve board books left "
         "standing cover out along the ledge"},

 {"id": "NUA-012", "zone": "Books and Quiet Play Zone",
  "title": "BOLT THE LEDGE AND CLEAR THE BATTERY HAZARDS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Fix the low shelf or ledge to the wall, and remove any toy "
          "with a battery flap that opens without a screwdriver or a "
          "stitched part working loose.",
  "why": "The day your baby pulls to standing, an unfixed shelf becomes "
         "the nearest handhold and comes down on top of them, and a "
         "loose button battery or a stitched eye is a choking risk at "
         "floor level.",
  "inputs": ["wall anchors", "a screwdriver",
             "a bag for toys pulled from rotation"],
  "steps": [
   "Bolt the low shelf or ledge to the wall if it is not fixed already.",
   "Check every light-up or musical toy's battery compartment, and "
   "pull any that opens without a screwdriver from the rotation "
   "entirely.",
   "Check every soft toy for a loose stitched eye, a split seam, or a "
   "long ribbon tag, and pull anything that fails from the basket."],
  "causes": ["KC-010"],
  "victory": "The low ledge is fixed to the wall, and no toy in the "
             "basket or rotation box has an open-access battery "
             "compartment or a loose part.",
  "next": "NUA-011",
  "art": "a hand fixing a low nursery book ledge to the wall with a "
         "wall anchor, a light-up toy with its battery compartment "
         "checked sitting beside a soft toy basket at floor level"},

 {"id": "NUA-013", "zone": None,
  "title": "THE FULL NURSERY HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking for a reachable cord, a chemical or "
          "medicine within a child's reach, an unanchored piece of "
          "furniture, and anything heavy stored above the crib.",
  "why": "This room's own rule is that safety outranks everything else, "
         "and the hazards spread across six different zones only get "
         "found together if someone walks the whole room on purpose.",
  "inputs": ["a screwdriver", "an anti-tip strap", "a lidded box"],
  "steps": [
   "Check the crib and the feeding station for any cord reachable from "
   "inside the rails or near a socket, and clip or shorten it.",
   "Check the changing station, the clothing zone, and the books zone "
   "for an unanchored dresser, chest, or shelf, and confirm each is "
   "bolted to the wall.",
   "Check the backstock shelf and the changing station drawer for a "
   "cream, medicine, or loose plastic within a standing child's reach, "
   "and box or latch it away."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No cord sits reachable from a crib or a socket, every "
             "dresser, chest, and shelf is anchored to the wall, and no "
             "chemical, medicine, or loose plastic sits within a "
             "child's reach.",
  "next": "NUE-001",
  "art": "a hand checking an anti-tip strap on a nursery chest of "
         "drawers, a monitor cable clipped high and back against the "
         "wall visible beyond"},

 {"id": "NUA-014", "zone": None, "title": "THE BUYING-AHEAD AUDIT",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Walk the clothing zone, the backstock shelf, and the feeding "
          "station checking that nothing has been bought further ahead "
          "than the room's own rule allows: two garments a size, two "
          "packs a size, one system given three honest feeds.",
  "why": "Babies skip sizes and reject brands without warning, and "
         "buying ahead is the one trap this room's own intro names by "
         "name: diapers in the next size, clothes for next winter, a "
         "second bottle brand in case the first fails.",
  "inputs": ["the outgoing bag", "a diaper bank or friend to give "
             "extras to"],
  "steps": [
   "Check the clothing zone for more than two garments kept in any "
   "outgrown size, and send the rest out in the outgoing bag today.",
   "Check the backstock shelf for more than two packs of any one "
   "diaper size, and give away or use down anything past that line.",
   "Check the feeding station for more bottle or pump systems than the "
   "household actually uses, and retire any that failed the three-feed "
   "test."],
  "causes": ["KC-001", "RC-015"],
  "victory": "No zone in the room holds more than the stated limit: two "
             "garments a size, two packs a size, and no system still "
             "kept after failing its own three-feed test.",
  "next": "NUA-015",
  "art": "a hand comparing a shelf of diaper packs against a marked "
         "two-pack line, an outgoing bag and a donation box standing "
         "ready beside it"},

 {"id": "NUA-015", "zone": None, "title": "THE 2 A.M. READINESS CHECK",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "The last thing before you go to bed, walk every zone and "
          "confirm it already meets its own standard, so a night waking "
          "meets a room that is already ready.",
  "why": "Every standard in this room is built for the person working "
         "one-handed at 2 a.m., and the only way that promise holds is "
         "if someone actually checks it the night before, not the night "
         "it fails.",
  "inputs": ["nothing, this is a walk-through"],
  "steps": [
   "Check the crib for a bare mattress and one sheet, and the changing "
   "station for diapers, wipes, and cream all within reach.",
   "Check the feeding station for the clean bin stocked and the "
   "backstock shelf for one pack of the current size standing at the "
   "front.",
   "Check the books ledge and toy basket sit at their standard, since a "
   "stumble over a spilled basket in the dark is its own kind of 2 a.m. "
   "problem."],
  "causes": ["KC-009", "RC-013", "RC-017"],
  "victory": "Every zone in the room meets its own written standard at "
             "the moment you check it, the last thing before bed.",
  "next": "NUA-013",
  "art": "a hand doing a last-check pass across a settled nursery, a "
         "clean changing station, a stocked feeding bin and a bare crib "
         "all visible in one dim room"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a nursery, one per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("NUE-001", "THE NIGHT A VISITING GRANDPARENT PUTS THE BABY DOWN",
  "A grandparent who has never put your baby down before offers to do "
  "the night's last settle, working from whatever the crib actually "
  "shows them.",
  ["NUZ-001"],
  "The crib holds a bare mattress with one fitted sheet, and the "
  "photographed standard taped inside the closet door tells them "
  "exactly what belongs and what doesn't, no question needed.",
  "If they had to ask what to do with the folded quilt on the rail, the "
  "standard was never photographed or the crib was never reset since "
  "the last laundry day. Draw NUA-002.",
  "a hand taping a photograph of a settled crib inside a nursery closet "
  "door, a bare mattress with one fitted sheet visible in the crib "
  "beyond"),
 ("NUE-002", "THE CHANGE THAT HAPPENS ONE-HANDED IN THE DARK",
  "Your baby wakes at 3 a.m. and the whole change has to happen with "
  "one hand, in low light, without a single extra step.",
  ["NUZ-002"],
  "Diapers, wipes, and cream are all reachable with your feet planted "
  "and one hand still on your baby, and the pail is one step away.",
  "If you had to lift your hand off your baby to reach something, the "
  "dresser top was never cleared to arm's-sweep distance. Draw "
  "NUA-003.",
  "a hand reaching diapers and wipes from within arm's reach of a "
  "changing pad in a dimly lit nursery"),
 ("NUE-003", "THE MORNING A SNAP WON'T CLOSE",
  "You go to dress your baby and a snap won't close over the diaper, on "
  "a morning you are already running late.",
  ["NUZ-003"],
  "The next size up is already filed one drawer down, sized and "
  "labeled, so dressing your baby costs one drawer, not a search.",
  "If you had to hunt through mixed sizes to find something that fit, "
  "the outgrown garment never made it into the outgoing bag when the "
  "last snap failed. Draw NUA-005.",
  "a hand pulling a correctly sized outfit from a labeled dresser "
  "drawer on a rushed morning"),
 ("NUE-004", "THE 2 A.M. BOTTLE",
  "Your baby is crying for a bottle at 2 a.m. and whoever is up has to "
  "assemble one without turning on the overhead light.",
  ["NUZ-004"],
  "The clean bin holds four fully assembled bottles, teat and collar "
  "already on, so the whole job is one grab.",
  "If you had to hunt for a matching collar or a dry teat, the clean "
  "bin was never refilled when the kitchen light went off. Draw "
  "NUA-007.",
  "a hand lifting a fully assembled bottle from a clean bin in a dim "
  "kitchen at night"),
 ("NUE-005", "THE LAST DIAPER IN THE PACK",
  "The last diaper comes out of an open pack during a change, with no "
  "time to go looking for more.",
  ["NUZ-005"],
  "One unopened pack of the current size already stands at the front "
  "of the shelf, ready before you need it.",
  "If the shelf only had the wrong size or none at all, the reserve "
  "never moved forward when the last open pack ran out. Draw NUA-009.",
  "a hand pulling one unopened diaper pack from the front of a "
  "backstock shelf"),
 ("NUE-006", "THE DAY A NEW TOY ARRIVES",
  "A grandparent visits with a new stuffed toy and hands it straight to "
  "your baby on the play floor.",
  ["NUZ-006"],
  "The basket sits exactly at its rim, so the new toy has a place, and "
  "two older toys swap into the rotation box the same day.",
  "If the basket was already piled above its rim, the two-out-two-in "
  "swap has not happened in a while. Draw NUA-011.",
  "a hand placing a new soft toy into a basket sitting level with its "
  "rim, two older toys already set aside for the rotation box"),
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
        "related": {"standard": f"NUS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your nursery, "
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
    standard_id = (f"NUS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"NUS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "NUR-001", "title": "THE NURSERY", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START WITH THE CRIB BEFORE YOU TOUCH "
                   "ANYTHING ELSE.",
        "objective": "The nursery is the room where safety outranks "
                     "everything else, and where the person using it is "
                     "usually exhausted and working one-handed. This "
                     "card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"NUZ-001 Crib and Sleep Zone. {start_tip['text']}"
            if start_tip else
            "NUZ-001 Crib and Sleep Zone. It takes one armful of work "
            "and changes how the whole room reads."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your nursery. Put the rest back.",
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
        "safety_first": "Do NUA-013 The Full Nursery Hazard Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "the cord beside the crib, the unanchored "
                        "furniture across every zone, and the chemicals "
                        "and medicine on the backstock shelf.",
        "related": {"contents": "NUZ-001 to NUZ-006, NUF-001 to "
                                 "NUF-018, the shared root causes in "
                                 "ops/root_causes.py, NUA-001 to "
                                 "NUA-015, NUS-001 to NUS-006, NUE-001 "
                                 "to NUE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole nursery "
                           "in its settled state, a bare crib, a "
                           "changing station with everything within arm "
                           "reach, a clothing chest with labeled "
                           "drawers, a feeding station, a backstock "
                           "shelf and a low book ledge all visible in "
                           "one frame",
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
    return {"deck": "nursery", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (ops/cardtext/build_entryway_deck.py,
    ops/cardtext/build_guest_bathroom_deck.py)."""
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

    assert any(c["id"] == "NUA-013" for c in cards), "no safety walk card"
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
    print(f"  deck        nursery ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
