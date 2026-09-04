#!/usr/bin/env python3
"""
Build the Kitchen deck: 72 cards, generated, never hand-copied.

WHY A GENERATOR AND NOT A HAND-WRITTEN JSON
-------------------------------------------
The Entryway deck's card text was transcribed back off finished cards, so its
twelve micro zones disagree with the Manual's five Entryway zones. A household
that owns the free deck and the $19 print pack is taught two different zone
lists for the same room, and neither file knows the other exists.

Everything derivable here is derived from content/manual/source/content.json,
the same file the book, the zone pages, the Home Quest and the print pack are
built from. Purpose, what done looks like, the standard, the trigger and the
safety checks are quoted from it, not rewritten, and a gate at the bottom
asserts they are still character-for-character identical. If the Manual
changes, this deck changes with it, and the drift cannot happen quietly.

The layers that are NOT in the Manual are hand authored below and marked:
the friction cards (what a household says out loud), the root cause cards,
the timed action cards, and the event cards. Those are the diagnostic engine,
and they are the reason this is a deck rather than the print pack reprinted.

WHAT THIS DOES NOT DO
---------------------
It does not render cards and it does not draw anything. It writes card copy
and, for each card, the art record the prompt builder turns into a generation
prompt. Rendering belongs to ops/build_card_template.py and ops/render_cards.py,
which this file does not touch.

Run:  python ops/cardtext/build_kitchen_deck.py
Out:  ops/cardtext/kitchen-deck.json
"""
from __future__ import annotations

import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(HERE, "kitchen-deck.json")

ROOM = "Kitchen"

# The card budget is a real constraint, not a round number. Print on demand
# card decks price in 18 card steps, so 72 is a tier and 75 is 90 with fifteen
# blanks paid for. Print at home, nine to a US Letter sheet, 72 is exactly
# eight sheets of fronts and eight of backs. Both economics land on 72, so the
# budget is fixed first and the content is cut to fit it, which is the
# opposite of how the 89 card Entryway deck happened.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 7, "FRICTION CARD": 21,
          "ROOT CAUSE CARD": 12, "ACTION CARD": 18, "STANDARD CARD": 7,
          "EVENT CARD": 6}
TOTAL = 72

# Proposed for ops/build_card_template.py's TYPE_COLOUR, which this file does
# not edit. Same palette family as the Entryway deck so a mixed pile still
# reads as one product line.
TYPE_COLOUR = {
    "ROOM CARD": "#2B2622", "ZONE CARD": "#2F5233",
    "FRICTION CARD": "#BC4B2A", "ROOT CAUSE CARD": "#6E5B8B",
    "ACTION CARD": "#3C5A6B", "STANDARD CARD": "#4E7A57",
    "EVENT CARD": "#8C5A2B",
}


# ---------------------------------------------------------------------------
# ZONE LAYER. Callouts are "done_looks_like" broken into six countable things,
# because the callout list is also the art specification: every numbered item
# has to be a visible object in the hero, and the art is rejected if you
# cannot count them. That test is new. The Entryway deck did not have it, and
# EM-003 Key Station shipped with six callouts over a photograph containing no
# keys, no hooks, no tray and no mail slot.
# ---------------------------------------------------------------------------

ZONES = {
 "Primary Prep Counter": {
  "id": "KZ-001", "order": 1, "difficulty": 3,
  "tagline": "ONE CLEAR RUN. THE REST GOES SOMEWHERE ELSE.",
  "callouts": [
   "Clear run, at least as wide as your largest cutting board",
   "The cutting board, down on bare counter",
   "Knife block or wall strip, on your dominant side",
   "Salt within one reach",
   "Kettle and toaster back against the wall, cords coiled",
   "Nothing parked: no mail, no fruit bowl, no charging phone",
  ],
  "art": ("a clear run of pale stone kitchen counter with one plain wooden "
          "cutting board lying flat, a wooden knife block holding four knives "
          "to the right of it, a small ceramic salt pot beside the board, and "
          "a kettle and a two slice toaster standing back against the "
          "backsplash with their cords coiled behind them"),
 },
 "Cooking Zone": {
  "id": "KZ-002", "order": 2, "difficulty": 3,
  "tagline": "HANDS BUSY, HEAT ON. EVERYTHING WITHIN ONE REACH.",
  "callouts": [
   "Oil, salt and pepper within one reach of the burners",
   "Utensil crock holding six tools, no more",
   "Pot holders on a hook you find without looking",
   "Weekly spices at the front of the rack",
   "Clear landing space beside the hob, wide enough for a hot pan",
   "Pan handles turned in, never over the front edge",
  ],
  "art": ("a four burner hob with one steel frying pan on it, its handle "
          "turned inward over the hob rather than out over the counter edge, "
          "a stoneware crock beside it holding five wooden and steel cooking "
          "tools, a bottle of oil and a pepper mill within arm's reach, two "
          "quilted pot holders hanging on a small hook on the wall, a spice "
          "rack with its front row standing proud, and an empty stretch of "
          "counter to the right of the hob"),
 },
 "Sink and Dishwashing Zone": {
  "id": "KZ-003", "order": 3, "difficulty": 2,
  "tagline": "THE WHOLE KITCHEN RESETS FROM HERE.",
  "callouts": [
   "Empty sink, dry basin",
   "Drain flange wiped",
   "One brush and one sponge standing where they drain",
   "Drying rack empty, or holding only what is still wet",
   "Under the sink: one tray, dish soap, tablets, one cleaner",
   "Pipes visible around the tray",
  ],
  "art": ("an empty stainless steel kitchen sink with a dry basin and a "
          "clean drain flange, a small slotted caddy at the back of it "
          "holding one dish brush and one sponge standing upright, an empty "
          "wire drying rack on the drainer, and below, the open cabinet "
          "beneath showing a single shallow plastic tray holding three plain "
          "unlabelled bottles with the bare white pipework fully visible "
          "around it"),
 },
 "Upper Cabinet Zone": {
  "id": "KZ-004", "order": 4, "difficulty": 2,
  "tagline": "DAILY THINGS AT DAILY HEIGHT.",
  "callouts": [
   "Everything daily between shoulder and eye height",
   "One category per stack",
   "No plate stack more than about six high",
   "Every mug lifts out without moving another mug",
   "Top shelf: only what you use less than monthly",
   "The platter for eight lives up there",
  ],
  "art": ("an open upper kitchen cabinet with two shelves in view, a stack "
          "of six plain white plates, a separate stack of four bowls beside "
          "it, a row of five mugs each standing clear of the next with space "
          "around them, and on the shelf above a single large oval serving "
          "platter stored on its edge"),
 },
 "Lower Cabinet and Cookware Zone": {
  "id": "KZ-005", "order": 5, "difficulty": 4,
  "tagline": "OUT IN ONE MOTION. BACK IN ONE MOTION.",
  "callouts": [
   "Every pan comes out and goes back in one motion",
   "Stacks capped at three, or pans on edge in a divider",
   "Lids in a rack or on a door rail, never loose",
   "Baking sheets standing on end",
   "The two nightly pans at the front, nearest the hob",
   "Heaviest pieces on the cabinet floor",
  ],
  "art": ("an open lower kitchen cabinet seen straight on, a wire divider on "
          "the left holding three baking sheets standing on end, two steel "
          "frying pans nested at the front within easy reach, a wire lid rack "
          "holding four pan lids upright on edge, and one heavy black cast "
          "iron pot sitting directly on the cabinet floor"),
 },
 "Utensil and Utility Drawers": {
  "id": "KZ-006", "order": 6, "difficulty": 2,
  "tagline": "ONE DRAWER. ONE JOB.",
  "callouts": [
   "Each drawer has one job",
   "Its name written inside its front edge",
   "Flatware in a divided insert, nothing loose beside it",
   "Foil, film and baking paper standing on end",
   "Blades sheathed, never loose among the spatulas",
   "Every drawer closes flush with one push",
  ],
  "art": ("two shallow kitchen drawers pulled open and seen from above, the "
          "upper one holding a divided wooden flatware insert with forks, "
          "knives and spoons in their own compartments and nothing loose, the "
          "lower one holding three plain unmarked boxes of foil and wrap "
          "standing upright on end in a divider beside a paring knife in a "
          "plain plastic blade sleeve"),
 },
 "Refrigerator and Freezer": {
  "id": "KZ-007", "order": 7, "difficulty": 4,
  "tagline": "SEE WHAT YOU OWN BEFORE YOU SHOP.",
  "callouts": [
   "Raw meat sealed, on the lowest shelf",
   "Leftovers in clear containers at eye level",
   "A blank label on every lid, for a name and a date",
   "One eat-first bin where the door opens onto it",
   "Rear vents clear, nothing pressed against them",
   "The door holds condiments only",
  ],
  "art": ("an open refrigerator seen straight on, a row of clear lidded "
          "containers on the middle shelf each wearing a small blank white "
          "label with no writing on it, a shallow open bin at the front edge "
          "of that shelf, a sealed vacuum pack of raw meat lying on the "
          "lowest shelf, the plain rear wall of the fridge clear and visible "
          "with nothing pushed against it, and the door shelves holding only "
          "condiment bottles"),
 },
}


