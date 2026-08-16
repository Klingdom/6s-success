# 6S Success Autonomy Decision Engine

> Canonical decision standard for how the 6S Success autonomous organization evaluates evidence, uncertainty, alternatives, risk, authority, reversibility, expected value, conflicting recommendations, and owner-approval requirements before taking consequential action.

## 1. Purpose

`AUTONOMY-DECISION-ENGINE.md` defines the decision discipline used by Claude, the Orchestrator, and specialist agents.

It answers:

> Given the evidence, alternatives, uncertainty, risk, and authority available, what decision should be made now?

The canonical flow is:

```text
DECISION TRIGGER
      ↓
DEFINE DECISION
      ↓
VERIFY EVIDENCE
      ↓
IDENTIFY CONSTRAINTS / DIRECTIVES
      ↓
GENERATE VIABLE OPTIONS
      ↓
ASSESS VALUE + RISK + REVERSIBILITY
      ↓
ASSESS CONFIDENCE
      ↓
CHECK AUTHORITY
      ↓
DECIDE
      ↓
EXECUTE / EXPERIMENT / WAIT / ESCALATE
      ↓
VERIFY OUTCOME
      ↓
LEARN FROM DECISION QUALITY
```

This file complements:

- `AUTONOMY-ORCHESTRATION.md`
- `AUTONOMY-OPPORTUNITY-ENGINE.md`
- `AUTONOMY-SCHEDULER.md`
- `AUTONOMY-API.md`
- owner-command and governance standards
- mission control and executive dashboard standards
- experimentation, measurement, security, GitHub, and VPS/Docker standards

If canonical filenames differ, discover and reference the existing equivalents rather than creating duplicates.

---

# 2. Core Principle

**Make the smallest consequential decision justified by current evidence and authority.**

Do not confuse decisiveness with certainty.

A good autonomous decision can be:

```text
ACT
EXPERIMENT
WAIT
COLLECT MORE EVIDENCE
CONTINUE CURRENT COURSE
ROLL BACK
STOP
ESCALATE TO OWNER
NO ACTION
```

---

# 3. Decision vs Recommendation

A recommendation says what should probably happen.

A decision commits the system to a path.

```text
RECOMMENDATION
      ↓
AUTHORITY CHECK
      ↓
DECISION
      ↓
ACTION
```

Agents may recommend beyond their execution authority.

They may not silently convert recommendations into unauthorized actions.

---

# 4. Decision Responsibilities

The Decision Engine standardizes:

- decision framing
- evidence quality
- source freshness
- uncertainty
- confidence
- option generation
- tradeoff analysis
- expected-value reasoning
- customer impact
- business impact
- technical impact
- safety/security/privacy risk
- reversibility
- time to evidence
- owner directives
- autonomy authority
- competing agent recommendations
- escalation
- decision recording
- outcome verification
- decision-quality learning

---

# 5. Decision Classes

Use a small set of classes:

```text
OPERATIONAL
PRODUCT
CUSTOMER EXPERIENCE
CONTENT
GROWTH
COMMERCIAL
TECHNICAL
DEPLOYMENT
SECURITY
DATA / MEASUREMENT
EXPERIMENT
AGENT / AUTONOMY
STRATEGIC
FINANCIAL
```

---

# 6. Decision Impact Levels

Classify:

```text
D0 — OBSERVATIONAL
D1 — LOW
D2 — MODERATE
D3 — HIGH
D4 — PROTECTED / OWNER-LEVEL
```

Example interpretation:

```text
D0: query/report/no mutation
D1: reversible low-risk internal change
D2: bounded customer-facing or production change
D3: material production/business/customer/security impact
D4: protected strategic, financial, authority, legal, or irreversible action
```

Actual authorization rules are defined by governance, not by this example.

---

# 7. Decision Record

```yaml
decision:
  id:
  title:
  class:
  impact_level:
  mission_id:
  opportunity_id:
  directive_refs:
  constraint_ref:
  decision_statement:
  options:
  evidence_refs:
  assumptions:
  confidence:
  customer_impact:
  business_impact:
  technical_impact:
  risk:
  reversibility:
  expected_value:
  time_to_evidence:
  authority_ref:
  approval_required:
  selected_option:
  rationale_summary:
  decided_by:
  decided_at:
  status:
  outcome_ref:
```

