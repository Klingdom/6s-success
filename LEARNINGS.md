# 6S Success Organizational Learnings

> Canonical evidence-backed learning memory for the autonomous 6S Success organization.

## 1. Purpose

`LEARNINGS.md` preserves what 6S Success has actually learned so Claude Code and specialist agents become smarter over time instead of repeatedly rediscovering the same facts.

It records durable evidence about customers, desired functions, rooms, micro-zones, root causes, quests, sustainment, products, pricing, content, SEO/AEO, conversion, GitHub, Hostinger VPS/Docker, reliability, data quality, and autonomous-agent performance.

Read with `CLAUDE.md`, `AUTONOMY.md`, `STATUS.md`, `BUSINESS.md`, `STRATEGY.md`, `METRICS.md`, `DATA-SOURCES.md`, `DASHBOARD.md`, `BACKLOG.md`, `EXPERIMENTS.md`, and `DECISIONS.md`.

## 2. Core Principle

**A learning is an evidence-backed observation, not an opinion.**

Operating loop:

**Observation → Evidence → Learning → Decision or New Hypothesis → Action → More Evidence**

## 3. What Counts as a Learning

A learning should be useful beyond one task, supported by evidence, scoped to the context actually observed, reusable by future agents, and capable of affecting a future decision.

Examples include:

- Entryway users completing desired-function discovery are more likely to begin a recommended quest.
- Shoe storage friction is disproportionately associated with capacity mismatch in tested households.
- A landing page receives high search impressions but weak qualified activation.
- A bundle increases AOV but reduces contribution.
- Production deployment metadata does not reliably identify the running Git commit.
- Backup jobs succeed, but no representative restore has been validated.

## 4. What Is Not a Validated Learning

Do not store agent opinion, brainstorming, generic best practice, unverified assumptions, isolated anecdotes, targets, strategies, tasks, decisions, or raw metric fluctuations as validated learnings.

These may instead become hypotheses or backlog items.

## 5. Learning IDs

Use stable IDs: `LRN-0001`, `LRN-0002`, etc. Never recycle IDs.

Reference them from decisions, experiments, backlog items, product requirements, content planning, and dashboard recommendations.

## 6. Learning Status

Use:

- `HYPOTHESIS`: plausible but not sufficiently evidenced
- `EMERGING`: some evidence exists
- `SUPPORTED`: adequate evidence for bounded operational use
- `STRONG`: repeated/high-quality evidence within defined scope
- `CONTRADICTED`: material conflicting evidence exists
- `SUPERSEDED`: newer learning better represents understanding
- `STALE`: context changed enough to require revalidation

## 7. Confidence

Use `HIGH`, `MEDIUM`, `LOW`, or `UNKNOWN`.

Confidence considers sample size, source quality, experimental quality, consistency, recency, confounding, directness, and replication.

## 8. Canonical Learning Record

```yaml
id: LRN-0001
title: Concise learning
status: EMERGING
confidence: MEDIUM
domain: PRODUCT
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: product-manager

statement: >
  The evidence-backed learning stated precisely.

scope:
  population: ...
  room: ...
  micro_zone: ...
  channel: ...
  period: ...

evidence:
  - type: EXPERIMENT
    reference: EXP-0000
    observation: ...

limitations:
  - ...

implications:
  - ...

related:
  decisions: []
  experiments: []
  backlog: []

revalidation_trigger: >
  What would require this learning to be tested again?

supersedes: null
superseded_by: null
```

Use `UNKNOWN` rather than inventing facts.

## 9. Scope Discipline

Never generalize farther than evidence permits.

Bad: **Families prefer 15-minute quests.**

Better: **Among first-time Entryway users in the tested cohort, 15-minute quest framing produced higher completion than 30-minute framing.**

## 10. Evidence Hierarchy

Stronger evidence may include randomized experiments, repeated behavioral evidence, verified transactions, validated product telemetry, representative usability testing, and verified production telemetry.

Moderate evidence may include cohort analysis, Search Console patterns, structured customer feedback, support patterns, and before/after analysis with known caveats.

Weaker evidence includes single anecdotes, agent intuition, generic web advice, competitor behavior, and synthetic evaluation.

