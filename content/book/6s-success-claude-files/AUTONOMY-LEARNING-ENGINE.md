# 6S Success Autonomy Learning Engine

> Canonical organizational-learning standard for converting verified
> outcomes, experiments, customer behavior, owner decisions, agent
> performance, incidents, and operating experience into durable, scoped,
> testable knowledge that improves the 6S Success autonomous
> organization over time.

## 1. Purpose

`AUTONOMY-LEARNING-ENGINE.md` defines how Claude learns from what
actually happens.

``` text
ACTION / EXPERIMENT / DECISION
          ↓
       OUTCOME
          ↓
   VERIFY EVIDENCE
          ↓
COMPARE EXPECTED vs ACTUAL
          ↓
      EXTRACT LESSON
          ↓
   DEFINE SCOPE + CONFIDENCE
          ↓
  VALIDATE / CHALLENGE
          ↓
STANDARDIZE, RETEST, OR REJECT
          ↓
 UPDATE REUSABLE KNOWLEDGE
          ↓
 CHANGE FUTURE DECISIONS
          ↓
     MEASURE AGAIN
```

It closes the loop:

``` text
Opportunity Engine
→ Decision Engine
→ Orchestrator
→ Mission
→ Execution
→ Measurement
→ Learning Engine
→ Better Opportunity / Decision / Execution
```

## 2. Core Principle

**Do not learn from activity. Learn from verified differences between
expectation and reality.**

A completed task is not automatically a lesson. A customer comment is
not automatically a rule. A successful experiment is not automatically
universal. A failed experiment is not automatically a bad idea
everywhere.

## 3. Why This Exists

Without disciplined learning, an autonomous system can repeat failures,
forget successful patterns, overfit to one customer, generalize from
tiny samples, turn owner corrections into unintended global policy,
preserve obsolete assumptions, make prompts longer without making
decisions better, copy Entryway solutions blindly into other rooms,
reward agents for activity rather than outcomes, and repeatedly
rediscover the same insight.

The Learning Engine creates controlled organizational memory.

## 4. Relationship to Other Standards

The Learning Engine consumes outcomes from and feeds improvements back
into:

-   `AUTONOMY-OPPORTUNITY-ENGINE.md`
-   `AUTONOMY-DECISION-ENGINE.md`
-   `AUTONOMY-ORCHESTRATION.md`
-   `AUTONOMY-SCHEDULER.md`
-   `AUTONOMY-API.md`
-   Mission Control
-   Executive Dashboard
-   analytics/measurement
-   experimentation
-   agent evaluation
-   GitHub/release management
-   VPS/Docker operations
-   security and incident management
-   room/micro-zone taxonomy
-   quest/card system
-   product/service recommendation logic

Discover canonical repository filenames before adding duplicate systems.

## 5. Learning Sources

### Customer

Desired-function selections, diagnosis outcomes, micro-zone
observations, quest starts/completions, card behavior, outcome
verification, sustain results, product recommendation
acceptance/rejection, and feedback.

### Experiments

Hypotheses, exposure, primary metrics, guardrails, outcomes, and
adoption/rejection decisions.

### Missions

Expected outcome, actual outcome, time/cost, blockers, and verification
results.

### Decisions

Prediction, confidence, selected option, actual result, owner override,
and reversal.

### Technical Operations

Incidents, deployments, rollbacks, recurring failures, recovery,
performance, and security findings.

### Agents

Task success, evaluation, routing, escalation, tool use, cost, and owner
correction.

### Owner

Directives, approvals, rejections, corrections, and strategic changes.

## 6. Learning Types

``` text
CUSTOMER_BEHAVIOR
DESIRED_FUNCTION
ROOT_CAUSE
6S_PATTERN
MICRO_ZONE
ROOM
QUEST
CARD
PRODUCT
SERVICE
CONTENT
SEO_AEO
GROWTH
MEASUREMENT
TECHNICAL
RELIABILITY
SECURITY
AGENT
ORCHESTRATION
DECISION
BUSINESS
```

