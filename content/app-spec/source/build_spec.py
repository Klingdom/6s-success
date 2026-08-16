# -*- coding: utf-8 -*-
"""Assemble the rebuilt 6S Home Reset Product Spec & Store Release Plan into a
navigable HTML document in the book design system."""
import json, io, re, html as H, os

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
OUTDIR = r"C:\Users\philk\Desktop\6S-Home-Reset-Product-Spec"
OUT = OUTDIR + r"\6S Home Reset - Product Specification and Store Release Plan.html"

data = json.load(io.open(SCRATCH + r"\spec.json", encoding="utf-8"))
units = data["units"] if isinstance(data, dict) else data

# unit order (matches the workflow UNITS order)
UNIT_ORDER = ["U1","U2","U3","U4","U5","U6","U7","U8","U9","U10","U11","U12"]
by_id = {u["unit"]: u for u in units if u.get("unit")}
ordered_units = [by_id[i] for i in UNIT_ORDER if i in by_id] + \
                [u for u in units if u.get("unit") not in UNIT_ORDER]

def esc(s): return H.escape("" if s is None else str(s), quote=False)
def slug(s): return re.sub(r"[^a-z0-9]+","-",str(s).lower()).strip("-")

def render_block(b):
    t = b.get("type")
    if t == "p":
        return "<p>%s</p>" % esc(b.get("text"))
    if t == "h3":
        return "<h3>%s</h3>" % esc(b.get("text"))
    if t == "bullets":
        return "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(i) for i in (b.get("items") or []))
    if t == "table":
        hs = b.get("headers") or []
        th = "".join("<th>%s</th>" % esc(h) for h in hs)
        rows = ""
        for r in (b.get("rows") or []):
            rows += "<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r)
        return '<div class="wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, rows)
    if t == "callout":
        v = (b.get("variant") or "note")
        v = v if v in ("tip","win","mistake","note","idea") else "note"
        lbl = esc(b.get("label") or v.title())
        if v == "idea":
            return '<div class="idea"><div class="lbl">%s</div><p>%s</p></div>' % (lbl, esc(b.get("text")))
        return '<aside class="callout %s"><div class="lbl"><span class="dot"></span>%s</div><p>%s</p></aside>' % (v, lbl, esc(b.get("text")))
    if t == "stats":
        cards = "".join('<div class="scard"><div class="num">%s</div><b>%s</b></div>'
                        % (esc(i.get("num")), esc(i.get("label"))) for i in (b.get("items") or []))
        return '<div class="statband">%s</div>' % cards
    if t == "kv":
        rows = "".join('<div class="kvrow"><div class="k">%s</div><div class="v">%s</div></div>'
                       % (esc(p.get("k")), esc(p.get("v"))) for p in (b.get("pairs") or []))
        return '<div class="kv">%s</div>' % rows
    # unknown block: render its text if any
    if b.get("text"):
        return "<p>%s</p>" % esc(b.get("text"))
    return ""

# flatten sections in order, assign numbers within Part I / II, front = unnumbered
sections = []
for u in ordered_units:
    for s in (u.get("sections") or []):
        sections.append(s)

part_labels = {"front": "", "I": "Part I · Current-State Specification",
               "II": "Part II · App Store & Google Play Release Spec",
               "III": "Part III · MVP Beta Build Plan",
               "IV": "Part IV · Usability, Data & Visualization"}
# numbering: front sections unnumbered; Parts I, II, III numbered continuously 1..N
num = 0
for s in sections:
    if s.get("part") in ("I", "II", "III", "IV"):
        num += 1
        s["_num"] = num
    else:
        s["_num"] = None
    s["_id"] = slug((("%02d " % s["_num"]) if s["_num"] else "") + (s.get("title") or ""))

# build TOC grouped by part
def toc_html():
    groups = [("front", "Overview"), ("I", part_labels["I"]), ("II", part_labels["II"]),
              ("III", part_labels["III"]), ("IV", part_labels["IV"])]
    out = []
    for pk, plabel in groups:
        items = [s for s in sections if s.get("part") == pk]
        if not items:
            continue
        links = "".join('<a href="#%s">%s%s%s</a>' % (
            s["_id"],
            ('<span class="tn">%02d</span>' % s["_num"]) if s["_num"] else '',
            esc(s.get("title")),
            ' <span class="newtag">new</span>' if s.get("is_new") else '')
            for s in items)
        out.append('<div class="tocgroup"><h4>%s</h4>%s</div>' % (esc(plabel or "Overview"), links))
    return "".join(out)

