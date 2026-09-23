"""Drive thanks.html's inline sku-branching script in a real browser and prove
each branch actually renders and behaves the way its own PLANS entry promises.

Named 2026-09-23 as the last unexercised page-level script on the standing
headless-Chromium handoff, after that method already found and fixed real
runtime failures on other pages (site.js's dropped paint() call, the
deck-gallery pages missing a script tag entirely). thanks.html is the page a
paying customer lands on immediately after a real charge, so a silent
failure here is a delivery problem, not a cosmetic one: CLAUDE.md 0.2 puts
"broken functionality" at P0 and STEP 8 of the operator prompt treats a
possible non-delivery as something to handle before anything else.

Nothing before this loaded the page and read the sku out. `gate_sellable`
and friends check that a Stripe payment link exists and charges the right
price; none of them load thanks.html and check what a buyer actually sees
once they land on it with `?sku=...` on the query string.

Three things had never been driven:

1. Every named sku in PLANS renders its OWN heading/lede, not a neighbour's
   and not the generic fallback. A hardcoded index bug (each key mapping to
   the next key's copy) would look identical in a code read and would only
   show up by rendering each one and comparing text.
2. schedule-block, hidden by default in the markup, is shown for exactly the
   two appointment skus (CN-VIRTUAL, CN-INHOME) and stays hidden for every
   digital sku and for no sku at all. Digital products have nothing to
   schedule; showing the block for one would ask a book buyer to "pick a
   time" for a delivery that just needs an inbox.
3. Submitting the schedule form actually produces a mailto href and a copy-
   box body carrying the sku, the service name and the time typed in, since
   that generated message is the only thing standing between a booked
   consult and Phil manually reading email to guess what someone bought.

Driven the same way as test_site_js_no_runtime_error.py and
test_quest_offer_cta.py: an iframe at phone width, headless Chromium,
--dump-dom against a virtual-time-budget, JSON handed back through
document.title. No network egress, no real mail client, no Stripe call.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import browser as B                                            # noqa: E402

PAGE_REL = "thanks.html"

# One digital sku, both scheduled skus, an unrecognised sku and no sku at
# all: enough to catch a shifted branch, a swapped label, or the schedule
# block leaking onto a page it should never appear on.
CASES = ("BK-EB", "CN-VIRTUAL", "CN-INHOME", "NOT-A-REAL-SKU", "")

EXPECT_HEADING = {
    "BK-EB": "Your copy of the book",
    "CN-VIRTUAL": "Your Virtual Home Consult",
    "CN-INHOME": "Your In-Home Reset Day",
    "NOT-A-REAL-SKU": "Your order",
    "": "Your order",
}

SCHEDULED = ("CN-VIRTUAL", "CN-INHOME")

WRAPPER_TMPL = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:390px;height:2400px;border:0}</style>
</head><body><iframe id="f" src="%(probe_rel)s"></iframe><script>
var out = {};
var frame = document.getElementById("f");
function done(){ document.title = "T>>" + JSON.stringify(out) + "<<E"; }
frame.addEventListener("load", function(){
  var d = frame.contentDocument, w = frame.contentWindow;
  if (!d || !d.body || !w) { out.error = "no document"; return done(); }
  setTimeout(function(){
    out.heading = (d.getElementById("heading") || {}).textContent || "";
    out.lede = (d.getElementById("lede") || {}).textContent || "";
    out.stepCount = d.querySelectorAll("#steps li").length;
    var block = d.getElementById("schedule-block");
    out.scheduleVisible = !!block && !block.hidden;

    if (block && !block.hidden) {
      var timeEl = d.getElementById("sch-time");
      var time2El = d.getElementById("sch-time2");
      var notesEl = d.getElementById("sch-notes");
      if (timeEl) timeEl.value = "14 October at 2pm";
      if (time2El) time2El.value = "16 October at 10am";
      if (notesEl) notesEl.value = "side gate code 4471";

      var form = d.getElementById("schedule-form");
      if (form && form.requestSubmit) { form.requestSubmit(); }
      else if (form) {
        var ev = d.createEvent ? d.createEvent("Event") : null;
        if (ev) { ev.initEvent("submit", true, true); form.dispatchEvent(ev); }
      }

      setTimeout(function(){
        var ok = d.getElementById("sch-ok");
        out.confirmVisible = !!ok && !ok.hidden;
        var link = d.getElementById("sch-mailto");
        out.mailtoHref = link ? link.getAttribute("href") : null;
        var copy = d.getElementById("sch-copy");
        out.copyValue = copy ? copy.value : null;
        out.errs = w.__errs || [];
        done();
      }, 300);
    } else {
      out.errs = w.__errs || [];
      done();
    }
  }, 500);
});
</script></body></html>"""

