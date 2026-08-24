#!/usr/bin/env python3
"""
Generate a page for every room and every micro zone.

Why this exists
---------------
All 114 micro zones currently live on one page, at about 37 words each. The
manual holds 500 to 900 words of specific, actionable method for each of them:
the function the zone should perform, what done looks like, the six passes in
order, the judgement call people get stuck on, the hazards, and the standard
that keeps it fixed.

So the most useful content in the business is invisible to anybody searching
for the thing it answers. Somebody types "how to organise entryway keys" and
there is no page about that, only a line on a list.

This is not page-count padding, and the distinction matters. CLAUDE.md forbids
generating thin pages to manipulate search, and it is right to. Each page here
carries the full method for one specific zone, written by a person, already
validated by the manual's own gates. If a zone had 40 words of content it would
not get a page.

What it writes
--------------
  site/rooms/<room>.html    20 pages, each listing its zones in working order
  site/zones/<room>-<zone>.html   114 pages, the full method for one zone

Both are wired into the existing chrome, carry the safety notice, and emit
schema.org HowTo, which is what answer engines read when deciding whether a
page actually answers a question.

Run:  python ops/build_zone_pages.py
"""
import html
import io
import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
BASE = "https://6s-success.com"
UMAMI = ('<script defer src="/stats/script.js" '
         'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
         'data-host-url="https://6s-success.com/stats"></script>')

SIX = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]

# The site and the manual name the same 114 zones differently. The manual says
# "Landing Zone", the site and the book say "The Landing Spot". Shipping pages
# in the manual's vocabulary would put two names for one zone in front of the
# same reader, so the display name always comes from the site while the method
# content comes from the manual. The map is by meaning, not by position,
# because at least one room lists its zones in a different order.
NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))


# Five drawn icons cover all 251 hazard entries across the 114 zones, because
# the corpus contains exactly five distinct hazard categories. The alternative
# on the table was 114 generated illustrations.
try:
    from hazard_icons import icon as hazard_icon
except Exception:                                             # noqa: BLE001
    def hazard_icon(q):
        return ""


def display(room, zone):
    return NAME_MAP.get(f"{room}|{zone}", zone)
SIX_WHY = {
    "sort": "Decide what stays. Everything else leaves the zone now.",
    "straighten": "Give what stays a home, placed where the hand actually reaches.",
    "shine": "Clean it, and use the cleaning to inspect what you cannot see when it is full.",
    "safety": "Make the zone safe for everybody who uses it, including the shortest person.",
    "standardize": "Write down the best way you know today, so it survives you forgetting.",
    "sustain": "Attach the reset to something that already happens, so it keeps itself.",
}


def esc(t):
    return html.escape(str(t or ""), quote=True)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def load_chrome():
    """Reuse the real header and footer so these pages cannot drift from the
    rest of the site. Relative links get a prefix because these pages sit one
    directory down."""
    src = io.open(os.path.join(SITE, "resources.html"), encoding="utf-8").read()
    head = src[src.find('<header class="site-header">'):src.find("</header>") + 9]
    foot = src[src.find('<footer class="site-footer">'):src.find("</footer>") + 10]

    def up(frag):
        return re.sub(r'(href|src)="(?!https?:|#|mailto:|/)([^"]+)"',
                      r'\1="../\2"', frag)
    return up(head), up(foot)


