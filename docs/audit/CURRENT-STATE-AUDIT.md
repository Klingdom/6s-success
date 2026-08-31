# Home Quest mobile: current-state audit

Backlog item 5B.1 (`super prompts/6S-SUCCESS-HOME-QUEST-MOBILE-CLAUDE-CODE.md`,
Prompt 1). Written by the cloud operator, 2026-08-31, against repository
`fccb986f` on `main`, worktree clean.

**Scope note.** Prompt 1 asks for nine separate artifact files plus a
competitive UX review. The backlog's own acceptance line for 5B.1, which
governs when the two disagree, asks for one thing: "a written audit naming
every gap between the web Quest and the mobile product principles." This is
that document. Splitting it into nine mostly-empty files would be the
bureaucracy CLAUDE.md section 56 warns against; the findings below are
organized under the same headings the prompt uses so nothing it asked for is
missing, just consolidated.

## What this sandbox can and cannot verify

Checked directly, not assumed:

- **No egress to `6s-success.com`.** `WebFetch` on `https://6s-success.com/quest.html`
  returns `EGRESS_BLOCKED` from the proxy. Everything below about the *live*
  product is inference from the repository plus `CURRENT_STATE_AUDIT.md`
  (written the same day, a different audit against the growth prompt's seven
  named risks, which did have a session with live access). Where the two
  disagree, the live-access one wins.
- **No real phone.** Nothing about the Expo Go picker, on-device accessibility,
  or on-device performance can be verified here. 5B.4 (device parity) and half
  of 5B.9 (device accessibility/privacy proof) are explicitly carrying this
  same wall; not re-litigated here.
