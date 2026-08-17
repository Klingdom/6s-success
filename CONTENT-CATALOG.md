# CONTENT-CATALOG.md

## 6S Success Canonical Content, Knowledge, Page, Card, and Asset Catalog Standard

**Document role:** Canonical content inventory, governance, reuse,
lifecycle, and publishing specification for 6S Success\
**Status:** ACTIVE\
**Owner:** Founder / Owner\
**Operational steward:** Claude Code autonomous operating system\
**Primary domain agents:** Content, Product, Home Quest, SEO/AEO,
Book/Editorial, Services, Commerce, Data, Brand, GitHub/DevOps as
applicable\
**Last updated:** 2026-08-17

------------------------------------------------------------------------

# 1. Purpose

`CONTENT-CATALOG.md` defines the source-of-truth architecture for the
large and growing body of 6S Success content.

The catalog must answer:

> **What content exists, what customer problem does it solve, where is
> it used, what canonical knowledge does it depend on, what other assets
> derive from it, how current is it, how well does it perform, and what
> should be created, updated, reused, consolidated, retired, or tested
> next?**

6S Success already contains substantial content R&D across:

-   the 6S Success Home Edition book;
-   Room Reset Manuals;
-   whole-home room and micro-zone guidance;
-   Entryway Home Quest cards;
-   quest/activity instructions;
-   cleaning and organization processes;
-   product and procurement guidance;
-   service offerings;
-   labeling and inventory systems;
-   3D-printing/Gridfinity concepts;
-   app guidance;
-   website pages;
-   LinkedIn/social content;
-   marketing and business materials;
-   visual/illustration plans;
-   educational content;
-   autonomous operating documentation.

This file prevents those assets from becoming disconnected copies.

------------------------------------------------------------------------

# 2. Core Principle

6S Success should create **canonical knowledge once and express it many
ways**.

``` text
CANONICAL KNOWLEDGE
        ↓
CONTENT MODULE
        ↓
┌────────────┬────────────┬────────────┬────────────┐
CARD         APP          WEBSITE      BOOK
QUEST        SERVICE      SOCIAL       EMAIL
LABEL        PRODUCT      VIDEO        TRAINING
```

Do not independently rewrite the same 6S method for every channel when a
reusable content object can drive them all.

------------------------------------------------------------------------

# 3. Content Is a Product System

Content is not merely marketing.

In 6S Success, content can:

``` text
teach
diagnose
instruct
motivate
guide
verify
standardize
sustain
sell
support
convert
retain
reduce service labor
reduce agent hallucination
```

Therefore content should be structured, versioned, measurable, and
connected to customer outcomes.

------------------------------------------------------------------------

# 4. Relationship to Canonical Files

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
CHANGELOG.md
```

Content must not silently contradict these sources.

------------------------------------------------------------------------

# 5. Content Catalog Scope

Canonical content types include:

``` text
KNOWLEDGE_MODULE
ROOM_GUIDE
MICRO_ZONE_GUIDE
6S_ACTIVITY
CARD
QUEST_TEMPLATE
QUEST_INSTRUCTION
VERIFICATION_GUIDE
SUSTAIN_GUIDE
SAFETY_GUIDE
CLEANING_PROCESS
ORGANIZATION_PROCESS
PRODUCT_GUIDE
KIT_GUIDE
SERVICE_GUIDE
LABEL_TEMPLATE
INVENTORY_GUIDE
APP_HELP
FAQ
WEBSITE_PAGE
LANDING_PAGE
SEO_PAGE
AEO_ANSWER
BLOG_ARTICLE
SOCIAL_POST
LINKEDIN_POST
EMAIL
BOOK_CHAPTER
BOOK_SECTION
ROOM_RESET_MANUAL
ILLUSTRATION_PLAN
FIGURE
INFOGRAPHIC
PHOTO_ASSET
LINE_DRAWING
VIDEO_SCRIPT
TRAINING_MODULE
CASE_STUDY
TESTIMONIAL
SALES_ASSET
EXECUTIVE_ASSET
INTERNAL_STANDARD
PROMPT
OTHER
```

------------------------------------------------------------------------

# 6. Stable Content Identity

Every canonical content object should have a stable ID.

Recommended:

``` text
CNT-000001
CNT-000002
...
```

Specialized content can additionally use human-readable IDs:

``` text
ROOM-ENTRYWAY
MZ-ENTRYWAY-KEYS
CARD-ENTRYWAY-KEYS-01
QUEST-ENTRYWAY-30M-01
FIG-47-23
POST-LI-0001
```

Human-readable IDs do not replace the canonical content ID.

------------------------------------------------------------------------

# 7. Content Record Schema

``` yaml
content:
  content_id:
  status:
  content_type:
  title:
  short_title:
  canonical_topic:
  purpose:
  audience:
  customer_problem:
  desired_outcome:
  six_s_steps:
  rooms:
  micro_zones:
  functions:
  requirement_ids:
  card_ids:
  quest_ids:
  product_ids:
  service_ids:
  related_content_ids:
  parent_content_id:
  source_content_ids:
  derivative_content_ids:
  channel:
  format:
  language:
  reading_level:
  estimated_duration:
  owner:
  author_agent:
  source_file:
  source_location:
  published_location:
  version:
  evidence_level:
  validation_status:
  safety_review:
  brand_review:
  seo_metadata:
  performance_metrics:
  created_at:
  updated_at:
  reviewed_at:
  expires_at:
  superseded_by:
  provenance:
```

Implementation may normalize fields into related tables.

------------------------------------------------------------------------

# 8. Content Status

Use:

``` text
IDEA
DRAFT
REVIEW
APPROVED
ACTIVE
PUBLISHED
TESTING
NEEDS_UPDATE
STALE
SUPERSEDED
RETIRED
ARCHIVED
REJECTED
```

Do not delete historical content merely because it is superseded.

------------------------------------------------------------------------

# 9. Canonical vs Derivative Content

## Canonical Content

The authoritative explanation or instruction.

## Derivative Content

A channel-specific expression of canonical content.

Example:

``` text
CANONICAL:
How to reset an Entryway key micro-zone.

DERIVATIVES:
Home Quest card
app instruction
website guide
LinkedIn post
book sidebar
service checklist
label
short video script
```

Derivatives should reference their canonical source.

------------------------------------------------------------------------

# 10. Content Dependency Graph

Recommended relationship:

``` text
ROOM
 ↓
MICRO-ZONE
 ↓
DESIRED FUNCTION
 ↓
PROBLEM / GAP
 ↓
ROOT-CAUSE CANDIDATES
 ↓
6S COUNTERMEASURES
 ↓
ACTIVITY
 ↓
CARD
 ↓
QUEST
 ↓
PRODUCT / SUPPLY
 ↓
VERIFICATION
 ↓
SUSTAIN
```

Content channels render this graph differently.

------------------------------------------------------------------------

# 11. Whole-Home Content Architecture

The whole-home system should not be a pile of room pages.

Use reusable layers:

``` text
LEVEL 1 — 6S PRINCIPLES
LEVEL 2 — HOUSEHOLD FUNCTIONS
LEVEL 3 — ROOM
LEVEL 4 — MICRO-ZONE
LEVEL 5 — CURRENT-STATE PATTERN
LEVEL 6 — COUNTERMEASURE
LEVEL 7 — ACTIVITY/CARD
LEVEL 8 — QUEST
LEVEL 9 — PRODUCT/SUPPLY
LEVEL 10 — VERIFICATION
LEVEL 11 — SUSTAIN
```

------------------------------------------------------------------------

# 12. Room Content

Each room should have a canonical room object containing:

``` text
room purpose
common desired functions
micro-zones
common failure patterns
priority safety considerations
high-value 6S opportunities
recommended quest types
verification patterns
sustain patterns
```

Room content should link to reusable micro-zone and activity content
rather than duplicating it.

------------------------------------------------------------------------

# 13. Micro-Zone Content

The micro-zone is a critical reusable content unit.

Each micro-zone should define:

``` yaml
micro_zone:
  id:
  room:
  name:
  desired_functions:
  common_items:
  common_current_states:
  root_cause_candidates:
  sort_actions:
  set_in_order_actions:
  shine_actions:
  standardize_actions:
  sustain_actions:
  safety_actions:
  product_classes:
  verification:
  sustain:
```

------------------------------------------------------------------------

# 14. Current-State Pattern Library

Photo analysis and manual diagnosis should use a shared pattern library.

Examples:

``` text
overfilled
mixed categories
no defined home
hidden inventory
duplicate inventory
dirty surface
blocked access
unsafe placement
excess travel
poor frequency-of-use placement
no visual control
no replenishment standard
```

Patterns should not assert root cause automatically.

------------------------------------------------------------------------

# 15. Desired-Function Library

Content should lead with function rather than aesthetics.

Examples:

``` text
keys are easy to drop and retrieve
shoes are contained without blocking walking
mail has a clear processing path
clean towels are accessible
medications are appropriately controlled
frequently used utensils are easy to reach
consumables are visible before they run out
```

------------------------------------------------------------------------

# 16. 6S Activity Library

Activities should be reusable across rooms.

Example:

``` text
remove expired items
group like items
define a home
set quantity limit
label location
wipe surface
move high-frequency items forward
create replenishment trigger
photograph standard state
```

Room-specific cards compose these primitives.

------------------------------------------------------------------------

# 17. Home Quest Card Catalog

The Home Quest card system is a major content surface.

Each card should include:

``` yaml
card:
  card_id:
  content_id:
  room:
  micro_zone:
  six_s_step:
  activity:
  desired_outcome:
  estimated_minutes:
  difficulty:
  player_count:
  supplies:
  optional_products:
  instructions:
  verification:
  sustain:
  safety:
  points_or_game_logic:
  front_asset:
  back_asset:
  status:
  validation:
```

------------------------------------------------------------------------

# 18. Entryway Prototype

The Entryway deck remains the first major Home Quest validation
environment.

Existing R&D includes:

-   Entryway room card;
-   micro-zone cards;
-   6S activity cards;
-   front/back prototypes;
-   LinkedIn card-sharing messages;
-   digital and physical beta concepts;
-   quest generation from cards;
-   individual, assigned, voluntary, and random selection concepts;
-   15--90 minute event construction;
-   multiplayer concepts;
-   escape-room/game concepts.

These assets should be cataloged rather than recreated.

------------------------------------------------------------------------

# 19. Quest Content

A quest is a composition of content objects.

``` text
QUEST
├── objective
├── duration
├── player configuration
├── cards
├── instructions
├── supplies
├── verification
└── sustain follow-up
```

Quest generation should reference content IDs so improvements propagate.

------------------------------------------------------------------------

# 20. Quest Duration

Existing target range:

``` text
15
30
45
60
90 minutes
```

Content should be tagged with realistic estimated duration and later
updated from observed completion data.

------------------------------------------------------------------------

# 21. Multiplayer Content

The smartphone-app requirements envision roughly 1--10 simultaneous
players.

Content metadata should support:

``` text
solo
pair
family
team
assigned
voluntary
random
competitive
cooperative
```

Game mechanics should remain optional.

------------------------------------------------------------------------

# 22. Verification Content

Every meaningful activity should define what "done" means.

Potential verification:

``` text
photo
count
location confirmation
surface clear
items categorized
label present
capacity limit established
customer confirmation
before/after comparison
```

Completion alone is not sufficient evidence of outcome.

------------------------------------------------------------------------

# 23. Sustain Content

Sustain should be explicit.

Potential:

``` text
reset trigger
daily check
weekly check
replenishment point
label
visual standard
photo standard
owner
review cadence
```

Content without Sustain guidance is incomplete for many 6S use cases.

------------------------------------------------------------------------

# 24. Safety Content

Safety content may address:

``` text
chemicals
electrical areas
ladders/reaching
sharp objects
medications
child access
elder accessibility
heavy objects
trip hazards
food safety
moisture/mold indicators
```

Use conservative language and appropriate escalation to professionals.

------------------------------------------------------------------------

# 25. Cleaning Content

Cleaning processes should define:

``` text
surface
soil/problem
tool
product class
sequence
frequency
safety
verification
```

Do not create unsafe chemical combinations.

------------------------------------------------------------------------

# 26. Organization Content

Organization content should follow:

``` text
SORT
 ↓
GROUP
 ↓
MEASURE
 ↓
SELECT HOME
 ↓
CONTAIN IF NEEDED
 ↓
LABEL / VISUAL CONTROL
 ↓
VERIFY
 ↓
SUSTAIN
```

Avoid "buy bins first" content.

------------------------------------------------------------------------

# 27. Product Content Integration

`PRODUCT-CATALOG.md` is authoritative for product identity, economics,
sourcing, and substitutions.

Content may explain:

``` text
why product class helps
where it fits
how to measure
how to use
alternatives
maintenance
```

Do not hard-code volatile retailer prices into evergreen content unless
the page is explicitly price-driven and refreshed.

------------------------------------------------------------------------

# 28. Service Content

Existing service R&D includes:

``` text
Shine / cleaning
one-time cleaning
recurring cleaning
decluttering
organization
micro-zone resets
kitchen
bathroom
closet
safety
visual controls
related home improvement/support concepts
```

Service content should define:

``` text
customer problem
scope
inputs
activities
deliverables
expected outcome
duration
products/supplies
exclusions
verification
upsell only where relevant
```

------------------------------------------------------------------------

# 29. Book Content

The 6S Success Home Edition book is a major canonical editorial system.

Audience:

``` text
young professionals and families
approximately 18–36 target reader
```

Editorial intent:

``` text
human-readable
warm
confident
home-focused
minimal Lean jargon
practical
visual
```

Book content should be connected to the same canonical household
knowledge used by the app and Home Quest.

------------------------------------------------------------------------

# 30. Room Reset Manuals

The Room Reset Manual series extends the book into room-specific
execution.

Existing work includes chapters in the 30s and 40s and extensive
illustration plans.

Catalog each chapter, section, figure, and room/micro-zone relationship.

------------------------------------------------------------------------

# 31. Editorial Voice

Canonical voice:

> Write like a compassionate Lean Six Sigma Master Black Belt with deep
> real-world experience, but explain household improvement like a useful
> human, not a consultant.

Avoid:

-   AI slop;
-   generic motivational filler;
-   unnecessary Lean jargon;
-   repetitive "transform your space" language;
-   overlong setup before practical advice;
-   em dashes.

------------------------------------------------------------------------

# 32. Visual House Style

Established Home Edition visual direction includes:

``` text
Scandinavian middle-class homes
warm sunlight
oak
white walls
natural textiles
plants
soft shadows
real people
whitespace
```

Palette:

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

Visual inspiration includes the clarity and information density
associated with DK-style reference publishing, IKEA-like instruction
clarity, clean editorial product photography, and warm lifestyle
editorial presentation.

Do not copy protected third-party artwork.

------------------------------------------------------------------------

# 33. Figure Catalog

Every book/manual figure should have:

``` yaml
figure:
  figure_id:
  chapter:
  title:
  purpose:
  source_plan:
  status:
  image_ref:
  visual_type:
  room:
  micro_zone:
  content_ids:
  version:
  approved:
```

Existing production rules include figure numbering such as:

``` text
Figure 47-01
Figure 47-02
...
```

Do not skip, merge, reorder, or silently replace figures when following
an approved illustration plan.

------------------------------------------------------------------------

# 34. Photo-to-Line-Drawing Workflow

Recent Room Reset Manual visual work uses:

``` text
hyper-realistic photo concept
      ↓
hyper-realistic line-drawing illustration
```

Catalog source concept and final illustration separately but link them.

------------------------------------------------------------------------

# 35. Website Content

The 6S Success website should derive pages from canonical knowledge
where practical.

Potential page classes:

``` text
home
how it works
room
micro-zone
6S method
Home Quest
service
product/kit
beta
book
resource
FAQ
about
contact
```

------------------------------------------------------------------------

# 36. SEO Content

SEO pages must provide real customer value.

Good page target:

``` text
specific problem
specific room/micro-zone
clear desired function
useful actions
verification
next step
```

Avoid mass-producing thin combinations solely for keyword coverage.

------------------------------------------------------------------------

# 37. AEO Content

Answer-engine content should provide concise, self-contained answers to
household questions while linking back to deeper canonical content.

Examples:

``` text
Where should towels be stored in a small bathroom?
How should I organize keys by the front door?
What should go under a bathroom sink?
What are the best supplies for a laundry-room reset?
```

------------------------------------------------------------------------

# 38. Social Content

Social posts are derivative content, not canonical truth.

Current LinkedIn patterns include:

-   6S Home Quest card reveals;
-   practical household 6S replies;
-   beta invitations;
-   cleaning/organization insights;
-   process improvement analogies;
-   product/service development updates.

Posts should point toward a useful action, insight, beta, product,
service, or deeper resource.

------------------------------------------------------------------------

# 39. LinkedIn Style

Preferred:

``` text
one clear idea
crisp sentences
human language
minimal jargon
specific example
clear relevance
brief CTA when appropriate
```

Avoid AI clichés and inflated claims.

------------------------------------------------------------------------

# 40. Email Content

Email should be event/lifecycle driven where possible.

Potential:

``` text
welcome
first quest
quest reminder
sustain check
beta feedback
service follow-up
kit follow-up
content recommendation
```

Avoid sending generic volume simply because content exists.

------------------------------------------------------------------------

# 41. App Content

App content should prioritize action.

UI instruction hierarchy:

``` text
WHAT TO DO
WHY
HOW
SUPPLIES
DONE WHEN
SAFETY
```

Do not paste book paragraphs into the app.

------------------------------------------------------------------------

# 42. Photo Analysis Content

The system should separate:

``` text
OBSERVED CONDITION
LIKELY INTERPRETATION
ROOT-CAUSE CANDIDATES
CUSTOMER CONFIRMATION
RECOMMENDED 6S ACTION
```

This protects against false certainty.

------------------------------------------------------------------------

# 43. Inventory Content

Inventory guidance should support:

``` text
identify item
primary function
room
micro-zone
keep
donate
move
store
container guidance
UPC
quantity
min/max
replenishment
```

------------------------------------------------------------------------

# 44. Label Content

Label content types:

``` text
location
category
quantity limit
QR inventory
min/max
maintenance
reset standard
safety
```

Label text should be short and readable.

------------------------------------------------------------------------

# 45. Content Reuse Model

Example:

``` text
Canonical micro-zone:
ENTRYWAY / KEYS

Can generate:
• app diagnosis
• Home Quest card
• 15-minute quest
• room guide section
• website article
• LinkedIn post
• label
• product recommendation
• service checklist
• book sidebar
• verification prompt
• sustain reminder
```

The system should track all derivatives.

------------------------------------------------------------------------

# 46. Content Composition

Prefer composable blocks.

Examples:

``` text
instruction block
safety block
verification block
product block
sustain block
root-cause block
```

This enables consistent reuse without copy-paste drift.

------------------------------------------------------------------------

# 47. Content Provenance

Every important content object should know:

``` text
who/what created it
source research
source artifact
owner directive
validation evidence
last review
```

AI-generated content without provenance should not silently become
canonical.

------------------------------------------------------------------------

# 48. Evidence Level

Use:

``` text
EXPERT_DESIGN
RESEARCH_SUPPORTED
INTERNAL_TESTED
CUSTOMER_OBSERVED
CUSTOMER_VALIDATED
OUTCOME_VALIDATED
```

Not every household instruction requires formal experimentation, but
evidence should be represented honestly.

------------------------------------------------------------------------

# 49. Content Validation

Potential validation signals:

``` text
customer completes activity
customer understands instruction
time estimate accurate
outcome verified
sustain achieved
low correction rate
low skip rate
positive qualitative feedback
```

Views alone are weak validation for instructional content.

------------------------------------------------------------------------

# 50. Content Performance

Metrics depend on type.

Potential:

``` text
view
qualified view
scroll/read completion
CTA
quest start
quest completion
instruction correction
card skip
outcome verification
sustain
signup
lead
purchase
service booking
```

Do not compare unlike content using one vanity score.

------------------------------------------------------------------------

# 51. Content Outcome Attribution

Where possible:

``` text
CONTENT VIEW
  ↓
