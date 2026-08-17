# 6S Success Autonomy Health

> Canonical health, effectiveness, efficiency, quality, and continuous-improvement framework for the 6S Success autonomous Claude Code operating system.

## 1. Purpose

`AUTONOMY-HEALTH.md` measures whether the autonomous operating system itself is working well.

The website, products, customer journeys, quests, GitHub, VPS, Docker, analytics, commerce, and growth systems can improve while the autonomous organization quietly becomes expensive, noisy, fragile, or ineffective.

This file prevents that.

It answers:

- Is Claude completing useful work autonomously?
- Are the right agents being routed?
- Are agents succeeding?
- Are agents duplicating work?
- Are owner interruptions decreasing?
- Are deployments safe?
- Are failures being recovered?
- Is autonomous work producing measurable value?
- Are API/token/tool costs reasonable?
- Are policies being followed?
- Is documentation becoming stale?
- Are agents learning from failures?
- Is the autonomous system becoming simpler and more capable over time?

---

# 2. Core Principle

**Do not optimize for agent activity. Optimize for verified outcomes per unit of risk, cost, and owner attention.**

More tasks, agents, commits, content, and tool calls are not inherently better.

---

# 3. Health Dimensions

Measure autonomy across:

1. Outcome Effectiveness
2. Autonomous Completion
3. Reliability
4. Quality
5. Routing Quality
6. Owner Attention
7. Speed
8. Cost Efficiency
9. Safety & Governance
10. Learning
11. Operational Hygiene
12. System Simplicity

---

# 4. Health Status

Use:

- `GREEN`
- `YELLOW`
- `RED`
- `UNKNOWN`

Never convert missing evidence into GREEN.

---

# 5. Overall Health

```yaml
autonomy_health:
  overall: UNKNOWN
  effectiveness: UNKNOWN
  reliability: UNKNOWN
  quality: UNKNOWN
  routing: UNKNOWN
  owner_attention: UNKNOWN
  speed: UNKNOWN
  cost_efficiency: UNKNOWN
  governance: UNKNOWN
  learning: UNKNOWN
  hygiene: UNKNOWN
  simplicity: UNKNOWN
  last_verified: UNKNOWN
```

---

# 6. Primary Autonomy KPI

The preferred top-level measure is:

```text
Verified Valuable Outcomes
────────────────────────────
Owner Attention + Risk + Cost
```

This is a conceptual management equation, not necessarily a single numeric score.

---

# 7. Autonomous Completion Rate

```text
Autonomous Completion Rate =
Eligible Tasks Completed Without Owner Intervention
───────────────────────────────────────────────────
All Eligible Completed Tasks
```

Do not include tasks that policy intentionally requires the owner to approve.

---

# 8. Owner Interruption Rate

```text
Owner Interruption Rate =
Routine Owner Interruptions
───────────────────────────
Eligible Autonomous Tasks
```

The target direction is downward without sacrificing safety.

---

# 9. Appropriate Escalation Rate

Low owner interruption is not sufficient.

Measure whether escalations were appropriate.

Examples of appropriate escalation:

- material spend
- major strategic pivot
- legal/reputational risk
- irreversible destructive action
- critical security issue
- explicit owner gate

Unnecessary escalation is an autonomy defect.

Failure to escalate a required decision is a governance defect.

---

# 10. Task Success Rate

```text
Task Success Rate =
Tasks Meeting Definition of Done
────────────────────────────────
Completed Task Attempts
```

A task is not successful merely because an agent produced text.

---

# 11. First-Pass Success Rate

```text
First-Pass Success =
Tasks Completed Without Rework
──────────────────────────────
Completed Tasks
```

Use this to identify weak prompts, agents, tests, or routing.

---

# 12. Rework Rate

Track work repeated because of:

- incomplete implementation
- incorrect assumptions
- failed tests
- owner correction
- routing error
- conflicting agent changes
- stale context
- poor requirements

---

# 13. Rollback Rate

```text
Rollback Rate =
Production Changes Rolled Back
──────────────────────────────
Production Changes
```

Interpret alongside change size and risk.

