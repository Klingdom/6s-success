#!/usr/bin/env python3
"""
Build the page that ships the Garage deck: 80 cards, typeset, built
straight off content.json's real seven zones.

WHY THIS FILE EXISTS
---------------------
BACKLOG-2026-09-07.md B9, the fifth and last room built this way after
Kitchen, Entryway, Laundry Room, Home Office and Primary Bathroom. Like
Laundry Room, Home Office and Primary Bathroom, there is no old, mismatched
free Garage deck to disclose against: no free Garage product exists on the
site yet, so this page is the first, at its own URL. This file mirrors
ops/build_primary_bathroom_deck_page.py function for function, and imports
the same shared, room-agnostic rendering helpers (`esc`, `band`,
`card_html`, `print_tile`, the CSS) rather than forking a second copy of
logic that has nothing room-specific in it.

Run:  python ops/build_garage_deck_page.py
Out:  site/garage-deck.html
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
sys.path.insert(0, os.path.join(ROOT, "ops", "cardtext"))

import build_garage_deck as GA                                   # noqa: E402
# Shared, room-agnostic rendering helpers: none of these read anything
# Kitchen-specific, they read only the card dict shape every generator
# here produces (id/type/title/tagline/...), so they are imported rather
# than forked a sixth time.
from build_kitchen_deck_page import (                            # noqa: E402
    esc, num_word as _num_word, colours, band,
    card_html, print_tile, CSS, UMAMI,
)

SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "garage-deck.html")

ZONE_ORDER = GA.ZONE_ORDER

TYPE_LABEL = {
    "ROOM CARD": "Room", "ZONE CARD": "Zone", "FRICTION CARD": "Friction",
    "ROOT CAUSE CARD": "Root Cause", "ACTION CARD": "Action",
    "STANDARD CARD": "Standard", "EVENT CARD": "Event",
}
TYPE_COUNT_ORDER = ["ROOM CARD", "ZONE CARD", "FRICTION CARD",
                     "ROOT CAUSE CARD", "ACTION CARD", "STANDARD CARD",
                     "EVENT CARD"]


def num_word(n: int) -> str:
    return _num_word(n)


# --------------------------------------------------------------- assembly

def build_body(deck: dict) -> str:
    cards = deck["cards"]
    by_id = {c["id"]: c for c in cards}
    import build_kitchen_deck_page as KDP
    KDP.ZONE_TOTAL[0] = sum(1 for c in cards if c.get("type") == "ZONE CARD")
    zmap = {c["zone"]: c for c in cards if c["type"] == "ZONE CARD"}
    fr = {}
    ac = {}
    st = {}
    for c in cards:
        if c["type"] == "FRICTION CARD":
            fr.setdefault(c["zone"], []).append(c)
        elif c["type"] == "ACTION CARD" and c.get("zone"):
            ac.setdefault(c["zone"], []).append(c)
        elif c["type"] == "STANDARD CARD":
            st[c["zone"]] = c
    room = [c for c in cards if c["type"] == "ROOM CARD"][0]
    causes = [c for c in cards if c["type"] == "ROOT CAUSE CARD"]
    events = [c for c in cards if c["type"] == "EVENT CARD"]
    whole = [c for c in cards
             if c["type"] == "ACTION CARD" and not c.get("zone")]

    parts = [f'<section class="kzone kzone-room"><h2>The Garage</h2>'
              f'{card_html(room, by_id)}</section>']
    for name in ZONE_ORDER:
        block = [f'<section class="kzone"><h2>{esc(name)}</h2>',
                  card_html(zmap[name], by_id)]
        block.append('<div class="ksub"><p class="keyebrow">'
                      f'{num_word(len(fr.get(name, [])))} frictions, '
                      f'then the fix</p>')
        for c in fr.get(name, []):
            block.append(card_html(c, by_id))
        for c in ac.get(name, []):
            block.append(card_html(c, by_id))
        if name in st:
            block.append(card_html(st[name], by_id))
        block.append('</div></section>')
        parts.append("".join(block))

    # Names what the three whole-room cards are about, not just how many: a
    # count alone cannot prove the naming below still matches.
    whole_ids = [c["id"] for c in whole]
    assert whole_ids == ["GAA-015", "GAA-016", "GAA-017"], (
        "whole-room action cards changed (%s); the 'fuel-and-chemistry "
        "walk/overhead-and-hook load check/verdict sweep' sentence in "
        "build_body() no longer describes the real three and must be "
        "rewritten by hand" % whole_ids)
    parts.append('<section class="kzone"><h2>Whole garage</h2>'
                  f'<p class="klead-p">{num_word(len(whole))} cards that '
                  'are not one zone’s job: a walk that checks nothing '
                  'flammable sits near a spark or a flame anywhere in '
                  'the room, a check that every hook, rail and overhead '
                  'rack is rated for what it actually carries, and a '
                  'sweep that gives a real verdict, today, to anything '
                  'sitting there postponed rather than stored.</p>'
                  + "".join(card_html(c, by_id) for c in whole)
                  + '</section>')
    parts.append('<section class="kzone"><h2>Root causes, the shared '
                  'deck</h2>'
                  f'<p class="klead-p">Every friction card in the garage '
                  f'points at one of these '
                  f'{num_word(len(causes)).lower()}, the same vocabulary '
                  f'the Kitchen, Entryway, Laundry Room, Home Office and '
                  f'Primary Bathroom decks use. Pull one when a friction '
                  f'card sends you here.</p>'
                  + "".join(card_html(c, by_id) for c in causes)
                  + '</section>')
    parts.append('<section class="kzone"><h2>Events, the day that tests '
                  'it</h2>'
                  '<p class="klead-p">Draw one when an ordinary hard day '
                  'happens, and see whether the standard held.</p>'
                  + "".join(card_html(c, by_id) for c in events)
                  + '</section>')

    rendered = set(re.findall(r'<article class="kcard" id="([^"]+)"',
                               "".join(parts)))
    missing = [c["id"] for c in cards if c["id"] not in rendered]
    assert not missing, f"{len(missing)} cards never rendered: {missing}"
    return "".join(parts)


def build_print_sheet(deck: dict) -> str:
    return '<div class="ksheet">' + "".join(
        print_tile(c) for c in deck["cards"]) + "</div>"


def type_spine(deck: dict) -> str:
    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    items = []
    for t in TYPE_COUNT_ORDER:
        raw, bg, fg, glyph, fam = colours(t)
        items.append(f'<li style="background:{bg};color:{fg}">'
                      f'{esc(TYPE_LABEL[t])} · {by.get(t, 0)}</li>')
    return "".join(items)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Garage Deck: __N__ cards, free to read</title>
<meta name="description" content="The Manual's real __NZONES_LOWER__ Garage zones, the friction each one causes, the root cause, the fix, and the standard to keep. __N__ cards, typeset, free.">
<!-- SEO:BEGIN -->
<link rel="canonical" href="https://6s-success.com/garage-deck.html">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="6S Success">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="https://6s-success.com/garage-deck.html">
<meta property="og:title" content="The Garage Deck: __N__ cards, typeset and free to read">
<meta property="og:description" content="The Manual's real __NZONES_LOWER__ Garage zones, the friction each one causes, the root cause, the fix, and the standard to keep. __N__ cards, typeset, free.">
<meta property="og:image" content="https://6s-success.com/assets/img/rooms/ch32-image01.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://6s-success.com/assets/img/rooms/ch32-image01.jpg">
<meta name="twitter:title" content="The Garage Deck: __N__ cards, typeset and free to read">
<meta name="twitter:description" content="The Manual's real __NZONES_LOWER__ Garage zones, the friction each one causes, the root cause, the fix, and the standard to keep. __N__ cards, typeset, free.">
<meta name="theme-color" content="#22323C">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://6s-success.com/"},
    {"@type": "ListItem", "position": 2, "name": "The Garage Deck", "item": "https://6s-success.com/garage-deck.html"}
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Game",
  "@id": "https://6s-success.com/garage-deck.html#deck",
  "name": "The 6S Success Garage Deck",
  "url": "https://6s-success.com/garage-deck.html",
  "inLanguage": "en",
  "numberOfPlayers": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 4},
  "gameItem": {"@type": "Thing", "name": "__N__ printable cards, front and back, typeset, no illustrations yet"},
  "publisher": {"@id": "https://6s-success.com/#organization"},
  "genre": "Household organization",
  "abstract": "A __N__ card deck for the garage, built from the Manual's real __NZONES_LOWER__ zones: the frictions each one causes, the __NCAUSES_LOWER__ root causes underneath (shared with the Kitchen, Entryway, Laundry Room, Home Office and Primary Bathroom decks), the actions that fix them, and the standard each zone keeps. Typeset, free, no illustrations yet."
}
</script>
<!-- SEO:END -->
<link rel="stylesheet" href="assets/css/site.css?v=326a1059ac">
<style>
__CSS__
</style>
<!-- PWA:BEGIN -->
<link rel="icon" href="assets/img/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<!-- PWA:END -->
<!-- PROGRESSIVE:BEGIN -->
<script>document.documentElement.className+=" js";</script>
<!-- PROGRESSIVE:END -->
</head>
<body>
<!-- SKIP:BEGIN -->
<a class="skip-link" href="#main">Skip to content</a>
<!-- SKIP:END -->
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="index.html" aria-label="6S Success home">
      <svg class="mark" viewBox="0 0 40 34" aria-hidden="true">
        <path d="M4 30 A16 16 0 0 1 36 30" fill="none" stroke="#E2D8C4" stroke-width="4" stroke-linecap="round"/>
        <path d="M4 30 A16 16 0 0 1 12 16.2" fill="none" stroke="#BC4B2A" stroke-width="4" stroke-linecap="round"/>
        <path d="M12 16.2 A16 16 0 0 1 28 16.2" fill="none" stroke="#DDA63A" stroke-width="4"/>
        <path d="M28 16.2 A16 16 0 0 1 36 30" fill="none" stroke="#6E8B5B" stroke-width="4" stroke-linecap="round"/>
        <line x1="20" y1="30" x2="29" y2="19" stroke="#2B2622" stroke-width="2.4" stroke-linecap="round"/>
        <circle cx="20" cy="30" r="3" fill="#2B2622"/>
      </svg>
      6S&nbsp;Success
    </a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
    <nav class="nav" aria-label="Primary">
      <a href="zones/">Start a reset</a>
      <a href="method.html">How 6S works</a>
      <a href="resources.html">Rooms</a>
      <a href="book.html">Cards and book</a>
      <a href="consulting.html">Get help</a>
    </nav>
    <div class="header-cta">
      <a class="btn btn-primary btn-sm" href="contact.html">Contact</a>
    </div>
  </div>
</header>
<main id="main">

<section class="hero">
  <div class="wrap">
    <div class="hero-copy">
      <p class="eyebrow on-deep">The deck, seven zones</p>
      <h1>The <em>Garage</em> Deck</h1>
      <p class="sub">__N__ cards: the Manual's real __NZONES_LOWER__ Garage zones, the frictions each one causes, the __NCAUSES_LOWER__ root causes underneath, the actions that fix them, and the standard each zone keeps. Typeset and free. No illustrations yet, so every card reads as text, not a photograph.</p>
      <div class="cta-row">
        <a class="btn btn-primary btn-lg" href="#garage-cards">Read the deck</a>
      </div>
      <p class="fulfil-note">Prefer paper? This page's own print layout lays the fronts out at true card size. Use your browser's print dialog.</p>
      <p class="fulfil-note">This is the first Garage deck on the site: built straight from the same Manual as the Kitchen, Entryway, Laundry Room, Home Office and Primary Bathroom decks, with the same rules.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">Built from the Manual, not around it</p>
    <h2>Seven zones, real diagnosis, nothing invented</h2>
    <p>__INTRO__</p>
    <p>Every card here is real: written from the same source as the Manual and the zone pages, gated so a root cause with no friction pointing at it, or an action nobody's problem needs, cannot ship. None of it is generated placeholder copy. What is missing is photography, which this deck does not pretend to have. A family-coloured panel and the card's own symbol stand where a photograph will eventually go.</p>
  </div>
</section>

<section class="section band" id="whats-in-it">
  <div class="wrap">
    <p class="eyebrow">__N__ cards, __NKINDS_LOWER__ kinds</p>
    <h2>One zone, one friction, one cause, one fix, one standard</h2>
    <p class="lede">A Zone card names the place. Friction cards say what a household actually complains about there. Each friction points at a Root Cause, and each cause names the Action that fixes it. A Standard card is what you write down and keep. Event cards are the days that test whether it held.</p>
    <ul class="spine">__SPINE__</ul>
  </div>
</section>

<section class="section" id="garage-cards">
  <div class="wrap">
    <p class="eyebrow">The deck</p>
    <h2>Read it here, zone by zone</h2>
    <p>Tap a card's "How it works" to see its back. Start at the workbench: it is the one surface the whole garage depends on, and clearing it changes what you can get done in every other zone.</p>
__BODY__
  </div>
</section>

<div class="print-only" aria-hidden="true">
__SHEET__
</div>

</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div class="brand-col">
        <a class="brand" href="index.html" style="color:#fff">
          <svg class="mark" viewBox="0 0 40 34" aria-hidden="true"><path d="M4 30 A16 16 0 0 1 36 30" fill="none" stroke="#33474F" stroke-width="4" stroke-linecap="round"/><path d="M4 30 A16 16 0 0 1 12 16.2" fill="none" stroke="#BC4B2A" stroke-width="4" stroke-linecap="round"/><path d="M12 16.2 A16 16 0 0 1 28 16.2" fill="none" stroke="#DDA63A" stroke-width="4"/><path d="M28 16.2 A16 16 0 0 1 36 30" fill="none" stroke="#6E8B5B" stroke-width="4" stroke-linecap="round"/><line x1="20" y1="30" x2="29" y2="19" stroke="#EDE4D2" stroke-width="2.4" stroke-linecap="round"/><circle cx="20" cy="30" r="3" fill="#EDE4D2"/></svg>
          6S&nbsp;Success
        </a>
        <p>A calm home, built one S at a time. Books, training, tools, and consulting for the six-S method, at home and at work.</p>
        <p class="newsletter-offer">Get your first five Quest cards. One small zone each day, with a clear finish line. <a href="quest.html">Start free, no email needed</a></p>
        <form class="foot-newsletter" onsubmit="return false" aria-label="Newsletter signup">
          <input type="email" placeholder="Your email" aria-label="Email address">
          <button class="btn btn-primary btn-sm" type="submit">Keep me posted</button>
        </form>
      </div>
      <div><h2>Learn</h2><a href="method.html">The Method</a><a href="book.html">The Book</a><a href="resources.html">Rooms and micro zones</a><a href="articles/">Articles</a><a href="deck.html">The Entryway Deck</a><a href="standards.html">The Standards Pack</a><a href="quest.html">The Home Quest</a><a href="shop.html?cat=Books%20%26%20Guides">The Print Pack</a><a href="method.html#videos">Video series</a></div>
      <div><h2>Shop</h2><a href="consulting.html">Consulting</a><a href="shop.html?cat=Books%20%26%20Guides">Books and guides</a><a href="shop.html">Everything</a></div>
      <div><h2>Company</h2><a href="about.html">About</a><a href="consulting.html">Consulting</a><a href="corporate.html">Lean 6S for teams</a><a href="contact.html">Contact</a><a href="about.html#nova">Nova Consulting</a></div>
    </div>
    <div class="foot-bottom"><span>&copy; 2026 6S Success &middot; A Nova Consulting brand</span><span><a href="privacy.html">Privacy</a> &middot; <a href="how-we-make-money.html">How we make money</a> &middot; <a href="affiliate-disclosure.html">Affiliate disclosure</a> &middot; <a href="terms.html">Terms</a> &middot; <a href="accessibility.html">Accessibility</a> &middot; <a href="disclaimer.html">Safety notice</a></span></div>
  </div>
</footer>
<script src="assets/js/site.js?v=c3275be873"></script>
__UMAMI__
<!-- MEASURE:BEGIN -->
<script defer src="assets/js/measure.js?v=7985935c0c"></script>
<!-- MEASURE:END -->
</body>
</html>
"""


