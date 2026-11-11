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

**None currently open.** The Primary Bedroom room-guide tier claim (opened 2026-11-07, ~23:0x slot, handed off unclaimed by three prior cycles as too large for a 30-minute slot) was released the same cycle once the tier was read in full and three genuine gaps closed (color-sorting a closet, under-the-bed storage, an ADHD-friendly framing FAQ). Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 159. Pruned per this section's own rule ("if a line here is older than a day and its work is in main, remove it"): the Garage/Stair Landing/Guest Bathroom/`ops/ship.py` claims this line used to list are all confirmed landed on `main`, reconfirmed with zero drift by several intervening cycles; full account of each stays in `ops/NIGHTLY-LOG.md`.

# 1. Status Metadata

**Latest, 2026-11-11 (~11:0x UTC), scheduled operator cycle: fixed the `/articles/index.html` directory-page misroute, a real measurement bug crediting hundreds of queries to a listing page instead of the page that actually answers them.** `/articles/index.html` mechanically repeats all 56 of its linked articles' own titles as its own `<h2>`s, so it tied or beat the real destination page on word-overlap alone. Fixed in `ops/keyword_demand.py`: a heading that is entirely one hyperlink to another page is no longer counted as a page's own content, checked site-wide first (only 3 of 244 pages are built this way, all directory pages, so no legitimate page's heading is touched). Full before/after diff of both corpora: 0 rows moved to a better status, 90 moved to a worse, honest one, all 90 previously misattributed to a directory page, 0 side effects elsewhere. Fail-then-pass proved (new test case 41). `GOALS.md`'s cluster citation corrected in place. Also added "inspo"/"inspiration" to `FORMAT_WORDS` (Home Office/Guest Bathroom mining). `preflight.py --skip-tests` 0 FAIL twice, same documented `gate_etsy_pdfs_current` network stall. GitHub: 31 open issues, unchanged since 2026-11-08, none from Phil. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` section 1.

**2026-11-04 (~02:5x UTC), scheduled operator cycle: the room-guide content-gap-mining lane is now genuinely exhausted across all 20 rooms (0 unfixed `gap` row remains in `room_guide_underperformance.py`'s ranking); this entry closes the gap `gate_status_currency` found, 14 material commits to THIS SECTION's own text since it was last touched (not a deploy gap; see `BLOCKER-001` for current deploy status), listed here rather than one by one. Since the 2026-11-01 entries below: a UTC-rollover sitemap `lastmod` bug caused a real `checks.yml`/`publish-image.yml` failure and was fixed twice (once at the commit that caused it, once at its sibling function `build_sitemap()` which had the same class of bug `_git_content_date()` was already fixed for on 2026-10-23), now gated by a new static test. Several rounds of keyword-noise exclusions landed in `ops/room_guide_candidates.py` (dental/gardening-series/reddit-life seed drift, business/pricing-model B2B noise, Workshop's craft-paint/diamond-painting cluster, Garage's car-interior-organizer cluster), each proved fail-then-pass per CLAUDE.md 10b, closing Workshop, Kitchen (the "corner cabinet" US-spelling gap), Garage and Hall Closet's remaining coverage gaps. One real CI FAIL this session itself shipped (an `also-called` digital-collision regression) was caught by `publish-image.yml`, fixed, and turned into a fast pre-push gate rather than left to recur. `preflight.py --skip-tests` reran clean this cycle: every gate passed, 38 warnings worth a read (mostly standing sandbox credential gaps: no Stripe/SSH/mail credential here, consistent with every recent cycle), 0 FAIL. GitHub: 30 open `decision`/`blocked-on-art` issues, unchanged since 2026-11-02, none from Phil (checked issue #42's thread directly). No new work unblocked; the ordering rule forbids picking any Phil-gated item.**

**Corrected 2026-11-04 (~15:0x UTC): the line above was already stale by one issue when read this cycle.** Re-pulled the open-issue list directly from the GitHub API rather than trusting the prior count: **29 open issues**, not 30 (`#2,#15,#18,#21,#29,#31,#33,#42,#43` through `#63`), one fewer than the 2026-11-02 reading. Still none from Phil, and still every remaining lane owner-gated; the count moved by one closure somewhere in the interval, not by any new non-Phil-gated work appearing.

**2026-11-05 (~04:5x UTC), scheduled operator cycle: fixed a real measurement-attribution bug in `ops/keyword_demand.py` that many prior cycles' one-at-a-time "misattribution" fixes (pegboard, chargers, hutch, bedside table, hallway closet) were symptoms of, not the root cause.** `score_rows()` always set `best_page`/`best_page_title` from the title-surface winner, even on rows where `matched_on` already said the heading surface scored higher and a different page earned the status. Checked directly against the live corpus before touching anything: 1402 of 2823 rows disagreed between the two surfaces, 778 of those pointing at a different ROOM entirely (e.g. "master bedroom storage" credited a Kids Bedroom zone while its actual 0.667 heading-coverage came from Primary Bedroom's own room page). Every downstream consumer (`room_guide_candidates.py`, `room_guide_underperformance.py`, `keyword_demand_global.py`, which reuses `keyword_demand.py`'s functions so one fix covers both corpora) reads `best_page` as "the page this query actually routes to", so this was silently sending prior cycles hunting for also-called synonyms on the wrong zone and miscounting which room most needs work. Fixed by deciding one winning surface before using it anywhere downstream, breaking an exact tie between surfaces the same way `_tie_break` already breaks a tie within one surface (prefer the page matching the query's own room signal). Two new numbered cases added to `ops/tests/test_keyword_demand.py` (case 20, both shapes: a clean heading win and a cross-room tie), fail-then-pass proved directly (`git stash` the fix, watch both new assertions fail with the exact wrong URLs, restore, watch them pass). `python ops/keyword_demand.py --rescore` and `python ops/keyword_demand_global.py --rescore` re-derived every status: gap/partial/covered totals unchanged (112/1262/1449 and 97/931/1142), as expected since the fix only corrects attribution, not scores. Spot-verified in the regenerated `ops/KEYWORD-DEMAND.md`: "back porch careers" now correctly points at the Patio or Deck deck instead of an unrelated article about family habits. `check_also_called_digital_collision_fast.py`, `test_gate_zone_also_called_is_heading.py` (6/6), `test_gate_also_called_no_digital_collision.py` (5/5), `test_room_also_called.py`, and the four `keyword-demand*-rescored/not-stale` gate tests all still pass. Full `preflight.py --skip-tests` run clean afterward: every gate passed, 39 warnings (standing sandbox gaps only), 0 FAIL. GitHub: still 29 open issues, none from Phil. No content, price or product page touched; this is a measurement-tool fix, not a site change, so IndexNow is not applicable. Full account in `ops/NIGHTLY-LOG.md`.