## 7. Learning Record

``` yaml
learning:
  id:
  type:
  statement:
  source_refs:
  evidence_refs:
  scope:
  applicability:
  confidence:
  status:
  expected_effect:
  observed_effect:
  created_at:
  last_validated_at:
  expires_or_review_at:
  standardized_into:
  supersedes:
  contradicted_by:
```

## 8. Learning Status

``` text
CANDIDATE
SUPPORTED
VALIDATED
STANDARDIZED
CONTESTED
SUPERSEDED
REJECTED
STALE
```

## 9. Candidate Learning

A candidate learning is a plausible lesson that has not earned broad
reuse.

Example:

> Entryway users appear more willing to begin when the first quest is
> framed as a 15-minute quick win.

Do not immediately encode this as a global rule.

## 10. Validated Learning

A learning becomes validated only when evidence is strong enough for its
stated scope.

``` text
Validated for:
Entryway starter quests among measured qualified users.

Not yet validated for:
Kitchen, Garage, Laundry, all users.
```

## 11. Standardized Learning

Standardization means a validated lesson has deliberately been
incorporated into a reusable system such as a card template, quest
assembly rule, UI component, root-cause mapping, agent instruction,
test, code/configuration, operating procedure, or content standard.

## 12. Evidence Before Memory

Durable learning must link to evidence.

Avoid:

``` text
"We learned users prefer short quests."
```

Prefer:

``` text
"Within the measured Entryway cohort, presenting a 15-minute starter option
increased quest starts without degrading completion or reported usefulness."
```

## 13. Facts, Interpretations, and Rules

Separate:

``` text
FACT
INTERPRETATION
RULE
```

Example:

``` text
FACT:
Quest starts increased in experiment.

INTERPRETATION:
Lower perceived commitment likely contributed.

RULE:
Use a short starter option for this validated context.
```

## 14. Scope

Every learning should specify applicability across relevant dimensions:
customer segment, room, micro-zone, desired function, root cause, 6S
dimension, card type, quest duration, platform, technical component,
agent, and environment.

## 15. Do Not Overgeneralize

One successful Entryway key-storage pattern does not prove that all
micro-zones should use hooks.

A valid broader lesson may instead be:

``` text
High-frequency items benefit from low-friction point-of-use homes.
```

The physical solution remains contextual.

## 16. Confidence

Use `HIGH`, `MEDIUM`, or `LOW`.

Confidence should reflect sample size, replication, measurement quality,
directness, consistency, experiment quality, confounding, source
authority, and recency.

## 17. Learning Promotion

``` text
CANDIDATE
→ SUPPORTED
→ VALIDATED
→ STANDARDIZED
```

Promotion requires evidence. Do not promote because an agent repeats the
same claim.

## 18. Contradiction

New evidence may contradict a learning. Do not hide it.

``` yaml
status: CONTESTED
contradicted_by:
  - evidence_ref
```

Route material contradictions for review.

## 19. Supersession

When a newer learning replaces an older one:

``` text
OLD → SUPERSEDED
NEW → VALIDATED/STANDARDIZED
```

Preserve history and reason.

## 20. Staleness

Learnings can become stale as product, audience, UI, room content,
technology, infrastructure, or business strategy changes. Important
learnings require review triggers.

## 21. Learning from Experiments

Compare hypothesis, expected effect, actual effect, guardrails,
unexpected effects, decision, and scope.

A positive experiment should explain what mechanism likely mattered, for
whom, under what conditions, effect size, what should change, and what
remains uncertain.

A negative experiment may mean the hypothesis was wrong, implementation
was weak, segment was mismatched, metric was wrong, or exposure was
insufficient.

An inconclusive experiment remains inconclusive.

## 22. Learning from Decisions

Compare:

``` text
Decision
Confidence
Expected outcome
Actual outcome
Decision-process quality
```

