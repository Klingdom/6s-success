# SUPERSEDED. The appendix builder now lives in ops/build_manual_print.py, which
# reads the 123-type library from ./products.json and ./zone_products.json and
# writes into ../appendices/. This file built the old 97-type appendices from a
# scratch directory that no longer exists. Kept for reference only.
# -*- coding: utf-8 -*-
"""Build Appendix A (The Complete 6S Home Kit) and Appendix B (Inputs & Sourcing List)
from the product library, in the book design system. Also emits Appendix B as CSV."""
import json, io, re, html as H, os, csv, collections

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
PKGDIR = r"C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\appendices"
OUT_A = PKGDIR + r"\Appendix A - The Complete 6S Home Kit.html"
OUT_B = PKGDIR + r"\Appendix B - Inputs and Sourcing List.html"
CSV_B = PKGDIR + r"\Appendix B - Inputs and Sourcing List.csv"

master = json.load(io.open(SCRATCH + r"\products.json", encoding="utf-8"))["master"]
zone_products = json.load(io.open(SCRATCH + r"\zone_products.json", encoding="utf-8"))
try:
    shine_gaps = json.load(io.open(SCRATCH + r"\shine_gaps.json", encoding="utf-8"))
except FileNotFoundError:
    shine_gaps = []
# classify each Shine-implied input: already in the library (needs wider zone mapping)
# vs genuinely new (add to the catalog)
_libnames = [str(m.get("Product Standard Name") or "").lower() for m in master]
def _in_library(name):
    n = name.lower()
    return any(n in ln or ln in n or (len(set(n.split()) & set(ln.split())) >= 2) for ln in _libnames)
for g in shine_gaps:
    g["status"] = "In library, map to more zones" if _in_library(g["item"]) else "New, add to catalog"

def esc(s): return H.escape("" if s is None else str(s).strip(), quote=False)
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def money(x):
    v = num(x); return ("$%.2f" % v) if v is not None else ""

# ----- family display order and which are "gaps" -----
FAMILY_ORDER = ["Cleaning Supplies", "Cleaning Tools", "Storage & Organization",
                "Sort & Routing", "Visual Controls", "Visual Controls & Safety", "Safety"]
# categories the user asked for that the library does not yet cover -> flagged placeholders
GAP_SECTIONS = [
    ("Decor", "Decor was requested but is not yet in the product library. Populate with the framed prints, plants, textiles, and finishing pieces that complete a zone once it is reset, each tied to the rooms where it applies."),
]
GAP_NOTES = [
    "Cleaning coverage is thin: the library holds 5 cleaning supplies and 4 cleaning tools. The deepened Shine pass in the manual references surface-specific cleaning that will need more inputs than these nine. Grow this family as the Shine methods are finalized.",
    "Decor is requested but absent from the library today; see the flagged Decor section.",
]

for m in master:
    m["_fam"] = m.get("Product Family") or "Other"
by_family = collections.OrderedDict()
for fam in FAMILY_ORDER:
    items = [m for m in master if m["_fam"] == fam]
    if items:
        by_family[fam] = items
for m in master:
    if m["_fam"] not in by_family:
        by_family.setdefault(m["_fam"], []).append(m)

TOTAL = len(master)
FALLBACK_MID = sum(num(m.get("Estimated Retail Mid")) or 0 for m in master)

# ---------- shared CSS (book design system) ----------
CSS = """
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
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.4em}
p{margin:0 0 1em;max-width:720px}
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule2);padding:9px 24px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:15px;margin-right:auto}
.topbar input{font-family:var(--sans);font-size:14px;padding:7px 11px;border:1px solid var(--rule2);border-radius:8px;background:var(--panel);color:var(--ink);min-width:220px}
.topbar a{font-family:var(--sans);font-size:12.5px;color:var(--slate);text-decoration:none;padding:4px 8px;border-radius:6px}
.topbar a:hover{background:var(--panel)}
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
@media print{.topbar,.totop{display:none}.item{break-inside:avoid}}
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

def fam_slug(f): return re.sub(r"[^a-z0-9]+","-",f.lower()).strip("-")

def phases(m): return esc(m.get("Supported 6S Phases"))
def lvl_class(m):
    l = (m.get("Required Level") or "Recommended").lower()
    return l if l in ("core","recommended","situational") else "recommended"

# ============ APPENDIX A, the categorized reference ============
def appendix_a():
    fam_nav = "".join('<a href="#%s">%s</a>' % (fam_slug(f), esc(f)) for f in by_family)
    for label,_ in GAP_SECTIONS:
        fam_nav += '<a href="#%s">%s</a>' % (fam_slug(label), esc(label))
    if shine_gaps:
        fam_nav += '<a href="#shine-implied">Shine-Implied</a>'
    secs = []
    for fam, items in by_family.items():
        rows = []
        for m in sorted(items, key=lambda x: (str(x.get("Category")), str(x.get("Product Standard Name")))):
            safety = m.get("Safety / Compatibility Notes")
            rows.append(f"""<div class="item" data-row><div class="top">
