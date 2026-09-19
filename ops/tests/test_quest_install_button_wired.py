"""Drive the Home Quest's install prompt on a cold landing and prove the
button, once shown, actually does something when tapped.

quest.js's own comment already says the common case out loud: "The browser
fires this whenever it likes, which on a cold landing is immediately."
beforeinstallprompt arrives before a first-time visitor has done anything, so
isFirstRun() is still true, and the handler correctly holds the button hidden
until a first win exists (pendingInstall = ev; return). Once a card is
finished and applyFirstRunGate() unhides #go-install on the next render, the
button becomes visible again on the returning-visitor start screen.

The defect: the click handler that calls ev.prompt() was only ever attached
inside the beforeinstallprompt callback itself, past the same
"if (isFirstRun()) return" guard that holds the button hidden. On a cold
landing that guard fires and returns before the click listener is ever
attached. applyFirstRunGate() later sets .hidden = false, unhiding the
button, but nothing ever wires a click handler to it. A visitor who taps
"Install the app" gets no prompt and no error: a live, silent dead button,
the same "renders but does not work" shape as the cart tile A6 already found
and fixed, and the same class as CLAUDE.md 0.6's "no obvious regression" and
GOALS.md's "copy and control disagree is a P0 trust defect."

Confirmed live before fixing: dispatching a synthetic beforeinstallprompt
before any progress exists, finishing a zone, returning to the start screen,
and clicking the now-visible #go-install called the mocked ev.prompt() zero
times and left the button un-hidden.

Run:  python ops/tests/test_quest_install_button_wired.py
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
  try { d = frame.contentDocument; } catch (e) { out.error = "blocked: " + e.message; return done(); }
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
    w.__prompted = 0;

    // Cold landing: the browser offers the prompt before anything has been
    // done, which is the case quest.js's own comment names as the common one.
    var fakeEvent;
    try { fakeEvent = new w.Event("beforeinstallprompt", { cancelable: true }); }
    catch (e) { fakeEvent = d.createEvent("Event"); fakeEvent.initEvent("beforeinstallprompt", false, true); }
    fakeEvent.prompt = function () { w.__prompted++; return w.Promise.resolve(); };
    w.dispatchEvent(fakeEvent);
    out.hiddenOnColdLanding = (function(){ var e = d.getElementById("go-install"); return !e || e.hidden; })();

    // Bail past the symptom screen the fast way, straight to a real card.
    var goFirst = d.getElementById("go-first") ||
      (function(){ var b = d.getElementById("sym-other"); if (b) b.click(); return d.getElementById("go-first"); })();
    out.hasGoFirst = !!goFirst;
    if (!goFirst) return done();
    goFirst.click();

    setTimeout(function(){
      // Finish the whole zone so isFirstRun() flips false.
      var clicks = 0;
      (function advance(){
        var b = d.getElementById("c-done");
        if (b && vis(d, "view-card") && clicks < 8) {
          clicks++; b.click(); return setTimeout(advance, 220);
        }
        var again = d.getElementById("f-again");
        out.hasAgain = !!again;
        if (!again) return done();
        again.click();

        setTimeout(function(){
          var installBtn = d.getElementById("go-install");
          out.installBtnPresent = !!installBtn;
          out.installBtnShownAfterProgress = installBtn ? !installBtn.hidden : false;
          if (!installBtn || installBtn.hidden) return done();

          installBtn.click();
          setTimeout(function(){
            out.promptCalled = w.__prompted;
            out.installBtnHiddenAfterClick = installBtn.hidden;
            done();
          }, 300);
        }, 500);
      })();
    }, 700);
  }, 900);
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-install-probe-")
    wrap = os.path.join(SITE, "_quest_install_probe.html")
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
        print("  the probe did not run, so the install flow was NOT exercised. "
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
    if not o.get("hiddenOnColdLanding"):
        bad.append("install button was already visible before any progress "
                    "existed, which asks a stranger to install an app they "
                    "have not used once")
    if not o.get("hasGoFirst"):
        bad.append("could not reach the classic start screen at all")
    if not o.get("hasAgain"):
        bad.append("could not finish a zone to reach the returning-visitor "
                    "start screen")
    if not o.get("installBtnPresent"):
        bad.append("#go-install is missing from the page entirely")
    elif not o.get("installBtnShownAfterProgress"):
        bad.append("install button stayed hidden even after a cold-landing "
                    "prompt and real progress, so the promise in "
                    "applyFirstRunGate's own comment does not hold")
    else:
        if not o.get("promptCalled"):
            bad.append("tapping the visible install button never called "
                       "ev.prompt(): the button renders but does nothing, a "
                       "live dead button on a cold-landing beforeinstallprompt")
        if not o.get("installBtnHiddenAfterClick"):
            bad.append("install button did not hide itself after being tapped")

    for b in bad:
        print("  FAIL " + b)
    if bad:
        print("  observed: %s" % json.dumps(o)[:800])
        return 1

    print("  ok  a cold-landing beforeinstallprompt is held until a first "
          "win exists, then the button that appears actually calls "
          "ev.prompt() when tapped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
