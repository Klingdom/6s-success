# 6S Success Cost Governance and Unit Economics

> Canonical policy for autonomous spending, infrastructure cost, AI/API usage, SaaS subscriptions, advertising, storage, observability, commerce fees, product economics, gross margin, budget thresholds, cost anomaly detection, and owner approval for 6S-success.com.

## 1. Purpose

`COST-GOVERNANCE.md` defines how Claude Code and specialist agents manage money while operating and growing 6S Success.

The objective is not simply to minimize cost.

The objective is to maximize:

**Customer Value + Sustainable Revenue + Learning Velocity + Reliability**

while controlling:

**Cash Burn + Waste + Vendor Risk + Low-Margin Growth + Unapproved Commitments**

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `METRICS.md`
- `OBSERVABILITY.md`
- `RELEASES.md`
- `SECURITY.md`
- `EXPERIMENTS.md`
- `BACKLOG.md`
- `STATUS.md`
- `DECISIONS.md`
- `LEARNINGS.md`

---

# 2. Prime Rule

**Claude may optimize approved resources autonomously, but it may not create material new financial commitments without authority.**

Autonomy to operate software is not unlimited authority to spend money.

---

# 3. Financial Objectives

The autonomous system should help 6S Success achieve:

1. positive customer value
2. increasing revenue
3. healthy gross margin
4. controlled recurring cost
5. measurable acquisition economics
6. efficient AI/API usage
7. infrastructure proportional to demand
8. minimal unused subscriptions
9. reliable commerce
10. sustainable path beyond $20,000/month revenue

---

# 4. Revenue Goal

Initial business target:

```yaml
monthly_revenue_target_usd: 20000
```

This is a target, not a forecast.

Claude must not imply the target has been achieved without authoritative commerce evidence.

---

# 5. Cost Categories

Track separately:

## Infrastructure

- Hostinger VPS
- storage
- backups
- domain/DNS
- CDN
- registry
- database

## Software / SaaS

- analytics
- observability
- email
- design/content tools
- automation
- SEO tools

## AI / API

- LLM inference
- image generation
- embeddings
- search APIs
- external data APIs

## Commerce

- payment processing
- storefront/platform
- transaction fees
- refunds/chargebacks
- fulfillment

## Acquisition

- paid advertising
- sponsorships
- affiliates
- creator partnerships

## Product Cost

- physical manufacturing
- printing
- packaging
- shipping
- digital delivery

## Labor / Services

Only where explicitly tracked and relevant.

---

# 6. Financial Source of Truth

For each cost/revenue category define the authoritative source.

Examples:

| Metric | Preferred Authority |
|---|---|
| Paid orders | Commerce provider |
| Refunds | Commerce provider |
| VPS cost | Hostinger billing |
| AI usage | AI provider billing |
| SaaS cost | Vendor billing |
| Ad spend | Ad platform |
| Shipping | Fulfillment/carrier source |

Analytics estimates are not authoritative accounting records.

---

# 7. Cost Ledger

Maintain a machine-readable cost ledger where practical.

Suggested fields:

```yaml
cost_id:
vendor:
category:
service:
amount_usd:
billing_period:
recurring: true|false
committed: true|false
approved_by:
source:
observed_at:
notes:
```

Do not store payment credentials.

---

# 8. Recurring Commitments

Recurring costs deserve special attention because small subscriptions accumulate.

Track:

- vendor
- purpose
- monthly/annual cost
- renewal date
- owner
- utilization
- business value
- cancellation method
- replacement dependency

---

# 9. Spending Authority Model

Use `AUTONOMY.md` as final authority.

Recommended conceptual tiers:

## GREEN

No new financial commitment.

Examples:

- optimize existing Docker resources
- reduce unnecessary logs
- delete safe obsolete build artifacts according to retention policy
- improve caching
- optimize AI prompts/model selection within approved providers

## YELLOW

Small reversible spend within a pre-approved budget.

