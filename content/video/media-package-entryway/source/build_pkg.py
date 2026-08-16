# -*- coding: utf-8 -*-
"""Assemble the Entryway YouTube media package: review HTML + paste-ready .txt per video."""
import json, io, re, html as H, os

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
PKGDIR = r"C:\Users\philk\Desktop\6S-Video-Production-Plan\media-package-entryway"
OUT_HTML = PKGDIR + r"\Entryway Media Package - YouTube.html"
PASTE = PKGDIR + r"\paste"

meta = json.load(io.open(SCRATCH + r"\package.json", encoding="utf-8"))["zones"]
pilot = {z["zone"]: z for z in json.load(io.open(SCRATCH + r"\pilot.json", encoding="utf-8"))["zones"]}

S_ORDER = ["Sort", "Straighten", "Shine", "Safety", "Standardize", "Sustain"]
S_COLOR = {"Sort": "#BC4B2A", "Straighten": "#DDA63A", "Shine": "#6E8B5B",
           "Safety": "#3C5A6B", "Standardize": "#8A6BA1", "Sustain": "#3D7A74"}
INTRO_SECONDS = 60   # cold open (~20s) + fixed opener (~40s)
CLOSE_LABEL = "The finished zone"

# series-wide description boilerplate. URLs are placeholders for the channel to fill.
SERIES_BLURB = ("The 6S Micro Zone Reset is the video companion to the book 6S Success: Home Edition. "
                "Each episode resets one small zone of a home using the same six steps, in order: "
                "Sort, Straighten, Shine, Safety, Standardize, Sustain. One zone, one sitting, and a "
                "change you can see from the doorway.")
LINKS = ["The Micro Zone Manual: [link]", "6S Success: Home Edition (book): [link]",
         "Full Entryway playlist: [link]"]
SERIES_HASHTAGS = ["#6S", "#MicroZoneReset", "#HomeOrganization"]