Keep process quality separate from outcome quality:

``` text
GOOD PROCESS + BAD LUCK
BAD PROCESS + GOOD LUCK
GOOD PROCESS + GOOD OUTCOME
BAD PROCESS + BAD OUTCOME
```

## 23. Forecast Learning

Track predicted versus actual quest duration, conversion lift, revenue
effect, infrastructure cost, delivery time, incident probability, and
agent task duration.

Use errors to improve future estimates.

## 24. Confidence Calibration

Check whether high-confidence predictions outperform medium-confidence
predictions. If not, confidence labels need recalibration.

## 25. Learning from Owner Overrides

An owner override is a signal. Investigate missing directives, bad
assumptions, wrong risk tolerance, weak evidence, excessive autonomy, or
unavailable strategic context.

Do not automatically encode every override as a permanent rule.

Repeated similar overrides may justify directive clarification,
decision-threshold changes, agent instruction updates, new approval
rules, or better dashboard context.

## 26. Learning from Customer Feedback and Behavior

Customer feedback can generate candidate learning. Require corroboration
before broad standardization unless individually critical.

Behavior often provides stronger evidence than stated preference for
interaction design. Use both, and do not assume behavior reveals all
motives.

## 27. Learning from Uploaded Images

Aggregate visual observations may reveal common storage patterns, access
problems, clutter types, cleaning friction, possible safety patterns,
and micro-zone variations.

Model uncertainty must remain visible.

Do not create durable personal-profile learning from unnecessary
household details. Prefer aggregate, product-relevant patterns.

## 28. Desired Function Learning

Track which desired functions appear by room/micro-zone and which
interventions best support them.

Example:

``` text
Entryway:
"Fast family launch" may prioritize visible ready-to-go zones differently from
"Calm minimal arrival."
```

Do not assume one organization standard for everyone.

## 29. Root-Cause Learning

Learn which observed states correlate with root causes and which
countermeasures work.

``` text
Observed:
keys migrate across horizontal surfaces

Likely cause:
no low-friction point-of-use home

Effective countermeasure:
defined landing point + visual standard
```

Scope and confidence remain explicit.

## 30. 6S Learning

Capture reusable patterns across:

``` text
SORT
SET IN ORDER
SHINE
STANDARDIZE
SUSTAIN
SAFETY
```

Potential learning includes decision-fatigue reduction, point-of-use
placement, cleaning sequences, visual controls, min/max, reset triggers,
ownership, and safety-specific controls.

Safety learnings require stronger evidence and careful scope.

## 31. Card Learning

Track:

``` text
selection
start
completion
abandonment
duration
outcome contribution
repeat use
sustain association
group participation
```

Compare estimated and actual duration by relevant context. Update
estimates only with sufficient evidence.

A card may be difficult because it is too broad, unclear, missing
prerequisites/supplies, decision-heavy, physically demanding, or
coordination-heavy. Learn the cause, not merely the abandonment rate.

When a card is retired, preserve why.

## 32. Quest Learning

Learn best starting patterns, sequencing, dependency rules, timebox fit,
early wins, verification placement, sustain steps, and group assignment.

Dynamic quest assembly should improve using:

``` text
available time
desired function
root cause
micro-zone state
player count
supplies
dependencies
safety
```

Do not optimize solely for card completion.

## 33. Group Quest Learning

Track idle time, task collisions, workload imbalance, collaboration,
verification bottlenecks, completion, enjoyment where measured, and
outcome quality.

## 34. Product Learning

Track whether a recommended product addressed a diagnosed need, was
accepted, was used, improved outcome, created maintenance burden, or was
unnecessary.

If users achieve the desired function using existing household items,
learn that too. The system should improve at avoiding unnecessary
purchases.

## 35. Service Learning

For Shine/organization/service offerings, learn demand, completion,
repeat rate, outcome, labor, margin, upsell usefulness, and customer
satisfaction.

