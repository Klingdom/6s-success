#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_room_hub_current() catches the defect
classes REVIEW-DISCOVERY-2026-09-07.md D10 exists to hold: an H1 reverted
to the bare room name (the pre-D10 shape), the "which zone first" answer
missing or rendered after the zone list instead of above it, and that
answer duplicated a second time inside "For this room".

Also runs against the real, committed corpus and site/rooms/*.html, so a
future content.json edit or a regeneration that silently drops D10's
work fails this test directly.

Run:  python ops/tests/test_gate_room_hub_current.py
"""
import glob
import html as _html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import build_zone_pages as bzp                                 # noqa: E402


def _page(h1_html, start_html, dup_start=False, start_after_rows=False):
    start_block = ('<p class="notice"><b>Start here.</b> %s</p>'
                   % start_html) if start_html else ""
    rows = '<ol class="zone-rows"><li>a</li></ol>'
    dup = ('<h2>For this room</h2><ul><li><b>Where to start.</b> %s</li>'
          '</ul>' % start_html) if dup_start else ""
    if start_after_rows:
        body = "<h1>%s</h1>%s%s%s" % (h1_html, rows, start_block, dup)
    else:
        body = "<h1>%s</h1>%s%s%s" % (h1_html, start_block, rows, dup)
    return body


def main() -> int:
    fails = []

    room, job, start = "Entryway", "everything that comes in, sorted", \
        "Do the mat first."
    want_h1 = "%s: %s" % (_html.escape(room, quote=True),
                          _html.escape(job, quote=True))
    want_start_html = _html.escape(start, quote=True)

    # 1. Clean page: H1 states room and job, start answer above the zone
    #    list, not duplicated. No problems.
    pages = {"entryway.html": _page(want_h1, want_start_html)}
    problems = preflight.check_room_hub_current(
        {room: job}, {room: start}, pages)
    if problems:
        fails.append("clean page wrongly flagged: %s" % problems)

    # 2. Regression: H1 reverted to the bare room name (the pre-D10 shape).
    regressed = {"entryway.html": _page(_html.escape(room, quote=True),
                                        want_start_html)}
    problems = preflight.check_room_hub_current(
        {room: job}, {room: start}, regressed)
    if not problems:
        fails.append("bare-room-name H1 (pre-D10 shape) NOT caught")

    # 3. The "which zone first" answer is missing entirely.
    no_start = {"entryway.html": _page(want_h1, "")}
    problems = preflight.check_room_hub_current(
        {room: job}, {room: start}, no_start)
    if not problems:
        fails.append("missing 'which zone first' answer NOT caught")

    # 4. The answer renders, but after the zone list rather than above it.
    after = {"entryway.html": _page(want_h1, want_start_html,
                                    start_after_rows=True)}
    problems = preflight.check_room_hub_current(
        {room: job}, {room: start}, after)
    if not problems:
        fails.append("'which zone first' answer after the zone list NOT "
                     "caught")

    # 5. The answer is duplicated a second time inside "For this room".
    dup = {"entryway.html": _page(want_h1, want_start_html, dup_start=True)}
    problems = preflight.check_room_hub_current(
        {room: job}, {room: start}, dup)
    if not problems:
        fails.append("'Where to start' duplicated in 'For this room' NOT "
                     "caught")

    # 6. A room in the corpus with no built file at all.
    problems = preflight.check_room_hub_current(
        {room: job, "Missing Room": job}, {room: start, "Missing Room": start},
        pages)
    if not problems:
        fails.append("room page missing from the built site NOT caught")

    # 7. Against the real, committed corpus and site/rooms/*.html: proves
    #    all 20 room pages actually ship D10's H1 and start answer today.
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
    job_map = dict(bzp.ROOM_JOB)
    start_map = {}
    for r in rooms:
        tips = {t.get("label"): t.get("text") for t in (r.get("tips") or [])}
        start_map[r["room"]] = tips.get("Where to start")
    if len(job_map) != 20:
        fails.append("expected 20 rooms in ROOM_JOB, found %d (has the "
                     "corpus changed? update this test's expectation "
                     "deliberately if so)" % len(job_map))
    real_pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))):
        real_pages[os.path.basename(f)] = io.open(
            f, encoding="utf-8", errors="replace").read()
    problems = preflight.check_room_hub_current(job_map, start_map, real_pages)
    if problems:
        fails.append("real committed site fails its own check: %s" % problems)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: %d cases" % 7)
    return 0


if __name__ == "__main__":
    sys.exit(main())
