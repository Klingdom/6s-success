#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_room_time_current() catches the defect it
exists for: ops.build_zone_pages.room_time()'s old hrs() used Python's
round(), which breaks an exact tie (session minutes landing precisely on a
half-hour boundary) toward the nearest EVEN half-hour rather than the
nearest higher one. Nine of the twenty rooms' zone-session sums land on
such a tie; the visible "Added together..." sentence and its FAQPage
duplicate both silently understated the room by half an hour.

Also runs against the real, committed corpus and site/rooms/*.html, so a
future reversion to round() (or any other drift between the generator and
the shipped page) fails this test directly.

Run:  python ops/tests/test_gate_room_time_rounding_current.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bzp                                 # noqa: E402


def _page(lo, hi, n, room="Kitchen"):
    faq = ('{"acceptedAnswer": {"text": "Added together, the %d sessions '
           'come to about %s to %s hours for the whole %s. That is not one '
           'long day."}}' % (n, lo, hi, room.lower()))
    notice = ('<p class="notice"><b>Added together, the %d sessions below '
              'come to about %s to %s hours for the whole %s.</b> Rest.</p>'
              % (n, lo, hi, room.lower()))
    return "<h1>%s</h1>%s%s" % (room, notice, faq)


def main() -> int:
    fails = []

    # 1. Clean page: both the visible sentence and the FAQPage duplicate
    #    state the current (correct) values. No problems.
    pages = {"kitchen.html": _page("4.5", "7.5", 7)}
    problems = preflight.check_room_time_current(
        {"kitchen": ("4.5", "7.5", 7)}, pages)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. Regression: the pre-fix round()-to-even shape, understating the
    #    high end by half an hour (7.5 -> 7), on both the visible sentence
    #    and the FAQPage duplicate.
    regressed = {"kitchen.html": _page("4.5", "7", 7)}
    problems = preflight.check_room_time_current(
        {"kitchen": ("4.5", "7.5", 7)}, regressed)
    if len(problems) != 2:
        fails.append("round()-to-even regression (both copies wrong) NOT "
                     "caught as two problems: %s" % problems)

    # 3. Only the FAQPage copy drifted (a hand edit fixed the visible
    #    sentence but not its structured-data duplicate, or vice versa).
    half_stale = {"kitchen.html": _page("4.5", "7.5", 7).replace(
        "come to about 4.5 to 7.5 hours for the whole kitchen. That",
        "come to about 4.5 to 7 hours for the whole kitchen. That")}
    problems = preflight.check_room_time_current(
        {"kitchen": ("4.5", "7.5", 7)}, half_stale)
    if len(problems) != 1:
        fails.append("FAQPage-only drift NOT caught as exactly one "
                     "problem: %s" % problems)

    # 4. A room whose content.json parse failed (room_time() returns None).
    #    Must not be treated as a defect.
    problems = preflight.check_room_time_current(
        {"kitchen": None}, {"kitchen.html": "<h1>Kitchen</h1>"})
    if problems:
        fails.append("unparseable room (room_time() None) wrongly "
                     "flagged: %s" % problems)

    # 5. A room named in the corpus with no built file at all. Must not be
    #    treated as a defect (a different gate covers missing pages).
    problems = preflight.check_room_time_current(
        {"kitchen": ("4.5", "7.5", 7), "garage": ("7", "10.5", 6)}, pages)
    if problems:
        fails.append("room page missing from the built site wrongly "
                     "flagged: %s" % problems)

    # 6. hrs() itself: the nine documented tie points round up, not to
    #    even, and a handful of ordinary non-tie sums are unaffected.
    cases = [(75, 1.5), (435, 7.5), (195, 3.5), (255, 4.5), (615, 10.5),
             (270, 4.5), (90, 1.5), (285, 5.0), (405, 7.0)]
    for mins, want in cases:
        got = None
        r = {"room": "T", "zones": [{"session": "%d-%d min" % (mins, mins)}]}
        result = bzp.room_time(r)
        got = float(result[0])
        if got != want:
            fails.append("room_time() low-end for %d min: got %s, want %s"
                         % (mins, got, want))

    # 7. Against the real, committed corpus and site/rooms/*.html: proves
    #    all 20 room pages actually ship the current room_time() values
    #    today, including the nine tie-point rooms this fix corrected.
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    if len(rooms) != 20:
        fails.append("expected 20 rooms, found %d (has the corpus changed? "
                     "update this test's expectation deliberately if so)"
                     % len(rooms))
    expected_map = {bzp.slug(r["room"]): bzp.room_time(r) for r in rooms}
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_room_time_current(expected_map, real_pages)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    # 8. The nine documented tie-point rooms specifically must now say the
    #    round-half-up (lo, hi) pair, pinned here independently of
    #    room_time() itself, so a regression inside room_time() (not just
    #    template drift) is also caught. Hand-derived from each room's own
    #    zone sessions in content.json: Kitchen 270-435 min, Primary
    #    Bedroom 195-315, Guest Bedroom 165-255, Kids Bedroom 255-405,
    #    Primary Bathroom 255-405, Home Office 255-405, Garage 405-615,
    #    Stair Landing 75-120, Patio or Deck 270-435.
    tie_rooms = {
        "kitchen": ("4.5", "7.5"), "primary-bedroom": ("3.5", "5.5"),
        "guest-bedroom": ("3", "4.5"), "kids-bedroom": ("4.5", "7"),
        "primary-bathroom": ("4.5", "7"), "home-office": ("4.5", "7"),
        "garage": ("7", "10.5"), "stair-landing": ("1.5", "2"),
        "patio-or-deck": ("4.5", "7.5"),
    }
    for slug, (want_lo, want_hi) in tie_rooms.items():
        body = real_pages.get("%s.html" % slug, "")
        want = "about %s to %s hours for the whole" % (want_lo, want_hi)
        if want not in body:
            fails.append("%s.html does not visibly state the corrected "
                         "'%s'" % (slug, want))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: 8 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
