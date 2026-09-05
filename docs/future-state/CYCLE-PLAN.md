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

## Cycle 2026-09-05 (third run)

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged, no commit
touching the file, `git log` shows the last touch is the 5B.11 first-run
commit itself). Did not re-attempt or nag. Read `App.js`, `lib/*.js`,
`ON-DEVICE-TEST.md`, `docs/product/PRD.md`, and this file's own prior two
cycles fresh before picking a bet, per step 1.

**Quality/root-cause bet this cycle: the exact candidate the prior cycle
named (`OPPORTUNITY-BACKLOG.md` cycle 2 note) rather than a fresh sweep.**
`lib/importProgress.js`'s merge behaviour against a corrupted or partial
backup file, checked against the actual code rather than the 2.10 fix's
own claim to have covered it. Found the 2.10 fix only validated the
incoming side of the merge; the existing on-device/browser value was still
trusted. Reproduced in `node` before writing anything (a corrupted
existing value turned a perfectly valid incoming timestamp into `NaN`).
Fixed both `mergeDone()` and web `restore()` to validate the existing side
the same way the incoming side already is. Full account in
`OPPORTUNITY-BACKLOG.md`'s 2026-09-05 entry and `LEARNING-LOG.md` L-APP-005.

**Verified no regression:** `npm install` (1,133 packages, matching every
prior cycle), `npm test` (29 assertions across 3 files, was 27), two new
`lib/importProgress.test.js` cases proved to fail against the pre-fix code
before the fix and pass after, `EXPO_OFFLINE=1 npx expo export` for both
platforms (iOS 551 modules/1.75 MB, Android 550 modules/1.76 MB, both
identical to the last recorded figures), `python ops/preflight.py` and
`--deep` both clean (9 standing warnings, one fewer than the prior cycle's
own count only because the hooks-enabled warning was also cleared this
cycle), full `ops/tests/test_*.py` (23 files) individually, `check_urls.py`
(187/187), `audit_pages.py` (0 findings), `audit_catalog.py` clean,
`affiliate.py --check` clean (162 documents). Widened
`gate_quest_restore_validates_timestamps` in `ops/preflight.py` for the
web side (still no JS harness there), proved to fail on the pre-fix
`quest.js` in an isolated worktree and pass on the fix.

**Not executed, and why:** the recommendation/audit-due engine and any
further App.js feature parity work, same standing deferral: the PRD
recommends waiting for the on-device pass, still not done. No device
testing attempted; it cannot be from this sandbox. Did not re-check
`docs/product/PRD.md`'s acceptance criteria against `App.js` (the other
candidate this cycle could have picked); left for the next cycle rather
than opening a second workstream in the same pass.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet, per
   step 1 above; do not re-attempt or nag if not.
2. If still not, check whether `docs/product/PRD.md`'s acceptance criteria
   still match what `App.js` actually implements, now that Diagnostics,
   the badge-text fix and this cycle's merge fix all exist; that candidate
   was named two cycles running and not yet picked up.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

## Cycle 2026-09-05 (fourth run)

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged, no commit
touching `mobile/quest-app/ON-DEVICE-TEST.md` since the 5B.11 first-run
commit). Did not re-attempt or nag.

**Picked the exact candidate the second and third runs both named and
deferred: does `docs/product/PRD.md` still match what `App.js` actually
implements.** Read `App.js`, `lib/pickCard.js`, `lib/importProgress.js`,
`lib/eventLog.js`, `package.json`, `README.md`, `ON-DEVICE-TEST.md` and the
PRD fresh, side by side, rather than trust either document's word for the
other's state.

**Section 6's seven parity gaps (recommendation engine, mode selection,
photo capture, analytics, timer, progress map, first-run gate) are still
genuinely gaps, not overclaimed anywhere.** Grepped `App.js` and every
`lib/*.js` file for `computeRecommendation`, `nearestZone`, `heldZones`,
`daysSince`, `streak`, `Timer`, `Camera`, `ImagePicker` and `analytics`:
none exist on mobile (the web equivalents were confirmed to exist in
`site/assets/js/quest.js` for comparison). `pickCard.js` walks the corpus's
own `steps[]` order rather than a hand-maintained list, matching Section
5's own protection rule. No network call, no Stripe/IAP reference anywhere
in `App.js`, `lib/*.js` or `package.json`'s dependency list, matching
Section 5 item 5 and the README's "no network calls at all" claim exactly.
Per the PRD's own Section 6 closing note, none of these seven gaps should
be built before 5B.4 (device verification) closes, which it has not; not
attempted here for that reason, not because of sandbox limits.

