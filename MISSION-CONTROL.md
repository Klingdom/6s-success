# 6S Success Mission Control

> Live operational command document for the autonomous 6S Success system. This file is the concise, continuously maintained handoff between operating cycles, specialist agents, deployments, experiments, incidents, and the executive dashboard.

## 1. Purpose

`MISSION-CONTROL.md` answers one question:

> What is the autonomous 6S Success system doing right now, why is it doing it, what is the evidence, and what happens next?

This is not a strategy document, backlog, log archive, or dashboard specification.

It is the **current operational picture**.

At any moment, Claude should be able to read this file and quickly understand:

- current business/customer state
- current system health
- primary constraint
- current mission
- active work
- assigned agents
- active experiment
- latest release
- blockers
- incidents
- risks
- owner decisions
- next action
- when the state was last verified

---

# 2. Relationship to Other Files

Use each file for its intended purpose.

| File | Primary Question |
|---|---|
| `OWNER-DIRECTIVES.md` | What does the owner want? |
| `AUTONOMY.md` | What is Claude allowed to do? |
| `SYSTEM-REGISTRY.md` | What systems actually exist? |
| `STATUS.md` | What is the broader current state? |
| `MISSION-CONTROL.md` | What are we doing right now? |
| `BACKLOG.md` | What work could/should happen later? |
| `EXPERIMENTS.md` | What experiments exist and what did they show? |
| `DECISIONS.md` | What important decisions were made? |
| `LEARNINGS.md` | What durable lessons should persist? |
| `EXECUTIVE-DASHBOARD.md` | What should the owner see? |
| `AUTONOMOUS-OPERATING-LOOP.md` | How does the whole autonomous loop operate? |

Do not duplicate large amounts of information across these files.

---

# 3. Core Principle

**Mission Control should describe the present, not preserve the entire past.**

History belongs in Git, experiment records, release records, decisions, incidents, and learnings.

Keep this file concise enough to be read at the start of every meaningful autonomous cycle.

---

# 4. Update Rule

Update Mission Control whenever one of these materially changes:

- primary constraint
- current mission
- mission status
- active agent assignment
- active experiment
- production health
- incident state
- deployment state
- material blocker
- owner decision requirement
- next action
- business/customer baseline used for current work

Do not update it for trivial internal steps.

---

# 5. Current-State Vocabulary

Use:

- `GREEN`
- `YELLOW`
- `RED`
- `UNKNOWN`

For work status use:

- `QUEUED`
- `ACTIVE`
- `BLOCKED`
- `WAITING`
- `VERIFYING`
- `MEASURING`
- `COMPLETED`
- `CANCELLED`

---

# 6. Freshness

Every live section should identify when it was last verified.

Example:

```yaml
last_verified: 2026-08-14T16:00:00-06:00
```

If the source is stale, say so.

Never present stale operational state as current.

---

# 7. Mission Control Header

Maintain:

```yaml
mission_control:
  status: UNKNOWN
  cycle_id: UNKNOWN
  current_stage: UNKNOWN
  last_updated: UNKNOWN
  last_verified: UNKNOWN
  next_scheduled_review: UNKNOWN
```

---

# 8. Executive Snapshot

This should be the fastest human-readable section.

```text
OVERALL STATUS: UNKNOWN

BUSINESS TARGET
> $20,000/month revenue

PRIMARY CONSTRAINT
UNKNOWN

CURRENT MISSION
UNKNOWN

CUSTOMER OUTCOME
UNKNOWN

PRODUCTION
UNKNOWN

AUTONOMOUS WORK
UNKNOWN

ACTIVE EXPERIMENT
UNKNOWN

OWNER DECISIONS
UNKNOWN

NEXT ACTION
Discover and verify current system state.
```

Do not fill unknown fields with invented values.

---

# 9. Current Owner Direction

Mission Control should summarize only the active directives that affect current execution.

Current strategic emphasis:

```yaml
owner_direction:
  primary_target: "Build toward >$20,000 monthly revenue"
  validation_focus: Entryway
  customer_model: "Desired Function → Root Cause → Quest → Outcome"
  growth_model: constraint_driven
  autonomy_goal: minimize_routine_owner_coordination
  reversible_experiment_posture: aggressive_within_governance
  infrastructure_risk_posture: conservative
```

Canonical directives remain in `OWNER-DIRECTIVES.md`.

---

# 10. System Health

```yaml
system_health:
  overall: UNKNOWN
  production: UNKNOWN
  commerce: UNKNOWN
  database: UNKNOWN
  github: UNKNOWN
  vps: UNKNOWN
  docker: UNKNOWN
  scheduler: UNKNOWN
  analytics: UNKNOWN
  backups: UNKNOWN
  security: UNKNOWN
  cost_controls: UNKNOWN
  last_verified: UNKNOWN
```

---

# 11. Health Precedence

Before normal growth work, resolve material issues in this order:

1. customer/human safety
2. security/privacy
3. data integrity
4. production
5. commerce
6. backup/recovery
7. runaway cost
8. measurement
9. customer journey
10. growth optimization

---

# 12. Business State

```yaml
business_state:
  monthly_revenue_target_usd: 20000
  revenue_mtd_usd: UNKNOWN
  projected_month_revenue_usd: UNKNOWN
  contribution_margin_mtd_usd: UNKNOWN
  orders_mtd: UNKNOWN
  refunds_mtd: UNKNOWN
  qualified_visitors_mtd: UNKNOWN
  last_verified: UNKNOWN
```

Target is known strategy. Actuals require verified sources.

---

# 13. Customer State

```yaml
customer_state:
  successful_micro_zone_outcomes_mtd: UNKNOWN
  entryway_qualified_visitors: UNKNOWN
  entryway_diagnoses: UNKNOWN
  entryway_quest_starts: UNKNOWN
  entryway_quest_completions: UNKNOWN
  entryway_successful_outcomes: UNKNOWN
  repeat_quest_rate: UNKNOWN
  last_verified: UNKNOWN
```

---

# 14. Primary Constraint

Only one primary customer/business constraint should normally be active.

```yaml
primary_constraint:
  id: UNKNOWN
  layer: UNKNOWN
  description: UNKNOWN
  metric: UNKNOWN
  baseline: UNKNOWN
  evidence: UNKNOWN
  confidence: UNKNOWN
  selected_at: UNKNOWN
```

Examples of layers:

- discovery
- landing
- desired_function
- diagnosis
- quest_start
- quest_completion
- outcome
- product_fit
- checkout
- retention
- margin
- measurement
- technical

---

# 15. Why This Constraint

Record concise evidence, not hidden reasoning.

```yaml
constraint_evidence:
  observation: UNKNOWN
  customer_impact: UNKNOWN
  business_impact: UNKNOWN
  supporting_metrics: []
  competing_constraints: []
```

---

# 16. Current Mission

There should normally be one primary mission.

```yaml
current_mission:
  mission_id: UNKNOWN
  title: UNKNOWN
  objective: UNKNOWN
  directive_refs: []
  constraint_ref: UNKNOWN
  status: UNKNOWN
  started_at: UNKNOWN
  target_completion: UNKNOWN
  owner_agent: UNKNOWN
  risk: UNKNOWN
```

---

# 17. Mission Hypothesis

For improvement work:

```yaml
hypothesis:
  statement: UNKNOWN
  primary_metric: UNKNOWN
  expected_direction: UNKNOWN
  guardrails: []
```

Example structure:

> If we simplify desired-function selection for qualified Entryway visitors, more visitors will begin a relevant quest without reducing successful outcome rate.

This example is illustrative.

---

# 18. Mission Definition of Done

```yaml
definition_of_done:
  implementation_complete: false
  required_tests_passed: false
  production_verified: false
  instrumentation_verified: false
  measurement_window_complete: false
  result_recorded: false
  learning_recorded: false
  dashboard_updated: false
```

