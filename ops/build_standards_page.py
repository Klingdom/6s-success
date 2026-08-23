#!/usr/bin/env python3
"""
Build site/standards.html, the free Standards Pack page.

WHY A GENERATOR AND NOT A HAND WRITTEN PAGE
-------------------------------------------
The site header and footer appear on 166 pages and change together. A page
hand copied from a sibling drifts the first time the nav changes, and the drift
is invisible because nothing renders the difference. This lifts the shell from
deck.html at build time, so the two can only ever agree.

The room list is read from the same content.json the pack itself is built from,
so the page cannot advertise a room the pack does not contain.

Run:  python ops/build_standards_page.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
SHELL = os.path.join(SITE, "deck.html")
OUT = os.path.join(SITE, "standards.html")

TITLE = "The Standards Pack: one page per room, free to print"
DESC = ("Twenty sheets, one per room, naming the standard each micro zone holds "
        "to and the everyday moment that triggers the reset. Free to print.")
IMG = "https://6s-success.com/assets/img/rhythm.jpg"
ALT = "A printed room standard posted inside a cupboard door"

PACK_BUY = "https://buy.stripe.com/9B66oAgYedoC4ZA6VW0kE04"


def esc(t) -> str:
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shell() -> tuple[str, str]:
    """The header and footer every page on this site shares."""
    s = io.open(SHELL, encoding="utf-8").read()
    head = s[s.index("<header class=\"site-header\">"):s.index("</header>") + 9]
    foot = s[s.index("<footer class=\"site-footer\">"):s.index("</body>")]
    return head, foot


def main() -> int:
    d = json.load(io.open(SRC, encoding="utf-8"))
    rooms = [r for r in d["rooms"]
             if any((z.get("leave_behind") or {}).get("standard") for z in r["zones"])]
    zones = sum(1 for r in rooms for z in r["zones"]
                if (z.get("leave_behind") or {}).get("standard"))

    header, footer = shell()

    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "@id": "https://6s-success.com/standards.html#pack",
        "name": "The 6S Success Standards Pack",
        "description": DESC,
        "image": IMG,
        "brand": {"@type": "Brand", "name": "6S Success"},
        "url": "https://6s-success.com/standards.html",
        "offers": {"@type": "Offer", "price": "0.00", "priceCurrency": "USD",
                   "availability": "https://schema.org/InStock",
                   "url": "https://6s-success.com/standards.html"},
    }, indent=1)

    crumbs = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": "https://6s-success.com/"},
            {"@type": "ListItem", "position": 2, "name": "The Standards Pack",
             "item": "https://6s-success.com/standards.html"}],
    }, indent=1)

    room_list = "".join(
        '<li><strong>' + esc(r["room"]) + '.</strong> '
        + str(sum(1 for z in r["zones"]
                  if (z.get("leave_behind") or {}).get("standard")))
        + " micro zones.</li>"
        for r in rooms)

    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-copy">
      <p class="eyebrow on-deep">Free to print</p>
      <h1>The standard is the part that stays</h1>
      <p class="lede">You can sort a room in an afternoon. Keeping it that way is
      a different job, and it is the one almost every organising system skips.
      This is twenty sheets, one per room, naming what each micro zone holds to
      and the everyday moment that brings it back.</p>
      <div class="cta-row">
        <a class="btn btn-on-deep btn-lg" href="downloads/6S-Standards-Pack.html">Open all twenty sheets</a>
      </div>
      <p style="color:#C9BFA9;font-size:14px;margin-top:14px">Opens in your
      browser. Print from there, or save it as a PDF. No email, no account.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <h2>A book tells you what to do. A standard tells you when you are done.</h2>
    <p>Every reset ends the same way: the room looks right, and nobody has
    written down what right was. Six weeks later the room has drifted and there
    is nothing to compare it against, so the whole job gets done again from the
    beginning.</p>
    <p>A standard is one sentence describing the finished state, checkable at a
    glance. It is not a rule and not a chore chart. It is the answer to the only
    question that matters when you walk in: is this zone right, or not?</p>
  </div>
</section>

<section class="section band">
  <div class="wrap">
    <p class="eyebrow">What is on a sheet</p>
    <h2>Three things, and one of them is a signature</h2>
    <div class="grid g-3">
      <div class="card">
        <h3>The standard</h3>
        <p>What the zone looks like when it is right, in one sentence. A
        description of a finished state, not an instruction.</p>
      </div>
      <div class="card">
        <h3>The trigger</h3>
        <p>The everyday moment that starts the reset. Coming home from the
        pharmacy. Putting the broom away. A standard attached to a moment
        survives. A standard attached to good intentions does not.</p>
      </div>
      <div class="card">
        <h3>Two signatures</h3>
        <p>A standard nobody agreed to is one person's preference, and the
        household will treat it as one. Those two lines matter more than the
        wording above them.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">Where it goes</p>
    <h2>On the door, not in a drawer</h2>
    <p>Inside the cupboard door. On the back of the pantry door. Above the bench
    where the work actually happens. A standard filed away is not a standard, and
    a standard on the fridge for a room upstairs gets read exactly once.</p>
    <p>Rewrite any line that stops being true. A standard that is quietly broken
    every week is a bad standard, and the room is telling you so. That is the
    point of the pen line, not a failure of it.</p>
  </div>
</section>

<section class="section band">
  <div class="wrap">
    <p class="eyebrow">Twenty sheets</p>
    <h2>Every room, {zones} micro zones</h2>
    <ul class="cols" style="columns:2;column-gap:44px;line-height:1.9">{room_list}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">What comes next</p>
    <h2>These sheets hold the work. They do not do it.</h2>
    <p>A standard says what right looks like. It does not tell you how to get
    there from a room that is currently wrong. That is the Whole House Print
    Pack: the same {zones} micro zones taken through all six passes, 684 cards
    you print nine to a page and carry into the room while you work.</p>
    <p>Sort, Straighten, Shine, Safety, Standardize, Sustain, one card at a time.
    Safety is the fourth S, not an afterthought at the end.</p>
    <div class="cta-row" style="margin-top:20px">
      <a class="btn btn-primary btn-lg" href="{PACK_BUY}" rel="noopener">The Print Pack, $19</a>
      <a class="btn btn-ghost btn-lg" href="deck.html">The free Entryway deck</a>
    </div>
    <p style="color:#584f46;font-size:14px;margin-top:14px">The Print Pack is
    emailed within the hour. These sheets stay free either way.</p>
  </div>
</section>
"""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(TITLE)}</title>
<meta name="description" content="{esc(DESC)}">
<!-- SEO:BEGIN -->
<link rel="canonical" href="https://6s-success.com/standards.html">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="product">
<meta property="og:site_name" content="6S Success">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="https://6s-success.com/standards.html">
<meta property="og:title" content="{esc(TITLE)}">
<meta property="og:description" content="{esc(DESC)}">
<meta property="og:image" content="{IMG}">
<meta property="og:image:alt" content="{esc(ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(TITLE)}">
<meta name="twitter:description" content="{esc(DESC)}">
<meta name="twitter:image" content="{IMG}">
<meta name="twitter:image:alt" content="{esc(ALT)}">
<meta name="theme-color" content="#22323C">
<script type="application/ld+json">
{crumbs}
</script>
<script type="application/ld+json">
{ld}
</script>
<!-- SEO:END -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
<script defer src="/stats/script.js" data-website-id="ANALYTICS-ID"></script>
</head>
<body>
{header}
{body}
{footer}
<script src="assets/js/data.js"></script>
<script src="assets/js/site.js"></script>
</body>
</html>
"""

    io.open(OUT, "w", encoding="utf-8", newline="").write(html)

    # The analytics id is a placeholder in this file only if the rest of the
    # site uses one too. Match whatever the siblings do rather than inventing.
    sib = io.open(SHELL, encoding="utf-8").read()
    m = re.search(r'data-website-id="([^"]+)"', sib)
    if m and m.group(1) != "ANALYTICS-ID":
        html = html.replace("ANALYTICS-ID", m.group(1))
        io.open(OUT, "w", encoding="utf-8", newline="").write(html)

    print(f"  site/standards.html  {len(html.encode()) // 1024} KB, "
          f"{len(rooms)} rooms, {zones} zones listed")

    # The page must not promise a file that is not there.
    dl = os.path.join(SITE, "downloads", "6S-Standards-Pack.html")
    assert os.path.exists(dl), "the page links a download that has not been copied in"
    assert "buy.stripe.com" in html, "the free page has no path to anything paid"
    assert 'data-website-id="ANALYTICS-ID"' not in html, "analytics id not filled in"
    print("  claims checked: the download exists, analytics wired, "
          "one paid path present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
