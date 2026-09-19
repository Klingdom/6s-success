"""Drive the Home Quest's Back button from the map screen, as a genuine
first-time visitor, and prove it actually goes back.

renderStart() is the handler wired to every "return to start" control that
exists (#m-back, #k-back, #f-again), not only the page's own initial load.
Its gate, applyFirstRunGate(), decides WHAT #view-start shows once it is the
visible section, never WHETHER it becomes the visible section: that was
show("start")'s job alone, called only after the gate's early return. A
visitor who has done 0 cards and held 0 zones is still "first run" by
isFirstRun()'s own definition (heldZones().length===0 && progress().done===0)
even after using "or pick a different room", the escape hatch that reveals
#go-map and #go-keep directly without changing either count. Such a visitor
could reach the map (or the Keep screen; same handler) and tap Back, hit the
gate's early return before show("start") ever ran, and see nothing happen:
#view-map stayed the visible section and #view-start stayed hidden.

Confirmed live before fixing, not assumed: driving the real flow in a headless
browser (#sym-other, then #go-other, then #go-map, then #m-back) and reading
the real `hidden` attributes on #view-start/#view-map directly showed both
unchanged by the Back click. Given the page's own measurement that the large
majority of visitors leave without finishing a single card, this is the
common case, not an edge case.

Run:  python ops/tests/test_quest_back_button_first_run.py
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
function hid(d, id){ var e = d.getElementById(id); return e ? !!e.hidden : "MISSING"; }

var frame = document.getElementById("f");
var phase = 0;
frame.addEventListener("load", function(){
  var d;
  try { d = frame.contentDocument; } catch (e) { out.error = "blocked"; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }
  if (phase === 0) {
    phase = 1;
    try { d.defaultView.localStorage.clear(); } catch (e) {}
    frame.contentWindow.location.reload();
    return;
  }
  if (phase !== 1) return;
  phase = 2;

  // A genuine first-time visitor: never touched a card, never held a zone.
  // Reach the map through the real escape hatch ("show me the house
  // instead", then "pick a different room"), the same path a stranger who
  // wants to browse before committing would take.
  setTimeout(function(){
    var symOther = d.getElementById("sym-other");
    if (!symOther) { out.error = "no #sym-other"; return done(); }
    symOther.click();

    setTimeout(function(){
      var goOther = d.getElementById("go-other");
      if (!goOther) { out.error = "no #go-other"; return done(); }
      goOther.click();

      setTimeout(function(){
        var goMap = d.getElementById("go-map");
        if (!goMap) { out.error = "no #go-map"; return done(); }
        goMap.click();

        setTimeout(function(){
          out.onMap = { viewStart: hid(d, "view-start"), viewMap: hid(d, "view-map") };

          var mBack = d.getElementById("m-back");
          if (!mBack) { out.error = "no #m-back"; return done(); }
          mBack.click();

          setTimeout(function(){
            out.afterBack = { viewStart: hid(d, "view-start"), viewMap: hid(d, "view-map") };
            done();
          }, 400);
        }, 400);
      }, 400);
    }, 400);
  }, 900);
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-back-profile-")
    wrap = os.path.join(SITE, "_quest_back_button_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=520,1440", "--virtual-time-budget=15000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"Q(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the Back button was NOT exercised. "
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

    on_map = o.get("onMap") or {}
    after = o.get("afterBack") or {}
    bad = []
    if on_map.get("viewStart") is not True or on_map.get("viewMap") is not False:
        bad.append("tapping 'See every room' did not land on the map view: %s" % on_map)
    if after.get("viewMap") is not True:
        bad.append("#view-map is still the visible section after tapping Back "
                    "as a first-time visitor: %s" % after)
    if after.get("viewStart") is not False:
        bad.append("#view-start did not become visible again after tapping "
                    "Back as a first-time visitor: %s" % after)
    for b in bad:
        print("  FAIL " + b)
    if bad:
        return 1

    print("  ok  Back from the map returns a first-time visitor (0 cards "
          "done, 0 zones held) to the real start screen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
