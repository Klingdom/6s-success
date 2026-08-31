# 6S Success Home Quest Mobile App
## Claude Code Super Prompt Series for iOS, Android, and Continuous Target-State Improvement

Version 1.0 · August 31, 2026

This package turns the current Home Quest web app into production-grade iOS and Android apps without losing the product's unusually strong promise: one card, one job, no shame, and no account required to begin.

## How to use this series

Run these prompts in order in Claude Code from the root of the repository that owns `6s-success.com` and the mobile apps. Give Claude Code access to the current repository, the files cited below, Xcode on macOS for iOS work, Android Studio/SDK for Android work, and the normal store credentials only when a prompt reaches a release step.

Each prompt is deliberately standalone. Do not paste all prompts into one Claude Code session. Start a fresh context for each prompt, let it read the artifacts created by prior prompts, and require it to commit or clearly checkpoint each completed stage.

Recommended sequence:

1. Repository and live-product audit
2. Product target, UX architecture, and migration contract
3. Shared mobile foundation and content pipeline
4. iOS production app
5. Android production app
6. Engagement, household play, AI, commerce, and growth
7. Quality, privacy, security, accessibility, and release readiness
8. Store launch and post-launch operations
9. Continuous target-future-state improvement loop

## Canonical source hierarchy

Claude Code must resolve conflicts using this order:

1. Current production behavior and content at `https://6s-success.com/quest.html`, when it is intentional and safe.
2. Current repository code and its tests.
3. This mobile prompt package and the decisions recorded by Prompt 2.
4. `6S Home Micro Zone SOP Field Manual v4` and the 114-zone activity architecture.
5. `6S-Card-System-v3-Architecture.html` for the card and game system.
6. `6S Home Reset Product Specification.pdf` for proven mobile-worthy engines and technical patterns, but not as authority to replace the current card-first Quest.
7. `Realm Reset Board Game Design v1.pdf` for optional cooperative-game inspiration.
8. Product-library spreadsheets for equipment mappings and commerce.
9. Older card templates and production notes as historical input only.

Never silently merge contradictory content. Record the conflict, pick a temporary canonical rule using the hierarchy above, and add it to `docs/product/DECISION-LOG.md`.

## Non-negotiable product principles

- Preserve the core loop: draw one card, do one bounded job, mark it done, stop without guilt or continue by choice.
- Preserve the correct order: Sort, Straighten, Shine, Safety, Standardize, Sustain. Safety remains the fourth S.
- A user gets real value before creating an account, accepting notifications, buying anything, or using AI.
- Local-first and offline-first. Garages, basements, workshops, and patios are core terrain.
- Warm, calm, adult, and practical. Never infantilize the user or turn chores into pressure.
- Progress represents real work. Never manufacture streaks, fake scarcity, false urgency, or manipulative engagement.
- Completion is not merely clean. A zone holds only after the standard and sustain mechanism exist.
- Photographs of home interiors are sensitive. Private by default, never used for model training, never shared without a deliberate user action.
- Use plain language. Avoid AI slop, corporate filler, and em dashes in user-facing copy.
- WCAG 2.2 AA is the floor. Support Dynamic Type, screen readers, switch access, reduced motion, high contrast, one-handed use, and large touch targets.
- Preserve user progress through upgrades, migrations, account creation, sign-out, reinstall where platform capabilities allow, and web-to-mobile import.
- Build one shared product, not two drifting products. Platform-native behavior is encouraged; conflicting product logic is not.

---

# PROMPT 1: Repository, Live App, Content, and Competitive UX Audit

