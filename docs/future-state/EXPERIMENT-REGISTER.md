# Home Quest: Experiment Register

No experiment has run yet. An experiment needs at least one real user
outside the people building the app, and there are zero installs. Registering
a "control vs variant" test now would be process theatre: nothing to
segment, nothing to measure.

What belongs here once the app has any real usage, in the same format
CLAUDE.md section 16 uses for the web business:

**Format:** Because we observed [evidence], we believe [change] will improve
[metric] for [audience] because [reason].

## Pending, not yet runnable

### EXP-APP-001: Does a first-time opener complete one card?

- **Because we observed:** nothing yet; this is the first question, not a
  follow-up to existing evidence.
- **We believe:** a person who installs Home Quest and opens it will
  complete at least one card before leaving, because the core loop requires
  no signup and presents one concrete task on the first screen.
- **Audience:** anyone who installs the app, starting with Phil's own
  on-device pass, then any real install after a store listing exists.
- **Control/variant:** not applicable yet; there is only one version of the
  app.
- **Primary metric:** first card completed, yes or no. Cannot be measured
  without either a store install funnel or a manual report, since the app
  has no network calls and therefore no automatic telemetry, by design
  (dimension 5, `TARGET-FUTURE-STATE.md`).
- **Guardrails:** none yet defined; will need a privacy-respecting design
  before any telemetry is added, since "no network calls" is a stated
  product promise, not a default that can be quietly reversed.
- **Duration/stopping logic:** cannot start until a distribution channel
  (store listing, 5B.10) exists.
- **Status:** blocked on 5B.6/5B.10 (both need Apple/Google developer
  accounts, Phil's identity). Not started.

### EXP-APP-002: Does the Diagnostics log change what an on-device tester reports?

- **Because we observed:** the on-device pass has never run, so there is no
  before/after data yet; this experiment is really a validation of the
  instrumentation itself, run once against the very first on-device pass.
- **We believe:** having `lib/eventLog.js`'s local log available will let
  the tester (Phil) report exact sequences and timestamps instead of a
  general impression, improving the quality of the one data point this
  project currently has zero of.
- **Audience:** Phil, on his own on-device pass.
- **Primary metric:** whether the diagnostics text is referenced in his
  report.
- **Status:** cannot start until `OWNER-ACTIONS.md` item 2 happens. Not a
  controlled experiment in the normal sense (n=1, no variant), recorded here
  anyway because it is this cycle's actual instrumentation bet and should be
  checked rather than assumed to have worked.
