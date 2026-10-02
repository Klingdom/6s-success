# 6S Success Current Operating Status

> Living operational state for Claude Code and all 6S Success autonomous agents.

## Document Role

`STATUS.md` is the fastest authoritative summary of **what is happening now**.

It is not a strategy document, backlog, changelog, incident archive, or analytics database.

Every agent performing meaningful autonomous work should read this file after `CLAUDE.md` and `AUTONOMY.md`.

Update this file whenever the material operating state changes.

---

# 0. Claim before you start, if more than one session is running

**Added 2026-09-29 after three collisions in a single afternoon.** Two
autonomous sessions independently built the same cross-zone
`diagnosed_reading()` precompute, wrote the same `forms_dead` increments into
`RISKS.md`, and then independently worked out the same rewording of the same
line in that file. Every one of those was correct work. All of it but the first
copy was waste, and the merges cost more than the fixes.

`BACKLOG-2026-09-07.md` B7 already says to claim a room before authoring it.
That rule was written for content and the collisions were not in content. It
applies to anything shared:

**For B9 (room decks) specifically, use `python ops/b9_claims.py --claim
"Room Name" --note "..."` (and `--release "Room Name"` when done), not a
hand-edited line below.** This section's own prose convention is what a
2026-09-29 cycle used to claim Nursery, minutes after a concurrent session
had already claimed it in `ops/b9-claims.json`: prose here does not check
`ops/b9-claims.json`, so it caught nothing, and a subagent spent real work
before the duplicate was found (`gate_b9_claims_current`'s own warning, not
this section, is what surfaced it). `ops/b9_claims.py --claim` reads that
same ledger and refuses outright if the room is already actively claimed by
someone else, so it is a real check, not just visibility. Still append a
line below too, for a human skimming this file, but treat the JSON ledger as
authoritative for B9 and check it (`python ops/b9_claims.py --status`)
before claiming a room here.

- a generator in `ops/`
- a gate in `ops/preflight.py`
- an operating document (`RISKS.md`, `STATUS.md`, `GOALS.md`, `OWNER-ACTIONS.md`)
- a workflow in `.github/workflows/`

**Before starting non-trivial work on one of those, append a line below.**
Delete it when the work lands. A stale claim is much cheaper than a duplicated
one: if a line here is older than a day and its work is in `main`, remove it.

This is a convention, not a lock. It cannot stop a collision on its own; it
makes one visible in the thirty seconds before the work starts, which is the
only moment it is cheap.

## Open claims

