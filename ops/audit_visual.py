"""Measure text contrast, image distortion and mobile usability on real
rendered pages.

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

2026-09-03, three gaps closed, each of which was hiding real live defects:

  * **Gradients were counted as "not measurable" and skipped.** 62 text nodes
    across the site sat on one and were silently excluded from every previous
    clean result. A gradient is not unmeasurable, it is a list of colour
    stops, and the honest reading is the *worst* stop: text that clears 4.5:1
    at the light end of a ramp and fails at the dark end fails. Stops are now
    parsed, translucent layers are composited over whatever is actually
    beneath them, and only a real raster or SVG background behind text is
    still reported unknown, because that one genuinely cannot be resolved from
    computed style alone. Inventing a number there would be worse than
    admitting it.

  * **Only 1280px was ever rendered.** CLAUDE.md section 44 says most
    household use is expected on phones, and nothing had ever measured a
    phone. --mobile renders at 390px, where different media queries apply and
    different colours, sizes and layouts are in play.

  * **Nothing checked the things a person notices before contrast:** targets
    too small to hit, a page that scrolls sideways, images with no intrinsic
    size to reserve space with, images with no alt text, heading levels that
    skip, inputs with no label. All are computable from the same rendered DOM
    for free, so they are computed here rather than in a fourth tool.

    python ops/audit_visual.py                  every page, desktop
    python ops/audit_visual.py --mobile         every page at 390px
    python ops/audit_visual.py site/book.html   one page
    python ops/audit_visual.py --live           also prove production serves
                                                the same bytes that were
                                                measured

--live matters because of CLAUDE.md 0.3: the repository is not the product.
This tool renders local files, so a clean result says nothing about the live
site unless the live site is serving those exact files. --live fetches each
page over HTTPS and compares, and reports any page where it does not, so a
pass can never quietly be a pass for the wrong artefact.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "ops"))

MIN_TEXT = 4.5           # WCAG AA, normal text
MIN_LARGE = 3.0          # >=24px, or >=18.66px bold
SKEW_LIMIT = 0.02        # 2 per cent off the intrinsic aspect ratio
MIN_TARGET = 24          # WCAG 2.2 AA 2.5.8, minimum target size
COMFY_TARGET = 44        # not a WCAG floor; the platform guidance both
                         # Apple and Google publish, reported as advisory
LIVE_ORIGIN = "https://6s-success.com"

PROBE = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:__W__px;height:__H__px;border:0}</style>
<iframe id="f" src="__SRC__"></iframe>
<pre id="out"></pre>
<script>
// Headless Chromium reports pointer:fine and hover:hover no matter how narrow
// the window is, because those describe the input device and not the viewport.
// site.css puts its entire 44px touch-target block behind
// @media (pointer: coarse), so a naive 390px render measures a narrow desktop
// window and reports touch targets that no phone has ever seen. Rather than
// report a number for a configuration nobody uses, the coarse-pointer and
// hover:none blocks are lifted out and re-applied unconditionally, at the end
// of the cascade so they win exactly as they would on a phone. If a stylesheet
// cannot be read, that is reported rather than passed over: a page whose touch
// rules could not be applied has not been measured as a phone.
function coarsify(d){
  var css='',failed=0;
  function walk(rules){
    for(var i=0;i<rules.length;i++){
      var r=rules[i];
      if(r.type===4){                       // CSSMediaRule
        var c=String(r.conditionText||r.media.mediaText||'');
        if(/pointer\\s*:\\s*coarse|hover\\s*:\\s*none|any-pointer\\s*:\\s*coarse/.test(c)){
          for(var j=0;j<r.cssRules.length;j++)css+=r.cssRules[j].cssText+'\\n';
        } else if(!/print/.test(c)){
          walk(r.cssRules);                 // width queries already applied
        }
      } else if(r.type===12&&r.cssRules){walk(r.cssRules);}
    }
  }
  for(var s=0;s<d.styleSheets.length;s++){
    try{walk(d.styleSheets[s].cssRules);}catch(e){failed++;}
  }
  if(css){var st=d.createElement('style');st.setAttribute('data-coarse','1');
    st.textContent=css;d.head.appendChild(st);}
  return failed;
}
function run(){
  var fr=document.getElementById('f');
  var d=fr.contentDocument;
  var w=fr.contentWindow;
  var sheetsUnreadable=__COARSE__?coarsify(d):0;
  var WHITE={r:255,g:255,b:255,a:1};
  function lum(r,g,b){var f=function(v){v/=255;return v<=0.03928?v/12.92:
    Math.pow((v+0.055)/1.055,2.4);};
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b);}
  function parse(c){var m=c.match(/rgba?\\(([^)]+)\\)/);if(!m)return null;
    var p=m[1].split(',').map(parseFloat);
    return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
  // A gradient is not an unmeasurable background, it is a list of stops, and
  // the honest reading of text sitting on one is its WORST stop. Only a real
  // raster or SVG image behind the text cannot be resolved from computed
  // style, and that case still returns null on purpose: unchecked is not the
  // same as failing, and inventing a ratio is worse than either.
  function stopsOf(bgi){
    if(bgi.indexOf('url(')>=0)return null;
    if(bgi.indexOf('gradient')<0)return null;
    var out=[],re=/rgba?\\(([^)]+)\\)/g,m;
    while((m=re.exec(bgi))){var p=m[1].split(',').map(parseFloat);
      out.push({r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1});}
    return out.length?out:null;}
  function over(fg,bg){var a=fg.a;
    return {r:fg.r*a+bg.r*(1-a),g:fg.g*a+bg.g*(1-a),
            b:fg.b*a+bg.b*(1-a),a:1};}
  // Returns the set of colours that can appear behind this element's own
  // text, or null when something in the stack is a real image.
  function bgAt(n,depth){
    if(!n||n===d.documentElement||depth>40)return [WHITE];
    var cs=w.getComputedStyle(n);
    var stack=[];                       // this element's paint, bottom first
    var bc=parse(cs.backgroundColor);
    if(bc&&bc.a>0.004)stack.push([bc]);
    var bgi=cs.backgroundImage;
    if(bgi&&bgi!=='none'){
      var st=stopsOf(bgi);
      if(!st)return null;               // photo or SVG: genuinely unknown
      stack.push(st);}
    if(!stack.length)return bgAt(n.parentElement,depth+1);
    var top=stack[stack.length-1],solid=true;
    for(var t=0;t<top.length;t++)if(top[t].a<0.999)solid=false;
    if(solid)return top;                // opaque, nothing below can show
    var acc=bgAt(n.parentElement,depth+1);
    if(!acc)return null;
    for(var i=0;i<stack.length;i++){
      var next=[];
      for(var j=0;j<stack[i].length;j++)
        for(var k=0;k<acc.length;k++)next.push(over(stack[i][j],acc[k]));
      acc=next.slice(0,32);}            // guard against combinatorial blowup
    return acc;}
  function ratio(a,b){var la=lum(a.r,a.g,a.b),lb=lum(b.r,b.g,b.b);
    return (Math.max(la,lb)+0.05)/(Math.min(la,lb)+0.05);}
  function where(el){var p=[],n=el,g=0;
    while(n&&n.tagName&&g<4){var s=n.tagName.toLowerCase();
      var c=String(n.className||'').split(/\\s+/)[0];
      if(c)s+='.'+c; p.unshift(s); n=n.parentElement; g++;}
    return p.join('>');}

  var text=[],images=[],targets=[],headings=[],inputs=[],overflow=[];
  var all=d.querySelectorAll('body *');
  for(var i=0;i<all.length;i++){
    var el=all[i], st=w.getComputedStyle(el);
    if(st.display==='none'||st.visibility==='hidden'||parseFloat(st.opacity)<0.1)continue;
    var r=el.getBoundingClientRect();
    if(r.width<1||r.height<1)continue;
    var tag=el.tagName.toLowerCase();
    var own='';
    for(var k=0;k<el.childNodes.length;k++){
      if(el.childNodes[k].nodeType===3)own+=' '+el.childNodes[k].textContent;}
    own=own.replace(/\\s+/g,' ').trim();
    if(own.length>1){
      var fg=parse(st.color);
      if(fg&&fg.a>0.1){
        var size=parseFloat(st.fontSize);
        var bold=parseInt(st.fontWeight,10)>=700;
        var bg=bgAt(el,0);
        var rr=null,worst=null;
        if(bg){rr=1e9;
          for(var b=0;b<bg.length;b++){
            var f=fg.a<0.999?over(fg,bg[b]):fg;
            var v=ratio(f,bg[b]);
            if(v<rr){rr=v;worst=bg[b];}}}
        text.push({tag:tag,
          cls:String(el.className||'').slice(0,40),
          size:size, large:(size>=24||(bold&&size>=18.66)),
          ratio:bg?Math.round(rr*100)/100:null,
          fgc:st.color,
          bgc:worst?('rgb('+Math.round(worst.r)+','+Math.round(worst.g)+','
                     +Math.round(worst.b)+')'):null,
          why:bg?null:st.backgroundImage.slice(0,60),
          path:where(el),
          sample:own.slice(0,46)});}}

    if(tag==='img'){
      // An image shifts the layout only if nothing reserved its box before
      // it loaded. Width and height attributes are one way; a CSS
      // aspect-ratio on the image or on the frame around it is another, and
      // the product tiles here use exactly that (.product .ph is 4/3).
      // Flagging those too would be 179 findings that are not defects, which
      // is how a check stops being read.
      var reserved=false, an=el, ad=0;
      while(an&&ad<4){
        var acs=w.getComputedStyle(an);
        if(acs.aspectRatio&&acs.aspectRatio!=='auto'){reserved=true;break;}
        an=an.parentElement; ad++;}
      var noDim=!(el.getAttribute('width')&&el.getAttribute('height'))&&!reserved;
      var alt=el.getAttribute('alt');
      images.push({src:String(el.currentSrc||el.src).split('/').pop().slice(0,44),
        intrinsic:el.naturalWidth>0?Math.round(el.naturalWidth/el.naturalHeight*1000)/1000:null,
        rendered:Math.round(r.width/r.height*1000)/1000,
        skew:el.naturalWidth>0?
          Math.round(Math.abs((r.width/r.height)/(el.naturalWidth/el.naturalHeight)-1)*1000)/1000:null,
        fit:st.objectFit, nodim:noDim,
        loaded:el.naturalWidth>0,
        alt:alt===null?null:alt,
        w:Math.round(r.width), h:Math.round(r.height)});}

    // Target size. The WCAG 2.2 exception for a link inside a sentence is
    // real and is honoured: an inline <a> whose parent block holds other text
    // is not a discrete target and is not counted.
    var role=el.getAttribute('role')||'';
    var hit=(tag==='a'&&el.getAttribute('href')!==null)||tag==='button'||
            tag==='select'||tag==='textarea'||
            (tag==='input'&&st.display!=='none')||
            role==='button'||role==='link'||
            (el.getAttribute('tabindex')&&el.getAttribute('tabindex')!=='-1');
    if(hit){
      var inline=false;
      if(tag==='a'&&st.display.indexOf('inline')===0){
        var par=el.parentElement;
        if(par){var pt=par.textContent.replace(/\\s+/g,' ').trim();
          var at=el.textContent.replace(/\\s+/g,' ').trim();
          if(pt.length>at.length+2)inline=true;}}
      if(!inline){
        targets.push({tag:tag,cls:String(el.className||'').slice(0,30),
          w:Math.round(r.width),h:Math.round(r.height),
          cx:r.left+r.width/2, cy:r.top+r.height/2,
          label:(el.textContent||el.getAttribute('aria-label')||
                 el.getAttribute('title')||'').replace(/\\s+/g,' ').trim().slice(0,30),
          path:where(el)});}}

    if(/^h[1-6]$/.test(tag))headings.push({lvl:parseInt(tag.slice(1),10),
      text:el.textContent.replace(/\\s+/g,' ').trim().slice(0,40)});

    if(tag==='input'||tag==='select'||tag==='textarea'){
      var ty=(el.getAttribute('type')||'').toLowerCase();
      if(ty!=='hidden'&&ty!=='submit'&&ty!=='button'&&ty!=='reset'){
        var id=el.id;
        var lab=id?d.querySelector('label[for="'+id+'"]'):null;
        var wrapped=el.closest?el.closest('label'):null;
        var ok=!!(lab||wrapped||el.getAttribute('aria-label')||
                  el.getAttribute('aria-labelledby')||
                  el.getAttribute('title'));
        if(!ok)inputs.push({tag:tag,type:ty,name:el.getAttribute('name')||'',
          ph:el.getAttribute('placeholder')||'',path:where(el)});}}

    // Anything painting past the right edge of the viewport is what makes a
    // phone scroll sideways. Report the widest few offenders, not every
    // descendant of one.
    if(r.right>w.innerWidth+2&&r.width>8&&st.position!=='fixed')
      overflow.push({path:where(el),right:Math.round(r.right),
        w:Math.round(r.width),
        sample:(el.textContent||'').replace(/\\s+/g,' ').trim().slice(0,30)});
  }

  // Focus visibility (WCAG 2.4.7). A keyboard or switch user who cannot see
  // where they are has no way to use the page at all, and this is not
  // inspectable without actually focusing things: a :focus-visible rule can
  // exist in the stylesheet and still be beaten by a later reset. So each
  // interactive element is really focused and its outline and box-shadow are
  // compared against its resting state. Capped, because focusing several
  // thousand elements on a long page costs more than the answer is worth and
  // the answer is nearly always a property of the component, not the instance.
  var noFocus=[];
  var focusables=d.querySelectorAll(
    'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])');
  for(var fi=0;fi<focusables.length&&fi<400;fi++){
    var fe=focusables[fi];
    var fr2=fe.getBoundingClientRect();
    if(fr2.width<1||fr2.height<1)continue;
    var before=w.getComputedStyle(fe);
    var b=[before.outlineStyle,before.outlineWidth,before.outlineColor,
           before.boxShadow,before.borderColor,before.backgroundColor,
           before.color,before.textDecorationLine].join('|');
    try{fe.focus({preventScroll:true});}catch(e){continue;}
    if(d.activeElement!==fe)continue;          // could not be focused at all
    var after=w.getComputedStyle(fe);
    var a=[after.outlineStyle,after.outlineWidth,after.outlineColor,
           after.boxShadow,after.borderColor,after.backgroundColor,
           after.color,after.textDecorationLine].join('|');
    if(a===b)noFocus.push({tag:fe.tagName.toLowerCase(),
      cls:String(fe.className||'').slice(0,30),path:where(fe),
      label:(fe.textContent||fe.getAttribute('aria-label')||'')
             .replace(/\\s+/g,' ').trim().slice(0,28)});
    try{fe.blur();}catch(e){}
  }

  // WCAG 2.2 SC 2.5.8 has a real spacing exception: an undersized target
  // still conforms if a 24px circle centred on it touches no other target's
  // circle. Without this, a tidy list of 16px links reads as a hard failure
  // when it is technically conformant, and a check that overstates is a check
  // that gets argued with instead of acted on. Undersized-and-crowded is the
  // true failure; undersized-but-spaced is reported separately and is still
  // worth fixing, because 16px is a poor thing to hit with a thumb whatever
  // the specification permits.
  for(var a1=0;a1<targets.length;a1++){
    var t1=targets[a1];
    if(Math.min(t1.w,t1.h)>=24){t1.crowded=false;continue;}
    t1.crowded=false;
    for(var a2=0;a2<targets.length;a2++){
      if(a1===a2)continue;
      var t2=targets[a2];
      var dx=t1.cx-t2.cx, dy=t1.cy-t2.cy;
      if(Math.sqrt(dx*dx+dy*dy)<24){t1.crowded=true;break;}}}

  var doc=d.documentElement;
  var land={main:d.querySelectorAll('main,[role=main]').length,
            nav:d.querySelectorAll('nav,[role=navigation]').length,
            header:d.querySelectorAll('header,[role=banner]').length,
            footer:d.querySelectorAll('footer,[role=contentinfo]').length,
            h1:d.querySelectorAll('h1').length};
  var scroll={doc:doc.scrollWidth,view:w.innerWidth};
  document.getElementById('out').textContent='RESULT'+JSON.stringify(
    {text:text,images:images,targets:targets,headings:headings,
     inputs:inputs,overflow:overflow.slice(0,6),land:land,scroll:scroll,
     sheetsUnreadable:sheetsUnreadable,noFocus:noFocus,
     fonts:(d.fonts?d.fonts.status:'unknown')})
    +'ENDRESULT';
}
// Measuring on a fixed timer produced different answers on different runs of
// the same unchanged page: the room headings on resources.html came back 44px
// tall on one run and 42px on the next, because the display face had not
// always arrived and the fallback has different metrics. That is the worst
// kind of check, one that reports "fixed" for a defect that is still there,
// so nothing is measured until the fonts have actually loaded and the images
// that are going to load have loaded. document.fonts.status travels with the
// result: a run that measured while fonts were still loading says so instead
// of quietly reporting numbers for a page nobody will ever see.
document.getElementById('f').onload=function(){
  var fr=document.getElementById('f'), d=fr.contentDocument;
  function settle(){setTimeout(run,250);}
  function afterImages(){
    var imgs=[].slice.call(d.images).filter(function(i){return !i.complete;});
    if(!imgs.length)return settle();
    var left=imgs.length, done=false;
    var finish=function(){if(!done){done=true;settle();}};
    imgs.forEach(function(i){
      var tick=function(){if(--left<=0)finish();};
      i.addEventListener('load',tick);i.addEventListener('error',tick);});
    setTimeout(finish,2500);        // a slow image must not stall the run
  }
  if(d.fonts&&d.fonts.ready){
    var raced=false;
    var go=function(){if(!raced){raced=true;afterImages();}};
    d.fonts.ready.then(go,go);
    setTimeout(go,4000);            // never hang on a font that never arrives
  } else { afterImages(); }
};
</script>"""


