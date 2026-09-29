#!/usr/bin/env python3
"""
Build the Mudroom deck: 69 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
content/manual/source/content.json, the same corpus the 114 zone pages
already read. build_kitchen_deck.py, build_entryway_deck.py,
build_laundry_room_deck.py, build_home_office_deck.py,
build_primary_bathroom_deck.py, build_garage_deck.py,
build_stair_landing_deck.py, build_pantry_deck.py, build_hall_closet_deck.py,
build_dining_room_deck.py, build_guest_bedroom_deck.py,
build_guest_bathroom_deck.py, build_family_room_deck.py and
build_living_room_deck.py proved the pattern for the first fourteen rooms;
this is the fifteenth. Purpose, done_looks_like, the standard, the trigger,
the first-15 action and its victory condition are quoted from the Manual,
not rewritten, and gate() at the bottom asserts they are still
character-for-character identical. The 18 frictions (three per zone) are
likewise derived straight from the Manual's own diagnosis layer, in zone
order, not retyped, so this deck cannot silently diverge from the
diagnostic engine already shipped on the site's zone pages. That diagnosis
layer was authored directly into content.json as part of this same B9
cycle: Mudroom carried the rest of its rich Manual content (purpose,
done_looks_like, passes, the_call, watch_for, leave_behind, shine_detail)
already, but no diagnosis and no deck until this file.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the nine
new action cards (the Manual gives one 15-minute reset per zone in
first_15; the 30-minute rebuild per zone and three whole-room actions are
authored here), the event cards, the micro quests, and the room card. The
root causes are not reauthored: they are the same frozen vocabulary in
ops/root_causes.py that every other room's deck already uses, so a
household owning more than one deck keeps one diagnosis pile rather than
several (DECK-GAME-DESIGN.md 4.3). This room's real frictions reach all
seventeen of the shared vocabulary's causes, confirmed against
content/manual/source/content.json before this file was written by walking
every branch actually authored below, not assumed from any other room's
count or padded toward a round number: the mudroom's own mix of wet floors,
poison-grade pet and lawn chemicals, overloaded hooks, hidden bench storage
and a caddy holding bleach beside an ammonia cleaner happens to give this
room unusually broad real reach across the vocabulary.

WHAT THE BUDGET IS AND WHY
---------------------------
Mudroom ships as a free typeset page, the same stage every prior room in
this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and
it does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). This room
has six real Manual zones, the same shape Family Room's and Living Room's
own six-zone decks used: six ZONE cards, eighteen FRICTION cards (three per
zone), seventeen reachable ROOT CAUSE cards, fifteen ACTION cards (two per
zone plus three whole-room), six STANDARD cards and six EVENT cards. 69
cards in total, not padded or trimmed to match
ops/cardtext/derive_room_deck.py's own generic BUDGET dict, which reports a
fixed 72/7-zone template for every room regardless of its real zone count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Mudroom deck to disclose against: no free Mudroom product exists on the
site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_mudroom_deck.py
Out:  ops/cardtext/mudroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "mudroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Mudroom"

BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 17, "ACTION CARD": 15, "STANDARD CARD": 6,
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
# content/manual/source/content.json before this file was written. This
# room's own frictions reach all seventeen of the shared vocabulary.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011", "KC-012",
             "RC-013", "RC-014", "RC-015", "RC-016", "RC-017"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior generator in this line uses:
# every numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Family Hook Zone": {
  "id": "MDZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE COAT, ONE BAG, ONE HAT PER COLUMN. BARE FLOOR UNDER THE "
             "HOOKS.",
  "callouts": [
   "Two coats and one bag hanging on each person's own named column",
   "A hand-lettered name tag at each column's own eye height",
   "The lowest hooks set at the height of the shortest person in the "
   "house",
   "Bare floor running the whole length of wall beneath the hooks",
   "No scarf or drawstring hanging low enough to reach a toddler's neck",
   "Every hook sitting flush against the wall with no lean or wobble",
  ],
  "art": ("a mudroom hook wall with two coats and one bag hanging on each "
          "person's own named column, a hand-lettered name tag at each "
          "column's eye height, the lowest hooks set at a child's own "
          "reach, and completely bare floor running the length of wall "
          "beneath them"),
 },
 "Bench and Transition Surface": {
  "id": "MDZ-002", "order": 2, "difficulty": 1,
  "tagline": "THREE THINGS MAX ON THE SEAT. THE BASKET EMPTIES ON THE "
             "NEXT TRIP.",
  "callouts": [
   "A bare wooden seat wide enough for two people to sit and lace boots "
   "at once",
   "No more than three objects resting on the surface",
   "One labelled basket at the end of the bench",
   "The basket holding only items that are leaving the house tomorrow",
   "A completely clear floor path in front of the bench",
   "Nothing stored on the shelf directly above the seat",
  ],
  "art": ("a mudroom bench with a bare wooden seat wide enough for two "
          "people to lace boots at once, no more than three objects on "
          "the surface, one labelled outbound basket at the end holding "
          "only what leaves tomorrow, and a clear floor in front of it"),
 },
 "Shoe and Boot Storage": {
  "id": "MDZ-003", "order": 3, "difficulty": 2,
  "tagline": "TWO PAIRS PER PERSON. WET STAYS ON THE TRAY.",
  "callouts": [
   "Two pairs of footwear per person standing on the rack",
   "Every pair standing soles down and toes pointing out",
   "One lipped tray sitting by the door",
   "Only wet or draining pairs standing on the tray",
   "A completely clear stretch of floor between the tray and the doorway",
   "Heavier boots on the rack's bottom row, lighter shoes on top",
  ],
  "art": ("a mudroom shoe rack holding two pairs of footwear per person "
          "standing soles down and toes out, one lipped boot tray by the "
          "door holding only wet pairs, heavier boots on the bottom row, "
          "and a completely clear stretch of floor between the tray and "
          "the doorway"),
 },
 "Pet Station": {
  "id": "MDZ-004", "order": 4, "difficulty": 1,
  "tagline": "ONE KIT ON ONE HOOK. TREATMENTS BEHIND A CLOSED DOOR.",
  "callouts": [
   "A lead clipped to its collar hanging on one hook",
   "A full roll of waste bags threaded onto that same lead",
   "A folded towel sitting within arm's reach of the door",
   "Food sealed inside a closed bin with the scoop resting inside it",
   "Every flea, tick or worming treatment behind a closed door above "
   "reach",
   "A clean water bowl standing on its own mat or tray",
  ],
  "art": ("a mudroom pet station with a lead clipped to its collar "
          "hanging on one hook with a full roll of waste bags threaded "
          "on, a folded towel within arm's reach of the door, a sealed "
          "food bin with its scoop inside, and every treatment stored "
          "behind a closed door above reach"),
 },
 "Seasonal Outdoor Gear": {
  "id": "MDZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE SEASON WITHIN REACH. THE OTHER CLOSED AND DATED ON THE "
             "SHELF.",
  "callouts": [
   "One open bin per person set at their own height",
   "This season's gloves and hat sitting matched in pairs inside each "
   "bin",
   "Umbrellas standing points down in one stand by the door",
   "The other season's bin closed and labelled with the month it was "
   "packed",
   "That closed off-season bin sitting up on the high shelf",
   "No single, unmatched glove visible in any open bin",
  ],
  "art": ("a mudroom seasonal gear shelf with one open bin per person at "
          "their own height holding this season's matched gloves and "
          "hats, umbrellas standing points down in a stand by the door, "
          "and a closed, labelled off-season bin sitting on the high "
          "shelf above"),
 },
 "Cleaning and Utility Zone": {
  "id": "MDZ-006", "order": 6, "difficulty": 2,
  "tagline": "EVERY TOOL HANGS. NOTHING GOES AWAY WET.",
  "callouts": [
   "A broom clipped to the wall with its bristles hanging clear of the "
   "floor",
   "A mop clipped beside it with its head also hanging clear of the "
   "floor",
   "A dustpan hanging empty on its own clip",
   "The vacuum parked flat against the wall inside a marked outline",
   "One caddy holding four labelled cleaner bottles",
   "No tool anywhere leaning loose against the wall",
  ],
  "art": ("a mudroom cleaning corner with a broom, mop and dustpan all "
          "clipped to the wall with their heads hanging clear of the "
          "floor, the vacuum parked flat inside a marked floor outline, "
          "and one caddy holding four labelled cleaner bottles"),
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
 "Family Hook Zone": {
  "frictions": [
   {"symptom": "A coat nobody has worn since the last change of season is "
               "still hanging on its owner's column, taking the slot the "
               "one-coat limit was supposed to leave open.",
    "branches": [
     {"answer": "It's a coat you love, and letting it go feels like "
                "admitting you won't wear it again, not a decision about "
                "this week's weather", "cause": "RC-014"},
     {"answer": "Nobody's actually run the one-week test the rule calls "
                "for, so it just keeps hanging there unchallenged",
      "cause": "RC-015"},
     {"answer": "The column is built for one coat, one bag, one hat, and "
                "a coat this rarely worn is more than that job needs",
      "cause": "KC-001"},
    ]},
   {"symptom": "Two children share one hook rail near the door instead of "
               "each having their own named column, and the older child's "
               "things end up at a height the younger one can't reach at "
               "all.",
    "branches": [
     {"answer": "The wall was never actually split into a vertical strip "
                "per person, so it's still one shared rail two people run "
                "by two different habits", "cause": "KC-012"},
     {"answer": "Whoever's coat went up first claimed the reachable "
                "height, so the younger child's things end up above "
                "their own reach", "cause": "KC-006"},
     {"answer": "Nobody's remeasured hook height since the youngest "
                "child grew, so what's within reach today is still last "
                "year's answer", "cause": "RC-017"},
    ]},
   {"symptom": "A scarf hangs down far enough to dangle at toddler height "
               "from the lowest hook on the wall, the same hook set at "
               "the shortest person's own reach.",
    "branches": [
     {"answer": "A scarf end or a drawstring hanging loose at a small "
                "child's neck height is a strangling risk that outranks "
                "which hook is convenient", "cause": "KC-010"},
     {"answer": "There's no separate rule yet for what never goes on the "
                "lowest hook, only which person's column it belongs to",
      "cause": "KC-008"},
     {"answer": "It's hung in that exact spot for so long that a "
                "dangling scarf end reads as part of the wall, not a "
                "hazard", "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Hang your own coat up right now and walk the whole wall "
             "column by column. Move anything sitting on the wrong "
             "person's column back to its owner, take down any coat, bag "
             "or hat on a column that already has its one coat, one bag, "
             "one hat filled, and move any scarf or drawstring hanging "
             "low enough to reach a toddler's neck up a hook.",
   "victory": "Every column holds no more than one coat, one bag and one "
              "hat, nothing dangles low enough to reach toddler height, "
              "and the floor under the hooks is bare.",
  },
 },
 "Bench and Transition Surface": {
  "frictions": [
   {"symptom": "The hinged bench seat's storage box is full, but nobody "
               "can say what's actually inside it, and it hasn't been "
               "opened in longer than a month.",
    "branches": [
     {"answer": "The box is closed and packed deep enough that you "
                "can't say what's inside without lifting the lid and "
                "clearing the seat first", "cause": "KC-005"},
     {"answer": "Storage under a seat everyone sits on ten times a day "
                "means checking it costs clearing the seat every single "
                "time", "cause": "KC-004"},
     {"answer": "Nobody's actually run the honest week-long lid-count "
                "the rule calls for, so the question just keeps getting "
                "deferred", "cause": "RC-015"},
    ]},
   {"symptom": "The bench surface is carrying more than the three "
               "objects the standard allows, most of it things that "
               "belong in another room entirely.",
    "branches": [
     {"answer": "Most of what's piled here belongs somewhere else in the "
                "house, and it's easier to set it down on the way in "
                "than carry it the rest of the way", "cause": "KC-003"},
     {"answer": "There's no outbound basket actually doing its job, so "
                "anything genuinely leaving the house has nowhere to "
                "wait except the seat itself", "cause": "KC-002"},
     {"answer": "Nobody treats taking one thing off the bench as part of "
                "standing up from it, so the pile only grows",
      "cause": "KC-009"},
    ]},
   {"symptom": "The bench seat is covered in bags, so the person "
               "changing shoes is balancing on one leg on a wet floor "
               "instead of sitting down.",
    "branches": [
     {"answer": "A person balancing on one leg on a wet floor because "
                "the seat is unusable is a fall risk that outranks how "
                "convenient it was to set bags down there",
      "cause": "KC-010"},
     {"answer": "The seat is being used as a shelf instead of a seat, "
                "and nobody's drawn a line between the two jobs",
      "cause": "KC-008"},
     {"answer": "Whoever put the bags there isn't the one who has to sit "
                "down and lace boots, so the cost of the pile falls on "
                "someone else", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Sit down right now and clear the bench to bare wood. Carry "
             "every item that belongs in another room there immediately "
             "rather than sliding it down the bench, and put whatever is "
             "genuinely leaving the house tomorrow into the outbound "
             "basket at the end, nothing else.",
   "victory": "The seat is bare enough for two people to lace boots at "
              "once, no more than three things sit on the surface, and "
              "the outbound basket holds only what leaves on the next "
              "trip out.",
  },
 },
 "Shoe and Boot Storage": {
  "frictions": [
   {"symptom": "A pair of boots bought for a season that hasn't arrived "
               "yet is still taking a rack slot, even though nobody's "
               "worn them in the last four weeks.",
    "branches": [
     {"answer": "They're expensive and undamaged, so nobody wants to be "
                "the one who decides they're not earning their spot",
      "cause": "RC-015"},
     {"answer": "The rack is built for two pairs per person worn this "
                "season, and a pair waiting on weather that hasn't come "
                "is more than that job needs", "cause": "KC-001"},
     {"answer": "Even after the honest four-week test clears out what "
                "shouldn't be here, one active kid's cleats, wellies and "
                "school shoes are already more than two pairs",
      "cause": "KC-007"},
    ]},
   {"symptom": "Wet soles are being carried past the tray onto the hard "
               "floor between it and the doorway, leaving an invisible "
               "film right where everyone turns toward the kitchen.",
    "branches": [
     {"answer": "The tray isn't sitting exactly where boots actually "
                "come off, so it's a step or two short of where the "
                "wet-sole change actually happens", "cause": "KC-003"},
     {"answer": "A wet floor between the tray and the doorway is the "
                "surest slip in the house, which outranks how far the "
                "tray sits from the door", "cause": "KC-010"},
     {"answer": "Nobody's specifically checking that stretch of floor is "
                "bare and dry before it becomes a problem",
      "cause": "RC-013"},
    ]},
   {"symptom": "Dried mud has caked along the underside of the wire "
               "rail, exactly where the shine pass says you never look, "
               "because reaching it means unloading the whole rack "
               "first.",
    "branches": [
     {"answer": "The underside of the rail costs more effort to reach "
                "than wiping the visible top shelf, so it never actually "
                "gets done", "cause": "RC-016"},
     {"answer": "Nobody's checking that hidden underside for the rust or "
                "burr the inspect note warns about, since it's out of "
                "sight", "cause": "RC-013"},
     {"answer": "It's been caked that way through enough cleaning passes "
                "that a crusted rail underside just reads as normal "
                "now", "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Check the tray right now for any pair that has finished "
             "draining and move it up to the rack soles down, toes out. "
             "While you're there, pull any pair that hasn't been worn in "
             "the last four weeks and set it aside with today's date to "
             "move to the wardrobe.",
   "victory": "The tray holds only what's still actually wet, every dry "
              "pair sits on the rack soles down and toes out, and "
              "nothing unworn for four weeks is still taking a slot "
              "without a dated slip.",
  },
 },
 "Pet Station": {
  "frictions": [
   {"symptom": "The food bin sits in the mudroom purely because the sack "
               "came in through this door, while the bowl it feeds sits "
               "in the kitchen, so every meal costs a walk across the "
               "house with the scoop.",
    "branches": [
     {"answer": "It's stored here because that's where it arrived, not "
                "because it's where it's actually used", "cause": "KC-003"},
     {"answer": "Nobody's actually asked the question the rule calls "
                "for, whether the bin would fit in the kitchen instead",
      "cause": "RC-015"},
     {"answer": "The walk from the food bin to the bowl is an extra trip "
                "every single meal, exactly the cost the straighten pass "
                "warns against", "cause": "KC-004"},
    ]},
   {"symptom": "Flea and worming treatment sits loose in the open caddy "
               "at the same height as the waste bags a child is allowed "
               "to fetch.",
    "branches": [
     {"answer": "Poison stored at a height a child is encouraged to "
                "reach into for something else entirely is a safety "
                "constraint that outranks convenience", "cause": "KC-010"},
     {"answer": "There's no separate rule yet that treatments go behind "
                "a closed door above reach, only that the walking kit "
                "hangs together", "cause": "KC-008"},
     {"answer": "It's sat in the caddy at that height for so long that "
                "nobody clocks it as a hazard walking past",
      "cause": "RC-017"},
    ]},
   {"symptom": "The waste bag roll ran out a quarter mile from the house "
               "on a walk last week, because nobody checked it when the "
               "lead went back on its hook.",
    "branches": [
     {"answer": "Nobody's actually pairing the lead-hook check with the "
                "bag-roll check the way the sustain rule calls for",
      "cause": "KC-009"},
     {"answer": "There's no spare roll kept behind the one in use, so "
                "running low has no backup", "cause": "KC-011"},
     {"answer": "Whoever walked the dog last isn't necessarily the one "
                "who's supposed to check the roll, so it falls through",
      "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Clip the lead back on its hook right now and check the bag "
             "roll: if it's down to the last few, swap it for the spare. "
             "Check the food bin's level against the scoop and refill it "
             "if it has dropped that low, and move any treatment sitting "
             "loose in the caddy behind a closed door above reach.",
   "victory": "The lead, collar and a full bag roll hang together as one "
              "kit on the hook, the food bin's level sits at or above "
              "the scoop line, and no treatment is loose in the open "
              "caddy.",
  },
 },
 "Seasonal Outdoor Gear": {
  "frictions": [
   {"symptom": "The bag of unmatched single gloves has survived three "
               "changeovers already, including a good ski glove nobody "
               "will actually throw out.",
    "branches": [
     {"answer": "The glove is expensive, and letting it go without "
                "finding its pair feels wasteful even three seasons on",
      "cause": "RC-014"},
     {"answer": "The one-bag-one-changeover rule exists, but nobody's "
                "actually applied it to this bag when the deadline came "
                "around", "cause": "RC-015"},
     {"answer": "Gloves get lost one at a time, so this bag quietly "
                "grows a bit worse every season without anyone noticing "
                "the accumulation", "cause": "RC-017"},
    ]},
   {"symptom": "A bottle of sun cream from two summers ago is still "
               "sitting in the open, low bin a young child is encouraged "
               "to help themselves from.",
    "branches": [
     {"answer": "Sun cream and insect repellent sitting where a small "
                "child can reach and taste them is a safety constraint "
                "that outranks tidy", "cause": "KC-010"},
     {"answer": "Nobody's reading the dates on these bottles at the "
                "changeover the way the sort pass calls for, so old "
                "stock just ages out unseen", "cause": "KC-011"},
     {"answer": "It's sat in that bin through enough seasons that an old "
                "bottle doesn't register as different from a fresh one",
      "cause": "RC-017"},
    ]},
   {"symptom": "An umbrella is standing spike up in the stand at exactly "
               "face height, instead of points down the way the "
               "standard calls for.",
    "branches": [
     {"answer": "An upright spike at a toddler's eye height is a safety "
                "constraint independent of how tidy the stand looks",
      "cause": "KC-010"},
     {"answer": "Nobody's specifically the one who checks the stand when "
                "umbrellas go back in, so however it lands stays that "
                "way", "cause": "RC-013"},
     {"answer": "There's no habit tied to a specific moment that flips a "
                "wrongly stood umbrella, so it only gets noticed by "
                "chance", "cause": "KC-009"},
    ]},
  ],
  "first_15": {
   "action": "Tip every glove, mitten and hat from this season's bin "
             "onto the floor and match them into pairs. Put any single "
             "into the dated singles bag, and check the sun cream and "
             "insect repellent for their dates, moving anything expired "
             "out of the low bin.",
   "victory": "Every glove and mitten in the bin is matched into a pair, "
              "the singles bag carries today's date, and no expired sun "
              "cream or insect repellent remains in the low bin.",
  },
 },
 "Cleaning and Utility Zone": {
  "frictions": [
   {"symptom": "The old vacuum has held its corner for over a year, but "
               "the main one has never actually broken down long enough "
               "to need it.",
    "branches": [
     {"answer": "Getting rid of a machine that still works feels "
                "wasteful, even though it isn't functioning as an actual "
                "backup", "cause": "RC-014"},
     {"answer": "Nobody's actually asked the one question the rule calls "
                "for, whether the spare has ever covered for the main "
                "one", "cause": "RC-015"},
     {"answer": "This corner is built for the tools that hang and the "
                "vacuum that parks in one outline; two vacuums is more "
                "than that job needs", "cause": "KC-001"},
    ]},
   {"symptom": "Bleach and an ammonia-based cleaner are capped together "
               "in one closed caddy, alongside a decanted bottle with no "
               "label.",
    "branches": [
     {"answer": "Two cleaners that mix into a gas if they leak together "
                "in a closed box is a safety constraint that outranks "
                "how tidy one caddy looks", "cause": "KC-010"},
     {"answer": "There's no agreed rule yet that every decanted bottle "
                "gets labelled before it goes in the caddy",
      "cause": "KC-008"},
     {"answer": "Nobody's the one who checks this caddy specifically for "
                "two things that shouldn't share a box", "cause": "RC-013"},
    ]},
   {"symptom": "The mop is leaning against the wall instead of clipped "
               "up, and it has slid sideways until it partly blocks the "
               "doorway.",
    "branches": [
     {"answer": "A long-handled tool leaned instead of clipped will "
                "slide and come down across a doorway, a fall risk "
                "independent of how quick it was to lean it there",
      "cause": "KC-010"},
     {"answer": "Leaning it against the wall takes less effort in the "
                "moment than reaching up to clip it, so that's what "
                "happens when hands are full", "cause": "KC-004"},
     {"answer": "Nobody's the one who notices a leaned tool has drifted "
                "across the doorway until someone almost trips on it",
      "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Shake the door mats out right now, hang the broom back on "
             "its clip with the bristles clear of the floor, and check "
             "whether the mop head has actually dried. Pull the "
             "decanted, unlabelled bottle out of the caddy and label it, "
             "or empty it if you can't tell what it is.",
   "victory": "The broom, mop and dustpan all hang clear of the floor, "
              "the mop head is dry, and every bottle in the caddy is "
              "labelled.",
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
 ("Family Hook Zone", "MDF-001",
  "A COAT NOBODY'S WORN SINCE MARCH IS STILL ON THE COLUMN",
  "a single coat hanging alone and dusty on an otherwise bare wall "
  "column, clearly untouched compared to the well used coats beside it"),
 ("Family Hook Zone", "MDF-002", "A CHILD CAN'T REACH THEIR OWN COAT",
  "a small child reaching up unsuccessfully toward a coat hung high on a "
  "shared hook rail, an older child's coat crowding the same hook"),
 ("Family Hook Zone", "MDF-003", "A SCARF HANGS DOWN AT TODDLER NECK "
  "HEIGHT",
  "a scarf hanging in a long loop from a low hook, dangling down to "
  "roughly toddler neck height in an otherwise tidy mudroom entry"),

 ("Bench and Transition Surface", "MDF-004",
  "NOBODY KNOWS WHAT'S UNDER THE BENCH LID",
  "a hinged mudroom bench lid propped half open revealing a crammed, "
  "disorganized storage box underneath"),
 ("Bench and Transition Surface", "MDF-005",
  "THE BENCH SURFACE HAS MORE THAN THREE THINGS ON IT",
  "a mudroom bench seat covered in several unrelated household items "
  "instead of a bare seat"),
 ("Bench and Transition Surface", "MDF-006",
  "SOMEONE'S BALANCING ON ONE LEG TO PULL OFF A BOOT",
  "a person balancing on one leg on a wet mudroom floor while trying to "
  "remove a boot, the bench seat behind them buried under bags"),

 ("Shoe and Boot Storage", "MDF-007",
  "A PAIR IS STILL WAITING FOR A WINTER THAT HASN'T COME",
  "an untouched pair of heavy winter boots standing on a shoe rack in a "
  "room otherwise full of current season footwear"),
 ("Shoe and Boot Storage", "MDF-008",
  "WET SOLES ARE LEAVING A FILM PAST THE TRAY",
  "a faint wet shoe print trail on a hard floor leading from an empty "
  "boot tray toward a doorway"),
 ("Shoe and Boot Storage", "MDF-009",
  "MUD HAS CAKED UNDER THE RAIL WHERE NOBODY LOOKS",
  "a close view of the underside of a wire shoe rack rail caked with "
  "dried mud, hidden from a standing view"),

 ("Pet Station", "MDF-010",
  "THE FOOD BIN LIVES HERE, THE BOWL LIVES IN THE KITCHEN",
  "a sealed pet food bin sitting in a mudroom corner far from a food "
  "bowl visible through a doorway into a kitchen"),
 ("Pet Station", "MDF-011",
  "TREATMENTS SIT LOOSE AT BAG-FETCHING HEIGHT",
  "flea and worming treatment packets sitting loose in an open caddy at "
  "the same low height as a roll of waste bags"),
 ("Pet Station", "MDF-012", "THE BAG ROLL RAN OUT ON A WALK",
  "an empty cardboard bag roll tube sitting on an otherwise tidy pet "
  "station hook, the lead hanging beside it"),

 ("Seasonal Outdoor Gear", "MDF-013",
  "THE SINGLE GLOVES BAG HAS SURVIVED THREE CHANGEOVERS",
  "a bag stuffed with unmatched single gloves and mittens sitting on a "
  "shelf beside two neatly matched seasonal bins"),
 ("Seasonal Outdoor Gear", "MDF-014",
  "SUN CREAM FROM TWO SUMMERS AGO IS STILL IN THE LOW BIN",
  "an old, faded sun cream bottle sitting in an open low bin at a small "
  "child's reach among gloves and hats"),
 ("Seasonal Outdoor Gear", "MDF-015",
  "AN UMBRELLA IS STANDING POINT UP AT FACE HEIGHT",
  "an umbrella standing spike up in a doorside stand at roughly a "
  "child's face height, among other umbrellas stood correctly points "
  "down"),

 ("Cleaning and Utility Zone", "MDF-016",
  "THE SECOND VACUUM HAS NEVER COVERED A BREAKDOWN",
  "an old, dusty backup vacuum wedged into a mudroom utility corner "
  "beside the newer vacuum actually in use"),
 ("Cleaning and Utility Zone", "MDF-017",
  "BLEACH AND AN AMMONIA CLEANER SHARE ONE SHUT CADDY",
  "a closed cleaning caddy holding a bleach bottle and an ammonia based "
  "cleaner capped together beside an unmarked decanted bottle"),
 ("Cleaning and Utility Zone", "MDF-018",
  "A MOP IS LEANING ACROSS THE DOORWAY",
  "a mop leaned against a wall having slid sideways to partly block a "
  "mudroom doorway, its wall clip hanging empty nearby"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, mudroom-scened art only. The name, meaning, six_s and
# confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "two vacuums crowded into one mudroom utility corner where "
           "only one of them actually gets used every week",
 "KC-002": "a stack of items piled on a mudroom bench with no outbound "
           "basket anywhere nearby to hold them",
 "KC-003": "a sealed pet food bin sitting in a mudroom corner far from "
           "the food bowl visible through a kitchen doorway",
 "KC-004": "a hand lifting a heavy hinged bench lid to reach a spare "
           "shoelace stored underneath the seat",
 "KC-005": "a closed hinged bench box propped open, its contents "
           "impossible to make out from a standing view",
 "KC-006": "a small child reaching up unsuccessfully toward a coat hook "
           "mounted at an adult's own height",
 "KC-007": "a shoe rack with every slot full of current season "
           "footwear, no room left for one more worn pair",
 "KC-008": "an unmarked decanted cleaning bottle sitting in an open "
           "caddy beside two clearly labelled ones",
 "KC-009": "an umbrella standing upright with its spike up in a "
           "doorside stand nobody has straightened in days",
 "KC-010": "a scarf hanging in a long loop from a low mudroom hook at "
           "roughly toddler neck height",
 "KC-011": "an empty cardboard bag roll tube sitting on a pet station "
           "hook with no spare roll behind it",
 "KC-012": "two coats crowded onto one shared hook rail instead of each "
           "hanging on its own named column",
 "RC-013": "a mop leaning loose against a mudroom wall instead of "
           "hanging on its own clip",
 "RC-014": "a good winter coat hanging untouched on its column while "
           "the coats beside it show real daily wear",
 "RC-015": "a single unmatched glove sitting in a bag that has already "
           "survived more than one seasonal changeover",
 "RC-016": "the underside of a wire shoe rack rail caked with dried mud "
           "nobody reaches without unloading the whole rack",
 "RC-017": "a hook mounted at a height that stopped matching the "
           "shortest person in the house seasons ago",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Family Hook Zone": [
  "Wipe the rail and the wall behind it in downward strokes, working the "
  "grey shoulder-height smear until it lifts.",
  "Brush the shoulders and collar of each coat with a soft clothing "
  "brush before it goes back on its column.",
  "Vacuum the floor strip under the hooks with the crevice tool, working "
  "into the corner where it meets the skirting.",
 ],
 "Bench and Transition Surface": [
  "Wipe the seat's front edge and apron where boot heels leave a dark "
  "rub line, letting the cleaner sit before you wipe.",
  "Pull the bench away from the wall and vacuum the drift of grit and "
  "lone socks underneath.",
  "Vacuum a cushioned seat with the upholstery tool, lifting any crumbs "
  "caught in the piping.",
 ],
 "Shoe and Boot Storage": [
  "Knock caked mud off boots outdoors and brush the welts and treads "
  "clear before they come back inside.",
  "Wipe each rail and shelf, working the dried mud off the underside "
  "where you never look.",
  "Hose and scrub the lipped tray outside until the lip and corners run "
  "clean.",
 ],
 "Pet Station": [
  "Wash the scoop in hot soapy water and dry it fully before it goes "
  "back in the bin.",
  "Send the paw towel through the wash with the door mats in the same "
  "load.",
  "Scrub the waterline ring in the water bowl and the dried film in the "
  "food bowl daily.",
 ],
 "Seasonal Outdoor Gear": [
  "Vacuum the sand and grit from the corners of each emptied glove bin "
  "before refilling it.",
  "Tip the umbrella stand over a bin and wipe or rinse the inside before "
  "the umbrellas go back.",
  "Wipe the high shelf and the closed off-season bin lids before you "
  "open anything stored there.",
 ],
 "Cleaning and Utility Zone": [
  "Comb the broom bristles clear of trapped hair and grit over the bin "
  "before hanging it back up.",
  "Cut the wound hair off the vacuum's brush bar with scissors and pull "
  "it free.",
  "Rinse the mop head under running water until it runs clear, then "
  "wring and hang it to dry.",
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
 {"id": "MDA-001", "zone": "Family Hook Zone",
  "title": "CLEAR THE WRONG-COLUMN COATS AND FIX THE LOW HOOKS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Walk the whole wall column by column, return anything on the "
          "wrong person's column, enforce one coat one bag one hat, and "
          "move any dangling scarf away from toddler height.",
  "why": "A coat on the wrong column and a scarf hanging low enough to "
         "reach a toddler's neck both cost the space a working column "
         "needs.",
  "inputs": ["none beyond the wall's own hooks"],
  "steps": [
   "Hang your own coat up right now and walk the whole wall column by "
   "column. Move anything sitting on the wrong person's column back to "
   "its owner, take down any coat, bag or hat on a column that already "
   "has its one coat, one bag, one hat filled, and move any scarf or "
   "drawstring hanging low enough to reach a toddler's neck up a hook.",
   "Leave the floor under the hooks bare before you finish."],
  "causes": ["KC-012", "KC-006", "KC-010", "KC-008"],
  "victory": "Every column holds no more than one coat, one bag and one "
             "hat, nothing dangles low enough to reach toddler height, "
             "and the floor under the hooks is bare.",
  "next": "MDS-001",
  "art": "a hand moving a coat from the wrong column back to its owner's "
         "while a scarf is lifted off a low hook to a higher one"},

 {"id": "MDA-002", "zone": "Family Hook Zone",
  "title": "SETTLE THE FOURTH COAT AND REMEASURE HOOK HEIGHT",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Run the one-week honest test on any coat that hasn't been "
          "worn, move it to the wardrobe if it fails, and remeasure hook "
          "height against the shortest person who actually uses the "
          "wall.",
  "why": "A coat kept because letting it go feels like admitting "
         "something, and a hook set for an adult's height on a wall a "
         "child also uses, both cost more than they earn.",
  "inputs": ["a marker", "a measuring tape", "a spare hook if needed"],
  "steps": [
   "Live with any untouched coat for a week and count honestly whether "
   "it moved. If it didn't, take it down and move it to its owner's "
   "wardrobe today.",
   "Stand the shortest household member at the wall and adjust or add a "
   "hook to their own reach.",
   "Write each person's name on their column at their own eye height."],
  "causes": ["RC-014", "RC-015", "KC-001", "KC-006"],
  "victory": "No untouched coat has occupied a column for more than a "
             "week, and every hook sits at the reach of the person whose "
             "column it is.",
  "next": "MDA-001",
  "art": "a hand hanging a name card at a newly lowered hook height "
         "beside a coat being carried up to a wardrobe"},

 {"id": "MDA-003", "zone": "Bench and Transition Surface",
  "title": "CLEAR THE BENCH TO BARE WOOD",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the bench to bare wood, carry stray items to the rooms "
          "they belong in, and give the outbound basket its one real "
          "job.",
  "why": "Every object on the bench beyond three is one more reason "
         "somebody ends up balancing on one leg to change shoes.",
  "inputs": ["the outbound basket itself"],
  "steps": [
   "Sit down right now and clear the bench to bare wood. Carry every "
   "item that belongs in another room there immediately rather than "
   "sliding it down the bench, and put whatever is genuinely leaving the "
   "house tomorrow into the outbound basket at the end, nothing else."],
  "causes": ["KC-003", "KC-002", "KC-010"],
  "victory": "The seat is bare enough for two people to lace boots at "
             "once, no more than three things sit on the surface, and "
             "the outbound basket holds only what leaves on the next "
             "trip out.",
  "next": "MDS-002",
  "art": "a hand carrying an armful of misplaced items off a mudroom "
         "bench into the house, one item going into a labelled outbound "
         "basket"},

 {"id": "MDA-004", "zone": "Bench and Transition Surface",
  "title": "EMPTY THE LID AND GIVE IT ONE HONEST JOB",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Empty the hinged bench box completely, run the honest "
          "lid-lift count for a week, and refill it only with things "
          "used while sitting.",
  "why": "Storage under a seat you sit on ten times a day is storage "
         "you will never open unless it earns that spot on purpose.",
  "inputs": ["spare laces", "a shoe horn", "a rag for wiping soles"],
  "steps": [
   "Empty the storage box completely onto the floor and sort what's "
   "actually inside.",
   "Keep only what you'd use while sitting: spare laces, a shoe horn, a "
   "rag for wiping soles.",
   "If the box is still empty after a week of real use, leave it empty "
   "rather than refilling it out of habit."],
  "causes": ["KC-005", "KC-004", "RC-015"],
  "victory": "The bench box holds only what's genuinely used while "
             "sitting, and an honestly empty box stays empty rather than "
             "being refilled out of habit.",
  "next": "MDA-003",
  "art": "a bench storage box emptied completely onto the floor, a small "
         "pile of laces and a shoe horn set aside to go back in"},

 {"id": "MDA-005", "zone": "Shoe and Boot Storage",
  "title": "DRAIN THE TRAY AND CLEAR THE FOUR-WEEK TEST",
  "minutes": 15, "players": "1", "six_s": "Straighten", "from_first_15": True,
  "goal": "Move every dry pair from the tray to the rack, and pull "
          "anything that hasn't earned its slot in the last four weeks.",
  "why": "A dry pair still parked on the tray and a pair nobody's worn "
         "in a month both cost the door the space this season's "
         "footwear needs.",
  "inputs": ["a dated slip of paper"],
  "steps": [
   "Check the tray right now for any pair that has finished draining and "
   "move it up to the rack soles down, toes out. While you're there, "
   "pull any pair that hasn't been worn in the last four weeks and set "
   "it aside with today's date to move to the wardrobe."],
  "causes": ["KC-003", "KC-010", "RC-015", "KC-007"],
  "victory": "The tray holds only what's still actually wet, every dry "
             "pair sits on the rack soles down and toes out, and nothing "
             "unworn for four weeks is still taking a slot without a "
             "dated slip.",
  "next": "MDS-003",
  "art": "a hand lifting a dry pair of boots off a tray onto a rack "
         "soles down, another pair set aside with a dated paper slip in "
         "its toe"},

 {"id": "MDA-006", "zone": "Shoe and Boot Storage",
  "title": "WASH THE TRAY AND CLEAR THE RAIL'S UNDERSIDE",
  "minutes": 30, "players": "1", "six_s": "Shine",
  "goal": "Tip the boot tray out and wash it, and reach under the rail "
          "to clear the caked mud nobody sees from standing height.",
  "why": "Dried mud on a tray turns to dust that gets walked straight "
         "back inside, and a caked rail underside is where rust starts "
         "unseen.",
  "inputs": ["a stiff scrubbing brush", "a garden hose or outdoor tap"],
  "steps": [
   "Carry the tray outside, tip out the grit, and scrub it with a stiff "
   "brush until the lip runs clean.",
   "Unload the rack shelf by shelf and wipe the underside of each rail "
   "where mud cakes unseen.",
   "Flag any rust or burr on the rail while it's unloaded, and vacuum "
   "the floor of the rack before boots go back."],
  "causes": ["RC-016", "RC-013", "RC-017"],
  "victory": "The tray runs clean when rinsed, the underside of every "
             "rail is free of caked mud, and the boots go back soles "
             "down, toes out.",
  "next": "MDA-005",
  "art": "a boot tray being scrubbed clean outdoors beside a shoe rack "
         "with its shelves unloaded and the underside of a rail being "
         "wiped"},

 {"id": "MDA-007", "zone": "Pet Station",
  "title": "CHECK THE HOOK, THE BAGS AND THE BIN",
  "minutes": 15, "players": "1", "six_s": "Sustain", "from_first_15": True,
  "goal": "Clip the lead back on its hook, check the bag roll and the "
          "food bin's level, and move any loose treatment behind a "
          "closed door.",
  "why": "A bag roll checked when the lead goes back is the only place "
         "that shortfall gets caught before it happens a quarter mile "
         "from the house.",
  "inputs": ["a spare bag roll"],
  "steps": [
   "Clip the lead back on its hook right now and check the bag roll: if "
   "it's down to the last few, swap it for the spare. Check the food "
   "bin's level against the scoop and refill it if it has dropped that "
   "low, and move any treatment sitting loose in the caddy behind a "
   "closed door above reach."],
  "causes": ["KC-009", "KC-011", "KC-010"],
  "victory": "The lead, collar and a full bag roll hang together as one "
             "kit on the hook, the food bin's level sits at or above the "
             "scoop line, and no treatment is loose in the open caddy.",
  "next": "MDS-004",
  "art": "a hand clipping a lead back onto its hook beside a full bag "
         "roll, a food bin's level checked against its scoop"},

 {"id": "MDA-008", "zone": "Pet Station",
  "title": "MOVE THE FOOD BIN TO WHERE THE BOWL ACTUALLY SITS",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Decide honestly where the bowl sits and move the food bin "
          "there, keeping this zone to departures and arrivals only.",
  "why": "This zone is for leads, bags, towels and paw washes; a feeding "
         "job it never signed up for costs a walk across the house every "
         "meal.",
  "inputs": ["a hand truck or box for the move"],
  "steps": [
   "Walk to wherever the bowl actually sits and measure whether the food "
   "bin will fit there.",
   "If it fits, move the bin, scoop and spare bag stock to the bowl's "
   "room today.",
   "If it doesn't fit, treat that as a kitchen storage problem to solve, "
   "not a reason to keep the walk."],
  "causes": ["KC-003", "RC-015", "KC-004"],
  "victory": "The food bin sits at the bowl, and this zone holds only "
             "what's needed for departures and arrivals: lead, bags, "
             "towel, coat, paw wash.",
  "next": "MDA-007",
  "art": "a pet food bin being carried out of a mudroom toward a kitchen "
         "doorway where a food bowl actually sits"},

 {"id": "MDA-009", "zone": "Seasonal Outdoor Gear",
  "title": "MATCH THE GLOVES AND CHECK THE DATES",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Match every glove into a pair, bag the singles with today's "
          "date, and clear any expired sun cream or repellent from the "
          "low bin.",
  "why": "An unmatched glove and an expired bottle in a low bin both "
         "cost the bin's one job, which is holding what this season "
         "actually needs.",
  "inputs": ["a dated singles bag"],
  "steps": [
   "Tip every glove, mitten and hat from this season's bin onto the "
   "floor and match them into pairs. Put any single into the dated "
   "singles bag, and check the sun cream and insect repellent for their "
   "dates, moving anything expired out of the low bin."],
  "causes": ["RC-017", "KC-011", "KC-010"],
  "victory": "Every glove and mitten in the bin is matched into a pair, "
             "the singles bag carries today's date, and no expired sun "
             "cream or insect repellent remains in the low bin.",
  "next": "MDS-005",
  "art": "a hand matching gloves into pairs on the floor beside a dated "
         "singles bag and an old sun cream bottle set aside"},

 {"id": "MDA-010", "zone": "Seasonal Outdoor Gear",
  "title": "CLOSE THE SEASON, LABEL THE MONTH, AND SETTLE THE SINGLES "
           "BAG",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Run the full seasonal changeover: wash and dry everything "
          "going into storage, date the singles bag's deadline, and "
          "close the off-season bin with the month on its lid.",
  "why": "Gloves are lost one at a time, so the changeover is the one "
         "moment that actually catches the drift before it becomes "
         "permanent.",
  "inputs": ["a marker", "a label", "a donation box"],
  "steps": [
   "Wash and fully dry anything going into off-season storage before "
   "it's boxed.",
   "Check the singles bag's date: anything unmatched since the last "
   "changeover leaves the house now, with one exception for a genuinely "
   "growing child's survivor.",
   "Label the closed bin with the month and the short order (gloves "
   "matched, hats washed, creams checked, umbrellas emptied), then lift "
   "it to the high shelf."],
  "causes": ["RC-014", "RC-015", "KC-011"],
  "victory": "The off-season bin is closed, dated and on the high shelf, "
             "and no single glove has survived more than one changeover "
             "without a genuine reason.",
  "next": "MDA-009",
  "art": "a closed seasonal storage bin with a month label being lifted "
         "onto a high shelf, a singles bag being emptied into a "
         "donation box beside it"},

 {"id": "MDA-011", "zone": "Cleaning and Utility Zone",
  "title": "HANG THE TOOLS AND CHECK THE MOP HEAD",
  "minutes": 15, "players": "1", "six_s": "Sustain", "from_first_15": True,
  "goal": "Hang the broom back on its clip, check whether the mop head "
          "has dried, and label the one unmarked bottle in the caddy.",
  "why": "A mop stored wet is what turns this corner sour, and an "
         "unmarked bottle is a guess waiting to be made by someone in a "
         "hurry.",
  "inputs": ["a marker or a blank label"],
  "steps": [
   "Shake the door mats out right now, hang the broom back on its clip "
   "with the bristles clear of the floor, and check whether the mop head "
   "has actually dried. Pull the decanted, unlabelled bottle out of the "
   "caddy and label it, or empty it if you can't tell what it is."],
  "causes": ["KC-010", "KC-004", "KC-008"],
  "victory": "The broom, mop and dustpan all hang clear of the floor, "
             "the mop head is dry, and every bottle in the caddy is "
             "labelled.",
  "next": "MDS-006",
  "art": "a hand hanging a broom back on its wall clip beside a mop head "
         "checked for dryness, a labelled bottle being set back in a "
         "caddy"},

 {"id": "MDA-012", "zone": "Cleaning and Utility Zone",
  "title": "SEPARATE THE BLEACH AND SETTLE THE SECOND VACUUM",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Split bleach and any ammonia-based cleaner into separate "
          "containers for good, and decide the second vacuum's fate with "
          "the one real question.",
  "why": "Bleach and an ammonia-based cleaner leaking together in a shut "
         "caddy make a gas nobody can outrun fast enough in this small a "
         "room.",
  "inputs": ["a second closed container or shelf"],
  "steps": [
   "Move the bleach and the ammonia-based cleaner into two separate, "
   "never-shared containers.",
   "Ask out loud whether the spare vacuum has ever actually covered for "
   "the main one in the last year.",
   "If the honest answer is no, pass the spare vacuum to someone with "
   "none, and give the corner back to the one you use every week."],
  "causes": ["KC-010", "RC-014", "RC-015", "KC-001"],
  "victory": "Bleach and an ammonia-based cleaner never share a "
             "container, and the corner holds only the vacuum actually "
             "used every week.",
  "next": "MDA-011",
  "art": "a bleach bottle and an ammonia based cleaner being separated "
         "onto different shelves, an old backup vacuum being carried out "
         "to a neighbor"},

 {"id": "MDA-013", "zone": None, "title": "THE FULL MUDROOM HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk all six zones checking hook anchoring, scarves and "
          "drawstrings, wet-floor slip zones, treatments and cleaners "
          "locked away, and every tool hanging clear of a doorway.",
  "why": "This is the room where every zone carries its own hazard, "
         "wet floors, poison-grade treatments, a bleach caddy, an "
         "overloaded rail, so the hazards only get found if someone "
         "checks all six on purpose.",
  "inputs": ["a childproof latch if needed", "a marker for labels"],
  "steps": [
   "Push on the loaded end of the hook rail and confirm it's anchored "
   "into a stud, not just plasterboard.",
   "Check for any scarf or drawstring hanging low enough to reach a "
   "toddler's neck.",
   "Walk the floor from the boot tray to the doorway and confirm it's "
   "bare and dry.",
   "Confirm every treatment and chemical sits behind a closed door above "
   "reach, and bleach never shares a container with an ammonia-based "
   "cleaner.",
   "Check that no long-handled tool is leaning loose across a doorway."],
  "causes": ["KC-010", "RC-013", "RC-016", "RC-017"],
  "victory": "No hook pulls at a touch, no scarf or drawstring hangs at "
             "toddler height, the floor from tray to door is bare and "
             "dry, every treatment and chemical is locked away "
             "correctly, and no tool leans across a doorway.",
  "next": "MDA-014",
  "art": "a hand testing a loaded hook rail for give, a cleared wet "
         "floor path visible behind toward a doorway with no leaning "
         "tools"},

 {"id": "MDA-014", "zone": None, "title": "THE DOOR-DAY SWEEP",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "The moment everyone's in for the evening, walk all six zones "
          "once in the order the house actually uses them: coats to "
          "their columns, boots to the rack or tray, the pet kit back on "
          "its hook, and the tools re-hung.",
  "why": "Every zone in this room has its own trigger already; the "
         "sweep is what actually fires all six on the same evening "
         "instead of one zone drifting behind the rest.",
  "inputs": ["none beyond the room's own hooks, tray and clips"],
  "steps": [
   "Hang every coat and bag on its own column as you come in.",
   "Set wet boots on the tray, dry pairs up on the rack.",
   "Clip the pet lead back on its hook and check the bag roll.",
   "Hang the broom, mop and dustpan back on their clips before the day "
   "ends."],
  "causes": ["KC-009", "RC-013"],
  "victory": "All six zones pass their own leave-behind standard on the "
             "same evening, in one walk.",
  "next": "MDA-015",
  "art": "a hand completing the last step of an evening sweep, hanging a "
         "mop back on its clip beside a rack of dry boots and a hooked "
         "coat"},

 {"id": "MDA-015", "zone": None, "title": "THE SEASONAL CHANGEOVER DAY",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "On a fixed day twice a year, swap the seasonal gear bins, "
          "re-check every hook height against who's grown, and clear "
          "anything that failed its honest test all cycle.",
  "why": "A changeover that only happens when someone remembers stops "
         "happening within a season; a fixed day is what actually keeps "
         "this room matched to the people who use it.",
  "inputs": ["a calendar reminder"],
  "steps": [
   "Pick a fixed day each spring and autumn and put it on a shared "
   "calendar.",
   "Swap the seasonal gear bins and remeasure hook heights against "
   "whoever's grown since the last changeover.",
   "Clear any coat, pair of boots, or bag of singles that failed its "
   "honest test since the last changeover."],
  "causes": ["KC-006", "KC-001", "RC-015"],
  "victory": "A changeover happens on the same calendar day twice a "
             "year, hook heights match who actually uses them, and "
             "nothing that failed its own test all cycle is still taking "
             "a slot.",
  "next": "MDA-013",
  "art": "a calendar reminder pinned near a mudroom wall while a "
         "seasonal bin is swapped and a hook height is remeasured "
         "against a child standing beside it"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a mudroom, one per zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("MDE-001", "A WET SCHOOL MORNING SENDS EVERYONE OUT AT ONCE",
  "Every coat, bag and hat has to come off the wall inside two minutes "
  "flat while the car is already running outside.",
  ["MDZ-001"],
  "Every person grabs exactly their own coat, bag and hat from their own "
  "column without asking where anything is.",
  "If someone had to search another person's column, or a coat was "
  "buried under someone else's, the wrong-column reset never happened. "
  "Draw MDA-001.",
  "several coats being pulled quickly off a hook wall by different "
  "hands, each hand reaching straight to its own named column"),
 ("MDE-002", "TWO PEOPLE NEED TO LACE BOOTS AT THE SAME TIME",
  "Two people arrive at the same moment and both need the bench to sit "
  "down and deal with wet boots.",
  ["MDZ-002"],
  "Both people sit down at once because the seat is bare and no more "
  "than three things sit on the surface.",
  "If one person had to stand on one leg because the seat was covered "
  "in bags, the bench-clearing reset never happened. Draw MDA-003.",
  "two people sitting side by side on a bare mudroom bench lacing boots "
  "at the same time"),
 ("MDE-003", "A SUDDEN DOWNPOUR SENDS EVERYONE IN SOAKED",
  "Everyone comes in from a sudden downpour at once, boots dripping, and "
  "all of them need somewhere to drain right now.",
  ["MDZ-003"],
  "Every wet pair lands on the tray with room to spare, and the path "
  "from the tray to the doorway stays bare underfoot.",
  "If a wet pair ended up on the rack, or the floor beyond the tray "
  "turned slick, the tray-and-rail reset never happened. Draw MDA-005.",
  "several pairs of dripping wet boots lined up on a boot tray, a bare "
  "dry floor stretching from the tray to the doorway"),
 ("MDE-004", "THE DOG NEEDS A WALK IN THE LAST FIVE MINUTES OF DAYLIGHT",
  "The dog needs walking right now, in the last five minutes before "
  "dark, and the whole kit has to come together in one grab.",
  ["MDZ-004"],
  "The lead, collar and a full bag roll come off the hook together as "
  "one kit, with no separate search for anything.",
  "If the bag roll turned out empty, or the lead and collar weren't "
  "already together, the hook-and-bag check never happened. Draw "
  "MDA-007.",
  "a hand lifting a lead already clipped to its collar off a hook, a "
  "full bag roll threaded on and ready to go"),
 ("MDE-005", "THE FIRST COLD MORNING OF THE YEAR ARRIVES WITHOUT WARNING",
  "The first genuinely cold morning of the year arrives overnight, and "
  "everyone needs gloves and a hat on their way out the door.",
  ["MDZ-005"],
  "Every glove in the bin is already matched into a pair, sized for the "
  "season that's actually here.",
  "If someone pulled out a single glove with no match, the changeover "
  "and the match-and-check pass never happened. Draw MDA-009.",
  "a hand pulling a matched pair of gloves straight out of an open bin "
  "on a cold morning"),
 ("MDE-006", "MUDDY FOOTPRINTS TRACK ACROSS THE FLOOR RIGHT BEFORE "
  "GUESTS ARRIVE",
  "Muddy footprints track across the entry floor twenty minutes before "
  "guests are due, and every cleaning tool has to be ready to go.",
  ["MDZ-006"],
  "The broom and mop are already hanging dry and ready, and the right "
  "cleaner is already labelled and easy to grab.",
  "If the mop head was still damp from last time, or a bottle had to be "
  "guessed at, the hang-and-check pass never happened. Draw MDA-011.",
  "a hand lifting a dry, ready mop off its wall clip beside a clearly "
  "labelled cleaner bottle"),
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
        "related": {"standard": f"MDS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your mudroom, "
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
    standard_id = (f"MDS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"MDS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "MDR-001", "title": "THE MUDROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START AT THE HOOKS.",
        "objective": "The mudroom is where the weather stops: coats, "
                     "boots, the pet, the seasonal gear and the tools "
                     "that keep the entry floor walkable all compete for "
                     "the same short run of wall. This card is the map "
                     "and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"MDZ-001 Family Hook Zone. {start_tip['text']}"
            if start_tip else
            "MDZ-001 Family Hook Zone. Almost everything lying on the "
            "floor is there for one reason: the wall above it ran out of "
            "room."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your mudroom. Put the rest back.",
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
        "safety_first": "Do MDA-013 The Full Mudroom Hazard Walk before "
                        "any rebuild. It takes thirty minutes and covers "
                        "hook anchoring, scarves and drawstrings at "
                        "toddler height, wet-floor slip zones, poison-"
                        "grade treatments and chemicals, and every tool "
                        "hanging clear of a doorway.",
        "related": {"contents": "MDZ-001 to MDZ-006, MDF-001 to "
                                 "MDF-018, the shared root causes in "
                                 "ops/root_causes.py, MDA-001 to "
                                 "MDA-015, MDS-001 to MDS-006, MDE-001 "
                                 "to MDE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole mudroom "
                           "in its settled state, a hook wall with named "
                           "columns, a bench with a bare seat and an "
                           "outbound basket, a shoe rack with a boot "
                           "tray by the door, a pet station, a seasonal "
                           "gear shelf, and a cleaning corner all "
                           "visible in one frame",
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
    return {"deck": "mudroom", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "MDA-013" for c in cards), "no safety walk card"
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
    print(f"  deck        mudroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
