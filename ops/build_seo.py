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
import json, os, re, datetime, subprocess

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
    # An Organization with no logo is harder for a search or answer engine to
    # recognise as an entity at all. This one is real and self hosted, which is
    # the only reason it is here.
    #
    # sameAs is deliberately absent. It is the other half of entity
    # recognition and it lists the profiles that prove an organisation is who
    # it says it is, so an invented one is a fabricated authority signal.
    # Nothing in this repository or on this site references a social profile,
    # so there is nothing honest to put here yet.
    "logo": {"@type": "ImageObject",
             "url": BASE + "/assets/img/apple-touch-icon.png",
             "width": 180, "height": 180},
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
    # Each item points at that room's own page, not at an anchor on this one.
    # An ItemList whose twenty entries all resolve to a single URL tells a
    # search or answer engine that this site has one page about rooms. It has
    # twenty, each with its own canonical, its own CollectionPage node and its
    # own three to seven micro zone pages under it, and pointing here is what
    # connects those entities to the hub. The visible page links the same
    # twenty destinations, so the markup and the page agree.
    "itemListElement": [
        {"@type": "ListItem", "position": i, "name": name,
         "url": BASE + "/rooms/" + slug}
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
# WHAT THESE TWELVE PICTURES ACTUALLY ARE.
#
# Every og:image on this site is one of twelve files in assets/img, and none
# of them is a photograph of a room. They are figures lifted out of the book,
# most of them carrying their own printed figure number and heading. That was
# never written down anywhere, so the alt text under each one described the
# room somebody assumed was in the picture, and social previews and screen
# readers were told things that are not in the file:
#
#   calm-living.jpg     Figure 15-01, "Good Homes. No Shared Picture."
#                       An entryway with dashed outlines around six zones and
#                       a question mark. Called "a calm, ordered living room"
#                       on eight pages. It is neither calm, ordered, nor a
#                       living room.
#   family.jpg          Figure 28-02, "The Difference Between a Symptom and a
#                       Cause". A four row chart. Called "a family in a calm,
#                       ordered home". There are no people in it.
#   reset.jpg           Figure 19-05, "The Power of the Timer". A without and
#                       with comparison. Called "sorted piles and labelled
#                       containers". There are none.
#   reset-together.jpg  Figure 19-10, "A Real 15-Minute Reset". Six numbered
#                       panels with a clock. Called "a consultant and a
#                       homeowner resetting a room side by side".
#   rhythm.jpg          Figure 29-07, "The Family Reset".
#   renewed.jpg         Figure 30-01, a Done and Renewed pair.
#   room-map.jpg        Figure 15-03, "The Home as Activity Zones", an
#                       isometric floor plan. The one alt that was roughly
#                       right.
#   standard.jpg        Figure 25-02, a pantry cupboard with its ideal-state
#                       photograph taped inside the door.
#   shine.jpg           Figure 16-04, "Cleaning Changes What You Can See".
#   straighten.jpg      Chapter 12, "Every Keeper Needs One Home".
#   hero-entry.jpg      Chapter 6, "Photograph Before You Fix".
#   prepare.jpg         "Five Jobs vs. One Job", an entryway before and after.
#
# Each alt below now says what is in its file. If a picture is replaced, the
# alt is part of the replacement, not something to inherit.

PAGES = {
    "index.html": dict(
        path="/",
        title="6S Success: the six-S method for organizing and cleaning a home",
        desc="Sort, Straighten, Shine, Safety, Standardize, Sustain: the Lean "
             "six-S method rebuilt for the home. Twenty rooms, 114 micro zones, "
             "and a fifty-chapter book.",
        image="renewed.jpg",
        image_alt="A book figure: two entryways side by side, one labelled Done and slipping back, one labelled Renewed with a family resetting it.",
        type="website",
        jsonld=[ORGANIZATION, WEBSITE],
    ),
    "method.html": dict(
        path="/method.html",
        title="Six S's: Sort, Straighten, Shine, Safety, Standardize, Sustain",
        desc="What each of the six S's actually asks of you, in the order that "
             "works, plus every way to learn the method: the book, courses, "
             "workshops, and the app.",
        image="room-map.jpg",
        image_alt="A book figure: an isometric floor plan of a home with each activity zone shaded and named, from launch pad to laundry.",
        type="article",
        jsonld=[crumbs(("Home", "/"), ("The method", "/method.html"))],
    ),
    "resources.html": dict(
        path="/resources.html",
        title="Rooms and micro zones: 20 rooms, 114 micro zones | 6S Success",
        desc="Every room broken into its micro zones, in the order to work them, "
             "with the product types each one needs. Twenty rooms, 114 micro "
             "zones.",
        image="room-map.jpg",
        image_alt="A book figure: an isometric floor plan of a home with each activity zone shaded and named, from launch pad to laundry.",
        type="article",
        jsonld=[crumbs(("Home", "/"), ("Rooms and micro zones", "/resources.html")),
                ROOM_LIST],
    ),
    "book.html": dict(
        path="/book.html",
        title="6S Success: Home Edition, the book, 50 chapters, 20 rooms",
        desc="Fifty chapters across nine parts, from your first room to twenty "
             "room-by-room playbooks. Chapters 1 to 30 are free to read online "
             "or download as a PDF.",
        image="renewed.jpg",
        image_alt="A book figure: two entryways side by side, one labelled Done and slipping back, one labelled Renewed with a family resetting it.",
        type="book",
        jsonld=[crumbs(("Home", "/"), ("The book", "/book.html")), BOOK],
    ),
    "shop.html": dict(
        path="/shop.html",
        title="Shop: books, guides, consulting, and the free app | 6S Success",
        desc="The book, the Manual, the Print Pack, the free Entryway Deck, the "
             "free Home Quest app, and consulting. Checkout for every priced "
             "item is live.",
        image="reset.jpg",
        image_alt="A book figure comparing a reset without a timer, which feels endless, against the same reset with a fifteen minute timer running.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Shop", "/shop.html"))],
    ),
    "consulting.html": dict(
        path="/consulting.html",
        # The old title and description sold an enquiry ("Request a quote")
        # for two things that can be bought outright, and named neither price.
        # The page now states both in its first screen, so the snippet that
        # brings somebody to it should qualify them the same way: the money and
        # the geographic limit are the two facts that decide whether the click
        # is worth anyone's time. Both figures are the live catalogue prices for
        # CN-VIRTUAL and CN-INHOME in site/assets/js/data.js.
        title="Home reset consulting: $250 online, $1,200 on site | 6S Success",
        # 191 characters was truncated in the result, which throws away the
        # refund term at the end. Both prices and the geography survive here.
        desc="An hour on video for $250, or a full day on site for $1,200 in "
             "the Treasure Valley, Idaho. You keep a written plan. Refunded "
             "within 7 days.",
        image="reset-together.jpg",
        image_alt="A book figure: six numbered photographs of a fifteen minute reset, clock running from zero to fifteen across kitchen, bathroom, living room and entryway.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Consulting", "/consulting.html")),
                CONSULTING_SERVICE],
    ),
    "about.html": dict(
        path="/about.html",
        title="About 6S Success: a factory discipline, rebuilt for real homes",
        desc="6S Success brings the Lean six-S method home: Sort, Straighten, "
             "Shine, Safety, Standardize, Sustain. Change the method, not your "
             "character.",
        image="family.jpg",
        image_alt="A book figure charting four household symptoms, such as coats on the chair, across to the cause underneath each one.",
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
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Contact", "/contact.html")),
                {"@type": "ContactPage", "url": BASE + "/contact.html",
                 "name": "Contact 6S Success", "mainEntity": {"@id": ORG_ID}}],
    ),
    "privacy.html": dict(
        path="/privacy.html",
        title="Privacy: no cookies, no trackers, no third parties | 6S Success",
        desc="What 6S Success does with your information: self hosted visit "
             "counts only, no cookies, no trackers, no advertising networks "
             "and no third party requests.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Privacy", "/privacy.html"))],
    ),
    "terms.html": dict(
        path="/terms.html",
        title="Terms of use: what is for sale and what is not | 6S Success",
        desc="Terms of use for 6s-success.com: what you can buy today through "
             "Stripe, what is not for sale yet, how the content may be used, "
             "and the limits of liability.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Terms", "/terms.html"))],
    ),
    "accessibility.html": dict(
        path="/accessibility.html",
        title="Accessibility at 6S Success: what works, what does not",
        desc="Our accessibility commitment for 6s-success.com, what the site does "
             "today, and an honest list of the gaps we have not closed yet.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Accessibility", "/accessibility.html"))],
    ),
    "disclaimer.html": dict(
        path="/disclaimer.html",
        title="Safety notice: read before any cleaning or organizing step",
        desc="Important safety information before following any 6S Success "
             "cleaning or organizing instruction: chemicals, tools, height, "
             "children, pets, and emergencies.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"), ("Safety notice", "/disclaimer.html"))],
    ),

    # The two commercial-honesty pages. Both were hand authored and neither
    # was ever registered here, so how-we-make-money.html was carrying a
    # copy-pasted SEO block that still described terms.html in its Twitter
    # card, and affiliate-disclosure.html had no entry to inherit one from.
    # Registering them puts both heads under this generator, which is the
    # only thing that keeps them from drifting again.
    "how-we-make-money.html": dict(
        path="/how-we-make-money.html",
        title="How we make money: what we sell, and what we do not earn on",
        desc="Where 6S Success revenue comes from: our own books, packs, decks "
             "and consulting. No ads, no sponsorship, no affiliate programme "
             "earning us anything.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"),
                       ("How we make money", "/how-we-make-money.html"))],
    ),
    "affiliate-disclosure.html": dict(
        path="/affiliate-disclosure.html",
        title="Affiliate disclosure: no link on this site earns a commission",
        desc="6S Success has no approved affiliate programme, so no link here "
             "earns a commission today. What that means, and where a paying "
             "link would never appear.",
        image="calm-living.jpg",
        image_alt="A book figure: an entryway with dashed outlines drawn around the keys, leash, umbrella, mail, shoe and backpack zones, and a question mark where the household&#39;s shared picture should be.",
        type="website",
        jsonld=[crumbs(("Home", "/"),
                       ("Affiliate disclosure", "/affiliate-disclosure.html"))],
    ),

    # ------------------------------------------------------------ not indexed
    # A cart is a per-visitor utility view with no standalone value, and it
    # cannot be entered usefully from a search result. Crawlable, not indexed.
    "cart.html": dict(
        path="/cart.html",
        title="Your cart | 6S Success",
        desc="Review the items you have picked. Every priced item on this site "
             "checks out directly and securely through Stripe.",
        image="reset.jpg",
        image_alt="A book figure comparing a reset without a timer, which feels endless, against the same reset with a fifteen minute timer running.",
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
        image="room-map.jpg",
        image_alt="A book figure: an isometric floor plan of a home with each activity zone shaded and named, from launch pad to laundry.",
        type="website", robots="noindex, follow", jsonld=[],
    ),
}

