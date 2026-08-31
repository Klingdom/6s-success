#!/usr/bin/env python3
"""
Build the two answer-engine articles at site/articles/.

Why this exists
---------------
The site has 114 micro zone pages that tell somebody how to do a thing. It has
no page that defines the method itself, and no page that sets an honest
expectation of how long the work takes. Those are the two questions an
assistant gets asked before anybody ever reaches a how-to page:

    "what is 6S"
    "how long does it actually take to organise a room"

Both pages answer in the opening paragraph, because that is the part that gets
quoted, and both carry FAQPage structured data whose answers match the visible
text.

Every number on the timing page is arithmetic on
content/manual/source/content.json. Nothing is estimated. If a session length
changes in the manual, rerun this and the article changes with it.

There is deliberately no whole-house total. The manual refuses to give one and
so does this page; the reasoning is written out on the page itself.

Run:  python ops/build_articles.py
"""
import html
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "articles")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
BASE = "https://6s-success.com"
UMAMI = ('<script defer src="/stats/script.js" '
         'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
         'data-host-url="https://6s-success.com/stats"></script>')
Z = "../zones/"
R = "../rooms/"


def esc(t):
    return html.escape(str(t or ""), quote=True)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


def load_chrome():
    """Same chrome as every other page, lifted from resources.html so these two
    cannot drift from the site. They sit one directory down, so relative links
    get a ../ prefix."""
    src = io.open(os.path.join(SITE, "resources.html"), encoding="utf-8").read()
    head = src[src.find('<header class="site-header">'):src.find("</header>") + 9]
    foot = src[src.find('<footer class="site-footer">'):src.find("</footer>") + 10]

    def up(frag):
        return re.sub(r'(href|src)="(?!https?:|#|mailto:|/)([^"]+)"',
                      r'\1="../\2"', frag)
    return up(head), up(foot)


# ---------------------------------------------------------------- timing data

def minutes(session):
    lo, hi = re.match(r"(\d+)-(\d+)\s*min", session).groups()
    return int(lo), int(hi)


def hm(m):
    """255 -> '4 h 15'. Whole hours drop the minutes."""
    h, r = divmod(m, 60)
    if h == 0:
        return "%d min" % r
    if r == 0:
        return "%d h" % h
    return "%d h %d" % (h, r)


def span(lo, hi):
    return "%s to %s" % (hm(lo), hm(hi))


def timing(rooms):
    out = []
    for r in rooms:
        lo = hi = 0
        for zone in r["zones"]:
            a, b = minutes(zone["session"])
            lo += a
            hi += b
        out.append({"room": r["room"], "slug": slug(r["room"]),
                    "zones": len(r["zones"]), "lo": lo, "hi": hi})
    return out


def bands(rooms):
    b = {}
    for r in rooms:
        for zone in r["zones"]:
            b[zone["session"]] = b.get(zone["session"], 0) + 1
    return sorted(b.items(), key=lambda kv: minutes(kv[0]))


def sort_heavy(rooms):
    """How many of the 114 zones name Sort as the step that eats the session.
    Counted strictly on the phrase, so the number is defensible."""
    n = 0
    for r in rooms:
        for zone in r["zones"]:
            if re.search(r"\bin Sort\b", zone.get("time_note", ""), re.I):
                n += 1
    return n


# ------------------------------------------------------------------- assembly

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

SAFETY = """<aside class="notice" style="margin:36px 0 0">
<b>Before you start.</b> This is guidance for organising and cleaning a home. It
is not instruction for electrical, gas, structural, or any other licensed work.
Do not lift or move anything unsafe, do not mix cleaning products, and follow the
label on anything you use. If a job needs a professional, that is the right
answer. See the <a href="../disclaimer.html">full safety notice</a>.
</aside>"""

# site.css has never had a table, because until now no page needed one. Scoped
# to .tbl so it cannot leak into the design system.
TABLE_CSS = """<style>
.tbl{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:15px;
  margin:16px 0 8px}
.tbl caption{caption-side:top;text-align:left;font-size:13.5px;color:var(--soft);
  padding:0 0 12px;max-width:64ch}
.tbl th,.tbl td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}
.tbl thead th{font-size:12px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:var(--soft);border-bottom:2px solid var(--line-2)}
.tbl .num{text-align:right;font-variant-numeric:tabular-nums}
.tbl tbody tr:hover{background:var(--panel)}
.tbl a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line-2)}
.tbl a:hover{color:var(--terra);border-color:var(--terra)}
@media (max-width:560px){.tbl th,.tbl td{padding:8px 5px;font-size:14px}}
</style>"""


# Same shape and the same tone as the offer on every zone page: the method is
# given away in full, the price is named once, and nothing is manufactured to
# make anybody hurry.
def offer(lead):
    return ('<section class="band" style="margin:44px 0 0;padding:26px 28px;'
            'border-radius:22px">'
            '<p class="eyebrow on-deep">If a zone keeps coming undone</p>'
            '<h2 style="margin:0 0 10px">Have us run a room with you</h2>'
            '<p style="margin:0 0 16px;max-width:62ch">The method above is '
            'complete and free, and ' + lead + ' Some zones fight back, and it '
            'is usually because the real problem sits somewhere else in the '
            'room. If that is where you are, a one hour virtual consult is 250 '
            'dollars: we find the function, the friction and the root cause '
            'together, and you keep a written standard for the space.</p>'
            '<p style="margin:0"><a class="btn btn-primary" '
            'href="../consulting.html">See what a consult covers</a>'
            '<a class="btn btn-on-deep" style="margin-left:10px" '
            'href="../resources.html">Or work a zone, free</a></p></section>')


