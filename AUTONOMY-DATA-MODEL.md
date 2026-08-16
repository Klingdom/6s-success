# 6S Success Autonomy Data Model

> Canonical logical data model for the 6S Success autonomous Claude Code operating system and its Mission Control / Executive Dashboard.

## 1. Purpose

`AUTONOMY-DATA-MODEL.md` translates the autonomous operating model into durable entities, relationships, identifiers, constraints, and projections.

It provides a concrete blueprint for storing and connecting:

- owner directives
- missions
- tasks
- agents and agent versions
- routing and handoffs
- autonomy events
- repositories and pull requests
- releases and deployments
- experiments and measurements
- owner decisions
- incidents
- evaluations
- costs
- customer outcomes
- rooms and micro-zones
- desired functions
- quests and cards
- products and orders
- content and SEO/AEO work
- learnings
- self-improvement

This is a logical model. Claude must inspect the actual application stack and existing schemas before implementing it.

---

# 2. Core Principle

**One connected operating model, not a collection of disconnected agent tables.**

Every important autonomous action should be traceable from strategic intent through execution to verified outcome.

```text
Directive
→ Mission
→ Task
→ Agent
→ Change
→ Deployment
→ Measurement
→ Customer / Business Outcome
→ Learning
```

---

# 3. Source-of-Truth Principle

Do not duplicate authoritative data unnecessarily.

Examples:

- GitHub remains authoritative for repository/PR state.
- Commerce provider remains authoritative for payment transactions.
- Runtime remains authoritative for current container state.
- Analytics platform may remain authoritative for high-volume behavioral events.
- This data model stores normalized references, operational projections, decisions, and cross-system relationships.

---

# 4. Database Strategy

Prefer the simplest reliable database already compatible with the project.

For a typical VPS/Docker web application, PostgreSQL is a strong default if already present or justified.

Do not introduce a second database solely because this document exists.

---

# 5. Identifier Strategy

Every internal entity should have a stable opaque ID.

Recommended examples:

```text
dir_...
mis_...
tsk_...
agt_...
agv_...
evt_...
exp_...
dep_...
rel_...
dec_...
inc_...
evl_...
lrn_...
qst_...
prd_...
```

UUID or ULID is acceptable.

Do not use mutable names as primary keys.

---

# 6. Common Fields

Where appropriate:

```yaml
id:
created_at:
updated_at:
status:
created_by:
metadata:
```

Use timezone-aware timestamps.

Avoid adding `metadata` as an excuse to skip proper schema design.

---

# 7. Entity Domains

The model is organized into:

1. Governance
2. Autonomous Operations
3. Software Delivery
4. Measurement & Experiments
5. Reliability & Security
6. Customer Value
7. Products & Commerce
8. Content & Growth
9. Learning & Self-Improvement
10. Dashboard Projections

---

# 8. GOVERNANCE DOMAIN

## 8.1 Owner Directive

Represents durable owner strategy, constraint, target, prohibition, or priority.

```yaml
owner_directive:
  id:
  title:
  directive_type:
  priority:
  statement:
  status:
  effective_at:
  retired_at:
  source_ref:
  created_at:
  updated_at:
```

Suggested `directive_type`:

- STRATEGY
- PRIORITY
- TARGET
- CONSTRAINT
- PROHIBITION
- PREFERENCE
- APPROVAL_RULE

---

# 9. Directive Version

Material directive changes should be versioned.

```yaml
directive_version:
  id:
  directive_id:
  version:
  statement:
  changed_at:
  change_reason:
  source_ref:
```

---

# 10. Autonomy Policy Reference

Do not necessarily copy every policy into database rows.

Store references where operational traceability requires them.

```yaml
policy_reference:
  id:
  policy_name:
  canonical_file:
  version_ref:
  status:
```

---

# 11. Owner Decision

Represents a discrete owner decision requested by the autonomous system.

```yaml
owner_decision:
  id:
  mission_id:
  task_id:
  requested_by_agent_id:
  decision_type:
  question:
  recommendation:
  status:
  requested_at:
  required_by:
  decided_at:
  selected_option:
  directive_id:
```

Status:

- PENDING
- DECIDED
- CANCELLED
- EXPIRED

---

# 12. Decision Option

```yaml
decision_option:
  id:
  decision_id:
  option_code:
  label:
  description:
  recommended:
  risk_level:
```

---

# 13. AUTONOMOUS OPERATIONS DOMAIN

## 13.1 Mission

A mission is a meaningful bounded unit of autonomous business/operational improvement.

```yaml
mission:
  id:
  title:
  objective:
  status:
  priority:
  primary_constraint:
  owner_agent_id:
  directive_id:
  success_metric_id:
  started_at:
  completed_at:
  result_status:
  result_summary:
  created_at:
  updated_at:
```

Status:

- PROPOSED
- READY
- ACTIVE
- PAUSED
- BLOCKED
- COMPLETED
- FAILED
- CANCELLED

---

