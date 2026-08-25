> **This is the SPECIFICATION, not the dashboard.** It defines what the
> executive view should contain. The generated output lives in
> [`EXECUTIVE-DASHBOARD-LIVE.md`](EXECUTIVE-DASHBOARD-LIVE.md), written by
> `python ops/dashboard.py`, and that is the file to read for current
> state. Issue #8 flagged the two as duplicates. They are not, but the
> names collided badly enough that somebody read the spec as the report.

# 6S Success Executive Dashboard

> Canonical owner dashboard specification for 6S-success.com. Defines the near-real-time executive view Claude should maintain across customer outcomes, revenue, growth, SEO/AEO, products, quests, GitHub, Hostinger VPS/Docker, security, costs, experiments, autonomous work, risks, and decisions.

## 1. Purpose

`EXECUTIVE-DASHBOARD.md` defines the single management surface for the autonomous 6S Success operating system.

The dashboard should let the owner answer, in roughly 60 seconds:

1. Is the business healthy?
2. Is the website working?
3. Are customers getting value?
4. Are we making money?
5. Are we moving toward the $20K/month target?
6. What is Claude working on?
7. What changed?
8. What is the current constraint?
9. What is at risk?
10. What requires my decision?

The dashboard is not a data dump.

It is a **decision system**.

---

# 2. Executive Dashboard Principle

**Show the smallest amount of information needed to understand business state, autonomous activity, risk, and next decisions.**

Detailed operational information should remain drillable.

---

# 3. Dashboard Hierarchy

The primary dashboard should have seven executive sections:

1. **Command Center**
2. **Customer Outcomes**
3. **Growth & Revenue**
4. **Quests & Products**
5. **Technology & Operations**
6. **Autonomous Work**
7. **Decisions & Risks**

---

# 4. Command Center

Top of screen should immediately show:

```yaml
overall_status:
monthly_revenue_target:
revenue_mtd:
projected_month_end:
successful_micro_zone_outcomes:
current_growth_constraint:
production_status:
autonomy_status:
critical_risks:
owner_decisions_required:
data_freshness:
```

Use actual authoritative data only.

---

# 5. Overall Status

Use:

- `GREEN`
- `YELLOW`
- `RED`
- `UNKNOWN`

Meaning:

## GREEN

Business and production are operating within defined guardrails.

## YELLOW

Material issue or risk requires attention but does not constitute critical failure.

## RED

Critical customer, revenue, security, data, or production problem.

## UNKNOWN

Required evidence is unavailable or stale.

Never convert UNKNOWN to GREEN.

---

# 6. Revenue Target

Current strategic target:

```yaml
monthly_revenue_target_usd: 20000
```

Display:

- target
- actual MTD
- percent to target
- projected month-end
- gap

Clearly distinguish target, actual, and projection.

---

# 7. Revenue Progress

Potential display:

```text
August Target        $20,000
Revenue MTD           $8,450
Target Progress          42%
Projected Month       $18,900
Projected Gap          $1,100
```

Numbers above are illustrative only.

Never use them as actual data.

---

# 8. Customer Outcome Hero Metric

Candidate:

**Successful Micro-Zone Outcomes**

Display:

- today
- last 7 days
- month to date
- trend

Formal definition belongs in `METRICS.md`.

---

# 9. Current Constraint

Display one primary constraint.

Examples:

```text
Current Constraint: Quest Start Rate
Current Constraint: Organic Discovery
Current Constraint: Checkout Completion
Current Constraint: Product Fit
```

Include:

- evidence
- affected metric
- active response

---

# 10. Claude Current Mission

Show one concise statement:

> Improve Entryway quest activation by simplifying desired-function selection and measuring the effect.

Not:

> Working on website.

---

# 11. Customer Outcomes Section

Display:

- qualified visitors
- diagnoses completed
- quest starts
- quest completions
- successful outcomes
- sustainment
- repeat quests

The dashboard should emphasize progression to value.

