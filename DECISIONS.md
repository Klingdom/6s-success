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
