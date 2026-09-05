# Home Quest: Opportunity Backlog

Written 2026-09-02, operator, Prompt 9 step 4. Scored on expected user
outcome, target-state gap closed, reach, confidence, effort, risk,
reversibility, and strategic fit. Safety, privacy, security and accessibility
defects override normal scoring, and none are open right now.

Selected this cycle (the prompt's own cap: one primary outcome bet, one
quality/root-cause bet, one learning/instrumentation bet):

## 1. Primary outcome bet: run the on-device test pass

**Problem statement and evidence:** the single largest gap
(`GAP-AND-ROOT-CAUSE-ANALYSIS.md`) is that nobody has opened the app on a
real phone. **Target user and moment:** Phil, once, for about ten minutes.
**Hypothesis:** the core loop works as unit-tested and the app is usable on a
real device; the fifteen checks in `ON-DEVICE-TEST.md` will mostly pass.
**Smallest credible change:** none needed on the code side; the script
already exists and is current as of this cycle. **Leading measure:** checks
completed. **Lagging measure:** checks passed vs failed. **Guardrails:** a
failed check is worth more than a pass, per the script's own closing note.
**Accessibility/privacy/security impact:** checks 10 and 11 cover
accessibility directly; nothing here touches privacy or security beyond what
is already true (no network calls). **Rollout:** this is a manual pass, not a
release. **Stop/rollback/expand/remove criteria:** if checks 1 to 9 fail,
stop building anything further on this app until the core loop itself is
fixed and re-verified; if they pass, proceed to closing the platform-parity
gap (dimension 8). **Required tests/docs:** none further; `ON-DEVICE-TEST.md`
is the artifact. **Status:** ready, tracked as OWNER-ACTIONS.md item 2,
blocked only on Phil's device and time.

## 2. Quality/root-cause bet: close the on-device script's own coverage gap

**Problem statement:** `ON-DEVICE-TEST.md` tested the 2026-09-02 "Stop here"
fix but not the 2026-09-01 "Not now" fix, so a device pass could report
"all checks pass" while the first fixed bug was silently still broken (it is
not, per source and unit tests, but the script could not have caught a
regression). **Target:** the on-device script itself. **Hypothesis:** adding
a direct check for "Not now" changing the visible card closes that gap.
**Smallest credible change:** two new checks (primary check 4, accessibility
check 11), renumbering the rest; no app code changed. **Leading/lagging
measure:** the script now names 15 checks instead of 14, and check 4 exists.
**Guardrails:** none beyond correctness of the renumbering, checked by
re-reading the file after editing. **Status:** done this cycle. See
`mobile/quest-app/ON-DEVICE-TEST.md`.

## 3. Learning/instrumentation bet: a local, on-device diagnostic log

**Problem statement:** step 1 of this prompt requires validating
instrumentation before trusting it; until this cycle, the only evidence an
on-device pass could produce was Phil's memory of what he tapped, which is
User-reported evidence at best, not Observed fact. **Target:** the app
itself. **Hypothesis:** a small, local-only, timestamped event log
(card drawn/done/skipped, zone finished, stopped, import attempted) that
renders as plain text on screen turns a subjective "it worked" into a
checkable record, without adding any network call, account, or new
dependency. **Smallest credible change:** `lib/eventLog.js` (pure functions,
7 unit tests), wired into `App.js` at the six points where something
meaningful happens, exposed behind one new "Diagnostics" text link at the
bottom of the card screen, off by default. **Guardrails:** capped at 300
entries so it cannot grow without bound; verified by a dedicated test
(`the log never grows past MAX_EVENTS, oldest dropped first`).
**Accessibility/privacy/security impact:** text-only, `selectable`, no new
native module, no data leaves the device, nothing added to the offline
guarantee's surface area (verified: grep for network calls still returns
zero after this change). **Status:** built and tested this cycle; its own
value is unverified until an on-device pass actually uses it, which is
exactly what it exists to make more measurable next time. See
`mobile/quest-app/lib/eventLog.js`, `lib/eventLog.test.js`, and
`ON-DEVICE-TEST.md`'s new Diagnostics section.

## Cycle 2026-09-03: quality/root-cause bet, badge text contrast

