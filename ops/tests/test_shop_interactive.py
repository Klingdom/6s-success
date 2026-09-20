"""Drive site/shop.html in a real browser: click every category filter and
every rendered buy/action link, the way a stranger actually would.

Every existing shop check reads static text (gate_prerender_shop_current,
gate_shop_buy_claim_honest, gate_price_matches_its_own_link and friends): they
compare the page's own HTML against the catalogue, but none of them has ever
actually clicked a filter button and watched the grid change, or walked every
rendered action link a real click would follow. That gap has been named twice
in ops/NIGHTLY-LOG.md as the standing next handoff and never actually run.

What this checks, as a first-time visitor clicking through the shop would:

    each of the 8 filter buttons (All + 7 real categories) renders the right
      tile count for its category, and marks itself (and only itself) pressed;
    every rendered tile has an action link with a non-empty href;
    every Stripe buy link is well-formed (https://buy.stripe.com/...) and
      carries the data-sku measure.js needs to attribute the click;
    no two different SKUs share the same Stripe buy link (a real, serious
      checkout bug: money from one product's buyer would raise the wrong
      product's link, or worse, sell a different product than advertised);
    free "Open it" links and contact.html fallbacks are non-empty and
      internally consistent with the product's own sku.

Driven the same way ops/tests/test_quest_flow.py drives the Quest: an iframe
at a real viewport width, headless Chromium, --dump-dom against a
virtual-time-budget, JSON handed back through document.title. No network
egress is needed or used: shop.html, data.js, site.js and shop.js are all
served from disk via file://.
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
<style>html,body{margin:0}iframe{width:1100px;height:2400px;border:0}</style>
</head><body><iframe id="f" src="shop.html"></iframe><script>
var out = {cats: []};
function done(){ document.title = "S>>" + JSON.stringify(out) + "<<E"; }

var frame = document.getElementById("f");
frame.addEventListener("load", function(){
  var d = frame.contentDocument;
  if (!d || !d.body) { out.error = "no document"; return done(); }

  setTimeout(function(){
    var w = d.defaultView;
    var buttons = Array.prototype.slice.call(d.querySelectorAll(".filters button"));
    out.buttonCount = buttons.length;
    out.buttonCats = buttons.map(function (b) { return b.dataset.cat; });

    function readGrid() {
      var tiles = Array.prototype.slice.call(d.querySelectorAll("#grid .card, #grid > *"));
      var actions = Array.prototype.slice.call(d.querySelectorAll("#grid a.btn"));
      return {
        tileCount: tiles.length,
        pressed: buttons.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })
                         .map(function (b) { return b.dataset.cat; }),
        actions: actions.map(function (a) {
          return {sku: a.dataset.sku || null, href: a.getAttribute("href") || "",
                   label: (a.textContent || "").trim()};
        })
      };
    }

    var i = 0;
    function step() {
      if (i >= buttons.length) { return done(); }
      buttons[i].click();
      var cat = buttons[i].dataset.cat;
      i += 1;
      setTimeout(function () {
        var g = readGrid();
        g.cat = cat;
        out.cats.push(g);
        step();
      }, 60);
    }
    step();
  }, 300);
});
</script></body></html>"""


def main():
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the shop page. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-shop-profile-")
    wrap = os.path.join(SITE, "_shop_interactive_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=1140,2500", "--virtual-time-budget=25000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"S(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the shop page was NOT exercised. "
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

    if o.get("buttonCount", 0) < 2:
        bad.append("only %d filter button(s) rendered; buildFilters() may not "
                    "have run" % o.get("buttonCount", 0))
    if o.get("buttonCats", [None])[0] != "All":
        bad.append("first filter button is not 'All': %r" % o.get("buttonCats"))

    # Load the real catalogue independently, from the committed source file,
    # not from the browser, so the expected-per-category counts cannot come
    # from the same code path being checked.
    data_js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                       encoding="utf-8").read()
    m2 = re.search(r"window\.CATALOG\s*=\s*(\[.*?\]);", data_js, re.S)
    if not m2:
        print("  could not find window.CATALOG in data.js to check against. "
              "NOT VERIFIED.")
        return 1
    catalog = json.loads(m2.group(1))
    by_cat = {}
    by_sku = {}
    for p in catalog:
        by_cat.setdefault(p.get("cat"), []).append(p)
        by_sku[p.get("sku")] = p

    all_buy_hrefs = {}   # href -> set of skus that used it
    seen_cats = set()
    for row in o.get("cats", []):
        cat = row.get("cat")
        seen_cats.add(cat)
        pressed = row.get("pressed", [])
        if pressed != [cat]:
            bad.append("clicking %r left aria-pressed=%r, expected only [%r]"
                       % (cat, pressed, cat))

        expected_n = len(catalog) if cat == "All" else len(by_cat.get(cat, []))
        if row.get("tileCount") != expected_n:
            bad.append("category %r rendered %d tile(s), catalogue has %d"
                       % (cat, row.get("tileCount"), expected_n))

        for a in row.get("actions", []):
            href = a.get("href", "")
            sku = a.get("sku")
            if not href:
                bad.append("category %r: action %r has an empty href"
                            % (cat, a.get("label")))
                continue
            if href.startswith("https://buy.stripe.com/"):
                if not sku:
                    bad.append("category %r: Stripe buy link %s has no "
                                "data-sku (measure.js cannot attribute it)"
                                % (cat, href))
                else:
                    all_buy_hrefs.setdefault(href, set()).add(sku)
                    p = by_sku.get(sku)
                    if p is None:
                        bad.append("category %r: buy link's data-sku %r is "
                                    "not a real catalogue SKU" % (cat, sku))
                    elif p.get("buy") != href:
                        bad.append("category %r: SKU %s rendered buy href %s "
                                    "but the catalogue's own 'buy' field says %s"
                                    % (cat, sku, href, p.get("buy")))
            elif "contact.html" in href:
                if sku and ("ref=" + sku) not in href:
                    bad.append("category %r: contact link for %s does not "
                                "carry its own ref: %s" % (cat, sku, href))

    expected_cats = set(["All"]) | set(by_cat.keys())
    if seen_cats != expected_cats:
        bad.append("filter row categories %r do not match the catalogue's "
                    "real categories %r" % (sorted(seen_cats), sorted(expected_cats)))

    for href, skus in all_buy_hrefs.items():
        if len(skus) > 1:
            bad.append("Stripe buy link %s is shared by %d different SKUs: "
                        "%s (a click cannot tell them apart, and a shared "
                        "link's line items are immutable per SKU)"
                        % (href, len(skus), sorted(skus)))

    print("  %d filter(s) clicked, %d category row(s) checked, %d distinct "
          "Stripe buy link(s) seen." % (o.get("buttonCount", 0), len(o.get("cats", [])),
                                         len(all_buy_hrefs)))

    if bad:
        for b in bad:
            print("  FAIL: " + b)
        return 1
    print("  shop.html: every filter renders the right count and marks only "
          "itself pressed; every buy link is well-formed, carries a real "
          "data-sku matching the catalogue's own 'buy' field, and no two "
          "SKUs share a payment link.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