**Released 2026-10-01, scheduled operator cycle: Primary Bedroom, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/primary-bedroom-deck.json`: zone order, FAQPage JSON-LD vs visible copy, pricing, deck card count (66), diagnosis blocks and the Sort/Straighten/Shine/Safety/Standardize/Sustain order all agree. Full account in `ops/NIGHTLY-LOG.md` this date. This cycle's real find was in `ops/preflight.py` itself, not the site: see the same log entry.

**Released 2026-10-01: the content-level visitor read lane, Workshop, finished and logged, no content defect.** The cycle's real find was a live publish deadlock, not a content issue: see `ops/NIGHTLY-LOG.md` this date (`gate_publish_image_current`).

**Released 2026-10-01: the content-level visitor read lane, Living Room, finished and logged.** Found a real, sitewide defect in the process (see `ops/NIGHTLY-LOG.md` this date), not a Living Room-only issue.

**Released 2026-10-01, scheduled operator cycle: Garage, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 7 zones, deck) as a visitor: zone order, "Start here", the FAQ's own zone list, every `is-here` chip and numbered sibling list, the A7 storage-before-Sort position (`id="sort"` < `id="what-to-store-it-in"` < `id="straighten"`) and session-time claims all agree with each other and with `content.json`, on all 7 zones and the room page; the $9 Garage Pack's "42 printable cards" claim matches the real built PDF (`build/products/RP-GARAGE.html`, 42 numbered cards plus a standards sheet) exactly. The real find this cycle was in the generator's own comments, not the live page: see `ops/NIGHTLY-LOG.md` this date (the D5/`is_pilot` cohort-naming drift).

**Released 2026-10-01, scheduled operator cycle: Entryway, content-level visitor read lane, finished and logged. No live content defect.** Read all 7 pages (room, 5 zones, deck) as a visitor: zone order agreement, no false "in working order" claim, storage-before-Sort position, `rel="nofollow"` on every external link, FAQ/JSON-LD agreement and all 31 cross-links all checked and clean; `entryway-deck.html`'s 57-card claim verified by count. This closed the fourth consecutive clean room in this lane (Workshop, Garage, Entryway all found no page-level defect); confirmed the same cycle that the `ops/*.py` cold-read alternative is fully exhausted (`cold_read_ledger.py --next`: 191 of 191 files already ledgered, 0 un-ledgered candidates), so content-read stayed the only lane with real unread material left.

**Released 2026-10-01, later scheduled operator cycle: Pantry, content-level visitor read lane, finished and logged.** Read all 7 pages (room, 5 zones, deck) as a visitor, checked against `mcp/content.json` and `site/assets/js/data.js`: zone order, storage-before-Sort byte position, external-link `nofollow`, internal links, pricing (RP-PANTRY $9, PACK-HOUSE $19, CN-VIRTUAL $250, all current), the 57-card deck's own count, diagnosis blocks and the safety notice all checked clean. **The real find was sitewide, not Pantry-specific.** Every room page's FAQPage JSON-LD answer to "how long does it take" and the real visible "Added together..." paragraph a few hundred lines down are supposed to say the same thing; they did not, on all 20 room pages. The closing clause had drifted onto two different sentences ("so it does not have to be done in one go" in the structured data against "stopping after the first still leaves the room better than it was" in the visible copy) since a 2026-09-26 fix kept only the numbers in sync. None of the five prior content-read cycles caught it because room pages have no visible FAQ `<dl>` to diff against, unlike zone pages. Fixed at the source (`room_faq()` in `ops/build_zone_pages.py`, matched to the shipped visible copy rather than the other way round); `check_room_time_current()`/`gate_room_time_rounding_current` in `preflight.py` extended to check the closing clause matches on both copies, fail-then-pass proved directly against the real committed file. All 20 `site/rooms/*.html` regenerated (one line each), `ops/build_seo.py` rerun after to re-stamp `sitemap.xml`'s content hashes (the one step `build_zone_pages.py` does not chain), idempotency confirmed by a second regeneration producing byte-identical output. `ops/tests/test_gate_room_time_rounding_current.py` (9 cases) and `ops/tests/test_gate_sitemap_lastmod_current.py` (6 cases) both pass directly. No price or product touched; no new page.

**Released 2026-10-01, scheduled operator cycle: Dining Room, content-level visitor read lane, finished and logged. No live content defect.** Read all 7 pages (room, 5 zones, deck) as a visitor, checked against `mcp/content.json`, `content/manual/source/products.json` and `data.js`: zone order, FAQPage-vs-visible copy (re-confirmed the Pantry sitewide fix held here too), storage-before-Sort byte position (the Beverage or Coffee Station zone has no storage section at all, correct generator behaviour since none of its 14 kit items are in the Storage & Organization family, not a bug), external-link `nofollow`, internal links, pricing (RP-DINING-ROO $9, PACK-HOUSE $19, CN-VIRTUAL $250, five $4 zone packs, all current), the 61-card deck's own count against its real corpus, diagnosis blocks and the safety notice all checked clean. 0 em/en dashes.

**Released 2026-10-01, scheduled operator cycle: Family Room, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, delegated to an agent then independently re-verified directly rather than trusted: zone order agreement across the room page's JSON-LD ItemList, room-map tiles, zone-rows list and FAQ, and each zone's own `is-here` chip (all 6 agree: Primary Media, Toy and Play, Board Game and Puzzle, Blanket and Comfort, Charging and Device, Craft and Activity); storage-before-Sort byte order on all 6 zones (`id="sort"` before `id="what-to-store-it-in"` before `id="straighten"`); the room page's FAQPage JSON-LD "how long does it take" answer genuinely carries the 2026-10-01 sitewide fix (matches the visible notice paragraph, differing only by the word "below" that page context requires); every zone's visible FAQ `<dl>` matches its own JSON-LD word for word; 0 external links missing `rel="nofollow"` (independently re-checked by direct grep, 0 violations); all internal cross-links resolve; pricing (RP-FAMILY-ROO $9, PACK-HOUSE $19, CN-VIRTUAL $250, six $4 zone packs) matches `data.js` byte for byte (independently re-checked); the 69-card deck's claimed count matches `ops/cardtext/family-room-deck.json` exactly (independently recounted: `count` field 69, real `len(cards)` 69); diagnosis blocks match `mcp/content.json` on all 6 zones; safety notice identical wording on all 8 pages; 0 em/en dashes (independently re-checked with a direct Python scan after the agent's own grep-based check errored on regex syntax, not on the result); no "Set in Order."

**Released 2026-10-02, scheduled operator cycle: Guest Bedroom, content-level visitor read lane, finished and logged. No live content defect.** Read all 7 pages (room, 5 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/guest-bedroom-deck.json`: zone order agreement across the room page's JSON-LD ItemList, room-map tiles, zone-rows list, FAQ and each zone's own `is-here` chip (Bed and Linens, Nightstand, Dresser, Closet, Welcome and Work Surface, start-here Closet matching `content.json`'s GBR-001); FAQPage JSON-LD vs visible copy word for word on all 6 pages, including the 2026-10-01 sitewide "how long does it take" fix confirmed holding here (no page carries the old divergent "so it does not have to be done in one go" wording); storage-before-Sort byte order on all 5 zones (`id="sort"` before `id="what-to-store-it-in"` before `id="straighten"`); pricing (RP-GUEST-BEDR $9/30 cards, PACK-HOUSE $19, CN-VIRTUAL $250, five $4 zone packs) matches `data.js` exactly, Stripe buy-link URLs agree between zone pages and `data.js`; the 57-card deck count matches `ops/cardtext/guest-bedroom-deck.json`'s own `count` field and card-type budget; diagnosis blocks (friction/root-cause/six_s pass) match the deck JSON on all 5 zones; safety notice byte-identical to Family Room's; 0 external links missing `rel="nofollow"` (checked programmatically, including Stripe links); 0 em/en dashes (Unicode count, not just regex); no "Set in Order"; internal cross-links spot-checked resolve. One non-defect noted for awareness: the room page's "about 3 to 4.5 hours" total is not a naive min/max sum of the 5 session ranges, consistent with `gate_room_time_rounding_current`'s own governed rounding, not re-derived separately this cycle. Full `preflight.py` run clean after (every gate passed, 28 warnings, all standing sandbox limitations); unrelated to this room, that run started moments before a concurrent PM check-in's commits landed and `ops/preflight.py` itself gained an additive warning mid-run, so the result was treated as provisional for anything touching that warning, immaterial here since nothing in this room's read touched it.

**Released 2026-10-02, scheduled operator cycle: Kids Bedroom, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/kids-bedroom-deck.json`: zone order agreement across the room page's JSON-LD ItemList, room-map tiles, zone-rows list, FAQ and every zone's own `is-here` chip, matching `content.json`'s order (Bed and Sleep Zone, Toy Storage Zone, Study Desk, Clothing Closet, Dresser Drawers, School and Activity Launch Zone); FAQPage JSON-LD vs visible copy word for word on all 7 pages, the 2026-10-01 sitewide "how long does it take" fix confirmed holding; storage-before-Sort byte order on all 6 zones; pricing (RP-KIDS-BEDRO $9/36 cards, PACK-HOUSE $19, CN-VIRTUAL $250, six $4 zone packs) matches `data.js` exactly including every Stripe buy-link URL; the 69-card deck count matches `ops/cardtext/kids-bedroom-deck.json`'s own `count` field and card-type budget; diagnosis blocks match on all 6 zones; safety notice byte-identical to Guest Bedroom's; 0 external links missing `rel="nofollow"`; 0 em/en dashes (Unicode count); no "Set in Order"; internal cross-links spot-checked resolve. One thing investigated and confirmed NOT a defect, worth recording so nobody re-opens it: the deck's own card order puts Toy Storage Zone first, ahead of Bed and Sleep Zone, the reverse of every other page's order. `ops/cardtext/build_kids_bedroom_deck.py`'s own docstring states this is deliberate, following the room's own "Where to start" tip ("Clear the floor first, working out of the Toy Storage Zone"), and the deck page's own copy tells the reader why; not a cross-page order defect.

**Released 2026-10-02, scheduled operator cycle: Nursery, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/nursery-deck.json`: zone order agreement (Crib and Sleep Zone, Changing Station, Baby Clothing Zone, Feeding Station, Diaper and Care Backstock, Books and Quiet Play Zone) across every surface including the deck's own card order, no reordering here unlike Kids Bedroom; FAQPage JSON-LD vs visible copy word for word; storage-before-Sort byte order on all 6 zones; pricing (RP-NURSERY $9/36 cards, PACK-HOUSE $19, CN-VIRTUAL $250, six $4 zone packs) matches `data.js` exactly; the 66-card deck count matches `ops/cardtext/nursery-deck.json`'s own `count` field; diagnosis blocks match on all 6 zones; safety notice byte-identical to Kids Bedroom's and Guest Bedroom's, and separately read in full for any fabricated or unsupported infant-safety claim (CLAUDE.md section 8): none found, every claim (anchor furniture, remove drawstrings/button batteries, short cords set back, lower the crib mattress at the pull-to-stand milestone, nothing heavy on shelves above the crib, water away from electrical sockets) is standard guidance, not a statistic or a performance claim; 0 external links missing `rel="nofollow"`; 0 em/en dashes; no "Set in Order"; internal cross-links checked exhaustively, all resolve.

**Separately this cycle: `ops/preflight.py`'s own 2026-10-02 full run found a real FAIL on `site/articles/why-is-my-house-always-messy.html` (shipped 2026-10-01), fixed at the source.** `ops/build_messy_article.py`'s `chrome()` lifts its sibling template's `<head>` and strips its JSON-LD script tags, but left an empty, vestigial `<!-- CRUMBLD:BEGIN/END -->` comment marker pair behind, which `gate_breadcrumbs_current` correctly read as a breadcrumb that drifted to nothing even though the page's own `ld()` already carries a separate, correct, native BreadcrumbList. Fixed by stripping the marker pair alongside the JSON-LD it used to wrap, in the generator, not on the shipped page; regenerated. Two other FAILs the same preflight run surfaced on this page (a missing consult-CTA button, `RISKS.md`'s stale `forms_dead=214`) turned out to already be fixed on `origin/main` by a concurrent session by the time this cycle merged; see `ops/NIGHTLY-LOG.md` this date for the full account of that collision and how it was reconciled. All gates re-verified directly against the real functions and the relevant `ops/tests/*.py` files, all passing. Full `preflight.py` re-run in the background after; see `ops/NIGHTLY-LOG.md` this date for the result.

**Released 2026-10-02, scheduled operator cycle: Primary Bathroom, content-level visitor read lane, finished and logged. No live content defect.** Read all 9 pages (room, 7 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/primary-bathroom-deck.json`: zone order agreement across the room page's JSON-LD ItemList, room-map tiles, zone-rows list, FAQ and every zone's own `is-here` chip, matching `content.json`'s order (Vanity Counter, Vanity Drawers, Under-Sink Cabinet, Medicine Cabinet, Shower or Tub, Toilet Area, Linen and Towel Storage), the deck's own card order agreeing too; FAQPage JSON-LD vs visible copy word for word on all 7 zone pages, the 2026-10-01 sitewide "how long does it take" fix confirmed holding (the room page itself has no visible FAQ `<dl>`, matching the same template pattern Nursery and Kids Bedroom also use, not a defect here); storage-before-Sort byte order on all 7 zones; pricing (RP-PRIMARY-BA $9, PACK-HOUSE $19, CN-VIRTUAL $250, seven $4 zone packs) matches `data.js` exactly including every Stripe buy-link URL; the 76-card deck count matches `ops/cardtext/primary-bathroom-deck.json`'s own `count` field; diagnosis blocks match on all 7 zones; safety notice byte-identical to Kids Bedroom's, and the Medicine Cabinet zone's medication guidance separately read in full for any fabricated claim (CLAUDE.md section 8): none found, all standard guidance (read dates, pharmacy take-back, child-reach height, no mixing with bleach, prescriptions out of bathroom humidity); 0 external links missing `rel="nofollow"`; 0 em/en dashes (Unicode count); no "Set in Order"; 12 internal cross-links spot-checked, all resolve.

**Released 2026-10-02, scheduled operator cycle: Guest Bathroom, content-level visitor read lane, finished and logged. No live content defect.** Read all 7 pages (room, 5 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/guest-bathroom-deck.json`: zone order agreement (Guest Vanity Counter, Guest Vanity Storage, Shower or Tub, Toilet Area, Guest Linen Zone) across the room page's JSON-LD ItemList, room-map tiles, zone-rows, FAQ and every zone's own `is-here` chip, the deck's own card order agreeing too; FAQPage JSON-LD vs visible copy word for word on all 5 zone pages, the 2026-10-01 sitewide "how long does it take" fix confirmed holding; storage-before-Sort byte order on all 5 zones; pricing (RP-GUEST-BATH $9, PACK-HOUSE $19, CN-VIRTUAL $250, five $4 zone packs) matches `data.js` exactly including every Stripe buy-link URL; the 60-card deck count matches `ops/cardtext/guest-bathroom-deck.json`'s own `count` field (Room 1, Zone 5, Friction 15, Root Cause 16, Action 13, Standard 5, Event 5); diagnosis blocks match on all 5 zones; safety notice byte-identical to Primary Bathroom's; 118 external links checked programmatically, all carry `rel="nofollow noopener"`; 0 em/en dashes (literal Unicode count); no "Set in Order"; internal cross-links scripted against the filesystem across all 7 files, 0 unresolved.

**Released 2026-10-02, scheduled operator cycle: Laundry Room, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/laundry-room-deck.json`: zone order agreement (Washer and Dryer, Detergent and Treatment Zone, Sorting and Hamper Zone, Folding Surface, Hanging and Air-Dry Zone, Utility and Cleaning Zone) across every surface including the deck's own order; FAQPage JSON-LD vs visible copy word for word on all 6 zone pages, the 2026-10-01 sitewide "how long does it take" fix confirmed holding; storage-before-Sort byte order on all 6 zones; pricing (RP-LAUNDRY-RO $9, PACK-HOUSE $19, CN-VIRTUAL $250, six $4 zone packs) matches `data.js` exactly including every Stripe buy-link URL; the 67-card deck count matches `ops/cardtext/laundry-room-deck.json`'s own `count` field and card-type budget; diagnosis blocks match on all 6 zones; safety notice byte-identical to Guest Bathroom's, and the Detergent and Treatment Zone / Utility and Cleaning Zone content separately checked for a fabricated safety statistic given the laundry chemicals involved: none found, all qualitative guidance; 110 external links all `rel="nofollow noopener"`; 0 em/en dashes; no "Set in Order"; 464 internal cross-links checked programmatically, all resolve.

**Released 2026-10-02, scheduled operator cycle: Home Office, content-level visitor read lane, finished and logged. No live content defect.** Read all 8 pages (room, 6 zones, deck) as a visitor, delegated to an agent, cross-checked against `mcp/content.json`, `site/assets/js/data.js` and `ops/cardtext/home-office-deck.json`: zone order agreement (Primary Desk, Desk Drawers and Pedestal, File Storage, Bookshelf and Reference Zone, Printer and Scanning Station, Supply Cabinet) across every surface, the deck's own zone-grouped card order confirmed the same established pattern as Laundry Room's, not a defect; FAQPage JSON-LD vs visible copy word for word on all 6 zone pages, the 2026-10-01 sitewide "how long does it take" fix confirmed holding; storage-before-Sort byte order on all 6 zones; pricing (RP-HOME-OFFIC $9, PACK-HOUSE $19, CN-VIRTUAL $250, six $4 zone packs) matches `data.js` exactly including every Stripe buy-link URL; the 66-card deck count matches `ops/cardtext/home-office-deck.json`'s own `count` field and id set exactly; diagnosis blocks spot-checked against two zones match; safety notice byte-identical to Laundry Room's; all external links `rel="nofollow noopener"`; 0 em/en dashes (literal Unicode count); no "Set in Order"; all internal cross-links resolve. The room page's own "4.5 to 7 hours" total was sanity-checked against the 6 zones' summed session ranges and found consistent with the same half-hour rounding convention already confirmed on Laundry Room, not a new finding.

**NEXT FOR THE OPERATOR: Mudroom, content-level visitor read lane.** Kitchen, Living Room, Workshop, Garage, Entryway, Pantry, Dining Room, Family Room, Primary Bedroom, Guest Bedroom, Kids Bedroom, Nursery, Primary Bathroom, Guest Bathroom, Laundry Room and Home Office are now read; Mudroom, Hall Closet, Stair Landing and Patio or Deck are not.

**B9 is done: all 20 rooms now have a diagnosis layer
and a deck.** Patio or Deck (`site/patio-or-deck-deck.html`) and Workshop
(`site/workshop-deck.html`) were the last two, built by two concurrent
sessions in parallel with no collision (different rooms), both claims
released via `ops/b9_claims.py --release`; see `ops/b9-claims.json` for the
full ledger. Primary Bedroom's claim shipped and released the same way just
before. **Correction, 2026-09-29 PM check-in: this line's own "B8" pointer was
stale.** `DECISIONS.md` D-027 closed B8 on 2026-09-25 (print-tier alignment
deferred until a room actually goes to print); `BACKLOG-2026-09-07.md`'s own
B8 row already says CLOSED. Epics 1-4 (`BACKLOG-2026-09-07.md` sections 2-4,
A1-A10/B1-B9/C1-C7) are also all done or Phil-gated, confirmed by reading
every row, not by re-citing the prior stale pointer. No BACKLOG "Now" item
is currently unblocked: section 5 is Hold pending traffic/evidence, section 6
is Phil's own owner gates, and all 8 open GitHub issues are `decision`/
`blocked-on-art`. The standing fallback several recent cycles have used in
this exact state, per `CLAUDE.md` 0.2, is independent re-verification plus a
cold-read of a low-mention `ops/*.py` file for a real, fixable defect.

**2026-09-30, later scheduled operator cycle: closed, no line left open.**
Cold-read `build_social_captions.py`, `build_social_pins.py` and
`build_youtube_metadata.py`, no defect in any of the three; found and fixed a
real one in `build_thumbnails.py` (see `ops/NIGHTLY-LOG.md` this date, and
`ops/cold-read-ledger.json`). Full `preflight.py` ran clean both before and
after the fix, 25 warnings, all standing sandbox limitations.

# 1. Status Metadata

**OPEN LOOP AT THE END OF THIS CYCLE, 2026-10-01: production is still serving build `f8e760d9a6da6239` and none of today's work is live.** `/articles/why-is-my-house-always-messy` returns 404 on the real site; the room artwork is not deployed. This is not a claim that it shipped, and it is the first thing the next session should close.

**Why, precisely.** `ops/deploy.py` was run and refused to report success, correctly: no published image covers these commits yet. The image builds are the bottleneck, they take 22 to 25 minutes each, several were queued at once, and **three of the recent ones failed outright** on gates rather than on the build. Those gate failures have been fixed and verified clean at HEAD (`gate_consult_cta_current`, `gate_risks_evidence_current`, `gate_build_id_current`, `gate_feed_current`, `gate_llms_txt_current`, `gate_sitemap_lastmod_current`), so the queued build for `9415d6ae4` is expected to pass, but expected is not verified.

**Nothing will deploy on its own.** `.github/workflows/deploy.yml` still finds no `VPS_DEPLOY_KEY` secret and exits without touching production, which is `OWNER-ACTIONS.md` item 0. A background watcher had been set to deploy the moment the builds settled; **it was killed by the host for low memory, along with a full `preflight.py` run that never finished.** So the next session with the key should: confirm the publish-image run for `9415d6ae4` (or later) is green, run `python ops/deploy.py`, then check the three URLs above return 200 and that the live `build-id.txt` matches the repository.

**Also killed mid-run and therefore NOT a result:** the full `preflight.py` on HEAD. It reached `gate_tests` and was stopped, so this cycle has no clean full-preflight run to cite. Individual gates were run directly and are recorded above; that is weaker evidence and is deliberately not described as a preflight pass. Two stray probe files it left in `site/` (`_site_js_wrapper_8.html`, `rooms/_site_js_probe_8.html`) were found and removed, and the three files git reported modified afterwards were byte-compared: all three are CRLF-versus-LF representations of identical content, not edits, so no killed test left a planted defect behind.

**Last Updated:** Scheduled operator cycle, 2026-10-02: **shipped the complaint-cluster article `BACKLOG-2026-09-07.md` A11 named as the highest-value unfinished work, closing the content half of `LRN-0029`.** `site/articles/why-is-my-house-always-messy.html` answers the kitchen, bedroom, kids' room and closet "why is my X always messy" variants directly, grounded only in the existing 17-cause vocabulary (`ops/root_causes.py`), cross-linked to the real room/zone pages, FAQPage JSON-LD verified word for word against the visible FAQ, added to the articles index and reciprocally linked from the three closest existing articles so it is not an orphan. `ops/build_seo.py` (sitemap 211 URLs) and `ops/build_feed.py` (30 entries) rerun; `audit_pages.py`, `check_urls.py` (211/211), `fix_dashes.py`, `affiliate.py --check` and `audit_visual.py --all` (219 pages) all clean after. **Two of A11's four accept criteria are not claimed done, both for lack of network egress from this sandbox:** `ops/indexnow.py --submit` refused to submit rather than guess, since it could not reach the live site to confirm the key file is served; a `keyword_demand.py` re-harvest to confirm the query moves off `gap` needs reach to Google's/Bing's autocomplete endpoints, which this sandbox also does not have (confirmed directly: both attempts refused by the proxy, not assumed from the earlier Search Console finding). Both are mechanical from a session with live network reach. Earlier the same cycle: the standing Guest Bedroom content-read handoff was finished and logged clean (no live content defect), released in favour of this higher-priority item per the ordering rule once a concurrent owner-directed cycle's merge surfaced it. Full account in `ops/NIGHTLY-LOG.md` this date.

**Last Updated:** Owner-directed cycle, 2026-10-01: **measured demand for the first time, then went and looked at the artwork, which found a defect in the paid product and eleven pages of pictures nobody had collected.**

**1. Half of "we cannot see queries" was never blocked on Phil.** `GOALS.md` had said for a month that impressions and queries need Search Console. Search Console is the only source for OUR impressions, and that stands. What people TYPE is public: Google and Bing answer their autocomplete endpoints with no key, no account and no referrer check, and nothing here had ever asked them. Every search term this site targets was invented by reading the Micro Zone Manual. `ops/keyword_demand.py` (new, 14/14, fail-then-pass proved against four planted defects) harvested 2,622 distinct queries from 137 corpus-built seeds, 274 attempts, 0 errors, both canaries clean. **346 covered, 1,562 partial, 714 with nothing of ours titled for them.** The finding to act on: the complaint cluster, how somebody searches before deciding that organising is the answer, is 49 queries and **zero** covered, and "why is my kitchen always messy" and "why is my bedroom always messy" are rank-1 suggestions. That is the one question 17 root causes and 114 diagnosed zones exist to answer. Also 0 covered: "small space" (153 queries) and "cheap, budget, DIY" (98). `BACKLOG-2026-09-07.md` A11 carries the page that answers it, and it is the highest-value unfinished work in this repository right now. **LRN-0029.**

**Indexation, half answered and half honestly unchecked.** One DuckDuckGo read of `site:6s-success.com` returned ten real pages of ours, so "not indexed at all" is FALSE for the Bing-derived index and the diagnosis there is indexed-and-not-ranking. Three follow-up queries for which SECTIONS are indexed were refused HTTP 202 after an earlier burst earned a block, so that is UNCHECKED, and nothing about Google's index was measured at all.

**2. Six book chapters drew their own room under the laundry room's name.** Found by rendering the artwork and reading it. Chapters 44 to 49 each carried, as the visible heading of their zone map, "The laundry room, drawn as its six zones". Chapter 43 IS the Laundry Room. The others are the Home Office, Garage, Workshop, Mudroom, Hall Closet and Stair Landing, and each drew its own zones correctly underneath, so chapter 45 announced a laundry room over seven garage zones and chapter 49 announced six zones over three. The strapline, "and five of them wait on the machines", is about a washer and a dryer and was sitting in a garage and a hall closet. Nothing could have caught it: in all twenty chapters the aria-label, the figcaption and the count of numbered zones were right. Only the two visible strings were copied. It was also an accessibility defect pointing the unusual way, since the screen-reader user was told the truth and the sighted reader was not. 12 files corrected in both packaged copies, deriving room and count from each figure's own aria-label so nothing new is asserted. `ops/tests/test_book_zone_map_strings.py`, 32 of 32, fail-then-pass proved three ways.

**3. Eleven room pages had artwork sitting in the book nobody had gone to get.** Those eleven carried a typographic panel instead of a picture. Rendering `garage.html` showed the panel's text is the same paragraph as the "Start here." callout below it, with the lede saying it a third time: the page made one point three times and called the third one a figure. Each of those chapters already held a finished hand-drawn overhead plan of the room as its numbered zones. `ops/import_room_diagrams.py` imports it and refuses more than it accepts: the drawing's accessible name must name the room, its zone count must match `content.json`, it must be self-contained, carry no fixed width, carry no colliding id, and must not call itself a photograph (chapter 50 does call one of these cards "the left-hand photograph", which is the author's voice about a photo the reader takes and is not ours to rewrite, but it must not reach the site). **All 20 room pages now lead on real artwork and zero carry a panel.** Mobile was measured rather than assumed: at 390px the labels rendered near 6px, a media query lifts them 1.4x without touching the imported artwork, and `ops/tests/test_room_diagram_fits.py` measures every label's real `getBBox` against its own box in a browser at 390px and 1200px (22 measurements, all fit, fail-then-pass proved at 34px).

**4. A test in the suite was passing for the wrong reason, which was worse than the one red line it produced.** `test_run_preflight_exit_code.py` drives the real `run_preflight.sh` through `subprocess` `bash`, and from Python on this machine `bash` resolves to Windows' own `System32/bash.exe`, the WSL launcher, which refuses every invocation and exits 1. Two of its three dynamic cases assert exit code 1, so both were passing, and would have passed against a `run_preflight.sh` deleted from disk, inside the one file written to catch a wrapper that reports success on a real failure. It now round-trips a probe string through its interpreter and probes up front for the tools the wrapper needs (Git Bash ships `nohup` but not `setsid`), reporting NOT VERIFIED rather than FAIL when it cannot execute. The one case still meaningful here, a static read of the committed wrapper, was proved to bite by planting the exact 2026-09-30 regression back in. **LRN-0030.**

**Also corrected in `ops/wire_zone_heroes.py`**, which still serves the three zone pages with a rejected hero: its 34px headline slot was filled with the zone name, empty for a room lead, so eleven panels shipped an empty `<text class="z">`; and `_wrap(done, 46)[:6]` cut three live panels mid-clause with no signal, so `garage.html` ended "The slab comes last, once the wall".

**5. Then acted on finding 1 the same day, and collided with another session doing the same thing.** `/articles/why-is-my-house-always-messy` shipped: 2,694 words, generated from `ops/root_causes.py` and registered in `GENERATOR_OWNERSHIP_CHAIN` so its seven causes and thirty-second tests cannot drift from the vocabulary sixteen decks and 114 zone pages use. One page rather than eight, with the kitchen, bedroom, kids' room and closet versions answered on it, because the answer to all four is the same diagnosis with a different example. **A concurrent session independently wrote the same article from the same data a few hours apart, at the same slug, and pushed first.** Resolved to one page, not two: this version kept as the base (the seven causes with their tests were not in theirs, and it is generator-owned), with the one thing theirs did better ported in, its FAQ worded as the exact harvested phrases rather than paraphrases. That port then created a defect of its own, four FAQ answers that restated the room sections above them, which is the same duplication this cycle spent the morning removing from eleven room pages; tightened to summaries, 10 entries to 9, and all 9 verified present in the page's visible text. **LRN-0031** records the real lesson: publishing an unclaimed gap to a shared main is publishing a job, and `STATUS.md` section 0's claim rule is written for when work starts rather than when a finding is published.

**6. Then the instrument from finding 1 turned out to be measuring something narrower than it was being read as, and that correction is bigger than the finding.** It scored a query against page TITLES only, so a page that answers a question properly under its own `<h2>` read as a gap. Reading headings as well moves the whole corpus from **714 gaps to 226 before this cycle wrote anything**, and the complaint cluster from 0 covered to 8. Decomposed three ways rather than argued: titles-only before the article, gap 714 / covered 346 (cluster 21 / 0); headings too, still before the article, gap 226 / covered 970 (cluster 3 / 8); headings too, with the article, gap 223 / covered 982 (cluster 1 / 17). So the article is a real addition, 8 covered to 17, and "49 queries and zero covered" was partly my own scorer, after it had been written into `GOALS.md` as evidence strong enough to choose work from. **What stopped it being expensive was writing one page instead of eight**: eight per-room pages would have been thin pages built on a number that was mostly measurement error, and `CLAUDE.md` section 11 is the only reason that did not happen. The two scores are now kept apart rather than merged, `coverage` stays title-only so it remains comparable with the first reading, and `matched_on` says which surface earned each row. Three planted defects proved the new cases bite, including the one that merges the scores and the one that makes everything match. **LRN-0029 corrected in place.**

**Verified, not assumed:** `audit_pages` clean, 0 duplicate titles or descriptions; `check_urls` 210 of 210; `fingerprint_assets` 652 references across 218 pages current; `fix_dashes` clean; generator idempotent (two consecutive builds byte-identical); every new and changed test fail-then-pass proved against planted defects and every planted file restored byte-identical. **One thing deliberately left unchecked:** the deploy ran but production is still serving the previous build, because the image build covering this commit was still running; `ops/deploy.py` refused to report success and said so, and the redeploy is the open loop at the end of this cycle rather than a claim.

**Last Updated:** Scheduled operator cycle, 2026-10-01: **the content-read lane's Living Room pass found a real, sitewide trust defect, not a Living Room oddity.** The room page's own numbered zone map, h2, figcaption and meta description all called the zone list "in working order" directly above a "Start here" notice naming a different zone (the LAST one in that list). Checked against `mcp/content.json` across all 20 rooms before treating this as sitewide: 18 of 20 disagree. The same false claim shipped on all 114 zone pages, all 20 room decks (the card corpus' own ROOM CARD text went further, stating outright "This card is the map and the order."), the printable Micro Zone Map download, `resources.html` and two hand-authored articles; `consulting.html`'s own identical-sounding claim is a real, human-determined, paid-deliverable promise and was correctly left alone.

Fixed at the source across 9 generator files (including `build_seo.py`'s own duplicate copy of the `resources.html` description, a second source of truth that would have silently reverted a source-only fix) plus 20 cardtext sources and one hand-authored article and one hand-authored image `alt` text; ran the full 39-generator `GENERATOR_OWNERSHIP_CHAIN` to regenerate all 189 affected files, proved idempotent on a second run. New `gate_no_false_zone_order_claim` in `preflight.py`, proved to fail by planting the exact regression back into a real committed file, new `ops/tests/test_gate_no_false_zone_order_claim.py` (6 cases) fail-then-pass proved directly. `check_urls.py` 210/210, `audit_pages.py` 214/0, `fix_dashes.py --check` 0/0, `affiliate.py --check` clean (165 documents). Full account in `ops/NIGHTLY-LOG.md` this date.

**Prior (Scheduled operator cycle, 2026-09-30, overnight, second stretch): spent the cycle on the measurement layer, after four instruments turned out to be reporting correct numbers about the wrong population.** None was broken, which is why all four had survived: each passed its own checks and returned a plausible figure, and a plausible figure is worse than a missing one because nobody investigates it. Recorded as **LRN-0026**.

**1. 420 payment links were followable, so crawling this site opened checkouts.** Went looking for a dead checkout (11 `buy-click` events from 9 visitors, one sale ever, the shape that once cost this site eight days of $0). The checkout was fine: `gate_live_links`, `gate_stripe_link_dedup`, `gate_stripe_orphan_link_active` and `gate_stripe_price_claims` all clean against the real account with a real key. The session list showed 12 Checkout Sessions created on 2026-09-15, a day the site recorded **zero** buy-clicks. A Stripe Payment Link opens a session when its page is merely opened, and 420 `<a>` tags across 171 pages carried `rel="noopener"` with no `nofollow`; the shop alone had 126. Fixed at ten emission points so regeneration reproduces it, verified by running all 45 generators and re-counting (420 of 420), deployed, confirmed live. The cost was not crawl budget: "sessions created versus paid" is the only conversion instrument here that does not need Search Console, and it was full of rows nothing could attribute. `gate_payment_links_nofollow`, 8/8 tests.

**2. Our own monitoring made 94% of the redirects in the only SEO log we have.** The three most requested paths on the entire site were ours and all 301s: `deploy_freshness.py` built its probe URL from the local filename and asked for the `.html` form of a zone page about twelve times an hour (2,270 in eight days). `urllib` follows a 301, so every check passed. While Search Console is unverified the access log is the only instrument for whether search engines read this site, and "Googlebot: 36 redirected" could not be read as a number about Googlebot. `gate_no_redirecting_probe_urls`, 7/7 tests.

**3. 77% of all traffic is this repository, and the crawl report called it human.** Of 75,590 requests over eight days, 58,247 were ours (`6s-freshness` 16,441, the healthcheck's wget 8,746, `6s-linkcheck` 3,721, `6s-dashboard` 2,970, `6s-success-indexnow` 1,803). None matched the classifier, so all counted as "human or unknown", the bucket a reader most easily mistakes for an audience: it printed 78,295 against a measured 48 real visitors. Now 58,247 own tooling and 13,986 human or unknown. 6/6 tests, including that the anchored pattern cannot claim a stranger's agent or shadow a real crawler.

**4. Every link this business publishes off-site needed a redirect.** All 114 YouTube descriptions (228 links) and all 114 social captions used the `.html` form. Fixed at both generators before Phil hand-uploads 102 more descriptions rather than after; all 570 generated links verified to resolve to a zone page that exists, by set comparison rather than sampling. `gate_published_zone_urls`, 7/7 tests. The concurrent session independently reached the same conclusion and updated its own `#sustain` gate to match; reconciled, CI green.

**The finding that should change what Phil does next.** The 12 published videos have sent this site **zero** visitors. From the all-time referrer table, every arrival ever: direct 79, linkedin.com 11 plus com.linkedin.android 1, go.bsky.app 3 plus bsky.app 2, google.com 3, bing.com 1. **youtube.com does not appear at all**, 26 days after the 12 went up. That measures referrals and not watching, and the two call for opposite work, so `OWNER-ACTIONS.md` item 1 now asks for a two-minute look at YouTube Studio **before** the 102 manual uploads it was requesting. LinkedIn (12 visitors) and Bluesky (5) are the only channels that have ever produced one, against 4 from every search engine combined.

**A false claim about production, inside the file that runs every gate.** `gate_mcp_corpus_current`'s docstring said "the live server (deployed 2026-08-31, watchtower-updated on push) was answering real MCP queries". Checked over ssh: there is no `6s-mcp` container running or stopped, port 8974 is not listening, the image was not even on the host, and no file names an endpoint a client could reach. It has never run. Corrected in place. Not deployed autonomously: with no route and no client it would convert "not deployed" into "deployed and still unused", and the only reason to run it is to expose it, which puts a new unauthenticated service on a VPS also carrying Ledgerium AI and Compassion Benchmark. **D-028** and `OWNER-ACTIONS.md` item 21 carry the decision, the measured capacity (4.4 GB free, port unused, image already pulled to the host) and the two commands for yes, plus an explicit offer to retire `mcp/` entirely for no.

**Also this stretch:** deployed the Patio or Deck page, which was in the repo and in the sitemap while production 404'd it, then verified all 21 sitemap deck pages serve 200 and announced it to IndexNow. Five technical explanations for the organic flatline tested and all five clean (crawled, crawlable, no self-inflicted redirects, correctly cached, sitemap honest), which is what makes Search Console the remaining instrument rather than more building. Tested the Search Console path rather than claiming it: dummy token in, tag really lands in `index.html` only, token out, tree byte-identical after; that test falsely bumped the homepage `lastmod`, which was restored rather than shipped.

**Verified, not assumed:** four new gates and five new test files (37 cases), every one fail-then-pass proved against the real tree; `check_urls` 210/210; `audit_pages` clean; `fix_dashes` 0/0; `link_graph_report` 0 orphans; production healthy and current. **One thing deliberately left unchecked:** the Listmonk subscriber count could not be re-measured (reading the container's environment was correctly refused as a credential risk, and no repository tool does it safely), so the standing "0 subscribers" figure is carried forward rather than confirmed.

**Prior (Scheduled operator cycle, 2026-09-30): attached clean (unshallowed, fast-forwarded 1140 commits onto `origin/main`), working tree clean. Confirmed independently (own read plus a delegated subagent's separate read) that no `BACKLOG-2026-09-07.md` "Now" item is unblocked and no open GitHub issue is Phil-unblocked, matching every recent cycle's own finding. Ran a full `python ops/preflight.py` (via subagent, ~9 minutes, no hang this run): every gate passed, 26 warnings, 25 of them standing/already-tracked. **The one new warning was real:** `status-deploy-verdict-current` flagged that this file's Public website / Production traceability rows and the Production Knowledge paragraph all still cited the superseded build `72f0b37c784c7b60`/commit `295ad54f9` (2026-09-29T20:29:14Z), while `ops/deploy-verdict.json` had moved to build `14089d51f264597d`, `checked_at: 2026-09-30T00:01:56Z`. Fixed once, then **fixed again in the same cycle**: before the first fix could be pushed, Phil's own concurrent commit (`8998cd048`) redeployed once more, closing that gap too. Every citation now reflects the actual current state, verified directly rather than cited: `ops/deploy-verdict.json` records build `1db1621639e93437`, `checked_at: 2026-09-30T01:06:56Z`, resolving via `resolve_verdict_commit()` to `9ddddd197` (Phil's own `nofollow` fix on all 420 `buy.stripe.com` links, the likely explanation for `GOALS.md`'s "12 sessions, zero buy-clicks" finding); `deploy_gap_material_commits('9ddddd197')` returns empty, so production matches `HEAD` exactly, zero gap. Both gate functions (`status_deploy_verdict_problem`, `deploy_gap_count_problem`) re-run directly against the final edited file: both return `''`. This is the standard "source corrected, artifact not re-derived" shape `CLAUDE.md` section 7 calls dominant, caught by the gate exactly as designed twice over in one cycle; no new gate needed. No price or product touched, no site page changed, `IndexNow` not applicable (no new/changed page).

**The find of the cycle was a live content defect nothing could have caught.** Reading one rendered page out loud surfaced that KC-008 MISSING STANDARD's confirmation test read *"Ask two people what this surface should look like at bedtime"*, and it was **live on 100 pages**: 84 zone pages and all 17 deck pages, including every garage, pantry, workshop and kitchen page. Confirmed against production, not the repository: `garage-deck.html` and `pantry-deck.html` were both serving it at the time of writing. No existing check could have found it, because `ops/root_causes.py` is the single shared vocabulary, 16 of the 17 deck sources are generated from it, and all of them agreed with it and with each other. The text was perfectly consistent everywhere and wrong everywhere. Rewrote it zone-neutral, regenerated, 101 pages corrected; the Kitchen pilot deliberately keeps its own kitchen voice. New `gate_cause_vocabulary` + `ops/tests/test_cause_vocabulary.py` (11/11) hold the two rules that are actually true: generated copies must match their generator, and text shared across twenty rooms must not name one room. One case restores the exact wording and asserts the real tree fails on it. **LRN-0023.**

**Also corrected:** `ops/root_causes.py`'s docstring claimed its first 12 causes were "copied character-for-character" from the Kitchen deck. Checked: false for 7 of 12, and rightly so: the pilot speaks in a kitchen voice while the shared model must speak to every room. A comment asserting an invariant nothing enforced; the gate now holds the real split and the docstring says what is true. Two learnings had also collided on id **LRN-0021** (this session's and a concurrent one's); renumbered one to LRN-0022 so both stay citeable.

**Five flaky tests repaired, not worked around.** `test_gate_kitchen_deck_current.py` failed on a file `cmp` proved byte-identical to HEAD: five gate tests asserted worktree cleanliness with `git status --porcelain`, whose stat cache calls a file modified the moment a generator rewrites it with identical bytes. `preflight.worktree_changes()` has documented that exact trap since the day it reported 186 phantom files; the tests never adopted it. New `ops/tests/_worktree.py` and all five switched to content comparison, because the cache lies in both directions, so the assertions that a file *was* left modified were passing for free too.

**A sixth collision with a concurrent session, and a new failure mode.** Both sessions authored Primary Bedroom simultaneously; theirs landed first, with a 66-card deck and page. **Discarded this cycle's own diagnosis rather than push a duplicate or fight the merge**, after verifying theirs directly (18 frictions, 54 branches, 14 causes), and ported forward only what was genuinely additive: **capacity and variants for all six zones**, which theirs did not have and which only 7 of 20 rooms now carry. Worse than the duplication: the other session is running generators and `git` operations in this same working directory, which produced six test failures that every one of them passed in isolation afterwards, and killed one generator outright with an OSError writing a page the other session was writing at the same moment. Recorded as **RISK-0014**, with the cheap structural fix named: `git worktree add` gives each session its own checkout and needs no repository change. **One piece of that evidence was withdrawn on inspection:** a file this cycle created did vanish, and the other session was blamed for it in the first draft of that risk. It was not them. `ops/tests/_worktree.py` matched `.gitignore`'s `ops/tests/_*` rule for scratch fixtures, so it was never tracked, `git add -A` silently skipped it, and CI failed on the import. Renamed to `ops/tests/worktree_state.py`, which is the convention the rule exists to protect rather than an exception carved into it. Local validation cannot be trusted while that is true, so CI on a clean checkout is the authority for this commit. **LRN-0024** records the other trap this exposed: reading the line-ending convention off the working copy is wrong under `core.autocrlf`, and it silently rewrote 1,300 lines across five files before `--numstat` caught it.

**Verified, not assumed:** generator chain (43 generators) clean; `mcp/content.json` byte-identical to the manual source; all 17 derived deck sources regenerated from their own builders; `check_urls.py` 208/208; `audit_pages.py` clean; `fix_dashes.py --check` 0/0; `link_graph_report.py` 0 orphans, 114/114 zones reachable; every test that failed in the shared-tree run re-run individually and passing. Corpus now 102 of 114 zones diagnosed; Workshop and Patio or Deck are claimed by the concurrent session and were deliberately left alone.

**Prior (Scheduled operator cycle, 2026-09-29): started by fixing the two preflight FAILs a PM check-in had handed off (`gate_diagnosis_rendered`, `gate_general_reading_differentiated`), then discovered mid-work that a concurrent session and Phil himself had already fixed both, with a more complete algorithmic solution (`diagnosed_reading()`, giving the diagnosed-zone pool the same uniqueness-and-ceiling guarantees `general_reading()` already had for the non-diagnosed pool, plus a proportional inbound-link ceiling instead of a fixed count) already merged and reconciled through two rounds of "two sessions solved the same problem" merges. **Discarded this cycle's own conflicting fix rather than push a duplicate or fight the merge**, matching this file's own established practice for exactly this shape of collision: verified the already-shipped version directly (both gates re-run clean against the real corpus) before adopting it, deleted this cycle's own now-incompatible test file. With that item already closed, picked BACKLOG's B9 (room decks): claimed Kids Bedroom (the standing claim from 12:55 had passed the 3-hour staleness window with no deck shipped), delegated the build to a subagent following the Mudroom reference pattern, independently re-verified before commit. New diagnosis layer for all six Kids Bedroom zones (18 frictions, 54 branches, all 17 shared root causes reachable, tying the best of any room so far), every branch grounded in the zone's own already-published text (a strangling cord at a sleeping child's neck height, a choke-sized toy part, an unanchored dresser a child climbs, a backpack carrying daily medication), new `ops/cardtext/build_kids_bedroom_deck.py` (69 cards) and `ops/build_kids_bedroom_deck_page.py`, shipped `site/kids-bedroom-deck.html`. **Verified, not assumed:** re-ran the two new gates and the two originally-red gates directly (0 problems, all four); `mcp/content.json` byte-identical; `build_zone_pages.py`/the two new generators confirmed idempotent; the dedicated test (6/6, fail-then-pass proved on the real committed files); `check_urls.py` (206/206), `audit_pages.py` (210/0), `affiliate.py --check` (165 documents), `fix_dashes.py --check` (0/0). One real gap the subagent's own pass caught and fixed: the new page was initially missing from `site/sitemap.xml` until `ops/build_seo.py` reran. No price or product touched; one new free page. Dashboard regenerated per step 11b.

**Older entries (88 of them, 2026-08 to 2026-09-29) live in `STATUS-ARCHIVE.md`.** Most recently added this cycle, moving the oldest of what would otherwise have been a five-entry stack there (the Guest Bathroom entry) to keep this stack at four (the same rotation practice this file has followed since 2026-09-17): the oldest archived each time a new one is added rather than left to grow unread. Nothing is deleted, and the gates that scan this file for stale claims (`gate_no_stale_session_label`, `gate_no_stale_checkout_count`, `gate_no_stale_listmonk_blocker`, `gate_corporate_buy_path_current`, `gate_critical_risks_escalated`) scan the archive too, so an archived claim is no less checked than a current one.

# 2. Executive Snapshot

## Current Objective

The money path now works well enough to test. The constraint has moved again,
from "can a customer pay" to "can anything be measured, and has a stranger
ever converted". `ROADMAP-2026-2029.md` (written 2026-08-24) is the current
authoritative strategy; it supersedes `ROADMAP.md`, `STRATEGY.md` and
`GROWTH-PLAN.md` in spirit even though those files still exist on disk.
`BACKLOG-2026-09-07.md` is the current authoritative work queue. **Corrected
2026-09-23: this line still named `BACKLOG-2026-H2.md` here, fifteen days
after section 21 below recorded that `BACKLOG-2026-09-07.md`, Phil's own
reprioritisation toward micro zones, decks and image/video work, supersedes
`BACKLOG-2026-H2.md`'s ordering.** `BACKLOG-2026-H2.md` still holds the
process rules (epics, gating discipline) and `BACKLOG.md` is superseded by
both.

Standing objective from the owner (2026-08-16): develop all content and products
continuously and iteratively toward $20,000 per month, without stopping for
approval, while keeping this file and the executive dashboard current enough to
be read at a glance each morning.

**The honest arithmetic, from `ROADMAP-2026-2029.md`:** the digital catalogue
cannot reach $20,000 a month on any reachable traffic (the $19 item alone needs
roughly a quarter million visits a month). Services (In-Home Reset Day at
$1,200) reach the number on far fewer bookings but consume Phil's own hours and
have not been demand-tested beyond one referral. Horizon 1 (now through August
2027) is about proving a stranger converts at all, with an honest revenue
target of $500 to $3,000 a month by month twelve, not $20,000.

## Current Business Goal

Build a trusted 6S Success digital business that helps customers improve rooms and micro-zones through desired-function discovery, root-cause diagnosis, quests, standards, products, and sustainment.

Long-term commercial target:

**$20,000+ monthly revenue**, pursued through real customer value rather than artificial activity or deceptive conversion tactics.

## Current Highest-Level Priority

**The ordering rule, from `BACKLOG-2026-09-07.md` section 0: the traffic
constraint decides the order.** Below it, the older rule still holds:
measurement before traffic, traffic before conversion, conversion before
product. Current state against each epic:

1. **Epic 1, measurement (blocks everything).** EXP-001 (has a stranger ever
   clicked a buy button) is answered, permanently: AMBIGUOUS (backlog 1.3,
   closed 2026-09-03). EXP-002 (does anyone reach the offer on a zone page)
   is still collecting scroll-depth data. Umami read access is partly done:
   Phil read the database directly 2026-09-02 and recorded a one-time
   baseline in `GOALS.md`, but no environment this operator runs in has a
   live credential, so that baseline cannot be refreshed or queried for
   EXP-002 without Phil re-pulling it by hand. The single highest-value item
   outstanding is a share URL or API key so an operator session can pull it
   directly (backlog item 1.2).
2. **Epic 2, broken or dishonest.** The real blocker is the shared Listmonk
   sending identity (issue #15, P0): a 6S signup currently would receive mail
   branded as a different company, so every signup surface on the site
   (footer and in-body) has been deliberately withdrawn rather than shipped
   half-honest. The email list is 0 and stays 0 until this is decided.
3. **Epic 3, traffic.** Search is the only durable, no-audience-required route
   and it takes 12 to 18 months to compound; Nova Consulting has no list to
   borrow. Issue #22 was closed 2026-08-25 (Phil's own session reached the
   site and IndexNow directly), but this operator's sandboxed network still
   returns http_code 000 for both on re-test the same day, so newly
   published pages still cannot be submitted to IndexNow from every session
   even though the ten already-written LinkedIn posts and image prompts are
   ready and waiting on Phil to publish/generate.
4. **Epic 4, conversion.** Deliberately not started; nothing here is
   interpretable until epic 1 lands.
5. **Epic 5, product.** The catalog is not short of products, it is short of
   visitors. Nothing here starts before epic 1 answers whether the funnel
   works at all.

Commerce was largely solved, then broke silently, then was fixed: 158 of 159
catalog items have a Stripe Payment Link or a real free download behind them
(widened from 10 on 2026-08-27, Phil's own Stripe sync); all six links the
live site actually served were found deactivated on 2026-08-30 and
reactivated and verified working by Phil on 2026-08-31 (see "Why this was
RED, and why it is YELLOW now" above). What is still unconfirmed is whether
the deployed site itself carries the rest of the repository's fixes and
current catalog and pricing. **Corrected 2026-09-11, operator: the "7 of 9
homepage assets behind" figure this paragraph cited is stale and no longer
what the dashboard measures** (`EXECUTIVE-DASHBOARD-LIVE.md` today reads
"could not be reached from here... treat public reachability as unverified,
not confirmed," not a specific stale-asset count); that number was last real
around 2026-08-31 and nobody re-derived this citation after the dashboard's
own measurement changed shape, the same "source corrected, artifact never
re-derived" defect class this file names throughout. The "Redeploy click"
framing is also superseded: `OWNER-ACTIONS.md` item 1 records the VPS SSH
deploy key installed 2026-09-01 ("No deploy needs you again"), so Hostinger's
manual click is no longer the mechanism. Every sandboxed (cloud) session,
this one included, reports "no deploy key at /root/.ssh/6s_deploy" and has no
egress to the VPS, so a sandboxed session can never confirm deploy freshness
directly. **Corrected 2026-09-23, PM check-in: the paragraph used to say
whether the site had ever been redeployed since 2026-09-01 was "genuinely
unknown from here." That was true once but is stale; it is not unknown.**
Local sessions with real VPS access hold the key's private half and use it
routinely, confirmed by real, timestamped entries in `OWNER-ACTIONS.md` and
`ops/deploy-verdict.json` (2026-09-15, -18, -20, -22, -23, several same-day):
each records the exact build hash moved to and the UTC timestamp checked
directly against the verdict file, not cited from memory. **Corrected again
2026-09-23, later PM check-in: this paragraph and the section 5 table below
had fallen one confirmation behind `BLOCKER-001`, which a same-day cycle had
already updated.** As of the last such check (`ops/deploy-verdict.json`,
`2026-09-23T19:00:39Z`), production served build `5eba61fde231c1a7`, from a
session that finished the Stripe SKU retirement (65 of 65 archived) and
redeployed (commit `8e4c8e33`, the dead mobile-nav fix on
`deck-gallery.html`/`deck-gallery-mudroom.html`). **Re-sized 2026-09-24,
PM check-in: the "one commit behind" figure above had itself gone stale
for over 8 hours while several intervening cycles repeated it unchecked.**
`git log 8e4c8e33..HEAD` is 47 commits, not 1 (repository HEAD build
`38b20571260ea9ff`, confirmed current via `ops/build_id.py --check`), and
two of those are live customer-facing, not internal-consistency work:
`a16788fa` fixed a second, real dead-nav-menu defect on `404.html`,
`corporate.html`, `kit.html` and 2 B2B articles (same defect class as
`8e4c8e33` itself), still serving the broken hamburger button to every
mobile visitor to those 5 pages right now; `b0166730` (Phil's own commit)
finished retiring the last of 65 dead/superseded Stripe SKUs, so
production's catalogue is stale by that much too. "No automated
pipeline exercises `ops/deploy.py`" is also still true (no `.github/workflows/`
job runs it) and remains a real gap: freshness depends on a local session
happening to run one, not on any guaranteed cadence.

### Completed since 2026-08-16

- Repository consolidated and made private; the complete-book PDF is no longer
  publicly downloadable from GitHub.
- Safety disclaimer injected estate-wide: 50/50 chapters, the Field Manual, the
  decks, the board games, the product appendix and the app prototype.
- Website legal surface built: privacy, terms, accessibility and safety notice,
  linked from all 13 pages. Dead links went from 24 to 0, and remain at 0.
- Two physical-safety defects fixed in the book (Ch 45 power tools, Ch 50 propane).
- 945 uses of the rejected term "Set in Order" swept to "Straighten".
- Amazon trademark removed from card EE-001 text and filenames.
- Site fonts: 14 missing real weights installed, ending faux bold, and the last
  third-party request removed. The site now makes zero external calls.
- All 14 site forms wired to a prefilled email handoff instead of discarding
  input (2026-08-17).
- Free sample PDF cut from 50.7 MB to 40.0 MB with no quality loss, and stopped
  claiming to be "The Complete Book" when it holds chapters 1 to 30 of 50
  (2026-08-17).
- Cart fixed to hand off what a customer actually selected, and the shop page
  stopped marketing 34 of 41 catalogued products, including two featured on the
  homepage, as available to buy when none has a supplier, a build, or a
  platform behind it yet. They now read "In development" and link to an
  honest interest form (2026-08-19).
- Site deployed to the Hostinger VPS: image published to `ghcr.io`, compose
  pasted and two silent faults fixed, DNS pointed at the VPS. The domain still
  does not reach it; see priority 1 above (2026-08-18).
- Free sample's on-disk filename still read "Complete Book" after its title
  and heading were corrected, so a reader's saved file carried the false claim
  the visible link text no longer made. Renamed the HTML and PDF (site and the
  content mirror) to name what they actually are: chapters 1 to 30 (2026-08-19).
- Live Stripe account onboarded and two consulting products taken live: Virtual
  Home Consult and In-Home Reset Day, both real Payment Links (2026-08-19).
- The consulting page's own primary "Book a consult" button sent buyers to a
  contact form instead of the live packages just below it, the exact page
  built to sell something that can now actually be bought. Repointed it to the
  packages section, and corrected `ops/dashboard.py`'s payment detection,
  which only looked for an embedded checkout script and so still reported
  "cannot take money" after the Payment Links went live (2026-08-19).
- Phil synced the 149 generated zone/room/kit/bundle packs to live Stripe
  himself and wired `window.CATALOG`, widening the buyable catalog from 10
  to 158 of 159 SKUs, and fixed the EPUB builder's hardcoded author
  placeholder that had blocked Amazon KDP submission (both 2026-08-27).
- Phil built a retail affiliate link layer (`ops/affiliate.py`,
  `ops/affiliate-accounts.json`, 10 programmes tracked), a compliance gate
  wired into `fulfil-orders.yml` (no affiliate link may ship inside a PDF,
  EPUB or other delivered document; disclosure must sit above any tracked
  link), and primary-sourced research on all 10 programmes, emailed to
  himself as a decision dossier (2026-08-28). No programme is applied to
  yet; opening an account requires his own legal/tax identity, so this is
  entirely his next step, not operator-actionable. The dossier's headline:
  do not apply to Amazon yet (a 180-day, 3-sale rule would likely burn the
  Associates ID permanently at current traffic), Wayfair's Creator terms
  forbid the only surfaces this site has, and Etsy/Office Depot/Home Depot
  legacy look like the best near-term fits.
- Phil found and fixed a live payment outage (all 6 Stripe links the site
  served were deactivated, invisible to every repository-level check for at
  least 3 days), added `ops/check_live_links.py` to catch it going forward,
  corrected terms/delivery-time/privacy copy that would have shipped
  publicly false statements on the same deploy, and hardened the deploy
  path itself (nginx config now validated in CI before publish, timeouts
  added to three proxied locations) (2026-08-30, `retro/RETRO-2026-08-30-cycle6.md`).
- Phil put each of the 109 sellable zone packs on its own zone page ($4 for
  6 cards, beside the existing $19 whole-house pack), closing the gap where
  the only pages that create demand for the long tail never linked to it
  (2026-08-30).
- One product, one card count: the Entryway deck was advertised as 46, 88
  and 90 cards in different places; corrected everywhere to the real 88, and
  `gate_deck_count` now checks it on every build (2026-08-30, Phil).
- The eight day payment outage closed: all six live Stripe payment links
  reactivated and verified working in a real browser, the same measurement
  that had reported them dead now reports the site can take money again
  (2026-08-31, Phil, `b0e9462`, `84c04cc`). The deployed site itself is
  still an older build than the repository; see the redeploy note above.

---

# 3. Current Operating Foundation

| Component | Status | Notes |
|---|---|---|
| `CLAUDE.md` | CREATED | Master autonomous operating constitution |
| `AUTONOMY.md` | CREATED | GREEN / YELLOW / RED execution authority |
| `STATUS.md` | CREATED | This living current-state file |
| Agent framework | IN PROGRESS | Specialist agents are being established |
| GitHub governance | DEFINED | `github-manager` agent created |
| Hostinger VPS/Docker governance | DEFINED | `vps-docker-manager` agent created |
| Reliability governance | DEFINED | `devops-sre` updated for separated ownership |
| Live business metrics | UNKNOWN | Must be connected and verified |
| Executive dashboard | NOT YET VERIFIED | Specification and implementation still required |
| Automated operating loop | IMPLEMENTED | Hourly trigger runs the cycle described in `DAILY-LOOP.md`. Issue #17 closed 2026-08-25: the trigger's prompt was rewritten to read `BACKLOG-2026-H2.md` directly rather than embedding a status snapshot, so it no longer needs self-update to stay current. |

---

# 4. Production Status

**Filled 2026-09-24, scheduled operator cycle, handed off by name by the
12:4x PM check-in: this table had stood as the unfilled 2026-08-16 bootstrap
template, every row `UNKNOWN`, even though sibling sections (5, 8, 17) had
long since been corrected with real evidence, contradicting this section in
the same document.** Filled from evidence already on hand across
`ARCHITECTURE.md` (corrected this same cycle), `DEPLOY-VPS.md`,
`RISKS.md`, `OWNER-ACTIONS.md` and `ops/deploy-verdict.json`, not guessed. No
sandboxed session can re-run any of this directly (no VPS egress, no
Stripe/SSH credential here); every row below is only as current as its own
citation, not this session's own measurement. A row stays `UNKNOWN` where no
session has ever actually measured it.

| Area | Status | Evidence / Notes |
|---|---|---|
| Public website | LIVE as of 2026-09-30T15:36:31Z, 0 commits behind (CORRECTED 2026-09-30, PM check-in 15:4x; see `BLOCKER-001`) | This row still cited the 07:42:00Z confirmation after a newer redeploy superseded it: commit `12e3402ca` (09:10, quest-symptom-shown) touched `site/`, moving the build one commit ahead, and Phil's own session then redeployed and recorded a fresh verdict in `ac8e2c1fc` (09:36:54-06:00 = 15:36:54Z) before this row was told. `ops/deploy-verdict.json`, read directly, records build `04167f5ad701b0e4`, `checked_at: 2026-09-30T15:36:31Z`, superseding `e70a81623df41ed5`/07:42:00Z. Fresh recount, not cited: `git log 12e3402ca..HEAD -- site/ Dockerfile` returns zero commits. Production matches `HEAD` exactly: `site/build-id.txt` at `HEAD` is `04167f5ad701b0e4`, byte-identical to the confirmed-live build. No P0 regression, no gap. |
| Application/API | N/A BY DESIGN | No application server, database or backend exists; the site is static HTML served by nginx (`ARCHITECTURE.md` section 1) |
| Database | N/A FOR THE SITE ITSELF | The site holds no database. The Umami analytics database lives on the same VPS but is not part of this site's own stack; it is not backed up off-host (`RISKS.md` RISK-0007's 2026-09-21 finding) |
| Reverse proxy | Nginx Proxy Manager | A pre-existing shared instance, not Traefik; also fronts Ledgerium AI and Compassion Benchmark on the same VPS (`CLAUDE.md` 36b). `ARCHITECTURE.md` section 4, corrected this cycle after standing wrong (naming Traefik) since the file was written |
| TLS/HTTPS | Let's Encrypt, issued through NPM's own panel | Not tracked by this repository; certificate expiry/renewal history has never been inspected by any session (genuinely `UNKNOWN`) |
| Docker host | One Hostinger VPS, `187.77.25.50`, shared with two other businesses | Ledgerium AI and Compassion Benchmark on the same host (`DEPLOY-VPS.md`, `CLAUDE.md` 36b) |
| Critical containers | `6s-success`: healthy, 0 restarts, as of 2026-09-16 | `OWNER-ACTIONS.md` 1f. Two other containers on the shared host were found crash-looping (177/197 restarts) the same day, traced to Ledgerium's own half-finished deploy, not this site's; no action needed on either. Not re-measured since 2026-09-16 |
| Persistent volumes | One: the nginx access log | `docker-compose.hostinger.yml` (the file actually pasted into the Hostinger panel, confirmed by `RUNBOOK.md`'s own 2026-09-20 diff against the live host file) mounts `/var/log/6s-success:/var/log/nginx/persist`, added 2026-09-20 so the crawl log survives a redeploy. The `letsencrypt` volume named here previously belongs to the unused `docker-compose.proxy.yml` Traefik topology. NPM's own certificate/config data lives in NPM's own volume, external to this repository (`ARCHITECTURE.md` section 9, corrected this cycle) |
| Backups | Site: not needed, rebuildable from Git + a fresh image pull. The access-log volume: not backed up. NPM's config: not backed up. Umami analytics: one manual point-in-time export exists (2026-09-21, `ops/backup_analytics.py`, verified by independently recomputing the headline numbers from the CSV), not on a schedule | `RISKS.md` RISK-0007's 2026-09-21 finding; `DISASTER-RECOVERY.md` section 7c/7d. NPM's proxy-host configuration is recorded field by field so it can be rebuilt from a document if that volume is lost, but the volume itself is not backed up |
| Restore readiness | PARTIALLY MEASURED | A real container-loss drill ran 2026-09-21: pull 0.46s, run 0.38s, first HTTP 200 0.54s, total 1.38s, correct build id and full 159-item catalogue confirmed. Covers "container lost or bad deploy." Does NOT cover a lost host: no VPS has ever been reprovisioned, no DNS/NPM/certificate rebuild has been drilled (`RISKS.md` RISK-0007) |
| Disk capacity | 40% used, 38G of 96G, 58G free | Measured 2026-09-20 (`OWNER-ACTIONS.md` 1f, closed); was 79% full on 2026-09-16 before something reclaimed ~38GB (not this operator). Re-open if free space ever drops under ~5G |
| Memory capacity | UNKNOWN | No session has measured `free -h` on the host |
| CPU health | UNKNOWN | No session has measured `nproc`/load on the host |
| Production logs | Two sources, both real | NPM's own access log (survives container recreation, reaches back to 2026-08-19, has client IPs); a bind-mounted `/var/log/6s-success/access.log` since 2026-09-20 (rotated weekly, no IPs). Neither is shipped off-host |
| Monitoring | Traffic only, confirmed no infrastructure monitoring | Umami tracks visitors/pageviews (not infra health). `RUNBOOK.md`'s own inventory: "no external uptime monitor... no error monitoring." Liveness is checked on demand only, by `ops/deploy.py`, `ops/check_live_links.py` and the container's own `HEALTHCHECK` |
| Active incidents | NONE currently open | `INCIDENTS.md` is a policy standard with no live incident log entries. The nearest real production-impacting events on record are the 8-day dead-payment-link outage (2026-08-22 to 30, closed) and the Ledgerium crash-looping containers found 2026-09-16 (not this site's incident) |

### Production Rule

Do not replace `UNKNOWN` with `GREEN` without evidence.

---

# 5. Production Release

**Corrected 2026-09-23, PM check-in: this table had stood as an unfilled
UNKNOWN template even though `ops/deploy-verdict.json` has answered most of
it, continuously, since it was introduced.** No sandboxed session can
re-verify these fields directly (no VPS egress, no deploy key here), so
treat them as only as fresh as the verdict file's own `checked_at`, not as
this session's own measurement.

**Currently Deployed Build (last confirmed):** `a6c5f96b77c7cff2` (resolves to commit `223f5111`), confirmed 2026-09-25T22:21:27Z, superseding the earlier `d40585d97500a3ca`/14:15:05Z confirmation
**Confirmed At:** `2026-09-24T21:10:12Z` (`ops/deploy-verdict.json`,
a session with real production access)
**Repository HEAD Build:** `6e4992daa2791557` (`site/build-id.txt`,
this scheduled operator cycle, 21:2x. One commit ahead of the confirmed
deployed build above: `869d4e93` ("Home Office personalised") landed
after the confirmation and touched `site/`, so `git diff --quiet
d5b0d5c8 HEAD -- site/ Dockerfile` is dirty again. Production is one
commit stale, not current; see `BLOCKER-001` below for the full account
and the standing caveat that this will keep recurring until
`VPS_DEPLOY_KEY` makes redeploy automatic)
**Release / Tag:** NONE, every deploy is tracked by commit SHA / image
digest, 0 GitHub tags or releases exist
**Deployment Method:** `ops/deploy.py`, run manually by a local session
holding `~/.ssh/6s_deploy` (installed 2026-09-01). **Corrected 2026-09-24:**
`.github/workflows/deploy.yml` now exists and calls it automatically on every
successful image publish, but is inert until `VPS_DEPLOY_KEY` is set as a
GitHub secret (`OWNER-ACTIONS.md` "start here" item 0), so a manual run is
still today's only real deploy path
**Known-Good Rollback Release:** UNKNOWN, no rollback procedure has been
exercised or documented in this repository's tooling
**Runtime/Image Identity:** `ghcr.io` image, tag/digest not tracked here

Owners:

- Release identity: `github-manager`
- Reliability/readiness: `devops-sre`
- Runtime deployment state: `vps-docker-manager`

The first production discovery cycle should reconcile:

**GitHub release → deployed artifact/image → running production**

---

# 6. GitHub Status

Owner: `github-manager`

**Corrected 2026-09-20, scheduled operator cycle.** This table had stood as an
unfilled bootstrap template, every row UNKNOWN, since the file's creation,
even though this same document's own section 1 narrative and
`EXECUTIVE-DASHBOARD-LIVE.md` report most of these facts on every cycle. Filled
with what is genuinely known and live-checked this cycle via the GitHub API; a
row stays UNKNOWN only where this operator sandbox truly cannot see the
answer (no admin/security-alerts scope confirmed either way).

| Area | Status | Notes |
|---|---|---|
| Repository identified | `Klingdom/6s-success` | Confirmed via the GitHub API this cycle |
| Default branch | `main` | Confirmed; it is also the only branch that exists |
| Branch protections | NONE | `main` returns `protected: false` via the API |
| Open PRs | 0 | Confirmed live this cycle |
| Active branches | 1 (`main` only) | Confirmed live this cycle; no stray/abandoned branches |
| CI health | GREEN | **Corrected 2026-09-25 06:1x, PM check-in: the two prior rows (#1194-1196, 2026-09-20) were nine days stale and predated this same day's own real `checks.yml` outage and fix (STATUS.md section 1, `gate_ci_checkout_full_history`).** Checked live via the API rather than cited: `checks.yml` runs #1408-#1411, the four completed runs since the shallow-checkout fix (`1da2f69e`) landed, all `success`; #1412 (current HEAD, `5e73ade8`) still `in_progress` at the time of this check. `fulfil-orders.yml`, `linkedin-drafts.yml`, `social-drafts.yml` unchanged, still green on their latest scheduled runs |
| Deployment workflow | BUILT, INERT UNTIL A SECRET IS SET | `.github/workflows/deploy.yml` (added 2026-09-24) runs `ops/deploy.py` automatically once `publish-image.yml` succeeds, but exits without acting because no `VPS_DEPLOY_KEY` secret exists yet; a local session holding the VPS deploy key still runs it manually today, confirmed routinely since 2026-09-01 (`ops/deploy-verdict.json`, `OWNER-ACTIONS.md`). **Corrected 2026-09-23:** this row previously implied the click may never have happened; it has, repeatedly, just never from a sandboxed session |
| Security/dependency alerts | UNKNOWN | This operator's GitHub access has not been confirmed to include the security-alerts scope; not checked |
| Release convention | NONE | 0 tags, 0 releases. Every deploy is tracked by commit SHA / image digest, not a tag |
| Production traceability | Tracked, current build citation, real gap CLOSED, 0 commits (2026-09-30, PM check-in 15:4x) | **CORRECTED 2026-09-30: this row also carried the stale `e70a81623df41ed5`/07:42:00Z citation the Public website row above has just been corrected from.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `04167f5ad701b0e4`, `checked_at: 2026-09-30T15:36:31Z` (commit `ac8e2c1fc`, authored by Phil directly), superseding `e70a81623df41ed5`. `git log 12e3402ca..HEAD -- site/ Dockerfile` returns zero commits: production matches `HEAD` exactly. Full account in `BLOCKER-001` and the Public website row above; this row and the one above now agree. |
| Repository hygiene | 8 open issues (6 `decision`, 2 `blocked-on-art`), 0 open PRs, 1 branch, 219+ test files, `preflight.py` clean | **Corrected 2026-09-25 06:1x, PM check-in:** the prior "7 issues (5 decision)" undercounted; issue #35 (`VPS_DEPLOY_KEY`, opened 2026-09-24) is a sixth `decision`-labelled issue, confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35). Not a formal audit, but the working facts a reader would otherwise have to reconstruct from `NIGHTLY-LOG.md` |

### GitHub Priority

Establish a trustworthy mapping between:

**work item → branch → PR → commit → release → production**

---

# 7. Hostinger VPS / Docker Status

Owner: `vps-docker-manager`

**Filled 2026-09-24, scheduled operator cycle, same handoff as section 4
above: this table stood as the unfilled 2026-08-16 bootstrap template while
`OWNER-ACTIONS.md`, `DEPLOY-VPS.md` and `RISKS.md` already had real, dated
answers for several rows.** Same sourcing rule as section 4: no sandboxed
session can measure any of this directly, so every row is only as current as
its own citation; genuine gaps stay `UNKNOWN` rather than guessed.

| Area | Status | Notes |
|---|---|---|
| VPS access | No sandboxed session holds it | Sessions running on Phil's own machine hold `~/.ssh/6s_deploy` (installed 2026-09-01) and use it routinely (`ops/deploy-verdict.json`'s history). `GitHub Actions` does not yet: issue #35 (`decision`) asks Phil to add it as `VPS_DEPLOY_KEY` |
| Host OS | Ubuntu 24.04.4 LTS, kernel 6.8.0-134-generic | `RUNBOOK.md`'s own hostinger inventory block |
| Docker Engine | Present, version UNKNOWN | Hostinger's own Docker Manager runs the compose stacks; no session has recorded the engine version |
| Docker Compose | Present; `docker-compose.hostinger.yml` is the file actually running | See `ARCHITECTURE.md` section 5, corrected this cycle. Confirmed by `RUNBOOK.md`'s own 2026-09-20 diff against the live host file. `docker-compose.yml` and `docker-compose.proxy.yml` also exist in this repository but neither is deployed |
| Compose projects | This site plus at least Ledgerium AI, Compassion Benchmark, Cal.com and Nginx Proxy Manager share the host | `CLAUDE.md` 36b, `RISKS.md` RISK-0007's 2026-09-21 finding. Full inventory (`docker compose ls`) has never been run and recorded here |
| Running containers | `6s-success`: confirmed healthy, 0 restarts, as of 2026-09-16 | `OWNER-ACTIONS.md` 1f. Two other containers on the shared host were crash-looping (177/197 restarts) the same day, traced to Ledgerium's own deploy, not this site's; no action taken on either, none needed. Full container inventory not recorded here |
| Container health | Healthy as of 2026-09-16 (0 restarts) | Not re-measured since; see row above |
| Networks | Known for this site | `docker-compose.hostinger.yml` joins the external `6s-proxy` network under the alias `6s-success`. NPM currently forwards to the VPS's own public IP on port 8973 rather than that alias (a tracked, not-yet-made improvement, `DISASTER-RECOVERY.md` 7c); the unused `docker-compose.proxy.yml` defines its own `web` network, not in use. No full `docker network ls` inventory of the whole shared host recorded |
| Volumes | This site's own stack defines one: the nginx access log | `/var/log/6s-success:/var/log/nginx/persist`, see section 4 above. NPM's own data volume and the Umami database volume also exist on the shared host, outside this repository's control; neither has been fully inventoried. Per the VPS Safety Rule below, nothing has been deleted |
| Images | 23.92 GB of images on the host as of 2026-09-20 (down from 62.65 GB on 2026-09-16) | `docker system df`, read by a session with real VPS access, `OWNER-ACTIONS.md` 1f. Includes images for every project on the shared host, not only this site's. ~38 GB of build cache was reclaimed between those two dates by an unidentified actor (not this operator) |
| Reverse proxy | Nginx Proxy Manager, shared instance | See section 4 above and `ARCHITECTURE.md` section 4, corrected this cycle (previously wrongly named Traefik) |
| Public ports | 80 and 443 held by NPM for all businesses on the host; this site's own container is not on either | `DEPLOY-VPS.md`. The site listens on host port 8973, reached only via NPM's forward |
| Environment configuration | The live file (`docker-compose.hostinger.yml`) needs no `.env` values; the unused proxy topology needs `DOMAIN`/`ACME_EMAIL` | `ARCHITECTURE.md` section 5. "Zero credentials touch the VPS" for the image-pull deploy method (`DEPLOY-VPS.md`); this would change if issue #35's `VPS_DEPLOY_KEY` decision is approved |
| Log rotation | Two logs, both rotate | NPM's own access log (rotation policy not recorded here) and the bind-mounted `/var/log/6s-success/access.log` (rotated weekly, confirmed in section 10 above) |
| Backup jobs | Host-level: Hostinger's own VPS backup, frequency UNKNOWN, never restore-tested (`RUNBOOK.md`). Application-level: NONE for NPM's config or the access-log volume; the Umami database has one manual, unscheduled export (2026-09-21) | `RISKS.md` RISK-0007's 2026-09-21 finding; `DISASTER-RECOVERY.md` section 7d. The site itself needs no backup job, being rebuildable from Git plus a fresh image pull |
| Off-host backup | The one manual Umami export (`ops/backup_analytics.py`, 2026-09-21) is the only off-host copy of anything VPS-side | NPM's config and the access-log volume have no off-host copy of any kind. Product masters (a separate, non-VPS risk, RISK-0011) have a OneDrive copy in progress, not yet restore-verified |
| Restore procedure | Documented, PARTIALLY drilled | `DISASTER-RECOVERY.md` covers both the container-loss and lost-host cases; only the container-loss case has been executed and timed (2026-09-21, 1.38s total, `RISKS.md` RISK-0007). The lost-host case (new VPS, DNS, NPM and certificate rebuild) has never been drilled |

### VPS Safety Rule

Unknown persistent resources must be preserved until understood.

**Unknown volume = DO NOT DELETE.**

---

# 8. Customer Experience Status

Owner: `product-manager`

Supporting agents:

- `ux-frontend`
- `qa-reviewer`
- `analytics-intelligence`

**Corrected 2026-09-20, scheduled operator cycle.** Every row below had stood
UNKNOWN even though most journeys are implemented and code-verified. Per
`CLAUDE.md` 0.3, "verified" here means proved against the repository through
automated/headless-browser tests, not against live production: this sandbox
has no egress to `6s-success.com`, so no row claims a live-production check
it did not make.

| Journey | Status | Notes |
|---|---|---|
| Homepage → useful next action | IMPLEMENTED | Home page leads to the Home Quest and the shop; `ops/audit_pages.py`/`audit_visual.py` find 0 findings across 190-191 pages, most recently re-run this cycle |
| Room discovery | IMPLEMENTED | 20 room pages, avg 28.8 inbound content links each, 0 orphans (`ops/link_graph_report.py`, this cycle) |
| Micro-zone discovery | IMPLEMENTED | 114 zone pages, same source, 0 orphans; `resources.html` links directly to all 114 |
| Personal Function Discovery | IMPLEMENTED for 5 zones | The Home Quest's first screen (`#symptom-step`) asks "What is annoying you right now?" in household words, then shows the zone, the real cause and a 2-minute action, per `CLAUDE.md` section 5's model. `SYMPTOM_PICKS` currently covers 5 zones (Entryway + Kitchen); the rest fall through to browsing by room |
| Root-cause guidance | IMPLEMENTED for 114 of 114 zones | **Corrected 2026-09-29, PM check-in: this row still said 12 of 114, the 2026-09-07 pilot figure, nine days after B9's room-deck build authored a full diagnosis layer for every remaining zone as a side effect of building all 20 room decks.** Confirmed live, not cited: `content.json` carries a non-empty `diagnosis` for 114 of 114 zones, and `grep -l 'id="diagnosis"' site/zones/*.html` returns 114 of 114 real zone pages (the 115th match is `zones/index.html`, which correctly carries none), matching `gate_diagnosis_rendered`'s own count-equality check. The 21-day pilot read this row cited as the gate never ran as a decision point; the corpus was rolled to all 114 zones directly. `BACKLOG-2026-09-07.md` section 5's own "Roll ... to all 114 / a 21-day read of a 12-zone pilot" row is the same stale claim, corrected in the same pass. |
| Quest selection | IMPLEMENTED, browser-tested | Symptom-first entry plus draw/room/single-pass modes; `ops/tests/test_quest_flow.py` and siblings drive the real flow in headless Chromium end to end |
| Quest completion | IMPLEMENTED, browser-tested | Victory conditions, Keep screen (photo record), back-button and full-completion edge cases all covered by dedicated headless-Chromium tests, several regressions caught and fixed this week (Keep-screen URL leak, Back button, full-completion shortcut) |
| Product discovery | IMPLEMENTED, browser-tested | `shop.html`'s filterable grid: `ops/tests/test_shop_interactive.py` (new this week) drives all 8 real category filters and cross-checks rendered tile counts against the live catalogue, 155 distinct buy links, 0 defects found |
| Cart/checkout | ONE-CLICK STRIPE LINKS | Cart removed 2026-09-08 (was unreachable, no page could add to it); replaced with a per-product Stripe Payment Link. 129 of 130 catalogue SKUs buyable (`ops/check_sellable.py`); Corporate Lean 6S is quote-based by design |
| Purchased content access | WORKING, one real order | The one recorded sale (Whole House Print Pack, 2026-08-21) fulfilled unattended in about 10 minutes per `ROADMAP-2026-2029.md`. No live-production re-check possible this cycle (no Stripe credential, no egress) |
| Mobile experience | AUDITED, browser-tested | `ops/audit_visual.py --all --mobile`: 0 pages scrolling sideways (last real defect fixed 2026-09-18), touch-target and badge-contrast gates in `preflight.py`, 5 mobile `npm test` suites passing |
| Accessibility | AUDITED, browser-tested | `ops/audit_visual.py`: 0 contrast/heading/landmark findings across 190+ pages after the CSS-`opacity`-aware contrast fix (A6); semantic landmarks wired by `wire_landmarks` on every generated page |

---

# 9. Business Metrics

Owner: `analytics-intelligence`

The values below must come from authoritative sources.

Do not manually estimate them.

**No live Stripe, Umami or Search Console credential exists in this operator
sandbox.** The revenue and order figures below are the one measurement
recorded in `ROADMAP-2026-2029.md`, not a live pull, and will not update again
until a session has real Stripe read access. **Corrected 2026-09-02:** Sessions
and organic sessions are no longer UNKNOWN. The Umami API token is expired
(401 on every route), but Phil's own session read the analytics database
directly on 2026-09-02 and recorded real numbers in `GOALS.md`, which is now
the authoritative source for these two rows. That was a one-time manual pull,
not a wired live feed: this sandbox still cannot refresh it, so treat it as
current as of 2026-09-02 and re-pull by the same means when it goes stale.
Everything else genuinely has no measurement source yet and stays UNKNOWN
rather than being estimated.

| Metric | Current | Period | Confidence |
|---|---:|---|---|
| Revenue | $19 gross / $18.15 net | MTD (Aug 2026) | MEASURED, one transaction, 2026-08-21, recorded manually in `ROADMAP-2026-2029.md`, not a live Stripe pull |
| Revenue | $0 | Last 30 days | MEASURED 2026-09-20 (`f32c0d8c`), direct Stripe charge-list read: the single 2026-08-21 sale fell out of the trailing 30-day window on 2026-09-20 with no second sale since. This row read "$19 ... Same single transaction" for 30 days after that sale and was never updated when the window rolled past it; corrected here to match GOALS.md section 1's own "Trailing-30-day revenue is now $0" (`f32c0d8c`). |
| Orders | 1 (20 checkout sessions started, 19 expired, 7 of those quoted a phantom $18 duplicate price archived 2026-09-06) | Since launch | MEASURED, same source |
| Average Order Value | UNKNOWN | Last 30 days | UNKNOWN |
| Refunds | UNKNOWN | Last 30 days | UNKNOWN |
| Sessions | 48 | Last 30 days | MEASURED 2026-09-29 (visitors; 119 visits, 731 pageviews), direct Umami database read over ssh, filtered to this site's website_id. Late-August days leaving the window explains part of the slide; the trailing week fell too, once a 20-minute burst is set aside. An unfiltered read the same night said 239: this Umami instance serves three sites, and `ops/experiments.py` now refuses that query shape. The 7 Sept automated session (431 pageviews) is long out of the window, so this figure is very nearly all human; previous 57 (09-25), 68 (09-23), 76 (09-21), 78 (09-17), 75 (09-14) |
| Sessions | 7 | Last 7 days | Human-plausible, same source, 2026-09-29. Recorded 14 visitors / 18 visits / 50 pageviews, but 30 pageviews and 9 visitor ids landed between 18:00 and 18:20 on 27 September, all direct, across four operating systems, a signature that also appears late on 23 August. Ex-burst: 7 visitors, 9 visits, 20 pageviews, DOWN on 12 / 14 / 27. **A first draft of this row today called it the first rise on every measure; checking where the pageviews came from withdrew that** |
| Organic sessions | 5 visits from 4 visitors, whole life of the site, re-measured 2026-09-29 and unchanged (1 Bing, 21 August; 4 Google visits from 3 visitors, 4 to 18 September) | Direct Umami database read, not carried forward. Byte-identical to the 2026-09-20 reading: eleven days, 114 of 114 zones diagnosed, three more deck pages, and no additional search referral |
| Assessment starts | UNKNOWN | Last 30 days | UNKNOWN |
| Assessment completions | UNKNOWN | Last 30 days | UNKNOWN |
| Quest starts | UNKNOWN | Last 30 days | UNKNOWN |
| Quest completions | UNKNOWN | Last 30 days | UNKNOWN |
| Product views | UNKNOWN | Last 30 days | UNKNOWN |
| Checkout starts | UNKNOWN | Last 30 days | UNKNOWN |
| Purchase conversion | UNKNOWN | Last 30 days | UNKNOWN |
| Repeat purchase | UNKNOWN | Appropriate cohort | UNKNOWN |

Metric definitions belong in `METRICS.md`.

Data authority belongs in `DATA-SOURCES.md`.

---

# 10. Search / Discovery Status

Owner: `seo-aeo`

Supporting:

- `content-editor`
- `analytics-intelligence`

**Corrected 2026-09-20, scheduled operator cycle.** This table had stood as
an unfilled bootstrap template, every row UNKNOWN, even though most rows are
directly checkable from the repository or from evidence already measured
and cited in `GOALS.md`. Filled with what this cycle could verify directly;
a row stays UNKNOWN only where the real answer needs a credential
(Search Console) this sandbox does not hold.

| Metric / Area | Status | Notes |
|---|---|---|
| Search Console connected | NO | No `google-site-verification` meta tag or file on the live homepage/repository; confirmed by grep this cycle. Owner gate: `OWNER-ACTIONS.md` item 2, a 3-minute paste from Phil. Every day unverified is gone permanently, no backfill |
| Indexed pages | UNKNOWN | Needs Search Console. The one indirect signal we have is crawl activity, not indexing: `GOALS.md` recorded Googlebot fetching the site 178 times in 72 hours (2026-09-05), 171 answered 200 |
| Indexed pages, partial direct evidence | AT LEAST 10 URLs are in Bing's index, measured 2026-09-20 | Search Console is still the only authoritative source and is still owner-gated, but Bing's RSS results endpoint (`/search?format=rss&q=site:6s-success.com`) answers without any credential. It returns: `/`, `/about.html`, `/method.html`, `/consulting.html`, `/contact.html`, `/resources.html`, `/articles/`, `/articles/how-long-does-it-take-to-organise-a-room.html`, `/rooms/home-office`, `/rooms/kitchen`. So room pages and at least one article are indexed. **No zone page appeared, and that is NOT evidence they are missing**: pagination (`first=`), path filters (`site:domain/zones`) and exact-phrase queries all returned nothing through this endpoint *including for control pages known to be indexed*, so the endpoint simply cannot answer those questions. Bing's own result counts contradicted themselves ("About 4,100" then "About 50" for the same query minutes apart) and are unusable. The indexed article is the `.html` form, which has 301'd to its extensionless canonical since 2026-09-17, so that duplicate should consolidate on its own. `ops/crawl_report.py` is now the better instrument for this question and needs only days of log to accumulate |
| Crawl activity, measurable at all | YES, and further back than this row first claimed | **Corrected the same day:** this row first said crawl history began 2026-09-20. It did not. Nginx Proxy Manager keeps its own access log in front of this site, it survives container recreation, it is rotated with archives, and it reaches back to **2026-08-19 (181,847 lines)**. `LEARNINGS.md` LRN-0010 had already used it on 2026-09-14. It also keeps client IPs, so a Googlebot claim can be reverse-DNS checked, which the new log cannot support by design. What was true is the narrower statement: the site container's own log went only to stdout, so it lived in `docker logs` and every deploy destroyed it. Checked that day: the container had restarted an hour earlier and the site's entire crawl history was 61 requests. It is now also written to a bind-mounted file that outlives the container (`/var/log/6s-success/access.log`, rotated weekly, **no IP addresses recorded**) and read by `ops/crawl_report.py`. **This starts history, it does not recover any**: everything before 2026-09-20 is gone and no figure for it can be produced. A user agent is also a claim, not an identity, so counts are "fetches by something calling itself Googlebot" |
| Search impressions | UNKNOWN | Needs Search Console |
| Search clicks | UNKNOWN | Needs Search Console |
| Organic CTR | UNKNOWN | Needs Search Console |
| Top queries | UNKNOWN | Needs Search Console |
| Top landing pages | PARTIALLY KNOWN | From Umami, not Search Console: of Google's 6 landing pageviews ever, 4 landed on `/standards.html`, 2 on the home page (measured 2026-09-14, reconfirmed 2026-09-17). The Standards Pack is the one page organic search currently sends anyone to |
| Technical SEO health | GOOD, measured this cycle | `ops/check_urls.py`: all 188 sitemap URLs resolve to a real file. `ops/audit_pages.py`: 191 pages audited, 0 duplicate titles, 0 duplicate descriptions, 0 findings |
| Structured data health | GOOD, measured this cycle | All 114 zone pages carry both FAQPage and HowTo JSON-LD (grep-confirmed). `gate_zone_name_consistency` and `gate_no_duplicate_hazard_labels` in `ops/preflight.py` protect against two real past defects (a doubled "The" in HowTo names; two distinct hazards sharing one FAQ question) already found and fixed |
| Sitemap health | GOOD | 188 URLs; `gate_sitemap_lastmod_current` (built 2026-09-19) ties each URL's lastmod to a real content hash rather than letting it go stale or over-fire on a shared-asset change |
| Internal-link architecture | GOOD, measured this cycle | `ops/link_graph_report.py`: 0 orphans across 114 zone, 20 room and 29 article pages; `resources.html` links directly to all 114 zone and 20 room pages |
| Room search architecture | LIVE | 20 room pages, avg 28.8 inbound content links each (min 26, max 31), 0 orphans, 0 dead ends |
| Micro-zone search architecture | LIVE | 114 zone pages, each with visible FAQ, HowTo/FAQPage JSON-LD, a hazard block and a kit disclosure |
| AEO/direct-answer coverage | PARTIAL, measured this cycle | `site/llms.txt` exists and names every promoted free asset (gated by `gate_llms_txt_current`). Visible `<dl>` FAQ blocks render on all 114 zone pages, not JSON-LD only. `GOALS.md` confirms ClaudeBot (20 fetches) and GPTBot (10 fetches) already crawl the site directly in one 72-hour window (measured 2026-09-05) |

Do not create mass content until the existing site and search state are understood.

---

# 11. Commerce Status

Owner: `commerce-manager`

Supporting:

- `cro-growth`
- `analytics-intelligence`
- `product-manager`
- `security-auditor`

| Area | Status | Notes |
|---|---|---|
| Commerce platform | LARGELY LIVE | 129 of 130 catalog items take a card directly through a Stripe Payment Link, real downloads for free ones. Corporate Lean 6S is priced-per-engagement by design, not gapless: `site/corporate.html` (Phil, commit `9e7b1cd1`, 2026-09-03) gives it a qualified-enquiry buy path ending in a written scope and fixed fee, deliberately with no self-serve checkout since two engagements with the same headcount can be very different weeks of work. This row still read "no buy path" as of 2026-09-05, corrected here 2026-09-06 after `GOALS.md` and `REVENUE-REVIEW-2026-09-04.md` were found with the same stale claim. Catalog widened from 10 to 159 SKUs on 2026-08-27 when Phil wired the 149 generated zone/room/kit/bundle packs to live Stripe products himself (commit `b10a278`, backlog 5.7); narrowed to 138 on 2026-09-22 when `147179c6` retired the 6 Area Bundles and 15 Situation Kits (D-023), and to 130 on 2026-09-23 when D-024 retired the 7 Kitchen zone packs and the Kitchen room pack. |
| Payment provider | LIVE | Stripe, acct_1U5rDs6OlZmKL8mF, charges and payouts enabled since 2026-08-19. One real transaction cleared 2026-08-21 ($19, $18.15 net), a personal referral, not a stranger. MCP connection is read only; writes go through reviewed scripts (`ops/stripe_catalog.py`, `ops/stripe_setup.py`, `ops/stripe_links.py`). |
| Checkout health | UNVERIFIED THIS SESSION | `buy.stripe.com` is unreachable from this operator session's sandboxed network (still http_code 000 on re-test 2026-08-27), though issue #22 was closed 2026-08-25 after Phil's own session reached the live site directly. Egress is inconsistent across sessions, not uniformly fixed. One real order completing on 2026-08-21 is the strongest evidence checkout works end to end. |
| Product catalog | 129 of 130 SKUs buyable | Corporate Lean 6S is quote-per-engagement, not gapless: see the commerce platform row above. Card decks (issue #20) closed 2026-09-15: one free 88-card deck, no paid tier, pending sales evidence, not an open decision. See `6S_SUCCESS_PRODUCT-CATALOG.md` and `PRODUCT-CATALOG.md`. |
| Digital fulfillment | WORKING | The one recorded sale (Whole House Print Pack) fulfilled unattended in about ten minutes per `ROADMAP-2026-2029.md`. |
| Physical fulfillment | N/A | Nothing physical is sold; consulting is a service |
| Pricing source of truth | `site/assets/js/data.js` (`window.CATALOG`), asserted against Stripe by `ops/stripe_catalog.py --apply` | Run after any price or product change |
| Tax handling | UNKNOWN | Identify current implementation |
| Refund workflow | DOCUMENTED, UNVERIFIED | `site/terms.html` states a distance-based refund schedule for bookings; no refund has been tested against live Stripe |
| Purchase analytics | 1 order, no repeat | The single 2026-08-21 sale; too small a sample to be more than a coincidence with a percentage sign, per `ROADMAP-2026-2029.md` |
| Product margin data | UNKNOWN | Establish if applicable |

Payment recipient changes remain RED.

---

# 12. Product Portfolio Status

Current strategic product concepts may include:

- Entryway digital deck
- Entryway physical deck
- room decks
- micro-zone mini decks
- digital quests
- printable resources
- labels / visual controls
- room reset kits
- organization components
- Gridfinity / 3D-printed modules
- premium digital functionality
- services

These are **concept/product-family context**, not proof that every item is live.

`PRODUCT-CATALOG.md` must distinguish:

- concept
- prototype
- beta
- active
- paused
- retired

Do not market a concept as an available product.

---

# 13. Content Portfolio Status

Known strategic content architecture includes:

**Home**
→ **Rooms**
→ **Micro-Zones**
→ **Desired Functions**
→ **Root Causes**
→ **6S Activities**
→ **Quests**
→ **Standards**
→ **Products / Kits**
→ **Sustainment**

**Corrected 2026-09-20, scheduled operator cycle.** Coverage is not
uniformly UNKNOWN; the counts below are measured directly from the
committed corpus this cycle.

| Layer | Coverage | Notes |
|---|---|---|
| Rooms | 20 of 20 pages live | 0 orphans, `ops/link_graph_report.py` |
| Micro-zones | 114 of 114 pages live | Every zone carries the six 6S passes, a visible FAQ block, and hazard guidance |
| Desired functions / root causes | 114 of 114 zones have authored diagnosis depth | **Corrected 2026-09-29, PM check-in:** this row still said 12 of 114 (Kitchen 7 + Entryway 5), the 2026-09-07 pilot figure. B9's room-deck build authored a full diagnosis layer for every remaining zone as a side effect of building all 20 room decks; confirmed live, `content.json` carries a non-empty `diagnosis` for 114 of 114 zones and all 114 real `site/zones/*.html` pages render the block, matching `gate_diagnosis_rendered`. See the same correction on the Root-cause guidance row above |
| Quests | Live app (`quest.html`) plus 684-card Whole House Print Pack | Symptom-first entry covers 5 of 114 zones; the rest enter by room or a full-house draw |
| Standards | Standards Pack (free, 20 pages) | The one page organic search currently lands anyone on |
| Products / kits | 129 of 130 catalogue SKUs buyable via direct Stripe checkout | Corporate Lean 6S is quote-based by design, not a gap |
| Free decks | All 20 rooms, free and ungated | **Corrected 2026-09-29, PM check-in:** this row still named only Entryway and Kitchen, the state before B9 shipped the other 18 room decks (`site/*-deck.html`, confirmed 20 files on disk; `python ops/b9_claims.py --status` reports zero rooms left undiagnosed). Card counts vary by room's own real corpus size rather than a fixed budget; see `BACKLOG-2026-09-07.md` B9 for the per-room detail |
| Articles | 29 published, differentiated per zone (`gate_general_reading_differentiated`) | 0 orphans, avg 26.7 inbound links each |
| Sustainment | Rewritten across all 114 zones | Median 28 to 94 words per Sustain slot, 0 near-duplicate across the corpus |

`CONTENT-CATALOG.md` should become the authoritative content inventory.

---

# 14. Active Major Workstreams

WIP limit from `CLAUDE.md`:

**Maximum 3 major active workstreams unless deliberately changed.**

The bootstrap-era workstreams below (governance foundation, GitHub/production
control plane, data visibility) closed out over 2026-08-16 through 08-24: all
required operating documents exist, `ops/dashboard.py` generates
`EXECUTIVE-DASHBOARD-LIVE.md` from measured state, and the site is deployed
and was verified live. Every item in `BACKLOG-2026-H2.md` epics 1 through 5
is still blocked on Phil, a decision issue, or a missing credential (see
section 21), and that file's own epic 6 (keep the operation honest) is where
most per-cycle work happened through 2026-09-06.

**Corrected 2026-09-07, this operator.** Phil gave a direct new instruction
(expand the micro zone model, the decks, and the app; recorded verbatim in
`PLAN-MICROZONES-DECKS-APP.md`) and `BACKLOG-2026-09-07.md` reprioritised the
whole queue around it, superseding `BACKLOG-2026-H2.md`'s ordering (that
file's process rules still hold). This is real, currently unblocked work, not
the absence this section described as of 2026-08-24; see Workstream 3 below.

## Workstream 1: Prove a stranger converts (Horizon 1, per `ROADMAP-2026-2029.md`)

**Status:** BLOCKED, not yet startable  
**Owner:** operator, gated by Phil on backlog items 1.2 and 2.1  
**Objective:** Answer whether the funnel converts anyone who was not
personally told about the site by Phil, per the roadmap's kill criterion
(fewer than 500 organic visits/month and nothing further has sold beyond
the single $19 of 2026-08-21, by August 2027).

EXP-001 is answered (permanently AMBIGUOUS, backlog 1.3). Blocked on: a
Umami share URL or API key (1.2), so EXP-002 and future funnel reads do not
depend on Phil re-pulling the database by hand each time.

---

## Workstream 2: Local demand test for service SKUs (Epic 3B)

**Status:** BLOCKED, awaiting a spending decision  
**Owner:** Phil approves, operator executes  
**Objective:** Test whether the In-Home Reset Day / Virtual Home Consult SKUs
have real non-referral demand, since they are the only route to $20,000 that
does not require quarter-million-visitor traffic.

Blocked on: 3B.1, a capped budget and stop date, correctly RED per `CLAUDE.md`
(material spending).

---

## Workstream 3: The diagnostic layer, Sustain depth, and the Kitchen deck

**Status:** ACTIVE, opened 2026-09-07  
**Owner:** operator, direction from Phil  
**Objective:** `PLAN-MICROZONES-DECKS-APP.md` + `BACKLOG-2026-09-07.md`
section 2/3: build the root-cause diagnostic layer the product currently
lacks (0 of 114 zones map a root cause), fix the app's first thirty seconds,
and ship the free unillustrated Kitchen deck.

**Done:** M1, the frozen 17-cause vocabulary (`ops/root_causes.py`,
`gate_root_cause_vocabulary`), corrected from the plan's own uncross-checked
"21" (a friction-card count, not a cause count). Separately this same cycle,
not part of this workstream's plan but found while verifying it: a live CI
break (three control docs' em/en dashes, plus real bugs in the fixing tool
itself) and a real generator-ownership drift (the $19 Print Pack, the live
Quest app's own data, and the mobile app's corpus all served pre-Sustain-
rewrite text after a concurrent session's content change), both fixed.

**Done 2026-09-07, operator, this cycle:** M2, the `diagnosis` schema and
validator (`ops/diagnosis.py`, `content/manual/source/validate.py` GATE 8,
`ops/tests/test_diagnosis_schema.py`). First draft flattened each friction to
one cause; corrected in the same cycle after checking it against the real
`kitchen-deck.json` FRICTION CARDs, which branch one symptom to two or three
causes. Zones without `diagnosis` still build (0 of 114 diagnosed today).
Also fixed this cycle, found by preflight at the start: `site/build-id.txt`
was stale against the prior commit's own `sw.js` regeneration, failing both
`checks.yml` and `publish-image.yml` at HEAD; fixed and both confirmed green.

**Done 2026-09-07, operator, same cycle:** M3's Kitchen half. All 7 Kitchen
zones now carry `diagnosis`, every string reused verbatim from
`ops/cardtext/kitchen-deck.json`'s own FRICTION and 15-minute ACTION cards
(0 schema problems). Entryway 5 is still open: those zones have no
equivalent card deck to reuse from, so it needs real authorship rather than
a mechanical mapping.

**Done 2026-09-07, operator, this cycle:** M3's Entryway half, and M3 is now
complete (12 of 12 pilot zones). The 5 Entryway zones carry hand-authored
`diagnosis`, since no Entryway card deck exists to reuse from; grounded
directly in each zone's own already-published `passes`/`the_call`/`watch_for`
text, every cause drawn from `ops/root_causes.py`'s frozen 17, no fact
invented. Reconciled with a concurrent session's own commit of the Kitchen
half (`3e58d480`, pushed while this cycle was in flight): rather than
re-push a conflicting `content.json`, reset onto their tip and layered only
the new Entryway zones on top, keeping their Kitchen authorship untouched.

New `gate_diagnosis_authoring` in `preflight.py` asserts, on every run, that
every Kitchen pilot zone's frictions reuse a real FRICTION CARD's `title` or
`objective` and branches character-for-character (their commit used `title`;
the gate accepts either real field, not one hardcoded guess), and scans
every diagnosed zone anywhere for a customer/reviewer attribution claim.
`ops/tests/test_diagnosis_authoring.py`, 5 cases, proves both defect classes
get caught on a planted mutation, then restores; real corpus clean.
`content/manual/source/validate.py` GATE 8: 12 of 114 zones diagnosed, 0
problems. `content.json`'s Entryway diff is a verified pure addition (259
lines, 0 changed), confirmed by a controlled round-trip before editing.

**Done 2026-09-07, operator, this cycle:** M4. `ops/build_zone_pages.py` now
renders the diagnosis block (symptom, branches, 30-second confirm test,
which pass to start at, plus the 15-minute entry) above the six passes on
all 12 pilot zone pages, adds one FAQPage Q&A per friction, and swaps their
related reading from the shared 19-link block to 3 to 5 articles chosen by
the zone's own diagnosed causes, no two of the 12 identical. Two real
grammar defects (a blanket `.lower()` and `str.capitalize()` both turning a
mid-sentence "I" into "i") caught by reading the rendered page, not by any
upstream check, and fixed before shipping. New `gate_diagnosis_rendered` in
`preflight.py` (`ops/tests/test_gate_diagnosis_rendered.py`, 8 cases) checks
render coverage, the link-count range, cross-zone uniqueness, and that exact
pronoun defect on every future run. Not checked against the live domain
itself (`CLAUDE.md` 0.3): no egress to 6s-success.com from this sandbox,
same wall every prior cycle records. Full detail in
`PLAN-MICROZONES-DECKS-APP.md`'s M4 row.

**Done 2026-09-07, operator, this cycle:** K0/B3, the deck card-count gate.
`gate_deck_count` counted rendered card-front PNGs to learn the deck's true
size, and returned immediately when `build/cards-rendered/` was empty, which
is every cloud run: the entire check, including every catalogue/page
comparison, silently never ran anywhere except a full local render. Rewrote
it to read `build/entryway-cardtext.json` (a committed corpus file, real in
every environment) instead, and to assert `ops/build_deck_gallery.py`'s
hardcoded `DECKS['entryway']['written']` against that corpus so the count
itself can never quietly drift. Verified a real, live defect this surfaced:
`deck.html`'s title, meta description and OG/Twitter tags said "89 cards"
with no explanation, while `data.js`, `shop.html` and the print-and-play
redirect page all said 88; fixed the six flat instances on `deck.html` to
88. Left the already-correct "72 of the deck's 89 cards are drawn" progress
sentences alone (89, the full written total, is the right denominator
there; `deck-gallery.html` already explains the 89/88 split). Also found
and corrected a stale claim in `PLAN-MICROZONES-DECKS-APP.md` 3.2: the "46
cards" figure it named in `ops/build_printpack.py`/`ops/build_standards.py`
no longer exists in either file, consistent with Phil's 2026-08-30 sweep;
that row was never re-read against the code after that fix landed. New
`ops/tests/test_gate_deck_count.py` (7 cases) proves the gate catches a
third-number catalogue claim and a bare wrong-number page, does not
false-positive on a CSS comment inside `<style>` (found live, a dormant
bug the never-runs gate had been hiding) or on the honest "X of Y drawn"
phrasing, and that the DECKS table matches the real corpus. `preflight.py`
confirmed clean after: every gate passed, same 15 sandbox-limitation
warnings. The 404-shop-tile half of K0 is unchanged: the referenced image
exists in this repository's own build, not the same claim as a live 200,
and this sandbox still has no egress to 6s-success.com to check that
directly.

**Next:** M4's 21-day clock starts once this is deployed and verified live.
A2 is now done (see below). M6 (diagnosis for the remaining 102 zones) stays
gated on M4's 21-day read, per the plan's own rule: do not start it early.

**A5 done, 2026-09-09, operator.** The three genuinely missing funnel events
(`quest-cause-shown`, `quest-card-abandoned`, `quest-return`) are now shipped
in `site/assets/js/quest.js`, verified by a new static gate and a real
headless-Chromium run; see `BACKLOG-2026-09-07.md`'s "A5 (funnel
instrumentation) closed" row and `PLAN-MICROZONES-DECKS-APP.md`'s A5 row for
the full account.

**S1-S4 re-measured, 2026-09-09, operator, rather than trusted from the
prior line's own hedge.** The prior note here was right to be suspicious:
the concurrent Sustain prose rewrite already covers most of what S1-S4 asked
for as authored content. Measured directly against `content.json`'s 114
`passes.sustain` strings: all 114 are now 87 to 106 words (median 94,
comfortably inside S2/S4's 90-to-130 target), and a rough keyword scan finds
recovery language in 102 of 114. What is still genuinely absent is the
*structured, machine-checkable* schema S1 itself asks for (a `sustain_detail`
object with six typed fields, a closed cadence list, a `drift_signal` noun
check): 0 of 114 zones carry any such field today, so S1's schema and gate
do not exist. Given the prose already answers the content gap that made S1
urgent, S1 as originally scoped (add the schema, then re-author it a second
time in structured form) reads as more product work ahead of the constraint
(`GOALS.md` rule 1: distribution beats production) rather than the
measurement-tier item it was filed as. Recommend re-scoping S1 to something
narrower before spending 0.5 to 3.5 days on it, or dropping it in favour of
Epic 3 (traffic) work; left as an open question rather than started this
cycle.

**A2 done, 2026-09-09, operator, a later cycle the same day.** "45 to 75
minutes" was still the first number a first-timer read on card one of the
classic ("show me the house instead" -> "Start at the door") path; the
symptom flow's own simplified card zero already hid it, but that path did
not. `site/assets/js/quest.js` now withholds `#c-session` on any card one of
a genuine first run (`run.i === 0 && isFirstRun()`), covering both paths with
one condition instead of two. The number moved to the finish screen instead
of disappearing: a new `#f-session` in `site/quest.html`, populated once at
least one card of a single-zone run is done, phrased against whether the
zone was just fully held. The zone page already stated it and is untouched.
Verified in a real headless-Chromium run of the classic path end to end
(card one empty, card two correctly shows "15-30 min for the whole zone, six
passes", finish screen reads "The whole zone runs about 15-30 min, all six
passes, whenever you want the rest of it."), plus the existing
`test_quest_flow.py` (symptom path) still passing unmodified. New
`gate_quest_session_placement` in `preflight.py`,
`ops/tests/test_gate_quest_session_placement.py` (6 cases, fail-then-pass
proved on both halves: the withholding and the finish-screen restatement).
`ops/fingerprint_assets.py` rerun; `site/quest.html`'s script-tag
fingerprint and `site/sw.js` follow. See `PLAN-MICROZONES-DECKS-APP.md`'s A2
row for the full account.

**M7/A1 found already fixed by Phil, closed against reality, 2026-09-09,
operator, a later cycle the same day.** Both rows still read as 1.5 days of
open work ("570 of 684 cards print a stop condition that card cannot
reach"). Phil's own `fa491b1a` (2026-09-07) had already fixed the actual
lie: `renderCard()` no longer heads a card "You can stop when" over the
whole-zone `done_looks_like` text, it says what the text is and where the
reader stands against it. The literal M7 acceptance criteria (a distinct
authored `victory` line per card) is still unmet and correctly unstarted;
`PLAN-MICROZONES-DECKS-APP.md` updated to say so. New
`gate_quest_card_victory_honesty` in `preflight.py`
(`ops/tests/test_gate_quest_card_victory_honesty.py`, 6 cases, fail-then-pass
proved by reintroducing the exact old heading live) protects the fix from
regressing. Also confirmed A3 and A4 already fully shipped under A5/A6's own
2026-09-08 commits, never marked against their own rows: A3's symptom
screen and A4's two-minute first-action override both live in
`site/assets/js/quest.js`, verified by reading the code directly. See
`PLAN-MICROZONES-DECKS-APP.md`'s M7/A1 rows and section 1.4 for the full
account.

**Done 2026-09-25, scheduled operator: the first of B9's five room decks
(Entryway) shipped, correcting this section's own now-stale line above
("Entryway 5 is still open: those zones have no equivalent card deck to
reuse from, so it needs real authorship rather than a mechanical
mapping").** That was true on 2026-09-07; the Manual's `diagnosis` layer
reached Entryway on 2026-09-24, which made a mechanical mapping possible
after all. New `ops/cardtext/build_entryway_deck.py` and
`ops/build_entryway_deck_page.py` ship a 57-card, corpus-accurate Entryway
deck at `site/entryway-deck.html`, mirroring
`ops/cardtext/build_kitchen_deck.py`'s pattern card for card; the frozen 12
root causes this section's M1 froze are reused verbatim (13 of the 17 are
reachable from Entryway's real frictions), so this new deck composes with
the Kitchen deck rather than forking its own vocabulary. Does not touch
the old illustrated 12-zone free deck (`deck.html`, the live `DECK-ENTRY`
SKU); both are live, each disclosing the other. New
`gate_entryway_deck_rendered` in `preflight.py`, fail-then-pass proved.
Full account in `ops/NIGHTLY-LOG.md`, 2026-09-25, and
`BACKLOG-2026-09-07.md` row B9. Four rooms remain (Laundry, Home Office,
Primary Bathroom, Garage).

**Corrected 2026-09-25, PM check-in: the line above is stale.** All four
named rooms have since shipped the same way (`site/laundry-room-deck.html`,
`site/home-office-deck.html`, `site/primary-bathroom-deck.html`,
`site/garage-deck.html`), each with its own `gate_<room>_deck_current`/
`gate_<room>_deck_rendered` pair, fail-then-pass proved, per
`ops/NIGHTLY-LOG.md`'s 2026-09-25 entries and `BACKLOG-2026-09-07.md` row
B9. B9 is fully closed, five of five rooms; no room deck row remains
open in section 3.

---

# 15. Current Experiments

No experiment should be treated as active until its implementation and measurement are verified.

| Experiment | Status | Owner | Primary Metric |
|---|---|---|---|
| None verified in this status file | NONE VERIFIED | - | - |

Active experiments should also be tracked in `EXPERIMENTS.md`.

---

# 16. Current Incidents

**No incident status has yet been verified.**

This does **not** mean there are no incidents.

Production inspection is required.

When an incident is active, record:

- ID
- severity
- start
- impact
- coordinator
- current state
- mitigation
- next update

Historical incidents belong in `INCIDENTS.md`.

---

# 17. Current Blockers

**Corrected 2026-09-20, scheduled operator cycle.** This section had stood
as the unfilled 2026-08-16 bootstrap template naming three blockers as not
yet started; two of the three have since been substantively resolved and
the third is narrower than originally stated. Updated against real,
currently-checkable state rather than left to describe a moment 5 weeks
past.

## BLOCKER-001: Production State Verifiable Only From a Session With Real Access

**RESOLVED 2026-09-25 14:15 UTC, this session: production redeployed and
verified, and the gap it closed was customer-visible.** `ops/deploy.py`
confirms production now serves build `d40585d97500a3ca` (commit `5ff17fcb`),
matching the repository.

What was actually behind: four room decks. `site/deck.html` is the hub that
links every deck, and a concurrent session had shipped Primary Bathroom,
Laundry Room, Home Office and Garage. All four returned **404 in production**
while the repository believed they existed. The live hub had not yet been
rebuilt, so no visitor met a broken link, which is luck rather than design:
had the hub deployed one build earlier than its targets, it would have shipped
four dead links on the page whose whole job is linking them.

Verified after deploying, on the live site rather than in the repository: all
six deck pages return 200 (130 KB to 177 KB), all six are linked from the live
hub, and the Garage deck renders all seven of its zones and 80 cards with
`site.js` present.



**Corrected 2026-09-25, scheduled operator cycle: both the Status line below and the "Production Knowledge" paragraph under Current Overall Assessment were citing a superseded confirmation.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, resolving via `resolve_verdict_commit()`/`git log -S` to commit `c6cc1a6a` (B9's Laundry Room deck). `deploy_gap_material_commits()` finds 5 material commits since (`8f6c47b3` build-id fix, `9c6d4063` the five-deck og:image fix, `e6017e8b`/`f3ceca2e`/`2cb970c1` B9's Garage/Primary Bathroom/Home Office decks), touching 8 distinct `site/`/`Dockerfile` files. No P0 regression: the gap is three new free deck pages and one image-metadata fix, undeployed until the next redeploy. No sandboxed session here holds the deploy key, so this is read from the committed verdict, not re-checked live against the VPS itself; `gate_status_deploy_verdict_current` caught the stale citation, not a live production check.

**Status: RESOLVED (as of 2026-09-25 14:15 UTC, production level with the repository at build `d40585d97500a3ca`, commit `5ff17fcb`, verified live by `ops/deploy.py` rather than read from a committed verdict), structurally recurring.** The 07:30 REOPENED line above it is superseded: the five commits it named, including B9's Garage, Primary Bathroom and Home Office decks, are the ones this deploy shipped. No sandboxed
operator session has ever held the VPS deploy key or egress to
`6s-success.com`, so this half genuinely cannot be verified from here on
any cycle, not just this one; it is a standing structural limit, not an
unstarted task. What IS known: the repository's own deploy-freshness
check (`ops/deploy_freshness.py`, `ops/deploy-verdict.json`) previously
went stale at 233 commits behind (last confirmed 2026-09-18T17:20:47Z,
build `7c765b634045a89c`), flagged by the 2026-09-20 11:12 PM check-in.
Phil redeployed twice that day, from a session with real production
access (`470834de`, then `7ae0e9b6`): the tracked verdict read current at
2026-09-20T17:46:50Z, build `d9fc700d0700972f`.

**Corrected 2026-09-23 20:0x, PM check-in: a newer confirmation superseded the 13:4x one, same closed state.**
`ops/deploy-verdict.json`, read directly rather than cited, now records
`verdict: "current"`, build `5eba61fde231c1a7`, `checked_at:
2026-09-23T19:00:39Z`, from a later session with real production access
that finished the Stripe SKU retirement (65 of 65 confirmed archived) and
redeployed. `site/build-id.txt` at HEAD read the same build id at that
time, so the marker and the repository agreed then.

**Reopened 2026-09-24 03:5x, PM check-in: the gap has grown to 47 commits and now includes a second live customer-facing defect, not just internal-consistency work.** `git log 8e4c8e33..HEAD` (the last deployed commit to HEAD): 47 commits. Two are not narrow: `a16788fa` fixed a real, live dead-nav-menu defect on `404.html`, `corporate.html`, `kit.html`, and 2 B2B articles (same class as `8e4c8e33` itself, which is why production is *already* known to have shipped this exact defect once): every one of those pages still ships the broken hamburger button in production right now, over 8 hours after the fix was committed. `b0166730` finished retiring the last of 65 dead/superseded Stripe SKUs, so production's catalogue is stale by that much too. No operator sandbox holds the deploy key or egress to verify or fix this itself, so the next confirmation still needs a session with real access, same structural limit as every prior occurrence, but this is no longer "nothing open to close": a real, known, live defect is sitting unfixed for customers, and the fix has been sitting ready in the repository for over 8 hours.

**Corrected 2026-09-24 04:1x, PM check-in: the 47-commit figure was already stale within one cycle; a third live defect has entered the gap.** Re-derived directly rather than repeated: `git log 8e4c8e33..HEAD` is now 50 commits, over 9 hours behind the last confirmed deploy. `a16788fa` (dead-nav-menu, 5 pages) and `b0166730` (65/65 SKU retirement) are unchanged from last cycle. New: `b6b35ee7` fixed invalid JSON-LD on both B2B articles (`what-a-5s-engagement-costs.html`, `why-5s-decays-after-six-months.html`), single-quoted Python literals rather than valid JSON, which had made both blocks unparseable by any real structured-data consumer and had silently excluded both articles from `feed.xml`; that fix, and the `feed.xml`/`sitemap.xml`/`llms.txt` regeneration it required, are also sitting undeployed. Still the same structural limit: no operator sandbox holds the deploy key or VPS egress, confirmed again directly this cycle (no key at `~/.ssh`, `curl` to `6s-success.com` `connect_rejected` by the agent proxy). This number will keep growing every cycle until a session with real access redeploys; the standing instruction for future cycles is to re-derive it with `git log`, not cite the last cycle's figure.

**Updated 2026-09-24 05:0x, scheduled operator: the image-publish half of this gap is closed, the VPS half is not.** `publish-image.yml`'s last attempt (commit `b6b35ee7`) had failed on an unrelated, already-fixed log-ordering gate, and nothing since had touched a `site/`-triggering path to retry it, so no current image existed to redeploy even if a session with VPS access ran one. Dispatched the workflow directly (it accepts `workflow_dispatch` alongside its push trigger); run 395 finished `success`. A fresh image built from current `main` is now published to `ghcr.io/klingdom/6s-success` and ready for the host's `Redeploy` click. The underlying commit gap and the three live defects named above are unchanged; only the "is there an image ready to pull" question has moved from no to yes.

**Independently confirmed 2026-09-24 05:1x, PM check-in, same conclusion from a different angle: this cycle happened to hold a working `GH_TOKEN` (rare for a sandboxed session today) and read `publish-image.yml`'s history directly rather than trust the operator's own account. Same fact, verified rather than merely cited: `git diff --quiet 914c2881 HEAD -- site/ Dockerfile` returns clean, confirming the GHCR image already matches HEAD.** `git log 8e4c8e33..HEAD` is 59 commits, but that count now measures undeployed work only, not unbuilt work; the one remaining step is Phil's Redeploy click in Hostinger (or a session with the VPS key running `ops/deploy.py`), per `OWNER-ACTIONS.md` item 1b.

**Re-confirmed 2026-09-24 05:4x/05:5x, two concurrent PM/operator cycles: unchanged, no new live defect.** `git log 8e4c8e33..HEAD` is 60 commits after this merge, growth being routine check-ins and log entries, not new site work. The two cycles collided on the same standing `wire_*.py` cold-read handoff (both closed it clean independently, folded into one account in section 1's "Last Updated" notes above rather than left as two competing claims) and merged rather than one overwriting the other. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**Re-confirmed 2026-09-24, this PM check-in: unchanged, no new live defect.** `git log 8e4c8e33..HEAD` is now 66 commits, growth again being routine check-ins, not new site work. `git diff --quiet 914c2881 HEAD -- site/ Dockerfile` re-run and still clean, so the GHCR image still carries every fix named above. `preflight.py` run to completion: every gate passed, 23 warnings, all previously diagnosed sandbox limits, none new. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**Re-confirmed 2026-09-24 18:1x, PM check-in: unchanged, no new live defect, and a newer build confirmation found than the one this section had been citing.** `git log 8e4c8e33..HEAD` is now 127 commits. Rather than re-run the `914c2881` diff again, checked GitHub Actions directly: `publish-image.yml` has since built and published successfully from a later commit anyway, run 398 (`https://github.com/Klingdom/6s-success/actions/runs/36032909521`, a plain push build, no dispatch needed), `success` at 2026-09-24T17:35:17Z against commit `accc9fff`. `git diff --quiet accc9fff HEAD -- site/ Dockerfile` is clean, so the GHCR image matches HEAD through the newer, later-confirmed commit, not just the older one this section named. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**RESOLVED 2026-09-24 19:2x, PM check-in: the redeploy this section has been waiting on since 05:0x already happened, and nobody had told this section.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `4ec571da81db3b34`, `checked_at: 2026-09-24T18:47:16Z`, written by `ops/deploy.py`'s own `write_verdict_marker()`, which only ever runs from a session that just confirmed production live by a real, credentialed check (committed in `44ef380a`, a Phil-authored commit co-authored by Claude, the same "local session holding `~/.ssh/6s_deploy`" pattern this file has recorded doing the redeploy on every prior occasion, not Phil clicking anything himself). `site/build-id.txt` at HEAD (`ef417f10`) reads the identical `4ec571da81db3b34`, and `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is clean, so no commit since that confirmation has touched anything a redeploy would need to carry. The gap this section spent all day narrating (47, then 50, then 60, then 66, then 127 commits) is zero right now: production is confirmed serving exactly what HEAD serves. This sandbox holds no VPS key (confirmed again this cycle: no file at `~/.ssh/6s_deploy`), so this is read from the committed verdict, not re-checked live; the structural limit BLOCKER-001 names (no sandboxed session can verify or redeploy production itself) still stands for the next time a `site/**` commit lands after this confirmation, which is why this is closed as of right now, not closed permanently.

**Reopened 2026-09-24 21:1x, PM check-in: the auto-deploy workflow fired end to end for the first time and proved it still cannot act, because `VPS_DEPLOY_KEY` has not been pasted; the gap is real again, 20 commits.** `git log 44ef380a..HEAD` is 20 commits, `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is dirty (29 files, mostly the Micro Zones "Primary Bathroom personalised" content shipped this cycle). `publish-image.yml` run 399 built and published clean from `d5b0d5c8` at 2026-09-24T21:06:42Z; `git diff --quiet d5b0d5c8 HEAD -- site/ Dockerfile` is clean, so the GHCR image already matches HEAD. `.github/workflows/deploy.yml` (added earlier today, `STATUS.md` section 1) then fired automatically for the first time, `workflow_run` off that publish, run 5, completed `success` at 2026-09-24T21:07:19Z. Read its own job log rather than trust the green checkmark: the "Deploy" step itself shows `conclusion: skipped`, exactly the no-op its own first step is built to do when `VPS_DEPLOY_KEY` is absent, confirmed absent in this sandbox (`ls ~/.ssh` empty). So the automation is proven wired correctly end to end, and still cannot close this gap without the one paste in `OWNER-ACTIONS.md` item 0 / GitHub issue #35. Production is confirmed stale by the 29 files above until either that secret is added or a session holding `~/.ssh/6s_deploy` runs `ops/deploy.py` by hand.

**RESOLVED 2026-09-24, later, scheduled operator cycle: a session holding real access redeployed again, then one more site commit landed after it, same recurring shape.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `28ed2709194afab5`, `checked_at: 2026-09-24T21:10:12Z`, matching commit `d5b0d5c8` (`git show d5b0d5c8:site/build-id.txt` is the same id); `git diff --quiet d5b0d5c8 HEAD~1 -- site/ Dockerfile` (against `869d4e93`, the commit that redeploy confirmation covers) is clean, so that redeploy did close the 21:1x gap in full at the time it ran. **Reopened by the same structural pattern within one cycle:** `869d4e93` ("Micro zones: Home Office personalised") landed immediately after, touching `site/`, and moved `site/build-id.txt` to `6e4992daa2791557`; `git diff --quiet d5b0d5c8 HEAD -- site/ Dockerfile` is dirty again (1 commit, `869d4e93`; this session's own `f62cc3ea` touches only `ops/` and a root CSV, not `site/` or `Dockerfile`, so it adds nothing to the gap). Still the same standing limit: this sandbox holds no `~/.ssh/6s_deploy` and no VPS egress (confirmed again, `ls ~/.ssh` empty), so this cannot be closed from here; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is what would make this stop recurring instead of being rediscovered every cycle.

**Widened 2026-09-24, later, scheduled operator cycle: the entry above's own commit count had already gone stale by the time this cycle read it, and a new gate now checks for exactly this.** The build_id citation (`28ed2709194afab5`) was still correct, but two further site-affecting commits landed after the entry above was written and neither was mentioned: `29a84fa2` ("Correct 13 wrong cause IDs across two rooms") and `b8eca135` ("Micro zones: Laundry Room personalised"). A fresh recount (`git log d5b0d5c8..HEAD -- site/ Dockerfile`, `d5b0d5c8` being the commit build_id `28ed2709194afab5` actually came from) puts the real gap at (3 commits, `869d4e93`, `29a84fa2`, `b8eca135`; 55 files, 805 insertions, 479 deletions), not the 1 commit the entry above named. No new live defect beyond the recurring structural one; this is the same gap, just correctly sized now. New `gate_status_deploy_gap_count_current` in `preflight.py` (pure logic in `deploy_gap_count_problem`, `ops/tests/test_gate_status_deploy_gap_count_current.py`, 6 cases) re-derives which commit a deploy verdict's build_id actually came from and recounts the real gap from there, so a correct build_id citation next to a stale commit-count no longer passes silently the way `gate_status_deploy_verdict_current` alone allowed it to; fail-then-pass proved directly (the test's own synthetic "(1 commit)" claim against a real count of 3 fails by name, "(3 commits)" passes), and it fired correctly against this exact live drift before this correction was written. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key.

**RESOLVED then reopened, 2026-09-25 00:1x, PM check-in: the entry above's own build_id citation was itself already superseded, not just its commit count.** Before correcting the "3 commits" figure by re-deriving from the same `28ed2709194afab5`/`d5b0d5c8` citation the entry above used, checked `ops/deploy-verdict.json` directly rather than trust that citation, per this file's own repeated lesson. It now records a newer confirmation: `verdict: "current"`, build `6a10df205a3d058c`, `checked_at: 2026-09-24T23:35:51Z`, unread by any prior entry in this section. `git log -S6a10df205a3d058c -- site/build-id.txt` resolves that build to commit `b8eca135` ("Micro zones: Laundry Room personalised"), so a session with real access redeployed again after the 21:1x confirmation and closed the gap in full at that time: `git diff --quiet b8eca135 HEAD~1 -- site/ Dockerfile` is clean. **Reopened by the same recurring pattern within the same cycle:** `ca49aa25` (Phil's own "Micro zones: Garage personalised") landed immediately after and touches `site/`; `git diff --quiet b8eca135 HEAD -- site/ Dockerfile` is dirty again, real gap now (1 commit, `ca49aa25`; 44 files, 547 insertions, 323 deletions), not the 4 the superseded recount above would have named against the older build. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key. Direct call to this repository's own `deploy_gap_count_problem()` against the corrected text below confirms clean.

**Widened 2026-09-25 01:4x, PM check-in: the entry above's own commit count had already gone stale, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run rather than assumed clean.** The build_id citation (`6a10df205a3d058c`) is still correct, resolving to commit `b8eca135` (`git log -S6a10df205a3d058c -- site/build-id.txt`). A fresh recount (`git log b8eca135..HEAD -- site/ Dockerfile`) finds two commits touching `site/`, not the one the entry above named: `fa78db8c` (Phil's own D-026 checkpoint, which shipped `measure.js`'s new `zone-block-seen` instrumentation to every zone page) landed the same day as `ca49aa25` and was not counted. Real gap is now (2 commits, `fa78db8c`, `ca49aa25`; 197 files, 808 insertions, 520 deletions). No new live defect beyond the recurring structural one; this is the same gap, just correctly sized. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key. Direct call to this repository's own `deploy_gap_count_problem()` against the corrected text confirms clean.

**Widened 2026-09-25, scheduled operator cycle: the entry above went stale within the same day, same recurring pattern, caught again by `gate_status_deploy_gap_count_current` before this cycle touched anything else.** The build_id citation (`6a10df205a3d058c`) is still correct, still resolving to commit `b8eca135`. A fresh recount (`git log b8eca135..HEAD -- site/ Dockerfile`, cross-checked against `preflight.py`'s own `resolve_verdict_commit`/`deploy_gap_material_commits`) finds three commits, not the two the entry above named: `ca49aa25`, `fa78db8c`, and `6ba42a27` ("Close 13 real gaps in \"how to clean anything\", and fix the page that promised it"), which landed after the entry above was written and was not counted. Real gap is now (3 commits, `ca49aa25`, `fa78db8c`, `6ba42a27`; 198 files, 975 insertions, 3518 deletions per `git diff --shortstat b8eca135 HEAD -- site/ Dockerfile`). No new live defect beyond the recurring structural one; this is the same gap, just correctly sized, and it will keep growing every cycle site work lands until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is set or a session holding `~/.ssh/6s_deploy` redeploys. This entry does not chase the count further after this correction: the gate that catches the drift already exists and fires correctly on every cycle's `preflight.py` run, so a fresher recount belongs to whichever cycle next touches this section, not to a loop of same-day corrections that adds no new information beyond "the number moved."

**Widened 2026-09-25, scheduled operator cycle: the entry above had already gone stale by one commit, and that commit is the P0 footer-restoration fix, not a routine content push.** `gate_status_deploy_gap_count_current` fired on this cycle's own `preflight.py` run. Same build_id (`6a10df205a3d058c`), same resolved commit (`b8eca135`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-24T23:35:51Z`, so no new redeploy has happened since the last confirmation. A fresh `git log b8eca135..HEAD -- site/ Dockerfile` now finds four commits, not three: `2d8077fd` ("Restore the site footer to all 134 room and zone pages, and stop the gate that missed it from staying silent") landed after `6ba42a27` and was not counted. Real gap is now (4 commits, `ca49aa25`, `fa78db8c`, `6ba42a27`, `2d8077fd`; 198 files, 1089 insertions, 684 deletions per `git diff --shortstat b8eca135 HEAD -- site/ Dockerfile`). This one is worth flagging by name rather than only by count: `2d8077fd` is the fix for the live P0 defect found earlier this same day (all 134 room/zone pages shipping with no footer, no privacy/terms/accessibility/safety links, no newsletter form), so until a redeploy happens, production is still missing that footer even though the repository has carried the fix for hours. No new structural change; same standing limit, `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**RESOLVED 2026-09-25 05:4x, PM check-in: a session holding real access redeployed again, and the footer fix named above is now confirmed live.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`. Resolved the build_id to the commit that set it (`git log -Saa7c7e7e578e9a18 -- site/build-id.txt`) rather than trust the number alone: it is `890c43a3` ("Restore the footer, legal links and newsletter form to all 114 zone pages and 20 room pages"), an earlier, independent fix for the identical defect `2d8077fd` also fixed; the two produced byte-identical output (both build to `aa7c7e7e578e9a18`, confirmed by reading `site/build-id.txt` at each commit directly), so whichever one production is confirmed against carries the fix either way. `git log 890c43a3..HEAD -- site/ Dockerfile` returns zero commits: production matches HEAD exactly right now, footer included, no gap. Same standing limit as every entry above: this sandbox holds no `~/.ssh/6s_deploy` or VPS egress, so this closes again the moment the next `site/**` commit lands without a following redeploy, per `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) still being the only fix for the recurrence itself, not for this instance of it.

**Reopened 2026-09-25 07:1x, PM check-in: the same recurring pattern, one real customer-facing commit undeployed.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Verified with this repository's own `resolve_verdict_commit()`/`deploy_gap_material_commits()` directly rather than a fresh `git log` invocation: real gap is (2 commits, `ad310568`, `cb37d0c8`; 4 files, 439 insertions, 2 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). `ad310568` is a merge carrying no independent site content; the real one is `cb37d0c8`, B9's new free `site/entryway-deck.html` page, live in the repository but not yet served to a visitor. No P0 regression, just new content sitting undeployed. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25 08:0x, PM check-in: the entry above had already gone stale by one commit, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (3 commits, `ad310568`, `cb37d0c8`, `c6cc1a6a`; 5 files, 908 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). `ad310568` is a merge carrying no independent site content; the two material ones are `cb37d0c8` (B9's Entryway deck) and the newly landed `c6cc1a6a` (B9's Laundry Room deck, `site/laundry-room-deck.html`), both live in the repository, neither served to a visitor yet. No P0 regression, just a second new free page joining the first behind the same undeployed gap. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25 09:1x, PM check-in: the entry above had already gone stale by two commits, same recurring pattern.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (5 commits, `1b6439a7`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 6 files, 1372 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). Three are material: `cb37d0c8` (B9's Entryway deck), `c6cc1a6a` (B9's Laundry Room deck), and the newly landed `2cb970c1` (B9's Home Office deck, `site/home-office-deck.html`, third of five rooms). `1b6439a7` and `ad310568` touch only `site/build-id.txt`/carry no independent content, same as before. No P0 regression, just a third new free page joining the other two behind the same undeployed gap. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25, scheduled operator cycle: two more room decks landed, closing B9 in full; the gap is now every remaining room-deck page, not the first three.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (6 commits, `e6017e8b`, `f3ceca2e`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 8 files, 2376 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). Five are material: `cb37d0c8` (B9's Entryway deck), `c6cc1a6a` (B9's Laundry Room deck), `2cb970c1` (B9's Home Office deck), `f3ceca2e` (B9's Primary Bathroom deck), and this cycle's own `e6017e8b` (B9's Garage deck, `site/garage-deck.html`, the fifth and last room, closing B9 in full). `ad310568` is a merge carrying no independent site content, same as every prior entry. No P0 regression, just a fifth new free page joining the other four behind the same undeployed gap; all five room decks now live in the repository and none served to a visitor yet. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25, PM check-in: the entry above had already gone stale by two commits, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (8 commits, `8f6c47b3`, `9c6d4063`, `e6017e8b`, `f3ceca2e`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 8 files, 2376 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). One is newly material: `9c6d4063`, the fix for five room-deck pages sharing the Kitchen chapter photo as their social-media preview image (a real, live-facing correctness fix, still undeployed). `8f6c47b3` and `ad310568` touch only `site/build-id.txt` or carry no independent content, same as every prior entry's own build-id/merge commits. No new P0 regression beyond the standing gap; this is the same structural wait, just correctly sized. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**NARROWED 2026-09-25 14:2x, PM check-in: a session with real access redeployed again since the entry above, closing the Entryway and Laundry Room decks' half of that gap; three room decks and both fixes above remain undeployed.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, superseding `aa7c7e7e578e9a18`. Resolved with `resolve_verdict_commit()` rather than assumed: it is `c6cc1a6a` (B9's Laundry Room deck). Confirmed with `git merge-base --is-ancestor` that both `cb37d0c8` (Entryway) and the merge `ad310568` are ancestors of `c6cc1a6a`, so that redeploy carried both of last cycle's "material" commits, not zero. Re-derived the remaining gap with `deploy_gap_material_commits(c6cc1a6a)` directly: five commits, `8f6c47b3`, `9c6d4063`, `e6017e8b`, `f3ceca2e`, `2cb970c1`; 8 files, 1476 insertions, 8 deletions per `git diff --shortstat c6cc1a6a HEAD -- site/ Dockerfile`. Three are B9 room decks not yet served to a visitor (Home Office, Primary Bathroom, Garage, the last three of five), one is the Kitchen-photo og:image correctness fix, one is a build-id restamp only. No P0 regression; the gap shrank, it did not close. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Reopened 2026-09-26 04:2x, PM check-in: the gap is real again, 3 material commits, and one of them is a real customer-facing honesty defect still live in production right now.** `ops/deploy-verdict.json` unchanged since the top-of-section RESOLVED note (build `d40585d97500a3ca`, `checked_at: 2026-09-25T14:15:05Z`, resolving via `resolve_verdict_commit()` to `8f6c47b3`); no new redeploy confirmation since. Re-derived with `deploy_gap_material_commits()` against that resolved commit directly, rather than a fresh manual `git log`: three commits, `ac1af6e7`, `ba73ec3c`, `223f5111`. `ac1af6e7` is internal (a `preflight.py` gate fix and a sitemap regeneration, no visible content change). The other two are customer-facing: `223f5111` links 44 room/zone pages to their decks (previously dead anchors), and `ba73ec3c` is the fix, shipped this same day, for `render_room()` claiming "not one product below carries a paying link" directly above real outbound `target.com`/`homedepot.com` links on all 20 room pages with a kit. That false disclosure is still what production serves until the next redeploy: the repository has carried the honest text for over an hour, and every visitor to a room page in that window has read the wrong claim. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again, `~/.ssh` has no deploy key, `curl` to `6s-success.com` is rejected by the agent proxy).

**Widened 2026-09-26, PM check-in: the entry above had already gone stale, and the "3 material commits" figure in its own header undercounted even at the time it was written.** Same build_id (`d40585d97500a3ca`), same resolved commit (`8f6c47b3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T14:15:05Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()` (default `git log`, not `--full-history`) rather than cited: real gap is now (5 commits, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`, `223f5111`). Note that this same function no longer lists `ac1af6e7` at all: git's default path-history simplification drops it once its net effect on `site/`/`Dockerfile` is folded into the surrounding merges, which is why the entry above could name "three commits" including it while the canonical count this repository has used throughout `BLOCKER-001`'s history was already 2 material (`ba73ec3c`, `223f5111`) even then, not 3. Three of the five current commits are material: `223f5111` (44 dead deck anchors, fixed) and `ba73ec3c` (the false no-affiliate-link disclosure fix on all 20 room pages) both already named above and still undeployed, plus the newly landed `dd9c0a01` (the Kitchen deck's Room card and page intro falsely claimed the Sink zone was the kitchen's shortest; it is not, per `content.json`'s own session-time data). `0f1641cb` and `89a030a5` are a build-id restamp and a sitemap-lastmod regeneration with no visible content change. No new P0 beyond the standing gap; the false room-page disclosure is still what production serves, now joined by one more false claim on the live Kitchen deck. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh/6s_deploy`, `curl` to `6s-success.com` rejected by the agent proxy).

**Widened 2026-09-26 19:4x, PM check-in: caught live by `gate_status_deploy_gap_count_current`, the entry above had already gone stale by two more commits.** Same build_id (`d40585d97500a3ca`), same resolved commit (`8f6c47b3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T14:15:05Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`, not cited: real gap is now 7 commits (`dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`, `223f5111`, `441a8208`, `dec5660a`). The two new ones: `441a8208` is a build-id/sitemap restamp, no visible content. `dec5660a` is material and customer-facing: `room_time()`'s rounding broke exact ties toward the nearest even half hour instead of up, so 9 of 20 room pages (Kitchen, Primary Bedroom, Guest Bedroom, Kids Bedroom, Primary Bathroom, Home Office, Garage, Stair Landing, Patio or Deck) understated their stated time range and FAQPage JSON-LD by half an hour; fixed in the repository, still serving the wrong number in production until the next redeploy. Four of the seven current commits are now material: `223f5111`, `ba73ec3c`, `dd9c0a01` (named above) plus `dec5660a`. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again this cycle).

**Superseded 2026-09-26 19:5x, PM check-in: a real redeploy landed concurrently while the entry above was being written, caught by `gate_status_deploy_verdict_current` on the very next preflight run.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `a6c5f96b77c7cff2`, `checked_at: 2026-09-25T22:21:27Z` (later than the 14:15:05Z confirmation every entry above cites), via a concurrent commit from a session with real production access (`fbeba2f7`, which also carried a real content fix: content.json's Kitchen Cooking Zone `purpose` had a typo reaching 21 downstream artifacts, corrected there). `resolve_verdict_commit()` resolves this build to `223f5111`, the same commit named as material and undeployed just above; it is deployed now. Re-derived the remaining gap with `deploy_gap_material_commits(223f5111)` directly: 8 commits (`0ce148e7`, `fbeba2f7`, `441a8208`, `dec5660a`, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`). Of these, `fbeba2f7` is itself material (the Kitchen zone content fix above, plus a Kitchen deck print PDF refresh and a sitemap-lastmod restamp), `dec5660a` and `dd9c0a01` are the room-time and shortest-zone fixes already named above, and `ba73ec3c` is the affiliate-disclosure fix already named above: 4 material. `0ce148e7` is the merge that reconciled two branches by regenerating already-tracked generated files (room pages, sitemap), not new material beyond what the commits above already carry; `441a8208`/`0f1641cb`/`89a030a5` are build-id/sitemap restamps only. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**Widened 2026-09-26 21:1x, PM check-in: `gate_status_deploy_gap_count_current`'s own regex could not parse this section's newest phrasing ("N commits (`hash`...)"), so it had silently stopped checking the moment that phrasing appeared above; fixed the regex (`ops/preflight.py`, proved fail-then-pass in `ops/tests/test_gate_status_deploy_gap_count_current.py`), and the real drift it should already have caught is now visible.** Same build_id (`a6c5f96b77c7cff2`), same resolved commit (`223f5111`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T22:21:27Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits(223f5111)`: real gap is now 9 commits (`4afe5b0d`, `0ce148e7`, `fbeba2f7`, `441a8208`, `dec5660a`, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`). The new one, `4afe5b0d`, is material and customer-facing: the last standing British spelling in the free sample PDF (page 243, "organised"), the lead magnet a stranger reads before ever reaching checkout. Five of the nine current commits are now material: `fbeba2f7`, `dec5660a`, `dd9c0a01`, `ba73ec3c` (named above) plus `4afe5b0d`. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**Widened 2026-09-27 07:0x, PM check-in: caught live by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run, the entry above had gone stale by five more commits, none of them a new customer-facing defect.** Same build_id (`a6c5f96b77c7cff2`), same resolved commit (`223f5111`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T22:21:27Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits(223f5111)`, not cited: real gap is now 14 commits (`979ceeba`, `9f5a302c`, `27ce7c92`, `c190ea51`, `329860ac`, `4afe5b0d`, `0ce148e7`, `fbeba2f7`, `441a8208`, `dec5660a`, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`). The five new ones, all from the cold-read lane's own close: `c190ea51` is a build-id restamp only, and `979ceeba` (the merge that reconciled two concurrent cold-read pushes) carries fingerprint version bumps across 202 pages plus already-tracked generated files, no visible content change. `27ce7c92` and `9f5a302c` are the same fix landed twice by two racing sessions before they merged: a dead DOM id selector, `#p-done-wrap`, removed from `quest.js`, explicitly no behaviour change since that selector never matched anything in shipped HTML. `329860ac` is a real bug fix in `measure.js` (a throwing `umami.track()` call was being counted as delivered and never retried, silently losing the event) but is not customer-visible: no page renders differently, only analytics fidelity improves. The same five commits already named material stay material and unchanged: `fbeba2f7`, `dec5660a`, `dd9c0a01`, `ba73ec3c`, `4afe5b0d`. No new P0. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh/6s_deploy`, `curl` to `6s-success.com` rejected by the agent proxy).

**Widened 2026-09-27 07:3x, PM check-in: caught live again by `gate_status_deploy_gap_count_current`, the entry above had gone stale by six more commits in roughly six minutes; the material count did not move.** Same build_id (`a6c5f96b77c7cff2`), same resolved commit (`223f5111`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T22:21:27Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits(223f5111)`, not cited: real gap is now 20 commits (`979ceeba`, `9f5a302c`, `27ce7c92`, `c190ea51`, `329860ac`, `4afe5b0d`, `0ce148e7`, `fbeba2f7`, `441a8208`, `dec5660a`, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`, `8154a5f8`, `cfb56c86`, `3ec6ad43`, `5ecc24d7`, `ec95bb55`, `c1c89b4e`). Six of these are new since the entry above: `8154a5f8` removes a dead `priceLo`/`priceHi` price range branch from `site.js`, already unreachable since D-023's retirement, no visible behaviour change. `cfb56c86`, `5ecc24d7`, `ec95bb55`, `c1c89b4e` are merges and command-deck restamps carrying no independent content. `3ec6ad43` removed 25 duplicate CSS rules from the book stylesheet; that cycle's own log entry proved the rendered output pixel identical at ten scroll positions before shipping it, so it is not material either. The material count stays at 5, unchanged: `fbeba2f7`, `dec5660a`, `dd9c0a01`, `ba73ec3c`, `4afe5b0d`. At this repository's current commit velocity, several concurrent sessions landing roughly one site touching commit every minute or two in bursts, the raw count is a moving target and retyping it to an exact figure every cycle is not the fix; the figure worth watching going forward is the material list, and it has not grown since the entry above. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**Widened 2026-09-27 21:5x, scheduled operator cycle: caught live again by `gate_status_deploy_gap_count_current`, and this time the material list did grow.** Same build_id (`a6c5f96b77c7cff2`), same resolved commit (`223f5111`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T22:21:27Z`. Re-derived directly with `deploy_gap_material_commits(223f5111)`: real gap is now 21 commits, one more than the entry above, the new arrival being Phil's own `1ae12630f` ("No zone page ships imageless: a typographic hero for the three with no photograph"). Checked, not assumed: this one is material, a real, customer-visible fix to three live zone pages (replacing a blank space where a rejected photographic hero used to leave nothing with a typographic panel quoting the zone's own `done_looks_like` text), not a dead-code removal or a proven-identical dedup like every commit the entry above screened out. **Material count: 6, not 5** (`fbeba2f7`, `dec5660a`, `dd9c0a01`, `ba73ec3c`, `4afe5b0d`, `1ae12630f`). Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**Widened 2026-09-27 22:4x, PM check-in: caught live again by `gate_status_deploy_gap_count_current`, one more commit, and it is material again.** Same build_id (`a6c5f96b77c7cff2`), same resolved commit (`223f5111`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T22:21:27Z`. Re-derived directly with `deploy_gap_material_commits(223f5111)`: real gap is now 22 commits, one more than the entry above, the new arrival being Phil's own `7c6a83084` ("Finish it: no page on this site ships with no image, room pages included"). Checked, not assumed: this one is material, a real, customer-visible fix to the nine of twenty room pages whose chapter carries no illustration, replacing a bare wall of text with a typographic panel built from the room's own intro, the same pattern the zone pages and `1ae12630f` above already use. **Material count: 7, not 6** (`fbeba2f7`, `dec5660a`, `dd9c0a01`, `ba73ec3c`, `4afe5b0d`, `1ae12630f`, `7c6a83084`). Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**RESOLVED 2026-09-27 23:1x, PM check-in: a session with real production access redeployed and verified live, closing the entry above in full, including the exact commit it had just flagged as newly undeployed; production now matches HEAD exactly.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `159acc34b643d712`, `checked_at: 2026-09-27T22:45:39Z`, a newer confirmation than the `a6c5f96b77c7cff2`/`223f5111` pair the entry above cites (that entry's own 22:4x check-in and this one ran concurrently; this one happened to read the newer verdict). This is the same check Phil's own `9b0de5cd4` ("LRN-0020: when a gate has no available action, change the format, not the blocker") records in its own commit message: "Deployed and verified live: production serves 159acc34b643d712 and matches the repository." Resolved with `resolve_verdict_commit()` rather than assumed: it is `7c6a83084` ("Finish it: no page on this site ships with no image, room pages included"), the exact commit the entry above names as the new material arrival; it is not undeployed, it is what this redeploy shipped. `git log 7c6a83084..HEAD -- site/ Dockerfile` is empty: no site- or Dockerfile-touching commit has landed since, including every scheduled operator and PM cycle between then and now (all of which touched only `STATUS.md`, `NIGHTLY-LOG.md`, `LEARNINGS.md`, or the command deck, confirmed by reading their own diffs' file lists rather than assumed from their subject lines). Production is confirmed current with HEAD, right now, not merely reported clean by a stale citation. Same standing limit as every entry above: no operator sandbox holds `~/.ssh/6s_deploy` or VPS egress (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy), so this closes again the moment the next `site/**` commit lands with no session to follow it; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Widened 2026-09-28 14:4x, PM check-in: one real, material commit landed since the 23:1x redeploy and is still undeployed.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 1 commit, `a74dba749` ("Fix: quest.html's 429KB card deck no longer blocks the symptom picker's download start", A10's safe half in `BACKLOG-2026-09-07.md`). Checked, not assumed: this is material, a real customer-facing performance fix to `quest.html`, the app's own entry point, moving four script tags (including the 429KB `quest-data.js`) from the foot of `<body>` into `<head>` with `defer` so the download starts as soon as the parser reaches the tag instead of after the whole page is read; production is still serving the slower, old script placement until the next redeploy. No P0 regression, no false claim newly live, just the standing recurring gap, once more. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy).

**Widened 2026-09-28 15:2x, PM check-in: A10's hard half landed and is also undeployed, the entry above was already one commit stale, and a third landed while this correction was in progress.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited, after rebasing onto a concurrent session's own push: real gap is now 3 commits. `a74dba749` (unchanged from the entry above). `80a111d1d` ("A10: split quest-data.js so the symptom picker does not wait on the manual", A10's hard half): a new 3KB `quest-data-symptoms.js` now loads eagerly instead of the 419KB full manual, with the manual itself deferred to lazy load only once a visitor needs it (`ensureRooms()`/`loadRooms()`). `a221c7a9c` ("Fix-forward: renderKeep() gate regression and stale fingerprint from A10"), landed by a concurrent session that independently found and fixed the exact same `gate_quest_keep_releases_urls_first` regression this check-in was about to fix itself: `80a111d1d`'s lazy-load wrapper had made `ensureRooms()` the first statement of `renderKeep()` instead of `releaseUrls()`, reopening a blob-URL leak an existing gate exists to catch; both sessions reached the same root cause and the same fix independently, confirmed in CI's own logs (`checks.yml` run 1561, `Preflight` step, `failure`) before this check-in trusted its own local diagnosis. Converged onto the concurrent push via rebase rather than duplicate the fix. Production is still serving the pre-A10 code until the next redeploy. No P0 regression, no false claim newly live, just the standing recurring gap, once more. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy).

**Widened 2026-09-28 23:5x, scheduled operator cycle: the "3 commits" figure above had gone stale again, the same recurring shape, while no redeploy happened in between.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 5 commits, not 3. The three named in the entry above are unchanged and still undeployed. Two more landed since: `46ff9077f` ("Fix live grammar defect: garage-deck.html's abstract read 'A 80 card deck', should be 'An 80'", a small live copy fix on a customer-facing page) and `4d7189c1d` ("Restamp build-id after the prior commit's site content change", a mechanical follow-on with no content of its own). No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy).

**Widened 2026-09-29, PM check-in: the "5 commits" figure above had gone stale by two more, and the gate that should have caught it had gone silent again on a third phrasing.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 7 commits, not 5 (30 files, 957 insertions, 287 deletions per `git diff --shortstat 7c6a83084 HEAD -- site/ Dockerfile`). The five named above are unchanged and still undeployed. Two more landed since: `86cc52d11` (a build-id restamp only, no content) and `5cecebb43` ("Ship the Stair Landing room deck: diagnosis layer, cards, page (B9 continued)"), a real, material, customer-facing new free page, the sixth room deck, not yet served to a visitor. **The gate itself had a real defect, now fixed:** the entry above dropped parentheses entirely around its own count, a third phrasing this file has drifted to; `gate_status_deploy_gap_count_current`'s regex still required a paren on one side or the other (fixed for exactly this recurring shape twice already, 2026-09-24 and 2026-09-26), so it matched nothing and stayed silent while the true figure kept climbing with no warning. Widened the regex in `ops/preflight.py`'s `deploy_gap_count_problem()` to a bare `<digits> commit(s)` match with no paren requirement, added two new cases to `ops/tests/test_gate_status_deploy_gap_count_current.py` proving fail-then-pass against this exact phrasing (11 checks, all passing), then confirmed live against this file: the fixed gate correctly flagged the stale citation above before this correction and clears now that this entry states the true count last. No P0 regression, no false claim newly live beyond the stale count itself, just the standing recurring gap, once more. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either. Real gap, restated once more so this entry's own last count is the current one: 7 commits.

**Widened 2026-09-29, scheduled operator cycle: the "7 commits" figure above had gone stale by one more.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 8 commits, not 7. The seven named above are unchanged and still undeployed. One more landed since: `40ec57eee` ("B9: build the Pantry room deck, the eighth room"), a real, material, customer-facing new free page, shipped by a concurrent session while this cycle was independently building the same room; converged onto their push rather than duplicate it. No P0 regression, no false claim newly live, just the standing recurring gap, once more. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either. Real gap, restated once more: 8 commits.

**Widened 2026-09-29, PM check-in: the "8 commits" figure above had gone stale by one more, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run rather than reconfirmed by citation.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 9 commits, not 8. The eight named above are unchanged and still undeployed. One more landed since: `a7693199c` ("B9: build the Hall Closet room deck, the ninth room"), a real, material, customer-facing new free page, shipped by a concurrent scheduled-operator cycle while this PM cycle triaged. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 9 commits, 7 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`; `4d7189c1d` and `86cc52d11` remain build-id restamps only).

**Widened 2026-09-29, PM check-in: the "9 commits" figure above had gone stale by one more, found while this cycle attached to a fresh fetch rather than assumed from the tree this cycle started with.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 10 commits, not 9. The nine named above are unchanged and still undeployed. One more landed since: `53af683fe` ("Add the Dining Room deck: tenth room, B9, all seventeen root causes"), a real, material, customer-facing new free page, shipped by the hourly operator, correctly continuing the exact room this cycle's own predecessor had handed off. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 10 commits, 8 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`; `4d7189c1d` and `86cc52d11` remain build-id restamps only).

**Widened 2026-09-29, PM check-in: the "10 commits" figure above had gone stale by two more.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 12 commits, not 10. The ten named above are unchanged and still undeployed. Two more landed since: `7859be181` ("Fix 7 real preflight failures the Dining Room deck exposed"), material and customer-facing (it changes two zones' rendered related-reading links so they stop duplicating each other's set, and corrects a missing-standard article's link count), and `11ca245dd` ("Regenerate build-id and sitemap lastmod hashes against final content"), a restamp only, no content of its own. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 12 commits, 9 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`, `7859be181`; `4d7189c1d`, `86cc52d11` and `11ca245dd` remain restamps only).

**Widened 2026-09-29, PM check-in: the "12 commits" figure above had gone stale by four more, caught live by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 16 commits, not 12. The nine named above are unchanged and still undeployed. Four more landed since, all from one concurrent session's own duplicate-work reconciliation (confirmed against `ops/NIGHTLY-LOG.md`'s own retrospective entry, not assumed): `f8145e2c` (an independent Hall Closet build, later superseded), `e6829190` (merge reconciling that Hall Closet collision onto the superset version), `0e629b24c` (merge picking up the Dining Room deck plus a second related-reading collision and a shared-article ceiling fix) and `9b1e06034` (merge picking up the Dining Room author's own follow-up fix for the same defect classes). Checked, not assumed: all four touch `site/` (zone and deck pages), so the gate correctly counts them material, but none adds content beyond what `a7693199c`/`53af683fe`/`7859be181` already represent; they are the mechanical trace of three sessions converging on the same two rooms, not four more of anything a visitor would see as new. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 16 commits, 13 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`, `7859be181`, `f8145e2c`, `e6829190`, `0e629b24c`, `9b1e06034`; `4d7189c1d`, `86cc52d11` and `11ca245dd` remain restamps only).

**Widened 2026-09-29, PM check-in: the "16 commits" figure above had gone stale by three more, found by re-deriving `deploy_gap_material_commits('7c6a83084')` fresh at the start of this cycle rather than trusting the prior citation.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly, not cited: real gap is now 19 commits, not 16. The thirteen material commits named above are unchanged and still undeployed. Three more landed since, all from the operator shipping Guest Bedroom (B9's eleventh room) while this cycle triaged: `e21413a38` ("Ship the Guest Bedroom room deck: diagnosis layer, cards, page"), a real, material, customer-facing new free page; `20c85444e`, a merge reconciling that push with a concurrent Hall Closet/nursery content edit, touching real card and zone content, not just build-id or sitemap; and `e6ee20807` ("Regenerate sitemap, dashboard and related-reading against the fully merged tip"), which shifted the related-reading links actually shown on 8 zone pages once the merge combined, a real visitor-visible change, not a restamp. Checked, not assumed: all three touch `site/`. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 19 commits, 16 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`, `7859be181`, `f8145e2c`, `e6829190`, `0e629b24c`, `9b1e06034`, `e21413a38`, `20c85444e`, `e6ee20807`; `4d7189c1d`, `86cc52d11` and `11ca245dd` remain restamps only).

**Widened 2026-09-29, PM check-in: the "19 commits" figure above had gone stale by one more within the same 30-minute slot, found by re-deriving `deploy_gap_material_commits('7c6a83084')` directly rather than trusting the prior PM cycle's own count, per `gate_status_deploy_gap_count_current`'s own live output (`problem: "cites 19 ... but a fresh count ... is 20"`).** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly, not cited: real gap is now 20 commits, not 19. The sixteen material commits named above are unchanged and still undeployed. One more landed since: `dc02ab1f7` ("Fix stale build-id and RISKS.md forms_dead citation after the merge"), checked directly with `git show --stat` rather than assumed: it touches `RISKS.md` and `site/build-id.txt` only, the latter a build-id restamp with no content of its own, so it joins `4d7189c1d`, `86cc52d11` and `11ca245dd` as the fourth restamp-only commit, not a seventeenth material one. No P0 regression, no false claim newly live, just the standing recurring gap, once more, and it will keep recurring at whatever size the next cycle finds it, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 20 commits, 16 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`, `7859be181`, `f8145e2c`, `e6829190`, `0e629b24c`, `9b1e06034`, `e21413a38`, `20c85444e`, `e6ee20807`; `4d7189c1d`, `86cc52d11`, `11ca245dd` and `dc02ab1f7` are restamps only).

**Widened 2026-09-29, scheduled operator: the gap grew by one after shipping Guest Bathroom (B9's twelfth room).** Same build_id/verdict (`159acc34b643d712`, `checked_at` `2026-09-27T22:45:39Z`), no new redeploy confirmation since. `deploy_gap_material_commits('7c6a83084')` now returns 21 commits, not 20: the sixteen already named plus `19f025bc9` (the Guest Bathroom deck, a real new free page; five zone pages rewired with a deck link and diagnosis-driven FAQ entries). No sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress to redeploy; the structural fix remains `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35), unchanged. Real gap, restated once more: 21 commits, 17 material (`a74dba749`, `80a111d1d`, `a221c7a9c`, `46ff9077f`, `5cecebb43`, `40ec57eee`, `a7693199c`, `53af683fe`, `7859be181`, `f8145e2c`, `e6829190`, `0e629b24c`, `9b1e06034`, `e21413a38`, `20c85444e`, `e6ee20807`, `19f025bc9`; `4d7189c1d`, `86cc52d11`, `11ca245dd` and `dc02ab1f7` are restamps only).

**Widened 2026-09-29, PM check-in (later slot): this section's own entry had gone stale by two more commits, and the fix a prior PM cycle this same slot made to the Public Website row (STATUS.md section 1) had not been carried here or to the Production Traceability row, leaving the file citing three different counts for the same gap at once.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z`. Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 22 commits, 17 material. Two more landed since the 20/16 count above: `19f025bc9` (the Guest Bathroom deck itself, B9's twelfth room, a real new free page, material) and `63c53cee3` ("Restamp build-id after merging the Guest Bathroom deck ship"), confirmed via `git show --stat` to touch only `site/build-id.txt`, a fifth restamp-only commit alongside `4d7189c1d`, `86cc52d11`, `11ca245dd` and `dc02ab1f7`. Verified directly against the gate's own logic: `deploy_gap_count_problem()` returns `''` against this entry's stated count. No P0 regression, no false claim newly live. Real gap, restated once more: 22 commits, 17 material (the sixteen named above plus `19f025bc9`; `4d7189c1d`, `86cc52d11`, `11ca245dd`, `dc02ab1f7` and `63c53cee3` are restamps only).

**Widened 2026-09-29, PM check-in: two more room decks shipped since the 22/17 entry above, found by re-deriving `deploy_gap_material_commits('7c6a83084')` fresh at the start of this cycle rather than trusting the prior citation.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly, not cited: real gap is now 26 commits, not 22. Five commits landed since the entry above, and one previously-counted commit dropped out: `63c53cee3` no longer appears in the function's own output at all, the same path-simplification disappearance this section already recorded once for `ac1af6e7` (2026-09-26): git's default path-history simplification drops a commit once its net effect on `site/`/`Dockerfile` folds into a later merge, not a miscount here or there. Of the five new arrivals, checked directly with `git show --stat` rather than assumed: `a722bd190` (the Family Room room deck, B9's thirteenth room, a real new free page) and `76b56e3d4` (the Living Room room deck, fourteenth room, a real new free page) are material; `58d5724ae` (regenerating zone pages after the Living Room merge) is material too, the same shape already established for `e6ee20807`, a related-reading redistribution visible on real zone pages, here across seventeen zones rather than eight; `bd99db870` (the merge commit reconciling both rooms) and `b1bf3389` (a build-id restamp) add nothing beyond what the direct commits above already carry. No P0 regression, no false claim newly live, just the standing recurring gap, once more, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy). Real gap, restated once more: 26 commits, 20 material (the seventeen named above plus `a722bd190`, `76b56e3d4`, `58d5724ae`; `4d7189c1d`, `86cc52d11`, `11ca245dd`, `dc02ab1f7`, `bd99db870` and `b1bf3389` are restamp/merge only, not material).

**Widened 2026-09-29, PM check-in: four more room decks shipped since the 26/20 entry above, Mudroom, Nursery, Kids Bedroom and Primary Bedroom, B9's fifteenth through eighteenth rooms, across a heavily concurrent stretch with several merge-based reconciliations.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 48 commits, not 26, verified by running the function in this session and counting its own returned list. Given the volume (22 new arrivals in one stretch, several of them merges reconciling concurrent room builds), this cycle did not re-derive a hand material versus restamp only split for all 22; that split is a narrative aid for a human reader and is not what the gate itself checks (`gate_status_deploy_gap_count_current` compares only the bare count in this function's raw output, not a hand-filtered subset), so publishing a guessed split here would be worse than leaving it honestly undone. Reporting unchecked as unchecked rather than writing a guess over it: the material/restamp breakdown above is now stale and is left unresolved this cycle for whichever session next has the time to redo it properly. No P0 regression, no false claim newly live, just the standing recurring gap, larger, until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy` closes it; no sandboxed session here holds either (confirmed again this cycle: no key at `~/.ssh`, network egress to the VPS denied by the agent proxy policy). Real gap, restated once more: 48 commits total, material breakdown not re-derived this cycle.

**Widened 2026-09-29, PM check-in (21:2x): caught live again by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`159acc34b643d712`), same resolved commit (`7c6a83084`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-27T22:45:39Z` (no new redeploy confirmation since). Re-derived directly with `deploy_gap_material_commits('7c6a83084')`, not cited: real gap is now 51 commits, up from 48. Three new arrivals: the Workshop room deck (B9's nineteenth room) and this check-in's own two commits (a stale `RISKS.md` `forms_dead` citation fix and this log entry), neither of the latter two customer-facing. No P0 regression. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either.

**NARROWED 2026-09-29, PM check-in (22:1x): Phil's own session redeployed and closed the entire 51-commit gap above, then B9's last two rooms plus one real content fix reopened a much smaller one.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `72f0b37c784c7b60`, `checked_at: 2026-09-29T20:29:14Z`; confirmed this is Phil's own commit, not this sandbox's: `git show --stat 09381b55f` shows only that file's `build_id`/`checked_at` fields changed, authored by Phil directly (`philklingmbb@gmail.com`), not a Claude co-author. Superseded build_id `159acc34b643d712`. Resolves via `resolve_verdict_commit('72f0b37c784c7b60')` to `295ad54f9`, not `7c6a83084`. Fresh `deploy_gap_material_commits('295ad54f9')` run this cycle, not cited: 15 commits, checked directly with `git show --stat` for each rather than assumed. Eleven material: `e75cac65c` (Workshop room deck, B9's nineteenth room, a real new free page), `c3b769165` (Patio or Deck room deck, B9's twentieth and final room, a real new free page), `c9b81024c`/`2019aeb18`/`e5103e542` (regenerating the Workshop zone pages so the diagnosis layer renders), `09381b55f` (Phil's own fix: a shared root-cause sentence wrongly told 100 pages, including every garage/pantry/workshop/kitchen page, to picture a surface "at bedtime"; rewritten zone-neutral), `1aa096102`/`a587bf36f`/`e273d0b7c` (regenerating the zone and Patio-or-Deck corpus after that fix merged), `c2ab3e996` (the related-reading load-balanced allocator fix), `37adba4d1` (regenerating the full zone corpus against it). Four restamp-only, no content of their own: `0a8930b7e`, `a51016e2b`, `7e0f6036d` (build-id.txt only), `63305c0fe` (build-id.txt plus sitemap lastmod). No P0 regression: the gap is two new free pages, one root-cause wording fix already live in the repository, and a related-reading rebalance, none of them broken, all of them simply not yet redeployed. Verified directly against the gate's own logic: `deploy_gap_count_problem()` returns `''` against this entry's stated count. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy), so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding the key, same as every prior entry; this narrowing came from exactly that, a session with real access, not from anything a sandbox can do on its own.

**NARROWED 2026-09-30T00:01:56Z, scheduled operator cycle: a session with real access redeployed and closed the entire 15-commit gap above; one commit has landed since.** Caught by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning: this section, the two rows in STATUS.md section 1 and the Production Knowledge paragraph all still cited the superseded build). `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `14089d51f264597d`, `checked_at: 2026-09-30T00:01:56Z`, superseding `72f0b37c784c7b60`. Resolves via `resolve_verdict_commit('14089d51f264597d')` to `0a8930b7e`, one of the prior entry's own "restamp only" commits, not `295ad54f9`. Fresh `deploy_gap_material_commits('0a8930b7e')` run this cycle, verified directly: 1 commit, 1 material: `9ddddd197` ("420 payment links were followable, so crawling this site opened checkouts", Phil's own commit, confirmed by `git show --stat` to touch only the `nofollow` attribute on 420 `buy.stripe.com` links across 171 pages plus the regenerated `site/build-id.txt`). `git log 9ddddd197..HEAD -- site/ Dockerfile` is empty: no further site- or Dockerfile-touching commit has landed since, so this is the whole gap, not a partial recount. No P0 regression: the gap is one already-correct trust fix, not a broken page. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress (confirmed again this cycle: no key at `~/.ssh`, `curl` to `6s-success.com` rejected by the agent proxy); `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) remains the only fix for the recurrence itself.

**CLOSED 2026-09-30T01:06:56Z, same scheduled operator cycle: Phil's own concurrent commit redeployed and closed the 1-commit gap the entry above had just finished documenting, before this cycle's own fix could even be pushed.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `1db1621639e93437`, `checked_at: 2026-09-30T01:06:56Z` (commit `8998cd048`, "Record the deploy verdict: production now carries the nofollow fix", authored by Phil directly, `philklingmbb@gmail.com`, not this sandbox). Resolves via `resolve_verdict_commit('1db1621639e93437')` to `9ddddd197` itself, the same commit the entry above named as the whole gap. `deploy_gap_material_commits('9ddddd197')` returns an empty list, verified directly. Production matches `HEAD` exactly: zero commits, zero gap. Merged rather than overwritten: this cycle's own STATUS.md edit had already gone stale by the time it was ready to push, and was corrected a second time in the same cycle rather than shipped stale. Same standing limit for the *next* gap that opens, whenever it does: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) remains the only fix for the recurrence itself.

**CLOSED 2026-09-30T16:49:06Z: the 15:36:31Z entry below went one confirmation stale within the hour, caught by `gate_status_deploy_verdict_current` rather than by reading.** `ops/deploy-verdict.json` records `verdict: "current"`, build `6f5176355eb29401`, `checked_at: 2026-09-30T16:49:06Z`, from the deploy that shipped `quest-offer-taken`. `deploy_freshness.py` reports CURRENT on all 10 assets and the content marker, and production was checked directly: `quest.html` serves `quest.js?v=6b3fb90cc8`, containing both new quest events. **A new shape of this blocker, worth naming here because the existing account does not cover it:** the image had to be dispatched by hand, because the push-triggered build failed on an unrelated fault in a concurrent session's commit and the fix for that touched no `site/**` path, so the workflow's filter correctly declined to rebuild and a shipped site change sat with no image at all. A failed build on a shared `main` therefore strands every site change made near it, silently, until something under `site/**` moves again. `ops/deploy.py` now asks GitHub which of building, ready, failed or none is true instead of always answering "the image is probably still publishing, run this again", which in that state would have looped forever (`ops/tests/test_deploy_publish_state.py`, 14 cases).

**CLOSED 2026-09-30T15:36:31Z, PM check-in 15:4x: the 07:42:00Z entry below went stale the same day and was carried unread by this file's own summary rows and by the dashboard, the exact recurring shape this section exists to name.** Commit `12e3402ca` (09:10:02-06:00, "quest-symptom-shown") touched `site/`, reopening a one-commit gap. Phil's own session redeployed and recorded the new verdict in `ac8e2c1fc` (09:36:54-06:00 = 15:36:54Z): `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `04167f5ad701b0e4`, `checked_at: 2026-09-30T15:36:31Z`, superseding `e70a81623df41ed5`. `git log 12e3402ca..HEAD -- site/ Dockerfile` returns zero commits: production matches `HEAD` exactly, zero gap, verified directly. `EXECUTIVE-DASHBOARD-LIVE.md` regenerated this cycle now reflects it. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**CLOSED 2026-09-30T07:42:00Z, PM check-in, independently confirmed by a concurrent scheduled operator cycle the same minute: caught live by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning: this section and Production Knowledge below both still cited the superseded `1db1621639e93437` build).** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `e70a81623df41ed5`, `checked_at: 2026-09-30T07:42:00Z` (commit `3f5f8ae46`, "Record the deploy verdict: production is current again", authored by Phil directly, `philklingmbb@gmail.com`, not this sandbox). `resolve_verdict_commit()` cannot surface it because `git blame site/build-id.txt` shows the line came in on a merge commit, `02274cc669` ("Merge origin/main: re-derive the dashboard"), and the pickaxe walk that function does skips merge diffs by default; confirmed directly with `git blame` instead of trusting the helper's `None`. The concurrent cycle's own fix reached the same conclusion by a simpler route: `3f5f8ae46` (the commit that wrote this verdict) is `HEAD` itself, so the gap is zero by construction. `git log 02274cc669..HEAD -- site/ Dockerfile` also returns zero commits: production matches `HEAD` exactly, zero gap, verified directly rather than assumed from the helper. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**CLOSED 2026-09-30T20:59:33-06:00 (= 2026-10-01T02:59:05Z), scheduled operator, caught live by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning: this section, Production Knowledge and Immediate Focus below all still cited the superseded `6f5176355eb29401` build).** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `8fbc6b7d3d2599ae`, `checked_at: 2026-10-01T02:59:05Z` (commit `b57ba4f58`, "Record the deploy verdict: the honest room panels are live", authored by Phil directly, `philklingmbb@gmail.com`, not this sandbox; verified against production, not the repository, that garage, workshop and nursery serve the correct accessible name with no stale "what done looks like" claim). `resolve_verdict_commit('8fbc6b7d3d2599ae')` resolves it to `b57ba4f58` itself. `git log b57ba4f58..HEAD -- site/ Dockerfile` returns zero commits, re-derived directly this cycle: production matches `HEAD` exactly, zero gap. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**REOPENED 2026-10-01T11:2x, PM check-in: the gap closed above has reopened, and this time the undeployed content is itself a trust fix, not a cosmetic one.** `ops/deploy-verdict.json` is unchanged since the entry above (`checked_at` still `2026-10-01T02:59:05Z`, build `8fbc6b7d3d2599ae`); re-derived the real gap directly with `deploy_gap_material_commits('b57ba4f58')` rather than trusting the still-"current" verdict (STATUS.md's own stale-verdict gate only fires inside a full `preflight.py` run, and this cycle's full run was still in progress at the time of this check, so nothing else had caught it yet). Real gap: 5 commits, 160 files, `git diff --shortstat b57ba4f58 HEAD -- site/ Dockerfile`. Two are material: `f8d7b5aaa` (Workshop/Patio or Deck each omitting the other from shared root-cause copy) and, more significantly, `f20f541a4`, the scheduled operator cycle's own fix for the sitewide false "zones in working order" claim across 20 rooms, 114 zone pages and 20 decks (see `ops/NIGHTLY-LOG.md`, 2026-10-01). **That means the false claim this fix corrects is still being served to live visitors right now**, since production has not redeployed past `b57ba4f58`, the commit before the fix landed. The other three commits (`08285fc29`, `085572035`, `a194251dd`) are cardtext/build-id/dashboard regens carrying no independent content. No new P0 regression beyond the one already fixed in the repository; the live exposure window is the same one this file's own "Last Updated" summary already described as corrected, just not yet confirmed closed in production. Same standing limit as every entry above: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**WIDENED 2026-10-01, scheduled operator cycle: the gap above has grown by two more commits, one of them a second structured-data-vs-visible-content trust fix.** `ops/deploy-verdict.json` is still unchanged (`checked_at` still `2026-10-01T02:59:05Z`, build `8fbc6b7d3d2599ae`); re-derived directly with `deploy_gap_material_commits('b57ba4f58')` rather than citing the entry above, since a full `python ops/preflight.py` run this cycle flagged this section as stale (`status-deploy-gap-count-current`) before this correction. Real gap now **6 commits**: the 5 named above, plus `52dfa04f1` (this cycle's own fix: all 20 room pages' FAQPage JSON-LD disagreed with their own visible "Added together..." paragraph on the closing clause, see `ops/NIGHTLY-LOG.md` 2026-10-01). The merge commit reconciling a concurrent PM check-in (`28b878de5`) carries no independent `site/`/`Dockerfile` content of its own. **That means two separate structured-data-vs-visible-content defects, both now fixed in the repository, are still being served live.** No new P0 regression beyond what is already fixed; same standing limit as every entry above: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**WIDENED 2026-10-01T13:2x, PM check-in: the entry above had already gone stale by one commit, caught by this cycle's own `preflight.py` run (`status-deploy-gap-count-current` warning, cited 6 against a fresh count of 7).** Same build_id (`8fbc6b7d3d2599ae`), same `checked_at` (`2026-10-01T02:59:05Z`); `resolve_verdict_commit()` resolves it to `1b3bc9a9` (the commit that actually set `site/build-id.txt` to this value), a few minutes earlier than `b57ba4f58` cited above but with no `site/`/`Dockerfile` difference between the two (`git log 1b3bc9a9..b57ba4f58 -- site/ Dockerfile` is empty, so both name the same deploy state). Re-derived directly with `deploy_gap_material_commits()`: real gap now **7 commits**, the 6 named above plus `b697f0b89` ("Regenerate build-id.txt after the FAQPage fix, correct the stale deploy-gap count", ironically the commit that made this count stale by one). `b697f0b89` carries no independent `site/`/`Dockerfile` content beyond what `52dfa04f1` already shipped, so the material count is unchanged: still 3 (`f8d7b5aaa`, `f20f541a4`, `52dfa04f1`), the same two structured-data-vs-visible-content fixes and the Workshop/Patio or Deck shared-copy fix named above, still being served live in production. No new P0 regression. Same standing limit as every entry above: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**WIDENED 2026-10-02T05:2x, PM check-in: caught live by this cycle's own `preflight.py` run (`status-deploy-gap-count-current` warning, cited 7 against a fresh count of 24).** Same build_id (`8fbc6b7d3d2599ae`), same `checked_at` (`2026-10-01T02:59:05Z`); `resolve_verdict_commit('8fbc6b7d3d2599ae')` still resolves to `1b3bc9a9` (same commit cited above, confirmed by direct re-run). Re-derived directly with `deploy_gap_material_commits()`, not cited: real gap is now **24 commits**, verified by running the function in this session and counting its own returned list (`ops/deploy-verdict.json` itself unchanged, so this is growth since the last confirmation, not a different baseline). Given the volume, a full hand material-versus-restamp split was not re-derived this cycle, the same honest-unknown choice this section took once before at a comparably large count: guessing the split would be worse than leaving it undone. Named directly rather than guessed: the complaint-cluster article (`why-is-my-house-always-messy.html`), its CTA-band and breadcrumb-JSON-LD fixes, the Kids Bedroom and Nursery room/zone/deck pages, and the room-time/FAQPage fixes already covered above are all in this gap, all real, none broken. No new P0 regression. Same standing limit as every entry above: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

Impact:

Autonomous agents cannot safely assume production architecture, health, release identity, backup state, or rollback capability.

Owners:

- `vps-docker-manager`
- `devops-sre`
- `github-manager`

Resolution:

Read-only discovery is done wherever it is reachable without a credential.
The remaining gap is Phil's own Redeploy click or a session holding the
deploy key; see `OWNER-ACTIONS.md` item 1b.

---

## BLOCKER-002: Live Business Data Established, Not Yet a Live Feed

**Status: PARTIALLY RESOLVED.** Real business data exists and is current:
`GOALS.md` and section 9 above carry a measured revenue, session and
organic-search baseline (last direct database pull 2026-09-17). What
remains missing is a wired, credential-free live feed: no Stripe, Umami
API, or Search Console credential exists in any operator sandbox, so every
number here is a manual pull re-run periodically, not a continuously
refreshing one.

Impact:

Claude cannot responsibly optimize toward revenue/customer metrics without trusted measurement.

Owners:

- `analytics-intelligence`
- `commerce-manager`
- `seo-aeo`

Resolution:

Metric definitions (`METRICS.md`) and the data-source map (`DATA-SOURCES.md`)
are both written. Connecting authoritative live sources needs a credential
only Phil holds (Umami share URL or API key, `OWNER-ACTIONS.md` item 1.2;
Search Console token, item 2).

---

## BLOCKER-003: Executive Dashboard Established

**Status: RESOLVED.** `DASHBOARD.md`, `METRICS.md` and `DATA-SOURCES.md`
all exist; `ops/dashboard.py` regenerates `EXECUTIVE-DASHBOARD-LIVE.md`
from measured state on every cycle (confirmed regenerated this cycle,
2026-09-20 11:48). This blocker was flagged as contradicted by a same-day
PM check-in (2026-09-20 10:40) but never itself corrected until now.

Impact (historical):

Owner lacked one trusted near-real-time view of business, product, growth, and production.

Owners:

- `analytics-intelligence`
- `6s-ceo`

Resolution: done.

---

# 18. Known Risks

## RISK-001: Autonomous Action Without Verified State

**Severity:** HIGH  
**Status:** OPEN

Risk:

Agents may modify systems based on assumptions.

Control:

Read current state and inspect actual systems before meaningful production action.

---

## RISK-002: Production / GitHub Drift

**Severity:** HIGH UNTIL VERIFIED  
**Status:** OPEN

Risk:

Production may not match repository configuration.

Control:

Map deployed commit/image/configuration to GitHub.

---

## RISK-003: Unknown Backup / Restore Readiness

**Severity:** HIGH UNTIL VERIFIED  
**Status:** OPEN

Risk:

Production data may not be recoverable.

Control:

Inventory persistent data, backup mechanism, off-host copy, and restore procedure.

---

## RISK-004: Optimization Without Trusted Metrics

**Severity:** MEDIUM-HIGH  
**Status:** PARTIALLY CONTROLLED, corrected 2026-09-20

Risk:

Autonomous agents may optimize vanity or incorrectly calculated metrics.

Control:

`METRICS.md` and `DATA-SOURCES.md` are both written and in use (this file's
own section 9 and `GOALS.md` cite them). The residual risk is narrower than
originally stated: it is that a metric's authoritative source goes stale
between the manual pulls a missing live credential still forces, not that
no definition or source map exists. `GOALS.md`'s own opening line already
names this as the standard to hold every baseline to.

---

# 19. Pending RED Decisions

None currently recorded.

If a RED action requires owner approval, record it here:

## RED-XXX

**Requested Action:**  
**Reason:**  
**Evidence:**  
**Risk:**  
**Recovery:**  
**Alternatives:**  
**Approval Status:** PENDING

Do not clutter this section with routine YELLOW coordination.

---

# 20. Recently Completed Meaningful Work

## Autonomous Governance Foundation

Completed:

- master `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`

## Agent Architecture

Completed or updated:

- `github-manager`
- `vps-docker-manager`
- `devops-sre`

Additional specialist agents may already exist in the repository and should be inventoried rather than assumed.

---

# 21. Highest-Priority Next Actions

All required operating documents in `CLAUDE.md` section 56 now exist on disk;
the P1 through P6 "create the missing document" actions this section used to
list are done and have been removed. **Corrected 2026-09-08:** the
authoritative queue is now `BACKLOG-2026-09-07.md`, Phil's own reprioritisation
toward micro zones, decks and image/video work, which explicitly supersedes
the ordering (not the process rules) in `BACKLOG-2026-H2.md`. The P1 through P6
Phil-gated items below, carried from the 2026-09-02 review, were individually
re-checked against the 9 open GitHub issues this cycle and are still open and
still accurate; they are not the whole queue any more. Unblocked
operator-actionable work now lives in `BACKLOG-2026-09-07.md` sections 2
through 4 (app, decks, images/video), not in this list. `OWNER-ACTIONS.md`
remains the standing consolidated list of everything genuinely gated on Phil.
The consolidated list of Phil-gated items:

## P1: Umami read access (backlog 1.1) -- corrected 2026-09-02

Not fully blocked any more. Phil read the analytics database directly on
2026-09-02 (the API token is expired) and got a real one-time baseline, now
recorded in `GOALS.md` and above in section 9. What is still open is items
1.2 through 1.4: wiring a share URL or API key into `ops/dashboard.py` so a
credential-less operator session can pull fresh numbers itself, instead of
depending on Phil re-reading the database by hand each time the baseline
goes stale.

Owner: **Phil** for the credential/share-URL; **operator** for the wiring
once it exists.

---

## P2: Decide the Listmonk sending identity (issue #15, P0)

Separate Listmonk instance for 6S Success, or change the shared instance's
global from-address and accept the cost to the other brand it currently
serves (Compassion Benchmark). Blocks email capture entirely; six prospects
already lost with no way to reach them.

Owner: **Phil decides, operator builds**

---

## P3: Publish the ten LinkedIn posts and generate the six tier-0 images (backlog 3.1, 3.3)

Both already drafted/prompted and waiting in Phil's queue. The only traffic
lever available that does not require search compounding time.

Owner: **Phil**

---

## P4: Resolve the routine self-update gap (issue #17), CLOSED 2026-08-25

Phil's own session rewrote the trigger's stored prompt to read
`BACKLOG-2026-H2.md` and the other operating documents directly each cycle,
rather than embedding a status snapshot that only the trigger's creator could
refresh. The self-update limitation still exists as a platform fact, but the
prompt no longer depends on being edited to stay current, so the practical
defect is resolved.

Owner: closed, no further action

---

## P5: Approve a capped local demand test for the service SKUs (backlog 3B.1)

A financial commitment, correctly RED per `CLAUDE.md`. This is the only tested
route to $20,000 that does not require a quarter-million monthly visitors; the
recommendation on file is a few hundred dollars and a hard 90-day stop.

Owner: **Phil**

---

## P6a: Sync the 155-SKU product spine to Stripe (backlog 5.7), CLOSED 2026-08-27

Phil did both halves himself: commit `b10a278` extended `SELLABLE`, ran the
live Stripe sync, and wired the resulting payment links into
`window.CATALOG`. 158 of 159 catalog items are now buyable (only Corporate
Lean 6S is not). A same-day follow-up commit `3e5248c` also fixed
`ops/build_epub.py` reading a hardcoded author placeholder, which had
blocked Amazon KDP submission. `ops/audit_catalog.py` re-verified clean
this cycle against the live 159-SKU set.

Owner: closed, no further action

---

## P6: Stripe business website field still reads Ledgerium (backlog 2.8, issue #21)

Everything else on the account's public identity is already fixed per account
(name, statement descriptor, support email/URL, legal pages, checkout
branding). Only the business website field remains, and Stripe's own safety
check blocked the operator from changing it because it can silently change
the shared legal entity's other account (Ledgerium) too. This has been open
since 2026-08-21 and was on the auto-generated dashboard but missing from
this file and from `BACKLOG-2026-H2.md` until this cycle added it.

Owner: **Phil**

---

# 22. Agent Startup Checklist

Before significant autonomous work:

- [ ] Read `CLAUDE.md`
- [ ] Read `AUTONOMY.md`
- [ ] Read `STATUS.md`
- [ ] Identify owning agent
- [ ] Check active workstreams
- [ ] Check blockers
- [ ] Check risks
- [ ] Inspect real system state when relevant
- [ ] Classify action GREEN / YELLOW / RED
- [ ] Avoid duplicating active work

---

# 23. Status Update Rules

Update this file when any of the following materially changes:

- production health
- deployed release
- active major workstream
- incident state
- major blocker
- material risk
- executive priority
- live data confidence
- GitHub control-plane health
- VPS/Docker health
- backup/restore confidence
- major product launch state

Do not update it for every commit.

---

# 24. How to Update Status

For each changed section:

1. obtain evidence
2. change status
3. add concise evidence/notes
4. update timestamp
5. identify owner if action remains
6. move historical detail to the appropriate long-term file

Do not allow this document to become an archive.

---

# 25. Freshness

Operational status decays quickly.

Agents should treat old status as a hypothesis when the underlying system can be inspected.

For highly dynamic information such as:

- production health
- container health
- current release
- incidents
- active PRs
- traffic
- revenue

prefer live sources over stale Markdown.

Update this summary afterward.

---

# 26. Truth Hierarchy

When this file conflicts with verified live state:

**Verified live state wins.**

Then update this file.

When two live sources conflict:

1. identify authoritative source from `DATA-SOURCES.md`
2. investigate discrepancy
3. report confidence
4. do not fabricate reconciliation

---

# 27. Status Ownership

Each specialist maintains its domain truth.

`github-manager`
→ GitHub/release status

`vps-docker-manager`
→ Hostinger/Docker runtime status

`devops-sre`
→ reliability/incident status

`analytics-intelligence`
→ business/product measurement confidence

`seo-aeo`
→ organic discovery status

`commerce-manager`
→ commerce status

`product-manager`
→ customer/product journey status

`6s-ceo`
→ strategic priority and executive synthesis

---

# 28. Executive Escalation

Surface to the owner when:

- production is RED
- significant customer data is at risk
- payment integrity is at risk
- a RED authorization is required
- recovery capability is materially compromised
- a major strategic decision is blocked
- a material financial/legal commitment is required

Do not escalate routine GREEN work.

---

# 29. Desired Future State

This file should eventually be generated largely from trusted system state.

Target pattern:

**GitHub + VPS + Analytics + Commerce + Search + Product Events**
→ **Metrics / Status Collection**
→ **STATUS.md summary**
→ **Executive Dashboard**
→ **6s-ceo prioritization**
→ **BACKLOG.md**
→ **Autonomous execution**

Human edits should not be required for routine status maintenance.

---

# 30. Current Overall Assessment

**Operating System:** OPERATING, governance and required documents in place

**Governance:** STRONG FOUNDATION

**Autonomous Execution Readiness:** FULL FOR GREEN-BAND WORK. AS OF 2026-09-15, THE AUTHORITATIVE QUEUE IS `BACKLOG-2026-09-07.md`, NOT `BACKLOG-2026-H2.md` (SUPERSEDED ON ORDERING, SECTION 21 ABOVE). SECTIONS 2 THROUGH 6 OF THAT FILE ARE, AS OF THIS DATE, ALL EITHER DONE OR EXPLICITLY GATED ON PHIL (ALL 8 OPEN GITHUB ISSUES CARRY A `P0`, `decision` OR `blocked-on-art` LABEL AS OF 2026-09-18, UP FROM 7 AFTER `#32` AND `#33` WERE OPENED SINCE 2026-09-15). WHEN THAT IS TRUE, THE ESTABLISHED FALLBACK IS A COLD READ OF A LOW-MENTION `ops/*.py` FILE OR HAND-MAINTAINED DOCUMENT, VERIFIED AGAINST THE LIVE OR GENERATED ARTIFACT RATHER THAN TRUSTED ON SIGHT; MOST REAL DEFECTS FOUND THIS MONTH CAME FROM THAT PRACTICE, NOT FROM THE BACKLOG.

**Production Knowledge, CLOSED 2026-10-01T02:59:05Z, scheduled operator: the 16:49:06Z entry below went one confirmation stale overnight, caught by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning naming this paragraph, BLOCKER-001 and Immediate Focus all three).** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `8fbc6b7d3d2599ae`, `checked_at: 2026-10-01T02:59:05Z` (commit `b57ba4f58`, "Record the deploy verdict: the honest room panels are live", authored by Phil directly, verified against production that garage, workshop and nursery serve the correct accessible name with no stale "what done looks like" claim). `resolve_verdict_commit('8fbc6b7d3d2599ae')` resolves to `b57ba4f58` itself; `git log b57ba4f58..HEAD -- site/ Dockerfile` returns zero commits, re-derived directly: production matches `HEAD` exactly, zero gap. No P0 regression. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**REOPENED 2026-10-01T11:2x, PM check-in: the gap closed above has reopened.** `ops/deploy-verdict.json` unchanged (`checked_at` still `2026-10-01T02:59:05Z`, build `8fbc6b7d3d2599ae`); re-derived directly with `deploy_gap_material_commits('b57ba4f58')`: 5 commits, 2 material (`f8d7b5aaa`, the Workshop/Patio or Deck shared-copy fix, and `f20f541a4`, the sitewide false "zones in working order" claim fix across 20 rooms/114 zones/20 decks). Full detail in `BLOCKER-001` above; not repeated here. The practical effect: **production is currently still serving the false zone-order claim the repository already fixed**, since the fix landed after the last confirmed redeploy. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. **Widened 2026-10-01T13:2x, PM check-in: this citation is now 2 commits stale; see `BLOCKER-001` above for the current count (7 commits, 3 material, `52dfa04f1`'s own FAQPage-vs-visible-copy fix added to the two named here) and the full account. Not repeated a third time; this paragraph's own practical conclusion (production still serves the false zone-order claim) is unchanged.** **Widened 2026-10-02T05:2x, PM check-in: that count is itself now stale; see `BLOCKER-001` above for the current figure (24 commits, hand material split not re-derived given the volume) and the full account. Not repeated again here; the practical conclusion (production is behind HEAD by real, unbroken customer-facing fixes) is unchanged.**

**Production Knowledge, CLOSED 2026-09-30T16:49:06Z: the 15:36:31Z entry below went one confirmation stale within the hour, caught by this cycle's own `gate_status_deploy_verdict_current` rather than by reading.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `6f5176355eb29401`, `checked_at: 2026-09-30T16:49:06Z`, from the deploy that shipped `quest-offer-taken` (the free half of the quest's offer had been firing nothing at all). `deploy_freshness.py` reports CURRENT on all 10 assets and the content marker, and production was verified directly rather than inferred: `quest.html` serves `quest.js?v=6b3fb90cc8` and that file contains both `quest-offer-taken` and `quest-symptom-shown`. **Worth recording because it is a new shape of the same recurrence:** that image had to be dispatched by hand. Its push-triggered build failed on a misordered `NIGHTLY-LOG.md` entry in a concurrent session's commit, and the upstream fix for that touched no `site/**` path, so `publish-image.yml`'s filter correctly declined to rebuild and a shipped site change sat with no image at all. `ops/deploy.py` used to answer that state with "usually the image has not finished publishing, run this again", which would have looped forever; it now asks GitHub which of building, ready, failed or none is true and says so. No P0 regression. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, CLOSED 2026-09-30T15:36:31Z, PM check-in 15:4x: the 07:42:00Z entry below went stale the same day, reopened by a site-touching commit, and was carried unread here and in the dashboard until this cycle.** Commit `12e3402ca` (09:10:02-06:00, "quest-symptom-shown") touched `site/`, reopening a one-commit gap the 07:42:00Z entry below predates. Phil's own session redeployed and recorded the new verdict in `ac8e2c1fc` (09:36:54-06:00 = 15:36:54Z): `ops/deploy-verdict.json` now records `verdict: "current"`, build `04167f5ad701b0e4`, `checked_at: 2026-09-30T15:36:31Z`. `git log 12e3402ca..HEAD -- site/ Dockerfile` returns zero commits: production matches `HEAD` exactly, zero gap, verified directly. `EXECUTIVE-DASHBOARD-LIVE.md` regenerated this cycle now reflects it: its "one constraint" line no longer names a stale build; the live constraint reads as discovery/traffic, not deploy lag. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, CLOSED 2026-09-30T07:42:00Z, PM check-in, independently confirmed by a concurrent scheduled operator cycle the same minute: caught live by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning: this paragraph and BLOCKER-001 both still cited the superseded `1db1621639e93437` build).** `ops/deploy-verdict.json` records build `e70a81623df41ed5`, `checked_at: 2026-09-30T07:42:00Z` (commit `3f5f8ae46`, "Record the deploy verdict: production is current again", authored `philklingmbb@gmail.com`, not this sandbox), a later confirmation than `1db1621639e93437`/01:06:56Z below. `resolve_verdict_commit()` returns `None` because the line landed via a merge commit, `02274cc669` ("Merge origin/main: re-derive the dashboard"), which the pickaxe walk skips by default; confirmed directly with `git blame site/build-id.txt` instead. The concurrent cycle's own fix reached the same conclusion the simpler way: `3f5f8ae46` (the commit that wrote this verdict) is `HEAD` itself, so the gap is zero by construction. `git log 02274cc669..HEAD -- site/ Dockerfile` also returns zero commits: production matches `HEAD` exactly. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, CLOSED 2026-09-30T01:06:56Z, same scheduled operator cycle: a sixth redeploy landed minutes after the one below, from Phil directly, closing the last commit and leaving zero gap.** `ops/deploy-verdict.json` records build `1db1621639e93437`, `checked_at: 2026-09-30T01:06:56Z` (commit `8998cd048`, authored `philklingmbb@gmail.com`, not this sandbox), a later confirmation than `14089d51f264597d`/00:01:56Z below. `resolve_verdict_commit()` resolves it to `9ddddd197` itself, the same commit the paragraph below named as the whole gap. `deploy_gap_material_commits('9ddddd197')` returns an empty list, verified directly: production matches `HEAD` exactly. No P0 regression. Same standing limit for whenever the next gap opens: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, NARROWED 2026-09-30T00:01:56Z, scheduled operator cycle: a fifth redeploy landed after the 22:1x one below, from a session with real production access, closing that gap and leaving only one commit undeployed.** `ops/deploy-verdict.json` records build `14089d51f264597d`, `checked_at: 2026-09-30T00:01:56Z`, a later confirmation than `72f0b37c784c7b60`/20:29:14Z below; caught live by this cycle's own `preflight.py` run (`status-deploy-verdict-current` warning: this section still cited the superseded build). `resolve_verdict_commit()` resolves it to `0a8930b7e`, not `295ad54f9`, so everything the 22:1x paragraph below named as undeployed (B9's last two room decks, the "at bedtime" wording fix, the related-reading allocator fix) is now live. Fresh gap since that redeploy: 1 commit, 1 material (`deploy_gap_material_commits('0a8930b7e')`, verified directly): `9ddddd197`, Phil's own fix adding `nofollow` to all 420 `buy.stripe.com` links sitewide so a crawler fetch can no longer open a Stripe Checkout Session (the likely explanation for the 12 checkout sessions created 2026-09-15 with zero matching buy-clicks, `GOALS.md` section 2). `site/build-id.txt` at HEAD (`1db1621639e93437`) is that commit's own regeneration, not yet redeployed. No P0 regression: the gap is one already-correct trust fix, not a broken page. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, NARROWED 2026-09-29 22:1x UTC, PM check-in: a fourth redeploy landed after the 22:4x one below, from a session with real production access, closing that gap and opening a much smaller one.** `ops/deploy-verdict.json` records build `72f0b37c784c7b60`, `checked_at: 2026-09-29T20:29:14Z`, a later confirmation than `159acc34b643d712`/22:45:39Z below; confirmed as Phil's own action, not this sandbox's, by reading the commit that changed the file (`09381b55f`, authored `philklingmbb@gmail.com`, no Claude co-author). `resolve_verdict_commit()` resolves it to `295ad54f9`, not `7c6a83084`, so everything the 22:4x paragraph below could have named as undeployed at that time is now live. Fresh gap since that redeploy: 15 commits, 11 material, full breakdown in `BLOCKER-001` above and the Public website / Production traceability rows above; in short, B9's last two room decks (Workshop, Patio or Deck, closing B9 at 20/20) and a real root-cause wording fix across 100 pages, still undeployed. No P0 regression. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, RESOLVED 2026-09-27 22:4x UTC, a session with real production access: a third redeploy landed after the 22:21 one below, closing that gap in full.** `ops/deploy-verdict.json` records build `159acc34b643d712`, `checked_at: 2026-09-27T22:45:39Z`, a later confirmation than the `a6c5f96b77c7cff2`/22:21:27Z one below; this is the same check Phil's own `9b0de5cd4` ("LRN-0020: when a gate has no available action, change the format, not the blocker") records in its own commit message. `resolve_verdict_commit()` resolves it to `7c6a83084` ("Finish it: no page on this site ships with no image, room pages included"), so everything the 22:21 paragraph named as still-undeployed (the Kitchen zone content-typo fix, the room-time rounding fix, the Kitchen deck's false "shortest zone" claim, the affiliate-disclosure fix) is now live. `git log 7c6a83084..HEAD -- site/ Dockerfile` is empty: no further site- or Dockerfile-touching commit has landed since, so production matches HEAD exactly right now, not just at the moment of that redeploy. Full account in `BLOCKER-001` above. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Prior, Production Knowledge, RESOLVED 2026-09-25 22:21 UTC, a session with real production access: a second redeploy landed after the 14:15 one below, closing that gap and opening a new one.** *(Superseded by the 2026-09-27 22:4x entry above, a later live-verified redeploy that closed the gap this paragraph opened.)* `ops/deploy-verdict.json` records build `a6c5f96b77c7cff2`, `checked_at: 2026-09-25T22:21:27Z`, a later confirmation than the 14:15:05Z one the paragraph below cites; found by this PM check-in via `gate_status_deploy_verdict_current` on the very next `preflight.py` run after the 14:15 paragraph was written. `resolve_verdict_commit()` resolves it to `223f5111`, so everything the 14:15 paragraph named as still-undeployed (the false room-page disclosure fix, the dead deck anchors) is now live. New gap since: 8 commits (`0ce148e7`, `fbeba2f7`, `441a8208`, `dec5660a`, `dd9c0a01`, `0f1641cb`, `89a030a5`, `ba73ec3c`), 4 material: `fbeba2f7` (a real content-typo fix reaching 21 downstream artifacts, corrected at the Kitchen zone's `purpose` source), `dec5660a` (room_time() rounding understated 9 of 20 rooms by half an hour), `dd9c0a01` (Kitchen deck's false "shortest zone" claim), `ba73ec3c` (a second false no-affiliate-link disclosure fix, landed again after the first redeploy). Full account in `BLOCKER-001` above. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Production Knowledge, RESOLVED 2026-09-25 14:15 UTC, this session: the gap closed again, and this time it was customer-visible.** *(Superseded by the 22:21 entry above, a later live-verified redeploy. Kept for its own history: it was itself kept above the 14:2x entry below it, which carried a later clock time but only re-read a stale committed file rather than verifying the live VPS.)* `ops/deploy.py` confirms production serves build `d40585d97500a3ca` (commit `5ff17fcb`), matching the repository, verified `2026-09-25T14:15:05Z` in `ops/deploy-verdict.json`. What had been behind was four room decks: Primary Bathroom, Laundry Room, Home Office and Garage all returned 404 live while the repository believed they shipped. After the deploy, all six deck pages return 200 and all six are linked from the live `deck.html` hub. Same standing limit as every prior entry: no operator sandbox holds the deploy key, so this closes again the moment the next `site/**` commit lands with no session to follow it; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Superseded: the 05:4x entry citing build `aa7c7e7e578e9a18`.

**Prior, REOPENED THEN NARROWED 2026-09-25 14:2x, PM check-in: RESOLVED 05:4x below went stale, caught by `gate_status_deploy_verdict_current` this cycle, and by the time this was checked a later redeploy had already partly closed the gap it should have named.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, resolving to commit `c6cc1a6a` (B9's Laundry Room deck), a full confirmation cycle later than the `aa7c7e7e578e9a18`/`890c43a3` pair the 05:4x note below cited. Full detail and the current 5-commit gap (three undeployed room decks, the Kitchen-photo og:image fix, one build-id restamp) are in `BLOCKER-001` below; not repeated here to avoid two sentences drifting apart again. Same standing limit as every prior entry: no operator sandbox holds the deploy key, so this closes again the moment the next `site/**` commit lands with no session to follow it; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Prior, RESOLVED 2026-09-25 05:4x, PM check-in: the gap named below closed again.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`, resolving to commit `890c43a3`. `git log 890c43a3..HEAD -- site/ Dockerfile` is empty: production matches HEAD exactly right now, including the footer restoration `BLOCKER-001` names. Superseded above once the next redeploy landed and the gap reopened.

**Prior (2026-09-25 00:1x, PM check-in): a newer redeploy confirmation than the one below was already sitting unread in `ops/deploy-verdict.json`, then went stale again within the same cycle, same recurring shape `BLOCKER-001` now names by pattern rather than by one date.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `6a10df205a3d058c`, `checked_at: 2026-09-24T23:35:51Z`, resolving via `git log -S` to commit `b8eca135` ("Micro zones: Laundry Room personalised"), a full confirmation cycle later than the `28ed2709194afab5`/`d5b0d5c8` pair this paragraph previously cited. One further site-affecting commit, `ca49aa25` (Phil's own "Micro zones: Garage personalised"), landed after that confirmation and moved `site/build-id.txt` again at HEAD; `git diff --quiet b8eca135 HEAD -- site/ Dockerfile` is dirty again (1 commit, 44 files). Production is therefore confirmed stale by exactly one commit again, not the four a recount against the older, superseded build would have shown. NO OPERATOR SANDBOX HOLDS THE DEPLOY KEY'S PRIVATE HALF OR EGRESS TO THE VPS (CONFIRMED AGAIN THIS CYCLE), SO THIS IS READ FROM THE COMMITTED VERDICT, NOT RE-CHECKED LIVE; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` ITEM 0, ISSUE #35) IS WHAT WOULD STOP THIS FROM BEING REDISCOVERED EVERY CYCLE.

**Prior (2026-09-24 21:2x, scheduled operator cycle): a newer redeploy confirmation superseded the 18:47:16Z one below, then went stale again within the same cycle.** `ops/deploy-verdict.json` then recorded `verdict: "current"`, build `28ed2709194afab5`, `checked_at: 2026-09-24T21:10:12Z`, matching commit `d5b0d5c8`. Superseded once a later redeploy confirmation (build `6a10df205a3d058c`) and a following site commit were found in the paragraph above.

**Prior (2026-09-24 19:2x, PM check-in): production redeployed and was confirmed current at that time.** `ops/deploy-verdict.json` then recorded build `4ec571da81db3b34`, `checked_at: 2026-09-24T18:47:16Z`, committed in `44ef380a` by a local session holding `~/.ssh/6s_deploy` (the same pattern this file has recorded on every prior redeploy; Phil did not click anything himself, see `OWNER-ACTIONS.md`'s own correction on this point). Superseded by the paragraph above once a later `site/**` commit landed and a later redeploy confirmed a newer build.

**Superseded entry, 2026-09-24, PM check-in: the 95-commit figure and the 914c2881 build citation below were both stale, and a newer, better confirmation than either already existed on GitHub unread.** LAST CONFIRMED CURRENT 2026-09-23T19:00:39Z (build `5eba61fde231c1a7`, per `ops/deploy-verdict.json`, a session with real production access that finished the Stripe SKU retirement and redeployed). `site/build-id.txt` at HEAD then read `4ec571da81db3b34`: 127 commits had landed since that confirmation (`git log 8e4c8e33..HEAD`), but the build side of that gap was closed, not open: `publish-image.yml` run 398 (`workflow_dispatch`-free, a plain push build, `https://github.com/Klingdom/6s-success/actions/runs/36032909521`) completed `success` at 2026-09-24T17:35:17Z against commit `accc9fff`, and `git diff --quiet accc9fff HEAD -- site/ Dockerfile` was clean, so the GHCR image already carried every fix named in BLOCKER-001, HEAD included. Only Phil's Hostinger Redeploy click (or a session holding the VPS key) remained, per `OWNER-ACTIONS.md` item 0/1b, until the paragraph above closed it.

**Business Data Knowledge, re-measured 2026-09-29.** ONE MEASURED TRANSACTION EVER ($19 GROSS, 2026-08-21, A REFERRAL). CURRENT TRAFFIC BASELINE (`GOALS.md`, MEASURED 2026-09-29 BY A DIRECT UMAMI DATABASE READ, FILTERED TO THIS SITE'S `website_id`): 48 VISITORS ACROSS 119 VISITS AND 731 PAGEVIEWS IN 30 DAYS, DOWN FROM 57. THE TRAILING WEEK RECORDS 14 VISITORS / 18 VISITS / 50 PAGEVIEWS, BUT 30 OF THOSE PAGEVIEWS AND 7 OF THOSE VISITORS ARRIVED IN ONE 20-MINUTE BURST ON 27 SEPTEMBER; EX-BURST THE WEEK IS 7 VISITORS / 9 VISITS / 20 PAGEVIEWS, DOWN ON THE PREVIOUS 12 / 14 / 27. AN UNFILTERED READ THE SAME NIGHT SAID 239 VISITORS, BECAUSE THIS UMAMI INSTANCE SERVES THREE SITES; `ops/experiments.py` NOW REFUSES A `website_event` QUERY THAT NAMES NO WEBSITE. IN UMAMI `session_id` IS THE VISITOR AND PERSISTS ACROSS DAYS, THE VISIT IS `visit_id`. BUY-CLICKS: 11 ALL TIME FROM 9 DISTINCT VISITORS (BOOK 4, METHOD 3, CONSULTING 2), OF WHOM ONE EVER PAID. **CORRECTED 2026-09-29: THIS LINE READ "STRANGERS' BUY-CLICKS SINCE 7 SEPT: 0" AND THAT IS NO LONGER TRUE**, THERE ARE CLICKS ON 14 AND 28 SEPTEMBER; `LEARNINGS.md` LRN-0010 WAS RIGHT WHEN WRITTEN AND HAS BEEN OVERTAKEN. THE EMAIL LIST IS READABLE, NOT UNREADABLE, AND MEASURED EMPTY: 0 SUBSCRIBERS (ISSUE #15, STILL UNRESOLVED, BLOCKS CAPTURE ENTIRELY).

**Executive Visibility:** LIVE, VIA `EXECUTIVE-DASHBOARD-LIVE.md` (GENERATED BY `ops/dashboard.py`, NOT HAND-TYPED)

**Immediate Focus:** UNCHANGED IN SUBSTANCE SINCE 2026-09-02, RE-CONFIRMED 2026-09-15: TRAFFIC, NOT ANALYTICS OR TECHNICAL DEBT, IS THE CONSTRAINT (`GOALS.md`). 2.5 VISITORS A DAY. THE CHANNELS THAT COULD CHANGE THAT (VIDEO PLATFORMS, LINKEDIN, PINTEREST, INSTAGRAM) NEED ACCOUNTS ONLY PHIL CAN CREATE (`OWNER-ACTIONS.md`); DISTRIBUTION PREP IS READY AND WAITING (114 ZONES OF VIDEO IN MULTIPLE CUTS, PINTEREST/INSTAGRAM CARDS FOR ALL 114 ZONES, ~4,939 READY-TO-PUBLISH SOCIAL UNITS TOTAL). THE DOMINANT DEFECT CLASS FOUND ACROSS MANY REVIEWS IS A CORRECTED SOURCE WHOSE SHIPPED ARTIFACT WAS NEVER RE-DERIVED (`BACKLOG-2026-09-07.md` SECTION 7). THE HONEST STATE OF THIS BUSINESS IS "COMMERCE WORKS, TRAFFIC IS MEASURED AND NEARLY ALL DIRECT, AND PRODUCTION MATCHES HEAD EXACTLY (LAST CONFIRMED 2026-10-01T02:59:05Z AT BUILD `8fbc6b7d3d2599ae`, PER `ops/deploy-verdict.json`, COMMIT `b57ba4f58`; SEE THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE), AND THE NEXT STEP ON EVERY DISTRIBUTION CHANNEL IS PHIL'S OWN ACTION." UPDATED 2026-09-30, SCHEDULED OPERATOR: THE PRIOR "04167f5ad701b0e4/15:36:31Z" READING HAD GONE ONE CONFIRMATION STALE WITHIN THE HOUR (THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE WAS ALREADY CORRECT, CAUGHT BY `gate_status_deploy_verdict_current` ON THAT CYCLE'S OWN RUN) BUT THIS LINE WAS NEVER TOLD, BECAUSE THE GATE ONLY EVER CHECKED BLOCKER-001 AND THE FIRST "**PRODUCTION KNOWLEDGE" MATCH, NOT THIS ONE: A THIRD SECTION OF THE SAME FILE CARRYING THE SAME CITATION, THE SAME "SOURCE CORRECTED, SIBLING NEVER TOLD" SHAPE THIS GATE EXISTS TO CATCH, JUST ONE SECTION FURTHER THAN IT HAD BEEN WIDENED TO REACH. RE-DERIVED FROM THE CURRENT VERDICT DIRECTLY (`deploy_gap_material_commits` RETURNS ZERO), NOT CARRIED FORWARD; THE GATE ITSELF WIDENED TO ALSO CHECK THIS SECTION, SO IT CANNOT DRIFT HERE AGAIN UNNOTICED. UPDATED 2026-10-01, SCHEDULED OPERATOR: THE PRIOR "6f5176355eb29401/16:49:06Z" CITATION HAD GONE ONE CONFIRMATION STALE OVERNIGHT, CAUGHT BY THIS CYCLE'S OWN `preflight.py` RUN NAMING ALL THREE SECTIONS AT ONCE; RE-DERIVED DIRECTLY (`deploy_gap_material_commits('b57ba4f58')` RETURNS ZERO), NOT CARRIED FORWARD. CORRECTED 2026-10-01T11:2x, PM CHECK-IN: THE "PRODUCTION MATCHES HEAD EXACTLY" CLAIM ABOVE WENT STALE AGAIN WITHIN THE SAME DAY. `deploy_gap_material_commits('b57ba4f58')` NOW RETURNS 5 COMMITS, 2 MATERIAL (`f8d7b5aaa`, `f20f541a4`); SEE BLOCKER-001 AND THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE FOR DETAIL. THE HONEST STATE IS: PRODUCTION IS BEHIND HEAD BY ONE REAL TRUST FIX (THE SITEWIDE FALSE ZONE-ORDER CLAIM) STILL AWAITING PHIL'S OWN REDEPLOY. WIDENED 2026-10-01T13:2x, PM CHECK-IN: THAT COUNT IS NOW 7 COMMITS, 3 MATERIAL (THE SAME TWO PLUS `52dfa04f1`, THE FAQPAGE-VS-VISIBLE-COPY FIX), CAUGHT BY THIS CYCLE'S OWN `preflight.py` RUN (`status-deploy-gap-count-current`); SEE BLOCKER-001 ABOVE FOR THE FULL ACCOUNT. THE HONEST STATE IS UNCHANGED IN KIND: PRODUCTION IS BEHIND HEAD BY REAL TRUST FIXES STILL AWAITING PHIL'S OWN REDEPLOY. WIDENED 2026-10-02T05:2x, PM CHECK-IN: THAT COUNT IS ITSELF NOW STALE, CAUGHT AGAIN BY THIS CYCLE'S OWN `preflight.py` RUN; REAL GAP IS NOW 24 COMMITS, SEE BLOCKER-001 ABOVE FOR THE FULL ACCOUNT (HAND MATERIAL SPLIT NOT RE-DERIVED GIVEN THE VOLUME). THE HONEST STATE IS UNCHANGED IN KIND: PRODUCTION IS BEHIND HEAD BY REAL, UNBROKEN TRUST AND CONTENT FIXES STILL AWAITING PHIL'S OWN REDEPLOY.

**Correction, 2026-09-30, scheduled operator: "the next step on every distribution channel is Phil's own action" stopped being true for Bluesky the moment this line's own paragraph shipped.** Bluesky already had a real account and real traffic (5 visitors, all time) with no drafting pipeline; `ops/bluesky_drafts.py` and `.github/workflows/bluesky-drafts.yml` now draft and send 3 posts a day from the existing corpus, using the same SMTP secrets the LinkedIn and Facebook/X draft mailers already send through. No new owner credential or account was needed, so this one channel no longer waits on Phil at all: he only has to keep reading the morning email and posting as written, same as the other two. See `GOALS.md` and `OWNER-ACTIONS.md` for the full account.

---

# Final Rule

`STATUS.md` must describe reality, not aspiration.

If something is unknown, write `UNKNOWN`.

If something is degraded, write `YELLOW`.

If something is broken, write `RED`.

If something is healthy, prove it.

The purpose of this file is to let every autonomous agent answer:

**Where are we now, what matters most, and what should happen next?**
