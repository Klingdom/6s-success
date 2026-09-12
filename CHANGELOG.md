# CHANGELOG.md

## 6S Success Canonical Change History and Release Intelligence Standard

**Document role:** Canonical record and governance standard for
meaningful changes across 6S Success\
**Status:** ACTIVE\
**Owner:** Founder / Owner\
**Operational steward:** Claude Code autonomous operating system\
**Primary contributors:** GitHub Manager, Hostinger VPS/Docker Manager,
DevOps/SRE, Product, Home Quest, Content, Data, Commerce, Services,
Security, AI/ML, and other domain agents\
**Last updated:** 2026-09-12

------------------------------------------------------------------------

# 1. Purpose

`CHANGELOG.md` records meaningful changes to the 6S Success business,
product, customer experience, content, data, infrastructure, autonomous
operating system, procurement architecture, services, and commercial
system.

It exists to answer:

> **What changed, when did it change, why did it change, what evidence
> or decision drove it, what systems and customers were affected, how
> was it verified, and what should we watch next?**

This is not a raw Git commit log.

It is the executive and operational history of changes that matter.

------------------------------------------------------------------------

# 2. Core Principle

``` text
CHANGE
  ↓
WHY
  ↓
IMPLEMENTATION
  ↓
VERIFICATION
  ↓
CUSTOMER / BUSINESS EFFECT
  ↓
LEARNING
  ↓
NEXT ACTION
```

A change is not complete merely because code was merged or a document
was edited.

------------------------------------------------------------------------

# 3. Relationship to Other Canonical Files

This file integrates with:

``` text
CLAUDE.md
BUSINESS.md
STRATEGY.md
AUTONOMY.md
METRICS.md
DASHBOARD.md
DATA-SOURCES.md
DATA-CONTRACTS.md
STATUS.md
ROADMAP.md
BACKLOG.md
DECISIONS.md
LEARNINGS.md
RISKS.md
EXPERIMENTS.md
EXECUTIVE-BRIEF.md
RUNBOOK.md
INCIDENTS.md
PRODUCT-CATALOG.md
CONTENT-CATALOG.md
```

`CHANGELOG.md` should point to those sources rather than duplicating
their full content.

------------------------------------------------------------------------

# 4. What Belongs in the Changelog

Record changes that materially affect one or more of:

``` text
customer experience
product behavior
business model
commercial offer
pricing
Home Quest
cards
quests
rooms/micro-zones
services
procurement
kits
content
book/manuals
data definitions
analytics
AI behavior
agent behavior
autonomy
security/privacy
production
GitHub/deployment
VPS/Docker
database
integrations
executive dashboard
canonical operating standards
```

------------------------------------------------------------------------

# 5. What Does Not Belong

Do not record every:

``` text
typo
formatting adjustment
minor refactor
dependency patch with no material effect
internal scratch note
temporary local experiment
routine automated refresh
individual social copy edit
```

unless the change is operationally meaningful.

------------------------------------------------------------------------

# 6. Changelog vs Git History

Git answers:

``` text
Which files changed?
Which commit?
Who committed?
```

The canonical changelog answers:

``` text
Why did the change matter?
What business/product capability changed?
What was the expected outcome?
How was it verified?
What should the owner know?
```

Both are required.

------------------------------------------------------------------------

# 7. Changelog vs Decisions

`DECISIONS.md` records important choices and rationale.

`CHANGELOG.md` records what actually changed.

Example:

``` text
DECISION:
Use Entryway as the first Home Quest validation environment.

CHANGE:
Entryway deck/card architecture implemented as the prototype
and whole-home expansion gated behind Entryway learning.
```

------------------------------------------------------------------------

# 8. Changelog vs Status

`STATUS.md` describes the current state.

`CHANGELOG.md` explains how the system got there.

------------------------------------------------------------------------

# 9. Changelog vs Incidents

`INCIDENTS.md` records failures and response.

`CHANGELOG.md` records meaningful corrective changes after incidents.

Example:

``` text
INCIDENT:
Quest completion events stopped recording.

CHANGELOG:
Added contract test and production synthetic check for quest.completed.
```

------------------------------------------------------------------------

# 10. Change ID

Every material change should have a stable ID.

Recommended:

``` text
CHG-YYYY-NNNN
```

Example:

``` text
CHG-2026-0001
```

Do not reuse IDs.

------------------------------------------------------------------------

# 11. Change Categories

Use one primary category:

``` text
STRATEGY
BUSINESS
PRODUCT
HOME_QUEST
APP
CONTENT
BOOK
VISUAL
SERVICE
COMMERCE
PROCUREMENT
PRODUCT_CATALOG
DATA
ANALYTICS
AI
AUTONOMY
AGENT
GITHUB
DEVOPS
INFRASTRUCTURE
VPS_DOCKER
DATABASE
SECURITY
PRIVACY
INTEGRATION
METRICS
DASHBOARD
OPERATIONS
DOCUMENTATION
OTHER
```

Secondary tags may be added.

------------------------------------------------------------------------

# 12. Change Types

Use:

``` text
ADDED
CHANGED
IMPROVED
FIXED
REMOVED
DEPRECATED
SUPERSEDED
MIGRATED
ROLLED_BACK
SECURITY
EXPERIMENTAL
```

------------------------------------------------------------------------

# 13. Change Status

Use:

``` text
PLANNED
IN_PROGRESS
DEPLOYED
VERIFIED
PARTIALLY_VERIFIED
ROLLED_BACK
SUPERSEDED
CANCELLED
```

Only `VERIFIED` means the intended result was checked.

------------------------------------------------------------------------

# 14. Impact Level

Use:

``` text
CRITICAL
MAJOR
MODERATE
MINOR
```

Impact reflects importance, not engineering effort.

------------------------------------------------------------------------

# 15. Canonical Change Record

``` yaml
change:
  change_id:
  date:
  title:
  category:
  type:
  status:
  impact:
  summary:
  reason:
  expected_outcome:
  customer_impact:
  business_impact:
  systems_affected:
  rooms:
  micro_zones:
  product_ids:
  content_ids:
  service_ids:
  requirement_ids:
  related_decisions:
  related_backlog:
  related_experiments:
  related_learnings:
  related_risks:
  related_incidents:
  github:
    repository:
    branch:
    pull_request:
    commit:
    release:
  deployment:
    environment:
    version:
    deployed_at:
  verification:
    method:
    result:
    verified_at:
  rollback:
    available:
    method:
  owner:
  implemented_by:
  source_provenance:
  notes:
```

------------------------------------------------------------------------

# 16. Human-Readable Entry Template

``` markdown
## CHG-YYYY-NNNN: [Title]

**Date:**  
**Category:**  
**Type:**  
**Impact:**  
**Status:**  

### Changed

### Why

### Expected Outcome

### Verification

### Customer / Business Impact

### Related
- Decision:
- Experiment:
- Learning:
- Risk:
- Incident:
- GitHub:
- Deployment:

### Watch Next
```

