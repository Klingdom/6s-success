# Home Quest: Cycle Plan

## Cycle 2026-09-02 (5B.11 first run)

**Selected bets:** see `OPPORTUNITY-BACKLOG.md`, items 1 to 3.

**Executed this cycle:**
1. Read `App.js`, `lib/pickCard.js`, `lib/importProgress.js`,
   `ON-DEVICE-TEST.md`, `docs/audit/CURRENT-STATE-AUDIT.md`, and
   `docs/product/PRD.md` to reconstruct current state honestly rather than
   assume it from prior log entries alone (Prompt 9 step 1).
2. Found a real coverage gap in `ON-DEVICE-TEST.md`: no check verified the
   2026-09-01 "Not now" fix on a device. Added checks 4 and 11, renumbered
   the file, updated the "what each check is for" section and the check
   count in the intro. Corrected the same stale count (still "12") in
   `OWNER-ACTIONS.md` and `APP-DEVELOPMENT-PLAN.md` after finding it named
   the count directly.
3. Built `lib/eventLog.js` (local-only diagnostic log, 300-entry cap) and
   `lib/eventLog.test.js` (7 tests), wired into `App.js` at every point
   something meaningful happens (card done, card skipped, zone finished,
   stopped, import ok/failed), exposed behind a new "Diagnostics" link.
   Verified: `npm test` (24 of 24 pass across 3 files), `npm install`
   (1,133 packages, matching the count prior cycles recorded),
   `EXPO_OFFLINE=1 npx expo export` for both platforms (551 iOS modules,
   1.75 MB; 550 Android modules, 1.76 MB), grep confirming no network call
   was introduced, `python ops/preflight.py` clean (10 standing warnings,
   same as before this cycle, no new ones).
4. Wrote this documentation set (`docs/future-state/`), Prompt 9's required
   output, for the first time.

**Not executed, and why:** no App.js parity feature work, per the
Opportunity Backlog's own deferral reasoning. No device testing was
attempted from this sandbox; it cannot be.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md`. If yes, read the results
   into `CURRENT-STATE-SCORECARD.md` and `LEARNING-LOG.md`, and decide
   whether to proceed to the recommendation-engine parity gap or fix
   whatever failed.
2. If not, do not re-attempt the on-device pass or nag; it is
   `OWNER-ACTIONS.md` item 2 and already ready. Look for the next real gap
   instead, the same way this cycle found the on-device script's own
   coverage hole.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

---

## Cycle 2026-09-03 (second run)

**Checked step 1 first, per the note above:** no evidence Phil has run
`ON-DEVICE-TEST.md` (no update to `OWNER-ACTIONS.md` item 2, no new commit
touching it, no message in the inbox agent). Did not re-attempt or nag. Read
`App.js`, `lib/*.js`, `ON-DEVICE-TEST.md`, `docs/audit/`, `docs/product/PRD.md`
and this cycle's own prior artifacts fresh, per step 1, before picking a bet.

**Quality/root-cause bet this cycle: verify the standing "12 contrast pairs
passing" claim by actually computing it, rather than carrying it forward.**
A source-level read (not a device test) of `App.js`'s colour tokens, using
the real WCAG relative-luminance formula against the real hex values, found
four of six pass-badge text colours below the 4.5:1 normal-text floor
(12px bold does not qualify for the 3:1 large-text exception the 2026-08-31
note had implicitly applied). Fixed with a new `BADGE_TEXT_COLOUR` mapping,
touching only the badge's text colour; the border and decorative dots keep
the original brand `PASS_COLOUR` values, which already clear the correct
3:1 non-text floor. Added `gate_mobile_badge_contrast` to
`ops/preflight.py`, proved to fail on a planted regression (reverted one
value, watched the gate name it, restored). Full account in
`LEARNING-LOG.md` L-APP-004 and `BACKLOG-2026-H2.md` 5B.9.

**Verified no regression:** `npm test` (24 of 24, unchanged), 1,133 packages
installed, `EXPO_OFFLINE=1 npx expo export` for both platforms (iOS 551
modules/1.75 MB, Android 550 modules/1.76 MB, identical to the prior
cycle's own figures), grep for network calls still zero,
`ops/tests/test_mobile_offline_and_a11y.py` and full `python ops/preflight.py`
both clean.

**Also checked and found clean, not just assumed:** corpus integrity
(114 zones, 684 cards, 20 rooms, correct S-order on all 114, 0 duplicate
card ids, computed directly from `quest-corpus.json`, not sampled). A full
third cold-read of `App.js`'s control logic (skip/mark-done/import/finish
state transitions) found no new functional defect of the "dead button"
shape the first two passes found; this is consistent with the prior
cycle's own note that the two-pass App.js sweep was reaching diminishing
returns, and this cycle's real finding was in a different layer (colour
tokens, not control logic).

**Not executed, and why:** the recommendation/audit-due engine and any
further App.js parity feature work, same deferral reasoning as the prior
cycle (`OPPORTUNITY-BACKLOG.md`): the PRD recommends waiting for the
on-device pass, still not done. No device testing attempted; it cannot be
from this sandbox.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet, per
   step 1 above; do not re-attempt or nag if not.
2. If still not, look for the next real gap the same way this cycle and the
   last one did (a fresh, skeptical read of one specific claim or one
   specific code path, not a repeat of the same sweep). Candidates not yet
   read closely: `lib/importProgress.js`'s merge behaviour against a
   corrupted or partial backup file (only well-formed fixtures are unit
   tested so far), and whether `docs/product/PRD.md`'s acceptance criteria
   still match what `App.js` actually implements now that Diagnostics and
   the badge-text fix exist.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.