**2026-11-05 (~07:5x UTC), scheduled operator cycle: closed the deck-page also-called structural gap for Patio or Deck (BACKLOG-2026-09-07.md 118), and found `checks.yml` red on main independently of this cycle's own work.** A fork re-verified the "room-guide mining is exhausted" claim rather than trusting it and found Patio or Deck's own number (52% uncovered) had never been re-read against entry 115's attribution fix. `ops/build_patio_or_deck_deck_page.py` now renders the room's already-vetted "also called the terrace, the backyard or the porch" heading, which no deck-page generator across any of the 20 rooms had ever carried; moved 3 queries off partial (16 to 13), the rest of the room's partial rows checked against real content and confirmed genuinely unfixable. Full account and verification in `ops/NIGHTLY-LOG.md` and the backlog entry. **Separately, `checks.yml`'s last completed run (c5faa3a8f, the 07:1x PM check-in's own em-dash fix) failed on `gate_publish_image_current`, not on tests**: that commit touched only `BACKLOG-2026-09-07.md`, never `site/`, so it could not re-trigger `publish-image.yml`'s path filter and the gap `ef623e4de`'s own test failure left behind (last real publish at `a86a3a81`) persisted. A concurrent session had already fired `publish-image.yml` by hand (`workflow_dispatch`, run 732, commit `5b3e47e8e`) before this cycle noticed; this cycle's own push (which does touch `site/`) will independently re-trigger both workflows on its own commit. Not treated as this cycle's own defect to fix by hand, since another session was already acting on it and a `site/`-touching push resolves it as a side effect.

**2026-11-05 (~11:0x UTC), scheduled operator cycle: Primary Bedroom's room page gained one scoped heading fix, closing 4 real keyword-coverage queries; its remaining partial rows confirmed exhausted (noise or unfixable without stuffing).** Picked up the prior PM check-in's handoff (Primary Bedroom, 40% uncovered, the highest-ranked room not yet row-by-row mined). Four queries scored one word short because neither "storage" nor "furniture" appeared in any heading on `/rooms/primary-bedroom.html`, though its own layout tip already describes both (the closet, the dresser, the nightstands). Retitled that heading to "Primary bedroom layout, furniture and storage", scoped to this room only in `ops/build_zone_pages.py`, checked against every other room's own "furniture" queries (guest bedroom, kids bedroom, nursery, dining room, family room, living room) to confirm none shifted. Rescored both keyword files: all four target queries moved to `covered`; room_guide_underperformance.py reads 40% to 36% uncovered. `preflight.py --skip-tests` clean (0 FAIL, 34 standing sandbox warnings, run unbuffered to a file this time rather than piped, which had silently swallowed a prior attempt's output). GitHub: still 29 open issues, none from Phil. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 121.

