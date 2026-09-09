#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_general_reading_picks() and
check_general_reading_rendered() catch the defect classes PLAN-MICROZONES-
DECKS-APP.md's M5 acceptance names: a zone with fewer than 3 or more than 5
related-reading links, two zones sharing an identical set, an article
falling under the 3-link floor or rising past the documented ceiling, and a
rendered page whose actual related-reading block does not match what the
corpus computes for it (the same class of gap gate_diagnosis_rendered
exists to catch for M4).

Also proves the real, live corpus (if built) passes clean today: general_
reading() re-run fresh against content.json, checked against both the
picks-level and the render-level rule.

Run:  python ops/tests/test_gate_general_reading.py
"""
import collections
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def main() -> int:
    fails = []

    # 1. A clean, well-formed slate passes with no problems.
    good_picks = {
        "z1": ["a", "b", "c"],
        "z2": ["a", "b", "d"],
        "z3": ["a", "c", "d"],
    }
    pool = {"a", "b", "c", "d"}
    problems = preflight.check_general_reading_picks(
        good_picks, collections.Counter(), pool, floor=2, cap_ceiling=10)
    if problems:
        fails.append("clean picks wrongly flagged: %s" % problems)

    # 2. Too few links (under 3).
    bad = dict(good_picks)
    bad["z4"] = ["a", "b"]
    problems = preflight.check_general_reading_picks(
        bad, collections.Counter(), pool, floor=2, cap_ceiling=10)
    if not any("z4" in p and "2 links" in p for p in problems):
        fails.append("under-3 link count not caught: %s" % problems)

    # 3. Too many links (over 5).
    bad = dict(good_picks)
    bad["z5"] = ["a", "b", "c", "d", "a", "b"]  # 6 entries
    problems = preflight.check_general_reading_picks(
        bad, collections.Counter(), pool, floor=2, cap_ceiling=10)
    if not any("z5" in p and "6 links" in p for p in problems):
        fails.append("over-5 link count not caught: %s" % problems)

    # 4. Two zones share an identical set (order-independent).
    bad = dict(good_picks)
    bad["z6"] = ["c", "b", "a"]  # same set as z1, different order
    problems = preflight.check_general_reading_picks(
        bad, collections.Counter(), pool, floor=2, cap_ceiling=10)
    if not any("identical related-reading set" in p for p in problems):
        fails.append("duplicate set not caught: %s" % problems)

    # 5. An article under the floor, counting diagnosed usage too.
    problems = preflight.check_general_reading_picks(
        good_picks, collections.Counter({"d": 0}), pool,
        floor=5, cap_ceiling=10)
    if not any(p.startswith("d:") and "floor" in p for p in problems):
        fails.append("under-floor article not caught: %s" % problems)

    # 6. Diagnosed usage alone can clear the floor without any
    #    non-diagnosed zone linking it.
    problems = preflight.check_general_reading_picks(
        good_picks, collections.Counter({"z-only-diagnosed": 5}),
        {"a", "b", "c", "d", "z-only-diagnosed"}, floor=3, cap_ceiling=10)
    if any(p.startswith("z-only-diagnosed") for p in problems):
        fails.append("diagnosed-only usage wrongly flagged under floor: %s"
                     % problems)

    # 7. An article over the ceiling, diagnosed usage counted in.
    heavy = {"z%d" % i: ["a", "b", "c"] for i in range(10)}
    problems = preflight.check_general_reading_picks(
        heavy, collections.Counter({"a": 5}), {"a", "b", "c"},
        floor=1, cap_ceiling=12)
    if not any(p.startswith("a:") and "ceiling" in p for p in problems):
        fails.append("over-ceiling article not caught: %s" % problems)

    # 8. An article outside `pool` (a ZONE_SPECIFIC_READING-style link that
    #    is meant to sit at exactly 1 inbound link) is never floor-checked.
    problems = preflight.check_general_reading_picks(
        good_picks, collections.Counter({"specific-only": 1}), pool,
        floor=3, cap_ceiling=10)
    if any("specific-only" in p for p in problems):
        fails.append("out-of-pool article wrongly floor-checked: %s"
                     % problems)

    # 9. check_general_reading_rendered: a clean match passes.
    body = ('<h2>Related reading</h2><ul>'
            '<li><a href="../articles/a">A</a></li>'
            '<li><a href="../articles/b.html">B</a></li>'
            '</ul>')
    ok = preflight.check_general_reading_rendered(
        {"z1.html": body},
        {"z1.html": {"../articles/a.html", "../articles/b.html"}})
    if ok:
        fails.append("matching render (with/without .html) wrongly "
                     "flagged: %s" % ok)

    # 10. check_general_reading_rendered: a real mismatch is caught.
    bad_render = preflight.check_general_reading_rendered(
        {"z1.html": body},
        {"z1.html": {"../articles/a.html", "../articles/c.html"}})
    if not bad_render:
        fails.append("render mismatch not caught")

    # 11. check_general_reading_rendered: an unbuilt page is caught, not
    #     silently skipped.
    missing = preflight.check_general_reading_rendered(
        {}, {"z1.html": {"../articles/a.html"}})
    if not missing:
        fails.append("missing page not caught")

    # 12. The real, live site (if built) passes clean today.
    src = os.path.join(ROOT, "content", "manual", "source", "content.json")
    if os.path.exists(src):
        rooms = json.load(io.open(src, encoding="utf-8"))["rooms"]
        real_pages = {}
        for f in sorted(glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))):
            real_pages[os.path.basename(f)] = io.open(
                f, encoding="utf-8", errors="replace").read()
        if real_pages:
            import build_zone_pages as bzp                        # noqa: E402
            picks_raw = bzp.general_reading(rooms)
            real_picks = {k: [e[0].rsplit("/", 1)[-1][:-len(".html")]
                              for e in v] for k, v in picks_raw.items()}
            diagnosed_usage = bzp._diagnosed_article_usage(rooms)
            real_pool = set(bzp._ARTICLE_BY_SLUG.keys())
            problems = preflight.check_general_reading_picks(
                real_picks, diagnosed_usage, real_pool)
            if problems:
                fails.append("real, built corpus wrongly flagged at the "
                             "picks level: %s" % problems[:3])

            expected = {}
            for key, links in picks_raw.items():
                specific = bzp.ZONE_SPECIFIC_READING.get(key, [])
                specific_hrefs = {e[0] for e in specific}
                combined = (specific + [e for e in links
                                        if e[0] not in specific_hrefs])[:5]
                expected[key + ".html"] = {e[0] for e in combined}
            render_problems = preflight.check_general_reading_rendered(
                real_pages, expected)
            if render_problems:
                fails.append("real, built site wrongly flagged at render "
                             "level: %s" % render_problems[:3])
        else:
            print("  note: site/zones/ not built in this environment, "
                  "skipping the live-site case")
    else:
        print("  note: content.json not found, skipping the live-site case")

    if fails:
        print("FAILED %d case(s):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED 12 cases (clean picks and renders pass, every defect "
         "class caught, out-of-pool articles exempt, real site clean if "
         "built)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
