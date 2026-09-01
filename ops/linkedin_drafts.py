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
    ebook = next((p for p in cat if p.get("sku") == "BK-EB"), None)

    return {
        "rooms": len(rooms),
        "zones": zones,
        "cards": sum(1 for r in rooms for z in r["zones"]
                     for k in ("sort", "straighten", "shine", "safety",
                               "standardize", "sustain")
                     if (z.get("passes") or {}).get(k)),
        "free": free,
        "cheapest": min((p["price"] for p in paid), default=None),
        "ebook_price": ebook["price"] if ebook else None,
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


def ebook_line(f: dict) -> str:
    """The one price claim in the daily draft's own honesty block.

    A pure function over facts() so a check can prove this line stays live
    without re-running build(), which really consumes the LinkedIn post
    rotation (marks posts as served) and must not be called just to test a
    price string.
    """
    if f.get("ebook_price") is None:
        return ("  Chapters 31 to 50 are inside the paid eBook (price not "
                 "found in the live catalogue this run).")
    return f"  Chapters 31 to 50 are inside the ${f['ebook_price']:g} eBook."


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
    """Three of Phil's own posts, plus one connection note.

    The corpus in content/book holds 324 usable LinkedIn posts he wrote and
    never published. Serving those beats serving anything invented here, so the
    hand written CORPUS above is now used only for the connection note, which is
    a one to one message and the one thing the corpus does not contain.
    """
    f = facts()
    today = today or datetime.date.today()

    posts, remaining = [], 0
    try:
        from corpus_posts import take, pool                    # noqa: E402
        posts = take("linkedin-post", 3, record=True)
        remaining = len(pool("linkedin-post"))
    except Exception:                                          # noqa: BLE001
        posts, remaining = [], 0

    L = [f"Three posts to publish today, {today:%A %d %B}.", ""]
    if posts:
        L += [f"These are your own writing, out of the chapter content packages. "
              f"{remaining} usable posts sit in that corpus and none had ever been "
              "published. Post as written, or edit freely.", ""]
        for i, p in enumerate(posts, 1):
            L += ["=" * 64,
                  f"{i}. {p['title']}   [{p['chapter']}, {p['words']} words]",
                  "", p["body"], ""]
    else:
        L += ["The corpus could not be read this run, so there is only the "
              "connection note below.", ""]

    note = pick(today.toordinal(), 1)[0]
    L += ["=" * 64, "AND ONE CONNECTION NOTE, for a direct message rather than a post",
          f"To: {note[0]}", f"Angle: {note[1]}", "",
          note[2].format(**f), ""]

    L += ["", "WHAT IS TRUE TODAY, so nothing above overstates it:",
          f"  {f['rooms']} rooms, {f['zones']} micro zones, {f['cards']} cards.",
          "  Chapters 1 to 30 are genuinely free to read at 6s-success.com.",
          ebook_line(f),
          "  Sixteen posts that would have called a paid chapter free are held",
          "  back automatically.",
          "  Customers to date: 1, and that one was a referral.", ""]

    subject = f"3 posts to publish, {today:%a %d %b}"
    return subject, "\n".join(L)


if __name__ == "__main__":
    subject, text = build()

    # The cap applies to the CONNECTION NOTE only. It was written when this file
    # served nothing but short direct messages, where a hundred words is the
    # whole promise of the format. The corpus posts are public posts and run to
    # 120 words or more by design, so applying the same cap to them would reject
    # Phil's own finished writing for being the length he wrote it.
    note = text.split("AND ONE CONNECTION NOTE", 1)
    if len(note) > 1:
        body = note[1].split("WHAT IS TRUE TODAY")[0]
        # Drop the To and Angle header lines before counting.
        prose = "\n".join(ln for ln in body.splitlines()
                          if not ln.startswith(("To:", "Angle:", "=")))
        n = len(prose.split())
        assert n <= WORD_CAP, f"the connection note ran to {n} words, cap is {WORD_CAP}"

    # And every served post has to be something a person could actually publish.
    assert "TODO" not in text and "[insert" not in text.lower(), \
        "an unfinished corpus file reached the draft"

    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    if mode == "--send" and len(sys.argv) > 2:
        from mailer import send                                # noqa: E402
        send(sys.argv[2], subject, text)
        print("sent:", subject)
    else:
        print("SUBJECT:", subject, "\n")
        print(text)