def crumb(pairs):
    bits = [('<a href="%s">%s</a>' % (h, esc(n)) if h else esc(n))
            for n, h in pairs]
    return ('<nav class="crumb" style="font-family:var(--sans);font-size:13px;'
            'color:var(--soft);margin:26px 0 0">' + " / ".join(bits) + "</nav>")


# Same @id ops/build_product_schema.py assigns the Virtual Home Consult's
# Product node on shop.html (every SKU gets "@id": BASE + "/shop.html#" + sku,
# regardless of which page it also renders on, so this is the same node
# consulting.html's copy of it points at too). Both articles built below end
# with offer(), which names this exact consult and its exact price, so the
# Article node names the product it is actually offering rather than leaving
# that connection only in prose a machine has to re-read to find.
CONSULT_ID = BASE + "/shop.html#CN-VIRTUAL"


def graph(url, title, desc, crumbs, faq):
    return json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n,
                 "item": BASE + u} for i, (n, u) in enumerate(crumbs)]},
            {"@type": "Article", "@id": url + "#article", "headline": title,
             "description": desc, "mainEntityOfPage": url,
             "inLanguage": "en", "isAccessibleForFree": True,
             "author": {"@type": "Organization", "name": "6S Success",
                        "url": BASE + "/about.html"},
             "publisher": {"@type": "Organization", "name": "6S Success",
                           "url": BASE + "/"},
             "mentions": [{"@id": CONSULT_ID}]},
            {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq]},
        ]}, indent=1, ensure_ascii=False)


def write(fname, title, desc, ld, body):
    header, footer = load_chrome()
    url = "%s/articles/%s" % (BASE, fname[:-5])
    doc = (HEAD_TPL.format(title=esc(title), desc=esc(desc), url=url,
                           BASE=BASE, ld=ld)
           + header + '\n<main class="wrap">\n' + body + "\n</main>\n"
           + footer + "\n\n" + UMAMI
           + '\n<script src="../assets/js/data.js"></script>'
           + '<script src="../assets/js/site.js"></script></body></html>\n')
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    path = os.path.join(OUT, fname)
    io.open(path, "w", encoding="utf-8", newline="\n").write(doc)
    return path, doc


def zlink(fn, label):
    return '<a href="%s%s.html">%s</a>' % (Z, fn, label)


def step(i, name, why, txt):
    return ('<section style="margin:26px 0"><h3>%d. %s</h3>'
            '<p class="notice" style="margin:0 0 10px">%s</p>'
            '<p>%s</p></section>' % (i, name, why, txt))


# ========================================================= article 1: what 6S is

A1_FILE = "what-is-6s.html"
A1_TITLE = "What is 6S? The six steps, and how it differs from 5S"
A1_DESC = ("6S is Sort, Straighten, Shine, Safety, Standardize, Sustain, in "
           "that order. What each step does, why Safety is fourth, and how "
           "it differs from 5S.")

A1_ANSWER = ("6S is a six-step method for making the right thing easy to find, "
             "easy to use and safe in a space, and then keeping it that way. "
             "The steps are Sort, Straighten, Shine, Safety, Standardize and "
             "Sustain, always in that order. It is the factory practice known "
             "as 5S with Safety added, and placed fourth rather than last.")

A1_FAQ = [
    ("What is 6S?",
     "6S is a six-step method for making the right thing easy to find, easy to "
     "use and safe in a space, and then keeping it that way. The steps are "
     "Sort, Straighten, Shine, Safety, Standardize and Sustain, always in that "
     "order. It is the factory practice known as 5S with Safety added, and "
     "placed fourth rather than last."),
    ("What is the difference between 6S and 5S?",
     "5S is the original five steps that came out of Japanese manufacturing: "
     "Sort, Straighten, Shine, Standardize and Sustain. 6S adds Safety as a "
     "step of its own rather than leaving it as an assumption. In the 6S "
     "Success method Safety is the fourth step, worked after Shine and before "
     "Standardize, so it can still change the layout instead of only commenting "
     "on one that is already set."),
    ("Why is Safety the fourth S and not the last one?",
     "Because the first three steps are what make the hazards visible, and the "
     "fifth step is what makes the arrangement permanent. Sort empties the "
     "space, Straighten arranges it and Shine cleans it, so by the fourth step "
     "you can see the overloaded socket, the chemical at child height and the "
     "heavy box stored above a head. Placed last, Safety can only comment on a "
     "layout that is already fixed."),
    ("How is 6S different from tidying or decluttering?",
     "Cleaning removes dirt but decides nothing about where things live, so it "
     "lasts hours. Tidying and decluttering arrange the things you own without "
     "building the system that keeps them arranged, so they last weeks. 6S "
     "includes both and then adds the three steps they leave out: Safety, "
     "Standardize and Sustain. Those are the steps that decide whether the "
     "result survives a busy week."),
    ("Where does 6S come from?",
     "From the Toyota Production System developed in Japan after the Second "
     "World War, and specifically from the idea of the visual workplace: set a "
     "space up so anyone can glance at it and tell whether things are where "
     "they should be. The five practices were later named 5S and spread into "
     "hospitals, aircraft maintenance, offices and eventually homes. Safety was "
     "added as a sixth by organisations that refused to leave it implied."),
    ("Does 6S mean my home has to look like a factory?",
     "No. 6S borrows the logic of the factory, not the look of it. The logic is "
     "that the right action should be the easy action, that normal should be "
     "visible so abnormal shows up early, and that the people using the space "
     "should be protected. A home applies that with a tray by the door and a "
     "hook for each person, not with floor tape and shadow boards."),
]

