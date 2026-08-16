# 6S Success Data Sources

> Authoritative source registry, freshness rules, reconciliation hierarchy, and data-access contract for autonomous 6S Success operations.

## 1. Purpose

`DATA-SOURCES.md` defines **where Claude and its specialist agents obtain operational and business truth**.

It prevents the autonomous system from:

- guessing metrics
- trusting stale Markdown over live systems
- mixing analytics events with financial truth
- treating GitHub as proof of what is deployed
- treating Docker state as proof of source-code state
- inventing revenue, traffic, SEO, product, or reliability numbers
- silently choosing between conflicting sources

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`

`METRICS.md` defines **what a metric means**.

This file defines **where the metric comes from**.

---

# 2. Core Rule

**No verified source = UNKNOWN.**

Never manufacture a current value from:

- memory
- previous reports
- screenshots
- estimates
- stale Markdown
- code comments
- assumptions
- synthetic test data

unless the output is explicitly labeled as an estimate, scenario, or test.

---

# 3. Truth Hierarchy

When sources conflict, prefer the source closest to the actual event being measured.

General hierarchy:

**Authoritative Transaction/System of Record**
→ **Authoritative Operational Telemetry**
→ **Validated Analytics**
→ **Derived Warehouse/Reporting Layer**
→ **Repository Configuration**
→ **Operational Documentation**
→ **Manual Report**
→ **Historical Narrative**
→ **Assumption**

This hierarchy is contextual.

Example:

GitHub may be authoritative for source history but not for the currently running production image.

---

# 4. Source Status

Every source must have one of:

- `VERIFIED`
- `PARTIALLY_VERIFIED`
- `UNVERIFIED`
- `DISCONNECTED`
- `DEPRECATED`

Do not treat `UNVERIFIED` as unavailable.

Verify it.

---

# 5. Source Registry

Maintain this table as integrations are discovered.

| Domain | Source | Status | Authority | Expected Freshness | Owner |
|---|---|---|---|---|---|
| Website | Production HTTP endpoints | UNVERIFIED | Runtime customer availability | Near real time | devops-sre |
| Source code | GitHub repository | UNVERIFIED | Code/version history | Near real time | github-manager |
| CI/CD | GitHub Actions or discovered CI | UNVERIFIED | Build/deployment execution | Near real time | github-manager |
| Runtime | Hostinger VPS | UNVERIFIED | Host/runtime state | Near real time | vps-docker-manager |
| Containers | Docker Engine / Compose | UNVERIFIED | Running container state | Near real time | vps-docker-manager |
| Application | Application logs/APM | UNVERIFIED | Runtime behavior | Near real time | devops-sre |
| Database | Production database | UNVERIFIED | Product transactional state | Near real time | data/application owner |
| Commerce | Commerce platform | UNVERIFIED | Orders/catalog where applicable | Hourly or better | commerce-manager |
| Payments | Payment processor | UNVERIFIED | Payment/refund transactions | Hourly or better | commerce-manager |
| Web analytics | Analytics platform | UNVERIFIED | Behavioral analytics | Daily or better | analytics-intelligence |
| Search | Google Search Console | UNVERIFIED | Google search performance | Daily/platform latency | seo-aeo |
| SEO crawl | Technical crawl/inspection | UNVERIFIED | Crawl observations | On demand | seo-aeo |
| Product events | Product analytics/event store | UNVERIFIED | Product behavior | Hourly or better | analytics-intelligence |
| Experiments | Experiment registry/data | UNVERIFIED | Test assignment/results | Daily or better | cro-growth |
| Email | Email platform | UNVERIFIED | Delivery/campaign behavior | Daily or better | lifecycle owner |
| Inventory | Commerce/inventory system | UNVERIFIED | Physical inventory | Hourly/daily | commerce-manager |
| Backups | Backup system/storage | UNVERIFIED | Backup existence/status | Daily | vps-docker-manager |
| Monitoring | Uptime/observability platform | UNVERIFIED | Reliability telemetry | Near real time | devops-sre |
| Security | Security/dependency tooling | UNVERIFIED | Security findings | Daily/on event | security-auditor |

Replace generic source names with actual systems after discovery.

---

# 6. Discovery Before Integration

Before building new data infrastructure:

1. inspect the repository
2. inspect environment/configuration without exposing secrets
3. inspect existing Docker services
4. identify current analytics
5. identify commerce/payment systems
6. identify databases
7. identify monitoring
8. identify Search Console integration
9. identify existing dashboards
10. identify scheduled jobs

Prefer reusing a healthy existing system over duplicating it.

---

# 7. Credentials

Credentials must never be stored in this file.

Store only:

- secret name
- integration purpose
- location/mechanism
- owning system

Example:

`STRIPE_SECRET_KEY`
→ payment API credential
→ production secret environment
→ commerce integration

Never write the secret value into Markdown, Git, logs, dashboards, or agent output.

---

# 8. Production Website

## Source

Actual public production endpoints for `6S-success.com`.

## Authority

Customer-visible availability and behavior.

## Use For

- HTTP availability
- redirect behavior
- TLS
- public rendering
- critical journey verification

## Do Not Use For

- authoritative revenue
- database integrity
- deployed Git commit unless exposed through a verified build identifier

## Freshness

Near real time / on demand.

---

# 9. GitHub

## Owner

`github-manager`

## Authority

GitHub is authoritative for:

- repository history
- commits
- branches
- pull requests
- tags
- releases
- workflow definitions
- GitHub Actions execution
- repository security settings where accessible

## GitHub Is Not Automatically Authoritative For

- what code is actually running
- what environment variables are active
- production database state
- Hostinger host configuration
- manually modified production files

Production identity must be reconciled.

---

# 10. Production Release Identity

Target mapping:

**Git Commit SHA**
→ **Build**
→ **Artifact / Docker Image**
→ **Deployment**
→ **Running Container**
→ **Production Verification**

Store enough metadata to answer:

**Exactly what code is running right now?**

Recommended metadata:

- commit SHA
- release/tag
- build ID
- image digest
- deployment timestamp
- environment
- runtime service

Avoid relying only on mutable Docker tags such as `latest`.

---

# 11. Hostinger VPS

## Owner

`vps-docker-manager`

## Authority

Hostinger VPS is authoritative for host-level runtime state such as:

- operating system
- CPU
- memory
- disk
- processes
- network listeners
- Docker daemon state
- mounted storage
- host-level configuration

## Freshness

Near real time.

## Safety

Initial discovery should be read-only.

Do not alter unknown host resources merely to simplify inventory.

---

# 12. Docker Engine

## Authority

Docker runtime is authoritative for:

- running containers
- stopped containers
- images present
- image IDs/digests
- networks
- volumes
- container health
- restart state
- mounts
- runtime configuration

Docker does not establish business correctness.

---

# 13. Docker Compose

Compose configuration is authoritative for **intended declared service configuration** only when verified as the active deployment mechanism.

Compare:

**Compose declaration**
vs
**Docker runtime**
vs
**GitHub version**

Drift should be surfaced.

---

# 14. Persistent Volumes

Maintain an inventory:

| Volume | Service | Data Type | Required? | Backup? | Restore Tested? |
|---|---|---|---|---|---|
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

Rule:

**Unknown volume = preserve.**

Never delete a volume because it appears unused until ownership and recoverability are verified.

---

# 15. Production Database

After discovery, document:

- engine
- logical database name
- owning service
- connection mechanism
- schema/version mechanism
- backup source
- replication if any
- recovery method

Do not record credentials.

## Authority

Production database is normally authoritative for product transactional state that it owns.

Examples may include:

- users
- quests
- saved standards
- inventory
- entitlements

Actual schema must be inspected before assumptions are made.

---

# 16. Database vs Analytics

Database records answer:

**What transactional state exists?**

Analytics answers:

**What behavior was observed?**

Example:

Database:
`quest status = completed`

Analytics:
`quest_complete event fired`

If they disagree, investigate instrumentation.

Do not silently overwrite one with the other.

---

# 17. Commerce Platform

After discovery, record actual provider.

Possible responsibilities:

- product catalog
- prices
- orders
- discounts
- refunds
- fulfillment
- inventory

## Authority

If the commerce platform owns orders, it is authoritative for order state.

Do not use browser analytics as authoritative order count.

---

# 18. Payment Processor

After discovery, record actual provider.

## Authority

Payment processor is authoritative for:

- payment attempts
- successful charges
- payment failures
- refunds processed by it
- disputes
- processing fees where exposed

Commerce order state and payment state can differ.

Reconcile them.

---

# 19. Financial Revenue Source

Recommended hierarchy:

**Commerce/accounting recognized order data**
+
**payment/refund reconciliation**

The final source depends on architecture.

Until established:

`gross_revenue = UNKNOWN`
`net_revenue = UNKNOWN`
`refund_amount = UNKNOWN`

Do not calculate executive revenue from client-side analytics events.

---

# 20. Product Catalog Source

`PRODUCT-CATALOG.md` may document business intent and state.

The live commerce/application catalog should be authoritative for what customers can actually purchase.

Reconcile:

**Business Catalog**
↔ **Application Catalog**
↔ **Commerce Catalog**
↔ **Website Presentation**

Surface mismatches.

---

# 21. Pricing Source

There must be one authoritative live pricing source.

After discovery, document it.

Do not allow:

- hard-coded page price
- commerce price
- checkout price
- structured-data price

to diverge silently.

Pricing tests must follow `AUTONOMY.md`.

---

# 22. Web Analytics

After discovery, record platform and property/site identifiers without secrets.

## Authority

Use for:

- users
- sessions
- channel attribution
- landing pages
- behavioral funnels where instrumented

## Limitations

Analytics may be affected by:

- consent
- blockers
- cookies
- identity limitations
- bots
- implementation bugs

Treat financial transaction systems as authoritative for revenue.

---

# 23. Search Console

## Owner

`seo-aeo`

## Authority

Google Search Console is authoritative for Google-reported:

- search clicks
- search impressions
- CTR
- average position
- query/page performance
- coverage/index observations available through the platform

## Freshness

Use platform-provided data with its normal reporting delay.

Do not call it real time.

---

# 24. Search Console vs Analytics

These will not exactly match.

Search Console measures search-result interaction.

Analytics measures observed site behavior.

Do not force equality.

Use Search Console for search performance.

Use analytics for on-site behavior.

---

# 25. Indexing

Use search-engine inspection/search-console evidence for indexing state.

A page existing in:

- sitemap
- Git
- database
- website

does not prove it is indexed.

---

# 26. SEO Crawl Data

Technical crawl tools may be authoritative for observed crawl properties at crawl time:

- status codes
- canonicals
- titles
- descriptions
- internal links
- structured data presence
- crawl depth

They are not authoritative for search rankings or traffic.

---

# 27. AEO Measurement

AEO is less standardized.

Do not invent a universal "AEO score."

Possible evidence:

- answer-engine referral traffic
- cited/linked appearances where reliably measured
- crawler access
- structured content coverage
- direct-answer content quality

Clearly distinguish observed data from heuristic audits.

---

# 28. Product Analytics

Product analytics should capture structured events for:

- room
- micro-zone
- desired function
- friction
- root cause
- assessment
- quest
- standard
- sustainment
- recommendation
- commerce handoff

Canonical event contracts should live in `DATA-CONTRACTS.md`.

---

# 29. Event Source of Truth

For each event define:

- event name
- trigger
- required properties
- optional properties
- identity
- timestamp
- environment
- version

Do not infer event semantics from the name alone.

---

# 30. Server-Side vs Client-Side Events

Prefer server-side confirmation for important transactional outcomes where feasible.

Examples:

- purchase
- entitlement
- quest persistence
- fulfillment

Client-side events remain valuable for behavioral interactions.

---

# 31. Experiment Registry

All active experiments should be registered in `EXPERIMENTS.md` or an integrated experiment system.

Source must identify:

- experiment ID
- hypothesis
- variants
- start/end
- population
- primary metric
- guardrails
- status
- decision

Do not analyze an experiment without knowing assignment logic.

---

# 32. Experiment Data

Experiment results should use the canonical metrics in `METRICS.md`.

Avoid:

- changing primary metric after results appear
- excluding unfavorable users without documented reason
- stopping solely when significance appears
- declaring causality from non-random before/after comparisons

---

# 33. Content Catalog

`CONTENT-CATALOG.md` should document intended/known content inventory.

The live site/CMS/application is authoritative for actual published availability.

Reconcile the catalog periodically.

---

# 34. Content Performance

Use:

**Analytics**
→ on-site behavior

**Search Console**
→ search discovery

**Commerce/Product Events**
→ downstream outcomes

Do not rank content solely by page views.

---

# 35. Social Media

If connected later, record each platform separately.

Potential uses:

- post reach
- clicks
- engagement
- referrals

Do not combine platform-native engagement into a fake universal engagement metric without definition.

---

# 36. Email Platform

If email is implemented, document provider.

Authority may include:

- sends
- delivery
- bounce
- unsubscribe
- campaign clicks

Open rates can be distorted by privacy technology.

Treat cautiously.

---

# 37. Customer Support

If support tooling exists, document source.

Potential learning data:

- issue categories
- product confusion
- refund reasons
- fulfillment problems
- repeated root causes

Protect customer privacy.

---

# 38. Services Data

If home services are offered, define the system of record for:

- lead
- quote
- booking
- appointment
- completion
- payment
- service area
- service outcome

Do not treat inquiry volume as completed service revenue.

---

# 39. Physical Inventory

If physical products exist, identify authoritative inventory source.

Track:

- SKU
- available
- reserved
- incoming
- damaged
- reorder point

Do not allow website availability to drift from inventory truth.

---

# 40. 3D Printing Production

If 3D products become active, establish source for:

- design version
- material
- print profile
- production quantity
- failed prints
- finished inventory
- fulfillment cost

Git may be authoritative for design files, but not physical inventory.

---

# 41. Backups

## Owner

`vps-docker-manager`

Document actual backup system after discovery.

For every required persistent asset capture:

- source asset
- backup mechanism
- destination class
- schedule
- retention
- encryption
- latest successful backup
- verification method
- restore procedure

A backup is not trustworthy solely because a scheduled job exists.

---

# 42. Backup Verification

Evidence levels:

## Level 0

Backup assumed.

## Level 1

Job exists.

## Level 2

Job reports success.

## Level 3

Backup artifact exists and is readable.

## Level 4

Representative restore succeeds.

Target critical data toward Level 4.

---

# 43. Monitoring

After discovery, document:

- uptime source
- application monitoring
- host monitoring
- log monitoring
- alerting
- synthetic journeys

Do not build duplicate monitoring before evaluating current tooling.

---

# 44. Uptime

Authoritative uptime should come from an external or appropriately independent monitor where possible.

An application reporting itself healthy is useful but insufficient by itself.

---

# 45. Critical Journey Monitoring

Priority journeys:

1. public site
2. desired-function/assessment experience
3. quest experience
4. checkout
5. purchased content/entitlement where applicable

Synthetic checks should not create production business data.

Use test markers/accounts.

---

# 46. Logs

Logs are diagnostic evidence.

They may include:

- web server
- reverse proxy
- application
- database
- Docker
- operating system

Do not expose:

- passwords
- tokens
- payment data
- private household images
- sensitive customer information

Sanitize before summarizing.

---

# 47. Security Sources

Potential authoritative sources:

- GitHub security alerts
- dependency scanning
- container scanning
- host security tooling
- application security testing
- access logs

Record actual tooling after discovery.

Security findings should be verified before executive classification where practical.

---

# 48. GitHub Security

Use GitHub-native security data where enabled for:

- dependency alerts
- secret scanning
- code scanning

Absence of an alert does not prove absence of vulnerability.

---

# 49. Host Security

Runtime evidence may include:

- package state
- SSH configuration
- firewall
- open ports
- Docker exposure
- failed login activity

Changes must follow `AUTONOMY.md`.

---

# 50. DNS

Identify authoritative DNS provider.

Document:

- provider
- zones
- key records
- ownership
- TTL strategy where relevant

Do not record account credentials.

DNS changes can have broad impact and should be classified appropriately.

---

# 51. Domain

Document registrar and ownership after discovery.

Domain transfer, ownership, or nameserver changes are high-impact actions.

Follow `AUTONOMY.md`.

---

# 52. TLS

Source:

Actual public certificate inspection plus active reverse-proxy/certificate configuration.

Track:

- issuer
- domains
- expiration
- renewal method

Do not assume automated renewal works merely because it is configured.

---

# 53. CDN / Proxy

If a CDN or external proxy exists, document:

- provider
- role
- caching
- DNS relationship
- security features

This may affect traffic, logs, TLS, and origin behavior.

---

# 54. Environment Registry

Maintain environments:

- local
- development
- test
- staging if present
- production

For each:

- URL
- branch/release relationship
- database class
- payment mode
- analytics mode

Never allow test events to pollute production metrics where avoidable.

---

# 55. Environment Variables

Maintain a **name-only** registry for important variables.

Example:

| Variable | Purpose | Environment | Secret? |
|---|---|---|---|
| `DATABASE_URL` | Database connection | Production | YES |
| `APP_ENV` | Runtime environment | Production | NO |

Never record secret values.

---

# 56. Scheduled Jobs

Inventory all recurring jobs:

- backups
- sitemap generation
- content tasks
- analytics aggregation
- cleanup
- email
- inventory
- monitoring

Document:

- schedule
- owner
- effect
- failure behavior
- observability

Avoid duplicate jobs.

---

# 57. Autonomous Agent Activity

Claude's actions should be traceable through appropriate sources:

- Git commits
- PRs
- issues/backlog
- deployment records
- decision log
- experiment registry
- status updates

Do not create a separate complex agent telemetry system unless useful.

---

# 58. Executive Dashboard Source Rule

Every dashboard tile must link logically to:

**Metric Definition**
→ **Source**
→ **Last Refresh**
→ **Confidence**

A number without source/freshness should not be presented as executive truth.

---

# 59. Dashboard Caching

Near-real-time does not mean every dashboard request must query every upstream system.

Use caching/materialization when appropriate.

Display:

**Last updated: [timestamp]**

for important cached data.

---

# 60. Derived Metrics

Derived metrics must identify dependencies.

Example:

`purchase_conversion_rate`

depends on:

- eligible purchasing sessions
- eligible sessions

If one dependency is stale or low-confidence, derived metric confidence cannot exceed the weakest critical input.

---

# 61. Reconciliation Status

Use:

- `MATCHED`
- `WITHIN_TOLERANCE`
- `MISMATCH`
- `NOT_COMPARABLE`
- `NOT_CHECKED`

Do not force sources with different definitions to match.

---

# 62. Revenue Reconciliation

Compare where applicable:

**Commerce Orders**
↔ **Payment Transactions**
↔ **Analytics Purchase Events**

Interpretation:

Commerce/payment discrepancy may indicate operational/financial issue.

Analytics discrepancy may indicate instrumentation issue.

Financial truth should not be overwritten by analytics.

---

# 63. Deployment Reconciliation

Compare:

**GitHub intended release**
↔ **built image digest**
↔ **running image digest**
↔ **production build identifier**

Any unexplained mismatch should be surfaced.

---

# 64. Catalog Reconciliation

Compare:

**PRODUCT-CATALOG.md**
↔ **commerce catalog**
↔ **website**
↔ **checkout**

Check:

- state
- title
- price
- availability
- SKU/product ID

---

# 65. Content Reconciliation

Compare:

**CONTENT-CATALOG.md**
↔ **routes/CMS**
↔ **sitemap**
↔ **live HTTP**
↔ **search index evidence**

Do not assume these layers are identical.

---

# 66. Data Freshness Classes

## F0 — Immediate

Seconds/minutes.

Examples:

- production incident
- critical checkout outage

## F1 — Near Real Time

Minutes.

Examples:

- uptime
- container health
- host capacity

## F2 — Hourly

Examples:

- orders
- revenue operational view
- product event aggregates

## F3 — Daily

Examples:

- SEO
- most funnel reporting
- content performance

## F4 — Weekly/Monthly

Examples:

- cohorts
- strategy
- mature retention
- unit economics reviews

---

# 67. Stale Data

A metric is stale when its age exceeds the expected freshness class.

When stale:

- label it
- reduce confidence
- do not silently present it as current
- investigate failed collection if critical

---

# 68. Missing Data

When data is missing:

1. identify whether source failed
2. identify whether event never occurred
3. distinguish zero from null
4. do not replace missing with zero without justification

`0 orders` and `order data unavailable` are not the same.

---

# 69. Time Zone

Choose and document a canonical business reporting timezone.

Until explicitly configured, agents must inspect current systems before assuming timezone behavior.

Store timestamps in UTC where practical.

Display business reporting in the configured business timezone.

---

# 70. Currency

Primary commercial reporting currency should be explicitly configured.

Do not assume all future transactions are USD if international commerce is introduced.

Record:

- transaction currency
- converted reporting currency if applicable
- conversion source/date

---

# 71. Personally Identifiable Data

Executive analytics should minimize direct PII.

Prefer:

- aggregate
- pseudonymous IDs
- household/user IDs where necessary

Do not place:

- full customer records
- private photos
- addresses
- payment details

in operational Markdown.

---

# 72. Household Images

If image assessment exists:

- identify storage source
- access control
- retention policy
- deletion process
- model-processing path
- consent requirements

Do not expose private household images in dashboards or logs.

---

# 73. Data Retention

Each source should eventually document retention requirements.

Retention should balance:

- business learning
- legal obligations
- customer privacy
- operational recovery
- cost

Do not retain sensitive data indefinitely without purpose.

---

# 74. Data Deletion

Customer deletion workflows must identify all applicable systems.

Do not claim deletion is complete unless downstream copies are handled according to policy.

Backups may require separate retention handling.

---

# 75. Data Contracts

Create `DATA-CONTRACTS.md` for event/schema details.

It should define:

- event names
- fields
- types
- required values
- enumerations
- versioning
- producers
- consumers

This file should remain source-oriented rather than schema-heavy.

---

# 76. IDs

Use stable IDs for reusable business entities:

- `room_id`
- `microzone_id`
- `desired_function_id`
- `root_cause_id`
- `quest_id`
- `card_id`
- `product_id`
- `experiment_id`

Do not use display names as primary identifiers.

---

# 77. Cross-System ID Mapping

When systems use different IDs, maintain mapping.

Example:

`internal_product_id`
↔ `commerce_product_id`
↔ `payment_price_id`
↔ `analytics_item_id`

Avoid joining solely on product name.

---

# 78. Schema Changes

Schema changes affecting analytics should:

1. be version controlled
2. update data contracts
3. preserve compatibility where reasonable
4. update transformations
5. validate dashboards
6. document metric impact

---

# 79. Test Data

Test data must be distinguishable.

Use:

- test environment
- test account flag
- test transaction mode
- explicit metadata

Exclude from business KPIs.

Never delete ambiguous production records merely because they "look like tests."

---

# 80. Bots and Crawlers

Search-engine crawlers are meaningful for technical operations but not customer engagement.

Separate bot/crawler traffic from customer behavioral analytics where practical.

---

# 81. Manual Data

Manual data may be used when no automated source exists.

It must include:

- owner
- entered date
- source evidence
- confidence
- expected replacement plan

Manual does not automatically mean bad.

Unlabeled manual data is bad.

---

# 82. External Market Data

For competitor/market research, record:

- source
- retrieval date
- scope
- methodology
- limitations

Do not blend market estimates into internal actuals.

---

# 83. Estimates

All estimates must be labeled:

`ESTIMATE`

Include:

- assumptions
- formula
- source inputs
- date

Never place an estimate in a dashboard field labeled as actual.

---

# 84. Forecasts

All forecasts must be labeled:

`FORECAST`

Include:

- horizon
- model/method
- assumptions
- confidence/range

A revenue target is not a forecast.

---

# 85. Targets

Targets are management choices.

Examples:

- $20K monthly revenue
- WIP ≤ 3

Do not present targets as observed data.

---

# 86. Historical Snapshots

Preserve enough historical state to analyze trends.

Do not use `STATUS.md` as the historical database.

Use actual data storage for time series.

Markdown should summarize.

---

# 87. Data Warehouse / Operational Database

Do not introduce a warehouse solely because one is common in larger companies.

First determine:

- data volume
- sources
- query needs
- dashboard latency
- complexity

A small reporting database/materialized layer may be sufficient initially.

---

# 88. Executive Data Layer

Target architecture:

**Operational Sources**
→ **Collection / APIs**
→ **Normalized Metrics Layer**
→ **Executive Dashboard**

The normalized layer should encode canonical definitions from `METRICS.md`.

---

# 89. Dashboard API

If the executive dashboard uses an API, it should expose:

- metric
- value
- period
- comparison
- source
- refreshed_at
- confidence
- status where relevant

Avoid embedding source credentials in frontend code.

---

# 90. Collection Failure

When collection fails:

1. retain last known value if useful
2. mark it stale
3. record failure
4. alert if critical
5. do not convert stale data into current data

---

# 91. Data Observability

At minimum monitor:

- collection success
- freshness
- row/event volume anomalies
- schema failures
- reconciliation failures

Do not build a huge data-observability platform before needed.

---

# 92. Metric Lineage

For executive KPIs, maintain lineage:

**Source**
→ **Raw Field/Event**
→ **Transformation**
→ **Metric**
→ **Dashboard**

This is especially important for revenue and conversion.

---

# 93. Analytics Intelligence Agent

`analytics-intelligence` owns:

- source registry quality
- metric implementation
- reconciliation
- freshness
- dashboard data confidence

It does not own the underlying production systems.

---

# 94. SEO/AEO Agent

`seo-aeo` owns interpretation of:

- Search Console
- crawl data
- index observations
- organic landing performance

It must use canonical revenue/product metrics for downstream business impact.

---

# 95. Commerce Manager

`commerce-manager` owns interpretation of:

- catalog
- orders
- pricing
- refunds
- fulfillment
- commerce economics

It should reconcile with payments and analytics.

---

# 96. GitHub Manager

`github-manager` owns:

- source-control truth
- CI truth
- release metadata

It coordinates with `vps-docker-manager` to establish deployed truth.

---

# 97. VPS/Docker Manager

`vps-docker-manager` owns:

- host truth
- container truth
- runtime configuration
- persistent runtime assets
- backup execution state

It does not redefine application/product metrics.

---

# 98. DevOps/SRE

`devops-sre` owns reliability interpretation across:

- external availability
- application behavior
- host/container signals
- incidents
- recovery readiness

---

# 99. Source Access Failure

If an agent lacks required access:

- report source as `DISCONNECTED` or inaccessible
- identify the missing permission/integration
- continue work that does not require it
- do not fabricate the missing information

---

# 100. First Discovery Run

The first autonomous discovery should produce a verified inventory.

## GitHub

- repository
- default branch
- workflows
- releases
- deployment configuration
- secrets names only where visible
- open PRs
- dependency/security state

## Hostinger

- host
- OS
- resources
- Docker
- Compose
- containers
- images
- networks
- volumes
- reverse proxy
- TLS
- scheduled jobs
- backup mechanism

## Application

- architecture
- database
- product events
- authentication
- commerce
- APIs

## Growth

- analytics
- Search Console
- sitemap
- robots
- SEO tooling

## Commerce

- catalog
- checkout
- payment provider
- orders
- refunds
- fulfillment

---

# 101. First Reconciliation Run

After discovery, reconcile:

1. GitHub → production
2. catalog → checkout
3. commerce → payments
4. analytics purchase events → commerce
5. content catalog → live site
6. sitemap → live routes
7. live routes → index evidence
8. database → product analytics for critical events
9. persistent data → backups

Document mismatches in `STATUS.md` and backlog them.

---

# 102. First Dashboard Data Set

Do not wait for every possible source.

Initial dashboard should prioritize verified:

- site status
- deployed release
- revenue
- orders
- users/sessions
- organic sessions
- search clicks
- quest starts
- quest completions
- purchase conversion
- active experiments
- incidents
- backup freshness
- active workstreams
- pending RED approvals

Unknown values should remain visible as UNKNOWN until connected.

---

# 103. Source Addition Process

When adding a source:

1. identify business need
2. identify owner
3. establish least-privilege access
4. verify source
5. document authority
6. document freshness
7. validate sample data
8. map canonical IDs
9. reconcile where necessary
10. update registry

---

# 104. Source Removal Process

Before removing a source:

1. identify dependent metrics
2. identify dashboards
3. identify automations
4. migrate dependencies
5. verify replacement
6. archive necessary historical data
7. mark source `DEPRECATED`

Do not silently break metric lineage.

---

# 105. Source Cost

Data tooling should have economic discipline.

Before adding paid infrastructure ask:

- What decision does it improve?
- Is an existing source sufficient?
- What is expected usage?
- What is monthly cost?
- Can it be removed easily?

Follow spending authority in `AUTONOMY.md`.

---

# 106. Near-Real-Time Philosophy

Near-real-time data is valuable where the next action depends on immediate state.

Use it for:

- outages
- checkout failures
- orders/revenue operational pulse
- deployment health

Daily is often sufficient for:

- SEO
- content performance
- most experiments

Weekly/monthly is often sufficient for:

- retention
- strategic economics

Do not create unnecessary streaming complexity.

---

# 107. Data and Autonomous Decisions

Before Claude makes a data-driven change:

1. verify metric definition
2. verify source
3. check freshness
4. check confidence
5. inspect relevant segment
6. identify plausible constraint
7. define expected outcome
8. execute within authority
9. measure result

This is the closed improvement loop.

---

# 108. Evidence Standard

When Claude says:

**"Conversion decreased."**

It should know:

- conversion definition
- current value
- comparison value
- periods
- sample size
- source
- freshness
- confidence

When Claude says:

**"This caused conversion to decrease."**

It needs stronger causal evidence.

Do not confuse observation with causation.

---

# 109. Executive Source Transparency

The executive dashboard should make source quality easy to inspect without overwhelming the owner.

Suggested interaction:

Metric card
→ current value
→ trend
→ status
→ source/freshness tooltip or detail

For UNKNOWN:

show why.

---

# 110. Status Integration

`STATUS.md` should summarize verified state.

When live source changes materially:

- live source wins
- update status
- preserve history elsewhere if necessary

Do not allow stale Markdown to override production truth.

---

# 111. Decision Integration

When a source conflict requires a durable policy decision, record it in `DECISIONS.md`.

Example:

**Decision:** Net revenue will use commerce recognized revenue with processor refund reconciliation.

Then implement consistently.

---

# 112. Learning Integration

When data reveals a durable customer insight, record it in `LEARNINGS.md`.

Example:

**Observed:** Entryway shoe quests under 30 minutes have materially higher completion than 60-minute variants.

Only record as validated learning when evidence supports it.

---

# 113. Backlog Integration

Data gaps are legitimate backlog items when they block decisions.

Examples:

- missing quest completion event
- no payment reconciliation
- no restore verification
- product IDs inconsistent across systems

Prioritize based on decision impact.

---

# 114. Security Rule

Never solve data visibility by weakening security.

Do not:

- expose database publicly
- put secret APIs in browser code
- commit credentials
- make dashboards public by accident
- log sensitive payment/customer data

Use secure server-side integration.

---

# 115. Owner Control

Autonomous access should remain revocable.

Prefer:

- scoped tokens
- service accounts
- least privilege
- auditable credentials
- separated production access where practical

Claude autonomy must not make the human owner unable to regain control.

---

# 116. Current Source State

At creation of this document, actual production integrations have **not been verified within this file**.

Therefore the correct state is:

**GitHub:** UNVERIFIED  
**Hostinger VPS:** UNVERIFIED  
**Docker:** UNVERIFIED  
**Database:** UNVERIFIED  
**Analytics:** UNVERIFIED  
**Search Console:** UNVERIFIED  
**Commerce:** UNVERIFIED  
**Payments:** UNVERIFIED  
**Monitoring:** UNVERIFIED  
**Backups:** UNVERIFIED

Agents should replace these states only after actual inspection.

---

# 117. Immediate Autonomous Tasks

After this file is installed:

## Task 1

`github-manager` performs read-only repository/control-plane discovery.

## Task 2

`vps-docker-manager` performs read-only runtime discovery.

## Task 3

`analytics-intelligence` inventories analytics/product-data sources.

## Task 4

`commerce-manager` inventories commerce/payment/catalog sources.

## Task 5

`seo-aeo` inventories search/indexing sources.

## Task 6

`devops-sre` inventories monitoring/reliability evidence.

## Task 7

Update this registry with verified source names and authority.

## Task 8

Update `STATUS.md`.

---

# 118. Desired End State

The autonomous system should eventually be able to answer:

**What code is running?**

from verified GitHub/build/runtime lineage.

**Is production healthy?**

from external and runtime telemetry.

**How many people are visiting?**

from verified analytics.

**How are they finding us?**

from analytics and search sources.

**Are they completing useful work?**

from product events and transactional state.

**What are they buying?**

from commerce.

**How much money are we making?**

from reconciled commerce/payment data.

**Are improvements sustaining?**

from product follow-up data.

**What should we improve next?**

from canonical metrics and strategy.

---

# Final Rule

**The autonomous system may move quickly, but it may not invent reality.**

When evidence exists, use it.

When sources disagree, reconcile them.

When data is stale, label it.

When data is missing, say `UNKNOWN`.

When a source is weak, report confidence.

The executive dashboard must become a window into the actual business and production system, not a polished collection of guesses.
