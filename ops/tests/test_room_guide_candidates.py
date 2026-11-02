#!/usr/bin/env python3
"""
Prove GUIDE_LESS_ROOMS in ops/room_guide_candidates.py is derived live from
ROOM_GUIDES rather than hand-copied. Found 2026-11-02: the hand-maintained
list still named "Kids Bedroom" the same cycle that room's guide shipped and
ROOM_GUIDES picked it up, so the tool kept scoring an already-answered room.
This test fails on a reintroduced hand-maintained list (it would list 20-12=8
rooms only by coincidence matching today's content; a stale manual list
drifts the next time a guide ships, this derived one cannot).

Run:  python ops/tests/test_room_guide_candidates.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_zone_pages as bzp                                   # noqa: E402
import room_guide_candidates as rgc                               # noqa: E402

failures = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


all_rooms = {r["room"] for r in
             json.loads(open(os.path.join(ROOT, "content/manual/source/content.json")).read())["rooms"]}
guided = set(bzp.ROOM_GUIDES.keys())
expected = sorted(all_rooms - guided)

check("GUIDE_LESS_ROOMS matches content.json minus ROOM_GUIDES",
      rgc.GUIDE_LESS_ROOMS == expected)
check("a room with a shipped guide is never in GUIDE_LESS_ROOMS",
      guided.isdisjoint(set(rgc.GUIDE_LESS_ROOMS)))
check("every guide-less room is a real room", set(rgc.GUIDE_LESS_ROOMS) <= all_rooms)
check("guide_less_rooms() is re-callable and stable",
      rgc.guide_less_rooms() == rgc.GUIDE_LESS_ROOMS)

if failures:
    print("\n%d FAILED: %s" % (len(failures), ", ".join(failures)))
    sys.exit(1)
print("\n%d/%d passed" % (4, 4))
