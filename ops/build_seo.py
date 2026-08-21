#!/usr/bin/env python3
"""
Build the SEO layer for site/: canonical tags, Open Graph, Twitter cards,
JSON-LD, robots.txt and sitemap.xml, plus the two information-architecture
edits that put the room content into the site's navigation.

Design notes
------------
* Idempotent. Every injected block sits between SEO:BEGIN / SEO:END markers and
  is replaced wholesale on each run, so this is safe to run repeatedly and safe
  to run after another agent has edited the same page.
* Zero third-party requests. Nothing here adds a script, a font, a pixel or a
  CDN reference. og:image points at an image we already self-host.
* Nothing is asserted that the visible page does not support. See DECLINED at
  the bottom of this file for the schema types deliberately left out and why.

Canonical URL policy
--------------------
nginx serves both /resources and /resources.html (try_files $uri $uri.html),
because the printed book prints the extensionless form. That means every page
is reachable at two URLs. Canonical points at the .html form, which is what
every internal link and the on-disk file both use, so the site stays correct
under any static host and the extensionless variant consolidates into it.
The home page canonicals to the bare origin.
"""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"
IMG = BASE + "/assets/img/"

BEGIN, END = "<!-- SEO:BEGIN -->", "<!-- SEO:END -->"

ORG_ID = BASE + "/#organization"
SITE_ID = BASE + "/#website"

ORGANIZATION = {
    "@type": "Organization",
    "@id": ORG_ID,
    "name": "6S Success",
    "url": BASE + "/",
    "description": "6S Success applies the Lean six-S method, Sort, Straighten, "
                   "Shine, Safety, Standardize and Sustain, to organizing and "
                   "cleaning a home, room by room and micro zone by micro zone.",
    "email": "support@6s-success.com",
    "parentOrganization": {"@type": "Organization", "name": "Nova Consulting"},
    "knowsAbout": [
        "Lean 6S", "Home organization", "Cleaning method",
        "Micro zones", "Visual standards", "Household routines",
    ],
}

WEBSITE = {
    "@type": "WebSite",
    "@id": SITE_ID,
    "url": BASE + "/",
    "name": "6S Success",
    "inLanguage": "en",
    "publisher": {"@id": ORG_ID},
}

ROOMS = [
    ("Entryway", "entryway", 31), ("Kitchen", "kitchen", 32),
    ("Pantry", "pantry", 33), ("Dining Room", "dining-room", 34),
    ("Living Room", "living-room", 35), ("Family Room", "family-room", 36),
    ("Primary Bedroom", "primary-bedroom", 37), ("Guest Bedroom", "guest-bedroom", 38),
    ("Kids Bedroom", "kids-bedroom", 39), ("Nursery", "nursery", 40),
    ("Primary Bathroom", "primary-bathroom", 41), ("Guest Bathroom", "guest-bathroom", 42),
    ("Laundry Room", "laundry-room", 43), ("Home Office", "home-office", 44),
    ("Garage", "garage", 45), ("Workshop", "workshop", 46),
    ("Mudroom", "mudroom", 47), ("Hall Closet", "hall-closet", 48),
    ("Stair Landing", "stair-landing", 49), ("Patio or Deck", "patio-or-deck", 50),
]


def crumbs(*pairs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": BASE + u}
            for i, (n, u) in enumerate(pairs, 1)
        ],
    }


BOOK = {
    "@type": "Book",
    "@id": BASE + "/book.html#book",
    "name": "6S Success: Home Edition",
    "url": BASE + "/book.html",
    "inLanguage": "en",
    "numberOfPages": None,          # not stated on the page; omitted below
    "bookFormat": "https://schema.org/Hardcover",
    "publisher": {"@id": ORG_ID},
    "genre": "Home organization",
    "abstract": "Fifty chapters across nine parts covering the six-S method for "
                "the home, followed by twenty room-by-room playbooks that break "
                "each room into its micro zones.",
    "about": [
        {"@type": "Thing", "name": "Lean 6S"},
        {"@type": "Thing", "name": "Home organization"},
        {"@type": "Thing", "name": "Household cleaning"},
    ],
}
BOOK = {k: v for k, v in BOOK.items() if v is not None}

