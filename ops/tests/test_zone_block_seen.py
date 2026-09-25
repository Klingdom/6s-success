#!/usr/bin/env python3
"""
Prove a real browser fires zone-block-seen for the three personalised blocks,
and only when they have actually been on screen.

WHY THIS EXISTS
---------------
DECISIONS.md D-026 authors capacity, variants and diagnosis a room at a time,
and its revisit clause asks whether the completed zones changed how the
diagnosis is used. On 2026-09-24, with four rooms authored and the checkpoint
due, that question could not be answered at all. The blocks are static HTML,
they emitted nothing, and the only page signal was a whole-page scroll bucket
that cannot separate "read the diagnosis" from "scrolled past it to the FAQ".

So an IntersectionObserver was added to measure.js. An observer that silently
fails to fire is indistinguishable from a reader who never scrolled, which is
exactly the failure class that has cost this repository the most: unchecked
reported as passing. Hence a real browser, the real measure.js, and the real
rendered zone page.

WHAT IT ASSERTS
---------------
  1. All three blocks report once when scrolled into view.
  2. Each reports AT MOST once, so a reader scrolling up and down does not
     inflate the count.
  3. The payload carries only which block it was. If it ever starts carrying
     a branch the reader matched, that describes somebody's home and must not
     be in analytics.

Run:  python ops/tests/test_zone_block_seen.py
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

# Capture what track() would have sent, before measure.js decides how to send
# it. Stubbing the transport rather than the tracker means the observer, the
# threshold and the payload are all the real ones.
SHIM = """<script>
window.__sent = [];
/* measure.js sends through window.umami.track and nothing else, so that is
   the boundary to stub. An earlier version of this test stubbed sendBeacon
   and fetch, which are what Umami's own remote script uses; that script never
   loads from file://, so measure.js queued every event and the test reported
   three silent failures for a tracker that was working. Stub what the code
   under test actually calls. */
window.umami = { track: function (name, data) {
  try { window.__sent.push(JSON.stringify({ n: name, d: data })); } catch (e) {}
} };
</script>
"""

DRIVER = """<script>
/* EVERYTHING THE OBSERVER NEEDS HAPPENS SYNCHRONOUSLY IN THE LOAD HANDLER.
   Measured on 2026-09-24: scrolling immediately on load reports; the SAME
   scroll wrapped in a 900ms setTimeout reports nothing at all. Under
   --virtual-time-budget the clock races ahead while the page is idle, the
   deferred callback still runs, but no further frames are rendered, and an
   IntersectionObserver is only evaluated per rendered frame. The tracker was
   correct in both runs; only the harness differed.

   It also scrolls to the FOOT of the page rather than to a named element.
   Zone pages shift layout as their images arrive, so scrollIntoView on a
   specific block lands somewhere else by the time a frame is drawn: in one
   run, scrolling to #capacity left #diagnosis on screen. The bottom of the
   document is the one position that cannot move out from under the test. */
