#!/usr/bin/env python3
"""
Build the page that ships the Kitchen deck: 72 cards, typeset, unillustrated.

WHY THIS SHAPE
--------------
BACKLOG-2026-09-07.md B1: "Ship the Kitchen deck typeset and unillustrated,
free, ungated." The card copy is finished and gated
(ops/cardtext/build_kitchen_deck.py); nothing has ever shown it to a reader.

The Entryway deck's gallery (ops/build_deck_gallery.py) is a photograph
viewer: every tile is a real <img>, sized off a scanned JPEG's own SOF
marker, flipped between two photographed faces. The Kitchen deck has no
photographs at all yet (image generation is billing-gated, C5, unresolved),
so that machinery does not fit and is not reused: there is nothing to
photograph. This page typesets the cards instead, in HTML and CSS, at the
same floor ops/card_spec.py already enforces for the printed deck (7pt
floor, 8.5pt for a running sentence), and does not pretend a hero
illustration exists where none does. A family-tinted panel carrying the
card's own glyph stands in the art position; it says what kind of card this
is, not what a kitchen looks like.

Two views of the same 72 cards:
  ON SCREEN   every card as a front (always visible) and a native <details>
              disclosure for the back, grouped the way the deck's own Room
              card explains it is played: zone by zone, then the shared
              Root Cause reference, then the Events.
  IN PRINT    a flat sheet of the 72 fronts only, laid out at true card size
              (2.5 x 3.5in, ops/card_spec.py's own trim), three to a row on
              US Letter, the same physical size as every other deck and pack
              this project ships, so a mixed pile still handles the same.
              Fronts only: a back needs its front on the other side of one
              physical card, which this generator does not attempt to pair
              for double-sided home printing.

Run:  python ops/build_kitchen_deck_page.py
Out:  site/kitchen-deck.html
"""
from __future__ import annotations

import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ops"))
sys.path.insert(0, os.path.join(ROOT, "ops", "cardtext"))

import card_spec as S                                           # noqa: E402
import build_kitchen_deck as KD                                 # noqa: E402

SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "kitchen-deck.html")

UMAMI = ('<script defer src="/stats/script.js" '
         'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
         'data-host-url="https://6s-success.com/stats"></script>')

ZONE_ORDER = ["Primary Prep Counter", "Cooking Zone",
              "Sink and Dishwashing Zone", "Upper Cabinet Zone",
              "Lower Cabinet and Cookware Zone",
              "Utensil and Utility Drawers", "Refrigerator and Freezer"]

TYPE_LABEL = {
    "ROOM CARD": "Room", "ZONE CARD": "Zone", "FRICTION CARD": "Friction",
    "ROOT CAUSE CARD": "Root Cause", "ACTION CARD": "Action",
    "STANDARD CARD": "Standard", "EVENT CARD": "Event",
}
TYPE_COUNT_ORDER = ["ROOM CARD", "ZONE CARD", "FRICTION CARD",
                     "ROOT CAUSE CARD", "ACTION CARD", "STANDARD CARD",
                     "EVENT CARD"]


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def short(text: str, limit: int = 118) -> str:
    """First sentence if it is short enough, else a word-boundary cut.

    Never a mid-word cut: ops/build_youtube_metadata.py's first_sentence()
    was fixed for the exact opposite mistake (2026-09-07, C3) and this
    follows the same rule rather than reintroducing it.
    """
    text = text.strip()
    m = re.search(r"[.!?](?:\s|$)", text)
    if m and m.end() <= limit + 20:
        return text[:m.end()].strip()
    if len(text) <= limit:
        return text
    cut = text.rfind(" ", 0, limit)
    cut = cut if cut > 0 else limit
    return text[:cut].rstrip(",.;: ") + "…"


def strip_num(line: str) -> str:
    return re.sub(r"^\d+\.\s*", "", line).strip()


def pips(n: int) -> str:
    n = int(n or 0)
    return ("●" * n) + ("○" * (5 - n))


def colours(card_type: str) -> tuple:
    fam = S.family_of(card_type)
    raw, glyph, _hue = S.FAMILY[fam]
    return raw, S.band_bg(raw), S.on(raw), glyph, fam


def band(card: dict) -> str:
    raw, bg, fg, glyph, fam = colours(card["type"])
    return (f'<div class="kband" style="background:{bg};color:{fg}">'
            f'<span class="kglyph" aria-hidden="true">{glyph}</span>'
            f'<span class="ktype">{esc(fam)}</span>'
            f'<span class="kid">{esc(card["id"])}</span></div>')


