#!/usr/bin/env python3
"""
Three LinkedIn messages, written fresh each morning, emailed for Phil to send.

WHAT THIS IS AND IS NOT
-----------------------
It drafts. Phil sends. There is no LinkedIn automation here and there will not
be: automated messaging breaks LinkedIn's terms, and more to the point a
connection note that was obviously not written by a person is worse than no
note. A human reading three drafts over coffee and sending the one that fits is
both allowed and better.

THE HARD RULE
-------------
Every factual claim in every message is read from the live catalogue and the
content spine at generation time. Nothing is typed in and nothing is inferred.

That is not fussiness. This business has one customer and no results to point
at, and the temptation in outreach copy is exactly to imply otherwise: "helping
families transform their homes", "join hundreds of...". Every one of those is a
lie at this stage and CLAUDE.md section 8 forbids them. So the corpus below
speaks only about what the thing IS and what is free, never about who is using
it or how well it works.

WHY THE MESSAGES ROTATE
-----------------------
The same three drafts every morning become wallpaper by the fourth day. The
angle, the audience and the opening are all selected from the date, so the set
changes daily and cycles slowly enough that a repeat feels like a rerun rather
than a stuck record.

Run:  python ops/linkedin_drafts.py --preview
      python ops/linkedin_drafts.py --send ADDRESS
"""
from __future__ import annotations

import datetime
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORD_CAP = 100


def facts() -> dict:
    """Every number these messages are allowed to use, measured now."""
    d = json.load(io.open(os.path.join(ROOT, "content", "manual", "source",
                                       "content.json"), encoding="utf-8"))
    rooms = d["rooms"]
    zones = sum(len(r["zones"]) for r in rooms)

    js = io.open(os.path.join(ROOT, "site", "assets", "js", "data.js"),
                 encoding="utf-8").read()
    cat = json.loads(js[js.index("["):js.rindex("]") + 1])
    free = [p for p in cat if p.get("price") == 0 and p.get("href")]
    paid = [p for p in cat if p.get("buy")]

    return {
        "rooms": len(rooms),
        "zones": zones,
        "cards": sum(1 for r in rooms for z in r["zones"]
                     for k in ("sort", "straighten", "shine", "safety",
                               "standardize", "sustain")
                     if (z.get("passes") or {}).get(k)),
        "free": free,
        "cheapest": min((p["price"] for p in paid), default=None),
    }


# Each entry is (audience, angle, body). Body is a format string over the facts
# dict. Nothing here claims a result, a customer, or an outcome anybody has had.
CORPUS = [
    ("A Lean or CI practitioner you know",
     "The thing itself, no ask",
     "I have been building something outside work: 6S applied to the house "
     "instead of the plant floor. {zones} micro zones across {rooms} rooms, "
     "each taken through all six passes. Safety sits fourth, not bolted on the "
     "end, which turns out to matter more at home than it does in a factory. "
     "The whole method is free to read. No pitch, I would just like it read by "
     "someone who knows what 5S actually costs to sustain."),

    ("A Lean or CI practitioner you know",
     "The disagreement",
     "A question I keep chewing on. Every 5S rollout I have seen dies at "
     "Sustain, and the usual answer is audits. I think the real failure is "
     "earlier: the unit is too big. A whole area cannot be diagnosed, so I have "
     "been working at micro zone scale, {zones} of them across a house. Small "
     "enough to finish, specific enough to standardise. Curious whether that "
     "matches what you have seen."),

    ("Someone you met recently",
     "The free thing, plainly",
     "Good to talk the other day. The thing I mentioned is up: a method for "
     "making a home work better, one small zone at a time. There is a free "
     "pack of {rooms} printable sheets, one per room, naming what each zone "
     "holds to and the everyday moment that resets it. No email required, no "
     "account. If it is useful, it is useful. If not, no harm done."),

    ("A facilities or operations manager",
     "The crossover",
     "Odd side project you might appreciate. I took the 6S discipline we use at "
     "work and pointed it at the house: {zones} micro zones, six passes each, "
     "with the standard written down at the end so the space does not quietly "
     "revert. The parts that transfer and the parts that do not have been the "
     "interesting bit. Free to read if you are curious."),

    ("A dormant contact worth reviving",
     "No ask at all",
     "No agenda, just surfacing. I have spent the last stretch building "
     "something: 6S for homes rather than workplaces, {zones} micro zones with "
     "the method written out for each. It is the most useful thing I have made "
     "in a while and it is free to read. Would genuinely rather hear what you "
     "have been building."),

    ("A Lean or CI practitioner you know",
     "The workshop angle",
     "Something you might use rather than just read. I built {cards} printable "
     "cards, one per micro zone per pass, for taking a space through 6S a card "
     "at a time. Built for houses, but the format works anywhere the problem is "
     "that people know the method and still do not run it. Happy to send it "
     "over if that is useful for a session."),

    ("Someone in your network with a new house or baby",
     "The specific moment",
     "Congratulations. Unsolicited and ignore if not useful: I have been "
     "building a method for setting up a home so it stays workable, broken into "
     "{zones} small zones rather than whole rooms. There is a free entryway "
     "deck and a free set of room sheets. The entryway is the one worth twenty "
     "minutes first. Genuinely no pitch attached."),

    ("A former colleague",
     "Ask for a read, not a share",
     "I would value your eye on something. I have written a method for making "
     "homes work, structured the way we structure improvement at work: function "
     "first, then root cause, then the smallest change, then a written "
     "standard. {rooms} rooms, {zones} zones. It is free and complete. What I "
     "want is not a share, it is one honest sentence about whether it holds up."),
]


