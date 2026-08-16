# -*- coding: utf-8 -*-
"""Assemble The Micro Zone Manual v3 from workflow JSON, in the book's design system."""
import json, io, re, sys, html as H

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
OUT = (r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting"
       r"\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master"
       r"\6S Success Home Edition\6S Home Micro Zone SOP Field Manual v3.html")

data = json.load(io.open(SCRATCH + r"\content.json", encoding="utf-8"))
rooms = data["rooms"] if isinstance(data, dict) else data

S_ORDER = ["sort", "straighten", "shine", "safety", "standardize", "sustain"]
S_NAME = {"sort": "Sort", "straighten": "Straighten", "shine": "Shine",
          "safety": "Safety", "standardize": "Standardize", "sustain": "Sustain"}
S_COLOR = {"sort": "#BC4B2A", "straighten": "#DDA63A", "shine": "#6E8B5B",
           "safety": "#3C5A6B", "standardize": "#8A6BA1", "sustain": "#3D7A74"}
S_GLOSS = {
    "sort": "Keep what serves the zone, route out the rest.",
    "straighten": "A home for everything, chosen by how it is used.",
    "shine": "Clean to inspect, not just to impress.",
    "safety": "The step that protects everything else.",
    "standardize": "Make the right state obvious at a glance.",
    "sustain": "Design the habit, do not rely on willpower.",
}

# Frozen canon lines from the book. Agents quote these verbatim and are meant to;
# they arrive inconsistently punctuated, so present them uniformly as quotations.
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

