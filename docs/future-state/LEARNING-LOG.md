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