def art_panel(card: dict) -> str:
    raw, bg, fg, glyph, fam = colours(card["type"])
    return (f'<div class="kart" style="background:{raw}22;color:{raw}" '
            f'role="img" aria-label="{esc(fam)} card, no illustration yet">'
            f'<span aria-hidden="true">{glyph}</span></div>')


def diff_html(card: dict) -> str:
    n = card.get("difficulty")
    if not n:
        return ""
    return (f'<span class="kdiff" title="difficulty {n} of 5">'
            f'{pips(n)}</span>')


# --------------------------------------------------------------- per type

def front_text(card: dict) -> str:
    t = card["type"]
    if t == "FRICTION CARD":
        return f"“{card['objective']}”"
    if t == "ACTION CARD":
        return card["goal"] if "goal" in card else card["objective"]
    return card["objective"]


def back_body(card: dict, by_id: dict) -> str:
    t = card["type"]
    out = []
    if t == "ROOM CARD":
        out.append(f'<p class="kcall"><strong>Start here.</strong> '
                    f'{esc(card["start_here"])}</p>')
        out.append('<h4>The seven zones, in order</h4><ol class="ktight">'
                    + "".join(f"<li>{esc(z)}</li>"
                              for z in card["zones_in_order"]) + "</ol>")
        out.append('<h4>How to play</h4><ol>'
                    + "".join(f"<li>{esc(strip_num(s))}</li>"
                              for s in card["how_to_play"]) + "</ol>")
        out.append(f'<p><strong>Players.</strong> {esc(card["players"])}</p>')
        out.append(f'<p class="ksafety"><strong>Safety first.</strong> '
                    f'{esc(card["safety_first"])}</p>')
    elif t == "ZONE CARD":
        out.append(f'<p><strong>Done looks like:</strong> '
                    f'{esc(card["done_looks_like"])}</p>')
        out.append('<h4>Six things to check</h4><ol>'
                    + "".join(f"<li>{esc(c)}</li>" for c in card["callouts"])
                    + "</ol>")
        for w in card.get("safety_checks", []):
            out.append(f'<p class="ksafety"><strong>{esc(w["question"])}</strong> '
                        f'{esc(w["text"])}</p>')
        tc = card.get("the_call", {})
        if tc.get("text"):
            out.append(f'<p class="kcall"><strong>{esc(tc["title"])}.</strong> '
                        f'{esc(tc["text"])}</p>')
        if card.get("supplies"):
            out.append('<h4>What it uses</h4><ul>'
                        + "".join(f"<li>{esc(s)}</li>" for s in card["supplies"])
                        + "</ul>")
    elif t == "FRICTION CARD":
        out.append(f'<p>{esc(card["prompt"])}</p>')
        out.append('<ol>' + "".join(
            f'<li>{esc(b["answer"])} → '
            f'<a href="#{esc(b["root_cause"])}">'
            f'{esc(by_id[b["root_cause"]]["title"])}</a></li>'
            for b in card["branches"]) + "</ol>")
        out.append(f'<p>{esc(card["instruction"])}</p>')
    elif t == "ROOT CAUSE CARD":
        out.append(f'<p><strong>Confirm in 30 seconds:</strong> '
                    f'{esc(card["confirm_in_30_seconds"])}</p>')
        out.append(f'<p>{esc(card["instruction"])}</p>')
        acts = card["related"]["actions"]
        if acts:
            out.append('<h4>Draw one of these</h4><ul>' + "".join(
                f'<li><a href="#{esc(a)}">{esc(by_id[a]["title"])}</a></li>'
                for a in acts) + "</ul>")
    elif t == "ACTION CARD":
        out.append(f'<p>{esc(card["why_it_matters"])}</p>')
        out.append('<h4>You need</h4><ul>'
                    + "".join(f"<li>{esc(i)}</li>" for i in card["inputs"])
                    + "</ul>")
        out.append('<h4>Steps</h4><ol>'
                    + "".join(f"<li>{esc(s)}</li>" for s in card["steps"])
                    + "</ol>")
        out.append(f'<p class="kcall"><strong>Victory.</strong> '
                    f'{esc(card["victory_condition"])}</p>')
        nxt = card.get("next_card")
        if nxt and nxt in by_id:
            out.append(f'<p>Next: <a href="#{esc(nxt)}">'
                        f'{esc(by_id[nxt]["title"])}</a></p>')
    elif t == "STANDARD CARD":
        out.append(f'<p><strong>Trigger:</strong> {esc(card["trigger"])}</p>')
        out.append('<h4>Write on</h4><ul class="kwrite">'
                    + "".join(f"<li>{esc(w)}</li>" for w in card["write_on"])
                    + "</ul>")
        out.append(f'<p>{esc(card["instruction"])}</p>')
    elif t == "EVENT CARD":
        zones = card["tests_zones"]
        out.append('<p><strong>Tests:</strong> ' + ", ".join(
            esc(by_id[z]["title"]) for z in zones if z in by_id) + "</p>")
        out.append(f'<p class="kcall"><strong>It held if:</strong> '
                    f'{esc(card["held_if"])}</p>')
        out.append(f'<p><strong>If it did not:</strong> '
                    f'{esc(card["if_it_failed"])}</p>')
    return "\n".join(out)