def words(t: str) -> int:
    return len(t.split())


def pick(day: int, n: int = 3) -> list:
    """Three from the corpus, rotating by date so no two mornings match."""
    out, seen = [], set()
    for i in range(len(CORPUS)):
        idx = (day * 3 + i) % len(CORPUS)
        item = CORPUS[idx]
        if item[0] in seen and len(seen) < 3:
            continue
        out.append(item)
        seen.add(item[0])
        if len(out) == n:
            break
    return out


def build(today: datetime.date | None = None) -> tuple[str, str]:
    f = facts()
    today = today or datetime.date.today()
    chosen = pick(today.toordinal())

    L = [f"Three to send today, {today:%A %d %B}. Pick one, edit freely, send it "
         "yourself.", ""]

    for i, (audience, angle, body) in enumerate(chosen, 1):
        text = body.format(**f)
        n = words(text)
        L += [f"{i}. {audience.upper()}", f"   Angle: {angle}", ""]
        # Wrapped for reading in a mail client, but the message itself is one
        # paragraph: LinkedIn strips the line breaks anyway.
        line = ""
        for w in text.split():
            if len(line) + len(w) + 1 > 72:
                L.append("   " + line)
                line = w
            else:
                line = (line + " " + w).strip()
        if line:
            L.append("   " + line)
        L += ["", f"   [{n} words]", ""]

    free = ", ".join(p["name"] for p in f["free"])
    L += ["", "WHAT IS TRUE TODAY, so nothing above overstates it:",
          f"  {f['rooms']} rooms, {f['zones']} micro zones, {f['cards']} cards.",
          f"  Free and complete: {free}.",
          f"  Cheapest paid item: ${f['cheapest']}.",
          "  Customers to date: 1. No message above mentions one, and none should",
          "  until there are enough that saying so is not misleading.", "",
          "Links worth pasting:",
          "  https://6s-success.com/standards.html   the free room sheets",
          "  https://6s-success.com/deck.html        the free entryway deck",
          "  https://6s-success.com/quest.html       the free app", ""]

    subject = f"3 LinkedIn drafts for {today:%a %d %b}"
    return subject, "\n".join(L)


if __name__ == "__main__":
    subject, text = build()

    # A message over the cap is a message nobody reads to the end of. This is a
    # build gate, not a warning, because the whole promise of the format is that
    # they are short.
    for block in text.split("\n\n"):
        if block.strip().startswith("["):
            n = int(block.strip().strip("[]").split()[0])
            assert n <= WORD_CAP, f"a draft ran to {n} words, cap is {WORD_CAP}"

    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    if mode == "--send" and len(sys.argv) > 2:
        from mailer import send                                # noqa: E402
        send(sys.argv[2], subject, text)
        print("sent:", subject)
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
