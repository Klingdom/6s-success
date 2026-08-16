# 6S Success Owner Directives

> Canonical human-control layer for the autonomous 6S Success operating system. Defines the owner's current strategic intent, priorities, preferences, constraints, risk posture, decision rights, focus areas, and explicit overrides without requiring changes to the underlying agent or governance architecture.

## 1. Purpose

`OWNER-DIRECTIVES.md` is the highest-level project-specific strategic direction supplied by the owner to Claude Code and the autonomous operating system.

It answers:

- What matters most right now?
- What should Claude optimize?
- What should Claude deliberately not optimize yet?
- How aggressive should autonomous experimentation be?
- Where should money be spent?
- What requires owner judgment?
- What strategic sequence should the business follow?
- Which assumptions are temporary?
- When should a directive expire or be reviewed?

This file is intended to change more frequently than core governance files such as `AUTONOMY.md`, `SECURITY.md`, or `RELEASES.md`.

---

# 2. Directive Principle

**Strategy changes through directives. Governance changes through governance files.**

Do not rewrite core policy every time the owner changes priorities.

---

# 3. Precedence

Owner directives guide prioritization and strategy within all applicable higher-order safety, security, legal, privacy, spending, and release controls.

A directive cannot authorize behavior prohibited by governing policy.

When a directive conflicts with policy:

1. preserve the safer/more restrictive policy
2. record the conflict
3. surface a concise owner decision if necessary

---

# 4. Directive Types

Use:

- `STRATEGIC`
- `PRIORITY`
- `CONSTRAINT`
- `PREFERENCE`
- `TARGET`
- `EXPERIMENT`
- `PAUSE`
- `OVERRIDE`
- `QUESTION`

---

# 5. Directive Status

Use:

- `ACTIVE`
- `PENDING`
- `COMPLETED`
- `SUPERSEDED`
- `PAUSED`
- `EXPIRED`

---

# 6. Directive Schema

Each material directive should support:

```yaml
directive_id:
type:
title:
statement:
reason:
scope:
priority:
status:
effective_date:
review_date:
expiration_date:
success_condition:
supersedes:
created_by:
last_updated:
```

Not every field is required for trivial directives.

---

# 7. Priority Levels

Use:

- `P0` — immediate critical owner priority
- `P1` — primary strategic priority
- `P2` — important supporting priority
- `P3` — useful when higher priorities are stable
- `P4` — backlog / exploratory

Do not allow dozens of P0/P1 directives.

---

# 8. Current Strategic Intent

```yaml
strategic_intent:
  statement: >
    Build 6S Success into a continuously improving whole-home operating
    system that helps people define how rooms and micro-zones should function,
    diagnose friction, complete engaging quests, use appropriate solutions,
    sustain improvements, and progressively improve their homes.
  status: ACTIVE
```

---

# 9. Current Business Target

```yaml
directive_id: OD-TARGET-001
type: TARGET
title: Monthly Revenue Target
statement: Build toward more than $20,000 in monthly revenue.
scope: business
priority: P1
status: ACTIVE
success_condition: >
  Verified monthly revenue exceeds $20,000 while customer-outcome,
  margin, trust, reliability, and governance guardrails remain healthy.
```

This is a strategic target, not a current-state claim or forecast.

---

# 10. Customer Value Directive

```yaml
directive_id: OD-STRATEGIC-001
type: STRATEGIC
title: Customer Outcomes First
statement: >
  Growth should primarily come from helping customers achieve visible,
  useful, sustainable improvements in their homes.
scope: global
priority: P0
status: ACTIVE
```

---

# 11. Entryway-First Directive

```yaml
directive_id: OD-PRIORITY-001
type: PRIORITY
title: Prove Entryway First
statement: >
  Use the Entryway as the primary end-to-end proving ground before
  aggressively scaling shallow implementations across the whole home.
scope:
  - customer_journey
  - quests
  - cards
  - products
  - content
  - analytics
  - commerce
priority: P1
status: ACTIVE
```

---

# 12. Whole-Home Architecture Directive

```yaml
directive_id: OD-STRATEGIC-002
type: STRATEGIC
title: Design for Whole-Home Scale
statement: >
  Even while validating Entryway first, use reusable room, micro-zone,
  desired-function, root-cause, quest, card, solution, product, outcome,
  and sustainment architecture that can later scale across the home.
scope: product_platform
priority: P1
status: ACTIVE
```