Only allowed if explicit budget authority exists.

## RED

Requires owner approval.

Examples:

- new paid SaaS subscription
- new VPS plan
- paid advertising campaign
- annual contract
- meaningful recurring cost
- purchasing inventory
- changing customer pricing materially
- increasing AI budget materially

---

# 10. No Assumed Budget

Until the owner establishes explicit limits:

```yaml
autonomous_new_recurring_spend_usd: 0
autonomous_paid_ad_spend_usd: 0
autonomous_inventory_purchase_usd: 0
```

Claude may recommend spending but should not assume authority.

---

# 11. Budget Configuration

Once approved, store policy rather than payment data.

Example:

```yaml
budgets:
  infrastructure_monthly_usd: TBD
  ai_api_monthly_usd: TBD
  saas_monthly_usd: TBD
  paid_acquisition_monthly_usd: TBD

autonomous_limits:
  max_new_monthly_commitment_usd: TBD
  max_single_reversible_experiment_usd: TBD
```

Use `TBD` until explicitly approved.

---

# 12. Cost Baseline

Before aggressive optimization, establish current monthly baseline.

At minimum:

- infrastructure
- AI/API
- SaaS
- commerce fees
- acquisition
- product costs

Do not invent missing numbers.

---

# 13. Cost Freshness

Every cost dashboard should show source and freshness.

Example:

```yaml
ai_cost_mtd_usd: 143.20
source: provider_billing
observed_at: 2026-08-14T20:00:00Z
confidence: VERIFIED
```

---

# 14. Cost Status

Use:

- `HEALTHY`
- `ATTENTION`
- `OVER_BUDGET`
- `UNKNOWN`
- `NOT_APPLICABLE`

Missing data is `UNKNOWN`, not zero.

---

# 15. Cost Anomaly Detection

Detect:

- sudden AI usage increase
- unexpected VPS billing
- storage growth
- observability ingestion spike
- duplicate SaaS subscriptions
- unexpected commerce fees
- advertising overspend

Investigate before taking destructive action.

---

# 16. Cost Alert Requirements

A useful alert includes:

- category
- current spend
- baseline/budget
- variance
- likely driver
- expected business impact
- recommended action
- authority required

---

# 17. Infrastructure Cost Governance

Claude should prefer the smallest infrastructure that reliably supports current demand and reasonable headroom.

Do not scale merely because CPU briefly spikes.

Use evidence:

- sustained CPU
- memory pressure
- disk
- latency
- traffic
- error rate
- capacity trends

---

# 18. Hostinger VPS Optimization

Potential safe optimization:

- remove unused containers
- right-size log retention
- clean safe Docker artifacts
- optimize application memory
- improve caching
- reduce unnecessary services

Never delete unknown volumes or backups to save space.

---

# 19. Scaling Decision

Before recommending a larger VPS, document:

```yaml
constraint:
evidence:
current_capacity:
peak_usage:
customer_impact:
optimization_attempts:
proposed_upgrade:
monthly_cost_delta:
expected_benefit:
```

---

# 20. Storage Cost

Monitor:

- database growth
- images
- product assets
- backups
- logs
- Docker images

Separate valuable business assets from disposable operational artifacts.

---

# 21. Backup Cost

Do not reduce backup quality simply to save a small amount.

Evaluate backup spending against recovery value defined in `DISASTER-RECOVERY.md`.

---

# 22. Observability Cost

Telemetry should be useful.

Control:

- log volume
- retention
- high-cardinality dimensions
- trace sampling
- duplicate ingestion

Never disable critical security/payment/error visibility solely to lower cost.

---

# 23. AI Cost Governance

AI usage should be attributable where practical to:

- feature
- agent
- task
- provider
- model
- environment

This allows cost-per-outcome analysis.

---

# 24. AI Usage Fields

Suggested:

```yaml
provider:
model:
feature:
agent:
requests:
input_tokens:
output_tokens:
estimated_cost_usd:
successful_outcomes:
period:
```