def card_html(card: dict, by_id: dict) -> str:
    return (
        f'<article class="kcard" id="{esc(card["id"])}">'
        f'<div class="kfront">{band(card)}'
        f'{art_panel(card)}'
        f'<h3 class="ktitle">{esc(card["title"])}</h3>'
        f'<p class="ktag">{esc(card["tagline"])}</p>'
        f'{diff_html(card)}'
        f'<p class="klede">{esc(front_text(card))}</p>'
        f'</div>'
        f'<details class="kback"><summary>How it works</summary>'
        f'<div class="kbody">{back_body(card, by_id)}</div>'
        f'</details></article>'
    )


def print_tile(card: dict) -> str:
    raw, bg, fg, glyph, fam = colours(card["type"])
    return (
        f'<div class="ktile" style="--c:{raw};--bg:{bg};--fg:{fg}">'
        f'<div class="tband">{esc(fam)} · {esc(card["id"])}</div>'
        f'<div class="tglyph" aria-hidden="true">{glyph}</div>'
        f'<h4 class="ttitle">{esc(card["title"])}</h4>'
        f'<p class="ttag">{esc(card["tagline"])}</p>'
        f'<p class="tlede">{esc(short(front_text(card)))}</p>'
        f'</div>'
    )


# --------------------------------------------------------------- assembly

def build_body(deck: dict) -> str:
    cards = deck["cards"]
    by_id = {c["id"]: c for c in cards}
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
    whole = [c for c in cards if c["type"] == "ACTION CARD" and not c.get("zone")]

    parts = [f'<section class="kzone kzone-room"><h2>The Kitchen</h2>'
              f'{card_html(room, by_id)}</section>']
    for name in ZONE_ORDER:
        block = [f'<section class="kzone"><h2>{esc(name)}</h2>',
                  card_html(zmap[name], by_id)]
        block.append('<div class="ksub"><p class="keyebrow">'
                      'Three frictions, then the fix</p>')
        for c in fr.get(name, []):
            block.append(card_html(c, by_id))
        for c in ac.get(name, []):
            block.append(card_html(c, by_id))
        if name in st:
            block.append(card_html(st[name], by_id))
        block.append('</div></section>')
        parts.append("".join(block))

    parts.append('<section class="kzone"><h2>Whole kitchen</h2>'
                  '<p class="klead-p">Four cards that are not one zone’s '
                  'job: the nightly close, the safety walk to do before any '
                  'rebuild, the shopping list loop, and the conversation two '
                  'cooks need to have once.</p>'
                  + "".join(card_html(c, by_id) for c in whole)
                  + '</section>')
    parts.append('<section class="kzone"><h2>Root causes, the shared deck</h2>'
                  '<p class="klead-p">Every friction card in the kitchen '
                  'points at one of these twelve. Pull one when a friction '
                  'card sends you here.</p>'
                  + "".join(card_html(c, by_id) for c in causes)
                  + '</section>')
    parts.append('<section class="kzone"><h2>Events, the day that tests it</h2>'
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
<title>The Kitchen Deck: 72 cards, typeset and free to read or print</title>
<meta name="description" content="Seven kitchen zones, the friction each one causes, the root cause, the fix, and the standard to keep. 72 cards, typeset, free.">
<!-- SEO:BEGIN -->
<link rel="canonical" href="https://6s-success.com/kitchen-deck.html">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="6S Success">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="https://6s-success.com/kitchen-deck.html">
<meta property="og:title" content="The Kitchen Deck: 72 cards, typeset and free to read or print">
<meta property="og:description" content="Seven kitchen zones, the friction each one causes, the root cause, the fix, and the standard to keep. 72 cards, typeset, free.">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="The Kitchen Deck: 72 cards, typeset and free to read or print">
<meta name="twitter:description" content="Seven kitchen zones, the friction each one causes, the root cause, the fix, and the standard to keep. 72 cards, typeset, free.">
<meta name="theme-color" content="#22323C">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://6s-success.com/"},
    {"@type": "ListItem", "position": 2, "name": "The Kitchen Deck", "item": "https://6s-success.com/kitchen-deck.html"}
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Game",
  "@id": "https://6s-success.com/kitchen-deck.html#deck",
  "name": "The 6S Success Kitchen Deck",
  "url": "https://6s-success.com/kitchen-deck.html",
  "inLanguage": "en",
  "numberOfPlayers": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 6},
  "gameItem": {"@type": "Thing", "name": "72 printable cards, front and back, typeset, no illustrations yet"},
  "publisher": {"@id": "https://6s-success.com/#organization"},
  "genre": "Household organization",
  "abstract": "A 72 card deck for the kitchen: seven zones, the frictions each one causes, the twelve root causes underneath, the actions that fix them, and the standard each zone keeps. Typeset, free, no illustrations yet."
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
      <p class="eyebrow on-deep">The deck</p>
      <h1>The <em>Kitchen</em> Deck</h1>
      <p class="sub">72 cards: seven zones, the frictions each one causes, the twelve root causes underneath, the actions that fix them, and the standard each zone keeps. Typeset and free. No illustrations yet, so every card reads as text, not a photograph.</p>
      <div class="cta-row">
        <button class="btn btn-primary btn-lg" type="button" onclick="window.print()">Print the 72 fronts</button>
        <a class="btn btn-on-deep btn-lg" href="#kitchen-cards">Read the deck</a>
      </div>
      <p class="fulfil-note">The Entryway deck, illustrated: <a href="deck.html" style="color:inherit">deck.html</a>.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">Why unillustrated</p>
    <h2>The words are finished. The pictures are not.</h2>
    <p>__INTRO__</p>
    <p>Every card here is real: written from the same source as the Manual and the zone pages, gated so a root cause with no friction pointing at it, or an action nobody's problem needs, cannot ship. None of it is generated placeholder copy. What is missing is photography, which this deck does not pretend to have. A family-coloured panel and the card's own symbol stand where a photograph will eventually go.</p>
  </div>
