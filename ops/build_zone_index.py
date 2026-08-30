#!/usr/bin/env python3
"""
Build /zones/, a browsable index of all 114 micro zones.

WHY
---
The micro zone is the unit this whole method is built on, and until now there
was no way to browse them. 114 pages existed and /zones/ returned 403, which is
worse than a 404: it tells a crawler the directory is there and refuses it.

resources.html lists them, but nested under their rooms, which answers "what is
in the kitchen" and not "which zones take fifteen minutes" or "which ones are
about paper". Those are the questions somebody actually arrives with, and the
zone data already answers both.

WHAT MAKES THIS NOT A THIN PAGE
-------------------------------
CLAUDE.md forbids generating pages to inflate a page count, correctly. This is
one page, it links to 114 that already exist, and every fact on it is read from
content.json. It is navigation, which is the honest use of an index.

THE FILTERS ARE REAL DATA, NOT INVENTED CATEGORIES
--------------------------------------------------
Session length comes from the zone's own `session` field. The room comes from
the room. Nothing here is a category somebody made up to have filters: if the
data cannot support a facet, the facet does not exist.

Run:  python ops/build_zone_index.py
"""
from __future__ import annotations

import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "content", "manual", "source", "content.json")
BASE = "https://6s-success.com"

sys.path.insert(0, os.path.join(ROOT, "ops"))


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


def esc(t):
    return html.escape(str(t or ""), quote=True)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", (t or "").lower()).strip("-")


NAME_MAP = json.load(io.open(os.path.join(ROOT, "ops", "zone-name-map.json"),
                             encoding="utf-8"))
try:
    SEARCH = json.load(io.open(os.path.join(ROOT, "ops", "zone-search-terms.json"),
                               encoding="utf-8"))
except Exception:
    SEARCH = {}


def display(room, zone):
    return NAME_MAP.get(f"{room}|{zone}", zone)


def searchable(room, zone, name):
    t = SEARCH.get(f"{room}|{zone}")
    if t:
        return t
    t = re.sub(r"^The ", "", name).strip()
    t = re.sub(r"\s+Zone$", "", t).strip()
    t = re.sub(r"^Primary ", "", t).strip()
    return t.lower() if t else name


def bucket(session: str) -> tuple[str, str]:
    """Group by the low end of the zone's own stated range. Buckets are the
    ranges the data actually uses, not round numbers chosen first."""
    m = re.search(r"(\d+)", session or "")
    n = int(m.group(1)) if m else 0
    if n and n <= 15:
        return "quick", "Under half an hour"
    if n and n <= 30:
        return "half", "Half an hour to an hour"
    if n and n <= 45:
        return "hour", "About an hour"
    return "long", "An hour or more"


ORDER = ["quick", "half", "hour", "long"]


