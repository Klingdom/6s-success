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
