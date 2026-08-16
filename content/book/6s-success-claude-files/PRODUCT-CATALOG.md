# 6S Success Product Catalog and Commercial Architecture

> Canonical commercial model connecting customer needs to rooms, micro-zones, desired functions, root causes, quests, cards, solutions, products, pricing, fulfillment, economics, recommendations, purchases, and measured outcomes for 6S-success.com.

## 1. Purpose

`PRODUCT-CATALOG.md` defines how 6S Success turns useful home-improvement guidance into relevant products and services without becoming a generic store.

The commercial chain is:

**Person**
→ **Room**
→ **Micro-Zone**
→ **Desired Primary Function**
→ **Root Cause / Friction**
→ **Desired Outcome**
→ **Quest**
→ **Card / Activity**
→ **Solution**
→ **Product / Kit / Service**
→ **Purchase**
→ **Implementation**
→ **Measured Outcome**
→ **Sustainment**

The product catalog must support the customer journey, not interrupt it.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `DATA-CONTRACTS.md`
- `METRICS.md`
- `EXPERIMENTS.md`
- `COST-GOVERNANCE.md`
- `OBSERVABILITY.md`
- `SCHEDULER.md`
- `SEO-AEO.md`
- `CONTENT.md`
- `STATUS.md`
- `BACKLOG.md`
- `DECISIONS.md`
- `LEARNINGS.md`

If a referenced file does not yet exist, do not invent its contents.

---

# 2. Prime Commercial Rule

**Sell the smallest useful solution to a real customer problem.**

Do not start with:

> What can we sell?

Start with:

> What is preventing this person from getting the outcome they want in this specific micro-zone?

Then determine whether a product is actually useful.

---

# 3. Customer Value Before Monetization

A recommendation should improve at least one of:

- function
- organization
- cleanliness
- safety
- accessibility
- speed
- visibility
- capacity
- maintenance
- aesthetics
- family usability
- sustainment

Do not insert products simply because an affiliate link or margin exists.

---

# 4. Commercial Architecture

Canonical hierarchy:

```text
Room
 └── Micro-Zone
      ├── Desired Function
      ├── Root Cause
      ├── Desired Outcome
      ├── Quest
      │    └── Cards / Activities
      ├── Solution
      │    ├── Method
      │    ├── Product
      │    ├── Kit
      │    ├── Printable
      │    ├── Digital Product
      │    ├── 3D Print
      │    └── Service
      └── Sustainment
```

---

# 5. Catalog Source of Truth

There should eventually be one canonical machine-readable catalog.

This Markdown file defines policy and structure.

The operational catalog may live in:

- database
- structured JSON/YAML
- commerce platform
- CMS

Actual architecture must be discovered and documented.

---

# 6. Stable IDs

Every commercial entity should have a stable ID.

Examples:

```text
ROOM-ENTRYWAY
MZ-ENTRYWAY-KEYS
FUNC-FAST-DAILY-EXIT
ROOT-NO-DEDICATED-HOME
OUTCOME-KEYS-IN-ONE-TOUCH
QUEST-ENTRYWAY-KEY-LANDING
CARD-ENTRYWAY-KEYS-001
SOL-KEY-DROP-ZONE
PROD-KEY-TRAY-001
KIT-ENTRYWAY-LAUNCH-001
SERVICE-ENTRYWAY-RESET-001
```

Names may change.

IDs should not.

---

# 7. Room Entity

Suggested:

```yaml
room_id:
name:
description:
primary_household_functions: []
micro_zone_ids: []
status:
```

Initial prototype focus:

`ROOM-ENTRYWAY`

---

# 8. Micro-Zone Entity

A micro-zone is a small functional area that can be independently improved.

Suggested:

```yaml
micro_zone_id:
room_id:
name:
primary_function_options: []
common_root_causes: []
common_outcomes: []
quest_ids: []
solution_ids: []
```

Examples in an Entryway may include:

- keys
- shoes
- coats
- bags
- mail
- incoming items
- outgoing items
- charging
- pet gear
- seasonal gear