# ---------------------------------------------------------------------------
# ROOT CAUSE LAYER. Twelve of the twenty one causes in the product model: the
# twelve that actually occur in a kitchen. Each says how to confirm it in
# thirty seconds while standing there, because a diagnosis you cannot check is
# a guess wearing a label.
# ---------------------------------------------------------------------------

CAUSES = [
 ("KC-001", "EXCESS", "Sort",
  "More things here than the job needs.",
  "Count what you used in the past month. If the honest number is a third of "
  "what is stored here, the space is not too small.",
  "a kitchen counter holding three nearly identical wooden spoons, two "
  "peelers and two can openers laid side by side on bare stone"),
 ("KC-002", "NO ASSIGNED HOME", "Straighten",
  "The thing has no defined destination, so it lands wherever the hand opens.",
  "Ask where one specific item lives. If two people answer differently, or "
  "nobody answers, it has no home.",
  "a kitchen counter with a set of keys, a stack of unopened post, a school "
  "folder and a charger cable lying where they were set down"),
 ("KC-003", "WRONG LOCATION", "Straighten",
  "It is stored somewhere. Just not where it is used.",
  "Stand where you use it and count the steps to where it is kept. More than "
  "two is the wrong cabinet.",
  "a kitchen with a large cooking pan stored in an open cabinet on the far "
  "wall, the hob visible in the distance across an empty floor"),
 ("KC-004", "EXCESS MOTION", "Straighten",
  "Getting it out means bending, lifting, unstacking, or moving something "
  "else first.",
  "Fetch it once and count the movements. More than two and the storage is "
  "charging you rent every time you cook.",
  "an open cabinet with a stack of five mixing bowls, the top three lifted "
  "out and set on the counter beside it to reach the one underneath"),
 ("KC-005", "POOR VISIBILITY", "Straighten",
  "You own it, but you cannot see it, so you buy it again or forget it.",
  "Open the door and, without moving anything, name what is at the back. If "
  "you cannot, that stock is invisible and you are paying for it twice.",
  "a deep kitchen shelf photographed straight on, the front row of jars "
  "hiding a second row behind it in shadow"),
 ("KC-006", "POOR ACCESSIBILITY", "Safety",
  "The people who use it cannot reach it safely, or at all.",
  "Have the shortest person who uses this kitchen fetch the everyday plates. "
  "If they climb, reach overhead, or ask for help, the height is wrong.",
  "a stack of everyday plates on a high shelf above head height with a "
  "kitchen chair pulled up beneath it"),
 ("KC-007", "INSUFFICIENT CAPACITY", "Sort",
  "The right storage exists and genuinely cannot hold what belongs in it.",
  "Put back only what belongs here. If it still will not close, or still "
  "stacks four deep, the capacity is the problem and not the habit.",
  "a kitchen drawer pushed shut on a spatula handle so it stands a finger's "
  "width open"),
 ("KC-008", "MISSING STANDARD", "Standardize",
  "Nobody agreed what good looks like, so everybody is right.",
  "Ask two people what this surface should look like at bedtime. Two answers "
  "means there is no standard to keep.",
  "a kitchen counter at dusk, half of it wiped and clear, the other half "
  "still holding the day's cooking things"),
 ("KC-009", "MISSING TRIGGER", "Sustain",
  "The reset is a good intention with nothing to attach it to.",
  "Name the moment it happens. If the answer is when I get round to it, "
  "there is no trigger and it will not survive a bad week.",
  "a kitchen at night lit only by the small light of a running dishwasher, "
  "the counter beside it still loaded"),
 ("KC-010", "SAFETY CONSTRAINT", "Safety",
  "The current arrangement can hurt somebody, and that outranks tidy.",
  "Look for the four: a blade your hand would meet, weight above shoulder "
  "height, heat beside something that burns, and raw food above ready to eat "
  "food.",
  "an uncovered paring knife lying loose among spatulas in an open kitchen "
  "drawer"),
 ("KC-011", "POOR REPLENISHMENT", "Standardize",
  "Consumables run out unnoticed, and food ages out of use unseen.",
  "Find the last one of something you use daily. If nothing tells you it is "
  "the last one, you will find out at the worst possible moment.",
  "an empty dishwasher tablet box standing on an otherwise clear counter "
  "beside a full sink"),
 ("KC-012", "CONFLICTING USERS", "Standardize",
  "Two people run one zone by two designs, so it is permanently half of each.",
  "Load the dishwasher together, once. The argument that starts is the "
  "conflict, and it is a design problem, not a character problem.",
  "an open dishwasher with the lower basket loaded in neat rows on one side "
  "and stacked at random on the other"),
]


# ---------------------------------------------------------------------------
# FRICTION LAYER. Three per zone, written the way a household says it out loud
# rather than in method language. The back of the card is the branch: why does
# this happen here, three plausible answers, each routing to a root cause.
# This is the diagnostic engine, and it is what the print pack does not have.
# ---------------------------------------------------------------------------