Not all tasks require every item, but material improvement missions usually do.

---

# 19. Active Work

Keep this small.

```yaml
active_work:
  - task_id: UNKNOWN
    title: UNKNOWN
    owner_agent: UNKNOWN
    mode: UNKNOWN
    status: UNKNOWN
    started_at: UNKNOWN
    expected_output: UNKNOWN
    blocking: []
```

Modes:

- `ANALYZE`
- `RECOMMEND`
- `IMPLEMENT`
- `TEST`
- `DEPLOY`
- `MONITOR`

---

# 20. Work-in-Progress Limit

Mission Control should reflect the WIP limits defined by scheduler/governance.

Do not create a long active-task list merely because many agents are available.

Prefer:

**few tasks → verified completion → learning → next tasks**

---

# 21. Agent Assignments

```yaml
agent_assignments:
  orchestrator:
    status: UNKNOWN
    current_task: UNKNOWN

  github_manager:
    status: UNKNOWN
    current_task: UNKNOWN

  hostinger_vps_docker_manager:
    status: UNKNOWN
    current_task: UNKNOWN

  devops_sre:
    status: UNKNOWN
    current_task: UNKNOWN

  security:
    status: UNKNOWN
    current_task: UNKNOWN

  analytics:
    status: UNKNOWN
    current_task: UNKNOWN

  seo_aeo:
    status: UNKNOWN
    current_task: UNKNOWN

  content:
    status: UNKNOWN
    current_task: UNKNOWN

  customer_journey:
    status: UNKNOWN
    current_task: UNKNOWN

  quest:
    status: UNKNOWN
    current_task: UNKNOWN

  product:
    status: UNKNOWN
    current_task: UNKNOWN

  commerce:
    status: UNKNOWN
    current_task: UNKNOWN

  growth:
    status: UNKNOWN
    current_task: UNKNOWN
```

Use actual configured agent names and remove nonexistent agents after discovery.

---

# 22. Agent Handoff Contract

When one agent hands work to another, record only what the next agent needs:

```yaml
handoff:
  from_agent:
  to_agent:
  task_id:
  completed:
  evidence:
  remaining:
  required_action:
  constraints:
```

Do not pass hidden chain-of-thought.

---

# 23. Active Experiment

```yaml
active_experiment:
  experiment_id: UNKNOWN
  title: UNKNOWN
  hypothesis: UNKNOWN
  primary_metric: UNKNOWN
  guardrails: []
  started_at: UNKNOWN
  decision_rule: UNKNOWN
  status: UNKNOWN
  current_result: UNKNOWN
```

Canonical experiment details belong in `EXPERIMENTS.md`.

---

# 24. Experiment State

Use:

- `DESIGNING`
- `READY`
- `RUNNING`
- `MEASURING`
- `WINNER`
- `LOSER`
- `INCONCLUSIVE`
- `STOPPED`

Do not call an experiment a winner merely because an early metric moved favorably.

---

# 25. Latest Release

```yaml
latest_release:
  release_id: UNKNOWN
  environment: production
  commit: UNKNOWN
  pull_request: UNKNOWN
  deployed_at: UNKNOWN
  deployed_by: UNKNOWN
  smoke_test: UNKNOWN
  health: UNKNOWN
  rollback_ready: UNKNOWN
```

---

# 26. Release in Progress

If a release is active:

```yaml
release_in_progress:
  status: UNKNOWN
  task_id: UNKNOWN
  deployment_lock: UNKNOWN
  started_at: UNKNOWN
  current_step: UNKNOWN
```

Only one production release should normally be active.

---

# 27. GitHub Operational State

```yaml
github_state:
  repository_id: UNKNOWN
  default_branch: UNKNOWN
  latest_commit: UNKNOWN
  open_pull_requests: UNKNOWN
  failed_required_workflows: UNKNOWN
  critical_security_alerts: UNKNOWN
  deployment_relationship_verified: UNKNOWN
  last_verified: UNKNOWN
```

