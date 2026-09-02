# Home Quest: Decisions Required From the Owner

This file tracks only app-specific decisions that Prompt 9's own process
surfaces. It does not duplicate `OWNER-ACTIONS.md`; it points to the same
items rather than repeating them, so there is one place each is described in
full.

## Nothing new this cycle

No decision surfaced this cycle that is not already tracked:

- **Run the on-device pass.** Not a decision, an action.
  `OWNER-ACTIONS.md` item 2, `mobile/quest-app/ON-DEVICE-TEST.md` (now 15
  checks). Ready, blocked only on Phil's phone and about 20 minutes.
- **Production builds, store accounts, household/account layer.** Genuine
  decisions and financial/identity commitments (Apple Developer account,
  Google Play account, an accounts layer shared with the wider 6S Plus
  question). Tracked in BACKLOG-2026-H2.md's 5B.6 to 5B.10 rows and
  `OWNER-ACTIONS.md`; not repeated here.

## Standing note for future cycles

Per this prompt's own step 5: never autonomously publish a store release,
change pricing, spend money, message users, alter legal policy, enable new
sensitive data collection, or materially broaden AI use. Nothing on this
list has been touched. The Diagnostics log added 2026-09-02
(`lib/eventLog.js`) is local-only and does not enable any new data
collection in the sense this rule means; it stores nothing that was not
already implicit in using the app, and sends nothing anywhere.