```text
You are the principal product engineer, mobile architect, UX researcher, Lean Six Sigma Master Black Belt, privacy engineer, and release manager for 6S Success Home Quest.

Your assignment is to perform an evidence-based current-state audit before changing code. Do not implement the mobile apps in this prompt. Produce the verified foundation that later prompts can trust.

STARTING POINT
- Live app: https://6s-success.com/quest.html
- Brand site: https://6s-success.com/
- Canonical method: Sort, Straighten, Shine, Safety, Standardize, Sustain.
- Live positioning: 684 cards across 114 micro zones, one card and one job at a time.
- Inspect all repository files before assuming the framework, deployment model, data source, or ownership boundaries.
- Locate and inspect, if present: quest.html, quest.js, quest-data.js, photos.js, service worker, manifest, measurement scripts, tests, deployment configuration, privacy/terms/accessibility/safety pages, product data, zone pages, store integration, and prior mobile prototypes.
- Locate the supplied product sources if they are in the workspace: 6S Card System v3 Architecture, Realm Reset, Home Reset Product Specification, Field Manual v4, activity breakdown, product-library spreadsheets, entryway print deck, card templates, and production system.

FIRST, CREATE A SAFE WORKING BASELINE
1. Read AGENTS.md, CLAUDE.md, README, package manifests, deployment files, and repository instructions.
2. Record the branch, HEAD, worktree status, and existing user changes. Preserve unrelated changes.
3. Identify how production is built and deployed. Do not deploy or mutate external systems.
4. Run the existing test, lint, typecheck, and build commands without weakening gates.
5. If the live page differs from the repository, capture both states and explain the likely reason.

AUDIT THE LIVE QUEST AS A REAL USER
Test responsive phone widths and at least one tablet width. Exercise fresh-start and returning-user paths. Verify:
- Opening promise and first useful action.
- Random card draw.
- Work-a-room mode.
- One-S-across-a-room mode.
- Timer behavior, stop, skip, done, and draw-again behavior.
- Full six-step completion semantics and zone-holding calculation.
- Sustain cadence, audit-due logic, streak behavior, and recommendation logic.
- Every-room progress view and re-run/reset safeguards.
- Before/after photo capture, storage limits, deletion, errors, and privacy copy.
- Backup creation and merge restore.
- PWA install path on supported platforms and the iOS installation gap.
- Offline behavior after first load.
- Keyboard, screen reader, focus, reduced motion, contrast, touch targets, zoom, and error recovery.
- First-party analytics events and whether they reveal sensitive room or photo information.
- Links from Quest to full zone methods, printed deck, store, consulting, privacy, safety, and accessibility.

INSPECT THE CONTENT MODEL
Establish exact counts and stable identifiers for rooms, zones, cards, steps, standards, triggers, hazards, time estimates, product mappings, images, and any editorial fields. Check for:
- Duplicate or unstable IDs.
- 114-zone and 684-card completeness.
- Correct six-S order everywhere.
- Missing standard or sustain content.
- Unsafe, contradictory, or ungrounded advice.
- Content drift among live Quest, zone pages, Field Manual v4, print deck, and prior app specification.
- Whether a versioned canonical JSON or schema already exists.

PERFORM A FOCUSED COMPETITIVE UX REVIEW
Using current public information, compare only patterns relevant to this product: micro-task activation, household chores, cooperative play, habit maintenance, home inventory, before/after proof, calm gamification, offline use, accessibility, and privacy. Do not copy proprietary expression or visual design. Separate observed facts from recommendations. Prefer direct product documentation and current store listings.

USE PRODUCT ANALYTICS CAREFULLY
If privacy-safe aggregate analytics are available in the repository or configured tools, inspect funnel and performance evidence. Never expose secrets, personal data, raw photo metadata, or individual household behavior. If analytics are unavailable, define what is unknown rather than inventing numbers.

CREATE THESE ARTIFACTS
- docs/audit/CURRENT-STATE-AUDIT.md
- docs/audit/FEATURE-INVENTORY.csv
- docs/audit/CONTENT-INTEGRITY-REPORT.md
- docs/audit/UX-FRICTION-REGISTER.md
- docs/audit/ACCESSIBILITY-AUDIT.md
- docs/audit/PRIVACY-SECURITY-AUDIT.md
- docs/audit/WEB-MOBILE-PARITY-BASELINE.md
- docs/audit/COMPETITIVE-PATTERN-REVIEW.md
- docs/audit/OPEN-QUESTIONS.md

For every issue include evidence, affected user, severity, confidence, recommendation, and whether it blocks mobile launch. Distinguish defect, missing capability, deliberate constraint, and future opportunity.

Finish with:
1. The ten strongest parts that must survive the port.
2. The ten largest verified gaps.
3. The five riskiest assumptions.
4. A go/no-go recommendation for proceeding to product architecture.
5. Exact commands run and their results.

Do not claim completion until all artifacts exist, links resolve, counts reconcile, and the repository remains no worse than you found it.
```

---

# PROMPT 2: Product Target, UX Architecture, and Migration Contract