**PM check-in, 2026-11-05 (~11:2x slot): previous work confirmed finished (Primary Bedroom heading fix, entry 121), nothing new unblocked, Home Office handed to the operator as the next un-mined room.** Attached per Step 0: fetch, real unshallow from a shallow detached checkout, `checkout -B main origin/main`, ff-only onto `af1d27850`, tree clean. Confirmed finished, not cited: working tree already clean, main already pushed and matching `origin/main`, GitHub's own `checks.yml` green on every completed run since the fix (the two intermediate pushes were absorbed by the path-filtered concurrency group rather than failing, consistent with this file's documented push-trigger behaviour). `preflight.py --skip-tests` run fresh, unbuffered to a file: 0 FAIL, standing warnings only (file-size tripwires, dated disclosures, Etsy fee-schedule/category fetch gaps, `ci-conclusion-current` unchecked while the latest push's own run was still in progress). GitHub re-pulled directly: 29 open issues, all `decision`/`blocked-on-art`, unchanged since 2026-11-02, none from Phil. `OWNER-ACTIONS.md`'s open section re-read: every row genuinely needs Phil's own account or money. Re-ran `room_guide_underperformance.py` fresh rather than trust the prior ranking: Garage/Hall Closet/Pantry/Patio or Deck/Kitchen/Mudroom/Primary Bedroom are all individually mined and confirmed exhausted (entries 114-121); Home Office is now the highest-ranked room (38% uncovered, 30 partial of 79 on-topic rows) that has not yet had a dedicated row-by-row read. Not mined this slot: that is an hours-scale task belonging to the hourly operator at :43, not this 30-minute triage. No small closing job found beyond this reconfirmation. No push notification: nothing material changed on the owner-facing picture since the last one. Dashboard regenerated, pushed to main.

**2026-11-05, scheduled operator cycle: entry 128's "no room left unmined" handoff was wrong, re-checked against a live rescan rather than trusted; Garage was still top-ranked at 51% uncovered, never fully mined, only 3 rows closed across entries 114/117.** Read its full scored partial list directly rather than the ranking tool's own 8-row sample and found a title-word-overlap noise cluster, not content gaps: "cricut supplies"/"prepping supplies" collided with the Automotive Care Zone's title (fluids/cables/rags content, nothing about a craft cutter or doomsday prepping); "pics on wall"/"pictures on a wall" collided with Hand Tool Wall and Cabinets' title (pegboard/tool content, nothing about hanging photographs). Checked each zone's real `content.json` and the full corpus before excluding (neither phrase is ever `covered` anywhere), added the four-phrase branch to `ops/room_guide_candidates.py`'s `OFF_TOPIC_CONTEXT`. A fifth candidate ("camping gear"/"hunting and fishing gear" onto Sports and Recreation Zone) was checked and correctly rejected: that zone's real content never addresses those activities, so it is a genuine content gap, not a wording gap, and forcing a synonym onto it would be the dishonest-labelling shape A32 already warns against. Fail-then-pass proved directly (4/4 new cases failed pre-fix, 25/25 passed post-fix); `test_room_guide_underperformance.py` 18/18. Re-ran live: Garage 170→166 on-topic, 51%→49% uncovered, matching exactly. `fix_dashes.py`/`fix_dialect.py --check`, `py_compile`, `check_urls.py` (235/235), `audit_pages.py` (240/0) all clean; full `preflight.py --skip-tests` reached 0 FAIL through every gate before genuinely stalling at the documented network-bound `gate_etsy_pdfs_current` (confirmed by flat CPU, not assumed). GitHub: still 29 open issues, none from Phil since 2026-11-02. No price, product or site page touched; measurement/ranking-tool fix only, `IndexNow` not applicable. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 129. **Next room-ranking claim should always be re-derived live, not cited:** Garage still has ~79 partial rows left (mostly documented retailer/geo-modifier noise) for the next slot.

**2026-11-05 (~22:0x UTC), scheduled operator cycle: two genuine Garage zone-synonym gaps mined ("cleaning" against the Automotive Care Zone, "ceiling" against the Bulk and Overhead Storage), closing Garage from 49% to 45% uncovered.** Re-derived `room_guide_underperformance.py` live rather than cite entry 130's ranking: Garage was still top, 49% uncovered. Read its full 80-row partial list (not the tool's own 8-row sample) against `content.json` before acting; most rows are documented noise already correctly left alone (retailer/platform names, construction/DIY intent, growing-a-garden queries, "garage sale" queries, the already-rejected camping/hunting/fishing-gear cluster). Added "car cleaning zone" to `Garage|Automotive Care Zone` and a new `Garage|Bulk and Overhead Storage` entry ("ceiling zone") in `ops/zone-also-called.json`. One false start caught before shipping: "ceiling storage zone" collided with unrelated digital-context queries on the bare word "storage" (`check_also_called_digital_collision_fast.py`), renamed to "ceiling zone" alone. Verified directly: 4 of 5 target queries moved `partial` to `covered` (1.0, 0 unmatched words) on rescore of both `ops/keyword_demand.py` and `ops/keyword_demand_global.py`; the fifth stays an honest `partial`. `test_gate_zone_also_called_is_heading.py` (6/6), `test_gate_also_called_no_digital_collision.py` (5/5), `test_keyword_demand.py` (30/30), `check_urls.py` (235/235), `audit_pages.py` (240/0), `fix_dashes.py`/`fix_dialect.py --check` (0/0), `affiliate.py --check`, `check_sellable.py` (124/126), `link_graph_report.py` (0 orphans), `build_id.py --check` (current), `audit_visual.py` scoped to both changed pages (0 findings except a non-deterministic "targets under 44px" count confirmed as sandbox measurement noise on unedited global nav markup, not a regression) all clean. A mid-cycle `preflight.py` rerun briefly FAILed on a stray `_visual_probe.html` this cycle's own concurrent `audit_visual.py` runs left behind; `gate_no_stray_probe_files` deleted it as designed, a clean rerun reached 0 FAIL again. GitHub: still 29 open issues, none from Phil since 2026-11-02. No price or product touched; two existing zone pages edited via their generator, no new page. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 133.

**2026-11-06 (~00:5x UTC), scheduled operator cycle: closed the standing `zone_faq()` durability-question thread entries 131/134/135 had each handed forward, by finishing the human read pass entry 135 deferred and deciding not to build.** Dumped and read all 114 zones' real `passes.sustain` text directly from `content/manual/source/content.json`, not the prior cycle's 5-keyword grep. Beyond the already-known Nursery diaper line, found six more genuine durability-shaped lines (Pantry leaveners, bathroom cosmetics and medicine dates, Home Office tax retention, Garage brake fluid/coolant, Workshop extinguisher/first-aid dates), then checked all six against the full 4,989-row measured keyword demand corpus (both files): none appear anywhere. The mechanism's real reach is the one query already found, still `partial`. Decided not to build a `zone_faq()` change touching all 114 zones' structured data to recover one low-signal query in a sandbox that cannot run `gate_tests` to completion; closed the thread by that decision rather than deferring it again. No code, content, price or page touched. `preflight.py --skip-tests` reran clean (0 FAIL through every gate reached) before stalling again at the documented network-bound `gate_etsy_pdfs_current`, killed by hand rather than waited out, same as recent cycles. GitHub: still 29 open issues, none from Phil since 2026-11-02; issue #42's cadence question unanswered. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 136.

**2026-11-06 (~05:1x UTC), scheduled operator cycle: closed the Kitchen island content gap (BACKLOG-2026-09-07.md A61) after reading eight rooms' full partial-row lists and declining three other candidates that did not clear the evidence bar.** "Toolbox" (Garage) is only published content.json text as a Laundry Room clutter example, not real Garage vocabulary; "dishes" (Kitchen Sink Zone) collides with the different "baking dishes"/"oven dishes" sense already live elsewhere; "coat hooks with shelves/on a board" (Mudroom) describes a different physical object than the Family Hook Zone's hooks-only design. "Kitchen island" was genuine (3 queries, neither "island" nor "countertop" anywhere in content.json, no bare "island" query in either corpus to risk a gaming-context collision); added a new "Kitchen island" tip grounded entirely in already-published zone facts, through the existing `tips.get(label)` mechanism rather than a zone rename, since an island is not honestly any one zone's other name. Rescored both corpora live: all 3 target queries moved to `covered`, 0 regressions; Kitchen 41% to 40% uncovered. `preflight.py --skip-tests` 0 FAIL twice (before and after), standing sandbox warnings only. 29 GitHub issues unchanged, none from Phil since 2026-11-02. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` A61.

