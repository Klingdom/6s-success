#!/usr/bin/env python3
"""
Build the page that actually shows the Entryway deck.

WHY
---
The deck has 90 finished cards, front and back, and the site has never shown
one of them. deck.html described the deck in prose and offered a print and
play sheet built in HTML and CSS that ignores the artwork entirely. Somebody
deciding whether this deck is worth anything had no way to look at it.

This builds site/deck-gallery.html: every card, filterable by type, each one
flipping between its front and its back.

DESIGN NOTES
------------
The flip is a real flip rather than a swap, because these cards were designed
as two faces of one object and the back only makes sense as the back. It is
CSS only, it works on a tap, it is keyboard reachable, and it is disabled
under prefers-reduced-motion, where the two faces stack instead.

Nothing here is lazy about weight. 90 cards at full size would be 40 MB on
first paint, so the grid serves the 400px tile, loading="lazy", and the large
face is only fetched when a card is opened.

Run:  python ops/build_deck_gallery.py
"""
from __future__ import annotations

import html
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DECKS = {
    "entryway": {"room": "Entryway", "total": 90},
    "mudroom": {"room": "Mudroom", "total": 90},
}
UMAMI = ('<script defer src="/stats/script.js" '
         'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
         'data-host-url="https://6s-success.com/stats"></script>')

# The order a person meets them in, which is the order the deck teaches: what
# a zone is, what goes wrong, what fixes it, what skill it builds, what habit
# holds it, then the play layer.
ORDER = ["Micro Zone", "Problem", "Tool", "Skill", "Habit",
         "Upgrade", "Event", "Win", "Room"]

BLURB = {
    "Micro Zone": "The twelve places an entryway actually is. Each one names "
                  "what it is for, and what done looks like.",
    "Problem": "What goes wrong, and the root cause underneath it. Every "
               "problem card points at the zone that fixes it.",
    "Tool": "The small interventions. A hook, a tray, a labelled bin, used "
            "for a reason rather than bought on spec.",
    "Skill": "What you get better at. These are the transferable parts, the "
             "ones that work in the next room too.",
    "Habit": "The sustain layer. Small repeatable actions attached to "
             "something you already do.",
    "Upgrade": "What a zone becomes once the basics hold.",
    "Event": "The days that test the system. Delivery day, a rainstorm, a "
             "school morning, a new puppy.",
    "Win": "What finishing feels like, named so it counts.",
    "Room": "The card that hands off to the next room.",
}


def face(deck: str, slug: str, side: str, eager: bool = False) -> str:
    """A picture element serving webp with a jpeg fallback.

    Every tile stays lazy except the very first image on the page: that one
    is the element the browser measures for Largest Contentful Paint, and
    lazy loading it delays the page's own first card behind a scroll.
    """
    b = f"assets/cards/{deck}/{slug}-{side}"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (
        f'<picture>'
        f'<source type="image/webp" srcset="{b}-md.webp 400w, {b}-lg.webp 760w" '
        f'sizes="(max-width:640px) 46vw, (max-width:1000px) 30vw, 230px">'
        f'<img src="{b}-md.jpg" alt="" {load} decoding="async" '
        f'width="400" height="560">'
        f'</picture>')


def main() -> int:
    for deck in DECKS:
        build(deck)

    # This generator's own <head> template carries no PWA icon links and no
    # measurement script; both were wired onto the two live gallery pages by
    # wire_pwa.py/wire_measure.py directly, same as every other page on the
    # site, so a plain rerun of this file alone silently deleted both
    # (issue #26). Re-running the whole-site, idempotent wiring scripts here
    # closes that gap the same way ops/build_zone_pages.py and
    # ops/build_articles.py already do.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wire_measure
    import wire_pwa
    wire_measure.main()
    wire_pwa.main()
    return 0


