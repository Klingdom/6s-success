# 6S Success Executive Dashboard

> Canonical requirements and operating standard for the owner-facing Executive Dashboard for the 6S Success autonomous Claude Code business system.

## 1. Purpose

`EXECUTIVE-DASHBOARD.md` defines the single owner view for understanding the health, progress, economics, customer value, and autonomy of 6S Success.

The dashboard should answer in under two minutes:

1. Is the business healthy?
2. Are customers getting measurable value?
3. Are we moving toward the revenue goal?
4. What is the biggest constraint?
5. What is Claude working on now?
6. What changed recently?
7. What is working or failing?
8. Is production healthy?
9. How much is autonomous operation costing?
10. Does Claude need a decision from the owner?
11. What does Claude recommend next?

The dashboard is not an analytics dumping ground.

It is an executive decision system.

---

# 2. Core Principle

**Show outcomes, constraints, decisions, and exceptions before activity.**

Bad executive metric:

```text
Claude generated 47 pages this week.
```

Better:

```text
Entryway qualified traffic +18%
Quest start rate unchanged
Primary constraint: activation
```

---

# 3. Owner Experience

The default dashboard should be:

- fast
- concise
- mobile-friendly
- near real time where useful
- evidence-backed
- drillable
- exception-oriented
- visually obvious
- honest about unknown data

The owner should not need to read logs, GitHub Actions, container output, or agent transcripts to understand the business.

---

# 4. Dashboard Hierarchy

Recommended top-level structure:

```text
1. Executive Summary
2. Revenue & Economics
3. Customer Value
4. Growth Funnel
5. Current Constraint
6. Autonomous Missions
7. Experiments
8. Production & Reliability
9. Agent / Autonomy Health
10. Owner Decisions
11. Recent Material Changes
12. Claude Recommendation
```

---

# 5. Above-the-Fold View

The first screen should contain approximately:

```text
6S SUCCESS                              Updated 4:32 PM

Revenue MTD       $X,XXX     Target $20,000
Customer Outcomes XX.X%      ▲/▼
Quest Completion  XX.X%      ▲/▼
Production        HEALTHY
Autonomy Health   XX/100
Owner Decisions   2

PRIMARY CONSTRAINT
Entryway visitors are reaching diagnosis but not starting a quest.

CURRENT MISSION
Improve Entryway diagnosis → quest activation.

CLAUDE RECOMMENDS
Test a one-tap 15-minute starter quest after diagnosis.
```

Use actual verified data only.

---

# 6. Revenue Target

The strategic target may be represented as:

```yaml
monthly_revenue_target_usd: 20000
```

This is a target, not actual revenue.

Actual revenue must come from authoritative commerce data.

---

# 7. Revenue Section

Show:

- revenue month-to-date
- monthly target
- projected month-end revenue
- prior month
- recurring revenue if applicable
- product/content/service revenue mix
- refunds
- average order value
- conversion rate

Only show metrics supported by actual systems.

---

# 8. Revenue Progress

Conceptual:

```text
Revenue MTD / Monthly Revenue Target
```

Display:

```text
$12,450 / $20,000
62%
```

Never display fictional placeholder values in production.

---

# 9. Revenue Forecast

Forecast should include confidence.

Example:

```yaml
forecast:
  month_end_revenue:
  confidence:
  method:
  updated_at:
```

Do not present a simple linear extrapolation as high-confidence forecasting without labeling it.

---

# 10. Revenue Mix

Potential categories:

- digital content
- physical products
- kits
- card decks
- subscriptions/memberships
- services
- affiliate/referral
- other

Use only categories that actually exist.

---

# 11. Economics

Show when available:

- gross revenue
- refunds
- payment fees
- product COGS
- fulfillment
- infrastructure
- AI/model/tool cost
- marketing spend
- estimated contribution margin

Do not fabricate missing cost data.

---

# 12. Autonomous Operating Cost

Show:

```text
AI / Agent Cost MTD
Infrastructure MTD
Tooling MTD
Autonomy Cost per Successful Mission
Autonomy Cost per Confirmed Customer Outcome
```

