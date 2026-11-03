"""Score every guide-less room's real on-topic keyword gap, once, the same way every time.

Built 2026-11-02 after the identical tie-score mistake recurred three times in
BACKLOG-2026-09-07.md (sections 82, 83, and the Family Room re-read this cycle
corrected): each cycle recomputed a candidate room's "gap count" with its own
ad hoc one-liner, and each one used a different, undocumented method (the
sparse `room` field vs the `best_page` a query actually routes to; with or
without an on-topic filter; with or without excluding digital/software
queries that route to a physical zone page by word overlap alone, e.g. "how
to organize steam games" landing on the board-game-and-puzzle zone). Three
different methods produced three different, each-confidently-stated gap
counts for the same room. This script is the one method, run the same way
every time, so the next cycle inherits a number instead of re-deriving one.

Usage: python ops/room_guide_candidates.py [--room "Family Room"]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

ON_TOPIC = re.compile(r"organiz|declutter|clean|storage|stock", re.I)
# Found 2026-11-02: queries that route to a room's zone page by word overlap
# (e.g. "storage", "organize") but ask about a digital library, not a
# physical zone. Excluding them is the fix the 13:4x cycle on 2026-11-02
# named and deferred as "too large for this slot."
# "hard drive" added 2026-11-03: "how to organize hard drive files",
# "organizing hard drive files" and "organize hard drive space" were all
# routing into Home Office's own File Storage zone (or nearby articles) as
# false on-topic gaps, the same digital-library shape this regex already
# excludes "pc"/"steam"/"computer" for, just a phrase this list had not
# named yet.
DIGITAL = re.compile(
    r"\b(pc|steam|computer|desktop|digital|online|software|app|download)\b"
    r"|hard drive", re.I)

# Found 2026-11-03 (Garage pass): "car organizer"/"car trunk"/retailer-named
# queries route to the Automotive Care Zone by word overlap on
# "organize"/"car" alone, but ask about a retail product for inside the
# vehicle (a trunk organizer, a seat-back caddy) or a specific store's stock,
# not the zone's own garage shelf. The zone's content.json purpose is
# explicit ("fluids, cables, and cleaning kit... upright, labeled, separate
# from everything the household touches"), nothing about the inside of the
# car itself, so this is the same false on-topic match DIGITAL already
# excludes, just a different mismatched physical space. Verified against the
# real corpus before adding: genuine on-topic rows ("organize car
# maintenance tips", "how to organize car cleaning supplies", "organize in
# car interior") use "organize" as a verb on supplies/maintenance and do not
# match any branch of this pattern.
OFF_TOPIC_CONTEXT = re.compile(
    r"\bcar organizers?\b|\bcar trunk\b|canadian tire|"
    r"organizers?\s+(?:bag\s+)?for\s+car\b|"
    r"organizers?\s+for\s+car\s+interior", re.I)


def guide_less_rooms():
    """Rooms with no article guide yet, derived live from ROOM_GUIDES.

    Found 2026-11-02: this used to be a hand-maintained list. It still said
    "Kids Bedroom" the same cycle that room's guide shipped and ROOM_GUIDES
    picked it up, the exact "source corrected, sibling never told" defect
    class this repository exists to catch. Deriving it from the two real
    sources removes the sync step instead of promising to remember it.
    """
    import build_zone_pages as b
    all_rooms = {r["room"] for r in
                 json.loads((ROOT / "content/manual/source/content.json").read_text())["rooms"]}
    return sorted(all_rooms - set(b.ROOM_GUIDES.keys()))


GUIDE_LESS_ROOMS = guide_less_rooms()


def slug(room):
    return room.lower().replace(" ", "-")


def room_rows(rows, room):
    """Rows whose best_page is this room's deck or one of its zone pages.

    Matches on best_page, not the sparse `room` field (881 of 2808 rows carry
    it; the rest, including most gap rows, do not), because best_page is what
    actually decides whether a query already has an answer on this room.

    Found 2026-11-03, verifying a PM check-in's handoff naming Entryway as
    the next room-guide candidate at "23 unmet rows" (the sparse `room`
    field count this docstring already warns against): this function itself
    was missing 80 real Entryway rows, 30 of them on-topic and none `gap`,
    because `/deck/entryway-print-and-play.html` is a second, differently
    shaped deck URL this room ships (print-and-play, under `/deck/`) that
    neither `deck_path` nor `zone_prefix` matched. Entryway is the only
    guide-less room with such a page today, but the shape is not
    room-specific, so the pattern is matched generally rather than
    special-cased to one slug.
    """
    s = slug(room)
    deck_path = f"/{s}-deck.html"
    print_and_play_path = f"/deck/{s}-print-and-play.html"
    zone_prefix = f"/zones/{s}-"
    out = []
    for r in rows:
        bp = r.get("best_page") or ""
        if bp == deck_path or bp == print_and_play_path or bp.startswith(zone_prefix):
            out.append(r)
    return out


def score_room(us_rows, global_rows, room):
    us = room_rows(us_rows, room)
    gl = room_rows(global_rows, room)
    # 1069 queries are tracked in both the US and global tiers (checked
    # 2026-11-02). A plain `us + gl` concatenation counts each of those
    # twice, inflating on_topic/partial/gap counts for every guide-less
    # room (verified: 1-8 double-counted partial rows per room today,
    # no gap-status duplicate yet, but len(gap) is the exact sort key
    # that picks the next room to ship, so one is a matter of when).
    by_query = {}
    for r in us + gl:
        by_query.setdefault(r["query"], r)
    combined = list(by_query.values())
    on_topic = [r for r in combined if ON_TOPIC.search(r["query"])]
    on_topic_clean = [r for r in on_topic
                       if not DIGITAL.search(r["query"]) and not OFF_TOPIC_CONTEXT.search(r["query"])]
    gap = [r for r in on_topic_clean if r["status"] == "gap"]
    partial = [r for r in on_topic_clean if r["status"] == "partial"]
    excluded_digital = [r for r in on_topic
                         if DIGITAL.search(r["query"]) or OFF_TOPIC_CONTEXT.search(r["query"])]
    return {
        "room": room,
        "total_routed_rows": len(combined),
        "on_topic_rows": len(on_topic_clean),
        "gap": gap,
        "partial_count": len(partial),
        "excluded_digital_count": len(excluded_digital),
        "excluded_digital_sample": [r["query"] for r in excluded_digital[:5]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", default=None, help="score one room instead of all guide-less rooms")
    args = ap.parse_args()

    us_rows = json.loads((ROOT / "ops/keyword-demand.json").read_text())["rows"]
    global_rows = json.loads((ROOT / "ops/keyword-demand-global.json").read_text())["rows"]

    rooms = [args.room] if args.room else GUIDE_LESS_ROOMS
    results = [score_room(us_rows, global_rows, r) for r in rooms]
    results.sort(key=lambda r: len(r["gap"]), reverse=True)

    for r in results:
        print(f"\n{r['room']}: {len(r['gap'])} on-topic gap, {r['partial_count']} partial, "
              f"{r['on_topic_rows']} on-topic of {r['total_routed_rows']} routed rows "
              f"({r['excluded_digital_count']} digital-context rows excluded)")
        for g in r["gap"]:
            print(f"    gap: {g['query']}  ({g.get('best_page')})")
        if r["excluded_digital_sample"]:
            print(f"    excluded sample: {r['excluded_digital_sample']}")


if __name__ == "__main__":
    main()