</section>

<section class="section band" id="whats-in-it">
  <div class="wrap">
    <p class="eyebrow">72 cards, seven kinds</p>
    <h2>One zone, one friction, one cause, one fix, one standard</h2>
    <p class="lede">A Zone card names the place. Friction cards say what a household actually complains about there. Each friction points at a Root Cause, and each cause names the Action that fixes it. A Standard card is what you write down and keep. Event cards are the days that test whether it held.</p>
    <ul class="spine">__SPINE__</ul>
  </div>
</section>

<section class="section" id="kitchen-cards">
  <div class="wrap">
    <p class="eyebrow">The deck</p>
    <h2>Read it here, zone by zone</h2>
    <p>Tap a card's "How it works" to see its back. Start at the sink: it is the shortest zone and the one the rest of the kitchen resets from.</p>
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
      <div><h2>Company</h2><a href="about.html">About</a><a href="consulting.html">Consulting</a><a href="contact.html">Contact</a><a href="about.html#nova">Nova Consulting</a></div>
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

CSS = """
.hero .sub{max-width:46ch}
.spine{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 0;padding:0;list-style:none}
.spine li{font-size:13px;font-weight:600;padding:7px 14px;border-radius:999px;
  color:#fff;font-family:"Inter",Arial,sans-serif}
.kzone{margin:0 0 46px}
.kzone h2{font-size:22px;margin:0 0 6px}
.klead-p{color:var(--soft);margin:0 0 18px}
.ksub{margin-top:14px;padding-left:18px;border-left:3px solid var(--line)}
.keyebrow{font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.14em;
  text-transform:uppercase;color:var(--mute);margin:18px 0 10px}
.kcard{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px 12px;margin:0 0 14px;max-width:640px}
.kfront{}
.kband{display:inline-flex;align-items:center;gap:7px;font-family:var(--sans);
  font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  padding:4px 10px;border-radius:999px;margin:0 0 10px}
.kglyph{font-size:13px;line-height:1}
.kart{width:56px;height:56px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;float:right;margin:0 0 8px 12px;font-size:26px}
.ktitle{font-size:19px;margin:0 0 3px}
.ktag{font-family:var(--sans);font-size:11.5px;font-weight:600;letter-spacing:.05em;
  color:var(--mute);margin:0 0 8px;text-transform:uppercase}
.kdiff{display:block;font-size:12px;letter-spacing:2px;color:var(--terra-d);margin:0 0 8px}
.klede{margin:0;line-height:1.5}
.kback{margin-top:10px;border-top:1px solid var(--line);padding-top:8px}
.kback summary{cursor:pointer;font-family:var(--sans);font-size:13px;font-weight:600;
  color:var(--terra-d);padding:4px 0}
.kback summary:focus-visible{outline:2px solid var(--focus,#F0C674);outline-offset:2px}
.kbody{padding-top:6px;font-size:15px;line-height:1.5}
.kbody h4{font-size:13px;margin:14px 0 6px;font-family:var(--sans);
  text-transform:uppercase;letter-spacing:.08em;color:var(--mute)}
.kbody ol,.kbody ul{margin:0 0 10px;padding-left:22px}
.kbody li{margin-bottom:5px}
.kbody .ktight li{margin-bottom:2px}
.kcall{background:#FBE9C7;border:1px solid #EAD69A;border-radius:8px;
  padding:8px 12px;color:#5a4413}
.ksafety{background:#F9E4DF;border:1px solid #EFC6BC;border-radius:8px;
  padding:8px 12px;color:#7a2e1c}
.kwrite li{list-style:none;padding-left:0;font-family:var(--sans);font-size:13px;
  color:var(--soft);border-bottom:1px dashed var(--line-2);padding-bottom:6px;margin-bottom:8px}
.print-only{display:none}
@media print{
  @page{size:letter;margin:0.35in}
  body *{visibility:hidden}
  .print-only,.print-only *{visibility:visible}
  .print-only{display:block;position:absolute;left:0;top:0;width:100%}
  .ksheet{display:grid;grid-template-columns:repeat(3,2.5in);gap:0.18in;justify-content:center}
  .ktile{width:2.5in;height:3.5in;border:1px solid #ccc;border-radius:0.12in;
    box-sizing:border-box;padding:0.14in;break-inside:avoid;position:relative;
    background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;
    display:flex;flex-direction:column}
  .tband{font-family:Arial,sans-serif;font-size:7.5pt;font-weight:700;letter-spacing:.06em;
    text-transform:uppercase;color:var(--fg);background:var(--bg);border-radius:999px;
    padding:2pt 7pt;display:inline-block;align-self:flex-start}
  .tglyph{position:absolute;top:0.14in;right:0.16in;font-size:16pt;color:var(--c);opacity:.55}
  .ttitle{font-family:Georgia,serif;font-size:14pt;line-height:1.08;margin:8pt 0 3pt;
    max-width:80%}
  .ttag{font-family:Arial,sans-serif;font-size:7.5pt;font-weight:600;letter-spacing:.04em;
    text-transform:uppercase;color:#666;margin:0 0 6pt}
  .tlede{font-family:Georgia,serif;font-size:9.5pt;line-height:1.32;margin:0;color:#222}
}
"""