**2026-11-06 (~19:2x UTC), scheduled operator cycle: `gate_status_deploy_verdict_current` caught a real, live "source corrected, sibling never told" gap during this cycle's own preflight run, fixed in the same cycle.** The 18:2x cycle's own deploy confirmation had updated the Production Knowledge paragraph to build `dedcbbebccc28c7f` (commit `8ff203bdf`, `checked_at` 2026-11-06T18:22:55Z) but never touched `BLOCKER-001`, section 4's "Public website" row, section 5's "Currently Deployed Build"/"Confirmed At"/"Repository HEAD Build" lines, or section 6's "Production traceability" row, all four of which still cited the two-days-stale `dfc7253ae2164447`/2026-11-04T08:17:47Z. Re-derived directly before touching anything: `resolve_verdict_commit('dedcbbebccc28c7f')` resolves to `8ff203bdf`; `deploy_gap_material_commits('8ff203bdf')` against real current `HEAD` returns an empty list, matching `site/build-id.txt` exactly. All four citations corrected to match; `gate_status_deploy_verdict_current()` re-run directly afterward returns clean (`None`), and `test_gate_status_deploy_verdict_current.py` (14/14) still passes. `preflight.py --skip-tests` reran clean (0 FAIL, 34 warnings, same standing sandbox gaps) both before and after this edit. GitHub re-pulled live: still 29 open issues, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02 (issue #42 unchanged). No new room-level keyword or content gap found this cycle: independently re-checked the gap tiers of both keyword corpora and confirmed every remaining row is documented off-topic noise (construction/DIY-build intent, word-sense collisions, retailer/platform mentions) or a genuine content gap outside this mechanism's scope ("building beds for kids organization": no bed-furniture text exists anywhere in Kids Bedroom's `content.json`, and the query's own intent is building furniture, not organizing it), consistent with entry 145's "fully exhausted" finding; declined rather than forced. Full account in `ops/NIGHTLY-LOG.md`.

