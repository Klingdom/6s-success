#!/usr/bin/env python3
"""
Email the owner the questions that are genuinely blocking, with a calendar
invite for the ones that need his hands rather than his answer.

The bar for appearing here is deliberately high. A question belongs in this
email only if no amount of Claude's work can resolve it: it needs Phil's legal
identity, his bank, his Google account, or a value only he holds. Anything that
is merely difficult gets done instead of asked.

Run:  python ops/send_questions.py --preview
      python ops/send_questions.py --send ADDRESS
"""
import datetime
import os
import mailer
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mailer import send                                # noqa: E402


def ics(summary, description, start, minutes, organizer, attendee):
    """A minimal but valid VEVENT. Written by hand rather than pulling a library
    for eighteen lines of text."""
    fmt = "%Y%m%dT%H%M%SZ"
    end = start + datetime.timedelta(minutes=minutes)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime(fmt)
    desc = description.replace("\n", "\\n")
    return ("BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//6S Success//ops//EN\r\n"
            "CALSCALE:GREGORIAN\r\n"
            "METHOD:REQUEST\r\n"
            "BEGIN:VEVENT\r\n"
            f"UID:{uuid.uuid4()}@6s-success.com\r\n"
            f"DTSTAMP:{stamp}\r\n"
            f"DTSTART:{start.strftime(fmt)}\r\n"
            f"DTEND:{end.strftime(fmt)}\r\n"
            f"SUMMARY:{summary}\r\n"
            f"DESCRIPTION:{desc}\r\n"
            f"ORGANIZER;CN=6S Success:mailto:{organizer}\r\n"
            f"ATTENDEE;CN=Phil;RSVP=TRUE:mailto:{attendee}\r\n"
            "STATUS:CONFIRMED\r\n"
            "SEQUENCE:0\r\n"
            "BEGIN:VALARM\r\n"
            "TRIGGER:-PT15M\r\n"
            "ACTION:DISPLAY\r\n"
            "DESCRIPTION:Reminder\r\n"
            "END:VALARM\r\n"
            "END:VEVENT\r\n"
            "END:VCALENDAR\r\n").encode()


BLOCKING = [
    ("Stripe live onboarding",
     "Identity and bank verification. Legally yours, not delegable.",
     "The account cannot take a single real payment until this is done. Both "
     "consulting offers already have working payment links, but they are test "
     "links. This is the difference between a site that looks like it sells and "
     "one that does.",
     "15 minutes in the Stripe dashboard"),
    ("Front matter: 13 bracketed fields",
     "Your legal name, imprint, and an ISBN.",
     "This blocks two finished products at once, a 261,000 word book and the "
     "114 zone manual. Neither needs traffic to be worth selling. It is the "
     "highest value hour on the whole board and it has been open since 16 August.",
     "20 minutes, plus an ISBN purchase of about 125 dollars"),
    ("Listmonk list UUID",
     "The identifier of the list new subscribers should join.",
     "Listmonk is already running on your VPS on port 8081 and its public "
     "subscription endpoint works. I need the UUID of the list to point the "
     "site's forms at. It is not a secret: it sits in the HTML of the signup "
     "form. Create a list called something like 6S Success readers, then send "
     "me the UUID from its page.",
     "3 minutes"),
    ("Google Search Console",
     "Register 6s-success.com and submit the sitemap.",
     "Needs your Google account. Organic search is the entire traffic plan and "
     "nothing about it can be reasoned about without 30 days of impressions. "
     "The clock does not start until somebody registers the property, so every "
     "day of delay moves month twelve back by a day.",
     "5 minutes"),
]

DECISIONS = [
    ("Cal.com", "You have Cal.com running on the VPS. Do you want consulting "
     "bookings to go through it? If so, tell me the URL and I will wire the "
     "consulting page to it. If you would rather field enquiries by email "
     "first, say so and I will leave it."),
    ("Reset kits and courses", "Eight priced SKUs have no supplier, no stock, "
     "no platform and no schedule. They are now correctly labelled as "
     "unavailable rather than buyable. Do you want them built, kept as "
     "in development, or removed from the catalogue?"),
    ("The 2,600 social units", "There are roughly 2,600 written, publishable "
     "social posts sitting unused. Publishing needs accounts. Which platforms "
     "do you want, and will you connect them?"),
]


def build():
    lines = [
        "Everything that can be done without you is being done. This is only "
        "the list that cannot.",
        "",
        "SITE STATUS",
        "  6s-success.com is live, 10 of 10 checks passing, TLS valid.",
        "  Deploys are automatic: push to main and the host pulls within five minutes.",
        "  Analytics is wired and waiting on one proxy path.",
        "  Both consulting offers have working payment links, in test mode.",
        "",
        "BLOCKING. Nothing I do can move these.",
        "",
    ]
    for i, (title, what, why, cost) in enumerate(BLOCKING, 1):
        lines += [f"  {i}. {title}", f"     {what}", f"     Why it matters: {why}",
                  f"     Cost to you: {cost}", ""]
    lines += ["DECISIONS. I will pick a sensible default if you would rather not.", ""]
    for i, (title, body) in enumerate(DECISIONS, 1):
        lines += [f"  {i}. {title}", f"     {body}", ""]
    lines += [
        "THE HONEST TIMELINE",
        "  20,000 a month needs about 112 of your hours plus 7,000 to 22,000",
        "  visits a month. Traffic on a site published today is roughly 800",
        "  visits by month three and 15,000 by month twelve. So the target is a",
        "  12 to 18 month objective. What can move quickly is consulting,",
        "  because it needs a handful of the right customers rather than a crowd.",
        "",
        "  The fastest path to first revenue is items 1 and 2 above.",
        "",
        "A calendar invite is attached for a 30 minute session covering items 1",
        "and 2, which together unblock every product that can be sold. Move it",
        "wherever suits. I will have everything else ready either way.",
        "",
        "Full detail: https://claude.ai/code/artifact/24137873-e944-49a1-85bf-b99979672d95",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    text = build()
    subject = ("6S Success: 4 things only you can do, and 3 decisions")

    # Next weekday morning at 9am Denver, which is 15:00 UTC.
    now = datetime.datetime.now(datetime.timezone.utc)
    start = (now + datetime.timedelta(days=1)).replace(
        hour=15, minute=0, second=0, microsecond=0)
    while start.weekday() > 4:
        start += datetime.timedelta(days=1)

    invite = ics(
        "6S Success: unblock the two things that gate all revenue",
        "1. Complete Stripe live onboarding, identity and bank verification.\n"
        "2. Fill in the 13 bracketed front matter fields, name, imprint, ISBN.\n\n"
        "Together these unblock every product that can currently be sold: both "
        "consulting offers for real money, plus the book and the manual.\n\n"
        "Everything else is already built and waiting.",
        start, 30, "support@6s-success.com", mailer.owner())

    if mode == "--preview":
        print("SUBJECT:", subject)
        print(f"INVITE:  {start:%Y-%m-%d %H:%M} UTC, 30 minutes")
        print()
        print(text)
        sys.exit(0)
    if mode == "--send":
        if len(sys.argv) < 3:
            sys.exit("usage: python ops/send_questions.py --send ADDRESS")
        print("sent", send(sys.argv[2], subject, text, None, None, None,
                           [("6s-success-unblock.ics", invite, "text", "calendar")]))