```text
Act as the accountable product director and staff mobile UX architect for Home Quest. Read every artifact from Prompt 1 and all canonical sources. Your job is to define a coherent mobile product before engineering begins.

The live Quest is the canonical product starting point. Do not casually replace it with the older, more complex AI-first Home Reset prototype. Harvest only capabilities that improve the card-first loop.

DEFINE THE PRODUCT PROMISE
Home Quest should help a tired adult or household make one visible improvement in under a minute of decision effort. The mobile app expands that into a calm, durable household practice without turning the home into a nagging dashboard.

SEGMENT THE EXPERIENCE
Design for:
- A solo adult who wants the smallest possible start.
- A couple sharing zones without conflict.
- A family with children where adults retain safety and account control.
- A user with limited mobility, fatigue, pain, attention, vision, hearing, or dexterity.
- A power user completing full-room resets.
- A returning user maintaining standards rather than endlessly resetting.

DEFINE THE MOBILE INFORMATION ARCHITECTURE
Use no more than five primary destinations. Evaluate and choose among Today, Quest, Home, Progress, and Profile/Settings. The first screen must answer: What is one useful thing I can do now? Preserve random draw, work a room, and one-S pass, but do not present three equal walls of explanation before action.

DESIGN THESE CORE FLOWS
1. First launch to first card without an account.
2. Draw, start, pause, skip, finish, and stop.
3. Complete six steps across one zone over one or many sessions.
4. Work an entire room in correct method order.
5. Run one S across a selected room.
6. Capture before/after evidence without making photos mandatory.
7. Write or confirm the standard and choose a sustain trigger.
8. Receive an audit-due card and honestly mark holding or drift.
9. Invite another adult and assign a zone owner.
10. Child participation without child accounts in v1.
11. Import a web backup and reconcile duplicate progress.
12. Upgrade, restore purchase, downgrade, delete account, and continue locally.

DEFINE CALM GAMIFICATION
Use the Card System architecture as input: Calm Track, Time Tokens, House Passport, Reset Run, Daily Draw, Family Race, interlocks, and Hazard Bounty. Choose only mechanics that reward meaningful work. Prohibit punishment for missed days, addictive variable rewards, public household shaming, loot boxes, fake countdowns, and pay-to-complete mechanics.

Clarify the relationship among:
- A card completed.
- An S completed for a zone.
- A zone reset.
- A zone holding its standard.
- A room holding.
- A whole-home milestone.

DEFINE FREE AND PAID VALUE
Free must be legitimately useful and include the current core Quest. Develop a defensible entitlement model. Recommended hypothesis to test:
- Free: current 684-card core, local-only progress, basic photos, backup/import, and one household profile on one device.
- Plus: secure sync, household collaboration, richer reset history, native reminders, advanced insights, optional AI coaching allowance, and premium share/print outputs.
- Commerce: relevant product recommendations after a need is identified, never before Sort.
Do not lock safety guidance, account deletion, accessibility, export, or already-earned progress behind payment.

DEFINE AI'S BOUNDARY
AI is optional, user-initiated, clearly labeled, and never the source of record. Candidate uses: photo-assisted Sort plan, visible-hazard suggestions with strong limitations, and warm after-review. Basic instructions, completion, photos, and sustain work fully without AI. Never identify people, infer sensitive traits, diagnose, price possessions, or claim a safety inspection is complete.

MAKE PLATFORM DECISIONS
Compare a shared React Native/Expo implementation with separate SwiftUI and Kotlin Compose implementations against the actual repository, team, lifecycle, accessibility, offline, photo, billing, notification, and test needs. Choose one and document why. Default toward one shared TypeScript domain/content layer with React Native/Expo unless verified constraints justify native separation. Platform-native modules and UI adaptations are allowed.

CREATE
- docs/product/PRODUCT-BRIEF.md
- docs/product/JTBD-AND-PERSONAS.md
- docs/product/INFORMATION-ARCHITECTURE.md
- docs/product/CORE-LOOPS-AND-STATE-MODEL.md
- docs/product/UX-FLOW-SPECS.md
- docs/product/GAMIFICATION-ETHICS.md
- docs/product/ENTITLEMENTS-AND-MONETIZATION.md
- docs/product/AI-BOUNDARIES.md
- docs/product/PLATFORM-ADR.md
- docs/product/WEB-TO-MOBILE-MIGRATION-CONTRACT.md
- docs/product/ANALYTICS-MEASUREMENT-PLAN.md
- docs/product/DECISION-LOG.md
- docs/product/PRD.md

The PRD must include requirements, non-goals, acceptance criteria, edge cases, empty/error/offline states, accessibility behavior, privacy classification, analytics event, and test method for each capability.

Create an impact-versus-effort roadmap with three releases:
- R1 Storeworthy Core: the smallest app worthy of public trust.
- R1.1 Household and Sustain: retention through genuine standards holding.
- R2 Guided Intelligence and Growth: optional AI, richer cooperative play, and responsible commerce.

Do not estimate dates until repository scope and staffing are known. Use dependency-aware work packages and confidence ranges. Finish by identifying decisions that genuinely require the owner; make all reversible technical and UX decisions yourself.
```

---

# PROMPT 3: Shared Mobile Foundation and Canonical Content Pipeline