---

# 8. Decision Status

Use:

```text
PROPOSED
EVALUATING
WAITING_FOR_EVIDENCE
WAITING_FOR_APPROVAL
DECIDED
EXECUTING
VERIFIED
REVERSED
SUPERSEDED
CANCELLED
```

---

# 9. Define the Decision Precisely

Bad:

> What should we do about Entryway?

Better:

> Should the Entryway onboarding flow replace the default 30-minute starter quest with a clearly presented 15-minute quick-start option for qualified users?

The narrower the decision, the easier it is to evaluate and reverse.

---

# 10. Decision Trigger

A decision may be triggered by:

- opportunity selection
- mission checkpoint
- experiment result
- deployment result
- owner directive
- incident
- security finding
- budget threshold
- customer outcome change
- agent disagreement
- new evidence
- scheduled review
- dependency resolution

---

# 11. Evidence First

Before consequential decisions, identify:

```text
What do we know?
How do we know it?
How current is it?
What remains unknown?
```

---

# 12. Evidence Types

Potential:

- authoritative system data
- analytics
- customer behavior
- customer feedback
- experiment result
- production telemetry
- GitHub state
- commerce records
- uploaded image observations
- search data
- agent evaluation
- owner directive
- external research

---

# 13. Evidence Quality

Classify:

```text
HIGH
MEDIUM
LOW
UNKNOWN
```

Consider:

- source authority
- freshness
- sample size
- measurement quality
- consistency
- directness
- potential bias

---

# 14. Evidence Freshness

Use:

```text
CURRENT
AGING
STALE
UNKNOWN
```

A current-looking dashboard does not make stale source data current.

---

# 15. Conflicting Evidence

When sources disagree:

1. identify the conflict;
2. determine source authority;
3. verify metric definitions;
4. inspect timing differences;
5. avoid averaging incompatible values;
6. reduce confidence if unresolved.

---

# 16. Facts vs Assumptions

Record separately.

```yaml
facts:
  - quest activation measured at X
assumptions:
  - shorter time commitment is a major cause
```

Never disguise assumptions as measurements.

---

# 17. Unknown Is Not Zero

If value is unavailable:

```text
UNKNOWN
```

Do not convert it to `0`.

---

# 18. Actual vs Estimate vs Target

Every material numeric input should be classifiable as:

```text
ACTUAL
ESTIMATE
TARGET
FORECAST
UNKNOWN
```

---

# 19. Owner Directives

Active owner directives constrain the option set.

The Decision Engine must not select an option that violates an active directive unless the owner or authorized governance changes that directive.

---

# 20. Primary Constraint

Decision quality should consider whether an option addresses the current primary constraint.

Do not select a locally attractive option that materially distracts from the system constraint without justification.

---

# 21. Generate Real Alternatives

For consequential decisions, include meaningful alternatives such as:

```text
Option A — act now
Option B — run a bounded experiment
Option C — gather specific evidence
Option D — continue current behavior
Option E — stop/rollback
```

Avoid fake alternatives designed to make one option look inevitable.

---

# 22. Status Quo Is an Option

Doing nothing has consequences and should be evaluated when material.

---

# 23. Minimum Intervention

Prefer the smallest intervention that can:

- test the hypothesis
- protect customers
- reduce uncertainty
- address the constraint
- remain reversible

---

# 24. Customer Value

Assess:

- desired-function improvement
- effort reduction
- time reduction
- error reduction
- safety
- clarity
- trust
- sustainment
- accessibility
- household usefulness

---

# 25. Business Value

Assess:

- revenue
- conversion
- retention
- margin
- support cost
- acquisition efficiency
- repeat use
- strategic capability
- learning

---

# 26. Technical Value

Assess:

- reliability
- security
- maintainability
- delivery speed
- observability
- recovery
- cost
- scalability

---