INDEXABLE = [f for f, p in PAGES.items() if not p.get("robots")]

# Every other page that names ORG_ID names it only as a bare {"@id": ...}
# reference (AboutPage.mainEntity, ContactPage.mainEntity,
# CONSULTING_SERVICE.provider): correct JSON-LD, but it only resolves for a
# consumer that fetches index.html too, and most structured-data readers
# parse one page at a time. The Organization description is true of every
# page on the site, not just the home page, so the full node is prepended
# here rather than left as a dangling reference on any indexed page that is
# not already carrying it whole.
for _fn, _p in PAGES.items():
    if _fn in INDEXABLE and not any(n is ORGANIZATION for n in _p["jsonld"]):
        _p["jsonld"] = [ORGANIZATION] + _p["jsonld"]


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
    L += verification_tags(fn)
    for node in p["jsonld"]:
        doc = dict(node)
        doc["@context"] = "https://schema.org"
        doc = {"@context": "https://schema.org", **node}
        L.append('<script type="application/ld+json">\n%s\n</script>'
                 % json.dumps(doc, indent=2, ensure_ascii=False))
    L.append(END)
    return "\n".join(L)


# ------------------------------------------------------- ownership verification
#
# Google is the one search engine that will not take a sitemap without an
# account, and as of 2026-09-03 nothing on this site claims the domain to any
# platform. That is why the sitemap has never been submitted to Google and why
# there is no impressions data at all.
#
# The gate is genuinely Phil's: only he can log into his own Google account and
# read the token out of it. Everything on THIS side of that gate is built here,
# so his part is "paste a string into ops/site-verification.json, run this
# script, deploy". No code change, no markup to hand-edit, no chance of pasting
# a whole <meta> tag into a content attribute.
#
# The tags go on the home page only. Every platform below verifies the property
# root, so putting them on 185 pages would add bytes to 184 pages that nobody
# ever reads them from.
VERIFY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "site-verification.json")
# config key -> the meta name the platform actually looks for
VERIFY_META = {
    "google_meta": "google-site-verification",
    "bing": "msvalidate.01",
    "pinterest": "p:domain_verify",
    "yandex": "yandex-verification",
}
VERIFY_HOME = "index.html"


