# 6S Success Current Operating Status

> Living operational state for Claude Code and all 6S Success autonomous agents.

## Document Role

`STATUS.md` is the fastest authoritative summary of **what is happening now**.

It is not a strategy document, backlog, changelog, incident archive, or analytics database.

Every agent performing meaningful autonomous work should read this file after `CLAUDE.md` and `AUTONOMY.md`.

Update this file whenever the material operating state changes.

---

# 1. Status Metadata

**Last Updated:** 2026-09-12  
**Updated By:** Claude, scheduled operator cycle. Unshallowed a shallow, detached checkout and fast-forwarded cleanly onto `origin/main`. Read `GOALS.md`, `BACKLOG-2026-09-07.md` (full), `ROADMAP-2026-2029.md`, `CLAUDE.md`, recent `ops/NIGHTLY-LOG.md` entries. `preflight.py` fresh: every gate passed, 22 warnings, all previously diagnosed. 8 GitHub issues confirmed unchanged (all decision-labelled or blocked-on-art, none pickable). `BACKLOG-2026-09-07.md` sections 2-6 again all done or Phil-gated, so worked a cold read of the lowest-mention `ops/*.py` file and found a real, live bug: `ops/social_drafts.py` and its sibling `ops/linkedin_drafts.py` (the real daily `--send` email Phil actually reads) both reported a static "N usable posts remain" figure that never decreased as posts were actually served, proved by replaying multiple simulated days. Fixed both to subtract the rotation's served set; new tests in `test_social_drafts.py`/`test_linkedin_drafts.py` fail-then-pass proved against the pre-fix code. Full `preflight.py`, all 117 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. `inbox_agent.py --apply` unchecked (no mail credential), not empty.

**Found and fixed:** per step 5d, cold-read the required governance docs a recent PM check-in had flagged as 19-26 days untouched (`CLAUDE.md` section 56) but never individually checked for content, only for date. `BUSINESS.md` and `EXPERIMENTS.md` are policy/framework text with no factual claim to go stale, matching `CONTENT-CATALOG.md`'s own recent verdict, left alone. `DATA-SOURCES.md` was genuinely wrong: its Section 5 registry and Section 116 "Current Source State" had said every source, GitHub included, was UNVERIFIED since the file's 2026-08-17 creation, never updated even though GitHub is used every cycle via the API and `GOALS.md` O1 records real traffic figures read directly from the production Umami database on three separate dates. Corrected both sections with per-source status and citations, not a blanket flip: several rows honestly stay UNVERIFIED or DISCONNECTED (Search Console, host-level monitoring, application logs, a separate product database that does not appear to exist). New `gate_data_sources_current` in `ops/preflight.py`, deliberately narrow to what is citable (GitHub, Analytics, and the original bootstrap sentence), `ops/tests/test_gate_data_sources_current.py` (6 cases), fail-then-pass proved directly against the real pre-fix file via `git stash`.

**Verified:** full `preflight.py` clean after (every gate passed, 23 warnings unchanged), 115 of 116 `ops/tests/test_*.py` files individually (0 failures; `test_generator_ownership.py` needs live egress this sandbox lacks, independently confirmed clean via `preflight.py --own`), `check_urls.py` (188/188), `audit_pages.py` (191/0, 0 duplicate titles/descriptions), `affiliate.py --check` (162 documents), mobile `npm test` (`mobile/quest-app`, 4 suites) all clean. No price or product touched, no site page changed, IndexNow not applicable (no page added or rewritten).

**Prior pass, for continuity:** Backfilled `CHANGELOG.md`'s 26-day silence with 13 real `CHG-2026-000N` entries, each citing a real commit and, where one exists, the gate that verifies it; new `gate_changelog_current` (warning-only, 21-day age threshold), `ops/tests/test_gate_changelog_current.py` (6 cases) fail-then-pass proved. Full `preflight.py` clean (23 warnings), all 116 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price or product touched, no site page changed, IndexNow not applicable.

**Prior pass, for continuity:** Previous work finished and independently verified rather than trusted: reread `ops/checkin.py`'s diff directly (line 250 now reads `persisted.get("products_live") is not None and persisted["products_live"] < 159`, matching the commit's own claim) and confirmed `preflight.py`'s `gate_tests()` already exercises the new `ops/tests/test_checkin.py` (15 cases) as part of the clean run below, rather than citing the commit message on trust. Six commits had landed here since this file's own last account (a `check_integrations.py` fix, three PM check-ins, a `STRIPE.md` reconciliation, and the `checkin.py` fix itself); none were defects, only this file's own currency needed correcting. `preflight.py` fresh: every gate passed, 23 warnings, all previously diagnosed. 8 GitHub issues unchanged via the API, all decision-labelled or blocked-on-art, none pickable. `BACKLOG-2026-09-07.md` sections 2-6 again all done or Phil-gated. Working tree clean, `main` up to date with `origin/main`. No new unblocked backlog item surfaced; no defect found this pass.

