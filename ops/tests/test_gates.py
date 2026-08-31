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

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  5 gates fire on a planted fault and stay quiet without "
              "it, and stale-claims counts visitor copy only")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
