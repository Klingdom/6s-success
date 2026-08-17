# PRODUCT-CATALOG.md

## 6S Success Canonical Product, Supply, Kit, and Procurement Catalog Standard

**Document role:** Canonical product-data and procurement
source-of-truth specification for 6S Success\
**Status:** ACTIVE\
**Owner:** Founder / Owner\
**Operational steward:** Claude Code autonomous operating system\
**Primary domain agents:** Product, Procurement/Commerce, Data, Content,
Home Quest, Services, GitHub/DevOps as applicable\
**Last updated:** 2026-08-17

------------------------------------------------------------------------

# 1. Purpose

`PRODUCT-CATALOG.md` defines the canonical architecture for every
physical product, cleaning supply, organization supply, storage
solution, label, consumable, safety item, 3D-printed component, service
kit component, Home Quest supply, and commercial bundle used or
recommended by 6S Success.

It exists to answer:

> **What product is this, what household problem does it solve, where
> should it be used, which 6S activity requires it, how much is needed,
> what can substitute for it, what does it cost, what should the
> customer pay, and is the recommendation still current?**

This file is the governance layer for the product catalog.

Structured product records should ultimately live in a machine-readable
catalog/database and be synchronized with this standard.

------------------------------------------------------------------------

# 2. Existing Procurement Baseline

The current 6S Success procurement work already includes an important
canonical artifact:

``` text
6S_Success_Whole_Home_Tiered_Procurement_Master_V9.html
```

V9 was derived from the earlier canonical V8 procurement master and
includes:

``` text
117-product procurement master
156-requirement mapping
$199 commercial tier
$299 commercial tier
$499 commercial tier
exact quantities
BOM economics
fallback/substitute products
affiliate-readiness fields
requirement coverage
margin/retail-price fields
```

That artifact remains the baseline procurement dataset until its records
are migrated into the canonical catalog architecture defined here.

Do not discard, silently replace, or rebuild the V9 data from memory.

Migration must preserve IDs, quantities, economics, requirements,
substitutions, and provenance.

------------------------------------------------------------------------

# 3. Product Philosophy

6S Success does not exist to sell household products.

Products exist to help a household achieve and sustain a desired
function.

Canonical logic:

``` text
DESIRED FUNCTION
      ↓
CURRENT GAP
      ↓
ROOT-CAUSE CANDIDATE
      ↓
6S COUNTERMEASURE
      ↓
DO WE NEED A PRODUCT?
      ↓
NO → USE / REPURPOSE WHAT EXISTS
YES → SELECT MINIMUM ADEQUATE PRODUCT
      ↓
VERIFY OUTCOME
      ↓
SUSTAIN
```

A product recommendation is a countermeasure, not the goal.

------------------------------------------------------------------------

# 4. Recommendation Hierarchy

Use this hierarchy whenever possible:

``` text
1. Use an adequate item already owned
2. Repurpose an existing item
3. Use a simple/inexpensive generic solution
4. Recommend a specific product class
5. Recommend a specific product
6. Offer a curated kit/bundle when it materially reduces friction
7. Offer premium/specialized solution only when justified
```

Commerce must not override customer value.

------------------------------------------------------------------------

# 5. Catalog Scope

The catalog includes:

``` text
CLEANING_SUPPLY
CLEANING_TOOL
ORGANIZER
CONTAINER
BIN
BASKET
DRAWER_INSERT
SHELF
RACK
HOOK
HANGER
TRAY
TURNTABLE
LABEL
LABEL_PRINTER
QR_LABEL
CONSUMABLE
SAFETY_PRODUCT
CHILD_SAFETY_PRODUCT
ACCESSIBILITY_PRODUCT
MAINTENANCE_SUPPLY
LAUNDRY_PRODUCT
KITCHEN_PRODUCT
BATHROOM_PRODUCT
ENTRYWAY_PRODUCT
OFFICE_PRODUCT
CLOSET_PRODUCT
GARAGE_PRODUCT
WHOLE_HOME_PRODUCT
3D_PRINTED_MODULE
GRIDFINITY_MODULE
CARD_DECK_COMPONENT
SERVICE_SUPPLY
KIT_COMPONENT
BUNDLE
DIGITAL_PRODUCT_REFERENCE
OTHER
```

------------------------------------------------------------------------

# 6. Canonical Product Identity

Every catalog item requires a stable internal ID.

Recommended:

``` text
PRD-000001
PRD-000002
...
```

Never use:

``` text
Amazon ASIN
UPC
retailer SKU
manufacturer SKU
product name
URL
```

as the canonical primary key.

Those values can change or be retailer-specific.

------------------------------------------------------------------------

# 7. Product Record Schema

