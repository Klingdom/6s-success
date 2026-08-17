# 6S Success Executive Dashboard Specification

> Canonical specification for the owner/executive command center used to understand business performance, customer value, autonomous work, experiments, GitHub-to-production state, and Hostinger VPS/Docker health.

## 1. Purpose

`DASHBOARD.md` defines **what the executive dashboard must show, how it should behave, and how Claude should use it to operate 6S Success**.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`
- `DATA-SOURCES.md`

`METRICS.md` defines metric meaning.

`DATA-SOURCES.md` defines source authority.

This file defines executive presentation and decision support.

---

# 2. Dashboard Mission

The dashboard should let the owner understand the business in roughly **60 seconds** and investigate important issues in roughly **5 minutes**.

It must answer:

1. Are customers getting value?
2. Are we growing?
3. Are we making money?
4. Are we on a credible path toward $20K+ monthly revenue?
5. What is the biggest constraint?
6. What is Claude improving now?
7. Did recent autonomous changes work?
8. What experiments are running?
9. Is GitHub aligned with production?
10. Is the Hostinger VPS/Docker environment healthy?
11. Are backups and recovery healthy?
12. What risks need attention?
13. What requires an owner decision?

---

# 3. Core Principle

The dashboard is not a collection of charts.

It is a **decision interface**.

Every major section should help answer:

**What happened?**

**Why does it matter?**

**What is likely causing it?**

**What is Claude doing about it?**

**What decision, if any, is required from the owner?**

---

# 4. Dashboard Audience

Primary audience:

**6S Success owner/executive**

Secondary audience:

- autonomous Claude orchestrator
- specialist agents
- future business/operations leadership

Do not optimize the primary dashboard for developers.

Technical detail belongs behind drill-down views.

---

# 5. Executive Dashboard Layout

Recommended top-level structure:

1. Executive Pulse
2. Revenue & Economics
3. Acquisition / SEO / AEO
4. Customer Value & Product
5. Funnel & Commerce
6. Products & Content
7. Experiments
8. Autonomous Work
9. GitHub & Releases
10. Production / VPS / Docker
11. Reliability / Backup / Security
12. Risks & Opportunities
13. Owner Decisions
14. Strategic Progress

---

# 6. Global Header

Always show:

**6S Success Executive Command Center**

Also show:

- environment: `PRODUCTION`
- dashboard last refreshed
- data confidence summary
- current production release
- overall business status
- overall production status
- active workstreams
- pending owner decisions

Example:

`Production: HEALTHY | Business: WATCH | Data: 82% VERIFIED | Release: abc1234 | Updated: 4 min ago`

Do not display fabricated values.

---

# 7. Status Language

Use a small consistent vocabulary:

- `HEALTHY`
- `WATCH`
- `AT RISK`
- `CRITICAL`
- `UNKNOWN`

For data:

- `HIGH`
- `MEDIUM`
- `LOW`
- `UNKNOWN`

Do not create dozens of status labels.

---

# 8. Status Threshold Rule

Do not invent business thresholds merely to color the dashboard.

Thresholds must come from:

- explicit target
- historical baseline
- experiment guardrail
- operational requirement
- documented specialist decision

If no valid threshold exists, show trend without artificial red/green judgment.

---

# 9. Executive Pulse

The first screen should fit without excessive scrolling.

Recommended cards:

## Revenue

- MTD Net Revenue
- $20K Target Progress
- Revenue Gap
- current pace / required pace

## Customers

- Users
- Activated Users
- Quest Completions
- Sustained Improvements when mature

## Growth

- Organic Sessions
- Search Clicks
- Qualified Landing Sessions

## Commerce

- Orders
- Purchase Conversion
- AOV
- Contribution Margin when available

## Product

- Quest Completion Rate
- Micro-Zone Completions
- Next Micro-Zone / Cross-Room Progression

## Operations

- Production Status
- Critical Journey Availability
- Backup Freshness
- Current Release

---

# 10. Executive Narrative

Above or immediately below the pulse, Claude should generate a concise evidence-grounded summary.

Recommended format:

**What changed:**  
2-4 material changes.

**Primary constraint:**  
The most important bottleneck currently limiting customer or revenue growth.

**Claude action:**  
What the autonomous organization is doing about it.

**Owner attention:**  
Only decisions that genuinely require the owner.

Do not generate generic executive prose.

---

# 11. $20K Monthly Revenue Panel

Strategic target:

**$20,000+ monthly revenue**

Show:

- MTD Net Revenue
- target
- target attainment %
- remaining gap
- days remaining
- required daily revenue pace
- current trailing daily pace
- forecast only if a valid forecasting method exists

Clearly label:

`TARGET`
`ACTUAL`
`FORECAST`

Never present target pace as forecast.

---

# 12. Revenue Driver Tree

Show a decomposed revenue model:

**Qualified Traffic**
× **Purchase Conversion**
× **AOV**
≈ **Revenue**

Optional deeper funnel:

**Traffic**
× **Qualified Engagement**
× **Product Exposure**
× **Purchase Conversion**
× **AOV**

Claude should identify which component currently appears most constraining.

---

# 13. Revenue Scenario Tool

Provide an interactive scenario calculator.

Inputs:

- monthly traffic
- qualified engagement rate
- purchase conversion
- AOV
- repeat purchase contribution

Output:

- estimated monthly orders
- estimated revenue
- gap to $20K
- required improvement by lever

Scenarios must be labeled:

`SCENARIO`

They are not forecasts.

---

# 14. Revenue Quality

Show when data exists:

- Gross Revenue
- Net Revenue
- Discounts
- Refunds
- COGS
- Gross Profit
- Gross Margin
- Contribution
- Contribution Margin

Do not celebrate revenue growth that destroys contribution economics.

---

# 15. Revenue Mix

Show revenue by:

- digital products
- physical products
- services
- bundles
- other validated streams

Also show top products by:

- revenue
- units
- contribution where available

Avoid charts with tiny categories that add no decision value.

---

# 16. Acquisition Overview

Show:

- Users
- New Users
- Returning Users
- Sessions
- Qualified Landing Sessions
- channel mix

Trend:

- 7 day
- 30 day
- comparable prior period

Highlight material channel changes.

---

# 17. Organic Search Panel

Use verified search data.

Show:

- Search Clicks
- Search Impressions
- Organic CTR
- Average Position
- Organic Sessions
- Indexed Pages where useful

Also show:

- top gaining queries
- top declining queries
- top gaining landing pages
- top declining landing pages
- high-impression / low-CTR opportunities

Do not optimize average position in isolation.

---

# 18. SEO Opportunity Queue

Rank opportunities using business relevance.

Candidate score inputs:

- impressions
- current position
- CTR opportunity
- room/micro-zone relevance
- conversion/activation history
- strategic priority
- effort

Example opportunity:

`entryway shoe storage`
→ high impressions
→ position 8
→ weak CTR
→ maps to Shoe Zone
→ strong quest/product fit

This is more valuable than a generic SEO audit list.

---

# 19. Technical SEO Health

Show concise status for:

- robots
- sitemap
- canonical issues
- 4xx
- 5xx
- redirect chains
- duplicate titles where material
- structured-data errors
- crawl/index anomalies

Technical issues should create actionable backlog items.

---

# 20. AEO Panel

Do not fabricate an "AI visibility score."

Show evidence such as:

- answer-engine referral traffic where identifiable
- structured direct-answer coverage
- key question coverage
- crawler accessibility
- verified citation/mention observations where measurable

Include:

**AEO Opportunities**

with specific pages/questions to improve.

---

# 21. Entryway Product Panel

While Entryway is the strategic proving ground, give it a dedicated section.

Show:

- Entryway visitors
- desired-function starts
- desired-function completions
- top desired functions
- top micro-zones
- root-cause diagnoses
- quest starts
- quest completions
- standards established
- sustainment checks
- purchases
- revenue

This panel should reveal whether the complete Entryway loop is working.

---

# 22. Desired Function Funnel

Show:

**Room View**
→ **Desired Function Start**
→ **Desired Function Completion**
→ **Micro-Zone Selection**
→ **Diagnosis**
→ **Quest Start**

Highlight the largest meaningful drop-off.

---

# 23. Desired Function Insights

Show distribution by:

- desired function
- room
- micro-zone

Potential Entryway examples:

- fastest exit
- visual calm
- child independence
- guest readiness
- weather readiness
- maximum useful capacity

Do not interpret preference distribution as universal customer truth without sufficient sample.

---

# 24. Root Cause Intelligence

Show top diagnosed root causes.

Examples:

- excess
- no home
- wrong home
- poor access
- poor visibility
- excess steps
- unclear ownership
- capacity mismatch
- no standard
- replenishment issue
- cleaning friction
- safety risk

Drill down:

**Root Cause**
→ **Micro-Zones**
→ **Quests**
→ **Completion**
→ **Products**
→ **Sustainment**

This can become one of the business's most valuable intelligence views.

---

# 25. Quest Panel

Show:

- Quest Starts
- Quest Completions
- Quest Completion Rate
- median Time to Completion
- abandonment
- multi-player rate

Break down by:

- 15 min
- 30 min
- 45 min
- 60 min
- 90 min

Also:

- top completing quests
- weakest quests
- highest progression quests
- highest product-assist quests

Do not reward agents for making quests trivially completable.

---

# 26. Customer Outcome Panel

The dashboard should mature toward outcome measurement.

Show:

- Micro-Zone Completions
- Standards Established
- Sustainment Checks
- Sustained Improvement Rate

Candidate North Star:

**Sustained Micro-Zone Improvements**

This should become prominent once data quality is sufficient.

---

# 27. Progression Panel

Show:

- first micro-zone → second micro-zone
- Entryway completion → another room
- 7/30/90-day meaningful return

This tests the retention thesis:

**A successful improvement should naturally lead to another useful improvement.**

---

# 28. Funnel Panel

Recommended funnel:

**Visitor**
→ **Qualified Engagement**
→ **Assessment / Desired Function**
→ **Quest Start**
→ **Quest Completion**
→ **Product View**
→ **Add to Cart**
→ **Checkout**
→ **Purchase**

For each stage show:

- count
- conversion from prior stage
- change vs comparison period

Claude should identify the largest economically meaningful leak.

---

# 29. Commerce Panel

Show:

- Product Views
- Product Recommendation Impressions
- Recommendation CTR
- Add-to-Cart Rate
- Checkout Starts
- Checkout Completion
- Purchases
- Purchase Conversion
- AOV
- Refund Rate
- Repeat Purchase Rate

Segment by product family.

---

# 30. Recommendation Performance

Because product recommendations should follow diagnosis, show:

**Root Cause**
→ **Recommendation**
→ **Click**
→ **Purchase**
→ **Outcome/Sustainment where possible**

This helps determine whether products actually help solve the diagnosed problem.

---

# 31. Product Catalog Panel

Show product state:

- CONCEPT
- PROTOTYPE
- BETA
- ACTIVE
- PAUSED
- RETIRED

For ACTIVE products:

- price
- availability
- sales
- conversion
- contribution
- refunds
- inventory where applicable

Surface catalog/checkout mismatches.

---

# 32. Product Opportunity Panel

Claude may recommend new products when evidence supports them.

Each opportunity should include:

- customer problem
- room/micro-zone
- root cause
- demand evidence
- proposed product
- expected customer value
- commercial hypothesis
- estimated effort
- risk
- recommended experiment

Do not generate product ideas simply to fill this section.

---

# 33. Content Panel

Show:

- total active content
- organic traffic
- qualified engagement
- assisted activation
- assisted revenue where valid

Highlight:

- high-value winners
- decaying content
- pages with traffic but weak activation
- pages with strong conversion but weak traffic
- content gaps tied to customer demand

---

# 34. Content Production Queue

Prioritize content based on:

**Customer Need**
+ **Search Opportunity**
+ **Product Relevance**
+ **Strategic Fit**
+ **Existing Coverage Gap**

Do not prioritize solely on keyword volume.

---

# 35. Experiment Command Center

Every active experiment should show:

- experiment ID
- hypothesis
- owner
- start date
- population
- variants
- primary metric
- guardrails
- sample size
- current result
- confidence
- next decision date/status

Status:

- PLANNED
- RUNNING
- HOLD
- CONCLUDED
- ADOPTED
- REJECTED

---

# 36. Experiment Decision View

For concluded experiments show:

**Hypothesis**

**Result**

**Primary metric**

**Guardrails**

**Interpretation**

**Decision**

**Learning**

**Follow-up**

Avoid simply labeling experiments "winner" or "loser."

---

# 37. Autonomous Work Panel

This is essential for owner trust.

Show:

## Completed Recently

Material changes Claude completed.

For each:

- change
- agent
- reason
- GitHub reference
- deployment
- expected metric
- measured outcome
- rollback status

## In Progress

Current major workstreams.

## Next

Highest-priority queued work.

## Blocked

What cannot proceed and why.

---

# 38. Autonomous Change Outcome

Each material autonomous change should eventually answer:

**Why did we do it?**

**What did we expect?**

**What happened?**

**Keep, iterate, or revert?**

This closes the continuous-improvement loop.

---

# 39. Agent Activity

Do not create a vanity leaderboard.

Useful view:

| Agent | Current Responsibility | Last Material Action | Status | Blocker |
|---|---|---|---|---|

The objective is accountability and coordination, not maximizing agent activity.

---

# 40. GitHub Control Panel

Show:

- repository
- default branch
- latest commit
- latest release/tag
- open PRs
- failed workflows
- security alerts summary
- dependency update state
- branch protection status where relevant

Most important:

**GitHub Intended Release**
vs
**Production Running Release**

---

# 41. Release Lineage

Show:

**Commit SHA**
→ **Build ID**
→ **Image Digest**
→ **Deployment**
→ **Running Container**
→ **Production Verification**

Status:

- MATCHED
- MISMATCH
- UNKNOWN

An unexplained mismatch should be prominent.

---

# 42. Deployment History

Show recent production deployments:

- timestamp
- commit
- agent/human actor
- deployment result
- verification result
- rollback if any

Avoid displaying every CI job in the executive view.

---

# 43. Hostinger VPS Panel

Show:

- host status
- CPU
- memory
- disk
- load where useful
- uptime
- key network/reverse-proxy status

Use trend and capacity risk, not just current utilization.

---

# 44. Docker Panel

Show:

- expected services
- running services
- unhealthy services
- unexpected stopped services
- restart trends
- running image digest
- volume health
- network status where relevant

Highlight configuration/runtime drift.

---

# 45. Production Service Map

Optional drill-down:

**Internet**
→ **DNS/CDN**
→ **Reverse Proxy**
→ **Application**
→ **Database**
→ **Commerce/Payment APIs**
→ **Persistent Storage**

Show status at each layer.

This should help diagnose incidents quickly.

---

# 46. Reliability Panel

Show:

- Site Availability
- Critical Journey Availability
- Server Error Rate
- Application Error Rate
- latency
- incidents
- MTTR
- change failure rate

Prioritize customer journeys over infrastructure vanity metrics.

---

# 47. Critical Journeys

Monitor at minimum when applicable:

1. Home page / public site
2. Entryway desired-function flow
3. Quest start/completion
4. Product view
5. Checkout
6. Purchase confirmation/entitlement

Show journey health.

---

# 48. Backup & Recovery Panel

Show:

- required persistent assets
- backup coverage
- latest backup
- backup age
- backup verification level
- latest restore test
- restore validation age
- failures

A green "backup" indicator should require meaningful evidence.

---

# 49. Security Panel

Executive summary only:

- Critical findings
- High findings
- secrets exposure status
- dependency risk
- host exposure issues
- certificate expiration risk
- security actions requiring approval

Do not display exploitable details in broad dashboard views.

---

# 50. Data Health Panel

Show:

- source connection status
- freshness
- reconciliation failures
- critical missing metrics
- confidence coverage

Example:

`Executive KPI coverage: 14/18 verified`

This prevents polished dashboards from hiding missing truth.

---

# 51. Source Drill-Down

For any metric, allow inspection of:

- definition
- source
- last refresh
- confidence
- comparison period
- known caveats

This metadata should come from `METRICS.md` and `DATA-SOURCES.md`.

---

# 52. Risks Panel

Rank material risks.

Each risk:

- ID
- description
- category
- severity
- likelihood
- business impact
- owner
- mitigation
- status
- decision required?

Categories:

- customer
- revenue
- product
- security
- reliability
- data
- legal/compliance
- fulfillment
- strategy

---

# 53. Opportunities Panel

Rank evidence-backed opportunities.

Each:

- opportunity
- evidence
- expected customer impact
- expected business impact
- confidence
- effort
- next experiment/action

Avoid generic idea lists.

---

# 54. Owner Decision Queue

This should be extremely prominent.

Only include decisions that genuinely require human authority.

Each decision:

**Decision needed**

**Why now**

**Recommended option**

**Alternatives**

**Impact of delay**

**Risk**

**Approval class**

Examples:

- RED financial commitment
- major production architecture change
- irreversible data action
- material pricing/brand decision outside autonomy
- legal/compliance issue

Do not ask the owner to approve routine autonomous work.

---

# 55. RED Approval Panel

Show:

- action
- requesting agent
- reason
- expected benefit
- risk
- rollback/reversibility
- cost if applicable
- requested by date

Owner actions:

- APPROVE
- REJECT
- MODIFY
- DEFER

Approval execution must still follow `AUTONOMY.md`.

---

# 56. Strategic Progress Panel

Show current phase:

- Phase 0 Operating Foundation
- Phase 1 Entryway Product-Market Learning
- Phase 2 Monetization Validation
- Phase 3 Repeatable Room Expansion
- Phase 4 Whole-Home Platform
- Phase 5 Scale

Show:

- current phase
- exit criteria
- completed criteria
- remaining criteria
- evidence confidence

Do not advance phases based on feature completion alone.

---

# 57. Entryway Validation Scorecard

Use evidence, not an arbitrary composite score.

Show each criterion individually:

- desired-function comprehension
- micro-zone engagement
- quest completion
- standards established
- sustainment
- repeat micro-zone use
- multi-player use
- purchase evidence
- organic demand
- customer feedback

Status:

- NOT MEASURED
- EARLY
- PROMISING
- VALIDATED
- CONTRADICTED

Criteria for `VALIDATED` must be documented.

---

# 58. Next Room Decision

When Phase 3 becomes relevant, dashboard should compare candidate rooms.

Potential dimensions:

- customer requests
- search demand
- current site behavior
- friction frequency
- micro-zone richness
- quest potential
- product potential
- repeat use
- implementation effort

Do not choose next room merely because content already exists.

---

# 59. Daily Autonomous Review

Claude should review the dashboard daily or on its configured operating cadence.

Process:

1. verify data freshness
2. check production health
3. check revenue/orders
4. inspect primary funnel
5. inspect active experiments
6. inspect workstreams
7. identify constraint
8. determine highest-value permitted action
9. update `STATUS.md` when materially necessary

Do not generate work solely because the queue is empty.

---

# 60. Weekly Executive Review

Dashboard should generate a weekly brief:

## Wins

What materially improved.

## Misses

What underperformed.

## Customer Learning

What was learned about household needs.

## Revenue

Performance and driver changes.

## Experiments

Results and next decisions.

## Production

Reliability/release state.

## Autonomous Work

Major completed work and outcomes.

## Next Week

Top 1-3 priorities.

## Owner Decisions

Only required decisions.

---

# 61. Monthly Business Review

Include:

- revenue vs target
- contribution economics
- acquisition
- activation
- quest/product outcomes
- retention/progression
- top products
- top content
- experiment portfolio
- strategic phase
- risks
- next-month priorities

Ask:

**What is now the primary constraint to sustainable $20K+ monthly revenue?**

---

# 62. Alerts

Dashboard alerts should be selective.

Potential immediate alerts:

- production outage
- checkout outage
- severe error spike
- critical security issue
- backup failure beyond tolerance
- disk exhaustion risk
- unexplained production/Git mismatch
- major revenue/payment reconciliation issue

Do not alert the owner for every minor fluctuation.

---

# 63. Business Watch Conditions

Potential watch items:

- meaningful traffic decline
- conversion deterioration
- quest completion deterioration
- refund increase
- stockout
- experiment guardrail breach
- search-index loss

Thresholds should be evidence-based.

---

# 64. Dashboard Freshness

Recommended:

## Near Real Time

- production status
- incidents
- critical journeys
- container health

## Hourly

- orders
- operational revenue
- deployments

## Daily

- SEO
- product funnels
- commerce performance
- experiments

## Weekly / Monthly

- retention
- sustainment
- strategic economics

Display source timestamp.

---

# 65. Dashboard Data API

Recommended response shape for a metric:

```json
{
  "metric_id": "net_revenue",
  "value": null,
  "unit": "USD",
  "period": "MTD",
  "comparison_value": null,
  "target": 20000,
  "source": "UNKNOWN",
  "refreshed_at": null,
  "confidence": "UNKNOWN",
  "status": "UNKNOWN"
}
```

`null` is preferable to fabricated zero.

---

# 66. Dashboard Storage

Do not use Markdown as the live metric database.

Use a small appropriate data layer discovered/designed based on actual architecture.

Markdown stores:

- definitions
- rules
- strategy
- summaries

Operational storage stores:

- time series
- events
- transactions
- telemetry

---

# 67. Dashboard Security

The executive dashboard should be private by default.

Protect:

- revenue
- infrastructure
- experiments
- customer information
- security findings
- deployment controls

Use authentication and least privilege.

Never expose production secrets to the browser.

---

# 68. Mobile Experience

The owner should be able to use the dashboard effectively on a phone.

Mobile first screen:

1. Production
2. Revenue vs $20K
3. Orders
4. Traffic
5. Quest Completion
6. Conversion
7. Primary Constraint
8. Claude Current Action
9. Owner Decision Count

Detailed technical panels can collapse.

---

# 69. Desktop Experience

Desktop should support deeper analysis with:

- trend charts
- funnels
- comparison tables
- drill-down
- experiment details
- release lineage
- infrastructure views

Avoid clutter.

---

# 70. Visual Design

Use the 6S Success visual system where practical.

Dashboard should feel:

- clean
- calm
- high-information
- executive
- trustworthy

Avoid:

- excessive gauges
- rainbow colors
- decorative 3D charts
- flashing indicators
- unnecessary animations

Use color primarily for status and meaning.

---

# 71. Charts

Preferred chart types:

- line charts for trends
- bars for category comparison
- funnels for staged conversion
- compact tables for ranked items
- sparklines for KPI cards

Avoid pie charts when category comparison matters.

Do not show a chart if one number and a trend arrow communicate the decision better.

---

# 72. Comparisons

Every major KPI should use an appropriate comparison when possible:

- prior 7 days
- prior 30 days
- prior month
- target
- experiment control
- historical baseline

Clearly label the comparison.

---

# 73. Confidence UI

Low-confidence data should look different from verified data.

Possible treatment:

`$8,420  [LOW CONFIDENCE]`

or:

`UNKNOWN: commerce source not connected`

Never hide uncertainty in a tooltip only.

---

# 74. Data Failure UI

If a source fails:

Do not show:

`Revenue: $0`

Show:

`Revenue: DATA STALE`

with:

`Last verified: [timestamp]`

and source status.

---

# 75. Claude Recommendations

Claude may show up to **three** executive recommendations.

Each must include:

- evidence
- expected impact
- effort
- risk
- action
- whether autonomous execution is permitted

Do not fill all three slots if only one good recommendation exists.

---

# 76. Primary Constraint

The dashboard should always attempt to identify one current primary constraint when evidence is sufficient.

Possible values:

- DATA
- TRAFFIC
- ACTIVATION
- QUEST COMPLETION
- PRODUCT FIT
- PRODUCT EXPOSURE
- CONVERSION
- AOV
- RETENTION
- MARGIN
- FULFILLMENT
- RELIABILITY
- UNKNOWN

This should directly influence backlog priority.

---

# 77. Constraint Confidence

Show:

- constraint
- evidence
- confidence

Example:

`Primary Constraint: ACTIVATION`
`Confidence: MEDIUM`

Evidence:

- organic traffic +22%
- desired-function starts stable
- completion rate down 18%
- purchase funnel unchanged after activation

Do not force a constraint if evidence is insufficient.

---

# 78. Autonomous Action Link

For the primary constraint, show:

**What Claude is doing now**

Example:

`Testing a shorter Entryway desired-function flow for new organic visitors.`

Then link to:

- experiment
- GitHub change
- expected metric
- review date

---

# 79. Change Impact Timeline

Create a timeline connecting:

**Change**
→ **Deployment**
→ **Experiment**
→ **Metric Movement**
→ **Decision**

This is crucial for continuous improvement.

---

# 80. Release Annotation

Annotate metric trend charts with major releases/experiments.

This helps investigation.

Do not infer causality solely from timing.

---

# 81. Incident Annotation

Annotate relevant charts with outages or major incidents.

Example:

A conversion decline during checkout outage should not be mistaken for product-market behavior.

---

# 82. Customer Feedback

If a reliable feedback source exists, show:

- major themes
- recurring friction
- product requests
- complaints
- positive outcomes

Use aggregated/sanitized summaries.

Do not expose private customer information.

---

# 83. Search-to-Product Intelligence

A high-value future view:

**Search Query**
→ **Landing Page**
→ **Room**
→ **Micro-Zone**
→ **Desired Function**
→ **Quest**
→ **Product**
→ **Revenue / Outcome**

This connects acquisition to customer value and monetization.

---

# 84. Micro-Zone Opportunity Map

Rank micro-zones by:

- demand
- friction frequency
- quest completion
- product opportunity
- sustained outcome

This can guide content and product development.

---

# 85. Root Cause Opportunity Map

Rank root causes by:

- diagnosis frequency
- unresolved rate
- quest success
- product gap
- repeat occurrence

This should help determine where 6S Success needs better solutions.

---

# 86. Product-Outcome Integrity

Do not optimize product sales independently of customer outcome.

Where possible compare:

**Product Purchased**
→ **Quest Completion**
→ **Sustainment**

If a product sells well but does not help the intended outcome, investigate.

---

# 87. Content-Outcome Integrity

Do not optimize content solely for clicks.

Compare:

**Content Visit**
→ **Useful Interaction**
→ **Quest**
→ **Outcome**
→ **Purchase where relevant**

A lower-traffic page may be strategically superior if it creates much more value.

---

# 88. Agent Guardrails

No agent may:

- alter dashboard definitions to make performance appear better
- hide negative metrics
- remove failed experiments from history
- suppress incidents
- change targets without authorization
- classify UNKNOWN as zero
- present estimates as actuals

---

# 89. Dashboard Change Governance

Material dashboard changes should preserve:

- metric definitions
- comparability
- source lineage
- executive usability

Changes to metric meaning belong in `METRICS.md`.

Changes to source authority belong in `DATA-SOURCES.md`.

---

# 90. Dashboard Development Sequence

## Stage 1: Skeleton

Build UI with `UNKNOWN` states.

Do not use fake production values.

## Stage 2: Operations

Connect:

- production availability
- GitHub release
- Docker/VPS
- backups

## Stage 3: Business

Connect:

- analytics
- search
- commerce
- payments

## Stage 4: Product

Connect:

- desired function
- root cause
- quests
- standards
- sustainment

## Stage 5: Intelligence

Add:

- constraint detection
- opportunity ranking
- recommendations
- experiment interpretation
- change-impact timeline

---

# 91. Minimum Viable Dashboard

The first useful production dashboard needs only:

- MTD Revenue
- $20K progress
- Orders
- Users
- Organic Sessions
- Search Clicks
- Quest Starts
- Quest Completions
- Purchase Conversion
- Production Status
- Running Release
- Backup Freshness
- Active Experiment(s)
- Active Workstreams
- Primary Constraint
- Pending Owner Decisions

Unknown values remain UNKNOWN.

---

# 92. Dashboard Acceptance Criteria

The initial dashboard is acceptable when:

1. it is private
2. it is mobile usable
3. every displayed metric has a canonical definition
4. every actual value has a source
5. freshness is visible
6. UNKNOWN is handled correctly
7. production release identity is visible
8. revenue is reconciled appropriately
9. active autonomous work is visible
10. owner decisions are obvious
11. no secrets are exposed
12. the owner can understand the current state quickly

---

# 93. Dashboard Validation

Before trusting the dashboard:

- manually compare sample orders
- manually compare revenue
- compare analytics totals
- compare Search Console
- compare running Docker release
- verify backup timestamps
- trigger safe test events
- confirm test data exclusions

Record discrepancies.

---

# 94. Executive Dashboard URL

The exact URL should be determined by the deployed architecture.

Prefer a private route/subdomain such as:

`dashboard.6S-success.com`

or:

`6S-success.com/admin/executive`

Do not expose it publicly merely because the route is obscure.

Security must not depend on URL secrecy.

---

# 95. Owner Actions

The dashboard may eventually support safe owner actions such as:

- approve/reject RED action
- pause experiment
- acknowledge risk
- reprioritize workstream
- request analysis

High-risk operational actions should not become one-click dashboard controls without appropriate safeguards.

---

# 96. Autonomous Read Loop

Claude should be able to consume the same normalized dashboard data programmatically.

This avoids separate realities:

**Owner Dashboard Truth**
and
**Agent Truth**

They should derive from the same metric/source layer.

---

# 97. Autonomous Write Loop

Agents should write operational outcomes back to appropriate systems:

- GitHub
- experiment registry
- backlog
- decisions
- learnings
- status

Do not write directly into historical metrics to make outcomes appear successful.

---

# 98. Executive Dashboard vs STATUS.md

`STATUS.md` is a concise living operational narrative.

The dashboard is live quantitative/operational visibility.

Use:

**Dashboard**
→ current measured state

**STATUS.md**
→ interpreted current state, active work, known issues

The dashboard should inform status updates.

---

# 99. Executive Dashboard vs BACKLOG.md

Dashboard identifies:

- constraints
- risks
- opportunities

`BACKLOG.md` converts those into prioritized work.

Do not turn the dashboard into a task-management system.

---

# 100. Executive Dashboard vs DECISIONS.md

Dashboard surfaces decisions.

`DECISIONS.md` records durable decisions and rationale.

Do not rely on dashboard history as the sole decision record.

---

# 101. Executive Dashboard vs LEARNINGS.md

Dashboard shows evidence.

`LEARNINGS.md` stores durable validated learning.

Do not convert every short-term metric fluctuation into a learning.

---

# 102. Initial Owner View Example

When sources are first being connected, a truthful dashboard may look like:

**Revenue:** UNKNOWN  
Commerce source not verified.

**Traffic:** UNKNOWN  
Analytics source not verified.

**SEO:** UNKNOWN  
Search Console not verified.

**Quest Completion:** UNKNOWN  
Product event instrumentation not verified.

**Production:** HEALTHY  
Verified external checks.

**Release:** MATCHED  
Git SHA and running image verified.

**Backups:** WATCH  
Backup job verified, restore test not yet completed.

**Primary Constraint:** DATA  
Critical business sources are not yet verified.

This is a successful early dashboard because it tells the truth.

---

# 103. Mature Owner View Example

A mature dashboard should be able to say something like:

**Revenue is ahead of last month's pace but below the $20K target trajectory. Organic qualified traffic is growing. Entryway quest completion improved after the latest flow change. Purchase conversion is stable. AOV is currently the strongest monetization constraint. Production is healthy and backups are restore-tested. Claude is testing an Entryway bundle designed to increase AOV without reducing quest completion. No owner decision is required today.**

Only generate statements like this from verified evidence.

---

# 104. Strategic Success

The dashboard is successful when the owner does **not** need to:

- SSH into the VPS to know whether production is healthy
- browse GitHub to determine what deployed
- manually check multiple analytics systems
- guess why revenue changed
- ask what Claude has been doing
- search documents for active experiments
- wonder whether backups work
- repeatedly ask what decision is needed

The dashboard should consolidate those answers.

---

# 105. Final Dashboard Principle

The executive dashboard should make autonomous operation **more transparent, not less**.

Claude should have enough freedom to improve the business continuously.

The owner should always be able to see:

**what is happening**

**what changed**

**why it changed**

**what Claude is doing**

**whether it worked**

**what is at risk**

**what needs a human decision**

The dashboard is the control surface connecting autonomous execution to human ownership.

Its ultimate purpose is not reporting.

Its purpose is to help 6S Success continuously make better decisions while building a trusted path toward meaningful customer outcomes and sustainable $20K+ monthly revenue.