CSS = """
:root{
 --paper:#F7F2E9; --panel:#FBF7EF; --ink:#2B2622; --soft:#6A625A;
 --terra:#BC4B2A; --honey:#DDA63A; --slate:#3C5A6B;
 --green:#6E8B5B; --spark:#CB4B36; --rule:#E2D8C4; --rule2:#D9CDB8;
 --plum:#8A6BA1; --teal:#3D7A74;
 --sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
 --serif:"Newsreader",Georgia,"Times New Roman",serif;
 --display:"Fraunces",Georgia,serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:19px;line-height:1.62}
.book{max-width:1000px;margin:0 auto;padding:0 28px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:56px 0 8px;max-width:664px;margin:0 auto}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 14px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(38px,7vw,64px);line-height:1.02;letter-spacing:-.015em;margin:.1em 0 .25em}
.subtitle{font-family:var(--serif);font-style:italic;color:var(--soft);font-size:clamp(18px,2.5vw,22px);margin:0 0 6px;max-width:560px}
.lede{max-width:664px;margin:18px auto 0;color:var(--soft);font-size:1.04em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(25px,3.4vw,32px);line-height:1.1;letter-spacing:-.01em;margin:2.4em auto .55em}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.5em}
h3{font-family:var(--display);font-weight:600;font-size:24px;margin:0;letter-spacing:-.01em}
.prose{max-width:664px;margin:0 auto}
.prose p{margin:0 auto 1.05em}
.pull{font-family:var(--display);font-weight:500;font-size:clamp(22px,3.4vw,29px);line-height:1.24;color:var(--slate);border-top:2px solid var(--rule2);border-bottom:2px solid var(--rule2);padding:.7em 0;margin:1.8em auto;max-width:664px}
.what{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:26px 30px 22px;margin:2em auto 1.4em;max-width:664px}
.what h4{font-family:var(--sans);font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);font-weight:700;margin:0 0 14px}
.what ul{list-style:none;margin:0;padding:0}
.what li{position:relative;padding-left:30px;margin:.5em 0;font-size:17.5px;line-height:1.5}
.what li::before{content:"";position:absolute;left:4px;top:.55em;width:9px;height:9px;background:var(--green);border-radius:50%}
.defbox{background:var(--panel);border:2px solid var(--slate);border-radius:14px;padding:24px 28px;max-width:664px;margin:1.8em auto}
.defbox .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--slate);font-weight:700;margin-bottom:10px}
.defbox p{margin:0;font-family:var(--display);font-weight:500;font-size:22px;line-height:1.3}
.idea{background:var(--ink);color:var(--paper);border-radius:16px;padding:30px 34px;max-width:664px;margin:2.2em auto}
.idea .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--honey);font-weight:700;margin-bottom:10px}
.idea p{margin:0;font-family:var(--display);font-weight:500;font-size:23px;line-height:1.3}
/* six S definitions */
.sixs{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1.6em 0}
.sdef{background:var(--panel);border:1px solid var(--rule);border-left:6px solid var(--rule);border-radius:12px;padding:16px 20px}
.sdef .n{font-family:var(--sans);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--soft);font-weight:700}
.sdef h4{font-family:var(--display);font-size:21px;margin:2px 0 4px;font-weight:600}
.sdef p{margin:0;font-size:16px;color:var(--soft);line-height:1.45}
/* table of contents */
.toc{columns:3;column-gap:28px;background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:22px 26px;margin:1.4em 0}
.toc a{display:block;color:var(--ink);text-decoration:none;margin:7px 0;font-size:16px;break-inside:avoid}
.toc a span{font-family:var(--sans);font-size:12px;color:var(--soft);display:block}
.toc a:hover{color:var(--terra)}
/* rooms */
.room{margin-top:86px}
.roomhead{border-bottom:3px solid var(--terra);padding-bottom:12px;margin-bottom:18px;display:flex;align-items:baseline;justify-content:space-between;gap:20px;flex-wrap:wrap}
.roomhead h2{margin:0;font-size:clamp(28px,4vw,38px)}
.roomstat{font-family:var(--sans);font-size:13.5px;color:var(--soft);white-space:nowrap}
.roomintro{font-size:18px;max-width:760px;margin:0 0 18px}
.tips{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:0 0 30px}
.tip{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 17px;font-size:15.5px;line-height:1.48}
.tip b{display:block;font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px;color:var(--terra)}
.tip.t1 b{color:var(--terra)} .tip.t2 b{color:var(--teal)} .tip.t3 b{color:var(--spark)}
/* zone cards */
.zone{background:var(--panel);border:1px solid var(--rule);border-radius:16px;padding:24px 28px 20px;margin:22px 0;break-inside:avoid}
.zhead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:4px}
.zmeta{font-family:var(--sans);font-size:13px;color:var(--soft);white-space:nowrap}
.zmeta b{color:var(--slate);font-weight:600}
.zpurpose{font-style:italic;color:var(--soft);margin:0 0 14px;font-size:17px}
.done{background:#fff;border:1px dashed var(--rule2);border-radius:10px;padding:14px 18px;margin:0 0 16px}
.done .lbl{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:700;margin-bottom:5px}
.done p{margin:0;font-size:17px;line-height:1.5}
.passes{list-style:none;margin:0 0 16px;padding:0}
.passes li{position:relative;padding-left:112px;margin:.62em 0;font-size:16.5px;line-height:1.5;min-height:26px}
.passes .s{position:absolute;left:0;top:2px;font-family:var(--sans);font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:#fff;padding:3px 9px;border-radius:5px;width:98px;text-align:center}
.call{border:1px solid var(--rule);border-left:5px solid var(--terra);background:#fff;border-radius:0 12px 12px 0;padding:16px 20px;margin:0 0 14px}
.call .lbl{font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--terra);margin-bottom:6px}
.call h5{font-family:var(--display);font-size:18.5px;margin:0 0 5px;font-weight:600}
.call p{margin:0;font-size:16.5px;line-height:1.5}
.watch{border:1px solid var(--rule);border-left:5px solid var(--slate);background:#fff;border-radius:0 12px 12px 0;padding:16px 20px;margin:0 0 14px}
.watch .lbl{font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);margin-bottom:8px}
.watch ul{list-style:none;margin:0;padding:0}
.watch li{font-size:16.5px;line-height:1.5;margin:.4em 0}
.watch li b{font-family:var(--sans);font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--slate);font-weight:700;display:block}
.leave{border:1px solid var(--rule);border-left:5px solid var(--green);background:#fff;border-radius:0 12px 12px 0;padding:16px 20px}
.leave .lbl{font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--green);margin-bottom:6px}
.leave p{margin:0 0 5px;font-size:16.5px;line-height:1.5}
.leave .trig{color:var(--soft);margin:0}
.leave .trig b{font-family:var(--sans);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--green);font-weight:700}
.xref{font-family:var(--sans);font-size:13.5px;color:var(--soft);margin:12px 0 0;font-style:normal}
.xref::before{content:"\\2192 ";color:var(--terra)}
.checklist{max-width:664px;margin:1.5em auto;background:var(--panel);border:1px dashed var(--rule2);border-radius:12px;padding:22px 26px}
.checklist h4{font-family:var(--sans);font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:0 0 12px}
.checklist ul{list-style:none;margin:0;padding:0}
.checklist li{position:relative;padding-left:34px;margin:.55em 0;font-size:17px;line-height:1.45}
.checklist li::before{content:"";position:absolute;left:0;top:.05em;width:19px;height:19px;border:2px solid var(--slate);border-radius:5px}
.gloss{columns:2;column-gap:40px;margin-top:1.2em}
.gloss>div{break-inside:avoid;margin-bottom:14px}
.gloss dt{font-family:var(--display);font-weight:600;font-size:18px;margin-bottom:2px}
.gloss dd{margin:0;font-size:16px;color:var(--soft);line-height:1.45}
footer{max-width:664px;margin:80px auto 0;border-top:2px solid var(--rule2);padding-top:18px;color:var(--soft);font-family:var(--sans);font-size:14px}
/* How to clean it (deepened Shine) */
.clean{border:1px solid var(--rule);border-left:5px solid var(--green);background:#fff;border-radius:0 12px 12px 0;padding:16px 20px;margin:0 0 14px}
.clean .lbl{font-family:var(--sans);font-size:11.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--green);margin-bottom:6px}
.clean .sum{margin:0 0 12px;font-size:16.5px;line-height:1.5}
.clean table{width:100%;border-collapse:collapse;font-size:15px;margin:0 0 12px}
.clean th{background:var(--green);color:#fff;text-align:left;padding:7px 10px;font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}
.clean td{padding:7px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
.clean tr:nth-child(even) td{background:#f7faf5}
.clean td.surf{font-weight:600;color:var(--slate);width:32%}
.clean h6{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:700;margin:12px 0 6px}
.clean .prod span{display:inline-block;font-family:var(--sans);font-size:12.5px;background:#eef3ea;color:#4a6340;padding:3px 10px;border-radius:13px;margin:0 5px 5px 0}
.clean .inspect{list-style:none;margin:0;padding:0}
.clean .inspect li{position:relative;padding-left:22px;margin:.32em 0;font-size:15px;line-height:1.45}
.clean .inspect li::before{content:"\\1F50D";position:absolute;left:0;font-size:12px;top:.15em}
@media(max-width:820px){.sixs,.tips{grid-template-columns:1fr}.toc{columns:2}.passes li{padding-left:0}.passes .s{position:static;display:inline-block;margin-bottom:4px}.clean td.surf{width:auto}}
@media(max-width:640px){body{font-size:17.5px}.toc{columns:1}.gloss{columns:1}.book{padding:0 18px 80px}}
@media print{body{background:#fff}.room{break-before:page}.zone{break-inside:avoid;border-color:#ccc}}
"""

