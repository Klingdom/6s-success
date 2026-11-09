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

# "organi[sz]" joined 2026-11-06, mining Garage: the British/Australian/
# Canadian "organise"/"organisation"/"organiser" spelling (with an s) never
# matched this pattern, which required the American "organiz" spelling
# literally. Found live while verifying a fix for "tool organiser wall
# mounted": keyword_demand.py and keyword_demand_global.py both score and
# route every such query correctly (dialect is handled at the scorer level),
# but this room-ranking tool silently dropped every one of them from the
# on-topic tally before a human ever saw them, because this regex, not the
# scorer, decides what counts as "on topic" for ranking which room needs
# work. Checked the live corpus before fixing: 441 queries across both
# harvests (28 US, 413 global) use "organis" and no other ON_TOPIC word
# (declutter/clean/storage/stock), so 441 real, already-scored rows were
# invisible to every room's uncovered-percentage ranking this whole lane has
# used since 2026-11-03. Checked for new noise this would surface before
# shipping: sampling 61 of the newly-visible queries that do not contain an
# obvious room/furniture/storage word, the few off-topic ones ("how to
# organise a charity walk", "a seating plan", "a strategy", "drop shipping")
# are the same shape OFF_TOPIC_CONTEXT already excludes for the American
# spelling, so broadening this pattern does not bypass that filter, it only
# lets the British-spelling rows reach it like every American-spelling row
# already does.
ON_TOPIC = re.compile(r"organi[sz]|declutter|clean|storage|stock", re.I)
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
    r"organizers?\s+for\s+car\s+interior|"
    # Found 2026-11-04 (Workshop pass): "how to organize bench" as a seed
    # picked up "Benchmark Advance" (a K-12 curriculum brand) autosuggest
    # noise, nothing to do with a home workshop's Material Rack. "craft
    # paint"/"diamond painting"/"paint storage for artists" seeded from
    # "how to organize paint and chemical storage" drifted to a hobbyist
    # audience; the Finishing and Chemical Zone's own content.json purpose
    # ("Store paint, glue, stain, and solvent so they stay usable and so
    # they never start a fire") is about woodworking finish and fire
    # safety, not craft/hobby acrylics. Verified against the real corpus:
    # the genuine on-topic rows ("chemical storage best practices",
    # "spray paint storage ideas", "containers for paint storage") do not
    # match any branch of this pattern.
    r"\bbenchmark advance\b|\bdiamond painting\b|\bpainting with diamonds\b|"
    r"\bcraft paint\b|\bpaint storage for artists\b|"
    # Found 2026-11-04 (Pantry/Primary Bedroom/Family Room pass): three more
    # seed-drift rows, the same autosuggest-noise shape as "Benchmark
    # Advance" above, each checked against its own real seed before adding.
    # "declutter gardening series lessons" (seed: "how to declutter a
    # nursery") drifted to an online gardening course, nothing to do with a
    # nursery. "dental organization ideas" (seed: "den organization ideas")
    # drifted from "den" to a dental practice/clinic query. "how to
    # declutter my life reddit" (seed: "how to declutter a mudroom")
    # drifted to a general life-advice Reddit thread, nothing to do with a
    # mudroom. Verified against the full corpus: no other row in either
    # harvest contains "gardening series", "gardening lessons", "dental" or
    # "declutter my life reddit", so this cannot suppress a genuine match.
    r"\bgardening series\b|\bgardening lessons\b|\bdental\b|"
    r"\bdeclutter my life\b|"
    # Found 2026-11-04 (PM check-in, 01:4x slot): a commercial/B2B-intent
    # cluster word-overlapping onto home zones purely on "cleaning",
    # "equipment", "baking" or "organize". "organize seasonal pricing
    # model" was diagnosed as this exact shape in prose on 2026-11-03
    # ("a 'seasonal pricing model' B2B query colliding on 'organize
    # seasonal' alone") but never coded, so it kept re-surfacing as a Hall
    # Closet gap every cycle since; mining the same shape found five more:
    # "baking supplies for small business", "business plan for a cleaning
    # equipment", "cleaning supplies for a business", "equipment needed
    # for cleaning business", "how to start an outdoor storage business"
    # and "how to start baking supplies business" (all asking how to run
    # or start a business, not how to organize a home), plus "cleaning
    # company equipment list pdf" and "office cleaning equipment list"
    # (a commercial equipment checklist, not a household closet). Checked
    # each target zone's own content.json purpose first: Hall Closet's
    # Cleaning Equipment Zone, Cleaning Supply Zone and Seasonal and Guest
    # Zone, Pantry's Baking Zone and Patio or Deck's Outdoor Storage Zone
    # all describe household use only, nothing about running a business.
    # Verified against the full corpus: "business" appears in exactly
    # these 6 rows, "equipment list" in exactly these 2, "pricing model"
    # in exactly this 1; no genuine on-topic row (e.g. "how do you
    # organize a company workshop", already `covered`) uses any of these
    # three phrases, so this cannot suppress a genuine match.
    r"\bbusiness\b|\bequipment list\b|\bpricing model\b|"
    # Found 2026-11-05 (Workshop pass, the 8 partial rows handed off by the
    # 02:1x PM check-in). Same seed drift as "Benchmark Advance" above, all
    # four from "how to organize paint and chemical storage": "how to paint
    # a storage container", "how to paint a metal storage container" and
    # "how to paint plastic storage bins" are autosuggest reading the seed
    # as a request to paint a container as a craft project, not to store
    # paint; "acrylic paint storage organizer" is the same hobbyist-acrylic
    # audience "craft paint"/"diamond painting" already excludes, just a
    # phrase that list had not named yet. The Finishing and Chemical Zone's
    # own content.json purpose ("Store paint, glue, stain, and solvent so
    # they stay usable and so they never start a fire") is about what goes
    # in the container, not how to decorate one. Verified against both
    # harvests: these four phrases match exactly these four rows and no
    # other, so this cannot suppress a genuine match.
    r"how to paint (a )?(metal |plastic )?storage (container|bins)\b|"
    r"\bacrylic paint\b|"
    # Found 2026-11-05 (Garage pass, the top-ranked room by
    # room_guide_underperformance.py, 51% uncovered). Three more
    # title-word-overlap collisions, the same shape as "Benchmark Advance"
    # above but matching on a zone page's own <title> rather than a seed's
    # autosuggest drift. "cricut supplies"/"prepping supplies" land on the
    # Automotive Care Zone purely because "organize"/"supplies"/"garage"
    # overlap its title; that zone's content.json purpose and common_items
    # are fluid bottles, jumper cables and rags, nothing about a craft
    # cutting machine (Cricut) or emergency-preparedness stockpiling.
    # "pics on wall"/"pictures on a wall" land on the Hand Tool Wall and
    # Cabinets zone purely on the word "wall"; that zone is pegboard and
    # tool storage, not hanging home-decor photographs. Checked against the
    # full corpus before excluding: none of "cricut", "prepping supplies",
    # "pics on wall" or "pictures on a wall" ever lands on a page that
    # actually answers them (cricut rows route to a paperwork article and
    # `/about.html` elsewhere in the corpus; "arrange pics on wall" already
    # shows the same false Hand Tool Wall route under a different verb), so
    # excluding them here cannot suppress a genuine match.
    r"\bcricut\b|\bprepping supplies\b|"
    r"\bpics? on (a )?wall\b|\bpictures? on (a )?wall\b|"
    # Found 2026-11-05 (Garage pass, the two remaining `gap`-status rows,
    # 49% uncovered). Both are the same title/seed word-overlap shape as
    # the rows directly above, not genuine content gaps. "how to organize
    # soap making supplies" lands on the Automotive Care Zone purely on
    # "organize"/"supplies" overlapping that zone's own title ("garage car
    # care supplies"); the zone's content.json purpose and common_items are
    # fluid bottles, jumper cables and rags, nothing about a soap-making
    # hobby. "how to organize raised garden beds" lands on the Lawn and
    # Garden Tool Zone via seed drift from two unrelated seeds, "how to
    # organize garden area" and "how to organize bed and bedding" (the
    # "bed" word colliding with bedroom bedding); the zone's own purpose is
    # storing yard tools, hose and chemicals, nothing about building or
    # arranging a planting bed structure. Verified against both harvests:
    # "soap making" and "raised garden bed" each appear in exactly the one
    # row named here (the global harvest has no "raised garden bed" row at
    # all), so excluding them here cannot suppress a genuine match.
    r"\bsoap making\b|\braised garden beds?\b|"
    # Found 2026-11-07 (Kitchen pass, 39% uncovered, the 38-row partial tier
    # four PM check-ins in a row had deferred as operator-cycle-sized).
    # "how to organise dressing table drawers" carries no room signal at
    # all (attribute_room finds no room name in it) and lands on Kitchen's
    # own declutter article purely on "organise"/"drawers" word overlap
    # with no room tie to break; a dressing table is bedroom furniture, not
    # a kitchen fixture. Checked the full corpus first: Primary Bedroom,
    # Guest Bedroom and Kids Bedroom each already have a real dresser/drawer
    # zone (Dresser Top, Dresser Drawers, Guest Dresser), so the query has a
    # genuine home elsewhere on the site; it is simply not Kitchen's to
    # answer, and forcing it onto a kitchen zone would misrepresent one the
    # same way the "dinnerware" bare-word lesson warns against. Verified
    # against both harvests: "dressing table" appears in exactly this one
    # row, so excluding it here cannot suppress a genuine match.
    r"\bdressing table\b|"
    # Found 2026-11-09 (Garage pass, the 79-row partial tier handed off
    # since the FORMAT_WORDS "must haves" fix closed the room's only gap
    # row). Two word-sense collisions on the Automotive Care Zone's own
    # title. "how to organise a care package" lands there purely because
    # "care" overlaps "Automotive Care Zone"; a care package (a gift box
    # for someone sick, deployed, or a new parent) has nothing to do with
    # fluid bottles and jumper cables, and content.json's purpose names
    # only "fluids, cables, and cleaning kit." "how to organize bedazzling
    # kit" is seed drift, not a household query at all: its own seed field
    # reads "how to organize bed", the same autosuggest-noise shape as
    # "Benchmark Advance" above, with nothing to do with rhinestone craft
    # kits or a garage. Checked the full corpus first: "care package"
    # appears in exactly two rows, the one above and "how to organise a
    # home care package" (which already routes to a different, unrelated
    # article, not Garage), and "bedazzl" appears in exactly the one row
    # named here, so excluding them here cannot suppress a genuine match.
    r"\bcare package\b|\bbedazzl\w*\b|"
    # Found 2026-11-09 (Garage pass, closing the "car boot"/"interior car
    # storage" cluster A78 twice left as "a closer call" rather than
    # decided). "car travel storage organizer" and "interior car storage
    # organizers" are retail-product searches for a trunk organizer or
    # caddy, the exact shape \bcar organizers?\b and the "organizer(s) for
    # car" branches above already exclude; these two rows only escaped
    # that net because "storage" sits between "car"/"interior" and
    # "organizer(s)", breaking the adjacency those patterns require. Added
    # as exact phrases rather than widening the regex, since exactly these
    # two rows carry the shape (checked against both harvests, below).
    # Decided and NOT added: "how to organise a car boot"/"how to organise
    # your car boot" are an organizing VERB on the car's cargo space, the
    # same shape as "organize in car interior", which this file's own
    # 2026-11-03 comment above already names as a genuine on-topic row to
    # keep, not exclude. The Automotive Care Zone's content.json purpose
    # (fluids, cables, a cleaning kit kept in the garage) genuinely does
    # not address organizing the space inside the vehicle itself, so both
    # "boot" rows stay honestly `partial`: a real content gap, not a
    # wording gap a synonym could close, and not product-shopping noise
    # either. This is the decision, not a further deferral: a third cycle
    # should not reopen it without new evidence (a zone that actually
    # discusses the car's cargo area, or a query that stops being a
    # one-off). Verified against both harvests: "car travel storage" and
    # "interior car storage" each appear in exactly the one row named
    # here, so excluding them here cannot suppress a genuine match.
    r"\bcar travel storage organizer\b|\binterior car storage organizers?\b|"
    # Found 2026-11-09 (scheduled operator cycle, mining Primary Bedroom's
    # own 1 gap row rather than Garage's partial tier, which a same-day
    # cycle, A78, already closed the two cleanest finds in). "declutter
    # woodworking fundamentals tips" carries seed "how to declutter a
    # workshop", not a bedroom seed at all; it drifted to Primary Bedroom
    # only because no "how-to-declutter-a-workshop" article exists on the
    # site, so the generic title-overlap scorer fell back to
    # "how-to-declutter-a-bedroom.html" on "declutter"+"a" alone. The
    # query itself (a woodworking skills tutorial) is not a household
    # organizing question for any room; Workshop's own genuine row, "how
    # to organize a woodworking workshop", already answers correctly
    # (`partial`, routed to Workshop's own article) and shares no words
    # with "fundamentals", so excluding this phrase cannot touch it.
    # Verified against both harvests: "woodworking fundamentals" appears in
    # exactly this one row; "woodworking" alone also appears in "woodworking
    # plans for nightstand" (construction-intent noise, Guest Bedroom,
    # already its own declined class, untouched by this narrower phrase)
    # and the genuine Workshop row above, neither of which this exact
    # two-word phrase matches.
    r"\bwoodworking fundamentals\b",
    re.I)


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
    """Rows whose best_page is this room's deck, one of its zone pages, or
    the room page itself.

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

    The room page itself (`/rooms/<slug>.html`) joined 2026-11-05 for the
    same reason named in `room_guide_underperformance.py`'s sibling
    function: a room-level also-called synonym renders onto that exact
    page, and a query that then routes there was being dropped from the
    room's row set entirely rather than credited.
    """
    s = slug(room)
    deck_path = f"/{s}-deck.html"
    print_and_play_path = f"/deck/{s}-print-and-play.html"
    zone_prefix = f"/zones/{s}-"
    room_path = f"/rooms/{s}.html"
    out = []
    for r in rows:
        bp = r.get("best_page") or ""
        if (bp == deck_path or bp == print_and_play_path
                or bp == room_path or bp.startswith(zone_prefix)):
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