------------------------------------------------------------------------

# 17. Release Entry Template

``` markdown
# Release [Version]: YYYY-MM-DD

## Added

## Changed

## Improved

## Fixed

## Removed / Deprecated

## Data / Metrics

## Infrastructure

## Security / Privacy

## Content

## Verification

## Known Issues

## Owner Attention
```

------------------------------------------------------------------------

# 18. Source of Truth Hierarchy

A changelog entry should be grounded in authoritative evidence.

Preferred order:

``` text
actual production state
deployment/release evidence
GitHub PR/commit
canonical artifact
database migration
owner-approved decision
experiment result
validated learning
```

Do not reconstruct precise implementation facts from conversational
memory when live evidence exists.

------------------------------------------------------------------------

# 19. Historical Reconstruction Rule

The project has substantial prior research and development, but not
every prior activity has a verified date, commit, or production state
available inside this document.

Therefore:

> **Do not fabricate a detailed historical deployment log.**

This file begins with a **Verified/Documented Baseline History**
containing only project milestones that are sufficiently established
from current project records.

When GitHub, VPS/Docker, production, and source artifacts are available,
Claude should reconcile and enrich the history.

------------------------------------------------------------------------

# 20. Historical Confidence

Historical entries may use:

``` text
VERIFIED
DOCUMENTED
INFERRED
UNKNOWN
```

Only `VERIFIED` should be used when direct authoritative evidence has
been inspected.

`DOCUMENTED` means established in project artifacts/conversation history
but not yet reconciled to production/Git history.

Do not present `INFERRED` changes as facts.

------------------------------------------------------------------------

# 21. Baseline Project Evolution

The following is a documented R&D baseline, not a claim that every item
is currently deployed in production.

------------------------------------------------------------------------

# 22. 6S Success Home Edition Established

**Historical confidence:** DOCUMENTED\
**Category:** BOOK / PRODUCT / CONTENT\
**Type:** ADDED

The project established **6S Success: Home Edition** as a practical
household adaptation of 6S for young professionals and families.

Core method:

``` text
Sort
Straighten
Shine
Safety
Standardize
Sustain
```

Editorial direction emphasized practical home use, compassionate
instruction, limited Lean jargon, strong visual communication, and
reusable household systems.

------------------------------------------------------------------------

# 23. Home Edition Visual System Established

**Historical confidence:** DOCUMENTED\
**Category:** VISUAL / CONTENT\
**Type:** ADDED

A recognizable visual system was established around warm, realistic,
Scandinavian-influenced middle-class homes, natural materials,
whitespace, editorial photography/illustration, and a defined color
palette.

Established palette includes:

``` text
Cream       #F7F2E9
Warm White  #FBF7EF
Near Black  #2B2622
Terracotta  #BC4B2A
Honey Amber #DDA63A
Slate Blue   #3C5A6B
Soft Green   #6E8B5B
Soft Oak     #E7C58B
```

------------------------------------------------------------------------

# 24. Room Reset Manual Architecture Added

**Historical confidence:** DOCUMENTED\
**Category:** BOOK / CONTENT\
**Type:** ADDED

Room-specific reset manuals expanded the Home Edition into detailed room
execution.

The system includes room-level chapters, micro-zone guidance,
illustration plans, and figure production.

Recent illustration work adopted a
realistic-photo-concept-to-line-drawing workflow.

------------------------------------------------------------------------

# 25. Micro-Zone Architecture Expanded

**Historical confidence:** DOCUMENTED\
**Category:** PRODUCT / CONTENT\
**Type:** IMPROVED

6S Success evolved from room-level organization toward a more granular
**micro-zone** operating model.

Examples include:

``` text
entryway keys
entryway shoes
mail
bags
bathroom countertop
medicine cabinet
bathroom drawers
under sink
towel storage
laundry sorting
desk cables
pantry categories
closet hanging/folded storage
```

This became foundational to the book, Home Quest, services, app, product
catalog, and photo-analysis concepts.

------------------------------------------------------------------------

# 26. Home Quest Concept Added

**Historical confidence:** DOCUMENTED\
**Category:** HOME_QUEST / PRODUCT\
**Type:** ADDED

The project introduced **6S Success Home Quest**, converting household
6S activities into cards and configurable quests.

Key concepts include:

``` text
room cards
micro-zone cards
6S activity cards
physical and digital cards
card selection
assignment
voluntary selection
random selection
15-90 minute events
individual and group play
```

------------------------------------------------------------------------

# 27. Entryway Selected as Prototype Environment

**Historical confidence:** DOCUMENTED\
**Category:** HOME_QUEST / STRATEGY\
**Type:** CHANGED

Entryway became the primary prototype environment for validating the
Home Quest system.

Entryway card prototypes, front/back designs, room/micro-zone structure,
and beta messaging were developed.

Current strategic direction is to validate Entryway deeply before
indiscriminate whole-home expansion.

------------------------------------------------------------------------

# 28. Whole-Home Master Card Architecture Added

**Historical confidence:** DOCUMENTED\
**Category:** HOME_QUEST / CONTENT\
**Type:** ADDED

The project expanded Entryway concepts into a whole-home master card
list organized around rooms, micro-zones, and 6S activities.

The actual source artifact should be inventoried and migrated into
`CONTENT-CATALOG.md` rather than recreated from memory.

------------------------------------------------------------------------

# 29. Multiplayer Quest App Requirements Added

**Historical confidence:** DOCUMENTED\
**Category:** APP / HOME_QUEST\
**Type:** ADDED

Requirements were developed for a smartphone experience capable of
engaging approximately **1--10 players simultaneously** in configurable,
predetermined, or random activities.

The concept includes cooperative/group execution and game-like
mechanics.

------------------------------------------------------------------------

# 30. Photo-Based Micro-Zone Analysis Added

**Historical confidence:** DOCUMENTED\
**Category:** APP / AI / PRODUCT\
**Type:** ADDED

The app concept evolved to allow customers to upload or take photos of
household micro-zones.

Intended flow:

``` text
capture/upload
 ↓
identify room/micro-zone/items/functions
 ↓
analyze current state
 ↓
recommend 6S activities
 ↓
identify supplies if needed
 ↓
provide step-by-step execution
 ↓
verify result
```

The architecture explicitly requires caution around AI certainty and
household privacy.

------------------------------------------------------------------------

# 31. Digital Inventory Concept Added

**Historical confidence:** DOCUMENTED\
**Category:** APP / PRODUCT\
**Type:** ADDED

A digital household inventory concept was developed:

``` text
photo item
identify item
identify primary function
identify room/micro-zone
keep / donate / move / store
guide storage selection
```

------------------------------------------------------------------------

# 32. UPC and Consumables Management Added

**Historical confidence:** DOCUMENTED\
**Category:** APP / COMMERCE / PRODUCT\
**Type:** ADDED

The inventory concept expanded to support:

``` text
UPC scanning
placement
quantity
consumable min/max
replenishment trigger
quick reorder
```

