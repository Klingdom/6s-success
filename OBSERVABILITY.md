# 6S Success Observability and Autonomous Intelligence

> Canonical policy for technical telemetry, business telemetry, logs, metrics, traces, uptime, alerts, anomaly detection, deployment intelligence, data freshness, executive visibility, and evidence-driven autonomous improvement.

## 1. Purpose

`OBSERVABILITY.md` defines how Claude Code and specialist agents determine what is actually happening across 6S Success.

The goal is not to collect maximum telemetry.

The goal is to make the business and technology **observable enough to operate, diagnose, improve, and make decisions with evidence**.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `METRICS.md`
- `DATA-SOURCES.md`
- `DATA-CONTRACTS.md`
- `DASHBOARD.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `TESTING.md`
- `EXPERIMENTS.md`
- `BACKLOG.md`
- `DECISIONS.md`
- `LEARNINGS.md`

---

# 2. Core Principle

Claude must be able to distinguish:

**Healthy**

from

**Broken**

from

**Degraded**

from

**Unknown**

Never convert missing or stale telemetry into an assumed healthy state.

---

# 3. Observability Mission

The system should eventually answer, with evidence:

1. Is 6S-success.com available?
2. Is the intended release running?
3. Are containers healthy?
4. Are errors increasing?
5. Are pages fast enough?
6. Are critical customer journeys working?
7. Are analytics events arriving?
8. Can customers purchase?
9. Are quests being started and completed?
10. Are customers sustaining improvements?
11. Which acquisition channels create valuable outcomes?
12. Which products generate revenue?
13. What changed recently?
14. Did that change improve the business?
15. What requires attention now?
16. What is the largest constraint on growth or reliability?

---

# 4. Four Observability Layers

## Layer 1: Infrastructure

Hostinger VPS, CPU, memory, disk, network, Docker.

## Layer 2: Application

HTTP, API, errors, latency, jobs, dependencies.

## Layer 3: Customer Journey

Desired functions, micro-zones, quests, products, checkout, sustainment.

## Layer 4: Business

Traffic, conversion, revenue, retention, product performance, experiments, customer outcomes.

Claude should reason across all four.

---

# 5. Evidence Hierarchy

Prefer evidence closest to the actual outcome.

Example:

Weak:

`Deployment command returned success.`

Better:

`Container is healthy.`

Stronger:

`Application responds.`

Stronger still:

`Critical customer journey works.`

Business evidence:

`Purchases and conversion remain healthy after release.`

---

# 6. Telemetry Categories

Canonical categories:

- logs
- metrics
- traces
- health checks
- synthetic checks
- analytics events
- commerce events
- deployment events
- security signals
- test signals
- external search/discovery data
- customer feedback

Not every system requires every category immediately.

---

# 7. Source Authority

Every signal must have a defined source.

Examples:

- GitHub is authoritative for commit/CI state.
- Running Docker is authoritative for runtime container state.
- Commerce provider is authoritative for transaction truth.
- Analytics platform is authoritative for tracked behavioral events.
- Search platform is authoritative for its own search performance data.

Follow `DATA-SOURCES.md`.

---

# 8. Freshness

Every dashboard signal should carry:

```yaml
observed_at: datetime
source: string
freshness_seconds: integer
```

A metric without freshness can mislead autonomous decisions.

---

# 9. Staleness

Define acceptable freshness per signal.

Examples:

### Uptime

Minutes.

### Container health

Minutes.

### Revenue

Minutes to hours depending on source.

### Search performance

Often delayed by provider.

### Strategic learnings

Days/weeks.

Do not demand "real time" from sources that are inherently delayed.

---

# 10. Status Semantics

Use:

- `HEALTHY`
- `DEGRADED`
- `DOWN`
- `ATTENTION`
- `UNKNOWN`
- `NOT_APPLICABLE`

Avoid ambiguous states such as `OK-ish`.

---

# 11. Logs

Logs should answer:

**What happened?**

Useful fields:

```yaml
timestamp:
severity:
service:
environment:
release_id:
request_id:
event:
message:
context:
```

Use structured logging where the stack supports it.

---

# 12. Log Severity

Suggested:

- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

Do not log ordinary expected user behavior as errors.

---

# 13. Sensitive Logging

Never log:

- passwords
- API keys
- auth tokens
- private keys
- full payment data
- unnecessary household/private content

Follow `SECURITY.md`.

---

# 14. Request Correlation

Where practical, use a request/correlation ID so Claude can follow:

**Request**
→ **API**
→ **Database**
→ **External dependency**
→ **Response**

Do not use PII as the correlation key.

---

# 15. Release Correlation

Application logs and important events should identify the deployed release where practical.

Recommended:

```yaml
release_id:
commit_sha:
image_digest:
```

This allows Claude to answer:

**Did errors begin after release X?**

---

# 16. Infrastructure Metrics

Hostinger VPS should eventually expose or report:

- CPU utilization
- memory utilization
- swap
- disk utilization
- disk inode utilization where relevant
- network
- load
- uptime
- filesystem health signals where available

---

# 17. Docker Metrics

Track:

- container state
- health status
- restart count
- CPU
- memory
- unexpected exits
- image identity
- uptime

A running container is not automatically a healthy application.

---

# 18. Disk Monitoring

Disk exhaustion is a predictable failure.

Monitor:

- filesystem percentage
- absolute free space
- Docker image growth
- container logs
- backup growth
- uploaded assets
- database growth

Alert before emergency levels.

Do not automatically delete unknown data.

---

# 19. Application Metrics

Useful baseline:

- request count
- status-code distribution
- error rate
- latency
- dependency failures
- background-job failures
- queue depth if queues exist

Instrument only what architecture actually uses.

---

# 20. Latency

Prefer percentile views where available:

- p50
- p95
- p99

Average latency can hide poor experiences.

---

# 21. Error Rate

Distinguish:

- expected 4xx
- unexpected 4xx
- 5xx
- application exceptions
- dependency failures

Do not trigger incidents because bots request nonexistent URLs.

---

# 22. Health Endpoints

A useful health system may include:

## Liveness

Process exists.

## Readiness

Service can accept traffic.

## Dependency Health

Critical dependencies function.

Follow `RUNBOOK.md` for restart behavior.

---

# 23. Synthetic Monitoring

Synthetic checks should validate critical public behavior without harmful side effects.

Initial candidates:

1. homepage loads
2. Entryway page loads
3. desired-function entry point loads
4. quest entry point loads
5. product page loads
6. checkout initiation endpoint/page is available where safe

---

# 24. Business Telemetry

Technical observability must connect to customer outcomes.

Core business signals should eventually include:

- visitors
- acquisition source
- engaged visitors
- desired-function starts/completions
- micro-zone selections
- diagnoses
- quest impressions
- quest starts
- quest completions
- standards created
- sustainment checks
- product recommendations
- product views
- add-to-cart
- checkout starts
- purchases
- refunds
- revenue

---

# 25. Canonical Funnel

Where applicable:

**Visitor**
→ **Useful Content**
→ **Desired Function**
→ **Micro-Zone**
→ **Diagnosis**
→ **Quest**
→ **Standard**
→ **Product**
→ **Purchase**
→ **Sustainment**
→ **Next Quest**

Users need not traverse every stage.

---

# 26. Funnel Conversion

Every funnel rate must specify numerator and denominator.

Example:

```text
Quest Completion Rate =
completed quest sessions / started quest sessions
```

Do not label a rate simply "conversion" without definition.

---

# 27. Revenue Observability

At minimum distinguish:

- gross sales
- discounts
- refunds
- net sales/revenue as defined in `METRICS.md`
- number of orders
- average order value

Do not infer authoritative revenue only from client analytics events.

Reconcile with commerce source.

---

# 28. $20K Monthly Revenue Goal

The executive system may track progress toward a $20,000/month target.

It must not fabricate trajectory.

Useful views:

- month-to-date net revenue
- projected month-end revenue with method disclosed
- revenue by product
- revenue by acquisition source
- conversion
- AOV
- refunds

Forecasts must be labeled forecasts.

---

# 29. Product Observability

For each active product:

- impressions/recommendations
- product views
- cart adds
- checkout starts
- purchases
- revenue
- refund rate
- conversion
- source context
- root-cause/micro-zone context where available

This helps Claude improve products based on evidence.

---

# 30. Content Observability

For content:

- impressions/search visibility where available
- visits
- engagement
- CTA actions
- desired-function starts
- quest starts
- product views
- purchases attributable under defined model

Traffic alone is not the objective.

---

# 31. SEO Observability

Track, from authoritative search sources where available:

- impressions
- clicks
- CTR
- average position with caution
- indexed pages
- crawl/index errors
- sitemap health
- query/page performance

Do not treat ranking as a guaranteed stable number.

---

# 32. AEO Observability

AEO is less directly measurable.

Use available evidence such as:

- referral traffic from answer/AI systems where identifiable
- citations/referrals where legitimately observable
- question-page engagement
- branded query growth
- conversions from attributable sources

Do not fabricate "AI visibility" metrics.

---

# 33. Quest Observability

For each quest:

- impressions
- starts
- completion
- abandonment
- median/percentile duration
- cards completed
- player count
- repeat use
- next action

Segment by:

- room
- micro-zone
- desired function
- root cause
- duration
- player count

Only when sample size supports interpretation.

---

# 34. Card Observability

Useful signals:

- viewed
- claimed
- assigned
- completed
- skipped
- completion time where available
- abandonment association

Use this to improve decks, not to create surveillance.

---

# 35. Sustainment Observability

Long-term product value should eventually measure:

- standards created
- sustainment checks
- sustained
- partially sustained
- not sustained
- days since standard
- repeat friction

This provides evidence beyond "task completed once."

---

# 36. Desired Function Observability

Track:

- rooms where desired function is started
- functions selected
- completion
- drop-off
- relationship to quest choice
- relationship to product conversion
- relationship to sustainment

This should help personalize systems without sensitive profiling.

---

# 37. Root Cause Observability

Aggregate root causes can reveal product opportunities.

Examples:

- no home
- wrong home
- excess
- poor access
- capacity mismatch
- no standard

Use aggregated evidence to prioritize solutions.

---

# 38. Experiment Observability

For active experiments show:

- status
- hypothesis
- variants
- exposures
- primary metric
- guardrails
- data-quality state
- result confidence/decision criteria
- start date
- planned review

Follow `EXPERIMENTS.md`.

---

# 39. Deployment Observability

Every production deployment should record:

- release ID
- commit
- image/digest
- start
- completion
- result
- smoke-test result
- rollback if any

This enables change-impact analysis.

---

# 40. Change Annotation

Material changes should be visible on relevant metric timelines.

Examples:

- new homepage
- Entryway deck release
- pricing change
- checkout change
- SEO migration
- major campaign
- infrastructure incident

Correlation is not causation, but annotations improve diagnosis.

---

# 41. Test Observability

Executive quality signals may include:

- CI status
- critical E2E status
- smoke-test status
- flaky tests
- open critical defects
- security regression status

Follow `TESTING.md`.

---

# 42. Security Observability

Security signals may include:

- critical vulnerabilities
- secret-scan findings
- unexpected access changes
- suspicious auth failures
- exposed-port drift
- TLS health
- backup security state

Follow `SECURITY.md`.

---

# 43. Backup Observability

Track:

- last backup attempt
- last successful backup
- last verified artifact
- last restore test
- backup age
- backup failures

A green backup icon should mean more than "cron ran."

---

# 44. Alert Philosophy

An alert should indicate:

**Someone or some agent should consider acting now.**

If no action is needed, it is probably a dashboard metric, not an alert.

---

# 45. Alert Severity

Suggested:

## CRITICAL

Immediate material customer/business/security impact.

## HIGH

Serious degradation or imminent risk.

## MEDIUM

Action needed but not urgent.

## LOW

Informational improvement opportunity.

Avoid excessive paging.

---

# 46. Alert Requirements

Every alert should include:

- what happened
- affected system
- observed time
- evidence/source
- severity
- likely customer impact
- first diagnostic step
- relevant runbook

---

# 47. Alert Deduplication

Repeated identical failures should not flood the owner.

Group or suppress duplicates while preserving severity.

---

# 48. Alert Routing

Default:

- autonomous agent handles GREEN operational issues
- agent investigates YELLOW issues and acts within authority
- owner receives RED decisions and material incidents

Do not notify owner for every minor log warning.

---

# 49. Owner Notification Threshold

Notify when:

- customer-facing outage
- material commerce failure
- credible security incident
- high-risk data issue
- autonomy boundary requires approval
- major business metric anomaly persists and is actionable
- recovery cannot proceed safely without decision

---

# 50. Anomaly Detection

Use anomaly detection carefully.

Prefer:

- known thresholds for hard limits
- baseline comparison
- day-of-week/time-of-day awareness
- minimum sample sizes
- persistence requirements

Do not treat every fluctuation as meaningful.

---

# 51. Hard Thresholds

Good for:

- disk space
- certificate expiry
- service down
- failed backup
- crash loop
- payment webhook failure
- severe error rate

Thresholds should be calibrated after baseline discovery.

---

# 52. Business Anomalies

Potential anomalies:

- traffic suddenly drops
- quest completion collapses
- checkout starts but purchases disappear
- revenue drops unexpectedly
- refunds spike
- product recommendation CTR changes sharply

Investigate instrumentation before assuming customer behavior changed.

---

# 53. Data Quality Before Business Diagnosis

When a metric changes unexpectedly:

1. verify source freshness
2. verify event ingestion
3. verify release changes
4. verify filters
5. verify denominator
6. then interpret behavior

Broken tracking is often indistinguishable from broken behavior until checked.

---

# 54. Observability Data Quality

Track:

- missing fields
- invalid IDs
- duplicate events
- late events
- unknown schema versions
- source outages
- stale sources

Follow `DATA-CONTRACTS.md`.

---

# 55. Dashboard Architecture

The executive dashboard should summarize rather than reproduce every telemetry system.

Recommended sections:

1. Executive Scorecard
2. Revenue
3. Acquisition
4. Customer Journey
5. Quest/Product Performance
6. Experiments
7. Production Health
8. Security/Quality
9. Autonomous Work
10. Decisions Needed

---

# 56. Executive Scorecard

Candidate fields:

```yaml
business_status:
month_to_date_revenue:
monthly_target:
visitors:
purchase_conversion:
quest_starts:
quest_completion_rate:
sustained_improvements:
production_status:
current_release:
active_experiments:
critical_incidents:
owner_decisions_needed:
last_updated:
```

Use `UNKNOWN` when unavailable.

---

# 57. Autonomous Work Panel

Show what Claude is doing:

- current objective
- active backlog item
- agent responsible
- status
- last action
- next verification
- blocked reason
- owner approval required
- latest measurable result

This prevents invisible autonomy.

---

# 58. Decision Panel

Owner should see only decisions that truly need owner judgment.

Each decision:

- decision ID
- question
- recommendation
- expected upside
- risk
- cost
- deadline if any

Do not turn routine implementation choices into executive noise.

---

# 59. Near-Real-Time

"Near real time" means different things by source.

Target:

### Operational health

Minutes.

### Application errors

Minutes.

### Commerce

Minutes where provider supports it.

### Analytics

Minutes to hours.

### Search data

Provider-dependent and often delayed.

Display actual freshness.

---

# 60. Dashboard Confidence

Each important metric should support a confidence/data-quality state.

Example:

- `VERIFIED`
- `PARTIAL`
- `STALE`
- `UNKNOWN`

This is especially useful during early autonomous setup.

---

# 61. Telemetry Cost

Observability has cost.

Monitor:

- log ingestion
- metric cardinality
- trace volume
- storage
- retention
- vendor charges

Do not collect high-cardinality data without purpose.

---

# 62. Cardinality

Avoid unbounded labels such as:

- raw URL query strings
- user names
- arbitrary customer text
- request bodies

Use controlled dimensions and opaque IDs.

---

# 63. Sampling

High-volume traces/logs may be sampled.

Never sample away:

- critical errors
- security incidents
- payment failures
- deployment failures

unless another reliable record exists.

---

# 64. Retention

Different telemetry requires different retention.

Define based on:

- diagnostic need
- experiment windows
- legal/privacy requirements
- cost
- business learning value

Do not retain everything indefinitely.

---

# 65. Tracing

Distributed tracing becomes valuable if architecture includes multiple services or external dependencies.

Do not deploy complex tracing infrastructure before architecture warrants it.

---

# 66. External Dependency Monitoring

Where critical, observe:

- commerce provider
- analytics
- database
- email
- AI services
- storage
- external APIs

Distinguish internal failure from dependency failure.

---

# 67. AI Cost Observability

If AI/LLM APIs are used, track:

- requests
- errors
- latency
- token/usage cost
- feature
- model/provider
- outcome where possible

Do not expose prompts containing private data in executive dashboards.

---

# 68. AI Quality Observability

For AI-generated recommendations/content, measure:

- acceptance/use
- correction rate
- downstream completion
- customer feedback
- unsupported-output incidents

Do not use model confidence as proof of correctness.

---

# 69. Autonomous Agent Observability

For each agent track, where practical:

- task
- start/end
- tools/actions
- success/failure
- files/services changed
- tests run
- deployment
- measured outcome
- escalation

Avoid logging hidden reasoning or secrets.

---

# 70. Agent Performance

Useful metrics:

- tasks completed
- tasks reverted
- change failure rate
- owner escalations
- unnecessary escalations
- mean verification time
- measurable improvements delivered

Do not optimize agents merely for number of commits.

---

# 71. Autonomous Improvement Loop

Canonical loop:

**Observe**
→ **Detect Constraint**
→ **Diagnose**
→ **Prioritize**
→ **Change**
→ **Test**
→ **Deploy**
→ **Verify**
→ **Measure**
→ **Learn**
→ **Standardize**
→ **Observe Again**

Observability closes the loop.

---

# 72. Constraint Detection

Claude should prioritize constraints with evidence.

Potential examples:

- traffic constraint
- content relevance constraint
- desired-function drop-off
- quest completion problem
- product mismatch
- checkout friction
- reliability problem
- slow deployment
- data-quality gap

Do not assume SEO is always the constraint.

---

# 73. Metric Guardrails

An optimization should not improve one metric by damaging another critical metric.

Example:

Higher checkout conversion

must not come from

misleading pricing or increased refunds.

Use guardrails defined in `METRICS.md` and `EXPERIMENTS.md`.

---

# 74. Causality

Observability shows correlation.

Experiments and stronger analysis help establish causality.

Claude must not claim:

"Change X caused +20% revenue"

solely because revenue rose after deployment.

---

# 75. Baselines

Before optimizing a metric, establish a baseline when practical.

Record:

- period
- value
- source
- filters
- known anomalies
- sample size

---

# 76. Comparisons

Use meaningful comparisons:

- previous comparable period
- experiment control
- baseline
- target
- cohort

Avoid cherry-picked comparisons.

---

# 77. Cohorts

Useful future cohorts may include:

- acquisition source
- room
- micro-zone
- desired function
- quest
- product
- new vs returning

Do not create sensitive demographic profiling without legitimate need.

---

# 78. Attribution

Revenue attribution must state model.

Possible models:

- last non-direct
- first touch
- direct campaign
- content-assisted
- experiment assignment

Do not present attribution as objective truth when model-dependent.

---

# 79. Customer Feedback

Qualitative evidence should complement metrics.

Potential sources:

- support
- surveys
- beta feedback
- product reviews
- quest feedback

Aggregate and sanitize private information.

---

# 80. Feedback-to-Backlog

Repeated customer friction should create backlog candidates with evidence.

Do not create a feature for every individual suggestion.

Look for patterns.

---

# 81. Observability and Root Cause

Use structured diagnosis:

**Symptom**
→ **Where**
→ **When**
→ **What Changed**
→ **Who/What Affected**
→ **Evidence**
→ **Root Cause**
→ **Corrective Action**

Avoid jumping from symptom to solution.

---

# 82. Incident Correlation

During an incident, correlate:

- deployment
- infrastructure
- errors
- latency
- dependencies
- business funnel

This reduces blind restarts.

---

# 83. Runbook Links

Alerts should point to the relevant procedure in `RUNBOOK.md`.

Observability detects.

Runbook guides response.

---

# 84. Test Links

Quality failures should connect to `TESTING.md`.

Example:

Critical E2E fails
→ block deployment
→ diagnose
→ repair
→ rerun
→ verify.

---

# 85. Security Links

Security signals follow `SECURITY.md`.

Do not automatically "fix" high-risk security anomalies without respecting authority.

---

# 86. Unknown-State Backlog

Material unknowns are work.

Examples:

- backup status unknown
- production commit unknown
- checkout telemetry unknown
- database exposure unknown

Create prioritized discovery items.

---

# 87. Initial Observability Stack

Do not install a giant observability platform immediately.

First discover what already exists.

Then fill the highest-value gaps.

Initial minimum:

- uptime
- release identity
- container health
- severe application errors
- disk
- backup state
- critical smoke tests
- analytics health
- commerce health

---

# 88. Build vs Buy

Use existing platform capabilities when they satisfy the need.

Do not add vendors merely because they are popular.

Evaluate:

- capability
- integration
- cost
- operational burden
- lock-in
- privacy
- scale

---

# 89. Open Standards

Where practical, prefer telemetry formats that preserve portability.

Do not force architectural complexity solely for theoretical future portability.

---

# 90. Executive Alert Example

Good:

> Checkout purchase confirmations dropped to zero while checkout starts remain normal. Commerce webhook failures began 8 minutes after release `abc123`. Production remains available. Recommend rolling back the checkout integration release. No owner approval required if rollback is GREEN under AUTONOMY.md.

Bad:

> Something seems wrong with sales.

---

# 91. Business Opportunity Alert Example

Good:

> Entryway "fast exit" visitors complete quests at 42%, versus 18% for "visual calm" over the last 30 days. Sample sizes are 214 and 176 starts. Recommend reviewing the visual-calm quest/card sequence before increasing acquisition spend.

Do not alert on tiny samples.

---

# 92. Owner Dashboard Principle

The owner should be able to open one dashboard and understand in under two minutes:

**Are we healthy?**

**Are we growing?**

**What is working?**

**What is not?**

**What is Claude doing?**

**What decision do I need to make?**

---

# 93. Daily Autonomous Observability Cycle

Claude may:

1. verify telemetry freshness
2. verify production health
3. inspect critical alerts
4. inspect failed jobs/deployments
5. inspect business funnel anomalies
6. verify commerce reconciliation
7. verify analytics health
8. identify highest-value actionable constraint
9. update status/backlog when warranted
10. act within authority

Do not make changes merely because a metric moved.

---

# 94. Weekly Intelligence Review

Review:

- acquisition
- customer journey
- quests
- products
- revenue
- experiments
- production reliability
- security
- quality
- autonomous agent effectiveness

Select the highest-leverage improvement themes.

---

# 95. Monthly Executive Review

Summarize:

## Business

Revenue, customers, conversion, product performance.

## Customer Outcomes

Quest completion and sustainment.

## Growth

SEO/AEO/content/acquisition.

## Product

What is being used and purchased.

## Experiments

What was learned.

## Technology

Reliability, performance, deployment.

## Risk

Security, backups, critical unknowns.

## Autonomous System

What Claude improved and what requires owner decisions.

---

# 96. Current Observability State

Populate from verified discovery only:

```yaml
production:
  domain: 6S-success.com
  uptime_monitor: UNKNOWN
  health_endpoint: UNKNOWN
  current_release_tracking: UNKNOWN

