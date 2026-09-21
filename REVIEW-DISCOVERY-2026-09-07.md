# Discovery review: what makes these pages rank, and the next 90 days

**Date:** 2026-09-07
**Scope:** organic search and answer-engine discovery for 6s-success.com
**Role:** seo-aeo
**Type:** report only. This review changed no file except itself.

**Status, 2026-09-14, operator:** re-verified against live code a week after
this report shipped. **D16** (visible FAQ answers) was already fixed the same
day by Phil (`9b7f5abb`, `faq_html()`), the report's own bottom line is stale
on that one point. **D7** (ungrammatical titles) verified still live and
fixed: `ops/zone-search-terms.json` gained overrides for the two nightstand
siblings and six "guest X guest Y" zones this pass found live but the report
under-counted (it named 4, the corpus had 8: also `guest closet`, `guest bed
and linens`), all title-only, no H1/display-name change, `audit_pages.py`
0 duplicate titles/descriptions after. **D6** (duplicate H1s / differentiation)
partially advanced as a side effect: the sibling cross-link mechanism the
generator already had picked up the newly-shared "vanity counter"/"closet"
terms automatically and added "The same zone in another room" sections to
`primary-bathroom-the-vanity-counter` and `primary-bedroom-the-primary-closet`,
without deciding which page should be primary for the shared query, which the
report correctly leaves gated on Search Console. **D11** (spelling
consistency) closed 2026-09-14, operator: every British organis*/organiz*
spelling normalized to American across the site (the shared "Before you
start" safety notice in `ops/build_articles.py`/`ops/build_zone_pages.py`,
27 hand-authored `site/articles/*.html` pages with no owning generator,
`ops/build_kit_page.py`/`ops/product_links.py`'s "organiser", one
hand-authored string in `content/manual/source/content.json`, and the free
sample book manuscript), except the one indexed URL
(`how-long-does-it-take-to-organise-a-room.html`) this review explicitly
said to leave alone. New `gate_us_spelling_consistency` in `preflight.py`
re-derives the real corpus on every run. **D15** (crawler log split) traced
2026-09-14 by a PM check-in, not built: "the existing log tooling" the
review refers to is VPS access-log analysis, which needs the SSH key this
environment has never had (the same standing gap `deploy-fresh`/
`live-links`/`owner-waiting` already warn about every cycle), so it is not
actually unblocked here. **D4** (household variants) shipped 2026-09-20,
operator, for the same 12-zone pilot cohort M4's diagnosis block already
uses (Entryway 5, Kitchen 7), per `BACKLOG-2026-09-07.md` section 5's
pilot-before-rollout rule. Each pilot zone now carries an "If your `<thing>`
is not like this" section with 2 real household conditions (no console/rents
and cannot drill/shared by several people/small kitchen/mobility limits,
chosen per zone from its own real purpose and done-looks-like text, nothing
invented) and concrete, different guidance under each, matching the
acceptance text verbatim. New `variants` field on `content.json`, rendered
by `variants_html()` in `ops/build_zone_pages.py`; new `gate_variants_rendered`
in `preflight.py` re-derives the block from the corpus and checks it against
the shipped HTML byte for byte, fail-then-pass proved against the real
committed file (`ops/tests/test_gate_variants_rendered.py`, 7 cases). Still
open, in report order: D15 (as above), D1-D3/D5/D8-D10/D12-D14 (larger-scope
pilot work), D19-D21 (Phil-gated). Full account in `ops/NIGHTLY-LOG.md`.

**Status, 2026-09-20, PM check-in:** the paragraph above went stale within a
week; **D1, D3 and D5 have since shipped** (operator cycles, 2026-09-20, full
detail in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` rows A5/A8/A9,
all 114 zone pages for D1, the same 12-zone pilot cohort for D3/D5). **D6's
own H1-and-grammar half is done, not merely "partially advanced" as the
09-14 note said**, verified live this cycle rather than carried forward: all
114 zone pages checked for duplicate H1 text, 0 found; the three exact pairs
this report measured (shower or tub, toilet area, two of the four dresser
drawers pages) each now carry a room-qualified H1 (`"The Shower or Tub, Guest
Bathroom"` vs `"...Primary Bathroom"`, etc.), and all six pages carry the
sibling cross-link section, not only the two the 09-14 note happened to
sample. D1's own `direct_answer()` also differentiates each sibling's opening
paragraph in practice (spot-checked the shower/tub pair: genuinely different
first sentences, not templated filler), satisfying D6's "states what makes it
different" acceptance line as a side effect, though this was not built for
that purpose and the ten groups were not all re-checked against it. The one
part of D6 still genuinely open is what the report itself gates: deciding
which page in each group is the primary answer for the shared query, blocked
on Search Console (`OWNER-ACTIONS.md` 1a), not guessed here. Also fixed this
cycle: the Day 0-7 checklist's own last row, "fix the `deck-gallery-mudroom.html`
orphan: it is in the sitemap with zero internal links. Link it or drop it
from the sitemap." Checked live: still a real orphan, zero inbound links,
present in `sitemap.xml`. `BACKLOG-2026-H2.md` 2.7/2.11 already record
Phil's explicit decision to hold the mudroom deck back from promotion until
the Entryway deck has evidence; `ops/build_deck_gallery.py` already gates
its `ImageGallery` schema on `deck == "entryway"` for that reason, but its
`<meta name="robots">` line was not gated the same way, so the page kept
asking to be indexed and kept landing in `scan_extra_pages()`'s sitemap
scan regardless. Gated `robots` the same way (`noindex` for any non-Entryway
deck, `follow` unchanged); regenerated, confirmed `site/sitemap.xml` 188 to
187 URLs, the mudroom page gone, `check_urls.py` (187/187) and
`audit_pages.py` (191/0) clean after. Dropped rather than linked, matching
the decision already on record rather than reversing it. Still open, in
report order: D2 (Phil-blocked), D6 (primary-page decision only), D8-D10,
D12-D14 (larger-scope pilot/decision work), D15 (traced, needs the SSH key
this environment lacks), D19-D21 (Phil-gated).

**Status, 2026-09-21, operator: D8 done, honestly partial.** The five
`ZONE_SPECIFIC_READING` articles this section names (keys, mail, charger,
medicine cabinet, junk drawer) were each linked from only the one zone
originally written for it, checked live before starting. Read every zone's
own published text for a genuine match rather than link zones to hit the
acceptance number: found 12 more real, specific mentions of the same
friction (a stray charger on 9 more zones across 5 rooms, mail and keys
each on 1-2 more, expired medicine on 1 more, a second junk drawer on 1
more), each grounded in a quoted sentence from that zone's own passes or
hazards, and added one `ZONE_SPECIFIC_READING` entry per match. The charger
article now clears this section's "at least 10" target (10 real inbound
links); keys (3), mail (4), junk drawer (2) and medicine cabinet (2) do
not, because no further zone's own text supported a genuine link without
fabricating one, which `CLAUDE.md` forbids. Recording that honestly here
rather than as a false "done": most homes have exactly one real zone for
each of those four topics, and this review's "at least 10" figure did not
anticipate that. Full detail, the transient test failure caught and
re-verified before shipping, and the exact list of new zone-to-article
links: `BACKLOG-2026-09-07.md` section 2, `ops/NIGHTLY-LOG.md` 2026-09-21.
Still open, in report order: D2 (Phil-blocked), D6 (primary-page decision
only), D10, D12-D14 (larger-scope pilot/decision work), D15 (traced,
needs the SSH key this environment lacks), D19-D21 (Phil-gated).

