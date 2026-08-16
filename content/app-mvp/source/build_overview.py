# -*- coding: utf-8 -*-
"""One self-contained page: introduces the app, explains features, shows the roadmap,
and lists what it takes to be a viable App Store / Google Play app. Book design system."""
import io, os, html as H

OUT = r"C:\Users\philk\Desktop\6S-Home-MicroZones-MVP-Beta\6S Home Micro Zones - App Overview.html"

def esc(s): return H.escape("" if s is None else str(s), quote=False)

STATS = [("20","room types"),("114","micro zones"),("6","steps per zone"),
         ("97","product types"),("v0.2.1","working prototype")]

FEATURES = [
 ("The guided zone reset","#BC4B2A",
  "You never face a whole room. You pick one micro zone and run it. Each zone opens with its mission (what it is for, what done looks like, what to watch for) and the one call that actually matters here, then walks the six steps: Sort, Straighten, Shine, Safety, Standardize, Sustain, with checkable, zone-specific sub-procedures.",
  ["Rooms broken into finishable micro zones","Six guided steps, Safety the fourth","Zone-specific substeps and the hard call named"]),
 ("See the change","#3C5A6B",
  "Photograph the honest before, work the zone, photograph the after. An optional AI reads your before photos into a tailored Sort plan and scores the after against the target state. When the zone is done, a before-and-after reveal shows the transformation, and that after photo becomes the zone's standard.",
  ["Before / after photos, kept on device","AI Sort plan from your own photos (optional)","Scored coach review and a completion reveal"]),
 ("The right kit, not the whole aisle","#DDA63A",
  "Each step surfaces the product types that zone actually rewards, grouped by the job they do, with a mark-as-owned toggle and three ways to buy. The value is the opposite of a catalogue: a short, finished set that gives you permission to stop buying clever organizers a zone will never use.",
  ["Product types by job, never brand noise","I-own-this toggle across all zones","Three sourced picks per product"]),
 ("Keep it","#6E8B5B",
  "A finished zone drifts back unless keeping is designed in. A two-minute audit checks the zone against its after photo, flags drift, and the home surfaces zones due for a check-in, so upkeep is a habit rather than a heroic weekend.",
  ["Two-minute sustain audit with drift flag","Audit-due and stalled-zone nudges","Room-as-zones keeps every job finishable"]),
 ("Private by design","#8A6BA1",
  "The sensitive asset is photos of the inside of your home, so they stay on the device. The AI is optional, off by default, and reachable only through a proxy that holds the key. Diagnostics are photo-free, and a full wipe clears everything.",
  ["Photos and progress stay on device","AI off by default, no key in the app","Photo-free diagnostics and a full data wipe"]),
 ("Built to learn","#3D7A74",
  "The beta instruments its own loop with privacy-safe, on-device events (counts and enums only) and a Diagnostics screen, so the team can see whether households reach a finished zone and keep going, without anything leaving the phone.",
  ["On-device event log, no PII","A Diagnostics status screen","Health and reliability signals for support"]),
]

# roadmap phases (condensed from the roadmap doc)
PHASES = [
 ("0","Now: Prototype","done","Verified on-device PWA of the full loop (v0.2.1)."),
 ("1","Foundation","planned","Port to native Expo, local-first, feature parity."),
 ("2","Intelligence & Data","planned","Backend, AI proxy with metering, event pipeline."),
 ("3","Trust & Beta-Ready","planned","Privacy, consent, permissions, encryption, deletion."),
 ("4","Closed Beta","planned","TestFlight and Play closed test; measure activation."),
 ("5","Launch","planned","Listings, data-safety, submit both stores."),
 ("6","Grow","planned","Accounts, subscriptions, notifications, all 20 rooms."),
]