# 14. Mission Directive Link

A mission may support multiple directives.

```yaml
mission_directive:
  mission_id:
  directive_id:
  relationship_type:
```

---

# 15. Task

```yaml
task:
  id:
  mission_id:
  parent_task_id:
  title:
  description:
  status:
  mode:
  priority:
  owner_agent_id:
  definition_of_done:
  authority_ref:
  blocked_reason:
  queued_at:
  started_at:
  completed_at:
  created_at:
  updated_at:
```

Status:

- CREATED
- QUEUED
- ASSIGNED
- ACTIVE
- BLOCKED
- COMPLETED
- FAILED
- CANCELLED

---

# 16. Task Dependency

```yaml
task_dependency:
  task_id:
  depends_on_task_id:
  dependency_type:
```

Avoid circular dependencies.

---

# 17. Task Agent Assignment

Supports owner + supporting agents.

```yaml
task_agent_assignment:
  id:
  task_id:
  agent_id:
  role:
  assigned_at:
  released_at:
```

Role:

- OWNER
- SUPPORT
- REVIEWER
- VERIFIER

Exactly one active OWNER should exist for material tasks.

---

# 18. Task Attempt

Track retries separately from the logical task.

```yaml
task_attempt:
  id:
  task_id:
  attempt_number:
  agent_version_id:
  started_at:
  ended_at:
  status:
  failure_class:
  estimated_cost_usd:
  output_ref:
```

---

# 19. Agent

Stable logical specialist identity.

```yaml
agent:
  id:
  slug:
  name:
  domain:
  status:
  trust_level:
  canonical_file:
  created_at:
  retired_at:
```

Status:

- ACTIVE
- DEGRADED
- SUSPENDED
- RETIRED

---

# 20. Agent Version

```yaml
agent_version:
  id:
  agent_id:
  version:
  git_commit:
  model_config_ref:
  tool_config_ref:
  effective_at:
  retired_at:
  evaluation_status:
```

Do not store secrets in tool configuration references.

---

# 21. Agent Capability

```yaml
agent_capability:
  id:
  agent_id:
  capability:
  mode:
  authority_level:
  status:
```

---

# 22. Agent Tool Access

```yaml
agent_tool_access:
  id:
  agent_id:
  tool_id:
  access_mode:
  granted_by_ref:
  effective_at:
  revoked_at:
```

Store permission metadata, never credentials.

---

# 23. Routing Decision

```yaml
routing_decision:
  id:
  mission_id:
  task_id:
  selected_agent_id:
  mode:
  reason_code:
  decided_at:
  rerouted:
  prior_routing_id:
```

Do not store hidden chain-of-thought.

---

# 24. Resource Lock

```yaml
resource_lock:
  id:
  resource_type:
  resource_id:
  task_id:
  agent_id:
  acquired_at:
  expires_at:
  released_at:
  status:
```

---

# 25. Handoff

```yaml
handoff:
  id:
  task_id:
  from_agent_id:
  to_agent_id:
  status:
  completed_work:
  remaining_work:
  evidence_refs:
  requested_at:
  completed_at:
```

---

# 26. AUTONOMY EVENT DOMAIN

## 26.1 Autonomy Event

Implement the envelope defined in `AUTONOMY-EVENTS.md`.

```yaml
autonomy_event:
  event_id:
  event_type:
  schema_version:
  occurred_at:
  recorded_at:
  source:
  environment:
  severity:
  mission_id:
  task_id:
  agent_id:
  actor_type:
  correlation_id:
  causation_id:
  resource_refs:
  evidence_refs:
  data:
  idempotency_key:
```

Prefer append-only semantics.

---

# 27. Event Type Registry

```yaml
event_type_registry:
  event_type:
  schema_version:
  domain:
  description:
  status:
  schema_ref:
```

---

# 28. Event Ingestion Failure

```yaml
event_ingestion_failure:
  id:
  received_at:
  source:
  event_type:
  failure_reason:
  payload_hash:
  status:
  resolved_at:
```

Do not persist unsafe rejected payloads unnecessarily.

---

# 29. SOFTWARE DELIVERY DOMAIN

## 29.1 Repository

```yaml
repository:
  id:
  provider:
  external_id:
  owner:
  name:
  default_branch:
  url_ref:
  status:
  last_verified_at:
```

---

# 30. Pull Request

```yaml
pull_request:
  id:
  repository_id:
  external_pr_number:
  task_id:
  title:
  branch:
  base_branch:
  status:
  opened_at:
  merged_at:
  external_ref:
```

---

# 31. Commit Reference

```yaml
commit_reference:
  id:
  repository_id:
  sha:
  pull_request_id:
  task_id:
  authored_at:
```

---

# 32. Release

```yaml
release:
  id:
  repository_id:
  commit_id:
  version:
  image_digest:
  status:
  created_at:
  release_ref:
```

---

# 33. Environment

```yaml
environment:
  id:
  name:
  environment_type:
  status:
  runtime_ref:
```