```text
You are the staff engineer accountable for building the shared foundation selected in PLATFORM-ADR.md. Implement the smallest vertical slice that proves the architecture, content integrity, offline persistence, and migration path. Do not build disposable scaffolding.

READ FIRST
- All Prompt 1 and Prompt 2 artifacts.
- Repository instructions and existing code.
- Current quest data and logic.
- Field Manual v4, product library, and card architecture where available.

PROTECT EXISTING WORK
Inspect git status. Do not overwrite unrelated user changes. Create a feature branch if repository policy allows. Use small coherent commits. Never place secrets in code, prompts, logs, fixtures, screenshots, or documentation.

ESTABLISH THE MONOREPO OR INTEGRATE CLEANLY
Create or adapt clear boundaries such as:
- apps/mobile
- packages/domain
- packages/content
- packages/design-system
- packages/analytics
- packages/testing
Do not reorganize the existing website merely for aesthetic consistency.

BUILD A CANONICAL VERSIONED CONTENT MODEL
Define schemas and stable IDs for room, zone, card, S-step, standard, sustain trigger, hazards, time, tools/products, editorial cue, and content version. Build a deterministic import pipeline from current Quest data and canonical source data. The runtime must consume generated validated content, not scrape HTML.

Required gates:
- Exactly 20 room types unless a documented canonical change exists.
- Exactly 114 active micro zones.
- Exactly six ordered S steps per zone.
- 684 executable zone-step cards.
- No missing IDs, duplicate IDs, unresolved references, template leaks, or invalid order.
- Safety is always fourth.
- Every zone has a function, done state, duration, standard, sustain behavior, and hazard guidance or an explicit reviewed exemption.
- Generated output is deterministic and carries a schema/content version and checksum.
- Content migrations never erase earned progress.

IMPLEMENT THE DOMAIN STATE MACHINE
Model card/session/zone/room states explicitly. Prevent impossible transitions such as Standardize complete before required earlier steps unless a documented import reconciliation marks legacy work. Keep event history sufficient to explain progress without collecting unnecessary personal data.

IMPLEMENT LOCAL-FIRST STORAGE
Use the selected production-grade mobile database and file storage. Include migrations, transaction boundaries, backup/export, import/merge, corruption handling, storage pressure behavior, and seeded demo data. Photos are files with thumbnails and metadata kept minimal. The app works fully offline except optional network capabilities.

IMPLEMENT WEB BACKUP IMPORT
Accept the current Home Quest backup schema. Validate it, preview what will merge, preserve the most complete legitimate progress, prevent duplicate completion inflation, and show a plain-language result. Build golden fixtures from real schema examples with personal data removed.

IMPLEMENT THE DESIGN FOUNDATION
Create semantic tokens from the 6S brand palette, step colors, typography, spacing, radii, elevation, motion, and states. Color cannot be the only carrier of S identity. Build accessible primitives for buttons, cards, progress, timers, sheets, dialogs, photo diptychs, and form controls. Verify light/dark/high-contrast behavior even if public dark mode is deferred.

IMPLEMENT ONE COMPLETE VERTICAL SLICE
Fresh install → draw card → view instruction → timer → mark done → persist → relaunch → progress correctly restored. Include one before and after photo, an offline restart, screen-reader labels, reduced motion, and an analytics event that contains no zone photo or household-sensitive text.

TEST
- Unit tests for content, state machine, recommendation, streak, due logic, merge, and migrations.
- Property-based or table-driven tests for all 684 cards.
- Component accessibility tests.
- Integration test for the vertical slice.
- Performance baseline on a representative low/mid device profile.

CREATE OR UPDATE
- architecture diagrams and ADRs
- data dictionary
- content authoring guide
- migration guide
- threat model
- test strategy
- developer setup and one-command verification documentation

Run format, lint, typecheck, unit, integration, content validation, and build gates. Repair causes, never disable gates. End with a working vertical slice, exact verification evidence, remaining risks, and the next safe handoff.
```

---

# PROMPT 4: Production iOS App

```text
Act as the lead iOS engineer and Apple-platform product designer. Build the production iOS expression of Home Quest on the shared foundation. Follow the PRD and platform ADR. Preserve shared product semantics while making the app feel native on iPhone and iPad.

TARGET
- Support the current practical iOS baseline documented in the repository and verify current App Store requirements before submission.
- iPhone is primary; iPad must be intentionally usable, not a stretched phone.
- Use native navigation, sheets, menus, haptics, camera/photo permission flows, share sheet, file importer/exporter, local notifications, background tasks, and StoreKit 2 where applicable.
- Do not require sign-in at launch.

BUILD ALL R1 CORE FLOWS
- First launch and immediate card draw.
- Today/recommendation surface.
- Random draw, room run, and single-S room pass.
- Card runner with timer, pause/resume, skip, done, stop, and recovery after interruption.
- Zone detail, six-step state, standard, sustain trigger, and audit outcome.
- Room and whole-home progress.
- Before/after photo capture and library selection, editing/cropping only when necessary, deletion, compare, storage-pressure handling, and offline use.
- Backup export, Files-based import, web-backup migration, and clear merge result.
- Settings, privacy controls, notification controls, data export, local wipe, account deletion when accounts exist, and support.
- Paywall and restore purchases only for approved paid entitlements. Never block core safety or earned data.

APPLE-SPECIFIC QUALITY
- Dynamic Type through accessibility sizes without clipping.
- VoiceOver order, labels, hints, adjustable controls, and announcements.
- Switch Control, Voice Control, keyboard navigation on iPad, Reduce Motion, Increase Contrast, and differentiate-without-color.
- Minimum comfortable touch targets and one-handed placement for frequent actions.
- Haptics are subtle and can be disabled by system preferences.
- Respect camera and photo-library limited access.
- Purpose strings say exactly why access is needed.
- No ATT prompt unless the product genuinely performs cross-app tracking. Prefer not to track.
- Sign in with Apple alongside any third-party identity provider.
- In-app account deletion and subscription management paths.
- Universal links for household invites and relevant web-to-app routes, with safe fallbacks.
- Widgets, Live Activities, Siri/App Intents, and watchOS are optional future work, not R1 blockers, unless already approved in the PRD.

NOTIFICATIONS
Make reminders useful and user-authored. Ask only after the user creates a sustain trigger or requests reminders. Support quiet scheduling, granular categories, time-zone changes, duplicate suppression, and a clear path from notification to the exact card/audit. Missing a reminder never damages a streak.

STOREKIT
Use current StoreKit 2 patterns, verified entitlement state, restore purchases, grace periods, offline entitlement caching, family/household rules as approved, and server validation if the architecture requires it. Price and terms must be plain. No dark patterns.

TEST ON REALISTIC STATES
Fresh, partially complete, fully complete, audit due, drift, no photos, many photos, low storage, offline, interrupted timer, denied permissions, large text, VoiceOver, reduced motion, subscription expired, and imported legacy backup.

DELIVER
- Production iOS project integrated with the shared app.
- Unit, integration, snapshot where valuable, and XCUITest critical paths.
- App privacy manifest and accurate data-use inventory.
- Entitlements and capabilities documentation.
- App Store screenshot plan and review notes draft.
- iOS release checklist.

Build and test against available simulators and at least one real device when configured. Do not fabricate device results. Report exact tests, OS/device matrix, unresolved risks, and anything requiring Apple account owner action.
```