Use the canonical master list once verified.

---

# 9. Desired Primary Function

The same physical area can serve different people differently.

Examples:

A bench might primarily support:

- putting on shoes
- bag staging
- child launch
- temporary incoming items
- accessibility/seating

Do not assume one universal "best" setup.

---

# 10. Desired Function Entity

```yaml
function_id:
name:
description:
room_ids: []
micro_zone_ids: []
customer_values: []
success_definition:
```

---

# 11. Personal Values

Desired function can be informed by values such as:

- speed
- simplicity
- calm
- family independence
- aesthetics
- accessibility
- safety
- minimalism
- preparedness
- hospitality
- cleanliness
- sustainability

Values help choose among valid solutions.

They should not be used to manipulate purchases.

---

# 12. Root Cause

Root cause describes why the desired outcome is not happening.

Examples:

- no dedicated home
- home too far from point of use
- insufficient capacity
- too many items
- poor visibility
- difficult access
- unclear ownership
- incompatible household habits
- replenishment failure
- no reset routine
- wrong container
- mixed functions
- excessive steps

---

# 13. Root Cause Entity

```yaml
root_cause_id:
name:
description:
diagnostic_questions: []
common_evidence: []
solution_patterns: []
```

---

# 14. Diagnostic Questions

Questions should reduce ambiguity.

For a key micro-zone:

- Where do keys naturally land today?
- Who uses this area?
- How many active key sets need a home?
- Do keys need to be hidden or visible?
- Is one-handed placement important?
- Are children able to reach the area?
- Is there a recurring "where are my keys?" problem?
- Is the current storage at the point of use?

The answer should influence the solution.

---

# 15. Desired Outcome

Outcomes should be observable.

Weak:

> Better organized keys.

Stronger:

> Every active key set has one obvious home within one step of the normal entry path and can be returned in under five seconds.

---

# 16. Outcome Entity

```yaml
outcome_id:
name:
description:
success_measure:
target:
sustainment_measure:
```

---

# 17. Quest

A quest is a bounded improvement event.

Suggested:

```yaml
quest_id:
room_id:
micro_zone_ids: []
function_ids: []
root_cause_ids: []
target_outcomes: []
estimated_minutes:
player_count:
card_ids: []
solution_ids: []
difficulty:
```

---

# 18. Quest Duration

The product architecture should support the existing Home Quest model of approximately:

- 15 minutes
- 30 minutes
- 45 minutes
- 60 minutes
- 90 minutes

A product recommendation must not be required for every quest.

---

# 19. Card

A card is an actionable unit within a quest/deck.

Suggested:

```yaml
card_id:
deck_id:
room_id:
micro_zone_ids: []
activity_type:
title:
instruction:
estimated_minutes:
required_inputs: []
optional_solution_ids: []
success_condition:
```

---

# 20. 6S Activity Mapping

Cards may map to:

- Sort
- Set in Order
- Shine
- Standardize
- Sustain
- Safety

Commercial recommendations should respect the activity.

Example:

A cleaning product may be relevant to Shine.

A drawer divider may be relevant to Set in Order.

A label may be relevant to Standardize.

---

# 21. Solution

A solution is not necessarily a product.

Solution types:

```text
METHOD
BEHAVIOR
RELOCATION
REDUCTION
LABEL
CONTAINER
ORGANIZER
DIGITAL_TOOL
PRINTABLE
3D_PRINT
KIT
SERVICE
```

Always consider no-purchase solutions first.

---

# 22. Solution Entity

```yaml
solution_id:
name:
solution_type:
description:
applicable_rooms: []
applicable_micro_zones: []
applicable_functions: []
addresses_root_causes: []
supports_outcomes: []
product_ids: []
```

---

# 23. No-Purchase Solution

The catalog must explicitly support:

```yaml
commercial_requirement: NONE
```

Examples:

- move the bowl closer to the door
- eliminate duplicate keys
- assign one hook per person
- stop using the area for unrelated items

