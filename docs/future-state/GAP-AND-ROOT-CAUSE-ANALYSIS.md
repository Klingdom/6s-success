# Home Quest: Gap and Root Cause Analysis

Written 2026-09-02, operator, Prompt 9 step 3.

## Value stream, discovery to a holding zone

```
discovery -> install -> open app -> draw first card -> do the task
  -> mark done -> finish a zone -> zone holds over time
```

Every stage after "open app" has zero measured drop-off, because zero people
have entered the funnel at all. This is not a conversion problem to optimize;
it is a distribution and verification problem to solve first, the same
ordering rule that governs the web business (BACKLOG-2026-H2.md: measurement
before traffic before conversion before product).

## The largest gap, named plainly

**Nobody, including the people building it, has opened this app on a real
phone.** Every other fact in `CURRENT-STATE-SCORECARD.md` is downstream of
this one. A perfectly unit-tested core loop that has never rendered on a real
device is still an unverified product.

## Root cause

Not a feature gap, a technical gap, or a market gap. It is a **verification
access gap**: the only device that can run Expo Go against this app belongs to
Phil, and only he can scan the QR code and report back. This is structurally
identical to several other stalled items in BACKLOG-2026-H2.md (Umami access,
Stripe business field, Google Business Profile phone number): a single
five-to-twenty-minute action, gated on one person's device or account, that
nothing else can substitute for.

Contributing causes, smaller and already addressed or in progress:
- Two real code defects (both fixed) would have made the first on-device pass
  fail on cosmetic-looking grounds ("the button didn't do anything") rather
  than reveal anything about the product itself. Closing those first was the
  right sequencing: an on-device pass that immediately hits a dead button
  wastes the one scarce resource (Phil's five minutes) on a bug a cold read
  could catch for free.
- The on-device script itself had a coverage gap: it tested the fix for one
  bug (`ON-DEVICE-TEST.md` checks 14 and 15, "Stop here, this counts") but not
  the other (the "Not now" button, fixed a day earlier). Fixed this cycle by
  adding checks 4 and 11.
- Until this cycle, an on-device pass would have produced only a subjective
  "it worked" or "it didn't," not a structured record. The new Diagnostics
  log (`lib/eventLog.js`) narrows that gap without needing network access or
  a new account: the log is local, and its text can be read straight off the
  phone screen.

## What this analysis does and does not justify

Does justify: keep closing code-level defects found by cold-reading source,
since two out of two `App.js` review passes have found a real, previously
invisible bug, and a third pass this cycle found the on-device script's own
coverage gap rather than a new App.js bug (a sign the two-pass sweep of
App.js is reaching diminishing returns, and the on-device script is a better
place to look next).

Does not justify: building parity features (recommendation engine, timer,
photo capture) ahead of the on-device pass. The PRD already recommends
against this and nothing in this analysis changes that recommendation.

Does not justify: an operator attempting the on-device pass itself. It
requires a physical phone and Phil's own Expo Go scan; no sandbox substitute
exists, and pretending otherwise would produce a false "verified."
