#!/usr/bin/env python3
"""
One page that makes 749 cleaning methods findable.

THE PROBLEM THIS SOLVES
-----------------------
The Micro Zone Manual holds a real cleaning method for every surface in a
house: 749 of them across the 114 micro zones, each naming the surface, the
product and the order of work. All 749 were already published. Not one was
findable.

They sit inside pages titled "How to organize the kitchen stove area", in a
list with no headings, and until 2026-09-24 every one of them shared a single
anchor per zone. So a reader searching for how to clean a range hood filter,
and an answer engine trying to cite that method, had nothing to address
smaller than an organising page about a different subject. Published and
unfindable is the most expensive way to own content.

WHAT THIS IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------
It is an index: every surface, grouped by room and zone, linking to its own
anchor on the page that carries the method.

It does NOT repeat the methods. Copying 749 paragraphs here would build a
second page competing with the 114 that already answer the question, which is
how a site ends up competing with itself. The index carries names and links;
the zone pages keep the instruction.

BUILT FROM THE RENDERED PAGES, NOT FROM THE CORPUS
--------------------------------------------------
Every link is read out of site/zones/*.html itself, so a link can only exist
if the anchor it points at exists. Deriving the URLs from content.json a
second time would have been a second derivation free to drift from the first.

    python ops/build_cleaning_index.py
"""
from __future__ import annotations

import glob
import html
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "how-to-clean-anything.html")
BASE = "https://6s-success.com"

sys.path.insert(0, os.path.join(ROOT, "ops"))

TITLE = "How to clean anything in your house, surface by surface"
DESC = ("A cleaning method for every surface in the house, grouped by room: "
        "what to use, what order to work in, and why. Free, no account.")


def strip_tags(t: str) -> str:
    # Source markup carries entities (e.g. "season&#x27;s"); decode them here
    # so the caller's own html.escape() re-encodes cleanly once, not twice.
    # Skipping this step doubles the escape and ships a literal "&amp;#x27;"
    # instead of an apostrophe (found live, 2026-09-24).
    t = html.unescape(t)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", t)).strip()


def read_zone(fp: str) -> dict | None:
    """One zone page's room, name, url and its surfaces with their anchors."""
    s = io.open(fp, encoding="utf-8").read()
    body = re.sub(r"(?is)<script.*?</script>", " ", s)
    surfaces = re.findall(
        r'<li id="(clean-[^"]+)"[^>]*>\s*<b>(.*?)</b>', body, re.S)
    if not surfaces:
        return None
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", body)
    crumb = re.search(r'(?is)<nav class="crumb".*?</nav>', body)
    room = ""
    if crumb:
        links = re.findall(r"(?is)<a[^>]*>(.*?)</a>", crumb.group(0))
        if len(links) >= 2:
            room = strip_tags(links[-1])
    slug = os.path.basename(fp)[:-5]
    return {
        "slug": slug,
        "url": "zones/" + slug,
        "title": strip_tags(h1.group(1)) if h1 else slug,
        "room": room or slug.split("-")[0].replace("-", " ").title(),
        "surfaces": [(a, strip_tags(n)) for a, n in surfaces],
    }


def manual_offer() -> str | None:
    """The one offer on this page, drawn from the live catalogue.

    The Micro Zone Manual is the book these 762 methods come from, so it is
    the honest next step for a reader who wants them offline and in order.
    Price and payment link are read from site/assets/js/data.js, the single
    source the shop renders from, so this card can never quote a price or a
    link the shop does not.
    """
    import json as _json
    src = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                  encoding="utf-8").read()
    row = None
    for line in src.splitlines():
        line = line.strip().rstrip(",")
        if '"sku": "MZ-MANUAL"' in line and line.startswith("{"):
            try:
                row = _json.loads(line)
            except ValueError:
                return None
    if not row or not row.get("buy") or not row.get("price"):
        return None
    price = ("%g" % row["price"])
    return (
        '<aside class="clean-offer" aria-label="The Micro Zone Manual">'
        '<picture><source type="image/webp" srcset="assets/img/w/'
        'product-manual-420.webp 420w, assets/img/w/product-manual-840.webp 840w"'
        ' sizes="(max-width:760px) 92vw, 360px">'
        '<img src="assets/img/product-manual.jpg" width="1280" height="960" '
        'loading="lazy" decoding="async" alt="Pages of the Micro Zone Manual '
        'laid out on paper"></picture>'
        '<div><p class="eyebrow">All of it, in one place</p>'
        '<h2 class="clean-offer-h">Every method on this page, offline and '
        'in order</h2>'
        '<p>The Micro Zone Manual is where these methods come from: all 20 '
        'rooms and 114 micro zones, each with the exact clean-and-shine '
        'steps, the products it needs and what done looks like. A field '
        'guide you can print or keep on a phone in the room.</p>'
        '<p class="clean-offer-buy"><a class="btn btn-primary" '
        'data-sku="MZ-MANUAL" href="' + html.escape(row["buy"]) + '" '
        'rel="nofollow noopener">Get the Manual, $' + price + ' USD</a> '
        '<span class="clean-offer-note">' + html.escape(row.get("fulfil", "")) +
        '. Every method stays free on this site either way.</span></p>'
        '</div></aside>')