<h3>{esc(m.get('Product Standard Name'))}</h3>
<span class="lvl {lvl_class(m)}">{esc(m.get('Required Level'))}</span></div>
<p class="purpose">{esc(m.get('Primary Purpose'))}</p>
<div class="meta"><span><b>Category:</b> {esc(m.get('Category'))}</span>
<span><b>6S phase:</b> {phases(m)}</span>
<span><b>Standard qty:</b> {esc(m.get('Standard Quantity'))} {esc(m.get('Unit of Measure'))}</span>
<span><b>Used in:</b> {esc(m.get('_zone_count'))} of 114 zones</span>
<span><b>Rooms:</b> {esc(m.get('Applicable Rooms'))}</span></div>
{f'<div class="safety">{esc(safety)}</div>' if safety else ''}</div>""")
        secs.append(f"""<section data-fam id="{fam_slug(fam)}"><div class="famhead"><h2>{esc(fam)}</h2>
<span class="n">{len(items)} standard{'s' if len(items)!=1 else ''}</span></div>{''.join(rows)}</section>""")
    for label, desc in GAP_SECTIONS:
        secs.append(f"""<section data-fam id="{fam_slug(label)}"><div class="famhead"><h2>{esc(label)}</h2>
<span class="n">to populate</span></div>
<div class="gap"><b>Gap &middot; not yet in the library</b>{esc(desc)}</div></section>""")
    # Shine-implied inputs the deepened cleaning pass references
    if shine_gaps:
        rows = "".join(
            "<tr data-row><td>%s</td><td>%s</td><td style='white-space:nowrap'>%s</td></tr>"
            % (esc(g["item"]), esc(g["zones"]), esc(g["status"])) for g in shine_gaps)
        secs.append(f"""<section data-fam id="shine-implied"><div class="famhead"><h2>Shine-Implied Inputs</h2>
<span class="n">{len(shine_gaps)} candidates</span></div>
<div class="gap"><b>Gap &middot; surfaced by the deepened Shine pass</b>The room-by-room cleaning methods in the manual reference these inputs. Some already exist in the library and simply need mapping to more zones; the rest are new items to add so the catalog matches what the cleaning actually requires.</div>
<div class="wrap"><table><thead><tr><th>Implied input</th><th>Zones referencing it</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div></section>""")
    gapnotes = "".join('<div class="gap"><b>Gap</b>%s</div>' % esc(g) for g in GAP_NOTES)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Appendix A - The Complete 6S Home Kit</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="topbar"><span class="brand">Appendix A &middot; The Complete 6S Home Kit</span>
<input id="f" type="search" placeholder="Filter items, rooms, uses..." aria-label="Filter">
<span class="count" id="c"></span>{fam_nav}</div>
<main class="book">
<header class="masthead"><p class="chno">6S Success &middot; Home Edition &middot; Companion Volume</p>
<p class="eyebrow">Appendix A</p><h1 class="title">The Complete 6S Home Kit</h1>
<p class="subtitle">Every cleaning supply, tool, storage, organization, and visual-control standard used to 6S the house, by category.</p></header>
<p class="lede">These are the {TOTAL} product standards behind the Micro Zone Manual: what each one is, what it does, which 6S step it serves, how many of the 114 zones use it, and where. Categories the library does not yet cover are flagged so the kit can grow.</p>
<section class="summary">
<div class="card"><div class="num">{TOTAL}</div><b>Product standards</b></div>
<div class="card"><div class="num">{len(by_family)}</div><b>Families</b></div>
<div class="card"><div class="num">114</div><b>Zones covered</b></div>
<div class="card"><div class="num">20</div><b>Rooms</b></div>
</section>
{gapnotes}
{''.join(secs)}
<footer><p><b>Appendix A &middot; The Complete 6S Home Kit</b> &middot; Companion to 6S Success: Home Edition. Built from the Master Product Library v2.</p></footer>
</main><a class="totop" href="#">Top</a><script>{FILTER_JS}</script></body></html>"""