Zero rollbacks can also indicate insufficient experimentation.

---

# 14. Change Failure Rate

Track production changes causing:

- outage
- degradation
- customer-visible defect
- commerce failure
- security issue
- urgent rollback
- hotfix

---

# 15. Mean Time to Recovery

For autonomous incidents:

```text
MTTR =
Average Time from Detection to Verified Recovery
```

Also record detection source.

---

# 16. Detection Quality

Track percentage of material failures first detected by:

- automated monitoring
- agent verification
- owner
- customer
- external provider

Desired direction:

**monitoring/verification detects problems before owner/customer reports them.**

---

# 17. Routing Accuracy

A routing decision is successful when:

- correct owner selected
- correct mode selected
- required support included
- unnecessary agents excluded
- authority matched task
- no avoidable reroute occurred

---

# 18. Reroute Rate

```text
Reroute Rate =
Tasks Reassigned Due to Incorrect Initial Routing
─────────────────────────────────────────────────
Routed Tasks
```

High reroute rate indicates `AGENT-ROUTING.md` needs improvement.

---

# 19. Agent Fan-Out

Track:

```yaml
fanout:
  average_agents_per_task:
  max_agents_per_task:
  tasks_exceeding_routine_limit:
```

More agents are not a quality signal.

---

# 20. Duplicate Work Rate

Detect:

- two agents analyzing same problem unnecessarily
- duplicate content
- duplicate PRs
- duplicate experiments
- repeated infrastructure discovery
- repeated owner questions

---

# 21. Conflict Rate

Track agent conflicts involving:

- same file
- same branch
- same environment
- same product
- same experiment
- same customer journey
- incompatible recommendations

---

# 22. Lock Health

```yaml
locks:
  stale_locks:
  lock_conflicts:
  forced_unlocks:
  average_hold_time:
```

Stale locks are an operational defect.

---

# 23. Agent Success Scorecard

For each agent:

```yaml
agent_health:
  agent_id:
  status:
  tasks_completed:
  success_rate:
  first_pass_success:
  reroute_rate:
  rework_rate:
  average_duration:
  estimated_cost:
  policy_violations:
  unnecessary_escalations:
  last_success:
  last_failure:
  last_reviewed:
```

Use verified metrics only.

---

# 24. Agent Health Status

Suggested interpretation:

## GREEN

Consistently successful, compliant, appropriately routed.

## YELLOW

Meaningful rework, failures, stale configuration, or unclear ownership.

## RED

Repeated unsafe, incorrect, expensive, or unreliable behavior.

## UNKNOWN

Insufficient evidence.

---

# 25. Agent Degradation

When an agent becomes degraded:

1. reduce authority if necessary
2. route lower-risk work only
3. inspect recent failures
4. compare task contracts
5. review agent MD file
6. test corrected behavior
7. restore authority only after verification

---

# 26. Agent Disablement

Disable routing when:

- repeated policy violation
- repeated destructive failure
- role is obsolete
- duplicate specialist exists
- required tools are unavailable
- outputs cannot be trusted

Update `SYSTEM-REGISTRY.md`.

---

# 27. Agent Improvement Loop

For repeated failure:

```text
Failure
→ Classify
→ Root Cause
→ Agent/Prompt/Policy/Tool Fix
→ Bounded Test
→ Measure
→ Standardize
```

Do not merely retry indefinitely.

---

# 28. Failure Taxonomy

Use:

- `ROUTING`
- `REQUIREMENTS`
- `CONTEXT`
- `DATA`
- `TOOL`
- `AUTHORITY`
- `IMPLEMENTATION`
- `TEST`
- `DEPLOYMENT`
- `VERIFICATION`
- `POLICY`
- `EXTERNAL`
- `UNKNOWN`

---

# 29. Root Cause Requirement

Repeated failures of the same class should trigger root-cause analysis.

Do not normalize recurring errors.

---

# 30. Owner Correction Rate

Track how often the owner must correct:

- strategic interpretation
- technical implementation
- brand/content
- product logic
- metrics
- agent behavior

A declining correction rate is a strong autonomy maturity signal.

