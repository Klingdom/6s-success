"""The Keep screen's object-URL leak, fail-then-pass against the real file.

Every photograph shown on the Keep screen (site/assets/js/quest.js) is read
from IndexedDB and turned into a `blob:` object URL via
`window.QuestPhotos.objectUrl()`. Those URLs are not garbage collected: the
spec keeps a blob alive for as long as anything holds its URL, so the file's
own `releaseUrls()` exists specifically to revoke the previous batch before a
repaint draws a new one, and its own comment says so ("Object URLs are
revoked on the next repaint... a page that takes a hundred of them and never
lets go holds a hundred blobs in memory for the life of the tab").

Two of `renderKeep()`'s five real call sites never called `releaseUrls()`
before this fix: the `#go-keep` nav button (the normal, everyday way anyone
opens this screen) and the restore-backup flow. Every other visit to Keep
leaked one blob URL per photograph shown, for the life of the tab, on the
one feature (the before/after record) whose entire value proposition depends
on it staying usable over a long-running session.

This drives the real quest.js/quest.html/photos.js in a headless browser.
IndexedDB itself does not complete under this sandbox's headless Chromium
against a file:// origin (`indexedDB.open` never fires onsuccess/onerror/
onblocked/onupgradeneeded within an 8s virtual-time budget, confirmed by a
standalone probe before writing this test), so `window.QuestPhotos` is
stubbed out with fake records instead of exercising real IndexedDB. That
stub is the only thing routed around; `renderKeep()`, `paintShots()`,
`releaseUrls()` and the real nav button all run unmodified.
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
function done(){ document.title = "K>>" + JSON.stringify(out) + "<<E"; }
var frame = document.getElementById("f");
var phase = 0;

frame.addEventListener("load", function () {
  var d;
  try { d = frame.contentDocument; }
  catch (e) { out.error = "blocked: " + e.message; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }
  var w = frame.contentWindow;

  if (phase === 0) {
    phase = 1;
    try { w.localStorage.clear(); } catch (e) {}
    w.location.reload();
    return;
  }

  if (phase === 1) {
    phase = 2;
    // Mark one real zone's every step done, straight from the page's own
    // QUEST data, so heldZones() finds it without driving all six cards by
    // hand: this test is about the Keep screen's photo repaint, not the
    // completion flow test_quest_flow.py already covers.
    try {
      var Q = w.QUEST;
      var r0 = Q.rooms[0], z0 = r0.zones[0];
      var doneMap = {};
      var now = Date.now();
      z0.steps.forEach(function (st) {
        doneMap[r0.room + "|" + z0.zone + "|" + st.s] = now;
      });
      w.localStorage.setItem("6s.quest.v1", JSON.stringify({ done: doneMap }));
    } catch (e) { out.error = "seed failed: " + e; return done(); }
    w.location.reload();
    return;
  }

  if (phase === 2) {
    phase = 3;

    // Stand in for real IndexedDB (unreachable here, see module docstring).
    // Every other moving part -- renderKeep, paintShots, releaseUrls, the
    // real #go-keep button -- runs exactly as shipped.
    var seq = 0;
    var revokes = [];
    w.QuestPhotos = {
      supported: function () { return true; },
      pair: function () {
        seq += 1;
        return w.Promise.resolve({ before: { blob: { fake: seq } }, after: null });
      },
      objectUrl: function (rec) {
        return rec && rec.blob ? "blob:fake-" + seq : null;
      }
    };
    var realRevoke = w.URL.revokeObjectURL;
    w.URL.revokeObjectURL = function (u) { revokes.push(u); return realRevoke.call(w.URL, u); };

    var keepBtn = d.getElementById("go-keep");
    out.hasKeepButton = !!keepBtn;
    if (!keepBtn) { return done(); }

    keepBtn.click();
    setTimeout(function () {
      out.hasPhotoAfterFirstOpen = /has\\b/.test(d.getElementById("keep-body").innerHTML);
      out.revokesAfterFirstOpen = revokes.length;

      // The everyday case this bug lived in: leaving Keep and coming straight
      // back, the normal way (the nav button), not a reset/upload/delete.
      keepBtn.click();
      setTimeout(function () {
        out.revokesAfterSecondOpen = revokes.length;
        done();
      }, 200);
    }, 200);
  }
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-keep-profile-")
    wrap = os.path.join(SITE, "_quest_keep_leak_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=520,1440", "--virtual-time-budget=15000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=120)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"K(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the Keep screen was NOT exercised. "
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
    if not o.get("hasKeepButton"):
        bad.append("#go-keep is missing, cannot test the nav path at all")
    if not o.get("hasPhotoAfterFirstOpen"):
        bad.append("the stub photograph never rendered, so this test proved "
                    "nothing (seed or stub is broken, not the real bug)")
    if o.get("revokesAfterFirstOpen", 0) != 0:
        bad.append("a URL was revoked on the very first open, before any "
                    "photo had ever been shown: %r" % o.get("revokesAfterFirstOpen"))
    if o.get("revokesAfterSecondOpen", 0) < 1:
        bad.append(
            "opening Keep a second time via the real #go-keep button did not "
            "revoke the first visit's object URL (revokes stayed at %r): "
            "the leak this test exists to catch"
            % o.get("revokesAfterSecondOpen"))

    if bad:
        print("  Keep screen URL-leak regression:")
        for b in bad:
            print("    - " + b)
        return 1

    print("  Keep screen releases the previous visit's photo URLs before "
          "repainting: revokes 0 -> %d -> %d across two real #go-keep opens"
          % (o.get("revokesAfterFirstOpen", 0), o.get("revokesAfterSecondOpen", 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
