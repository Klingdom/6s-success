# BACKLOG-2026-09-07.md closed-section archive

Numbered "## N. Closed/Done ..." sections older than ops/rotate_backlog_closed.py's retention window, moved here verbatim from BACKLOG-2026-09-07.md by that script. Never hand-edited. Newest first.

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