def main() -> int:
    d = json.load(io.open(SRC, encoding="utf-8"))
    src = io.open(os.path.join(SITE, "resources.html"), encoding="utf-8").read()
    header = src[src.find('<header class="site-header">'):src.find("</header>") + 9]
    footer = src[src.find('<footer class="site-footer">'):src.find("</footer>") + 10]

    def up(frag):
        return re.sub(r'(href|src)="(?!https?:|#|mailto:|/)([^"]+)"', r'\1="../\2"', frag)
    header, footer = up(header), up(footer)

    zones = []
    for r in d["rooms"]:
        for z in r["zones"]:
            name = display(r["room"], z["zone"])
            zones.append({
                "room": r["room"],
                "roomSlug": slug(r["room"]),
                "name": name,
                "thing": searchable(r["room"], z["zone"], name),
                "url": f"../zones/{slug(r['room'])}-{slug(name)}",
                "purpose": " ".join((z.get("purpose") or "").split()),
                "session": z.get("session", ""),
                "bucket": bucket(z.get("session", ""))[0],
            })

    rooms = sorted({z["room"] for z in zones})
    buckets = [(k, bucket_label) for k in ORDER
               for bucket_label in [next((bucket(z["session"])[1] for z in zones
                                          if z["bucket"] == k), k)]]

    # Filter controls. Plain links with a data attribute, filtered by a little
    # script; with no JavaScript every zone is simply visible, which is the
    # right no-script behaviour for an index.
    chips = ['<button type="button" class="zchip is-on" data-filter="all">'
             f'All {len(zones)}</button>']
    for k, label in buckets:
        n = sum(1 for z in zones if z["bucket"] == k)
        if n:
            chips.append(f'<button type="button" class="zchip" data-filter="{k}">'
                         f'{esc(label)} <span>{n}</span></button>')

    cards = []
    for z in sorted(zones, key=lambda x: (x["room"], x["name"])):
        cards.append(
            f'<li class="zcard" data-bucket="{z["bucket"]}" '
            f'data-room="{esc(z["roomSlug"])}">'
            f'<a href="{esc(z["url"])}">'
            f'<span class="zroom">{esc(z["room"])}</span>'
            f'<span class="zname">{esc(z["name"])}</span>'
            f'<span class="zpurpose">{esc(z["purpose"][:120])}</span>'
            f'<span class="zsession">{esc(z["session"])}</span>'
            "</a></li>")

    room_links = "".join(
        f'<option value="{esc(slug(r))}">{esc(r)}</option>' for r in rooms)

    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Every micro zone in the house",
        "description": (f"All {len(zones)} micro zones across {len(rooms)} rooms, "
                        "each with the six passes written out."),
        "url": f"{BASE}/zones/",
        "isPartOf": {"@id": f"{BASE}/#website"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(zones),
            "itemListElement": [
                {"@type": "ListItem", "position": i,
                 "name": z["name"],
                 "url": f"{BASE}/zones/{z['roomSlug']}-{slug(z['name'])}"}
                for i, z in enumerate(sorted(zones, key=lambda x: (x["room"], x["name"])), 1)
            ],
        },
    }, indent=1)

    crumbs = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Micro zones",
             "item": f"{BASE}/zones/"}],
    }, indent=1)

    title = f"All {len(zones)} micro zones, and how long each one takes"
    desc = (f"Every micro zone in the house, {len(zones)} of them across "
            f"{len(rooms)} rooms. Filter by how long you have, and take any one "
            "through all six passes.")

    css = """
.zfilters{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:22px 0 6px}
.zchip{font:600 13px/1 var(--sans),system-ui,sans-serif;padding:10px 14px;
  min-height:40px;border-radius:99px;border:1px solid #E2D8C4;background:#FBF7EF;
  color:#584f46;cursor:pointer}
.zchip span{color:#8C8478;font-weight:700;margin-left:4px}
.zchip:hover{border-color:#BC4B2A;color:#2B2622}
.zchip.is-on{background:#22323C;border-color:#22323C;color:#EDE4D2}
.zchip.is-on span{color:#C9BFA9}
.zchip:focus-visible{outline:3px solid #3C5A6B;outline-offset:2px}
.zroom-select{font:inherit;font-size:15px;padding:10px 12px;min-height:40px;
  border:1px solid #E2D8C4;border-radius:9px;background:#fff;color:#2B2622}
.zcount{font:600 12px/1 var(--sans),system-ui,sans-serif;letter-spacing:.09em;
  text-transform:uppercase;color:#8C8478;margin:16px 0 0}
.zgrid{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:12px;
  grid-template-columns:repeat(auto-fill,minmax(258px,1fr))}
.zcard a{display:flex;flex-direction:column;gap:5px;height:100%;
  background:#FBF7EF;border:1px solid #E2D8C4;border-left:4px solid #6E8B5B;
  border-radius:0 12px 12px 0;padding:15px 17px;text-decoration:none;color:inherit}
.zcard a:hover{border-left-color:#BC4B2A;background:#fff}
.zcard a:focus-visible{outline:3px solid #3C5A6B;outline-offset:2px}
.zroom{font:700 10.5px/1 var(--sans),system-ui,sans-serif;letter-spacing:.11em;
  text-transform:uppercase;color:#8C8478}
.zname{font-family:var(--display),Georgia,serif;font-size:19px;line-height:1.2;
  color:#2B2622}
.zpurpose{font-size:14.5px;line-height:1.45;color:#584f46;flex:1}
.zsession{font:700 11px/1 var(--sans),system-ui,sans-serif;letter-spacing:.08em;
  text-transform:uppercase;color:#6E8B5B;margin-top:3px}
.zempty{margin:20px 0;color:#584f46}
"""

    body = f"""
<section class="section">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Micro zones</p>
      <h1>{esc(title)}</h1>
      <p class="lede">A room is too big to diagnose and too big to finish. A
      micro zone is not. These are all {len(zones)} of them, and every one has
      the whole method written out: what it is for, what done looks like, the
      six passes in order, and the standard that keeps it.</p>
    </div>

    <div class="zfilters">
      {"".join(chips)}
      <label class="visually-hidden" for="zroom">Room</label>
      <select id="zroom" class="zroom-select">
        <option value="all">Every room</option>
        {room_links}
      </select>
    </div>
    <p class="zcount" id="zcount" role="status">{len(zones)} zones</p>

    <ul class="zgrid" id="zgrid">
      {"".join(cards)}
    </ul>
    <p class="zempty" id="zempty" hidden>No zone matches both of those. Try a
    different length, or every room.</p>
  </div>
</section>

<section class="section band">
  <div class="wrap narrow">
    <p class="eyebrow on-deep">Take them with you</p>
    <h2>Every one of these on a card you can carry</h2>
    <p class="lede">The method above is free and complete. The Whole House Print
    Pack is the same {len(zones)} zones as 684 printable cards, nine to a page,
    so you carry the zone into the room instead of the room to a screen.</p>
    <div class="cta-row" style="margin-top:18px">
      <a class="btn btn-primary btn-lg" href="{PACK_BUY}" rel="noopener">The Print Pack, $19</a>
      <a class="btn btn-on-deep btn-lg" href="../quest.html">Or use the free app</a>
    </div>
  </div>
</section>

<script>
(function () {{
  var grid = document.getElementById("zgrid");
  var count = document.getElementById("zcount");
  var empty = document.getElementById("zempty");
  var roomSel = document.getElementById("zroom");
  var chips = [].slice.call(document.querySelectorAll(".zchip"));
  var cards = [].slice.call(grid.querySelectorAll(".zcard"));
  var bucket = "all";

  function apply() {{
    var room = roomSel.value;
    var n = 0;
    cards.forEach(function (c) {{
      var ok = (bucket === "all" || c.getAttribute("data-bucket") === bucket) &&
               (room === "all" || c.getAttribute("data-room") === room);
      c.hidden = !ok;
      if (ok) {{ n++; }}
    }});
    /* role=status on the count means a screen reader hears the result of a
       filter, which is otherwise a silent change to a long list. */
    count.textContent = n + (n === 1 ? " zone" : " zones");
    empty.hidden = n > 0;
  }}

  chips.forEach(function (b) {{
    b.addEventListener("click", function () {{
      chips.forEach(function (x) {{ x.classList.remove("is-on"); }});
      b.classList.add("is-on");
      bucket = b.getAttribute("data-filter");
      apply();
    }});
  }});
  roomSel.addEventListener("change", apply);
}})();
</script>
"""

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{BASE}/zones/">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="6S Success">
<meta property="og:url" content="{BASE}/zones/">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE}/assets/img/room-map.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/assets/img/room-map.jpg">
<meta name="theme-color" content="#22323C">
<script type="application/ld+json">
{crumbs}
</script>
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="../assets/css/site.css">
<style>{css}</style>
<!-- An index with no analytics tag is a page whose filters nobody can
     learn from, which is the only reason to build filters. -->