``` yaml
product:
  product_id:
  status:
  canonical_name:
  short_name:
  product_type:
  product_class:
  description:
  primary_function:
  secondary_functions:
  six_s_steps:
  rooms:
  micro_zones:
  requirements:
  card_ids:
  quest_types:
  service_ids:
  kit_ids:
  recommended_for:
  not_recommended_for:
  safety_notes:
  accessibility_notes:
  dimensions:
  capacity:
  material:
  color_options:
  quantity_unit:
  default_quantity:
  min_quantity:
  max_quantity:
  consumable:
  reusable:
  upc:
  manufacturer:
  manufacturer_model:
  retailer_options:
  preferred_source:
  affiliate_eligible:
  affiliate_program:
  acquisition_cost:
  landed_cost:
  target_retail:
  gross_margin:
  margin_percent:
  price_last_verified:
  availability_status:
  availability_last_verified:
  substitute_product_ids:
  substitute_class:
  quality_tier:
  commercial_tier:
  image_refs:
  instructions_ref:
  source_provenance:
  confidence:
  created_at:
  updated_at:
  reviewed_at:
```

Fields may be normalized into related tables in implementation.

------------------------------------------------------------------------

# 8. Product Status

Use:

``` text
CANDIDATE
TESTING
APPROVED
PREFERRED
ACTIVE
LIMITED
OUT_OF_STOCK
DISCONTINUED
SUPERSEDED
REJECTED
ARCHIVED
```

A product should not become `PREFERRED` merely because it appears in a
retailer search.

------------------------------------------------------------------------

# 9. Product Class vs Specific Product

Separate the functional need from the retailer item.

Example:

``` text
PRODUCT CLASS:
11-inch under-sink turntable

SPECIFIC PRODUCT:
[manufacturer/model/retailer listing]
```

Cards and quests should depend on product classes whenever possible.

This reduces retailer lock-in and substitution failures.

------------------------------------------------------------------------

# 10. Functional Taxonomy

Every product should answer:

``` text
WHAT FUNCTION DOES THIS ENABLE?
```

Examples:

``` text
contain
separate
divide
label
identify
limit
store vertically
store by frequency of use
clean
disinfect
wipe
scrub
dry
protect
stage
transport
replenish
prevent spill
prevent child access
reduce trip hazard
create visual control
maintain min/max
```

------------------------------------------------------------------------

# 11. 6S Mapping

Map products to one or more 6S steps:

``` text
SORT
SET_IN_ORDER
SHINE
STANDARDIZE
SUSTAIN
SAFETY
```

Examples:

``` text
donation bag → SORT
drawer divider → SET_IN_ORDER
microfiber cloth → SHINE
label → STANDARDIZE
min/max card → SUSTAIN
child lock → SAFETY
```

------------------------------------------------------------------------

# 12. Room Taxonomy

Products may map to:

``` text
ENTRYWAY
MUDROOM
KITCHEN
PANTRY
DINING
LIVING_ROOM
FAMILY_ROOM
PRIMARY_BEDROOM
CHILD_BEDROOM
GUEST_BEDROOM
PRIMARY_BATHROOM
BATHROOM
LAUNDRY
HOME_OFFICE
CLOSET
LINEN_CLOSET
UTILITY
GARAGE
BASEMENT
ATTIC
OUTDOOR
WHOLE_HOME
```

Use canonical room IDs in the implementation.

------------------------------------------------------------------------

# 13. Micro-Zone Mapping

The product system should map to the established whole-home micro-zone
architecture.

Examples:

``` text
entryway keys
entryway shoes
entryway bags
entryway mail
entryway coats
bathroom countertop
medicine cabinet
bathroom drawers
under sink
towel storage
laundry detergent zone
laundry sorting
desk writing tools
desk cables
pantry cans
pantry snacks
kitchen utensils
junk drawer
closet hanging
closet folded clothing
```

Do not create product-specific micro-zone names when an existing
canonical zone applies.

------------------------------------------------------------------------

# 14. Requirement Mapping

The existing procurement baseline contains **156 mapped requirements**.

Each requirement should receive a stable ID:

``` text
REQ-0001
...
```

The catalog should preserve:

``` text
requirement
room
micro-zone
desired function
required/optional
covered_by_product_ids
covered_by_kit_ids
fallback
verification method
```

This prevents kits from appearing complete while leaving functional
requirements uncovered.

------------------------------------------------------------------------

# 15. Card Mapping

Home Quest cards should specify product needs through:

``` text
REQUIRED
OPTIONAL
SUBSTITUTE_ALLOWED
HOUSEHOLD_ITEM
NO_PRODUCT_REQUIRED
```

Cards should reference `product_class` or `product_id`, not embed
retailer URLs as logic.

------------------------------------------------------------------------

# 16. Quest Mapping

At quest generation time, the system should calculate:

``` text
products already owned
products needed
acceptable substitutes
optional products
consumables
estimated quantity
```

A quest should not be blocked unnecessarily because the customer lacks a
preferred commercial product.

------------------------------------------------------------------------

# 17. Photo Analysis Integration

Photo analysis may identify:

``` text
visible item class
possible organizer need
possible storage capacity issue
possible cleaning need
possible safety concern
```