Weak evidence can generate hypotheses but should rarely create `STRONG` learnings.

## 11. Converging Evidence

Prefer multiple independent evidence sources.

A micro-zone problem appearing in desired-function responses, quest abandonment, customer feedback, product searches, and repeat diagnoses is more credible than one signal alone.

## 12. Contradictory Evidence

Never hide contradictions. Record conflicting evidence, source quality, possible segment differences, and whether confidence should change.

Contradiction may reveal segmentation rather than invalidate the entire learning.

## 13. Negative Knowledge

Preserve what does not work.

Examples:

- a quest mechanic reduced completion
- a bundle reduced contribution
- a page rewrite reduced qualified activation
- a deployment method created runtime drift
- an automation produced noisy alerts

Negative knowledge prevents repeated waste.

## 14. Learning vs Decision

Learning: **Users in the tested Entryway cohort completed more quests after selecting a desired function.**

Decision: **Desired-function selection will remain in the default Entryway flow.**

Evidence informs decisions, but the artifacts remain separate.

## 15. Learning vs Experiment

`EXPERIMENTS.md` stores hypothesis, design, results, and experiment disposition.

`LEARNINGS.md` stores durable reusable knowledge produced by experiments and other evidence.

Not every experiment needs a durable learning.

## 16. Learning vs Metric

Metric: `Quest completion rate = 41%`

Learning: **Quest completion is materially lower for quests requiring multiple storage relocation steps in the observed cohort.**

Metrics are observations. Learnings are evidence-backed interpretations.

## 17. Learning Domains

Use one primary domain:

`CUSTOMER`, `VALUES`, `DESIRED_FUNCTION`, `ROOM`, `MICRO_ZONE`, `ROOT_CAUSE`, `QUEST`, `SUSTAINMENT`, `MULTIPLAYER`, `PRODUCT`, `COMMERCE`, `PRICING`, `CONTENT`, `SEO`, `AEO`, `ACQUISITION`, `CONVERSION`, `RETENTION`, `DATA`, `GITHUB`, `DEVOPS`, `VPS`, `DOCKER`, `RELIABILITY`, `SECURITY`, `AUTONOMY`, or `OPERATIONS`.

## 18. Customer Learning Model

Customer learning should increasingly answer:

**Who? → What do they want the area to do? → What prevents that? → What intervention works? → What persists? → What are they willing to pay for?**

## 19. Values and Desired Functions

Learn which expressed values influence room outcomes, such as speed, calm, independence, hospitality, safety, simplicity, preparedness, accessibility, family participation, and visual order.

Do not infer sensitive personal attributes.

For each room and micro-zone, learn common desired functions, conflicting functions, household differences, effective discovery questions, and which desired functions predict useful quests or products.

## 20. Root-Cause Learning

Build evidence around root-cause families such as:

- excess
- no home
- wrong home
- poor access
- poor visibility
- excess steps
- unclear ownership
- capacity mismatch
- no standard
- replenishment failure
- cleaning friction
- safety risk

Track which causes are frequent, persistent, expensive, easy to solve, product-assisted, and likely to recur.

## 21. Micro-Zone Learning

For each micro-zone, learn primary functions, common items, common friction, root causes, successful quests, useful standards, sustainment failure modes, relevant products, and seasonal variation.

This should eventually power increasingly precise recommendations.

## 22. Quest Learning

Track completion, duration, difficulty, abandonment, player count, voluntary versus assigned cards, random versus configured selection, root-cause match, sustained outcome, and progression.

Never optimize completion by making quests meaningless.

## 23. Sustainment Learning

Learn what causes improvements to persist, including visual controls, labels, assigned homes, ownership, capacity limits, reset routines, replenishment cues, follow-up timing, and physical product support.

Sustainment is strategically more important than one-time cleanup.

## 24. Multiplayer Learning

Learn optimal team size, role clarity, card selection behavior, conflict points, participation, completion, child-friendly mechanics, and adult coordination.

Do not design mechanics that pressure or shame household members.

## 25. Product and Pricing Learning

For products, learn the problem solved, root causes addressed, micro-zones served, purchase intent, conversion, returns/refunds, usage where measurable, quest impact, and sustainment impact.