def audit(page: str, exe: str, extra_args: list, width: int, height: int,
          coarse: bool = False):
    """Returns the probe payload dict, or None if the page could not be
    measured. None is a real answer and must never be read as clean."""
    # The probe sits beside the page so every relative stylesheet, font and
    # image resolves exactly as it does in production. Copying the page
    # elsewhere silently strips its CSS and reports a perfectly readable
    # unstyled document.
    probe = os.path.join(os.path.dirname(page), "_visual_probe.html")
    body = (PROBE.replace("__SRC__", os.path.basename(page))
                 .replace("__W__", str(width)).replace("__H__", str(height))
                 .replace("__COARSE__", "true" if coarse else "false"))
    io.open(probe, "w", encoding="utf-8", newline="").write(body)
    try:
        p = subprocess.run(
            [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--window-size=%d,%d" % (width + 40, height),
             "--allow-file-access-from-files",
             # 6000 was less than the probe's own worst case: it waits up
             # to 4s for fonts, then up to 2.5s for images, then 250ms to
             # settle. Virtual time ran out first, the probe never wrote its
             # result, and the page came back "NOT measured" -- a different
             # one on every full run, roughly one in 190. That is reported
             # honestly rather than as a pass, but a check that randomly
             # cannot see a page is a check people stop reading, so the
             # budget now clears the probe's own ceiling.
             "--virtual-time-budget=15000", "--dump-dom", *extra_args,
             "file:///" + probe.replace(os.sep, "/")],
            capture_output=True, text=True, timeout=120)
        m = re.search(r"RESULT(\{.*?\})ENDRESULT", p.stdout, re.S)
        if not m:
            return None
        return json.loads(m.group(1))
    except Exception:
        return None
    finally:
        # Deleting the scratch file must never be able to end the run. Two
        # whole-site passes died here on WinError 32, the file still held by
        # something (the browser process winding down, or a scanner), which
        # aborted 191 pages of measuring over a temporary lock AND left the
        # probe sitting in site/articles/ afterwards, which is exactly the
        # stray-file shape issue 6.53 exists to prevent. Retry briefly, then
        # give up quietly on this one file rather than take the audit with it.
        for attempt in range(6):
            if not os.path.exists(probe):
                break
            try:
                os.remove(probe)
                break
            except OSError:
                time.sleep(0.25)