ACTION
  ↓
QUEST / SERVICE / PURCHASE
  ↓
OUTCOME
```

Use cautious attribution.

A page view does not prove causal impact.

------------------------------------------------------------------------

# 52. Content Freshness

Content can become stale due to:

``` text
product changes
price changes
app changes
service changes
strategy changes
new learning
safety changes
room taxonomy changes
superseded card
broken link
```

Store `reviewed_at` and, where useful, `expires_at`.

------------------------------------------------------------------------

# 53. Freshness Priority

Refresh more frequently when content is:

``` text
high traffic
high conversion
safety-related
product-price dependent
app-instruction dependent
service/pricing dependent
strategically important
```

Evergreen principles can refresh less frequently.

------------------------------------------------------------------------

# 54. Duplicate Content Detection

Autonomous checks should identify:

``` text
same topic with conflicting guidance
duplicate room pages
duplicate card instructions
old product references
multiple definitions of 6S
stale service offers
orphan illustrations
```

Prefer consolidation over uncontrolled growth.

------------------------------------------------------------------------

# 55. Supersession

When content is replaced:

``` yaml
status: SUPERSEDED
superseded_by: CNT-...
reason:
effective_at:
```

Published destinations should redirect/update where appropriate.

------------------------------------------------------------------------

# 56. Content Deletion

Do not delete historical content required for:

``` text
audit
old quest history
book version
customer record
experiment interpretation
decision provenance
```

Archive instead.

------------------------------------------------------------------------

# 57. Content Safety Review

Require stronger review for:

``` text
chemical guidance
electrical guidance
child safety
medication storage
elder safety
heavy storage
ladder/reaching
food safety
mold/contamination
```

Do not imply professional expertise outside actual scope.

------------------------------------------------------------------------

# 58. Accessibility

Content should account for:

``` text
mobility
reach
vision
reading
cognition
time
strength
household composition
```

Avoid assuming everyone can kneel, lift, climb, or complete the same
task duration.

------------------------------------------------------------------------

# 59. Brand Consistency

Every external content asset should preserve:

``` text
6S Success
Simple systems. Better living.
supportive practical tone
clear visual hierarchy
realistic homes
non-judgmental current-state language
```

The system should help users improve, not shame them for clutter.

------------------------------------------------------------------------

# 60. Content and Commerce Separation

Instructional content must remain useful even when no purchase occurs.

A healthy page/card can say:

``` text
Use the tray you already own.
```

Do not turn every micro-zone guide into an affiliate funnel.

------------------------------------------------------------------------

# 61. Product Link Governance

When content references a specific product:

``` text
reference product_id
resolve current preferred source dynamically where possible
show substitute criteria
```

Avoid permanent retailer URLs embedded throughout static content.

------------------------------------------------------------------------

# 62. Service Link Governance

Service descriptions should reference canonical service IDs and current
commercial definitions rather than duplicating pricing/scope in many
places.

------------------------------------------------------------------------

# 63. Content-to-Risk

Relevant risks include:

``` text
content quantity over quality
brand dilution
unsafe guidance
stale product information
AI overconfidence
commerce damaging trust
duplicate sources of truth
```

Material content risks should link to `RISKS.md`.

------------------------------------------------------------------------

# 64. Content-to-Incident

Potential content incidents:

``` text
unsafe instruction published
private image exposed
wrong product instruction at scale
broken app guidance blocks quest
material false claim
mass publication of corrupted content
```

Use `INCIDENTS.md` when severity warrants.

------------------------------------------------------------------------

# 65. Content-to-Experiment

High-value experiments may compare:

``` text
card wording
instruction length
photo vs text
video vs static
checklist vs quest
different duration framing
different CTA
different sustain prompt
different product timing
```

Measure downstream behavior.

------------------------------------------------------------------------

# 66. Content-to-Learning

Validated content learning should update the canonical source, then
propagate to derivatives.

Do not manually patch every derivative if the system can regenerate
safely.

------------------------------------------------------------------------

# 67. Content-to-Changelog

Meaningful public or canonical content changes belong in `CHANGELOG.md`.

Examples:

``` text
Entryway card standard changed
new room guide released
service scope changed
safety guidance corrected
book chapter materially revised
```

------------------------------------------------------------------------

# 68. Content Production Workflow

``` text
NEED
 ↓
CANONICAL SOURCE CHECK
 ↓
REUSE / UPDATE / CREATE
 ↓
DRAFT
 ↓
FACT / SAFETY / BRAND REVIEW
 ↓
APPROVE
 ↓
PUBLISH
 ↓
MEASURE
 ↓
LEARN
 ↓
