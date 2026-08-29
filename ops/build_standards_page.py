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

# Read live from data.js rather than typed here: a hardcoded copy of this
# link went stale after the 2026-08-27 Stripe sync retired the original
# payment links, and nothing caught it because no gate reads .js files for
# dead links. Reading the one place Stripe sync actually writes to means
# this cannot go stale again the same way.
def _live_buy(sku):
    src = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                  encoding="utf-8").read()
    catalog = json.loads(src[src.index("["):src.rindex("]") + 1])
    for p in catalog:
        if p.get("sku") == sku:
            return p["buy"]
    raise KeyError(f"{sku} not in data.js")


PACK_BUY = _live_buy("PACK-HOUSE")


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

    # The hero shows a real sheet, so its text is read from content.json rather
    # than typed in. A hand written hero is a second copy of the product that
    # nobody rebuilds, and the first paraphrase in it makes the page a liar
    # about what the buyer gets.
    ent = next(r for r in rooms if r["room"] == "Entryway")
    hero_zones = ent["zones"][:2]

    def clip(t: str, n: int) -> str:
        """Shorten to fit the card without inventing a sentence.

        Cutting at a word and adding a full stop produced 'keys never ride out
        of the.', which reads as a typo in the product rather than as a
        preview of it. So: keep the whole thing if it fits, otherwise end at a
        real sentence boundary, and only if there is no boundary fall back to a
        word cut marked with an ellipsis, which does not claim the sentence
        ended there.
        """
        t = " ".join(str(t or "").split())
        if len(t) <= n:
            return t
        cut = t[:n + 12]
        end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
        if end > n * 0.45:
            return cut[:end + 1]
        return t[:n].rsplit(" ", 1)[0].rstrip(" ,.;:") + " ..."

    hero_rows = "".join(
        '<p style="font-family:var(--sans);font-size:9px;font-weight:700;'
        'letter-spacing:.09em;text-transform:uppercase;color:#6E8B5B;'
        'margin:0 0 4px">' + esc(z["zone"]) + '</p>'
        '<p style="font-size:12.5px;line-height:1.4;color:#2B2622;margin:0 0 6px">'
        + esc(clip(z["leave_behind"]["standard"], 140)) + '</p>'
        '<p style="font-size:10.5px;line-height:1.4;color:#584f46;margin:0 0 14px;'
        'padding-left:8px;border-left:2px solid #DDA63A">'
        + esc(clip(z["leave_behind"]["trigger"], 96)) + '</p>'
        for z in hero_zones)
    hero_count = sum(1 for z in ent["zones"]
                     if (z.get("leave_behind") or {}).get("standard"))

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
      <p class="sub">You can sort a room in an afternoon. Keeping it that way is
      a different job, and it is the one almost every organising system skips.
      This is twenty sheets, one per room, naming what each micro zone holds to
      and the everyday moment that brings it back.</p>
      <div class="cta-row">
        <a class="btn btn-on-deep btn-lg" href="downloads/6S-Standards-Pack.html">Open all twenty sheets</a>
      </div>
      <p style="color:#C9BFA9;font-size:14px;margin-top:14px">Opens in your
      browser. Print from there, or save it as a PDF. No email, no account.</p>
    </div>
    <div class="hero-art">
      <!-- The hero of a page selling a printed sheet should be the printed
           sheet. Real text from the entryway sheet, not a placeholder. -->
      <div style="background:#FBF7EF;border-top:5px solid #6E8B5B;border-radius:3px;
        padding:26px 24px 18px;max-width:340px;width:100%;
        box-shadow:0 22px 48px rgba(0,0,0,.34);transform:rotate(-1.4deg)">
        <div style="display:flex;justify-content:space-between;align-items:baseline;
          border-bottom:1px solid #E2D8C4;padding-bottom:8px;margin-bottom:12px">
          <strong style="font-family:var(--display);font-size:20px;color:#2B2622;
            letter-spacing:-.015em">{esc(ent["room"])}</strong>
          <span style="font-family:var(--sans);font-size:8.5px;font-weight:700;
            letter-spacing:.12em;text-transform:uppercase;color:#8C8478">{hero_count} zones</span>
        </div>
        {hero_rows}
        <div style="display:flex;gap:14px;align-items:flex-end;padding-top:11px;
          border-top:1px solid #E2D8C4;font-family:var(--sans);font-size:8px;
          font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#8C8478">
          <span>Agreed</span><i style="flex:1;border-bottom:1px solid #C9BFA9;height:12px"></i>
          <span>Date</span><i style="flex:.6;border-bottom:1px solid #C9BFA9;height:12px"></i>
        </div>
      </div>
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
<link rel="stylesheet" href="assets/css/site.css">
<script defer src="/stats/script.js" data-website-id="ANALYTICS-ID"></script>
</head>
<body>
{header}
{body}
<!-- SIGNUP:BEGIN -->
<!-- Signup withdrawn 2026-08-23: this Listmonk instance sends its
     opt-in confirmation from "Compassion Benchmark", a different business
     sharing the same host. A visitor who signed up here received mail from
     a company they have never heard of. Restore ops/wire_signup.py once the
     sending identity is per brand. -->
<!-- SIGNUP:END -->
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

    # Everything the hero shows must be in the pack. This is the check that
    # would have caught the shoe zone line, which was written from memory of a
    # deck card and said "two pairs" nowhere the source did.
    flat = " ".join(html.split())
    for z in hero_zones:
        for f in ("standard", "trigger"):
            q = clip(z["leave_behind"][f], 140 if f == "standard" else 96)
            assert esc(q) in flat,                 f"the hero quotes {z['zone']} {f} in words content.json does not use"
    print(f"  hero quotes {len(hero_zones)} zones, all verbatim from content.json")
    print("  claims checked: the download exists, analytics wired, "
          "one paid path present")

    # This generator's own <head> template carries no PWA icon links; the
    # footer's MEASURE block survives only because shell() copies it verbatim
    # from deck.html, but the PWA block sits in deck.html's <head>, outside
    # what shell() extracts, so a plain rebuild silently dropped it (issue
    # #26). Re-running the whole-site, idempotent wiring scripts here closes
    # that gap the same way ops/build_articles.py and
    # ops/build_deck_gallery.py already do.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wire_measure
    import wire_pwa
    wire_measure.main()
    wire_pwa.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