Purchasing remains subject to customer/owner authority.

------------------------------------------------------------------------

# 33. Label Ecosystem Added

**Historical confidence:** DOCUMENTED\
**Category:** PRODUCT / CONTENT\
**Type:** ADDED

6S Success developed a labeling ecosystem including Phomemo M02 use
cases, location/category labels, QR inventory labels, and visual-control
concepts across rooms and micro-zones.

------------------------------------------------------------------------

# 34. Gridfinity / 3D Printing Ecosystem Added

**Historical confidence:** DOCUMENTED\
**Category:** PRODUCT / PRODUCT_CATALOG\
**Type:** ADDED

Whole-home modular storage R&D was added around Bambu Lab 3D printing
and Gridfinity-style modular systems.

Priority environments included:

``` text
entryway
desk/office
bathroom
other compatible micro-zones
```

A key-tray module was an early prototype target.

------------------------------------------------------------------------

# 35. Home Services Business Expanded

**Historical confidence:** DOCUMENTED\
**Category:** SERVICE / BUSINESS\
**Type:** ADDED

6S Success expanded beyond DIY content into a home organization and
cleaning service concept.

The service architecture includes Shine/cleaning, decluttering,
organization, micro-zone resets, safety, visual control, and related
value-added services.

Shine was explored as a potential entry service that could create
near-term revenue and lead into broader 6S services.

------------------------------------------------------------------------

# 36. Brand Architecture Improved

**Historical confidence:** DOCUMENTED\
**Category:** BUSINESS / CONTENT / VISUAL\
**Type:** IMPROVED

Brand R&D included a simplified circular 6S Success identity and the
tagline:

``` text
Simple systems. Better living.
```

Visual simplification and clearer service communication became
priorities.

------------------------------------------------------------------------

# 37. Product and Service Kit Architecture Expanded

**Historical confidence:** DOCUMENTED\
**Category:** PROCUREMENT / COMMERCE / SERVICE\
**Type:** ADDED

Product/supply lists were expanded to support documented services and
room/micro-zone resets.

The objective became linking each activity/service to the exact
cleaning, organization, storage, visual-control, and safety inputs
required.

------------------------------------------------------------------------

# 38. Whole-Home Procurement V8 Established

**Historical confidence:** DOCUMENTED\
**Category:** PROCUREMENT / PRODUCT_CATALOG\
**Type:** ADDED

A canonical procurement artifact was established:

``` text
6S_Success_Whole_Home_Procurement_Kit_Master_V8.html
```

V8 became the baseline/source file for subsequent procurement
development.

------------------------------------------------------------------------

# 39. Whole-Home Procurement V9 Established

**Historical confidence:** DOCUMENTED\
**Category:** PROCUREMENT / PRODUCT_CATALOG / COMMERCE\
**Type:** IMPROVED

V9 evolved the procurement architecture into:

``` text
6S_Success_Whole_Home_Tiered_Procurement_Master_V9.html
```

Documented characteristics include:

``` text
117-product procurement master
156-requirement mapping
$199 tier
$299 tier
$499 tier
exact quantities
BOM economics
fallback products
affiliate-readiness fields
requirement coverage
margin/retail-price fields
```

V9 remains the procurement migration baseline until reconciled into the
structured product catalog.

------------------------------------------------------------------------

# 40. Tiered Commercial Kit Hypothesis Added

**Historical confidence:** DOCUMENTED\
**Category:** COMMERCE / PROCUREMENT\
**Type:** ADDED

Nested commercial kit concepts were established at:

``` text
$199
$299
$499
```

These remain commercial hypotheses requiring customer-demand and
full-economics validation.

------------------------------------------------------------------------

# 41. Autonomous Claude Code Operating Model Added

**Historical confidence:** DOCUMENTED\
**Category:** AUTONOMY / AI / OPERATIONS\
**Type:** ADDED

The project expanded toward an autonomous Claude Code operating system
capable of:

``` text
understanding business context
managing backlog/roadmap
monitoring health
working through specialized agents
using GitHub
managing VPS/Docker
measuring outcomes
surfacing executive information
continuously improving
```

------------------------------------------------------------------------

# 42. Specialized GitHub Manager Agent Added

**Historical confidence:** DOCUMENTED\
**Category:** AGENT / GITHUB\
**Type:** ADDED

A dedicated GitHub management/optimization sub-agent was developed to
improve repository health, change control, CI/CD awareness, code
governance, and traceability.

------------------------------------------------------------------------

# 43. Specialized Hostinger VPS/Docker Manager Agent Added

**Historical confidence:** DOCUMENTED\
**Category:** AGENT / VPS_DOCKER\
**Type:** ADDED

A dedicated Hostinger VPS/Docker project-management sub-agent was
developed for infrastructure health, container operations, deployments,
recovery, and operational optimization.

------------------------------------------------------------------------

# 44. DevOps Agent Architecture Updated

**Historical confidence:** DOCUMENTED\
**Category:** AGENT / DEVOPS\
**Type:** IMPROVED

The broader DevOps/SRE agent architecture was updated to work with the
specialized GitHub and Hostinger VPS/Docker agents rather than
duplicating their responsibilities.

------------------------------------------------------------------------

# 45. Canonical Non-Agent Operating System Added

**Historical confidence:** DOCUMENTED\
**Category:** AUTONOMY / DOCUMENTATION\
**Type:** ADDED

A canonical set of non-agent Markdown files was defined so Claude can
operate with persistent business, strategic, operational, data, risk,
product, and executive context.

The original baseline contains 21 files:

``` text
CLAUDE.md
BUSINESS.md
STRATEGY.md
AUTONOMY.md
METRICS.md
DASHBOARD.md
DATA-SOURCES.md
DATA-CONTRACTS.md
STATUS.md
ROADMAP.md
BACKLOG.md
DECISIONS.md
LEARNINGS.md
RISKS.md
EXPERIMENTS.md
EXECUTIVE-BRIEF.md
RUNBOOK.md
INCIDENTS.md
PRODUCT-CATALOG.md
CONTENT-CATALOG.md
CHANGELOG.md
```

------------------------------------------------------------------------

# 46. Executive Dashboard Architecture Added

**Historical confidence:** DOCUMENTED\
**Category:** DASHBOARD / DATA / AUTONOMY\
**Type:** ADDED

The autonomous operating model includes an executive dashboard intended
to provide near-real-time owner visibility into business and system
health.

The dashboard should prioritize decisions, exceptions, risks, customer
evidence, revenue/commercial signals, experiments, system health, and
autonomous work rather than vanity metrics.

------------------------------------------------------------------------

# 47. Metrics and Data Governance Added

**Historical confidence:** DOCUMENTED\
**Category:** METRICS / DATA\
**Type:** ADDED

Canonical metric definitions, data-source mapping, and data-contract
architecture were established to prevent autonomous decisions from
relying on ambiguous or inconsistent measures.

------------------------------------------------------------------------

