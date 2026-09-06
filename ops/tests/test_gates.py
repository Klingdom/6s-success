"""Prove the gates in preflight.py actually fire.

The repository is currently clean, so every gate passes, so a working gate and
a gate that can no longer detect anything produce exactly the same output. That
is not a hypothetical: four analysis tools were audited this week and all four
were silently reporting something other than what they had measured, and one
gate in this very file spent a commit unable to parse and another with a regex
matching nothing.

So each gate covered here is asked two questions:

    with a fault planted, does it complain?
    with the fault removed, does it stay quiet?

Only the second is true today, and only the second is what a passing run tells
you. Gates that need the network or a Stripe credential are covered by their
own tests instead: check_live_links, deploy_freshness, check_urls.

Gates are called directly rather than through main(), so this stays fast and
names the gate that failed rather than "preflight failed".
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)

import preflight as P                                         # noqa: E402

SITE = P.SITE

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Temporary gate fixture</title>
<meta name="description" content="Written and deleted by ops/tests/test_gates.py.">
%(head)s
</head><body><main>%(body)s</main></body></html>
"""


class Planted:
    """Write a file, run a gate, and always clean up."""

    def __init__(self, rel: str, text: str):
        self.path = os.path.join(SITE, rel.replace("/", os.sep))
        self.text = text

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        io.open(self.path, "w", encoding="utf-8", newline="").write(self.text)
        return self

    def __exit__(self, *a):
        if os.path.exists(self.path):
            os.remove(self.path)


def fired(gate, name: str) -> bool:
    """Run one gate in isolation and say whether it reported `name`."""
    P.FAIL.clear()
    P.WARN.clear()
    gate()
    return any(g == name for g, _ in P.FAIL + P.WARN)


