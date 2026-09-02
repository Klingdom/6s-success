"""Measure text contrast and image distortion on real rendered pages.

Two defects shipped on 2026-09-01 and 2026-09-02 that no existing check could
see, because both only exist once a browser has resolved the cascade:

  1. Chapter lists on book.html rendered #EDE4D2 on #FBF7EF, a contrast of
     1.18:1 against the 4.5:1 minimum. The .card sets its own light background
     but inherited cream text from the dark .band section around it. Nothing in
     the stylesheet is wrong in isolation; only the combination is.

  2. The hero image on the same page was visibly stretched, because intrinsic
     width and height attributes were added to stop layout shift without a
     height:auto rule, so the browser honoured the literal height against a
     constrained width.

Both are invisible to grep and obvious to a person, which is exactly the class
of defect a rendering check exists for. This walks the real DOM, resolves each
text node's effective background by climbing until it finds one that is
actually painted, and compares every image's rendered aspect ratio against its
intrinsic one.

    python ops/audit_visual.py                 every page
    python ops/audit_visual.py site/book.html  one page
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

MIN_TEXT = 4.5           # WCAG AA, normal text
MIN_LARGE = 3.0          # >=24px, or >=18.66px bold
SKEW_LIMIT = 0.02        # 2 per cent off the intrinsic aspect ratio

PROBE = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:1280px;height:2600px;border:0}</style>
<iframe id="f" src="__SRC__"></iframe>
<pre id="out"></pre>
<script>
function run(){
  var d=document.getElementById('f').contentDocument;
  var w=document.getElementById('f').contentWindow;
  function lum(r,g,b){var f=function(v){v/=255;return v<=0.03928?v/12.92:
    Math.pow((v+0.055)/1.055,2.4);};
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b);}
  function parse(c){var m=c.match(/rgba?\\(([^)]+)\\)/);if(!m)return null;
    var p=m[1].split(',').map(parseFloat);
    return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
  // A gradient or image background has no single colour to compare against,
  // and climbing past it to the page white invents a contrast that is not
  // there. The dark hero reported 1.13:1 that way, on text that is actually
  // cream on near-black. Return null instead and let the caller record it as
  // unmeasured, because unchecked is not the same as failing.
  function bgOf(el){var n=el;
    while(n&&n!==d.documentElement){
      var cs=w.getComputedStyle(n);
      if(cs.backgroundImage&&cs.backgroundImage!=='none')return null;
      var c=parse(cs.backgroundColor);
      if(c&&c.a>0.5)return c; n=n.parentElement;}
    return {r:255,g:255,b:255,a:1};}
  function ratio(a,b){var la=lum(a.r,a.g,a.b),lb=lum(b.r,b.g,b.b);
    return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05);}
  var text=[],images=[];
  var all=d.querySelectorAll('body *');
  for(var i=0;i<all.length;i++){
    var el=all[i], st=w.getComputedStyle(el);
    if(st.display==='none'||st.visibility==='hidden'||parseFloat(st.opacity)<0.1)continue;
    var r=el.getBoundingClientRect();
    if(r.width<1||r.height<1)continue;
    var own='';
    for(var k=0;k<el.childNodes.length;k++){
      if(el.childNodes[k].nodeType===3)own+=' '+el.childNodes[k].textContent;}
    own=own.replace(/\\s+/g,' ').trim();
    if(own.length>1){
      var fg=parse(st.color);
      if(fg&&fg.a>0.1){
        var size=parseFloat(st.fontSize);
        var bold=parseInt(st.fontWeight,10)>=700;
        var bg=bgOf(el);
        text.push({tag:el.tagName.toLowerCase(),
          cls:String(el.className||'').slice(0,40),
          size:size, large:(size>=24||(bold&&size>=18.66)),
          ratio:bg?Math.round(ratio(fg,bg)*100)/100:null,
          sample:own.slice(0,46)});}}
    if(el.tagName==='IMG'&&el.naturalWidth>0){
      var intr=el.naturalWidth/el.naturalHeight, rend=r.width/r.height;
      images.push({src:String(el.currentSrc||el.src).split('/').pop().slice(0,44),
        intrinsic:Math.round(intr*1000)/1000,
        rendered:Math.round(rend*1000)/1000,
        skew:Math.round(Math.abs(rend/intr-1)*1000)/1000,
        fit:st.objectFit});}}
  document.getElementById('out').textContent=
    'RESULT'+JSON.stringify({text:text,images:images})+'ENDRESULT';
}
document.getElementById('f').onload=function(){setTimeout(run,400);};
</script>"""


