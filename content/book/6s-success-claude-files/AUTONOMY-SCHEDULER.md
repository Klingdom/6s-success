# 6S Success Autonomy Scheduler

> Canonical scheduling, recurring-work, wake-up, and autonomous operating-loop standard for the 6S Success Claude Code organization.

## 1. Purpose

`AUTONOMY-SCHEDULER.md` defines when the autonomous organization wakes up, what it may inspect or execute, how recurring work is prioritized, and how runaway autonomous activity is prevented.

```text
TIME / CONDITION
      ↓
SCHEDULE
      ↓
AUTHORIZED JOB
      ↓
ORCHESTRATOR
      ↓
MISSION / TASK
      ↓
SPECIALIST AGENT
      ↓
VERIFY → EVENT → MEASURE → LEARN
```

A schedule is not permission. Every run remains subject to governance, trust level, budget, environment, and approval rules.

## 2. Core Principle

**Wake Claude when useful, not merely because time passed.**

Bad:
`Every hour, ask every agent to find something to improve.`

Better:
`Every hour, perform lightweight production-health checks. Route bounded investigation only when a meaningful anomaly exists.`

## 3. Responsibilities

The scheduler may coordinate production health, GitHub and VPS/Docker checks, backups, security, analytics freshness, business KPIs, customer outcomes, experiments, SEO/AEO discovery, content freshness, product and quest reviews, mission checkpoints, agent evaluations, autonomy health, costs, executive reporting, and continuous improvement.

## 4. Scheduler vs Orchestrator

The Scheduler answers: **When should work be considered?**

The Orchestrator answers: **What should happen, who should do it, and is it authorized?**

Do not encode business strategy in cron expressions.

## 5. Schedule Types

1. **Fixed recurrence**: hourly, daily, weekly, monthly.
2. **Condition watch**: production degradation, threshold reached, stale backup, experiment decision point.
3. **Deferred/one-time**: recheck tomorrow, sustain check in 30 days, reevaluate an agent after remediation.
4. **Event-driven**: owner command, deployment failure, commerce webhook, security alert.

Prefer reliable events over frequent polling.

## 6. Schedule Record

```yaml
schedule:
  id:
  name:
  job_type:
  schedule_type:
  cadence:
  condition_ref:
  target_ref:
  owner_agent_id:
  authority_ref:
  priority:
  enabled:
  max_runtime:
  max_attempts:
  concurrency_policy:
  budget_policy_ref:
  last_run_at:
  next_run_at:
```

## 7. Scheduled Run

```yaml
scheduled_run:
  id:
  schedule_id:
  planned_at:
  started_at:
  completed_at:
  status:
  attempt:
  mission_id:
  task_id:
  result_ref:
  cost_usd:
  correlation_id:
```

Statuses: `PLANNED`, `QUEUED`, `RUNNING`, `SUCCEEDED`, `NO_ACTION`, `FAILED`, `BLOCKED`, `SKIPPED`, `CANCELLED`.

`NO_ACTION` is a successful result.

## 8. Authority

Every schedule requires an `authority_ref`. No scheduled job may expand its own permissions, budget, production authority, or agent trust.

## 9. Job Classes

- HEALTH_CHECK
- RECONCILIATION
- MEASUREMENT
- ANALYSIS
- MAINTENANCE
- EXPERIMENT_CHECKPOINT
- CONTENT_REVIEW
- GROWTH_REVIEW
- SECURITY_REVIEW
- BACKUP_REVIEW
- EXECUTIVE_REPORT
- AGENT_EVALUATION
- SELF_IMPROVEMENT_REVIEW
- SUSTAIN_CHECK

## 10. Priority

Use `P0 CRITICAL`, `P1 HIGH`, `P2 NORMAL`, `P3 LOW`. P0 is reserved for critical recovery, security, or customer-impact work.

## 11. Concurrency

Each schedule uses `ALLOW`, `FORBID`, or `REPLACE`. Default to `FORBID` for expensive analysis and mutating jobs.

Define global WIP limits for active missions, tasks, parallel agent tasks, and production changes. Tune actual limits from evidence.

## 12. Resource Locks