A1_STEPS = [
    ("Sort", "Keep what serves the space, route out the rest.",
     "Take everything out where you can see it, then give every object one of "
     "three verdicts: keep, relocate, or release. You are not organising yet, "
     "you are deciding. This is the step that makes every later step smaller, "
     "which is why an hour in Sort saves several hours of arranging and "
     "cleaning things you were about to remove. It is also the step people skip "
     "by buying containers first, which only gives the clutter a nicer place to "
     "live."),
    ("Straighten", "A home for everything, chosen by how it is used.",
     "Everything that survived Sort gets a deliberate home, and the rule that "
     "decides those homes is frequency of use. Daily things get the easy reach, "
     "monthly things move back, twice-a-year things go up or out. This is the "
     "difference between a space that is tidy and a space that is easy. Tidy "
     "means everything looks lined up. Easy means the thing you need most is "
     "the thing your hand reaches first. The test is whether somebody who has "
     "never opened this cupboard finds the dish soap on the first try."),
    ("Shine", "Clean to inspect, not just to impress.",
     "Cleaning is the only time you see a space empty, so it is the only "
     "reliable chance you get to inspect it. Wiping a surface slowly is also "
     "running your eyes and hands across every inch of it, and that is when the "
     "slow leak, the soft patch of board, the frayed cord and the loose hinge "
     "finally show themselves. Cleaning done at speed tells you nothing. In 6S, "
     "Shine flags what it finds and hands it to the next step rather than "
     "stopping to fix it."),
    ("Safety", "The step that protects everything else.",
     "Fix what the first three steps just made visible: the chemical at "
     "grabbing height, the socket carrying three things, the heavy box stored "
     "above a head, the rug that slides, the cord across a walking line. Crouch "
     "while you do it, because most of the hazards in a house sit at the height "
     "of the shortest person living there. At work somebody is paid to spot "
     "these. At home, the inspector is you."),
    ("Standardize", "Make the right state obvious at a glance.",
     "The arrangement you just built currently exists only in your head, and "
     "your head is busy. Standardize moves it out into the open, usually as a "
     "photograph of the finished state taped where people already glance, "
     "sometimes as a label or a cap on a number. This is the visual workplace "
     "idea shrunk to one cupboard door: make normal visible so abnormal becomes "
     "obvious, and the space corrects itself without anybody having to nag."),
    ("Sustain", "Design the habit, do not rely on willpower.",
     "A standard that needs a weekly overhaul was a bad standard. Sustain "
     "attaches a small reset to something that already happens, so nobody has "
     "to remember it as a separate task: the paper folder comes with you when "
     "you sit down after dinner, the bench gets cleared before the safety "
     "glasses come off. Sustain does not end the method. It hands you back to "
     "Sort, because a home is alive and its contents keep changing."),
]


