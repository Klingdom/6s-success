#!/usr/bin/env python3
"""
Prove every zone of every drawn room gets a "Where it is" locator plan.

ops/room_locator.py returns None, on purpose, when it cannot find a zone in
its room's drawing, so the zone page falls back to the list alone rather
than show the wrong place. That makes a broken layout silent: a zone would
just lose its plan. This fails instead, by name, and also checks that the
built zone pages actually carry the 74 plans.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_room_maps as B                                    # noqa: E402
import room_locator as R                                       # noqa: E402


def main():
    fails, n = [], 0
    for room, spec in B.ROOMS.items():
        for i, name in enumerate(spec[3]):
            n += 1
            svg = R.locator_svg(room, i, name)
            if not svg:
                fails.append("%s zone %d (%s) has no locator" % (room, i + 1,
                                                                 name))
                continue
            if svg.count('stroke-width="6"') != 1:
                fails.append("%s zone %d: expected exactly one highlight"
                             % (room, i + 1))
            if "<text" in svg:
                fails.append("%s zone %d: locator carries text" % (room, i + 1))
    if R.locator_svg("Kitchen", 0, "x") is not None:
        fails.append("a room with no drawn plan returned a locator")
    pages = glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))
    with_plan = sum(1 for p in pages
                    if 'class="zd-plan-svg"' in io.open(p, encoding="utf-8").read())
    if with_plan != n:
        fails.append("%d zone pages carry a locator plan, expected %d"
                     % (with_plan, n))
    if fails:
        print("FAIL: room_locator")
        for f in fails:
            print("  - " + f)
        return 1
    print("OK: room_locator, all %d zones of %d drawn rooms have exactly one "
          "highlighted plan, and %d zone pages carry it" % (n, len(B.ROOMS),
                                                           with_plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