UPDATE / RETIRE
```

Always check for existing content before creating another version.

------------------------------------------------------------------------

# 69. Autonomous Content Authority

Claude may autonomously within policy:

-   inventory content;
-   identify duplicates;
-   draft derivatives;
-   update metadata;
-   flag stale assets;
-   generate internal briefs;
-   propose SEO/AEO opportunities;
-   create experiments;
-   prepare content updates;
-   propagate approved canonical changes to authorized destinations.

Protected actions may include:

-   material brand repositioning;
-   major public claims;
-   legal/safety-sensitive publication;
-   irreversible mass deletion;
-   paid campaigns/spend;
-   commercial pricing changes;
-   owner-attributed statements beyond authority.

Follow `AUTONOMY.md`.

------------------------------------------------------------------------

# 70. Content Agent Responsibilities

## Content Agent

Canonical writing and reuse.

## Home Quest Agent

Cards, quests, verification, Sustain.

## Product Agent

Product guidance accuracy.

## Service Agent

Service scope and delivery content.

## SEO/AEO Agent

Search/answer discoverability.

## Book/Editorial Agent

Long-form editorial system.

## Visual Agent

Figures, diagrams, imagery, brand execution.

## Data Agent

Catalog integrity and performance.

## DevOps Agent

Publishing systems and reliability.

------------------------------------------------------------------------

# 71. Content Backlog Prioritization

Score opportunities by:

``` text
customer pain
strategic relevance
Entryway validation value
reuse potential
search demand
conversion potential
content gap
effort
risk
```

Near-term priority should favor content that helps prove the product.

------------------------------------------------------------------------

# 72. Current Strategic Content Priority

The next content objective is not "publish everything for every room."

It is:

``` text
MAKE ENTRYWAY EXCELLENT
      ↓
LEARN WHAT USERS NEED
      ↓
STANDARDIZE REUSABLE CONTENT OBJECTS
      ↓
EXPAND TO NEXT HIGH-VALUE ROOMS
```

------------------------------------------------------------------------

# 73. Entryway Content Acceptance Criteria

Entryway content should eventually cover:

``` text
room overview
all prototype micro-zones
desired functions
common current states
6S activities
cards
quest compositions
15–90 minute options
solo/group options
supplies
product-free alternatives
verification
sustain
safety
beta feedback
```

------------------------------------------------------------------------

# 74. Whole-Home Master Card List

Existing whole-home card-list R&D should be treated as a major catalog
input.

It should eventually map every card to:

``` text
room
micro-zone
6S step
activity
duration
difficulty
players
products
verification
sustain
```

Do not rebuild the master list from memory if the actual artifact is
available.

------------------------------------------------------------------------

# 75. Existing Entryway Card List

The existing Entryway deck card-list artifacts are canonical migration
inputs.

Preserve card names, relationships, and prototype status when migrating
into structured records.

------------------------------------------------------------------------

# 76. Book Migration

Existing completed chapters and illustration plans should be inventoried
with:

``` text
chapter
section
figure
status
source file
canonical topics
room/micro-zone links
```

Do not regenerate chapters merely to populate the catalog.

------------------------------------------------------------------------

# 77. Illustration Migration

Existing figures should be inventoried from actual artifacts/files.

Do not assume a figure exists merely because an illustration plan called
for it.

Use:

``` text
PLANNED
GENERATED
REVIEWED
APPROVED
SUPERSEDED
```

------------------------------------------------------------------------

# 78. Website Migration

Inventory actual published pages and compare them against canonical
content.

Classify:

``` text
KEEP
UPDATE
MERGE
REDIRECT
REMOVE
CREATE
```

------------------------------------------------------------------------

# 79. Social Migration

Do not attempt to catalog every historic social sentence as a canonical
asset.

Catalog:

``` text
campaign
post
source topic
CTA
publication date
performance
reusable learning
```

Prioritize current/high-value content.

------------------------------------------------------------------------

# 80. Content Catalog Views

Useful views:

``` text
BY ROOM
BY MICRO-ZONE
BY 6S STEP
BY CONTENT TYPE
BY CHANNEL
BY STATUS
BY FRESHNESS
BY PERFORMANCE
BY PRODUCT
BY SERVICE
BY CARD
BY QUEST
BY BOOK CHAPTER
BY RISK
```

------------------------------------------------------------------------

# 81. Content Coverage Matrix

Recommended:

  --------------------------------------------------------------------------------------
  Room     Micro-Zones    Guides     Cards    Quests    Product   Verification   Sustain
                                                       Guidance                
  ------ ------------- --------- --------- --------- ---------- -------------- ---------

  --------------------------------------------------------------------------------------

Generate from data.

------------------------------------------------------------------------

# 82. Micro-Zone Coverage Matrix

  -------------------------------------------------------------------------------------------
  Micro-Zone   Desired    Guide   Card    Quest   Product   Verification   Sustain   Status
               Function                                                              
  ------------ ---------- ------- ------- ------- --------- -------------- --------- --------

  -------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 83. Channel Coverage Matrix

  ----------------------------------------------------------------------------
  Canonical   App      Card     Web      Book     Social   Service   Product
  Topic                                                              
  ----------- -------- -------- -------- -------- -------- --------- ---------

  ----------------------------------------------------------------------------

Missing channel coverage is not automatically a gap. Create only where
useful.

------------------------------------------------------------------------

# 84. Content Dashboard

Potential executive/content metrics:

``` text
canonical content objects
Entryway coverage
stale high-priority content
duplicate/conflicting content
card completion
instruction correction
content-assisted quest starts
verified outcomes
sustain
qualified organic traffic
beta conversion
content-to-service lead
content-to-product conversion
```

Do not put raw content volume on the executive dashboard unless it
serves a decision.

------------------------------------------------------------------------

# 85. Content Quality Metrics

Potential:

``` text
instruction completion
skip rate
correction rate
time-estimate accuracy
verification rate
sustain rate
customer helpfulness
search engagement
CTA conversion
```

Definitions belong in `METRICS.md`.

------------------------------------------------------------------------

# 86. Content Graph

Recommended graph relationships:

``` text
CONTENT SUPPORTS FUNCTION
CONTENT APPLIES_TO ROOM
CONTENT APPLIES_TO MICRO_ZONE
CONTENT USES ACTIVITY
CONTENT REQUIRES PRODUCT_CLASS
CONTENT DERIVES_FROM CONTENT
CONTENT SUPERSEDES CONTENT
CONTENT SUPPORTS SERVICE
CONTENT IMPLEMENTS LEARNING
CONTENT TESTED_BY EXPERIMENT
```

------------------------------------------------------------------------

# 87. Content API / Service Boundary

Potential capabilities:

``` text
get content
search content
get canonical source
get derivatives
get room content
get micro-zone content
get card
get quest content
get verification
get sustain
get product guidance
get stale content
get content performance
```

------------------------------------------------------------------------

# 88. Content Events

Potential:

``` text
content.created
content.approved
content.published
content.updated
content.stale
content.superseded
content.retired
content.performance_changed
content.validation_changed
```

Avoid triggering expensive autonomous work on trivial edits.

------------------------------------------------------------------------

# 89. Content Integrity Checks

Automated checks should eventually detect:

``` text
missing content IDs
broken parent relationships
orphan cards
orphan figures
missing room/micro-zone mappings
invalid product IDs
superseded source still published
conflicting canonical instructions
stale safety content
broken destinations
missing provenance
duplicate canonical topics
```

------------------------------------------------------------------------

# 90. Canonical Topic Ownership

One canonical object should own each core instruction.

Example:

``` text
How to establish a home for keys
```

may be reused everywhere, but should not have five competing canonical
versions.

------------------------------------------------------------------------

# 91. Content Versioning

Material revisions increment version.

Historical published versions may be retained when needed for:

``` text
book editions
quest history
experiments
customer records
audit
```

------------------------------------------------------------------------

# 92. Content Localization

The architecture should allow future language/localization support
without mixing translated text into canonical IDs.

Use:

``` text
content_id
locale
translation_status
source_version
```

Do not prioritize localization before demand.

------------------------------------------------------------------------

# 93. Content Personalization

Future personalization may adapt:

``` text
room type
micro-zone
household size
children
pets
mobility/accessibility
time available
products already owned
player count
budget
```

Personalization should compose approved content, not invent unsafe
instructions.

------------------------------------------------------------------------

# 94. Content and AI Generation

Generative AI can:

``` text
compose
summarize
adapt tone
select relevant modules
create quest narrative
personalize sequence
```

AI should not silently alter canonical safety, product, or outcome
logic.

------------------------------------------------------------------------

# 95. Near-Real-Time Content Improvement

When enough usage exists:

``` text
USER ACTION
 ↓