Use provider-supported billing data when available.

---

# 25. AI Model Selection

Use the least expensive model that reliably meets the quality requirement.

Do not automatically use the largest model for:

- classification
- extraction
- formatting
- simple routing
- deterministic transformations

Higher-capability models are justified when they materially improve outcomes.

---

# 26. AI Routing

Potential strategy:

**Deterministic code first**
→ **small/efficient model**
→ **larger model for complex reasoning**

when quality supports it.

Do not add model-routing complexity without measurable benefit.

---

# 27. AI Caching

Cache safely reusable AI outputs when:

- inputs are stable
- privacy permits
- staleness is acceptable
- cost savings matter

Do not cache private household outputs into shared public state.

---

# 28. AI Retry Cost

Retries can multiply cost.

Use:

- bounded retries
- backoff
- error classification
- idempotency

Do not repeatedly retry permanent failures.

---

# 29. AI Agent Cost

Autonomous agents should not perform endless low-value loops.

Track:

- cost per task
- commits/results per task
- measurable business outcome
- repeated failed attempts

Stop or escalate runaway loops.

---

# 30. AI Cost Kill Switch

Establish a mechanism to halt noncritical AI spending if:

- budget exceeded
- runaway loop detected
- provider billing anomaly
- compromised credentials suspected

Critical customer functionality should degrade gracefully where possible.

---

# 31. SaaS Governance

Before recommending a new paid tool, answer:

1. What problem does it solve?
2. Can current tools solve it?
3. What is monthly/annual cost?
4. Is there lock-in?
5. What data does it receive?
6. What integration burden exists?
7. What measurable outcome justifies it?
8. How is it cancelled?

---

# 32. Duplicate Tools

Avoid paying for multiple tools that perform essentially the same function unless there is a justified need.

Review periodically.

---

# 33. Free Tier Governance

Free is not automatically better.

Evaluate:

- limits
- reliability
- data/privacy
- operational burden
- upgrade cliff
- vendor stability

---

# 34. Annual Contracts

Annual commitments require owner approval unless explicitly pre-authorized.

Show:

- annual cost
- monthly equivalent
- savings vs monthly
- cancellation risk
- expected use

---

# 35. Paid Acquisition

Paid advertising should be treated as an experiment before becoming a scaling channel.

Do not spend simply to increase traffic.

Measure:

**Spend → Qualified Visit → Desired Function/Quest → Purchase → Margin**

---

# 36. Acquisition Metrics

Track:

- spend
- impressions
- clicks
- CPC
- qualified visits
- leads where applicable
- purchases
- CAC
- revenue
- gross profit
- ROAS
- payback period where relevant

Definitions belong in `METRICS.md`.

---

# 37. CAC

Customer Acquisition Cost:

```text
CAC = attributable acquisition spend / acquired customers
```

State attribution model and period.

---

# 38. ROAS

```text
ROAS = attributable revenue / advertising spend
```

ROAS is not profit.

---

# 39. Contribution Margin

A more useful growth measure may be:

```text
Contribution Margin =
Revenue
- payment fees
- fulfillment/product variable costs
- attributable AI/API variable costs
- attributable acquisition cost
```

Exact definition must be standardized in `METRICS.md`.

---

# 40. Paid Scaling Rule

Do not scale an acquisition channel solely because revenue exceeds ad spend.

Consider:

- refunds
- product cost
- payment fees
- shipping
- repeat purchase
- support burden
- margin

---

# 41. Organic Acquisition Economics

SEO/AEO/content is not free.

Track where useful:

- content production cost
- AI cost
- tooling
- traffic
- conversions
- revenue
- assisted outcomes

Do not over-engineer attribution early.

---

# 42. Product Economics

Each sellable product should eventually have:

```yaml
product_id:
price:
discount:
net_revenue:
variable_cost:
payment_fee:
fulfillment_cost:
shipping_subsidy:
estimated_contribution_margin:
refund_rate:
```