FRICTIONS = [
 ("Primary Prep Counter", "KF-001", "THE COUNTER IS NEVER CLEAR",
  "I wipe it on Sunday and by Tuesday it is gone again.",
  [("Things get set down here on the way past", "KC-002"),
   ("There is more kitchen here than the counter can hold", "KC-001"),
   ("Nobody ever agreed what is allowed to live on it", "KC-008")],
  "a kitchen counter carrying a fruit bowl, a stack of post, two small "
  "appliances and a folded tea towel, with only a hand's width of bare "
  "surface left at the front"),
 ("Primary Prep Counter", "KF-002", "I COOK ON A CHOPPING BOARD OF SPACE",
  "There is a metre of counter and I use twenty centimetres of it.",
  [("The appliances came out for one job and never went back", "KC-001"),
   ("The board's spot is taken, so it sits wherever it fits", "KC-003"),
   ("There is nowhere to set a bowl down while I work", "KC-007")],
  "a small cutting board wedged into a narrow gap of counter between a bread "
  "bin, a kettle and a knife block"),
 ("Primary Prep Counter", "KF-003", "MAIL AND HOMEWORK LAND HERE",
  "It is the first flat surface anyone meets, so it takes everything.",
  [("None of it has anywhere else to go", "KC-002"),
   ("The real drop zone is in another room", "KC-003"),
   ("Nothing ever moves it back", "KC-009")],
  "the end of a kitchen counter holding a leaning stack of envelopes, a "
  "school exercise book and a set of car keys"),

 ("Cooking Zone", "KF-004", "I HUNT FOR THE TURNER WITH THE PAN HOT",
  "The oil is smoking and I am opening the third drawer.",
  [("The crock holds twenty tools and I use six", "KC-001"),
   ("The tool I need lives on the other side of the kitchen", "KC-003"),
   ("The drawer is a jumble and nothing shows", "KC-005")],
  "a crowded utensil crock beside a hob holding more than a dozen tools "
  "packed tight, a pan heating on the burner behind it"),
 ("Cooking Zone", "KF-005", "NOWHERE TO PUT A HOT PAN DOWN",
  "I stand holding it, looking round my own kitchen, arm aching.",
  [("The landing space has slowly filled with other things", "KC-007"),
   ("Those things have no home of their own", "KC-002"),
   ("Nobody calls that space anything, so it is fair game", "KC-008")],
  "the counter beside a hob covered with a chopping board, a jar, an open "
  "cookbook and a mug, leaving no clear surface"),
 ("Cooking Zone", "KF-006", "I BUY SPICES I ALREADY OWN",
  "Three jars of cumin, and I bought two of them this year.",
  [("The front row hides the back row completely", "KC-005"),
   ("Nothing tells me what is nearly gone", "KC-011"),
   ("There are more jars here than the rack was built for", "KC-001")],
  "a two row spice rack seen straight on, the back row lost behind the "
  "front, several small jars crowded in at one end"),

 ("Sink and Dishwashing Zone", "KF-007", "THE SINK IS FULL AGAIN BY EVENING",
  "Empty at eight in the morning, a mountain at six.",
  [("There is no moment in the day when it gets cleared", "KC-009"),
   ("Dishes have nowhere to go until the dishwasher is emptied", "KC-004"),
   ("Two of us run this sink two different ways", "KC-012")],
  "a kitchen sink holding a day's worth of plates, pans and mugs stacked "
  "above the rim"),
 ("Sink and Dishwashing Zone", "KF-008", "UNDER THE SINK IS A CHEMICAL JUMBLE",
  "I move four bottles to find the one I want, and I could not tell you what "
  "half of them are.",
  [("Bleach and an acidic cleaner are standing side by side", "KC-010"),
   ("Nothing under here has a defined place", "KC-002"),
   ("We have bought the same cleaner three times", "KC-001")],
  "an open under sink cabinet crowded with plain bottles and cloths leaning "
  "against each other, the pipework hidden behind them"),
 ("Sink and Dishwashing Zone", "KF-009", "THE SPONGE SMELLS",
  "It is always wet, and it never seems to be a new one.",
  [("It lies flat in a puddle instead of standing to drain", "KC-003"),
   ("Nothing says when it gets replaced", "KC-011"),
   ("Nobody agreed what this sink looks like at the end of a day", "KC-008")],
  "a flattened kitchen sponge lying in a shallow pool of water on the corner "
  "of a sink surround"),

 ("Upper Cabinet Zone", "KF-010", "I MOVE THREE MUGS TO GET ONE",
  "Every morning, before coffee, in the half dark.",
  [("There are more mugs here than anyone drinks from", "KC-001"),
   ("They are stacked because there is no width to stand them", "KC-007"),
   ("Getting one out costs three movements", "KC-004")],
  "an open cabinet shelf packed with mugs nested and stacked two deep so "
  "none can be lifted clear"),
 ("Upper Cabinet Zone", "KF-011", "I STAND ON A CHAIR FOR THE EVERYDAY PLATES",
  "Or I ask somebody taller, which is worse.",
  [("Daily things are stored above daily reach", "KC-006"),
   ("The reachable shelf is full of things used twice a year", "KC-001"),
   ("Climbing to a high shelf holding china is how kitchens hurt people",
    "KC-010")],
  "a kitchen chair standing in front of a tall cabinet, everyday plates "
  "visible on the shelf above head height"),
 ("Upper Cabinet Zone", "KF-012", "GLASSES COME DOWN WHEN THE DOOR OPENS",
  "Something shifts every single time, and one day it will not stop.",
  [("Glass is stacked at or above head height", "KC-010"),
   ("Categories are mixed, so nothing stacks squarely", "KC-008"),
   ("The shelf is holding more than it was built for", "KC-007")],
  "an open cabinet with drinking glasses stacked rim to base in a leaning "
  "tower on a high shelf"),

 ("Lower Cabinet and Cookware Zone", "KF-013",
  "EVERY PAN IS UNDER THREE OTHERS",
  "I take out four to cook with one, then leave them on the floor.",
  [("The stacks are deeper than three", "KC-004"),
   ("There are more pans here than we cook with", "KC-001"),
   ("Nothing holds them apart", "KC-007")],
  "an open low cabinet with five pans nested deep inside one another and two "
  "more pulled out onto the floor in front of it"),
 ("Lower Cabinet and Cookware Zone", "KF-014", "THE LIDS ARE A LANDSLIDE",
  "They live loose and they come out sideways.",
  [("Lids have no place of their own", "KC-002"),
   ("There is no rack or rail to stand them in", "KC-007"),
   ("They are stored away from the pans they belong to", "KC-003")],
  "a low cabinet with eight pan lids lying loose and overlapping, one tipped "
  "forward past the cabinet edge"),
 ("Lower Cabinet and Cookware Zone", "KF-015",
  "THE HEAVY POT LIVES OVER MY HEAD",
  "I lift it down with both arms and hope.",
  [("Weight is stored above shoulder height", "KC-010"),
   ("It is nowhere near the hob it is used at", "KC-003"),
   ("The cabinet floor, where it should be, is already full", "KC-007")],
  "a heavy cast iron pot standing on a high shelf above a kitchen counter, "
  "well above shoulder height"),

 ("Utensil and Utility Drawers", "KF-016", "THE JUNK DRAWER TAKES ANYTHING",
  "It takes anything and it gives nothing back.",
  [("The things in it have no home anywhere else", "KC-002"),
   ("The drawer has never been given a job", "KC-008"),
   ("You cannot see what is in it without emptying it", "KC-005")],
  "an open shallow drawer holding tangled cable, loose batteries, a tape "
  "measure, string, pens and coins jumbled together"),
 ("Utensil and Utility Drawers", "KF-017",
  "I REACH FOR A SPATULA AND FIND A BLADE",
  "One of these mornings that is going to be stitches.",
  [("An unsheathed blade is loose among the hand tools", "KC-010"),
   ("Nothing divides the drawer", "KC-007"),
   ("No drawer in here holds one category", "KC-008")],
  "an open drawer of mixed kitchen tools with an uncovered paring knife and "
  "a mandoline blade lying among wooden spoons and spatulas"),
 ("Utensil and Utility Drawers", "KF-018", "THE DRAWER WILL NOT CLOSE",
  "It catches on something every time, and I shove it.",
  [("It holds more than it can take", "KC-007"),
   ("Most of what is in it is a duplicate", "KC-001"),
   ("Half of it belongs in a different drawer", "KC-003")],
  "a kitchen drawer standing a finger's width open with a wooden spoon "
  "handle jammed above the drawer front"),

 ("Refrigerator and Freezer", "KF-019", "WE THROW FOOD AWAY EVERY WEEK",
  "Good food, bought on purpose, binned unopened.",
  [("We cannot see what we already own", "KC-005"),
   ("Nothing has a place that means eat this first", "KC-002"),
   ("Nothing checks the fridge before the shopping list", "KC-009")],
  "an open refrigerator with a crowded middle shelf, containers pushed "
  "behind one another, a wilting bag of salad leaves at the back"),
 ("Refrigerator and Freezer", "KF-020", "RAW MEAT SITS ABOVE THE SALAD",
  "It goes wherever there was a gap when the shopping came in.",
  [("Raw food above ready to eat food drips onto it", "KC-010"),
   ("No shelf has been assigned to anything", "KC-002"),
   ("The low shelf is full of drinks", "KC-003")],
  "an open refrigerator with a packaged raw chicken on an upper shelf "
  "directly above an open bowl of salad leaves"),
 ("Refrigerator and Freezer", "KF-021", "THE BACK OF THE FRIDGE IS ARCHAEOLOGY",
  "Nobody knows how long that jar has been in there.",
  [("Nothing carries a date", "KC-005"),
   ("There is no moment when the fridge gets cleared", "KC-009"),
   ("Leftovers go in and are never counted again", "KC-011")],
  "the back of a refrigerator shelf holding several forgotten jars and an "
  "opaque container pushed into the corner"),
]