For pricing, learn willingness to pay, conversion, AOV, contribution, refunds, bundle response, and meaningful segment differences.

A high-selling product that does not improve the intended outcome requires investigation.

## 26. Content, SEO, and AEO Learning

Learn which content attracts qualified visitors, answers real questions, activates quests, assists purchases, and creates progression.

SEO learning should connect queries, intent, landing pages, CTR, ranking, qualified engagement, activation, and conversion.

AEO learning must use observable evidence such as referrals, citations/mentions where measurable, crawler accessibility, and question coverage. Never fabricate visibility.

## 27. Funnel and Revenue Learning

Learn where and why users stop in the journey.

Revenue learning should identify which levers matter: qualified traffic, activation, product exposure, conversion, AOV, repeat purchase, margin, and customer outcome.

The $20K/month target should become increasingly decomposed into evidence-backed levers.

## 28. Technical and Operational Learning

Preserve reusable findings about:

- GitHub release processes and CI failure patterns
- rollback effectiveness and traceability
- VPS/Docker runtime architecture and drift
- persistent-data locations and dependencies
- incident root causes
- recovery effectiveness
- instrumentation and reconciliation problems
- bot/test contamination
- autonomous-agent handoff or alert failures

Never store secrets.

## 29. Learning Promotion and Demotion

A learning may progress:

`HYPOTHESIS → EMERGING → SUPPORTED → STRONG`

or regress when evidence weakens it:

`STRONG → SUPPORTED → EMERGING → CONTRADICTED`

Promotion requires evidence, not age.

## 30. Revalidation

Revalidate when customer segments, products, room taxonomy, pricing, acquisition channels, UX, instrumentation, market context, or technical architecture materially change.

Different learnings have different half-lives. Search rankings and conversion benchmarks age faster than stable physical room relationships.

## 31. Learning Index

Maintain:

| ID | Learning | Domain | Status | Confidence |
|---|---|---|---|---|

Only evidence-backed learnings should appear as `SUPPORTED` or `STRONG`.

## 32. Initial Hypothesis Register

Do not pretend strategic beliefs are validated learnings.

### LRN-0001: Desired Function May Improve Recommendation Relevance

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** DESIRED_FUNCTION

Allowing users to define what they want a room or micro-zone to accomplish may improve quest and product recommendation relevance.

Evidence needed: desired-function completion, recommendation interaction, quest start, quest completion, and progression.

Related: `DEC-0002`, `EXP-0001`, `EXP-0002`.

### LRN-0002: Root-Cause Matching May Improve Quest Outcomes

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** ROOT_CAUSE

Matching quests to diagnosed root causes may produce better outcomes than generic room-level recommendations.

Evidence needed: credible matched-versus-generic comparison.

Related: `DEC-0003`, `EXP-0004`.

### LRN-0003: Short Quests May Reduce Initial Participation Friction

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** QUEST

A clearly bounded 15-minute quest may increase first-time completion relative to longer initial commitments.

Evidence needed: starts, completion, quality, and progression by duration.

Related: `DEC-0005`, `EXP-0003`.

### LRN-0004: Cooperative Card Choice May Improve Group Engagement

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** MULTIPLAYER

Allowing participants to voluntarily claim cards may improve group engagement compared with fully assigned tasks.

Evidence needed: participation distribution, completion, abandonment, and feedback.

Related: `EXP-0008`.

### LRN-0005: Sustainment Requires More Than Initial Organization

**Status:** HYPOTHESIS  
**Confidence:** MEDIUM  
**Domain:** SUSTAINMENT

One-time organization is unlikely to be sufficient for durable micro-zone performance without some combination of standards, visual controls, ownership, capacity limits, or reset behavior.

Evidence needed: longitudinal micro-zone outcome data.

Related: `DEC-0004`, `EXP-0009`.

## 33. Verified Learning Registers

### Verified Technical Learnings

`NONE VERIFIED IN THIS FILE`

### Verified Customer Learnings

`NONE VERIFIED IN THIS FILE`

### Verified Commerce Learnings

`NONE VERIFIED IN THIS FILE`

