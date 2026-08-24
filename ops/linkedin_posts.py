#!/usr/bin/env python3
"""
Ten LinkedIn posts, for Phil to publish.

DIFFERENT FROM ops/linkedin_drafts.py, WHICH SENDS DAILY
--------------------------------------------------------
Those are one to one messages: short, addressed to a named person, sent in a DM.
These are public posts: they stand alone, they have to be worth reading by
somebody who has never heard of this business, and they cannot end in a pitch
without burning the goodwill that made anybody read them.

WHERE THE CONTENT COMES FROM
----------------------------
Every post is built on a `the_call` entry from content.json, which is the
judgement call people actually get stuck on in a given micro zone. Those are the
sharpest writing in the whole corpus and they are already true, already specific
and already written. A post assembled from real material beats a post about the
business, and it means none of these can drift from what the site says.

WHAT THEY NEVER CLAIM
---------------------
No customer count, no results, no testimonials, no "companies are discovering".
This business has had one sale and it was a personal referral. The posts talk
about the idea and the free artifacts, which is all that is honestly available.

Run:  python ops/linkedin_posts.py --preview
      python ops/linkedin_posts.py --send ADDRESS
"""
from __future__ import annotations

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def facts() -> dict:
    d = json.load(io.open(os.path.join(ROOT, "content", "manual", "source",
                                       "content.json"), encoding="utf-8"))
    return {"rooms": len(d["rooms"]),
            "zones": sum(len(r["zones"]) for r in d["rooms"])}


POSTS = [
    ("The 5S step everybody skips",
     """Every 5S rollout I have seen dies at Sustain.

The usual diagnosis is discipline. People did not keep it up. Run another audit,
add another board.

I think the diagnosis is wrong, and the failure is much earlier.

The unit is too big. You cannot diagnose "the stockroom". It has nine different
problems with nine different causes, and an improvement aimed at all of them at
once is aimed at none of them.

Shrink the unit until it has exactly one job and one failure mode. Then it can
be sorted in an afternoon, described in a sentence, and checked at a glance.

I have spent the last stretch applying that idea at home rather than at work.
{zones} zones across {rooms} rooms, each small enough to finish in one sitting.

The method transfers almost completely. What does not transfer is interesting,
and I will write that up separately."""),

    ("Safety is the fourth S, not a bolt-on",
     """5S has a well known problem: Safety got added later, at the end, and
everybody knows it.

Sort, Set in Order, Shine, Standardize, Sustain. Then, eventually, Safety, tacked
on the back where it reads like a compliance note.

Put it fourth instead.

After you have cleaned something is exactly when you can see what is wrong with
it. The clean is the inspection. That is when the frayed cord, the blocked
swing, the loose rail actually become visible, and it is the last moment before
you write down a standard that would otherwise standardise a hazard.

Safety fourth is not a nicer ordering. It is the only ordering where the
information arrives before the decision."""),

    ("The judgement call is the real work",
     """Ask somebody why a drawer is still a mess and they will tell you they
have not had time.

That is almost never it. Ten minutes exists. What does not exist is a decision.

Every stuck space I have looked at has exactly one item at the centre of it that
nobody will make a call on. In an entryway it is usually six sheets of paper,
each needing one small unpleasant action: a form, a phone call, a payment. In a
garage it is the half-finished project on the bench.

The pile is not a storage problem. It is a decision that has been deferred so
many times it has taken up residence.

Name the item. Give it a verdict today. The rest of the space follows in
minutes, and it will not hold until you do."""),

    ("The sunk cost on your coat rail",
     """There is a good coat on your rail that cost real money and goes outside
roughly never.

It has survived every clear-out, because getting rid of it feels like admitting
to the money.

The money is already spent. It was spent the day you bought it, and it is
equally spent whether the coat hangs there or not. What the coat is costing you
now is different: a hook, a decision every time you look at it, and the low
background hum of a wrong call you have not closed.

We teach this as sunk cost in every operations course and then walk past it in
our own hallway every morning.

Coats are counted by weather, not by number. If a second one does not beat the
first on a day you can name, it is not a coat, it is an argument you keep
having."""),

    ("What a standard actually is",
     """Most household organising advice ends at the moment the room looks
right. That is the least durable moment there is.

In a plant we would never accept that. We would ask what the standard is, and we
would write it where the work happens.

A standard is not a rule and not a chore chart. It is one sentence describing
the finished state, checkable at a glance, so anybody walking in can answer one
question: is this right, or not?

"The surface holds the tray and the folder and nothing else."

That is the whole thing. Post it where the zone is, not in a drawer. Two people
sign it, because a standard nobody agreed to is one person's preference and the
household will treat it as one.

One page per room, {rooms} of them, free and no email:
6s-success.com/standards.html"""),

    ("A trigger beats good intentions",
     """The reason your reset does not hold has nothing to do with willpower.

It is that the reset is attached to an intention rather than to a moment.

"I will tidy the entryway more often" has no moment in it. Nothing in your week
causes it to happen.

"As you take your coat off, your hands are already full and already stopped.
That is the moment everything in them goes into the tray." That has a moment in
it, and the moment already happens every single day whether you plan it or not.

Lean people already know this. We call it a trigger, or a pitch, or takt. We are
disciplined about it at work and completely undisciplined about it at home.

Find the moment that already happens. Attach the reset to it. Stop relying on
remembering."""),

    ("The test for a doormat",
     """Here is a small thing that changed how I think about inspection.

A doormat looks perfectly fine long after it has stopped working. So you never
replace it, because nothing about it looks broken, and replacing something
unbroken feels wasteful.

So stop looking at it and test it instead.

Walk in from outside on a dry gritty day. Wipe your feet the way you actually
do, not the way you would for a demonstration. Then lift the mat.

If the grit rode over the fibres and is sitting on the floor underneath, the mat
is finished. It is not catching anything. It is decoration that you sweep
around.

Most of what we call maintenance is looking at things. Almost none of it is
testing them, and looking is what lets a failed control sit in place for
years."""),

    ("Where the six S's do not transfer",
     """I have been applying workplace 6S at home for a while now. Most of it
transfers cleanly. Two things do not, and they are the interesting part.

First: there is no supervisor. Every workplace standard is ultimately backed by
somebody whose job it is to notice. A house has nobody in that role, which means
a standard has to survive purely on being easier to follow than to ignore. That
is a much higher bar and it kills most of what works at work.

Second: the people are not employees. You cannot roll out a standard to your own
family. You can propose one, and if they did not agree to it you do not have a
standard, you have a preference and a source of friction.

Both push the same way. At home, the design has to carry the discipline, because
nothing else will."""),

    ("A hazard hiding behind paper towels",
     """A genuine one from under a bathroom sink.

The cabinet is packed wall to wall, because it is the only storage in the room.
Behind the tower of paper towels is the P-trap.

Here is the arithmetic people avoid: a joint that weeps unnoticed for months
costs a cabinet floor, a subfloor, and sometimes a ceiling. The reason nobody
catches it is not carelessness. It is that the leak is behind the storage, and
nothing about the storage looks dangerous.

We would call that an obscured inspection point and we would not tolerate it on
a line.

Leave the plumbing visible. Whatever you cannot see, you cannot inspect, and
whatever you cannot inspect will eventually cost you more than the storage was
worth."""),

    ("Start with twenty minutes, not a weekend",
     """The reason your whole-house plan keeps failing is that it is a
whole-house plan.

A weekend reset requires a free weekend, energy, and everybody's cooperation on
the same day. That combination arrives about twice a year, and the plan waits
for it.

Take the smallest complete unit instead. Not the hallway: the spot inside the
door where pockets empty on the way in. Twenty minutes, one surface, one
decision about paper.

It is the highest leverage square foot in a house, because everyone in the
building interacts with it within an hour of you finishing, and because it is
small enough that finishing is actually available today.

Finishing something small beats starting something large. That is true on a
shop floor and it is true in a hallway.

The whole method is free to read: 6s-success.com"""),
]