It must not automatically conclude that a purchase is necessary.

Recommended flow:

``` text
PHOTO
 ↓
OBSERVED CONDITION
 ↓
DESIRED FUNCTION
 ↓
COUNTERMEASURE
 ↓
EXISTING ITEM CHECK
 ↓
PRODUCT NEED IF CONFIRMED
```

------------------------------------------------------------------------

# 18. Customer Inventory Integration

The smartphone inventory concept should allow:

``` text
photo identification
UPC scan
item function
room
micro-zone
keep
donate
move
store
quantity
storage container
min/max
reorder
```

The customer's owned-item catalog and the commercial product catalog are
related but distinct datasets.

------------------------------------------------------------------------

# 19. UPC

UPC is an external identifier.

Use it for:

``` text
recognition
inventory intake
replenishment
product matching
```

Do not assume every product has a UPC.

3D-printed and generic household solutions may not.

------------------------------------------------------------------------

# 20. Consumables

Consumables require additional fields:

``` yaml
consumable:
  current_quantity:
  minimum:
  target:
  maximum:
  reorder_point:
  reorder_quantity:
  unit:
  expected_usage_rate:
  last_replenished:
```

Customer-specific quantities belong in customer inventory, not the
global product master.

------------------------------------------------------------------------

# 21. Min/Max System

For household consumables:

``` text
MAX = desired stocked quantity
MIN = replenishment trigger
CURRENT = observed/recorded quantity
```

Recommended state:

``` text
CURRENT > MIN → OK
CURRENT <= MIN → REPLENISH
CURRENT > MAX → OVERSTOCK
```

The system may recommend reorder.

It must not purchase without explicit authority.

------------------------------------------------------------------------

# 22. Label Ecosystem

Catalog label-related products separately:

``` text
Phomemo M02-compatible labels
category labels
location labels
QR inventory labels
min/max labels
visual-control labels
maintenance labels
expiration/review labels
```

Label content itself belongs in content/data systems; label
stock/printers belong here.

------------------------------------------------------------------------

# 23. 3D Printing

The catalog should support 3D-printable products.

Fields:

``` yaml
printable:
  design_id:
  stl_ref:
  source_file_ref:
  version:
  gridfinity_units:
  dimensions:
  material:
  printer_profile:
  print_time_estimate:
  filament_estimate:
  tested_printer:
  test_status:
```

Current R&D includes Bambu Lab-compatible whole-home Gridfinity concepts
and a key-tray module.

------------------------------------------------------------------------

# 24. Gridfinity

Use Gridfinity where modularity provides value.

Potential high-value areas:

``` text
entryway
desk/office
bathroom drawers
kitchen drawers
utility drawers
craft/tool micro-zones
```

Do not force Gridfinity into zones where a simple bin/basket is better.

------------------------------------------------------------------------

# 25. Cleaning Product Architecture

Cleaning recommendations should separate:

``` text
chemical
tool
surface compatibility
task
safety
frequency
```

Never recommend unsafe chemical combinations.

Manufacturer instructions remain authoritative for product use.

------------------------------------------------------------------------

# 26. Organization Product Architecture

Organization products should be selected based on:

``` text
item type
quantity
dimensions
access frequency
visibility need
available space
user reach/accessibility
cleanability
budget
```

Do not recommend containers before sorting unnecessary items.

------------------------------------------------------------------------

# 27. Storage Sizing

Where possible:

``` text
MEASURE ITEMS
+
MEASURE AVAILABLE SPACE
+
ALLOW ACCESS CLEARANCE
=
VALID STORAGE SOLUTION
```

Avoid recommending organizers solely from visual appearance.

------------------------------------------------------------------------

# 28. Product Quality Tiers

Use:

``` text
VALUE
STANDARD
PREMIUM
SPECIALTY
```

Quality tier is independent from commercial kit tier.

------------------------------------------------------------------------

# 29. Commercial Kit Tiers

Current procurement architecture:

``` text
$199
$299
$499
```

These are commercial hypotheses requiring validation.

Each kit should have a stable ID:

``` text
KIT-199-001
KIT-299-001
KIT-499-001
```

Actual price may evolve. Do not encode price as the only identity.

------------------------------------------------------------------------

# 30. Nested Kit Principle

Higher tiers should generally contain the functional value of lower
tiers plus meaningful additional coverage/capability.

Validate nesting explicitly.

Do not create higher tiers by adding arbitrary products merely to reach
a price.

------------------------------------------------------------------------

# 31. Kit Record Schema

``` yaml
kit:
  kit_id:
  name:
  status:
  tier:
  target_customer:
  target_outcome:
  rooms:
  micro_zones:
  requirements_covered:
  product_lines:
  total_units:
  bom_cost:
  landed_cost:
  packaging_cost:
  fulfillment_cost:
  target_retail:
  gross_profit:
  gross_margin_percent:
  affiliate_equivalent:
  substitutions:
  coverage_score:
  last_cost_refresh:
  last_availability_refresh:
  validation_status:
```

