#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_intro_call_current() catches the defect
class REVIEW-COMMERCE-2026-09-07.md C10 exists to close: the service line
had no pre-payment conversion event, only a $250/$1,200 payment or a
blank contact form. Fixed 2026-09-22 with a free, capped, 15-minute
"which zone first" call: a new #intro-call section on consulting.html
(the composed-mailto pattern contact.html already uses, so no mail pipe
is required) and a plain-text link to it from every zone and room page's
existing consult CTA, carrying the same from=<type>:<slug> origin
convention the paid consult button already uses.

Also runs against the real, committed site/consulting.html, site/zones/
and site/rooms/ files, so a future hand edit, a regeneration that drops
the link, or a rewrite that quietly removes the stated cap or the
"not a booking" language fails this test directly.

Run:  python ops/tests/test_gate_intro_call_current.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD_CONSULTING = """
<div id="intro-call">
  <p>We take up to 5 of these a week.</p>
  <form id="intro-call-form">
    <input id="ic-name">
    <input id="ic-email">
    <input id="ic-room">
  </form>
  <p>This is a request, not a booking.</p>
  <script>window.Measure.track("intro-call-request", {});</script>
</div>
"""

GOOD_ZONE_LINK = ('<p><a href="../consulting.html?from=zone:'
                   'entryway-the-landing-spot#intro-call">'
                   'Ask which zone first, free</a></p>')

GOOD_ROOM_LINK = ('<p><a href="../consulting.html?from=room:entryway'
                   '#intro-call">Ask which zone first, free</a></p>')


def main() -> int:
    fails = []

    # 1. Clean set: no problems.
    pages = {
        "zone": {"entryway-the-landing-spot.html": GOOD_ZONE_LINK},
        "room": {"entryway.html": GOOD_ROOM_LINK},
    }
    problems = preflight.check_intro_call_current(GOOD_CONSULTING, pages)
    if problems:
        fails.append("clean set flagged: %s" % problems)

    # 2. The section is missing entirely from consulting.html.
    problems = preflight.check_intro_call_current(
        "<p>nothing here</p>", pages)
    if not any('no id="intro-call" section' in p for p in problems):
        fails.append("missing section not caught: %s" % problems)

    # 3. The section exists but the stated cap has been quietly removed.
    no_cap = GOOD_CONSULTING.replace(
        "<p>We take up to 5 of these a week.</p>", "")
    problems = preflight.check_intro_call_current(no_cap, pages)
    if not any("no stated weekly cap" in p for p in problems):
        fails.append("missing cap not caught: %s" % problems)

    # 4. The "not a booking" language has been quietly removed, which is
    #    exactly C10's own acceptance line: "nothing about it implies a
    #    booked appointment that has not been agreed."
    no_booking_line = GOOD_CONSULTING.replace(
        "<p>This is a request, not a booking.</p>", "")
    problems = preflight.check_intro_call_current(no_booking_line, pages)
    if not any('not a booking" language' in p for p in problems):
        fails.append("missing 'not a booking' language not caught: %s" % problems)

    # 5. A required form field has been dropped.
    no_room_field = GOOD_CONSULTING.replace('<input id="ic-room">', "")
    problems = preflight.check_intro_call_current(no_room_field, pages)
    if not any('id="ic-room"' in p for p in problems):
        fails.append("missing field not caught: %s" % problems)

    # 6. The tracking call has been dropped.
    no_tracking = GOOD_CONSULTING.replace(
        'window.Measure.track("intro-call-request", {});', "")
    problems = preflight.check_intro_call_current(no_tracking, pages)
    if not any("no intro-call-request tracking call" in p for p in problems):
        fails.append("missing tracking call not caught: %s" % problems)

    # 7. A zone page's link has been stripped.
    pages_stripped = {
        "zone": {"entryway-the-landing-spot.html": "<p>nothing here</p>"},
        "room": {"entryway.html": GOOD_ROOM_LINK},
    }
    problems = preflight.check_intro_call_current(GOOD_CONSULTING, pages_stripped)
    if not any("no free \"which zone first\" link" in p for p in problems):
        fails.append("stripped zone link not caught: %s" % problems)

    # 8. A room page carries a zone-typed origin by mistake (the wrong
    #    from= prefix for its own page type).
    wrong_type = GOOD_ROOM_LINK.replace("from=room:", "from=zone:")
    pages_wrong_type = {
        "zone": {"entryway-the-landing-spot.html": GOOD_ZONE_LINK},
        "room": {"entryway.html": wrong_type},
    }
    problems = preflight.check_intro_call_current(GOOD_CONSULTING, pages_wrong_type)
    if not any("expected" in p for p in problems):
        fails.append("wrong origin type not caught: %s" % problems)

    # 9. Real site: the real committed consulting.html and every real
    #    zone/room page must already pass clean.
    cpath = os.path.join(ROOT, "site", "consulting.html")
    if not os.path.exists(cpath):
        print("  no real site found here; skipping the live-site case")
    else:
        real_consulting = io.open(cpath, encoding="utf-8", errors="replace").read()
        real_pages = {}
        for label, subdir, skip in (
            ("zone", "zones", {"index.html"}),
            ("room", "rooms", set()),
        ):
            files = {}
            for f in sorted(glob.glob(os.path.join(ROOT, "site", subdir, "*.html"))):
                name = os.path.basename(f)
                if name in skip or name.startswith("_"):
                    continue
                files[name] = io.open(f, encoding="utf-8", errors="replace").read()
            real_pages[label] = files
        problems = preflight.check_intro_call_current(real_consulting, real_pages)
        if problems:
            fails.append("real committed site is not clean: %s" % problems[:6])
        n = sum(len(v) for v in real_pages.values())
        print(f"  real site: consulting.html + {n} zone/room page(s) checked")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print(f"PASS ({9} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
