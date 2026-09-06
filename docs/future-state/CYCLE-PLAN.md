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


## Cycle 2026-09-05 (sixth run)

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged; `git log` on the
file shows only the commits that created and renumbered it, none from
Phil running it). Did not re-attempt or nag.

**Picked the exact candidate the fifth run named: extend transpile-level
scrutiny to `ON-DEVICE-TEST.md` checks 12 to 15**, the four extra checks
the fifth run had only read side by side with `App.js`, not compiled.
Installed `@babel/core`/`@babel/preset-react` standalone in a scratch
directory again (not added to the project) and transpiled every
multi-line `<Text>` block feeding those four checks: the "Good stopping
point." screen body (check 14, `zonesHeld`/`CORPUS.zoneCount` followed by
"zones in the house holding." then a second sentence on its own line),
the persistent under-card footer carrying the same zones-holding count
(adjacent to checks 12/13's screen), the finished-zone note, and the
import-link text. All four compiled with the correct single space at
every join; none share check 6's shape (a text line ending in a plain
character immediately followed by a line starting with `{`). Read the
existing `gate_mobile_no_bare_jsx_text_expr_break` regex against the same
four blocks by hand: it agrees, correctly, that none of them match its
narrower flagged pattern.

**Check 13 (Dynamic Type) checked at the source level, the closest a
transpile can get without a device:** grepped every style and `<Text>` in
`App.js` for `numberOfLines`, `allowFontScaling`, `maxFontSizeMultiplier`,
fixed `width`, or `ellipsizeMode` on anything that holds copy or a button
label. None exist; only the six decorative finish-screen dots have a
fixed `height`/`width`, and they carry no text. This does not prove the
layout survives the largest system text size on a real screen (that is
what check 13 is for and only a device can settle it), but it rules out
the specific failure modes source code can cause by itself.

**Check 12 (web-to-mobile import via the on-device file picker) and check
13's actual runtime rendering remain genuinely device-only**, per
`ON-DEVICE-TEST.md`'s own "what each check is for" section; the import
message's string formatting (plain JS ternary/concatenation, not JSX) was
also transpiled and carries no whitespace-collapse risk of its own kind,
but confirming a real phone can open a real picked file is not something
this sandbox can do.

**The honest finding: none.** All four extra checks' underlying source is
now verified the same way check 6 was, not merely read, and none carry
the defect class that check 6 did.

**Verified:** `npm test` unchanged (33/33, no source touched), `python
ops/preflight.py`/`--deep` both clean (9-10 standing warnings, no new
ones), no file under `mobile/quest-app/` modified this cycle.

**Not executed, and why:** no App.js feature work; the on-device pass
itself is still the only way to settle checks 12 to 15's actual runtime
behaviour, and no evidence exists that Phil has run it yet.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet;
   do not re-attempt or nag if not.
2. If still not, the transpile-level source review of `App.js` and
   `ON-DEVICE-TEST.md` is now exhausted for this pass (all 15 checks
   cross-checked against source, two real bugs found and fixed across the
   fourth and fifth runs, the rest confirmed clean). A fresh angle worth
   trying next: read `lib/eventLog.js`'s diagnostics output format against
   what `ON-DEVICE-TEST.md`'s own "Diagnostics" section promises it shows,
   which has not been checked since the feature was built.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

## Cycle 2026-09-05 (seventh run): the diagnostics log's own unkept promise

**Picked the exact candidate the sixth run named:** read `lib/eventLog.js`'s
output against `ON-DEVICE-TEST.md`'s own Diagnostics section, which promises
the log records "cards drawn, done, skipped, zones finished, stops, and
import attempts." Grepped every `record(` call site in `App.js` rather than
trust the promise: `card_done`, `zone_finished`, `card_skipped`,
`import_ok`/`import_failed`, and `stopped` all exist. `card_drawn` does not,
anywhere. `App.js`'s own header comment (line 35) repeats the same six-item
promise, so this was not a stale doc drifting from working code; the code
never did what its own comment beside it says.

**Root cause:** `card` is a `useMemo` recomputed from `done`/`skipped`
regardless of which screen is on top of it. The finished-zone recap and the
stopping screen both render over it without a card visible underneath, so
`card` being non-null was never the same fact as a card being drawn onto the
screen, and nothing distinguished the two.

**Fixed:** `isCardVisible(finished, idle, card)` in `lib/pickCard.js`, pure
and unit-tested (4 new assertions), and a `useEffect` in `App.js` recording
`card_drawn` exactly on the transition to visible, including a card
reappearing after the recap or stopping screen closes. New
`gate_mobile_diagnostics_promise_kept` in `ops/preflight.py`: greps `App.js`
for a `record()` call covering each of the six promised categories, proved
to fail in an isolated worktree with the fix's own line swapped for a
comment (the exact planted regression), then restored and reran clean.