def clean_block(z):
    """The deepened Shine 'How to clean it' block, rendered only if present."""
    sd = z.get("shine_detail")
    if not sd:
        return ""
    surfaces = "".join(
        "<tr><td class='surf'>%s</td><td>%s</td></tr>" % (esc(s.get("surface")), esc(s.get("method")))
        for s in (sd.get("surfaces") or []))
    prods = "".join("<span>%s</span>" % esc(p) for p in (sd.get("products_used") or []))
    inspect = "".join("<li>%s</li>" % esc(i) for i in (sd.get("inspect_as_you_clean") or []))
    return f"""<div class="clean"><div class="lbl">How to clean it</div>
<p class="sum">{esc(sd.get('shine_summary'))}</p>
<table><thead><tr><th>Surface or area</th><th>Method</th></tr></thead><tbody>{surfaces}</tbody></table>
<h6>What you clean with</h6><div class="prod">{prods}</div>
<h6>Inspect as you clean</h6><ul class="inspect">{inspect}</ul></div>"""

def zone_card(z, room_slug):
    p = z.get("passes", {}) or {}
    passes = "".join(
        '<li><span class="s" style="background:%s">%s</span>%s</li>' % (
            S_COLOR[k], S_NAME[k], esc(p.get(k, "")))
        for k in S_ORDER if p.get(k))
    watch = "".join(
        "<li><b>%s</b>%s</li>" % (esc(w.get("question", "")), esc(w.get("text", "")))
        for w in (z.get("watch_for") or []))
    call = z.get("the_call", {}) or {}
    leave = z.get("leave_behind", {}) or {}
    xref = z.get("chapter_ref")
    tn = z.get("time_note", "")
    # zone names repeat across rooms (two bathrooms both have a Toilet Area),
    # so ids are namespaced by room
    return f"""<article class="zone" id="{room_slug}--{slug(z.get('zone',''))}">
<div class="zhead"><h3>{esc(z.get('zone'))}</h3>
<span class="zmeta"><b>{esc(z.get('session'))}</b>{(", " + esc(tn)) if tn else ""}</span></div>
<p class="zpurpose">{esc(z.get('purpose'))}</p>
<div class="done"><div class="lbl">Done looks like</div><p>{esc(z.get('done_looks_like'))}</p></div>
<ul class="passes">{passes}</ul>
{clean_block(z)}
<div class="call"><div class="lbl">The call that matters here</div><h5>{esc(call.get('title'))}</h5><p>{esc(call.get('text'))}</p></div>
<div class="watch"><div class="lbl">Watch for</div><ul>{watch}</ul></div>
<div class="leave"><div class="lbl">Leave behind</div><p>{esc(leave.get('standard'))}</p>
<p class="trig"><b>Trigger:</b> {esc(leave.get('trigger'))}</p></div>
{f'<p class="xref">{esc(xref)}</p>' if xref else ''}
</article>"""