Types:

- LOCAL
- TEST
- STAGING
- PRODUCTION

---

# 34. Deployment

```yaml
deployment:
  id:
  release_id:
  environment_id:
  task_id:
  status:
  started_at:
  completed_at:
  verified_at:
  rollback_release_id:
  verification_status:
  external_ref:
```

Status:

- REQUESTED
- STARTED
- COMPLETED
- VERIFIED
- FAILED
- ROLLED_BACK

---

# 35. Deployment Verification

```yaml
deployment_verification:
  id:
  deployment_id:
  verifier_agent_id:
  smoke_test_status:
  health_check_status:
  customer_path_status:
  evidence_refs:
  verified_at:
```

---

# 36. Runtime Host

```yaml
runtime_host:
  id:
  provider:
  host_alias:
  environment_id:
  status:
  last_verified_at:
```

Do not store SSH secrets.

---

# 37. Runtime Service

```yaml
runtime_service:
  id:
  host_id:
  service_name:
  service_type:
  image_ref:
  status:
  public_exposure:
  persistent_data:
  last_verified_at:
```

---

# 38. MEASUREMENT & EXPERIMENT DOMAIN

## 38.1 Metric Definition

```yaml
metric_definition:
  id:
  slug:
  name:
  description:
  unit:
  calculation:
  source_system:
  freshness_requirement:
  status:
```

---

# 39. Metric Observation

```yaml
metric_observation:
  id:
  metric_id:
  observed_at:
  period_start:
  period_end:
  value_numeric:
  value_text:
  confidence:
  source_ref:
  freshness_status:
```

Do not force all metrics into numeric values.

---

# 40. Baseline

```yaml
baseline:
  id:
  metric_id:
  mission_id:
  experiment_id:
  period_start:
  period_end:
  value:
  source_ref:
  established_at:
```

---

# 41. Experiment

```yaml
experiment:
  id:
  mission_id:
  title:
  hypothesis:
  status:
  primary_metric_id:
  baseline_id:
  decision_rule:
  started_at:
  ended_at:
  decision:
```

Status:

- PROPOSED
- ACTIVE
- MEASURING
- COMPLETED
- STOPPED

Decision:

- ADOPT
- REVISE
- ROLLBACK
- INCONCLUSIVE
- ABANDON

---

# 42. Experiment Guardrail

```yaml
experiment_guardrail:
  id:
  experiment_id:
  metric_id:
  threshold_rule:
```

---

# 43. Experiment Measurement

```yaml
experiment_measurement:
  id:
  experiment_id:
  metric_id:
  measured_at:
  baseline_value:
  result_value:
  delta:
  confidence:
  source_ref:
```

---

# 44. Outcome Attribution

```yaml
outcome_attribution:
  id:
  mission_id:
  experiment_id:
  outcome_type:
  outcome_ref:
  attribution_method:
  confidence:
  evidence_refs:
```

Never imply causal certainty beyond evidence.

---

# 45. Cost Record

```yaml
cost_record:
  id:
  mission_id:
  task_id:
  agent_id:
  provider:
  cost_category:
  amount_usd:
  usage_period_start:
  usage_period_end:
  source_ref:
```

---

# 46. RELIABILITY & SECURITY DOMAIN

## 46.1 Incident

```yaml
incident:
  id:
  mission_id:
  category:
  severity:
  status:
  owner_agent_id:
  opened_at:
  mitigated_at:
  resolved_at:
  customer_impact:
  root_cause:
  postmortem_ref:
```

---

# 47. Incident Timeline

```yaml
incident_timeline:
  id:
  incident_id:
  occurred_at:
  event_type:
  summary:
  evidence_ref:
```

---

# 48. Security Finding

```yaml
security_finding:
  id:
  severity:
  category:
  resource_ref:
  status:
  detected_at:
  resolved_at:
  evidence_ref:
```

Never store exposed secret values.

---

# 49. Backup Record

```yaml
backup_record:
  id:
  resource_ref:
  status:
  started_at:
  completed_at:
  backup_ref:
  verification_status:
```

---

# 50. Recovery Test

```yaml
recovery_test:
  id:
  resource_ref:
  status:
  started_at:
  completed_at:
  recovery_time_seconds:
  evidence_ref:
```

---

# 51. AGENT EVALUATION DOMAIN

## 51.1 Evaluation Case

```yaml
evaluation_case:
  id:
  agent_domain:
  case_code:
  test_type:
  scenario_ref:
  trust_level_tested:
  status:
```

---

# 52. Evaluation Run

```yaml
evaluation_run:
  id:
  agent_version_id:
  started_at:
  completed_at:
  status:
  total_score:
  critical_failure:
  trust_recommendation:
```

---

# 53. Evaluation Case Result

```yaml
evaluation_case_result:
  id:
  evaluation_run_id:
  evaluation_case_id:
  status:
  score:
  failure_class:
  evidence_ref:
```

---