# ---------------------------------------------------------------------------
# ACTION LAYER. Two per zone, a fifteen minute reset that restores the
# standard and a thirty minute rebuild that changes the zone so the standard
# is achievable, plus four whole kitchen cards. Every one is written to be
# read standing up with a phone in one hand, so the steps are numbered,
# physical, and end in something you can see.
# ---------------------------------------------------------------------------

ACTIONS = [
 {"id": "KA-001", "zone": "Primary Prep Counter", "title": "CLEAR THE RUN",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Get one unbroken run of counter back, and prove it can hold.",
  "why": "You cannot cook in twenty centimetres, and every other habit in "
         "this kitchen starts on this surface.",
  "inputs": ["the dining table, as a staging area", "a bin bag",
             "a damp cloth"],
  "steps": [
   "Take everything off the prep counter and set it on the dining table. "
   "Everything, including the things you are sure belong there.",
   "Let only three things back: what you cut on, what you cut with, and what "
   "you season with.",
   "Lift the kettle and the toaster rather than wiping around them, clean "
   "under their feet, set them back against the wall and coil the cords.",
   "Everything still on the table goes to a home elsewhere, or leaves. Do "
   "not put one item back to decide about later, because that is the item "
   "the pile grows from.",
   "Wipe the run and lay the board down on bare counter."],
  "causes": ["KC-001", "KC-008"],
  "victory": "Your largest cutting board lies flat with room on both sides, "
             "and nothing else is on the run.",
  "next": "KS-001",
  "art": "a long run of kitchen counter completely bare except for one "
         "wooden cutting board lying flat in the middle of it"},

 {"id": "KA-002", "zone": "Primary Prep Counter",
  "title": "REBUILD THE PREP COUNTER", "minutes": 30, "players": "1 to 2",
  "six_s": "Straighten",
  "goal": "Change the counter so clear is the easy state rather than the "
          "daily effort.",
  "why": "A surface you have to defend every evening was laid out wrong. "
         "Fix the layout and the defending stops.",
  "inputs": ["a tape measure", "low tack tape or a marker",
             "one empty low cabinet shelf"],
  "steps": [
   "Stand where you actually cut, and do not move. That spot is the anchor "
   "and everything else is measured from it.",
   "Measure your largest board and mark that width under the counter lip "
   "with tape, so where the work surface starts is a fact and not an "
   "opinion.",
   "Knives on your dominant side, on a wall strip or in a block. Oil and "
   "salt behind the board rather than beside it.",
   "Mixing bowls into the cabinet directly underneath, so you can reach one "
   "without turning around.",
   "Count real uses of every appliance still on the counter over the past "
   "month, not intended ones. Under a couple of times a week, it goes to a "
   "low cabinet. Not switched on in a year, it leaves the kitchen."],
  "causes": ["KC-003", "KC-004", "KC-007"],
  "victory": "You can cut, season, and reach a mixing bowl without taking a "
             "step or turning around.",
  "next": "KA-001",
  "art": "a kitchen counter with a short strip of plain tape marking the "
         "width of a cutting board under the counter lip, the board in place "
         "above it and a knife strip on the wall to the right"},

 {"id": "KA-003", "zone": "Cooking Zone", "title": "COOKING ZONE RESET",
  "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "Put oil, salt and one turner back within a single reach, and "
          "clear the landing space.",
  "why": "Everything here is done with your hands full and the heat already "
         "on. A step taken now is a step you cannot take then.",
  "inputs": ["a tray or a large bowl to hold the tools you pull",
             "a damp cloth"],
  "steps": [
   "Empty the utensil crock out onto the counter.",
   "Put back six tools, each one you actually used this month. The rest go "
   "to a drawer or leave the kitchen.",
   "Oil, salt and pepper within one reach of the burner you use most.",
   "Clear the landing space beside the hob down to bare counter, wide enough "
   "to set a hot pan on.",
   "Turn every pan handle in, so nothing sticks out over the front edge."],
  "causes": ["KC-001", "KC-007"],
  "victory": "With your feet still, you can reach oil, salt and a turner, and "
             "you have somewhere to set a hot pan down.",
  "next": "KS-002",
  "art": "a stoneware crock beside a hob holding exactly six cooking tools "
         "with space around them, a bottle of oil and a salt pot alongside, "
         "and a clear stretch of bare counter to the right"},

 {"id": "KA-004", "zone": "Cooking Zone", "title": "REBUILD THE COOKING ZONE",
  "minutes": 30, "players": "1", "six_s": "Safety",
  "goal": "Lay the burner surround out for one reach, and take the fire risk "
          "out of it.",
  "why": "Oil left heating and a tea towel stored within reach of a live "
         "burner are the two ways a kitchen fire actually starts.",
  "inputs": ["a small hook and its fixing", "a bin bag",
             "a food area degreaser and a microfibre cloth"],
  "steps": [
   "Mount a hook for the pot holders within a hand's reach of the burners "
   "and clear of the heat, so you never hunt for them with a hot pan.",
   "Pull every spice jar. Anything not used in a year leaves. The ones you "
   "reach for weekly go to the front row.",
   "Move the paper towel roll, the tea towels and any packaging off the "
   "burner side entirely.",
   "Degrease the surround and the hob, working top down so what you loosen "
   "falls onto surfaces you have not cleaned yet.",
   "After cleaning, light every burner once and watch for an even blue ring. "
   "A lazy yellow flame, or a burner that clicks and will not catch, is a "
   "call to a registered engineer and not a thing to adjust yourself."],
  "causes": ["KC-005", "KC-010"],
  "victory": "Pot holders found without looking, weekly spices in the front "
             "row, nothing that burns within reach of a burner, and every "
             "burner lighting evenly.",
  "next": "KA-016",
  "art": "the wall and counter beside a clean gas hob, two quilted pot "
         "holders hanging on a small hook clear of the burners, a spice rack "
         "with its front row standing proud, and no cloth or paper anywhere "
         "near the heat"},

 {"id": "KA-005", "zone": "Sink and Dishwashing Zone", "title": "SINK RESET",
  "minutes": 15, "players": "1", "six_s": "Shine",
  "goal": "Empty basin, dry basin, two tools standing.",
  "why": "This is the point the whole kitchen resets from. When it is clear "
         "the rest is recoverable, and when it is not, nothing else starts.",
  "inputs": ["a microfibre cloth", "a neutral pH cleaner"],
  "steps": [
   "Empty the sink completely, including the pan you were going to soak.",
   "Wipe the basin dry, and wipe the drain flange, which is the part nobody "
   "cleans and everybody smells.",
   "One brush and one sponge, standing where they drain. Everything else "
   "comes off the surround.",
   "Take out of the drying rack anything that is already dry.",
   "Wipe the tap and the surround, and dry them so no water sits."],
  "causes": ["KC-009", "KC-008"],
  "victory": "Dry basin, two tools standing, nothing lying in water.",
  "next": "KS-003",
  "art": "an empty stainless sink with a dry basin and a clean drain flange, "
         "one brush and one sponge standing upright in a small slotted caddy, "
         "and an empty drying rack beside it"},

 {"id": "KA-006", "zone": "Sink and Dishwashing Zone",
  "title": "REBUILD UNDER THE SINK", "minutes": 30, "players": "1",
  "six_s": "Safety",
  "goal": "One tray, the pipes visible, and nothing stored that can react "
          "with anything beside it.",
  "why": "This is the one cabinet in the house where two ordinary bottles "
         "make a gas that will drive you out of the room.",
  "inputs": ["one shallow tray", "a bin bag",
             "your local household chemical disposal rules"],
  "steps": [
   "Take everything out. Everything, including the bottles at the back.",
   "Separate bleach from any acidic or ammonia based cleaner, and never "
   "store them in the same tray. If you cannot tell what a bottle is, read "
   "the label. If it has no label, dispose of it by your local rules rather "
   "than guessing.",
   "Anything hazardous that sits within a child's reach moves up and out of "
   "this cabinet, or the cabinet gets a latch.",
   "One shallow tray goes back, holding dish soap, dishwasher tablets and "
   "one all purpose cleaner. That is the whole inventory.",
   "Leave the pipework visible, so a leak is something you see early instead "
   "of something you smell late."],
  "causes": ["KC-010", "KC-002", "KC-001"],
  "victory": "One tray, three bottles, and bare pipes you can see all the "
             "way around.",
  "next": "KA-016",
  "art": "an open under sink cabinet holding a single shallow tray with "
         "three plain unlabelled bottles on it, the white pipework fully "
         "visible and clear all around, the rest of the cabinet floor bare"},

 {"id": "KA-007", "zone": "Upper Cabinet Zone",
  "title": "UPPER CABINET RESET", "minutes": 15, "players": "1",
  "six_s": "Straighten",
  "goal": "Daily things to daily height, one category per stack.",
  "why": "Every plate you use is fetched twice a day. Height is the whole "
         "cost.",
  "inputs": ["clear counter space to stage on", "a step stool with a "
             "handrail, if anything is genuinely out of reach"],
  "steps": [
   "Bring down everything you use less than once a month.",
   "Send it to the top shelf, on its edge where it will stand.",
   "Everything daily comes to the shelf between your shoulder and your eye.",
   "One category per stack. Plates with plates, bowls with bowls, and "
   "nothing perched on top of a different thing.",
   "Cap plate stacks at about six, and space the mugs so each one lifts out "
   "without moving another."],
  "causes": ["KC-004", "KC-006"],
  "victory": "You can take a plate and a mug down with one hand each, moving "
             "nothing else.",
  "next": "KS-004",
  "art": "an open upper cabinet with a stack of six plates and a separate "
         "stack of bowls at chest height, five mugs standing clear of one "
         "another, and one large platter on edge on the shelf above"},

 {"id": "KA-008", "zone": "Upper Cabinet Zone",
  "title": "REBUILD THE UPPER CABINETS", "minutes": 30, "players": "1 to 2",
  "six_s": "Safety",
  "goal": "Band the cabinet by height so nobody climbs for anything they use "
          "every day.",
  "why": "Reaching a top shelf from a chair, a counter edge or an open drawer "
         "is how people fall in kitchens, and it happens while they are "
         "holding something breakable.",
  "inputs": ["a step stool with a handrail",
             "somewhere outside the kitchen for the second set"],
  "steps": [
   "Have the shortest adult who uses this kitchen fetch the everyday plates "
   "while you watch. Their reach is the test, not yours.",
   "Band the cabinet: below shoulder and shoulder to eye are for daily "
   "things, above eye is for monthly or less.",
   "No glass above head height. None, in any cabinet, for any reason.",
   "Second sets, inherited china and the platter for eight go to the top "
   "shelf or out of the kitchen altogether.",
   "If something still needs a climb, buy a two step stool with a handrail "
   "and keep it in the kitchen. Never a chair, never a drawer edge, never "
   "the counter."],
  "causes": ["KC-006", "KC-010", "KC-001"],
  "victory": "The shortest person in the house can lay the table without "
             "climbing or asking.",
  "next": "KA-016",
  "art": "a tall run of kitchen cabinets with the everyday plates and bowls "
         "on the shelf at chest height, the highest shelf holding one large "
         "platter and nothing else, and a small two step stool with a "
         "handrail standing beside them"},

 {"id": "KA-009", "zone": "Lower Cabinet and Cookware Zone",
  "title": "COOKWARE RESET", "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "The two pans you cook with nightly at the front, everything else "
          "capped at three deep.",
  "why": "Taking four pans out to use one is why they end up living on the "
         "floor of the kitchen.",
  "inputs": ["floor space to lay everything out", "a damp cloth"],
  "steps": [
   "Take out every pan and every lid.",
   "Put back the two you cook with nightly, at the front, in the cabinet "
   "nearest the hob.",
   "Cap every stack at three, or stand pans on edge if you have a divider.",
   "Stand the baking sheets on end rather than laying them flat.",
   "Whatever is still on the floor when you finish has not earned the "
   "cabinet. Decide about it now, not next week."],
  "causes": ["KC-004", "KC-001"],
  "victory": "Each of your three most used pans comes out in one motion, "
             "moving nothing else.",
  "next": "KS-005",
  "art": "an open low cabinet with two frying pans at the front within easy "
         "reach, three baking sheets standing on end in a divider, and clear "
         "space between each group"},

 {"id": "KA-010", "zone": "Lower Cabinet and Cookware Zone",
  "title": "REBUILD THE COOKWARE CABINET", "minutes": 30, "players": "1",
  "six_s": "Straighten",
  "goal": "Give the heavy pieces a floor, the lids a rack, and the sheets an "
          "edge to stand on.",
  "why": "A tall nest of pans, or a cast iron pot stored above waist height, "
         "comes down on hands and feet the moment the stack shifts.",
  "inputs": ["a wire divider or two tension rods", "a lid rack or a door rail",
             "a sheathed box for loose blades"],
  "steps": [
   "Heaviest pieces onto the cabinet floor. Nothing heavy above shoulder "
   "height anywhere in this kitchen.",
   "Set a divider or a pair of tension rods so baking sheets, boards and "
   "shallow pans stand on end.",
   "Fit a lid rack, or a rail on the inside of the door, so no lid is ever "
   "loose.",
   "Food processor and blender blades go into a sheathed box, never loose "
   "inside a bowl in a dark low cabinet where fingers go looking.",
   "Test it: fetch your three most used pans one at a time and count the "
   "movements. Two or fewer, or move it again."],
  "causes": ["KC-004", "KC-010", "KC-007"],
  "victory": "Nothing has to come out to reach anything else, and nothing "
             "heavy is stored above your shoulder.",
  "next": "KA-016",
  "art": "an open low cabinet with a heavy cast iron pot on the cabinet "
         "floor, a wire lid rack holding four lids upright, and a divider "
         "holding three baking sheets on end"},

 {"id": "KA-011", "zone": "Utensil and Utility Drawers",
  "title": "DRAWER RESET", "minutes": 15, "players": "1", "six_s": "Sort",
  "goal": "One drawer, one job, and it closes with one push.",
  "why": "A drawer with no job accepts everything, and then nothing in it "
         "can be found.",
  "inputs": ["a tray to tip onto", "blade sleeves or sheaths",
             "a damp cloth"],
  "steps": [
   "One drawer at a time. Tip it out onto a tray.",
   "Say the drawer's one job out loud before anything goes back into it.",
   "Only that category returns. Everything else goes to the drawer it "
   "belongs in, or out of the kitchen.",
   "Sheath every blade. If a blade has no sheath, it does not go back in "
   "until it has one.",
   "Close it. If it does not close flush with one push, take something out "
   "rather than shoving it."],
  "causes": ["KC-007", "KC-010", "KC-008"],
  "victory": "You can name each drawer's job, and each one closes with one "
             "push.",
  "next": "KS-006",
  "art": "an open shallow drawer holding only a divided flatware insert, "
         "each compartment holding one kind of utensil and nothing loose "
         "beside it"},

 {"id": "KA-012", "zone": "Utensil and Utility Drawers",
  "title": "REBUILD THE DRAWERS", "minutes": 30, "players": "1",
  "six_s": "Standardize",
  "goal": "Name every drawer where only the household sees it, and get the "
          "small hazards out of the low ones.",
  "why": "A drawer that is named is a drawer that gets put back correctly by "
         "somebody who does not live here.",
  "inputs": ["masking tape and a pen", "a divided insert",
             "a lidded box for batteries"],
  "steps": [
   "Write each drawer's name on tape inside its front edge, where you see it "
   "as it opens and no guest ever does.",
   "Divided insert for flatware, with nothing loose beside it.",
   "Foil, cling film and baking paper stand on end so you can read the boxes "
   "from above.",
   "Button batteries and anything small enough to be swallowed leave the low "
   "drawers entirely, into a lidded box stored high.",
   "Give the junk drawer a real job, or dissolve it. Tape, batteries and a "
   "tape measure can each have a home. The rest of it is a decision you have "
   "been storing instead of making."],
  "causes": ["KC-002", "KC-008", "KC-010"],
  "victory": "Every drawer has a name written inside it, and nothing "
             "swallowable is stored at child height.",
  "next": "KS-006",
  "art": "an open kitchen drawer seen from above with a strip of plain "
         "masking tape along the inside of its front edge, a divided insert "
         "below it, and three boxes of wrap standing upright on end"},

 {"id": "KA-013", "zone": "Refrigerator and Freezer", "title": "FRIDGE RESET",
  "minutes": 15, "players": "1", "six_s": "Shine",
  "goal": "Raw low, dates on, one eat first bin at the front.",
  "why": "Most food thrown away in a house was bought on purpose and then "
         "became invisible.",
  "inputs": ["one shallow open bin", "blank labels and a pen", "a bin bag",
             "a neutral pH cleaner and a cloth"],
  "steps": [
   "Bin the obvious. Do not negotiate with a container you have to smell.",
   "Raw meat down to the lowest shelf, sealed, so nothing can drip onto "
   "anything you will not cook again.",
   "Put one shallow bin at the front of the middle shelf, where the door "
   "opens straight onto it, and put everything within three days of turning "
   "into it.",
   "A blank label and a date on every leftover, on the lid where you will "
   "read it.",
   "Wipe the one shelf you cleared. One shelf today is a finished job; the "
   "whole fridge is an abandoned one."],
  "causes": ["KC-005", "KC-010", "KC-011"],
  "victory": "Nothing raw above anything ready to eat, every leftover dated, "
             "and one bin at the front that tells you what to cook tonight.",
  "next": "KS-007",
  "art": "an open refrigerator with a shallow open bin at the front of the "
         "middle shelf, clear lidded containers behind it each wearing a "
         "small blank white label, and a sealed pack of raw meat on the "
         "lowest shelf"},

 {"id": "KA-014", "zone": "Refrigerator and Freezer",
  "title": "REBUILD THE FRIDGE", "minutes": 30, "players": "1 to 2",
  "six_s": "Standardize",
  "goal": "Assign every shelf a job, and make the cold chain visible.",
  "why": "A fridge without assigned shelves is filled by whoever unpacks the "
         "shopping, which is why the raw chicken ends up over the salad.",
  "inputs": ["a fridge thermometer", "clear lidded containers",
             "blank labels and a pen"],
  "steps": [
   "Assign the shelves out loud and agree them with whoever else shops: raw "
   "low and sealed, leftovers at eye level, door for condiments only.",
   "Pull anything pressed against the rear vents. Blocked vents cost cooling "
   "and they cost money every day.",
   "Clear containers only for anything you want eaten. Opaque food is "
   "forgotten food.",
   "Put a thermometer in and check it. The usual food safety guidance is a "
   "fridge at or below 5C or 41F and a freezer at minus 18C or 0F; if yours "
   "will not hold that, it is a repair call, not a storage problem.",
   "Set the eat first bin where the door opens straight onto it, and nothing "
   "else goes in that spot."],
  "causes": ["KC-005", "KC-010", "KC-011", "KC-012"],
  "victory": "Anyone unpacking the shopping can put it away correctly "
             "without being told, and the thermometer reads in range.",
  "next": "KA-017",
  "art": "an open refrigerator seen straight on with clearly separated "
         "shelves, sealed raw meat lowest, clear labelled containers at eye "
         "level, a small round thermometer clipped to a shelf, and the rear "
         "wall clear of anything pressed against it"},

 {"id": "KA-015", "zone": None, "title": "THE FIVE MINUTE CLOSE",
  "minutes": 5, "players": "1, any night", "six_s": "Sustain",
  "goal": "Leave the kitchen in a state tomorrow can start from.",
  "why": "This is the card that makes the other seventy one hold. A standard "
         "with no closing ritual decays in about a week.",
  "inputs": ["a cloth", "the dishwasher"],
  "steps": [
   "Sink empty, basin dry.",
   "Prep run clear to bare counter, board down.",
   "Landing space beside the hob clear.",
   "Anything that does not live in the kitchen leaves the kitchen.",
   "Press start on the dishwasher. That is the trigger, and it is the "
   "finish line."],
  "causes": ["KC-009"],
  "victory": "Five minutes, five things, and tomorrow starts from zero.",
  "next": "KE-001",
  "art": "a kitchen at night with every counter bare, the sink empty and "
         "dry, one cutting board lying flat, and a single low light on"},

 {"id": "KA-016", "zone": None, "title": "THE HOT ZONE WALK",
  "minutes": 15, "players": "1, and one other person to disagree with you",
  "six_s": "Safety",
  "goal": "Six checks across the whole kitchen, and an honest answer on "
          "each.",
  "why": "Safety outranks tidy and it outranks pretty. Do this card before "
         "any of the rebuilds, because the rebuilds move heavy and sharp "
         "things around.",
  "inputs": ["nothing but fifteen minutes and your eyes"],
  "steps": [
   "Blades. Every blade sheathed, in a block, or on a strip. None loose in a "
   "drawer, none blade up in a drying rack, none under suds in a full sink.",
   "Weight. Nothing heavy above shoulder height. No glass above head height.",
   "Heat. Tea towels, paper roll and packaging out of reach of any burner, "
   "and the toaster clear of the cabinet above it.",
   "Water and electricity. No kettle, socket, or charging phone within "
   "splash distance of the basin.",
   "Chemicals. Bleach stored apart from any acidic or ammonia cleaner, "
   "everything labelled, and anything hazardous out of a child's reach.",
   "Raw above ready to eat. Nothing raw stored above anything that will not "
   "be cooked again."],
  "causes": ["KC-010", "KC-006"],
  "victory": "Six checks done, and you can say out loud which ones failed. "
             "Anything involving gas, a scorch mark, a frayed cord, or a "
             "burner that will not light is a call to a qualified person and "
             "not a job for this card.",
  "next": "KS-001",
  "art": "a calm kitchen seen wide with a knife block on the counter, a "
         "clear space around the hob, a closed low cabinet, and no cloth or "
         "paper near the burners"},

 {"id": "KA-017", "zone": None, "title": "THE SHOPPING LIST LOOP",
  "minutes": 15, "players": "everyone who shops", "six_s": "Standardize",
  "goal": "Write the list from what you own instead of from what you "
          "imagine.",
  "why": "Buying what you already own is a visibility problem, and it costs "
          "money every single month.",
  "inputs": ["one list, in one place everyone can reach"],
  "steps": [
   "Before the list, open the fridge and look in the eat first bin. Write "
   "the list from what is there.",
   "Anything down to its last one goes on the list now, not when it runs "
   "out.",
   "One list, one place, and everyone in the house can add to it.",
   "Put the shopping away into the fridge order you assigned, not wherever "
   "there is a gap.",
   "Note anything you bought that you already owned. That is the measure "
   "this card improves."],
  "causes": ["KC-011", "KC-005"],
  "victory": "One shop where you bought nothing you already had, and threw "
             "nothing away that week.",
  "next": "KA-013",
  "art": "a small blank notepad and a pencil on a clear kitchen counter "
         "beside an open refrigerator door, no writing visible on the page"},

 {"id": "KA-018", "zone": None, "title": "THE TWO COOK TREATY",
  "minutes": 20, "players": "everyone who uses this kitchen",
  "six_s": "Standardize",
  "goal": "One sentence about this kitchen that two people will both sign.",
  "why": "The dishwasher argument is not about the dishwasher. Two people "
         "are running one zone by two designs, and both of them are right.",
  "inputs": ["one card each and a pen", "twenty minutes when nobody is "
             "hungry"],
  "steps": [
   "Each person writes, separately and without discussion, what this kitchen "
   "should look like at bedtime. One sentence.",
   "Read them out. Circle what you agree on. That part is already your "
   "standard.",
   "Where you differ, name the value underneath it rather than arguing the "
   "arrangement: speed, calm, cleanliness, or being able to see things.",
   "Design for the shared outcome and accommodate the difference. If one "
   "person needs it visible and one needs it hidden, put it visible inside a "
   "closed door.",
   "Write the sentence you both signed onto the standard card, and put it "
   "where the disagreement actually happens."],
  "causes": ["KC-012", "KC-008"],
  "victory": "One sentence, two signatures, on the wall, and neither person "
             "had to lose.",
  "next": "KS-003",
  "art": "two small blank cards and a pen lying side by side on a clear "
         "kitchen table, no writing on either card"},
]


