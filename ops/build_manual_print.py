# -*- coding: utf-8 -*-
"""
Print production build for The Micro Zone Manual (6S Home Micro Zone SOP Field Manual v3).

What this does, in order:

  1. House style       normalises dashes to zero em dashes and zero en dashes,
                       in the manual HTML and in its source content.json.
  2. Appendices        rebuilds Appendix A and Appendix B (HTML + CSV) from the
                       current 123-type master product library, recomputing
                       per-zone usage from the zone map rather than trusting the
                       stale _zone_count baked into products.json.
  3. Front matter      injects a half title, a copyright and imprint page, and a
                       "Read this before you begin" page carrying the frozen
                       six-s-disclaimer block near the front of the book.
  4. Print stylesheet  injects a 7 x 10 in paged-media stylesheet: trim, recto and
                       verso margins, folios, running heads, break control,
                       and a one-colour ink conversion. Screen rendering is
                       untouched because every rule is inside @media print or an
                       @page block.
  5. Print edition     writes a single self-contained document with the appendices
                       bound in, plus self-hosted fonts, to content/manual/print/.
  6. Gates             counts em dashes, en dashes, brand names, rooms, zones and
                       products, and fails loudly.

Every injected region is fenced with sentinel comments, so the script is
idempotent: run it twice and you get the same file.

Usage:
    python ops/build_manual_print.py             # build + validate
    python ops/build_manual_print.py --measure   # also render PDFs and count pages
"""

import base64
import collections
import csv
import html as H
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL_DIR = os.path.join(ROOT, "content", "manual")
SOURCE_DIR = os.path.join(MANUAL_DIR, "source")
APPX_DIR = os.path.join(MANUAL_DIR, "appendices")
PRINT_DIR = os.path.join(MANUAL_DIR, "print")
FONT_SRC = os.path.join(ROOT, "site", "assets", "fonts")   # read only, never written

MANUAL = os.path.join(MANUAL_DIR, "6S Home Micro Zone SOP Field Manual v3.html")
PUBLISHABLE = os.path.join(MANUAL_DIR, "micro-zone-manual-publishable.html")
CONTENT_JSON = os.path.join(SOURCE_DIR, "content.json")
PRODUCTS_JSON = os.path.join(SOURCE_DIR, "products.json")
ZONE_PRODUCTS_JSON = os.path.join(SOURCE_DIR, "zone_products.json")
SHINE_GAPS_JSON = os.path.join(SOURCE_DIR, "shine_gaps.json")

OUT_A = os.path.join(APPX_DIR, "Appendix A - The Complete 6S Home Kit.html")
OUT_B = os.path.join(APPX_DIR, "Appendix B - Inputs and Sourcing List.html")
OUT_B_CSV = os.path.join(APPX_DIR, "Appendix B - Inputs and Sourcing List.csv")
OUT_PRINT = os.path.join(PRINT_DIR, "6S-Micro-Zone-Manual-PRINT-7x10.html")

EM = u"\u2014"
EN = u"\u2013"

# Retailers and manufacturer brands. The manual names product TYPES only. A
# brand-dense variant of this manual was quarantined, so this list is a gate,
# not a suggestion.
BRANDS = [
    "Walmart", "Amazon", "Target", "Home Depot", "Lowe's", "Lowes", "Lysol", "IKEA",
    "Costco", "Clorox", "Sharpie", "Rubbermaid", "Container Store", "OXO", "Wayfair",
    "Etsy", "eBay", "Dollar Tree", "Command Strip", "Elfa", "simplehuman", "Swiffer",
    "Windex", "Magic Eraser", "Mr. Clean", "Bona", "Seventh Generation", "Sterilite",
    "Akro-Mils", "Gladiator", "Husky", "Craftsman", "Kallax", "Trofast", "Ziploc",
    "Tupperware", "Brita", "Dyson", "Shark Navigator", "Bissell", "Yeti", "Weber",
    "Rubbermaid Brilliance", "Zep", "Krud Kutter", "Goo Gone", "WD-40", "Scrubbing Bubbles",
]

TRIM_W_IN, TRIM_H_IN = 7.0, 10.0

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def read(path):
    return io.open(path, encoding="utf-8").read()


def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)


def esc(s):
    return H.escape("" if s is None else str(s).strip(), quote=False)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def money(x):
    v = num(x)
    return ("$%.2f" % v) if v is not None else ""


def strip_tags(s):
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    return H.unescape(re.sub(r"<[^>]+>", " ", s))


def fence(name, payload):
    return "<!-- BEGIN 6S %s -->\n%s\n<!-- END 6S %s -->" % (name, payload, name)


def unfence(doc, name):
    """Remove a previously injected region so the build is idempotent."""
    # Consume the trailing newline only. Eating the leading one too would make
    # the build drift by a blank line on every re-run.
    pat = re.compile(
        r"<!-- BEGIN 6S %s -->.*?<!-- END 6S %s -->\n?" % (re.escape(name), re.escape(name)),
        re.S,
    )
    return pat.sub("", doc)


def normalise_dashes(s):
    """Zero em dashes, zero en dashes. House style, no exceptions.

    Every en dash in this corpus sits inside a session-time range (30-45 min),
    so a hyphen is the correct replacement and reads identically in print. Any
    other en dash is a defect and is reported by the gate, not silently mangled.
    """
    s = re.sub(r"(\d)\s*" + EN + r"\s*(\d)", r"\1-\2", s)
    return s


# ---------------------------------------------------------------------------
# product library
# ---------------------------------------------------------------------------


def load_library():
    master = json.load(io.open(PRODUCTS_JSON, encoding="utf-8"))["master"]
    zone_products = json.load(io.open(ZONE_PRODUCTS_JSON, encoding="utf-8"))

    # Recompute per-zone usage from the zone map. products.json carries a
    # _zone_count that was frozen at an earlier catalog state and is wrong for
    # ten records, all of them cleaning tools added after the count was taken.
    used = collections.Counter()
    for items in zone_products.values():
        for it in items:
            used[it["id"]] += 1

    stale = []
    for m in master:
        pid = m["Product ID"]
        actual = used.get(pid, 0)
        if int(m.get("_zone_count") or 0) != actual:
            stale.append((pid, m.get("Product Standard Name"), m.get("_zone_count"), actual))
        m["_zones_used"] = actual
        m["_fam"] = m.get("Product Family") or "Other"

    return master, zone_products, used, stale


FAMILY_ORDER = [
    "Cleaning Supplies", "Cleaning Tools", "Sort & Routing", "Storage & Organization",
    "Visual Controls", "Visual Controls & Safety", "Safety",
]


def group_families(master):
    by = collections.OrderedDict()
    for fam in FAMILY_ORDER:
        items = [m for m in master if m["_fam"] == fam]
        if items:
            by[fam] = items
    for m in master:
        if m["_fam"] not in by:
            by.setdefault(m["_fam"], []).append(m)
    return by


def close_shine_gaps(master):
    """Which of the 20 Shine-implied inputs the catalog has since absorbed."""
    try:
        gaps = json.load(io.open(SHINE_GAPS_JSON, encoding="utf-8"))
    except (IOError, OSError, ValueError):
        return []
    lib = [(m["Product ID"], str(m.get("Product Standard Name") or ""),
            str(m.get("Category") or "")) for m in master]

    def match(item):
        n = set(re.findall(r"[a-z]+", item.lower())) - {
            "a", "the", "for", "and", "or", "of", "with", "set", "to", "in", "on"}
        best = None
        for pid, name, cat in lib:
            w = set(re.findall(r"[a-z]+", (name + " " + cat).lower()))
            score = len(n & w)
            if score >= 2 and (best is None or score > best[0]):
                best = (score, pid, name)
        return best

    out = []
    for g in gaps:
        hit = match(g["item"])
        out.append({
            "item": g["item"],
            "zones": g["zones"],
            "status": "Closed, now in the library" if hit else "Still missing, add to the catalog",
            "matched": ("%s %s" % (hit[1], hit[2])) if hit else "",
        })
    return out


# ---------------------------------------------------------------------------
# appendix chrome (book design system, print-aware)
# ---------------------------------------------------------------------------

