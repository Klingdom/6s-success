#!/usr/bin/env python3
"""
The page for the question this whole product exists to answer.

WHY THIS EXISTS
---------------
2026-10-01, ops/keyword_demand.py took this business's first reading of what
people actually type. The complaint cluster, how somebody searches BEFORE they
have decided that organising is the answer, came back as 49 queries with ZERO
covered by anything we publish. "why is my kitchen always messy", "why is my
kitchen always a mess", "why is my bedroom always messy" and "why your home is
always messy" are all rank-1 autocomplete suggestions, and the closest page on
this site was the articles index.

That is the gap worth closing, and not because it is a gap. It is the exact
question seventeen root causes and 114 diagnosed micro zones were built to
answer, and in six weeks of SEO work nobody had put a page in front of it.

ONE PAGE, NOT EIGHT
-------------------
The obvious move is a page per room: why is my kitchen messy, why is my bedroom
messy, and so on down the list. CLAUDE.md section 11 forbids it, correctly, and
the content reason is stronger than the policy one: the answer to all of them
is the same diagnosis with a different example, so eight pages would be one
article padded seven times. The room-specific questions are answered on this
page, in their own words, each linking to the room that goes deeper.

WHY IT IS GENERATED AND NOT TYPED
---------------------------------
Every cause, its meaning, its thirty-second test and its linked article come
from ops/root_causes.py, the single shared vocabulary behind sixteen decks and
114 zone pages. Typing them here would create a seventeenth copy to drift, and
LRN-0023 is what that costs: one wrong sentence in that vocabulary was live on
100 pages, perfectly consistent everywhere and wrong everywhere.

Run:  python ops/build_messy_article.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))

from root_causes import BY_ID                                  # noqa: E402

SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "articles", "why-is-my-house-always-messy.html")
TEMPLATE = os.path.join(SITE, "articles", "why-your-house-gets-messy-again.html")
BASE = "https://6s-success.com"
SLUG = "why-is-my-house-always-messy"
PUBLISHED = "2026-10-01"

TITLE = "Why is my house always messy?"
DESC = ("Because it is almost never the whole house. It is four or five small "
        "zones failing for different reasons, which is why one big tidy never "
        "holds. How to find yours, and what each one actually needs.")

# The order a reader meets them, not the order they are numbered in. These are
# the causes that answer "always", which is the word in the question: a zone
# that comes back is failing at assignment, volume, agreement or trigger far
# more often than at effort.
CAUSE_ORDER = ("KC-002", "KC-001", "RC-015", "KC-004", "KC-008",
               "KC-009", "RC-017")

# What each cause looks like in a house, written here because the vocabulary
# deliberately speaks about any zone and a reader arriving on this question
# needs one concrete picture. The meaning and the test below each one are
# quoted from root_causes.py and are not retyped.
PICTURE = {
    "KC-002": ("The keys are the famous one, but it is usually duller than "
               "that: the scissors, the sellotape, the phone charger, the bag "
               "that gets carried in every day. None of them is homeless "
               "because the house is small. They are homeless because nobody "
               "ever decided."),
    "KC-001": ("This is the one people resist, because the room genuinely "
               "feels short of space. It usually is not. A drawer holding "
               "three times what the drawer's job needs will look messy five "
               "minutes after it is tidied, and so will the next drawer you "
               "buy to hold the overflow."),
    "RC-015": ("A pile of post is not untidiness. It is a stack of decisions "
               "somebody has postponed, and it cannot be tidied, because the "
               "only thing that moves it is deciding. Put it in a tray and "
               "you have a tidier stack of the same postponed decisions."),
    "KC-004": ("If putting something away costs four movements and dropping "
               "it on the side costs one, the side wins, every time, for "
               "everybody in the house. That is not laziness, it is "
               "arithmetic, and it is the arrangement's fault."),
    "KC-008": ("Two people clear the same counter to two different finished "
               "states. Neither is wrong, so neither holds, and whoever cares "
               "most does it twice and resents it. This one is the quiet "
               "reason a lot of houses argue about mess."),
    "KC-009": ("Almost every household that resets a zone reliably has "
               "attached it to something else that already happens: the "
               "kettle going on, the bins going out, the end of a cooking "
               "session. Intention does not survive a bad week. A trigger "
               "does."),
    "RC-017": ("The box that arrived in March is now furniture. Nobody in the "
               "house sees it any more, which is exactly why it is still "
               "there, and why a visitor spots it in four seconds."),
}

ROOM_SECTIONS = [
    ("Why is my kitchen always messy?", "Kitchen", "kitchen",
     "KC-002",
     "Because the counter is doing two jobs. It is the surface you cook on, "
     "and it is the first flat thing anybody passing through puts anything "
     "down on: post, keys, a school letter, a parcel, a water bottle. Those "
     "things are not kitchen things. They are things with no home anywhere "
     "else, landing on the nearest available surface, which happens to be the "
     "one you need clear to make dinner.",
     "Give the three or four usual offenders a home that is not the counter, "
     "and the counter stops being a landing strip. Clearing it again tonight, "
     "without doing that, buys you until about Thursday."),
    ("Why is my bedroom always messy?", "Primary Bedroom", "primary-bedroom",
     "KC-002",
     "Because of clothes that are neither clean nor dirty. Almost every "
     "bedroom that stays messy has a chair, a bench, an exercise bike or a "
     "floor doing the job of holding worn-once clothes, and almost none of "
     "them has anywhere that is supposed to hold them. The wardrobe is for "
     "clean, the basket is for dirty, and the jumper you wore for two hours "
     "is honestly neither.",
     "It is the clearest example of a missing home there is, and it is also "
     "the easiest to fix, because the pile tells you how much capacity the "
     "answer needs."),
    ("Why is my kids' room always messy?", "Kids Bedroom", "kids-bedroom",
     "KC-008",
     "Usually because the standard is one an adult can meet and a child "
     "cannot. If putting the toys away means stacking boxes by size inside a "
     "cupboard, a six-year-old will not do it, not because they are "
     "unwilling but because the method is beyond them. The same room with "
     "three open bins at their reach, each with a picture on the front, gets "
     "reset most days.",
     "Lower the standard to one the actual person can hit, and it starts "
     "holding. Then raise it later, if you still want to."),
    ("Why is my closet always a mess?", "Hall Closet", "hall-closet",
     "KC-001",
     "Because a closet is the only place in the house with no social "
     "pressure. Nobody sees it, so it absorbs whatever the rooms evict, and "
     "it keeps absorbing until the door stops closing. By then the problem "
     "reads as not enough storage, and it is almost always volume.",
     "The test below separates the two honestly, and it matters, because one "
     "of them is solved by an afternoon and the other by buying something "
     "that will fill up too."),
]

FAQ = [
    ("Why is my house always messy even though I clean it?",
     "Cleaning removes dirt. It does not decide where anything lives, so a "
     "freshly cleaned room still has nowhere to put the things that made it "
     "messy. Within a few days they are back on the same surfaces. What "
     "changes that is giving the few repeat offenders a home, and agreeing "
     "what the surface looks like when it is finished."),
    ("Is my house messy because I do not have enough storage?",
     "Sometimes, and less often than it feels. The honest test is to put back "
     "only what genuinely belongs in that spot. If it still will not close, "
     "the capacity really is the problem. If it closes easily, the space was "
     "never the issue and more storage will fill up too."),
    ("Where do I start if the whole house is messy?",
     "With one micro zone, not a room, and preferably the one that annoys you "
     "most often rather than the one that looks worst. A finished zone that "
     "you pass twenty times a day pays you back immediately, and it is a "
     "fifteen to forty-five minute job rather than a weekend."),
    ("Why does my house get messy again so fast?",
     "Because nothing was attached to the reset. A zone that is cleared "
     "without a trigger depends on somebody remembering, and that survives a "
     "good week and fails a bad one. Households that hold a zone almost "
     "always hooked it to something that already happens anyway."),
    ("Am I just lazy?",
     "Almost certainly not, and this is worth saying plainly. If putting "
     "something away takes four movements and dropping it takes one, everyone "
     "in the house drops it, including the tidy ones. That is the "
     "arrangement's fault rather than a character fault, and it is fixable "
     "without becoming a different person."),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def chrome():
    """(head_before_ld, header, footer) lifted from a sibling article.

    Taken from a real shipped page rather than written here, so this article
    inherits the nav, the footer, the asset fingerprints and the measurement
    script that every sweep in ops/ expects to find, and cannot drift from
    them on the day one of those sweeps changes.
    """
    s = io.open(TEMPLATE, encoding="utf-8").read()
    head = s[:s.index('<script type="application/ld+json">')]
    header = s[s.index("</head>") + len("</head>"):s.index("<main")]
    footer = s[s.index("</main>") + len("</main>"):]
    return head, header, footer


def retitle(head):
    """The sibling's head with every one of its own strings replaced.

    Done by explicit substitution with a count check rather than a loose
    regex: a head that silently kept the template's canonical would publish a
    duplicate of another page, which is the kind of defect that looks fine on
    screen and is invisible until a search engine picks one of them.
    """
    old_title = "Why your house gets messy again a week after you clean it"
    old_desc = ("Cleaning is an event, and events expire. Why a clean room "
                "drifts back within a week, and the two things that hold it: "
                "a written standard and a reset trigger.")
    old_slug = "why-your-house-gets-messy-again"
    # Counted against the real template, not guessed: title and description
    # appear three times each (the <title>/<meta>, the og: pair and the
    # twitter: pair), the slug twice (canonical and og:url). The check is
    # here because a head that silently kept the template's canonical would
    # publish this page as a duplicate of another one.
    for old, new, least in ((old_title, TITLE, 3),
                            (old_desc, DESC, 3),
                            (old_slug, SLUG, 2)):
        n = head.count(old)
        if n < least:
            raise SystemExit("template head carried %r %d time(s), expected at "
                             "least %d: the substitution is no longer safe"
                             % (old[:40], n, least))
        head = head.replace(old, esc(new) if "<" not in new else new)
    if old_slug in head or old_title in head:
        raise SystemExit("the template's own title or slug survived "
                         "substitution")
    return head


def article_title(slug):
    """The linked article's own title, read from the shipped page.

    So the link text describes where it goes. Seven links all reading
    "read more on this one" tell a screen-reader user cycling the link list
    nothing, and tell a search engine nothing about the destination either.
    Raises if the file is missing, because a cause pointing at an article
    that does not exist is a broken link this generator would otherwise
    emit on every run.
    """
    path = os.path.join(SITE, "articles", slug + ".html")
    if not os.path.exists(path):
        raise SystemExit("root_causes.py points %r at an article that does "
                         "not exist: %s" % (slug, path))
    s = io.open(path, encoding="utf-8").read()
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m:
        raise SystemExit("no <title> in %s" % path)
    return re.sub(r"[ \n\t]+", " ",
                  m.group(1)).split("|")[0].strip()


def cause_block():
    out = []
    for cid in CAUSE_ORDER:
        c = BY_ID[cid]
        out.append(
            '<h3>%s</h3>\n<p>%s</p>\n<p>%s</p>\n'
            '<p class="notice" style="max-width:60ch"><b>The thirty-second '
            'test.</b> %s</p>\n'
            '<p><a href="%s">%s</a></p>'
            % (esc(c["name"].title()), esc(c["meaning"]), esc(PICTURE[cid]),
               esc(c["confirm_30s"]), esc(c["article"]),
               esc(article_title(c["article"]))))
    return "\n\n".join(out)


def room_blocks():
    out = []
    for heading, room, slug, cid, why, then in ROOM_SECTIONS:
        c = BY_ID[cid]
        out.append(
            '<h2 id="%s">%s</h2>\n<p>%s</p>\n<p>%s</p>\n'
            '<p>The cause is usually <b>%s</b>: %s %s '
            '<a href="../rooms/%s">See the %s broken into its micro zones</a>.</p>'
            % (re.sub(r"[^a-z]+", "-", heading.lower()).strip("-"),
               esc(heading), esc(why), esc(then),
               esc(c["name"].lower()), esc(c["meaning"]),
               esc(c["confirm_30s"]), slug, esc(room.lower())))
    return "\n\n".join(out)


def faq_html():
    rows = "\n".join('<dt style="font-weight:600;margin-top:18px">%s</dt>\n'
                     '<dd style="margin:6px 0 0">%s</dd>' % (esc(q), esc(a))
                     for q, a in FAQ)
    return '<dl style="max-width:62ch">\n%s\n</dl>' % rows


def ld():
    url = "%s/articles/%s" % (BASE, SLUG)
    return json.dumps([
        {"@context": "https://schema.org", "@type": "Article",
         "@id": url + "#article", "url": url, "headline": TITLE,
         "description": DESC, "inLanguage": "en",
         # Dated, so ops/build_feed.py and ops/build_seo.py can see it.
         # An article with no date is silently left out of the Atom feed:
         # the feed carried 29 of 31 articles for exactly that reason.
         "datePublished": PUBLISHED, "dateModified": PUBLISHED,
         "isAccessibleForFree": True,
         "publisher": {"@type": "Organization", "name": "6S Success",
                       "url": BASE + "/"},
         "about": [{"@type": "Thing", "name": BY_ID[c]["name"].title()}
                   for c in CAUSE_ORDER]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Home",
              "item": BASE + "/"},
             {"@type": "ListItem", "position": 2, "name": "Articles",
              "item": BASE + "/articles/"},
             {"@type": "ListItem", "position": 3, "name": TITLE,
              "item": url}]},
        # The answers here are the visible text, character for character.
        # Structured data that says something the page does not is the
        # fabrication CLAUDE.md section 8 forbids, and it is also what gets a
        # site's rich results turned off.
        {"@context": "https://schema.org", "@type": "FAQPage",
         "@id": url + "#faq",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in FAQ]},
    ], indent=1)


BODY = """<nav class="crumb" style="font-family:var(--sans);font-size:13px;color:var(--soft);margin:26px 0 0"><a href="../index.html">Home</a> / <a href="../articles/">Articles</a> / Why is my house always messy</nav>
<div class="head" style="margin-top:10px">
<p class="eyebrow">The diagnosis</p>
<h1>Why is my house always messy?</h1>
<p class="lede">Because it is almost never the whole house. It is four or five small places failing for different reasons, and a tidy treats them all the same, which is why it never holds.</p></div>