**Verified:** `npm test` 34/34 (was 33). Transpiled the changed `App.js`
with the same standalone Babel setup prior runs used and read the compiled
hook back to confirm it matches source. `npm install` (1,133 packages) then
`EXPO_OFFLINE=1 npx expo export` both platforms, no bundler error.

**A measurement caveat worth recording rather than ignoring:** exported
twice more in the same session to compare module counts against the fix,
once with the pre-fix code and a cleared cache (547 iOS / 551 Android) and
once with the fix (552 / 551). A bare one-file addition should not move the
iOS count by 5, and re-exporting the *same* pre-fix source with a warm vs.
cleared cache already produced two different counts on its own (545 vs
547) before the fix was even involved. Metro's per-export module count is
not a stable signal in this sandbox across cache states; treated the clean
export and the correct transpiled output as the real verification instead,
not the raw number. Not filed as a new gate: this is a measurement-noise
finding about the tooling, not a defect in the app.

**Not executed, and why:** no evidence Phil has run `ON-DEVICE-TEST.md`;
per the standing rule, did not nag. The log's own real value (sensible
`card_drawn` counts on an actual install) is still device-only.

**Next cycle should:** re-run Prompt 9 per its own instruction first; if
`ON-DEVICE-TEST.md` still shows no evidence of a device pass, the
diagnostics-promise angle is now closed (all six categories verified
against source). A fresh angle worth trying: `docs/product/PRD.md`'s
Section 5 "protected properties" list against `App.js` again, since it was
last checked in the fourth run before this cycle's two `App.js` edits.

## Cycle 2026-09-05 (eighth run): the deep-linking gap neither planning document disclosed

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged; no new commit
touching the file). Did not re-attempt or nag.

**Picked the exact candidate the seventh run named: `docs/product/PRD.md`
Section 5's ten protected properties against current `App.js`.** Nine of
ten hold with no change needed. Item 4, "deep-linking straight into a zone
or room," is named a property the port must protect in both the PRD and
`docs/audit/CURRENT-STATE-AUDIT.md`'s "ten strongest parts" list, the exact
same framing given to the recommendation engine and analytics, both of
which are correctly tracked as gaps in their respective build-order lists.
Deep-linking was not, in either document. Grepped `App.js`, every
`lib/*.js` file and the Expo config for `Linking`, `scheme`, `initialUR`,
`expo-linking` and any URL/query-param parsing before treating the
documents' silence as a defect rather than shorthand: zero matches, so the
gap is real.

**Fixed both planning documents, not code.** Added it as gap 8 in the
PRD's Section 6 build order (appended last, not by priority, to avoid
renumbering gaps 1 through 5 already cited by number elsewhere in the
PRD) and as item 7 in the audit's own gap list (renumbering the two
non-code items after it). Cross-referenced from PRD Section 5 item 4. No
feature built: Section 6's sequencing rule holds every gap, this one
included, until 5B.4 clears.

**Verified:** re-checked every numeric cross-reference to the renumbered
audit items and the PRD's gap numbers for breakage; none found. `npm test`
unchanged (34/34), `python ops/preflight.py`/`--deep` both clean, no new
warnings (no `mobile/quest-app/**` or `ops/**` file changed).

**Went well:** re-deriving all ten Section 5 items against source instead
of only the one the seventh run flagged, which is what surfaced this.

**Did not go well:** same unrelated-history checkout shape; issue #27
still open.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet,
   per step 1 above; do not re-attempt or nag if not.
2. If still not, the PRD/audit protected-properties cross-check is now
   closed for this pass (all ten items verified against source). A fresh
   angle worth trying: whether `ON-DEVICE-TEST.md`'s own checks still
   correctly describe the Diagnostics screen's `showDiag`/`formatForDisplay`
   output format now that `card_drawn` entries exist in it, not checked
   since the seventh run added them.
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

## Cycle 2026-09-05 (ninth run): Diagnostics screen against ON-DEVICE-TEST.md, no defect

**Checked step 1 first, per the standing rule:** no evidence Phil has run
`ON-DEVICE-TEST.md` (`OWNER-ACTIONS.md` item 2 unchanged; no commit touching
the file since the 5B.11 first-run commit). Did not re-attempt or nag.

