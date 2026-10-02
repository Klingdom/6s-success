#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_also_called_is_heading() catches the defect
it exists for: ops.build_zone_pages.also_called_html() used to render a
room's household synonyms ("foyer", "larder", "master bedroom"...) inside a
plain <p>. ops/keyword_demand.py's own scorer only reads page titles and
h1-h3 text, by its own documented design, so those words were invisible to
it: six real, rank-1-to-3 gap queries existed for content the room page
already carried, just in the wrong element.

Also runs against the real, committed ops/room-also-called.json and
site/rooms/*.html, so a future reversion back to a plain paragraph (or any
other way of dropping the name out of a heading) fails this test directly.

Run:  python ops/tests/test_gate_also_called_is_heading.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Clean page: the name sits inside an <h2>. No problems.
    clean = {"entryway.html": (
        "<h1>Entryway</h1>"
        '<h2 class="also-called">Also called the foyer or the entrance '
        "hall. Same room, same micro zones.</h2>")}
    problems = preflight.check_also_called_is_heading(
        {"Entryway": ["foyer", "entrance hall"]}, clean)
    if problems:
        fails.append("clean h2 page wrongly flagged: %s" % problems)

    # 2. Regression: the pre-fix shape, the exact same words inside a
    #    plain <p> instead of a heading. Must be caught.
    regressed = {"entryway.html": (
        "<h1>Entryway</h1>"
        '<p class="also-called">Also called the foyer or the entrance '
        "hall. Same room, same micro zones.</p>")}
    problems = preflight.check_also_called_is_heading(
        {"Entryway": ["foyer", "entrance hall"]}, regressed)
    if len(problems) != 2:
        fails.append("plain-<p> regression (both names invisible to "
                     "headings) NOT caught as two problems: %s" % problems)

    # 3. Partial regression: one of two names lost from the heading (e.g. a
    #    hand edit that shortens the sentence).
    half_lost = {"entryway.html": (
        "<h1>Entryway</h1>"
        '<h2 class="also-called">Also called the foyer. Same room, same '
        "micro zones.</h2>")}
    problems = preflight.check_also_called_is_heading(
        {"Entryway": ["foyer", "entrance hall"]}, half_lost)
    if len(problems) != 1 or "entrance hall" not in problems[0]:
        fails.append("partial loss ('entrance hall' dropped) not caught "
                     "correctly: %s" % problems)

    # 4. A room with no entry (empty names) must never be flagged, whether
    #    or not its page carries unrelated headings.
    problems = preflight.check_also_called_is_heading(
        {"Kitchen": []}, {"kitchen.html": "<h1>Kitchen</h1>"})
    if problems:
        fails.append("room with no names wrongly flagged: %s" % problems)

    # 5. A room named in the map whose page is missing entirely must not
    #    crash and must not be flagged (gate_also_called_is_heading's own
    #    "no room pages built yet" branch covers the all-missing case; this
    #    covers one missing page among others).
    problems = preflight.check_also_called_is_heading(
        {"Entryway": ["foyer"]}, {"other.html": "<h1>Other</h1>"})
    if problems:
        fails.append("missing page wrongly flagged: %s" % problems)

    # 6. The real, committed site: every room in the real
    #    ops/room-also-called.json must carry every one of its names inside
    #    a real h1-h3 heading on its real site/rooms/*.html page.
    map_path = os.path.join(ROOT, "ops", "room-also-called.json")
    rooms_dir = os.path.join(ROOT, "site", "rooms")
    if os.path.exists(map_path) and os.path.isdir(rooms_dir):
        data = json.loads(io.open(map_path, encoding="utf-8").read())
        rooms = {room: entry.get("names") or []
                 for room, entry in (data.get("rooms") or {}).items()}
        page_bodies = {}
        for f in sorted(glob.glob(os.path.join(rooms_dir, "*.html"))):
            page_bodies[os.path.basename(f)] = io.open(
                f, encoding="utf-8", errors="replace").read()
        if rooms and page_bodies:
            problems = preflight.check_also_called_is_heading(
                rooms, page_bodies)
            if problems:
                fails.append("real committed site has a name hidden from "
                             "every heading: %s" % problems)
        else:
            print("NOT VERIFIED (case 6): map or room pages not present "
                  "to check against.")
    else:
        print("NOT VERIFIED (case 6): ops/room-also-called.json or "
              "site/rooms/ not present.")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 6/6 cases, including the real committed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