def build(deck: str) -> None:
    spec = DECKS[deck]
    CARDS = os.path.join(SITE, "assets", "cards", deck)
    # The print at home PDF, linked only if the file is really on disk.
    # A download button pointing at a 404 is worse than no button, and
    # this artefact is 25 MB and generated, so it can legitimately be
    # missing from a checkout.
    pnp_file = os.path.join(SITE, "downloads",
                            "6S-Entryway-Deck-PrintAndPlay.pdf")
    if deck == "entryway" and os.path.exists(pnp_file):
        mb = os.path.getsize(pnp_file) / 1024 / 1024
        pnp = (
            '<p class="pnp"><a class="btn btn-primary" '
            'href="downloads/6S-Entryway-Deck-PrintAndPlay.pdf" '
            'download>Download the printable deck</a> '
            '<span>All 88 cards, fronts and backs, twenty sheets, '
            f'{mb:.0f} MB PDF. Print double sided at 100 percent, flip '
            'on the long edge, then cut on the marks. Free, and no '
            'email address needed.</span></p>')
    else:
        pnp = ""

    OUT = os.path.join(SITE, f"deck-gallery-{deck}.html") if deck != "entryway"         else os.path.join(SITE, "deck-gallery.html")
    idx = json.load(io.open(os.path.join(CARDS, "index.json"), encoding="utf-8"))
    cards = idx["cards"]

    by = {}
    for c in cards:
        by.setdefault(c["type"], []).append(c)

    head = io.open(os.path.join(SITE, "deck.html"), encoding="utf-8").read()
    hdr = head[head.index("<header"):head.index("</header>") + 9] \
        if "<header" in head else ""
    ftr = head[head.index("<footer"):head.index("</footer>") + 9] \
        if "<footer" in head else ""

    # A deck that is only part drawn says so. Writing "all 2 cards in the
    # deck" across a deck of 90 with 2 illustrated is the kind of small false
    # claim that costs more than the page is worth.
    total = spec.get("total", len(cards))
    if len(cards) >= total:
        lede = (f"All {len(cards)} cards in the deck. Tap any card to turn it "
                f"over: the front is what to do, the back is why it matters, "
                f"what usually goes wrong, and which card comes next.")
    else:
        lede = (f"{len(cards)} of the {total} cards in this deck are "
                f"illustrated so far. The written deck is complete and every "
                f"card has its copy; the artwork is being made a card at a "
                f"time. Tap any card to turn it over.")

    types = [t for t in ORDER if t in by] + \
            [t for t in sorted(by) if t not in ORDER]

    chips = ['<button type="button" data-t="all" aria-pressed="true">'
             f'All <span class="n">{len(cards)}</span></button>']
    for t in types:
        chips.append(f'<button type="button" data-t="{html.escape(t)}" '
                     f'aria-pressed="false">{html.escape(t)} '
                     f'<span class="n">{len(by[t])}</span></button>')

    def tile(c: dict, eager: bool = False) -> str:
        title = html.escape(c["title"])
        code = html.escape(c["code"])
        return (
            f'<li class="c" data-t="{html.escape(c["type"])}">'
            f'<button class="flip" type="button" aria-pressed="false" '
            f'aria-label="{code}, {title}. Show the back of this card.">'
            f'<span class="inner">'
            f'<span class="f">{face(deck, c["slug"], "front", eager)}</span>'
            f'<span class="b">{face(deck, c["slug"], "back")}</span>'
            f'</span></button>'
            f'<p class="cap"><b>{code}</b> {title}</p></li>')

    def group(t: str, first: bool = False) -> str:
        """A heading, its blurb, and its own grid.

        The first version emitted all nine headings and then one grid of 90,
        so every heading stacked above the deck and none of them sat with the
        cards it described.
        """
        ordered = sorted(by[t], key=lambda x: x["code"])
        rows = "".join(
            tile(c, eager=(first and i == 0)) for i, c in enumerate(ordered))
        return (f'<section class="grp" data-t="{html.escape(t)}">'
                f'<h2>{html.escape(t)} cards '
                f'<span class="cnt">{len(by[t])}</span></h2>'
                f'<p class="gb">{html.escape(BLURB.get(t, ""))}</p>'
                f'<ul class="deckgrid">{rows}</ul></section>')

    sections = "".join(group(t, first=(i == 0)) for i, t in enumerate(types))

    meta_count = (f"All {len(cards)}" if len(cards) >= total
                  else f"{len(cards)} of {total}")

    # Only the Entryway deck has a real print-at-home PDF today. Naming it
    # from another deck's gallery page told a mudroom visitor, honestly 2 of
    # 90 cards in, to go print an Entryway deck they never asked for.
    printable = (' and the <a href="downloads/6S-Entryway-Deck-PrintAndPlay.pdf">'
                 'print and play PDF</a> is free' if deck == "entryway" else "")

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Every card in the {spec["room"]} deck | 6S Success</title>
<meta name="description" content="{meta_count} cards in the 6S Success \
{spec["room"]} deck, front and back. Micro zones, problems, tools, skills, \
habits and the play layer that ties them together.">
<link rel="canonical" href="https://6s-success.com/{os.path.basename(OUT)}">
<link rel="stylesheet" href="assets/css/site.css">
<style>
.chips{{display:flex;flex-wrap:wrap;gap:9px;margin:0 0 30px}}
.chips button{{font-family:var(--sans);font-size:13.5px;font-weight:600;
  color:var(--soft);background:var(--panel);border:1px solid var(--line);
  border-radius:99px;padding:8px 14px;cursor:pointer}}
.chips button[aria-pressed="true"]{{background:var(--ink);color:var(--paper);
  border-color:var(--ink)}}
.chips .n{{opacity:.55;font-variant-numeric:tabular-nums;margin-left:3px}}
.grp h2{{margin:44px 0 4px;font-size:22px}}
.grp .cnt{{font-family:var(--sans);font-size:14px;color:var(--soft);
  font-weight:600;vertical-align:3px;margin-left:6px}}