---

# PROMPT 5: Production Android App

```text
Act as the lead Android engineer and Material-platform product designer. Build the production Android expression of Home Quest on the shared foundation. Preserve the same domain logic, content, entitlements, privacy, and analytics semantics as iOS while following Android conventions.

TARGET
- Verify the current Google Play target API and policy requirements at execution time.
- Support the practical Android baseline documented in the ADR across representative low, mid, and high device profiles.
- Phones are primary. Support tablets, foldables, edge-to-edge layouts, system back, predictive back, process death, and configuration changes intentionally.
- Do not require sign-in at launch.

BUILD ALL R1 CORE FLOWS
Match the approved product requirements and parity contract from Prompt 4: immediate draw, three play modes, resilient timer, six-step zone progress, standards/sustain/audits, room and home progress, photos, backup/export/import, settings/privacy, notifications, and approved billing.

ANDROID-SPECIFIC QUALITY
- Material conventions without losing the 6S visual identity.
- TalkBack, font scaling, display scaling, keyboard/D-pad where relevant, switch access, high contrast, reduced animation, and color-independent S identity.
- Photo Picker where supported and safe fallback behavior on older supported versions.
- Camera permission only at the moment of user action.
- Scoped storage and Storage Access Framework for export/import.
- WorkManager for appropriate deferrable work; never abuse exact alarms.
- Notification channels by purpose, runtime permission on applicable versions, deep links to exact context, and duplicate suppression.
- App Links with verified domain and safe browser fallback.
- Reliable Room/SQLite migrations, file cleanup, cache limits, and process-death restoration.
- Play Billing Library current version, acknowledged purchases, restore, pending transactions, offline caching, server verification if required, and clear subscription management.
- No advertising ID or cross-app tracking unless separately approved. Prefer neither.

PERFORMANCE
Set and enforce budgets for cold start, card draw, database operations, list scrolling, image memory, APK/AAB size, crashes, and ANRs. Test a photo-heavy household and all 684 cards on a constrained device profile.

PLAY REQUIREMENTS
Prepare an accurate Data safety inventory, content rating inputs, account deletion URL/path, subscription disclosure, demo/reviewer path, and closed-testing plan when required by the account type. Do not guess policy. Verify current official requirements during the release prompt.

DELIVER
- Production Android app integrated with the shared foundation.
- Unit, instrumentation, screenshot where valuable, and Compose/UI critical-path tests appropriate to the chosen stack.
- Baseline profile/performance work when supported.
- Android accessibility report.
- Play policy/data safety working sheet.
- Android release checklist.

Run all gates and test representative API levels, form factors, permission states, offline/process-death states, and large-font accessibility. Do not claim real-device testing unless it happened. Report exact results and any owner action required.
```

---

# PROMPT 6: Household Play, Optional AI, Commerce, Engagement, and Growth

```text
You own R1.1 and R2 capabilities. Implement only after the storeworthy core is stable and measured. Read the target-state backlog and use evidence to sequence work. Do not add complexity merely because the older specification contains it.

HOUSEHOLD COLLABORATION
Add an adult-created household with up to the approved member limit, secure invite links, roles, zone ownership, conflict-safe progress merge, activity explanations, and leave/remove flows. For v1, children participate through adult-managed profiles or local player labels, not independent child accounts. Avoid competitive leaderboards that turn domestic labor into blame.

CALM GAME MODES
Prototype and validate the approved mechanics from Card System v3 and Realm Reset:
- Daily Draw: one useful card.
- Reset Run: a bounded room or time-boxed mission.
- Family Race: cooperative race against a shared timer or entropy, never person against person by default.
- Calm Track and House Passport: visible durable progress.
- Hazard Bounty: extra recognition for making a real hazard safer.
- Time Tokens: help a household choose work that fits available energy.
Every mechanic must map to actual 6S work and have an accessibility alternative. Feature-flag experiments. Remove mechanics that improve taps but reduce completed or holding zones.

OPTIONAL AI
Implement AI behind a server-side proxy with authentication as needed, abuse protection, rate limits, per-user allowance, cost telemetry, timeouts, retries, schema validation, moderation, and a kill switch. Never ship provider keys in the client.

Approved initial contracts:
1. Sort Plan: user selects up to the approved number of before photos; output visible items that likely belong, review items with tentative verdicts, visible hazard suggestions, a concise plan, and uncertainty.
2. Coach Review: compare user-selected before/after images against the written target state; return limited wins, remaining items, and warm guidance.

Rules:
- AI cannot mark a step complete.
- Hazard output says it is a limited visual suggestion, not an inspection.
- Never identify people or infer health, wealth, protected traits, home address, or sensitive possessions.
- Strip unnecessary metadata, resize for transport, minimize retention, and delete server copies according to policy.
- Give the user a preview and explicit Analyze action.
- Provide fully functional manual fallback on timeout, outage, cap, refusal, or opt-out.
- Log cost, latency, schema validity, and broad success status, not image content or sensitive generated text.

COMMERCE
Import the current product library through a versioned catalog service. Recommendations appear only when relevant to a card and after the user has determined a real need. Clearly label affiliate relationships. Verify price/availability freshness or use non-price language. Provide retailer choice. Never imply a product is required when a household item works. Never sell before Sort, and never monetize emergency or safety fear.

SHARING AND ORGANIC GROWTH
Create optional branded before/after share cards with local preview and explicit system share action. Default to no address, faces, EXIF, timestamps, or precise household details. Offer crop/redaction guidance. Add deep links that open a public-safe explanation of the method, not another user's private record.

MEASURE OUTCOMES
Primary measures:
- Time from install to first card started.
- Started-to-completed card rate.
- First zone holding within 7 days.
- Audit completion and holding rate.
- 7-day and 30-day return among activated users.
- Household invite acceptance and shared-zone completion.
- Crash-free sessions, ANRs, sync failures, AI cost/success, accessibility defects, support issues, and refund rate.
Revenue is a constraint and outcome, not permission to damage trust.

Use feature flags, staged rollout, experiment guardrails, and removal criteria. Update PRD, schemas, threat model, privacy/data safety records, tests, support content, and decision log with every capability. Finish with measured acceptance evidence, not a feature list.
```