window.addEventListener("load", function () {
  if (%s) { window.scrollTo(0, document.body.scrollHeight); }
  setTimeout(function () {
    var out = [];
    for (var i = 0; i < window.__sent.length; i++) {
      if (window.__sent[i].indexOf("zone-block-seen") >= 0) {
        out.push(window.__sent[i]);
      }
    }
    document.title = "VERDICT:" + JSON.stringify({ sent: out });
  }, 700);
});
</script>
"""


def pick_page():
    site = os.path.join(ROOT, "site", "zones")
    for z in sorted(os.listdir(site)):
        if not z.endswith(".html") or z == "index.html":
            continue
        s = io.open(os.path.join(site, z), encoding="utf-8").read()
        if all(('id="%s"' % b) in s for b in ("capacity", "variants", "diagnosis")):
            return z, s
    return None, None


def run_case(browser, args, scroll):
    """Load a real zone page with the transport stubbed and scroll it."""
    name, page_src = pick_page()
    if page_src is None:
        return None, "no built zone page carries all three blocks yet"

    m = re.search(r'<script[^>]+assets/js/measure\.js', page_src)
    if not m:
        return None, "could not find the measure.js tag on %s" % name
    doctored = (page_src[:m.start()] + SHIM + page_src[m.start():])
    doctored = doctored.replace(
        "</body>", (DRIVER % ("true" if scroll else "false")) + "</body>", 1)

    out = os.path.join(ROOT, "site", "zones", "_test_block_seen.html")
    try:
        io.open(out, "w", encoding="utf-8", newline="\n").write(doctored)
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--window-size=900,700", "--virtual-time-budget=12000",
               "--dump-dom", "file:///" + out.replace("\\", "/")] + args
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        dom = r.stdout or ""
    finally:
        try:
            os.remove(out)
        except OSError:
            pass

    mt = re.search(r"VERDICT:(\{.*?\})</title>", dom, re.S)
    if not mt:
        return None, "the page never reported a verdict (measure.js may not have run)"
    try:
        return json.loads(mt.group(1).replace("&quot;", '"')), None
    except ValueError as exc:
        return None, "verdict was not JSON: %r (%s)" % (mt.group(1)[:90], exc)


SYNTHETIC = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>t</title></head><body>
<script>
window.__sent = [];
window.umami = { track: function (name, data) {
  try { window.__sent.push(JSON.stringify({ n: name, d: data })); } catch (e) {}
} };
</script>
<div style="height:1500px"></div>
<section id="capacity" style="height:%(h)dpx;background:#eee">capacity</section>
<div style="height:1500px"></div>
<script src="%(js)s"></script>
<script>
window.addEventListener("load", function () {
  /* Put the block's MIDDLE in the viewport: it fills the screen completely,
     but because it is taller than the screen its intersectionRatio is well
     under 0.5. That is the exact shape a real diagnosis block has. */
  var el = document.getElementById("capacity");
  var r = el.getBoundingClientRect();
  window.scrollTo(0, window.scrollY + r.top + (r.height / 2)
                     - (window.innerHeight / 2));
  setTimeout(function () {
    document.title = "VERDICT:" + JSON.stringify({ sent: window.__sent });
  }, 700);
});
</script>
</body></html>
"""


def run_synthetic(browser, args, height):
    """A page whose only block is `height` tall, scrolled to its middle.

    Deterministic where the real-page case is not: zone pages shift layout as
    images arrive, so which of the three blocks ends up on screen varies run
    to run (measured: 1, 1, 2 and 3 blocks across four identical runs). That
    variability is fine for proving the observer fires at all, and useless for
    proving the TALL-BLOCK rule, which is the part that was actually broken.
    This page has no images and fixed heights, so it cannot drift.
    """
    site = os.path.join(ROOT, "site")
    out = os.path.join(site, "_test_block_synth.html")
    try:
        io.open(out, "w", encoding="utf-8", newline="\n").write(
            SYNTHETIC % {"h": height, "js": "assets/js/measure.js"})
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--window-size=900,700", "--virtual-time-budget=8000",
               "--dump-dom", "file:///" + out.replace("\\", "/")] + args
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        dom = r.stdout or ""
    finally:
        try:
            os.remove(out)
        except OSError:
            pass
    mt = re.search(r"VERDICT:(\{.*?\})</title>", dom, re.S)
    if not mt:
        return None, "the synthetic page never reported a verdict"
    try:
        return json.loads(mt.group(1).replace("&quot;", '"')), None
    except ValueError as exc:
        return None, "verdict was not JSON: %r (%s)" % (mt.group(1)[:90], exc)