Do not optimize upsell rate independently of customer value.

## 36. Content and SEO/AEO Learning

Track whether content answers a real question and contributes to
qualified engagement, desired-function progression, quest progression,
and customer outcome.

Pageviews alone are insufficient.

Learn which search/answer opportunities produce useful customer
journeys. Do not learn `more pages = better` without evidence.

## 37. Technical Learning

Capture recurring failure modes, deployment issues, test gaps,
configuration problems, capacity limits, recovery methods, observability
gaps, and security findings.

After material incidents ask:

``` text
What happened?
Why?
Why was it not prevented?
Why was it not detected sooner?
What reduced impact?
What should change?
```

Focus on system improvement, not blame.

## 38. GitHub and VPS/Docker Learning

GitHub learning may include components associated with failures,
recurring CI problems, PR/release bottlenecks, missing tests, and
dependency issues.

VPS/Docker learning may include resource trends, restart causes,
deployment failure modes, backup/recovery performance, capacity
thresholds, and safe cleanup patterns.

Do not convert one transient spike into permanent infrastructure policy.

## 39. Agent Learning

Track agent performance by task class:

``` text
success
verification failures
reroutes
owner overrides
cost
latency
tool errors
policy issues
```

Use evidence to improve specialization and routing.

Prompt/instruction changes should address recurring observed defects. Do
not continuously rewrite prompts because one output was imperfect.

Trust may increase or decrease only through governance. Agents cannot
promote themselves.

## 40. Orchestration, Opportunity, Decision, and Scheduler Learning

Evaluate:

### Orchestration

Constraint selection, mission selection, WIP, routing, dependencies,
escalation, verified outcomes.

### Opportunity Engine

Whether high-ranked opportunities actually produce more value.

### Decision Engine

Recommendation accuracy, confidence calibration, risk prediction, owner
override, reversals, expected vs actual value.

### Scheduler

Useful findings, false positives, NO_ACTION rate, cost, missed issues,
duplicate work.

A high NO_ACTION rate can be healthy for cheap monitoring.

## 41. Cost and Tool Learning

Track cost per useful finding, verified improvement, mission, agent,
decision, and experiment.

Compare deterministic code, analytics queries, smaller models, larger
models, specialist agents, and owner decisions.

Prefer the least costly method that reliably meets the requirement.

## 42. Reusable Pattern Record

``` yaml
pattern:
  id:
  name:
  problem_class:
  context:
  intervention:
  evidence_refs:
  confidence:
  applicable_to:
  exclusions:
  verification:
```

Potential libraries include desired-function patterns, root-cause
patterns, 6S countermeasures, micro-zone patterns, card structures,
quest sequences, product-need mappings, sustain mechanisms, UI patterns,
deployment/recovery patterns, and agent-routing patterns.

## 43. Standardization Hierarchy

Prefer standardizing at the lowest reusable level:

``` text
Global rule
  ↓ only if truly universal
Room-family pattern
  ↓
Room pattern
  ↓
Micro-zone pattern
  ↓
Individual exception
```

A standard must permit justified exceptions for safety, desired
function, accessibility, or physical constraints.

## 44. Learning Propagation

Before propagating ask:

``` text
Is the mechanism transferable?
Is context comparable?
Are risks comparable?
Is measurement ready?
```

Example:

``` text
Validated:
visible point-of-use homes reduce retrieval friction in Entryway.

Candidate transfer:
Office charging accessories.

Not automatic:
Medication storage, due to safety constraints.
```

## 45. Learning Storage Layers

Conceptually separate:

``` text
RAW EVIDENCE
OBSERVATIONS
LEARNINGS
STANDARDIZED PATTERNS
ACTIVE RULES
```

Do not collapse them into one unstructured memory file.

## 46. Learning Retrieval

Agents should retrieve relevant learnings based on task, room,
micro-zone, desired function, root cause, 6S dimension, decision class,
technical component, and agent role.

