# 6S Success Autonomous Scheduler

> Canonical operating cadence for Claude Code and specialist agents: recurring inspections, scheduled jobs, prioritization, locking, retries, failure handling, content and SEO cadence, experiments, GitHub/VPS operations, executive dashboard refresh, maintenance, and continuous improvement for 6S-success.com.

## 1. Purpose

`SCHEDULER.md` defines **when autonomous work happens, what gets checked, how often it runs, how duplicate work is prevented, and when Claude should stop and escalate**.

The scheduler exists to create disciplined continuous improvement, not constant activity.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BACKLOG.md`
- `METRICS.md`
- `OBSERVABILITY.md`
- `TESTING.md`
- `RELEASES.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `DISASTER-RECOVERY.md`
- `COST-GOVERNANCE.md`
- `EXPERIMENTS.md`
- `DECISIONS.md`
- `LEARNINGS.md`

---

# 2. Prime Rule

**Claude should run work because there is a reason, not because a timer fired.**

A scheduled trigger begins an evaluation.

It does not automatically justify a change.

Canonical loop:

**Wake**
→ **Verify State**
→ **Check for Urgency**
→ **Identify Constraint**
→ **Select Highest-Value Authorized Work**
→ **Act**
→ **Test**
→ **Deploy if justified**
→ **Verify**
→ **Measure**
→ **Record**
→ **Sleep**

---

# 3. Scheduler Objectives

The scheduler should ensure that:

1. production problems are noticed quickly
2. security and commerce failures receive priority
3. data remains fresh enough for decisions
4. Claude continuously works the highest-value backlog
5. experiments are reviewed on time
6. content and SEO improve consistently
7. GitHub and VPS remain healthy
8. costs remain controlled
9. backups and recovery stay viable
10. the owner sees concise executive status
11. agents do not create duplicate or runaway work
12. autonomous work remains reversible and auditable

---

# 4. Scheduling Layers

Use five conceptual layers:

## Event-Driven

Triggered by events such as:

- failed deployment
- failed health check
- security finding
- purchase webhook failure
- pull request
- experiment threshold

## Frequent

Operational checks every few minutes or hourly where justified.

## Daily

Business and operational review.

## Weekly

Improvement and prioritization cycle.

## Monthly / Quarterly

Strategic, financial, resilience, architecture, and governance review.

---

# 5. Do Not Poll What Can Be Event-Driven

Prefer event/webhook-driven workflows when reliable and secure.

Examples:

- GitHub workflow failure
- deployment completion
- commerce webhook
- security scan finding

Use polling where event mechanisms are unavailable or insufficient.

---

# 6. Minimum Frequency Principle

Use the **lowest frequency that still protects the business and enables timely action**.

Do not check a slow-changing metric every minute.

Excessive polling creates:

- API cost
- rate-limit risk
- noise
- duplicated work
- false urgency

---

# 7. Scheduler Source of Truth

The production scheduler implementation must be discovered.

Potential mechanisms:

- GitHub Actions
- cron
- systemd timers
- application scheduler
- queue worker
- external scheduler

Do not create multiple overlapping scheduler systems without reason.

---

# 8. Job Registry

Every recurring autonomous job should have a registry entry.

Suggested:

```yaml
job_id:
name:
purpose:
owner_agent:
trigger:
schedule:
priority:
authority:
timeout:
retry_policy:
lock:
dependencies:
success_evidence:
failure_action:
last_run:
next_run:
enabled:
```

---

# 9. Job IDs

Use stable identifiers.

Examples:

```text
OPS-HEALTH-001
SEO-DISCOVERY-001
CONTENT-REVIEW-001
COST-REVIEW-001
DR-BACKUP-VERIFY-001
EXEC-DASHBOARD-001
```

Do not reuse retired IDs for unrelated jobs.

---

# 10. Job Priority

Suggested:

## P0 — Critical

Active security, data, commerce, or outage risk.

## P1 — High

Serious degradation, failed deployment, backup failure.

## P2 — Business-Critical

Revenue/customer journey constraint.

## P3 — Improvement