def edge():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    return None


def audit(page: str, exe: str):
    """Returns (text[], images[]) or None if the page could not be measured."""
    # The probe sits beside the page so every relative stylesheet, font and
    # image resolves exactly as it does in production. Copying the page
    # elsewhere silently strips its CSS and reports a perfectly readable
    # unstyled document.
    probe = os.path.join(os.path.dirname(page), "_visual_probe.html")
    io.open(probe, "w", encoding="utf-8", newline="").write(
        PROBE.replace("__SRC__", os.path.basename(page)))
    try:
        p = subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--window-size=1280,2600", "--allow-file-access-from-files",
             "--virtual-time-budget=6000", "--dump-dom",
             "file:///" + probe.replace(os.sep, "/")],
            capture_output=True, text=True, timeout=120)
        m = re.search(r"RESULT(\{.*?\})ENDRESULT", p.stdout, re.S)
        if not m:
            return None
        d = json.loads(m.group(1))
        return d["text"], d["images"]
    except Exception:
        return None
    finally:
        if os.path.exists(probe):
            os.remove(probe)


def main() -> int:
    exe = edge()
    if not exe:
        print("  no browser found, so nothing was measured. "
              "Unchecked is not passing.")
        return 1

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pages = args or sorted(glob.glob(os.path.join(SITE, "*.html")))

    bad_text, bad_img, unread = [], [], []
    unmeasured = 0
    for page in pages:
        rel = os.path.relpath(page, ROOT).replace(os.sep, "/")
        if os.path.basename(page).startswith("_"):
            continue
        r = audit(page if os.path.isabs(page) else os.path.join(ROOT, page), exe)
        if r is None:
            unread.append(rel)
            continue
        text, images = r
        for t in text:
            floor = MIN_LARGE if t["large"] else MIN_TEXT
            if t["ratio"] is None:
                # Sits on a gradient or image. Not measurable this way, and
                # counted so the total never reads as full coverage.
                unmeasured += 1
                continue
            if t["ratio"] < floor:
                bad_text.append((rel, t["ratio"], floor, t["tag"], t["cls"],
                                 t["sample"]))
        for im in images:
            if im["fit"] in ("cover", "contain"):
                continue    # deliberately reframed, not distorted
            if im["skew"] > SKEW_LIMIT:
                bad_img.append((rel, im["src"], im["skew"], im["intrinsic"],
                                im["rendered"]))

    print("  pages measured        : %d" % (len(pages) - len(unread)))
    if unread:
        print("  pages NOT measured    : %d %s  (unchecked, not passing)"
              % (len(unread), unread[:3]))
    print("  text on a gradient, not measurable this way: %d" % unmeasured)
    print("  text below contrast   : %d" % len(bad_text))
    limit = None if "--all" in sys.argv else 12
    for rel, r, floor, tag, cls, sample in bad_text[:limit]:
        print("     %-26s %.2f:1 (needs %.1f) <%s class=%r> %r"
              % (rel, r, floor, tag, cls[:22], sample[:34]))
    print("  images distorted      : %d" % len(bad_img))
    for rel, src, skew, i, r in bad_img[:limit]:
        print("     %-26s %-34s %.1f%% off (intrinsic %.3f, rendered %.3f)"
              % (rel, src, skew * 100, i, r))
    return 1 if (bad_text or bad_img) else 0


if __name__ == "__main__":
    sys.exit(main())