def article_one():
    b = []
    b.append(crumb([("Home", "../index.html"),
                    ("The Method", "../method.html"),
                    ("What is 6S", None)]))
    b.append('<div class="head" style="margin-top:10px">'
             '<p class="eyebrow">The method, defined</p>'
             '<h1>What is 6S, and how is it different from 5S and from '
             'tidying?</h1></div>')
    b.append("<p><b>" + A1_ANSWER + "</b></p>")
    b.append('<p class="notice" style="max-width:62ch">The short version of the '
             'difference: cleaning removes dirt, tidying arranges the things you '
             'own, and 6S builds the system that keeps a space arranged, clean '
             'and safe without anybody having to be heroic about it.</p>')

    b.append("<h2>What are the six steps of 6S?</h2>")
    b.append("<p>Six steps, always in this order. The order is not decoration. "
             "Each step cuts the work of the next: sorting first means you "
             "straighten fewer things, straightening first means you clean "
             "around less, and Safety lands at the point where it can still "
             "change the layout rather than merely comment on it.</p>")
    for i, (name, why, txt) in enumerate(A1_STEPS, 1):
        b.append(step(i, name, why, txt))
    b.append('<p class="notice" style="max-width:62ch">A note on the names. '
             'Different books translate the original Japanese words '
             'differently, so you will see the second step called several '
             'things. We say <b>Straighten</b> everywhere, and <b>Safety</b> is '
             'the fourth S everywhere. The words are handles. The order is the '
             'method.</p>')

    b.append("<h2>What is the difference between 6S and 5S?</h2>")
    b.append("<p>5S is the original five: Sort, Straighten, Shine, Standardize, "
             "Sustain, from the Japanese seiri, seiton, seiso, seiketsu and "
             "shitsuke. 6S is those five with Safety added as a step of its own "
             "instead of an assumption. You will sometimes see it written as 5S "
             "plus 1, which is a fair description of how it happened. "
             "Organisations running the method in real workplaces kept arriving "
             "at the same conclusion: none of the rest of it matters if "
             "somebody gets hurt.</p>")
    b.append("<p>The second difference is placement, and that is the one that "
             "changes the work. Where workplace programmes do include Safety, "
             "it is commonly bolted on at the end, after the standard is set, "
             "which turns it into an audit rather than a decision. Plenty of 5S "
             "implementations leave it out entirely and treat it as somebody "
             "else's department. We make it the fourth step, in the middle of "
             "the loop, for the reason below.</p>")

    b.append("<h2>Why is Safety the fourth S and not the last?</h2>")
    b.append("<p>Because you cannot see the hazards until the first three steps "
             "have run, and you cannot act on them cheaply once the fifth has. "
             "While a cupboard is full, the drain cleaner at the front is just "
             "one more bottle in the chaos. Sort empties it, Straighten "
             "arranges it, Shine cleans it, and only then is the space honest "
             "enough to show you that the bottle sits at the exact height of a "
             "two-year-old, behind a door that does not latch. Move it now and "
             "it costs a minute. Move it after Standardize and you are "
             "unpicking a standard you just set.</p>")
    b.append("<p>This matters more at home than at work, which is the "
             "uncomfortable part. A workplace has inspectors, rules and "
             "somebody whose job it is to walk the floor. A house has children, "
             "medicines, heavy things stored above head height, cleaning "
             "chemicals under the sink, extension leads behind furniture, and "
             "stairs that people walk in the dark. Nobody is coming to audit "
             "any of it. The same walk-through that organises a space is the "
             "one realistic chance you get to secure it, because your hands are "
             "already on everything.</p>")
    b.append("<p>These are the zones where the Safety step usually earns its "
             "place first:</p>")
    b.append("<ul>"
             "<li>" + zlink("primary-bathroom-the-medicine-cabinet",
                            "The Medicine Cabinet") +
             ", where dates, look-alike boxes and reachable height all land in "
             "one small space</li>"
             "<li>" + zlink("primary-bathroom-the-under-sink-cabinet",
                            "The Under-Sink Cabinet") +
             ", the standard place a household stores what can burn or poison, "
             "at floor level</li>"
             "<li>" + zlink("family-room-the-charging-and-device-zone",
                            "The Charging and Device Zone") +
             ", where lithium batteries, soft furnishings and one overloaded "
             "socket meet</li>"
             "<li>" + zlink("stair-landing-the-stair-and-floor-path",
                            "The Stair and Floor Path") +
             ", where the session is spent walking the flight tread by tread "
             "rather than organising anything</li>"
             "<li>" + zlink("nursery-the-crib-and-sleep-zone",
                            "The Crib and Sleep Zone") +
             ", where what is absent matters more than what is arranged</li>"
             "<li>" + zlink("garage-the-power-tool-and-battery-zone",
                            "The Power Tool and Battery Zone") +
             ", chargers, battery packs and fuel-adjacent storage in one "
             "corner</li>"
             "<li>" + zlink("garage-the-bulk-and-overhead-storage",
                            "The Bulk and Overhead Storage") +
             ", the zone where weight is stored above people</li>"
             "<li>" + zlink("workshop-the-safety-and-ppe-station",
                            "The Safety and PPE Station") +
             ", the one zone that exists only for this step</li>"
             "</ul>")

    b.append("<h2>How is 6S different from tidying, cleaning and "
             "decluttering?</h2>")
    b.append("<p>Most of us own two tools for a house that has become hard to "
             "live in. We clean it, or we organise it. Both are good things to "
             "do. Neither is this method, and the difference is mostly shelf "
             "life.</p>")
    b.append("<ul>"
             "<li><b>Cleaning</b> removes dirt. It makes a space healthy and "
             "pleasant and it decides nothing about where anything lives. You "
             "can clean a chaotic room beautifully and still not find the "
             "scissors. A clean mess is still a mess, and it lasts about as "
             "long as it takes for one ordinary day to happen.</li>"
             "<li><b>Tidying and organising</b> arrange the things you own. The "
             "before and after is genuinely satisfying, and it usually does not "
             "hold, because it arranges the stuff without building the system "
             "that keeps it arranged. Three weeks later the closet has quietly "
             "collapsed back into its old shape and you conclude, wrongly, that "
             "you are bad at this.</li>"
             "<li><b>Decluttering</b> asks each object to justify its "
             "relationship to your entire life. Do I still like this, will I "
             "use it someday, who gave it to me. That is an exhausting way to "
             "spend a Saturday, and it is why so many attempts stall in three "
             "half-sorted piles.</li>"
             "<li><b>6S</b> contains the useful parts of all three and adds "
             "what they leave out. Sort asks one small, answerable question "
             "instead of a large one: does this help this space do its job. "
             "Shine cleans and inspects at the same time. Then Safety, "
             "Standardize and Sustain decide whether any of it survives the "
             "next busy week.</li>"
             "</ul>")
    b.append("<p>Put simply: cleaning and tidying are events you perform on a "
             "space. 6S is a system you give a space, once, so it can mostly "
             "look after itself afterwards. And if a drawer will not stay fixed "
             "no matter how many times you redo it, you did not fail at "
             "willpower. You skipped a step, and it is usually Sort or "
             "Standardize.</p>")

    b.append("<h2>Where did 6S come from, and what transfers to a house?</h2>")
    b.append("<p>In the years after the Second World War, Toyota was trying to "
             "compete with much larger and much richer rivals. They could not "
             "win by spending more, so they had to win by wasting less: less "
             "material, less motion, less searching. Out of that came the "
             "Toyota Production System, and inside it the idea of the visual "
             "workplace. Set a space up well and anyone can glance at it and "
             "tell whether things are where they should be. The tool is "
             "outlined on the board, so a missing tool leaves an obvious gap. "
             "Normal becomes visible, which means abnormal becomes visible too, "
             "and problems get caught early instead of festering.</p>")
    b.append("<p>The five practices underneath that were later named 5S, and "
             "the name travelled a long way from cars: into hospitals, where a "
             "missing instrument is an emergency, into aircraft maintenance, "
             "where a tool left in an engine costs lives, and then into "
             "offices, laboratories, kitchens and eventually homes. Safety was "
             "added by organisations that would not leave it implied.</p>")
    b.append("<p><b>What transfers to a house:</b></p>")
    b.append("<ul>"
             "<li>Make the right action the easy action, and the wrong action "
             "obvious.</li>"
             "<li>Make normal visible, so a space corrects itself without a "
             "person policing it.</li>"
             "<li>Clean in order to inspect, not only to impress.</li>"
             "<li>Protect the people who use the space, including the shortest "
             "one.</li>"
             "<li>The loop does not change with scale. The same six steps work "
             "on a drawer, a shelf, a room and a garage. Only the time "
             "changes.</li>"
             "</ul>")
    b.append("<p><b>What does not transfer:</b></p>")
    b.append("<ul>"
             "<li><b>The look.</b> No floor tape, no shadow boards on the "
             "kitchen wall, no label maker gone rogue. A well-run home is not "
             "an empty one, and organised does not mean bare. The fruit bowl "
             "and the art on the fridge are the life the method exists to "
             "protect.</li>"
             "<li><b>The enforcement.</b> A factory has shifts, supervisors and "
             "audits. A home has tired people at seven in the morning, which is "
             "why Sustain has to hook onto something that already happens "
             "rather than onto anybody remembering.</li>"
             "<li><b>The goal.</b> A plant optimises throughput. A home is for "
             "the people in it, and two households will want the same room to "
             "do genuinely different things. Function comes before "
             "organisation, every time, which is why the first question is "
             "what this space is for and not which containers to buy.</li>"
             "<li><b>Sole ownership.</b> Some zones are shared, and at least "
             "one in most houses is not yours to decide about. That is a "
             "conversation, not a standard you impose.</li>"
             "</ul>")

    b.append("<h2>How do you actually start?</h2>")
    b.append("<p>Pick one zone. Not a room, not a floor. One zone: a drawer, a "
             "shelf, the strip of counter beside the kettle. Small enough that "
             "you finish, because a finished zone is proof, and proof is what "
             "carries you to the next one. Read the whole card before you touch "
             "anything, including the part describing what done looks like, "
             "then work the six steps in order without skipping ahead to the "
             "satisfying ones.</p>")
    b.append("<p>Start with the entryway if you have no strong preference. It "
             "is small, it is fast, and your household crosses it twice a day, "
             "so the payoff shows up before anyone has time to lose faith in "
             "the project. Good first zones:</p>")
    b.append("<ul>"
             "<li>" + zlink("entryway-the-landing-spot",
                            "The Landing Spot in the Entryway") +
             ", a 30-45 min session, most of it spent deciding what happens to "
             "paper</li>"
             "<li>" + zlink("living-room-the-coffee-table",
                            "The Coffee Table in the Living Room") +
             ", a 15-30 min session and one of the shortest in the model</li>"
             "<li>" + zlink("kitchen-the-utensil-and-utility-drawers",
                            "The Utensil and Utility Drawers") +
             ", quick per drawer, and the clearest demonstration of what Sort "
             "is for</li>"
             "<li>" + zlink("hall-closet-the-cleaning-supply-zone",
                            "The Cleaning Supply Zone") +
             ", where Sort and Safety do the work together</li>"
             "</ul>")
    b.append('<p>The full model is 20 rooms broken into 114 micro zones, each '
             'one sized to finish in a single sitting. You can '
             '<a href="../resources.html">work through every room and micro '
             'zone free</a>, or read '
             '<a href="how-long-does-it-take-to-organise-a-room.html">how long '
             'a room actually takes</a> before you give an afternoon to '
             'one.</p>')

    b.append(SAFETY)
    b.append("<h2>Keep going</h2>")
    b.append("<ul>"
             '<li><a href="../method.html">The six steps in full</a>, with the '
             "worked example each one came from</li>"
             '<li><a href="../resources.html">All 20 rooms and 114 micro '
             "zones</a>, in the order to work them</li>"
             '<li><a href="how-long-does-it-take-to-organise-a-room.html">How '
             "long it takes to organise a room</a>, with the real session time "
             "for every room</li>"
             '<li><a href="why-your-house-gets-messy-again.html">Why a room '
             'gets messy again</a>, the two steps this page only defines</li>'
             '<li><a href="tidy-is-not-the-same-as-safe.html">Why tidy is '
             'not the same as safe</a>, the check the fourth step above runs '
             'on its own</li>'
             '<li><a href="../book.html">6S Success: Home Edition</a>, the 50 '
             "chapters this page summarises</li>"
             "</ul>")
    b.append(offer("most people can work a single zone from it in one session "
                   "without any help from us."))

    ld = graph(BASE + "/articles/what-is-6s", A1_TITLE, A1_DESC,
               [("Home", "/"), ("The Method", "/method.html"),
                ("What is 6S", "/articles/what-is-6s")], A1_FAQ)
    return write(A1_FILE, A1_TITLE, A1_DESC, ld, "\n".join(b))


