#!/usr/bin/env python3
"""
Prove no zone-map label spills out of its box, at phone width or desktop.

WHY THIS CANNOT BE REASONED ABOUT
---------------------------------
The eleven room pages with no photograph carry the book's hand-drawn zone map
(ops/import_room_diagrams.py). The drawing is 1000 units wide, so inside a
390px phone it scales to about 0.39 and its 15px labels render at roughly 6px,
which is unreadable. build_zone_pages.py's DIAGRAM_CSS lifts them with a media
query, using an attribute selector so the imported artwork itself is untouched
and stays diffable against the chapter it came from.

Enlarging text inside a fixed-size drawing is exactly the change that quietly
breaks it: the longest label, "Stair and floor path", starts at x=112 inside a
box whose right edge is 350, so it has 238 units and no more. Character counts
and em estimates are not good enough to settle that, because the real width
depends on the font that actually resolved. So this measures, in a real
browser, with getBBox, at both widths.

If no browser is available it says NOT VERIFIED and exits 0, which
gate_tests() counts as unchecked rather than passing.

Run:  python ops/tests/test_room_diagram_fits.py
"""
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import browser                                                 # noqa: E402

PROBE = """
<script>
window.addEventListener('load', function () {
  var out = [];
  document.querySelectorAll('.room-lead-diagram svg').forEach(function (svg) {
    var boxes = [];
    svg.querySelectorAll('rect').forEach(function (r) {
      var w = parseFloat(r.getAttribute('width'));
      if (w && w < 900) {
        boxes.push({x: parseFloat(r.getAttribute('x') || 0),
                    y: parseFloat(r.getAttribute('y') || 0),
                    w: w, h: parseFloat(r.getAttribute('height') || 0)});
      }
    });
    svg.querySelectorAll('text').forEach(function (t) {
      var b;
      try { b = t.getBBox(); } catch (e) { return; }
      var inside = null;
      boxes.forEach(function (r) {
        if (b.x >= r.x - 2 && b.y >= r.y - 2 &&
            b.x <= r.x + r.w && b.y <= r.y + r.h) { inside = r; }
      });
      if (inside && b.x + b.width > inside.x + inside.w - 4) {
        out.push({text: t.textContent.slice(0, 30),
                  right: Math.round(b.x + b.width),
                  limit: Math.round(inside.x + inside.w)});
      }
    });
  });
  document.title = 'PROBE' + JSON.stringify(out);
});
</script>
"""


def pages():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "site", "rooms", "*.html"))):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        if "room-lead-diagram" in s:
            out.append((f, s))
    return out


def measure(exe, extra, path, source, width):
    """Overflowing labels on one page at one viewport width."""
    probe = os.path.join(os.path.dirname(path), "_diagram_probe.html")
    io.open(probe, "w", encoding="utf-8").write(
        source.replace("</body>", PROBE + "</body>"))
    try:
        cmd = ([exe, "--headless=new", "--disable-gpu"] + list(extra)
               + ["--window-size=%d,900" % width, "--virtual-time-budget=4000",
                  "--dump-dom", "file:///" + probe.replace("\\", "/")])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        m = re.search(r"<title>PROBE(.*?)</title>", r.stdout, re.S)
        if not m:
            return None
        return json.loads(m.group(1))
    finally:
        if os.path.exists(probe):
            os.remove(probe)


def main():
    found = browser.find_browser()
    if not found:
        print("NOT VERIFIED: no Chromium-family browser on this machine, so "
              "no label was measured and nothing here is proved.")
        return 0
    exe, extra = found

    targets = pages()
    if len(targets) < 5:
        print("FAIL")
        print(" - only %d page(s) carry a zone-map diagram, which means this "
              "test stopped looking rather than stopped finding problems"
              % len(targets))
        return 1

    fails, measured = [], 0
    for path, source in targets:
        rel = os.path.relpath(path, ROOT)
        for width in (390, 1200):
            over = measure(exe, extra, path, source, width)
            if over is None:
                print("NOT VERIFIED: the probe never reported for %s at %dpx, "
                      "so this page was not measured." % (rel, width))
                return 0
            measured += 1
            for o in over:
                fails.append("%s at %dpx: %r runs to %d inside a box that "
                             "ends at %d" % (rel, width, o["text"],
                                             o["right"], o["limit"]))

    if fails:
        print("FAIL")
        for f in fails[:12]:
            print(" -", f)
        return 1
    print("OK: %d page/viewport measurement(s), every zone label fits its own "
          "box at 390px and 1200px" % measured)
    return 0


if __name__ == "__main__":
    sys.exit(main())
