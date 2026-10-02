#!/usr/bin/env python3
"""
Prove no room claims an alternative name nobody actually types.

WHY THIS EXISTS
---------------
ops/room-also-called.json puts a line on five room pages: "Also called the
master bedroom", "Also called the foyer or the entrance hall", and so on. That
is useful to a reader who does not use this site's word for their room, and it
is also the exact shape of change that rots into keyword stuffing: a list of
synonyms is cheap to extend, each addition looks harmless, and nothing in the
page tells you whether anybody searches for the word.

So the file is held to its own rule. Every name in it must appear in
ops/keyword-demand.json, which is a record of phrases Google and Bing actually
suggest. "ensuite", "rec room", "master closet" and "lounge" were all
considered when the file was written and all returned zero queries; this test
is what stops the next cycle adding them anyway.

The second half is the same honesty pointed the other way: a name the site
ALREADY answers for does not belong here either, because the line would be
noise on the page and would claim a gap that is closed. "linen closet" (51
queries, 24 covered) and "walk in closet" (34, 15) are the examples.

Run:  python ops/tests/test_room_also_called.py
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAP = os.path.join(ROOT, "ops", "room-also-called.json")
DEMAND = os.path.join(ROOT, "ops", "keyword-demand.json")
CORPUS = os.path.join(ROOT, "content", "manual", "source", "content.json")
ROOMS_DIR = os.path.join(ROOT, "site", "rooms")

LINE = re.compile(r'<p class="also-called"[^>]*>(.*?)</p>', re.S)


def load():
    return json.loads(io.open(MAP, encoding="utf-8").read())


def demand_rows():
    if not os.path.exists(DEMAND):
        return None
    return json.loads(io.open(DEMAND, encoding="utf-8").read())["rows"]


def main():
    fails = []
    if not os.path.exists(MAP):
        print("NOT VERIFIED: ops/room-also-called.json is not present, so "
              "nothing was checked.")
        return 0
    data = load()
    rooms = data.get("rooms", {})

    # 1. It has to be doing something.
    if len(rooms) < 3:
        fails.append("only %d room(s) carry an alternative name, which is too "
                     "few for this test to be checking anything" % len(rooms))

    # 2. Every room named must be a real room in the corpus.
    real = {r["room"] for r in
            json.loads(io.open(CORPUS, encoding="utf-8").read())["rooms"]}
    for room in rooms:
        if room not in real:
            fails.append("%r is not a room in content.json" % room)

    # 3. THE RULE THAT MATTERS. Every name must be a phrase people type,
    #    evidenced by the demand harvest, not by anybody's intuition.
    rows = demand_rows()
    if rows is None:
        print("NOT VERIFIED: ops/keyword-demand.json is not present, so the "
              "demand behind these names was NOT checked. The rendering "
              "checks below still ran.")
    else:
        for room, entry in sorted(rooms.items()):
            for name in entry.get("names", []):
                pat = re.compile(r"\b" + re.escape(name) + r"\b")
                hits = [r for r in rows if pat.search(r["query"])]
                if not hits:
                    fails.append(
                        "%s claims the name %r, and that phrase appears in "
                        "zero of the %d harvested queries. Naming it invents "
                        "demand." % (room, name, len(rows)))
                    continue
                covered = sum(1 for r in hits if r["status"] == "covered")
                if covered and covered == len(hits):
                    fails.append(
                        "%s claims the name %r, but all %d harvested queries "
                        "using it are already covered, so the line is noise "
                        "rather than a gap being closed"
                        % (room, name, len(hits)))

    # 4. The shipped pages must match the file exactly: the named rooms carry
    #    the line, and no other room does. A page keeping a line after its
    #    entry is removed is the "source corrected, artifact not re-derived"
    #    shape this repository names as its dominant defect class.
    pages = [f for f in sorted(glob.glob(os.path.join(ROOMS_DIR, "*.html")))
             if not f.endswith("index.html")]
    if len(pages) < 20:
        fails.append("only %d room page(s) found, so the rendering was not "
                     "really checked" % len(pages))
    slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    want = {slug(r): r for r in rooms}
    for f in pages:
        name = os.path.basename(f)[:-len(".html")]
        html = io.open(f, encoding="utf-8", errors="replace").read()
        m = LINE.search(html)
        if name in want and not m:
            fails.append("%s is named in room-also-called.json and its page "
                         "carries no line" % name)
        elif name not in want and m:
            fails.append("%s carries an also-called line and is not in "
                         "room-also-called.json: %r"
                         % (name, re.sub(r"<[^>]+>", "", m.group(1))[:60]))
        elif name in want and m:
            text = re.sub(r"<[^>]+>", "", m.group(1)).lower()
            for n in rooms[want[name]]["names"]:
                if n.lower() not in text:
                    fails.append("%s's line does not mention %r: %r"
                                 % (name, n, text[:70]))

    if fails:
        print("FAIL")
        for f in sorted(set(fails)):
            print(" -", f)
        return 1
    print("OK: %d room(s) carry an alternative name, every name is evidenced "
          "by the demand harvest, and the shipped pages match the file"
          % len(rooms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