**Status, 2026-09-21, operator: D9 done, honestly partial.** This
section's own examples (entryway shoes vs mudroom shoe storage; kitchen
sink vs under-sink; nightstand vs nightstand) are not exact-noun matches,
so the existing sibling mechanism never linked them, checked directly
before starting. Built `ZONE_RELATIONS` in `ops/build_zone_pages.py`, 22
hand-curated real same-job groups across different zone names (workbench,
hand tools, cleaning chemicals, landing surfaces, shoes, coats, sinks,
nightstands, dressers, closets, desks, books, linens, charging, seating,
dining, cooking, garden tools, outdoor gear, paper storage, backstock,
floor paths, display), each checked against the zone's own real name, not
invented to hit a count; deliberately not exhaustive, since about a third
of the 114 zones have no genuine same-job counterpart in this content set
and forcing one would be the fabrication `CLAUDE.md` section 6 forbids.
**The floor half of this section's acceptance is met: 0 zones below 8
in-degree (was 1).** The median half is not: median in-degree 10 to 12,
average 10.7 to 12.2, against this section's "above 15" target; 17 of 114
zones now clear 15 (was 6), and 69 of 114 gained at least one new link.
Recorded honestly, matching D8's own posture immediately above, rather
than claimed done. Full detail: `BACKLOG-2026-09-07.md` section 2,
`ops/NIGHTLY-LOG.md` 2026-09-21. Still open, in report order: D2
(Phil-blocked), D6 (primary-page decision only), D10, D12-D14
(larger-scope pilot/decision work), D15 (traced, needs the SSH key this
environment lacks), D19-D21 (Phil-gated). Closing the rest of D9's own gap
needs either more genuine cross-room relationships than this pass found,
which risks diluting quality, or a structural change (D10's room-hub
depth is the more promising lever, since it changes how much link equity
each room's own hub page distributes rather than searching for more
pairwise matches).