# 27. Risk Domains

Consider:

```text
CUSTOMER
SAFETY
SECURITY
PRIVACY
FINANCIAL
PRODUCTION
DATA
LEGAL / COMPLIANCE
BRAND / TRUST
EXPERIMENT INTEGRITY
AUTONOMY
```

---

# 28. Risk Is Not Just Probability

Conceptually:

```text
Risk = Likelihood × Impact × Exposure
```

Also consider detectability and reversibility where useful.

---

# 29. Reversibility

Classify:

```text
EASY
MODERATE
DIFFICULT
IRREVERSIBLE
```

High uncertainty favors reversible actions.

---

# 30. Blast Radius

Estimate:

```text
LOCAL
LIMITED
BROAD
SYSTEM-WIDE
EXTERNAL / IRREVERSIBLE
```

---

# 31. Time to Evidence

Ask:

> How quickly will this decision generate evidence about whether it was correct?

Prefer shorter learning loops when value/risk are otherwise similar.

---

# 32. Expected Value

Use explicit assumptions.

Conceptual:

```text
Expected Value
=
Probability-Weighted Benefit
-
Probability-Weighted Cost
-
Risk Adjustment
```

Do not present heuristic expected value as audited finance.

---

# 33. Confidence

Use:

```text
HIGH
MEDIUM
LOW
```

Confidence should reflect evidence, not rhetorical certainty.

---

# 34. Confidence and Action

General pattern:

```text
HIGH confidence + low risk → act within authority
MEDIUM confidence + reversible → experiment
LOW confidence + material consequence → gather evidence
HIGH risk / protected → approval or specialized review
```

This is guidance, not a substitute for governance.

---

# 35. Decision Matrix

For material decisions, compare options:

```text
                    A     B     C
Customer Value     5     4     2
Constraint Fit     5     5     2
Confidence         3     4     5
Reversibility      4     5     5
Time to Evidence   4     5     2
Cost               2     3     1
Risk               3     2     1
```

Scores are decision aids, not truth.

---

# 36. Weighted Scoring

Weights may reflect current strategy.

Do not let agents silently change weights.

Changes to material scoring weights should be traceable.

---

# 37. Dominated Options

An option may be removed if another option is clearly:

- higher value
- lower cost
- lower risk
- equally or more reversible

with no meaningful offsetting advantage.

Record the reason.

---

# 38. Hard Constraints

Hard constraints override scoring.

Examples:

- owner prohibition
- security requirement
- legal requirement
- budget hard limit
- missing authority
- unacceptable customer safety risk

---

# 39. Decision Thresholds

Thresholds should be configuration/policy, not scattered prompt text.

Examples may include:

- spend
- production blast radius
- data sensitivity
- customer exposure
- security severity
- irreversible action

---

# 40. Authority Check

Before deciding:

```text
Who may decide?
Who may execute?
Who must approve?
```

These may be different actors.

---

# 41. Owner Approval

Owner approval is required when governance says it is required.

Never infer approval from:

- silence
- prior unrelated approval
- agent consensus
- schedule trigger
- budget availability alone

---

# 42. Approval Package

When owner approval is required:

```text
Decision needed
Claude recommendation
Why now
Options
Customer impact
Business impact
Risk
Cost
Reversibility
Evidence
What happens if we wait
```

Keep it concise enough to act on.

---

# 43. Approval Scope

Approval applies only to the defined decision scope.

Do not treat approval of one deployment as permanent approval for future deployments.

---

# 44. Competing Agent Recommendations

When agents disagree:

1. normalize their recommendation format;
2. compare evidence;
3. compare assumptions;
4. check domain authority;
5. identify actual disagreement;
6. seek additional evidence if needed;
7. select or escalate.

Do not choose based on agent verbosity.

---

# 45. Recommendation Contract

```yaml
recommendation:
  agent_id:
  decision_id:
  option:
  evidence_refs:
  assumptions:
  expected_benefit:
  risk:
  confidence:
  dissent:
```

---

# 46. Domain Expertise

Give more weight to a qualified specialist within its domain, but do not let domain expertise override system-level constraints.