# 54. Trust History

```yaml
agent_trust_history:
  id:
  agent_id:
  prior_trust_level:
  new_trust_level:
  reason:
  evaluation_run_id:
  changed_at:
```

---

# 55. CUSTOMER VALUE DOMAIN

This domain should integrate with existing application/customer schemas rather than duplicate them.

Use privacy-minimized identifiers.

---

# 56. Customer / Household Profile

If the product requires persistent customer configuration:

```yaml
customer_profile:
  id:
  external_user_ref:
  status:
  created_at:
```

Avoid storing unnecessary personal data.

---

# 57. Room Type

```yaml
room_type:
  id:
  slug:
  name:
  description:
  status:
```

Examples:

- entryway
- kitchen
- bathroom
- laundry-room
- home-office

---

# 58. Micro-Zone Type

```yaml
micro_zone_type:
  id:
  room_type_id:
  slug:
  name:
  primary_function_default:
  status:
```

---

# 59. Household Space

Represents a customer's instance of a room/micro-zone.

```yaml
household_space:
  id:
  customer_profile_id:
  room_type_id:
  micro_zone_type_id:
  nickname:
  status:
```

---

# 60. Desired Function

Defines an available functional outcome.

```yaml
desired_function:
  id:
  room_type_id:
  micro_zone_type_id:
  slug:
  name:
  description:
  outcome_category:
  status:
```

---

# 61. Customer Desired Function Selection

```yaml
desired_function_selection:
  id:
  customer_profile_id:
  household_space_id:
  desired_function_id:
  selected_at:
  status:
  source_flow:
```

Store categorical selections rather than sensitive free-form personal values where possible.

---

# 62. Root Cause Category

```yaml
root_cause_category:
  id:
  slug:
  name:
  description:
  status:
```

Examples might include:

- excess inventory
- unclear home
- poor accessibility
- insufficient capacity
- weak visual control
- maintenance friction

---

# 63. Space Diagnosis

```yaml
space_diagnosis:
  id:
  household_space_id:
  desired_function_id:
  root_cause_category_id:
  confidence:
  source:
  created_at:
```

---

# 64. Customer Outcome

```yaml
customer_outcome:
  id:
  customer_profile_id:
  household_space_id:
  outcome_type:
  outcome_ref:
  confirmation_method:
  confirmed_at:
  evidence_ref:
```

This is a key business-value entity.

---

# 65. Sustain Check

```yaml
sustain_check:
  id:
  customer_outcome_id:
  checked_at:
  status:
  friction_score:
  follow_up_action_ref:
```

---

# 66. QUEST DOMAIN

## 66.1 Quest

```yaml
quest:
  id:
  slug:
  title:
  room_type_id:
  micro_zone_type_id:
  desired_function_id:
  planned_minutes_min:
  planned_minutes_max:
  min_players:
  max_players:
  difficulty:
  status:
```

---

# 67. Quest Card

```yaml
quest_card:
  id:
  card_code:
  title:
  card_type:
  six_s_activity:
  room_type_id:
  micro_zone_type_id:
  estimated_minutes:
  status:
```

---

# 68. Quest Card Membership

```yaml
quest_card_membership:
  quest_id:
  quest_card_id:
  sequence:
  required:
```

---

# 69. Quest Session

```yaml
quest_session:
  id:
  customer_profile_id:
  quest_id:
  household_space_id:
  player_count:
  status:
  started_at:
  completed_at:
  actual_minutes:
```

---

# 70. Quest Session Card

```yaml
quest_session_card:
  id:
  quest_session_id:
  quest_card_id:
  assigned_player_ref:
  status:
  started_at:
  completed_at:
```

---

# 71. PRODUCT & COMMERCE DOMAIN

## 71.1 Product

```yaml
product:
  id:
  sku:
  slug:
  name:
  product_type:
  status:
  current_price_ref:
  inventory_ref:
```

Commerce platform may remain authoritative for price/inventory.

---

# 72. Product Outcome Mapping

```yaml
product_outcome_mapping:
  product_id:
  desired_function_id:
  micro_zone_type_id:
  relationship_type:
  priority:
```

This allows products to be recommended because they solve a verified need.

---

# 73. Product Recommendation

```yaml
product_recommendation:
  id:
  customer_profile_id:
  household_space_id:
  product_id:
  desired_function_id:
  diagnosis_id:
  reason_code:
  created_at:
```

---

# 74. Order Reference

```yaml
order_reference:
  id:
  customer_profile_id:
  commerce_provider:
  external_order_id:
  status:
  order_total_usd:
  created_at:
  external_ref:
```

Do not duplicate sensitive payment details.

---

# 75. Order Item Reference

```yaml
order_item_reference:
  id:
  order_id:
  product_id:
  quantity:
  unit_price_usd:
```

---

# 76. CONTENT & GROWTH DOMAIN

## 76.1 Content Asset