**2026-11-06 (~20:1x UTC), scheduled operator cycle: the room-guide "fully exhausted" finding (entry dated 2026-11-04 above, repeated and re-confirmed by name in at least six later entries including the one directly above) was never actually true; a real measurement bug in the ranking tool itself, not the content, hid 441 real queries from every room's uncovered count.** Mining Garage's own partial tier for a wall-mounted-tool-organizer wording gap (closed via `zone-also-called.json`, the usual mechanism), the two target queries used British "organiser"/"organised" spelling, and the fix for one of them did not move that room's own uncovered percentage at all, which should not happen for a real `partial`-to-`covered` move. Traced it to `ops/room_guide_candidates.py`'s `ON_TOPIC` regex (`organiz|declutter|clean|storage|stock`), reused unmodified by `room_guide_underperformance.py`: it requires the American "organiz" spelling literally and has never matched British/Australian/Canadian "organise"/"organisation"/"organiser" (with an s). `keyword_demand.py` and `keyword_demand_global.py` both score and route every such query correctly; only this ranking tool's on-topic tally, the one every "room X is exhausted" finding since 2026-11-03 has been read from, silently dropped them before a human or a later cycle ever saw them. Counted directly against the live corpus before fixing: 441 rows (28 US, 413 global) carry "organis" and no other `ON_TOPIC` word, all invisible to every room's uncovered-percentage ranking this whole lane has used. Checked for new false positives before shipping (CLAUDE.md 5d): sampled 61 of the newly-visible queries with no obvious room/furniture/storage word; a handful are genuinely off-topic ("how to organise a charity walk", "a seating plan", "a strategy", "drop shipping"), the exact shape `OFF_TOPIC_CONTEXT` already excludes for the American spelling, so broadening this pattern surfaces them to the same existing filter rather than bypassing it. Fixed to `organi[sz]|declutter|clean|storage|stock`. Fail-then-pass proved directly (reverted the regex, added test, watched it fail with the exact pre-fix behaviour, restored, watched it pass); `ops/tests/test_room_guide_underperformance.py` 19/19, `ops/tests/test_room_guide_candidates.py` 28/28. Re-ran the ranking live, before/after: **Kitchen 39% to 44% uncovered, Garage 36% to 37%**, both going up, not down, because real demand that was always there became visible; this directly contradicts "fully exhausted," which was computed on an undercount the whole time. No content was touched by this fix; it only corrects what the ranking tool can see. The 441 newly-visible rows are mostly expected to resolve the same way the American-spelling rows already have (noise, already-covered, or a genuine small gap), but reading all of them is multiple cycles' worth of work, explicitly not attempted in one sitting (CLAUDE.md 18's work-in-progress limit); handed to the next cycle as the real next step in this lane, not a new "exhausted" claim. Separately, closed the original Garage finding: added "wall-mounted tool organizer" to `Garage|Hand Tool Wall and Cabinets` in `zone-also-called.json` (self-flattery checked first: "mounted" in 3 of 243 pages' headings, "mount" in 0, well under the bar that blocked "systems"; only 3 live queries anywhere contain "mount"/"mounted", all already about this exact zone), moving 2 of 3 to `covered`; the third (bare singular "mount") stays honestly `partial`. `check_also_called_digital_collision_fast.py`, `test_gate_zone_also_called_is_heading.py` (6/6), `check_urls.py` (235/235), `audit_pages.py` (0 duplicates), `fix_dashes.py`/`fix_dialect.py --check` (0/0), `affiliate.py --check`, `check_sellable.py`, `link_graph_report.py` (0 orphans), `build_id.py --check`, `audit_visual.py` scoped to the changed page (desktop and mobile, 0 findings each) all clean. `preflight.py --skip-tests` run fresh, 0 FAIL through every gate reached. 29 GitHub issues re-pulled live, unchanged since 2026-11-02, none from Phil. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` A68/A69.

**2026-11-07 (~11:0x UTC), scheduled operator cycle: closed the remaining, unchecked share of the 2026-11-06 ~20:1x "organis" British spelling fallout (BACKLOG-2026-09-07.md entry 152), no new fixable gap found.** Entries 148 to 151 the same day (2026-11-07) had already read Pantry, Kitchen, Garage and Hall Closet in full, covering most of the room tagged rows that fix made newly visible. Read the rest directly rather than cite the 2026-11-06 entry's own 61-row sample: all 111 live `gap`/`partial` rows containing "organis" across both keyword corpora, including the 88 of them that carry no room tag at all and so were outside every per-room read done so far. All 111 checked against real `content.json`/rendered page text; every one is either a retailer, platform or locale suffix (kmart, ikea, pinterest, reddit, dropbox, bunnings, target, australia, tamil, india), a genuinely off topic activity sharing the bare word "organise" (a bake sale, a charity walk, a seating plan, drop shipping, a step challenge), or a single generic filler word short of a page that already covers everything else in the query (oven, appliances, way, chef, large). "car boot"/"car organisation essentials" and "kids playroom" were checked by name and confirmed the same honest no-zone-to-route-to gaps entry 150 already left open for Garage's car interior cluster; nothing new. `preflight.py --skip-tests` 0 FAIL, 33 standing sandbox warnings. `cold_read_ledger.py --next`: 308 of 308, nothing left to cold read. GitHub re-pulled live: still 29 open issues, all `decision`/`blocked-on-art`, none from Phil since 2026-11-02; issue #42's cadence question still unanswered. `inbox_agent.py --apply`: no mail credential here, unchecked. No price, product or site page touched; no code change, a measurement question answered, not a defect found. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 152.

**2026-11-07 (~23:0x UTC), scheduled operator cycle: claimed the Primary Bedroom room-guide tier three prior cycles had each declined as too large for a 30-minute slot; three genuine gaps closed, the rest of its 34-row tier read and correctly left alone.** Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 159: a color-sorting closet FAQ, an under-the-bed storage FAQ, and an honest ADHD-friendly-framing FAQ, all grounded in facts `content.json` already states, added to the hand-authored `how-to-declutter-a-bedroom.html`; checked every corpus row containing the same three words for collision before shipping, found none. Room's own uncovered share: 24% to 23%. `preflight.py --skip-tests` 0 FAIL both before and after, same documented `gate_etsy_pdfs_current` network stall (flat CPU over 80s, confirmed not a hang) killed by hand. GitHub: still 29 open issues, none from Phil since 2026-11-02; issue #42 read in full, not re-raised, nothing in it has changed.

**2026-11-07 (~23:3x UTC), PM check-in: a real measurement bug in `household_room_signal()` found while chasing a single Primary Bedroom gap row, fixed at the root; 67 corpus rows across both keyword files corrected, zero regressions.** Previous work (entry 159 above) reconfirmed finished independently this slot (fresh `preflight.py --skip-tests` 0 FAIL, 29 GitHub issues re-pulled live, deploy-verdict citations re-derived directly and confirmed current, not stale). Of the six single-row room-guide `gap` entries left across all 20 rooms, five were documented noise or already-declined; the sixth, "nightstands with hidden storage", scored to Family Room's blanket zone via the word "storage" alone. Traced the real cause: `household_room_signal()`'s plain substring check let Family Room's synonym "den" match inside "hidden" (and "garden", "wooden", "dental", 74 rows total), winning a false room-signal tie against Primary Bedroom's own nightstand zones. Fixed with a real word boundary in `ops/keyword_demand.py` (shared by `keyword_demand_global.py`), plural-tolerant after a first version broke three genuine matches ("backyards", "larders own", "types of master bedrooms") caught by a full before/after corpus diff before shipping. Final diff: 67 rows corrected, zero regressions, re-verified after the correction. New test case 28 (8 assertions) in `ops/tests/test_keyword_demand.py` proves it fail-then-pass. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` entry 160. `preflight.py --skip-tests` 0 FAIL after the fix, same documented network stall. GitHub re-pulled a second time: still 29 open issues, none from Phil.

**2026-11-11 (~09:5x UTC), scheduled operator cycle: added `gate_nightly_log_entries_not_overlong`, the gate for the cause rather than the symptom of the living-docs bloat this section's own `gate_living_docs_total_size_tripwire` keeps warning about.** All 31 open GitHub issues checked fresh: still every one `decision`/`blocked-on-art`/`P0`, none from Phil; a push notification on exactly this (31 decisions, owner silence) already went out 2026-11-10 with a stated no-repeat-before of 2026-11-12, so not repeated here. Confirmed via `OWNER-ACTIONS.md`'s 24 numbered items and the room-guide lane's own history (STATUS.md 2026-11-06 ~20:1x above) that the lane has real content gaps left but its own self-audit entries now run 1,500-6,000+ words against the operating prompt's stated 250/120-word budget, 41 of them in the current log window alone. New gate warns (not fails) on any recent entry over 750 words; fail-then-pass proved in `ops/tests/test_gate_nightly_log_entries_not_overlong.py` (4/4), confirmed firing on the real file (41 offenders) without disturbing any sibling oversized-doc gate. `preflight.py --skip-tests` 0 FAIL through every gate reached, same documented `gate_etsy_pdfs_current` network stall, killed by hand, confirmed no stray files. No price, product or site page touched.

**Older entries (123 of them, 2026-08 to 2026-11-04) live in `STATUS-ARCHIVE.md`.** Rotated 2026-11-04 by `ops/rotate_status_metadata.py --apply`: kept live only the entry (or entries, where more than one shares the same most recent date) carrying 2026-11-04, the actual most recent date found in the chain, not simply whichever entry happened to sit physically first (the chain had drifted out of newest-first order); 4 more entries moved to the archive. Nothing is deleted, and the gates that scan this file for stale claims (`gate_no_stale_session_label`, `gate_no_stale_checkout_count`, `gate_no_stale_listmonk_blocker`, `gate_corporate_buy_path_current`, `gate_critical_risks_escalated`) scan the archive too, so an archived claim is no less checked than a current one.

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
| Public website | LIVE, build `d979ab225efc1ae3` (confirmed 2026-11-11T05:13:38Z), **2 commits undeployed per this record, deploys automatic** (see `BLOCKER-001`) | **CORRECTED 2026-11-11 (~08:1x slot), PM check-in: this row still cited the 2026-11-10 confirmation, stale against a newer `ops/deploy-verdict.json` record, the same "source corrected, sibling never told" shape this row has recorded before.** Re-derived directly: `resolve_verdict_commit('d979ab225efc1ae3')` resolves to `fc174da0c`; `deploy_gap_material_commits('fc174da0c')` against real current `HEAD` (`a26ba07c4`) returns `['325844b8e', 'ef879af3c']`. Deploys are automatic, so production has very likely already caught up; this sandbox cannot confirm it directly, so the gap is reported honestly rather than zeroed out. |
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

**CORRECTED 2026-10-26, scheduled operator cycle: the "Repository HEAD Build"/"Confirmed At" lines below still cited the stale `a1c75dafaee8ca8c` build and claimed a 4-commit, 2-material gap, re-derived directly rather than trusted, the same fifth-section gap this paragraph's own prior correction named and left unfixed.** `site/build-id.txt` reads `00187aebb3255957` directly, matching `ops/deploy-verdict.json`'s own confirmed build exactly; `deploy_gap_material_commits` re-derived against current `HEAD` (`267697dcf`) returns an empty list. Repository HEAD and the confirmed deployed build are the same thing right now: zero commits undeployed. Fixed below; this gate still does not parse this section, so it can drift again. Prior state, kept because the shape recurs: **CORRECTED 2026-10-26, PM check-in (05:4x slot): this section had stood unedited since the 2026-09-25T22:21:27Z confirmation even though `ops/deploy-verdict.json`, `BLOCKER-001` and section 4's own "Public website" row had each moved past it since, the same "source corrected, sibling section never told" shape `status_deploy_verdict_problem`'s own docstring names, just for a fifth section that gate does not parse (it checks only BLOCKER-001, Production Knowledge, and the Public website/Production traceability table rows).** Found while confirming the previous cycle's handoff rather than citing it; not yet added to that gate's section map, so this can still drift silently again until it is.

**Currently Deployed Build (last confirmed):** `d979ab225efc1ae3` (resolves to commit `fc174da0c`), confirmed 2026-11-11T05:13:38Z in `ops/deploy-verdict.json`, superseding `aeb22db95bcb7ece`/2026-11-10T08:28:29Z. **CORRECTED 2026-11-11 (~08:1x slot), PM check-in:** this field still cited the 2026-11-10 confirmation, the same gate-unparsed fifth-section drift this paragraph's own history already names; re-derived directly against current `HEAD` (`a26ba07c4`): `deploy_gap_material_commits(resolve_verdict_commit('d979ab225efc1ae3'))` returns `['325844b8e', 'ef879af3c']`, two material commits since this verdict was recorded. Not re-confirmed live (no VPS/SSH credential in this sandbox); reported as a 2-commit gap against the last real confirmation, not as zero.
**Confirmed At:** `2026-11-10T08:28:29Z` (`ops/deploy-verdict.json`, written by
an automated GitHub Actions confirmation after live `build-id.txt` was read equal to the repository)
**Repository HEAD Build:** `aeb22db95bcb7ece` (`site/build-id.txt`, re-read directly
2026-11-10 ~08:4x slot against current `HEAD`, commit `c0d74250f`). **CORRECTED
2026-11-10 (~08:4x slot), PM check-in: this field now matches the confirmed
deployed build above exactly.**
**Matches the confirmed deployed build above: 0 commits undeployed**
(`deploy_gap_material_commits(resolve_verdict_commit('aeb22db95bcb7ece'))`
re-derived directly against current `HEAD`, returns an empty list).
`VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) makes redeploy automatic.
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
| Production traceability | Tracked, current build citation, **2 commits undeployed per this record, deploys automatic**, build `d979ab225efc1ae3` | **CORRECTED 2026-11-11 (~08:1x slot), PM check-in**, same as the Public website row above: this row still cited the 2026-11-10 confirmation, stale against a newer `ops/deploy-verdict.json` record; `deploy_gap_material_commits(resolve_verdict_commit('d979ab225efc1ae3'))` re-derived against current `HEAD` (`a26ba07c4`) returns `['325844b8e', 'ef879af3c']`, not an empty list this time; reported as unconfirmed rather than closed since this sandbox cannot reach the live site. |
| Repository hygiene | 31 open issues (10 `P0`, 29 `decision`, 2 `blocked-on-art`), 0 open PRs, 1 branch, 220+ test files, `preflight.py` clean | **Corrected 2026-11-09 (~21:1x UTC), PM check-in:** the prior "29 issues" row had gone stale by two; confirmed live via the GitHub API this cycle (31 open, `#2,#15,#18,#21,#29,#31,#33,#42,#43` through `#65`), 0 open PRs. Issues #64 and #65 (opened 2026-11-08, both already tracked with a backlink in `OWNER-ACTIONS.md`) were the ones widening it. Prior state, kept because the shape recurs: **Corrected 2026-11-04 (~15:4x UTC), PM check-in:** the prior "30 issues" row had gone stale by one, same closure already noted at line 79 above; confirmed live via the GitHub API this cycle (29 open, `#2,#15,#18,#21,#29,#31,#33,#42,#43` through `#63`), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-11-02, PM check-in:** the prior "24 issues" row had gone stale; issues #57-#63 (opened 2026-11-01, 7 more `OWNER-ACTIONS.md` items never previously tracked) widened it to 30. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #40, #42, #43 through #63), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-11-01, scheduled operator cycle:** the prior "16 issues" row had gone stale; issues #49-#56 (opened 2026-11-01, 8 more `OWNER-ACTIONS.md` items never previously tracked, including one CRITICAL risk, RISK-0011, split across two items) widened it to 24. Also closed a related gap the same cycle: four of the six 2026-10-31 issues (#45-#48) had never had their own OWNER-ACTIONS.md section tell Phil the issue existed; all thirteen items now carry a backlink, and a new `gate_owner_actions_items_tracked` preflight gate warns if a future item goes untracked again. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40, #42, #43, #44, #45, #46, #47, #48, #49, #50, #51, #52, #53, #54, #55, #56), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-11-01, PM check-in:** the prior "10 issues (8 decision)" row had gone stale; issues #43-#48 (opened 2026-10-31, each an `OWNER-ACTIONS.md` item never previously tracked as an issue) widened it to 16. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40, #42, #43, #44, #45, #46, #47, #48), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-10-20, PM check-in:** the prior "9 issues (7 decision)" row had gone stale; issue #42 (the 2026-10-14 cadence-waste question, `decision`-labelled) was never added here. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40, #42), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-10-12, PM check-in:** the prior "8 issues (6 decision)" row had gone stale; issue #40 (the 2026-10-09 usage-limit stall, `decision`-labelled) was never added here even though `OWNER-ACTIONS.md` item -1 and several `NIGHTLY-LOG.md` entries already cite it. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-09-25 06:1x, PM check-in:** the prior "7 issues (5 decision)" undercounted; issue #35 (`VPS_DEPLOY_KEY`, opened 2026-09-24) is a sixth `decision`-labelled issue, confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35). Not a formal audit, but the working facts a reader would otherwise have to reconstruct from `NIGHTLY-LOG.md` |

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
| Sessions | 49 | Last 30 days | MEASURED 2026-10-02 (visitors; 121 visits, 719 pageviews), direct Umami database read over ssh, filtered to this site's website_id. Flat on the 48/119/731 of three days earlier; late-August days leaving the window explains part of the earlier slide. An unfiltered read on 2026-09-29 said 239: this Umami instance serves three sites, and `ops/experiments.py` now refuses that query shape. The 7 Sept automated session (431 pageviews) is long out of the window, so this figure is very nearly all human; previous 48 (09-29), 57 (09-25), 68 (09-23), 76 (09-21), 78 (09-17), 75 (09-14) |
| Sessions | 7 | Last 7 days | Human-plausible, same source, 2026-09-29. Recorded 14 visitors / 18 visits / 50 pageviews, but 30 pageviews and 9 visitor ids landed between 18:00 and 18:20 on 27 September, all direct, across four operating systems, a signature that also appears late on 23 August. Ex-burst: 7 visitors, 9 visits, 20 pageviews, DOWN on 12 / 14 / 27. **A first draft of this row today called it the first rise on every measure; checking where the pageviews came from withdrew that** |
| Organic sessions | 6 visits from 5 visitors, whole life of the site, re-measured 2026-10-02 (1 Bing, 21 August; 5 Google visits from 4 visitors, 4 September to 1 October) | Direct Umami database read, not carried forward. The number moved for the first time in three weeks: one more Google visitor, most recent organic arrival now 1 October rather than 18 September |
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
| Search Console connected | YES, since 2026-10-14 | **Corrected 2026-11-03, PM check-in: this row still said NO and pointed at a stale `OWNER-ACTIONS.md` item 2, over three weeks after Phil verified the Domain property.** Phil set up the Domain property via a DNS TXT record (not the meta tag this row used to check for), confirmed live by `nslookup` at the time and recorded in `ops/site-verification.json`'s `google_dns_txt` field; `gate_site_verification_declared` passes clean on it, most recently this cycle. The live DNS record itself is UNCHECKED this cycle (no egress from this sandbox to query it), not re-confirmed live, but nothing has flagged it missing since. Verification does not supply impressions/clicks/queries data by itself: this sandbox still has no Search Console API credential, so the rows below stay UNKNOWN until read access exists |
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
| Articles | 48 published, differentiated per zone (`gate_general_reading_differentiated`) | **Corrected 2026-11-02, scheduled operator cycle:** this row still read 29/26.7, stale since well before the eight room guides this week (bedroom, kitchen, garage, workshop, laundry, pantry, living room, guest bathroom) plus the kids bedroom guide this cycle. Re-measured directly via `ops/link_graph_report.py`: 0 orphans, avg 21.3 inbound links each (lower average is more pages sharing a fixed set of hub links, not weaker linking; min inbound is 2, no page under-linked) |
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