### Verified SEO/AEO Learnings

`NONE VERIFIED IN THIS FILE`

Claude should treat empty verified registers as a reason to gather evidence, not fabricate it.

## 34. Learning Creation Process

When evidence produces a potentially durable finding:

1. Search existing learnings.
2. Determine whether it updates an existing learning.
3. Inspect source quality.
4. Define scope.
5. Document limitations.
6. Assign confidence.
7. Record implications.
8. Link experiments, metrics, and sources.
9. Determine whether a decision or backlog change follows.

## 35. Contradiction Process

When evidence contradicts a learning:

1. Preserve old evidence.
2. Add contradictory evidence.
3. Assess segment/context differences.
4. Lower confidence if warranted.
5. Mark `CONTRADICTED` when necessary.
6. Create a replacement learning if understanding changed.
7. Revisit related decisions.

## 36. From Learning to Action

A learning may produce:

- a durable decision in `DECISIONS.md`
- a new item in `BACKLOG.md`
- a new experiment in `EXPERIMENTS.md`
- updated content
- a new or changed product
- improved personalization
- a technical standard

Do not automatically turn every learning into work.

## 37. Learning Dashboard

The executive dashboard may surface:

**New This Week**: newly supported learning.

**Challenged**: existing learning weakened by evidence.

**Highest-Value Unknown**: the uncertainty most worth resolving next.

**Applied Learning**: knowledge that changed a product, experiment, or decision.

Do not overwhelm the owner with the full registry.

## 38. Weekly Learning Review

Ask:

1. What did we learn?
2. What evidence became stronger?
3. What was contradicted?
4. What remains uncertain?
5. What should change?
6. What should we stop doing?

## 39. Strategic Learning Gates

Phase progression should depend on knowledge, not feature delivery.

Before broad Entryway expansion, seek credible answers to:

- What do users want the Entryway to do?
- Which micro-zones matter most?
- What root causes recur?
- Which quests create useful completion?
- Which improvements sustain?
- Do users progress to another micro-zone?
- Will customers pay for incremental value?

## 40. Privacy and Security

Never store passwords, API keys, tokens, private household images, unnecessary PII, or sensitive customer attributes.

Use aggregate or sanitized evidence.

## 41. Learning Integrity

Agents must never fabricate evidence, inflate confidence, hide contradictory results, generalize beyond scope, convert targets into learnings, rewrite history to support current strategy, or claim causality from simple correlation without qualification.

## 42. Learning Quality Test

Before promoting a learning, ask:

**What evidence supports this?**

**What population does it apply to?**

**What are the limitations?**

**Could another explanation produce the observation?**

**Would this change a future decision?**

If these cannot be answered, keep it a hypothesis or observation.

## 43. Relationship to the Autonomous System

The complete loop is:

**DATA-SOURCES → METRICS → DASHBOARD → BACKLOG → EXPERIMENTS → LEARNINGS → DECISIONS → GitHub/VPS/Docker Execution → STATUS → Repeat**

## 44. Knowledge Flywheel

The long-term competitive advantage should become:

**More households use 6S Success**
→ **More useful outcome data**
→ **Better understanding of desired functions and root causes**
→ **Better quests**
→ **Better standards**
→ **Better product recommendations**
→ **Better customer outcomes**
→ **More trust and adoption**
→ **More learning**

This flywheel must respect privacy and customer control.

## 45. Highest-Value Learning Goal

The system should ultimately understand:

> For a household with a particular desired function, in a particular room and micro-zone, experiencing a particular type of friction, what is the smallest intervention most likely to create a sustained improvement?

That is more strategically valuable than simply knowing which page receives the most clicks.

## 46. Final Rule

Claude should not merely remember what it **did**.

It must remember what the organization **learned**.

Every meaningful cycle should leave the system with one of three outcomes:

1. We have stronger evidence for something.
2. We discovered that something we believed was wrong or incomplete.
3. We reduced an important uncertainty.

If autonomous work repeatedly produces code and content without producing better knowledge or better customer outcomes, the system is not continuously improving.

`LEARNINGS.md` is the memory that turns repeated execution into compounding intelligence.
