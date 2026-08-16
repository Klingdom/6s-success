# 6S Success Autonomous Backlog

> Canonical prioritization and work-control system for Claude Code and all 6S Success specialist agents.

## 1. Purpose

`BACKLOG.md` converts strategy, measured constraints, incidents, customer learning, experiments, SEO/AEO opportunities, product opportunities, and technical risks into **controlled executable work**.

It answers:

- What should Claude work on next?
- Why is that more important than other work?
- Who owns it?
- What evidence supports it?
- What outcome should change?
- How will success be measured?
- Is autonomous execution permitted?
- When should work stop?
- What is blocked?
- What should not be worked on?

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`
- `DATA-SOURCES.md`
- `DASHBOARD.md`

---

# 2. Core Rule

**The backlog exists to improve outcomes, not to keep agents busy.**

Claude must not create work merely because:

- an agent is idle
- a feature sounds interesting
- a competitor has it
- more content could be generated
- more automation is technically possible
- a code area could be refactored
- a dashboard could have another chart

Every material backlog item must connect to a customer outcome, strategic objective, current constraint, risk, or validated learning opportunity.

---

# 3. Work-in-Progress Limit

Default maximum:

**3 major active workstreams**

Recommended current categories:

1. Autonomous operating/data foundation
2. GitHub-to-production reliability
3. Entryway customer/monetization loop

Claude may perform small maintenance tasks outside these streams when they do not materially distract from priority work.

Do not evade the WIP limit by splitting one major initiative into many "small" tasks.

---

# 4. Backlog States

Every item must have one state:

- `INBOX`
- `NEEDS_EVIDENCE`
- `READY`
- `ACTIVE`
- `BLOCKED`
- `WAITING_FOR_DATA`
- `WAITING_FOR_APPROVAL`
- `VALIDATING`
- `DONE`
- `REJECTED`
- `DEFERRED`

`DONE` means outcome and verification are recorded, not merely that code was written.

---

# 5. Priority Classes

Use:

## P0 — Immediate

Customer, security, financial, data-loss, or production emergency.

Examples:

- checkout unavailable
- production outage
- active critical security issue
- imminent data loss
- failed recovery path during incident

P0 interrupts normal WIP.

## P1 — Critical Strategic Constraint

Highest-value work directly addressing the current business/product constraint or major reliability risk.

## P2 — High Value

Strong evidence of customer/business value but not the primary constraint.

## P3 — Useful

Meaningful improvement with lower urgency or impact.

## P4 — Optional

Good idea without current evidence or urgency.

## PARKED

Not currently aligned with strategy.

Priority is not determined by who suggested the item.

---

# 6. Current Strategic Ordering

Unless live evidence indicates otherwise, prioritize:

1. Production/customer safety and reliability
2. Data truth and measurement
3. Current primary constraint
4. Entryway product learning
5. Monetization validation
6. SEO/AEO opportunities connected to qualified demand
7. Reusable architecture
8. Technical debt with demonstrated impact
9. Expansion
10. speculative features

---

# 7. Backlog Item Schema

Every material item should use:

```yaml
id: BL-0001
title: Short action-oriented title
state: READY
priority: P1
type: PRODUCT
workstream: Entryway
owner: product-manager
created: YYYY-MM-DD
updated: YYYY-MM-DD

problem: >
  What verified problem or opportunity exists?

evidence:
  - source: ...
    observation: ...

customer_outcome: >
  What should become better for the customer?

business_outcome: >
  What business result may improve?

primary_metric: quest_completion_rate

guardrails:
  - purchase_conversion_rate
  - application_error_rate

baseline: UNKNOWN
target_or_expected_direction: increase

hypothesis: >
  If we do X for Y, metric Z should improve because...

scope:
  in:
    - ...
  out:
    - ...

dependencies:
  - ...

autonomy_class: GREEN
approval_required: false

implementation_notes:
  - ...

validation:
  method: ...
  minimum_window: ...
  success_condition: ...
  failure_condition: ...