Acquire appropriate locks before conflicting work involving repositories, deployments, migrations, content paths, experiment configuration, or other shared resources.

## 13. Duplicate Prevention

Before scheduled analysis creates new work:

1. search active missions;
2. search active tasks;
3. inspect recent completed work;
4. inspect existing opportunities;
5. create new work only when not already covered.

## 14. Opportunity Queue

Low-priority findings belong in a backlog, not immediately in missions.

```yaml
opportunity:
  id:
  domain:
  statement:
  evidence_refs:
  expected_value:
  confidence:
  effort:
  risk:
  status:
  discovered_at:
```

## 15. Constraint-First Rule

Recurring improvement analysis first asks:

**What is the primary constraint now?**

Prioritize the work most likely to relieve it. Avoid optimizing every business area simultaneously.

# 16. Recommended Operating Cadence

This is a starting framework. Claude must inspect existing cron jobs, GitHub Actions, Hostinger jobs, monitoring, workers, and queues before creating anything.

## Event-Driven

Use events where available for:

- owner commands and decisions
- failed deployments
- critical incidents
- security alerts
- commerce events
- GitHub workflow/release failures
- experiment thresholds

## Hourly: Lightweight Operational Health

Candidate checks:

- public website availability
- critical customer path
- API health
- container health
- disk/memory pressure
- unexpected restarts
- event-pipeline freshness
- production release reconciliation
- critical GitHub workflow/security exceptions

Hourly checks should be deterministic and cheap whenever possible.

## Daily: Business and Operating Pulse

Review:

- revenue and authoritative commerce reconciliation
- customer outcomes
- desired-function funnel
- quest completion
- product performance
- active/blocked/stale missions
- experiment checkpoints
- analytics freshness and instrumentation
- GitHub exceptions
- VPS/Docker trends
- AI/tool/infrastructure cost

Do not create content or products simply because the daily job ran.

## Weekly: Improvement and Strategy Loop

Review:

- primary constraint
- mission portfolio
- experiments
- SEO/AEO opportunities
- content portfolio
- quest/card performance
- product portfolio
- customer journey
- autonomy health
- agent failures/evaluations
- self-improvement opportunities
- executive owner brief

## Monthly: Business System Review

Review:

- revenue vs owner target
- customer outcomes and retention
- product economics
- acquisition efficiency
- room/micro-zone expansion
- infrastructure cost/reliability
- architecture debt
- security posture
- backup/recovery evidence
- agent organization and autonomy maturity

Do not redesign architecture merely because a month passed.

# 17. Executive Brief

A weekly owner brief should contain only verified, decision-useful information:

```text
Business health
Customer outcomes
Primary constraint
What Claude changed
Experiment results
Production/autonomy health
Decisions needed
Claude recommendation
```

If critical sources are stale, report the staleness instead of inventing a current summary.

# 18. Customer Sustain Scheduling

Completed micro-zone outcomes may create future sustain checks, such as 7-, 30-, or 90-day follow-up when product design and customer preference support it. Avoid notification spam.

# 19. Experiment Scheduling

Experiments should run until decision criteria are met based on exposure, elapsed time, primary metrics, and guardrails. Do not change experiments every day because a scheduled review occurs.

# 20. Content / SEO / AEO

Scheduled reviews may identify:

- technical search problems
- important content decay
- unanswered high-intent questions
- query clusters
- content-to-outcome gaps
- answer-engine referral opportunities

They do **not** automatically authorize mass publishing.

Content production remains mission-driven and must provide unique user value.

# 21. Product Scheduling

Periodic product analysis may identify repeated unmet needs, micro-zone friction, kit opportunities, digital products, returns, margins, or outcome gaps.

Do not automatically purchase inventory or create physical products.

# 22. Quest Scheduling

Review quest/card completion, abandonment, duration accuracy, desired-function fit, outcomes, repeat use, and group behavior. Material changes should normally be tested as experiments.

# 23. GitHub Manager Cadence

Potential:

**Hourly:** critical workflow/release blockers.

**Daily:** branch/repository health, stale critical PRs, security/dependency exceptions.

