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
    # "organi[sz]er" joined 2026-11-10, mining Garage: the ON_TOPIC pattern
    # was broadened to the British/Australian/Canadian "organis" spelling on
    # 2026-11-06, but this exclusion was never given the same treatment, so
    # "car organiser diy" (the exact British-spelling twin of the already-
    # excluded "car organizer ideas diy") was leaking through as a false
    # on-topic match. Checked the corpus first: only that one row uses the
    # "organiser(s)" spelling anywhere near "car"; "car organisation
    # essentials/must haves" use the noun "organisation" (the activity, not
    # the product), the exact same shape as the already-kept z-spelling
    # "car organization and storage"/"car organization india" rows, so
    # broadening to "organi[sz]er" rather than "organi[sz](?:er)?" cannot
    # touch them.
    r"\bcar organi[sz]ers?\b|\bcar trunk\b|canadian tire|"
    r"organi[sz]ers?\s+(?:bag\s+)?for\s+car\b|"
    r"organi[sz]ers?\s+for\s+car\s+interior|"
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
    r"\bwoodworking fundamentals\b|"
    # Found 2026-11-10 (scheduled operator cycle, mining Garage's 74-row
    # partial tier, the shape entries A68-A78 kept re-discovering one word
    # at a time without ever naming the class). "garage organization ideas
    # pinterest/ikea/reddit/lowes/youtube/home depot", "garden tool
    # organizer canada/rona", "kitchen organization ideas dollar
    # tree/amazon/tamil/indian", "linen cupboard organisation
    # kmart/target/australia" and 70 more rows across 16 rooms score
    # `partial`/`gap` for exactly one reason: the query names a retailer, a
    # content platform, or a country/language, and the room's real content
    # does not. It never will, by design: CLAUDE.md section 5 is explicit,
    # "Product types, never brand names," so this site cannot honestly
    # become the page that ranks for "ikea" or "pinterest" without breaking
    # its own rule, and a country/language word ("canada", "australia",
    # "tamil", "indian") is not a wording gap a synonym closes either,
    # since the advice itself does not change by country. Counted directly
    # against the live corpus before adding (CLAUDE.md 5c/5d): 89 on-topic
    # `gap`/`partial` rows across 16 rooms have unmatched_words that are
    # entirely one of these words, and only 2 rows anywhere in either
    # harvest contain one of these words AND a different unmatched word
    # ("amazon shopping car organizer", "how to declutter my life
    # reddit"), both already excluded above by the `car organizers?` and
    # `declutter my life` branches, so this cannot suppress a genuine
    # match or hide a second real gap behind a brand mention. This is a
    # measurement-tool correction, not a content fix: every room's
    # uncovered percentage was counting rows that cannot be fixed without
    # violating section 5, inflating Garage/Kitchen/Pantry/Hall Closet/Home
    # Office's own shortfall and sending cycle after cycle back through
    # the same retailer-name rows. "home depot" and "dollar tree" are
    # exact two-word phrases, not split on "home"/"dollar"/"tree" alone,
    # since those single words are common and unrelated (e.g. "home
    # office", "linen closet organization amazon" already matches
    # \bamazon\b without needing "tree").
    r"\bpinterest\b|\bikea\b|\breddit\b|\byoutube\b|\bamazon\b|\blowes\b|"
    r"\bkmart\b|\btarget\b|\bwalmart\b|\brona\b|\bhome depot\b|"
    r"\bdollar tree\b|\baustralia\b|\bcanada\b|\bindian?\b|\btamil\b|"
    # Found 2026-11-10, mining Guest Bathroom's 20-row partial tier (least-
    # mined room this lane has reached, per the 19:1x PM check-in's own
    # handoff). "linen cupboard organisation bunnings" is the same retailer-
    # name shape the branch above already excludes for kmart/target/ikea
    # etc, just one brand (Bunnings, an Australian hardware chain) the
    # original list missed. Checked against both harvests: "bunnings"
    # appears in exactly this one row.
    r"\bbunnings\b|"
    # Found 2026-11-10 (scheduled operator cycle, finally executing the
    # Garage/Hall Closet zone-level mining four prior cycles had named as
    # the one deferred lane but never opened). Three more word-overlap
    # collisions in Garage's 60-row and Hall Closet's 42-row partial tiers.
    # "garage sale" queries ("how to organize items for a garage sale",
    # "how to organize a garage sale without tables") are about selling
    # possessions at an event, not about organizing the garage as a room;
    # the word "garage" is the same homonym collision "declutter my life"
    # and "dental" above already exclude for other rooms. "back of stove
    # storage" is a kitchen-appliance query (seed: "how to organize stove
    # area") that only reached Garage because "storage" overlaps the
    # garage article's title; a stove has nothing to do with a garage.
    # "list of equipment for cleaning services" is the same commercial/B2B
    # shape \bequipment list\b already excludes, just reordered ("equipment
    # for cleaning services" vs "cleaning equipment list"): someone
    # researching what a cleaning business needs, not a household closet.
    # Verified against both harvests before adding: "garage sale" appears
    # only in the rows named above plus a handful already scored `covered`
    # (e.g. "how to organize a garage sale", which already has a real
    # answer and is untouched by this exclusion); "back of stove" and
    # "cleaning services" each appear in exactly the one row named here.
    # None of these three phrases ever appears on a genuine on-topic row
    # that lacks another exclusion already, so this cannot suppress a real
    # gap.
    r"\bgarage sale\b|\bback of stove\b|\bcleaning services\b|"
    # Found 2026-11-10, this operator cycle (Mudroom/Patio or Deck pass,
    # both tied top at 28% uncovered once the retailer/platform/geo and
    # garage-sale/stove/B2B noise above was already excluded). "woodworking
    # plans for nightstand" and "woodworking fundamentals" above were each
    # excluded one query at a time as they turned up; the underlying class
    # was never named or consolidated anywhere in this file. 61 on-topic
    # gap/partial rows across at least 10 rooms (Patio or Deck, Mudroom,
    # Stair Landing, Family Room, Garage, Guest Bedroom, Laundry Room,
    # Nursery, Entryway, Living Room) ask how to BUILD a physical structure
    # from raw materials (a deck, a railing, a walkway, a staircase, an
    # entertainment center, a charging station, a grill station, a drying
    # rack, a nightstand, a wall tool organizer, a drop zone, mudroom or
    # bench or outdoor storage, a handrail, exterior stairs, a book storage
    # box) rather than how to ORGANIZE one that already exists. This site
    # teaches the 6S method on belongings a household already owns; it has
    # no carpentry, woodworking or construction content anywhere, and
    # answering these would mean writing a different trade's how-to, not
    # closing an organizing-wording gap a synonym could ever fix. Checked
    # against the full corpus before adding (CLAUDE.md 5c/5d): the pattern
    # matches exactly 61 gap/partial rows across both harvests and 1
    # covered row ("how to make a nightstand"), left untouched since this
    # exclusion only narrows the gap/partial on-topic tally and never
    # reclassifies a covered row. Spot-checked a sample of the 61 against
    # their real routed pages: every one is construction intent, and none
    # is already answered as an organizing question anywhere else in
    # either corpus.
    r"\b(?:build(?:ing)?|how to (?:build|make))\b.{0,40}\b(?:railing|walkway|"
    r"staircase|stair\s*landing|patio\s*deck|entertainment\s*center|"
    r"charging\s*station|grill\s*station|drying\s*rack|nightstand|"
    r"tool\s*organizer|drop\s*zone|mudroom\s*storage|bench\s*storage|"
    r"outdoor\s*storage|outdoor\s*seat(?:ing|s)?|"
    r"outdoor\s*(?:dining\s*table|table\s*and\s*chairs)|handrail|"
    r"exterior\s*stairs|book\s*storage\s*box)\b|"
    # Found 2026-11-10 (Workshop pass): "workshop" collides with the
    # professional seminar/class/meeting sense (a dance workshop, a training
    # workshop, a writing workshop, "a successful workshop," "a workshop
    # presentation," "organize meditation/negotiation workshop," "organize
    # logistics for a workshop"), none of which concern a home garage
    # workshop; this site has no event-planning content to answer them with.
    # Two more collisions in the same room's tier: "how to organize power
    # tools in truck" is vehicle-interior storage, the same mismatched-
    # physical-space shape the car-organizer branch above already excludes
    # for Garage, and "how to store paintings in storage" means fine-art
    # paintings, not the Finishing and Chemical Zone's own paint cans.
    # "woodworking workshop" was checked and deliberately left alone: a home
    # workshop used for woodworking is also common usage, so excluding it
    # would risk suppressing a real match on weak evidence (CLAUDE.md 5d).
    # Checked against the full corpus before adding: every genuine on-topic
    # row ("how to organize a home workshop", "garage workshop organization
    # ideas", "workshop storage ideas", "wood workshop organization ideas")
    # names the workshop as a physical space directly and matches none of
    # these branches.
    r"\b(?:dance|successful|training|writing)\s+workshop\b|"
    r"\bworkshop\s+presentation\b|"
    r"\borganize\s+(?:logistics\s+for\s+a|meditation|negotiation)\s+workshop\b|"
    r"\bpower\s+tools?\s+in\s+(?:a\s+)?truck\b|"
    r"\bstore\s+paintings?\s+in\s+storage\b|"
    # Found 2026-11-10 (scheduled operator cycle, mining Garage's remaining
    # 54-row partial tier, the one the 17:1x PM check-in handed forward as
    # the single highest-ranked room, 27% uncovered). Two more word-overlap
    # collisions, checked against both harvests before excluding (CLAUDE.md
    # 5c/5d). "sports card storage ideas" lands on the Sports and Recreation
    # Zone purely because "sports" overlaps that zone's title; the zone's
    # own content.json ("Bikes on wall hooks," "One labeled bin per
    # activity," helmets, cleats) is about gear for sports a household
    # plays, not a collectible trading-card hobby. "organize tool adobe"
    # lands on the Hand Tool Wall and Cabinets zone on "tool" alone; "adobe"
    # names design software (Photoshop/Acrobat) or a construction material,
    # neither of which this site's pegboard-and-hand-tool zone addresses.
    # Checked against both harvests before adding: "card" appears in
    # exactly two rows total, this one and the genuine on-topic "card games
    # organizer storage" (Family Room's Board Game and Puzzle Zone, an
    # activity noun this exact phrase does not touch), so excluding the
    # two-word phrase here cannot suppress that match; "adobe" appears in
    # exactly the one row named here.
    r"\bsports cards?\b|\badobe\b|"
    # Same pass: "toolganize power tool organiser" is a single Bing-sourced
    # row (best_rank 21, seed "how to organize power tool storage") whose
    # unmatched word, "toolganize," is not an English word a page could
    # honestly carry; it reads as a scrape/autosuggest concatenation
    # glitch of "tool" and "organize," the same non-fixable-artifact shape
    # as this file's existing brand/platform exclusions, not a wording gap
    # a synonym could close. Checked against both harvests: "toolganize"
    # appears in exactly this one row, so excluding it here cannot
    # suppress a genuine match.
    r"\btoolganize\b|"
    # Found 2026-11-10, mining Kids Bedroom's single gap-tier row (the most
    # severe miss class, ranked above every room's partial tier). "building
    # beds for kids organization" (best_rank 12, seed "kids bedroom
    # organization ideas") drifted onto the kids-bedroom article purely on
    # the word "kids"; the unmatched words "beds"/"building" show it asks
    # how to construct a bed frame, a woodworking project, not how to
    # organize a bedroom the bed is already in. "how to organize a clothing
    # drive" and "organizing a clothing drive" (both seeded from "how to
    # organize safety gear") drifted onto the Clothing Closet zone purely on
    # "organize"/"clothing"; both ask how to run a charity clothing
    # collection event, not how to arrange clothes in storage, the same
    # donation/charity-event sense excluded for "garage sale" on 2026-11-10's
    # Garage pass. Checked against both harvests before adding: "building
    # bed(s)" and "clothing drive" each appear only in these three rows;
    # genuine on-topic rows ("how to organize clothing", "off season
    # clothing storage ideas", "seasonal clothing storage solutions") do not
    # contain "drive" and so cannot be touched by this phrase.
    r"\bbuilding\s+beds?\b|\bclothing\s+drive\b|"
    # Found 2026-11-10, mining Living Room's 12-row partial tier (the first
    # pass this room has had; every prior cycle mined Garage/Hall Closet
    # instead). "how to organize/organise a seating chart" lands on the
    # Sofa and Seating Zone purely on the word "seating"; a seating chart
    # is the event-planning sense (assigning named guests to numbered
    # seats at a wedding or banquet), not arranging the room's own
    # furniture, and content.json's purpose for this zone ("somewhere
    # every person in the house can sit down without first moving
    # something") never addresses assigning seats to guests. "how to
    # organize billy bookcase" lands on the Living Room deck purely on
    # "organize"/"bookcase"; Billy is IKEA's own bookcase product line
    # name, the same brand-name shape CLAUDE.md section 5 ("product
    # types, never brand names") already bars this site from chasing, and
    # the exact kind the "ikea"/"home depot" branch above excludes for
    # other rooms, just not spelled with the word "ikea" itself here.
    # Checked against both harvests before adding: "seating chart" appears
    # in exactly these two rows (organize/organise spellings) and "billy"
    # in exactly this one; the genuine on-topic rows ("how to organize a
    # bookcase", "how to organise bookcase", "how to arrange outdoor
    # seating", the whole outdoor-seating cluster on Patio or Deck) contain
    # neither phrase and cannot be touched.
    r"\bseating chart\b|\bbilly bookcase\b|"
    # Found 2026-11-10, mining Family Room's 21-row partial tier. "how to
    # organize a games night" lands on the Family Room deck purely on the
    # word "organize"; this is the event-planning sense (deciding who to
    # invite, what to play, what to serve for a games night), not storing
    # the games themselves, the same host-an-event shape "seating chart"
    # excludes above. The Board Game and Puzzle Zone's own content.json
    # purpose ("Store games and puzzles so that anything you pull off the
    # shelf is complete and playable tonight") is about keeping game
    # components intact in storage, never about planning the event itself.
    # Checked against both harvests before adding: "games night"/"game
    # night" appears in exactly this one row; the other low-coverage Family
    # Room row this same pass looked at, "how to organize stardew valley
    # board game" (a specific board-game title, the real on-topic shape
    # this zone already serves), does not contain the phrase and is left
    # alone as a genuine content gap, not excluded.
    r"\bgames? night\b|"
    # Same pass: "how to organise middle class room" and "how to organize
    # your room middle class" land on the Guest Bathroom deck purely on
    # "organize"/"room"; "middle class" is a socioeconomic descriptor with
    # no connection to a bathroom or any other room, and neither query names
    # a fixture, zone or activity this site addresses. Checked against both
    # harvests: "middle class" appears in exactly these two rows.
    r"\bmiddle class\b",
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
