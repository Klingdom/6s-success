"""Load real pages in a real browser and prove site.js's shared init code
actually runs, instead of trusting that it does.

Found live 2026-09-23: `site.js`'s single `DOMContentLoaded` listener called
`paint();` as its second statement, a leftover from the cart, which was
removed entirely on 2026-09-08 (commit f2e7ba72) along with the `paint()`
function itself. The call was never deleted. Every real page load since has
thrown `Uncaught ReferenceError: paint is not defined` inside that listener,
which aborted the rest of the function before it reached the mobile
`.nav-toggle` click wiring or the `.reveal` `IntersectionObserver`/fallback
setup a few lines later.

Consequence, confirmed directly, not inferred: the hamburger menu on every
page did nothing when tapped (`aria-expanded` never changed, `.nav` never
opened), and on the 10 pages using `.reveal` for scroll-in animation
(`index.html`, `shop.html`, `book.html`, `consulting.html` among them),
`.js .reveal{opacity:0}` never got the `.in` class that would ever set it
back to visible, because the code that adds `.in` never ran. A visitor with
JavaScript enabled and no reduced-motion preference (the overwhelming
majority) could not open the mobile nav and, on those 10 pages, would never
see any `.reveal`-marked content below the belt-and-suspenders' initial
viewport check.

No prior check caught this because none of them load a page and watch for a
thrown error: `audit_visual.py`'s screenshots are taken with
prefers-reduced-motion emulated for determinism, which independently forces
`.reveal` to opacity:1 via its own media-query override and so never
observes the JS crash underneath it; the static gates read HTML text, not
runtime behaviour.

This test does what none of those do: load a real page, actually click the
nav toggle, and fail loudly if the DOM does not respond or if `window.onerror`
ever fired. Driven the same way the shop/contact/corporate/intro-call
interactive tests already drive their own pages: an iframe at a real
viewport width, headless Chromium, --dump-dom against a virtual-time-budget,
JSON handed back through document.title. No network egress is needed or
used.
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

# One page that carries .reveal (the homepage, the single highest-value page
# a stranger meets) and one that does not (a zone page, chosen for its own
# real mobile kit/CTA links), so a regression anywhere in the shared
# listener is caught regardless of which symptom a given page would show.
# 404.html added 2026-09-23: every mistyped or dead link on the whole site
# lands here, and it was one of five pages found the same day shipping a
# .nav-toggle button with no assets/js/site.js reference at all (see
# gate_nav_toggle_wired in ops/preflight.py). That gate proves the script
# tag is present; this test proves the click it enables actually works.
# resources.html and all 20 room hub pages added 2026-09-23, the last
# unexercised part of the standing headless-Chromium handoff: checked
# clean (each carries its own site.js reference already, unlike the
# deck-gallery pages that same day), and planting the exact dropped-script
# defect on resources.html made this test fail by name before it was
# restored, so the coverage is real, not assumed.
#
# book.html, bundle.html, consulting.html, method.html, invest.html,
# about.html, shop.html and corporate.html added 2026-09-24, closing the
# gap the 2026-09-23 paint()-crash postmortem itself left open: these are
# the 9 pages that carry `.reveal` (`grep -rl 'class="[^"]*reveal'
# site/*.html`), the exact defect class that crash broke sitewide, and
# only index.html of the 9 was exercised by this test. shop.html and
# corporate.html already had their own separate interactive tests
# (test_shop_interactive.py, test_corporate_interactive.py) but neither
# asserts window.onerror, so a page-specific JS regression on any of
# these 8 could still ship with every existing gate green.
PAGES = ("index.html", "zones/entryway-the-landing-spot.html", "404.html",
         "resources.html",
         "rooms/dining-room.html", "rooms/entryway.html",
         "rooms/family-room.html", "rooms/garage.html",
         "rooms/guest-bathroom.html", "rooms/guest-bedroom.html",
         "rooms/hall-closet.html", "rooms/home-office.html",
         "rooms/kids-bedroom.html", "rooms/kitchen.html",
         "rooms/laundry-room.html", "rooms/living-room.html",
         "rooms/mudroom.html", "rooms/nursery.html", "rooms/pantry.html",
         "rooms/patio-or-deck.html", "rooms/primary-bathroom.html",
         "rooms/primary-bedroom.html", "rooms/stair-landing.html",
         "rooms/workshop.html",
         "book.html", "bundle.html", "consulting.html", "method.html",
         "invest.html", "about.html", "shop.html", "corporate.html")

# invest.html is a deliberately separate design (its own minimal header and
# footer for an investor audience, confirmed against ops/preflight.py's own
# no_footer_by_design set and its "invest.html has its own minimal legal
# footer" comment): a single anchor-link <nav>, no hamburger toggle, no
# assets/js/site.js dependency at all (it wires its own inline reveal
# script). Every other page in PAGES carries a real .nav-toggle, checked
# directly before adding this exception rather than assumed.
NO_NAV_TOGGLE_BY_DESIGN = {"invest.html"}

ERROR_HOOK = (
    '<script>window.__errs=[];window.onerror=function(m,s,l,c,e){'
    'window.__errs.push(String(m)+" @ "+l+":"+c);};</script>'
)

WRAPPER_TMPL = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:1100px;height:2600px;border:0}</style>
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
    var before = tog ? tog.getAttribute("aria-expanded") : null;
    if (tog) tog.click();
    var after = tog ? tog.getAttribute("aria-expanded") : null;
    out.navBefore = before;
    out.navAfter = after;
    out.navToggleChangedAria = (tog != null) && (before !== after);
    var navEl = d.querySelector(".nav");
    out.navToggleOpenedClass = !!(navEl && navEl.classList.contains("open"));
    out.errs = w.__errs || [];
    /* Only the "already within the first screen at load" fallback
       (site.js's own belt-and-suspenders getBoundingClientRect check,
       200ms after DOMContentLoaded) can be verified here: scroll-triggered
       IntersectionObserver reveal was tried (window.scrollTo, then
       el.scrollIntoView on each element directly, each followed by a
       further wait) and confirmed NOT to fire under headless --dump-dom
       with --virtual-time-budget, on this page and independently on a
       non-iframed direct load of the same file, real browsers do not
       share this limitation. So this only counts .reveal elements whose
       own getBoundingClientRect places them in the loaded viewport,
       exactly the population the belt-and-suspenders fallback promises
       to catch; content further down the page is real, correct,
       scroll-to-reveal behaviour this harness cannot observe, not a
       claim that it works. */
    var vh = w.innerHeight || d.documentElement.clientHeight;
    var top = 0, topIn = 0;
    d.querySelectorAll(".reveal").forEach(function(el){
      var r = el.getBoundingClientRect();
      if (r.top < vh * 0.92 && r.bottom > 0) { top++; if (el.classList.contains("in")) topIn++; }
    });
    out.revealTopCount = top;
    out.revealTopInCount = topIn;
    done();
  }, 900);
});
</script></body></html>"""