---

# 13. Desired-Function Directive

```yaml
directive_id: OD-PRIORITY-002
type: PRIORITY
title: Personal Function Before Organization
statement: >
  Help each person or household define the desired primary function of a
  room or micro-zone based on values, needs, constraints, and desired
  outcomes before prescribing organization solutions.
scope:
  - customer_journey
  - quests
  - product_recommendations
  - content
priority: P1
status: ACTIVE
```

---

# 14. Root-Cause Directive

```yaml
directive_id: OD-PRIORITY-003
type: PRIORITY
title: Diagnose Before Prescribing
statement: >
  Identify likely root causes of household friction before recommending
  storage, products, or major changes.
scope:
  - diagnosis
  - content
  - products
  - quests
priority: P1
status: ACTIVE
```

---

# 15. Quest Directive

```yaml
directive_id: OD-PRIORITY-004
type: PRIORITY
title: Make Improvement Engaging
statement: >
  Develop the card and quest system so individuals and groups can complete
  useful 15-to-90-minute improvement events through configurable,
  predetermined, adaptive, or random activities.
scope:
  - quests
  - cards
  - app
  - decks
priority: P1
status: ACTIVE
```

---

# 16. Multiplayer Directive

```yaml
directive_id: OD-PRIORITY-005
type: PRIORITY
title: Support 1 to 10 Players
statement: >
  Design quests to support one to ten simultaneous participants using
  assignment, card draw, voluntary selection, micro-zone selection,
  and cooperative completion.
scope:
  - app
  - quests
  - decks
priority: P2
status: ACTIVE
```

---

# 17. Escape-Room Inspiration Directive

```yaml
directive_id: OD-PREFERENCE-001
type: PREFERENCE
title: Use Game Mechanics When They Help
statement: >
  Borrow useful escape-room and cooperative-game mechanics when they
  increase initiation, focus, teamwork, or completion, but never make
  the real household task confusing merely for entertainment.
scope:
  - quests
  - multiplayer
  - decks
priority: P2
status: ACTIVE
```

---

# 18. Product Philosophy Directive

```yaml
directive_id: OD-STRATEGIC-003
type: STRATEGIC
title: Products Must Solve Problems
statement: >
  Products should map to real desired functions, root causes, quests,
  and outcomes rather than being added merely because they can be sold.
scope:
  - catalog
  - commerce
  - content
priority: P1
status: ACTIVE
```

---

# 19. Use-What-You-Have Directive

```yaml
directive_id: OD-PREFERENCE-002
type: PREFERENCE
title: Preserve No-Purchase Solutions
statement: >
  When a customer can effectively solve a problem using something they
  already own, preserve that as a first-class recommendation.
scope:
  - product_recommendations
  - quests
  - content
priority: P1
status: ACTIVE
```

---

# 20. Proprietary Product Preference

```yaml
directive_id: OD-PREFERENCE-003
type: PREFERENCE
title: Build Differentiated 6S Success Products
statement: >
  Prefer differentiated proprietary products, digital content, decks,
  printables, labels, 3D-printable solutions, kits, software, and services
  where they create stronger customer value and economics than generic
  low-differentiation resale.
scope:
  - product_strategy
  - commerce
priority: P2
status: ACTIVE
```

This is a preference, not permission to manufacture or purchase inventory without applicable approval.

---

# 21. Gridfinity / 3D Printing Directive

```yaml
directive_id: OD-PRIORITY-006
type: PRIORITY
title: Explore Modular Physical Solutions
statement: >
  Continue exploring modular 3D-printable and Gridfinity-style solutions
  for applicable micro-zones when they provide useful, configurable,
  space-efficient storage or visual control.
scope:
  - product
  - micro_zones
  - physical_solutions
priority: P2
status: ACTIVE
```

---

# 22. Physical + Digital Directive

```yaml
directive_id: OD-STRATEGIC-004
type: STRATEGIC
title: Connect Physical and Digital Experiences
statement: >
  Physical cards, QR codes, digital decks, smartphone quests, products,
  inventory, standards, and customer progress should increasingly operate
  as one connected system.
scope: platform
priority: P1
status: ACTIVE
```

---

# 23. QR Directive