# render section bodies, grouped with part dividers
def body_html():
    out = []
    last_part = None
    for s in sections:
        pk = s.get("part")
        if pk in ("I","II","III","IV") and pk != last_part:
            out.append('<div class="partdiv" id="part-%s"><span class="pl">%s</span></div>'
                       % (pk, esc(part_labels[pk])))
            last_part = pk
        blocks = "".join(render_block(b) for b in (s.get("blocks") or []))
        numtag = ('<span class="secnum">%02d</span>' % s["_num"]) if s["_num"] else ''
        newtag = ' <span class="newtag">new</span>' if s.get("is_new") else ''
        out.append('<section class="sec" id="%s"><h2>%s%s%s</h2>%s</section>'
                   % (s["_id"], numtag, esc(s.get("title")), newtag, blocks))
    return "".join(out)

n_sec = len(sections)
n_new = sum(1 for s in sections if s.get("is_new"))

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--honey:#DDA63A;--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:20px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17.5px;line-height:1.6}
.layout{display:grid;grid-template-columns:288px 1fr;max-width:1300px;margin:0 auto;gap:0}
/* sidebar TOC */
.side{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:26px 20px 40px;border-right:1px solid var(--rule2);background:var(--panel)}
.side .brand{font-family:var(--display);font-weight:700;font-size:16px;color:var(--ink);line-height:1.15;margin-bottom:2px}
.side .brandsub{font-family:var(--sans);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-weight:600;margin-bottom:18px}
.tocgroup{margin-bottom:16px}
.tocgroup h4{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:14px 0 6px;border-bottom:1px solid var(--rule);padding-bottom:5px}
.tocgroup a{display:block;font-family:var(--sans);font-size:13px;color:var(--ink);text-decoration:none;padding:4px 6px;border-radius:6px;line-height:1.35}
.tocgroup a:hover{background:#fff;color:var(--terra)}
.tocgroup a.active{background:#fff;color:var(--terra);font-weight:600}
.tn{display:inline-block;min-width:20px;font-variant-numeric:tabular-nums;color:var(--soft);font-weight:600}
.newtag{font-family:var(--sans);font-size:8.5px;letter-spacing:.1em;text-transform:uppercase;background:var(--honey);color:#4a3610;padding:1px 5px;border-radius:8px;font-weight:700;vertical-align:middle}
/* main */
main{padding:0 46px 140px;min-width:0}
.masthead{padding:56px 0 20px;border-bottom:3px solid var(--terra);margin-bottom:8px}
.chno{font-family:var(--sans);font-weight:600;font-size:12px;letter-spacing:.18em;color:var(--slate);text-transform:uppercase;margin:0 0 14px}
.confidential{color:var(--spark)}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(34px,5vw,52px);line-height:1.03;letter-spacing:-.015em;margin:.1em 0 .2em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(18px,2.4vw,22px);margin:0 0 10px;max-width:640px}
.docmeta{font-family:var(--sans);font-size:12.5px;color:var(--soft);letter-spacing:.02em}
.partdiv{margin:56px 0 8px;padding:12px 0;border-top:2px solid var(--rule2);border-bottom:2px solid var(--rule2)}
.partdiv .pl{font-family:var(--display);font-weight:700;font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:var(--terra)}
.sec{padding:22px 0;border-bottom:1px solid var(--rule)}
h2{font-family:var(--display);font-weight:600;font-size:clamp(23px,3vw,30px);line-height:1.12;margin:.2em 0 .5em;letter-spacing:-.01em;scroll-margin-top:16px}
.secnum{display:inline-block;font-family:var(--sans);font-size:15px;font-weight:700;color:var(--terra);background:#f6e2da;border-radius:8px;padding:1px 9px;margin-right:12px;vertical-align:middle}
h3{font-family:var(--display);font-weight:600;font-size:20px;margin:1.4em 0 .4em;color:var(--slate)}
p{margin:0 0 1em;max-width:820px}
ul{max-width:820px;margin:0 0 1em;padding-left:22px}
li{margin:.35em 0}
.statband{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:1.4em 0}
.scard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 16px}
.scard .num{font-family:var(--display);font-size:26px;font-weight:700;color:var(--green);line-height:1}
.scard b{font-family:var(--sans);font-size:11.5px;letter-spacing:.4px;text-transform:uppercase;color:var(--soft);display:block;margin-top:4px}
.wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;margin:1.3em 0;max-width:100%}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:13.5px;background:var(--panel);min-width:520px}
th{background:var(--slate);color:var(--paper);text-align:left;padding:9px 12px;font-weight:600;font-size:12px;letter-spacing:.02em}
td{padding:9px 12px;border-bottom:1px solid var(--rule);vertical-align:top;line-height:1.45}
tr:nth-child(even) td{background:#faf6ee}
.callout{border:1px solid var(--rule);border-left:5px solid var(--terra);background:var(--panel);border-radius:0 12px 12px 0;padding:16px 20px;margin:1.4em 0;max-width:820px}
.callout .lbl{font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);display:flex;align-items:center;gap:8px;margin-bottom:6px}
.callout p{margin:0;font-size:16px}
.callout .dot{width:8px;height:8px;border-radius:50%;background:currentColor;display:inline-block}
.callout.tip{border-left-color:var(--slate)}.callout.tip .lbl{color:var(--slate)}
.callout.win{border-left-color:var(--green)}.callout.win .lbl{color:var(--green)}
.callout.mistake{border-left-color:var(--spark)}.callout.mistake .lbl{color:var(--spark)}
.callout.note{border-left-color:var(--honey)}.callout.note .lbl{color:#B5811E}
.idea{background:var(--ink);color:var(--paper);border-radius:16px;padding:24px 28px;margin:1.6em 0;max-width:820px}
.idea .lbl{font-family:var(--sans);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--honey);font-weight:700;margin-bottom:8px}
.idea p{margin:0;font-family:var(--display);font-weight:500;font-size:20px;line-height:1.3}
.kv{border:1px solid var(--rule);border-radius:12px;overflow:hidden;margin:1.3em 0;max-width:820px}
.kvrow{display:grid;grid-template-columns:210px 1fr}
.kvrow:nth-child(even){background:var(--panel)}
.kvrow .k{font-family:var(--sans);font-size:12.5px;font-weight:700;color:var(--slate);padding:9px 14px;border-right:1px solid var(--rule)}
.kvrow .v{padding:9px 14px;font-size:15px}
.mobmenu{display:none}
@media(max-width:920px){.layout{grid-template-columns:1fr}.side{display:none}main{padding:0 22px 90px}
.statband{grid-template-columns:1fr 1fr}.kvrow{grid-template-columns:1fr}.kvrow .k{border-right:0;border-bottom:1px solid var(--rule)}}
@media print{.side{display:none}.layout{grid-template-columns:1fr}main{padding:0}.sec{break-inside:avoid}.partdiv{break-before:page}}
"""

JS = """
(function(){
 var links=[].slice.call(document.querySelectorAll('.tocgroup a'));
 var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
 var secs=[].slice.call(document.querySelectorAll('.sec'));
 var obs=new IntersectionObserver(function(es){
   es.forEach(function(e){if(e.isIntersecting){
     links.forEach(function(a){a.classList.remove('active');});
     var a=map[e.target.id];if(a)a.classList.add('active');}});
 },{rootMargin:'-10% 0px -80% 0px'});
 secs.forEach(function(s){obs.observe(s);});
})();
"""

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>6S Home Reset - Product Specification & Store Release Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="layout">
<nav class="side">
<div class="brand">6S Home Reset</div>
<div class="brandsub">Product Spec &amp; Store Plan</div>
{toc_html()}
</nav>
<main>
<header class="masthead">
<p class="chno"><span class="confidential">Confidential working draft</span> &middot; 6S Success Product Documentation</p>
<h1 class="title">Product Specification &amp; Store Release Plan</h1>
<p class="subtitle">6S Home Reset. Room by room, zone by zone.</p>
<p class="docmeta">Version 1.1 &middot; rebuilt {esc(data.get('date','2026-07-22'))} &middot; {n_sec} sections ({n_new} new) &middot; Part I documents the validated v2.4 artifact; Part II is the committed App Store and Google Play scope.</p>
</header>
{body_html()}
<footer style="margin-top:40px;color:var(--soft);font-family:var(--sans);font-size:13px;border-top:2px solid var(--rule2);padding-top:16px">
<p>6S Home Reset &middot; Product Specification &amp; Store Release Plan. The six steps, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth S.</p>
<p>Prices, costs, and conversion figures introduced in this rebuild are recommendations or illustrative assumptions to validate, not decided facts. Store fees, testing gates, and guideline numbers change frequently; re-verify at submission.</p>
</footer>
</main>
</div>
<script>{JS}</script>
</body></html>"""

os.makedirs(OUTDIR, exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(doc)
print("wrote:", OUT)
print("sections: %d (%d new)  bytes: %d" % (n_sec, n_new, len(doc)))