ROOM_LIST = {
    "@type": "ItemList",
    "@id": BASE + "/resources.html#rooms",
    "name": "The twenty rooms of the 6S Success micro zone model",
    "description": "Every room in the home, each broken into the micro zones "
                   "that are worked in order.",
    "numberOfItems": len(ROOMS),
    "itemListOrder": "https://schema.org/ItemListOrderAscending",
    "itemListElement": [
        {"@type": "ListItem", "position": i, "name": name,
         "url": BASE + "/resources.html#" + slug}
        for i, (name, slug, _ch) in enumerate(ROOMS, 1)
    ],
}

CONSULTING_SERVICE = {
    "@type": "Service",
    "@id": BASE + "/consulting.html#service",
    "name": "6S home and workplace reset consulting",
    "serviceType": "Home organizing and Lean 6S consulting",
    "provider": {"@id": ORG_ID},
    "description": "A virtual home consult, an in-home reset day, or a Lean 6S "
                   "engagement for a team, delivered by Nova Consulting.",
    "url": BASE + "/consulting.html",
}

# ---------------------------------------------------------------- page table
# title, description, canonical path, og image, og type, robots, jsonld nodes
PAGES = {
    "index.html": dict(
        path="/",
        title="6S Success: the six-S method for organizing and cleaning a home",
        desc="Sort, Straighten, Shine, Safety, Standardize, Sustain: the Lean "
             "six-S method rebuilt for the home. Twenty rooms, 114 micro zones, "
             "and a fifty-chapter book.",
        image="renewed.jpg",
        image_alt="A bright, renewed room after a six-S reset",
        type="website",
        jsonld=[ORGANIZATION, WEBSITE],
    ),
    "method.html": dict(
        path="/method.html",
        title="The six S's: Sort, Straighten, Shine, Safety, Standardize, Sustain",
        desc="What each of the six S's actually asks of you, in the order that "
             "works, plus every way to learn the method: the book, courses, "
             "workshops, and the app.",
        image="room-map.jpg",
        image_alt="A room map showing where each thing belongs",
        type="article",
        jsonld=[crumbs(("Home", "/"), ("The method", "/method.html"))],
    ),
    "resources.html": dict(
        path="/resources.html",
        title="Rooms and micro zones: 20 rooms, 114 micro zones | 6S Success",
        desc="Every room broken into its micro zones, in the order to work them, "
             "with the product types each one needs. Twenty rooms, 114 micro "
             "zones. Free companion to the book.",
        image="room-map.jpg",
        image_alt="A room map showing where each thing belongs",
        type="article",
        jsonld=[crumbs(("Home", "/"), ("Rooms and micro zones", "/resources.html")),
                ROOM_LIST],
    ),
    "book.html": dict(
        path="/book.html",
        title="6S Success: Home Edition, the book: 50 chapters, 20 room playbooks",
        desc="Fifty chapters across nine parts, from your first room to twenty "
             "room-by-room playbooks. Chapters 1 to 30 are free to read online "
             "or download as a PDF.",
        image="renewed.jpg",
        image_alt="A bright, renewed room after a six-S reset",
        type="book",
        jsonld=[crumbs(("Home", "/"), ("The book", "/book.html")), BOOK],
    ),
    "shop.html": dict(
        path="/shop.html",
        title="Shop: books, courses, reset kits, tools, and the app | 6S Success",
        desc="Books and guides, courses, reset kits, the app, consulting, and the "
             "tools the method calls for, each mapped to the S it serves. "
             "Ordering is not live yet.",
        image="reset.jpg",
        image_alt="A reset in progress, sorted piles and labelled containers",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Shop", "/shop.html"))],
    ),
    "consulting.html": dict(
        path="/consulting.html",
        title="Consulting: have us run the six-S reset with you | 6S Success",
        desc="A virtual home consult, an in-home reset day, or a Lean 6S "
             "engagement for a team, delivered by Nova Consulting, the parent "
             "behind the method. Request a quote.",
        image="reset-together.jpg",
        image_alt="A consultant and a homeowner resetting a room side by side",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Consulting", "/consulting.html")),
                CONSULTING_SERVICE],
    ),
    "about.html": dict(
        path="/about.html",
        title="About 6S Success: a factory discipline, rebuilt for real homes",
        desc="6S Success brings the Lean six-S method home: Sort, Straighten, "
             "Shine, Safety, Standardize, Sustain. Change the method, not your "
             "character. A Nova Consulting brand.",
        image="family.jpg",
        image_alt="A family in a calm, ordered home",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("About", "/about.html")),
                {"@type": "AboutPage", "url": BASE + "/about.html",
                 "name": "About 6S Success", "mainEntity": {"@id": ORG_ID}}],
    ),
    "contact.html": dict(
        path="/contact.html",
        title="Contact 6S Success: books, quotes, workshops, and press",
        desc="Tell us the room or the routine that keeps fighting you. Reach 6S "
             "Success about the book, a consulting quote, a workshop seat, or a "
             "press enquiry.",
        image="calm-living.jpg",
        image_alt="A calm, ordered living room in warm daylight",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Contact", "/contact.html")),
                {"@type": "ContactPage", "url": BASE + "/contact.html",
                 "name": "Contact 6S Success", "mainEntity": {"@id": ORG_ID}}],
    ),
    "privacy.html": dict(
        path="/privacy.html",
        title="Privacy: no analytics, no trackers, no cookies | 6S Success",
        desc="What 6S Success does with your information: no analytics, no "
             "trackers, no cookies, no third-party requests, and a cart that "
             "never leaves your browser.",
        image="calm-living.jpg", image_alt="A calm, ordered living room",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Privacy", "/privacy.html"))],
    ),
    "terms.html": dict(
        path="/terms.html",
        title="Terms of use: what this site is and why ordering is not live | 6S Success",
        desc="Terms of use for 6s-success.com: what the site is, why ordering is "
             "not yet live, how the content may be used, and the limits of "
             "liability.",
        image="calm-living.jpg", image_alt="A calm, ordered living room",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Terms", "/terms.html"))],
    ),
    "accessibility.html": dict(
        path="/accessibility.html",
        title="Accessibility: what the site does today and the known gaps | 6S Success",
        desc="Our accessibility commitment for 6s-success.com, what the site does "
             "today, and an honest list of the gaps we have not closed yet.",
        image="calm-living.jpg", image_alt="A calm, ordered living room",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Accessibility", "/accessibility.html"))],
    ),
    "disclaimer.html": dict(
        path="/disclaimer.html",
        title="Safety notice: read this before any cleaning or organizing step | 6S Success",
        desc="Important safety information before following any 6S Success "
             "cleaning or organizing instruction: chemicals, tools, height, "
             "children, pets, and emergencies.",
        image="calm-living.jpg", image_alt="A calm, ordered living room",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Safety notice", "/disclaimer.html"))],
    ),

    # ------------------------------------------------------------ not indexed
    # A cart is a per-visitor utility view with no standalone value, and it
    # cannot be entered usefully from a search result. Crawlable, not indexed.
    "cart.html": dict(
        path="/cart.html",
        title="Your cart | 6S Success",
        desc="Review the items you have picked. Checkout is not live yet, so the "
             "cart sends a request for an invoice or a booking link.",
        image="reset.jpg", image_alt="A reset in progress",
        type="website", robots="noindex, follow", jsonld=[],
    ),
    # An investor deck. Its prices and market figures are explicitly labelled
    # illustrative planning targets, so surfacing it to shoppers in search would
    # advertise numbers the business cannot honour. Direct link only.
    "invest.html": dict(
        path="/invest.html",
        title="Venture plan | 6S Success Micro Zone",
        desc="The 6S Success Micro Zone venture plan. Figures are illustrative "
             "planning targets for discussion, not an offer to sell securities.",
        image="room-map.jpg", image_alt="A room map",
        type="website", robots="noindex, follow", jsonld=[],
    ),
}