------------------------------------------------------------------------

# 32. Kit Line Schema

``` yaml
kit_line:
  kit_id:
  product_id:
  quantity:
  required:
  substitution_group:
  unit_cost:
  extended_cost:
```

------------------------------------------------------------------------

# 33. BOM Calculation

``` text
EXTENDED COST = UNIT LANDED COST × QUANTITY

KIT BOM = SUM(EXTENDED COST)

TRUE KIT COST =
BOM
+ PACKAGING
+ INBOUND FREIGHT
+ PICK/PACK
+ PAYMENT COST
+ SHIPPING SUBSIDY
+ EXPECTED RETURNS/LOSS
+ OTHER VARIABLE COSTS
```

Do not calculate margin from product purchase price alone if fulfillment
costs are material.

------------------------------------------------------------------------

# 34. Gross Margin

``` text
GROSS PROFIT = NET REVENUE - VARIABLE COST

GROSS MARGIN % = GROSS PROFIT / NET REVENUE
```

Canonical revenue definitions must align with `METRICS.md`.

------------------------------------------------------------------------

# 35. Procurement Strategy

Early-stage preferred sequence:

``` text
recommendation / affiliate
       ↓
small curated bundle
       ↓
preorder / limited inventory
       ↓
validated recurring demand
       ↓
inventory commitment
```

Avoid large inventory purchases before demand evidence.

------------------------------------------------------------------------

# 36. Source Types

Products may come from:

``` text
MANUFACTURER
DISTRIBUTOR
WHOLESALER
RETAILER
MARKETPLACE
AFFILIATE
LOCAL_SOURCE
3D_PRINT
CUSTOM
HOUSEHOLD_EXISTING
```

------------------------------------------------------------------------

# 37. Retailer Record

``` yaml
retailer_option:
  retailer:
  retailer_sku:
  url_ref:
  price:
  shipping:
  availability:
  affiliate:
  affiliate_ref:
  verified_at:
```

URLs and prices are volatile data and should be refreshed rather than
treated as permanent truth.

------------------------------------------------------------------------

# 38. Preferred Source

A preferred source should optimize:

``` text
fit
quality
availability
cost
customer convenience
returns
reliability
affiliate economics
```

Affiliate commission is not the primary selection criterion.

------------------------------------------------------------------------

# 39. Affiliate Readiness

The existing V9 fields should migrate.

Potential fields:

``` text
affiliate_eligible
program
tracking_ready
commission_type
destination_verified
last_verified
```

Never recommend an inferior item merely because it pays commission.

------------------------------------------------------------------------

# 40. Substitution

Every important product should define either:

``` text
specific substitutes
or
functional substitution criteria
```

Example:

``` text
Preferred:
11-inch turntable

Substitute criteria:
10–12 inch diameter
fits measured cabinet
raised rim
washable
appropriate load capacity
```

------------------------------------------------------------------------

# 41. Substitution Groups

Use stable IDs:

``` text
SUB-UNDER-SINK-TURNTABLE-01
SUB-DRAWER-DIVIDER-01
```

A kit line can reference a substitution group rather than one fragile
SKU.

------------------------------------------------------------------------

# 42. Availability

Use:

``` text
IN_STOCK
LOW_STOCK
BACKORDER
OUT_OF_STOCK
DISCONTINUED
UNKNOWN
```

Always store verification timestamp.

------------------------------------------------------------------------

# 43. Price Freshness

Use explicit freshness.

Example:

``` yaml
price:
  amount: 12.99
  currency: USD
  verified_at: 2026-08-17T...
```

Do not describe old procurement prices as current.

------------------------------------------------------------------------

# 44. Product Freshness

A product can become stale because:

``` text
listing changed
dimensions changed
model changed
price changed
retailer changed
availability changed
quality changed
affiliate destination changed
```

Schedule refresh proportional to importance and volatility.

------------------------------------------------------------------------

# 45. Product Validation

Validation levels:

``` text
RESEARCHED
DESIGN_RECOMMENDED
PROCUREMENT_VERIFIED
PHYSICALLY_TESTED
CUSTOMER_TESTED
OUTCOME_VALIDATED
```

Do not equate research with customer validation.

------------------------------------------------------------------------

# 46. Preferred Product Criteria

To become `PREFERRED`, an item should generally demonstrate:

``` text
functional fit
reasonable availability
acceptable cost
quality
substitution path
safe use
customer usability
```

High-volume/high-risk items should have stronger validation.

------------------------------------------------------------------------

# 47. Product Score

Optional decision-support score:

``` text
FUNCTIONAL_FIT
QUALITY
VALUE
AVAILABILITY
VERSATILITY
SPACE_EFFICIENCY
EASE_OF_USE
CLEANABILITY
SUSTAINABILITY_OF_SYSTEM
```

Do not allow one composite score to hide a safety or fit failure.

------------------------------------------------------------------------