# ============ APPENDIX B, the sourcing / procurement list ============
def appendix_b():
    COLS = ["ID","Product standard","Family","Category","Purpose","6S phase","Level",
            "Qty","Unit","Est. low","Est. mid","Est. high","Safety / compatibility",
            "Partner link","Own-label SKU"]
    body = []
    for fam in list(by_family) :
        items = by_family[fam]
        body.append('<tr data-fam><td colspan="%d" style="background:#efe7d6;font-weight:700;color:var(--slate)">%s (%d)</td></tr>' % (len(COLS), esc(fam), len(items)))
        for m in sorted(items, key=lambda x: str(x.get("Product ID"))):
            body.append("<tr data-row>"
                + "<td class='id'>%s</td>" % esc(m.get("Product ID"))
                + "<td>%s</td>" % esc(m.get("Product Standard Name"))
                + "<td>%s</td>" % esc(m.get("Product Family"))
                + "<td>%s</td>" % esc(m.get("Category"))
                + "<td>%s</td>" % esc(m.get("Primary Purpose"))
                + "<td>%s</td>" % phases(m)
                + "<td>%s</td>" % esc(m.get("Required Level"))
                + "<td>%s</td>" % esc(m.get("Standard Quantity"))
                + "<td>%s</td>" % esc(m.get("Unit of Measure"))
                + "<td>%s</td>" % money(m.get("Estimated Retail Low"))
                + "<td>%s</td>" % money(m.get("Estimated Retail Mid"))
                + "<td>%s</td>" % money(m.get("Estimated Retail High"))
                + "<td>%s</td>" % esc(m.get("Safety / Compatibility Notes"))
                + "<td class='blank'>to add</td><td class='blank'>to add</td></tr>")
    gapnotes = "".join('<div class="gap"><b>Gap</b>%s</div>' % esc(g) for g in GAP_NOTES)
    th = "".join("<th>%s</th>" % esc(c) for c in COLS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Appendix B - Inputs and Sourcing List</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="topbar"><span class="brand">Appendix B &middot; Inputs &amp; Sourcing List</span>
<input id="f" type="search" placeholder="Filter inputs..." aria-label="Filter">
<span class="count" id="c"></span></div>
<main class="book">
<header class="masthead"><p class="chno">6S Success &middot; Home Edition &middot; Companion Volume</p>
<p class="eyebrow">Appendix B</p><h1 class="title">Inputs &amp; Sourcing List</h1>
<p class="subtitle">Every input the micro-zone 6S process consumes, as a procurement sheet, with columns ready for partner links or own-label SKUs.</p></header>
<p class="lede">The same {TOTAL} standards as a sourcing table: purpose, 6S phase, standard quantity, estimated retail range, and safety notes, plus two blank columns, Partner link and Own-label SKU, to fill as the product line is built. The full table is also provided as a CSV for spreadsheet and affiliate-management use.</p>
{gapnotes}
<div class="wrap"><table><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>
<footer><p><b>Appendix B &middot; Inputs &amp; Sourcing List</b> &middot; Companion to 6S Success: Home Edition. Built from the Master Product Library v2. Prices are estimated retail; Partner link and Own-label SKU are to be filled.</p></footer>
</main><a class="totop" href="#">Top</a><script>{FILTER_JS}</script></body></html>"""

os.makedirs(PKGDIR, exist_ok=True)
io.open(OUT_A, "w", encoding="utf-8").write(appendix_a())
io.open(OUT_B, "w", encoding="utf-8").write(appendix_b())

# CSV for Appendix B
with io.open(CSV_B, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["Product ID","Product Standard","Family","Category","Primary Purpose",
                "6S Phase","Level","Standard Qty","Unit","Est Retail Low","Est Retail Mid",
                "Est Retail High","Safety / Compatibility","Partner Link","Own-Label SKU"])
    for m in master:
        w.writerow([m.get("Product ID"), m.get("Product Standard Name"), m.get("Product Family"),
                    m.get("Category"), m.get("Primary Purpose"), m.get("Supported 6S Phases"),
                    m.get("Required Level"), m.get("Standard Quantity"), m.get("Unit of Measure"),
                    m.get("Estimated Retail Low"), m.get("Estimated Retail Mid"),
                    m.get("Estimated Retail High"), m.get("Safety / Compatibility Notes"), "", ""])

print("wrote Appendix A:", OUT_A)
print("wrote Appendix B:", OUT_B)
print("wrote CSV:", CSV_B)
print("products: %d  families: %d" % (TOTAL, len(by_family)))