<p class="notice" style="max-width:60ch"><b>The short answer.</b> Your house is probably not messy. Four or five small zones in it are, they are messy for different reasons, and tidying all of them the same way fixes none of them for long. Find the zones, name the reason for each one, and fix the reason.</p>

<h2>It is not the whole house, and that is the useful part</h2>
<p>Ask anyone who lives there to point at the three worst spots and you will have an answer in about four seconds, usually the same answer from everybody. The counter by the kettle. The chair in the bedroom. The shelf inside the front door. The table where the post lands.</p>
<p>That speed matters. A house that was uniformly messy would be hard to describe, and nobody describes it that way. They name places. Mess concentrates, and it concentrates in a small number of specific spots that do a particular job badly.</p>
<p>We call those micro zones, and there are about 114 of them across a normal home. On any given day most of them are fine. The reason a whole-house tidy feels endless and achieves so little is that it spends most of its effort on the ones that were already working.</p>

<h2>Tidying moves the objects. It does not change why they arrive</h2>
<p>Here is the test that separates a mess from a messy spot. Clear it completely, then watch it for a week. If it is back, nothing you did addressed why things land there, because the only thing that changed was the objects, and the objects were the symptom.</p>
<p>A spot that comes back is not a tidying failure. It is a design that is working exactly as built, and the useful question is not "how do I tidy this" but "what is this place doing that makes things stop here".</p>
<p>There are not many answers. After diagnosing 114 zones the same handful keeps coming up, and almost every chronically messy spot in a house is one or two of them.</p>