def load_verification():
    """Tokens the owner has filled in. Missing file is not an error: the site
    is simply unverified, which is the state it has been in since launch."""
    try:
        with open(VERIFY_FILE, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except FileNotFoundError:
        return {}
    except (ValueError, OSError) as e:
        # Loud, because a malformed file here silently means "unverified" and
        # unverified looks identical to "not filled in yet".
        print("  WARNING: %s unreadable, no verification tags emitted: %s"
              % (os.path.basename(VERIFY_FILE), e))
        return {}
    out = {}
    for k, v in cfg.items():
        if k.startswith("_") or not isinstance(v, str):
            continue
        v = v.strip()
        if v:
            out[k] = v
    return out


def verification_tags(fn):
    cfg = load_verification()
    if fn != VERIFY_HOME or not cfg:
        return []
    tags = []
    for key, meta_name in VERIFY_META.items():
        token = cfg.get(key)
        if not token:
            continue
        # Guard against the commonest paste error: dropping the whole tag in
        # rather than the content value. Left alone it produces markup the
        # platform cannot read and a verification that silently never passes.
        if "<" in token or 'content=' in token:
            m = re.search(r'content=["\']([^"\']+)["\']', token)
            if not m:
                print("  WARNING: %s looks like a whole tag, not a token; skipped"
                      % key)
                continue
            token = m.group(1)
        tags.append('<meta name="%s" content="%s">' % (meta_name, esc(token)))
    return tags


def build_verification_file():
    """The file half of Google's two verification methods.

    Google names a file (google<hash>.html) and expects its body to be the
    single line "google-site-verification: <that same filename>". Writing it
    from the token means the filename and the body can never disagree, which is
    the only way this method fails in practice.

    Returns the path written, or None.
    """
    cfg = load_verification()
    name = cfg.get("google_html", "")
    if not name:
        return None
    name = os.path.basename(name.strip())
    if not re.fullmatch(r"google[0-9a-zA-Z_-]+\.html", name):
        print("  WARNING: google_html %r is not a google<token>.html filename;"
              " nothing written" % name)
        return None
    p = os.path.join(SITE, name)
    # No canonical link and no robots meta, so scan_extra_pages() skips it and
    # it never reaches the sitemap. That is deliberate: it is a proof of
    # ownership, not a page.
    open(p, "w", encoding="utf-8", newline="\n").write(
        "google-site-verification: %s\n" % name)
    return p


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
    # sorted(), not just filtered: os.walk() yields subdirectories in
    # whatever order os.scandir() returns them, which is filesystem order,
    # not name order, and differs between a long-lived local checkout and a
    # fresh CI clone of the identical commit. That produced a sitemap.xml
    # whose row order matched its own generator on the machine that wrote
    # it and disagreed on any other, so gate_generator_ownership flagged
    # "drift" that was really just reordering with no content change,
    # repeatedly, on regenerations that were otherwise correct.
    for root, dirs, files in os.walk(SITE):
        dirs[:] = sorted(d for d in dirs if d not in SCAN_EXCLUDE_DIRS)
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
            out.append((cm.group(1), priority, changefreq, fp))
    return out


def _committed_date(fp):
    """The date this file was last committed, which is the same in every
    checkout of the same commit.

    Replaces a working-tree comparison that was environment sensitive.
    _changed_since_head() asks whether the file differs from HEAD *right now*,
    so a page regenerated during preflight's generator-ownership gate could
    look changed on a CI runner and unchanged on this machine. The sitemap then
    differed between the two, and the gate failed the build on drift that only
    existed because the gate itself had just run the generators. That blocked
    the publish twice on 2026-09-04.

    A commit date cannot drift that way. Returns None when git cannot answer,
    and the caller keeps whatever lastmod is already recorded rather than
    stamping today over it.
    """
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception:                                           # noqa: BLE001
        return None
    d = (r.stdout or "").strip()
    return d if r.returncode == 0 and len(d) == 10 else None


def _existing_lastmods():
    fp = os.path.join(SITE, "sitemap.xml")
    if not os.path.exists(fp):
        return {}
    src = open(fp, encoding="utf-8").read()
    return dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", src))


def build_sitemap():
    """lastmod is per-URL, not a single stamp for the whole file: a page whose
    working-tree content has not moved since the last commit keeps the
    lastmod already in sitemap.xml, and only a page that actually changed (or
    is new) gets today's date. See issue #23: the old version stamped every
    row with datetime.date.today() on every run, so adding one page rewrote
    the other 180-plus with a false modification date.
    """
    today = datetime.date.today().isoformat()
    prio = {"index.html": "1.0", "resources.html": "0.9", "method.html": "0.9",
            "book.html": "0.8", "shop.html": "0.7", "consulting.html": "0.7",
            "about.html": "0.5", "contact.html": "0.5"}
    entries = []
    for fn in INDEXABLE:
        p = PAGES[fn]
        entries.append((BASE + p["path"], prio.get(fn, "0.3"), "weekly",
                         os.path.join(SITE, fn)))
    entries += scan_extra_pages()
    prev = _existing_lastmods()
    rows = []
    for url, priority, changefreq, fp in entries:
        # An existing URL keeps the lastmod already recorded; only a URL the
        # sitemap has never carried gets today.
        #
        # This deliberately does NOT ask git when the file last changed. I
        # tried that on 2026-09-04 to make the value platform independent, and
        # it is self-referential: the sitemap records commit dates, committing
        # the sitemap changes those dates, so the next run produces a different
        # file and generator-ownership fails forever. It also does not ask
        # whether the working tree differs from HEAD, which was the previous
        # version and was environment dependent for the same reason the gate
        # regenerates pages before comparing them.
        #
        # The cost is that editing a page no longer bumps its lastmod by
        # itself. That is the right trade: lastmod is a hint to a crawler, and
        # a stable build is worth more than an automatic hint. Bump it
        # deliberately by removing the row.
        lastmod = prev.get(url) or today
        rows.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>%s</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>" % (url, lastmod, changefreq, priority)
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)
    return len(rows)