SEO, content, UX, performance, automation.

## P4 — Maintenance

Cleanup, documentation, low-risk technical debt.

A P4 scheduled job should not displace P0–P2 work.

---

# 11. Authority

Each job must inherit authority from `AUTONOMY.md`.

A scheduler cannot convert a RED action into a GREEN action.

Example:

A daily cost review may recommend a paid SEO tool.

It may not purchase it unless spending authority exists.

---

# 12. Scheduler Locking

Prevent duplicate execution.

A job should normally have a lock.

Example:

```yaml
lock:
  key: SEO-DISCOVERY-001
  max_age_minutes: 60
```

If a valid lock exists:

- do not start duplicate work
- report current run
- recover stale lock only according to policy

---

# 13. Global Deployment Lock

Only one uncontrolled production deployment should occur at a time.

Use a deployment lock/concurrency group.

This prevents two agents from simultaneously changing production state.

---

# 14. Entity Locks

For high-contention work, lock by entity.

Examples:

```text
release:production
content:entryway
experiment:EXP-014
migration:db-2026-08-14-001
```

Do not lock the entire system unnecessarily.

---

# 15. Idempotency

Recurring jobs should be safe when invoked twice where practical.

Examples:

- dashboard refresh
- sitemap validation
- backup verification
- metrics collection

Critical side-effect jobs require explicit idempotency.

---

# 16. Job Timeout

Every job should have a reasonable timeout.

A job that never finishes can become:

- cost leak
- deployment lock
- agent loop
- resource leak

Timeout should match expected work.

---

# 17. Retry Policy

Retry only likely transient failures.

Suggested concept:

```yaml
max_attempts: 3
backoff: exponential
retry_on:
  - network_timeout
  - transient_provider_error
do_not_retry:
  - invalid_credentials
  - failed_security_gate
  - invalid_schema
  - destructive_conflict
```

---

# 18. Retry Budget

Retries consume resources.

Do not allow nested agents and infrastructure to multiply retries indefinitely.

One layer should own retry behavior.

---

# 19. Failure Escalation

After retry exhaustion:

- preserve evidence
- release safe locks
- mark job failed
- create/associate incident or backlog item
- escalate according to severity

Do not silently ignore recurring failures.

---

# 20. Dead-Letter Work

For asynchronous jobs that cannot complete, preserve enough context for diagnosis.

Do not endlessly requeue malformed tasks.

---

# 21. Scheduler Heartbeat

The scheduler itself should be observable.

Track:

```yaml
last_heartbeat:
last_successful_cycle:
active_jobs:
failed_jobs_24h:
stale_locks:
scheduler_status:
```

A dead scheduler must not appear as "everything healthy."

---

# 22. Scheduler Status

Use:

- `HEALTHY`
- `DEGRADED`
- `STOPPED`
- `PAUSED`
- `UNKNOWN`

---

# 23. Global Pause

There should be a mechanism to pause noncritical autonomous work.

Use during:

- security incident
- disaster recovery
- major migration
- owner-requested freeze
- runaway agent behavior

Critical monitoring may remain active.

---

# 24. Agent Kill Switch

`DISASTER-RECOVERY.md` defines broader containment.

Scheduler must support disabling:

- autonomous writes
- deployments
- content publishing
- paid API-heavy jobs
- experiments

without disabling owner access.

---

# 25. Maintenance Mode

A maintenance mode may temporarily:

- pause optimization
- pause publishing
- pause experiments
- preserve monitoring
- preserve backups

Use only when justified.

---

# 26. Time Zone

Store scheduler times explicitly.

Recommended:

- system automation in UTC where practical
- owner-facing dashboard may display local time

Never rely on ambiguous local server time.

---

# 27. Daylight Saving Time

For owner-facing scheduled reports, use an explicit timezone.

For infrastructure jobs, UTC reduces DST ambiguity.

---

# 28. Hourly Operational Cycle

Candidate hourly checks:

- production availability
- critical container health
- severe error anomalies
- failed deployment state
- commerce failure signals
- disk emergency threshold
- critical security alerts
- scheduler heartbeat