**Reconciliation, 2026-09-21, PM check-in.** The 03:4x PM cycle and the
scheduled operator cycle immediately after it disagreed in `ops/NIGHTLY-LOG.md`
about whether D9 was done: the operator's own aggregate line listed D9 among
"D1, D3-D5, D7-D12 all confirmed live and done" with no D9-specific number
checked, while this section (written the same day, by D9's own author) already
recorded it honestly as partial. Re-ran `ops/link_graph_report.py` fresh
against the current `main` (`61ff3dfe`, after D10 shipped): zone-page inbound
links still run min 9, max 20, avg 12.2, identical to the numbers D9's own
status block above already recorded. **D10 did not move D9's number.** The
speculation two paragraphs up, that D10's room-hub depth "is the more
promising lever" for D9's median, does not hold in practice: D10 changed room
page H1s and the position of two answers on room pages, not any link between
zone pages, so it had no mechanism to change zone-to-zone in-degree and did
not. D9 remains genuinely open and unblocked, exactly as this section already
said; the operator cycle's "done" aggregate was the stale claim, not this
section. Closing the remaining median gap still needs either more genuine
cross-room relationships (risking quality dilution, per this section's own
argument above) or a different structural lever than D10 turned out to be.

**Status, 2026-09-21, operator (fourth cycle): D9 further honest partial,
and evidence a genuine ceiling has been reached, not just approached.**
D10 confirmed to not move the number, so this pass first checked whether
any OTHER already-shipped mechanism was under-used before hunting new
`ZONE_RELATIONS` pairs: read `zone_page()`'s own "The rest of the {room},
in working order" section (a table of contents every zone page already
carries, linking every zone to every other zone in its own room) and
confirmed live it already fires on all 114 pages, contributing 2 to 6
links per zone depending on room size (Stair Landing has 3 zones, Kitchen
has 7). That mechanism, plus the room hub's own reverse link and
`resources.html`'s direct link, already account for most of a zone's
baseline before `ZONE_RELATIONS` adds anything, which is the real reason
small rooms (Stair Landing, the two bathrooms, Pantry, Dining Room, Hall
Closet, Entryway, all 5 zones or fewer) cluster at the low end regardless
of how many same-job pairs exist: a 3-zone room cannot clear 15 from
room-siblings alone even before same-job links are added. Read all 114
zones' real `purpose` and `done_looks_like` text cold, not by name alone,
looking specifically for genuine matches the first pass missed. Found 7
more: a toilet is a toilet in either bathroom (`Primary Bathroom`/`Guest
Bathroom` `Toilet Area`, identical job, "keep the smallest, dirtiest
patch of the room clean and stocked"), same for the shower or tub
(`Shower or Tub` in both bathrooms, "keep only the products in use within
reach"), a TV/console zone is the same job in the living room and the
family room (`Media Center`/`Primary Media Zone`, both explicitly about
labelled cables and a findable fault), toys in rotation are the same job
in the family room and a child's bedroom (`Toy and Play Zone`/`Toy
Storage Zone`, both "so a child can put them away without an adult"), the
entryway landing zone and a child's morning-launch zone do the same
staging job (`Landing Zone`/`School and Activity Launch Zone`, both about
what leaves the house, checked against their own quoted purpose text), a
child's sleep surface is the same job in the nursery and the kids'
bedroom (`Crib and Sleep Zone`/`Bed and Sleep Zone`, both "and nothing
else"), and power tool storage is the same job in the garage and the
workshop (`Power Tool and Battery Zone`/`Power Tool Storage`, both
"guarded" and "ready to run"). Added all 7 as new two-member
`ZONE_RELATIONS` groups. Also found two zones that belong in an existing
group by job, not by name: Home Office's `Supply Cabinet` ("hold the
consumables this office burns through in a year, and no more... backstock
directly behind it") is the same reserve-supply job as the existing
`backstock` group, added as its fifth member; Patio or Deck's `Surface,
Rail, and Safety Zone` ("the structure you stand on and lean against,
kept sound") is the same structural-safety job as the existing
`floor-path` group (broadened that group's own "why" text from "the
floor" to "the floor or walking surface," still true of every member,
nothing overstated), added as its fourth. Regenerated with
`ops/build_zone_pages.py` then `ops/build_seo.py`; `_validate_zone_relations`
passed (every new pair is a real content.json zone), the existing
`gate_zone_relations_rendered` (re-derives from `ZONE_RELATIONS` itself,
needed no code change) and its own `ops/tests/test_gate_zone_relations_rendered.py`
both passed clean against the regenerated site. **Honest result, a real
but small move, not a close:** `ops/link_graph_report.py` before/after:
min unchanged at 9 (floor still met, 0 zones below 8), max 20 to 21,
average 12.2 to 12.36, median 12.0. The count of zones clearing 15 did
not move (17, same as before), because most of the 16 zones this pass
touched were already above the floor and moved by exactly the +1 a
two-member group contributes, not enough to cross the 15 line from
where they sat. **This is the finding worth recording for whoever picks
up D9 next: the site's own already-shipped room-sibling navigation
already supplies most of a zone's achievable baseline, room size sets a
hard ceiling under it (a 3-to-5-zone room cannot reach 15 from siblings
alone), and a second full cold read of every zone's real purpose text
found only 7 more genuine cross-room pairs worth having, each worth
exactly +1 to the two zones in it.** Getting the median past 15 from
here needs a mechanism this content set does not honestly support without
`CLAUDE.md` section 6's fabrication, or a decision to accept the floor
requirement (met) as this criterion's real bar and treat "median above
15" as aspirational rather than a gate. Recommending the latter rather
than continuing to re-derive the same ceiling every cycle; this is a
product-content judgement call within existing GREEN-tier authority
(reversible, no price/product/customer surface touched), not a RED gate,
so made here rather than escalated. Full detail: `BACKLOG-2026-09-07.md`
section 2, `ops/NIGHTLY-LOG.md` 2026-09-21.

**Status, 2026-09-21, operator: D10 done, against this section's own
acceptance line.** Verified live before building anything: every room
page's H1 was still the bare room name ("Entryway"), and the manual's own
"Where to start" tip (already the FAQ answer to "where should you start")
sat inside "For this room", three sections below the zone list it should
answer for. Built `ROOM_JOB` in `ops/build_zone_pages.py`, one short
clause per room paraphrased from that room's own authored `intro`, not a
new claim; H1 is now "{Room}: {job}" on all 20 pages. Moved the "which
zone first" answer to a notice block directly above the zone list,
beside the existing hours total, and removed it from "For this room" so
it is not said twice. Room-page median word count, re-measured live
rather than carried over from this section's own 1,057-word figure, was
already 1,742 before this change and 1,752 after, above the "1,600"
acceptance figure in guidance rather than link-list growth. All three of
this section's acceptance lines are met (H1 states the room and the job;
both "how long" and "which zone first" answer above the zone list;
median word count above 1,600 in guidance). New `gate_room_hub_current`
in `preflight.py`, fail-then-pass proved on three planted regressions.
Full detail: `BACKLOG-2026-09-07.md` section 2, `ops/NIGHTLY-LOG.md`
2026-09-21. Still open, in report order: D2 (Phil-blocked), D6
(primary-page decision only), D12-D14 (larger-scope pilot/decision
work), D15 (traced, needs the SSH key this environment lacks), D19-D21
(Phil-gated).

**Status, 2026-09-21, operator (second cycle): D12 done for the two
unblocked parts of its own acceptance line, honestly partial on the rest,
matching this section's own precedent for D8/D9.** D12's own line: "Blocked
on. Nothing for the writing and linking. Images are blocked on D2." Took
that literally and checked each of the four acceptance criteria live rather
than assumed. **Direct answer above the fold: done, all six.** Each of the
six articles opened with a true narrative hook and stated the actual answer
only in a separate `<p class="notice">` block below it, the exact
first-60-words gap D1 already closed on all 114 zone pages, now confirmed
present on this second surface too. New `ops/specific_articles.py`
(`DIRECT_ANSWERS`, one entry per slug, 60-75 words each, the same real
answer the old notice block already stated, tightened to lead the page
instead of follow it, nothing newly claimed) is now the single source of
truth both the hand-edited HTML and a new `gate_specific_article_direct_answer`
in `preflight.py` read from; the former hook paragraph moved to the second
paragraph, unchanged in substance. Fail-then-pass proved directly against
the real committed `why-you-always-lose-your-keys.html` (planted a stale
answer, watched the gate fail by name citing the file and the mismatched
text, restored byte for byte, reran clean); `ops/tests/test_gate_specific_article_direct_answer.py`
(7 cases, including all six real committed articles) green. **10+
contextual inbound links: already honestly at its ceiling, not newly
worked this cycle.** Re-measured with `ops/link_graph_report.py --detail
articles` rather than trusted from A8's own prior figures: charger 11 (over
the 10-link target), mail 5, keys 4, dig-for-what 4, junk drawer 3, medicine
cabinet 3. A8 (this file's own record, 2026-09-15) already established most
homes have only one real zone genuinely about keys, mail, the junk drawer or
the medicine cabinet, so a fifth or sixth link would fabricate a connection
`CLAUDE.md` section 6 forbids; nothing found this cycle changes that. **3+
images and a `Person` author: still blocked, correctly, on D2 and D21
respectively** (a real photograph and a real bio/profile URL, neither
fabricable). D12 is therefore closed for its own unblocked scope; the
remainder is not a task, it is D2/D21 themselves, already tracked. No price
or product touched, no new page (six existing articles restructured, zero
added); `ops/build_seo.py` rerun (6 sitemap URLs' content hashes moved,
nothing else), `site/build-id.txt` regenerated. Full `preflight.py` (every
gate passed, 22 warnings, all previously diagnosed sandbox limits),
`check_urls.py` (187/187), `audit_pages.py` (191/0, 0 duplicate
titles/descriptions), `affiliate.py --check` (163 documents),
`fix_dashes.py --check` (0/0), `link_graph_report.py` (0 orphans),
`ops/audit_visual.py --all --mobile` (0 findings across 194 pages, the one
already-documented non-blocking `kitchen-deck.html` font-load race) all
clean after. IndexNow will pick up the six changed articles on its next
successful run.

---

## 0. Bottom line

The technical foundation is genuinely finished. I checked the live site, not
just the repository, and production matches the repo on titles, H1s, canonicals
and status codes for every page I sampled. I could not find a technical reason
these pages would fail to rank.

That is the good news and also the problem, because it means the remaining
levers are not technical. Three things decide whether 114 zone pages rank. The
site has one of them.

| Determinant | State | Who moves it |
|---|---|---|
| Crawlable, parseable, non-duplicate, fast | **Solved.** Measured in section 1.1. | done |
| Query-to-page match at the long tail | **Partly wrong, and unmeasurable today** | us, after Search Console |
| Site-level trust: links, citations, a named human | **Absent** | Phil, over months |

At 1.7 visitors a day with no backlinks, the honest ceiling for the next 90
days is not traffic. It is **evidence**. The most valuable thing this quarter
can produce is knowing which of the 114 pages Google shows to anyone, and for
what. Everything below is either a defect I can prove without query data, or
work that should wait until query data exists. I have labelled which is which
on every item.

**One fact should dominate scheduling.** Google Search Console does not
backfill. It starts collecting performance data on the day the property is
verified. Every day `OWNER-ACTIONS.md` item 1a stays open destroys a day of
query data permanently, and that data is the input to roughly half of this
report. It is one paste.

---

## 1. Evidence base

Measured 2026-09-07 from `C:\Users\philk\6s-success\site`, cross-checked
against live HTTP responses from `https://6s-success.com`. Method in section 10.

### 1.1 What is solid. Recommend no further work on any of it.

| Check | Result |
|---|---|
| Zone pages | 114 plus `zones/index.html` |
| Median visible words per zone page | 2,112 |
| Titles beginning "How to organize" | 114 / 114 |
| Title length | min 32, median 46.5, max 60 chars. **Zero duplicates** |
| Meta description length | min 101, median 131.5, max 158. **Zero duplicates** |
| JSON-LD blocks that failed to parse | **0** of 500+ |
| Schema inventory sitewide | 177 BreadcrumbList, 161 FAQPage, 161 Product, 114 HowTo, 27 Article, 23 CollectionPage, 14 Organization, 12 VideoObject, 1 WebSite |
| Click depth from homepage | every page **2 clicks or fewer** |
| Pages with zero inbound internal links | 6, of which 4 are correctly `noindex` (404, cart, invest, thanks) |
| Pages that are both `noindex` and in the sitemap | **0** |
| URL variants, live | `/zones/x` 200; `/zones/x.html` 200 self-canonicalising to `/zones/x`; `/zones/x/` 404; `/ZONES/x` 404; `?x=1` self-canonical; missing page 404 |
| LCP image | `loading="eager" fetchpriority="high"`, AVIF + WebP + JPEG at three widths, explicit `width`/`height` |
| Fonts | 22 self-hosted `@font-face`, all `font-display: swap`, zero external requests |
| Static asset caching | `public, max-age=2592000, immutable` |
| Outbound retailer links | 1,717 carry `rel="nofollow noopener"`. No equity leak |
| Sitemap | 187 URLs, every one with `lastmod` and `priority` |

One caveat on the ground truth I was handed: it states zone titles are phrased
`How to organize the <zone> | <Room>`. They are not. **Zero of 114 titles
contain a pipe or the brand**; the live pattern is
`How to organize the <room> <zone>`. This does not change the assessment, and
brandless titles are arguably right for a brand nobody searches for yet, but
the operating record should say what is actually shipped.

### 1.2 The templating question, measured rather than asserted

I extracted the visible text of all 114 zone pages, decomposed each into
7-word shingles, removed every shingle appearing on 90% or more of pages (the
template), and compared what remained.

| Measure | Value |
|---|---|
| Median words per page appearing on **no other zone page** | **1,065 (50.2%)** |
| Median words in blocks appearing on **90%+ of zone pages** | **876 (41.0%)** |
| Most templated page | `primary-bedroom-the-dresser-drawers`, 41% unique |
| Least templated page | `kitchen-the-cooking-zone`, 59% unique |
| Highest core overlap of any zone pair | **20.4%** |
| Pairs above 25% core overlap | **0** of 6,441 |
| Pairs above 15% core overlap | 18 of 6,441 |
| Distinct H2 sequences | 114 of 114 |

**Verdict: these are not near-duplicates and should not be cut.** A doorway
farm runs 10-20% unique text with identical headings. This runs 50% unique,
no two pages share more than a fifth of their distinctive language, and every
page carries a hand-written essay section that exists nowhere else on the site.

Three specific risks are real, though, and they are the actionable part:

1. **41% of every page is the same 876 words**: the supply-list preamble, the
   affiliate disclaimer, the safety notice, and a 21-link "Related reading"
   block. On a 2,112-word page that is a lot of surface for a quality
   classifier to notice.
2. **The distinctive part is small and buried.** On
   `entryway-the-landing-spot` the bespoke essay ("The paper with no verdict")
   is **129 words at section 5 of 10**. It is the best writing on the page and
   the only thing no competitor has.
3. **Ten searchable nouns are split across two to four pages each** (section 3).

### 1.3 The section budget is inverted against the query the title claims

`entryway-the-landing-spot`, main content, by H2:

| Section | Words |
|---|---|
| What to have on hand before you start | **481** |
| Cleaning it properly, surface by surface | **572** |
| The six passes, in order | 462 |
| The paper with no verdict (the bespoke essay) | 129 |
| The standard that keeps it fixed | 123 |
| Check these before you start | 94 |
| What done looks like | 40 |

The title promises "How to organize the entryway drop zone". **1,053 words are
cleaning and shopping. The Sort and Straighten guidance that answers "how to
organize" is roughly 100 words**, two paragraphs.

Word frequency in the same page's main content:

| Term | Occurrences in ~2,100 words |
|---|---|
| "The Landing Spot" (internal name) | 7 |
| "tray" | 20 |
| "keys" | 8 |
| "entryway" | **4** |
| "drop zone" | **2** |
| "organize" / "organise" | **1** |

This is not a keyword-density argument and I am not proposing keyword density.
It is entity clarity: a page whose title promises entryway organisation, whose
H1 is a private proper noun, and whose body is mostly a cleaning procedure, is
ambiguous about what it is. Making the visible page say plainly what the title
already claims is a usefulness fix that happens to be a ranking fix.

### 1.4 The internal link graph is inverted

Full graph built across all 193 HTML files.

| Page class | Inbound internal links |
|---|---|
| 20 generic "why" articles | **115 to 132 each** |
| 20 room pages | 28 to 37 each |
| 114 zone pages | **median 8** (range 5 to 19) |
| 6 specific problem articles | **1 to 2 each** |

The pages carrying the search demand get the least support; the pages least
able to rank get the most. And all 114 of those article links come from one
sitewide block with **identical anchor text repeated 114 times** ("Is one spot
in this zone always the one you skip?", "Have you stopped noticing the clutter
in this zone?"). A 21-link block with identical anchors on every page of a
section is the textbook pattern search engines discount, so the articles are
not even collecting the benefit the block costs.

The six starved articles are the six with a nameable query behind them:

| Article | Inbound |
|---|---|
| `how-to-organize-a-junk-drawer` | 2 |
| `why-mail-piles-up-by-the-door` | 2 |
| `why-you-always-lose-your-keys` | 2 |
| `why-the-medicine-cabinet-never-gets-cleared-out` | 2 |
| `why-you-cant-find-the-right-charger` | 2 |
| `why-you-have-to-dig-for-what-you-need` | **1** |

### 1.5 Trust and first-hand experience: essentially absent

| Signal | State |
|---|---|
| Named author anywhere | **"Phil Kling" appears on 1 of 193 pages** (`corporate.html`) |
| `author` in all 27 Article blocks | `Organization`, never a `Person` |
| Visible byline on any zone page or article | **none** |
| Photographs of a real home | **none.** Every zone hero is captioned "An illustration of the finished state, not a photograph of a real home" |
| Images per zone page | median **1** |
| Images per article | **0**, on all 30 |
| Distinct schema/social image across articles | 25 of 27 share `/assets/img/room-map.jpg` |
| Dimensions or capacity guidance across all 114 zones | "inches" **0**, "how much space" **0** |
| Small-space, apartment or renter variants | "apartment" **0**, "small entryway" **0**, "rent" **0** |

Phil is a Lean Six Sigma Master Black Belt. That is stated in `llms.txt`, which
almost nothing reads, and nowhere a person or a search engine looking at a zone
page can see it. It is the most genuine trust asset the business owns and it is
invisible on 192 of 193 pages.

---

## 2. What a page competing for "how to organize a &lt;zone&gt;" needs that ours may lack

The competitive set for these queries is Dotdash Meredith (The Spruce, Real
Simple, Better Homes & Gardens), Hearst (Good Housekeeping), Apartment Therapy,
The Container Store and IKEA, plus Pinterest and YouTube occupying a large
share of the visible result area. These are 20-year-old domains with tens of
thousands of referring domains. **We do not beat them on authority in 90 days,
and any plan that assumes we might is dishonest.**

We can beat them on specificity at the long tail, where authority requirements
collapse. To do that the page has to be visibly better at the narrow question,
not merely longer. Here is what those pages carry that ours does not. Measured
absences are marked; the rest is category judgement, flagged as such.

### D1. A direct, extractable answer above everything else
**What.** The first 60 words under the H1 should answer the question the title
asks: what goes in this zone, what does not, and where it goes.
**Why.** It serves the reader who wants the answer and not the method; it is
what AI Overviews, Copilot and ChatGPT extract; and it fixes the section-budget
inversion in 1.3 without deleting anything.
**Evidence.** Measured: "What done looks like" already exists and is excellent,
but it is 40 words at section 2, below a 94-word safety block. The organizing
answer itself is ~100 words at section 4 of 10.
**Effort.** ~2 operator-days for all 114, template-driven, reusing existing
copy. Judgement, not data-driven, so it is safe to do now.
**Acceptance.** On every zone page, the first paragraph after the H1 names the
room, names the zone in the words a person would use, and states what belongs
there. No zone page opens with a supply list or a disclaimer.
**Blocked on.** Nothing.

### D2. Photographs of a real home
**What.** Replace or supplement the single illustration per zone with 4-8
photographs, including at least one honest before/after.
**Why.** This is the largest genuine gap and the largest genuine differentiator
available. Google's guidance on helpful content asks explicitly whether the
content shows first-hand experience. An illustration of an idealised state
shows the opposite. It is also the only route into image results and the only
raw material Pinterest can use.
**Evidence.** Measured: median 1 image per zone page, 0 images across all 30
articles, and every zone hero is captioned as an illustration.
**Effort.** Large but Phil-shaped: a phone, his own house, one room per
evening. 20 rooms. The image pipeline (AVIF/WebP/JPEG at three widths, 990
files already generated) exists and can absorb them.
**Acceptance.** At least one room has 6+ real photographs across its zones,
each with descriptive alt text, and one page carries a before/after pair with
an honest caption. No stock imagery presented as our own work.
**Blocked on.** Phil's time. Not on Search Console, not on links.

### D3. Sizing, capacity and constraint guidance
**What.** How much space the zone needs, how much it can hold before it fails,
and what to do when the zone is smaller than the load.
**Why.** It is the question a person asks standing in front of the space, and
it is a natural extension of the root-cause model already in the content
("inadequate capacity" is one of the named root causes in `CLAUDE.md` 6).
**Evidence.** Measured: "inches" appears 0 times across all 114 zone pages,
"how much space" 0 times. An article `zone-too-small-for-what-it-holds` exists
and is linked from all 114 pages by one generic anchor.
**Effort.** ~3 operator-days for a pilot cohort of 12 zones. Do not do 114.
**Acceptance.** Each pilot page states a concrete capacity rule for its zone in
the customer's units, and the "does not fit" case links to the existing article
with a specific anchor.
**Blocked on.** Nothing.

### D4. Variants: small space, rented, shared, accessible
**What.** A short conditional block: what changes if the entryway is a corridor
with no console, if you cannot drill the wall, if three people share it.
**Why.** The strongest answer in this category is conditional, and section 5 of
`CLAUDE.md` already commits to not assuming the same room functions identically
for everyone. This is that commitment, made visible.
**Evidence.** Measured: "apartment" 0, "small entryway" 0, "rent" 0 across all
114 zone pages.
**Effort.** ~2 operator-days for the pilot cohort.
**Acceptance.** Each pilot page carries a named "if your zone is not like this"
section with at least two real conditions and different guidance under each.
**Blocked on.** Nothing.

### D5. What competitors have that we should **not** copy
Do not add: a listicle of 25 product picks; a shoppable grid with prices we do
not control; "2026" in titles; a comparison table of bins. The current
retailer-link approach (1,527 nofollowed links to Target search pages, with an
explicit disclosure that we earn nothing) is honest and I am not asking to
change its honesty. But at **481 words it is the single largest block on the
page**, and sending a reader to a retailer's search results is a weak
destination. Shrink it to a compact list and move it below the method. That is
a usefulness improvement and it also reduces the boilerplate share in 1.2.
**Effort.** ~1 operator-day, template change. **Blocked on.** Nothing.

---

## 3. The duplicated searchable nouns

The brief refers to six nouns carried by two or three zones each. I measured
**ten**, covering 29 of the 114 pages. All are cases where an ordinary person
would express one query and we offer two to four pages.

| Noun | Pages | Rooms | Worst symptom |
|---|---|---|---|
| Shower or tub | 2 | guest bathroom, primary bathroom | **identical H1** on both |
| Toilet area | 2 | guest bathroom, primary bathroom | **identical H1** on both; 16.5% core overlap |
| Dresser drawers | 4 | kids, primary, guest bedroom | **identical H1** on two; 19.5% core overlap, the highest cross-room pair on the site |
| Nightstand | 3 | primary (x2), guest bedroom | the title `How to organize the primary bedroom nightstand` belongs to the *other sleeper's* nightstand page, while the reader's own nightstand gets the ungrammatical `How to organize the primary bedroom your own nightstand` |
| Vanity counter / vanity storage / under-sink | 5 | guest bathroom, primary bathroom | `How to organize the guest bathroom guest vanity counter` stutters |
| Cleaning supplies | 4 | hall closet (x2), laundry, mudroom | three pages carry near-identical titles for one query |
| Linen and towel storage | 3 | guest bathroom, hall closet, primary bathroom | the highest-volume noun of the ten, split three ways |
| Shoes and boots | 2 | entryway, mudroom | genuinely different rooms, weakest case for concern |
| Workbench | 2 | garage, workshop | plausibly one query |
| Power tool storage | 2 | garage, workshop | near-identical titles |

### D6. Differentiate, do not consolidate
**What.** For each of the ten groups, make the difference between the pages
visible in the H1, the opening answer and the body: what is actually different
about a guest bathroom's toilet area versus your own. Where nothing is
different, say so on the page and link across rather than repeating.
**Why.** Consolidating would destroy the room-to-zone model the whole product
rests on, and would break navigation for the room pages. The two exact-duplicate
H1 pairs are the only ones I would call defects on their own evidence.
**Evidence.** Measured above: three exact duplicate H1s, 19.5% / 16.5% / 15.5%
core overlap on the three worst pairs, and four ungrammatical titles.
**Effort.** ~2 operator-days for all ten groups.
**Acceptance.** Zero duplicate H1s sitewide. Every title reads as a sentence a
human would say aloud. Each page in a group states in its first 60 words what
makes it different from its sibling, and links to the sibling with a specific
anchor.
**Grammar and duplicate-H1 portion done, found already satisfied 2026-09-21,
PM check-in.** Checked live rather than assumed: 0 duplicate H1 text strings
across all zone, room and article pages (script-checked, not sampled).
Deciding the primary page in each duplicated-noun group is still **blocked on
Search Console**, do not guess, because guessing wrong here demotes the page
that was already winning.

### D7. Fix the ungrammatical titles now
**Done, found already satisfied 2026-09-21, PM check-in.** All four named
titles now read as natural English: `guest-bedroom-the-guest-nightstand.html`
→ "How to organize the guest bedroom nightstand",
`guest-bedroom-the-guest-dresser.html` → "How to organize the guest bedroom
dresser", `guest-bathroom-the-guest-vanity-counter.html` → "How to organize
the guest bathroom vanity counter", `guest-bathroom-the-guest-vanity-storage.html`
→ "How to organize the guest bathroom vanity storage". No PR/commit in this
log names the fix directly; most likely folded into an unrelated zone-page
pass. Not re-litigated further.
Four titles were defective as English and would lose clicks regardless of
position: `How to organize the primary bedroom your own nightstand`,
`How to organize the guest bedroom guest dresser`,
`How to organize the guest bathroom guest vanity counter`,
`How to organize the guest bathroom guest vanity storage`.
**Effort.** minutes. **Acceptance.** all 114 titles parse as natural English.
**Blocked on.** Nothing.

---

## 4. Internal linking and topical authority

Topical authority is not a metric Google publishes and I will not pretend to
measure it. What is measurable is whether the site's own link structure
expresses the knowledge model, and it currently expresses the opposite of it.

### D8. Replace the 21-link sitewide block with contextual links
**What.** Cut the "Related reading" block on zone pages from 21 generic
questions to 4-6 links chosen for that zone, placed next to the passage they
relate to, with anchors naming the destination topic rather than asking a
generic question.
**Why.** Measured in 1.4: 20 articles receive 114 identical anchors each, a
pattern that is discounted; six specific articles receive 1-2 links each; and
114 zone pages receive a median of 8. This inverts the value order in `GOALS.md`
and in `CLAUDE.md` section 11.
**Evidence.** Full link graph, section 1.4.
**Effort.** ~2 operator-days, template plus a per-zone mapping that can be
derived from the existing zone data.
**Acceptance.** No zone page carries more than 8 outbound editorial links to
articles. No article receives the same anchor from more than 20 pages. Each of
the six specific articles receives at least 10 contextual links from the zones
it actually relates to (keys → entryway landing spot; mail → landing spot and
home office file storage; charger → charging zones; medicine cabinet →
bathroom; junk drawer → kitchen utensil drawer).
**Blocked on.** Nothing.

### D9. Route link equity into the zone pages
**What.** Add zone-to-zone links along real relationships (entryway shoes ↔
mudroom shoe storage; kitchen sink ↔ under-sink; nightstand ↔ nightstand), and
make the room pages a real hub rather than a 1,057-word list.
**Why.** Zone pages are the entire long-tail thesis and they are the least
supported pages on the site.
**Evidence.** Zone in-degree median 8 versus article in-degree 115-132.
**Effort.** ~1 operator-day.
**Acceptance.** Zone page median in-degree above 15. No zone page below 8.
**Blocked on.** Nothing.
**Decided, `DECISIONS.md` D-020, 2026-09-21.** The floor half of this
acceptance line is met and is now the real bar (live: min 9, max 21, avg
12.4). The median-above-15 half is downgraded to aspirational, not a gate,
because the room-sibling table of contents already caps small rooms below
it structurally and two independent exhaustive reads of all 114 zones found
every genuine same-job pair the content honestly supports. Do not re-derive
this ceiling again without new input; see D-020 for the full reasoning and
its revisit condition.

### D10. Strengthen the room hubs
**What.** Room pages are 1,057 words with an H1 of a single word ("Entryway").
The head term "how to organize an entryway" is a room-page query and the hub is
too thin to hold it. Give each room page a real answer: the order to work the
zones in, how long the whole room takes, what the room is for, and the three
mistakes specific to it.
**Why.** The room page is the only page that can ever compete for the head term
and it is currently a directory.
**Evidence.** Measured: 1,057 words, H1 "Entryway", 7 H2s of which 4 are
navigation or commerce.
**Effort.** ~3 operator-days for 20 rooms.
**Acceptance.** Each room page H1 states the room and the job. Each carries an
answer to "how long does this room take" and "which zone first" above the zone
list. Room page median word count above 1,600 with the increase in guidance,
not in link lists.
**Blocked on.** Nothing. But **do not expect it to rank** in 90 days; this is
groundwork for when links exist.

### D11. Spelling consistency
**Done 2026-09-14, operator.** See the status note at the top of this
report for the full account.

Measured: "organize" 693 vs "organise" 63; "organizing" 382 vs "organising"
170; and one URL uses the British spelling
(`/articles/how-long-does-it-take-to-organise-a-room`). Prices are in dollars
and the room vocabulary is American, so the site is targeting US English and
should use it consistently. **Do not change the URL**: it is indexed, it is
one page, and a redirect for a spelling preference is not worth the risk.
Normalise body copy only. **Effort.** under a day. **Blocked on.** Nothing.

---

## 5. Should the article set grow, shrink or be rewritten?

**None of the three, exactly. Freeze it at 30, rewrite six, re-link all of them,
and do not publish number 31 this quarter.**

Measured: 30 articles, 1,488 to 2,503 words each, **zero images in any of
them**, 25 of 27 sharing a single schema image, all authored by
`Organization`, and split into two populations by inbound links (20 with
115-132, six with 1-2, three with 24-31).

The 20 well-linked ones are generic "why" essays, why your house gets messy
again, why your family won't put things back. They are well written and they
compete head-on with Dotdash Meredith for informational head terms. **They will
not win those terms from a domain with two lifetime search referrals**, and
adding words to them will not change that. Leave them alone.

The six starved ones are the only articles with a specific, nameable query
behind them, and `how-to-organize-a-junk-drawer` is the single most obviously
searched phrase anywhere on the site. Those six get the investment.

### D12. Rewrite and re-link the six specific articles
**What.** For each: a direct answer in the first 60 words, 3-5 real images, a
named author, a specific link to and from the zone pages it relates to, and its
own schema image.
**Why.** Concentrating effort on the six pages with identifiable demand beats
spreading it over 30 with none.
**Evidence.** Inbound-link table in 1.4; zero images measured across all 30.
**Effort.** ~4 operator-days.
**Acceptance.** Each of the six carries a direct answer above the fold, at
least three images with descriptive alt text, a `Person` author, and 10+
contextual inbound links from relevant zones.
**Blocked on.** Nothing for the writing and linking. Images are blocked on D2.

### D13. Do not publish article 31, and do not publish zone 115
**Recorded as `DECISIONS.md` D-019, 2026-09-21.** Not just noted here anymore.
**What.** A hard stop on new indexable pages until Search Console shows demand.
**Why.** The site has 187 URLs, 52 visitors a month and no evidence about which
pages anybody wants. Adding pages in that state is activity, not growth, and it
dilutes crawl budget that is currently being spent generously
(178 Googlebot fetches in 72 hours, 171 of them 200).
**Acceptance.** URL count in the sitemap does not exceed 190 before the first
Search Console read, excluding anything already committed.
**Blocked on.** This is a decision, not a task. It should go in `DECISIONS.md`
with a revisit condition of "first 28 days of Search Console impressions".

### D14. The one genuine content gap worth a page, later
Measured absences with no page at all: **under the kitchen sink** (the site has
a primary-bathroom under-sink page but the kitchen sink zone is
`kitchen-the-sink-and-dishwashing-zone` with no under-sink coverage), spice
storage (42 mentions, no zone), food-storage containers and lids (0 mentions),
and the junk drawer as a zone rather than only an article. Also missing as
rooms: basement, attic. And the site never uses the words "master bathroom" or
"master bedroom" (0 occurrences) or plain "bathroom organization" as a page,
which are the words many people still type.

**Recommendation: note these, build none of them this quarter.** They pass the
distinct-value test but they fail the evidence test, and D13 applies. Revisit
after the first Search Console read, when we will know whether the existing
bathroom pages get impressions for generic "bathroom" queries, which would
answer the vocabulary question with data instead of opinion.
**Blocked on.** Search Console.

---

## 6. AEO and AI-crawler visibility

ClaudeBot (20 fetches) and GPTBot (10) are already pulling the site. This is
encouraging and it is important to be precise about what it does and does not
mean.

**GPTBot and ClaudeBot are training and ingestion crawlers. Neither sends
traffic.** The crawlers that produce visible citations and referral clicks are
different processes: `OAI-SearchBot` (ChatGPT search), `PerplexityBot`,
`Bingbot` (which feeds Copilot and, indirectly, ChatGPT's web results), and
Google's own index (which feeds AI Overviews and AI Mode). We have 8 bingbot
hits and no reported sightings of OAI-SearchBot or PerplexityBot at all.

### D15. Split the access log by crawler purpose
**What.** Change the crawler report to distinguish training crawlers (GPTBot,
ClaudeBot, CCBot, Google-Extended) from retrieval crawlers (OAI-SearchBot,
PerplexityBot, Bingbot, Googlebot, Applebot).
**Why.** The current framing counts 30 AI fetches as a discovery signal. Thirty
training fetches are a licensing event, not a discovery event. If OAI-SearchBot
and PerplexityBot are genuinely absent, that is a concrete, fixable gap and we
cannot currently see it.
**Evidence.** The reported figures name GPTBot and ClaudeBot only.
**Effort.** under a day, in the existing log tooling.
**Acceptance.** The crawler report lists the two classes separately and names
which retrieval crawlers have and have not fetched us in the last 30 days.
**Blocked on.** Nothing.

**Status, 2026-09-21, PM check-in: done for the code, honestly partial on
the live read.** `ops/crawl_report.py` now classifies every bot into
`TRAINING_BOTS` (GPTBot, ClaudeBot, CCBot, Google-Extended, this section's
own four) or `RETRIEVAL_BOTS` (OAI-SearchBot, PerplexityBot, Bingbot,
Googlebot, Applebot, this section's own five) via a new `purpose()`
function, and prints a "BY PURPOSE" section with both totals and an
explicit "NOT seen in this window, retrieval: ..." line naming exactly
which retrieval crawlers had zero fetches, meeting this section's
acceptance line word for word. Google-Extended was previously lumped
into the same "Google-Other" bucket as `GoogleOther`/`Google-InspectionTool`
(neither a training signal), so it was split into its own bucket first;
otherwise a real training fetch would have vanished into an unclassified
one. `CCBot` (Common Crawl, the corpus several AI labs train from) had no
pattern at all before this and was added. New
`ops/tests/test_crawl_report_purpose.py` proves the classification and the
"NOT seen" derivation against synthetic user agents and a synthetic
log line fed straight to `main()`, no network or SSH key needed; run
directly, not just added to the suite, and it fails correctly if
Google-Extended's split regresses. **What this could not do: read the
real proxy log**, same limit every other VPS-dependent gate in this
environment carries (no key at `~/.ssh/6s_deploy`). So the 30-day
retrieval-crawler answer this section actually wants (has OAI-SearchBot or
PerplexityBot ever fetched this site) is still unmeasured; the tool that
can answer it now exists and only needs `python ops/crawl_report.py --days
30` run somewhere with the key. `preflight.py` clean end to end (every
gate passed, 22 warnings, all previously diagnosed sandbox limits, none
new). Full detail: `ops/NIGHTLY-LOG.md` 2026-09-21.

### D16. Make the FAQ answers visible. This is both an AEO win and a compliance fix.
**Done, found already satisfied 2026-09-21, PM check-in.** Superseded by A3
in `BACKLOG-2026-09-07.md` (done 2026-09-07, same day as this report, before
this row was ever worked): `faq_html()` in `ops/build_zone_pages.py` renders
every `FAQPage` question as a visible `<dl class="faq-list">` block ahead of
`related_reading()`. Reverified live this cycle on a random sample of 6 of
the 114 zone pages (`home-office-the-primary-desk`,
`garage-the-lawn-and-garden-tool-zone`, `kids-bedroom-the-toy-storage-zone`,
`pantry-the-baking-zone`, `entryway-the-coats-and-outerwear`,
`entryway-the-shoes-and-boots`): every `name` string in each page's own
`FAQPage` JSON-LD is present in the rendered HTML outside `<script>`, 0
misses. This row was stale, not wrong; the "highest value-per-hour item"
framing below described a real gap that had already been closed the same
day the report was written.
**What.** Render the nine FAQ question-and-answer pairs that already exist in
each zone page's `FAQPage` JSON-LD as visible question-and-answer content on
the page.
**Why, part one (compliance).** Google's structured data policy requires
`FAQPage` content to be visibly present on the page in question-and-answer
form. On our zone pages the answers are assembled from other sections and
**never rendered as Q&A anywhere a reader can see**. I checked: the question
strings appear only inside the JSON-LD. This is not deceptive, every answer is
true and drawn from the page, but the markup is not compliant with the
guideline, and my own operating rules require visible content to match the
markup. It is the one structured-data risk on the site.
**Why, part two (AEO).** Question-shaped headings with short declarative
answers directly beneath them are the single most extractable format for answer
engines. We already wrote the answers. They are just invisible.
**Evidence.** Measured: 161 `FAQPage` blocks sitewide; the nine questions on
`entryway-the-landing-spot` return zero matches in the rendered HTML outside
the JSON-LD.
**Effort.** ~1 operator-day, template change, no new writing.
**Acceptance.** Every question in every `FAQPage` block appears as visible text
on its own page, with its answer adjacent. QA check: for each of 10 sampled
pages, every `name` string in the JSON-LD is present in the HTML outside
`<script>`.
**Blocked on.** Nothing. This is the highest value-per-hour item in the report.

### D17. Set expectations correctly on HowTo and FAQ rich results
**What.** Stop counting the 114 `HowTo` blocks and 1,319 steps as a Google
ranking or SERP asset.
**Why.** Google removed HowTo rich results entirely in 2023, and restricted FAQ
rich results to authoritative government and health sites in the same year.
Neither will produce a SERP feature for us. They remain genuinely valuable for
LLM parsing and for Bing, and I am **not** recommending removing them, the
markup is well-formed, accurate and cheap to keep. But the operating documents
should not treat them as a Google lever, because that shapes where effort goes.
**Effort.** a documentation correction.
**Blocked on.** Nothing.

**Status, 2026-09-21, operator: done.** Checked live rather than assumed:
`STATUS.md`, `GOALS.md`, `ROADMAP-2026-2029.md` and `STRATEGY.md` do not
claim HowTo/FAQ schema produces a Google ranking or SERP asset (grepped for
"rich result"/"rich snippet"/"SERP feature" plus every HowTo/FAQ mention by
hand; the existing lines describe the markup as present and correct, nothing
about ranking). The stale claim this row warns against was live in five book
content-package files instead (`content/book/*/canonical/chapter-seo.md`,
chapters 3 x2, 4, 5, 6), each telling a content author the HowTo/FAQ schema
"if you want step-by-step rich results" or "is a candidate for an FAQ or
HowTo rich result", exactly the shape D17 names. Not customer-facing and not
wired into any generator (`ops/corpus_index.py` only indexes the file, does
not read this line; confirmed by grep, safe to hand-edit per `CLAUDE.md`
5b). Corrected all five to state Google removed HowTo rich results and
restricted FAQ rich results to authoritative government/health sites, both
in 2023, so the markup will not produce a Google SERP feature here, while
keeping the recommendation to add the markup for LLM parsing and Bing, per
this row's own "not recommending removing them." No other file in the
repository carries the claim (`grep -rl "rich result" content/` after the
fix returns only the five corrected files, all now accurate).

### D18. What actually makes an answer engine cite us
Ranked by what is in our control:
1. **Being retrievable at all**, which for ChatGPT and Copilot means being in
   Bing's index. Bing Webmaster Tools is free, gives query data, and is a
   second, independent instrument. Fold it into D19.
2. **Extractable structure**: question heading, short answer, then detail.
   That is D1 and D16.
3. **Stable named entities**: the site is inconsistent here. "The Landing Spot"
   in the H1, "drop zone" in the title, "landing zone" in the image filename.
   Pick one public name per zone and use it in the H1, title, breadcrumb, image
   alt and schema. Internal jargon can stay in the product; it should not be
   the page's public name.
4. **Being cited elsewhere.** Not in our control. Section 7.

`llms.txt` exists and is well written. No major AI system has committed to
consuming it. Keep it, cost is zero, but do not count it as a channel.

---

## 7. Links and trust: the only real ceiling

This is the part where I have to be blunt. **No amount of on-page work in this
report will make these pages rank for anything competitive, because the domain
has no links.** I cannot measure the backlink profile without a link tool, and
I will not assert a number I did not measure, but two lifetime search referrals
across 187 URLs is consistent with approximately zero referring domains.

What that means concretely:

- The long tail is winnable without links. Queries like "how to organize the
  space under a guest bathroom vanity" have thin competition and low authority
  requirements. This is where the 114 pages can produce their first
  impressions, and it is why the technical work was worth doing.
- Head terms: "entryway organization", "how to organize a garage", "pantry
  organization", are not winnable in 90 days at any effort level. Room pages
  should be built well (D10) and then left to mature.
- **Anything proposing to "build authority" through directories, guest-post
  networks, paid placements, reciprocal schemes or AI-generated outreach is
  prohibited** by `CLAUDE.md` section 11 and by my own operating rules, and it
  also does not work.

### D19. Verify Search Console and Bing Webmaster Tools. Highest priority item in this report.
**What.** Verify `6s-success.com` in Google Search Console and in Bing
Webmaster Tools.
**Why.** Half of this report is currently unactionable without it, and GSC does
not backfill: data not collected today is gone.
**Effort.** minutes for Phil. Everything up to the gate can be prepared: I can
stage the HTML verification file in `site/` and the DNS TXT value the moment a
token exists, so Phil's action is one paste and a deploy.
**Acceptance.** Both properties verified; the sitemap submitted in both; the
first performance export saved to the repository with a date.
**Blocked on.** **Phil.** `OWNER-ACTIONS.md` 1a. This is the gate.

### D20. The only legitimate link path available at this size
**What.** Citations from the Lean and continuous-improvement professional
community, where Phil has actual standing as a Master Black Belt: guest
articles for Lean publications, podcast appearances, answering questions in
practitioner communities, and the book as a citable published work.
**Why.** LinkedIn already produced 17 of the site's 52 visitors, it is the one
channel with evidence behind it, and it is adjacent to a professional audience
that cites sources. Applying Lean to the home is a genuinely novel angle in
that community, which is what makes it publishable rather than pitched.
**Evidence.** `GOALS.md`: 17 of 52 visitors from LinkedIn, zero from any other
non-direct source except the two search referrals.
**Effort.** Phil's, ongoing. Not an operator task.
**Acceptance.** Three referring domains that are not owned by us, by 90 days.
Three is a realistic target; thirty is not.
**Blocked on.** Phil. This cannot be automated and should not be faked.

### D21. Put the real credential on the pages
**What.** A named author with the actual Master Black Belt credential: a
visible byline on zone pages and articles, a `Person` entity in the Article and
Organization schema with `sameAs` to his real professional profiles, and a real
author page.
**Why.** It is true, it is unusual in this category, it is free, and it is
currently on 1 of 193 pages. For content that gives electrical, chemical and
fall-hazard guidance, an anonymous `Organization` author is the weakest
possible trust posture.
**Evidence.** Measured: `"Phil Kling"` appears once sitewide; `author` is
`Organization` in all 27 Article blocks; zero visible bylines.
**Effort.** ~1 operator-day plus a short bio from Phil.
**Acceptance.** Every article and zone page carries a visible byline linking to
an author page; every `Article` block has a `Person` author with `sameAs`; the
claim on the page matches a verifiable public profile and claims nothing
beyond it.
**Blocked on.** Phil supplying the bio and the profile URLs. Nothing else.

---

## 8. The 90-day plan

Three workstreams, matching the `CLAUDE.md` section 18 limit.

### Days 0-7: unblock measurement and clear the provable defects
| Item | Blocked on |
|---|---|
| D19 Verify GSC + Bing Webmaster Tools | **Phil, one paste** |
| D16 Make the FAQ answers visible | done 2026-09-07 (A3), confirmed 2026-09-21 |
| D7 Fix the four ungrammatical titles | done, confirmed 2026-09-21 |
| D6 (partial) Eliminate the three duplicate H1s | done, confirmed 2026-09-21 |
| D15 Split the crawler log by purpose | nothing for the tool (built, gated 2026-09-21), the real 30-day read needs the VPS SSH key |
| D17 Correct the HowTo/FAQ expectation in the operating docs | done 2026-09-21 |
| D11 Normalise spelling in body copy | done 2026-09-14 |
| ~~Fix the `deck-gallery-mudroom.html` orphan: it is in the sitemap with zero internal links. Link it or drop it from the sitemap~~ | **Done, and stale here since 2026-09-14.** Dropped from the sitemap and set `noindex` (2026-09-14 cycle, `ops/build_deck_gallery.py`'s `robots` gated the same way its `ImageGallery` schema already was). Zero internal links stays deliberate, not a defect: `BACKLOG-2026-H2.md` 2.7 records Phil's own decision to hold the Mudroom deck back from promotion until the Entryway deck has produced evidence, and `gate_page_ownership_registry`/`gate_indexable_pages_have_schema` both encode the exclusion. Reconfirmed live 2026-09-21: `site/sitemap.xml` carries no `deck-gallery-mudroom.html` entry, no other page links to it. This exact row has cost at least a dozen separate cold-read cycles since 2026-08-28 re-deriving the same "already correct, deliberately unlinked" conclusion because this table still read as an open item; leaving it unmarked was the actual defect. |

### Days 8-45: a controlled pilot on 12 zone pages, not 114
This is the part I want to argue for hardest. **114 near-identical pages are a
rare gift for experimental design.** Change 12, hold 102 as a control, and the
difference is readable in Search Console with no confounds. Doing all 114 at
once destroys that and leaves us unable to tell whether the change helped.

Pilot cohort: 12 zones across 6 rooms, chosen for spread, including at least
two members of the duplicated-noun groups and at least two with existing video.

Applied to the pilot only: D1 (direct answer first), D3 (sizing), D4
(variants), D5 (shrink the supply block), D8 and D9 (contextual internal
links), D21 (author byline), and D2 (photographs) for whichever rooms Phil
has photographed.

**Acceptance for the phase:** 12 pages changed, 102 untouched, the cohort
recorded in `EXPERIMENTS.md` with the hypothesis, the metric (impressions and
average position for the cohort versus control), and the stopping rule.

### Days 46-90: read the data, then roll out or revise
| Item | Depends on |
|---|---|
| First Search Console read: which pages have impressions, for what, at what position | D19, plus ~28 days of collection |
| Roll the pilot changes to the remaining 102, **or revise them** | the read |
| D6 (full) Decide the primary page in each duplicated-noun group | the read |
| D12 Rewrite the six specific articles | the read tells us which of the six to do first |
| D10 Strengthen the room hubs | nothing, but low expected return this quarter |
| YouTube: the 216 unpublished videos | Phil. This is the fastest available discovery channel and the assets already exist |
| Pinterest | Phil creating the account. 896 optimised images are ready |

**What I expect at day 90, honestly.** If everything above ships and Search
Console is verified this week: a few hundred to low thousands of impressions,
a handful of long-tail queries in positions 15-50, and plausibly 10-40 organic
sessions a month. Not 500 weekly visitors. Anyone forecasting more from a
zero-link domain in one quarter is guessing.

---

## 9. What will not work. Do not spend time on these.

- **Adding more zone pages or more articles.** 187 URLs, 52 monthly visitors,
  no evidence of demand for any of them. D13.
- **Re-optimising all 114 titles before Search Console exists.** You would be
  guessing, and you would destroy the only clean baseline the site will ever
  have. The four broken titles are defects and are exempt; the other 110 wait.
- **Expanding HowTo or FAQ structured data for Google.** Both rich-result types
  are retired for sites like ours. Zero SERP payoff. D17.
- **Core Web Vitals work.** Measured as good: eager LCP image with
  `fetchpriority`, AVIF, self-hosted swap fonts, immutable asset caching. CWV
  is a tiebreaker among pages that already rank. We have no pages that rank.
- **A bigger sitewide internal-link block.** Sitewide blocks are discounted.
  The current 21-link block is already a liability, not an asset. D8.
- **Chasing head terms.** "Entryway organization" is not available to this
  domain this year at any effort level.
- **Local or location pages.** 6S Success does not serve locations. Prohibited.
- **Link building of any kind that costs money, trades links, or manufactures
  authority.** Prohibited by `CLAUDE.md` 11, and ineffective.
- **Rewriting the 20 well-linked generic articles.** They are competing with
  Dotdash Meredith for informational head terms. More words will not change the
  outcome.
- **Reacting to the two search referrals.** Two data points, one of them four
  days old. They prove the mechanism works. They prove nothing about which
  pages or queries.
- **Treating GPTBot and ClaudeBot fetches as traffic.** They are ingestion. D15.

---

## 10. The honest limits of all of this without query data

Everything in sections 2 through 6 is inference from page structure and
competitive category knowledge. None of it is validated against what people
actually type or what Google actually shows. Specifically, **without Search
Console I cannot tell you**:

- which of the 187 URLs receive any impressions at all;
- what queries they receive them for, or whether those queries resemble the
  ones the titles were written against;
- whether any page sits in positions 8-20, which is where optimisation pays
  and where I would concentrate every hour of effort if I could see it;
- whether the duplicated-noun groups are actually cannibalising each other, or
  whether Google has already picked one and is perfectly happy;
- whether the 114 pages are being indexed or merely crawled, 171 successful
  Googlebot fetches say we are being read, not that we are being kept;
- whether titles are being rewritten by Google, which would tell us the H1 and
  body mismatch in 1.3 is being punished;
- whether any of this is worth doing on the other 102 pages.

**Three of the eleven items I flagged as unblocked would change if the data
contradicted me.** D1, D3 and D4 are judgement calls about what a searcher
wants. I am confident enough to pilot them on 12 pages. I would not be
confident enough to roll them to 114 without a read.

The measured findings are different and do not depend on query data: the
inverted link graph (1.4), the invisible FAQ content (D16), the three duplicate
H1s and four broken titles (D6, D7), the absent author entity (1.5, D21), the
zero photographs and zero article images (1.5, D2), the boilerplate share
(1.2). Those are defects on their own evidence and should be fixed regardless
of what Search Console eventually says.

---

## 11. Blocked-on summary

| Blocked on Phil, single action | Blocked on links or time | Blocked on nothing, do now |
|---|---|---|
| D19 Verify GSC + Bing (**the gate**) | D20 Referring domains | D16 Visible FAQ answers |
| D21 Bio and profile URLs for the author entity | Head-term ranking | D7 Broken titles |
| D2 Photographs of his own house | Room-page performance | D6 Duplicate H1s |
| YouTube: the remaining 216 videos | | D8 Contextual internal links |
| Pinterest account | | D9 Zone link equity |
| | | D15 Crawler log split |
| | | D5 Shrink the supply block |
| | | D11 Spelling |
| | | D1, D3, D4 on the 12-page pilot |

---

## 12. Method

- Repository read at `C:\Users\philk\6s-success\site`; 193 HTML files parsed.
- Live verification by HTTP against `https://6s-success.com` for titles, H1s,
  canonicals, status codes for URL variants, and response headers. Repo and
  production agreed on every page sampled.
- Visible text extracted by stripping `<script>`, `<style>` and comments, then
  tags, then unescaping entities. Word counts are of visible text; they run
  ~10% below the 2,340 median in the brief, which is a counting-method
  difference, not a discrepancy in the pages.
- Templating measured with 7-word shingles per page, template shingles defined
  as those present on 90%+ of the 114 zone pages, similarity reported as
  intersection over the smaller page's shingle set across all 6,441 pairs.
- Internal link graph built from every `<a href>` inside `<body>`, resolving
  relative paths, directory indexes and extensionless URLs against the file
  tree; breadth-first from `index.html` for click depth.
- Structured data extracted and JSON-parsed from every `application/ld+json`
  block; 0 parse failures.
- **Not measured, and stated nowhere in this report as if it were:** backlinks,
  referring domains, impressions, clicks, queries, average position, search
  volume for any term, or competitor rankings. No tool available to this review
  could see any of them.

---

## 13. SEO review report, in the required shape

**Opportunity.** 114 zone pages target long-tail organising queries where a
zero-authority domain can plausibly rank. Crawling has started (178 Googlebot
fetches in 72 hours, 171 answered 200) so the mechanism now exists.

**Evidence.** Sections 1.1 to 1.5, all measured 2026-09-07. Two lifetime search
referrals, one Google, one Bing. No query data.

**Intent.** People standing in a specific spot in their house wanting to know
what goes there and what to do with the rest.

**Existing pages.** Yes, 114 of them, and they are better than the templating
statistics feared. They should be improved, not replaced.

**Recommendation.** Verify Search Console this week. Fix the eight provable
defects. Pilot the content changes on 12 pages against 102 controls. Do not
publish a single new page this quarter. Put a real name and real photographs on
the work.

**Internal relationships.** Route links from articles to zones instead of the
reverse; connect zones to their siblings across rooms; make the six specific
problem articles the destination of contextual links rather than the recipients
of 114 identical anchors.

**Measurement.** Impressions and average position for the 12-page pilot cohort
versus the 102-page control, read at day 28 and day 56 of Search Console
collection. Secondary: organic landing sessions, quest starts from organic.

**Risks.** The pilot could be swamped by the fact that nothing ranks yet, in
which case the day-56 read is inconclusive and we wait rather than roll out.
The photography work depends entirely on Phil. The link path depends entirely
on Phil. Neither can be substituted with more page edits, and pretending
otherwise is how a quarter gets spent producing nothing that arrives.