# viability checklist: status done=in prototype today / build=to build
VIABLE = [
 ("Foundation (both platforms)", [
   ("Native app shell (Expo / React Native), not a web wrapper","build"),
   ("On-device storage for progress and full-resolution photos","build"),
   ("Native camera and photo-library capture","build"),
   ("Works offline; garages and basements are core terrain","build"),
   ("The core zone-reset loop, engines, and content","done"),
 ]),
 ("Backend & AI", [
   ("Server proxy holds the API key (never shipped in the binary)","build"),
   ("AI on a zero-retention, no-training configuration, documented","build"),
   ("Per-user metering and cost logging on AI calls","build"),
   ("Configurable AI endpoint with graceful static fallback","done"),
   ("Clamped, schema-validated AI output before render","done"),
 ]),
 ("Apple App Store", [
   ("Apple Developer Program enrollment (organization, D-U-N-S)","build"),
   ("Sign in with Apple (offered alongside any third-party login)","build"),
   ("In-app account deletion (Guideline 5.1.1(v))","build"),
   ("StoreKit 2 for any subscription; IAP for digital goods","build"),
   ("Privacy nutrition labels; camera and photo usage strings","build"),
   ("Review-ready: demo account, no dead links, AI disclosed","build"),
 ]),
 ("Google Play", [
   ("Play Console registration (organization account)","build"),
   ("Closed test: 12+ testers for 14 continuous days","build"),
   ("Data-safety form matching the privacy policy exactly","build"),
   ("Play Billing for subscriptions; modern photo-picker path","build"),
   ("In-app and web account-deletion path, linked on the listing","build"),
   ("Current target API level and scoped media permissions","build"),
 ]),
 ("Privacy, safety & compliance", [
   ("Privacy policy and terms, linked in-app and in both listings","build"),
   ("First-run consent and a one-time photo-send notice before AI","build"),
   ("Encryption of photos at rest in the native shell","build"),
   ("Deletion that also covers any server-retained copy","build"),
   ("Liability disclaimers for cleaning-chemistry and AI hazard notes","build"),
   ("Photo-free diagnostic export and an in-app error boundary","done"),
   ("On-device, privacy-safe instrumentation (no cross-app tracking)","done"),
 ]),
 ("Monetization (for a business, not just a listing)", [
   ("Freemium gate (free rooms, then 6S Plus)","build"),
   ("Affiliate tagging on the sourced product links, with FTC disclosure","build"),
   ("Store-compliant separation of physical-goods links from digital IAP","build"),
 ]),
]