Only when measurable.

---

# 13. Customer Value Section

The dashboard should emphasize whether customers achieve better spaces, not merely whether they visit pages.

Potential core metrics:

- desired functions selected
- diagnoses completed
- quests started
- quests completed
- outcomes confirmed
- sustain checks passed
- repeat quest users
- time-to-outcome

---

# 14. North-Star Candidate

A strong candidate is:

```text
Confirmed Useful Space Outcomes
```

or:

```text
Household Micro-Zones Successfully Improved
```

The exact north-star metric should be validated through product usage.

---

# 15. Customer Outcome Funnel

Recommended:

```text
Desired Function Selected
↓
Diagnosis Completed
↓
Quest Started
↓
Quest Completed
↓
Outcome Confirmed
↓
Sustain Check Passed
```

---

# 16. Customer Outcome by Room

Show:

```text
Entryway
Kitchen
Bathroom
Laundry
Home Office
...
```

Rank by:

- activity
- completion
- outcomes
- retention
- revenue when useful

---

# 17. Customer Outcome by Micro-Zone

Allow drill-down.

Example:

```text
Entryway
├── Keys
├── Shoes
├── Bags
├── Mail
├── Coats
└── Drop Zone
```

Use actual configured micro-zones.

---

# 18. Desired Function Analytics

Show which outcomes customers most frequently choose.

Examples:

- find keys instantly
- reduce visual clutter
- make leaving home easier
- create a safe landing zone
- simplify shoe storage

These are examples, not assumed production categories.

---

# 19. Root Cause Analytics

Show common verified diagnosis categories.

Potential categories:

- excess inventory
- unclear item home
- poor accessibility
- insufficient capacity
- weak visual control
- maintenance friction

---

# 20. Quest Analytics

Show:

- quest starts
- completion rate
- average planned duration
- average actual duration
- 15-minute vs longer quest performance
- single-player vs group completion
- card completion
- abandonment point
- repeat quest rate

---

# 21. Card Analytics

For Home Quest cards:

```text
Most Started
Most Completed
Highest Outcome Rate
Highest Abandonment
Most Frequently Selected
Most Frequently Assigned
Best Group Cards
Best 15-Minute Cards
```

Avoid optimizing cards solely for clicks.

---

# 22. Product Value Analytics

Show products by:

- purchases
- conversion
- margin
- associated desired function
- associated micro-zone
- associated confirmed outcome

This helps distinguish products that sell from products that actually solve problems.

---

# 23. No-Purchase Solutions

Measure when customers achieve an outcome without buying something.

This protects the brand from becoming a system that recommends products merely to create revenue.

---

# 24. Growth Funnel

Potential funnel:

```text
Impression
→ Qualified Visit
→ Desired Function Start
→ Desired Function Selection
→ Diagnosis
→ Quest Start
→ Quest Completion
→ Outcome
→ Purchase / Other Solution
→ Return
```

---

# 25. Acquisition

Potential sources:

- organic search
- answer engines
- direct
- LinkedIn
- referrals
- email
- paid acquisition
- partner
- other

Use actual attribution data.

---

# 26. SEO Section

Show decision-useful metrics:

- organic qualified sessions
- search impressions
- clicks
- CTR
- indexed useful pages
- top query clusters
- pages losing visibility
- technical SEO issues
- search → desired-function conversion

Do not celebrate traffic disconnected from customer value.

---

# 27. AEO Section

Where measurable:

- answer-engine referrals
- cited/referenced pages
- AI referral sessions
- answer-intent content performance
- AI referral → outcome conversion

Do not invent attribution unavailable from source data.

---

# 28. Content Performance

Rank content by:

```text
Qualified Traffic
→ Desired Function Selection
→ Quest Start
→ Outcome
→ Revenue
```

not pageviews alone.

---

# 29. Primary Constraint

One of the most important dashboard elements.

Show exactly one primary constraint when evidence supports it.

Example:

```yaml
primary_constraint:
  domain: ACTIVATION
  statement: >
    Users completing Entryway diagnosis are not starting the recommended quest.
  evidence:
  confidence:
  identified_at:
```

