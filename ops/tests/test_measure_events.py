"""Drive site/assets/js/measure.js in a real browser and read what it sends.

WHY THIS EXISTS
---------------
On 2026-09-03, scroll-depth had fired eleven times in the database and nobody
could say what the bucket values were, so EXP-002 sat marked "blocked" for a
fortnight. The instrumentation turned out to be fine and the query was wrong,
but the reason that took a fortnight to find is that nothing had ever asserted
what measure.js actually emits. The only evidence was the code, and reading the
code is exactly the thing CLAUDE.md section 0.3 says is not proof.

Two defects this file would have caught the day they shipped:

  1. buy-click carried a hand-typed table of four Stripe payment link ids. The
     site has 155 and Stripe reissues them, so seven of the nine buy-clicks
     ever recorded came back `sku: "unknown"`.
  2. scroll-depth fired only when the reader had scrolled at all, so a visitor
     who landed and left emitted nothing, and "did not scroll" was stored
     identically to "we lost the event". EXP-002 wants a share, and a share
     needs a denominator that version could not supply.

WHAT IT CHECKS
--------------
Real Chromium, real page loads, a stubbed umami that records instead of sending.
Four pages, because the interesting cases are per page load:

  A  a long page, scrolled to the bottom, plus both buy button shapes
  B  a long page nobody scrolled: must still emit, at 0-14
  C  a section index (/articles/): must emit nothing, it is not an article
  D  a page shorter than the viewport: seen in full without scrolling, 90-100
  E  ?6s-internal=1 stamps who:"internal", and =0 clears it again

E matters because it is the only thing that will ever let EXP-001 tell our own
buy-clicks from a stranger's. A marker that silently stopped working would
leave every future click as ambiguous as the nine already recorded, and would
look exactly like a site whose owner never clicks anything.

Served over http rather than file://, because page() reads location.pathname
and the whole point is which path the page thinks it is at.
"""
import functools
import http.server
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import browser as B                                           # noqa: E402

HEAD = """<!doctype html><html><head><meta charset="utf-8"><title>probe</title>
<script>
window.__ev = [];
window.umami = { track: function (n, d) { window.__ev.push({ n: n, d: d }); } };
%(pretend)s
</script>
<script src="/assets/js/measure.js"></script>
</head><body>
"""

TAIL = """
<script>
/* Registered after measure.js, so measure.js sees the click first and this
   only stops the browser from actually leaving for Stripe. */
document.addEventListener("click", function (e) { e.preventDefault(); }, true);
function finish() { document.title = "M>>" + JSON.stringify(window.__ev) + "<<E"; }
%(body)s
</script></body></html>"""


def probe(name, pretend, markup, script):
    return ((HEAD % {"pretend": pretend}) + markup
            + (TAIL % {"body": script}))


TALL = '<div style="height:6000px">tall</div>'
BUYS = (
    '<a id="plain" href="https://buy.stripe.com/bJeeV623kcky0Jk4NO0kF0S">a</a>'
    '<a id="declared" href="https://buy.stripe.com/00wdR223kfwK9fQ9440kF28"'
    ' data-sku="PACK-HOUSE">b</a>'
)

# A: long page, both buy shapes, scrolled to the bottom, then two exit signals
# to prove the once-only guard holds.
PROBE_A = probe(
    "a", "", TALL + BUYS, """
document.getElementById("plain").click();
document.getElementById("declared").click();
window.scrollTo(0, document.documentElement.scrollHeight);
window.dispatchEvent(new Event("scroll"));
setTimeout(function () {
  window.dispatchEvent(new Event("pagehide"));
  document.dispatchEvent(new Event("visibilitychange"));
  window.dispatchEvent(new Event("pagehide"));
  setTimeout(finish, 120);
}, 150);
""")

# B: the case v1 could not record at all.
PROBE_B = probe("b", "", TALL, """
setTimeout(function () {
  window.dispatchEvent(new Event("pagehide"));
  setTimeout(finish, 120);
}, 150);
""")