# ======================================================= article 2: how long

A2_FILE = "how-long-does-it-take-to-organise-a-room.html"
A2_TITLE = ("How long does it actually take to organise a room? | 6S Success")
A2_DESC = ("Real session times for all 20 rooms, summed from the 114 micro "
           "zones. A room is 3 to 7 sessions, not one afternoon, and that is "
           "why whole-room attempts fail.")


def article_two(rooms):
    t = timing(rooms)
    by_room = {x["room"]: x for x in t}
    total_zones = sum(x["zones"] for x in t)
    shortest = min(t, key=lambda x: x["hi"])
    longest = max(t, key=lambda x: x["hi"])
    los = sorted(x["lo"] for x in t)
    his = sorted(x["hi"] for x in t)
    med_lo = (los[9] + los[10]) // 2
    med_hi = (his[9] + his[10]) // 2
    bnd = bands(rooms)
    sh = sort_heavy(rooms)
    min_z = min(x["zones"] for x in t)
    max_z = max(x["zones"] for x in t)

    answer = ("A room takes %s to %s of hands-on work, depending which room it "
              "is, and it is never a single job. The 6S model splits a home "
              "into %d micro zones across 20 rooms, and each zone carries its "
              "own session of 15 to 90 minutes. A room is %d to %d of those "
              "sessions, worked on separate days." %
              (hm(shortest["lo"]), hm(longest["hi"]), total_zones,
               min_z, max_z))

    faq = [
        ("How long does it take to organise a room?",
         "Between %s and %s of hands-on work depending on the room, split "
         "across %d to %d separate sessions. The median room in the 6S model "
         "takes %s. The %s is the shortest at %s across %d zones, and the %s is "
         "the longest at %s across %d zones." %
         (hm(shortest["lo"]), hm(longest["hi"]), min_z, max_z,
          span(med_lo, med_hi), shortest["room"].lower(),
          span(shortest["lo"], shortest["hi"]), shortest["zones"],
          longest["room"].lower(), span(longest["lo"], longest["hi"]),
          longest["zones"])),
        ("How long does it take to organise a kitchen?",
         "A kitchen is %d micro zones and totals %s of hands-on work. That is "
         "not one day. It is %d sessions, and the longest single one is the "
         "refrigerator and freezer at 60-90 min." %
         (by_room["Kitchen"]["zones"],
          span(by_room["Kitchen"]["lo"], by_room["Kitchen"]["hi"]),
          by_room["Kitchen"]["zones"])),
        ("How long does it take to organise a garage?",
         "A garage is %s of hands-on work across %d micro zones, which makes it "
         "the longest room in the model by a wide margin. Six of its seven "
         "zones are 60-90 min sessions. Anyone telling you a garage is a "
         "weekend is describing a weekend of full days." %
         (span(by_room["Garage"]["lo"], by_room["Garage"]["hi"]),
          by_room["Garage"]["zones"])),
        ("Why can I not organise a whole room in one day?",
         "You can start one, and that is usually the problem. Most home "
         "projects fail on scope rather than on effort: you set out to do the "
         "kitchen, you are four hours in with every cupboard on the floor, and "
         "dinner still has to happen. A room is not a unit of work. A micro "
         "zone is, because it is small enough to finish, and finishing is what "
         "carries you to the next one."),
        ("What is the longest single session in the method?",
         "90 minutes. Every one of the %d micro zones is sized to finish in a "
         "single sitting, and the longest band is 60-90 min, which covers %d "
         "zones. The shortest band is 15-30 min and covers %d zones." %
         (total_zones, dict(bnd).get("60-90 min", 0),
          dict(bnd).get("15-30 min", 0))),
        ("How long does it take to organise a whole house?",
         "We do not publish a whole-house figure, on purpose. No house has all "
         "20 rooms, no two garages hold the same amount, and a single large "
         "number is the exact thing that stops people starting. The useful "
         "number is the next session, which is 15 to 90 minutes."),
    ]

    b = [TABLE_CSS]
    b.append(crumb([("Home", "../index.html"),
                    ("Rooms", "../resources.html"),
                    ("Micro zones", "../zones/"),
                    ("How long a room takes", None)]))
    b.append('<div class="head" style="margin-top:10px">'
             '<p class="eyebrow">Honest numbers</p>'
             '<h1>How long does it actually take to organise a room?</h1></div>')
    b.append("<p><b>" + answer + "</b></p>")
    b.append('<p class="notice" style="max-width:64ch">Where these numbers come '
             'from: every one of the %d micro zones in the '
             '<a href="../resources.html">6S micro zone model</a> carries a '
             'session length written when the method for that zone was written. '
             'The room totals below are those session lengths added up. They '
             'are hands-on time only. They do not include shopping, repairs you '
             'flag along the way, or the days in between.</p>' % total_zones)

    b.append("<h2>How long does each room take?</h2>")
    b.append("<p>Twenty rooms, %d micro zones, sorted here in the order the "
             "manual works them. The total column is the sum of that room's "
             "session times, low end to high end.</p>" % total_zones)

    rows = []
    for x in t:
        rows.append("<tr><th scope=\"row\"><a href=\"%s%s.html\">%s</a></th>"
                    "<td class=\"num\">%d</td><td>%s</td></tr>"
                    % (R, x["slug"], esc(x["room"]), x["zones"],
                       span(x["lo"], x["hi"])))
    b.append('<table class="tbl">'
             "<caption>Hands-on time per room, summed from the session length "
             "of every micro zone in it. Split across as many sessions as the "
             "room has zones.</caption>"
             "<thead><tr><th scope=\"col\">Room</th>"
             "<th scope=\"col\" class=\"num\">Micro zones</th>"
             "<th scope=\"col\">Realistic total, hands on</th></tr></thead>"
             "<tbody>" + "".join(rows) + "</tbody></table>")
    b.append("<p>The middle of that table is where most homes live. The median "
             "room is %s across five or six zones. If you want one number to "
             "carry in your head, carry that one, and then ignore it in favour "
             "of the only number you can act on today, which is the length of "
             "the next session.</p>" % span(med_lo, med_hi))

    b.append("<h2>Why is a room several sessions instead of one day?</h2>")
    b.append("<p>Because most home projects fail on scope, not on effort. The "
             "usual shape of the failure is familiar: you set out to do the "
             "kitchen on a Saturday, you are four hours in with every cupboard "
             "emptied onto the floor, everyone is tired, and dinner still has "
             "to happen. Nothing is finished, the room is worse than when you "
             "started, and the conclusion you draw is that you are bad at "
             "this.</p>")
    b.append("<p>You are not. The room beat you because a room is not a unit of "
             "work. A micro zone is: one drawer, one shelf, the strip of "
             "counter beside the kettle. Small enough that you finish, and "
             "finishing is the whole point, because a finished zone is proof "
             "and proof is what funds the next one. A room of six zones is six "
             "small finished things, not one enormous unfinished one.</p>")
    b.append("<p>There is a rule attached to this that people find harder than "
             "the work: <b>stop when the zone is done, and resist the pull into "
             "the next zone on the same day.</b> The pull is real, because "
             "finishing feels good and the next shelf is right there. Taking it "
             "is how a 30 minute win turns into the four hour collapse "
             "above.</p>")

    b.append("<h2>How long is a single session?</h2>")
    b.append("<p>Every zone falls into one of four bands. Nothing in the method "
             "is longer than 90 minutes, because past that point people stop "
             "finishing.</p>")
    brows = []
    labels = {
        "15-30 min": ("Surfaces and small single-purpose zones", "living-room-the-coffee-table", "The Coffee Table"),
        "30-45 min": ("The common case: one drawer, one shelf, one surface with decisions on it", "entryway-the-landing-spot", "The Landing Spot"),
        "45-75 min": ("Zones where reading, dating or pairing slows every item down", "primary-bathroom-the-medicine-cabinet", "The Medicine Cabinet"),
        "60-90 min": ("Zones where everything has to come out onto the floor first", "home-office-the-file-storage", "The File Storage"),
    }
    for sess, n in bnd:
        what, fn, label = labels[sess]
        brows.append("<tr><th scope=\"row\">%s</th><td class=\"num\">%d</td>"
                     "<td>%s. Example: %s</td></tr>"
                     % (sess, n, what, zlink(fn, label)))
    b.append('<table class="tbl">'
             "<caption>The four session bands, and how many of the %d micro "
             "zones sit in each.</caption>"
             "<thead><tr><th scope=\"col\">Session</th>"
             "<th scope=\"col\" class=\"num\">Zones</th>"
             "<th scope=\"col\">What lands here</th></tr></thead>"
             "<tbody>" % total_zones + "".join(brows) + "</tbody></table>")

    b.append("<h2>Which room takes the longest?</h2>")
    b.append("<p>The garage, and it is not close. %s across %d zones, which is "
             "more than double the median room. The reason is visible in the "
             "session lengths: six of its seven zones are 60-90 min, because "
             "every one of them needs its contents brought down to floor level "
             "before a single decision can be made. The "
             "%s alone is a full 60-90 min session, and so is the "
             "%s.</p>"
             % (span(by_room["Garage"]["lo"], by_room["Garage"]["hi"]),
                by_room["Garage"]["zones"],
                zlink("garage-the-bulk-and-overhead-storage",
                      "bulk and overhead storage"),
                zlink("garage-the-power-tool-and-battery-zone",
                      "power tool and battery zone")))
    b.append("<p>Behind it: the workshop at %s, then the kitchen and the patio "
             "or deck, both at %s. If somebody tells you a garage is a weekend, "
             "they are describing a weekend of full working days, and they are "
             "describing exactly the attempt that fails.</p>"
             % (span(by_room["Workshop"]["lo"], by_room["Workshop"]["hi"]),
                span(by_room["Kitchen"]["lo"], by_room["Kitchen"]["hi"])))

    b.append("<h2>Which room is quickest, and where should you start?</h2>")
    b.append("<p>The %s is the shortest room in the model at %s, because it has "
             "only %d zones. The guest bathroom is next at %s.</p>"
             % (shortest["room"].lower(),
                span(shortest["lo"], shortest["hi"]), shortest["zones"],
                span(by_room["Guest Bathroom"]["lo"],
                     by_room["Guest Bathroom"]["hi"])))
    b.append("<p>Neither is where we suggest you start. Start with the "
             "<a href=\"%sentryway.html\">entryway</a>, %s across %d zones, "
             "because it is the room your household crosses twice a day. The "
             "payoff shows up on the hallway floor within a week, before anyone "
             "has had time to lose faith in the project. Belief is a resource "
             "and the early rooms are how you fund it. After that, go wherever "
             "the friction is loudest: the zone you swear at on a Tuesday "
             "morning is worth more than the one that merely looks untidy on a "
             "Sunday.</p>"
             % (R, span(by_room["Entryway"]["lo"], by_room["Entryway"]["hi"]),
                by_room["Entryway"]["zones"]))
    b.append("<p>Inside the entryway, the shortest zone is the "
             "%s. It gives you somewhere to stand while you work the other "
             "four.</p>"
             % zlink("entryway-the-door-mat-and-immediate-floor",
                     "door mat and immediate floor"))

    b.append("<h2>Why does Sort take most of the time?</h2>")
    b.append("<p>Of the %d micro zones, <b>%d name Sort as the step that takes "
             "most of the session</b>. That is not because Sort involves more "
             "lifting. It is because Sort is where the deciding happens, and "
             "deciding is slower than moving.</p>" % (total_zones, sh))
    b.append("<ul>"
             "<li>" + zlink("home-office-the-file-storage", "The File Storage")
             + " is 60-90 min and nearly all of it is Sort, because it is "
             "hundreds of small keep-or-shred calls in a row.</li>"
             "<li>" + zlink("primary-bathroom-the-medicine-cabinet",
                            "The Medicine Cabinet")
             + " is 45-75 min, spent reading labels and dates one box at a "
             "time.</li>"
             "<li>" + zlink("kids-bedroom-the-toy-storage-zone",
                            "The Toy Storage Zone")
             + " is 60-90 min, most of it after every bin has been tipped out "
             "onto the floor.</li>"
             "<li>" + zlink("pantry-the-dry-goods-shelves",
                            "The Dry Goods Shelves")
             + " is 45-75 min, opening bags and reading dates.</li>"
             "</ul>")
    b.append("<p>This is the practical argument against the container aisle. "
             "Buying storage before you sort does not shorten any of these "
             "sessions, because the slow part was never the arranging. It "
             "lengthens them, because now you are also fitting the things you "
             "were about to remove into something you paid for.</p>")
    b.append("<p>A handful of zones break the pattern, and they are the ones "
             "worth knowing about before you start. The "
             "%s is mostly Shine, because degreasing a hood and grates is slow "
             "work whatever else you do. The "
             "%s is mostly Safety, walked tread by tread. The "
             "%s is mostly Straighten, fitting bins around the pipework.</p>"
             % (zlink("kitchen-the-cooking-zone", "cooking zone"),
                zlink("stair-landing-the-stair-and-floor-path",
                      "stair and floor path"),
                zlink("primary-bathroom-the-under-sink-cabinet",
                      "under-sink cabinet")))

    b.append("<h2>How long does the whole house take?</h2>")
    b.append("<p>We do not publish that number, and the omission is "
             "deliberate.</p>")
    b.append("<p>Three reasons. No house has all 20 rooms, so any total would "
             "describe a home nobody lives in. The rooms that vary most between "
             "households are the ones that dominate the total, and a garage "
             "with two cars in it is not the same job as a garage with a decade "
             "of boxes in it. And a single large number is the exact thing that "
             "stops people starting, which makes it worse than useless even "
             "when it is accurate.</p>")
    b.append("<p>If you want a house-level figure, add the rows in the table "
             "for the rooms you actually have. The arithmetic is yours to do "
             "and it will be more honest than ours. What we would rather you "
             "take away is the number you can act on this evening: one zone, 15 "
             "to 90 minutes, finished.</p>")

    b.append("<h2>What the times do not include</h2>")
    b.append("<ul>"
             "<li><b>Shopping.</b> The method tells you what a zone needs after "
             "you have sorted it, not before. If you need a container, that is "
             "a separate trip on a separate day.</li>"
             "<li><b>Repairs.</b> Shine flags the leak, the frayed cord, the "
             "loose bracket. Fixing them is its own job and often somebody "
             "else's.</li>"
             "<li><b>Waiting.</b> Some zones start a wash or a descaling cycle "
             "and then carry on around it. The linen shelf in a bathroom needs "
             "the machine running before you touch anything else.</li>"
             "<li><b>The conversation.</b> Shared zones need agreement before "
             "they need sorting, and at least one zone in most homes is not "
             "yours to decide about. Budget for talking, not just "
             "working.</li>"
             "</ul>")

    b.append(SAFETY)
    b.append("<h2>Pick a room and see the sessions</h2>")
    b.append("<ul>"
             '<li><a href="%sentryway.html">Entryway</a>, %d zones, %s, and the '
             "room to start with</li>"
             '<li><a href="%skitchen.html">Kitchen</a>, %d zones, %s</li>'
             '<li><a href="%sprimary-bathroom.html">Primary bathroom</a>, %d '
             "zones, %s</li>"
             '<li><a href="%sgarage.html">Garage</a>, %d zones, %s, the longest '
             "room in the model</li>"
             '<li><a href="../resources.html">All 20 rooms and %d micro '
             "zones</a></li>"
             '<li><a href="what-is-6s.html">What is 6S</a>, if you want the '
             "method before the schedule</li>"
             '<li><a href="where-to-start-decluttering.html">Where to start '
             'if the whole room feels like too much</a>, once you know the '
             'time it takes</li>'
             "</ul>"
             % (R, by_room["Entryway"]["zones"],
                span(by_room["Entryway"]["lo"], by_room["Entryway"]["hi"]),
                R, by_room["Kitchen"]["zones"],
                span(by_room["Kitchen"]["lo"], by_room["Kitchen"]["hi"]),
                R, by_room["Primary Bathroom"]["zones"],
                span(by_room["Primary Bathroom"]["lo"],
                     by_room["Primary Bathroom"]["hi"]),
                R, by_room["Garage"]["zones"],
                span(by_room["Garage"]["lo"], by_room["Garage"]["hi"]),
                total_zones))
    b.append(offer("the session times above are what it takes to work a zone "
                   "on your own."))

    ld = graph(BASE + "/articles/" + A2_FILE[:-5], A2_TITLE, A2_DESC,
               [("Home", "/"), ("Rooms and micro zones", "/resources.html"),
                ("How long a room takes", "/articles/" + A2_FILE[:-5])], faq)
    return write(A2_FILE, A2_TITLE, A2_DESC, ld, "\n".join(b))


