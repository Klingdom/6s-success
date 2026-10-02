#!/usr/bin/env python3
"""The page for the "I don't want to buy anything" half of this product.

WHY THIS EXISTS
----------------
ops/keyword_demand.py's 2026-10-02 re-harvest (ops/keyword-demand.json) holds
a cheap/budget/DIY query cluster, 108 queries, checked against every title
and heading on the site. Most of it is already partial coverage from the
room and zone pages. Five queries are a genuine, on-mission gap, nothing of
ours titled or headed for them:

    declutter worksheets free
    diy baking sheet organizer
    diy cubbies for mudroom
    kitchen organization ideas for small spaces diy
    kitchen organization ideas for small spaces on a budget

The rest of the cluster's gaps (attic, basement, bonus room, backyard BBQ
station, outdoor walkways, an "outdoor diy lab") name rooms this site does
not have a diagnosis for. Writing for them would mean inventing content for
a room with no corpus behind it, which is exactly the fabrication CLAUDE.md
section 8 forbids. They are left alone on purpose, not missed.

ONE PAGE, NOT FIVE
------------------
Same reasoning as ops/build_messy_article.py (CLAUDE.md section 11): the five
gap queries are one belief wearing different clothes, "organizing costs
money", and the honest answer to all five is the same, grounded in two real
root causes (insufficient capacity really does need more capacity; excess
does not). The two zone-specific DIY questions get a real section each,
grounded in that zone's own diagnosed friction, not invented for the
occasion.

WHY IT IS GENERATED AND NOT TYPED
----------------------------------
The root-cause names, meanings and thirty-second tests come from
ops/root_causes.py, the single shared vocabulary. The zone quotes
(done_looks_like) come from content/manual/source/content.json, read fresh
on every run rather than retyped, so this page cannot become a nineteenth
copy of either to drift (LRN-0023).

Run:  python ops/build_budget_diy_article.py
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
CONTENT_JSON = os.path.join(ROOT, "content", "manual", "source", "content.json")
OUT = os.path.join(SITE, "articles", "organizing-on-a-budget.html")
TEMPLATE = os.path.join(SITE, "articles", "why-is-my-house-always-messy.html")
BASE = "https://6s-success.com"
SLUG = "organizing-on-a-budget"
PUBLISHED = "2026-10-02"

TITLE = "How to organize on a budget, with what you already own"
DESC = ("Most of what is wrong is not a shopping problem. The two tests to "
        "run before you buy, plus DIY fixes for a baking sheet drawer, a "
        "mudroom rack, a small kitchen.")

ZONE_QUOTES = {
    # (room, zone name as it appears in content.json, zone page slug)
    "kitchen": ("Kitchen", "Lower Cabinet and Cookware Zone",
                "kitchen-the-lower-cabinets-and-cookware"),
    "mudroom": ("Mudroom", "Shoe and Boot Storage",
                "mudroom-the-shoe-and-boot-storage"),
}


def load_zone(room, zone_name):
    data = json.load(io.open(CONTENT_JSON, encoding="utf-8"))
    for r in data["rooms"]:
        if r["room"] != room:
            continue
        for z in r["zones"]:
            name = z.get("name") or z.get("zone")
            if name == zone_name:
                return z
    raise SystemExit("content.json no longer has %s / %s" % (room, zone_name))


# FAQ ANSWERS ARE ALSO VISIBLE PROSE ON THIS PAGE. Worded as the harvested
# phrases themselves (ops/keyword-demand.json), not a paraphrase of them,
# the same lesson build_messy_article.py ported from a concurrent session.
FAQ = [
    ("How do I organize on a budget?",
     "Run the two tests below before buying anything. Most zones that feel "
     "like a shopping problem are actually an excess problem (too much kept, "
     "fixed free by removing some of it) or a missing-home problem (fixed "
     "free by deciding where one thing lives). Only a zone that fails the "
     "capacity test genuinely needs more storage, and even then it rarely "
     "needs to be bought new."),
    ("Are there free declutter worksheets?",
     "We do not sell a fill-in-the-blank worksheet, and the honest answer "
     "is that most households do not need one. The free Micro Zone Map does "
     "the same job: twenty printable sheets, one per room, naming every "
     "micro zone and how long one session takes, so you know where to start "
     "without filling in a form first. The free Quest tool does the same "
     "job on a screen instead of paper."),
    ("How do I make a DIY baking sheet organizer?",
     "Stand the sheets on their long edge instead of stacking them flat, "
     "held upright by anything with slots: a dish-drying rack turned on its "
     "side, a magazine file, or a cut-down cereal box, all things most "
     "kitchens already own. The goal is a divider, not a purchase; a "
     "shop-bought one is the same idea in metal."),
    ("How do I make DIY cubbies for a mudroom?",
     "A cubby is just one assigned slot per person, and a slot does not "
     "have to be bought as a cubby to work as one. A repurposed crate, a "
     "wine box on its side, or even taped-off sections of an existing shelf, "
     "one per person and labeled, does the same job as a flat-pack cubby "
     "unit for nothing."),
    ("How do I organize a small kitchen on a budget?",
     "Separate the two questions first. If the honest test below says the "
     "kitchen has insufficient capacity, no amount of free rearranging fixes "
     "that, and a small, cheap addition (a divider, a riser, a rail) is the "
     "right move. If it passes that test, the kitchen was never too small, "
     "it was holding more than its job needs, and the fix costs nothing."),
    ("Do I need to buy bins and boxes to get organized?",
     "Usually not first. CLAUDE.md's own product principle here is to "
     "diagnose before prescribing: decide what is actually wrong with the "
     "assigned-home test and the capacity test, then buy only for what is "
     "left over once removing excess and reusing what you own are both "
     "done."),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def chrome():
    """(head_without_json_ld, header, footer) lifted from a sibling article.

    Same approach and same three found-by-diffing bugs as
    ops/build_messy_article.py's own chrome(): strip every json-ld block
    (not just the first), strip the breadcrumb marker comment (wire_
    breadcrumbs.py's to fill, not this generator's), and keep everything
    else so the PWA/progressive/measure wiring sweeps already applied to the
    template survive onto this page.
    """
    s = io.open(TEMPLATE, encoding="utf-8").read()
    head = s[:s.index("</head>")]
    head = re.sub(r'(?is)<script type="application/ld\+json">.*?</script>\s*', "", head)
    head = re.sub(r'(?is)<!-- CRUMBLD:BEGIN -->.*?<!-- CRUMBLD:END -->\s*', "", head)
    header = s[s.index("</head>") + len("</head>"):s.index("<main")]
    footer = s[s.index("</main>") + len("</main>"):]
    return head, header, footer


def retitle(head):
    """The sibling's head with every one of its own strings replaced.

    Explicit substitution with a count check, same reasoning as
    build_messy_article.py's retitle(): a head that silently kept the
    template's own title/description/canonical would publish this page as a
    duplicate of another one, which looks fine on screen and is invisible
    until a search engine picks one of them.
    """
    old_title = "Why is my house always messy?"
    old_desc = ("Because it is almost never the whole house. It is four or "
                "five small zones failing for different reasons. How to "
                "find yours, and what each one needs.")
    old_slug = "why-is-my-house-always-messy"
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
    """A linked article's own <title>, read from the shipped page.

    So the link text describes where it goes, and so a cause pointing at a
    retired or renamed article breaks the build instead of shipping a dead
    link quietly.
    """
    path = os.path.join(SITE, "articles", slug + ".html")
    if not os.path.exists(path):
        raise SystemExit("root_causes.py points %r at an article that does "
                         "not exist: %s" % (slug, path))
    s = io.open(path, encoding="utf-8").read()
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m:
        raise SystemExit("no <title> in %s" % path)
    return re.sub(r"[ \n\t]+", " ", m.group(1)).split("|")[0].strip()


def test_block(cid):
    c = BY_ID[cid]
    return ('<h3>%s</h3>\n<p>%s</p>\n'
            '<p class="notice" style="max-width:60ch"><b>The thirty-second '
            'test.</b> %s</p>\n'
            '<p><a href="%s">%s</a></p>'
            % (esc(c["name"].title()), esc(c["meaning"]),
               esc(c["confirm_30s"]), esc(c["article"]),
               esc(article_title(c["article"]))))


def kitchen_section():
    z = load_zone(*ZONE_QUOTES["kitchen"][:2])
    done = z["done_looks_like"]
    slug = ZONE_QUOTES["kitchen"][2]
    return (
        '<h2 id="baking-sheet-organizer">A DIY baking sheet organizer, '
        'from what the kitchen already has</h2>\n'
        '<p>The real friction is rarely the baking sheet. It is that a flat '
        'sheet stacked under three pans has to come all the way out before '
        'anything under it moves, which is the excess-motion cause, not a '
        'missing product.</p>\n'
        '<p>What a finished version of this zone actually looks like, '
        'quoted from the diagnosis for the real zone this question is '
        'about: &ldquo;%s&rdquo;</p>\n'
        '<p>The part that matters is &ldquo;standing on end&rdquo;, not '
        '&ldquo;bought new&rdquo;. Anything that holds sheets upright and '
        'separate does the job: a dish-drying rack turned on its side, a '
        'magazine file, or a cut-down cereal box wide enough for the '
        'largest sheet. None of those are a baking sheet organizer sold as '
        'one; all of them work as one.</p>\n'
        '<p><a href="../zones/%s">See the full diagnosis for this zone</a>, '
        'including the two other frictions that usually sit next to this '
        'one.</p>'
        % (esc(done), slug))


def mudroom_section():
    z = load_zone(*ZONE_QUOTES["mudroom"][:2])
    purpose = z["purpose"]
    slug = ZONE_QUOTES["mudroom"][2]
    return (
        '<h2 id="diy-cubbies-mudroom">DIY cubbies for a mudroom, without '
        'buying cubbies</h2>\n'
        '<p>What this zone is actually for: &ldquo;%s&rdquo; A cubby is one '
        'name for one idea, an assigned slot per person, and the slot is '
        'doing the work, not the word.</p>\n'
        '<p>A repurposed crate, a wine box on its side, or taped-off '
        'sections of a shelf you already have, one per person and labeled '
        'with who it belongs to, answers the same no-assigned-home cause a '
        'bought cubby unit answers. The honest reason this one is worth '
        'doing even on a budget: the diagnosis for this zone found that a '
        'rack built for two pairs per person runs out of room the moment '
        'one person owns three, which a cheap, flexible crate fixes more '
        'easily than a fixed cubby grid does.</p>\n'
        '<p><a href="../zones/%s">See the full diagnosis for this zone</a>.</p>'
        % (esc(purpose), slug))


def small_kitchen_section():
    return (
        '<h2 id="small-kitchen-budget">A small kitchen, organized on a '
        'budget</h2>\n'
        '<p>Separate the two questions before spending anything. '
        '<a href="zone-too-small-for-what-it-holds">The honest capacity '
        'test</a> tells you which one you actually have: put back only what '
        'the zone\'s job needs, and if it still will not close, the '
        'kitchen genuinely does not have enough room and a small, cheap '
        'addition, a riser, a divider, a rail, is the right next step. If '
        'it closes easily, the kitchen was never too small. It was holding '
        'more than its job needs, and that fix is free: remove what the '
        'honest count does not justify, then stop.</p>\n'
        '<p><a href="../rooms/kitchen">See the kitchen broken into its '
        'seven micro zones</a> for the room-level view this applies to.</p>')


def worksheet_section():
    return (
        '<h2 id="free-tools">The free tools that do a worksheet\'s job</h2>\n'
        '<p>We do not sell a declutter worksheet, and most households do '
        'not need one. Two things already do what a worksheet is for, '
        'telling you where to start and what counts as finished, and both '
        'are free with nothing to sign up for:</p>\n'
        '<ul style="max-width:62ch">\n'
        '<li><a href="../downloads/6S-Micro-Zone-Map.html">The Micro Zone '
        'Map</a>, twenty printable sheets, one per room, naming every '
        'micro zone in the house and how long one session takes.</li>\n'
        '<li><a href="../quest.html">The Quest tool</a>, the same idea on '
        'a screen: it asks what is annoying you, works out the likely '
        'zone and cause, and gives you one job with a clear finish line.'
        '</li>\n'
        '</ul>')


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
         "datePublished": PUBLISHED, "dateModified": PUBLISHED,
         "isAccessibleForFree": True,
         "publisher": {"@type": "Organization", "name": "6S Success",
                       "url": BASE + "/"},
         "about": [{"@type": "Thing", "name": BY_ID[c]["name"].title()}
                   for c in ("KC-001", "KC-007")]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Home",
              "item": BASE + "/"},
             {"@type": "ListItem", "position": 2, "name": "Articles",
              "item": BASE + "/articles/"},
             {"@type": "ListItem", "position": 3, "name": TITLE,
              "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "@id": url + "#faq",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in FAQ]},
    ], indent=1)


BODY = """<nav class="crumb" style="font-family:var(--sans);font-size:13px;color:var(--soft);margin:26px 0 0"><a href="../index.html">Home</a> / <a href="../articles/">Articles</a> / How to organize on a budget</nav>
<div class="head" style="margin-top:10px">
<p class="eyebrow">Before you buy anything</p>
<h1>How to organize on a budget</h1>
<p class="lede">Most of what is wrong in a zone is not a shopping problem. Two tests tell you which of the few zones actually need more storage, and which only need less in them.</p></div>

