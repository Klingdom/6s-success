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
# TWO COUNTINGS, AND WHICH ONE EVERY NUMBER ON THIS PAGE USES.
#
# The Entryway deck is 89 written cards. One of them, ER-001, is the Room
# card: the single card that names the room and hands off to the next one.
# The catalogue and deck.html quote 88, which is 89 with the Room card left
# out, because you buy a room's worth of zone cards, not the divider.
#
# Both numbers are true and they are one card apart, which is exactly how a
# page ends up saying "72 of 88" when 72 already includes the Room card and
# so is being compared against the wrong total. That off-by-one was live on
# both this page and deck.html.
#
# The rule here: "written" is the whole deck, Room card included, and every
# count of illustrated cards is counted the same way. If a number appears in
# prose it says which counting it used.
DECKS = {
    "entryway": {"room": "Entryway", "written": 89, "with_room_card": True},
    "mudroom": {"room": "Mudroom", "written": 90, "with_room_card": True},
}

# Art defects found by looking at the shipped files, not at their filenames.
# A card listed here is still shown, because hiding two of the twelve micro
# zones would misrepresent the deck more than the defect does, but it carries
# a plain note so nobody meets the fault as a surprise. A fake QR code in
# particular is the kind of thing somebody points a phone at.
#
# Remove an entry the moment its art is redrawn. Nothing else reads this.
ART_DEFECTS = {
    "EM-005": "The strip along the bottom of this card front is unreadable: "
              "the words are nonsense and the square block beside them looks "
              "like a QR code but is not one and will not scan. Everything "
              "above that strip is correct. Redraw queued.",
    "EM-006": "Same fault as EM-005 along the bottom of the front: nonsense "
              "words and a decorative block that imitates a scannable code. "
              "The card above it is correct. Redraw queued.",
}
UMAMI = ('<script defer src="/stats/script.js" '
         'data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" '
         'data-host-url="https://6s-success.com/stats"></script>')

# The order a person meets them in, which is the order the deck teaches: what
# a zone is, what goes wrong, what fixes it, what skill it builds, what habit
# holds it, then the play layer.
_SIZES: dict = {}

ORDER = ["Micro Zone", "Problem", "Tool", "Skill", "Habit",
         "Upgrade", "Event", "Win", "Room"]