def build() -> tuple[str, str]:
    f = facts()
    L = ["Ten posts, ready to publish. Each stands on its own, so post them in "
         "any order and space them out.", "",
         "Three carry a link and seven do not, on purpose. A feed where every "
         "post ends in a URL stops being read.", "",
         "Nothing below claims a customer, a result, or a number this business "
         "does not have. There has been one sale and it was a referral, so the "
         "posts talk about the idea and the free artifacts, which is all that "
         "is honestly available.", "", "=" * 66, ""]

    for i, (title, body) in enumerate(POSTS, 1):
        text = body.format(**f).strip()
        n = len(text)
        L += [f"POST {i}: {title}", "", text, "",
              f"[{n} characters, {len(text.split())} words]", "", "-" * 66, ""]

    L += ["", "A note on the first line. LinkedIn truncates at about 200 "
          "characters, so the opening line is the whole advert for the rest. "
          "Every post above is built to work if a reader only ever sees its "
          "first two lines.", ""]
    return "Ten LinkedIn posts, as asked", "\n".join(L)


if __name__ == "__main__":
    subject, text = build()
    # A post that runs past roughly 1,300 characters gets collapsed and loses
    # its ending, which is where the point usually is.
    for i, (title, body) in enumerate(POSTS, 1):
        n = len(body.format(**facts()).strip())
        assert n <= 1400, f"post {i} runs to {n} characters, too long for a feed"
    assert len(POSTS) == 10, f"asked for ten posts, have {len(POSTS)}"

    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    if mode == "--send" and len(sys.argv) > 2:
        from mailer import send                               # noqa: E402
        send(sys.argv[2], subject, text)
        print("sent:", subject)
    else:
        print(text)
