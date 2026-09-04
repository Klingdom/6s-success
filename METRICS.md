# 6S Success Metrics Dictionary

> Canonical metric definitions, formulas, dimensions, guardrails, and measurement rules for 6S Success.

## 1. Purpose

`METRICS.md` defines **exactly how 6S Success measures customer value, product usage, acquisition, commerce, growth, experiments, and reliability**.

All agents must use these definitions unless a metric is explicitly revised through the decision process.

This file answers:

**What does the metric mean?**

`DATA-SOURCES.md` answers:

**Where does the data come from?**

`DASHBOARD.md` answers:

**How should the metric be presented?**

`STATUS.md` answers:

**What is happening now?**

Do not put manually invented live values in this file.

---

# 2. Measurement Principles

1. Measure customer outcomes, not merely activity.
2. Use one canonical definition for each KPI.
3. Distinguish counts, rates, dollars, and cohorts.
4. Distinguish gross revenue from profit.
5. Use verified data sources.
6. Report data confidence.
7. Do not silently change metric definitions.
8. Do not optimize a metric by undermining its meaning.
9. Use guardrail metrics for experiments.
10. Prefer simple useful metrics over large vanity dashboards.

---

# 3. Metric Naming Convention

Use stable machine-friendly names where possible.

Examples:

`users`
`sessions`
`organic_sessions`
`assessment_start_rate`
`quest_completion_rate`
`purchase_conversion_rate`
`gross_revenue`
`net_revenue`
`aov`
`refund_rate`
`repeat_purchase_rate`
`site_availability`

Human-readable dashboards may use friendly labels.

---

# 4. Required Metric Metadata

Every important metric should eventually define:

- metric ID
- display name
- business question
- formula
- numerator
- denominator
- unit
- grain
- time window
- dimensions
- authoritative source
- refresh frequency
- exclusions
- caveats
- owner
- confidence

Authoritative source mapping belongs in `DATA-SOURCES.md`.

---

# 5. Data Confidence

Use:

## HIGH

Authoritative source is connected, validated, timely, and reconciliation is acceptable.

## MEDIUM

Source is credible but has known latency, incomplete coverage, or unresolved minor discrepancies.

## LOW

Data is incomplete, inferred, manually maintained, or materially uncertain.

## UNKNOWN

No verified source exists.

Never display an uncertain number as authoritative without confidence context.

---

# 6. Time Windows

Standard windows:

- Today
- Yesterday
- Last 7 days
- Last 30 days
- Month to date
- Previous comparable period
- Rolling 90 days
- Cohort-based period where applicable

Avoid comparing unequal windows without labeling them.

---

# 7. User

## Metric ID

`users`

## Definition

Distinct recognized visitors/users during the selected period according to the authoritative analytics identity model.

## Important

A user is not necessarily:

- a customer
- an account
- a household
- a person uniquely identified across all devices

The analytics implementation must document identity behavior.

---

# 8. Session

## Metric ID

`sessions`

## Definition

A distinct website/application session according to the authoritative analytics platform's session rules.

Do not mix sessions from different platforms without reconciliation.

---

# 9. New Users

## Metric ID

`new_users`

Distinct users classified as first-time users by the authoritative analytics system.

Use cautiously when identity is cookie/device based.

---

# 10. Returning Users

## Metric ID

`returning_users`

Distinct users observed in a prior period and returning during the selected period, according to the analytics identity model.

---

# 11. Traffic by Channel

## Metric ID

`users_by_channel`

Primary dimensions may include:

- Organic Search
- Direct
- Referral
- Organic Social
- Paid Search
- Paid Social
- Email
- Other

Maintain consistent attribution rules.

---

# 12. Organic Sessions

## Metric ID

`organic_sessions`

Sessions attributed to unpaid search traffic.

Use the authoritative analytics attribution model.

Search Console clicks are a different metric and should not be substituted silently.

---

# 13. Search Impressions

## Metric ID

`search_impressions`

Number of times a 6S Success result was shown in eligible search results according to the authoritative search-performance source.

---

# 14. Search Clicks

## Metric ID

`search_clicks`

Clicks from eligible search results to 6S Success according to the authoritative search-performance source.

---

# 15. Organic CTR

## Metric ID

`organic_ctr`

Formula:

**Search Clicks / Search Impressions**

Express as percentage.

Do not calculate using analytics sessions.

---

# 16. Average Search Position

## Metric ID

`average_search_position`

Use the authoritative search platform's definition.

Treat as directional.

Do not treat average position as a direct business outcome.

---

# 17. Indexed Pages

## Metric ID

`indexed_pages`

Number of canonical site pages verified as indexed according to the authoritative search/index source.

More indexed pages is not automatically better.