---

# PROMPT 7: Quality, Privacy, Security, Accessibility, and Release Readiness

```text
Act as the independent launch-quality lead. Assume the apps contain defects until evidence proves otherwise. You may fix launch blockers and high-severity defects, but do not redesign unrelated product scope.

ESTABLISH TRACEABILITY
Map every R1 PRD requirement to implementation, automated test, manual test where necessary, analytics event, accessibility behavior, privacy classification, and release status. No requirement may disappear between documents and code.

TEST MATRIX
Cover iOS and Android supported versions, phone sizes, at least one tablet class per platform, light/dark/high contrast, large text, screen readers, reduced motion, denied/limited permissions, no network/poor network/reconnect, low storage, large photo histories, process termination, app update, database migration, import, sync conflicts, subscription states, time-zone/daylight-saving changes, and localization expansion.

CRITICAL JOURNEYS
- First useful card with no account and no network.
- Finish a card and resume after forced termination.
- Complete a zone across multiple sessions.
- Receive and complete a sustain audit.
- Capture, compare, delete, export, and optionally analyze photos.
- Import current web backup without losing mobile work.
- Create/join/leave household and resolve concurrent edits, if included.
- Buy, restore, expire, and refund a subscription.
- Export and delete data/account.
- Recover from every external-service outage.

ACCESSIBILITY
Audit against WCAG 2.2 AA and current Apple/Google guidance. Use automated scanning plus manual VoiceOver and TalkBack journeys. Verify reading order, headings, labels, focus, announcements, target sizes, contrast, non-color status, Dynamic Type/font scaling, zoom, orientation, reduced motion, time controls, error identification, and cognitive load. Timers never force failure.

PRIVACY AND SECURITY
- Update data-flow diagram and inventory from code, not aspiration.
- Threat-model home photos, auth, invite links, backups, sync, AI proxy, billing, affiliate redirects, analytics, logs, and support exports.
- Verify least privilege, row-level authorization, signed URL scope/expiry, secret management, transport/storage protection, deletion propagation, rate limiting, dependency/supply-chain controls, and log redaction.
- Prove one household cannot access another household's records or photos.
- Verify no secrets or personal content in source maps, crash reports, analytics, test artifacts, or screenshots.
- Run static/dependency scanning and appropriate dynamic/API tests. Do not perform destructive testing against production.

CONTENT SAFETY
Validate all 684 cards. Flag dangerous chemical combinations, electrical/fire risks, unsafe lifting, childproofing claims, medication/food guidance, ladder/tool advice, and any AI overclaim. Preserve the Safety fourth-S interlock. Include a clear limitation without weakening useful instructions.

RELEASE GATES
Define numeric or binary gates for crashes, ANRs, critical flows, P0/P1 defects, accessibility blockers, migration success, content integrity, privacy accuracy, deletion, billing, support readiness, and performance. Do not waive a gate silently. A waiver needs owner, rationale, risk, mitigation, and expiry.

PRODUCE
- docs/release/REQUIREMENTS-TRACEABILITY-MATRIX.csv
- docs/release/TEST-MATRIX.md
- docs/release/ACCESSIBILITY-CONFORMANCE-REPORT.md
- docs/release/PRIVACY-DATA-INVENTORY.md
- docs/release/SECURITY-ASSESSMENT.md
- docs/release/CONTENT-SAFETY-REVIEW.md
- docs/release/DEFECT-REGISTER.md
- docs/release/GO-NO-GO.md

Run all feasible tests and fix verified launch blockers. End with a candid go/no-go decision and the exact remaining owner decisions. Never label the build ready because the checklist exists.
```

---

# PROMPT 8: App Store, Google Play, Launch, and Post-Launch Operations