```yaml
content_asset:
  id:
  slug:
  content_type:
  title:
  status:
  canonical_path:
  room_type_id:
  micro_zone_type_id:
  desired_function_id:
  published_at:
  updated_at:
```

---

# 77. Search Intent

```yaml
search_intent:
  id:
  query_cluster:
  intent_type:
  room_type_id:
  micro_zone_type_id:
  desired_function_id:
  status:
```

---

# 78. Content Search Mapping

```yaml
content_search_mapping:
  content_asset_id:
  search_intent_id:
  relationship_type:
```

---

# 79. Growth Opportunity

```yaml
growth_opportunity:
  id:
  opportunity_type:
  funnel_stage:
  metric_id:
  evidence_ref:
  priority:
  status:
  created_at:
```

---

# 80. Growth Experiment Link

```yaml
growth_experiment:
  growth_opportunity_id:
  experiment_id:
```

---

# 81. LEARNING & SELF-IMPROVEMENT DOMAIN

## 81.1 Learning

```yaml
learning:
  id:
  mission_id:
  experiment_id:
  incident_id:
  category:
  statement:
  confidence:
  status:
  recorded_at:
  standardized_at:
```

Status:

- PROVISIONAL
- VERIFIED
- STANDARDIZED
- INVALIDATED

---

# 82. Decision Record

Material architecture/business decisions:

```yaml
decision_record:
  id:
  title:
  decision:
  rationale_summary:
  status:
  decided_at:
  supersedes_id:
  canonical_ref:
```

Keep detailed rationale in `DECISIONS.md` if that is canonical.

---

# 83. Self-Improvement

```yaml
self_improvement:
  id:
  target_type:
  target_ref:
  change_class:
  problem:
  root_cause:
  status:
  baseline_ref:
  primary_metric_id:
  proposed_change:
  rollback_ref:
  started_at:
  completed_at:
  decision:
```

---

# 84. Self-Improvement Guardrail

```yaml
self_improvement_guardrail:
  id:
  self_improvement_id:
  metric_id:
  threshold_rule:
```

---

# 85. Agent Improvement Link

```yaml
agent_improvement:
  self_improvement_id:
  agent_id:
  prior_agent_version_id:
  new_agent_version_id:
```

---

# 86. KEY RELATIONSHIPS

Core operating relationships:

```text
OwnerDirective 1──* Mission
Mission        1──* Task
Task           *──* Agent
Agent          1──* AgentVersion
Task           1──* TaskAttempt
Task           1──* RoutingDecision
Task           1──* Handoff
Mission/Task   1──* AutonomyEvent
Task           1──* PullRequest
PullRequest    1──* CommitReference
Commit         1──* Release
Release        1──* Deployment
Mission        1──* Experiment
Experiment     1──* ExperimentMeasurement
AgentVersion   1──* EvaluationRun
Mission        1──* CostRecord
Mission        1──* Learning
```

---

# 87. CUSTOMER VALUE RELATIONSHIPS

```text
RoomType       1──* MicroZoneType
MicroZoneType  1──* DesiredFunction
Customer       1──* HouseholdSpace
HouseholdSpace 1──* DesiredFunctionSelection
HouseholdSpace 1──* SpaceDiagnosis
DesiredFunction 1──* Quest
Quest          *──* QuestCard
Quest          1──* QuestSession
HouseholdSpace 1──* CustomerOutcome
DesiredFunction *──* Product
Customer       1──* OrderReference
```

---

# 88. END-TO-END VALUE CHAIN

The model should support queries such as:

```text
Which owner directive caused this mission?
Which tasks supported it?
Which agents executed those tasks?
Which PR changed the site?
Which release was deployed?
Was it verified?
Which experiment measured the change?
Did quest completion improve?
Did customer outcomes improve?
Did revenue change?
What did the work cost?
What did Claude learn?
```

---

# 89. Executive Dashboard Projection

Do not make the executive dashboard query dozens of raw tables directly.

Create read models/views.

Recommended:

```text
dashboard_executive_summary
dashboard_active_missions
dashboard_owner_decisions
dashboard_agent_health
dashboard_release_health
dashboard_customer_funnel
dashboard_revenue
dashboard_autonomy_health
dashboard_incidents
dashboard_experiments
```

---

# 90. Executive Summary Projection

Conceptual:

```yaml
executive_summary:
  generated_at:
  monthly_revenue:
  revenue_target:
  active_customers:
  quest_completion_rate:
  customer_outcome_rate:
  active_missions:
  primary_business_constraint:
  production_health:
  autonomy_health:
  pending_owner_decisions:
  active_incidents:
  latest_release:
```

Use UNKNOWN when data is unavailable.

---

# 91. Mission Control Projection

```yaml
mission_control:
  current_mission:
  primary_constraint:
  active_tasks:
  blocked_tasks:
  active_agents:
  resource_locks:
  current_experiment:
  latest_deployment:
  owner_decisions:
  incidents:
```

---

# 92. Agent Health Projection

Derived from:

