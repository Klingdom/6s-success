#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_articles_room_zone_counts_current() catches
site/articles/what-is-6s.html or the timing article naming a room or micro
zone count that no longer matches
content/manual/source/content.json.

Found 2026-09-18, cold-reading ops/build_articles.py per the standing
handoff. Both AEO articles hand-typed "20 rooms" (spelled "Twenty rooms" in
one place) and "114 micro zones" as plain prose literals in several spots,
while every zone-per-room figure on the same pages was already computed
fresh from the real manual, including the article's own median-time
calculation, which silently assumed exactly 20 rooms (an even count) to
average index 9 and 10 of a sorted list rather than compute a real median.
Both numbers matched reality today (20 rooms, 114 zones in content.json),
so this closed a latent gap rather than a live defect; fixed at the source
in ops/build_articles.py (article_one()/article_two() now derive both
counts from the real room list, and the median calculation is now generic
for any room count).

Tests the pure logic (check_articles_room_zone_counts) with synthetic
data, then checks the real committed pages against a live re-derivation
from the real content.json, so a future regression (a hand edit to either
article, or build_articles.py reverting to a hardcoded literal) is caught
either way.

Run:  python ops/tests/test_gate_articles_room_zone_counts.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    # 1. Clean: both pages correctly name the live counts.
    pages = {
        "what-is-6s.html": "<p>The full model is 20 rooms broken into 114 "
                           "micro zones.</p>",
        "how-long-does-it-take-to-organise-a-room.html":
            "<p>20 rooms, 114 micro zones, sorted here.</p>",
    }
    problems = preflight.check_articles_room_zone_counts(20, 114, pages)
    if problems:
        fails.append(f"1. expected clean, got {problems}")

    # 2. A stale spelled-out room count, the exact shape the real
    # what-is-6s.html carried before this fix ("Twenty rooms").
    pages_stale_word = {
        "how-long-does-it-take-to-organise-a-room.html":
            "<p>Twenty rooms, 114 micro zones, sorted here.</p>",
    }
    problems = preflight.check_articles_room_zone_counts(20, 114,
                                                          pages_stale_word)
    if not problems or "Twenty" not in str(problems) and "spelled" not in str(problems):
        fails.append(f"2. expected a spelled-out-number finding, got {problems}")

    # 3. A room count that no longer matches (a room added, page not rerun).
    pages_stale_room = {
        "what-is-6s.html": "<p>The full model is 20 rooms broken into 114 "
                           "micro zones.</p>",
    }
    problems = preflight.check_articles_room_zone_counts(21, 114,
                                                          pages_stale_room)
    if not problems or "21" not in str(problems):
        fails.append(f"3. expected a stale room-count finding naming 21, "
                     f"got {problems}")

    # 4. A zone count that no longer matches (a zone added, page not rerun).
    pages_stale_zone = {
        "what-is-6s.html": "<p>The full model is 20 rooms broken into 114 "
                           "micro zones.</p>",
    }
    problems = preflight.check_articles_room_zone_counts(20, 115,
                                                          pages_stale_zone)
    if not problems or "115" not in str(problems):
        fails.append(f"4. expected a stale zone-count finding naming 115, "
                     f"got {problems}")

    # 5. A genuinely unrelated number ("5 chapters", "3 sessions") must not
    # false-positive: only a bare "<n> rooms"/"<n> micro zones" counts.
    pages_unrelated = {
        "what-is-6s.html": "<p>20 rooms, 114 micro zones. The 50 chapters "
                           "this page summarises took 3 sessions.</p>",
    }
    problems = preflight.check_articles_room_zone_counts(20, 114,
                                                          pages_unrelated)
    if problems:
        fails.append(f"5. expected no false positive on unrelated numbers, "
                     f"got {problems}")

    # 6. Live check: the real committed pages against a live re-derivation
    # from the real content.json.
    src_path = os.path.join(ROOT, "content", "manual", "source",
                            "content.json")
    a1_path = os.path.join(ROOT, "site", "articles", "what-is-6s.html")
    a2_path = os.path.join(ROOT, "site", "articles",
                           "how-long-does-it-take-to-organise-a-room.html")
    if os.path.exists(src_path) and os.path.exists(a1_path) and os.path.exists(a2_path):
        rooms = json.load(io.open(src_path, encoding="utf-8"))["rooms"]
        n_rooms = len(rooms)
        n_zones = sum(len(r["zones"]) for r in rooms)
        real_pages = {
            os.path.basename(p): io.open(p, encoding="utf-8",
                                         errors="replace").read()
            for p in (a1_path, a2_path)
        }
        problems = preflight.check_articles_room_zone_counts(
            n_rooms, n_zones, real_pages)
        if problems:
            fails.append(f"6. real committed pages should be clean against "
                         f"the real content.json, got {problems}")
    else:
        fails.append("6. real files missing, cannot run live check")

    if fails:
        print("FAIL")
        for f in fails:
            print(" ", f)
        return 1
    print(f"PASS ({6} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