Trust is a commercial asset.

---

# 24. Product Types

Potential product types:

- physical organizer
- cleaning supply
- storage container
- label
- 3D printed module
- printable
- digital card deck
- digital guide
- physical card deck
- room reset kit
- micro-zone kit
- service
- subscription/membership
- partner/affiliate product

Only activate categories that genuinely fit the business.

---

# 25. Product Entity

Canonical structure:

```yaml
product_id:
sku:
name:
product_type:
status:
description:
customer_problem:
room_ids: []
micro_zone_ids: []
function_ids: []
root_cause_ids: []
outcome_ids: []
solution_ids: []
price:
currency:
cost:
margin:
fulfillment_type:
inventory_policy:
commerce_product_id:
product_url:
image_assets: []
instructions:
safety_notes:
```

---

# 26. Product Status

Use:

- `IDEA`
- `VALIDATING`
- `ACTIVE`
- `LOW_STOCK`
- `OUT_OF_STOCK`
- `PAUSED`
- `DISCONTINUED`
- `UNKNOWN`

Do not recommend unavailable products as immediately purchasable.

---

# 27. Product Fit

Each product should answer:

1. What problem does it solve?
2. For which micro-zone?
3. For which desired function?
4. Which root cause does it address?
5. What outcome should improve?
6. Why this product instead of a no-cost change?
7. What constraints make it unsuitable?

---

# 28. Recommendation Strength

Use:

## REQUIRED

The activity cannot reasonably be completed without the item.

Use rarely.

## RECOMMENDED

Strong fit for diagnosed problem.

## OPTIONAL

Helpful but not necessary.

## ALTERNATIVE

One of several valid approaches.

## NOT RECOMMENDED

Known mismatch.

---

# 29. Recommendation Reason

Every recommendation should be explainable.

Example:

> Your keys already land on this console, so the issue is not location. The issue is that the landing spot is undefined. A shallow divided tray is optional and can create a visible home without adding another step.

This is better than:

> Buy our key organizer.

---

# 30. Recommendation Confidence

Suggested:

- `HIGH`
- `MEDIUM`
- `LOW`

Confidence may depend on:

- customer answers
- image evidence
- known dimensions
- household constraints
- product compatibility

Low confidence should trigger questions, not aggressive selling.

---

# 31. Compatibility

Physical products should track relevant constraints:

- dimensions
- mounting type
- weight capacity
- moisture resistance
- child safety
- pet safety
- accessibility
- material
- power requirement

Do not recommend a product without required compatibility information.

---

# 32. Measurement Before Purchase

For dimension-sensitive products, prompt the customer to measure first.

Examples:

- drawer organizers
- shelves
- under-sink systems
- Gridfinity modules
- bins

Avoid preventable returns.

---

# 33. Product Bundle

A bundle groups products that solve one coherent problem.

```yaml
bundle_id:
name:
problem:
product_ids: []
bundle_price:
individual_price_total:
customer_savings:
expected_outcome:
```

Do not bundle unrelated products merely to increase AOV.

---

# 34. Micro-Zone Kit

A micro-zone kit should contain the minimum set of inputs needed to reset one small area.

Example:

**Key Landing Kit**

Potential components:

- tray or hooks
- label/visual control
- mounting hardware if applicable
- quick-start card
- QR link to digital quest

Actual kit should be validated.

---

# 35. Room Kit

A room kit combines compatible micro-zone solutions.

Do not create giant kits that force customers to buy solutions for problems they do not have.

Prefer configurable kits where practical.

---

# 36. Quest Kit

A Quest Kit should map directly to a specific quest.

```yaml
quest_id:
kit_id:
required_products: []
optional_products: []
included_cards: []
estimated_completion_time:
```

---

# 37. Digital Product

Potential digital products:

- room deck
- micro-zone mini deck
- printable cards
- reset manual
- checklist
- family quest pack
- labels
- inventory templates

Digital products should have clear delivery and entitlement rules.

---

# 38. Physical Card Deck