def room_section(r, i, total):
    tipcls = {"Where to start": "t1", "Cleaning note": "t2", "The trap": "t3"}
    tips = "".join(
        '<div class="tip %s"><b>%s</b>%s</div>' % (
            tipcls.get(t.get("label"), "t1"), esc(t.get("label")), esc(t.get("text")))
        for t in (r.get("tips") or []))
    rslug = slug(r.get("room"))
    zones = "".join(zone_card(z, rslug) for z in (r.get("zones") or []))
    n = len(r.get("zones") or [])
    return f"""<section class="room" id="{rslug}">
<div class="roomhead"><div><p class="eyebrow">Room {i:02d} of {total}</p><h2>{esc(r.get('room'))}</h2></div>
<span class="roomstat">{n} zone{'s' if n != 1 else ''}</span></div>
<p class="roomintro">{esc(r.get('intro'))}</p>
<div class="tips">{tips}</div>
{zones}
</section>"""

total_rooms = len(rooms)
total_zones = sum(len(r.get("zones") or []) for r in rooms)

sixs = "".join(
    '<div class="sdef" style="border-left-color:%s"><div class="n">%s S</div><h4>%s</h4><p>%s</p></div>' % (
        S_COLOR[k], ["First", "Second", "Third", "Fourth", "Fifth", "Sixth"][i], S_NAME[k], S_GLOSS[k])
    for i, k in enumerate(S_ORDER))

toc = "".join(
    '<a href="#%s">%s<span>%d zones</span></a>' % (slug(r.get("room")), esc(r.get("room")), len(r.get("zones") or []))
    for r in rooms)

body = "".join(room_section(r, i + 1, total_rooms) for i, r in enumerate(rooms))

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Micro Zone Manual - 6S Success Home Edition</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><main class="book">

<header class="masthead">
<p class="chno">6S Success &middot; Home Edition &middot; Companion Volume</p>
<p class="eyebrow">The Field Reference</p>
<h1 class="title">The Micro Zone Manual</h1>
<p class="subtitle">One shelf, one drawer, one corner at a time.</p>
</header>

<div class="prose">
<p class="lede">The book taught you the six steps. This is the book you carry to the shelf. {total_zones} micro zones across {total_rooms} rooms, each one small enough to finish in a single sitting, each one ending in a change you can see from the doorway.</p>

<h2><span class="kick">Why zones</span>Small enough to finish</h2>
<p>Most home projects fail on scope, not on effort. You set out to do the kitchen, you are four hours in with every cupboard on the floor, and dinner still has to happen. The room beat you because a room is not a unit of work.</p>
<p>A micro zone is. One drawer. One shelf. The strip of counter beside the kettle. Small enough that you finish, and finishing is the whole point, because a finished zone is proof, and proof is what carries you to the next one.</p>

<div class="defbox"><div class="lbl">Micro zone</div>
<p>The smallest patch of your home that can be finished in one sitting and judged from the doorway.</p></div>

<h2><span class="kick">The method</span>Six steps, always in this order</h2>
<p>The order is not decoration. Each step cuts the work of the next: sorting first means you straighten fewer things, straightening first means you clean around less, and safety lands where it can still change the layout rather than merely comment on it.</p>
</div>

<div class="sixs">{sixs}</div>

<div class="prose">
<div class="what"><h4>How to use this manual</h4><ul>
<li>Pick one zone. Not a room, not a floor. One zone.</li>
<li>Read its card before you touch anything, including "Done looks like".</li>
<li>Work the six steps in order, without skipping ahead to the satisfying ones.</li>
<li>Stop when the card says you are done. Resist the pull into the next zone on the same day.</li>
<li>Set the trigger before you walk away. A zone without a trigger comes undone.</li>
</ul></div>