---

# 12. Customer Funnel

Canonical funnel:

```text
Qualified Visitor
↓
Diagnosis
↓
Quest Start
↓
Quest Completion
↓
Successful Outcome
↓
Next Quest
```

Show conversion between stages.

---

# 13. Funnel Visualization

Each stage should display:

- count
- conversion
- trend
- comparison period

Avoid decorative funnels that hide numbers.

---

# 14. Outcome Segmentation

Allow drill-down by:

- room
- micro-zone
- desired function
- root cause
- quest duration
- player count
- acquisition source

Do not overload the executive default view.

---

# 15. Entryway Scorecard

Until the prototype is proven, Entryway deserves a dedicated card.

Suggested:

```yaml
entryway:
  visitors:
  diagnoses:
  quest_starts:
  quest_completion_rate:
  successful_outcomes:
  product_revenue:
  repeat_micro_zone_rate:
  active_experiments:
  maturity:
```

---

# 16. Room Expansion Readiness

Show:

```text
Entryway: VALIDATING
Kitchen: NOT STARTED
Bathroom: NOT STARTED
```

Use actual taxonomy/status.

Do not imply readiness without evidence.

---

# 17. Growth & Revenue Section

Display:

- qualified visitors
- revenue
- orders
- conversion
- AOV
- contribution margin
- refunds
- repeat purchase/quest
- target trajectory

---

# 18. Revenue by Source

Where attribution is reliable:

- organic search
- AI referral
- social
- direct
- email
- referral
- paid

Use `UNKNOWN` when attribution is insufficient.

---

# 19. Revenue by Room

Potential:

```text
Entryway
Bathroom
Kitchen
Laundry
Other
```

Only display when products map reliably to canonical room IDs.

---

# 20. Revenue by Product Type

Potential:

- digital
- physical
- deck
- kit
- 3D print
- service
- third party

---

# 21. Contribution Margin

Revenue alone is insufficient.

Display:

```yaml
revenue:
variable_cost:
payment_fees:
fulfillment:
approved_acquisition_cost:
contribution_margin:
```

Follow `COST-GOVERNANCE.md`.

---

# 22. Refunds

Display:

- count
- value
- rate
- leading reason

Refund spikes may indicate:

- product mismatch
- sizing problem
- fulfillment
- unclear expectations
- quality

---

# 23. Acquisition

Show channel health.

Suggested executive view:

| Channel | Qualified Visitors | Activation | Revenue | Trend |
|---|---:|---:|---:|---|
| Organic | | | | |
| AI/AEO | | | | |
| Social | | | | |
| Direct | | | | |
| Referral | | | | |

Populate only from verified data.

---

# 24. SEO Executive Card

Show:

- organic clicks
- impressions
- qualified organic visitors
- indexed high-value pages
- top opportunity
- major technical issue

Do not show dozens of keyword positions by default.

---

# 25. AEO Executive Card

Where measurable:

- AI referral sessions
- AI referral conversions
- high-value answer pages
- structured-data health
- top AEO opportunity

Do not claim visibility inside AI systems without evidence.

---

# 26. Content Performance

Rank content by useful outcomes, not pageviews alone.

Potential score:

```text
Qualified Visits
→ Diagnosis
→ Quest Start
→ Outcome
→ Revenue
```

---

# 27. Top Content Opportunities

Show 3-5 only.

Example:

```yaml
topic:
room:
micro_zone:
evidence:
opportunity:
recommended_action:
```

---

# 28. Quests Section

Display:

- active quest definitions
- starts
- completion
- median completion time
- card skip/block rate
- multiplayer usage
- outcome success

---

# 29. Quest Performance Table

Potential:

| Quest | Starts | Completion | Outcome Success | Revenue Assisted |
|---|---:|---:|---:|---:|
| | | | | |

Revenue-assisted must be defined carefully.

---

# 30. Card Intelligence

Identify:

- most completed
- most skipped
- most blocked
- longest
- strongest outcome association

Use this to improve decks.

---

# 31. Multiplayer Card

Display:

- multiplayer quests
- average players
- completion
- comparison with solo
- most effective assignment mode

Only when sufficient data exists.

---

# 32. Product Section

Display:

- active products
- active kits
- active services
- product revenue
- product margin
- recommendation acceptance
- refunds
- inventory risks

---

# 33. Product Performance

Potential table:

| Product | Recommendations | Purchases | Revenue | Margin | Outcome |
|---|---:|---:|---:|---:|---:|
| | | | | | |

Outcome is more important than conversion alone.

---

# 34. Product Opportunity

Show:

**Highest-value unsolved customer problem**

Example structure:

```yaml
micro_zone:
root_cause:
frequency:
current_solution_gap:
potential_product:
evidence:
```

---

# 35. Inventory Risk

Show only actionable conditions:

- out of stock
- below reorder
- excessive inventory
- stale inventory
- fulfillment issue

Do not clutter the executive view with normal SKU counts.

---

# 36. Commerce Health

Display:

```yaml
checkout_status:
payment_status:
order_processing:
digital_delivery:
fulfillment:
refund_processing:
last_verified:
```

---

# 37. Technology & Operations

Executive technology view:

- production
- website availability
- latency/performance
- error rate
- latest release
- GitHub
- VPS/Docker
- backup
- security
- scheduler

---

# 38. Production Status

Show:

```text
Production: HEALTHY
Last Deploy: 2h ago
Release: abc123
Smoke Tests: PASS
```

Actual values only.

---

# 39. GitHub Card

GitHub Manager supplies:

```yaml
default_branch:
latest_commit:
open_prs:
failed_workflows:
security_alerts:
stale_high_priority_prs:
branch_protection:
last_verified:
```

Executive view should show only exceptions and current release lineage.

---

# 40. Hostinger VPS / Docker Card

VPS Manager supplies:

```yaml
host_status:
cpu:
memory:
disk:
containers_running:
containers_unhealthy:
restart_anomalies:
public_ports:
last_backup:
last_verified:
```

Highlight risk, not routine detail.

---

# 41. Deployment Card

Display:

- latest production release
- status
- commit
- deployment duration
- smoke test
- rollback readiness

---

# 42. Availability

Track meaningful customer availability.

Potential:

```yaml
availability_24h:
availability_7d:
critical_endpoint_status:
```

Formal SLO belongs elsewhere.

---

# 43. Performance

Executive metrics may include:

- LCP / Core Web Vitals
- API latency
- checkout latency

Only show metrics that affect customer experience.

---

# 44. Errors

Display:

- critical errors
- change vs baseline
- top unresolved customer-impacting error

Do not show every log exception.

---

# 45. Backup & Recovery

Show:

```yaml
latest_backup:
backup_status:
latest_restore_test:
restore_test_status:
rpo_risk:
rto_risk:
```

A successful backup is not equivalent to a verified restore.

---

# 46. Security

Show:

- critical findings
- high findings
- exposed secret incidents
- dependency criticals
- suspicious auth/access issues
- unresolved security decisions

Do not expose secrets on dashboard.

---

# 47. Scheduler

Display:

```yaml
scheduler_status:
last_heartbeat:
active_jobs:
failed_jobs_24h:
stale_locks:
paused_jobs:
```

Follow `SCHEDULER.md`.

---

# 48. Cost Section

Show:

- infrastructure MTD
- AI/API MTD
- SaaS MTD
- commerce fees
- approved acquisition
- total operating cost
- cost anomaly

---

# 49. AI Cost

Because autonomous agents may generate substantial usage, show:

```yaml
ai_cost_today:
ai_cost_mtd:
top_cost_agent:
top_cost_job:
cost_anomaly:
```

Use provider billing data where possible.

---

# 50. Cost Efficiency

Potential:

```text
AI Cost per Successful Micro-Zone Outcome
Infrastructure Cost per 1,000 Qualified Visits
```

Use only when data is meaningful.

---

# 51. Autonomous Work Section

This is critical.

The owner should see what Claude is doing without reading Git logs.

Show:

- current mission
- active agents
- recently completed work
- current experiment
- queued high-priority work
- blocked work
- approvals needed

---

# 52. Active Agent Table

Potential:

| Agent | Task | Status | Started | Risk |
|---|---|---|---|---|
| | | | | |

Only show currently meaningful tasks.

---

# 53. Recently Completed

Show 3-10 high-value items.

Example:

> Improved Entryway key-landing page internal links and deployed release `abc123`. Search/activation impact pending.

Separate action from outcome.

---

# 54. Action vs Result

Dashboard must distinguish:

**Action**
> Published revised Entryway page.

from:

**Result**
> Quest-start conversion increased 11%.

Do not claim an action caused a result without sufficient evidence.

---

# 55. Autonomous Change Feed

Every material change should link to evidence where possible:

- task
- PR
- commit
- release
- experiment
- decision
- metric

This creates auditability.

---

# 56. Current Experiment

Show:

```yaml
experiment_id:
hypothesis:
primary_metric:
guardrails:
started:
status:
decision_date_or_rule:
```

Do not declare winners early.

---

# 57. Experiment Portfolio

Executive view:

- active
- completed this month
- winners
- losers
- inconclusive
- estimated impact

---

# 58. Backlog

Show only:

- top 3 autonomous priorities
- blocked high-value work
- owner-dependent work

Do not show a 200-item backlog by default.

---

# 59. Current Constraint Card

This should be one of the most prominent components.

Example:

```yaml
constraint: Entryway quest activation
evidence: 68% of qualified visitors leave before quest start
hypothesis: desired-function selection is too complex
active_action: simplify selection to 4 primary outcomes
metric: quest_start_rate
status: EXPERIMENTING
```

Values above are illustrative.

---

# 60. Decisions & Risks

Separate:

## Decisions Needed

Human judgment/authority required.

## Risks

Claude can manage but owner should know.

## Incidents

Something has failed.

Do not mix them.

---

# 61. Decision Card

Each decision should include:

```yaml
decision_id:
question:
why_now:
options:
recommended_option:
expected_value:
cost:
risk:
deadline:
authority_required:
```

---

# 62. Decision Quality

Do not ask:

> Should I improve SEO?

Ask:

> Search Console shows high impressions but low CTR on five Entryway pages. I recommend rewriting titles/descriptions and testing them. No new spend required. Approve only if this falls outside current autonomous content authority.

Where authority already exists, do not unnecessarily ask.

---

# 63. Financial Approval Card

For spending decisions:

```yaml
proposal:
one_time_cost:
monthly_cost:
expected_value:
payback_assumption:
stop_loss:
alternatives:
recommendation:
```

Follow `COST-GOVERNANCE.md`.

---

# 64. Risk Card

Each material risk:

```yaml
risk_id:
category:
description:
probability:
impact:
status:
mitigation:
owner:
```

---

# 65. Risk Categories

Potential:

- CUSTOMER
- REVENUE
- SECURITY
- PRIVACY
- PRODUCTION
- DATA
- COST
- LEGAL
- SUPPLY
- REPUTATION

---

# 66. Incident Card

Display:

- severity
- started
- customer impact
- current state
- mitigation
- next update

Resolved incidents should move to history.

---

# 67. Data Freshness

Every dashboard card must know freshness.

Suggested:

```yaml
source:
observed_at:
expected_refresh:
freshness_status:
```

Use:

- `FRESH`
- `STALE`
- `FAILED`
- `UNKNOWN`

---

# 68. Near Real Time

Not every metric needs second-level updates.

Suggested expectations:

## 1-5 minutes

- production health
- critical errors
- checkout failure
- incidents

## 15-60 minutes