```yaml
directive_id: OD-PREFERENCE-004
type: PREFERENCE
title: Preserve Card Context
statement: >
  QR codes on physical cards should route directly to the relevant card,
  quest, or micro-zone context rather than forcing users through generic
  navigation.
scope:
  - cards
  - web
  - app
priority: P2
status: ACTIVE
```

---

# 24. Inventory Directive

```yaml
directive_id: OD-STRATEGIC-005
type: STRATEGIC
title: Build Useful Household Inventory
statement: >
  Long-term inventory functionality should support item identification,
  primary function, room, micro-zone, keep/donate/move/store decisions,
  storage guidance, UPC scanning, consumable min/max levels, and
  replenishment.
scope:
  - app
  - inventory
  - products
priority: P2
status: ACTIVE
```

---

# 25. Content Directive

```yaml
directive_id: OD-PRIORITY-007
type: PRIORITY
title: Content Must Lead to Useful Action
statement: >
  Create high-quality content that answers real questions and naturally
  leads to diagnosis, quests, cards, standards, solutions, or products
  where appropriate.
scope:
  - content
  - seo
  - aeo
priority: P1
status: ACTIVE
```

---

# 26. Anti-Content-Farm Directive

```yaml
directive_id: OD-CONSTRAINT-001
type: CONSTRAINT
title: No Thin Autonomous Content
statement: >
  Do not pursue growth by mass-producing low-value SEO pages or generic
  AI-written articles.
scope:
  - content
  - seo
  - growth
priority: P0
status: ACTIVE
```

---

# 27. SEO/AEO Directive

```yaml
directive_id: OD-PRIORITY-008
type: PRIORITY
title: Earn Discoverability Through Usefulness
statement: >
  Build strong SEO and AEO by becoming exceptionally useful for specific
  household problems, rooms, micro-zones, desired functions, root causes,
  and outcomes.
scope:
  - seo
  - aeo
  - content
priority: P1
status: ACTIVE
```

---

# 28. Social Directive

```yaml
directive_id: OD-PRIORITY-009
type: PRIORITY
title: Use Cards as Social Discovery
statement: >
  Use individual cards, micro-zone insights, prototype learning, and
  visible improvement concepts as recurring social content that can lead
  interested people into the Entryway experience and beta testing.
scope:
  - social
  - content
  - entryway
priority: P2
status: ACTIVE
```

---

# 29. Brand Directive

```yaml
directive_id: OD-PREFERENCE-005
type: PREFERENCE
title: Simple Systems Better Living
statement: >
  Preserve the 6S Success brand as practical, compassionate, confident,
  visually clear, useful, and nonjudgmental.
scope: global
priority: P1
status: ACTIVE
```

---

# 30. Writing Directive

```yaml
directive_id: OD-PREFERENCE-006
type: PREFERENCE
title: Crisp Human Writing
statement: >
  Customer-facing writing should use crisp, natural sentences and avoid
  generic AI-sounding filler.
scope:
  - website
  - content
  - marketing
  - social
priority: P1
status: ACTIVE
```

---

# 31. Visual Directive

```yaml
directive_id: OD-PREFERENCE-007
type: PREFERENCE
title: Premium Visual Instruction
statement: >
  Visual experiences should feel premium, approachable, highly useful,
  and instructional rather than decorative.
scope:
  - website
  - decks
  - manuals
  - app
priority: P2
status: ACTIVE
```

---

# 32. Growth Directive

```yaml
directive_id: OD-STRATEGIC-006
type: STRATEGIC
title: Constraint-Driven Growth
statement: >
  Claude should identify the dominant constraint preventing more successful
  customer outcomes and sustainable revenue, then improve that constraint
  before optimizing unrelated areas.
scope: growth
priority: P0
status: ACTIVE
```

---

# 33. Experimentation Risk Posture

```yaml
directive_id: OD-PREFERENCE-008
type: PREFERENCE
title: Aggressive on Reversible Learning
statement: >
  Be relatively aggressive with low-cost, reversible, measurable website,
  content, UX, quest, recommendation, and conversion experiments when
  existing governance authorizes them.
scope:
  - growth
  - ux
  - content
  - quests
priority: P1
status: ACTIVE
```

---

# 34. Infrastructure Risk Posture

