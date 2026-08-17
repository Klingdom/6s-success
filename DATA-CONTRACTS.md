# 6S Success Data Contracts

> Canonical data language for the 6S Success website, applications, analytics, experiments, dashboard, commerce, room decks, quests, products, and autonomous agents.

## 1. Purpose

`DATA-CONTRACTS.md` defines the stable entities, identifiers, events, properties, validation rules, and compatibility expectations used across 6S Success.

Its purpose is to prevent different agents from independently inventing incompatible names and schemas.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`
- `DATA-SOURCES.md`
- `DASHBOARD.md`
- `BACKLOG.md`
- `EXPERIMENTS.md`
- `DECISIONS.md`
- `LEARNINGS.md`

## 2. Core Principle

**One business concept should have one canonical identity.**

The website, app, physical cards, digital decks, analytics, commerce, and executive dashboard should refer to the same conceptual objects.

Preferred relationship:

**Household/User**
→ **Room**
→ **Micro-Zone**
→ **Desired Function**
→ **Friction**
→ **Root Cause**
→ **Quest**
→ **Card**
→ **Standard**
→ **Sustainment**
→ **Product**

## 3. Contract Authority

This file defines canonical contract intent.

Actual implementation must first be discovered.

Do not overwrite a functioning production schema merely because this document uses a different example.

If implementation differs:

1. inventory actual schema
2. map actual → canonical
3. identify risk
4. design migration if justified
5. preserve backward compatibility
6. update this document

## 4. Contract Rules

All core entities should have:

- stable machine ID
- human-readable name
- version where content changes materially
- lifecycle state
- timestamps where operationally relevant

Never use display text as the only identity.

## 5. ID Conventions

Recommended prefixes:

| Entity | Prefix | Example |
|---|---|---|
| Room | `room_` | `room_entryway` |
| Micro-Zone | `mz_` | `mz_entryway_keys` |
| Desired Function | `df_` | `df_fast_exit` |
| Value | `val_` | `val_simplicity` |
| Friction | `fr_` | `fr_keys_missing` |
| Root Cause | `rc_` | `rc_no_home` |
| Quest | `quest_` | `quest_entryway_keys_15` |
| Card | `card_` | `card_entryway_keys_sort` |
| Standard | `std_` | `std_keys_home` |
| Product | `prod_` | `prod_entryway_digital_deck` |
| Content | `content_` | `content_entryway_keys` |
| Experiment | `EXP-` | `EXP-0001` |
| Learning | `LRN-` | `LRN-0001` |
| Decision | `DEC-` | `DEC-0001` |
| Backlog | `BL-` | `BL-0001` |

IDs should be immutable after publication.

## 6. Naming Rules

Machine names:

- lowercase
- snake_case
- ASCII where practical
- descriptive
- stable

Event names use past-tense or action-completed semantics where practical.

Examples:

`desired_function_started`

`quest_completed`

Avoid:

`click1`

`thing_done`

`new_event_final_v2`

## 7. Versioning

Use semantic contract versions when needed:

`1.0.0`

Breaking changes require migration planning.

Adding an optional field is normally backward compatible.

Renaming/removing a required field is breaking.

## 8. Common Metadata

Recommended common event envelope:

```json
{
  "event_name": "quest_started",
  "event_version": "1.0.0",
  "event_id": "uuid",
  "occurred_at": "ISO-8601",
  "environment": "production",
  "anonymous_id": "opaque-id",
  "user_id": null,
  "household_id": null,
  "session_id": "opaque-id",
  "source": "web",
  "release_id": "git-sha-or-release",
  "properties": {}
}
```

Do not put secrets or unnecessary PII in analytics events.

## 9. Environments

Canonical values:

- `production`
- `staging`
- `development`
- `test`

Executive metrics should normally include only `production`.

## 10. User Identity

Use anonymous interaction where identity is unnecessary.

Potential fields:

```yaml
anonymous_id: string
user_id: nullable string
household_id: nullable string
```

Do not infer or store sensitive personal attributes for personalization.

## 11. Household

Conceptual schema:

```yaml
household_id: string
created_at: datetime
member_count: nullable integer
preferences: object
```

Only collect information necessary to provide customer value.

## 12. Room Entity

```yaml
room_id: string
name: string
slug: string
description: string
status: active|beta|planned|retired
version: string
```

Example:

```yaml
room_id: room_entryway
name: Entryway
slug: entryway
status: active
```

## 13. Micro-Zone Entity

```yaml
micro_zone_id: string
room_id: string
name: string
slug: string
primary_function_default: nullable string
description: string
status: active|beta|planned|retired
version: string
```

Examples:

- Key Zone
- Shoe Zone
- Coat Zone
- Bag/Backpack Zone
- Mail/Paper Zone
- Drop Zone
- Guest Arrival Zone
- Weather Gear Zone

Actual taxonomy must come from the canonical catalog.

## 14. Personal Value Entity

```yaml
value_id: string
name: string
description: string
status: active|retired
```

Possible values:

- simplicity
- speed
- calm
- safety
- independence
- hospitality
- preparedness
- accessibility
- family participation
- visual order

These are examples, not evidence about any user.

## 15. Desired Function Entity

```yaml
desired_function_id: string
name: string
description: string
applicable_room_ids: []
applicable_micro_zone_ids: []
status: active|beta|retired
version: string
```

Examples:

- fastest exit
- visual calm
- child independence
- guest readiness
- weather readiness
- maximum useful capacity

## 16. Desired Function Selection

```yaml
selection_id: string
room_id: string
micro_zone_id: nullable string
desired_function_id: string
value_ids: []
priority: nullable integer
created_at: datetime
```

Do not assume one desired function must apply permanently.

## 17. Friction Entity

Friction describes the observable problem.

```yaml
friction_id: string
name: string
description: string
room_ids: []
micro_zone_ids: []
status: active|retired
```

Examples:

- keys frequently misplaced
- shoes block walkway
- backpacks accumulate on floor
- mail creates pile
- coats exceed accessible capacity

## 18. Root Cause Entity

Root cause describes why friction occurs.

```yaml
root_cause_id: string
name: string
description: string
category: string
status: active|retired
```

Canonical root-cause families should include:

- `excess`
- `no_home`
- `wrong_home`
- `poor_access`
- `poor_visibility`
- `excess_steps`
- `unclear_ownership`
- `capacity_mismatch`
- `no_standard`
- `replenishment_failure`
- `cleaning_friction`
- `safety_risk`

## 19. Diagnosis

```yaml
diagnosis_id: string
room_id: string
micro_zone_id: string
friction_ids: []
root_cause_ids: []
desired_function_id: nullable string
confidence: nullable number
created_at: datetime
```

If confidence is algorithmic, document how it is calculated.

Do not present heuristic confidence as scientific certainty.

## 20. Quest Entity

```yaml
quest_id: string
name: string
room_id: string
micro_zone_ids: []
root_cause_ids: []
desired_function_ids: []
duration_minutes: integer
min_players: integer
max_players: integer
difficulty: nullable string
card_ids: []
instructions: string
completion_definition: string
status: draft|beta|active|retired
version: string
```

Supported target duration range:

**15-90 minutes**

Exceptions should be explicit.

## 21. Card Entity

```yaml
card_id: string
name: string
card_type: string
room_id: string
micro_zone_ids: []
root_cause_ids: []
desired_function_ids: []
estimated_minutes: nullable integer
instructions: string
completion_definition: string
physical_deck: boolean
digital_deck: boolean
status: draft|beta|active|retired
version: string
```

Physical and digital decks should share canonical card identity where practical.

## 22. Card Types

Possible controlled values:

- `room`
- `micro_zone`
- `sort`
- `set_in_order`
- `shine`
- `standardize`
- `sustain`
- `safety`
- `diagnosis`
- `challenge`
- `wildcard`
- `standard`
- `product_assist`

Extend intentionally, not ad hoc.

## 23. Quest Session

```yaml
quest_session_id: string
quest_id: string
room_id: string
micro_zone_ids: []
player_count: integer
selection_mode: configured|random|assigned|voluntary|mixed
started_at: datetime
completed_at: nullable datetime
status: started|completed|abandoned
```

## 24. Quest Card Assignment

```yaml
quest_session_id: string
card_id: string
participant_id: nullable string
assignment_mode: assigned|voluntary|random
claimed_at: nullable datetime
completed_at: nullable datetime
status: available|claimed|completed|skipped
```

## 25. Standard Entity

A standard defines the intended maintained condition.

```yaml
standard_id: string
room_id: string
micro_zone_id: string
desired_function_id: nullable string
name: string
description: string
visual_reference_id: nullable string
capacity_limit: nullable number
reset_frequency: nullable string
status: active|retired
version: string
```

## 26. Sustainment Check

```yaml
sustainment_check_id: string
standard_id: string
micro_zone_id: string
checked_at: datetime
status: sustained|partially_sustained|not_sustained
friction_ids: []
notes: nullable string
```

## 27. Product Entity

```yaml
product_id: string
name: string
product_type: digital|physical|service|bundle
status: concept|prototype|beta|active|paused|retired
room_ids: []
micro_zone_ids: []
desired_function_ids: []
root_cause_ids: []
quest_ids: []
price: nullable number
currency: nullable string
sku: nullable string
commerce_product_id: nullable string
version: string
```

The commerce platform remains authoritative for transactional price/order truth where defined in `DATA-SOURCES.md`.

## 28. Product Recommendation

```yaml
recommendation_id: string
product_id: string
room_id: nullable string
micro_zone_id: nullable string
desired_function_id: nullable string
root_cause_ids: []
quest_id: nullable string
reason_code: string
created_at: datetime
```

Recommendations should be explainable.

## 29. Content Entity

```yaml
content_id: string
content_type: article|guide|landing_page|faq|video|tool
title: string
url_path: string
room_ids: []
micro_zone_ids: []
desired_function_ids: []
root_cause_ids: []
quest_ids: []
product_ids: []
status: draft|active|updated|retired
version: string
```

## 30. Commerce Order Reference

Analytics should reference transactions without duplicating the full commerce database.

```yaml
order_id: string
commerce_source: string
currency: string
gross_amount: number
discount_amount: number
refund_amount: number
net_amount: number
created_at: datetime
```

Financial authority follows `DATA-SOURCES.md`.

## 31. Experiment Assignment

```yaml
experiment_id: string
variant_id: string
assignment_unit_id: string
assigned_at: datetime
```

Assignment should remain stable for the intended unit.

## 32. Event Taxonomy

Core event families:

- acquisition
- navigation
- desired function
- diagnosis
- quest
- card
- standard
- sustainment
- product
- commerce
- content
- experiment
- system

Avoid tracking every click.

Track behavior that helps answer meaningful questions.

## 33. Acquisition Events

Examples:

`landing_page_viewed`

`search_landing_viewed`

Recommended properties:

```yaml
content_id: nullable string
landing_path: string
channel: nullable string
campaign_id: nullable string
```

## 34. Desired Function Events

### `desired_function_started`

Required:

```yaml
room_id: string
micro_zone_id: nullable string
```

### `desired_function_selected`

Required:

```yaml
room_id: string
micro_zone_id: nullable string
desired_function_id: string
```

Optional:

```yaml
value_ids: []
```

### `desired_function_completed`

Required:

```yaml
room_id: string
desired_function_id: string
```

## 35. Micro-Zone Events

### `micro_zone_viewed`

```yaml
room_id: string
micro_zone_id: string
```

### `micro_zone_selected`

```yaml
room_id: string
micro_zone_id: string
desired_function_id: nullable string
```

## 36. Diagnosis Events

### `diagnosis_started`

```yaml
room_id: string
micro_zone_id: string
```

### `friction_selected`

```yaml
room_id: string
micro_zone_id: string
friction_id: string
```

### `root_cause_identified`

```yaml
room_id: string
micro_zone_id: string
root_cause_id: string
method: user_selected|guided|system_suggested
```

### `diagnosis_completed`

```yaml
diagnosis_id: string
room_id: string
micro_zone_id: string
root_cause_ids: []
```

## 37. Quest Events

### `quest_impression`

```yaml
quest_id: string
room_id: string
micro_zone_ids: []
recommendation_reason: nullable string
```

### `quest_started`

```yaml
quest_session_id: string
quest_id: string
player_count: integer
selection_mode: string
```

### `quest_completed`

```yaml
quest_session_id: string
quest_id: string
duration_seconds: integer
player_count: integer
cards_completed: integer
cards_total: integer
```

### `quest_abandoned`

```yaml
quest_session_id: string
quest_id: string
elapsed_seconds: nullable integer
last_card_id: nullable string
```

## 38. Card Events

Examples:

`card_viewed`

`card_claimed`

`card_assigned`

`card_completed`

`card_skipped`

Properties should include `card_id` and `quest_session_id` when applicable.

## 39. Standard Events

### `standard_created`

```yaml
standard_id: string
room_id: string
micro_zone_id: string
```

### `standard_confirmed`

```yaml
standard_id: string
micro_zone_id: string
```

## 40. Sustainment Events

### `sustainment_check_completed`

```yaml
sustainment_check_id: string
standard_id: string
micro_zone_id: string
status: sustained|partially_sustained|not_sustained
days_since_standard: integer
```

This event is important for the future North Star.

## 41. Product Events

### `product_viewed`

```yaml
product_id: string
room_id: nullable string
micro_zone_id: nullable string
```

### `product_recommended`

```yaml
recommendation_id: string
product_id: string
reason_code: string
root_cause_ids: []
```

### `product_recommendation_clicked`

```yaml
recommendation_id: string
product_id: string
```

## 42. Commerce Events

Useful behavioral events may include:

- `add_to_cart`
- `checkout_started`
- `purchase_completed`
- `refund_recorded`

`purchase_completed` analytics must reconcile with the authoritative transaction system.

Example:

```yaml
order_id: string
currency: string
value: number
product_ids: []
```

Do not treat a client-side purchase event as financial truth by itself.

## 43. Content Events

Track meaningful interaction, not arbitrary scrolling.

Examples:

`content_viewed`

`content_cta_selected`

`content_to_quest_started`

`content_to_product_viewed`

## 44. Experiment Events

### `experiment_exposed`

```yaml
experiment_id: string
variant_id: string
assignment_unit_id: string
```

Do not infer exposure solely because a user was assigned a variant if treatment was never rendered.

## 45. System/Release Events

Operational systems may record:

`deployment_started`

`deployment_completed`

`deployment_failed`

`rollback_completed`

These belong in operational telemetry, not necessarily customer analytics.

Recommended metadata:

```yaml
release_id: string
commit_sha: string
image_digest: nullable string
environment: string
```

## 46. Required Event Quality

Every production event should support, where applicable:

- unique event ID
- timestamp
- environment
- event version
- source
- session/anonymous identity
- release identity

This enables debugging and reconciliation.

## 47. Event Idempotency

Events capable of creating transactional or durable side effects require idempotency.

Analytics ingestion should also deduplicate when event IDs repeat.

Never allow a retry to create duplicate orders or entitlements.

## 48. Time

Store canonical timestamps in UTC where practical.

Render local time at the presentation layer.

Record timezone when local scheduling matters.

## 49. Currency

Never store money as ambiguous floating-point values in transactional systems.

Use the commerce platform's native safe representation or integer minor units where appropriate.

Always include currency.

## 50. Duration

Canonical analytics duration unit:

`seconds`

Content entities may use estimated minutes for human display.

Do not mix milliseconds, seconds, and minutes under the same field name.

## 51. Null vs Zero

`null` means unknown/not applicable.

`0` means measured zero.

Never replace missing data with zero.

## 52. Boolean Fields

Use actual booleans:

`true`

`false`

not:

`"yes"`

`"no"`

unless required by an external API.

## 53. Enumerations

Controlled enumerations must be documented.

Do not allow agents to introduce spelling variants such as:

`microzone`

`micro-zone`

`micro_zone`

for the same machine concept.

Canonical machine term:

`micro_zone`

## 54. Taxonomy Changes

Before changing a canonical taxonomy:

1. search usages
2. inspect analytics history
3. inspect products/cards/content
4. determine migration
5. preserve historical interpretation
6. update dependent contracts

Taxonomy changes can be breaking changes.

## 55. Event Deprecation

Do not silently stop an event.

Mark:

`DEPRECATED`

Document replacement.

Maintain compatibility long enough for dashboards/experiments to migrate.

## 56. Schema Validation

Where practical, implement machine-readable validation using the project's actual stack.

Possible technologies include:

- JSON Schema
- Zod
- TypeScript types
- Pydantic
- database constraints

Do not add multiple competing validation systems without need.

## 57. Contract Tests

Critical contracts should have automated tests.

Examples:

- required event properties
- valid enum values
- valid entity references
- purchase reconciliation
- experiment exposure
- release metadata
- API compatibility

## 58. Referential Integrity

Where practical:

- `micro_zone.room_id` must exist
- `quest.card_ids` must exist
- `product.root_cause_ids` must exist
- `content.product_ids` must exist

Do not allow orphaned canonical entities.

## 59. Analytics Integrity

Validate:

- production environment
- test/internal exclusions
- event uniqueness
- required IDs
- event ordering where relevant
- release metadata
- transaction reconciliation

## 60. Privacy

Data minimization is mandatory.

Do not place in routine analytics:

- passwords
- API keys
- tokens
- precise home addresses
- private photographs
- unnecessary names
- sensitive personal attributes

Household images require a separate privacy/security design.

## 61. Consent

If optional analytics, personalization, marketing, or image analysis requires consent under applicable requirements, respect the user's choice.

Do not use data-contract consistency as a reason to collect unnecessary data.

## 62. Retention

Retention rules should be defined by actual legal, operational, and product requirements.

Do not retain raw customer data indefinitely merely because storage is cheap.

## 63. Data Ownership

Suggested ownership:

| Contract | Owner |
|---|---|
| Rooms / Micro-Zones | product-manager |
| Desired Functions / Root Causes | product-manager |
| Quests / Cards | quest-experience |
| Products | commerce-manager |
| Content | content-strategy |
| Analytics Events | analytics-intelligence |
| Experiments | analytics-intelligence + experiment owner |
| Release Metadata | github-manager + devops-sre |
| Runtime Metadata | vps-docker-manager |
| Financial Transactions | commerce/payment source |

Ownership does not override source authority.

## 64. API Contracts

APIs should use the canonical IDs when practical.

Example:

```json
{
  "room_id": "room_entryway",
  "micro_zone_id": "mz_entryway_keys",
  "desired_function_id": "df_fast_exit"
}
```

Avoid passing human labels as primary foreign keys.

## 65. URL Contracts

Public URLs should be human-readable and SEO-friendly.

Example:

`/entryway/keys`

Internally map to stable IDs.

Changing a slug should not change entity identity.

Use redirects when public URLs change.

## 66. Product Recommendation Contract

A recommendation should be traceable to context:

```yaml
product_id: prod_example
reason_code: solves_root_cause
root_cause_ids:
  - rc_no_home