HEAD_TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:site_name" content="6S Success">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}/assets/img/room-map.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}/assets/img/room-map.jpg">
<meta name="theme-color" content="#22323C">
<link rel="stylesheet" href="../assets/css/site.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
"""

SAFETY = ("""<aside class="notice" style="margin:36px 0 0">
<b>Before you start.</b> This is guidance for organising and cleaning a home. It
is not instruction for electrical, gas, structural, or any other licensed work.
Do not lift or move anything unsafe, do not mix cleaning products, and follow the
label on anything you use. If a job needs a professional, that is the right
answer. See the <a href="../disclaimer.html">full safety notice</a>.
</aside>""")



# A zone page gives away about 950 words of method and then, until now, ended.
# The offer below follows the order CLAUDE.md sets out: diagnose, recommend,
# explain, then offer. It names a price, manufactures no urgency, and only ever
# offers the one thing that can actually be delivered today. It also says
# plainly that the method above is free and complete, because it is, and a
# reader who never buys anything should still leave better off.
#
# The primary button is the 19 dollar Print Pack, not the 250 dollar consult.
# A reader on a zone page just finished a free, complete, self serve guide to
# this exact zone, so the next step that matches where they actually are is
# carrying that same guidance into the room, not booking a consultant. The 20
# room pages already lead with the Print Pack for the same reason; this
# brings the 114 zone pages, the more specific and more numerous page, in
# line with that. The consult stays, for the zone that keeps fighting back,
# as the second offer rather than the first.
PACK_BUY = "https://buy.stripe.com/9B66oAgYedoC4ZA6VW0kE04"

# The same @id ops/build_product_schema.py assigns these two products' Product
# nodes on shop.html (every SKU there gets "@id": BASE + "/shop.html#" + sku,
# regardless of which page renders it, including the copy of CN-VIRTUAL that
# also appears on consulting.html). Referencing them here, rather than
# inventing a new id, is what actually connects a zone's HowTo to the product
# the page offers: an answer engine reading this page alone learns that a
# Product exists and where its full definition lives, the same pattern this
# codebase already uses for Organization (see ops/build_seo.py, ORG_ID).
PACK_ID = f"{BASE}/shop.html#PACK-HOUSE"
CONSULT_ID = f"{BASE}/shop.html#CN-VIRTUAL"


def offer(name):
    return ('<section class="band" style="margin:44px 0 0;padding:26px 28px;border-radius:22px">'
            '<p class="eyebrow on-deep">When you want it off the screen</p>'
            f'<h2 style="margin:0 0 10px">Carry {esc(name)} into the room</h2>'
            '<p style="margin:0 0 16px;max-width:62ch">The method above is complete and '
            f'free. The Whole House Print Pack puts {esc(name)} and the other 113 micro '
            'zones on 684 printable cards, so the steps you just read are not stuck '
            'behind a phone screen while your hands are full.</p>'
            '<p style="margin:0 0 14px"><a class="btn btn-primary" href="' + PACK_BUY + '" '
            'rel="noopener">The Print Pack, 19 dollars</a>'
            '<a class="btn btn-on-deep" style="margin-left:10px" href="../quest.html">'
            'Or draw a card free</a></p>'
            f'<p style="margin:0;font-size:14.5px;opacity:.85">If {esc(name)} keeps '
            'fighting back, the real problem usually sits somewhere else in the room. A '
            'one hour virtual consult is 250 dollars: we find the function, the friction '
            'and the root cause together, and you keep a written standard for the space. '
            '<a href="../consulting.html" style="color:#DDA63A">See what a consult '
            'covers</a>.</p></section>')


def room_offer(room, n):
    """The 20 room pages carried no commerce at all, which made them the only
    page type where somebody ready to buy found nothing. They are also the
    highest intent browse surface: a person on the Kitchen page has already
    told you which room is beating them."""
    return ('<section class="band" style="margin:44px 0 0;padding:26px 28px;border-radius:22px">'
            '<p class="eyebrow on-deep">When you want it off the screen</p>'
            '<h2 style="margin:0 0 10px">The whole ' + esc(room) + ' on cards you can carry</h2>'
            '<p style="margin:0 0 16px;max-width:62ch">Everything above is free and stays '
            'free. The Whole House Print Pack is the same method for all 114 micro zones, '
            'including these ' + str(n) + ', on 684 cards that print nine to a page. It is '
            'for the part where you are stood in the room with wet hands and would rather '
            'not be holding a phone.</p>'
            '<p style="margin:0"><a class="btn btn-primary" href="' + PACK_BUY + '" '
            'rel="noopener">The Print Pack, 19 dollars</a>'
            '<a class="btn btn-on-deep" style="margin-left:10px" href="../quest.html">'
            'Or draw a card free</a></p></section>')


# Every zone and room page taught the site's own articles nothing: 114 zone
# pages and 20 room pages carried zero links back to the articles, even
# though every article links out to specific zones and rooms as examples.
# That one-way graph left the articles reachable only from the homepage and
# their own index, and gave search engines no signal that the pillar content
# and the method pages belong to the same topic. This is the other direction
# of that link, chosen for what each page type actually needs next: a zone
# page's reader just worked one zone, so what is 6S, why it does not stay
# fixed, and why Sort has to come before Straighten are the natural next
# reads; a room page's reader is still choosing where to start, how much
# time the whole room takes, and what size unit ("micro zone") to pick.
#
# Two of the six articles, decluttering-vs-organizing and
# what-is-a-micro-zone, were added after this list was first written and were
# never wired in, so they were reachable only from the article cluster
# itself and (for the micro zone piece) resources.html. Both are added below,
# each placed where its topic actually answers the reader's next question.
#
# A seventh article, more-storage-wont-fix-clutter, answers the question a
# zone page's reader is about to ask right after reading the six-pass method:
# whether to go buy a bin for what is left. Added here rather than to
# ROOM_READING because the moment it is useful is right after working one
# specific zone, not while still choosing which room to start in.
#
# An eighth article, sentimental-items-without-guilt, answers the question
# that stalls Sort in more zones than any other single cause: the item that
# is not a "still use it" decision at all. Placed here because the stall
# happens mid-zone, not while choosing a room, the same reasoning as the
# seventh article above.
#
# A ninth article, family-wont-put-things-back, answers the question that
# surfaces right after Standardize: the standard is written, and somebody
# else in the house still is not following it. That is a Sustain problem
# specific to this zone, the same reasoning that placed the sixth article
# here rather than in ROOM_READING.
#
# A tenth article, why-you-keep-buying-things-you-already-own, answers a
# question that surfaces mid-Sort in exactly this kind of zone: why a
# duplicate keeps showing up even after a reset. Placed here rather than in
# ROOM_READING because the realization happens while working one shelf, not
# while choosing a room.
#
# An eleventh article, everything-needs-an-assigned-home, names the root
# cause the "leave it behind" standard on every zone page is already
# enforcing without ever explaining: a spot with room is not the same as a
# home. Placed here, right after the standard section a reader just read,
# rather than in ROOM_READING, because the standard that names one home per
# category is specific to this zone, not to the room as a whole.
#
# A twelfth article, tidy-is-not-the-same-as-safe, names unsafe placement as
# its own root cause, distinct from clutter: an item can sit within reach of
# a hazard in a zone that is otherwise fully sorted and homed, and only the
# Safety pass a reader just read checks for that. Placed second, right after
# the "what is 6S" entry that first names Safety as the fourth step, rather
# than in ROOM_READING, because the check is run zone by zone, not chosen
# once per room.
#
# A thirteenth article, how-long-to-keep-a-maybe, answers the question a
# reader hits at the exact moment Sort stalls on one item in this zone.
# Placed last because it is the entry most zone pages will not need, only
# the ones where a reader is stuck. This entry was previously present only
# in the committed HTML output, added by hand and never carried back into
# this list, so a rebuild from this file would have silently dropped it
# from all 114 zone pages. Fixed here rather than left as output-only.
#
# A fourteenth article, why-you-keep-running-out-of-things, names a root
# cause distinct from every one above: a missing replenishment signal,
# where the zone is fully sorted and homed and still fails, silently,
# because nothing marks the point where a consumable needs replacing.
# Placed after the maybe-pile entry, at the end of the list, for the same
# reason: most zones do not hold consumables and will not need it, but the
# ones that do, pantry, bathroom cabinet, laundry, are exactly the zones
# where this is the actual recurring failure the standard above does not
# name on its own.
#
# A fifteenth article, zone-too-small-for-what-it-holds, names inadequate
# capacity: the case where a genuinely reduced, honestly sized amount of
# belongings still does not fit, because the zone itself is smaller than
# its job, not because it is disorganized. Placed right after
# more-storage-wont-fix-clutter, the article it is the structural
# counterpart to, because a reader who just ruled out excess is exactly
# the reader who needs to know that the other explanation exists and has
# a different fix.
#
# A sixteenth article, why-the-same-spot-never-gets-clean, names difficult
# cleaning: a Shine pass root cause distinct from all the ones above, where
# the zone is sorted, homed, and safe, and still carries hidden dirt because
# the actual physical cost of cleaning one spot in it, a fetched tool, a
# stool, disassembly, is higher than everything else nearby. Placed right
# after the safety entry, because both are read at the same point in a
# zone page, right after the Shine section a reader who is already looking
# at what to clean is the reader this answers.
#
# A seventeenth article, everyday-things-out-of-reach, names poor
# accessibility: a Straighten pass root cause distinct from too many steps
# and from inadequate capacity, where a zone has room and a home for
# everything and still fails daily because what gets used most is not what
# sits in the easiest spot. Placed right after the "no assigned home" entry,
# because both are read while a reader is deciding where inside the zone
# something actually lives, not just whether it has a home at all.
#
# An eighteenth article, why-everyone-in-your-house-disagrees-about-clean,
# names inconsistent standard: a Standardize root cause distinct from
# family-wont-put-things-back's too many steps, where the standard is
# written and everything already has a home, and the zone still fails
# because the standard was never specific enough to give two people, or
# the same person on two different days, the same verdict. Placed right
# after the too-many-steps entry, because both are read at the same
# moment, a reader who just learned a written standard is not enough on
# its own is exactly the reader who needs to know a written standard can
# still be too vague to hold.
#
# A nineteenth article, why-a-shared-zone-never-stays-reset, names unclear
# ownership: a Sustain root cause distinct from both entries above, where
# the standard is written, specific, and easy to follow, and the zone
# still drifts because no single person is assigned to notice and enforce
# it. Placed right after the inconsistent-standard entry, continuing the
# same cluster in order: a reader who has just learned that a standard can
# be too vague to hold is exactly the reader who needs to know that even a
# perfectly clear standard still fails without someone specific checking
# it.
#
# A twentieth article, why-it-lives-in-one-room-but-gets-used-in-another,
# names wrong location: a Straighten root cause distinct from no assigned
# home, where the item does have a real, known address, and the zone still
# fails because that address is in the wrong room for how the item is
# actually used, so every use pays a round trip and the item drifts to
# wherever it is used instead. Placed right after zone-too-small-for-what-
# it-holds, closing out the excess and capacity cluster more-storage-wont-
# fix-clutter opens, before the reader moves on to sentimental items and
# family compliance.
ZONE_READING = [
    ("../articles/what-is-6s.html", "What is 6S?",
     "The six steps in order, and why Safety is the fourth one."),
    ("../articles/tidy-is-not-the-same-as-safe.html",
     "This zone's safety pass, in full",
     "Why a zone can be fully sorted and homed and still fail this check, and the three step way to run it."),
    ("../articles/why-the-same-spot-never-gets-clean.html",
     "Is one spot in this zone always the one you skip?",
     "Why difficult cleaning is its own root cause, and how to lower what the task costs instead of trying to want it more."),
    ("../articles/why-your-house-gets-messy-again.html",
     "Why this zone gets messy again",
     "What holds a reset, and what does not."),
    ("../articles/decluttering-vs-organizing.html",
     "Decluttering vs. organizing",
     "Why deciding what stays has to happen before deciding where it lives, which is the order below."),
    ("../articles/more-storage-wont-fix-clutter.html",
     "Before you buy storage for this zone",
     "Why a bin cannot fix excess, wrong location, or no assigned home, the three problems that actually cause clutter."),
    ("../articles/zone-too-small-for-what-it-holds.html",
     "Still does not fit, even after the honest count?",
     "How to tell a genuinely undersized zone from an overstuffed one, and the fixes that are not buying more storage."),
    ("../articles/why-it-lives-in-one-room-but-gets-used-in-another.html",
     "Does something in this zone actually get used somewhere else?",
     "Why an item can have a real, known home and still cause clutter, because that home is in the wrong room for how it gets used."),
    ("../articles/sentimental-items-without-guilt.html",
     "Stuck on one item in this zone?",
     "Why sentimental items break the usual keep or let go test, and five ways to decide anyway."),
    ("../articles/family-wont-put-things-back.html",
     "Written the standard, but nobody else follows it?",
     "Why willingness is rarely the real problem, and four ways to make putting it back the easier choice."),
    ("../articles/why-everyone-in-your-house-disagrees-about-clean.html",
     "Does everyone in the house agree what \"done\" looks like here?",
     "Why a standard that exists can still be too vague to hold, and the three things that make it specific instead."),
    ("../articles/why-a-shared-zone-never-stays-reset.html",
     "Does more than one person use this zone?",
     "Why a written, specific standard can still fail without one named person checking it, and how to assign that job."),
    ("../articles/why-you-keep-buying-things-you-already-own.html",
     "Found a duplicate of something in this zone?",
     "Why overbuying is a visibility problem, not a willpower problem, and four fixes that work at home."),
    ("../articles/everything-needs-an-assigned-home.html",
     "Why the standard above names one home per category",
     "The difference between a spot with room and a home, and why only one of them stops the pile from reforming."),
    ("../articles/everyday-things-out-of-reach.html",
     "Is the everyday item in this zone actually the easy one to reach?",
     "Why poor accessibility is its own root cause, distinct from clutter or capacity, and the rule that matches height to how often something gets used."),
    ("../articles/how-long-to-keep-a-maybe.html",
     "Not sure whether to keep something in this zone?",
     "How long is fair to wait, and the one habit that turns a maybe pile into an actual system instead of a nicer junk pile."),
    ("../articles/why-you-keep-running-out-of-things.html",
     "Does this zone keep running out of something?",
     "Why a fully sorted, fully homed zone can still run out without warning, and the one visible line that fixes it."),
    # A twenty first article, why-you-never-finish-a-zone, is not a root cause
    # from CLAUDE.md section 6, it is about the session itself: picking a
    # correctly sized zone is necessary and not sufficient, because the
    # session can still stall from decision fatigue, losing track of time, or
    # a "figure it out later" pile. Placed last because it applies to every
    # zone above rather than diagnosing one particular failure.
    ("../articles/why-you-never-finish-a-zone.html",
     "Started this zone and stalled partway through?",
     "Why the session stalls even when the zone was the right size, and four changes that fix finishing rather than starting."),
]
ROOM_READING = [
    ("../articles/how-long-does-it-take-to-organise-a-room.html",
     "How long this room actually takes",
     "Real session times for all 20 rooms, summed from the 114 zones."),
    ("../articles/where-to-start-decluttering.html",
     "Where to start if the whole room feels like too much",
     "How to pick a first zone using friction and effort."),
    ("../articles/what-is-a-micro-zone.html",
     "What is a micro zone?",
     "The size in between a whole room and a single object, and why it is the size that holds."),
]


def related_reading(links, descriptions=False):
    """The article links, by default as titles only.

    These descriptions used to render in full on all 114 zone pages, putting 401
    identical words on every one of them. Measured against another zone page, 55
    percent of the visible body was word for word the same, and this block was
    the largest single contributor. A hundred and fourteen pages that are half
    identical prose are a set a search engine indexes a few of and drops the
    rest, and this site is not indexed at all yet, so it is worth fixing before
    something crawls it rather than after.

    Nothing a reader needs is lost: every link survives, and the descriptions
    still belong on the articles index, which is the page whose job is helping
    someone choose between them. Pass descriptions=True there.
    """
    out = ['<h2>Related reading</h2><ul>']
    for href, title, text in links:
        tail = f', {esc(text)}' if descriptions else ''
        out.append(f'<li><a href="{esc(href)}">{esc(title)}</a>{tail}</li>')
    out.append('</ul>')
    return "\n".join(out)


# The book's finished photographs, with the alt text a person wrote for them.
# Empty for the twelve rooms that have no imagery yet, which is why every use
# below is guarded rather than assumed.
try:
    ROOM_IMAGES = json.load(io.open(os.path.join(ROOT, "ops", "room-images.json"),
                                    encoding="utf-8"))
except Exception:
    ROOM_IMAGES = {}


def room_figures(room):
    return ROOM_IMAGES.get(room, [])


def figure_html(entry, cls=""):
    """One figure.

    A caption is only shown when the book actually gave the figure a title, the
    "..., titled Coat Storage Standard, ..." pattern. Otherwise there is none.
    Slicing the first sentence off the alt text and calling it a caption puts
    the same words on the page twice, and a screen reader reads both, so the
    people the alt exists for are the ones it inconveniences."""
    alt = entry["alt"]
    cap = ""
    if ", titled " in alt:
        cap = alt.split(", titled ", 1)[1]
        cap = re.split(r", subtitled |\. |, with |, one |, daily ", cap)[0].strip(" .,")
        if len(cap) > 70:
            cap = ""
    # The hero is the largest thing above the fold and is usually the element
    # the browser measures for Largest Contentful Paint. Lazy loading it delays
    # the page's own headline image until a scroll, which is the opposite of
    # what lazy loading is for. Everything below it stays lazy.
    eager = cls == "hero"
    out = (f'<figure class="{cls}" style="margin:26px 0">'
           f'<img src="../assets/img/rooms/{entry["file"]}" alt="{esc(alt)}" '
           + ('loading="eager" fetchpriority="high" ' if eager else 'loading="lazy" ')
           + 'style="width:100%;height:auto;border-radius:14px">')
    if cap:
        out += (f'<figcaption style="font-family:var(--sans);font-size:13px;'
                f'color:var(--soft);margin-top:8px">{esc(cap)}</figcaption>')
    return out + "</figure>"


def _crumbs(*pairs):
    """BreadcrumbList JSON-LD from (name, url) pairs. The generated pages have
    shown a visual breadcrumb since launch and carried no markup for it, so the
    hierarchy was visible to a reader and invisible to everything else."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": u}
            for i, (n, u) in enumerate(pairs, 1)],
    }


