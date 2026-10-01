#!/usr/bin/env python3
"""
Build the Kids Bedroom deck: 69 cards, generated, never hand-copied.

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
build_guest_bathroom_deck.py, build_family_room_deck.py,
build_living_room_deck.py and build_mudroom_deck.py proved the pattern for
the first fifteen rooms; this is the sixteenth. Purpose, done_looks_like,
the standard, the trigger, the first-15 action and its victory condition are
quoted from the Manual, not rewritten, and gate() at the bottom asserts they
are still character-for-character identical. The 18 frictions (three per
zone) are likewise derived straight from the Manual's own diagnosis layer,
in this file's own zone order, not retyped, so this deck cannot silently
diverge from the diagnostic engine already shipped on the site's zone
pages. That diagnosis layer was authored directly into content.json as part
of this same B9 cycle: Kids Bedroom carried the rest of its rich Manual
content (purpose, done_looks_like, passes, the_call, watch_for,
leave_behind, shine_detail) already, but no diagnosis and no deck until
this file.

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
count or padded toward a round number: a sleeping child, a crawling
sibling reaching into a toy bin, a jammed dresser drawer, an unanchored
chest of drawers, and daily medication packed for school all happen in the
same six zones, which gives this room unusually broad real reach across
the vocabulary.

WHY THE ZONE ORDER IS NOT THE MANUAL'S OWN LIST ORDER
------------------------------------------------------
content.json lists this room's zones as Bed and Sleep Zone, Toy Storage
Zone, Study Desk, Clothing Closet, Dresser Drawers, School and Activity
Launch Zone. The room's own "tips" field, quoted verbatim on the room card,
says to start at the Toy Storage Zone ("Clear the floor first, working out
of the Toy Storage Zone"): the deck's play order follows that real, already
-published instruction rather than the Manual's storage order, so the room
card's own "start here" line and the tip it quotes name the same zone.
Nothing about zone lookup below depends on this file's ZONE_ORDER matching
content.json's list order; each zone is read from the Manual by name.

WHAT THE BUDGET IS AND WHY
---------------------------
Kids Bedroom ships as a free typeset page, the same stage every prior room
in this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and it
does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). This room has
six real Manual zones, the same shape Family Room's, Living Room's and
Mudroom's own six-zone decks used: six ZONE cards, eighteen FRICTION cards
(three per zone), seventeen reachable ROOT CAUSE cards, fifteen ACTION
cards (two per zone plus three whole-room), six STANDARD cards and six
EVENT cards. 69 cards in total, not padded or trimmed to match
ops/cardtext/derive_room_deck.py's own generic BUDGET dict, which reports a
fixed 72/7-zone template for every room regardless of its real zone count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Kids Bedroom deck to disclose against: no free Kids Bedroom product exists
on the site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_kids_bedroom_deck.py
Out:  ops/cardtext/kids-bedroom-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "kids-bedroom-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Kids Bedroom"

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
# every numbered item has to be a visible object in the hero. Order follows
# this file's own play order (see module docstring), not the Manual's list
# order.
# ---------------------------------------------------------------------------

ZONES = {
 "Toy Storage Zone": {
  "id": "KBZ-001", "order": 1, "difficulty": 3,
  "tagline": "SIX BINS, ONE FAMILY EACH. THE CARPET STAYS CLEAR.",
  "callouts": [
   "Six open bins standing no higher than the child's own shoulder",
   "A photo label taped to the front face of every bin",
   "Blocks, vehicles and small figures each kept in their own bin",
   "A patch of clear carpet large enough to lie down on",
   "One rotation box sitting on the wardrobe's top shelf",
   "A dated label on the rotation box's lid",
  ],
  "art": ("a kids' bedroom toy storage zone with six open bins at child "
          "shoulder height each carrying a photo label on its front face, "
          "blocks and vehicles and figures sorted into their own bins, a "
          "wide patch of clear carpet, and one dated rotation box up on "
          "the wardrobe top shelf"),
 },
 "Bed and Sleep Zone": {
  "id": "KBZ-002", "order": 2, "difficulty": 2,
  "tagline": "ONE DUVET, ONE PILLOW. NOTHING DANGLES AT TODDLER HEIGHT.",
  "callouts": [
   "A duvet pulled flat with one pillow squared at the head",
   "Three or four stuffed animals resting on the bed itself",
   "The rest of the stuffed animals sitting in an open basket at the foot "
   "of the bed",
   "A nightlight cord run behind the bed leg, out of the walking path",
   "A clear walkable path from the pillow to the door",
   "No cord or drawstring hanging low enough to reach a toddler's neck",
  ],
  "art": ("a child's bedroom sleep zone with a duvet pulled flat and one "
          "pillow squared at the head, three or four stuffed animals on "
          "the bed and the rest visible in an open basket at the foot, a "
          "nightlight cord tucked behind the bed leg, and a completely "
          "clear path from the pillow to the door"),
 },
 "Study Desk": {
  "id": "KBZ-003", "order": 3, "difficulty": 2,
  "tagline": "ONE TRAY FOR LIVE WORK. EVERYTHING ELSE HAS A HOME.",
  "callouts": [
   "A desk surface bare except for a lamp",
   "A pen cup standing within reach of the writing hand",
   "One tray holding only live, current work",
   "A laptop charger threaded through a clip at the desk edge",
   "Books standing on the shelf above, none stacked on the desk",
   "An empty chair pushed in at the desk",
  ],
  "art": ("a child's study desk cleared to a lamp, a standing pen cup and "
          "one tray of live work, a laptop charger threaded through a "
          "desk-edge clip, books standing on the shelf above rather than "
          "stacked on the surface, and an empty chair pushed in"),
 },
 "Clothing Closet": {
  "id": "KBZ-004", "order": 4, "difficulty": 3,
  "tagline": "THE ROD DROPS TO THEIR REACH. ONLY WHAT FITS TODAY HANGS.",
  "callouts": [
   "A rod lowered to the child's own reach, no stool needed",
   "Every hanger the same type, all facing the same way",
   "Shirts, dresses and jackets grouped with a hand's width gap between "
   "each group",
   "Shoes standing in pairs on the floor rack",
   "A backpack hanging on its own low hook",
   "One labelled next size box on the top shelf",
  ],
  "art": ("a child's clothing closet with the rod lowered to the child's "
          "own reach, every hanger the same type and facing the same "
          "way, shirts and dresses and jackets grouped with a visible gap "
          "between each group, shoes standing in pairs on a floor rack, a "
          "backpack on its own low hook, and one labelled next size box "
          "on the top shelf"),
 },
 "Dresser Drawers": {
  "id": "KBZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE CATEGORY PER DRAWER. EVERY DRAWER SHUTS WITH ONE PUSH.",
  "callouts": [
   "Five drawers, each holding exactly one clothing category",
   "A picture label on every drawer front",
   "Socks and underwear standing upright in visible rows",
   "Every drawer closing flush with a single push",
   "An anti-tip strap anchoring the dresser to the wall",
   "A bare dresser top with nothing worth climbing for",
  ],
  "art": ("a kids' bedroom dresser with five drawers each holding one "
          "category and carrying a picture label on its front, socks and "
          "underwear standing upright in visible rows, every drawer "
          "closing flush with a single push, an anti-tip strap anchoring "
          "it to the wall, and a bare top with nothing worth climbing "
          "for"),
 },
 "School and Activity Launch Zone": {
  "id": "KBZ-006", "order": 6, "difficulty": 1,
  "tagline": "BAG ON THE HOOK. FLOOR COMPLETELY CLEAR.",
  "callouts": [
   "A backpack hanging packed and zipped on its own hook",
   "Shoes standing side by side directly underneath the hook",
   "Signed forms sitting in the backpack's front pocket",
   "A sports bag hanging on the second hook",
   "An instrument case standing upright against the wall",
   "A completely clear floor beneath the hooks",
  ],
  "art": ("a school and activity launch corner by a bedroom door with a "
          "packed, zipped backpack hanging on its own hook, shoes "
          "standing side by side directly underneath, a sports bag on a "
          "second hook, an instrument case standing upright against the "
          "wall, and a completely clear floor beneath"),
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
 "Bed and Sleep Zone": {
  "frictions": [
   {"symptom": "A blind cord or looped drawstring hangs down near the "
               "pillow, well within reach of a sleeping child's neck.",
    "branches": [
     {"answer": "A cord or loop hanging at a sleeping child's neck "
                "height is a strangling risk that outranks how the "
                "window dressing looks", "cause": "KC-010"},
     {"answer": "There's no separate rule yet that says cords get "
                "cleated up near a bed specifically, only that the room "
                "should look tidy", "cause": "KC-008"},
     {"answer": "It's hung in that exact spot for so long that a "
                "dangling cord reads as part of the window, not a "
                "hazard", "cause": "RC-017"},
    ]},
   {"symptom": "Stuffed animals have spread off the basket and onto the "
               "floor by the door, far more than the handful that "
               "actually get slept with.",
    "branches": [
     {"answer": "Most of them were gifts, and moving one out feels like "
                "admitting it won't be missed, not a decision about what "
                "gets slept with", "cause": "RC-014"},
     {"answer": "Nobody's actually pulled them all out and counted what "
                "was really in the bed the way the sort pass calls for",
      "cause": "RC-015"},
     {"answer": "The basket is sized for a handful a child actually "
                "sleeps with, and a floor full of animals is more than "
                "that job needs", "cause": "KC-001"},
    ]},
   {"symptom": "The duvet most mornings no longer matches the made-bed "
               "photo taped inside the wardrobe door, and it happens on "
               "the mornings an adult remade it rather than the child.",
    "branches": [
     {"answer": "Whoever ends up remaking the bed on a given morning "
                "isn't the child it's supposed to teach, so the slip "
                "never actually costs the person who caused it",
      "cause": "RC-013"},
     {"answer": "Making the bed isn't actually tied to the school bag "
                "going on some mornings, it just happens whenever, if at "
                "all", "cause": "KC-009"},
     {"answer": "A top sheet, blanket and quilt on top of a duvet is "
                "more layers to square away than a young child can "
                "manage before the door closes", "cause": "KC-004"},
    ]},
  ],
  "first_15": {
   "action": "Check every blind or curtain cord near the bed head right "
             "now and cleat any hanging loop up out of a sleeping "
             "child's reach. Strip the duvet and pillow off, count how "
             "many stuffed animals were actually in the bed, and move "
             "the rest into the basket at the foot where they're still "
             "visible. Square the pillow and pull the duvet flat before "
             "you finish.",
   "victory": "No cord or loop hangs within reach of the pillow, the bed "
              "carries a squared pillow and a flat duvet with only the "
              "animals that fit in two arms on top, and the rest sit "
              "visible in the basket at the foot.",
  },
 },
 "Toy Storage Zone": {
  "frictions": [
   {"symptom": "Small figures and a loose button battery from a broken "
               "toy sit in an open bin at floor height, well within "
               "reach of a younger sibling who is starting to crawl.",
    "branches": [
     {"answer": "Anything small enough to fit through a toilet roll "
                "tube sitting at a crawling sibling's reach is a safety "
                "constraint that outranks which bin it's tidiest in",
      "cause": "KC-010"},
     {"answer": "It's sat in that low bin through enough tidy-ups that a "
                "choke-sized piece doesn't register as different from "
                "any other toy", "cause": "RC-017"},
     {"answer": "There's no rule yet that says small parts specifically "
                "go up high, only that each toy family gets a bin",
      "cause": "KC-008"},
    ]},
   {"symptom": "A big block set gets tipped across the carpet and walked "
               "away from before anything gets built, then sits "
               "untouched on the floor until the next tidy-up.",
    "branches": [
     {"answer": "Nobody's actually run the rotation trial the way the "
                "sort pass calls for, so the question of whether it's "
                "still wanted just gets deferred", "cause": "RC-015"},
     {"answer": "It's expensive and a relative asks after it, so moving "
                "it to the rotation box feels like deciding they won't "
                "play with it again", "cause": "RC-014"},
     {"answer": "Even with the broken pieces and the orphans already "
                "gone, one growing set alone is more than one bin can "
                "actually hold, and the overflow is what ends up on the "
                "floor", "cause": "KC-007"},
    ]},
   {"symptom": "A bin's photo label shows blocks, but figures and a "
               "puzzle piece have ended up mixed in during a rushed "
               "pickup, so the label no longer matches what's inside.",
    "branches": [
     {"answer": "Two different people put this bin away by two "
                "different rules, one sorting by family and one just "
                "tipping whatever's nearest in", "cause": "KC-012"},
     {"answer": "The label is the only way anyone sees what's actually "
                "in the bin, so once it's wrong the contents are as good "
                "as invisible", "cause": "KC-005"},
     {"answer": "It's been slightly wrong for long enough that a "
                "mismatched label reads as normal rather than a signal "
                "to fix it", "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Tip out the bin nearest the door and check every piece "
             "against the toilet-roll-tube test: anything small enough "
             "to fit through goes up into a bin on the wardrobe top "
             "shelf, out of a younger sibling's reach, right now. Wipe "
             "that bin's photo label clean enough to read, and clear a "
             "lie-down-sized patch of carpet before you stop.",
   "victory": "No choke-sized piece or loose battery sits in a bin at "
              "floor height, the wiped label is readable and matches "
              "what's actually inside, and there's enough clear carpet "
              "to lie down on.",
  },
 },
 "Study Desk": {
  "frictions": [
   {"symptom": "Worksheets and finished exercise books pile up on the "
               "desk surface instead of going to the memory box or "
               "recycling, because no specific sheet has anywhere in "
               "particular it's supposed to end up.",
    "branches": [
     {"answer": "There's no single defined destination for a given "
                "sheet, so it lands wherever the hand opens, on the "
                "desk", "cause": "KC-002"},
     {"answer": "Binning any of it feels like deciding you didn't care, "
                "not a decision about whether this term's work is "
                "current", "cause": "RC-014"},
     {"answer": "Keep, photograph or recycle is a decision that hasn't "
                "actually been made for this sheet, so it gets stacked "
                "instead", "cause": "RC-015"},
    ]},
   {"symptom": "A lamp, a laptop charger and a second extension strip "
               "are all chained into one strip under the desk, with the "
               "water bottle sitting at the same end.",
    "branches": [
     {"answer": "A chain of strips feeding a desk this size is an "
                "overloaded socket, a safety constraint that outranks "
                "how convenient the chain was to build", "cause": "KC-010"},
     {"answer": "Nobody's specifically the one who checks under the desk "
                "for a growing chain of plugs, so it grows until someone "
                "trips over it", "cause": "RC-013"},
     {"answer": "It's been wired that way for so long that one more "
                "strip stopped registering as a change worth noticing",
      "cause": "RC-017"},
    ]},
   {"symptom": "Craft supplies and small toys keep migrating from the "
               "toy storage zone onto the desk, because it's the "
               "nearest flat surface, crowding out the pen cup and the "
               "tray.",
    "branches": [
     {"answer": "It's landing here because the desk is the closest flat "
                "surface, not because anything is actually used at the "
                "desk", "cause": "KC-003"},
     {"answer": "Nothing specific happens at a fixed moment that clears "
                "the desk of stray items, so whatever lands there just "
                "stays", "cause": "KC-009"},
     {"answer": "The drift has been happening for so long that a desk "
                "half covered in toys reads as how this desk normally "
                "looks", "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Clear the desk down to bare wood right now. Sort every "
             "loose sheet of paper into exactly one of three piles, live "
             "work into the tray, keepsake into the memory box, "
             "everything else into recycling, and count the plugs under "
             "the desk, bringing any chain of strips back to one strip "
             "in one wall socket.",
   "victory": "The desk holds only the lamp, the pen cup and one tray of "
              "live work, every other sheet of paper has a verdict, and "
              "exactly one power strip runs from exactly one wall "
              "socket.",
  },
 },
 "Clothing Closet": {
  "frictions": [
   {"symptom": "The rod sits at adult shoulder height, so the child "
               "stands on a step stool or asks for help to get a hanger "
               "down, and getting dressed becomes a two-person job.",
    "branches": [
     {"answer": "The people actually dressing from this rod can't reach "
                "it safely, or at all, without a stool or an adult",
      "cause": "KC-006"},
     {"answer": "The rod's been at that height since it went in, before "
                "anyone measured it against the child's own reach",
      "cause": "RC-017"},
     {"answer": "There's no agreed rule yet that hanger height should "
                "match whoever's actually dressing from this closet",
      "cause": "KC-008"},
    ]},
   {"symptom": "The box of next-size-up clothes on the top shelf hasn't "
               "been opened in over a season, so nobody knows whether it "
               "still matches the child's actual size by the time the "
               "rod clothes run out.",
    "branches": [
     {"answer": "The stock in that box is ageing out of use unseen, "
                "exactly the way clothes nobody checks on quietly stop "
                "fitting by the time they're needed", "cause": "KC-011"},
     {"answer": "Nobody's actually opened it and checked the sizing "
                "against the child the way the rule calls for",
      "cause": "RC-015"},
     {"answer": "There's no fixed moment, like a seasonal changeover, "
                "that triggers checking the box at all", "cause": "KC-009"},
    ]},
   {"symptom": "The back wall behind the hanging clothes and the top "
               "shelf above it haven't been wiped in longer than anyone "
               "can remember, because reaching either means clearing "
               "the closet first.",
    "branches": [
     {"answer": "Reaching that back wall costs more effort than wiping "
                "the visible parts of the closet combined, so it gets "
                "skipped every time", "cause": "RC-016"},
     {"answer": "Getting to it means unloading the rod and the shelf "
                "first, which is more steps than a normal tidy-up ever "
                "involves", "cause": "KC-004"},
     {"answer": "Nobody's specifically the one who checks behind stored "
                "boxes for damp on a wall shared with the outside",
      "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Stand the shortest person who dresses from this closet at "
             "the rod right now and check whether they can reach a "
             "hanger unaided. If they can't, lower the rod one bracket "
             "notch immediately. While you're in there, pull down the "
             "next-size box and check its labeled size against how the "
             "child actually measures today.",
   "victory": "The rod sits at a height the child reaches without a "
              "stool, and the next-size box on the shelf is labeled "
              "with a size that still matches where the child actually "
              "is.",
  },
 },
 "Dresser Drawers": {
  "frictions": [
   {"symptom": "A drawer needs a hard yank to open because it's "
               "overstuffed, and it comes free suddenly enough to pull "
               "the child backwards off balance.",
    "branches": [
     {"answer": "A jammed drawer that gives suddenly when it finally "
                "opens is a fall risk that outranks how full the drawer "
                "looks", "cause": "KC-010"},
     {"answer": "Eleven shirts in a drawer sized for the wash rhythm is "
                "more than that drawer's own job needs", "cause": "KC-001"},
     {"answer": "Nobody's actually counted the days between washes and "
                "set a real quantity the way the arithmetic test calls "
                "for", "cause": "RC-015"},
    ]},
   {"symptom": "The chest of drawers has no anti-tip strap fitted, and a "
               "tablet sits on top where a child is tempted to climb for "
               "it using the open drawers as steps.",
    "branches": [
     {"answer": "An unanchored chest of drawers with something worth "
                "climbing for on top is a safety constraint independent "
                "of how full the drawers are", "cause": "KC-010"},
     {"answer": "There's no agreed rule yet that the dresser top stays "
                "bare of anything a child would want to climb for",
      "cause": "KC-008"},
     {"answer": "Fitting the anti-tip strap has been on the list for so "
                "long that the unstrapped dresser stopped reading as "
                "urgent", "cause": "RC-017"},
    ]},
   {"symptom": "A drawer that used to close with one push now needs a "
               "press, and the socks inside are lying flat instead of "
               "standing upright, because the last laundry load went in "
               "stacked on top rather than filed in.",
    "branches": [
     {"answer": "Refolding isn't actually happening straight out of the "
                "laundry basket the way the sustain rule calls for",
      "cause": "KC-009"},
     {"answer": "Whoever put this load away isn't necessarily the "
                "person who owns this drawer, so the standard slips "
                "without anyone noticing it was theirs to keep",
      "cause": "RC-013"},
     {"answer": "Two different people run this drawer two different "
                "ways, one filing upright and one stacking flat",
      "cause": "KC-012"},
    ]},
  ],
  "first_15": {
   "action": "Open every drawer right now and push on it once without "
             "leaning. Any drawer that needs a press to close gets "
             "emptied onto the bed immediately, and anything with dead "
             "elastic, no pair, or a hem that now stops above the ankle "
             "comes out for good. Refile what's left standing upright "
             "before you move to the next drawer.",
   "victory": "Every drawer closes with a single push, socks and "
              "underwear stand upright rather than lying flat, and "
              "nothing with a broken pair, dead elastic or the wrong "
              "size is back in a drawer.",
  },
 },
 "School and Activity Launch Zone": {
  "frictions": [
   {"symptom": "The backpack sits unzipped and half in the doorway most "
               "mornings instead of hanging packed on its hook, so it "
               "becomes the thing everyone's foot finds at seven "
               "o'clock.",
    "branches": [
     {"answer": "A bag left on the floor in the doorway everyone walks "
                "at seven in the morning is a fall risk independent of "
                "whose turn it was to hang it up", "cause": "KC-010"},
     {"answer": "Packing isn't actually anchored to the bath running "
                "the way the sustain rule calls for, so it happens "
                "whenever, if at all", "cause": "KC-009"},
     {"answer": "It's genuinely unclear some nights whether the child or "
                "an adult is the one who packs and hangs the bag",
      "cause": "RC-013"},
    ]},
   {"symptom": "A signed form goes missing on a Wednesday because it "
               "never made it into the backpack's front pocket, and by "
               "Thursday nobody can say where it went.",
    "branches": [
     {"answer": "A form has no single defined destination beyond "
                "somewhere in the bag, so it lands wherever the hand "
                "let go of it", "cause": "KC-002"},
     {"answer": "The five line checklist by the hook has no line for "
                "forms specifically, only bag, shoes, lunch and kit",
      "cause": "KC-008"},
     {"answer": "Forms going missing has happened often enough that "
                "nobody flags it as a real gap in the checklist "
                "anymore", "cause": "RC-017"},
    ]},
   {"symptom": "An inhaler ends up loose in a side pocket instead of the "
               "one named pocket it's supposed to live in, hard to find "
               "fast at the school gate and easy for a younger sibling "
               "to reach.",
    "branches": [
     {"answer": "Medication loose in a side pocket a younger sibling can "
                "reach is a safety constraint that outranks which pocket "
                "was quickest at packing time", "cause": "KC-010"},
     {"answer": "Whoever packed the bag that morning didn't specifically "
                "check the named pocket, so it drifted to wherever was "
                "quickest", "cause": "RC-013"},
     {"answer": "Different people pack this bag on different days, and "
                "each one has their own idea of where the medication "
                "actually goes", "cause": "KC-012"},
    ]},
  ],
  "first_15": {
   "action": "Check the hook right now: if the backpack isn't hanging "
             "there zipped, empty it onto the floor, sort tomorrow's "
             "real needs back in, and hang it up. Confirm any inhaler, "
             "epipen or daily medication is in its one named pocket, "
             "and set the shoes directly underneath the hook before you "
             "finish.",
   "victory": "The backpack hangs zipped on its hook with shoes "
              "underneath, any medication sits in its one named pocket, "
              "and the floor by the door is completely clear.",
  },
 },
}


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine. Three per
# zone, matching that data exactly, in this file's own ZONE_ORDER.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Toy Storage Zone", "KBF-001",
  "SMALL PARTS SIT IN A BIN A CRAWLING SIBLING CAN REACH",
  "small toy figures and a loose button battery lying in an open bin at "
  "floor height, a crawling baby's hand reaching toward it"),
 ("Toy Storage Zone", "KBF-002",
  "A BIG BLOCK SET GETS TIPPED OUT AND WALKED AWAY FROM",
  "a large block set tipped across the carpet and abandoned, untouched "
  "since it was poured out"),
 ("Toy Storage Zone", "KBF-003",
  "A BIN'S PHOTO LABEL NO LONGER MATCHES WHAT'S INSIDE",
  "a toy bin's photo label showing blocks while figures and a stray "
  "puzzle piece sit inside instead"),

 ("Bed and Sleep Zone", "KBF-004",
  "A CORD DANGLES AT TODDLER NECK HEIGHT BY THE BED",
  "a blind or curtain cord hanging in a loop near a child's bed head, "
  "dangling low enough to reach a toddler's neck"),
 ("Bed and Sleep Zone", "KBF-005",
  "STUFFED ANIMALS HAVE SPREAD OFF THE BASKET ONTO THE FLOOR",
  "stuffed animals spilling off an open basket and across the floor by a "
  "child's bedroom door, far more than a handful"),
 ("Bed and Sleep Zone", "KBF-006",
  "THE BED NO LONGER MATCHES ITS OWN PHOTO STANDARD",
  "an unmade child's bed with a twisted duvet, a taped photo of a neatly "
  "made bed visible on the inside of a nearby wardrobe door"),

 ("Study Desk", "KBF-007",
  "SCHOOLWORK PILES UP WITH NOWHERE SPECIFIC TO GO",
  "worksheets and finished exercise books piled on a child's desk "
  "surface instead of sorted to a tray, a memory box or recycling"),
 ("Study Desk", "KBF-008", "A CHAIN OF EXTENSION STRIPS FEEDS THE DESK",
  "a lamp, a laptop charger and a second extension strip all chained "
  "into one overloaded power strip under a child's desk"),
 ("Study Desk", "KBF-009",
  "TOYS KEEP MIGRATING FROM THE FLOOR ONTO THE DESK",
  "craft supplies and small toys crowding a child's desk surface, "
  "pushed up against the pen cup and the work tray"),

 ("Clothing Closet", "KBF-010",
  "THE ROD SITS TOO HIGH FOR THE CHILD TO REACH ALONE",
  "a small child standing on a step stool reaching unsuccessfully for a "
  "hanger on a closet rod mounted at adult height"),
 ("Clothing Closet", "KBF-011",
  "THE NEXT SIZE BOX HASN'T BEEN OPENED IN A SEASON",
  "a labelled next size clothing box sitting unopened and dusty on a "
  "closet's top shelf"),
 ("Clothing Closet", "KBF-012",
  "THE BACK WALL AND TOP SHELF HAVEN'T BEEN WIPED IN A YEAR",
  "a dusty closet back wall and top shelf visible only once the hanging "
  "clothes and boxes have been cleared away"),

 ("Dresser Drawers", "KBF-013",
  "A JAMMED DRAWER GIVES SUDDENLY AND PULLS A CHILD OFF BALANCE",
  "a child yanking hard on an overstuffed dresser drawer that has just "
  "given way suddenly"),
 ("Dresser Drawers", "KBF-014",
  "AN UNSTRAPPED DRESSER INVITES CLIMBING FOR WHAT'S ON TOP",
  "a chest of drawers with open drawers used as steps, a tablet sitting "
  "on top out of a child's reach, no anti-tip strap visible"),
 ("Dresser Drawers", "KBF-015",
  "A DRAWER NEEDS A PRESS AND THE SOCKS ARE LYING FLAT",
  "a dresser drawer being pressed shut with effort, socks lying flat "
  "instead of standing upright inside"),

 ("School and Activity Launch Zone", "KBF-016",
  "THE BACKPACK SITS UNZIPPED IN THE DOORWAY AT SEVEN A.M.",
  "an unzipped backpack lying half in a bedroom doorway instead of "
  "hanging packed on its hook"),
 ("School and Activity Launch Zone", "KBF-017",
  "A SIGNED FORM GOES MISSING BY WEDNESDAY",
  "a signed permission form loose on a bedroom floor instead of tucked "
  "into a backpack's front pocket"),
 ("School and Activity Launch Zone", "KBF-018",
  "MEDICATION ENDS UP LOOSE IN THE WRONG POCKET",
  "an inhaler sitting loose in a backpack's side pocket instead of its "
  "own named pocket, a younger sibling's hand nearby"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, kids-bedroom-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a floor covered in more stuffed animals than fit in two arms, "
           "spilling well past a half-full basket at the foot of a "
           "child's bed",
 "KC-002": "a worksheet lying loose on a child's desk with no tray, "
           "memory box or recycling bin anywhere in reach",
 "KC-003": "a small toy sitting abandoned on a child's desk surface "
           "instead of in the toy bin it actually belongs in",
 "KC-004": "a hand reaching behind a fully loaded closet rod and a "
           "stacked top shelf to wipe a section of wall nobody can get "
           "to quickly",
 "KC-005": "a toy bin's photo label showing blocks while a hand lifts a "
           "mismatched puzzle piece out from inside",
 "KC-006": "a small child standing on tiptoe, unable to reach a hanger "
           "on a closet rod mounted at adult shoulder height",
 "KC-007": "a single toy bin overflowing with one oversized collection, "
           "the lid unable to close over it",
 "KC-008": "two different picture labels on two dresser drawers, one "
           "crisp and one clearly guessed at, with no shared pattern "
           "between them",
 "KC-009": "an unzipped backpack sitting on a bedroom floor while a bath "
           "runs unseen down the hall",
 "KC-010": "a curtain cord hanging in a loop at exactly a toddler's neck "
           "height beside a child's bed",
 "KC-011": "a labelled next size clothing box sitting sealed and "
           "forgotten on a closet's top shelf",
 "KC-012": "two different folding styles visible in one open dresser "
           "drawer, some clothes standing upright and some lying flat",
 "RC-013": "an inhaler sitting loose in the wrong backpack pocket, "
           "nobody having checked the one it belongs in",
 "RC-014": "a single oversized stuffed animal kept on a shelf long after "
           "the rest of its kind moved to the rotation box",
 "RC-015": "a stack of finished exercise books sitting on a desk "
           "corner, neither filed away nor recycled",
 "RC-016": "a hand reaching into the dim back corner of an emptied "
           "closet, well behind where the hanging clothes usually sit",
 "RC-017": "a dusty rotation box sitting on a wardrobe's top shelf for "
           "so long its label has gone unread",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Toy Storage Zone": [
  "Wipe each bin's outer face and its taped photo label with a damp "
  "cloth, going gently so the picture doesn't peel.",
  "Vacuum tight into the skirting corners and carpet edges where small "
  "parts and dust migrate out of sight.",
  "Wash the hard plastic blocks and figures in warm soapy water and "
  "spread them on a towel to dry fully.",
 ],
 "Bed and Sleep Zone": [
  "Vacuum the strip of floor under the bed frame with the crevice tool, "
  "working right into the corner where it meets the wall.",
  "Wipe the nightlight casing and shade with a dry cloth, then a barely "
  "damp one, so it throws its full brightness again.",
  "Brush the stuffed animals' fur with a soft clothing brush before any "
  "of them go back onto the bed or into the basket.",
 ],
 "Study Desk": [
  "Dust the shelf above the desk and run the cloth along the top edges "
  "of the standing books, left to right.",
  "Vacuum the pencil-sharpener shavings and dried glue out of the "
  "drawer corners, then wipe both runners clean.",
  "Wipe the laptop screen dry only, in slow straight passes, keeping "
  "every spray and damp cloth away from the glass.",
 ],
 "Clothing Closet": [
  "Wipe the full length of the hanging rod with a damp cloth to lift the "
  "grey line the sliding hangers leave.",
  "Draw a lint brush over the shoulders of each hanging garment where "
  "dust settles, working straight along the rod.",
  "Run the detail brush along the sliding or bifold door track to clear "
  "the grit that stops it running smoothly.",
 ],
 "Dresser Drawers": [
  "Pull each drawer fully out, tip the lint into the bin, vacuum the "
  "corners, and wipe the base before refilling.",
  "Vacuum each runner, then work the detail brush along it to clear the "
  "grit that jams the glide.",
  "Wipe the dresser's exposed sides, then vacuum the gap behind and "
  "under it with the crevice tool while it's pulled out.",
 ],
 "School and Activity Launch Zone": [
  "Turn the backpack over a bin and shake out crumbs and paper, then "
  "wipe its base where a drink once leaked.",
  "Scrub the water bottle's lid threads and drinking valve with a "
  "detail brush, since that's where mould grows unseen.",
  "Vacuum the patch of floor under the hooks, then damp mop it if it's a "
  "hard floor, so the morning lane starts clean.",
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
 {"id": "KBA-001", "zone": "Toy Storage Zone",
  "title": "CLEAR CHOKE-SIZED PARTS AND WIPE THE LABEL",
  "minutes": 15, "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Move every choke-sized piece and loose battery up out of a "
          "crawling sibling's reach, and get one bin's label readable "
          "again.",
  "why": "A choke-sized piece at floor height and a label nobody can "
         "trust both cost this zone the one job it has, letting a young "
         "child put things away without asking.",
  "inputs": ["a high bin or shelf out of a crawling sibling's reach"],
  "steps": [
   "Tip out the bin nearest the door and check every piece against the "
   "toilet-roll-tube test: anything small enough to fit through goes up "
   "into a bin on the wardrobe top shelf, out of a younger sibling's "
   "reach, right now. Wipe that bin's photo label clean enough to read, "
   "and clear a lie-down-sized patch of carpet before you stop."],
  "causes": ["KC-010", "RC-017", "KC-008"],
  "victory": "No choke-sized piece or loose battery sits in a bin at "
             "floor height, the wiped label is readable and matches "
             "what's actually inside, and there's enough clear carpet "
             "to lie down on.",
  "next": "KBS-001",
  "art": "a hand lifting small figures and a loose battery out of a low "
         "bin into a high one, another hand wiping a toy bin's photo "
         "label clean"},

 {"id": "KBA-002", "zone": "Toy Storage Zone",
  "title": "RUN THE ROTATION TRIAL AND FIX THE BIN LABELS",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Move half of any tipped-and-abandoned set to the dated "
          "rotation box for a genuine trial, and reconcile every bin's "
          "photo label against what's actually inside it.",
  "why": "A set that never gets touched again after a real trial has "
         "earned its answer, and a bin whose label no longer matches "
         "its contents stops working as a system a young child can run "
         "alone.",
  "inputs": ["a marker or a fresh label", "the dated rotation box"],
  "steps": [
   "Move half of any tipped-and-abandoned set into the dated rotation "
   "box today, for six weeks, no more.",
   "Open every bin, sort what's actually inside back into its own "
   "family, and reprint or retape any label that no longer matches.",
   "Agree out loud who's allowed to just tip toys in without sorting, "
   "and fix whatever's causing the mismatch."],
  "causes": ["RC-015", "RC-014", "KC-007", "KC-012", "KC-005"],
  "victory": "Half of any abandoned set sits in the dated rotation box, "
             "and every bin's photo label matches what's actually "
             "inside it.",
  "next": "KBA-001",
  "art": "a hand carrying half a block set into a dated rotation box, a "
         "bin's photo label being retaped to match what's sorted inside "
         "it"},

 {"id": "KBA-003", "zone": "Bed and Sleep Zone",
  "title": "CLEAR THE CORDS AND COUNT THE ANIMALS",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Cleat every blind or curtain cord near the bed head out of "
          "reach, then pull every stuffed animal out to count what's "
          "actually sleeping in the bed.",
  "why": "A dangling cord at toddler neck height and a bed buried in "
         "animals both cost this zone the calm, walkable sleep space "
         "it's supposed to be.",
  "inputs": ["a cord cleat or clip if none exists"],
  "steps": [
   "Check every blind or curtain cord near the bed head right now and "
   "cleat any hanging loop up out of a sleeping child's reach. Strip "
   "the duvet and pillow off, count how many stuffed animals were "
   "actually in the bed, and move the rest into the basket at the foot "
   "where they're still visible. Square the pillow and pull the duvet "
   "flat before you finish."],
  "causes": ["KC-010", "KC-008", "RC-017", "RC-014", "KC-001"],
  "victory": "No cord or loop hangs within reach of the pillow, the bed "
             "carries a squared pillow and a flat duvet with only the "
             "animals that fit in two arms on top, and the rest sit "
             "visible in the basket at the foot.",
  "next": "KBS-002",
  "art": "a hand cleating a curtain cord high on the wall beside a bed, "
         "a child counting stuffed animals on a freshly squared duvet"},

 {"id": "KBA-004", "zone": "Bed and Sleep Zone",
  "title": "REMEASURE THE COVERS AND RENEW THE MADE-BED PHOTO",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Test whether the bedding can actually be pulled flat by the "
          "child alone, drop to a single duvet in a washable cover if "
          "not, and retake the made-bed photo for the wardrobe door.",
  "why": "Layers a young child can't manage and a photo that no longer "
         "matches what a single duvet actually looks like both "
         "undermine the one flat pull the whole zone depends on.",
  "inputs": ["a camera or phone", "tape", "a washable duvet cover if "
             "needed"],
  "steps": [
   "Time how long it takes the child to remake the bed alone. If it "
   "needs help or takes more than a minute, drop to one duvet in a "
   "washable cover.",
   "Tie remaking the bed to the school bag going onto the shoulder, out "
   "loud, so it's not left to whenever.",
   "Take a fresh photo of the properly made bed and tape it inside the "
   "wardrobe door at the child's eye height."],
  "causes": ["RC-013", "KC-009", "KC-004", "RC-015"],
  "victory": "The child remakes the bed alone in about a minute, and a "
             "current photo of that made bed is taped inside the "
             "wardrobe door.",
  "next": "KBA-003",
  "art": "a child pulling a single duvet flat alone, a fresh photo being "
         "taped inside a wardrobe door at their own eye height"},

 {"id": "KBA-005", "zone": "Study Desk",
  "title": "CLEAR THE DESK AND GIVE EVERY SHEET A VERDICT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the desk to bare wood and sort every loose sheet of "
          "paper into live work, keepsake or recycling.",
  "why": "A sheet with nowhere specific to go is why the pile keeps "
         "growing, and it grows on a surface that's supposed to hold "
         "only what's live.",
  "inputs": ["the live-work tray", "the memory box", "a recycling bin"],
  "steps": [
   "Clear the desk down to bare wood right now. Sort every loose sheet "
   "of paper into exactly one of three piles, live work into the tray, "
   "keepsake into the memory box, everything else into recycling, and "
   "count the plugs under the desk, bringing any chain of strips back "
   "to one strip in one wall socket."],
  "causes": ["KC-002", "RC-014", "RC-015"],
  "victory": "The desk holds only the lamp, the pen cup and one tray of "
             "live work, every other sheet of paper has a verdict, and "
             "exactly one power strip runs from exactly one wall "
             "socket.",
  "next": "KBS-003",
  "art": "a hand sorting loose school papers into a tray, a memory box "
         "and a recycling bin beside a desk cleared to bare wood"},

 {"id": "KBA-006", "zone": "Study Desk",
  "title": "UNCHAIN THE PLUGS AND SEND STRAY TOYS HOME",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Bring every plug under the desk back to one strip in one "
          "wall socket, and carry every stray toy and craft item back "
          "to the zone it actually belongs in.",
  "why": "A chained power strip is a fire and trip risk waiting for a "
         "cold morning, and a desk half covered in toys stops being a "
         "surface anyone can actually work at.",
  "inputs": ["one extension strip", "a box for stray items"],
  "steps": [
   "Unplug the chain of strips under the desk and replug down to one "
   "strip in one wall socket.",
   "Carry every stray toy, craft item and game piece on the desk back "
   "to the zone it actually belongs in.",
   "Pick a fixed moment, like homework starting, when the desk gets "
   "checked for drift before it's allowed to pile up again."],
  "causes": ["KC-010", "RC-013", "RC-017", "KC-003", "KC-009"],
  "victory": "Exactly one power strip runs from exactly one wall socket "
             "under the desk, and no stray toy or craft item remains on "
             "the desk surface.",
  "next": "KBA-005",
  "art": "a hand unplugging a chain of power strips down to one under a "
         "desk, a stray toy being carried back to its own bin"},

 {"id": "KBA-007", "zone": "Clothing Closet",
  "title": "LOWER THE ROD AND CHECK THE NEXT SIZE BOX",
  "minutes": 15, "players": "1", "six_s": "Straighten", "from_first_15": True,
  "goal": "Lower the rod to the child's own reach if it isn't already "
          "there, and check the next-size box's label against how the "
          "child measures today.",
  "why": "A rod the child can't reach and a next-size box nobody's "
         "checked both cost this closet the one job it has, dressing "
         "the child who actually uses it.",
  "inputs": ["a spare bracket or hook if the rod needs lowering"],
  "steps": [
   "Stand the shortest person who dresses from this closet at the rod "
   "right now and check whether they can reach a hanger unaided. If "
   "they can't, lower the rod one bracket notch immediately. While "
   "you're in there, pull down the next-size box and check its "
   "labeled size against how the child actually measures today."],
  "causes": ["KC-006", "RC-017", "KC-008", "KC-011", "RC-015", "KC-009"],
  "victory": "The rod sits at a height the child reaches without a "
             "stool, and the next-size box on the shelf is labeled with "
             "a size that still matches where the child actually is.",
  "next": "KBS-004",
  "art": "a child reaching a hanger unaided from a newly lowered rod, a "
         "next-size box being checked against them beside the closet"},

 {"id": "KBA-008", "zone": "Clothing Closet",
  "title": "CLEAR THE BACK WALL AND CHECK FOR DAMP",
  "minutes": 30, "players": "1", "six_s": "Shine",
  "goal": "Empty the closet completely, wipe the back wall and top "
          "shelf that never get touched, and flag any damp before it "
          "becomes mould.",
  "why": "The one wall you can only see when the closet's empty is "
         "exactly where damp and mould get a head start, and reaching "
         "it at all takes clearing everything else out of the way "
         "first.",
  "inputs": ["a cloth", "a torch", "a calendar reminder"],
  "steps": [
   "Empty the closet floor, rod and top shelf completely onto the "
   "bed.",
   "Wipe the back wall and the top shelf, checking closely on any wall "
   "shared with the outside of the house.",
   "Agree whose job the yearly empty-and-check actually is, and put a "
   "date on the calendar for it."],
  "causes": ["RC-016", "KC-004", "RC-013"],
  "victory": "The back wall and top shelf are wiped clean with no damp "
             "or mould found, or any found is flagged, and a calendar "
             "date is set for the next check.",
  "next": "KBA-007",
  "art": "a closet emptied completely, a hand wiping the bare back wall "
         "with a torch checking the corner behind where boxes sat"},

 {"id": "KBA-009", "zone": "Dresser Drawers",
  "title": "EMPTY THE JAMMED DRAWER AND CUT THE COUNT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Push every drawer once and empty any that need a press, "
          "cutting the count down to what the wash rhythm actually "
          "needs.",
  "why": "A jammed drawer that gives suddenly is a fall risk, and it's "
         "jammed because it's carrying more than the wash rhythm needs "
         "between loads.",
  "inputs": ["none beyond the drawers themselves"],
  "steps": [
   "Open every drawer right now and push on it once without leaning. "
   "Any drawer that needs a press to close gets emptied onto the bed "
   "immediately, and anything with dead elastic, no pair, or a hem "
   "that now stops above the ankle comes out for good. Refile what's "
   "left standing upright before you move to the next drawer."],
  "causes": ["KC-010", "KC-001", "RC-015"],
  "victory": "Every drawer closes with a single push, socks and "
             "underwear stand upright rather than lying flat, and "
             "nothing with a broken pair, dead elastic or the wrong "
             "size is back in a drawer.",
  "next": "KBS-005",
  "art": "a hand pushing a dresser drawer shut with a single push, "
         "clothes standing upright and filed inside"},

 {"id": "KBA-010", "zone": "Dresser Drawers",
  "title": "STRAP THE DRESSER AND REFILE THE LOAD",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Fit an anti-tip strap to a wall stud, clear the dresser top "
          "of anything worth climbing for, and refile the last laundry "
          "load standing upright.",
  "why": "An unanchored dresser with something worth climbing for on "
         "top is a tip-over risk regardless of how full any drawer is, "
         "and clothes stacked flat instead of filed upright are what "
         "make a drawer stop closing.",
  "inputs": ["an anti-tip strap and wall anchor kit"],
  "steps": [
   "Fit an anti-tip strap from the dresser to a wall stud, and clear "
   "the top of anything a child would climb for.",
   "Pull out the most recent laundry load and refile it standing "
   "upright rather than stacked flat.",
   "Agree which two drawers the child owns outright, and let them run "
   "those two their own way."],
  "causes": ["KC-008", "RC-017", "KC-009", "RC-013", "KC-012"],
  "victory": "The dresser is strapped to a wall stud with a bare top, "
             "and the last laundry load is refiled standing upright in "
             "its own drawer.",
  "next": "KBA-009",
  "art": "a hand fitting an anti-tip strap from a dresser to a wall "
         "stud, a bare dresser top beside it"},

 {"id": "KBA-011", "zone": "School and Activity Launch Zone",
  "title": "HANG THE BAG AND CHECK THE NAMED POCKET",
  "minutes": 15, "players": "1", "six_s": "Sustain", "from_first_15": True,
  "goal": "Get the backpack packed, zipped and hung on its hook, with "
          "any medication confirmed in its one named pocket.",
  "why": "A bag left on the floor is the trip everyone's foot finds at "
         "seven, and medication that isn't where it's supposed to be "
         "is the emergency that arrives without warning.",
  "inputs": ["none beyond the hook and the bag itself"],
  "steps": [
   "Check the hook right now: if the backpack isn't hanging there "
   "zipped, empty it onto the floor, sort tomorrow's real needs back "
   "in, and hang it up. Confirm any inhaler, epipen or daily "
   "medication is in its one named pocket, and set the shoes directly "
   "underneath the hook before you finish."],
  "causes": ["KC-010", "KC-009", "RC-013"],
  "victory": "The backpack hangs zipped on its hook with shoes "
             "underneath, any medication sits in its one named pocket, "
             "and the floor by the door is completely clear.",
  "next": "KBS-006",
  "art": "a packed backpack being hung zipped on its hook, a hand "
         "checking a named pocket for an inhaler, shoes set underneath"},

 {"id": "KBA-012", "zone": "School and Activity Launch Zone",
  "title": "GIVE EVERY FORM A HOME AND ADD A LINE TO THE LIST",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "Give every form a fixed destination in the front pocket, add "
          "a form line to the five line checklist, and confirm who's "
          "checking the named medication pocket each time the bag is "
          "packed.",
  "why": "A form with nowhere specific to go and a checklist with no "
         "line for it both guarantee the same paper goes missing "
         "again, and medication that drifts between packers is a risk "
         "that shouldn't depend on which day it is.",
  "inputs": ["a marker", "the checklist taped beside the hook"],
  "steps": [
   "Agree that every form's one destination is the backpack's front "
   "pocket, checked the moment it's signed.",
   "Add a fifth line, forms, to the checklist taped beside the hook.",
   "Whoever packs the bag that day checks the one named medication "
   "pocket specifically, out loud, before the bag is zipped."],
  "causes": ["KC-002", "KC-008", "RC-017", "RC-013", "KC-012"],
  "victory": "Every signed form goes straight into the front pocket, the "
             "checklist carries a fifth line for forms, and the named "
             "medication pocket is checked out loud every time the bag "
             "is packed.",
  "next": "KBA-011",
  "art": "a hand adding a fifth line for forms to a checklist taped "
         "beside a hook, a signed form being tucked into a backpack's "
         "front pocket"},

 {"id": "KBA-013", "zone": None,
  "title": "THE FULL KIDS BEDROOM HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk all six zones checking cords near the bed, choke-sized "
          "parts and treatments, the closet rod and rack anchoring, "
          "the dresser's anti-tip strap, and the launch zone's "
          "medication pocket.",
  "why": "This room combines a sleeping child, a crawling sibling, a "
         "jammed dresser drawer and daily medication, so the hazards "
         "only get found if every zone is checked on the same walk.",
  "inputs": ["an anti-tip strap kit if none is fitted", "a cord cleat"],
  "steps": [
   "Check every cord and drawstring near the bed head for anything "
   "hanging low enough to reach a toddler's neck.",
   "Check the toy bins for small parts or loose batteries sitting at a "
   "younger sibling's reach.",
   "Push on the closet rod and confirm it holds without give, and "
   "clear the closet floor of anything to climb on to reach the top "
   "shelf.",
   "Confirm the dresser's anti-tip strap is fitted to a wall stud and "
   "the top is bare of anything worth climbing for.",
   "Confirm the named medication pocket in the backpack actually holds "
   "what it's supposed to, checked today."],
  "causes": ["KC-010", "RC-013", "RC-017"],
  "victory": "No cord hangs at toddler height, no choke-sized part sits "
             "at a crawling sibling's reach, the rod and rack hold "
             "without give, the dresser is strapped with a bare top, "
             "and the named medication pocket holds what it should.",
  "next": "KBA-014",
  "art": "a hand testing a closet rod for give beside a strapped "
         "dresser, a checked medication pocket visible in an open "
         "backpack nearby"},

 {"id": "KBA-014", "zone": None, "title": "THE EVENING ROOM SWEEP",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "The moment bath time starts, walk all six zones once in the "
          "order the room actually uses them: bed made, toys binned, "
          "desk cleared, closet checked, drawers pushed shut, bag "
          "packed and hung.",
  "why": "Every zone in this room already has its own trigger; the "
         "sweep is what actually fires all six on the same evening "
         "instead of one drifting behind the rest.",
  "inputs": ["none beyond the room's own bins, hooks and drawers"],
  "steps": [
   "Square the pillow and pull the duvet flat.",
   "Clear the floor of toys back into their own bins.",
   "Clear the desk to the lamp, pen cup and tray.",
   "Push every drawer shut with one push, refiling anything that "
   "needed a press.",
   "Pack and hang the backpack on its hook."],
  "causes": ["KC-009", "RC-013"],
  "victory": "All six zones pass their own leave-behind standard on the "
             "same evening, in one walk.",
  "next": "KBA-015",
  "art": "a hand completing the last step of an evening sweep, hanging "
         "a packed backpack beside a made bed and cleared desk"},

 {"id": "KBA-015", "zone": None, "title": "THE TERM CHANGEOVER DAY",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "On a fixed day each term, check the next size box against "
          "the child's actual measurements, retake the made-bed photo, "
          "and clear anything that failed its own honest test since "
          "the last changeover.",
  "why": "A child outgrows a size and a set of interests faster than a "
         "term turns, so a fixed changeover day is what actually keeps "
         "this room matched to who's using it right now.",
  "inputs": ["a calendar reminder", "a camera or phone"],
  "steps": [
   "Pick a fixed day each term and put it on a shared calendar.",
   "Check the next size box's labelled size against how the child "
   "measures today, and swap in a new size if it's due.",
   "Retake the made-bed photo and clear anything, a coat, a toy set, a "
   "drawer's worth of clothes, that failed its own honest test all "
   "term."],
  "causes": ["KC-006", "KC-011", "RC-015"],
  "victory": "A changeover happens on the same calendar day every term, "
             "the next size box matches how the child measures today, "
             "and nothing that failed its own test all term is still "
             "taking a slot.",
  "next": "KBA-013",
  "art": "a calendar reminder pinned near a bedroom door while a next "
         "size box is checked against a child standing beside it"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a kids bedroom, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("KBE-001", "A RAINY SATURDAY MEANS EVERY BIN GETS EMPTIED AT ONCE",
  "A full rainy Saturday means every bin gets tipped out for a "
  "different game, one after another, until the whole floor is "
  "covered.",
  ["KBZ-001"],
  "By bedtime every family of toys goes back into the bin whose photo "
  "label actually matches it.",
  "If a toy went back into a bin its own photo doesn't show, the label "
  "check never happened. Draw KBA-002.",
  "toy bins tipped out across a bedroom floor mid rainy-day play, each "
  "bin's photo label still visible on its front face"),
 ("KBE-002", "A SLEEPOVER GUEST ARRIVES WITH THEIR OWN STUFFED ANIMAL",
  "A sleepover guest arrives with their own stuffed animal and needs "
  "somewhere on the bed for it tonight, on top of whatever's already "
  "there.",
  ["KBZ-002"],
  "There's room on the bed for one more animal without the basket "
  "already overflowing onto the floor.",
  "If the basket was already spilling onto the floor before the "
  "guest's animal even arrived, the count-and-clear reset never "
  "happened. Draw KBA-003.",
  "two children's stuffed animals sitting together on a neatly made "
  "bed, a basket beside it with room still left inside"),
 ("KBE-003", "A BIG PROJECT DUE TOMORROW TAKES OVER THE WHOLE DESK",
  "A big project due tomorrow needs every inch of the desk at once, "
  "posters, glue, scissors and a laptop all going at the same time.",
  ["KBZ-003"],
  "The desk still has a tray telling you what's live and a chair "
  "nobody has to clear to sit down.",
  "If the chair had to be cleared before anyone could sit, or nobody "
  "could say what was actually due next, the desk-and-plug reset never "
  "happened. Draw KBA-006.",
  "a child's desk crowded with a school project's supplies, a clear "
  "tray of live work and an empty chair still visible among them"),
 ("KBE-004", "A GROWTH SPURT MAKES HALF THE ROD SUDDENLY TOO SMALL",
  "A growth spurt over the summer makes half the clothes on the rod "
  "suddenly too small, all discovered on the same school-uniform "
  "morning.",
  ["KBZ-004"],
  "The next size box on the shelf already holds what actually fits "
  "now, checked and ready to hang.",
  "If the next size box hadn't been opened and checked, the whole "
  "morning turns into a scramble. Draw KBA-007.",
  "a child standing at a closet rod holding up a shirt that no longer "
  "fits, a labelled box open on the shelf above with the next size "
  "visible inside"),
 ("KBE-005", "LAUNDRY DAY BRINGS BACK A FULL BASKET AT ONCE",
  "Laundry day brings back a full basket of clean clothes at once, all "
  "needing to go into the dresser before the basket's needed again.",
  ["KBZ-005"],
  "Every drawer still closes with one push once the whole basket has "
  "gone in.",
  "If a drawer needed a press to close once the load went in, the "
  "refile-upright habit never happened. Draw KBA-010.",
  "a full laundry basket beside an open dresser drawer with socks and "
  "shirts standing upright in neat rows"),
 ("KBE-006", "A PERMISSION SLIP IS DUE BACK THE SAME MORNING IT'S SIGNED",
  "A permission slip comes home, gets signed at the kitchen table, and "
  "is due back the very next morning before the bell.",
  ["KBZ-006"],
  "The signed slip goes straight into the backpack's front pocket the "
  "same night, not left on the counter.",
  "If the slip was still sitting on the counter the next morning, the "
  "assigned-home fix for forms never happened. Draw KBA-012.",
  "a signed permission slip being tucked into a backpack's front "
  "pocket beside forms already filed there, the bag hanging packed on "
  "its hook"),
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
        "related": {"standard": f"KBS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your kids "
                       "bedroom, then turn to that root cause card. If "
                       "two are true, take the one you could change this "
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
    standard_id = (f"KBS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"KBS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
    first_zone_id = ZONES[ZONE_ORDER[0]]["id"]
    return {
        "id": "KBR-001", "title": "THE KIDS BEDROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START ON THE FLOOR.",
        "objective": "A child's bedroom has to work at their height and "
                     "their reading level, not an adult's: toys, clothes, "
                     "sleep, homework and tomorrow's bag all compete for "
                     "the same small room. This card is the map.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"{first_zone_id} {ZONE_ORDER[0]}. {start_tip['text']}"
            if start_tip else
            f"{first_zone_id} {ZONE_ORDER[0]}. Clear the floor first, "
            f"since almost everything else in this room is failing onto "
            f"it."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your kids bedroom. Put the rest back.",
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
        "safety_first": "Do KBA-013 The Full Kids Bedroom Hazard Walk "
                        "before any rebuild. It takes thirty minutes and "
                        "covers cords near the bed, choke-sized parts "
                        "and loose batteries, the closet rod and rack "
                        "anchoring, the dresser's anti-tip strap, and "
                        "the named medication pocket in the backpack.",
        "related": {"contents": "KBZ-001 to KBZ-006, KBF-001 to "
                                 "KBF-018, the shared root causes in "
                                 "ops/root_causes.py, KBA-001 to "
                                 "KBA-015, KBS-001 to KBS-006, KBE-001 "
                                 "to KBE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole kids "
                           "bedroom in its settled state, six open toy "
                           "bins at child height, a made bed with a "
                           "basket of animals at the foot, a cleared "
                           "study desk, a closet with a lowered rod, a "
                           "strapped dresser, and a packed backpack "
                           "hanging by the door, all visible in one "
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
    return {"deck": "kids-bedroom", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "KBA-013" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"

    # This deck's zone list must be exactly the Manual's six, nothing added
    # or renamed, in this file's own play order (see module docstring for
    # why that order differs from the Manual's storage-list order).
    assert [c["zone"] for c in cards if c["type"] == "ZONE CARD"] == \
        ZONE_ORDER, "zone card order does not match this file's own ZONES"
    assert len(ZONES) == 6, (
        "this room has six Manual zones; that count moved")


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        kids-bedroom ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