.gb{{margin:0 0 20px;color:var(--soft);max-width:62ch;font-size:15.5px}}
.pnp{{margin:24px 0 0;display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px}}
.pnp span{{font-family:var(--sans);font-size:14px;line-height:1.5;color:var(--soft);max-width:44ch}}
.deckgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));
  gap:22px 18px;list-style:none;padding:0;margin:0}}
.c{{margin:0}}
.flip{{all:unset;display:block;width:100%;aspect-ratio:2.5/3.5;cursor:pointer;
  perspective:1200px;border-radius:12px}}
.flip:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}
.inner{{position:relative;display:block;width:100%;height:100%;
  transition:transform .55s cubic-bezier(.2,.7,.3,1);transform-style:preserve-3d}}
.flip[aria-pressed="true"] .inner{{transform:rotateY(180deg)}}
.f,.b{{position:absolute;inset:0;backface-visibility:hidden;
  border-radius:12px;overflow:hidden;box-shadow:0 2px 10px #2b26221f}}
.b{{transform:rotateY(180deg)}}
/* contain, never cover. The source sheets are not all one shape: 63 are
   1536x1024 and 18 are 1402x1122, so their faces land at 0.71 and 0.61 wide
   for tall. Cover cropped the narrower ones top and bottom, which took the
   header bar off EM-001 and would have quietly trimmed content from every
   card in that group. A little letterboxing is the honest trade. */
.f img,.b img,.f picture,.b picture{{display:block;width:100%;height:100%;
  object-fit:contain;background:var(--panel)}}
.cap{{margin:9px 2px 0;font-family:var(--sans);font-size:12.5px;
  line-height:1.4;color:var(--soft)}}
.cap b{{color:var(--ink);font-variant-numeric:tabular-nums}}
@media (prefers-reduced-motion:reduce){{
  .inner{{transition:none;transform:none!important;transform-style:flat}}
  .f,.b{{position:relative;backface-visibility:visible;transform:none}}
  .flip{{aspect-ratio:auto;perspective:none}}
  .b{{margin-top:10px}}
}}
</style>
{UMAMI}
</head>
<body>
{hdr}
<main>
<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">The {spec["room"]} deck</p>
    <h1>Every card, front and back</h1>
    <p class="lede">{lede}</p>
    <p style="color:var(--soft)">The deck is one room. The method behind it
    covers <a href="zones/">114 micro zones across twenty rooms</a>{printable}.</p>
    {pnp}
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="chips" role="group" aria-label="Filter cards by type">
      {"".join(chips)}
    </div>
    <div id="grid">{sections}</div>
  </div>
</section>
</main>
{ftr}
<script>
(function () {{
  var grid = document.getElementById("grid");
  var chips = [].slice.call(document.querySelectorAll(".chips button"));
  var groups = [].slice.call(document.querySelectorAll(".grp"));

  /* A card turns over rather than swapping pictures, because the two faces
     were designed as two sides of one object. aria-pressed carries the state
     so a screen reader knows which face is showing. */
  grid.addEventListener("click", function (e) {{
    var b = e.target.closest(".flip");
    if (!b) {{ return; }}
    var on = b.getAttribute("aria-pressed") === "true";
    b.setAttribute("aria-pressed", on ? "false" : "true");
    b.setAttribute("aria-label", b.getAttribute("aria-label")
      .replace(on ? "Show the front" : "Show the back",
               on ? "Show the back" : "Show the front"));
  }});

  /* Filtering hides whole groups, so a heading never survives its cards. */
  function show(t) {{
    groups.forEach(function (g) {{ g.hidden = t !== "all" && g.dataset.t !== t; }});
    chips.forEach(function (b) {{
      b.setAttribute("aria-pressed", b.dataset.t === t ? "true" : "false");
    }});
  }}
  chips.forEach(function (b) {{
      b.setAttribute("aria-pressed", b.dataset.t === t ? "true" : "false");
    }});
  }}
  chips.forEach(function (b) {{
    b.addEventListener("click", function () {{ show(b.dataset.t); }});
  }});
}})();
</script>
</body>
</html>
"""
    io.open(OUT, "w", encoding="utf-8", newline="").write(doc)

    assert doc.count("<picture>") == len(cards) * 2, "a face is missing"
    assert doc.count('class="deckgrid"') == len(types), (
        "each type needs its own grid, or headings stack above the deck")
    missing = []
    for c in cards:
        for side in ("front", "back"):
            for f in (f"{c['slug']}-{side}-md.jpg", f"{c['slug']}-{side}-md.webp",
                      f"{c['slug']}-{side}-lg.webp"):
                if not os.path.exists(os.path.join(CARDS, f)):
                    missing.append(f)
    assert not missing, f"page references {len(missing)} files that do not exist: {missing[:3]}"

    print(f"  wrote site/{os.path.basename(OUT)}")
    print(f"  {len(cards)} cards, {len(cards)*2} faces, {len(types)} types")
    print(f"  every referenced image file exists")
    for t in types:
        print(f"    {t:12} {len(by[t])}")
    return


if __name__ == "__main__":
    raise SystemExit(main())