---

# 30. Constraint Categories

Potential:

- ACQUISITION
- ACTIVATION
- QUEST_COMPLETION
- CUSTOMER_OUTCOME
- RETENTION
- MONETIZATION
- RELIABILITY
- MEASUREMENT
- AUTONOMY
- COST
- SECURITY

---

# 31. Constraint Confidence

Use:

- HIGH
- MEDIUM
- LOW
- UNKNOWN

If measurement is unreliable, the primary constraint may be:

```text
MEASUREMENT
```

---

# 32. Current Mission

Display:

```yaml
current_mission:
  title:
  objective:
  owner_agent:
  status:
  success_metric:
  baseline:
  current:
  target:
  next_checkpoint:
```

---

# 33. Mission Portfolio

Show:

- active
- blocked
- waiting measurement
- completed recently

Keep work-in-progress intentionally limited.

---

# 34. Mission Card

Example:

```text
MISSION
Improve Entryway Quest Activation

Owner: Customer Journey Agent
Support: Analytics, Quest, GitHub
Status: MEASURING
Baseline: 18.2%
Current: 23.4%
Target: 25%
Cost: $XX
Owner action: None
```

Values must be real.

---

# 35. Agent Activity

Do not display agent chatter.

Show:

```text
Agent              Current Responsibility      Status
Orchestrator       Constraint / coordination   Active
Analytics          Measuring activation        Active
Quest              Starter quest design        Complete
GitHub Manager     Deployment trace            Waiting
```

---

# 36. Agent Status

Use:

- IDLE
- ACTIVE
- WAITING
- BLOCKED
- DEGRADED
- SUSPENDED

---

# 37. Autonomy Health

Show the score/model defined by `AUTONOMY-HEALTH.md`.

Potential components:

- autonomous completion
- task success
- reroute
- rework
- owner interruption
- deployment reliability
- agent health
- cost efficiency
- measurement integrity

---

# 38. Agent Readiness

Show trust/evaluation status:

```text
Orchestrator        T?
GitHub Manager      T?
VPS/Docker Manager  T?
DevOps/SRE          T?
Security            T?
Analytics           T?
...
```

Use verified trust levels only.

---

# 39. Weakest Agent

Surface only if actionable.

Example:

```text
WEAKEST AUTONOMY COMPONENT
Analytics Agent
Reason: repeated stale-data detection failures
Action: evaluation + instrumentation repair
```

---

# 40. Owner Interruption

Show:

```text
Owner decisions requested
Owner overrides
Owner corrections
Routine escalations avoided
```

The goal is not zero owner interaction.

The goal is owner attention only where valuable or required.

---

# 41. Owner Decision Queue

This must be prominent.

Each decision should contain:

```text
Decision
Why it matters
Claude recommendation
Options
Risk
Deadline
```

---

# 42. Decision Example

```text
DECISION REQUIRED

Approve $750 acquisition test?

Recommendation: Approve

Why:
Organic Entryway conversion is validated, but acquisition volume is below experiment threshold.

Options:
[Approve] [Reject] [Modify]

Required by:
Friday
```

Only if actual governance requires owner approval.

---

# 43. No Decision State

If none:

```text
Owner Decisions: 0
Claude does not need your attention.
```

This is a useful outcome.

---

# 44. Experiments

Show:

- experiment
- hypothesis
- primary metric
- baseline
- current result
- guardrails
- status
- decision date
- recommended action

---

# 45. Experiment Status

Use:

- PROPOSED
- ACTIVE
- MEASURING
- DECISION_READY
- ADOPTED
- REVISED
- ROLLED_BACK
- INCONCLUSIVE
- ABANDONED

---

# 46. Experiment Card

```text
15-Minute Starter Quest

Hypothesis:
A one-tap starter quest increases diagnosis → quest activation.

Baseline: X%
Current: Y%
Guardrails: Healthy
Confidence: Medium
Decision: Continue measuring
```

---

# 47. Production Health

At minimum:

```text
Website
API
Database
Commerce
Background Jobs
Event Pipeline
```