micro_zone_id: mz_entryway_keys
quest_id: quest_entryway_keys_15
```

This enables recommendation-quality measurement.

## 67. Search-to-Outcome Contract

Future intelligence should support:

**Search Query**
→ **Content**
→ **Room**
→ **Micro-Zone**
→ **Desired Function**
→ **Diagnosis**
→ **Quest**
→ **Product**
→ **Outcome**

Do not force all users through every step.

## 68. UPC / Inventory Future Contract

When inventory functionality is implemented:

```yaml
inventory_item_id: string
upc: nullable string
name: string
primary_function: string
room_id: string
micro_zone_id: string
storage_location_id: nullable string
quantity: nullable number
min_quantity: nullable number
max_quantity: nullable number
reorder_enabled: boolean
```

This is a future contract until the feature exists.

## 69. Storage Location Future Contract

```yaml
storage_location_id: string
room_id: string
micro_zone_id: string
container_type: nullable string
capacity: nullable number
label_id: nullable string
```

Future inventory guidance can map an item to an appropriate location/container.

## 70. Physical Product / 3D Print Future Contract

For future modular storage products:

```yaml
product_id: string
micro_zone_ids: []
grid_system: nullable string
dimensions_mm: {}
material: nullable string
printer_compatibility: []
file_asset_ids: []
```

Do not mix manufacturing specifications into generic analytics events.

## 71. Executive Metric Contracts

`METRICS.md` defines metric formulas.

Every dashboard metric should resolve to:

- metric ID
- definition
- source
- period
- filters
- freshness
- confidence

`DATA-CONTRACTS.md` ensures underlying events/entities can support those formulas.

## 72. North Star Contract

Candidate future North Star:

`Sustained Micro-Zone Improvements`

A qualifying outcome will require a documented formula using:

- completed improvement
- established standard
- later sustainment evidence
- deduplication rules
- time window

Do not publish the metric until the contract is finalized and measurable.

## 73. Contract Discovery Process

Before implementing these contracts in an existing codebase:

1. inspect database schema
2. inspect API models
3. inspect TypeScript/types
4. inspect analytics events
5. inspect commerce models
6. inspect content/card files
7. inspect dashboard queries
8. build mapping table
9. identify conflicts
10. propose migration

Do not blindly rewrite production.

## 74. Migration Table

Use when actual names differ:

| Existing | Canonical | Action | Breaking? |
|---|---|---|---|
| `zoneId` | `micro_zone_id` | map/migrate | TBD |
| `taskId` | `card_id` | inspect semantics | TBD |

Never assume similarly named concepts are equivalent.

## 75. Backward Compatibility

During migration, support old and new contracts when necessary.

Prefer explicit adapters.

Remove compatibility code after verified migration.

## 76. Contract Change Process

For material changes:

1. identify problem
2. identify consumers
3. propose contract
4. determine compatibility
5. update version
6. implement validators
7. migrate
8. verify analytics/dashboard
9. document
10. deprecate old contract

## 77. Contract Decision Authority

Small backward-compatible additions may be autonomous.

Breaking changes to core business entities require stronger review and must follow `AUTONOMY.md`.

Changes affecting financial, customer identity, privacy, or irreversible data require appropriate approval.

## 78. Data Quality Dashboard

Eventually show:

- invalid events
- missing required fields
- unknown entity IDs
- duplicate events
- stale sources
- reconciliation failures
- schema-version distribution

Do not hide contract failures.

## 79. Dead-Letter Handling

Invalid production events should not silently disappear.

Where architecture supports it:

- quarantine invalid event
- record reason
- alert based on severity
- allow safe replay after correction

Never replay financial side effects without idempotency.

## 80. Release Compatibility

A release should declare which contract versions it emits/accepts where material.

This is especially important during migrations.

## 81. Agent Rules

Before creating a new entity, event, property, or enum, agents must:

1. search this file
2. search code
3. search analytics schema
4. reuse canonical concept if it exists
5. extend intentionally if it does not

Do not invent duplicate concepts.

## 82. Analytics Agent Rule

`analytics-intelligence` owns measurement coherence.

It should reject ambiguous events such as:

`button_clicked`

when the business question requires:

`quest_started`

Track business behavior rather than UI implementation whenever possible.

## 83. Product Agent Rule

`product-manager` should define the semantic business entity first.

Implementation agents then map UI/database/API behavior to it.

## 84. Commerce Agent Rule

`commerce-manager` must preserve separation between:

- product catalog identity
- commerce platform identity
- analytics identity

Map them explicitly.

## 85. GitHub / DevOps Rule

`github-manager` and `devops-sre` should ensure release metadata allows business events and incidents to be associated with the deployed software version.

## 86. Documentation Rule

When a contract changes materially, update:

- this file
- affected metric definitions
- affected source definitions
- experiment definitions
- API/schema docs
- tests

## 87. Initial Implementation Priorities

Recommended order:

### P1

1. inventory existing contracts
2. canonical room/micro-zone IDs
3. desired-function/root-cause IDs
4. quest/card IDs
5. core event envelope
6. quest lifecycle events
7. commerce reconciliation IDs
8. experiment exposure
9. release identity

### P2

10. standard/sustainment events
11. product recommendation traceability
12. content-to-outcome mapping

### Later

13. household inventory
14. UPC/replenishment
15. storage locations
16. 3D-print product metadata

## 88. Minimum Viable Event Set

Do not instrument hundreds of events initially.

Start with:

- `landing_page_viewed`
- `desired_function_started`
- `desired_function_completed`
- `micro_zone_selected`
- `diagnosis_completed`
- `quest_impression`
- `quest_started`
- `quest_completed`
- `quest_abandoned`
- `standard_created`
- `sustainment_check_completed`
- `product_viewed`
- `product_recommended`
- `product_recommendation_clicked`
- `add_to_cart`
- `checkout_started`
- `purchase_completed`
- `experiment_exposed`

Only implement events that correspond to real features.

## 89. Contract Acceptance Criteria

The first production contract layer is acceptable when:

1. canonical IDs exist for active Entryway entities
2. event names are documented
3. required properties are validated
4. environment is captured
5. release identity is captured where feasible
6. test traffic can be excluded
7. purchase analytics reconcile with transactions
8. experiment exposure is trustworthy
9. unknown entity IDs are detectable
10. no secrets/PII leak into routine analytics

## 90. Final Principle

6S Success should not become a collection of disconnected pages, cards, products, analytics events, and databases.

It should become one coherent system where the same concepts connect:

**what a person values**

to

**what they want a space to do**

to

**what prevents it**

to

**what quest can improve it**

to

**what standard sustains it**

to

**what product may help**

to

**what outcome actually occurred**

`DATA-CONTRACTS.md` is the common language that makes that system possible.

When every agent speaks the same language, Claude can reason across the entire business instead of managing disconnected software components.