APPX_CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--honey:#DDA63A;--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.55}
.book{max-width:1080px;margin:0 auto;padding:0 24px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:48px 0 6px;max-width:720px}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(32px,5.5vw,50px);line-height:1.04;margin:.1em 0 .25em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(17px,2.3vw,20px);margin:0 0 6px;max-width:640px}
.lede{max-width:720px;color:var(--soft);font-size:1.02em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(22px,3vw,29px);margin:2em 0 .4em;scroll-margin-top:64px}
p{margin:0 0 1em;max-width:720px}
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);border-bottom:1px solid var(--rule2);padding:9px 24px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:15px;margin-right:auto}
.topbar input{font-family:var(--sans);font-size:14px;padding:7px 11px;border:1px solid var(--rule2);border-radius:8px;background:var(--panel);color:var(--ink);min-width:220px}
.topbar a{font-family:var(--sans);font-size:12.5px;color:var(--slate);text-decoration:none;padding:4px 8px;border-radius:6px}
.topbar .count{font-family:var(--sans);font-size:12.5px;color:var(--soft)}
.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 6px}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:16px 18px}
.card .num{font-family:var(--display);font-size:30px;font-weight:700;color:var(--green)}
.card b{color:var(--soft);font-size:12.5px;letter-spacing:.5px;text-transform:uppercase;font-family:var(--sans)}
.gap{background:#fbf3e6;border:1px solid var(--honey);border-left:5px solid var(--honey);border-radius:0 12px 12px 0;padding:14px 18px;margin:1.2em 0;max-width:none}
.gap b{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#B5811E;display:block;margin-bottom:5px}
.famhead{border-bottom:3px solid var(--terra);padding-bottom:8px;margin:2.2em 0 .6em;display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap}
.famhead h2{margin:0;border:0}
.famhead .n{font-family:var(--sans);font-size:13px;color:var(--soft)}
.item{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:15px 18px;margin:10px 0;break-inside:avoid}
.item .top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.item h3{font-family:var(--display);font-size:19px;font-weight:600;margin:0}
.item .lvl{font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 9px;border-radius:12px;white-space:nowrap}
.lvl.core{background:#e6efe4;color:#3f6647}.lvl.recommended{background:#eef1f3;color:var(--slate)}.lvl.situational{background:#f4ece0;color:#8a6a2b}
.item .purpose{margin:.4em 0 .5em;font-size:16px}
.item .meta{font-family:var(--sans);font-size:13px;color:var(--soft);display:flex;flex-wrap:wrap;gap:6px 18px}
.item .meta b{color:var(--slate);font-weight:600}
.item .safety{font-family:var(--sans);font-size:12.5px;color:#9a5a3a;margin-top:6px}
.item .safety::before{content:"\\26A0  "}
.wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;margin:1.2em 0}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:13px;background:var(--panel);min-width:900px}
th{background:var(--slate);color:var(--paper);text-align:left;padding:9px 10px;font-weight:600;font-size:11.5px;letter-spacing:.03em;position:sticky;top:0}
td{padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
tr:nth-child(even) td{background:#faf6ee}
td.id{font-variant-numeric:tabular-nums;color:var(--soft);white-space:nowrap}
td.blank{background:#fff8ec !important;color:#c9a15a;font-style:italic}
.totop{position:fixed;right:16px;bottom:16px;z-index:60;background:var(--slate);color:var(--paper);font-family:var(--sans);font-size:12.5px;padding:9px 14px;border-radius:20px;text-decoration:none;opacity:.9}
footer{max-width:720px;margin:64px auto 0;border-top:2px solid var(--rule2);padding-top:16px;color:var(--soft);font-family:var(--sans);font-size:13.5px}
@media(max-width:820px){.summary{grid-template-columns:1fr 1fr}}
"""

FILTER_JS = """
(function(){var b=document.getElementById('f'),c=document.getElementById('c');
if(!b)return;var items=[].slice.call(document.querySelectorAll('[data-row]'));
items.forEach(function(i){i.dataset.h=(i.textContent||'').toLowerCase();});
function ap(){var q=(b.value||'').trim().toLowerCase(),n=0;
items.forEach(function(i){var hit=!q||i.dataset.h.indexOf(q)>-1;i.style.display=hit?'':'none';if(hit)n++;});
document.querySelectorAll('[data-fam]').forEach(function(s){
var any=[].slice.call(s.querySelectorAll('[data-row]')).some(function(i){return i.style.display!=='none';});
s.style.display=any?'':'none';});
if(c)c.textContent=n+' of '+items.length+' items';}
b.addEventListener('input',ap);ap();})();
"""

GFONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
          '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;'
          '9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;'
          '0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">')


def fam_slug(f):
    return re.sub(r"[^a-z0-9]+", "-", f.lower()).strip("-")


def lvl_class(m):
    lv = (m.get("Required Level") or "Recommended").lower()
    return lv if lv in ("core", "recommended", "situational") else "recommended"


# ---------------------------------------------------------------------------
# Appendix A
# ---------------------------------------------------------------------------


def build_appendix_a(master, by_family, unmapped, shine, notes, total_pairs):
    fam_nav = "".join('<a href="#%s">%s</a>' % (fam_slug(f), esc(f)) for f in by_family)
    fam_nav += '<a href="#unmapped">Not yet mapped</a><a href="#decor">Decor</a>'
    if shine:
        fam_nav += '<a href="#shine-implied">Shine-implied</a>'

    secs = []
    for fam, items in by_family.items():
        rows = []
        key = lambda x: (str(x.get("Category")), str(x.get("Product Standard Name")))
        for m in sorted(items, key=key):
            safety = m.get("Safety / Compatibility Notes")
            rows.append(
                '<div class="item" data-row><div class="top">'
                '<h3>%s</h3><span class="lvl %s">%s</span></div>'
                '<p class="purpose">%s</p>'
                '<div class="meta"><span><b>Ref:</b> %s</span>'
                '<span><b>Category:</b> %s</span>'
                '<span><b>6S step:</b> %s</span>'
                '<span><b>Standard qty:</b> %s %s</span>'
                '<span><b>Typical retail:</b> %s to %s</span>'
                '<span><b>Used in:</b> %d of 114 zones</span>'
                '<span><b>Rooms:</b> %s</span></div>%s</div>'
                % (esc(m.get("Product Standard Name")), lvl_class(m), esc(m.get("Required Level")),
                   esc(m.get("Primary Purpose")), esc(m.get("Product ID")), esc(m.get("Category")),
                   esc(m.get("Supported 6S Phases")), esc(m.get("Standard Quantity")),
                   esc(m.get("Unit of Measure")), money(m.get("Estimated Retail Low")),
                   money(m.get("Estimated Retail High")), m["_zones_used"],
                   esc(m.get("Applicable Rooms")),
                   ('<div class="safety">%s</div>' % esc(safety)) if safety else ""))
        secs.append(
            '<section data-fam id="%s"><div class="famhead"><h2>%s</h2>'
            '<span class="n">%d type%s</span></div>%s</section>'
            % (fam_slug(fam), esc(fam), len(items), "" if len(items) == 1 else "s", "".join(rows)))

    # in the kit, not yet mapped to any zone
    if unmapped:
        rows = "".join(
            "<tr data-row><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(m.get("Product ID")), esc(m.get("Product Standard Name")), esc(m.get("Product Family")))
            for m in unmapped)
        secs.append(
            '<section data-fam id="unmapped"><div class="famhead"><h2>In the kit, not yet mapped</h2>'
            '<span class="n">%d types</span></div>'
            '<div class="gap"><b>Gap, mapping</b>These types are in the library and are real parts of the '
            'method, but no zone card currently calls for them. Either map each one to the zones where it '
            'belongs, or retire it. Leaving a type in the catalog that nothing asks for is how a kit grows '
            'items nobody needs.</div>'
            '<div class="wrap"><table><thead><tr><th>Ref</th><th>Type</th><th>Family</th></tr></thead>'
            '<tbody>%s</tbody></table></div></section>' % (len(unmapped), rows))

    secs.append(
        '<section data-fam id="decor"><div class="famhead"><h2>Decor</h2>'
        '<span class="n">to populate</span></div>'
        '<div class="gap"><b>Gap, not yet in the library</b>Decor is still absent. If it is added, it '
        'belongs here as types: framed print, table lamp, plant and pot, rug, throw and cushion, each tied '
        'to the rooms and zones where a finished surface actually needs one. Until then the manual does '
        'not recommend decor, and it should not pretend to.</div></section>')

    if shine:
        closed = [g for g in shine if g["status"].startswith("Closed")]
        still = [g for g in shine if not g["status"].startswith("Closed")]
        rows = "".join(
            "<tr data-row><td>%s</td><td style='text-align:center'>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(g["item"]), esc(g["zones"]), esc(g["status"]), esc(g["matched"]))
            for g in shine)
        secs.append(
            '<section data-fam id="shine-implied"><div class="famhead"><h2>Shine-implied inputs</h2>'
            '<span class="n">%d tracked, %d closed</span></div>'
            '<div class="gap"><b>Tracking, from the deepened Shine pass</b>Writing a cleaning method for '
            'every surface surfaced twenty inputs the catalog did not carry. %d of them have since been '
            'added, which is most of the growth from 97 types to %d. %d are still open.</div>'
            '<div class="wrap"><table><thead><tr><th>Implied input</th><th>Zones</th><th>Status</th>'
            '<th>Now covered by</th></tr></thead><tbody>%s</tbody></table></div></section>'
            % (len(shine), len(closed), len(closed), len(master), len(still), rows))

    gapnotes = "".join('<div class="gap"><b>Note</b>%s</div>' % esc(n) for n in notes)

    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Appendix A - The Complete 6S Home Kit</title>
<meta name="description" content="Every product type used to 6S a home, by family, with its purpose, its 6S step, and how many of the 114 micro zones call for it.">
%s
<style>%s</style>
<style>%s</style></head><body>
<div class="topbar"><span class="brand">Appendix A &middot; The Complete 6S Home Kit</span>
<input id="f" type="search" placeholder="Filter types, rooms, uses..." aria-label="Filter">
<span class="count" id="c"></span>%s</div>
<main class="book">
<header class="masthead"><p class="chno">6S Success &middot; Home Edition &middot; Companion Volume</p>
<p class="eyebrow">Appendix A</p><h1 class="title">The Complete 6S Home Kit</h1>
<p class="subtitle">Every cleaning supply, tool, storage, organization, visual control, and safety type used to 6S a home, by family.</p></header>
<p class="lede">These are the %d product types behind the Micro Zone Manual: what each one is for, which of the six steps it serves, how many of the 114 zones call for it, and where. Types, not brands. Gaps are flagged rather than hidden.</p>
<section class="summary">
<div class="card"><div class="num">%d</div><b>Product types</b></div>
<div class="card"><div class="num">%d</div><b>Families</b></div>
<div class="card"><div class="num">%s</div><b>Zone to type links</b></div>
<div class="card"><div class="num">114</div><b>Zones covered</b></div>
</section>
%s
%s
<footer><p><b>Appendix A &middot; The Complete 6S Home Kit</b> &middot; Companion to 6S Success: Home Edition.
Built from the master product library, %d types, and the zone map, %s links across 114 zones.
Types only. No brands, no retailers. Retail ranges are planning estimates, not quotations.</p></footer>
</main><a class="totop" href="#">Top</a><script>%s</script></body></html>""" % (
        GFONTS, APPX_CSS, appendix_print_css(), fam_nav, len(master), len(master),
        len(by_family), "{:,}".format(total_pairs), gapnotes, "".join(secs),
        len(master), "{:,}".format(total_pairs), FILTER_JS)


# ---------------------------------------------------------------------------
# Appendix B
# ---------------------------------------------------------------------------

B_COLS = ["Ref", "Product type", "Family", "Category", "Purpose", "6S step", "Level",
          "Qty", "Unit", "Est. low", "Est. mid", "Est. high", "Zones",
          "Safety and compatibility", "Partner link", "Own-label SKU"]


def build_appendix_b(master, by_family, notes, total_pairs):
    body = []
    for fam, items in by_family.items():
        body.append('<tr data-fam><td colspan="%d" style="background:#efe7d6;font-weight:700;'
                    'color:var(--slate)">%s (%d)</td></tr>' % (len(B_COLS), esc(fam), len(items)))
        for m in sorted(items, key=lambda x: str(x.get("Product ID"))):
            body.append(
                "<tr data-row>"
                "<td class='id'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                "<td style='text-align:center'>%d</td><td>%s</td>"
                "<td class='blank'>to add</td><td class='blank'>to add</td></tr>"
                % (esc(m.get("Product ID")), esc(m.get("Product Standard Name")),
                   esc(m.get("Product Family")), esc(m.get("Category")),
                   esc(m.get("Primary Purpose")), esc(m.get("Supported 6S Phases")),
                   esc(m.get("Required Level")), esc(m.get("Standard Quantity")),
                   esc(m.get("Unit of Measure")), money(m.get("Estimated Retail Low")),
                   money(m.get("Estimated Retail Mid")), money(m.get("Estimated Retail High")),
                   m["_zones_used"], esc(m.get("Safety / Compatibility Notes"))))

    lo = sum(num(m.get("Estimated Retail Low")) or 0 for m in master)
    hi = sum(num(m.get("Estimated Retail High")) or 0 for m in master)
    core = [m for m in master if (m.get("Required Level") or "").lower() == "core"]
    core_lo = sum(num(m.get("Estimated Retail Low")) or 0 for m in core)
    core_hi = sum(num(m.get("Estimated Retail High")) or 0 for m in core)

    gapnotes = "".join('<div class="gap"><b>Note</b>%s</div>' % esc(n) for n in notes)
    th = "".join("<th>%s</th>" % esc(c) for c in B_COLS)

    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Appendix B - Inputs and Sourcing List</title>
<meta name="description" content="The 6S home kit as a sourcing sheet: every product type with quantity, retail range, safety notes, and blank columns for partner links and own-label SKUs.">
%s
<style>%s</style>
<style>%s</style></head><body>
<div class="topbar"><span class="brand">Appendix B &middot; Inputs and Sourcing List</span>
<input id="f" type="search" placeholder="Filter inputs..." aria-label="Filter">
<span class="count" id="c"></span></div>
<main class="book">
<header class="masthead"><p class="chno">6S Success &middot; Home Edition &middot; Companion Volume</p>
<p class="eyebrow">Appendix B</p><h1 class="title">Inputs and Sourcing List</h1>
<p class="subtitle">The same kit as a procurement sheet, with columns left open for partner links and own-label references.</p></header>
<p class="lede">All %d types as a sourcing table: purpose, 6S step, standard quantity, estimated retail range, how many zones call for it, and the safety note that travels with it. Two columns are deliberately blank, Partner link and Own-label SKU, to be filled as the product line is built. The same table ships as a CSV.</p>
<section class="summary">
<div class="card"><div class="num">%d</div><b>Product types</b></div>
<div class="card"><div class="num">%d</div><b>Core types</b></div>
<div class="card"><div class="num">%s</div><b>Core kit, low to high</b></div>
<div class="card"><div class="num">%s</div><b>Full kit, low to high</b></div>
</section>
<div class="gap"><b>How to read the money columns</b>These are planning estimates for a type of product,
gathered as a range because the same type sells at very different prices. They are not quotations, they
carry no brand, and they will move. Nobody buys the full kit. The Core column is the honest starting
number, and most homes will not need all of that either.</div>
%s
<div class="wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>
<footer><p><b>Appendix B &middot; Inputs and Sourcing List</b> &middot; Companion to 6S Success: Home Edition.
Built from the master product library, %d types, and the zone map, %s links across 114 zones.
Types only. No brands, no retailers. Partner link and Own-label SKU are to be filled.</p></footer>
</main><a class="totop" href="#">Top</a><script>%s</script></body></html>""" % (
        GFONTS, APPX_CSS, appendix_print_css(), len(master), len(master), len(core),
        "%s to %s" % (money(core_lo), money(core_hi)),
        "%s to %s" % (money(lo), money(hi)),
        gapnotes, th, "".join(body), len(master), "{:,}".format(total_pairs), FILTER_JS)


def build_appendix_b_csv(master):
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["Product ID", "Product Type", "Family", "Category", "Primary Purpose",
                "6S Step", "Level", "Standard Qty", "Unit", "Est Retail Low",
                "Est Retail Mid", "Est Retail High", "Zones Using", "Applicable Rooms",
                "Safety / Compatibility", "Partner Link", "Own-Label SKU"])
    for m in sorted(master, key=lambda x: str(x.get("Product ID"))):
        w.writerow([m.get("Product ID"), m.get("Product Standard Name"), m.get("Product Family"),
                    m.get("Category"), m.get("Primary Purpose"), m.get("Supported 6S Phases"),
                    m.get("Required Level"), m.get("Standard Quantity"), m.get("Unit of Measure"),
                    m.get("Estimated Retail Low"), m.get("Estimated Retail Mid"),
                    m.get("Estimated Retail High"), m["_zones_used"], m.get("Applicable Rooms"),
                    m.get("Safety / Compatibility Notes"), "", ""])
    return out.getvalue()


# ---------------------------------------------------------------------------
# print stylesheet
# ---------------------------------------------------------------------------

def appendix_print_css():
    """Minimal paged rules for the two appendices when printed on their own."""
    return """
@page{size:7in 10in;margin:.7in .625in .75in .875in}
@page :right{margin-left:.875in;margin-right:.625in;@bottom-right{content:counter(page);font-family:"Inter",Arial,sans-serif;font-size:9pt}}
@page :left{margin-left:.625in;margin-right:.875in;@bottom-left{content:counter(page);font-family:"Inter",Arial,sans-serif;font-size:9pt}}
@media print{
 html,body{background:#fff!important;color:#000!important;font-size:9.5pt;line-height:1.34}
 .topbar,.totop{display:none!important}
 .book{max-width:none;padding:0}
 p,.lede,.subtitle,footer{max-width:none}
 .masthead{padding:0}
 h1.title{font-size:26pt}
 h2{font-size:15pt;break-after:avoid}
 .summary{display:none}
 .item,.gap{background:#fff!important;border:.5pt solid #000!important;border-radius:0;break-inside:avoid;padding:6pt 8pt;margin:0 0 6pt}
 .item h3{font-size:11pt}
 .item .lvl{background:#fff!important;color:#000!important;border:.5pt solid #000;border-radius:0;font-size:7pt}
 .famhead{border-bottom:1pt solid #000;break-after:avoid;break-inside:avoid;margin:16pt 0 6pt}
 .wrap{overflow:visible;border:0;border-radius:0}
 table{min-width:0;width:100%;font-size:7.2pt;background:#fff!important}
 th{background:#fff!important;color:#000!important;border-bottom:1pt solid #000;position:static;padding:3pt 4pt;font-size:6.8pt}
 td{padding:2.5pt 4pt;border-bottom:.25pt solid #999;background:#fff!important}
 td.blank{background:#fff!important;color:#666!important}
 thead{display:table-header-group}
 tr{break-inside:avoid}
 a{color:inherit;text-decoration:none}
}
"""


def print_css(self_hosted_fonts=False):
    """The 7 x 10 in print stylesheet for the manual.

    Design decisions, all deliberate and all reversible from this one function:

    TRIM      7 x 10 in. Standard print-on-demand size, so no custom-trim
              surcharge, and the widest common trade trim that still reads as a
              book you carry rather than a workbook you leave on a desk. The
              surface-by-surface cleaning tables are two columns of running
              prose; at 6 x 9 the method column wraps to four and five lines a
              row and the extent balloons. At 7 x 10 the text block is 5.5 in
              wide, which holds a 10.5 pt serif at roughly 72 characters a line.

    MARGINS   inside .875 in, outside .625 in, head .7 in, foot .75 in. The inside
              margin carries the gutter allowance for a perfect-bound block over
              300 pages, which is what makes the book usable open on a shelf
              rather than fighting the spine.

    INK       one colour, black, no fills anywhere. A field manual of this extent
              is a print-on-demand product, and colour interiors at 350-plus
              pages are not economic. Every panel, chip and table header is
              converted to a rule or an outline, so the file prints correctly
              without depending on print-color-adjust and without any tint that
              a mono press would screen into mud.

    FOLIOS    drop folios, outside corner, roman in the front matter and arabic
              from the first room. Running heads carry the book name on the
              verso and the current room on the recto. These use CSS paged-media
              margin boxes, which Prince, Antenna House and WeasyPrint honour.
              Chromium does not implement margin boxes, so a Chromium render
              gives the right page count but no folios. That is expected.
    """
    faces = ""
    if self_hosted_fonts:
        faces = FONT_FACE_CSS
    return faces + """
/* =====================================================================
   THE MICRO ZONE MANUAL - PRINT EDITION
   Trim 7 x 10 in (178 x 254 mm), portrait, perfect bound, one colour.
   Screen rendering is untouched: everything below is inside an @page
   block or an @media print block, apart from the two visibility rules
   and the front-matter styling immediately below, which only affect
   elements this build added.
   ===================================================================== */

.print-only{display:none}
.copyright-page,.notice-page{max-width:664px;margin:0 auto;padding:26px 0}
.copyright-page{font-size:15.5px;line-height:1.5;color:var(--soft)}
.copyright-page p{margin:0 0 1em}
.copyright-page b{color:var(--ink)}
.fm-lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;
        color:var(--terra);font-weight:700;margin:0 0 10px}
.fm-h{font-family:var(--display);font-weight:600;font-size:28px;margin:0 0 .6em;letter-spacing:-.01em}
.fm-more p{margin:0 0 1em;font-size:16.5px;line-height:1.5}
.fm-rule{border:0;border-top:1px solid var(--rule2);margin:1.6em 0}

@page{
  size:%(w)gin %(h)gin;
  margin:.70in .625in .75in .875in;      /* head, outside, foot, inside */
}
@page :right{
  margin-left:.875in;margin-right:.625in;
  @top-right{content:string(roomname);font-family:"Inter",Arial,sans-serif;font-size:8pt;
             font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#000;
             vertical-align:bottom;padding-bottom:.18in}
  @bottom-right{content:counter(page);font-family:"Inter",Arial,sans-serif;font-size:9pt;
             color:#000;vertical-align:top;padding-top:.24in}
}
@page :left{
  margin-left:.625in;margin-right:.875in;
  @top-left{content:"The Micro Zone Manual";font-family:"Inter",Arial,sans-serif;font-size:8pt;
             font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#000;
             vertical-align:bottom;padding-bottom:.18in}
  @bottom-left{content:counter(page);font-family:"Inter",Arial,sans-serif;font-size:9pt;
             color:#000;vertical-align:top;padding-top:.24in}
}
/* no folio or running head on the title spread or on a blank verso */
@page :first{@top-right{content:none}@top-left{content:none}
             @bottom-right{content:none}@bottom-left{content:none}}
@page :blank{@top-right{content:none}@top-left{content:none}
             @bottom-right{content:none}@bottom-left{content:none}}
/* a room opener carries its own big heading, so it drops the running head.
   Named-page :first matches the first page of each chapter sequence. */
@page chapter:first{@top-right{content:none}@top-left{content:none}}

/* front matter folios in lower roman */
@page frontmatter{@top-right{content:none}@top-left{content:none}}
@page frontmatter:right{margin-left:.875in;margin-right:.625in;
  @top-right{content:none}
  @bottom-right{content:counter(page,lower-roman);font-family:"Inter",Arial,sans-serif;
                font-size:9pt;vertical-align:top;padding-top:.24in}}
@page frontmatter:left{margin-left:.625in;margin-right:.875in;
  @top-left{content:none}
  @bottom-left{content:counter(page,lower-roman);font-family:"Inter",Arial,sans-serif;
                font-size:9pt;vertical-align:top;padding-top:.24in}}

@media print{

  /* ---------- base ---------- */
  html,body{background:#fff!important;color:#000!important;
            font-family:"Newsreader",Georgia,"Times New Roman",serif;
            font-size:10.5pt;line-height:1.38;
            -webkit-print-color-adjust:economy;print-color-adjust:economy}
  .book{max-width:none;margin:0;padding:0}
  .prose,.what,.defbox,.idea,.checklist,.gloss,footer,.lede,.prose p,
  .roomintro,.subtitle{max-width:none;margin-left:0;margin-right:0}
  p{orphans:3;widows:3;margin:0 0 .55em}
  a{color:#000!important;text-decoration:none}
  abbr{text-decoration:none}

  /* ---------- front matter ---------- */
  .frontmatter{page:frontmatter}
  .print-only{display:block!important}
  .screen-only{display:none!important}
  .halftitle{break-after:page;break-before:avoid;text-align:center;padding-top:2.6in}
  .halftitle .ht-title{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:22pt;margin:0}
  .halftitle .ht-sub{font-style:italic;color:#000;font-size:11pt;margin:.5em 0 0}
  .masthead{break-before:right;break-after:page;padding:2.2in 0 0;text-align:center;max-width:none}
  .masthead h1.title{font-size:38pt;line-height:1.02}
  .masthead .subtitle{font-size:13pt;margin-left:auto;margin-right:auto}
  .copyright-page{break-before:page;break-after:page;font-size:8.6pt;line-height:1.42}
  .copyright-page p{margin:0 0 .7em;max-width:none}
  .notice-page{break-before:right;break-after:page}
  .notice-page .six-s-disclaimer{max-width:none!important;border-left:2pt solid #000!important;
      background:#fff!important;color:#000!important;font-size:9.4pt!important;
      padding:8pt 0 8pt 12pt!important;margin:0 0 12pt!important}
  .notice-page .six-s-disclaimer p{margin-bottom:.6em!important;color:#000!important}
  .fm-lbl{font-family:"Inter",Arial,sans-serif;font-size:7.5pt;font-weight:700;
      letter-spacing:.2em;text-transform:uppercase;margin:0 0 .6em}
  .fm-h{font-family:"Fraunces",Georgia,serif;font-size:19pt;margin:0 0 .5em;break-after:avoid}
  .fm-more{font-size:9.4pt;line-height:1.42}
  .fm-more b{font-family:"Inter",Arial,sans-serif;font-size:8.4pt;letter-spacing:.02em}
  .fm-rule{border:0;border-top:.5pt solid #000;margin:1.2em 0}

  /* ---------- headings and running heads ---------- */
  h1,h2,h3,h4,h5,h6{break-after:avoid;break-inside:avoid;color:#000}
  h2{font-size:16pt;margin:1.4em 0 .45em}
  h2 .kick{font-size:7.5pt;letter-spacing:.2em;color:#000;margin-bottom:.5em}
  h3{font-size:13pt}
  .eyebrow,.chno{color:#000}

  /* ---------- rooms ----------
     Every room opens on a recto, which is how a reference book is used: you
     open it flat at a room and the room starts a spread. Named page "chapter"
     exists only so the opener can drop its running head. footer shares the
     name so no page-name change forces a stray break at the back. */
  .room,footer{page:chapter}
  #entryway{counter-reset:page 1}      /* arabic folios start at room one */
  .room{break-before:right;margin-top:0}
  .roomhead{border-bottom:1.5pt solid #000;padding-bottom:5pt;margin-bottom:9pt;
            break-after:avoid;break-inside:avoid}
  .roomhead h2{font-size:24pt;margin:0;string-set:roomname content(text)}
  .roomstat{font-family:"Inter",Arial,sans-serif;font-size:8.5pt;color:#000}
  .roomintro{font-size:10.5pt;margin-bottom:9pt}
  .tips{display:block;margin:0 0 12pt}
  .tip{background:#fff!important;border:0;border-left:1pt solid #000;border-radius:0;
       padding:0 0 0 8pt;margin:0 0 6pt;font-size:9.2pt;break-inside:avoid}
  .tip b{font-size:7.5pt;color:#000;letter-spacing:.16em}

  /* ---------- zone cards ----------
     A zone card runs well over a page once the cleaning table is in it, so the
     card itself is allowed to break and the blocks inside it are not. */
  .zone{background:#fff!important;border:0;border-top:1.5pt solid #000;border-radius:0;
        padding:7pt 0 10pt;margin:0 0 10pt;break-inside:auto;break-before:auto}
  .zhead{margin-bottom:2pt;break-after:avoid}
  .zmeta{font-family:"Inter",Arial,sans-serif;font-size:8.5pt;color:#000}
  .zmeta b{color:#000}
  .zpurpose{font-size:10pt;margin:0 0 7pt;color:#000;break-after:avoid}
  .done,.call,.watch,.leave,.what,.defbox,.idea,.checklist{break-inside:avoid}
  .done{background:#fff!important;border:.5pt dashed #000;border-radius:0;padding:6pt 8pt;margin:0 0 8pt}
  .done .lbl,.call .lbl,.watch .lbl,.leave .lbl,.clean .lbl,.what h4,.defbox .lbl,
  .idea .lbl,.checklist h4{color:#000;font-size:7.5pt;letter-spacing:.16em}
  .done p{font-size:10pt}
  .call,.watch,.leave,.clean{background:#fff!important;border:0;border-left:1.5pt solid #000;
        border-radius:0;padding:0 0 0 9pt;margin:0 0 8pt}
  .call h5{font-size:10.5pt;margin:0 0 3pt}
  .call p,.watch li,.leave p,.leave .trig{font-size:9.6pt;line-height:1.42}
  .watch li b,.leave .trig b{font-size:7.6pt;color:#000}
  .leave .trig{color:#000}
  /* the cross-reference already reads "See Chapter 25, the ideal-state photo",
     so the decorative arrow is dropped rather than risking a fallback glyph */
  .xref{font-size:8.4pt;color:#000;margin-top:6pt;break-inside:avoid;font-style:italic}
  .xref::before{content:none}

  /* the six passes: outlined chips, never reversed out of a solid, so nothing
     depends on the printer honouring a background */
  .passes{margin:0 0 9pt}
  .passes li{padding-left:78pt;margin:0 0 4pt;font-size:9.8pt;line-height:1.4;
             min-height:0;break-inside:avoid}
  .passes .s{background:#fff!important;color:#000!important;border:.5pt solid #000;
             border-radius:0;font-size:6.8pt;font-weight:700;padding:1pt 3pt;
             letter-spacing:.06em;top:1.5pt;width:70pt;text-align:center}

  /* ---------- the cleaning tables ---------- */
  .clean .sum{font-size:9.6pt;margin:0 0 6pt;break-after:avoid}
  .clean table{font-size:8.6pt;margin:0 0 6pt;background:#fff!important;break-inside:auto}
  .clean thead{display:table-header-group}
  .clean tr{break-inside:avoid}
  .clean th{background:#fff!important;color:#000!important;border-bottom:1pt solid #000;
            padding:2.5pt 4pt 2.5pt 0;font-size:6.8pt;letter-spacing:.1em}
  .clean td{padding:3pt 6pt 3pt 0;border-bottom:.25pt solid #000;background:#fff!important;
            line-height:1.34}
  .clean tr:nth-child(even) td{background:#fff!important}
  .clean td.surf{color:#000;width:30%%}
  .clean h6{font-size:6.8pt;color:#000;letter-spacing:.16em;margin:7pt 0 3pt;break-after:avoid}
  .clean .prod span{background:#fff!important;color:#000!important;border:.5pt solid #000;
            border-radius:0;font-size:7.6pt;padding:.5pt 3pt;margin:0 3pt 3pt 0}
  .clean .inspect li{font-size:9pt;padding-left:11pt;margin:0 0 2pt;break-inside:avoid}
  /* the magnifier emoji does not belong in a one-colour interior */
  .clean .inspect li::before{content:"\\2022";font-size:9pt;top:0;left:2pt}

  /* ---------- back matter ---------- */
  .what,.defbox,.checklist{background:#fff!important;border:.5pt solid #000;border-radius:0;
        padding:8pt 10pt;margin:0 0 10pt}
  .what li{font-size:9.8pt;padding-left:12pt;margin:0 0 3pt}
  .what li::before{background:#000;width:3pt;height:3pt;left:2pt;top:.55em}
  .defbox p,.idea p{font-size:12pt;line-height:1.28}
  .idea{background:#fff!important;color:#000!important;border:1.5pt solid #000;border-radius:0;
        padding:9pt 12pt;margin:0 0 10pt}
  .pull{border-top:1pt solid #000;border-bottom:1pt solid #000;color:#000;font-size:14pt}
  .checklist li{font-size:9.8pt;padding-left:16pt;margin:0 0 4pt}
  .checklist li::before{border:.75pt solid #000;border-radius:0;width:9pt;height:9pt}
  .gloss{columns:2;column-gap:22pt}
  .gloss dt{font-size:10.5pt}
  .gloss dd{font-size:9.4pt;color:#000;line-height:1.36}
  .sixs{display:block}
  .sdef{background:#fff!important;border:0;border-left:1pt solid #000!important;border-radius:0;
        padding:0 0 0 9pt;margin:0 0 6pt;break-inside:avoid}
  .sdef .n{font-size:7.2pt;color:#000}
  .sdef h4{font-size:11pt;margin:0}
  .sdef p{font-size:9.4pt;color:#000}
  footer{border-top:1pt solid #000;color:#000;font-size:8.4pt;margin-top:18pt;padding-top:8pt}

  /* ---------- contents ----------
     Leaders and folios resolve in a paged-media engine. Chromium prints the
     entry without the folio, which is why the vendor PDF is not a browser PDF. */
  .toc{columns:2;column-gap:22pt;background:#fff!important;border:0;border-top:1pt solid #000;
       border-bottom:1pt solid #000;border-radius:0;padding:8pt 0;margin:0 0 10pt}
  .toc a{font-size:9.6pt;margin:0 0 3pt;break-inside:avoid;display:block}
  .toc a span{font-size:7.6pt;color:#000;display:inline;margin-left:.4em}
  .toc a::after{content:leader('.') target-counter(attr(href url),page);
                font-family:"Inter",Arial,sans-serif;font-size:8.4pt}

  /* ---------- bound-in appendices ---------- */
  .appendix{break-before:right;page:chapter}
  .appendix .item{background:#fff!important;border:0;border-top:.5pt solid #000;border-radius:0;
        padding:5pt 0 6pt;margin:0;break-inside:avoid}
  .appendix .item h3{font-size:10.5pt}
  .appendix .item .lvl{background:#fff!important;color:#000!important;border:.5pt solid #000;
        border-radius:0;font-size:6.6pt}
  .appendix .item .purpose{font-size:9.4pt;margin:.2em 0 .3em}
  .appendix .item .meta{font-size:7.8pt;color:#000;gap:2pt 10pt}
  .appendix .item .meta b{color:#000}
  .appendix .item .safety{font-size:7.8pt;color:#000}
  .appendix .item .safety::before{content:"Safety. ";font-weight:700}
  .appendix .famhead{border-bottom:1pt solid #000;margin:14pt 0 5pt;break-after:avoid}
  .appendix .gap{background:#fff!important;border:0;border-left:1.5pt solid #000;border-radius:0;
        padding:0 0 0 9pt;margin:0 0 9pt;font-size:9.2pt}
  .appendix .gap b{color:#000;font-size:7.5pt}
  .appendix .wrap{overflow:visible;border:0;border-radius:0}
  .appendix table{min-width:0;width:100%%;font-size:7.4pt;background:#fff!important}
  .appendix th{background:#fff!important;color:#000!important;border-bottom:1pt solid #000;
        position:static;padding:3pt 4pt 3pt 0;font-size:6.6pt}
  .appendix td{padding:2.5pt 5pt 2.5pt 0;border-bottom:.25pt solid #000;background:#fff!important}
  .appendix td.blank{background:#fff!important;color:#000!important}
  .appendix thead{display:table-header-group}
  .appendix tr{break-inside:avoid}
  .appendix .summary{display:block;margin:0 0 10pt}
  .appendix .card{background:#fff!important;border:0;border-left:1pt solid #000;border-radius:0;
        padding:0 0 0 8pt;margin:0 0 4pt;display:flex;gap:8pt;align-items:baseline}
  .appendix .card .num{font-size:12pt;color:#000}
  .appendix .topbar,.appendix .totop{display:none!important}
}
""" % {"w": TRIM_W_IN, "h": TRIM_H_IN}


FONT_FACE_CSS = ""  # filled by embed_fonts()


def embed_fonts():
    """Return @font-face CSS with the woff2 faces inlined as data URIs.

    The print edition has to be one file a vendor can open with nothing else
    attached, and the whole text of this manual sits inside Latin-1 plus a
    handful of punctuation, so only the base subsets are needed. The Latin
    Extended cuts are deliberately left out: nothing in the book uses them, and
    they would add weight to a file that is already a megabyte.

    Inlining rather than copying also keeps the print folder free of binaries.
    The repository ignores content/**/*.woff2, so a copied font file would not
    survive a checkout and the vendor file would silently lose its typeface.
    """
    global FONT_FACE_CSS
    LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
             "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
    wanted = [("Fraunces", 400, "normal"), ("Fraunces", 500, "normal"),
              ("Fraunces", 600, "normal"), ("Fraunces", 900, "normal"),
              ("Inter", 400, "normal"), ("Inter", 600, "normal"), ("Inter", 700, "normal"),
              ("Newsreader", 400, "normal"), ("Newsreader", 500, "normal"),
              ("Newsreader", 400, "italic")]
    faces = ["/* Typefaces embedded as data URIs. Zero external requests: this file",
             "   renders identically on a machine with no network. */"]
    n = 0
    for fam, w, st in wanted:
        fn = os.path.join(FONT_SRC, "%s-%d-%s.woff2" % (fam, w, st))
        if not os.path.exists(fn):
            continue
        b64 = base64.b64encode(io.open(fn, "rb").read()).decode("ascii")
        faces.append("@font-face{font-family:'%s';font-style:%s;font-weight:%d;"
                     "font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');"
                     "unicode-range:%s}" % (fam, st, w, b64, LATIN))
        n += 1
    FONT_FACE_CSS = "\n".join(faces) + "\n"
    return n


# ---------------------------------------------------------------------------
# front matter
# ---------------------------------------------------------------------------

HALF_TITLE = """<section class="halftitle print-only" aria-hidden="true">
<p class="ht-title">The Micro Zone Manual</p>
<p class="ht-sub">One shelf, one drawer, one corner at a time.</p>
</section>"""

# NOTE FOR PRODUCTION, NOT FOR PRINT: the copyright and notice copy below is
# plain-English scaffolding in the book's voice, adapted for this manual from
# content/book/6S-Success-Front-Matter/FRONT_MATTER.md. It has NOT been reviewed
# by a lawyer. Every bracketed field must be filled and the whole of the notice
# must go to counsel before any commercial release, in every territory of sale.
COPYRIGHT_PAGE = """<section class="copyright-page" id="copyright" aria-label="Copyright and imprint">
<p class="fm-lbl screen-only">Copyright and imprint</p>
<p><b>The Micro Zone Manual</b><br>
One shelf, one drawer, one corner at a time.<br>
6S Success &middot; Home Edition &middot; Companion Volume</p>

<p>Copyright &copy; [YEAR] by [AUTHOR OR RIGHTS HOLDER]. All rights reserved.</p>

<p>No part of this publication may be reproduced, distributed, or transmitted in any form or by
any means, including photocopying, recording, or other electronic or mechanical methods, without
the prior written permission of the publisher, except in the case of brief quotations embodied in
critical reviews and certain other noncommercial uses permitted by copyright law. For permission
requests, write to the publisher at the address below.</p>

<p>First edition, [YEAR]<br>
[PRINTING NUMBER LINE: 10 9 8 7 6 5 4 3 2 1]</p>

<p>ISBN (paperback): [ISBN]<br>
ISBN (ebook): [ISBN]</p>

<p>Published by [IMPRINT OR PUBLISHER NAME]<br>
[PUBLISHER ADDRESS]<br>
[PUBLISHER CONTACT]<br>
[PUBLISHER WEB ADDRESS]</p>

<p>Cover and interior design by [DESIGNER]<br>
Typeset in Fraunces and Newsreader<br>
Printed and bound in [COUNTRY OF MANUFACTURE]<br>
[TERRITORY STATEMENT]</p>

<hr class="fm-rule">

<p>This manual is a companion volume to <i>6S Success: Home Edition</i>. It is a field reference to
114 micro zones across 20 rooms, and it does not re-teach the method. Cross-references in the form
"See Chapter 21, the hazard hunt" point to the main book.</p>

<p>The six steps are Sort, Straighten, Shine, Safety, Standardize, and Sustain, always in that
order. The method is adapted from the industrial 5S practice developed in Japanese manufacturing,
with Safety added as a distinct fourth step. The second step is called Straighten throughout this
series.</p>

<p>This manual names types of product, not brands. Any trademarks, service marks, or product names
that appear are the property of their respective owners and are used for identification only. Their
use does not imply any endorsement, affiliation, or sponsorship in either direction.</p>

<p>Retail figures in the appendices are planning estimates for a type of product, gathered as a
range. They are not quotations, they carry no brand, and they will move.</p>
</section>"""

NOTICE_PAGE_HEAD = """<section class="notice-page" id="before-you-begin" aria-label="Safety notice">
<p class="fm-lbl">Important</p>
<h2 class="fm-h">Read this before you begin</h2>
"""

NOTICE_PAGE_TAIL = """<div class="fm-more">
<hr class="fm-rule">
<p><b>Know your limits, and stop at them.</b> Where a zone card takes you toward structural,
electrical, plumbing, gas, roofing, or carpentry work, the instruction is always to stop and call a
qualified trade. Follow it. If a job requires a licensed trade where you live, use one.</p>

<p><b>Height.</b> Several zones ask you to clear a high shelf, a garage rafter, or the top of a
wardrobe. Use a stable step stool or step ladder on a level surface. Do not stand on furniture, on a
box, or on the top step, and where you can, have another adult in the room.</p>

<p><b>Anything you route out of the house.</b> The bathroom, laundry, garage, and workshop zones all
move things out. Dispose of medicines and hazardous household waste according to your local
authority, your pharmacy take-back scheme, or your national regulator. Local rules differ, and they
take precedence over anything suggested here.</p>

<p><b>Products.</b> This manual names types of product, not brands, and the two appendices list
those types. It does not test, rate, certify, or recommend any particular make. Where a companion
website or resource list carries affiliate links, that relationship is disclosed on the page where
the links appear.</p>

<p><b>Third-party content.</b> Any website address given here was accurate at the time of
publication. Neither the author nor the publisher is responsible for content on other people's
websites.</p>
</div>
</section>"""

FOOTER_ONELINE = ('<p>Use at your own risk. Follow all product and tool instructions, never mix '
                  'cleaning products, and keep chemicals away from children and pets. Not a '
                  'substitute for a qualified professional. The full notice is at the front of this '
                  'manual, under "Read this before you begin".</p>')


# ---------------------------------------------------------------------------
# manual transform
# ---------------------------------------------------------------------------


def extract_disclaimer(doc):
    """Pull the six-s-disclaimer aside out of wherever it currently sits."""
    m = re.search(r'<aside class="six-s-disclaimer".*?</aside>', doc, re.S)
    if not m:
        return doc, None
    return doc[:m.start()] + doc[m.end():], m.group(0)


def transform_manual(doc):
    # --- 1. house style -------------------------------------------------
    doc = normalise_dashes(doc)

    # --- 2. lift the frozen disclaimer out of wherever it currently sits.
    # This has to happen BEFORE the fences are cleared, because on a re-run the
    # block lives inside the SAFETY NOTICE fence.
    doc, disclaimer = extract_disclaimer(doc)
    if disclaimer is None:
        raise SystemExit("FATAL: the six-s-disclaimer block is missing from the manual.")

    # --- 3. clear previous injections so this is idempotent -------------
    for name in ("PRINT STYLESHEET", "HALF TITLE", "COPYRIGHT PAGE", "SAFETY NOTICE",
                 "FOOTER NOTICE"):
        doc = unfence(doc, name)
    doc = doc.replace('<div class="frontmatter">\n', "").replace(
        "\n</div><!-- /frontmatter -->", "")
    # on a first run the aside sat outside </main>; tidy the newline it leaves
    doc = re.sub(r"</main>\s*\n*\s*</body>", "</main>\n</body>", doc)

    # --- 4. retire the old three-rule print block -----------------------
    doc = doc.replace(
        "@media print{body{background:#fff}.room{break-before:page}"
        ".zone{break-inside:avoid;border-color:#ccc}}\n",
        "/* print rules live in the print stylesheet below, see ops/build_manual_print.py */\n")

    # --- 5. print stylesheet --------------------------------------------
    css = fence("PRINT STYLESHEET",
                '<style id="print-edition" media="all">\n%s\n</style>' % print_css())
    doc = doc.replace("</head>", css + "\n</head>", 1)

    # --- 6. front matter -------------------------------------------------
    doc = doc.replace('<body><main class="book">\n',
                      '<body><main class="book">\n<div class="frontmatter">\n'
                      + fence("HALF TITLE", HALF_TITLE) + "\n", 1)

    notice = NOTICE_PAGE_HEAD + disclaimer.strip() + "\n" + NOTICE_PAGE_TAIL
    doc = doc.replace("</header>\n",
                      "</header>\n"
                      + fence("COPYRIGHT PAGE", COPYRIGHT_PAGE) + "\n"
                      + fence("SAFETY NOTICE", notice) + "\n", 1)

    # close the front matter wrapper after the contents nav
    doc = doc.replace("</nav>\n", "</nav>\n</div><!-- /frontmatter -->\n", 1)

    # --- 7. one-line notice in the footer --------------------------------
    doc = doc.replace(
        "<p>The six S's, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. "
        "Safety is the fourth S.</p>",
        "<p>The six S's, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. "
        "Safety is the fourth S.</p>\n" + fence("FOOTER NOTICE", FOOTER_ONELINE), 1)

    return doc


# ---------------------------------------------------------------------------
# bound print edition
# ---------------------------------------------------------------------------


def appendix_body(path, appendix_id, label):
    """Lift the <main> out of an appendix file so it can be bound into the manual."""
    s = read(path)
    m = re.search(r"<main class=\"book\">(.*?)</main>", s, re.S)
    if not m:
        raise SystemExit("FATAL: cannot find the body of %s" % path)
    inner = m.group(1)
    inner = re.sub(r'<header class="masthead">.*?</header>', "", inner, flags=re.S)
    inner = re.sub(r"<script>.*?</script>", "", inner, flags=re.S)
    return ('<section class="room appendix" id="%s">\n'
            '<div class="roomhead"><div><p class="eyebrow">%s</p>'
            '<h2>%s</h2></div></div>\n%s\n</section>' % (appendix_id, label[0], label[1], inner))


def build_print_edition(manual_doc, master):
    n_fonts = embed_fonts()
    doc = manual_doc

    # self-hosted fonts, zero external requests
    doc = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", doc)
    doc = re.sub(r'<link href="https://fonts\.googleapis\.com[^>]*>\s*', "", doc)
    doc = doc.replace('<style id="print-edition" media="all">\n',
                      '<style id="print-edition" media="all">\n' + FONT_FACE_CSS)

    a = appendix_body(OUT_A, "appendix-a", ("Appendix A", "The Complete 6S Home Kit"))
    b = appendix_body(OUT_B, "appendix-b", ("Appendix B", "Inputs and Sourcing List"))

    # bind the appendices in ahead of the footer, and add them to the contents
    doc = doc.replace("</nav>\n", (
        '<a href="#appendix-a">Appendix A<span>The complete kit, %d types</span></a>'
        '<a href="#appendix-b">Appendix B<span>Sourcing list</span></a></nav>\n'
        % len(master)), 1)
    doc = doc.replace("<footer>\n", a + "\n" + b + "\n<footer>\n", 1)
    doc = doc.replace("<title>The Micro Zone Manual - 6S Success Home Edition</title>",
                      "<title>The Micro Zone Manual - print edition, %g x %g in</title>"
                      % (TRIM_W_IN, TRIM_H_IN), 1)
    return doc, n_fonts


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------


def gates(paths, master, zone_products):
    fails = []
    print("\n" + "=" * 68)
    print("GATES")
    print("=" * 68)

    for label, path in paths:
        s = read(path)
        txt = strip_tags(s)
        em = txt.count(EM)
        en = txt.count(EN)
        raw_em = s.count(EM)
        raw_en = s.count(EN)
        brand_hits = {}
        for b in BRANDS:
            c = len(re.findall(r"(?<![A-Za-z])" + re.escape(b) + r"(?![A-Za-z])", txt))
            if c:
                brand_hits[b] = c
        setorder = len(re.findall(r"Set\s+in\s+Order", s, re.I))
        print("\n  %s" % label)
        print("    em dashes        %d  (whole file %d)" % (em, raw_em))
        print("    en dashes        %d  (whole file %d)" % (en, raw_en))
        print("    brand names      %s" % (brand_hits or "none"))
        print("    'Set in Order'   %d" % setorder)
        if raw_em:
            fails.append("%s: %d em dashes" % (label, raw_em))
        if raw_en:
            fails.append("%s: %d en dashes" % (label, raw_en))
        if brand_hits:
            fails.append("%s: brand names %s" % (label, brand_hits))
        if setorder:
            fails.append("%s: uses 'Set in Order', the term is Straighten" % label)

        if "Manual" in label or "manual" in label or "PRINT" in label:
            zones = len(re.findall(r'<article class="zone"', s))
            rooms = len(re.findall(r'<section class="room"[^>]*id="(?!appendix)', s))
            print("    zone cards       %d" % zones)
            print("    room sections    %d" % rooms)
            if zones != 114:
                fails.append("%s: %d zone cards, expected 114" % (label, zones))
            # six-S canon: Safety must be the fourth S in every enumerated run
            runs = re.findall(
                r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)"
                r"(?:\s*(?:,|and|&|\u00b7|>|/)\s*"
                r"(?:Sort|Straighten|Shine|Safety|Standardize|Sustain)){3,}", txt)
            S = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]
            bad = []
            for r in runs:
                seq = re.findall(r"Sort|Straighten|Shine|Safety|Standardize|Sustain", r)
                if len(seq) >= 5 and seq[:6] != S[:len(seq)]:
                    bad.append(r.strip()[:70])
            print("    six-S runs       %d checked, %d bad" % (len(runs), len(bad)))
            if bad:
                fails.append("%s: Safety not 4th in %s" % (label, bad[:2]))
            has_notice = 'id="before-you-begin"' in s
            has_copyright = 'id="copyright"' in s
            # the notice must sit in the front third of the document
            pos = s.find('id="before-you-begin"') / float(len(s)) if has_notice else 1.0
            print("    copyright page   %s" % ("present" if has_copyright else "MISSING"))
            print("    safety notice    %s, at %.1f%% of the document"
                  % ("present" if has_notice else "MISSING", pos * 100))
            if not has_copyright:
                fails.append("%s: no copyright page" % label)
            if not has_notice or pos > 0.10:
                fails.append("%s: safety notice missing or not near the front" % label)
            print("    @page rules      %d" % len(re.findall(r"@page", s)))
            if "@page" not in s:
                fails.append("%s: no @page rule" % label)
        else:
            ids = len(set(re.findall(r"MPL-\d{5}", s)))
            print("    product types    %d" % ids)
            if ids and ids != len(master):
                fails.append("%s: %d product refs, expected %d" % (label, ids, len(master)))

        for tag in ("section", "article", "div", "ul", "li", "dl", "nav", "main", "aside", "table"):
            o = len(re.findall(r"<%s[\s>]" % tag, s))
            c = len(re.findall(r"</%s>" % tag, s))
            if o != c:
                fails.append("%s: unbalanced <%s> %d open / %d close" % (label, tag, o, c))

    print("\n  Library")
    print("    product types    %d" % len(master))
    print("    zones in map     %d" % len(zone_products))
    print("    zone-type links  %d" % sum(len(v) for v in zone_products.values()))
    if len(master) != 123:
        fails.append("library is %d types, expected 123" % len(master))
    if len(zone_products) != 114:
        fails.append("zone map has %d zones, expected 114" % len(zone_products))

    print("\n" + "=" * 68)
    if fails:
        print("FAILED %d gate(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("ALL GATES PASSED")
    return 0


# ---------------------------------------------------------------------------
# page-extent measurement
# ---------------------------------------------------------------------------

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def measure(path, tag, outdir):
    """Render with headless Chromium and count pages. Chromium honours @page
    size and margin, so the extent is real. It ignores margin boxes, so the
    render has no folios; the vendor PDF comes from a paged-media engine."""
    if not os.path.exists(EDGE):
        print("  (no Chromium available, skipping page count for %s)" % tag)
        return None
    pdf = os.path.join(outdir, tag + ".pdf")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=30000",
                    "--print-to-pdf=" + pdf, "--print-to-pdf-no-header",
                    "file:///" + path.replace("\\", "/")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    if not os.path.exists(pdf):
        return None
    data = io.open(pdf, "rb").read()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    boxes = set(re.findall(rb"/MediaBox\s*\[[^\]]*\]", data))
    print("  %-28s %4d pages   %s" % (tag, pages, ", ".join(b.decode() for b in boxes)))
    return pages


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main():
    do_measure = "--measure" in sys.argv

    print("=" * 68)
    print("THE MICRO ZONE MANUAL  |  print build  |  %g x %g in" % (TRIM_W_IN, TRIM_H_IN))
    print("=" * 68)

    # --- product library ------------------------------------------------
    master, zone_products, used, stale = load_library()
    by_family = group_families(master)
    total_pairs = sum(len(v) for v in zone_products.values())
    unmapped = [m for m in master if m["_zones_used"] == 0]
    shine = close_shine_gaps(master)
    closed = [g for g in shine if g["status"].startswith("Closed")]

    print("\nLIBRARY")
    print("  types                %d" % len(master))
    print("  families             %d  %s" % (len(by_family), list(by_family)))
    print("  zone-to-type links   %d across %d zones" % (total_pairs, len(zone_products)))
    print("  stale _zone_count    %d records, recomputed from the zone map" % len(stale))
    for pid, name, was, now in stale:
        print("      %s %-38s was %s, is %s" % (pid, str(name)[:38], was, now))
    print("  unmapped types       %d  %s" % (len(unmapped),
                                             [m["Product ID"] for m in unmapped]))
    print("  Shine gaps closed    %d of %d" % (len(closed), len(shine)))

    notes = [
        "Counts of zones per type are recomputed from the zone map at build time. The "
        "_zone_count field carried in the source library was frozen at an earlier catalog "
        "state and understates ten of the cleaning tools.",
        "Cleaning coverage is no longer the thin spot it was. The library now carries %d "
        "cleaning supplies and %d cleaning tools, against nine in total when the deepened "
        "cleaning pass was written." % (len(by_family.get("Cleaning Supplies", [])),
                                        len(by_family.get("Cleaning Tools", []))),
        "The twelve types in Visual Controls and Safety carry a descriptive phrase in their "
        "category field where every other family carries a category label. It is a data "
        "defect in the source library, not a difference in kind, and it is left visible here "
        "rather than papered over.",
        "Decor is still absent from the library. See the flagged Decor section.",
    ]

    print("\nAPPENDICES")
    write(OUT_A, build_appendix_a(master, by_family, unmapped, shine, notes, total_pairs))
    write(OUT_B, build_appendix_b(master, by_family, notes, total_pairs))
    io.open(OUT_B_CSV, "w", encoding="utf-8-sig", newline="").write(build_appendix_b_csv(master))
    print("  wrote %s" % os.path.relpath(OUT_A, ROOT))
    print("  wrote %s" % os.path.relpath(OUT_B, ROOT))
    print("  wrote %s" % os.path.relpath(OUT_B_CSV, ROOT))

    # --- source content.json --------------------------------------------
    cj = read(CONTENT_JSON)
    cj2 = normalise_dashes(cj)
    if cj2 != cj:
        write(CONTENT_JSON, cj2)
        print("\nSOURCE\n  normalised %d en dashes in content.json"
              % (cj.count(EN) - cj2.count(EN)))
    else:
        print("\nSOURCE\n  content.json already clean")

    # --- the manual -------------------------------------------------------
    print("\nMANUAL")
    doc = read(MANUAL)
    before_en = doc.count(EN)
    doc = transform_manual(doc)
    write(MANUAL, doc)
    write(PUBLISHABLE, doc)
    print("  normalised %d en dashes" % before_en)
    print("  injected print stylesheet, half title, copyright page, safety notice")
    print("  wrote %s" % os.path.relpath(MANUAL, ROOT))
    print("  wrote %s" % os.path.relpath(PUBLISHABLE, ROOT))

    # --- bound print edition ----------------------------------------------
    print("\nPRINT EDITION")
    pdoc, n_fonts = build_print_edition(doc, master)
    write(OUT_PRINT, pdoc)
    print("  embedded %d typeface cuts as data URIs, zero external requests" % n_fonts)
    print("  wrote %s" % os.path.relpath(OUT_PRINT, ROOT))

    # --- gates -------------------------------------------------------------
    rc = gates([("Manual", MANUAL),
                ("PRINT edition", OUT_PRINT),
                ("Appendix A", OUT_A),
                ("Appendix B", OUT_B)], master, zone_products)

    # --- extent ------------------------------------------------------------
    if do_measure:
        print("\n" + "=" * 68)
        print("PAGE EXTENT  (headless Chromium, real pagination)")
        print("=" * 68)
        # measurement PDFs are throwaway and must not land in the repository:
        # content/**/*.pdf is git-ignored, so anything written there disappears
        # on the next clean and looks like data loss.
        outdir = tempfile.mkdtemp(prefix="6s-manual-extent-")
        print("  scratch: %s" % outdir)
        measure(MANUAL, "manual-7x10", outdir)
        measure(OUT_PRINT, "print-edition-7x10", outdir)
        measure(OUT_A, "appendix-a-7x10", outdir)
        measure(OUT_B, "appendix-b-7x10", outdir)

    return rc


if __name__ == "__main__":
    sys.exit(main())