rollback:
  possible: true
  method: ...

result:
  status: NOT_MEASURED
  evidence: []
  decision: null
```

Small tasks may use a compact version.

---

# 8. Backlog Item Types

Use one primary type:

- `INCIDENT`
- `SECURITY`
- `RELIABILITY`
- `DATA`
- `PRODUCT`
- `UX`
- `EXPERIMENT`
- `COMMERCE`
- `SEO`
- `AEO`
- `CONTENT`
- `GROWTH`
- `INFRASTRUCTURE`
- `DEVOPS`
- `GITHUB`
- `COST`
- `CUSTOMER_FEEDBACK`
- `DOCUMENTATION`
- `TECH_DEBT`
- `STRATEGY`

---

# 9. Intake Sources

Backlog items may originate from:

- executive dashboard
- production incident
- monitoring
- security findings
- customer feedback
- product analytics
- Search Console
- SEO crawl
- commerce data
- payment reconciliation
- experiment results
- agent observation
- GitHub issues
- dependency updates
- VPS/Docker capacity
- backup/recovery testing
- owner request
- strategic review

Every item should preserve its origin.

---

# 10. Evidence Standard

Evidence can include:

- verified metric
- customer behavior
- customer feedback
- production telemetry
- search demand
- experiment result
- error logs
- support pattern
- commerce data
- security finding
- reproducible defect

Weak evidence:

- "best practice"
- agent preference
- generic industry advice
- competitor feature
- aesthetic opinion

Weak-evidence items should usually enter `NEEDS_EVIDENCE`, not `READY`.

---

# 11. Prioritization Formula

Do not rely blindly on one mathematical score.

Use a structured decision model.

Evaluate:

## Customer Impact

0–5

Does it improve real household outcomes?

## Strategic Alignment

0–5

Does it strengthen the current strategic loop?

## Constraint Impact

0–5

Does it address the current primary constraint?

## Revenue/Economic Impact

0–5

Could it improve sustainable economics?

## Learning Value

0–5

Will it resolve important uncertainty?

## Confidence

0–5

How strong is the evidence?

## Urgency/Risk Reduction

0–5

What happens if we delay?

## Effort

1–5

How much implementation/coordination is required?

## Operational Complexity

0–5

How much ongoing burden will it create?

A useful heuristic:

**Priority Value = positive impact × confidence / effort**

But human/agent judgment remains necessary.

P0 safety/security/reliability incidents override normal scoring.

---

# 12. Primary Constraint Rule

The dashboard should identify the current primary constraint when evidence permits.

Possible constraints:

- DATA
- TRAFFIC
- ACTIVATION
- QUEST COMPLETION
- PRODUCT FIT
- PRODUCT EXPOSURE
- CONVERSION
- AOV
- RETENTION
- MARGIN
- FULFILLMENT
- RELIABILITY
- UNKNOWN

At least one major active workstream should normally address the current constraint.

If none does, explain why.

---

# 13. Data Before Optimization

If critical data is `UNKNOWN`, unreliable, or unreconciled, the first backlog item may need to fix measurement.

Example:

Do not optimize checkout conversion if completed purchases cannot be reliably reconciled.

Do not optimize quest completion if completion events are not trustworthy.

---

# 14. Experiment vs Feature

When uncertainty is high, prefer an experiment.

Use a full feature when:

- customer need is established
- solution is understood
- implementation risk is low
- measurement exists

Use an experiment when:

- value is uncertain
- behavior is uncertain
- pricing is uncertain
- UX is uncertain
- demand is uncertain

---

# 15. Smallest Useful Change

Prefer:

**small change**
→ **measure**
→ **learn**
→ **iterate**

over:

**large build**
→ **months of work**
→ **uncertain result**

This is especially important before Entryway validation.

---

# 16. Definition of Ready

A material item is `READY` when:

- problem is understandable
- evidence exists
- owner/agent is known
- scope is bounded
- metric exists or measurement plan exists
- dependencies are known
- autonomy class is known
- major safety/security issues are considered
- success can be evaluated

If these are missing, use `NEEDS_EVIDENCE`.

---

# 17. Definition of Active

An item becomes `ACTIVE` only when:

- it is within WIP limit
- prerequisites are satisfied
- execution has actually begun

Do not mark planned work active.

---

# 18. Definition of Done

A material item is `DONE` when:

1. implementation is complete
2. tests/verification pass
3. deployment is verified if applicable
4. monitoring is healthy
5. metric/behavior is observed when appropriate
6. documentation is updated
7. result is recorded
8. follow-up is created only if justified

Code merged is not automatically done.

---

# 19. Validation State

After implementation, items may enter `VALIDATING`.

Use this when enough time/data is required to determine outcome.

Do not immediately call a change successful because it deployed.

---

# 20. Failure Is Allowed

If an experiment or improvement fails:

- record result
- revert if appropriate
- preserve learning
- mark `DONE` or `REJECTED` as appropriate

Do not hide failed work.

Failed experiments can be valuable.

---

# 21. Kill Criteria

Stop or reject work when:

- evidence contradicts hypothesis
- customer value is weak
- effort expands materially
- operational complexity becomes excessive
- safety/security risk is disproportionate
- economics are poor
- a better solution emerges
- strategic alignment changes
- dependency is no longer available

Avoid sunk-cost behavior.

---

# 22. Blocked Items

A `BLOCKED` item must state:

- blocker
- owner of blocker
- impact
- next check/action

Do not leave items blocked indefinitely without review.

---

# 23. Waiting for Approval

Use `WAITING_FOR_APPROVAL` only for actions genuinely requiring owner authorization under `AUTONOMY.md`.

Include:

- exact decision
- recommendation
- alternatives
- cost/risk
- impact of delay

Do not use approval state to offload routine decisions to the owner.

---

# 24. Autonomous Authority

Every item must respect the autonomy classification defined in `AUTONOMY.md`.

Typical pattern:

## GREEN

Claude may execute and verify autonomously.

## YELLOW

Claude may execute within documented bounded conditions.

## RED

Explicit owner approval required.

If classification is unclear, inspect `AUTONOMY.md`; do not invent authority.

---

# 25. Incident Handling

P0/P1 incidents should create or link to an incident record.

Sequence:

**Detect**
→ **Stabilize**
→ **Restore**
→ **Verify**
→ **Root Cause**
→ **Corrective Action**
→ **Learning**

Do not prioritize roadmap work over active customer-impacting incidents.

---

# 26. Security Handling

Critical/high security work may override normal business prioritization.

Do not publish sensitive vulnerability details in the general backlog.

Use sanitized descriptions.

---

# 27. Reliability Work

Reliability items should connect to:

- customer journey
- incident
- capacity risk
- recovery risk
- change failure
- measurable technical risk

Avoid infrastructure work solely because it is technically elegant.

---

# 28. Technical Debt

Technical debt is backlog-worthy when it causes or materially increases:

- defects
- slow delivery
- security risk
- reliability risk
- operating cost
- inability to measure
- inability to experiment

"Code could be cleaner" is not sufficient by itself.

---

# 29. SEO Backlog

SEO items should include:

- query/page opportunity
- evidence
- current performance
- customer intent
- room/micro-zone mapping
- expected customer action
- commercial/product relevance where appropriate

Avoid bulk creation of low-value pages.

---

# 30. AEO Backlog

AEO items should target real questions and machine-readable clarity.

Examples:

- direct-answer gaps
- unclear entity relationships
- missing structured explanatory content
- crawler access issue
- weak FAQ coverage where useful

Do not create fake authority or fabricated citations.

---

# 31. Content Backlog

Content items should answer:

- What customer question?
- Which room?
- Which micro-zone?
- Which root cause?
- What useful outcome?
- What existing page competes/overlaps?
- What next action should the user take?

Prefer updating strong existing pages over creating duplicates.

---

# 32. Product Backlog

Product work must map to:

**Desired Function**
→ **Friction**
→ **Root Cause**
→ **Solution**

Every product backlog item should explain why the product is better than simply giving the customer instructions.

---

# 33. Commerce Backlog

Commerce work may target:

- conversion
- checkout
- AOV
- bundles
- product availability
- refunds
- fulfillment
- margin

Guardrails should include customer trust and product outcome.

---

# 34. Entryway Backlog

Until Entryway is validated, maintain dedicated Entryway priorities.

High-value categories:

- desired-function discovery
- micro-zone navigation
- root-cause diagnosis
- quest selection
- quest completion
- standards
- sustainment
- multiplayer
- digital deck
- physical deck
- product recommendation
- conversion

Do not let expansion work crowd out Entryway learning.

---

# 35. Room Expansion Backlog

Major new room work remains `DEFERRED` until the expansion gate in `STRATEGY.md` is met.

Research may occur earlier if low cost and strategically useful.

---

# 36. GitHub Backlog

`github-manager` may create work for:

- CI failures
- release traceability
- branch protection
- dependency hygiene
- repository structure
- deployment metadata
- rollback support

Prioritize production safety and delivery confidence over repository cosmetics.

---

# 37. VPS/Docker Backlog

`vps-docker-manager` may create work for:

- runtime drift
- resource exhaustion
- unhealthy containers
- unsafe persistent data
- backup gaps
- restore gaps
- deployment reproducibility
- log growth
- certificate/runtime issues

Never delete unknown persistent assets to "clean up" the server.

---

# 38. Dashboard Backlog

Dashboard work should improve decisions.

High-value:

- missing authoritative KPI
- stale data
- reconciliation
- primary constraint visibility
- owner decision visibility

Low-value:

- decorative chart changes
- excessive animation
- vanity metrics

---

# 39. Documentation Backlog

Documentation work is valuable when it:

- prevents repeated errors
- enables autonomous execution
- clarifies authority
- preserves decisions
- preserves learning
- reduces owner dependency

Do not generate documentation nobody uses.

---

# 40. Agent-Generated Backlog Items

Agents may propose backlog items.

They must not automatically promote every proposal to active work.

The orchestrator evaluates:

- evidence
- strategy
- constraint
- WIP
- risk
- expected outcome

---

# 41. Duplicate Detection

Before creating an item:

- search backlog
- search active experiments
- search GitHub issues
- inspect recent decisions
- inspect learnings

Merge duplicates where practical.

---

# 42. Dependency Mapping

Use explicit dependencies.

Example:

`BL-0042 Improve Entryway quest completion`

depends on:

`BL-0031 Validate quest completion event`

Do not optimize unmeasured behavior.

---

# 43. Sequencing

Preferred sequence:

**Instrument**
→ **Baseline**
→ **Hypothesize**
→ **Change**
→ **Verify**
→ **Measure**
→ **Learn**
→ **Standardize**

Not every tiny fix requires the full sequence, but major work should follow it.

---

# 44. Owner Requests

Direct owner requests should be prioritized highly, but still classified for:

- safety
- dependencies
- autonomy
- measurement

If an owner request conflicts with a known critical incident, surface the conflict.

---

# 45. Emergency Override

P0 work may temporarily exceed WIP.

Once stabilized:

- close emergency work
- restore WIP discipline
- reassess displaced priorities

---

# 46. Backlog Grooming Cadence

## Continuous

Agents may add evidence-backed items.

## Daily

Review P0/P1, blockers, data gaps, current constraint.

## Weekly

Re-rank major backlog using current evidence.

## Monthly

Remove stale/speculative work and compare backlog to strategy.

---

# 47. Stale Item Rule

If an item has not progressed and no longer has strong evidence:

- revalidate
- defer
- reject

Do not allow an infinite backlog of old ideas.

---

# 48. Backlog Size

The backlog should be comprehensive enough to preserve important work but small enough to reason about.

Prefer:

- active priorities
- near-term ready queue
- meaningful deferred opportunities

over thousands of speculative tasks.

---

# 49. Current Workstreams

At initialization, use these until verified `STATUS.md` changes them:

## WS-01 Autonomous Operating Foundation

Goal:

Create trustworthy autonomous governance, measurement, and executive visibility.

## WS-02 GitHub-to-Production Control Plane

Goal:

Establish verified source/build/deploy/runtime lineage and safe recovery.

## WS-03 Entryway Customer & Monetization Loop

Goal:

Prove the complete customer improvement and commercial loop in Entryway.

---

# 50. Initial Backlog

The following items are seeded from current strategy.

They are not proof that the underlying systems are missing.

Discovery must verify reality first.

---

## BL-0001 — Verify GitHub Repository and Delivery Control Plane

**Priority:** P1  
**State:** READY  
**Type:** GITHUB  
**Workstream:** WS-02  
**Owner:** github-manager

### Problem

Current GitHub repository, CI/CD, branch, release, and deployment state are not yet verified in the operating documentation.

### Outcome

Know exactly how source becomes production.

### Success

Document verified:

- repository
- default branch
- CI
- release process
- deployment trigger
- release identity
- rollback mechanism

### Autonomy

Read-only discovery first.

---

## BL-0002 — Verify Hostinger VPS and Docker Runtime

**Priority:** P1  
**State:** READY  
**Type:** INFRASTRUCTURE  
**Workstream:** WS-02  
**Owner:** vps-docker-manager

### Problem

Actual VPS/Docker runtime state is currently unverified.

### Outcome

Establish trustworthy production runtime inventory.

### Success

Verify:

- host
- Docker
- Compose
- containers
- images
- networks
- volumes
- proxy
- TLS
- scheduled jobs
- resource health

### Guardrail

Preserve unknown volumes/configuration.

---

## BL-0003 — Reconcile GitHub Release to Running Production

**Priority:** P1  
**State:** BLOCKED  
**Type:** DEVOPS  
**Workstream:** WS-02  
**Owner:** devops-sre

### Dependencies

- BL-0001
- BL-0002

### Outcome

Answer:

**What exact Git commit is running in production?**

### Success

Verified lineage:

Commit
→ Build
→ Image Digest
→ Deployment
→ Running Container
→ Production Verification

---

## BL-0004 — Verify Backup Coverage

**Priority:** P1  
**State:** BLOCKED  
**Type:** RELIABILITY  
**Workstream:** WS-02  
**Owner:** vps-docker-manager

### Dependency

BL-0002

### Outcome

Know whether all required persistent production data is backed up.

### Success

Every required persistent asset has verified backup state.

---

## BL-0005 — Perform Representative Restore Validation

**Priority:** P1  
**State:** BLOCKED  
**Type:** RELIABILITY  
**Workstream:** WS-02  
**Owner:** devops-sre

### Dependency

BL-0004

### Outcome

Move critical backup confidence toward Level 4.

### Success

Representative restore succeeds without risking production.

---

## BL-0006 — Inventory Business Data Sources

**Priority:** P1  
**State:** READY  
**Type:** DATA  
**Workstream:** WS-01  
**Owner:** analytics-intelligence

### Outcome

Verify actual sources for:

- analytics
- product events
- commerce
- payments
- Search Console
- experiments

### Success

Update `DATA-SOURCES.md` from UNVERIFIED to evidence-backed states.

---

## BL-0007 — Establish Revenue Source of Truth

**Priority:** P1  
**State:** BLOCKED  
**Type:** DATA  
**Workstream:** WS-01  
**Owner:** commerce-manager

### Dependency

BL-0006

### Outcome

Define authoritative:

- gross revenue
- net revenue
- refunds
- orders
- AOV
- contribution inputs

### Success

Revenue can be shown on executive dashboard with source, freshness, and confidence.

---

## BL-0008 — Validate Analytics Instrumentation

**Priority:** P1  
**State:** BLOCKED  
**Type:** DATA  
**Workstream:** WS-01  
**Owner:** analytics-intelligence

### Dependency

BL-0006

### Outcome

Verify existing event quality before optimizing funnels.

### Focus

- identity
- environment
- internal/test exclusion
- key events
- purchase reconciliation
- room/micro-zone events if present

---

## BL-0009 — Build Executive Dashboard Skeleton

**Priority:** P1  
**State:** READY  
**Type:** DATA  
**Workstream:** WS-01  
**Owner:** analytics-intelligence

### Outcome

Implement the dashboard architecture from `DASHBOARD.md`.

### Important

Use truthful `UNKNOWN` states until sources are verified.

Do not seed fake production metrics.

---

## BL-0010 — Connect Production Health to Dashboard

**Priority:** P1  
**State:** BLOCKED  
**Type:** RELIABILITY  
**Workstream:** WS-01  
**Owner:** devops-sre

### Dependencies

- BL-0002
- BL-0009

### Outcome

Dashboard shows verified:

- production status
- critical journey status
- running release
- container health
- backup freshness

---

## BL-0011 — Connect Business KPIs to Dashboard

**Priority:** P1  
**State:** BLOCKED  
**Type:** DATA  
**Workstream:** WS-01  
**Owner:** analytics-intelligence

### Dependencies

- BL-0006
- BL-0007
- BL-0008
- BL-0009

### Outcome

Dashboard shows verified business KPIs with freshness/confidence.

---

## BL-0012 — Baseline Entryway Customer Journey

**Priority:** P1  
**State:** WAITING_FOR_DATA  
**Type:** PRODUCT  
**Workstream:** WS-03  
**Owner:** product-manager

### Outcome

Understand current Entryway flow from discovery to useful action.

### Baseline

Measure where available:

- visitors
- desired-function usage
- micro-zone usage
- diagnosis
- quest starts
- quest completions
- standards
- purchases

Do not infer missing events.

---

## BL-0013 — Complete Entryway Desired-Function Experience

**Priority:** P1  
**State:** NEEDS_EVIDENCE  
**Type:** PRODUCT  
**Workstream:** WS-03  
**Owner:** product-manager

### Hypothesis

Helping customers define what they want a micro-zone to do will improve relevance of quests and recommendations.

### Scope

Entryway first.

### Validation

Measure:

- completion
- quest start
- quest completion
- downstream product engagement

---

## BL-0014 — Implement/Validate Root-Cause Diagnosis

**Priority:** P1  
**State:** NEEDS_EVIDENCE  
**Type:** PRODUCT  
**Workstream:** WS-03  
**Owner:** product-manager

### Hypothesis

Root-cause diagnosis will produce better actions than generic organization advice.

### Root Cause Families

Use canonical business taxonomy.

### Validation

Compare downstream quest success and progression.

---

## BL-0015 — Instrument Quest Lifecycle

**Priority:** P1  
**State:** NEEDS_EVIDENCE  
**Type:** DATA  
**Workstream:** WS-03  
**Owner:** analytics-intelligence

### Required Events

- quest impression
- quest start
- quest completion
- duration
- player count where applicable
- standard established
- sustainment follow-up

Actual implementation must follow `DATA-CONTRACTS.md`.

---

## BL-0016 — Establish Entryway Quest Baseline

**Priority:** P1  
**State:** BLOCKED  
**Type:** PRODUCT  
**Workstream:** WS-03  
**Owner:** product-manager

### Dependency

BL-0015

### Outcome

Identify:

- strongest quests
- weak quests
- duration effects
- micro-zone differences
- abandonment points

---

## BL-0017 — Validate First Paid Entryway Offer

**Priority:** P1  
**State:** NEEDS_EVIDENCE  
**Type:** COMMERCE  
**Workstream:** WS-03  
**Owner:** commerce-manager

### Candidate Offers

Evaluate based on evidence:

- digital deck
- printable quest pack
- physical deck
- micro-zone kit
- visual controls

### Outcome

Determine whether customers will pay for meaningful incremental value.

Do not launch a large catalog.

---

## BL-0018 — Establish Search Console Baseline

**Priority:** P2  
**State:** READY  
**Type:** SEO  
**Workstream:** WS-03  
**Owner:** seo-aeo

### Outcome

Identify current:

- clicks
- impressions
- CTR
- positions
- top queries
- top pages
- Entryway opportunities

---

## BL-0019 — Audit Entryway SEO/AEO Architecture

**Priority:** P2  
**State:** BLOCKED  
**Type:** SEO  
**Workstream:** WS-03  
**Owner:** seo-aeo

### Dependency

BL-0018

### Outcome

Ensure Entryway content architecture maps:

Room
→ Micro-Zone
→ Problem
→ Root Cause
→ Quest
→ Standard
→ Product

---

## BL-0020 — Identify Primary Business Constraint

**Priority:** P1  
**State:** BLOCKED  
**Type:** STRATEGY  
**Workstream:** WS-01  
**Owner:** 6s-ceo

### Dependencies

- verified business data
- baseline dashboard

### Outcome

Select one evidence-backed primary constraint.

### Output

Update:

- dashboard
- `STATUS.md`
- backlog ordering

---

# 51. Initial Deferred Opportunities

These should not displace current work without evidence.

## BL-D001 — Expand to Bathroom

State: DEFERRED

## BL-D002 — Expand to Laundry

State: DEFERRED

## BL-D003 — Expand to Home Office

State: DEFERRED

## BL-D004 — Whole-Home Inventory Platform

State: DEFERRED

## BL-D005 — UPC Consumable Replenishment

State: DEFERRED

## BL-D006 — Large 3D-Printed Product Catalog

State: DEFERRED

## BL-D007 — Professional/B2B Platform

State: DEFERRED

## BL-D008 — National Home Services Expansion

State: DEFERRED

These may become high priority later.

---

# 52. Daily Selection Algorithm

At the start of an autonomous work cycle:

1. Check for P0 incidents.
2. Check security/reliability criticals.
3. Check production health.
4. Check data freshness.
5. Read current primary constraint.
6. Review active workstreams.
7. Respect WIP limit.
8. Unblock active high-value work first.
9. Select highest-value READY item.
10. Verify autonomy class.
11. Execute.
12. Validate.
13. Record outcome.

---

# 53. Work Selection Tie-Breakers

If two items appear equally valuable, prefer:

1. lower risk
2. lower effort
3. faster learning
4. more reversible
5. more reusable
6. better customer impact
7. less operational complexity

---

# 54. Do Not Cherry-Pick Easy Work

Claude must not select only easy tasks to maximize completion count.

A difficult P1 constraint item outranks several easy P3 items.

---

# 55. Agent Coordination

One backlog item has one accountable owner.

Other agents may contribute.

Example:

`product-manager`
owns Entryway desired-function experiment.

`analytics-intelligence`
supports instrumentation.

`github-manager`
supports code/release.

`devops-sre`
supports production validation.

Avoid shared ownership without accountability.

---

# 56. Handoff

When an agent needs another agent:

Record:

- requested contribution
- dependency
- expected artifact/result

Do not create endless conversational handoffs.

---

# 57. Backlog and GitHub Issues

GitHub Issues may mirror executable engineering work.

`BACKLOG.md` remains the strategic priority layer unless an integrated system replaces it.

Maintain IDs between systems where practical.

Example:

`BL-0015` ↔ GitHub Issue `#42`