# ---------------------------------------------------------------------------
# EVENT LAYER. Six days that test a kitchen. An event is not a chore, it is a
# stress test: it names which standard is under load, how you know it held,
# and which card to draw if it did not. This is the only part of the deck
# with any play in it, and it is what makes the deck worth keeping after the
# first pass instead of filing.
# ---------------------------------------------------------------------------

EVENTS = [
 ("KE-001", "THE GROCERY HAUL",
  "Twelve bags on the floor and forty minutes of cold chain.",
  ["KZ-007", "KZ-004"],
  "Everything cold is away within ten minutes, and nothing already in the "
  "fridge had to be moved to make room.",
  "Whatever you could not put away without shifting something else is a "
  "capacity or location problem. Draw that zone's rebuild.",
  "a kitchen floor and counter with eight full paper grocery bags standing "
  "in front of an open refrigerator"),
 ("KE-002", "WEEKNIGHT DINNER, FORTY MINUTES",
  "Everyone is hungry, nothing is prepped, and it is a school night.",
  ["KZ-001", "KZ-002"],
  "You opened no more than two drawers looking for a tool, and there was "
  "somewhere clear to set the hot pan down.",
  "Every extra drawer you opened is a point of use problem. Draw KA-003.",
  "a hob with two pans going and a clear stretch of counter beside them, "
  "steam rising, evening light through a window"),
 ("KE-003", "THE DISHWASHER IS BROKEN",
  "Three days of washing by hand, with everyone still eating.",
  ["KZ-003"],
  "The sink is still empty at bedtime on day three.",
  "If it failed on day one, the sink was never running on a standard, it was "
  "running on a machine. Draw KA-018 and then KS-003.",
  "a kitchen sink with a washing up bowl, a drying rack holding clean "
  "plates, and a dry clear surround"),
 ("KE-004", "SIX DISHES AT ONCE",
  "The holiday cook. Four burners, one oven, and people in the room.",
  ["KZ-002", "KZ-005"],
  "Nothing heavy came down off a high shelf, and every pan handle stayed "
  "turned in with people moving behind you.",
  "If you reached over a burner for anything, that thing is in the wrong "
  "place. Draw KA-004.",
  "a busy kitchen counter with several prepared dishes waiting, pans on "
  "every burner, handles all turned inward"),
 ("KE-005", "SOMEBODY IN THE HOUSE IS ILL",
  "Cooking for a household where hygiene suddenly matters more than usual.",
  ["KZ-003", "KZ-007"],
  "Cloths and sponges were changed, raw stayed low and sealed, and the sink "
  "still got cleared on the bad day.",
  "If the close down was the thing that slipped, it was never attached to a "
  "trigger. Draw KA-015.",
  "a clean kitchen sink with a fresh sponge and a folded clean cloth beside "
  "it, everything dry and clear"),
 ("KE-006", "GUESTS IN THE KITCHEN",
  "Three people and one work triangle, and none of them live here.",
  ["KZ-004", "KZ-006"],
  "A guest found a glass without asking, and nobody had to cross the hob to "
  "get anywhere.",
  "If they had to ask, the cabinet is not readable from outside. Draw "
  "KA-007, then name the drawers with KA-012.",
  "an open kitchen with a clear walkway past the hob and an open cabinet "
  "showing plainly separated glasses, plates and bowls"),
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
        "related": {"standard": f"KS-{spec['order']:03d}",
                    "actions": [a["id"] for a in ACTIONS
                                if a["zone"] == name]},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Zone",
                "subject": spec["art"],
                "must_show": spec["callouts"],
                "must_show_kind": "objects",
                "accept_test": "Count the six callouts in the picture. If "
                               "any one of them is not a visible object, the "
                               "image is rejected."},
    }