---

# 31. Owner Attention Budget

Owner attention is scarce.

Track:

```yaml
owner_attention:
  decisions_requested:
  routine_questions:
  emergency_interruptions:
  batched_reviews:
  estimated_minutes:
```

Do not optimize this metric by hiding material issues.

---

# 32. Decision Batching

Measure percentage of nonurgent owner decisions successfully batched into planned review.

---

# 33. Autonomous Value

Every major autonomous mission should map to at least one:

- customer outcome
- revenue
- margin
- conversion
- retention
- reliability
- risk reduction
- cost reduction
- cycle-time reduction
- learning
- owner-time reduction

---

# 34. Value Attribution

Do not claim value without evidence.

Use:

```yaml
value:
  type:
  baseline:
  result:
  confidence:
  attribution:
  evidence:
```

---

# 35. Activity vs Value

Track both, but never confuse:

```text
50 commits ≠ value
100 articles ≠ value
20 agents ≠ value
1,000 tool calls ≠ value
```

A single improvement that increases successful Entryway outcomes may be more valuable.

---

# 36. Autonomy Cost

Track:

- model/API cost
- external API cost
- compute
- SaaS
- CI minutes
- storage
- paid tools
- agent-induced infrastructure cost

---

# 37. Cost Per Successful Mission

```text
Autonomy Cost per Successful Mission =
Autonomy Operating Cost
───────────────────────
Successful Missions
```

Interpret by mission complexity.

---

# 38. Cost Per Verified Outcome

Where measurable:

```text
Autonomy Cost
─────────────
Verified Customer/Business Outcomes
```

Use cautiously and transparently.

---

# 39. Token / Model Efficiency

If available, track:

```yaml
model_efficiency:
  total_cost:
  cost_by_agent:
  cost_by_mission:
  retries:
  expensive_failures:
  context_bloat:
```

Do not sacrifice output quality solely to minimize tokens.

---

# 40. Context Efficiency

Watch for:

- huge repeated prompts
- every agent loading every MD file
- repeated infrastructure discovery
- duplicate analytics retrieval
- irrelevant context

`AGENT-ROUTING.md` should package only necessary context.

---

# 41. Tool Efficiency

Track repeated unnecessary:

- GitHub calls
- SSH sessions
- Docker inspections
- analytics queries
- content generation
- deployments

Cache verified state where safe and respect freshness requirements.

---

# 42. Cycle Time

Measure:

```text
Mission Selected
→ Implementation
→ Deployment
→ Measurement
→ Decision
```

Break down waiting time vs active work.

---

# 43. Queue Time

High queue time may indicate:

- overloaded agent
- excessive WIP
- lock contention
- slow owner approvals
- external dependency

---

# 44. Time to First Evidence

Measure how quickly a mission moves from hypothesis to meaningful evidence.

This is often more valuable than raw implementation speed.

---

# 45. Deployment Frequency

Track production releases, but do not maximize frequency blindly.

Healthy frequency should reflect:

- small reversible changes
- adequate testing
- measurable improvement

---

# 46. Experiment Throughput

Track:

- experiments started
- completed
- inconclusive
- stopped
- standardized
- rolled back

Quality matters more than volume.

---

# 47. Experiment Learning Yield

```text
Learning Yield =
Experiments Producing Actionable Learning
─────────────────────────────────────────
Completed Experiments
```

A losing experiment can have high learning yield.

---

# 48. Instrumentation Health

Autonomy depends on trustworthy measurement.

Track:

- missing events
- stale pipelines
- duplicate events
- broken attribution
- schema drift
- impossible values
- metric conflicts

---

# 49. Evidence Freshness

Track percentage of decisions made from sources within required freshness windows.

---

# 50. Unknown Rate

Healthy autonomous systems surface unknowns.

```text
Unknown Rate =
Material Decision Inputs Marked UNKNOWN
───────────────────────────────────────
Material Decision Inputs
```

Do not drive this to zero through guessing.

Instead reduce it through better instrumentation.

---

# 51. Documentation Freshness

Monitor:

- `SYSTEM-REGISTRY.md`
- `MISSION-CONTROL.md`
- `OWNER-DIRECTIVES.md`
- `AGENT-ROUTING.md`
- `STATUS.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `DISASTER-RECOVERY.md`

Flag stale operational documents.

---

# 52. Registry Drift

Track discrepancies between `SYSTEM-REGISTRY.md` and reality.

Examples:

- unregistered container
- unregistered service
- missing job
- changed DNS
- orphaned secret
- stale repository mapping

---

# 53. Mission Control Freshness

Mission Control should be one of the freshest operational artifacts.

Track:

```yaml
mission_control_health:
  last_updated:
  stale_fields:
  orphaned_tasks:
  invalid_agent_refs:
  invalid_release_ref:
```

---

# 54. Backlog Health

Watch for:

- excessive size
- stale items
- duplicate items
- items unrelated to directives
- missing evidence
- unclear owner
- no success criteria

---

# 55. Policy Compliance

Track violations of:

- autonomy
- security
- release
- cost
- privacy
- content/evidence
- routing
- owner directives

---

# 56. Policy Violation Severity

Use:

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

Critical/high violations require review before normal autonomous work continues where appropriate.

---

# 57. Near-Miss Tracking

Record significant cases where controls prevented:

- unsafe deployment
- exposed secret
- destructive action
- runaway spend
- conflicting writes
- bad experiment conclusion

Near misses are valuable learning.

---

# 58. Security Autonomy Health

Track:

- critical vulnerabilities
- time to remediate
- exposed secrets
- excessive privileges
- unauthorized access attempts
- stale credentials
- security agent response quality

Do not store secret values.

---

# 59. Recovery Health

Track:

- backup success
- restore tests
- rollback success
- recovery time
- failed recovery attempts
- undocumented dependencies

---

# 60. Production Verification Rate

```text
Production Verification Rate =
Releases With Verified Post-Deploy Checks
────────────────────────────────────────
Production Releases
```

Target should approach 100%.

---

# 61. Traceability Rate

Track percentage of production changes traceable through:

```text
Mission/Task
→ PR
→ Commit
→ Image
→ Deployment
→ Verification
```

---

# 62. Orphan Rate

Track:

- orphaned containers
- orphaned jobs
- orphaned secrets
- orphaned branches
- orphaned services
- orphaned experiments
- orphaned tasks

---

# 63. Complexity Budget

Autonomy should not continuously add:

- agents
- services
- containers
- tools
- databases
- queues
- policy files

without retiring or simplifying when appropriate.

---

# 64. Complexity Metrics

Track:

```yaml
complexity:
  active_agents:
  active_services:
  production_containers:
  repositories:
  scheduled_jobs:
  policy_files:
  external_services:
```

Interpret changes against value.

---

# 65. Simplicity Review

Ask periodically:

> Could the same outcomes be achieved with fewer agents, fewer services, fewer jobs, fewer dependencies, or simpler workflows?

If yes, simplify.

---

# 66. Automation Debt

Automation debt includes:

- brittle scripts
- undocumented jobs
- manual recovery
- duplicate automations
- missing ownership
- excessive permissions
- no tests
- stale prompts
- hard-coded infrastructure assumptions

Track in backlog.

---

# 67. Agent Prompt Drift

Agent MD files can become outdated.

Review when:

- repeated failure
- system architecture changes
- tool access changes
- policies change
- role overlap grows

---

# 68. Routing Drift

Update `AGENT-ROUTING.md` when:

- ownership changes
- new agent added
- agent retired
- repeated reroutes
- recurring cross-agent conflict

---

# 69. Autonomy Regression

A regression occurs when the owner must resume work Claude previously handled reliably.

Record:

```yaml
autonomy_regression:
  capability:
  previous_state:
  current_state:
  cause:
  recovery_plan:
```

---

# 70. Human Override Rate

Track owner overrides separately from corrections.

An override may reflect a legitimate strategy change rather than autonomous failure.

---

# 71. Strategic Alignment

Measure percentage of autonomous missions traceable to:

- P0/P1 owner directive
- current constraint
- critical maintenance
- incident
- validated learning

Low alignment indicates autonomous busywork.

---

# 72. Constraint Alignment

The majority of improvement capacity should target the current constraint or prerequisites to solving it.

---

# 73. WIP Health

Track:

```yaml
wip:
  active_missions:
  active_tasks:
  active_experiments:
  tasks_per_agent:
  limit_breaches:
```

Too much WIP increases cycle time and coordination failures.

---

# 74. Stalled Work

A task is stalled when no meaningful progress occurs beyond its expected window.

Record:

```yaml
stalled:
  task_id:
  age:
  blocker:
  owner:
  next_action:
```

---

# 75. Retry Health

Track:

- retries per task
- same-failure retries
- retry cost
- eventual success

Repeated identical retries should trigger root-cause analysis.

---

# 76. Scheduler Health

Track:

- missed jobs
- failed jobs
- duplicate executions
- stale locks
- excessive retries
- long-running jobs
- jobs producing no value

---

# 77. Job Value Review

Every recurring job should periodically answer:

> What decision, protection, or outcome does this job enable?

Disable useless recurring work.

---

# 78. Alert Health

Track:

- actionable alerts
- false positives
- duplicate alerts
- owner-facing alerts
- auto-resolved alerts

High alert noise damages autonomy.

---

# 79. Owner Alert Precision

Prefer:

**few important alerts**

over:

**constant operational chatter**

---

# 80. Customer Outcome Link

Autonomy health should ultimately connect to 6S Success outcomes.

Examples:

- more successful Entryway resets
- higher quest completion
- lower friction
- stronger sustainment
- better product fit
- higher repeat engagement

Operational perfection without customer value is insufficient.

---

# 81. Revenue Link

Autonomy should support the strategic goal of building toward more than $20,000 monthly revenue, but revenue growth must remain linked to customer value, margin, trust, reliability, and governance.

---

# 82. Monthly Revenue Target

```yaml
business_target:
  monthly_revenue_usd: 20000
  interpretation: strategic_target
```

Do not treat this as current revenue.

---

# 83. Autonomy Dashboard Summary

Executive dashboard should show a compact block:

```text
AUTONOMY HEALTH       UNKNOWN
AUTONOMOUS COMPLETION UNKNOWN
TASK SUCCESS          UNKNOWN
CHANGE FAILURE        UNKNOWN
OWNER INTERRUPTIONS   UNKNOWN
AGENT COST            UNKNOWN
POLICY VIOLATIONS     UNKNOWN
STALE AGENTS          UNKNOWN
```

---

# 84. Detailed Dashboard Drill-Down

Allow drill-down into:

- agent scorecards
- failures
- costs
- routing
- deployments
- owner decisions
- policy events
- learning
- complexity

---

# 85. Weekly Autonomy Review

Automatically summarize:

1. missions completed
2. verified value
3. failures
4. rework
5. rollbacks
6. owner interruptions
7. routing errors
8. agent costs
9. policy violations
10. top autonomy improvement

---

# 86. Monthly Autonomy Review

Evaluate:

- Is autonomy increasing?
- Is quality improving?
- Is owner attention decreasing appropriately?
- Is cost justified?
- Are agents becoming simpler or more complex?
- Which agent needs improvement?
- Which agent should be retired?
- Which automation should be removed?
- What is the biggest autonomy constraint?

---

# 87. Autonomy Constraint

Just as the business has a primary constraint, the autonomous system should identify its own largest operating constraint.

Examples:

- poor measurement
- slow deployments
- weak routing
- excessive owner approvals
- unreliable agent
- high API cost
- missing tests
- stale system registry

---

# 88. One Autonomy Improvement at a Time

Do not constantly rewrite all agent prompts.

Select the highest-leverage autonomy constraint, improve it, measure, and standardize.

---

# 89. Autonomy Improvement Experiment

```yaml
autonomy_experiment:
  id:
  problem:
  baseline:
  change:
  primary_metric:
  guardrails:
  result:
  decision:
```

---

# 90. Example: Excessive Escalation

```text
Problem:
Agents ask owner for routine approval.