CONTENT ID
 ↓
COMPLETION / SKIP / CORRECTION
 ↓
OUTCOME
 ↓
SUSTAIN
 ↓
CONTENT PERFORMANCE
 ↓
EXPERIMENT / UPDATE
```

This creates a continuously improving content system.

------------------------------------------------------------------------

# 96. Customer Feedback Integration

Feedback should attach to the content object used.

Examples:

``` text
instruction unclear
too long
missing supply
wrong time estimate
not applicable
product unnecessary
worked well
```

Aggregate patterns before rewriting canonical content.

------------------------------------------------------------------------

# 97. Content Experiment Guardrails

Do not experiment with unsafe variants merely for engagement.

Safety, privacy, legal, and critical product constraints remain fixed
guardrails.

------------------------------------------------------------------------

# 98. Content Cost Control

Do not regenerate thousands of assets after every small canonical edit.

Use dependency impact analysis.

``` text
CHANGE
 ↓
AFFECTED DERIVATIVES
 ↓
MATERIAL?
 ↓
REGENERATE ONLY WHAT IS NEEDED
```

------------------------------------------------------------------------

# 99. Content Anti-Patterns

Never:

-   create duplicate canonical guidance without checking the catalog;
-   mass-generate thin SEO pages;
-   treat views as proof of customer value;
-   embed stale prices throughout evergreen content;
-   rewrite product truth outside `PRODUCT-CATALOG.md`;
-   present AI root-cause guesses as facts;
-   omit verification and Sustain from action content where they matter;
-   shame customers for clutter;
-   copy third-party editorial/artwork;
-   regenerate existing book/card assets from memory when actual files
    exist;
-   publish unreviewed safety-sensitive content;
-   create content because an agent has idle capacity;
-   measure success by number of pages/posts/cards alone;
-   allow channel-specific copy to become conflicting canonical truth.

------------------------------------------------------------------------

# 100. Content Record Template

``` markdown
# CNT-XXXXXX — [Title]