Detailed repository topology belongs in `SYSTEM-REGISTRY.md`.

---

# 28. Hostinger VPS / Docker State

```yaml
runtime_state:
  host_id: UNKNOWN
  host_health: UNKNOWN
  cpu: UNKNOWN
  memory: UNKNOWN
  disk: UNKNOWN
  containers_running: UNKNOWN
  containers_unhealthy: UNKNOWN
  restart_anomalies: UNKNOWN
  unexpected_public_ports: UNKNOWN
  last_verified: UNKNOWN
```

---

# 29. Scheduler State

```yaml
scheduler_state:
  status: UNKNOWN
  heartbeat: UNKNOWN
  active_jobs: UNKNOWN
  failed_jobs_24h: UNKNOWN
  stale_locks: UNKNOWN
  global_pause: UNKNOWN
  last_verified: UNKNOWN
```

---

# 30. Backup / Recovery State

```yaml
recovery_state:
  latest_backup: UNKNOWN
  latest_backup_status: UNKNOWN
  latest_restore_test: UNKNOWN
  restore_test_status: UNKNOWN
  rollback_readiness: UNKNOWN
  last_verified: UNKNOWN
```

A backup without a restore test is not full recovery confidence.

---

# 31. Security State

```yaml
security_state:
  status: UNKNOWN
  critical_findings: UNKNOWN
  high_findings: UNKNOWN
  exposed_secrets: UNKNOWN
  dependency_criticals: UNKNOWN
  suspicious_access: UNKNOWN
  last_verified: UNKNOWN
```

Never include secret values.

---

# 32. Cost State

```yaml
cost_state:
  infrastructure_mtd_usd: UNKNOWN
  ai_api_mtd_usd: UNKNOWN
  saas_mtd_usd: UNKNOWN
  commerce_fees_mtd_usd: UNKNOWN
  approved_acquisition_mtd_usd: UNKNOWN
  cost_anomaly: UNKNOWN
  last_verified: UNKNOWN
```

---

# 33. Blockers

Only current blockers:

```yaml
blockers:
  - blocker_id:
    description:
    blocks:
    owner:
    first_seen:
    next_action:
    escalation_required:
```

Resolved blockers should be removed from live Mission Control after their resolution is recorded elsewhere.

---

# 34. Risks

Only material current risks:

```yaml
risks:
  - risk_id:
    category:
    description:
    probability:
    impact:
    mitigation:
    owner:
    status:
```

---

# 35. Incidents

```yaml
incidents:
  - incident_id:
    severity:
    description:
    customer_impact:
    started_at:
    status:
    mitigation:
    owner:
    next_update:
```

If there are no active incidents:

```yaml
incidents: []
```

Do not leave resolved incidents here indefinitely.

---

# 36. Owner Decisions Required

Keep this highly visible.

```yaml
owner_decisions_required:
  - decision_id:
    question:
    why_now:
    recommendation:
    alternatives:
    cost:
    risk:
    deadline:
```

If none:

```yaml
owner_decisions_required: []
```

---

# 37. Do Not Manufacture Decisions

If Claude already has authority, act.

Do not create an owner decision merely to transfer responsibility.

---

# 38. Waiting State

When work cannot proceed:

```yaml
waiting_on:
  type:
  dependency:
  since:
  next_check:
  can_do_other_work:
```

Potential types:

- owner
- external_provider
- experiment_data
- deployment
- DNS
- vendor
- inventory
- scheduled_window

---

# 39. Next Action

Mission Control must always identify the next meaningful action.

```yaml
next_action:
  action: UNKNOWN
  owner_agent: UNKNOWN
  mode: UNKNOWN
  trigger: UNKNOWN
  authority: UNKNOWN
```

If no action is warranted:

```yaml
next_action:
  action: NO_ACTION
  reason: UNKNOWN
  next_check: UNKNOWN
```

