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

    body = []
    body.append('<main id="main">')
    body.append('<nav class="crumb" style="font-family:var(--sans);'
                'font-size:13px;margin:26px 0 0">'
                '<a href="index.html">Home</a> / How to clean anything</nav>')
    body.append(f"<h1>{html.escape(TITLE)}</h1>")
    body.append(
        '<p class="lede">Every surface in the house, with the method for '
        f'cleaning it: {total} of them, grouped by the room and the micro '
        'zone they belong to. Each one links straight to its own method, '
        'which names the product, the order of work and the reason for it.</p>')
    body.append(
        '<p>Two rules run through all of it. <b>Work down, not across</b>, '
        'because whatever comes off a high surface lands on the one below. '
        'And <b>sort before you shine</b>, because cleaning around something '
        'that should not be there is cleaning you will do again next week.</p>')

    body.append('<nav aria-label="Jump to a room" class="clean-rooms">')
    for room in sorted(rooms):
        body.append(f'<a href="#{re.sub(r"[^a-z0-9]+", "-", room.lower()).strip("-")}">'
                    f'{html.escape(room)}</a> ')
    body.append("</nav>")

    for room in sorted(rooms):
        rid = re.sub(r"[^a-z0-9]+", "-", room.lower()).strip("-")
        n = sum(len(z["surfaces"]) for z in rooms[room])
        body.append(f'<h2 id="{rid}">{html.escape(room)} '
                    f'<span style="font-weight:400;opacity:.7">'
                    f'({n} surfaces)</span></h2>')
        for z in sorted(rooms[room], key=lambda x: x["title"]):
            body.append(f'<h3 class="clean-zone">'
                        f'<a href="{z["url"]}">{html.escape(z["title"])}'
                        f'</a></h3>')
            body.append('<ul class="clean-list">')
            for anchor, name in z["surfaces"]:
                body.append(f'<li><a href="{z["url"]}#{anchor}">'
                            f'{html.escape(name)}</a></li>')
            body.append("</ul>")
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
    print("  wrote %s" % os.path.relpath(OUT, ROOT))
    print("  %d zones, %d surfaces, %d rooms"
          % (len(zones), total, len(rooms)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