- **`WebSearch` works, but returned low-quality aggregator content** ("best
  chore apps of 2026" SEO farms, not primary product documentation) for a
  household-chore-app competitive query. The prompt asks to prefer direct
  product documentation and current store listings; this sandbox's search
  access could not clear that bar, so no competitive-pattern claims appear
  below. Fabricating one from SEO blogspam would violate CLAUDE.md section 8.
  Worth doing later from a session with real App Store / Play Store browsing.

## Content model: verified against `site/assets/js/quest-data.js`

Parsed the actual JSON (380,955 bytes, generator-owned by `ops/build_quest.py`,
header says do not edit):

- **20 rooms, 114 zones, 684 cards.** Matches every public claim on the site
  and in `mobile/quest-app/README.md`.
- **Every zone carries exactly 6 steps**, no more, no fewer.
- **S-order checked on every zone, not sampled:** `steps[].s` values are
  `sort, straighten, shine, safety, standardize, sustain` in that order for
  all 114 zones. Safety fourth, consistent with D-014. No zone found reversing
  Safety and Standardize or renaming Straighten to "Set in Order."
- Each zone carries `zone, session, purpose, done, steps, call, watch,
  standard, trigger, url`. A `done` field (the standard) and per-step text
  exist for all 114, not a partial set.
- `mobile/quest-app/assets/quest-corpus.json` (248,475 bytes) is a build
  product of the same source file, records its sha256, and its own header
  states 20/114/684, matching. `ops/build_mobile_corpus.py --check` is the
  drift detector; not re-run this cycle since nothing touched either file.

## Web Quest feature inventory (from `site/assets/js/quest.js`, 1,155 lines)

Read the whole file rather than sampling. What exists today, each grounded in
a real function:

- **Modes:** `build(mode, roomName, zoneName, s)` supports at least random
  draw, a named zone run, and a named room run (method order); deep links via
  `findZoneBySlug`/`findRoomBySlug` land a visitor straight into their own
  zone or room without the two-dropdown start screen (5.6, done 2026-08-26/27).
- **Timer:** `startTimer`/`stopTimer`, a live-updating `paint()` closure.
- **Photo capture:** `paintShots`/`slot`, backed by `window.QuestPhotos`
  (IndexedDB, confirmed by the code comment at line 383: "Photographs live in
  IndexedDB and are read asynchronously"). Storage-full is handled with a
  specific message ("There is no room left on this device...") rather than a
  silent failure.
- **Backup/restore:** `backup()` writes a JSON file; `restore(text)` reads one
  back. This is the exact shape `mobile/quest-app/lib/importProgress.js`
  parses; already exercised end to end with a real browser-produced file per
  `RETRO-2026-08-31-cycle34.md`.
- **Recommendation engine:** `computeRecommendation()`, `nearestZone()`,
  `heldZones()`, `daysSince()`, `streak()` together implement audit-due and
  sustain-cadence logic. **Nothing in the mobile MVP has an equivalent.**
- **Progress map:** `renderMap()`, a whole-house view, separate from the
  single-card view.
- **First-run gate:** `isFirstRun()`/`applyFirstRunGate()`, a distinct
  first-time-visitor path.
- **Analytics:** `m(name, data)` fires first-party events: `quest-offer-shown`,
  `quest-card-done`, `quest-zone-held`, `quest-first-start`. No room name or
  photo content in any payload checked (only `s`, `nth`, `zone` name, `sku`),
  consistent with the product principle against leaking sensitive room/photo
  data into analytics.
- **Accessibility:** 6 `aria-`/`role=` attributes and one explicit `.focus()`
  call (line 976, after `resetRoom()`, moving focus back to a live element)
  found in the JS; the HTML template carries more. One `prefers-reduced-motion`
  rule exists in the CSS. This is evidence of *some* accessibility work, not a
  WCAG 2.2 AA claim; `accessibility.html` itself says a formal audit has not
  been done (verified true, not stale, per this cycle's preflight run).
- **Offline/PWA:** `site/sw.js` exists and `quest.html` registers it (line
  244-246) guarded by `"serviceWorker" in navigator`.
- **Privacy copy:** `privacy.html` states photographs "are held in your own
  browser", matches the IndexedDB implementation, not a broken promise.

## Mobile MVP feature inventory (from `mobile/quest-app/App.js`, 320 lines)

- Draws the **first unfinished card** by walking the corpus in order, not a
  random draw, and no mode selection (no work-a-room vs. one-S-across-room
  choice; the whole app is currently one implicit mode).
- `markDone()`, `skip()`, `zoneProgress`, `zonesHeld`, the done/skip loop and
  house-level progress exist.
- `importBackup()`, the merge path from cycle 34/35, proven against real web
  output in a real browser, not yet against a real device picker.
- Persistence: `AsyncStorage` under the same `6s.quest.v1` key the web app
  uses for `localStorage`.
- **Not present at all:** timer, photo capture, the recommendation/audit-due
  engine, streak, progress map view, first-run gate, analytics, mode
  selection (random / room / one-S).

## Web-to-mobile parity gap table

| Capability | Web Quest | Mobile MVP | Note |
|---|---|---|---|
| Random draw | yes | no (sequential walk only) | mode selection not built |
| Work-a-room mode | yes | no | |
| One-S-across-room mode | yes | no | |
| Timer | yes | no | |
| Photo capture (before/after) | yes, IndexedDB | no | product principle 51 (privacy) has nothing to violate yet since it is simply absent |
| Sustain / audit-due recommendation | yes | no | the mechanic that makes "sustain" real rather than a label |
| Streak | yes | no | deliberately not urgency-driven per product principles; still a gap if the intent is parity |
| Progress map (whole house) | yes | zone/house counts only, no map view | |
| First-run gate | yes | no (every launch behaves the same) | |
| Analytics | yes, first-party, no sensitive payloads | none | cannot measure 5.2 (EXP-004 retention) on mobile without this |
| Backup export | yes | not built (import only) | a phone user cannot currently back up to hand to a second device |
| Backup import / merge | n/a | yes, unit tested, not device-verified | |
| Offline | yes, service worker | yes, native, no network calls at all (README states this as a decision) | mobile is actually stronger here |
| Accounts | none (by design, v1) | none (by design, v1) | matches |

## Accessibility, privacy, security (consolidated, not a separate file)

- **Web:** some ARIA/role usage and one explicit focus-management call found;
  no completed third-party audit (site says so, correctly, per the
  `stale-claims` preflight check reading this exact sentence and it still
  being true). Photos are device-local (IndexedDB), matching the privacy
  page's claim.
- **Mobile:** README states "no network calls at all" as a decision, which
  the app's own dependency list is consistent with (no fetch/axios/network
  library imported in `App.js`); not independently traced call-by-call this
  cycle. 5B.9, claimed in progress by a session with device access as of the
  last commit on `main` (`fccb986f`, "Claim 5B.9 before starting it"), is
  already doing the deeper version of this: a static accessibility review of
  the app's own source plus proving nothing leaves the phone. Not duplicated
  here.
- No credentials, tokens, or payment data touch the mobile app in its current
  form; nothing found to flag.

## Ten strongest parts that must survive the port

1. The single-card, one-job, no-shame loop itself, the actual product.
2. Correct, unbroken S-order across all 114 zones (Safety fourth, matches
   D-014), this is load-bearing and easy to regress by accident.
3. `quest-data.js` as one shared, generator-owned corpus, the mobile corpus
   already derives from it rather than copying, avoiding the drift class that
   cost 12 days elsewhere in this repo (`mcp/content.json`).
4. Deep-linking a visitor straight into their own zone or room (5.6).
5. Photos staying device-local and never entering analytics payloads.
6. The backup/restore JSON shape, simple enough that the mobile merge needed
   no translation layer.
7. No account required to get value, both products agree on this today.
8. The recommendation/audit-due engine, the mechanic that makes "sustain"
   more than a word; currently web-only, not something to lose in the port.
9. First-party analytics with no sensitive payload shape, if/when it is built
   for mobile.
10. The "what deliberately does not exist" list in the mobile README:
    explicit non-goals recorded in writing, the same practice this backlog
    already uses to stop settled decisions from being reopened without
    evidence.

## Largest verified gaps

1. No recommendation/sustain engine on mobile, the app can be "done" with a
   card but nothing tells a returning user what is due.
2. No mode selection on mobile (random / room / one-S), one linear path only.
3. No photo capture on mobile, before/after is currently a web-only feature.
4. No analytics on mobile, 5B.11's "continuous improvement loop" and 5.2's
   retention question (EXP-004) cannot be answered for the app without this.
5. No timer on mobile.
6. No progress map view on mobile, only counts.
7. Device verification gap, not a code gap: nothing about the picker,
   accessibility, or performance has run on a real phone yet (5B.4, half of
   5B.9).
8. No competitive-pattern evidence exists that meets this repository's own
   evidence bar; the search tool available here returns SEO content, not
   product documentation.

## Riskiest assumptions

1. That closing the parity gaps above (recommendation engine, modes, photos,
   analytics) is worth doing before device verification, rather than after.
   The honest order, per this backlog's own rule ("nothing that adds product
   matters until it can be bought" / measured), is device-verify the MVP
   first, since an unverified core loop makes every larger feature moot if
   the picker or the loop itself does not actually work on a phone.
2. That `AsyncStorage` will hold up as photo capture is added later; photos
   as base64 in `AsyncStorage` would be a real performance and storage risk,
   not tested here since photo capture does not exist on mobile yet.
3. That "no network calls at all" survives contact with analytics, once
   built; the two goals (measure retention, never phone home) need a
   deliberate design, not an assumption that first-party analytics is
   automatically as safe on-device as it is in the browser.
4. That the sequential-walk-only mode on mobile matches what users actually
   want; the web app offers three because Phil's team judged all three
   necessary, and nothing has tested whether mobile can ship with fewer.

## Go/no-go recommendation

**Go, narrowly.** The core loop (draw, do, done, stop, resume) is real, code
complete per this reading, and unit-verified for the one piece that touches
someone else's data (the import merge). The single highest-value next step
is not more building: it is the device verification 5B.4 already names and
cycle 34's own retro repeats, Phil scanning the Expo QR code once. Building
further parity features (recommendation engine, modes, photos, analytics)
before that verification risks compounding unverified code on top of an
unverified core loop. Recommend 5B.2 (product target / migration contract)
proceed on paper now, since it does not need a device, but recommend against
starting the parity build-out itself until 5B.4 closes.

## What was checked to produce this

`site/assets/js/quest.js` (full read), `site/assets/js/quest-data.js` (parsed
as JSON, not sampled), `site/sw.js` (existence and registration site),
`site/privacy.html`, `site/accessibility.html`, `mobile/quest-app/App.js`
(full read), `mobile/quest-app/README.md`, `mobile/quest-app/assets/quest-corpus.json`
(header fields), `CURRENT_STATE_AUDIT.md`, `RETRO-2026-08-31-cycle34.md`,
`BACKLOG-2026-H2.md` epic 5B, one `WebFetch` against the live site (blocked,
confirming the standing egress wall), one `WebSearch` query (returned
low-confidence results, not used as evidence). `git status`/`git log` for the
baseline.