<h2>The seven reasons a zone keeps coming back</h2>
<p>Each one has a test you can run in about thirty seconds, standing in front of the spot. Run them in order and stop at the first one that is clearly true, because the first true answer is almost always the one doing the damage.</p>

__CAUSES__

<h2>The same question, room by room</h2>
<p>These are the four versions of this question people ask most. The diagnosis above is the same one; what changes is which cause dominates and what the fix looks like in that room.</p>

__ROOMS__

<h2>Why does my house feel messy even when it is clean?</h2>
<p>Because "clean" and "finished" are different states and only one of them is visible. A room can be genuinely clean, with nothing dirty anywhere, and still read as messy because the surfaces are carrying things that have no reason to be on them.</p>
<p>Visual noise is almost entirely a surface problem: the horizontal planes you see first when you walk in. A counter with eleven objects on it reads as mess at a glance even when every one of them is clean, and the same counter with three reads as calm. Nothing was cleaned in between.</p>
<p>If that is the gap you are feeling, the work is not cleaning and it is not decluttering the whole house. It is deciding what the two or three surfaces you see first are allowed to hold, which is a ten-minute conversation and then a standard.</p>

<h2>What to do tonight, in fifteen minutes</h2>
<p>Not the house. One zone, and specifically the one that annoys you most often rather than the one that looks worst, because the annoying one pays you back every day and the ugly one might be a cupboard you open twice a year.</p>
<ol style="max-width:62ch">
<li>Pick the spot. One surface, one drawer, one shelf.</li>
<li>Run the tests above until one is obviously true. That is the cause.</li>
<li>Take everything off it. Everything, not the top layer.</li>
<li>Put back only what has a reason to be there. Anything whose answer is "it lives somewhere else" goes to where it lives, now.</li>
<li>Say out loud what the spot looks like when it is finished, and if anybody else uses it, say it to them. That sentence is the standard.</li>
<li>Name the moment it gets reset: after dinner, before the bins, when the kettle goes on. That is the trigger, and without it you will be doing this again in a fortnight.</li>
</ol>
<p>Fifteen to forty-five minutes, one spot, done. Then leave the rest of the house alone until that one has held for a week, because a zone that holds teaches you more than four that do not.</p>
<p><a href="../quest.html">Start with one zone, free, in your browser</a>. It asks what is annoying you, works out the likely cause, and gives you the one job rather than the whole list. Nothing to install and nothing to sign up for.</p>