**Type:**  
**Status:**  
**Canonical topic:**  
**Audience:**  
**Room:**  
**Micro-zone:**  
**6S step:**  
**Version:**  

## Purpose

## Customer Problem

## Desired Outcome

## Canonical Content

## Products / Supplies

## Verification

## Sustain

## Safety

## Source / Provenance

## Derivatives

## Validation

## Performance

## Change History
```

------------------------------------------------------------------------

# 101. Card Record Template

``` markdown
# [CARD-ID] — [Card Name]

**Room:**  
**Micro-zone:**  
**6S step:**  
**Minutes:**  
**Players:**  
**Status:**  

## Objective

## Instructions

## Supplies

## Product-Free Alternative

## Done When

## Sustain

## Safety

## Front Asset

## Back Asset

## Validation
```

------------------------------------------------------------------------

# 102. Room Record Template

``` markdown
# [ROOM-ID] — [Room]

## Purpose

## Desired Functions

## Micro-Zones

## Common Current States

## Priority 6S Opportunities

## Cards

## Quests

## Products

## Verification

## Sustain

## Safety

## Related Book / Web / Service Content
```

------------------------------------------------------------------------

# 103. Initial Catalog Baseline

``` yaml
content_catalog:
  stage: INVENTORY_NORMALIZATION_AND_VALIDATION
  strongest_existing_domains:
    - 6S Home Edition book
    - Room Reset Manuals
    - Entryway Home Quest
    - whole-home micro-zone/card research
    - cleaning and organization processes
    - service architecture
    - product/procurement guidance
    - labeling/inventory
    - Gridfinity/3D printing
    - website/social marketing
  immediate_focus:
    - Entryway canonical content
    - reusable micro-zone schema
    - card/quest content IDs
    - product-content linkage
    - verification and Sustain
    - actual artifact inventory
```

------------------------------------------------------------------------

# 104. Migration Strategy

Do not populate the catalog from conversational memory alone.

Use actual source artifacts.

Sequence:

``` text
1. inventory available 6S Success files
2. identify canonical/current versions
3. classify by content type
4. assign stable content IDs
5. map rooms/micro-zones
6. map 6S steps
7. map products/services
8. identify canonical vs derivative
9. identify duplicates/conflicts
10. preserve provenance
11. flag stale/superseded assets
12. validate Entryway first
13. expand systematically
```

------------------------------------------------------------------------

# 105. Migration Priority

## P0

``` text
Entryway card list
Entryway deck assets
Entryway quest content
whole-home master card list
V9 product linkages
core room/micro-zone taxonomy
```

## P1

``` text
Room Reset Manuals
book chapters
illustration plans/figures
services
inventory/label content
```

## P2

``` text
website
SEO/AEO
social
marketing derivatives
```

------------------------------------------------------------------------

# 106. Do Not Invent Missing Assets

If an illustration plan references Figure 47-23 but the actual generated
image cannot be found:

``` text
status = PLANNED or UNKNOWN
```

Do not mark it generated from memory.

The same rule applies to cards, pages, chapters, and other assets.

------------------------------------------------------------------------

# 107. Current Content Strategy

The content system should now shift from:

``` text
MORE CONTENT
```

toward:

``` text
BETTER STRUCTURE
+
ENTRYWAY VALIDATION
+
REUSE
+
MEASUREMENT
+
CONTROLLED EXPANSION
```

The organization already has enough R&D to begin learning which content
actually changes household behavior.

------------------------------------------------------------------------

# 108. Entryway Learning Loop

``` text
ENTRYWAY CONTENT
      ↓
REAL USER
      ↓
CARD / QUEST
      ↓
COMPLETION
      ↓
VERIFIED OUTCOME
      ↓
SUSTAIN
      ↓
FEEDBACK
      ↓
CONTENT UPDATE
      ↓
RETEST
```

This should become the template for every future room.

------------------------------------------------------------------------

# 109. Whole-Home Expansion

After Entryway evidence is strong enough:

``` text
SELECT NEXT ROOM
 ↓
REUSE CONTENT PRIMITIVES
 ↓
ADD ROOM-SPECIFIC KNOWLEDGE
 ↓
TEST
 ↓
VALIDATE
 ↓
EXPAND
```

Do not simply publish every researched room at once.

------------------------------------------------------------------------

# 110. Final Principle

6S Success has the potential to become a large household knowledge
system, but the value is not the number of pages, cards, chapters,
figures, or posts.

The value is the connection:

``` text
RIGHT CONTENT
   ↓
RIGHT PERSON
   ↓
RIGHT MICRO-ZONE
   ↓
RIGHT MOMENT
   ↓
CLEAR ACTION
   ↓
MINIMUM NECESSARY SUPPLIES
   ↓
VERIFIED BETTER STATE
   ↓
SUSTAINED BETTER STATE
```

The catalog should make every major 6S Success asset discoverable,
reusable, measurable, governable, and improvable.

**Create canonical knowledge once. Reuse it intelligently. Measure
whether it helps. Improve what matters. Retire what does not.**