---

# 58. Backlog and Pull Requests

PRs should reference backlog/experiment IDs where relevant.

Example:

`BL-0013 / EXP-0004: Simplify Entryway desired-function flow`

This improves traceability.

---

# 59. Backlog and Releases

Material release notes should identify completed backlog items.

Then dashboard can connect:

**Backlog**
→ **PR**
→ **Commit**
→ **Release**
→ **Metric**

---

# 60. Backlog and Experiments

Experiment backlog items should create entries in `EXPERIMENTS.md`.

Do not duplicate experiment truth in multiple places.

Backlog tracks work.

Experiment registry tracks test design/results.

---

# 61. Backlog and Decisions

If execution requires a durable strategic/architectural decision:

Record it in `DECISIONS.md`.

Backlog item links to decision ID.

---

# 62. Backlog and Learnings

When completed work generates durable knowledge:

Record it in `LEARNINGS.md`.

Do not overload backlog history with all learning.

---

# 63. Backlog and STATUS.md

`STATUS.md` should summarize:

- current workstreams
- top active items
- blockers
- primary constraint
- material recent outcomes

Do not copy the entire backlog into status.

---

# 64. Backlog and Dashboard

Dashboard should display:

- active workstreams
- active P0/P1
- blockers
- next highest-value work
- completed material changes
- pending approvals