**Weekly:** workflow efficiency, release traceability, repository hygiene, branch-policy verification.

Avoid cosmetic churn.

# 24. VPS/Docker Manager Cadence

Potential:

**Hourly:** service health, pressure, restarts, public endpoint health.

**Daily:** disk trends, images/containers, certificates, backups, deployment drift.

**Weekly:** capacity, recovery readiness, configuration drift, safe cleanup opportunities.

Cleanup actions require safeguards.

# 25. Security Cadence

Prefer event-driven security alerts. Periodically inspect dependency findings, secret exposure, permissions, public ports, certificates, image vulnerabilities, and security headers.

Critical security work may preempt ordinary optimization.

# 26. Analytics Cadence

Daily: freshness, quality, business/customer KPI refresh.

Weekly: funnel, constraints, experiments, metric-definition integrity, attribution quality.

# 27. Cost-Aware Scheduling

Classify jobs as `NEGLIGIBLE`, `LOW`, `MEDIUM`, or `HIGH`.

High-cost recurring analysis requires strong justification.

Support configurable soft and hard AI/tool spend limits.

At a soft limit, defer low-priority analysis.

At a hard limit, stop discretionary AI-intensive work while preserving critical monitoring/recovery according to policy.

# 28. Deterministic Checks First

Use deterministic mechanisms before LLM reasoning when possible.

```text
HTTP health check
→ healthy
→ NO_ACTION
```

Do not invoke an expensive model merely to determine whether an HTTP endpoint responds.

# 29. Escalation Ladder

```text
Deterministic Check
→ Rule Evaluation
→ Specialist Agent
→ Orchestrator
→ Owner only if required
```

# 30. Runaway Loop Prevention

All recurring work must have:

- bounded retries
- bounded child tasks
- WIP limits
- cost limits
- duplicate detection
- cooldowns where appropriate
- explicit authority
- maximum runtime
- concurrency policy

Agents may propose new schedules. They may create or alter them only when governance explicitly allows it.

# 31. Retry Policy

Example:

```yaml
retry:
  max_attempts: 3
  backoff: EXPONENTIAL
  retry_on:
    - TRANSIENT_NETWORK
    - RATE_LIMIT
```

Never retry permanent authorization or validation failures forever.

# 32. Failure Escalation

After maximum attempts:

```text
FAILED
→ classify
→ bounded recovery if authorized
→ alert if material
→ stop retrying
```

# 33. Cooldowns and Storm Protection

Deduplicate repeated noncritical alerts/tasks over a configurable period while preserving underlying event counts.

If an external dependency repeatedly fails, stop expensive repeated calls until recovery when appropriate.

# 34. Time Zones

Schedules must use explicit timezone semantics. Owner-facing schedules should display in the configured owner timezone. Do not assume server timezone equals owner timezone. Use DST-aware scheduling.

# 35. Maintenance and Quiet Windows

Support maintenance windows and owner/customer notification quiet hours where useful. Quiet hours must not suppress critical recovery when policy requires it.

# 36. Job Dependencies

Example:

```text
Analytics Refresh
→ Executive Projection
→ Owner Brief
```

If upstream refresh fails, downstream reports must be marked stale or blocked.

# 37. Scheduler Health Metrics

Track:

- scheduler heartbeat
- due/late jobs
- failed/blocked jobs
- queue lag
- duplicate prevention
- cost
- NO_ACTION rate
- useful findings
- missions created
- false positives
- cost per useful finding

# 38. Schedule Retirement

Periodically retire schedules that duplicate another mechanism, generate noise, have obsolete targets, produce no value, or cost more than justified.

Every schedule must have a logical owner. No orphan schedules.

# 39. Owner Visibility

The Owner Command Center should summarize:

- important active schedules
- high-cost schedules
- failed schedules
- material recurring commitments

The owner should not need to manage cron expressions.

Potential controls: pause, resume, request review, adjust approved budget, retire.

# 40. Autonomy Mode Interaction

## EMERGENCY_STOP

- stop new nonessential scheduled mutations
- preserve monitoring and evidence
- preserve critical recovery actions according to policy

## READ_ONLY

