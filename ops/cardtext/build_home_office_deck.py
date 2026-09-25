#!/usr/bin/env python3
"""
Build the Home Office deck: 67 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT HAND AUTHORING
------------------------------------------------
BACKLOG-2026-09-07.md B9: the diagnosis layer supplies a friction's SYMPTOM
and every BRANCH to a root cause straight from
`content/manual/source/content.json`, the same corpus the 114 zone pages
already read. `ops/cardtext/build_kitchen_deck.py`,
`ops/cardtext/build_entryway_deck.py` and `ops/cardtext/build_laundry_room_deck.py`
proved the pattern for the first three rooms; this is the fourth. Purpose,
done_looks_like, the standard, the trigger, the first-15 action and its
victory condition are quoted from the Manual, not rewritten, and `gate()` at
the bottom asserts they are still character-for-character identical. The 18
frictions (three per zone) are likewise derived straight from the Manual's
own `diagnosis` layer, in zone order, not retyped, so this deck cannot
silently diverge from the diagnostic engine already shipped on the site's
zone pages.

The layers the Manual does not hold are hand authored below and marked: the
all-caps titles and art briefs for the zone and friction cards, the nine new
action cards (the Manual gives one 15-minute reset per zone in `first_15`;
the 30-minute rebuild per zone and three whole-room actions are authored
here), the event cards, the micro quests, and the room card. The root
causes are not reauthored: they are the same frozen vocabulary in
`ops/root_causes.py` that the Kitchen, Entryway and Laundry Room decks
already use, so a household owning more than one deck keeps one diagnosis
pile rather than several (DECK-GAME-DESIGN.md 4.3). This room's own
diagnosis data reaches fourteen of the shared vocabulary's seventeen
causes (every one except KC-012, RC-014 and RC-017, none of which any Home
Office friction branches to), confirmed against
content/manual/source/content.json before this file was written, not
assumed from any other room's count.

WHAT THIS DOES NOT DO
----------------------
It does not render cards and it does not draw anything, the same split
every prior room generator here keeps. There is no old, mismatched free
Home Office deck to disclose against: no free Home Office product exists on
the site yet, so this one ships as the first, at its own URL.

Run:  python ops/cardtext/build_home_office_deck.py
Out:  ops/cardtext/home-office-deck.json
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "home-office-deck.json")

sys.path.insert(0, os.path.join(ROOT, "ops"))
import root_causes as RC                                        # noqa: E402

ROOM = "Home Office"

# This room ships as a free typeset page, the same stage every prior room
# deck shipped at before any print-on-demand decision existed, so the
# budget here is the honest count of what this room's own corpus,
# diagnosis layer and a proportionate amount of new authorship produce: six
# real zones, fourteen reachable root causes, two actions per zone plus
# three whole-room ones.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 6, "FRICTION CARD": 18,
          "ROOT CAUSE CARD": 14, "ACTION CARD": 15, "STANDARD CARD": 6,
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

# Root causes this room's real diagnosis branches actually reach, derived
# below from the Manual and asserted (in gate()) to be exactly this set:
# not a number chosen first and filled in. Confirmed against
# content/manual/source/content.json before this file was written: every
# one of the six zones' nine diagnosis branches (18 frictions x 3 branches)
# was read and its "cause" field copied here verbatim.
CAUSE_IDS = ["KC-001", "KC-002", "KC-003", "KC-004", "KC-005", "KC-006",
             "KC-007", "KC-008", "KC-009", "KC-010", "KC-011",
             "RC-013", "RC-015", "RC-016"]

# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are done_looks_like broken into six countable things,
# the same art specification rule every prior room generator uses: every
# numbered item has to be a visible object in the hero.
# ---------------------------------------------------------------------------

ZONES = {
 "Primary Desk": {
  "id": "HOZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE INBOX TRAY. UNDER A DOZEN SHEETS, ALWAYS.",
  "callouts": [
   "Monitor, keyboard and mouse sitting in fixed positions",
   "One notebook on the desk",
   "One inbox tray holding fewer than a dozen sheets",
   "No sticky notes on the monitor bezel",
   "The power strip hooked off the floor onto the desk leg",
   "Bare carpet under the full arc the chair rolls through",
  ],
  "art": ("a desk with a monitor, keyboard and mouse in fixed positions, "
          "one notebook beside the keyboard, a single inbox tray holding "
          "a small stack of fewer than a dozen sheets, a bare monitor "
          "bezel with no sticky notes, a power strip hooked onto the "
          "desk leg off the floor, and bare carpet visible in the arc "
          "where a chair would roll"),
 },
 "Desk Drawers and Pedestal": {
  "id": "HOZ-002", "order": 2, "difficulty": 2,
  "tagline": "EVERY PEN WRITES. THE SCISSORS POINT DOWN.",
  "callouts": [
   "A divided tray in the top drawer",
   "Pens in the tray that all write",
   "One stapler in the tray",
   "Scissors resting point-down in their own slot",
   "A deep pedestal drawer of hanging files",
   "File tabs all standing in one line",
  ],
  "art": ("an open desk drawer showing a divided tray holding pens, one "
          "stapler, and scissors resting point-down in their own slot, "
          "beside a deep pedestal drawer of hanging files with every tab "
          "standing at the same height in one line"),
 },
 "File Storage": {
  "id": "HOZ-003", "order": 3, "difficulty": 3,
  "tagline": "ONE QUESTION PER FOLDER. ONE STRAIGHT LINE OF TABS.",
  "callouts": [
   "Hanging folders labeled by the question you would ask",
   "Every tab in the same position along the row",
   "A closed fireproof box holding the permanent originals",
   "A full shred bag standing by the door",
   "A retention card taped inside the top drawer",
   "The cabinet anchored to the wall",
  ],
  "art": ("an open filing cabinet drawer showing hanging folders with "
          "tabs all standing in one straight line, a small closed "
          "fireproof box sitting nearby holding permanent documents, a "
          "full shred bag standing by the office door, a retention card "
          "taped inside the drawer, and the cabinet visibly anchored to "
          "the wall with a strap"),
 },
 "Bookshelf and Reference Zone": {
  "id": "HOZ-004", "order": 4, "difficulty": 2,
  "tagline": "A BOOKEND CLOSES EVERY GROUP. A HAND'S WIDTH LEFT OVER.",
  "callouts": [
   "Working reference books at seated eye level",
   "Heavy binders and box files on the bottom two shelves",
   "A bookend closing each group of books",
   "A hand's width of empty shelf at the end of every row",
   "The unit screwed to the wall",
   "No books stacked flat on top of the upright row",
  ],
  "art": ("a bookshelf unit screwed to the wall, working reference books "
          "at seated eye level closed off by a bookend, heavy binders "
          "and box files filling the bottom two shelves, a hand's width "
          "of empty space at the end of each row, and no books stacked "
          "flat on top of the upright rows"),
 },
 "Printer and Scanning Station": {
  "id": "HOZ-005", "order": 5, "difficulty": 2,
  "tagline": "A MIN LINE INSIDE THE BIN. CLEAR AIR BEHIND THE MACHINE.",
  "callouts": [
   "A paper bin directly beneath the printer",
   "A min line and a max line drawn inside the bin",
   "One spare cartridge in a labeled box beside it",
   "A scan tray split into a to-do side and a done side",
   "Clear air behind the machine",
   "Nothing sitting on top of the lid",
  ],
  "art": ("a printer with a paper bin directly beneath it marked with a "
          "min line and a max line, a labelled box holding one spare "
          "cartridge standing beside it, a scan tray divided into a "
          "to-do side and a done side nearby, a gap of clear air behind "
          "the machine, and a completely bare top of the lid"),
 },
 "Supply Cabinet": {
  "id": "HOZ-006", "order": 6, "difficulty": 2,
  "tagline": "ONE OPEN PACK. ONE SPARE BEHIND IT. NOTED ON THE SHELF.",
  "callouts": [
   "One open pack of each consumable at hand height",
   "Backstock standing directly behind the open pack",
   "Reams of paper on the bottom shelf",
   "Min and max noted on a card at the front edge of each shelf",
   "A step stool standing in the corner of the room",
   "Nothing stacked above shoulder height",
  ],
  "art": ("a supply cabinet with one open pack of each consumable "
          "standing at hand height with its backstock directly behind "
          "it, reams of paper stacked on the bottom shelf, a card noting "
          "min and max at the front edge of each shelf, a step stool "
          "standing in the corner of the room, and nothing stored above "
          "shoulder height"),
 },
}

ZONE_ORDER = [n for n, _ in sorted(ZONES.items(), key=lambda kv: kv[1]["order"])]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Titles and art only. The symptom and every branch to a
# root cause are not retyped here: they are read straight off each zone's
# own content.json["diagnosis"]["frictions"], in order, at build time, so
# this list cannot silently diverge from the diagnostic engine already
# shipped on the 114 zone pages. Three per zone, matching that data exactly.
# ---------------------------------------------------------------------------

FRICTION_META = [
 ("Primary Desk", "HOF-001", "CLEAR MONDAY, COVERED BY FRIDAY",
  "a desk surface covered edge to edge with loose papers, a coffee mug "
  "and tangled cables, barely any bare wood visible between them"),
 ("Primary Desk", "HOF-002", "THE NOTE IS SOMEWHERE, LOST AGAIN",
  "a hand searching through loose papers and sticky notes scattered "
  "across a desk, one sticky note peeling and falling off the edge of a "
  "monitor bezel"),
 ("Primary Desk", "HOF-003", "THE CHAIR CATCHES ON SOMETHING AGAIN",
  "an office chair with its caster wheel snagged on a loose power cable "
  "running across the floor beside a cardboard box stored under the "
  "desk"),

 ("Desk Drawers and Pedestal", "HOF-004", "THREE DEAD PENS BEFORE ONE WRITES",
  "a hand testing several pens on a scrap of paper, three dry unwriting "
  "scribbles beside one that has finally made a mark"),
 ("Desk Drawers and Pedestal", "HOF-005", "PULLING THREE FOLDERS TO FIND ONE",
  "a hand pulling several hanging folders partway out of a drawer, "
  "their tabs staggered at different heights making none of them easy "
  "to read at a glance"),
 ("Desk Drawers and Pedestal", "HOF-006", "THE SCISSORS CAUGHT MY HAND AGAIN",
  "a hand reaching blindly into an open desk drawer crowded with loose "
  "pens and paperclips, a pair of scissors lying with its open blade "
  "facing upward among them"),

 ("File Storage", "HOF-007", "FILED SOMEWHERE, FOUND NOWHERE",
  "a hand flipping through a drawer of hanging folders with staggered, "
  "uneven tabs, two folders labeled with a company name rather than a "
  "clear subject"),
 ("File Storage", "HOF-008", "THE TO-BE-FILED PILE KEEPS GROWING",
  "a stack of unsorted paper piled beside a filing cabinet drawer that "
  "is packed too tightly to slide a new folder into"),
 ("File Storage", "HOF-009", "A BANK STATEMENT WENT OUT WITH THE TRASH",
  "a wastebasket beside a desk with a bank statement visible among "
  "ordinary rubbish, no shredder or shred bag anywhere nearby"),

 ("Bookshelf and Reference Zone", "HOF-010",
  "THE SHELF IS FULL BUT THE BOOK ISN'T THERE",
  "a crowded bookshelf with books arranged by height and colour rather "
  "than subject, a hand scanning the spines without finding the one it "
  "is looking for"),
 ("Bookshelf and Reference Zone", "HOF-011",
  "THINGS ARE PILING UP ON TOP OF THE BOOKS",
  "a row of upright books on a shelf with loose folders and binders "
  "stacked flat across the top of them, no bookend or empty space "
  "visible anywhere on the shelf"),
 ("Bookshelf and Reference Zone", "HOF-012",
  "THE SHELF ROCKS WHEN A BOOK COMES OUT",
  "a tall bookshelf leaning slightly away from the wall with no visible "
  "anchor strap, heavy binders loaded on its topmost shelf"),

 ("Printer and Scanning Station", "HOF-013",
  "OUT OF PAPER HALFWAY THROUGH THE JOB",
  "a printer paused mid-print with an empty paper tray, no ream of "
  "backup paper visible anywhere nearby"),
 ("Printer and Scanning Station", "HOF-014",
  "THE SCANNED PILE NEVER GETS SMALLER",
  "a single messy stack of paper sitting beside a scanner with no "
  "visible division between what has been scanned and what has not"),
 ("Printer and Scanning Station", "HOF-015",
  "THE PAPER KEEPS COMING OUT CURLED",
  "a sheet of curled, jammed paper caught halfway out of a printer's "
  "feed tray, a box stored directly on top of the machine's lid"),

 ("Supply Cabinet", "HOF-016", "THREE PACKS OF THE SAME THING, AGAIN",
  "three identical unopened packs of sticky notes standing side by side "
  "on a cluttered shelf, one open pack tucked out of sight behind them"),
 ("Supply Cabinet", "HOF-017", "OUT OF STAPLES WITH NO WARNING AT ALL",
  "an empty stapler beside a bare shelf slot with no backstock and no "
  "card marking a min line anywhere nearby"),
 ("Supply Cabinet", "HOF-018", "REACHING THE TOP SHELF ON A ROLLING CHAIR",
  "a person's foot balanced on the seat of a rolling office chair, "
  "reaching up toward a heavy box on the top shelf of a supply cabinet "
  "with no step stool in sight"),
]


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER, home-office-scened art only. The name, meaning, six_s
# and confirm_in_30_seconds text are not reauthored: they are read straight
# from ops/root_causes.py, the one shared vocabulary the deck, the app and
# the articles all already use, so this deck composes with every other room
# deck rather than forking its own copy (DECK-GAME-DESIGN.md 4.3).
# ---------------------------------------------------------------------------

CAUSE_ART = {
 "KC-001": "a shelf crowded with far more identical pens or notebooks "
           "than one desk could ever use",
 "KC-002": "a loose cable and a notepad lying on a desk with no drawer, "
           "tray or hook anywhere near them",
 "KC-003": "a stack of cardboard boxes stored directly under a desk "
           "where a chair needs to roll",
 "KC-004": "a notebook sitting on a shelf across the room, out of arm's "
           "reach from the desk chair",
 "KC-005": "a row of hanging file folders with tabs staggered at "
           "different heights, one folder's tab hidden behind another",
 "KC-006": "a supply shelf set deep enough that a hand reaching in "
           "cannot see or feel what is at the back",
 "KC-007": "a drawer stuffed so full that a folder springs up the "
           "moment the drawer opens",
 "KC-008": "one drawer holding pens, paper clips and tape all mixed "
           "with no divider between them",
 "KC-009": "an inbox tray stacked well past a dozen sheets, no calendar "
           "or clock nearby marking when it was last cleared",
 "KC-010": "a pair of scissors lying blade-up and loose in an open desk "
           "drawer",
 "KC-011": "an empty box of paper clips sitting back on the shelf where "
           "a full one used to be",
 "RC-013": "an empty printer paper bin standing untouched with nobody "
           "nearby to refill it",
 "RC-015": "a single loose sheet of paper sitting alone on an otherwise "
           "cleared desk corner",
 "RC-016": "a hand reaching behind a printer into a narrow gap tight "
           "against the wall",
}


# ---------------------------------------------------------------------------
# MICRO QUEST LAYER. Three per zone, one physical movement each, grounded
# in that zone's own Manual passes, the same contract every prior room
# generator's MICRO_QUESTS already meets (DECK-GAME-DESIGN.md section 2).
# Printed on the STANDARD card back.
# ---------------------------------------------------------------------------

MICRO_QUESTS = {
 "Primary Desk": [
  "Count the sheets in your inbox tray right now, and if it is more "
  "than a dozen, give the top three a verdict before you stand up.",
  "Peel every sticky note off the monitor bezel and either act on it "
  "now or copy it into the notebook.",
  "Check the power strip is still hooked on the desk leg, and coil any "
  "cable that crosses where the chair rolls.",
 ],
 "Desk Drawers and Pedestal": [
  "Pull three pens from the tray at random and test each on scrap "
  "paper, binning any that skip.",
  "Check the scissors sit point-down in their own slot, not loose among "
  "the pens.",
  "Run your finger along the hanging file tabs and nudge any that sit "
  "out of line back into place.",
 ],
 "File Storage": [
  "Pull one folder and read its label out loud: if it names a company "
  "instead of a question, rename it now.",
  "Check the shred bag by the door; if it is full, carry it out before "
  "you sit back down.",
  "Open the fireproof box and confirm it still closes flush over what "
  "is inside.",
 ],
 "Bookshelf and Reference Zone": [
  "Run your hand along one shelf's end and confirm a hand's width of "
  "empty space is still there.",
  "Pick one book you have not opened in a year and name out loud the "
  "last time you actually used it.",
  "Give the shelf unit a gentle push and confirm it does not rock or "
  "lean away from the wall.",
 ],
 "Printer and Scanning Station": [
  "Check the paper bin against its min line, and add paper to today's "
  "list if it is close.",
  "Move anything sitting on top of the printer lid off it, right now.",
  "Sort the scan tray into its to-do side and its done side before you "
  "leave the room.",
 ],
 "Supply Cabinet": [
  "Count the open packs of one consumable; if more than one is open at "
  "a time, close and shelve the spare.",
  "Check the min and max card on one shelf still matches what is "
  "actually sitting there.",
  "Confirm the step stool is standing in its corner, not a chair being "
  "used in its place.",
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
 {"id": "HOA-001", "zone": "Primary Desk",
  "title": "CLEAR THE DESK AND HOOK THE STRIP UP", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Clear the desk down to the monitor, keyboard and mouse, and "
          "get the power strip off the floor.",
  "why": "Paper with no other place to land is why this desk fills back "
         "up by the end of the week, and a power strip on the floor is "
         "what the chair catches on every time.",
  "inputs": ["nothing beyond fifteen minutes and the inbox tray"],
  "steps": [
   "Take everything off the desk except the monitor, keyboard and "
   "mouse. Put the loose paper into the inbox tray, give every sheet in "
   "it a verdict until it is under a dozen, and hook the power strip up "
   "off the floor.",
   "Set the notebook on your writing-hand side and the phone face down "
   "beyond it.",
   "Check the sweep the mouse travels is left completely bare."],
  "causes": ["KC-002", "KC-009"],
  "victory": "One notebook and one tray under a dozen sheets, and the "
             "chair rolls the width of the desk without catching.",
  "next": "HOS-001",
  "art": "a desk with only the monitor, keyboard and mouse on it, a "
         "notebook and a small inbox tray beside it holding fewer than "
         "a dozen sheets, and a power strip hooked onto the desk leg "
         "clear of the floor"},

 {"id": "HOA-002", "zone": "Primary Desk",
  "title": "PHOTOGRAPH THE CLEARED DESK", "minutes": 30, "players": "1",
  "six_s": "Standardize",
  "goal": "Photograph the cleared desk, tape the print inside the "
          "drawer, and settle the half-finished project sitting in the "
          "corner.",
  "why": "A surface with no photographed standard drifts back to full "
         "by familiarity alone, not volume, and a project you cannot "
         "name a next action for is not stalled, it is abandoned.",
  "inputs": ["a phone or camera", "a printer or tape for the photo",
             "an index card"],
  "steps": [
   "Clear the desk completely and photograph it.",
   "Tape the printed photo inside the top drawer so the word clear "
   "stops being a matter of opinion.",
   "Say the half-finished project's next physical action out loud in "
   "one sentence; if you can name it, write it on a card and clip it "
   "into the inbox tray.",
   "If you cannot name a next action, box the project, mark today's "
   "date on the lid, and put it on the shelf."],
  "causes": ["KC-008", "RC-015"],
  "victory": "A taped photo of the bare desk hangs inside the drawer, "
             "and the half-finished project either carries a named next "
             "action or sits boxed and dated on the shelf.",
  "next": "HOA-001",
  "art": "a photograph of a bare desk taped inside an open desk drawer, "
         "a small labelled box with a dated marking on its lid sitting "
         "on a shelf nearby"},

 {"id": "HOA-003", "zone": "Desk Drawers and Pedestal",
  "title": "TEST THE PENS AND SLOT THE SCISSORS", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Empty the top drawer, test every pen, and give the scissors "
          "a fixed point-down slot.",
  "why": "A drawer you reach into without looking is the wrong place "
         "for a loose blade, and a dead pen that goes back in the "
         "drawer is a decision deferred, not avoided.",
  "inputs": ["scrap paper", "the divided tray"],
  "steps": [
   "Empty the top drawer, test every pen on a scrap and bin the ones "
   "that skip, then put back only what writes into a divided tray with "
   "the scissors point-down in their own slot.",
   "Wipe the tray before anything goes back into it.",
   "Confirm the stapler sits in the tray, not riding on top of any "
   "folder."],
  "causes": ["KC-008", "KC-010"],
  "victory": "Every pen in the drawer writes first time, and the "
             "scissors have a slot of their own.",
  "next": "HOS-002",
  "art": "an open desk drawer with a divided tray holding only pens "
         "that write, a stapler in its own compartment, and scissors "
         "resting point-down in a dedicated slot"},

 {"id": "HOA-004", "zone": "Desk Drawers and Pedestal",
  "title": "EMPTY THE CABLE BAG", "minutes": 30, "players": "1",
  "six_s": "Sort",
  "goal": "Empty the whole bag of loose cables and adapters onto the "
          "desk, name each device, and keep one spare of each connector "
          "you actually use.",
  "why": "A drawer full of cables too cheap to think about and too "
         "specific to throw away only clears when the whole bag is "
         "judged at once, not one cable at a time.",
  "inputs": ["the cable bag", "a labelled small box for the kept "
             "spares", "a bag for electronics recycling"],
  "steps": [
   "Empty the whole cable bag onto the cleared desk in one go.",
   "Pick up each cable and adapter and point at the device it powers, "
   "physically, somewhere in this house.",
   "Anything with no device gets no keep: it goes straight into the "
   "recycling bag.",
   "Coil and band exactly one spare of each connector type you still "
   "use daily, and box the rest for electronics recycling this week."],
  "causes": ["KC-001", "RC-013"],
  "victory": "One labelled box holds exactly one spare of each "
             "connector type still in daily use, and everything else "
             "is boxed for electronics recycling.",
  "next": "HOA-003",
  "art": "a small labelled box holding one coiled spare of each cable "
         "connector type, a bag of surplus adapters set aside for "
         "electronics recycling nearby"},

 {"id": "HOA-005", "zone": "File Storage",
  "title": "RELABEL ONE DRAWER BY THE QUESTION", "minutes": 15,
  "players": "1", "six_s": "Straighten", "from_first_15": True,
  "goal": "Relabel one drawer's folders by the question you would ask, "
          "and line up every tab.",
  "why": "Nobody has ever gone looking for a folder called "
         "Correspondence, and a staggered row of tabs makes your eye "
         "zigzag instead of run straight down the line.",
  "inputs": ["blank tab inserts or a marker", "the shred bag"],
  "steps": [
   "Take one drawer. Relabel each folder with the question you would "
   "ask when looking for it, set every tab in the same position, and "
   "shred the statements you could download again.",
   "Check the drawer closes without pressure once the tabs are "
   "aligned.",
   "Carry anything shredded straight to the bag by the door."],
  "causes": ["KC-008", "KC-005"],
  "victory": "One drawer where the tabs read down in a single line, and "
             "it closes without pressure.",
  "next": "HOS-003",
  "art": "an open filing cabinet drawer with folder tabs relabelled and "
         "standing in a single straight line, the drawer closing easily "
         "with room to spare"},

 {"id": "HOA-006", "zone": "File Storage",
  "title": "SORT INTO KEEP, SCAN, SHRED", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "Work the backlog pile into three piles by rule, and get the "
          "retention card written.",
  "why": "The middle band, neither obviously permanent nor obviously "
         "rubbish, is why this job stalls; a rule applied once settles "
         "the whole pile instead of one sheet at a time.",
  "inputs": ["the shred bag", "a scanner if you keep digital copies",
             "an index card for the retention rule"],
  "steps": [
   "Work one drawer at a time into three piles: keep as paper, scan "
   "then shred, shred now.",
   "Move permanent originals into a closed fireproof box, never the "
   "filing cabinet.",
   "Write your retention rule on a card and tape it inside the top "
   "drawer.",
   "Carry the finished shred pile straight to the bag by the door."],
  "causes": ["KC-004", "KC-007"],
  "victory": "Every sheet from the drawer sits in one of three piles, "
             "permanent originals are in the fireproof box, and the "
             "retention card is taped inside the drawer.",
  "next": "HOA-005",
  "art": "three piles of paper on a desk marked by role, keep, scan, "
         "and shred, a small fireproof box standing to one side and a "
         "retention card visible taped inside an open drawer"},

 {"id": "HOA-007", "zone": "Bookshelf and Reference Zone",
  "title": "MOVE THE WEIGHT DOWN AND ANCHOR THE SHELF", "minutes": 15,
  "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Move the heaviest binders down, bring real reference to eye "
          "level, and confirm the wall fixing.",
  "why": "An unanchored shelf loaded heavy at the top is a fall risk "
         "the moment you pull the wrong book, and reference you cannot "
         "reach without standing is reference you stop using.",
  "inputs": ["a wall anchor kit if none is fitted", "a step stool"],
  "steps": [
   "Move every heavy binder to the bottom two shelves, bring the "
   "reference you actually open to seated eye level, then check the "
   "wall fixing and fit one if it is missing.",
   "Close each group with a bookend.",
   "Confirm a hand's width of empty shelf remains at the end of every "
   "row."],
  "causes": ["KC-003", "KC-010"],
  "victory": "The heaviest things are lowest, the unit does not move "
             "when you pull a book, and every row ends in a hand's "
             "width of space.",
  "next": "HOS-004",
  "art": "a bookshelf with heavy binders moved to the bottom two "
         "shelves, working reference books at seated eye level closed "
         "off with a bookend, and a visible wall anchor strap securing "
         "the top of the unit"},

 {"id": "HOA-008", "zone": "Bookshelf and Reference Zone",
  "title": "THIN ONE GROUP BY THE LAST-TAKEN-DOWN TEST", "minutes": 30,
  "players": "1", "six_s": "Sort",
  "goal": "For one group of books, name the last time each was taken "
          "down, and remove anything that fails the test.",
  "why": "A book that stands for who you used to be is the hardest to "
         "release, and the shelf only stays a working shelf if "
         "reference wins its place in open competition with everything "
         "else on it.",
  "inputs": ["a box for books leaving the house",
             "nothing else beyond thirty minutes"],
  "steps": [
   "Pick one group of books on the shelf.",
   "For each one, name out loud a specific occasion you last took it "
   "down; if you cannot, it is display, not reference.",
   "Box anything that fails the test for donation or resale.",
   "Confirm a hand's width of empty shelf remains once the group is "
   "thinned."],
  "causes": ["KC-001", "KC-009"],
  "victory": "Every book in the group has a named reason for staying, "
             "and a hand's width of shelf is free at the end of the "
             "row.",
  "next": "HOA-007",
  "art": "a bookshelf group with several books removed and boxed for "
         "donation, the remaining books standing with clear space at "
         "the end of the row"},

 {"id": "HOA-009", "zone": "Printer and Scanning Station",
  "title": "DRAW THE MIN LINE AND CLEAR THE VENTS", "minutes": 15,
  "players": "1", "six_s": "Safety", "from_first_15": True,
  "goal": "Clear the space around the printer and mark a min and max "
          "line on the paper bin.",
  "why": "A printer with no clear air behind it and no visible paper "
         "level is how this room runs out mid-job and overheats at the "
         "same time.",
  "inputs": ["a marker", "nothing else beyond fifteen minutes"],
  "steps": [
   "Clear the top of and the space behind the printer, draw a min line "
   "and a max line on the paper bin, and split the scan tray into a "
   "to-do side and a done side.",
   "Move anything sitting on top of the lid off it for good.",
   "Confirm the printer plugs straight into a wall outlet, not a strip "
   "chained off another strip."],
  "causes": ["KC-011", "KC-002"],
  "victory": "Air behind the machine, a paper level anyone can read at "
             "a glance, and a scan tray that says what still needs "
             "doing.",
  "next": "HOS-005",
  "art": "a printer with a paper bin marked with a min line and a max "
         "line beneath it, clear space visible behind the machine, and "
         "a scan tray split into a to-do side and a done side"},

 {"id": "HOA-010", "zone": "Printer and Scanning Station",
  "title": "SETTLE THE BACKUP PRINTER AND MATCH THE CARTRIDGES",
  "minutes": 30, "players": "1", "six_s": "Sort",
  "goal": "Test the spare printer for real, decide backup or recycle, "
          "and match every cartridge box to the machine you actually "
          "use.",
  "why": "An unplugged spare printer is a large object you have not "
         "decided about, not a backup, and an unmatched cartridge only "
         "loses value the longer it sits.",
  "inputs": ["the spare printer", "its power cable",
             "a marker to note the model on kept cartridge boxes"],
  "steps": [
   "Plug in the spare printer and print a test page right now.",
   "If it prints and you will stock a spare cartridge for it, give it "
   "a real home; if not, box it for electronics recycling this week.",
   "Hold every sealed cartridge box against the model number on the "
   "machine you actually use.",
   "Sell or recycle any cartridge that does not match."],
  "causes": ["RC-013", "KC-003"],
  "victory": "The spare printer either has a real home with a named "
             "spare cartridge or is boxed for recycling, and every "
             "kept cartridge matches the machine on the desk.",
  "next": "HOA-009",
  "art": "a spare printer either freshly settled onto a shelf with a "
         "printed test page beside it or boxed for recycling, a small "
         "stack of cartridge boxes matched against a printer's visible "
         "model number"},

 {"id": "HOA-011", "zone": "Supply Cabinet",
  "title": "CONSOLIDATE TO ONE OPEN PACK EACH", "minutes": 15,
  "players": "1", "six_s": "Sort", "from_first_15": True,
  "goal": "Bring every consumable together and consolidate to one open "
          "pack of each at hand height.",
  "why": "A dozen packs of sticky notes look like nothing until they "
         "stand side by side, and backstock nobody can see is "
         "backstock that gets bought again.",
  "inputs": ["a card and marker for the min/max note"],
  "steps": [
   "Bring every consumable together, move reams to the bottom shelf, "
   "put one open pack of each at hand height with its backstock "
   "directly behind, and write min and max on a card inside the door.",
   "Line up the true count of each item where you can see it before "
   "deciding what stays.",
   "Recycle dried glue sticks, dead markers and cracked folders now."],
  "causes": ["KC-005", "KC-008"],
  "victory": "One open pack of each thing visible at hand height, "
             "nothing heavy above your shoulder, and a card that says "
             "when to buy.",
  "next": "HOS-006",
  "art": "a supply cabinet shelf with one open pack of each consumable "
         "at hand height, its backstock lined up directly behind it, "
         "and a card marked with min and max lines taped inside the "
         "door"},

 {"id": "HOA-012", "zone": "Supply Cabinet",
  "title": "MOVE THE WEIGHT DOWN AND BRING IN THE STOOL", "minutes": 30,
  "players": "1", "six_s": "Safety",
  "goal": "Move reams and heavy boxes below shoulder height, and put a "
          "real step stool in this room.",
  "why": "A rolling chair is not a ladder, and a slipping box from a "
         "shoulder-height shelf lands on your head while your arms are "
         "already up.",
  "inputs": ["a step stool", "nothing else beyond thirty minutes"],
  "steps": [
   "Move every ream of paper and heavy box down to the bottom shelf.",
   "Bring an actual step stool into this room and leave it standing in "
   "the corner.",
   "Confirm nothing heavier than light supplies sits above shoulder "
   "height.",
   "Check the deepest shelf for anything lost at the back now that "
   "reach is easier."],
  "causes": ["KC-010", "KC-006"],
  "victory": "A step stool stands in the corner, and nothing heavier "
             "than light supplies sits above shoulder height.",
  "next": "HOA-011",
  "art": "a step stool standing in the corner of a supply room, heavy "
         "reams of paper stacked on the bottom shelf, and only light "
         "supplies visible above shoulder height"},

 {"id": "HOA-013", "zone": None,
  "title": "FOLLOW ONE PIECE OF PAPER FROM DOOR TO DRAWER",
  "minutes": 30, "players": "1", "six_s": "Straighten",
  "goal": "Pick one real piece of paper that arrived today and walk it "
          "through every decision point in this room until it lands in "
          "a folder or the bin.",
  "why": "This room's whole job is unmade decisions about paper living "
         "in one drawer, and no single zone can be judged in isolation "
         "from the others it feeds.",
  "inputs": ["one real piece of paper that arrived today"],
  "steps": [
   "Pick up the newest piece of paper that arrived in this room today.",
   "Give it a verdict at the desk: act, file, or recycle, the same test "
   "the inbox tray uses.",
   "If it needs filing, carry it straight to the cabinet and give it a "
   "folder named for the question you would ask.",
   "If a step along the way stalled, note which zone stalled it: that "
   "zone is today's real job, not this one."],
  "causes": ["RC-015", "KC-009"],
  "victory": "The one piece of paper reaches a folder or the bin, and "
             "you can name which zone, if any, slowed it down.",
  "next": "HOA-014",
  "art": "a single sheet of paper being carried from a desk inbox tray "
         "directly to a labelled folder in an open filing cabinet "
         "drawer, no other paper visible along the way"},

 {"id": "HOA-014", "zone": None, "title": "THE HOLDING PEN SWEEP",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Walk the whole room and carry out anything that is not "
          "actually office work.",
  "why": "This is the room with a door that closes, so it quietly "
         "becomes the household's holding pen, and anything that is "
         "not office work becomes permanent furniture if it stays past "
         "today.",
  "inputs": ["nothing beyond fifteen minutes and somewhere else in the "
             "house to carry things to"],
  "steps": [
   "Walk every surface and the floor, and name each object: office "
   "work, or not.",
   "Carry anything that is not office work to the room it actually "
   "belongs in, right now.",
   "If nothing else in the house claims it, box it for donation rather "
   "than setting it back down here."],
  "causes": ["KC-001", "KC-003"],
  "victory": "Every object left in the room is genuinely office work.",
  "next": "HOA-015",
  "art": "a home office with a broken lamp, an unopened moving box and "
         "a bag of miscellaneous items being carried out through the "
         "open door, the room behind them holding only office "
         "furniture"},

 {"id": "HOA-015", "zone": None,
  "title": "THE QUARTERLY REACH-BEHIND CLEAN AND SAFETY WALK",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Clean the spots this room hides behind its furniture, and "
          "walk it once checking for the four things that hurt people "
          "here.",
  "why": "Dust settles behind the printer and the bookshelf where "
         "nobody looks, and water, electricity, a fall and a tipping "
         "cabinet are the four risks in this room that only show up if "
         "you look on purpose.",
  "inputs": ["nothing beyond thirty minutes and a working set of "
             "hands"],
  "steps": [
   "Ease the printer, the bookshelf and the filing cabinet out or reach "
   "behind each with the crevice tool, and clear the dust and any stray "
   "paper.",
   "Check every charger cable and the power strip for a frayed lead or "
   "a cable crossing where the chair rolls.",
   "Check the filing cabinet and bookshelf are both anchored, and that "
   "nothing heavy sits above head height on either.",
   "Check the scissors and letter opener sit point-down in their own "
   "slot, and that the printer has clear air behind it.",
   "Fix anything you find right there, or write it on a card in the "
   "inbox tray if it needs a tool you do not have to hand."],
  "causes": ["RC-016", "KC-010"],
  "victory": "You can name, out loud, that behind the printer, behind "
             "the bookshelf, the cables, the cabinets and the sharp "
             "tools have each been checked today.",
  "next": "HOA-001",
  "art": "a hand reaching behind a printer with a crevice tool "
         "attachment, a filing cabinet visibly anchored to the wall "
         "further along the same room, a charger cable being checked "
         "near a power strip"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six ordinary hard days that test a home office, one per
# zone.
# ---------------------------------------------------------------------------

EVENTS = [
 ("HOE-001", "THE DEADLINE ALL-NIGHTER",
  "A deadline lands and you need the desk and every drawer tool ready "
  "for six straight hours of work, starting now.",
  ["HOZ-001", "HOZ-002"],
  "The desk is already clear enough to spread out on, and the first pen "
  "you grab writes.",
  "If you had to clear clutter or hunt for a working pen before you "
  "could start, the everyday reset was not being kept. Draw HOA-001 or "
  "HOA-003.",
  "a desk cleared and ready for a long work session, a pen resting on "
  "an open notebook beside a keyboard, a lamp lit against a darkening "
  "window"),
 ("HOE-002", "THE TAX SEASON ENVELOPE",
  "This year's tax documents arrive in the post and need a folder, a "
  "shred decision, and a place in the cabinet the same afternoon.",
  ["HOZ-003"],
  "The new folder slots straight in at the front of this year's tabs, "
  "and the oldest year past your retention period comes out to be "
  "shredded the same day.",
  "If the drawer would not close for the new folder, the retention "
  "pass has not been run. Draw HOA-005 or HOA-006.",
  "a new folder of tax documents being slotted into a filing cabinet "
  "drawer with clearly labelled tabs, an older folder pulled out beside "
  "a shred bag"),
 ("HOE-003", "THE SCHOOL PROJECT RESEARCH NIGHT",
  "A child needs three reference books from the shelf for a project "
  "due tomorrow, and needs to find them without help.",
  ["HOZ-004"],
  "The right books sit at an eye level a child can actually reach and "
  "read the spines of, grouped by subject.",
  "If a book had to be hunted for on a stool or was not there at all, "
  "the shelf is not grouped by why it gets used. Draw HOA-007 or "
  "HOA-008.",
  "a child's hand pulling a reference book from a shelf at their own "
  "eye level, the spines around it clearly grouped by subject"),
 ("HOE-004", "THE LAST-MINUTE PRINTING RUN",
  "Fifty pages need to print and scan back in within the hour, right "
  "before you have to leave the house.",
  ["HOZ-005"],
  "The paper bin has enough stock to finish the job, and the finished "
  "scans land on the done side of the tray without a pause to sort "
  "them.",
  "If you ran out of paper mid-job or the scan tray had no clear done "
  "side, the everyday reset was not being kept. Draw HOA-009.",
  "a printer running continuously with a full paper bin beneath it, a "
  "stack of finished scans sitting on the clearly marked done side of a "
  "nearby tray"),
 ("HOE-005", "THE OFFICE SUPPLY RUN YOU ALMOST SKIPPED",
  "You are about to leave for the shop and need to know, in ten "
  "seconds, exactly what this room is actually low on.",
  ["HOZ-006"],
  "The min and max cards on the shelf edges answer the question "
  "without opening a single box.",
  "If you had to open boxes to find out what was low, the cards were "
  "not being kept current. Draw HOA-011.",
  "a hand scanning a supply cabinet shelf edge where cards marked with "
  "min and max lines are clearly visible, no box needing to be opened"),
 ("HOE-006", "THE DOOR-CLOSES-ON-IT WEEKEND",
  "Nobody has been in this room in two weeks because the door stayed "
  "shut, and a guest is coming through the house this weekend.",
  ["HOZ-001", "HOZ-006"],
  "Nothing that is not office work has collected in the room, and the "
  "desk is still in its photographed state.",
  "If a holding-pen item had crept in, or the desk had drifted from "
  "its photo, the room's own trap caught you. Draw HOA-014 or HOA-002.",
  "a home office door standing open onto a tidy room with nothing but "
  "office furniture and supplies visible, a cleared desk matching a "
  "small taped photo inside its drawer"),
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
        "related": {"standard": f"HOS-{spec['order']:03d}",
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
        "instruction": "Pick the answer that is true in your home "
                       "office, then turn to that root cause card. If "
                       "two are true, take the one you could change "
                       "this week.",
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
    standard_id = (f"HOS-{ZONES[a['zone']]['order']:03d}"
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
        "id": f"HOS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "id": "HOR-001", "title": "THE HOME OFFICE", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SIX ZONES. START WITH THE DESK.",
        "objective": "The home office is six small jobs built around "
                     "one shared trap: physical clutter and unmade "
                     "decisions about paper. This card is the map and "
                     "the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": (
            f"HOZ-001 Primary Desk. {start_tip['text']}" if start_tip
            else "HOZ-001 Primary Desk. Every other zone in this room "
                 "gets emptied onto that surface at some point."),
        "how_to_play": [
            "1. Deal the six ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to "
            "start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones "
            "that are true in your home office. Put the rest back.",
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
        "players": "1 to 6. With more than one, split the chain: one "
                   "clears the desk and drawers, another works the "
                   "filing and the shelf.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do HOA-015 The Quarterly Reach-Behind Clean and "
                        "Safety Walk before any rebuild. It takes thirty "
                        "minutes and covers the cables, the cabinets, "
                        "the shelves and the printer.",
        "related": {"contents": "HOZ-001 to HOZ-006, HOF-001 to "
                                 "HOF-018, the shared root causes in "
                                 "ops/root_causes.py, HOA-001 to "
                                 "HOA-015, HOS-001 to HOS-006, HOE-001 "
                                 "to HOE-006"},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole tidy "
                           "home office in its settled state, a cleared "
                           "desk, a filing cabinet, a bookshelf, a "
                           "printer station and a supply cabinet all "
                           "visible in one frame, everything put away",
                "must_show": ["all six zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where "
                               "each of the six zones is. If two are "
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
    return {"deck": "home-office", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these mirrors a real defect class found on this
    project's other card generators (build_kitchen_deck.py,
    build_entryway_deck.py, build_laundry_room_deck.py)."""
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

    assert any(c["id"] == "HOA-015" for c in cards), "no safety walk card"
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
    print(f"  deck        home-office ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting "
          f"lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