---

# 18. Qualified Landing Session

## Metric ID

`qualified_landing_sessions`

A session entering through a content/product landing page that performs at least one defined meaningful engagement action.

Initial candidate qualifying actions:

- micro-zone selection
- desired-function interaction
- assessment start
- quest interaction
- product-detail interaction

Final implementation must be documented.

This metric helps distinguish useful traffic from raw traffic.

---

# 19. Room View

## Metric ID

`room_views`

Count of valid views of a room experience.

Dimension:

`room_id`

Avoid double-counting technical rerenders as page views.

---

# 20. Micro-Zone View

## Metric ID

`microzone_views`

Count of valid views of a micro-zone experience.

Dimensions:

- `room_id`
- `microzone_id`

---

# 21. Desired Function Start

## Metric ID

`desired_function_starts`

Count of sessions/users beginning Personal Function Discovery.

---

# 22. Desired Function Completion

## Metric ID

`desired_function_completions`

Count of successful Personal Function Discovery completions where a valid desired-function result is produced or selected.

---

# 23. Desired Function Completion Rate

## Metric ID

`desired_function_completion_rate`

Formula:

**Desired Function Completions / Desired Function Starts**

Use the same attribution/window logic for numerator and denominator.

---

# 24. Desired Function Distribution

## Metric ID

`desired_function_distribution`

Share of completed desired-function selections by function/value.

Useful dimensions:

- room
- micro-zone
- household segment where legitimately available
- acquisition channel

This is a learning metric, not inherently a KPI.

---

# 25. Friction Identified

## Metric ID

`friction_identifications`

Count of valid customer interactions where a current problem/friction is identified.

---

# 26. Root Cause Diagnosis

## Metric ID

`root_cause_diagnoses`

Count of completed diagnosis events producing at least one valid root-cause classification.

---

# 27. Root Cause Distribution

## Metric ID

`root_cause_distribution`

Distribution of diagnosed root causes.

Potential dimensions:

- room
- micro-zone
- desired function
- quest outcome

This can become strategically valuable product intelligence.

---

# 28. Assessment Start

## Metric ID

`assessment_starts`

Count of valid assessment initiations.

Define assessment type as a dimension if multiple assessment types exist.

---

# 29. Assessment Completion

## Metric ID

`assessment_completions`

Count of assessments reaching a valid completed state.

---

# 30. Assessment Completion Rate

## Metric ID

`assessment_completion_rate`

Formula:

**Assessment Completions / Assessment Starts**

---

# 31. Quest Impression

## Metric ID

`quest_impressions`

Count of valid displays of a quest recommendation or selectable quest card.

Use carefully. This is a funnel diagnostic, not a North Star.

---

# 32. Quest Start

## Metric ID

`quest_starts`

A quest begins when the user explicitly starts/accepts the activity, not merely when it is displayed.

Dimensions:

- `quest_id`
- room
- micro-zone
- duration
- player count
- quest type
- root cause
- desired function

---

# 33. Quest Completion

## Metric ID

`quest_completions`

A quest is completed when the customer explicitly completes the defined completion condition.

Do not automatically mark a quest complete solely because elapsed time passed.

---

# 34. Quest Completion Rate

## Metric ID

`quest_completion_rate`

Preferred formula:

**Completed Quests / Started Quests**

Use a sufficiently mature cohort so recent starts are not unfairly counted as failures.

For short same-session quests, same-session reporting may also be useful.

---

# 35. Quest Abandonment Rate

## Metric ID

`quest_abandonment_rate`

Formula:

**Eligible Started Quests Not Completed / Eligible Started Quests**

Define eligibility window based on quest duration and expected behavior.

---

# 36. Quest Time to Completion

## Metric ID

`quest_time_to_completion`

Elapsed time between valid quest start and completion.

Report:

- median
- p75/p90 where useful

Avoid relying only on averages.

---

# 37. Quest Duration Accuracy

## Metric ID

`quest_duration_accuracy`

Measures how closely actual completion duration aligns with estimated duration.

One possible formula:

**Completed quests within acceptable estimated-time band / completed quests with valid duration data**

Exact tolerance should be defined through product research.

---

# 38. Player Count

## Metric ID

`quest_player_count`

Number of participants assigned/participating in a quest where reliably known.

Do not infer household size from this metric.

---

# 39. Multi-Player Quest Rate

## Metric ID

`multiplayer_quest_rate`

Formula:

**Started Quests With 2+ Players / Quest Starts**

---

# 40. Micro-Zone Completion

## Metric ID

`microzone_completions`

Count of micro-zones that reach the defined completed functional standard.

This should require more than merely viewing content.

---

# 41. Room Progression

## Metric ID

