"""Drive the Home Quest in a real browser and check the loop actually works.

The Quest is the only complete journey a visitor can finish today: it is free,
runs entirely in the browser, needs no account and no payment, and it is
therefore the whole of what the site currently delivers while the payment links
are dead. It has never been functionally tested. Every check in this repository
so far has asked whether pages render, resolve, or say true things; none has
asked whether the product works.

What this asks, in order, as a first time visitor would:

    the first run screen is the one that shows;
    pressing "Start at the door" opens a card with real content on it;
    the card names a zone, a pass, and something to do;
    marking it done advances to the next card;
    progress survives a reload, which is the entire promise of a quest you
      pick up over several days.

Driven through an iframe so the page runs at a real phone width, and because
ops/shoot_mobile.py already proved that is the honest way to do it here.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import browser as B                                           # noqa: E402

WRAPPER = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:390px;height:1400px;border:0}</style>
</head><body><iframe id="f" src="quest.html"></iframe><script>
var out = {};
function done(){ document.title = "Q>>" + JSON.stringify(out) + "<<E"; }
function vis(d, id){ var e = d.getElementById(id); return !!e && !e.hidden
    && getComputedStyle(e).display !== "none"; }
function txt(d, id){ var e = d.getElementById(id); return e ? (e.textContent||"").trim() : ""; }

// The page reads its saved progress and renders before any script here can
// touch it, so clearing storage after the first load was too late: the frame
// was already showing the returning visitor view and clearing it changed
// nothing on screen. The first version of this test passed only because the
// browser profile happened to be empty, and failed the moment a previous run
// had left progress behind. A test whose result depends on something it did
// not set up is not a test.
//
// So: clear on the first load, reload, and only then look. The second load is
// a genuine first time visitor.
var frame = document.getElementById("f");
var phase = 0;

frame.addEventListener("load", function(){
  var d;
  try { d = frame.contentDocument; }
  catch (e) { out.error = "blocked: " + e.message; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }

  if (phase === 0) {
    phase = 1;
    try { d.defaultView.localStorage.clear(); } catch (e) {}
    frame.contentWindow.location.reload();
    return;
  }
  if (phase !== 1) return;
  phase = 2;

  setTimeout(function(){
    var w = d.defaultView;

    out.firstRun = vis(d, "first-run");
    out.startHeadHidden = !vis(d, "start-head");

    var go = d.getElementById("go-first");
    out.hasStart = !!go;
    out.startLabel = go ? (go.textContent||"").trim() : "";
    if (!go) return done();
    go.click();

    setTimeout(function(){
      out.cardShown = vis(d, "view-card");
      out.zone      = txt(d, "c-where");
      out.pass      = txt(d, "c-badge");
      out.purpose   = txt(d, "c-purpose");
      out.todo      = txt(d, "c-do");
      out.count     = txt(d, "c-count");

      var doneBtn = d.getElementById("c-done");
      out.hasDone = !!doneBtn;
      if (!doneBtn) return done();
      doneBtn.click();

      setTimeout(function(){
        out.pass2    = txt(d, "c-badge");
        out.purpose2 = txt(d, "c-purpose");
        try { out.saved = w.localStorage.getItem("6s.quest.v1") || ""; }
        catch (e) { out.saved = ""; }

        // The other half of the promise: put it down, come back another day.
        // Reload the same frame with the saved progress still in place and
        // check the returning visitor is met with their progress rather than
        // the first run pitch all over again.
        frame.addEventListener("load", function once(){
          frame.removeEventListener("load", once);
          setTimeout(function(){
            var d2 = frame.contentDocument;
            out.returnFirstRunHidden = !vis(d2, "first-run");
            out.returnHeadShown = vis(d2, "start-head");
            out.returnDone  = txt(d2, "p-done");
            out.returnTotal = txt(d2, "p-total");
            done();
          }, 900);
        });
        frame.contentWindow.location.reload();
      }, 500);
    }, 700);
  }, 900);
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-profile-")
    wrap = os.path.join(SITE, "_quest_flow_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,     # never inherit another run's storage
             "--window-size=520,1440", "--virtual-time-budget=20000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"Q(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the Quest was NOT exercised. "
              "This is unchecked, not working.")
        return 1
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        o = json.loads(raw)
    except ValueError:
        print("  probe output unreadable: %s" % raw[:200])
        return 1

    if o.get("error"):
        print("  probe error: %s" % o["error"])
        return 1

    bad = []
    if not o.get("firstRun"):
        bad.append("a first time visitor is not shown the first run screen")
    if not o.get("startHeadHidden"):
        bad.append("the returning visitor header shows on a first visit too")
    if not o.get("hasStart"):
        bad.append("there is no start button")
    if not o.get("cardShown"):
        bad.append("pressing start did not open a card")
    for field, label in (("zone", "which zone this is"),
                         ("pass", "which of the six passes"),
                         ("purpose", "what the card is for"),
                         ("todo", "what to actually do")):
        if not o.get(field):
            bad.append("the card does not say %s (%s is empty)" % (label, field))
    if not o.get("hasDone"):
        bad.append("the card has no way to mark it done")
    if o.get("purpose2") and o.get("purpose2") == o.get("purpose"):
        bad.append("marking a card done did not advance to a different card")
    if not o.get("returnFirstRunHidden"):
        bad.append("a returning visitor with saved progress is shown the first "
                   "run pitch again instead of their progress")
    if not o.get("returnHeadShown"):
        bad.append("a returning visitor is not shown the progress header")
    if not (o.get("returnDone") or "").strip():
        bad.append("the progress header does not say how many cards are done")

    saved = o.get("saved") or ""
    if not saved or saved == "{}":
        bad.append("nothing was written to localStorage, so progress would not "
                   "survive a reload")

    for b in bad:
        print("  FAIL " + b)
    if bad:
        print("  observed: %s" % json.dumps(
            {k: (v[:60] if isinstance(v, str) else v) for k, v in o.items()})[:600])
        return 1

    print("  ok  first run opens a card in %s (%s pass), done advances, "
          "and a reload meets the returning visitor at %s of %s"
          % (o["zone"][:34] or "a zone", o["pass"][:10],
             o.get("returnDone") or "?", o.get("returnTotal") or "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