It should not expose every P4 idea by default.

---

# 65. Autonomous Improvement Loop

The full operating loop is:

**Observe**
→ dashboard/data

**Diagnose**
→ identify constraint/root cause

**Prioritize**
→ backlog

**Hypothesize**
→ experiment/change

**Execute**
→ agents/GitHub/VPS

**Verify**
→ production

**Measure**
→ canonical metrics

**Learn**
→ learnings

**Standardize**
→ code/docs/process

**Repeat**

This is the core autonomous continuous-improvement system.

---

# 66. Anti-Patterns

Do not allow:

## Backlog Inflation

Thousands of speculative tasks.

## Roadmap Theater

Large future plans disconnected from evidence.

## Agent Busywork

Tasks created to keep agents active.

## Metric Gaming

Work selected because it makes dashboards look good.

## Expansion Addiction

New rooms/products before Entryway learning.

## Infrastructure Hobbyism

Rebuilding systems without a customer/business reason.

## Content Factory Behavior

Publishing volume without useful outcomes.

## Approval Dumping

Sending routine decisions to the owner.

---

# 67. Owner Override

The owner may:

- reprioritize
- pause
- reject
- approve
- create strategic work

When this happens:

- preserve the instruction
- update priority/state
- identify displaced work
- maintain safety constraints

