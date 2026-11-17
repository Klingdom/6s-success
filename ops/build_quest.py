#!/usr/bin/env python3
"""
Build the Home Quest web app: a playable deck over all 114 micro zones.

WHAT IT IS
----------
The card deck's loop is draw a card, do one thing, put it down. That works on
paper for one room. The manual holds the same structure for 114 micro zones
across 20 rooms, which is far too much to print and exactly the right size for
something that remembers where you got to.

So this is the deck, generalised: every micro zone becomes six cards, one per
S, drawn from the same content the book and the site are built from. Nothing
here is written fresh. If the manual changes, the app changes.

WHY IT IS CLIENT SIDE
---------------------
The site is a static nginx bundle with no server and no accounts. That is a
constraint and also the right answer: a household reset app has no business
holding an account, and progress belongs in the browser of the person doing the
work. Everything persists to localStorage. Nothing is sent anywhere.

WHAT GETS TRIMMED, AND WHY
--------------------------
content.json is 702 KB. Roughly 390 KB of that is `shine_detail`, the deep
per-surface cleaning method, which belongs on the zone pages where somebody is
reading rather than in an app where somebody is holding a cloth. Dropping it
and two reference fields takes the payload to about a third, and the zone page
is one tap away for anybody who wants the detail.

Run:  python ops/build_quest.py
"""
from __future__ import annotations

import io
import json
import os
import re

# The frozen root-cause vocabulary (PLAN-MICROZONES-DECKS-APP.md M1/M4), the
# same module ops/build_zone_pages.py uses to resolve a diagnosis branch's
# cause id to a name and the pass that fixes it. Needed here for the symptom
# entry screen (4.3): a picked symptom names a cause, not just a zone.
import root_causes                                             # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")

# The 110 reviewed zone pictures the zone pages already publish. Two separate
# files have to agree before one is offered to the app, and the third check is
# the disk:
#
#   ops/hero-verdicts.json   somebody looked at this picture and said "ok"
#   ops/hero-fallback.json   the alt text that review approved, verbatim
#   site/assets/zones/       the derivative actually exists at that width
#
# All three, because each has been wrong on its own before. Four of the 114
# are marked "no" (a garage of sawhorses, a board-game zone of moving boxes)
# and must never reach a screen; a stem with no derivative on disk would put a
# 404 inside a <picture> that no browser reports; and inventing alt text for a
# picture nobody described is how an image gets announced as something it is
# not. A zone that fails any of the three simply ships without an image, and
# the app renders text, which is what it did for its whole life until now.
VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")
HERO_ALT = os.path.join(ROOT, "ops", "hero-fallback.json")
ZONE_IMG = os.path.join(SITE, "assets", "zones")
# The site's zone pages are named from the display name, not the raw zone name,
# so "Primary Prep Counter" is published at kitchen-the-primary-prep-counter.
# Using the raw name here produced a link on every card that 404s.
NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))

# Canonical order, asserted rather than trusted to dict iteration. Safety is
# the fourth S and that is the method's most distinctive claim.
SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]

# The six-S ramp, chaos to calm, straight from site/assets/css/site.css.
COLOURS = {"sort": "#CB4B36", "straighten": "#BC4B2A", "shine": "#D98A2B",
           "safety": "#DDA63A", "standardize": "#6E8B5B", "sustain": "#4E7A57"}

# What each pass is for, in the app's own voice. One line, because it sits
# above the instruction and must not compete with it.
PURPOSE = {
    "sort": "Decide what stays. Nothing else.",
    "straighten": "Give what stayed a home you can reach.",
    "shine": "Clean it, and see what the cleaning tells you.",
    "safety": "Fix what could hurt somebody. The fourth S, not the last.",
    "standardize": "Write down what good looks like, so it is not a memory.",
    "sustain": "Attach the reset to something that already happens.",
}


PUBLISHED = os.path.join(ROOT, "ops", "youtube-published.json")