<p class="notice" style="max-width:60ch"><b>The short answer.</b> Run the excess test and the capacity test below before buying anything. Most zones fail the first one, which costs nothing to fix. A real minority fail the second, and for those a small, cheap addition is the honest next step, not a bought-new one.</p>

<h2>The two tests, before you spend anything</h2>
<p>Everything below assumes one of these two is true, because almost every zone that reads as a budget problem is actually one of them wearing a price tag.</p>

__TESTS__

__KITCHEN__

__MUDROOM__

__SMALLKITCHEN__

__WORKSHEET__

<h2>Common questions</h2>
__FAQ__

<section class="band" style="margin:44px 0 0;padding:26px 28px;border-radius:22px"><p class="eyebrow on-deep">If one zone genuinely needs more capacity</p><h2 style="margin:0 0 10px">Get the standard written down, for nineteen dollars</h2><p style="margin:0 0 16px;max-width:62ch">The Whole House Print Pack carries the honest-count check and the finished standard for all 114 micro zones onto cards you print at home. Most of what is in it costs you time, not money. If a zone keeps fighting back after the free tools and the Print Pack, a <a href="../consulting.html" style="color:#DDA63A">one hour virtual consult</a> is 250 dollars.</p><p style="margin:0"><a data-sku="PACK-HOUSE" class="btn btn-primary" href="https://buy.stripe.com/00wdR223kfwK9fQ9440kF28" rel="nofollow noopener">The Print Pack, 19 dollars</a><a class="btn btn-on-deep" style="margin-left:10px" href="../resources.html">Or work a zone, free</a><a class="btn btn-on-deep btn-sm" style="margin-left:10px" data-sku="CN-VIRTUAL" href="../consulting.html?from=article:organizing-on-a-budget">Talk it through, 250 dollars</a></p></section>

<h2>Keep reading</h2>
<ul style="max-width:62ch">
<li><a href="more-storage-wont-fix-clutter">More storage will not fix a messy room</a>, the longer version of the excess test above.</li>
<li><a href="zone-too-small-for-what-it-holds">The zone that is too small for what it holds</a>, the longer version of the capacity test above.</li>
<li><a href="why-is-my-house-always-messy">Why is my house always messy?</a>, if the budget question is really a different one.</li>
<li><a href="../resources.html">All twenty rooms, broken into their micro zones</a>.</li>
</ul>
"""


def build():
    head, header, footer = chrome()
    head = retitle(head)
    body = (BODY
            .replace("__TESTS__", test_block("KC-001") + "\n\n" + test_block("KC-007"))
            .replace("__KITCHEN__", kitchen_section())
            .replace("__MUDROOM__", mudroom_section())
            .replace("__SMALLKITCHEN__", small_kitchen_section())
            .replace("__WORKSHEET__", worksheet_section())
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
    print("  %d FAQ entries" % len(FAQ))
    print("Now run: python ops/build_seo.py && python ops/fingerprint_assets.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
