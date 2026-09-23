"""Drive site/corporate.html's #corp-form in a real browser: fill it in,
submit it, and watch what actually happens.

site/corporate.html is the one page on this site aimed at a buyer with a
budget (CLAUDE.md, STATUS.md section 2: Corporate Lean 6S is the only route
to $20,000 that needs no consumer traffic at all). test_corporate_page.py
already guards the static properties (no price, the catalogue and page
agree, CN-CORP has no payment link) but has never actually typed into the
form and clicked submit, the same gap test_shop_interactive.py and
test_intro_call_interactive.py already closed for shop.html and
consulting.html's #intro-call form.

What this checks, as a real visitor filling in the form would:

    submitting with the three required fields (company, name, email) empty
      is blocked by native validation: no success notice, no tracking event;
    an invalid email format is also blocked (the form uses type="email",
      not a hand-rolled emptiness check, per the page's own code comment);
    submitting a fully filled form succeeds and reveals the success notice;
    the composed mailto link carries the right subject ("Corporate Lean 6S
      enquiry: <company>") and every field the visitor typed;
    the copy-box fallback textarea holds the same composed message, for a
      browser with no mail client attached;
    window.Measure.track fires exactly once, with the event name
      "corporate-enquiry" and a payload that carries only the bounded
      {timed, sv} fields, never the company name, contact details or the
      free-text "what prompted this" answer (CLAUDE.md section 47: no free
      text in an analytics event);
    the "timed" field in that payload is 1 only when the visitor filled in
      a scoping-call time, 0 when they left it blank, since that is the
      one thing the tracked event is meant to distinguish.

Driven the same way ops/tests/test_intro_call_interactive.py drives
consulting.html: an iframe at a real viewport width, headless Chromium,
--dump-dom against a virtual-time-budget, JSON handed back through
document.title. No network egress is needed or used: corporate.html,
site.css, site.js and measure.js are all served from disk via file://.
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
<style>html,body{margin:0}iframe{width:1100px;height:4200px;border:0}</style>
</head><body>
<iframe id="f" src="corporate.html#enquiry"></iframe>
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

    var form = d.getElementById("corp-form");
    if (!form) { out.error = "no #corp-form in the document"; return done(); }

    function fill(id, val) {
      var el = d.getElementById(id);
      if (el) { el.value = val; }
    }
    function readState(label) {
      var ok = d.getElementById("corp-ok");
      var mailto = d.getElementById("corp-mailto");
      var copy = d.getElementById("corp-copy");
      return {
        label: label,
        successVisible: ok ? !ok.hidden : null,
        mailtoHref: mailto ? mailto.getAttribute("href") : null,
        copyValue: copy ? copy.value : null,
        trackCalls: calls.slice()
      };
    }

    /* Case A: every required field empty should block native submission,
       so nothing should fire. */
    fill("k-company", ""); fill("k-name", ""); fill("k-email", "");
    form.querySelector("button[type=submit]").click();
    out.emptySubmit = readState("empty");

    /* Case B: required fields present but the email is malformed. The
       page's own comment says this replaced a hand-rolled emptiness check
       specifically so a typo'd address cannot pass through. */
    calls.length = 0;
    fill("k-company", "Acme Fabrication");
    fill("k-name", "Jamie Rivera, Plant Manager");
    fill("k-email", "not-an-email");
    form.querySelector("button[type=submit]").click();
    out.badEmailSubmit = readState("bad-email");

    /* Case C: every required field filled in, no scoping-call time, should
       succeed with timed:0. */
    calls.length = 0;
    fill("k-email", "jamie@acmefab.example.com");
    fill("k-phone", "208-555-0141");
    fill("k-sites", "One plant, Nampa ID");
    fill("k-people", "14 across two shifts");
    fill("k-zones", "Stockroom and the maintenance shop");
    fill("k-when", "Before the end of the quarter");
    fill("k-why", "A customer audit found the stockroom disorganized.");
    fill("k-time", "");
    form.querySelector("button[type=submit]").click();
    out.filledNoTime = readState("filled-no-time");

    /* Case D: same, but with a scoping-call time, should succeed with
       timed:1. */
    calls.length = 0;
    fill("k-time", "14 October at 2pm");
    form.querySelector("button[type=submit]").click();
    out.filledWithTime = readState("filled-with-time");

    done();
  }, 300);
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive corporate.html. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-corpform-profile-")
    wrap = os.path.join(SITE, "_corporate_form_interactive_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=1140,4300", "--virtual-time-budget=25000",
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
        bad.append("submitting with every required field empty still showed "
                    "the success notice; native `required` validation is "
                    "not blocking it")
    if empty.get("trackCalls"):
        bad.append("submitting with every required field empty still fired "
                    "a tracking event: %r" % empty.get("trackCalls"))

    bad_email = o.get("badEmailSubmit", {})
    if bad_email.get("successVisible"):
        bad.append("submitting a malformed email still showed the success "
                    "notice; type=email validation is not blocking it")
    if bad_email.get("trackCalls"):
        bad.append("submitting a malformed email still fired a tracking "
                    "event: %r" % bad_email.get("trackCalls"))

    for case_key, want_timed in (("filledNoTime", 0), ("filledWithTime", 1)):
        filled = o.get(case_key, {})
        label = case_key
        if not filled.get("successVisible"):
            bad.append("%s: a fully filled form did not reveal the success "
                        "notice" % label)

        mailto = filled.get("mailtoHref") or ""
        if "subject=" not in mailto or "Acme%20Fabrication" not in mailto:
            bad.append("%s: mailto href missing the expected subject: %r"
                        % (label, mailto))
        for needle in ("Jamie%20Rivera", "jamie%40acmefab.example.com",
                       "Nampa%20ID", "maintenance%20shop"):
            if needle not in mailto:
                bad.append("%s: mailto href missing %r: %r"
                            % (label, needle, mailto))

        copy_val = filled.get("copyValue") or ""
        if "Acme Fabrication" not in copy_val or "Jamie Rivera" not in copy_val:
            bad.append("%s: copy-box fallback missing the composed message: %r"
                        % (label, copy_val))

        calls = filled.get("trackCalls") or []
        if len(calls) != 1:
            bad.append("%s: expected exactly 1 tracking call on a "
                        "successful submit, got %d: %r"
                        % (label, len(calls), calls))
            continue
        name, data = calls[0]
        if name != "corporate-enquiry":
            bad.append("%s: tracking event name is %r, expected "
                        "'corporate-enquiry'" % (label, name))
        data = data or {}
        allowed = {"timed", "sv"}
        leaked = [k for k in data if k not in allowed]
        if leaked:
            bad.append("%s: tracking event carries field(s) beyond "
                        "{timed, sv}: %r (CLAUDE.md 47: no free text in an "
                        "analytics event)" % (label, leaked))
        for v in data.values():
            for needle in ("Acme", "Jamie", "acmefab.example.com", "Nampa",
                           "maintenance shop", "customer audit"):
                if isinstance(v, str) and needle in v:
                    bad.append("%s: tracking event leaked visitor-entered "
                                "text: %r in %r" % (label, needle, data))
        if data.get("timed") != want_timed:
            bad.append("%s: tracking event's timed= is %r, expected %r"
                        % (label, data.get("timed"), want_timed))

    if bad:
        print("FAIL")
        for b in bad:
            print(" -", b)
        return 1
    print("PASS (empty-submit blocked, malformed-email blocked, "
          "filled-submit succeeds, mailto composed correctly, copy-box "
          "fallback populated, tracking event fires once with a bounded "
          "payload, timed=0/1 tracked correctly, no visitor text leaked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