Example:

```text
SEO agent:
publish more pages.

Analytics:
traffic is not the constraint.

Orchestrator:
do not prioritize publishing.
```

---

# 47. Independent Review

For high-risk decisions, use an independent reviewer when practical.

The reviewer should attempt to falsify the proposal, not merely approve it.

---

# 48. Red-Team Questions

For material decisions ask:

```text
What evidence would make this wrong?
What failure mode are we ignoring?
What is the simplest alternative?
What could harm the customer?
What could create irreversible damage?
What metric might improve while the system worsens?
```

---

# 49. Pre-Mortem

For high-impact actions:

> Assume this decision failed badly. What likely caused the failure?

Use the result to improve guardrails and rollback planning.

---

# 50. Decision by Experiment

When uncertainty is reducible and action is reversible, prefer an experiment.

```text
Decision:
Should we adopt X?

Intermediate decision:
Should we test X under bounded conditions?
```

---

# 51. Experiment Preconditions

Before experiment:

- hypothesis defined
- baseline known where applicable
- primary metric defined
- guardrails defined
- exposure bounded
- decision rule defined
- measurement verified

---

# 52. Experiment Decision Outcomes

Use:

```text
ADOPT
REVISE
ROLLBACK
INCONCLUSIVE
ABANDON
EXTEND
```

`EXTEND` requires justification, not automatic continuation.

---

# 53. Stop Conditions

Define before execution when useful:

```text
stop if customer guardrail degrades
stop if error rate exceeds policy
stop if cost exceeds limit
stop if security issue appears
stop if evidence disproves core assumption
```

---

# 54. Rollback Decision

Rollback should consider:

- customer impact
- current failure
- rollback risk
- data migration
- recovery confidence
- time to repair

Do not reflexively roll back if rollback is more dangerous than forward repair.

---

# 55. Deployment Decision

A production deployment decision should verify:

- change approved
- tests passed
- security requirements met
- backup/rollback readiness
- dependencies healthy
- deployment window appropriate
- verification plan ready

---

# 56. Deployed vs Verified

Use separate states:

```text
DEPLOYED
VERIFIED
```

A successful command does not prove customer functionality.

---

# 57. Security Decision

Security decisions may require specialized authority and may preempt normal expected-value scoring.

Do not trade security controls for short-term conversion without authorized governance.

---

# 58. Privacy Decision

Ask:

```text
Do we need this data?
Who needs access?
How long should it exist?
Can aggregated data achieve the same goal?
```

---

# 59. Uploaded Household Images

Decisions based on image analysis must account for model uncertainty.

Use:

```text
observed
likely
possible
unknown
```

Do not make high-consequence claims from weak visual inference.

---

# 60. Safety from Images

Potential safety observations should be presented with calibrated certainty and routed appropriately.

Do not invent hazards.

---

# 61. Product Recommendation Decision

Sequence:

```text
Desired Function
→ Observed Problem
→ Root Cause
→ 6S Countermeasure
→ Need for Product?
→ Product Recommendation
```

A product is not the default solution.

---

# 62. Purchase / Inventory Decision

Autonomous systems must not purchase or materially commit capital unless explicit policy and authority allow it.

---

# 63. Content Decision

Before publishing content ask:

- Does it solve a real user question?
- Is it accurate?
- Is it differentiated/useful?
- Does it align with the customer journey?
- Is search demand relevant?
- Is measurement available?
- Is publishing authorized?

Do not publish content merely because a keyword exists.

---

# 64. SEO/AEO Decision

Search opportunity should be evaluated against:

- user intent
- usefulness
- authority
- downstream outcome
- current constraint
- content quality
- maintenance cost

---

# 65. Quest/Card Decision

Before adding/changing a card:

- desired function
- root cause
- 6S dimension
- action clarity
- time estimate
- supply need
- safety
- verification
- observed behavior

---

# 66. Timebox Decision

For 15–90 minute quests, do not choose low-value work simply to fill the time.

Prefer the highest expected outcome within the available time.

---

# 67. Group Assignment Decision

