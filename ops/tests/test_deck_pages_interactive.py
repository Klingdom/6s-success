"""Drive kitchen-deck.html and deck-gallery.html in a real browser and prove
their own interactive markup actually works, instead of trusting it does.

Handed to the operator by name across several 2026-09-23 cycles once the
same method (load a real page, click the real controls, watch for a thrown
error) found and fixed a live sitewide JS crash on index.html
(test_site_js_no_runtime_error.py). These two pages were the two unblocked
pages that method had not yet been run against: kitchen-deck.html is a
72-card native-`<details>` flip deck with no JS dependency at all, and
deck-gallery.html adds a real inline script (chip filtering, card flip via
aria-pressed) that nothing had ever clicked in a browser before.

This test does what a static read cannot: actually click the nav toggle, a
card's flip button, a `<details>` summary and a filter chip, and fail loudly
if the DOM does not respond the way the page's own markup and inline script
say it should, or if window.onerror ever fired. Driven the same way the
sitewide and shop/contact interactive tests already drive their own pages:
an iframe at a real viewport width, headless Chromium, --dump-dom against a
virtual-time-budget, JSON handed back through document.title. No network
egress is needed or used.
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

ERROR_HOOK = (
    '<script>window.__errs=[];window.onerror=function(m,s,l,c,e){'
    'window.__errs.push(String(m)+" @ "+l+":"+c);};</script>'
)

WRAPPER_TMPL = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:1100px;height:3200px;border:0}</style>
</head><body><iframe id="f" src="%(probe_rel)s"></iframe><script>
var out = {};
var frame = document.getElementById("f");
function done(){ document.title = "S>>" + JSON.stringify(out) + "<<E"; }
frame.addEventListener("load", function(){
  var d = frame.contentDocument, w = frame.contentWindow;
  if (!d || !d.body || !w) { out.error = "no document"; return done(); }
  setTimeout(function(){
    var tog = d.querySelector(".nav-toggle");
    out.hasNavToggle = !!tog;
    var navBefore = tog ? tog.getAttribute("aria-expanded") : null;
    if (tog) tog.click();
    var navAfter = tog ? tog.getAttribute("aria-expanded") : null;
    out.navToggleChangedAria = (tog != null) && (navBefore !== navAfter);
    var navEl = d.querySelector(".nav");
    out.navToggleOpenedClass = !!(navEl && navEl.classList.contains("open"));

    %(page_probe)s

    out.errs = w.__errs || [];
    done();
  }, 900);
});
</script></body></html>"""

KITCHEN_DECK_PROBE = """
    var det = d.querySelector("details.kback");
    out.hasDetails = !!det;
    if (det) {
      var sum = det.querySelector("summary");
      out.openBefore = det.open;
      if (sum) sum.click();
      out.openAfterFirstClick = det.open;
      if (sum) sum.click();
      out.openAfterSecondClick = det.open;
    }
    out.cardCount = d.querySelectorAll(".kcard").length;
"""

DECK_GALLERY_PROBE = """
    var flip = d.querySelector(".flip");
    out.hasFlip = !!flip;
    if (flip) {
      out.flipPressedBefore = flip.getAttribute("aria-pressed");
      out.flipLabelBefore = flip.getAttribute("aria-label");
      flip.click();
      out.flipPressedAfter = flip.getAttribute("aria-pressed");
      out.flipLabelAfter = flip.getAttribute("aria-label");
    }
    var chip = d.querySelector('.chips button[data-t="Problem"]');
    var allChip = d.querySelector('.chips button[data-t="all"]');
    out.hasChip = !!chip;
    if (chip) {
      chip.click();
      var groups = [].slice.call(d.querySelectorAll(".grp"));
      out.problemGroupHidden = groups.filter(function (g) {
        return g.dataset.t === "Problem";
      }).every(function (g) { return !g.hidden; });
      out.otherGroupsHidden = groups.filter(function (g) {
        return g.dataset.t !== "Problem";
      }).every(function (g) { return g.hidden; });
      out.chipPressedAfter = chip.getAttribute("aria-pressed");
      if (allChip) allChip.click();
      out.allGroupsVisibleAfterReset = groups.every(function (g) {
        return !g.hidden;
      });
    }
"""

PAGES = (
    ("kitchen-deck.html", KITCHEN_DECK_PROBE),
    ("deck-gallery.html", DECK_GALLERY_PROBE),
)