if __name__ == "__main__":
    ch = build_pages()
    build_robots()
    n = build_sitemap()
    vf = build_verification_file()
    print("pages written : %d" % len(ch))
    for f in ch:
        print("   %s" % f)
    print("robots.txt    : written")
    print("sitemap.xml   : %d URLs" % n)
    _v = load_verification()
    _named = [k for k in VERIFY_META if _v.get(k)]
    if vf:
        _named.append("google_html -> " + os.path.basename(vf))
    print("verification  : %s" % (", ".join(_named) if _named
                                  else "NONE. The site claims ownership to no "
                                       "platform, so Google Search Console has "
                                       "no data. See OWNER-ACTIONS.md."))

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
#   Product      Emitted separately, by ops/build_product_schema.py, chained to
#                ops/stripe_catalog.py so Product/Offer markup only ever names a
#                price and availability Stripe can actually honour.
#   Review       There are no customer reviews. A fabricated testimonial that
#   AggregateRating was on the home page has been removed rather than marked up.
#   Person       No author is named anywhere on the site, so Book has no author
#                property. Add one when the site names the author.
#   logo         Organization has no logo property: the brand mark is inline SVG
#                and no raster logo file exists to point at.
#   sameAs       No verified social profiles are linked from the site.
#   SearchAction The site has no search endpoint, so WebSite carries no
#                potentialAction. Claiming one that 404s is a broken promise.