---

# 40. Next Three

Optionally maintain at most three near-term steps:

```yaml
next_three:
  - order: 1
    action:
  - order: 2
    action:
  - order: 3
    action:
```

Do not turn this into the backlog.

---

# 41. Recently Completed

Keep only the latest high-value completions.

```yaml
recently_completed:
  - task_id:
    completed_at:
    action:
    evidence:
    result_status:
```

Limit to roughly 3–7 items.

---

# 42. Action vs Outcome

Always distinguish:

```yaml
action:
result:
```

Example:

```yaml
action: Simplified Entryway desired-function selection.
result: Measurement window still open.
```

Do not claim success before outcome evidence exists.

---

# 43. Latest Learning

Mission Control may show one or two operationally relevant learnings.

```yaml
latest_learning:
  observation:
  implication:
  learning_ref:
```

Durable history belongs in `LEARNINGS.md`.

---

# 44. Current Measurement Window

```yaml
measurement_window:
  metric:
  baseline_period:
  test_period:
  minimum_evidence:
  current_status:
  expected_decision_at:
```

This helps prevent premature optimization.

---

# 45. Data Quality

```yaml
data_quality:
  overall: UNKNOWN
  stale_sources: []
  failed_collectors: []
  conflicting_metrics: []
  instrumentation_gaps: []
```

If critical data is invalid, the current mission may need to become measurement repair.

---

# 46. Current Growth Funnel

Only populate with verified data.

```yaml
growth_funnel:
  qualified_visitors: UNKNOWN
  desired_function_started: UNKNOWN
  diagnoses_completed: UNKNOWN
  quest_starts: UNKNOWN
  quest_completions: UNKNOWN
  successful_outcomes: UNKNOWN
  purchases: UNKNOWN
  repeat_quests: UNKNOWN
```

---

# 47. Current Entryway Funnel

```yaml
entryway_funnel:
  visitors: UNKNOWN
  desired_function_started: UNKNOWN
  desired_function_completed: UNKNOWN
  root_cause_diagnoses: UNKNOWN
  quest_starts: UNKNOWN
  quest_completions: UNKNOWN
  successful_outcomes: UNKNOWN
  product_recommendations: UNKNOWN
  purchases: UNKNOWN
```

---

# 48. Current Product Signal

```yaml
product_signal:
  strongest_validated_need: UNKNOWN
  strongest_product: UNKNOWN
  strongest_no_purchase_solution: UNKNOWN
  highest_refund_issue: UNKNOWN
  highest_margin_opportunity: UNKNOWN
```

---

# 49. Current Content / SEO Signal

```yaml
discovery_signal:
  top_qualified_entry_page: UNKNOWN
  top_search_opportunity: UNKNOWN
  top_aeo_opportunity: UNKNOWN
  content_gap: UNKNOWN
  technical_search_issue: UNKNOWN
```

---

# 50. Current Customer Feedback Signal

```yaml
customer_feedback:
  dominant_positive_signal: UNKNOWN
  dominant_friction: UNKNOWN
  top_request: UNKNOWN
  evidence_source: UNKNOWN
```

Do not infer broad customer sentiment from one anecdote.

---

# 51. Operational Timeline

Mission Control may maintain a very short timeline for the current mission:

```yaml
timeline:
  - at:
    event:
    ref:
```

Limit this to current-cycle relevance.

---

# 52. Cycle ID

Use a stable identifier such as:

```text
MC-2026-08-14-001
```

Exact format may be automated.

---

# 53. Cycle Start

At the beginning of an operating cycle:

1. read active owner directives
2. read Mission Control
3. check global pause
4. validate critical health
5. validate relevant data freshness
6. inspect active mission
7. determine whether mission continues
8. inspect blockers/incidents
9. select next action
10. update cycle metadata

---

# 54. Cycle End

Before ending a meaningful cycle:

1. record completed action
2. record evidence
3. update mission status
4. update release/experiment state
5. update blockers/risks
6. update next action
7. update dashboard-facing summary
8. set next review/check
9. release locks