`room_progression_rate`

Candidate definition:

**Users/households completing a meaningful action in a second micro-zone within the same room / users/households completing their first micro-zone**

Cohort window must be explicit.

---

# 42. Cross-Room Progression

## Metric ID

`cross_room_progression_rate`

Candidate definition:

**Eligible users/households beginning meaningful improvement in another room after completing a first-room milestone / eligible first-room completers**

This may become a major retention indicator.

---

# 43. Standard Established

## Metric ID

`standards_established`

Count of completed improvement flows where a valid post-quest standard is explicitly saved/accepted.

---

# 44. Sustainment Check

## Metric ID

`sustainment_checks`

Count of valid follow-up checks evaluating whether a completed standard remains in place.

---

# 45. Sustained Improvement Rate

## Metric ID

`sustained_improvement_rate`

Formula:

**Successful Sustainment Checks / Eligible Sustainment Checks Completed**

This is a high-value customer-outcome metric.

Do not claim sustained improvement without actual follow-up evidence.

---

# 46. Activation

## Metric ID

`activated_users`

Initial strategic definition:

A user becomes activated when they reach a meaningful first-value event.

Recommended initial activation event:

**Complete a first quest OR complete another explicitly designated equivalent first-value outcome.**

Do not define account creation alone as activation.

Final event implementation must be documented.

---

# 47. Activation Rate

## Metric ID

`activation_rate`

Formula:

**Activated Eligible Users / Eligible New Users**

Define eligible population consistently.

Segment by acquisition source where useful.

---

# 48. Time to First Value

## Metric ID

`time_to_first_value`

Elapsed time from first eligible product interaction to activation.

Prefer median.

Lower is generally better only if outcome quality remains strong.

---

# 49. Retention

Retention must always specify:

- cohort
- return window
- qualifying return action

Do not publish a generic "retention rate" without these.

---

# 50. Product Retention

## Metric ID

`product_retention_rate`

Candidate definition:

**Activated users performing another meaningful improvement action within the defined return window / activated users eligible for that window**

Potential windows:

- 7-day
- 30-day
- 90-day

---

# 51. Meaningful Return Action

A meaningful return action may include:

- new quest start
- new quest completion
- sustainment check
- another micro-zone
- another room
- inventory/replenishment action

A simple page reload should not count as product retention.

---

# 52. Product View

## Metric ID

`product_views`

Count of valid product-detail views.

Dimension:

`product_id`

---

# 53. Product Recommendation Impression

## Metric ID

`product_recommendation_impressions`

Count of times a product recommendation is meaningfully displayed.

Dimensions should include:

- product
- room
- micro-zone
- root cause
- recommendation context

---

# 54. Product Recommendation Click Rate

## Metric ID

`product_recommendation_ctr`

Formula:

**Recommendation Clicks / Recommendation Impressions**

Use unique-event/session variants where helpful.

---

# 55. Add to Cart

## Metric ID

`add_to_cart_events`

Count of valid add-to-cart actions.

Also maintain:

`users_adding_to_cart`

to avoid interpreting repeated additions as customers.

---

# 56. Add-to-Cart Rate

## Metric ID

`add_to_cart_rate`

Preferred funnel definition:

**Eligible Sessions/Users With Add-to-Cart / Eligible Product-Engaged Sessions/Users**

Do not mix user-based numerator with session-based denominator.

---

# 57. Checkout Start

## Metric ID

`checkout_starts`

Count of valid checkout initiations.

---

# 58. Purchase

## Metric ID

`purchases`

Count of successfully completed orders recognized by the authoritative commerce system.

Client-side "thank you" page events must not be the sole source of truth.

---

# 59. Purchase Conversion Rate

## Metric ID

`purchase_conversion_rate`

Default site-level formula:

**Purchasing Sessions / Eligible Sessions**

A product-funnel conversion may instead use:

**Purchasing Product-Engaged Sessions / Product-Engaged Sessions**

Always label denominator.

---

# 60. Checkout Completion Rate

## Metric ID

`checkout_completion_rate`

Formula:

**Completed Purchases / Checkout Starts**

Use reconciled order data.

---

# 61. Gross Revenue

## Metric ID

`gross_revenue`

Total recognized sales before discounts/refunds/returns/taxes/fees as defined by the commerce/accounting source.

The exact accounting treatment must be mapped in `DATA-SOURCES.md`.

Do not call this profit.

---

# 62. Discounts

## Metric ID

`discount_amount`

Total recognized discount value applied to orders.

---

# 63. Refunds

## Metric ID

`refund_amount`

Total recognized refunded amount during the reporting definition.

Be explicit whether reporting uses refund-date or original-order attribution.

---