def published_videos() -> dict:
    """{zone stem: YouTube id} for zones whose video is actually published.

    Added 2026-09-16. Twelve zone videos are live on YouTube and every zone
    page links its own, but the app offered none, so the one surface a person
    is actually working in could not show the zone being done. The file is
    keyed by exactly the stem build_data() computes below (room slug, two
    dashes, raw zone name), so this is a lookup, not a guess.

    Only an id that looks like a YouTube id is carried: a half-written entry
    would otherwise ship a dead link into the app. A missing file is normal
    in a checkout with no publishing history and yields no videos at all.
    """
    if not os.path.exists(PUBLISHED):
        return {}
    out = {}
    for stem, rec in json.load(io.open(PUBLISHED, encoding="utf-8")).items():
        vid = (rec or {}).get("video_id") if isinstance(rec, dict) else None
        if isinstance(vid, str) and re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            out[stem] = vid
    return out


def approved_and_published() -> set:
    """Stems that MUST appear, independent of what is on disk right now.

    Deliberately does not look at site/assets/zones/: that is the thing being
    checked. heroes() below adds the disk test on top of this, and main()
    compares the two, so "the file was missing" can never be mistaken for
    "the picture was never approved".
    """
    if not (os.path.exists(VERDICTS) and os.path.exists(HERO_ALT)):
        return set()
    ok = {stem for stem, rec in
          json.load(io.open(VERDICTS, encoding="utf-8")).items()
          if isinstance(rec, dict) and rec.get("verdict") == "ok"}
    published = {e.get("stem") for e in
                 json.load(io.open(HERO_ALT, encoding="utf-8")).values()}
    return ok & published


def heroes() -> set:
    """The stems the app may show. Pictures only, never their sentences.

    WHY NO ALT TEXT IS CARRIED, WHICH LOOKS LIKE A MISSING FEATURE
    -------------------------------------------------------------
    The obvious move is to ship each picture's published alt text alongside
    it. That was built first, and then the alt text was checked against the
    pictures, which is the step that had never happened anywhere in this
    pipeline.

    site/assets/zones/kitchen--sink-and-dishwashing-zone-md.jpg is a wide run
    of wood counter under two windows, with a sink, a dishwasher and a plant.
    Its alt text, live on the zone page today, is "a wiped drain flange".
    There is no drain flange in the image.

    It is not a one-off. `figure()` in wire_zone_heroes.py builds alt from the
    GENERATION SUBJECT, which is the prompt the picture was asked for, not a
    description of the picture that came back. So 26 of the 110 read as
    instructions rather than as scenes: "Every pan comes out, lids in a rack",
    "one category each", "one in use, one in the wash". ops/hero-verdicts.json
    certifies that somebody looked at the PICTURE and approved it. Nothing has
    ever certified the SENTENCE.

    Announcing a picture as something it is not is the accessibility version
    of a fabricated before and after, and shipping 110 of them into an app on
    the strength of a review that was never about them is not a trade worth
    making.

    So the app carries the stem and nothing else. In every place these appear
    the zone name is visible text within a few pixels of the picture, which
    makes the picture decorative in the WCAG sense: alt="" is not a gap there,
    it is the correct value, and it is the only one that is certainly true.
    The one image with a real description is the first-run picture in
    quest.html, written by opening the file and looking at it.

    Fixing the zone pages' own alt text is a real and separate job, owned by
    ops/wire_zone_heroes.py, and it needs somebody to look at 110 pictures.
    """
    # hero-fallback.json is the record of what is actually wired onto a
    # published zone page. Requiring membership there as well as an "ok"
    # verdict means the app can never be the only place a picture appears,
    # which would put an image in front of a customer that no page has ever
    # shown and no reviewer has seen in context.
    out = set()
    for stem in sorted(approved_and_published()):
        # Every width and format the app can ask for has to be on disk. A
        # <source> naming a file that is not there is a broken image in every
        # browser that prefers that format, and browsers do not report it.
        if all(os.path.exists(os.path.join(ZONE_IMG, f"{stem}-{t}.{e}"))
               for t in ("sm", "md", "lg") for e in ("avif", "webp", "jpg")):
            out.add(stem)
    return out


