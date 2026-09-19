#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_zone_kit_disclosure_grammar() catches the
old subject-verb-disagreement sentence in a zone page's optional kit
list, and does not false-positive on the fixed wording.

Found 2026-09-19, the narrative-level cold read of site/zones/*.html.
ops/zone_supplies.py built "Only if your {noun} has one" / "Not every
{noun} needs these" for the collapsed part of the kit list; correct only
when {noun} is singular. Several real nouns in ops/zone-search-terms.json
are plural or a plural compound ("towels", "dresser drawers", "bed and
linens"), so the real, live guest-bathroom-the-guest-linen-zone page
shipped "Only if your towels has one" and "Not every towels needs
these". Fixed in zone_supplies.py to "Only if it applies to the {noun}"
/ "Not every home needs these for the {noun}", which puts the noun where
no verb has to agree with it.

A first version of this gate's own regex was itself wrong: it flagged
the FIXED text too, because "Not every home needs these" contains
"needs these" and the naive pattern did not exclude the new fixed
noun ("home"). Caught by running this exact test against the real,
already-fixed repository before trusting the gate; kept here as case 3
so that mistake cannot repeat silently.

Run:  python ops/tests/test_gate_zone_kit_disclosure_grammar.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    zone_dir = os.path.join(ROOT, "site", "zones")
    files = sorted(glob.glob(os.path.join(zone_dir, "*.html")))
    if not files:
        print("SKIP: no site/zones/*.html in this checkout")
        return 0

    # 1. The real, committed repository today must be clean (the fix has
    #    already been applied and regenerated).
    preflight.FAIL.clear()
    preflight.gate_zone_kit_disclosure_grammar()
    if preflight.FAIL:
        fails.append("real committed pages wrongly flagged: %s" %
                     preflight.FAIL)

    # 2. Plant the exact real 2026-09-19 regression on one real file, prove
    #    the gate catches it by name, then restore byte for byte.
    target = os.path.join(zone_dir,
                          "guest-bathroom-the-guest-linen-zone.html")
    orig = io.open(target, encoding="utf-8").read()
    if "Only if it applies to the towels: 1 more" not in orig:
        fails.append("fixture file no longer matches this test's "
                     "assumptions; update the planted string")
    else:
        planted = orig.replace(
            "Only if it applies to the towels: 1 more",
            "Only if your towels has one: 1 more"
        ).replace(
            "Not every home needs these for the towels.",
            "Not every towels needs these."
        )
        try:
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(planted)
            preflight.FAIL.clear()
            preflight.gate_zone_kit_disclosure_grammar()
            names = [msg for _, msg in preflight.FAIL]
            if not any("guest-bathroom-the-guest-linen-zone.html" in m
                      for m in names):
                fails.append("planted regression was not caught by name: "
                             "%s" % names)
        finally:
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(orig)
            restored = io.open(target, encoding="utf-8").read()
            if restored != orig:
                fails.append("failed to restore the fixture file exactly")

    # 3. The fixed wording itself must never be flagged (guards against
    #    the exact "needs these" false-positive this gate's own docstring
    #    records finding while building it).
    preflight.FAIL.clear()
    preflight.gate_zone_kit_disclosure_grammar()
    if preflight.FAIL:
        fails.append("fixed wording false-positived after restore: %s" %
                     preflight.FAIL)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: gate_zone_kit_disclosure_grammar catches the real "
         "regression by name and does not false-positive on the fixed "
         "wording, proved directly against the real committed pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
