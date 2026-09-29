#!/usr/bin/env python3
"""
Build the Family Room deck: 69 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
content/manual/source/content.json, the same corpus the 114 zone pages
already read. build_kitchen_deck.py, build_entryway_deck.py,
build_laundry_room_deck.py, build_home_office_deck.py,
build_primary_bathroom_deck.py, build_garage_deck.py,
build_stair_landing_deck.py, build_pantry_deck.py, build_hall_closet_deck.py,
build_dining_room_deck.py, build_guest_bedroom_deck.py and
build_guest_bathroom_deck.py proved the pattern for the first twelve rooms;
this is the thirteenth. Purpose, done_looks_like, the standard, the trigger,
the first-15 action and its victory condition are quoted from the Manual,
not rewritten, and gate() at the bottom asserts they are still
character-for-character identical. The 18 frictions (three per zone) are
likewise derived straight from the Manual's own diagnosis layer, in zone
order, not retyped, so this deck cannot silently diverge from the
diagnostic engine already shipped on the site's zone pages. That diagnosis
layer was authored directly into content.json as part of this same B9
cycle: Family Room carried the rest of its rich Manual content (purpose,
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
several (DECK-GAME-DESIGN.md 4.3). This room's real frictions happen to
reach all seventeen of the shared vocabulary's causes, confirmed against
content/manual/source/content.json before this file was written by walking
every branch actually authored below, not assumed from any other room's
count or padded toward a round number: six zones each carrying a screen, a
heater, small parts, cables and a hot glue gun within a child's reach gives
this particular room's real problems unusual reach across the vocabulary.

WHAT THE BUDGET IS AND WHY
---------------------------
Family Room ships as a free typeset page, the same stage every prior room
in this line shipped at before any print-on-demand decision existed
(DECK-GAME-DESIGN.md 4.1 is Kitchen's fixed-72 print-tier constraint, and
it does not apply here; D-027 already settled that trimming or filling a
room's honest count to chase a print tier is the wrong move). This room
has six real Manual zones, not seven, so its budget is sized the same way
Home Office's and Laundry Room's own six-zone decks were: six ZONE cards,
eighteen FRICTION cards (three per zone), seventeen reachable ROOT CAUSE
cards, fifteen ACTION cards (two per zone plus three whole-room), six
STANDARD cards and six EVENT cards. 69 cards in total, not padded or
trimmed to match ops/cardtext/derive_room_deck.py's own generic BUDGET
dict, which reports a fixed 72/7-zone template for every room regardless
of its real zone count (confirmed live: Home Office ships 66 cards with a
ZONE CARD budget of 6, and Laundry Room ships 67 with a ZONE CARD budget
of 6, neither matching that generic template either) rather than the
zone count content.json actually carries for this room.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Family Room deck to disclose against: no free Family Room product exists
on the site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_family_room_deck.py
Out:  ops/cardtext/family-room-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "family-room-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Family Room"

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
 "Primary Media Zone": {
  "id": "FRZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE CONSOLE PER SHELF. CONTROLLERS DOCKED. NOTHING ON THE "
             "VENTS.",
  "callouts": [
   "One console standing alone on its own shelf with its controllers "
   "docked beside it",
   "Disc cases standing spine out in a single row",
   "Every visible cable wearing a label at both ends",
   "The power strip sitting off the carpet, clear of the walking path",
   "A completely clear vent slot on the top of the console",
   "The television standing solid when nudged, with no forward rock",
  ],
  "art": ("a media cabinet holding one console alone on its own shelf "
          "with its controllers docked beside it, disc cases standing "
          "spine out in a single row, labeled cables running behind the "
          "unit, the power strip lifted off the carpet, and a "
          "completely clear vent slot on the console's top"),
 },
 "Toy and Play Zone": {
  "id": "FRZ-002", "order": 2, "difficulty": 2,
  "tagline": "FIVE OR SIX OPEN BINS. PICTURE LABELS. THE OVERFLOW LIVES "
             "IN THE CLOSET.",
  "callouts": [
   "Five or six open bins with no lids sitting on the lowest shelf",
   "A photo of each bin's contents taped to its front face at a child's "
   "eye level",
   "The play mat rolled and standing against the wall",
   "A clear stretch of floor wide enough for two children to build "
   "without moving anything first",
   "Nothing stacked above shoulder height on the shelf",
   "No cracked plastic or loose small part visible in any open bin",
  ],
  "art": ("a low shelf holding five or six open lidless bins each with "
          "a photo label taped to its front face, a rolled play mat "
          "standing against the wall, and a wide clear stretch of "
          "floor in front of it"),
 },
 "Board Game and Puzzle Zone": {
  "id": "FRZ-003", "order": 3, "difficulty": 3,
  "tagline": "STACKS NO MORE THAN FIVE HIGH. A NAME ON EVERY SHORT EDGE.",
  "callouts": [
   "Boxes lying flat in stacks no more than five high",
   "A tape strip naming the game readable on the short edge from the "
   "doorway",
   "No stack sitting high enough to require moving five boxes to reach "
   "the bottom one",
   "A loose piece bagged and visible inside its own box lid",
   "No box wearing an undated or old sticky note",
   "A clear shelf face with no dice or pawns scattered on the floor "
   "beneath it",
  ],
  "art": ("a bookshelf holding board game boxes lying flat in stacks no "
          "more than five high, each with a tape strip naming the game "
          "readable on the short edge, no loose dice visible on the "
          "floor beneath it"),
 },
 "Blanket and Comfort Zone": {
  "id": "FRZ-004", "order": 4, "difficulty": 1,
  "tagline": "ONE BASKET. FOUR THROWS FOLDED THE SAME WAY. NOTHING ON THE "
             "RADIATOR.",
  "callouts": [
   "One basket holding throws folded to the same rectangle so the fold "
   "edges line up",
   "Two floor cushions stacked beside the basket",
   "A completely bare radiator, heater, and lamp shade nearby",
   "Nothing draped over the sofa back or the arm of a chair",
   "No throw lying on the floor beside the sofa",
   "A basket standing clear of the walking path between the sofa and "
   "the door",
  ],
  "art": ("a basket beside a sofa holding several matching throws "
          "folded to the same rectangle with two floor cushions "
          "stacked next to it, a bare radiator visible in the "
          "background with nothing draped over it"),
 },
 "Charging and Device Zone": {
  "id": "FRZ-005", "order": 5, "difficulty": 2,
  "tagline": "ONE STRIP. NAMED SLOTS. NO CHARGER ANYWHERE ELSE IN THE "
             "ROOM.",
  "callouts": [
   "One power strip standing on a hard surface",
   "Four or five labeled cables each ending at a named slot",
   "The empty slots visible and readable in daylight",
   "No cable hanging low enough to loop at a toddler's neck height",
   "No drink or glass anywhere on the same surface as the strip",
   "No charger plugged in at any other socket in the room",
  ],
  "art": ("a power strip standing on a hard side table with four or "
          "five labeled cables running to named slots, the empty slots "
          "visible, no drink glass on the same surface and no cable "
          "hanging in a low loop"),
 },
 "Craft and Activity Zone": {
  "id": "FRZ-006", "order": 6, "difficulty": 3,
  "tagline": "FOUR LIDDED BINS. ONE PROJECT OUT. SCISSORS POINT DOWN.",
  "callouts": [
   "Four lidded bins labeled by what they make standing on the shelf",
   "Exactly one project bin out on an otherwise completely clear work "
   "surface",
   "Scissors standing point down in a cup",
   "The glue gun sitting unplugged on its own heat-safe tile",
   "Beads, solvents, and craft knives standing on a shelf above the "
   "youngest child's reach",
   "No loose small part visible on the floor beneath the table",
  ],
  "art": ("a craft table holding four lidded labeled bins on a shelf "
          "behind it, one project bin out on an otherwise clear work "
          "surface, scissors standing point down in a cup, and an "
          "unplugged glue gun resting on its own tile"),
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
 "Primary Media Zone": {
  "frictions": [
   {"symptom": "A previous-generation console has sat unplugged behind "
               "the newer one for two years because someone's save file "
               "lives on it.",
    "branches": [
     {"answer": "It's a genuine attachment to what's on that save "
                "file, not to the box itself", "cause": "RC-014"},
     {"answer": "Moving the save data or letting the console go is a "
                "decision nobody has actually made, so it just keeps "
                "the shelf", "cause": "RC-015"},
     {"answer": "Two consoles is more than the shelf's one-console-"
                "per-job plan needs once you're honest about which one "
                "gets used", "cause": "KC-001"},
    ]},
   {"symptom": "Dust has caked thick in the vent slots on the back of a "
               "console, exactly the buildup that cooks the board, "
               "because reaching it means pulling the whole unit out "
               "from the wall first.",
    "branches": [
     {"answer": "The vents cost more effort to reach than the rest of "
                "the shelf combined, so they get skipped",
      "cause": "RC-016"},
     {"answer": "A blanket or a stack of disc cases sits on top "
                "blocking the vents, trapping that heat against the "
                "board", "cause": "KC-010"},
     {"answer": "It's been running warm in the same spot for so long "
                "that nobody thinks to check the vents at all anymore",
      "cause": "RC-017"},
    ]},
   {"symptom": "The dock has an empty cradle, and nobody in the house "
               "can say who had the controller last.",
    "branches": [
     {"answer": "Three people used the same pad tonight, so nobody felt "
                "like the one who had to put it back", "cause": "KC-012"},
     {"answer": "There's no rule that says the credits rolling is when "
                "it goes back on the dock", "cause": "KC-009"},
     {"answer": "It's been missing long enough that an empty cradle "
                "just reads as normal instead of a problem to solve",
      "cause": "RC-017"},
    ]},
  ],
  "first_15": {
   "action": "Pull every disc case, spare remote, headset, and loose "
             "cable out of the cabinet onto the floor. Anything that "
             "pairs with a console or a television you no longer own "
             "leaves today, including any remote you have been keeping "
             "in case. Check the dock: if a cradle is empty, that "
             "controller is loose in the house, and you go find it now "
             "rather than at the start of the next game.",
   "victory": "Every remaining disc case, controller, and cable in the "
              "cabinet pairs with a console or television the house "
              "still owns, and every dock cradle holds the controller "
              "that belongs in it.",
  },
 },
 "Toy and Play Zone": {
  "frictions": [
   {"symptom": "A large, loud toy a relative gave takes up its own "
               "space on the shelf, and no child has reached for it "
               "without being pointed at it in months.",
    "branches": [
     {"answer": "It's kept for the giver, not for a child who plays "
                "with it, and letting go of it feels disloyal",
      "cause": "RC-014"},
     {"answer": "Nobody's actually run the honest week test to see "
                "whether a child reaches for it unprompted, so the "
                "question keeps getting deferred", "cause": "RC-015"},
     {"answer": "It's sat in the same spot so long it doesn't register "
                "as unused clutter anymore, just furniture",
      "cause": "RC-017"},
    ]},
   {"symptom": "The bins on the shelf are crammed two deep with toys "
               "that belong in the overflow bins in the closet, not on "
               "this shelf at all.",
    "branches": [
     {"answer": "The overflow is stored right here on the play shelf "
                "instead of the closet, so the shelf never gets down "
                "to five or six real choices", "cause": "KC-003"},
     {"answer": "A bin crammed two deep hides half of what's inside it "
                "from a child looking down at the label",
      "cause": "KC-005"},
     {"answer": "There's no trigger that says a bin gets swapped in "
                "from the closet by name and the old one goes back "
                "out, so overflow just keeps arriving here instead",
      "cause": "KC-009"},
    ]},
   {"symptom": "A wheel snapped off a toy vehicle and a handful of "
               "small figure accessories are loose on the floor a "
               "crawling child also uses.",
    "branches": [
     {"answer": "Pieces small enough to fit through a toilet paper "
                "tube ended up on a floor a crawling child can reach, "
                "and that outranks anything else about this shelf",
      "cause": "KC-010"},
     {"answer": "Nobody's agreed that a cracked or broken toy comes "
                "off the shelf the moment it's noticed, so it just "
                "stays in rotation", "cause": "KC-008"},
     {"answer": "Nobody specifically checks this shelf and floor for a "
                "broken edge or a stray small part between resets",
      "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Pull every toy off the shelf and run the two-question "
             "sort in the open: does a child actually reach for this "
             "without being pointed at it, and is it in one piece with "
             "no small part loose enough to choke on. Anything nobody "
             "has chosen in the last honest week, and anything cracked "
             "or missing a piece that could be swallowed, comes off the "
             "shelf today.",
   "victory": "Only toys a child actually chooses remain on the shelf, "
              "none of them cracked or missing a small part, sorted "
              "into five or six open bins a child can see into from "
              "standing height.",
  },
 },
 "Board Game and Puzzle Zone": {
  "frictions": [
   {"symptom": "A game box has been missing one piece for longer than "
               "anyone can remember, and it never got a sticky note or "
               "a deadline.",
    "branches": [
     {"answer": "The missing piece is structural, a board section or a "
                "single puzzle piece, and the game is already over "
                "even though the box still looks fine on the shelf",
      "cause": "RC-015"},
     {"answer": "Nobody's the one who checks a box's piece count "
                "before it goes back on the shelf, so a loss from last "
                "time goes unnoticed until the next play",
      "cause": "RC-013"},
     {"answer": "The box has sat looking complete for so long that the "
                "missing piece has stopped registering as a problem",
      "cause": "RC-017"},
    ]},
   {"symptom": "A stack of six or seven boxes on a high shelf has to "
               "come down as one weight to reach the bottom one.",
    "branches": [
     {"answer": "That much weight coming down at once onto whoever "
                "reaches the bottom box is a real fall and crush risk "
                "that outranks how compact the stack looks",
      "cause": "KC-010"},
     {"answer": "The shelf sits high enough that reaching the bottom "
                "box safely isn't possible without pulling the whole "
                "stack down first", "cause": "KC-006"},
     {"answer": "Getting the bottom box out means moving five others "
                "first, every single time", "cause": "KC-004"},
    ]},
   {"symptom": "You can't read which game is which from across the "
               "room, and dice and pawns from an open box are "
               "scattered on the same floor the play zone shares with "
               "a young child.",
    "branches": [
     {"answer": "Nobody's put a tape strip naming the game on the "
                "short edge, so the only way to identify it is pulling "
                "the whole box out", "cause": "KC-005"},
     {"answer": "Loose dice and pawns on a shared floor are a choke "
                "hazard for a crawling child, independent of how the "
                "shelf looks", "cause": "KC-010"},
     {"answer": "There's no habit of bagging loose pieces inside the "
                "lid before the box goes back, so pieces migrate onto "
                "the floor between plays", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Pull every box and check its lid for a name label and a "
             "tape strip on the short edge. While each one is open, "
             "count the pieces against the box's own list. If "
             "something is missing, decide now whether it's "
             "substitutable (a token, a die, a bill of play money you "
             "can replace) or structural (a rules booklet, a board "
             "section, a single puzzle piece). Write the missing item "
             "and today's date on a sticky note on any box you are not "
             "fixing immediately.",
   "victory": "Every box on the shelf is labeled and stacked no more "
              "than five high, and any box missing a piece carries a "
              "dated sticky note naming exactly what is gone.",
  },
 },
 "Blanket and Comfort Zone": {
  "frictions": [
   {"symptom": "A fleece throw is draped over the radiator to dry or "
               "just to be out of the way, right where the room's "
               "heat source runs hottest.",
    "branches": [
     {"answer": "Synthetic fabric left against a hot surface once the "
                "room empties is a real fire risk, and that overrides "
                "how convenient the spot is", "cause": "KC-010"},
     {"answer": "The basket is already full, so draping it over the "
                "radiator is easier than working it back in",
      "cause": "KC-007"},
     {"answer": "Nobody's decided a radiator isn't a storage spot for "
                "a throw, so it just keeps happening", "cause": "KC-002"},
    ]},
   {"symptom": "The good-looking wool throw sits folded and untouched "
               "on the arm of a chair while a pilled fleece gets "
               "fought over every night.",
    "branches": [
     {"answer": "The wool one is kept because it matches the room, not "
                "because anyone reaches for it, and that's a decision "
                "about looks standing in for a decision about use",
      "cause": "RC-015"},
     {"answer": "An heirloom blanket a relative knitted is being kept "
                "here out of guilt rather than because anyone actually "
                "wraps up in it", "cause": "RC-014"},
     {"answer": "The room has more throws than the one basket's job "
                "needs once you count only the ones people actually "
                "reach for", "cause": "KC-001"},
    ]},
   {"symptom": "A throw slides off the sofa arm onto the floor in the "
               "dark, right where the next person puts a foot when "
               "they stand up.",
    "branches": [
     {"answer": "A throw left on the floor in a walked path in the "
                "dark is a fall hazard, plain and simple",
      "cause": "KC-010"},
     {"answer": "There's no habit of folding it back into the basket "
                "the moment the last lamp goes off, so it just stays "
                "where it landed", "cause": "KC-009"},
     {"answer": "Nobody in the house treats putting a dropped throw "
                "away as specifically their job", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "Pull every throw and cushion out and fold each throw to "
             "the same rectangle so the fold edges line up in the "
             "basket. Run the reaches test out loud: which ones "
             "actually get pulled off the pile in an average week. The "
             "decorative one nobody reaches for goes to the guest bed "
             "or out, and a genuine heirloom nobody unfolds goes to "
             "the linen closet or to the person who will actually use "
             "it.",
   "victory": "One basket holds one throw per regular seat plus one "
              "spare, all folded to the same rectangle, and nothing is "
              "draped over the sofa back, a radiator, or a chair arm.",
  },
 },
 "Charging and Device Zone": {
  "frictions": [
   {"symptom": "A retired phone sits in the drawer, kept as both a "
               "backup that hasn't been charged in a year and an "
               "archive that was never transferred.",
    "branches": [
     {"answer": "It's serving two contradictory jobs at once and "
                "actually doing neither, and nobody's settled which "
                "one it is", "cause": "RC-015"},
     {"answer": "The photos on it matter to someone, which is a real "
                "reason to keep it, but transferring them is a task "
                "that's been avoided rather than a home it's missing",
      "cause": "RC-014"},
     {"answer": "A phone with a swollen or dead battery sitting loose "
                "in a drawer is a real hazard, not just clutter",
      "cause": "KC-010"},
    ]},
   {"symptom": "A charging cable hangs in a loop from the side table "
               "down to the floor at exactly toddler neck height, on "
               "the same table where drinks get set down.",
    "branches": [
     {"answer": "A loose loop at a toddler's neck height and a drink "
                "beside a live strip are both safety constraints that "
                "outrank tidy", "cause": "KC-010"},
     {"answer": "Nobody's shortened or clipped the cable flat since it "
                "was first run, because nobody specifically checks "
                "this station for hazards", "cause": "RC-013"},
     {"answer": "Nobody notices a specific cable type has run out "
                "until a device needs it and there's no spare left in "
                "the bag", "cause": "KC-011"},
    ]},
   {"symptom": "A tablet is charging under a blanket on the sofa "
               "cushion instead of on the strip, and it's warm to the "
               "touch.",
    "branches": [
     {"answer": "Charging on soft material that traps heat against a "
                "battery is a fire risk that overrides where it's "
                "convenient to leave it", "cause": "KC-010"},
     {"answer": "The station's slots are already all taken, so the "
                "next device charges wherever there's an open outlet",
      "cause": "KC-007"},
     {"answer": "There's no rule that every device charges at the one "
                "strip, so people default to whatever socket is "
                "closest", "cause": "KC-008"},
    ]},
  ],
  "first_15": {
   "action": "Match every cable at the station to a device the house "
             "actually uses, and keep one spare of each connector type "
             "in a labeled bag. Pull the retired phone out of the "
             "drawer, charge it, and decide out loud whether it is "
             "genuinely a backup or an archive. If it is an archive, "
             "transfer the photos now while it is charged and in your "
             "hand; if it is neither, recycle it with the battery "
             "still in it at a proper collection point.",
   "victory": "Every cable at the station ends at a named device the "
              "house uses, the retired phone has been settled as "
              "backup, archive, or recycled, and no charger is plugged "
              "in anywhere else in the room.",
  },
 },
 "Craft and Activity Zone": {
  "frictions": [
   {"symptom": "Seed beads and pompoms from the kits-in-progress bin "
               "are scattered on the floor this room shares with a "
               "crawling child, and finding the glue means opening "
               "three different bins.",
    "branches": [
     {"answer": "Small beads on a floor a crawling child also uses are "
                "a choke hazard that overrides anything about the "
                "room's tidiness", "cause": "KC-010"},
     {"answer": "Supplies aren't grouped by activity the way the four "
                "labeled bins are supposed to work, so finding one "
                "thing means opening several", "cause": "KC-004"},
     {"answer": "The bins have drifted out of their labeled categories "
                "over time, so what's inside no longer matches what "
                "the label promises", "cause": "KC-002"},
    ]},
   {"symptom": "A half-finished project has held the good end of the "
               "work surface for months, and clearing it feels like "
               "quitting.",
    "branches": [
     {"answer": "It's a decision nobody's made about whether the "
                "project is actually still active, not a storage "
                "problem", "cause": "RC-015"},
     {"answer": "It's been sitting on the table so long that it "
                "doesn't register as unfinished anymore, just part of "
                "the furniture", "cause": "RC-017"},
     {"answer": "The project stalled because it never got a named "
                "next action and a day to do it, so it just sits",
      "cause": "KC-009"},
    ]},
   {"symptom": "The glue gun is still plugged in on the table after "
               "everyone's walked away, and the scissors are sitting "
               "blade up where a child reaches across the table.",
    "branches": [
     {"answer": "A hot glue tip and blade-up scissors within a "
                "child's reach are safety constraints that outrank how "
                "the table looks", "cause": "KC-010"},
     {"answer": "There's no standard that scissors go back point down "
                "in the cup and the glue gun gets unplugged before "
                "anyone leaves the table", "cause": "KC-008"},
     {"answer": "Nobody specifically checks the table for a hot tool "
                "before the room empties", "cause": "RC-013"},
    ]},
  ],
  "first_15": {
   "action": "For any project sitting on the work surface, name its "
             "very next physical action and the day you will do it, "
             "out loud. If you can't produce both without stalling, "
             "the project is finished whether it says so or not. Break "
             "it down: good materials go back into the paper, drawing, "
             "or glue bins where the next project can use them, and "
             "the partly worked piece goes to someone who will finish "
             "it or goes out. Put the scissors point down in the cup "
             "and unplug the glue gun.",
   "victory": "The work surface is completely clear except for at "
              "most one active project bin, every scissors sits point "
              "down in its cup, and the glue gun is unplugged.",
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
 ("Primary Media Zone", "FRF-002",
  "A SECOND CONSOLE HAS SAT UNPLUGGED FOR TWO YEARS",
  "an older video game console sitting unplugged and dusty behind a "
  "newer console on the same media shelf"),
 ("Primary Media Zone", "FRF-003",
  "DUST HAS CAKED THICK IN THE CONSOLE'S VENT SLOTS",
  "a close view of a console's vent slots caked with visible dust, the "
  "unit pulled slightly away from the wall"),
 ("Primary Media Zone", "FRF-001",
  "NOBODY KNOWS WHO HAD THE CONTROLLER LAST",
  "an empty charging cradle on a media shelf beside a docked controller, "
  "a second empty cradle without its pad"),

 ("Toy and Play Zone", "FRF-004", "NO CHILD HAS CHOSEN THIS TOY IN MONTHS",
  "a large, oversized toy standing untouched in a corner of a play area "
  "while smaller toys nearby show wear"),
 ("Toy and Play Zone", "FRF-005", "THE SHELF BINS ARE CRAMMED TWO DEEP",
  "an open toy bin on a low shelf crammed two layers deep, the back "
  "layer hidden from a child looking down"),
 ("Toy and Play Zone", "FRF-006",
  "A LOOSE WHEEL AND SMALL PARTS SIT ON THE PLAY FLOOR",
  "a small toy vehicle wheel and a few loose figure accessories lying "
  "on an open floor near a low toy shelf"),

 ("Board Game and Puzzle Zone", "FRF-007",
  "ONE BOX HAS BEEN MISSING A PIECE FOR YEARS",
  "a board game box lid lying open with an empty compartment where one "
  "piece should sit"),
 ("Board Game and Puzzle Zone", "FRF-008",
  "A SIX-BOX STACK HAS TO COME DOWN AS ONE WEIGHT",
  "a tall stack of board game boxes on a shelf, six high, leaning "
  "slightly as a hand reaches for the bottom one"),
 ("Board Game and Puzzle Zone", "FRF-009",
  "YOU CAN'T READ WHICH GAME IS WHICH FROM THE DOORWAY",
  "a row of board game boxes on a shelf with no visible name markings "
  "on their short edges"),

 ("Blanket and Comfort Zone", "FRF-010",
  "A THROW IS DRAPED OVER THE RADIATOR AGAIN",
  "a fleece throw draped directly across a home radiator in a family "
  "room"),
 ("Blanket and Comfort Zone", "FRF-011",
  "THE GOOD THROW SITS FOLDED AND UNTOUCHED",
  "a neatly folded wool throw sitting untouched on a chair arm beside a "
  "well worn fleece throw"),
 ("Blanket and Comfort Zone", "FRF-012",
  "A THROW SLID OFF THE SOFA ARM IN THE DARK",
  "a throw lying on the floor beside a sofa in a dimly lit family room"),

 ("Charging and Device Zone", "FRF-013",
  "THE RETIRED PHONE IS BOTH A BACKUP AND AN ARCHIVE",
  "an old phone sitting in an open drawer beside tangled cables, its "
  "screen dark and uncharged"),
 ("Charging and Device Zone", "FRF-015",
  "A CHARGING CABLE LOOPS TOWARD THE FLOOR AT NECK HEIGHT",
  "a charging cable hanging in a low loop from a side table down "
  "toward the floor beside a drink glass"),
 ("Charging and Device Zone", "FRF-014",
  "A TABLET IS CHARGING UNDER A BLANKET ON THE SOFA",
  "a tablet charging beneath a folded blanket on a sofa cushion, its "
  "cable running off to a wall outlet"),

 ("Craft and Activity Zone", "FRF-018",
  "BEADS ARE SCATTERED ON THE FLOOR NEAR A CRAWLING CHILD",
  "small craft beads and pompoms scattered on a floor near a low craft "
  "table"),
 ("Craft and Activity Zone", "FRF-016",
  "A HALF-FINISHED PROJECT HAS HELD THE TABLE FOR MONTHS",
  "a partly completed craft project spread across a family room table, "
  "materials scattered around it"),
 ("Craft and Activity Zone", "FRF-017",
  "THE GLUE GUN IS STILL PLUGGED IN AFTER EVERYONE LEFT",
  "a glue gun left plugged in on an empty craft table beside a pair of "
  "scissors lying blade up"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, family-room-scened art only. The name, meaning,
# six_s and confirm_in_30_seconds text are not reauthored: they are read
# straight from ops/root_causes.py, the one shared vocabulary the deck,
# the app and the articles all already use.
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "two video game consoles crowded onto one media shelf where "
           "only one console's controllers and cables actually get used",
 "KC-002": "a fleece throw lying across a hot radiator instead of the "
           "basket sitting empty a few feet away",
 "KC-003": "a stack of overflow toy bins sitting on a play shelf instead "
           "of on a closet shelf across the hall",
 "KC-004": "a hand pulling five stacked board game boxes off a shelf "
           "just to reach the one on the bottom",
 "KC-005": "a game box with no name visible on its short edge standing "
           "on a shelf across a family room",
 "KC-006": "a stack of board game boxes sitting on a shelf mounted "
           "higher than a seated child could safely reach",
 "KC-007": "a charging strip with every slot already filled while "
           "another cable waits with nowhere to plug in",
 "KC-008": "a pair of scissors lying blade up on a craft table beside "
           "an unplugged cup meant to hold them point down",
 "KC-009": "a game controller sitting off its charging dock long after "
           "the television screen has gone dark",
 "KC-010": "a charging cable hanging in a low loop from a side table "
           "toward the floor of a family room",
 "KC-011": "an empty labeled bag where a spare charging cable connector "
           "should be sitting beside a charging strip",
 "KC-012": "two hands reaching for the same game controller at the same "
           "media shelf",
 "RC-013": "a throw lying on a family room floor beside a sofa, "
           "untouched since it slid off the arm the night before",
 "RC-014": "an oversized toy standing untouched in a corner of a family "
           "room while smaller toys nearby show real wear",
 "RC-015": "a half finished craft project still spread across a family "
           "room table weeks after it was started",
 "RC-016": "a thick layer of dust sitting in the vent slots on the back "
           "of a console pulled slightly away from the wall",
 "RC-017": "an empty charging cradle on a media shelf that has sat "
           "empty long enough nobody in the family notices it anymore",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded in
# that zone's own Manual passes. Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Primary Media Zone": [
  "Brush the vent slots on each console with a vacuum brush head, "
  "working along every slot rather than just the front face.",
  "Wipe the controller grips and thumbstick collars with a barely damp "
  "cloth, working into the seams around the buttons.",
  "Finish the screen with a dry microfiber cloth only, never a spray or "
  "a damp cloth.",
 ],
 "Toy and Play Zone": [
  "Wash one hard plastic toy in mild soapy water and dry it fully "
  "before it goes back in a closed bin.",
  "Run the fabric dolls and soft blocks through the machine in a mesh "
  "wash bag.",
  "Lift the play mat and vacuum the crumbs collected underneath it.",
 ],
 "Board Game and Puzzle Zone": [
  "Wipe the lid and edges of one box, working off the film a room where "
  "people eat leaves behind.",
  "Check the bottom box in each stack for soft or bowed corners, and "
  "shorten any stack crushing it.",
  "Vacuum the shelf face where box corners rest, clearing the dust that "
  "collects along that edge.",
 ],
 "Blanket and Comfort Zone": [
  "Wash every throw in the basket this round, even the ones that still "
  "look clean.",
  "Vacuum the basket's inside corners before the clean throws go back "
  "in.",
  "Wipe the floor cushions on both sides before restacking them beside "
  "the basket.",
 ],
 "Charging and Device Zone": [
  "Wipe each cable end and check the last few centimetres near the "
  "plug, where the sheath cracks first.",
  "Blow or brush the lint out of every charging port on the strip.",
  "Wipe the hard surface under the strip where dust and crumbs collect "
  "around the cables.",
 ],
 "Craft and Activity Zone": [
  "Scrape dried glue and paint off the work surface with a plastic "
  "scraper before you wipe it.",
  "Work a cloth into the cracks along the table edge where glitter "
  "settles and hides.",
  "Stand every brush bristle up in its cup so it dries without "
  "bending.",
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
 {"id": "FRA-001", "zone": "Primary Media Zone",
  "title": "CLEAR THE CABINET AND FIND THE LOOSE CONTROLLER",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the cabinet down to what pairs with a console or "
          "television the house still owns, and track down any "
          "controller missing from its dock.",
  "why": "A remote kept in case and a controller nobody feels "
         "responsible for both cost the same shelf space as the "
         "console people actually use.",
  "inputs": ["a bin bag", "a box for anything to donate"],
  "steps": [
   "Pull every disc case, spare remote, headset, and loose cable out of "
   "the cabinet onto the floor. Anything that pairs with a console or a "
   "television you no longer own leaves today, including any remote "
   "you have been keeping in case. Check the dock: if a cradle is "
   "empty, that controller is loose in the house, and you go find it "
   "now rather than at the start of the next game.",
   "Return the console cabinet to one shelf per console, controllers "
   "docked beside it."],
  "causes": ["KC-012", "KC-009"],
  "victory": "Every remaining disc case, controller, and cable in the "
             "cabinet pairs with a console or television the house "
             "still owns, and every dock cradle holds the controller "
             "that belongs in it.",
  "next": "FRS-001",
  "art": "a media cabinet mid clear, a small box of outdated remotes "
         "being carried out and a controller being returned to an "
         "empty dock cradle"},

 {"id": "FRA-002", "zone": "Primary Media Zone",
  "title": "SETTLE THE SECOND CONSOLE AND LABEL WHAT STAYS",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Decide the previous-generation console's fate for good: move "
          "its save data or let it go, then label every cable and "
          "pairing that remains.",
  "why": "A console that has sat unplugged for two years guarding one "
         "save file is still taking up a shelf that only fits one "
         "console's job at a time.",
  "inputs": ["a memory card or transfer cable", "cable labels",
             "a marker", "an index card"],
  "steps": [
   "Plug in the older console and either move the save data to a card "
   "or to the current console, or hand a controller over for one real "
   "session to see if anyone still cares.",
   "If it will not power on, or nobody asks for it again, route the "
   "console, its controllers, and its cables out together in one trip.",
   "Label both ends of every remaining cable and tape a pairing card "
   "inside the cabinet door naming which controller and headset belong "
   "to which console."],
  "causes": ["RC-014", "RC-015", "KC-001"],
  "victory": "The second console is either transferred and in active "
             "use or gone from the shelf entirely, and every remaining "
             "cable is labeled at both ends.",
  "next": "FRA-001",
  "art": "a hand transferring save data from an older console before "
         "it and its controllers leave the shelf together in one box"},

 {"id": "FRA-003", "zone": "Toy and Play Zone",
  "title": "RUN THE TWO-QUESTION TOY SORT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Pull every toy off the shelf and keep only what a child "
          "actually chooses and what is safe to keep.",
  "why": "A toy nobody reaches for and a cracked one both cost a bin "
         "that a favorite toy doesn't currently have.",
  "inputs": ["a donation box", "a bin bag"],
  "steps": [
   "Pull every toy off the shelf and run the two-question sort in the "
   "open: does a child actually reach for this without being pointed "
   "at it, and is it in one piece with no small part loose enough to "
   "choke on. Anything nobody has chosen in the last honest week, and "
   "anything cracked or missing a piece that could be swallowed, comes "
   "off the shelf today.",
   "Sort what remains into five or six open bins, one category each."],
  "causes": ["RC-015", "RC-014", "KC-010"],
  "victory": "Only toys a child actually chooses remain on the shelf, "
             "none of them cracked or missing a small part, sorted "
             "into five or six open bins a child can see into from "
             "standing height.",
  "next": "FRS-002",
  "art": "a hand sorting toys on a floor into a keep pile of open bins "
         "and a donation box, a cracked toy set aside for the bin"},

 {"id": "FRA-004", "zone": "Toy and Play Zone",
  "title": "SWAP THE OVERFLOW BIN AND PHOTO-LABEL THE SHELF",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Move overflow off the play shelf into labeled bins in the "
          "closet, and tape a photo of each bin's contents to its "
          "front face.",
  "why": "The trap here is storing more than the room actually plays; "
         "fewer visible choices means longer play and a pickup that "
         "finishes inside one song.",
  "inputs": ["a camera or phone", "printed photos or a printer", "tape",
             "labeled bins for the closet"],
  "steps": [
   "Move anything that does not fit in five or six open bins to "
   "labeled bins in the closet.",
   "Photograph the contents of each remaining bin and tape the picture "
   "to its front face at a child's eye level.",
   "Agree the swap rule: a closet bin comes in only when a child asks "
   "for it by name, and the bin it replaces goes back out."],
  "causes": ["KC-003", "KC-005", "KC-009"],
  "victory": "Five or six open bins sit on the shelf, each with a photo "
             "label a child can read from standing height, and the "
             "overflow is stored in named bins in the closet.",
  "next": "FRA-003",
  "art": "a labeled overflow bin being carried from a closet shelf to "
         "swap with a photo-labeled bin already on the play shelf"},

 {"id": "FRA-005", "zone": "Board Game and Puzzle Zone",
  "title": "COUNT EVERY BOX AND STICKY-NOTE WHAT'S MISSING",
  "minutes": 15, "players": "1", "six_s": "Standardize",
  "from_first_15": True,
  "goal": "Check each box's piece count and label the ones that are "
          "missing something with a date.",
  "why": "A box that looks complete on the shelf and empties out short "
         "at game night is worse than an empty shelf, because it "
         "wastes the one evening you had to play it.",
  "inputs": ["sticky notes", "a pen", "tape strips for labeling"],
  "steps": [
   "Pull every box and check its lid for a name label and a tape strip "
   "on the short edge. While each one is open, count the pieces "
   "against the box's own list. If something is missing, decide now "
   "whether it's substitutable (a token, a die, a bill of play money "
   "you can replace) or structural (a rules booklet, a board section, "
   "a single puzzle piece). Write the missing item and today's date on "
   "a sticky note on any box you are not fixing immediately.",
   "Stack the checked boxes no more than five high, name readable on "
   "the short edge."],
  "causes": ["RC-013", "RC-015"],
  "victory": "Every box on the shelf is labeled and stacked no more "
             "than five high, and any box missing a piece carries a "
             "dated sticky note naming exactly what is gone.",
  "next": "FRS-003",
  "art": "a hand counting game pieces against a box's checklist beside "
         "a sticky note reading a missing piece and today's date"},

 {"id": "FRA-006", "zone": "Board Game and Puzzle Zone",
  "title": "SETTLE EVERY DATED STICKY NOTE AND RESTACK BY REACH",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Decide substitutable or structural for every box still "
          "carrying a dated missing-piece note, act on it, and restack "
          "so the bottom of any deep pile is not the one played most.",
  "why": "A vague guilt about an incomplete game turns into a deadline "
         "you can meet or honestly fail the moment it is written down "
         "and dated, and a stack that always makes you move five boxes "
         "to reach the one you want is charging you rent every game "
         "night.",
  "inputs": ["replacement tokens, dice, or coins", "a donation box"],
  "steps": [
   "Pull every box still wearing a dated sticky note.",
   "For a substitutable loss, replace it now with a coin, button, "
   "printed sheet, or a request to the publisher, and remove the note.",
   "For a structural loss, or any note still on a box from before "
   "today, take the game off the shelf and donate or recycle it.",
   "Restack so the games played most often sit on top or at a "
   "reachable height, not buried under five others."],
  "causes": ["RC-015", "KC-006", "KC-004"],
  "victory": "No box on the shelf carries a sticky note older than "
             "today, every remaining box has passed its count, and the "
             "games played most are not buried at the bottom of a "
             "stack.",
  "next": "FRA-005",
  "art": "a hand removing a settled sticky note from a game box lid, a "
         "replacement token sitting beside it"},

 {"id": "FRA-007", "zone": "Blanket and Comfort Zone",
  "title": "FOLD, TEST BY REACHES, AND RELOCATE THE DECORATIVE ONE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Fold every throw to match, test the basket by what people "
          "actually reach for, and give the decorative one a real home "
          "elsewhere.",
  "why": "The test is reaches, not looks: a basket that stores comfort "
         "has to hold what people actually pull off the pile.",
  "inputs": ["a laundry basket for anything leaving",
             "the guest room as a destination"],
  "steps": [
   "Pull every throw and cushion out and fold each throw to the same "
   "rectangle so the fold edges line up in the basket. Run the reaches "
   "test out loud: which ones actually get pulled off the pile in an "
   "average week. The decorative one nobody reaches for goes to the "
   "guest bed or out, and a genuine heirloom nobody unfolds goes to "
   "the linen closet or to the person who will actually use it."],
  "causes": ["RC-015", "RC-014", "KC-002"],
  "victory": "One basket holds one throw per regular seat plus one "
             "spare, all folded to the same rectangle, and nothing is "
             "draped over the sofa back, a radiator, or a chair arm.",
  "next": "FRS-004",
  "art": "a hand folding throws to a matching rectangle in a basket, "
         "one decorative throw set aside to move to the guest room"},

 {"id": "FRA-008", "zone": "Blanket and Comfort Zone",
  "title": "MOVE EVERY THROW OFF THE RADIATOR AND SHORTEN THE NIGHT "
           "ROUTINE",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Clear every throw off the radiator, heater, or lamp shade "
          "for good, and agree the last-lamp fold-back routine.",
  "why": "Synthetic fabric left against a hot surface once the room "
         "empties is a slow fire that starts after everyone has gone "
         "to bed.",
  "inputs": ["none beyond the basket itself"],
  "steps": [
   "Walk the room and move every throw draped over a radiator, heater, "
   "or lamp shade back into the basket.",
   "Agree out loud: when the last lamp goes off, whoever is last up "
   "folds any throw back into the basket before leaving the room.",
   "Check that the basket itself is not blocking the walked path "
   "between the sofa and the door."],
  "causes": ["KC-010", "KC-009"],
  "victory": "No throw is draped over a radiator, heater, or lamp "
             "shade anywhere in the room, and the last-lamp fold-back "
             "routine is agreed out loud.",
  "next": "FRA-007",
  "art": "a throw being lifted off a radiator and folded back into a "
         "basket beside a sofa in the evening"},

 {"id": "FRA-009", "zone": "Charging and Device Zone",
  "title": "MATCH EVERY CABLE AND SETTLE THE OLD PHONE",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Match every cable to a device the house uses, stock one "
          "spare connector of each type, and settle the retired phone "
          "for good.",
  "why": "A retired phone serving as both an unused backup and a never"
         "-made archive is doing neither job while it takes up the "
         "drawer, and a full strip cluttered with dead connections is "
         "why the next device ends up charging somewhere unsafe.",
  "inputs": ["a labeled bag for spare connectors", "a charging cable",
             "a recycling drop-off location"],
  "steps": [
   "Match every cable at the station to a device the house actually "
   "uses, and keep one spare of each connector type in a labeled bag. "
   "Pull the retired phone out of the drawer, charge it, and decide "
   "out loud whether it is genuinely a backup or an archive. If it is "
   "an archive, transfer the photos now while it is charged and in "
   "your hand; if it is neither, recycle it with the battery still in "
   "it at a proper collection point."],
  "causes": ["RC-015", "KC-010", "KC-007", "KC-011"],
  "victory": "Every cable at the station ends at a named device the "
             "house uses, the retired phone has been settled as "
             "backup, archive, or recycled, and no charger is plugged "
             "in anywhere else in the room.",
  "next": "FRS-005",
  "art": "a hand transferring photos from an old phone plugged into a "
         "charger, a labeled bag of spare cable connectors beside it"},

 {"id": "FRA-010", "zone": "Charging and Device Zone",
  "title": "SHORTEN THE CABLE LOOP AND MOVE DRINKS OFF THE STATION",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Shorten or clip flat any cable hanging at toddler neck "
          "height, and give the charging surface a no-drinks rule.",
  "why": "A loop at a toddler's neck height and a glass beside a live "
         "strip are both safety constraints that outrank how "
         "convenient the table is.",
  "inputs": ["cable clips", "a coaster or drink shelf elsewhere in the "
             "room"],
  "steps": [
   "Shorten or clip flat any cable that hangs low enough to loop at a "
   "toddler's neck height.",
   "Move where people set down drinks to a surface away from the "
   "charging strip.",
   "Check every device on the strip for swelling, heat, or a bulging "
   "seam, and take any that fail off the strip permanently."],
  "causes": ["KC-010", "RC-013"],
  "victory": "No cable hangs loose enough to loop at toddler height, no "
             "drink lands on the charging surface, and every device on "
             "the strip passes a swelling and heat check.",
  "next": "FRA-009",
  "art": "a hand clipping a charging cable flat to a table edge, a "
         "drink resting on a separate surface away from the power "
         "strip"},

 {"id": "FRA-011", "zone": "Craft and Activity Zone",
  "title": "NAME THE NEXT ACTION OR BREAK DOWN THE PROJECT",
  "minutes": 15, "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Name the very next physical action and the day for any "
          "project on the table, or break it down for good.",
  "why": "A project that cannot produce a next action and a day "
         "finished a while ago without telling anyone, and it is the "
         "only thing standing between this table and dinner.",
  "inputs": ["the four labeled bins", "a bag for a partly worked piece "
             "leaving the house"],
  "steps": [
   "For any project sitting on the work surface, name its very next "
   "physical action and the day you will do it, out loud. If you "
   "can't produce both without stalling, the project is finished "
   "whether it says so or not. Break it down: good materials go back "
   "into the paper, drawing, or glue bins where the next project can "
   "use them, and the partly worked piece goes to someone who will "
   "finish it or goes out. Put the scissors point down in the cup and "
   "unplug the glue gun."],
  "causes": ["RC-015", "KC-009"],
  "victory": "The work surface is completely clear except for at most "
             "one active project bin, every scissors sits point down "
             "in its cup, and the glue gun is unplugged.",
  "next": "FRS-006",
  "art": "a work surface being cleared of a half finished project, "
         "materials sorted back into labeled paper, drawing, and glue "
         "bins"},

 {"id": "FRA-012", "zone": "Craft and Activity Zone",
  "title": "UNPLUG THE GLUE GUN, POINT THE SCISSORS DOWN, AND SHELVE "
           "THE SMALL PARTS",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Set a hard stop for hot tools and small parts every time the "
          "table is used: scissors point down, glue gun unplugged, "
          "beads and solvents up high.",
  "why": "A hot glue tip and blade-up scissors within a child's reach, "
         "and beads on a floor shared with a crawling child, are "
         "safety constraints that outrank how the table looks.",
  "inputs": ["a cup for scissors", "a high shelf for beads, solvents, "
             "and craft knives"],
  "steps": [
   "Move all seed beads, googly eyes, pompoms, and solvent-based "
   "markers to a shelf above the youngest child's reach.",
   "Set a rule: scissors and craft knives go point or blade down in "
   "the cup the moment they are not in a hand.",
   "Agree that the glue gun gets unplugged the moment nobody is "
   "actively using it, not at the end of the session."],
  "causes": ["KC-010", "KC-008"],
  "victory": "Beads, solvents, and craft knives sit above the "
             "youngest child's reach, scissors stand point down in the "
             "cup, and the glue gun is unplugged whenever it is not in "
             "use.",
  "next": "FRA-011",
  "art": "a high shelf holding beads and solvent markers above a "
         "child's reach, scissors standing point down in a cup on a "
         "clear table"},

 {"id": "FRA-013", "zone": None,
  "title": "THE FULL FAMILY ROOM HAZARD WALK",
  "minutes": 30, "players": "1 to 2", "six_s": "Safety",
  "goal": "Walk every zone checking the television's anti-tip strap, "
          "vent heat, cables across the floor, the charging station's "
          "cable loop and drinks, and every choke-size small part on a "
          "floor a crawling child shares.",
  "why": "This is the room where a screen, a heater, small parts, and "
         "a hot glue gun all sit within a child's reach at the same "
         "time, so the hazards get found only if someone looks at all "
         "six zones on purpose.",
  "inputs": ["a childproof latch if needed", "cable clips", "a bin "
             "bag"],
  "steps": [
   "Push gently on the television's top edge and check the anti-tip "
   "strap or mount bolts by hand.",
   "Check for any blanket, disc case, or throw covering a vent slot, "
   "and clear it.",
   "Check the floor shared by the toy and board game zones for "
   "choke-size pieces, and the charging station for a cable loop at "
   "toddler height.",
   "Check the craft table for an unplugged glue gun and scissors "
   "stored point down."],
  "causes": ["KC-010", "RC-013", "RC-017", "RC-016"],
  "victory": "No vent is covered, no cord loops at toddler height, no "
             "choke-size piece sits on the floor, and the glue gun is "
             "unplugged.",
  "next": "FRA-014",
  "art": "a hand checking a television's anti-tip strap in a family "
         "room, a cleared floor and an unplugged glue gun visible in "
         "the same wide view"},

 {"id": "FRA-014", "zone": None, "title": "THE CREDITS-ROLL SWEEP",
  "minutes": 15, "players": "1", "six_s": "Sustain",
  "goal": "The moment the evening's screen time, play, or craft ends, "
          "walk all six zones once in the order the room is used: "
          "controllers to the dock, toys to their bins, games stacked "
          "and counted, throws folded to the basket, devices on the "
          "strip, and the craft table cleared.",
  "why": "Every zone in this room has its own trigger already; the "
         "sweep is what actually fires all six on the same night "
         "instead of one zone drifting a week behind the others.",
  "inputs": ["none beyond the room's own bins and baskets"],
  "steps": [
   "Dock every controller and remote before the television goes off.",
   "Return toys to their bins and games to the shelf, counted as they "
   "go back in the box.",
   "Fold throws into the basket and set every device on the charging "
   "strip.",
   "Clear the craft table to at most one active project bin."],
  "causes": ["KC-009", "RC-013"],
  "victory": "All six zones pass their own leave-behind standard on "
             "the same night, in one walk.",
  "next": "FRA-015",
  "art": "a hand completing the last step of an evening sweep, folding "
         "a throw into a basket beside a cleared craft table and a "
         "docked controller"},

 {"id": "FRA-015", "zone": None, "title": "THE OVERFLOW SWAP DAY",
  "minutes": 30, "players": "1", "six_s": "Standardize",
  "goal": "On a fixed day, swap the toy shelf's bins against the "
          "closet's labeled overflow bins by name, and re-photograph "
          "any bin whose contents changed.",
  "why": "The trap in this room is storing more than it plays; a swap "
         "that only happens when someone remembers to do it stops "
         "happening within a month.",
  "inputs": ["a calendar reminder", "a camera or phone", "labeled bins "
             "in the closet"],
  "steps": [
   "Pick a fixed day each month and put it on a shared calendar.",
   "On that day, swap at least one shelf bin for a named bin from the "
   "closet.",
   "Re-photograph the front face of any bin whose contents changed and "
   "retape the label."],
  "causes": ["KC-003", "KC-001"],
  "victory": "A swap happens on the same calendar day every month, and "
             "every bin's photo label matches what is actually inside "
             "it.",
  "next": "FRA-013",
  "art": "a labeled bin being swapped between a closet shelf and a "
         "play shelf, a calendar reminder visible pinned nearby"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a family room, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("FRE-001", "TWO KIDS WANT THE SAME CONTROLLER AT ONCE",
  "Two kids grab for the same game at the same time, and the argument "
  "is really about whose controller is missing.",
  ["FRZ-001"],
  "Both docks are full, so a spare pad is already sitting exactly "
  "where the argument needs it to be.",
  "If a cradle was empty and nobody could say where the controller "
  "went, the credits-roll handoff never happened. Draw FRA-001.",
  "two hands reaching for a media cabinet dock holding two full "
  "charging cradles side by side"),
 ("FRE-002", "A TODDLER VISITS FOR THE AFTERNOON",
  "A crawling toddler who has never been in this room before gets an "
  "hour of unsupervised floor time.",
  ["FRZ-002"],
  "Every bin at floor height holds pieces too large to choke on, and "
  "nothing cracked or broken is anywhere on the shelf.",
  "If a small figure accessory or a cracked toy was on that floor, the "
  "two-question sort slipped. Draw FRA-003.",
  "a toddler reaching into an open floor-level toy bin holding only "
  "large, uncracked pieces"),
 ("FRE-003", "GAME NIGHT PICKS THE BOX OFF THE TOP OF THE PILE",
  "Friends come over for game night and grab whatever box looks "
  "interesting from across the room, sight unseen.",
  ["FRZ-003"],
  "The name is readable from the doorway, the box comes down without "
  "pulling five others with it, and every piece is actually inside.",
  "If the label was unreadable, the stack came down as one weight, or "
  "a piece turned up missing mid-game, the count-and-label pass "
  "slipped. Draw FRA-005.",
  "a hand lifting a single labeled game box cleanly off a shelf "
  "stacked no more than five high"),
 ("FRE-004", "A COLD NIGHT AND FOUR PEOPLE ON THE SOFA AT ONCE",
  "Everyone wants a throw at the same time on the coldest night of the "
  "month, and the basket has to answer for all of them.",
  ["FRZ-004"],
  "One throw per regular seat plus a spare is already folded and "
  "ready in the basket, none of them on the radiator.",
  "If someone had to hunt for a throw draped over the radiator "
  "instead, the fold-and-test pass slipped. Draw FRA-007.",
  "a basket holding several matching folded throws being handed out "
  "to people seated around a sofa"),
 ("FRE-005", "EVERY DEVICE IN THE HOUSE NEEDS CHARGING BY BEDTIME",
  "Phones, tablets, controllers, and headphones all arrive at the "
  "station at once, at the exact hour the dishwasher usually starts.",
  ["FRZ-005"],
  "Every device has a named slot waiting for it, no charger is "
  "plugged in anywhere else in the room, and no drink sits on the "
  "surface.",
  "If a device had to charge on a cushion or at another outlet, the "
  "station is full of clutter instead of live connections. Draw "
  "FRA-009.",
  "several phones and a tablet charging together on one power strip on "
  "a hard surface, each cable ending at a labeled slot"),
 ("FRE-006", "DINNER IS BEING SET IN FIFTEEN MINUTES",
  "The table that has been a craft project all afternoon has to become "
  "a dinner table with no warning.",
  ["FRZ-006"],
  "The surface clears in one motion because only one project bin was "
  "ever out, the glue gun is already unplugged, and the scissors are "
  "already point down.",
  "If clearing the table took longer than the fifteen minutes allowed, "
  "the next-action test on the half-finished project was never run. "
  "Draw FRA-011.",
  "a work surface being wiped clear in one motion, one closed project "
  "bin already back on its shelf"),
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
        "related": {"standard": f"FRS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your family "
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
    standard_id = (f"FRS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"FRS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "FRR-001", "title": "THE FAMILY ROOM", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START WHERE THE CABLES CROSS THE FLOOR.",
        "objective": "The family room carries more jobs than any other "
                     "room in the house: screens, floor play, games, "
                     "blankets, charging, and craft all compete for the "
                     "same square meters. This card is the map and the "
                     "order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"FRZ-001 Primary Media Zone. {start_tip['text']}"
            if start_tip else
            "FRZ-001 Primary Media Zone. Its cables cross the floor "
            "into the other zones, so clearing it first lets the rest "
            "of the room tell you the truth about itself."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your family room. Put the rest back.",
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
        "safety_first": "Do FRA-013 The Full Family Room Hazard Walk "
                        "before any rebuild. It takes thirty minutes and "
                        "covers the television's anti-tip strap, the "
                        "vent heat behind the media unit, the cables "
                        "crossing the floor, the charging station's "
                        "cable loop, and the hot glue gun on the craft "
                        "table.",
        "related": {"contents": "FRZ-001 to FRZ-006, FRF-001 to "
                                 "FRF-018, the shared root causes in "
                                 "ops/root_causes.py, FRA-001 to "
                                 "FRA-015, FRS-001 to FRS-006, FRE-001 "
                                 "to FRE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole family "
                           "room in its settled state, a media unit "
                           "with one console per shelf, a low toy shelf "
                           "with open bins, a board game shelf, a "
                           "basket of folded throws beside the sofa, a "
                           "charging station, and a craft table all "
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
    return {"deck": "family-room", "room": ROOM, "count": len(cards),
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

    assert any(c["id"] == "FRA-013" for c in cards), "no safety walk card"
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
    print(f"  deck        family-room ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