def main() -> int:
    zones = []
    for fp in sorted(glob.glob(os.path.join(SITE, "zones", "*.html"))):
        if fp.endswith("index.html"):
            continue
        z = read_zone(fp)
        if z:
            zones.append(z)
    if not zones:
        print("  no zone page carries per-surface anchors. Run "
              "ops/build_zone_pages.py first; refusing to write an empty "
              "index.")
        return 1

    total = sum(len(z["surfaces"]) for z in zones)

    src = io.open(os.path.join(SITE, "resources.html"), encoding="utf-8").read()
    header = src[src.find('<header class="site-header">'):
                 src.find("</header>") + 9]
    footer = src[src.find('<footer class="site-footer">'):
                 src.find("</footer>") + 10]
    head_open = src[:src.find("</head>")]
    css = re.search(r'<link rel="stylesheet" href="([^"]+)"', head_open)
    css_href = css.group(1) if css else "assets/css/site.css"

    # The script tail is LIFTED from a real page, never typed here: site.js
    # then the analytics tag. It lives after </footer>, NOT in the head,
    # which is why an earlier version of this generator looked in the head,
    # found nothing, and shipped a page with no measurement at all.
    #
    # It matters more here than on most pages. Without the analytics tag
    # ops/wire_measure.py correctly refuses to add measure.js, and a page
    # built to be found that cannot tell you whether anyone found it is the
    # one page on this site least worth shipping blind. Copying rather than
    # typing also means the site id and host cannot drift from what every
    # other page sends.
    # str.rfind RETURNS -1 WHEN IT FINDS NOTHING, and -1 is a valid index, so
    # the slice below silently becomes "almost the whole file" rather than
    # failing. On 2026-09-24 a broken build of resources.html shipped with a
    # literal {FOOTER} placeholder and no footer at all; this line found no
    # </footer>, took garbage as the "script tail", and wrote an index page
    # with no site.js and no measure.js. The result was a dead mobile nav
    # button and a page built to be found that could not report whether anyone
    # found it, which is the exact failure the comment above warns about.
    #
    # So it is checked rather than assumed, and the check is on what the tail
    # must CONTAIN, not merely on whether a marker was located.
    cut = src.rfind("</footer>")
    if cut == -1:
        print("  resources.html carries no </footer>, so the script tail "
              "cannot be lifted from it. Refusing to write a page with no "
              "navigation and no measurement. Rebuild resources.html first.")
        return 1
    tail = src[cut + len("</footer>"):]
    tail = tail.split("<!-- MEASURE:BEGIN -->")[0]
    tail = tail.replace("</body>", "").replace("</html>", "").strip()
    if "site.js" not in tail:
        print("  the script tail lifted from resources.html carries no "
              "site.js, so this page's nav button would be dead on load. "
              "Refusing to write it.")
        return 1

    rooms: dict = {}
    for z in zones:
        rooms.setdefault(z["room"], []).append(z)

    manual = manual_offer()
    if manual is None:
        print("  the Micro Zone Manual (MZ-MANUAL) has no price and buy link "
              "in site/assets/js/data.js, so the offer card cannot be drawn "
              "honestly. Refusing to write the page without it.")
        return 1

    def rid_of(room):
        return re.sub(r"[^a-z0-9]+", "-", room.lower()).strip("-")

    body = []
    body.append('<main id="main">')
    # THE PAGE SAT FLUSH AGAINST THE LEFT EDGE OF THE WINDOW until 2026-10-26:
    # every other page puts its content inside .section > .wrap and this one
    # wrote straight into <main>, so 762 links ran from x=0 with no margin on
    # desktop. Same container as the rest of the site now.
    body.append('<section class="section clean-head"><div class="wrap">')
    body.append('<nav class="crumb" style="font-family:var(--sans);'
                'font-size:13px;margin:0 0 14px">'
                '<a href="index.html">Home</a> / How to clean anything</nav>')
    body.append(f"<h1>{html.escape(TITLE)}</h1>")
    body.append(
        '<p class="lede">Every surface in the house, with the method for '
        f'cleaning it: {total} of them, grouped by the room and the micro '
        'zone they belong to. Each one links straight to its own method, '
        'which names the product, the order of work and the reason for it.</p>')
    body.append('<div class="clean-rules">'
                '<p><b>Work down, not across.</b> Whatever comes off a high '
                'surface lands on the one below, so the floor is always last.</p>'
                '<p><b>Sort before you shine.</b> Cleaning around something that '
                'should not be there is cleaning you will do again next week.</p>'
                '<p><b>Never mix cleaners.</b> One product at a time, the room '
                'aired, and gloves on for anything that says so on the label.</p>'
                '</div>')
    body.append('<nav aria-label="Jump to a room" class="clean-rooms">')
    for room in sorted(rooms):
        n = sum(len(z["surfaces"]) for z in rooms[room])
        body.append(f'<a href="#{rid_of(room)}">{html.escape(room)} '
                    f'<span class="n">{n}</span></a>')
    body.append("</nav>")
    body.append("</div></section>")

    body.append('<section class="section clean-body"><div class="wrap">')
    ordered = sorted(rooms)
    for i, room in enumerate(ordered):
        n = sum(len(z["surfaces"]) for z in rooms[room])
        body.append(f'<section class="clean-room" aria-labelledby="{rid_of(room)}">')
        body.append(f'<h2 id="{rid_of(room)}">{html.escape(room)} '
                    f'<span class="clean-n">{n} surfaces</span></h2>')
        body.append('<div class="clean-grid">')
        for z in sorted(rooms[room], key=lambda x: x["title"]):
            k = len(z["surfaces"])
            body.append('<div class="clean-card">')
            body.append(f'<h3 class="clean-zone">'
                        f'<a href="{z["url"]}">{html.escape(z["title"])}'
                        f'</a></h3>')
            body.append(f'<p class="clean-count">{k} '
                        f'{"surface" if k == 1 else "surfaces"}</p>')
            body.append('<ul class="clean-list">')
            for anchor, name in z["surfaces"]:
                body.append(f'<li><a href="{z["url"]}#{anchor}">'
                            f'{html.escape(name)}</a></li>')
            body.append("</ul></div>")
        body.append("</div></section>")
        # One offer, once, after the third room: far enough in that the
        # reader has seen what the methods are, early enough that a reader
        # who wants them all in one place is not made to scroll 700 links.
        if i == 2:
            body.append(manual)
    body.append("</div></section>")
    body.append("</main>")

    # CollectionPage, matching kit.html's own established pattern for a
    # hand-authored, non-generator-owned index page (gate_indexable_pages_
    # have_schema, 2026-09-05): no fabricated rating, price or review, only
    # what this page actually is, an index of real published methods.
    schema = (
        '<script type="application/ld+json">\n'
        + __import__("json").dumps({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "@id": f"{BASE}/how-to-clean-anything.html#collectionpage",
            "name": TITLE,
            "url": f"{BASE}/how-to-clean-anything.html",
            "description": DESC,
            "isPartOf": {"@id": f"{BASE}/#website"},
            "publisher": {"@id": f"{BASE}/#organization"},
        }, indent=2)
        + "\n</script>\n"
    )

    doc = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(TITLE)}</title>"
        f'<meta name="description" content="{html.escape(DESC)}">'
        f'<link rel="canonical" href="{BASE}/how-to-clean-anything.html">'
        + schema +
        f'<link rel="stylesheet" href="{css_href}">'
        "</head><body>" + header + "\n".join(body) + footer +
        "\n" + tail + "\n</body></html>")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(doc)

    # Chain the whole-site wiring passes, exactly as ops/build_articles.py
    # does and for the same reason (issue #26): this template carries no
    # measurement, no PWA icons and no nav position of its own, so a bare
    # rerun would write a page missing all three. It also breaks
    # gate_generator_ownership, which reruns every generator and diffs the
    # result: the committed page is wired, a freshly generated one would
    # not be, and the diff fails with no obvious cause.
    for _mod in ("canonical_links", "wire_landmarks", "wire_progressive",
                 "wire_measure", "wire_pwa", "wire_aria_current"):
        try:
            _m = __import__(_mod)
            if hasattr(_m, "main"):
                _m.main()
        except SystemExit:
            pass
        except Exception as _exc:                              # noqa: BLE001
            print("  WARNING: %s did not run (%s), so this page may be "
                  "missing its wiring" % (_mod, _exc))

    # Found 2026-10-26, cold-reading this file after Phil's own cleaning
    # review touched it: the comment above claims this chains "exactly as
    # ops/build_articles.py does", but build_articles.py's own chain calls
    # build_avif.wire() after wire_aria_current and then fingerprints,
    # and this file never did either. build_avif's function is wire(), not
    # main(), so it could not have been folded into the generic
    # hasattr(_m, "main") loop above without silently no-op'ing, the exact
    # trap build_articles.py's own comment names by date ("failed CI eleven
    # times on 2026-09-01: the wiring pass existed and was never chained").
    # Reproduced directly: a standalone run of this file (the way an
    # operator actually reaches for it, after a content.json edit) stripped
    # the committed AVIF <source> off the manual-offer picture, confirmed
    # by diffing the result against the committed site/how-to-clean-
    # anything.html. Invisible inside a full preflight.py --own run,
    # because build_avif.wire() runs globally later in that same chain and
    # repairs it as a side effect everywhere, this page included.
    try:
        import build_avif
        build_avif.wire()
        import fingerprint_assets
        fingerprint_assets.main(False)
    except SystemExit:
        pass
    except Exception as _exc:                                  # noqa: BLE001
        print("  WARNING: build_avif/fingerprint_assets did not run (%s), "
              "so this page may be missing its AVIF source or cache-"
              "busting fingerprint" % _exc)
    print("  wrote %s" % os.path.relpath(OUT, ROOT))
    print("  %d zones, %d surfaces, %d rooms"
          % (len(zones), total, len(rooms)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
