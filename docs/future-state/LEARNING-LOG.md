# Home Quest: Learning Log

Format matches `LEARNINGS.md`: observation, evidence, confidence,
implication, next action. App-specific learnings live here so Prompt 9 cycles
do not have to search the whole-business log for the subset that applies to
the app.

## L-APP-001: A control's accessibility label and its actual behaviour can drift apart silently

**Observation:** twice in three days, a button in `App.js` had a correct
label, a correct-looking position, and a broken `onPress` handler: "Not now"
did nothing (2026-08-31/09-01), and "Stop here, this counts" did the same
thing as "Draw the next card" (2026-09-02).
**Evidence:** both confirmed by tracing the exact render path and `onPress`
body, not by assumption; both fixed with a unit test proving the new
behaviour, and a preflight gate proving the old bug shape fails.
**Confidence:** high; this is an observed fact, not inference, for both
instances.
**Implication:** a source read that checks labels, roles, and hints (the
accessibility pass done 2026-08-31) is necessary but not sufficient. It can
confirm a screen reader will announce a button correctly while missing that
pressing it does nothing.
**Next action:** when adding or reviewing a `Pressable`, read its `onPress`
body line by line and ask what state it changes, not just whether it has an
`accessibilityLabel`. Applied this cycle: read every `onPress` in `App.js`
again before adding the Diagnostics button; found no new instance of this
pattern.

## L-APP-002: An on-device test script can go stale the same way a preflight gate can

**Observation:** `ON-DEVICE-TEST.md` was written to prove the "Stop here"
fix (checks 13 and 14, since renumbered 14 and 15) but was never updated
after the earlier "Not now" fix landed a day before it, so the script's own
coverage silently fell behind the code it was meant to verify.
**Evidence:** read the file directly, confirmed no check exercises pressing
"Not now" and observing a different card.
**Confidence:** high, observed fact.
**Implication:** a test script is also an artifact that needs the same
"proven, not assumed current" discipline this project already applies to
preflight gates and generators. Fixing a bug and writing a unit test for it
is not the same as updating the human-run verification script that a
non-engineer will actually execute.
**Next action:** whenever an `App.js` control's behaviour is fixed, check
`ON-DEVICE-TEST.md` for a corresponding on-device check in the same cycle,
not as a separate follow-up.

## L-APP-003: A local-only instrumentation log is possible without breaking the offline/no-network promise

**Observation:** it is possible to give an on-device tester a structured,
timestamped record of what happened without adding any network call,
account, or third-party SDK: `lib/eventLog.js` persists to the same
`AsyncStorage` the app already uses for progress, and renders as plain
selectable text.
**Evidence:** grep for network-call patterns across `mobile/quest-app/`
returns nothing before or after this change; the app still exports clean on
both platforms.
**Confidence:** high, observed fact.
**Implication:** "no telemetry" and "no way to verify what happened" are not
the same constraint. A future feature that seems to require network access
for measurement should be checked against this pattern first.
**Next action:** if EXP-APP-002 shows Phil's on-device report is genuinely
better with the log than without, keep extending this pattern rather than
reaching for a network-based analytics SDK, which the product's own
principles rule out anyway without a real privacy decision first.

## L-APP-004: "Measured and passing" is not the same claim as "checked against the right floor, by a gate that can fail"