# {room} and {zones} are filled in per deck. The Micro Zone line used to be
# hardcoded to "the twelve places an entryway actually is", which the Mudroom
# gallery printed verbatim above a mudroom card.
BLURB = {
    "Micro Zone": "The {zones} places {room} actually is. Each one names "
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
    # The real intrinsic size, read off the file. Every face was declared
    # 400x560 and not one of them is: the scanned sheets run from 400x536 to
    # 400x657, so the browser was told the wrong shape for all 144 of them.
    # It happens not to shift the layout, because .flip pins the tile to
    # 2.5/3.5 and the image is object-fit:contain inside it, but a width and
    # height attribute is a statement about the file and this one was false.
    w, h = _face_size(deck, f"{slug}-{side}-md.jpg")
    return (
        f'<picture>'
        f'<source type="image/webp" srcset="{b}-md.webp 400w, {b}-lg.webp 760w" '
        f'sizes="(max-width:640px) 46vw, (max-width:1000px) 30vw, 230px">'
        f'<img src="{b}-md.jpg" alt="" {load} decoding="async" '
        f'width="{w}" height="{h}">'
        f'</picture>')


def _jpeg_size(path: str) -> tuple[int, int]:
    """Width and height read straight out of the JPEG's own SOF marker.

    Stdlib only, on purpose: ops/requirements.txt is deliberately Pillow-free
    (its own header explains why: it installs inside publish-image.yml and
    fulfil-orders.yml, both of which hold live secrets, and an unpinned
    imaging library is review surface next to a Stripe key nobody asked for).
    gate_icons_current and build_social_pins.py already solved the same
    problem for PNG with a stdlib IHDR read; this is the JPEG sibling.

    A first version of this function called PIL.Image.open() instead, which
    works on any machine that happens to have Pillow installed and silently
    falls back to a wrong constant on any machine that does not, this
    sandbox and CI's publish-image.yml both included. gate_generator_ownership
    caught it: regenerating without Pillow replaced all 148 real, distinct
    per-card heights (400x536 to 400x657, committed by a machine that did
    have Pillow) with a single wrong 400x560 on every card, invisible in a
    line-level diff because every card sits on the same physical line.
    """
    with io.open(path, "rb") as f:
        data = f.read()
    if data[0:2] != b"\xff\xd8":
        raise ValueError("not a JPEG: %s" % path)
    i, n = 2, len(data)
    no_length = {0xD8, 0xD9, 0x01} | set(range(0xD0, 0xD8))
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
           0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while i < n - 1:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker == 0xFF:
            i -= 1  # padding byte before the real marker
            continue
        if marker in no_length:
            continue
        seg_len = (data[i] << 8) | data[i + 1]
        if marker in sof:
            height = (data[i + 3] << 8) | data[i + 4]
            width = (data[i + 5] << 8) | data[i + 6]
            return width, height
        i += seg_len
    raise ValueError("no SOF marker: %s" % path)


def _face_size(deck: str, fname: str) -> tuple[int, int]:
    """Intrinsic size of one card face, cached.

    Falls back to the old 400x560 if the file cannot be read or is not a
    JPEG this parser understands, because a wrong dimension is a smaller
    problem than a generator that will not run.
    """
    key = (deck, fname)
    if key in _SIZES:
        return _SIZES[key]
    wh = (400, 560)
    try:
        wh = _jpeg_size(os.path.join(SITE, "assets", "cards", deck, fname))
    except Exception:
        pass
    _SIZES[key] = wh
    return wh


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
    import canonical_links
    import prune_catalog_js
    import wire_landmarks
    import wire_progressive
    import wire_measure
    import wire_pwa
    import wire_aria_current
    import build_avif
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
    # Every generator writes .html internal links, so
    # without this a rebuild reintroduces all 2,704 links
    # to addresses the site's own canonicals disown.
    canonical_links.main()
    prune_catalog_js.main()
    wire_landmarks.main()
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()
    # Must be last of the page passes. Every generator above copies
    # its header from resources.html, which marks itself as the
    # Rooms page, so without this a rebuild leaves 135 zone and room
    # pages each claiming to be Rooms to a screen reader.
    wire_aria_current.main()
    # After the nav mark, because it rewrites <source> tags inside the
    # page body. Without this a rebuild strips every AVIF source and
    # the ownership gate reports drift, which is exactly what failed
    # CI eleven times on 2026-09-01: the wiring pass existed and was
    # never chained, so the generator and the repository disagreed.
    build_avif.wire()
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
            '<span>Twenty sheets, nine cards to a sheet, fronts and '
            f'backs, {mb:.0f} MB PDF. Print double sided at 100 percent, flip '
            'on the long edge, then cut on the marks. Free, and no '
            'email address needed.</span></p>')
    else:
        pnp = ""

    OUT = os.path.join(SITE, f"deck-gallery-{deck}.html") if deck != "entryway"         else os.path.join(SITE, "deck-gallery.html")
    idx = json.load(io.open(os.path.join(CARDS, "index.json"), encoding="utf-8"))
    cards = idx["cards"]

    # THE WRITTEN DECK, WHICH IS NOT THE SAME LIST AS THE DRAWN ONE.
    #
    # index.json describes the artwork that exists. build/<deck>-cardtext.json
    # is the deck itself: every card that has been written, drawn or not. Two
    # things on this page can only be answered from the second file.
    #
    #   1. How many micro zones the room has. The page was reporting the count
    #      of micro zone cards that happen to have art, which is 10, and
    #      calling it the number of micro zones in an entryway. There are 12.
    #      Two of them are simply not drawn yet.
    #   2. What a card is called. split_deck_cards.py builds the title by
    #      dropping the first three slug segments, which works for
    #      EM-005-Entryway-Shoe-Zone and leaves nothing for ER-001-Entryway,
    #      so the Room card fell back to its own slug and the gallery
    #      published a caption reading "ER-001 ER-001-Entryway".
    #
    # Missing file is not fatal: this is a fallback to what index.json says,
    # which is what the page did before.
    # Two files can describe the deck and they mean different things.
    # <deck>-cardtext.json is the finished copy: objective, callouts, the six
    # S lesson, the back of the card. <deck>-cards.json is the outline: one
    # canonical line per card, "Audit status: Audit pending". Saying "written
    # in full" over the second one would be a claim about work that has not
    # been done, so the page says which it has.
    written_cards, full_copy = {}, False
    try:
        raw = json.load(io.open(
            os.path.join(ROOT, "build", f"{deck}-cardtext.json"),
            encoding="utf-8"))["cards"]
        written_cards = raw if isinstance(raw, dict) else {c["id"]: c for c in raw}
        full_copy = True
    except Exception:
        try:
            raw = json.load(io.open(
                os.path.join(ROOT, "build", f"{deck}-cards.json"),
                encoding="utf-8"))
            written_cards = {c["ID"]: {"title": c.get("Card", ""),
                                       "type": c.get("Category", "")}
                             for c in raw}
        except Exception:
            written_cards = {}

    for c in cards:
        # Only repair a title that is plainly the slug wearing a title's
        # clothes. Everything else keeps the casing the gallery already had.
        if c["title"] == c["slug"] or c["title"].startswith(c["code"]):
            w = written_cards.get(c["code"])
            if w and w.get("title"):
                c["title"] = w["title"].title()

    by = {}
    for c in cards:
        by.setdefault(c["type"], []).append(c)

    head = io.open(os.path.join(SITE, "deck.html"), encoding="utf-8").read()
    hdr = head[head.index("<header"):head.index("</header>") + 9] \
        if "<header" in head else ""
    ftr = head[head.index("<footer"):head.index("</footer>") + 9] \
        if "<footer" in head else ""

    # A deck that is only part drawn says so, and says it against the right
    # total. See the note on DECKS: "written" counts the Room card, so the
    # illustrated count must too, or the page reports one card fewer missing
    # than there are.
    written = spec.get("written", len(cards))
    drawn = len(cards)
    short = written - drawn
    minus_room = written - 1 if spec.get("with_room_card") else written
    # How many cards of each type the deck actually has, drawn or not. The
    # written files spell the types differently from index.json ("MICRO ZONE
    # CARD", "WIN / REWARD CARD"), so match on the gallery's own type names
    # rather than trying to normalise theirs.
    written_by = {}
    for w in written_cards.values():
        wt = str(w.get("type", "")).upper()
        for t in ORDER:
            if wt.startswith(t.upper()) or (t == "Win" and wt.startswith("WIN")):
                written_by[t] = written_by.get(t, 0) + 1
                break

    # Micro zones the room has, from the written deck, not from how many of
    # them happen to be illustrated.
    zones = sum(1 for w in written_cards.values()
                if str(w.get("type", "")).upper().startswith("MICRO ZONE"))         or len(by.get("Micro Zone", []))

    state = ("written in full and waiting on their artwork" if full_copy
             else "named and outlined, and neither written out nor drawn yet")
    if short <= 0:
        lede = (f"All {drawn} cards, front and back. Tap any card to turn it "
                f"over.")
    else:
        lede = (f"{drawn} of the deck's {written} cards are drawn and shown "
                f"here, front and back. The other {short} are {state}. "
                f"Tap any card to turn it over.")

    # The counting, said once, plainly, where somebody comparing this page
    # against the shop can see why the two numbers differ. Only the Entryway
    # deck is in the catalogue, so only the Entryway page can say what the
    # catalogue calls it without inventing a listing.
    counting = (f"Counted whole, the deck is {written} cards including the "
                f"single Room card that names the room.")
    if deck == "entryway":
        counting += (f" The catalogue and the deck page quote {minus_room}, "
                     f"which is the same deck with that one divider left out.")
    counting += " Every count on this page is the whole-deck one."

    types = [t for t in ORDER if t in by] + \
            [t for t in sorted(by) if t not in ORDER]

    chips = ['<button type="button" data-t="all" aria-pressed="true">'
             f'All <span class="n">{len(cards)}</span></button>']
    for t in types:
        chips.append(f'<button type="button" data-t="{html.escape(t)}" '
                     f'aria-pressed="false">{html.escape(t)} '
                     f'<span class="n">{len(by[t])}</span></button>')

    def tile(c: dict, eager: bool = False) -> str:
        """One card, both faces, and whatever is true about its artwork.

        The two <img> elements carry alt="" on purpose. They sit inside a
        button that already names the card, its type and which face is
        showing, so alt text here would make a screen reader read the same
        card twice and still not describe the picture. What it must never do
        is repeat the title as though that were a description of the image.
        """
        title = html.escape(c["title"])
        code = html.escape(c["code"])
        kind = html.escape(c["type"])
        note = ART_DEFECTS.get(c["code"], "")
        flag = (f'<p class="cap note">Known artwork fault: {html.escape(note)}</p>'
                if note else "")
        return (
            f'<li class="c" data-t="{kind}">'
            f'<button class="flip" type="button" aria-pressed="false" '
            f'aria-label="{kind} card {code}, {title}. '
            f'Front is showing. Turn it over.">'
            f'<span class="inner">'
            f'<span class="f">{face(deck, c["slug"], "front", eager)}</span>'
            f'<span class="b">{face(deck, c["slug"], "back")}</span>'
            f'</span>'
            f'<span class="turn" aria-hidden="true">Turn over</span>'
            f'</button>'
            f'<p class="cap"><b>{code}</b> {title}</p>{flag}</li>')

    WORDS = {1: "one", 2: "two", 6: "six", 8: "eight", 9: "nine", 10: "ten",
             11: "eleven", 12: "twelve"}

    def blurb(t: str) -> str:
        room = spec["room"].lower()
        # "a entryway" shipped on the live page. One rule, not a list.
        art = "an" if room[:1] in "aeiou" else "a"
        return BLURB.get(t, "").format(
            room=f"{art} {room}", zones=WORDS.get(zones, str(zones)))

    def group(t: str, first: bool = False) -> str:
        """A heading, its blurb, and its own grid.

        The first version emitted all nine headings and then one grid of 90,
        so every heading stacked above the deck and none of them sat with the
        cards it described.
        """
        ordered = sorted(by[t], key=lambda x: x["code"])
        rows = "".join(
            tile(c, eager=(first and i == 0)) for i, c in enumerate(ordered))
        # "Micro Zone cards 10" above a line reading "the twelve places an
        # entryway actually is" reads as a contradiction, and only one of the
        # two numbers is about artwork. Say both, and say which is which,
        # rather than picking one and leaving the reader to reconcile them.
        n_drawn, n_written = len(by[t]), written_by.get(t, len(by[t]))
        cnt = (str(n_drawn) if n_drawn >= n_written
               else f"{n_drawn} of {n_written} drawn")
        return (f'<section class="grp" data-t="{html.escape(t)}">'
                f'<h2>{html.escape(t)} cards '
                f'<span class="cnt">{cnt}</span></h2>'
                f'<p class="gb">{html.escape(blurb(t))}</p>'
                f'<ul class="deckgrid">{rows}</ul></section>')

    sections = "".join(group(t, first=(i == 0)) for i, t in enumerate(types))

    meta_count = (f"All {drawn}" if short <= 0 else f"{drawn} of {written}")

    # Only the Entryway deck has a real print-at-home PDF today. Naming it
    # from another deck's gallery page told a mudroom visitor, honestly 2 of
    # 90 cards in, to go print an Entryway deck they never asked for.
    printable = (' and the <a href="downloads/6S-Entryway-Deck-PrintAndPlay.pdf">'
                 'print and play PDF</a> is free' if deck == "entryway" else "")

    # WHAT A CARD IS, ON THE PAGE THAT SHOWS THE CARDS.
    #
    # This page was a grid of pictures with nine headings. Somebody arriving
    # on it cold could see that a deck existed and could not learn what one
    # card does, what the two faces are for, how big it is, what it costs, or
    # how to get it. deck.html answers all of that and this page never linked
    # to it. The gallery is where a buyer looks hardest, so the answers belong
    # here too, short, above the grid, and then out of the way.
    anatomy = f"""
  <div class="anat">
    <h2>What one card is</h2>
    <p>A card is one micro zone, one pass, and one finish line: trading card
    size, two and a half by three and a half inches, printed on both
    sides.</p>
    <div class="two">
      <div>
        <h3>The front is what to do</h3>
        <p>The zone or the problem, five numbered points on the picture that
        show you where they are, the objective, a thirty second win, and the
        action to take in your own home.</p>
      </div>
      <div>
        <h3>The back is why, and what next</h3>
        <p>Why the zone matters, the symptoms that say it has slipped, the
        best practices, a seven day challenge, and the card to pick up
        afterwards.</p>
      </div>
    </div>
    <p class="count">{counting}</p>
  </div>"""

    # The last thing on a shop window should be how to get the thing. This
    # page ended on the Room card and stopped.
    if deck == "entryway":
        getit = """
<section class="section" style="padding-top:0">
  <div class="wrap narrow">
    <h2>Getting it</h2>
    <p>The whole Entryway deck prints at home, free, nine cards to a letter
    page with crop marks. No email address, no account. If you want the other
    nineteen rooms, the <a href="shop.html">Whole House Print Pack</a> is the
    same cards for all 114 micro zones.</p>
    <p><a class="btn btn-primary"
    href="downloads/6S-Entryway-Deck-PrintAndPlay.pdf" download>Print the
    deck, free</a> <a class="btn btn-ghost" href="deck.html">How to play
    it</a></p>
    <p style="color:var(--soft);font-size:15px">Whether a printed or boxed
    edition is ever sold, and at what price, has not been decided. When it is,
    it will say so here with a real date rather than a preorder for something
    that does not exist.</p>
  </div>
</section>"""
    else:
        getit = """
<section class="section" style="padding-top:0">
  <div class="wrap narrow">
    <h2>Getting it</h2>
    <p>This deck is not finished and nothing here is for sale yet. The
    <a href="deck-gallery.html">Entryway deck</a> is the one that is drawn,
    and it prints at home free today.</p>
  </div>
</section>"""

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
/* Ten filter chips at 34px, the only way to narrow 72 cards down to the type
   you want. Coarse pointer only, so the desktop row keeps its density; the
   same treatment .filters button gets in site.css for the shop's own chips,
   which are the same control doing the same job. */