Do not run expensive full business analysis hourly unless justified.

---

# 29. Daily Operations Cycle

Daily review:

1. production health
2. deployment state
3. severe errors
4. backup state
5. commerce reconciliation
6. analytics freshness
7. cost anomalies
8. security findings
9. failed jobs
10. stale locks
11. owner decisions needed

---

# 30. Daily Business Cycle

Review:

- visitors
- acquisition
- desired-function starts
- micro-zone activity
- quest starts
- quest completion
- product views
- checkout
- purchases
- refunds
- revenue

Do not overreact to one low-volume day.

---

# 31. Daily Backlog Cycle

After urgent work is clear:

1. inspect `BACKLOG.md`
2. inspect active experiments
3. identify current constraint
4. score candidate work
5. select limited work-in-progress
6. assign agent
7. execute within authority
8. verify
9. update status

---

# 32. Work-in-Progress Limit

Autonomous agents should not start dozens of parallel improvements.

Suggested initial global WIP:

```yaml
major_active_improvements: 1-3
active_experiments: 1-3
```

Adjust based on system maturity and traffic.

---

# 33. Finish Before Starting

Prefer completing and measuring work before starting another change to the same customer journey.

This improves:

- attribution
- quality
- focus
- learning

---

# 34. Daily Executive Dashboard Refresh

Refresh the executive dashboard from authoritative sources.

Show:

- business status
- revenue
- customer journey
- production
- experiments
- cost
- security/quality
- autonomous work
- decisions

Display freshness.

---

# 35. Owner Notification Cadence

Do not send constant updates.

Default concept:

- immediate: critical actionable event
- daily dashboard: concise current state
- weekly summary: learning and priorities
- monthly: strategic/business review

Actual notification mechanism must be configured separately.

---

# 36. Daily Content Evaluation

Daily content work should begin with evidence.

Ask:

- what questions are users searching?
- what existing pages underperform?
- what micro-zones lack useful content?
- what content supports active products/quests?
- what customer friction is emerging?

Do not publish simply to hit a daily quota.

---

# 37. Content Publishing Cadence

Avoid arbitrary volume goals.

Use:

**Quality + Search Demand + Customer Need + Product Relevance**

A strong useful page is better than many thin pages.

---

# 38. Content Queue

Content candidates should have:

```yaml
content_id:
topic:
room:
micro_zone:
desired_function:
root_cause:
search_intent:
customer_value:
commercial_relevance:
evidence:
priority:
status:
```

---

# 39. Content Quality Gate

Before publishing:

- content is useful
- no unsupported claims
- no duplication
- SEO metadata valid
- internal links useful
- CTA appropriate
- mobile readable
- analytics ready
- no secrets/private data

Follow `TESTING.md`.

---

# 40. Weekly SEO Cycle

Weekly:

1. inspect search data
2. inspect index coverage
3. inspect high-impression/low-click pages
4. inspect ranking/query opportunities
5. inspect broken links/redirects
6. inspect internal-link opportunities
7. inspect content gaps
8. identify 1–3 highest-value improvements

Do not rewrite pages solely because ranking fluctuated.

---

# 41. Weekly AEO Cycle

Review:

- high-value question formats
- direct answer clarity
- entity/context clarity
- structured data validity
- attributable AI/referral traffic where available
- content usefulness

Do not fabricate AI visibility.

---

# 42. Weekly Product Cycle

Review:

- recommendations
- product views
- cart adds
- checkout
- purchases
- revenue
- margin
- refunds
- customer outcome

Identify:

- strong products
- weak products
- missing products
- poor recommendation mappings

---

# 43. Weekly Quest Cycle

Review:

- starts
- completion
- abandonment
- duration
- cards skipped
- multiplayer behavior
- desired-function/root-cause segments

Select specific deck/quest improvements based on evidence.

---

# 44. Weekly Experiment Cycle

For each experiment:

- data quality
- exposures
- primary metric
- guardrails
- sample sufficiency
- decision timing

Do not peek and declare winners without the defined decision approach.

---

# 45. Weekly GitHub Cycle

GitHub Manager should review:

- open PRs
- failed workflows
- stale branches
- dependency alerts
- branch protection
- release lineage
- unresolved issues
- repository drift indicators

Do not delete branches with uncertain value.

---

# 46. Weekly VPS/Docker Cycle

VPS/Docker Manager should review:

- CPU trends
- memory
- disk
- container restarts
- image accumulation
- log growth
- exposed ports
- Compose state
- backup status
- OS/security maintenance signals

Do not blindly prune volumes.

---

# 47. Weekly DevOps/SRE Cycle

Review:

- availability
- latency
- errors
- deployment success
- incidents
- smoke tests
- recovery readiness
- observability gaps

Prioritize reliability work proportional to actual risk.

---

# 48. Weekly Cost Cycle

Review:

- MTD revenue
- infrastructure
- AI/API
- SaaS
- commerce fees
- acquisition
- cost anomalies
- contribution margin

Follow `COST-GOVERNANCE.md`.

---

# 49. Weekly Security Cycle

Review:

- dependency vulnerabilities
- secret scanning
- auth anomalies
- access changes
- exposed services
- TLS
- unresolved security backlog

High-severity findings override normal growth work.

---

# 50. Weekly Quality Cycle

Review:

- failed tests
- flaky tests
- escaped defects
- E2E coverage
- accessibility
- mobile regressions
- analytics regressions

Follow `TESTING.md`.

---

# 51. Weekly Learning Cycle

Update `LEARNINGS.md` only with durable learning.

Examples:

- customer behavior
- product economics
- quest design
- technical architecture
- deployment reliability

Do not turn learnings into daily log.

---

# 52. Weekly Decision Review

Review unresolved `DECISIONS.md` items.

Escalate only decisions that require owner authority or strategic judgment.

---

# 53. Weekly Executive Summary

Keep concise:

## Results

What changed.

## Business

Revenue and funnel.

## Customer

Quest/outcome signals.

## Experiments

What was learned.

## Technology

Reliability/security.

## Autonomous Work

What Claude completed.

## Next

Top priorities.

## Decisions Needed

Only real owner decisions.

---

# 54. Monthly Business Review

Review:

- revenue vs target
- conversion
- AOV
- contribution margin
- acquisition
- product performance
- refunds
- customer outcomes
- room/micro-zone performance
- content/SEO
- experiments
- technology
- costs

---

# 55. Monthly Portfolio Review

Ask:

- Which rooms/micro-zones create most value?
- Which desired functions resonate?
- Which root causes are common?
- Which quests perform best?
- Which products make money?
- Which content converts?
- What should be stopped?
- What should be scaled?

---

# 56. Monthly Architecture Review

Review:

- system complexity
- technical debt
- scaling needs
- observability
- deployment
- data contracts
- security
- recovery

Do not redesign architecture every month.

---

# 57. Monthly Cost Review

Follow `COST-GOVERNANCE.md`.

Identify:

- unused subscriptions
- AI cost efficiency
- infrastructure sizing
- margin
- paid experiment economics
- upcoming renewals

---

# 58. Monthly Content Pruning Review

Look for:

- obsolete content
- duplicate pages
- cannibalization
- low-value thin content
- outdated product references

Do not delete pages solely because they have low recent traffic.

Consider strategic and search value.

---

# 59. Monthly Agent Review

Evaluate each subagent:

- useful outcomes
- failures
- reversions
- cost
- escalations
- permission needs
- overlapping responsibility

Simplify agent architecture when possible.

---

# 60. Quarterly Disaster-Recovery Review

Follow `DISASTER-RECOVERY.md`.

Review:

- backups
- restore tests
- VPS reconstruction
- domain recovery
- GitHub recovery
- agent kill switch
- RPO/RTO

---

# 61. Quarterly Security Review

Review:

- permissions
- service accounts
- credentials
- unused access
- architecture
- dependencies
- recovery controls

Rotate credentials based on policy/risk, not arbitrary churn.

---

# 62. Quarterly Strategy Review

Ask:

- Is the $20K/month target on track?
- What is the dominant growth constraint?
- What customer outcome is strongest?
- Which room should expand next?
- Which product categories should scale?
- What should be discontinued?
- Does autonomy need more or less authority?

---

# 63. Quarterly Taxonomy Review

Review canonical:

- rooms
- micro-zones
- desired functions
- root causes
- quests
- cards
- products

Avoid uncontrolled taxonomy growth.

---

# 64. Quarterly Scheduler Review

Review the scheduler itself.

Remove:

- redundant jobs
- noisy alerts
- unused reports
- expensive low-value checks
- duplicate polling

Add checks only when evidence shows a gap.

---

# 65. Event: Production Down

Immediately:

1. verify signal
2. invoke incident workflow
3. pause noncritical deployments
4. diagnose
5. recover
6. verify
7. update owner if severity warrants

Operational recovery overrides scheduled content work.

---

# 66. Event: Failed Deployment

Immediately:

- identify release
- inspect failure
- determine current production state
- rollback/fix within authority
- verify
- record release status

Do not continue unrelated deployment work.

---

# 67. Event: Security Critical

Immediately:

- contain
- preserve evidence
- pause unsafe autonomy
- follow `SECURITY.md`
- invoke DR if needed

---

# 68. Event: Commerce Failure

Immediately:

- verify provider/application
- prevent duplicate side effects
- preserve order state
- disable misleading checkout if necessary and authorized
- reconcile after recovery

---

# 69. Event: Cost Runaway

Immediately:

- verify billing signal
- stop noncritical source if authorized
- preserve evidence
- diagnose loop/campaign
- follow `COST-GOVERNANCE.md`

---

# 70. Event: Backup Failure

A single failure may be P1/P2 depending on redundancy.

Investigate before the next expected recovery window becomes unsafe.

---

# 71. Event: Experiment Completion

When decision criteria are reached:

1. verify data
2. analyze
3. decide
4. record
5. remove losing/stale variant where appropriate
6. capture learning
7. update backlog

Do not leave completed experiments running forever.

---

# 72. Event: Strong Content Opportunity

A new search/customer opportunity enters backlog.

It does not automatically interrupt higher-priority work.

---

# 73. Event: Owner Approval

When owner approves a RED/YELLOW action:

- record scope
- execute only approved scope
- verify
- report outcome
- do not generalize approval into permanent authority unless explicitly stated

---

# 74. Dependency Scheduling

Jobs should declare dependencies.

Example:

```text
content_publish
depends_on:
  content_generate
  content_quality_gate
  seo_validate
```

Do not publish before gates pass.

---

# 75. DAG Workflows

Complex workflows may be modeled as a directed acyclic graph.

Avoid recursive agent spawning without explicit bounds.

---

# 76. Agent Delegation

The orchestrator should assign specialized work to the appropriate subagent.

Examples:

- GitHub → GitHub Manager
- runtime → VPS/Docker Manager
- release reliability → DevOps/SRE
- SEO → SEO/AEO agent
- analytics → analytics/intelligence
- commerce → commerce manager
- quests → quest experience agent

Use actual installed agent names.

---

# 77. Agent Concurrency

Parallel work is appropriate when tasks do not conflict.

Good:

- SEO research
- read-only cost analysis
- test analysis

Potentially unsafe:

- two agents editing same file
- two production deployments
- simultaneous migrations

Use locks.

---

# 78. Maximum Agent Fan-Out

Do not allow uncontrolled recursive subagent creation.

Set an implementation-level concurrency limit appropriate to resources.

Current limit:

`UNKNOWN`

Discover and configure deliberately.

---

# 79. Agent Task Contract

Each delegated task should include:

```yaml
task_id:
objective:
scope:
constraints:
authority:
expected_output:
success_evidence:
deadline_or_timeout:
```

---

# 80. Agent Completion

An agent returning text is not necessarily completion.

Completion requires the expected evidence.

Example:

A deployment task is complete only after production verification.

---

# 81. Scheduler and Backlog

Scheduled cycles should pull from the backlog rather than inventing random work.

Exceptions:

- incident
- security
- operational maintenance
- newly detected high-value opportunity