def _clean(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def _join_clause(first: str, second: str) -> str:
    """Join two content fields into one sentence without inventing a full stop
    in front of a lowercase word.

    The fields in content.json are written as fragments that continue each
    other: session is "30-45 min" and time_note is "most of it in Sort". Joined
    with a period that produced "30-45 min. most of it in Sort" in 125 answers,
    which reads as a typo in the structured data and would be read aloud as one
    by anything that speaks it.

    So: a fragment that starts lowercase is a continuation and gets a comma. A
    fragment that starts a new sentence keeps its full stop.
    """
    first = " ".join(str(first or "").split()).rstrip(" .,;")
    second = " ".join(str(second or "").split())
    if not second:
        return first + "."
    if second[0].islower():
        return f"{first}, {second.rstrip('.')}."
    return f"{first}. {second.rstrip('.')}."


def zone_faq(thing, zone):
    """Question/answer pairs for FAQPage, built only from fields the page
    body already renders in full below (done_looks_like, the_call, watch_for,
    leave_behind, the session line). Nothing here is written for this
    function; every answer is the same sentence a reader sees in the "What
    done looks like", "Check these before you start" and "The standard that
    keeps it fixed" sections, so the structured data cannot say more than the
    visible page does.

    Takes `thing`, not the page's display `name`: 113 of 114 zones display
    as "The [Noun]", and "reset the The Landing Spot" is not a question
    anyone typed or would want read back to them. `thing` is the same
    lower-cased, "The "-stripped common noun searchable() already computes
    for the title, which is exactly the shape a real question needs.

    A zone with none of these fields returns an empty list and gets no
    FAQPage, rather than inventing generic questions to fill the type out.
    """
    qa = []

    session = zone.get("session", "")
    if session:
        note = zone.get("time_note", "")
        # Same words in the same order as the "One session" line the page
        # renders just below the title, so the answer is not a rephrasing.
        a = _join_clause(f"One session: {session}", note)
        qa.append((f"How long does it take to reset the {thing}?", _clean(a)))

    if zone.get("done_looks_like"):
        qa.append((f"What does a finished {thing} look like?",
                   _clean(zone["done_looks_like"])))

    call = zone.get("the_call") or {}
    if call.get("text"):
        qa.append((f"What is the hardest call to make in the {thing}?",
                   _clean(call["text"])))

    leave = zone.get("leave_behind") or {}
    if leave.get("standard"):
        # Same continuation problem as the session line: a trigger reads "when
        # the kitchen light goes off...", so a full stop in front of it puts a
        # lowercase word at the start of a sentence.
        a = _join_clause(leave["standard"], leave.get("trigger", ""))
        qa.append((f"How do you keep the {thing} from getting cluttered again?",
                   _clean(a)))

    for w in (zone.get("watch_for") or []):
        q, a = w.get("question", ""), w.get("text", "")
        if q and a:
            qa.append((f"Is there a {q.lower()} risk in the {thing}?", _clean(a)))

    return qa


# Zone display names are the vocabulary of the method, not of a search box.
# "Cooking Zone", "Sorting and Hamper Zone", "Paper and Household Backstock":
# every one of those is a phrase this business uses and nobody types. This map
# supplies the common noun where there is one.
#
# It covers 53 of the 114 zones. The rest are already ordinary words, and were
# deliberately left alone: "Medicine Cabinet", "Coffee Table", "Washer and
# Dryer" need no translation and inventing one would make them worse.
#
# HONESTY ABOUT THIS FILE: these are informed judgements, not measured demand.
# "sorting hampers" was corrected against live results after "hamper" turned
# out to drop the sorting job every competing page leads with. On 2026-08-23,
# with web search reachable even though the live site and Stripe were not, 12
# more were checked against real search results and 6 were wrong: "TV area"
# (nobody says that; "entertainment center" is what every source uses), "yard
# tool storage" ("garden tool storage" is what real guides call it), and four
# that repeated the room name back into the title ("guest bathroom guest
# towels", "laundry room laundry supplies", "patio or deck deck and railing",
# "stair landing staircase"). The other 41 remain unchecked judgement calls.
try:
    SEARCH_TERMS = json.load(io.open(
        os.path.join(ROOT, "ops", "zone-search-terms.json"), encoding="utf-8"))
except Exception:
    SEARCH_TERMS = {}


def searchable(room, zone, name):
    """The common noun for this zone, for use in a title a person might type."""
    t = SEARCH_TERMS.get(f"{room}|{zone}")
    if t:
        return t
    # No override: strip the tics that make an ordinary noun sound internal.
    # "Primary" is a brand habit, not a distinction a reader makes: there is one
    # workbench and they call it the workbench. The room name already carries
    # any "primary" that matters, as in Primary Bathroom.
    t = re.sub(r"^The ", "", name).strip()
    t = re.sub(r"\s+Zone$", "", t).strip()
    t = re.sub(r"^Primary ", "", t).strip()
    # Lowercased whole, not just the first letter. These are common nouns, and
    # "medicine Cabinet" in a title reads as a bug, which is what it was.
    return t.lower() if t else name


def zone_page(room, zone, prev_z, next_z, header, footer):
    name = display(room["room"], zone["zone"])
    rs, zs = slug(room["room"]), slug(name)
    url = f"{BASE}/zones/{rs}-{zs}"
    # Titles are cut off in search results somewhere around 60 characters. The
    # old shape, "{name} in the {room}: the six-S reset | 6S Success", ran to a
    # median of 69 and a maximum of 86, so 106 of 114 zone pages lost their
    # ending. The brand suffix was costing 13 characters that the zone and room
    # names need more, and Stripe aside, a search engine already knows the site
    # name from og:site_name. Dropping it and the "in the" leaves a median of 50
    # and 5 pages over.
    # "the six-S reset" was in 103 of these titles and nobody searches it. It is
    # a phrase this business invented, and a title made of private vocabulary
    # cannot match a query. Checked against live results for one of these zones:
    # real people and every competing page say "drop zone", "entryway
    # organization", "sorting hampers". They never say "landing spot", and they
    # certainly never say "six-S reset".
    #
    # So the title now leads with the job the reader came to do, in their words.
    # searchable() supplies the common noun where the internal name is not one.
    thing = searchable(room["room"], zone["zone"], name)
    title = f"How to organize the {room['room'].lower()} {thing}"
    # Some room and thing pairs overrun 60 even in that shape. Falling back to
    # the noun phrase alone keeps the words a searcher actually typed and loses
    # only the framing, which the page itself supplies.
    if len(title) > 60:
        title = f"{room['room']} {thing}: how to organize it"
    if len(title) > 60:
        title = f"How to organize {thing}"
    desc = (zone.get("purpose") or "").strip()
    # A few purposes are a single short sentence. Left alone they produce a
    # description far shorter than the space a search result actually gives,
    # so a second line is appended when there is room for it. That line used to
    # say "the six-S reset for this zone", which told a searcher nothing and
    # spent the space on vocabulary they had never met.
    # Keep this short. The first version ran to 91 characters, which meant that
    # added to a typical purpose it broke the 158 budget every time and was
    # therefore never appended once. A tail that never appears is not a tail.
    tail = "Step by step, and how to keep it that way."
    # Budget against the ESCAPED length, because that is what ends up in the
    # tag and what a search engine counts. One apostrophe becomes &#x27;, six
    # characters for one, which is enough to push a 158 character description
    # to 163 without a single extra word.
    if len(esc(f"{desc} {tail}")) <= 158:
        desc = f"{desc} {tail}".strip()
    while len(esc(desc)) > 158:
        desc = desc[:desc.rstrip().rfind(" ")].rstrip()
    passes = zone.get("passes", {})

    steps = []
    for i, s in enumerate(SIX, 1):
        body = passes.get(s)
        if body:
            steps.append({"@type": "HowToStep", "position": i, "name": s.title(),
                          "text": re.sub(r"\s+", " ", body)[:900]})
    ld = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to reset the {name} in the {room['room']}",
        "description": zone.get("purpose", ""),
        "totalTime": _iso_time(zone.get("session", "")),
        "step": steps,
        "about": {"@type": "Thing", "name": f"{room['room']} {name}"},
        # Both products are named in the offer section every zone page ends
        # with (see offer() above). mentions is the correct CreativeWork
        # property for naming a Thing the page discusses without claiming the
        # HowTo requires it to be completed, which HowToSupply/HowToTool would
        # wrongly imply for something that is genuinely optional.
        "mentions": [{"@id": PACK_ID}, {"@id": CONSULT_ID}],
    }
    ld_nodes = [ld, _crumbs(("Home", f"{BASE}/"),
                            ("Rooms", f"{BASE}/resources.html"),
                            (room["room"], f"{BASE}/rooms/{rs}"),
                            (name, url))]
    faq = zone_faq(thing, zone)
    if faq:
        ld_nodes.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq],
        })
    ld = json.dumps(ld_nodes, indent=1)

    out = [HEAD_TPL.format(title=esc(title), desc=esc(desc), url=url, BASE=BASE, ld=ld),
           header, '<main class="wrap">']
    out.append('<nav class="crumb" style="font-family:var(--sans);font-size:13px;'
               'color:var(--soft);margin:26px 0 0">'
               f'<a href="../resources.html">Rooms</a> / '
               f'<a href="../rooms/{rs}.html">{esc(room["room"])}</a> / '
               f'{esc(name)}</nav>')
    out.append('<div class="head" style="margin-top:10px">')
    out.append(f'<p class="eyebrow">{esc(room["room"])} micro zone</p>')
    out.append(f'<h1>{esc(name)}</h1>')
    out.append(f'<p class="lede">{esc(zone.get("purpose", ""))}</p></div>')

    out.append('<p class="notice" style="max-width:60ch">'
               f'<b>One session: {esc(zone.get("session", ""))}.</b> '
               f'{esc(zone.get("time_note", ""))}</p>')

    if zone.get("done_looks_like"):
        out.append('<h2>What done looks like</h2>')
        out.append(f'<p>{esc(zone["done_looks_like"])}</p>')

    out.append('<h2>The six passes, in order</h2>')
    out.append('<p>Work them in this order. Sorting after you have arranged '
               'things means arranging things you were about to remove.</p>')
    for i, s in enumerate(SIX, 1):
        body = passes.get(s)
        if not body:
            continue
        # The chip classes already exist in site.css and already carry the six
        # S colours. They were on the game and absent from the encyclopedia, so
        # six identical grey headings sat on every zone page while the one
        # visual signature this brand owns went unused.
        out.append(f'<section style="margin:26px 0" id="{s}">'
                   f'<h3><span class="chip {s.title()}">{s.title()}</span></h3>')
        out.append(f'<p class="notice" style="margin:0 0 10px">{esc(SIX_WHY[s])}</p>')
        out.append(f'<p>{esc(body)}</p></section>')

    call = zone.get("the_call") or {}
    if call.get("text"):
        out.append(f'<h2>{esc(call.get("title", "The call"))}</h2>')
        out.append(f'<p>{esc(call["text"])}</p>')

    watch = zone.get("watch_for") or []
    if watch:
        out.append('<h2>Check these before you start</h2>'
                   '<ul class="hazard-list">')
        for w in watch:
            q = w.get("question", "")
            out.append(f'<li>{hazard_icon(q)}<span><b>{esc(q)}</b>'
                       f'{esc(w.get("text", ""))}</span></li>')
        out.append('</ul>')

    shine = zone.get("shine_detail") or {}
    if shine.get("shine_summary"):
        out.append('<h2>Cleaning it properly</h2>')
        out.append(f'<p>{esc(shine["shine_summary"])}</p>')
        if shine.get("inspect_as_you_clean"):
            v = shine["inspect_as_you_clean"]
            items = v if isinstance(v, list) else [v]
            out.append('<p><b>Inspect as you clean.</b> Cleaning is the only time '
                       'you see the zone empty, so use it.</p><ul>')
            out += [f'<li>{esc(x)}</li>' for x in items]
            out.append('</ul>')

    leave = zone.get("leave_behind") or {}
    if leave.get("standard"):
        out.append('<h2>The standard that keeps it fixed</h2>')
        out.append(f'<p>{esc(leave["standard"])}</p>')
        if leave.get("trigger"):
            out.append(f'<p><b>Reset trigger.</b> {esc(leave["trigger"])}</p>')

    out.append(SAFETY)

    out.append('<h2>Next in this room</h2><ul>')
    if prev_z:
        out.append(f'<li><a href="{slug(room["room"])}-{slug(prev_z)}.html">'
                   f'{esc(prev_z)}</a>, the zone before this one</li>')
    if next_z:
        out.append(f'<li><a href="{slug(room["room"])}-{slug(next_z)}.html">'
                   f'{esc(next_z)}</a>, the zone after this one</li>')
    out.append(f'<li><a href="../rooms/{rs}.html">All '
               f'{len(room["zones"])} micro zones in the {esc(room["room"])}</a></li>')
    out.append('</ul>')
    out.append(related_reading(ZONE_READING))
    out.append(offer(name))
    out.append('</main>')
    out.append(footer)
    out.append(UMAMI)
    out.append('<script src="../assets/js/data.js"></script>'
               '<script src="../assets/js/site.js"></script></body></html>')
    return "\n".join(out)