def display(room: str, zone: str) -> str:
    return NAME_MAP.get(f"{room}|{zone}", zone)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _clean(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


def _norm_symptom(s: str) -> str:
    """Same case fix as ops/build_zone_pages.py's own `_norm_symptom`: the
    Kitchen frictions store a card title in capitals, which reads as
    shouting on a screen. Display-only; the corpus itself is untouched.
    Duplicated rather than imported, because build_zone_pages.py runs heavy
    module-level I/O on import and this file only needs six lines of it.
    """
    s = (s or "").strip()
    if s and s == s.upper():
        s = s.lower()
        s = s[:1].upper() + s[1:]
        s = re.sub(r"\bi\b", "I", s)
    return s.rstrip(".")


# THE SYMPTOM ENTRY SCREEN (PLAN-MICROZONES-DECKS-APP.md 4.3, item A3;
# BACKLOG-2026-09-07.md A5, "the app's first thirty seconds").
#
# A stranger recognises a symptom before they choose a room. Real frictions,
# picked by hand for spread across rooms rather than generated, each (room,
# zone, friction index, branch index) into that zone's own content.json
# diagnosis block. Nothing here is paraphrased: the symptom, the cause and
# the two-minute action are all direct fields, resolved the same way
# diagnosis_html() resolves them on the zone page itself. The last option,
# "show me the house instead", is the app's original first-run screen; see
# quest.js.
#
# Widened 2026-11-16, scheduled operator cycle: from 5 entries across 2 of
# the 20 rooms (Entryway, Kitchen) to 13 across 10. `STATUS.md` section 8's
# own "Personal Function Discovery" row had read "IMPLEMENTED for 5 zones...
# the rest fall through to browsing by room" since 2026-09-20, correctly
# labelled, never picked up as the gap it names: a stranger whose friction
# lives in any of the other 18 rooms got no symptom-first match at all,
# even though every one of the other 114 zones already carries the same
# `diagnosis` block this screen reads from (confirmed live before picking
# candidates: 0 of 114 zones lack a `passes` entry for all six S's, and
# every zone below has a non-empty `frictions`/`first_15`). The render path
# needed no change to take more: `#sym-list` (quest.html) is an empty list
# populated by `renderSymptomList()` (quest.js) from `Q.symptoms`, one
# `<button data-sym="i">` per entry with no fixed count anywhere in the
# markup or the click handler (`[data-sym]`, parsed by index); the
# "hardcodes five option buttons" comment this file's own `main()` carried
# was already stale before this change; the only real constraint was `#sym-
# list`'s `flex-direction:column` layout, which scales to 13 short rows on
# a phone screen without redesign (checked against the CSS directly, not
# assumed). The 8 new picks were read from each room's own first-listed
# friction (content.json's `diagnosis.frictions[0]`), not invented, choosing
# the single zone per room whose symptom text was shortest and most
# recognisable on first read, same bar the original 5 set (Kitchen's "THE
# SINK IS FULL AGAIN BY EVENING" shape): Primary Bathroom's vanity counter,
# Home Office's desk, Garage's workbench and Laundry Room's washer mirror
# that same "it is covered/full again" shape; Living Room's sofa, Primary
# Bedroom's dresser drawer and Dining Room's table are the next clearest
# single-sentence frictions in their own rooms; Hall Closet's cleaning-
# supply zone was picked over its own shorter candidates specifically
# because it is a Safety-pass friction (CLAUDE.md D-014, Safety the fourth
# S), giving the list its first non-Straighten/Shine cause and matching
# CLAUDE.md 0.7's P0 priority on safety over polish.
#
# Widened again 2026-11-16, scheduled operator cycle: from 13 entries across
# 10 of the 20 rooms to 23 across all 20. The remaining 10 (Pantry, Family
# Room, Guest Bedroom, Kids Bedroom, Nursery, Guest Bathroom, Workshop,
# Mudroom, Stair Landing, Patio or Deck) each had every zone's own first
# friction read by hand (content.json's `diagnosis.frictions[0]`, not a
# second or later branch, not invented), and the shortest, most recognisable
# single-sentence symptom in each room picked, the same bar the first
# widening set, with a lean toward a genuine Safety-pass friction where one
# was both short and recognisable rather than always defaulting to the
# shortest Sort/Straighten line: Kids Bedroom's loose blind cord near the
# pillow, Guest Bathroom's low-mounted reserve roll and Workshop's sticking
# blade guard are all Safety-pass causes, not picked for length alone. Every
# one of the 10 new entries was verified live before shipping (symptom,
# branch answer, first_15 action and victory text all non-empty, read
# directly from content.json, not assumed) rather than guessed from the
# symptom text alone.
#
# Widened a third time 2026-11-17, scheduled operator cycle: from 23 entries
# (one per room, three rooms with more) to 40, a second entry for every room
# that still had only one (all but Entryway and Kitchen). A166/A167 defined
# "done" as at least one entry per room so a stranger's own words match
# somewhere in every room; this is the next genuine increment, not a redo of
# that lane, since each pick names a different zone the first entry could
# not reach. Same picking bar: the second zone's own `frictions[0]` symptom,
# shortest and most recognisable among that room's remaining zones, with a
# lean toward a real Safety-pass cause when one was close in length rather
# than always the shortest Sort/Straighten line. Four of the seventeen new
# picks are genuinely Safety-pass (CLAUDE.md D-014): Family Room's throw
# left drying on a hot radiator, Primary Bedroom's loose medication in the
# nightstand, Kids Bedroom's overstuffed drawer that yanks a child off
# balance, and Workshop's unchecked extinguisher gauge. Garage's leaning
# long-handled tools and Patio or Deck's own "Safety Zone" name both read
# as Safety on the zone name alone but their actual root-cause tag in
# content.json is Sort, confirmed before shipping rather than assumed from
# the zone's name; recorded here so a future cycle does not miscite them.
# Every one of the 17 new entries was verified live before shipping the
# same way as every prior widening (symptom, branch answer, first_15 action
# and victory text and a real cause ID, all non-empty, read directly from
# content.json).
#
# Found and fixed 2026-11-17, same cycle: that widening's own commit and
# log entry both claimed "a second entry for all 18 single-entry rooms
# (every room but Entryway and Kitchen)" and counted 40 total, but
# Primary Bathroom was left at one entry (Vanity Counter only), the exact
# "source corrected, sibling never told" shape BACKLOG-2026-09-07.md
# section 7 names as this repository's dominant defect class. Counted the
# list directly rather than trust the claim: 40 rows, 19 rooms at 2 (or
# more), Primary Bathroom alone at 1. Added a second entry the same way as
# every other room: of Primary Bathroom's six still-unused zones, only one
# friction's own first branch (bi=0) carries a genuine Safety root cause
# (KC-006, POOR ACCESSIBILITY) rather than Sort/Straighten/Shine/Standardize/
# Sustain, checked directly against ops/root_causes.py rather than assumed
# from wording: Linen and Towel Storage's third friction, "Pulling one
# towel out brings the stack down, or I need a stool to reach it," a real
# fall risk, not merely longer than that zone's own shortest (Sort) friction.
# Picked it over the next-shortest alternative (Medicine Cabinet or Wall
# Storage's "we cannot find something in an emergency," whose own first
# branch scores Straighten, not Safety) for the same reason A168 leaned
# Safety elsewhere: a real hazard outranks a merely shorter convenience
# symptom. Verified live before shipping: symptom, branch answer, and
# first_15 action/victory all non-empty, read directly from content.json.
#
# Widened a fourth time 2026-11-17, scheduled operator cycle: a third
# entry for every one of the 18 rooms the prior widening left at exactly
# two (all but Entryway, already at 2 of 5 zones, and Kitchen, already at
# 3 of 4), 41 entries to 59. For each room, read every remaining zone's
# own frictions[*] by hand, checked each candidate's first branch (bi=0)
# against ops/root_causes.py rather than assumed from wording, and picked
# the shortest, most recognisable symptom, leaning Safety only when a
# Safety-pass candidate was close in length (judged case by case, not a
# fixed percentage) to the shortest non-Safety one in that same room; a
# Safety candidate that was merely available but far longer than the
# room's shortest option was declined rather than forced (Dining Room,
# Hall Closet, Guest Bedroom all had a genuine Safety-pass friction in
# their remaining zones that was 30 to 80 percent longer than the room's
# actual shortest; none was picked). 12 of the 18 new picks are genuine
# Safety-pass causes (D-014): Home Office's leaning bookshelf, Garage's
# fire-or-poisoning-risk shelf, Laundry Room's child-reachable chemical,
# Living Room's loose tablets in a child's reach, Primary Bedroom's water
# glass beside a power strip, Family Room's overheating tablet under a
# blanket, Kids Bedroom's overloaded extension strip with a water bottle
# at the same end, Nursery's heavy carton over the crib, Guest Bathroom's
# missing bath mat and grab bar, Workshop's unseparated solvent and
# water-based paint cans, Mudroom's child-height flea treatment, and
# Patio or Deck's wet-board extension lead. The other six (Primary
# Bathroom, Dining Room, Hall Closet, Pantry, Guest Bedroom, Stair
# Landing) had no comparably short Safety-pass candidate in their
# remaining zones, so each took its room's genuinely shortest, most
# recognisable remaining friction instead, honestly tagged Standardize,
# Shine, Sort or Sort rather than stretched to Safety. Every one of the
# 18 new entries verified live before shipping, the same way as every
# prior widening: symptom, branch answer, and first_15 action/victory
# text all non-empty, read directly from content.json.
#
# A171, 2026-11-17, PM check-in: Entryway's third entry, the last room
# left below the 3-per-room bar every other room already cleared. Of its
# three remaining zones, the Entry Console or Bench drawer's one genuine
# Safety-pass friction ("batteries, coins, and small things end up loose
# in the back corners of the drawer," KC-010) was 82 chars against the
# room's shortest non-Safety option at 57, 44 percent longer, inside the
# same 30 to 80 percent band already declined for Dining Room, Hall
# Closet and Guest Bedroom above, so it was declined here too and the
# shortest, most recognisable friction was picked instead: the same zone's
# own first friction, "the drawer fills back up within a month of being
# emptied" (KC-002, Straighten).
SYMPTOM_PICKS = [
    ("Entryway", "Landing Zone", 1, 0),
    ("Entryway", "Coat and Outerwear Zone", 0, 0),
    ("Entryway", "Entry Console or Bench", 0, 0),
    ("Kitchen", "Primary Prep Counter", 0, 0),
    ("Kitchen", "Utensil and Utility Drawers", 0, 0),
    ("Kitchen", "Sink and Dishwashing Zone", 0, 0),
    ("Primary Bathroom", "Vanity Counter", 0, 0),
    ("Primary Bathroom", "Linen and Towel Storage", 2, 0),
    ("Home Office", "Primary Desk", 0, 0),
    ("Home Office", "Printer and Scanning Station", 0, 0),
    ("Garage", "Primary Workbench", 0, 0),
    ("Garage", "Lawn and Garden Tool Zone", 0, 0),
    ("Laundry Room", "Washer and Dryer", 0, 0),
    ("Laundry Room", "Hanging and Air-Dry Zone", 0, 0),
    ("Living Room", "Sofa and Seating Zone", 0, 0),
    ("Living Room", "Floor and Circulation Path", 0, 0),
    ("Primary Bedroom", "Dresser Drawers", 0, 0),
    ("Primary Bedroom", "Nightstand Right", 0, 0),
    ("Dining Room", "Dining Table", 0, 0),
    ("Dining Room", "Beverage or Coffee Station", 0, 0),
    ("Hall Closet", "Cleaning Supply Zone", 0, 0),
    ("Hall Closet", "Paper and Household Backstock", 0, 0),
    ("Pantry", "Canned and Jarred Goods", 0, 0),
    ("Pantry", "Snack and Lunch Zone", 0, 0),
    ("Family Room", "Board Game and Puzzle Zone", 0, 0),
    ("Family Room", "Blanket and Comfort Zone", 0, 0),
    ("Guest Bedroom", "Guest Closet", 0, 0),
    ("Guest Bedroom", "Guest Dresser", 0, 0),
    ("Kids Bedroom", "Bed and Sleep Zone", 0, 0),
    ("Kids Bedroom", "Dresser Drawers", 0, 0),
    ("Nursery", "Baby Clothing Zone", 0, 0),
    ("Nursery", "Books and Quiet Play Zone", 0, 0),
    ("Guest Bathroom", "Toilet Area", 0, 0),
    ("Guest Bathroom", "Guest Vanity Counter", 0, 0),
    ("Workshop", "Power Tool Storage", 0, 0),
    ("Workshop", "Safety and PPE Station", 0, 0),
    ("Mudroom", "Cleaning and Utility Zone", 0, 0),
    ("Mudroom", "Seasonal Outdoor Gear", 0, 0),
    ("Stair Landing", "Landing Surface or Console", 0, 0),
    ("Stair Landing", "Stair and Floor Path", 0, 0),
    ("Patio or Deck", "Garden and Plant Care Zone", 0, 0),
    ("Patio or Deck", "Surface, Rail, and Safety Zone", 0, 0),
    ("Primary Bathroom", "Toilet Area", 1, 0),
    ("Home Office", "Bookshelf and Reference Zone", 2, 0),
    ("Garage", "Automotive Care Zone", 3, 0),
    ("Laundry Room", "Detergent and Treatment Zone", 2, 0),
    ("Living Room", "Side Tables and Lighting", 1, 0),
    ("Primary Bedroom", "Nightstand Left", 1, 0),
    ("Dining Room", "China or Display Cabinet", 2, 0),
    ("Hall Closet", "Cleaning Equipment Zone", 1, 0),
    ("Pantry", "Baking Zone", 1, 0),
    ("Family Room", "Charging and Device Zone", 2, 0),
    ("Guest Bedroom", "Guest Bed and Linens", 1, 0),
    ("Kids Bedroom", "Study Desk", 1, 0),
    ("Nursery", "Diaper and Care Backstock", 1, 0),
    ("Guest Bathroom", "Shower or Tub", 2, 0),
    ("Workshop", "Finishing and Chemical Zone", 2, 0),
    ("Mudroom", "Pet Station", 1, 0),
    ("Stair Landing", "Wall and Display Zone", 1, 0),
    ("Patio or Deck", "Outdoor Dining Zone", 1, 0),
]


def build_symptoms(raw_rooms: list, zone_lookup: dict) -> list:
    out = []
    for room, zone, fi, bi in SYMPTOM_PICKS:
        raw_room = next(r for r in raw_rooms if r["room"] == room)
        raw_zone = next(z for z in raw_room["zones"] if z["zone"] == zone)
        diag = raw_zone["diagnosis"]
        fr = diag["frictions"][fi]
        br = fr["branches"][bi]
        cause = root_causes.BY_ID[br["cause"]]
        first15 = diag["first_15"]
        built = zone_lookup[(room, zone)]
        out.append({
            "symptom": _norm_symptom(fr["symptom"]),
            "room": room,
            "zone": zone,
            "why": _clean(br["answer"]),
            "sixS": cause["six_s"],
            "action": _clean(first15["action"]),
            "victory": _clean(first15["victory"]),
            "img": built.get("img"),
            "url": built["url"],
        })
    return out


def build_data() -> tuple[str, dict]:
    d = json.load(io.open(SRC, encoding="utf-8"))
    art = heroes()
    vids = published_videos()
    rooms, cards, pictured, videoed = [], 0, 0, 0

    for r in d["rooms"]:
        zones = []
        for z in r["zones"]:
            passes = z.get("passes") or {}
            steps = [{"s": s, "text": passes[s]} for s in SIX if passes.get(s)]
            if not steps:
                continue
            cards += len(steps)
            leave = z.get("leave_behind") or {}
            call = z.get("the_call") or {}
            zones.append({
                "zone": z["zone"],
                "session": z.get("session", ""),
                "purpose": z.get("purpose", ""),
                "done": z.get("done_looks_like", ""),
                "steps": steps,
                # The judgement call is the thing people get stuck on, so it
                # rides with the zone rather than being buried on a web page.
                "call": {"title": call.get("title", ""), "text": call.get("text", "")}
                        if call.get("text") else None,
                "watch": [{"q": w.get("question", ""), "t": w.get("text", "")}
                          for w in (z.get("watch_for") or []) if w.get("text")],
                "standard": leave.get("standard", ""),
                "trigger": leave.get("trigger", ""),
                "url": f"/zones/{slug(r['room'])}-{slug(display(r['room'], z['zone']))}",
            })
            # The same stem wire_zone_heroes.py names its files with:
            # the room slug, two dashes, the RAW zone name from this very
            # file. Derived, not guessed, and then checked against the disk
            # in heroes() above, so a rename on either side drops the picture
            # instead of shipping a dead reference.
            stem = f"{slug(r['room'])}--{slug(z['zone'])}"
            if stem in art:
                zones[-1]["img"] = stem
                pictured += 1
            # The zone's own published video, for the 12 that have one. A link
            # only: nothing is requested from YouTube until somebody presses it,
            # which is the same promise the zone pages make.
            if stem in vids:
                zones[-1]["video"] = vids[stem]
                videoed += 1
        if zones:
            rooms.append({"room": r["room"], "slug": slug(r["room"]), "zones": zones})

    zone_lookup = {(r["room"], z["zone"]): z for r in rooms for z in r["zones"]}
    symptoms = build_symptoms(d["rooms"], zone_lookup)

    payload = {"rooms": rooms, "six": SIX, "colours": COLOURS, "purpose": PURPOSE,
               "symptoms": symptoms}
    js = ("/* Auto-generated by ops/build_quest.py from the Micro Zone Manual.\n"
          "   Do not edit. Change content.json and rebuild. */\n"
          "window.QUEST = " + json.dumps(payload, ensure_ascii=False,
                                         separators=(",", ":")) + ";\n")

    # The symptom picker (quest.html's first screen for a new visitor) only
    # ever reads symptoms/six/colours/purpose, never rooms, which is 99.9% of
    # this payload's bytes (432 KB of 429 KB total, measured 2026-09-28). A
    # small sibling file carrying only what that first screen needs lets
    # quest.js show it without waiting on the full manual; quest.js loads
    # this real quest-data.js lazily afterward, on the first interaction that
    # actually needs a room. Same shape, same window.QUEST name, so a stale
    # cached copy of one without the other still assigns something quest.js
    # can check for truthiness; the "rooms" key is simply absent until the
    # lazy load replaces the whole object.
    small_payload = {"six": SIX, "colours": COLOURS, "purpose": PURPOSE,
                      "symptoms": symptoms}
    small_js = ("/* Auto-generated by ops/build_quest.py from the Micro Zone "
                "Manual.\n   Do not edit. Change content.json and rebuild.\n"
                "   The symptom picker's eager payload only: no rooms. quest.js "
                "loads the full quest-data.js lazily on first need. */\n"
                "window.QUEST = " + json.dumps(small_payload, ensure_ascii=False,
                                                separators=(",", ":")) + ";\n")

    return js, small_js, {"rooms": len(rooms),
                "zones": sum(len(r["zones"]) for r in rooms),
                "cards": cards, "pictured": pictured, "videoed": videoed,
                "kb": len(js.encode()) // 1024,
                "small_kb": len(small_js.encode()) // 1024}


def main() -> int:
    js, small_js, stats = build_data()
    out = os.path.join(SITE, "assets", "js", "quest-data.js")
    io.open(out, "w", encoding="utf-8", newline="").write(js)
    small_out = os.path.join(SITE, "assets", "js", "quest-data-symptoms.js")
    io.open(small_out, "w", encoding="utf-8", newline="").write(small_js)
    print(f"  quest-data.js  {stats['rooms']} rooms, {stats['zones']} zones, "
          f"{stats['cards']} cards, {stats['kb']} KB")
    print(f"  quest-data-symptoms.js  {stats['small_kb']} KB, the symptom "
          f"picker's eager payload, no rooms")
    print(f"  pictures       {stats['pictured']} of {stats['zones']} zones carry "
          f"a reviewed image; the rest render text, as they always did")
    print(f"  videos         {stats['videoed']} of {stats['zones']} zones carry a "
          f"published video id; the app links it, and requests nothing from "
          f"YouTube until somebody presses it")

    # Guard the two claims the whole method rests on. A generated file is
    # exactly where a quiet reordering would survive unnoticed.
    data = json.loads(js[js.index("{"):js.rindex(";")])
    assert data["six"] == SIX, "the six S's are out of canonical order"
    assert data["six"][3] == "safety", "Safety must be the fourth S"
    print("  canon        Safety is the fourth S, order asserted")

    # The symptom entry screen (quest.html's #symptom-step) hardcodes five
    # option buttons, one per SYMPTOM_PICKS entry. A short payload here would
    # leave buttons with nothing to bind to; a long one would leave buttons
    # silently unfilled. Either is worse than failing the build.
    assert len(data["symptoms"]) == len(SYMPTOM_PICKS), (
        f"expected {len(SYMPTOM_PICKS)} symptoms, got {len(data['symptoms'])}")
    for s in data["symptoms"]:
        assert s["symptom"] and s["why"] and s["action"] and s["victory"], (
            f"symptom entry for {s.get('zone')} is missing a required field")
    print(f"  symptoms     {len(data['symptoms'])} real frictions wired to the "
          f"entry screen, each naming a zone and a cause")

    # A COUNT THAT DROPS QUIETLY IS THE DEFECT, NOT THE SYMPTOM
    #
    # Two consecutive runs of this file, minutes apart, with no edit of its
    # own between them, printed 110 pictures and then 107. That turned out to
    # be correct: another process had rewritten ops/hero-verdicts.json in the
    # interval and withdrawn approval for three images, and this file honoured
    # it immediately, which is exactly what it should do.
    #
    # But nothing said so. 107 pictures is a perfectly valid file, every
    # downstream check passes on it, and a build that had instead dropped
    # three because a derivative was half-written during a concurrent encode
    # would have looked identical. That is the failure shape this repository
    # has paid for more than any other: a partial result indistinguishable
    # from a complete one.
    #
    # So the two causes are separated. `expected` comes from the approval
    # record alone and never looks at the disk; `shipped` is what actually
    # made it into the payload. A withdrawn approval moves both together and
    # is silent, correctly. A missing or unreadable file moves only one, and
    # is named and fails the build. Rerunning costs seconds.
    expected = approved_and_published()
    shipped = {z["img"] for r in data["rooms"] for z in r["zones"] if z.get("img")}
    short = sorted(expected - shipped)
    if short:
        print(f"  BROKEN       {len(short)} approved picture(s) did not make it "
              f"into the app, so this build would silently ship fewer than the "
              f"site shows. Usually a file was being rewritten; run it again.")
        for stem in short[:5]:
            print(f"                 {stem}")
        return 1
    print(f"  pictures     all {len(expected)} approved and published image(s) "
          f"present, counted against ops/hero-verdicts.json, not trusted")


    missing = []
    for r in data["rooms"]:
        for z in r["zones"]:
            page = os.path.join(SITE, z["url"].lstrip("/").replace("/", os.sep) + ".html")
            if not os.path.exists(page):
                missing.append(z["url"])
    if missing:
        print(f"  BROKEN       {len(missing)} zone link(s) point at no page:")
        for u in missing[:5]:
            print(f"                 {u}")
        return 1
    print(f"  links        all {stats['zones']} zone links resolve to a real page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