- task attempts
- routing decisions
- evaluations
- owner corrections
- costs
- policy events

---

# 93. Revenue Projection

Use commerce-authoritative data.

Do not calculate revenue from page events.

---

# 94. Customer Funnel Projection

Potential funnel:

```text
Qualified Visitor
→ Desired Function Started
→ Desired Function Selected
→ Diagnosis Completed
→ Quest Started
→ Quest Completed
→ Outcome Confirmed
→ Product Purchase / No-Purchase Solution
→ Sustain Check
```

This is more useful than traffic alone.

---

# 95. Room / Micro-Zone Performance

Support:

```yaml
micro_zone_performance:
  room:
  micro_zone:
  visitors:
  desired_function_selections:
  quest_starts:
  quest_completions:
  outcomes_confirmed:
  purchases:
  repeat_engagement:
```

---

# 96. Product Performance by Outcome

Support questions like:

> Which products actually help users achieve the desired Entryway function?

Not merely:

> Which products sell?

---

# 97. Autonomy ROI Projection

Conceptual:

```text
Verified Business Value
───────────────────────
Agent + Model + Tool + Infrastructure Cost
```

Do not fabricate monetary attribution.

---

# 98. Constraints

Recommended database constraints:

- one active task owner
- unique agent slug
- unique quest card code
- unique product SKU where applicable
- valid foreign keys
- nonnegative monetary amounts
- valid status enums
- no self-dependency for tasks
- unique event ID
- unique idempotency key where provided

---

# 99. Soft Delete

Prefer explicit status/retirement over deleting important historical operational records.

---

# 100. Audit Fields

For governance-sensitive changes consider:

```yaml
created_by:
updated_by:
change_ref:
```

---

# 101. Data Classification

Classify fields/entities as:

- PUBLIC
- INTERNAL
- CONFIDENTIAL
- SENSITIVE

Do not assume all telemetry is harmless.

---

# 102. Secrets

Credentials must not be modeled as normal business data.

Store only references to an approved secret store/configuration mechanism.

---

# 103. Personal Data

Minimize.

For desired-function and values flows:

- prefer category IDs
- avoid unnecessary free text
- avoid inferring sensitive personal traits
- define retention/privacy requirements

---

# 104. Payment Data

Do not store raw card data.

Use commerce-provider tokens/references only as allowed.

---

# 105. Event Payload vs Normalized Tables

Events preserve history.

Normalized tables support current state and efficient queries.

Use both where justified.

Example:

```text
task.assigned event
+
task.owner_agent_id current projection
```

---

# 106. Projection Rebuild

Where possible, derived autonomy state should be rebuildable from events plus authoritative external systems.

---

# 107. External System References

Standardize references.

Example:

```yaml
external_ref:
  provider:
  type:
  id:
```

or equivalent.

---

# 108. Synchronization

External synchronization jobs should record:

- last successful sync
- cursor/checkpoint
- error state
- source freshness

---

# 109. Sync State

```yaml
sync_state:
  id:
  source_system:
  entity_type:
  last_success_at:
  cursor:
  status:
  last_error_class:
```

---

# 110. Idempotency

Writes triggered by external events should support idempotency.

Particularly:

- orders
- webhooks
- deployments
- scheduler jobs
- event ingestion

---

# 111. Concurrency

Use database transactions/locking where multiple agents could update the same state.

Do not rely only on prompt instructions for concurrency safety.

---

# 112. Resource Locks vs Database Locks

`resource_lock` expresses business/orchestration ownership.

Database locks protect technical transaction integrity.

They are not the same thing.

---

# 113. Status Transition Validation

Important entities should have legal state transitions.

Example deployment:

```text
REQUESTED
→ STARTED
→ COMPLETED
→ VERIFIED
```

or:

```text
STARTED
→ FAILED
→ ROLLED_BACK
```

Reject impossible transitions.

---

# 114. Mission State Machine

```text
PROPOSED
→ READY
→ ACTIVE
→ COMPLETED
```

Alternative:

```text
ACTIVE
→ BLOCKED
→ ACTIVE
```

or:

```text
ACTIVE
→ FAILED/CANCELLED
```

---

# 115. Task State Machine

```text
CREATED
→ QUEUED
→ ASSIGNED
→ ACTIVE
→ COMPLETED
```

With BLOCKED/FAILED/CANCELLED paths.

---

# 116. Experiment State Machine

```text
PROPOSED
→ ACTIVE
→ MEASURING
→ COMPLETED
```

Decision stored separately.

---

# 117. Data Freshness

Every dashboard metric should know:

- source
- last update
- freshness requirement
- freshness status

---

# 118. UNKNOWN Semantics

Missing data is not zero.

Use:

- NULL
- UNKNOWN status
- explicit unavailable state

as appropriate.

---

# 119. Target vs Actual

Never store targets as if they are observed metrics.

Example:

```yaml
target:
  metric: monthly_revenue
  value: 20000

actual:
  metric_observation_id:
```