def _iso_time(session):
    m = re.findall(r"\d+", session or "")
    return f"PT{m[-1]}M" if m else "PT30M"


def room_page(room, header, footer):
    rs = slug(room["room"])
    url = f"{BASE}/rooms/{rs}"
    n = len(room["zones"])
    # "micro zones" and "reset" are both this business's words. A person with a
    # kitchen that is beating them searches "how to organize a kitchen", so that
    # is what the title says, with the zone count as the reason to click.
    title = f"How to organize a {room['room'].lower()}, zone by zone"
    if len(title) > 60:
        title = f"How to organize a {room['room'].lower()}"
    desc = (f"Every part of the {room['room'].lower()} worth its own hour, in "
            f"the order to work them, with what done looks like for each.")
    item_list = {
        "@type": "ItemList",
        "name": f"{room['room']} micro zones",
        "numberOfItems": n,
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "name": display(room["room"], z["zone"]),
             "url": f"{BASE}/zones/{rs}-{slug(display(room['room'], z['zone']))}"}
            for i, z in enumerate(room["zones"], 1)],
    }
    # ItemList is an Intangible, not a CreativeWork, so it has no mentions
    # property to hang the Print Pack reference on. CollectionPage is a
    # WebPage, which is a CreativeWork, and its mainEntity is genuinely this
    # list, so the connection to the product every room page ends with (see
    # room_offer() above) sits on the page node rather than being invented on
    # a type that does not support it.
    page_node = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": url + "#page",
        "url": url,
        "name": f"{room['room']}: {n} micro zones",
        "mainEntity": item_list,
        "mentions": [{"@id": PACK_ID}],
    }
    ld = json.dumps([page_node, _crumbs(("Home", f"{BASE}/"),
                                        ("Rooms", f"{BASE}/resources.html"),
                                        (room["room"], url))], indent=1)

    out = [HEAD_TPL.format(title=esc(title), desc=esc(desc), url=url, BASE=BASE, ld=ld),
           header, '<main class="wrap">']
    out.append('<nav class="crumb" style="font-family:var(--sans);font-size:13px;'
               'color:var(--soft);margin:26px 0 0">'
               '<a href="../resources.html">Rooms</a> / ' + esc(room["room"]) + '</nav>')
    out.append(f'<div class="head" style="margin-top:10px"><p class="eyebrow">Room</p>'
               f'<h1>{esc(room["room"])}</h1>')
    if room.get("intro"):
        out.append(f'<p class="lede">{esc(room["intro"])}</p>')
    out.append('</div>')
    figs = room_figures(room["room"])
    if figs:
        out.append(figure_html(figs[0], "hero"))
    out.append(f'<h2>The {n} micro zones, in working order</h2>')
    out.append('<p>A micro zone is one session, not a whole day. Finish one before '
               'you start the next.</p><ol>')
    for z in room["zones"]:
        dn = display(room["room"], z["zone"])
        out.append(f'<li style="margin:0 0 14px"><a href="../zones/{rs}-{slug(dn)}.html">'
                   f'<b>{esc(dn)}</b></a> ({esc(z.get("session", ""))})<br>'
                   f'{esc(z.get("purpose", ""))}</li>')
    out.append('</ol>')
    for f in figs[1:]:
        out.append(figure_html(f))
    tips = room.get("tips") or []
    if tips:
        out.append('<h2>For this room</h2><ul>')
        out += [f'<li><b>{esc(t.get("label", ""))}.</b> {esc(t.get("text", ""))}</li>'
                for t in tips]
        out.append('</ul>')
    out.append(SAFETY)
    out.append(room_offer(room['room'], n))
    out.append('<h2>Other rooms</h2><p><a href="../resources.html">All 20 rooms and '
               '114 micro zones</a></p>')
    out.append(related_reading(ROOM_READING))
    out.append('</main>')
    out.append(footer)
    out.append(UMAMI)
    out.append('<script src="../assets/js/data.js"></script>'
               '<script src="../assets/js/site.js"></script></body></html>')
    return "\n".join(out)


