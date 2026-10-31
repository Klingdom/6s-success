# BACKLOG-2026-09-07.md closed-section archive

Numbered "## N. Closed/Done ..." sections older than ops/rotate_backlog_closed.py's retention window, moved here verbatim from BACKLOG-2026-09-07.md by that script. Never hand-edited. Newest first.

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
