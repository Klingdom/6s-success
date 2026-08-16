# -*- coding: utf-8 -*-
"""Visual product roadmap for the 6S Success Home Micro Zones app (book design system)."""
import io, os, html as H

OUT = r"C:\Users\philk\Desktop\6S-Home-Reset-Product-Spec\roadmap\6S Home Micro Zones - Product Roadmap.html"

def esc(s): return H.escape("" if s is None else str(s), quote=False)

# status: done / active / planned / deferred
PHASES = [
 {"n":"0","name":"Now: Prototype","when":"Complete","status":"done","tag":"v0.2.1",
  "goal":"Prove the core loop off the Claude artifact host, on a real device.",
  "items":["Runnable on-device PWA: full zone-reset loop, 6 curated rooms / 37 zones",
           "On-device instrumentation + Diagnostics screen; before/after completion reveal (gated on both photos)",
           "AI off-state with Cancel/Retry; error boundary; in-app help + photo-free diagnostic export",
           "The call that matters here per zone; room-as-zones framing; items-released fixed"],
  "milestone":"Core loop verified in-browser, no console errors."},
 {"n":"1","name":"Foundation","when":"~3 weeks (est.)","status":"planned","tag":"Expo port",
  "goal":"Port the prototype to a native local-first app with feature parity.",
  "items":["Expo / React Native scaffold; port datasets, instruction engines, AI prompts, JSON repair, design tokens",
           "Device storage (SQLite + file-system photos); native camera + image-manipulator; StyleSheet; navigation",
           "Add TypeScript and a top-level error boundary"],
  "milestone":"Feature parity with the prototype on a phone, offline, single user."},
 {"n":"2","name":"Intelligence & Data","when":"~3 weeks, overlaps (est.)","status":"planned","tag":"Backend + AI",
  "goal":"Stand up the thin backend, the AI proxy, and the event pipeline.",
  "items":["Managed backend (Supabase or Firebase); AI proxy holds the key, zero-retention, per-user metering + cost logs; model pinned server-side",
           "Event pipeline: on-device queue flushes to privacy-respecting analytics (consented)",
           "Versioned catalog service so the 90-day sourcing refresh ships without an app update"],
  "milestone":"AI runs through our keys with cost logs; events flush with consent."},
 {"n":"3","name":"Trust & Beta-Ready","when":"~2 to 3 weeks (est.)","status":"planned","tag":"Compliance",
  "goal":"Make it safe to put real home photos through the beta.",
  "items":["Privacy policy + terms; first-run consent + a one-time photo-send notice; native permission strings; encryption at rest",
           "Account / data-deletion path (covers any server copy); data-safety form and privacy labels",
           "Liability disclaimers for cleaning-chemistry and AI hazard guidance; runtime AI JSON validation"],
  "milestone":"P0 and P1 compliance gates cleared."},
 {"n":"4","name":"Closed Beta","when":"~4 weeks (est.)","status":"planned","tag":"TestFlight + Play",
  "goal":"Learn whether households finish a zone and keep going.",
  "items":["TestFlight internal then external; Play closed test (12+ testers, 14 continuous days)",
           "Recruit from the content funnel (book, manual, the 114-video series)",
           "Measure activation, AI attach, sustain retention, home-improvement delta; stand up the five team dashboards",
           "Guided first-run to one fast-win zone; at-risk and stalled-zone nudges"],
  "milestone":"Activation and crash-free targets met; review-readiness green."},
 {"n":"5","name":"Launch","when":"~2 weeks (est.)","status":"planned","tag":"Both stores",
  "goal":"Ship to the App Store and Google Play.",
  "items":["Store listing title: 6S Success Home Micro Zones: Organization & Housekeeping",
           "Screenshots, privacy labels and data-safety form, seeded demo account",
           "Submit both stores; plan for one revision cycle"],
  "milestone":"Live on the App Store and Google Play."},
 {"n":"6","name":"Grow","when":"v1.x then v2 (later)","status":"planned","tag":"Post-launch",
  "goal":"Turn the loop into a retained, monetized household product.",
  "items":["Accounts and households with zone-owner assignment (the retention engine); cloud sync",
           "6S Plus subscription and paywall; push notifications and audit reminders",
           "Before/after share cards + deep-link attribution; the full 20 rooms / 114 zones; affiliate on the 291 sourced picks"],
  "milestone":"Freemium loop and household retention live."},
]

# workstream x phase presence: 2=lead, 1=supporting, 0=none
LANES = [
 ("Core app & UX",        [2,2,0,1,1,1,2]),
 ("AI coaching",          [1,0,2,1,0,0,1]),
 ("Data & instrumentation",[2,0,2,0,2,0,1]),
 ("Privacy & compliance", [1,0,1,2,1,2,1]),
 ("Growth & monetization",[0,0,0,0,1,1,2]),
]