@media (pointer: coarse){{.chips button{{min-height:44px}}}}
.grp h2{{margin:44px 0 4px;font-size:22px}}
.grp .cnt{{font-family:var(--sans);font-size:14px;color:var(--soft);
  font-weight:600;vertical-align:3px;margin-left:6px}}
.gb{{margin:0 0 20px;color:var(--soft);max-width:62ch;font-size:15.5px}}
.pnp{{margin:24px 0 0;display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px}}
.pnp span{{font-family:var(--sans);font-size:14px;line-height:1.5;color:var(--soft);max-width:44ch}}
.deckgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));
  gap:22px 18px;list-style:none;padding:0;margin:0}}
.c{{margin:0}}
/* position:relative is load-bearing, not decoration: all:unset resets the
   button to static, and the "Turn over" badge is absolutely positioned
   against this box. Without it the badge anchors to the page. */
.flip{{all:unset;display:block;position:relative;width:100%;
  aspect-ratio:2.5/3.5;cursor:pointer;perspective:1200px;border-radius:12px}}
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
/* A stated artwork fault. Not styled as an alarm: it is a fact about one
   card, and the card is still worth looking at. */
.cap.note{{margin-top:5px;font-size:11.5px;border-left:2px solid var(--line);
  padding-left:8px}}
