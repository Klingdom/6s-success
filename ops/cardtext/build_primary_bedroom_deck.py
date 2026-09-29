#!/usr/bin/env python3
"""
Build the Primary Bedroom deck: 66 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-TYPED DECK
------------------------------------------------
BACKLOG-2026-09-07.md B9: seventeen rooms already carry a full diagnosis
layer and a shipped deck (Entryway, Kitchen, Pantry, Dining Room, Primary
Bathroom, Laundry Room, Home Office, Garage, Hall Closet, Stair Landing,
Guest Bedroom, Guest Bathroom, Family Room, Living Room, Mudroom, Nursery,
Kids Bedroom, by the time this file was written). Primary Bedroom is the
next room built the same way: rich, hand-authored Manual content for all
six zones (purpose, done_looks_like, passes, the_call, watch_for,
leave_behind, shine_detail), and a diagnosis layer already authored into
content/manual/source/content.json (eighteen frictions, fifty-four
branches, six first_15 actions) by a separate pass this file does not
redo. This file only reads that layer and builds the deck straight off
it, the same shape ops/cardtext/build_kids_bedroom_deck.py already uses
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
twelve zone-linked action cards, the three whole-room actions, the event
cards, the micro quests, and the room card. The root causes are not
reauthored: they are the same frozen vocabulary in ops/root_causes.py that
every other room's deck already uses, so a household owning more than one
deck keeps one diagnosis pile rather than several (DECK-GAME-DESIGN.md
4.3). Fourteen of the seventeen shared ids are reachable from this room's
real frictions, counted honestly from the branches actually written below,
not chosen first and filled in: KC-001, KC-002, KC-003, KC-005, KC-007,
KC-008, KC-009, KC-010, KC-011, KC-012, RC-013, RC-014, RC-015, RC-017.
Three are not reachable, and each is a true statement about this room's
own frictions, not an oversight:

KC-004 (excess motion) is not reachable because nothing in the real
diagnosis branches is about extra steps or unstacking to reach something
already stored correctly; the room's real motion costs (the second,
downstairs setup a Nursery zone has, for instance) belong to other rooms'
decks, not this one's actual friction text.

KC-006 (poor accessibility) is not reachable because nothing in the real
diagnosis branches is about a person who cannot physically reach something
safely; every hazard in this room's own frictions is about a thing placed
somewhere unsafe (a cord in reach, an unstrapped dresser), not about a
user unable to reach a thing that is stored correctly.

RC-016 (difficult to clean) is not reachable because, unlike Guest
Bathroom's grout or Kitchen's cooktop, nothing in the Primary Bedroom's
real frictions is a surface that resists being reached and wiped; the
shine layer is thorough (behind the headboard, the gap behind the
dresser, the runners under each drawer) but the frictions branch to what
is stored wrong or unchecked, not to what is hard to clean.

WHAT THE BUDGET IS AND WHY
---------------------------
Primary Bedroom ships as a free typeset page, the same stage every prior
room in this line shipped at before any print-on-demand decision existed.
The budget below is six real zones, eighteen frictions (three per zone),
fourteen reachable root causes, fifteen action cards (two per zone plus
three whole-room), six standard cards and six event cards. 66 cards in
total, not padded or trimmed to match any other room's count: fourteen
causes matches Nursery's own count, arrived at independently from this
room's own real frictions, not copied from it.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior generator in this line keeps.

Run:  python ops/cardtext/build_primary_bedroom_deck.py
Out:  ops/cardtext/primary-bedroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "primary-bedroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Primary Bedroom"

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
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-005", "KC-007", "KC-008",
             "KC-009", "KC-010", "KC-011", "KC-012", "RC-013", "RC-014",
             "RC-015", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Bed and Bedding Zone": {
  "id": "PRZ-001", "order": 1, "difficulty": 2,
  "tagline": "TWO SHEET SETS. ONE ON, ONE CLEAN. NOTHING ELSE ON THE SHELF.",
  "callouts": [
   "A made bed holding a fitted sheet, a flat sheet or duvet, and two "
   "sleeping pillows per person",
   "One throw folded at the foot of the bed",
   "Two complete sheet sets for this bed, one on it and one folded on "
   "the linen shelf",
   "Under the bed holding either nothing or two labelled flat bins",
   "A clear floor on both sides of the bed all the way to the door",
   "A headboard shelf holding nothing but the lamp",
  ],
  "art": ("a primary bedroom bed made with a fitted sheet, a flat sheet "
          "or duvet, two pillows per side, and one throw folded at the "
          "foot, a clear floor on both sides leading to the door, and a "
          "headboard shelf holding only a lamp"),
 },
 "Nightstand Left": {
  "id": "PRZ-002", "order": 2, "difficulty": 1,
  "tagline": "FIVE THINGS OR FEWER. COUNTABLE FROM THE DOORWAY.",
  "callouts": [
   "A lamp, a lidded bottle or coaster, one book, and a small dish "
   "holding glasses, all on top",
   "Five things or fewer on the top, countable from the doorway",
   "No cable crossing the top surface",
   "A drawer with three divided sections, each with room left in it",
   "The lamp and clock cords clipped down the back leg",
   "The power strip moved off the top and onto the floor behind the "
   "nightstand",
  ],
  "art": ("a primary bedroom nightstand top holding a lamp, a lidded "
          "bottle, one book, and a small dish of reading glasses, five "
          "items in total, with the lamp cord clipped down the back leg "
          "and no cable crossing the top"),
 },
 "Nightstand Right": {
  "id": "PRZ-003", "order": 3, "difficulty": 2,
  "tagline": "YOU CLEAN. THEY CULL. MEDICATION IS THE ONE EXCEPTION.",
  "callouts": [
   "A top clear enough to set a mug down without moving anything first",
   "The lamp cord running behind the leg, not across the floor beside "
   "the bed",
   "Medication in the drawer capped and in date",
   "Medication closed away from a child or a dog that can climb onto "
   "the bed",
   "The same item count on this top as the other nightstand",
   "A floor beside this nightstand kept clear, the same as the other "
   "side",
  ],
  "art": ("a primary bedroom's second nightstand with a clear top, a "
          "capped medication bottle visible inside a slightly open "
          "drawer, and a lamp cord running down behind the leg rather "
          "than across the floor"),
 },
 "Dresser Top": {
  "id": "PRZ-004", "order": 4, "difficulty": 2,
  "tagline": "ONE TRAY. EVERYTHING FROM YOUR POCKETS LANDS INSIDE IT.",
  "callouts": [
   "One valet tray holding keys, wallet, watch and rings, with nothing "
   "sitting outside it",
   "Fragrance bottles grouped on a small dish, set back from the front "
   "edge",
   "No folded laundry resting on the dresser top",
   "No receipts or loose coins on the bare wood",
   "An anti-tip strap running from the back of the dresser into the "
   "wall",
   "A dresser top with nothing else on the bare wood besides the tray "
   "and the dish",
  ],
  "art": ("a primary bedroom dresser top holding one valet tray with "
          "keys, a wallet, a watch and rings, a small dish of fragrance "
          "bottles set back from the front edge, and bare wood "
          "everywhere else, with an anti-tip strap visible running from "
          "the back of the dresser into the wall"),
 },
 "Dresser Drawers": {
  "id": "PRZ-005", "order": 5, "difficulty": 3,
  "tagline": "ONE CATEGORY PER DRAWER. A HAND'S WIDTH OF SPACE LEFT.",
  "callouts": [
   "Each drawer holding one category: underwear and socks, sleepwear, "
   "t-shirts, workout clothes",
   "Clothes folded to stand upright, readable from above when the "
   "drawer opens",
   "A hand's width of free space in each drawer",
   "Every drawer sliding shut without being pressed down",
   "The heaviest categories, jeans and knitwear, in the bottom drawers",
   "Mothballs or cedar blocks sealed inside a mesh bag rather than "
   "rolling loose",
  ],
  "art": ("an open primary bedroom dresser drawer with clothes folded "
          "upright in a single category, a hand's width of empty space "
          "at the front, and the drawer beneath sliding fully shut"),
 },
 "Primary Closet": {
  "id": "PRZ-006", "order": 6, "difficulty": 4,
  "tagline": "TWO FINGERS OF SPACE. ONE IN, ONE OUT.",
  "callouts": [
   "One hanger style throughout, every hook facing the same way",
   "Garments grouped by type and then by shade",
   "Shoes in pairs on a rack, not heaped on the floor",
   "Bags standing upright on the shelf, belts on one hook",
   "Two fingers of space between hanging items, and a bare stretch of "
   "rod at one end",
   "A clear closet floor you can stand on",
  ],
  "art": ("a primary closet with one hanger style throughout, garments "
          "grouped by type and shade, shoes in pairs on a rack, bags "
          "standing upright on a shelf, and a clear stretch of floor "
          "beneath"),
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
 "Bed and Bedding Zone": {
  "frictions": [
   {
    "symptom": "There are three or more sheet sets stacked on the linen shelf, including the good set you have never actually put on the bed.",
    "branches": [
     {"answer": "One was a wedding gift and letting it go feels like refusing the person who gave it", "cause": "RC-014"},
     {"answer": "The honest number is one on, one clean, but nobody has ever said that out loud as the rule", "cause": "KC-008"},
     {"answer": "A set that has stood on the shelf that long stops registering as more than the bed actually needs", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "There is a storage bin, a pair of shoes, or a charging cable sitting in the strip of floor between the bed and the door.",
    "branches": [
     {"answer": "The cable has nowhere else it is supposed to live once it reaches this side of the room", "cause": "KC-002"},
     {"answer": "It is what your foot finds at three in the morning, and that risk outranks the two seconds it takes to leave it there", "cause": "KC-010"},
     {"answer": "Nothing marks the moment to clear that strip, so it only gets checked once someone trips", "cause": "KC-009"}
    ]
   },
   {
    "symptom": "A stack of books, a speaker, or a framed picture sits on a headboard shelf directly above the pillows.",
    "branches": [
     {"answer": "It is weight sitting right over a sleeping head, and that outranks how it looks on the shelf", "cause": "KC-010"},
     {"answer": "Nobody has decided the shelf above the pillows is off limits to anything but the lamp", "cause": "KC-008"},
     {"answer": "It has been up there since before anyone thought about what is underneath it, so the height stopped reading as a hazard", "cause": "RC-017"}
    ]
   }
  ],
  "first_15": {
   "action": "Clear the floor strip between the bed and the door of anything sitting on it, and move any headboard-shelf item that is not the lamp off the shelf.",
   "victory": "The floor strip between the bed and the door is bare, and the headboard shelf above the pillows holds only the lamp."
  }
 },
 "Nightstand Left": {
  "frictions": [
   {
    "symptom": "The phone is charging on the nightstand top and doubles as your alarm clock.",
    "branches": [
     {"answer": "There is never a specific moment, a birthday or a new year, that turns buying the clock into something that actually happens", "cause": "KC-009"},
     {"answer": "The charger has no other assigned spot in the room, so it stayed exactly where it was first plugged in", "cause": "KC-002"},
     {"answer": "It has been the alarm for so long that calling the arrangement temporary does not feel dishonest anymore", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "There is an open glass of water sitting on the same small top as the lamp and a power strip.",
    "branches": [
     {"answer": "It is a single knocked elbow from water and electricity meeting, and that outranks the convenience of a lidless glass", "cause": "KC-010"},
     {"answer": "The power strip has never had anywhere else on this nightstand to go besides the top", "cause": "KC-002"},
     {"answer": "Nobody set the rule that water needs a lid near this outlet, so it is whoever's habit wins that night", "cause": "KC-008"}
    ]
   },
   {
    "symptom": "The drawer holds a charger for a phone you do not own anymore, a dead pen, and a couple of books you started months ago.",
    "branches": [
     {"answer": "None of it has been used in months, but nothing has forced the drawer to prove it is still earning its spot", "cause": "KC-001"},
     {"answer": "Once it is stirred into the pile you cannot see it without digging, so it never surfaces to be judged", "cause": "KC-005"},
     {"answer": "Nobody clears it out on any schedule, so it only gets sorted whenever someone happens to dump the drawer on the bed", "cause": "KC-009"}
    ]
   }
  ],
  "first_15": {
   "action": "Empty the top down to five items and empty the drawer onto the bed: the dead pen, the chargers for phones you do not own, and any book you have not picked up this week go straight to the shelf or the bin.",
   "victory": "The nightstand top holds five things or fewer with no cable crossing it, and the drawer holds only what you would actually reach for tonight."
  }
 },
 "Nightstand Right": {
  "frictions": [
   {
    "symptom": "There is medication, capped or not, sitting loose in the open drawer on this side.",
    "branches": [
     {"answer": "It is a poisoning risk at exactly the height a toddler or a dog reaches from the mattress, and that is worth raising even though the rest of the drawer is not yours to touch", "cause": "KC-010"},
     {"answer": "Nobody has checked the dates together in a while, so a bottle ages out of use unnoticed", "cause": "KC-011"},
     {"answer": "It has been in that drawer long enough that neither of you registers it as open and unsecured anymore", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "The lamp cord on this side runs loose across the floor instead of behind the leg.",
    "branches": [
     {"answer": "It crosses the exact strip you both walk in the dark, and that is a real trip risk ahead of how it looks", "cause": "KC-010"},
     {"answer": "This side's cord was never run behind the leg the way the other side's was, so the shared standard stopped at one nightstand", "cause": "KC-008"},
     {"answer": "The floor beside this side is not yours to rearrange, so a hazard sitting in shared space does not get fixed because it is not your side", "cause": "RC-013"}
    ]
   },
   {
    "symptom": "The two nightstand tops are holding different numbers of things, one cluttered, one clear.",
    "branches": [
     {"answer": "One person tidied the other's side once, and it started an argument that has made both of you avoid the topic since", "cause": "KC-012"},
     {"answer": "There is no agreed number for this side the way there is for the other, so clear means something different to each of you", "cause": "KC-008"},
     {"answer": "Whoever notices the gap first assumes it is the other person's job to close it", "cause": "RC-013"}
    ]
   }
  ],
  "first_15": {
   "action": "Check the medication dates together right now: cap anything loose, and if a child or a dog gets onto this bed, move it into a closed box. Then run the lamp cord behind the leg on this side to match the other.",
   "victory": "Medication on this side is capped and closed away, and the lamp cord runs behind the leg instead of across the floor."
  }
 },
 "Dresser Top": {
  "frictions": [
   {
    "symptom": "There is loose change, a receipt, or a single earring sitting on the bare wood beside the tray instead of inside it.",
    "branches": [
     {"answer": "The tray is already full, so the honest fix is thinning the keyring or moving a ring to the jewellery box, not starting a second pile", "cause": "KC-007"},
     {"answer": "Loose change and receipts have no assigned home of their own once they leave your pocket", "cause": "KC-002"},
     {"answer": "One receipt on bare wood does not look like much on its own, which is exactly how a second pile starts", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "There are three or four fragrance bottles standing on the top, but you only reach for one of them.",
    "branches": [
     {"answer": "The others were gifts, and letting them go feels like it dishonors who gave them", "cause": "RC-014"},
     {"answer": "Nothing has actually been decided about the ones you have not worn in a year, so they just keep standing there", "cause": "RC-015"},
     {"answer": "They have stood in the same spot so long that four bottles does not register as three too many", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "The dresser is not strapped to the wall, and a drawer left open sits low enough for a child to lean on.",
    "branches": [
     {"answer": "A tall unstrapped chest can tip forward and pin a child, and that outranks how a strap looks on the wall", "cause": "KC-010"},
     {"answer": "Fitting it means finding a stud and doing a small job that keeps getting pushed to another weekend", "cause": "KC-009"},
     {"answer": "It has stood unstrapped since it was delivered, so the risk stopped registering the moment it became furniture", "cause": "RC-017"}
    ]
   }
  ],
  "first_15": {
   "action": "Sweep the dresser top down to just the valet tray and the fragrance dish: pocket sediment (change, receipts, stray jewellery) gets sorted into a jar, the bin, or the repair bag, and any bottle you have not reached for in a year comes off entirely.",
   "victory": "The dresser top holds only the valet tray and a small dish of fragrance bottles, and nothing loose sits on the bare wood."
  }
 },
 "Dresser Drawers": {
  "frictions": [
   {
    "symptom": "A drawer needs a shove or a press-down to close, and it is the one holding workout tops or t-shirts.",
    "branches": [
     {"answer": "You own more of that category than you actually wear, six workout tops when you wear two", "cause": "KC-001"},
     {"answer": "There is no fill line anyone is applying, so the drawer just absorbs more until it will not shut", "cause": "KC-008"},
     {"answer": "The overflow only shows up as effort at closing time, so it is easy to keep ignoring until today", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "Two of the drawers are part filled with clothes that do not fit you today.",
    "branches": [
     {"answer": "You have not decided yet whether these come back, so they sit exactly where they always have instead of leaving the bedroom", "cause": "RC-015"},
     {"answer": "They stayed in the main rotation of drawers instead of moving to a box elsewhere in the house, so there is no boundary marking them as separate", "cause": "KC-003"},
     {"answer": "Nobody has re-checked these drawers since your size changed; there was no moment that prompted it", "cause": "KC-009"}
    ]
   },
   {
    "symptom": "Mothballs or cedar blocks are rolling loose in the bottom of a sock or underwear drawer.",
    "branches": [
     {"answer": "Loose in an open drawer, they look like candy to a toddler standing at drawer height, and that outranks the moth protection", "cause": "KC-010"},
     {"answer": "They have never been given their own mesh bag, so loose is just how they have always been stored", "cause": "KC-002"},
     {"answer": "They have rolled around long enough, under the folded rows, that nobody notices them as loose anymore", "cause": "RC-017"}
    ]
   }
  ],
  "first_15": {
   "action": "Open the drawer that needs a shove to close and pull one full category's worth of overflow out right now: extra workout tops, a wrong-size stack, or loose mothballs, whichever is worst.",
   "victory": "Every drawer closes without being pressed down, and a hand's width of free space shows in each one."
  }
 },
 "Primary Closet": {
  "frictions": [
   {
    "symptom": "There is a wire hanger or a plastic dry-cleaner sheath still on a garment on the rod.",
    "branches": [
     {"answer": "The dry cleaner sends them home and nothing has ever swapped them out for the one hanger style the rest of the closet uses", "cause": "KC-008"},
     {"answer": "The plastic sheath is a real suffocation risk if a small child gets in here, and that outranks leaving it on for now", "cause": "KC-010"},
     {"answer": "It blends into a rod that is this full, so a wire hanger among dozens of matching ones does not stand out anymore", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "There is a suit, a coat, or a pair of shoes in here that cost real money and has not been worn in over a year.",
    "branches": [
     {"answer": "Letting it go feels like admitting the money is gone, so it stays even though the money already left the day it was bought", "cause": "RC-014"},
     {"answer": "There is no deadline attached to it, photograph it, list it, thirty days, so someday never actually arrives", "cause": "RC-015"},
     {"answer": "It has hung in the same spot long enough that walking past it barely registers anymore", "cause": "RC-017"}
    ]
   },
   {
    "symptom": "You cannot slide two fingers between the hangers anywhere along the rod, and there is no bare stretch left at the end.",
    "branches": [
     {"answer": "The rod is carrying more than the two-finger standard allows, so one in one out has stopped happening", "cause": "KC-001"},
     {"answer": "Winter coats and heavy knits that should have moved to the labelled bin for the off season never actually left the rod", "cause": "KC-003"},
     {"answer": "The overloaded rod is putting real weight on brackets only ever meant to hold what one season needs, and it can tear out of the plasterboard while you are reaching in underneath", "cause": "KC-010"}
    ]
   }
  ],
  "first_15": {
   "action": "Walk the rod and pull every wire hanger and plastic dry-cleaner sheath off the garments right now, and bag them for the bin.",
   "victory": "Every hanger on the rod is the same style, and no wire hanger or dry-cleaner sheath remains on anything hanging."
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
 ("Bed and Bedding Zone", "PRF-001",
  "THREE OR MORE SHEET SETS ARE STACKED ON THE LINEN SHELF",
  "a linen shelf holding four folded sheet sets stacked together, one "
  "still wrapped in its original packaging, crowding a shelf meant for "
  "two"),
 ("Bed and Bedding Zone", "PRF-002",
  "A BIN, SHOES, OR A CABLE SIT IN THE FLOOR STRIP BETWEEN THE BED AND "
  "THE DOOR",
  "a phone charging cable and a pair of shoes lying across the strip of "
  "bedroom floor between the foot of the bed and the door"),
 ("Bed and Bedding Zone", "PRF-003",
  "BOOKS, A SPEAKER, OR A FRAMED PICTURE SIT ON THE SHELF ABOVE THE "
  "PILLOWS",
  "a small stack of books and a framed picture sitting on a headboard "
  "shelf directly above two sleeping pillows"),

 ("Nightstand Left", "PRF-004",
  "THE PHONE CHARGES ON THE NIGHTSTAND TOP AND DOUBLES AS THE ALARM",
  "a phone lying face up on a nightstand top, its charging cable "
  "running to an outlet, sitting beside a lamp with no separate alarm "
  "clock in sight"),
 ("Nightstand Left", "PRF-005",
  "AN OPEN GLASS OF WATER SITS ON THE SAME TOP AS THE LAMP AND A POWER "
  "STRIP",
  "an open glass of water standing on a small nightstand top beside a "
  "lamp base and a power strip with two cables plugged in"),
 ("Nightstand Left", "PRF-006",
  "THE DRAWER HOLDS AN OLD CHARGER, A DEAD PEN, AND UNREAD BOOKS",
  "an open nightstand drawer holding a tangled phone charger, a "
  "dried-out pen, and two books with bookmarks partway through, none of "
  "it sorted into sections"),

 ("Nightstand Right", "PRF-007",
  "MEDICATION SITS LOOSE IN THE OPEN DRAWER ON THIS SIDE",
  "a nightstand drawer standing open with a few medication bottles "
  "lying loose inside, one lid sitting unscrewed beside it"),
 ("Nightstand Right", "PRF-008",
  "THE LAMP CORD ON THIS SIDE RUNS LOOSE ACROSS THE FLOOR",
  "a lamp cord running loose across the bedroom floor beside a "
  "nightstand instead of tucked behind the leg"),
 ("Nightstand Right", "PRF-009",
  "THE TWO NIGHTSTAND TOPS HOLD DIFFERENT NUMBERS OF THINGS",
  "two nightstands on either side of a made bed, one top bare and "
  "orderly, the other crowded with several more items than the first"),

 ("Dresser Top", "PRF-010",
  "LOOSE CHANGE, A RECEIPT, OR AN EARRING SITS ON THE BARE WOOD BESIDE "
  "THE TRAY",
  "a dresser top with a valet tray at its center and a scatter of "
  "loose coins, a folded receipt, and a single earring sitting on the "
  "bare wood just outside it"),
 ("Dresser Top", "PRF-011",
  "THREE OR FOUR FRAGRANCE BOTTLES STAND ON THE TOP BUT ONLY ONE GETS "
  "USED",
  "four fragrance bottles of different heights standing together on a "
  "dresser top, one visibly used down to half and the others still "
  "full and dusty"),
 ("Dresser Top", "PRF-012",
  "THE DRESSER IS NOT STRAPPED TO THE WALL, AND AN OPEN DRAWER SITS LOW "
  "ENOUGH TO LEAN ON",
  "a tall dresser standing away from the wall with no anti-tip strap "
  "visible, its bottom drawer left open at a height a small child could "
  "lean on"),

 ("Dresser Drawers", "PRF-013",
  "A DRAWER NEEDS A SHOVE TO CLOSE, AND IT IS THE ONE HOLDING WORKOUT "
  "TOPS",
  "a dresser drawer stuffed with folded workout tops bulging above the "
  "drawer's own rim, a hand pressing down on the pile to force it shut"),
 ("Dresser Drawers", "PRF-014",
  "TWO DRAWERS ARE PART FILLED WITH CLOTHES THAT DO NOT FIT TODAY",
  "two half-filled dresser drawers holding folded clothes in a visibly "
  "different size from what is hanging in the closet beyond"),
 ("Dresser Drawers", "PRF-015",
  "MOTHBALLS OR CEDAR BLOCKS ROLL LOOSE IN THE BOTTOM OF A DRAWER",
  "a few loose mothballs rolling among folded socks in the bottom of an "
  "open dresser drawer, no mesh bag or pouch in sight"),

 ("Primary Closet", "PRF-016",
  "A WIRE HANGER OR A DRY-CLEANER SHEATH IS STILL ON A GARMENT ON THE "
  "ROD",
  "a thin wire hanger holding a shirt among rows of matching wooden "
  "hangers, and a sheer plastic dry-cleaner sheath still covering a "
  "coat beside it"),
 ("Primary Closet", "PRF-017",
  "A SUIT, A COAT, OR SHOES THAT COST REAL MONEY HAVEN'T BEEN WORN IN A "
  "YEAR",
  "a formal suit hanging at the end of the closet rod with a thin "
  "layer of dust visible on its shoulders, untouched among more "
  "recently worn clothes"),
 ("Primary Closet", "PRF-018",
  "YOU CANNOT SLIDE TWO FINGERS BETWEEN THE HANGERS ANYWHERE ON THE ROD",
  "a closet rod packed edge to edge with hanging garments touching at "
  "the shoulders, no gap visible anywhere along its length"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, primary-bedroom-scened art only. The name, meaning,
# six_s and confirm_in_30_seconds text are not reauthored: they are read
# straight from ops/root_causes.py, the one shared vocabulary the deck, the
# app and the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "six workout tops stuffed into one dresser drawer when only "
           "two are ever actually worn in a week",
 "KC-002": "a power strip and a phone charger sitting on a nightstand "
           "top with no drawer or shelf ever assigned to either",
 "KC-003": "winter coats and heavy knits still hanging on the closet rod "
           "months after they should have moved to the seasonal bin",
 "KC-005": "a nightstand drawer so crowded with a charger, a pen and "
           "old books that nothing in it can be named without digging",
 "KC-007": "a single valet tray already overflowing with keys, a watch "
           "and rings, with no room left for anything else that belongs "
           "in it",
 "KC-008": "a headboard shelf holding a stack of books and a framed "
           "picture, with no note anywhere saying the shelf is for the "
           "lamp alone",
 "KC-009": "a dresser standing unstrapped to the wall since delivery "
           "day, with no reminder anywhere that the job was ever "
           "supposed to happen",
 "KC-010": "a lamp cord running loose across the bedroom floor exactly "
           "where a foot lands getting out of bed in the dark",
 "KC-011": "a medication bottle sitting in a nightstand drawer well "
           "past its printed date, never checked since it was put away",
 "KC-012": "two nightstands on either side of the same bed, one holding "
           "five items and the other holding twice that many",
 "RC-013": "a lamp cord crossing the shared floor beside a nightstand "
           "that neither sleeper has claimed as their job to fix",
 "RC-014": "a wedding-gift sheet set still sealed in its original "
           "packaging on the linen shelf, years after the wedding",
 "RC-015": "a suit for a job that ended still hanging at the end of the "
           "closet rod, with no date set for when it finally leaves",
 "RC-017": "a folded quilt draped over the same spot on a headboard "
           "shelf for so long that walking past it barely registers "
           "anymore",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Bed and Bedding Zone": [
  "Run the vacuum crevice tool down the gap where dust and hair pack "
  "against the wall behind the headboard.",
  "Wipe along the top of the bed frame rails and down the legs, getting "
  "the inner faces of the slats you never see once the mattress is "
  "back down.",
  "Slide a pillowcase over each still fan blade, close it and pull "
  "back so the dust comes off inside the case, then wipe each blade "
  "dry.",
 ],
 "Nightstand Left": [
  "Wipe the lamp base and switch with a barely damp cloth, getting "
  "into the ring where fingers turn it on night after night.",
  "Tip out the drawer's divided sections, vacuum the grit from the "
  "corners, then wipe the base and both runners.",
  "Follow the lamp cord down to the floor and check nothing is snagged "
  "along the skirting behind the leg.",
 ],
 "Nightstand Right": [
  "Lift the framed photo, dust the back and stand, then mist glass "
  "cleaner onto the cloth rather than the glass and wipe the front "
  "streak-free.",
  "Run the crevice tool down the narrow slot between the nightstand "
  "and the bed frame, where tissues and dust collect unseen.",
  "Vacuum the drawer interior without unpacking what is stored there, "
  "and wipe the base around it.",
 ],
 "Dresser Top": [
  "Vacuum the dust from the narrow gap behind the dresser, then wipe "
  "the back edge of the top where a cloth rarely reaches.",
  "Empty the valet tray and wipe it inside and out, then clean the "
  "necks and bases of the fragrance bottles where scent has gone "
  "tacky.",
  "Wipe each drawer front and get into the handles where hands leave "
  "an oily film.",
 ],
 "Dresser Drawers": [
  "Lift each drawer out completely, vacuum the corners and folds, and "
  "wipe the base, letting it dry fully before clothes return.",
  "Work the detail brush along the metal runners and into the track, "
  "lifting the grit that makes a drawer stick and jump.",
  "With the drawers out, vacuum inside the empty carcass and the back "
  "panel where dust and stray socks gather.",
 ],
 "Primary Closet": [
  "Lift the bags and boxes down from the top shelf, dust where a film "
  "has been settling onto stored things all year.",
  "Run a damp cloth the full length of the hanging rod to take off the "
  "fuzzy grey film that transfers onto a dark shoulder.",
  "Lift the shoes off the rack, wipe the shelves clean of grit and "
  "dried mud, and wipe the soles before pairs go back.",
 ],
}


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone: the 15-minute reset (the Manual's own
# first_15 action and victory condition, quoted and gate-checked, expanded
# into a short numbered script) and an authored 30-minute rebuild. Three
# more whole-bedroom actions, the same shape every other room's whole-room
# cards use: no zone or standard invented for them, only their real root
# causes.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "PRA-001", "zone": "Bed and Bedding Zone",
  "title": "CLEAR THE FLOOR STRIP AND THE HEADBOARD SHELF",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the floor strip between the bed and the door, and move "
          "any headboard-shelf item that is not the lamp off the shelf.",
  "why": "A bin, a shoe, or a cable in the walking strip is what your "
         "foot finds at three in the morning, and weight over the "
         "pillows on an unmarked shelf is a fall risk you sleep under "
         "every night.",
  "inputs": ["a laundry basket", "the linen shelf"],
  "steps": [
   "Clear the floor strip between the bed and the door of anything "
   "sitting on it, and move any headboard-shelf item that is not the "
   "lamp off the shelf.",
   "Carry each item to where it actually belongs rather than setting "
   "it down again somewhere else in the room."],
  "causes": ["KC-002", "KC-010"],
  "victory": "The floor strip between the bed and the door is bare, and "
             "the headboard shelf above the pillows holds only the "
             "lamp.",
  "next": "PRS-001",
  "art": "a bedroom floor strip between the bed and the door being "
         "cleared of a charging cable and a pair of shoes, a headboard "
         "shelf above the pillows left holding only a lamp"},

 {"id": "PRA-002", "zone": "Bed and Bedding Zone",
  "title": "SET THE SHEET COUNT AND MOVE THIS BED'S LINEN TO ITS OWN "
           "SPACE",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Pull the linen shelf down to two sheet sets for this bed and "
          "separate them from guest and kid linens.",
  "why": "A shelf holding four or five sets for one bed is not spare "
         "capacity, it is a decision nobody has made yet, and mixing "
         "this bed's sets with other beds' linen means digging every "
         "time you strip it.",
  "inputs": ["a donation bag or rag bin", "a marker for the shelf"],
  "steps": [
   "Count every sheet set for this bed on the linen shelf. Keep two: "
   "one on the bed, one clean. A third stays only if a child or a pet "
   "actually sleeps here and you have stripped this bed at two in the "
   "morning within the last year.",
   "Move whatever is left, worn thin, pilled, or simply extra, out as "
   "rag or textile recycling, and separate this bed's own two sets "
   "from any guest doubles or kid singles sharing the same shelf."],
  "causes": ["RC-014", "KC-008", "RC-017"],
  "victory": "The linen shelf holds exactly two sheet sets for this "
             "bed, set apart from any guest or kid linen sharing the "
             "shelf.",
  "next": "PRA-001",
  "art": "a linen shelf holding exactly two folded sheet sets for one "
         "bed, set apart from a separate stack of guest and kids' "
         "sheets"},

 {"id": "PRA-003", "zone": "Nightstand Left",
  "title": "CLEAR THE TOP TO FIVE AND EMPTY THE DRAWER",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the top down to five items and empty the drawer onto "
          "the bed, clearing out what no longer earns its spot.",
  "why": "A dead charger and a book you are not reading this week cost "
         "nothing to keep and everything to dig through the one time "
         "you actually need the drawer.",
  "inputs": ["a bin", "the bookshelf"],
  "steps": [
   "Empty the top down to five items and empty the drawer onto the "
   "bed: the dead pen, the chargers for phones you do not own, and any "
   "book you have not picked up this week go straight to the shelf or "
   "the bin.",
   "Divide the drawer so glasses, lip balm and earplugs each sit in "
   "their own section instead of sliding into one heap."],
  "causes": ["KC-001", "KC-005", "KC-009"],
  "victory": "The nightstand top holds five things or fewer with no "
             "cable crossing it, and the drawer holds only what you "
             "would actually reach for tonight.",
  "next": "PRS-002",
  "art": "a nightstand top mid-clear, a dead pen and an old phone "
         "charger being lifted out of the drawer, five items left "
         "standing on the top"},

 {"id": "PRA-004", "zone": "Nightstand Left",
  "title": "SEPARATE WATER FROM POWER AND GIVE THE PHONE CHARGER A REAL "
           "HOME",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Move the power strip off the nightstand top, commit to a "
          "lidded drink at the bedside, and give the phone charger a "
          "charging spot that is not beside your pillow.",
  "why": "Water and a power strip sharing one small surface is a single "
         "knocked elbow from a real problem, and a phone doubling as "
         "your alarm is the reason it never actually leaves the "
         "bedside.",
  "inputs": ["a bottle with a lid", "a nine-dollar alarm clock"],
  "steps": [
   "Move the power strip off the nightstand top and onto the floor "
   "behind it, and if you drink in bed, switch to a bottle with a lid.",
   "Buy the cheap alarm clock, move the phone charger to the dresser "
   "across the room, and give the phone a landing spot you have to "
   "stand up to reach; if you will not commit to that, keep the "
   "charger but lay the phone face down and drop one other item so the "
   "top still counts to five."],
  "causes": ["KC-010", "KC-002", "KC-009", "RC-017", "KC-008"],
  "victory": "The power strip is off the top and on the floor behind "
             "the nightstand, and the phone charger has either moved to "
             "the dresser or the phone lies face down with the top "
             "still counting to five.",
  "next": "PRA-003",
  "art": "a hand moving a power strip off a nightstand top onto the "
         "floor behind it, a phone lying face down beside a small "
         "battery alarm clock"},

 {"id": "PRA-005", "zone": "Nightstand Right",
  "title": "CHECK THE MEDICATION AND RUN THE CORD BEHIND THE LEG",
  "minutes": 15, "players": "1 to 2", "six_s": "Safety",
  "from_first_15": True,
  "goal": "Check the medication dates together, cap and close away "
          "anything loose, and run the lamp cord behind the leg on this "
          "side to match the other.",
  "why": "Sleep aids and painkillers loose in an open bedside drawer "
         "sit at exactly the height a toddler or a dog reaches from the "
         "mattress, and this is the one thing worth raising even though "
         "the rest of the drawer is not yours to touch.",
  "inputs": ["a closed box for medication", "cable clips"],
  "steps": [
   "Check the medication dates together right now: cap anything loose, "
   "and if a child or a dog gets onto this bed, move it into a closed "
   "box. Then run the lamp cord behind the leg on this side to match "
   "the other.",
   "Confirm both changes hold before you leave the room: the drawer "
   "closed, the cord out of the walking path."],
  "causes": ["KC-010", "KC-011", "RC-017"],
  "victory": "Medication on this side is capped and closed away, and "
             "the lamp cord runs behind the leg instead of across the "
             "floor.",
  "next": "PRS-003",
  "art": "a hand capping a medication bottle over a closed box on a "
         "nightstand, a lamp cord running down behind the leg instead "
         "of across the floor"},

 {"id": "PRA-006", "zone": "Nightstand Right",
  "title": "AGREE THE SHARED STANDARD AND CLOSE THE COUNT GAP",
  "minutes": 30, "players": "1 to 2", "six_s": "Standardize",
  "goal": "Agree out loud that the cord rule and the item count apply "
          "to both nightstands equally, then bring this side's count "
          "level with the other.",
  "why": "Every argument about tidiness in a shared bedroom starts with "
         "one person fixing the side that is not theirs to fix; "
         "matching the standard instead of the contents settles it "
         "without either of you touching the other's drawer.",
  "inputs": ["nothing, this is a conversation"],
  "steps": [
   "Say out loud, together, that the cord-behind-the-leg rule and the "
   "shared item count apply to both nightstands, not just the one that "
   "already meets it.",
   "Whoever's top is running high brings their own count down to match "
   "the other's; you may wipe and vacuum this side, but the choice of "
   "what stays in the drawer is theirs alone to make."],
  "causes": ["KC-008", "RC-013", "KC-012"],
  "victory": "Both nightstand tops run the same lamp-cord rule and the "
             "same item count, and the difference that started the "
             "conversation is gone.",
  "next": "PRA-005",
  "art": "two nightstands on either side of a made bed, both tops now "
         "holding the same small number of items"},

 {"id": "PRA-007", "zone": "Dresser Top",
  "title": "SWEEP THE TOP DOWN TO THE TRAY AND THE DISH",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Sweep the dresser top down to just the valet tray and the "
          "fragrance dish, sorting the pocket sediment as you go.",
  "why": "Loose change, a receipt, and a snapped chain do not improve "
         "by sitting on the wood, they just start the second pile that "
         "spreads from there.",
  "inputs": ["a jar for change", "a small repair bag"],
  "steps": [
   "Sweep the dresser top down to just the valet tray and the "
   "fragrance dish: pocket sediment (change, receipts, stray "
   "jewellery) gets sorted into a jar, the bin, or the repair bag, and "
   "any bottle you have not reached for in a year comes off entirely.",
   "Move any jewellery you love but never wear into a box in the "
   "closet rather than back onto the top."],
  "causes": ["KC-007", "KC-002"],
  "victory": "The dresser top holds only the valet tray and a small "
             "dish of fragrance bottles, and nothing loose sits on the "
             "bare wood.",
  "next": "PRS-004",
  "art": "a dresser top mid-sweep, loose change and a receipt being "
         "lifted off the bare wood into a jar, the valet tray and "
         "fragrance dish left standing alone"},

 {"id": "PRA-008", "zone": "Dresser Top",
  "title": "STRAP THE DRESSER AND CLEAR OUT THE UNWORN FRAGRANCE",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Fit an anti-tip strap into a stud, and keep only the "
          "fragrance you actually wear and the one you honestly "
          "alternate to.",
  "why": "An unstrapped tall dresser tips forward the moment a loaded "
         "drawer is open and a child leans on it, and a shelf of "
         "unworn fragrance is glass sitting at exactly that same "
         "front edge.",
  "inputs": ["an anti-tip strap", "a screwdriver"],
  "steps": [
   "Fit an anti-tip strap into a stud, and check the fixing holds when "
   "you lean on an open drawer.",
   "Test every fragrance bottle against the last year: keep the one "
   "you wear and the one you honestly alternate to, and let the rest "
   "go along with the guilt."],
  "causes": ["KC-010", "KC-009", "RC-014", "RC-015", "RC-017"],
  "victory": "The dresser is strapped into a stud, and the only "
             "fragrance bottles left on the dish are ones you have "
             "actually reached for in the last year.",
  "next": "PRA-007",
  "art": "a hand fitting an anti-tip strap between a dresser and the "
         "wall stud, two fragrance bottles set aside on a cloth while "
         "two remain on the dish"},

 {"id": "PRA-009", "zone": "Dresser Drawers",
  "title": "PULL THE OVERFLOW FROM THE DRAWER THAT NEEDS A SHOVE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Open the drawer that needs a shove to close and pull one "
          "full category's worth of overflow out right now.",
  "why": "A drawer that needs pressing down to shut has already "
         "outgrown its category, and the fix costs the same fifteen "
         "minutes today that it costs every day you put it off.",
  "inputs": ["a donation bag"],
  "steps": [
   "Open the drawer that needs a shove to close and pull one full "
   "category's worth of overflow out right now: extra workout tops, a "
   "wrong-size stack, or loose mothballs, whichever is worst.",
   "Check that the drawer now closes without being pressed down before "
   "you move on."],
  "causes": ["KC-001", "KC-008"],
  "victory": "Every drawer closes without being pressed down, and a "
             "hand's width of free space shows in each one.",
  "next": "PRS-005",
  "art": "a dresser drawer mid-sort, a stack of extra workout tops "
         "being lifted out, a hand's width of space showing at the "
         "front of the drawer"},

 {"id": "PRA-010", "zone": "Dresser Drawers",
  "title": "BOX THE WRONG SIZE, BAG THE MOTHBALLS, AND STRAP THE CHEST",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Move the two part-filled off-size drawers into one dated box "
          "out of the bedroom, bag any loose mothballs or cedar, and "
          "confirm the chest is anchored.",
  "why": "Clothes that do not fit today are a small unpleasant reminder "
         "every morning, and loose mothballs at drawer height look "
         "like candy to a toddler standing at the open bottom drawer.",
  "inputs": ["a box and a marker", "a mesh bag"],
  "steps": [
   "Empty the two part-filled off-size drawers into one box, write "
   "today's date on the lid, and store it somewhere else in the house; "
   "if it is still sealed a year from now it leaves sealed.",
   "Gather any loose mothballs or cedar blocks into a mesh bag hung at "
   "the back of the drawer, or leave them out entirely, and confirm "
   "the anti-tip strap is fitted and holding."],
  "causes": ["RC-015", "KC-003", "KC-009", "KC-010", "KC-002", "RC-017"],
  "victory": "No drawer holds clothes in a size you are not wearing "
             "today, any mothballs or cedar are sealed in a mesh bag "
             "rather than rolling loose, and the chest is anchored to "
             "the wall.",
  "next": "PRA-009",
  "art": "a dated cardboard box holding off-size clothes being carried "
         "out of a bedroom, a mesh bag of mothballs set inside an open "
         "drawer behind it"},

 {"id": "PRA-011", "zone": "Primary Closet",
  "title": "PULL EVERY WIRE HANGER AND DRY-CLEANER SHEATH OFF THE ROD",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Walk the rod and pull every wire hanger and plastic "
          "dry-cleaner sheath off the garments, and bag them for the "
          "bin.",
  "why": "A thin dry-cleaning bag clinging to a face is a real "
         "suffocation risk if a small child plays in here, and a wire "
         "hanger among matching ones is the first sign the one-hanger "
         "rule has slipped.",
  "inputs": ["a bin bag"],
  "steps": [
   "Walk the rod and pull every wire hanger and plastic dry-cleaner "
   "sheath off the garments right now, and bag them for the bin.",
   "Swap anything left on a wire hanger onto the closet's own hanger "
   "style before it goes back on the rod."],
  "causes": ["KC-008", "KC-010"],
  "victory": "Every hanger on the rod is the same style, and no wire "
             "hanger or dry-cleaner sheath remains on anything hanging.",
  "next": "PRS-006",
  "art": "a closet rod mid-sort, a wire hanger and a sheer "
         "dry-cleaner sheath being pulled off into a bin bag, matching "
         "wooden hangers left in place"},

 {"id": "PRA-012", "zone": "Primary Closet",
  "title": "SET THE THIRTY-DAY DEADLINE AND CLEAR THE ROD TO TWO "
           "FINGERS",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Photograph and list the one expensive unworn item with a "
          "thirty-day deadline, and move winter coats or heavy knits "
          "off the rod until you can slide two fingers between every "
          "hanger.",
  "why": "An overloaded rod can tear its brackets out of plasterboard "
         "while you are standing underneath reaching in, and an "
         "expensive item you never wear costs you a hanger and a flinch "
         "every time you slide past it.",
  "inputs": ["a phone camera", "the seasonal storage bin"],
  "steps": [
   "Photograph the one suit, coat, or pair of shoes that cost real "
   "money and has not been worn in a year, list it for sale, and set a "
   "thirty-day deadline: unsold, it goes to the charity shop without "
   "another conversation.",
   "Move winter coats and heavy knits that belong in the labelled "
   "off-season bin off the rod until you can slide two fingers between "
   "every remaining hanger, with a bare stretch left at one end."],
  "causes": ["RC-014", "RC-015", "RC-017", "KC-001", "KC-003", "KC-010"],
  "victory": "The expensive unworn item has a photograph, a listing, "
             "and a thirty-day deadline, and you can slide two fingers "
             "between every hanger on the rod with a bare stretch left "
             "at the end.",
  "next": "PRA-011",
  "art": "a phone photographing an unworn suit on a closet rod, a "
         "labelled seasonal bin standing nearby with a folded coat "
         "going into it"},

 {"id": "PRA-013", "zone": None, "title": "THE FULL BEDROOM HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking for a reachable cord, an unanchored "
          "dresser, and medication left loose in an open drawer.",
  "why": "This room's own hazards, a cord in the dark path to the door, "
         "an unstrapped dresser, capped medication, sit across four "
         "different zones and only get found together if someone walks "
         "the whole room on purpose.",
  "inputs": ["a screwdriver", "an anti-tip strap"],
  "steps": [
   "Check the floor strip beside the bed and both nightstands for any "
   "cord running loose across it, and clip or reroute each one behind "
   "a leg.",
   "Check the dresser and confirm the anti-tip strap is fitted and "
   "holding, and check the headboard shelf for anything unfixed "
   "sitting above the pillows.",
   "Check both nightstand drawers for medication that is not capped "
   "and in date, and close it away if a child or a dog can climb onto "
   "this bed."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No cord runs loose across a walked path, the dresser is "
             "anchored, nothing unfixed sits above the pillows, and all "
             "medication is capped, in date, and closed away.",
  "next": "PRE-001",
  "art": "a hand checking an anti-tip strap on a bedroom dresser, a "
         "lamp cord clipped behind a nightstand leg visible beyond"},

 {"id": "PRA-014", "zone": None,
  "title": "THE ROOM'S OWN TRAP: WHAT THE REST OF THE HOUSE OFFLOADED "
           "HERE",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Walk the room looking for anything that belongs to another "
          "room entirely, wrapping paper, exercise equipment, "
          "paperwork, and move each thing back to where it is actually "
          "used.",
  "why": "The bedroom absorbs what the rest of the house refuses "
         "because the door usually stays shut; none of it supports "
         "sleep, and it only stays here by default.",
  "inputs": ["a laundry basket for cross-room items"],
  "steps": [
   "Walk the whole room and pull out anything that plainly belongs to "
   "another room: gift wrap, seasonal decor, exercise equipment, a box "
   "of unfiled paperwork.",
   "Carry each item to the room it is actually used in today, not to a "
   "corner of this one, and if nowhere else in the house wants it, "
   "that is itself the answer."],
  "causes": ["KC-003", "RC-015"],
  "victory": "Nothing remains in the bedroom that plainly belongs to "
             "another room's job, and every item pulled has either "
             "moved to where it is used or left the house.",
  "next": "PRA-015",
  "art": "a roll of wrapping paper and a box of paperwork being carried "
         "out of a bedroom, an exercise bike left bare of any clothes "
         "draped over it"},

 {"id": "PRA-015", "zone": None, "title": "THE LAST-THING-BEFORE-BED "
                                          "RESET",
  "minutes": 15, "players": "1 to 2", "six_s": "Sustain",
  "goal": "The last thing before you leave the room in the morning, "
          "confirm the bed is made, both nightstand tops are at their "
          "count, and the dresser tray is empty of loose pocket items.",
  "why": "Every standard in this room is built to survive a bad week, "
         "and the only way that holds is checking it meets its own "
         "standard before you leave, not noticing days later that it "
         "slipped.",
  "inputs": ["nothing, this is a walk-through"],
  "steps": [
   "Make the bed before you leave the room, while the duvet is still "
   "thrown back and it takes one pull.",
   "Check both nightstand tops sit at their agreed count, and empty "
   "your pockets into the dresser tray rather than beside it."],
  "causes": ["KC-009", "RC-013", "RC-017"],
  "victory": "The bed is made, both nightstand tops sit at their agreed "
             "count, and nothing from your pockets sits loose beside "
             "the dresser tray.",
  "next": "PRA-013",
  "art": "a hand doing a last-check pass across a settled bedroom, a "
         "made bed and two matching nightstand tops visible in one "
         "frame"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a primary bedroom, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("PRE-001", "THE NIGHT YOU GET INTO BED WITHOUT TURNING ON A LIGHT",
  "You come to bed late and get in without turning on the overhead "
  "light, feeling your way from the door.",
  ["PRZ-001"],
  "The floor strip between the door and the bed is completely bare, so "
  "nothing catches your foot in the dark.",
  "If you stubbed a toe on a bin, a shoe, or a cable, the floor strip "
  "was never cleared or it slipped back since. Draw PRA-002.",
  "a hand feeling along a dark bedroom wall toward a bed, the floor "
  "strip between the door and the bed completely bare"),
 ("PRE-002", "THE MORNING YOU HIT SNOOZE WITHOUT LOOKING",
  "Your alarm goes off and your hand reaches for the nightstand top "
  "without your eyes open yet.",
  ["PRZ-002"],
  "Your hand finds the lamp switch or the clock in the same five items "
  "every time, nothing else in the way.",
  "If your hand knocked into a glass, a charger cable, or a sixth item "
  "you did not expect, the top has drifted past five. Draw PRA-003.",
  "a hand reaching for a small alarm clock on a nightstand top holding "
  "five items, eyes still closed"),
 ("PRE-003", "THE NIGHT YOUR PARTNER IS SICK AND NEEDS MEDICATION IN "
             "THE DARK",
  "Your partner wakes at 2 a.m. needing their medication, and you are "
  "the one reaching into their nightstand drawer in the dark.",
  ["PRZ-003"],
  "The medication is capped, in date, and easy to find because you "
  "both agreed on the cord and the count, even though the rest of the "
  "drawer stayed theirs.",
  "If you had to hunt or the cap was already off, the one exception "
  "this side allows, checking medication together, has not happened in "
  "a while. Draw PRA-005.",
  "a hand finding a capped medication bottle inside a nightstand drawer "
  "in a dim bedroom at night"),
 ("PRE-004", "THE MORNING YOU'RE ALREADY LATE AND EMPTYING YOUR "
             "POCKETS",
  "You are rushing out the door and empty last night's pockets onto "
  "the dresser on your way past.",
  ["PRZ-004"],
  "Everything lands inside the valet tray in one motion because the "
  "tray still has room, and the wood around it stays bare.",
  "If something landed on the bare wood beside the tray because it was "
  "already full, the tray needs thinning, not a bigger tray. Draw "
  "PRA-007.",
  "a hand dropping keys and a watch into a valet tray on a dresser top "
  "in one motion while rushing past"),
 ("PRE-005", "THE DAY LAUNDRY COMES BACK AND YOU'RE TIRED",
  "A full laundry basket comes back up to the bedroom at the end of a "
  "long day, and putting it away is the last thing you want to do.",
  ["PRZ-005"],
  "Every drawer still has a hand's width of space waiting, so folding "
  "it in takes ten minutes and nothing gets pressed down.",
  "If a drawer needed a shove to close, the overflow was never pulled "
  "the last time this happened. Draw PRA-009.",
  "a laundry basket beside an open dresser drawer with a hand's width "
  "of free space visible at the front"),
 ("PRE-006", "THE MORNING YOU NEED SOMETHING SPECIFIC IN A HURRY",
  "You need one specific jacket for an event this morning and you are "
  "already running behind.",
  ["PRZ-006"],
  "You can slide two fingers along the rod straight to it because "
  "everything hangs at the same depth, grouped by type and shade.",
  "If you had to fight through a packed rod to find it, one in one out "
  "has stopped happening. Draw PRA-012.",
  "a hand pulling one jacket straight from a closet rod with two "
  "fingers of space visible on either side of it"),
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
        "related": {"standard": f"PRS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your bedroom, "
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
    standard_id = (f"PRS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"PRS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "PRR-001", "title": "THE PRIMARY BEDROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START WITH YOUR OWN NIGHTSTAND TONIGHT.",
        "objective": "The primary bedroom is the only room in the house "
                     "whose job is to help you stop. This card is the "
                     "map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"PRZ-002 Nightstand Left. {start_tip['text']}"
            if start_tip else
            "PRZ-002 Nightstand Left. It is the smallest zone in the "
            "room and shows you the change twice before you touch "
            "anything bigger."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your bedroom. Put the rest back.",
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
        "players": "1 to 2. With a shared bed, the Nightstand Right "
                   "zone belongs to the other sleeper: you may clean it, "
                   "not cull it. Let the difference between the two "
                   "nightstands make the argument, not a conversation.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do PRA-013 The Full Bedroom Hazard Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "every cord reachable from the walking strip, "
                        "the unanchored dresser, and the medication in "
                        "either nightstand drawer.",
        "related": {"contents": "PRZ-001 to PRZ-006, PRF-001 to "
                                 "PRF-018, the shared root causes in "
                                 "ops/root_causes.py, PRA-001 to "
                                 "PRA-015, PRS-001 to PRS-006, PRE-001 "
                                 "to PRE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole primary "
                           "bedroom in its settled state, a made bed "
                           "with two matching nightstands, a dresser "
                           "with a valet tray on top and folded "
                           "clothes visible in an open drawer, and a "
                           "closet with garments hanging at a shared "
                           "depth all visible in one frame",
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
    return {"deck": "primary-bedroom", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "PRA-013" for c in cards), "no safety walk card"
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
    print(f"  deck        primary-bedroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