<h2><span class="kick">Where to begin</span>Start with the entryway</h2>
<p>Run the entryway first. It is small, it is fast, and it is the room your household crosses twice a day, so the payoff shows up before anyone has time to lose faith in the project. Belief is a resource, and early rooms are how you fund it.</p>
<p>After that, go where the friction is loudest. The zone you swear at at seven in the morning is worth more than the zone that merely looks untidy on a Sunday.</p>

<div class="idea"><div class="lbl">One idea to keep</div>
<p>A finished zone is worth more than three started rooms.</p></div>

<h2><span class="kick">Contents</span>Twenty rooms</h2>
</div>
<nav class="toc">{toc}</nav>

{body}

<section class="room" id="keeping-it">
<div class="roomhead"><div><p class="eyebrow">Afterward</p><h2>Keeping It</h2></div></div>
<div class="prose">
<p>Every zone in this manual can be undone in a week. That is not pessimism, it is just how houses work: life pushes, and a standard with nothing behind it gives way. The sixth S is the answer, and it is mechanical rather than moral. You do not need more discipline. You need a trigger, a name, and a check that is short enough to actually happen.</p>

<h2><span class="kick">The rhythm</span>Three loops, three speeds</h2>
<div class="what"><h4>The keeping rhythm</h4><ul>
<li><b>The daily reset.</b> Two or three high-traffic zones, returned to standard, attached to something you already do. The kitchen counter while the coffee brews. The entry tray when you hang up your coat.</li>
<li><b>The weekly walk.</b> One room, card in hand, checking the zones against their "Done looks like". Ten minutes, not an afternoon.</li>
<li><b>The seasonal return.</b> One room re-run properly, four times a year. Homes change, and a standard set in March may be wrong by October.</li>
</ul></div>

<h2><span class="kick">The check</span>The two-minute zone audit</h2>
<p>Stand at the doorway and ask five questions. If you answer no to any of them, the fix is usually smaller than you fear, and it is almost always the standard rather than the household.</p>
</div>
<div class="checklist"><h4>Two-minute zone audit</h4><ul>
<li>Does the zone match its "Done looks like", from the doorway, without squinting?</li>
<li>Is anything here that does not belong to this zone?</li>
<li>Does everything present have a home, and is that home obvious to someone else?</li>
<li>Has a new hazard appeared since the last look?</li>
<li>Did the trigger actually fire this week, or did you rely on remembering?</li>
</ul></div>
<div class="prose">
<div class="defbox"><div class="lbl">The rule</div>
<p>An audit checks the home, not the household. What it finds is always a system to fix, never a person to blame.</p></div>
<p>If a zone fails the same question three times, stop repairing it and redesign it. Three failures is not a discipline problem, it is the zone telling you the standard was wrong. Lower the bar until it holds, then raise it slowly if you still want to.</p>

<h2><span class="kick">Words</span>Glossary</h2>
</div>
<dl class="gloss">
<div><dt>Micro zone</dt><dd>The smallest patch of home that can be finished in one sitting and judged from the doorway.</dd></div>
<div><dt>Done looks like</dt><dd>The zone's target state, written concretely enough to photograph. The written form of an ideal-state photo.</dd></div>
<div><dt>Holding bin</dt><dd>A dated container for genuinely undecided items, so one hard call cannot stall a whole session.</dd></div>
<div><dt>Trigger</dt><dd>An event that already happens in your house, used to start a reset. Not a reminder, not an app.</dd></div>
<div><dt>Standard</dt><dd>The best way you know today, written down. Living and updatable, not a cage.</dd></div>
<div><dt>Visual control</dt><dd>A label, outline, or boundary that makes the right state obvious without anyone explaining it.</dd></div>
<div><dt>The friendly audit</dt><dd>A short, regular, expected check that catches drift while it is still small.</dd></div>
<div><dt>Drift</dt><dd>The slow return of a zone toward its old state. Normal, expected, and cheap to fix early.</dd></div>
</dl>
</section>

<footer>
<p><b>The Micro Zone Manual</b> &middot; Companion volume to 6S Success: Home Edition &middot; {total_rooms} rooms, {total_zones} micro zones.</p>
<p>The six S's, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth S.</p>
</footer>
</main></body></html>"""

io.open(OUT, "w", encoding="utf-8").write(doc)
print("wrote:", OUT)
print("rooms: %d  zones: %d  bytes: %d" % (total_rooms, total_zones, len(doc)))
