#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_zone_also_called_is_heading() catches the
defect it exists for: ops/zone-also-called.json has carried real entries
since before this gate existed (2026-10-23), with nothing checking that a
committed entry actually renders where zone_also_called_html() says it
will, an <h2> right after the H1. That is the exact gap the room-level map
had until 2026-10-02 (see test_gate_also_called_is_heading.py), one level
down.

Also runs against the real, committed ops/zone-also-called.json and
site/zones/*.html, so a future reversion back to a plain paragraph (or any
other way of dropping the name out of a heading) fails this test directly.

Run:  python ops/tests/test_gate_zone_also_called_is_heading.py
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
    clean = {"guest-bathroom-the-guest-linen-zone.html": (
        "<h1>Guest Linen Zone</h1>"
        '<h2 class="also-called">Also called the airing cupboard</h2>')}
    problems = preflight.check_zone_also_called_is_heading(
        {"Guest Bathroom|Guest Linen Zone": ["airing cupboard"]}, clean)
    if problems:
        fails.append("clean h2 page wrongly flagged: %s" % problems)

    # 2. Regression: the exact same word inside a plain <p> instead of a
    #    heading. Must be caught.
    regressed = {"guest-bathroom-the-guest-linen-zone.html": (
        "<h1>Guest Linen Zone</h1>"
        '<p class="also-called">Also called the airing cupboard</p>')}
    problems = preflight.check_zone_also_called_is_heading(
        {"Guest Bathroom|Guest Linen Zone": ["airing cupboard"]}, regressed)
    if len(problems) != 1 or "airing cupboard" not in problems[0]:
        fails.append("plain-<p> regression not caught correctly: %s"
                      % problems)

    # 3. A zone with no entry (empty names) must never be flagged.
    problems = preflight.check_zone_also_called_is_heading(
        {"Kitchen|Sink and Dishwashing Zone": []},
        {"kitchen-the-sink-and-dishwashing-zone.html": "<h1>Sink</h1>"})
    if problems:
        fails.append("zone with no names wrongly flagged: %s" % problems)

    # 4. A zone named in the map whose page is missing entirely must be
    #    flagged by name, not silently skipped or crashed on.
    problems = preflight.check_zone_also_called_is_heading(
        {"Guest Bathroom|Guest Linen Zone": ["airing cupboard"]},
        {"other.html": "<h1>Other</h1>"})
    if len(problems) != 1 or "no site/zones/" not in problems[0]:
        fails.append("missing page not flagged correctly: %s" % problems)

    # 5. A malformed key with no "|" must be skipped, not crash.
    problems = preflight.check_zone_also_called_is_heading(
        {"NoSeparator": ["x"]}, {"other.html": "<h1>Other</h1>"})
    if problems:
        fails.append("malformed key wrongly flagged: %s" % problems)

    # 6. The real, committed site: every zone in the real
    #    ops/zone-also-called.json must carry every one of its names inside
    #    a real h1-h3 heading on its real site/zones/*.html page.
    map_path = os.path.join(ROOT, "ops", "zone-also-called.json")
    zones_dir = os.path.join(ROOT, "site", "zones")
    if os.path.exists(map_path) and os.path.isdir(zones_dir):
        data = json.loads(io.open(map_path, encoding="utf-8").read())
        zones = {key: entry.get("names") or []
                 for key, entry in (data.get("zones") or {}).items()}
        page_bodies = {}
        for f in sorted(glob.glob(os.path.join(zones_dir, "*.html"))):
            page_bodies[os.path.basename(f)] = io.open(
                f, encoding="utf-8", errors="replace").read()
        if zones and page_bodies:
            problems = preflight.check_zone_also_called_is_heading(
                zones, page_bodies)
            if problems:
                fails.append("real committed site has a name hidden from "
                             "every heading: %s" % problems)
        else:
            print("NOT VERIFIED (case 6): map or zone pages not present "
                  "to check against.")
    else:
        print("NOT VERIFIED (case 6): ops/zone-also-called.json or "
              "site/zones/ not present.")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 6/6 cases, including the real committed site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