Digital and physical products differ substantially.

---

# 43. Digital Product Economics

Digital products can have high gross margins but still incur:

- payment fees
- platform fees
- AI generation cost
- support
- storage/delivery
- acquisition

Do not call revenue profit.

---

# 44. Physical Product Economics

Include:

- manufacturing
- printing
- packaging
- inbound freight
- storage
- pick/pack
- shipping subsidy
- returns
- damaged inventory
- transaction fees

Do not scale a physical product without understanding landed economics.

---

# 45. Inventory Governance

Purchasing physical inventory is a financial commitment.

Default: owner approval required.

Before recommending purchase:

- demand evidence
- unit cost
- MOQ
- lead time
- storage
- expected sell-through
- margin
- downside if unsold

---

# 46. Print-on-Demand

Print-on-demand may reduce inventory risk at higher unit cost.

Evaluate total economics and customer experience.

---

# 47. Product Pricing

Claude may analyze and recommend pricing.

Material price changes should follow autonomy/approval policy.

Before changing price, consider:

- customer value
- conversion
- margin
- alternatives
- refunds
- positioning
- experiment design

---

# 48. Discount Governance

Discounts reduce revenue and can alter customer expectations.

Track:

- code/campaign
- discount value
- orders
- incremental conversion where measurable
- contribution margin

Do not leave temporary discounts active indefinitely.

---

# 49. Refund Economics

Monitor:

- refund rate
- product
- reason
- acquisition source
- cohort

A high-revenue product with high refunds may be poor business.

---

# 50. Chargebacks

Track separately from refunds.

A spike may indicate:

- customer confusion
- fraud
- fulfillment problem
- misleading marketing

Escalate material anomalies.

---

# 51. Revenue Quality

Prefer revenue that is:

- profitable
- low-refund
- repeatable
- aligned to customer value
- operationally supportable

Do not optimize for gross sales alone.

---

# 52. Gross Margin

Define formally in `METRICS.md`.

Typical concept:

```text
Gross Margin % =
(Revenue - Cost of Goods Sold) / Revenue
```

For digital services/products, classification must be consistent.

---

# 53. Unit Economics by Product

Rank products not only by revenue but also by:

- contribution margin
- conversion
- refund rate
- repeat purchase
- customer outcome
- support burden

---

# 54. Unit Economics by Micro-Zone

As the system matures, analyze economics by:

- room
- micro-zone
- desired function
- root cause
- quest

This can reveal which problems customers most value solving.

---

# 55. Cost Per Quest

Potential future metric:

```text
Cost per Quest Completion =
attributable variable platform/AI cost / completed quests
```

Useful if AI features create meaningful variable cost.

---

# 56. Revenue Per Quest

Potential:

```text
Revenue per Quest Starter
Revenue per Quest Completer
```

Use defined attribution windows.

---

# 57. Lifetime Value

Do not fabricate LTV early.

Estimate only when sufficient repeat-purchase/retention evidence exists.

Label model assumptions.

---

# 58. Break-Even Analysis

For paid experiments:

```text
Break-even CAC ≈ contribution margin available for acquisition
```

Use actual product economics rather than arbitrary industry benchmarks.

---

# 59. Experiment Budget

Every paid experiment should define:

```yaml
experiment_id:
max_spend_usd:
duration:
primary_metric:
stop_condition:
success_condition:
owner_approval:
```

Do not let experiments run indefinitely.

---

# 60. Stop-Loss

Paid experiments should have stop-loss rules.

Examples:

- maximum spend
- unacceptable CAC
- severe refund rate
- tracking failure
- security issue
- no valid measurement

---

# 61. Cost of Learning

Some experiments can lose money and still be valuable.

But the learning objective must be explicit.

Do not label uncontrolled spending "learning."

---

# 62. Revenue Reinvestment

Claude may recommend reinvesting profits into:

- acquisition
- product development
- content
- infrastructure
- customer experience

Actual reinvestment authority must be explicit.

---

# 63. Monthly Cost Review

Review:

- revenue
- gross/contribution margin
- infrastructure
- AI/API
- SaaS
- commerce fees
- acquisition
- product costs
- anomalies
- unused commitments

---

# 64. Vendor Review

For material vendors ask:

- still needed?
- usage?
- cost trend?
- reliability?
- cheaper tier?
- better alternative?
- lock-in?
- security/privacy?

Do not churn vendors for trivial savings that create operational risk.

---

# 65. Cost Optimization Backlog

Create opportunities such as:

- reduce AI model cost
- right-size VPS
- reduce log retention
- remove unused SaaS
- improve image compression
- improve cache hit rate
- reduce payment/fulfillment friction

Prioritize by savings × effort × risk.

---

# 66. Cost Reduction Verification

Never claim savings merely because a change "should" reduce cost.

Measure before and after.

Record:

- baseline
- new cost
- period
- volume normalization
- actual savings
- side effects

---

# 67. Avoid False Savings

Examples:

Saving $10/month while creating hours of maintenance is not necessarily valuable.

Reducing server capacity until conversion suffers is not savings.

Deleting backups to save storage is not acceptable optimization.

---

# 68. Cost vs Reliability

Reliability has economic value.

Do not optimize infrastructure cost below the level needed for:

- customer trust
- checkout reliability
- data protection
- recovery

---

# 69. Cost vs Security

Security controls are not ordinary waste.

Do not remove:

- backups
- MFA
- monitoring
- vulnerability management
- access controls

solely for small savings.

---

# 70. Cost vs Speed

Sometimes a paid tool materially accelerates learning or revenue.

Evaluate total economic impact, not subscription price alone.

---

# 71. Cost Forecasting

Forecasts must disclose method.

Potential simple model:

```text
Projected Month-End Cost =
MTD Cost / elapsed days × days in month
```

Only when spending is reasonably linear.

For non-linear costs, use a more appropriate model.

---

# 72. Revenue Forecasting

Likewise, projections are not commitments.

Display:

- actual MTD
- projection
- method
- confidence
- major assumptions

---

# 73. Scenario Planning

Useful scenarios:

- base
- conservative
- growth

Variables:

- traffic
- conversion
- AOV
- acquisition spend
- product margin
- AI cost
- infrastructure

Do not present scenarios as predictions.

---

# 74. $20K Revenue Equation

Claude should decompose the goal.

Examples:

```text
Revenue = Visitors × Purchase Conversion × AOV
```

or:

```text
Revenue = Number of Orders × AOV
```

Example combinations should be clearly illustrative, not forecasts.

---

# 75. Constraint Economics

Identify the current constraint before spending.

Examples:

If traffic is low but conversion is strong:
→ acquisition may be constraint.

If traffic is high but purchase conversion is weak:
→ spending more on traffic may waste money.

If purchases occur but refunds are high:
→ product/customer fit may be constraint.

---

# 76. Executive Financial Dashboard

Recommended:

## Revenue

- MTD revenue
- monthly target
- projection
- orders
- AOV

## Economics

- gross margin
- contribution margin
- refund rate
- CAC if applicable

## Costs

- infrastructure
- AI/API
- SaaS
- acquisition
- commerce
- product

## Efficiency

- cost per purchase
- revenue per visitor
- AI cost per valuable outcome where relevant

## Decisions

- new spend approvals
- cost anomalies
- scaling recommendations

---

# 77. Dashboard Financial Confidence

Each metric:

```yaml
value:
source:
observed_at:
confidence: VERIFIED|PARTIAL|STALE|UNKNOWN
```

Do not show stale vendor billing as real-time.

---

# 78. Owner Approval Request

For a proposed spend:

## Proposal

What Claude wants to purchase/change.

## Cost

One-time and recurring.