/* Nothing on the tile said the card turns over, so most visitors would never
   have found the back. Visible always on a touch screen, where there is no
   hover to discover it with; on a pointer it fades up. */
.turn{{position:absolute;left:50%;bottom:8px;transform:translateX(-50%);
  font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.02em;
  color:var(--paper);background:#2b2622cc;border-radius:99px;
  padding:4px 10px;pointer-events:none}}
@media (hover:hover){{
  .turn{{opacity:0;transition:opacity .18s}}
  .flip:hover .turn,.flip:focus-visible .turn{{opacity:1}}
}}
.flip[aria-pressed="true"] .turn{{opacity:0}}
.anat{{margin:30px 0 0;padding:24px 26px;background:var(--panel);
  border:1px solid var(--line);border-radius:18px}}
.anat h2{{margin:0 0 8px;font-size:20px}}
.anat h3{{margin:0 0 4px;font-size:15px;font-family:var(--sans)}}
.anat p{{margin:0 0 12px;font-size:15.5px;color:var(--soft)}}
.anat .two{{display:grid;grid-template-columns:1fr 1fr;gap:6px 26px}}
@media (max-width:640px){{.anat .two{{grid-template-columns:1fr}}}}
.anat .count{{margin:6px 0 0;font-family:var(--sans);font-size:13.5px;
  padding-top:12px;border-top:1px solid var(--line)}}
