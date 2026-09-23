"""Drive site/contact.html's #contact-form in a real browser: fill it in,
submit it, and watch what actually happens.

contact.html is the fallback funnel for every product page's "Request a
quote" link and the only page a visitor with an unusual question ever
reaches. test_shop_interactive.py, test_intro_call_interactive.py and
test_corporate_form_interactive.py already close this exact gap for
shop.html, consulting.html and corporate.html; contact.html had only a
static test (site/tests would be ops/tests/test_contact_page.py if one
existed; none does) and had never actually been submitted by a script,
named as a handoff by the 2026-09-23 02:4x PM check-in.

What this checks, as a real visitor filling in the form would:

    submitting with the three required fields (name, email, message) empty
      is blocked by native validation: no success notice, no tracking event;
    an invalid email format is also blocked (the field uses type="email");
    submitting a fully filled form succeeds and reveals the success notice;
    the composed mailto link and the copy-box fallback both carry the
      subject, topic, name, email and message the visitor typed;
    window.Measure.track fires exactly once, named "contact-submit", with
      a payload that carries only the bounded {topic} field (one of five
      fixed dropdown options), never the visitor's name, email or message
      (CLAUDE.md section 47: no free text in an analytics event);
    a visitor arriving via a known product's "Request a quote" link
      (?ref=CN-CORP) gets an "About: Corporate Lean 6S" line prepended to
      the composed message, so they never have to repeat what they already
      clicked to say;
    a visitor arriving with an unrecognised or hostile ?ref= value (not in
      the page's own fixed NAMES lookup) gets no "About:" line and, more to
      the point, that raw query value never appears anywhere in the
      composed mailto or copy-box text: the page's own code comment says
      ?ref= is attacker-controlled and must never be reflected unvalidated
      into the DOM, and this is the one place that claim can actually be
      tested rather than trusted.

Driven the same way the three sibling tests drive their own pages: iframes
at a real viewport width, headless Chromium, --dump-dom against a
virtual-time-budget, JSON handed back through document.title. No network
egress is needed or used: contact.html, site.css, site.js and measure.js
are all served from disk via file://. Three iframes in one page, since
?ref= is read once from location.search at load time and cannot be
changed by a later submit on the same document.
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
<style>html,body{margin:0}iframe{width:1100px;height:1400px;border:0}</style>
</head><body>
<iframe id="f1" src="contact.html"></iframe>
<iframe id="f2" src="contact.html?ref=CN-CORP"></iframe>
<iframe id="f3" src="contact.html?ref=%3Cscript%3Ealert(1)%3C%2Fscript%3E"></iframe>
<script>
var out = {};
var pending = 3;
function maybeDone(){ pending -= 1; if (pending === 0) {
  document.title = "S>>" + JSON.stringify(out) + "<<E";
} }

function readState(d, label) {
  var ok = d.getElementById("contact-success");
  var mailto = d.getElementById("contact-mailto");
  var copy = d.getElementById("contact-copy");
  return {
    label: label,
    successVisible: ok ? !ok.hidden : null,
    mailtoHref: mailto ? mailto.getAttribute("href") : null,
    copyValue: copy ? copy.value : null
  };
}

function fill(d, id, val) {
  var el = d.getElementById(id);
  if (el) { el.value = val; }
}

/* Frame 1: no ?ref=, exercises validation blocking and a normal successful
   submit, plus the tracking-event payload shape. */
document.getElementById("f1").addEventListener("load", function(){
  var frame = this;
  var d = frame.contentDocument;
  var w = frame.contentWindow;
  if (!d || !d.body || !w) { out.f1error = "no document"; return maybeDone(); }

  setTimeout(function(){
    var calls = [];
    if (w.Measure) { w.Measure.track = function (name, data) { calls.push([name, data]); }; }
    else { out.f1error = "window.Measure never appeared"; return maybeDone(); }

    var form = d.getElementById("contact-form");
    if (!form) { out.f1error = "no #contact-form in the document"; return maybeDone(); }

    /* Case A: every required field empty. */
    fill(d, "c-name", ""); fill(d, "c-email", ""); fill(d, "c-message", "");
    form.querySelector("button[type=submit]").click();
    out.emptySubmit = readState(d, "empty");
    out.emptySubmitCalls = calls.slice();

    /* Case B: required fields present but the email is malformed. */
    calls.length = 0;
    fill(d, "c-name", "Jordan Ellis");
    fill(d, "c-email", "not-an-email");
    fill(d, "c-message", "The hall closet never stays sorted past a week.");
    form.querySelector("button[type=submit]").click();
    out.badEmailSubmit = readState(d, "bad-email");
    out.badEmailSubmitCalls = calls.slice();

    /* Case C: every required field filled correctly, a non-default topic
       chosen, should succeed and track that topic. */
    calls.length = 0;
    fill(d, "c-email", "jordan.ellis@example.com");
    var topic = d.getElementById("c-topic");
    if (topic) { topic.value = "Consulting / quote"; }
    form.querySelector("button[type=submit]").click();
    out.filled = readState(d, "filled");
    out.filledCalls = calls.slice();

    maybeDone();
  }, 300);
});

/* Frame 2: ?ref=CN-CORP, a recognised product SKU, should prepend an
   "About: Corporate Lean 6S" line to the composed message. */
document.getElementById("f2").addEventListener("load", function(){
  var frame = this;
  var d = frame.contentDocument;
  var w = frame.contentWindow;
  if (!d || !d.body || !w) { out.f2error = "no document"; return maybeDone(); }

  setTimeout(function(){
    var form = d.getElementById("contact-form");
    if (!form) { out.f2error = "no #contact-form in the document"; return maybeDone(); }
    fill(d, "c-name", "Priya Nair");
    fill(d, "c-email", "priya@example.com");
    fill(d, "c-message", "What is included in the corporate engagement?");
    form.querySelector("button[type=submit]").click();
    out.knownRef = readState(d, "known-ref");
    maybeDone();
  }, 300);
});

/* Frame 3: ?ref= carries an unrecognised, hostile value. Nothing derived
   from it should appear anywhere in the composed message. */
document.getElementById("f3").addEventListener("load", function(){
  var frame = this;
  var d = frame.contentDocument;
  var w = frame.contentWindow;
  if (!d || !d.body || !w) { out.f3error = "no document"; return maybeDone(); }

  setTimeout(function(){
    var form = d.getElementById("contact-form");
    if (!form) { out.f3error = "no #contact-form in the document"; return maybeDone(); }
    fill(d, "c-name", "Sam Okafor");
    fill(d, "c-email", "sam@example.com");
    fill(d, "c-message", "Do you ship internationally?");
    form.querySelector("button[type=submit]").click();
    out.unknownRef = readState(d, "unknown-ref");
    maybeDone();
  }, 300);
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive contact.html. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-contactform-profile-")
    wrap = os.path.join(SITE, "_contact_form_interactive_probe.html")
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

    for key in ("f1error", "f2error", "f3error"):
        if o.get(key):
            print("  probe error (%s): %s" % (key, o[key]))
            return 1

    bad = []

    empty = o.get("emptySubmit", {})
    if empty.get("successVisible"):
        bad.append("submitting with every required field empty still showed "
                    "the success notice; native `required` validation is "
                    "not blocking it")
    if o.get("emptySubmitCalls"):
        bad.append("submitting with every required field empty still fired "
                    "a tracking event: %r" % o.get("emptySubmitCalls"))

    bad_email = o.get("badEmailSubmit", {})
    if bad_email.get("successVisible"):
        bad.append("submitting a malformed email still showed the success "
                    "notice; type=email validation is not blocking it")
    if o.get("badEmailSubmitCalls"):
        bad.append("submitting a malformed email still fired a tracking "
                    "event: %r" % o.get("badEmailSubmitCalls"))

    filled = o.get("filled", {})
    if not filled.get("successVisible"):
        bad.append("a fully filled form did not reveal the success notice")

    mailto = filled.get("mailtoHref") or ""
    if "subject=" not in mailto or "Consulting" not in mailto:
        bad.append("mailto href missing the expected topic in its subject: %r"
                    % mailto)
    for needle in ("Jordan%20Ellis", "jordan.ellis%40example.com",
                   "hall%20closet"):
        if needle not in mailto:
            bad.append("mailto href missing %r: %r" % (needle, mailto))

    copy_val = filled.get("copyValue") or ""
    if "Jordan Ellis" not in copy_val or "jordan.ellis@example.com" not in copy_val:
        bad.append("copy-box fallback missing the composed message: %r"
                    % copy_val)

    calls = o.get("filledCalls") or []
    if len(calls) != 1:
        bad.append("expected exactly 1 tracking call on a successful submit, "
                    "got %d: %r" % (len(calls), calls))
    else:
        name, data = calls[0]
        if name != "contact-submit":
            bad.append("tracking event name is %r, expected 'contact-submit'"
                        % name)
        data = data or {}
        allowed = {"topic"}
        leaked = [k for k in data if k not in allowed]
        if leaked:
            bad.append("tracking event carries field(s) beyond {topic}: %r "
                        "(CLAUDE.md 47: no free text in an analytics event)"
                        % leaked)
        if data.get("topic") != "Consulting / quote":
            bad.append("tracking event's topic= is %r, expected "
                        "'Consulting / quote'" % data.get("topic"))
        for v in data.values():
            for needle in ("Jordan", "jordan.ellis", "hall closet"):
                if isinstance(v, str) and needle in v:
                    bad.append("tracking event leaked visitor-entered text: "
                                "%r in %r" % (needle, data))

    known_ref = o.get("knownRef", {})
    if not known_ref.get("successVisible"):
        bad.append("known-ref case: a fully filled form did not reveal the "
                    "success notice")
    known_mailto = known_ref.get("mailtoHref") or ""
    known_copy = known_ref.get("copyValue") or ""
    if "About%3A%20Corporate%20Lean%206S" not in known_mailto:
        bad.append("known ?ref=CN-CORP did not prepend the expected "
                    "'About: Corporate Lean 6S' line to the mailto body: %r"
                    % known_mailto)
    if "About: Corporate Lean 6S" not in known_copy:
        bad.append("known ?ref=CN-CORP did not prepend the expected "
                    "'About: Corporate Lean 6S' line to the copy-box "
                    "fallback: %r" % known_copy)

    unknown_ref = o.get("unknownRef", {})
    if not unknown_ref.get("successVisible"):
        bad.append("unknown-ref case: a fully filled form did not reveal "
                    "the success notice")
    unknown_mailto = unknown_ref.get("mailtoHref") or ""
    unknown_copy = unknown_ref.get("copyValue") or ""
    if "About:" in unknown_copy or "About%3A" in unknown_mailto:
        bad.append("an unrecognised ?ref= value still produced an 'About:' "
                    "line, meaning it was trusted rather than looked up: "
                    "mailto=%r copy=%r" % (unknown_mailto, unknown_copy))
    for leaked_needle in ("script", "alert", "%3Cscript%3E"):
        if leaked_needle in unknown_mailto or leaked_needle in unknown_copy:
            bad.append("an unrecognised, hostile ?ref= value leaked into the "
                        "composed message: %r found in mailto=%r copy=%r"
                        % (leaked_needle, unknown_mailto, unknown_copy))

    if bad:
        print("FAIL")
        for b in bad:
            print(" -", b)
        return 1
    print("PASS (empty-submit blocked, malformed-email blocked, "
          "filled-submit succeeds, mailto/copy-box composed correctly, "
          "tracking event fires once with a bounded {topic} payload, no "
          "visitor text leaked, known ?ref= prepends the right About line, "
          "unknown/hostile ?ref= is ignored and never reflected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