<h2>Common questions</h2>
__FAQ__

<h2>Keep reading</h2>
<ul style="max-width:62ch">
<li><a href="why-your-house-gets-messy-again">Why your house gets messy again a week after you clean it</a>, which is the other half of this: not why it is messy now, but why it goes back after you fix it.</li>
<li><a href="more-storage-wont-fix-clutter">More storage will not fix a messy room</a>, if the honest answer to the capacity test surprised you.</li>
<li><a href="where-to-start-decluttering">Where to start decluttering</a>, if the hard part is choosing the first spot.</li>
<li><a href="what-is-a-micro-zone">What a micro zone is</a>, and why it is the unit that actually finishes.</li>
<li><a href="../resources.html">All twenty rooms, broken into their micro zones</a>.</li>
</ul>
"""


def build():
    head, header, footer = chrome()
    head = retitle(head)
    body = (BODY.replace("__CAUSES__", cause_block())
                .replace("__ROOMS__", room_blocks())
                .replace("__FAQ__", faq_html()))
    page = (head + '<script type="application/ld+json">\n' + ld()
            + "\n</script>\n</head>" + header
            + '<main id="main" class="wrap">\n' + body + "</main>" + footer)
    return page


def main():
    page = build()
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(page)
    words = len(re.findall(r"[A-Za-z']+",
                           re.sub(r"(?is)<(script|style)\b.*?</\1>", " ",
                                  re.sub(r"<[^>]+>", " ", page))))
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("  %d bytes, about %d words of visible text" % (len(page), words))
    print("  %d causes, %d room sections, %d FAQ entries"
          % (len(CAUSE_ORDER), len(ROOM_SECTIONS), len(FAQ)))
    print("Now run: python ops/build_seo.py && python ops/fingerprint_assets.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
