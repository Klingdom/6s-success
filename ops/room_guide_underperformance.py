"""Score every room's real on-topic keyword coverage, guide included, once.

Built 2026-11-03. `room_guide_candidates.py` answered "which guide-less room
should get a guide" and that lane is now closed: all 20 rooms have one
(`ops/build_zone_pages.py`'s `ROOM_GUIDES`). The 20:4x PM check-in named the
next real question this repository has not yet answered with one method:
now that every room has a guide, which room's guide and zone pages still
leave the most real, on-topic search demand uncovered or only partially
covered. That is a genuinely different question from "has a guide" (a guide
existing does not mean the right queries land on it or its zone pages), so
it needs its own scorer rather than a flag flip on the old one.

Reuses `room_guide_candidates.py`'s matching rules (best_page over the sparse
`room` field, the on-topic/digital-context filters, the US+global dedup) and
extends them with one more route a room can answer a query through: the
guide article itself, which the old scorer never needed to match because no
guide-less room had one.

Usage: python ops/room_guide_underperformance.py [--room "Family Room"]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ops"))

from room_guide_candidates import ON_TOPIC, DIGITAL, OFF_TOPIC_CONTEXT, slug  # noqa: E402
import build_zone_pages as b  # noqa: E402


def all_rooms():
    return sorted(r["room"] for r in
                  json.loads((ROOT / "content/manual/source/content.json").read_text())["rooms"])


def guide_path(room):
    """The room's own guide article path, as a query's best_page would read it."""
    guides = b.ROOM_GUIDES.get(room)
    if not guides:
        return None
    name = guides[0][0].rsplit("/", 1)[-1]
    return f"/articles/{name}"


def room_rows(rows, room):
    """Rows whose best_page is this room's deck, a zone page, or its guide article.

    Same matching `room_guide_candidates.py.room_rows` does (deck, print-and-play
    deck, zone prefix), plus the guide article path, which that function never
    needed to check because every room it scored had none.
    """
    s = slug(room)
    deck_path = f"/{s}-deck.html"
    print_and_play_path = f"/deck/{s}-print-and-play.html"
    zone_prefix = f"/zones/{s}-"
    gp = guide_path(room)
    out = []
    for r in rows:
        bp = r.get("best_page") or ""
        if bp == deck_path or bp == print_and_play_path or bp == gp or bp.startswith(zone_prefix):
            out.append(r)
    return out


def score_room(us_rows, global_rows, room):
    us = room_rows(us_rows, room)
    gl = room_rows(global_rows, room)
    # Same double-count guard room_guide_candidates.py uses: 1069+ queries are
    # tracked in both tiers, and a plain concatenation would count them twice.
    by_query = {}
    for r in us + gl:
        by_query.setdefault(r["query"], r)
    combined = list(by_query.values())
    on_topic = [r for r in combined if ON_TOPIC.search(r["query"])]
    on_topic_clean = [r for r in on_topic
                       if not DIGITAL.search(r["query"]) and not OFF_TOPIC_CONTEXT.search(r["query"])]
    gap = [r for r in on_topic_clean if r["status"] == "gap"]
    partial = [r for r in on_topic_clean if r["status"] == "partial"]
    covered = [r for r in on_topic_clean if r["status"] == "covered"]
    uncovered_count = len(gap) + len(partial)
    on_topic_n = len(on_topic_clean)
    shortfall = (uncovered_count / on_topic_n) if on_topic_n else 0.0
    return {
        "room": room,
        "has_guide": room in b.ROOM_GUIDES,
        "total_routed_rows": len(combined),
        "on_topic_rows": on_topic_n,
        "gap": gap,
        "partial": partial,
        "covered_count": len(covered),
        "uncovered_count": uncovered_count,
        "shortfall": shortfall,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", default=None, help="score one room instead of every room")
    ap.add_argument("--min-on-topic", type=int, default=5,
                    help="skip rooms with fewer on-topic rows than this (too little signal to rank); default 5")
    args = ap.parse_args()

    us_rows = json.loads((ROOT / "ops/keyword-demand.json").read_text())["rows"]
    global_rows = json.loads((ROOT / "ops/keyword-demand-global.json").read_text())["rows"]

    rooms = [args.room] if args.room else all_rooms()
    results = [score_room(us_rows, global_rows, r) for r in rooms]
    ranked = [r for r in results if r["on_topic_rows"] >= args.min_on_topic] if not args.room else results
    skipped = [r for r in results if r["on_topic_rows"] < args.min_on_topic] if not args.room else []
    ranked.sort(key=lambda r: (r["shortfall"], r["uncovered_count"]), reverse=True)

    for r in ranked:
        guide_note = "guide" if r["has_guide"] else "NO GUIDE"
        print(f"\n{r['room']} ({guide_note}): {r['shortfall']:.0%} uncovered "
              f"({len(r['gap'])} gap + {len(r['partial'])} partial of {r['on_topic_rows']} on-topic, "
              f"{r['covered_count']} covered, {r['total_routed_rows']} routed rows total)")
        for g in r["gap"]:
            print(f"    gap: {g['query']}  (-> {g.get('best_page')})")
        for p in r["partial"][:8]:
            print(f"    partial ({p.get('coverage')}): {p['query']}  (-> {p.get('best_page')})")

    if skipped:
        print(f"\nSkipped (fewer than {args.min_on_topic} on-topic rows, too little signal to rank): "
              + ", ".join(f"{r['room']} ({r['on_topic_rows']})" for r in skipped))


if __name__ == "__main__":
    main()