---

# 55. Mission Change

Do not change missions merely because another idea appears interesting.

Change when:

- mission completes
- mission fails
- higher-priority incident occurs
- evidence changes the primary constraint
- owner overrides
- stop condition occurs
- mission becomes blocked long enough that parallel safe work is justified

---

# 56. Mission Completion

When complete:

```yaml
mission_result:
  status:
  primary_metric_result:
  guardrail_result:
  technical_result:
  business_result:
  customer_result:
  learning_ref:
  standardized:
```

Then select the next constraint.

---

# 57. Mission Failure

Failure should be explicit.

```yaml
mission_result:
  status: FAILED
  reason:
  rollback:
  evidence:
  learning_ref:
```

Failure is useful when it generates learning.

---

# 58. Mission Cancellation

Use when strategy or context changes.

```yaml
status: CANCELLED
reason:
```

Do not relabel cancellation as success.

---

# 59. Constraint Change

When constraint changes:

```yaml
previous_constraint:
new_constraint:
evidence:
changed_at:
```

Record durable analysis elsewhere if significant.

---

# 60. Incident Preemption

A critical incident can preempt the current mission.

Mission Control should show:

```yaml
mission:
  status: PAUSED
  paused_for: incident-id
```

Resume only after safe recovery.

---

# 61. Global Pause

If autonomy is paused:

```yaml
autonomy:
  global_pause: true
  reason:
  activated_at:
  activated_by:
  allowed_activity:
    - monitoring
    - backups
    - incident_response
    - owner_access
```

Follow canonical governance.

---

# 62. Deployment Lock

Mission Control should expose deployment lock state:

```yaml
deployment_lock:
  status:
  holder:
  task_id:
  acquired_at:
  expires_or_timeout:
```

---

# 63. Entity Locks

For cross-agent work, optionally track material entity locks:

```yaml
entity_locks:
  - resource:
    holder:
    task_id:
    acquired_at:
```

Do not use this file as the actual locking mechanism unless the architecture explicitly does so.

---

# 64. Autonomous Work Summary

Owner-facing summary:

```yaml
autonomous_work:
  active_tasks: UNKNOWN
  active_agents: UNKNOWN
  blocked_tasks: UNKNOWN
  failed_jobs_24h: UNKNOWN
  completed_high_value_24h: UNKNOWN
```

---

# 65. Current Mission Narrative

Maintain a short human-readable narrative:

> Claude is currently validating the 6S Success production environment and measurement stack before selecting the first evidence-based Entryway growth constraint. No revenue, funnel, or production-health assumptions should be treated as verified until discovery is complete.

Update this narrative when state changes.

---

# 66. Owner Brief Format

When Mission Control feeds the dashboard, generate:

## Status

One sentence.

## Current Constraint

One sentence.

## Claude Mission

One sentence.

## Latest Meaningful Change

One sentence.

## Risk

One sentence if material.

## Decision Needed

One sentence if required.

Keep the owner view concise.

---

# 67. Daily Handoff

At the end of a daily autonomous operating period:

```yaml
daily_handoff:
  date:
  completed:
  current_state:
  unresolved:
  overnight_jobs:
  next_priority:
  owner_attention:
```

---

# 68. Weekly Handoff

Weekly Mission Control should roll durable material into:

- `STATUS.md`
- `DECISIONS.md`
- `LEARNINGS.md`
- `EXPERIMENTS.md`
- `BACKLOG.md`

Then prune stale live detail.

---

# 69. Pruning Rule

Remove from Mission Control when no longer operationally relevant:

- completed old tasks
- resolved incidents
- closed decisions
- old releases
- old experiment details
- obsolete blockers

Git history preserves changes.

---

# 70. No Log Dump

Do not paste:

- Docker logs
- CI logs
- analytics exports
- stack traces
- long agent outputs

Link/reference them through appropriate systems.