# 48. Risk Management Standard Added

**Date:** 2026-08-17 baseline\
**Historical confidence:** DOCUMENTED\
**Category:** OPERATIONS / AUTONOMY\
**Type:** ADDED

`RISKS.md` established the canonical risk-management framework.

High-priority themes include:

``` text
architecture outrunning validation
Entryway outcomes not yet sufficiently proven
autonomy complexity outrunning value
multiple sources of truth
household-image privacy
AI overstatement
deployment failure
measurement failure
security/secrets
backup/restore
commerce trust
kit economics
physical production
founder dependency
```

------------------------------------------------------------------------

# 49. Incident Management Standard Added

**Date:** 2026-08-17 baseline\
**Historical confidence:** DOCUMENTED\
**Category:** OPERATIONS / DEVOPS\
**Type:** ADDED

`INCIDENTS.md` established:

``` text
severity
classification
incident command
containment
mitigation
recovery
verification
postmortem
corrective/preventive actions
historical reconstruction rules
```

It explicitly recognizes measurement failures as potentially
strategically material.

------------------------------------------------------------------------

# 50. Product Catalog Standard Added

**Date:** 2026-08-17 baseline\
**Historical confidence:** DOCUMENTED\
**Category:** PRODUCT_CATALOG / PROCUREMENT\
**Type:** ADDED

`PRODUCT-CATALOG.md` established the canonical architecture connecting:

``` text
room
micro-zone
desired function
requirement
6S activity
card/quest
product class
specific product
substitute
kit
service
outcome
Sustain
```

It requires migration from the actual V9 artifact rather than
fabrication from memory.

------------------------------------------------------------------------

# 51. Content Catalog Standard Added

**Date:** 2026-08-17 baseline\
**Historical confidence:** DOCUMENTED\
**Category:** CONTENT\
**Type:** ADDED

`CONTENT-CATALOG.md` established the architecture for canonical
knowledge and derivatives across:

``` text
book
Room Reset Manuals
Home Quest
cards
quests
app
website
SEO/AEO
services
products
labels
social
visual assets
```

Core principle:

``` text
CREATE CANONICAL KNOWLEDGE ONCE
REUSE IT INTELLIGENTLY
MEASURE WHETHER IT HELPS
```

------------------------------------------------------------------------

# 52. Changelog Standard Added

**Date:** 2026-08-17\
**Historical confidence:** VERIFIED BY THIS ARTIFACT\
**Category:** OPERATIONS / DOCUMENTATION\
**Type:** ADDED

This file completes the original 21-file canonical non-agent baseline.

The next phase should move from creating governance documents toward
connecting them to live systems and validating that Claude actually uses
them.

------------------------------------------------------------------------

# 53. Current Canonical Baseline Status

As of this baseline:

``` text
21 / 21 ORIGINAL NON-AGENT CANONICAL FILES DEFINED/CREATED
```

This does not mean the autonomous operating system is finished.

It means the initial documentation/control plane is now established.

------------------------------------------------------------------------

# 54. Next Phase: From Documents to Operating System

Priority should now shift toward:

``` text
1. inventory actual files and repositories
2. verify canonical versions
3. connect GitHub
4. inspect production architecture
5. inspect Hostinger VPS/Docker
6. map databases and integrations
7. verify analytics/events
8. populate executive dashboard from live sources
9. migrate V9 product data
10. migrate Entryway/content assets
11. implement automated health/integrity checks
12. run autonomy acceptance tests
```

------------------------------------------------------------------------

# 55. Near-Term Change Priorities

The highest-value future changelog entries should represent actual
operating improvements such as:

``` text
live GitHub repository map completed
production deployment path verified
VPS/Docker topology verified
backup restore tested
Entryway analytics instrumented
first real beta cohort launched
first verified quest outcomes collected
first Sustain measurement collected
V9 migrated into structured catalog
content catalog populated from actual assets
executive dashboard connected to live data
```

------------------------------------------------------------------------

# 56. Change Verification

Verification should match the change.

## Code

``` text
tests
deployment
health check
customer-flow check
```

## Data

``` text
schema validation
event validation
reconciliation
dashboard check
```

## Content

``` text
canonical review
published rendering
link/product integrity
customer usability where appropriate
```

## Procurement

``` text
BOM reconciliation
quantity validation
availability
margin
coverage
```

## Agent

``` text
acceptance scenario
authority check
context check
failure handling
```

------------------------------------------------------------------------

# 57. Production Change Rule

A production change should normally capture:

``` text
GitHub reference
deployment reference
environment
verification
rollback capability
```

Do not call a merge a deployment.

------------------------------------------------------------------------

# 58. Database Change Rule

Database changes should record:

``` text
migration
compatibility
backup/recovery considerations
application dependency
verification
rollback/forward-fix strategy
```

------------------------------------------------------------------------

# 59. AI / Prompt Change Rule

Material changes to AI behavior should record:

``` text
model/prompt/config affected
expected behavior change
evaluation performed
safety implications
cost implications
customer impact
```

Prompt changes can be production changes.

------------------------------------------------------------------------

# 60. Agent Change Rule

When changing an agent:

``` text
responsibility
authority
inputs/context
tools
outputs
escalation
acceptance tests
```

must be evaluated.

Do not optimize one agent in a way that creates overlapping ownership.

------------------------------------------------------------------------

# 61. Autonomy Change Rule

Changes that expand Claude's authority require explicit attention.

Record:

``` text
old authority
new authority
reason
guardrails
rollback
owner approval if required
```

------------------------------------------------------------------------

# 62. Dashboard Change Rule

When dashboard metrics change, record:

``` text
metric added/removed
definition
source
decision supported
freshness
historical comparability
```

Avoid silently redefining metrics.

------------------------------------------------------------------------

# 63. Metric Definition Change

If a metric formula changes:

``` text
OLD DEFINITION
NEW DEFINITION
EFFECTIVE DATE
HISTORICAL RESTATEMENT?
WHY
```

must be documented.

------------------------------------------------------------------------

# 64. Product Catalog Change Rule

Material product changes should capture:

``` text
product_id
product class
substitute
kit impact
requirement impact
cost/margin impact
availability
reason
```

------------------------------------------------------------------------

# 65. Kit Change Rule

For \$199/\$299/\$499 or future kits, record:

``` text
product additions/removals
quantity changes
substitution changes
BOM delta
retail-price delta
margin delta
coverage delta
```

------------------------------------------------------------------------

# 66. Content Change Rule

Material canonical content changes should capture:

``` text
content_id
source changed
derivatives affected
reason
evidence/learning
safety impact
publication status
```

------------------------------------------------------------------------

# 67. Home Quest Change Rule

For card/quest changes:

``` text
card_id / quest_id
micro-zone
instruction
duration
supplies
verification
Sustain
game logic
reason
customer evidence
```

------------------------------------------------------------------------

# 68. Service Change Rule

Record material changes to:

``` text
scope
pricing
duration
supplies
delivery standard
customer promise
service area
upsell
```

------------------------------------------------------------------------

# 69. Security / Privacy Change Rule

Security/privacy changes should record enough to establish governance
without exposing secrets.

Never put:

``` text
passwords
tokens
private keys
sensitive customer data
exploit details that create unnecessary risk
```

into the changelog.

------------------------------------------------------------------------

# 70. Rollback Record

If a change is rolled back:

``` text
original change ID
rollback reason
rollback time
customer impact
state after rollback
follow-up
```

A rollback is itself a meaningful change.

------------------------------------------------------------------------

# 71. Change-to-Experiment

If an experiment drives a change:

``` text
EXP-ID
hypothesis
result
decision
change
```

should be traceable.

------------------------------------------------------------------------

# 72. Change-to-Learning

If a validated learning changes the product:

``` text
LEARNING
  ↓
DECISION
  ↓
CHANGE
  ↓
MEASURE AGAIN
```

This is the desired continuous-improvement loop.

------------------------------------------------------------------------

# 73. Change-to-Risk

A change may:

``` text
reduce risk
increase risk
create new risk
retire risk
```

Update `RISKS.md` when material.

------------------------------------------------------------------------

# 74. Change-to-Executive-Brief

The Executive Brief should surface:

``` text
major changes since last brief
material releases
rollbacks
new capability
owner decisions
changes affecting metrics/revenue/customer experience
```

Do not list every minor commit.

------------------------------------------------------------------------

# 75. Change-to-Roadmap

When a roadmap item is delivered, record the actual change and update
roadmap status.

Roadmap completion without a verified implementation should not be
treated as delivered.

------------------------------------------------------------------------

# 76. Change-to-Backlog

When backlog work results in a change:

``` text
BACKLOG ITEM
 ↓
IMPLEMENTATION
 ↓
VERIFICATION
 ↓
CHANGELOG
 ↓
CLOSE BACKLOG ITEM
```

------------------------------------------------------------------------

# 77. Automated Changelog Generation

Claude may draft changelog entries from:

``` text
merged PRs
releases
deployments
database migrations
canonical document updates
experiment decisions
product catalog changes
content releases
incident corrective actions
```

But it must filter for materiality.

------------------------------------------------------------------------

# 78. Automated Reconciliation

Recommended daily/continuous process:

``` text
GitHub changes
+
deployment state
+
database/schema changes
+
canonical artifact changes
+
agent actions
        ↓
materiality filter
        ↓
draft change entries
        ↓
verification
        ↓
canonical changelog
```

------------------------------------------------------------------------

# 79. Do Not Trust Commit Messages Alone

A commit named:

``` text
"fix stuff"
```

is not sufficient evidence.

Inspect the actual change and production effect where relevant.

------------------------------------------------------------------------

# 80. Change Correlation

Use correlation IDs or mission IDs where possible so one autonomous
mission can be traced through:

``` text
mission
backlog
agent
PR
commit
deployment
event
metric
change
```

------------------------------------------------------------------------

# 81. Release Versioning

Recommended application releases:

``` text
MAJOR.MINOR.PATCH
```

Example:

``` text
0.4.2
```

Use practical semantic versioning where useful.

Content, product catalogs, and procurement artifacts may use their own
controlled versions.

------------------------------------------------------------------------

# 82. Procurement Versioning

Existing example:

``` text
V8
V9
```

Future versions should document exactly what changed.

Avoid version-number increments without change summary and
reconciliation.

------------------------------------------------------------------------

# 83. Canonical Document Versioning

Material changes to operating standards should record:

``` text
document
version/date
reason
affected behavior
```

Git remains the detailed history once these files are
repository-managed.

------------------------------------------------------------------------

# 84. Change Freeze

A scoped change freeze may be appropriate during:

``` text
SEV-0/SEV-1 incident
unknown data corruption
security compromise
failed recovery
critical launch window
```

Follow `INCIDENTS.md`.

------------------------------------------------------------------------

# 85. Change Failure

If verification fails:

``` text
do not mark VERIFIED
```

Use:

``` text
PARTIALLY_VERIFIED
ROLLED_BACK
IN_PROGRESS
```

as appropriate.

------------------------------------------------------------------------

# 86. Change Success

A successful deployment is not necessarily a successful product change.

Example:

``` text
Deployment: successful.
Feature: users do not understand it.
Business outcome: worse.
```

Changelog should distinguish technical verification from customer
validation.

------------------------------------------------------------------------

# 87. Customer Validation Status

Optional:

``` text
NOT_TESTED
INTERNAL_TESTED
BETA_TESTED
CUSTOMER_OBSERVED
OUTCOME_VALIDATED
SUSTAIN_VALIDATED
```

This is especially useful for Home Quest.

------------------------------------------------------------------------

# 88. Change Performance Window

For material product changes, define what should be watched after
release.

Examples:

``` text
24 hours
7 days
30 days
next 20 quests
next 10 beta households
```

Use a meaningful denominator, not arbitrary waiting.

------------------------------------------------------------------------

# 89. Change Watch Fields

``` yaml
watch:
  metrics:
  guardrails:
  window:
  expected_direction:
  review_date:
```

------------------------------------------------------------------------

# 90. Change Dashboard

Useful executive view:

``` text
LAST PRODUCTION CHANGE
LAST VERIFIED RELEASE
CHANGES LAST 7 DAYS
FAILED / ROLLED-BACK CHANGES
MAJOR PRODUCT CHANGES
METRIC DEFINITION CHANGES
OPEN POST-CHANGE WATCHES
```

------------------------------------------------------------------------

# 91. Change Metrics

Potential:

``` text
deployment frequency
change failure rate
rollback rate
lead time for change
verification rate
unverified-change age
customer-impacting changes
experiment-driven changes
incident-driven changes
```

Definitions belong in `METRICS.md`.

------------------------------------------------------------------------

# 92. Continuous Improvement

The changelog should make PDCA visible:

``` text
PLAN
roadmap / experiment / decision

DO
implementation

CHECK
verification / metrics / customer evidence

ACT
standardize / revise / rollback
```

------------------------------------------------------------------------

# 93. 6S Lens for Change Management

## Sort

Remove obsolete changes and deprecated paths.

## Straighten

Make every meaningful change traceable.

## Shine

Continuously remove configuration drift and operational debt.

## Safety

Protect customers, data, production, finances, and owner authority.

## Standardize

Use repeatable release/change patterns.

## Sustain

Verify standards remain active.

------------------------------------------------------------------------

# 94. Autonomous Change Acceptance Tests

## GitHub Merge

Input:

``` text
PR merged but not deployed.
```

Expected:

``` text
Do not claim production changed.
```

## Deployment

Input:

``` text
Deployment completed but synthetic customer flow fails.
```

Expected:

``` text
Do not mark VERIFIED.
Initiate mitigation/incident handling as appropriate.
```

## Metric Change

Input:

``` text
conversion formula changes.
```

Expected:

``` text
Record old/new definitions and comparability impact.
```

## Content

Input:

``` text
Entryway card instruction materially changes.
```

Expected:

``` text
Update canonical content record, affected derivatives,
and changelog.
```

## Product

Input:

``` text
Preferred organizer is discontinued.
```

Expected:

``` text
Update product catalog, substitute, affected kits/content,
and changelog if material.
```

## Autonomy

Input:

``` text
Agent gains authority to deploy production automatically.
```

Expected:

``` text
Record authority expansion, guardrails, tests, and required approval.
```

------------------------------------------------------------------------

# 95. Changelog Anti-Patterns

Never:

-   dump every Git commit into this file;
-   claim code is deployed because it was merged;
-   claim customer success because deployment succeeded;
-   fabricate historical dates;
-   reconstruct detailed old releases from memory;
-   silently redefine metrics;
-   hide rollbacks;
-   omit failed changes to make performance look better;
-   record secrets;
-   duplicate entire incident/postmortem text;
-   create changelog entries with no reason or verification;
-   mark untested work as verified;
-   let agents modify production without traceability;
-   create documentation changes solely to make the changelog appear
    active.

------------------------------------------------------------------------

# 96. Historical Reconciliation Plan

Once live systems are available:

``` text
1. inspect GitHub repositories
2. identify releases/tags
3. inspect PR/commit history
4. inspect CI/CD history
5. inspect Hostinger VPS/Docker deployment state
6. inspect database migrations
7. inspect application/version metadata
8. inspect analytics instrumentation history
9. compare canonical files/artifacts
10. reconcile meaningful historical milestones
11. assign change IDs
12. mark evidence confidence
```

------------------------------------------------------------------------

# 97. Current Baseline Limitations

At creation time, this file does not claim to know:

``` text
current production commit
current production release
exact VPS container topology
actual CI/CD state
actual backup state
actual database migration history
actual live analytics completeness
exact website deployment history
```

Those must be discovered from live sources.

------------------------------------------------------------------------

# 98. Canonical Operating System Completion Milestone

## CHG-2026-BASELINE --- Original 21-File Operating Baseline Completed

**Date:** 2026-08-17\
**Category:** AUTONOMY / DOCUMENTATION\
**Type:** ADDED\
**Impact:** MAJOR\
**Status:** VERIFIED at artifact-creation level

### Changed

The original 21-file non-agent operating-document baseline for
autonomous Claude Code management has now been defined.

### Why

6S Success requires persistent, structured context so autonomous agents
can act consistently across business strategy, product development,
data, operations, GitHub, infrastructure, customer learning,
procurement, content, risks, and executive reporting.

### Expected Outcome

Claude Code can be given a coherent management/control plane instead of
relying on fragmented prompts and conversational memory.

### Verification

All 21 named baseline document categories have been created in the
project workflow.

### Important Limitation

The documents must now be placed under controlled repository management,
reconciled with actual source artifacts, connected to live systems, and
tested for real autonomous use.

------------------------------------------------------------------------

# 99. The 21-File Baseline

``` text
01 CLAUDE.md
02 BUSINESS.md
03 STRATEGY.md
04 AUTONOMY.md
05 METRICS.md
06 DASHBOARD.md
07 DATA-SOURCES.md
08 DATA-CONTRACTS.md
09 STATUS.md
10 ROADMAP.md
11 BACKLOG.md
12 DECISIONS.md
13 LEARNINGS.md
14 RISKS.md
15 EXPERIMENTS.md
16 EXECUTIVE-BRIEF.md
17 RUNBOOK.md
18 INCIDENTS.md
19 PRODUCT-CATALOG.md
20 CONTENT-CATALOG.md
21 CHANGELOG.md
```

------------------------------------------------------------------------

# 100. Recommended Next Operating Milestone

The next milestone should not be another large set of governance
documents.

It should be:

> **LIVE SYSTEM RECONCILIATION AND AUTONOMY ACTIVATION**

Success means Claude can answer from evidence:

``` text
What is running?
What changed?
Is production healthy?
What are customers doing?
What is working?
What is failing?
What should we do next?
What can Claude safely do without the owner?
What requires owner attention?
```

------------------------------------------------------------------------

# 101. Recommended Activation Sequence

``` text
PHASE 1: REPOSITORY TRUTH
GitHub map
canonical files committed
agent files committed
branch/protection/CI understood

PHASE 2: PRODUCTION TRUTH
Hostinger VPS
Docker topology
domains
services
databases
secrets/config references
deployment path

PHASE 3: DATA TRUTH
events
metrics
analytics
customer/quest data
revenue/commercial data

PHASE 4: CATALOG TRUTH
V9 procurement migration
content artifact inventory
Entryway card/quest migration

PHASE 5: EXECUTIVE TRUTH
near-real-time dashboard
Executive Brief
exceptions
risks
owner decisions

PHASE 6: AUTONOMOUS IMPROVEMENT
missions
experiments
safe changes
verification
learning
continuous improvement
```

------------------------------------------------------------------------

# 102. Changelog Maintenance Cadence

## Per Material Change

Update immediately or automatically after verification.

## Daily

Reconcile autonomous changes and deployments.

## Weekly

Review major changes, rollbacks, open watches, and missing verification.

## Monthly

Review change patterns and systemic improvement opportunities.

------------------------------------------------------------------------

# 103. Owner View

The owner should be able to ask:

``` text
"What changed this week?"
```

and receive a concise answer covering:

``` text
customer/product
revenue/commercial
experiments/learnings
production
data
risks/incidents
autonomous actions
owner decisions needed
```

This file supplies the historical backbone for that answer.

------------------------------------------------------------------------

# 104. Final Principle

A continuously improving autonomous business needs institutional memory
of change.

The target loop is:

``` text
OBSERVE
   ↓
UNDERSTAND
   ↓
DECIDE
   ↓
CHANGE
   ↓
VERIFY
   ↓
MEASURE
   ↓
LEARN
   ↓
STANDARDIZE OR REVISE
   ↓
RECORD
   ↓
REPEAT
```

`CHANGELOG.md` makes that loop auditable.

**6S Success should never have to guess why the system is different
today than it was yesterday. Every meaningful change should have a
reason, evidence, verification, and a connection to customer or business
value.**

------------------------------------------------------------------------

# 105. Post-Baseline Change Record, 2026-08-17 to 2026-09-12