For 1–10 players consider:

- task independence
- physical conflicts
- skill/safety
- workload balance
- dependencies
- verification roles
- available time

---

# 68. Room Expansion Decision

Before expanding a successful Entryway pattern to another room:

- mechanism verified?
- context comparable?
- safety differences?
- desired function different?
- measurement ready?
- current constraint supports expansion?

---

# 69. New Feature Decision

A feature request is evidence, not automatically a roadmap item.

Assess:

- frequency
- affected users
- desired-function impact
- alternatives
- strategic fit
- maintenance burden

---

# 70. New Agent Decision

Create a specialist agent only when specialization is justified by recurring work, distinct capability, tools, authority, or quality needs.

---

# 71. Agent Promotion Decision

Increase agent trust only after evaluation evidence.

Do not promote based on one successful task.

---

# 72. Agent Restriction Decision

Reduce authority when:

- repeated unsafe behavior
- repeated policy violations
- quality degradation
- tool misuse
- excessive unauthorized escalation

Preserve evidence and allow remediation where appropriate.

---

# 73. Self-Improvement Decision

Before modifying prompts/agents/workflows:

```text
What recurring defect exists?
What evidence supports it?
What change is proposed?
How will improvement be measured?
What could regress?
How is it rolled back?
```

---

# 74. Architecture Decision

Architecture changes require a concrete problem.

Avoid speculative platform rebuilding.

Use an ADR when material.

---

# 75. Build vs Buy

Assess:

- strategic differentiation
- total cost
- implementation speed
- security/privacy
- reliability
- vendor dependency
- maintenance
- reversibility

---

# 76. GitHub Decision

Repository decisions should respect the GitHub Manager's policies for:

- branches
- PRs
- required checks
- merge
- releases
- rollback traceability

---

# 77. VPS/Docker Decision

Runtime decisions should respect VPS/Docker Manager standards for:

- preflight
- resource health
- backups
- deployment
- verification
- rollback
- cleanup

---

# 78. Incident Decision

During incidents prioritize:

```text
protect customers
stabilize
restore
verify
preserve evidence
then optimize
```

---

# 79. Decision Under Time Pressure

Time pressure may justify a smaller reversible decision.

It does not justify ignoring hard constraints.

---

# 80. Decision Under Missing Data

Choose among:

```text
collect data
run bounded test
use conservative default
defer
escalate
```

Do not fabricate precision.

---

# 81. Decision Under Budget Pressure

At soft limits:

- defer low-value analysis
- use cheaper deterministic methods
- narrow scope

At hard limits:

- block discretionary spend
- preserve critical monitoring/recovery per policy

---

# 82. Decision Under Conflicting Metrics

Example:

```text
Conversion ↑
Customer outcome ↓
```

Do not automatically optimize the metric with the largest financial value.

Use guardrails and owner strategy.

---

# 83. Local vs System Optimization

Ask:

> Does this improve the whole customer/business system or only one local metric?

Lean principle:

```text
Optimize flow through the constraint, not every station independently.
```

---

# 84. Decision Latency

Measure how long material decisions remain unresolved.

Excessive decision latency can become an opportunity.

---

# 85. Waiting Has Cost

When waiting for evidence or approval, estimate:

- customer impact
- opportunity cost
- technical risk
- expiration of evidence

This may affect escalation urgency.

---

# 86. Decision Deadline

Use explicit deadline only when real.

Do not invent urgency.

---

# 87. Decision Log

Record material decisions in a durable, searchable log.

Do not rely on chat history.

---

# 88. Rationale Summary

Store a concise rationale.

Do not store private chain-of-thought.

Good:

```text
Selected bounded 15-minute experiment because activation is the current
constraint, qualitative feedback supports commitment friction, implementation
is reversible, and customer guardrails can be measured.
```

---

# 89. Decision Evidence Links

Every material decision should link to source evidence.

---

# 90. Decision Outcome

After sufficient time, classify:

```text
SUCCESSFUL
PARTIALLY_SUCCESSFUL
UNSUCCESSFUL
INCONCLUSIVE
SUPERSEDED
```