---

# 82. Prioritization Formula

Potential framework:

```text
Priority Score =
(Expected Customer/Business Value × Confidence × Urgency)
/
(Effort × Risk)
```

Do not treat formula as mechanically authoritative.

Strategic dependencies matter.

---

# 83. Constraint First

Before choosing growth work, identify current system constraint.

Examples:

- discovery
- conversion
- quest completion
- product relevance
- checkout
- retention/sustainment
- reliability

Do not optimize everything simultaneously.

---

# 84. Entryway Priority

Until Entryway proves the full model, prioritize completing and learning from the Entryway journey before scaling shallow implementations across the entire home.

---

# 85. No-Work Decision

A valid autonomous decision is:

**Do nothing now.**

Examples:

- metric movement is noise
- experiment needs more data
- no authorized high-value task exists
- deployment risk exceeds benefit
- system is healthy and backlog is blocked

Autonomy does not require constant code changes.

---

# 86. Quiet Hours

Nonurgent owner notifications should respect configured owner preferences.

Infrastructure monitoring continues.

Current preference:

`UNKNOWN`

Do not invent one.

---

# 87. Maintenance Windows

High-risk maintenance may use a planned window when customer impact justifies it.

Record:

- start
- expected duration
- rollback
- verification
- owner approval if required

---

# 88. Job Audit Trail

Every material scheduled run should record:

```yaml
run_id:
job_id:
started_at:
completed_at:
agent:
result:
actions:
evidence:
cost:
release_id:
error:
```

Do not log secrets or hidden reasoning.

---

# 89. Job Cost

Track expensive jobs where useful:

- AI tokens/cost
- external APIs
- compute
- image generation

This helps remove low-value automation.

---

# 90. Job Effectiveness

A job should periodically prove it is useful.

Examples:

SEO job:
→ actionable opportunities found.

Backup verification:
→ recovery evidence improved.

Content job:
→ useful content published and measured.

Delete or redesign jobs that repeatedly produce no value.

---

# 91. Scheduler Dashboard

Executive/operations panel:

```yaml
scheduler_status:
last_heartbeat:
active_jobs:
queued_jobs:
failed_jobs_24h:
stale_locks:
paused_jobs:
current_priority:
current_agent:
last_production_change:
next_major_review:
owner_approvals_waiting:
```

---

# 92. Daily Dashboard

Business panel:

```yaml
production_status:
revenue_mtd:
monthly_target:
visitors:
quest_starts:
quest_completion_rate:
purchases:
refunds:
active_experiments:
critical_alerts:
current_improvement:
decisions_needed:
data_freshness:
```

---

# 93. Scheduler Alerting

Alert for:

- scheduler heartbeat missing
- critical job repeatedly failing
- stale deployment lock
- runaway job
- unauthorized job attempt
- excessive retry
- queue backlog threatening customer operation

---

# 94. Scheduler Security

Scheduled tasks must:

- use least privilege
- avoid secrets in command lines/logs where possible
- verify target environment
- validate inputs
- respect authority
- use scoped credentials

---

# 95. Scheduler Testing

Test:

- schedule expression
- duplicate invocation
- lock behavior
- retry
- timeout
- failure
- disabled job
- stale lock
- authority boundary
- event trigger

Follow `TESTING.md`.

---

# 96. Scheduler Releases

Scheduler changes are production changes.

Follow `RELEASES.md`.

A broken scheduler can silently stop backups, monitoring, or business workflows.

---

# 97. Scheduler Recovery

Scheduler configuration should be reconstructable from source-controlled policy/configuration where appropriate.

Follow `DISASTER-RECOVERY.md`.

---

# 98. Current Scheduler State

Populate from verified discovery:

```yaml
scheduler:
  implementation: UNKNOWN
  timezone: UNKNOWN
  heartbeat: UNKNOWN
  global_pause: UNKNOWN
  concurrency_limit: UNKNOWN
  deployment_lock: UNKNOWN

jobs:
  hourly_health: UNKNOWN
  daily_operations: UNKNOWN
  daily_business: UNKNOWN
  dashboard_refresh: UNKNOWN
  weekly_seo: UNKNOWN
  weekly_product: UNKNOWN
  weekly_quest: UNKNOWN
  weekly_github: UNKNOWN
  weekly_vps: UNKNOWN
  weekly_security: UNKNOWN
  weekly_cost: UNKNOWN
  monthly_business_review: UNKNOWN
  quarterly_dr_review: UNKNOWN

notifications:
  critical_channel: UNKNOWN
  daily_summary: UNKNOWN
  weekly_summary: UNKNOWN

agent_controls:
  kill_switch: UNKNOWN
  max_fan_out: UNKNOWN
  task_timeout: UNKNOWN

job_history:
  storage: UNKNOWN
  retention: UNKNOWN
```

---

# 99. Initial Recommended Cadence

This is a starting framework, not permission to implement blindly.

| Cadence | Activity |
|---|---|
| Every 5–15 min | Uptime/critical synthetic checks if needed |
| Hourly | Critical operations/commerce/security anomaly check |
| Daily | Operations + business + backlog + dashboard |
| Weekly | SEO/AEO, quest, product, GitHub, VPS, security, quality, cost, experiments |
| Monthly | Business, portfolio, architecture, subscriptions, content pruning, agent performance |
| Quarterly | DR, security/access, strategy, taxonomy, scheduler governance |

Actual frequency must be calibrated to traffic, risk, vendor limits, and cost.

---

# 100. First Scheduler Mission

Once Claude has legitimate access:

1. discover existing schedulers
2. inventory recurring jobs
3. identify duplicate mechanisms
4. identify critical missing jobs
5. identify uncontrolled loops
6. verify timezone
7. verify locking/concurrency
8. verify retry/timeout behavior
9. verify scheduler observability
10. verify global pause/kill switch
11. map jobs to agents
12. connect job status to dashboard
13. disable nothing during discovery unless an active hazard exists and authority permits
14. update Current Scheduler State
15. create prioritized scheduler backlog

---

# 101. Minimum Scheduler Before Broad Autonomy

Before Claude operates continuously, establish:

- scheduler source of truth
- heartbeat
- global pause
- bounded retries
- job timeouts
- deployment lock
- agent concurrency control
- job audit trail
- critical health checks
- daily business review
- executive dashboard refresh
- authority enforcement

---

# 102. Scheduler Maturity Model

## Level 0 — Ad Hoc

Claude acts only when manually prompted.

## Level 1 — Scheduled

Basic recurring jobs run.

## Level 2 — Controlled

Locks, retries, timeouts, permissions, and monitoring exist.

## Level 3 — Prioritized

Scheduler selects work based on business constraints and backlog.

## Level 4 — Adaptive

Cadence and resources adjust based on evidence, traffic, risk, and cost.

## Level 5 — Autonomous Operating System

The system continuously senses business and technical state, selects the highest-value authorized work, coordinates specialist agents, verifies outcomes, learns, and escalates only decisions requiring human judgment.

---

# 103. Non-Negotiable Scheduler Rules

Claude and subagents must not:

- create uncontrolled recursive loops
- start duplicate production deployments
- bypass autonomy policy because a job is scheduled
- repeatedly retry permanent failures
- run expensive analysis at unjustified frequency
- publish content merely to satisfy a quota
- scale paid activity without authority
- continue experiments indefinitely
- treat stale data as current
- hide scheduler failures
- leave stale locks indefinitely
- allow low-priority work to displace incidents
- create changes simply to appear active

---

# 104. Final Principle

The scheduler is the heartbeat of autonomous 6S Success.

It should not behave like a robot that blindly executes a calendar.

It should behave like a disciplined operating system:

**Watch the business.**

**Protect the customer.**

**Protect production.**

**Identify the constraint.**

**Choose the highest-value work.**

**Use the right specialist.**

**Stay inside authority.**

**Finish what was started.**

**Verify the result.**

**Measure whether it mattered.**

**Capture what was learned.**

**Escalate only when human judgment is actually required.**

That is the purpose of `SCHEDULER.md`.
