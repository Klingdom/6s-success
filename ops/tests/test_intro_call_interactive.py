"""Drive site/consulting.html's free #intro-call form in a real browser:
fill it in, submit it, and watch what actually happens.

Every existing intro-call check (check_intro_call_current /
gate_intro_call_current) reads static HTML text: the section exists, the
required field ids exist, the tracking call string is present somewhere in
the page. None of them has ever actually typed into the form and clicked
submit, the same gap test_shop_interactive.py's own docstring names for
shop.html. REVIEW-COMMERCE-2026-09-07.md C10.

What this checks, as a real visitor filling in the form would:

    submitting with the required fields present succeeds (no native
      validation block) and reveals the success notice;
    the composed mailto link carries the right subject and the visitor's
      own name/email/room, plus the origin ("Came from: zone (...)") when
      the page was reached with a ?from= query string;
    the copy-box fallback textarea holds the same composed message;
    window.Measure.track fires exactly once, with the event name
      "intro-call-request" and a payload that carries only the bounded
      "from" field, never the visitor's name, email, room or message
      (CLAUDE.md section 47: no free text in an analytics event);
    submitting with a required field left empty does NOT fire the
      tracking event (native `required` validation should block it).

Driven the same way ops/tests/test_shop_interactive.py drives shop.html:
an iframe at a real viewport width, headless Chromium, --dump-dom against
a virtual-time-budget, JSON handed back through document.title. No network
egress is needed or used: consulting.html, site.css, site.js and
measure.js are all served from disk via file://.
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
<style>html,body{margin:0}iframe{width:1100px;height:3400px;border:0}</style>
</head><body>
<iframe id="f" src="consulting.html?from=zone:entryway-the-landing-spot#intro-call"></iframe>
<script>
var out = {};
function done(){ document.title = "S>>" + JSON.stringify(out) + "<<E"; }

var frame = document.getElementById("f");
frame.addEventListener("load", function(){
  var d = frame.contentDocument;
  var w = frame.contentWindow;
  if (!d || !d.body || !w) { out.error = "no document"; return done(); }

  setTimeout(function(){
    var calls = [];
    /* measure.js has already run (deferred, fires before this timeout),
       so window.Measure exists; replace .track with a spy before the
       form's own submit handler can call the real one. */
    if (w.Measure) { w.Measure.track = function (name, data) { calls.push([name, data]); }; }
    else { out.error = "window.Measure never appeared"; return done(); }

    var form = d.getElementById("intro-call-form");
    if (!form) { out.error = "no #intro-call-form in the document"; return done(); }

    function fill(id, val) {
      var el = d.getElementById(id);
      if (el) { el.value = val; }
    }
    function readState(label) {
      var ok = d.getElementById("intro-call-success");
      var mailto = d.getElementById("intro-call-mailto");
      var copy = d.getElementById("intro-call-copy");
      return {
        label: label,
        successVisible: ok ? !ok.hidden : null,
        mailtoHref: mailto ? mailto.getAttribute("href") : null,
        copyValue: copy ? copy.value : null,
        trackCalls: calls.slice()
      };
    }

    /* Case A: an empty, required field should block native submission,
       so nothing should fire. */
    fill("ic-name", ""); fill("ic-email", ""); fill("ic-room", ""); fill("ic-message", "");
    form.querySelector("button[type=submit]").click();
    out.emptySubmit = readState("empty");

    /* Case B: every required field filled in should succeed. */
    fill("ic-name", "Jamie Rivera");
    fill("ic-email", "jamie@example.com");
    fill("ic-room", "Kitchen");
    fill("ic-message", "The counter never stays clear past Tuesday.");
    calls.length = 0;
    form.querySelector("button[type=submit]").click();
    out.filledSubmit = readState("filled");

    done();
  }, 300);
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive consulting.html. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-introcall-profile-")
    wrap = os.path.join(SITE, "_intro_call_interactive_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=1140,3500", "--virtual-time-budget=25000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"S(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the form was NOT exercised. "
              "This is unchecked, not working.")
        return 1
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        o = json.loads(raw)
    except ValueError:
        print("  probe output unreadable: %s" % raw[:300])
        return 1

    if o.get("error"):
        print("  probe error: %s" % o["error"])
        return 1

    bad = []

    empty = o.get("emptySubmit", {})
    if empty.get("successVisible"):
        bad.append("submitting with every field empty still showed the "
                    "success notice; native `required` validation is not "
                    "blocking it")
    if empty.get("trackCalls"):
        bad.append("submitting with every field empty still fired a "
                    "tracking event: %r" % empty.get("trackCalls"))

    filled = o.get("filledSubmit", {})
    if not filled.get("successVisible"):
        bad.append("submitting a fully filled form did not reveal the "
                    "success notice")

    mailto = filled.get("mailtoHref") or ""
    if "subject=" not in mailto or "which%20zone%20first" not in mailto.lower():
        bad.append("mailto href missing the expected subject: %r" % mailto)
    for needle in ("Jamie%20Rivera", "jamie%40example.com", "Kitchen"):
        if needle not in mailto:
            bad.append("mailto href missing %r: %r" % (needle, mailto))
    if "zone" not in mailto or "entryway-the-landing-spot" not in mailto:
        bad.append("mailto href does not carry the ?from= origin: %r" % mailto)

    copy_val = filled.get("copyValue") or ""
    if "Jamie Rivera" not in copy_val or "Kitchen" not in copy_val:
        bad.append("copy-box fallback missing the composed message: %r" % copy_val)

    calls = filled.get("trackCalls") or []
    if len(calls) != 1:
        bad.append("expected exactly 1 tracking call on a successful "
                    "submit, got %d: %r" % (len(calls), calls))
    else:
        name, data = calls[0]
        if name != "intro-call-request":
            bad.append("tracking event name is %r, expected "
                        "'intro-call-request'" % name)
        data = data or {}
        allowed = {"from"}
        leaked = [k for k in data if k not in allowed]
        if leaked:
            bad.append("tracking event carries field(s) beyond {from}: %r "
                        "(CLAUDE.md 47: no free text in an analytics "
                        "event)" % leaked)
        for v in data.values():
            for needle in ("Jamie", "jamie@example.com", "Kitchen", "Tuesday"):
                if isinstance(v, str) and needle in v:
                    bad.append("tracking event leaked visitor-entered text: "
                                "%r in %r" % (needle, data))
        if data.get("from") != "zone":
            bad.append("tracking event's from= is %r, expected 'zone' from "
                        "the iframe's own ?from=zone:... query string" %
                        data.get("from"))

    if bad:
        print("FAIL")
        for b in bad:
            print(" -", b)
        return 1
    print(f"PASS ({6} checks: empty-submit blocked, filled-submit succeeds, "
          f"mailto composed correctly, copy-box fallback populated, "
          f"tracking event fires once with a bounded payload, origin carried "
          f"through)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