Track:

- edition/version
- number of cards
- printing cost
- packaging
- inventory
- fulfillment
- digital companion access

Avoid selling obsolete editions without clear labeling.

---

# 39. 3D Printed Product

For Gridfinity or other modules:

```yaml
product_id:
stl_version:
printer_compatibility:
material:
dimensions:
grid_units:
print_time:
estimated_material_cost:
safety_constraints:
```

Separate downloadable STL from printed physical product.

---

# 40. Service

Service entity:

```yaml
service_id:
name:
service_type:
room_ids: []
micro_zone_ids: []
scope:
estimated_duration:
inputs:
deliverables:
price_model:
service_area:
booking_method:
```

Examples may include:

- Shine service
- Entryway reset
- closet reset
- safety assessment

Only offer services actually operationally available.

---

# 41. Service + Product

Services may recommend/install products.

Keep product cost and service labor transparent where appropriate.

Do not manufacture unnecessary product needs to inflate service revenue.

---

# 42. Affiliate Products

If external products are recommended:

- disclose affiliate relationship where legally/ethically required
- prioritize fit over commission
- verify availability when possible
- avoid misleading pricing
- distinguish 6S Success products from third-party products

---

# 43. Commerce Provider Mapping

Each active product should map to its commerce record.

```yaml
product_id:
commerce_provider:
commerce_product_id:
commerce_variant_id:
price_id:
last_verified:
```

The commerce provider is authoritative for actual transaction state where defined.

---

# 44. SKU

Physical products should use stable SKUs.

Suggested pattern:

```text
6S-ENT-KEY-TRAY-01
```

Do not encode volatile data such as price into SKU.

---

# 45. Product URL

URLs should be stable and descriptive.

Example concept:

```text
/products/entryway-key-landing-kit
```

Do not create multiple thin URLs for trivial variants if it harms UX/SEO.

---

# 46. Product Page Requirements

A useful product page should explain:

- problem
- who it is for
- who it is not for
- desired outcome
- dimensions/compatibility
- what's included
- how to use it
- related quest
- price
- fulfillment
- returns
- safety
- evidence/reviews only when authentic

---

# 47. Product Images

Images should teach.

Useful images:

- product alone
- product in micro-zone
- before/after context
- dimensions
- included components
- installation
- completed standard

Avoid decorative images that obscure function.

---

# 48. Product Instructions

Instructions should connect back to the quest.

Example:

1. clear the micro-zone
2. confirm desired function
3. place/install product
4. assign homes
5. label if needed
6. test normal use
7. define reset rule

---

# 49. Pricing

Price should reflect:

- customer value
- market context
- product cost
- fulfillment
- support
- acquisition
- target margin

Follow `COST-GOVERNANCE.md`.

---

# 50. Margin

Track both revenue and economics.

At minimum:

```yaml
price:
variable_cost:
payment_fee:
fulfillment_cost:
estimated_contribution_margin:
```

Do not optimize recommendation ranking solely for margin.

---

# 51. Inventory

For physical products:

```yaml
inventory_policy:
stock_on_hand:
reorder_point:
target_stock:
lead_time_days:
supplier:
last_verified:
```

Inventory state must come from an authoritative source.

---

# 52. Out-of-Stock Behavior

If unavailable:

1. do not pretend it is available
2. offer valid alternative if one exists
3. allow waitlist/restock notification if supported
4. preserve the no-purchase solution

---

# 53. Fulfillment Types

Examples:

- digital immediate
- print-on-demand
- stocked physical
- 3D printed on demand
- third-party fulfillment
- local service

Each type requires different operational controls.

---

# 54. Shipping

Physical products should expose:

- shipping eligibility
- estimated handling
- shipping cost policy
- tracking availability

Do not promise delivery dates unsupported by fulfillment data.

---

# 55. Returns

Return policy should be explicit.

Use return reasons as product-learning signals.

Common reasons may reveal:

- sizing mismatch
- quality issue
- unclear instructions
- poor recommendation
- expectation mismatch