# 64. Net Revenue

## Metric ID

`net_revenue`

Preferred business formula:

**Gross Revenue - Discounts - Refunds/Returns**

Tax/shipping treatment must be documented consistently.

---

# 65. Average Order Value

## Metric ID

`aov`

Formula:

**Order Revenue / Number of Orders**

Use the same revenue basis consistently.

Recommended executive basis:

**Net merchandise/order revenue / completed orders**

Document final implementation.

---

# 66. Units per Order

## Metric ID

`units_per_order`

Formula:

**Units Sold / Completed Orders**

Useful for physical/bundle economics.

---

# 67. Cost of Goods Sold

## Metric ID

`cogs`

Direct cost attributable to sold goods according to accounting policy.

May include:

- manufacturing
- materials
- purchased inventory

Do not include unrelated operating expenses.

---

# 68. Gross Profit

## Metric ID

`gross_profit`

Formula:

**Net Revenue - COGS**

Where fulfillment/payment costs are treated separately, keep treatment consistent.

---

# 69. Gross Margin

## Metric ID

`gross_margin`

Formula:

**Gross Profit / Net Revenue**

Express as percentage.

---

# 70. Contribution

## Metric ID

`contribution`

Recommended formula:

**Net Revenue - COGS - Variable Fulfillment Costs - Payment Processing - Variable Acquisition Cost - Other Direct Variable Costs**

Final accounting treatment must be documented.

This is more useful than revenue alone when scaling.

---

# 71. Contribution Margin

## Metric ID

`contribution_margin`

Formula:

**Contribution / Net Revenue**

---

# 72. Refund Rate

## Metric ID

`refund_rate`

Possible order-based definition:

**Refunded Orders / Eligible Completed Orders**

Also track amount-based refund rate:

**Refund Amount / Eligible Revenue**

Label which is used.

---

# 73. Repeat Purchase Rate

## Metric ID

`repeat_purchase_rate`

Formula:

**Customers With 2+ Completed Purchases / Customers With At Least 1 Completed Purchase**

Use a defined cohort/window for trend analysis.

---

# 74. Revenue per Customer

## Metric ID

`revenue_per_customer`

Formula:

**Net Revenue / Purchasing Customers**

---

# 75. Revenue per Visitor

## Metric ID

`revenue_per_visitor`

Formula:

**Net Revenue / Eligible Users**

Useful as a high-level funnel efficiency metric.

Use carefully with identity limitations.

---

# 76. Digital Product Revenue

## Metric ID

`digital_product_revenue`

Net revenue attributable to products classified as digital.

---

# 77. Physical Product Revenue

## Metric ID

`physical_product_revenue`

Net revenue attributable to physical products.

---

# 78. Service Revenue

## Metric ID

`service_revenue`

Net recognized revenue from fulfilled/recognized services according to accounting policy.

Do not count an inquiry as revenue.

---

# 79. Monthly Revenue Target Progress

## Metric ID

`monthly_revenue_target_progress`

Current strategic target:

**$20,000+ monthly revenue**

Formula:

**Month-to-Date Net Revenue / $20,000**

Display target progress as a planning indicator.

Do not imply forecast certainty from MTD pace alone.

---

# 80. Required Daily Revenue Pace

## Metric ID

`required_daily_revenue_pace`

Formula:

**Remaining Monthly Revenue Target / Remaining Selling/Calendar Days**

Specify whether calendar days or operating days are used.

This is a planning metric, not a performance judgment.

---

# 81. Revenue Gap

## Metric ID

`monthly_revenue_gap`

Formula:

**max(0, $20,000 - Month-to-Date Net Revenue)**

---

# 82. Revenue Driver Model

Use:

**Revenue ≈ Qualified Traffic × Purchase Conversion × AOV**

For more diagnostic detail:

**Revenue ≈ Traffic × Qualified Engagement Rate × Product Exposure Rate × Purchase Conversion × AOV**

This is an analytical model, not an accounting formula.

Use it to locate constraints.

---

# 83. Product Attach Rate

## Metric ID

`product_attach_rate`

For a specified base product/experience:

**Orders Including Add-On Product / Eligible Base Orders**

Always specify the base.

---

# 84. Bundle Penetration

## Metric ID

`bundle_penetration`

Formula:

**Orders Containing Bundle / Eligible Orders**

---

# 85. Inventory Sell-Through

## Metric ID

`inventory_sell_through`

For physical inventory:

**Units Sold / Units Available for Sale During Defined Period**

Implementation must account for beginning inventory and receipts appropriately.

---

# 86. Stockout Rate

## Metric ID

`stockout_rate`

Share of relevant demand periods/products where an active product is unavailable due to inventory shortage.