def _run_probe(idx: int, page_rel: str):
    """Inject the error hook into a copy of `page_rel`, drive it in an
    iframe, return the parsed probe JSON or an error dict. Never raises."""
    src_path = os.path.join(SITE, page_rel)
    html = io.open(src_path, encoding="utf-8").read()
    if "<head>" not in html:
        return {"error": "no <head> tag in %s to inject the hook into" % page_rel}
    probed = html.replace("<head>", "<head>" + ERROR_HOOK, 1)

    # The probe copy must live next to the original (not at the site root),
    # or every page-relative asset href ("../assets/js/site.js") resolves
    # one directory too high and silently 404s, which would make the nav
    # toggle look broken for the wrong reason: the asset never loading, not
    # the runtime error this test exists to catch.
    probe_dir = os.path.dirname(src_path)
    probe_name = "_site_js_probe_%d.html" % idx
    probe_path = os.path.join(probe_dir, probe_name)
    probe_rel = os.path.relpath(probe_path, SITE).replace(os.sep, "/")
    wrap_name = "_site_js_wrapper_%d.html" % idx
    wrap_path = os.path.join(SITE, wrap_name)

    found = B.find_browser()
    if not found:
        return {"skip": "no browser here"}
    exe, extra = found

    io.open(probe_path, "w", encoding="utf-8", newline="").write(probed)
    io.open(wrap_path, "w", encoding="utf-8", newline="").write(
        WRAPPER_TMPL % {"probe_rel": probe_rel})

    profile = tempfile.mkdtemp(prefix="6s-sitejs-probe-")
    try:
        r = subprocess.run(
            [exe] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=1140,2700", "--virtual-time-budget=8000",
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


def main() -> int:
    bad = []
    unverified = False
    for idx, page in enumerate(PAGES):
        o = _run_probe(idx, page)
        if o.get("skip"):
            print("  no browser here, cannot drive %s. NOT VERIFIED." % page)
            unverified = True
            continue
        if o.get("error"):
            bad.append("%s: %s" % (page, o["error"]))
            continue
        if o.get("errs"):
            bad.append("%s: JavaScript threw during load: %s"
                        % (page, o["errs"]))
        if not o.get("hasNavToggle"):
            if page not in NO_NAV_TOGGLE_BY_DESIGN:
                bad.append("%s: no .nav-toggle button found" % page)
        elif not o.get("navToggleChangedAria"):
            bad.append(
                "%s: clicking .nav-toggle did not change aria-expanded "
                "(before=%r after=%r); the click handler in site.js's "
                "DOMContentLoaded listener never ran"
                % (page, o.get("navBefore"), o.get("navAfter")))
        elif not o.get("navToggleOpenedClass"):
            bad.append("%s: .nav-toggle changed aria-expanded but .nav "
                        "never gained the open class" % page)
        rc, ric = o.get("revealTopCount", 0), o.get("revealTopInCount", 0)
        if rc and not ric:
            bad.append(
                "%s: %d .reveal element(s) in the loaded viewport, 0 carry "
                ".in; the belt-and-suspenders initial-viewport reveal never "
                "ran, so this page's first-screen content stays invisible "
                "to a visitor with motion enabled" % (page, rc))

    if bad:
        print("  %d problem(s) found:" % len(bad))
        for b in bad:
            print("    - %s" % b)
        return 1
    if unverified:
        return 0
    print("  %d page(s) driven, no JS error, .nav-toggle works, "
          "any .reveal content on the first screen is visible"
          % len(PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