INDEXABLE = [f for f, p in PAGES.items() if not p.get("robots")]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def seo_block(fn, p):
    url = BASE + p["path"]
    L = [BEGIN,
         '<link rel="canonical" href="%s">' % url]
    if p.get("robots"):
        L.append('<meta name="robots" content="%s">' % p["robots"])
    else:
        L.append('<meta name="robots" content="index, follow, max-image-preview:large">')
    L += [
        '<meta property="og:type" content="%s">' % p["type"],
        '<meta property="og:site_name" content="6S Success">',
        '<meta property="og:locale" content="en_US">',
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:title" content="%s">' % esc(p["title"]),
        '<meta property="og:description" content="%s">' % esc(p["desc"]),
        '<meta property="og:image" content="%s%s">' % (IMG, p["image"]),
        '<meta property="og:image:alt" content="%s">' % esc(p["image_alt"]),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % esc(p["title"]),
        '<meta name="twitter:description" content="%s">' % esc(p["desc"]),
        '<meta name="twitter:image" content="%s%s">' % (IMG, p["image"]),
        '<meta name="twitter:image:alt" content="%s">' % esc(p["image_alt"]),
        '<meta name="theme-color" content="#22323C">',
    ]
    for node in p["jsonld"]:
        doc = dict(node)
        doc["@context"] = "https://schema.org"
        doc = {"@context": "https://schema.org", **node}
        L.append('<script type="application/ld+json">\n%s\n</script>'
                 % json.dumps(doc, indent=2, ensure_ascii=False))
    L.append(END)
    return "\n".join(L)


