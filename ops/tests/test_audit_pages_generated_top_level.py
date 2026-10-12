"""Prove ops/audit_pages.py attributes a finding on a top-level generated
page to its real generator, not to "hand written pages".

Found 2026-10-12, second-pass cold read: is_generated()'s predecessor,
the bare GENERATED regex, only matched a /rooms/ or /zones/ path segment.
Every one of the 28 top-level generated pages in ops/preflight.py's own
GENERATED_TOP_LEVEL_PAGES registry (kitchen-deck.html and its 23 deck
siblings, corporate.html, how-to-clean-anything.html, both deck-gallery
pages, kit.html, resources.html, standards.html, shop.html) fell outside
it, so a finding there would have printed "hand written pages" as where
the fix goes: the exact misdirection step 5b warns against, hand-editing
a file a generator overwrites on its next run.

This does not plant a file (audit_pages.py's own pages() glob would pick
up a stray site/kitchen-deck.html-shaped fixture and risk colliding with
the real page of that name); it tests is_generated() directly, the one
function the fix lives in.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import audit_pages as A                                       # noqa: E402
import preflight as P                                         # noqa: E402

SITE = A.SITE


def main() -> int:
    bad = []

    # A sample of top-level generated pages, each from a different
    # generator, per ops/preflight.py's GENERATED_TOP_LEVEL_PAGES.
    for name in ("kitchen-deck.html", "corporate.html", "shop.html",
                  "deck-gallery-mudroom.html", "how-to-clean-anything.html"):
        path = os.path.join(SITE, name)
        if not A.is_generated(path):
            bad.append(f"is_generated() said {name!r} is hand written, but "
                       f"ops/preflight.py's GENERATED_TOP_LEVEL_PAGES names "
                       f"a generator for it")

    # A real zone/room page: still recognised, the pre-existing behaviour.
    zone_path = os.path.join(SITE, "zones",
                             "kitchen-the-cooking-zone.html")
    if not A.is_generated(zone_path):
        bad.append("is_generated() stopped recognising a /zones/ page as "
                   "generated; this is the behaviour the fix must keep")

    # A genuinely hand-maintained page: must NOT be reclassified.
    for name in ("about.html", "index.html", "book.html"):
        path = os.path.join(SITE, name)
        if A.is_generated(path):
            bad.append(f"is_generated() said {name!r} is generated; it is "
                       f"in ops/preflight.py's HAND_MAINTAINED_PAGES")

    # The two registries must stay disjoint, same invariant
    # gate_page_ownership_registry already enforces in ops/preflight.py;
    # checked here too since is_generated() depends on it directly.
    overlap = set(A.GENERATED_TOP_LEVEL_PAGES) & P.HAND_MAINTAINED_PAGES
    if overlap:
        bad.append(f"GENERATED_TOP_LEVEL_PAGES and HAND_MAINTAINED_PAGES "
                   f"overlap on {sorted(overlap)}")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  is_generated() correctly classifies top-level "
              "generated pages, zone/room pages, and hand-maintained "
              "pages")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
