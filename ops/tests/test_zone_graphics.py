#!/usr/bin/env python3
"""
Prove ops/zone_graphics.py's zone diagram does not silently drop content.

Found 2026-09-18 (PM check-in): the footer's reset-trigger line drew only
wrap(...)[0], the first 92 characters, with the rest dropped and no
ellipsis. 70 of 114 real triggers need a second line. This file pins the
fix (the footer grows to fit every line) with a synthetic case and a real
plant-and-restore against the actual file, the same way
gate_zone_graphics_trigger_not_truncated re-derives it on every cycle.

Run:  python ops/tests/test_zone_graphics.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import video_zone as V                                             # noqa: E402
import zone_graphics as G                                          # noqa: E402


def main() -> int:
    fails = []

    # 1. A trigger long enough to need two lines must have BOTH lines
    #    present in the rendered SVG, not just the first.
    long_trigger = ("When you empty your pockets at the end of the day, "
                     "the tray takes all of it and the wood stays bare.")
    zone = {"zone": "Test Zone", "session": "15 min", "purpose": "A test.",
            "leave_behind": {"trigger": long_trigger}}
    svg = G.zone_diagram_svg("Test Room", zone, ["Test Zone"], ["Item one"],
                              uid="x")
    lines = G.wrap("Reset trigger: " + long_trigger, 92)
    if len(lines) < 2:
        fails.append("test fixture trigger did not need 2 lines; fix the "
                      "fixture, not the assertion")
    for ln in lines:
        if G.esc(ln) not in svg:
            fails.append(f"footer dropped a real line: {ln!r}")

    # 2. A short trigger (one line) still renders, footer stays compact.
    zone2 = dict(zone, leave_behind={"trigger": "Close the drawer."})
    svg2 = G.zone_diagram_svg("Test Room", zone2, ["Test Zone"], ["Item"],
                               uid="y")
    if G.esc("Reset trigger: Close the drawer.") not in svg2:
        fails.append("short trigger did not render in full")

    # 3. Every real trigger in content.json, in full, on the real diagram.
    zones = V.zones()
    rooms: dict = {}
    for room, z in zones:
        rooms.setdefault(room, []).append(z["zone"])
    needed_two_lines = 0
    offenders = []
    for room, z in zones:
        trigger = (z.get("leave_behind") or {}).get("trigger", "")
        if not trigger:
            continue
        svg = G.zone_diagram_svg(room, z, rooms[room], V.done_items(z),
                                  uid="pf")
        wlines = G.wrap("Reset trigger: " + trigger, 92)
        if len(wlines) > 1:
            needed_two_lines += 1
        for ln in wlines:
            if G.esc(ln) not in svg:
                offenders.append((room, z["zone"], ln))
                break
    if needed_two_lines < 50:
        fails.append(f"expected most of the 114 real zones to need a "
                      f"2-line trigger, only {needed_two_lines} did; the "
                      f"corpus may have changed under this test")
    if offenders:
        fails.append(f"{len(offenders)} real zone(s) drop trigger text, "
                      f"first: {offenders[0]}")

    # 4. Plant the pre-fix shape directly on the real file and confirm the
    #    gate's own re-derivation would have caught it, then confirm the
    #    committed file (the fixed version) is clean.
    src_path = os.path.join(ROOT, "ops", "zone_graphics.py")
    with open(src_path, encoding="utf-8") as f:
        real_src = f.read()
    if "trigger_lines" not in real_src:
        fails.append("zone_graphics.py no longer defines trigger_lines; "
                      "did the fix get reverted?")
    if 'wrap("Reset trigger: " + trigger, 92)[0]' in real_src:
        fails.append("zone_graphics.py still truncates the footer to "
                      "wrap(...)[0]; the fix did not land")

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print(f"OK  test_zone_graphics: 4/4 cases pass, {needed_two_lines}/114 "
          f"real zones confirmed needing and getting their full trigger "
          f"line")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