def main():
    data = json.load(io.open(SRC, encoding="utf-8"))
    header, footer = load_chrome()
    os.makedirs(os.path.join(SITE, "rooms"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "zones"), exist_ok=True)

    urls, nz, words = [], 0, 0
    for room in data["rooms"]:
        rs = slug(room["room"])
        p = os.path.join(SITE, "rooms", f"{rs}.html")
        io.open(p, "w", encoding="utf-8", newline="").write(room_page(room, header, footer))
        urls.append(f"/rooms/{rs}.html")

        zs = room["zones"]
        for i, z in enumerate(zs):
            prev_z = display(room["room"], zs[i - 1]["zone"]) if i else None
            next_z = display(room["room"], zs[i + 1]["zone"]) if i + 1 < len(zs) else None
            html_out = zone_page(room, z, prev_z, next_z, header, footer)
            fp = os.path.join(SITE, "zones", f"{rs}-{slug(display(room['room'], z['zone']))}.html")
            io.open(fp, "w", encoding="utf-8", newline="").write(html_out)
            urls.append(f"/zones/{rs}-{slug(display(room['room'], z['zone']))}.html")
            body = html_out[html_out.find("<main"):html_out.find("</main>")]
            words += len(re.sub(r"<[^>]+>", " ", body).split())
            nz += 1

    print(f"  rooms written: {len(data['rooms'])}")
    print(f"  zones written: {nz}")
    print(f"  average words of real content per zone page: {words // max(nz,1)}")
    return urls


if __name__ == "__main__":
    main()