def main():
    rooms = json.load(io.open(SRC, encoding="utf-8"))["rooms"]
    for path, doc in (article_one(), article_two(rooms)):
        bad = [c for c in "–—" if c in doc]
        assert not bad, "dash found in " + path
        assert "Set in Order" not in doc, "banned step name in " + path
        text = re.sub(r"<[^>]+>", " ", doc.split("<main")[1].split("</main>")[0])
        print("%s  %d words" % (path, len(text.split())))

    # This generator's own <head>/<body> template carries no PWA icon links
    # and no measurement script; both were wired onto the two live article
    # pages by wire_pwa.py/wire_measure.py directly, same as every other page
    # on the site, so a plain rerun of this file alone silently deleted both
    # (issue #26). Re-running the whole-site, idempotent wiring scripts here
    # closes that gap the same way ops/build_zone_pages.py already does.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import prune_catalog_js
    import wire_landmarks
    import wire_progressive
    import wire_measure
    import wire_pwa
    # Same trap as the measurement block: this generator's
    # own <head> template has no progressive marker, so a
    # rewrite would strip it and put back the failure where
    # a blocked script leaves sections invisible.
    # Same trap as the measurement and progressive blocks:
    # this generator's own template has no skip link and
    # some of its pages have no main landmark, so a rewrite
    # would strip both and put a keyboard visitor back in
    # front of twenty seven links with no way past them.
    # Last of the page passes: this generator's template
    # includes the catalogue script on every page it writes,
    # so without this a rebuild puts 73 KB back onto 173
    # pages that never read a byte of it.
    prune_catalog_js.main()
    wire_landmarks.main()
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()


if __name__ == "__main__":
    main()
