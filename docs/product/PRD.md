# Home Quest mobile: product target, UX architecture, PRD

Backlog item 5B.2 (`super prompts/6S-SUCCESS-HOME-QUEST-MOBILE-CLAUDE-CODE.md`,
Prompt 2). Written by the cloud operator, 2026-08-31, against repository
`cad4747f` on `main`, worktree clean, building directly on
`docs/audit/CURRENT-STATE-AUDIT.md` (5B.1).

**Scope note, same call as 5B.1 and for the same reason.** Prompt 2 asks for
thirteen separate files. CLAUDE.md section 56 warns against empty bureaucracy,
and thirteen mostly short files would scatter one coherent set of decisions
across more surface than the decisions themselves need. This single document
covers every section the prompt names, in the prompt's own order, so nothing
is missing, only consolidated. The one exception is
`WEB-TO-MOBILE-MIGRATION-CONTRACT.md`, kept as its own file because the
backlog's acceptance line names it directly ("the contract states what moves,
what changes and what a web user keeps when they install") and later work
(5B.4, 5B.5, a future store listing) will want to cite it on its own rather
than find it buried in a longer document.

**What this is not.** Personas below are design hypotheses, not customer
research. No claim in this document is a measured fact about real users;
zero real customers have used the mobile app yet, and the roadmap
(`ROADMAP-2026-2029.md`) is explicit that the web product itself has
converted exactly one stranger, never mind the app. Every persona,
flow decision and monetization number here is labelled as a hypothesis to
test, per CLAUDE.md's evidence hierarchy, not asserted as validated.

---

## 1. The product promise

Home Quest should help a tired adult or household make one visible
improvement in under a minute of decision effort. The mobile app expands
that into a calm, durable household practice without turning the home into
a nagging dashboard.

The live web Quest is the canonical starting point, confirmed by 5B.1's
full read of `quest.js` and `quest-data.js`: single-card draw, six bounded
steps per zone in fixed S order, no account, no shame for stopping. Nothing
in this document replaces that loop. The mobile app's job is to carry it
onto a phone, in a garage or a closet, without new friction, and then to
close the one gap the web loop cannot close on its own: telling a returning
user what is actually due for another look, which is what makes "sustain"
real instead of a label on a card nobody revisits.

Do not casually reach for the older, more complex AI-first Home Reset
prototype mentioned in the super prompt. Nothing found in this repository
during 5B.1 shows that prototype shipped or is in active use; the live
product is the 684-card Quest. Harvest from it only if a specific capability
is verified to exist and to improve the card-first loop, never by default.

## 2. Segments

Six segments, each a design hypothesis rather than a researched persona
(no interviews, no survey, no session recording exists for this product):

1. **Solo adult, smallest possible start.** Wants one card, one job, no
   setup. Already the primary case the web Quest and the mobile MVP both
   serve today.
2. **Couple sharing zones without conflict.** Needs to see what the other
   person already finished so two people do not duplicate or contest the
   same zone. No account exists in v1, so this segment is served by the
   backup/import merge (Section 8) rather than real-time sharing; real
   sharing needs the accounts layer named in Section 9 and is explicitly
   out of scope for R1.
3. **Family with children, adults keep control.** Children participate in
   the physical work; account control and any safety-relevant confirmation
   stay with an adult. No child accounts in v1 (matches the super prompt's
   own instruction and CLAUDE.md's privacy stance on unnecessary data
   collection about minors).
