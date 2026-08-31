"""Render and measure pages at a true phone width.

Edge refuses to open a window narrower than about 492 CSS pixels, so
--window-size=390 does not give a 390 pixel viewport: it lays the page out at
492 and the screenshot canvas then crops the right hand 102 pixels away. That
looks exactly like a horizontal overflow bug and is not one. It cost this
project a wrong diagnosis on 2026-08-30.

An iframe has no such minimum, and media queries inside one resolve against the
iframe's own width, so a 390 pixel iframe is a genuine 390 pixel viewport. We
host the page in one, screenshot the wrapper, and crop to the frame.

Usage:  python ops/shoot_mobile.py [--width 390] [page ...]
"""
import argparse
import io
import os
import re
import subprocess
import sys

import browser as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "shots")

DEFAULT_PAGES = [
    "site/index.html",
    "site/quest.html",
    "site/book.html",
    "site/cart.html",
    "site/rooms/kitchen.html",
    "site/zones/kitchen-the-cooking-zone.html",
]


def edge():
    found = B.find_browser()
    if not found:
        sys.exit("no browser found (Edge or the sandbox's pre-installed Chromium)")
    return found


WRAPPER = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;padding:0;background:#fff}}
iframe{{width:{w}px;height:{h}px;border:0;display:block}}</style></head><body>
<iframe id="f" src="{src}"></iframe>
<script>
// Give the framed page a moment to run its own DOMContentLoaded work, then ask
// it what does not fit. scrollWidth catches text painting wider than its box,
// which a bounding rect alone never reveals.
function scan(){{
  var d, out = [];
  try {{ d = document.getElementById('f').contentDocument; }}
  catch (e) {{ document.title = 'OV>>BLOCKED ' + e.message + '<<END'; return; }}
  if (!d || !d.body) {{ document.title = 'OV>>NO DOCUMENT<<END'; return; }}
  var W = d.documentElement.clientWidth;
  out.push('viewport=' + W);
  d.querySelectorAll('body *').forEach(function(el){{
    var r = el.getBoundingClientRect();
    if (r.width === 0) return;
    // A skip link and other visually-hidden helpers are parked far off to the
    // left on purpose. Anything wholly off the left edge is deliberate, not a
    // layout fault, and reporting it buries the real findings.
    if (r.right < 0) return;
    // Content inside a scroll container is contained by design: a wide table
    // in an overflow-x:auto wrapper scrolls within itself and never moves the
    // page. Walking up and skipping those is the difference between "the
    // document scrolls sideways" and "something further in is wide".
    for (var a = el.parentElement; a && a !== d.body; a = a.parentElement) {{
      var ox = getComputedStyle(a).overflowX;
      if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') return;
    }}
    var over = (r.right > W + 1) || (r.left < -1)
      || (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0
          && getComputedStyle(el).overflowX === 'visible');
    if (!over) return;
    out.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '')
      + (el.className && el.className.baseVal === undefined
         ? '.' + String(el.className).trim().split(/[ ]+/).join('.') : '')
      + ' | rect ' + Math.round(r.left) + '-' + Math.round(r.right)
      + ' | client' + el.clientWidth + ' scroll' + el.scrollWidth);
  }});
  document.title = 'OV>>' + out.join(' ;; ') + '<<END';
}}
document.getElementById('f').addEventListener('load', function(){{
  setTimeout(scan, 600);
}});
</script></body></html>"""


def run(width: int, height: int, pages: list) -> int:
    os.makedirs(OUT, exist_ok=True)
    exe, extra = edge()
    bad = 0
    for rel in pages:
        src = os.path.join(ROOT, rel.replace("/", os.sep))
        # Keyed by path, not basename. site/zones/index.html,
        # site/articles/index.html and site/index.html are three different
        # pages that all used to write to shots/index-390.png, so a sweep
        # covering them kept only the last one's screenshot and silently
        # destroyed the evidence for the other two.
        name = (os.path.splitext(rel)[0]
                .replace("\\", "/").removeprefix("site/").replace("/", "-"))
        if not os.path.exists(src):
            print("  %-28s MISSING" % name)
            bad += 1
            continue
        # The wrapper must sit beside the page so the relative src, and every
        # stylesheet and image the page pulls, resolve as they do in production.
        wrap = os.path.join(os.path.dirname(src), "_shoot_wrapper.html")
        io.open(wrap, "w", encoding="utf-8", newline="").write(
            WRAPPER.format(w=width, h=height, src=os.path.basename(src)))
        png = os.path.join(OUT, "%s-%d.png" % (name, width))
        try:
            common = ([exe] + extra +
                      ["--headless=new", "--disable-gpu", "--hide-scrollbars",
                       "--force-device-scale-factor=1",
                       "--allow-file-access-from-files",
                       "--window-size=%d,%d" % (width + 120, height + 40),
                       "file:///" + wrap.replace("\\", "/")])
            subprocess.run(common[:-1] + ["--screenshot=" + png, common[-1]],
                           capture_output=True, timeout=120)
            r = subprocess.run(common[:-1] + ["--virtual-time-budget=8000",
                                              "--dump-dom", common[-1]],
                               capture_output=True, timeout=120)
        finally:
            if os.path.exists(wrap):
                os.remove(wrap)

        dom = r.stdout.decode("utf-8", "replace")
        m = re.search(r"OV(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)END", dom, re.S)
        parts = (m.group(1).split(" ;; ") if m else ["PROBE DID NOT RUN"])
        head = parts[0]
        if not head.startswith("viewport="):
            print("  %-28s CANNOT MEASURE: %s" % (name, head[:60]))
            bad += 1
            continue
        vp = int(head.split("=")[1])
        if vp != width:
            # Refuse to report on a width we did not actually render.
            print("  %-28s WRONG VIEWPORT %d, wanted %d" % (name, vp, width))
            bad += 1
            continue
        if len(parts) == 1:
            print("  %-28s clean at %dpx" % (name, vp))
        else:
            bad += 1
            print("  %-28s %d OVERFLOWING at %dpx" % (name, len(parts) - 1, vp))
            for line in parts[1:8]:
                print("       " + line[:120])
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=1400)
    ap.add_argument("pages", nargs="*")
    a = ap.parse_args()
    n = run(a.width, a.height, a.pages or DEFAULT_PAGES)
    print("\n  %d page(s) with findings" % n)
    sys.exit(0)