Only show components that exist.

---

# 48. Production Status

Use:

- HEALTHY
- DEGRADED
- INCIDENT
- UNKNOWN

---

# 49. Latest Deployment

Show:

```text
Release
Commit
Deployment time
Verification
Rollback availability
Customer impact
```

---

# 50. Deployment Quality

Potential:

- deployment success rate
- failed deployments
- rollbacks
- mean recovery time
- change failure rate

---

# 51. GitHub Health

Show exceptions:

- failing default-branch workflow
- open critical security alert
- blocked release
- branch protection issue
- stale critical PR

Do not make the executive owner manage routine GitHub housekeeping.

---

# 52. VPS / Docker Health

Show exceptions:

- unhealthy container
- restart loop
- disk pressure
- memory pressure
- unexpected public port
- backup failure
- certificate problem

---

# 53. Security

Executive status:

```text
Security: HEALTHY / ACTION REQUIRED / INCIDENT / UNKNOWN
```

Potential drill-down:

- critical findings
- exposed secrets
- vulnerable dependencies
- permission changes
- suspicious exposure

Never expose secret values.

---

# 54. Backup / Recovery

Show:

```text
Last backup
Last successful restore test
Recovery readiness
```

A backup that has never been restore-tested should not be labeled fully verified.

---

# 55. Event Pipeline

Since dashboard depends on telemetry:

```text
Last event received
Projection lag
Failed events
Dead-letter count
```

If telemetry is stale, visibly mark dashboard freshness.

---

# 56. Dashboard Freshness

Always display:

```text
Last updated:
Data freshness:
```

Potential:

- LIVE
- CURRENT
- DELAYED
- STALE
- UNKNOWN

---

# 57. Metric-Level Freshness

Critical metrics should expose source freshness on drill-down.

---

# 58. Unknown Data

Display:

```text
UNKNOWN
```

not:

```text
0
```

when data is unavailable.

---

# 59. Data Confidence

Important derived metrics should optionally show:

- VERIFIED
- ESTIMATED
- INFERRED
- UNKNOWN

---

# 60. Recent Material Changes

Show only meaningful changes:

- production release
- experiment decision
- major content launch
- product launch
- incident
- self-improvement
- owner directive
- significant customer milestone

---

# 61. Activity Feed Example

```text
4:20 PM  Entryway release deployed       VERIFIED
2:15 PM  Starter quest experiment        MEASURING
11:40 AM Agent routing update             ADOPTED
9:05 AM  Production backup               VERIFIED
```

---

# 62. Claude Recommendation

The dashboard should end its executive summary with one recommendation.

Format:

```yaml
claude_recommendation:
  action:
  why:
  expected_impact:
  confidence:
  owner_action_required:
```

---

# 63. Recommendation Rules

Recommendation must:

- address primary constraint
- use evidence
- be bounded
- be actionable
- avoid unnecessary complexity
- identify uncertainty
- state owner action only when required

---

# 64. Recommendation Example

```text
CLAUDE RECOMMENDS

Run the 15-minute Entryway starter quest experiment for another 200 qualified diagnosis completions.

Why:
Early activation improved, but sample size is still insufficient for a confident decision.

Owner action:
None.
```

---

# 65. What Claude Should Not Recommend

Avoid vague:

```text
Improve SEO.
Create more content.
Increase engagement.
Optimize the website.
```

Recommendations should specify the constraint and intervention.

---

# 66. Alerts vs Dashboard

The dashboard is not the same as alerts.

Urgent conditions should notify through configured alert channels.

The dashboard provides current executive state.

---

# 67. Alert Conditions

Potential:

- production down
- checkout unavailable
- critical security issue
- backup/recovery failure
- spend threshold exceeded
- owner decision deadline
- telemetry severely stale

Actual thresholds come from governance.

---

# 68. Mobile Design

Owner view should work well on a phone.

Prioritize:

1. business status
2. customer outcomes
3. primary constraint
4. owner decisions
5. Claude recommendation

before detailed technical data.

---

# 69. Desktop Design

Desktop may add:

- trend charts
- mission board
- funnel visualization
- agent scorecards
- deployment timeline
- experiment history

---

# 70. Drill-Down Architecture

Top-level cards should link to:

```text
Revenue
Customers
Rooms
Micro-Zones
Quests
Products
Growth
Missions
Agents
Experiments
Production
Security
Costs
Decisions
```

---

# 71. Room Dashboard

For each room:

```text
Traffic
Desired functions
Diagnoses
Quest starts
Quest completion
Confirmed outcomes
Repeat usage
Products
Revenue
Top constraint
Active experiment
```

---

# 72. Micro-Zone Dashboard

For each micro-zone:

```text
Primary desired functions
Common root causes
Top quests
Top cards
Completion
Outcome rate
Products used
No-purchase solutions
Sustain rate
```

---

# 73. Entryway Prototype Dashboard

Because Entryway may serve as the prototype, its drill-down should be capable of becoming the reference implementation for future room dashboards.

Do not hard-code the entire platform around Entryway.

---

# 74. Quest Dashboard

Show:

- sessions
- players
- duration
- completion
- cards
- abandonment
- outcomes
- repeat use
- group performance

---

# 75. Product Dashboard

Show:

- units/orders
- revenue
- margin
- conversion
- desired function served
- micro-zones served
- associated outcomes
- refunds
- customer feedback

---

# 76. Content Dashboard

Show:

- qualified visits
- search visibility
- desired-function starts
- quest starts
- outcomes
- assisted revenue
- freshness
- update opportunities

---

# 77. Agent Dashboard

For each agent:

```text
Trust Level
Evaluation Status
Current Task
Success Rate
Failure Rate
Reroute Rate
Rework Rate
Owner Escalation Rate
Cost
Last Evaluation
Known Weakness
```

---

# 78. GitHub Manager Dashboard

Potential:

- repos
- active PRs
- failing workflows
- release status
- deployment linkage
- security alerts
- branch protection

---

# 79. VPS/Docker Dashboard

Potential:

- host health
- container health
- CPU
- memory
- disk
- restart counts
- exposed ports
- backup
- certificates

---

# 80. DevOps/SRE Dashboard

Potential:

- availability
- incidents
- MTTR
- change failure
- rollback
- observability gaps

---

# 81. Security Dashboard

Potential:

- critical findings
- high findings
- unresolved findings
- secrets
- permissions
- dependency vulnerabilities
- exposure

---

# 82. Analytics Dashboard

Potential:

- data freshness
- broken instrumentation
- metric conflicts
- missing baselines
- attribution confidence

---

# 83. Self-Improvement Dashboard

Show:

```text
Current autonomy constraint
Active self-improvement
Baseline
Expected improvement
Current result
Guardrails
Decision
```

---

# 84. Mission Control vs Executive Dashboard

`MISSION-CONTROL.md` / Mission Control UI answers:

> What is the autonomous organization doing right now?

Executive Dashboard answers:

> Is the business and autonomous organization achieving the right outcomes?

They should share data but not be identical interfaces.

---

# 85. Dashboard Data Sources

Potential sources:

- autonomy database
- autonomy event projections
- analytics
- commerce
- GitHub
- runtime monitoring
- scheduler
- security tooling
- owner directives

Actual sources must be discovered.

---

# 86. Dashboard Read Model

Use a dedicated read/projection layer rather than complex ad hoc queries from the browser.

Potential:

```text
dashboard_executive_summary
dashboard_revenue
dashboard_customer_value
dashboard_growth_funnel
dashboard_active_missions
dashboard_experiments
dashboard_production_health
dashboard_agent_health
dashboard_owner_decisions
```

---

# 87. Dashboard API

Potential read-only routes:

```text
/api/dashboard/executive
/api/dashboard/revenue
/api/dashboard/customer-value
/api/dashboard/missions
/api/dashboard/agents
/api/dashboard/experiments
/api/dashboard/production
/api/dashboard/decisions
```

Use actual application conventions.

---

# 88. Authentication

Executive Dashboard must not be publicly accessible by default.