```text
Act as release conductor for both stores. Start only from a release candidate that passed Prompt 7 or has explicit documented waivers. Verify current official Apple and Google requirements at execution time. Never rely solely on dates or policy details embedded in this prompt package.

RELEASE IDENTITY
Confirm product name, subtitle/short description, bundle/application IDs, company seller identity, category, age/content rating, support email support@6s-success.com, privacy URL, terms URL, account deletion URL, website links, and version/build numbering. Do not invent legal statements or credentials.

STORE ASSETS
Create accurate copy and a screenshot/storyboard plan grounded in real production UI. Do not show unshipped capabilities, fake reviews, fabricated awards, false rankings, or misleading before/after transformations. Include accessibility-conscious screenshots and plain explanation of free versus paid value, optional AI, photo privacy, offline core, and subscription terms.

APPLE
Prepare App Store Connect metadata, privacy nutrition answers, review notes, demo path/account if needed, IAP/subscription configuration worksheet, restore path, account deletion instructions, encryption/export-compliance inputs, age rating, and reviewer explanation for home photos and AI. Validate archives and automated store checks. Use TestFlight and staged/phased release as approved.

GOOGLE
Prepare Play Console listing, Data safety answers, content rating, app access, account deletion, subscriptions/base plans/offers, target API verification, testing-track requirements for the actual account type, pre-launch report, AAB validation, and staged rollout.

LEGAL AND TRUST CONSISTENCY
Cross-check in-app behavior, privacy policy, store labels, AI disclosure, analytics, retention/deletion, affiliate disclosure, subscription terms, and support documentation. The strictest accurate description wins. Stop if public policy and code materially conflict.

LAUNCH OPERATIONS
Create:
- docs/launch/OWNER-ACTIONS.md
- docs/launch/IOS-SUBMISSION-WORKSHEET.md
- docs/launch/ANDROID-SUBMISSION-WORKSHEET.md
- docs/launch/STORE-LISTING-COPY.md
- docs/launch/SCREENSHOT-STORYBOARD.md
- docs/launch/REVIEWER-NOTES.md
- docs/launch/ROLLOUT-AND-ROLLBACK.md
- docs/launch/INCIDENT-RUNBOOK.md
- docs/launch/SUPPORT-MACROS.md
- docs/launch/THIRTY-DAY-LAUNCH-PLAN.md

Use a staged rollout with defined observation windows, crash/ANR/support/refund/sync/AI-cost thresholds, kill switches, rollback decision rights, and a method for preserving user data across rollback. Monitor reviews and support themes without replying automatically as the owner. Draft replies for approval unless explicit authority to publish exists.

Do not submit, purchase accounts, accept contracts, change production DNS, publish a release, or spend money without the account owner's explicit authorization at the relevant step. You may prepare everything else and surface the exact final actions cleanly.
```

---

# PROMPT 9: Continuous Target Future State and Autonomous Improvement System