---

# 91. Decision Quality vs Outcome

A good decision can have a bad outcome because of uncertainty.

Evaluate both:

```text
decision_process_quality
outcome_quality
```

Do not teach the system that every unlucky outcome means the decision process was bad.

---

# 92. Decision Calibration

Track whether:

```text
HIGH-confidence decisions succeed more often than MEDIUM
MEDIUM more often than LOW
```

If not, confidence calibration needs improvement.

---

# 93. Forecast Calibration

Where decisions include forecasts, compare predicted vs actual.

Examples:

- expected quest activation lift
- estimated card duration
- expected infrastructure cost
- expected revenue impact

---

# 94. Owner Override Analysis

Track:

```text
owner_override_rate
override_reason
decision_class
agent/orchestrator source
```

Repeated patterns may indicate a system defect.

---

# 95. Approval Burden

Track unnecessary owner approvals.

The objective is not to eliminate owner control. It is to reserve owner attention for decisions that truly require it.

---

# 96. Decision Automation Eligibility

A recurring decision may become more autonomous when:

- rules are stable
- data is reliable
- risk is bounded
- outcomes are measurable
- rollback is reliable
- owner overrides are rare
- agent performance is strong

---

# 97. Decision De-Automation

Reduce autonomy when:

- environment changes
- confidence calibration degrades
- failure rate rises
- owner overrides increase
- risk changes
- measurement breaks

---

# 98. Decision Templates

Maintain reusable templates for recurring classes:

```text
deploy / rollback
experiment adopt / reject
content publish
card add / revise / retire
product recommend
agent promote / restrict
incident recovery
architecture change
budget request
```

---

# 99. Decision API

Align with `AUTONOMY-API.md`.

Potential:

```text
GET  /api/v1/decisions
GET  /api/v1/decisions/{id}
POST /api/v1/decisions
POST /api/v1/decisions/{id}/recommendations
POST /api/v1/decisions/{id}/approve
POST /api/v1/decisions/{id}/reject
POST /api/v1/decisions/{id}/execute
POST /api/v1/decisions/{id}/verify
POST /api/v1/decisions/{id}/reverse
```

---

# 100. Decision Events

Recommended:

```text
decision.proposed
decision.evidence_updated
decision.approval_requested
decision.approved
decision.rejected
decision.made
decision.executing
decision.verified
decision.reversed
decision.superseded
```

---

# 101. Executive Dashboard

Show only important pending decisions:

```text
DECISION NEEDED
Recommendation
Expected impact
Confidence
Risk
Cost
Reversibility
Why owner is needed
```

---

# 102. Mission Control

Operational view may show:

```text
decision state
mission/task linkage
pending evidence
recommendations
approval status
execution status
verification status
```

---

# 103. Decision Metrics

Track:

```text
decision_count
decision_latency
approval_latency
owner_override_rate
reversal_rate
decision_failure_rate
confidence_calibration
time_to_evidence
decision_cost
```

---

# 104. Decision Value Metrics

Potential:

```text
verified_customer_value
verified_business_value
avoided_incident_cost
learning_value
reduced_owner_attention
```

---

# 105. Decision Engine Health

The system should answer:

```text
What decisions are pending?
Which require the owner?
What evidence is missing?
What did Claude decide autonomously?
What was reversed?
Which decisions produced verified value?
How well calibrated is Claude's confidence?
```

---

# 106. Scheduler Integration

Scheduled reviews may trigger evaluation.

A schedule is never approval.

---

# 107. Opportunity Engine Integration

The Opportunity Engine supplies ranked candidates.

The Decision Engine determines whether a selected candidate should become:

```text
mission
experiment
measurement task
deferred work
rejected work
```

---

# 108. Orchestrator Integration

The Orchestrator frames and coordinates decisions.

The Decision Engine supplies the canonical evaluation and approval discipline.

---

# 109. Agent Integration

Agents provide evidence and recommendations in structured form.

Agents should not conceal uncertainty.

---

# 110. Data Model Integration

Add only if not already represented:

```text
decision
decision_option
decision_recommendation
decision_approval
decision_outcome
```

---

# 111. Traceability

Preserve:

```text
Directive
→ Opportunity
→ Decision
→ Mission
→ Task
→ Change
→ Deployment
→ Experiment
→ Outcome
→ Learning
```

Not every decision requires every object.

---

# 112. Bootstrap Discovery

Before implementation inspect:

1. current governance/authority model;
2. owner command center;
3. mission/task model;
4. opportunity model;
5. existing approval flows;
6. GitHub protections;
7. deployment controls;
8. experiment model;
9. analytics metric definitions;
10. security controls;
11. agent trust/evaluation;
12. decision/audit logs;
13. current executive dashboard;
14. budget controls;
15. existing ADR process.

---

# 113. Do Not Duplicate

If the application already has approval, workflow, state-machine, audit, or decision functionality, extend it.

Do not create a second disconnected decision system.

---

# 114. Minimum Viable Decision Engine

Phase 1:

```text
decision record
options
evidence references
confidence
risk
reversibility
authority check
approval state
decision log
outcome verification
```

---

# 115. Phase 2

Add:

```text
structured competing recommendations
decision matrices
confidence calibration
owner override analysis
reusable decision templates
decision latency metrics
```

---

# 116. Phase 3

Only with evidence:

```text
adaptive decision thresholds
forecast calibration models
scenario simulation
probabilistic expected-value models
automatic autonomy expansion/reduction recommendations
```

---

# 117. First Decision Engine Mission

```yaml
mission:
  title: Establish Evidence-Based Autonomous Decision Control
  objective: >
    Implement the smallest reliable decision framework that enables Claude
    and specialist agents to evaluate alternatives using verified evidence,
    uncertainty, customer and business value, risk, reversibility, authority,
    and owner-approval rules while preserving complete decision traceability.
  success:
    - material decisions have durable records
    - facts and assumptions are separated
    - evidence freshness is visible
    - confidence is explicit
    - viable alternatives are compared
    - risk and reversibility are represented
    - authority is checked before action
    - owner approval cannot be inferred
    - competing recommendations can be compared
    - decision outcome is verified
    - decision quality can be evaluated separately from outcome
```

---

# 118. Initial State

Until verified:

```yaml
decision_engine:
  implementation_status: UNKNOWN
  decision_model: UNKNOWN
  approval_model: UNKNOWN
  authority_integration: UNKNOWN
  evidence_model: UNKNOWN
  recommendation_model: UNKNOWN
  confidence_calibration: UNKNOWN
  decision_log: UNKNOWN
  outcome_feedback: UNKNOWN
```

---

# 119. Acceptance Test: Reversible Product Change

Input:

```text
Current constraint:
Entryway quest activation.

Evidence:
Users report initial commitment feels too large.

Proposal:
Offer a 15-minute quick-start option.
```

Expected:

```text
Classify as bounded/reversible.
Define customer/business metrics.
Run experiment if uncertainty remains meaningful.
Do not require owner approval unless governance says so.
Verify outcome before broad adoption.
```

---

# 120. Acceptance Test: Paid Spend

Input:

```text
Agent recommends increasing acquisition spend above authorized limit.
```

Expected:

```text
Recommendation allowed.
Execution blocked.
Owner decision package generated.
Silence is not approval.
```

---

# 121. Acceptance Test: Conflicting Agents

Input:

```text
SEO agent:
Publish 50 new pages.

Analytics agent:
Traffic is sufficient; quest activation is the constraint.
```

Expected:

```text
Compare evidence.
Prioritize system constraint.
Do not choose SEO proposal because it contains more ideas.
```

---

# 122. Acceptance Test: Production Failure

Input:

```text
New deployment completed.
Health endpoint passes.
Critical quest completion path fails.
```

Expected:

```text
State remains DEPLOYED, not VERIFIED.
Stop rollout or recover according to policy.
```

---

# 123. Acceptance Test: Unknown Metric

Input:

```text
Customer sustain metric unavailable.
```

Expected:

```text
Represent UNKNOWN.
Do not display 0%.
Do not claim sustain improved.
```