---

# 56. Product Safety

Relevant products should include safety constraints.

Examples:

- child-accessible mounting
- sharp edges
- load limits
- chemical handling
- electrical use
- trip hazards

Safety outranks conversion.

---

# 57. Recommendation Engine Inputs

Potential inputs:

- room
- micro-zone
- desired function
- personal values
- root cause
- household members
- dimensions
- current items
- quest
- budget preference
- style preference
- safety/accessibility constraints

Collect only information actually needed.

---

# 58. Recommendation Engine Output

Suggested:

```yaml
solution_id:
product_id:
recommendation_strength:
reason:
confidence:
expected_outcome:
required_measurement:
alternatives: []
no_purchase_option:
```

---

# 59. Ranking Principle

Rank primarily by:

1. customer fit
2. outcome likelihood
3. compatibility
4. simplicity
5. cost/value
6. availability

Commercial margin may be a secondary business factor, never the primary hidden determinant.

---

# 60. Recommendation Transparency

Where appropriate explain:

> Why this is being recommended.

This increases trust and gives the customer the ability to reject the assumption.

---

# 61. Budget Preference

Customers may choose:

- use what I have
- low cost
- best value
- premium

Do not equate premium with better outcome automatically.

---

# 62. "Use What You Have" Mode

This should be a first-class mode.

Claude should identify existing household items that can solve the problem before recommending purchases.

This can become a major trust differentiator.

---

# 63. Product Discovery from Root Cause

Example:

```text
Problem:
Shoes accumulate across the entry floor.

Desired Function:
Fast family exit.

Root Cause:
No capacity-limited shoe home near entry.

Possible Solutions:
1. Reduce active shoe quantity.
2. Move existing basket.
3. Add low shoe rack.
4. Add individual family shoe zones.

Product recommendation is conditional on which solution is selected.
```

---

# 64. Product Discovery from Quest

After a quest reveals a missing input, the system may recommend a product.

Example:

> Your 15-minute key quest identified "no dedicated home" as the remaining constraint. Would you like to use something you already own, print a Gridfinity tray, or see a ready-made key landing option?

Commerce follows diagnosis.

---

# 65. Root Cause to Solution Matrix

Maintain machine-readable mappings.

Example:

| Root Cause | Preferred Solution Pattern |
|---|---|
| Too many items | Sort/reduce before storage |
| No dedicated home | Assign/mark location |
| Poor visibility | Open/clear/label |
| Excess steps | Relocate to point of use |
| Insufficient capacity | Reduce or add capacity |
| Mixed functions | Separate zones |
| Reset failure | Standard + sustain routine |

Products should support the solution pattern.

---

# 66. Product Recommendation Timing

Good moments:

- after root cause is identified
- when a card requires an input
- when customer requests a solution
- after measurement confirms fit
- when sustainment identifies a recurring need

Bad moments:

- immediately on every page
- before understanding the problem
- during unrelated learning
- when a free fix is clearly sufficient

---

# 67. Cross-Sell

Cross-sell only when products solve adjacent confirmed needs.

Example:

A key landing kit should not automatically trigger unrelated bathroom products.

---

# 68. Upsell

Upsell should mean better fit, durability, capacity, or convenience.

Do not create artificial inferior products merely to force an upsell.

---

# 69. Post-Purchase Journey

Purchase is not the end.

```text
Purchase
→ Delivery
→ Installation
→ Quest Completion
→ Outcome Check
→ Sustainment
→ Feedback
```

Measure whether the product actually helped.

---

# 70. Outcome Verification

Potential question:

> Did this solution make the area easier to use?

Possible measures:

- time
- clutter recurrence
- search events
- reset effort
- completion
- satisfaction

Do not burden customers with excessive surveys.

---

# 71. Product Success Metrics

Evaluate:

- views
- recommendation rate
- acceptance
- add-to-cart
- checkout
- purchase
- margin
- refund
- outcome success
- repeat use

A product with high conversion but poor outcomes should not be considered successful.