Exact implementation depends on commerce/inventory system.

---

# 87. Fulfillment Time

## Metric ID

`fulfillment_time`

Elapsed time from eligible paid/confirmed order to fulfillment/shipment/delivery milestone, depending product type.

Separate digital and physical fulfillment.

---

# 88. Customer Acquisition Cost

## Metric ID

`cac`

Formula:

**Eligible Acquisition Spend / New Customers Attributed to That Spend**

Do not calculate blended CAC if attribution is too unreliable without labeling it.

---

# 89. Return on Ad Spend

## Metric ID

`roas`

Formula:

**Attributed Revenue / Advertising Spend**

ROAS is not profit.

Use contribution where possible for better economics.

---

# 90. Customer Lifetime Value

## Metric ID

`ltv`

Do not publish a precise LTV until sufficient repeat-purchase/retention evidence exists.

When implemented, document:

- cohort
- horizon
- revenue vs contribution basis
- churn/retention assumptions
- discounting if used

Until then use observed cohort revenue/contribution.

---

# 91. Content Page Views

## Metric ID

`content_page_views`

Valid page views for content classified in the content catalog.

Not a primary business KPI.

---

# 92. Content Assisted Activation

## Metric ID

`content_assisted_activation_rate`

Candidate definition:

**Users exposed to specified content who later activate within attribution window / eligible users exposed to content**

Treat attribution cautiously.

---

# 93. Content Assisted Revenue

## Metric ID

`content_assisted_revenue`

Revenue associated with journeys involving specified content within a defined attribution model.

Do not claim causal impact from simple assisted attribution.

---

# 94. Internal Search Success

If site search exists:

## Metric ID

`internal_search_success_rate`

Candidate definition:

**Search sessions resulting in a meaningful downstream action / valid internal search sessions**

Also track zero-result searches.

---

# 95. Zero-Result Search Rate

## Metric ID

`zero_result_search_rate`

Formula:

**Internal Searches Returning No Useful Result / Valid Internal Searches**

This can reveal content/product gaps.

---

# 96. Experiment Exposure

## Metric ID

`experiment_exposures`

Distinct eligible users/sessions assigned to an experiment variant.

Do not count internal/test traffic.

---

# 97. Experiment Primary Metric Lift

## Metric ID

`experiment_primary_metric_lift`

Formula:

**(Variant Metric - Control Metric) / Control Metric**

Report:

- absolute values
- relative lift
- sample size
- confidence/statistical method where appropriate

Do not report lift without context.

---

# 98. Experiment Guardrail Breach

## Metric ID

`experiment_guardrail_breach`

Boolean or count indicating whether a predefined guardrail crossed its stop threshold.

Examples:

- refund rate
- error rate
- checkout failure
- unsubscribe rate
- customer complaint rate

---

# 99. Experiment Win Rate

## Metric ID

`experiment_win_rate`

Formula:

**Experiments Adopted Due to Positive Evidence / Concluded Experiments**

This is an organizational-learning metric, not a goal to maximize.

A low win rate can be healthy.

---

# 100. Deployment Frequency

## Metric ID

`deployment_frequency`

Number of meaningful production deployments in the selected period.

Not a vanity target.

---

# 101. Deployment Success Rate

## Metric ID

`deployment_success_rate`

Formula:

**Successful Production Deployments / Production Deployment Attempts**

Define success window so immediate rollback/hotfix is handled consistently.

---

# 102. Change Failure Rate

## Metric ID

`change_failure_rate`

Formula:

**Production Changes Causing Material Incident, Rollback, or Emergency Fix / Production Changes**

Use consistent severity criteria.

---

# 103. Mean Time to Restore

## Metric ID

`mttr`

Average or median elapsed time from qualifying service-impacting incident start/detection to meaningful service restoration.

Prefer median alongside average.

---

# 104. Site Availability

## Metric ID

`site_availability`

Formula:

**Successful Eligible Availability Checks / Total Eligible Availability Checks**

Define:

- endpoint/journey
- check frequency
- planned maintenance treatment

---

# 105. Critical Journey Availability

## Metric ID

`critical_journey_availability`

Availability of defined end-to-end journeys such as:

- website
- quest
- checkout
- purchased-content access

This may be more meaningful than server uptime.

---

# 106. Server Error Rate

## Metric ID

`server_error_rate`

Formula:

**Eligible 5xx Requests / Eligible Requests**

Exclude monitoring endpoints if they distort customer traffic, but document exclusions.

---

# 107. Application Error Rate

## Metric ID

`application_error_rate`

Count/rate of meaningful application failures according to observability rules.

Do not count every harmless console warning.

---

# 108. Latency

Metric IDs may include:

`page_p75_latency`
`api_p95_latency`

