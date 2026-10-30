# BACKLOG-2026-09-07.md closed-section archive

Numbered "## N. Closed/Done ..." sections older than ops/rotate_backlog_closed.py's retention window, moved here verbatim from BACKLOG-2026-09-07.md by that script. Never hand-edited. Newest first.

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