Require appropriate owner/admin authentication.

---

# 89. Authorization

Separate:

- public customer site
- customer account
- internal operational dashboard
- owner control plane

---

# 90. Owner Actions

If dashboard supports actions, use explicit controls.

Potential:

- approve
- reject
- modify decision
- pause mission
- resume mission
- change priority
- acknowledge incident

Every material owner action should create an autonomy event.

---

# 91. Destructive Controls

Do not place casual destructive infrastructure controls on the executive dashboard.

Example:

```text
DELETE PRODUCTION DATABASE
```

should not be a convenient dashboard button.

---

# 92. Dashboard Performance

Executive summary should load quickly.

Use cached/materialized projections if needed.

Always display freshness.

---

# 93. Near-Real-Time Definition

For this system, near real time means sufficiently current for operational decisions.

Not every metric needs sub-second updates.

Examples:

- incidents: fast
- deployments: fast
- owner decisions: fast
- revenue: minutes may be sufficient
- SEO: hours/daily may be sufficient

---

# 94. Refresh Strategy

Use the simplest approach meeting freshness needs:

- polling
- server-sent events
- WebSocket
- scheduled projection refresh

Do not overbuild.

---

# 95. Visualization Principles

Use charts only when they improve decisions.

Prefer:

- KPI cards
- funnels
- sparklines
- simple trends
- status badges
- progress bars
- concise tables

Avoid decorative dashboards.

---

# 96. Color Semantics

Use consistent semantics:

- healthy
- warning
- critical
- neutral/unknown

Do not rely on color alone.

---

# 97. Accessibility

Dashboard should support:

- readable contrast
- keyboard navigation
- labels
- responsive layout
- non-color status cues

---

# 98. Trend Windows

Useful comparisons may include:

- today
- 7 days
- 30 days
- month-to-date
- prior period

Use appropriate window per metric.

---

# 99. Metric Definitions

Every metric should have drill-down metadata:

```yaml
metric:
  name:
  definition:
  calculation:
  source:
  freshness:
  confidence:
  owner:
```

---

# 100. Revenue Definition

Define whether displayed revenue means:

- gross orders
- net revenue
- recognized revenue
- collected cash

Do not mix definitions.

---

# 101. Customer Outcome Definition

A confirmed outcome must have a defined confirmation method.

Do not count a page view as an outcome.

---

# 102. Qualified Visitor Definition

Define qualification based on actual business logic.

Do not use all bot/accidental traffic as denominator.

---

# 103. Conversion Definition

Every conversion rate should state numerator and denominator.

---

# 104. Experiment Guardrails

Dashboard should make it impossible to celebrate a primary metric improvement while hiding a failed guardrail.

---

# 105. Statistical Honesty

Use:

- insufficient data
- early signal
- directional
- statistically/operationally meaningful where justified

Do not declare winners prematurely.

---

# 106. Forecast Honesty

Forecasts must distinguish:

- actual
- forecast
- target

---

# 107. Dashboard Annotations

Annotate major events on trend charts:

- release
- campaign
- incident
- pricing change
- experiment

This helps avoid false interpretation.

---

# 108. Owner Digest

Dashboard data can support a concise owner digest.

Potential:

```text
Business
Customer
Constraint
Claude Work
Risk
Decision Needed
Recommendation
```

---

# 109. Daily Digest

Only if useful.

Do not send daily reports containing no material changes.

---

# 110. Weekly Executive Review

Recommended questions:

1. What customer value improved?
2. What business metric improved?
3. What is the constraint now?
4. What experiments finished?
5. What failed?
6. What did Claude learn?
7. What requires owner direction?
8. What should stop?

---

# 111. Monthly Review

Include:

- revenue vs target
- customer outcomes
- retention
- room/micro-zone expansion
- product economics
- growth efficiency
- autonomy cost
- autonomy health
- agent changes
- infrastructure/reliability
- strategic recommendations

---

# 112. $20K/Month Goal View

The dashboard should explicitly track progress toward the business objective without letting the revenue goal override customer value.

Conceptually:

```text
MONTHLY REVENUE
Actual:    VERIFIED_VALUE
Target:    $20,000
Gap:       CALCULATED
Forecast:  ESTIMATE + CONFIDENCE
```

Below it:

```text
CUSTOMER VALUE
Confirmed Outcomes: VERIFIED_VALUE
Sustain Rate: VERIFIED_VALUE
```

Both matter.

---

# 113. Revenue Gap Analysis

When below target, Claude should diagnose the gap:

```text
Traffic
× Activation
× Outcome Completion
× Purchase Rate
× Average Order Value
× Repeat Rate
```

rather than simply recommending more traffic.

---

# 114. Constraint Tree

Potential drill-down:

```text
Revenue Gap
├── Qualified Traffic
├── Activation
├── Quest Completion
├── Product Fit
├── Purchase Conversion
├── AOV
└── Retention
```

---

# 115. Opportunity Ranking

Rank opportunities by:

```text
Expected Customer Value
× Expected Business Impact
× Confidence
÷ Effort / Risk
```

This is conceptual, not a license to fabricate numbers.

---

# 116. Claude Recommendation Engine

Recommendation should consider:

- owner directives
- primary constraint
- current missions
- experiment evidence
- customer outcomes
- revenue gap
- costs
- reliability
- security
- agent capacity

---

# 117. Recommendation Priority

Priority order:

1. critical safety/security
2. production/customer failure
3. measurement failure blocking decisions
4. largest customer-value constraint
5. largest business constraint
6. autonomy constraint
7. cost optimization
8. lower-value optimization

---

# 118. No-Action Recommendation

Claude may recommend:

```text
Continue measuring. No change recommended yet.
```

This is preferable to constant churn.

---

# 119. Owner Attention Budget

Treat owner attention as scarce.

The dashboard should minimize:

- routine approvals
- technical noise
- duplicate alerts
- low-value decisions

---

# 120. Decision Escalation Threshold

Only place something in Owner Decisions when:

- governance requires it
- strategic direction is ambiguous
- irreversible/high-risk choice exists
- spend authority exceeded
- owner preference materially changes outcome

---

# 121. Executive Narrative

Generate a short narrative from verified metrics.

Example structure:

```text
Revenue is tracking below target primarily because qualified Entryway traffic is low. Users who begin a quest are completing at a healthy rate. Claude is therefore testing acquisition rather than redesigning the quest flow. Production is healthy and no owner decision is required.
```

Do not fabricate values.

---

# 122. Dashboard Truth Hierarchy

Prefer:

1. authoritative transaction/system data
2. validated projections
3. verified analytics
4. estimates clearly labeled
5. UNKNOWN

Never choose a confident guess over UNKNOWN.

---

# 123. Data Conflict

If sources disagree:

```text
DATA CONFLICT
Revenue source mismatch detected.
Executive revenue temporarily marked UNKNOWN.
```

Do not silently choose the more favorable number.

---

# 124. Dashboard Failure

If dashboard data is stale:

- show stale status
- show last successful update
- preserve last known value only if clearly labeled
- do not imply current state

---

# 125. Dashboard Observability

Monitor:

- API health
- projection lag
- rendering errors
- authentication failures
- stale data
- metric query failures

---

# 126. Dashboard Testing

Test:

- authenticated access
- unauthorized access rejected
- mobile layout
- desktop layout
- unknown metric
- stale metric
- data conflict
- production incident
- pending owner decision
- no-decision state
- revenue target vs actual
- event pipeline failure

---

# 127. Data Contract Testing

Each dashboard card should have a defined response schema and source.

---

# 128. End-to-End Test

A deployment should be capable of appearing:

```text
GitHub merge
→ deployment event
→ deployment verification
→ dashboard latest release
```

---

# 129. Customer Outcome Test

A quest outcome should flow:

```text
Quest completion
→ outcome confirmation
→ customer-value projection
→ room dashboard
→ executive summary
```

---

# 130. Owner Decision Test

```text
owner.decision_requested
→ dashboard queue
→ owner action
→ owner.decision_received
→ task resumed
→ queue cleared
```

---