# 48. Existing Bathroom R&D

Preserve tested/researched concepts such as:

``` text
one-sink bathroom standard
countertop
medicine cabinet
drawers
under-sink
smaller stacked under-sink slide-out storage
approximately 11-inch Lazy Susan/turntable
standardized drawer organizers
towel storage
```

These should migrate into product classes and requirement mappings
rather than remain isolated notes.

------------------------------------------------------------------------

# 49. Existing Laundry R&D

Laundry catalog should cover common cleaning/organization supplies and
micro-zone needs such as:

``` text
sorting
detergent
stain treatment
dryer supplies
lint
cleaning
hanging
folding
lost-item containment
replenishment
visual control
```

------------------------------------------------------------------------

# 50. Entryway R&D

Entryway is the first product-validation environment.

Likely product classes include:

``` text
key tray/hooks
shoe containment
coat hooks/hangers
bag storage
mail sorter
donation/outgoing bin
umbrella containment
cleaning supplies
labels
visual controls
safety solutions
```

The Entryway quest system should validate which of these are actually
necessary.

------------------------------------------------------------------------

# 51. Office / Desk R&D

Potential product classes:

``` text
writing-tool modules
cable management
charging
document staging
drawer organization
Gridfinity modules
labels
small-item containment
```

------------------------------------------------------------------------

# 52. Kitchen R&D

Product selection should support the kitchen process, not generic
organizer accumulation.

Prioritize:

``` text
workflow
frequency of use
food safety
cleanability
visibility
inventory
min/max
container fit
```

------------------------------------------------------------------------

# 53. Whole-Home Reuse

A major catalog objective is to minimize unique SKUs.

Prefer products that work across multiple zones when they fit well.

Examples:

``` text
standard bins
standard drawer dividers
standard labels
standard microfiber cloths
standard hooks
```

Measure SKU reuse across requirements.

------------------------------------------------------------------------

# 54. Standardization vs Fit

Do not standardize a product merely to reduce SKU count if it performs
poorly in a zone.

Use:

``` text
STANDARD WHERE POSSIBLE
ZONE-SPECIFIC WHERE NECESSARY
```

------------------------------------------------------------------------

# 55. Product-to-Service Mapping

Every service should have:

``` text
required supplies
consumables
reusable tools
customer-provided items
optional upsells
estimated consumption
replacement cycle
```

This supports service costing and technician readiness.

------------------------------------------------------------------------

# 56. Service Kit

Create service kits separate from customer retail kits.

Example:

``` text
SERVICE-KIT-SHINE-BATHROOM
SERVICE-KIT-ENTRYWAY-RESET
```

Service kits optimize technician execution, not retail merchandising.

------------------------------------------------------------------------

# 57. Product-to-Content Mapping

Product content may include:

``` text
why it is used
where it belongs
how to size it
how to install/use it
alternatives
what not to buy
maintenance
safety
```

`CONTENT-CATALOG.md` should reference `product_id`.

------------------------------------------------------------------------

# 58. Product-to-Learning

Customer evidence can change catalog status.

Example:

``` text
Learning:
Users consistently avoid a deep bin because items disappear from view.

Action:
Downgrade product for that micro-zone and test a shallow alternative.
```

------------------------------------------------------------------------

# 59. Product-to-Experiment

Potential experiments:

``` text
existing-item vs recommended product
generic vs premium
open bin vs lidded bin
hook vs tray
turntable vs shelf
physical label vs QR label
kit vs à la carte
```

Judge on household outcomes, not only clicks.

------------------------------------------------------------------------

# 60. Product-to-Risk

Relevant risks from `RISKS.md` include:

``` text
R-009 commerce damages trust
R-010 tiered kit economics unproven
R-012 whole-home custom logic explosion
R-014 premature physical production
procurement freshness
affiliate dependency
inventory accuracy
safety
```

------------------------------------------------------------------------

# 61. Product-to-Incident

Potential incidents:

``` text
incorrect kit contents
unsafe product guidance
wrong substitution
broken product destination
material pricing error
inventory corruption
unauthorized reorder
```

Link incident IDs back to affected product records.

------------------------------------------------------------------------

# 62. Product Change Control

Material changes should record:

``` text
what changed
why
evidence
affected kits
affected cards
affected quests
affected services
effective date
```

Meaningful changes belong in `CHANGELOG.md`.

------------------------------------------------------------------------

# 63. Product Supersession

When replacing a product:

``` yaml
old_product:
  status: SUPERSEDED
  superseded_by: PRD-...
  reason:
  effective_at:
```

Do not delete historical product records used by prior quests/orders.

------------------------------------------------------------------------

# 64. Catalog Integrity

Automated checks should eventually identify:

``` text
duplicate product IDs
missing canonical names
orphan requirements
kit lines with invalid product IDs
missing quantities
missing substitutions for critical items
stale prices
stale availability
negative margins
invalid dimensions
discontinued preferred products
broken mappings
```