**Picked the exact candidate the eighth run named: whether the Diagnostics
screen's actual output still matches `ON-DEVICE-TEST.md`'s own description,
now that `card_drawn` exists.** Read `lib/eventLog.js`'s `formatForDisplay()`
against the doc's Diagnostics section line by line rather than trust the
seventh run's own record-call check as proof the display side agrees too.
`formatForDisplay()` builds its type-count summary and recent-entries list
generically from whatever is in the log (`Object.keys(sum.byType)`), so it
never hardcodes the six categories and needed no change when `card_drawn`
was added; confirmed by reading the function itself rather than assuming a
generic implementation is automatically correct. Cross-checked three
adjacent claims the doc's wording implies: the Diagnostics toggle's actual
screen reachability (only rendered on the main card screen, `App.js` lines
390 to 401, not on the finished-zone recap or "Good stopping point." screens
that sit in front of it), which matches the doc's own instruction to check
it "after running the checks above" from a card screen, not mid-sequence;
`isCardVisible()` in `lib/pickCard.js`, the function the `card_drawn`
`useEffect` depends on, reads correctly against its own one-line contract;
and `mobile/quest-app/package.json`'s `test` script includes all four
`lib/*.test.js` files present on disk, so `gate_mobile_npm_test_complete`
has nothing to catch here.

**The honest finding: none.** The Diagnostics display path, its reachability,
and the visibility logic feeding it are all correct against the doc's
description.

**Verified:** no file under `mobile/quest-app/` modified this cycle;
`npm test` unchanged (34/34); `python ops/preflight.py`/`--deep` both clean,
10 standing warnings, no new ones.

**Also checked, and deliberately not acted on:** `gate_mobile_no_bare_jsx_text_expr_break`'s
regex only recognises ASCII sentence-ending punctuation before treating a
line as JSX text, and drops a text/expression pair entirely if a blank line
sits between them. Grepped the whole `mobile/quest-app` tree for curly
quotes or em/en dashes inside JSX text: zero hits, and no blank-line-then-`{}`
pattern exists anywhere either. Both are real latent narrowness in the
checker, not an observed defect, and CLAUDE.md 5c's own rule (a count is not
a finding until read) cuts the other way here too: broadening a regex with
no live case behind it is exactly the "manufacture a finding to justify the
read" shape the eighth run's own retro named as the wrong instinct. Left
alone; worth revisiting only if the site's copy source ever starts
producing curly punctuation (it does not today; `content.json` and the
corpus are plain ASCII prose).

**Not executed, and why:** the recommendation/audit-due engine and any
further App.js feature parity work, same standing deferral: the PRD
recommends waiting for the on-device pass, still not done. No device
testing attempted; it cannot be from this sandbox.

**The Diagnostics-vs-doc check itself found no defect, but following its own
"fresh angle" suggestion in the same cycle did.** Rather than stop at the
clean result and defer the next candidate to a tenth run, used the
remaining cycle to read `site/assets/js/quest.js`'s `restore()` against
`lib/importProgress.js`'s `mergeDone()` side by side for a behavioural gap,
since the 2.10 fix and its correction had fixed the same bug class in both
files without checking whether the two stayed equivalent afterward.

