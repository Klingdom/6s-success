# 6S Success Decision Register

> Durable decision memory for autonomous business, product, growth, commerce, architecture, GitHub, Hostinger VPS, Docker, data, security, and operating decisions.

## 1. Purpose

`DECISIONS.md` prevents Claude Code and specialist agents from repeatedly reopening settled questions, silently reversing strategy, or losing the reasoning behind important choices.

It records:

- what was decided
- why it was decided
- what evidence supported it
- who had authority
- what alternatives were considered
- what constraints apply
- when the decision should be revisited
- what would invalidate it

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`
- `DATA-SOURCES.md`
- `DASHBOARD.md`
- `BACKLOG.md`
- `EXPERIMENTS.md`

---

# 2. Core Rule

**Durable decisions must be explicit.**

Do not allow important decisions to exist only in:

- chat history
- agent memory
- commit messages
- Slack/email
- code comments
- dashboard state
- undocumented production configuration

If a future agent needs to know the choice and rationale, record it here.

---

# 3. What Belongs Here

Record decisions that materially affect:

- business model
- strategic sequencing
- product architecture
- customer experience
- pricing policy
- commerce
- content strategy
- SEO/AEO architecture
- data definitions
- source authority
- experimentation policy
- autonomy boundaries
- GitHub/release strategy
- VPS/Docker architecture
- backup/recovery
- security
- privacy
- major vendor selection
- significant recurring cost
- expansion gates

Do not record every routine implementation choice.

---

# 4. Decision ID

Use:

`DEC-0001`

`DEC-0002`

Never recycle IDs.

Reference decision IDs from:

- backlog items
- experiments
- PRs
- architecture docs
- runbooks
- learnings
- status updates

---

# 5. Decision Status

Use:

- `PROPOSED`
- `APPROVED`
- `ACTIVE`
- `SUPERSEDED`
- `REVERSED`
- `EXPIRED`
- `REJECTED`

Most settled decisions should be `ACTIVE`.

---

# 6. Decision Record Template

```yaml
id: DEC-0001
title: Short decision title
status: ACTIVE
date: YYYY-MM-DD
decision_owner: owner
proposed_by: 6s-ceo
authority_class: GREEN|YELLOW|RED
approval_reference: null

context: >
  What problem, uncertainty, or choice required a decision?

decision: >
  What exactly was decided?

rationale:
  - ...

evidence:
  - source: ...
    observation: ...

alternatives:
  - option: ...
    reason_not_selected: ...

consequences:
  positive:
    - ...
  negative:
    - ...

constraints:
  - ...

related:
  backlog: []
  experiments: []
  github: []
  documents: []

review:
  trigger: ...
  date: null