# Print-sheet type sizes are declared here in real CSS points, which are a
# physical unit (1pt = 1/72in) independent of screen DPI, so no px/300dpi
# conversion is needed the way ops/card_spec.py needs one for a rasterised
# PNG. They still have to clear the same floor that file enforces.
PRINT_PT = {"tband": 7.5, "ttag": 7.5, "tlede": 9.5, "ttitle": 14.0}
for _role, _size in PRINT_PT.items():
    assert _size >= S.FLOOR_PT, f"{_role} at {_size}pt is under the print floor"
del _role, _size


def main() -> int:
    deck = KD.build()
    src = json.load(io.open(KD.SRC, encoding="utf-8"))
    kitchen_intro = [r for r in src["rooms"] if r["room"] == "Kitchen"][0]["intro"]

    page = (PAGE
            .replace("__CSS__", CSS)
            .replace("__INTRO__", esc(kitchen_intro))
            .replace("__SPINE__", type_spine(deck))
            .replace("__BODY__", build_body(deck))
            .replace("__SHEET__", build_print_sheet(deck))
            .replace("__UMAMI__", UMAMI))

    io.open(OUT, "w", encoding="utf-8", newline="").write(page)

    by = {}
    for c in deck["cards"]:
        by[c["type"]] = by.get(c["type"], 0) + 1
    print(f"  kitchen deck page  {deck['count']} cards")
    for t in TYPE_COUNT_ORDER:
        print(f"    {TYPE_LABEL[t]:<10} {by.get(t, 0)}")
    print(f"  written  {os.path.relpath(OUT, ROOT)}")

    # This generator's own template carries a hardcoded fingerprint on
    # site.css/measure.js and a literal PWA block, the same issue #26 shape
    # ops/build_kit_page.py, ops/build_corporate.py and ops/build_resources.py
    # each already found and fixed for themselves: every other single-page
    # generator re-runs the whole-site wiring passes on its own output so a
    # plain rebuild cannot silently strip or stale them, and this one had
    # simply never been added to that list. Same order those three use,
    # fingerprint_assets.py last because wire_measure resets the ?v= to bare.
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