Root Cause:
Task contracts do not include authority.

Change:
Add explicit authority field from AUTONOMY.md.

Measure:
Routine owner interruptions per eligible task.

Guardrail:
Required high-risk escalations must not decrease.
```

---

# 91. Example: Duplicate Analysis

```text
Problem:
Growth, SEO, and Analytics independently analyze the same funnel.

Root Cause:
No accountable task owner.

Change:
Route funnel diagnosis to Analytics with Growth as support.

Measure:
Duplicate tool calls and cycle time.
```

---

# 92. Example: Deployment Failure

```text
Problem:
Changes repeatedly fail after deployment.

Root Cause:
Insufficient pre-deploy test coverage.

Change:
Strengthen release gate.

Measure:
Change failure rate and cycle time.

Guardrail:
Do not create excessive deployment latency.
```

---

# 93. Example: High Agent Cost

```text
Problem:
Agent cost increases without increased outcomes.

Root Cause:
Large repeated context and redundant discovery.

Change:
Use SYSTEM-REGISTRY and scoped context packages.

Measure:
Cost per successful mission.
```

---

# 94. Improvement Ownership

The orchestrator owns autonomy health.

Specialists provide domain evidence.

No specialist should independently rewrite the entire autonomous architecture.

---

# 95. Autonomy Health Job

Recommended recurring job:

```yaml
job:
  name: autonomy-health-review
  owner: orchestrator
  cadence: daily_summary_weekly_analysis
  mode: ANALYZE
  output:
    - health_status
    - anomalies
    - highest_priority_improvement
```

Actual schedule belongs in `SCHEDULER.md`.

---

# 96. Daily Checks

Lightweight:

- failed jobs
- failed deployments
- critical policy violations
- stale locks
- agent failures
- owner interruption anomalies
- cost anomaly

---

# 97. Weekly Checks

Deeper:

- agent success
- routing accuracy
- rework
- cost
- cycle time
- duplicate work
- documentation drift
- learning yield
- complexity

---

# 98. Monthly Checks

Strategic:

- autonomy maturity
- agent roster
- system simplification
- owner experience
- economic value
- governance effectiveness

---

# 99. Data Sources

Prefer authoritative sources:

- Mission Control
- scheduler
- GitHub
- deployment system
- VPS/Docker
- analytics
- commerce
- cost systems
- incident records
- decisions
- agent task records

Do not manually invent scores.

---

# 100. Autonomy Event Schema

Long term, record structured events:

```yaml
event:
  timestamp:
  mission_id:
  task_id:
  agent_id:
  event_type:
  status:
  duration:
  cost:
  owner_intervention:
  failure_class:
  evidence_ref:
```

This enables real measurement.

---

# 101. Event Types

Potential:

- task_started
- task_completed
- task_failed
- task_rerouted
- owner_escalated
- owner_corrected
- deployment_started
- deployment_verified
- rollback
- policy_violation
- agent_disabled
- learning_recorded

---

# 102. Machine-Readable Companion

Long term consider:

```text
autonomy-health.yaml
```

or a database-backed event/metrics layer.

This Markdown file defines semantics and policy.

---

# 103. Health Thresholds

Do not establish arbitrary numerical thresholds without baseline evidence.

Start with:

```yaml
thresholds:
  source: baseline_required
```

Then set thresholds from observed system performance and business risk.

---

# 104. Baseline Period

Before optimizing autonomy metrics:

1. instrument events
2. collect baseline
3. identify normal variation
4. establish useful thresholds
5. improve highest-impact defect

---

# 105. Gaming Prevention

Never improve a metric by degrading the underlying system.

Examples:

- fewer escalations by hiding risks
- higher success by avoiding difficult tasks
- lower cost by skipping verification
- fewer rollbacks by making fewer useful changes
- faster cycle time by eliminating measurement

Use balanced guardrails.

---

# 106. Balanced Scorecard

Every major autonomy optimization should consider:

```text
Effectiveness
Reliability
Owner Attention
Cost
Risk
Learning
```

---

# 107. Quality Gate

An autonomy improvement is not successful if it:

- increases security risk
- reduces recovery ability
- increases customer defects
- hides unknowns
- bypasses owner authority
- damages measurement integrity

---

# 108. Current Bootstrap State

Until actual autonomous operations are measured:

```yaml
autonomy_health:
  overall: UNKNOWN
  effectiveness: UNKNOWN
  reliability: UNKNOWN
  quality: UNKNOWN
  routing: UNKNOWN
  owner_attention: UNKNOWN
  speed: UNKNOWN
  cost_efficiency: UNKNOWN
  governance: UNKNOWN
  learning: UNKNOWN
  hygiene: UNKNOWN
  simplicity: UNKNOWN