@media (prefers-reduced-motion:reduce){{
  .inner{{transition:none;transform:none!important;transform-style:flat}}
  .f,.b{{position:relative;backface-visibility:visible;transform:none}}
  .flip{{aspect-ratio:auto;perspective:none}}
  .b{{margin-top:10px}}
  /* Both faces are already on screen when motion is reduced, so a badge
     telling somebody to turn the card over is instructing them to undo
     something that has not happened. */
  .turn{{display:none}}
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
    <p style="color:var(--soft)">The deck is one room, its {zones} micro
    zones and everything that holds them. The method behind it covers
    <a href="zones/">114 micro zones across twenty rooms</a>{printable}.</p>
    {pnp}
    {anatomy}
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
{getit}
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
    /* The label says which face a sighted person is looking at, so it has to
       change with the face. It carries the whole sentence rather than just a
       verb, because "Turn it over" alone tells a screen reader nothing about
       what is currently in front of them. */
    b.setAttribute("aria-label", b.getAttribute("aria-label")
      .replace(on ? "Back is showing" : "Front is showing",
               on ? "Front is showing" : "Back is showing"));
  }});

  /* Filtering hides whole groups, so a heading never survives its cards. */
  function show(t) {{
    groups.forEach(function (g) {{ g.hidden = t !== "all" && g.dataset.t !== t; }});
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

    # AND THE FINGERPRINTER. This generator writes a bare
    # assets/css/site.css reference, while every page on the site ships that
    # link with a ?v= content hash stamped by ops/fingerprint_assets.py. Left
    # unchained, its output can never equal what the site actually carries, so
    # preflight's generator-ownership gate reported these two pages as hand
    # edited on an untouched checkout and failed CI. build_kit_page.py had the
    # identical defect and was fixed the same day. Idempotent, so a later
    # preflight run changes nothing.
    import fingerprint_assets
    fingerprint_assets.main(False)

    print(f"  wrote site/{os.path.basename(OUT)}")
    print(f"  {len(cards)} cards, {len(cards)*2} faces, {len(types)} types")
    print(f"  every referenced image file exists")
    for t in types:
        print(f"    {t:12} {len(by[t])}")
    return


if __name__ == "__main__":
    raise SystemExit(main())