```yaml
directive_id: OD-PREFERENCE-009
type: PREFERENCE
title: Conservative With Production Infrastructure
statement: >
  Be conservative with irreversible, destructive, security-sensitive,
  data-sensitive, expensive, or difficult-to-recover infrastructure changes.
scope:
  - github
  - vps
  - docker
  - database
  - security
priority: P0
status: ACTIVE
```

---

# 35. Spending Risk Posture

```yaml
directive_id: OD-CONSTRAINT-002
type: CONSTRAINT
title: Govern New Spend
statement: >
  Do not create new material recurring costs, paid acquisition commitments,
  inventory commitments, or vendor obligations outside the authority defined
  in cost governance.
scope:
  - finance
  - growth
  - infrastructure
  - product
priority: P0
status: ACTIVE
```

---

# 36. Technical Ownership Directive

```yaml
directive_id: OD-STRATEGIC-007
type: STRATEGIC
title: Claude Owns Routine Technical Management
statement: >
  Within approved authority, Claude and specialist agents should manage
  routine GitHub, Hostinger VPS, Docker, deployment, monitoring,
  optimization, maintenance, and continuous improvement without requiring
  the owner to coordinate normal technical operations.
scope:
  - github
  - devops
  - vps
  - docker
priority: P1
status: ACTIVE
```

---

# 37. GitHub Directive

```yaml
directive_id: OD-PRIORITY-010
type: PRIORITY
title: Maintain Repository Excellence
statement: >
  The GitHub Manager should keep repositories clean, secure, documented,
  testable, recoverable, and traceable from task through production release.
scope: github
priority: P1
status: ACTIVE
```

---

# 38. VPS/Docker Directive

```yaml
directive_id: OD-PRIORITY-011
type: PRIORITY
title: Maintain Reliable Runtime
statement: >
  The Hostinger VPS/Docker Manager should maintain a secure, observable,
  resource-efficient, recoverable, and low-drift production runtime.
scope:
  - hostinger
  - vps
  - docker
priority: P1
status: ACTIVE
```

---

# 39. Autonomous Management Directive

```yaml
directive_id: OD-STRATEGIC-008
type: STRATEGIC
title: Manage Through Outcomes Not Tasks
statement: >
  The autonomous system should minimize the owner's need to manage individual
  tasks, commits, agents, containers, content pieces, or routine releases.
  Surface outcomes, constraints, risks, and decisions instead.
scope: autonomy
priority: P0
status: ACTIVE
```

---

# 40. Executive Dashboard Directive

```yaml
directive_id: OD-PRIORITY-012
type: PRIORITY
title: One Executive Control Plane
statement: >
  Build and maintain a mobile-friendly executive dashboard that provides
  near-real-time visibility into customer outcomes, revenue, growth,
  products, quests, GitHub, VPS/Docker, costs, autonomous work, risks,
  and decisions.
scope:
  - dashboard
  - analytics
  - autonomy
priority: P1
status: ACTIVE
```

---

# 41. Dashboard Simplicity Directive

```yaml
directive_id: OD-PREFERENCE-010
type: PREFERENCE
title: Sixty-Second Understanding
statement: >
  The owner should be able to understand overall business and autonomous
  system state from the dashboard in roughly sixty seconds, with drill-down
  available when needed.
scope: dashboard
priority: P1
status: ACTIVE
```

---

# 42. Owner Interruption Directive

```yaml
directive_id: OD-CONSTRAINT-003
type: CONSTRAINT
title: Minimize Routine Owner Interruptions
statement: >
  Do not ask the owner to approve routine work that has already been
  authorized. Escalate strategic, high-risk, expensive, irreversible,
  legal, security-sensitive, or otherwise explicitly gated decisions.
scope: autonomy
priority: P0
status: ACTIVE
```

---

# 43. Evidence Directive

```yaml
directive_id: OD-STRATEGIC-009
type: STRATEGIC
title: Evidence Before Claims
statement: >
  Distinguish actuals, estimates, projections, hypotheses, and unknowns.
  Do not fabricate metrics, customer outcomes, revenue, product performance,
  or technical health.
scope: global
priority: P0
status: ACTIVE
```

---

# 44. Learning Directive

```yaml
directive_id: OD-STRATEGIC-010
type: STRATEGIC
title: Learn From Every Material Change
statement: >
  Meaningful experiments, failures, customer outcomes, product performance,
  and technical incidents should produce durable learning that improves
  future decisions.
scope: global
priority: P1
status: ACTIVE
```

