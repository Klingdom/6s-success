"""Drive the Home Quest's own installed-app shortcut once the whole deck is
already done, and prove it lands somewhere real.

site/manifest.webmanifest wires the PWA shortcut "Draw a card" to exactly
quest.html?go=draw, so this is the one deep link a returning, engaged
visitor is likely to open over and over from their home screen, unlike
?zone= or ?room=, each usually followed once from an article. Those two
already handle the case where begin() finds nothing left to draw (every
card in scope already done): they check `if (run) { return; }` after
calling begin() and fall through to releaseHero()/renderStart() when it is
still null, so the page never renders in the raw pre-render markup state.
?go=draw had no such guard: `if (go === "draw") { begin("draw"); return; }`
returned unconditionally, so a visitor who has finished every one of the
684 cards in the house and taps their own home-screen shortcut got the
page's raw, un-rendered markup: the hero still suppressed, #first-run
(visible by default, for the no-JS case) telling them to "start at the
door", and #mode-list/#start-head (hidden by default, only unhidden by
applyFirstRunGate()) never shown at all.

Run:  python ops/tests/test_quest_draw_shortcut_full_completion.py
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

var frame = document.getElementById("f");
var phase = 0;

frame.addEventListener("load", function(){
  var d;
  try { d = frame.contentDocument; }
  catch (e) { out.error = "blocked: " + e.message; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }

  if (phase === 0) {
    phase = 1;
    // A fresh profile, but wait for window.QUEST (quest-data.js, a
    // synchronous script ahead of quest.js) before reading it, the same
    // margin test_quest_flow.py gives it.
    setTimeout(function(){
      var w = d.defaultView;
      if (!w.QUEST || !w.QUEST.rooms) { out.error = "window.QUEST never loaded"; return done(); }
      // Mark every real card done, the same id shape quest.js's own
      // cardId() builds (room + "|" + zone.zone + "|" + step.s), so this
      // is the real deck, not a stand-in for it.
      var doneMap = {};
      var now = Date.now();
      w.QUEST.rooms.forEach(function (r) {
        r.zones.forEach(function (z) {
          z.steps.forEach(function (st) {
            doneMap[r.room + "|" + z.zone + "|" + st.s] = now;
          });
        });
      });
      out.cardCount = Object.keys(doneMap).length;
      try {
        w.localStorage.setItem("6s.quest.v1", JSON.stringify({
          done: doneMap, lastSeen: now - 1000
        }));
      } catch (e) { out.error = "could not seed localStorage: " + e.message; return done(); }
      phase = 2;
      // Exactly the deep link the manifest shortcut opens.
      frame.src = "quest.html?go=draw";
    }, 900);
    return;
  }
  if (phase !== 2) return;
  phase = 3;

  setTimeout(function(){
    var d2 = frame.contentDocument;
    out.firstRunShown  = vis(d2, "first-run");
    out.symptomShown   = vis(d2, "symptom-step");
    out.causeShown     = vis(d2, "cause-step");
    out.startHeadShown = vis(d2, "start-head");
    out.modeListShown  = vis(d2, "mode-list");
    out.cardShown      = vis(d2, "view-card");
    out.pDone = (d2.getElementById("p-done") || {}).textContent || "";
    out.pTotal = (d2.getElementById("p-total") || {}).textContent || "";
    done();
  }, 900);
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-draw-profile-")
    wrap = os.path.join(SITE, "_quest_draw_shortcut_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
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
        print("  the probe did not run, so the shortcut was NOT exercised. "
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
    if not o.get("cardCount"):
        bad.append("no cards were seeded as done, so this never reached a real "
                    "full-completion state")
    if o.get("firstRunShown"):
        bad.append("a visitor who has finished every card in the house is shown "
                    "the first-run pitch ('start at the door') on the shortcut "
                    "built for exactly this return visit")
    if o.get("symptomShown") or o.get("causeShown"):
        bad.append("the symptom or cause screen is shown to a visitor who has "
                    "already finished every card")
    if o.get("cardShown"):
        bad.append("a card is shown even though nothing is left to draw")
    if not o.get("startHeadShown"):
        bad.append("the returning-visitor progress header never appears "
                    "(#start-head stays hidden, its markup default)")
    if not o.get("modeListShown"):
        bad.append("the mode picker never appears (#mode-list stays hidden, "
                    "its markup default), leaving no way to do anything")
    for b in bad:
        print("  FAIL " + b)
    if bad:
        print("  observed: %s" % json.dumps(o)[:600])
        return 1

    print("  ok  the go=draw shortcut falls through to the real start screen "
          "once all %s cards are done, instead of the page's raw pre-render "
          "markup" % o.get("cardCount"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