Use percentiles.

Define endpoint/page scope.

---

# 109. Container Health

## Metric ID

`unhealthy_container_count`

Count of production containers currently in unhealthy/failed state.

Also track restart trends where useful.

---

# 110. Container Restart Rate

## Metric ID

`container_restart_rate`

Count of unexpected production container restarts over the selected period, segmented by service.

---

# 111. CPU Utilization

## Metric ID

`host_cpu_utilization`

Host CPU utilization from the authoritative runtime monitoring source.

Use sustained trend/percentiles rather than reacting to every spike.

---

# 112. Memory Utilization

## Metric ID

`host_memory_utilization`

Host memory utilization.

Also monitor:

- swap
- OOM events
- container memory pressure

---

# 113. Disk Utilization

## Metric ID

`host_disk_utilization`

Used disk / usable disk.

Track trend and predicted exhaustion where possible.

Disk risk should consider:

- logs
- Docker images
- database growth
- backups
- volumes

---

# 114. Backup Freshness

## Metric ID

`backup_age_hours`

Hours since the latest verified successful required production backup.

"Backup job ran" is insufficient if backup validity cannot be established.

---

# 115. Restore Validation Age

## Metric ID

`restore_validation_age_days`

Days since the latest successful representative restore test.

This is a major recoverability metric.

---

# 116. Incident Count

## Metric ID

`incident_count`

Count of qualifying incidents by severity.

Dimensions:

- P0
- P1
- P2
- P3

Do not inflate severity to make operations appear active.

---

# 117. Open Reliability Risks

## Metric ID

`open_high_reliability_risks`

Count of unresolved HIGH/CRITICAL reliability risks.

Useful executive indicator.

---

# 118. Security Findings

Potential metric IDs:

`open_critical_security_findings`
`open_high_security_findings`

Count unresolved findings from the authoritative security process.

Do not expose vulnerability details on public dashboards.

---

# 119. Vulnerability Remediation Time

## Metric ID

`security_remediation_time`

Elapsed time from confirmed qualifying security finding to remediation.

Segment by severity.

---

# 120. Backup Coverage

## Metric ID

`backup_coverage_rate`

Formula:

**Required Persistent Data Assets With Verified Backup / Required Persistent Data Assets**

This requires an inventory of required persistent assets.

---

# 121. Autonomous Work Completed

## Metric ID

`autonomous_major_changes_completed`

Count of meaningful autonomous changes completed and verified.

Do not count trivial commits.

This is transparency data, not a productivity target.

---

# 122. Autonomous Change Success Rate

## Metric ID

`autonomous_change_success_rate`

Candidate formula:

**Autonomous Changes Achieving Intended Technical/Product Outcome Without Material Regression / Eligible Autonomous Changes**

Use cautiously until outcome classification is reliable.

---

# 123. Human Escalations

## Metric ID

`human_escalations`

Count of material owner decisions requested.

Dimensions:

- RED approval
- strategy
- financial
- legal
- ownership/access
- unresolved ambiguity

The goal is not zero.

The goal is appropriate escalation.

---

# 124. RED Approval Queue

## Metric ID

`pending_red_approvals`

Count of unresolved actions requiring explicit human authorization under `AUTONOMY.md`.

Executive dashboard should show this clearly.

---

# 125. Work in Progress

## Metric ID

`major_active_workstreams`

Count of major active workstreams.

Default guardrail:

**≤ 3**

Do not game the metric by relabeling major work as minor.

---

# 126. Backlog Aging

## Metric ID

`backlog_item_age`

Elapsed time since a backlog item entered its current meaningful priority/state.

Useful for identifying blocked high-value work.

---

# 127. Decision Aging

## Metric ID

`pending_decision_age`

Elapsed time for unresolved decisions that block material work.

---

# 128. Data Freshness

## Metric ID

`data_freshness`

For each source/metric:

**Current Time - Latest Successful Data Update Time**

Dashboard should surface stale critical data.

---

# 129. Data Quality

Potential dimensions:

- completeness
- timeliness
- validity
- uniqueness
- reconciliation

Do not compress data quality into a single score unless the calculation is useful and transparent.

---

# 130. North Star Candidate

The business should not prematurely lock into a North Star before product behavior is observed.

A strong candidate is:

## `sustained_microzone_improvements`

**Number of micro-zone improvements that reach a defined standard and later pass a sustainment check.**

Why it is promising:

It measures real household improvement rather than traffic or clicks.

Limitations:

- requires follow-up
- slower feedback loop
- instrumentation must be trustworthy

Use faster leading indicators operationally.

---

# 131. Leading Product Indicators

Potential leading indicators:

- desired-function completion
- root-cause diagnosis
- quest start
- quest completion
- standard established
- next micro-zone progression

These can predict customer value faster than sustainment.

---

# 132. Executive KPI Set

The executive dashboard should remain compact.

Recommended top-line metrics:

## Business
- MTD Net Revenue
- Revenue Target Progress
- Orders
- AOV
- Contribution / Contribution Margin when available

## Acquisition
- Users
- Organic Sessions
- Search Clicks
- Qualified Landing Sessions

## Product
- Activation Rate
- Quest Starts
- Quest Completion Rate
- Micro-Zone Completions
- Cross-Room Progression when mature

## Commerce
- Purchase Conversion Rate
- Checkout Completion Rate
- Repeat Purchase Rate

## Customer Outcome
- Sustained Improvement Rate when available

## Reliability
- Production Status
- Critical Journey Availability
- Error Rate
- Backup Freshness
- Restore Validation Age

## Autonomy
- Active Workstreams
- Active Experiments
- Pending RED Approvals
- Material Risks

Do not put every metric in the executive view.

---

# 133. Funnel

Initial customer funnel:

**Visitor**
→ **Qualified Engagement**
→ **Desired Function / Assessment**
→ **Quest Start**
→ **Quest Completion**
→ **Product Engagement**
→ **Checkout**
→ **Purchase**
→ **Repeat Improvement**
→ **Repeat Purchase / Retention**

Measure drop-off at each stage.

Not every customer must follow exactly this path.

---

# 134. Funnel Conversion Definitions

Each funnel conversion must use compatible populations.

Example:

`quest_start_rate_from_assessment`

**Users Starting Quest After Assessment / Users Completing Assessment**

Do not divide event counts by users unless intentionally defined.

---

# 135. Cohort Rules

Use cohorts for:

- retention
- repeat purchase
- sustainment
- progression
- LTV

Cohort definitions must specify:

- entry event
- entry date/window
- eligibility
- observation window

Recent cohorts should not be compared to mature cohorts without adjustment.

---

# 136. Internal / Test Traffic

Exclude where practical:

- development environments
- automated tests
- uptime monitors
- bots
- internal administrative activity
- known staff testing

Document exclusions.

Do not hide real customer failures as "test traffic."

---

# 137. Bot Traffic

Use the analytics/search platform's bot controls plus documented filters where appropriate.

Do not claim exact human traffic when bot filtering is uncertain.

---

# 138. Revenue Reconciliation

Commerce events and analytics purchase events may differ.

Authoritative financial revenue should come from the commerce/payment/accounting source defined in `DATA-SOURCES.md`.

Analytics purchase events are primarily behavioral instrumentation.

Reconcile discrepancies.

---

# 139. Search Reconciliation

Search Console clicks and analytics organic sessions are different concepts.

Do not expect exact equality.

Use each for its intended purpose.

---

# 140. Event Versioning

When event definitions change:

- version event/schema if materially different
- record effective date
- preserve historical interpretation
- update `DATA-CONTRACTS.md`
- update this file if metric meaning changes

Do not silently redefine historical metrics.

---

# 141. Metric Ownership

Recommended ownership:

`analytics-intelligence`
→ metric governance and calculation

`seo-aeo`
→ search interpretation

`commerce-manager`
→ commerce economics

`product-manager`
→ product outcome interpretation

`devops-sre`
→ reliability metrics

`security-auditor`
→ security metrics

`6s-ceo`
→ executive KPI selection

Owners do not get to redefine canonical formulas silently.

---

# 142. Metric Change Process

For material metric changes:

1. identify current definition
2. identify problem
3. propose new definition
4. assess historical comparability
5. update implementation
6. validate
7. document effective date
8. update `DECISIONS.md` if strategically material

---

# 143. Metric Guardrails

Never improve a metric by:

- auto-completing quests
- suppressing errors
- removing meaningful tests
- blocking refunds
- hiding unsubscribe
- forcing cart additions
- manipulating attribution
- excluding legitimate failures
- misclassifying revenue
- inflating user counts

This is goal hacking.

---

# 144. Constraint Metric

Each weekly review should identify the metric currently acting as the primary business constraint.

Examples:

- qualified traffic
- activation
- quest completion
- product engagement
- checkout completion
- AOV
- repeat purchase
- contribution
- reliability

The constraint should drive backlog priority.

---

# 145. $20K Monthly Revenue Diagnostic

When monthly revenue is below target, diagnose in order:

1. Is data trustworthy?
2. Is qualified traffic sufficient?
3. Are visitors activating?
4. Are users completing quests?
5. Are relevant products being seen?
6. Is purchase conversion healthy?
7. Is AOV sufficient?
8. Is repeat purchase developing?
9. Are margins healthy?
10. Is reliability hurting the funnel?

