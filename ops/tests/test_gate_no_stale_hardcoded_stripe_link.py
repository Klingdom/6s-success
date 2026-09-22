#!/usr/bin/env python3
"""
Prove ops/preflight.py's stale_hardcoded_stripe_links()/
gate_no_stale_hardcoded_stripe_link() catch a buy.stripe.com link written
into a page or a .js file that no longer matches any current entry in
data.js's own catalogue, and that the real, committed site is clean today.

Found 2026-09-22 while tracing one real customer journey end to end (a zone
page's consult and print-pack buttons through data.js to the Stripe URL,
then through measure.js's click handler): no live defect, but a real,
credential-free gap. quest.js hardcodes the print pack's own href and SKU
as a literal object, rather than reading data.js at render time, the same
shape as the four hand-typed payment-link ids measure.js used to carry
before one of them went stale mid price-rotation and silently miscounted
seven of nine buy-clicks. Nothing before this gate checked a hardcoded
JS link against the live catalogue without a Stripe credential.

Run:  python ops/tests/test_gate_no_stale_hardcoded_stripe_link.py
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

LIVE = {"https://buy.stripe.com/00wdR223kfwK9fQ9440kF28",
        "https://buy.stripe.com/5kQaEQ9vMacq63E2FG0kF2a"}

STALE_HTML = ('<a class="btn" href="https://buy.stripe.com/DEADLINKDEADLINK">'
              'Buy, $19</a>\n')
STALE_JS = ('var CTA = {href: "https://buy.stripe.com/DEADLINKDEADLINK", '
            'sku: "PACK-HOUSE"};\n')
GOOD_HTML = ('<a class="btn" href="https://buy.stripe.com/00wdR223kfwK9fQ9'
             '440kF28">Buy, $19</a>\n')
NO_LINK = "Nothing but ordinary prose about the print pack here.\n"

passed = failed = 0


def check(name, got, want_empty):
    global passed, failed
    ok = (len(got) == 0) if want_empty else (len(got) > 0)
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want_empty={want_empty}")


# 1. A stale link in an HTML anchor must be caught.
check("stale link in HTML",
      preflight.stale_hardcoded_stripe_links({"x.html": STALE_HTML}, LIVE),
      False)

# 2. A stale link hardcoded inside a JS object literal (quest.js's own
#    shape, not an <a> tag at all) must be caught too.
check("stale link in JS object literal",
      preflight.stale_hardcoded_stripe_links({"x.js": STALE_JS}, LIVE),
      False)

# 3. The real, live link must not be flagged.
check("live link, clean",
      preflight.stale_hardcoded_stripe_links({"x.html": GOOD_HTML}, LIVE),
      True)

# 4. No link at all: nothing to check, not a failure.
check("no link, nothing to check",
      preflight.stale_hardcoded_stripe_links({"x.html": NO_LINK}, LIVE),
      True)

# 5. The real, committed site must be clean today.
data_js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                   encoding="utf-8").read()
catalog = json.loads(data_js[data_js.index("["):data_js.rindex("]") + 1])
real_live_buys = {i["buy"] for i in catalog if i.get("buy")}

real_files = {}
for f in preflight.all_pages():
    real_files[f] = io.open(f, encoding="utf-8", errors="replace").read()
for f in glob.glob(os.path.join(SITE, "assets", "js", "*.js")):
    real_files[f] = io.open(f, encoding="utf-8", errors="replace").read()

check("real committed site, no stale hardcoded link",
      preflight.stale_hardcoded_stripe_links(real_files, real_live_buys),
      True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