---

# 120. Metric Lineage

A dashboard number should be traceable to:

```text
Metric Definition
→ Source
→ Observation
→ Projection
→ Dashboard
```

---

# 121. Dashboard Cache

Near-real-time dashboards may use cached projections.

Cache must expose freshness.

---

# 122. Query Examples

The model should support:

```sql
-- Conceptual only
SELECT active missions and their accountable agents;

SELECT pending owner decisions ordered by urgency;

SELECT failed deployments in the last 30 days;

SELECT agent success rate by version;

SELECT quest completion by room and micro-zone;

SELECT customer outcomes by desired function;

SELECT revenue associated with product/outcome categories;

SELECT autonomy cost by mission;

SELECT self-improvements adopted and their measured results;
```

---

# 123. API Boundaries

Potential logical APIs:

```text
/governance
/missions
/tasks
/agents
/events
/deployments
/experiments
/metrics
/decisions
/incidents
/evaluations
/customer-outcomes
/quests
/products
/dashboard
```

Do not expose internal control APIs publicly by default.

---

# 124. Command vs Query Separation

Commands mutate state.

Queries read state.

High-risk commands require authorization.

Dashboard endpoints should normally be read-only.

---

# 125. Executive Dashboard Access

Protect operational/business data with authentication and least privilege.

Do not expose Mission Control publicly.

---

# 126. Owner Command Center

Long term, owner actions may include:

- approve/reject decision
- pause mission
- change priority
- acknowledge incident
- approve protected change

These should produce events.

---

# 127. Dashboard Refresh

Use polling, server-sent events, WebSockets, or another appropriate mechanism based on actual need.

Do not add real-time infrastructure before measuring the need.

---

# 128. Data Retention

Define retention by domain.

Examples requiring longer retention may include:

- decisions
- releases
- incidents
- evaluations
- audit events

High-volume analytics may have different policies.

Actual retention belongs in privacy/data governance.

---

# 129. Archival

Historical missions/tasks should remain queryable without slowing operational views excessively.

Choose archival strategy based on scale.

---

# 130. Backup

Include critical operating tables in backup policy.

---

# 131. Restore

Restore testing should prove:

- missions recover
- directives recover
- events recover
- agent/evaluation history recovers
- dashboard projections can rebuild

---

# 132. Migration Discipline

Database schema changes require:

- versioned migration
- backward compatibility where needed
- backup/recovery awareness
- deployment sequencing
- rollback strategy

---

# 133. Schema Ownership

Recommended logical ownership:

| Domain | Primary Owner |
|---|---|
| Governance | Orchestrator |
| Agent / routing | Orchestrator |
| GitHub / release | GitHub Manager |
| Runtime / deployment | VPS/DevOps |
| Metrics / experiments | Analytics |
| Security | Security |
| Customer outcome | Customer Journey |
| Quest | Quest Agent |
| Product | Product Agent |
| Commerce | Commerce Agent |
| Content/search | Content + SEO/AEO |
| Self-improvement | Orchestrator |

Implementation ownership may differ based on application architecture.

---

# 134. Cross-Domain Writes

Agents should not directly mutate another domain's authoritative tables merely because they can access the database.

Use service/API boundaries or explicit ownership rules where practical.

---

# 135. Database Credentials

Agents should receive least-privilege access.

Prefer:

- read-only analytics access
- scoped service credentials
- migration role separated from application role

according to actual architecture.

---

# 136. Production Database Safety

No autonomous agent should casually:

- DROP tables
- truncate production data
- rewrite large datasets
- remove audit history
- bypass migrations

without appropriate authority and safeguards.

---

# 137. Initial Physical Implementation

Before creating tables:

1. inspect existing database
2. inspect migrations
3. inspect current user/product schemas
4. inspect analytics stack
5. inspect commerce provider
6. inspect GitHub/deployment metadata already available
7. identify what can be referenced instead of duplicated
8. propose minimum schema delta
9. review risk
10. implement incrementally

---

# 138. Minimum Viable Autonomy Schema

Phase 1 can be much smaller:

```text
agents
agent_versions
missions
tasks
task_attempts
routing_decisions
owner_decisions
autonomy_events
repositories
pull_requests
releases
deployments
experiments
metric_definitions
metric_observations
cost_records
evaluation_runs
learnings
```

This is enough to begin powering Mission Control and Autonomy Health.

---

# 139. Phase 2 Customer Value Schema

Add/integrate:

```text
room_types
micro_zone_types
desired_functions
desired_function_selections
space_diagnoses
quests
quest_cards
quest_sessions
customer_outcomes
sustain_checks
products
product_outcome_mappings
order_references
content_assets
search_intents
```

Only after inspecting existing product schema.

---

# 140. Phase 3 Closed-Loop Intelligence

Connect:

```text
Autonomous Work
↕
Customer Outcomes
↕
Revenue
↕
Cost
↕
Experiments
↕
Learning
↕
Self-Improvement
```

---