Do not automatically conclude "we need more traffic."

---

# 146. Example Revenue Scenario Analysis

Scenario analysis may calculate:

**Required Orders = Revenue Target / Expected AOV**

Examples:

At $25 AOV:

**$20,000 / $25 = 800 orders**

At $50 AOV:

**$20,000 / $50 = 400 orders**

At $100 AOV:

**$20,000 / $100 = 200 orders**

At $200 AOV:

**$20,000 / $200 = 100 orders**

These are mathematical scenarios, not forecasts.

Use actual conversion and traffic to evaluate feasibility.

---

# 147. Dashboard Status Thresholds

Thresholds should eventually be evidence-based.

Until calibrated:

Do not create arbitrary red/green thresholds for business metrics.

For technical/safety metrics, reasonable operational thresholds may be established by the owning specialist and documented.

Dashboard should distinguish:

- target
- warning threshold
- critical threshold

---

# 148. Metric Freshness Requirements

Suggested categories:

## Near Real Time

Useful for:

- production health
- critical errors
- checkout failures
- incidents

## Hourly

Useful for:

- operational traffic
- orders
- deployment effects

## Daily

Useful for:

- revenue trends
- search performance
- product funnels
- experiment summaries

## Weekly / Monthly

Useful for:

- retention
- cohorts
- strategy
- economics

Do not force every metric into real-time infrastructure.

---

# 149. Executive Interpretation

A metric without interpretation is incomplete.

Executive reporting should explain:

- what changed
- why it likely changed
- confidence
- business impact
- recommended action

Do not generate causal explanations without evidence.

Use language such as:

- "correlated with"
- "likely contributor"
- "hypothesis"
- "confirmed by experiment"

appropriately.

---

# 150. Required Next Step

After this file is adopted, create `DATA-SOURCES.md`.

For every executive and operational KPI, identify:

- authoritative system
- table/API/report
- refresh cadence
- access method
- data owner
- known limitations
- reconciliation logic

Until a source is verified, current value remains:

**UNKNOWN**

---

# Final Measurement Principle

6S Success should never confuse:

**traffic with value**

**engagement with improvement**

**revenue with profit**

**deployment with success**

**activity with progress**

The strongest measurement system connects:

**Customer Need**
→ **Action**
→ **Functional Improvement**
→ **Sustainment**
→ **Commercial Value**
→ **Learning**

Measure what helps the autonomous organization make better decisions.

---

# Corporate Lean 6S funnel, added 2026-09-03

The corporate page is the only surface aimed at a buyer with a budget, and at
1.7 visitors a day it cannot be A/B tested (the experiment registry computes
1,427 days to significance). So it is instrumented instead: two events, both
emitted by `site/assets/js/measure.js` into Umami, both with a stated meaning
here so nobody has to guess later what a count means.

## corporate-enquiry

**Emitted by** the submit handler on `/corporate.html`, generated by
`ops/build_corporate.py`.

**Definition.** A visitor completed the enquiry form and the page composed a
message for their mail app. It is **not** a lead. Nothing on this site can
observe whether they pressed send in their own mail client, and pretending
otherwise would make this number a lie the first time somebody abandoned at
that step.

**Dimensions.**

- `timed` — 1 if the visitor named a date and time for a scoping call, 0 if
  not. The difference between a reply that can carry a calendar invite through
  `ops/service_orders.py` and one that has to ask.
- `sv` — schema version, currently 1.

**Nothing identifying is sent.** Not the company, not the name, not the email,
not the free text. Those go only into the visitor's own mail client. CLAUDE.md
section 47.

**Reconciliation.** The real denominator for conversion is the count of
enquiries that actually arrive in the support@ inbox, which
`ops/service_orders.py` forwards and records in
`ops/state-service-orders.json`. `corporate-enquiry` minus arrivals is the
mailto's own drop-off, which is currently unmeasured anywhere else and is the
main reason to keep both numbers.

**Confidence.** MEDIUM as an intent signal, LOW as a lead count. Do not report
it as leads.

## quote-click, extended

**Existing event**, previously fired only on links of the form
`contact.html?ref=SKU`. It now also fires on any link to `/corporate.html`,
carrying the `data-sku` the product card rendered, so click-through to the
highest value offer in the catalogue stays inside the same funnel rather than
disappearing when the destination changed.

**Watch for.** `quote-click` with `sku: CN-CORP` and `from: shop`, against
`/corporate.html` pageviews, against `corporate-enquiry`. Those three in order
are the whole funnel for this line.

**Baseline at the time of writing: zero of all three.** The page did not exist
before 2026-09-03, so any number is new information.