Mission Control contains conclusions and evidence references.

---

# 71. No Hidden Reasoning

Record:

- observation
- evidence
- decision
- action
- result

Do not store private chain-of-thought.

---

# 72. Machine-Readable Companion

Long term, a structured companion may be useful:

```text
mission-control.yaml
```

Potential purpose:

- scheduler state
- dashboard API
- agent coordination
- automated validation

`MISSION-CONTROL.md` remains the readable operational specification/state summary.

---

# 73. Validation

Automated checks should eventually validate:

- one primary mission
- one primary constraint
- valid status values
- valid agent references
- valid directive references
- no secret-looking values
- no duplicate task IDs
- no stale deployment locks
- required timestamps
- no completed tasks marked active

---

# 74. Dashboard Integration

`EXECUTIVE-DASHBOARD.md` should consume Mission Control for:

- current mission
- current constraint
- autonomous work
- blockers
- risks
- owner decisions
- latest release
- next action

The dashboard should retrieve actual business metrics from their canonical metrics layer, not blindly trust manually copied values here.

---

# 75. Scheduler Integration

`SCHEDULER.md` should use Mission Control to avoid:

- duplicate work
- conflicting missions
- starting work during global pause
- exceeding WIP
- repeated owner escalation
- launching new experiments before current measurement completes

---

# 76. GitHub Manager Integration

GitHub Manager should update/reference:

- active task
- PR
- commit
- workflow status
- release lineage

Do not let Mission Control become a second GitHub.

---

# 77. VPS Manager Integration

VPS/Docker Manager should update/reference:

- runtime health
- deployment state
- container anomaly
- capacity risk
- recovery readiness

Detailed runtime inventory belongs in `SYSTEM-REGISTRY.md`.

---

# 78. Analytics Agent Integration

Analytics agent should supply:

- baseline
- current metric
- data quality
- constraint evidence
- experiment evidence

---

# 79. Growth Agent Integration

Growth agent may recommend constraints and experiments.

The orchestrator decides the primary constraint.

---

# 80. Security Agent Integration

Critical security findings should immediately update Mission Control and may preempt the current mission.

---

# 81. Commerce Agent Integration

Commerce failures affecting orders, payments, fulfillment, or refunds should be visible here when material.

---

# 82. Cost Agent Integration

Runaway or anomalous spend should become a visible risk or incident.

---

# 83. Current Bootstrap State

The following is intentionally conservative because the live GitHub/VPS/business systems have not been verified from this document alone.

```yaml
mission_control:
  status: UNKNOWN
  cycle_id: BOOTSTRAP
  current_stage: DISCOVERY
  last_updated: UNKNOWN
  last_verified: UNKNOWN

overall_status: UNKNOWN

business:
  monthly_revenue_target_usd: 20000
  revenue_mtd_usd: UNKNOWN
  contribution_margin_mtd_usd: UNKNOWN

customer:
  validation_focus: Entryway
  successful_micro_zone_outcomes: UNKNOWN
  entryway_funnel: UNKNOWN

primary_constraint:
  description: UNKNOWN
  reason: Insufficient verified operating and customer data

current_mission:
  title: Establish Verified Autonomous Operating Baseline
  objective: >
    Verify the actual GitHub, Hostinger VPS/Docker, production,
    analytics, commerce, scheduler, backup, security, agent,
    and Entryway customer-journey state before selecting the
    first evidence-based improvement constraint.
  status: QUEUED
  owner_agent: orchestrator

system_health:
  production: UNKNOWN
  github: UNKNOWN
  vps: UNKNOWN
  docker: UNKNOWN
  commerce: UNKNOWN
  analytics: UNKNOWN
  backups: UNKNOWN
  security: UNKNOWN

active_experiment:
  status: UNKNOWN

owner_decisions_required: []

next_action:
  action: Bootstrap SYSTEM-REGISTRY and verify current operating state
  owner_agent: orchestrator
  mode: ANALYZE
```

