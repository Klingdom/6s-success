#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_room_deck_pages_counts_current() catches a
room deck page stating a card/zone/root-cause count, or naming its
zoneless action cards, in a way that no longer matches the room's own
ops/cardtext/<slug>-deck.json.

Found 2026-10-17, cold-reading ops/cardtext/*.py (never ledgered in
ops/cold_read_ledger.py's LANES, a subdirectory its "ops/*.py" glob cannot
see). gate_kitchen_deck_page_counts_current (2026-09-18) fixed this exact
defect class for Kitchen alone: a hand-written sentence in
build_kitchen_deck_page.py naming the whole-kitchen action cards, guarded
only by an `assert whole_ids == [...]` inside the generator. All 19 other
room decks were built afterward from the same template and carry the
identical unguarded risk: if a future content.json edit ever changes a
room's zoneless action-card set, that room's generator's own internal
assert fires, the generator crashes, and site/<room>-deck.html is simply
never rewritten, left byte-identical to HEAD. gate_generator_ownership only
diffs a generator's fresh output against the committed file, so an
unchanged file reads as a clean, undirtied tree, never as a caught
regression. This generalises the Kitchen fix to the other 19 rooms,
re-deriving independently of whether each room's generator can even run.

Tests the pure logic (check_room_deck_page_counts) with synthetic data,
then checks every real committed site/<room>-deck.html against its own
real committed ops/cardtext/<slug>-deck.json.

Run:  python ops/tests/test_gate_room_deck_page_counts.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def synthetic_cards(n_zones=2, n_causes=3, whole_ids=("GAA-015", "GAA-016",
                                                        "GAA-017")):
    cards = [{"id": "GR-001", "type": "ROOM CARD"}]
    for i in range(n_zones):
        cards.append({"id": "GZ-%03d" % i, "type": "ZONE CARD",
                      "zone": "Zone %d" % i})
    for i in range(n_causes):
        cards.append({"id": "GC-%03d" % i, "type": "ROOT CAUSE CARD"})
    for wid in whole_ids:
        cards.append({"id": wid, "type": "ACTION CARD", "zone": None})
    return cards


def clean_page(room, n_total, n_zones, n_causes, n_whole):
    words = {2: "two", 3: "three", 4: "four", 5: "five"}
    return (
        "<title>The %s Deck: %d cards</title>\n"
        "<meta name=\"description\" content=\"The Manual's real %s %s "
        "zones, ...\">\n"
        "<p>points at one of these %s, the same vocabulary.</p>\n"
        "<p>%s cards that are not one zone's job: a walk, a pass, a "
        "sweep.</p>"
        % (room, n_total, words[n_zones], room, words[n_causes],
           words[n_whole].capitalize())
    )


def main() -> int:
    fails = []

    # 1. Clean: the page's own prose matches the real, freshly-derived
    #    counts for a room genuinely in ROOM_DECK_WHOLE_IDS.
    cards = synthetic_cards(n_zones=2, n_causes=3)
    page = clean_page("Garage", len(cards), 2, 3, 3)
    problems = preflight.check_room_deck_page_counts("Garage", cards, page)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. The exact regression this gate exists for: the deck grew a third
    #    zone, but the shipped page still says "two Garage zones".
    cards3 = synthetic_cards(n_zones=3, n_causes=3)
    stale_page = clean_page("Garage", len(cards3), 2, 3, 3)
    problems = preflight.check_room_deck_page_counts(
        "Garage", cards3, stale_page)
    if not any("zone count" in p for p in problems):
        fails.append("a stale zone count was NOT caught: %s" % problems)

    # 3. The root-cause count drifted.
    cards4 = synthetic_cards(n_zones=2, n_causes=4)
    stale_page = clean_page("Garage", len(cards4), 2, 3, 3)
    problems = preflight.check_room_deck_page_counts(
        "Garage", cards4, stale_page)
    if not any("root-cause" in p for p in problems):
        fails.append("a stale root-cause count was NOT caught: %s" % problems)

    # 4. The whole-room card SET changed (a card swapped for a new id) even
    #    though the count stayed the same; both the hand-written sentence
    #    and ROOM_DECK_WHOLE_IDS now describe the wrong cards.
    cards5 = synthetic_cards(whole_ids=("GAA-015", "GAA-016", "GAA-099"))
    page5 = clean_page("Garage", len(cards5), 2, 3, 3)
    problems = preflight.check_room_deck_page_counts("Garage", cards5, page5)
    if not any("GAA-099" in p for p in problems):
        fails.append("a changed whole-room card set was NOT caught: %s"
                     % problems)

    # 5. A room with no recorded expected whole_ids at all is flagged
    #    rather than silently skipped.
    problems = preflight.check_room_deck_page_counts(
        "Not A Real Room", cards, page)
    if not any("no recorded expected" in p for p in problems):
        fails.append("an unregistered room was NOT flagged: %s" % problems)

    # 6. Real files: every room in ROOM_DECK_WHOLE_IDS, checked against its
    #    own real committed deck JSON and HTML page.
    checked = 0
    for room in preflight.ROOM_DECK_WHOLE_IDS:
        slug = room.lower().replace(" ", "-")
        deck_path = os.path.join(ROOT, "ops", "cardtext", "%s-deck.json" % slug)
        page_path = os.path.join(ROOT, "site", "%s-deck.html" % slug)
        if not (os.path.exists(deck_path) and os.path.exists(page_path)):
            continue
        checked += 1
        real_cards = json.load(io.open(deck_path, encoding="utf-8"))["cards"]
        real_page = io.open(page_path, encoding="utf-8",
                             errors="replace").read()
        problems = preflight.check_room_deck_page_counts(
            room, real_cards, real_page)
        if problems:
            fails.append("%s: real committed page does not match a live "
                         "re-derivation of the deck's own counts: %s"
                         % (room, problems))
    if checked == 0:
        print("  (skipped case 6: no real room deck files found here)")

    # 7. Every build_*_deck.py under ops/cardtext/ is at least covered by
    #    some mechanism named here, so a 21st room added later cannot ship
    #    silently unprotected the way all 19 did until this gate existed.
    all_rooms = set()
    for f in glob.glob(os.path.join(ROOT, "ops", "cardtext", "*-deck.json")):
        room = json.load(io.open(f, encoding="utf-8"))["room"]
        all_rooms.add(room)
    uncovered = [r for r in all_rooms
                 if r != "Kitchen" and r not in preflight.ROOM_DECK_WHOLE_IDS]
    if uncovered:
        fails.append("room deck(s) with no entry in ROOM_DECK_WHOLE_IDS, "
                     "unprotected by this gate: %s" % uncovered)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  gate_room_deck_pages_counts: 7/7 cases pass (%d real rooms "
          "checked)" % checked)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
