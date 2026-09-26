#!/usr/bin/env python3
"""
Prove ops/zone_supplies.py's render_room() never claims a room page has no
outbound retailer links when the list right below the claim carries some.

Found 2026-09-26, cold-read of zone_supplies.py. render() and
render_storage() both call `A.disclosure(amazon, True, prefix)` once they
have already confirmed at least one product on the page carries a link
(True there means "has_links", the affiliate.py docstring's own name for
the argument). render_room() instead called
`A.disclosure(amazon, bool(tracked), prefix)`, passing whether any link is
an APPROVED, paying link rather than whether any link exists at all. No
affiliate programme is approved today, so `tracked` is 0 on every one of
the 20 rooms, and every room page with any retailer link at all (all 20,
confirmed live) rendered affiliate.py's NO_LINK_HTML: "Nothing on this
page earns us anything ... not one product below carries a paying link",
whose own premise, per affiliate.py's own comment above PLAIN_LINK_HTML,
is that there is no link at all. site/rooms/entryway.html shipped this
exact text directly above nine live target.com/homedepot.com anchors.

This is the identical bug shape render()'s own docstring already
diagnoses and fixes for its own call site; render_room() just never got
the same fix.

Run:  python ops/tests/test_gate_room_kit_disclosure_honest.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import zone_supplies as zs                                     # noqa: E402

NO_LINK_CLAIM = "Nothing on this page earns us anything"


def main() -> int:
    fails = []

    zp = zs._zone_products()
    rooms = {}
    for key in zp:
        room, zone = key.split("||", 1)
        rooms.setdefault(room, []).append(zone)

    checked_a_room_with_links = False
    for room, zones in rooms.items():
        items = zs.room_kit(room, zones)
        if not items:
            continue
        links = sum(1 for r in items if r["kind"])
        if not links:
            continue
        checked_a_room_with_links = True
        out = zs.render_room(room, zones, room.lower())
        if NO_LINK_CLAIM in out:
            fails.append(
                f"{room}: render_room() claims no page link exists "
                f"('{NO_LINK_CLAIM}') while {links} product(s) on the "
                "same page carry a real outbound retailer link")

    if not checked_a_room_with_links:
        fails.append("no room with any linked product was found at all; "
                     "this test proves nothing without one")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: render_room() never claims a room page has no outbound "
          "retailer link while one is actually rendered on it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