<script defer src="/stats/script.js" data-website-id="f1fc5160-4473-422d-a89e-73ff6cbdca7a" data-host-url="https://6s-success.com/stats"></script>
</head>
<body>
{header}
{body}
{footer}
<script src="../assets/js/site.js"></script>
</body>
</html>
"""

    out = os.path.join(SITE, "zones", "index.html")
    io.open(out, "w", encoding="utf-8", newline="").write(page)

    print(f"  site/zones/index.html  {len(zones)} zones, {len(rooms)} rooms, "
          f"{len(page.encode()) // 1024} KB")

    # Every link on an index has to resolve, or the index is the problem.
    bad = [z for z in zones
           if not os.path.exists(os.path.join(SITE, "zones",
                                              f"{z['roomSlug']}-{slug(z['name'])}.html"))]
    assert not bad, f"{len(bad)} zones link to a page that is not there: {bad[:3]}"
    assert len(zones) == 114, f"expected 114 zones, built {len(zones)}"
    print(f"  checked: all {len(zones)} links resolve")

    # This generator's own <head> template carries no PWA icon links and no
    # measurement script; both were wired onto the live page by
    # wire_pwa.py/wire_measure.py directly, same as every other page on the
    # site, so a plain rerun of this file alone silently deleted both (issue
    # #26). Re-running the whole-site, idempotent wiring scripts here closes
    # that gap the same way ops/build_articles.py and
    # ops/build_deck_gallery.py already do.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wire_progressive
    import wire_measure
    import wire_pwa
    # Same trap as the measurement block: this generator's
    # own <head> template has no progressive marker, so a
    # rewrite would strip it and put back the failure where
    # a blocked script leaves sections invisible.
    wire_progressive.main()
    wire_measure.main()
    wire_pwa.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
