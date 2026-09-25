#!/usr/bin/env python3
"""
Measure what a room deck would actually cost, by deriving everything the
corpus can already supply and reporting only what is genuinely left to author.

WHY THIS EXISTS RATHER THAN ANOTHER ESTIMATE
--------------------------------------------
BACKLOG-2026-09-07.md B7 was written on 2026-09-24 claiming five more room
decks would take about three days, on the reasoning that the diagnosis layer
now supplies a deck's hand-authored half. That reasoning was half right and
the number was wrong, and an over-optimistic estimate sitting in a backlog is
how a bad plan gets picked up later by somebody who trusts it.

What the diagnosis layer actually supplies is the friction cards' SYMPTOM and
their BRANCHES. A FRICTION CARD also needs a short all-caps title and a
one-line art brief, which are not in the corpus. A ZONE CARD needs a tagline,
six callouts and an art brief on top of what the Manual holds. ACTION, EVENT
and ROOM cards are almost entirely authored.

So this does not estimate. It derives, then counts the holes, per room, and
prints the total. A measured remaining cost can be argued with; an estimate
written from a hunch cannot.

It writes nothing into the deck corpus. Its output is a report, and a
machine-readable skeleton per room under build/deck-skeletons/ that an
authoring pass can fill in.

    python ops/cardtext/derive_room_deck.py                # every room
    python ops/cardtext/derive_room_deck.py "Primary Bathroom"
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUTDIR = os.path.join(ROOT, "build", "deck-skeletons")

sys.path.insert(0, os.path.join(ROOT, "ops"))

# DECK-GAME-DESIGN.md 4.1: 72 is not a preference. Print-on-demand prices in
# 18-card steps and 72 is exactly eight US Letter sheets at nine-up, so every
# slot is allocated and a new card type costs a whole print tier.
BUDGET = {"ROOM CARD": 1, "ZONE CARD": 7, "FRICTION CARD": 21,
          "ROOT CAUSE CARD": 12, "ACTION CARD": 18, "STANDARD CARD": 7,
          "EVENT CARD": 6}


def rooms() -> list:
    return json.load(io.open(SRC, encoding="utf-8"))["rooms"]


def derive(room: dict) -> dict:
    """Everything this room's corpus can already supply, plus the holes."""
    zones = room.get("zones") or []
    have, need = [], []

    zone_cards = []
    for i, z in enumerate(zones, 1):
        sd = z.get("shine_detail") or {}
        zone_cards.append({
            "zone": z["zone"],
            "order": i,
            # Derived, quoted from the Manual, never rewritten.
            "objective": z.get("purpose"),
            "done_looks_like": z.get("done_looks_like"),
            "session": z.get("session"),
            "safety_checks": (z.get("watch_for") or [])[:2],
            "the_call": z.get("the_call"),
            "supplies": sd.get("products_used"),
            # Authored. Not in the corpus in any form.
            "tagline": None,
            "callouts": None,          # six, and the art accept test counts them
            "art": None,
        })
    have.append(("ZONE CARD", len(zone_cards), "objective, done_looks_like, "
                 "session, safety_checks, the_call, supplies"))
    need.append(("ZONE CARD", len(zone_cards) * 3,
                 "tagline, six callouts, art brief, per zone"))

    standard_cards = []
    for i, z in enumerate(zones, 1):
        lb = z.get("leave_behind") or []
        standard_cards.append({
            "zone": z["zone"], "order": i,
            "leave_behind": lb,
            "micro_quests": None,      # DECK-GAME-DESIGN.md 4.1: three per card
        })
    have.append(("STANDARD CARD", len(standard_cards),
                 "the write-on sentence and its trigger"))
    need.append(("STANDARD CARD", len(standard_cards),
                 "three micro quests per card"))

    friction_cards = []
    for z in zones:
        diag = z.get("diagnosis") or {}
        for f in diag.get("frictions") or []:
            friction_cards.append({
                "zone": z["zone"],
                # Derived: this is what the 2026-09-24 authoring pass bought.
                "said": f.get("symptom"),
                "branches": [(b.get("answer"), b.get("cause"))
                             for b in f.get("branches") or []],
                # Authored.
                "title": None,
                "art": None,
            })
    if friction_cards:
        have.append(("FRICTION CARD", len(friction_cards),
                     "the symptom in household words, and every branch with "
                     "its real cause id"))
        need.append(("FRICTION CARD", len(friction_cards) * 2,
                     "an all-caps title and an art brief, per friction"))
    else:
        need.append(("FRICTION CARD", BUDGET["FRICTION CARD"] * 4,
                     "NO diagnosis layer in this room yet: symptom, branches, "
                     "title and art all have to be authored"))

    # first_15 gives one timed action per zone, with its own victory line.
    actions_derived = sum(
        1 for z in zones
        if ((z.get("diagnosis") or {}).get("first_15") or {}).get("action"))
    if actions_derived:
        have.append(("ACTION CARD", actions_derived,
                     "a 15-minute action and its victory condition, from "
                     "first_15"))
    need.append(("ACTION CARD", max(0, BUDGET["ACTION CARD"] - actions_derived),
                 "the remaining actions, with inputs and steps"))

    need.append(("EVENT CARD", BUDGET["EVENT CARD"],
                 "the ordinary hard day that tests the standard"))
    need.append(("ROOM CARD", BUDGET["ROOM CARD"], "the map and the rules"))

    # ROOT CAUSE cards are the same twelve in every room, already written.
    have.append(("ROOT CAUSE CARD", BUDGET["ROOT CAUSE CARD"],
                 "shared across every room, already written in "
                 "ops/root_causes.py"))

    return {"room": room["room"], "zones": len(zones),
            "zone_cards": zone_cards, "standard_cards": standard_cards,
            "friction_cards": friction_cards,
            "have": have, "need": need}


def main() -> int:
    want = sys.argv[1] if len(sys.argv) > 1 else None
    rs = [r for r in rooms() if not want or r["room"] == want]
    if not rs:
        print("  no room called %r in the corpus" % want)
        return 1
    os.makedirs(OUTDIR, exist_ok=True)

    print("  A deck is %d cards and every slot is allocated "
          "(DECK-GAME-DESIGN.md 4.1)." % sum(BUDGET.values()))
    print()
    print("  %-18s %6s %8s %8s  %s"
          % ("room", "zones", "derived", "to write", "biggest remaining piece"))
    tot_need = 0
    for r in rs:
        d = derive(r)
        n = sum(c for _t, c, _w in d["need"])
        tot_need += n
        derived = sum(c for _t, c, _w in d["have"])
        worst = max(d["need"], key=lambda x: x[1])
        print("  %-18s %6d %8d %8d  %s (%d)"
              % (d["room"], d["zones"], derived, n, worst[0], worst[1]))
        io.open(os.path.join(OUTDIR, "%s.json" % d["room"].lower().replace(" ", "-")),
                "w", encoding="utf-8", newline="\n").write(
            json.dumps(d, indent=1, ensure_ascii=False))

    print()
    print("  %d authored field(s) still needed across %d room(s)."
          % (tot_need, len(rs)))
    print("  Skeletons written to %s" % os.path.relpath(OUTDIR, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