supersedes: null
superseded_by: null
```

Use `UNKNOWN` when facts are not yet verified.

---

# 7. Decision Authority

Every decision must respect `AUTONOMY.md`.

## GREEN

Claude may decide autonomously.

## YELLOW

Claude may decide within defined constraints.

## RED

Explicit owner approval is required.

Do not convert a RED decision into GREEN by calling it an experiment.

---

# 8. Owner Decisions

Owner decisions have highest authority within legal, safety, security, and platform constraints.

When the owner makes a durable choice:

1. record it
2. capture rationale if known
3. identify implications
4. update affected documents
5. prevent agents from silently reversing it

---

# 9. Agent Decisions

Agents may make durable decisions only within their delegated authority.

Examples:

`github-manager`
may choose a safe repository housekeeping method.

It may not independently change the company's business model.

`vps-docker-manager`
may select a safe diagnostic command.

It may not destroy persistent production data.

---

# 10. Decision vs Experiment

Use a decision when choosing a policy, direction, standard, or architecture.

Use an experiment when evidence is needed before choosing.

Preferred sequence:

**Uncertainty**
→ **Experiment**
→ **Evidence**
→ **Decision**
→ **Standard**

Do not prematurely turn hypotheses into permanent decisions.

---

# 11. Decision vs Learning

A decision says:

**We will do X.**

A learning says:

**Evidence indicates Y.**

A decision may rely on one or more learnings.

Keep them separate.

---

# 12. Decision vs Status

`STATUS.md` says what is true now.

`DECISIONS.md` says why important choices were made.

Do not use status as durable decision memory.

---

# 13. Decision vs Backlog

A decision can create work.

Example:

Decision:
Use immutable image digests for production release identity.

Backlog:
Implement digest capture and dashboard reconciliation.

Do not put implementation checklists into the decision record unless needed for context.

---

# 14. Decision vs Code

Code is evidence that a choice was implemented.

Code is not sufficient documentation of why the choice exists.

---

# 15. Reopening a Decision

Do not reopen an ACTIVE decision simply because a new agent prefers another approach.

Reopen only when:

- new evidence materially changes assumptions
- customer behavior contradicts rationale
- economics change
- vendor/tool capability changes
- security/reliability requirements change
- strategic phase changes
- owner requests reconsideration
- review trigger occurs

---

# 16. Reversal

Never silently edit history to make it look like the old decision never existed.

Create a new decision:

`DEC-00XX`

Then mark old decision:

`SUPERSEDED` or `REVERSED`

and link both.

---

# 17. Decision Review

Not every decision needs a calendar review.

Prefer event-based triggers.

Examples:

- Entryway validation achieved
- monthly revenue exceeds threshold
- traffic exceeds architecture capacity
- vendor cost exceeds threshold
- first physical product launches
- security architecture changes
- first 10,000 active users

---

# 18. Decision Quality

A good decision record is:

- concise
- specific
- evidence-aware
- reversible where possible
- explicit about tradeoffs
- clear about authority

Avoid writing essays merely to appear rigorous.

---

# 19. Reversible vs Irreversible

Classify mentally using:

## Two-Way Door

Easy to reverse.

Move quickly within authority.

## One-Way Door

Difficult, expensive, risky, or impossible to reverse.

Require stronger evidence and appropriate approval.

Examples of one-way or high-cost choices:

- destructive data deletion
- domain transfer
- major customer-data migration
- irreversible pricing commitments
- large vendor contract
- public promise with material liability

---

# 20. Default Bias

For uncertain architecture/product choices, prefer:

- reversible
- incremental
- observable
- low recurring cost
- standards-based
- exportable
- minimally coupled

This preserves future options.

---

# 21. Strategic Decision Register

The following decisions capture the current operating direction.

They should be verified against existing project files when installed.

---

## DEC-0001: Entryway Is the Initial Product Proving Ground

**Status:** ACTIVE  
**Decision Owner:** Owner  
**Authority:** RED / strategic owner decision

### Decision

Entryway will serve as the first complete room-level proving ground for the 6S Success system before broad whole-home expansion.

### Rationale

Entryway provides:

- clear micro-zones
- frequent household interaction
- visible friction
- short quests
- organization opportunities
- safety opportunities
- product opportunities
- multiplayer potential
- natural before/after outcomes

### Consequence

Other rooms may be researched, but major expansion should not displace Entryway validation.

### Review Trigger

Entryway phase exit criteria in `STRATEGY.md` are achieved or owner changes strategy.

---

## DEC-0002: Customer Desired Function Precedes Prescriptive Organization

**Status:** ACTIVE  
**Decision Owner:** Owner  
**Authority:** RED / product philosophy

### Decision

6S Success should determine what the person or household wants an area to accomplish before prescribing how it should be organized.

### Model

**Values / Desired Outcome**
→ **Desired Function**
→ **Micro-Zone**
→ **Friction**
→ **Root Cause**
→ **Quest / Improvement**
→ **Standard**
→ **Sustainment**

### Rationale

The same physical space can serve different households differently.

The system should optimize for the user's desired function rather than impose a universal "organized" appearance.

---

## DEC-0003: Root Cause Before Product Recommendation

**Status:** ACTIVE  
**Decision Owner:** Owner  
**Authority:** RED / customer trust

### Decision

Product recommendations should follow an understood need/root cause whenever practical.

### Rationale

6S Success should not become a generic affiliate/product catalog.

Products should remove specific friction or enable a desired function.

### Consequence

Recommendation architecture should connect products to:

- room
- micro-zone
- desired function
- root cause
- quest

---

## DEC-0004: Customer Outcome Outranks Engagement

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

The system will prioritize meaningful household improvement over maximizing clicks, time-on-site, card draws, streaks, or other engagement metrics.

### Candidate North Star

**Sustained Micro-Zone Improvements**

when measurement is mature enough.

### Guardrail

Gamification should support useful completion, not addictive usage for its own sake.

---

## DEC-0005: Quests Support 15 to 90 Minute Improvement Events

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

The card/quest system should support configurable improvement events approximately 15 to 90 minutes in duration.

### Experience

Cards may be:

- selected
- assigned
- voluntarily claimed
- configured
- randomized

and should support 1-10 players where appropriate.

---

## DEC-0006: Room Decks Include Desired-Function Discovery

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

Room decks should include a mechanism for discovering and aligning on the room's desired primary function and micro-zone outcomes.

### Rationale

The deck should not begin with cleaning/organizing tasks before participants understand what the area is supposed to accomplish.

---

## DEC-0007: Entryway Deck Is Both Product and Learning Instrument

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

The Entryway deck is not only content to sell.

It is also a structured mechanism for learning:

- desired functions
- common friction
- root causes
- quest preferences
- completion patterns
- multiplayer behavior
- product needs
- sustainment

### Constraint

Customer privacy and consent must be respected.

---

# 22. Business Decisions

---

## DEC-0008: $20K Monthly Revenue Is a Strategic Target, Not a Metric Result

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

$20,000+ monthly revenue is a strategic business target.

It must always be displayed as `TARGET`, not `ACTUAL` or `FORECAST`.

### Consequence

Claude should decompose the target into actionable drivers:

**Qualified Traffic**
× **Conversion**
× **AOV**
× **Repeat Contribution**

while preserving margin and customer outcomes.

---

## DEC-0009: Revenue Growth Must Be Sustainable

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

Claude should optimize for sustainable economic value, not gross revenue alone.

### Relevant Measures

When available:

- net revenue
- refunds
- COGS
- gross margin
- contribution margin
- repeat purchase
- customer outcome

### Consequence

A revenue increase that materially damages margin, trust, or customer outcomes is not automatically successful.

---

## DEC-0010: Free Content Should Lead Naturally to Useful Paid Value

**Status:** ACTIVE  
**Decision Owner:** Owner

### Decision

Free content should create genuine standalone value while exposing situations where a paid product, deck, kit, service, or tool provides meaningful additional value.

### Constraint

Do not intentionally make free guidance incomplete or frustrating solely to force purchase.

---

# 23. Autonomous Operating Decisions

---

## DEC-0011: Maximum Three Major Active Workstreams

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

Default WIP limit is three major active workstreams.

### Current Initial Workstreams

1. Autonomous operating/data foundation
2. GitHub-to-production control plane
3. Entryway customer/monetization loop

### Review Trigger

Evidence shows WIP limit materially constrains or fails to constrain effective delivery.

---

## DEC-0012: Unknown Data Must Remain UNKNOWN

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

If a current value lacks a verified source, report:

`UNKNOWN`

Do not substitute:

- zero
- estimate
- stale value
- assumed value

without explicit labeling.

### Rationale

Autonomous operation requires trustworthy reality.

---

## DEC-0013: Live Authoritative Systems Override Stale Markdown

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

When live verified system state conflicts with stale operational documentation, the authoritative live source wins.

Then update the documentation.

### Constraint

Do not treat every live system as authoritative for every question.

Follow `DATA-SOURCES.md`.

---

## DEC-0014: Dashboard Is a Decision Interface

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

The executive dashboard will prioritize:

- customer outcomes
- business performance
- current constraint
- autonomous actions
- experiment outcomes
- production health
- owner decisions

over vanity charts.

---

## DEC-0015: Claude Must Measure Material Changes

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

For material changes, Claude should record:

**Why**
→ **Expected Outcome**
→ **Implementation**
→ **Verification**
→ **Measured Result**
→ **Keep / Iterate / Revert**

### Rationale

Autonomous coding must become autonomous continuous improvement.

---

# 24. Experimentation Decisions

---

## DEC-0016: Changes Are Not Automatically Improvements

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

Claude may say a change was implemented after deployment.

Claude may call it an improvement only when evidence supports improved outcomes.

---

## DEC-0017: One Primary Metric Per Experiment by Default

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

Each material experiment should preselect one primary metric unless design requirements clearly justify otherwise.

### Rationale

Prevents metric shopping.

---

## DEC-0018: Failed and Inconclusive Experiments Are Preserved

**Status:** ACTIVE  
**Decision Owner:** Autonomous Operating System

### Decision

Experiment history will retain:

- supported
- unsupported
- mixed
- inconclusive
- invalid

results.

### Rationale

Negative knowledge prevents repeated waste.

---

# 25. GitHub Decisions

These decisions define desired operating principles. Actual repository implementation must first be verified.

---

## DEC-0019: GitHub Is Source-Control Truth, Not Automatic Production Truth

**Status:** ACTIVE  
**Decision Owner:** github-manager / devops-sre

### Decision

GitHub is authoritative for repository history and CI definitions.

It does not automatically prove what code is running on Hostinger.

### Requirement

Production lineage should verify:

**Commit**
→ **Build**
→ **Image**
→ **Deployment**
→ **Running Container**

---

## DEC-0020: Production Releases Should Be Traceable to Immutable Identity

**Status:** ACTIVE  
**Decision Owner:** devops-sre

### Decision

Production should be traceable to an immutable release identity such as commit SHA and image digest.

### Constraint

Do not rely solely on mutable tags such as `latest`.

### Implementation

Must be adapted to the actual verified deployment architecture.

---

## DEC-0021: Repository Changes Should Preserve Rollback

**Status:** ACTIVE  
**Decision Owner:** github-manager

### Decision

Material production changes should be structured so prior known-good state can be restored where practical.

---

# 26. Hostinger VPS / Docker Decisions

---

## DEC-0022: Initial VPS Discovery Is Read-Only

**Status:** ACTIVE  
**Decision Owner:** vps-docker-manager

### Decision

Initial Hostinger VPS/Docker discovery should not modify unknown production resources.

### Rationale

The first objective is to establish reality safely.

---

## DEC-0023: Unknown Persistent Volumes Are Preserved

**Status:** ACTIVE  
**Decision Owner:** vps-docker-manager

### Decision

Unknown Docker volumes or persistent assets must not be deleted until ownership, necessity, backup, and recovery implications are understood.

---

## DEC-0024: Runtime Must Be Reconciled With Declared Configuration

**Status:** ACTIVE  
**Decision Owner:** vps-docker-manager

### Decision

Compare:

- Git configuration
- Compose/deployment declaration
- Docker runtime
- production behavior

Surface unexplained drift.

---

## DEC-0025: Backup Success Requires More Than a Scheduled Job

**Status:** ACTIVE  
**Decision Owner:** devops-sre

### Decision

Backup confidence progresses through evidence levels:

0. assumed
1. job exists
2. job reports success
3. artifact verified
4. restore validated

Critical persistent data should target Level 4.

---

# 27. Data Decisions

---

## DEC-0026: Transaction Systems Outrank Client Analytics for Financial Truth

**Status:** ACTIVE  
**Decision Owner:** analytics-intelligence / commerce-manager

### Decision

Client analytics purchase events are not the authoritative financial source.

Use reconciled commerce/payment data according to `DATA-SOURCES.md`.

---

## DEC-0027: Database and Analytics Serve Different Truths

**Status:** ACTIVE  
**Decision Owner:** analytics-intelligence

### Decision

Transactional databases describe persisted state.

Analytics describes observed behavior.

Disagreement should trigger investigation rather than silent replacement.

---

## DEC-0028: Test Data Must Be Distinguishable

**Status:** ACTIVE  
**Decision Owner:** analytics-intelligence

### Decision

Internal/test traffic, transactions, and events must be identifiable and excluded from executive business metrics where appropriate.

---

# 28. SEO / AEO Decisions

---

## DEC-0029: SEO Prioritization Must Connect to Customer Intent

**Status:** ACTIVE  
**Decision Owner:** seo-aeo

### Decision

SEO work should prioritize opportunities using:

- search evidence
- customer intent
- room/micro-zone relevance
- useful next action
- downstream activation/value

not keyword volume alone.

---

## DEC-0030: No Fabricated AEO Score

**Status:** ACTIVE  
**Decision Owner:** seo-aeo

### Decision

Do not create a universal proprietary "AEO score" and present it as objective truth.

Use observable evidence and clearly labeled heuristics.

---

## DEC-0031: Content Volume Is Not the Goal

**Status:** ACTIVE  
**Decision Owner:** content-strategy

### Decision

Claude should not mass-publish pages simply to increase indexed page count.

Prefer:

- useful
- differentiated
- intent-aligned
- internally coherent
- outcome-oriented

content.

---

# 29. Commerce Decisions

---

## DEC-0032: Recommendations Must Be Useful, Not Merely Profitable

**Status:** ACTIVE  
**Decision Owner:** commerce-manager

### Decision

Product recommendation ranking should consider expected customer usefulness and diagnosed need, not only margin or commission.

---

## DEC-0033: Bundles Must Solve Coherent Problems

**Status:** ACTIVE  
**Decision Owner:** commerce-manager

### Decision

Bundles should combine products that jointly solve a customer problem.

Do not bundle unrelated items solely to inflate AOV.

---

## DEC-0034: Avoid Dark Patterns

**Status:** ACTIVE  
**Decision Owner:** Owner / commerce-manager

### Decision

6S Success will not use deceptive conversion tactics such as:

- fake scarcity
- hidden charges
- misleading countdowns
- confusing cancellation
- false testimonials
- disguised recurring billing

Customer trust is a business asset.

---

# 30. Product Architecture Decisions

---

## DEC-0035: Stable IDs for Core Business Entities

**Status:** ACTIVE  
**Decision Owner:** product/data architecture

### Decision

Use stable IDs for reusable entities such as:

- room
- micro-zone
- desired function
- root cause
- quest
- card
- product
- experiment

Display names should not serve as primary identity.

---

## DEC-0036: Room and Micro-Zone Taxonomy Is Foundational

**Status:** ACTIVE  
**Decision Owner:** product-manager

### Decision

The system should use a reusable whole-home room/micro-zone taxonomy so:

- cards
- quests
- content
- products
- inventory
- analytics
- services

can connect to the same conceptual model.

---

## DEC-0037: Physical and Digital Decks Share a Common Content Model

**Status:** ACTIVE  
**Decision Owner:** product-manager

### Decision

Where practical, physical cards and digital cards should derive from a shared canonical card/quest model rather than becoming independent products with conflicting content.

---

# 31. Decision Proposal Process

When an agent identifies a durable choice:

1. search existing decisions
2. determine whether a decision already exists
3. gather evidence
4. classify authority
5. document alternatives
6. recommend an option
7. obtain approval if required
8. record decision
9. update affected systems/docs
10. create implementation backlog items

---

# 32. Owner Approval Request Format

For RED decisions:

## Decision Needed

One sentence.

## Recommendation

One option.

## Why

Evidence and rationale.

## Alternatives

Maximum useful alternatives.

## Risk

What could go wrong.

## Cost

If applicable.

## Reversibility

Easy / Moderate / Difficult.

## Impact of Delay

What happens if no decision is made.

Avoid long approval essays unless complexity requires them.

---

# 33. Architectural Decision Format

For technical architecture:

Include:

- problem
- constraints
- selected architecture
- alternatives
- operational impact
- security impact
- cost
- migration
- rollback
- review trigger

Avoid choosing technology because it is fashionable.

---

# 34. Vendor Decision Format

Before adding a significant vendor:

Record:

- problem being solved
- existing alternatives
- monthly/annual cost
- lock-in
- exportability
- security/privacy
- operational dependency
- exit plan

Follow spending authority.

---

# 35. Pricing Decision Format

For durable pricing choices:

Record:

- product
- customer value
- price
- evidence
- cost/margin
- competitive context if used
- experiment evidence
- review trigger

Pricing tests belong in `EXPERIMENTS.md`.

The adopted pricing policy belongs here.

---

# 36. Decision Conflict

If two ACTIVE decisions conflict:

1. stop affected autonomous work if material
2. identify conflict
3. determine newer/more specific authority
4. request owner resolution if necessary
5. supersede one explicitly

Do not silently choose whichever decision an agent prefers.

---

# 37. Decision Precedence

General precedence:

1. law/safety/security requirements
2. explicit current owner decision
3. `AUTONOMY.md`
4. active strategic decision
5. active architectural/operating decision
6. specialist-agent preference
7. implementation convenience

---

# 38. Decision Freshness

A decision does not become invalid merely because it is old.

Age is a reason to inspect assumptions, not automatically reverse it.

Use review triggers.

---

# 39. Decision Evidence Updates

New evidence may be appended to an ACTIVE decision without changing its meaning.

If the decision itself changes, create a new decision record.

---

# 40. Decision Metrics

Do not optimize for number of decisions made.

A healthy autonomous system should make many routine decisions without permanent documentation and preserve only those that matter.

---

# 41. Decision Dashboard

Dashboard should surface only:

- pending owner decisions
- recently changed major decisions
- decisions affecting current work

Do not make the executive dashboard a decision archive.

---

# 42. Initial Pending Decisions

At creation of this file, do not invent pending owner decisions.

Agents should populate this section only when a real unresolved RED decision exists.

Current:

`NONE VERIFIED`

---

# 43. Decision Index

Maintain a compact index as the file grows.

| ID | Decision | Status | Domain |
|---|---|---|---|
| DEC-0001 | Entryway is initial proving ground | ACTIVE | Strategy |
| DEC-0002 | Desired function precedes prescription | ACTIVE | Product |
| DEC-0003 | Root cause before product recommendation | ACTIVE | Product |
| DEC-0004 | Customer outcome outranks engagement | ACTIVE | Strategy |
| DEC-0005 | Quests support 15-90 minute events | ACTIVE | Product |
| DEC-0006 | Room decks include desired-function discovery | ACTIVE | Product |
| DEC-0007 | Entryway deck is product and learning instrument | ACTIVE | Product |
| DEC-0008 | $20K/month is a target | ACTIVE | Business |
| DEC-0009 | Revenue growth must be sustainable | ACTIVE | Business |
| DEC-0010 | Free content leads to useful paid value | ACTIVE | Business |
| DEC-0011 | Maximum three major workstreams | ACTIVE | Operations |
| DEC-0012 | Unknown data remains UNKNOWN | ACTIVE | Data |
| DEC-0013 | Authoritative live systems override stale docs | ACTIVE | Data |
| DEC-0014 | Dashboard is a decision interface | ACTIVE | Operations |
| DEC-0015 | Material changes must be measured | ACTIVE | Operations |
| DEC-0016 | Changes are not automatically improvements | ACTIVE | Experiments |
| DEC-0017 | One primary metric by default | ACTIVE | Experiments |
| DEC-0018 | Preserve negative/inconclusive experiments | ACTIVE | Experiments |
| DEC-0019 | GitHub is not automatic production truth | ACTIVE | GitHub |
| DEC-0020 | Releases use immutable identity | ACTIVE | DevOps |
| DEC-0021 | Preserve rollback | ACTIVE | GitHub |
| DEC-0022 | Initial VPS discovery is read-only | ACTIVE | VPS |
| DEC-0023 | Preserve unknown persistent volumes | ACTIVE | Docker |
| DEC-0024 | Reconcile runtime with declared config | ACTIVE | Docker |
| DEC-0025 | Backups require verification | ACTIVE | Reliability |
| DEC-0026 | Transaction systems outrank analytics for finance | ACTIVE | Data |
| DEC-0027 | Database and analytics serve different truths | ACTIVE | Data |
| DEC-0028 | Test data must be distinguishable | ACTIVE | Data |
| DEC-0029 | SEO connects to customer intent | ACTIVE | SEO |
| DEC-0030 | No fabricated AEO score | ACTIVE | AEO |
| DEC-0031 | Content volume is not the goal | ACTIVE | Content |
| DEC-0032 | Recommendations prioritize usefulness | ACTIVE | Commerce |
| DEC-0033 | Bundles solve coherent problems | ACTIVE | Commerce |
| DEC-0034 | Avoid dark patterns | ACTIVE | Commerce |
| DEC-0035 | Stable IDs for core entities | ACTIVE | Architecture |
| DEC-0036 | Room/micro-zone taxonomy is foundational | ACTIVE | Product |
| DEC-0037 | Physical/digital decks share content model | ACTIVE | Product |

---

# 44. Maintenance Rule

Whenever a major decision is made:

- add decision record
- update index
- update related docs
- commit with decision ID where practical

Whenever superseded:

- preserve old record
- update status
- link replacement

---

# 45. Anti-Patterns

Never allow:

## Decision Amnesia

Reopening settled questions because a new agent lacks context.

## Silent Reversal

Changing strategy without recording it.

## Documentation Theater

Recording trivial decisions nobody needs.

## Evidence Theater

Listing weak evidence to make a preference appear objective.

## Authority Bypass

Making a RED decision through implementation first.

## Historical Rewriting

Deleting old decisions after strategy changes.

## Architecture Fashion

Changing stacks because a newer technology exists.

---

# 46. Decision Quality Test

Before recording a decision, ask:

**Will a competent future agent benefit from knowing that this choice was intentional and why?**

If yes, record it.

If no, it probably belongs in code, a task, or nowhere.

---

# 47. Final Principle

Autonomy requires memory.

Without durable decision memory, autonomous agents repeatedly reconsider the same questions, drift from strategy, reverse one another's work, and force the owner to explain the business again.

`DECISIONS.md` is the organization's institutional memory for intentional choices.

The system should be able to answer:

**What did we decide?**

**Why?**

**Based on what evidence?**

**Who had authority?**

**What would cause us to reconsider?**

Then Claude can move forward without repeatedly asking the owner to resolve the same questions.

## D-001 | 2026-08-22 | The Standards Pack ships free, not at $12

**Decision.** Build the Standards Pack and give it away, reversing a plan to
sell it at $12.

**Rationale.** It was scoped on the claim that `leave_behind` carried content in
no paid product. Measured before shipping, that is false: median overlap with
the passes already sold in the $19 Print Pack is 0.27 for the standards and 0.58
for the triggers, with 49 of 114 triggers near verbatim. Charging for it would
be selling a buyer their own purchase back in a smaller typeface.

**Evidence.** `ops/build_standards.py` prints the overlap on every build.
Measurement tier: verified product data, which is tier 2.

**Alternatives.** Sell at a lower price, which is the same problem smaller.
Bundle it into the Print Pack silently, which hides the best free artifact the
business has behind a paywall while traffic is the binding constraint. Kill it,
which throws away a genuinely different artifact: this one stays on the door
after the work ends, and everything else in the catalogue is carried in and put
down.

**Consequences.** No new revenue line. One more real reason to arrive, one more
indexable page, and a second free tier that demonstrates whole house scope
rather than one room. The Print Pack is the named next step on the page.

**Revisit when.** 200 downloads with under 1% onward conversion to the Print
Pack. Then change the offer block, not the price.

## D-002 | 2026-08-25 | EXECUTIVE-DASHBOARD.md at project root is canonical; the ALT version is discarded

**Decision.** Keep `EXECUTIVE-DASHBOARD.md` (project root) as the canonical
dashboard specification. Discard `_review/EXECUTIVE-DASHBOARD-ALT.md`. Closes
issue #8.

**Rationale.** Both files are aspirational design specs installed together on
2026-08-16 under the same name, neither a version of the other. The root file
is already the one every other control doc references by name
(`SYSTEM-REGISTRY.md`, `MISSION-CONTROL.md`, `AUTONOMOUS-OPERATING-LOOP.md`),
so keeping it avoids rewriting those references. ALT's content that looked
unique at install time (Revenue Mix, Revenue Definition, Customer Outcome
Definition, Qualified Visitor Definition, Conversion Definition, Experiment
Guardrails) is now redundant: `METRICS.md` already carries Funnel Conversion
Definitions and Experiment Guardrail Breach, and `CUSTOMER-JOURNEY.md`
already defines Qualified Visitor. Those canonical docs did not exist at
install time; they do now, and they are more current than ALT's copies.

**Evidence.** Direct read of both files' section headers (139 sections in
ALT, 109 in root, neither a subset of the other) and a grep for ALT's
signature terms against `METRICS.md`, `DATA-SOURCES.md`, `CUSTOMER-JOURNEY.md`,
confirming the overlap. Tier: direct inspection of repository content.

**Alternatives.** Merge both into one document: rejected, both are
aspirational templates far larger than the actual implemented dashboard
(`EXECUTIVE-DASHBOARD-LIVE.md`, generated by `ops/dashboard.py`), so merging
two unimplemented specs would produce a bigger unimplemented spec, not more
value. Keep both under distinct names: rejected, nothing in the live system
would ever read the second one, so it would just be a second thing to keep
in sync with nothing.

**Consequences.** One canonical dashboard spec at the root. `_review/`
keeps a note of the resolution in `INSTALL-NOTES.md` rather than the dead
file itself.

**Revisit when.** Never, unless a future session finds ALT contained
something genuinely load-bearing that this review missed; the file's
content remains readable in git history at any point before this commit.

## D-003 | 2026-08-27 | The 90 Entryway deck images are not a rejected asset; they are the deck

**Decision.** Reverse the 2026-08-26 finding in `BACKLOG-2026-H2.md` (3.3b)
that called the 90 Entryway card images "the wrong artefact... two panel
trading card mockups with game chrome baked in." The chrome is not a defect,
it is the product: the images are the front and back faces of a 90 card game
deck. They now ship at `deck-gallery.html`, split into individual faces by
`ops/split_deck_cards.py` and rendered by `ops/build_deck_gallery.py`.

**Rationale.** The earlier review read the sheets as failed editorial
photography (the same lens correctly applied to the 94 shop photos and the
864 book plates) and rejected them on that basis without asking what a card
deck's own source art is supposed to look like. Phil corrected it directly by
building and shipping the gallery himself. This is recorded so a future
cycle does not read the superseded language in an old log entry and either
repeat the same misreading or waste a cycle re-verifying a call Phil already
made and shipped.

**Evidence.** `75aa115` (Phil Kling, 2026-08-27), which builds and deploys
the working gallery from the same source files the prior review opened and
rejected. Tier: direct inspection of the shipped commit and its output.

**Alternatives.** Leave the old finding standing and let the shipped gallery
contradict it silently: rejected, that is exactly the stale-documentation
failure mode `STATUS.md` was rewritten to fix on 2026-08-24.

**Consequences.** `BACKLOG-2026-H2.md` 3.3b now carries a strikethrough and
correction pointing here instead of the original claim. 5.1 (how card decks
get sold) has new context: the full deck is now publicly viewable for free,
worth weighing when that decision is made, not blocking it.

**Revisit when.** Not expected to. If a future session finds a reason the
gallery itself should not have shipped (a licensing problem in the source
art, for instance), open a new decision rather than editing this one.

## D-014  Safety is the fourth S, not the sixth
**Date** 2026-08-28

**Decision.** Sort, Straighten, Shine, **Safety**, Standardize, Sustain. Safety
sits fourth and the order does not change.

**Evidence.** Phil's own original numbered curriculum, written in 2009 and on
disk at `Desktop/Process Kaizen/Process Kaizen/Work Folder/6S/`, numbers the
steps unambiguously: 1.xx Sort, 2.xx Straighten, 3.xx Shine, **4.01 Assess the
Target Area for Hazards, 4.02 Eliminate all Hazards, 4.03 Improve Overall
Safety**, 5.xx Standardize, 6.xx Sustain. This is the strongest possible source:
the author of the brand, teaching it, seventeen years ago.

**The conflict, named so it is not rediscovered.** `Documents/6S-Success-
Trainer.txt` presents Safety as an appended sixth S, via the 5S to 5S+1 to 6S
history. That framing is correct about where the sixth S came from historically
and wrong about where this brand puts it. Both can be true: the industry added
safety as an extra S; Phil's curriculum places it fourth, before Standardize,
because you cannot standardize a hazard.

**Consequence.** The site, the book, the manual, the decks and CLAUDE.md are
all already correct. No change was needed. The Trainer document is the outlier
and should be corrected if it is ever published.

**Revisit if.** Phil says the sequence was different in a later engagement.

## D-015 | 2026-08-29 | Abandoned checkouts are recoverable in principle; building the recovery send is deliberately deferred, not blocked

**Decision.** Backlog item 4.4 asked whether checkout sessions can be
recovered at all. Answer: yes, architecturally, without a webhook or a cart
of our own, using the same poll pattern `ops/stripe_fulfil.py` already uses
for fulfilment. Building the actual poller and recovery send is deferred
until 2.1 (Listmonk sending identity, issue #15) resolves, not attempted now.

**Rationale.** Verified in this repo: every buyable item here is sold
through a Stripe Payment Link (`ops/stripe_catalog.py`, `ops/stripe_links.py`
both call the `payment_links` endpoint exclusively; nothing in this codebase
creates a Checkout Session directly). Verified: fulfilment itself
(`ops/stripe_fulfil.py`) deliberately has no webhook, polling Stripe for
completed PaymentIntents instead, on the documented grounds that a webhook
needs a standing service this business's volume does not justify yet.

A Payment Link is not a dead end for this question: Stripe's Payment Links
product creates an ordinary Checkout Session behind every link, and the
Checkout Sessions List API accepts a `payment_link` filter, returning each
session's `status` (open, complete, expired) and, once a visitor has typed
it, `customer_details.email`, whether or not they finished paying. That
means the same poll-based approach already used for fulfilment could be
pointed at Checkout Sessions instead of only PaymentIntents to find
"typed an email, did not pay," with no new service, port or secret. This
last paragraph is informed technical knowledge about how Stripe's product
works, not a verified live finding: `docs.stripe.com` is rejected by this
sandbox's egress proxy and no Stripe secret key is present here
(`.env.secrets` does not exist in this container), so the actual current
behaviour of this account's Payment Links has not been checked against a
live session and cannot be from this environment.

Even if verified, this is deliberately not built yet. A recovery message is
a more sensitive send than the newsletter confirmation issue #15 already
found broken: it addresses one visitor about one specific unpaid amount, not
a generic welcome. Sending it under the wrong brand identity, the exact
defect 2.1 is about, would be worse than sending nothing. Building the code
now and leaving it unused until 2.1 lands would also violate CLAUDE.md
section 42 (no unused code for a hypothetical future state) more than it
would save time later, since the poller is a small addition once a working
mailer exists.

**Evidence.** Direct reading of `ops/stripe_catalog.py`, `ops/stripe_links.py`
and `ops/stripe_fulfil.py` in this repo (tier: direct inspection of the code
that runs today). The Checkout Sessions / Payment Links relationship is
general Stripe product knowledge, tier: informed hypothesis, explicitly not
verified against live docs or a live account from this sandbox.

**Alternatives.** Build the poller now, ready to switch on the moment 2.1
resolves: rejected, because untested unused code sitting next to a payments
integration is itself a risk (Stripe's API surface can shift the exact
session fields this would rely on before it is ever run), and confirming the
Checkout Sessions behaviour needs a live account check first regardless.
Leave 4.4 marked undecided: rejected, since the actual question the backlog
row asks ("can it be recovered at all") has a real, evidenced answer now.

**Consequences.** `BACKLOG-2026-H2.md` 4.4 marked decided, pointing here.
4.3 (post-purchase sequence) and any future recovery poller both wait on
2.1 for the same reason. The next session picking this up should verify the
Checkout Sessions / Payment Links claim above against a live account before
writing any code against it, not take this decision's technical description
on faith.

**Revisit when.** 2.1 (Listmonk sending identity) is decided and a
brand-correct mailer exists, or a session with a live Stripe key confirms or
corrects the Checkout Sessions behaviour described above.

## D-016 | 2026-09-03 | The entry offer is the $9 room pack, and the room page is where it is offered

**Decision.** Name one entry offer and merchandise the catalogue behind it: the
**$9 room pack for the room the visitor is already reading about**. Implement it
where the visitor actually is, which is the room page, not the shop page. Do not
change any price to do it.

**The problem being solved.** 159 products, 52 lifetime visitors, zero
purchases. A first-time visitor with a messy entryway had no obvious single
thing to buy: the shop's first screen was seven near-identical $4 tiles, and the
20 room pages offered only the $19 Whole House Print Pack, which is 684 cards
for twenty rooms to a person who came about one.

**Rationale, from the customer's job rather than from margin.**

1. **A room is the unit people name.** Nobody says "my shoe zone is a mess".
   They say "my kitchen is a mess". The micro zone is our unit of diagnosis; the
   room is their unit of complaint. Diagnose in micro zones, sell in rooms.
2. **A room pack is a finishable job.** 18 to 42 cards, four to five sheets of
   paper, one weekend, one visible outcome. The $19 pack is 76 sheets. Nobody
   prints 76 sheets on the strength of a first visit, and an unused purchase
   produces no trust, no repeat and a fair refund request.
3. **$9 is under the threshold where a digital purchase needs deliberation**,
   and the first sale to a stranger is a trust transaction before it is a
   revenue one.
4. **It is the offer that matches the sentence they arrived with.** A person on
   `/rooms/kitchen.html` has already told us, by being there, the one thing they
   care about.

**Why not the alternatives.**

- **The $4 zone pack.** Smaller than any job anybody names out loud, and its
  value against the 1,300 free words directly above it on the same page is
  genuinely thin. It should stay, offered from the zone page where it fits, but
  it cannot carry the catalogue.
- **The $19 Whole House Print Pack.** Better arithmetic and the only thing ever
  sold, but it answers a job the visitor does not have yet. It is the right
  **expansion**, not the right entry, and it remains the primary offer on the
  114 zone pages where the alternative is a single micro zone.
- **The $9.99 eBook.** The measured buy-clicks did land on `/book.html`, which
  is real evidence and the reason this decision should be revisited early. But
  the book is a thing to read, and the job is a room that does not work. It
  stays as the parallel offer on its own page.

**What was implemented, 2026-09-03.**

- All 19 room pages that have a room pack now lead with it, with the whole house
  comparison stated in the same breath and both real prices shown, so nobody can
  buy the room pack without having been shown the cheaper-per-card option
  (`ops/build_zone_pages.py`, `room_offer`). The Entryway has no room pack (its
  zones are free) and correctly falls back to the previous whole house offer.
- Shop order now leads with room packs (`site/assets/js/data.js` and
  `shop.js`'s `CAT_ORDER`, kept identical so they cannot disagree).
- Every pack tile states its superset in words read from the catalogue.

**Evidence tier.** Tier 8, informed hypothesis, and it must be labelled that
way. There is one transaction in the history of this business and it was a
personal referral. Nothing here is validated. What makes it defensible is that
it is cheap, reversible, changes no price, and is measurable: every one of the
19 new room-pack links resolves to a SKU through `measure.js`'s payment-link id
and the generated catalogue in `shop.html`.

**Consequences.** Contribution per entry order falls from $18.15 to $8.44 if a
buyer who would have taken the whole house takes a room instead. That is
accepted deliberately: at zero customers, the scarce thing is a first stranger
who buys and then succeeds, not the size of a transaction that is not happening.
The whole house is one click away on the same block and is named as the better
value in plain words.

**Revisit when.** Any of:

- Ten room-pack orders exist. Then compare their refund and repeat behaviour
  against whole-house orders and let the measurement, not this argument, decide.
- A room-pack buyer upgrades to the whole house or the bundle. That would make
  the ladder evidence rather than a theory.
- `/book.html` continues to out-convert the room pages once both are measurable,
  in which case the entry offer is the $9.99 eBook and this decision is wrong.
- The $9 room pack and the $9.99 eBook are separated in price (see `PRICING.md`
  section 0.3), which would change the comparison a buyer makes.

---

## D-017 | 2026-09-04 | The service is the product; the free quest is the top of the funnel, and it keeps the hero

**Decision.** Treat the $250 Virtual Home Consult and the $1,200 In-Home Reset
Day as the product this business sells, and the free Home Quest, the zone guides
and the printable packs as what brings people to it. Rebuild `/consulting.html`
as a page that sells a considered service, give the homepage a full section for
the services in the position where a reader can first judge them, and connect
every free surface to the paid one. Do not move the consult back into the hero.

**The evidence.** `REVENUE-REVIEW-2026-09-04.md`, measured against Stripe and
the analytics database: $19 gross revenue all time from one charge, 52 visitors
in 30 days, 97% of 159 products priced $4 to $19. At a 2% conversion the $19
pack needs 52,632 visitors a month to reach $20,000, which is 1,012 times
today's traffic; the $4 packs need 4,808 times. Eight in-home days plus forty
two virtual consults is $20,100 from fifty transactions and needs 48 times
today's traffic, and 1.9 in-home days a week is deliverable by one person. The
low-priced catalogue cannot reach the goal by arithmetic, not by opinion.

**Why the free thing still comes first.** D-016's sequencing logic applies here
too, and yesterday's decision to take "Book a consult" out of the homepage hero
was right: the most expensive thing on the site should not be the second thing a
stranger is offered. `/quest.html` has had 53 views against 61 for the home page,
so the free app is what people already reach for. The hero keeps "Start free: one
zone, 15 minutes" as its only button, and gains one subordinate line naming the
$250 entry price for the visitor who arrived already wanting a person.

**The sequence chosen for the homepage.** What is this, how it works, do it
yourself free, then *or have someone run it with you*, then the paper products,
the book and the rooms. The service section replaced "Three ways in", a grid of
three equal pillars that repeated the nav and gave a $1,200 service the same
visual weight as a $19 printable. It sits immediately after the free section
because a reader who has just been shown exactly what doing it yourself involves
is the first reader on the page equipped to decide whether they want to. It
carries no pay button: a homepage card cannot answer what happens on the day,
what you keep, or what the refund is, so both cards lead to the part of
`/consulting.html` that does.

**What was wrong with the consulting page.** Its offer was three catalogue tiles
rendered at runtime from `window.CATALOG`. Verified against production with curl
on 2026-09-04: the live page serves **zero** Stripe links in plain HTML, so a
client that does not run JavaScript cannot pay for a consult at all. That is the
same defect `gate_shop_prerendered()` exists for on `shop.html`, on the page with
the most revenue riding on it. Both offers are now static HTML.

**Alternatives rejected.**

- *Put a $1,200 button in the hero.* Rejected: it reverses a decision taken for
  a good reason one day earlier and asks for the largest commitment on the site
  before any value has been shown.
- *A/B test the sequence.* Impossible, not merely unwise: the experiment
  registry computes 1,427 days to significance at 1.7 visitors a day. The
  changes are made because they are correct on their merits and this says so.
- *Leave the runtime grid and add copy around it.* Rejected: it keeps the
  no-JavaScript payment failure and keeps a $1,200 service in a shop tile.

**Consequences.** Two prices are now typed into prose on two pages instead of
read from the catalogue at runtime, which is exactly how the book came to show
$9.99 beside a link that charged $18. `ops/tests/test_service_offer_page.py`
guards it: both SKUs must have a buy button in plain HTML, at the catalogue
price, pointing at the catalogue's payment link, with the Treasure Valley towns
named. It was proved to fail on a planted fault before being trusted.

**Revisit when.** Any of:

- A consult is booked by somebody who is not us. That turns this from arithmetic
  into evidence and the next question becomes capacity, not conversion.
- Traffic reaches a level where the sequence can be measured rather than argued.
- `/consulting.html` pageviews rise but `CN-VIRTUAL` and `CN-INHOME` quote and
  buy clicks do not, which would say the routing works and the page does not.
- Delivery capacity changes, since fifty service events a month is the ceiling
  this decision accepts.

---

## D-018 | 2026-09-03 | Corporate Lean 6S gets a real page and a qualified enquiry route, and still gets no price

**Decision.** Build `site/corporate.html` from `ops/build_corporate.py`, point
the CN-CORP catalogue record at it, and publish **no price and no range** for
Corporate Lean 6S. Publish the nine things that determine the scope instead.

**Why now.** `REVENUE-REVIEW-2026-09-04.md`, measured against Stripe, Umami and
the live site: $19 of revenue in the business's life, one charge, 52 visitors in
thirty days, zero from Google. 97% of the 159 SKUs are priced $4 to $19, and at
a 2% conversion the $4 packs would need 250,000 visitors a month. CN-CORP is the
only line in the catalogue that needs **no consumer traffic at all**, and its
entire presence on the live site was one sentence on consulting.html, a
`price: null` record, and a "Request a quote" badge leading to a generic contact
form. The highest value item we sell had nowhere to send a buyer who was ready.

**Why no price.** The same review names $5,000 to $15,000 for this kind of
work and says plainly, in its own limits section, that this is a market range
and not a quote we have given or received. Printing it makes somebody else's
benchmark our price. It is also commercially wrong: two engagements with the
same headcount differ by a factor of several on sites, travel, shifts and
train-the-trainer, so one number is wrong in both directions at once. Full
reasoning in `PRICING.md`.

**Why no proof.** No logos, testimonials, case studies or count of engagements,
because none exist, and the corporate buyer is the reader most likely to check.
The page says so in a box of its own rather than leaving the absence to be
noticed. What it does carry is Phil's own record, already published on
about.html, framed as a career record rather than as a client reference.

**The enquiry mechanism.** A mailto to support@6s-success.com, with the
mechanism stated before the ask and the composed message shown in a copyable
box, matching the pattern cro-growth established on contact.html. Listmonk
returns HTTP 500, so nothing else on this site can be trusted with a lead.
`ops/service_orders.py` already watches that inbox, forwards service mail to
the owner and attaches a real .ics invite when a time is named, so the subject
line, the body labels and the date example on the form are all shaped to what
that tool can actually parse, and asserted at build time.

**Alternatives rejected.**

- *Publish "from $5,000".* Rejected: a figure we have never charged, taken from
  an industry benchmark, presented as ours. CLAUDE.md section 8.
- *Create a Stripe price and a payment link.* Rejected: nobody buys a scoped
  engagement from a checkout button, and it would invent the number above.
- *Leave it on consulting.html with more copy.* Rejected: a corporate buyer and
  a homeowner want different pages, and one page cannot answer "what do we have
  to supply" and "will you tidy my entryway" at once.
- *A landing page with a form that posts nowhere.* Rejected: that is the failure
  the contact form already documents. A mailto delivers or visibly does not.

**Consequences.** A quote-only product can now name its own page through a
`quote` field in `data.js`, which `site.js` renders as a primary button;
anything without one keeps the old contact-form route. Click-through is counted
as `quote-click` in `measure.js` and composing an enquiry fires
`corporate-enquiry`, so the page is measurable at 1.7 visitors a day where
nothing can be A/B tested. `ops/tests/test_corporate_page.py` fails the build if
a dollar figure appears on the page, if a price appears in its structured data,
if the subject stops routing to Corporate Lean 6S, or if CN-CORP acquires a
price or a payment link. It was proved to fail on a planted `$5,000` before
being trusted.

**A defect fixed on the way.** `service_orders.which_service()` matched service
phrases in list order rather than by position in the text, so an enquiry whose
free text mentioned "reset day" or "home consult" was routed to a household
booking regardless of its subject line. Corporate is last in that list, so it
was the most exposed. It now matches the earliest phrase in the text, which
means the subject decides. Verified: the old code routed a realistic corporate
enquiry mentioning a decayed 5S "reset day" to In-Home Reset Day.

**Revisit when.** Any of:

- A first quote is actually issued. Record the figure and the scope in
  `PRICING.md` that day; two or three real quotes beat any market range.
- An engagement is delivered. Then, and only then, the page can carry an
  outcome, with the client's permission.
- Enquiries arrive but none convert, which would make the page a routing
  problem rather than a demand problem.
- Enquiries do not arrive at all after the page has been indexed, which would
  say the constraint for this line is discovery and not the offer.