- orders
- revenue
- autonomous jobs
- experiments

## Daily

- SEO
- content
- many customer metrics

## Weekly/Monthly

- strategic trend metrics

Use the minimum useful refresh rate.

---

# 69. Source of Truth

Each metric must identify authoritative source.

Potential:

```yaml
metric_id:
source_system:
query_or_endpoint:
refresh_job:
owner_agent:
```

Do not calculate the same metric differently in multiple agents.

---

# 70. Metric Registry

Maintain a canonical metric registry.

Suggested:

```yaml
metric_id:
name:
definition:
formula:
source:
grain:
timezone:
refresh:
owner:
quality_checks:
```

Formal definitions belong in `METRICS.md`.

---

# 71. Dashboard Data Architecture

Preferred pattern:

```text
Source Systems
↓
Collectors / APIs
↓
Canonical Metrics Layer
↓
Dashboard API
↓
Executive UI
```

Avoid the browser independently querying every provider.

---

# 72. Potential Data Sources

Discover actual providers.

Potential categories:

- website analytics
- Search Console
- commerce
- GitHub
- VPS telemetry
- Docker
- application database
- error monitoring
- AI provider billing
- uptime
- email
- product inventory

Do not assume a specific provider is installed.

---

# 73. Dashboard API

The dashboard should consume normalized data.

Potential conceptual endpoint:

```text
/api/executive/summary
```

Actual architecture should match the project.

---

# 74. Dashboard Snapshot

Persist periodic snapshots where useful.

Benefits:

- historical trend
- audit
- comparison
- outage resilience

Do not store sensitive raw data unnecessarily.

---

# 75. Owner View vs Agent View

## Owner View

Concise, decision-oriented.

## Agent View

Detailed operational diagnostics.

Do not expose all agent internals in the executive view.

---

# 76. Mobile First

The owner dashboard should work well on a smartphone.

First screen should show:

- status
- revenue target
- customer outcome
- current constraint
- Claude mission
- decisions needed

---

# 77. Desktop View

Desktop may add:

- trends
- funnel
- agent activity
- infrastructure
- experiments
- deeper tables

---

# 78. Color

Use color only for meaning.

Suggested semantic use:

- green = healthy
- amber = attention
- red = critical
- gray = unknown/inactive

Do not rely on color alone for accessibility.

---

# 79. Trend Indicators

Use:

- ↑ improving
- → stable
- ↓ worsening

Direction must account for metric meaning.

A falling refund rate is positive.

---

# 80. Comparison Windows

Default:

- today vs comparable prior period
- 7 days vs prior 7 days
- MTD vs comparable prior month period

Avoid misleading partial-month comparisons.

---

# 81. Statistical Noise

Do not label small changes as meaningful without sufficient volume.

Use confidence where appropriate.

---

# 82. Forecasts

Forecast display must identify method and confidence.

Example:

```yaml
projection:
method:
confidence:
last_updated:
```

---

# 83. Executive Narrative

Claude should generate a short dashboard summary.

Maximum useful structure:

## What Changed

2-4 material changes.

## Why It Matters

Business/customer implication.

## What Claude Is Doing

Current response.

## What You Need to Decide

Only if necessary.

---

# 84. Example Narrative

> Revenue is tracking below the monthly target, but Entryway quest completion improved this week. The largest current leak is between diagnosis and quest start. Claude is testing a shorter desired-function flow before increasing acquisition. Production, checkout, backups, and security are healthy. No owner decision is currently required.

This is illustrative only.

---

# 85. Daily Owner Brief

Generate once daily when configured.

Keep concise.

Include:

- status
- revenue
- customer outcomes
- constraint
- autonomous work
- risks
- decisions

---

# 86. Weekly Owner Brief

Include:

- performance
- learning
- experiments
- product/quest changes
- technology
- costs
- next priorities

---

# 87. Monthly Executive Review

Include:

- $20K target performance
- contribution margin
- customer outcomes
- acquisition
- retention
- product portfolio
- Entryway maturity
- whole-home expansion recommendation
- autonomous system performance

---

# 88. Dashboard Alerts

Only alert the owner when useful.

Immediate examples:

- production outage
- checkout failure
- critical security issue
- data-loss risk
- runaway cost
- owner approval blocking critical work

Everything else can enter dashboard/brief.

---

# 89. Notification Fatigue

Do not notify for:

- routine deployments
- normal metric noise
- successful scheduled jobs
- every content publication
- low-priority backlog changes

---

# 90. Dashboard Security

Dashboard may expose sensitive business information.

Requirements:

- authentication
- authorization
- TLS
- no secrets
- secure session handling
- least privilege
- audit where appropriate

Do not expose dashboard publicly.

---

# 91. Dashboard Privacy

Avoid unnecessary customer-level personal data.

Executive metrics should generally be aggregated.

---

# 92. Dashboard Reliability

If one provider fails, dashboard should:

- show affected metric as stale/unknown
- preserve other sections
- identify data-source failure

Do not crash the entire dashboard.

---

# 93. Dashboard Performance

Executive dashboard should load quickly.

Prefer:

- cached summaries
- asynchronous collectors
- normalized API

Avoid dozens of slow provider calls during page load.

---

# 94. Dashboard Observability

Monitor:

- dashboard availability
- API errors
- collector failures
- metric freshness
- refresh duration

---

# 95. Dashboard Testing

Test:

- missing data
- stale data
- zero revenue
- provider failure
- negative trends
- critical alert
- no decisions
- mobile layout
- authorization
- large numbers
- timezone boundaries

---

# 96. Dashboard Release

Dashboard changes follow normal GitHub/release controls.

Do not bypass deployment policy because it is "internal."

---

# 97. Autonomous System Scorecard

Potential executive indicators:

```yaml
autonomous_tasks_completed:
autonomous_changes_reverted:
failed_jobs:
owner_escalations:
estimated_value_created:
ai_cost:
automation_efficiency:
```

Avoid invented "value created."

Use measurable evidence.

---

# 98. Autonomy Health

Use:

- `HEALTHY`
- `LIMITED`
- `PAUSED`
- `DEGRADED`
- `UNKNOWN`

---

# 99. Agent Performance

Monthly, evaluate agents on:

- completed useful work
- failure rate
- revert rate
- cost
- quality
- unnecessary escalations
- policy violations

Do not optimize agent performance by raw task count.

---

# 100. Executive Action Buttons

Where safely implemented, dashboard may support controlled actions such as:

- pause autonomous writes
- pause publishing
- pause deployments
- pause experiments
- approve/reject decision
- open incident
- view release
- view GitHub PR

High-risk actions require appropriate confirmation and authorization.

---

# 101. Global Pause

The dashboard should expose autonomy state and, when safely implemented, a clear global pause mechanism.

This should preserve:

- monitoring
- backups
- owner access

while stopping noncritical autonomous writes.

---

# 102. Drill-Down Pages

Potential:

- `/executive`
- `/executive/growth`
- `/executive/customers`
- `/executive/quests`
- `/executive/products`
- `/executive/technology`
- `/executive/agents`
- `/executive/costs`
- `/executive/decisions`

Actual routes should fit the application.

---

# 103. Executive Dashboard Data Contract

Conceptual:

```yaml
generated_at:
overall:
customer:
growth:
revenue:
quests:
products:
technology:
costs:
autonomy:
experiments:
risks:
decisions:
freshness:
```

Formal schema belongs in `DATA-CONTRACTS.md`.

---

# 104. Current Dashboard State

Populate only from verified evidence:

```yaml
dashboard:
  exists: UNKNOWN
  url: UNKNOWN
  authentication: UNKNOWN
  mobile_ready: UNKNOWN
  last_verified: UNKNOWN

data_sources:
  analytics: UNKNOWN
  search: UNKNOWN
  commerce: UNKNOWN
  github: UNKNOWN
  vps: UNKNOWN
  docker: UNKNOWN
  errors: UNKNOWN
  ai_billing: UNKNOWN

metrics:
  revenue: UNKNOWN
  contribution_margin: UNKNOWN
  successful_micro_zone_outcomes: UNKNOWN
  quest_completion: UNKNOWN
  activation: UNKNOWN
  retention: UNKNOWN

operations:
  production_health: UNKNOWN
  deployment_status: UNKNOWN
  backup_status: UNKNOWN
  security_status: UNKNOWN
  scheduler_status: UNKNOWN

autonomy:
  current_mission: UNKNOWN
  active_agents: UNKNOWN
  recent_changes: UNKNOWN
  pause_control: UNKNOWN

governance:
  decisions: UNKNOWN
  risks: UNKNOWN
  approvals: UNKNOWN

freshness:
  status: UNKNOWN
```

Never replace UNKNOWN with assumptions.

---

# 105. First Dashboard Mission

Once Claude has legitimate access:

1. inventory available data sources
2. verify authentication/permissions
3. identify authoritative source for every critical metric
4. create metric registry
5. establish freshness expectations
6. build normalized summary layer
7. build Command Center
8. add customer outcome funnel
9. add revenue/target view
10. add Entryway scorecard
11. add production/GitHub/VPS cards
12. add autonomous-work panel
13. add decisions/risks
14. add mobile layout
15. add data-quality states
16. connect scheduler refresh jobs
17. test failure modes
18. document dashboard URL and access
19. update Current Dashboard State
20. create dashboard improvement backlog

Do not fabricate unavailable metrics to make the dashboard look complete.

---

# 106. Minimum Viable Executive Dashboard

Version 1 should include:

1. overall status
2. revenue target vs actual
3. customer outcome metric
4. Entryway funnel
5. current growth constraint
6. production status
7. latest release
8. GitHub health
9. VPS/Docker health
10. cost MTD
11. Claude current mission
12. active experiment
13. top risks
14. owner decisions required
15. data freshness

---

# 107. Dashboard Maturity Model

## Level 0: Reports

Manual data collection.

## Level 1: Visibility

Core business and technical metrics displayed.

## Level 2: Integrated

Customer, revenue, product, GitHub, VPS, and autonomous activity share one view.

## Level 3: Decision-Oriented

Dashboard identifies constraints, risks, and required decisions.

## Level 4: Adaptive

Claude uses the same metrics to prioritize autonomous work and continuously updates recommendations.

## Level 5: Autonomous Executive Operating System

The dashboard becomes the owner's control plane for a continuously improving business. Claude and specialist agents operate the system, evidence is near real time, risks and decisions are surfaced clearly, and the owner can understand or intervene without managing routine execution.

---

# 108. Non-Negotiable Dashboard Rules

Claude and subagents must not:

- fabricate metrics
- replace UNKNOWN with zero
- replace UNKNOWN with healthy
- present projections as actuals
- call revenue MRR unless recurring
- hide stale data
- hide failed autonomous jobs
- claim causal impact without evidence
- expose secrets
- expose unnecessary customer PII
- overload the executive screen with operational noise
- optimize dashboard appearance over decision usefulness
- bury critical owner decisions
- use vanity metrics as primary business success
- report task volume as autonomous value

---

# 109. Final Principle

The owner should not need to manage Claude, GitHub, Hostinger, Docker, SEO, content, quests, products, experiments, analytics, and commerce as separate systems.

The executive dashboard should collapse them into one understandable operating picture:

**Are customers succeeding?**

**Are we growing?**

**Are we profitable?**

**What is constraining growth?**

**Is production healthy?**

**What is Claude doing about it?**

**What changed?**

**What is at risk?**

**What needs my decision?**

Everything else should be autonomous, governed, measurable, and drillable.

That is the purpose of `EXECUTIVE-DASHBOARD.md`.