**Status:** CLOSED, 2026-10-03, PM check-in. Opened 2026-09-07. Every item is
now done, dropped, or genuinely gated on Phil: M1-M5, A1-A18, B1-B9 and C1-C4/C7
all shipped (see the "Done"/strikethrough rows throughout this section and
`BACKLOG-2026-09-07.md` sections 2-4). M6 stays shut per `DECISIONS.md` D-021/
D-026 (needs real zone entrances or a Search Console read, neither true yet).
S1-S4 (the structured `sustain_detail` schema) are DROPPED, not merely
deferred: see `DECISIONS.md` D-029, recorded this cycle, closing the open
question this section itself raised on 2026-09-09 and nobody had revisited
since. C5/C6 stay on Phil (Gemini billing, YouTube OAuth). This closure frees
a WIP slot under `CLAUDE.md` section 18's limit of 3; no replacement
workstream is opened here, since nothing in the current backlog is both
unblocked and workstream-sized (`BACKLOG-2026-09-07.md` section 7).  
**Owner:** operator, direction from Phil  
**Objective:** `PLAN-MICROZONES-DECKS-APP.md` + `BACKLOG-2026-09-07.md`
section 2/3: build the root-cause diagnostic layer the product currently
lacks (0 of 114 zones map a root cause), fix the app's first thirty seconds,
and ship the free unillustrated Kitchen deck.