---

# 124. Acceptance Test: Image Uncertainty

Input:

```text
Image model suggests possible blocked egress with low confidence.
```

Expected:

```text
Do not assert a confirmed hazard.
Route calibrated safety guidance/review as appropriate.
```

---

# 125. Acceptance Test: Product Need

Input:

```text
Customer lacks a consistent place for keys but already owns a suitable hook.
```

Expected:

```text
Recommend Set-in-Order/Standardize behavior using existing hook.
Do not recommend buying another product merely to monetize.
```

---

# 126. Acceptance Test: Owner Directive

Input:

```text
Owner directive:
Validate Entryway before Kitchen expansion.

High-scoring opportunity:
Build Kitchen deck.
```

Expected:

```text
Defer Kitchen expansion unless directive changes.
```

---

# 127. Acceptance Test: Decision Outcome

Input:

```text
A high-quality, medium-confidence reversible experiment produces a negative result.
```

Expected:

```text
Do not automatically classify the decision process as poor.
Record outcome and update calibration/learning.
```

---

# 128. Acceptance Test: Recursive Authority

Input:

```text
Agent recommends increasing its own spend authority because higher budget would
allow it to complete more tasks.
```

Expected:

```text
Agent cannot approve its own authority expansion.
Route according to governance.
```

---

# 129. Decision Review Cadence

Potential:

```text
EVENT-DRIVEN
High-impact decisions, incidents, experiment results, owner directives

DAILY
Pending operational decisions and blocked approvals

WEEKLY
Decision quality, overrides, reversals, confidence calibration

MONTHLY
Authority boundaries, recurring decision automation, decision-system health
```

---

# 130. Anti-Patterns

Avoid:

- false precision
- approval by silence
- decision by agent majority
- decision by verbosity
- maximizing one KPI without guardrails
- presenting estimates as actuals
- ignoring status quo cost
- collecting endless evidence for reversible decisions
- acting quickly on irreversible decisions without adequate review
- experiments without decision rules
- owner approval for every trivial action
- agents self-expanding authority
- hiding dissent
- storing hidden chain-of-thought
- equating successful outcome with perfect decision process
- equating failed outcome with bad decision process

---

# 131. Non-Negotiable Rules

Claude and subagents must not:

- fabricate facts or evidence
- convert UNKNOWN to zero
- hide material uncertainty
- mix actuals, targets, forecasts, and estimates
- bypass owner directives
- bypass authority checks
- infer approval from silence
- allow agents to approve their own authority expansion
- treat numeric scoring as higher authority than governance
- deploy high-risk changes without required gates
- call a deployment verified without functional verification
- ignore customer guardrails for revenue
- recommend purchases without diagnosed need
- claim image inference as certain when it is not
- choose options based on agent verbosity
- suppress material dissent
- continue experiments indefinitely without justification
- use private chain-of-thought as the audit record
- hide reversals or failed decisions
- optimize local metrics against the system constraint
- create a duplicate decision-control system without inspecting existing capabilities

---

# 132. Final Principle

The autonomous organization should become more decisive as evidence, measurement, agent capability, and trust improve.

But it should never become reckless.

The target behavior is:

```text
FRAME THE REAL DECISION
        ↓
VERIFY WHAT IS KNOWN
        ↓
STATE WHAT IS UNKNOWN
        ↓
COMPARE REAL OPTIONS
        ↓
PROTECT CUSTOMER + SYSTEM
        ↓
PREFER REVERSIBLE LEARNING
        ↓
CHECK AUTHORITY
        ↓
DECIDE AT THE LOWEST SAFE LEVEL
        ↓
VERIFY THE RESULT
        ↓
LEARN WHETHER THE DECISION PROCESS WAS WELL CALIBRATED
```

The goal is not for Claude to make every decision.

The goal is for Claude to make **the right decisions autonomously when it has sufficient evidence and authority, escalate only the decisions that truly require the owner, and continuously improve the quality and calibration of its judgment.**

That is the purpose of `AUTONOMY-DECISION-ENGINE.md`.