def friction_card(rec) -> dict:
    zone, cid, title, said, branches, art = rec
    return {
        "id": cid, "title": title, "type": "FRICTION CARD", "room": ROOM,
        "zone": zone, "difficulty": 1,
        "tagline": "WHAT IT LOOKS LIKE. THEN WHY.",
        "objective": said,
        "prompt": "Why does this happen here?",
        "branches": [{"answer": a, "root_cause": c} for a, c in branches],
        "instruction": "Pick the answer that is true in your kitchen, then "
                       "turn to that root cause card. If two are true, take "
                       "the one you could change this week.",
        "related": {"zone": ZONES[zone]["id"],
                    "root_causes": [c for _, c in branches]},
        "source": "hand authored, not in the Manual",
        "art": {"framing": "Friction",
                "subject": art,
                "must_show": [said],
                "must_show_kind": "condition",
                # A tidy picture on a friction card is the exact defect that
                # shipped on the previous deck: a card about lost keys over a
                # photograph of a pristine, empty console table. The reviewer
                # test is stated on the card so it cannot be forgotten again.
                # The other deck is not named here, because the prompt
                # builder refuses any prompt that names a different room and
                # it is right to.
                "accept_test": "The problem has to be visible, and it has to "
                               "look like a real Tuesday rather than a "
                               "disaster. A tidy picture on a friction card "
                               "is a rejection: if a stranger could not say "
                               "what is wrong, it failed."},
    }