**Observation:** the 2026-08-31 accessibility pass recorded "all 12 contrast
pairs measured and passing, weakest 3.04:1 against a 3.0 floor" in
`BACKLOG-2026-H2.md`. That number was a real, honestly measured ratio, but
the floor it was checked against was wrong: WCAG's 3:1 exception is for
large text (14pt/~18.7px bold or bigger), and the pass badge's text is 12px
bold, so the correct floor was 4.5:1. Four of six values were actually
below it. No repeatable check enforced either floor; the claim was a
one-time manual calculation that nothing re-verified on the next colour
change.
**Evidence:** recomputed directly from `App.js`'s real hex values with the
WCAG relative-luminance formula, 2026-09-03; `ops/tests/test_mobile_offline_and_a11y.py`,
the only automated mobile a11y check that existed, does not compute
contrast at all (confirmed by reading it), so "measured" had never meant
"gated."
**Confidence:** high, observed fact; the four ratios are reproducible from
the committed source.
**Implication:** this is the same shape as `CLAUDE.md` 5c ("do not report a
count as a finding") and 5d (verify a claim before acting on it), applied to
this project's own prior claim about itself, not an external audit. A
number being real and a number being checked against the correct rule are
two different properties, and a backlog note can assert both are true while
only the first one is.
**Next action:** any future "measured and passing" note for a numeric
threshold (contrast, size, timing, count) should name the actual rule it
was checked against, not just the observed number, and should get a gate
that recomputes it from source in the same cycle it is claimed done, not
as a follow-up. Applied this cycle: `gate_mobile_badge_contrast` computes
from `App.js` directly rather than trusting the corrected numbers to stay
correct.

## L-APP-005: a fix's own commit message can overclaim what it actually checked

**Observation:** the 2026-09-03 fix for the Quest restore/import merge
(`BACKLOG-2026-H2.md` 2.10) is titled and described as checking that
"either side" of a card's timestamp is a real number before merging with
`Math.min`. Reading the code directly rather than trusting the title: both
`lib/importProgress.js`'s `mergeDone()` and web `quest.js`'s `restore()`
only ever validated the incoming value. The value already stored on the
device or in the browser was still used unvalidated, and it is exactly as
able to turn `Math.min(a, b)` into `NaN` as a corrupted incoming value,
even when the incoming value is perfectly good.
**Evidence:** reproduced directly in `node` before writing anything:
`mergeDone({ "A|Z|sort": "corrupted-legacy-value" }, { "A|Z|sort":
1700000000000 })` returned `NaN` for a card whose incoming value was
completely valid. Not reachable from a fresh install (the app only ever
writes `Date.now()` into this store itself), but reachable from a
hand-edited local store or a value written by some earlier, since-fixed
bug, which is exactly the scenario a restore/import feature exists to be
resilient against.
**Confidence:** high, observed fact, reproduced twice (mobile via `node`,
web via a preflight gate run against an isolated worktree at the pre-fix
commit).
**Implication:** the same shape as L-APP-004, one layer removed: there a
real number was checked against the wrong rule, here a real fix checked
the wrong half of a two-sided condition, and its own description said
"both" while the code said "one." A prior cycle's fix having tests and a
gate is evidence the fix does what its tests and gate check, not evidence
it does what its own prose claims.
**Next action:** when a fix's own description uses a word like "either,"
"both," or "every," treat that as a claim to verify against the diff, not
a summary to carry forward; a symmetric-sounding bug (two sides of a
merge, two branches of a condition) is a natural place for a fix to
symmetrically address one half and describe both. Applied this cycle: the
second half fixed in both files, a new node-level reproduction and a
widened `gate_quest_restore_validates_timestamps` so a future edit cannot
silently drop either side's check again.

## L-APP-006: a JSX line break next to an expression can delete a space instead of collapsing it

**Observation:** the zone finish screen (`App.js`, shown every single time
a zone's six passes complete) wrote its summary line across two JSX lines:
a text node ending "...zones in the house" on one line, then
`{zonesHeld === 1 ? "is" : "are"}` starting the next. The intuition that a
line break in JSX "becomes a space" is only true when both sides of the
break are plain text; here the trailing segment (indentation before the
next `{`) is a whitespace-only line, and Babel's JSX child-trimming drops a
whitespace-only line entirely rather than condensing it to one space. The
compiled children array was `[..., "zones in the house", "is", "
holding."]`, three adjacent array entries with no separator between the
first two, so React Native rendered "1 of 114 zones in the houseis
holding." on the single screen a finished zone always lands on.
**Evidence:** reproduced by transpiling the exact JSX (and the two
sibling text blocks nearby) with `@babel/preset-react` in isolation and
reading the literal `children:` array Babel produced, not by guessing from
the whitespace rule's usual description. The two other multi-line `<Text>`
blocks in the same file were checked the same way and are fine, because
each already embeds its own explicit spaces inside the string literals on
either side of the line break (e.g. `"About "` + variable + `" for the
whole zone."`) rather than relying on a bare newline to supply one.
**Confidence:** high, observed fact from the actual compiler output, not
inferred from source reading alone.
**Implication:** "the JSX renders roughly what it looks like" is not
reliable exactly at the boundary between a text node and an expression
container split across lines; a source-only review (the kind every prior
`App.js` cycle already did) can look at this pattern and see correctly
spaced words without noticing the compiler disagrees. `ON-DEVICE-TEST.md`
check 6 already names the exact expected sentence, but nobody had run the
on-device pass yet, so this stayed invisible from source review alone
until this cycle transpiled the file directly instead of just reading it.
**Next action:** fixed by building the whole sentence as one JS string
inside a single `{}` expression (`lib/format.js`'s `zonesHoldingLine()`)
instead of relying on JSX's own line-break whitespace behaviour, and
pulled it out where `lib/pickCard.js` and `lib/importProgress.js` already
put similar pure logic, so it is unit tested with plain node
(`lib/format.test.js`, wired into `npm test`). When a future review meets
another multi-line `<Text>` block whose line break sits directly next to
`{}` rather than between two plain-text segments, transpile it rather than
eyeball it; source reading missed this one for at least three prior
cycles that read this exact file closely.

## L-APP-007: a feature's own comment can describe a promise the feature does not keep

**Observation:** `ON-DEVICE-TEST.md`'s Diagnostics section and `App.js`'s
own `DIAG_KEY` comment (written together, same commit, 2026-09-02) both say
the local event log records "cards drawn, done, skipped, zones finished,
stops, and import attempts." `App.js` calls `record()` for five of those
six: `card_done`, `card_skipped`, `zone_finished`, `stopped`,
`import_ok`/`import_failed`. Nothing ever called it for a card being drawn.
**Evidence:** grepped every `record(` call site in `App.js` directly rather
than trust either piece of prose describing the feature; found the gap by
absence, then confirmed by reading `card`'s own `useMemo` (recomputes from
`done`/`skipped` regardless of which screen is showing) that no code path
existed which could have logged it even accidentally.
**Confidence:** high, a direct source read of every call site of the
relevant function, not an inference from the doc or the comment.
**Implication:** a promise written correctly and reused consistently in two
places (the user-facing doc and the code's own comment) is still just a
claim until something checks the implementation against it; two matching
descriptions of a feature are not two independent pieces of evidence that
it works; they can both be transcriptions of the same original intention
that was never fully built. This is the same shape as L-APP-004 ("measured
and passing" is not "checked against the right floor by a gate that can
fail") one layer up: a specific, enumerable promise about what a feature
does belongs in a gate the moment it is specific enough to check by string
search, not only in the paragraph that stated it.
**Next action:** fixed by adding `isCardVisible()` to `lib/pickCard.js` and
wiring a `card_drawn` record into `App.js` at the point a card actually
becomes visible (not merely computed). New `gate_mobile_diagnostics_promise_kept`
in `ops/preflight.py` greps `App.js` for a `record()` call covering each of
the six promised categories, so a future edit that silently drops one of
them fails preflight instead of waiting for someone to reread the
Diagnostics section against the source by hand again. When a doc and a code
comment both enumerate specific things a feature does, check the list
against the implementation once and gate it, rather than trusting that two
matching descriptions make it true.

## L-APP-008: a planning document can name a property to protect and then quietly drop it from its own gap list

**Observation:** `docs/audit/CURRENT-STATE-AUDIT.md`'s "ten strongest parts
that must survive the port" and `docs/product/PRD.md` Section 5 both list
"deep-linking straight into a zone or room" as a web property mobile must
not lose. Neither document's actual gap-tracking list (the audit's "largest
verified gaps," the PRD's Section 6 build order) ever mentioned it, even
though the two sibling items with the exact same shape, currently a web-only
capability, protected by name, are both correctly listed as gaps (the
recommendation engine, analytics).
**Evidence:** grepped `App.js`, every `mobile/quest-app/lib/*.js` file and
the Expo config for `Linking`, `scheme`, `initialUR`, `expo-linking`, and
any URL/query-param parsing: zero matches. Not inferred from the documents'
silence; independently confirmed the capability does not exist before
treating its absence from the gap list as a documentation defect rather
than a documentation shorthand.
**Confidence:** high, direct grep of the only two documents that define the
gap set plus the only code that could implement it.
**Implication:** a "properties to protect" list and a "gaps to build" list
describe the same underlying facts from two directions, and nothing
mechanically keeps them in sync; a web-only capability can sit correctly
named as important in one list while silently missing from the other, and
because the missing one never causes a test failure or a runtime error,
nothing forces a re-read. This is a different shape from L-APP-007 (a
feature's comment overclaiming what code does): here neither document was
wrong about mobile's current state on its own, the drift was between two
documents that were each individually consistent internally.
**Next action:** fixed by adding it to both lists (PRD Section 6 gap 8,
audit item 7), appended rather than inserted by priority, to avoid
renumbering the gaps already cited by number elsewhere in the PRD. Not
gated: this is a one-off planning-document reconciliation, not a
recurring code-defect class with a mechanical check to write; if the same
shape (a "protect" list and a "build" list silently disagreeing) recurs a
third time across these documents, that would be the signal to write one.

## L-APP-009: splitting a self-contained validator into two functions can silently drop half its self-defence

**Observation:** `lib/importProgress.js`'s `mergeDone()` docstring claims
"same rule as quest.js's restore()," but `restore()` validates both the
incoming and the existing timestamp inline, inside the one function that
does the merge, while `mergeDone()` only validated the existing side
itself; the incoming side's validation had been moved into a different
function, `parseBackup()`, that happens to be the only thing that calls
`mergeDone()` today. Calling `mergeDone()` directly with a corrupted
incoming value (a string, a negative number) reproduced the exact NaN/silent-erasure
bug the 2.10 fix and its 2026-09-05 correction had already fixed twice for
the existing-value side, this time on the incoming side, and this time only
reachable by skipping `parseBackup`, not by any path the shipped app
actually takes.
**Evidence:** reproduced directly in `node`, called `mergeDone()` alone with
`{ "A|Z|sort": 1700000000000 }` against `{ "A|Z|sort": "corrupted" }` before
writing anything: returned `{"A|Z|sort": null}` (a `NaN`, JSON-serialised),
the identical failure shape as both prior rounds. Confirmed the one real
call site (`App.js`'s `importBackup()`) always calls `parseBackup()` first,
so this was never live in the shipped app; confirmed by grep that no other
call site of `mergeDone` exists in the codebase besides that one and the
test file.
**Confidence:** high, reproduced directly, and the one live call path
independently confirmed safe.
**Implication:** refactoring a self-contained validate-then-merge function
into two smaller, separately testable functions (good practice on its own,
the same reason this file exists split from `App.js`) can quietly turn an
internal invariant ("this function is safe on its own") into an
inter-function contract ("this function is safe only if its one caller
validated first") without anyone deciding to make that trade. The function's
own docstring kept claiming the stronger guarantee after the refactor made
it only true in combination. This is the third time this exact file has
needed the same lesson (2.10, its correction, now this): validate every
value at the point it is used, not at the point it happens to enter the
system today, because the number of paths that can reach a merge only grows.
**Next action:** fixed by validating both sides inside `mergeDone()` itself
via one shared `sanitizeTimestamp()` helper, so the function is self-contained
again regardless of caller. Reproduced the failure against the pre-fix code
in an isolated worktree before restoring, then added two new test cases in
`importProgress.test.js` that call `mergeDone()` directly (bypassing
`parseBackup`) with a corrupted and a negative incoming value; both proved
to fail on pre-fix code and pass on the fix. Not a new preflight gate: the
existing `gate_mobile_js_tests` already runs every `lib/*.test.js` file and
fails on any nonzero exit, so these two new cases are already load-bearing
going forward without a bespoke check.

## L-APP-010: "re-read the cross-reference chain" checked the one citation touched, not every citation to the thing that changed

**Observation:** when gap 8 (deep-linking) was added to `PRD.md` Section 6
(L-APP-008, the eighth run), that same cycle's own verification step says it
"re-read the full cross-reference chain" for any numeric reference to the
renumbered items, and found none needing a change. That check was real but
narrower than it sounded: it re-read the specific sections that cite
individual gaps by number, not every place in `docs/` that states or implies
the total count. Two errors survived nine further runs of this same series
as a result: `PRD.md` Section 13 still said "Section 6's seven gaps" (a
total-count claim, not a reference to any one numbered gap, so the
per-citation re-read never looked at it), and `OPPORTUNITY-BACKLOG.md` cited
the recommendation engine as "parity gap 8.1 in the PRD," a number that had
never existed in `PRD.md` at all, introduced the same day the file was
written (2026-09-02) and never touched by the gap-8 re-read because that
citation names gap 1, not gap 8.
**Evidence:** `grep -rn "gap [0-9]|seven gaps|eight gaps|parity gap" docs/`
across the whole tree, not just the files the triggering commit touched;
confirmed the `8.1` error's age by checking `PRD.md` at the original commit
that introduced the `OPPORTUNITY-BACKLOG.md` line (`fe635125`, 2026-09-02),
where the recommendation engine was already gap 1.
**Confidence:** high, both corrected against the PRD's own current and
historical text.
**Near-miss, not a finding:** the same sweep produced a third apparent hit,
`CURRENT-STATE-AUDIT.md` citing the recommendation engine and analytics as
"item 8" and "item 9." Nearly edited it to match the audit's own "largest
verified gaps" numbering (items 1 and 4) before rereading the sentence and
finding it anchors to a different list in the same file, "ten strongest
parts that must survive the port," where 8 and 9 are correct. A grep-driven
sweep finds candidates; it does not tell you which of two lists in the same
file a number belongs to, and fixing on pattern-match alone would have
introduced the exact defect this entry is about.
**Implication:** a verification step scoped to "the citation this commit
just touched" will not catch drift in citations this commit did not touch,
even when they reference the same fact. A repository-wide grep for the
pattern class (a number, a total count, a section name) catches what a
citation-by-citation re-read misses, but only if a human or agent still
reads each hit in its own surrounding context before changing it.
**Next action:** no new preflight gate. A cross-document numbered citation
is free text, not a structured reference `preflight.py` could parse and
recompute automatically without a real risk of a false match across
unrelated numbered lists, the exact trap the near-miss above walked into
by pattern alone. If a third instance of this same drift shape turns up
in these documents, that repetition is the signal to design a narrower,
safe check rather than a fourth manual sweep.

## L-APP-011: a build-output number is a fact about one run, not the build

**Observation:** `README.md` recorded "1,131 packages... 539 modules, 1.73
MB" as a verified fact from 2026-08-31, stated with no date qualifier
implying it still held. Neither number reproduces: a clean `npm install`
against the same, unchanged-since-2026-08-25 lockfile now resolves 1,133
packages, and two consecutive `npx expo export` runs in this same session,
with no source change between them, bundled the iOS build at 552 modules
and then 526.
**Evidence:** `rm -rf node_modules && npm install` twice, both times 1,133
packages; `npx expo export --platform ios --platform android` run twice in
a row, iOS read 552 then 526 modules while Android held at 551 both times.
Confirms the seventh run's own note in `CYCLE-PLAN.md` ("module counts...
noisy across cache states") rather than a new finding, this time on the
package count too.
**Confidence:** high on the instability (directly reproduced twice); the
1,131-to-1,133 package drift's root cause is not established (same
lockfile, different npm resolver behaviour is the working guess, not
confirmed).
**Implication:** a specific number captured from one build's output belongs
in a dated log entry, not in a document read as the current state of the
project. This README already carried a date on the claim, which is better
than the undated stale-claims phrases `gate_stale_claims` watches for on
the live site, but a date does not stop a reader from taking the number as
still true, and it was not: the app has grown four library files since
that measurement, and this environment cannot even hold the number still
across two runs in the same session to check it.
**Next action:** removed the specific module/bundle-size claim from
`README.md` rather than replacing it with a fresher number that would go
stale the same way; kept the reproducible package count, dated, with the
instability noted so the next reader does not treat either figure as load
bearing. No new preflight gate: gating a number that is not stable even
within one session would fail on noise, not on a regression, the shape
`CLAUDE.md` calls theatre in the other direction. If package resolution
itself becomes a real correctness question, the fix is a committed
lockfile digest check, not a package-count assertion in prose.