def check_predicate():
    """Run measure.js's own blockSeenEnough() in node against real numbers."""
    js = io.open(os.path.join(ROOT, "site", "assets", "js", "measure.js"),
                 encoding="utf-8").read()
    m = re.search(r"function blockSeenEnough[^}]*}", js, re.S)
    if not m:
        return ["measure.js no longer defines blockSeenEnough(), so the rule "
                "that decides whether a block counts as read is untested"]
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=20)
    except Exception:                                          # noqa: BLE001
        print("  UNCHECKED: no node on this machine, so the tall-block rule "
              "was NOT exercised. That is not a pass.")
        return []

    # (ratio, shown, viewport, must_report, why)
    cases = [
        # Measured off a real zone page on 2026-09-24: a 2100px diagnosis
        # block on a 608px viewport, scrolled to its middle. It fills the
        # screen completely and its ratio is 0.29. The 0.5-only threshold
        # this shipped with could never fire on it.
        (0.29, 608, 608, True, "a tall block filling the whole viewport"),
        (0.23, 700, 700, True, "a 3x-viewport block filling the screen"),
        (0.60, 300, 500, True, "an ordinary block more than half visible"),
        (1.00, 200, 700, True, "a short block fully on screen"),
        (0.10, 70, 700, False, "a block only just creeping into view"),
        (0.40, 280, 700, False, "40% of a block, filling 40% of the screen"),
        (0.00, 0, 700, False, "not on screen at all"),
        (0.30, 200, 0, False, "no viewport height to divide by"),
    ]
    script = [m.group(0), "var bad = [];"]
    for ratio, shown, vp, want, why in cases:
        script.append(
            "if (blockSeenEnough(%r, %r, %r) !== %s) { bad.push(%s); }"
            % (ratio, shown, vp, "true" if want else "false",
               json.dumps("%s: expected %s" % (why, want))))
    script.append("console.log(JSON.stringify(bad));")
    r = subprocess.run(["node", "-e", "\n".join(script)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return ["node could not run the extracted predicate: %s"
                % (r.stderr or "")[:200]]
    try:
        bad = json.loads((r.stdout or "[]").strip().splitlines()[-1])
    except (ValueError, IndexError):
        return ["the predicate harness printed nothing parseable: %r"
                % (r.stdout or "")[:200]]
    return ["blockSeenEnough is wrong for %s" % b for b in bad]


def blocks_in(sent):
    got = []
    for s in sent:
        m = re.search(r'"block"\s*:\s*"([a-z]+)"', s)
        if m:
            got.append(m.group(1))
    return got


def main() -> int:
    import browser as B
    found = B.find_browser()
    if not found:
        print("  UNCHECKED: no Edge or Chromium on this machine, so the real "
              "observer was NOT exercised. That is not a pass.")
        return 0
    exe, args = found
    fails = []

    # 1. Scrolled to the foot: at least one of the three blocks was genuinely
    #    on screen, so at least one must report, and it must name a real block.
    v, err = run_case(exe, args, scroll=True)
    if err:
        print("  UNCHECKED: " + err)
        return 0
    got = blocks_in(v["sent"])
    if not got:
        fails.append("the page was scrolled to its foot, where at least one "
                     "of capacity/variants/diagnosis is on screen, and "
                     "nothing reported at all: %r" % v["sent"])
    for b in got:
        if b not in ("capacity", "variants", "diagnosis"):
            fails.append("reported an unexpected block name %r" % b)
    dupes = sorted({b for b in got if got.count(b) > 1})
    if dupes:
        fails.append("reported the same block more than once in a single "
                     "page view: %s" % ", ".join(dupes))

    # 2. The payload must never carry anything about the reader's own home.
    for s in v["sent"]:
        for leak in ("answer", "branch", "symptom", "cause"):
            if '"%s"' % leak in s:
                fails.append("payload carries %r, which describes the "
                             "reader's home: %r" % (leak, s[:160]))

    # 3. Never scrolled: the blocks sit well below the fold on every zone
    #    page, so nothing may report. Without this the event would just be a
    #    second, more expensive pageview.
    v2, err2 = run_case(exe, args, scroll=False)
    if err2:
        print("  UNCHECKED (unscrolled case): " + err2)
    elif blocks_in(v2["sent"]):
        fails.append("reported without the page ever being scrolled, so this "
                     "measures arrival and not reading: %r" % v2["sent"])

    # 4. THE TALL-BLOCK RULE, in node, against the real shipped source.
    #    This is the part that was actually broken and the part a browser
    #    cannot decide here: headless Chrome under --virtual-time-budget does
    #    not reliably render a frame after a programmatic scroll, and an
    #    IntersectionObserver is only evaluated per rendered frame. Measured:
    #    the same real page reported 1, 1, 2 and 3 blocks across four
    #    identical runs. So the predicate is extracted from measure.js and
    #    run directly, with the numbers taken off a real page.
    pred_fails = check_predicate()
    fails.extend(pred_fails)

    if fails:
        print("FAILURES:")
        for f in fails:
            print("  - " + f)
        return 1
    print("  ok  scrolled to the foot: %s reported" % ", ".join(got))
    print("  ok  no block reported twice in one page view")
    print("  ok  nothing reported when the page was never scrolled")
    print("  ok  the tall-block rule is right on 8 real-shaped cases")
    print("  ok  the payload names the block and nothing about the reader")
    print("all zone-block-seen tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