def apply_head(s, fn, p):
    """title, description, and the marker-delimited SEO block."""
    s = re.sub(r"<title>.*?</title>",
               lambda m: "<title>%s</title>" % esc(p["title"]), s, count=1, flags=re.S)

    desc_tag = '<meta name="description" content="%s">' % esc(p["desc"])
    if re.search(r'<meta\s+name="description"[^>]*>', s):
        s = re.sub(r'<meta\s+name="description"[^>]*>',
                   lambda m: desc_tag, s, count=1)
    else:
        s = s.replace("</title>", "</title>\n" + desc_tag, 1)

    block = seo_block(fn, p)
    if BEGIN in s:
        s = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                   lambda m: block, s, count=1, flags=re.S)
    else:
        s = s.replace(desc_tag, desc_tag + "\n" + block, 1)
    return s


NAV_RE = re.compile(r'<nav class="nav"[^>]*>.*?</nav>', re.S)
FOOT_LEARN_RE = re.compile(
    r'<h4>Learn</h4><a href="method\.html">The Method</a><a href="book\.html">The Book</a>')


def apply_ia(s, fn):
    """Put the room content into the navigation, not just the legal strip.

    The primary nav and the footer Learn column contain the byte-identical
    string <a href="book.html">The Book</a>, so every edit here is scoped to
    one region or anchored on a heading. A plain str.replace hits the nav.
    """
    n = 0

    # 0. repair: strip any footer-style link that landed inside the primary nav
    s = NAV_RE.sub(
        lambda m: m.group(0).replace(
            '<a href="resources.html">Rooms and micro zones</a>', ''), s)

    # 0b. repair: collapse duplicate Rooms links (an aria-current variant on the
    #     Rooms page itself once slipped past a literal-string guard)
    def dedupe(m):
        blk, seen = m.group(0), 0
        def one(a):
            nonlocal seen
            seen += 1
            return a.group(0) if seen == 1 else ""
        return re.sub(r'\s*<a href="resources\.html"[^>]*>Rooms</a>', one, blk)
    s = NAV_RE.sub(dedupe, s)

    # 1. primary nav: Rooms, straight after The Method
    nav = NAV_RE.search(s)
    if nav and not re.search(r'href="resources\.html"[^>]*>Rooms</a>', nav.group(0)):
        cur = ' aria-current="page"' if fn == "resources.html" else ""
        new = re.sub(r'(<a href="method\.html"[^>]*>The Method</a>)',
                     r'\1\n      <a href="resources.html"%s>Rooms</a>' % cur,
                     nav.group(0), count=1)
        if new != nav.group(0):
            s = s[:nav.start()] + new + s[nav.end():]
            n += 1

    # 2. footer Learn column: the rooms belong with the things you learn from
    if FOOT_LEARN_RE.search(s) and 'href="resources.html">Rooms and micro zones</a>' not in s:
        s = FOOT_LEARN_RE.sub(
            lambda m: m.group(0) + '<a href="resources.html">Rooms and micro zones</a>',
            s, count=1)
        n += 1

    # 3. the bottom strip is for legal pages; Resources was buried there
    s = s.replace('<a href="resources.html">Resources</a> &middot; ', '', 1)
    return s, n


def build_pages():
    changed = []
    for fn, p in PAGES.items():
        fp = os.path.join(SITE, fn)
        if not os.path.exists(fp):
            print("  MISSING %s" % fn)
            continue
        src = open(fp, encoding="utf-8").read()
        out = apply_head(src, fn, p)
        out, _ = apply_ia(out, fn)
        if out != src:
            open(fp, "w", encoding="utf-8").write(out)
            changed.append(fn)
    return changed


def build_robots():
    txt = (
        "# 6s-success.com\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# Utility and direct-link-only pages carry a noindex meta tag instead of a\n"
        "# Disallow, because a crawler has to fetch a page to see the noindex.\n"
        "\n"
        "Sitemap: %s/sitemap.xml\n" % BASE
    )
    open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8", newline="\n").write(txt)
    return txt