Do not silently undo owner priorities.

---

# 68. Autonomous Reprioritization

Claude may reprioritize without owner approval when:

- live evidence changes
- incident occurs
- blocker appears
- experiment concludes
- primary constraint changes
- risk changes

Subject to `AUTONOMY.md`.

Material reprioritization should be visible in the dashboard/status.

---

# 69. Backlog History

Preserve meaningful history through Git and/or structured work records.

Do not erase rejected/failed strategic items merely to make the backlog look cleaner.

Archive when appropriate.

---

# 70. Success Measure for the Backlog

The backlog is working when:

- WIP remains controlled
- high-value work finishes
- blockers are visible
- data gaps are resolved
- experiments produce learning
- production remains safe
- Entryway becomes validated
- revenue constraints become clearer
- agents do not create uncontrolled work
- the owner rarely needs to manually assign routine tasks

---

# 71. Next Recommended Operating Files

After `BACKLOG.md`, prioritize:

1. `EXPERIMENTS.md`
2. `DECISIONS.md`
3. `LEARNINGS.md`
4. `DATA-CONTRACTS.md`
5. `RUNBOOK.md`
6. `INCIDENTS.md`
7. `PRODUCT-CATALOG.md`
8. `CONTENT-CATALOG.md`
9. `SECURITY.md`
10. `RELEASES.md`

The exact sequence may change if discovery reveals a more urgent gap.

---

# Final Rule

Claude should never ask:

**"What can I build next?"**

The better question is:

**"What is currently preventing 6S Success from creating more customer value and sustainable business value, and what is the smallest safe action that will teach us or improve it?"**

The backlog exists to make that answer executable.

**Evidence determines priority.**

**Strategy determines direction.**

**WIP limits protect focus.**

**Autonomy enables execution.**

**Metrics determine outcome.**

**Learning determines what happens next.**