def cause_card(rec) -> dict:
    cid, title, six_s, meaning, confirm, art = rec
    frictions = [f[1] for f in FRICTIONS
                 if cid in [c for _, c in f[4]]]
    actions = [a["id"] for a in ACTIONS if cid in a["causes"]]
    return {
        "id": cid, "title": title, "type": "ROOT CAUSE CARD", "room": ROOM,
        "zone": None, "difficulty": 2, "six_s": six_s,
        "tagline": f"{six_s.upper()} FIXES THIS ONE.",
        "objective": meaning,
        "confirm_in_30_seconds": confirm,
        "instruction": f"This is a {six_s} problem. Draw one of the action "
                       f"cards listed and do it now, at the length you "
                       f"actually have.",
        "related": {"frictions": frictions, "actions": actions},
        "source": "hand authored, from the product root cause model",
        "art": {"framing": "Root Cause",
                "subject": art,
                "must_show": [meaning],
                "must_show_kind": "condition",
                "accept_test": "One idea, one object, no room tour. If the "
                               "picture could illustrate three different "
                               "causes it is rejected."},
    }


def action_card(a: dict) -> dict:
    return {
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
        "victory_condition": a["victory"],
        "next_card": a["next"],
        "source": "hand authored, steps grounded in the Manual passes",
        "art": {"framing": "Action",
                "subject": a["art"],
                "must_show": [a["victory"]],
                "must_show_kind": "condition",
                "accept_test": "The picture shows the finished state the "
                               "victory condition describes, not the work in "
                               "progress and not a person doing it."},
    }