def main() -> int:
    deck = GA.build()
    src = json.load(io.open(GA.SRC, encoding="utf-8"))
    intro = [r for r in src["rooms"]
             if r["room"] == "Garage"][0]["intro"]

    n_total = deck["count"]
    n_zones = len(ZONE_ORDER)
    n_causes = len([c for c in deck["cards"] if c["type"] == "ROOT CAUSE CARD"])
    n_kinds = len(TYPE_COUNT_ORDER)

    page = (PAGE
            .replace("__CSS__", CSS)
            .replace("__INTRO__", esc(intro))
            .replace("__SPINE__", type_spine(deck))
            .replace("__BODY__", build_body(deck))
            .replace("__SHEET__", build_print_sheet(deck))
            .replace("__UMAMI__", UMAMI)
            .replace("__N__", str(n_total))
            .replace("__NZONES_LOWER__", num_word(n_zones).lower())
            .replace("__NZONES__", num_word(n_zones))
            .replace("__NCAUSES_LOWER__", num_word(n_causes).lower())
            .replace("__NKINDS_LOWER__", num_word(n_kinds).lower()))

    io.open(OUT, "w", encoding="utf-8", newline="").write(page)

    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  garage deck page  {deck['count']} cards")
    for t in TYPE_COUNT_ORDER:
        print(f"    {TYPE_LABEL[t]:<10} {by.get(t, 0)}")
    print(f"  written  {os.path.relpath(OUT, ROOT)}")

    # Same whole-site wiring chain every other single-page generator here
    # re-runs on its own output.
    import canonical_links
    import prune_catalog_js
    import wire_landmarks
    import wire_progressive
    import wire_measure
    import wire_pwa
    import wire_aria_current
    import build_avif
    import fingerprint_assets
    canonical_links.main()
    prune_catalog_js.main()
    wire_landmarks.main()
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()
    wire_aria_current.main()
    build_avif.wire()
    fingerprint_assets.main(False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