## Why

Constraint/opportunity.

## Expected Outcome

Metric and hypothesis.

## Alternatives

Including no-spend option.

## Risk

Financial, technical, vendor.

## Exit

How to cancel/reverse.

## Recommendation

Approve / reject / test smaller.

---

# 79. Subscription Approval Example

Good:

> Recommend adding an SEO platform at $99/month only after current free search data proves insufficient for the next prioritized experiment. Expected decision value: faster query/page opportunity analysis. Current recommendation: do not purchase yet.

This protects against tool accumulation.

---

# 80. Autonomous Savings

Claude may normally implement reversible savings inside existing approved services if:

- customer impact is protected
- security is protected
- recovery is protected
- no new commitment is created
- tests verify behavior

---

# 81. Vendor Cancellation

Cancellation can have destructive consequences.

Before cancelling:

- identify dependencies
- export required data
- identify replacement
- verify retention/deletion
- confirm authority

Material cancellation may require approval.

---

# 82. Cost Attribution

Where practical tag costs to:

- environment
- service
- feature
- agent
- product
- campaign

Do not create high-cardinality telemetry solely for perfect accounting.

---

# 83. Development vs Production Cost

Separate where possible.

Test/agent loops should not silently consume production-scale resources.

---

# 84. Cost Controls in CI/CD

Potential controls:

- limit runaway workflow loops
- cache dependencies appropriately
- avoid redundant builds
- clean artifacts per retention policy
- use concurrency controls

Do not sacrifice release traceability for trivial savings.

---

# 85. Cost Controls for Autonomous Content

Track:

- AI generation cost
- image cost
- publishing volume
- organic traffic
- conversions
- revenue

Do not mass-generate content simply because generation is cheap.

---

# 86. Content ROI

A content asset may be evaluated over a longer horizon.

Potential:

```text
Content Contribution =
attributable/assisted contribution margin - creation/maintenance cost
```

Use caution with attribution.

---

# 87. Cost Controls for Images

High-resolution image generation/storage can become costly.

Use:

- purposeful generation
- reuse where appropriate
- optimized delivery
- sensible dimensions
- archival policy

Do not degrade product quality purely for minimal storage savings.

---

# 88. API Key Budget Controls

Where providers support it:

- spending limits
- rate limits
- usage alerts
- scoped keys

Use technical limits in addition to Markdown policy.

---

# 89. Cost Incident

Declare a cost incident for:

- runaway API usage
- compromised billing credential
- unexpected large charge
- uncontrolled ad spend
- duplicate fulfillment
- severe billing anomaly

Contain first, then diagnose.

---

# 90. Runaway AI Procedure

1. stop noncritical agent/API execution
2. verify provider usage
3. revoke/limit compromised key if necessary
4. identify loop/task
5. preserve evidence
6. fix retry/loop controls
7. test
8. re-enable gradually
9. update learnings

---

# 91. Runaway Advertising Procedure

1. pause affected campaign if authorized
2. verify actual spend
3. inspect automation/rules
4. verify tracking
5. reconcile charges
6. require owner approval before resuming if material

---

# 92. Cost and Disaster Recovery

Do not cut DR capability without evaluating business risk.

Follow `DISASTER-RECOVERY.md`.

---

# 93. Cost and Security

Do not weaken security to hit arbitrary cost targets.

Follow `SECURITY.md`.

---

# 94. Cost and Experiments

Every paid experiment should have a budget and stop condition.

Follow `EXPERIMENTS.md`.

---

# 95. Cost and Observability

Financial anomalies should appear in the executive dashboard.

Follow `OBSERVABILITY.md`.

---

# 96. Cost and Releases

A release that materially changes variable cost should identify expected impact.

Examples:

- new AI feature
- new image processing
- increased logging
- external API integration

---

# 97. Current Financial State

Populate only from verified sources:

```yaml
targets:
  monthly_revenue_usd: 20000

revenue:
  current_mtd_usd: UNKNOWN
  source: UNKNOWN

infrastructure:
  hostinger_monthly_usd: UNKNOWN
  storage_monthly_usd: UNKNOWN
  backup_monthly_usd: UNKNOWN

ai_api:
  providers: UNKNOWN
  current_mtd_usd: UNKNOWN
  monthly_budget_usd: UNKNOWN

saas:
  subscriptions: UNKNOWN
  monthly_total_usd: UNKNOWN

commerce:
  provider: UNKNOWN
  processing_fees_mtd_usd: UNKNOWN
  refunds_mtd_usd: UNKNOWN

acquisition:
  paid_spend_mtd_usd: UNKNOWN
  approved_budget_usd: 0

products:
  gross_margin: UNKNOWN
  contribution_margin: UNKNOWN

autonomy:
  new_recurring_spend_limit_usd: 0
  paid_ad_spend_limit_usd: 0
  inventory_purchase_limit_usd: 0

financial_dashboard:
  implementation: UNKNOWN
  last_verified: UNKNOWN
```

The zero autonomous limits remain until explicitly changed by owner policy.

---

# 98. First Cost-Governance Mission

Once legitimate billing/data access exists:

1. inventory vendors
2. identify recurring commitments
3. establish authoritative sources
4. calculate current monthly baseline
5. identify variable costs
6. map costs to major services/features where useful
7. calculate initial product economics
8. identify waste/anomalies
9. establish alerts
10. connect costs to executive dashboard
11. identify highest-value savings
12. identify spending opportunities requiring owner approval
13. update Current Financial State
14. create prioritized backlog

Do not cancel or purchase services during discovery.

---

# 99. Cost Maturity Model

## Level 0 — Unknown

Costs are scattered and poorly understood.

## Level 1 — Visible

Recurring and variable costs are inventoried.

## Level 2 — Controlled

Budgets, alerts, and authority boundaries exist.

## Level 3 — Attributed

Major costs connect to products, features, and acquisition.

## Level 4 — Optimized

Claude continuously improves cost efficiency without harming customer outcomes.

## Level 5 — Economic Autonomy

The system can safely allocate pre-approved budgets toward measured opportunities, stop poor-performing spend, and recommend capital allocation using reliable unit economics.

---

# 100. Definition of Financially Healthy Autonomy

Claude's autonomy is financially healthy when:

- every material recurring cost is known
- new spending authority is explicit
- runaway usage has technical controls
- product economics are measurable
- revenue is reconciled
- paid acquisition has stop-loss rules
- infrastructure scales from evidence
- AI cost maps to value
- owner sees material financial decisions
- savings are verified
- growth is evaluated on margin and customer value, not revenue alone

---

# 101. Non-Negotiable Rules

Claude and subagents must not:

- create paid subscriptions without authority
- launch paid advertising without authority
- buy physical inventory without authority
- hide recurring costs
- treat analytics revenue as accounting truth
- treat revenue as profit
- scale ads solely on ROAS
- fabricate CAC/LTV/margin
- disable critical backups/security to save money
- delete unknown data to reduce storage
- let AI agents loop without cost controls
- leave temporary paid experiments running indefinitely
- present forecasts as actuals
- optimize cost while materially harming customer value

---

# 102. Final Principle

The objective is not a cheap website.

The objective is a **profitable, resilient, continuously improving business**.

Claude should learn to answer:

**What are we spending?**

**Why are we spending it?**

**What customer or business outcome does it create?**

**What is the unit economics?**

**Can we achieve the same outcome more efficiently?**

**Should we invest more?**

**Should we stop?**

**Does the owner need to approve this?**

As 6S Success grows beyond $20,000 per month, the autonomous system should increasingly allocate attention based on **contribution margin, customer outcomes, growth constraints, and risk-adjusted return**, not merely traffic, activity, or gross revenue.

That is the purpose of `COST-GOVERNANCE.md`.