def main() -> int:
    bad = []

    def case(label, gate, name, rel, text):
        """The gate must fire with the fault present and be quiet without it."""
        with Planted(rel, text):
            if not fired(gate, name):
                bad.append("%s: fault planted in %s and %r did not fire"
                           % (label, rel, name))
        if fired(gate, name):
            bad.append("%s: %r fires on the clean tree, so it cannot "
                       "distinguish a fault" % (label, name))

    # A request to an outside host, on a site whose privacy page promises none.
    case("third-party request", P.gate_third_party, "third-party",
         "_gate_fixture_tp.html",
         PAGE % {"head": '<script src="https://cdn.not-our-domain.test/a.js"></script>',
                 "body": "<h1>Fixture</h1>"})

    # A statistic about people or results with no source. CLAUDE.md section 8
    # rules these out; four once shipped printed on a card deck.
    case("unsourced statistic", P.gate_unsourced_stats, "unsourced-stats",
         "_gate_fixture_stat.html",
         PAGE % {"head": "",
                 "body": "<h1>Fixture</h1><p>On average this saves you 40 hours "
                         "a year in the average household.</p>"})

    # A page that is not one of the six nav destinations but marks a nav link
    # as the current page anyway. This direction matters more than the missing
    # one: the header is not merely silent, it tells a screen reader the
    # visitor is somewhere they are not. A rebuild produced exactly this on 135
    # zone and room pages before ops/wire_aria_current.py was chained, because
    # the generators copy their header from resources.html and resources.html
    # correctly marks itself.
    case("false nav position", P.gate_nav_current, "nav-current",
         "_gate_fixture_nav.html",
         PAGE % {"head": "",
                 "body": '</main><header class="site-header"><nav class="nav">'
                         '<a href="book.html" aria-current="page">Cards and book</a>'
                         '</nav></header><main>'})

    # Copy that goes stale. This one cannot be tested by "does it fire",
    # because it has two legitimate standing hits that are real page copy and
    # still true: the WCAG statement of intent on accessibility.html, and "we
    # have not run a paid reset day yet" on consulting.html. A gate with a
    # correct non-zero baseline needs its count compared, not its silence.
    def stale_count() -> int:
        P.FAIL.clear()
        P.WARN.clear()
        P.gate_stale_claims()
        for g, msg in P.WARN:
            if g == "stale-claims":
                return int(re.match(r"\s*(\d+)", msg).group(1))
        return 0

    base = stale_count()
    with Planted("_gate_fixture_stale.html",
                 PAGE % {"head": "",
                         "body": "<h1>Fixture</h1><p>The full range is coming "
                                 "soon.</p>"}):
        if stale_count() != base + 1:
            bad.append("stale claim: planting one stale phrase should raise the "
                       "count from %d to %d, got %d"
                       % (base, base + 1, stale_count()))

    # And the specific false positive this gate had until 2026-08-31: the same
    # words inside a script are not visitor copy and must not be counted.
    with Planted("_gate_fixture_script.html",
                 PAGE % {"head": "",
                         "body": "<h1>Fixture</h1><script>/* coming soon */"
                                 "</script>"}):
        if stale_count() != base:
            bad.append("stale claim: words inside a <script> are not visitor "
                       "copy and must not be counted, count moved from %d to %d"
                       % (base, stale_count()))

    # The bundle's stated saving must equal its parts minus its price. "Save
    # $17" and "bought separately they are $66" were both true until the ebook
    # moved from $18 to $9.99, at which point they quietly became false and
    # stayed on the page. Both directions matter: a wrong figure must be
    # caught, and the correct figure must be left alone, because a gate that
    # rejects the true number would push someone to write a false one.
    import json as _json
    _js = io.open(os.path.join(SITE, "assets", "js", "data.js"),
                  encoding="utf-8").read()
    _cat = {i["sku"]: i for i in
            _json.loads(_js[_js.index("["):_js.rindex("]") + 1])}
    _parts = ["BK-EB", "MZ-MANUAL", "PACK-HOUSE"]
    if all(k in _cat for k in _parts + ["BK-BUNDLE"]):
        apart = round(sum(_cat[k]["price"] for k in _parts), 2)
        saving = round(apart - _cat["BK-BUNDLE"]["price"], 2)

        case("wrong bundle saving", P.gate_bundle_maths, "bundle-maths",
             "_gate_fixture_bundle.html",
             PAGE % {"head": "",
                     "body": "<h1>Fixture</h1><p>Save $%d today.</p>"
                             % int(saving + 100)})

        # The true figures, written the way the page writes them.
        txt = ("<h1>Fixture</h1><p>Save $%s, separately they are $%s.</p>"
               % (("%.2f" % saving).rstrip("0").rstrip(".") if saving % 1
                  else int(saving),
                  ("%.2f" % apart).rstrip("0").rstrip(".") if apart % 1
                  else int(apart)))
        with Planted("_gate_fixture_bundle_ok.html",
                     PAGE % {"head": "", "body": txt}):
            if fired(P.gate_bundle_maths, "bundle-maths"):
                bad.append("bundle maths: the correct saving and parts total "
                           "were reported as wrong (%r)" % txt)

        # And it must look beyond the seventeen pages sitting directly in
        # site/, which is the glob that has already been found too narrow
        # twice in this repository.
        case("wrong bundle saving in a subdirectory", P.gate_bundle_maths,
             "bundle-maths", "zones/_gate_fixture_bundle_sub.html",
             PAGE % {"head": "",
                     "body": "<h1>Fixture</h1><p>Save $%d today.</p>"
                             % int(saving + 100)})

    # An indexable page absent from sitemap.xml. Phil's kit.html shipped this
    # way: title, description and canonical, and unlisted.
    case("page missing from sitemap", P.gate_sitemap_complete, "sitemap-complete",
         "_gate_fixture_sitemap.html",
         PAGE % {"head": '<link rel="canonical" '
                         'href="https://6s-success.com/_gate_fixture_sitemap.html">',
                 "body": "<h1>Fixture</h1>"})

    # An unresolved merge conflict. This one is not hypothetical: a rebase once
    # committed markers into preflight.py itself, so every gate in the file was
    # dead, in a commit that was adding a gate.
    marker = "<" * 7 + " HEAD"
    case("conflict marker", P.gate_conflict_markers, "conflict-markers",
         "_gate_fixture_conflict.html",
         PAGE % {"head": "", "body": "<h1>Fixture</h1>\n" + marker + "\n"})

    # gate_roadmap_prices_current's page-count check must not false-fail when
    # a stray site/**/_*.html scratch file exists mid-flight (audit_visual.py's
    # own probe, or any sibling test fixture in this file): found 2026-09-06,
    # a real preflight --deep run overlapping a concurrent audit_visual.py
    # call turned a true 191-page count into 192 and this gate reported a
    # false drift against ROADMAP-2026-2029.md. Plant one directly, using the
    # same prefix every other case in this file already relies on, and prove
    # the gate stays quiet.
    with Planted("_gate_fixture_roadmap_pages.html",
                 PAGE % {"head": "", "body": "<h1>Fixture</h1>"}):
        if fired(P.gate_roadmap_prices_current, "roadmap-prices-current"):
            bad.append("roadmap page count: a stray _gate_fixture_roadmap_"
                       "pages.html was counted as a real page")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  7 gates fire on a planted fault and stay quiet without "
              "it; stale-claims counts visitor copy only, bundle-maths "
              "accepts the true figures and looks in subdirectories, and "
              "roadmap-prices-current ignores a stray scratch page")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