**Found: `mergeDone()` alone is not safe against a corrupted incoming value; `restore()` is.**
`restore()` validates both the incoming and existing timestamp inline,
inside the one function that merges them. `mergeDone()`'s existing-value
validation lives in the function itself, but its incoming-value validation
had been moved into a separate function, `parseBackup()`, that happens to
be `mergeDone()`'s only real caller today. Reproduced in `node` before
writing anything: `mergeDone({ "A|Z|sort": 1700000000000 }, { "A|Z|sort": "corrupted" })`
returns `{"A|Z|sort": null}`, the identical NaN/silent-erasure shape as both
prior rounds of this bug, this time reachable only by calling `mergeDone`
directly and skipping `parseBackup`. Confirmed the one live call site
(`App.js`'s `importBackup()`) always calls `parseBackup()` first, so this
was never reachable in the shipped app; not a live defect, a latent gap in
the function's own self-defence that its docstring's "same rule as
`restore()`" claim did not actually hold.

**Fixed:** added a shared `sanitizeTimestamp()` helper and applied it to
both sides inside `mergeDone()`, making it self-contained regardless of
caller, matching `restore()`. Reproduced the failure against the pre-fix
code in an isolated worktree (test failed with `actual: NaN, expected:
1700000000000`), then restored and confirmed the fix passes. Two new cases
in `lib/importProgress.test.js` call `mergeDone()` directly, bypassing
`parseBackup`, with a corrupted and a negative incoming value. No new
preflight gate needed: `gate_mobile_js_tests` already runs every
`lib/*.test.js` file and fails on any nonzero exit, so these cases are
already load-bearing. Full account in `LEARNING-LOG.md` L-APP-009.

**Verified:** `npm test` 36/36 (was 34, two new cases), `npm install` (1,134
packages), `EXPO_OFFLINE=1 npx expo export` both platforms (552 iOS/551
Android, unchanged from the last recorded figures, confirming the fix added
no new module), `python ops/preflight.py`/`--deep` both clean (9 standing
warnings, `hooks-enabled` cleared this cycle), `check_urls.py` (187/187),
`audit_pages.py` (0 findings), `affiliate.py --check` (162 documents).

**Went well:** not stopping at a clean verification result when the same
cycle's own remaining budget could chase the next candidate it had just
named, and reproducing the exact failure in isolation before and after the
fix rather than trusting the read.

**Did not go well:** same unrelated-history checkout shape; issue #27 still
open. This is the third time `mergeDone()`/`restore()` has needed the same
class of fix; worth naming explicitly in the log as a pattern rather than
three unconnected findings.

**Next cycle should:**
1. Check whether Phil has run `ON-DEVICE-TEST.md` before picking a bet,
   per step 1 above; do not re-attempt or nag if not.
2. If still not, this file's merge/restore logic has now had three rounds
   of the same defect class fixed (existing-side twice, incoming-side once)
   across both platforms; a fresh angle worth trying next cycle, away from
   this file entirely: `docs/product/PRD.md` Section 6's build-order
   sequencing rule itself (whether every one of the now-eight gaps still
   correctly cites 5B.4 as its own gate, not assumed from the one gap
   checked when it was added).
3. Re-run this prompt (Prompt 9) at the start of the cycle, per its own
   instruction, before picking new bets.

## Cycle 2026-09-06 (tenth run): the citation drift the eighth run's own addition left behind

**Checked step 1 first, per the standing rule:** no commit touching
`ON-DEVICE-TEST.md` since the first 5B.11 run (`fe635125`); no evidence
Phil has run it. Did not re-attempt or nag.

**Picked the ninth run's own named next step:** re-checked every numeric
citation to `PRD.md` Section 6's parity gaps across the planning documents,
not only the one gap touched when gap 8 was added. Grepped for `gap [0-9]`,
`seven gaps` and `eight gaps` across `docs/` rather than re-reading only the
files the eighth run had touched.

**Found two real citation errors, both predating gap 8 and never caught by
the "re-read the full cross-reference chain" step every prior run in this
series performed:**
1. `PRD.md` Section 13 (the roadmap) still said "Section 6's seven gaps"
   and "none of the seven gaps," a live self-reference inside the same
   document whose own Section 6 has carried eight gaps since the eighth
   run, not a dated log line describing past state. Corrected to eight.
2. `OPPORTUNITY-BACKLOG.md` cited the recommendation engine as "parity gap
   8.1 in the PRD," a number that has never existed in `PRD.md`'s Section 6
   (checked against the original 2026-09-02 commit that introduced the
   line, `fe635125`: the recommendation engine was gap 1 from day one).
   Corrected to gap 1.

**One suspected third error, checked and found to be correct, not fixed:**
`CURRENT-STATE-AUDIT.md` line 188-191 cites the recommendation engine and
analytics as "item 8" and "item 9" while its own "largest verified gaps"
list numbers them 1 and 4. Nearly changed this before noticing the
sentence anchors to a different list in the same file, "ten strongest
parts that must survive the port," where they genuinely are items 8 and 9.
Left unchanged after re-reading both lists side by side.

**Verified:** re-grepped `docs/` for the same patterns after editing, no
remaining stale count found; `check_urls.py` (187/187), `audit_pages.py`
(0 findings), `affiliate.py --check` (162 documents), `python
ops/preflight.py` clean (9 warnings, same set as before this cycle, no new
ones) since nothing under `mobile/quest-app/**` or `ops/**` changed.

**Went well:** searching across all of `docs/` for the citation pattern
instead of re-reading only the file the triggering commit touched, which
is what surfaced the `OPPORTUNITY-BACKLOG.md` error nine runs missed.

**Did not go well:** nearly introduced a real regression by "fixing" the
`CURRENT-STATE-AUDIT.md` citation without first checking which of the
file's two numbered lists it anchored to; caught before committing, but a
lesson to record rather than a clean pass.

**Next cycle should:** the deep-linking build itself, and every other
Section 6 gap, stays correctly gated behind 5B.4 (device verification),
which has still not happened. With citation drift now checked across the
whole `docs/` tree rather than one file at a time, a fresh angle worth
trying next: whether `README.md`'s and `package.json`'s own claims (module
counts, dependency list, "no network calls") still match `App.js` after
the `sanitizeTimestamp()` change from the ninth run, the same drift class
this cycle just found, applied to code-vs-doc instead of doc-vs-doc.