---

# 84. First Mission Control Mission

Once Claude Code has legitimate project access:

1. load `OWNER-DIRECTIVES.md`
2. load `AUTONOMY.md`
3. load `SYSTEM-REGISTRY.md`
4. load `AUTONOMOUS-OPERATING-LOOP.md`
5. inspect repository and agent configuration
6. verify GitHub
7. verify Hostinger VPS/Docker
8. verify production
9. verify scheduler
10. verify analytics
11. verify commerce
12. verify backups
13. verify security baseline
14. verify cost sources
15. verify Entryway implementation
16. verify customer funnel instrumentation
17. populate `SYSTEM-REGISTRY.md`
18. populate current Mission Control state
19. identify the primary constraint
20. define the first bounded mission
21. assign specialist agents
22. execute through normal controls
23. verify
24. measure
25. update dashboard

Do not begin by redesigning the entire site.

---

# 85. First Mission Selection Rule

After bootstrap, choose the first mission using:

```text
Critical Health
→ Measurement Integrity
→ Entryway Customer Outcome Constraint
→ Commerce Constraint
→ Growth Constraint
→ Expansion
```

---

# 86. Example Mature Mission Control

Illustrative only:

```text
6S SUCCESS MISSION CONTROL

STATUS
GREEN

TARGET
>$20K/month

PRIMARY CONSTRAINT
Entryway diagnosis → quest-start conversion

CURRENT MISSION
Reduce friction in desired-function selection.

OWNER AGENT
Customer Journey Agent

ACTIVE SUPPORT
Analytics Agent
Quest Agent
GitHub Manager

EXPERIMENT
ENTRYWAY-DF-004
RUNNING

PRODUCTION
Healthy
Release abc123

RISKS
None material

OWNER DECISIONS
None

NEXT ACTION
Continue measurement until decision threshold is reached.
```

Never use illustrative values as live state.

---

# 87. Mission Control Maturity Model

## Level 0 — Chat Handoff

Current work exists mostly in conversation history.

## Level 1 — Current Mission

One mission and next action are documented.

## Level 2 — Coordinated

Agents, releases, experiments, blockers, and health share one operational picture.

## Level 3 — Verified

Mission Control is refreshed from authoritative systems.

## Level 4 — Autonomous

Scheduler and orchestrator use Mission Control to coordinate work without duplicate/conflicting execution.

## Level 5 — Continuous Improvement Command System

Mission Control becomes the continuously updated operational brainstem connecting owner direction, verified state, constraints, specialist agents, experiments, GitHub, production, measurements, learning, and the executive dashboard.

---

# 88. Non-Negotiable Rules

Claude and subagents must not:

- use Mission Control as a giant historical log
- fabricate current state
- hide UNKNOWN values
- list dozens of active priorities
- maintain multiple competing primary missions
- allow every specialist to choose the global constraint
- treat deployment as successful outcome
- hide failed work
- hide incidents
- hide owner decisions
- leave stale deployment locks
- copy secrets into this file
- paste large raw logs
- store private chain-of-thought
- keep resolved operational noise indefinitely
- change owner strategy from this file
- bypass `AUTONOMY.md`
- treat this file as more authoritative than live runtime state for facts
- let live runtime state override governance

---

# 89. Final Principle

The autonomous system needs a reliable shift handoff.

At all times, Claude should be able to answer:

**What is happening?**

**Is the system healthy?**

**What does the owner currently care about?**

**What is the biggest constraint?**

**What mission are we running?**

**Which agent owns it?**

**What experiment is active?**

**What changed in production?**

**What evidence do we have?**

**What is blocked?**

**What is at risk?**

**Does the owner need to decide anything?**

**What happens next?**

If those answers require reconstructing dozens of chats, Git commits, Docker logs, agent transcripts, and analytics screens, the autonomous system is not operationally mature.

`MISSION-CONTROL.md` provides the live operational picture that keeps the entire system aligned from one cycle to the next.