4. **User with limited mobility, fatigue, pain, attention, vision, or
   hearing.** Served by the accessibility work already landed (5B.9 static
   half: contrast, roles, labels, hints) and the device-verification work
   still open (5B.9's on-device half, 5B.4). Nothing in this PRD proposes a
   separate "accessible mode"; the product is one experience, accessible by
   default, per CLAUDE.md section 45.
5. **Power user completing full-room resets.** Needs work-a-room mode
   (method order across a whole room), which exists on web and is a
   confirmed mobile gap (5B.1's parity table, row 2).
6. **Returning user maintaining standards.** Needs the recommendation and
   audit-due engine, which exists on web (`computeRecommendation`,
   `nearestZone`, `heldZones`, `daysSince`, `streak`) and is a confirmed
   mobile gap (5B.1's parity table, row 6). This segment is the one the
   product promise in Section 1 explicitly names as the mobile app's job to
   close; it is the highest-priority parity gap in this document.

## 3. Information architecture

**Chosen: three primary destinations, not five.** The super prompt allows
up to five (Today, Quest, Home, Progress, Profile/Settings) and asks which
to use. Five wall-to-wall destinations for an app whose entire v1 has no
account and no settings worth a dedicated screen would itself be the "three
equal walls of explanation before action" the prompt warns against.

1. **Today** (default screen on launch). Answers "what is one useful thing
   I can do now": the next recommended card if the audit-due engine has one,
   otherwise a draw button. This is the screen the current MVP's single view
   effectively is today, once the recommendation engine (Section 6) lands.
2. **Quest** (the working screen). The active card: instructions, timer,
   photo slot, done/skip/pause. Reached from Today by drawing, or directly
   via a room/zone deep link, matching the web app's own `?zone=`/`?room=`
   pattern (5.6).
3. **Home** (progress and settings combined). Whole-house progress map,
   zone-held list, streak if the ethics review in Section 7 keeps it, backup
   export/import, and the small settings surface v1 actually has (nothing
   requiring a dedicated Profile screen exists without accounts).

Room and one-S mode selection are entry points into Quest, not destinations
of their own, matching the web app's own mode parameter rather than
inventing new top-level navigation for them.

## 4. Core loops and state model

**One state object, one shape, both platforms.** The mobile app already
persists under the same key the web app uses (`6s.quest.v1`) and the same
`cardId()` shape (`room|zone|pass`), confirmed in 5B.1. This document does
not change that; it is the reason the import merge needed no translation
layer and should stay true as new state is added.

**State hierarchy, clarified per the prompt's own request:**

- **A card completed.** One `done[cardId] = timestamp` entry. Atomic, the
  smallest unit of progress.
- **An S completed for a zone.** All six `cardId`s for one zone's one pass
  are already the full set (each zone has one card per S; "an S completed
  for a zone" and "a card completed" are the same event, not two ranks of
  state). No new state needed.
- **A zone reset.** All six cards for a zone marked done at least once.
  Read from `done`, not stored separately (matches `zonesHeld`'s existing
  computation on the web side).
- **A zone holding its standard.** A zone reset AND its most recent
  Sustain card timestamp is inside the zone's own audit cadence (the web
  app's `daysSince`/`heldZones` logic). This is state that changes over
  time without user action (a held zone can silently age out of "holding"),
  so it must be computed at read time, never cached, on both platforms.
- **A room holding.** All zones in a room holding. Computed, not stored.
- **A whole-home milestone.** All rooms holding, or a percentage threshold
  for the progress map. Computed, not stored, and never gated behind
  payment (Section 8).

**Core flows, the twelve the prompt names, each with the v1 decision:**

1. **First launch to first card, no account.** Already true on mobile
   (5B.1 confirms no account gate exists). Today screen shows a draw
   button on first launch since there is no recommendation yet to show.
2. **Draw, start, pause, skip, finish, stop.** Draw and finish (`markDone`)
   and skip exist on mobile today. Start/pause need the timer (Section 6,
   gap 5). Stop without guilt already works: closing the app mid-card loses
   nothing, since nothing is written until `markDone`.
3. **Six steps across one zone, one or many sessions.** Already works;
   `AsyncStorage` persists between sessions.
4. **Work a room in method order.** Gap (Section 6, gap 2). Reuses the
   web's `build("room", roomName)` semantics: draw the next undone card in
   that room, S order first, then zone order.
5. **Run one S across a selected room.** Same gap, same mode family.
6. **Capture before/after evidence, never mandatory.** Gap (Section 6,
   gap 3). Photo slot appears on the card; skipping it never blocks
   `markDone`, matching the web app's own optional photo behaviour.
7. **Write or confirm the standard, choose a sustain trigger.** The corpus
   already carries `done` (the standard text) and `trigger` per zone
   (confirmed present for all 114 zones in 5B.1); v1 displays them on the
   Sustain card rather than letting a user author new ones. Custom
   standards are a R2 idea (Section 10), not a v1 requirement; the prompt
   does not require authoring, only "write or confirm."
8. **Receive an audit-due card, mark holding or drift honestly.** Gap
   (Section 6, gap 1, the highest-priority one). "Honestly mark drift" is
   load-bearing: the recommendation engine must never assume a zone still
   holds just because it once did, and the UI must make marking drift as
   easy as confirming holding, or the data becomes optimistic rather than
   true, the same shape of dishonesty CLAUDE.md section 8 forbids in
   marketing copy.
9. **Invite another adult, assign a zone owner.** Needs accounts. Out of
   scope for R1 and R1.1 as currently staffed; see Section 9 and Section
   10's R1.1 note on what a no-account version of "sharing" can do instead
   (export/import, Section 8).
10. **Child participation without child accounts.** No separate flow is
    proposed for v1: a child can hold the phone and do the physical work
    under a logged-in-as-nobody app exactly as it works today, since v1 has
    no accounts for anyone. Revisit only once household accounts (R1.1)
    exist, so a child's presence does not accidentally create a child
    account by omission.
11. **Import a web backup, reconcile duplicate progress.** Built and unit
    tested (5B.5, `lib/importProgress.js`), not yet device-verified
    (Section 8 covers this in full, since it is also the acceptance
    criterion for this document).
12. **Upgrade, restore purchase, downgrade, delete account, continue
    locally.** No paid tier and no account exist yet, so nothing here is
    buildable in R1. "Delete account, continue locally" degrades to
    "delete all local data," which should exist in Home settings regardless
    of accounts (a plain data-wipe control), since CLAUDE.md section 47
    treats a clear deletion path as a privacy baseline, not a paid feature.

## 5. What must survive the port

Restating 5B.1's own list here since Prompt 2 explicitly asks for
architecture decisions to protect it, not just name it:

1. The single-card, one-job, no-shame loop.
2. Correct, unbroken S order (Safety fourth, D-014) across all 114 zones.
   Any new mode (room, one-S) must draw from the corpus's existing
   `steps[].s` order, never a hand-maintained list that could drift from it.
3. `quest-data.js` to `quest-corpus.json` as a generated, checksummed
   pipeline (`ops/build_mobile_corpus.py --check`), not a hand copy.
4. Deep-linking straight into a zone or room. Currently web-only, same as
   item 8 below; unlike item 8 this was missing from Section 6's build
   order until this document's own 2026-09-05 correction added it as gap 8.
5. Photos staying device-local, never entering analytics payloads.
6. The backup/restore JSON shape and the earliest-timestamp-wins merge
   rule.
7. No account required to get value.
8. The recommendation/audit-due engine, ported faithfully, not
   reinvented, since a differently-tuned cadence on mobile than on web
   would mean the same zone reads "due" on one device and "holding" on the
   other for the same household.
9. First-party analytics with no sensitive payload shape (Section 11).
10. Written non-goals, kept current in the mobile README and this
    document, so a settled call (no accounts in v1, no streak pressure) is
    not silently reopened by a later cycle without new evidence, the same
    discipline `BACKLOG-2026-H2.md` already holds itself to.

## 6. Parity gaps this document orders (not builds)

Restating 5B.1's gap table with an explicit build order for whenever 5B.4
(device verification) clears it, since Prompt 2 asks for a roadmap and
5B.1 deliberately stopped short of ordering the gaps:

1. **Recommendation/audit-due engine.** Highest priority. Without it,
   "sustain" is a card label, not a mechanic, and Section 2's segment 6
   (returning user) has nothing built for them at all.
2. **Mode selection (room, one-S).** Needed for segment 5 (power user) and
   flows 4 to 5.
3. **Photo capture.** Needed for flow 6. Device-local only, per Section 5,
   item 5; never uploaded, never in analytics.
4. **Analytics.** Needed to answer 5.2 (EXP-004 retention) and to run
   5B.11's own improvement loop at all. Must ship with the no-sensitive-
   payload constraint from day one, not bolted on after a privacy review
   finds a leak (Section 11).
5. **Timer.** Needed for flow 2's start/pause.
6. **Progress map.** Needed for Home's whole-house view (Section 3);
   counts alone already exist and are an acceptable interim.
7. **First-run gate.** Lowest priority; a returning user seeing the same
   first screen as a new one is a cosmetic gap, not a functional one.
8. **Deep-linking into a zone or room.** Found missing from this list
   2026-09-05, Prompt 9's eighth run: Section 5, item 4 and 5B.1's own "ten
   strongest parts" list both name this a property the port must protect,
   the same framing given to the recommendation engine (gap 1) and
   analytics (gap 4), but unlike those two it was never carried into this
   build order, so the plan silently dropped a gap it elsewhere claims to
   guard. Grepping `App.js`, every `lib/*.js` file and the Expo config
   confirms it: no `Linking` import, no URL scheme, no query-param parsing
   anywhere. Priority sits with mode selection (gap 2), a related
   entry-point mechanism; numbered last here only to avoid renumbering the
   gaps this document already cites by number elsewhere (Sections 4 and 11).

Building any of these before 5B.4 (a real phone actually running the
current core loop) risks compounding unverified code on unverified code,
which is 5B.1's own recommendation and this document does not override it.
This is a build order, to be picked up only after 5B.4 closes.

## 7. Calm gamification: what is allowed and what is prohibited

**Prohibited outright, matching the super prompt's own list and CLAUDE.md
section 8's ban on manufactured urgency and fake proof:** punishment for
missed days, addictive variable rewards, public household shaming, loot
boxes, fake countdowns, pay-to-complete mechanics.

**Allowed, evaluated one at a time against "does this reward meaningful
work":**

- **Streak.** Allowed only if reframed away from daily-login pressure: a
  streak here should count zones held, not consecutive days opened, so
  missing a day never breaks it and a household that checks in weekly is
  never punished relative to one that checks in daily. This is a change
  from the web app's own streak semantics (`streak()`, not fully read for
  its exact day-based logic in 5B.1) and needs that function re-read before
  either platform ships it; flagged here rather than assumed compatible.
- **House Passport / Reset Run / whole-home milestone.** Allowed: a
  cumulative record of real work done, closer to a logbook than a game
  mechanic. No countdown, no expiry.
- **Time Tokens, Daily Draw, Family Race, interlocks, Hazard Bounty.**
  Named in the super prompt's Card System architecture reference but not
  found anywhere in this repository (not in `quest.js`, not in
  `quest-data.js`, not in any committed design doc). Treated as unbuilt
  concepts, not existing product, and out of scope for R1 pending a
  concrete design that can be checked against the prohibited list above
  item by item; naming them here without one would be exactly the kind of
  unfinished half-built feature CLAUDE.md warns against carrying.

## 8. Free, paid, and the migration contract

Full detail in `WEB-TO-MOBILE-MIGRATION-CONTRACT.md`, which this section
summarizes rather than duplicates.

**Entitlement hypothesis, labelled a hypothesis, not a decision, since
building a paid mobile tier needs the accounts layer this document
explicitly defers (Section 9):**

- **Free.** The current 684-card core, local-only progress, photos, backup
  and import, one household profile on one device. This is not a reduced
  tier; it is the entire product as it exists today, and CLAUDE.md's rule
  against gating something already advertised as free applies directly:
  nothing in the free web Quest may become paid-only on mobile.
- **Plus (not built, R1.1 at earliest).** Secure sync, household
  collaboration, richer reset history, native reminders, an optional AI
  coaching allowance, premium share/print outputs. Needs the accounts layer
  named in Section 9; not a R1 deliverable.
- **Commerce.** Relevant product recommendations after a need is
  identified, never before Sort, matching CLAUDE.md section 48's
  "Recommended because [outcome/root cause/constraint]" pattern exactly.
  The zone pack / room pack catalogue already exists and already prices
  this way on web (5.9); mobile should reuse the same catalogue and the
  same rule rather than invent new pricing, once a purchase path exists on
  mobile at all (it does not yet; no Stripe or IAP integration is present
  in `mobile/quest-app`).

**Never locked behind payment, on either platform:** safety guidance,
account deletion, accessibility, export, or already-earned progress. This
mirrors CLAUDE.md's own commerce and trust rules and is not a new policy
invented for mobile.

## 9. AI boundary

AI is optional, user-initiated, clearly labelled, and never the source of
record. No AI feature exists in `mobile/quest-app` today (confirmed in
5B.1: no network calls at all, so nothing calling a model exists), so this
section is entirely forward-looking, for R2 only.

**Candidate uses, none built:** a photo-assisted Sort plan, visible-hazard
suggestions carrying strong stated limitations, a warm after-review summary
of what was completed.

**Hard boundaries, matching the super prompt and CLAUDE.md sections 8 and
32:** never identify people, never infer sensitive traits, never diagnose,
never price possessions, never claim a safety inspection is complete. Basic
instructions, completion, photos, and sustain tracking must work fully with
zero AI involvement, since the current product already does and nothing in
this document should make that a dependency.

Any AI feature reaching for a network call would also break the app's
current, deliberate "no network calls at all" property (Section 5, item 5's
sibling rule in the mobile README). That tradeoff (calm/private vs.
AI-assisted) needs an explicit decision when R2 is actually staffed, not a
default; recorded as open in Section 12.

## 10. Platform decision

**Decision: continue with the shared React Native / Expo implementation
already built, rather than separate SwiftUI and Kotlin Compose apps.**

This is not a new choice being made here; it ratifies what 5B.3 already
built and 5B.1 already verified working (1,132 packages resolve, the app
bundles clean, Metro serves it over the LAN). Revisiting it now, after a
working vertical slice already exists and after the actual constraint on
progress is device verification (5B.4) rather than framework choice, would
be reopening a settled call without new evidence, exactly what CLAUDE.md's
Decision Memory section warns against.

**Why it was and remains the right call, checked against the prompt's own
criteria:**

- **Repository fit.** One shared TypeScript-adjacent domain layer already
  reads `quest-data.js` through a single generated corpus
  (`ops/build_mobile_corpus.py`), avoiding a second, hand-maintained
  content copy per platform, the same drift risk that cost twelve days
  elsewhere in this repository per 5B.1's own note.
- **Team.** One operator (human plus autonomous agents) building both a
  web app and a mobile app; two native codebases would double the surface
  one team has to keep in sync with zero measured demand yet to justify it.
- **Offline and photo needs.** Expo's file system and async storage APIs
  already meet the current requirement (no network calls, local
  persistence) without native modules beyond the two already added for the
  document picker.
- **Accessibility, billing, notifications.** Not yet built on either
  platform choice, so this criterion does not currently favour native; if
  a specific Expo limitation blocks a required accessibility or billing
  capability during R1.1 or R2, that would be new evidence and grounds to
  revisit, not a reason to switch now.

Platform-native modules remain allowed where a specific verified constraint
needs one (the prompt's own allowance), same as the document-picker modules
already added in 5B.5.

## 11. Analytics measurement plan

**Principle, carried over from the web app's own `m()` function rather than
invented fresh:** first-party events only, no sensitive payload. 5B.1
confirmed the web app's event payloads carry only `s`, `nth`, `zone` name
and `sku`, never room contents, photo data, or anything personally
identifying.

**Mobile has zero analytics today** (5B.1, confirmed gap). Building it is
gap 4 in Section 6's order, and it directly blocks measuring 5.2 (EXP-004,
mobile retention) and 5B.11 (the app's own improvement loop), so it should
not be left until last within its own priority band even though Section 6
orders it fourth relative to the other gaps.

**The tension this document surfaces rather than resolves:** the mobile
README's "no network calls at all" is a stated product decision and a real
trust signal (a photograph of somebody's home must never leave the device).
Analytics, by definition, sends something over the network. This is not a
contradiction to paper over: the resolution is that analytics events (not
photos, not room content) are the one narrow, explicit exception, sent only
as the same minimal shape the web app already proves is safe, and the
mobile README and privacy copy must say so explicitly the moment analytics
ships, rather than let "no network calls at all" quietly become false
without an update to the promise that made it. Flagged as a required
documentation change alongside the Section 6, gap 4 build, not a blocker to
building it.

## 12. Decisions and open questions

Decisions made in this document, in the same evidence-and-alternative
format `DECISIONS.md` uses, kept here rather than duplicated there since
each is scoped to the mobile product rather than the business as a whole:

- **Three primary destinations, not five** (Section 3). Evidence: the
  prompt's own warning against three equal walls of explanation; five
  destinations for a v1 with no account and minimal settings would
  reproduce that problem in the nav bar instead of the first screen.
  Alternative rejected: five destinations to match the prompt's full menu,
  rejected as premature information architecture for features that do not
  exist yet (Profile has nothing to hold without accounts).
- **Continue Expo/React Native** (Section 10). Evidence and alternatives
  above.
- **Recommendation engine ordered first among parity gaps** (Section 6).
  Evidence: it is the only gap that makes the product's own stated promise
  (Section 1) true on mobile; the other gaps are feature parity, this one
  is the difference between "sustain" being real or being a word.

**Open, not decided here, and named rather than guessed at:**

- Whether the streak mechanic's day-based semantics (web) survive
  unchanged or need the zones-held reframing proposed in Section 7; needs
  a full read of `streak()` before either platform commits to a shape.
- Whether Plus-tier pricing (Section 8) should mirror the web catalogue's
  existing price points or needs its own model; blocked on the accounts
  layer existing at all, so not worth guessing at yet.
- The AI/offline tradeoff named in Section 9, deferred to R2 staffing.

## 13. Roadmap: three releases, impact versus effort, no dates

Per the prompt's own instruction, no calendar dates: repository scope and
staffing are not known well enough to commit to one, and a dated plan this
early would be the same mistake `ROADMAP-2026-2029.md` section 1 already
named and corrected once (a target stated for weeks and never divided by a
real number).

**R1, Storeworthy Core: the smallest app worthy of public trust.**
Dependency order: 5B.4 (device verification, blocking, must go first) then
Section 6's eight gaps in the order given, then 5B.9's on-device
accessibility half, then 5B.6/5B.7 (store builds, both blocked on
accounts Phil must create, named in the backlog and not repeated here).
Confidence: high on the build sequence itself (grounded in code that
already exists or is a direct port of code that does), low on effort
sizing, since none of the eight gaps has been scoped function-by-function
yet.

**R1.1, Household and Sustain: retention through genuine standards
holding.** Depends on an accounts layer that does not exist in this
repository in any form today (confirmed by grep across `mobile/` and
`ops/` during this session: no auth library, no user table, no session
token anywhere). This is the same wall the roadmap's own $11,250-of-
$21,500 note names for 6S Plus generally, not a mobile-specific gap.
Work packages: accounts and household sharing (flow 9), Plus entitlements
(Section 8), real streak/reminder mechanics once Section 7's open question
is resolved. High uncertainty; effort cannot be sized until an auth
approach is chosen, which this document does not attempt, since it is a
business-wide decision, not a mobile-only one.

**R2, Guided Intelligence and Growth: optional AI, richer cooperative
play, responsible commerce.** Depends on R1.1's accounts layer for
cooperative play, and on the AI boundary in Section 9 plus its unresolved
offline tradeoff. Lowest confidence of the three, correctly: nothing in
this repository today does any of what R2 describes, and CLAUDE.md's own
rule against designing for hypothetical future requirements argues against
scoping it further than the boundary already set in Section 9 until R1 and
R1.1 produce real usage to design against.

**What this document deliberately does not do:** assign dates, promise
hiring, or estimate a mobile-specific revenue number. `ROADMAP-2026-2029.md`
already governs the business's dated targets and gates (G1 through G5); this
document adds a product sequence underneath that plan, not a competing one.