def standard_card(name: str, z: dict, spec: dict) -> dict:
    return {
        "id": f"KS-{spec['order']:03d}", "title": f"{name.upper()} STANDARD",
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
        "instruction": "This is a write on card. Fill it in with a pen, in "
                       "your own words if the printed sentence is not yours, "
                       "and put it where the zone is. A standard nobody "
                       "signed is a preference.",
        "related": {"zone": spec["id"],
                    "actions": [a["id"] for a in ACTIONS
                                if a["zone"] == name]},
        "source": "content/manual/source/content.json",
        "art": {"framing": "Standard",
                "subject": f"{spec['art']}, photographed plainly with a "
                           f"generous area of empty calm surface across the "
                           f"lower half for the write on lines",
                "must_show": ["the zone holding its standard"],
                "must_show_kind": "condition",
                "accept_test": "The lower half of the frame must be visually "
                               "quiet enough to print three blank lines over "
                               "it and still read."},
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
        "instruction": "Do not do anything to prepare. Live the day, then "
                       "read the two lines below and be honest about which "
                       "one you are.",
        "related": {"zones": zones},
        "source": "hand authored, not in the Manual",
        "art": {"framing": "Event",
                "subject": art,
                "must_show": [setup],
                "must_show_kind": "condition",
                "accept_test": "The pressure has to be visible in the "
                               "objects. No people, so the load has to be "
                               "shown by what is on the surfaces."},
    }


def room_card(zones: dict) -> dict:
    order = sorted(ZONES.items(), key=lambda kv: kv[1]["order"])
    return {
        "id": "KR-001", "title": "THE KITCHEN", "type": "ROOM CARD",
        "room": ROOM, "zone": None, "difficulty": 1,
        "tagline": "SEVEN ZONES. START AT THE SINK.",
        "objective": "The kitchen is seven small places, not one big job. "
                     "This card is the map and the order.",
        "zones_in_order": [f"{v['id']} {k}" for k, v in order],
        "start_here": "KZ-003 Sink and Dishwashing Zone. It is the shortest "
                      "zone, it is the point the whole kitchen resets from, "
                      "and you will have finished something in fifteen "
                      "minutes.",
        "how_to_play": [
            "1. Deal the seven ZONE cards face up. Pick the one that is "
            "annoying you today, or take the one this card says to start at.",
            "2. Lay out that zone's three FRICTION cards. Keep the ones that "
            "are true in your kitchen. Put the rest back.",
            "3. Turn a friction card over and pick the answer that is true. "
            "It names a ROOT CAUSE.",
            "4. The root cause card names the ACTION cards that fix that "
            "cause. Pick the one that matches the time you actually have: "
            "five, fifteen or thirty minutes.",
            "5. Do it standing up, with the card in your hand.",
            "6. Read the victory condition out loud. If it is not true yet, "
            "you are not finished, and that is the whole scoring system.",
            "7. Fill in the zone's STANDARD card with a pen and put it where "
            "the zone is.",
            "8. Draw an EVENT card when an ordinary hard day happens, and see "
            "whether the standard held.",
        ],
        "players": "1 to 6. With more than one, deal the friction cards out "
                   "and let each person keep the ones they believe. "
                   "Disagreement is the useful part, not a problem to "
                   "resolve before starting.",
        "six_s": "Sort, Straighten, Shine, Safety, Standardize, Sustain",
        "safety_first": "Do KA-016 The Hot Zone Walk before any rebuild. It "
                        "takes fifteen minutes and the rebuilds move heavy "
                        "and sharp things around.",
        "source": "content/manual/source/content.json",
        "art": {"framing": "Room",
                "subject": "a wide establishing view of a whole modern "
                           "kitchen in its settled state, hob, sink, prep "
                           "counter, upper cabinets and refrigerator all "
                           "visible in one frame, everything put away",
                "must_show": ["all seven zones legible in one frame"],
                "must_show_kind": "objects",
                "accept_test": "You should be able to point at where each of "
                               "the seven zones is. If two are not in frame, "
                               "reshoot."},
    }


def build() -> dict:
    zmap = manual_zones()
    missing = [z for z in ZONES if z not in zmap]
    if missing:
        raise SystemExit(
            f"these zones are not in the Manual and would be invented: "
            f"{missing}. The deck's zone list must be the Manual's zone list, "
            f"which is exactly what the Entryway deck got wrong.")

    cards = [room_card(zmap)]
    for name, spec in sorted(ZONES.items(), key=lambda kv: kv[1]["order"]):
        cards.append(zone_card(name, zmap[name], spec))
    cards += [friction_card(f) for f in FRICTIONS]
    cards += [cause_card(c) for c in CAUSES]
    cards += [action_card(a) for a in ACTIONS]
    for name, spec in sorted(ZONES.items(), key=lambda kv: kv[1]["order"]):
        cards.append(standard_card(name, zmap[name], spec))
    cards += [event_card(e) for e in EVENTS]

    gate(cards, zmap)
    return {"deck": "kitchen", "room": ROOM, "count": len(cards),
            "budget": BUDGET, "type_colour": TYPE_COLOUR,
            "source": "content/manual/source/content.json",
            "cards": cards}


def gate(cards: list, zmap: dict) -> None:
    """Every one of these has already been a real defect on this project."""
    ids = [c["id"] for c in cards]
    assert len(ids) == len(set(ids)), "duplicate card id"
    assert len(cards) == TOTAL, f"{len(cards)} cards, budget says {TOTAL}"

    got = {}
    for c in cards:
        got[c["type"]] = got.get(c["type"], 0) + 1
    assert got == BUDGET, f"type counts {got} do not match budget {BUDGET}"

    # Nothing quoted from the Manual may have been edited on the way through.
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["objective"] == zmap[c["zone"]]["purpose"]
            assert c["done_looks_like"] == zmap[c["zone"]]["done_looks_like"]
        if c["type"] == "STANDARD CARD":
            lb = zmap[c["zone"]]["leave_behind"]
            assert c["objective"] == lb["standard"]
            assert c["trigger"] == lb["trigger"]

    known = {c["id"] for c in cards}
    for c in cards:
        for ref in (c.get("related", {}).get("root_causes", [])
                    + c.get("root_causes", [])
                    + c.get("related", {}).get("actions", [])
                    + c.get("tests_zones", [])):
            assert ref in known, f"{c['id']} points at unknown card {ref}"
        nxt = c.get("next_card")
        assert not nxt or nxt in known, f"{c['id']} next_card {nxt} unknown"

    # A root cause nobody can reach is a card that never gets drawn.
    reachable = set()
    for c in cards:
        if c["type"] == "FRICTION CARD":
            reachable |= {b["root_cause"] for b in c["branches"]}
    orphan = [c["id"] for c in cards
              if c["type"] == "ROOT CAUSE CARD" and c["id"] not in reachable]
    assert not orphan, f"root causes no friction routes to: {orphan}"

    # A cause with no action is a diagnosis with no treatment.
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

    # Every card has to be drawable, which means it has to have art.
    for c in cards:
        art = c.get("art") or {}
        assert art.get("subject"), f"{c['id']} has no art subject"
        assert art.get("accept_test"), f"{c['id']} has no art accept test"
        assert art.get("must_show_kind") in ("objects", "condition"), (
            f"{c['id']} does not say whether must_show is a list of things "
            f"to count or a condition to satisfy. Feeding a sentence to a "
            f"model as a list of objects to draw produces a picture of the "
            f"sentence.")
        # The template sets all wording as real type. A prompt that asks for
        # lettering produces garbled text, which is the single most common
        # rejection on this project.
        low = art["subject"].lower()
        for bad in ("label reading", "sign saying", "written", "text",
                    "logo", "brand"):
            assert bad not in low, f"{c['id']} art asks for {bad}"

    # Safety may not be quietly dropped from a room with knives and gas in it.
    assert any(c["id"] == "KA-016" for c in cards), "no safety walk card"
    for c in cards:
        if c["type"] == "ZONE CARD":
            assert c["safety_checks"], f"{c['id']} has no safety check"


def main() -> int:
    deck = build()
    io.open(OUT, "w", encoding="utf-8", newline="").write(
        json.dumps(deck, indent=1, ensure_ascii=False) + "\n")
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  deck        kitchen ({ROOM}), {deck['count']} cards")
    for k in BUDGET:
        print(f"  {k:<18} {by.get(k, 0)}")
    print(f"  zones       {len(ZONES)}, all present in the Manual")
    print(f"  written     {os.path.relpath(OUT, ROOT)}")
    print(f"  art         {deck['count']} subjects, none requesting lettering")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