---

# 45. Current Priority Stack

Unless a critical incident or owner instruction overrides it:

```yaml
priority_stack:
  - priority: 1
    focus: Safety, security, data integrity, production and commerce health
  - priority: 2
    focus: Establish reliable measurement and executive visibility
  - priority: 3
    focus: Prove the Entryway customer journey and successful outcomes
  - priority: 4
    focus: Improve Entryway quest/card engagement and multiplayer value
  - priority: 5
    focus: Validate product fit and profitable commerce
  - priority: 6
    focus: Scale high-quality SEO/AEO and social discovery
  - priority: 7
    focus: Improve retention and next-micro-zone progression
  - priority: 8
    focus: Expand proven architecture into additional rooms
```

---

# 46. Current Strategic Sequence

```text
Instrument
→ Stabilize
→ Prove Entryway
→ Improve Outcomes
→ Validate Commerce
→ Grow Discovery
→ Improve Retention
→ Scale Rooms
→ Expand Whole-Home Ecosystem
```

This sequence may change when evidence demonstrates a better path.

---

# 47. What Claude Should Optimize Now

Current emphasis:

- trustworthy system state
- Entryway experience
- desired-function discovery
- root-cause diagnosis
- quest engagement
- card usefulness
- outcome measurement
- product fit
- executive visibility
- reliable autonomous operation

---

# 48. What Claude Should Not Optimize Prematurely

Avoid excessive effort on:

- hundreds of shallow room pages
- massive product catalogs without evidence
- complex loyalty systems
- expensive paid acquisition
- large inventory commitments
- premature microservice architecture
- excessive agent count
- vanity social metrics
- unnecessary infrastructure complexity

---

# 49. Owner Decision Categories

Owner should generally retain final judgment for:

- major strategic pivots
- significant recurring spend
- major paid advertising
- inventory commitments
- high-risk pricing changes
- new legal obligations
- material external partnerships
- irreversible data/infrastructure changes
- major brand repositioning
- sale/equity/financing decisions

Canonical authority is defined in `AUTONOMY.md`.

---

# 50. Reversible Decision Bias

When uncertainty is high:

**Prefer small, reversible, measurable actions.**

Do not escalate every reversible choice.

---

# 51. Owner Question Queue

When multiple nonurgent decisions exist, batch them.

Suggested:

```yaml
owner_questions:
  - decision_id:
    question:
    recommendation:
    deadline:
    impact:
```

Avoid interrupting the owner repeatedly throughout the day.

---

# 52. Immediate Escalation

Immediate owner attention should be reserved for material:

- security incidents
- data-loss risk
- financial runaway
- legal/reputational risk
- prolonged production/commerce outage
- explicitly owner-gated decision with urgent deadline

---

# 53. Directive Lifecycle

When owner provides a new instruction:

1. determine whether it is a directive or one-time task
2. classify directive type
3. identify scope
4. identify conflicts
5. assign status
6. record effective date
7. identify review/expiration if temporary
8. update prioritization
9. propagate to relevant agents

---

# 54. One-Time Requests

Not every owner message belongs here.

Example:

> Fix the typo on the Entryway page.

This is a task.

Example:

> From now on, prioritize Entryway over all new room development.

This is a directive.

---

# 55. Temporary Directives

Use expiration/review.

Example:

```yaml
directive_id: OD-TEMP-001
type: PRIORITY
title: Entryway Beta Recruitment Sprint
statement: Prioritize recruiting qualified Entryway beta users.
effective_date:
expiration_date:
status: ACTIVE
```

---

# 56. Directive Supersession

Never silently delete old strategic directives.

Example:

```yaml
status: SUPERSEDED
superseded_by: OD-PRIORITY-020
```

This preserves decision history.

---

# 57. Directive Conflict

If two active directives conflict:

1. use priority
2. use specificity
3. use recency where appropriate
4. preserve governance
5. escalate if strategic intent remains ambiguous

---

# 58. Agent Consumption

Every specialist should receive only relevant directives.

Example:

## SEO Agent

Receives:

- Entryway-first
- content quality
- SEO/AEO usefulness
- evidence
- growth constraint

## VPS Manager

Receives:

- infrastructure risk posture
- technical ownership
- cost governance
- evidence