ST = {"done":("#6E8B5B","In the prototype"),"build":("#BC4B2A","To build")}

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;--honey:#DDA63A;
--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:62px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17.5px;line-height:1.6}
.book{max-width:1080px;margin:0 auto;padding:0 26px 120px}
.nav{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule2);padding:11px 26px;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.nav .brand{font-family:var(--display);font-weight:700;font-size:15px;margin-right:auto}
.nav a{font-family:var(--sans);font-size:13px;color:var(--slate);text-decoration:none;padding:5px 10px;border-radius:7px}
.nav a:hover{background:var(--panel);color:var(--terra)}
.hero{padding:56px 0 8px;max-width:820px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(36px,6.5vw,62px);line-height:1.02;letter-spacing:-.015em;margin:.12em 0 .2em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(18px,2.6vw,23px);margin:0 0 8px;max-width:640px}
.storeline{font-family:var(--sans);font-size:13px;color:var(--soft)}
.storeline b{color:var(--slate)}
.statband{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:28px 0 6px}
.scard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:15px 14px;text-align:center}
.scard .num{font-family:var(--display);font-size:27px;font-weight:700;color:var(--green);line-height:1}
.scard b{font-family:var(--sans);font-size:11px;letter-spacing:.4px;text-transform:uppercase;color:var(--soft);display:block;margin-top:4px;font-weight:600}
h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.4vw,32px);margin:2.3em 0 .5em;scroll-margin-top:58px}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.4em}
p{margin:0 0 1em;max-width:780px}.lead{font-size:1.05em}
.method{display:flex;flex-wrap:wrap;gap:8px;margin:1em 0}
.step{font-family:var(--sans);font-size:13px;font-weight:600;padding:7px 13px;border-radius:20px;color:#fff}
.feat{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin-top:14px}
.fcard{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:18px 20px;border-top:5px solid var(--slate)}
.fcard h3{font-family:var(--display);font-size:20px;font-weight:600;margin:0 0 7px}
.fcard p{font-size:15px;margin:0 0 10px}
.fcard ul{list-style:none;margin:0;padding:0}
.fcard li{position:relative;padding-left:22px;margin:.35em 0;font-size:14px;color:var(--ink)}
.fcard li::before{content:"";position:absolute;left:2px;top:.52em;width:8px;height:8px;border-radius:50%;background:var(--green)}
/* roadmap */
.rail{position:relative;margin:22px 0 6px}
.railline{position:absolute;top:20px;left:0;right:0;height:4px;background:var(--rule);border-radius:3px}
.railprog{position:absolute;top:20px;left:0;height:4px;background:var(--green);border-radius:3px;width:8%}
.dots{position:relative;display:flex;justify-content:space-between}
.dot{display:flex;flex-direction:column;align-items:center;gap:7px;flex:1;min-width:0}
.dot .k{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;font-family:var(--display);font-weight:700;font-size:16px;color:#fff;border:4px solid var(--paper)}
.dot .lbl{font-family:var(--sans);font-size:11px;font-weight:600;text-align:center;line-height:1.2}
.dot .now{font-family:var(--sans);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--green)}
.rmlist{margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.rm{display:flex;gap:12px;background:var(--panel);border:1px solid var(--rule);border-radius:11px;padding:12px 15px}
.rm .rn{font-family:var(--display);font-weight:900;font-size:22px;color:var(--rule2);line-height:1}
.rm b{font-family:var(--display);font-size:16px;color:var(--ink)}
.rm .rw{font-size:14px;color:var(--soft);margin-top:2px}
.rm.done{border-left:4px solid var(--green)}.rm.done .rn{color:var(--green)}
.linkline{font-family:var(--sans);font-size:13.5px;color:var(--soft);margin-top:10px}
/* viability */
.legend{display:flex;gap:16px;font-family:var(--sans);font-size:13px;color:var(--soft);margin:8px 0 14px}
.legend span{display:inline-flex;align-items:center;gap:7px}
.sw{width:12px;height:12px;border-radius:50%;display:inline-block}
.vgroup{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:16px 20px;margin:12px 0}
.vgroup h3{font-family:var(--display);font-size:19px;font-weight:600;margin:0 0 8px;color:var(--slate)}
.vgroup ul{list-style:none;margin:0;padding:0}
.vitem{display:flex;align-items:flex-start;gap:11px;padding:7px 0;border-bottom:1px dashed var(--rule2);font-size:15px}
.vitem:last-child{border-bottom:0}
.vdot{width:18px;height:18px;border-radius:50%;flex:none;margin-top:2px;display:grid;place-items:center;color:#fff;font-size:11px;font-weight:700}
.vtag{font-family:var(--sans);font-size:10px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:1px 7px;border-radius:9px;color:#fff;white-space:nowrap;margin-left:auto;align-self:center}
.summary{background:var(--ink);color:var(--paper);border-radius:16px;padding:26px 30px;margin:2em 0}
.summary .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--honey);font-weight:700;margin-bottom:9px}
.summary p{font-family:var(--display);font-weight:500;font-size:21px;line-height:1.32;margin:0;max-width:none}
footer{max-width:820px;margin:56px auto 0;border-top:2px solid var(--rule2);padding-top:16px;color:var(--soft);font-family:var(--sans);font-size:13px}
@media(max-width:820px){.statband{grid-template-columns:1fr 1fr 1fr}.rmlist{grid-template-columns:1fr}.dot .lbl{font-size:9px}.dot .k{width:32px;height:32px;font-size:13px}}
@media print{body{background:#fff}.nav{display:none}.fcard,.vgroup,.rm{break-inside:avoid}}
"""

sb="".join('<div class="scard"><div class="num">%s</div><b>%s</b></div>'%(esc(n),esc(l)) for n,l in STATS)
STEP_C=["#a8452f","#b8862b","#3f6647","#16395f","#6b4f8a","#3d6d74"]
method="".join('<span class="step" style="background:%s">%s. %s</span>'%(STEP_C[i],i+1,s) for i,s in enumerate(["Sort","Straighten","Shine","Safety","Standardize","Sustain"]))
feats="".join('<div class="fcard" style="border-top-color:%s"><h3>%s</h3><p>%s</p><ul>%s</ul></div>'%(c,esc(t),esc(d),"".join("<li>%s</li>"%esc(x) for x in b)) for t,c,d,b in FEATURES)

dots="".join('<div class="dot"><div class="k" style="background:%s">%s</div><div class="lbl">%s</div>%s</div>'%(
  ST["done"][0] if st=="done" else "#3C5A6B", n, esc(nm.split(":")[-1].strip()),
  '<span class="now">Here</span>' if st=="done" else '<span class="now" style="visibility:hidden">.</span>') for n,nm,st,_ in PHASES)
rmlist="".join('<div class="rm %s"><span class="rn">%s</span><div><b>%s</b><div class="rw">%s</div></div></div>'%(
  "done" if st=="done" else "", n, esc(nm), esc(desc)) for n,nm,st,desc in PHASES)

vgroups=""
for title,items in VIABLE:
    lis=""
    for txt,st in items:
        col,lbl=ST[st];mark="✓" if st=="done" else ""
        lis+='<li class="vitem"><span class="vdot" style="background:%s">%s</span><span>%s</span><span class="vtag" style="background:%s">%s</span></li>'%(col,mark,esc(txt),col,esc(lbl))
    vgroups+='<div class="vgroup"><h3>%s</h3><ul>%s</ul></div>'%(esc(title),lis)

# counts
done_n=sum(1 for _,items in VIABLE for _,st in items if st=="done")
build_n=sum(1 for _,items in VIABLE for _,st in items if st=="build")

doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>6S Home Micro Zones - App Overview</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="nav"><span class="brand">6S Home Micro Zones</span>
<a href="#what">What it is</a><a href="#features">Features</a><a href="#roadmap">Roadmap</a><a href="#viable">What it takes to ship</a></div>
<main class="book">
<header class="hero">
<p class="eyebrow">Smartphone App &middot; Overview</p>
<h1 class="title">6S Home Micro Zones</h1>
<p class="subtitle">Organization &amp; Housekeeping. Reset your home one small zone at a time.</p>
<p class="storeline"><b>Store title:</b> 6S Success Home Micro Zones: Organization &amp; Housekeeping &nbsp;&middot;&nbsp; <b>Status:</b> working on-device prototype (v0.2.1), targeting the Apple App Store and Google Play.</p>
<div class="statband">{sb}</div>
</header>

<section id="what"><h2><span class="kick">What it is</span>A system, not a checklist</h2>
<p class="lead">6S Home Micro Zones turns a professional home-reset method into a phone you can actually follow. It breaks a whole home into 114 bounded micro zones across 20 room types, each engineered to finish in one short sitting and end in a change you can see from the doorway. In one flow it is a work-session guide, a photographic before-and-after, an optional AI coach that builds a plan from your own photos, and a sourced shopping companion.</p>
<p>The method is the six S's, run in order on every zone. Safety is the fourth S.</p>
<div class="method">{method}</div>
<p>It is built for the household adult driving the reset and the family who has to keep it, so the standards are designed to survive children, tired Tuesdays, and 7:40 in the morning.</p>
</section>

<section id="features"><h2><span class="kick">Features</span>What it does</h2>
<div class="feat">{feats}</div></section>

<section id="roadmap"><h2><span class="kick">Where it is going</span>Product roadmap</h2>
<p>Seven phases from today's verified prototype to a launched, retained app. Durations in the full roadmap are planning estimates.</p>
<div class="rail"><div class="railline"></div><div class="railprog"></div><div class="dots">{dots}</div></div>
<div class="rmlist">{rmlist}</div>
<p class="linkline">The full visual roadmap, with per-phase deliverables, milestones, and a workstream swimlane grid, is in <b>roadmap/6S Home Micro Zones - Product Roadmap.html</b> (product-spec package).</p>
</section>

<section id="viable"><h2><span class="kick">What it takes to ship</span>Viable on the App Store and Google Play</h2>
<p>The prototype proves the experience. Turning it into an app real people can download and trust means the work below. {done_n} of these are already true in the prototype; {build_n} are still to build.</p>
<div class="legend"><span><span class="sw" style="background:{ST['done'][0]}"></span> In the prototype today</span><span><span class="sw" style="background:{ST['build'][0]}"></span> Still to build</span></div>
{vgroups}
<div class="summary"><div class="lbl">The honest state</div>
<p>The core loop works and is private by design. What stands between it and the stores is not more features, it is the native shell, a key-holding AI proxy, and the trust and store-compliance work: privacy policy and consent, account deletion, permission strings, and the two stores' billing and testing gates.</p></div>
</section>

<footer><p><b>6S Home Micro Zones &middot; App Overview.</b> Built from the product specification, the MVP beta plan, the seven-discipline review, and the running v0.2.1 prototype. The six steps, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth S.</p></footer>
</main></body></html>"""

os.makedirs(os.path.dirname(OUT),exist_ok=True)
io.open(OUT,"w",encoding="utf-8").write(doc)
print("wrote:",OUT)
print("features:",len(FEATURES),"phases:",len(PHASES),"viability items:",done_n+build_n,"(done %d / build %d)"%(done_n,build_n))
print("em-dashes:",doc.replace("&middot;","").replace("&amp;","").count("—"),"bytes:",len(doc))