**Archived 2026-10-24, scheduled operator, by `ops/rotate_status_workstreams.py --apply`:** the dated build-log narrative that used to sit here (2026-09-07 through 2026-09-25, M1 through B9, the full account of how this workstream reached the closure above) moved verbatim to `STATUS-ARCHIVE.md`. The closure summary above is the current, live statement; nothing below it was left unresolved.


---

# 15. Current Experiments

No experiment should be treated as active until its implementation and measurement are verified.

| Experiment | Status | Owner | Primary Metric |
|---|---|---|---|
| None verified in this status file | NONE VERIFIED | - | - |

Active experiments should also be tracked in `EXPERIMENTS.md`.

---

# 16. Current Incidents

No current incidents. The 5 incidents previously tracked here (INCIDENT-001 through INCIDENT-005, all RESOLVED or STALL NOT RECURRING) were moved verbatim to `INCIDENTS.md` by the 2026-11-06 PM check-in (~04:1x slot), per this section's own standing rule below and `gate_living_docs_total_size_tripwire`'s finding that this section (15.8KB, all of it resolved history) was most of STATUS.md's overage past its 110000-byte tripwire. Nothing was edited on the way over; CLAUDE.md 54 ("Failure Is Information") still holds, the record is just no longer read every cycle as if it were current.

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

**CORRECTED 2026-11-09 (~22:4x slot), PM check-in: this section still cited the 08:1x confirmation below, 14 hours stale against `ops/deploy-verdict.json`'s own newer record.** Re-derived directly: `resolve_verdict_commit('0aef00af365fe703')` resolves to `ff48f126e`; `deploy_gap_material_commits('ff48f126e')` against real current `HEAD` (`a8519ae29`) returns an empty list, and `site/build-id.txt` matches exactly. Production matches the repository exactly, 0 commits undeployed.

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