# Directories that are never page content: static files, the reverse proxy
# config, and the free sample download (its own indexability is issue #14,
# still open, so it stays out until that is decided).
SCAN_EXCLUDE_DIRS = {"assets", "nginx", "downloads"}
# (priority, changefreq) for pages found by scan_extra_pages, keyed by their
# top-level subdirectory under site/. A bare top-level page not in PAGES
# (for example deck.html or quest.html) falls through to the "" default.
SCAN_META = {"rooms": ("0.7", "monthly"), "articles": ("0.75", "monthly"),
             "zones": ("0.6", "monthly"), "deck": ("0.7", "monthly"),
             "": ("0.7", "monthly")}


def scan_extra_pages():
    """Every indexable page not hand-listed in PAGES above.

    Rooms, zones, articles, the deck and the quest app are built by other
    scripts and already carry their own canonical link and robots meta, put
    there directly rather than through this file. This script's own
    build_sitemap used to only ever walk PAGES, so it could regenerate a
    sitemap missing every room, zone, article, deck and quest page, 143 of
    the 157 real URLs, the moment anyone ran it standalone: those pages had
    only ever been kept in sitemap.xml by hand edits in the commits that
    added them, never by this generator. Reading the live tree here closes
    that gap so the generator matches what is actually on disk.
    """
    out = []
    covered = {os.path.join(SITE, fn) for fn in PAGES}
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in SCAN_EXCLUDE_DIRS]
        top = os.path.relpath(root, SITE)
        top = "" if top == "." else top.split(os.sep)[0]
        priority, changefreq = SCAN_META.get(top, ("0.7", "monthly"))
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(root, fn)
            if fp in covered:
                continue
            src = open(fp, encoding="utf-8").read()
            rm = re.search(r'<meta\s+name="robots"[^>]*content="([^"]*)"', src)
            if rm and "noindex" in rm.group(1):
                continue
            cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', src)
            if not cm:
                continue
            out.append((cm.group(1), priority, changefreq))
    return out


def build_sitemap():
    today = datetime.date.today().isoformat()
    prio = {"index.html": "1.0", "resources.html": "0.9", "method.html": "0.9",
            "book.html": "0.8", "shop.html": "0.7", "consulting.html": "0.7",
            "about.html": "0.5", "contact.html": "0.5"}
    entries = []
    for fn in INDEXABLE:
        p = PAGES[fn]
        entries.append((BASE + p["path"], prio.get(fn, "0.3"), "weekly"))
    entries += scan_extra_pages()
    rows = [
        "  <url>\n"
        "    <loc>%s</loc>\n"
        "    <lastmod>%s</lastmod>\n"
        "    <changefreq>%s</changefreq>\n"
        "    <priority>%s</priority>\n"
        "  </url>" % (url, today, changefreq, priority)
        for url, priority, changefreq in entries
    ]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)
    return len(rows)


if __name__ == "__main__":
    ch = build_pages()
    build_robots()
    n = build_sitemap()
    print("pages written : %d" % len(ch))
    for f in ch:
        print("   %s" % f)
    print("robots.txt    : written")
    print("sitemap.xml   : %d URLs" % n)

# ------------------------------------------------------------------ DECLINED
# Deliberately NOT emitted, because the visible pages do not support it:
#
#   HowTo        resources.html lists micro zone names and the product types for
#                each room. It does not contain the step-by-step instructions
#                themselves; those are in the book. HowTo markup would describe
#                steps that are not on the page. (Google also retired HowTo rich
#                results in 2023, so there is no upside to offset the risk.)
#   FAQPage      No page on the site contains a genuine question-and-answer
#                block. The legal pages use statement headings, not questions.
#   Product      The catalog renders names and prices, but checkout is not live
#                and the terms page says so. Product/Offer markup implies price
#                and availability we cannot honour.
#   Review       There are no customer reviews. A fabricated testimonial that
#   AggregateRating was on the home page has been removed rather than marked up.
#   Person       No author is named anywhere on the site, so Book has no author
#                property. Add one when the site names the author.
#   logo         Organization has no logo property: the brand mark is inline SVG
#                and no raster logo file exists to point at.
#   sameAs       No verified social profiles are linked from the site.
#   SearchAction The site has no search endpoint, so WebSite carries no
#                potentialAction. Claiming one that 404s is a broken promise.
