# BACKLOG-2026-09-07.md closed-section archive

Numbered "## N. Closed/Done ..." sections older than ops/rotate_backlog_closed.py's retention window, moved here verbatim from BACKLOG-2026-09-07.md by that script. Never hand-edited. Newest first.

## 113. Closed 2026-11-04, scheduled operator cycle: a "bedside table" zone-level vocabulary gap, found by mining the partial tier for single-unmatched-word patterns the 22:4x PM check-in named as not yet confirmed exhausted

Every row in sections 2-6 was again Done, Closed or Phil-gated (29 open GitHub issues reconfirmed directly, all `decision`/`blocked-on-art`, issue #42's full thread read end to end, no genuine Phil reply), the room-guide lane confirmed complete at 20/20 rooms, and the cold-read ledger confirmed exhausted at 308/308, 0 stale, 0 un-ledgered. The 22:4x PM check-in's own handoff named the one lane not yet confirmed exhausted: re-mine the `partial` tier for an undiagnosed single-unmatched-word collision, the same method sections 109-112 used for "layout" and "hallway". Grouped every `partial` row with exactly one unmatched word by that word, both tiers: almost all high-frequency hits (design, diy, tips, pinterest, ikea, plan, decorating, decorate, porch, furniture, railing, declutter) are the generic-modifier or named-brand trap A40/A48 already ruled out, correctly left alone. "Bedside" was different: 10 rows across both tiers, all "how to organise/organize bedside table/drawers" and close variants, several scoring to clearly wrong pages via coincidental word overlap (`/articles/how-to-declutter-a-kitchen.html` on "organize"+"table"; `/zones/dining-room-the-dining-table.html` on "table"+"drawer"), the same misattribution shape as A37/A45/A46/A49. Checked Primary Bedroom's own two nightstand zones in `content.json` before adding anything: Nightstand Left and Nightstand Right each have real, substantial `done_looks_like`/`passes` text about the drawer and the top surface already, but neither zone's own heading ever uses the household word "bedside table," only "nightstand." The queries never specify a side, so rather than arbitrarily pick one zone, added "bedside table" to both `zone-also-called.json` entries (`Primary Bedroom|Nightstand Left` and `Primary Bedroom|Nightstand Right`): a reader asking generically about a bedside table is equally served by either real page, not a coincidental collision. Reran `ops/build_zone_pages.py` (self-chained: canonical links, landmarks, PWA, AVIF, fingerprint, sitemap, build-id), then `ops/build_seo.py` directly. Verified: `test_gate_zone_also_called_is_heading.py` (6/6, both new headings render exactly as committed, confirmed by grep against the real rendered pages). `ops/keyword_demand.py --rescore` and `ops/keyword_demand_global.py --rescore`: 8 of the 10 target rows moved from wrong-page `gap`/mismatched `partial` to `covered` on the real Nightstand Right zone page (the scorer's own tie-break consistently picked Nightstand Right over Left, a sensible, non-arbitrary outcome since both pages answer the query equally); global tier gap count unchanged at 97 (none of the 10 were themselves `gap` rows; this was a misattribution/coverage fix, not a gap closure), partial 952 to 945, covered 1121 to 1128; US tier partial 1272 to 1271, covered 1437 to 1438. One residual row, "how to organise/organize bedside table drawers" (plural), stays `partial`: an exact-word-not-stem gap on "drawers" vs. the page's own singular "drawer," the same class A34/A36 already accepted leaving unchased elsewhere, and a scorer tie between the title surface (the kitchen article's title literally contains "drawers") and the heading surface (which now matches "bedside" but not the plural) that left `matched_on: "title"` for that one row; the heading_page field still correctly names the real Nightstand Right zone, so a future cycle reading this row is not misled, just not maximally scored. `check_urls.py` (235/235), `audit_pages.py` (240/0, 0 duplicates), `fix_dashes.py`/`fix_dialect.py --check` (0/0), `affiliate.py --check` (165 documents), `check_sellable.py` (124/126 Stripe-matched, 2 known service SKUs), `link_graph_report.py` (0 orphans, min 2 inbound), `build_id.py --check` (current), `ops/audit_visual.py` scoped to both changed zone pages (desktop and mobile, 0 findings each) all clean. `preflight.py --skip-tests` run fresh before and after the change: 0 FAIL both times through every gate reached, genuinely stalled at the documented network-bound `gate_etsy_pdfs_current` both times (confirmed by static CPU-time readings, not assumed), reported unchecked past that point per `CLAUDE.md` 0.4. No price or product touched; two existing zone pages edited, no new page; `IndexNow` to submit on push.

Pushed to main: `ops/zone-also-called.json`, `site/zones/primary-bedroom-your-own-nightstand.html`, `site/zones/primary-bedroom-the-other-sleeper-s-nightstand.html`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, `ops/KEYWORD-DEMAND-GLOBAL.md`, this entry, dashboard files. No price or product touched; two existing zone pages edited, no new page; `IndexNow` to submit on push.

## 112. Closed 2026-11-04, scheduled operator cycle: a "hallway closet" misattribution, found by mining the partial tier for single-unmatched-word patterns past "layout"

Section 111 closed the "layout" lane completely. Rather than re-confirm that exhaustion a sixth time, mined the wider partial tier for the same shape against every other single-unmatched word, not just "layout": most high-frequency hits (design, diy, tips, decorating, build, decorate) are the generic-modifier trap A40 named ("plan") and would misattribute many unrelated rooms' queries if chased, correctly left alone. "Hallway" was different: not a generic modifier, a real household word, and most "hallway closet" queries already route correctly to `hall-closet-deck.html`. Three did not: "how to organize a deep/small hallway closet" and "small hallway closet organization ideas" scored `partial` against an unrelated linen-closet or laundry-room article via a tied word-overlap collision on "organize"/"closet" alone, the same alphabetical-tie-break shape as A25/A26/A37. Checked the room's own identity before adding anything: Hall Closet's own intro already calls it "the darkest and deepest storage in the house," i.e. the closet in the hallway, so "hallway closet" is the plain household name, not invented. Added it to the existing `Hall Closet` entry in `room-also-called.json` (alongside "hall cupboard"), reran `ops/build_zone_pages.py` (self-chained: sitemap, fingerprints). Verified directly: rescoring both tiers moved exactly 7 rows' `heading_page` to a genuine Hall Closet page, none changing status bucket (misattribution fixes of this shape rarely do, same as A37), none newly misattributed, audited by hand including the "coat closet" and "cold hallway" rows, which correctly stayed where they were. `check_urls.py` (235/235), `audit_pages.py` (240/0), `fix_dashes.py --check` (0/0), `affiliate.py --check`, `check_sellable.py` (124/126), `link_graph_report.py` (0 orphans), `test_room_also_called.py` OK, `audit_visual.py` (desktop+mobile, scoped) 0 findings all clean. `preflight.py --skip-tests` run fresh before and after: 0 FAIL both times, one real FAIL caught and self-healed mid-cycle (a stray probe file left by an earlier killed run of this same session's own preflight attempt, `gate_no_stray_probe_files` deleted it, rerun clean). GitHub reconfirmed directly: 29 open issues, all `decision`/`blocked-on-art`, zero genuine Phil reply (read issue #42's full thread). No price or product touched; one existing room page edited, no new page; `IndexNow` to submit on push.

Pushed to main: `content/manual/source/content.json`, `mcp/content.json`, `site/rooms/dining-room.html`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, this entry, dashboard files. No price or product touched; one existing room page edited, no new page; `IndexNow` to submit on push.

## 111. Closed 2026-11-04, PM check-in: section 110's own "Next" line called the layout lane exhausted; it had only audited for misattribution regressions, not re-scanned for the same gap in rooms it never touched. Seven more rooms had it. One closed this slot, six handed to the operator.

**Previous work confirmed finished.** Attached clean (fetch, genuine unshallow, `checkout -B main origin/main`, ff-only onto `325e0d857`, tree clean). `preflight.py --skip-tests` run fresh to real completion-or-stall: 0 FAIL through every gate reached, genuinely stalled at the documented network-bound `gate_etsy_pdfs_current`, killed by pid, same standing limitation. GitHub re-checked directly: 30 open issues, unchanged, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02.

**Section 110's exhaustion claim did not hold up.** It audited "all 27 other layout rows site-wide" for regressions from its own two-room fix, then concluded the lane was exhausted. Re-ran the same raw-`unmatched_words` grep it itself recommended in its own "changing next cycle" line, cold, against both tiers: 15 US-tier and 7 global-tier rows still carry `layout` unmatched. Most are off-topic or belong to pages this product has no business answering (`best way to layout a garden`, a `kitchen`/`mudroom` pair that only *look* unfixed because the scorer's tie-break between a tied title/heading score checks the title surface's words, not the heading's, even though both rooms already carry the heading and a human reader already finds the answer there). Filtering those out, seven rooms had the exact section-109/110 shape, word genuinely absent from every heading on the site: Dining Room, Guest Bathroom, Home Office, Primary Bedroom (x2 query variants), Laundry Room (+ "utility room" variant), Primary Bathroom (x2), and Pantry ("larder organization/organisation and layout", both spellings, global tier only).

**Closed one, Dining Room, inside this slot.** Grounded in facts the room's own zones already state, nothing invented: the Dining Table's own `done_looks_like` already says placemats and trivets live in the sideboard drawer "one step away"; the Buffet/Sideboard Surface's own `done_looks_like` already says its bare-wood run sits "at the end nearest the table"; the China/Display Cabinet's purpose is "safe, visible, and genuinely usable" (not meal-time reach); the Beverage/Coffee Station's purpose is handing a drink over "without crossing into the kitchen." Added a "Room layout" tip to `content.json`'s Dining Room tips array using the existing mechanism, resynced `mcp/content.json`, reran `ops/build_zone_pages.py`.

**Verified.** `ops/keyword_demand.py --rescore`: the targeted row ("dining room layout ideas") moved `partial` (0.667) to `covered` (heading coverage 1.0, zero unmatched words). Global tier unaffected (correctly; that query isn't in it). Gap counts unchanged in both tiers. Checked for misattribution directly: only the targeted query and one pre-existing, correctly-unrelated partial row now resolve to the Dining Room page. `check_urls.py` (235/235), `audit_pages.py` (240 pages, 0 findings), `fix_dashes.py --check` (0/0). `preflight.py --skip-tests` re-run after the change: identical 0 FAIL, same stopping point.

**Handing six rooms to the operator, not doing them in this slot.** Writing six more grounded, individually-verified tips inside a 30 minute triage window risks the generic-filler and misattribution mistakes this exact lane has already made twice; it is real work, not a quick close. For the operator at :43, already scoped so no re-derivation is needed: Guest Bathroom (`guest bathroom layout ideas`), Home Office (`how to arrange a home office layout`, `how to plan a home office layout`, both tiers), Primary Bedroom (`large primary bedroom layout`, `primary bedroom layout ideas`), Laundry Room (`laundry room layout ideas`, `utility room layout`, both tiers), Primary Bathroom (`primary bathroom layout ideas`, `small primary bathroom layout`), Pantry (`larder organization and layout` / `larder organisation and layout`, global tier). Ground each in that room's own existing zone facts only, per the method above; verify with `--rescore` and a misattribution check before shipping.

**Closed 2026-11-04, scheduled operator cycle: all six done, in this one slot, because each tip grounds directly in facts the room's own zones already state and none needed invention.** Guest Bathroom: the vanity counter's sightline from the doorway, the guest linen zone's bundled towels, the toilet area's seated-reach spare roll, the guest vanity storage nobody but the owner opens. Home Office: the desk's floor-mounted power strip, the bookshelf's seated-eye-level reference, the printer's need for clear air behind it. Primary Bedroom: the bed's dual walking paths to the door, the right nightstand's lamp cord routed behind its leg, the dresser's wall-anchored anti-tip strap, the closet's hanging-space and rod-clearance numbers. Laundry Room: the machines' bare-floor doors shared with the sorting zone's walking line, the folding surface's proximity to the dryer, the air-dry rack folding flat against the wall, the detergent zone's shoulder-height latch. Primary Bathroom: the vanity counter facing the door, the toilet area's seated-reach reserve rolls, the under-sink cabinet's swing clearance for its shut-off valves, the wall-mounted medicine cabinet buying back floor space. Pantry: the dry goods shelves' doorway sightline, the canned goods' riser depth, the snack zone's two-height split, the backstock zone's waist-height weight rule. Added via the existing `content.json` tips mechanism (label `"Room layout"`), same pattern as Dining Room above; `mcp/content.json` resynced; `ops/build_zone_pages.py` regenerated all six room pages.

**Verified.** `ops/keyword_demand.py --rescore` and `ops/keyword_demand_global.py --rescore`: 8 of the 11 target query rows moved `partial` to `covered` across both tiers (gap counts unchanged, 115 US / 97 global); the remaining 3 (`how to plan a home office layout`, `large primary bedroom layout`, `small primary bathroom layout`) stay `partial` on the single unmatched word `plan`/`large`/`small`, generic modifiers the Dining Room precedent already declined to chase, correctly left alone rather than invented. Checked every one of the 28 US-tier and 21 global-tier rows containing the word "layout" for misattribution, not just the 11 targeted: all resolve to the correct room; one incidental improvement, `how to organize bedroom layout` (no room qualifier) moved from the bedroom-declutter article to the Primary Bedroom page, because that page is now the only bedroom page answering layout at all, not a misattribution. `check_urls.py` 235/235, `audit_pages.py` 240/0, `fix_dashes.py --check` 0/0 on touched files.

**Went well:** treating a prior cycle's own "exhausted" conclusion as a claim to re-check rather than a fact, even though that cycle had explicitly audited the area already.

**Did not go well:** this is the third time this exact mistake shape has recurred (section 109 named it once, section 110 repeated it against a different tool, this entry found section 110 itself had repeated it a third time against a narrower scope than it claimed). The recurring root cause: "I checked X and found nothing more" gets written as "X is exhausted" without naming what X actually covered.

**Changing next cycle:** when closing a keyword-gap lane, name exactly what was checked (which tool, which rooms, which tiers) in the same sentence as the word "exhausted," so the next cycle can tell a narrow check from a complete one without re-deriving it.

**Next:** six rooms above, scoped and grounded, for the operator. 30 open `decision` GitHub issues, none from Phil, remain the standing queue otherwise.

## 110. Closed 2026-11-04, scheduled operator cycle: a 2026-11-03 cycle's own "changing next cycle" note (ops/NIGHTLY-LOG.md) had re-checked the layout lane through `room_guide_underperformance.py` alone, which only surfaces `gap` rows; Living Room and Family Room both carried real, unfixed `partial`-tier layout demand that tool cannot see

**Previous work confirmed finished before starting anything new.** Fresh checkout, genuine unshallow (`fetch --unshallow`, 873 commits behind), `checkout -B main origin/main`, ff-only onto `1e2533e3a`, tree clean. `preflight.py --skip-tests` run fresh (not cited): 0 FAIL through every gate reached, stalled at the documented `gate_etsy_pdfs_current` network gate, killed by pid per standing precedent. GitHub re-checked directly via the API: 30 open issues, unchanged, all `decision`, none from Phil since 2026-11-02.

**Independently re-derived, not cited.** A later 2026-11-03 cycle logged (`ops/NIGHTLY-LOG.md`) that it ran `room_guide_underperformance.py` fresh, grepped its output for "layout", and found no matches outside the already-fixed Mudroom row, concluding the lane was exhausted. That tool ranks `gap` rows only. Read both `ops/keyword-demand.json` and `ops/keyword-demand-global.json` directly for every `partial`-or-`gap` row whose `unmatched_words` contains "layout": Living Room (4 rows, both tiers) and Family Room (4 rows, both tiers) each carry real "___ room layout ideas" demand, routing correctly to their own deck pages already, but `grep -ci layout site/rooms/living-room.html site/rooms/family-room.html` returned 0 for both, the exact "missing the word anywhere on the site" shape section 109 closed for Mudroom, Kitchen, Garage, Nursery and Workshop, just invisible to the gap-only tool the 2026-11-03 cycle trusted.

**Fixed with the existing mechanism, nothing new built.** Added a "Room layout" tip to each room's `tips` array in `content.json`, grounded entirely in facts each room's own zones already state. Living Room: the Floor and Circulation Path zone's own purpose ("let anyone cross this room... without touching anything") and done-looks-like (a continuous clear route from the doorway past the sofa to the other exit) decide the layout before furniture does; the Media Center's own safety note (a clear hand's gap of air around the vents) rules out pushing it into a corner; the Coffee Table and Side Tables' own purposes place them by the seating they serve. Family Room: the room's own intro already states the ordering fact ("start with the media zone, because its cables run under and behind everything else"); the Toy and Play Zone's own done-looks-like (enough clear floor for two children to build) and the Charging Zone's and Craft Zone's own purposes (a hard surface near a socket; one surface kept clear between projects) ground the rest. Nothing invented. Resynced `mcp/content.json` from the edited source. Reran `ops/build_zone_pages.py` then `ops/build_seo.py` directly.

**Verified.** `ops/keyword_demand.py --rescore` and `ops/keyword_demand_global.py --rescore`: 4 of the 8 target rows per tier moved `partial` to `covered` (both "ideas" and "ideas with tv" variants on each room; the "with fireplace" variants stayed `partial` at 0.75, honestly, since this site makes no fireplace claim); a genuine bonus, "bonus room layout," also moved to `covered` on Family Room's page, which it already matched before this fix. Gap count unchanged in both tiers (115 US, 97 global): nothing was pulled off `gap` incorrectly, because this fix only adds a heading word, it does not touch scoring logic. Audited all 27 other "layout" rows site-wide by hand (diffed old vs. new status for every query, not just the eight targeted): zero regressions, zero misattributions to Living Room or Family Room from an unrelated room's query. `check_urls.py` (235/235), `audit_pages.py` (240/0 findings), `fix_dashes.py`/`fix_dialect.py --check` (0/0), `affiliate.py --check` (165 documents), `check_sellable.py` (124/126, 2 known service SKUs), `link_graph_report.py` (0 orphans), `build_id.py --check` (current), `audit_visual.py` scoped to `site/rooms/living-room.html` and `site/rooms/family-room.html` (desktop and mobile, 0 findings each) all clean. `preflight.py --skip-tests` run fresh again after the change: identical 0 FAIL result, same stopping point. No price or product touched; two existing room pages edited, no new page; `IndexNow` to submit on push.

**Went well:** checking a settled "exhausted" conclusion against the real per-query data again, exactly as section 109's own handoff asked, rather than trusting a tool whose blind spot had already been named once.

**Did not go well:** the 2026-11-03 cycle's mistake was a narrower version of the same thing section 109 itself warned about ("a room's zero gap-count is not the same claim as no fixable row remains"), applied to the wrong tool rather than the wrong room. A one-line check ("does this tool even look at partial rows?") would have caught it before logging "exhausted."

**Changing next cycle:** `room_guide_underperformance.py` ranks `gap` rows only; a lane described as "exhausted" by that tool alone has not been checked against `partial` rows. Before writing "exhausted" for any keyword-gap lane, grep the raw `unmatched_words` field across both tiers directly, not just a ranking tool's own output.

**Next:** the remaining "layout" partial rows with unmatched sibling words ("fireplace", "tv" already closed; "plans", "event", "for students", "templates" on Workshop deliberately excluded as off-topic per A42's own ambiguous-word precedent) look exhausted for this specific word. No further unfixed `gap` or missing-heading-word `partial` row of this shape was found this cycle. 30 open `decision` GitHub issues, none from Phil, remain the only standing queue.

Pushed to main: `content/manual/source/content.json`, `mcp/content.json`, `site/rooms/living-room.html`, `site/rooms/family-room.html`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, `ops/KEYWORD-DEMAND-GLOBAL.md`, this entry, dashboard files. No price or product touched; `IndexNow` to submit on push.

## 109. Closed 2026-11-04, scheduled operator cycle: section 108 confirmed the gap tier genuinely exhausted; mining the wider partial tier the same way found one more real fix, a missing Mudroom "Room layout" tip

**Previous work confirmed finished before starting anything new.** Fresh checkout, genuine unshallow, `checkout -B main origin/main`, ff-only onto `97194ccb9`, tree clean. `cycle_signal.py --check` read SAME against the prior cycle's own snapshot; GitHub re-checked directly via the API, 30 open issues, unchanged, all `decision`/`blocked-on-art`, none from Phil. `check_urls.py`, `audit_pages.py`, `fix_dashes.py --check`, `affiliate.py --check`, `check_sellable.py`, `link_graph_report.py` all clean before touching anything.

**Independently re-derived section 108's own conclusion rather than citing it.** Read `room_guide_underperformance.py`'s remaining `gap` rows directly against each target zone's own `content.json` purpose/done_looks_like text, per CLAUDE.md 5c/5d: Garage's "raised garden beds" and "soap making supplies" and Pantry's "pantry organization ideas dollar tree" have no genuine zone grounding to stretch to (soap-making fits no existing zone's stated purpose; "dollar tree" and "cricut" are brand names CLAUDE.md 5 bars from content, and the scorer only credits an exact word match, so adding them without the literal brand word closes nothing); "draw a larder organization chart" is the same autocomplete-garble noise shape as prior excluded rows. Confirmed, not merely trusted: the gap tier is genuinely exhausted.

**Mined the wider `partial` tier the gap-only ranking does not surface, and it is not exhausted the same way.** Read every `partial` row carrying the word "layout" across both harvests (28 rows) and found Mudroom alone, among the four rooms A40/A42 already built the generic `tips.get("Room layout")` heading for (Nursery, Kitchen, Garage, and by the same mechanism any future room), had never received its own entry: 6 "mudroom design/layout ideas" queries (1 gap, 5 partial), all missing the word "layout" in any heading anywhere on the site.

**Fixed with the existing mechanism, nothing new built.** Added a "Room layout" tip to Mudroom's `tips` array in `content.json`, grounded entirely in facts the room's own content already states: the door decides the order, not the wall; the threshold mats, the Shoe and Boot Storage's lipped tray and the Pet Station all have to sit within reach of the door itself (their own `done_looks_like`/cleaning-note text already says so); the Family Hook Zone and Bench and Transition Surface come next; Seasonal Outdoor Gear and the Cleaning and Utility Zone, reached far less often, can sit furthest away, even on a high shelf. Resynced `mcp/content.json`, reran `ops/build_zone_pages.py` then `ops/build_seo.py`.

**Verified.** `ops/keyword_demand.py --rescore` moves "mudroom design layout ideas" from `gap` (0.333, `/mudroom-deck.html`) to `partial` (`heading_coverage` 0.667, matched on heading, `/rooms/mudroom.html`); site-wide gap count 116 to 115. Audited all 28 "layout" rows across both tiers by hand, the exact collision A40 warned about: no other room's query was pulled toward Mudroom, every one still routes to its own page, because this tip deliberately omits the generic word "design" the way A40's own fix dropped "plan." `check_urls.py` (235/235), `audit_pages.py` (240/0 findings), `fix_dashes.py`/`fix_dialect.py --check` (0/0), `affiliate.py --check` (165 documents), `check_sellable.py` (124/126, 2 known service SKUs), `link_graph_report.py` (0 orphans), `build_id.py --check` (current), `audit_visual.py` scoped to `site/rooms/mudroom.html` (desktop and mobile, 0 findings each) all clean. `preflight.py --skip-tests` run fresh after the change, 0 FAIL through every gate reached, stalled at the documented `gate_etsy_pdfs_current` network gate, killed by pid per standing precedent rather than trusted past it. A stray in-flight `ops/cycle-signal.json` checkpoint from the backgrounded run, and one stray `site/zones/_visual_probe.html` left by an unrelated killed `audit_visual.py` invocation, were both found and discarded/auto-cleaned before this commit, neither staged. No price or product touched; one existing room page edited, no new page; `IndexNow` to submit on push.

**Went well:** checking a settled "exhausted" conclusion against the real files instead of carrying it forward, then widening the search from gap-only to partial-plus-missing-heading-word, found a genuine fix after the gap tier itself had actually run dry.

**Did not go well:** nothing new; the same standing sandbox gaps (no Stripe/SSH/mail credential, Etsy fee page 403, no JRE) every recent cycle has already logged.

**Changing next cycle:** when `room_guide_underperformance.py`'s gap count reads zero for a room, that is not the same claim as "no fixable row remains"; check its `partial` rows for a missing-heading-word pattern (the "Room layout"/"Garage sale"/"Design" shape) before concluding a room is done.

**Next:** the partial tier may hold a few more "Room layout"-shaped single-word gaps worth one more pass across other rooms before concluding that lane is exhausted too. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil, remain the only standing queue otherwise.

Pushed to main: `content/manual/source/content.json`, `mcp/content.json`, `site/rooms/mudroom.html`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, this entry, dashboard files. No price or product touched; `IndexNow` to submit on push.

## 108. Closed 2026-11-04, PM check-in (01:4x slot): the "seasonal pricing model" row section 105/A56 diagnosed in prose but never gated, closed along with five more of the same commercial-intent shape

**Previous work confirmed finished before starting anything new.** Fresh checkout, genuine unshallow, `checkout -B main origin/main`, ff-only onto `eaab2c297`, tree clean. Re-derived rather than cited: `room_guide_underperformance.py` unscoped confirmed Workshop (0 gap), Primary Bedroom (2 gap) and Family Room (2 gap) hold at the counts section 107/A56 last reported, no drift. `preflight.py --skip-tests` run fresh in the background, watched to a genuine stall (flat CPU) at the documented `gate_etsy_pdfs_current` network gate: 0 FAIL through every gate reached. 30 open GitHub issues reconfirmed via the API, unchanged, all `decision`/`blocked-on-art`, none from Phil; the owner-notification cooldown from 2026-11-02T04:17Z has not yet elapsed (no-repeat-before 2026-11-04T04:00Z) and nothing material changed, so correctly sent none.

**A diagnosed-but-ungated row found while re-checking the ranking, the same defect class A56 closed for "dental"/"gardening series."** Section 105 (and the 22:0x/23:4x entries before it) correctly read Hall Closet's "organize seasonal pricing model" as a B2B query colliding on "organize seasonal" alone and declined to build content for it, but never added it to `OFF_TOPIC_CONTEXT`, so it kept re-scoring as a live `gap` row on every ranking since. Mining the same shape (business/B2B-intent queries word-overlapping onto household zones via "cleaning", "equipment", "organize" or "baking") found five more, none caught by any existing pattern: "baking supplies for small business" and "how to start baking supplies business" (Pantry Baking Zone), "business plan for a cleaning equipment", "cleaning supplies for a business", "equipment needed for cleaning business", "office cleaning equipment list" and "cleaning company equipment list pdf" (Hall Closet Cleaning Equipment/Cleaning Supply Zones), and "how to start an outdoor storage business" (Patio or Deck Outdoor Storage Zone).

**Checked each target zone's own content.json purpose before excluding anything, per CLAUDE.md 5c/5d.** Hall Closet's Cleaning Equipment Zone ("parks the vacuum, broom, and mop"), Cleaning Supply Zone and Seasonal and Guest Zone, Pantry's Baking Zone ("holds everything you need to start a bake without a trip to the shop"), and Patio or Deck's Outdoor Storage Zone ("get the cushions under a lid within a minute of the first drop of rain") each describe household use only; none addresses running or starting a business, a commercial equipment checklist, or a pricing model. Verified against the full corpus before adding: "business" appears in exactly the 6 rows named above, "equipment list" in exactly 2, "pricing model" in exactly 1, across both US and global tiers; no `covered` row (e.g. "how do you organize a company workshop", "cleaning and organizing company", "how to start a detergent company") shares any of the three phrases, so excluding them cannot suppress a genuine match.

**Fixed at the regex.** Added `\bbusiness\b|\bequipment list\b|\bpricing model\b` to the existing `OFF_TOPIC_CONTEXT` pattern in `ops/room_guide_candidates.py` (shared by `room_guide_underperformance.py`).

**Turned into a test, per CLAUDE.md 10b.** `test_room_guide_candidates.py` (now 15/15) and `test_room_guide_underperformance.py` (now 17/17) each gained cases proving a noise row is excluded and a genuine on-topic "organize cleaning supplies" row is not. Fail-then-pass proved directly: `git stash` on `ops/room_guide_candidates.py` alone, reran both test files, watched exactly the 3 new "excluded" cases fail in each (the "NOT excluded" case and every pre-existing case stayed passing), restored, reconfirmed 15/15 and 17/17.

**Verified.** Full unscoped `room_guide_underperformance.py` run: only Hall Closet (40% to 39% uncovered, 2 gap to 1, the "closet tutorial guide" row already correctly left unfixed) and Patio or Deck (52% to 50%, 14 partial to 13) moved; every other room's counts unchanged, confirmed by diffing the full before/after output rather than spot-checking. Pantry's two business rows never counted in the first place (they contain none of `organiz|declutter|clean|storage|stock`, so the upstream `ON_TOPIC` filter already excluded them; the new pattern is still correct and consistent for any future seed that does carry one of those words). `room_guide_candidates.py` still reports 0 guide-less rooms. `check_also_called_digital_collision_fast.py` clean. `fix_dashes.py --check` 0/0 on all three changed files. `check_urls.py` 235/235. A stray in-flight `ops/cycle-signal.json` checkpoint from the backgrounded preflight run was discarded (`git checkout --`), not committed. No price, product or page touched; these are diagnostic tools, not `site/` generators, so no rebuild or `IndexNow` applies.

**Went well:** re-checking a settled "left alone" conclusion instead of carrying it forward unchanged found a genuinely ungated defect, the same shape as A56, and mining the full cluster past the one originally-named row closed five more in the same pass.

**Did not go well:** nothing new.

**Changing next cycle:** nothing; same standing discipline (check the real rows and the zone's own content before excluding or adding anything, and re-check a prior "declined" conclusion for whether it was ever actually gated).

**Next:** Garage's 2 remaining gap rows (raised garden beds, soap making supplies) and Hall Closet's 1 remaining gap row (closet tutorial guide) were already checked and correctly left unfixed in section 105/107; no further unfixed `gap` row exists anywhere in the current ranking. The content-gap-mining lane is now genuinely exhausted across all 20 rooms. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil, remain the only standing queue.

Pushed to main: `ops/room_guide_candidates.py`, `ops/tests/test_room_guide_candidates.py`, `ops/tests/test_room_guide_underperformance.py`, this entry, dashboard files. No price, product or page touched; `IndexNow` not applicable.

## 107. Closed 2026-11-04, PM check-in (00:1x slot): Workshop's own "craft paint" collision, named and left unbuilt in section 100, closed by the exclusion mechanism rather than a synonym

**Previous work confirmed finished before starting anything new.** Fresh checkout, genuine unshallow, `checkout -B main origin/main`, ff-only onto `63c1b7a17`, tree clean. `preflight.py --skip-tests` run fresh in the background, watched rather than trusted: 0 FAIL through every gate reached, genuinely stalled (flat CPU, 8.8% then 8.4% across a confirmed 29s window) at the documented `gate_etsy_pdfs_current` network gate, killed there. 30 open GitHub issues reconfirmed via the API, unchanged, all `decision`/`blocked-on-art`, none from Phil. The ordering rule forbids picking any of them.

**Section 100 (2026-11-03) already found this exact row and declined to touch it, but only considered one fix.** It read Workshop's worst-ranked 61% uncovered as a "'paint' word-overlap collision, not real workshop demand" and wrote "left alone rather than built around, since fixing it honestly would need deciding whether this site serves craft-paint storage at all, not adding a synonym." That correctly ruled out writing craft-paint content into the Finishing and Chemical Zone. It did not consider the other fix already standing in this file for the identical shape: excluding the noise cluster from the scorer, the same mechanism `OFF_TOPIC_CONTEXT` already applies to Garage's car-organizer rows (section 105) and `DIGITAL` applies to Home Office's hard-drive rows (section 104). Section 100's own conclusion ("this site doesn't serve craft-paint storage") is exactly the premise that exclusion encodes; it was just never acted on.

**Checked the real rows before adding anything.** `score_room()` on live `Workshop`: 2 true `gap` rows and 20 `partial` rows. Read each `gap` row's `seeds` field, not just its text: "storage organizer for painting with diamonds" is diamond painting (a rhinestone craft kit, nothing to do with wood finish or fire-safe chemical storage); "how to organize benchmark advance materials" seeded from "how to organize bench" and drifted onto "Benchmark Advance," a K-12 classroom curriculum brand, not a home workshop's Material Rack. Checked the Finishing and Chemical Zone's own `content.json` purpose before excluding anything ("Store paint, glue, stain, and solvent so they stay usable and so they never start a fire"): fire-safe wood-finish storage, nothing about craft acrylics or classroom materials.

**Fixed at the regex, with the on-topic boundary checked against the real corpus before shipping, same discipline as section 105.** Added `\bbenchmark advance\b|\bdiamond painting\b|\bpainting with diamonds\b|\bcraft paint\b|\bpaint storage for artists\b` to the existing `OFF_TOPIC_CONTEXT` pattern in `ops/room_guide_candidates.py` (shared by `room_guide_underperformance.py`). Verified against every row in both harvests before and after: exactly 7 rows match (the 2 gap rows plus 5 craft/artist-worded partials: "craft paint organizers and storage," "craft paint storage container," "craft paint storage ideas," "diy craft paint storage ideas," "paint storage for artists"), and the genuine on-topic cluster ("chemical storage best practices," "spray paint storage ideas," "containers for paint storage," "how to paint a metal storage container," "spray paint can organizer," "acrylic paint storage organizer") matches none of the new pattern's branches and stays counted.

**Turned into a test, per `CLAUDE.md` 10b.** `ops/tests/test_room_guide_candidates.py` (now 11/11) and `ops/tests/test_room_guide_underperformance.py` (now 14/14) each gained cases: one proving a noise row (craft paint / diamond painting / benchmark advance) is excluded, one proving a genuine on-topic row is not. Fail-then-pass proved directly: `git stash` on `ops/room_guide_candidates.py` alone, reran both test files, watched exactly the new "excluded" cases fail (1 in the candidates file, 2 in the underperformance file) while every pre-existing case and the "NOT excluded" cases stayed passing, restored, reconfirmed 11/11 and 14/14.

**Verified.** `room_guide_underperformance.py --room Workshop` reports 0 gap, 15 partial (was 2 gap, 20 partial). Full unscoped run across all 20 rooms shows no other room's gap/partial/covered counts moved (Garage still 2 gap, Pantry 2 gap, Hall Closet 2 gap, Primary Bedroom 4 gap, Family Room 3 gap, Kitchen 1 gap, all unchanged from section 106's reading). `fix_dashes.py --check` on all three changed files: 0 em dashes, 0 en dashes. `check_also_called_digital_collision_fast.py` and `check_risks_evidence_fast.py` both clean. A stray in-flight `ops/cycle-signal.json` checkpoint from the first, interrupted background preflight attempt was discarded (`git checkout --`), not committed. No price, product or page touched; `room_guide_candidates.py`/`room_guide_underperformance.py` are diagnostic tools, not `site/` generators, so no rebuild or `IndexNow` applies.

**Went well:** re-reading a prior cycle's own "left alone" conclusion instead of either repeating it unchanged or re-opening it as a fresh decision found that the right fix already existed in this file, just never applied to this row.

**Did not go well:** nothing new.

**Changing next cycle:** nothing; same standing discipline (check the real rows and the zone's own content before excluding or adding anything).

**Next:** Pantry (2 gap), Primary Bedroom (4 gap), Family Room (3 gap) remain the next-ranked rooms with unfixed `gap` rows by `room_guide_underperformance.py`'s ranking, each needing the same row-by-row read. Garage's 2 remaining gap rows (raised garden beds, soap making supplies) and Hall Closet's 2 (closet tutorial guide, seasonal pricing model) were already checked and correctly left unfixed in section 105. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil. Leaving the Pantry/Primary Bedroom/Family Room row-by-row read to the hourly operator at :43: each needs the same zone-content cross-check this entry used, sized for a full slot, not a 30-minute triage.

Pushed to main: `ops/room_guide_candidates.py`, `ops/tests/test_room_guide_candidates.py`, `ops/tests/test_room_guide_underperformance.py`, this entry, dashboard files. No price, product or page touched; `IndexNow` not applicable.

## 106. Closed 2026-11-03, scheduled operator cycle: the Kitchen "corner cabinet" lead the 23:4x PM check-in named, a genuine exact-word-not-stem gap, same shape as A34/A36

**Did.** The concurrent 23:4x PM check-in (handled as a merge alongside section 105's push) named one real row worth a first look: Kitchen's partial (0.333) "how to organize a kitchen corner cabinet," the US-spelling sibling of "corner cupboard," which A31 already covered on 2026-10-30. Checked directly rather than trusted: `how to organise a kitchen corner cupboard` (GB/AU/IN) is `covered`, its `heading_page` correctly resolving to `/zones/kitchen-the-lower-cabinets-and-cookware.html` via the existing "Also called the corner cupboard" heading; the US "corner cabinet" phrasing scores `partial` (0.333) and its `heading_page` is `/kitchen-deck.html`, not the zone page at all, because the zone's own `<h1>` says "Cabinets" (plural) and no heading anywhere says "cabinet" (singular) or "corner cabinet," the exact exact-word-not-stem shape A34 (nappy/nappies) and A36 (craft/crafts) already fixed elsewhere.

**Checked against the zone's own content before adding anything.** `content.json`'s Lower Cabinet and Cookware Zone purpose ("Deep, low storage for the heavy pieces: pots, pans, lids, bakeware") supports "cabinet" exactly as well as the already-approved "cupboard"; both are the same real object, one US and one GB/AU/IN word for it. Added "corner cabinet" to the existing `Kitchen|Lower Cabinet and Cookware Zone` entry in `zone-also-called.json` alongside "corner cupboard" (the file's own multi-name joining already renders "Also called the corner cupboard or the corner cabinet," one honest heading, not two separate dishonest ones). Reran `ops/build_zone_pages.py` (self-chained: canonical links, landmarks, PWA, AVIF, fingerprint, sitemap, build-id).

**Verified.** `ops/keyword_demand_global.py --rescore` moves the query from `partial` to `covered` (partial 964 to 963, covered 1109 to 1110); `ops/keyword_demand.py --rescore` (US harvest) the same (partial 1277 to 1276, covered 1415 to 1416). `test_gate_zone_also_called_is_heading.py` (6/6, including the real committed site). `check_also_called_digital_collision_fast.py` clean. `fix_dashes.py --check` 0/0. `check_urls.py` (235/235), `audit_pages.py` (240/0 findings, 0 duplicates), `check_sellable.py` (124/126 Stripe-matched, 2 known service SKUs), `link_graph_report.py` (0 orphans), `affiliate.py --check` (165 documents) all clean. No price or product touched; one existing zone page edited, no new page; `IndexNow` to submit on push.

**Went well:** the handoff named a specific, checkable row rather than a vague lead, and it held up: a real exact-word gap with an honest fix already supported by the zone's own content, no fabrication needed.

**Did not go well:** nothing new.

**Changing next cycle:** nothing; same standing discipline.

**Next:** unchanged from section 105: Workshop (2 gap), Pantry (2 gap), Primary Bedroom (4 gap), Family Room (3 gap) by `room_guide_underperformance.py`'s ranking. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil.

Pushed to main: `ops/zone-also-called.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `build_zone_pages.py`-regenerated site files, this entry, dashboard files. No price or product touched; `IndexNow` to submit on push.

## 105. Closed 2026-11-03, scheduled operator cycle: did the row-by-row read section 104 handed off for Garage, Hall Closet and Kitchen; a real noise cluster found and excluded in Garage, the other two gap rows checked and correctly left unfixed

**Did.** Unshallowed and attached to main cleanly, ff-only onto `e5f6291b8`, tree clean. Read `GOALS.md`, `BACKLOG-2026-09-07.md` sections 0-7 and the newest entries, `STATUS.md` open claims (none), and pulled GitHub issues fresh: 30 open, all `decision`/`blocked-on-art`, none from Phil. Ran `preflight.py --skip-tests` fresh in the background and watched it to real completion rather than cite a prior run: 0 FAIL through every gate reached, genuinely stalled at `gate_etsy_pdfs_current` (confirmed by a flat `ps` CPU-time reading across a 5s window before killing), same standing network-credential limitation every cycle today has hit. `inbox_agent.py --apply`: no mail credentials in this sandbox, reported unchecked.

**Did the row-by-row read, not a ranking-strength synonym, for all three named rooms.** Garage's 5 `gap` rows (and several `partial` siblings) were a genuine cluster, not one-offs: "amazon shopping car organizer," "car organizer canadian tire," "how to organize car trunk suv," plus "car organizer with tissues," "car organizers for suv," "car organizers interior car accessories," "document/grocery/bag organizer for car," "organizers for car interior." Checked the Automotive Care Zone's own `content.json` purpose before concluding anything ("Keeps the fluids, cables, and cleaning kit for the cars you actually own upright, labeled, and separate from everything the household touches"): every one of those queries is about a retail product for inside the vehicle (a trunk or seat-back organizer) or a specific retailer's stock, a different physical space from the zone's own garage shelf, the identical "digital-context word overlap" shape `DIGITAL` already excludes for "hard drive," just a different mismatched context. No honest zone-name fix exists for noise, so this is an exclusion, not a synonym.

**Fixed at the regex, with the on-topic boundary checked against the real corpus before shipping.** Added `OFF_TOPIC_CONTEXT` to `ops/room_guide_candidates.py` (`\bcar organizers?\b|\bcar trunk\b|canadian tire|organizers?\s+(?:bag\s+)?for\s+car\b|organizers?\s+for\s+car\s+interior`), wired into both `room_guide_candidates.score_room()` and `room_guide_underperformance.score_room()` (which imports the same constant) alongside the existing `DIGITAL` filter. Verified against every real Automotive Care Zone row before and after: the genuine on-topic cluster ("organize car maintenance tips/guide/routine/checklist/overview/techniques/tools," "how to organize car cleaning/detailing/wash supplies," "organize in car interior," "car organization india," "how to organize your car") matches none of the new pattern's branches and stays counted; the noise cluster (11 rows across both harvests) is now excluded. Garage's reported gap count: 5 to 2.

**The two remaining Garage gaps checked and correctly left unfixed.** "how to organize raised garden beds" is about garden-bed layout and planting, not the Lawn and Garden Tool Zone's own stated job (storing tools so handles stay off the floor, chemicals latched away); the zone's content does not honestly support it. "how to organize soap making supplies" is an unrelated hobby query colliding with the Automotive Care Zone purely on the generic word "supplies"; nothing on this site answers it, and it is a single stray, not a cluster, so no new exclusion is warranted for it alone.

**Hall Closet's 2 gaps checked the same way, both correctly left unfixed.** "how to organize closet tutorial guide" routes to the room's own guide article (`site/articles/how-to-organize-a-linen-closet.html`), which genuinely answers the query in nine headings, but none contain the generic filler words "tutorial" or "guide," the exact A40 "plan" lesson recurring: adding either word to a heading would just as wrongly inflate every other room's "how to organize a {room} tutorial guide" query, so the real gap is the bag-of-words scorer's blindness to filler words, not missing content. "organize seasonal pricing model" is a B2B pricing-model query that has nothing to do with a household closet, colliding on "organize" + "seasonal" with the Seasonal and Guest Zone's own name; a single stray, no honest fix, no content on this site answers it.

**Kitchen's 1 gap checked and left unfixed, same reasoning as Pantry's identical shape (A-series precedent, section 2 A13/A14 area).** "kitchen organization ideas dollar tree" names a specific retailer; this site makes no claims about any named store's stock or prices (`CLAUDE.md` section 9/48), so no honest page can answer it by name, and it was already the correct call once before.

**Turned into a test, per `CLAUDE.md` 10b.** `ops/tests/test_room_guide_candidates.py` (now 9/9) and `ops/tests/test_room_guide_underperformance.py` (now 12/12) each gained two cases: one proving the noise row is excluded, one proving a genuine on-topic car-maintenance row is NOT caught by the same pattern. Fail-then-pass proved directly: `git stash` on both changed source files, reran both test files, watched the new "excluded" case fail exactly as expected (the on-topic-row case stayed passing, confirming the pattern itself, not the whole filter, was being tested), restored, reconfirmed 9/9 and 12/12.

**Verified.** `room_guide_underperformance.py --room "Garage"` reports 2 gap (was 5); full unscoped run across all 20 rooms shows no other room's gap/partial/covered counts changed (the pattern matches no query outside the automotive-car cluster). `fix_dashes.py --check` on all four changed files: 0 em dashes, 0 en dashes. `check_also_called_digital_collision_fast.py` and `check_risks_evidence_fast.py` both clean. A stray in-flight `ops/cycle-signal.json` checkpoint from the background preflight run was discarded (`git checkout --`), not committed, same precedent every prior cycle has recorded as safe. No price, product or page touched; `room_guide_candidates.py`/`room_guide_underperformance.py` are diagnostic tools, not `site/` generators, so no rebuild or `IndexNow` applies.

**Went well:** checking the real content and the real query intent for all five gap rows across three rooms before touching anything, per `CLAUDE.md` 5c/5d, which found one genuine fixable cluster and correctly declined to fabricate synonyms for the other four.

**Did not go well:** nothing new; the row-by-row discipline section 104 established held up cleanly on a second room.

**Changing next cycle:** nothing; the "verify before acting, check content.json before adding a synonym" discipline is already the standing rule, reconfirmed rather than revised.

**Next:** Hall Closet and Kitchen (now fully checked, no further unfixed gaps found) are closed for this lane; `room_guide_underperformance.py`'s unscoped run shows Workshop (2 gap), Pantry (2 gap, one Dollar Tree, same shape as Kitchen's), Primary Bedroom (4 gap), Family Room (3 gap) as the next-ranked rooms with any `gap` rows left, each needing the same row-by-row read. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil since 2026-11-01/02.

Pushed to main: `ops/room_guide_candidates.py`, `ops/room_guide_underperformance.py`, `ops/tests/test_room_guide_candidates.py`, `ops/tests/test_room_guide_underperformance.py`, this entry, dashboard files. No price, product or page touched; `IndexNow` not applicable.

## 104. Closed 2026-11-03, scheduled operator cycle: the "A37-shaped basement collision" sections 101-103 each named as the real next lever was checked directly, not re-cited, and does not hold up as described; a real but different gap found and fixed instead (Home Office "hard drive" digital noise)

**Verified the named claim before acting on it, per `CLAUDE.md` 5d.** Three consecutive entries (101, 102, 103) named "the 'outdoor storage' vs basement-article cross-page collision on Patio or Deck" as the real next lever, each time deferring it as bigger than that slot, without any of them calling the scorer directly against the real rows. Done this cycle: of the 9 "outdoor storage" queries in `ops/keyword-demand.json` plus 7 more in the global harvest, only ONE still has a genuine cross-page problem, "how to store clothes in outdoor storage" (both harvests), and it is a dead-even tie (0.75 heading-coverage each) between the real Patio or Deck Outdoor Storage Zone page and the basement article's unrelated FAQ ("What is the best way to store clothes in a basement?") plus its own "storage shelving" heading, not the one-sided misattribution the three prior entries described. Every other "outdoor storage" query in both harvests already resolves correctly to the Outdoor Storage Zone page (several fixed by sections 100-102's own "grilling zone"/cushions/snack-box work, which also reran the rescore this cycle's reading used).

**Checked whether the honest fix exists, and it does not.** The tie-break precedent (A31/A32/A40-A42) is to add the missing word only if the zone's own `content.json` purpose/done_looks_like genuinely supports it. This zone's real content is explicit: "two labeled totes beneath: games and covers," cushions, a croquet set, charcoal, furniture covers. Nowhere does it mention clothing, and the deck box's own described contents are patio accessories, not garments. Adding "clothes" to `zone-also-called.json` to win the tie would be the exact dishonest stretch `CLAUDE.md` section 6/8 forbids and A32's own "dinnerware" lesson warns against (a claim nobody searching for it actually makes about this page). **Correctly left unfixed, same precedent as Garage's car-organizer queries (section 102) and Workshop's paint queries**, not deferred as "bigger," because it the real size is one query this page cannot honestly answer.

**A real gap found instead, by the same `room_guide_underperformance.py` ranking sections 101-103 pointed at for Garage/Hall Closet/Home Office/Kitchen.** Home Office carried 2 true `gap` rows, "how to organize hard drive files" and "organizing hard drive files" (plus "organize hard drive space" elsewhere in the tier), all routing into Home Office's own File Storage zone or a nearby article purely on the words "organize"/"files"/"storage" overlapping a computer hard drive query, the identical digital-library-not-physical-zone shape `room_guide_candidates.py`'s own `DIGITAL` regex already excludes "pc"/"steam"/"computer"/"desktop" for. "Hard drive" was simply never added to that list. Added it (`ops/room_guide_candidates.py`, shared by `room_guide_underperformance.py`), confirmed it does not false-match a genuine physical query ("how to organize a hardware closet" still excluded correctly, i.e. still matches, since "hardware" is a different word from "hard drive" and the regex only blocks the two-word phrase). This regex is explicitly documented as safe to widen (a false exclusion there "costs nothing," per its own comment), unlike `preflight.py`'s separate, narrower, hard-failing `_DIGITAL_CONTEXT_WORD`, which was deliberately left untouched.

**Turned into a test, per `CLAUDE.md` 10b.** Added a case to `ops/tests/test_room_guide_underperformance.py` (now 10/10) asserting a "hard drive" query scores 0 on-topic rows. Fail-then-pass proved directly: stashed the regex change, reran the test file, watched the new case fail exactly as expected (`on_topic_rows` stayed 1), restored, reconfirmed 10/10.

**Verified.** `room_guide_underperformance.py --room "Home Office"` now reports 0 gap (was 2). `test_room_guide_candidates.py` (7/7, unaffected). `fix_dashes.py --check` 0/0. `check_also_called_digital_collision_fast.py` and `check_risks_evidence_fast.py` both clean. `preflight.py --skip-tests` run fresh in the background to real completion this cycle: 0 FAIL through every gate reached, genuinely stalled (confirmed by flat CPU over a 5s window) at the documented `gate_etsy_pdfs_current` network gate before being killed clean; the stray in-flight `ops/cycle-signal.json` checkpoint it left was discarded, same precedent as every prior cycle. No price, product or page touched; `ops/room_guide_candidates.py` is a diagnostic tool, not a `site/` generator, so no rebuild or `IndexNow` applies.

**Went well:** checking the actual rows behind a three-times-repeated claim before building around it, exactly `CLAUDE.md` 5c/5d, which avoided fabricating an honest-sounding synonym for a page that genuinely does not answer the query, and found a smaller, real, fixable defect in the same pass instead.

**Did not go well:** three prior cycles (101-103) spent their own "Next" lines re-citing an overstated claim without anyone calling the scorer directly; the actual mechanism (a tie-break, not a one-sided misattribution) was one `best_by()` call away the whole time.

**Changing next cycle:** when a backlog entry names a cross-page "collision" by field name (`heading_page`), call `keyword_demand.best_by()` directly against the real rows before sizing the fix or deferring it again; `best_page`/`heading_page`/`matched_on` interact (the true winning page is `best_page` only when `matched_on == "title"`, else `heading_page`), and reading only one field gives a wrong page for roughly half of partial/gap rows.

**Next:** Garage, Hall Closet and Kitchen remain next-ranked by `room_guide_underperformance.py` (Garage's own top candidates already ruled out, section 102); each needs the same row-by-row read this entry and section 102 both used, not a synonym added on the strength of the ranking alone. Otherwise unchanged: 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil since 2026-11-01/02 (confirmed again this cycle via the GitHub API, including issue #42's full comment thread, all self-authored by prior agent cycles).

Pushed to main: `ops/room_guide_candidates.py`, `ops/tests/test_room_guide_underperformance.py`, this entry, dashboard files. No price, product or page touched; `IndexNow` not applicable.

## 103. Closed 2026-11-03, scheduled operator cycle: a real CI FAIL from section 101's own fix, caught by `publish-image.yml` before it reached production, corrected rather than ignored

**The failure, confirmed before being treated as real, per `CLAUDE.md` 0.4.** Watched `checks.yml`/`publish-image.yml`/`deploy.yml` for section 101's push via a background monitor rather than assumed green. `publish-image.yml` run 41727990954 completed `failure` at its "Preflight, including generator ownership" step, the step that runs the full test suite this sandbox cannot (`gate_tests`, stalled here every cycle). Read the real log (`gh run view --job=... --log`), not a summary: `gate_also_called_no_digital_collision` FAILed, 2 gates failed total. `deploy.yml` never ran for this commit because the build never published; nothing section 101 shipped reached production in a broken state, confirmed directly rather than assumed, because the earlier bedroom-fix deploy (run 318) had already landed and this commit sat behind it, never promoted.

**The actual defect.** `gate_also_called_no_digital_collision` (built 2026-11-02, after an earlier cycle's own near-miss with "games") exists exactly because `zone_also_called_html()`'s heading is matched as a page-unscoped bag of words: a name added to fix one query can silently flip an unrelated query anywhere in the corpus if they share a word. Section 101's "grilling station" shared the word "station" with the unrelated digital-context query "desktop charging station organizer," a collision this sandbox's own local preflight runs never caught because they all used `--skip-tests` to route around the Chromium hang, and this specific check lives inside the full test suite, not the fast gate path. A real, if narrow, gap in this session's own verification discipline, not a false alarm.

**Fixed, not patched around.** Renamed the entry from "grilling station" to "grilling zone," the established `<word> zone` A-series naming precedent (A21/A23/A24/A32/A33/A34/A36) that exists for exactly this reason: it isolates the one missing content word without reusing a word already live in an unrelated digital query. Checked directly against the real gate function before shipping, not assumed: `check_also_called_no_digital_collision()` called live with the new name returns zero problems. `test_gate_also_called_no_digital_collision.py` (5/5) and `test_gate_zone_also_called_is_heading.py` (6/6) both pass against the real committed site.

**Verified.** `ops/keyword_demand.py --rescore`: "organize grilling station" still `covered` (`heading_coverage` 1.0, same page); the digital-context row "desktop charging station organizer" still routes to Family Room's charging zone, confirmed unaffected, not assumed. `fix_dashes.py --check` 0/0. `check_urls.py` 235/235. `audit_pages.py` 0 duplicates. `link_graph_report.py` 0 orphans. `affiliate.py --check` and `check_sellable.py` clean. `build_id.py --check` current.

**Went well:** watching the actual CI result for a push rather than treating "pushed" as "done" caught this before it reached production; the fix was already pointed at by the file's own precedent (A32's "dinnerware cabinet" lesson, the same shape) once the real cause was read.

**Did not go well, said plainly:** this session shipped a FAIL-worthy regression once this cycle, caught by CI rather than by this session's own local verification, because every local preflight run used `--skip-tests` to route around the documented Chromium hang, and `gate_also_called_no_digital_collision` lives inside that skipped suite. The fix shipped before production saw the bad version, which is the system working as designed, not luck, but the local verification gap is real.

**Changing next cycle:** when adding to `room-also-called.json` or `zone-also-called.json` specifically, run `check_also_called_no_digital_collision()` directly against the candidate name before shipping, the way this entry's fix did, rather than relying on `--skip-tests` preflight alone; that check is cheap (no Chromium, no network) and does not need the full suite to run standalone.

**Next:** unchanged from section 101: the A37-shaped basement collision on Patio or Deck's "outdoor storage" queries is the real next lever, then Garage/Hall Closet/Home Office/Kitchen by `room_guide_underperformance.py`'s ranking. 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil since 2026-11-01/02; no push notification, nothing material changed on that front.

Pushed to main: `ops/zone-also-called.json`, `build_zone_pages.py`-regenerated files, `ops/keyword-demand.json`, `ops/KEYWORD-DEMAND.md`, this entry, dashboard files. No price or product touched; no new page, so `IndexNow` does not apply.

## 102. Closed 2026-11-03, scheduled operator cycle: two more genuine gaps closed (Patio or Deck's Outdoor Seating Zone, Pantry's Snack and Lunch Zone), concurrent with section 101's grilling-station fix, and the Garage candidates section 100 named checked and ruled out

**Did, concurrent with section 101 above, discovered only when pushing.** Attached clean, ran `preflight.py --skip-tests` fresh in the background to real completion: 0 FAIL through every gate reached, 34 standing warnings. Rebased the resulting checkpoint commit onto four concurrent pushes (hourly check-in, deploy verdict, a PM check-in naming Patio or Deck, section 101's own grilling-station fix) and pushed clean. Independently, before seeing section 101, picked Patio or Deck off the same `room_guide_underperformance.py` ranking and the same PM handoff, and separately checked the Garage candidates section 100 had named ("car organizer," "raised garden beds," "soap making").

**The Garage candidates do not hold up.** Checked each against the Automotive Care Zone's real `content.json` content (fluid bottles, jumper cables, a drip tray, nothing about a vehicle's interior): "car organizer canadian tire," "car organizers for suv," "car organizers interior car accessories" and "car organizer with tissues" are all about an in-car storage product, the same word-overlap-on-"car" collision Workshop's "paint" queries already demonstrated for a different zone. The honest answer to the general "car organization and storage" intent already exists and is `covered`, matched on heading, at `more-storage-wont-fix-clutter.html`; adding a synonym to the Automotive Care Zone for the remaining long-tail variants would misroute a shopper to a page about garage-shelf fluid storage, not an in-car product. "How to organize raised garden beds" (plant layout, not tool storage) and "how to organize soap making supplies" (a craft hobby, tied to the zone only by a stray tie-break) are the same shape. Left all four unadded, the same call section 101's own larger "outdoor storage" collision and the 21:2x cycle's Workshop-paint call both already made.

**Two Patio or Deck rows held up, neither the one section 101 fixed.** Read every non-covered row for the room directly, both harvests: "how to store outdoor seating cushions" (US and global, `partial`, missing only "cushions") and "outdoor furniture seating storage" (US, `partial`, missing "furniture"), both already routed to `/zones/patio-or-deck-the-outdoor-seating-zone.html`, a genuine match, not a collision: that zone's own `content.json` purpose and passes repeatedly discuss cushions ("Seats people... with the cushions kept dry," "Cushions live in the deck box, not stacked on a seat," "one cushion per seat and none spare") as the zone's own real answer to where a chair's cushions go. Added "cushions zone" (the `<word> zone` precedent from the A-series) to a new `Patio or Deck|Outdoor Seating Zone` entry, a different zone from section 101's Grill and Outdoor Cooking fix, so no collision with that work.

**A second genuine gap, found along the way, not part of either handoff.** "build a snack box" and "fruit snack box organizer" (both `gap`, already routed to `/zones/pantry-the-snack-and-lunch-zone.html`, the room's only zone matching "snack") were missing only "box" from any heading; the literal phrase "snack box" already appears twice in that page's body copy. Added "snack box" to the zone's existing entry, alongside "snacks zone".

**Rebased onto section 101's own push before verifying, not merged by hand.** Both cycles edited `ops/zone-also-called.json`, `ops/keyword-demand.json` and the regenerated derived files (sitemap, build-id, dashboard trio) concurrently; a first rebase attempt hit conflicts across all of them because two independent `--rescore` runs and two independent `build_zone_pages.py` runs do not merge as text. Reset onto the fresh post-101 `main`, reapplied only the real source edit (the two `zone-also-called.json` entries) by hand, then regenerated every derived file fresh against that base rather than attempting a line-level merge of any of them, the same discipline section 5b names for generator-owned output.

**Verified, against the post-101 base.** `test_gate_zone_also_called_is_heading.py` (6/6, including section 101's own grilling-station heading, confirmed still intact). `ops/build_zone_pages.py` reran (self-chained). `ops/keyword_demand.py --rescore`: "build a snack box" and "fruit snack box organizer" moved `gap` to `partial`; "how to store outdoor seating cushions" moved `partial` to `covered` (US and global both); US gap count 118 to 116, global unchanged at 97 (partial-to-covered only), both confirmed against the real rows. `check_urls.py` (235/235), `audit_pages.py` (0 duplicates), `fix_dashes.py --check` (0/0), `affiliate.py --check` (165 documents), `check_sellable.py` (124/126, unchanged), `link_graph_report.py` (0 orphans) all clean. `ops/audit_visual.py` scoped to both changed pages as separate positional arguments (desktop and mobile), 0 findings each.

**Went well:** resetting to the fresh post-rebase `main` and reapplying the one real source edit by hand, rather than trying to text-merge two concurrent rescorings and rebuilds, avoided shipping a corrupted or half-merged derived file.

**Did not go well:** the first rebase attempt cost real time discovering that derived-file conflicts from two concurrent `--rescore`/`build_zone_pages.py` runs cannot be resolved as text; worth remembering for the next concurrent collision on these same files.

**Next:** section 101's named follow-on (the "outdoor storage" vs basement-article cross-page collision, A37-shaped) is the strongest remaining Patio or Deck lead; Garage, Hall Closet, Home Office and Kitchen remain the next-ranked rooms by `room_guide_underperformance.py`, and Garage's own remaining rows need the same scrutiny this cycle applied, not an assumption that a high ranking means a real gap. The real lever otherwise stays Phil-gated: 30 open `decision`/`blocked-on-art` issues, none from him since 2026-11-01/02.

Pushed to main: `ops/zone-also-called.json`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, `ops/KEYWORD-DEMAND-GLOBAL.md`, `site/zones/pantry-the-snack-and-lunch-zone.html`, `site/zones/patio-or-deck-the-outdoor-seating-zone.html`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, `site/build-id.txt`, this entry, dashboard files. No price or product touched; two existing zone pages rewritten, no new page; `IndexNow` to submit on push.

## 101. Closed 2026-11-03, scheduled operator cycle: a second `room_guide_underperformance.py` finding, Patio or Deck's "grilling station" the exact-word-not-stem shape again

**Did, same cycle as section 100 above, continuing after production confirmed current for that fix** (deploy workflow's own build-id check matched live against repo, not assumed from a green run; verified directly via `gh run view --log` before starting anything else). A concurrent PM check-in (21:4x slot, `ops/NIGHTLY-LOG.md`) independently found and read this session's own work, confirmed it finished a fourth way, and deliberately queued Patio or Deck for "the operator" rather than duplicate it; picked that up rather than mining the gap tier blindly again.

**Checked before building, per `CLAUDE.md` 5c/5d.** `room_guide_underperformance.py --room "Patio or Deck"` showed 0 gap, 15 partial. Read the raw rows behind several of the 8 printed, not just the headline ratio: "building an outdoor storage box"/"diy outdoor storage box" are genuinely close already (unmatched word is the query's own gerund/acronym, not a real content gap); "how to store clothes in outdoor storage" and "how to organize outdoor storage shed" are the A37-shaped cross-page collision (their `heading_page` is `/articles/how-to-organize-a-basement.html`, a different page entirely, by coincidental word overlap, the same misattribution class A37 already fixed once for "utility room"), real but a bigger, riskier fix than this slot and worth naming rather than rushing. "Organize grilling station" was the one clean, same-page, single-word case: `best_page` and `heading_page` both already correctly point to `/zones/patio-or-deck-the-grill-and-outdoor-cooking-zone.html` (best_rank 1, the top query for this zone), held at `partial` (0.5 coverage) only because the page's own title says "grill station" and the scorer matches exact words, not stems: `unmatched_words: ["grilling"]`, the identical shape A34/A36/this cycle's own bedroom fix already corrected for other words. Checked the zone's own purpose text before adding: the grill, the fuel, the long-handled tools and the cooking surface are exactly what "grilling station" names.

**The fix.** Added `Patio or Deck|Grill and Outdoor Cooking Zone` to `ops/zone-also-called.json` with `"grilling station"`, the exact phrase searched and a real name people use for this kind of zone, following the established format and sourcing convention exactly (checked against the file's own `_rule`: a measured query, not already covered). Reran `ops/build_zone_pages.py` (self-chained: canonical links, PWA, sitemap, build-id, all regenerated together).

**Verified.** `test_gate_zone_also_called_is_heading.py`: 6/6, the new heading renders correctly on the real committed page. `ops/keyword_demand.py --rescore`: the query moves from `partial` (0.5 title coverage) to `covered` (`heading_coverage` 1.0, `matched_on: "heading"`, now the zone's own page), confirmed against the real row, not the summary line; US partial count 1278 to 1276, covered 1412 to 1414. `ops/keyword_demand_global.py --rescore`: unchanged (this query is US-tier only), nothing moved backward. `fix_dashes.py --check` 0/0. `check_urls.py` 235/235. `audit_pages.py`: 0 duplicate titles/descriptions. `link_graph_report.py`: 0 orphans. `affiliate.py --check` and `check_sellable.py` both clean, neither price nor product touched. `check_risks_evidence_fast.py` clean (no new form-bearing page). `build_id.py --check`: current, self-regenerated by `build_zone_pages.py`'s own run.

**Went well:** reading the actual rows behind a printed ratio, rather than the ratio alone, separated one clean fix from two real but larger, riskier ones (the basement cross-page collision) and two non-issues (gerund/acronym noise); naming the larger ones rather than attempting them in the time left was the honest call, not a shortcut.

**Did not go well:** the A37-shaped basement collision on "outdoor storage"/"outdoor storage shed" is real and now named explicitly rather than buried in a ratio; it needs the same careful cross-page read A37 did, not a quick synonym, and is sized for its own slot.

**Next:** the real, larger follow-on this tool surfaced: Patio or Deck's own "outdoor storage" queries are losing their heading-coverage comparison to the basement article by coincidental word overlap, the same shape as A37's "utility room"/laundry-room fix; worth a dedicated read before the next room on `room_guide_underperformance.py`'s own ranking (Garage, Hall Closet, Home Office, Kitchen, all 34 to 48 percent uncovered). Otherwise unchanged: 30 open `decision`/`blocked-on-art` GitHub issues, none from Phil since 2026-11-01/02; no push notification, nothing material changed.

Pushed to main: `ops/zone-also-called.json`, `ops/build_zone_pages.py`-regenerated zone/room pages and derived files (canonical links, sitemap, build-id), `ops/keyword-demand.json`, `ops/KEYWORD-DEMAND.md`, this entry, dashboard files. No price or product touched; no new page, so `IndexNow` does not apply.

## 100. Closed 2026-11-03, scheduled operator cycle: built the next-lever tool the 20:4x PM check-in named, now that the room-guide gap-filling lane is closed, and used it to close one real coverage gap

**Checked before building anything, per `CLAUDE.md` 5c/5d.** Unshallowed genuinely this time (watched the process reach real completion, `is-shallow-repository` false, not assumed from elapsed time), attached cleanly, rebased one trivial checkpoint commit onto a concurrent cycle's push rather than force anything. Independently re-verified the exhaustion claim rather than trusting the fifth confirmation: `room_guide_candidates.py` printed nothing (0 guide-less rooms), `cold_read_ledger.py --next` read 306 of 306 ledgered with 0 un-ledgered candidates, `ops/state.json` showed a fresh (not carried-forward) Stripe read still at 1 sale/$19 all time and $0 this month, 30 GitHub issues re-pulled sorted by `updated_at` descending showed nothing newer than 2026-11-01, and `inbox_agent.py --apply` again found no mail credential in this sandbox. All of it held.

**The named next lever, built rather than deferred a sixth time.** The 20:4x PM check-in's own handoff named a real, different question this repository had not yet answered with one method: `room_guide_candidates.py` only ever asked "does this room have a guide," and that is now true for all 20, so it goes silent. It never asked "how well does an already-shipped guide, plus its zone and deck pages, actually answer the real search demand that is on-topic for that room." Built `ops/room_guide_underperformance.py`: same matching rules as its sibling (`best_page` routing over the sparse `room` field, the on-topic/digital-context filters, the US-plus-global dedup guard that prevents a shared query counting twice), extended with one more route a room can answer through that the old tool never needed, its own guide article. Ranks every room by the share of its on-topic, routed demand that is still `gap` or `partial` rather than `covered`.

**Tested before trusting it.** `ops/tests/test_room_guide_underperformance.py`, 9 checks: the room list is derived live from `content.json`, not hand-copied; every guided room resolves a `guide_path` and an unguided one does not; the new guide-article route actually matches, the old deck/zone routes still do too, the dedup guard holds, off-topic and digital-context rows are still excluded, and the shortfall ratio is 0 when nothing is left uncovered. Fail-then-pass proved directly: reverting the guide-article match in `room_rows()` turned 3 of the 9 red, confirmed, then restored.

**Ran it, read the output rather than trusted the ranking, and verified the one candidate that held up.** Workshop ranked worst (61% uncovered) but its own top rows turned out to be a "paint" word-overlap collision, not real workshop demand: `/zones/workshop-the-finishing-and-chemical-zone.html`'s own `<title>` says "workshop paint and chemical storage," which pulls in craft-paint queries ("acrylic paint storage organizer") that have nothing to do with wood finish or house paint, the same false-attribution shape several A-series fixes already corrected for other words; left alone rather than built around, since fixing it honestly would need deciding whether this site serves craft-paint storage at all, not adding a synonym. Checked the actual top "gap" rows (true 0.0-coverage misses, a stronger signal than a partial match) across every room instead: most were autocomplete noise or stray verb-sense collisions ("how to paint a metal storage container" is about painting an object, not about paint storage), but Primary Bedroom's "organizing ideas for bedrooms" (US tier, rank 11, `gap`, `unmatched_words: ["bedrooms"]`) was a clean, verifiable miss, read directly against the raw JSON before acting on it: the room's guide article title says "bedroom" (singular), and the scorer matches exact words, not stems, the identical shape A34 (nappy/nappies) and A36 (craft/crafts) already fixed.

**The smallest honest fix, grounded in the page's own already-stated content.** `site/articles/how-to-declutter-a-bedroom.html` is hand-authored (no `ops/build_*.py` writes its body, confirmed before editing it). Added one new FAQ pair, "What are good organizing ideas for bedrooms beyond a quick declutter?", in both the visible `<h3>`/`<p>` and the matching `FAQPage` JSON-LD entry, word for word identical per this corpus's own convention. The answer names only zones the page already describes (nightstand, dresser top, drawers, closet) and invents no new claim or statistic.

**Verified.** Both JSON-LD blocks still parse (`json.loads`, direct, every block in the file). `fix_dashes.py --check`: 0/0. `gate_unsourced_stats()` called directly: clean. `ops/keyword_demand.py --rescore`: the target row moves from `gap` (0.0 coverage) to `covered` (`heading_coverage` 1.0, `matched_on: "heading"`), confirmed by reading the rescored row directly, not the summary line; site-wide US gap count 126 to 118. `ops/keyword_demand_global.py --rescore`: global gap count unchanged at 97 (this query is not tracked there), covered count up by 2 from incidental page-content rescoring elsewhere, nothing moved backward. `check_urls.py` (235/235), `audit_pages.py` (240 pages, 0 findings, 0 duplicates), `link_graph_report.py` (0 orphans), `affiliate.py --check` (165 documents, no link on this page), `check_sellable.py` (124/126, unchanged) all clean, neither price nor product touched. `check_risks_evidence_fast.py` clean (no new form-bearing page, `forms_dead` unchanged). `cold_read_ledger.py --add` recorded the new tool as reviewed and clean (test files are deliberately excluded from the ledger by its own design, read together with the module they test). `preflight.py --skip-tests` re-run fresh after every change: 0 FAIL through every gate reached, same standing warnings (the two living-docs size tripwires, CI-conclusion-unreachable, build-id staged-changes notice while mid-edit), stalled again at the documented `gate_etsy_pdfs_current` network gate, confirmed genuinely stalled by flat CPU time rather than assumed, killed clean.

**Went well:** verified the ranking tool's own top candidate before building around it, and the honest answer was "this one is a false positive, leave it," which is as real a result as a fix; the second candidate held up under the same scrutiny and shipped clean.

**Did not go well:** nothing new; the Workshop paint-title collision is a real, if small, defect worth naming for whoever revisits that zone's title, but rewriting it was out of scope for this slot (it is accurate for its actual subject, not broken).

**Next:** the new tool now gives every future cycle a one-command answer to "which room's guide most needs attention" instead of a fresh ad hoc read each time, the same job `room_guide_candidates.py` did for "which room needs a guide at all." Patio or Deck, Garage, Hall Closet, Home Office and Kitchen are the next-ranked candidates by the same measure (34 to 56 percent uncovered); several of their own gap/partial rows looked genuinely on-topic (car-trunk and car-organizer queries for Garage's Automotive Care Zone, a snack-box query for Pantry) and are worth reading closely, not mined blindly, the next time this lane is picked up. The real lever otherwise stays Phil-gated: 30 open `decision`/`blocked-on-art` issues, none from him since 2026-11-01/02.

Pushed to main: `ops/room_guide_underperformance.py`, `ops/tests/test_room_guide_underperformance.py`, `site/articles/how-to-declutter-a-bedroom.html`, `ops/keyword-demand.json`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND.md`, `ops/KEYWORD-DEMAND-GLOBAL.md`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price or product touched; no new page, so `IndexNow` does not apply.

## 99. Closed 2026-11-03, scheduled operator cycle: checked the three OWNER-ACTIONS.md sections the 19:4x PM check-in named for further trimming, and found none of them safe to cut this cycle

The 19:4x PM check-in handed off a specific next step: read item 1's OAuth steps, item 1b's Gemini cost table and item 4's Amazon policy table for the same correction-stacking shape section 91 already cleared six paragraphs of, since `OWNER-ACTIONS.md` (115,514 bytes) is still over its 110,000-byte warn-level tripwire.

**Read all three in full before touching anything, per `CLAUDE.md` 5c/5d, rather than pattern-match on a "Corrected"/"Superseded" marker the way a mechanical scan would.** Item 4 (affiliate applications) and item 1 (YouTube OAuth) are already tightly maintained: every superseded sub-paragraph in both already carries its own "Superseded/Closed, archived to `OWNER-ACTIONS-ARCHIVE.md`" pointer from earlier cycles, and the remaining prose in each is either a live, unresolved ask or context its own text explicitly says to keep ("worth keeping, because it is why the item changed"). Nothing in either item matched the shape section 91 cleared.

Item 1b (Gemini billing) looked more promising: a "Corrected 2026-09-30" paragraph re-derives a zone-hero-missing count that the table two paragraphs below it also states. Read closely rather than assumed redundant: the correction paragraph is the only place in the file that describes the actual mechanism (`build_zone_pages.py` now renders an honest SVG "no photograph yet" panel instead of shipping a blank slot), which the table does not carry. Deleting it would lose that fact, not just a repeated number. Checked the one candidate that looked like a stale citation instead: the 7-card list ("EE-002, EM-009, ES-007, ET-003, EU-002, EU-004, EU-009") against the live `ops/card-hero-verdicts.json` directly. **Still exactly those 7, still accurate.** Not a stale citation; nothing to correct or archive.

**Result: no bytes removed this cycle, and that is the honest outcome, not a non-finding.** All three sections the handoff named are either already clean or hold live, load-bearing content; the prior cycle's own caution ("several are already load-bearing live instructions, not correction stacking") held on direct inspection. Forcing a cut here risks exactly what section 91 was careful to avoid: deleting a fact Phil would otherwise rely on, in a document whose whole job is to be read for a decision. The tripwire stays a WARN, not a FAIL, and `gate_living_docs_total_size_tripwire` does not block anything.

**Verified:** `ops/rotate_owner_actions_item_history.py --check` (the mechanical rotator, newly landed since section 91) reports CLEAN, confirming there is no further automatable rotation left either. `preflight.py` run fresh to the documented `gate_tests` sandbox hang: 0 FAIL, 6 warn (all standing, documented). `cold_read_ledger.py --next`: 306 of 306, 0 stale. 30 GitHub issues re-pulled live: unchanged, all `decision`/`blocked-on-art`, issue #42's full thread re-read, no comment from Phil since 2026-11-02. `ops/state.json` re-measured by a concurrent session minutes earlier: still 1 sale all time, $19, $0 in the trailing 30 days. `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty. Deploy gap re-derived directly (`resolve_verdict_commit`/`deploy_gap_material_commits`): 0 commits undeployed.

**Went well:** verified a specific, checkable claim (the 7-card list) against the live JSON rather than assuming it was stale because it looked old, the same discipline `CLAUDE.md` 5d asks for; avoided a plausible-looking edit that would have quietly deleted the one description of a real feature.

**Did not go well:** nothing new; the structured queue (room guides, cold-read ledger, backlog sections 2-6) remains fully exhausted, confirmed independently rather than cited from the log.

**Changing next cycle:** none. If a future cycle wants `OWNER-ACTIONS.md` fully under its tripwire, the honest next step is still the one section 91 already named: either a dedicated per-item correction-stacking rotator (needs very careful per-item scoping, not a generic pattern), or raising the ceiling for a file whose job is to carry a live, Phil-facing history.

**Next:** every non-Phil-gated lane is exhausted and independently reconfirmed; the real next motion is one of the 30 open `decision`/`blocked-on-art` GitHub issues, or new evidence (a Phil reply, a second sale, a fresh traffic read).

Pushed to main: this entry, dashboard files. No content, price or product touched; no file other than this one and the dashboard trio changed.

## 98. Closed 2026-11-03, scheduled operator cycle: a step-by-step stair landing guide, the last guide-less room

**Did.** Unshallowed and attached to main cleanly. Read `BACKLOG-2026-09-07.md`, `BACKLOG-2026-H2.md`'s process rules, `ROADMAP-2026-2029.md`, `CLAUDE.md`, and the last several `ops/NIGHTLY-LOG.md` entries. `python ops/preflight.py` (the full, non-`--skip-tests` gate per STEP 2) surfaced a real `FAIL ci-conclusion-current`: `checks.yml`'s most recent completed run on commit `13cb6a2c8e` had FAILED. Pulled the job logs directly via the GitHub API rather than trust the summary: both `checks.yml` run 2925/2926 and `publish-image.yml` run 706 failed at the same `Preflight` step, root cause `test_gate_keyword_demand_global_rescored_current.py`, because `ops/keyword-demand-global.json` was scored 5+ real `site/`-touching commits stale, so the dining room guide (item 97) was sitting pushed but genuinely unpublished. Began diagnosing the fix (`python ops/keyword_demand_global.py --rescore`); mid-diagnosis, a concurrent PM 17:4x cycle pushed the identical fix first (commit `69080a3d2`) and re-triggered `publish-image.yml` by `workflow_dispatch`. Re-fetched, found the fix already landed, and verified it directly rather than duplicate it: `ops/tests/test_gate_keyword_demand_global_rescored_current.py` and its US sibling both pass clean against the real committed file. Rescored the US file too (`ops/keyword_demand.py --rescore`, 0 commits stale at that point) as a small supplementary freshness improvement, not a second fix of the same defect.

**Claimed before starting, per `STATUS.md` section 0.** Added an open-claims line for the Stair Landing room guide before writing anything, since the 17:4x PM cycle's own handoff named it the only remaining non-Phil-gated lever and several concurrent sessions were shipping room guides the same hour.

**Picked per the ordering rule.** `ops/room_guide_candidates.py` re-run fresh confirmed Stair Landing as the only remaining guide-less room (0 on-topic gap, 3 partial, 4 on-topic of 25 routed rows). 30 open GitHub issues, unchanged, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02.

**Built following the room's own explicit tip, not the hub's listed order.** `content.json`'s "Where to start" tip for this room says to do the Stair and Floor Path zone first, "even though it looks like the least cluttered," because clearing the treads and fixing the lighting sets the real limit on what the console and the wall are allowed to hold, the opposite of the hub's display order (Console, Wall, Stair/Floor). Followed the tip rather than the display order, the same precedent the entryway guide (item 95) set when its own tip reordered the zones. Shipped `site/articles/how-to-organize-a-stair-landing.html` (2,354 words), grounded in all three zones' real `purpose`/`passes`/`the_call`/`watch_for`/`capacity` fields: the runner that has already lifted once, the going-upstairs-anyway pile, and the heavy mirror you would rather not touch, nothing invented. Summed the three session ranges by hand (75 to 120 minutes, 30+15+30 to 45+30+45) and phrased it "about one hour fifteen minutes to two hours" to match this site's established phrasing convention.

**Wired and verified.** `ROOM_GUIDES` in `ops/build_zone_pages.py` (also regenerates `site/rooms/stair-landing.html`'s Related Reading link and `site/sitemap.xml`, 235 URLs), the articles index card and JSON-LD `ItemList` entry, `llms.txt` (55 to 56 articles, feed count 53 to 54 of 56), the feed (`ops/build_feed.py`, 54 entries), a real generated share card (`ops/share_cards.py`, 1 drawn, 0 failed, `--wire` confirmed 0 changes needed since the og:image URL was already correct), and reciprocal links into two existing topic articles: `why-is-my-house-always-messy.html` (generator-owned by `ops/build_messy_article.py`, edited in the generator's source and rebuilt, not hand-edited in the output) and `tidy-is-not-the-same-as-safe.html` (hand-written, edited directly), the latter chosen for the frame push-and-pull test and the zero-capacity tread finding rather than the generic pair alone.

**`forms_dead` and the page-count citation updated before push, not left for the next cycle.** The new footer form moved the live tree's count from 239 to 240 (`preflight.tree_derived_state()` called directly, not read off a snapshot); `RISKS.md`'s RISK-0012 citation updated to match and re-verified with `ops/check_risks_evidence_fast.py`, clean (it had passed leniently against the stale `ops/state.json` snapshot even before the fix, the exact "unchecked is not passing" trap that script's own docstring names, so the live citation was corrected anyway rather than relying on the lenient pass). `ROADMAP-2026-2029.md`'s headline and narrative chain updated 239 to 240 with a new "Then 240" entry; verified by calling `gate_roadmap_catalogue_count_current()` and `gate_roadmap_prices_current()` directly, no exception.

**Verified.** `fix_dashes.py --check` 0/0. `audit_pages.py` 240 pages, 0 findings. `check_urls.py` 235/235. `link_graph_report.py`: 56 articles, 0 orphans, min 2 inbound links. `affiliate.py --check` and `check_sellable.py` both clean; neither price nor product touched (the Stair Landing Pack's existing $9 Stripe link, `RP-STAIR-LAND`, was only read). Ran every directly-relevant gate function by name against the live tree (`gate_llms_txt_current`, `gate_feed_current`, `gate_sitemap_urls`/`_complete`, `gate_articles_room_zone_counts_current`, `gate_stair_landing_deck_rendered`, `gate_room_hub_current`, `gate_unsourced_stats`, `gate_payment_links_nofollow`, `gate_breadcrumbs_current`, `gate_indexable_pages_have_schema`, and others): all clean. `preflight.py --skip-tests` re-run fresh: 0 FAIL through every gate reached, stopped at the documented `gate_etsy_pdfs_current` network stall, reported unchecked past that point per CLAUDE.md 0.4; no stray probe files left behind by the kill (checked `git status` directly). `audit_visual.py` not run this cycle (no headless-Chromium egress in this sandbox, the documented gap); reported unchecked, not assumed clean.

**All 20 rooms now have a step-by-step article.** This closes the room-guide lane opened in item 90 (Guest Bathroom) and continued through items 91-97; no further guide-less room remains on `room_guide_candidates.py`'s own count. The next traffic-epic lever, if this one is picked up again, is improving an existing guide against real search demand rather than filling a gap, since no gap is left to fill.

**Went well:** caught a real, currently-failing CI gate before building on top of it, diagnosed it to the exact root cause via the GitHub API rather than the preflight summary alone, and verified a concurrent session's fix directly instead of either duplicating it or blindly trusting it.

**Did not go well:** `checks.yml` run 2927 and the `publish-image.yml` workflow_dispatch re-trigger (both on commit `69080a3d2`) were still `in_progress` after 15+ minutes when this cycle needed to move on; named as unverified rather than assumed clean, per CLAUDE.md 0.4.

**Changing next cycle:** none; the staleness class this cycle hit already has a gate and a test (`gate_keyword_demand_global_rescored_current`), which is exactly why it was caught rather than silently shipping broken. The open question is cadence, not coverage: at this shipping velocity (multiple room-guide-sized `site/`-touching commits per hour from concurrent cycles), the 5-commit staleness threshold trips routinely; worth watching whether it recurs enough to justify a `--rescore` step inside the room-guide shipping path itself rather than a separate fix each time.

**Next:** confirm `checks.yml` run 2927 and `publish-image.yml` run 707 actually went green on `69080a3d2` before trusting production is current; no non-Phil-gated room-guide work remains, so the next cycle's real lever is the same 30 open `decision`/`blocked-on-art` GitHub issues every recent cycle has already surfaced, or re-checking an existing guide against fresh keyword demand.

Pushed to main: the new article and its wiring (`ops/build_zone_pages.py`, `ops/build_messy_article.py` and its regenerated output, `site/rooms/stair-landing.html`, `site/articles/index.html`, `tidy-is-not-the-same-as-safe.html`, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, the new share card, `ops/share-cards.json`, `RISKS.md`, `ROADMAP-2026-2029.md`), the US keyword-demand rescore, `BACKLOG-2026-09-07.md`, `STATUS.md`'s open claim (released below), dashboard files, this entry. No price or product changed. `ops/indexnow.py --submit` to follow since this is a new page.

## 97. Closed 2026-11-03, scheduled operator cycle: a step-by-step dining room guide, the stronger of the two remaining guide-less rooms

**Did.** Attached clean: checkout arrived shallow and detached, unshallowed, `checkout -B main origin/main`, ff-only onto `d56dffa89`, tree clean. Read `BACKLOG-2026-09-07.md`, `BACKLOG-2026-H2.md`'s process rules, `ROADMAP-2026-2029.md`, `CLAUDE.md`, the last several `ops/NIGHTLY-LOG.md` entries, and 30 live GitHub issues (unchanged, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02). Per the ordering rule, picked the highest non-Phil-gated item in epic 3: `ops/room_guide_candidates.py` re-run fresh named Dining Room the stronger of the two remaining guide-less rooms (0 on-topic gap, 6 partial, 25 on-topic of 98 routed rows, ahead of Stair Landing's 3 partial of 25), the same 0-gap-but-shipped-anyway case five prior room guides already set precedent for.

**Built around the room's own data, in the room hub's own already-shipped order.** `content.json`'s "Where to start" tip names the Dining Table as the quickest zone, and the room hub (`site/rooms/dining-room.html`) sequences the room in exactly that order already: Dining Table, Sideboard Surface, Sideboard Storage, China or Display Cabinet, Beverage or Coffee Station. Followed that order rather than re-deriving one, the same discipline the guest bedroom guide's own entry (96) named. Shipped `site/articles/how-to-organize-a-dining-room.html` (3,242 words), grounded in all five zones' real `purpose`/`passes`/`the_call`/`watch_for`/`leave_behind` fields: the person who has made the table a desk, the taped-run measurement test for the sideboard surface, the tablecloth-measuring test for storage, the grandmother's china settled by actual hosting history rather than guilt, and the second-coffee-machine test, nothing invented. Summed the five session ranges by hand (165 to 270 minutes, 30+15+45+45+30 to 45+30+75+75+45) and phrased it "two and three quarter to four and a half hours" to match this site's own established phrasing convention for that exact span.

**Caught before shipping, not after.** The meta description (169 characters) tripped `audit_pages.py`'s 160-character `desc-long` check on the first `--skip-tests` preflight pass; shortened to 153 characters across the meta description, og:description, twitter:description and the Article JSON-LD's own description field, then re-verified clean and re-ran `ops/share_cards.py` so the manifest and the rendered card picked up the corrected text rather than drawing a card off stale copy.

**Two real stray files, found and removed, not shipped.** The full `preflight.py` run (no `--skip-tests`) genuinely hung at `test_contact_form_interactive.py` (confirmed by elapsed time climbing with flat CPU across two checks, not assumed from one slow reading), killed after 11+ minutes with no progress. The kill left `site/_contact_form_interactive_probe.html` on disk, which `audit_pages.py` then correctly flagged (no lang, no title, no description, no h1, no analytics) as a genuine finding on a genuine stray file, not a false positive. Separately, a misdirected `audit_visual.py --help` call (the script takes no such flag, and an unrecognized flag falls through to probing every page on the site rather than erroring) was killed mid-run and left `site/rooms/_visual_probe.html` on disk, which `link_graph_report.py` then correctly counted as a 21st "room page" with 0 inbound and 0 outbound links. Both deleted (untracked, never committed), and `audit_pages.py`/`link_graph_report.py` both re-ran clean afterward, rather than widening either gate to tolerate them.

**Wired and verified.** `ROOM_GUIDES` in `ops/build_zone_pages.py`, the articles index card and JSON-LD `hasPart`, `llms.txt` (54 to 55 articles), the feed (53 entries), the sitemap (234 URLs, regenerated by `build_zone_pages.py` and `build_seo.py`), a real generated share card (`ops/share_cards.py`, 1 drawn, 0 failed), and reciprocal links into two existing topic articles: `why-is-my-house-always-messy.html` (generator-owned by `ops/build_messy_article.py`, edited in the generator's own source and rebuilt, not hand-edited in the output, the exact CLAUDE.md 5b trap; caught before it compounded, reverted the first hand edit and redid it in the right file) and `tidy-is-not-the-same-as-safe.html` (hand-written, edited directly), chosen for the china cabinet's own tip-over and lead-glaze findings rather than the generic safety/messy pair alone. While editing the messy-article hub also found and fixed a real gap: the guest bedroom guide (item 96) was never actually added to its own two-reciprocal-link promise there, confirmed by a direct grep returning zero matches; added it in the same pass rather than leave a second room guide silently missing from that hub.

**`forms_dead` citation updated before push, not left for the next cycle to catch.** This guide's new footer form moved the live tree's count from 238 to 239, computed directly (`sum of 'onsubmit="return false"' occurrences across site/**/*.html`), not read off a possibly-stale snapshot; updated `RISKS.md`'s RISK-0012 citation to match and re-verified with `ops/check_risks_evidence_fast.py`, clean. `ROADMAP-2026-2029.md`'s own page-count headline and narrative chain updated the same way, 238 to 239, with a new "Then 239" entry appended rather than the headline rewritten in isolation, the identical drift class three same-day cycles already fixed for this file; verified by calling `gate_roadmap_prices_current()` directly, no exception.

**Verified.** `fix_dashes.py --check` 0/0. `audit_pages.py` 239 pages, 0 findings. `check_urls.py` 234/234. `link_graph_report.py`: 55 articles, 0 orphans, min 2 inbound links. `affiliate.py --check` and `check_sellable.py` both clean; neither price nor product touched (the Dining Room Pack's existing $9 Stripe link, `RP-DINING-ROO`, was only read). `audit_visual.py`, scoped to the new page, desktop and mobile viewports, 0 findings each. `preflight.py --skip-tests` re-run fresh after all edits: 0 FAIL through every gate reached, stopped at the documented `gate_etsy_pdfs_current` network stall, reported unchecked past that point per CLAUDE.md 0.4.

**Went well:** caught the generator-ownership trap on the messy-article hub before it shipped, and turned a verification pass into a second real fix (the guest bedroom hub gap) rather than stopping at the one planned change.

**Did not go well:** the full test suite genuinely hung on a new gate (`test_contact_form_interactive.py`) not previously named in this log as a hang point; worth watching whether it recurs.

**Changing next cycle:** none; the stray-probe-file risk from a killed test run is already covered by `audit_pages.py` catching it, not a new gate.

**Next:** one guide-less room remains, Stair Landing (3 partial of 25 on-topic rows), weaker than every room shipped so far. The real lever stays Phil-gated: 30 open `decision`/`blocked-on-art` issues, none from him since 2026-11-02.

Pushed to main: the new article and its wiring (`ops/build_zone_pages.py`, `ops/build_messy_article.py` and its regenerated output, `site/rooms/dining-room.html`, `site/articles/index.html`, `tidy-is-not-the-same-as-safe.html`, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, the new share card, `ops/share-cards.json`, `RISKS.md`, `ROADMAP-2026-2029.md`), `BACKLOG-2026-09-07.md`, dashboard files, this entry. No price or product changed. `ops/indexnow.py --submit` to follow since this is a new page.

## 96. Closed 2026-11-03, scheduled operator cycle: a step-by-step guest bedroom guide, the strongest of the three remaining guide-less rooms

**Did.** Attached clean (fetch, `fetch --unshallow` 742 commits, `checkout -B main origin/main`, ff-only onto `10cee3d42`). Read `BACKLOG-2026-09-07.md`, `ROADMAP-2026-2029.md`, `CLAUDE.md`, the last several `ops/NIGHTLY-LOG.md` entries, and 30 live GitHub issues (unchanged, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02). `preflight.py --skip-tests` fresh: 0 FAIL through every gate before the documented `gate_etsy_pdfs_current` network stall. Per the ordering rule, picked the highest non-Phil-gated item in epic 3: `ops/room_guide_candidates.py` re-run fresh named Guest Bedroom the strongest of the three remaining guide-less rooms (0 gap, 11 partial, 30 on-topic of 93 routed rows), ahead of Dining Room and Stair Landing, the same 0-gap-but-shipped-anyway case Guest Bathroom, Patio or Deck and Entryway already set precedent for. Checked three on-topic rows before trusting them (CLAUDE.md 5c/5d): "how to organize truck bed", "how to organize paper files at work" and "how to organize backpack for work" all route to this room's pages by word overlap alone (a truck's bed, an office desk) and are not real guest bedroom demand; excluded, not used.

**Built around the room's own data, in the room hub's own already-shipped order.** The room's "Where to start" tip in `content.json` says open the closet first as a diagnostic move, but the room hub (`site/rooms/guest-bedroom.html`) and the zone pages themselves sequence the room Bed and Linens, Nightstand, Dresser, Closet, Welcome and Work Surface; followed that order rather than the tip's, since contradicting the room hub's own published sequence would be the "copy and a control disagree" trust defect CLAUDE.md step 6 names, and opened instead with why the bed comes first for a step-by-step guide (a visitor needs it even if the session runs out of time). Shipped `site/articles/how-to-organize-a-guest-bedroom.html` (2,968 words), grounded in all five zones' real `purpose`/`passes`/`the_call`/`watch_for`/`capacity` fields, nothing invented. Pulled the room's real total hours from the already-shipped room hub page itself ("about 3 to 4.5 hours") rather than summing the five session ranges by hand, since `ops/build_zone_pages.room_time()` rounds that figure by its own rule and a hand sum would have silently disagreed with the page already live.

**Caught before shipping, not after.** Checked the draft against `gate_unsourced_stats`'s own CLAIMY/STAT regexes by hand before the first preflight run, specifically for "up to" near a time range, the exact false positive the entryway guide's own cycle hit; none found. The meta description (164 characters) tripped `audit_pages.py`'s 160-character `desc-long` check; shortened to 144 and re-verified clean.

**Wired and verified.** `ROOM_GUIDES` in `ops/build_zone_pages.py`, the articles index card and JSON-LD `hasPart`, `llms.txt` (53 to 54 articles), the feed (52 entries), the sitemap (233 URLs, regenerated by `build_zone_pages.py` and `build_seo.py`), a real generated share card (`ops/share_cards.py`, 1 drawn, 0 failed), `site/rooms/guest-bedroom.html`'s Related Reading (regenerated by the generator, not hand-edited), and two reciprocal Keep Reading links into existing topic articles (`sentimental-items-without-guilt.html` for the sealed closet box, `more-storage-wont-fix-clutter.html` for the dresser overflow) rather than the generic safety/messy pair, since both are more topically relevant. `fix_dashes.py --check` 0/0. `audit_pages.py` 238 pages, 0 findings. `check_urls.py` 233/233. `link_graph_report.py`: 54 articles, 0 orphans, min 2 inbound links. `affiliate.py --check` and `check_sellable.py` both clean; neither price nor product touched (the Guest Bedroom Pack's existing $9 Stripe link, `RP-GUEST-BEDR`, was only read, not changed). `preflight.py --skip-tests` re-run fresh after all edits: 0 FAIL.

**The pre-push `check_risks_evidence_fast.py` gate (section 94) caught its own second real occurrence.** This guide's new form-bearing page moved the live tree's `forms_dead` from 237 to 238; `ops/state.json`'s own hourly snapshot had not caught up, so the gate's tree-first comparison passed by coincidentally matching the still-stale snapshot value (237) RISKS.md also cited, not because the citation was actually current. Fixed the citation to 238, the real tree value, before push rather than leave it to fail the moment the snapshot catches up, which is the gap the gate's own fallback-to-snapshot leniency can reopen.

**Went well.** Deriving the room's total-hours claim from the already-shipped room hub page, rather than re-summing the session ranges, avoided shipping a second page that silently disagreed with the first on the same fact.

**Did not go well:** nothing new; same standing `gate_etsy_pdfs_current` network stall and no-mail-credential gap every recent cycle has already logged.

**Changing next cycle:** none.

**Next:** two guide-less rooms remain (Dining Room, Stair Landing), both weaker than Guest Bedroom on every count `room_guide_candidates.py` tracks. The real lever stays Phil-gated: 30 open `decision`/`blocked-on-art` issues, none from him since 2026-11-02.

Pushed to main: the new article and its wiring (`ops/build_zone_pages.py`, `site/rooms/guest-bedroom.html`, `site/articles/index.html`, two reciprocal-link articles unchanged, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, `ops/sitemap-content-hashes.json`, the new share card, `ops/share-cards.json`, `RISKS.md`), `BACKLOG-2026-09-07.md`, dashboard files, this entry. No price or product changed. `ops/indexnow.py --submit` to follow since this is a new page.

## 95. Closed 2026-11-03, scheduled operator cycle: a step-by-step entryway guide, the strongest of the four remaining guide-less rooms

**Did.** Unshallowed and attached to main cleanly (the checkout arrived shallow and detached). Read `BACKLOG-2026-09-07.md`, `ROADMAP-2026-2029.md`, `CLAUDE.md`, and the last four `ops/NIGHTLY-LOG.md` entries before touching anything. Ran `preflight.py --skip-tests` fresh: 0 FAIL through every gate before the documented `gate_etsy_pdfs_current` network stall. Pulled all 30 GitHub issues live via the API: unchanged, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02T13:51Z; 0 open PRs. `inbox_agent.py --apply`: no mail credential in this sandbox, reported unchecked. Epics 1 and 2 (measurement, broken/dishonest) both came back clean; sections 2-6 of this file carry only C5/C6 unstruck, both explicit `YES, Phil`. Per the ordering rule, picked the highest non-Phil-gated item in epic 3 (traffic/distribution): `ops/room_guide_candidates.py` re-run fresh named Entryway the strongest of the four remaining guide-less rooms (0 on-topic gap, 15 partial, 38 on-topic of 121 routed rows), ahead of Dining Room, Guest Bedroom and Stair Landing, the same 0-gap-but-shipped-anyway case Guest Bathroom and Patio or Deck already set precedent for.

**Built around the room's own data, in the room's own documented order.** `mcp/content.json`'s Entryway intro and tips already name the real sequence ("Fix the zones first, the Door and Mat, the Landing Spot, the Coats, the Shoes, the Bench, so there is already a place for everything that comes through the door") and the real trap (buying more hooks and baskets before setting a cap). Shipped `site/articles/how-to-organize-an-entryway.html` (3,202 words) in that exact order, grounded in all five zones' real `purpose`/`passes`/`the_call`/`watch_for`/`capacity` fields, nothing invented. Checked three of the real on-topic rows before trusting them (CLAUDE.md 5c/5d): "how to organize a potting bench", "how to organize a reloading bench", and "how to organize drop down list in excel" all route to Entryway pages by word overlap alone and are not real entryway demand; excluded, not used, same discipline as Mudroom's own excluded gap row.

**Caught and fixed before shipping.** `gate_unsourced_stats` flagged "coats up to a bedroom...45 to 75 minutes" as an unsourced claim, "up to" sitting near a time range by coincidence of ordinary phrasing ("carrying ... up to a bedroom") rather than a saving being asserted. Reworded to "coats to a bedroom" and re-verified clean directly rather than widen the gate's own regex on one occurrence.

**Wired and verified.** `ROOM_GUIDES` in `ops/build_zone_pages.py`, the articles index card and JSON-LD `hasPart`, `llms.txt` (52 to 53 articles), the feed (51 entries), the sitemap (232 URLs), a real generated share card (`ops/share_cards.py`, 1 drawn, 0 failed), `site/rooms/entryway.html`'s Related Reading (regenerated by the generator, not hand-edited), and two reciprocal Keep Reading links into the room's own two existing topic articles (`why-you-always-lose-your-keys.html`, `why-mail-piles-up-by-the-door.html`) rather than the generic safety/messy pair every prior guide used, since both already existed and are more topically relevant than a generic pair. `fix_dashes.py --check` 0/0. `audit_pages.py` 237 pages, 0 findings. `check_urls.py` 232/232. `link_graph_report.py`: 53 articles, 0 orphans, min 2 inbound links. `affiliate.py --check` and `check_sellable.py` both clean; neither price nor product touched. `preflight.py --skip-tests` re-run fresh after all edits: 0 FAIL, `unsourced-stats` confirmed silent. `audit_visual.py` could not run: headless Chromium in this sandbox reaches for google.com, which the egress proxy refuses, the same documented hang class as `gate_tests`; reported unchecked, not assumed clean.

**Went well.** Using `content.json`'s own documented zone order, rather than inventing one, meant the guide's structure needed no judgment call. The word-overlap noise check caught three false "demand" rows before they were cited as evidence for picking this room.

**Did not go well:** the `gate_unsourced_stats` false positive on ordinary phrasing ("up to" as a preposition, not a quantity) cost a rework-and-reverify pass; not escalated to a gate change on one occurrence, per this file's own three-strikes bar, but worth watching if the same shape recurs on a future guide.

**The new pre-push gate from section 94 caught its own first real occurrence.** `ops/check_risks_evidence_fast.py` (built this same day, one cycle earlier) correctly FAILed before push: this guide's new form-bearing page moved `ops/state.json`'s `forms_dead` from 236 to 237, and RISKS.md's RISK-0012 evidence line still cited 236. Fixed the citation, re-ran the fast gate directly, confirmed clean, then pushed. Exactly the shape the gate was built to stop; the fact that it fired on its very next opportunity is the verification section 94 could not give itself.

**Changing next cycle:** none.

**Next:** three guide-less rooms remain (Dining Room, Guest Bedroom, Stair Landing), all weaker than Entryway on every count `room_guide_candidates.py` tracks. The real lever stays Phil-gated: 30 open `decision`/`blocked-on-art` issues, none from him since 2026-11-02.

Pushed to main: the new article and its wiring (`ops/build_zone_pages.py`, `ops/build_messy_article.py`, `site/rooms/entryway.html`, `site/articles/index.html`, two reciprocal-link articles, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, the new share card, `ops/share-cards.json`, `ROADMAP-2026-2029.md`), `BACKLOG-2026-09-07.md`, dashboard files, this entry. No price or product changed. `ops/indexnow.py --submit` to follow since this is a new page.

## 94. Closed 2026-11-03, scheduled operator cycle: a stuck publish-image chain confirmed cleared, and the recurring RISKS.md citation drift turned into a pre-push gate rather than re-reported a seventh time

**Did.** Unshallowed and attached to main cleanly, fast-forwarding through two concurrent cycles' own pushes while this one ran (the 13:4x PM check-in's `publish-image.yml` re-trigger, then its own deploy-verdict commit). Re-verified rather than cited: all 30 GitHub issues unchanged, all `decision`/`blocked-on-art`, every comment on #42 self-authored by a prior cycle, none from Phil since 2026-11-02; `ops/last-owner-notification.json`'s no-repeat-before of 2026-11-04T04:00Z still holds, so no push sent. `cold_read_ledger.py --stale`/`--next` and `room_guide_candidates.py` both re-ran fresh: 0/305 stale, all 4 remaining guide-less rooms still 0 on-topic gap, both lanes still genuinely exhausted. `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty.

**Found a real, live P0 before trusting "nothing left": production was behind on real content.** `deploy.yml` run 309 (11:04Z) had failed its post-deploy read; a later cycle's manual re-dispatch (run 310) confirmed production current at that time, but `publish-image.yml` run 702, for the commit carrying the mudroom guide, then failed on `gate_risks_evidence_current` (RISKS.md's `forms_dead=235` stale against the tree's 236), and because `publish-image.yml` only re-triggers on a `site/**`/`Dockerfile` push, no later dashboard-only commit (including the one that fixed the citation) ever re-fired it. Checked directly via the Actions API, not assumed: `checks.yml` run 2915 for the fix commit itself also failed, now on `gate_publish_image_current` ("real content changes sitting unpublished"), confirming the mudroom guide was built but not shipped to the image the host pulls. The 13:4x PM check-in cycle had independently found and begun fixing the same gap concurrently (manually re-dispatching `publish-image.yml`, run 703); watched it rather than duplicating the dispatch. Confirmed to completion: run 703 succeeded, `deploy.yml` run 312 fired automatically and succeeded, production confirmed current at build `03f8d72ec071ec89` by the workflow's own commit, not assumed from a green run alone.

**The repeat, not the incident, is what's worth fixing.** This exact shape, RISK-0012's `forms_dead=NNN` citation going stale the moment a page-shipping commit lands, has now recurred at least six times in one day alone (`ops/NIGHTLY-LOG.md`: 232 to 233, 233 to 234, 234 to 235, 235 to 236, each one caught only by CI). `gate_risks_evidence_current` in `preflight.py` already catches it correctly and leniently (tree-derived, since 2026-10-29), but it sits after `gate_tests` in `main()`'s own call order, so this sandbox's documented Chromium hang hides it from every local run that doesn't pass `--skip-tests`, the same shape `check_nightly_log_fast.py` already exists to solve for a different gate. Built `ops/check_risks_evidence_fast.py`, mirroring that script exactly: imports `preflight`, calls `gate_risks_evidence_current()` directly, skips `gate_tests` entirely, finishes in under a second. Wired into `.githooks/pre-push` alongside the existing nightly-log check, same python-candidate-must-prove-it-runs pattern, same refuse-with-instructions-rather-than-silently-fix convention.

**Verified.** `ops/tests/test_check_risks_evidence_fast.py`, a new test of the wrapper itself (the gate's own logic is already covered by `test_gate_risks_evidence_tree_derived.py`): fail-then-pass proved directly, 2/2, a citation matching neither the tree nor the snapshot fails, one matching either passes. `bash -n .githooks/pre-push` parses; running the hook directly against the real, current repo passes both checks silently. `fix_dashes.py --check` on both new files and the hook: 0/0. `python3 -c "import ast; ast.parse(...)"` on both new `.py` files before relying on them. `ops/dashboard.py` regenerated fresh (YELLOW, revenue carried forward, P0 9, need-you 28, commits7d 1437); `forms_dead` re-checked after regen, still 236, still matching RISKS.md, so this cycle's own dashboard run did not retrip the gate it just built. No price or product touched; no new site page, so `IndexNow` does not apply.

**Went well:** caught a real customer-facing gap (built content sitting unpublished) before assuming the backlog's own "nothing left" reading meant nothing was wrong, per `CLAUDE.md` 0.3; the fix was already in flight from a concurrent cycle, so this one verified rather than duplicated it, then spent the slot on the systemic version of the problem instead.

**Did not go well:** nothing new; the standing sandbox `gate_tests` hang is exactly the thing this cycle's own fix now routes around for one more gate.

**Changing next cycle:** none.

**Next:** the recurring-citation class should now cost one `git push --no-verify` decision instead of a full CI-fail-then-republish cycle, the next time a page ships without updating RISKS.md in the same commit; worth watching whether it actually prevents a seventh occurrence. Otherwise unchanged: room-guide and cold-read lanes both exhausted, 30 GitHub issues all Phil-gated, no reply since 2026-11-02.

Pushed to main: `ops/check_risks_evidence_fast.py`, `ops/tests/test_check_risks_evidence_fast.py`, `.githooks/pre-push`, dashboard files, this entry. No price or product touched, no new page, IndexNow not applicable.

## 93. Closed 2026-11-03, scheduled operator cycle: a step-by-step mudroom guide, the last room this session's own evidence actually supports

Re-ran `ops/room_guide_candidates.py` fresh rather than trust section 92's "5 rooms left" count: Mudroom scores 1 on-topic gap / 9 partial of 96 routed rows, still clearly ahead of the other 4 (Entryway 0/15/121, Guest Bedroom 0/11/93, Dining Room 0/6/98, Stair Landing 0/3/25). Checked the one "gap" row before trusting it, per `CLAUDE.md` 5c/5d: "organize outdoor diy lab" is an autocomplete garble of "how to organize outdoor dining" (already recorded as noise in `ROADMAP-2026-2029.md`'s 2026-10-29 entry, so this cycle did not re-derive that finding, only confirmed it still holds), not real Mudroom demand. The guide is built around the room's own six zones, not that row.

Grounded in the room's own `content.json`: the family hook zone first (its own tip says to start there, since almost everything else on the floor is only there because the wall ran out of room), then the bench and transition surface, shoe and boot storage, the pet station, seasonal outdoor gear and the cleaning and utility zone, the room's own session order. Every step, hazard and the-call in the guide (the hook pulling out of plasterboard, the flea treatment that must sit above reach, the bleach/ammonia caddy rule, the single vacuum test) is the room's own data, not invented.

Wired into `ROOM_GUIDES` (`ops/build_zone_pages.py`, regenerated: `site/rooms/mudroom.html` now links the guide, no zone pages changed, matching the Family Room precedent of touching only the room hub), the articles index card and JSON-LD `hasPart`, `llms.txt` (52 articles, 50 of 52 in the feed, both re-derived by running `ops/build_feed.py` directly), `ROADMAP-2026-2029.md`'s page-live count (235 to 236, plus a short note closing the loop on its own 2026-10-29 Mudroom-noise paragraph), two reciprocal Keep Reading links (`why-is-my-house-always-messy.html`, `tidy-is-not-the-same-as-safe.html`) and `build_messy_article.py`'s own Keep Reading list, and a real share card generated by `ops/share_cards.py`.

**Caught and fixed before shipping, not after:** the first draft's meta description ran 161 characters, 1 over `audit_pages.py`'s own 160-character `desc-long` threshold, caught by running the audit rather than trusting the draft; shortened to 155 characters in the meta tags, the JSON-LD `description`, the og/twitter tags and the articles-index card text, then re-ran `build_feed.py` and `build_seo.py` so the derived `feed.xml`/`sitemap.xml` summaries picked up the fix rather than carrying the stale one.

**Verified, not assumed:** `fix_dashes.py --check`: 0 em dashes, 0 en dashes. `audit_pages.py`: 236 pages, 0 findings, 0 duplicate titles/descriptions. `check_urls.py`: 231/231 sitemap URLs resolve. `link_graph_report.py`: 0 orphans across zones, rooms and articles (52 articles, min 2 inbound links). `affiliate.py --check` and `check_sellable.py` both clean, neither price nor product touched. `preflight.py` re-run fresh after the changes, twice: the first run's only `FAIL` was a stale share-card hash from the description fix above, fixed by rerunning `share_cards.py`; the second run reached `gate_tests` with 0 FAIL on every gate before it (one self-healing `stray-probe-files` cleanup each run, a leftover fixture from this same session killing an earlier hung `gate_tests` pass, not a site defect), the same standing sandbox limitation every recent cycle has hit.

**Next:** 4 rooms remain guide-less (Entryway, Dining Room, Guest Bedroom, Stair Landing), all at 0 on-topic gap on the current harvest and each weaker than every room guide shipped so far; the real lever stays Phil-gated: 30 open GitHub issues, none from him since 2026-11-02 (confirmed directly this cycle by reading issue #42's own comment history, every entry self-authored by a prior agent cycle). A push notification on that decision backlog went out 2026-11-02 with a stated no-repeat-before of 2026-11-04; nothing material has changed since, so none was sent this cycle.

Pushed to main: the new article, `ops/build_zone_pages.py`, `ops/build_messy_article.py`, `site/rooms/mudroom.html`, `site/articles/index.html`, two reciprocal-link articles, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, the new share card and `ops/share-cards.json`, `ROADMAP-2026-2029.md`, dashboard files, this entry. No price or product changed; `ops/indexnow.py --submit` to follow in the deploy step since this is a new page.

## 92. Closed 2026-11-03, scheduled operator cycle: a step-by-step family room guide, the strongest remaining room among the 6 still lacking one

Re-ran `ops/room_guide_candidates.py` fresh rather than trust the 2026-11-02 "7 guide-less rooms" count: Guest Bathroom and Primary Bathroom had already closed (sections 90 and 89 above), leaving 6. Family Room scored 4 on-topic gap / 30 partial of 221 routed rows, clearly ahead of Mudroom (1/9/96) and the other four (0 gap each). Read two of the four "gap" rows before trusting the count, per `CLAUDE.md` 5c/5d: "dental organization ideas" and "nightstands with hidden storage" are both autocomplete-seed artifacts ("den organization ideas" expanding to "dental"; "how to organize left nightstand" routing to the blanket zone), not real Family Room demand, so the guide was not built around them. "storage for video games" and "card games organizer storage" are genuine and land naturally in the media and game zones this room already has.

Grounded in the room's own `content.json`: media cabinet first (its own tips say so, the cables cross every other zone), then toy and play, board game and puzzle, blanket and comfort, charging and device, craft and activity, in the room's own session order. Every step, hazard and the-call in the guide is the room's own data, not invented.

Wired into `ROOM_GUIDES` (`ops/build_zone_pages.py`, regenerated: 20 room pages rewritten, `site/rooms/family-room.html` now links the guide), the articles index card and JSON-LD `hasPart`, `llms.txt` (51 articles, 49 of 51 in the feed, both counts re-derived by listing `site/articles/*.html` and running `ops/build_feed.py` directly rather than incremented by assumption), `ROADMAP-2026-2029.md`'s page-live count (234 to 235), two reciprocal Keep Reading links (`why-is-my-house-always-messy.html`, `tidy-is-not-the-same-as-safe.html`) and `build_messy_article.py`'s own Keep Reading list, and a real share card generated by `ops/share_cards.py` (not a placeholder).

**Verified, not assumed:** `fix_dashes.py --check` on every touched file, 0/0. `audit_pages.py`: 235 pages, 0 findings, 0 duplicate titles/descriptions. `check_urls.py`: 230/230 sitemap URLs resolve. `link_graph_report.py`: 0 orphans across zones, rooms and articles (51 articles, min 2 inbound links). `preflight.py` re-run fresh after the changes: 0 FAIL across every gate before the documented `gate_tests` sandbox hang (same standing limitation every recent cycle has hit), same 5 pre-existing warnings as before this change (CI conclusion unreachable, `OWNER-ACTIONS.md` size, build-id staged-changes notice, 2 dated disclosures, image-coverage sourcing note), none new.

**Next:** 5 rooms remain guide-less (Entryway, Dining Room, Guest Bedroom, Mudroom, Stair Landing), all at 0 on-topic gap on the current harvest; Mudroom (1 gap, 9 partial) is the next candidate if this lane is picked up again, otherwise the real lever stays Phil-gated: 30 open GitHub issues, none from him since 2026-11-02.

Pushed to main: the new article, `ops/build_zone_pages.py`, `ops/build_messy_article.py`, `site/rooms/family-room.html`, `site/articles/index.html`, two reciprocal-link articles, `site/llms.txt`, `site/feed.xml`, `site/sitemap.xml`, the new share card and `ops/share-cards.json`, `ROADMAP-2026-2029.md`, dashboard files, this entry. No price or product changed; `ops/indexnow.py --submit` to follow in the deploy step since this is a new page.

## 91. Closed 2026-11-03, scheduled operator cycle: closed part of the `OWNER-ACTIONS.md` size tripwire the 08:2x PM check-in named and deferred as "more than this slot"

**Checked before acting, per `CLAUDE.md` 5c/5d.** Confirmed first that the room-guide and global-tier lanes (sections 89/90 above) are genuinely exhausted and all 30 open GitHub issues remain `decision`/`blocked-on-art` with none from Phil since 2026-11-02, so epic 6 (operational honesty) is correctly next in the ordering rule. `OWNER-ACTIONS.md` was 122,670 bytes against its 110,000-byte tripwire; every existing rotator (`rotate_owner_actions.py`, `rotate_owner_actions_closed_items.py`, `rotate_owner_actions_gemini_billing.py`) reported CLEAN, confirming the 08:2x cycle's own finding that the remainder is live, open items whose own accumulated correction history outgrew the ceiling, not a rotation gap.

**Hand-read six candidates before touching any of them**, the same editorial pattern this file already used once (item 1b's deploy row, archived 2026-11-01): a sub-paragraph inside a still-open item that is itself fully resolved, superseded, or redundant with a canonical source elsewhere, verified individually rather than matched by a generic pattern (only 2 of 6 were machine-findable via a "Resolved/Closed" marker scan; the other 4 needed reading the item to see a paragraph had been overtaken by a later one in the same item, or by `GOALS.md`/`STATUS.md`, or by item 0's own closure). Archived, each with a one-line pointer in place and the verbatim original moved to `OWNER-ACTIONS-ARCHIVE.md`: (1) item 0's trailing 2026-09-29 404-measurement paragraph, justification for a now-closed item; (2) item 1's 2026-09-29 traffic snapshot, superseded by `GOALS.md`/`STATUS.md`'s own canonical, currently-maintained figures; (3) item 1's resolved Bluesky-drafting aside; (4) item 1's resolved edge-tts caption-batch paragraph; (5) item 4's "one thing gates all of it... 404 in production" paragraph, whose own deploy gap item 0 now records as closed (the live-content claim itself is unchecked from this sandbox, no egress to `6s-success.com`, flagged rather than deleted); (6) item 23's 2026-10-17 addendum narrative, independently re-confirmed word-for-word by the 2026-10-23 addendum that follows it, so only the superseded intermediate telling moved, the direct Routine-edit links kept live.

**Caught and fixed before shipping, not after.** A first pass left row 0's markdown table row missing its closing `|` (the replacement text dropped it), and a second left a double blank line where the item-1 traffic paragraph met the next one; both found by rereading the diff, not assumed correct from the edit call succeeding, and fixed before verification.

**Verified.** All 6 original substrings matched exactly once before replacement (scripted check, not eyeballed). `git diff` read in full: every live ask, number and link outside the six archived spans is untouched. The 3 existing rotators re-run, all still CLEAN. `fix_dashes.py --check` on both files: 0/0. `check_urls.py` 229/229. `audit_pages.py`: 0 duplicate titles/descriptions. `affiliate.py --check`: 165 documents clean. Called `gate_living_docs_total_size_tripwire`, `gate_owner_actions_closed_items_rotated`, `gate_owner_actions_items_tracked`, `gate_owner_actions_history_not_oversized`, `gate_owner_actions_preamble_not_oversized`, `gate_owner_actions_gemini_billing_not_oversized`, `gate_owner_actions_zone_art_citation_current` and `gate_owner_actions_retired_sku_count_current` directly: all clean. **One real FAIL caught by this same scan, not missed:** `gate_owner_actions_last_measured_current` failed because the file's "List reviewed" marker still read 2026-11-02 while this edit's own date is 2026-11-03; fixed in the same cycle, re-checked clean.

**Result: 122,670 to 118,214 bytes, a 4,456-byte reduction. The tripwire is not cleared** (still over 110,000) **and this is said plainly rather than rounded up to "fixed".** Six candidates is what a careful hand-read found safe to move without risking a live ask; the file's remaining size is genuinely live, open content, the same conclusion the 08:2x cycle reached. If a future cycle wants the tripwire fully clear, the honest next step named here is the same one section 87's pattern suggests: either a dedicated per-item correction-stacking rotator (higher risk, needs very careful scoping per item, not attempted this cycle because free-text judgment calls do not generalise safely the way the backlog's dated-row format did), or accepting a higher ceiling for a file whose own job is to carry a live, read, Phil-facing history rather than be pruned to the bone.

A separate, smaller thing closed in passing: `ops/cold_read_ledger.py --stale` named one real entry, `ops/rotate_backlog_closed.py` (ledgered 2026-11-01, touched again 2026-11-03 by the 08:0x cycle's retention-floor fix, already covered in that cycle's own commit). Read the diff cold: one constant changed (2 to 0 days) plus a docstring note, matches its own commit message, tests pass unmodified. No defect found; re-ledgered clean rather than left stale.

**Went well:** caught two real formatting mistakes (missing table pipe, doubled blank line) by rereading the diff before calling it done, and a real gate FAIL (stale review-date marker) by running the actual gate functions rather than assuming the edit was complete.

**Did not go well:** the tripwire is only partly closed; a free-text judgment call does not scale the way the backlog's dated-row rotators did, so this took a full cycle's hand-reading for six paragraphs.

**Next:** real next lever remains Phil-gated: 30 open GitHub issues, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02. If this lane is picked up again, read the remaining large sections (item 1's OAuth steps, item 1b's Gemini cost table, item 4's Amazon policy table) for the same shape before assuming more is safe to cut; several are already load-bearing live instructions, not correction stacking.

Pushed to main: `OWNER-ACTIONS.md`, `OWNER-ACTIONS-ARCHIVE.md`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price or product touched, no new page, IndexNow not applicable.

## 90. Closed 2026-11-03, scheduled operator cycle: verified and closed the one real candidate the 03:4x PM check-in named, the global tier's last on-topic gap row

**Checked before acting, per CLAUDE.md 5c/5d.** The prior check-in named "how to organise belongings" (rank 11, global gap, 0.0 coverage) as the one genuine on-topic miss left in 98 mostly-noise gap rows, but had not verified it against real content. Ran it live: `content_words()` already folds `organise` to `organize` (the 2026-10-23 fix) and deliberately excludes it as a task-verb `FORMAT_WORD`, so the only real content word is `belongings`, and it appeared on no page's title or heading at all. Confirmed the row was not stale scoring: live `best_page()`/`best_by()` against the real site both returned 0.0 for `/about.html`, matching the stored row exactly.

**The real gap, and the smallest honest fix.** "Belongings" is a whole-house synonym for the thing this entire product organizes, not a room- or zone-level term, so the right target is `where-to-start-decluttering.html`, the one article already about organizing a whole house rather than one room, hand-authored (confirmed no `ops/build_*.py` generator writes its body before editing it, only `build_articles.py`'s/`build_zone_pages.py`'s own "Keep reading" lists reference it). Added one genuine FAQ question in its existing voice, "How do I organize all my belongings, not just declutter them?", answered from the page's own already-stated method (a zone is not finished until everything staying in it has an assigned spot), in both the visible `<h3>`/`<p>` and the matching `FAQPage` JSON-LD entry. No invented claim, no new statistic, no price or product touched.

**Verified.** Re-ran the real scorer after the edit: `best_by(..., "head_words")` now returns 1.0/`covered` on `/articles/where-to-start-decluttering.html` (was 0.0/`gap` on `/about.html`). `python ops/keyword_demand_global.py --rescore`: gap 98 to 97, covered 1094 to 1095, partial unchanged, exactly the one row moving, confirmed by diffing `ops/keyword-demand-global.json` rather than trusting the summary line alone. The US tier (`ops/keyword-demand.json`) carries no "belongings" query, so nothing there to rescore. Both JSON-LD blocks on the page parse (`json.loads`, direct). `fix_dashes.py --check` and `fix_dialect.py --check` on the file: 0/0. `audit_pages.py` (234 pages, 0 findings), `check_urls.py` (229/229), `affiliate.py --check` (165 documents, no affiliate link on this page), `check_sellable.py` (124/126, unchanged) all clean. `gate_specific_article_direct_answer`, `gate_article_figures_current`, `gate_keyword_demand_rescored_current`, `gate_keyword_demand_global_rescored_current`, `gate_keyword_demand_not_stale` and `gate_keyword_demand_global_not_stale` called directly against the real files: all clean. `ops/indexnow.py --submit` correctly reported UNCHECKED (could not reach the live key file from this sandbox), not a false pass.

**A second, smaller thing closed in passing.** `ops/cold_read_ledger.py --stale` named one real entry, `ops/room_guide_candidates.py` ledgered 2026-11-02 but touched again 2026-11-03 (the `/deck/{slug}-print-and-play.html` fix, commit `7ea370b59`). Read the diff cold: matches its own commit message, fail-then-pass proved (7/7), already documented in section 89 above. No defect found; recorded clean rather than left stale for the next cycle to re-read.

**Went well:** the handoff's own candidate held up under verification, unlike several recent handoffs this repository's log has had to correct.

**Did not go well:** nothing new; the standing `gate_tests` sandbox Chromium hang (`test_audit_catalog.py`) recurred and was killed cleanly, same documented limit.

**Next:** the global tier now reads 97 gap rows, essentially all previously-named noise (CAD/cribbage/bench-press/daycare/vastu/pasta); no further on-topic candidate remains there. Guest Bedroom (11 partial) stays the only room-guide candidate and is still below the Workshop-class bar. Real next lever remains Phil-gated: 30 open GitHub issues, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02.

Pushed to main: `site/articles/where-to-start-decluttering.html`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND-GLOBAL.md`, `ops/cold-read-ledger.json`, `ops/cycle-signal.json`, this entry, dashboard files. No price or product touched, no new page, IndexNow attempted and correctly reported unchecked.

## 89. Closed 2026-11-03, scheduled operator cycle: a real blind spot in `room_guide_candidates.py` found while verifying a handoff, before shipping a guide the evidence did not actually support

**The handoff, checked before acting on it, not after.** The 05:4x PM check-in named Entryway as the next unblocked content item, citing "23 unmet rows... ties Mudroom... larger total demand (50 rows vs 43)". That count used the sparse `room` field on `ops/keyword-demand.json` rows, the exact method `room_guide_candidates.py`'s own docstring already names as deprecated (881 of 2808 rows carry it, the rest do not, and it was the source of three earlier wrong gap counts in sections 82/83/84). Ran `room_guide_candidates.py` itself first, per `CLAUDE.md` 5c/5d: it said Entryway has 0 on-topic gap and only 3 partial, a much weaker case than the PM's claim.

**Neither number was trustworthy as stated, so both were checked against the real file.** Reading the `room`-field rows directly: 23 of 50 are `gap`/`partial`, and nearly all are genuinely on-topic ("entryway closet ideas", "how to declutter entryway", "narrow entryway organization ideas"), not noise. But `room_guide_candidates.py`'s own `room_rows()` only matches `best_page == "/entryway-deck.html"` or a `/zones/entryway-*` prefix, by design (its docstring explains why it prefers `best_page` over the sparse field). Checking what those 23 rows actually route to: 53 of them land on `/deck/entryway-print-and-play.html`, a second, differently shaped deck URL this one room ships (a print-and-play page under `/deck/`, not `{room}-deck.html`) that `room_rows()` was never taught to recognise. So the tool was silently blind to 80 real Entryway rows, 30 of them on-topic, **0 of them `gap`**, because that page already answers most of them (many `covered`, the rest `partial`).

**Fixed the tool, not the symptom.** `room_rows()` now also matches `/deck/{slug}-print-and-play.html`. Fail-then-pass proved: reverted only the source change (kept the new test), confirmed `test_room_guide_candidates.py` FAILs on the missing match, reapplied, confirmed 7/7 pass. Re-ran `room_guide_candidates.py` on the real corpus after fixing: Entryway now scores 0 on-topic gap, 15 partial (up from 3), 38 on-topic of 121 routed rows (up from 8 of 41). Entryway has no second shipped room with the same URL shape today, so this was not special-cased to one slug; the pattern is matched generally.

**The decision, now on real evidence rather than either prior count.** Entryway does not get a guide this cycle: 0 gap either way, and the corrected reading shows its existing print-and-play deck page already covers most of the organizing queries that exist for it (several `covered` at full score), the opposite of a real gap. Declining for the same reason section 84's Family Room decision did: the method this repository now trusts says no, and the PM's naive count that said otherwise was itself the thing worth checking, not the thing to act on. Guest Bedroom (11 partial, still the highest of the genuinely guide-less rooms, confirmed unaffected by this fix since it ships no print-and-play variant) remains the next weakest-case candidate if that lane is picked up again; no room currently clears the Workshop-class bar (31+34) that justified a guide outright.

**Verified.** `python ops/tests/test_room_guide_candidates.py` 7/7. `python ops/fix_dashes.py --check` on both changed files, 0/0. Python syntax parsed directly on both files before relying on them. No content, price or product touched; no new page shipped, so `IndexNow` does not apply. `ops/preflight.py` run fresh this cycle reached `gate_tests` clean (0 FAIL on everything before it, `cycle_signal.py --check` confirms SAME against this snapshot) before hitting the same documented sandbox Chromium hang; killed cleanly, no orphaned process left behind.

## 88. Closed 2026-11-03, scheduled operator cycle: a step-by-step primary bathroom guide, the strongest remaining partial-coverage room after Patio or Deck

**Did.** Unshallowed and attached to main cleanly (651 commits fast-forwarded). Verified rather than cited: 30 GitHub issues pulled fresh via the API, unchanged, all `decision`, none genuinely from Phil (every comment on #42 traces to a prior agent cycle's own template, confirmed by reading the full thread, not assumed from the label); `inbox_agent.py --apply` correctly reports no mail credentials in this sandbox. Ran `ops/room_guide_candidates.py` fresh rather than trust the prior cycle's reading: Primary Bathroom scores 0 on-topic gap and 12 partial, the highest partial count of the 7 rooms still guide-less (Guest Bedroom 11, Dining Room 6), matching the method section 86 set. Family Room's 4 "gap" rows were read again, not just cited as already-declined: all four are either a misroute (dental organization landing on a family room page by word overlap alone) or a sub-topic the board-game zone already covers by a different phrase, not a real uncovered demand; left alone, same conclusion as every prior cycle today.

**Shipped** `site/articles/how-to-organize-a-primary-bathroom.html`, 3,105 words in `<main>`, grounded entirely in the room's own 7-zone `content.json` data (nothing invented): the heat-tool cord and plug-pull rule, the one-shampoo-one-conditioner-per-person caddy limit, the capped-razor-blade rule, the P-trap-visible bin layout and the dark-ring leak tell, the bleach-never-meets-bowl-cleaner rule, the three-towels-per-person count and the shelf-bracket weight check, and the medicine cabinet's humidity-accelerated expiry and child-catch rule. Order follows the room's own intro exactly (counter first, shower second, drawers, under-sink, toilet, linen, medicine cabinet last, "a session where you are willing to read small print"), not the corpus's listed zone order. Six-question FAQ grounded in the real partial-coverage queries `ops/keyword-demand.json`/`-global.json` actually carry for this room (master bathroom storage ideas for small spaces, under sink organizer, how to fold towels for storage), not invented questions. Primary offer RP-PRIMARY-BA ($9, 42 cards, confirmed live against `site/assets/js/data.js`'s own Stripe link), free start at the vanity counter zone matching the room's own stated priority.

**Wired the same way every room guide before it has been.** Added `"Primary Bathroom"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, reran it rather than hand-editing `site/rooms/primary-bathroom.html`, which picked up only the expected one-line "Related reading" addition). `site/articles/index.html` card and `CollectionPage` JSON-LD `hasPart` entry (hand-maintained, confirmed no generator owns this file before editing it; found and also fixed the same cycle, not reported around: Patio or Deck's own `hasPart` entry had been skipped by the cycle that shipped it, so both it and Primary Bathroom were added here). `site/llms.txt`'s `/articles/` bullet (49 to 50) and feed sub-clause (47 to 48 of 49 to 50), re-derived against the real file count rather than incremented by assumption. Sitemap (229, via `build_zone_pages.py`'s own rebuild). Feed (48, via `build_feed.py`, confirmed the new page's dated JSON-LD was picked up automatically). Share card (drew clean, 1 of 1). Two inbound links added: `tidy-is-not-the-same-as-safe.html` (the bowl-cleaner/bleach and medicine-date content is a direct fit) and a reciprocal link from `how-to-organize-a-guest-bathroom.html`, the sibling room. A third added to `ops/build_messy_article.py`'s generated Keep Reading list (self-chained, reran it rather than hand-editing the generated page, which also required `build_seo.py`, `fingerprint_assets.py --apply` and a second `build_feed.py` run to keep the regenerated page's own feed entry and asset hashes current).

**The keyword case, honestly.** This guide moved zero rows on either keyword tier (confirmed by rerunning `room_guide_candidates.py` after shipping: Primary Bathroom no longer appears in the guide-less list, and the global/US tiers were not rescored because the room had 0 gap rows to begin with, only partial). Picked on partial-coverage volume and topical completeness toward all 20 rooms, the same honestly-stated weakest case section 86 set for Patio or Deck, not a gap to close.

**A real, fixable gate failure found and fixed, not just logged.** Running `gate_roadmap_prices_current` directly after shipping caught `ROADMAP-2026-2029.md` section 2's own "233 pages live" citation one page stale against the real site (234, after this cycle's new article). Fixed in place; re-ran the gate directly, clean. `gate_risks_evidence_current` was already clean without a manual edit: its own `tree_derived_state()` fallback reconciles a RISKS.md citation against the live tree when the hourly `ops/state.json` snapshot has not caught up yet, exactly the case here, confirmed by reading the gate's logic rather than assuming a pass meant nothing had drifted.

**Verified.** `check_urls.py` (229/229), `audit_pages.py` (235 pages, 8 findings at first, all 8 on a single pre-existing gitignored probe artifact from a stalled `gate_tests` run this cycle itself killed, not on any page this cycle touched; the probe file removed). The same gate then caught a real defect in this cycle's own new page: the meta description ran 178 characters, 18 over the 160-character `desc-long` ceiling, meaning Google would have truncated it mid-sentence. Shortened to 144 characters across all four copies (`meta description`, `og:description`, `twitter:description`, the Article JSON-LD), confirmed by rerunning `audit_pages.py` (234 pages, 0 findings), and reran `share_cards.py` afterward since the card's own text had changed. `fix_dashes.py --check` (0 em/en dashes), `fix_dialect.py --check` (0 British spellings), manually confirmed 0 of each on the new page directly. `affiliate.py --check` (165 documents, unchanged, no affiliate link on the new page). `check_sellable.py` (124/126, 2 known services, unchanged). `link_graph_report.py` (50 articles, 0 orphans, min 2 inbound links, confirmed the new page itself carries exactly 2). `gate_primary_bathroom_deck_rendered`, `gate_llms_txt_current`, `gate_article_figures_current`, `gate_share_cards_current`, `gate_articles_room_zone_counts_current`, `gate_deck_article_grammar`, `gate_root_cause_articles_current` and `gate_specific_article_direct_answer` all called directly against the real committed files: clean. `ops/dashboard.py` rerun, state committed.

**Not fully checked, said so rather than assumed.** A full unbackgrounded `preflight.py` run hit the same documented headless-Chromium `test_contact_form_interactive.py` hang partway through `gate_tests` that several cycles today already logged; killed by pid after confirming flat CPU time across a real wait, the orphaned Chromium tree and its gitignored probe HTML file both cleaned up by hand rather than left for the next cycle to rediscover. Every gate this cycle's own change could plausibly touch was instead called directly against the real files and confirmed clean above, which is narrower than a full run but is not a guess. No Search Console data exists to confirm this guide earns any impressions; that stays an unmeasured bet, same as every room guide before it. Entryway, Dining Room, Family Room, Guest Bedroom, Mudroom and Stair Landing remain guide-less; Family Room and Mudroom are both weaker per this cycle's own re-read above, so Guest Bedroom (11 partial) is the next candidate, not a re-derivation from scratch. Real next lever remains Phil-gated (YouTube OAuth, Search Console, Gemini billing, Amazon KDP/Etsy, Apple/Play, the accounts decision).

## 87. Closed 2026-11-03, scheduled operator cycle: built the section-3/4 rotation tool two prior cycles named real but deferred, closing a standing `rotate_backlog_section2_items.py` handoff rather than re-deferring it a third time

**Did.** Unshallowed and attached to main cleanly (642 commits fast-forwarded onto `0aa05974f`, tree clean). Re-verified rather than trusted: 30 GitHub issues pulled fresh, unchanged, all `decision`/`blocked-on-art`, none from Phil; `BACKLOG-2026-09-07.md` sections 2-6 only C5/C6 unstruck, both explicit `YES, Phil`; a full `preflight.py --skip-tests` run reached roughly 230 gates with 0 FAIL before the same documented `gate_etsy_pdfs_current` network stall (Etsy's fee schedule, HTTP 403) every recent cycle has already hit; killed there rather than left to hang. `inbox_agent.py --apply`: no mail credentials in this sandbox, correctly reported unchecked. Epics 1-5 (measurement, broken/dishonest, traffic, conversion, product) confirmed exhausted of non-Phil-gated work by at least three separate cycles earlier today; this cycle picked up the one piece of named, real, unclaimed epic-6 work the 01:5x and 02:0x cycles both flagged as "not urgent enough for this slot": `BACKLOG-2026-09-07.md` sections 3-4 had no rotation tool, unlike sections 1b and 2, because `rotate_backlog_section2_items.py`'s own docstring deferred them, citing `rotate_backlog_done_items.py`'s warning that "a generic find a line starting with `**ID` parser would silently archive the wrong text... or the right text under the wrong byline."

**Checked the hazard directly rather than re-deferring on the strength of the old warning.** A scan of the real byte structure found the warning was right but incomplete. Two things differ from section 2's shape: (1) several rows are bare bold paragraphs with no leading pipe at all ("**B1 follow-on, found and fixed 2026-09-08...**"), which a pipe-only parser misses entirely; (2) the real misattribution hazard is concrete, not hypothetical: two un-id'd "Corrected 2026-10-14" paragraphs near the end of section 4 sit physically after the "C7 fourth-wave" row (dated 2026-10-27) but actually amend the different, earlier "C7 second wave" entry (dated 2026-10-09). Section 2's rule ("archive from one matched row up to the next") is safe there because its rows sit back-to-back with no orphan continuation text between them; it would not be safe here.

**Built accordingly, narrower than section 2's rule by design.** `ops/rotate_backlog_journal_core.py` (shared logic) plus two thin wrappers, `ops/rotate_backlog_section3_items.py` and `ops/rotate_backlog_section4_items.py`, each archiving into their own new `BACKLOG-2026-09-07-SECTION3-ARCHIVE.md` / `SECTION4-ARCHIVE.md`. The core's rule: archive ONLY a matched row's own single physical line (confirmed by direct scan that every dated row in both sections really is one line); never touch anything after its own trailing newline, no matter what it is, blank line, `---` divider, or a substantial orphan paragraph. This makes the byline-misattribution hazard structurally impossible rather than merely checked for, at the cost of never auto-rotating an un-id'd orphan paragraph, which is the correct, conservative answer rather than a gap to close by guessing which row it belongs to.

**Verified before touching the live file, then verified again after.** Dry-run `--check` against the real file matched a hand-built manual scan exactly (6 rows/13420 bytes due in section 3, 2 rows/4783 bytes in section 4). Applied; confirmed by direct inspection of the resulting diff, not assumed: the `---` divider between the old B8 and B9 rows survived untouched, and the two "Corrected again 2026-10-14"/"CLOSED 2026-10-14" orphan paragraphs in section 4, plus the C7 third-wave and fourth-wave rows (both dated 2026-10-27, inside the 14-day retention window), were left exactly as they were, live. `BACKLOG-2026-09-07.md` fell from 202890 to 185829 bytes (17061 bytes moved). New `gate_backlog_section3_items_rotated` and `gate_backlog_section4_items_rotated` wired into `preflight.py`, mirroring `gate_backlog_section2_items_rotated`'s retention-plus-7-day-buffer pattern exactly; both silent against the real, now-rotated file. Fail-then-pass proved directly: `ops/tests/test_gate_backlog_section3_items_rotated.py` (6/6, including a bare no-leading-pipe paragraph row, the shape section 2's tool cannot see) and `ops/tests/test_gate_backlog_section4_items_rotated.py` (6/6, including a planted orphan-paragraph case that asserts the rotation leaves it live and files exactly one block, not two, into the archive) both pass; both warn correctly on a synthetic stale file and stay silent on a synthetic fresh one. Re-ran the sibling section2/section1b tests afterward to confirm no regression from editing `preflight.py`: both still 5/5. Full `preflight.py --skip-tests` re-run after all edits: same 0-FAIL result up to the same pre-existing network stall, both new gates present and silent in the log. `fix_dashes.py --check`: 0 em/en dashes across the whole repository including the three new `.py` files.

**Still over the tripwire, correctly, not neglected.** `BACKLOG-2026-09-07.md` is 185829 bytes against its 150000-byte tripwire; `OWNER-ACTIONS.md`'s own equivalent gap (128458 bytes against 110000, no rotation tool for its open-items section) is unchanged and real, left for a future cycle rather than started here, the same kind of explicit, named deferral this entry itself just closed for sections 3-4. No price or product touched, no site page changed, IndexNow not applicable.

## 86. Closed 2026-11-02, scheduled operator cycle: a step-by-step patio or deck guide, the room `room_guide_candidates.py` and the 12:4x PM check-in both named once Guest Bathroom shipped

Fresh checkout arrived shallow and detached per STEP 0; unshallowed, attached to main cleanly (613 commits fast-forwarded, tree clean). All 30 open GitHub issues re-pulled fresh: unchanged, all `decision`/`blocked-on-art`, issue #42 untouched since 13:51:51Z, no reply from Phil. `inbox_agent.py --apply`: no mail credentials in this sandbox, correctly reported unchecked.

**Picked the room, not assumed it.** Ran `ops/room_guide_candidates.py` fresh against the 8 remaining guide-less rooms (Entryway, Dining Room, Family Room, Guest Bedroom, Primary Bathroom, Mudroom, Stair Landing, Patio or Deck): Patio or Deck scores 0 on-topic `gap` and 14 `partial`, the highest partial count of any of them (Primary Bathroom 12, Guest Bedroom 11), confirming it as the strongest candidate left once Guest Bathroom (section 83) closed out its own tie-score pair. Spot-checked the two softest-looking global gap rows that mention this room's words before writing anything: "how to organize car trunk suv" and "how to organize soap making supplies" were already correctly declined by two independent prior cycles (logged above, 2026-10-31) as genuine content gaps this room's real zone text does not cover (no "trunk" or cargo-storage content, no lye/soap-making safety text), not a synonym fix; left alone again rather than re-litigated.

Shipped `site/articles/how-to-organize-a-patio-or-deck.html`, 3,550 words in `<main>`. Zones ordered by the room's own `content.json` intro ("do the Surface, Rail, and Safety Zone first... before you touch a single cushion"), not the corpus's listed order: structure and safety first, then seating, the deck box the cushions actually live in, the dining table, the grill, and the garden/chemical zone last. Every fact pulled from the real zone data, nothing invented: the chair-flex press test, the resin-brittleness check, the propane tare-weight scale test and tank requalification date stamp, the wire-brush-bristle and grease-tray fire risks, the deck-box lid-stay hinge hazard and mouse-nesting fabric risk, the umbrella-as-sail and RCD-cord electrical rules, the half-bottle chemical disposal rule, and the screwdriver board-probe test. Six-question FAQ, a "balcony, not a full deck" variant section covering the seating and storage edge cases the zone data itself names, primary offer RP-PATIO-OR-D ($9, 36 cards, confirmed live against `site/assets/js/data.js`'s own Stripe link), free start at the surface/rail/safety zone matching the room's own stated priority.

**Wired the same way every room guide before it has been.** Added `"Patio or Deck"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, reran it rather than hand-editing `site/rooms/patio-or-deck.html`, which picked up only the expected one-line "Related reading" addition). `site/articles/index.html` card and JSON-LD list entry (hand-maintained, confirmed no generator owns this file before editing it). `llms.txt` (49 articles, feed 47). Sitemap (228, via `build_zone_pages.py`'s own rebuild). Feed (47, via `build_feed.py`'s auto-discovery of the new page's dated JSON-LD). Share card (drew clean, 1 of 1, after fixing this fresh container's own Pillow mismatch below). Two inbound links added: `tidy-is-not-the-same-as-safe.html` (the rail-push, board-probe and grease-tray content is a direct fit for that page's own safety-check theme) and `how-to-organize-a-garage.html` (the other space where fuel, chemicals and tools share close quarters). A third link added to `ops/build_messy_article.py`'s generated Keep Reading list (self-chained, reran it rather than hand-editing the generated page), continuing the chain that article's generator already carries for the prior three guides.

**The keyword case, honestly.** Both tiers rescored (`--rescore`, free, no network): US 131/1297/1380 unchanged; global 98/986/1086 unchanged. This guide moved zero rows on either tier, the same weakest-case shape Guest Bathroom (section 83) already set as precedent, consistent with issue #42's own thesis that the keyword-gap lane is exhausted; the room was picked on partial-coverage volume and topical completeness toward all 20 rooms, not a gap to close, and that is stated here rather than overclaimed.

**A real sandbox defect found and fixed again, not reported around.** `ops/share_cards.py` failed on the new page with the identical `cannot import name '_imaging' from 'PIL'` error section 80's entry already diagnosed once in a different container. This is a fresh container with no memory of that fix; `python3 -m pip install --force-reinstall --no-deps Pillow` fixed it again, confirmed by `from PIL import Image` succeeding and the card drawing clean (manifest 91 pages, drew 1, failed 0). Recorded again here rather than assumed permanent, since section 80 already flagged this as a standing risk that recurs on every freshly provisioned sandbox.

**Verified.** `check_urls.py` (228/228), `audit_pages.py` (233 pages, 0 findings, 0 duplicate titles/descriptions), `fix_dashes.py --check` (0 em/en dashes sitewide), `fix_dialect.py --check` (0 British spellings on the tracked surfaces), manually confirmed 0 em/en dashes and 0 British spellings on the new page directly as well. `affiliate.py --check` (165 documents, unchanged, no affiliate link on the new page). `check_sellable.py` (124/126, 2 known services, unchanged). `link_graph_report.py` (49 articles, 0 orphans, min 2 inbound links). `ROADMAP-2026-2029.md`'s page-live count (232 to 233) and `RISKS.md`'s `forms_dead` citation (232 to 233) both re-derived directly against the live tree (`len(all_pages())`, the footer-form count) rather than guessed, matching `gate_roadmap_prices_current` and `gate_risks_evidence_current`'s own logic exactly.

**Not fully checked, said so rather than assumed.** A full `preflight.py --skip-tests` run was started to confirm no regression beyond the targeted checks above: it reached roughly 230 of the suite's gates with 0 FAIL before stalling on `gate_etsy_pdfs_current`, a network-fetch gate (Etsy's fee schedule returns HTTP 403 from this sandbox) entirely unrelated to this cycle's change, the same class of network-dependent stall this repository's log already documents repeatedly. Killed after several minutes rather than left to hang; the resulting stale `/tmp/.preflight_py_running.lock` (pid confirmed dead) removed. Every gate that actually touches pages, links, dashes, dialect, affiliate rules, sellability or the link graph was run individually above and is clean; the untested remainder of the suite is almost entirely the same standing Etsy/KDP/Stripe-network/DNS limitations every recent cycle already reports as unchecked, not failing.

**Not done.** No Search Console data exists to confirm this guide earns any impressions over the room hub. Entryway, Dining Room, Family Room, Guest Bedroom, Primary Bathroom, Mudroom and Stair Landing remain guide-less; Family Room (1 real gap row) and Mudroom (0 after noise exclusion) are both weaker than this pick per section 84's own method, and the next cycle should not re-derive that ranking from scratch. Real next lever remains Phil-gated (Etsy, KDP, Search Console, YouTube OAuth, Gemini billing, the accounts decision, issue #42 itself).

## 85. Closed 2026-11-02, scheduled operator cycle: STATUS.md's deploy citations drifted stale again, and the real reason `rotate_status_history.py` never caught 13 un-rotated entries was found and gated

`status_deploy_verdict_problem()` called directly found `ops/deploy-verdict.json` had moved to `c294d052311be657` (the kids bedroom ship's own rebuild) while all five spots STATUS.md uses to cite the deploy state still read `b150c19629689ad2`. Fixed all five, re-derived directly against real current `HEAD` (0 commits undeployed).

Fixing it pushed STATUS.md to 112,901 bytes, over its own 110,000-byte tripwire, but `ops/rotate_status_history.py --check`/`--check-blocker1` both answered "CLEAN: 1 entry live," which did not square with a Production Knowledge paragraph visibly carrying a dozen dated corrections back to 2026-10-22. Root cause: `split_chain()`/`split_blocker1_chain()` both require one entry per physical line or blank-line paragraph, and the real chain had every entry glued onto one physical line via the "Prior state, kept because the shape recurs: " handoff phrase, so the parser saw one line and stopped looking. This chain appears to have never rotated successfully: 13 Production Knowledge entries and 3 BLOCKER-001 entries had silently piled up, invisible to the tool built to catch exactly this.

Split both chains by hand on the handoff phrase (round-trip verified byte-for-byte before touching anything), archived 12 Production Knowledge and 2 BLOCKER-001 entries verbatim to `STATUS-ARCHIVE.md`, kept one live entry in each field. STATUS.md: 100,157 bytes, tripwire clear. New `gate_status_history_chain_not_collapsed` in `preflight.py` warns if either chain's live span contains the handoff phrase again, per `CLAUDE.md` 10b. Fail-then-pass proved directly: `ops/tests/test_gate_status_history_chain_not_collapsed.py`, 5/5; confirmed silent against the real, fixed file.

**Verified.** Full `preflight.py --skip-tests` to genuine completion: 0 FAIL, 34 warnings, all previously diagnosed (no Stripe/.env.secrets, no SSH deploy key, no mail credential, no DNS, no live films/images, Etsy/shop-prerender timeouts). `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents, `check_sellable.py` 124/126 (2 known services), `check_urls.py` 227/227. `gate_tests` itself not run (documented sandbox hang); unchecked, not passed, per `CLAUDE.md` 0.4. `ops/indexnow.py --submit` correctly refused to claim submission for the one unsubmitted sitemap URL from an earlier cycle's ship (cannot reach the site from here to confirm the key file serves). Command deck regenerated: YELLOW, $0 of $20,000 (carried forward), $19 all-time, 9 P0, 28 need-you.

**Not done.** No price, product or site page touched; no new page, `IndexNow` not applicable to this cycle's own changes. Real next lever remains Phil-gated (Etsy, KDP, Search Console, YouTube OAuth, Gemini billing, the accounts decision).

## 84. Closed 2026-11-02, scheduled operator cycle: a step-by-step kids bedroom guide, a reusable tie-score tool, and a third correction to the method itself

A 13:4x PM handoff the same day re-scored Family Room as "9 gap (US tier)", up from a prior cycle's own "0 gap" read, and named but did not fix the reason: it matched candidate rows by `best_page` rather than this entry's own `room:`-tag filter (`room:` is sparse, present on only 881 of 2808 rows; `best_page`, which page a query actually routes to today, is the field that decides whether a query already has an answer), and several of its 9 were digital-library queries ("how to organize steam games", "online storage for games") that happen to route to the Family Room board-game zone page by word overlap but are not physical-organization demand. Checked directly rather than trusted, per `CLAUDE.md` 5d: re-ran the `room:`-tag method myself first, got 0 (the opposite error, wrong in the other direction), then matched the handoff's own 9 by `best_page` and confirmed it.

**Built `ops/room_guide_candidates.py` so this stops being re-derived by a different one-liner every cycle.** One script: matches candidate rows by `best_page` against each guide-less room's deck and zone pages, filters on-topic by the organize/declutter/clean/storage/stock pattern sections 82/83 already established, and adds a digital-context exclusion list (pc, steam, computer, desktop, digital, online, software, app, download) the prior filter never had. Run across all 9 remaining guide-less rooms (Dining Room, Entryway, Family Room, Guest Bedroom, Kids Bedroom, Mudroom, Patio or Deck, Primary Bathroom, Stair Landing).

**Results, each gap row hand-read per CLAUDE.md 5c before trusting the count.** Family Room: 9 raw, 4 after the digital exclusion (`card games organizer storage`, `dental organization ideas`, `nightstands with hidden storage`, `storage for video games`); reading the seeds behind the remaining 4 found 2 more are autocomplete noise, not demand (`dental organization ideas` is Google substituting "dental" for the seed `den organization ideas`, 0.0 coverage; `nightstands with hidden storage` comes from the seed `how to organize left nightstand`, an odd phrase its own suggestion garbled). Real count: 1 (`card games organizer storage`). Kids Bedroom: 1 on-topic gap row with no noise to exclude, `building beds for kids organization`, a coherent match to its own seed `kids bedroom organization ideas`. Mudroom: 1 raw gap row, `organize outdoor diy lab`, also noise (seed `how to organize outdoor dining`, same garble class). The other 6 rooms scored 0. **Picked Kids Bedroom over Family Room despite Family Room's higher raw count**, because Kids Bedroom's single row survived the noise check and Family Room's did not.

Shipped `site/articles/how-to-organize-a-kids-bedroom.html`, roughly 3,100 words in `<main>` (3,814 including nav and footer boilerplate): six zones in the order the room's own corpus tip names ("clear the floor first, working out of the Toy Storage Zone"), not `content.json`'s listed order, since that is the one explicit sequencing instruction already in the data. Every fact (the unanchored dresser as a climbing-frame tip risk, the blind-cord strangle risk near the bed head, the overloaded desk socket, the overloaded closet rod, button batteries and small parts reachable by a younger sibling, the named medication pocket in the school bag) pulled from the real zone `watch_for`, `safety` and `the_call` fields, nothing invented. 6-question FAQ matching sampled query phrasings. Primary offer RP-KIDS-BEDRO ($9, 36 cards, confirmed live against `site/assets/js/data.js`'s own Stripe link), free start at the toy storage zone. Added `"Kids Bedroom"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, reran it rather than hand-editing `site/rooms/kids-bedroom.html`, which only added the one "Related reading" link as expected). Wired: `site/articles/index.html` card and JSON-LD list entry (hand-maintained, confirmed no generator owns this file), `llms.txt` (48 articles, feed 46), sitemap (227, via `build_zone_pages.py`'s own rebuild), feed (46, via `build_feed.py`'s auto-discovery), share card (drew clean, 1 of 1), `ROADMAP-2026-2029.md` (232, with the corrected tie-score method recorded in the chain), `RISKS.md` RISK-0012 headline count only (231 to 232, per that section's own rule to stop writing a log line for same-kind additions).

Both keyword-demand tiers rescored (`--rescore`, free, no network): US 132/1300/1376 to 131/1297/1380 (gap/partial/covered); global 99/990/1081 to 98/986/1086. **Checked which row actually closed, not assumed:** in both tiers the 1 `gap` that closed is `simple guest bathroom decorating ideas pictures`, unrelated to this guide, a decorating-intent row drifting against the guest bathroom deck page. This guide itself moved **zero** gap rows to covered, the same weakest-case shape as Guest Bathroom and Living Room, but did become the new `best_page` for 8 US and 46 global previously-`covered` rows and 19 US `partial` rows that used to point at the generic room hub or zone pages, a real precision gain even without a literal gap closure.

**Verified.** `check_urls.py` (227/227), `audit_pages.py` (232 pages, 0 findings), `fix_dashes.py --check` (0/0, sitewide), `affiliate.py --check` (165 documents, unchanged, no affiliate link on the new page), `check_sellable.py --deep` (124/126, 2 known services, deep live-price check unavailable, no `.env.secrets`), `link_graph_report.py` (48 articles, 0 orphans) all clean. `audit_visual.py` on the new page, desktop and mobile: 0 findings each. First `preflight.py --fast` pass hit the documented `gate_tests` headless-Chromium sandbox hang at `test_audit_catalog.py`: confirmed genuinely stalled by flat CPU time across a 15s sample, killed by PID, stale lock directory removed. **Own mistake caught and fixed mid-cycle:** a misplaced `git stash` run to compare before/after keyword-demand state stashed every uncommitted change in the working tree, including this cycle's own unpushed work, for about a minute while a concurrent `preflight.py --skip-tests` run was reading those same files; `git status` immediately after showed only the untracked new files remained, `git stash pop` restored everything, confirmed clean by `git status` again, and the disturbed preflight run was killed and rerun from a known-clean tree rather than trusted.

**Not done.** No Search Console data exists to confirm this guide earns any impressions. Patio or Deck, Guest Bedroom, Dining Room, Entryway, Primary Bathroom and Stair Landing all scored 0 under the corrected method, confirming, on a fourth independent method now, issue #42's thesis: the room-guide-via-keyword-gap lane is exhausted. The remaining value in shipping the other 7 guide-less rooms, if any cycle picks this up again, is topical completeness and internal-linking precision (the 8/46/19-row reclassification above), not a keyword gap to close; say so plainly rather than tie-scoring a candidate that has none.

## 83. Closed 2026-11-02, scheduled operator cycle: a step-by-step guest bathroom guide, and a correction to the tie-score method's own query filter

Took the 12:4x PM check-in's own tie-score pick between Guest Bathroom and Patio or Deck (tied at "7" non-covered rows each, Guest Bathroom carrying the one real `gap` row). **Checked the "7" itself before committing, per `CLAUDE.md` 5d, rather than trusted it, and it was wrong in a different way than the living-room cycle's gap-vs-partial correction: it counted every row tagged `room: Guest Bathroom` regardless of query intent, and this room's demand is almost entirely decorating/design/pinterest queries an organizing guide cannot honestly answer.** Filtered to the organize/declutter/clean/storage/stock word pattern the pantry and living-room ships both used: Guest Bathroom carries only 6 US and 10 global on-topic rows, and all 16 were already `covered` or `partial` against the existing free deck page and the vanity-storage zone page, 0 `gap`. The guide moved zero rows from `partial`/`gap` to `covered` on rescoring, the weakest keyword case of any room guide so far.

Shipped `site/articles/how-to-organize-a-guest-bathroom.html`, 2,571 words, anyway: the room had no step-by-step guide or direct-answer FAQ surface of its own, every fact (the dry-trap sewer smell, the toddler-height bowl-cleaner hazard, the bleach-plus-acid-cleaner gas risk, the unanchored towel bar, the water-heater scorch risk in a shared linen closet) pulled from `content.json`'s real zone `watch_for`/`passes` data, nothing invented, and the site's own pattern has been to give every room this format eventually. 6-question FAQ matching the on-topic queries sampled above, including the two genuinely unanswered-elsewhere ones ("how do I stock a guest bathroom", "why does it smell musty"). Primary offer RP-GUEST-BATH ($9, 30 cards, confirmed live against `site/assets/js/data.js`'s own Stripe link), free start at the vanity counter zone. Wired the same way as every guide before it: `ROOM_GUIDES` (self-chained generator, `ops/build_zone_pages.py`), `ops/build_messy_article.py`'s own template (regenerated, not hand-edited), `family-wont-put-things-back.html` (hand-maintained), `site/articles/index.html` card and JSON-LD entry (hand-maintained, no generator owns this file), `llms.txt` (47 articles, feed 45), sitemap (226, via `build_zone_pages.py`'s rebuild plus `build_seo.py`), feed (45, `build_feed.py`'s auto-discovery), share card (drew clean), `ROADMAP-2026-2029.md` (231, with the query-filter correction recorded in the chain), `RISKS.md` headline count only (230 to 231, per that file's own "nothing new in kind" rule).

Both keyword-demand tiers rescored (`--rescore`, free, no network): US 133/1300/1375 to 132/1300/1376; global 100/991/1079 to 99/990/1081 (the one gap closed in each tier was unrelated to this room, both already decorating-intent rows elsewhere; Guest Bathroom's own 2 `gap` rows, both pinterest/decorating queries outside this guide's scope, are unchanged and correctly so).

**Verified.** `check_urls.py` (226/226), `audit_pages.py` (232 audited including one transient, gitignored probe file from a concurrently running test suite, not a real page; 0 findings on the new page), `fix_dashes.py --check` (0/0), `fix_dialect.py --check` (0/0), `affiliate.py --check` (165 documents, unchanged, no affiliate link on the new page), `check_sellable.py --deep` (124/126, 2 known services, deep live-price check unavailable, no `.env.secrets`), `link_graph_report.py` (47 articles, 0 orphans, min 2 inbound) all clean. `audit_visual.py` on the new page, desktop and mobile: 0 findings each. A full local `preflight.py` run hit the documented `gate_tests` headless-Chromium sandbox hang at `test_contact_form_interactive.py` (a different test than usual, same standing shape): confirmed genuinely stalled by flat CPU time across a 20s sample, killed by PID, confirmed dead, stale lock removed; `preflight.py --skip-tests` run separately to cover everything else.

**Not done.** No Search Console data exists to confirm this guide earns any impressions; unmeasured-bet status, same as every room guide before it. **Recorded for the next room-guide cycle: filter a candidate room's on-topic query count by the organize/declutter/clean/storage word pattern BEFORE scoring its tie-score candidacy, not by raw `room:` tag membership**, which is what let a decorating-heavy room look like a 7-row opportunity when the real on-topic number was 0 `gap`. Patio or Deck has not been re-checked against this corrected filter and may score differently than its own raw count suggested; a future cycle should re-run the filter on it before picking it next.

---

## 82. Closed 2026-11-02, scheduled operator cycle: a step-by-step living room guide, and a correction to the room-guide tie-score method itself

Handed off by name (11:4x PM check-in): start the Living Room guide, the next room by raw query volume (43 US + 23 global) among the 11 rooms still without a `ROOM_GUIDES` entry, same method the pantry cycle used. Sampled all 47 unique US-plus-global queries in the organize/declutter/clean/storage cluster before committing, per `CLAUDE.md` 5c: every one genuinely on-topic (furniture arrangement by shape, toys, blankets, small spaces), no noise. **Checked the claim behind the handoff rather than trusted it, per `CLAUDE.md` 5d, and it was only half right.** Unlike pantry, laundry, kitchen, garage, workshop and bedroom, none of which had a dedicated guide and mostly scored `gap` against `/about.html` before their guide shipped, Living Room's own cluster had **zero `gap` rows in either tier**: `/living-room-deck.html`'s own headings already matched 24 of 44 US rows and 21 of 26 global rows to `covered`, the rest to `partial`. The room was still the right pick by the tie-score method as written (raw volume among ungated rooms), but "the only genuinely unblocked traffic lane" overstated what writing the guide would actually close. Recorded here so the next room-guide cycle checks gap status specifically, not just volume, before claiming a room closes a coverage gap.

Shipped `site/articles/how-to-organize-a-living-room.html`, 2,533 words: the six zones in `content.json`'s own stated order of priority (the intro names the floor and the coffee table first, "because those two are what you see from the doorway," ahead of the zones array's own listed order), every fact (the recliner footrest and sofa-bed pinch risk, the unanchored television tipping forward, the unstrapped bookcase, the loose-tablet choke risk, the media center's blocked-vent fire risk) pulled from the real zone `watch_for` and `diagnosis` data, not invented. 6-question FAQ matching sampled query phrasings, including a small-living-room answer and a kids'-toys answer that honestly routes heavy daily toy traffic to the Family Room's own Toy and Play Zone rather than inventing a toy bin this room's content does not have. One query cluster set aside rather than answered: "how to arrange a long/narrow/two-sofa living room" is a furniture-layout question with no sourced guidance on this site, stated plainly on the page rather than guessed at. Primary offer RP-LIVING-ROO ($9, 36 cards, confirmed live against `site/shop.html`'s own Stripe link), free start at the floor and circulation path zone. Added `"Living Room"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, not hand-edited output) so `/rooms/living-room.html` links the guide first. Inbound links added from `family-wont-put-things-back` (hand-maintained) and `why-is-my-house-always-messy` (generator-owned, `ops/build_messy_article.py`; added the link to its own `BODY` template and reran the generator rather than hand-editing its output, per `CLAUDE.md` 5b). Wired: `site/articles/index.html` card and JSON-LD list entry (hand-maintained, confirmed no generator owns this file before editing it), `llms.txt` (46 articles, feed 44), sitemap (225, via `build_zone_pages.py`'s own rebuild plus `build_seo.py`), feed (44, via `build_feed.py`'s auto-discovery), share card (drew clean), `ROADMAP-2026-2029.md` (230, with the gap-status correction above recorded in the chain rather than silently matching the prior entries' phrasing), `RISKS.md` RISK-0012 headline count only (229 to 230, same inert-footer-form convention as every prior addition).

Both keyword-demand tiers rescored (`--rescore`, free, no network): US 133/1303/1372 to 133/1300/1375 (gap/partial/covered, gap unchanged, confirming the finding above); global 100/993/1077 to 100/991/1079.

**Verified.** `check_urls.py` (225/225), `audit_pages.py` (230 pages/0 findings, 0 duplicates), `fix_dashes.py --check` (0/0), `fix_dialect.py --check` (0/0), `affiliate.py --check` (165 documents, unchanged, no affiliate link on the new page), `check_sellable.py --deep` (124/126, 2 known services, deep live-price check unavailable, no `.env.secrets`), `link_graph_report.py` (46 articles, 0 orphans, min 2 inbound) all clean. `audit_visual.py` on both the new page and the regenerated `why-is-my-house-always-messy.html`, desktop and mobile: 0 findings each. `gate_roadmap_prices_current`, `gate_risks_evidence_current`, `gate_feed_current`, `gate_llms_txt_current`, `gate_sitemap_complete` and `gate_sitemap_lastmod_current` called directly against the live tree after every edit above, matching this morning's 09:1x/09:2x CI-red lesson (a page-count bump left uncorrected in a sibling document): all clean before this item's own commit, not left for CI to catch.

**Not done.** No Search Console data exists to confirm this guide earns impressions over the deck page it partly duplicates; unmeasured-bet status, same as every room guide before it. The furniture-arrangement query cluster (long, narrow, two-sofa, two-focal-point living rooms) is real, sampled demand with no sourced answer on this site; flagged here rather than fabricated, for a future cycle with the right sourcing.

## 81. Closed 2026-11-02, scheduled operator cycle: a step-by-step pantry guide, the next tie-score candidate after laundry room

**Verified exhausted first, not assumed.** All 30 open GitHub issues checked live via the API: unchanged since `2026-11-01T19:44:28Z`, none from Phil (spot-checked issue #63, the newest, directly: 0 comments). `ops/last-owner-notification.json` names a standing no-repeat-before of `2026-11-04T04:00Z` for the owner-decision-queue topic; that window had not passed and nothing material changed, so no push notification this cycle. Sections 2-6 of this file hold nothing unstruck beyond the owner gates, same standing conclusion every recent cycle has independently reached.

**Action.** Continued the other half of Epic 3 (traffic) that item 80 started: scored the eleven remaining candidate rooms without a `ROOM_GUIDES` entry against both keyword tiers directly (organize/declutter/clean/storage rows, any status). Pantry led by a wide margin at 58 US + 56 global rows, ahead of Living Room (43+23), Entryway (28+22) and Mudroom (20+20); Family Room, item 80's other named candidate, scored only 4+4 this pass once the counting matched the real query text rather than a prior estimate. Sampled the actual pantry query list before committing, all 114 unique rows: overwhelmingly genuine "how to organize a pantry" variants (deep shelves, pull-out shelves, wire racks, walk-in pantry, pantry cabinet, small pantry, baking supplies, snacks, bulk shopping), with one unrelated cluster set aside rather than answered: "why is my pantry damp/cold/warm/humid" is a moisture and climate-control question, a different root cause this operator has no sourced facts for, not an organizing-method gap, so no FAQ entry invents an answer to it.

Shipped `site/articles/how-to-organize-a-pantry.html`: the five zones in the order the room's own `content.json` intro gives them (dry goods shelves first, "gives every other zone somewhere to put things"), each section's facts pulled from the real zone data, not invented: the moth/webbing pest check, the domed-can and dented-seam spoilage warning, the allergen cross-contact and child-reach hazards in the baking and snack zones, the stacked-case and heavy-sack lift risks in backstock. 2,295 words, 6-question FAQ matching the real query phrasings sampled above (including a deep-shelves answer and a small-pantry/pantry-cabinet answer), a dedicated section for both. Primary offer RP-PANTRY ($9, 30 cards, confirmed not retired and matching the live Stripe link in `site/shop.html`) plus CN-VIRTUAL; free start link to the dry-goods-shelves zone, matching the room's own "where to start" tip. Added `"Pantry"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, not hand-edited output) so `/rooms/pantry.html` links the guide first in Related reading. Inbound links added from `family-wont-put-things-back` and `why-you-keep-running-out-of-things`. Wired: `site/articles/index.html` card and JSON-LD list entry (hand-maintained, confirmed no generator owns this file before editing it), `llms.txt` (45 articles, feed 43), sitemap (224, via `build_zone_pages.py`'s own rebuild), feed (43, via `build_feed.py`'s auto-discovery of the new page's dated JSON-LD), share card (drew clean, the Pillow fix from item 80 held), `ROADMAP-2026-2029.md` (229), `RISKS.md` RISK-0012 headline count only (228 to 229, per that entry's own "enumerate only when different in kind" convention, since this addition carries the same inert footer form as every other page).

**Verified.** `check_urls.py`, `audit_pages.py`, `fix_dashes.py --check`, `fix_dialect.py --check`, `affiliate.py --check`, `check_sellable.py --deep`, `link_graph_report.py`, and a full `preflight.py --skip-tests` run were all run after this item shipped; results recorded in this same cycle's `ops/NIGHTLY-LOG.md` entry per `CLAUDE.md` 0.4 rather than cited twice here. `gate_risks_evidence_current` and `gate_roadmap_prices_current` called directly after the RISKS.md/ROADMAP edits above, matching this morning's 09:1x/09:2x CI-red lesson (a page-count bump left uncorrected in a sibling document): both clean before this item's own commit, not left for CI to catch.

**Not done.** No Search Console data exists to confirm this guide earns impressions over the room hub; same unmeasured-bet status sections 71/73/74/80 already carry. The "why is my pantry damp/warm" query cluster found above is a genuine, unanswered intent, but it is a moisture/ventilation question outside this operator's sourced material; flagging it here rather than fabricating an answer, for a future cycle with the right sourcing to pick up if it is worth a dedicated page.

## 80. Closed 2026-11-02, scheduled operator cycle: a step-by-step laundry room guide, and a broken Pillow install in this sandbox fixed rather than reported around

**Verified exhausted first, not assumed.** All 30 open GitHub issues checked live: unchanged since `2026-11-01T19:44:28Z`, none from Phil. `ops/last-owner-notification.json` names a standing no-repeat-before of `2026-11-04T04:00Z` for the owner-decision-queue topic; that window had not passed and nothing material changed, so no push notification this cycle. Sections 2-6 of this file hold nothing unstruck beyond the owner gates. With the standing queue genuinely exhausted, read the gap tier of both keyword-demand files directly rather than cite their counts (per `CLAUDE.md` 5c): opened and read all 23 queries across the 10 highest-volume `best_page` buckets in the 133-row gap tier (stair landing, family room board games, guest bathroom, patio or deck, kitchen, nursery, and five more). Every one is the same word-collision noise this repository has already named (A54/section 74's class): staircase construction queries matching "stair landing," PC and console gaming queries matching "board game zone," medical bathroom-frequency queries matching "guest bathroom," deck-and-patio landscaping queries matching the patio room, adult incontinence and woodworking-plans queries matching nursery and nightstand zones. None is a real organizing-content gap. The gap tier is exhausted for actionable new content, same conclusion as every recent cycle, now backed by an opened sample rather than a cited count.

**Action.** Moved to the other half of Epic 3 (traffic): the "organize/declutter query ties to the room hub instead of a dedicated how-to guide" scan sections 71/73/74 already used for kitchen, garage and workshop. Scored the twelve remaining candidate rooms without a `ROOM_GUIDES` entry directly against both keyword tiers (organize/declutter rows only, partial or covered status): laundry room led at 72 US + 44 global, ahead of family room (70+48, noisier on inspection) and pantry (64+50). Sampled the actual laundry room query text before committing: "best laundry room organization," "declutter laundry room," "how to organize a laundry room cabinet/closet," "how to organize a basement laundry room," all genuine organizing intent, no collision noise.

Shipped `site/articles/how-to-organize-a-laundry-room.html`: the six zones in the order the room's own `content.json` intro gives them (machines first, "every other zone is waiting on" them), each section's facts pulled from the real zone data, not invented, the washer-and-dryer duct-fire warning, the bleach/ammonia and detergent-pod hazards, the hamper fall risk, the iron and drying-rack electrical risks all reused verbatim from the manual rather than written fresh. 2,355 words, 6-question FAQ matching the real query phrasings sampled above, a small-laundry-closet and basement-laundry-room section answering two more sampled queries directly. Primary offer RP-LAUNDRY-RO ($9, 36 cards, confirmed not retired in `ops/retired-skus.json`) plus CN-VIRTUAL; free start link to the washer-and-dryer zone, matching the room's own "where to start" tip. Added `"Laundry Room"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, not hand-edited output) so `/rooms/laundry-room.html` links the guide first in Related reading. Inbound links added from the linen-closet guide and `family-wont-put-things-back`. Wired: `site/articles/index.html` card and JSON-LD list entry (hand-maintained, confirmed no generator owns this file before editing it), `llms.txt` (44 articles, feed 42), sitemap (223, via `build_zone_pages.py`'s own rebuild), feed (42, via `build_feed.py`'s auto-discovery of the new page's dated JSON-LD), share card, `ROADMAP-2026-2029.md` (228).

**A real defect found and fixed, not reported around.** `ops/share_cards.py` failed on the new page: `cannot import name '_imaging' from 'PIL'`. Traced rather than assumed a one-off: this sandbox has two Python installs (3.11 at `/usr/local/bin/python3`, 3.13's own dist-packages pip shadowing it as the bare `pip` command), and the system `PIL` package at `/usr/lib/python3/dist-packages` was a mismatched 10.2.0 against a 3.13-targeted wheel. `pip install` (the bare command) silently reinstalled for the wrong interpreter the first attempt; `python3 -m pip install --force-reinstall --no-deps Pillow` (the 3.11-targeted one) actually fixed it, confirmed by `from PIL import Image` succeeding and the share card drawing (manifest 86 pages, drew 1, failed 0, up from drew 0 failed 1). This was a standing sandbox gap that would have silently failed every future image-dependent check in this specific container, not reported as a limitation because nobody had hit it since the container was provisioned.

**Caught before shipping, not after.** First draft's meta/og/twitter description was 202 characters; `ops/audit_pages.py`'s `desc-long` check (160-char limit) caught it immediately, confirmed against the real limit in the script rather than guessed, rewritten to 156 characters across all four occurrences.

**Verified.** `check_urls.py` 223/223, `audit_pages.py` 228 pages/0 findings, `fix_dashes.py --check` 0 em/en dashes, `fix_dialect.py --check` clean, `affiliate.py --check` 165 documents (unchanged, the new page carries no affiliate link), `check_sellable.py` 124/126 (2 known services, unchanged), `link_graph_report.py` 44 articles/0 orphans (new page's own inbound count: 2, from the room hub and the linen-closet guide). JSON-LD on the new page parses (3 blocks: Article, FAQPage, BreadcrumbList). `grep -i "set in order"` and em/en dash count on the new page: 0 hits each. `ops/audit_visual.py` on the new page, desktop and mobile: 0 findings each, including the touch-target and sideways-scroll checks the mobile pass adds. Both keyword-demand tiers re-scored (no network): US gap/partial/covered 133/1310/1365 to 133/1309/1366 (1 query moved partial to covered); global 100/1003/1067 to 100/1001/1069 (2 moved). `gate_build_id_current` called directly after staging (`git add`): clean. Full `preflight.py --skip-tests` run; result recorded in this same cycle's `ops/NIGHTLY-LOG.md` entry per `CLAUDE.md` 0.4 rather than cited twice here.

**Not done.** No Search Console data exists to confirm this guide earns impressions over the room hub; same unmeasured-bet status sections 71/73/74 already carry. The Pillow fix is local to this container only; a future sandbox provisioned fresh may hit the identical mismatch, and nothing in this repository can fix that permanently from inside a session, so it is recorded here as a known recurring risk rather than closed for good.

## 79. Closed 2026-11-02, scheduled operator cycle: STATUS.md's deploy-verdict citations had drifted behind a newer confirmation again, found by running the standing gate rather than trusting the last cycle's "exhausted" conclusion

Attached onto `main` cleanly after unshallowing (448 commits forwarded, ff-only, tree clean). Every prior cycle today had correctly reported sections 2-6 exhausted and all 30 GitHub issues Phil-gated; rather than re-cite that, ran a full `preflight.py --skip-tests` to genuine completion and read every warning rather than counting them. `gate_status_deploy_verdict_current` warned: `BLOCKER-001`, the "Production Knowledge" paragraph, the "Public website" and "Production traceability" table rows, and the "Currently Deployed Build (last confirmed)" field all still cited `6b6fb70b98ef9333` (or older), while `ops/deploy-verdict.json` had already moved to `b150c19629689ad2`, confirmed 2026-11-01T22:33:43Z. The exact "source corrected, sibling never told" shape this gate exists to catch, found in a file every cycle reads first.

**Verified before fixing, not assumed from the gate's own message.** `site/build-id.txt` reads `b150c19629689ad2` directly; `resolve_verdict_commit('b150c19629689ad2')` resolves to `f66c0df5e`; `deploy_gap_material_commits('f66c0df5e')` against real current `HEAD` returns an empty list. Production matches the repository exactly, zero commits undeployed, no P0 regression: this was a stale citation, not a real deploy gap.

**Fixed all five sections the gate checks**, each with a new dated confirmation citing the real build id and the re-derivation that proves it, in the same "CONFIRMED/CORRECTED, prior state kept because the shape recurs" convention every earlier instance of this same drift has used. Fixing pushed `STATUS.md` from 108792 to 110533 bytes, crossing its own 110000-byte `gate_living_docs_total_size_tripwire` for the first time this cycle; ran `rotate_status_history.py --check-table-rows` (DUE, 2 entries live in each of the Public website/Production traceability rows), applied it (1176 bytes archived to `STATUS-ARCHIVE.md`), confirmed CLEAN after, final size 109357 bytes, under the tripwire.

**Verified.** `status_deploy_verdict_problem()` called directly against the real committed files: empty string, clean. `ops/tests/test_gate_status_deploy_verdict_current.py` 14/14. `fix_dashes.py --check` 0 em/en dashes. `check_urls.py` 222/222, `audit_pages.py` 227/0, `link_graph_report.py` 0 orphans, `affiliate.py --check` 165 documents, `check_sellable.py` 124/126 (2 known services). `cold_read_ledger.py --next` 0 un-ledgered candidates; all 7 `rotate_*.py --check` scripts across both backlogs, `OWNER-ACTIONS.md` and `STATUS.md` CLEAN (table-rows now CLEAN too, post-apply). Both keyword-demand tiers re-scored (no network): byte-identical gap/partial/covered counts to the last recorded state (US 133/1310/1365, global 100/1003/1067), confirming no fresh harvest data exists yet to close a vocabulary gap this cycle. Full `preflight.py --skip-tests` ran to genuine completion, watched by PID rather than assumed: 0 FAIL, 35 warnings, every one already diagnosed in prior cycles (no Stripe/.env.secrets, no SSH deploy key, no mail credential, no DNS query, no local films/images, Etsy fee page 403, `gate_etsy_pdfs_current` and `gate_prerender_shop_current` hit their documented 300s/120s bounds and resolved to WARN rather than hanging). `gate_tests` itself not run this cycle (documented multi-cycle sandbox limitation, already being addressed by the per-file heartbeat section 78 shipped); reported unchecked, not passed, per `CLAUDE.md` 0.4.

No price, product or page touched; no new page, `IndexNow` not applicable. This is the same defect class sections 64-78 have each found once in a different living document; no new gate needed since `gate_status_deploy_verdict_current` already exists and caught it correctly, it was simply never run to completion by a recent cycle before this one.

## 78. Closed 2026-11-02, scheduled operator cycle: `gate_tests()` gained a per-file heartbeat, closing the "cannot tell stalled from slow" gap that forced minutes of CPU-time guessing on every cycle for weeks

**The recurring cost.** For weeks, every cycle that reached `gate_tests` inside `preflight.py` and watched it in the background had to decide "stalled or merely slow" by sampling `/proc` CPU time two or three times over several minutes, because nothing printed between the outer `...gate_tests` heartbeat (`run_gate`'s own fix, `CLAUDE.md`-style, from 2026-09-13) and `gate_tests()`'s own return. `run_gate`'s docstring already names the exact shape of this problem one level up in the gate sequence ("A heartbeat line per gate, flushed immediately... turns the next such run's log into 'reached gate_x, never finished' instead of forcing another blind guess"); `gate_tests()` itself, looping over roughly 130 test files, had the identical blind spot and nobody had closed it there.

**Fixed the mechanism.** Added a one-line, immediately-flushed heartbeat (`  ...test i/N: basename`) printed before each test file's own bounded subprocess call inside `gate_tests()`'s loop. It costs nothing (one `print` per file, same pattern already used for every gate), cannot change any gate's PASS/FAIL/WARN outcome, and turns "CPU time flat for three minutes, no idea which of ~130 files it is on" into "stuck on test file 47 of 130" in the time it takes to read the log.

**Verified.** New `ops/tests/test_gate_tests_heartbeat.py`, fail-then-pass proved directly: reverted the change via `git stash`, confirmed the test goes red (0 heartbeat lines, the slow file's own line missing before its call even returns), restored, reran clean. The three existing `gate_tests`-adjacent tests (`test_gate_tests_timeout_guarded.py`, `test_gate_tests_skip_flag.py`, `test_gate_tests_cycle_signal_checkpoint.py`) all still pass unchanged, and visibly print the new heartbeat lines as a side effect of exercising the real loop. `check_urls.py` 222/222, `fix_dashes.py --check` 0/0. No price, product or page touched; `IndexNow` not applicable.

## 77. Closed 2026-11-02, scheduled operator cycle: the third instance of the title-tie-break class fixed at the root, per `CLAUDE.md` 10b, instead of logged a fourth time

Section 76 named the "grilling station" misattribution as the third instance of the same shape (A25 master-bath, the nightstand-drawers case, this one) and declined to fix the scorer, flagging it "for a future cycle to decide deliberately, with its own review of what reclassifies." This cycle read all three prior accounts (A26, section 75, section 76) before acting, per `CLAUDE.md` 5d, and confirmed the real root cause directly against the live pages: `/zones/patio-or-deck-the-grill-and-outdoor-cooking-zone.html`'s own `<title>` reads "How to organize the patio or deck grill station"; `ops/keyword_demand.py`'s `best_page()` compares exact word forms only, so "grilling" (the query) never equals "grill" (the title), and the tie against the dining room's unrelated beverage/coffee station (which shares only "station") fell to url-alphabetical order, same mechanism A26 already generalised for the room-signal half of this class.

**Fixed the mechanism, not the query.** Per `CLAUDE.md` 10b (three consecutive instances, no gate), added `_morphology_variants()` and `_near_miss_count()` to `ops/keyword_demand.py` and threaded a `cw`/`field` argument through `_tie_break()`, `best_page()` and `best_by()`. Deliberately narrow, matching exactly the two real shapes found so far (a dropped plural, "drawers"/"drawer"; a gerund, "grilling"/"grill"), not a general stemmer: a word's variants are checked only as a tie-break signal when two pages already carry the identical exact-match score, never as part of the score itself. This is the same shape and risk class as A26's own already-shipped fix (a new tie-break criterion, not a scoring change), chosen over touching `words()` directly for the reason section 76 named: `words()` folds every word before scoring, so changing it would move all 4,978 rows' scores at once; a tie-break-only signal cannot move any row's score, by construction.

**Verified the blast radius directly, not assumed.** Snapshotted both `keyword-demand.json` and `keyword-demand-global.json` before the change, re-ran `--rescore` on both (no network) after, and diffed every row: **gap/partial/covered counts are byte-identical in both tiers** (2808: 133/1310/1365; 2170: 100/1003/1067), and a full field-by-field diff confirms **zero rows changed `status`, `coverage`, `heading_coverage` or `room`** across all 4,978 rows. 183 rows (6.5% of the main tier) changed which page is cited in `best_page`/`heading_page` on an exact tie, the cosmetic, internal-report-only field section 75 already established this class affects, never a live gap or a customer-facing claim. Spot-checked a sample: most moved a generic/irrelevant default (`/about.html`, an unrelated article) to the actually-relevant zone page (e.g. "how to organize diapers" now cites the nursery diaper zone instead of `/about.html`; "organize grilling station" now cites the real patio grill page). One new coincidental word-sense collision was found while sampling ("how to organize books at home" now cites `/book.html`, the product page, on a spurious "books"/"book" match against the site's own book title) and is recorded here as a known, accepted residual risk of the same shape A27 already documented for this triage tool ("deliberately crude... a triage score for a human reading the report, not a ranking model"), not chased further.

New test case 19 in `ops/tests/test_keyword_demand.py` (fail-then-pass proved directly: reverted the fix via `git stash`, confirmed the old test's assertion on the real patio/dining titles failed, restored, reran clean), plus a regression guard that the no-near-miss case (case 17's own query) is unchanged and that a double-`s` word ("dress") is never wrongly despluralized. 23 of 23 cases pass.

**Verified.** `check_urls.py` 222/222, `audit_pages.py` 227/0, `fix_dashes.py --check` 0/0, `link_graph_report.py` 0 orphans, `affiliate.py --check` 165 documents, `check_sellable.py` 124/126 (2 known services). `gate_keyword_demand_rescored_current()` and its global sibling, called directly against the post-fix files: both clean. Full `preflight.py --skip-tests` run to completion in the background (one pre-existing stray probe file self-healed by `gate_stray_probe_files`, 0 FAIL otherwise); `gate_tests` itself not run this pass (the documented sandbox hang), reported **unchecked, not passed**, per `CLAUDE.md` 0.4. No price, product or page touched; `IndexNow` not applicable (two measurement files regenerated, no site page changed).

## 76. Closed 2026-11-01, scheduled operator cycle: `ops/keyword-demand.json` (the US tier) had gone stale against the four guide articles sections 71/73/74 shipped the same day, re-derived rather than cited

- **Observation.** All 30 open GitHub issues checked live via the GitHub API: unchanged, every one `decision`/`P0`/`blocked-on-art`, none newly answered. The cold-read ledger (`ops/cold_read_ledger.py --stale`/`--next`) stays fully exhausted at 300 of 300 files, 0 stale. Rotation scripts for all three living-doc size tripwires preflight warned on (`BACKLOG-2026-09-07.md`, `OWNER-ACTIONS.md`, `STATUS.md`) all report CLEAN: every section still within its own retention window, nothing yet eligible to archive, the same "warned but not actionable yet" shape prior cycles already named for this file. With the standing queue genuinely exhausted by every one of those checks, read `ops/keyword-demand.json` cold instead of trusting its own "Scored" line: it still carried `scored_against_commit: 54aeb5632` (18:15:29Z) and 229 pages, while `ops/keyword-demand-global.json` had already been re-scored against the current `HEAD` (230 pages, including the kitchen/garage/workshop guide articles sections 71/73/74 shipped earlier today). The sibling gate `gate_keyword_demand_rescored_current` exists for exactly this and had not yet fired on the next full `preflight.py` pass (sandbox-hung at `gate_tests` before reaching it, same documented shape every recent cycle reports), so this was caught by reading the file directly, not by a red gate.
- **Action.** `python ops/keyword_demand.py --rescore` (free, no network, re-derives coverage against the current site only). 2,808 queries rescored against the current 230 pages: gap 135 to 133, partial 1,317 to 1,310, covered 1,356 to 1,365. Workshop's own partial count fell from 36 to 31, the clearest single mover, consistent with its new guide article and Room-layout heading (sections 74/75) not having been reflected in this file before. `ops/KEYWORD-DEMAND.md` regenerated in the same run.
- **A second, related finding, not fixed.** Verifying the rescore surfaced a live case of the same title-level tie-break class section 75 logged and declined to hand-patch: "organize grilling station" scores to `/zones/dining-room-the-beverage-or-coffee-station.html` ("organize"+"station" match) instead of the real page, `/zones/patio-or-deck-the-grill-and-outdoor-cooking-zone.html` ("How to organize the patio or deck grill station"), because the scorer compares exact word forms with no stemming and "grilling" never equals "grill". Confirmed directly against both pages' real `<title>` tags, not guessed. This is the third instance of the same shape this repository has now found (A25 master-bath, the nightstand-drawers case in section 75, this one), each patched as a one-query content fix rather than at the scorer. Not fixed here either: a stemming or suffix-folding change to `words()`/`_tie_break` in `ops/keyword_demand.py` touches the classification of all 2,808 + 2,170 already-reviewed rows in both tiers at once, a bigger and riskier change than this cycle's own "finish one thing" scope allows, and (as with the nightstand case) the query's own `status` is unaffected (`partial` either way, just attributed to the wrong closest-page). Left for a future cycle to decide deliberately, with its own review of what reclassifies, rather than slipped in as a side effect of a rescore.
- **Verified.** `check_urls.py` 222/222, `audit_pages.py` 227 pages/0 duplicate titles or descriptions, `fix_dashes.py --check` 0 em/en dashes, `check_sellable.py` 124/126 (the 2 known service SKUs), `link_graph_report.py` 0 orphans. `gate_keyword_demand_rescored_current()` and `gate_keyword_demand_global_rescored_current()` called directly against the post-rescore files: both clean, no warning. Full `preflight.py` run in the background; every gate through `gate_image_coverage` and the pre-`gate_tests` `cycle_signal` checkpoint passed with 0 FAIL before it hung at `gate_tests` (CPU time frozen, the documented sandbox shape), so it was killed rather than left running past the point it stopped advancing; reported **unchecked, not passed**, for `gate_tests` itself, per `CLAUDE.md` 0.4. No price, product or page touched; `IndexNow` not applicable (no new or rewritten page this cycle).

## 75. Closed 2026-11-01, scheduled operator cycle: the "workshop layout" vocabulary gap, and a real misattribution found while verifying it

- **Observation.** The global keyword harvest's gap tier (`ops/keyword-demand-global.json`, 102 of 2170 rows) still had "how to plan a workshop layout" and three siblings ("event", "for students", "templates"; gb/au/ca/in) scoring to `/rooms/workshop.html` at only 0.333 coverage, because no page on the site used the word "layout" in any `<h1>`-`<h3>`. Checked `ops/build_zone_pages.py` directly: Kitchen, Nursery and Garage already carry a `"Room layout"` tip rendered as its own heading (A40/A42's own mechanism); Workshop never got one.
- **Action.** Added a `"Room layout"` tip to Workshop in `content/manual/source/content.json`, written from the room's own six zones (Main Workbench, Power Tool Storage, Fastener and Hardware Zone, Material Rack, Finishing and Chemical Zone, Safety and PPE Station), not invented: work outward from the bench, power tools and fasteners within reach of it, the Finishing and Chemical Zone kept clear of Power Tool Storage (solvent fume and a motor's spark), PPE by the door, the Material Rack for whatever is left. Re-ran `ops/build_zone_pages.py` (self-chained generator; `site/rooms/workshop.html` is its output, never hand-edited) and re-synced `mcp/content.json` byte for byte.
- **Second finding, same rescore.** `ops/keyword_demand_global.py --rescore` (free, no network) also surfaced "how to organize nightstand drawers" attributing to `/articles/how-to-declutter-a-kitchen.html` on a coincidental "drawers" word match, not the real one, the Guest Bedroom nightstand zone, which never used the plural "drawers" in a heading (71 uses of the singular "drawer" in body text only). Added `"drawers zone"` to `ops/zone-also-called.json` (measured demand, the established "<word> zone" synonym pattern: A21/A23/A24/A31/A32/A33/A34/A36) so the zone page now carries an honest "Also called the drawers zone" heading. Traced further rather than assumed fixed: the query's top-level `best_page`/`status` field is scored on page TITLE words only (`keyword_demand.best_page`), a separate, earlier-computed field from `heading_coverage`/`heading_page`; both the kitchen page and (for the heading surface) `/downloads/6S-Standards-Pack.html` already tie at the max score on "nightstand"+"drawers" against the nightstand page itself, and the tie-break falls to alphabetical URL order with no room signal in either case, so the top-level attribution did not flip. The query's classification was and stays `covered`, so this is a cosmetic internal-report attribution, not a live gap or a customer-facing defect; the heading addition itself is still real, measured content, left in rather than reverted.
- **Verified.** `check_urls.py` 222/222, `audit_pages.py` 227 pages/0 duplicates, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents clean, `diagnosis.check_all()` 0 problems, `mcp/content.json` byte-identical to the manual source, `ops/tests/test_room_also_called.py` and `ops/tests/test_gate_zone_also_called_is_heading.py` both pass. `ops/keyword_demand_global.py --rescore`: global gap tier 102 to 100 (2 of the 4 workshop-layout queries move gap to partial on a real heading match; "for students" and "templates" stay gap, honestly, since nothing on the page answers them).
- **Not done.** The nightstand-drawers title-level tie-break itself: fixing it would mean editing an already-indexed page's `<title>` tag, a higher-risk SEO change than a heading addition, and the query's classification is unaffected either way (`covered` throughout). Logged here rather than hand-patched, for a future cycle that wants to look at the scorer's title-tie-break class generally rather than one query at a time.

## 74. Closed 2026-11-01, scheduled operator cycle: a step-by-step workshop guide, the strongest tie-score signal in the global and US keyword tiers

- **Observation.** The 18:4x PM check-in handed the operator the next room whose high-rank "organize/declutter" queries tie-score to its own hub page instead of a dedicated guide, naming primary bathroom, laundry room, pantry, entryway, living room, family room, dining room, guest bedroom, guest bathroom, kids bedroom, mudroom, patio-or-deck, stair landing and workshop as candidates with no guide yet. Checked each against both keyword tiers directly rather than guess: workshop carries 31 global and 34 US "organize/declutter" rows scored against `/rooms/workshop.html`, an order of magnitude more than every other candidate combined (stair landing: 1 and 2). Read the actual query text before committing: several workshop rows are the business-event sense ("workshop presentation", "organize meditation workshop", "training workshop"), the same word-sense ambiguity A54-series work already named for "desktop"; excluded those and kept only the physical-space rows ("how to organize a workshop", "small workshop organisation ideas", "garage workshop organization ideas", "how to organize a home/basement workshop", "workshop organization tips"), still the clear largest cluster.
- **Action.** `site/articles/how-to-organize-a-workshop.html`, built from the room's own `content.json` zone data, not invented: safety and PPE station first (30-45 min, the room's own "Where to start" tip, since everything else involves a blade, a solvent or dust), then the main workbench (60-90 min), power tool storage (60-90 min), the fastener and hardware zone (45-75 min), the material rack (60-90 min), and the finishing and chemical zone (45-75 min). Checklist; a "workshop that lives in the garage" section cross-linking the garage guide; a small-workshop section; 7-question FAQ matching the real query phrasings. Total time (5 h to 7 h 45) independently cross-checked against the existing `how-long-does-it-take-to-organise-a-room.html` table's own Workshop row before publishing, not just summed and trusted. Primary offer RP-WORKSHOP ($9, 36 cards; confirmed in the catalog and `check_sellable.py`'s clean 124/126, no live-Stripe-price check possible, no credential in this sandbox) plus CN-VIRTUAL; free start link to the safety station zone page. Added `"Workshop"` to `ops/build_zone_pages.py`'s `ROOM_GUIDES` (self-chained generator, not hand-edited output) so `/rooms/workshop.html` links the guide first in Related reading, the same hub-and-how-to pattern as sections 71 and 73. Inbound links added from the basement, attic and garage guides (the garage guide's own workbench step now also points here, for the workshop that shares a garage). Wired: index (card tile + JSON-LD list), llms.txt (43 articles, feed 41), feed (41 entries, confirmed by rerun), sitemap (222 URLs, confirmed by rerun), share card (drawn and auto-wired, 0 manual edits needed), build-id (current after the chain).
- **Verified.** `check_urls.py` 222/222, `audit_pages.py` 227 pages/0 duplicates, `fix_dashes.py --check` 0/0, `fix_dialect.py --check` clean, `affiliate.py --check` 165 documents clean, `link_graph_report.py` 0 orphans across 43 articles (min 3 inbound, this page included), `check_sellable.py` 124/126 (unchanged), `ops/audit_visual.py` on the new page plus the three edited pages, desktop and mobile: 0 findings each. JSON-LD on the new page parses (3 blocks: Article, FAQPage, BreadcrumbList). `grep -i "set in order"` on the new page: 0 hits. Full `preflight.py --skip-tests` run; result recorded in the same cycle's `ops/NIGHTLY-LOG.md` entry rather than cited here, per `CLAUDE.md` 0.4.
- **Not done.** No keyword rescore: this is the hub-and-how-to pattern (a second, sequenced page for an existing intent already judged `covered`/`partial`), not a vocabulary-gap fix, so `keyword_demand.py --rescore` is not the applicable check here, the same distinction section 71's own correction drew. Whether this guide earns impressions over the room hub needs Search Console (`OWNER-ACTIONS.md` item 1a, Phil-gated); until then this is an unmeasured bet, same as sections 71 and 73.

## 73. Closed 2026-11-01, owner-invoked CEO cycle: a step-by-step garage guide

- **Observation.** Same shape as section 71: "how to organize a garage full of stuff", "full of tools", "very messy garage", "declutter a garage quickly", "simple way to declutter garage for beginners" (ranks 1 to 6) match `/garage-deck.html` on a tie with `/rooms/garage` ("How to organize a garage, zone by zone"); same intent bet as section 71. To make the two page types a hub and its how-to rather than competitors, `ops/build_zone_pages.py` now carries `ROOM_GUIDES`: the kitchen, garage, primary bedroom, hall closet, nursery and home office room pages each link their step-by-step guide first in Related reading.
- **Action.** `site/articles/how-to-organize-a-garage.html`: three driveway areas plus a hazardous-waste box; floor first; then the overhead bins, sports gear, tools and batteries plus workbench, garden tools and chemicals, car supplies; put back by frequency; checklist; very messy garages; 7-question FAQ. Times from the zone pages (whole garage 6 h 45 to 10 h 15, matching the how-long article). Safety claims kept local-rule-aware (dried latex paint, stain-soaked rags, damaged lithium packs). Primary offer RP-GARAGE ($9, link verified active) rather than the house pack, plus CN-VIRTUAL. Inbound from the basement, attic and kitchen guides. Wired: index, llms.txt (42), feed (40), sitemap (221), share card, ROADMAP (226), RISKS forms_dead=226.
- **Verified.** See the commit; production checked after the automatic deploy.

## 72. Closed 2026-11-01, scheduled operator cycle: the same "item has an issue, or should, but the item itself cannot say so" gap found twice more, now gated

- **Observation.** Checking whether the 2026-10-31 sweep (issues #43-48) had actually closed the "owner item invisible to Phil" defect class, found it had not: it filed the issues but never wrote the backlink back into OWNER-ACTIONS.md itself for four of the six (items 1, 1b, 5, 6), so the issue existed and nobody reading the item could find it. Reading the rest of the file by the same method found thirteen more open, numbered items that had never been filed at all: a CRITICAL, unmitigated risk split across two items (1g, 13, RISK-0011, the product masters' single point of failure), one live security exposure (item 8, two public ports open to the internet with no firewall), and six genuine distribution/decision items (11, 16, 17, 18, 21, 22) including the ROADMAP G2 gate test (item 17), never ranked anywhere Phil would see them.
- **Action.** Filed 8 new GitHub issues (#49 RISK-0011, #50 the two ports, #51 the vertical zone videos, #52 Pinterest/Instagram, #53 the G2 local demand test, #54 Facebook/X, #55 the MCP endpoint decision, #56 the photos API deploy decision), each `decision` and `P0` where it is a trust/safety or revenue-blocking item. Added a one-line backlink into all thirteen items' own OWNER-ACTIONS.md sections (1, 1b, 5, 6, 7, 7a, 8, 11, 13, 16, 17, 18, 1g, 21, 22), including the four from 2026-10-31 that never got one.
- **Gated.** New `owner_actions_untracked_items()`/`gate_owner_actions_items_tracked()` in `ops/preflight.py`: every open, numbered OWNER-ACTIONS.md heading (a bare "N." or "Na.", not struck through, not already marked done) must cite "issue #" somewhere in its own section, warned by name otherwise. Deliberately narrow (never matches a narrative subsection heading) and deliberately a WARN, not a FAIL, since an untracked item is a visibility gap, not a wrong claim, and several remaining low-urgency items (2, 4, 4b, 19, 20, and a second, differently-numbered "1b" later in the file, a pre-existing numbering collision this gate correctly treats as its own item) are left for a future cycle rather than forced into an issue today. `ops/tests/test_gate_owner_actions_items_tracked.py` (7/7), fail-then-pass proved directly: the real committed file before this cycle's own fix flagged item 7 (Listmonk) by name; after, it does not, and items 14/15/1/6/8/16 are all confirmed clean.
- **Verified.** `python3 -c "import ast; ast.parse(...)"` confirms `preflight.py` still parses. `fix_dashes.py --check` on every touched file: 0/0. `check_urls.py` 219/219, `audit_pages.py` 224/0 duplicates, `affiliate.py --check` 165 documents clean. `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty. No price, product or site page touched; not customer-facing; `IndexNow` not applicable.
- **Not done.** The remaining 9 untracked items this gate itself now names (1b "deploy yourself", 1c, 1d, 1e, 2, 4, 4b, 19, 20) are left exactly as flagged, deliberately: none is revenue-blocking or a trust/safety risk the way the thirteen above were, and filing an issue for every one of them in a single cycle would be noise, not triage. A future cycle can close them one at a time against this same gate's own WARN.

## 71. Closed 2026-11-01, owner-invoked CEO cycle: a step-by-step kitchen declutter guide, and the deploy verdict step proven

- **Observation.** `ops/keyword-demand.json` has "how to declutter a kitchen" at rank 1 plus counter, countertop, kitchen-table and cabinet variants (ranks 1 to 4). The scorer calls them `covered` or `partial`, by the Kitchen deck on a tie with `/rooms/kitchen` ("How to organize a kitchen, zone by zone"). So this is NOT an uncovered gap: it is a different intent (a sequenced declutter of the whole room) from the zone hub, and the bet is that a step-by-step page matches it better. Checked later the same cycle: a "deck strictly beats every guide" tier holds only 2 rows, so the PM check-in's "gap lane exhausted" reading was right on the scorer's terms; the scorer change that tested it was reverted rather than shipped on a false premise.
- **Action.** `site/articles/how-to-declutter-a-kitchen.html`: a basket, a box and a trash bag; counters, sink and under-sink, drawers (90-150 min, summed from the zone session times) as session one; upper cabinets, lower cabinets, fridge (135-210 min) as session two; checklist; small kitchen and kitchen-table section; 7-question FAQ; PACK-HOUSE plus CN-VIRTUAL band. Inbound from the bedroom guide, the junk drawer guide, `where-to-start-decluttering` and `why-is-my-house-always-messy` (through `ops/build_messy_article.py`). Wired: index, llms.txt (41), feed (39), sitemap (220), share card, ROADMAP (225), RISKS forms_dead=225.
- **Also proven.** The `deploy.yml` step added in `4eb1acbb1` ran on its first site push: `github-actions` committed `2b591aedf` (verdict current at `6b6fb70b98ef9333`), and since `ops/` does not trigger publish-image there was no loop.
- **Verified.** check_urls 220/220, audit_pages clean, dashes, affiliate, preflight gates except tests and generator ownership, 390px render.
- **Measure.** Whether either guide earns impressions for its cluster over the room hub needs Search Console (OWNER-ACTIONS 1a); until then this is an unmeasured bet.

## 70. Closed 2026-11-01, scheduled operator cycle: `gate_living_docs_total_size_tripwire` refired on this file itself, closed section 1b's own uncovered growth and tightened the closed-section retention a second time

- **Observation.** A fresh `python ops/rotate_backlog_closed.py --check` and `gate_living_docs_total_size_tripwire` call, re-derived directly rather than cited, put `BACKLOG-2026-09-07.md` at 167,753 bytes against its 150,000-byte ceiling even though `rotate_backlog_closed.py`, `rotate_backlog_done_items.py`, `rotate_backlog_section2_items.py` and `rotate_backlog.py` all reported CLEAN: every section they cover was within its own retention window, confirming this needed an editorial trim of still-uncovered content, not a mechanical re-run.
- **Found, not assumed.** Measured each live section's own byte span directly rather than guess which one was large: section 1b, "Measured this week, awaiting a decision," was 12,106 bytes, every one of its nine bold-led paragraphs already RESOLVED, Done or CLOSED (dated 2026-09-15 through 2026-10-14, 18 to 47 days old), and no rotation tool had ever covered it; `rotate_backlog.py`'s own docstring only ever claimed section 1's flat table, `rotate_backlog_section2_items.py`'s only section 2's table rows. The same unbounded-growth shape as both, a third time, just free prose instead of a table row.
- **Action.** Built `ops/rotate_backlog_section1b_items.py`, grouping section 1b's paragraphs by their own leading bold-span date (a dated paragraph starts a new group; an undated paragraph joins whichever group is open, since several of this section's own conclusions carry no date of their own) rather than assuming one paragraph equals one item. Ran `--apply`: 6 groups, 12,054 bytes, moved verbatim into the new `BACKLOG-2026-09-07-SECTION1B-ARCHIVE.md`, each replaced live by a single pointer paragraph carrying its own original bold lead sentence, the same convention `rotate_backlog_section2_items.py` already uses. New `gate_backlog_section1b_items_rotated` wired into `preflight.py`'s `main()`, mirroring `gate_backlog_section2_items_rotated` (retention plus a 7-day buffer, WARN not FAIL); `ops/tests/test_gate_backlog_section1b_items_rotated.py` (5/5) proves it, and the gate was deliberately broken and watched fail before being restored, per CLAUDE.md step 10b's "a gate that cannot fail is theatre."
- **Second action.** Even after section 1b's fix the file was still over ceiling: the closed-section chain (sections 54-69, 45,380 bytes) was entirely inside `rotate_backlog_closed.py`'s 4-day window set by section 66's own fix six days ago, because the closure rate kept climbing (16 sections in 4 days this time, versus the 51-in-14-days that justified 4 days in the first place). Lowered `DEFAULT_RETENTION_DAYS` from 4 to 2, by the same arithmetic section 66 used: live content outside the closed chain and section 1b runs about 110,267 bytes, so a closed-section budget above roughly 40,000 bytes reopens the tripwire, and 2 days settles near 19,000, a real buffer rather than a razor's edge. Ran `--apply`: 9 sections (54-62, 26,521 bytes) moved into `BACKLOG-2026-09-07-CLOSED-ARCHIVE.md`; sections 63-69 stay live.
- **Verified.** `BACKLOG-2026-09-07.md` now 130,559 bytes, re-confirmed directly, not cited. `gate_living_docs_total_size_tripwire`, `gate_backlog_closed_sections_not_oversized`, `gate_backlog_done_items_rotated`, `gate_backlog_section2_items_rotated`, `gate_backlog_section1b_items_rotated` and `gate_backlog_gemini_cost_current` all called directly against the real committed file: 0 FAIL, the only standing WARN is the pre-existing, untouched `OWNER-ACTIONS.md` 123,276-byte tripwire (section 66's own deliberate deferral, needs its own editorial pass, not touched this cycle). `ops/tests/test_rotate_backlog_closed.py` (8/8) and `test_gate_backlog_closed_sections_not_oversized.py` (5/5) both re-ran clean against the lowered default, confirming section 66's own fix (deriving the test's buffer window from the module's `DEFAULT_RETENTION_DAYS` at import time) still works unmodified. `fix_dashes.py --check` on every touched file: 0/0. `check_urls.py` (219/219), `audit_pages.py` (224/0 duplicates), `affiliate.py --check` (165 documents), `check_sellable.py` (124/126), `cold_read_ledger.py --stale` (0) all clean after. A grep across the repository for the archived section numbers (54-62) by name found only historical `STATUS-ARCHIVE.md` citations of commits, which point at a commit hash, not a live section, and stay valid either way. 16 open GitHub issues checked live via the MCP tool, same set as every cycle since 2026-10-31T21:00:15Z, all `decision`/`P0`/`blocked-on-art`, none mine. `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty.
- **Not done.** A full, unbackgrounded `python ops/preflight.py` run (the only way to reach `gate_tests` itself) was started in the background and killed by the harness's own background-task limit before it could flush any output, the same documented sandbox wall most cycles today hit; not reported as a pass. Every gate this cycle's own change touches was instead run directly and individually, confirmed clean above, which is narrower than a full run but is not a guess. Not deployed: no operator sandbox holds the deploy key (`VPS_DEPLOY_KEY`, issue #35); the standing 41-commit gap in `BLOCKER-001` is unaffected by this cycle's tooling-only change (no `site/**` file touched). No price, product or site page touched; not customer-facing; `IndexNow` not applicable.

## 69. Closed 2026-11-01, PM check-in: `affiliate.py --check` and `check_sellable.py` now bootstrap their own fresh-sandbox gap, so a standalone run cannot misread it as a content regression

- **Observation.** A standalone `python ops/affiliate.py --check` in this cycle's fresh container FAILed: "could not read 3 delivered document(s)", and `python ops/check_sellable.py` FAILed separately: "120 name a file that is not built". Both were a cold start, not a real defect: `pymupdf` was never installed into the interpreter this container actually runs (a `pip`/`python3` version mismatch, not the pinned package missing from `ops/requirements.txt`), and `build/products/` had never been generated. `ops/preflight.py` already carries an unconditional `bootstrap_fresh_sandbox()` fix for exactly this pair, with its own docstring naming at least seven prior nightly-log entries that hit it before that fix landed. That fix only runs inside `preflight.py`; it never covered a standalone run of either narrow script, which is the exact pattern most PM/operator cycles use ("ran checks directly instead of trusting... check_urls.py, affiliate.py --check").
- **Chased, not just logged.** Installed `pymupdf==1.28.2` with the correct interpreter's `pip` (`python3 -m pip install`, not the bare `pip` on this container, which was bound to a different Python) and ran `ops/build_catalog.py --build`; both checks then reported the real, historically consistent numbers: `affiliate.py --check` 165 delivered documents clean, `check_sellable.py` 124 of 126 buyable products confirmed deliverable. No content regression existed; the long-running "165 documents clean" citation across weeks of log entries is genuine, not a copied, unverified number.
- **Action.** Added a small `_bootstrap_fresh_sandbox()` to both `ops/affiliate.py` (`check()`) and `ops/check_sellable.py` (`main()`), mirroring `preflight.py`'s own proven fix at smaller scope: install `pymupdf` from `ops/requirements.txt` if it is not importable, build `build/products/` if the directory is missing. Both run unconditionally, idempotent, side-effect free.
- **Verified.** Simulated a fresh sandbox (`rm -rf build/products`) and reran both scripts standalone: both self-heal and report the same clean numbers as above, with no manual pip install or build step first. `ops/tests/test_affiliate.py`, `ops/tests/test_check_sellable.py`, `ops/tests/test_check_sellable_excluded_note.py` all pass. `fix_dashes.py --check` on both edited files: 0/0. `check_urls.py` 219/219, `audit_pages.py` 224/0, `cold_read_ledger.py --stale` 0, backlog unchecked rows 0. No price, product or page touched; tooling-only fix, not a content change; IndexNow not applicable.
- **Not done.** `ops/preflight.py`'s own `bootstrap_fresh_sandbox()`/`ensure_pymupdf()` were left untouched rather than refactored into a shared module the three files import, because that refactor touches a 31,000-line gate file for a cosmetic de-duplication, higher regression risk than the three functions it would save; revisit only if a fourth script hits the same trap.

## 68. Closed 2026-11-01, scheduled operator cycle: re-derived a stale deploy-gap count and fixed a gate that had gone blind to its own target row

- **Observation.** A full `preflight.py` run (every gate reached, including `gate_tests`, backgrounded rather than killed at the documented sandbox timeout) came back clean except two real, fixable warnings: `gate_status_deploy_gap_count_current` and `gate_status_table_rows_gap_count_current` both flagged that `STATUS.md`'s cited deploy gap (39 commits, 32 content) had gone stale against a fresh recount. A third warning, `gate_backlog_gemini_cost_current`, said it could not find section 6's Gemini-billing row at all.
- **Action, part one.** Re-derived the real gap directly (`deploy_gap_material_commits(resolve_verdict_commit('a0bbe5bb276ee21b'))` against real current HEAD): 41 commits, not 39. Two new since the last entry: `3f474d85c` (A51, a Pantry Baking Zone synonym, content) and `b90efa242` (a sitemap-lastmod drift fix, mechanical). Updated BLOCKER-001's own entry and both section-1 table rows (Public website, Production traceability) to the real count; all three gates re-run directly against the edited file and confirmed clean.
- **Action, part two.** Found why the Gemini-billing gate went blind: its regex required the row's bold span to close immediately after the word "billing" (`\*\*Gemini billing\*\*`), and the real row had grown a trailing period inside the bold span (`**Gemini billing.**`) when issue #47 was filed against it on 2026-10-31, a punctuation change with no effect on meaning that nonetheless broke an exact-match regex. Widened to `\*\*Gemini billing[.:]?\*\*`. Proved fail-then-pass: the old pattern does not match the real row's text (confirmed directly in Python before editing), the new one does; two new regression test cases added to `ops/tests/test_gate_backlog_gemini_cost_current.py` reproducing the real period-bearing shape (8/8 checks pass).
- **Verified.** All four gates (`gate_status_deploy_gap_count_current`, `gate_status_table_rows_gap_count_current`, `gate_status_latest_entry_gap_current`, `gate_backlog_gemini_cost_current`) called directly against the real committed files: 0 FAIL, 0 WARN. `check_urls.py`, `fix_dashes.py --check`, rotation scripts all re-confirmed clean the same cycle. No price, product or site page touched; no new page, IndexNow not applicable.
- **Why this matters more than the fix itself.** Both defects are the same shape this file's section 7 names as the dominant defect class: a source changed (a git log that kept moving, a row that gained one character) and a sibling artifact describing it was never re-derived. Neither defect was a new bug in the underlying facts; both were a check quietly going blind to drift it exists to catch. Fixing the gate, not just the one stale number, is what stops this specific recurrence.

## 67. Closed 2026-10-31, owner-invoked CEO cycle: a step-by-step bedroom declutter guide

- **Observation.** About 20 queries in the two harvests ask how to declutter a bedroom step by step, in one day, fast, or with a checklist; they had matched `/disclaimer.html`, `sentimental-items-without-guilt` and `everyday-things-out-of-reach`. The "why" intent is already answered by `why-is-my-house-always-messy` (it has a bedroom section), so this page takes the "how" intent only, to avoid a duplicate.
- **Action.** `site/articles/how-to-declutter-a-bedroom.html` (`5eaabc827`): three bags and a basket, then floor, bed, surfaces, nightstands, dresser top, and the basket emptied once; about two to three hours, from the primary bedroom zone session times (bed 30-45, nightstands and dresser top 15-30 each); drawers and closet (60-90 each) as their own sessions; checklist; very messy rooms in timed rounds; children's rooms; nightly two minutes. 7-question FAQ, PACK-HOUSE plus CN-VIRTUAL band. Inbound links from `where-to-start-decluttering` (hand-written) and `why-is-my-house-always-messy` (through its generator, `ops/build_messy_article.py`, not a hand edit). Wired: index, llms.txt (40), feed (38), sitemap (219), share card, ROADMAP (224). RISKS forms_dead=224 (tree-derived, accepted since `71a5f721d`).
- **Verified.** check_urls, audit_pages (224/0), dashes, affiliate, 14 wiring gates, 390px render.
- **Not done.** Deploy and measurement, as BLOCKER-001's newest entry states.

## 66. Closed 2026-10-31, scheduled operator cycle: `gate_living_docs_total_size_tripwire` warned on three living documents at once, the first genuinely unblocked row in two weeks

Preflight was the only item this cycle found. A fresh real run (not the cached `cycle_signal.py` snapshot) surfaced `gate_living_docs_total_size_tripwire` warning on `CHECKIN-LOG.md` (276,869 bytes against a 110,000 ceiling), `OWNER-ACTIONS.md` (123,276 against 110,000), and `BACKLOG-2026-09-07.md` itself (313,175 against 150,000). Every per-file rotation tool reported CLEAN against its own retention window first: nothing was stale by date, the files were simply oversized at their steady, in-window volume.

**CHECKIN-LOG.md.** Measured the real shape before changing anything: 632 hourly entries spanning exactly 30 days, roughly 440 bytes each, so the file's own 30-day default retention settles near 316KB by arithmetic alone, regardless of staleness. Lowered `ops/rotate_checkin_log.py`'s `DEFAULT_RETENTION_DAYS` from 30 to 8 (leaves roughly 90 to 100KB, a two day buffer under the tripwire) and ran `--apply`: 425 entries, 186,351 bytes moved verbatim into `CHECKIN-LOG-ARCHIVE.md`. Live file now 90,518 bytes.

**BACKLOG-2026-09-07.md.** The "## N. Closed" sections (then 15 through 65, 213,536 bytes of the file's 313,175) were all dated inside `ops/rotate_backlog_closed.py`'s 14 day window, because the operator cadence has been closing roughly one section a day. Lowered that script's `DEFAULT_RETENTION_DAYS` from 14 to 4 and ran `--apply`: 38 sections moved verbatim into `BACKLOG-2026-09-07-CLOSED-ARCHIVE.md`. Live file now 138,198 bytes, under its 150,000 ceiling.

**OWNER-ACTIONS.md, deliberately not touched.** Its own preamble and closed-item rotation tools both already reported CLEAN (357 bytes live in the preamble, no fully closed items left), so the remaining 123,276 bytes are the "Open, ranked by what they unblock" section itself, cold read directly rather than assumed: 12 genuinely open, non duplicate owner decision items, several with long measured histories Phil still needs (traffic numbers, dated corrections, step by step account creation instructions). No safe, information preserving rotation candidate was found. Hand trimming real content Phil has not yet acted on would risk exactly the information loss CLAUDE.md warns against, so the warning was left standing rather than silenced; it needs a dedicated editorial pass with time to verify what is genuinely redundant, not a blind cut inside this cycle.

**Verified.** Both changed scripts' own test suites pass (`test_rotate_checkin_log.py`, `test_rotate_backlog_closed.py`). Found two sibling gate tests broken by the same edit: `test_gate_checkin_log_not_oversized.py` and `test_gate_backlog_closed_sections_not_oversized.py` had hardcoded day offsets (36, 40, 20) assuming the old 30 day and 14 day defaults, so they failed the instant the default changed under them. Fixed both to derive their buffer window from the module's own `DEFAULT_RETENTION_DAYS` at import time instead of a hardcoded number; reran, 4/4 and 5/5 pass. Reran `gate_living_docs_total_size_tripwire` directly: silent on `CHECKIN-LOG.md` and `BACKLOG-2026-09-07.md`, still warns on `OWNER-ACTIONS.md` exactly as expected. Ran the real `python ops/preflight.py` to completion of every reachable gate: 0 FAIL/ERROR, 4 warnings, all pre-existing and already documented (CI conclusion unchecked in this sandbox, the `OWNER-ACTIONS.md` tripwire above, two standing honest disclosures, gitignored source images), stalled only at the documented `gate_tests` sandbox hang. `ops/affiliate.py --check`: 165 documents clean. `fix_dashes.py --check` on every changed file: 0 em or en dashes. No price, product or page touched; tooling-only fix, not a content change; IndexNow not applicable.

## 65. Closed 2026-10-31, scheduled operator cycle: generalised the "a pure gate sits after `gate_tests` and never gets verified locally" class, instead of relocating a third individual gate

Epics 1 through 5 were independently re-confirmed exhausted this cycle before picking this up: re-read all 138 rows of `ops/keyword-demand-global.json`'s gap tier directly (not a prior cycle's citation), none clear the real-synonym bar A29-A36 established, same conclusion several cycles already reached; `checks.yml`/`publish-image.yml` both green on `main`; decks and images/video sections 3-4 all Done or Phil-gated (C5, C6); 10 GitHub issues unchanged since 2026-10-25, 0 Phil replies. Sections 38 and 64 above each relocated one gate (`gate_owner_actions_last_measured_current`, then `gate_build_id_current`) ahead of `gate_tests` after it went red in CI, because both are pure, no-browser, no-network checks sitting behind this sandbox's own ~90-minute `gate_tests` cost (measured directly, ops/NIGHTLY-LOG.md 2026-10-28), unreachable by any run shorter than that. Roughly 300 other gates sit in the identical position today, each one gap-build-id-current away from its own CI-red incident. Relocating gates one at a time only ever fixes the one that already broke.

**Fix.** Added a real `--skip-tests` flag to `ops/preflight.py`: `gate_tests(skip=True)` WARNs by name ("skipped via --skip-tests...") and returns without globbing or running a single file, so a run can decline the suite's own real cost on purpose and still execute every gate after it in the same pass. `main()` reads `"--skip-tests" in sys.argv`, passes it through `run_gate(gate_tests, skip_tests)`, and the end-of-run `cycle_signal` recording branches on it so a `--skip-tests` run is stored with an honest "near-full pass... test suite itself not run this pass" note rather than the plain "clean pass" note a real full run gets; `--check` elsewhere must not be able to read a skipped suite as equivalent to a verified one.

**Verified directly, not assumed.** New `ops/tests/test_gate_tests_skip_flag.py`: skip=True never calls `glob.glob` (patched to raise if it did) and records exactly one WARN; skip=False/default is byte-identical to the pre-existing behaviour (still globs, stays silent on zero test files); main()'s source actually wires the flag through and branches the cycle_signal note. Fail-then-pass proved directly: stashed the `preflight.py` fix and reran the new test, got a clean `TypeError` failure naming the missing parameter; restored, reran clean. Two existing ordering tests (`test_gate_no_stray_probe_files.py`, `test_gate_tests_cycle_signal_checkpoint.py`) pin the literal call-site string `"run_gate(gate_tests)"`; updated both to the new `"run_gate(gate_tests,"` marker and reran, both still pass, same for `test_gate_owner_actions_last_measured_current.py`/`test_gate_ci_conclusion_current.py`/`test_gate_nightly_log_ordering.py`/`test_gate_tests_timeout_guarded.py`, which already matched on the shorter, unaffected prefix. Then ran the real thing: `python ops/preflight.py --skip-tests` end to end in the background, not sampled, finished in about 4 minutes (vs. ~90 for the real suite) and reached literally every one of the roughly 300 gates after `gate_tests` for the first time any local run in this sandbox has: **0 FAIL, 39 warnings, all pre-existing and documented** (no Stripe/ssh/mail credential, no local narrated films, Etsy's fee page returns 403 to this sandbox). `ops/cycle-signal.json` correctly recorded the honest near-full-pass note, confirmed by reading the committed file, not the console line (which prints the same literal text either way). `fix_dashes.py --check` on every changed file: 0 em/en dashes. `ops/cold_read_ledger.py --add ops/preflight.py --status fixed` recorded this read (the file had gone stale against the ledger after today's A34/section-64 build-id fix).

**Not done.** The ~300 gates themselves were not individually re-audited for whether each one is actually safe to run before `gate_tests` has executed (none appeared to depend on it this run, since all 300 ran clean), only proven reachable; a future cold read could still find one that assumed something upstream. No price, product or page touched; tooling-only fix, not a content change; IndexNow not applicable.

## 64. Closed 2026-10-31, scheduled operator cycle: CI red on main after A34, `gate_build_id_current` moved ahead of the sandbox hang, the same fix section 38 already applied once to a different gate

A34's own commit (`d403f144b`) edited a zone page's content without regenerating `site/build-id.txt`, so `checks.yml` failed `gate_build_id_current` even though preflight passed every gate it could reach locally. Not a new mistake: `MARKETPLACE-LISTINGS.md`'s CI history (run `41144124451`, 2026-10-30 23:0x) shows A33 hit the identical failure the cycle before, and A32 (`41114691751`, 2026-10-30 19:2x) the cycle before that, three in a row. The gate itself is correct and has caught every one of the three; what is wrong is its position, after `gate_tests` in `preflight.py`'s own run order, and `gate_tests` hangs on headless Chromium in this sandbox on every single run, so no local pass before push can ever reach it, the exact shape section 38 already fixed once for `gate_owner_actions_last_measured_current`. Moved `gate_build_id_current` to run alongside it. Regenerated `site/build-id.txt` with `ops/build_id.py`, verified `m.current() == m.compute()` directly, and proved the gate still fails on a planted stale hash and passes clean on the real one at its new position. `fix_dashes.py --check` 0/0. No price, product or page touched; tooling-only fix, not a content change.

## 63. Closed 2026-10-30, scheduled operator cycle: CI red on main, the `gate_nightly_log_ordering` gate caught a real append-not-prepend mistake exactly as built

Preflight (`--fast`, backgrounded) and `checks.yml`'s own most recent completed run (`40996971909`, commit `d67b10942`) both failed `gate_nightly_log_ordering`: the 03:0x PM check-in's own entry had landed appended after `ops/NIGHTLY-LOG.md`'s legacy 2026-10-16 tail instead of prepended under today's other entries, entry #982 of 982, 2.4MB from where "read the last four entries" (this operating prompt's own step 1) would look. Same misreading-of-"last" shape the gate's own docstring already names from 2026-09-05. Cut the misplaced entry from the end and prepended it under the file's header, byte-identical content, no rewording; re-ran `gate_nightly_log_ordering()` directly (clean) and its own test file (`ops/tests/test_gate_nightly_log_ordering.py`, 8/8). No new gate needed: the existing one did exactly its job, on the first push after the defect landed, in both preflight and CI. `check_urls.py` (218/218), `audit_pages.py` (223/0 duplicates), `fix_dashes.py --check` (0/0), `affiliate.py --check` (165 documents), `cold_read_ledger.py` (298/298, 0 stale, 0 un-ledgered), all 8 `rotate_*.py --check` scripts CLEAN, `check_sellable.py` (124/126, the 2 known service SKUs), `b9_claims.py --status` (zero rooms undiagnosed), `link_graph_report.py` (0 orphans), mobile `npm test` (4 suites) all clean after. `preflight.py --fast` hung at the documented `gate_tests` sandbox limit as every recent cycle; killed after 155s, reported unchecked for that gate, not passing; CI's own GitHub-hosted runner is the real coverage for it and will confirm or fail on this push. GitHub: 10 open issues unchanged (8 decision, 2 blocked-on-art), 0 open PRs. No price, product or page touched; IndexNow not applicable.

## 62. Closed 2026-10-29, owner-invoked CEO cycle: a linen closet guide, and `gate_risks_evidence_current` stopped failing the build on every new page

- **Observation.** The linen-closet cluster across both harvests is about 90 queries, 41 of them partial ("how to organize a small linen closet", "linen closet organization deep shelves / sheets / systems / labels", "how to organize towels without linen closet"), nearly all landing on the hall-closet linen shelf zone page, which states the standard but not the closet-wide layout, deep shelves, small closets or the no-closet case.
- **Action.** `site/articles/how-to-organize-a-linen-closet.html`: check every set is complete and fits a bed you own, two or three sets per bed (the zone page's standard is three), towels counted by people and laundry, set-in-its-own-pillowcase bundle, shelves arranged by reach, shelf-edge labels carrying bed size and count, deep shelves, small closet, no closet, clean/dry/safe, laundry-day reset and one-in-one-out. 7-question FAQ, PACK-HOUSE plus CN-VIRTUAL band. Title shortened to 58 characters after `audit_pages` title-long (the h1 keeps the longer wording). Wired: articles/index card and hasPart, llms.txt (39 articles, feed 37 of 39), feed, sitemap (218), share card, ROADMAP (223 pages), inbound links from the blanket and baby-clothes guides.
- **Structural fix (`71a5f721d`).** Every new page adds one footer form, so the commit adding a page had to cite `forms_dead` to match either the hourly `ops/state.json` snapshot (stale an hour later) or the tree (failing Checks and publish-image until the hourly run, which failed publish-image this cycle). `tree_derived_state()` in `preflight.py` computes `forms_dead` exactly as `dashboard.py` does, and a citation matching it now counts as current; keys the tree cannot derive still compare to the snapshot only. `ops/tests/test_gate_risks_evidence_tree_derived.py` fails 1/5 without the change, 5/5 with. RISKS.md now cites `forms_dead=223`, matching the tree.
- **Also fixed.** `gate_prerender_shop_current` failed: `site/shop.html`'s pre-rendered grid lacked the " USD" price marks the JS renderer has added since `2140c7f83`, so JS-less crawlers read unmarked prices. Re-ran `python ops/prerender_shop.py`.
- **Not done.** Deploy (refused to this session, BLOCKER-001) and measurement (Search Console export, OWNER-ACTIONS 1a).

## 61. Closed 2026-10-29, owner-invoked CEO cycle: a baby clothes guide, and `article_figures.apply()` stopped failing every Windows checkout

- **Observation.** The baby-clothes cluster in `ops/keyword-demand.json` and the global harvest is about 45 queries ("how to organize baby clothes in drawers / without a dresser / for storage / in totes / for garage sale / in small space"), most of them partial, landing on the nursery clothing zone page, the junk-drawer article or `zone-too-small-for-what-it-holds`. The zone page answers the active drawers; nothing answered the next-size bin, outgrown sizes or storing for a second baby.
- **Action.** `site/articles/how-to-organize-baby-clothes.html` (c7cb03eb3): sort by the label not the look, count by laundry cycle, one size per labeled drawer filed upright, closet size dividers, no-dresser options, next-size bin, outgoing bag with destinations, storing (washed, dry, clear lidded bins, no mothballs), nursery safety (anchor the dresser, hood and neck drawstrings, empty crib per AAP, supplies out of reach), sustain. 7-question FAQ, PACK-HOUSE plus CN-VIRTUAL band. Wired: articles/index card and hasPart, llms.txt (38 articles, feed 36 of 38), feed, sitemap (217), share card, ROADMAP (222 pages), inbound links from toys and zone-too-small. RISKS forms_dead and the derived `ops/state.json` forms_dead both 222 (recomputed from the tree exactly as `dashboard.py` does, so `gate_risks_evidence_current` does not fail the image build until the hourly run catches up, which broke publish-image last cycle).
- **Fix found on the way.** `gate_article_figures_current` failed locally on 4 to 7 articles that were in fact wired: `article_figures.apply()` inserted its block with bare LF, so on a CRLF (autocrlf) checkout apply(src) never equalled src. Same LF round trip as `share_cards.apply()`; `ops/tests/test_article_figures_crlf.py` fails without it and passes 4/4 with it. CI on Linux was never affected.
- **Verified.** check_urls (217 resolve), audit_pages clean, fix_dashes clean, affiliate check clean, build id current, every preflight gate except `gate_tests` (documented local hang) passes apart from the expected generator-ownership "commit first" and size-tripwire warnings, 390px render clean.
- **Not done.** Deploy (refused to this session, BLOCKER-001), and measurement: whether any of these guides gets impressions needs the Search Console export (OWNER-ACTIONS 1a).

## 60. Closed 2026-10-29, owner-invoked CEO cycle: a home paperwork guide, and `share_cards.py --wire` stopped stacking stray carriage returns

**Observation.** "How to organize a home office filing system" is rank 1 in both `ops/keyword-demand.json` and the global harvest, and "paper files at home", "papers at home", "your paper files", "ways to organize papers" and "papers to keep" were all partial, several matched to the hall closet's paper-towel backstock page. Separately, while wiring section 59, `2404a870c` was found to have committed two bare CRs per page into three articles: `share_cards.apply()`'s `_EXTRA` regex strips `
<meta ...>` but not the CR before it, so every `--wire` run on a Windows (`core.autocrlf=true`) checkout stacked them.

**Action.** `/articles/how-to-organize-paperwork` (`c79829238`): three kinds of paper (act, file, keep safe), the dated act folder and fourteen-day rule from the mail article, folders labeled by the question (the file storage zone's own standard), a fire-resistant box for originals, paper versus scan, retention anchored only on the IRS's general three-year guidance with its exceptions named, small spaces, safety, weekly and yearly sustain triggers. Wired into the index, the mail and assigned-home articles, sitemap 216, feed 35, llms.txt, share card, ROADMAP 221, build id. `apply()` now works in LF and returns the page's own endings; `ops/tests/test_share_cards_crlf.py` fails 2/4 without the fix and passes 4/4 with it; the staged tree held no CR in any `site/` or `ops/*.json` blob. Also escaped a docstring regex in `ops/preflight.py` (`bfbf2bd04`) that Python 3.14 flags as an invalid escape on every import.

**Verified.** check_urls 216/216, audit_pages 221/0, 0 dashes, affiliate rules, JSON-LD, FAQ verbatim, 390px render, article gates clean, `test_gate_share_cards_current` still 5/5. BLOCKER-001's gap citation re-derived to 6 commits.

**Not done.** Not deployed, same refusal as section 59.

## 59. Closed 2026-10-29, owner-invoked CEO cycle: a toy organization guide, the next on-topic cluster after blankets

**Observation.** After section 55 and section 57 (`ea437edc0`, the overnight FAQ-gap fix), the largest remaining in-scope cluster in `ops/keyword-demand.json` was toys: 37 queries, 10 at coverage 0.34 or below, among them "how to declutter kids toys", "how to organize a living room with toys" (rank 2), "how to organize toys in cube storage" and "what is the best way to store toys". The two toy zone pages answer the bedroom and family-room bins; nothing answered the living room, rotation, decluttering with a child, or cube storage.

**Action.** `/articles/how-to-organize-toys` (`2404a870c`), on D-031's precedent. Root causes first, a four-pile sort with the child, open low photo-labeled bins (the zone pages' own standard), cube storage, large toys, rotation, living-room containment, small spaces, and a safety block (small parts, button batteries, cracked plastic, tip-over, hinged toy-chest lids). No fabricated figures. Seven FAQ entries verbatim in the visible text. Wired into the index, two related articles, sitemap 215, feed 34, llms.txt, share card, ROADMAP 220, build id. Also stripped stray carriage returns an earlier `share_cards.py --wire` run had committed into two meta lines on three articles (content-neutral).

**Verified.** check_urls 215/215, audit_pages 220/0 (a 170-character description was caught and shortened), 0 dashes, affiliate rules, JSON-LD, FAQ verbatim, 0 broken internal links, true-390px render clean, and the article/feed/llms/share/consult/sitemap/Stripe/deploy-gap gates pass. Full `preflight.py` not run to completion (documented `gate_tests` hang).

**Not done.** Not deployed: `python ops/deploy.py` was refused by this session's permission layer even with Phil's explicit instruction, so it needs a permission rule for that command or `VPS_DEPLOY_KEY`. Numbered 59, not 56, because concurrent cycles took 56 to 58 while this was being built.

## 58. Closed 2026-10-29, scheduled operator cycle: `fail()`/`warn()` in `ops/preflight.py` printed nothing until the end of a run, so a run killed at the documented `gate_tests` sandbox hang could hide a real failure with no trace

**Observation.** The full-completion run section 57 launched hit a real FAIL before reaching `gate_tests` (`maybe_record_cycle_signal`'s own checkpoint reported "not recorded, this run has failing gate(s)"), but which gate and why was invisible: `fail()`/`warn()` only append to a list, and main()'s own report of their contents sits after `gate_tests` in the call order, the exact line this sandbox's documented hang has never once reached. A monkeypatched `fail()` that printed immediately, then a second clean rerun with no code change, showed the FAIL was a transient collision with a concurrent preflight process (pid 1883) holding the run lock, not a real defect in this sandbox's own state, the same collision class sections 18/19/25 already closed for other symptoms. The 05:4x `ops/NIGHTLY-LOG.md` entry independently diagnosed the identical root cause the same hour and named the fix ("`fail()`/`warn()` print immediately when called, not just append"), deliberately leaving it for a cycle with room for a `preflight.py` change.

**Action.** Built the fix that entry named rather than re-diagnosing it: `fail()` and `warn()` now print their line to stderr the instant they are called, matching the heartbeat line `run_gate()` already had for the same silent-hang reason. New `ops/tests/test_gate_fail_warn_print_immediately.py`, fail-then-pass proved by hand (removed the print, watched the test catch it, restored it, watched it pass).

**Verified.** `test_preflight_cycle_signal_record.py`, `test_run_preflight_exit_code.py`, `test_gate_tests_timeout_guarded.py`, `fix_dashes.py --check` all clean after; syntax parsed before running. `gate_nightly_log_ordering`/`gate_nightly_log_no_duplicate_entries`/`gate_nightly_log_not_oversized` run directly against the real files, clean. No price, product or site page touched; not customer-facing, `IndexNow` not applicable.

## 57. Closed 2026-10-29, scheduled operator cycle: the 2026-10-28 16:27 harvest's second-largest real cluster closed, and the rest of its 166 gap rows read and confirmed mostly out of scope

**Observation.** Section 55 closed the blanket cluster from this same harvest but left the other 160+ gap rows unread. Read the full list rather than trusting the count (CLAUDE.md 5c). First, re-scored it against the corpus as it stands now (`ops/keyword_demand.py --rescore`, pure, no network, LRN-0032): "how to store extra blankets" and "ways to store blankets" were still showing `gap` only because the harvest predates section 55's own article by about an hour; rescoring moved them to `covered` and the overall count from 166 to 164, a stale reading rather than a second defect. Of the 164 that remained, the great majority are not this business and this product will not fake being one: computer/game-file organization (hard drives, Steam, Sims 4, PoE2, Dropbox), medical questions (bathroom frequency, adult diapers), construction and woodworking plans (staircases, railings, nightstands, walkways), interior-decor photo intent (foyer design ideas, primary bathroom images), institutional spaces (daycare, classrooms, cribbage tournaments, training workshops), and what reads as autocomplete filler rather than real queries ("declutter gardening series lessons," "explore decluttering pro guide"). The one real, in-scope, unaddressed cluster: "decluttering tips for beginners," "best decluttering advice for beginners," "beginner decluttering kit tips," and "decluttering tips and tricks," four variants on a question this site already answers in substance on `/articles/where-to-start-decluttering`, just not in the words a beginner actually types.

**Action.** Not a new page, per CLAUDE.md 51/11 (improve an existing high-value page, no thin near-duplicate): three new FAQ entries added to `where-to-start-decluttering.html`, each grounded in content already on the page (the friction-minus-effort score, sizing a session honestly, writing the next zone down and resisting the second one) rather than inventing new advice. The "kit" question is answered honestly rather than stretched into a product recommendation: no special kit is needed to start, a bag or box and a timer are enough, matching CLAUDE.md section 3's "do not sell people more stuff merely because they are trying to organize their stuff."

**Verified.** Visible `<h3>`/`<p>` text checked programmatically word-for-word identical to the FAQPage JSON-LD (the same check A13/A14 used), 8/8 pairs. Re-scored after: all four target queries move to `covered`, and the `heading_page` field (not the title-match `best_page` field, which still points elsewhere) confirms the claim honestly, matched on real heading coverage rather than a stale title tie-break. `ops/build_feed.py` and `ops/build_seo.py` rerun for the new content hash and sitemap lastmod. `fix_dashes.py --check` (clean), `audit_pages.py` (0 findings beyond a pre-existing untracked scratch probe file, unrelated), `check_urls.py` (214/214), `affiliate.py --check` (165 documents, clean), `link_graph_report.py` (0 orphans) all clean after. `preflight.py --fast`: 0 FAIL through every gate reached (one transient FAIL traced to a concurrent session's own preflight lock contention, confirmed gone on an immediate clean rerun with a live monkeypatched fail() to prove no silent failure was hiding behind the usual `gate_tests` stall).

**Expected result and how to tell.** Same honest caveat as A11/A13/A14/section 55: this is a rescore against the edited page, not a live re-harvest. The real test is the weekly `keyword-demand.yml` run or a manual fire with live network, which this sandbox does not have.

**Also launched this cycle, handed off by the 04:4x PM check-in by name:** the full, unmodified `python ops/preflight.py` (not `--fast`) to genuine completion in the background, since the only completion on record was 2026-10-28 23:16:50Z, now stale. Result recorded separately once it finishes; see the dated `ops/NIGHTLY-LOG.md` entry for this cycle.

---

## 56. Closed 2026-10-28, scheduled operator cycle: `ops/tests/test_audit_catalog.py`'s own fixture lock was missing the exact recycled-pid protection `ops/preflight.py`'s run lock got on 2026-10-21, a plausible root cause of the chronic `gate_tests` sandbox hang dozens of cycles have reported and killed rather than diagnosed

**Handed off by name, 2026-10-28 PM check-in (20:4x slot):** a sharper lead than "run the whole suite again": `test_audit_catalog.py`'s own `run()` shells out to `audit_catalog.py --include-fixtures` with a 600s subprocess timeout, and the flat-CPU-while-elapsed-climbs symptom dozens of prior cycles measured and killed is consistent with the CHILD being stuck idle-waiting on something in this sandbox, not merely slow.

**Checked directly rather than trusted.** Ran `audit_catalog.py --include-fixtures` on its own: finishes in ~20-24s, genuinely CPU-bound (confirmed via `resource.getrusage`, ~19s user CPU against ~19s wall). `main()` calls `run()` twelve times, so the file legitimately needs roughly four minutes end to end, not a hang by itself; that alone explains why the many prior cycles that wrapped the WHOLE `preflight.py` invocation in a short external `timeout` (90 to 170s) never saw it finish, independent of any lock defect.

**The real defect, found by reading the lock, not by watching it fail again.** `preflight.py`'s own `acquire_preflight_lock()` carries a comment claiming `test_audit_catalog.py` already "proved this exact shape...for its own narrower fixture lock." That comment is stale: this file's `_lock()` only ever had the dead-pid-breaks-immediately check (`os.kill(pid, 0)`), never the start-time comparison `acquire_preflight_lock()` gained on 2026-10-21 (BACKLOG section 25) after a killed `preflight.py` was handed its own now-dead pid back by the kernel and treated a provably-recycled pid as "that's just me, still holding it," falling through to a full stale-timeout wait instead of breaking at once. This sandbox runs many concurrent operator/PM sessions against the same filesystem right now (a concurrent `preflight.py` lock wait was observed live during this same cycle), and any one of them killed mid-test by its own external timeout leaves this exact lockdir behind, reproducing the 2026-10-21 incident in a sibling lock nobody had ported the fix to.

**Reproduced before fixing, not assumed.** Staged a lockdir whose `pid` file equals the current process's own real pid (the recycled-pid shape): the unpatched `_lock()` blocked for its full explicit timeout (5s) then raised `RuntimeError`, confirmed live. **Fixed:** `_lock()` now records `/proc/<pid>/stat`'s starttime field alongside the pid when it takes the lock (`_proc_start_time()`, ported verbatim from `preflight.py`'s own helper) and compares it on the next encounter; a mismatch breaks the lock immediately, same as a provably-dead pid. Re-ran the identical staged scenario against the fixed code: broke in under 0.01s. New `_check_lock_breaks_on_pid_reuse_fast()`, mirroring `gate_preflight_lock_blocks_concurrent_runs`'s own "Half 4" test line for line, wired into `main()` so every `gate_tests()` invocation of this file re-proves it; the two existing self-checks (`_check_lock_self_heals`, `_check_lock_breaks_on_dead_pid_fast`) still pass unchanged. No separate `preflight.py` gate needed: this file's `main()` is already what `gate_tests()` runs and fails on.

**Verified end to end, not inferred.** Ran the real, unmodified `test_audit_catalog.py` to genuine completion with no external timeout: finished clean (`ok`, exit 0) in a little over four minutes, no leftover lockdir or fixture file afterward. This is the first time in the log's visible history this file has been run to completion outside CI rather than killed partway through and reported as "sandbox hang, unchecked."

**Not fully closed.** This explains and fixes one concrete, reproduced way `gate_tests()` can genuinely hang (not just run long) in this sandbox; it does not prove every historical "flat CPU" report across dozens of cycles had this exact cause rather than plain slowness compounding across ~130 test files under a short external wrapper. The practical fix for the slowness half is unglamorous and already named by several prior cycles: give `preflight.py --fast` itself several minutes of real wall time in the background rather than a 90 to 170s foreground `timeout`, since `gate_tests()`'s own per-file budget (700s) already accounts for a file like this one.

Committed and pushed directly (`868129c1a`), ahead of this backlog write-up, since the fix was independently provable without the full-suite run. `check_urls.py`, `audit_pages.py`, `affiliate.py --check` unaffected (no site/catalogue content touched). No price, product or site page touched; not customer-facing, IndexNow not applicable.

**Addendum, 2026-10-28, scheduled operator cycle: the residual open question above is answered.** Ran the real, unmodified `python ops/preflight.py` (not `--fast`) in the background with no external timeout, started roughly 21:50Z, finished 23:16:50Z: a little under 86 minutes wall time. Result: **every gate passed, 0 real FAIL, 37 warnings**, all previously-diagnosed sandbox gaps (no Stripe/SSH/mail credential, no egress to the live site or Etsy's fee page, a few generator subprocesses timing out under this sandbox's own short per-call budget). `gate_tests` itself completed inside that run rather than hanging or being killed; this is the first time in this log's visible history the full suite has been allowed to run to completion and done so clean. This confirms the 56 fix above was sufficient on its own: the chronic "flat CPU, killed, unchecked" shape dozens of cycles reported was the recycled-pid lock bug compounding with a background window too short for ~130 test files' real wall time, not a second, undiagnosed hang. Practical implication for future cycles: `preflight.py`'s full suite needs on the order of 90 minutes of real background time to reach a genuine pass/fail verdict in this sandbox; a 90-170s foreground `timeout` or a 30-minute background cap will still report "unchecked past `gate_tests`" even though the suite is healthy, and that unchecked state should not be read as suspicious on its own. No new gate needed: section 56's own fix is what made this run possible, and the duration itself is an environment fact, not a defect to gate.

## 55. Closed 2026-10-28, owner-invoked CEO cycle: a blanket storage guide, the largest on-topic demand cluster the 2026-10-28 harvest still scored weak

**Observation.** `ops/keyword-demand.json` (harvested 16:27 UTC today) holds about 31 blanket and bedding queries; 15 are `partial` or `gap`, and the highest-intent ones ("how to store blankets", "ways to organize blankets", "how to store extra blankets", "how to store large blankets", "how to organize comforters and sheets") scored 0.0 coverage, falling back to `/about.html`. The answer already existed, split across four zone pages (family room blanket zone, hall closet linen shelf, guest bed and linens, primary bed and bedding), with no page that asks the question the way people type it. That is more demand than the 21 basement queries that justified D-031's guide, and it is seasonal now.

**Action.** `/articles/how-to-store-blankets`, on D-031's precedent (a guide across existing zones, not a new corpus zone). Root cause first (excess quantity, wrong location, bulk), count before containers, three homes matched to use, a fold method, no-linen-closet fallback, AAP safe-sleep note, a seasonal-swap sustain trigger. Every number matches the zone pages it links (one throw per regular seat plus one spare, two flat under-bed bins). Nothing fabricated: no capacity figures, no product claims; vacuum-bag guidance defers to the care label. Seven FAQ entries, each verbatim in the visible text. Wired: articles index card and CollectionPage, inbound links from `more-storage-wont-fix-clutter` and `why-it-lives-in-one-room-but-gets-used-in-another`, sitemap 214, feed 33, llms.txt counts, share card, ROADMAP 219 pages, build id.

**Verified.** check_urls 214/214, audit_pages clean, 0 dashes, affiliate rules pass, JSON-LD parses, 0 broken internal links, true-390px render clean (`ops/shoot_mobile.py`), and 12 article/feed/llms/share/consult/sitemap/Stripe-orphan gates pass. Full `preflight.py` was not run to completion (the documented `gate_tests` hang).

**Expected result and how to tell.** The rows above move from `gap`/`partial` to `covered` on the next weekly harvest re-score (mechanical, not evidence of traffic). The real test is the page appearing in `ops/indexation.json` and, once Phil sends a Search Console Performance export (OWNER-ACTIONS 1a), impressions for blanket queries. Neither exists today.

**Not done, and said plainly.** Not deployed: production SSH was refused to this session, and `deploy.yml` still lacks `VPS_DEPLOY_KEY` (OWNER-ACTIONS 0). Production was already one site commit behind (`840f3e11b`) before this cycle. Traffic not re-measured: the same refusal, and CI has had no database key since 2026-10-03, so the dashboard's traffic line is now 25 days old.

---

## 54. Closed 2026-10-28, scheduled operator cycle: `CHANGELOG.md`'s own "Last updated" date was 26 days stale, backfilled with 9 real entries rather than a date bump

Sections 2-6 were again fully exhausted except the standing Phil-gated rows; all 10 GitHub issues unchanged since 2026-10-25, none from Phil; cold-read ledger 0/297 stale, 0 un-ledgered. A full `preflight.py` run reached genuine completion this cycle (about 34 minutes; `gate_tests` confirmed still progressing by reading its live child-process tree, not assumed hung) and found one real, new warning: `gate_changelog_current` flagged `CHANGELOG.md`'s "Last updated" line at 2026-10-02, 26 days old, past the 21-day threshold section 102 promises.

The gate's own docstring explicitly warns against just bumping the date, so `git log`, this file's own closed sections 9 through 53 and `STATUS-ARCHIVE.md` were read for what had actually shipped in that window, and 9 real, commit-grounded `CHG-2026-NNNN` entries (0016 through 0024) were added: the room and shop-product image fixes, the link-preview/article-figure/room-locator rollout, visitor-country tracking and the shop's international clarity, the global keyword vocabulary and scorer fixes, the full cleaning-method safety and dialect review, the unexposed Photos API hardening, the LinkedIn draft link bug, the video re-render root cause, and the recurring operating-system integrity gates (grouped into one entry pointing at `NIGHTLY-LOG.md` for individual dates, rather than 15 separate entries for routine internal rotation work).

**Verified:** `gate_changelog_current()` called directly after the edit, raises nothing. `fix_dashes.py --check` clean on the new text (0/0). A second full `preflight.py` run afterward reached completion again (every gate passed, 35 warnings, the changelog warning gone, nothing new, same standing environment-access shape). `check_urls.py` (213/213), `affiliate.py --check` (165 documents), mobile `npm test` (3/3 suites). No price, product or site page touched; no new page, `IndexNow` not applicable.

**Next:** backlog and cold-read ledger both genuinely exhausted again; this document-currency fix was the only unblocked, non-Phil-gated work this cycle could find. Same standing Phil-gated queue (10 issues: #42, #40, #35, #33, #31, #29, #21, #18, #15, #2).

## 53. Closed 2026-10-27, scheduled operator cycle: built the one `rotate_status_history.py`-style sibling named by name across five consecutive cycles, STATUS.md section 1 ("Status Metadata"), and found a second real defect while building it

Preflight ran clean up to the documented `gate_tests` sandbox hang (0 FAIL/0 WARN through every gate reached). Sections 2-6 remained fully exhausted except the standing Phil-gated rows (C5 Gemini billing, C6 YouTube OAuth, C7 second wave, KDP/Etsy account creation), confirmed live against GitHub's 10 open issues (all `decision`/`blocked-on-art`, none touched by Phil since 2026-10-25). With nothing else unblocked, picked up the item five straight 2026-10-27 PM check-ins (14:0x through 17:1x) had named by name and each correctly declined as too large for a 30-minute slot: STATUS.md section 1 had grown to 24 entries, 67KB of a 170KB file, the one sibling never built for Production Knowledge, Immediate Focus, BLOCKER-001, the Production Status table rows, `CHECKIN-LOG.md`, `OWNER-ACTIONS.md` and this file's own Done table.

The chain's shape fit none of the existing split functions (entries are variable-length paragraph runs, not one line or one paragraph each), so `ops/rotate_status_metadata.py` reads entry starts from an explicit allow-list of the literal labels this section has actually used, folding every other bold paragraph into the entry above it, and proves the split lossless (byte-identical round-trip against the real file) before trusting it with `--apply`. Verifying it surfaced a second, real defect: the chain was not reliably newest-first by file position. Two entries dated 2026-10-26 sat below entries dated 2026-10-23/24, because a session had prepended its own entry at the wrong anchor point. Keeping "whatever sits physically first" live, the rule every sibling rotator uses, would have archived the genuinely newest work while leaving a stale entry live and labelled current, the exact "copy and control disagree" P0 shape CLAUDE.md's own verification rules name, made worse rather than fixed. So this rotator keeps live every entry at the chain's own maximum date (two, here, a genuine same-day tie) rather than just the physically first one, and archives the rest, verbatim, in file order, into `STATUS-ARCHIVE.md` (reusing `rotate_status_history.py`'s own `apply_archive`, same file, same "new material on top" shape).

Ran `--apply`: 22 entries, 62,995 bytes, moved; section 1 dropped from 67KB to under 5KB, STATUS.md's total size from 170KB to 107KB; nothing lost, confirmed directly by file-size diff against `STATUS-ARCHIVE.md`'s own growth, not assumed. New `gate_status_metadata_not_oversized` in `ops/preflight.py`, wired ahead of `gate_tests` alongside its seven siblings (pure file-parsing, no browser, no network); fail-then-pass proved directly (planted a 10-older-entry chain, watched it warn by name, confirmed a chain at or under the 3-entry buffer and a tied-latest-date pair both stay silent) and in `ops/tests/test_gate_status_metadata_not_oversized.py` (7/7) and `ops/tests/test_rotate_status_metadata.py` (7/7, including the byte-exact round-trip against the real committed file).

**Verified:** full `preflight.py` ran clean through every gate reached before the documented `gate_tests` sandbox hang (0 FAIL, including the new gate re-run directly against the rotated file); `fix_dashes.py --check` (0/0, new files included); `affiliate.py --check` (165 documents); `check_urls.py` (213/213); `py_compile` clean on `ops/preflight.py`, `ops/rotate_status_metadata.py` and both new test files. No price, product or site page touched; no new page, `IndexNow` not applicable.

**Not fixed, and out of scope here:** the standing Phil-gated rows and the deploy gap itself, unchanged; no sandbox session in this run holds `VPS_DEPLOY_KEY`. The root cause behind the newest-first drift (no single, enforced insertion point for new section-1 entries) is not fixed, only its symptom: a future session could still prepend at the wrong anchor and regrow the same disorder this rotator just corrected.

**Next:** backlog and cold-read ledger both genuinely exhausted again; the only unblocked, non-Phil-gated work this run could find was this rotator. The next cycle should watch whether the misordering defect recurs (a new entry landing somewhere other than directly after the "# 1. Status Metadata" heading), since nothing yet enforces the insertion point itself.

## 52. Closed 2026-10-26, scheduled operator cycle: the deploy gap reopened by section 51's own commit, and the gate meant to catch that drift had a substring blind spot

Attached clean (fetch, unshallow, ff-only onto `origin/main`, 9aa6700a0). Backlog sections 2-6 and the cold-read ledger (296/296, 0 stale, 0 un-ledgered) both confirmed exhausted again by direct re-check, GitHub's 10 open issues unchanged (all `decision`/`blocked-on-art`), 0 open PRs, inbox unchecked (no mail credential, same standing gap). A fresh affiliate.py --check failed closed on 3 unreadable PDFs; root-caused to this fresh sandbox not yet having pymupdf installed (the documented fresh-container gap, not a content defect), fixed by `pip install -r ops/requirements.txt`, reconfirmed clean on 10 documents.

**The real finding:** re-derived the deploy gap directly rather than citing the 16:4x PM check-in's "CLOSED: zero commits undeployed." `deploy_gap_material_commits('ad933f9e5')` against real current `HEAD` returns 1 commit: `840f3e11b` (section 51's own avif-chain and British-spelling-gate fix), landed after Phil's 16:51:56Z deploy. STATUS.md's five independent deploy-gap citations (`BLOCKER-001`, Production Knowledge, the Public website and Production traceability table rows, and the Currently Deployed Build/Repository HEAD Build field block) all still said zero gap. Worse: `status_deploy_verdict_problem()`, the gate built specifically to catch this five-section drift, read the fifth section as current too, because its check only asked whether the real build_id appeared anywhere in the paragraph, and it did, just as the "Repository HEAD Build" value in a sentence saying it did NOT match the deployed build. A real, live stale citation passed the exact gate built to catch it.

**Fixed:** all five STATUS.md sections corrected to the real state (deployed build `a0bbe5bb276ee21b`/`ad933f9e5`, confirmed 16:51:56Z; HEAD build `a6815d0c93a17bf5`/`9aa6700a0`; gap: 1 material commit, `840f3e11b`). Narrowed `status_deploy_verdict_problem()`'s fifth-section check to extract the "Currently Deployed Build (last confirmed):" field's own backtick value and compare it directly to the verdict's `build_id`, instead of a substring-anywhere match across the whole paragraph. Fail-then-pass proved directly against the real unmodified STATUS.md (fired, naming the right section) and again after the fix (clean), and in `ops/tests/test_gate_status_deploy_verdict_current.py` (new case 14, 14/14 passing). Cold-read ledger entry for `ops/preflight.py` updated to `fixed` with today's date and a note on what changed.

**Verified:** `check_urls.py` (213/213), `fix_dashes.py --check` (0/0), `affiliate.py --check` (165 documents, after the pymupdf install), `py_compile` clean on both edited files. A full `preflight.py` run reached `cycle_signal: snapshot recorded (clean pass)` with 0 FAIL/0 WARN printed through 101 gates, then hit the documented `gate_tests` sandbox hang (killed at 180s, exit 124, same known shape every recent cycle logs, not a new defect).

**Not fixed, and out of scope here:** the deploy gap itself. No sandbox session holds `VPS_DEPLOY_KEY` or SSH access; closing the recurrence needs Phil's own action on `OWNER-ACTIONS.md` item 0 / issue #35, not another citation fix. This commit will itself need the same correction once Phil deploys again or another commit lands, which is exactly the shape issue #35 exists to end.

**Next:** backlog and cold-read ledger both genuinely exhausted again; the only unblocked, non-Phil-gated work this cycle could find was this citation/gate fix. Remaining work is the standing Phil-gated queue (`OWNER-ACTIONS.md` item 0, the owner-gates table, and the ten open decision/blocked-on-art issues) plus re-measurement drift as it recurs.

---

## 51. Closed 2026-10-26, scheduled operator cycle: the 18-entry cold-read-ledger tier Phil's own cleaning-content review left behind, one real generator-chain defect and six real live British-vocabulary misses found and fixed

**Found:** sections 2-7 confirmed exhausted again, all Done/Archived/Phil-gated; the only genuine unblocked work was the cold-read-ledger staleness gap left by Phil's own `ad933f9e5`/`be352e857` (cleaning-content review: safety fixes, kit completions, a new `fix_dialect.VOCAB` word-choice list, and a cleaning-index redesign), which touched `ops/fix_dialect.py`, `ops/audit_pages.py`, `ops/verify_deploy.py`, `ops/build_cleaning_index.py` and all 14 `ops/cardtext/build_*_deck.py` files without re-ledgering any of them (confirmed live: `cold_read_ledger.py --stale` returned exactly those 18, matching a same-day PM check-in's handoff by name). Two real defects surfaced from actually reading the diffs rather than trusting the count:

1. **`ops/build_cleaning_index.py` never chained `build_avif.wire()`/`fingerprint_assets.main()`, the exact gap class this repo's own `build_articles.py` names by date ("failed CI eleven times on 2026-09-01").** Its own comment claimed to chain "exactly as ops/build_articles.py does," but reproduced directly: a standalone run stripped the committed AVIF `<source>` off the Micro Zone Manual offer card, confirmed by diffing the result against the committed `site/how-to-clean-anything.html`. Invisible inside a full `preflight.py --own` run because `build_avif.wire()` runs globally later in that same gens list and repairs it everywhere as a side effect, including this page.
2. **The new `VOCAB` list was fixed in its three source targets and the deck builders' frozen copies, but `gate_no_british_spellings_shipped`'s pattern was still built from `fix_dialect.PAIRS` alone**, so six live pages kept shipping the exact words the review was fixing elsewhere: `site/articles/how-to-organize-a-junk-drawer.html` (five paragraphs plus its own FAQPage JSON-LD said "a torch"/"the takeaway menus", one said "a tea towel"), `site/consulting.html` and the `why-is-my-house-always-messy.html` generator (`ops/build_messy_article.py`) both said "a fortnight", and `site/deck.html`'s own card alt text said "a rubbish bag". Found by a direct regex scan of `site/**/*.html` and `ops/cardtext/build_*.py` against `fix_dialect.VOCAB`, not assumed from the count.

**Fixed:** `ops/build_cleaning_index.py` now chains both calls after its existing wiring loop; two consecutive standalone runs reproduce the committed file byte for byte (confirmed by diff, not assumed). All six live vocabulary misses corrected at the right layer (the generator source for the one generator-owned page, the hand-maintained HTML directly for the other three, per step 5b) and regenerated. Two false positives deliberately left alone, each checked in context before being excluded rather than assumed safe: "trainers" on `corporate.html`/`what-a-5s-engagement-costs.html` means people ("train your trainers"), not shoes, and has no room-name to disambiguate it the way "extractor" is; "airing cupboard" on `guest-bathroom-the-guest-linen-zone.html` is the zone's own deliberate "Also called..." synonym heading (section 36), not drift.

**Gated, per step 10b:** `gate_generator_chains_avif` (new, `ops/preflight.py`), the sibling `gate_generator_chains_fingerprint` does not cover (that one only fires once a generator already chains `build_avif.wire()`); scans `ops/build_*.py`/`wire_*.py` for a literal WebP `<source>` with no `build_avif.wire()` call, with three documented, individually-verified exclusions (`build_avif.py` itself, `build_epub.py`'s unrelated MIME-type table, `wire_zone_heroes.py`'s internal-helper status since its caller, `build_zone_pages.py`, already chains the call afterward). `gate_no_british_spellings_shipped` widened to also match `fix_dialect.VOCAB` minus "trainers" (excluded the same way `fix_dialect.py`'s own docstring excludes "cupboard"/"fridge"/"mobile"), plus a named, capped exception for the one "airing cupboard" synonym heading. Both fail-then-pass proved directly: `ops/tests/test_gate_generator_chains_avif.py` (7/7, including a real-file fixture pulled from `wire_zone_heroes.py` and `build_epub.py` to prove the exclusions are narrow, not blanket) and `ops/tests/test_gate_no_british_spellings_shipped_vocab.py` (10/10, including both carve-outs catching a *different* word on the same page/file so neither is a page-wide or phrase-wide exemption). The pre-existing `test_gate_no_british_spellings_shipped_case.py` (5/5) still passes.

**Verified:** `fix_dialect.py --check` clean (0 British spellings in tracked surfaces). A fresh VOCAB-pattern scan of the real `site/**/*.html` and `ops/cardtext/build_*.py` after all fixes returns only the three documented, deliberate exceptions. `check_urls.py` (213/213), `audit_pages.py` (218/0), `affiliate.py --check` (165 documents), `fix_dashes.py --check` (0/0) all clean after. `preflight.py` run live, twice: the first (before these fixes) hit the documented `gate_tests` sandbox hang with 0 FAIL through every gate reached; a scripted re-run of all 99 gates ahead of `gate_tests`, individually, with correct arguments, against the real post-fix tree also returned 0 FAIL. All 18 cold-read-ledger entries re-added (`build_cleaning_index.py` as `fixed`, the other 17 as `clean`, each with a note naming what was actually checked); `cold_read_ledger.py --stale` now reports 0, and `--next` confirms the ledger remains fully exhausted at 296/296.

**Went well:** reading the diffs instead of trusting the staleness count directly surfaced a real generator-ownership defect (the avif chain) that a shallower "re-ledger and move on" pass would have missed entirely, since it is invisible inside a full preflight run and only shows up on a standalone regeneration, exactly the way CLAUDE.md step 0.3 and 5d ask this operator to verify.

**Did not go well:** the first full background `preflight.py` run briefly reported "not recorded, this run has failing gate(s)" at its own pre-`gate_tests` checkpoint; tracked down to lock contention between two overlapping preflight processes during this cycle's own kill-and-restart, not a real defect, confirmed by the clean scripted 99-gate re-run above. No gate change made for this, since it is this operator's own concurrency, not a repository defect.

**Next:** the backlog and the cold-read ledger are both genuinely exhausted again. Remaining unblocked work is re-measurement drift as it recurs, plus whatever Phil's own next action in `OWNER-ACTIONS.md` unblocks.

---

## 50. Closed 2026-10-26, scheduled operator cycle: the fifth deploy-gap citation drift, named twice and left unfixed, finally closed at the gate rather than the prose

**Found:** sections 2-6 confirmed exhausted again (every row Done, Archived, or Phil-gated), consistent with sections 47-49's own recent readings. `STATUS.md`'s "Currently Deployed Build (last confirmed)"/"Repository HEAD Build" paragraph under the Technical Operations table still cited the stale build `84c234bd3857ed4c` and a false "4 commits, 2 material" undeployed gap, even though a same-day 05:4x PM check-in had already found and named this exact fifth section as a hole in `status_deploy_verdict_problem()`'s own section map (it only ever parsed BLOCKER-001, Production Knowledge, and the two status-table rows) and left the gate itself unwidened. Re-derived directly rather than trusted: `site/build-id.txt` and `ops/deploy-verdict.json` both read `00187aebb3255957`, and `deploy_gap_material_commits()` against real current `HEAD` returns an empty list. Production matches `HEAD` exactly; the cited gap was stale, not real.

**Fixed:** corrected the prose, then widened `status_deploy_verdict_problem()` itself to parse this fifth section, so this exact drift cannot recur silently a third time, consistent with CLAUDE.md step 10b ("a gate that cannot fail is theatre," proven otherwise here by a fail-then-pass run against a planted corruption of the real file). `ops/tests/test_gate_status_deploy_verdict_current.py` gained two new cases (13/13 passing). Also rotated `ops/NIGHTLY-LOG.md` (249 entries, 734565 bytes, past its 14-day retention window) via the existing `rotate_nightly_log.py --apply`, and regenerated the command deck.

**Verified:** `py_compile` clean on both edited files. `rotate_nightly_log.py --check` reports CLEAN after `--apply`; `gate_nightly_log_ordering`/`gate_nightly_log_no_duplicate_entries` both clean. This cycle's own full `preflight.py` run was superseded by a concurrent cycle's independently clean completion (0 FAIL through the documented `gate_tests` sandbox hang) at essentially the same `HEAD`, confirmed via `ops/cycle-signal.json`'s own auto-recorded note rather than assumed; this cycle's redundant copy was killed rather than waited out twice. 10 GitHub issues re-pulled live, unchanged, all `decision`/`blocked-on-art`, none from Phil.

**Went well:** a concurrent PM check-in (15:1x slot) independently found the identical STATUS.md defect minutes later, hit a push conflict, compared the two fixes, and adopted this one as the more thorough of the two (the same four spots plus the fifth this cycle widened the gate for) rather than duplicating or fighting it, exactly the Step 8 collision handling this file's own process rules ask for.

**Did not go well:** running a second full `preflight.py` cold was wasted effort once a concurrent clean pass already existed at the same commit; a planning fork spent 200 turns and 314k tokens without returning usable findings and was stopped.

**Next:** the backlog is genuinely exhausted again, independently confirmed by two concurrent cycles the same slot. Remaining unblocked work is re-measurement drift as it recurs, plus whatever Phil's own next action in `OWNER-ACTIONS.md`/issue #42 unblocks.

---

## 49. Closed 2026-10-26, scheduled operator cycle: the 485-commit pull this cycle opened with carried six ops scripts section 48's own "exhausted" reading never covered, and two of the six had real defects

**Section 48's "0 un-ledgered candidates" reading predated this.** This cycle's own checkout started shallow and detached (per this prompt's STEP 0), unshallowed, and fast-forwarded 485 commits onto a `main` that had moved well past the commit section 48 was written against. Checked directly against `ops/cold-read-ledger.json` rather than assumed: six files the pull introduced (`ops/keyword_demand_global.py`, `ops/rotate_backlog_closed.py`, `ops/rotate_backlog_done_items.py`, `ops/rotate_owner_actions_closed_items.py`, `ops/rotate_owner_actions_gemini_billing.py`, `ops/rotate_status_workstreams.py`) had no ledger entry at all, so the cold-read lane was not actually exhausted, only exhausted as of a now-stale snapshot.

**Two real defects found, both fixed and tested.** (1) `ops/rotate_backlog_closed.py`'s `count_stats()` returned one `n_bytes` figure used for both "how big is the live corpus" and "how many bytes would `--apply` move", so `--check` and the sibling `preflight.py` gate (`gate_backlog_closed_sections_not_oversized`) both reported the entire corpus's size (180769 bytes) as the size of the one section actually due (2888 bytes), a 62x overstatement. Fixed by returning `overdue_bytes` separately and using it in both messages. (2) `ops/rotate_owner_actions_closed_items.py`'s `do_apply()` opened `OWNER-ACTIONS-ARCHIVE.md` in append mode, growing at the bottom while every sibling rotate tool (`rotate_owner_actions.py`, `rotate_owner_actions_gemini_billing.py`, `rotate_status_workstreams.py`) prepends after the header divider, so its one real run (2026-10-24) already landed out of chronological order relative to later entries. Fixed to prepend for future runs; the one already-misplaced entry is left alone, since the archive's own contract says nothing here is edited on the way in. Both fixes proven with new regression tests (`ops/tests/test_rotate_backlog_closed.py` 8/8, `ops/tests/test_rotate_owner_actions_closed_items.py` 5/5), re-verified after a same-cycle merge with two concurrent check-in commits. The other four files cold-read clean: idempotent, `--check` matches live state, existing gate/unit tests pass. All six now carry a ledger entry.

**No new preflight gate added.** Both defects were in CLI/report text and archive-write mechanics already exercised by existing gates (`gate_backlog_closed_sections_not_oversized`, `gate_owner_actions_closed_items_rotated`) and their own unit tests; the fix plus the new regression tests closes the gap without a new gate function, consistent with CLAUDE.md step 10b's "a gate that cannot fail is theatre" only where failure is actually possible to construct.

**Next:** the cold-read ledger is genuinely exhausted again as of this commit (`git log` confirms no further un-ledgered `ops/*.py` files in the pulled history). The next time any cycle pulls a batch of upstream commits before starting work, re-check `ops/cold_read_ledger.py --next` against the fresh HEAD rather than trusting the previous cycle's reading of it, exactly the gap this section closed. Remaining unblocked work is unchanged from section 48: re-measurement drift as it recurs, plus whatever Phil's own next action in `OWNER-ACTIONS.md`/issue #42 unblocks.

---

## 48. Closed 2026-10-26, scheduled operator cycle: the cold-read lane that section 47's own "Next" line pointed at is now confirmed exhausted too, and a concurrent session beat this one to the stale deploy-gap citation it also found

**Correction to section 47's own "Next" line, which said the next step is the living-doc cold read.** A sub-agent checked `ops/cold_read_ledger.py --stale` (0 of 296) and `--next 10` (0 un-ledgered candidates) directly: every file across every lane (ops, mobile app, photos, cardtext, build/listings, githooks/mcp, content sources) has now been read and ledgered at least once. There is no legitimate "next cold read" left; that lane, run since 2026-10-16 (section 14), is exhausted the same way epics 1-5 already were.

**The one real, bounded defect this cycle's own investigation found** (`STATUS.md`'s `BLOCKER-001` and its two sibling rows citing a stale "2 commits, 1 material" undeployed against build `84c234bd3857ed4c`, now really 4 commits/2 material) was independently found and fixed, slightly more thoroughly, by a concurrent PM check-in (00:4x slot) that pushed first; this cycle's own edit was discarded on merge rather than duplicated, and the fix was re-verified clean (`gate_status_deploy_gap_count_current`, `gate_status_deploy_verdict_current`) against the version that actually landed. No new gate was needed either way: the gate that caught this already exists (2026-09-24).

**Next:** every non-Phil-gated lane this repository currently has (epics 1-5, the full cold-read ledger) is confirmed exhausted as of today, by two sessions independently. The only remaining unblocked work is re-measurement drift of this exact shape, as it recurs, plus whatever Phil's own next action in `OWNER-ACTIONS.md`/issue #42 unblocks. KDP and Etsy remain single-step-ready pending Phil's account creation.

---

## 47. Closed 2026-10-25, scheduled operator cycle: `OWNER-ACTIONS.md` item 1b (Gemini billing) carried a ten-year's-worth, non-chronological correction chain neither existing rotate tool touched, and one of its claims was flatly false

**Found:** independently re-verified the standing state first (fresh attach to main after unshallowing, `preflight.py` 0 FAIL through every gate reached before the documented `gate_tests` sandbox hang, confirmed via `ops/cycle_signal.py --check` reporting SAME against a snapshot this same cycle recorded, 10 GitHub issues unchanged and re-pulled live rather than cited, KDP and Etsy packages re-verified live at 0 FAIL each, inbox unchecked rather than assumed clean, no mail credential in this sandbox). `gate_living_docs_total_size_tripwire` warned all four tracked files, including `OWNER-ACTIONS.md` at 131688 bytes against its 110000-byte ceiling. `rotate_owner_actions.py --check` and `rotate_owner_actions_closed_items.py --check` both reported CLEAN, so the overage sat outside both tools' known chains, in item 1b, which `rotate_owner_actions.py`'s own docstring already names as deliberately untouched ("a different, larger job, left for a future cycle").

**Why it had grown:** item 1b accumulated a dated string of "Corrected"/"Correction to the correction"/"Superseded" paragraphs between 2026-09-04 and 2026-09-30, each narrating a changing count of broken card-hero and zone-hero images (12 then 7 card heroes; 30, 8, 4, 7, then 3 zone heroes) as different review passes and local retries ran, not reliably ordered by date. One paragraph claimed "card art for all 89 Entryway cards (that folder is empty, so cards render with stock photography)"; checked against `ops/card-hero-verdicts.json` directly rather than trusted, that claim was false: 81 of 88 card heroes are already generated and live. A seven-row "what the image must show" zone table still listed four zones (family room, mudroom, nursery, primary bathroom) already fixed on 2026-09-17, confirmed resolved against `ops/hero-verdicts.json` ("ok", not "no").

**Fixed:** `ops/rotate_owner_actions_gemini_billing.py` (new), anchored on three fixed text spans plus the four resolved table rows, archives everything verbatim to `OWNER-ACTIONS-ARCHIVE.md` and leaves one short settled-state paragraph behind, checked against the live verdict files (7 card heroes and 3 zone heroes confirmed as the current, correct counts) rather than against the chain's own last word. The table's "Those seven pages are text only today" became "Those three pages", matching the three rows left (home office file storage, home office printer station, workshop material rack) and the untouched "Current reading" sentence `gate_owner_actions_zone_art_citation_current` parses by name. `gate_owner_actions_gemini_billing_not_oversized` added to `ops/preflight.py`, wired into `main()` right after `gate_owner_actions_closed_items_rotated`.

**Verified:** `ops/card-hero-verdicts.json` and `ops/hero-verdicts.json` re-read directly (7 and 3, matching exactly) rather than trusting the tool's own docstring. `OWNER-ACTIONS.md` 131688 to 121685 bytes (10003 saved); still over its 110000-byte tripwire, honestly reported rather than forced further, since the rest of the overage is diffuse across many smaller items with no single clean extraction point. `test_gate_owner_actions_gemini_billing_not_oversized.py` fail-then-pass proved, 5/5 checks. Every pre-existing `OWNER-ACTIONS.md`-related test (`test_rotate_owner_actions.py`, `test_rotate_owner_actions_closed_items.py`, `test_gate_owner_actions_history_not_oversized.py`, `test_gate_owner_actions_preamble_not_oversized.py`, `test_gate_owner_actions_closed_items_rotated.py`, `test_gate_owner_actions_last_measured_current.py`, `test_gate_owner_actions_retired_sku_count_current.py`, `test_gate_owner_actions_zone_art_citation_current.py`) re-run, all still pass: no cross-tool regression. `py_compile` clean. Full `preflight.py` re-run after the change, 0 FAIL through every gate reached, including the new one, confirmed by direct re-run rather than assumed from the earlier pass.

**Went well:** checking the chain's own factual claims against the live verdict JSON files, rather than trusting the chain's own most recent correction, caught a stale claim ("that folder is empty") the chain itself had never corrected.

**Did not go well:** `OWNER-ACTIONS.md` is still over its tripwire; this closes one clean chain, not the file's whole overage, and a concurrent PM check-in cycle's own push to `ops/cycle-signal.json` collided with this cycle's, resolved by normal merge, no content lost.

**Changing next cycle:** none structural. The remaining overage in `OWNER-ACTIONS.md`, `STATUS.md`, `CHECKIN-LOG.md` and `BACKLOG-2026-09-07.md` is each file's own next cold-read candidate, not yet characterised.

**Next:** KDP and Etsy are both still single-step-ready (re-verified live this cycle, 0 FAIL each) and still waiting on Phil's own account creation; no new non-Phil-gated item exists beyond the next living-doc cold read. GitHub issue #42 (the cadence question) is unchanged and inside its own 48h no-repeat floor; not re-raised this cycle.

---

## 46. Closed 2026-10-24, scheduled operator cycle: the "different, higher-risk job" `rotate_backlog.py` and `rotate_backlog_closed.py` both deferred by name, sections 2-4's mixed open/closed per-item rows, got its first safe slice instead of a fourth deferral

**Found:** independently re-verified the standing "fully exhausted" state first (fresh checkout, `preflight.py` 0 FAIL through every gate reached before the documented `gate_tests` sandbox hang, `cold_read_ledger.py --stale` 0/294 and `--next` 0 un-ledgered, 10 GitHub issues unchanged via a fresh API pull, all `decision`/`blocked-on-art`, deploy gap re-derived directly at 2 commits/1 material unchanged, production unreachable from this sandbox confirmed again). With every existing rotate tool reporting CLEAN (`rotate_backlog.py`, `rotate_backlog_closed.py`, `rotate_checkin_log.py`, `rotate_owner_actions.py`, `rotate_owner_actions_closed_items.py`, `rotate_status_workstreams.py`, every `rotate_status_history.py` mode, all re-run fresh this cycle), the only remaining overage against `gate_living_docs_total_size_tripwire` is sections 2-4's own per-item rows, which every prior cycle today correctly declined to touch, naming it "a different, higher-risk job" without attempting a scoped slice of it.

**Why it is genuinely risky, characterised precisely rather than just restated:** sections 2-4 reuse letter+digit ids in free-form journal rows (`B4` the original row vs. a later, unrelated `**B4 follow-on, found and fixed 2026-09-08...**` note sharing the prefix; `**C6/C7 adjacent, thumbnail font defect...**` naming two ids in one entry), so a generic "find a line starting with `**ID`" parser would silently archive the wrong text. Confirmed directly: of the 18 rows the original section-2/3/4 tables defined, exactly 17 are written in one unambiguous shape, `| **ID** | ~~struck item~~ | ...`, which never collides with the free-form `**ID, ...** ` journal rows (always a comma right after the id, never `**` then ` | ~~`). The 18th, C5, is open and correctly excluded by the same check (no strikethrough).

**Fixed:** `ops/rotate_backlog_done_items.py` (new), a hardcoded 17-id whitelist (A1-A6, B1-B4, B6, B8, B9, C1-C3, C7), each matched only against the exact `| **ID** | ~~...~~ | ` shape within the section-2-to-5 span, refusing rather than guessing if a whitelisted id's row doesn't match that shape or matches more than once. Every trailing cell moves verbatim into `BACKLOG-2026-09-07-ITEMS-ARCHIVE.md` (new), the live row shrinking to id + struck title + a one-line pointer, the same convention `BACKLOG-2026-09-07-B9-ARCHIVE.md` set for this file's single largest row (whose own remaining ~3.2KB live cell this fix also finishes, since that one-off never touched it). `gate_backlog_done_items_rotated` added to `ops/preflight.py`, wired into `main()` right after its closed-sections sibling. Every free-form journal row (A7 onward, B5/B7, C4-C6's later notes) is explicitly untouched: classifying those safely is still the larger, deferred job.

**Verified:** dry-run against a scratch copy first; round-trip (rebuilding each original row from its pointer plus the archived rest-cell) reproduced the input byte for byte before the real `--apply`. Applied for real: `git diff --stat` on the live file shows exactly 17 lines changed, 17 insertions, 17 deletions, matching the 17 rows one for one; the real output byte-matches the pure `plan_rotation()` prediction computed from the pre-apply file. `BACKLOG-2026-09-07.md` 317652 to 293184 bytes (24468 saved); still over its 150000-byte tripwire. 8/8 new unit tests (`test_rotate_backlog_done_items.py`: exact-shape match, free-form-journal-row non-match even on a whitelisted prefix, section-2-4 boundary respected, round-trip, idempotency, non-strikethrough non-match, duplicate-match refusal, archive prepend/header-mismatch refusal) and 4/4 new gate tests (`test_gate_backlog_done_items_rotated.py`: warns on an unrotated row, silent on a rotated one, silent on a file with none of the 17 ids, warns rather than crashes on a duplicate). `py_compile` clean. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0. The new gate run directly against the real, now-rotated file: silent. Full `preflight.py` re-run in the background after the change: 0 FAIL through every gate reached, including the new one, confirmed by grep rather than assumed. Ledgered the new tool in `cold_read_ledger.py` as authored-and-verified this cycle rather than leaving it for a future cold read.

**Went well:** characterising the actual ambiguity (duplicate-prefix journal rows) before writing any parser turned "higher-risk job" from a reason to defer into a precise boundary the tool could enforce by refusing outside it.

**Did not go well:** nothing new; this closes one well-defined slice, not the whole gap.

**Changing next cycle:** none structural. If the free-form journal rows (A7-A28, B5/B7, C4-C6's later notes) ever get a safe classification rule, a sibling tool is the next step; this one deliberately does not attempt it.

**Next:** `BACKLOG-2026-09-07.md` is still ~143KB over its tripwire, almost entirely the free-form journal rows this fix explicitly left alone. Everything else remains the same standing Phil-gated queue (Gemini billing, YouTube OAuth, Search Console reports, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42).

## 45. Closed 2026-10-24, scheduled operator cycle: `STATUS.md`'s own "Public website" and "Production traceability" table rows had the identical unbounded-growth defect every sibling field above was already fixed for, the exact gap the 13:4x PM check-in's own handoff named by name

**Found:** this cycle's own checkout attached onto `3934dd234`, re-verified rather than cited: `cold_read_ledger.py --next` 294/294 ledgered, `--stale` 0; 10 open GitHub issues unchanged, all `decision`/`blocked-on-art` (issue #42's own 07:4x comment confirmed current, no reply from Phil since); 0 PRs; `inbox_agent.py --apply` no mail credential, unchecked rather than assumed empty; `preflight.py` run to completion in the background, 0 FAIL across every one of 98 gates reached before the documented `gate_tests` sandbox hang. With the cold-read lane and the GitHub queue both confirmed still exhausted, picked up the one concrete, already-scoped, non-Phil-gated task on record: the 13:4x PM check-in's own handoff, naming `STATUS.md`'s `# 4. Production Status` table's "Public website" and "Production traceability" rows as carrying the identical dated-correction-chain growth defect already fixed for Production Knowledge, Immediate Focus, BLOCKER-001, CHECKIN-LOG, OWNER-ACTIONS and this file's own sections, with no gate watching either row's size. Confirmed directly before building anything: both rows were 21 entries each, 17551 and 8978 bytes, the figures the handoff cited.

**Fixed:** added `split_table_row_chain`/`plan_rotation_table_row`/`plan_rotation_table_rows` to `ops/rotate_status_history.py` (new `--check-table-rows`/`--apply-table-rows` CLI modes), a third shape again: a table cell cannot hold a newline, so unlike BLOCKER-001's paragraph-bounded chain this one lives on a single physical line, newest first, each entry after the first introduced by the literal text "Prior state, kept because the shape recurs: " instead of a line or paragraph break. The row is located by its own first-column label and the function refuses to guess if the row is missing, duplicated, does not have exactly 4 pipes (3 columns, guarding against a stray literal `|` inside the prose), or its cell does not open on a bold entry. Applied for real: both rows now carry exactly their current, live entry (1262 and 536 bytes), the other 40 entries moved verbatim to `STATUS-ARCHIVE.md`. Added `gate_status_production_table_rows_not_oversized` to `ops/preflight.py`, mirroring `gate_status_blocker001_not_oversized`'s shape (a WARNING with a buffer of 3, not a FAIL), wired into `main()`.

**Verified:** dry-run against a scratch copy of `STATUS.md` first, confirmed round-trip (rejoining the split entries on the chain marker reconstructs the original cell exactly) before touching the real file; the real `--apply-table-rows` output matched the scratch prediction byte for byte (`cmp`). `--check-table-rows` CLEAN after. Proved the new gate can actually fail: ran it against a synthetic oversized row and confirmed it warns, naming the row; confirmed it stays silent on the real, now-rotated file. Added `ops/tests/test_gate_status_production_table_rows_not_oversized.py` (6/6: warns on both rows oversized, silent at exactly 1 entry each, silent at the buffer, warns naming only the oversized row when the other is clean, no-crash on a missing file, no-crash on an unrecognisable file) and 8 new cases (19-26) to `ops/tests/test_rotate_status_history.py`, including a round-trip proof against the real, committed `STATUS.md`. All new/touched tests pass; `test_gate_status_blocker001_not_oversized.py` re-run unchanged, confirming no regression on the sibling gate. `py_compile` clean on every touched file. Re-ran the status-specific gates directly against the real edited file (`gate_status_deploy_verdict_current`, `gate_status_deploy_gap_count_current`, the four `*_not_oversized` siblings, `gate_living_docs_total_size_tripwire`): 0 FAIL, 0 new WARN beyond the pre-existing, already-tracked living-docs tripwire (all four named files, including `STATUS.md`, still over their ceiling even after this fix, a separate standing item). `check_urls.py` 213/213, `audit_pages.py` 218/0, `fix_dashes.py --check` 0/0. Full `preflight.py` re-run in the background to the documented `gate_tests` hang a second time, after this change: 0 FAIL on every gate reached, including the new one, confirmed by grepping the run's own log rather than assumed.

**Went well:** the handoff was specific enough (row names, byte counts, the exact shape to generalise from) that no re-diagnosis was needed, only implementation; `split_blocker1_chain`'s own round-trip-before-trusting pattern transferred directly to a differently-shaped chain.

**Did not go well:** nothing new; this was a clean implementation of an already-diagnosed gap.

**Changing next cycle:** none; this closes the one item named by name. If a sibling single-physical-line, marker-separated chain turns up elsewhere, generalise then rather than writing a fourth near-identical split function by hand.

**Next:** `STATUS.md` is still ~49KB over its 110000-byte tripwire even after this fix (down from ~74KB over), and `BACKLOG-2026-09-07.md`, `CHECKIN-LOG.md` and `OWNER-ACTIONS.md` remain over theirs too, per `gate_living_docs_total_size_tripwire`'s own standing warning; no single prunable chain of this row's size was found elsewhere in `STATUS.md` this cycle. Everything else remains the same standing Phil-gated queue (Gemini billing, YouTube OAuth, Search Console reports, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42).

## 44. Closed 2026-10-24, scheduled operator cycle: `ops/rotate_owner_actions.py`'s own main `--check`/`--apply` was silently broken by that same morning's preamble-rotation commit, and both preflight gates reading it swallowed the breakage with no warning

**Found:** with cold-read, GitHub issues, inbox and the structured backlog all independently reconfirmed exhausted this cycle (293/293 ledgered, 0 stale; 10 issues unchanged, all `decision`/`blocked-on-art`; 0 PRs; no mail credential), ran `python ops/rotate_owner_actions.py --check` directly rather than trust the standing "clean" citation, per CLAUDE.md 5d. It refused: `start anchor missing or duplicated: 'it says nothing about traffic.'`. That sentence was the literal tail of the "List reviewed:" paragraph the script's `REGION_START_AFTER` constant was hardcoded against; commit `bd7f59312`, earlier the same morning (07:10 UTC), rewrote that paragraph to `LR_REPLACEMENT` as part of rotating its own accumulated history, and the exact words this constant searched for then existed nowhere in the file. Worse, both preflight gates that call into this (`gate_owner_actions_history_not_oversized`, `gate_owner_actions_preamble_not_oversized`) caught the resulting `ValueError` with a bare `except ValueError: return`, so the breakage produced neither a WARN nor a FAIL anywhere in a full `preflight.py` run; the sibling gate for the closed-items rotation (`gate_owner_actions_closed_items_rotated`) already shows the correct pattern, catching its own tool's refusal and turning it into a named warning, so this was an inconsistency within the same file, not a novel problem.

**Fixed:** `REGION_START_AFTER` now derives from `LR_REPLACEMENT` itself (`REGION_START_AFTER = LR_REPLACEMENT.strip()`, assigned just below that constant's own definition) instead of carrying a frozen copy of its words, so the two paragraphs can never drift apart again regardless of how the preamble rotation's own replacement text changes in the future. Both preflight gates' exception handlers now warn by name instead of returning clean, guarded so a document carrying none of this gate's structural markers (a synthetic fixture with no "List reviewed"/"Last measured" header at all) stays silent exactly as it did before, and only a file that looks like a real `OWNER-ACTIONS.md` but fails to parse speaks up.

**Verified:** reproduced the live breakage directly before fixing it (`git stash` on just the one file, confirmed `--check` refuses and both gates return silently with zero WARN/FAIL); confirmed the fix resolves it (`--check`/`--check-preamble` both CLEAN against the real file); confirmed the gate fix actually fires (reverted only the anchor fix, kept the gate fix, called both gates directly: `gate_owner_actions_history_not_oversized` now warns by name) and stays silent again once both fixes are in place together. Updated `ops/tests/test_rotate_owner_actions.py`, `ops/tests/test_gate_owner_actions_history_not_oversized.py` and `ops/tests/test_gate_owner_actions_preamble_not_oversized.py`, which had hardcoded the same dead sentence in their own synthetic fixtures; added a case to each of the two gate tests proving a real-shaped-but-drifted file now warns, distinct from the existing case proving a wholly unrelated document still stays silent. All three: clean (19/19, 6/6, 7/7). `ops/cold_read_ledger.py` updated for both `ops/rotate_owner_actions.py` and `ops/preflight.py` (fixed, today). `check_urls.py` 213/213, `audit_pages.py` 218/0, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents, `link_graph_report.py` 0 orphans, `py_compile` clean on every touched file, `cold_read_ledger.py --stale` 0. Full `preflight.py` run to the documented `gate_tests` sandbox hang, 0 FAIL on every gate reached before it, same standing limitation every cycle today reports.

**Went well:** running the tool directly instead of trusting its own prior-cycle "CLEAN" citation found a real, same-day regression nothing else had caught; the sibling gate's already-correct exception-handling pattern gave a ready template for the fix instead of inventing a new one.

**Did not go well:** `bd7f59312`'s own commit message said it was "proved against the real parsing functions," and it was, for the two paragraphs it touched; it did not check whether another part of the same file depended on the text it was rewriting. The dependency was real and local to one file, and nothing flagged it.

**Changing next cycle:** none; this is a one-off anchor fix tied to one file's own cross-reference, not a new recurring class. If a third sibling anchor-into-volatile-prose break shows up elsewhere, that would be the signal to generalize rather than patch the third instance by hand (CLAUDE.md step 10b).

**Next:** this file is still roughly 153KB over its tripwire. The next prunable candidates are the same shape in other items (A7-A28's own dated follow-on notes in section 2, B1-B8's follow-ons in section 3), and sections 2-4's deliberately-deferred "mixed open/closed" structure still has no generalised rotation tool, only this one hand fix. Everything else remains the same standing Phil-gated queue (Gemini billing, YouTube OAuth, Search Console reports, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42).

## 43. Closed 2026-10-24, scheduled operator cycle: item B9's own per-room completion narrative, 54KB inline inside one still-open table row, the exact shape sections 1 and 8+ were already rotated for and sections 2-4 were explicitly left out of scope

**Found:** the living-docs size tripwire (`gate_living_docs_total_size_tripwire`) was WARNING live on all four tracked files again (`STATUS.md` 183568/110000, `OWNER-ACTIONS.md` 131688/110000, `CHECKIN-LOG.md` 250159/110000, this file 354007/150000), confirmed by calling the gate directly rather than citing the dashboard; every sibling `rotate_*.py --check` (status history, owner-actions closed items, backlog closed sections, checkin log, status workstreams) reported CLEAN, meaning the overage was coming from somewhere none of the existing rotation tools cover. Cold-read this file's own two rotation tools' docstrings (`rotate_backlog.py`, `rotate_backlog_closed.py`): both explicitly name sections 2-4 as out of scope, because they "mix open and closed rows under their own per-item ids," and call fixing that "a different, higher-risk job." Read section 3 ("Now: decks") looking for the actual shape of that risk rather than guessing: item **B9**'s own table row, done and struck through since 2026-09-29, had every one of its 20 per-room "Nth done" completion entries appended inline, never removed, growing the row itself to roughly 54KB (41220 + 10218 + 2533 bytes across the row and two continuation lines) inside a section whose own job is to be the current, still-open queue.

**Fixed:** moved the per-room narrative (everything from "Entryway done 2026-09-25" onward) verbatim into a new `BACKLOG-2026-09-07-B9-ARCHIVE.md`, oldest-first (the order it was originally appended in), matching this file's existing archive convention. Replaced it in the live row with a one-sentence pointer and closed the row's own "Accept when" cell with a proper trailing `|`, fixing the same missing-delimiter degradation `rotate_backlog.py` found and fixed elsewhere in this file. Grepped the whole repository first for any script or test that parses this narrative by name ("Entryway done", "Nineteenth done", ordinal markers): none found; it is prose, read by humans and agents, never by code. This is a one-time hand rotation of a single finished item, not a new generalised tool: B9 is fully done and will not grow again, unlike the recurring per-cycle growth the `rotate_status_history`/`rotate_checkin_log`-style gates exist to catch.

**Verified:** archived body (50963 bytes) confirmed byte-identical to the original source text before editing the live file (direct string comparison, not assumed). `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents, `check_urls.py` 213/213, `cold_read_ledger.py --stale` 0. `preflight.py --fast` run fresh to completion: 0 FAIL through every gate reached, genuinely hung at the documented `gate_tests` sandbox limitation, same as every other cycle today, nothing new broken. This file: 354007 to 303307 bytes, still well over its 150000-byte tripwire ceiling, so this closes one large candidate, not the whole gap.

**Went well:** grepping for code references to the narrative before archiving it, rather than assuming prose is safe to move, cost thirty seconds and ruled out a real risk.

**Did not go well:** nothing new; this is the same "cold-read a named-but-deferred gap" pattern several sections above already used successfully.

**Changing next cycle:** none.

---

## 42. Closed 2026-10-24, scheduled operator cycle: `ops/rotate_status_workstreams.py` had no dedicated preflight gate, unlike every sibling rotate tool, the exact gap section 41 above left open on purpose; independently verified after finding a concurrent session had already shipped the identical fix

`cold_read_ledger.py --next` turned up exactly one un-ledgered file: `ops/rotate_status_workstreams.py` itself, the 10:2x cycle's own new script (section 41 above). Read it cold. The rotation logic is correct and already applied cleanly to the live `STATUS.md` (`--check` reports CLEAN). But unlike `gate_owner_actions_closed_items_rotated`, `gate_backlog_done_table_not_oversized` and the other `gate_status_*` chain gates, no dedicated gate watched this one span. Section 41's own reasoning was that `gate_living_docs_total_size_tripwire` (the generic byte-ceiling WARN added the same day) already covers `STATUS.md`, so a second gate would duplicate it. That is only true for the file's TOTAL size: the tripwire cannot tell this specific narrative has regrown if another section of the same file shrinks by more in the meantime, which is exactly the "source corrected, nothing keeps it that way" shape this file's own BLOCKER-001 and Production Knowledge chains (sections 28-29, 33) were each gated for by name.

**Started building the fix, then found on fetch before push that a concurrent session had already shipped the identical one** (`35d66a5b4`, "Add gate_status_workstreams_rotated: catch STATUS.md section 14 regrowth", same gate name, same reasoning, same test file name): `gate_status_workstreams_rotated` in `ops/preflight.py`, importing `rotate_status_workstreams` and calling its own `split_workstream3` to warn if the live narrative is non-empty and does not match the pointer the tool leaves behind, warn (rather than crash) if the anchors it depends on go missing, and no-op if `STATUS.md` itself is missing, wired into `main()` right after the tripwire gate. Rather than reconcile two copies of the same fix, took theirs and verified it independently instead of trusting the commit message or discarding this cycle's own in-progress copy blind: the working tree already matched their shipped version byte for byte once fetched, so nothing of this cycle's own was lost by not pushing a duplicate.

**Verified independently:** `ops/tests/test_gate_status_workstreams_rotated.py`, 6 cases (unarchived narrative warns; freshly rotated stays silent; `plan_rotation` is idempotent on already-rotated text; new text appended after the pointer warns again, the actual regrowth case this gate exists to catch; a missing anchor warns instead of crashing; a missing `STATUS.md` is a silent no-op), all 6 pass. Proved the test can actually fail, not just pass: neutered the gate's warn call in a scratch copy, confirmed the test correctly reported 2 failures by name, restored it, confirmed 6/6 again. Called the new gate directly against the real live `STATUS.md`: 0 FAIL, 0 WARN. `python ops/rotate_status_workstreams.py --check` independently confirms CLEAN. `ast.parse` on `preflight.py` before relying on it. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents. Full `preflight.py` run was contended by a concurrent session's own run holding the file lock for 7+ minutes (the documented `gate_tests` sandbox hang, not a crash); rather than wait indefinitely, verified the new gate and its neighbours by direct function call against the live module instead of the CLI. `cold_read_ledger.py --next` now reports 294 of 294, 0 stale, until a new file changes or appears.

**Went well:** fetching before push caught the collision before anything duplicate shipped; verifying the concurrent fix independently rather than trusting its commit message still had value, since it is the only place this fix is written up in the narrative logs (the shipping commit touched no `BACKLOG`/`NIGHTLY-LOG` file).

**Did not go well:** real effort went into building a fix someone else had already pushed minutes earlier, the same collision shape several other cold-read-lane cycles this week have hit; the preflight run-lock contention from a concurrent session is a known, already-documented limitation, not a fresh defect.

**Changing next cycle:** none.

**Next:** `STATUS.md` is still 183568 of 110000 bytes (unchanged by this entry, which only added a gate, not a rotation). The next cold-read of this file should look at Open claims, section 20 ("Recently Completed Meaningful Work") and the BLOCKER-001 chain for the next prunable candidate, same handoff section 41 left. Everything else remains the same standing Phil-gated queue (Gemini billing, YouTube OAuth, Search Console reports, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42). No push notification due this cycle: the last one (2026-10-22T13:5x) is not yet 48 hours old and nothing material in the owner-gated state has changed.

Pushed to main. `ops/preflight.py`, `ops/tests/test_gate_status_workstreams_rotated.py`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

---

## 41. Closed 2026-10-24, scheduled operator cycle: `STATUS.md` section 14's own closed Workstream 3 build-log narrative, the exact candidate section 33 and section 40 both named and nobody had read, finally rotated

A concurrent 09:4x PM check-in found `gate_living_docs_total_size_tripwire` (new 2026-10-24, generic byte-ceiling check) firing live on all four tracked files and named `STATUS.md` section 14 ("Active Major Workstreams") as the one unread candidate three prior cycles (including section 33 and section 40 above) had deferred without a closer read. Merged that cycle's commit cleanly (conflict only in the generated dashboard trio and the nightly log, resolved by regenerating the dashboard fresh and keeping both log entries in order), then read section 14 in full rather than act on the handoff's summary alone: Workstreams 1 and 2 are still BLOCKED, their short descriptions current; Workstream 3 was CLOSED 2026-10-03, but ~18 dated "Done"/"Found"/"Corrected" entries from 2026-09-07 through 2026-09-25 (M1 through B9) documenting how it closed still sat live underneath the one-paragraph closure summary.

**Built** `ops/rotate_status_workstreams.py` (`--check`/`--apply`), same anchored-span, refuse-rather-than-guess shape as its siblings. No new preflight gate added for this one section specifically: the generic tripwire already watches the whole file and a second gate would duplicate it.

**Verified:** `ops/tests/test_rotate_status_workstreams.py`, 12 cases. One real bug caught before shipping: the first draft's `--check` tested bare `if narrative:` and would have reported an already-rotated file as DUE forever, because the pointer sentence this script leaves behind is itself non-empty text between the two anchors; a test that runs `main()` itself against a scratch file (not just the pure `split_workstream3`/`plan_rotation` functions) caught it, confirmed by deliberately reintroducing the bug and watching that test fail by name before fixing it back. Applied for real: moved 13563 bytes verbatim to `STATUS-ARCHIVE.md`. `STATUS.md` 196738 to 183568 bytes, still over the 110000-byte tripwire (this is one candidate of the overage, not the whole fix; the generic gate still warns honestly). Confirmed by direct read that the Workstream 1/2/3 headers, the closure summary, and section 15 immediately following are all untouched. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents. Preflight's own run lock was held by a concurrent session during this cycle; rather than wait or skip the check, called `gate_living_docs_total_size_tripwire`/`gate_status_deploy_verdict_current`/`gate_status_deploy_gap_count_current` directly against the live module and read `preflight.FAIL`/`preflight.WARN` afterward: 0 FAIL, the four expected living-docs WARNs (STATUS.md now 183568, the other three unchanged), confirming the rotation broke nothing without needing the lock. `ops/tests/test_rotate_status_history.py` (STATUS.md's other rotation tool) still passes against the edited file, confirming the shared document shape survived.

**Went well:** running the new test through the CLI's own `main()`, not only the pure functions it calls, caught a real idempotency bug that would otherwise have nagged every future cycle with a false DUE.

**Did not go well:** same "test the function, not the entry point" gap a few other tools in this repository's history have hit; worth a standing habit, not a new gate.

**Changing next cycle:** none.

**Next:** `STATUS.md` is still 183568 of 110000 bytes. The next cold-read of this file should look at Open claims, section 20 ("Recently Completed Meaningful Work") and the BLOCKER-001 chain for the next prunable candidate. Everything else remains the same standing Phil-gated queue (Gemini billing, YouTube OAuth, Search Console reports, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42).

Pushed to main. `ops/rotate_status_workstreams.py`, `ops/tests/test_rotate_status_workstreams.py`, `STATUS.md`, `STATUS-ARCHIVE.md`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

## 40. Closed 2026-10-24, scheduled operator cycle: `OWNER-ACTIONS.md`'s own "Last measured"/"List reviewed" paragraphs, the one item sections 31 and 32 both named and deliberately deferred, finally done with the care their own deferral asked for

Attached per STEP 0, clean (unshallow, `checkout main`, ff-only onto `0eaa7cc10`, tree clean). Read `GOALS.md`, `BACKLOG-2026-09-07.md` sections 0-7, `CLAUDE.md`, and the real newest-first head of `ops/NIGHTLY-LOG.md`. Pulled all 10 open GitHub issues fresh: unchanged, all `decision`/`blocked-on-art`, matching issue #42's own standing status exactly (read its full comment thread, not just its title: five consecutive status updates since 2026-10-14, all confirming the same exhausted/Phil-gated state). `cold_read_ledger.py --stale`: 0 stale. `inbox_agent.py --apply`: no mail credential, unchecked, not assumed empty. Confirmed epics 1-5 exhausted/Phil-gated again, so this cycle worked epic 6 (operational honesty), section 32's own "Next" line: "The 'Last measured'/'List reviewed' paragraphs in `OWNER-ACTIONS.md`, named by section 31, are still open too."

**Verified section 31's deferral was real, not stale, before touching anything.** Both paragraphs had in fact kept growing since 2026-10-23: "Last measured" carried its original 2026-10-02 traffic citation plus a full correction chain and an unrelated item-1 (YouTube) readiness narrative (1,318 bytes); "List reviewed" carried its 2026-10-23 date plus a four-entry "Earlier, DATE:" changelog back to 2026-10-17 plus a closing clause explaining the split from "Last measured" (2,204 bytes). Confirmed both gates that read these paragraphs by name (`ops/dashboard.py`'s `_owner_actions_traffic_citation()`, `ops/preflight.py`'s `gate_owner_actions_last_measured_current`) before changing anything, so the fix could be proved against the real parsers, not just against this script's own idea of what they need.

**Fixed with a different mechanism than section 31's, because the risk was different.** The other chain's dead text never changes again; these two paragraphs are expected to change again, the next time a session with VPS access re-measures traffic or re-reviews the list, so a rotation tied to today's specific date or number would break the moment that happened. `ops/rotate_owner_actions.py` gained `--check-preamble`/`--apply-preamble`: `LM_CITATION_RE`/`LR_DATE_RE` find each paragraph's live sentence by the same regex shape `dashboard._owner_actions_traffic_citation()` and `gate_owner_actions_last_measured_current` themselves require, never a hardcoded string, so a real future re-measurement is found exactly the same way. Everything after the live sentence, up to the next fixed structural boundary (the "List reviewed" header, or the already-stable "Deploy-gap and per-item history" pointer section 31 left behind), is archived to `OWNER-ACTIONS-ARCHIVE.md` and replaced with a short, deliberately evergreen pointer that names no specific topic or date, so it never goes stale itself. The "List reviewed" marker's real operational knowledge (what bumping its date does and does not mean, why it must never be conflated with "Last measured") is folded permanently into that pointer rather than kept as live prose that could regrow a third time.

**Turned into a gate.** New `gate_owner_actions_preamble_not_oversized` in `preflight.py`, same WARNING-not-FAIL, buffer-past-pointer shape as its `gate_owner_actions_history_not_oversized` sibling, wired in immediately after it in `main()`'s call order (ahead of `gate_tests`, pure file-parsing, no browser or network needed).

**Verified against synthetic cases and the real file, not just this script's own output.** `ops/tests/test_rotate_owner_actions.py` extended to 18 cases (was 10): the new cases prove the regex-based anchors survive a different real reading (a synthetic 2027 date, not today's), that rotation never touches text outside the two paragraphs, that a reworded citation is refused rather than guessed past, and, critically, that the real committed `OWNER-ACTIONS.md` parses clean through the actual `dashboard._owner_actions_traffic_citation()` and `gate_owner_actions_last_measured_current` functions, not a synthetic copy of them. New `ops/tests/test_gate_owner_actions_preamble_not_oversized.py` (6/6), fail-then-pass proved directly: a synthetic oversized "Last measured" paragraph warns, a synthetic oversized "List reviewed" paragraph warns independently, a freshly rotated copy and the real committed file both stay silent. Applied for real: `--check-preamble` reported 1,205 and 2,175 bytes DUE; `--apply-preamble` moved 3,462 bytes to `OWNER-ACTIONS-ARCHIVE.md` verbatim (confirmed present there by direct grep); `--check-preamble` immediately after reports CLEAN (239 and 393 bytes, each at its own pointer's size). Diffed the real file before/after: everything from `**Deploy-gap and per-item history` onward is byte-identical. Ran the real parsing functions directly against the rotated live file: `gate_dashboard_owner_actions_traffic_citation_current` and `gate_owner_actions_last_measured_current` both clean (0 FAIL/0 WARN), `dashboard._owner_actions_traffic_citation()` still returns `('2026-10-02', 49, 121)`, the same real reading as before rotation. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents, `cold_read_ledger.py --stale` 0 stale (ledger entry for `rotate_owner_actions.py` bumped to today with a note on what changed). `preflight.py` fast run to completion in the background: 0 FAIL through every gate reached, including the new one in its correct call-order position, before the documented `gate_tests` headless-Chromium sandbox hang; confirmed the hang was real by CPU-flat evidence (process 1895, 14s CPU time at both 267s and 972s elapsed, 705s apart with zero progress) before killing it; unchecked past that point, not assumed passing.

**Went well:** verifying the actual parsing contract first (reading both consumer functions' regexes directly, then testing candidate replacement text against them in isolation before writing a single line of the rotation script) caught the fragile design this would otherwise have shipped with: a first draft used fixed string anchors tied to today's exact date and numbers, which would have silently stopped finding its own anchor the next time either paragraph legitimately changed. Switching to the same regex shape the real consumers use instead of a hardcoded literal is what makes this survive a future re-measurement rather than becoming a fourth thing to fix next cycle.

**Did not go well:** the first `--apply-preamble` run produced a grammatically malformed sentence ("...30 days Earlier corrections...", missing a terminal period; "List reviewed: 2026-10-23: every item...", an awkward double-colon) because the citation regex's own match boundary does not include trailing punctuation. Caught by reading the actual rotated output before committing to it, not by a test; fixed by adjusting the replacement constants' own leading punctuation and re-running. A future instance of this same class (a replacement constant whose leading character assumes punctuation the citation regex does not itself guarantee) is still possible for a differently-worded future citation; not gated, because the grammar itself is cosmetic, not a parsing-contract break, and gating English grammar is a worse trade than reading the output once per change.

**Changing next cycle:** none.

**Next:** sections 2-4 of this file (A/B/C item tables) remain the lower-value, harder-to-safely-rotate target section 32 already named, still not urgent at today's size. `STATUS.md`'s other long sections (`# 1. Status Metadata`, `# 4. Production Status`, `# 14. Active Major Workstreams`) were sized but not read in full by section 33; still nobody's done that read. Every epic ahead of operational honesty still dead-ends at a Phil decision or account action (Gemini billing, YouTube OAuth, Search Console, Amazon/Etsy/Apple/Play accounts, issue #15, issue #42).

Pushed to main. `OWNER-ACTIONS.md`, `OWNER-ACTIONS-ARCHIVE.md`, `ops/rotate_owner_actions.py`, `ops/preflight.py`, `ops/tests/test_rotate_owner_actions.py`, `ops/tests/test_gate_owner_actions_preamble_not_oversized.py`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

## 39. Closed 2026-10-24, scheduled operator cycle: this file's own section 6 Gemini-billing row still quoted the dollar figure section 2 already marks superseded, the file's own named defect class recurring inside one document

Attached per STEP 0, clean (fetch, unshallow, `checkout main`, ff-only onto `a0412bef3`). Read `GOALS.md` context, `BACKLOG-2026-09-07.md` sections 0-7 directly, `BACKLOG-2026-H2.md`'s ordering note, `ROADMAP-2026-2029.md`, `CLAUDE.md`, and the real head (newest-first) of `ops/NIGHTLY-LOG.md`, four entries. Pulled all 10 open GitHub issues fresh via the API: unchanged (#42, #40, #15, #35, #2, #33, #21, #31, #29, #18), all `decision`/`blocked-on-art`, none newly actionable, matching every cycle logged today. Confirmed epics 1-5 (measurement, broken/dishonest, traffic, conversion, product) are genuinely exhausted: sections 2-5 are Done or Hold except the section 6 owner gates, all already built up to the gate.

**Reading section 6 directly rather than trusting it, found a real instance of this file's own section 7 defect class inside itself.** Row C5 (section 2, the Gemini billing pilot) already carries a note that its original cost figures, $13.53 (card heroes + zone rejects) to $47.26 (a full re-shoot), are superseded by `OWNER-ACTIONS.md` 1b's later, more careful measurement, because most of what that first estimate priced turned out to be free local retries, not billing-gated at all. Section 6's own "Owner gates" row 3, for the identical ask, still quoted the stale $13.53/$47.26 pair with no such note, a day-of-fix inconsistency between two rows of the same section. Verified the correct figure directly against `OWNER-ACTIONS.md` 1b's own cost table rather than guess: the "Everything" row reads $8.62 (Flash), $4.32 (Flash batch), $29.62 (Pro), the same table row C5 already points to.

**Fixed the row and built the gate, not just the one instance.** Row 3 corrected to the current range with a dated note. New `gate_backlog_gemini_cost_current` in `ops/preflight.py`, same narrow shape as its siblings `gate_backlog_h2_video_count_current` and `gate_linkedin_drafts_price_current` just above it: reads OWNER-ACTIONS.md 1b's cost table and BACKLOG section 6's Gemini row, fails if the row's dollar figures do not match either the Flash-batch-to-Pro or Flash-to-Pro range. Wired into `main()` right after its `gate_backlog_h2_video_count_current` sibling. `ops/tests/test_gate_backlog_gemini_cost_current.py` written first against the old row (fails, naming both the stale and current figures), then against the fixed row (passes); 6/6 cases including both reshaped-file warn paths. Re-ran against the real committed documents: 0 FAIL.

**Verified:** `python3 -c "import ast; ast.parse(...)"` on `ops/preflight.py` clean. `python ops/affiliate.py --check`: 165 documents, clean. `preflight.py` run in the background to completion: 0 FAIL across every gate (roughly 130) before the documented `gate_tests` headless-Chromium sandbox hang; confirmed the hang was real rather than assumed, by checking process 741's elapsed time against its CPU time twice (302s elapsed/19s CPU, then 318s elapsed/19s CPU, 16s apart with zero CPU progress) before killing it and reporting unchecked past that point. `PYTHONIOENCODING=utf-8 python ops/inbox_agent.py --apply`: no mail credential in this sandbox, reported unchecked, not assumed empty. No price or product touched, so `ops/stripe_catalog.py`/`check_sellable.py --deep` do not apply this cycle.

**Went well:** the fix found itself inside a routine read of the live queue rather than a dedicated cold-read sweep, and it is small, verified and gated rather than merely logged.

**Did not go well:** nothing new; this is the same "source corrected, artifact never re-derived" shape the last dozen entries keep finding in a different document each time, now caught a thirteenth time rather than prevented a thirteenth time, because each instance still needs a human-shaped read to notice the specific pair of rows.

**Changing next cycle:** none; no new pattern, just another instance of the one already being gated piecemeal.

**Next:** no further defect found this cycle beyond this one. Every epic ahead of operational honesty still dead-ends at a Phil decision or account action (owner gates section 6): Gemini billing, YouTube OAuth, Amazon/Etsy/Apple/Play accounts, the Search Console reports, issue #15 (Listmonk) and issue #42 (cadence). The next genuinely new workstream starts when Phil clears one of those or traffic moves enough to revisit `GOALS.md` section 5.

Pushed to main. `BACKLOG-2026-09-07.md`, `ops/preflight.py`, `ops/tests/test_gate_backlog_gemini_cost_current.py`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

---

## 38. Closed 2026-10-23, scheduled operator cycle: `gate_owner_actions_last_measured_current` moved ahead of the `gate_tests` sandbox hang, the same defect class the nightly-log gates were fixed for on 2026-10-21

Attached per STEP 0, clean (fetch, unshallow, `checkout main`, ff-only onto `b1dff2617`). Read `GOALS.md`, `BACKLOG-2026-09-07.md` sections 0-7, `CLAUDE.md`, the last four `NIGHTLY-LOG.md` entries, and GitHub's 10 open issues (all `decision`/`blocked-on-art`, unchanged, confirming issue #42's standing claim rather than carrying it forward). `ops/cold_read_ledger.py --next`: 292 of 292 files ledgered, 0 un-ledgered candidates. `ops/cold_read_ledger.py --stale`: 0. `ops/keyword_demand.py`'s own current gap list (166 of 2822) is noise (video games, cribbage tournaments, PC hardware), not household-organization demand. Confirmed rather than assumed: there is genuinely no unblocked backlog or content-gap item left to execute this cycle, matching every PM/operator cycle today.

**Looked for the thing those cycles' own evidence pointed at instead of re-confirming exhaustion a second time.** `OWNER-ACTIONS.md`'s own header names the exact recurring failure: `gate_owner_actions_last_measured_current` caught its own marker drifting stale on the real GitHub runner at least twice today (CI runs 2300 and 2301, both red), never once caught by a local `preflight.py` run, because this sandbox's `gate_tests` hangs and kills every local run before reaching that gate, which sits well after it in `main()`'s call order. This is the identical shape the 2026-10-21 entry already fixed for three nightly-log gates (moved them ahead of `gate_tests` "since they are pure file-parsing with no reason to sit behind the Chromium sandbox hang"), confirmed by reading `gate_owner_actions_last_measured_current()`'s own body: one regex read of `OWNER-ACTIONS.md`, no subprocess, no browser, no network.

**Fixed at the root, not by bumping the marker again.** Moved `run_gate(gate_owner_actions_last_measured_current)` out of its old position (after `gate_tests`, alongside `gate_experiment_owner_actions_surfaced`, `gate_image_prompts_tiers_current`) into the dedicated early block `main()` already carries for this exact purpose, right after `gate_nightly_log_no_duplicate_entries` and before `gate_existing`. Left `gate_experiment_owner_actions_surfaced` where it was: no evidence of it ever failing in CI, so moving it would have been a second, unverified change riding on this one (`CLAUDE.md` 5c/5d).

**Verified:** extended `ops/tests/test_gate_owner_actions_last_measured_current.py` with a ninth case, the same call-site assertion the nightly-log test already proves for itself (`inspect.getsource(preflight.main)`, asserts the gate name appears before `run_gate(gate_tests` in source order). Fail-then-pass proved directly: `git stash push -- ops/preflight.py` then rerunning the test gives `FAIL: gate_owner_actions_last_measured_current is not called before gate_tests`; restored, 9/9 pass. Ran the gate directly against the real committed `OWNER-ACTIONS.md`: 0 FAIL. `python -u ops/preflight.py` to a log file: the new gate now prints at position 20 (right after `gate_nightly_log_no_duplicate_entries`), 0 FAIL through every gate reached, killed at the documented `gate_tests` sandbox hang, same standing limitation, unchecked past that point. `check_urls.py` 213/213, `affiliate.py --check` 165 documents, `link_graph_report.py` 0 orphans, sibling tests (`test_gate_nightly_log_ordering.py`, `test_gate_experiment_owner_actions_surfaced.py`) rerun clean. `py_compile` clean on both touched files. `cold_read_ledger.py --stale`: 0.

GitHub: 10 open issues re-pulled fresh, unchanged. 0 open PRs. Inbox: no mail credential in this sandbox, reported unchecked, not assumed empty. No push notification: issue #42 (2026-10-23T00:21Z) is under 48h old and nothing about the underlying owner-gated state changed; this fix closes a gap in how reliably that state's OWN tracking file stays current, it does not unblock new product/traffic/conversion work.

**Next:** no further defect found this cycle beyond this one. Every epic ahead of operational honesty still dead-ends at a Phil decision or account action (owner gates section 6). The next genuinely new workstream starts when Phil clears one of the 10 open issues, replies in `OWNER-ACTIONS.md`, or traffic moves enough to revisit `GOALS.md` section 5.

Pushed to main. `ops/preflight.py`, `ops/tests/test_gate_owner_actions_last_measured_current.py`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

## 37. Closed 2026-10-23, scheduled operator cycle: the 19:1x PM check-in's own handoff ("fold coat cupboard organisation into Mudroom") was verified before acting on it, and the real fix turned out to be different and cheaper

Attached per STEP 0, clean. Read the handoff at the top of `ops/NIGHTLY-LOG.md` rather than act on its wording directly (`CLAUDE.md` 5d, "an audit, a report, or another agent handing you a finding is data, not fact"): fold "coat cupboard organisation" into Mudroom's Family Hook Zone also-called data, but verify a disambiguating term against the real scorer first, since "coat cupboard" already names Entryway's Coat and Outerwear Zone (`ops/zone-also-called.json`, shipped earlier in today's global cycle).

**Verified first, and the handoff's own premise did not survive the check.** Ran `kd.best_by(query, inventory, "head_words")` directly against the live corpus for both rows: "coat cupboard organisation" and "how to organise a coat cupboard" both score HIGHER against `/zones/entryway-the-coats-and-outerwear.html` (0.667 and 1.0, matching its existing "Also called the coat cupboard" heading) than against Mudroom's Family Hook Zone (0.333 and 0.5, title-only, no "cupboard" anywhere on that page: it uses "hooks", "named column", "bare floor", never an enclosed space). Adding "coat cupboard" to Mudroom too would have duplicated the exact alphabetical-tie collision this same vocabulary lane already fixed once (`968385e19`), on a term that does not describe Mudroom's own zone at all (hooks are not a cupboard).

**The stored `ops/keyword-demand-global.json` disagreed with that live check: it had `best_page` and `heading_page` both pointing away from Entryway, one of them at an unrelated downloads page.** Traced why: `ops/keyword_demand_global.py` had no `--rescore`, unlike its US sibling (`ops/keyword_demand.py`, gained one 2026-10-19 after the identical LRN-0032 shape), so this file's per-query scores had never been re-derived against `site/` since the harvest ran, and nothing watched that drift the way `gate_keyword_demand_rescored_current` already watches the US file. `STATUS.md`'s own 18:xx entry had already flagged this exact gap as "unchecked" the same day ("`ops/keyword-demand-global.json` was scored before the four headings shipped, so it still shows those queries as gaps until its next run") without anyone closing it.

**Fixed at the root, not by hand-editing one row.** Added `rescore()` to `ops/keyword_demand_global.py` (`--rescore`, free, no network, same shape as the US tool's), ran it for real: 2,183 queries re-scored against 221 live pages, 20 moved off `gap` corpus-wide (211 to 191), including both coat-cupboard rows, now `partial` and `covered` respectively with `heading_page` correctly pointing at Entryway's zone. New `gate_keyword_demand_global_rescored_current` in `preflight.py`, reusing the same pure `keyword_demand_rescore_staleness_problem()` the US gate already uses (it does not care which file it is told about), wired into `main()` immediately after its sibling.

**Verified, not assumed.** `ops/tests/test_gate_keyword_demand_global_rescored_current.py` (5 cases: missing file does not warn, missing `scored_against_commit` warns and names the right tool, 0 real commits since rescore does not warn, 5+ real commits since a real historical commit does warn, the real freshly-rescored file passes clean), fail-then-pass proved directly: with `ops/preflight.py`'s own addition stashed out, the test crashes with `AttributeError: module 'preflight' has no attribute 'gate_keyword_demand_global_rescored_current'`; restored, all 5 pass. Sibling tests (`test_gate_keyword_demand_rescored_current.py`, `test_gate_keyword_demand_global_not_stale.py`) rerun clean, confirming no regression. Also closed in the same cycle: `ops/cold-read-ledger.json`'s `check_cron_cadence.py` entry had gone stale the moment the 19:1x check-in's own commit (`d3d824c4c`) fixed its `WORKFLOWS` registry without bumping the ledger date; checked directly (`WORKFLOWS` now lists all 11 real cron-scheduled `.github/workflows/*.yml` files, confirmed by a fresh `grep -l '^  schedule:'`) and the ledger entry corrected. `check_urls.py` (213/213), `audit_pages.py` (218/0), `fix_dashes.py --check` (0/0), `affiliate.py --check` (165 documents), `link_graph_report.py` (0 orphans), `py_compile` sweep of all touched files, clean. Full `preflight.py` hit the documented `gate_tests` sandbox hang again (killed cleanly, stale lock directory removed); the narrower checks above stand in, the standing workaround every recent cycle uses.

GitHub: all 10 open issues re-pulled fresh, unchanged, all `decision`/`blocked-on-art`, none newly actionable. Inbox: no mail credential in this sandbox, reported unchecked, not assumed empty. No push notification sent: the standing one (issue #42, sent 2026-10-22) is not yet 48h old and nothing material has changed in the owner-gated state.

**Next:** this closes the global-harvest rescore gap cleanly; no further "coat cupboard"-shaped vocabulary work is warranted on Mudroom. Otherwise unchanged: every epic ahead of operational honesty still dead-ends at a Phil decision or account action (owner gates section 6).

Pushed to main. `ops/keyword_demand_global.py`, `ops/keyword-demand-global.json`, `ops/KEYWORD-DEMAND-GLOBAL.md`, `ops/preflight.py`, `ops/tests/test_gate_keyword_demand_global_rescored_current.py`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price, product or served page touched; not customer-facing in itself, so IndexNow not applicable.

---

## 36. Closed 2026-10-23, scheduled operator cycle: "airing cupboard" folded into the zone-level also-called data, and the zone-level mechanism itself had no gate at all, unlike its room-level twin

**Did:** Attached clean per STEP 0 (fetch, unshallow, `checkout main`, ff-only onto `b7a8342a1`, tree clean). Read `GOALS.md`, this file's sections 0 and 7, `ROADMAP-2026-2029.md`, `CLAUDE.md`, the last several `NIGHTLY-LOG.md` entries. The 17:4x and 18:1x PM check-ins both named the same unclaimed, non-Phil-gated task by hand: fold "airing cupboard" into also-called data for the guest-bathroom/hall-closet linen zones, from `ops/keyword-demand-global.json`'s own rank-1 gap rows. All 10 GitHub issues re-pulled fresh: unchanged, all `decision`/`blocked-on-art`. `inbox_agent.py --apply`: no mail credential in this sandbox, reported unchecked, not assumed empty.

**Verified the claim before acting on it.** Read the real row rather than trust the handoff's wording: `ops/keyword-demand-global.json` has exactly one row containing "airing cupboard" ("how to organise towels in airing cupboard", rank 1, gb/au/in, status gap), and its `best_page` is `/zones/guest-bathroom-the-guest-linen-zone.html`, not Hall Closet's Linen Shelf Zone. Hall Closet already carries a different, separately-measured term ("linen cupboard", 13 queries, added earlier the same day). Matching that same convention (one term goes to the zone its own measured row points at, not both), added "airing cupboard" only to `Guest Bathroom|Guest Linen Zone` in `ops/zone-also-called.json`, queries 1, covered 0, sourced to the same harvest file and date as its siblings.

**Found while verifying, not after shipping: the zone-level also-called mechanism (`ops/zone-also-called.json` / `zone_also_called_html()`) had no gate at all**, unlike `ops/room-also-called.json`'s own `gate_also_called_is_heading`, closed 2026-10-02 for the exact defect class this is: a household synonym can only move a `keyword_demand.py` query off `gap` if it lands inside a real `<h1>`-`<h3>` heading, and nothing checked that a committed zone-level entry actually renders there rather than silently drifting (an edit to the JSON with no rebuild, or a future template change that drops the heading). The zone-level map already had three older entries with no coverage at all.

**Fixed:** `python ops/build_zone_pages.py` regenerated the one changed page (confirmed live: `Also called the airing cupboard` now renders inside a real `<h2>` immediately after the H1, before the `<p class="lede">`'s sibling). New `check_zone_also_called_is_heading()` and `gate_zone_also_called_is_heading()` in `ops/preflight.py`, the zone-scoped twin of the room-level pair, re-deriving the expected zone/name map from the real committed `ops/zone-also-called.json` and diffing it against the real `site/zones/*.html` files; wired into `main()` immediately after `gate_also_called_is_heading`.

**Verified:** `ops/tests/test_gate_zone_also_called_is_heading.py` (6 cases, including the real committed site) passes. Fail-then-pass proved directly against the real file, not only the test's synthetic cases: planted the pre-fix shape (the real `<h2>` downgraded to a plain `<p>`) on the real committed `site/zones/guest-bathroom-the-guest-linen-zone.html`, called `check_zone_also_called_is_heading()` directly and watched it fail by name citing the file and the hidden word, restored byte-for-byte (confirmed via `md5sum`), reran clean. `py_compile` clean on both touched Python files. `check_urls.py` (213/213), `audit_pages.py` (218/0), `fix_dashes.py --check` (0/0), `link_graph_report.py` (0 orphans), `affiliate.py --check` (165 documents) all clean after. `ops/preflight.py` run unbuffered to completion in the background: 0 FAIL, 0 WARN through every gate reached (including the new one, confirmed in the log by name) before the documented `gate_tests` headless-Chromium sandbox hang; killed there per standing practice, reported unchecked past that point, not assumed passing. `cold_read_ledger.py --stale`: 0 of 292.

**Went well:** checking the handoff's own wording against the real measured row before acting on it, rather than adding the term to both zones because the note said "guest-bathroom/hall-closet", caught that only one of the two actually has evidence; and the zone-level gate gap (found while verifying a one-line content fix) is a real, previously-unguarded defect class closed before it could recur silently.

**Did not go well:** none new this cycle.

**Changing next cycle:** none.

**Next:** the remaining rank-1 gap rows in `ops/keyword-demand-global.json` are mostly autocomplete noise unrelated to this site's real content (classroom benches, gas-fire stones, outdoor-step handrails, dollar-store brand names, a staircase trivia question) and do not warrant also-called entries; a future cycle should treat this lane as exhausted for now rather than re-scan the same rows. Otherwise unchanged: every epic ahead of operational honesty still dead-ends at a Phil decision or account action (owner gates section 6).

Pushed to main. `ops/zone-also-called.json`, `site/zones/guest-bathroom-the-guest-linen-zone.html`, `ops/preflight.py`, `ops/tests/test_gate_zone_also_called_is_heading.py`, `ops/sitemap-content-hashes.json`, this entry, dashboard files. No price or product touched; one existing free page changed, not added, so `IndexNow` will pick it up on its next successful submission rather than needing a fresh one.

---

## 35. Closed 2026-10-23, scheduled operator cycle: `ops/keyword_demand_global.py` shipped minutes earlier with no staleness gate and no scheduled refresh, the same gap `gate_keyword_demand_not_stale` was built to close for its US sibling

**Did:** Attached clean (unshallow, `checkout main`, ff-only onto `b7afb5112`, tree clean). All 10 GitHub issues re-pulled fresh via the API: unchanged, all `decision`/`blocked-on-art`, matching issue #42. `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty. `preflight.py` run unbuffered to completion in the background: 0 FAIL, 0 WARN through every gate before the documented `gate_tests` headless-Chromium sandbox hang. A concurrent session was actively pushing real work the whole time this cycle ran (international keyword-demand harvest, visitor-country tracking, USD price labels, three to four pushes inside twenty minutes); re-fetched and ff-only merged twice mid-cycle rather than let the local branch drift, confirmed no file overlap with this cycle's own changes before each merge.

**Found, not assumed:** `ops/cold_read_ledger.py --stale` named `site/assets/js/site.js` as touched since its last ledger entry; read the one commit since (`2140c7f8`, USD price-suffix rendering) and found it correct (guards on `typeof p.price === "number" && p.price > 0`, so the null/quote and 0/free branches above it cannot be hit), ledgered clean. `--next` then surfaced `ops/keyword_demand_global.py` (new, 0 mentions) as the lowest-covered un-ledgered file. Read it in full against `ops/keyword_demand.py`'s own precedent line by line (interface shapes for `score_rows`/`refusal_reason`, the `localise()` regex's `\borganiz` prefix match against every inflection, the pre/post canary-merge logic): a faithful, correctly-scoped port, no defect found in the harvest logic itself. What was missing is structural: no `ops/tests/test_keyword_demand_global.py`-shaped test suite risk aside, it shipped with no `gate_X_not_stale` entry in `preflight.py` and no scheduled workflow, so its first (hand-fired) reading could sit unrefreshed indefinitely, exactly the shape `GOALS.md`'s own account of the original US harvest describes before `keyword-demand.yml` and `gate_keyword_demand_not_stale` existed for it.

**Fixed:** `keyword_demand_global_staleness_problem()` and `gate_keyword_demand_global_not_stale()` in `ops/preflight.py`, modelled directly on the US harvest's own pair (14-day ceiling, not 10, since this reading has no dedicated workflow yet to hold it to a tighter one); wired into `main()` immediately after its sibling. `.github/workflows/keyword-demand-global.yml` (new), same shape as `keyword-demand.yml`, Thursdays rather than Wednesdays so the two harvests never compete for the same hour's patience from Google's side.

**Verified:** `ops/tests/test_gate_keyword_demand_global_not_stale.py` (6 cases, same shape as the US test, fail-then-pass proved: missing file, 21-day-stale, a real-shaped 15-day-old reading, 2-day-fresh, no `checked_at`, unparseable `checked_at`) all pass. Called `gate_keyword_demand_global_not_stale()` directly against the real committed `ops/keyword-demand-global.json` (checked_at `2026-10-23T17:21:09Z`): clean, no warning. New workflow YAML parsed with `yaml.safe_load`. `py_compile` clean on all three touched Python files. `check_urls.py` (213/213), `fix_dashes.py --check` (0/0) clean after. `ops/cold_read_ledger.py --stale`: 0 of 292, both newly-reviewed files recorded.

**Went well:** the standing cold-read practice (check what a concurrent session just shipped, rather than only re-verifying old "exhausted" claims) found a real, concrete, non-Phil-gated gap in work that was itself only minutes old.

**Did not go well:** confirmed, not newly found: this gate is registered after `gate_tests` in `main()`'s call order, the same region its sibling `gate_keyword_demand_not_stale` already sits in, so neither ever actually executes in this sandbox's own interactive `preflight.py` runs (all of which hang at `gate_tests` first). `checks.yml` runs `python3 ops/preflight.py` directly on a GitHub-hosted runner, where `gate_tests` is not known to hang, so both gates do run there; this is a pre-existing structural quirk of the gate list's ordering, not something this cycle introduced, and not fixed here since fixing the ordering is a separate, larger change touching every gate after `gate_tests`.

**Changing next cycle:** none.

**Next:** nothing newly unblocked. Same standing state: all five epics ahead of operational honesty dead-end at a Phil decision or account action. The concurrent session's own international-demand and visitor-country work is still landing; a future cycle should read `GOALS.md`'s O1 section once it settles, since this is the first new traffic-and-distribution evidence in days.

Pushed to main. `ops/preflight.py`, `ops/tests/test_gate_keyword_demand_global_not_stale.py`, `.github/workflows/keyword-demand-global.yml`, `ops/cold-read-ledger.json`, this entry, dashboard files. No price, product or served page touched; not customer-facing, so IndexNow not applicable.

---

## 34. Closed 2026-10-23, scheduled operator cycle: this file's own numbered "Closed" sections (8 and up), the one gap section 32's fix explicitly deferred as a future cycle's job

**Did:** Attached clean (unshallow, `checkout main`, ff-only onto `415125043`, tree clean). All 10 GitHub issues re-pulled fresh: unchanged, all `decision`/`blocked-on-art`, matching issue #42, no reply from Phil since `a791b54c4` (2026-10-22). `inbox_agent.py --apply`: no mail credential in this sandbox, unchecked, not assumed empty. `preflight.py` run to completion in the background: 0 FAIL, 0 WARN through every gate before the documented `gate_tests` headless-Chromium sandbox hang (killed there at 183s, CI shows this same workflow green on the latest push, run 2306). `deploy-verdict.json` re-derived directly: still current, 0 commits since touching `site/`, `ops/build_*.py` or `mcp/`. Sections 0-7 and `OWNER-ACTIONS.md`'s open list read directly: exhausted or Phil-gated again, no new ground since the last several dozen cycles.

**Found:** rather than stop at "exhausted," sized this file's own numbered sections directly: sections 8 through 33 (the "Closed"/"Done" narrative record this same cold-read lane has been appending to all day) total 105KB of this file's 304KB, read by STEP 1 of the operating prompt every single cycle as part of "the CURRENT queue". `ops/rotate_backlog.py`'s own docstring had already named this exact gap and deliberately left it out of scope ("sections ... 8-31 mix open rows with closed ones or use a different per-item numbering ... a different, higher-risk job ... left for a future cycle"). Checked rather than assumed: a repository-wide grep found nothing that references any of these section numbers by name (unlike the B9/D5-style row ids in sections 2-4 that motivated the original caution), so lifting a whole numbered section out is as safe as archiving a `NIGHTLY-LOG.md` entry, not the higher-risk job it looked like.

**Fixed:** new `ops/rotate_backlog_closed.py` (`--check`/`--apply`, `--days`), modelled on `ops/rotate_nightly_log.py`'s date-window retention rather than `ops/rotate_status_history.py`'s keep-only-latest BLOCKER-001 shape, because these sections are independent closed items, not one evolving status field. `find_sections()` locates every `## N. Closed/Done ...` heading with N >= 8 by its own heading-line date; `plan_rotation()` removes whole overdue spans and returns the rest byte-identical outside those spans; `apply_archive()` prepends newly archived sections, newest first, above whatever `BACKLOG-2026-09-07-CLOSED-ARCHIVE.md` (new file) already holds, same convention as this file's sibling archives. New `gate_backlog_closed_sections_not_oversized` in `preflight.py`, same WARNING-not-FAIL, 14+7-day buffer convention as its six siblings above, wired into the same no-browser-no-network block ahead of `gate_tests`.

**Verified:** dry-run against a scratch copy with an artificial cutoff first (15 of 26 sections correctly identified and moved, content proven present verbatim in the original, idempotent on a second pass, clean markdown at the section-7/section-23 boundary) before writing any test. `ops/tests/test_rotate_backlog_closed.py` (7 cases: section-number filtering, undated sections kept live, correct newest-first archive order, losslessness, idempotency, archive-prepend behaviour, a mismatched-header refusal) and `ops/tests/test_gate_backlog_closed_sections_not_oversized.py` (5 cases, fail-then-pass proved against synthetic text) both pass. Against the real file: `--check` reports CLEAN, 26 sections, 105,008 bytes, all within the 14-day window (nothing is actually overdue yet; the oldest, section 8, is 12 days old), so no `--apply` was run on the real file this cycle, only the gate and tool were added, ahead of the gap rather than after it, unlike every rotation before it. `gate_backlog_closed_sections_not_oversized` run directly against the live file: clean. `gate_backlog_done_table_not_oversized`, `gate_status_blocker001_not_oversized` and `gate_ops_python_syntax` re-run directly: all clean, confirming this change touched nothing of theirs. `fix_dashes.py --check` 0/0 full-repo. `py_compile` sweep of all four touched/added files clean.

**Went well:** the repository-wide grep for section-number references before starting turned a "higher-risk job" the original author correctly deferred into a safe one; building the dry-run scratch-copy proof before writing a single test or touching the real file caught the newest-first archive ordering and the section-boundary whitespace behaviour early, with nothing to undo.

**Did not go well:** nothing new found beyond the one gap; this is the eighth instance of the identical unbounded-growth shape found in this repository today alone (`NIGHTLY-LOG.md`, `STATUS.md` twice, `CHECKIN-LOG.md`, `OWNER-ACTIONS.md`, this file's "Done this week" table, and now this file's own "Closed" sections), which is itself worth naming plainly rather than treating each occurrence as a fresh surprise.

**Changing next cycle:** none.

**Next:** no numbered section is actually due for rotation yet; the gate exists to catch it once one is. `STATUS.md`'s remaining long, unread sections (`# 1. Status Metadata`, `# 4. Production Status`, `# 14. Active Major Workstreams`) and sections 2-4 of this file are still the only named, unexamined candidates, and both were already correctly deferred by the cycles that named them.

No price, product or served page touched; not customer-facing, so IndexNow not applicable.

## 33. Closed 2026-10-23, scheduled operator cycle: `STATUS.md`'s own `BLOCKER-001`, the single biggest unrotated chain left, the one this cycle's own cold read actually found

**Did:** Attached clean per STEP 0 (unshallow, `checkout -B main origin/main`, ff-only, tree clean). All 10 GitHub issues re-pulled fresh via the API: unchanged, all `decision`/`blocked-on-art`, matching issue #42. `git log --author="Phil Kling"` confirmed his last commit is still `a791b54c4` (2026-10-22), nothing new since. Sections 0-7 of this file and `OWNER-ACTIONS.md`'s "Open, ranked" list read directly: exhausted or Phil-gated again. `inbox_agent.py --apply`: no mail credential in this sandbox, same standing limit, unchecked rather than assumed empty. Rather than stop at "exhausted" on the log's own repeated word, sized every `*.md` file directly: `STATUS.md` was still 319KB even after today's earlier Production Knowledge/Immediate Focus fixes, and its own section 17 (`BLOCKER-001`) was 135KB of that, by far the largest section in the file and bigger than any section this cold-read lane had checked by name today.

**Found:** `BLOCKER-001` had grown to 97 entries back to 2026-09-25, the identical unbounded-growth shape this same day already fixed for `NIGHTLY-LOG.md`, `CHECKIN-LOG.md`, `STATUS.md`'s own two sibling fields, `OWNER-ACTIONS.md`'s preamble, and this file's own "Done this week" table, and nobody had checked it because the existing gates that read `BLOCKER-001` (`gate_status_deploy_verdict_current`, `gate_status_deploy_gap_count_current`) only ever check whether its NEWEST entry is current, never the chain's size. Unlike the Production Knowledge chain (one entry per physical line, newest first), this one is appended to oldest first and an entry can span more than one paragraph (its first entry alone carries two plain continuation paragraphs after its own bold opening), so it needed its own read rule rather than reusing the existing one unchanged.

**Fixed:** `ops/rotate_status_history.py` gained `split_blocker1_chain()`/`plan_rotation_blocker1()` (`--check-blocker1`/`--apply-blocker1`): a new entry starts only where a paragraph's own text opens with a bold run, every following paragraph until the next one that does is a continuation of the entry before it, and the function proves its own split is lossless (entries plus their separators reconstruct the original span exactly) before returning, raising rather than guessing if that check fails. New `gate_status_blocker001_not_oversized` in `preflight.py`, same WARNING-not-FAIL, buffer-of-3 shape as its five siblings above, wired into the same no-browser-no-network block ahead of `gate_tests`.

**Verified:** `ops/tests/test_rotate_status_history.py` (18 cases now, 6 new for this chain, including a round-trip proof run directly against the real committed `STATUS.md`) and `ops/tests/test_gate_status_blocker001_not_oversized.py` (6/6), both fail-then-pass proved against synthetic text before touching the real file. `--check-blocker1` (DUE, 97 entries) then `--apply-blocker1` then re-running the gate directly (CLEAN, 0 warnings). Diffed the real file before/after: everything outside `BLOCKER-001` byte-identical; all 96 archived entries confirmed present verbatim in `STATUS-ARCHIVE.md` (0 missing, checked by probing each entry's own opening text). `STATUS.md` dropped from 319KB to 186KB. Re-ran the two existing stale-citation gates that also read `BLOCKER-001` (`gate_status_deploy_verdict_current`, `gate_status_deploy_gap_count_current`) directly against the rotated file: both still clean, confirming the kept entry (the real, current `CLOSED 2026-10-23` state, build `1e15140736f2a808`, zero-commit gap) is exactly what those gates already expected. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0, full `py_compile` sweep of `ops/*.py` and `ops/tests/*.py` clean. Full `preflight.py` run in the background: 0 FAIL, 0 WARN through every gate reached, including the new one, before the documented `gate_tests` headless-Chromium sandbox hang (confirmed by CPU-flat evidence, 249s elapsed against 15s of CPU time, before being killed there); unchecked past that point, not assumed passing.

**Went well:** sizing every markdown file directly, rather than trusting the log's own repeated "exhausted" conclusion, found a real, concrete, non-Phil-gated gap the last several cycles' narrower cold-reads had not named; reusing the existing script and WARNING-gate shape kept this a mechanical extension rather than a new design, once the one real structural difference (oldest-first, multi-paragraph entries) was identified and tested rather than assumed away.

**Did not go well:** nothing new found beyond the one gap.

**Changing next cycle:** none.

**Next:** `STATUS.md`'s other long sections (`# 1. Status Metadata`, 59KB; `# 4. Production Status`, 20KB; `# 14. Active Major Workstreams`, 17KB) were sized but not read in full this cycle; none approached `BLOCKER-001`'s size and none is flagged as a correction chain by name, so none is an obvious next target without a closer read. Sections 2-4 of this file (A/B/C item tables) remain the lower-value, harder-to-safely-rotate target section 32 already named.

No price, product or served page touched; not customer-facing, so IndexNow not applicable.

---

## 32. Closed 2026-10-23, scheduled operator cycle: this file's own "Done this week" table had the identical unbounded-growth defect every sibling file above was already fixed for

**Did:** All 10 GitHub issues re-confirmed `decision`/`blocked-on-art` via the API; `cold_read_ledger.py --next` 289/289 ledgered, 0 stale, 0 un-ledgered; `inbox_agent.py --apply` confirmed no mail credential in this sandbox, same standing limit. Sections 0-6 and all open backlog rows genuinely exhausted/Phil-gated again, so this cycle picked up section 30's own deferred handoff pointer by going one file further than it named: `OWNER-ACTIONS.md`'s preamble (fixed that cycle) was not the only place this exact lesson, already recorded in this file's own sections 10, 28, 29 and 30, had not yet been applied. This file's own section 1 ("Done this week, for the record") table was 282KB across 48 rows back to 2026-09-07, over half the file's 568KB total, append-only and never rotated, while STEP 1 of the operating prompt reads this whole file as "the CURRENT queue... your work list" every single cycle. While building the fix, also found and left alone (out of scope, flagged rather than guessed at): one pre-existing row (originally "Two real defects found in the second-pass cold-read handoff... 2026-10-12") is missing a newline before a second, unrelated item ("...a scheduled workflow was missing from its own cadence checker... 2026-10-09"), merging two completed items onto one physical table line with the second item's own opening clause apparently lost. Left exactly as found: splitting it correctly would mean guessing at text that may no longer exist, and since the row's governing date keeps it live either way, nothing is lost by leaving the two halves joined.

**Fixed:** `ops/rotate_backlog.py`, modelled directly on `ops/rotate_nightly_log.py`'s date-cutoff shape but adapted for table rows instead of `## ` headings: it locates the table by two fixed anchors (the section heading and the `\n\n---\n\n## 1b.` boundary before it), reads each row's own completion date from inside its first bold span (an Evidence cell may cite an earlier date; that always sits later in the string), and moves every row older than the retention window into new `BACKLOG-2026-09-07-ARCHIVE.md`, newest material on top, same convention as every other archive here. Also found while building it: 14 of the 48 rows (the oldest continuous run, 2026-09-11 through 2026-09-22) had degraded to bare paragraphs missing both the table's leading `| ` and trailing ` |`, breaking table rendering for exactly those rows; `normalize_row()` re-wraps every row it touches in correct syntax, live or archived, fixing this as a side effect rather than a separate pass. New `gate_backlog_done_table_not_oversized` in `preflight.py`, same WARNING-not-FAIL, retention-plus-7-day-buffer shape as its NIGHTLY-LOG/STATUS/CHECKIN-LOG/OWNER-ACTIONS siblings, so this cannot quietly regrow unnoticed the way the live table did for six weeks.

**Verified:** `ops/tests/test_rotate_backlog.py` (11/11) and `ops/tests/test_gate_backlog_done_table_not_oversized.py` (5/5), both fail-then-pass proved against synthetic tables before touching the real file. Dry-run `--check` against the real file first (DUE, 45 of 48 rows, 282,262 bytes), then `--apply`, then `--check` again (CLEAN, 3 rows, 7,795 bytes). Diffed the real file before/after directly: everything outside the table byte-identical; every archived row's content confirmed present in the archive (0 missing); re-running `plan_rotation()` on the rotated output is a no-op (proved idempotent). `check_urls.py` 213/213, `audit_pages.py` 0 duplicate titles/descriptions, `fix_dashes.py --check` 0/0 (across the new archive file too), `affiliate.py --check` 165 documents, `link_graph_report.py` 0 orphans, all clean after. Full `preflight.py` run in the background, including the two new gates: 0 FAIL through every gate reached before the documented `gate_tests` headless-Chromium sandbox hang; killed there, reported unchecked past that point, not assumed passing.

**Went well:** reusing `ops/rotate_nightly_log.py`'s exact shape (pure `plan_rotation()`/`apply_archive()` functions, a CLI with `--check`/`--apply`, a WARN-only gate with a retention-plus-buffer window) made this a mechanical port rather than a new design, and meant the dry-run-then-diff verification sequence was already proven correct by its sibling's own test suite.

**Did not go well:** the pre-existing merged-row defect found while verifying is a real, if minor, data-quality gap in a file nobody has fully re-read start to finish in weeks; flagged above rather than guessed at.

**Changing next cycle:** none.

**Next:** sections 2-4 (A/B/C item tables, 77-80KB each) mix open rows with closed ones and are not safe to archive with this same blunt date-cutoff tool; sections 8-31 (the numbered "Closed"/"Done" record this very section continues) are individually small and a lower-value target than section 1 was. The "Last measured"/"List reviewed" paragraphs in `OWNER-ACTIONS.md`, named by section 31, are still open too. Any of the three is a reasonable next pick; none is urgent at today's size.

No price, product or served page touched; not customer-facing, so IndexNow not applicable.

---

## 31. Closed 2026-10-23, scheduled operator cycle: `OWNER-ACTIONS.md`'s
own preamble history, the exact gap section 30 deferred, fixed with more
care than a straight copy of the STATUS.md pattern

Sections 1-5 and all 10 open GitHub issues were exhausted/Phil-gated
again this cycle (independently re-derived: `ops/cold_read_ledger.py
--next` 288/288 ledgered, 0 stale; 10 open issues all `decision`/
`blocked-on-art`, none newly actionable). `inbox_agent.py --apply`: no
mail credential in this sandbox, unchecked, not assumed empty.

Picked up section 30's own handoff: `OWNER-ACTIONS.md`, the file Phil
reads directly to decide what needs him, carried two superseded chains
between its "List reviewed" paragraph and the "Resolved today" table
(14,875 bytes). One was a 2026-09-24/25 deploy-gap narrative of bold-
prefixed "Corrected"/"Widened"/"Reopened"/"RESOLVED"/"Added" paragraphs;
the other a single run-on "Earlier: <date>, item N ..." changelog back
to 2026-09-04. Read in full before touching anything, because the
caution section 30 recorded was real: unlike STATUS.md's own chain, this
one is not reliably newest-first (a 2026-09-24 paragraph sits after a
2026-09-25 one), so `ops/rotate_status_history.py`'s "keep the newest
entry live" rule would have kept a stale paragraph live and archived the
current one. Every entry in both chains is superseded regardless of
position: the deploy-gap figure they all chase is now tracked live by
`ops/deploy-verdict.json` and `STATUS.md`'s `BLOCKER-001`, and every
numbered item the changelog narrates has its own current row in "Open,
ranked by what they unblock" or "Resolved today".

**Fixed, with the shape the risk actually called for.** New
`ops/rotate_owner_actions.py` does not try to pick "the newest" entry:
it archives the whole bounded span (between the fixed phrase ending the
untouched "List reviewed" paragraph and the fixed "## Resolved today"
heading) verbatim into new `OWNER-ACTIONS-ARCHIVE.md`, and replaces it
with one pointer sentence naming where current deploy status lives and
which ask is still open. Deliberately left untouched: the "Last
measured" and "List reviewed" paragraphs themselves, both parsed by name
for their first sentence (`gate_goals_sessions_citations_current`,
`dashboard.py`'s `_owner_actions_traffic_citation()`), a different and
higher-risk job than archiving an already-dead narrative.

**Turned into a gate.** New `gate_owner_actions_history_not_oversized`
in `preflight.py` (WARNING, not FAIL, same severity as its STATUS.md and
`CHECKIN-LOG.md` siblings): measures the same bounded span and warns once
it grows past the pointer sentence's own size plus a 400-byte buffer.
Fail-then-pass proved directly: `ops/tests/test_gate_owner_actions_
history_not_oversized.py` (5/5) builds a synthetic 15-entry chain and
confirms the gate warns, then confirms a freshly rotated span, a single
short note still inside the buffer, a missing file, and a file with no
recognisable anchors all stay silent. `ops/tests/test_rotate_owner_
actions.py` (10/10) proves the rotation script itself: the span moves
verbatim, nothing outside it is touched, a missing or duplicated anchor
is refused rather than guessed past, and the archive write appends above
existing content without disturbing it.

**Verified against the real file, not just synthetic cases.** Ran
`--check` (DUE: 14,875 bytes live), then `--apply`, then `--check` again
(CLEAN: 357 bytes, the pointer sentence itself). Diffed the real file
before and after: everything from `## Resolved today` onward is byte-
identical (143,184 bytes both sides), and both archived boundary phrases
("Corrected 2026-09-25 00:1x" and the chain's last line, "...item 12
resolved, items 1a, 14 and 15 added by Phil directly, R3 added") are
present in `OWNER-ACTIONS-ARCHIVE.md` and absent from the live file.
`check_urls.py` 213/213, `audit_pages.py` 218/0, `fix_dashes.py --check`
0/0, `affiliate.py --check` clean. Full `preflight.py` run: every gate
through `gate_image_coverage` passed with 0 FAIL/0 WARN, including both
new gates, before hitting the documented `gate_tests` headless-Chromium
sandbox hang; killed there, reported unchecked past that point, not
assumed passing. Ledgered `ops/rotate_owner_actions.py` as clean in
`ops/cold-read-ledger.json`.

No price, product or served page touched; not customer-facing, so
IndexNow not applicable. The "Last measured"/"List reviewed" paragraphs
remain the next candidate for this treatment, deliberately deferred for
the same reason section 30 deferred the whole file: both are gate-parsed
by exact first-sentence shape, and rewriting them safely is a different
job from archiving dead narrative.

---

## 30. Closed 2026-10-23, scheduled operator cycle: `CHECKIN-LOG.md` had the identical unbounded-growth defect sections 10/28/29 above each already found and fixed elsewhere, and nothing had checked it

Sections 1-5 and all 10 open GitHub issues were again exhausted/Phil-gated
this cycle (a delegated survey independently re-derived the same state,
including that the `sort_scope` rollout section 2 once tracked is now
complete at 114 of 114 zones, not in progress). `ops/last-owner-
notification.json` was checked before considering a push on issue #42:
not yet 48h since the 2026-10-22 send and nothing material has changed,
so none sent.

The survey's one concrete, non-duplicate finding: `CHECKIN-LOG.md`,
written append-only, oldest first, once an hour by `ops/checkin.py`
since 2026-09-02, had never been rotated either, the identical shape and
trajectory `ops/NIGHTLY-LOG.md` was in before section 10's fix (8.1MB)
and STATUS.md's two fields were in before sections 28/29's fixes, just
earlier in its growth (673 entries, 294,571 bytes). Nothing before this
cycle checked whether it needed rotation.

**Fixed:** `ops/rotate_checkin_log.py`, built directly on `ops/
rotate_nightly_log.py`'s split_header_and_entries/plan_rotation/
apply_archive shape, with the one real structural difference made
explicit in code and proved by test: this log is oldest-first, so a
newly-archived chunk (always newer than what the archive already holds)
is appended AFTER the existing archive body, not before it, the mirror
image of the newest-first file's own convention. New `gate_checkin_log_
not_oversized` in `preflight.py`, modelled on `gate_nightly_log_not_
oversized` (same retention-plus-7-day buffer, same WARNING-not-FAIL
severity), wired into the same no-browser-no-network block that already
runs ahead of the `gate_tests` hang. Ran `--apply` once: 120 entries
(52,359 bytes) older than 30 days moved into the new `CHECKIN-LOG-
ARCHIVE.md`; live log now 553 entries, 242,212 bytes.

**Verified, not assumed:** `ops/tests/test_rotate_checkin_log.py` (7
cases, including the oldest-first archive-ordering difference) and
`ops/tests/test_gate_checkin_log_not_oversized.py` (4 cases) both
fail-then-pass proved directly. Checked that no entry was lost rather
than trusted the entry count alone: every one of the 673 original
headings is present exactly once across the two files after rotation,
diffed by heading line (one pre-existing duplicate heading, two entries
genuinely sharing a timestamp, was already present before this cycle
touched the file and is not a defect this rotation introduced).
`check_urls.py` 213/213, `audit_pages.py` 218/0, `fix_dashes.py --check`
0/0, `affiliate.py --check` clean, `link_graph_report.py` 0 orphans,
`py_compile` sweep of `ops/*.py` and `ops/tests/*.py` clean. Full
`preflight.py` hit the documented `gate_tests` sandbox hang again, same
standing limitation; every gate reached before it, including the new
one, ran with 0 FAIL/0 WARN. `inbox_agent.py --apply`: no mail
credential in this sandbox, unchecked, not assumed empty. No price,
product or served page touched; not customer-facing, so IndexNow not
applicable.

**Left for a future cycle, deliberately not attempted here:**
`OWNER-ACTIONS.md`'s own preamble (its "Last measured"/"List reviewed"
block, before the numbered items) carries the identical single-
paragraph correction-chain shape sections 28/29 fixed in STATUS.md.
Not touched this cycle: Phil reads and acts on that file directly, and
a safe generalized rotation there deserves more care than copying this
fix did.

## 29. Closed 2026-10-23, scheduled operator cycle: the "Immediate Focus" line two fields below section 28's own Production Knowledge fix had the identical unbounded-growth defect, in a different shape no existing tool read

Sections 2-6 and all open GitHub issues were exhausted/Phil-gated again
this cycle (independently re-derived: `ops/cold_read_ledger.py --next`
287/287 ledgered, 0 stale, nothing un-ledgered). `ops/keyword_demand.py
--rescore` was run first (stale against 10 commits per the preflight
warning); counts held (166 gap, 1450 partial, 1206 covered), and the 166
gap-tier queries were read in full looking for a real, in-scope synonym
or misattribution gap, the proven A21/A23/A24/A25/A26 shape. None found:
the list is almost entirely off-topic noise this site should not chase
(digital/PC-game organizing, medical bathroom symptoms, construction/
railing/stair queries, decor-only "pinterest"/"vastu"/"with mirror"
modifiers, and what reads as autocomplete-combinator spam around
"decluttering course/tutorial/pro guide"); the few on-topic candidates
(laundry, home office, bedroom, craft-supply organizing) score as `gap`
only on narrow aesthetic modifiers already outside this site's stated
scope (`CLAUDE.md` section 3: function over decor), so authoring nothing
against this list is the correct call, not a skipped opportunity.

Reading section 28's own fresh fix while confirming the above led
straight to its sibling defect: STATUS.md's "Immediate Focus" field
(section 30) had grown the exact same way Production Knowledge had, 27
corrections since 2026-09-02 piled onto it, but in a shape nothing
existing could rotate, because the field has no per-entry line break to
anchor a bold paragraph against; every correction was appended as a
plain sentence onto ONE physical line instead, 15KB of a 345KB file. All
27 did nothing but re-state the same deploy-gap figure the Production
Knowledge paragraph two fields above already tracks, by the chain's own
words ("THIS LINE NEVER CAUGHT UP WITH THE PRODUCTION KNOWLEDGE
PARAGRAPH ABOVE OR BLOCKER-001", written into the chain itself
2026-10-19).

**Fixed:** `ops/rotate_status_history.py` gained a second, parallel
operation (`split_focus_line`, `plan_rotation_focus`, `--check-focus`/
`--apply-focus`), built and verified separately from the existing
Production Knowledge chain logic because the two shapes are genuinely
different: one line, oldest first, sentence-appended, versus separate
bold paragraphs, newest first. Found live while building the splitter,
not after: a naive marker regex matched the base statement's own
comma-introduced clause ("...SINCE 2026-09-02, RE-CONFIRMED
2026-09-15: TRAFFIC...") as if it were a dated correction, which would
have archived away the real, still-true substance of the field and left
only its first six words live. Fixed by requiring a marker to be
preceded by sentence-ending punctuation (".", "\"", ")") once trailing
whitespace is stripped, never a comma; proved against the real base
statement and a synthetic case with the identical shape before trusting
the splitter on the live file. Ran `--apply-focus`: the base statement
(still true, unchanged) stays live with a new tail pointing at the
Production Knowledge paragraph and `BLOCKER-001` for current deploy
status instead of re-stating it; all 27 corrections moved verbatim,
newest-first, to `STATUS-ARCHIVE.md` (matching that file's own stated
convention, the opposite order from this field's native oldest-first).
Also hand-corrected the one specific stale claim the kept base statement
itself still carried (a named "LAST CONFIRMED" build/commit that went
stale hours after it was written, per BLOCKER-001's own history) rather
than leave a second embedded citation for this line to re-accumulate
around.

New `gate_status_immediate_focus_not_oversized` in `preflight.py`,
modelled directly on `gate_status_production_knowledge_not_oversized`
(same buffer of 3, same WARNING-not-FAIL severity, same reasoning): a
WARNING, not a FAIL: a long line wastes every later cycle's time
re-reading it, it does not ship anything broken to a customer.
`ops/tests/test_gate_status_immediate_focus_not_oversized.py` (7 cases)
and three new cases appended to `ops/tests/test_rotate_status_history.py`
(10-12) both fail-then-pass proved directly: ran each against a
synthetic oversized line (warns/returns entries correctly), a clean
line (silent/no-op), the exact comma-clause trap above (not
misclassified), and the real, just-rotated `STATUS.md` itself (silent).
`gate_tests()` already globs every `ops/tests/test_*.py` file, so no
separate `preflight.py` wiring was needed beyond the new gate's own
`run_gate()` call. Full `preflight.py` run: every gate reached before
`gate_tests` passed (0 FAIL, 0 WARN, including both the new gate and its
Production Knowledge sibling), then hung at the documented `gate_tests`
headless-Chromium sandbox limit, the same pre-existing, unrelated
limitation recorded throughout this file and `ops/NIGHTLY-LOG.md`; the
two new/modified test files were also run directly and both pass. No
price, product or served page touched; not customer-facing, so IndexNow
not applicable. Ledgered `ops/rotate_status_history.py` as re-touched
in `ops/cold-read-ledger.json`.

## 28. Closed 2026-10-23, scheduled operator cycle: STATUS.md's own section 24 rule ("do not allow this document to become an archive") had never been enforced for its section 30 "Production Knowledge" chain

Sections 2-6 and all 10 GitHub issues were exhausted/Phil-gated again this
cycle (independently re-derived: deploy gap 0 material commits re-checked
directly with `git log`, 10 open issues all `decision`/`blocked-on-art`
unchanged, `ops/cold_read_ledger.py --next` 283/283 ledgered, 0 stale). The
previous cycle's own handoff (cold-read `ops/bluesky_drafts.py` and
`ops/social_drafts.py` for the same missing-link shape as section 27)
checked out clean: both already append their `LINK`/`LINKS[...]` correctly,
confirmed by reading `build()` in each file, not assumed.

Read `STATUS.md` cold instead. Section 30's "Production Knowledge" chain
had grown to 37 bold-prefixed paragraphs (`**Production Knowledge,`/
`**Prior`/`**Superseded entry,`/bare `**WIDENED`/`**REOPENED` from before
any label convention existed) back to 2026-09-24, 38KB of the file's 358KB,
every single one explicitly superseding the entry below it ("the gap below
has reopened", "same standing limit as every entry below"), so only the
newest line was ever current. `STATUS.md` section 24 already states the
exact rule being broken: "move historical detail to the appropriate
long-term file. Do not allow this document to become an archive." Nothing
had ever carried that out for this field; `STATUS-ARCHIVE.md`'s own header
records one prior hand-done rotation of a different section (2026-09-17),
never automated, never repeated here.

**Fixed, not merely diagnosed.** New `ops/rotate_status_history.py`, built
on the same shape as the existing `ops/rotate_nightly_log.py`: `--check`
reports whether more than the newest entry is live, `--apply` moves every
entry but the newest into `STATUS-ARCHIVE.md`, verbatim and in original
order, nothing deleted (`CLAUDE.md` section 54). Applied once this cycle:
36 entries / 37,959 bytes moved; `STATUS.md` now carries 1 live entry (was
37), `STATUS-ARCHIVE.md` grew from 321,861 to 359,819 bytes with the new
batch placed above its existing content, same ordering `rotate_nightly_
log.py` already uses. Re-read both files directly after the move to
confirm no entry was lost, duplicated, or edited.

**Turned into a gate.** New `gate_status_production_knowledge_not_oversized`
in `preflight.py` (a WARNING, matching its `gate_nightly_log_not_oversized`
neighbour): fires once the chain exceeds the newest entry plus a buffer of
3. Fail-then-pass proved directly: deliberately broke `plan_rotation()`'s
own slice, watched `ops/tests/test_rotate_status_history.py` catch it (1
failure named exactly), reverted. `ops/tests/test_gate_status_production_
knowledge_not_oversized.py` (6/6) and `ops/tests/test_rotate_status_
history.py` (all checks) both new, both pass; `gate_tests` globs `ops/
tests/test_*.py` automatically, no separate wiring needed. Ran the gate
directly against the real (pre-rotation) `STATUS.md` first and confirmed it
warned naming 37 entries, then against the rotated file and confirmed
silence, rather than trusting either state unchecked. Added a one-line
cross-reference in `STATUS.md` section 24 pointing at the new gate and
script, so the rule and its enforcement are findable from the same place.

No price or product touched, no new page, IndexNow not applicable. Ledgered
`ops/rotate_status_history.py` in `ops/cold-read-ledger.json` as clean.

---

## 27. Closed 2026-10-23, scheduled operator cycle: the LinkedIn daily draft's connection note and corporate post had no link either, the same 2026-10-02 bug in two code paths the earlier fix never reached

Sections 2-6's structured queue was fully exhausted again this cycle (every
item Done, Closed, Hold, or Phil-gated), and GitHub issue #42 already tracks
the risk of an 18th consecutive "still exhausted" re-verification adding
nothing. Rather than write that cycle, this run read `ops/linkedin_drafts.py`
cold, the file the 2026-10-02 fix ("a post with nowhere to go cannot produce
an arrival") already touched once.

That fix only reached the three corpus POSTS (`LINK` appended once, inside
the `posts` loop). Two other sections of the same daily email, built by the
same `build()` function and mailed to Phil every morning, never got it:
the single CONNECTION NOTE (`note[2].format(**f)`, a direct message to
someone Phil actually knows, arguably the highest-propensity send in the
whole email) and the corporate B2B post (`corporate_block()`). Both still
ended in "free to read" or an offer to discuss, with literally no URL
anywhere in the message. Confirmed live by running `--preview`: neither
section printed a single `http`.

**Fixed.** `note[2].format(**f)` and the corporate `body` now each get a
trailing blank line and a link appended, same shape as the existing posts
loop. The connection note reuses `LINK` (`book.html?from=li`), since it is
selling the same free book the posts are. The corporate post gets its own
`CORP_LINK` (`corporate.html?from=li`), since that pitch is paid consulting,
not the free book, and sending a B2B lead to the consumer ebook page would
be a second, self-inflicted defect. Checked both word caps before shipping:
the longest connection-note body is 76 words against a 100-word cap, the
longest corporate body is 100 against 130; appending one more "word" (a
URL has no spaces) leaves both comfortably clear, confirmed by running
`build()` across 40 rotation days with no assertion failure.
`ops/tests/test_linkedin_drafts.py` (4/4, unrelated rotation-mechanics
tests) still passes.

**Turned into a gate**, since the root cause was that nothing checked the
NOTE or the CORPORATE block specifically, only the posts loop's own `LINK`
constant. New `gate_linkedin_drafts_every_item_has_link` in `preflight.py`:
builds a real day's draft via `build(record=False)` (a pure preview call,
no rotation side effect) and checks the connection-note section and the
corporate-post section each independently for a `http` URL, plus a
standing check that the posts section has not regressed to the original
2026-10-02 shape. Fail-then-pass proved directly: `git stash` on
`ops/linkedin_drafts.py` reverted it to the pre-fix body, the gate correctly
failed naming both missing links, `git stash pop` restored the fix, the
gate passed clean. Wired into `main()` after
`gate_corporate_linkedin_claims_current`.

`preflight.py`: all 83 gates before `gate_tests` ran clean (0 FAIL, 0 WARN)
in a full run this cycle; `gate_tests` itself hung on the same documented
headless-Chromium sandbox egress refusal (`redirector.gvt1.com`,
`www.google.com`) every recent cycle's own account already names, unrelated
to this change, and was killed after several minutes rather than assumed
past. No price or product touched. Ledgered in `ops/cold-read-ledger.json`
as fixed.

---

## 26. Closed 2026-10-22, scheduled operator cycle: `ops/build_product_images.py`'s hardcoded Manual page index was already wrong in this sandbox, the designated next cold-read

Sections 2-6 are all Done, Closed or Phil-gated (YouTube OAuth, Search Console
reports, Gemini billing, Amazon KDP/Etsy, Apple/Play accounts); the 22:1x and
22:4x PM check-ins and the 2026-10-22 scheduled operator cycle before this one
had each independently named the same designated next step:
`ops/cold_read_ledger.py --next` returns `ops/build_product_images.py` (369
lines, un-ledgered, written by the shop product-image commit `833401444`),
the only genuinely unblocked, never-reviewed surface this period found.

Read in full. `manual_spread()`, one of the nine product-tile makers, prints
the Manual's own HTML to PDF with a headless browser and crops a fixed page
index (page 22) for the zone-name-and-six-passes sample shown on
`product-manual.jpg`. **Reproduced live, not suspected:** printing the same
committed `content/manual/micro-zone-manual-publishable.html` in this
sandbox put the intended "Lower Cabinet and Cookware Zone" heading on page
20, not 22; page 22 held the unrelated tail end of a different zone's
cleaning-method table, with no zone name on it at all. Chromium's HTML to
PDF pagination depends on font metrics and is not portable across rendering
environments, so a hardcoded page index is not a fact about the document, it
is a fact about whichever machine last printed it. The shipped
`product-manual.jpg` (built elsewhere) was correct; the generator's own
`if not os.path.exists(...)` guard meant nobody would notice until someone
regenerated it with `--force` from a different sandbox, at which point the
site's own sample image for the $29 Micro Zone Manual would have silently
shown the wrong zone, and `gate_product_images_exist` (the only gate tied to
this generator) checks file existence only, not content, so nothing would
have caught it.

**Fixed at the root, not the page.** New `find_page(pdf, needle)` locates a
page by searching its own text for a heading, raising a named error if no
page carries it, rather than trusting a number. `manual_spread()` now calls
it for both crops it takes (the zone page and the table-of-contents page).
Proved directly in this same sandbox: regenerating `product-manual.jpg`
with the fix lands on page 20 here and shows the correct zone and all six
passes; `ops/tests/test_build_product_images.py` (new, 4 checks: a planted
multi-page lookup, a first-page lookup, a missing-needle `RuntimeError`, and
the real Manual's zone block and TOC) fail-then-pass proved by `git stash`
(the function is simply undefined without the fix, confirmed `AttributeError`,
clean with it restored). Regenerated `product-manual.jpg` and its 420/840
jpg/webp/avif variants (`ops/build_avif.py --encode` for the two invalidated
avif siblings); `gate_product_images_exist` reruns clean. `check_urls.py`
(213/213), `fix_dashes.py --check` (0/0), `affiliate.py --check` (165
documents) all clean after. No price or product touched; one existing
product-tile image corrected in place, not added. Ledgered in
`ops/cold-read-ledger.json` as fixed.

`preflight.py` launched in the background for this cycle; still progressing
through `gate_tests`'s full sequential suite well past the 280s mark every
recent cycle's own account cites as the usual stall point, with real,
changing child processes throughout rather than flat CPU, so this is a very
long sequential run rather than the documented deadlock. Reported in the
nightly log as whatever it had reached by the time this entry was written,
not assumed clean past that point.

**STEP 10b closed the same day, same cycle: the lesson above turned into a
gate.** This section's own text already named the gap precisely ("the only
gate tied to this generator checks file existence, not content, so nothing
would have caught it"), so a defect a check could have caught got a check.
New `gate_manual_spread_no_hardcoded_page` in `preflight.py`: reads
`manual_spread()`'s own source and fails if it no longer calls `find_page()`
for both page lookups, or if `find_page()` itself has been removed. It
cannot see whether the shipped JPG is currently correct (that needs a real
PDF render, already covered above), only whether a future hand edit
reintroduces a magic page number. Fail-then-pass proved directly against the
real file in a scratch copy: planted the old `page(m, 22)`/`page(m, 5)`
shape and, separately, a renamed-away `find_page()`, watched both fail by
name citing the real cause, restored byte for byte, reran clean. New
`ops/tests/test_gate_manual_spread_no_hardcoded_page.py` (4 cases: the real
fixed file, both regression shapes, a missing file correctly skipped not
failed). Full `preflight.py` rerun end to end with the new gate wired into
`main()`: every gate passed, 28 warnings (all previously diagnosed sandbox
limits), `gate_tests` completed this time rather than stalling or running
long.

## 25. Closed 2026-10-21, scheduled operator cycle: the preflight run lock itself deadlocked against a recycled pid, found live rather than in a planted test

Every lane reconfirmed exhausted before looking anywhere else: 10 open GitHub issues unchanged, all `decision`/`blocked-on-art`, none from Phil (checked issue #42's own comment thread directly, all three self-authored by prior agent cycles); `cold_read_ledger.py --stale` 0 of 277; `BACKLOG-2026-09-07.md` sections 2 to 4 re-derived from their own strikethrough markers, only C5 (Gemini billing) and C6 (YouTube OAuth, 102 videos) open, both already Phil-gated with everything up to the gate built; `ops/last-owner-notification.json` correctly withholds a repeat push on issue #42's topic (sent 2026-10-19, no reply, no state change since).

**Found while running `preflight.py` itself, not by auditing it.** A first attempt (`timeout 110 python ops/preflight.py`, the exact anti-pattern `acquire_preflight_lock()`'s own docstring warns against, bypassing `ops/run_preflight.sh`) was killed by the foreground timeout mid-run, orphaning its lock directory under `/tmp/.preflight_py_running.lock` with that process's real pid written inside. The very next `python ops/preflight.py` invocation was handed that exact pid back by the kernel (this sandbox runs very few processes, so low pids recycle fast) and deadlocked against its own lock: `acquire_preflight_lock()`'s staleness check reads `holder != own_pid and not _run_lock_pid_alive(holder)`, and with `holder == own_pid` (true by coincidence, not by any legitimate re-entrant call) that whole branch is skipped, falling through to a 1200-second mtime-based timeout against a lock the holding process could never have genuinely still held, since it had already been handed to someone else.

**Why `gate_preflight_lock_blocks_concurrent_runs` did not already catch this.** Its own "Half 1" test comment names the exact risk ("own_pid=0: a sentinel no real OS pid can ever equal, so it can never coincidentally collide... the first time this gate was run, masking the dead-pid fast path entirely") and works around it with a fake pid rather than proving the real default path (`own_pid=None`, what `main()` actually calls) survives the collision. The gate tested around the bug instead of testing it.

**Fixed at the root.** `_proc_start_time()` (new) reads `/proc/<pid>/stat`'s own starttime field, which the kernel sets once at exec and never repeats for two processes alive at the same instant, so it tells "still that process" apart from "pid recycled" even when the pid number itself is identical to the current process's own. The lock directory now carries a `start` file alongside `pid`; `acquire_preflight_lock()` checks it first, independent of any `holder != own_pid` comparison, and marks a mismatched or now-unreadable start time stale immediately rather than waiting out the mtime fallback. Reproduced the live incident directly before and after: stashed the fix, replayed the exact collision (lock holding a real pid equal to `own_pid` via the real default), watched it wait the full timeout and raise; restored the fix, same replay broke in under a millisecond. New "Half 4" in the existing gate proves the same shape going forward, called with `acquire_preflight_lock()`'s real default rather than the sentinel the first three halves use.

**Went well:** running the thing live surfaced a bug three separate planted-test halves had each carefully routed around rather than exercised; CLAUDE.md 0.3's "verify against production, not the repository" generalizes past the website.

**Did not go well:** lost real time to the deadlock itself before diagnosing it (the default 1800s `acquire_preflight_lock()` timeout at the real `main()` call site means an unlucky recurrence would have blocked a whole cycle for 20 minutes, not just this one investigation).

**Next:** push; the dashboard regen and nightly log entry this cycle still need writing; no other lane is genuinely unblocked, non-Phil-gated work right now.

---

## 24. Closed 2026-10-21, scheduled operator cycle: section 23's own fix did not survive a fresh sandbox, fourth occurrence, fixed by moving the gate itself ahead of `gate_tests` instead of depending on a hook

Every lane reconfirmed exhausted before looking anywhere else: 10 open GitHub issues unchanged since 2026-10-18, all `decision`/`blocked-on-art`, no reply from Phil; no mail credential in this sandbox (`ops/inbox_agent.py --apply` reports it plainly rather than assuming an empty inbox); `cold_read_ledger.py --next` 277/277 ledgered, 0 stale; `checks.yml`'s latest run against the last `site/`-touching commit was a clean `conclusion: success`.

**Checked the thing itself rather than trusting the prior cycle's identical-looking "exhausted, no new defect" conclusion (CLAUDE.md 5d).** Ran `ops/check_nightly_log_fast.py` directly. Two more 2026-10-21 entries had landed appended to the file's physical tail, behind 2026-10-04 history: the same shape section 23 closed the day before.

**Root cause this time, not just the symptom: section 23's fix cannot survive a fresh sandbox.** It wired the check into `.githooks/pre-push` and set `core.hooksPath` locally to make it run, but `core.hooksPath` is local git config, not a file in the repository, so every fresh checkout (which is what a scheduled cycle gets) starts with it unset and the hook never fires. Detection existed; enforcement did not travel with the repo.

**Fixed at the root.** Moved `run_gate(gate_nightly_log_not_oversized / _ordering / _no_duplicate_entries)` inside `ops/preflight.py`'s `main()` to run before `run_gate(gate_tests)`, the same spot and reasoning `gate_ci_conclusion_current` already uses (section 22). These three gates are pure file parsing with no browser and no network, so there was never a reason they needed to sit behind the sandbox's `gate_tests` hang. Now every `python ops/preflight.py` run reaches and enforces them regardless of hook config, token presence, or the hang. Fail-then-pass proved two ways: called the gate directly against a deliberately re-broken copy of the file and watched it fail by name, restored and confirmed clean; added a structural assertion to `test_gate_nightly_log_ordering.py` (now 8/8) that the gate's call site precedes `gate_tests` in `main()`'s source, confirmed it fails when reverted and passes when restored.

**Went well:** not stopping at "a gate exists" and checking instead whether the gate is reachable without optional local configuration, which is the actual gap the first three fixes left open.

**Did not go well:** this is the fourth occurrence of the identical shape (2026-09-05, 2026-10-15, 2026-10-20, now), and the third fix attempt; the first three each strengthened detection without asking whether enforcement depended on something outside the repository.

**Next:** push, confirm `checks.yml` stays green on this commit; no other lane is genuinely unblocked, non-Phil-gated work right now.

## 23. Closed 2026-10-20, scheduled operator cycle: checks.yml red on main again, same blind spot as section 22, a cycle appended instead of prepending

Every lane reconfirmed exhausted before looking anywhere else: 10 open GitHub issues unchanged since 2026-10-18, all `decision`/`blocked-on-art`/P0, no reply from Phil; no mail credential in this sandbox; `cold_read_ledger.py --stale` 0 of 276; all 20 room decks ship; every Hold row still correctly waiting on traffic. `check_urls.py` 213/213, `fix_dashes.py --check` 0/0, `affiliate.py --check` 165 documents clean.

**Checked CI directly instead of trusting a local preflight that never reaches `gate_tests`'s neighbours, per section 22's own lesson.** `checks.yml`'s latest run on main (`16766efe8`, "Regenerate dashboard after merging the concurrent 06:4x PM check-in") was `conclusion: failure`. The job log named the real cause: `ops/NIGHTLY-LOG.md` entry #841 ("scheduled operator cycle... notified Phil directly...") was appended to the tail of the file, after the entries had already moved on to 2026-10-04, instead of prepended to the top. Two further entries (05:1x PM, "sixth straight cycle") landed in the same spot behind it, all three misreading "the last four entries" as the physical end of the file, exactly the failure mode `gate_nightly_log_ordering`'s own docstring already named from 2026-09-05.

`gate_ci_conclusion_current` (section 22's own gate, meant to catch exactly this) did not fire: it needs `GH_TOKEN`/`GITHUB_TOKEN` or the `gh` CLI, neither present in this sandbox, so it correctly WARNed "could not be queried" instead of silently passing. Not fixed this cycle; querying GitHub by hand (the MCP tools this session has, not an env var) is what actually caught it.

**Fixed.** Moved all three misplaced entries to their correct newest-first position by committer timestamp (`git blame`, not guessed from prose): the "notified Phil directly" entry (04:49:47Z) between the 04:4x and 04:1x PM check-ins; "05:1x slot" (05:18:36Z) between 05:4x and 04:4x; "sixth straight cycle" (06:01:09Z) between 06:1x and 05:4x. `gate_nightly_log_ordering()` and the two sibling test files (`test_nightly_log.py`, `test_gate_nightly_log_ordering.py`) all pass clean against the corrected file.

**Turned the lesson into a gate that does not depend on a GitHub token, per CLAUDE.md step 10b.** The actual gap is narrower than "CI catches it": the local sandbox's own `gate_tests` hang means NO local check before a push ever reaches `gate_nightly_log_ordering`, token or no token, so the broken file reaches `git push` every time. New `ops/check_nightly_log_fast.py` runs the three pure-file-parsing nightly-log gates (`gate_nightly_log_not_oversized`, `gate_nightly_log_ordering`, `gate_nightly_log_no_duplicate_entries`) standalone in under a second, no browser, no network, no Stripe key. Wired into `.githooks/pre-push` (which already existed for conflict markers) so it runs at the one moment that actually prevents the defect: before the file leaves this machine. **Fail-then-pass proved directly**, both the script and the wired hook: appended a deliberately out-of-order entry, watched `check_nightly_log_fast.py` and `sh .githooks/pre-push` both exit 1 and name the exact entry, restored the file, watched both exit 0. `core.hooksPath` was unset in this sandbox (the same gap section 22's job log flagged for `hooks-enabled`); set it to `.githooks` so the hook actually runs here.

**Went well:** checking the live CI run before trusting a local "0 FAIL" the same way section 22 recommends, and finding that the recommended fix (a gate) is not enough by itself when the gate needs a credential this sandbox does not have; the fast, credential-free script closes the gap a token-dependent gate cannot.

**Did not go well:** this is the third occurrence of the identical shape (2026-09-05, then widened 2026-10-15 for a differently-worded heading, now 2026-10-20 for a plain re-append), each time only after it had already reached CI and sat red on main for some number of cycles.

**Next:** push, confirm `checks.yml` goes green on this commit, keep watching for the next genuinely unblocked, non-Phil-gated item; none exists right now beyond this fix.

## 22. Closed 2026-10-19, scheduled operator cycle: checks.yml had been red on main for three straight pushes and nobody checked

Attached clean (fetch, real unshallow, `checkout -B main origin/main`, ff-only merge onto `692af6165`). Read `GOALS.md`, this file's sections 0 to 7 and 20 to 21, `CLAUDE.md`, the last `ops/NIGHTLY-LOG.md` entries. Reconfirmed exhausted independently before looking anywhere else: GitHub's 10 open issues unchanged since 2026-10-18T19:54:35Z, all `decision`/`blocked-on-art`; `cold_read_ledger.py --next` 276/276, 0 stale; `inbox_agent.py --apply` no mail credential, unchecked not empty. `cycle_signal.py --check` returned SAME against the last recorded snapshot.

Every recent `ops/NIGHTLY-LOG.md` entry stopped its own verification at "`preflight.py`: 0 FAIL through every gate reached before the documented `gate_tests` sandbox hang" and never separately pulled the actual CI conclusion for the commit it had just pushed. Checked that directly instead of citing it: the last three completed `checks.yml` runs on main (`759c43f85`, `a7498109b`, `7c630782e`) were all `conclusion: failure`, not the green state every one of those entries implied. Same for `publish-image.yml`: its last two attempts (`ebb990769`, `a58dd54e`) also failed, so real content changes had sat unpublished since the last successful build, `3d84199d` on 2026-10-15.

**Root cause, verified by reading the actual job log, not by guessing from the gate name:** the 18:5x operator cycle's cellar/basement synonym fix (`0e50c3f27`) hand-edited `site/articles/how-to-organize-a-basement.html` (correctly, per CLAUDE.md 5b: it is hand-authored, no generator owns it) but never re-ran `ops/build_seo.py`, so `site/sitemap.xml`'s `<lastmod>` for that URL stayed at `2026-10-14` while the file itself changed on `2026-10-19`. `gate_sitemap_lastmod_current` caught it correctly, every single time, on CI; the matching test (`test_gate_sitemap_lastmod_current.py`) failed too, as designed. Both gates are ordered after `gate_tests` in `preflight.py`'s own call order, so a local sandbox (every sandbox this project has run in) never reaches either one, and the CI-only failure went unread for three cycles. `publish-image-current`'s own failure was the documented derived consequence of the same root cause, not a separate defect (see that gate's docstring from 2026-10-15, the first time this exact shape happened).

**Fixed.** Ran `python ops/build_seo.py` (the generator that owns `site/sitemap.xml`, confirmed by reading it rather than hand-editing the XML per CLAUDE.md 5b): `<lastmod>` for the basement article moved to `2026-10-19`, a 2-line diff plus its content-hash cache. Verified directly: `gate_sitemap_lastmod_current()` returns clean, `test_gate_sitemap_lastmod_current.py` passes (6 cases), `check_urls.py` 213/213, `audit_pages.py` 0/0, `affiliate.py --check` 165 documents clean, `fix_dashes.py --check` 0/0. `python -c "import ast; ast.parse(...)"` on `preflight.py`. Not re-verified: a genuine full local `preflight.py` run past `gate_tests`, same standing sandbox limitation every recent cycle documents; CI on this push is the real confirmation, same as every prior occurrence of this gap.

**Turned the lesson into a gate, per CLAUDE.md step 10b, rather than writing a fourth prose warning about it.** This exact defect class (a real CI failure hidden by the local `gate_tests` hang, nobody separately checking CI) has now cost two incidents four days apart (2026-10-15's "Fix the 9 CI gate failures the Photos API frontend shipped, unnoticed across 3 pushes", and this one). `gate_workflows_healthy` already watches `checks.yml` but only warns, and is itself ordered after `gate_tests`, so it inherits the exact blind spot it exists to report on. Added `gate_ci_conclusion_current` to `ops/preflight.py`, called near the very top of `main()`, before `gate_tests`: queries `checks.yml`'s own most recently completed run via the GitHub API (same `_workflow_run_via_api` helper `gate_workflows_healthy`/`gate_money_critical_workflows` already use) and hard-FAILs, by name, if it was a failure, the same escalation `gate_money_critical_workflows` already makes for a broken delivery pipeline rather than a warning that reads as routine noise. New `ops/tests/test_gate_ci_conclusion_current.py` (5 cases): fails on a failed run with a message naming the `gate_tests` hang, is clean on a passing run, warns rather than silently passing when it cannot query, and asserts the call site in `main()`'s own source actually sits before `gate_tests`. **Fail-then-pass proved against real live data, not only a mock:** called the new gate function directly against the real GitHub API before this fix was pushed and it correctly FAILED, citing the real failing commit (`7c630782ef6b`) and the real timestamp; it will read clean once this push's own `checks.yml` run completes green.

**Went well:** checking the thing itself (the actual CI job log) rather than trusting the chain of "0 FAIL through every gate reached" citations that had accumulated across several cycles, per CLAUDE.md 5d.

**Did not go well:** the 2026-10-15 incident named this exact gap in its own commit message ("nobody has been reading the Checks conclusion on recent pushes") and recommended relying on CI when `gate_tests` hangs, but that was advice recorded in prose, not a gate, so it recurred four days later exactly as CLAUDE.md step 10b warns a stored lesson will if nothing enforces it.

**Changing next cycle:** none beyond the new gate; every future cycle that hangs at `gate_tests` locally will now still see a hard FAIL near the top of the same run if the last push broke CI, instead of needing to remember to check GitHub separately.

**Next:** push this, watch `checks.yml` and `publish-image.yml` both go green on the next run (confirming the sitemap fix and closing the undeployed-content gap), then regenerate the dashboard. No other unblocked, non-Phil-gated workstream exists right now: every row in sections 2 to 6 is Done or Phil-gated (C5 Gemini billing, C6 YouTube OAuth), the cold-read ledger is exhausted, and all 10 GitHub issues are `decision`/`blocked-on-art`.

**Confirmed, same cycle.** The fix itself went stale once (`site/build-id.txt`, fixed in `6d2bc368d`, same root cause one level down: a generator not re-run after a `site/`-touching change). Watched `publish-image.yml` on that commit to completion rather than inferring from `in_progress`: `conclusion: success`, 2026-10-19T21:22:54Z, the first fully green run since `3d84199d` (2026-10-15). Section closed for real; `STATUS.md` INCIDENT-004 updated to match.

## 21. Closed 2026-10-19, scheduled operator cycle: the "cellar" synonym gap, the one real query the "167 gap rows" note left unexamined

Every lane was reconfirmed exhausted, independently, before picking this up: 10 open GitHub issues unchanged since 2026-10-18, all `decision`/`blocked-on-art`; no mail credential in this sandbox; `ops/cold_read_ledger.py --next` reports 276 of 276 files ledgered, 0 stale; `preflight.py` ran 76 gates clean (0 FAIL, 0 WARN) before the documented `gate_tests` headless-Chromium sandbox hang (confirmed genuinely stalled, flat CPU time across several minutes, then killed, same standing limitation every recent cycle reports).

Section 20's own "Next" line named two candidates: the "foyer"/"entryway" synonym mismatch, and the 167 remaining `gap` rows in `ops/keyword-demand.json`, calling them "mostly noise." Checked both rather than assumed. The foyer/entryway pair is already mostly covered or partial (the 2026-10-02 synonym fix holds); its remaining `gap` rows are "foyer design ideas for flat/india/pinterest" style queries, a decor-intent cluster this product does not address, not a real gap. A random sample of 15 of the 167 `gap` rows confirmed the "mostly noise" read (wood stoves, woodworking plans, desktop game organizers, gardening), with one real exception: "cellar organization ideas" (1 query, rank 11, Google), scored `gap` against `/about.html` at 0.0 coverage, with no page on the site containing the word "cellar" anywhere (confirmed by direct search).

**Fixed.** `/articles/how-to-organize-a-basement.html` is a hand-authored article (confirmed: no `ops/build_*.py` generator references it), so it was safe to edit directly per CLAUDE.md 5b. Added one genuine FAQ entry, in both the visible `<h3>`/`<p>` "Common questions" section and the matching `FAQPage` JSON-LD `mainEntity` (now 8 of each, confirmed by direct count): "Is a cellar the same thing as a basement?", answered honestly (the US/UK naming difference, not a claim they are identical), not stuffed in as a bare keyword. Re-scored with `python ops/keyword_demand.py --rescore` (free, no network): "cellar organization ideas" moved from `gap` to `covered` (`matched_on: heading`, `heading_page` now correctly the basement article), 167 gap rows site-wide down to 166, covered up one. No new preflight gate added: this was an individual content gap the existing `keyword_demand.py` tooling already surfaces correctly, not a systemic defect class with nothing watching it.

**Verified:** `check_urls.py` 213/213, `audit_pages.py` 0 duplicate titles/descriptions, `fix_dashes.py --check` 0 em/en dashes (repo-wide, including the new sentences), `link_graph_report.py` 0 orphans, `affiliate.py --check` 165 documents clean, `gate_keyword_demand_rescored_current` and `gate_keyword_demand_not_stale` both called directly: 0 FAIL. JSON-LD re-parsed and counted programmatically (8 entries, valid JSON) rather than eyeballed.

## 20. Closed 2026-10-19: `ops/keyword-demand.json`'s own LRN-0032 lesson had never been turned into a gate, and it recurred for real

Every row above was again Done or Phil-gated (10 open `decision`/`blocked-
on-art` issues unchanged, 0 unstruck rows, 0 open PRs), and `ops/
cold_read_ledger.py --stale` reported 0 stale and 0 un-ledgered candidates:
full cold-read coverage, so even the standing fallback had nothing left to
point at. This cycle went upstream of the backlog instead, to the
measurement layer section 3 of `CLAUDE.md`'s own ordering puts first.

**Found by hand, reading `ops/keyword-demand.json` directly rather than
trusting its own status field (CLAUDE.md 0.4/5d).** "attic organization
ideas" and "basement organization ideas", both rank-1 autocomplete
suggestions, scored `gap` against `/about.html` at 0.0 coverage, five days
after `/articles/how-to-organize-an-attic` and `/articles/how-to-organize-
a-basement` had shipped to answer exactly that (section 1b above, D-031).
The harvest's own `checked_at` (2026-10-14T14:47:50Z) was well inside
`gate_keyword_demand_not_stale`'s 10-day ceiling, so that gate had nothing
to say; the actual gap was that nobody had re-scored since, and `LEARNINGS.md`
LRN-0032 (2026-10-02) had already named this exact failure shape once,
"a stored status is a snapshot of a corpus other sessions are changing",
and had already built the free fix (`keyword_demand.py --rescore`, pure
functions over files already on disk, no network) without wiring it into
anything that runs on its own.

**Fixed in two parts, per 0.2/10b: the data, then the gate that stops it
recurring a third time.** `python ops/keyword_demand.py --rescore` moved 19
of 2,821 rows off `gap` against the corpus as it actually stands (commit
`c95de8903`), including both attic and basement queries, which now score
`covered`. `GOALS.md`'s own `gate_goals_keyword_cluster_citation_current`
caught the "cheap/budget/DIY" cluster citation going stale the same move
(two "diy"-suffixed attic/basement variants moved cluster membership too);
corrected in place to **30 covered / 64 partial / 4 gap of 98**, with a
dated correction paragraph, same convention as every prior correction to
that sentence. New `gate_keyword_demand_rescored_current` in `ops/
preflight.py` (pure logic in `keyword_demand_rescore_staleness_problem`,
`ops/tests/test_gate_keyword_demand_rescored_current.py`, 6 cases): warns
whenever 5 or more commits have touched `site/` since the stored
`scored_against_commit`, which is the thing that actually goes stale
between harvests and the thing `gate_keyword_demand_not_stale` never
watched. **Fail-then-pass proved directly against real git history**, not
a synthetic fixture: pointed it at a real commit 21 `site/`-touching
commits back and watched it fire by name citing the commit and the count,
confirmed clean once pointed at the post-rescore commit.

**Added 2026-10-19, PM/operator cycle (19:4x): hand-read every one of the 166 remaining `gap` rows, not a sample, so the next cycle does not re-open this same handoff.** Overwhelmingly off-topic noise unrelated to this site at all (cribbage tournaments, PC/Steam/Sims game-folder organizing, construction safety gear, vastu, diaper disposal, gardening, staircase-with-landing construction): a scraped-autocomplete artifact, not a content gap. A second cluster (`mudroom design layout ideas`, `home office organization tips...`, `how to decorate a large entryway`) already matches a room's own deck/article page at low coverage, the same "already answered, scored conservatively" shape prior cycles called mostly noise, not a real miss. One genuine candidate found: `organizing ideas for bedrooms` (rank 11) and `how to organize belts` both score 0.0 against `/about.html`, because no page addresses bedrooms generically across the three bedroom types (Primary/Kids/Guest), each of which has its own deck page. Not fixed this cycle: a generic "bedrooms" hub page risks the duplicate-page problem `CLAUDE.md` section 50 warns against, and `belts` reads as a single autocomplete artifact (`seeds: ['how to organize bench']`), not a real query cluster. Left open as the one real, small candidate if a future cycle has room; everything else in the 166 is closed as noise, not left as an unexamined count.

No price or product touched, no new page; one existing measurement file
re-derived and one GOALS.md citation corrected to match. The remaining 167
real `gap` rows were read by hand and are overwhelmingly off-topic
autocomplete noise (video games, cribbage tournaments, plant nurseries,
medical supplies), not a coherent, addressable demand cluster; "small
space" now reads 0 gap of 61 and the one meaningful synonym pattern
noticed in passing, "foyer" for "entryway", is left unactioned here as a
smaller, separate finding, not folded into this row.

## 19. Closed 2026-10-18: a second concurrent-preflight collision the same date, this time a structural lock instead of another prose warning

Independently re-verified the 17:5x/18:1x cycles' exhausted/Phil-gated
conclusion holds (10 open `decision`/`blocked-on-art` issues unchanged, 0
unstruck rows, 0 open PRs), then hit a real incident rather than filing
another reconfirmation: a background research subagent this cycle had been
launched for a read-only backlog digest but, inheriting full autonomous tool
access, ran `python ops/preflight.py` and `ops/dashboard.py` directly against
the same working tree while this session's own `ops/run_preflight.sh`-launched
run was still alive. Unlike the first such collision the same date
(`LEARNINGS.md` LRN-0041, a false `gate_tests` FAIL, disproved by a solo
rerun), this one killed the session's own run outright with no FAIL and no
summary line, and left a stack of duplicate `audit_catalog.py`/
`test_audit_catalog.py` processes fighting over the same lockdir.

**Fixed at the root, per 0.2/10b, not re-noted a second time.** New
`acquire_preflight_lock()`/`release_preflight_lock()` in `ops/preflight.py`,
wrapping the real `__main__` entry point: a dead holder's lock breaks
immediately (same proven shape `ops/tests/test_audit_catalog.py` already
uses for its own fixture lock), a genuinely live holder is waited out rather
than walked past, no matter whether the second invocation goes through
`ops/run_preflight.sh` or calls the file directly. New
`gate_preflight_lock_blocks_concurrent_runs` proves both halves,
**fail-then-pass confirmed**: disabled the dead-pid check and watched it go
red with the exact old-bug shape (times out waiting on a holder that is
actually dead), restored it and watched it pass clean. Also smoke-tested as
two real, separate OS processes, not just in-process: the second genuinely
blocked for the first's full runtime before acquiring the lock itself.

Also closed two smaller preflight warnings found along the way: `core.hooksPath`
was unset in this sandbox (pre-commit/pre-push present but never running;
the gate's own self-heal set it), and `ops/dashboard.py` had not been
re-ledgered after its own 17:5x fix landed (closed independently of, and
before discovering, the concurrent session that re-ledgered the same file
seconds apart: resolved as a normal merge, not a collision needing a new
rule). Full preflight re-run solo after the lock fix: every gate passed, 26
warnings, all explained by missing credentials/network access in this
sandbox. Full account in `ops/NIGHTLY-LOG.md` this date and `LEARNINGS.md`
LRN-0041's addendum.

---

## 18. Closed 2026-10-18: a dashboard near-miss caught by hand got the gate that would have caught it automatically

Every lane was reconfirmed exhausted again this cycle (issues, both backlogs,
cold-read ledger 276/276, preflight, inbox), so rather than file a 21st
"nothing new" entry, this cycle chased the 17:1x PM check-in's own stated
lesson to its root cause instead of only re-citing it. That cycle had, by
hand, caught `ops/dashboard.py` about to overwrite a committed
`deploy.reachable: true` (from a session with real production access) with
this sandbox's own `false`, on an already-current deck. `resolve_deploy_verdict()`
already protected the flat `deploy_verdict`/asset-count keys from this exact
shape (`gate_dashboard_deploy_carry_forward`); nothing protected the nested
`deploy["reachable"]` dict one key under it, so it still wrote straight from
this run's own failed probe every time. **Fixed:** new `resolve_deploy_reachable()`
in `ops/dashboard.py`, pure, carrying the previous real `reachable` forward
exactly when the verdict itself is carried, and new `gate_dashboard_deploy_reachable_carry_forward`
in `preflight.py`, proven to fail against the old behavior and pass against
the fix. Verified end to end against the real `ops/state.json`, not just
synthetic inputs: this sandbox's own regeneration now correctly carries
`reachable: true` forward instead of flipping it. A concurrent GitHub Actions
hourly check-in's own fresh real measurement (`d8b0fca4c`) landed the same
cycle; merged ff-only and its fresher dashboard artifacts kept over this
sandbox's own regeneration, same standing rule. Full account in
`ops/NIGHTLY-LOG.md` this date.

---

## 17. Closed 2026-10-18: `.githooks/mcp/mobile/quest-app/content/*` had never been a cold-read candidate, and the lane gap finally got its own gate; the search also found a real stale product

Attached clean on a fresh checkout (`fetch --unshallow`, `checkout -B main
origin/main`, `merge --ff-only`). Every GitHub issue (now 10: #42 added
2026-10-14, re the cadence cost of re-verifying an exhausted state) was
unchanged and owner-gated, 0 open PRs. `ops/cold_read_ledger.py --stale`
read 0 of 238, `--next` empty, matching the standing exhausted state. Ran
the same independent sweep items 14-16 each used (`git ls-files '*.py'
'*.js'` against every `LANES` directory) rather than trusting "238 of
238" to mean every file.

**Found a real gap, the fourth time running.** 39 hand-authored files
across 13 directories had never been a lane: `.githooks` (1), `mcp` (1,
the live MCP server), `mobile/quest-app` and its `assets/` (3, the React
Native app shell), and five `content/*/source` directories behind the
app-mvp prototype, the app spec, the print manual's own extraction
scripts, and three video-package pipelines (33). This is the third
consecutive cycle finding this exact shape (photos/, ops/cardtext/,
build/listings/, now this), which `CLAUDE.md` STEP 10b says means stop
re-discovering it by hand and gate it. Added
`gate_cold_read_lanes_complete` (ops/preflight.py): it runs the same `git
ls-files` sweep every cycle and warns if any `*.py`/`*.js` file sits
outside every `LANES` entry and every known-generated exclusion, proven
fail-then-pass against a planted stray file
(`ops/tests/test_gate_cold_read_lanes_complete.py`, 9/9, including a live
assertion that the real repository has zero gaps as of this commit).
Added the 13 lanes to `ops/cold_read_ledger.py`'s `LANES`, which also
exposed a real second bug: the ledger's bare-basename keys assumed no two
lanes ever share a filename, and `mcp/server.py` collided with the
already-ledgered `photos/server.py`. Fixed by collision-qualifying keys
(`lane_dir/base`) only for colliding basenames, migrating the two
pre-existing bare-keyed entries (`server.py`, and a second real collision
on `build_pwa.py` between `ops/` and `content/app-mvp/source/`) rather
than losing their history.

Read and ran all 39 (one, `zoneHeroes.js`, turned out generated by
`ops/build_mobile_corpus.py`, the same shape `GENERATED_JS` already
excludes for two other files, added there instead of ledgered). Most were
historical, already-executed Desktop-only generators (every path a dead
`C:\Users\philk\...` or ephemeral-session scratch/workflow-journal path)
with no live defect possible; the live ones (`mcp/server.py`, the React
Native `App.js`, the app-mvp service worker) were read in full and found
correct.

**The one that was not a dry hole.** Cold-reading
`content/manual/source/validate.py` (the Micro Zone Manual's own
validator, runnable here unlike its siblings since both content.json and
the Manual are committed) found an off-by-one in its Gate 2: the Safety-
fourth-S order check on a regex-matched run only applied when the run had
5+ names, but the regex's own minimum is 4, so an exactly-4-term
out-of-order run would skip the check. The identical bug was already
found and fixed in `ops/build_manual_print.py` on 2026-09-21
(`ops/tests/test_gate_manual_print_six_s_order.py`), unconnected until
now; also found copy-pasted into `content/video/source/validate_video.py`,
`content/video/media-package-entryway/source/validate_pkg.py` and
`content/app-spec/source/validate_spec.py`, fixed in all four (the latter
three cannot execute here, dead Desktop paths, so verified by `py_compile`
and parity with the proven fix rather than a live run).

Running `content/manual/source/build.py` for real against the committed
`content.json` (patched its dead paths to a scratch file) and diffing
against the committed Manual, as the validator-fix prompted, surfaced a
real, live defect rather than a latent one: **content.json's Sustain pass
had been rewritten for all 114 zones on 2026-09-07 and the sold Micro Zone
Manual never caught up**, plus 4 Standardize and 2 Safety/Shine zones with
smaller real drift, one of them (kitchen cooking zone) missing an entire
paragraph of real gas-leak safety instructions that exists in content.json
and nowhere in the shipped product. `gate_manual_zone_content_current`
(added 2026-09-26, LRN-0019) only ever compared `purpose` and
`done_looks_like`, so this was invisible to it. Hand-corrected all 120
drifted fields to match content.json exactly (verified byte-for-byte after
the fix, 0 remaining mismatches across all six passes), fixed one stray
British spelling in a `shine_detail.shine_summary` the same pass missed,
and re-ran `python ops/build_manual_print.py` so the publishable and print
copies MZ-MANUAL is actually fulfilled from carry the fix too. Extended
`gate_manual_zone_content_current` to check all six `passes` fields (with
a quote-mark fold so a canon-line quotation is never a false positive),
proven fail-then-pass against the real file and with 10 synthetic cases
(`ops/tests/test_gate_manual_zone_content_current.py`).

Verified after: `content/manual/source/validate.py` ALL GATES PASSED (20
rooms, 114 zones); `ops/fix_dialect.py --check` and `ops/fix_dashes.py
--check` both clean; `.githooks/check_control_bytes.py` clean on the
rewritten Manual; `ops/tests/test_gate_cold_read_lanes_complete.py` 9/9,
`test_cold_read_ledger_stale.py` 7/7, `test_gate_cold_read_handoff_not_stale.py`
26/26, `test_gate_manual_zone_content_current.py` 10/10; `check_urls.py`
213/213; `audit_pages.py` 0 duplicate titles/descriptions; `affiliate.py
--check` 165 documents clean; `preflight.py` fast run 0 FAIL through every
gate before the documented `gate_tests` sandbox hang. `ops/cold_read_ledger.py
--next` now empty, 276 of 276, 0 stale. No price touched; IndexNow not
applicable (no new page). Full account in `ops/NIGHTLY-LOG.md`.

---

## 16. Closed 2026-10-18: `build/listings/*.py`, the commerce channel scripts for Amazon KDP and Etsy, had never been a cold-read candidate at all

Attached clean on a fresh checkout (`fetch --unshallow`, `checkout -B main
origin/main`, `merge --ff-only`, no reset or force). Every row in sections
2 through 15 was again Done, Hold or Phil-gated; the same 10 GitHub issues
unchanged (8 decision, 2 blocked-on-art), 0 open PRs, no mail credential.
`ops/cold_read_ledger.py --stale` read 0, 229 of 229 ledgered, `--next`
empty, matching the standing exhausted state. Rather than log that a
further time, checked whether the ledger's lane list was itself still
complete, the same question that found `photos/` and `ops/cardtext`:
listed every `*.py`/`*.js` file in the repository outside the six known
lanes.

**Found a real gap.** `build/listings/*.py` (9 files: `amazon_nodes.py`,
`amazon_suggest.py`, `etsy_economics.py`, `check_etsy.py`, `check_kdp.py`,
`verify_epub.py`, `verify_zone_claims.py`, `build_kdp_cover.py`,
`build_etsy_assets.py`) is the commerce-channel package behind the
Amazon KDP and Etsy listings, last touched 2026-09-03 through 2026-09-27
and never ledgered under any lane (the non-recursive `ops/*.py` glob
cannot see `build/`, the same shape as the two prior gaps). This is not a
peripheral directory: `ROADMAP-2026-2029.md` names Amazon and Etsy as the
channels that reach buyers already shopping, ahead of search, so a latent
defect here is closer to the actual revenue path than most of what the
last several cold-read cycles checked.

Read and ran all 9, not sampled. `check_etsy.py`, `check_kdp.py`,
`verify_epub.py` and `verify_zone_claims.py` all PASS with 0 FAIL against
the real committed listing package, `etsy-listings.json`, `kdp/fields.json`
and the real PDFs/EPUB. `verify_zone_claims.py`'s zone counts were also
hand cross-checked against `MARKETPLACE-LISTINGS.md`'s own copy (L4: 13
zones across Entryway/Kitchen/Primary Bedroom/Primary Bathroom; L5: 16
across Guest Bedroom/Guest Bathroom/Dining Room/Entryway); both match.
`build_kdp_cover.py`, run against the real `build/cover.png`, produced a
file byte-identical to the committed `cover-kdp.jpg`: no drift.
`build_etsy_assets.py`, run end to end (regenerates its HTML sources,
renders three listings through headless Chromium, audits the result),
also reported 0 FAIL; the regenerated PDFs matched the committed files in
text, page count and card count exactly, and the only byte differences
were a Chromium-embedded render timestamp and, for one file, non
deterministic font/image re-encoding with identical content. Confirmed
this was re-render noise, not a fix, by diffing page text directly rather
than trusting the byte count; the regenerated files were not committed.

**No defect found.** The commerce package itself is correct and current;
the gap was purely in the cold-read ledger's own coverage. Added
`("build/listings", "*.py")` as a seventh lane in `ops/cold_read_ledger.py`
(checked for a basename collision against the other six lanes first:
none), documented why in the module docstring, and recorded all 9 files
as clean with the specific evidence above via `--add`. `--stale` now
reads 0 across 238 of 238 files, `--next` empty.

Verified after: `ops/tests/test_cold_read_ledger_stale.py` 7/7,
`ops/tests/test_gate_cold_read_handoff_not_stale.py` 26/26, `check_urls.py`
213/213, `audit_pages.py` 218 pages/0 duplicates, `fix_dashes.py --check`
0/0, `affiliate.py --check` 165 documents clean. No price, product or page
touched; IndexNow not applicable.

## 15. Closed 2026-10-17: `ops/cardtext/*.py` had never been a cold-read candidate at all, and the generalisation it needed was 19 rooms wide

Every row in sections 2 through 14 was again Done, Hold or Phil-gated; all
10 GitHub issues unchanged (8 decision, 2 blocked-on-art), 0 open PRs; no
mail credential; `cold_read_ledger.py --stale` read 0, 208 of 208 ledgered.
Rather than log the exhausted state a further time (the PM twin had already
done exactly that three minutes earlier this same hour and notified Phil
directly on the standing cadence-cost decision, `OWNER-ACTIONS.md` item 23),
checked whether the ledger's own lane list was still complete, the same
question that found the `photos/` gap on 2026-10-16.

**Found: `ops/cardtext/*.py` (21 files, all 20 room-deck generators plus
`derive_room_deck.py`) was never a candidate under any lane.** The "ops"
lane is a non-recursive `ops/*.py` glob, which cannot see its own
subdirectory, the identical blind spot `photos/` closed a day earlier for a
different subdirectory. Read and ran all 21: every `build_*_deck.py`
regenerates its committed `ops/cardtext/*-deck.json` byte-identical (0
drift) and passes its own extensive internal asserts (related-field
cross-refs, orphan/untreated root causes, per-zone counts, no art request
for lettering, safety coverage present). Checked a plausible-looking lead
(duplicate card IDs across rooms) and ruled it out: `KC-`/root-cause IDs are
deliberately shared, `ops/root_causes.py`'s "shared vocabulary", not a bug.

**The real finding was one level up, in the sibling page builders.**
`gate_kitchen_deck_page_counts_current` (2026-09-18) exists because
`build_kitchen_deck_page.py`'s hand-written prose naming the four
zoneless action cards was guarded only by an `assert whole_ids == [...]`
*inside the generator*: if the card set ever changed, that assert fires,
the generator crashes before writing, and `site/kitchen-deck.html` stays
byte-identical to HEAD, which `gate_generator_ownership`'s diff-only check
reads as clean rather than caught. All 19 other room decks were built
afterward from the same template and ship the identical unguarded pattern,
confirmed directly in `build_garage_deck_page.py`, `build_hall_closet_deck_page.py`
and others (`assert whole_ids == [...]`, same shape, never generalised
when the other 19 rooms shipped). Proved the gap is real, not theoretical,
with a forced simulation: flipped one Garage action card from zone-scoped
to zoneless without touching any committed file, and confirmed the old
(ungeneralised) check would have missed it.

**Fixed.** New `check_room_deck_page_counts()`/`gate_room_deck_pages_counts_current()`
in `ops/preflight.py`, generalising the Kitchen gate to the other 19 rooms:
independently re-derives each room's total card count, zone count, root-cause
count and zoneless-action-card set from its own committed `ops/cardtext/<slug>-deck.json`,
and checks the committed `site/<slug>-deck.html` still states them correctly,
regardless of whether that room's generator can even run today. Tolerant of
a genuine wording difference (Hall Closet and Pantry say "not one shelf's
job" rather than "not one zone's job"), found by testing the generalised
template against all 19 pages before writing the gate, not assumed.
`ROOM_DECK_WHOLE_IDS` records each room's current, verified-correct
zoneless-action-card list; a 21st room added later with no entry is flagged
by name rather than shipped unprotected (case 7 of the new test). Proved
fail-then-pass directly (a forced Garage mutation, not committed) and in new
`ops/tests/test_gate_room_deck_page_counts.py` (7/7 cases, including all 19
real rooms checked against their real committed files). All 21 files
ledgered in `ops/cold-read-ledger.json`; `ops/cold_read_ledger.py` widened to
a sixth lane (`ops/cardtext`, `*.py`), checked for a basename collision
against the other five lanes first (none).

**A separate, unplanned finding from this same cycle, recorded because it is
true and the next session needs it, and corrected below after the first
write of it got the cause wrong.** Having made all of the above edits, a
forked sub-agent doing this work found every edited file (this one,
`ops/preflight.py`, `ops/cold_read_ledger.py`, `ops/NIGHTLY-LOG.md`)
reverted to the prior committed state on disk mid-cycle, HEAD unchanged,
while a new, untracked test file survived untouched (`git checkout --`
cannot revert a file git does not yet track, which is why that one file
alone was spared). The fork's own first write-up blamed "a harness-level
shell initialisation step," having caught a `git stash && python
ops/preflight.py --help; git stash pop` sequence live in `ps aux` and
assumed it was environmental. It was not: that command was the parent
session's own manual sanity check, issued as an ordinary Bash tool call in
this same cycle, in the SAME working directory the fork was concurrently
editing, because the `Agent` fork had been launched without worktree
isolation. A fork inherits context but, absent `isolation: "worktree"`,
shares the parent's actual checkout; a parent-issued `git stash`/`git
stash pop` lands on whatever the fork has mid-written, with no locking
between the two. The real lesson is not "this environment stashes your
work for no reason," it is: never run a git-mutating command (stash, reset,
checkout, commit) from the parent session while a fork with file-write
access is active in the same unisolated working directory, and a fork
should commit its own edits promptly rather than leaving them sitting
uncommitted across multiple tool calls, precisely because the parent
session cannot be assumed to leave the tree alone. The fork redid the lost
edits from its own session history, verified every test again, and
committed immediately once it understood what had actually happened.

Verified after: `check_room_deck_page_counts`/`gate_room_deck_pages_counts_current`
0 FAIL on the real committed files, `gate_kitchen_deck_page_counts_current`
and `gate_every_generator_has_a_protection_plan` both still clean,
`test_gate_room_deck_page_counts.py` 7/7, `test_gate_kitchen_deck_page_counts.py`
5/5, `test_cold_read_ledger_stale.py` 7/7, `test_gate_cold_read_handoff_not_stale.py`
26/26, `check_urls.py` 213/213, `audit_pages.py` 218/0, `fix_dashes.py --check`
0/0, `affiliate.py --check` 165 documents. No price, product or page touched;
this closes a latent gap (today's 19 pages are all still correct), not a
live defect, the same shape as the Kitchen fix itself; IndexNow not
applicable.

---

## 14. Closed 2026-10-16: `photos/*.py` had never been cold-read, and the one read found a real lost-upload race

Every row in sections 2 through 13 was again Done, Hold or Phil-gated; all
10 GitHub issues unchanged (8 decision, 2 blocked-on-art); 0 open PRs;
`cycle_signal.py --check` read SAME against the 2026-10-15T22:55:52Z
snapshot; `cold_read_ledger.py --stale` read 0, 204 of 204 ledgered. Rather
than re-run the same full reconfirmation a further time today (the git and
nightly-log history already show roughly a dozen cycles reaching this exact
conclusion on 2026-10-16 alone), looked for ground nothing had swept yet.

`ops/cold_read_ledger.py`'s own lanes only ever covered `ops/*.py`,
`ops/*.js`, `site/assets/js/*.js` and `mobile/quest-app/lib/*.js`.
`photos/*.py` (4 files, built 2026-10-14/15) had two independent
adversarial security passes but had never been read by this mechanism, and
a security review and a cold read are shaped to catch different things: the
reviews hunted for attacker-triggered gaps, not an ordinary-use correctness
bug.

**Found, reading `photos/store.py` directly: a real lost-upload race.**
`add_photo`/`delete_photo`/`save_analysis` each did read-modify-write on one
session's `meta.json` with no lock. `ThreadingHTTPServer` gives every
request its own thread, so two overlapping requests on the same session (a
before and an after photo sent back to back is the ordinary case, not a
contrived one) could both read `meta.json` before either wrote it back; the
second write then silently erased the first writer's new photo entry. The
`.jpg` file itself still lands on disk, orphaned and unreferenced, while the
caller who uploaded it was already sent `201`. Proved directly against the
pre-fix code with a forced, deterministic interleave, not timing luck: both
uploads returned `201`, only one id survived in the session's photo list
afterward.

**Fixed.** One re-entrant lock per session (`Store._lock_for`, created only
once a session directory is confirmed to exist, so a flood of guessed or
invalid session ids cannot grow the lock table unboundedly), and a new
`_authorize()` helper that reads and checks the token without writing, so
`open()`, `add_photo`, `delete_photo`, `save_analysis` and `delete_session`
each now run their full read-through-write as one locked critical section
instead of two separate, unguarded ones. Re-proved fail-then-pass in
`ops/tests/test_photos_service.py` (33 to 37 checks): the new cases force a
second request to actually block mid-`open()` while the first still holds
the lock, then confirm both uploads survive.

**Gate for next time, not just a fix for this time.** Added `photos/*.py` as
a fifth lane in `ops/cold_read_ledger.py` and ledgered all four files
(`store.py` fixed, the other three clean), so this gap cannot silently
reopen by the lane list quietly staying three directories behind the
repository's own content. `PHOTOS-API.md` and `OWNER-ACTIONS.md` item 22
both updated to the new 37-check count.

Verified after: full relevant suite re-run clean (`test_photos_service.py`
37/37, `test_build_photo_check_data.py` 5/5, `test_cold_read_ledger_stale.py`
7/7, `test_gate_cold_read_handoff_not_stale.py` 26/26), `check_urls.py`
213/213, `audit_pages.py` clean, `fix_dashes.py --check` 0/0,
`affiliate.py --check` 165 documents, `link_graph_report.py` 0 orphans.
No price, product or shipped page touched; `photos/` is still undeployed, so
this fix reaches zero live customers today and closes a gap before Phil's
own deploy decision (`OWNER-ACTIONS.md` item 22) can expose it.

## 13. Done 2026-10-15, scheduled operator: the Photos API's own "not yet
built" frontend, built and kept off until the backend is

Not a pre-existing backlog row either. Every row in sections 2 through 12
was again Done, Hold, Phil-gated or closed; all 10 GitHub issues unchanged
(decision/blocked-on-art); no mail credential; the standing cold-read
fallback's first mode had just run out of candidates for the first time
(201 of 201 ledgered) and its handed-off second mode (re-reading ten files
unchanged since 2026-10-11, confirmed by `git log --since` before starting)
had no realistic chance of finding anything new. Picked the next epic down
(5, product) rather than repeat a check with no expected value: `PHOTOS-API.md`
named its own frontend as "not yet built," the backend is already built,
tested (33/33) and independently security-reviewed, and `CLAUDE.md` 0.5 asks
for exactly this, building up to an owner gate so the owner's action is a
single step.

**Done.** `site/photo-check.html` + `site/assets/js/photo-check.js`: upload a
before/after photo, get the zone's published method back. Verified against
the contract directly, not against `PHOTOS-API.md`'s own prose: ran a local
`photos/server.py` and exercised session-create, photo PUT, analyze, delete
and the bad-token 404 shape with curl first, which caught one real
documentation gap before it became a client bug (the PUT response's photo
id field is `id`, never `photo_id`; only the analyze request body uses
`photo_id`). Every model-controlled field (`summary`, step `action`/`because`,
safety lines) renders through `textContent`, never `innerHTML`, which is the
one open risk `PHOTOS-API.md`'s security review named as unverifiable because
no frontend existed yet to check. Zone data (`site/assets/js/photo-check-zones.js`)
comes from new `ops/build_photo_check_data.py`, which imports
`photos/methodology.py` directly rather than re-deriving the slug rule, so the
picker can never offer a slug `GET /v1/zones` would reject; registered in
`preflight.py`'s `GENERATOR_OWNERSHIP_CHAIN` (immediately after `build_epub.py`,
before `fingerprint_assets.py`, the same slot every other asset generator
holds) so drift is caught the same way as every other generator here, not a
bespoke check. New `ops/tests/test_build_photo_check_data.py` (5 cases,
fail-then-pass proved directly: corrupted the committed output, watched the
idempotency check fail by name, restored, reran clean).

**Deliberately not linked anywhere, and excluded from the sitemap and feed**
(`<meta name="robots" content="noindex, nofollow">`, which `ops/build_seo.py`'s
own `scan_extra_pages()` already treats as the signal to skip a page, the same
mechanism the Google-verification file relies on; confirmed directly,
0 matches for "photo-check" in both files after a full `build_seo.py` rerun).
The page also detects whether the API answers `GET /v1/health` before
showing the upload form, so even a direct hit on the URL, which nothing
currently links to, reads as "this feature is not live yet" with a link to
the zone pages instead of a broken form. This was the deciding reason to
build the frontend now rather than wait for the deploy decision: shipping it
live-but-undiscoverable, with a graceful unavailable state, carries none of
the "never list something that cannot be delivered" risk `CLAUDE.md` section
8 names, while still collapsing two separate future sessions' worth of work
(deploy, then build the frontend against whatever the deploy actually
shipped) into one.

Verified after: `audit_pages.py` 218/0 (one real finding caught and fixed in
the same cycle, a missing canonical link on the new page, required even
though it is noindexed), `check_urls.py` 213/213, `fix_dashes.py --check`
0/0, `affiliate.py --check` clean (165 documents, unchanged, this page
carries no affiliate link), `node --check` clean on both new JS files,
`ops/tests/test_photos_service.py` 33/33 (backend unchanged, re-run to
confirm this cycle did not touch it), `ops/tests/test_build_photo_check_data.py`
5/5. `PHOTOS-API.md` and `OWNER-ACTIONS.md` item 22 both updated the same
cycle so neither goes stale behind this. No price, product or existing page
touched; IndexNow not applicable (the one new page is deliberately
unindexed).

**Accept when:** Phil deploys `photos/` (`OWNER-ACTIONS.md` item 22). At
that point turning the frontend on is removing one `<meta>` line and adding
one link, not a build.

## 12. Closed 2026-10-15: `ops/video_cleanalong.py` could silently render the
wrong aspect ratio depending on import order

Not a backlog row; found by this cycle's own standing cold-read fallback
(`cold_read_ledger.py --next`'s oldest un-ledgered candidate) after
independently reconfirming sections 2 through 11 exhausted and all 10
GitHub issues unchanged.

`video_cleanalong.py` (new 2026-10-14, built for Phil's "those videos kind
of suck" note) forces the shared `video_zone` module into YouTube wide mode
by appending `--wide` to `sys.argv` before importing it. `video_zone`
reads `sys.argv` for `WIDE`/`W`/`H` exactly once, at its own import time,
and caches the result on the module. Proved directly in a throwaway
process: import `video_zone` narrow first (as any other caller would),
then import `video_cleanalong`, and the already-cached module never
re-reads the now-mutated `sys.argv`; `vz.WIDE` stays False and `W,H` stay
1080x1920. Every slide `video_cleanalong.py` renders through `vz.page()`
and `vz.shot()` would then be silently portrait, which the pipeline's own
final `ffmpeg scale=1920:1080` stretches into a distorted 16:9 file, with
no error or warning anywhere in the chain.

**Not a live defect today.** `preflight.py`'s `gate_tests` runs every
`test_*.py` as its own subprocess, one process per file, so no import
order carries between test files there; and nothing else in the repository
imports `video_cleanalong` (grepped), so there is no script that combines
it with `video_zone` in one process yet. It is a latent hazard for
whatever batch script does that next, the same shape as the KC-008
"bedtime" defect and the Entryway caption-length defect this register's
own history already lists: correct everywhere it has been tried, wrong
the moment someone combines it with something else, silently.

**Fixed.** Replaced the `sys.argv` mutation with setting `vz.WIDE`,
`vz.W`, `vz.H` directly on the imported module after import, which forces
wide mode regardless of who imported `video_zone` first and leaves
`sys.argv` untouched for every other module sharing the process.
Fail-then-pass proved directly against both mechanisms in the adversarial
order: old mechanism left `WIDE` False; new mechanism forces it True,
`sys.argv` unchanged. `ops/tests/test_video_cleanalong.py` extended (6 to
8 checks) to assert both, re-run clean. Ledgered as fixed in
`ops/cold-read-ledger.json`.

## 11. Closed 2026-10-15: `ops/cycle_signal.py` was defeating its own purpose

Not a backlog row; found by this cycle's own operator pass after
independently reconfirming sections 2 through 10 exhausted (every row Done,
Phil-gated, or closed by decision; all 10 GitHub issues unchanged, decision
or blocked-on-art; `preflight.py` ~75 gates clean through the documented
`gate_tests` sandbox hang), rather than stop at "nothing to pick."

`ops/cycle_signal.py`'s `SIGNAL_FILES` included `ops/cold-read-ledger.json`.
The standing fallback for a cycle with nothing else unblocked is to
re-verify a couple of already-clean cold-read entries for drift, and that
fallback appends to the ledger even when it finds no defect. So every time
the fallback ran, it invalidated the "nothing changed since last cycle"
SAME verdict the tool exists to provide, forcing the next cycle straight
back into a full local re-verification, which (finding nothing else to do)
ran the same fallback again. 44 commits touched the ledger in the 4 days
since the tool shipped, 2026-10-11 through 2026-10-15, each one a cycle
paying for a full re-verification the tool was supposed to let it skip.
Same shape as section 10's finding, and the same shape issue #42 (open,
Phil-gated) names for the cadence generally: a real cost nobody had traced
to this one file.

**Fixed.** Removed `ops/cold-read-ledger.json` from `SIGNAL_FILES`, same
rationale already documented in the file's own docstring for excluding the
command deck and `ops/NIGHTLY-LOG.md` (both rewritten most cycles regardless
of whether anything else moved). A real new cold-read finding still surfaces
through `BACKLOG`/`STATUS`/`OWNER-ACTIONS` (all still signals) or a
preflight gate failing, so nothing here goes unchecked. Fail-then-pass
proved directly on a synthetic repro (old signal set read CHANGED after a
no-op ledger append; new set reads SAME); `ops/tests/test_cycle_signal.py`
(isolated synthetic files, unaffected by the `SIGNAL_FILES` edit) still
passes 6/6. Recorded a fresh real snapshot; `--check` now reads SAME against
the live repo.

## 10. Closed 2026-10-14: ops/NIGHTLY-LOG.md's own unbounded growth

Not a backlog row (nothing above named it); found by a cold-read agent this
cycle asked to find the top unblocked item, after it confirmed sections 2
through 9 are genuinely exhausted (every row Done, Phil-gated, or closed by
decision, matching `ops/cycle_signal.py --check`'s independent SAME verdict
and `ops/cold_read_ledger.py`'s 199-of-199 saturation) and looked for
something nobody had named yet rather than stop at "nothing to pick."

`ops/NIGHTLY-LOG.md` had grown to 8.1MB / 57,105 lines / 2,795 entries back
to 2026-08-23, never rotated since the file existed, because nothing ever
checked whether it needed to be. Three gates already in `ops/preflight.py`
(`gate_nightly_log_ordering`, `gate_nightly_log_no_duplicate_entries`,
`gate_cold_read_handoff_not_stale`) each read the whole file on every single
preflight run to look at a handful of recent entries, and STEP 1 of the
operating prompt itself asks every cycle to read "the last four entries,"
which on this file meant opening and searching 8MB each time. That is a real
and compounding cost: this is the same shape issue #42 (open, Phil-gated)
names for the autonomous cadence generally, just never traced to this one
file, and section 7's own "source corrected, artifact never re-derived from
it" complaint applies here too, pointed at the log that records every other
instance of it.

**Fixed, not merely diagnosed.** New `ops/rotate_nightly_log.py` moves
entries older than a 14-day retention window into `ops/NIGHTLY-LOG-
ARCHIVE.md`, verbatim and in their existing order; nothing is deleted
(`CLAUDE.md` section 54, Failure Is Information). Entry dates are resolved
by searching each heading line for a `YYYY-MM-DD` anywhere in it (about a
quarter of real entries have no leading date, reusing a neighbour's date
instead, e.g. `"## PM check-in (10:1x slot): ..."`) and inheriting forward
from the nearest earlier dated entry when a heading names none at all.
Applied once this cycle: the live log is now 780 entries / 2.24MB (was
2,795 / 8.06MB), archive holds the rest. New `gate_nightly_log_not_oversized`
in `preflight.py` (a WARNING, matching its two neighbours) fires once the
log drifts more than retention-plus-7-days past the window again, so this
does not quietly regrow back to the same cost; `ops/tests/
test_rotate_nightly_log.py` and `ops/tests/test_gate_nightly_log_not_
oversized.py` both fail-then-pass proved. Re-verified clean directly against
the real rotated file and against the real (pre-rotation) file before that,
not assumed.

## 9. Closed 2026-10-13: dashboard staleness fixed at the source, not re-gated

By 2026-10-13 every row in sections 2 to 6 was Done, Phil-gated, or closed by
decision, independently reconfirmed by several same-day cycles in
`ops/NIGHTLY-LOG.md`. The one thing every one of those cycles kept finding
and fixing by hand was `gate_dashboard_self_description_fresh` firing again:
`EXECUTIVE-DASHBOARD-LIVE.md`'s own cited "Last commit" one or more commits
behind real HEAD, each time fixed by rerunning `ops/dashboard.py` and
pushing, each time stale again within the hour. That gate already existed,
already fired correctly, and already explains in its own docstring why it
WARNs rather than FAILs; the recurrence was never a detection gap, it was
that nothing made regeneration the unconditional last step before a commit
lands, so the warning kept coming back true.

Traced the actual commit stream (`git log --oneline -20`) rather than
assuming: direct Claude-session pushes interleave with `github-actions`
commits from `.github/workflows/hourly-brief.yml` ("Hourly check-in
record"), which fires on every push to `main` as well as hourly and commits
unconditionally, with nothing in that job ever touching the deck. That one
workflow, not any single session, is the dominant source of the gap.

Fixed at both of the two places that actually land commits most often,
rather than adding a third gate on top of one that already works:

- `ops/ship.py` now runs `python ops/dashboard.py` unconditionally before
  staging anything, on every real (non `--check`) invocation, so the one
  tool every push is told to go through (`CLAUDE.md` STEP 12) cannot forget
  the step STEP 11b already asks for every cycle.
- `.github/workflows/hourly-brief.yml`'s "Commit the check-in record" step
  now regenerates the deck first and commits its three output files
  alongside the check-in record, since this job commits to `main` far more
  often than any single Claude session does.

Verified before claiming: `python ops/dashboard.py` runs clean standalone
(stdlib only, degrades Stripe/GitHub fields to "carried forward"/"unknown"
without credentials, same as every sandboxed cycle already shows); `python
ops/ship.py --check` stays read-only (2 uncommitted files reported, dashboard
not touched); all three existing `ops/tests/test_ship_*.py` files still pass
against the changed file. `.github/workflows/hourly-brief.yml` parses as
valid YAML.

That workflow's own comment claimed, present tense, that its commit step had
never once reached origin (a 403 found 2026-09-03). Checked rather than
cited: `git log --author=github-actions --grep="Hourly check-in record"`
shows 520 such commits in history, most recent minutes old; the
`permissions: contents: write` block already fixed the real bug and the
comment was simply never updated after. Corrected the comment in the same
pass. This means the commit mechanism itself is proven live; only the new
regeneration step inside it is unverified until its first real run.

Left for a later cycle if the warning still recurs after this: the three
other workflows that also commit to `main` on a `push` trigger
(`bluesky-drafts.yml`, `social-drafts.yml`; `linkedin-drafts.yml` has no
push trigger) were deliberately left untouched this cycle, since each wraps
its commit in a more fragile rebase-retry loop already built to handle a
cross-workflow race, and each commits far less often (gated behind its own
daily send-or-not decision) than `hourly-brief.yml`. If staleness still
recurs after this fix lands, those three are the next place to look, in
that order.

**Addendum, 2026-10-14, scheduled operator cycle: a sibling carry-forward gap
found and fixed, all-time revenue regressing to "not measured" on every
credential-less run.** `revenue_all_time`/`sales_all_time` in
`ops/dashboard.py` (the one $19 sale, 2026-08-21) had no carry-forward at
all, unlike `traffic_line`, `affiliate_trigger` and `revenue_month`, each
already fixed for this exact shape. Every run without a Stripe credential
(the common case here) regressed the committed "$19 all time from 1 sale"
to null, printing "all time not measured", the identical "business looks
deader than it is" regression `_stripe_all_time()`'s own docstring says it
exists to prevent, reopened one layer over. A prior cycle had checked this
exact symptom and judged it not a regression because the rendered text is
honestly labelled, missing that the underlying fact was still being lost,
not merely unmeasured that run. New `carry_forward_all_time()` in
`ops/dashboard.py`, same pattern as its siblings; new
`ops/tests/test_all_time_carry_forward.py` (10/10) and
`gate_dashboard_all_time_carry_forward` in `preflight.py`, fail-then-pass
proved directly. `preflight.py --fast` reached past the documented
`gate_tests` sandbox hang this cycle (378 gates logged, 0 real FAIL) before
the 600 second background budget ended it near the very last gates.

## 8. Closed 2026-10-11: the full-reverification efficiency gap

Every row above in sections 2 to 6 was already Done, Phil-gated, or closed by
decision as of this date, independently re-confirmed this cycle (direct
GitHub read, full re-read of this file, clean `preflight.py`). Dozens of
scheduled cycles on 2026-10-11 each re-derived that identical conclusion from
scratch, a cost `ops/NIGHTLY-LOG.md`'s own 23:0x entry named plainly: "the
honest fix, if one exists, is a cheaper way to confirm nothing changed since
the last cycle before paying for a full re-verification, not skipping
verification."

Built `ops/cycle_signal.py` (`ops/tests/test_cycle_signal.py`, 6 cases). It
hashes a narrow set of signal files (both backlogs, `OWNER-ACTIONS.md`,
`STATUS.md`, `GOALS.md`, `ops/deploy-verdict.json`,
`ops/cold-read-ledger.json`) and compares against a committed snapshot,
`ops/cycle-signal.json`. `--check` returns SAME only when every one of those
files is byte-identical to the last recorded clean pass; CHANGED names the
files that moved; MISSING means no snapshot exists yet. It never replaces a
check, only the redundant repetition of one: GitHub, the mail inbox and the
scheduled workflows still need a direct read every cycle regardless of the
verdict, since nothing local can see those. A future cycle should run
`python ops/cycle_signal.py --check` right after attaching; on SAME, skip the
expensive local re-verification (full backlog re-read, `preflight.py`'s
multi-minute `gate_tests` pass) and spend the cycle on the external checks
and the Phil-gated queue instead, then `--record` a fresh snapshot once a
full pass does run clean again.

**Addendum, 2026-10-13, scheduled operator cycle: `keyword-demand.yml`'s weekly
cron found stuck, cancelled and replaced with a fresh dispatch, A27 reconfirmed
rather than reopened.** The 2026-10-07 scheduled run sat `queued` on GitHub for
six days; a `workflow_dispatch` cancel attempt 409'd ("not queued yet",
GitHub's own contradiction), but a fresh dispatch ran `in_progress` immediately
regardless, confirming the stuck entry held no real concurrency lock on
`keyword-demand`, just a stale row in the run list. The new harvest
(2026-10-13T05:22:30Z, 151 seeds, 302 attempts, 0 failed, both canaries OK)
diffed against the pre-harvest snapshot by query, not by count: 0 new gap
queries, 1 gap query (`hall cupboard design ideas`) dropped out of autocomplete
entirely (the same benign churn `GOALS.md` has recorded three times already,
not a regression), and the one previously-investigated room-mismatch
(`why are garages left unfinished` scoring against a Primary Bedroom nightstand
page) persists unchanged, same as when A27 closed it with no safe fix. A27
stays closed; no new row opened. `gate_keyword_demand_not_stale` and
`gate_goals_keyword_cluster_citation_current` both checked clean directly
against the fresh file.
