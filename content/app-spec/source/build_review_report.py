# -*- coding: utf-8 -*-
"""Render the seven-discipline MVP review as a navigable report (book design system)."""
import json, io, re, html as H, os, collections

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
OUT = r"C:\Users\philk\Desktop\6S-Home-Reset-Product-Spec\review-panel\MVP Review Panel - Seven Disciplines.html"

reviews = json.load(io.open(SCRATCH + r"\reviews.json", encoding="utf-8"))["reviews"]

def esc(s): return H.escape("" if s is None else str(s), quote=False)
def slug(s): return re.sub(r"[^a-z0-9]+","-",str(s).lower()).strip("-")

THEME = {"usability":("Usability","#BC4B2A"),"data-collection":("Data collection","#3C5A6B"),
         "visualization":("Visualization","#6E8B5B")}
SEV = {"high":"#CB4B36","medium":"#DDA63A","low":"#6A625A"}

all_findings = [dict(f, _role=v.get("role")) for v in reviews for f in (v.get("findings") or [])]
by_theme = collections.OrderedDict((k,[]) for k in ["usability","data-collection","visualization"])
for f in all_findings:
    by_theme.setdefault(f.get("theme","usability"),[]).append(f)
sev_rank = {"high":0,"medium":1,"low":2}

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;--honey:#DDA63A;
--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17.5px;line-height:1.55}
.book{max-width:1000px;margin:0 auto;padding:0 26px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:52px 0 6px;max-width:720px}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(32px,5.5vw,50px);line-height:1.04;margin:.1em 0 .25em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(17px,2.3vw,20px);margin:0 0 8px;max-width:640px}
.lede{max-width:720px;color:var(--soft)}
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule2);padding:9px 26px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:15px;margin-right:auto}
.topbar a{font-family:var(--sans);font-size:12.5px;color:var(--slate);text-decoration:none;padding:4px 8px;border-radius:6px}
.topbar a:hover{background:var(--panel)}
h2{font-family:var(--display);font-weight:600;font-size:clamp(22px,3vw,29px);margin:2em 0 .5em;border-bottom:3px solid var(--terra);padding-bottom:8px;scroll-margin-top:60px}
h3{font-family:var(--display);font-weight:600;font-size:20px;margin:1.4em 0 .3em;color:var(--slate)}
p{margin:0 0 .8em;max-width:800px}
.rolecard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:16px 20px;margin:1em 0}
.rolecard .prio{border-left:4px solid var(--terra);padding-left:12px;margin-top:8px;font-size:15.5px}
.rolecard .prio b{font-family:var(--sans);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);display:block;margin-bottom:3px}
.f{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:15px 18px;margin:11px 0;border-left:5px solid var(--rule)}
.f .top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.f h4{font-family:var(--display);font-size:18px;font-weight:600;margin:0}
.f .tags{display:flex;gap:6px;flex-wrap:wrap;white-space:nowrap}
.tag{font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 9px;border-radius:11px;color:#fff}
.tag.role{background:#eee9de;color:var(--soft)}
.f .lbl{font-family:var(--sans);font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--soft);font-weight:700;margin-top:8px}
.f .rec{color:var(--ink)}.f .spec{color:var(--slate);font-style:italic}
.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}
.scard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 16px}
.scard .num{font-family:var(--display);font-size:28px;font-weight:700;color:var(--green)}
.scard b{font-family:var(--sans);font-size:11.5px;letter-spacing:.4px;text-transform:uppercase;color:var(--soft);display:block;margin-top:3px}
@media(max-width:760px){.summary{grid-template-columns:1fr 1fr}}
@media print{.topbar{display:none}.f{break-inside:avoid}}
"""

def finding(f, show_role=True):
    tn, tc = THEME.get(f.get("theme"),("",""))
    sev = f.get("severity","low")
    tags = '<span class="tag" style="background:%s">%s</span><span class="tag" style="background:%s">%s</span>' % (
        SEV.get(sev,"#999"), esc(sev), tc, esc(tn))
    if show_role: tags += '<span class="tag role">%s</span>' % esc(f.get("_role",""))
    return f"""<div class="f" style="border-left-color:{tc}">
<div class="top"><h4>{esc(f.get('title'))}</h4><div class="tags">{tags}</div></div>
<p>{esc(f.get('observation'))}</p>
<div class="lbl">Recommendation</div><p class="rec">{esc(f.get('recommendation'))}</p>
<div class="lbl">Spec change</div><p class="spec">{esc(f.get('spec_change'))}</p></div>"""

nav = '<a href="#by-theme">By theme</a>' + "".join('<a href="#%s">%s</a>' % (slug(v.get("role")), esc(v.get("role").split()[0])) for v in reviews)
nfind = len(all_findings)
nhigh = sum(1 for f in all_findings if f.get("severity")=="high")

# by-theme section
theme_html = ['<h2 id="by-theme">Findings by Theme</h2>']
for tk,(tlabel,tcol) in THEME.items():
    fs = sorted(by_theme.get(tk,[]), key=lambda x:sev_rank.get(x.get("severity"),3))
    theme_html.append('<h3 style="color:%s">%s (%d)</h3>' % (tcol, tlabel, len(fs)))
    theme_html += [finding(f, True) for f in fs]

# by-role sections
role_html = ['<h2>Reviews by Discipline</h2>']
for v in reviews:
    fs = sorted(v.get("findings") or [], key=lambda x:sev_rank.get(x.get("severity"),3))
    role_html.append('<h3 id="%s">%s</h3>' % (slug(v.get("role")), esc(v.get("role"))))
    role_html.append('<div class="rolecard"><p>%s</p><div class="prio"><b>Top priority</b>%s</div></div>' % (esc(v.get("summary")), esc(v.get("top_priority"))))
    role_html += [finding(f, False) for f in fs]

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MVP Review Panel - Seven Disciplines</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="topbar"><span class="brand">MVP Review Panel</span>{nav}</div>
<main class="book">
<header class="masthead">
<p class="chno">6S Success &middot; Home Micro Zones &middot; MVP Beta</p>
<p class="eyebrow">Seven-Discipline Review</p>
<h1 class="title">MVP Review Panel</h1>
<p class="subtitle">Marketing, customer success, support, product, QA, front-end, and back-end review the beta.</p>
<p class="lede">Each discipline reviewed the running MVP and the product spec, focused on usability, data collection, and visualization. Findings feed the spec update (Part IV).</p></header>
<section class="summary">
<div class="scard"><div class="num">{len(reviews)}</div><b>Disciplines</b></div>
<div class="scard"><div class="num">{nfind}</div><b>Findings</b></div>
<div class="scard"><div class="num">{nhigh}</div><b>High severity</b></div>
<div class="scard"><div class="num">3</div><b>Themes</b></div>
</section>
{''.join(theme_html)}
{''.join(role_html)}
</main></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(doc)
print("wrote:", OUT)
print("reviews: %d  findings: %d  high: %d" % (len(reviews), nfind, nhigh))