def esc(s): return H.escape(str(s or "").strip(), quote=False)
def slug(s): return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
def mmss(sec): return "%d:%02d" % (sec // 60, sec % 60)

def chapters_for(zone):
    """Estimated chapter list from the script's segment target_seconds."""
    segs = {s["step"]: s for s in pilot[zone]["segments"]}
    rows = [(0, "Intro")]
    t = INTRO_SECONDS
    for step in S_ORDER:
        rows.append((t, step))
        t += int(segs[step].get("target_seconds") or 45)
    rows.append((t, CLOSE_LABEL))
    return rows

def full_description(m):
    zone = m["zone"]
    parts = []
    parts.append(m.get("description_hook", "").strip())
    parts.append("\n".join(p.strip() for p in (m.get("description_body") or [])))
    ch = chapters_for(zone)
    chlines = ["Chapters (estimated, replace with real timestamps after the edit):"]
    chlines += ["%s %s" % (mmss(t), lbl) for t, lbl in ch]
    parts.append("\n".join(chlines))
    parts.append(SERIES_BLURB)
    parts.append("\n".join(LINKS))
    parts.append(" ".join(SERIES_HASHTAGS))
    return "\n\n".join(p for p in parts if p)

# ---------- paste-ready text ----------
def paste_text(m):
    zone = m["zone"]
    p = pilot[zone]
    L = []
    L.append("=" * 70)
    L.append("%s  |  %s" % (p.get("episode_code", ""), zone))
    L.append("=" * 70)
    L.append("\nVIDEO TITLE\n" + p.get("title", ""))
    L.append("\nDESCRIPTION\n" + full_description(m))
    L.append("\nTAGS (comma separated)\n" + ", ".join(m.get("tags") or []))
    L.append("\nPINNED COMMENT\n" + m.get("pinned_comment", ""))
    es = m.get("end_screen") or {}
    L.append("\nEND SCREEN\n- " + "\n- ".join(es.get("features") or []) + "\nLead-in: " + es.get("note", ""))
    th = m.get("thumbnail") or {}
    L.append("\nTHUMBNAIL\nText: %s\nVisual: %s" % (th.get("text", ""), th.get("visual", "")))
    L.append("\n" + "-" * 70 + "\nSHORTS\n" + "-" * 70)
    for sh in (m.get("shorts") or []):
        L.append("\n[%s]  %s" % (sh.get("step", ""), sh.get("short_title", "")))
        L.append("Caption: " + sh.get("caption", ""))
        L.append("Hashtags: " + " ".join(sh.get("hashtags") or []))
    return "\n".join(L) + "\n"

# ---------- HTML ----------
CSS = """
:root{--paper:#F7F2E9;--panel:#FBF7EF;--ink:#2B2622;--soft:#6A625A;--terra:#BC4B2A;
--honey:#DDA63A;--slate:#3C5A6B;--green:#6E8B5B;--rule:#E2D8C4;--rule2:#D9CDB8;
--sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
--serif:"Newsreader",Georgia,"Times New Roman",serif;--display:"Fraunces",Georgia,serif;}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:66px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.58}
.book{max-width:940px;margin:0 auto;padding:0 26px 120px}
.eyebrow{font-family:var(--sans);font-size:12.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--terra);font-weight:600;margin:0}
.masthead{padding:50px 0 6px;max-width:680px}
.chno{font-family:var(--display);font-weight:900;font-size:15px;letter-spacing:.06em;color:var(--slate);text-transform:uppercase;margin:0 0 12px}
h1.title{font-family:var(--display);font-weight:600;font-size:clamp(34px,6vw,54px);line-height:1.04;margin:.1em 0 .25em}
.subtitle{font-style:italic;color:var(--soft);font-size:clamp(18px,2.4vw,21px);margin:0 0 6px;max-width:600px}
.lede{max-width:680px;color:var(--soft);font-size:1.02em}
h2{font-family:var(--display);font-weight:600;font-size:clamp(23px,3.2vw,30px);margin:2em 0 .5em}
h2 .kick{display:block;font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);margin-bottom:.5em}
h3{font-family:var(--display);font-weight:600;font-size:22px;margin:0}
p{margin:0 0 1em;max-width:680px}
.topbar{position:sticky;top:0;z-index:50;background:rgba(247,242,233,.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule2);padding:10px 26px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-family:var(--display);font-weight:600;font-size:15px;margin-right:auto}
.topbar a{font-family:var(--sans);font-size:13px;color:var(--slate);text-decoration:none;padding:4px 9px;border-radius:7px}
.topbar a:hover{background:var(--panel)}
.what{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:22px 26px 18px;margin:1.5em 0;max-width:680px}
.what h4{font-family:var(--sans);font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);font-weight:700;margin:0 0 12px}
.what ul{list-style:none;margin:0;padding:0}
.what li{position:relative;padding-left:28px;margin:.45em 0;font-size:16.5px;line-height:1.5}
.what li::before{content:"";position:absolute;left:4px;top:.55em;width:8px;height:8px;background:var(--green);border-radius:50%}
.ep{margin-top:60px;border-top:3px solid var(--terra);padding-top:16px}
.ephead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap}
.ep .code{font-family:var(--sans);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-weight:700}
.epmeta{font-family:var(--sans);font-size:12.5px;color:var(--soft)}
h5{font-family:var(--sans);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:20px 0 7px}
.copy{position:relative;background:#fff;border:1px solid var(--rule2);border-radius:10px;padding:14px 16px;margin:0 0 6px}
.copy pre{margin:0;font-family:var(--sans);font-size:14px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;color:var(--ink)}
.copy .btn{position:absolute;top:9px;right:9px;font-family:var(--sans);font-size:11px;font-weight:600;letter-spacing:.05em;background:var(--slate);color:var(--paper);border:none;border-radius:6px;padding:5px 10px;cursor:pointer;opacity:.85}
.copy .btn:hover{opacity:1}
.pill{display:inline-block;font-family:var(--sans);font-size:12px;background:#eee9de;color:var(--soft);padding:3px 10px;border-radius:14px;margin:0 5px 5px 0}
.chapters{font-family:var(--sans);font-size:14px;color:var(--ink);background:#fff;border:1px dashed var(--rule2);border-radius:10px;padding:12px 16px}
.chapters .est{color:var(--terra);font-size:12px;display:block;margin-bottom:6px;text-transform:uppercase;letter-spacing:.1em;font-weight:700}
.chapters div{padding:2px 0}
.chapters b{color:var(--slate);font-variant-numeric:tabular-nums;margin-right:10px}
.shortcard{border:1px solid var(--rule);border-radius:12px;background:var(--panel);margin:12px 0;overflow:hidden}
.shorthd{display:flex;align-items:center;gap:11px;padding:9px 15px;border-bottom:1px solid var(--rule)}
.shorthd .chip{color:#fff;font-family:var(--sans);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;padding:3px 10px;border-radius:5px;min-width:92px;text-align:center}
.shorthd .t{font-family:var(--display);font-size:16px;font-weight:600}
.shortbody{padding:12px 16px}
.totop{position:fixed;right:18px;bottom:18px;z-index:60;background:var(--slate);color:var(--paper);font-family:var(--sans);font-size:12.5px;padding:9px 14px;border-radius:20px;text-decoration:none;opacity:.9}
footer{max-width:680px;margin:70px auto 0;border-top:2px solid var(--rule2);padding-top:16px;color:var(--soft);font-family:var(--sans);font-size:14px}
@media print{.topbar,.totop,.copy .btn{display:none}.ep{break-before:page}}
"""

JS = """
document.querySelectorAll('.copy').forEach(function(box){
  var b=document.createElement('button');b.className='btn';b.textContent='Copy';
  b.addEventListener('click',function(){
    var t=box.querySelector('pre').innerText;
    navigator.clipboard.writeText(t).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy';},1400);});
  });
  box.appendChild(b);
});
"""

def copybox(text):
    return '<div class="copy"><pre>%s</pre></div>' % esc(text)

def chapters_html(zone):
    rows = chapters_for(zone)
    inner = "".join("<div><b>%s</b>%s</div>" % (mmss(t), esc(lbl)) for t, lbl in rows)
    return ('<div class="chapters"><span class="est">Estimated &middot; replace after the edit</span>%s</div>' % inner)

def short_card(sh):
    step = sh.get("step", "")
    return f"""<div class="shortcard">
<div class="shorthd"><span class="chip" style="background:{S_COLOR.get(step,'#666')}">{esc(step)}</span>
<span class="t">{esc(sh.get('short_title'))}</span></div>
<div class="shortbody">
<h5 style="margin-top:4px">Caption</h5>{copybox(sh.get('caption'))}
<h5>Hashtags</h5>{copybox(" ".join(sh.get('hashtags') or []))}
</div></div>"""

def episode_html(m):
    zone = m["zone"]
    p = pilot[zone]
    es = m.get("end_screen") or {}
    th = m.get("thumbnail") or {}
    shorts = "".join(short_card(sh) for sh in (m.get("shorts") or []))
    return f"""<section class="ep" id="{slug(zone)}">
<div class="ephead"><div><span class="code">{esc(p.get('episode_code'))}</span><h3>{esc(zone)}</h3></div>
<span class="epmeta">{esc(p.get('runtime'))} &middot; {len(m.get('shorts') or [])} Shorts</span></div>
<h5>Video title</h5>{copybox(p.get('title'))}
<h5>Description (paste as-is)</h5>{copybox(full_description(m))}
<h5>Chapters</h5>{chapters_html(zone)}
<h5>Tags</h5>{copybox(", ".join(m.get('tags') or []))}
<h5>Pinned comment</h5>{copybox(m.get('pinned_comment'))}
<h5>End screen</h5>
<div class="what" style="margin:.4em 0"><ul>{"".join("<li>%s</li>" % esc(f) for f in (es.get('features') or []))}</ul>
<p style="margin:.4em 0 0;font-size:15px;color:var(--soft)">Lead-in: {esc(es.get('note'))}</p></div>
<h5>Thumbnail</h5>
<div class="what" style="margin:.4em 0"><ul><li><b>Text:</b> {esc(th.get('text'))}</li>
<li><b>Visual:</b> {esc(th.get('visual'))}</li></ul></div>
<h5>Shorts &middot; individual copy</h5>{shorts}
</section>"""

nav = "".join('<a href="#%s">%s</a>' % (slug(m["zone"]), esc(m["zone"].split(",")[0])) for m in meta)
episodes = "".join(episode_html(m) for m in meta)
n_short = sum(len(m.get("shorts") or []) for m in meta)

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entryway Media Package - YouTube - 6S Micro Zone Reset</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="topbar"><span class="brand">Entryway Media Package &middot; YouTube</span>{nav}</div>

<main class="book">
<header class="masthead">
<p class="chno">6S Success &middot; Home Edition &middot; Video Companion</p>
<p class="eyebrow">Media Package &middot; YouTube</p>
<h1 class="title">Entryway, Ready to Publish</h1>
<p class="subtitle">Titles, descriptions, chapters, tags, pinned comments, end screens, thumbnails, and Shorts copy for all five episodes.</p>
</header>

<p class="lede">Everything you paste into YouTube to publish the five Entryway episodes and their {n_short} Shorts. Each block has a copy button. The same text is in the paste folder as one .txt per episode.</p>

<div class="what"><h4>Before you publish</h4><ul>
<li>Chapter timestamps are estimated from the scripts. Replace them with real ones after the edit, keeping the first at 0:00.</li>
<li>Links in the descriptions are placeholders in square brackets. Drop in your real channel, playlist, book, and manual URLs.</li>
<li>Thumbnails are headless: an object or a before and after, never a face.</li>
<li>Publish in this order. The Door, Mat, and Immediate Floor episode is the shortest and the best first upload.</li>
</ul></div>

{episodes}

<footer>
<p><b>Entryway Media Package</b> &middot; 5 episodes, {n_short} Shorts &middot; Companion to 6S Success: Home Edition.</p>
<p>Six steps, in order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety is the fourth step.</p>
</footer>
</main>
<a class="totop" href="#">Top</a>
<script>{JS}</script>
</body></html>"""

os.makedirs(PKGDIR, exist_ok=True)
os.makedirs(PASTE, exist_ok=True)
io.open(OUT_HTML, "w", encoding="utf-8").write(doc)
for m in meta:
    code = pilot[m["zone"]].get("episode_code", "").split(".")[0].strip().replace(" ", "")
    fn = "%s - %s.txt" % (code or slug(m["zone"]), slug(m["zone"]))
    io.open(os.path.join(PASTE, fn), "w", encoding="utf-8").write(paste_text(m))

print("wrote:", OUT_HTML)
print("episodes: %d  shorts: %d  bytes: %d" % (len(meta), n_short, len(doc)))
print("paste files:", len(meta))
