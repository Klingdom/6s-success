# Home Quest: Current State Scorecard

Written 2026-09-02, operator, Prompt 9 step 1 ("reconstruct the current
state... separate observed fact, user-reported evidence, inference,
hypothesis, unknown").

## Observed fact (verified directly this cycle or a prior one, source cited)

- 684 cards across 114 zones in `quest-corpus.json`, S-order correct on all
  114 (parsed as JSON, not sampled). Matches the public web Quest's own
  count.
- The app has no network call anywhere in `App.js` or `lib/`: grepped for
  `fetch(`, `XMLHttpRequest`, `axios`, and literal `http://`/`https://`
  2026-09-02, zero hits outside `node_modules`.
- 24 of 24 unit tests pass (`npm test`, plain node, no device): 10 in
  `importProgress.test.js`, 7 in `pickCard.test.js`, 7 in `eventLog.test.js`.
- The app bundles clean for both platforms: `EXPO_OFFLINE=1 npx expo export`
  produces a 551-module iOS bundle (1.75 MB) and a 550-module Android bundle
  (1.76 MB), 2026-09-02.
- `python ops/preflight.py` passes with 10 warnings, all standing
  credential/network gaps (no Stripe, no mail, no `gh`, no live site
  reachability from this sandbox), none mobile-specific.
- Two real defects were found and fixed in `App.js` by cold-reading source,
  not by a device test: the "Not now" button was a no-op
  (`setFinished(null)` when `finished` was already `null`, 2026-08-31/09-01),
  and the two finish-screen buttons called the identical handler
  (2026-09-02). Both now have a dedicated preflight gate proven to fail on
  the original bug shape.
- `mobile/quest-app/ON-DEVICE-TEST.md` existed with 14 checks but had no
  check for the "Not now" fix specifically; one was added this cycle
  (now 15 checks, primary table renumbered to 11).

## User-reported evidence

- None. No user, including Phil, has opened the app on a device yet.

## Inference

- The core loop (draw, do, done, skip, finish, resume) is very likely correct
  on a device, because its logic is unit tested and its rendering is plain
  React Native with no platform-specific APIs beyond `AsyncStorage`,
  `expo-document-picker`, and `expo-file-system`, all standard and widely
  used. This is not proof; see Unknown below.
- The recommendation/audit-due engine is the single biggest feature gap
  between web and mobile (per the PRD), inferred to matter most because it
  is the one piece of the product's own stated promise ("the system tells
  you what to do next") that the web app has and the mobile MVP does not.

## Hypothesis

- A stranger who installs Home Quest will complete at least one card before
  abandoning, because the core loop requires no signup and shows a concrete
  task within one screen. Unvalidated: zero installs exist to test this
  against.
- The "Diagnostics" screen added this cycle will make Phil's on-device pass
  produce more useful evidence than an unaided pass would, because it turns
  "it worked" into a timestamped, orderable record. Unvalidated until he
  actually uses it.

## Unknown (say so, do not default)

- Whether the app actually runs, renders, and responds to touch on a real
  phone. Nothing here proves that; only a device can.
- Crash rate, ANR rate, ANR causes: no device, no crash reporting exists or
  should exist without a privacy decision first.
- Whether VoiceOver/TalkBack announce controls in a sensible order: measured
  from source (roles, labels, hints all present) but announcement order is
  explicitly a device-only check (`ON-DEVICE-TEST.md` checks 10 and 11).
- Store status, review status, install count, retention: the app has never
  been submitted anywhere.
- AI cost, support load: no AI feature exists in the app; not applicable yet.