baseline:
  status: NOT_ESTABLISHED

primary_autonomy_constraint:
  status: UNKNOWN

agent_scorecards:
  status: NOT_ESTABLISHED
```

This is the correct starting state.

---

# 109. First Autonomy Health Mission

After core autonomous operations are running:

1. verify agent registry
2. instrument task lifecycle
3. instrument routing
4. instrument owner escalations
5. instrument deployments
6. instrument failures/retries
7. instrument agent/tool cost where available
8. instrument policy events
9. collect baseline
10. calculate first scorecards
11. identify largest autonomy constraint
12. create one bounded improvement
13. measure
14. standardize if successful
15. surface results on executive dashboard

---

# 110. Recommended Initial Metrics

Start with a small set:

```yaml
initial_metrics:
  - autonomous_completion_rate
  - task_success_rate
  - first_pass_success_rate
  - change_failure_rate
  - owner_interruptions
  - reroute_rate
  - duplicate_work_rate
  - cost_per_successful_mission
  - policy_violations
  - production_verification_rate
  - mission_cycle_time
  - learning_yield
```

Add metrics only when they support decisions.

---

# 111. Autonomy Maturity Model

## Level 0: Assisted

Owner coordinates most work.

## Level 1: Automated Tasks

Claude performs isolated tasks.

## Level 2: Routed Specialists

Orchestrator assigns bounded work to specialist agents.

## Level 3: Managed Autonomy

Mission Control, routing, governance, verification, and dashboard are integrated.

## Level 4: Self-Improving Autonomy

The system measures its own failures, cost, routing, owner attention, and outcomes and improves its operating model.

## Level 5: Executive Autonomy

The owner primarily sets strategic direction and reviews outcomes. The autonomous organization manages routine execution, detects its own operating constraints, improves itself safely, and demonstrates measurable customer and business value.

---

# 112. Non-Negotiable Rules

Claude and subagents must not:

- optimize agent activity instead of outcomes
- fabricate health metrics
- hide UNKNOWN values
- suppress required owner escalation to improve autonomy scores
- avoid difficult work to improve success rate
- skip tests to improve cycle time
- skip verification to reduce cost
- retry identical failures indefinitely
- tolerate repeated routing errors without improvement
- tolerate recurring policy violations
- keep useless recurring jobs
- keep redundant agents solely because they exist
- add complexity without measurable need
- claim business value without evidence
- treat token count as the only cost
- expose secrets in health reporting
- store private chain-of-thought
- automatically broaden agent authority because performance is good
- rewrite core governance merely to improve metrics

---

# 113. Final Principle

A truly autonomous system does more than operate the website.

It evaluates **how well it is operating itself**.

It should continuously ask:

**Are we working on the right problem?**

**Did we route it to the right agent?**

**Did the agent succeed?**

**Did we create measurable value?**

**Did we needlessly interrupt the owner?**

**Did we introduce risk?**

**Did we spend efficiently?**

**Did we learn?**

**Did we simplify?**

**Can we perform this class of work better next time?**

The desired trajectory is:

```text
More Verified Customer Value
More Sustainable Revenue
More Reliable Autonomous Completion
Fewer Routine Owner Interruptions
Less Rework
Lower Coordination Waste
Better Learning
Controlled Cost
Controlled Risk
Simpler Architecture
```

That is the purpose of `AUTONOMY-HEALTH.md`.