# C: /articles/ is the index of the articles, not an article. replaceState runs
# before measure.js loads, so page() sees the path we are testing.
PROBE_C = probe("c", 'history.replaceState(null, "", "/articles/");',
                TALL, """
setTimeout(function () {
  window.dispatchEvent(new Event("pagehide"));
  setTimeout(finish, 120);
}, 150);
""")

# D: nothing to scroll. Reporting 0 here would libel the reader.
PROBE_D = probe("d", "", '<p>short</p>', """
setTimeout(function () {
  window.dispatchEvent(new Event("pagehide"));
  setTimeout(finish, 120);
}, 150);
""")

# E: the internal-traffic marker, driven through one page three times: set it,
# see it persist without the query string, then clear it.
PROBE_E = probe("e", "", TALL + BUYS, """
document.getElementById("plain").click();
setTimeout(function () {
  window.dispatchEvent(new Event("pagehide"));
  setTimeout(finish, 120);
}, 150);
""")

PROBES = {
    "zones/_measure_probe_a.html": PROBE_A,
    "zones/_measure_probe_b.html": PROBE_B,
    "zones/_measure_probe_c.html": PROBE_C,
    "zones/_measure_probe_d.html": PROBE_D,
    "zones/_measure_probe_e.html": PROBE_E,
}


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=directory)
    handler.log_message = lambda *a, **k: None
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def run(edge, extra, url, profile):
    r = subprocess.run(
        [edge] + extra +
        ["--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--user-data-dir=" + profile,
         "--window-size=520,800", "--virtual-time-budget=8000",
         "--dump-dom", url],
        capture_output=True, timeout=120)
    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"M(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        return None
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        return json.loads(raw)
    except ValueError:
        return None