**Problem statement and evidence:** the 2026-08-31 accessibility pass
recorded "all 12 contrast pairs measured and passing, weakest 3.04:1
against a 3.0 floor" (`BACKLOG-2026-H2.md` 5B.9). Recomputing directly from
`App.js`'s real colour values with the WCAG relative-luminance formula
found four of six pass-badge text colours below the 4.5:1 floor that
actually applies to 12px bold text (sort 3.35:1, safety 3.04:1,
standardize 4.01:1, sustain 3.09:1); the 3:1 floor the prior note used is
the large-text exception, and this text does not qualify for it.
**Target:** the badge that names the current pass, shown on every card
screen. **Hypothesis:** a separate, corrected text-colour mapping closes
the gap without touching the border or the decorative dots, which already
clear their own (correct, lower) 3:1 non-text floor.
**Smallest credible change:** `BADGE_TEXT_COLOUR` in `App.js`, four values
lightened along their own hue to clear 4.5:1 with margin; two left
unchanged because they already cleared it.
**Leading/lagging measure:** `gate_mobile_badge_contrast` in
`ops/preflight.py` computes the real ratio from source; passing is the
measure, not a one-time number.
**Guardrails:** the gate is proved to fail on a planted regression, not
merely present; the border and dots, which are correct as-is, were left
untouched so the visual identity by pass is unchanged.
**Accessibility/privacy/security impact:** accessibility only, and it is a
straight improvement; no privacy or security surface touched.
**Status:** done this cycle. See `BACKLOG-2026-H2.md` 5B.9,
`LEARNING-LOG.md` L-APP-004, `mobile/quest-app/App.js`.

## Cycle 2026-09-05: quality/root-cause bet, the other half of the restore fix

**Problem statement and evidence:** the prior cycle's own named next-step
list (this file, cycle 2 note) pointed at "`lib/importProgress.js`'s merge
behaviour against a corrupted or partial backup file (only well-formed
fixtures are unit tested so far)." Reading `mergeDone()` and web
`restore()` against that question directly, rather than trusting the
2026-09-03 fix (`BACKLOG-2026-H2.md` 2.10) to have closed it: that fix's
own commit message says it checked "either side" of the merge, but the
code only ever validated the incoming value. The value already in
`existingDone`/`state.done` was still trusted unvalidated, and
`Math.min(a, b)` with a corrupted `a` produces `NaN` exactly as it does
with a corrupted `b`, reproduced directly in `node` before writing the fix.
**Target:** anyone restoring a Quest backup on a device or browser whose
own stored progress already carries a corrupted value for some card (from
a hand-edited store, or a value written by a bug that predates either
fix). **Hypothesis:** validating the existing side the same way the
incoming side is already validated closes the remaining half of the same
failure mode, with no change to normal restores.
**Smallest credible change:** in `mergeDone()`, derive a sanitised `a` from
`existingDone[k]` (finite, positive number, else `undefined`) before using
it in the merge; same pattern in web `restore()` for `state.done[k]`.
**Leading/lagging measure:** two new cases in
`lib/importProgress.test.js` (`gate_mobile_js_tests` runs them); a second
`fail()` branch added to `gate_quest_restore_validates_timestamps` in
`ops/preflight.py` for the web side, which has no JS harness.
**Guardrails:** both new checks proved to fail on the pre-fix code (the
node reproduction for the mobile side; the gate run against an isolated
worktree at the pre-fix commit for the web side) and pass on the fix,
restored clean. `npm test` (29 assertions, was 27), `EXPO_OFFLINE=1 npx
expo export` for both platforms (551 iOS/550 Android modules, unchanged
from the last recorded figures) and the full `ops/tests/test_*.py` suite
(23 files) all verified after.
**Accessibility/privacy/security impact:** none; this is data-integrity
only, and it only ever makes a merge more conservative (falls back to
whichever side is actually a valid timestamp) than before.
**Status:** done this cycle. See `BACKLOG-2026-H2.md` 2.10 correction,
`LEARNING-LOG.md` L-APP-005, `mobile/quest-app/lib/importProgress.js`,
`site/assets/js/quest.js`, `ops/preflight.py`.

## Deferred, not selected this cycle, and why

- **Recommendation/audit-due engine (parity gap 8.1 in the PRD).** Highest
  standalone value of the remaining parity gaps, but the PRD's own
  recommendation (ratified again in `GAP-AND-ROOT-CAUSE-ANALYSIS.md`) is to
  wait for the on-device pass first. Building it now would risk a second
  round of rework if the on-device pass surfaces a core-loop problem.
- **A third cold-read pass of `App.js` for more bugs.** Two passes have each
  found one real bug; this cycle's read found no new App.js-level defect
  (the gap found was in the on-device script, not the app). Diminishing
  returns judged likely; the on-device pass itself is now the better place
  to find the next real defect.
- **5B.6 to 5B.8, 5B.10 (production builds, household features, store
  submission).** All explicitly blocked on accounts only Phil can create.
  No operator action closes these; tracked in `OWNER-ACTIONS.md`.