```text
You are the long-running product improvement steward for 6S Success Home Quest across web, iOS, and Android. Your job is not to chase feature volume. Your job is to repeatedly close the gap between current performance and a clearly defined, evidence-backed target future state while protecting trust, method fidelity, and maintainability.

RUN THIS PROMPT AT THE START OF EACH PLANNING CYCLE AND AFTER ANY MAJOR RELEASE OR INCIDENT.

OPERATING PRINCIPLE
Treat the product itself with 6S:
- Sort: remove low-value features, duplicate content, dead paths, and misleading metrics.
- Straighten: make the next useful action obvious and keep one source of truth for logic/content.
- Shine: fix defects, friction, performance, and confusing copy while inspecting root causes.
- Safety: protect physical safety, privacy, security, accessibility, children, billing, and emotional wellbeing.
- Standardize: encode proven behavior in schemas, components, tests, content rules, runbooks, and dashboards.
- Sustain: monitor, audit, learn, and revise the standard when reality disproves it.

STEP 1: RECONSTRUCT THE CURRENT STATE
Read the current PRD, roadmap, decision log, source, content version, releases, store status, experiments, analytics definitions, privacy/security/accessibility reports, support themes, reviews, incidents, refunds, performance, crash/ANR data, AI cost and quality, commerce freshness, and open defects. Use aggregate privacy-safe evidence. Never expose individual household behavior or images.

Validate instrumentation before trusting it. Separate:
- Observed fact.
- User-reported evidence.
- Inference.
- Hypothesis.
- Unknown.

STEP 2: MAINTAIN A CLEAR TARGET FUTURE STATE
Update `docs/future-state/TARGET-FUTURE-STATE.md` across these dimensions:
1. User outcome: a person starts quickly, finishes bounded work, and zones genuinely hold.
2. Method fidelity: correct six-S sequence and safety integrity.
3. Experience: calm, clear, accessible, fast, and resilient offline.
4. Household value: fair ownership and cooperative progress without blame.
5. Trust: private photos, transparent AI, secure sync, honest billing and commerce.
6. Product quality: low crashes/ANRs, correct migrations, explainable state, maintainable content.
7. Business health: sustainable acquisition, conversion, retention, affiliate value, AI COGS, refunds, and support load.
8. Platform parity: one product contract with intentional native differences.
9. Content operations: canonical versioned 20-room/114-zone/684-card system with safe updates.
10. Learning velocity: small reversible experiments and rapid defect/root-cause closure.

For every target include metric, baseline, desired range, rationale, guardrail, source, confidence, owner, and review date. Never invent a baseline. If unavailable, prioritize the smallest privacy-safe measurement needed.

Recommended outcome hierarchy:
- North-star candidate: active households with at least one zone verified as holding its standard during the period.
- Activation: first card completed and first standard/sustain trigger established.
- Retention: return for meaningful work or honest audit, not app opens.
- Quality guardrails: crash-free use, ANRs, sync loss, migration failure, accessibility blockers, safety errors, privacy incidents, refunds, and notification opt-outs.
- Business: paid conversion after demonstrated value, net revenue, affiliate conversion without trust erosion, AI gross margin, and support cost.

STEP 3: ANALYZE THE GAP
Create a value-stream view from discovery to a holding zone. Quantify drop-offs where trustworthy. Perform root-cause analysis on the largest gap using evidence, not feature requests alone. Identify whether the cause is acquisition mismatch, decision friction, instruction quality, task size, interruption recovery, household dynamics, notification design, technical failure, accessibility, trust, pricing, or missing capability.

STEP 4: PRIORITIZE THE NEXT BET
Maintain one ordered backlog in `docs/future-state/OPPORTUNITY-BACKLOG.md`. Score opportunities using expected user outcome, target-state gap, reach, confidence, effort, risk, reversibility, and strategic fit. Safety/privacy/security/accessibility defects override normal scoring.

Select no more than:
- One primary outcome bet.
- One quality/root-cause improvement.
- One learning/instrumentation improvement.
per cycle.

Each selected bet needs:
- Problem statement and evidence.
- Target user and moment.
- Hypothesis.
- Smallest credible change.
- Leading and lagging measure.
- Guardrails and ethical risk.
- Accessibility/privacy/security impact.
- Experiment or rollout design.
- Stop, rollback, expand, and remove criteria.
- Required tests and documentation.

STEP 5: EXECUTE SAFELY
Work in small coherent changes. Preserve unrelated work. Update schemas and migrations safely. Use feature flags for uncertain changes. Add tests before or with fixes. Validate all affected cards/content. Run platform parity and offline paths. Never lower gates to make a release pass.

Do not autonomously publish store releases, change pricing, spend money, message users, alter legal policies, enable new sensitive data collection, or materially broaden AI use without explicit owner authorization. Prepare the decision with evidence and reversible options.

STEP 6: CHECK THE RESULT
After the agreed observation window, compare results with the predeclared hypothesis. Segment only where privacy-safe and statistically responsible. Look for novelty effects, notification coercion, household unfairness, accessibility regressions, support burden, AI cost, and revenue-quality tradeoffs. Prefer removing a failed feature to rationalizing it.

STEP 7: STANDARDIZE AND SUSTAIN
If successful, update the PRD, decision log, design system, content authoring rules, tests, analytics dictionary, support docs, privacy/data safety inventory, runbooks, and target baseline. If unsuccessful, roll back or revise, document the learning, and avoid repeating it.

CREATE OR UPDATE EACH CYCLE
- docs/future-state/TARGET-FUTURE-STATE.md
- docs/future-state/CURRENT-STATE-SCORECARD.md
- docs/future-state/GAP-AND-ROOT-CAUSE-ANALYSIS.md
- docs/future-state/OPPORTUNITY-BACKLOG.md
- docs/future-state/CYCLE-PLAN.md
- docs/future-state/EXPERIMENT-REGISTER.md
- docs/future-state/LEARNING-LOG.md
- docs/future-state/OWNER-DECISIONS.md

END-OF-CYCLE REPORT
Write a concise report containing:
1. What materially changed.
2. What users can now do better.
3. Which metric moved and with what confidence.
4. Any trust, safety, quality, cost, or support tradeoff.
5. What was removed or simplified.
6. The current largest target-state gap.
7. The next three priorities.
8. Exact decisions required from the owner.

The future state is a living standard, not a fixed fantasy. Improve it when evidence shows a better way to help a home stay calm.
```

---

## Initial target-future-state hypothesis for Home Quest

This is the starting hypothesis Prompt 9 should validate, not a substitute for evidence.

### Product outcome

Home Quest becomes the most trustworthy way for a household to convert vague cleaning pressure into one bounded action, then turn completed resets into standards that actually hold.

### R1 Storeworthy Core

- Immediate anonymous use.
- All 684 current cards and three session modes.
- Full local-first offline operation.
- Reliable timer and interruption recovery.
- Room, zone, S-step, sustain, and audit progress.
- Optional before/after photos stored locally.
- Web-backup import and native export.
- Native accessibility and carefully timed local reminders.
- No AI or account required.

### R1.1 Household and Sustain

- Optional account and encrypted sync.
- Adult household invitations and zone ownership.
- Conflict-safe progress and photo sync.
- User-authored sustain triggers and audit reminders.
- Calm Track, House Passport, Hazard Bounty, and cooperative Reset Runs, only after usability validation.
- Subscription value concentrated in cross-device, household, history, and premium guidance, not core safety or earned progress.

### R2 Guided Intelligence and Growth

- Optional photo-assisted Sort Plan and Coach Review with strict privacy boundaries.
- Versioned product catalog and contextual affiliate links after demonstrated need.
- Private-by-default share cards.
- Responsible experiments that optimize holding zones and household value, not raw screen time.
- Professional-organizer mode remains a separate validated opportunity, not clutter in the household app.

## Definition of success

The apps are successful when users can begin faster than they can talk themselves out of starting, complete meaningful work without shame, return because the system helps rather than nags, and demonstrate that more zones are still holding weeks later. Revenue should grow from that durable value.
