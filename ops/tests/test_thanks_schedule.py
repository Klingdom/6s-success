"""Drive site/thanks.html in a real browser: does the scheduling block
actually show for the two appointment services, stay hidden for everything
else, and compose a message ops/service_orders.py's find_time() can parse.

REVIEW-COMMERCE-2026-09-07.md C9: the payment link for CN-VIRTUAL/CN-INHOME
collects no time, so ops/service_orders.py's own find_time() never had
anything to find until a customer emailed one in unprompted. This is the
block that asks on thanks.html itself, immediately after payment. A static
read of the page cannot tell whether the block actually appears for the
right two SKUs, stays hidden for a digital product, or produces a message in
the exact "14 October at 2pm" / "Oct 14 at 2pm" shape find_time()'s own
regex requires, so this drives it in headless Chromium the same way
test_shop_interactive.py drives site/shop.html: an iframe at a real page,
--dump-dom against a virtual-time-budget, JSON handed back through
document.title. No network egress: thanks.html and its inline script are
served from disk via file://.

Run:  python ops/tests/test_thanks_schedule.py
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
<style>html,body{margin:0}iframe{width:900px;height:1800px;border:0}</style>
</head><body><iframe id="f" src="thanks.html?sku=%(sku)s"></iframe><script>
var out = {};
function done(){ document.title = "S>>" + JSON.stringify(out) + "<<E"; }

var frame = document.getElementById("f");
frame.addEventListener("load", function(){
  var d = frame.contentDocument;
  if (!d || !d.body) { out.error = "no document"; return done(); }

  setTimeout(function(){
    var block = d.getElementById("schedule-block");
    out.blockHidden = block ? block.hidden : null;
    out.blockExists = !!block;
    if (!block || block.hidden) { return done(); }

    out.heading = (d.getElementById("schedule-heading") || {}).textContent || "";

    var time1 = d.getElementById("sch-time");
    var time2 = d.getElementById("sch-time2");
    var notes = d.getElementById("sch-notes");
    var form = d.getElementById("schedule-form");
    if (time1) time1.value = "14 October at 2pm";
    if (time2) time2.value = "16 October at 10am";
    if (notes) notes.value = "Front door sticks, use the side gate.";

    var okBefore = (d.getElementById("sch-ok") || {}).hidden;
    out.okHiddenBeforeSubmit = okBefore;

    if (form && form.requestSubmit) { form.requestSubmit(); }
    else if (form) {
      var ev = d.createEvent("Event");
      ev.initEvent("submit", true, true);
      form.dispatchEvent(ev);
    }

    setTimeout(function () {
      out.okHiddenAfterSubmit = (d.getElementById("sch-ok") || {}).hidden;
      out.mailtoHref = (d.getElementById("sch-mailto") || {}).getAttribute
        ? d.getElementById("sch-mailto").getAttribute("href") : null;
      out.composedBody = (d.getElementById("sch-copy") || {}).value || "";
      done();
    }, 80);
  }, 200);
});
</script></body></html>"""


def drive(sku: str) -> dict:
    found = B.find_browser()
    if not found:
        return {"_no_browser": True}
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-thanks-profile-")
    wrap = os.path.join(SITE, "_thanks_schedule_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(
        WRAPPER % {"sku": sku})
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=940,1900", "--virtual-time-budget=20000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=120)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"S(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        return {"_probe_failed": True}
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        return json.loads(raw)
    except ValueError:
        return {"_unreadable": raw[:300]}


# The exact shape ops/service_orders.py's find_time() parses: "D Month at
# HH(:MM)(am|pm)". Importing the real function rather than re-deriving the
# pattern here, so a future change to either side cannot silently disagree.
sys.path.insert(0, OPS)
import service_orders as SO                                    # noqa: E402


def main() -> int:
    problems = []

    for sku, expect_visible in (("CN-VIRTUAL", True), ("CN-INHOME", True),
                                 ("BK-EB", False), ("", False),
                                 ("NOT-A-REAL-SKU", False)):
        o = drive(sku)
        if o.get("_no_browser"):
            print("  no browser here, cannot drive thanks.html. NOT VERIFIED.")
            return 0
        if o.get("_probe_failed") or o.get("_unreadable") or o.get("error"):
            problems.append("%r: probe did not complete cleanly: %s"
                             % (sku, o))
            continue
        if not o.get("blockExists"):
            problems.append("%r: #schedule-block is not on the page at all"
                             % sku)
            continue

        visible = not o.get("blockHidden")
        if visible != expect_visible:
            problems.append(
                "sku=%r: schedule block visible=%s, expected %s"
                % (sku or "(none)", visible, expect_visible))
            continue

        if not expect_visible:
            continue

        if not o.get("heading"):
            problems.append("sku=%r: schedule-heading is empty" % sku)

        if o.get("okHiddenBeforeSubmit") is not True:
            problems.append(
                "sku=%r: #sch-ok should start hidden, before the form is "
                "submitted" % sku)
        if o.get("okHiddenAfterSubmit") is not False:
            problems.append(
                "sku=%r: #sch-ok did not un-hide after a valid submit" % sku)

        href = o.get("mailtoHref") or ""
        if not href.startswith("mailto:support@6s-success.com?"):
            problems.append("sku=%r: mailto href malformed: %r" % (sku, href))

        body = o.get("composedBody") or ""
        if "14 October at 2pm" not in body:
            problems.append(
                "sku=%r: composed message dropped the first preferred "
                "time verbatim: %r" % (sku, body[:200]))
        if "16 October at 10am" not in body:
            problems.append(
                "sku=%r: composed message dropped the second choice: %r"
                % (sku, body[:200]))
        if "Front door sticks" not in body:
            problems.append(
                "sku=%r: composed message dropped the free-text notes: %r"
                % (sku, body[:200]))
        if sku not in body:
            problems.append(
                "sku=%r: composed message never names the sku it is for"
                % sku)

        # The point of the exact placeholder shape: prove the real parser
        # this feeds, not a re-implementation of its regex, actually reads
        # the composed message back out as a datetime.
        when = SO.find_time(body)
        if when is None:
            problems.append(
                "sku=%r: ops/service_orders.py's own find_time() could not "
                "read a time out of the composed message: %r"
                % (sku, body[:200]))
        elif (when.month, when.day, when.hour) != (10, 14, 14):
            problems.append(
                "sku=%r: find_time() read %s from the composed message, "
                "expected 14 October at 14:00" % (sku, when))

    if problems:
        print("  %d problem(s):" % len(problems))
        for p in problems:
            print("    - %s" % p)
        return 1

    print("  ok  schedule block shows for CN-VIRTUAL/CN-INHOME only, "
          "composes a message find_time() can actually parse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