def main() -> int:
    found = B.find_browser()
    if not found:
        # Section 0.4: a run that could not look says so rather than passing.
        print("  no browser here, so measure.js was NOT exercised. UNCHECKED.")
        return 0
    edge, extra = found

    written = []
    srv = None
    profile = tempfile.mkdtemp(prefix="6s-measure-profile-")
    try:
        for rel, html in PROBES.items():
            p = os.path.join(SITE, rel.replace("/", os.sep))
            io.open(p, "w", encoding="utf-8", newline="").write(html)
            written.append(p)
        srv, port = serve(SITE)

        got = {}
        for rel in PROBES:
            got[rel] = run(edge, extra, "http://127.0.0.1:%d/%s" % (port, rel),
                           profile)
        # The marker lives in localStorage, so these three loads must share one
        # browser profile and must run in this order.
        e_url = "http://127.0.0.1:%d/zones/_measure_probe_e.html" % port
        marker = tempfile.mkdtemp(prefix="6s-measure-marker-")
        try:
            got["E:set"] = run(edge, extra, e_url + "?6s-internal=1", marker)
            got["E:persists"] = run(edge, extra, e_url, marker)
            got["E:cleared"] = run(edge, extra, e_url + "?6s-internal=0", marker)
        finally:
            shutil.rmtree(marker, ignore_errors=True)
    finally:
        if srv:
            srv.shutdown()
        for p in written:
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(profile, ignore_errors=True)

    bad = []
    for rel, evs in got.items():
        if evs is None:
            bad.append("%s: the probe never reported, so nothing about it was "
                       "checked. This is unchecked, not passing." % rel)
    if bad:
        for b in bad:
            print("  FAIL " + b)
        return 1

    def only(rel, name):
        return [e for e in got[rel] if e["n"] == name]

    # ---- A: buy-click carries the link id, and the SKU only when declared.
    buys = only("zones/_measure_probe_a.html", "buy-click")
    if len(buys) != 2:
        bad.append("clicking two payment links produced %d buy-click events, "
                   "expected 2" % len(buys))
    else:
        plain, declared = buys[0]["d"], buys[1]["d"]
        if plain.get("plink") != "bJeeV623kcky0Jk4NO0kF0S":
            bad.append("buy-click did not carry the payment link id, it sent "
                       "plink=%r. Without it a click cannot be traced to a "
                       "product at all." % plain.get("plink"))
        if "sku" in plain:
            bad.append("buy-click invented sku=%r for a link whose page never "
                       "declared one. A guessed SKU reads as a measurement."
                       % plain.get("sku"))
        if declared.get("sku") != "PACK-HOUSE":
            bad.append("buy-click dropped the data-sku the page did declare, "
                       "sent %r" % declared.get("sku"))
        if plain.get("from") != "zone":
            bad.append("buy-click on a /zones/ page reported from=%r, not zone"
                       % plain.get("from"))

    # ---- A: exactly one scroll-depth per page view, however it exits.
    a = only("zones/_measure_probe_a.html", "scroll-depth")
    if len(a) != 1:
        bad.append("a page that fired pagehide, visibilitychange and pagehide "
                   "again emitted %d scroll-depth events, expected exactly 1. "
                   "Duplicates would inflate the denominator EXP-002 needs."
                   % len(a))
    elif a[0]["d"].get("depth") != "90-100":
        bad.append("scrolled to the very bottom and reported depth=%r"
                   % a[0]["d"].get("depth"))
    elif a[0]["d"].get("type") != "zone" or a[0]["d"].get("sv") != 2:
        bad.append("scroll-depth payload is %r, expected type=zone and sv=2"
                   % a[0]["d"])

    # ---- B: the denominator case. v1 sent nothing here.
    b = only("zones/_measure_probe_b.html", "scroll-depth")
    if len(b) != 1:
        bad.append("a long page nobody scrolled emitted %d scroll-depth "
                   "events, expected 1. Without it, 'did not scroll' is "
                   "stored identically to 'the event was lost'." % len(b))
    elif b[0]["d"].get("depth") != "0-14":
        bad.append("an unscrolled long page reported depth=%r, expected 0-14"
                   % b[0]["d"].get("depth"))

    # ---- C: a section index is not a page of that section.
    c = only("zones/_measure_probe_c.html", "scroll-depth")
    if c:
        bad.append("/articles/ (the index) emitted scroll-depth %r. It is not "
                   "an article and counting it corrupts the article share."
                   % c[0]["d"])

    # ---- D: seen in full without scrolling.
    d = only("zones/_measure_probe_d.html", "scroll-depth")
    if len(d) != 1:
        bad.append("a page shorter than the viewport emitted %d scroll-depth "
                   "events, expected 1" % len(d))
    elif d[0]["d"].get("depth") != "90-100":
        bad.append("a page with nothing to scroll reported depth=%r; the "
                   "reader saw all of it" % d[0]["d"].get("depth"))

    # ---- E: the internal marker, which is what makes EXP-001 answerable.
    def who(key):
        evs = got[key] or []
        return sorted({(e.get("d") or {}).get("who", "(absent)") for e in evs})

    if not (got["E:set"] and who("E:set") == ["internal"]):
        bad.append('?6s-internal=1 did not stamp who="internal" on everything '
                   "it sent, it sent %s. Without this every future buy-click "
                   "is as unattributable as the nine already recorded."
                   % who("E:set"))
    if not (got["E:persists"] and who("E:persists") == ["internal"]):
        bad.append("the internal marker did not survive a load without the "
                   "query string, it sent %s. It has to stick, or it only "
                   "labels the one page we happened to open."
                   % who("E:persists"))
    if not (got["E:cleared"] and who("E:cleared") == ["(absent)"]):
        bad.append("?6s-internal=0 did not clear the marker, still sending %s. "
                   "A marker that cannot be turned off would label a real "
                   "visitor's browser as ours forever." % who("E:cleared"))

    # ---- Nothing personal, ever.
    for rel, evs in got.items():
        for e in evs:
            for k, v in (e.get("d") or {}).items():
                if isinstance(v, str) and ("@" in v or len(v) > 64):
                    bad.append("%s sent %s=%r, which is too long or looks like "
                               "an address" % (rel, k, v))

    for x in bad:
        print("  FAIL " + x)
    if bad:
        print("  observed: %s" % json.dumps(got)[:900])
        return 1

    print("  ok  buy-click carries plink=%s (sku only when the page declares "
          "it), and scroll-depth fires exactly once per page view: bottom "
          "90-100, unscrolled 0-14, short page 90-100, section index silent. "
          "?6s-internal=1 stamps who=internal, it persists, =0 clears it."
          % buys[0]["d"]["plink"][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
