#!/usr/bin/env python3
"""
Build the Home Quest web app: a playable deck over all 114 micro zones.

WHAT IT IS
----------
The card deck's loop is draw a card, do one thing, put it down. That works on
paper for one room. The manual holds the same structure for 114 micro zones
across 20 rooms, which is far too much to print and exactly the right size for
something that remembers where you got to.

So this is the deck, generalised: every micro zone becomes six cards, one per
S, drawn from the same content the book and the site are built from. Nothing
here is written fresh. If the manual changes, the app changes.

WHY IT IS CLIENT SIDE
---------------------
The site is a static nginx bundle with no server and no accounts. That is a
constraint and also the right answer: a household reset app has no business
holding an account, and progress belongs in the browser of the person doing the
work. Everything persists to localStorage. Nothing is sent anywhere.

WHAT GETS TRIMMED, AND WHY
--------------------------
content.json is 702 KB. Roughly 390 KB of that is `shine_detail`, the deep
per-surface cleaning method, which belongs on the zone pages where somebody is
reading rather than in an app where somebody is holding a cloth. Dropping it
and two reference fields takes the payload to about a third, and the zone page
is one tap away for anybody who wants the detail.

Run:  python ops/build_quest.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")

# The 110 reviewed zone pictures the zone pages already publish. Two separate
# files have to agree before one is offered to the app, and the third check is
# the disk:
#
#   ops/hero-verdicts.json   somebody looked at this picture and said "ok"
#   ops/hero-fallback.json   the alt text that review approved, verbatim
#   site/assets/zones/       the derivative actually exists at that width
#
# All three, because each has been wrong on its own before. Four of the 114
# are marked "no" (a garage of sawhorses, a board-game zone of moving boxes)
# and must never reach a screen; a stem with no derivative on disk would put a
# 404 inside a <picture> that no browser reports; and inventing alt text for a
# picture nobody described is how an image gets announced as something it is
# not. A zone that fails any of the three simply ships without an image, and
# the app renders text, which is what it did for its whole life until now.
VERDICTS = os.path.join(ROOT, "ops", "hero-verdicts.json")
HERO_ALT = os.path.join(ROOT, "ops", "hero-fallback.json")
ZONE_IMG = os.path.join(SITE, "assets", "zones")
# The site's zone pages are named from the display name, not the raw zone name,
# so "Primary Prep Counter" is published at kitchen-the-primary-prep-counter.
# Using the raw name here produced a link on every card that 404s.
NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))

# Canonical order, asserted rather than trusted to dict iteration. Safety is
# the fourth S and that is the method's most distinctive claim.
SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]

# The six-S ramp, chaos to calm, straight from site/assets/css/site.css.
COLOURS = {"sort": "#CB4B36", "straighten": "#BC4B2A", "shine": "#D98A2B",
           "safety": "#DDA63A", "standardize": "#6E8B5B", "sustain": "#4E7A57"}

# What each pass is for, in the app's own voice. One line, because it sits
# above the instruction and must not compete with it.
PURPOSE = {
    "sort": "Decide what stays. Nothing else.",
    "straighten": "Give what stayed a home you can reach.",
    "shine": "Clean it, and see what the cleaning tells you.",
    "safety": "Fix what could hurt somebody. The fourth S, not the last.",
    "standardize": "Write down what good looks like, so it is not a memory.",
    "sustain": "Attach the reset to something that already happens.",
}


def approved_and_published() -> set:
    """Stems that MUST appear, independent of what is on disk right now.

    Deliberately does not look at site/assets/zones/: that is the thing being
    checked. heroes() below adds the disk test on top of this, and main()
    compares the two, so "the file was missing" can never be mistaken for
    "the picture was never approved".
    """
    if not (os.path.exists(VERDICTS) and os.path.exists(HERO_ALT)):
        return set()
    ok = {stem for stem, rec in
          json.load(io.open(VERDICTS, encoding="utf-8")).items()
          if isinstance(rec, dict) and rec.get("verdict") == "ok"}
    published = {e.get("stem") for e in
                 json.load(io.open(HERO_ALT, encoding="utf-8")).values()}
    return ok & published


def heroes() -> set:
    """The stems the app may show. Pictures only, never their sentences.

    WHY NO ALT TEXT IS CARRIED, WHICH LOOKS LIKE A MISSING FEATURE
    -------------------------------------------------------------
    The obvious move is to ship each picture's published alt text alongside
    it. That was built first, and then the alt text was checked against the
    pictures, which is the step that had never happened anywhere in this
    pipeline.

    site/assets/zones/kitchen--sink-and-dishwashing-zone-md.jpg is a wide run
    of wood counter under two windows, with a sink, a dishwasher and a plant.
    Its alt text, live on the zone page today, is "a wiped drain flange".
    There is no drain flange in the image.

    It is not a one-off. `figure()` in wire_zone_heroes.py builds alt from the
    GENERATION SUBJECT, which is the prompt the picture was asked for, not a
    description of the picture that came back. So 26 of the 110 read as
    instructions rather than as scenes: "Every pan comes out, lids in a rack",
    "one category each", "one in use, one in the wash". ops/hero-verdicts.json
    certifies that somebody looked at the PICTURE and approved it. Nothing has
    ever certified the SENTENCE.

    Announcing a picture as something it is not is the accessibility version
    of a fabricated before and after, and shipping 110 of them into an app on
    the strength of a review that was never about them is not a trade worth
    making.

    So the app carries the stem and nothing else. In every place these appear
    the zone name is visible text within a few pixels of the picture, which
    makes the picture decorative in the WCAG sense: alt="" is not a gap there,
    it is the correct value, and it is the only one that is certainly true.
    The one image with a real description is the first-run picture in
    quest.html, written by opening the file and looking at it.

    Fixing the zone pages' own alt text is a real and separate job, owned by
    ops/wire_zone_heroes.py, and it needs somebody to look at 110 pictures.
    """
    # hero-fallback.json is the record of what is actually wired onto a
    # published zone page. Requiring membership there as well as an "ok"
    # verdict means the app can never be the only place a picture appears,
    # which would put an image in front of a customer that no page has ever
    # shown and no reviewer has seen in context.
    out = set()
    for stem in sorted(approved_and_published()):
        # Every width and format the app can ask for has to be on disk. A
        # <source> naming a file that is not there is a broken image in every
        # browser that prefers that format, and browsers do not report it.
        if all(os.path.exists(os.path.join(ZONE_IMG, f"{stem}-{t}.{e}"))
               for t in ("sm", "md", "lg") for e in ("avif", "webp", "jpg")):
            out.add(stem)
    return out


def display(room: str, zone: str) -> str:
    return NAME_MAP.get(f"{room}|{zone}", zone)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_data() -> tuple[str, dict]:
    d = json.load(io.open(SRC, encoding="utf-8"))
    art = heroes()
    rooms, cards, pictured = [], 0, 0

    for r in d["rooms"]:
        zones = []
        for z in r["zones"]:
            passes = z.get("passes") or {}
            steps = [{"s": s, "text": passes[s]} for s in SIX if passes.get(s)]
            if not steps:
                continue
            cards += len(steps)
            leave = z.get("leave_behind") or {}
            call = z.get("the_call") or {}
            zones.append({
                "zone": z["zone"],
                "session": z.get("session", ""),
                "purpose": z.get("purpose", ""),
                "done": z.get("done_looks_like", ""),
                "steps": steps,
                # The judgement call is the thing people get stuck on, so it
                # rides with the zone rather than being buried on a web page.
                "call": {"title": call.get("title", ""), "text": call.get("text", "")}
                        if call.get("text") else None,
                "watch": [{"q": w.get("question", ""), "t": w.get("text", "")}
                          for w in (z.get("watch_for") or []) if w.get("text")],
                "standard": leave.get("standard", ""),
                "trigger": leave.get("trigger", ""),
                "url": f"/zones/{slug(r['room'])}-{slug(display(r['room'], z['zone']))}",
            })
            # The same stem wire_zone_heroes.py names its files with:
            # the room slug, two dashes, the RAW zone name from this very
            # file. Derived, not guessed, and then checked against the disk
            # in heroes() above, so a rename on either side drops the picture
            # instead of shipping a dead reference.
            stem = f"{slug(r['room'])}--{slug(z['zone'])}"
            if stem in art:
                zones[-1]["img"] = stem
                pictured += 1
        if zones:
            rooms.append({"room": r["room"], "slug": slug(r["room"]), "zones": zones})

    payload = {"rooms": rooms, "six": SIX, "colours": COLOURS, "purpose": PURPOSE}
    js = ("/* Auto-generated by ops/build_quest.py from the Micro Zone Manual.\n"
          "   Do not edit. Change content.json and rebuild. */\n"
          "window.QUEST = " + json.dumps(payload, ensure_ascii=False,
                                         separators=(",", ":")) + ";\n")
    return js, {"rooms": len(rooms),
                "zones": sum(len(r["zones"]) for r in rooms),
                "cards": cards, "pictured": pictured,
                "kb": len(js.encode()) // 1024}


def main() -> int:
    js, stats = build_data()
    out = os.path.join(SITE, "assets", "js", "quest-data.js")
    io.open(out, "w", encoding="utf-8", newline="").write(js)
    print(f"  quest-data.js  {stats['rooms']} rooms, {stats['zones']} zones, "
          f"{stats['cards']} cards, {stats['kb']} KB")
    print(f"  pictures       {stats['pictured']} of {stats['zones']} zones carry "
          f"a reviewed image; the rest render text, as they always did")

    # Guard the two claims the whole method rests on. A generated file is
    # exactly where a quiet reordering would survive unnoticed.
    data = json.loads(js[js.index("{"):js.rindex(";")])
    assert data["six"] == SIX, "the six S's are out of canonical order"
    assert data["six"][3] == "safety", "Safety must be the fourth S"
    print("  canon        Safety is the fourth S, order asserted")

    # A COUNT THAT DROPS QUIETLY IS THE DEFECT, NOT THE SYMPTOM
    #
    # Two consecutive runs of this file, minutes apart, with no edit of its
    # own between them, printed 110 pictures and then 107. That turned out to
    # be correct: another process had rewritten ops/hero-verdicts.json in the
    # interval and withdrawn approval for three images, and this file honoured
    # it immediately, which is exactly what it should do.
    #
    # But nothing said so. 107 pictures is a perfectly valid file, every
    # downstream check passes on it, and a build that had instead dropped
    # three because a derivative was half-written during a concurrent encode
    # would have looked identical. That is the failure shape this repository
    # has paid for more than any other: a partial result indistinguishable
    # from a complete one.
    #
    # So the two causes are separated. `expected` comes from the approval
    # record alone and never looks at the disk; `shipped` is what actually
    # made it into the payload. A withdrawn approval moves both together and
    # is silent, correctly. A missing or unreadable file moves only one, and
    # is named and fails the build. Rerunning costs seconds.
    expected = approved_and_published()
    shipped = {z["img"] for r in data["rooms"] for z in r["zones"] if z.get("img")}
    short = sorted(expected - shipped)
    if short:
        print(f"  BROKEN       {len(short)} approved picture(s) did not make it "
              f"into the app, so this build would silently ship fewer than the "
              f"site shows. Usually a file was being rewritten; run it again.")
        for stem in short[:5]:
            print(f"                 {stem}")
        return 1
    print(f"  pictures     all {len(expected)} approved and published image(s) "
          f"present, counted against ops/hero-verdicts.json, not trusted")


    missing = []
    for r in data["rooms"]:
        for z in r["zones"]:
            page = os.path.join(SITE, z["url"].lstrip("/").replace("/", os.sep) + ".html")
            if not os.path.exists(page):
                missing.append(z["url"])
    if missing:
        print(f"  BROKEN       {len(missing)} zone link(s) point at no page:")
        for u in missing[:5]:
            print(f"                 {u}")
        return 1
    print(f"  links        all {stats['zones']} zone links resolve to a real page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