Allow monitoring, analysis, reporting, and evaluations. Block code/config/content/product/deployment mutations unless explicitly allowed.

## CONSERVATIVE

Reduce discretionary work, preserve monitoring, and strengthen gates for production changes.

# 41. Customer and Revenue Guardrails

The revenue target does not authorize:

- unlimited spend
- manipulative UX
- unnecessary product recommendations
- low-quality mass content
- privacy/security weakening

If revenue improves while customer-outcome guardrails deteriorate, stop and review the experiment.

# 42. Scheduler Technology

Use the simplest existing mechanism that satisfies the need.

Infrastructure cron is appropriate for simple infrastructure tasks.

Application scheduling is better when jobs require business state, authorization, idempotency, dynamic cadence, mission linkage, or rich auditability.

Do not create a second scheduler if an adequate one already exists.

# 43. Persistence

Important schedules and run state must survive container/application restarts.

In multi-instance environments, prevent duplicate execution through appropriate locking, leader election, or queue semantics.

# 44. Misfire Policy

After downtime, do not blindly execute every missed recurrence.

Possible policies:

- RUN_ONCE_NOW
- SKIP
- RESCHEDULE
- REQUIRE_REVIEW

Set by job type.

# 45. API Integration

Align with `AUTONOMY-API.md`.

```text
GET  /api/v1/schedules
POST /api/v1/schedules
PATCH /api/v1/schedules/{id}
POST /api/v1/schedules/{id}/pause
POST /api/v1/schedules/{id}/resume
GET  /api/v1/schedules/{id}/runs
```

# 46. Events

Recommended:

```text
schedule.created
schedule.updated
schedule.started
schedule.no_action
schedule.completed
schedule.failed
schedule.blocked
schedule.paused
schedule.resumed
schedule.retired
```

# 47. Data Model Integration

Add only if not already represented:

```text
schedule
scheduled_run
opportunity
```

Preserve:

```text
Schedule Run → Opportunity → Mission → Task → Result
```

# 48. Bootstrap Discovery

Before implementation inspect:

1. cron jobs
2. application scheduler
3. Docker Compose/services
4. workers
5. queues
6. GitHub Actions schedules
7. Hostinger scheduled tasks
8. analytics refreshes
9. commerce webhooks
10. backups
11. monitoring/alerts
12. current AI/tool budget controls

Document overlap before adding jobs.

# 49. Minimum Viable Scheduler

Phase 1 should normally focus on:

```text
production health
deployment reconciliation
telemetry freshness
daily business pulse
mission health
weekly primary-constraint review
weekly owner brief
```

Only after verifying what already exists.

# 50. Phase 2

Add when useful:

```text
SEO/AEO review
content freshness
quest review
product review
agent evaluations
autonomy improvement review
cost optimization
sustain checks
```

# 51. Phase 3

Only with evidence:

```text
dynamic cadence
condition-based scheduling
adaptive cost budgets
predictive maintenance
automatic schedule retirement
```

# 52. First Scheduler Mission

```yaml
mission:
  title: Establish Autonomous Operating Cadence
  objective: >
    Inspect all existing scheduled and event-driven automation, then implement
    the smallest safe recurring operating loop required for production health,
    business measurement, mission review, constraint identification, and
    owner visibility.
  success:
    - existing schedulers inventoried
    - duplicate schedules eliminated
    - production health monitoring verified
    - deployment reconciliation operational
    - daily business pulse operational
    - weekly constraint review operational
    - owner brief generated from fresh data
    - WIP limits enforced
    - cost limits enforced
    - retries bounded
    - scheduled work survives restart
```

# 53. Initial State

Until verified:

```yaml
autonomy_scheduler:
  implementation_status: UNKNOWN
  scheduler_technology: UNKNOWN
  cron_jobs: UNKNOWN
  github_schedules: UNKNOWN
  background_workers: UNKNOWN
  queue: UNKNOWN
  monitoring_schedule: UNKNOWN
  backup_schedule: UNKNOWN
  ai_cost_guardrails: UNKNOWN
```

# 54. Acceptance Tests

At minimum:

- due job executes once
- duplicate run is blocked
- restart does not duplicate material work
- transient failure retries within limit
- permanent failure does not retry forever
- hard budget limit blocks discretionary AI work
- emergency stop blocks scheduled mutations
- read-only mode preserves monitoring
- stale analytics prevents a falsely current report
- NO_ACTION completes successfully
- schedule-created mission is traceable
- disabled schedule does not execute
- unauthorized agent cannot create privileged schedule

# 55. Runaway Test

Simulate:

```text
schedule
→ mission
→ new schedule
→ new mission
→ new schedule
```

The system must stop recursive expansion.

# 56. Cost Spike Test

Simulate a high-cost recurring job and verify classification, budget checks, soft-limit behavior, hard-limit behavior, and owner visibility.

# 57. Failure Storm Test

Simulate repeated dependency failure and verify bounded retries, cooldown, deduplicated alerts, preserved evidence, and no unbounded agent invocation.

# 58. Recommended Starting Rhythm

After discovery and verification:

```text
EVENT-DRIVEN
Critical incidents, owner commands, deployment failures, commerce events

HOURLY
Lightweight production/runtime/telemetry health

DAILY
Business pulse, mission health, analytics quality, cost pulse

WEEKLY
Primary constraint, experiments, SEO/AEO, quests, products, autonomy, owner brief

MONTHLY
Business review, strategy alignment, architecture/recovery review
```

# 59. Autonomous Improvement Loop

```text
OBSERVE
  ↓
MEASURE
  ↓
IDENTIFY PRIMARY CONSTRAINT
  ↓
PRIORITIZE
  ↓
CREATE / CONTINUE MISSION
  ↓
EXECUTE
  ↓
VERIFY
  ↓
EXPERIMENT
  ↓
LEARN
  ↓
STANDARDIZE OR ROLLBACK
  ↓
OBSERVE AGAIN
```

# 60. Business Loop

```text
TRAFFIC
  ↓
DESIRED FUNCTION
  ↓
DIAGNOSIS
  ↓
QUEST
  ↓
OUTCOME
  ↓
SUSTAIN
  ↓
PRODUCT / SERVICE WHEN USEFUL
  ↓
REVENUE
  ↓
LEARNING
```

Scheduled analysis should seek the largest constraint in this loop rather than maximizing every stage independently.

# 61. Technical Loop

```text
CODE → TEST → MERGE → RELEASE → DEPLOY → VERIFY → OBSERVE → IMPROVE
```

# 62. Autonomy Loop

```text
AGENT TASK → RESULT → EVALUATION → PATTERN → IMPROVEMENT → REQUALIFICATION
```

# 63. Non-Negotiable Rules

Claude and subagents must not:

- create unlimited recurring jobs
- create recursive scheduling loops
- treat schedules as permission
- bypass required owner approval
- run expensive strategic analysis hourly without evidence
- create missions for every observation
- mass-generate SEO/AEO pages on a timer
- mass-create products on a timer
- increase paid spend solely because a schedule ran
- retry forever
- duplicate production mutations
- ignore WIP or cost limits
- invoke LLMs where deterministic checks suffice
- generate current-looking reports from stale data
- let restarts duplicate important jobs
- allow disabled schedules to execute
- let agents self-expand recurring authority
- hide failed scheduled work
- equate activity with value
- optimize revenue at the expense of customer trust, privacy, security, or useful outcomes
- assume scheduling technology before inspection
- build a parallel scheduler without justification

# 64. Final Principle

The goal is not to make Claude work constantly.

The goal is to make Claude **wake up at the right times, inspect the right signals, select the highest-value authorized work, and return to waiting when nothing useful needs to happen.**

```text
MONITOR QUIETLY
      ↓
DETECT MEANINGFUL CHANGE
      ↓
VERIFY
      ↓
PRIORITIZE AGAINST THE PRIMARY CONSTRAINT
      ↓
ACT WITHIN AUTHORITY
      ↓
MEASURE
      ↓
REPORT ONLY WHAT MATTERS
```

A mature autonomous organization should frequently conclude:

> Everything important is healthy. No action is required right now.

That is successful autonomy.

That is the purpose of `AUTONOMY-SCHEDULER.md`.