Avoid injecting the entire learning corpus into every prompt.

## 47. Learning Precedence

Conceptual precedence:

``` text
Owner Directive
Governance / Security Policy
Canonical Current Standard
Validated Learning
Supported Learning
Candidate Learning
Raw Observation
```

Lower layers cannot override higher authority.

## 48. Learning-to-Standard Change

A validated learning should not automatically rewrite protected
instructions.

Use:

``` text
Learning
→ Proposed Standard Change
→ Review/Test
→ Approval if required
→ Versioned Update
→ Verification
```

Important standards and patterns should be versioned with effective
date, reason, evidence, and superseded version.

## 49. Rollback and Decay

If a standardized learning causes regression, revert where safe and
investigate.

Important learnings should have revalidation logic based on elapsed
time, product/environment changes, contradictory evidence, and poor
recent outcomes.

## 50. Forgotten Learning Prevention

Before creating a new solution, search for prior similar opportunities,
experiments, rejected ideas, patterns, incidents, and owner decisions.

This prevents rediscovery.

## 51. Bad Learning Prevention

Do not learn global rules from:

-   one anecdote
-   one low-confidence image
-   one unusual household
-   one failed agent response
-   one traffic spike
-   one deployment
-   one owner correction without context

Guard against survivorship bias, selection bias, metric gaming, causal
overclaiming, seasonality, and misleading global averages.

## 52. Accessibility and Personalization

Capture patterns that reduce physical or cognitive effort where
measured.

Personalization should use relevant preferences such as desired function
and available time.

Avoid unnecessary sensitive inference.

## 53. Learning Events

``` text
learning.candidate_created
learning.supported
learning.validated
learning.standardized
learning.contested
learning.superseded
learning.rejected
learning.stale
pattern.created
pattern.updated
```

## 54. API

Align with `AUTONOMY-API.md`.

Potential:

``` text
GET  /api/v1/learnings
GET  /api/v1/learnings/{id}
POST /api/v1/learnings
POST /api/v1/learnings/{id}/validate
POST /api/v1/learnings/{id}/contest
POST /api/v1/learnings/{id}/standardize
POST /api/v1/learnings/{id}/supersede
GET  /api/v1/patterns
GET  /api/v1/patterns/{id}
```

## 55. Executive Dashboard and Mission Control

Executive Dashboard should show only strategically useful learning:

``` text
WHAT WE LEARNED
Evidence
Confidence
Where it applies
What changed because of it
Expected/verified impact
```

Mission Control may show mission learnings, experiment learnings,
pending validation, contested learnings, standards changed, and agent
remediation.

## 56. Learning Metrics

Track:

``` text
candidate_learnings
validated_learnings
standardized_learnings
contested_learnings
superseded_learnings
time_to_validation
learning_reuse_rate
learning_reversal_rate
repeat_failures_prevented
decision_accuracy_improvement
estimate_accuracy_improvement
quest_outcome_improvement
agent_quality_improvement
cost_reduction
time_to_evidence_reduction
```

Do not optimize learning count. Optimize useful learning that changes
future behavior and improves outcomes.

## 57. Scheduler Integration

Suggested starting cadence:

``` text
EVENT-DRIVEN
Experiment completion, incident resolution, owner override, major mission outcome

DAILY
Lightweight outcome capture

WEEKLY
Learning synthesis and pattern review

MONTHLY
Staleness, contradiction, cross-room patterns, agent calibration
```

A weekly review asks:

``` text
What did we expect?
What actually happened?
What surprised us?
What should we repeat?
What should we stop?
What needs more evidence?
What standard should change?
```

## 58. Executive Learning Brief

Keep concise:

``` text
Top 3 things learned
What changed
Verified impact
What remains uncertain
What decision this enables next
```

## 59. Bootstrap Discovery

Before implementation inspect:

1.  current database/data model;
2.  event system;
3.  experiment records;
4.  mission/task outcomes;
5.  decision records;
6.  owner directives/overrides;
7.  analytics;
8.  room/micro-zone taxonomy;
9.  desired-function model;
10. root-cause taxonomy;
11. quest/card data;
12. product/service outcomes;
13. GitHub/deployment history;
14. incidents;
15. agent evaluations;
16. existing knowledge/memory systems;
17. current standards and versioning.

## 60. Do Not Duplicate Memory Systems

If the project already has a knowledge base, pattern library, experiment
repository, ADRs, postmortems, or agent evaluations, integrate through
references rather than copying everything into a new database.

## 61. Minimum Viable Learning Engine

Phase 1:

``` text
learning record
evidence linkage
scope
confidence
status
experiment outcome ingestion
mission outcome ingestion
decision outcome ingestion
search/retrieval
standardization workflow
```

Phase 2:

``` text
pattern library
cross-room learning
forecast calibration
agent-routing learning
staleness detection
contradiction detection
learning reuse metrics
```

Phase 3, only with evidence:

``` text
automated transfer-learning recommendations
adaptive confidence models
causal pattern analysis
dynamic quest optimization
automatic standard-review proposals
```

## 62. First Learning Engine Mission

``` yaml
mission:
  title: Establish Closed-Loop Organizational Learning
  objective: >
    Implement the smallest reliable learning system that converts verified
    mission, experiment, decision, customer, technical, and agent outcomes
    into scoped and evidence-linked learnings that can improve future
    orchestration without overgeneralizing or silently changing protected
    standards.
  success:
    - learning records are durable
    - evidence is required
    - scope is explicit
    - confidence is explicit
    - candidate and validated learning are distinct
    - contradictions are preserved
    - standards are changed through controlled workflow
    - prior learnings are searchable before new work
    - experiment outcomes feed learning
    - decision predictions can be compared to actuals
    - agent performance can improve routing
    - stale learnings can be identified
```

## 63. Initial State

Until verified:

``` yaml
learning_engine:
  implementation_status: UNKNOWN
  learning_model: UNKNOWN
  pattern_library: UNKNOWN
  evidence_linkage: UNKNOWN
  experiment_ingestion: UNKNOWN
  decision_feedback: UNKNOWN
  agent_feedback: UNKNOWN
  standardization_workflow: UNKNOWN
  staleness_detection: UNKNOWN
  contradiction_detection: UNKNOWN
```

## 64. Acceptance Test: Entryway Quick Start

Input:

``` text
Experiment:
15-minute starter option increases Entryway quest starts.

Guardrails:
Completion and reported usefulness remain healthy.
```

Expected:

``` text
Create scoped learning.
Do not immediately generalize to all rooms.
Promote only to validated status supported by evidence.
Consider a controlled cross-room transfer test.
```

## 65. Acceptance Test: Failed Experiment

Input:

``` text
Gamified timer reduces completion for one measured cohort.
```

Expected:

``` text
Record negative result and context.
Do not globally prohibit timers without broader evidence.
Prevent identical unmodified retest in same context unless new evidence exists.
```

## 66. Acceptance Test: Owner Override

Input:

``` text
Owner rejects Kitchen expansion to continue Entryway validation.
```

Expected:

``` text
Record decision context.
Do not create permanent rule "never expand Kitchen."
Use active directive as authority.
```

## 67. Acceptance Test: Card Duration

Input:

``` text
A 10-minute card takes median 23 minutes across a sufficient representative sample.
```

Expected:

``` text
Create duration-estimation learning.
Update estimate through controlled content/data change.
Track effect after update.
```

## 68. Acceptance Test: One Customer

Input:

``` text
One customer says hooks are ugly.
```

Expected:

``` text
Potential qualitative signal.
No universal anti-hook rule.
```

## 69. Acceptance Test: Technical Incident

Input:

``` text
Deployment fails because environment variable validation was absent.
```

Expected:

``` text
Capture failure mechanism.
Propose preflight validation standard.
Test and standardize if appropriate.
```

## 70. Acceptance Test: Agent Failure

Input:

``` text
Agent repeatedly misroutes VPS deployment work to GitHub-only tooling.
```

Expected:

``` text
Create agent/routing learning.
Remediate instructions or capability registry.
Reevaluate.
Do not merely add more prompt text without testing.
```

## 71. Acceptance Test: Contradiction

Input:

``` text
Previously validated card sequence now performs poorly after major UI redesign.
```

Expected:

``` text
Mark learning contested/stale as appropriate.
Do not preserve it as unquestioned truth.
```

## 72. Acceptance Test: Product Recommendation

Input:

``` text
Users with an existing suitable key bowl achieve the same outcome as users
who purchase a dedicated tray.
```

Expected:

``` text
Learn that dedicated purchase is not required for that use case.
Improve recommendation logic to prefer existing adequate solutions.
```

## 73. Acceptance Test: Cross-Room Pattern

Input:

``` text
Point-of-use storage improves outcomes in Entryway and Office.
```

Expected:

``` text
Create broader candidate pattern.
Do not apply automatically to safety-sensitive medication storage.
```

## 74. Learning Health Questions

At any time the system should answer:

``` text
What have we learned recently?
What evidence supports it?
How confident are we?
Where does it apply?
What did we standardize?
What was contradicted?
What assumptions were invalidated?
What are we still uncertain about?
How has learning changed future decisions?
```

## 75. Anti-Patterns

Avoid:

-   memory without evidence
-   global rules from anecdotes
-   prompt growth as a substitute for learning
-   storing every observation forever
-   forgetting negative experiments
-   ignoring contradictions
-   treating owner corrections as universal policy
-   optimizing learning count
-   copying room solutions blindly
-   confusing correlation with causation
-   rewarding agents only for success
-   deleting failed-decision history
-   retaining stale standards indefinitely
-   letting agents rewrite protected instructions automatically
-   using raw private customer data when aggregate learning is
    sufficient

## 76. Non-Negotiable Rules

Claude and subagents must not:

-   fabricate learning
-   promote observation directly to universal rule
-   hide evidence scope
-   hide contradictory evidence
-   convert low-confidence inference into high-confidence standard
-   let agents self-promote based on their own claims
-   let one owner override become permanent policy without justification
-   overwrite history when a learning is superseded
-   claim causality from simple correlation
-   mix actual and predicted outcomes
-   expose unnecessary private household data
-   retain sensitive raw data merely because it might be useful later
-   standardize a product recommendation without diagnosed need
-   optimize card engagement while ignoring customer outcome
-   treat a successful deployment as proof of business/customer value
-   continuously rewrite prompts without evaluation
-   allow learned rules to override governance or owner directives
-   create duplicate knowledge systems without discovery
-   treat more learning records as the objective

## 77. Final Principle

A mature autonomous organization should become measurably better because
it remembers **what reality taught it**, not because its prompts become
longer.

``` text
PREDICT
  ↓
ACT
  ↓
MEASURE
  ↓
COMPARE
  ↓
LEARN
  ↓
CHALLENGE
  ↓
STANDARDIZE ONLY WHAT HOLDS
  ↓
REUSE IN THE RIGHT CONTEXT
  ↓
MEASURE AGAIN
```

For 6S Success, the system should continuously improve its understanding
of:

``` text
what people want a space to do
why a micro-zone is failing
which 6S countermeasure works
which card is appropriate
how long it really takes
which quest sequence works
when a product is actually useful
what helps the result sustain
which agents make good decisions
which operating patterns are reliable
```

The objective is not infinite memory.

The objective is a **controlled learning system that makes future
customer experiences, autonomous decisions, missions, agents, products,
quests, and operations demonstrably better.**

That is the purpose of `AUTONOMY-LEARNING-ENGINE.md`.