def live_url(rel: str) -> str:
    """site/index.html -> /, site/zones/x.html -> /zones/x.html."""
    path = rel[len("site/"):] if rel.startswith("site/") else rel
    if path == "index.html":
        path = ""
    elif path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return LIVE_ORIGIN + "/" + path


def live_matches(rel: str, local: str):
    """True/False/None: same bytes as production, different, or could not ask.

    None is deliberately distinct from False. A network failure has not proved
    production is stale, and must not be reported as if it had.
    """
    import urllib.request
    try:
        with urllib.request.urlopen(live_url(rel), timeout=25) as r:
            served = r.read()
    except Exception:
        return None
    try:
        with open(local, "rb") as fh:
            mine = fh.read()
    except Exception:
        return None
    return served.replace(b"\r\n", b"\n") == mine.replace(b"\r\n", b"\n")


def main() -> int:
    import browser as B
    found = B.find_browser()
    if not found:
        print("  no browser found, so nothing was measured. "
              "Unchecked is not passing.")
        return 1
    exe, extra_args = found

    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mobile = "--mobile" in flags
    width, height = (390, 3400) if mobile else (1280, 2600)
    check_live = "--live" in flags
    show_all = "--all" in flags

    pages = args or sorted(
        glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))

    bad_text, bad_img, unread = [], [], []
    small_t, tiny_t, no_dim, no_alt, bad_head = [], [], [], [], []
    broken_img, no_label, side_scroll, no_land = [], [], [], []
    no_focus = []
    unknown = []
    stale, unverified, unreadable_css = [], [], []
    fonts_pending = []

    print("  viewport              : %dx%d %s"
          % (width, height,
             "(phone, coarse pointer rules applied)" if mobile
             else "(desktop)"))
    for page in pages:
        rel = os.path.relpath(page, ROOT).replace(os.sep, "/")
        if os.path.basename(page).startswith("_"):
            continue
        full = page if os.path.isabs(page) else os.path.join(ROOT, page)
        if check_live:
            same = live_matches(rel, full)
            if same is None:
                unverified.append(rel)
            elif not same:
                stale.append(rel)
        d = audit(full, exe, extra_args, width, height, coarse=mobile)
        if d is None:
            unread.append(rel)
            continue
        if d.get("sheetsUnreadable"):
            unreadable_css.append((rel, d["sheetsUnreadable"]))
        if d.get("fonts") != "loaded":
            fonts_pending.append((rel, d.get("fonts")))

        for t in d["text"]:
            floor = MIN_LARGE if t["large"] else MIN_TEXT
            if t["ratio"] is None:
                # A real image sits behind this text. Not resolvable from
                # computed style, recorded so the total never reads as full
                # coverage.
                unknown.append((rel, t["path"], t["why"], t["sample"]))
                continue
            if t["ratio"] < floor:
                bad_text.append((rel, t["ratio"], floor, t["tag"], t["cls"],
                                 t["sample"], t["fgc"], t["bgc"], t["path"]))
        for im in d["images"]:
            if not im["loaded"]:
                broken_img.append((rel, im["src"]))
                continue
            if im["nodim"]:
                no_dim.append((rel, im["src"], im["w"], im["h"]))
            if im["alt"] is None:
                no_alt.append((rel, im["src"]))
            if im["fit"] in ("cover", "contain"):
                continue    # deliberately reframed, not distorted
            if im["skew"] is not None and im["skew"] > SKEW_LIMIT:
                bad_img.append((rel, im["src"], im["skew"], im["intrinsic"],
                                im["rendered"]))
        if mobile:
            for t in d["targets"]:
                if min(t["w"], t["h"]) < MIN_TARGET and t.get("crowded"):
                    tiny_t.append((rel, t["tag"], t["cls"], t["w"], t["h"],
                                   t["label"], t["path"]))
                elif min(t["w"], t["h"]) < COMFY_TARGET:
                    small_t.append((rel, t["tag"], t["cls"], t["w"], t["h"],
                                    t["label"]))
            if d["scroll"]["doc"] > d["scroll"]["view"] + 2:
                side_scroll.append((rel, d["scroll"]["doc"],
                                    d["scroll"]["view"], d["overflow"]))
        lvl = 0
        for h in d["headings"]:
            if lvl and h["lvl"] > lvl + 1:
                bad_head.append((rel, lvl, h["lvl"], h["text"]))
            lvl = h["lvl"]
        for f in d["inputs"]:
            no_label.append((rel, f["tag"], f["type"], f["name"], f["ph"]))
        for f in d.get("noFocus", []):
            no_focus.append((rel, f["tag"], f["cls"], f["label"], f["path"]))
        L = d["land"]
        # Only <main> and a single <h1> are reported as problems. A standalone
        # printable (the Standards Pack, the print-and-play deck) legitimately
        # has no site header or footer to distinguish itself from, and flagging
        # those three documents on every run forever is how a check stops being
        # read. They are carried as context on rows that fail for a real
        # reason instead.
        missing = [k for k in ("main", "header", "footer") if not L[k]]
        if not L["main"] or L["h1"] != 1:
            no_land.append((rel, missing, L["h1"]))

    limit = None if show_all else 12

    def section(title, rows, fmt):
        print("  %-22s: %d" % (title, len(rows)))
        for row in rows[:limit]:
            print("     " + fmt(row))

    print("  pages measured        : %d" % (len(pages) - len(unread)))
    if unread:
        print("  pages NOT measured    : %d %s  (unchecked, not passing)"
              % (len(unread), unread[:3]))
    if fonts_pending:
        print("  fonts NOT loaded      : %d page(s) %s  (text sizes and target "
              "heights on these were measured against a fallback face, so they "
              "are not what a visitor sees)"
              % (len(fonts_pending), fonts_pending[:3]))
    if unreadable_css:
        print("  stylesheets unreadable: %d page(s) %s  (their coarse-pointer "
              "rules could not be applied, so those pages were NOT measured "
              "as a phone)" % (len(unreadable_css), unreadable_css[:3]))
    if check_live:
        print("  production mismatch   : %d %s" % (len(stale), stale[:4]))
        if unverified:
            print("  production UNVERIFIED : %d %s  (could not ask, not proof)"
                  % (len(unverified), unverified[:3]))
    print("  text on a gradient, not measurable this way: %d" % len(unknown))
    for rel, path, why, sample in unknown[:limit]:
        print("     %-26s %-38s %r" % (rel, path[:38], sample[:26]))
    section("text below contrast", bad_text,
            lambda r: "%-26s %.2f:1 (needs %.1f) <%s class=%r> %r  %s on %s"
                      % (r[0], r[1], r[2], r[3], r[4][:22], r[5][:34],
                         r[6], r[7]))
    section("images distorted", bad_img,
            lambda r: "%-26s %-34s %.1f%% off (intrinsic %.3f, rendered %.3f)"
                      % (r[0], r[1], r[2] * 100, r[3], r[4]))
    section("images not loading", broken_img,
            lambda r: "%-26s %s" % (r[0], r[1]))
    section("images without w/h", no_dim,
            lambda r: "%-26s %-34s rendered %dx%d" % (r[0], r[1], r[2], r[3]))
    section("images without alt", no_alt,
            lambda r: "%-26s %s" % (r[0], r[1]))
    section("heading level jumps", bad_head,
            lambda r: "%-26s h%d -> h%d  %r" % (r[0], r[1], r[2], r[3]))
    section("inputs without label", no_label,
            lambda r: "%-26s <%s type=%s name=%s> placeholder=%r"
                      % (r[0], r[1], r[2], r[3], r[4]))
    section("no visible focus", no_focus,
            lambda r: "%-26s <%s class=%r> %r" % (r[0], r[1], r[2][:20], r[3]))
    section("landmark/h1 problems", no_land,
            lambda r: "%-26s missing=%s h1=%d" % (r[0], r[1], r[2]))
    if mobile:
        section("targets under 24, crowded", tiny_t,
                lambda r: "%-26s <%s class=%r> %dx%d %r"
                          % (r[0], r[1], r[2][:18], r[3], r[4], r[5]))
        section("targets under 44px", small_t,
                lambda r: "%-26s <%s class=%r> %dx%d %r"
                          % (r[0], r[1], r[2][:18], r[3], r[4], r[5]))
        section("pages scrolling sideways", side_scroll,
                lambda r: "%-26s doc %dpx > view %dpx  %s"
                          % (r[0], r[1], r[2],
                             [o["path"][:44] for o in r[3][:2]]))
    return 1 if (bad_text or bad_img) else 0


if __name__ == "__main__":
    sys.exit(main())