# 131. Bootstrap Implementation

Before building:

1. inspect existing application
2. inspect current admin/dashboard UI
3. inspect database
4. inspect analytics
5. inspect commerce
6. inspect autonomy event implementation
7. identify current auth
8. identify available metrics
9. identify missing instrumentation
10. implement minimum read models
11. build executive summary first
12. add drill-downs incrementally

---

# 132. Phase 1 Dashboard

Start with:

```text
Executive Summary
Revenue
Current Mission
Primary Constraint
Production Health
Owner Decisions
Latest Deployment
Active Experiment
Autonomy Health
Claude Recommendation
```

---

# 133. Phase 2 Dashboard

Add:

```text
Customer Outcome Funnel
Room / Micro-Zone Performance
Quest Analytics
Product Performance
SEO/AEO
Content
Agent Scorecards
Costs
```

---

# 134. Phase 3 Dashboard

Add:

```text
Forecasting
Opportunity Ranking
Outcome Attribution
Autonomy ROI
Self-Improvement History
Advanced owner controls
```

only when data quality supports them.

---

# 135. Initial State

Until connected to real data:

```yaml
executive_dashboard:
  status: NOT_IMPLEMENTED_OR_UNVERIFIED
  revenue_actual: UNKNOWN
  customer_outcomes: UNKNOWN
  primary_constraint: UNKNOWN
  production_health: UNKNOWN
  autonomy_health: UNKNOWN
  owner_decisions: UNKNOWN
  claude_recommendation: ESTABLISH_BASELINE
```

---

# 136. First Dashboard Mission

```yaml
mission:
  title: Build Owner Executive Command Center
  objective: >
    Create a secure owner-facing dashboard that provides verified,
    decision-useful visibility into revenue, customer value, the current
    business constraint, autonomous missions, production health, experiments,
    autonomy health, and owner decisions.
  success:
    - secure owner access
    - verified revenue source
    - primary constraint visible
    - current mission visible
    - production health visible
    - owner decision queue functional
    - latest deployment traceable
    - data freshness visible
    - unknown data handled honestly
    - mobile experience usable
```

---

# 137. Executive Dashboard Acceptance Criteria

The owner should be able to open one page and answer:

```text
How much revenue have we generated this month?
Are we on track for $20K?
Are customers achieving useful outcomes?
Where is the biggest funnel constraint?
What is Claude doing about it?
Which agents are involved?
What experiment is active?
Is production healthy?
What changed recently?
How much is autonomy costing?
Does Claude need me?
What does Claude recommend next?
```

within approximately two minutes.

---

# 138. Non-Negotiable Rules

Claude and subagents must not:

- fabricate dashboard metrics
- show targets as actuals
- show stale data as current
- treat pageviews as customer outcomes
- optimize traffic without downstream value
- hide failed experiment guardrails
- hide production incidents
- hide material cost overruns
- bury owner decisions
- flood the owner with routine technical noise
- expose secrets
- expose payment data
- expose private customer information unnecessarily
- expose private chain-of-thought
- make the internal dashboard public by default
- create destructive production controls casually
- add complex real-time infrastructure without need
- claim causal attribution without evidence
- declare experiment success prematurely
- use AI-generated narrative unsupported by metrics
- interpret UNKNOWN as zero
- prioritize autonomy activity over customer/business outcomes

---

# 139. Final Principle

The Executive Dashboard should not tell the owner how busy Claude is.

It should tell the owner whether the autonomous organization is creating value.

The core executive chain is:

```text
BUSINESS HEALTH
+
CUSTOMER VALUE
+
PRIMARY CONSTRAINT
+
CURRENT MISSION
+
VERIFIED CHANGE
+
EXPERIMENT RESULT
+
AUTONOMY HEALTH
+
OWNER DECISION
+
CLAUDE RECOMMENDATION
```

The desired owner experience is:

> I can open one screen, understand the state of 6S Success, see what Claude is doing, know whether customers and the business are improving, identify anything that needs my attention, and then leave Claude to continue operating.

That is the purpose of `EXECUTIVE-DASHBOARD.md`.