This section backfills the material changes this file went silent on for
26 days after `CHG-2026-BASELINE`. It does not attempt every commit
(section 4 says not to); it covers the changes that materially affected
customer experience, product behavior, or trust, each grounded in a real
commit and, where a gate exists, a real check. Full detail on any item
lives in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md` under the same
date.

## CHG-2026-0001: Root-cause diagnosis rendered for 12 pilot zones

**Date:** 2026-09-07 **Category:** PRODUCT / HOME_QUEST **Type:** ADDED
**Impact:** MAJOR **Status:** VERIFIED

### Changed

12 of 114 zone pages (5 Entryway, 7 Kitchen) now render a diagnosis
block above the six 6S passes: the friction, its root cause, and a
branch, sourced from a new `diagnosis` schema in `content.json`
(`78165b33`, corrected `0ec5046b`), authored per zone (`3e58d480`), and
rendered live (`a0014e76`).

### Why

`CLAUDE.md` section 6 requires diagnosing root cause before prescribing
a fix. Before this, the product prescribed for all 114 zones and
diagnosed for none.

### Verification

`gate_diagnosis_rendered` (preflight), a real regenerate-and-diff check.
Not checked against the live domain: no egress from the operator
sandbox.

### Customer / Business Impact

A reader on these 12 pages sees why a zone fails, not only what to do
about it.

### Watch Next

A 21-day read of the pilot before rolling the remaining 102 zones (M6,
held on evidence per `BACKLOG-2026-09-07.md`).

## CHG-2026-0002: Symptom-first entry added to the Quest app

**Date:** 2026-09-08 **Category:** HOME_QUEST / APP **Type:** ADDED
**Impact:** MAJOR **Status:** VERIFIED

### Changed

`quest.html`'s first screen (commit `d7d2ea57`) now asks "What is
annoying you right now?" with five real household-worded symptoms drawn
from the diagnosis data above, ahead of any room or zone name. Picking
one shows the real cause and starts a simplified two-minute first
action with its own victory line, instead of the prior single generic
start button.

### Why

Convert Personal Function Discovery (`CLAUDE.md` section 5) into the
product's actual first thirty seconds.

### Verification

`ops/tests/test_quest_flow.py`, a real headless-Chromium run of the flow
end to end; `gate_quest_symptom_entry`. New events
`quest-symptom-picked`, `quest-symptom-start`, `quest-first-victory`
(no free text, no zone name, per `CLAUDE.md` section 47).

### Customer / Business Impact

Shorter path from a household frustration to a concrete first action.

## CHG-2026-0003: Kitchen deck shipped, 72 cards, free and ungated

**Date:** 2026-09-08 **Category:** CONTENT / PRODUCT **Type:** ADDED
**Impact:** MAJOR **Status:** VERIFIED

### Changed

`site/kitchen-deck.html` (commit `ea851e2d`) ships all 72 written
Kitchen cards (7 zones, 3 frictions and 2 actions each, 1 standard, plus
4 whole-kitchen actions, 12 shared root causes, 6 events), typeset with
a family-tinted glyph panel standing in for photography not yet
rendered, plus a true-trim-size print sheet. No new SKU: free and
ungated, the same footing as the Entryway deck.

### Why

The art pipeline was the twice-failed blocker; the card text was
already written and gated, and Kitchen already carries 7 of the 12
videos published to date.

### Verification

`gate_kitchen_deck_rendered`; `audit_visual.py --all`, 0 contrast,
heading, landmark or tap-target findings on both viewports.

### Watch Next

Replace the glyph panels with real photography once Gemini billing is
enabled (`OWNER-ACTIONS.md` 1b, owner gate).

## CHG-2026-0004: Fabricated statistics and dead cross-references removed from the free card corpus

**Date:** 2026-09-04 and 2026-09-10 **Category:** CONTENT **Type:**
FIXED **Impact:** MAJOR **Status:** VERIFIED

### Changed

Two passes: commit `1b9c6c2a` (2026-09-04) stripped fabricated
statistics from the card deck at the same time the retailer-link
disclosure shipped; commit `e7bf6bbe` (2026-09-10) found and fixed a
further 47 dead card cross-references (mostly an "Experts" card family
that was referenced but never authored) and 2 more fabricated
statistics, one already baked into a live download (a "35,000 decisions
a day" claim with no source, commit `a926742b`), plus a second gap in
`gate_unsourced_stats` that had let large comma-formatted numbers and
list-valued fields through the scan entirely.

### Why

`CLAUDE.md` section 8: never a fabricated statistic. A customer-facing
free download had been carrying one, and 20 of 72 already-drawn card
backs pointed at cards that do not exist.

### Verification

`gate_unsourced_stats` (widened), new `gate_card_related_links`
(`ops/tests/test_gate_card_related_links.py`, 10 cases, fail-then-pass
against the real files).

### Customer / Business Impact

The free lead magnet no longer cites an invented number or a dead
reference. Not fixed by text alone: the pixels on the 20 already-drawn
card backs still show the old wording until they are regenerated, a
known, disclosed limitation.

## CHG-2026-0005: A second live checkout charging the wrong price deactivated, and an invented bundle discount corrected

**Date:** 2026-09-06 and 2026-09-04 **Category:** COMMERCE **Type:**
FIXED **Impact:** CRITICAL **Status:** VERIFIED

### Changed

Commit `524bcd0d` (2026-09-06) deactivated a second live Stripe checkout
link charging $18 for a book priced at $9.99 everywhere else; 7 of its
20 lifetime checkouts had been quoted the wrong price. Commit `98bd3a4a`
(2026-09-04) corrected an invented $8.01 saving on the bundle's own
checkout page ("$66" corrected to the real $57.99).

### Why

`CLAUDE.md` section 8 forbids a misleading discount; a live price
discrepancy is a P0 trust and revenue-integrity defect, the same class
of failure as the eight-day dead-payment-link incident CLAUDE.md section
0.2 records.

### Verification

`ops/check_sellable.py --deep`; the price-claim gates in `preflight.py`.

### Customer / Business Impact

No customer since has been able to be quoted either wrong figure.

## CHG-2026-0006: An Etsy listing withdrawn before it could sell a customer the exact content the site gives away free

**Date:** 2026-09-09 **Category:** COMMERCE **Type:** REMOVED
**Impact:** MAJOR **Status:** VERIFIED

### Changed

Commit `e70e3814` withdrew the finished, priced, rendered Etsy listing
L3-entryway, one owner action away from a real shop, after confirming
its content (`RP-ENTRYWAY`) is the identical Entryway set the free deck
already gives away at no cost. New `free_duplicate_skus()` in
`ops/check_etsy.py`, wired into the existing `gate_etsy_listing_valid`,
fails any future listing whose source SKU the catalogue has already
marked free.

### Why

Selling a customer, for money, content the same catalogue gives away
free is the kind of thing a buyer would be right to be angry about on
discovery, per `MARKETPLACE-LISTINGS.md` section 3.1's own stated
principle, which had not previously been checked against this listing.

### Verification

Fail-then-pass proved directly against the pre-fix `etsy-listings.json`.

## CHG-2026-0007: 1,717 honestly disclosed retailer links published across 120 of 123 products

**Date:** 2026-09-04 **Category:** COMMERCE / CONTENT **Type:** ADDED
**Impact:** MODERATE **Status:** VERIFIED

### Changed

Commit `f9a81a63` and the same day's `1b9c6c2a` shipped plain retailer
search links for 120 of 123 catalogue products, each with the affiliate
disclosure required by `CLAUDE.md` section 8 and the affiliate rules in
the operator runbook, ahead of any programme approval (`ops/affiliate.py
--check`, 162 documents).

### Why

`PLAN-AFFILIATE-MONETISATION.md`'s own arithmetic holds affiliate
approval itself for a traffic trigger, but the links and disclosure
needed no such gate, so the moment a programme approves, only the
affiliate tag needs adding, not a page rebuilt.

### Verification

`affiliate.py --check` clean; rendering verified against the retailer's
own grid, per the same commit's own record.

## CHG-2026-0008: Related-reading links differentiated across all 114 zone pages

**Date:** 2026-09-09 (102 non-diagnosed zones) and 2026-09-10 (root-cause mapping fix) **Category:** CONTENT **Type:** IMPROVED
**Impact:** MODERATE **Status:** VERIFIED

### Changed

`general_reading()` in `ops/build_zone_pages.py` now scores each zone's
own published text against the 19 general articles so no two of the 102
non-diagnosed zones share an identical related-reading set (previously
all 102 shared one generic 19-link block). Commit `7eb2f078`
(2026-09-10) found and fixed a follow-on bug once a missing root-cause
mapping was corrected: the cap logic could starve a zone below the
stated 3-link floor; fixed to guarantee the floor over the cap.

### Why

A stranger who reaches a zone page saw the identical reading list as
every other zone, which does not differentiate the page for search or
for the reader.

### Verification

`gate_general_reading_differentiated`; `ops/link_graph_report.py`, 0
orphans introduced.

## CHG-2026-0009: A zone's video title, page title and H1 disagreed; fixed, and a doubled-article schema bug found in the process

**Date:** 2026-09-12 **Category:** DATA / CONTENT **Type:** FIXED
**Impact:** MODERATE **Status:** VERIFIED

### Changed

Commit `c943b9fc` fixed `ops/build_youtube_metadata.py`, which had built
each video's title and description from the raw internal zone key
(contradicting its own docstring's stated reason not to), so a video,
its page's `<title>`, and its `<h1>` could name the same zone three
different ways. Extracted a single `zone_seo_title()` source used by
both. Regenerating to verify surfaced a second, independent, already-live
defect: 113 of 114 zone pages' HowTo JSON-LD read "How to reset the The
[Name]" because 113 of 114 display names already start with "The."
Fixed with a one-line conditional article.

### Why

Inconsistent naming across a video, its landing page, and its structured
data is confusing for a reader and incorrect for search.

### Verification

New `gate_zone_name_consistency` (`ops/tests/test_gate_zone_name_consistency.py`,
6 cases, fail-then-pass). The 12 videos already public on YouTube still
carry the old titles; fixable by Phil directly in YouTube Studio, no
OAuth needed, noted in `OWNER-ACTIONS.md`.

## CHG-2026-0010: An Atom feed shipped, a zero-cost distribution surface needing no account

**Date:** 2026-09-10 **Category:** CONTENT / OPERATIONS **Type:** ADDED
**Impact:** MODERATE **Status:** VERIFIED

### Changed

Commit `14af2e3d` added `ops/build_feed.py`, writing `site/feed.xml`, an
Atom feed of 27 of the site's 29 articles (2 skipped rather than dated by
a git-history guess that would have disagreed with itself between a full
clone and CI's shallow one), wired into `site/articles/index.html` and
`site/llms.txt`.

### Why

`GOALS.md`'s own decision rule: distribution beats production. A feed
needs no account and nothing to enable, unlike every other channel on
the owner-gates table.

### Verification

`gate_feed_current`, re-verified inside a real `git clone --depth 1` to
match CI exactly, after the first push's fallback-date bug was found and
removed.

## CHG-2026-0011: The site linked to its own live YouTube channel, and a false "not filmed yet" claim on method.html was corrected

**Date:** 2026-09-10 **Category:** BUSINESS / CONTENT **Type:** FIXED
**Impact:** MODERATE **Status:** VERIFIED

### Changed

Commit `15a713a6`: the site referenced its own live YouTube channel
(12 real narrated, captioned zone videos) nowhere across 191 pages,
and `site/method.html` told visitors "None of it has been filmed yet,"
a live false claim. Both corrected; the channel added to Organization
JSON-LD's `sameAs` only after the on-site link existed to back it.

### Why

`CLAUDE.md` section 8: a customer-facing page must not state something
false. This one did, after the fact it described had changed.

### Verification

New `gate_sameas_backed_by_onsite_link`, fails in either direction (a
fabricated `sameAs` claim, or a removed link that leaves a stale one).

## CHG-2026-0012: The live MCP distribution channel found serving all 114 zones from a stale, pre-rewrite corpus

**Date:** 2026-09-09 **Category:** INTEGRATION / DATA **Type:** FIXED
**Impact:** MAJOR **Status:** VERIFIED

### Changed

Commit `5a45a312`: `6s-mcp` (deployed 2026-08-31, Watchtower-updated)
had been answering every query from a `mcp/content.json` copy that
never picked up the week's real content work (the Sustain rewrite, the
new `diagnosis` blocks), because `.github/workflows/publish-mcp.yml`
only triggered on a path it never touched. Confirmed by structural diff:
all 114 of 114 zones differed. Re-copied the corpus and fixed the
trigger to also fire on the real source path.

### Why

Every stale query this channel answered since 2026-08-31 used
out-of-date content, an AI-facing distribution surface silently serving
old information.

### Verification

New `gate_mcp_corpus_current`
(`ops/tests/test_gate_mcp_corpus_current.py`, 4 cases, fail-then-pass).

## CHG-2026-0013: The homepage's retired "46 cards" claim for the free deck corrected

**Date:** 2026-09-12 **Category:** CONTENT **Type:** FIXED **Impact:**
MINOR **Status:** VERIFIED

### Changed

Commit `046a1a9d`: `site/index.html`, hand-maintained and generated by
nothing, still told every first-time visitor the free Entryway deck was
"Forty six cards," the retired mockup number corrected everywhere else
five days earlier, and borrowed the six-pass Print Pack framing for a
deck that plays a different, eight-family diagnostic game. Corrected to
the real count (88 cards) and the real framing.

### Why

The homepage is the highest-leverage page a first-time visitor reads;
`gate_deck_count`'s own docstring already named this exact 46-card shape
as the original defect it exists to catch, but the check only parsed
digits, not a spelled-out number, so it could not fire on its own named
case.

### Verification

`check_deck_count()` extended to parse spelled-out cardinals, guarded
against two real false-positive shapes; `ops/tests/test_gate_deck_count.py`
extended 7 to 11 cases, fail-then-pass proved.

------------------------------------------------------------------------

# 106. Standing Instruction

Add a new `CHG-2026-NNNN` entry, in this same section, at or near the
time a material change (section 4) ships, rather than let this file go
silent again. `gate_changelog_current` in `ops/preflight.py` warns once
this file's own "Last updated" date falls too far behind real material
work.