The section 30 "Production Knowledge" chain is rule 6 applied automatically:
`gate_status_production_knowledge_not_oversized` in `ops/preflight.py` warns
once more than the newest entry plus a small buffer has piled up, and
`python ops/rotate_status_history.py --apply` moves the rest into
`STATUS-ARCHIVE.md`, verbatim. Found 2026-10-23 at 37 live entries, never
enforced before that date.

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

**Production Knowledge, CORRECTED 2026-11-11 (~08:1x slot), PM check-in: build `d979ab225efc1ae3`, confirmed `2026-11-11T05:13:38Z`, 2 commits undeployed per this record.** The prior entry (build `aeb22db95bcb7ece`, 2026-11-10T08:28:29Z) had gone stale against `ops/deploy-verdict.json`'s own newer record by the time this cycle re-checked it. `resolve_verdict_commit('d979ab225efc1ae3')` resolves to `fc174da0c`; `deploy_gap_material_commits('fc174da0c')` against real current `HEAD` (`a26ba07c4`) returns `['325844b8e', 'ef879af3c']`, two site content edits that landed after this verdict was recorded. No P0 regression in either commit (a misroute fix and a content-gap close, both already shipped to `main` and gated by the same checks every room-guide fix in this lane passes). Deploys are automatic, so production has very likely already caught up; this sandbox has no SSH/VPS credential to confirm it directly, so the gap is reported as unconfirmed rather than closed. (Prior confirmations stay in `ops/NIGHTLY-LOG.md`, not kept inline here per this field's own current-only rule, section 24.)

**Business Data Knowledge, re-measured 2026-09-29, WIDENED 2026-10-02 (scheduled operator cycle): caught by `gate_goals_traffic_current` on this cycle's own `preflight.py` run, this paragraph was three days stale against `GOALS.md`'s own current baseline.** ONE MEASURED TRANSACTION EVER ($19 GROSS, 2026-08-21, A REFERRAL). CURRENT TRAFFIC BASELINE (`GOALS.md`, MEASURED 2026-10-02 BY A DIRECT UMAMI DATABASE READ, FILTERED TO THIS SITE'S `website_id`): 49 VISITORS ACROSS 121 VISITS AND 719 PAGEVIEWS IN 30 DAYS, FLAT ON THE 48/119/731 OF THREE DAYS EARLIER. THE TRAILING WEEK ROSE FOR THE FIRST TIME IN THREE WEEKS: 22 VISITORS / 29 VISITS / 62 PAGEVIEWS AS RECORDED, 13 VISITORS / 20 VISITS / 32 PAGEVIEWS EXCLUDING ITS OWN BUSIEST 20-MINUTE BUCKET (THE SAME 27 SEPTEMBER SIGNATURE NAMED BELOW), AGAINST 7 EX-BURST THREE DAYS EARLIER. READ HONESTLY THIS COULD BE NOISE ON A SMALL NUMBER, NOT A TREND. AN UNFILTERED READ ON 2026-09-29 SAID 239 VISITORS, BECAUSE THIS UMAMI INSTANCE SERVES THREE SITES; `ops/experiments.py` NOW REFUSES A `website_event` QUERY THAT NAMES NO WEBSITE. IN UMAMI `session_id` IS THE VISITOR AND PERSISTS ACROSS DAYS, THE VISIT IS `visit_id`. BUY-CLICKS: 11 ALL TIME FROM 9 DISTINCT VISITORS (BOOK 4, METHOD 3, CONSULTING 2), OF WHOM ONE EVER PAID. **CORRECTED 2026-09-29: THIS LINE READ "STRANGERS' BUY-CLICKS SINCE 7 SEPT: 0" AND THAT IS NO LONGER TRUE**, THERE ARE CLICKS ON 14 AND 28 SEPTEMBER; `LEARNINGS.md` LRN-0010 WAS RIGHT WHEN WRITTEN AND HAS BEEN OVERTAKEN. THE EMAIL LIST IS READABLE, NOT UNREADABLE, AND MEASURED EMPTY: 0 SUBSCRIBERS (ISSUE #15, STILL UNRESOLVED, BLOCKS CAPTURE ENTIRELY).

**Executive Visibility:** LIVE, VIA `EXECUTIVE-DASHBOARD-LIVE.md` (GENERATED BY `ops/dashboard.py`, NOT HAND-TYPED)

**Immediate Focus:** UNCHANGED IN SUBSTANCE SINCE 2026-09-02, RE-CONFIRMED 2026-09-15: TRAFFIC, NOT ANALYTICS OR TECHNICAL DEBT, IS THE CONSTRAINT (`GOALS.md`). 2.5 VISITORS A DAY. THE CHANNELS THAT COULD CHANGE THAT (VIDEO PLATFORMS, LINKEDIN, PINTEREST, INSTAGRAM) NEED ACCOUNTS ONLY PHIL CAN CREATE (`OWNER-ACTIONS.md`); DISTRIBUTION PREP IS READY AND WAITING (114 ZONES OF VIDEO IN MULTIPLE CUTS, PINTEREST/INSTAGRAM CARDS FOR ALL 114 ZONES, ~4,939 READY-TO-PUBLISH SOCIAL UNITS TOTAL). THE DOMINANT DEFECT CLASS FOUND ACROSS MANY REVIEWS IS A CORRECTED SOURCE WHOSE SHIPPED ARTIFACT WAS NEVER RE-DERIVED (`BACKLOG-2026-09-07.md` SECTION 7). THE HONEST STATE OF THIS BUSINESS IS "COMMERCE WORKS, TRAFFIC IS MEASURED AND NEARLY ALL DIRECT, AND THE NEXT STEP ON EVERY DISTRIBUTION CHANNEL IS PHIL'S OWN ACTION." FOR CURRENT DEPLOY STATUS SEE THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE AND `BLOCKER-001`, NOT THIS LINE: the specific build/commit this line used to cite (2026-10-01, `8fbc6b7d3d2599ae`) went stale within hours and the 27-entry correction chain that followed, trying to keep up here too, is exactly the growth `ops/rotate_status_history.py --apply-focus` moved to `STATUS-ARCHIVE.md`, 2026-10-23, scheduled operator.

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