# 141. Bootstrap State

Until verified:

```yaml
autonomy_data_model:
  implementation_status: NOT_VERIFIED
  database_engine: UNKNOWN
  existing_schema: UNKNOWN
  migration_system: UNKNOWN
  event_store: UNKNOWN
  dashboard_projection_store: UNKNOWN
  analytics_system: UNKNOWN
  commerce_system: UNKNOWN
```

Do not infer implementation from this specification.

---

# 142. First Data-Model Mission

```yaml
mission:
  title: Establish Autonomy Control Data Layer
  objective: >
    Inspect the existing 6S Success application architecture and implement
    the smallest safe schema required to connect missions, tasks, agents,
    events, deployments, owner decisions, experiments, costs, and evaluations.
  success:
    - existing schema inventoried
    - authoritative systems identified
    - minimum schema approved by governance
    - migrations created
    - event model implemented
    - Mission Control projection available
    - Executive Dashboard can read current state
    - backup/restore impact verified
```

---

# 143. Acceptance Tests

Minimum:

- create mission
- assign task
- assign exactly one task owner
- record agent version
- emit validated event
- open owner decision
- connect PR to task
- connect release to deployment
- verify deployment
- create experiment
- record metric observation
- record cost
- record evaluation
- record learning
- query executive summary
- reject invalid foreign key
- reject duplicate event ID
- preserve UNKNOWN instead of coercing to zero
- verify secret filtering

---

# 144. Dashboard Acceptance Test

The owner should be able to see, from real data:

```text
What is Claude working on?
Why?
Which agents own it?
What is blocked?
What changed in production?
Is production healthy?
What experiments are running?
What decisions need me?
What is the system costing?
What customer/business outcomes changed?
How healthy is the autonomous organization?
```

---

# 145. Traceability Acceptance Test

Select any material production deployment.

The system should trace:

```text
Deployment
→ Release
→ Commit
→ PR
→ Task
→ Mission
→ Directive
```

and, when applicable:

```text
Deployment
→ Experiment
→ Metric
→ Outcome
→ Learning
```

---

# 146. Data Quality Metrics

Track:

- orphan records
- invalid state transitions
- missing agent versions
- stale projections
- missing source refs
- duplicate external refs
- unknown event types
- failed syncs
- dashboard freshness

---

# 147. Data Quality Ownership

Analytics owns measurement quality.

Domain owners own correctness of their operational records.

Orchestrator owns cross-domain integrity.

---

# 148. Data Model Maturity

## Level 0 — Files and Chat

State is manually reconstructed.

## Level 1 — Autonomy Control Tables

Missions, tasks, agents, events, decisions, and deployments are connected.

## Level 2 — Operational Intelligence

Experiments, costs, incidents, and evaluations are integrated.

## Level 3 — Customer Value Intelligence

Rooms, micro-zones, desired functions, quests, outcomes, products, and commerce connect.

## Level 4 — Executive Operating System

Mission Control and Executive Dashboard are generated from reliable projections.

## Level 5 — Closed-Loop Autonomous Business

Owner directives, autonomous execution, production changes, customer outcomes, revenue, cost, learning, and self-improvement form one auditable data model.

---

# 149. Non-Negotiable Rules

Claude and subagents must not:

- create duplicate systems of record without need
- assume a database engine without inspection
- store secrets in normal tables
- store raw payment card data
- treat missing values as zero
- treat targets as actual results
- fabricate customer outcomes
- fabricate revenue attribution
- use mutable names as critical identity
- allow multiple accountable task owners
- silently rewrite audit history
- permit impossible state transitions
- let every agent invent incompatible schemas
- bypass migration discipline
- expose internal control-plane APIs publicly by default
- overbuild streaming/distributed infrastructure without evidence
- create tables before inspecting existing schemas
- allow analytics projections to override authoritative transaction systems
- store private chain-of-thought
- weaken privacy in pursuit of better personalization

---

# 150. Final Principle

The autonomous organization should eventually be represented as one connected graph of verified work and value:

```text
OWNER
  ↓
DIRECTIVES
  ↓
MISSIONS
  ↓
TASKS
  ↓
AGENTS
  ↓
CHANGES
  ↓
RELEASES
  ↓
DEPLOYMENTS
  ↓
EXPERIMENTS
  ↓
CUSTOMER OUTCOMES
  ↓
REVENUE / COST
  ↓
LEARNINGS
  ↓
SELF-IMPROVEMENT
```

For the 6S Success customer experience, the business-value side should connect:

```text
ROOM
→ MICRO-ZONE
→ DESIRED FUNCTION
→ ROOT CAUSE
→ QUEST
→ CARD
→ ACTION
→ OUTCOME
→ SUSTAIN
→ PRODUCT WHEN USEFUL
```

When these two chains connect, Claude can optimize the business for verified customer value rather than simply generating more code, content, traffic, or agent activity.

That is the purpose of `AUTONOMY-DATA-MODEL.md`.