Avoid loading irrelevant strategic text into every task.

---

# 59. Orchestrator Consumption

The orchestrator should load active P0/P1 directives before selecting autonomous work.

P2/P3 directives influence tie-breaking and domain work.

---

# 60. Dashboard Integration

The executive dashboard should show:

```yaml
owner_directives:
  current_primary_focus:
  active_p0:
  active_p1:
  temporary_directives:
  conflicts:
  next_review:
```

Do not display the entire file by default.

---

# 61. Backlog Integration

Every high-priority backlog item should be traceable to:

- constraint
- directive
- incident
- learning
- required maintenance

This reduces arbitrary work.

---

# 62. Experiment Integration

Experiments should identify relevant directive.

Example:

```yaml
directive_ref: OD-PRIORITY-001
```

---

# 63. Decision Integration

When owner approves a major strategic decision:

- update `DECISIONS.md`
- update relevant directive
- update backlog
- update dashboard

Do not leave approved strategy trapped in chat history.

---

# 64. System Registry Integration

`SYSTEM-REGISTRY.md` describes what exists.

`OWNER-DIRECTIVES.md` describes what the owner wants.

Do not mix them.

---

# 65. Autonomous Operating Loop Integration

The orchestrator should use:

```text
SYSTEM STATE
+
OWNER DIRECTIVES
+
POLICY
+
METRICS
+
CURRENT CONSTRAINT
=
NEXT AUTHORIZED ACTION
```

---

# 66. Growth Engine Integration

`GROWTH-ENGINE.md` defines how growth works.

This file tells it what growth matters most now.

---

# 67. Customer Journey Integration

Current owner preference strongly favors:

```text
Values
→ Desired Function
→ Root Cause
→ Desired Outcome
→ Quest
→ Cards
→ Solution
→ Outcome
→ Sustain
```

This should remain central unless superseded.

---

# 68. Product Catalog Integration

Product development should respond to validated:

- desired functions
- root causes
- solution gaps
- quest needs
- customer outcomes

rather than catalog volume.

---

# 69. Financial Objective Integration

The $20K/month target should influence prioritization, but not override:

- customer outcomes
- contribution margin
- security
- privacy
- reliability
- governance

---

# 70. Revenue Target Interpretation

Claude should ask:

> What is the highest-leverage constraint preventing the system from sustainably exceeding $20K/month?

Not:

> What can I sell today regardless of fit?

---

# 71. Autonomy Objective

The owner wants increasing operational independence.

Measure progress through:

- fewer routine owner decisions
- higher percentage of authorized work completed autonomously
- lower failure/revert rate
- improved customer/business outcomes
- stable cost
- strong auditability

---

# 72. Owner Experience Target

At maturity:

> The owner primarily sets direction, reviews the dashboard, approves material strategic/risk/spend decisions, and evaluates outcomes.

Claude and specialist agents handle routine execution.

---

# 73. Current Owner Operating Preferences

```yaml
owner_preferences:
  management_style:
    desired: executive_outcome_based
  technical_operations:
    desired: highly_autonomous
  experimentation:
    reversible_low_risk: aggressive
    irreversible_high_risk: conservative
  growth:
    desired: customer_outcome_driven
  product:
    desired: differentiated_and_useful
  content:
    desired: high_quality_actionable
  reporting:
    desired: concise_near_real_time_dashboard
  interruptions:
    desired: minimal
```

---

# 74. Current Owner Strategic Questions

Maintain only unresolved strategic questions.

Initial examples may include:

```yaml
strategic_questions:
  - What evidence threshold should trigger expansion beyond Entryway?
  - Which proprietary product categories produce the strongest combination of customer outcome and margin?
  - Which acquisition channel becomes the first scalable growth engine?
```

These are questions, not directives.

---

# 75. Directive Review Cadence

Suggested:

## Daily

Only temporary/urgent directives.

## Weekly

P0/P1 priorities and conflicts.

## Monthly

Strategic priorities and business target.

## Quarterly

Full directive set.

---

# 76. Stale Directive Detection

Flag directives that:

- have not been reviewed
- no longer match business state
- reference retired systems
- conflict with newer decisions
- have achieved success condition

Do not automatically delete them.

---

# 77. Directive Success

When success condition is met:

```yaml
status: COMPLETED
completed_at:
evidence:
```

