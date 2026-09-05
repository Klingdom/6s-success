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
    ("Listmonk: decide the instance, then fix its SMTP identity",
     "A VPS admin decision plus five minutes in Listmonk's settings.",
     "The shared Listmonk sends 6S Success's confirmation mail branded as "
     "Compassion Benchmark, with a dead localhost opt-in link, so the signup "
     "form is withdrawn rather than shipping that. Decide whether 6S Success "
     "gets its own Listmonk instance or the shared one's SMTP host, user, "
     "pass and root URL get corrected for this brand. The email list is the "
     "one asset here that compounds and right now nobody can join it.",
     "10 minutes, plus whichever fix you choose"),
    ("Google Search Console",
     "Register 6s-success.com and submit the sitemap.",
     "Needs your Google account. Organic search is the entire traffic plan and "
     "nothing about it can be reasoned about without 30 days of impressions. "
     "The clock does not start until somebody registers the property, so every "
     "day of delay moves month twelve back by a day.",
     "5 minutes"),
]

# Stripe live onboarding and the book/manual front matter both used to be here.
# Removed 2026-09-05, this operator, having verified rather than assumed: Stripe
# has been in live mode and has taken one real sale since 2026-08-21 (see
# ROADMAP-2026-2029.md section 2), and front matter was answered from facts this
# system already held (commits 139f92f7, 3e5248c7, 2026-08-27), not by Phil.
# Sending either claim now would tell him something false.

DECISIONS = [
    ("Cal.com", "You have Cal.com running on the VPS. Do you want consulting "
     "bookings to go through it? If so, tell me the URL and I will wire the "
     "consulting page to it. If you would rather field enquiries by email "
     "first, say so and I will leave it."),
    ("Reset kits and courses", "Eight priced SKUs have no supplier, no stock, "
     "no platform and no schedule. They are now correctly labelled as "
     "unavailable rather than buyable. Do you want them built, kept as "
     "in development, or removed from the catalogue?"),
    ("The social corpus", "There are roughly {social_units} written, "
     "publishable social posts sitting unused. Publishing needs accounts. "
     "Which platforms do you want, and will you connect them?"),
]


def social_units_now():
    """Live count, not a number hand typed once and left to rot.

    2026-09-05: this file's own DECISIONS list still quoted a retired social
    unit count months after ops/dashboard.py fixed the identical hardcoded
    figure in itself (its own comment names the exact defect), and nothing
    carried the fix here. Reading it live the same way dashboard.py does
    closes the gap rather than replacing one frozen number with another.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import corpus_index
        rows, _, _ = corpus_index.build_index()
        return f"{sum(r['units'] for r in rows if r['ready']):,}"
    except Exception:
        return "an unknown number of"


def build():
    lines = [
        "Everything that can be done without you is being done. This is only "
        "the list that cannot.",
        "",
        "SITE STATUS",
        "  6s-success.com is live, 10 of 10 checks passing, TLS valid.",
        "  Deploys are automatic: push to main and the host pulls within five minutes.",
        "  Analytics is wired and waiting on one proxy path.",
        "  Both consulting offers have working live payment links. Stripe has",
        "  been in live mode and has taken one real sale since 2026-08-21.",
        "",
        "BLOCKING. Nothing I do can move these.",
        "",
    ]
    for i, (title, what, why, cost) in enumerate(BLOCKING, 1):
        lines += [f"  {i}. {title}", f"     {what}", f"     Why it matters: {why}",
                  f"     Cost to you: {cost}", ""]
    lines += ["DECISIONS. I will pick a sensible default if you would rather not.", ""]
    units = social_units_now()
    for i, (title, body) in enumerate(DECISIONS, 1):
        body = body.format(social_units=units)
        lines += [f"  {i}. {title}", f"     {body}", ""]
    lines += [
        "THE HONEST TIMELINE",
        "  ROADMAP-2026-2029.md's own honest target is $500 to $3,000 a month by",
        "  month twelve, not $20,000: search takes 12 to 18 months to compound on",
        "  a new domain, and the digital catalogue alone cannot reach $20,000 on",
        "  reachable traffic. What can move faster is services and the local",
        "  demand test in that roadmap's epic 3B, and the email list item 1",
        "  above is the one asset here that compounds once it can grow again.",
        "",
        "A calendar invite is attached for a 15 minute session covering items 1",
        "and 2 above. Move it wherever suits. I will have everything else ready",
        "either way.",
        "",
        "Full detail: https://claude.ai/code/artifact/24137873-e944-49a1-85bf-b99979672d95",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    text = build()
    subject = ("6S Success: 2 things only you can do, and 3 decisions")

    # Next weekday morning at 9am Denver, which is 15:00 UTC.
    now = datetime.datetime.now(datetime.timezone.utc)
    start = (now + datetime.timedelta(days=1)).replace(
        hour=15, minute=0, second=0, microsecond=0)
    while start.weekday() > 4:
        start += datetime.timedelta(days=1)

    invite = ics(
        "6S Success: Listmonk and Search Console",
        "1. Decide whether 6S Success gets its own Listmonk instance, or fix "
        "the shared one's SMTP identity and root URL.\n"
        "2. Verify 6s-success.com in Google Search Console and submit the "
        "sitemap.\n\n"
        "Together these unblock the email list and start the organic-search "
        "clock. Everything else is already built and waiting.",
        start, 15, "support@6s-success.com", mailer.owner())

    if mode == "--preview":
        print("SUBJECT:", subject)
        print(f"INVITE:  {start:%Y-%m-%d %H:%M} UTC, 15 minutes")
        print()
        print(text)
        sys.exit(0)
    if mode == "--send":
        if len(sys.argv) < 3:
            sys.exit("usage: python ops/send_questions.py --send ADDRESS")
        print("sent", send(sys.argv[2], subject, text, None, None, None,
                           [("6s-success-unblock.ics", invite, "text", "calendar")]))