------------------------------------------------------------------------

# 65. Requirement Coverage

Calculate:

``` text
REQUIREMENT COVERAGE =
requirements satisfied / applicable requirements
```

Distinguish:

``` text
REQUIRED COVERAGE
OPTIONAL COVERAGE
```

A kit should not claim whole-home completeness without defined coverage.

------------------------------------------------------------------------

# 66. Kit Coverage Matrix

Recommended structure:

  Requirement   \$199   \$299   \$499   Substitute   Notes
  ------------- ------- ------- ------- ------------ -------

This should be generated from data, not manually maintained in multiple
places.

------------------------------------------------------------------------

# 67. Room Coverage Matrix

Recommended:

  ----------------------------------------------------------------------------
  Room        Requirements     Products        \$199        \$299        \$499
                                            Coverage     Coverage     Coverage
  --------- -------------- ------------ ------------ ------------ ------------

  ----------------------------------------------------------------------------

------------------------------------------------------------------------

# 68. Micro-Zone Coverage Matrix

Recommended:

  --------------------------------------------------------------------------
  Micro-Zone     Desired        Requirement    Product        Kit Coverage
                 Function       IDs            Classes        
  -------------- -------------- -------------- -------------- --------------

  --------------------------------------------------------------------------

------------------------------------------------------------------------

# 69. Customer Product Need

The app should distinguish:

``` text
NEEDED_NOW
OPTIONAL_IMPROVEMENT
ALREADY_OWNED
CAN_REPURPOSE
NOT_NEEDED
```

This is critical to maintaining trust.

------------------------------------------------------------------------

# 70. Product Recommendation Explanation

When recommending a product, explain:

``` text
why it helps
where it goes
what problem it addresses
required dimensions/fit
quantity
acceptable alternative
```

Avoid generic shopping lists detached from the quest.

------------------------------------------------------------------------

# 71. Product Timing

Do not front-load purchasing.

Preferred flow:

``` text
SORT
 ↓
UNDERSTAND WHAT REMAINS
 ↓
MEASURE
 ↓
SELECT STORAGE/ORGANIZATION
```

This prevents buying organizers for items that should leave the space.

------------------------------------------------------------------------

# 72. Product Bundling Logic

Bundle when it reduces:

``` text
search effort
decision fatigue
compatibility risk
setup time
```

Do not bundle merely to increase order value.

------------------------------------------------------------------------

# 73. Retail vs Affiliate vs DIY

For each product need, the system may compare:

``` text
existing household solution
DIY/3D print
retail purchase
affiliate purchase
6S Success kit
service-provided supply
```

The best path depends on customer value.

------------------------------------------------------------------------

# 74. 3D Print Economics

For printable items, estimate:

``` text
filament
print time
failure allowance
machine time
post-processing
packaging
shipping
```

Do not assume 3D printing is cheaper than mass-produced organizers.

------------------------------------------------------------------------

# 75. Safety Metadata

Product records should include safety metadata when applicable:

``` text
chemical
sharp
electrical
child hazard
tip/fall
load
food contact
heat
moisture
medication
installation
```

Safety warnings should be specific, not generic boilerplate.

------------------------------------------------------------------------

# 76. Accessibility Metadata

Potential:

``` text
reach height
grip requirement
lifting requirement
visibility
label readability
one-handed use
wheelchair access
child access
elder access
```

This allows better product matching.

------------------------------------------------------------------------

# 77. Sustainability

Where useful, track:

``` text
reusable
refillable
repairable
recyclable
material
packaging
```

But do not make unsupported environmental claims.

------------------------------------------------------------------------

# 78. Product Images

Store references, not duplicate binary data unnecessarily.

Image types may include:

``` text
catalog image
installed example
dimension diagram
micro-zone example
before/after
3D render
```

Respect source rights/licensing.

------------------------------------------------------------------------

# 79. Product Documentation

Instructions should be versioned and linked.

Examples:

``` text
installation
cleaning
maintenance
printing
assembly
replacement
```

------------------------------------------------------------------------

# 80. Search and Discovery

Catalog should support retrieval by:

``` text
room
micro-zone
6S step
function
requirement
card
quest
service
kit
product class
specific product
UPC
manufacturer
retailer
price tier
```

------------------------------------------------------------------------

# 81. Product API / Service Boundary

Recommended capabilities:

``` text
get product
search product
get substitutes
get products for micro-zone
get products for card
get products for quest
get kit
calculate kit BOM
validate kit coverage
refresh availability
refresh pricing
resolve UPC
```

------------------------------------------------------------------------

# 82. Catalog Events

Potential:

``` text
product.created
product.updated
product.approved
product.preferred
product.price_changed
product.availability_changed
product.discontinued
product.superseded
kit.updated
kit.margin_changed
kit.coverage_changed
```

Events should trigger only necessary downstream work.

------------------------------------------------------------------------

# 83. Pricing Alerts

Potential conditions:

``` text
preferred product price rises materially
kit margin falls below threshold
product becomes unavailable
substitute unavailable
retailer listing changes materially
```

Threshold definitions belong in metrics/configuration.

------------------------------------------------------------------------

# 84. Procurement Refresh

High-use preferred products should refresh more frequently than obscure
optional items.

Refresh priority should consider:

``` text
kit inclusion
recommendation frequency
price volatility
availability volatility
revenue exposure
customer impact
```

------------------------------------------------------------------------

# 85. Catalog Dashboard

Executive/product views may show:

``` text
active products
preferred products
stale products
out-of-stock preferred products
requirements covered
kit BOM
kit margin
kit availability
products lacking substitutes
customer product conversion
verified outcome after recommendation
```

------------------------------------------------------------------------

# 86. Catalog Quality KPIs

Potential metrics:

``` text
catalog completeness
requirement coverage
preferred-product freshness
substitution coverage
kit availability
kit gross margin
SKU reuse
product recommendation acceptance
product recommendation outcome lift
return/problem rate
```

Definitions belong in `METRICS.md`.

------------------------------------------------------------------------

# 87. Autonomous Catalog Management

Claude may autonomously:

-   detect stale records;
-   identify duplicate products;
-   calculate BOM;
-   validate requirement coverage;
-   suggest substitutes;
-   flag discontinued items;
-   prepare catalog updates;
-   refresh allowed public-source fields;
-   create experiments;
-   identify missing product classes.

Claude must respect authority before:

-   purchasing inventory;
-   changing commercial prices beyond authority;
-   committing to suppliers;
-   making unsupported safety claims;
-   deleting historical records;
-   automatically reordering customer products.

------------------------------------------------------------------------

# 88. Catalog Agent Responsibilities

## Product Agent

Functional fit and customer value.

## Procurement/Commerce Agent

Cost, availability, sourcing, substitutes, economics.

## Home Quest Agent

Card/quest product requirements.

## Service Agent

Service supply requirements.

## Data Agent

Schema, integrity, metrics.

## Content Agent

Customer-facing product guidance.

## DevOps Agent

Catalog service reliability/deployment.

One domain should own each decision; agents should not create
conflicting catalog truth.

------------------------------------------------------------------------

# 89. Migration from V9

Migration sequence:

``` text
1. Preserve V9 artifact unchanged.
2. Parse all 117 product records.
3. Assign/retain stable product IDs.
4. Parse all 156 requirements.
5. Assign stable requirement IDs.
6. Preserve exact quantities.
7. Preserve $199/$299/$499 tier membership.
8. Preserve fallback products.
9. Preserve BOM/economic fields.
10. Preserve affiliate-readiness fields.
11. Normalize rooms/micro-zones/functions.
12. Build substitution groups.
13. Validate all kit totals.
14. Compare migrated output to V9.
15. Resolve discrepancies explicitly.
16. Mark structured catalog as canonical only after verification.
```

Never silently "improve" data during migration.

------------------------------------------------------------------------

# 90. Migration Acceptance Criteria

Migration is complete only when:

``` text
117/117 source product records accounted for
156/156 source requirements accounted for
all tier quantities reconcile
BOM totals reconcile or differences are documented
substitutions preserved
affiliate fields preserved
no orphan requirements
no orphan kit lines
source provenance retained
```

If the source dataset later proves to contain different counts, update
the canonical counts with evidence rather than forcing these numbers.

------------------------------------------------------------------------

# 91. Current Data Truth

This document knows that the V9 procurement artifact contains the
established procurement architecture described above.

It does **not** reproduce all 117 product rows or 156 requirement rows
from memory.

Those records must be migrated from the actual canonical V9 source file.

This prevents hallucinated catalog data.

------------------------------------------------------------------------

# 92. Current Product Strategy

Near-term product strategy:

``` text
DO NOT:
massively expand retail SKUs
buy broad inventory
optimize affiliate clicks
produce large physical kit quantities

DO:
use Entryway to learn what products are actually needed
validate product classes
test substitutes
measure product-assisted outcomes
keep recommendations minimal
validate kit demand before inventory
```

------------------------------------------------------------------------

# 93. Entryway Product Validation Plan

For each Entryway micro-zone:

``` text
1. define desired function
2. identify common current-state failures
3. identify product-free countermeasures
4. define product class if needed
5. test with real users
6. record already-owned solutions
7. record recommended product acceptance
8. verify outcome
9. verify sustain
10. determine whether product belongs in a kit
```

------------------------------------------------------------------------

# 94. Whole-Home Expansion Gate

A product class should expand across rooms when evidence supports reuse.

Example:

``` text
standard shallow bin works well in:
entryway
bathroom
office
laundry
```

Then standardize.

If fit differs materially, create a zone-specific class.

------------------------------------------------------------------------

# 95. Physical Kit Launch Gate

Before meaningful inventory commitment, require evidence for:

``` text
customer demand
required product mix
acceptable price
BOM economics
fulfillment economics
substitution plan
return risk
storage requirement
supplier reliability
```

------------------------------------------------------------------------

# 96. Product Recommendation Trust Test

A healthy product system should sometimes say:

``` text
You do not need to buy anything for this quest.
```

If nearly every quest produces a shopping list, investigate whether
commerce is distorting the system.

------------------------------------------------------------------------

# 97. Product Catalog Anti-Patterns

Never:

-   recommend organizers before Sort when unnecessary;
-   make retailer URLs the canonical product identity;
-   treat affiliate commission as product quality;
-   claim stale prices are current;
-   silently substitute different dimensions;
-   create dozens of unique SKUs when reusable classes work;
-   treat a photo as proof that a purchase is required;
-   auto-purchase without authority;
-   fabricate V9 product rows from memory;
-   delete superseded records used historically;
-   call a kit profitable without full variable-cost consideration;
-   claim whole-home coverage without requirement mapping;
-   confuse customer inventory with commercial catalog;
-   recommend unsafe chemical combinations;
-   make unsupported product-performance claims.

------------------------------------------------------------------------

# 98. Product Record Template

``` markdown
# PRD-XXXXXX — [Canonical Name]

**Status:**  
**Product class:**  
**Type:**  
**Primary function:**  
**6S step:**  
**Rooms:**  
**Micro-zones:**  

## Why It Exists

## Requirements Covered

## Recommended Use

## Do Not Use When

## Quantity

## Dimensions / Fit

## Safety / Accessibility

## Preferred Source

## Cost / Price

## Availability

## Substitutes

## Cards / Quests

## Kits

## Services

## Validation

## Provenance

## Change History
```

------------------------------------------------------------------------

# 99. Kit Template

``` markdown
# KIT-XXX — [Kit Name]

**Status:**  
**Tier:**  
**Target customer:**  
**Target outcome:**  
**Retail target:**  

## Requirements Covered

## Product Lines

| Product ID | Product | Qty | Required | Substitute Group | Unit Cost | Extended Cost |
|---|---|---:|---|---|---:|---:|

## Economics

**BOM:**  
**Landed/variable cost:**  
**Target retail:**  
**Gross profit:**  
**Gross margin:**  

## Coverage

## Substitutions

## Validation

## Risks

## Last Refresh
```

------------------------------------------------------------------------

# 100. Initial Canonical Catalog Baseline

``` yaml
catalog_baseline:
  stage: MIGRATION_AND_VALIDATION
  canonical_procurement_source:
    file: 6S_Success_Whole_Home_Tiered_Procurement_Master_V9.html
    products_reported: 117
    requirements_reported: 156
    commercial_tiers:
      - 199
      - 299
      - 499
  product_strategy:
    - minimize unnecessary purchasing
    - validate product need through Entryway
    - prefer functional product classes
    - preserve substitutions
    - validate full economics before inventory
    - connect products to verified outcomes
  immediate_priorities:
    - migrate V9 into structured records
    - preserve source provenance
    - validate tier BOMs
    - normalize requirement mappings
    - create substitution groups
    - connect Entryway cards/quests to product classes
```

------------------------------------------------------------------------

# 101. Immediate Implementation Priorities

1.  Locate and preserve the canonical V9 procurement artifact.
2.  Parse and validate its 117-product master.
3.  Parse and validate its 156-requirement mapping.
4.  Create stable product and requirement IDs.
5.  Reconcile the \$199/\$299/\$499 tiers.
6.  Create product-class abstraction above retailer SKUs.
7.  Build substitution groups.
8.  Map Entryway cards and micro-zones first.
9.  Connect customer inventory/UPC architecture without mixing datasets.
10. Add freshness for price and availability.
11. Add product/kit integrity tests.
12. Surface only decision-relevant product metrics on the executive
    dashboard.

------------------------------------------------------------------------

# 102. Final Principle

The 6S Success product catalog should become a **functional household
countermeasure graph**, not a shopping database.

The fundamental relationship is:

``` text
CUSTOMER
  ↓
ROOM
  ↓
MICRO-ZONE
  ↓
DESIRED FUNCTION
  ↓
GAP
  ↓
ROOT-CAUSE CANDIDATE
  ↓
6S ACTIVITY
  ↓
CARD / QUEST
  ↓
PRODUCT NEED?
  ↓
PRODUCT CLASS
  ↓
SPECIFIC PRODUCT / SUBSTITUTE / EXISTING ITEM
  ↓
VERIFIED OUTCOME
  ↓
SUSTAIN
```

The commercial system then sits on top:

``` text
VALIDATED PRODUCT NEED
      ↓
SOURCE
      ↓
COST
      ↓
SUBSTITUTION
      ↓
KIT
      ↓
PRICE / MARGIN
      ↓
CUSTOMER CHOICE
```

**6S Success should sell or recommend fewer things, better selected, at
the exact moment they remove friction and help the household sustain a
better system.**