**The one real finding: `README.md`'s "What it does today" list never
mentioned the Diagnostics feature**, live in `App.js` since the first
5B.11 run (2026-09-02) and documented in `ON-DEVICE-TEST.md`, but absent
from the file a developer reads first for current app behaviour. Not a
functional defect, a documentation gap of exactly the shape CLAUDE.md's
definition of done names. Fixed: added a bullet describing the local-only
diagnostic log, its storage key, and that it is never sent anywhere,
cross-referencing `ON-DEVICE-TEST.md`.

**Verified no regression:** `npm test` (29 assertions across 3 files,
unchanged), `python ops/preflight.py` clean. No corpus, code or test file
touched, so `expo export` figures are unchanged from the third run's own
recorded counts (not rerun, since nothing that export depends on changed).

**Not executed, and why:** no App.js parity feature work, same standing
deferral (waiting on 5B.4). No device testing attempted; it cannot be from
this sandbox.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet, per
   step 1 above; do not re-attempt or nag if not.
2. If still not, the PRD/App.js cross-check candidate is now closed for
   this pass; look for the next real gap via a fresh angle (a cold read of
   `lib/eventLog.js`'s own edge cases, or `ON-DEVICE-TEST.md`'s checks
   against the exact current button labels and screens in `App.js`, not
   yet done since Diagnostics landed).
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

## Cycle 2026-09-05 (fifth run)

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged, no commit
touching `mobile/quest-app/ON-DEVICE-TEST.md` since the 5B.11 first-run
commit). Did not re-attempt or nag.

**Picked the exact candidate the fourth run named: `ON-DEVICE-TEST.md`'s
checks against the exact current button labels and screens in `App.js`.**
Read every one of the eleven checks side by side with the current
`App.js` source rather than trust the fourth run's own PRD cross-check as
proof the two still agree line by line. Ten of eleven checks match the
source exactly, including the accessibility labels check 10 and 11 name.

**The one real finding, and it needed more than a side-by-side read to
surface: check 6's exact expected text, "1 of 114 zones in the house is
holding.", is not what the app actually renders.** The line was written
across two JSX lines, text ending "...zones in the house" then a new line
starting `{zonesHeld === 1 ? "is" : "are"}`. A source read alone looks
correctly spaced; transpiling the exact source with `@babel/preset-react`
(installed standalone in a scratch directory, not added to the project)
showed the real compiled children array: `[..., "zones in the house",
"is", " holding."]`, three adjacent entries with no separator between the
first two. Babel's JSX whitespace rule only collapses a line break to a
single space when both sides are plain text; a whitespace-only line
between a text node and a `{}` expression is dropped entirely. The two
other multi-line `<Text>` blocks in the file were checked the same way
and are fine, because their line breaks fall between two plain-text
segments or the space is already embedded inside a string literal.

**Fixed** by pulling the sentence into a new pure function,
`lib/format.js`'s `zonesHoldingLine(zonesHeld, zoneCount)`, called from a
single `{}` expression in `App.js` instead of relying on JSX line-break
whitespace at all. Four new cases in `lib/format.test.js`, wired into
`npm test`. New `gate_mobile_no_bare_jsx_text_expr_break` in
`ops/preflight.py`: a regex heuristic (no JS parser dependency) that
flags a line ending in ordinary text immediately followed by a line
starting with `{` anywhere in `mobile/quest-app/*.js`. Proved it fails by
planting the exact original two-line pattern back into an isolated copy
of `App.js` and watching it name the file and line, then confirmed clean
on the real fixed tree.

**Verified:** `npm test` (33 assertions across 4 files, was 29), `npm
install` (1,133 packages, matching every prior cycle), `EXPO_OFFLINE=1
npx expo export` both platforms (iOS 552 modules/1.75 MB, Android 551
modules/1.76 MB, both exactly +1 module from the last recorded figures,
the new `lib/format.js` import and nothing else), `python
ops/preflight.py` and `--deep` both clean (9-10 standing warnings, no new
ones). Full account in `LEARNING-LOG.md` L-APP-006.

**Not executed, and why:** the recommendation/audit-due engine and any
further App.js feature parity work, same standing deferral: the PRD
recommends waiting for the on-device pass, still not done. No device
testing attempted; it cannot be from this sandbox.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet,
   per step 1 above; do not re-attempt or nag if not.
2. If still not, finish the `ON-DEVICE-TEST.md`-vs-`App.js` cross-check
   this run started: checks 12 to 15 (the four extra checks) were read
   but not transpiled/verified as closely as check 6 was; worth the same
   scrutiny before assuming a side-by-side text match is a working match.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.
