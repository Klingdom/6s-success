# -*- coding: utf-8 -*-
"""Assemble The 6S Micro Zone Reset - YouTube production plan (outline level)."""
import json, io, re, os, html as H

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\6S Micro Zone Reset - YouTube Production Plan.html"

data = json.load(io.open(SCRATCH + r"\video.json", encoding="utf-8"))
rooms = data["rooms"] if isinstance(data, dict) else data

S_ORDER = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]
S_COLOR = {"Sort": "#BC4B2A", "Straighten": "#DDA63A", "Shine": "#6E8B5B",
           "Safety": "#3C5A6B", "Standardize": "#8A6BA1", "Sustain": "#3D7A74"}

CANON = [
    "A standard is the best way you know today, written down.",
    "An audit checks the home, not the household. What it finds is always a system to fix, never a person to blame.",
    "You do not finish 6S. You keep it.",
    "Find it, and fix it now.",
]

def normalize_canon(s):
    for c in CANON:
        for op, cl in (('"', '"'), ("“", "”"), ("'", "'")):
            s = s.replace(op + c + cl, c)
        s = s.replace(c, "“" + c + "”")
    return s

def esc(s):
    return H.escape(normalize_canon(str(s or "").strip()), quote=False)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")

def ul(items, cls=""):
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % esc(i) for i in (items or [])))

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--honey:#DDA63A;--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:78px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.6}
.book{max-width:1060px;margin:0 auto;padding:0 26px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:52px 0 6px;max-width:700px}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(36px,6vw,58px);line-height:1.03;letter-spacing:-.015em;margin:.1em 0 .25em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(18px,2.4vw,21px);margin:0 0 6px;max-width:600px}
.lede{max-width:700px;color:var(--soft);font-size:1.03em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.2vw,31px);line-height:1.1;margin:2.2em 0 .5em}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.5em}
h3{font-family:var(--display);font-weight:600;font-size:23px;margin:0;letter-spacing:-.01em}
p{margin:0 0 1em;max-width:700px}
/* sticky nav */
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);backdrop-filter:blur(8px);
border-bottom:1px solid var(--rule2);padding:11px 26px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:16px;margin-right:auto;white-space:nowrap}
.topbar select,.topbar input{font-family:var(--sans);font-size:14px;padding:7px 11px;border:1px solid var(--rule2);
border-radius:8px;background:var(--panel);color:var(--ink)}
.topbar input{min-width:230px}
.topbar .count{font-family:var(--sans);font-size:12.5px;color:var(--soft);white-space:nowrap}
.totop{position:fixed;right:20px;bottom:20px;z-index:60;background:var(--slate);color:var(--paper);
font-family:var(--sans);font-size:12.5px;padding:9px 14px;border-radius:20px;text-decoration:none;opacity:.9}
.totop:hover{opacity:1}
/* blocks */
.what{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:24px 28px 20px;margin:1.6em 0;max-width:700px}
.what h4{font-family:var(--sans);font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);font-weight:700;margin:0 0 12px}
.what ul{list-style:none;margin:0;padding:0}
.what li{position:relative;padding-left:28px;margin:.45em 0;font-size:16.5px;line-height:1.5}
.what li::before{content:"";position:absolute;left:4px;top:.55em;width:8px;height:8px;background:var(--green);border-radius:50%}
.defbox{background:var(--panel);border:2px solid var(--slate);border-radius:14px;padding:22px 26px;max-width:700px;margin:1.6em 0}
.defbox .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--slate);font-weight:700;margin-bottom:9px}
.defbox p{margin:0;font-family:var(--display);font-weight:500;font-size:21px;line-height:1.3}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1.4em 0}
.gcard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:16px 20px}
.gcard h5{font-family:var(--sans);font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--terra);font-weight:700;margin:0 0 7px}
.gcard p,.gcard ul{margin:0;font-size:15.5px}
.gcard ul{padding-left:18px}
.gcard li{margin:.28em 0}
/* opener spec */
.beats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:1.4em 0}
.beat{background:var(--panel);border:1px solid var(--rule);border-top:5px solid var(--slate);border-radius:12px;padding:16px 19px}
.beat.var{border-top-color:var(--terra)}
.beat .n{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--soft);font-weight:700}
.beat h5{font-family:var(--display);font-size:19px;margin:3px 0 6px;font-weight:600}
.beat p{margin:0;font-size:15.5px;line-height:1.48}
.tagchip{display:inline-block;font-family:var(--sans);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
font-weight:700;padding:2px 8px;border-radius:20px;margin-top:8px}
.tagchip.fixed{background:#e6ebef;color:var(--slate)}
.tagchip.zone{background:#f6e2da;color:var(--terra)}
/* index */
.toc{columns:3;column-gap:26px;background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:20px 24px;margin:1.2em 0}
.toc a{display:block;color:var(--ink);text-decoration:none;margin:6px 0;font-size:15.5px;break-inside:avoid}
.toc a span{font-family:var(--sans);font-size:11.5px;color:var(--soft);display:block}
.toc a:hover{color:var(--terra)}
/* rooms */
.room{margin-top:74px}
.roomhead{border-bottom:3px solid var(--terra);padding-bottom:11px;margin-bottom:14px;display:flex;
align-items:baseline;justify-content:space-between;gap:18px;flex-wrap:wrap}
.roomhead h2{margin:0;font-size:clamp(26px,3.6vw,34px)}
.roomstat{font-family:var(--sans);font-size:13px;color:var(--soft);white-space:nowrap}
.roomnote{background:var(--panel);border-left:5px solid var(--honey);border-radius:0 10px 10px 0;
padding:13px 18px;margin:0 0 22px;font-size:16px;max-width:900px}
.roomnote b{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#B5811E;display:block;margin-bottom:4px}
/* video card */
.vid{background:var(--panel);border:1px solid var(--rule);border-radius:16px;padding:22px 26px 18px;margin:20px 0}
.vhead{display:flex;justify-content:space-between;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:3px}
.vid .code{font-family:var(--sans);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-weight:700}
.vmeta{font-family:var(--sans);font-size:12.5px;color:var(--soft);white-space:nowrap}
.vtitle{font-family:var(--display);font-size:19px;font-weight:500;color:var(--slate);margin:6px 0 2px}
.vtitle::before{content:"Title: ";font-family:var(--sans);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--soft);font-weight:700}
.cold{border:1px solid var(--rule);border-left:5px solid var(--terra);background:#fff;border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.cold .lbl{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--terra);font-weight:700;margin-bottom:5px}
.cold p{margin:0;font-size:16px}
.seg{border:1px solid var(--rule);border-radius:12px;background:#fff;margin:10px 0;overflow:hidden}
.seg summary{cursor:pointer;padding:10px 16px;font-family:var(--sans);font-size:13px;font-weight:700;
letter-spacing:.06em;display:flex;align-items:center;gap:10px;list-style:none}
.seg summary::-webkit-details-marker{display:none}
.seg summary::after{content:"+";margin-left:auto;color:var(--soft);font-size:16px}
.seg[open] summary::after{content:"\\2212"}
.seg .chip{color:#fff;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;padding:3px 10px;border-radius:5px;min-width:92px;text-align:center}
.seg .covers{color:var(--soft);font-weight:400;font-family:var(--serif);font-size:15px;letter-spacing:0}
.segbody{padding:4px 18px 16px;border-top:1px solid var(--rule)}
.segbody h6{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
color:var(--slate);font-weight:700;margin:13px 0 5px}
.segbody ul{margin:0;padding-left:19px;font-size:15.5px}
.segbody li{margin:.26em 0}
.ost li{font-family:var(--sans);font-size:13.5px;color:var(--terra);font-weight:600}
.shortbox{background:#f4f1ea;border-radius:9px;padding:11px 15px;margin-top:12px;font-size:15px}
.shortbox b{font-family:var(--sans);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--green);display:block;margin-bottom:4px}
.shortbox .len{font-family:var(--sans);font-size:12px;color:var(--soft)}
.foot2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}
.foot2 .b{background:#fff;border:1px solid var(--rule);border-radius:11px;padding:13px 17px;font-size:15.5px}
.foot2 .b h6{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:0 0 6px}
.foot2 ul{margin:0;padding-left:18px}
.tags{margin-top:12px}
.tags span{display:inline-block;font-family:var(--sans);font-size:12px;background:#eee9de;color:var(--soft);
padding:3px 10px;border-radius:14px;margin:0 5px 5px 0}
.nores{display:none;padding:40px 0;color:var(--soft);font-style:italic}
@media(max-width:860px){.grid2,.beats,.foot2{grid-template-columns:1fr}.toc{columns:2}}
@media(max-width:620px){.toc{columns:1}body{font-size:17px}.topbar input{min-width:140px}}
@media print{.topbar,.totop{display:none}.room{break-before:page}.vid{break-inside:avoid}.seg{break-inside:avoid}
.seg summary::after{content:""}}
"""

JS = """
(function(){
 var box=document.getElementById('filter'), sel=document.getElementById('roomjump'),
     cnt=document.getElementById('count'), nores=document.getElementById('nores');
 var vids=[].slice.call(document.querySelectorAll('.vid'));
 var rooms=[].slice.call(document.querySelectorAll('.room'));
 vids.forEach(function(v){ v.dataset.hay=(v.textContent||'').toLowerCase(); });
 function apply(){
   var q=(box.value||'').trim().toLowerCase(); var shown=0;
   vids.forEach(function(v){
     var hit=!q||v.dataset.hay.indexOf(q)>-1;
     v.style.display=hit?'':'none'; if(hit)shown++;
   });
   rooms.forEach(function(r){
     var any=[].slice.call(r.querySelectorAll('.vid')).some(function(v){return v.style.display!=='none';});
     r.style.display=any?'':'none';
   });
   cnt.textContent=shown+' of '+vids.length+' videos';
   nores.style.display=shown?'none':'block';
 }
 box.addEventListener('input',apply);
 sel.addEventListener('change',function(){
   if(!sel.value)return;
   box.value='';apply();
   var el=document.getElementById(sel.value); if(el)el.scrollIntoView();
   sel.selectedIndex=0;
 });
 document.getElementById('expand').addEventListener('click',function(e){
   e.preventDefault();
   var open=this.dataset.state!=='open';
   document.querySelectorAll('details.seg').forEach(function(d){d.open=open;});
   this.dataset.state=open?'open':'shut';
   this.textContent=open?'Collapse all':'Expand all';
 });
 apply();
})();
"""

def segment(s):
    step = s.get("step", "")
    sh = s.get("short", {}) or {}
    return f"""<details class="seg">
<summary><span class="chip" style="background:{S_COLOR.get(step,'#666')}">{esc(step)}</span>
<span class="covers">{esc(s.get('covers'))}</span></summary>
<div class="segbody">
<h6>Beats</h6>{ul(s.get('beats'))}
<h6>Shots</h6>{ul(s.get('shots'))}
<h6>On-screen text</h6>{ul(s.get('on_screen_text'), 'ost')}
<div class="shortbox"><b>Short cut &middot; {esc(sh.get('target_length'))}</b>
{esc(sh.get('hook'))}<br><span class="len">Stands alone: {esc(sh.get('standalone_note'))}</span></div>
</div></details>"""

def video(v, code, rslug):
    cl = v.get("close", {}) or {}
    segs = {s.get("step"): s for s in (v.get("segments") or [])}
    ordered = [segs[k] for k in S_ORDER if k in segs]
    return f"""<article class="vid" id="{rslug}--{slug(v.get('zone',''))}">
<div class="vhead"><div><span class="code">{code}</span><h3>{esc(v.get('zone'))}</h3></div>
<span class="vmeta">{esc(v.get('runtime'))} &middot; thumbnail: &ldquo;{esc(v.get('thumbnail_text'))}&rdquo;</span></div>
<p class="vtitle">{esc(v.get('title'))}</p>
<div class="cold"><div class="lbl">Cold open &middot; beat 1 of 3 &middot; the problem</div>
<p>{esc(v.get('cold_open_problem'))}</p></div>
{"".join(segment(s) for s in ordered)}
<div class="foot2">
<div class="b"><h6>Close</h6><p style="margin:0 0 7px">{esc(cl.get('standard_beat'))}</p>
<p style="margin:0;color:var(--soft)">Next: {esc(cl.get('next_zone_teaser'))}</p></div>
<div class="b"><h6>Shot list</h6>{ul(v.get('shot_list'))}</div>
</div>
<div class="foot2"><div class="b" style="grid-column:1/-1"><h6>Description hook</h6>
<p style="margin:0">{esc(v.get('description_hook'))}</p>
<div class="tags">{"".join("<span>%s</span>" % esc(t) for t in (v.get('tags') or []))}</div></div></div>
</article>"""

n_room = len(rooms)
n_vid = sum(len(r.get("videos") or []) for r in rooms)
n_short = sum(len(v.get("segments") or []) for r in rooms for v in (r.get("videos") or []))

sections, counter = [], 0
for i, r in enumerate(rooms, 1):
    rslug = slug(r.get("room"))
    cards = []
    for j, v in enumerate(r.get("videos") or [], 1):
        counter += 1
        cards.append(video(v, "MZ-%03d &middot; R%02d.%02d" % (counter, i, j), rslug))
    sections.append(f"""<section class="room" id="{rslug}">
<div class="roomhead"><div><p class="eyebrow">Room {i:02d} of {n_room}</p><h2>{esc(r.get('room'))}</h2></div>
<span class="roomstat">{len(r.get('videos') or [])} videos &middot; {len(r.get('videos') or [])*6} Shorts</span></div>
<div class="roomnote"><b>Production note</b>{esc(r.get('room_note'))}</div>
{"".join(cards)}</section>""")

toc = "".join('<a href="#%s">%s<span>%d videos</span></a>' % (slug(r.get("room")), esc(r.get("room")), len(r.get("videos") or [])) for r in rooms)
opts = "".join('<option value="%s">%s</option>' % (slug(r.get("room")), esc(r.get("room"))) for r in rooms)

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The 6S Micro Zone Reset - YouTube Production Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="topbar">
<span class="brand">6S Micro Zone Reset</span>
<select id="roomjump" aria-label="Jump to room"><option value="">Jump to room…</option>{opts}</select>
<input id="filter" type="search" placeholder="Filter zones, titles, shots…" aria-label="Filter videos">
<a href="#" id="expand" data-state="shut" style="font-family:var(--sans);font-size:13px;color:var(--slate)">Expand all</a>
<span class="count" id="count"></span>
</div>

<main class="book">
<header class="masthead">
<p class="chno">6S Success &middot; Home Edition &middot; Video Companion</p>
<p class="eyebrow">Headless YouTube Series &middot; Production Plan</p>
<h1 class="title">The 6S Micro Zone Reset</h1>
<p class="subtitle">One zone, one sitting, one video.</p>
</header>

<p class="lede">Outline-level production plan for {n_vid} headless zone videos across {n_room} rooms, each cut into six Shorts for {n_short} short-form assets in total. Every video teaches one micro zone from The Micro Zone Manual, using that zone's real done-state, hazards, and hard decision. No presenter appears on camera at any point.</p>

<h2><span class="kick">The series</span>What this is</h2>
<p>The book explains why. The manual tells you what to do at a specific shelf. The videos show it happening. Each one takes a single micro zone from start to finished standard, in the order the six steps are meant to run.</p>
<p>The format is deliberately repeatable rather than novel. Same opener structure, same six segments, same close, every time. That is what lets one person shoot a zone in an afternoon and what lets a viewer who found you through the Pantry know exactly how the Garage video will go.</p>

<div class="defbox"><div class="lbl">The promise, every episode</div>
<p>One micro zone, one sitting, and a change you can see from the doorway.</p></div>

<h2><span class="kick">Cold open</span>The 60 second opener</h2>
<p>Every episode opens the same way, in three beats, running about sixty seconds. Two beats are fixed series-wide and recorded once as reusable assets. Only the first beat changes, and it changes because the problem it names belongs to that specific zone.</p>

<div class="beats">
<div class="beat var"><div class="n">Beat 1 &middot; about 20s</div><h5>The problem</h5>
<p>The specific failure in this zone, shown before it is explained. Drawn from that zone's hardest decision in the manual, so it names something the viewer has genuinely been avoiding rather than generic mess.</p>
<span class="tagchip zone">Written per zone</span></div>
<div class="beat"><div class="n">Beat 2 &middot; about 20s</div><h5>What 6S is</h5>
<p>Six steps, always in the same order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth S. Animated title cards over b-roll, cut once and reused on every episode.</p>
<span class="tagchip fixed">Fixed, recorded once</span></div>
<div class="beat"><div class="n">Beat 3 &middot; about 20s</div><h5>The solution</h5>
<p>The 6S Success Home Edition Micro Zone Room Reset. Rooms fail because a room is not a unit of work; a micro zone is. Ends on the promise line and this episode's zone name and session length.</p>
<span class="tagchip fixed">Fixed frame, zone name swapped</span></div>
</div>

<div class="what"><h4>Why the opener is not identical every time</h4><ul>
<li>A verbatim repeat gets skipped by returning viewers, and the skip lands right where retention is measured.</li>
<li>Beat 1 doubles as the hook, so it has to be about the viewer's drawer, not about the series.</li>
<li>Beats 2 and 3 stay fixed so the method and the promise never drift, and so they only ever need recording once.</li>
</ul></div>

<h2><span class="kick">Format</span>Headless production standard</h2>
<div class="grid2">
<div class="gcard"><h5>Camera</h5><ul>
<li>No presenter on camera at any point. Hands only, never above the wrists.</li>
<li>Two setups per zone: overhead on a tripod arm, and a three-quarter angle at working height.</li>
<li>Detail and macro inserts carry the teaching. Cut to the object being discussed, not to a wide.</li>
<li>Static frames by default. Movement only where it shows a reach or a path.</li></ul></div>
<div class="gcard"><h5>Light and sound</h5><ul>
<li>Window light wherever possible, one bounce card to lift shadows in cabinets and drawers.</li>
<li>Interiors of closets and under-sink zones need a small fill; plan it, do not fix it in post.</li>
<li>Voiceover recorded separately in a quiet room. Never rely on on-set audio.</li>
<li>Keep real object sound as texture, mixed under the voice.</li></ul></div>
<div class="gcard"><h5>On-screen text</h5><ul>
<li>A few words at a time, never a sentence the narrator is also saying.</li>
<li>Step name persists in a corner chip through each segment, in that step's colour.</li>
<li>Counts and limits get text; explanations stay in voiceover.</li></ul></div>
<div class="gcard"><h5>Pace and structure</h5><ul>
<li>Opener, then six segments in canonical order, then the close. No exceptions.</li>
<li>Real-time work compressed, but never so fast the decision becomes invisible. The decision is the content.</li>
<li>End on the finished standard held long enough to read, then the trigger.</li></ul></div>
</div>

<h2><span class="kick">Short form</span>Six Shorts from every episode</h2>
<p>Each segment is written to survive being lifted out on its own, which is why every one carries a hook and a note on what has to be re-established without the parent video. That yields six Shorts per zone and {n_short} across the series, from the same shoot and the same script pass.</p>
<div class="what"><h4>Rules for the cut</h4><ul>
<li>A Short opens on the problem or the result, never on the series intro.</li>
<li>It must make sense to someone who has never heard of 6S, so name the step rather than assuming it.</li>
<li>One idea per Short. If the segment carries two, cut two Shorts.</li>
<li>Point back to the full zone episode at the end, not at the start.</li></ul></div>

<h2><span class="kick">Convention</span>Numbering and publishing order</h2>
<div class="what"><h4>How episodes are identified</h4><ul>
<li><b>MZ-001</b> through <b>MZ-{n_vid:03d}</b>, a stable series number that never changes.</li>
<li><b>R02.03</b> alongside it, meaning room two, zone three, so a file name sorts the way the manual reads.</li>
<li>Shorts inherit the parent number plus the step, for example MZ-014-SAFETY.</li></ul></div>
<p>Publish in manual order, starting with the Entryway. It is the smallest room, the payoff is visible within a week, and it gives a new viewer a finished result before you ask them for a harder room. Save the Garage and the Workshop until the format is proven, because those shoots are the longest and the least forgiving.</p>

<h2><span class="kick">Index</span>Twenty rooms, {n_vid} episodes</h2>
<nav class="toc">{toc}</nav>

{"".join(sections)}
<p class="nores" id="nores">No videos match that filter.</p>
</main>
<a class="totop" href="#">Top</a>
<script>{JS}</script>
</body></html>"""

import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(doc)
print("wrote:", OUT)
print("rooms: %d  videos: %d  shorts: %d  bytes: %d" % (n_room, n_vid, n_short, len(doc)))
