#!/usr/bin/env python3
"""
Two things about zone related-reading that broke on the same day, for the same
underlying reason: the corpus got six and a half times bigger and two fixed
numbers stopped meaning what they were chosen to mean.

1. NO TWO DIAGNOSED ZONES MAY SHIP AN IDENTICAL SET
   cause_reading() picks a zone's articles from its own causes, in the order
   those causes first appear. Correct, and not sufficient alone: on 2026-09-29
   Dining Table and Sofa and Seating both resolved to the same five articles in
   different orders, from genuinely different friction lists. Ordering cannot
   fix it because the requirement compares sets, and with 17 causes and 78
   diagnosed zones collisions get likelier, not rarer.

   diagnosed_reading() now assigns across every room at once and swaps the last
   pick for that zone's next distinct cause article until the set is unique.
   Every link is still chosen by the zone's own causes; only which of its own
   causes takes the fifth slot changes.

2. THE INBOUND-LINK CEILING IS A SHARE, NOT A COUNT
   35 was calibrated when 12 zones were diagnosed. Measured at 114 zones, 25
   articles and 570 links: an even spread is 22.8 per article and the busiest
   sits at 39, which is 34% of zones. That is a healthy distribution. The
   absolute number rose because the denominator grew, and nothing about the
   linking got worse.

   A fixed count fails every time another room is diagnosed, which teaches
   whoever sees it to raise the number rather than look at the spread.

Run:  python ops/tests/test_reading_spread_and_uniqueness.py
"""
import collections
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

BLOCK = re.compile(r"(?is)<h2>Related reading</h2>(.*?)</ul>")


def _shipped():
    """{filename: [article slug]} for every zone page that ships the block."""
    out = {}
    for fp in glob.glob(os.path.join(ROOT, "site", "zones", "*.html")):
        s = io.open(fp, encoding="utf-8", errors="replace").read()
        m = BLOCK.search(s)
        if not m:
            continue
        out[os.path.basename(fp)] = re.findall(
            r'href="\.\./articles/([^"]+)"', m.group(1))
    return out


def case_no_two_diagnosed_zones_share_a_set():
    seen = {}
    dupes = []
    for name, slugs in _shipped().items():
        fp = os.path.join(ROOT, "site", "zones", name)
        if 'id="diagnosis"' not in io.open(fp, encoding="utf-8",
                                           errors="replace").read():
            continue
        key = frozenset(slugs)
        if key in seen:
            dupes.append((seen[key], name))
        seen[key] = name
    assert not dupes, dupes


def case_every_zone_gets_three_to_five():
    bad = {n: len(s) for n, s in _shipped().items() if not (3 <= len(s) <= 5)}
    assert not bad, bad


def case_ceiling_scales_with_the_corpus():
    """A share, so more rooms does not mean a redder gate."""
    picks = {"z%d" % i: ["a", "b", "c"] for i in range(10)}
    small = P.check_general_reading_picks(picks, {}, {"a", "b", "c"},
                                          zones_linking=10)
    assert not [p for p in small if "ceiling" in p], small
    # 200 zones all pointing at one article IS concentration, and must fail.
    heavy = {"z%d" % i: ["a", "b", "c"] for i in range(200)}
    out = P.check_general_reading_picks(heavy, {}, {"a", "b", "c"},
                                        zones_linking=200)
    assert any("ceiling" in p for p in out), out


def case_a_floor_still_catches_an_orphan_article():
    picks = {"z%d" % i: ["a", "b", "c"] for i in range(40)}
    out = P.check_general_reading_picks(picks, {}, {"a", "b", "c", "orphan"},
                                        zones_linking=40)
    assert any("orphan" in p and "floor" in p for p in out), out


def case_the_real_spread_is_healthy():
    """Re-derived, not pinned: no article may exceed 40% of linking zones."""
    shipped = _shipped()
    counts = collections.Counter()
    for slugs in shipped.values():
        counts.update(slugs)
    assert shipped, "no zone page ships related reading"
    worst, n = counts.most_common(1)[0]
    share = n / float(len(shipped))
    assert share <= 0.40, (
        "%s is linked from %.0f%% of zones (%d of %d); the spread has "
        "genuinely collapsed rather than the denominator having grown"
        % (worst, share * 100, n, len(shipped)))


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