hostinger_vps:
  cpu_monitoring: UNKNOWN
  memory_monitoring: UNKNOWN
  disk_monitoring: UNKNOWN

docker:
  container_health: UNKNOWN
  restart_monitoring: UNKNOWN
  resource_monitoring: UNKNOWN

application:
  structured_logs: UNKNOWN
  error_monitoring: UNKNOWN
  latency_monitoring: UNKNOWN
  request_correlation: UNKNOWN

analytics:
  provider: UNKNOWN
  event_health: UNKNOWN
  funnel_dashboard: UNKNOWN

commerce:
  provider: UNKNOWN
  transaction_reconciliation: UNKNOWN
  webhook_monitoring: UNKNOWN

seo:
  search_data_source: UNKNOWN
  indexing_monitoring: UNKNOWN

testing:
  ci_status: UNKNOWN
  e2e_status: UNKNOWN
  production_smoke: UNKNOWN

security:
  vulnerability_monitoring: UNKNOWN
  secret_scan: UNKNOWN
  tls_monitoring: UNKNOWN

backup:
  job_monitoring: UNKNOWN
  artifact_verification: UNKNOWN
  restore_test: UNKNOWN

executive_dashboard:
  implementation: UNKNOWN
  freshness_display: UNKNOWN
```

---

# 97. First Observability Mission

Once Claude has legitimate access:

1. discover existing telemetry
2. map sources
3. identify production release
4. establish uptime visibility
5. establish Docker/runtime visibility
6. establish error visibility
7. establish disk visibility
8. establish backup visibility
9. verify analytics
10. verify commerce telemetry if commerce exists
11. establish critical smoke-test signal
12. connect signals to executive dashboard
13. document freshness
14. identify blind spots
15. create prioritized backlog

Do not replace working tools without evidence.

---

# 98. Observability Maturity Model

## Level 0: Blind

Health and business state largely unknown.

## Level 1: Visible

Core infrastructure and business metrics can be inspected.

## Level 2: Correlated

Releases, errors, customer behavior, and revenue can be connected.

## Level 3: Actionable

Alerts reliably identify conditions requiring action.

## Level 4: Self-Diagnosing

Claude can automatically gather evidence and identify likely root cause.

## Level 5: Self-Improving

Telemetry continuously identifies constraints, launches safe improvements, verifies outcomes, captures learning, and updates standards.

---

# 99. Definition of Observable

A critical system is observable when Claude can answer:

- current state
- last known good state
- freshness
- source
- recent changes
- likely cause of abnormal behavior
- customer impact
- safe next action

without guessing.

---

# 100. Final Principle

Autonomy without observability is guesswork.

Observability without action is reporting.

The 6S Success autonomous operating model should combine:

**Observe**
+ **Understand**
+ **Act Safely**
+ **Verify**
+ **Learn**

The executive dashboard is not merely a collection of charts.

It is the human-facing control surface for an autonomous business system.

Claude should continuously transform raw telemetry into:

**What happened?**

**Why does it matter?**

**What should happen next?**

**Can Claude safely do it?**

**Did it work?**

That is the purpose of `OBSERVABILITY.md`.