DEFERRED = ["Pro tier (organizer edition, client households, white-label)","Web app",
 "AI vision v2 (richer, passive analysis)","Non-US markets and localization",
 "These are explicitly out of scope for v1.0; the data model anticipates them."]

STATUS = {"done":("#6E8B5B","Complete"),"active":("#DDA63A","In progress"),
          "planned":("#3C5A6B","Planned"),"deferred":("#6A625A","Deferred")}

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;--honey:#DDA63A;
--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17px;line-height:1.55}
.book{max-width:1180px;margin:0 auto;padding:0 26px 110px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:52px 0 10px;max-width:820px}
.chno{font-family:var(--display);font-weight:900;font-size:14px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(32px,5.2vw,50px);line-height:1.03;margin:.1em 0 .22em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(17px,2.3vw,21px);margin:0 0 8px;max-width:620px}
.lede{max-width:820px;color:var(--soft);font-size:1.02em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(21px,2.8vw,27px);margin:2.2em 0 .6em}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.4em}
/* timeline rail */
.rail{position:relative;margin:26px 0 8px;padding:0 2px}
.railline{position:absolute;top:22px;left:0;right:0;height:4px;background:var(--rule);border-radius:3px}
.railprog{position:absolute;top:22px;left:0;height:4px;background:var(--green);border-radius:3px;width:9%}
.dots{position:relative;display:flex;justify-content:space-between}
.dot{display:flex;flex-direction:column;align-items:center;gap:8px;flex:1;min-width:0}
.dot .k{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;font-family:var(--display);font-weight:700;font-size:18px;color:#fff;border:4px solid var(--paper);z-index:1}
.dot .lbl{font-family:var(--sans);font-size:11.5px;font-weight:600;text-align:center;color:var(--ink);line-height:1.25}
.dot .now{font-family:var(--sans);font-size:9.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--green)}
/* phase cards */
.phases{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px;margin-top:22px}
.pcard{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:18px 20px;border-top:5px solid var(--slate)}
.pcard .ph{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.pcard h3{font-family:var(--display);font-size:20px;font-weight:600;margin:0;color:var(--ink)}
.pcard .pn{font-family:var(--display);font-weight:900;font-size:26px;color:var(--rule2);line-height:1}
.pcard .when{font-family:var(--sans);font-size:12px;color:var(--soft);margin:2px 0 2px}
.chip{display:inline-block;font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 9px;border-radius:11px;color:#fff}
.chip.soft{background:#eee9de;color:var(--soft)}
.pcard .goal{font-size:15px;margin:8px 0 10px}
.pcard ul{margin:0;padding-left:18px;font-size:14px;color:var(--ink)}
.pcard li{margin:.32em 0;line-height:1.42}
.pcard .ms{margin-top:11px;font-family:var(--sans);font-size:12.5px;color:var(--slate);border-top:1px dashed var(--rule2);padding-top:9px}
.pcard .ms b{color:var(--green)}
/* swimlane grid */
.wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;margin:1em 0}
table{border-collapse:collapse;width:100%;min-width:760px;background:var(--panel);font-family:var(--sans)}
th,td{padding:10px 8px;text-align:center;border-bottom:1px solid var(--rule);font-size:12.5px}
th{background:var(--slate);color:var(--paper);font-weight:600;font-size:11.5px}
td.lane{text-align:left;font-weight:600;color:var(--ink);white-space:nowrap;background:#faf6ee}
.cell{width:22px;height:22px;border-radius:6px;margin:0 auto;display:block}
.cell.lead{background:var(--terra)}.cell.sup{background:#e6c9a0}.cell.none{background:transparent;border:1px dashed var(--rule2)}
/* deferred */
.deferred{background:var(--panel);border:1px dashed var(--rule2);border-radius:12px;padding:16px 20px;margin:1em 0}
.deferred h4{font-family:var(--sans);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--soft);font-weight:700;margin:0 0 10px}
.deferred ul{margin:0;padding-left:18px;font-size:14.5px;color:var(--soft)}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:12px 0;font-family:var(--sans);font-size:12.5px;color:var(--soft)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:14px;height:14px;border-radius:4px;display:inline-block}
.principles{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin:1em 0}
.pr{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 16px}
.pr b{font-family:var(--display);color:var(--slate);font-size:16px;display:block;margin-bottom:4px}
.pr span{font-size:14px;color:var(--soft)}
footer{max-width:820px;margin:56px auto 0;border-top:2px solid var(--rule2);padding-top:16px;color:var(--soft);font-family:var(--sans);font-size:13px}
@media(max-width:720px){.dot .lbl{font-size:9.5px}.dot .k{width:36px;height:36px;font-size:15px}}
@media print{body{background:#fff}.pcard{break-inside:avoid}}
"""

def phase_dot(p):
    col=STATUS[p["status"]][0]
    now='<span class="now">You are here</span>' if p["status"]=="done" else '<span class="now" style="visibility:hidden">.</span>'
    return f'<div class="dot"><div class="k" style="background:{col}">{esc(p["n"])}</div><div class="lbl">{esc(p["name"].split(":")[-1].strip())}</div>{now}</div>'

def phase_card(p):
    col,slabel=STATUS[p["status"]]
    items="".join("<li>%s</li>"%esc(x) for x in p["items"])
    return f"""<div class="pcard" style="border-top-color:{col}">
<div class="ph"><div><span class="pn">{esc(p["n"])}</span> <h3 style="display:inline">{esc(p["name"])}</h3></div>
<span class="chip" style="background:{col}">{esc(slabel)}</span></div>
<div class="when">{esc(p["when"])} &middot; <span class="chip soft">{esc(p["tag"])}</span></div>
<p class="goal">{esc(p["goal"])}</p><ul>{items}</ul>
<div class="ms"><b>Milestone.</b> {esc(p["milestone"])}</div></div>"""

# swimlane
ncol=len(PHASES)
head="<tr><th class='lane' style='text-align:left'>Workstream</th>"+"".join("<th>%s<br><span style='opacity:.7'>%s</span></th>"%(esc(p["n"]),esc(p["name"].split(":")[-1].strip())) for p in PHASES)+"</tr>"
rows=""
for lane,marks in LANES:
    cells=""
    for m in marks:
        cls="lead" if m==2 else ("sup" if m==1 else "none")
        cells+="<td><span class='cell %s'></span></td>"%cls
    rows+="<tr><td class='lane'>%s</td>%s</tr>"%(esc(lane),cells)

dots="".join(phase_dot(p) for p in PHASES)
cards="".join(phase_card(p) for p in PHASES)
deferred="".join("<li>%s</li>"%esc(x) for x in DEFERRED)

PRINCIPLES=[("Instrument the loop","Ship telemetry with the beta, not after it, so the app can answer its own questions."),
 ("Show the change","The before/after reveal is the payoff; every phase protects it."),
 ("Privacy is the product","Home photos stay private by default; compliance leads, not trails, the beta."),
 ("One funnel, one door","App rooms, videos, and book Part 9 chapters all point at the same 20 rooms.")]
prin="".join('<div class="pr"><b>%s</b><span>%s</span></div>'%(esc(t),esc(d)) for t,d in PRINCIPLES)

doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>6S Home Micro Zones - Product Roadmap</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<main class="book">
<header class="masthead">
<p class="chno">6S Success &middot; Home Micro Zones &middot; Product</p>
<p class="eyebrow">Visual Product Roadmap</p>
<h1 class="title">From prototype to the App Store</h1>
<p class="subtitle">6S Success Home Micro Zones: Organization &amp; Housekeeping.</p>
<p class="lede">Seven phases from the verified on-device prototype (today) to a launched, retained smartphone app. Durations are planning estimates to validate against real team capacity; store timelines add calendar beyond build time.</p>
</header>

<h2><span class="kick">The path</span>Phase timeline</h2>
<div class="rail"><div class="railline"></div><div class="railprog"></div><div class="dots">{dots}</div></div>

<div class="phases">{cards}</div>

<h2><span class="kick">Who works when</span>Workstreams across the phases</h2>
<div class="legend">
<span><span class="sw" style="background:var(--terra)"></span> Lead work</span>
<span><span class="sw" style="background:#e6c9a0"></span> Supporting</span>
<span><span class="sw" style="border:1px dashed var(--rule2)"></span> None</span></div>
<div class="wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>

<h2><span class="kick">Later, on purpose</span>Deferred beyond v1.0</h2>
<div class="deferred"><h4>Out of scope for launch</h4><ul>{deferred}</ul></div>

<h2><span class="kick">What guides the sequence</span>Roadmap principles</h2>
<div class="principles">{prin}</div>

<footer><p><b>6S Home Micro Zones &middot; Product Roadmap.</b> Phase 0 is the current verified prototype (v0.2.1). Phases 1 to 6 are the committed path from the product spec, the MVP beta plan, and the seven-discipline review. Durations are estimates to validate.</p></footer>
</main></body></html>"""

os.makedirs(os.path.dirname(OUT),exist_ok=True)
io.open(OUT,"w",encoding="utf-8").write(doc)
print("wrote:",OUT)
print("phases:",len(PHASES),"lanes:",len(LANES),"em-dashes:",doc.replace("&middot;","").count("—"),"bytes:",len(doc))
