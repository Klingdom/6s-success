#!/usr/bin/env python3
"""
Pick one dialect for the catalogue's own prose, and hold it there.

BACKLOG-2026-09-07.md A12 measured content.json split inside itself: labelled
93 against labeled 60, grey 41 against gray 12, colour 18 against color 127,
centre 3 against center 7, neighbour 4 against neighbor 0, favourite 3 against
favorite 1. That is not a British voice, which would be a legitimate editorial
choice (CLAUDE.md section 10); it is no voice, inconsistent inside one
authored corpus, while every page title on the site is American ("How to
organize the entryway coats and outerwear") and the market is Boise, Idaho.
American is the dialect already winning every surface a reader judges a site
by first, so American is what this file enforces, not a fresh choice.

Two sources carry the drift, independently, not one feeding the other:

  content/manual/source/content.json           the live site's own data source
                                                 (zone pages, room pages, decks)
  content/manual/micro-zone-manual-publishable.html
                                                 the $29 Micro Zone Manual's own
                                                 prose, a separate static file
                                                 that content.json does not feed
                                                 and that no generator produces

Both are fixed here, independently, because both are real, currently-sold
surfaces. The 50-chapter book (content/book/**) is NOT touched by this file.
It carries the same kind of drift at a much larger scale (589 files at last
count) but it is hand-authored prose in Phil's own voice, not data fields, and
a blind pass across a paid book risks mangling a quote, a proper noun or a
deliberate stylistic choice this tool cannot tell from a genuine defect. That
is recorded as its own, separate, deliberately un-started backlog item rather
than folded in here under one commit's blast radius.

The substitution is not blind inside the files it does touch, either: every
pair below is a genuine British-only spelling with no American sense (not
"towards", which is standard in both dialects and not a dialect error), each
one checked against its real context in this corpus before being added (shed
grit, cable labels, discoloured grout, a dresser full of jewellery: plain
prose, no brand name, no quoted dialogue, no proper noun). Word-boundary
matching only, case preserved on the first letter so a sentence-initial
capital survives ("Mould" stays "Mold", not "mold").

Run:      python ops/fix_dialect.py --check     report only, exit 1 if any remain
          python ops/fix_dialect.py --apply     rewrite the files
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = [
    os.path.join(ROOT, "content", "manual", "source", "content.json"),
    os.path.join(ROOT, "content", "manual", "micro-zone-manual-publishable.html"),
    # gate_manual_zone_content_current checks this file's own purpose/
    # done_looks_like text against content.json directly; it is a second,
    # not-quite-identical hand-authored copy of the Manual (482 lines of
    # structural diff against the publishable.html above, same zone prose),
    # so it carries the same drift independently and needs the same fix.
    os.path.join(ROOT, "content", "manual", "6S Home Micro Zone SOP Field Manual v3.html"),
    # Captions/alt text for the imported room diagrams (ops/import_room_
    # images.py), consumed by ops/build_zone_pages.py and shown on every
    # room page ("On the left, labelled before..."). Copied over from the
    # book's own figure captions at import time, so it carries the same
    # drift independently of content.json.
    os.path.join(ROOT, "ops", "room-images.json"),
    # The 123-product master catalogue: every "why" sentence shown in a
    # zone's kit list (ops/zone_supplies.py) and every product page
    # (ops/build_kit_page.py) traces back to this one hand-maintained CSV.
    os.path.join(ROOT, "ops", "affiliate-catalogue.csv"),
    # ops/zone_supplies.py's own docstring: two files know what each zone's
    # kit needs, independently of content.json. This is the other one
    # (114 zones, 1,867 product rows, hand-maintained, not CSV-derived).
    os.path.join(ROOT, "content", "manual", "source", "zone_products.json"),
    os.path.join(ROOT, "content", "manual", "source", "products.json"),
    # Delivered to every Etsy buyer as "How-to-print-these-cards.pdf"
    # (build/listings/build_etsy_assets.py's own INSTRUCTIONS tuple).
    os.path.join(ROOT, "build", "listings", "print-instructions.html"),
]

# British -> American, longest/most-specific first so e.g. "unlabelled" is
# matched before "labelled" would otherwise eat its tail via re.sub ordering
# (word-boundary matching makes this moot for substring safety, but ordering
# still keeps the report grouped sensibly).
PAIRS = [
    ("unlabelled", "unlabeled"), ("relabelled", "relabeled"), ("mislabelled", "mislabeled"),
    ("labelled", "labeled"), ("labelling", "labeling"),
    ("discoloured", "discolored"), ("discolouring", "discoloring"), ("discolouration", "discoloration"),
    ("colourful", "colorful"), ("coloured", "colored"), ("colouring", "coloring"),
    ("colours", "colors"), ("colour", "color"),
    ("neighbourhoods", "neighborhoods"), ("neighbourhood", "neighborhood"),
    ("neighbours", "neighbors"), ("neighbour", "neighbor"),
    ("favourites", "favorites"), ("favourite", "favorite"),
    ("greyed", "grayed"), ("greying", "graying"), ("grey", "gray"),
    ("centred", "centered"), ("centring", "centering"), ("centres", "centers"), ("centre", "center"),
    ("moulded", "molded"), ("moulding", "molding"), ("mouldy", "moldy"), ("mould", "mold"),
    ("jewellery", "jewelry"),
    ("tyres", "tires"), ("tyre", "tire"),
    ("metres", "meters"), ("metre", "meter"),
    ("fibres", "fibers"), ("fibre", "fiber"),
    ("travelling", "traveling"), ("travelled", "traveled"), ("traveller", "traveler"),
    ("draughty", "drafty"), ("draught", "draft"),
    ("honoured", "honored"), ("honours", "honors"), ("honour", "honor"),
    ("vapour", "vapor"),
    ("odours", "odors"), ("odour", "odor"),
    ("ageing", "aging"),
    ("judgements", "judgments"), ("judgement", "judgment"),
    ("storeys", "stories"), ("storey", "story"),
]


# VOCABULARY, not spelling. Added 2026-10-26 after reading every cleaning
# method on the live site: the corpus spells American and SPEAKS British, so a
# US reader was told to degrease the hob, wipe the skirting, rinse under the
# tap and fetch a torch. Each pair below was checked in context across every
# TARGET before it went in, and each is a phrase with no competing American
# sense at a word boundary. Deliberately NOT here:
#   "cupboard", "fridge", "mobile"   ordinary American usage too
#   bare "takeaway"                  room-images.json uses it to mean "the
#                                    lesson", so only the food senses below
#   bare "tap"                       also a verb ("tap the papers square",
#                                    "when you tap it"), so only noun phrases
VOCAB = [
    ("skirting boards", "baseboards"), ("skirting board", "baseboard"),
    ("skirting", "baseboard"),
    # "the extractor" is a range hood in a kitchen and an exhaust fan in a
    # bathroom; the first version of this list made it a range hood in
    # the toilet area. Only phrases whose room is unambiguous.
    ("extractor hood", "range hood"),
    ("the extractor is not clearing", "the range hood is not clearing"),
    ("the extractor running", "the exhaust fan running"),
    ("hobs", "stovetops"), ("hob", "stovetop"),
    ("washing-up liquid", "dish soap"),
    # Clothing senses only: "jumper cables" is correct American and the
    # first version of this list turned it into "sweater cables".
    ("jumpers", "sweaters"), ("wool jumper", "wool sweater"),
    ("a jumper or", "a sweater or"),
    ("cotton buds", "cotton swabs"), ("cotton bud", "cotton swab"),
    ("chiselling", "chiseling"),
    ("kitchen roll", "paper towels"),
    ("tea towels", "dish towels"), ("tea towel", "dish towel"),
    ("torches", "flashlights"), ("torch", "flashlight"),
    ("trainers", "sneakers"),
    ("wellies", "rain boots"),
    ("sun cream", "sunscreen"),
    ("tinned", "canned"),
    ("takeaway menus", "takeout menus"),
    ("takeaway chopsticks", "takeout chopsticks"),
    ("dog lead", "dog leash"),
    ("rubbish sack", "trash bag"), ("rubbish", "trash"),
    ("airing cupboard", "linen closet"),
    ("a fortnight", "two weeks"),
    ("the taps", "the faucets"), ("the tap", "the faucet"),
    ("outdoor tap", "outdoor faucet"), ("shower tap", "shower faucet"),
]


def _replacement(match: "re.Match", american: str) -> str:
    word = match.group(0)
    if word[0].isupper():
        return american[0].upper() + american[1:]
    return american


def fix_text(text: str) -> tuple[str, dict]:
    counts: dict = {}
    for british, american in PAIRS + VOCAB:
        pattern = re.compile(r"\b" + re.escape(british) + r"\b", re.IGNORECASE)
        n = len(pattern.findall(text))
        if n:
            counts[british] = n
            text = pattern.sub(lambda m, a=american: _replacement(m, a), text)
    return text, counts


def main(apply: bool) -> int:
    total = 0
    any_file_changed = False
    for path in TARGETS:
        if not os.path.exists(path):
            print(f"  MISSING: {path}")
            continue
        with open(path, encoding="utf-8") as f:
            original = f.read()
        fixed, counts = fix_text(original)
        file_total = sum(counts.values())
        rel = os.path.relpath(path, ROOT)
        if not counts:
            print(f"  {rel}: clean")
            continue
        total += file_total
        any_file_changed = True
        print(f"  {rel}: {file_total} instance(s)")
        for british, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            american = dict(PAIRS + VOCAB)[british]
            print(f"      {british} -> {american}: {n}")
        if apply:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(fixed)
            print(f"      written")

    if apply:
        if any_file_changed:
            print(f"\nFixed {total} instance(s). Re-run the generator ownership "
                  "chain (ops/preflight.py --own, or the individual build_*.py "
                  "scripts that read content.json) before committing.")
        return 0

    if total:
        print(f"\n{total} British spelling instance(s) remain. "
              "Run with --apply to fix.")
        return 1
    print("\nClean: 0 British spellings in the tracked surfaces.")
    return 0


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    sys.exit(main(apply))