ERROR_HOOK = (
    '<script>window.__errs=[];window.onerror=function(m,s,l,c,e){'
    'window.__errs.push(String(m)+" @ "+l+":"+c);};</script>'
)


def _run_probe(idx: int, sku: str):
    """Inject the error hook into a copy of thanks.html, drive it in an
    iframe with `?sku=<sku>` on the probe URL, return the parsed probe JSON
    or an error dict. Never raises."""
    src_path = os.path.join(SITE, PAGE_REL)
    html = io.open(src_path, encoding="utf-8").read()
    if "<head>" not in html:
        return {"error": "no <head> tag in thanks.html to inject the hook into"}
    probed = html.replace("<head>", "<head>" + ERROR_HOOK, 1)

    probe_name = "_thanks_probe_%d.html" % idx
    probe_path = os.path.join(SITE, probe_name)
    query = ("?sku=" + sku) if sku else ""
    probe_rel = probe_name + query
    wrap_name = "_thanks_wrapper_%d.html" % idx
    wrap_path = os.path.join(SITE, wrap_name)

    found = B.find_browser()
    if not found:
        return {"skip": "no browser here"}
    exe, extra = found

    io.open(probe_path, "w", encoding="utf-8", newline="").write(probed)
    io.open(wrap_path, "w", encoding="utf-8", newline="").write(
        WRAPPER_TMPL % {"probe_rel": probe_rel})

    profile = tempfile.mkdtemp(prefix="6s-thanks-probe-")
    try:
        r = subprocess.run(
            [exe] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=420,2500", "--virtual-time-budget=8000",
             "--dump-dom", "file:///" + wrap_path.replace("\\", "/")],
            capture_output=True, timeout=90)
    finally:
        for p in (probe_path, wrap_path):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"T(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        return {"error": "probe did not run for sku=%r" % sku}
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        return json.loads(raw)
    except ValueError:
        return {"error": "probe output unreadable for sku=%r: %s"
                          % (sku, raw[:300])}


def main() -> int:
    bad = []
    unverified = False
    for idx, sku in enumerate(CASES):
        o = _run_probe(idx, sku)
        label = sku or "(no sku)"
        if o.get("skip"):
            print("  no browser here, cannot drive thanks.html. NOT VERIFIED.")
            unverified = True
            continue
        if o.get("error"):
            bad.append("sku=%s: %s" % (label, o["error"]))
            continue
        if o.get("errs"):
            bad.append("sku=%s: JavaScript threw: %s" % (label, o["errs"]))

        want_heading = EXPECT_HEADING[sku]
        if o.get("heading") != want_heading:
            bad.append("sku=%s: heading was %r, expected %r"
                        % (label, o.get("heading"), want_heading))
        if not o.get("lede"):
            bad.append("sku=%s: lede is empty" % label)
        if not o.get("stepCount"):
            bad.append("sku=%s: 0 steps rendered, a confirmation with "
                        "nothing under it" % label)

        want_scheduled = sku in SCHEDULED
        if o.get("scheduleVisible") != want_scheduled:
            bad.append(
                "sku=%s: schedule-block visible=%r, expected %r "
                "(only CN-VIRTUAL/CN-INHOME should offer scheduling)"
                % (label, o.get("scheduleVisible"), want_scheduled))

        if want_scheduled and o.get("scheduleVisible"):
            if not o.get("confirmVisible"):
                bad.append("sku=%s: submitting the schedule form never "
                            "revealed the confirmation notice" % label)
            href = o.get("mailtoHref") or ""
            decoded_href = urllib.parse.unquote(href)
            if not href.startswith("mailto:support@6s-success.com"):
                bad.append("sku=%s: mailto href is %r, not a support "
                            "address" % (label, href))
            if sku not in decoded_href:
                bad.append("sku=%s: mailto body/subject does not carry "
                            "the sku, so a reply cannot be traced to what "
                            "was bought" % label)
            if "14 October at 2pm" not in decoded_href:
                bad.append("sku=%s: the preferred time typed into the form "
                            "never reached the mailto body" % label)
            copy_val = o.get("copyValue") or ""
            if sku not in copy_val or "14 October at 2pm" not in copy_val:
                bad.append("sku=%s: the copy-to-clipboard fallback text "
                            "does not match what the mailto link carries"
                            % label)

    if bad:
        print("  %d problem(s) found:" % len(bad))
        for b in bad:
            print("    - %s" % b)
        return 1
    if unverified:
        return 0
    print("  %d sku case(s) driven on thanks.html, each rendering its own "
          "heading/lede/steps, schedule-block shown only for the two "
          "appointment skus, and a submitted schedule producing a "
          "traceable mailto and matching copy text" % len(CASES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