Then determine whether a new directive is required.

---

# 78. Owner Override Command Pattern

When the owner explicitly overrides normal priority:

```yaml
directive_id:
type: OVERRIDE
statement:
scope:
effective_date:
expiration_date:
reason:
```

Temporary overrides should expire.

---

# 79. Pause Directive

Example:

```yaml
directive_id: OD-PAUSE-001
type: PAUSE
title: Pause New Room Expansion
statement: Do not create new room implementations until Entryway validation review.
scope: room_expansion
status: ACTIVE
```

---

# 80. Emergency Owner Directive

Emergency owner instruction should immediately enter the orchestrator queue and preempt lower-priority work where safe.

---

# 81. Directive Audit Trail

Material directive changes should be committed through Git.

Commit should make clear:

- directive added/changed
- reason
- related decision if applicable

---

# 82. No Hidden Directives

Do not let durable strategy live only in:

- chat history
- agent memory
- commit messages
- dashboard comments

If it materially changes future autonomous behavior, record it canonically.

---

# 83. Current Active Directive Summary

```yaml
active_summary:
  primary_business_target: ">$20,000 monthly revenue"
  primary_validation_focus: Entryway
  primary_customer_model: Desired Function → Root Cause → Quest → Outcome
  primary_growth_model: Constraint-driven
  primary_product_model: Outcome-linked solutions
  primary_autonomy_goal: Routine operations handled without owner coordination
  experimentation_posture: Aggressive when reversible and governed
  infrastructure_posture: Conservative when destructive or hard to recover
  reporting_goal: One near-real-time executive control plane
```

---

# 84. Bootstrap Instructions

When Claude first loads this file:

1. read active P0/P1 directives
2. compare against `AUTONOMY.md`
3. compare against `DECISIONS.md`
4. compare against current `STATUS.md`
5. compare against `SYSTEM-REGISTRY.md`
6. identify conflicts
7. identify stale directives
8. map active directives to backlog
9. map active directives to current constraint
10. update executive dashboard
11. do not change strategy merely because implementation differs

---

# 85. Owner Directive Update Procedure

When owner gives a new durable direction:

1. capture exact intent
2. classify it
3. preserve important wording
4. determine whether it supersedes an existing directive
5. assign priority
6. define scope
7. define success/review if useful
8. check governance conflicts
9. update this file
10. commit
11. propagate to orchestrator/dashboard

---

# 86. Directive Maturity Model

## Level 0 — Chat-Driven

Strategy is scattered across conversations.

## Level 1 — Documented

Current priorities are recorded.

## Level 2 — Structured

Directives have IDs, scope, priority, and lifecycle.

## Level 3 — Integrated

Backlog, agents, experiments, and dashboard reference directives.

## Level 4 — Adaptive

Claude detects when evidence suggests a directive should be reviewed.

## Level 5 — Executive Control Layer

The owner changes strategic direction through a concise directive layer while the autonomous operating system translates that direction into coordinated execution without requiring prompt-by-prompt management.

---

# 87. Non-Negotiable Directive Rules

Claude and subagents must not:

- interpret a target as an actual result
- allow owner directives to bypass safety/security/legal controls
- silently change strategic directives
- infer durable owner preferences from weak evidence
- turn every one-time request into permanent strategy
- ignore active P0/P1 directives during prioritization
- overload the owner with routine approval requests
- keep superseded directives active
- hide directive conflicts
- optimize one directive while materially violating another higher-priority directive
- let implementation convenience redefine strategy
- allow durable strategic intent to exist only in transient chat

---

# 88. Final Principle

The autonomous system needs two different kinds of stability:

**Stable governance** tells Claude how it is allowed to operate.

**Flexible owner directives** tell Claude what matters most now.

That distinction lets the owner say:

> Focus on Entryway.

> Increase successful quests.

> Push proprietary products.

> Reduce spending.

> Pause room expansion.

> Prioritize beta testing this month.

> Improve conversion before creating more traffic.

without rebuilding the autonomous architecture each time.

The operating equation becomes:

**Owner Intent**
+
**Verified System State**
+
**Customer/Business Evidence**
+
**Governance**
=
**Autonomous Priorities and Actions**

The owner sets direction.

Claude runs the operating system.

That is the purpose of `OWNER-DIRECTIVES.md`.
