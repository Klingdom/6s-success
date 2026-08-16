# -*- coding: utf-8 -*-
"""Assemble the Entryway pilot shooting-script document."""
import json, io, re, html as H, os

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
OUT = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\pilot\Entryway Pilot - Shooting Scripts.html"

zones = json.load(io.open(SCRATCH + r"\pilot.json", encoding="utf-8"))["zones"]
opener = json.load(io.open(SCRATCH + r"\opener_asset.json", encoding="utf-8"))

S_ORDER = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]
S_COLOR = {"Sort": "#BC4B2A", "Straighten": "#DDA63A", "Shine": "#6E8B5B",
           "Safety": "#3C5A6B", "Standardize": "#8A6BA1", "Sustain": "#3D7A74"}

def esc(s):
    return H.escape(str(s or "").strip(), quote=False)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")

CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--honey:#DDA63A;--slate:#3C5A6B;--green:#6E8B5B;--spark:#CB4B36;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.58}
.book{max-width:960px;margin:0 auto;padding:0 26px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:50px 0 6px;max-width:680px}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(34px,6vw,54px);line-height:1.04;margin:.1em 0 .25em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(18px,2.4vw,21px);margin:0 0 6px;max-width:600px}
.lede{max-width:680px;color:var(--soft);font-size:1.02em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(23px,3.2vw,30px);line-height:1.1;margin:2em 0 .5em}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.5em}
h3{font-family:var(--display);font-weight:600;font-size:22px;margin:0}
p{margin:0 0 1em;max-width:680px}
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);backdrop-filter:blur(8px);
border-bottom:1px solid var(--rule2);padding:10px 26px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:15px;margin-right:auto}
.topbar a{font-family:var(--sans);font-size:13px;color:var(--slate);text-decoration:none;padding:4px 9px;border-radius:7px}
.topbar a:hover{background:var(--panel)}
.what{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:22px 26px 18px;margin:1.5em 0;max-width:680px}
.what h4{font-family:var(--sans);font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);font-weight:700;margin:0 0 12px}
.what ul{list-style:none;margin:0;padding:0}
.what li{position:relative;padding-left:28px;margin:.45em 0;font-size:16.5px;line-height:1.5}
.what li::before{content:"";position:absolute;left:4px;top:.55em;width:8px;height:8px;background:var(--green);border-radius:50%}
.defbox{background:var(--panel);border:2px solid var(--slate);border-radius:14px;padding:20px 26px;max-width:680px;margin:1.5em 0}
.defbox .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--slate);font-weight:700;margin-bottom:9px}
.defbox p{margin:0;font-family:var(--display);font-weight:500;font-size:20px;line-height:1.32}
/* episode */
.ep{margin-top:66px;border-top:3px solid var(--terra);padding-top:16px}
.ephead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap}
.ep .code{font-family:var(--sans);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-weight:700}
.epmeta{font-family:var(--sans);font-size:12.5px;color:var(--soft)}
.eptitle{font-family:var(--display);font-size:19px;font-weight:500;color:var(--slate);margin:6px 0 0}
.shoot{background:#f6f1e3;border-left:5px solid var(--honey);border-radius:0 10px 10px 0;padding:12px 17px;margin:14px 0;font-size:15.5px;max-width:none}
.shoot b{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#B5811E;display:block;margin-bottom:4px}
/* segment / opener block */
.blk{border:1px solid var(--rule);border-radius:13px;background:var(--panel);margin:16px 0;overflow:hidden}
.blkhead{display:flex;align-items:center;gap:12px;padding:11px 18px;border-bottom:1px solid var(--rule)}
.blkhead .chip{color:#fff;font-family:var(--sans);font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;padding:4px 12px;border-radius:6px;min-width:104px;text-align:center}
.blkhead .cf{font-family:var(--display);font-size:18px;font-weight:600}
.blkhead .secs{margin-left:auto;font-family:var(--sans);font-size:12px;color:var(--soft)}
.blkbody{padding:14px 20px 16px}
.vo{background:#fff;border:1px solid var(--rule2);border-radius:9px;padding:13px 17px;margin:0 0 13px}
.vo .lbl{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);font-weight:700;margin-bottom:5px}
.vo p{margin:0;font-size:17px;line-height:1.5;max-width:none}
.vo.varfill em{color:var(--terra);font-style:normal;font-weight:600}
h6{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:14px 0 6px}
table{width:100%;border-collapse:collapse;font-size:14px;margin:2px 0 4px}
th{background:var(--slate);color:var(--paper);text-align:left;padding:7px 9px;font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.03em}
td{padding:7px 9px;border-bottom:1px solid var(--rule);vertical-align:top}
tr:nth-child(even) td{background:#faf6ee}
td.sn{font-family:var(--sans);font-weight:700;color:var(--terra);white-space:nowrap}
td.secs{font-family:var(--sans);color:var(--green);white-space:nowrap}
.ost{list-style:none;padding:0;margin:0}
.ost li{font-family:var(--sans);font-size:13.5px;margin:.3em 0;padding-left:16px;position:relative}
.ost li::before{content:"\\25AA";color:var(--terra);position:absolute;left:0}
.ost li b{color:var(--terra)}
.short{background:#edf3ec;border:1px solid #cfe0cd;border-radius:9px;padding:12px 16px;margin-top:12px}
.short b{font-family:var(--sans);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--green);display:block;margin-bottom:5px}
.short .l{font-size:15px;margin:.25em 0}
.short .l span{font-family:var(--sans);font-size:11px;color:var(--soft);text-transform:uppercase;letter-spacing:.08em;margin-right:6px}
.close{border:1px solid var(--rule);border-left:5px solid var(--green);background:#fff;border-radius:0 12px 12px 0;padding:14px 18px;margin:14px 0}
.close .lbl{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--green);font-weight:700;margin-bottom:5px}
.slist{background:var(--panel);border:1px dashed var(--rule2);border-radius:11px;padding:16px 20px;margin:14px 0}
.slist h6{margin-top:0}
.slist ul{margin:0;padding-left:19px;font-size:15px}
.slist li{margin:.28em 0}
.totop{position:fixed;right:18px;bottom:18px;z-index:60;background:var(--slate);color:var(--paper);font-family:var(--sans);font-size:12.5px;padding:9px 14px;border-radius:20px;text-decoration:none;opacity:.9}
footer{max-width:680px;margin:70px auto 0;border-top:2px solid var(--rule2);padding-top:16px;color:var(--soft);font-family:var(--sans);font-size:14px}
@media(max-width:720px){table{font-size:13px}.blkhead .chip{min-width:80px}}
@media print{.topbar,.totop{display:none}.ep{break-before:page}.blk{break-inside:avoid}}
"""

def shot_rows(shots):
    rows = ""
    for sh in shots or []:
        rows += ("<tr><td class='sn'>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='secs'>~%ss</td></tr>"
                 % (esc(sh.get("n")), esc(sh.get("angle")), esc(sh.get("action")),
                    esc(sh.get("vo_sync")), esc(sh.get("approx_seconds"))))
    return ("<table><thead><tr><th>#</th><th>Angle</th><th>Action</th>"
            "<th>VO sync</th><th>Est.</th></tr></thead><tbody>%s</tbody></table>" % rows)

def ost_list(ost):
    return "<ul class='ost'>" + "".join(
        "<li><b>%s</b> &mdash; %s</li>" % (esc(o.get("text")), esc(o.get("when"))) for o in (ost or [])) + "</ul>"

def segment(s):
    step = s.get("step", "")
    sc = s.get("short_cut", {}) or {}
    short = ""
    if sc.get("use_as_short", True):
        short = (f"<div class='short'><b>Short cut &middot; {esc(step)}</b>"
                 f"<p class='l'><span>Intro</span>{esc(sc.get('standalone_intro_vo'))}</p>"
                 f"<p class='l'><span>End card</span>{esc(sc.get('end_card_vo'))}</p></div>")
    return f"""<div class="blk">
<div class="blkhead"><span class="chip" style="background:{S_COLOR.get(step,'#666')}">{esc(step)}</span>
<span class="cf">{esc(step)}</span><span class="secs">~{esc(s.get('target_seconds'))}s</span></div>
<div class="blkbody">
<div class="vo"><div class="lbl">Voiceover</div><p>{esc(s.get('vo'))}</p></div>
<h6>Shots</h6>{shot_rows(s.get('shots'))}
<h6>On-screen text</h6>{ost_list(s.get('on_screen_text'))}
{short}
</div></div>"""

def episode(v, i):
    segs = {s.get("step"): s for s in (v.get("segments") or [])}
    ordered = [segs[k] for k in S_ORDER if k in segs]
    return f"""<section class="ep" id="{slug(v.get('zone'))}">
<div class="ephead"><div><span class="code">{esc(v.get('episode_code'))}</span><h3>{esc(v.get('zone'))}</h3></div>
<span class="epmeta">{esc(v.get('runtime'))} &middot; thumbnail: &ldquo;{esc(v.get('thumbnail_text'))}&rdquo;</span></div>
<p class="eptitle">Title: {esc(v.get('title'))}</p>
<div class="shoot"><b>Shoot notes</b>{esc(v.get('shoot_notes'))}</div>
<div class="blk"><div class="blkhead"><span class="chip" style="background:{S_COLOR['Sort']}">Cold open</span>
<span class="cf">Beat 1 &middot; the problem</span><span class="secs">~20s</span></div>
<div class="blkbody"><div class="vo"><div class="lbl">Voiceover</div><p>{esc(v.get('cold_open_vo'))}</p></div>
<p style="font-family:var(--sans);font-size:13px;color:var(--soft);margin:6px 0 0">Then the fixed opener (beats 2 and 3) plays, with this episode&rsquo;s zone name and session length swapped into its closing line.</p></div></div>
{"".join(segment(s) for s in ordered)}
<div class="close"><div class="lbl">Close</div><p style="margin:0 0 8px;max-width:none">{esc(v.get('close_vo'))}</p>
<p style="margin:0;color:var(--soft);max-width:none"><b>Next teaser:</b> {esc(v.get('next_teaser_vo'))}</p></div>
<div class="slist"><h6>Consolidated shot list for the shoot</h6><ul>{"".join("<li>%s</li>" % esc(x) for x in (v.get('consolidated_shot_list') or []))}</ul></div>
</section>"""

# opener asset block
def opener_beat(b):
    return f"""<div class="blk"><div class="blkhead"><span class="chip" style="background:var(--slate)">Beat {esc(b.get('beat'))}</span>
<span class="cf">{esc(b.get('label'))}</span><span class="secs">~{esc(b.get('target_seconds'))}s</span></div>
<div class="blkbody"><div class="vo varfill"><div class="lbl">Voiceover</div><p>{esc(b.get('vo')).replace('[ZONE NAME]','<em>[zone name]</em>').replace('[SESSION LENGTH]','<em>[session length]</em>')}</p></div>
<h6>Shots</h6>{shot_rows(b.get('shots'))}
<h6>On-screen text</h6>{ost_list(b.get('on_screen_text'))}
</div></div>"""

nav = "".join('<a href="#%s">%s</a>' % (slug(v.get("zone")), esc(v.get("zone").split(",")[0])) for v in zones)
episodes = "".join(episode(v, i + 1) for i, v in enumerate(zones))
opener_blocks = "".join(opener_beat(b) for b in opener["beats"])

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entryway Pilot - Shooting Scripts - 6S Micro Zone Reset</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="topbar"><span class="brand">Entryway Pilot &middot; Shooting Scripts</span>
<a href="#opener">Fixed opener</a>{nav}</div>

<main class="book">
<header class="masthead">
<p class="chno">6S Success &middot; Home Edition &middot; Video Companion</p>
<p class="eyebrow">Pilot &middot; Production Scripts</p>
<h1 class="title">The Entryway Pilot</h1>
<p class="subtitle">Five shootable episodes, to prove the format before we build 114.</p>
</header>

<p class="lede">Full production scripts for the five Entryway zones: verbatim voiceover, a synced shot sequence, on-screen text, and the six Short cuts per episode. Everything is headless, no presenter on camera. Shoot these five, watch how they land, and adjust the format here before scaling to the rest of the house.</p>

<div class="what"><h4>How to read a script</h4><ul>
<li>Every episode is the fixed cold open, then six segments in order, then the close.</li>
<li>The voiceover boxes are the exact words to record. Timing estimates are targets, not measured, so let the edit breathe.</li>
<li>The shot table syncs each setup to the line of VO it plays under.</li>
<li>The green box in each segment is its Short cut: the extra intro line that lets it stand alone, and the end card back to the full episode.</li>
</ul></div>

<div class="defbox"><div class="lbl">What the pilot is testing</div>
<p>Does headless carry a full reset on its own. Is sixty seconds the right opener. Does a single segment really stand alone as a Short. Five episodes answer all three cheaply.</p></div>

<h2 id="opener"><span class="kick">Record once, reuse everywhere</span>The fixed opener</h2>
<p>Beat 1 of the cold open is written per zone and lives in each episode below. Beats 2 and 3 are the same on all 114 episodes and are recorded once as the asset below. Only the final line of beat 3 changes, where the zone name and session length are swapped in.</p>
{opener_blocks}

<h2><span class="kick">The five episodes</span>Entryway, in shooting order</h2>
<p>Shoot the room in one session, in this order. The Door, Mat, and Immediate Floor zone is the shortest and gives you somewhere to stand while you work the rest.</p>

{episodes}

<footer>
<p><b>The Entryway Pilot</b> &middot; 5 episodes, 30 Shorts &middot; Companion to 6S Success: Home Edition.</p>
<p>Six steps, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth step.</p>
</footer>
</main>
<a class="totop" href="#">Top</a>
</body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(doc)
n_short = sum(1 for v in zones for s in (v.get("segments") or []) if (s.get("short_cut") or {}).get("use_as_short", True))
print("wrote:", OUT)
print("episodes: %d  shorts: %d  bytes: %d" % (len(zones), n_short, len(doc)))