---

# 72. Recommendation Success

Potential metric:

```text
Recommendation Acceptance Rate =
accepted product recommendations / eligible recommendations
```

But pair with outcome quality.

---

# 73. Product Outcome Rate

Potential:

```text
Product Outcome Success Rate =
customers reporting/observing desired outcome /
customers with sufficient follow-up
```

Define in `METRICS.md`.

---

# 74. Product Experiments

Use `EXPERIMENTS.md` for:

- price
- bundles
- recommendation placement
- product copy
- kit composition
- digital vs physical
- "use what you have" flows

Do not run manipulative dark-pattern experiments.

---

# 75. Catalog SEO

Each high-value product/solution should connect naturally to useful educational content.

Potential path:

```text
Question
→ Helpful Micro-Zone Guide
→ Diagnostic
→ Quest
→ Solution
→ Product
```

Avoid thin affiliate/product pages created only for search engines.

---

# 76. Catalog AEO

Answer direct questions clearly.

Examples:

- What should I keep by my front door?
- Where should keys be stored?
- How many pairs of shoes should stay in an entryway?
- What is the best way to organize incoming mail?

Product recommendations may follow the answer, not replace it.

---

# 77. Internal Linking

Useful connections:

- room guide → micro-zone
- micro-zone → root cause
- root cause → quest
- quest → solution
- solution → product
- product → instructions/quest
- product → sustainment

This creates a coherent knowledge-commerce graph.

---

# 78. Product Knowledge Graph

Long-term canonical graph:

```text
ROOM
  ↕
MICRO_ZONE
  ↕
FUNCTION
  ↕
ROOT_CAUSE
  ↕
OUTCOME
  ↕
QUEST
  ↕
CARD
  ↕
SOLUTION
  ↕
PRODUCT
```

This graph should power:

- search
- recommendations
- content
- app
- decks
- commerce
- analytics

---

# 79. Deck Commerce Integration

Physical/digital room decks should not become catalogs.

Instead, cards may include:

- required inputs
- optional solution types
- QR link to personalized solution page
- "use what you have" option
- compatible kit

The deck remains useful without a purchase.

---

# 80. QR Product Journey

Potential:

```text
Card QR
→ Card Detail
→ Confirm Problem
→ Choose Solution Type
→ Use What You Have / DIY / Buy
→ Complete Card
→ Record Outcome
```

---

# 81. Whole-Home Expansion

Do not populate thousands of products immediately.

Expansion sequence:

1. prove Entryway
2. identify high-frequency micro-zone problems
3. validate solution patterns
4. validate product economics
5. standardize catalog schema
6. expand room by room

---

# 82. Entryway Commercial Prototype

Priority commercial categories may include:

- key landing
- shoes
- coats
- bags
- mail/paper
- incoming/outgoing staging
- labels/visual controls
- cleaning/Shine
- safety
- family launch systems

These are hypotheses until validated against the canonical deck and customer evidence.

---

# 83. Entryway Product Ladder

Potential ladder:

```text
Free Guide
↓
Free/Digital Quest
↓
Digital Mini Deck
↓
Printable/Label Pack
↓
Micro-Zone Product
↓
Micro-Zone Kit
↓
Physical Entryway Deck
↓
Entryway Reset Kit
↓
Entryway Service
```

Do not assume every rung must exist.

---

# 84. Product Development Pipeline

Use:

`DISCOVER`
→ `VALIDATE`
→ `DESIGN`
→ `COST`
→ `PROTOTYPE`
→ `TEST`
→ `LAUNCH`
→ `MEASURE`
→ `IMPROVE`
→ `SCALE` or `RETIRE`

---

# 85. Product Idea Score

Potential framework:

```text
Opportunity =
Problem Frequency
× Problem Severity
× Solution Fit
× Customer Willingness
× Strategic Fit
× Confidence
÷ Complexity
```

Margin is important but should not overpower customer value.

---

# 86. Product Validation

Before investing heavily:

- confirm problem
- confirm frequency
- confirm desired outcome
- test no-purchase solution
- test product concept
- estimate economics
- validate usability

---

# 87. Product Retirement

Retire when:

- poor outcome
- poor economics
- safety concern
- repeated returns
- supplier failure
- better solution exists
- no meaningful demand

Preserve redirects and customer entitlements where applicable.

---

# 88. Catalog Versioning

Material catalog changes should be traceable.

Examples:

- product compatibility
- kit composition
- price
- product status
- solution mapping

Use Git/versioned data where appropriate.

---

# 89. Catalog Quality Checks

Automate:

- duplicate IDs
- missing mappings
- orphan products
- invalid prices
- inactive product recommendations
- missing images
- missing safety data
- broken URLs
- stale inventory
- invalid commerce IDs

---

# 90. Catalog Freshness

Track:

```yaml
last_catalog_sync:
last_inventory_sync:
last_price_sync:
last_commerce_verification:
```

Stale inventory/price data should not be presented as verified.

---

# 91. Commerce Reconciliation

Periodically reconcile:

**Catalog**
↔ **Commerce Provider**
↔ **Website**
↔ **Orders**

Detect:

- missing products
- wrong prices
- disabled products still linked
- invalid variants
- broken checkout mappings

---

# 92. Product Agent Responsibilities

The product/catalog agent should:

- maintain mappings
- identify gaps
- analyze product performance
- propose products
- detect stale catalog data
- improve recommendations
- coordinate with content/SEO/commerce

It may not create unapproved financial commitments.

---

# 93. Commerce Agent Responsibilities

Commerce agent should:

- verify product state
- verify pricing
- monitor checkout
- reconcile orders
- monitor refunds
- detect commerce anomalies

Authority follows `AUTONOMY.md`.

---

# 94. Content Agent Responsibilities

Content should teach the solution independent of the product.

It may surface relevant product options after value is established.

---

# 95. SEO/AEO Agent Responsibilities

SEO/AEO should identify customer questions and demand.

It should not invent products merely because a keyword has volume.

---

# 96. Analytics Agent Responsibilities

Analytics should connect:

```text
Content
→ Diagnostic
→ Quest
→ Recommendation
→ Product
→ Purchase
→ Outcome
```

without overstating attribution.

---

# 97. Cost Agent Responsibilities

Use `COST-GOVERNANCE.md` to calculate:

- product cost
- contribution margin
- inventory exposure
- fulfillment cost
- acquisition economics

---

# 98. Scheduler Integration

Suggested jobs:

## Daily

- commerce availability
- stale inventory
- broken product links

## Weekly

- product funnel
- recommendations
- refunds
- catalog gaps
- Entryway opportunities

## Monthly

- unit economics
- product portfolio
- retirement candidates
- supplier/fulfillment review

Follow `SCHEDULER.md`.

---

# 99. Executive Product Dashboard

Display:

## Catalog

- active products
- active kits
- active services
- catalog freshness

## Revenue

- revenue by product
- revenue by room
- revenue by micro-zone
- AOV

## Economics

- contribution margin
- refunds
- inventory exposure

## Customer

- recommendation acceptance
- outcome success
- quest-to-purchase

## Opportunities

- high-frequency unsolved root causes
- missing products
- products to improve/retire

---

# 100. Product Decision Request

When owner approval is required:

## Opportunity

Customer problem.

## Evidence

Observed demand/root cause.

## Proposed Product

What it is.

## Customer Outcome

What improves.

## Economics

Price, estimated cost, margin, investment.

## Risk

Inventory, supplier, safety, complexity.

## Test

Smallest validation.

## Decision

Exact approval needed.

---

# 101. Current Catalog State

Populate from verified evidence:

```yaml
catalog:
  canonical_store: UNKNOWN
  schema_version: UNKNOWN
  last_verified: UNKNOWN

rooms:
  entryway:
    room_id: UNKNOWN
    micro_zone_count: UNKNOWN
    quest_count: UNKNOWN
    card_count: UNKNOWN

commerce:
  provider: UNKNOWN
  product_count: UNKNOWN
  active_product_count: UNKNOWN
  last_reconciled: UNKNOWN

products:
  digital: UNKNOWN
  physical: UNKNOWN
  kits: UNKNOWN
  services: UNKNOWN
  third_party: UNKNOWN

inventory:
  source_of_truth: UNKNOWN
  last_sync: UNKNOWN

recommendations:
  engine: UNKNOWN
  explainability: UNKNOWN
  no_purchase_option: UNKNOWN

economics:
  contribution_margin_available: UNKNOWN
  product_cost_data: UNKNOWN

analytics:
  quest_to_product_tracking: UNKNOWN
  product_outcome_tracking: UNKNOWN
```

Never replace `UNKNOWN` with assumptions.

---

# 102. First Catalog Mission

Once Claude has legitimate access to website, repository, commerce, and existing product data:

1. inventory existing products
2. inventory existing Entryway micro-zones
3. inventory quests/cards
4. establish stable IDs
5. map products to solutions
6. map solutions to root causes
7. map root causes to desired functions/outcomes
8. identify no-purchase alternatives
9. verify commerce IDs/prices
10. verify inventory/availability
11. calculate initial economics
12. identify orphan products
13. identify unsolved high-value root causes
14. connect analytics
15. update Current Catalog State
16. create prioritized product backlog

Do not create products or purchase inventory during discovery.

---

# 103. Minimum Viable Catalog

Before aggressive commerce automation:

1. stable product IDs
2. stable micro-zone IDs
3. solution mappings
4. root-cause mappings
5. authoritative prices
6. authoritative availability
7. basic economics
8. product instructions
9. compatibility constraints
10. no-purchase option
11. analytics
12. commerce reconciliation

---

# 104. Catalog Maturity Model

## Level 0 — Store

Products are listed without structured customer-problem mapping.

## Level 1 — Organized

Products map to rooms and micro-zones.

## Level 2 — Diagnostic

Products map to desired functions and root causes.

## Level 3 — Outcome-Based

Recommendations are tied to measurable outcomes and quests.

## Level 4 — Adaptive

Recommendations improve from customer behavior, outcomes, compatibility, and economics.

## Level 5 — Autonomous Commercial System

6S Success continuously discovers customer problems, validates solution patterns, creates or sources appropriate products, measures outcomes and economics, improves the catalog, and scales only solutions that genuinely help customers.

---

# 105. Non-Negotiable Catalog Rules

Claude and subagents must not:

- recommend products solely because they have higher margin
- hide a clearly sufficient no-cost solution
- invent product availability
- invent price
- invent reviews
- fabricate demand
- recommend dimension-sensitive products without compatibility consideration
- sell unsafe products
- purchase inventory without authority
- create deceptive scarcity
- create fake discounts
- use dark patterns
- confuse revenue with customer success
- mass-create low-value products for SEO
- recommend inactive products as available
- allow catalog IDs to drift across systems
- optimize AOV at the expense of trust

---

# 106. Final Principle

6S Success should not become a store that happens to have organizing content.

It should become a **home operating system that understands what a person wants an area to do, diagnoses what prevents that outcome, guides the person through a small achievable quest, and offers the right solution only when a product genuinely helps.**

The commercial engine should understand:

**What room are we improving?**

**Which micro-zone matters?**

**What does this person want it to do?**

**Why is it not working now?**

**What outcome would success look like?**

**What is the smallest useful quest?**

**Can the problem be solved with what they already own?**

**If not, what solution is the best fit?**

**Is there a 6S Success product, kit, printable, 3D print, deck, or service that helps?**

**Did the purchase actually improve the outcome?**

When those relationships become structured data, the same commercial architecture can power the **website, smartphone app, physical decks, digital decks, personalized quests, SEO/AEO content, recommendation engine, 3D-print ecosystem, services, and executive dashboard**.

That is the purpose of `PRODUCT-CATALOG.md`.