def _run_probe(idx: int, page_rel: str, page_probe: str):
    """Inject the error hook into a copy of `page_rel`, drive it in an
    iframe, return the parsed probe JSON or an error dict. Never raises."""
    src_path = os.path.join(SITE, page_rel)
    html = io.open(src_path, encoding="utf-8").read()
    if "<head>" not in html:
        return {"error": "no <head> tag in %s to inject the hook into" % page_rel}
    probed = html.replace("<head>", "<head>" + ERROR_HOOK, 1)

    # The probe copy must live next to the original (not at the site root),
    # or every page-relative asset href resolves one directory too high and
    # silently 404s, which would make a broken control look broken for the
    # wrong reason: the asset never loading, not the behaviour this test
    # exists to check.
    probe_dir = os.path.dirname(src_path)
    probe_name = "_deck_probe_%d.html" % idx
    probe_path = os.path.join(probe_dir, probe_name)
    probe_rel = os.path.relpath(probe_path, SITE).replace(os.sep, "/")
    wrap_name = "_deck_wrapper_%d.html" % idx
    wrap_path = os.path.join(SITE, wrap_name)

    found = B.find_browser()
    if not found:
        return {"skip": "no browser here"}
    exe, extra = found

    io.open(probe_path, "w", encoding="utf-8", newline="").write(probed)
    io.open(wrap_path, "w", encoding="utf-8", newline="").write(
        WRAPPER_TMPL % {"probe_rel": probe_rel, "page_probe": page_probe})

    profile = tempfile.mkdtemp(prefix="6s-deck-probe-")
    try:
        r = subprocess.run(
            [exe] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=1140,3300", "--virtual-time-budget=8000",
             "--dump-dom", "file:///" + wrap_path.replace("\\", "/")],
            capture_output=True, timeout=90)
    finally:
        for p in (probe_path, wrap_path):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"S(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        return {"error": "probe did not run against %s" % page_rel}
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        return json.loads(raw)
    except ValueError:
        return {"error": "probe output unreadable for %s: %s"
                          % (page_rel, raw[:300])}


def _check_common(page: str, o: dict, bad: list) -> None:
    if o.get("errs"):
        bad.append("%s: JavaScript threw during load: %s" % (page, o["errs"]))
    if not o.get("hasNavToggle"):
        bad.append("%s: no .nav-toggle button found" % page)
    elif not o.get("navToggleChangedAria"):
        bad.append(
            "%s: clicking .nav-toggle did not change aria-expanded; the "
            "click handler in site.js's DOMContentLoaded listener never ran"
            % page)
    elif not o.get("navToggleOpenedClass"):
        bad.append("%s: .nav-toggle changed aria-expanded but .nav never "
                    "gained the open class" % page)


def _check_kitchen_deck(o: dict, bad: list) -> None:
    page = "kitchen-deck.html"
    if not o.get("hasDetails"):
        bad.append("%s: no details.kback card back found" % page)
        return
    if o.get("openBefore"):
        bad.append("%s: a card back rendered already open" % page)
    if not o.get("openAfterFirstClick"):
        bad.append("%s: clicking a card's summary did not open its details "
                    "(native <details> toggle did not fire)" % page)
    if o.get("openAfterSecondClick"):
        bad.append("%s: clicking a card's summary a second time did not "
                    "close its details" % page)
    if not o.get("cardCount"):
        bad.append("%s: no .kcard elements found on the page" % page)


def _check_deck_gallery(o: dict, bad: list) -> None:
    page = "deck-gallery.html"
    if not o.get("hasFlip"):
        bad.append("%s: no .flip card button found" % page)
    else:
        if o.get("flipPressedBefore") != "false":
            bad.append("%s: a card rendered already flipped" % page)
        if o.get("flipPressedAfter") != "true":
            bad.append("%s: clicking .flip did not set aria-pressed=true; "
                        "the grid's click handler never ran" % page)
        before, after = o.get("flipLabelBefore"), o.get("flipLabelAfter")
        if before == after:
            bad.append("%s: clicking .flip did not update aria-label to "
                        "say which face is showing" % page)
    if not o.get("hasChip"):
        bad.append("%s: no filter chip found for data-t=\"Problem\"" % page)
    else:
        if not o.get("problemGroupHidden"):
            bad.append("%s: filtering to Problem left the Problem group "
                        "hidden" % page)
        if not o.get("otherGroupsHidden"):
            bad.append("%s: filtering to Problem did not hide the other "
                        "groups; show() never ran or ran wrong" % page)
        if o.get("chipPressedAfter") != "true":
            bad.append("%s: the clicked chip never gained aria-pressed=true"
                        % page)
        if not o.get("allGroupsVisibleAfterReset"):
            bad.append("%s: clicking the All chip after filtering did not "
                        "unhide every group" % page)


CHECKERS = {
    "kitchen-deck.html": _check_kitchen_deck,
    "deck-gallery.html": _check_deck_gallery,
}


def main() -> int:
    bad = []
    unverified = False
    for idx, (page, probe) in enumerate(PAGES):
        o = _run_probe(idx, page, probe)
        if o.get("skip"):
            print("  no browser here, cannot drive %s. NOT VERIFIED." % page)
            unverified = True
            continue
        if o.get("error"):
            bad.append("%s: %s" % (page, o["error"]))
            continue
        _check_common(page, o, bad)
        CHECKERS[page](o, bad)

    if bad:
        print("  %d problem(s) found:" % len(bad))
        for b in bad:
            print("    - %s" % b)
        return 1
    if unverified:
        return 0
    print("  %d page(s) driven: nav toggle, card flip/details and filter "
          "chips all behave as their own markup and script say they should"
          % len(PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