**Prior pass, for continuity:** Every unblocked `BACKLOG-2026-09-07.md` row again done or Phil-gated, the standing zero-mention doc handoff already closed, 8 GitHub issues unchanged (all decision/blocked-on-art), no mail credential, so cold-read a genuinely low-mention `ops/*.py` file per step 5d: `ops/check_integrations.py`. Found a real defect: its beacon (`/stats/api/send`) and mailing-list (`/subscribe`) checks folded a `fetch()` network failure (no answer at all) into the same `False` used for a real wrong answer, so one flaky hop on either path while the site was otherwise reachable printed "BROKEN, an integration answers but is not the service it should be" on evidence that only supported "could not be reached," the exact unknown-reported-as-failing shape CLAUDE.md 0.4 names. The site-id check already handled this correctly (`ok=None`); widened the other two to match. New `ops/tests/test_check_integrations.py` (5 cases), fail-then-pass proved directly (`git stash` on the fix alone, old code failed 5 of 5, reverted, new code passes 5 of 5); a genuine wrong answer (not a fetch failure) still correctly fails, proving the fix does not blunt real defects into unknown. Full `preflight.py` (every gate passed, 23 warnings, all previously diagnosed), all 113 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No egress to the live site from this sandbox, confirmed directly. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity:** Cold-read `ops/build_youtube_metadata.py` and found one real zone named three different ways across its YouTube title, its own page's SEO title and its own H1; fixed by pointing the metadata generator at `build_zone_pages.py`'s real naming functions. Regenerating surfaced a second defect: 113 of 114 zone pages' own HowTo JSON-LD read "How to reset the The Landing Spot" (a doubled article), fixed with a one-line conditional. New `gate_zone_name_consistency`. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity:** Found, by opening the actual rendered picture rather than trusting its recorded verdict, that `kitchen--primary-prep-counter`'s approved zone hero shows a counter covered in bowls, produce and flowers, directly contradicting its own done_looks_like ("holding only the board, the knife block or strip, and the salt... no fruit bowl") under a caption calling it "an illustration of the finished state." Withdrew the verdict. That alone did nothing: `ops/wire_zone_heroes.py`'s figure-removal sweep only ever ran with real source PNGs present (Phil's machine only), so a verdict withdrawn anywhere else could never reach an already-published page; fixed. Regenerating then surfaced two more bugs the fix itself revealed: `audit_pages.py` flagged the page's now-first, unrelated video thumbnail as a lazy above-fold hero (fixed: video-play thumbnails excluded from that check), and `preflight.py`'s zone-art count still read the page as pictured because it checked for any `<img>` rather than the hero specifically (fixed). All three fail-then-pass proved directly. `OWNER-ACTIONS.md` and `BACKLOG-2026-09-07.md` corrected (7 zone gaps to 8, 30 surfaces to 31, still a free local retry, no billing). Full `preflight.py` (0 gates failed, 22 warnings, all standing), all 100+ `ops/tests/test_*.py` individually (0 fail), `check_urls.py` (188/188), `audit_pages.py` (0 findings), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price or product touched, no new page. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity:** Clean attach (fetch, unshallow, fast-forward onto origin/main), `preflight.py` clean on arrival, 8 issues and 0 PRs unchanged, no mail credential, no egress, no Stripe credential (all retested directly, same as every prior sandbox this week). `BACKLOG-2026-09-07.md` sections 2-6 all done or Phil-gated again; the `ops/*.py` cold-read tier is now fully exhausted (lowest real mention count across the whole tree is 6, up from the 5 recorded two prior passes ago). Per step 5d, ran `ops/roadmap_report.py --allow-partial` directly rather than trust its last-known-good output, since it is the one tool built specifically to separate genuinely actionable rows from Phil-gated ones. It still surfaced `BACKLOG-2026-H2.md` row 3.8 ("Directory and citation listings") as `operator, see note` in "NEXT IN THE QUEUE," the exact misclassification class `row_is_waiting()` was widened to catch earlier today (14 rows fixed, `ops/tests/test_roadmap_report.py`). This one escaped because the fix matches dependency language in the Owner cell, and 3.8's cell said only "see note," pointing at prose two screens away that in fact declines the row outright: real submission means creating third-party accounts under the business's identity, which needs Phil's awareness first (researched and declined 2026-08-24, never reversed). Corrected the row's own Owner cell to state the real blocker directly ("needs Phil (account creation), see note") rather than widen the regex again for one row; verified `\bphil\b` in `WAITING_RE` now catches it, reran the live report and confirmed 3.8 no longer appears in the actionable queue, `ops/tests/test_roadmap_report.py` still 12/12. `preflight.py` clean after (every gate passed, 19 warnings, one fewer than arrival: `hooks-enabled` cleared by setting `core.hooksPath` for this checkout). No price/product touched, no site page changed, IndexNow not applicable. The three CRITICAL-and-OPEN risks in `RISKS.md` (RISK-0007 restore unproven, RISK-0011 product masters unbacked, RISK-0013 no stranger has converted) were re-checked and remain correctly tracked in `OWNER-ACTIONS.md`/`BACKLOG-2026-H2.md`, each genuinely blocked on Phil's own hand or a credential no sandbox holds, not on anything newly found. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity:** Clean attach (fetch, unshallow, fast-forward onto `04f987ef`, no unrelated-history symptom, 311 commits), `preflight.py` clean on arrival (0 gates failed, 20 standing warnings, all previously diagnosed). All 8 open GitHub issues unchanged (art-blocked or decision-labelled), 0 open PRs, no mail credential. `BACKLOG-2026-09-07.md` sections 2-6 remain all done or Phil-gated; the standing cold-read tier and hand-maintained-doc lane, both already worked through roughly 20 cycles today, came back exhausted again. Tried four fresh angles rather than repeat the same search: direct egress test to the live site (still blocked, 403, confirming rather than assuming the sandbox limit); a site-wide sweep of every hand-maintained page for staleness red flags and every dollar amount for a stale/duplicate price (all legitimate); a check for GPU/torch/the cached SDXL model in this container (none present, confirming the local image-generation blocker is this environment, not the 2026-09-10 code fix); and a direct diff of HEAD against `STATUS.md`'s own last-cited commit (already identical, no drift). No defect found. **Prior pass, for continuity:** read `RISKS.md` and `MARKETPLACE-LISTINGS.md` cold. `RISKS.md` checked out current (last reviewed 2026-09-10, section 8's CRITICAL/OPEN list matches RISK-0013's own closing paragraph). `MARKETPLACE-LISTINGS.md` section 1's "Verified on 2026-09-03" table still said the book is "262,633 words", the exact stale figure `gate_kdp_word_count_current` (2026-09-10) exists to catch elsewhere in the same file; it missed this row because its regex required singular "word" and never matched the plural "words" this row used, a blind spot regardless of how stale the number got, not a tolerance question (the real 3.2% drift was always under the gate's deliberate 5% band). Corrected the row to the real, live-measured 271,362 (`build/listings/verify_epub.py`); widened the regex to `words?`; proved fail-then-pass directly in an isolated worktree (old regex: 0 FAIL against a synthetic 26.3%-stale plural claim; new regex: fails it by name; real corrected file: clean). `ops/tests/test_gate_kdp_word_count_current.py` extended 6 to 8 cases. Full `preflight.py` (every gate passed, 20 warnings, unchanged), `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no HTML page changed, IndexNow not applicable.

**Prior pass, for continuity: `BACKLOG-2026-09-07.md` sections 2-6 remain all done or Phil-gated, all 8 open GitHub issues unchanged (art-blocked or decision-labelled), 0 open PRs, no mail credential. Per step 5d, cold-read six low-mention `ops/*.py` files this pass (`wire_legal_strip.py`, `wire_zone_heroes.py`, `hazard_icons.py`, `build_printpack.py`, `prerender_shop.py`, `stripe_links.py`), all clean on direct reruns. Found the real defect reading `site/llms.txt` itself, the file AI answer engines read to learn what the site offers: its `/articles/` bullet said "30 explanatory articles" while `site/articles/` actually holds 29 (confirmed by listing the real files; `ops/build_feed.py`'s own docstring already cites "the 29 root-cause articles" for the same directory). The line was written correct on 2026-09-05 (commit `11d42751`) and never re-derived after the real count changed, the exact "source corrected, artifact never re-derived" class this file's own `gate_llms_txt_current` already exists to catch for missing assets, just not yet for a stale count inside a bullet it does check. Corrected the count and widened `gate_llms_txt_current` to re-derive the real article count from disk on every run and fail if the stated number drifts; `ops/tests/test_gate_llms_txt_current.py` extended 5 to 8 cases (the exact regression, a correct count, and a body with no parseable count degrading to a warning rather than a false failure), fail-then-pass proved directly against the real file (planted the old "30" text, watched `preflight.py` fail by name citing "30" and "29", reverted). Full `preflight.py` (every gate passed, 21 warnings, one more only because `build-id` flags the uncommitted change at measurement time), all 93 test files individually, `check_urls.py` (188/188), `audit_pages.py` (191/0, 0 duplicate titles/descriptions), `affiliate.py --check` (162 documents), mobile `npm test` (`mobile/quest-app`, all suites) all clean after. No price/product touched, no HTML page changed, IndexNow correctly reported nothing to submit (llms.txt is not a sitemap URL).

**Prior pass, for continuity: closed a recurring gap in the operating loop itself, rather than one more content fix.** `ops/NIGHTLY-LOG.md` shows "STATUS.md was N commits stale" corrected by hand at least six separate times this week, twice on 2026-09-11 alone, each caught only when a check-in happened to compare this file's own account against real git history. Two of those entries explicitly declined to gate it ("STATUS.md's own prose is not mechanically diffable the way a generator's output is"), which is true and unchanged. New `gate_status_currency` in `ops/preflight.py` does not diff prose: it warns (never fails) once at least 8 real commits touching `site/`, a page generator, `ops/preflight.py` itself, or one of the five startup-procedure planning documents have landed since this file's last edit with no citation of their hash anywhere in it, the same backtick-hash citation convention already used throughout this file and the log. An ordinary short lag between check-ins stays silent by design. `ops/tests/test_gate_status_currency.py` (17 cases) fail-then-pass proved the pure logic, and a real, isolated `git worktree` planting 9 unmentioned commits proved the wrapper fires by name; the real repository today reports clean. Full account in `BACKLOG-2026-09-07.md`'s "done this week" table and `ops/NIGHTLY-LOG.md`. A concurrent session independently ran a PM check-in over the same five-commit lag this pass started against (see "Prior pass" immediately below); no work was duplicated, both landed on the same `23bee8dd` finding by different reads and only the prose needed reconciling here.

**Prior pass, for continuity: previous work finished and verified independently; brought this file current rather than starting new work.** `preflight.py` failed one gate on this cycle's own first run (`stray-probe-files`, two leftover fixture files under `site/`), traced to this pass's own earlier run being cut off by an outer timeout mid-`gate_tests()`, the exact shape that gate exists to catch; a clean rerun confirmed no files remained and every gate passed (20 warnings, all pre-existing and already diagnosed), so this was not a defect carried over from a prior cycle. The five intervening commits closed the exact handoff the prior pass below left open: Phil, directly with Claude Opus 5, reworded both the `page-art` and `deck-art` preflight warnings (`23bee8dd`), which previously ended "Unblocked by enabling image generation (OWNER-ACTIONS.md 1b)" as if generating and reviewing were one owner-gated step. They are two: GENERATING a replacement runs locally and needs only free system RAM (no decision, no spend); REVIEWING what it generates is the part that needs the vision billing. Both warnings now say so explicitly and point at `ops/generate_zone_heroes.py` for the measured RAM figures rather than repeating a number that can drift. Verified directly rather than trusted from the commit message: `ops/preflight.py`'s current `gate_pages_missing_art` and `gate_deck_download_has_art` source both carry the two-blocker wording, and this cycle's own preflight run reproduced both warnings live with the corrected text. `OWNER-ACTIONS.md` 1b itself was not touched by that commit and should be read together with this correction: it still correctly gates the review/billing half only.

**Prior pass, for continuity: previous work finished and verified independently; brought this file current rather than starting new work.** The four intervening commits (`cc6e68e7`, `22b4b340`, `2e528ad3`, `ba789b9b`, Phil directly with Claude Opus 5) were a real fix, not yet reflected here: local zone-hero image generation (`ops/image_local.py`, SDXL Turbo on the RTX 2070 SUPER) has produced nothing since 2026-08-30 and nothing had reported why. Three compounding defects, each making a broken capability look idle rather than failing: (1) `from_pretrained` reached the network to check for updates on a fully-cached, pinned model, and that call hangs instead of erroring (two runs sat at "0%" for 25 minutes; forced local-only reached 17% in under a second); (2) `--probe` printed torch/CUDA/model/cache and exited 0 without ever loading the pipeline, so it reported healthy on a machine where the real load dies at exit 139; (3) the generate loop caught `Exception`, which does nothing against a segfault. Fixed: local-first load with a genuine-cache-miss fallback, `--probe` now actually loads the pipeline, and the generator now probes in a subprocess so a crash is caught and reported (`NOTHING GENERATED`) instead of silently producing nothing. Verified independently this pass: `python ops/tests/test_image_negations.py` still passes, `preflight.py` still green after the merge. The underlying remaining blocker is system RAM on Phil's own machine (15.8 GB total, about 2 GB free when it last failed), not VRAM: a first diagnosis blamed the GPU's 8 GB card, was corrected same-day (`6a10e6af`/`cd4f8345`, measured rather than repeated: 6.96 GB of VRAM was free when the load died CPU-side), and the generator now prints both figures at failure time instead of asserting a cause. Not billing, not a decision; freeing RAM and a rerun is the next step, and it is not something this sandbox (no local machine) can do. `OWNER-ACTIONS.md` 1b's framing (Gemini billing unblocks "every image on the roadmap") still holds for the *review* step on zone heroes and for all Gemini-API-generated art; it does not cover this local-generation outage, which is now fixed at the code level and gated on hardware availability instead. ~~Left for the operator: `preflight.py`'s `page-art`/`deck-art` warning text still cites only the billing gate as the unblock path and could be misread as meaning generation itself needs billing; worth a precise re-word, not started here.~~ **Done, `23bee8dd`, Phil, 2026-09-10: both warnings now state both blockers by name.**

**Prior pass, for continuity: `BACKLOG-2026-09-07.md` sections 2-6 all done or Phil-gated, so worked the last two names on the standing cold-read tier: `canonical_links.py`, `link_standards.py`.** Both verified live rather than trusted from the read. `canonical_links.py --check`: 0 links would rewrite across the whole site, 2301 internal links extensionless, 0 `.html`, confirming the earlier fix still holds. `link_standards.py`: 0 pages changed, 189 already carry the Standards Pack footer link; checked the 4 without it by hand rather than trusting the count as a defect: two are stripped print/reader pages with no site footer at all, one is the pack's own page (a self-link would be circular), one (`invest.html`) is `noindex`, linked from nowhere on the site, and carries a deliberately minimal footer with no deck/Articles anchor for this tool to key off. All four legitimate, none a bug. The named cold-read tier is now fully exhausted; no fresh low-mention candidate is queued for the next cycle. A concurrent session independently reached this same pair the same day (see the prior-pass account immediately below); no work was duplicated, only the log/dashboard prose needed reconciling. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity: previous work finished and verified independently; this file had gone ten commits stale since its own last account below, so brought it current rather than starting new work.** Two of those ten were PM currency corrections to `EXECUTIVE-DASHBOARD-LIVE.md` (`f21ac74f`, logged in `ed46c1fd`), no defect. The other real one was the operator's own fix (`9bb64ed7`), not yet reflected here: the `wrap_two_lines()` fix logged below (2026-09-10) regenerated only the canonical `build/video/zones` captions via `ops/video_srt.py`; the 228 `build/video/zones-narrated` sidecars that actually ship beside the films kept the old wrapping, up to 55 characters against the stated 42-character budget, because their cue timings come from real narration audio durations stored nowhere else and cannot simply be regenerated. Re-wrapped cue by cue instead; a sample check against git HEAD confirmed timings and words unchanged, only line breaks moved. New `gate_caption_line_length` in `preflight.py` now checks both caption sets against `video_srt.py`'s own `LINE_CHARS` constant, so the two sets cannot drift apart again. That commit also noted `fulfil-orders` has cleared the `cron-cadence` warning entirely since its push trigger landed; `hourly-brief` remains the one schedule reported degraded (3.9x its interval), which is a report cadence, not a delivery. No new defect found in this PM pass itself; the correction was to this file's own currency.

**Prior pass, for continuity: `BACKLOG-2026-09-07.md` sections 2-6 all done or Phil-gated, so per step 5d worked the standing 5-mention cold-read tier: `wire_generated_catalog.py`, `wire_landmarks.py`, `build_icons.py`, `room_image_variants.py`, `prune_catalog_js.py`, `video_narrated.py`.** All six checked out clean on live reruns and direct reads. One near-miss caught before it shipped: `build_icons.py` regenerated the 5 icon files with different bytes than the committed ones, but a pixel-level comparison against the git-committed originals showed 0 differing pixels; that is PNG/ICO encoder non-determinism from a newer Pillow version installed in this sandbox, not a content defect, so the regenerated files were reverted rather than shipped as a fix, per step 5d's own instruction to verify a claim before acting on it. `video_narrated.py` cannot execute here (needs ffmpeg and edge-tts network TTS); read cold instead, no new defect found. Full `preflight.py`, all 92 test files individually, `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No new gate needed: nothing broken was found. Full account in `ops/NIGHTLY-LOG.md`.

**Prior pass, for continuity: previous work verified finished; this file had gone one commit stale since its own last account of "This pass" below, so brought it current rather than starting new work.** The one intervening commit (`48427ed7`) fixed a real defect: `ops/check_affiliate_trigger.py`'s SQL counted every `outbound-click` event toward T2 (the Amazon-application trigger) regardless of destination host, which stopped being correct the moment `site/method.html` shipped a live YouTube channel link on 2026-09-10, since a reader clicking that link fired the identical event and would have counted toward the retailer threshold. Fixed to require the event's own host to be a real retailer, read from `ops/product_links.py`'s own `MERCHANTS` config; new `ops/tests/test_check_affiliate_trigger.py` (3 cases), fail-then-pass proved via `git stash` on the real pre-fix file. Full `preflight.py`, all 92 test files, `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after, per that commit's own account. `BACKLOG-2026-09-07.md` sections 2-6 remain all done or Phil-gated; the standing cold-read lane (5-mention `ops/*.py` tier) is now one file shorter (`build_icons.py`, `room_image_variants.py`, `video_narrated.py`, plus the rest named below). No new defect found in this PM pass itself; the correction was to this file's own currency, the same recurring drift class the entries below already name.

**Prior pass, for continuity: previous work verified finished; this file had gone four substantive commits stale since its own last account of "This pass" below (a PM check-in that checked this file and found it current had run one commit before the drift, not after), so brought it current rather than starting new work.** In order since the `video_srt.py` entry below: `STATUS.md` was corrected once already (`e7f00547`) for the `DECISIONS.md` index fix, the `EXPERIMENT-PLAN.md` correction and the `video_srt.py` fix itself; a PM check-in then handed the operator the catalog-wiring cold-read tier, finding nothing new; the operator's own next cycle came back clean too; and then a same-window cycle closed the ownership-drift defect class for good, auditing all 34 real `ops/build_*.py` generators against `gate_generator_ownership`'s chain (it has separately caught and fixed 15 unprotected ones this week, one operator at a time). All 15 outside the chain already had a real gate protecting them elsewhere; a new `gate_every_generator_has_a_protection_plan()` now fails by name the day a 35th generator ships in neither list, proven on a real planted file (`LEARNINGS.md` LRN-0009). `BACKLOG-2026-09-07.md` sections 2-6 remain all done or Phil-gated; the standing cold-read lane (5-mention `ops/*.py` tier) is unchanged and still handed to the operator below. No new defect found in this PM pass itself; the correction was to this file's own currency, the exact class of drift the ownership-drift close above was about, just recurring here instead.

**Prior pass, for continuity: previous work verified finished; this file had gone three substantive commits stale since its own last account of "This pass" below, so brought it current rather than starting new work.** `BACKLOG-2026-09-07.md` sections 2-6 all done or Phil-gated, so the standing cold-read lane continued: `ops/video_srt.py`'s `wrap_two_lines()` was found and fixed (a cue needing a third wrapped line collapsed into one unbounded string, 617 of 6,732 lines across all 114 committed `.srt` sidecars over the stated 42-character budget; regenerated clean, `ops/tests/test_video_srt.py` added, fail-then-pass proved). Separately, `EXPERIMENT-PLAN.md`'s Phase 0 table still read analytics, conversion events and traffic as Missing, written launch day; Umami and six gated `quest.js` funnel events have since shipped and gone unrecorded there, and EXP-102's premise ("most SKUs cannot be bought") was stale against the current 158-of-159 buyable catalogue. Both corrected. Separately, `DECISIONS.md`'s own "Decision Index" table, which calls itself a compact index of the whole file, had never grown to include the eight D-series decisions (D-001 to D-003, D-014 to D-018), two of them among the file's most consequential calls; indexed, new `gate_decisions_index_current` added. None of this was reflected here. No new defect found in this PM pass itself; the correction was to this file's own currency. Left for the operator: the 5-mention `ops/*.py` cold-read tier, now one file shorter (`build_icons.py`, `build_social_captions.py`, `canonical_links.py`, `card_spec.py`, `check_affiliate_trigger.py`, `generate_card_heroes.py`, `generate_zone_heroes.py`, `link_standards.py`, `prune_catalog_js.py`, `review_deck_art.py`, `review_heroes.py`, `room_image_variants.py`, `shoot_mobile.py`, `video_narrated.py`, `video_zone_photo.py`, `wire_aria_current.py`, `wire_generated_catalog.py`, `wire_landmarks.py`), an hours-sized read not started here.

**Prior pass, for continuity: `ops/merge_cardtext.py`, the free Entryway deck's own text corpus builder, had never once been called from `preflight.py`; running it cold surfaced 47 dead card cross-references and two fabricated statistics, one already baked into a live download.** The standing handoff (`DECISIONS.md` cold-read for citation staleness) was worked first and came back genuinely clean: every dated evidence line in D-016/017/018 checked directly against current catalogue and traffic data, still accurate as historical record. `fill_front_matter.py` and `optimize_sample_pdf.py` also checked cold, both clean and already correctly applied. Per step 5d, moved to `ops/merge_cardtext.py`, a file whose own dangling-link and unsourced-claim checks had never been wired into `preflight.py`. Running it printed "34 dangling links"; widened the check myself (the field is also stored as lists of "CODE Title" strings across different transcription batches, not only bare codes) and found 47, mostly a whole "Experts" card family (`EX-001` to `EX-012`) that was cross-referenced but never authored. Verified against the real shipped product, not the JSON: `site/assets/cards/entryway/EE-002-Entryway-Rainstorm-back-lg.webp`, already live on `deck-gallery.html`, prints "EXPERTS to EX-002 Weather Prep," a card that does not exist. 20 of 72 already-drawn cards carry this. One card, `EM-012` (the deck's last), also prints an unsourced "People make up to 35,000 decisions a day" statistic and a "NEXT CARD: Living Room" promise for a second room deck this backlog holds on evidence, not built. Fixed what code can fix, free: all 47 references corrected or dropped across the six source batches, both statistics rewritten to true, non-statistical copy, `claims` cleared on 3 cards already resolved via a rewritten `did_you_know`. New `gate_card_related_links` in `preflight.py`, plus two real gaps in `gate_unsourced_stats` fixed (a number not glued to its unit word; list-valued fields never scanned), `ops/tests/test_gate_card_related_links.py` (10 cases, fail-then-pass). Cannot fix by text alone: the 20 already-drawn images still show the old pixels, added to `OWNER-ACTIONS.md` item 1b as a cheap addition to the existing Gemini billing gate. Full `preflight.py` (every gate passed, 17 warnings), all tests, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents) clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass, for continuity: closed the gap between work already shipped on main and this file's own account of it.** Three pushed cycles, a real fix to `ops/accept_image.py`'s negative-clause parser plus two PM triage check-ins, had landed after this file's last update and it still read as if the `build_sample_html.py` fix below were the current state. `ops/accept_image.py`: `_negative_clauses()` derives "must not show" checklist items from a zone's own `done_looks_like` text via a `no|nothing` regex, and matched "or X" as a second forbidden item even when it followed "nothing", inverting an acceptable alternative state into a violation. The bedroom zone's own real text, "Under the bed holds either nothing or two labelled flat bins," produced the forbidden phrase "or two labelled flat bins." Scanned all 114 zones: 1 hit, this one. Fixed by skipping any captured phrase starting with `or\b`, extended `ops/tests/test_accept_image.py` with both the regression case and a case proving a genuine "no X or Y" pair still fails correctly, fail-then-pass proved via `git stash`. Verified: `--self-test` (4/4), `--check` (89 cards plus 114 zones, 0 errors), full `preflight.py`, `affiliate.py --check` (162 documents). The two PM check-ins that followed found every unblocked backlog row again done or Phil-gated, corrected a stale handoff (`accept_image.py` and `build_manual_print.py` had both already been solved in earlier passes; the mention-count heuristic that named them unread had only scanned nearby log entries, not the full 18,700-line log), and concluded the `ops/*.py` cold-read lane is now genuinely saturated (lowest real mention count across the whole file tree is 5). Handed the next reader to `DECISIONS.md` for a citation-staleness cold-read instead, the same defect class `RISKS.md`, `GOALS.md` and this file have each caught today; that read is hours-sized, left for the hourly operator rather than started here.

**Prior pass, for continuity: `ops/build_sample_html.py`, the generator for the site's primary lead magnet (the free 30-chapter sample), found stripping its own cache-busting fingerprint on a standalone run; fixed and the gate that protects six sibling generators widened to catch this shape too.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass cold-read `ops/build_social_captions.py` (clean) then `ops/build_sample_html.py`. Its own docstring instructs `python ops/build_sample_html.py --apply` as a standalone command, but `main()` never chained `fingerprint_assets.main()`. Reproduced directly: ran its own transform against the real source and diffed the result against the committed, shipped file, the only difference was the `?v=` hash missing off both stylesheet links. `gate_generator_chains_fingerprint` (written 2026-09-09) could not see it: it never calls `build_avif.wire()`, since it wires no pictures at all, only degrades them to text. Fixed by chaining the fingerprinter, verified a standalone run now reproduces the committed file byte-for-byte. Widened the gate with a second, direct trigger, any `ops/build_*.py` with a literal unversioned href to a `.css`/`.js` under `assets/`, checked against the real tier before trusting it (hits exactly the 9 real page generators that write such a literal, all 9 now correctly chaining the fingerprinter, 0 false positives). `ops/tests/test_gate_generator_chains_fingerprint.py` extended 6 to 9 cases, fail-then-pass proved directly against the real file. Full `preflight.py` (every gate passed, 18 warnings, unchanged), all test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page content changed (the shipped file is byte-identical to before, correctly restamped).

**Prior pass, for continuity: `ops/root_causes.py` said EXCESS had no matching article a full two days after a real, on-topic one shipped, and fixing that mapping surfaced a second, independent bug in `general_reading()`'s cap logic that could push a zone under M5's 3-link floor.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass cold-read `ops/root_causes.py`. Its own comment said EXCESS and CONFLICTING USERS both had no article; checking `site/articles/` directly found `more-storage-wont-fix-clutter` (shipped 2026-09-08, "the container trap": excess, wrong location, no assigned home, unclear ownership), a genuine match for EXCESS the mapping was never told about, the same "source shipped, artifact never re-derived" class this backlog names as dominant. Confirmed live impact before fixing: 10 real friction branches across the 12 diagnosed pilot zones reference EXCESS. Mapped it. Regenerating `site/zones/` to pick up the fix surfaced a second, real bug rather than a clean rebuild: `general_reading()`'s initial per-zone pick loop respects its own `article_cap` but never checks the 3-link `floor` its exclusions could push a zone below, and the extra diagnosed-zone usage from the EXCESS fix (shared `counts` state, dict-iteration order deciding who gets first pick) starved two low-signal patio zones to 2 links each, silently under M5's stated floor. Fixed `general_reading()` to guarantee the floor over the cap, the same standing the uniqueness swap pass already gives the floor; verified the fix holds even under an artificially harsh `article_cap=1` against the real corpus, not just today's numbers. New `gate_root_cause_articles_current` in `preflight.py` (two-way docstring-vs-mapping consistency, `ops/tests/test_gate_root_cause_articles_current.py`, 5 cases) and a 5th check added to `ops/tests/test_general_reading.py`, both fail-then-pass proved directly against the real files. `ops/build_zone_pages.py` re-run twice back to back, byte-identical after. Full `preflight.py` (every gate passed, 19 warnings, one more than baseline only because uncommitted changes were present when measured), `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), `link_graph_report.py` (0 orphans, min 3 inbound on the two previously-starved zones), mobile `npm test` (4 suites) all clean after. No price/product touched, no new page; 54 zone pages' related-reading content changed. IndexNow `--changed` queued, correctly reported UNCHECKED here (no egress), picked up by the hourly workflow's own credentialed run.

**Prior pass, for continuity: `ops/build_avif.py`'s `wire()` silently stopped adding AVIF sources to a page's second picture block once its first was already wired.** Handed off by the prior PM check-in as the next low-mention file to cold-read, per step 5d. `wire()` skipped an entire page the instant it contained any `type="image/avif"` string anywhere, on the assumption one avif source meant the whole page was done. Reproduced directly: a two-picture fixture with the first block already avif-wired and the second still webp-only, its own `.avif` file present on disk, got nothing added to the second block. No live page hits this today (887 of 887 webp files carry an avif sibling, coverage complete everywhere, because every generator regenerates its pages from scratch before wiring), but a hand-maintained page gaining a second image after its first wire pass, or a changed generator run order, would ship it silently. Fixed to check per source tag whether an avif source immediately precedes it, not whether the file has one anywhere. New `ops/tests/test_build_avif.py` (3 cases), fail-then-pass proved (`git stash` on the fix, 2 of 3 assertions failed by name, clean after). Reran `--wire` against the real site: 0 pages changed, confirming today's coverage was already complete and the fix is purely protective. Full `preflight.py` (every gate passed, 18 warnings, all pre-existing), 84 test files via `gate_tests`, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page content changed, IndexNow not applicable.

**Prior pass, for continuity: the site had no inbound link to its own live YouTube channel anywhere, and `method.html` told visitors none of it had been filmed.** Every unblocked backlog row was again done or Phil-gated, so per `GOALS.md` decision rule 1 (distribution beats production) this pass checked whether the site references its own YouTube channel: it did not, on any of 191 pages, despite 12 real narrated, captioned zone videos being live there today (`ops/youtube-published.json`, `ops/state-checkin.json`). Worse, `site/method.html`'s video section stated "None of it has been filmed yet," a live false claim on a customer-facing page (`CLAUDE.md` section 8). Corrected the claim and added an honest link to the real channel; only then added the channel to Organization JSON-LD's `sameAs` in `ops/build_seo.py` (it was deliberately empty, with a comment explaining why that had gone stale today). Disclosed the new outbound host in `privacy.html`, which `gate_third_party` correctly required. New `gate_sameas_backed_by_onsite_link` in `preflight.py`: a `sameAs` entry with no matching on-site link now fails the build in either direction, fail-then-pass proved directly. Full `preflight.py` (every gate passed, 19 warnings, one more than baseline only because uncommitted changes were present when measured), all 76 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), `link_graph_report.py` (0 orphans), mobile `npm test` (4 suites) all clean after. No price/product touched. IndexNow attempted (`--changed`, 15 URLs queued) and correctly reported UNCHECKED: no egress to the live site from this sandbox, picked up by the hourly workflow's own credentialed run.

**Prior pass, for continuity:**

**Closed: `gate_visual_audit`, a hard-FAIL preflight gate, was reading a real timing race in `ops/audit_visual.py` as a live contrast defect on `site/shop.html`.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass ran `ops/audit_visual.py --all` directly rather than cite a prior clean result. Two back to back runs on the same unchanged tree disagreed: one reported dozens of shop.html contrast failures as low as 1.52:1, the next reported 0. Computing WCAG contrast by hand for the exact RGB pairs it printed gave 5.6:1 to 15:1, proving the numbers, not the page, were wrong. Cause: site.css fades shop.html's client-rendered product grid in from `opacity:0` over a real, wall-clock-timed 0.7s transition; the audit's own settle timer only waits a fixed 250ms after images load, so its DOM dump can land mid-fade under load. Fixed by adding `--force-prefers-reduced-motion` to the headless browser flags, which makes it apply site.css's own existing reduced-motion rule (`.reveal{opacity:1}`, no transition), a real state some visitors already get, removing the race rather than out-waiting it. New `ops/tests/test_audit_visual_reduced_motion.py` proves the flag is present and genuinely works on this machine's browser; a true fail/pass reproduction of the timing race itself was attempted and abandoned as impractical (a synthetic single-page test could not reproduce it), recorded honestly. Full `preflight.py` (every gate passed, 18 warnings), all 75 test files, `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed: this is QA-tooling correctness, not a shipped defect.

**Closed this pass: `ops/zone_supplies.py`'s own module docstring described the affiliate catalogue as it stood before 2026-09-04, in the present tense, after the real state moved past it.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass cold-read six low-mention `ops/*.py` files, running each rather than trusting the read. Five (`stripe_check.py`, `mailer.py`, `sync_page_links.py`, `verify_media_delivery.py`, `receive_deploy_key.py`) were clean. `zone_supplies.py` said, twice, "Today every one of its 123 rows carries `Link Status: Unverified` and an empty `Affiliate URL`... the state all 123 rows are in right now." Checked directly against `ops/affiliate-catalogue.csv`: 120 of 123 rows have carried a verified URL since 2026-09-04 (`ops/product_links.py`), and the module's own `_report()` already correctly renders 1,717 real links from them; only the comment describing the code was wrong, the same "source corrected, artifact never re-derived" class this backlog names as dominant, here inside a docstring. Corrected both instances to the real count. New `gate_zone_supplies_docstring_current` in `preflight.py` re-derives the verified-row count from the CSV on every run and fails if the docstring's own cited number drifts, or if the old claim reappears; fail-then-pass proved twice directly against the real committed file. Full `preflight.py` (every gate passed, 18 warnings), all 72 test files, `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass, for continuity: this session's own first `preflight.py` run failed two gates that a second, unmodified run passed clean; root-caused and fixed rather than treated as noise.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass checked its own first cold-checkout preflight run rather than another `ops/*.py` file: it reported `FAIL affiliate` ("could not read 2 delivered document(s)") and `FAIL tests` (3 of 71, the same check inside `test_affiliate.py`), and a second run moments later, nothing else changed, passed both clean. Traced rather than shrugged off: `bootstrap_fresh_sandbox()` fires one `pip install pymupdf` and moves on regardless of exit code; this run's first attempt hit a genuine `ReadTimeoutError` against `files.pythonhosted.org` (a cold proxy tunnel, not a policy denial), leaving pymupdf still missing when `affiliate.check()` tried to read two PDFs, which correctly fails closed when it cannot look. This is exactly the "fresh checkout hits a known gap" class the bootstrap's own docstring says it exists to end, still reachable because the install itself was never verified. Fixed with new `ensure_pymupdf()`: retries the install up to 3 times with a longer pip timeout, confirms a real `import pymupdf` after each attempt instead of trusting pip's exit code, and names the cause plainly if it still cannot import after every retry. `ops/tests/test_ensure_pymupdf.py` (4 cases), fail-then-pass proved via `git stash` (old code has no such function). Reproduced the real fix end to end: uninstalled pymupdf, ran the real `preflight.py` cold, attempt 1 succeeded, every gate passed. Full `preflight.py` (every gate passed, 18 warnings), all 74 test files, `check_urls.py` (188/188), `audit_pages.py` (0 dup), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass, for continuity: a stale book word count in two owner-facing documents, corrected and gated.** Every unblocked backlog row was again done or Phil-gated, so per step 5d this pass ran `build/listings/verify_epub.py` against the real, committed EPUB rather than trust `check_kdp.py`'s "zero failures" claim on sight. It measures 271,362 words; `MARKETPLACE-LISTINGS.md` and `OWNER-ACTIONS.md` (item 14, the Amazon KDP owner action) both said "262,000 word," a figure written 2026-09-03 before later manuscript edits, 3.5% stale. Not material to the royalty math, which prices delivery off the file's MB size, but the same "source corrected, artifact never re-derived" defect class this backlog names as dominant, this time in a number Phil is told to weigh a pricing decision against. Both documents corrected to 271,000 (rounded). New `gate_kdp_word_count_current` in `preflight.py`, recomputing the live count independently and failing if either document's claim drifts more than 5% from the real EPUB; `ops/tests/test_gate_kdp_word_count_current.py` (6 cases), fail-then-pass proved. Full `preflight.py` (every gate passed, 19 warnings), `check_urls.py` (188/188), `audit_pages.py` (0 duplicate titles/descriptions), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass (twelfth), for continuity: `PLAN-VISUAL-STRATEGY.md` (ux-frontend, 2026-09-07) claimed in present tense that all 114 films still fail the truncation/six-pass tests, when the same commit that introduced the document (`2d99fecb`) had already fixed exactly that in `ops/video_zone.py`.** Verified directly against the code: `beats()` already splits every pass at sentence boundaries and renders all six passes, and `video_narrated.py` calls the same function, so the narrated pipeline was never a separate gap. Yet the plan's summary, its §5.1 lead-in, its "Today all 114 films fail V1 and V2" line, and its §5.2 to-do list all still read as if the defect were live. Corrected all four spots, keeping the original finding as a dated record rather than deleting it, and honestly flagged what stays unverified: whether already-rendered local video files reflect the fix (no ffmpeg in this sandbox to check), and whether the 12 videos already live on YouTube (uploaded by hand before this pipeline existed) carry it, since YouTube cannot replace an uploaded file. New `gate_visual_strategy_truncation_current` in `preflight.py` checks both the document's claim and that the code still contains the fix; fail-then-pass proved directly. Also caught and fixed one em dash introduced while drafting the correction, via `ops/dashboard.py`'s own `ctrl_em` count moving 0 to 1, before it reached a commit. Full `preflight.py` (every gate passed, 19 warnings), `check_urls.py` (188/188), `audit_pages.py` (0 duplicate titles/descriptions), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass (eleventh), for continuity:**

**Closed: `gate_affiliate_trigger` was silently swallowing its own "could not check" state, which is the exact defect class this repository has spent the month building gates to catch, this time inside one of the gates itself.** Every unblocked backlog row was again done or Phil-gated, so this pass read a genuinely unmentioned file cold (`ops/check_affiliate_trigger.py`, 0 hits in `ops/NIGHTLY-LOG.md`), per step 5d, despite it being cited in `GOALS.md` and wired into both `ops/dashboard.py` and `ops/preflight.py`. Its own `verdict()` correctly distinguishes three states: T2 fired (True), measured and genuinely below threshold (False, silent by design so a "0 of 60" line does not get skipped for a year), and could-not-read-the-database (`None`, meant to be reported, never treated as a measured zero, per the module's own docstring quoting `CLAUDE.md` 0.4 almost verbatim). `gate_affiliate_trigger` only tested `if fired:`, and `None` is falsy in Python, so the unreadable case printed nothing at all. Proved directly in this sandbox: called the real function, got `fired=None` (no ssh key, database unreachable, the state every credential-less sandbox this operator has ever run in actually produces), and confirmed the gate emitted zero warning lines instead of the "T2 NOT EVALUATED" line its own reading already knew to write. Fixed with `if fired or fired is None:`. New `ops/tests/test_gate_affiliate_trigger.py` (4 cases: fired warns, measured-below-threshold stays silent, unreadable warns UNCHECKED, a raised exception still warns via the existing except clause), fail-then-pass proved via `git stash` against the real pre-fix file. Preflight's warning count moved from 18 to 19, the new `affiliate-trigger: T2 NOT EVALUATED` line now visible on every run in this sandbox instead of nowhere. Full `preflight.py` (every gate passed, 19 warnings), all 66 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass (tenth), for continuity:**

**Closed: the Etsy listing checker was never wired into any unattended cycle, and the flagship listing's own zone-claims verifier printed a false "standards sheet ABSENT" on every run.** Every unblocked backlog row was again done or Phil-gated, so this pass read the genuinely unread `build/listings/*.py` tier (0-1 log mentions, versus 4+ for every `ops/*.py` file by now) instead of a saturated re-read; these are the Amazon/Etsy/KDP listing tools, directly relevant to the traffic epic (owner gate 4, "the only channels with buyers already in them"). `check_etsy.py` passes clean but, like the KDP package before `gate_kdp_listing_valid` existed, nothing ran it unattended. Separately, `verify_zone_claims.py` (the tool that once caught a real false zone claim in the Kitchen listing) hardcoded one file per listing; L1 correctly bundles its standards sheet as a second, separate PDF, so this tool never opened it and printed "standards sheet ABSENT" for the highest-price listing every time it ran, a false negative about the exact kind of claim it exists to protect. Fixed `verify_zone_claims.py` to read the real file list from `etsy-listings.json` and recognise the standalone Standards Pack's own "SHEET n OF 20" heading alongside the phrase the other four packs use. New `gate_etsy_listing_valid` in `preflight.py` runs `check_etsy.py` and independently re-derives the standards-content fact with its own marker patterns, deliberately not importing the fixed script's constant (proved while testing: doing so silently fell to warn rather than fail against the pre-fix script). `ops/tests/test_gate_etsy_listing_valid.py` (4 cases), fail-then-pass proved by monkeypatching pymupdf. Full `preflight.py` (every gate passed, 17 warnings), all 62 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no site page changed, IndexNow not applicable.

**Prior pass (ninth), for continuity:**

**Closed: the one automated, credentialed, hourly mail Phil actually reads could have sat through a repeat of the exact 2026-08-30 payment-link outage and still said "all pages 200".** Every unblocked backlog row was again done or Phil-gated, so this pass checked which scheduled job actually holds both a Stripe credential and real egress to the live site, since `check_live_links.py` (built specifically to catch a deactivated Stripe link that still answers HTTP 200) needs both and this sandbox has neither. `.github/workflows/hourly-brief.yml` has both: it already carries `STRIPE_SECRET_KEY` and already proves real egress to `6s-success.com` by running `ops/indexnow.py` in the same job. It never called `check_live_links.py`. `ops/hourly_brief.py`'s own SITE section only checked HTTP status (the exact blind spot that tool's docstring names) and its COMMERCE "live payment links" line was a raw count of active Stripe links, not a check that the live buttons point at them. So the credentialed automation could reach "all pages 200" and "N live payment links" during a real repeat of the outage this codebase is scarred by, and nobody would see it in the one channel built to reach Phil hourly. Fixed with `hourly_brief.payment_link_summary()`, a pure function wired into `build()` that calls `check_live_links.check()` and prepends `OUTAGE - PAYMENT LINK DEAD -` to the SUBJECT line (not only the body) whenever the live site serves a confirmed-dead or account-unknown link; a genuinely unchecked state (no credential, site unreachable) reads as UNCHECKED, never as OK and never as an outage, per `CLAUDE.md` 0.4. No workflow YAML change needed: the credential the fix needs was already in that exact step's env. New `gate_hourly_brief_payment_links` in `preflight.py`, proved fail-then-pass directly (an `AttributeError` without the fix, surfaced by name through `run_gate`'s own exception handling; clean after), exercising all four real branches (ok, dead, unknown-with-slugs, unchecked) plus the real `build()` subject line with everything else stubbed and no network touched. Full `preflight.py` (every gate passed, 17 warnings), all 59 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents) all clean after. No price/product touched, no site page changed (ops/ only), IndexNow not applicable.

**Prior pass (eighth), for continuity:**

**Closed: `site/llms.txt`, the manifest AI answer engines read to learn what the site offers, was missing both free card decks.** Every unblocked backlog row was again done or Phil-gated, so this pass read a low-mention, hand-maintained file cold, per step 5d. `llms.txt` named `/zones/`, `/rooms/`, `/articles/`, `/method.html`, `/quest.html` and `/shop.html`, but not `/deck.html` (Entryway deck, 88 cards, free) or `/kitchen-deck.html` (Kitchen deck, 72 cards, free, shipped 2026-09-08). Both are exactly the kind of free, ungated asset an AI answer engine could cite; `GOALS.md` O1 already confirms ClaudeBot and GPTBot fetch this site directly. Checked before writing anything: the mudroom deck stays out on purpose, `BACKLOG-2026-H2.md` 2.7 records Phil's own decision to hold it back from promotion, not a second oversight. Added one bullet naming both promoted decks, honestly noting the Kitchen deck's art is not drawn yet. New `gate_llms_txt_current` in `preflight.py` (`ops/tests/test_gate_llms_txt_current.py`, 5 cases, fail-then-pass proved against the real committed file) stops the next promoted page shipping unmentioned. Full `preflight.py` (every gate passed, 17 warnings), all 59 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites) all clean after. No price/product touched, no HTML page changed, IndexNow not applicable (llms.txt is not in the sitemap).

**Prior pass (seventh), for continuity:**

**Closed A2/M5 this pass: the 102 zone pages with no `diagnosis` yet stopped carrying the identical 19-link related-reading block.** Every unblocked backlog row was again done or Phil-gated (M6 correctly still gated on M4's 21-day read), so this pass worked the highest-ranked genuinely open row aimed at the constraint (Epic 3, traffic) instead of another audit pass. New `general_reading()` in `ops/build_zone_pages.py` scores each of the 19 general articles against a non-diagnosed zone's own already-published text (its judgement call, all six passes, its hazards) using grounded keywords, real overlap only. Two real bugs found and fixed before shipping: the scoring was non-deterministic across `PYTHONHASHSEED` (an unsorted set-intersection sum), and the per-article cap of 30 only watched the 102 non-diagnosed zones, letting the 12 diagnosed zones' independent picks push three articles to 38 site-wide links; both fixed, plus a deterministic collision-resolution pass for the 11 of 102 zones whose thin real text tied under the tightened cap. Verified against the real, generated pages: all 114 zone pages carry 3 to 5 links, 0 duplicate sets site-wide, 0 orphans introduced (`ops/link_graph_report.py`), article inbound-link concentration dropped from avg 76.3 (max 124) to avg 26.6 (max 47). New `gate_general_reading_differentiated` in `preflight.py`, two new test files (`test_gate_general_reading.py` 12 cases, `test_general_reading.py` 4-seed determinism and idempotency), both fail-then-pass proved. Full preflight, all 58 test files, `check_urls.py` (188/188), `audit_pages.py` (191/0), `affiliate.py --check` (163 documents), mobile `npm test` (36 assertions) all clean. Pushed (`b7e24dda` merged with a concurrent hourly check-in commit, `a9d61d35`); CI triggered, not yet confirmed at the time this line was written. Full account in `PLAN-MICROZONES-DECKS-APP.md`'s M5 row and `ops/NIGHTLY-LOG.md`.

**Prior pass (sixth), for continuity:**

**Found and fixed: the cron-cadence gate the previous pass built only ever covered 2 of the repository's 5 scheduled workflows, because its parser only understood one cron shape.** Every unblocked row in `BACKLOG-2026-09-07.md` was again done or Phil-gated, and the deep audit and every low-mention `ops/*.py` candidate checked this pass came back clean (see `ops/NIGHTLY-LOG.md` for the full list read), so this pass re-examined the prior pass's own new tool rather than manufacture a finding. `ops/check_cron_cadence.py`'s `WORKFLOWS` list named only `fulfil-orders.yml` and `hourly-brief.yml`; `.github/workflows/` actually schedules five (`linkedin-drafts.yml`, once daily; `status-email.yml`, six fixed hours in one cron line; `roadmap-report.yml`, four fixed hours across separate cron lines). `configured_interval_minutes()` could not parse any of those three shapes: tested directly against the real files, it silently returned 60 minutes for a once-a-day cron (24x wrong) and for a six-times-a-day cron (4x wrong), and `None` (unmeasurable) for the four-separate-lines shape. Rewrote the parser to count real fires per day (minute values times hour values, summed across every `cron:` line) rather than only reading the minute field of the first line, and to explicitly refuse to guess (return `None`) whenever a day-of-month/month/weekday field is not `*`, since the every-day-alike arithmetic would then be wrong rather than merely unmeasured. Measured all 5 workflows against the real Actions API the same way: `linkedin-drafts.yml` (mean gap 1438 min against a configured 1440, ratio 1.00) and `roadmap-report.yml` (352 against 360, ratio 0.98) both run almost exactly on schedule; `status-email.yml` runs a real 1.57x slower than its four-hour cycle (mean 376 min against 240), measurable drift but under the gate's 2.5x "degraded" line. This narrows, not widens, the finding below: the sustained multi-day slowdown is specific to the two workflows GitHub is asked to fire more than once an hour, not a blanket fact about every scheduled job on this account. `ops/tests/test_check_cron_cadence.py` extended from 5 to 9 cases (the daily shape, the six-hour-one-line shape, the four-separate-lines shape, and the weekday-restriction refusal), fail-then-pass proved in an isolated git worktree against the original parser: it mis-parsed all three real new workflows and wrongly guessed a number for the weekday case. Also fixed, found while reading the test file: its own final line hardcoded "N of 6 cases pass" when only 5 cases existed, so it had been over-reporting its own coverage by one; now computed from the real case count. `preflight.py`'s `gate_scheduled_workflow_cadence` docstring updated to match; its live warning output is unchanged (2 warnings, same two degraded workflows), because none of the three newly-covered workflows crosses the degraded threshold. Full verification after: `preflight.py` (0 gates failed, 16 warnings, `hooks-enabled` cleared this pass), all 54 `ops/tests/test_*.py` files, `check_urls.py` (188/188), `audit_pages.py` (191/0, 0 duplicate titles/descriptions), `affiliate.py --check` (162 documents), mobile `npm test` (4 suites), all clean.

**Prior pass (fifth), for continuity: found and fixed the same coverage gap's parent finding.** Scheduled GitHub Actions workflows in this repository do not run on their configured schedule, sustained for 14+ days, and one same-day log entry had already misdiagnosed one instance of this as a one-off "GitHub-side incident." Pulled the real run history for `fulfil-orders.yml` (order fulfilment, configured every 30 minutes, its own comment written against the promise on `thanks.html`) and `hourly-brief.yml` (configured hourly) via the Actions API directly rather than trusting the cron line: `fulfil-orders.yml`'s last 49 gaps averaged 213 minutes (worst 367) against a configured 30, and `hourly-brief.yml`'s last 49 averaged roughly 4 hours against a configured 60, both computed from every run since the earliest page the API returned (8 to 14+ days), not a single bad day. Zero of 49 `fulfil-orders.yml` gaps were within 35 minutes of the previous run. This is not new latency the operator caused; it is GitHub's own scheduler under-delivering on the `schedule:` trigger, invisible until someone asked the API rather than trusted the YAML. Two live consequences, both fixed: `ops/roadmap_report.py`'s email to Phil said "the instruction reaches the operator within the hour," which the measured data shows is false (typically several hours); reworded to "the operator's next automated cycle picks it up, typically within a few hours (GitHub's own scheduler, not a fixed clock)." `thanks.html`'s own live delivery copy was already honest ("within a few hours... not instant") and needed no change; `fulfil-orders.yml`'s header comment, which still reasoned from the literal 30-minute promise, was corrected to cite the measured reality instead. New `ops/check_cron_cadence.py` (parses the real cron line out of the workflow file, pulls real run history via the Actions API, flags a workflow whose mean gap exceeds 2.5x its configured interval) and `gate_scheduled_workflow_cadence` in `preflight.py` make this a standing, machine-checked warning rather than a fact that has to be rediscovered by hand again; `ops/tests/test_check_cron_cadence.py` (6 cases, fail-then-pass proved) covers on-schedule, degraded, unreachable-API and too-few-samples. Left as a warning, not a failure, since the delay is not something a commit here causes and no live customer-facing page is currently wrong; recorded here rather than as an `OWNER-ACTIONS.md` item because the documented mitigation (swap fulfilment for a Stripe webhook) is only worth Phil's time if volume ever makes the latency commercially unacceptable, which one lifetime order has not shown.

**Prior pass (fourth), for continuity, found and corrected a stale claim rather than re-doing already-fixed work: `PLAN-MICROZONES-DECKS-APP.md`'s M7/A1 (per-card victory conditions, 1.5 days scoped, still marked open) had already had its actual honesty defect fixed by Phil directly (`fa491b1a`, 2026-09-07) two days before this pass read it.** The row's own premise, "570 of 684 cards print a stop condition that card cannot reach," was true when written and had already been resolved: `site/assets/js/quest.js`'s `renderCard()` no longer heads the card "You can stop when" over the whole-zone `done_looks_like` text; it says what the text is ("The whole zone is done when") and places the reader against it ("This card is pass N of 6, so you are not aiming for all of it right now"). Verified by reading the shipped code directly, not the commit message alone. What Phil's fix does not do, and what M7's full acceptance criteria still asks for, is a genuinely distinct authored `victory` line per card (570 of them); that stays real, correctly unstarted product-tier work per `GOALS.md` rule 1 (distribution beats production), not a defect. Updated `PLAN-MICROZONES-DECKS-APP.md` (section 1.4, M7, A1) to say precisely what is fixed and what remains, so a future cycle does not re-open the row cold and either re-investigate it or spend 1.5 days re-authoring the half that no longer needs it. New `gate_quest_card_victory_honesty` in `preflight.py` (`ops/tests/test_gate_quest_card_victory_honesty.py`, 6 cases) protects Phil's fix from regressing, since nothing did before; proved fail-then-pass by reintroducing the literal old heading into the live, committed file, watching `preflight.py` fail by name, then reverting (clean diff after). Also checked A1/A3/A4 against the live app directly: A3 (the symptom entry screen) and A4 (the two-minute first action) are both already fully implemented, shipped under A5/A6's own commits on 2026-09-08 though never marked against their own rows in this table; left a note in the plan doc rather than re-verifying and re-shipping them a second time. `core.hooksPath` was unset again (per-clone) and reset to `.githooks`.

**Prior pass (third), for continuity: closed A5 (app funnel instrumentation), `PLAN-MICROZONES-DECKS-APP.md` section 4.4/4.5, and found S1-S4 (Sustain schema) likely does not need the days it was scoped for.** A5 asked for five funnel events; two already existed (`quest-symptom-picked`, `quest-symptom-start`), and this pass added the three genuinely missing ones to `site/assets/js/quest.js`: `quest-cause-shown` (the ask vs. the reveal are now distinguishable), `quest-card-abandoned` (pass, elapsed seconds; fires only while a card's timer is running and the tab hides or closes), and `quest-return` (integer days since the browser's last visit). `quest-victory-confirmed` was not added separately since `quest-first-victory` already marks that moment. Verified two ways: a new static gate (`gate_quest_funnel_events`, `ops/tests/test_gate_quest_funnel_events.py`, 8 cases, fail-then-pass proved on all five markers) and a real headless-Chromium run (`ops/tests/test_quest_flow.py` extended to stub `window.Measure`, drive the symptom flow, and simulate a hidden tab mid-card): `quest-symptom-picked`, `quest-cause-shown` and `quest-card-abandoned` all confirmed actually firing with correct data, not just present in source. Not verified: the events landing in the live Umami database (no credential in this sandbox). Separately, re-measured S1-S4's own premise against the real corpus rather than trusting the prior pass's hedge: all 114 `passes.sustain` strings are already 87-106 words (median 94), inside S2/S4's target range, with recovery language in 102 of 114 by a rough scan. The prose gap S1-S4 was filed to close is largely already closed by the concurrent Sustain rewrite; see the Workstream 3 section below for the full finding and the open question of whether S1's structured schema is still worth its 0.5-3.5 days. `ops/fingerprint_assets.py` rerun after the `quest.js` edit; `site/quest.html`, `site/sw.js`, `site/build-id.txt` all follow. Pushed after this line was written; commit hash and CI status recorded in `ops/NIGHTLY-LOG.md`.

Preflight fast clean (0 gates failed, 16 warnings, all sandbox-environment limitations or expected float-day noise). Page count 191, unchanged (no new page; `quest.html`'s one script-tag fingerprint is the only site page edit). GitHub: 8 open issues unchanged (all art-blocked or decision-labelled), 0 open PRs. All 51 test files (50 plus the new gate test), check_urls (188/188), audit_pages (0 findings), affiliate.py (162 documents), mobile npm test (4 suites), all clean.  
**Overall Status:** YELLOW  
**Production Confidence:** THE STRIPE-SIDE OUTAGE IS FIXED AND PHIL-VERIFIED: ALL SIX LIVE PAYMENT LINKS ARE REACTIVATED. SEPARATELY, THE DEPLOYED SITE'S FRESHNESS AGAINST THE REPOSITORY IS UNVERIFIED FROM THIS SANDBOX (NO EGRESS TO 6S-SUCCESS.COM), SO WHETHER IT STILL SERVES AN OLDER BUILD IS UNKNOWN RATHER THAN CONFIRMED EITHER WAY. THE DEPLOY MECHANISM ITSELF CHANGED 2026-09-01: PHIL INSTALLED AN SSH DEPLOY KEY ON THE VPS SO A SESSION HOLDING THE PRIVATE HALF CAN RUN `OPS/DEPLOY.PY` DIRECTLY, NO BROWSER REDEPLOY CLICK NEEDED ANY MORE. THIS SESSION IS NOT THAT SESSION: `PYTHON OPS/DEPLOY.PY --CHECK` REPORTS "NO DEPLOY KEY AT /ROOT/.SSH/6S_DEPLOY" HERE, SO IT STILL CANNOT DEPLOY, FOR A DIFFERENT REASON THAN BEFORE. TREAT "PAYMENT LINKS WORK, DEPLOY FRESHNESS UNKNOWN" AS THE OPERATING HEADLINE UNTIL A SESSION HOLDING THE DEPLOY KEY CONFIRMS DIRECTLY. SEE `RETRO-2026-08-30-CYCLE6.MD` FOR THE ORIGINAL OUTAGE FINDING AND `OWNER-ACTIONS.MD` ITEM 1B FOR THE SUPERSEDED REDEPLOY ACTION.  
**Data Confidence:** MEASURED FROM DISK AND GITHUB. NO UMAMI, SEARCH CONSOLE, LISTMONK, STRIPE OR MAIL CREDENTIALS EXIST IN THIS OPERATOR SANDBOX, SO NONE OF THEM CAN BE PULLED LIVE THIS SESSION. THE ONE REVENUE FIGURE BELOW IS FROM `ROADMAP-2026-2029.MD`'S RECORDED MEASUREMENT, NOT A LIVE PULL. TRAFFIC IS THE ONE EXCEPTION: PHIL'S OWN SESSION READ THE ANALYTICS DATABASE DIRECTLY (THE API TOKEN IS EXPIRED) AND RECORDED REAL NUMBERS IN `GOALS.MD` (2026-09-02, CORRECTED 2026-09-03 AFTER THE FIRST READ CONFLATED VISITOR WITH SESSION, RE-MEASURED 2026-09-07: 60 VISITORS / 161 VISITS / 30 DAYS, 21 SESSIONS / 7 DAYS, 2 ORGANIC AS OF 2026-09-05, ONE BING ONE GOOGLE). THAT WAS A ONE-TIME MANUAL PULL, NOT A LIVE FEED THIS SANDBOX CAN REFRESH.

> Live figures are generated, not typed. See `EXECUTIVE-DASHBOARD-LIVE.md` and
> `ops/dashboard.html`, produced by `ops/dashboard.py`. Re-run that script rather
> than editing numbers by hand.

**Why this was RED, and why it is YELLOW now:** found 2026-08-30 by this
operator running eight parallel specialist audits at Phil's request,
confirmed four independent ways: all six of the live site's payment
links had been deactivated in Stripe for at least three days, and nobody
knew, because a deactivated Stripe Payment Link still returns HTTP 200 and
serves the same JavaScript shell as a working one, resolving to "no longer
active" only once a browser actually runs it. `check_sellable.py` checks the
repository, where the links were correct, which is exactly what made the
outage invisible to every prior check. It stayed open for eight days across
many credential-less cloud cycles because closing it needed a session with
real Stripe access, which this sandbox does not have.

**RESOLVED 2026-08-31, by Phil directly.** All six payment links reactivated
in Stripe and verified working in a real browser (`b0e9462`); the same
measurement that reported the outage RED for eight days now reports the site
can take money again, and the generated dashboard headline moved from RED to
YELLOW on that basis (`84c04cc`). This is Phil's own verified fix, not this
operator's; recorded here because a stale RED status describing a resolved
outage would itself be a false claim.

**Still open, and why the status is YELLOW rather than GREEN:** deploy
freshness against the repository is unverified from this sandbox (no egress
to 6s-success.com, no deploy key here either), so whether production still
serves an older, narrower catalog at stale prices is unknown rather than
confirmed. The single outstanding action is a session with the VPS deploy
key running `ops/deploy.py`; nothing else in the repository can close it,
and this operator cannot make it. Separate from
both: the business has taken one payment, ever, $19 gross ($18.15 net), on
2026-08-21, for the Whole House Print Pack. That buyer was a personal
referral from Phil, not a stranger who found the site, so it is not evidence
the funnel converts. Twenty checkout sessions have existed in total; nineteen
expired without completing and one finished. Seven of the nineteen were quoted
$18.00, a price that never existed in the catalog: BK-EB carried a duplicate
Stripe product with a second live payment link at $18 while the page
advertised $9.99, archived 2026-09-06. A third of every checkout this business
has ever had was quoted a price we do not charge, a better explanation for the
abandonment than anything about the funnel (`ROADMAP-2026-2029.md`, corrected
2026-09-07). The catalog can serve 158 of 159
listed items (Stripe Payment Links or real free downloads) once the
redeployed build is live; only Corporate Lean 6S still cannot be bought. The
email list is 0: Listmonk exists but shares a sending identity with a
different business (Compassion Benchmark), so every signup surface has been
deliberately withdrawn rather than mail customers under the wrong brand
(issue #15, P0). The real constraint now is that almost nobody is arriving at
the site: 60 visitors / 161 visits in the last 30 days, 21 sessions in the
last 7, and as of 2026-09-05, exactly two visits have ever come from a
search engine (one Bing, one Google), per Phil's direct database reads
recorded in `GOALS.md` (2026-09-02, corrected 2026-09-03 after the first
read conflated visitor with session, re-measured 2026-09-07). EXP-001 ("has a
stranger ever clicked a buy button") is answered, permanently: AMBIGUOUS. 9
buy-clicks from 7 visitors out of 52 ever (the 2026-09-03 count, when the
item closed), nothing distinguishing captured at
the time, so the nine can never be attributed to a stranger versus someone
Phil told directly (backlog item 1.3, closed 2026-09-03).

Status values:

- `GREEN` = operating normally
- `YELLOW` = degraded, uncertain, blocked, or requires attention
- `RED` = material failure or immediate risk
- `INITIALIZING` = system is still establishing authoritative state
- `UNKNOWN` = insufficient evidence

Never mark something GREEN merely because no problem has been reported.

---

# 2. Executive Snapshot

## Current Objective

The money path now works well enough to test. The constraint has moved again,
from "can a customer pay" to "can anything be measured, and has a stranger
ever converted". `ROADMAP-2026-2029.md` (written 2026-08-24) is the current
authoritative strategy; it supersedes `ROADMAP.md`, `STRATEGY.md` and
`GROWTH-PLAN.md` in spirit even though those files still exist on disk.
`BACKLOG-2026-H2.md` is the current authoritative work queue and supersedes
`BACKLOG.md` as a list of what to do next.

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

**The ordering rule in `BACKLOG-2026-H2.md`: measurement before traffic, traffic
before conversion, conversion before product.** Current state against each
epic:

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
manual click is no longer the mechanism. What has NOT been verified since:
whether any operator session has ever actually held the private half of that
key. Every sandboxed cycle since, this one included, reports "no deploy key
at /root/.ssh/6s_deploy," and no workflow in `.github/workflows/` runs
`ops/deploy.py`, so no automated pipeline exercises it either. Whether the
live site has been redeployed even once since 2026-09-01, by Phil's own hand
or otherwise, is genuinely unknown from here, not merely "not measured this
run." Treat deploy freshness as unconfirmed by design until either a session
holding the key checks directly or Phil confirms he deploys manually.

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
  added to three proxied locations) (2026-08-30, `RETRO-2026-08-30-cycle6.md`).
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

Do not infer production health from this template.

The `vps-docker-manager` and `devops-sre` should populate this section from actual production evidence.

| Area | Status | Evidence / Notes |
|---|---|---|
| Public website | UNKNOWN | Verify externally |
| Application/API | UNKNOWN | Inspect implemented architecture |
| Database | UNKNOWN | Identify authoritative production database |
| Reverse proxy | UNKNOWN | Inspect VPS |
| TLS/HTTPS | UNKNOWN | Verify certificate and renewal |
| Docker host | UNKNOWN | Inspect Hostinger VPS |
| Critical containers | UNKNOWN | Inventory required |
| Persistent volumes | UNKNOWN | Inventory required |
| Backups | UNKNOWN | Verify actual backup system |
| Restore readiness | UNKNOWN | Restore validation required |
| Disk capacity | UNKNOWN | Inspect host |
| Memory capacity | UNKNOWN | Inspect host |
| CPU health | UNKNOWN | Inspect host |
| Production logs | UNKNOWN | Identify sources and retention |
| Monitoring | UNKNOWN | Identify existing monitoring |
| Active incidents | UNKNOWN | Verify |

### Production Rule

Do not replace `UNKNOWN` with `GREEN` without evidence.

---

# 5. Production Release

**Currently Deployed Commit:** UNKNOWN  
**Release / Tag:** UNKNOWN  
**Deployment Timestamp:** UNKNOWN  
**Deployment Method:** UNKNOWN  
**Known-Good Rollback Release:** UNKNOWN  
**Runtime/Image Identity:** UNKNOWN

Owners:

- Release identity: `github-manager`
- Reliability/readiness: `devops-sre`
- Runtime deployment state: `vps-docker-manager`

The first production discovery cycle should reconcile:

**GitHub release → deployed artifact/image → running production**

---

# 6. GitHub Status

Owner: `github-manager`

| Area | Status | Notes |
|---|---|---|
| Repository identified | UNKNOWN | Confirm authoritative repository |
| Default branch | UNKNOWN | Inspect |
| Branch protections | UNKNOWN | Inspect |
| Open PRs | UNKNOWN | Inspect |
| Active branches | UNKNOWN | Inspect |
| CI health | UNKNOWN | Inspect GitHub Actions |
| Deployment workflow | UNKNOWN | Inspect |
| Security/dependency alerts | UNKNOWN | Inspect if available |
| Release convention | UNKNOWN | Establish or confirm |
| Production traceability | UNKNOWN | Map deployed version to Git |
| Repository hygiene | UNKNOWN | Initial audit required |

### GitHub Priority

Establish a trustworthy mapping between:

**work item → branch → PR → commit → release → production**

---

# 7. Hostinger VPS / Docker Status

Owner: `vps-docker-manager`

| Area | Status | Notes |
|---|---|---|
| VPS access | UNKNOWN | Confirm available authorized access |
| Host OS | UNKNOWN | Inspect |
| Docker Engine | UNKNOWN | Inspect |
| Docker Compose | UNKNOWN | Inspect |
| Compose projects | UNKNOWN | Inventory |
| Running containers | UNKNOWN | Inventory |
| Container health | UNKNOWN | Verify |
| Networks | UNKNOWN | Inventory |
| Volumes | UNKNOWN | Inventory before cleanup |
| Images | UNKNOWN | Inventory |
| Reverse proxy | UNKNOWN | Identify |
| Public ports | UNKNOWN | Inspect |
| Environment configuration | UNKNOWN | Map without exposing secrets |
| Log rotation | UNKNOWN | Verify |
| Backup jobs | UNKNOWN | Verify |
| Off-host backup | UNKNOWN | Verify |
| Restore procedure | UNKNOWN | Verify/document |

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

| Journey | Status | Notes |
|---|---|---|
| Homepage → useful next action | UNKNOWN | Verify |
| Room discovery | UNKNOWN | Verify implementation |
| Micro-zone discovery | UNKNOWN | Verify implementation |
| Personal Function Discovery | UNKNOWN | Determine current implementation |
| Root-cause guidance | UNKNOWN | Determine current implementation |
| Quest selection | UNKNOWN | Determine current implementation |
| Quest completion | UNKNOWN | Determine current implementation |
| Product discovery | UNKNOWN | Verify |
| Cart/checkout | UNKNOWN | Verify actual commerce implementation |
| Purchased content access | UNKNOWN | Verify if implemented |
| Mobile experience | UNKNOWN | Audit |
| Accessibility | UNKNOWN | Audit |

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
| Revenue | $19 gross / $18.15 net | Last 30 days | Same single transaction |
| Orders | 1 (20 checkout sessions started, 19 expired, 7 of those quoted a phantom $18 duplicate price archived 2026-09-06) | Since launch | MEASURED, same source |
| Average Order Value | UNKNOWN | Last 30 days | UNKNOWN |
| Refunds | UNKNOWN | Last 30 days | UNKNOWN |
| Sessions | 60 | Last 30 days | MEASURED 2026-09-07 by Phil (re-measured from an earlier 2026-09-02 pull that read 52), direct database read, recorded in `GOALS.md`; not a live pull, this sandbox cannot refresh it |
| Sessions | 21 | Last 7 days | Same source and same caveat |
| Organic sessions | 2, whole life of the site, as of 2026-09-05 (1 Bing, 1 Google) | Last 30 days | Same source and same caveat. Corrected 2026-09-09: this row said "1 from Bing, 0 from Google" for four days after `GOALS.md`'s own 2026-09-05 correction retired that claim. |
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

| Metric / Area | Status |
|---|---|
| Search Console connected | UNKNOWN |
| Indexed pages | UNKNOWN |
| Search impressions | UNKNOWN |
| Search clicks | UNKNOWN |
| Organic CTR | UNKNOWN |
| Top queries | UNKNOWN |
| Top landing pages | UNKNOWN |
| Technical SEO health | UNKNOWN |
| Structured data health | UNKNOWN |
| Sitemap health | UNKNOWN |
| Internal-link architecture | UNKNOWN |
| Room search architecture | UNKNOWN |
| Micro-zone search architecture | UNKNOWN |
| AEO/direct-answer coverage | UNKNOWN |

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
| Commerce platform | LARGELY LIVE | 158 of 159 catalog items take a card directly through a Stripe Payment Link, real downloads for free ones. Corporate Lean 6S is priced-per-engagement by design, not gapless: `site/corporate.html` (Phil, commit `9e7b1cd1`, 2026-09-03) gives it a qualified-enquiry buy path ending in a written scope and fixed fee, deliberately with no self-serve checkout since two engagements with the same headcount can be very different weeks of work. This row still read "no buy path" as of 2026-09-05, corrected here 2026-09-06 after `GOALS.md` and `REVENUE-REVIEW-2026-09-04.md` were found with the same stale claim. Catalog widened from 10 to 159 SKUs on 2026-08-27 when Phil wired the 149 generated zone/room/kit/bundle packs to live Stripe products himself (commit `b10a278`, backlog 5.7). |
| Payment provider | LIVE | Stripe, acct_1U5rDs6OlZmKL8mF, charges and payouts enabled since 2026-08-19. One real transaction cleared 2026-08-21 ($19, $18.15 net), a personal referral, not a stranger. MCP connection is read only; writes go through reviewed scripts (`ops/stripe_catalog.py`, `ops/stripe_setup.py`, `ops/stripe_links.py`). |
| Checkout health | UNVERIFIED THIS SESSION | `buy.stripe.com` is unreachable from this operator session's sandboxed network (still http_code 000 on re-test 2026-08-27), though issue #22 was closed 2026-08-25 after Phil's own session reached the live site directly. Egress is inconsistent across sessions, not uniformly fixed. One real order completing on 2026-08-21 is the strongest evidence checkout works end to end. |
| Product catalog | 158 of 159 SKUs buyable | Corporate Lean 6S is quote-per-engagement, not gapless: see the commerce platform row above. Card decks remain a separate, unresolved decision (issue #20). See `6S_SUCCESS_PRODUCT-CATALOG.md` and `PRODUCT-CATALOG.md`. |
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

Current production coverage is UNKNOWN until audited.

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

## BLOCKER-001: Production State Not Yet Verified

Impact:

Autonomous agents cannot safely assume production architecture, health, release identity, backup state, or rollback capability.

Owners:

- `vps-docker-manager`
- `devops-sre`
- `github-manager`

Resolution:

Perform read-only discovery first.

---

## BLOCKER-002: Live Business Data Not Yet Established

Impact:

Claude cannot responsibly optimize toward revenue/customer metrics without trusted measurement.

Owners:

- `analytics-intelligence`
- `commerce-manager`
- `seo-aeo`

Resolution:

Create metric definitions and data-source map, then connect authoritative sources.

---

## BLOCKER-003: Executive Dashboard Not Yet Established

Impact:

Owner lacks one trusted near-real-time view of business, product, growth, and production.

Owners:

- `analytics-intelligence`
- `6s-ceo`

Resolution:

Define `DASHBOARD.md`, then implement live dashboard.

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
**Status:** OPEN

Risk:

Autonomous agents may optimize vanity or incorrectly calculated metrics.

Control:

Create `METRICS.md` and `DATA-SOURCES.md`.

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

**Autonomous Execution Readiness:** FULL FOR GREEN-BAND WORK. AS OF 2026-08-26, MOST BUT NOT ALL EPIC 1-5 ITEMS ARE BLOCKED ON PHIL, A DECISION ISSUE, OR A MISSING CREDENTIAL: BACKLOG 5.6 (REBUILD THE QUEST AS THE PRIMARY WAY IN) HAD REAL UNBLOCKED WORK AND GOT A FIRST INCREMENT THIS CYCLE. CHECK BACKLOG-2026-H2.MD DIRECTLY RATHER THAN THIS LINE BEFORE ASSUMING NOTHING IS ACTIONABLE.

**Production Knowledge:** LAST VERIFIED LIVE 2026-08-19 (10/10 CHECKS). ISSUE #22 CLOSED 2026-08-25 AFTER PHIL'S OWN SESSION REACHED THE SITE DIRECTLY (181/181 INDEXNOW URLS ACCEPTED); THIS OPERATOR'S OWN SANDBOX STILL HAD NO EGRESS ON RE-TEST THE SAME DAY. TREAT EGRESS AS PER-SESSION, NOT UNIFORMLY RESTORED.

**Business Data Knowledge:** ONE MEASURED TRANSACTION EVER ($19 GROSS, 2026-08-21, A REFERRAL). CORRECTED 2026-09-02, RE-CORRECTED 2026-09-03, RE-MEASURED 2026-09-07: TRAFFIC IS NO LONGER UNREADABLE. THE UMAMI API TOKEN IS EXPIRED (401), BUT PHIL'S OWN SESSION READ THE DATABASE DIRECTLY AND GOT REAL NUMBERS, NOW THE BASELINE IN `GOALS.MD`: 60 VISITORS ACROSS 161 VISITS IN 30 DAYS, 21 SESSIONS IN THE LAST 7. THE EARLIER "47 SESSIONS" FIGURE WAS A VISITOR COUNT WEARING A SESSIONS LABEL, CORRECTED 2026-09-03; `SESSION_ID` IN UMAMI IS THE VISITOR AND PERSISTS ACROSS DAYS, THE VISIT IS `VISIT_ID`. AS OF 2026-09-05, TWO VISITS HAVE EVER CAME FROM A SEARCH ENGINE (ONE BING, ONE GOOGLE); THIS LINE SAID "ZERO FROM GOOGLE" FOR FOUR DAYS AFTER THAT STOPPED BEING TRUE. EMAIL-LIST DATA IS STILL UNREADABLE (LIST IS EMPTY, ISSUE #15 UNRESOLVED).

**Executive Visibility:** LIVE, VIA `EXECUTIVE-DASHBOARD-LIVE.md` (GENERATED BY `ops/dashboard.py`, NOT HAND-TYPED)

**Immediate Focus:** CORRECTED 2026-09-02, ANALYTICS IS NO LONGER THE BLOCKER. GOALS.MD NAMES THE REAL CONSTRAINT DIRECTLY: ALMOST NOBODY ARRIVES, AND THE CHANNELS THAT COULD CHANGE THAT (VIDEO PLATFORMS, LINKEDIN) NEED ACCOUNTS ONLY PHIL CAN CREATE (`OWNER-ACTIONS.MD`). WHAT IS NOT BLOCKED AND IS BEING WORKED: SEO (CHECKED 2026-09-02, TECHNICALLY CLEAN, SO THE ZERO-GOOGLE-VISITS FACT READS AS A NEW-DOMAIN COMPOUNDING PROBLEM, NOT A BUG), AND DISTRIBUTION PREP (114 ZONE VIDEOS IN BOTH 9:16 AND 16:9, PLUS PINTEREST/INSTAGRAM SAVE-AND-SHARE CARDS FOR ALL 114 ZONES AS OF 2026-09-02, READY TO POST THE MOMENT AN ACCOUNT EXISTS). THE HONEST STATE OF THIS BUSINESS IS "COMMERCE WORKS, TRAFFIC IS NOW MEASURED AND IT IS NEARLY ALL DIRECT OR LINKEDIN, AND THE NEXT STEP ON EVERY DISTRIBUTION CHANNEL IS PHIL'S OWN ACCOUNT CREATION."

---

# Final Rule

`STATUS.md` must describe reality, not aspiration.

If something is unknown, write `UNKNOWN`.

If something is degraded, write `YELLOW`.

If something is broken, write `RED`.

If something is healthy, prove it.

The purpose of this file is to let every autonomous agent answer:

**Where are we now, what matters most, and what should happen next?**
