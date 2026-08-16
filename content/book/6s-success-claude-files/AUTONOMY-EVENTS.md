# 6S Success Autonomy Events

> Canonical event model for the 6S Success autonomous Claude Code operating system. This specification defines how agent work, missions, deployments, experiments, incidents, costs, owner interactions, customer outcomes, and self-improvement become structured, auditable, queryable data.

## 1. Purpose

`AUTONOMY-EVENTS.md` defines the telemetry backbone of the autonomous organization.

Without structured events, Claude can operate, but it cannot reliably answer:

- What happened?
- Which agent did it?
- Why was it done?
- What mission did it support?
- What changed?
- What did it cost?
- Was it verified?
- Did it create value?
- Did the owner need to intervene?
- Did it fail?
- Was it rolled back?
- What should the system learn?

The event stream should eventually power:

- Mission Control
- Executive Dashboard
- Autonomy Health
- Agent Evaluations
- Scheduler
- Incident reporting
- Cost analysis
- Experiment analysis
- Audit history
- Continuous self-improvement

---

# 2. Core Principle

**Every material autonomous action should leave a structured, traceable event.**

Do not rely on chat history, terminal history, or agent memory as the system of record.

---

# 3. Event Philosophy

Events should be:

- structured
- append-oriented
- timestamped
- attributable
- traceable
- minimal
- useful
- safe
- queryable
- immutable after finalization where practical

---

# 4. What Is an Event?

An event is a factual record that something material occurred.

Examples:

```text
mission.started
task.assigned
agent.started
handoff.completed
pull_request.opened
deployment.started
deployment.verified
experiment.started
experiment.measured
incident.opened
owner.decision_requested
owner.decision_received
cost.anomaly_detected
customer.quest_completed
self_improvement.adopted
```

---

# 5. Event vs State

Events describe change.

State describes current condition.

Example:

```text
Event:
deployment.verified at 14:32

State:
production_release = abc123
```

Mission Control is primarily state.

Autonomy Events records how state changed.

---

# 6. Event vs Log

Logs contain detailed technical output.

Events contain decision-useful facts.

Do not dump raw logs into the event stream.

Use references.

---

# 7. Event Envelope

Every event should use a common envelope.

```yaml
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
resource_refs: []
evidence_refs: []
data: {}
```

---

# 8. Required Core Fields

Minimum:

```yaml
event_id:
event_type:
schema_version:
occurred_at:
source:
actor_type:
data:
```

Additional fields are required when applicable.

---

# 9. Event ID

Use globally unique IDs.

Potential format:

```text
evt_01J...
```

UUID/ULID or equivalent is acceptable.

Do not use sequential IDs if they create avoidable coordination problems.

---

# 10. Event Type Naming

Use:

```text
domain.action
```

Examples:

```text
task.started
deployment.failed
owner.decision_requested
```

Prefer past-tense action semantics for completed facts.

---

# 11. Schema Version

Example:

```yaml
schema_version: "1.0"
```

Do not silently change event meaning without schema/version management.

---

# 12. Time

Use timezone-aware ISO 8601 timestamps.

Example:

```yaml
occurred_at: 2026-08-14T16:32:10-06:00
```

Store UTC internally if architecture prefers, but preserve clear timezone semantics.

---

# 13. Occurred vs Recorded

```yaml
occurred_at:
recorded_at:
```

These may differ if an event is ingested later.

---

# 14. Actor Type

Use:

- `AGENT`
- `OWNER`
- `SYSTEM`
- `CUSTOMER`
- `EXTERNAL`

---

# 15. Agent Identity

When actor is an agent:

```yaml
agent_id:
agent_version:
```

Agent version should be traceable to configuration/commit when practical.

---

# 16. Source

Examples:

- orchestrator
- github
- docker
- scheduler
- analytics
- commerce
- website
- monitoring
- owner-interface

Use actual registered source IDs.

---

# 17. Environment

Use:

- `LOCAL`
- `TEST`
- `STAGING`
- `PRODUCTION`
- `CONTROL_PLANE`
- `UNKNOWN`

---

# 18. Severity

Use:

- `INFO`
- `NOTICE`
- `WARNING`
- `ERROR`
- `CRITICAL`

Do not label routine events critical.

---

# 19. Correlation ID

Use `correlation_id` to group related events across agents/systems.

Example:

All events for one deployment share a correlation ID.

---

# 20. Causation ID

`causation_id` points to the event that directly caused the new event where useful.

Example:

```text
experiment.decision_made
caused_by
experiment.measurement_completed
```

---

# 21. Mission ID

All work supporting a mission should carry:

```yaml
mission_id:
```

when available.

---

# 22. Task ID

All delegated work should carry:

```yaml
task_id:
```

---

# 23. Resource References

Examples:

```yaml
resource_refs:
  - github:repo/owner/name
  - github:pr/123
  - docker:container/web
  - journey:entryway
  - experiment:ENTRYWAY-DF-004
```

Never put credentials in resource references.

---

# 24. Evidence References

Events should reference evidence, not duplicate it.

Examples:

```yaml
evidence_refs:
  - github:workflow-run/123
  - metrics:funnel/entryway/2026-08-14
  - logs:deployment/abc123
```

---

# 25. Event Data

`data` contains event-specific structured fields.

Keep it small.

---

# 26. Mission Events

Recommended:

```text
mission.created
mission.started
mission.paused
mission.resumed
mission.completed
mission.failed
mission.cancelled
mission.constraint_changed
```

---

# 27. Mission Started

```yaml
event_type: mission.started
data:
  title:
  objective:
  primary_constraint:
  owner_agent:
  success_metric:
```

---

# 28. Mission Completed

```yaml
event_type: mission.completed
data:
  result_status:
  primary_metric_result:
  customer_result:
  business_result:
  learning_ref:
```

Do not claim customer/business result without evidence.

---

# 29. Task Events

Recommended:

```text
task.created
task.queued
task.assigned
task.started
task.blocked
task.resumed
task.completed
task.failed
task.cancelled
task.rerouted
task.retried
```

---

# 30. Task Assigned

```yaml
event_type: task.assigned
data:
  owner_agent:
  support_agents: []
  mode:
  scope:
  authority:
```

---

# 31. Task Completed

```yaml
event_type: task.completed
data:
  definition_of_done_met:
  output_refs: []
  verification_status:
  duration_seconds:
  estimated_cost_usd:
```

---

# 32. Task Failed

```yaml
event_type: task.failed
severity: ERROR
data:
  failure_class:
  safe_state:
  retryable:
  attempt:
  next_action:
```

Do not store raw secret-bearing error output.

---

# 33. Agent Events

Recommended:

```text
agent.invoked
agent.completed
agent.failed
agent.degraded
agent.suspended
agent.promoted
agent.requalified
```

---

# 34. Agent Invocation

```yaml
event_type: agent.invoked
data:
  mode:
  trust_level:
  context_package_ref:
  tool_scope:
```

---

# 35. Agent Completion

```yaml
event_type: agent.completed
data:
  result_status:
  handoff_required:
  owner_escalation_required:
  estimated_cost_usd:
```

---

# 36. Routing Events

Recommended:

```text
routing.decision_made
routing.rerouted
routing.conflict_detected
routing.lock_acquired
routing.lock_released
routing.lock_stale
```

---

# 37. Routing Decision

```yaml
event_type: routing.decision_made
data:
  selected_owner:
  support_agents: []
  mode:
  reason_code:
```

Do not store hidden chain-of-thought.

Use concise reason codes/evidence.

---

# 38. Handoff Events

Recommended:

```text
handoff.requested
handoff.completed
handoff.rejected
```

---

# 39. Handoff Completed

```yaml
event_type: handoff.completed
data:
  from_agent:
  to_agent:
  completed_work:
  remaining_work:
  evidence_refs: []
```

---

# 40. GitHub Events

Recommended:

```text
github.issue_opened
github.branch_created
github.pull_request_opened
github.pull_request_reviewed
github.pull_request_merged
github.workflow_started
github.workflow_failed
github.workflow_passed
github.release_created
github.security_alert_detected
```

---

# 41. Pull Request Opened

```yaml
event_type: github.pull_request_opened
data:
  repository:
  pr_number:
  branch:
  base_branch:
  change_type:
```

---

# 42. Workflow Failed

```yaml
event_type: github.workflow_failed
severity: ERROR
data:
  repository:
  workflow:
  run_id:
  failing_job:
  failure_class:
```

---

# 43. VPS / Docker Events

Recommended:

```text
vps.health_changed
vps.capacity_warning
docker.container_started
docker.container_stopped
docker.container_unhealthy
docker.container_restarted
docker.image_changed
docker.port_exposure_detected
docker.volume_risk_detected
```

---

# 44. Container Unhealthy

```yaml
event_type: docker.container_unhealthy
severity: ERROR
data:
  host_id:
  container:
  image:
  restart_count:
  healthcheck_status:
```

---

# 45. Deployment Events

Recommended:

```text
deployment.requested
deployment.started
deployment.completed
deployment.verified
deployment.failed
deployment.rolled_back
```

---

# 46. Deployment Started

```yaml
event_type: deployment.started
data:
  release_id:
  commit:
  image_digest:
  environment:
  rollback_ref:
```

---

# 47. Deployment Verified

```yaml
event_type: deployment.verified
data:
  release_id:
  commit:
  smoke_tests:
  health_checks:
  verification_status:
```

---

# 48. Deployment Failed

```yaml
event_type: deployment.failed
severity: ERROR
data:
  release_id:
  stage:
  failure_class:
  rollback_required:
```

---

# 49. Experiment Events

Recommended:

```text
experiment.created
experiment.started
experiment.exposure_recorded
experiment.measurement_completed
experiment.decision_made
experiment.stopped
experiment.standardized
```

---

# 50. Experiment Started

```yaml
event_type: experiment.started
data:
  experiment_id:
  hypothesis:
  primary_metric:
  guardrails: []
  baseline_ref:
  decision_rule:
```

---

# 51. Experiment Measurement

```yaml
event_type: experiment.measurement_completed
data:
  experiment_id:
  primary_metric_result:
  guardrail_results:
  sample_quality:
  confidence:
```

---

# 52. Experiment Decision

```yaml
event_type: experiment.decision_made
data:
  experiment_id:
  decision:
  rationale_code:
  learning_ref:
```

Use decisions:

- ADOPT
- REVISE
- ROLLBACK
- INCONCLUSIVE
- ABANDON

---

# 53. Analytics Events

Recommended:

```text
analytics.metric_updated
analytics.data_stale
analytics.instrumentation_failed
analytics.metric_conflict
analytics.baseline_established
analytics.anomaly_detected
```

---

# 54. Data Stale

```yaml
event_type: analytics.data_stale
severity: WARNING
data:
  dataset:
  last_good_timestamp:
  affected_metrics: []
```

---

# 55. Metric Conflict

```yaml
event_type: analytics.metric_conflict
severity: WARNING
data:
  metric:
  source_a:
  source_b:
  reconciliation_status:
```

---

# 56. Customer Journey Events

Recommended:

```text
customer.desired_function_started
customer.desired_function_selected
customer.diagnosis_completed
customer.quest_started
customer.quest_completed
customer.outcome_confirmed
customer.sustain_check_completed
customer.feedback_received
```

These are product/customer events and require appropriate privacy design.

---

# 57. Desired Function Selected

```yaml
event_type: customer.desired_function_selected
actor_type: CUSTOMER
data:
  room:
  micro_zone:
  function_id:
  source_flow:
```

Do not store unnecessary personal values or free text in the event if a safe categorical ID is sufficient.

---

# 58. Diagnosis Completed

```yaml
event_type: customer.diagnosis_completed
data:
  room:
  micro_zone:
  diagnosis_category:
  recommended_quest_id:
```

---

# 59. Quest Started

```yaml
event_type: customer.quest_started
data:
  quest_id:
  room:
  micro_zone:
  player_count:
  planned_minutes:
```

---

# 60. Quest Completed

```yaml
event_type: customer.quest_completed
data:
  quest_id:
  room:
  micro_zone:
  player_count:
  actual_minutes:
  cards_completed:
```

---

# 61. Outcome Confirmed

```yaml
event_type: customer.outcome_confirmed
data:
  room:
  micro_zone:
  outcome_id:
  confirmation_method:
```

This is more valuable than merely recording a page view.

---

# 62. Product Events

Recommended:

```text
product.viewed
product.recommended
product.added_to_cart
product.purchased
product.refunded
product.solution_used
product.no_purchase_solution_selected
```

---

# 63. Product Recommendation

```yaml
event_type: product.recommended
data:
  product_id:
  room:
  micro_zone:
  outcome_id:
  recommendation_reason_code:
```

---

# 64. No-Purchase Solution

```yaml
event_type: product.no_purchase_solution_selected
data:
  solution_id:
  room:
  micro_zone:
  outcome_id:
```

The system should measure useful outcomes even when no sale occurs.

---

# 65. Commerce Events

Recommended:

```text
commerce.checkout_started
commerce.checkout_completed
commerce.payment_failed
commerce.order_created
commerce.order_fulfilled
commerce.refund_requested
commerce.refund_completed
commerce.provider_failed
```

---

# 66. Commerce Safety

Never store:

- full payment card numbers
- CVV
- passwords
- raw payment secrets

Use provider-safe identifiers.

---

# 67. SEO / Content Events

Recommended:

```text
content.created
content.updated
content.published
content.retired
seo.opportunity_detected
seo.indexation_changed
seo.technical_issue_detected
aeo.answer_opportunity_detected
```

---

# 68. Content Published

```yaml
event_type: content.published
data:
  content_id:
  content_type:
  canonical_path:
  target_intent:
  related_room:
  related_micro_zone:
```

---

# 69. Growth Events

Recommended:

```text
growth.constraint_identified
growth.experiment_proposed
growth.channel_anomaly_detected
growth.conversion_changed
growth.retention_changed
```

Avoid creating redundant events when experiment/analytics events already express the fact.

---

# 70. Owner Interaction Events

Recommended:

```text
owner.decision_requested
owner.decision_received
owner.override
owner.correction
owner.directive_added
owner.directive_changed
owner.directive_retired
```

---

# 71. Owner Decision Requested

```yaml
event_type: owner.decision_requested
actor_type: AGENT
data:
  decision_id:
  question:
  recommendation:
  reason_code:
  deadline:
```

---

# 72. Owner Decision Received

```yaml
event_type: owner.decision_received
actor_type: OWNER
data:
  decision_id:
  selected_option:
  directive_ref:
```

Do not over-record private free-form owner content when structured decision data is sufficient.

---

# 73. Owner Correction

```yaml
event_type: owner.correction
data:
  affected_task:
  correction_category:
  affected_agent:
  regression_candidate:
```

Owner corrections should feed autonomy improvement.

---

# 74. Cost Events

Recommended:

```text
cost.usage_recorded
cost.threshold_warning
cost.anomaly_detected
cost.budget_exceeded
cost.saving_verified
```

---

# 75. Cost Usage

```yaml
event_type: cost.usage_recorded
data:
  cost_category:
  amount_usd:
  provider:
  mission_id:
  agent_id:
```

Use aggregation where per-call event volume would be excessive.

---

# 76. Security Events

Recommended:

```text
security.finding_detected
security.secret_exposure_detected
security.permission_change_requested
security.permission_change_applied
security.incident_opened
security.incident_contained
security.finding_resolved
```

Do not store exploitable secret values.

---

# 77. Incident Events

Recommended:

```text
incident.opened
incident.severity_changed
incident.mitigated
incident.resolved
incident.postmortem_completed
```

---

# 78. Incident Opened

```yaml
event_type: incident.opened
severity: ERROR
data:
  incident_id:
  category:
  severity_level:
  customer_impact:
  incident_owner:
```

---

# 79. Recovery Events

Recommended:

```text
backup.completed
backup.failed
restore_test.started
restore_test.completed
rollback.started
rollback.completed
recovery.verified
```

---

# 80. Scheduler Events

Recommended:

```text
scheduler.job_started
scheduler.job_completed
scheduler.job_failed
scheduler.job_retried
scheduler.job_disabled
scheduler.duplicate_prevented
scheduler.lock_stale
```

---

# 81. Evaluation Events

Recommended:

```text
evaluation.started
evaluation.completed
evaluation.failed
agent.trust_promoted
agent.trust_degraded
agent.trust_suspended
```

---

# 82. Evaluation Completed

```yaml
event_type: evaluation.completed
data:
  evaluation_id:
  agent_id:
  agent_version:
  score:
  result:
  critical_failures:
  trust_recommendation:
```

---

# 83. Self-Improvement Events

Recommended:

```text
self_improvement.constraint_identified
self_improvement.proposed
self_improvement.started
self_improvement.measured
self_improvement.adopted
self_improvement.revised
self_improvement.rolled_back
self_improvement.abandoned
```

---

# 84. Self-Improvement Adopted

```yaml
event_type: self_improvement.adopted
data:
  improvement_id:
  target:
  baseline:
  result:
  guardrails:
  change_ref:
```

---

# 85. Learning Events

Recommended:

```text
learning.recorded
learning.standardized
learning.invalidated
```

---

# 86. Decision Events

Recommended:

```text
decision.recorded
decision.superseded
```

Material architecture/business decisions should remain in `DECISIONS.md`; events record lifecycle.

---

# 87. Event Privacy

Apply data minimization.

Ask:

> Does this event need this field to support a decision, audit, measurement, or recovery?

If not, do not store it.

---

# 88. Customer Identity

Prefer pseudonymous identifiers where identity is not required.

Do not put sensitive personal information into general autonomy telemetry.

---

# 89. Secret Filtering

Before persistence, scan event payloads for:

- API keys
- tokens
- passwords
- private keys
- connection strings
- session secrets

Reject/redact as appropriate.

---

# 90. Free-Text Minimization

Prefer controlled fields and reason codes over large free-text payloads.

Benefits:

- lower storage
- safer telemetry
- easier querying
- easier dashboards
- less accidental secret leakage

---

# 91. Reason Codes

Examples:

```yaml
reason_code:
  - PRIMARY_CONSTRAINT
  - INCIDENT
  - OWNER_DIRECTIVE
  - POLICY_REQUIRED
  - EXPERIMENT
  - MAINTENANCE
  - COST_ANOMALY
  - SECURITY
```

Extend carefully.

---

# 92. Failure Classes

Use canonical failure classes from `AUTONOMY-HEALTH.md`:

- ROUTING
- REQUIREMENTS
- CONTEXT
- DATA
- TOOL
- AUTHORITY
- IMPLEMENTATION
- TEST
- DEPLOYMENT
- VERIFICATION
- POLICY
- EXTERNAL
- UNKNOWN

---

# 93. Event Idempotency

Where external systems may retry delivery, support an idempotency key.

```yaml
idempotency_key:
```

Prevent duplicate logical events.

---

# 94. Event Ordering

Do not assume perfect global ordering across distributed sources.

Use timestamps, correlation IDs, and source sequence where necessary.

---

# 95. Source Sequence

Optional:

```yaml
source_sequence:
```

Useful for ordering events from one producer.

---

# 96. Append-Only Principle

Prefer append-only storage.

Corrections should generally produce a correction/superseding event rather than silently rewriting history.

---

# 97. Event Correction

Example:

```text
analytics.metric_updated
↓
analytics.metric_corrected
```

Preserve auditability.

---

# 98. Retention

Retention should vary by event type.

Potential categories:

- audit-critical
- operational
- analytical
- high-volume telemetry

Define actual periods in data/privacy governance rather than inventing them here.

---

# 99. Event Volume

Do not emit an autonomy event for every trivial token or internal reasoning step.

Capture material state transitions and decision-useful facts.

---

# 100. High-Volume Product Analytics

Customer page views/clicks may belong in a dedicated analytics platform.

The autonomy event system may ingest aggregates or key lifecycle events rather than duplicating all web analytics.

---

# 101. Event Store

Potential implementation options:

- PostgreSQL table
- append-only JSONL initially
- event/analytics warehouse
- message queue + database

Choose based on actual architecture.

Do not add Kafka or complex streaming infrastructure without demonstrated need.

---

# 102. Recommended Bootstrap

For an early implementation, a simple durable database table may be enough.

Example conceptual schema:

```sql
autonomy_events
---------------
event_id
event_type
schema_version
occurred_at
recorded_at
source
environment
severity
mission_id
task_id
agent_id
actor_type
correlation_id
causation_id
resource_refs
evidence_refs
data
```

Actual database design should follow the project's stack and data governance.

---

# 103. Event API

Potential internal interface:

```text
emit_event(event)
query_events(filters)
get_event(event_id)
```

Keep write interface narrow.

---

# 104. Validation

Reject events that:

- lack required fields
- use unknown schema version
- contain invalid event type
- contain secret-like data
- exceed payload limits
- violate field types

---

# 105. Event Registry

Maintain a machine-readable registry of valid event types.

Potential:

```text
schemas/events/
```

or:

```text
event-registry.yaml
```

Do not create parallel definitions that drift from this policy without generation/validation.

---

# 106. Schema Evolution

For breaking changes:

1. introduce new version
2. support migration/dual-read if required
3. update producers
4. update consumers
5. verify dashboard/metrics
6. retire old version intentionally

---

# 107. Event Consumers

Potential consumers:

```text
Mission Control Builder
Executive Dashboard
Autonomy Health Calculator
Agent Scorecards
Scheduler
Incident Monitor
Cost Monitor
Experiment Analyzer
Self-Improvement Analyzer
```

---

# 108. Mission Control Projection

Mission Control should be derivable as much as practical from authoritative events plus live system state.

Example:

```text
latest mission.started
minus mission.completed
→ current mission candidate
```

Do not rely on event projection alone for facts requiring current runtime verification.

---

# 109. Executive Dashboard Projection

Examples:

```text
task.completed
→ autonomous work count

owner.decision_requested
→ owner decision queue

deployment.verified
→ latest production release

incident.opened/resolved
→ incident status
```

---

# 110. Autonomy Health Projection

Examples:

```text
task.completed + owner interaction
→ autonomous completion rate

task.rerouted
→ reroute rate

deployment.failed
→ change failure rate

owner.correction
→ owner correction rate
```

---

# 111. Agent Scorecard Projection

Group by:

```yaml
agent_id
agent_version
```

Calculate:

- tasks
- success
- failures
- reroutes
- cost
- owner escalations
- policy violations

---

# 112. Near-Real-Time Dashboard

The event system should support low-latency updates without requiring literal millisecond streaming.

For this business, "near real time" should mean current enough to support operational decisions.

Avoid unnecessary infrastructure complexity.

---

# 113. Event-to-Metric Latency

Track:

```yaml
event_pipeline:
  last_event_received:
  projection_lag:
  failed_events:
  dead_letter_count:
```

---

# 114. Dead-Letter Handling

Invalid/unprocessable events should not silently disappear.

Use a recoverable quarantine/dead-letter mechanism appropriate to architecture.

---

# 115. Event Replay

Where architecture supports projections, events should be replayable to rebuild derived state.

---

# 116. Replay Safety

Replaying events must not re-trigger external side effects such as:

- payments
- emails
- deployments
- purchases

Separate event consumption from commands.

---

# 117. Command vs Event

A command requests action:

```text
Deploy release X
```

An event records fact:

```text
deployment.verified
```

Do not treat event replay as command replay.

---

# 118. Audit Trail

For important actions, the event chain should answer:

```text
Why?
→ mission/task

Who?
→ agent/owner

What authority?
→ task/authorization reference

What changed?
→ resource/change reference

Was it verified?
→ verification event

What happened afterward?
→ measurement/outcome event
```

---

# 119. Deployment Trace Example

```text
mission.started
↓
task.assigned
↓
github.pull_request_opened
↓
github.pull_request_merged
↓
deployment.started
↓
deployment.completed
↓
deployment.verified
↓
experiment.measurement_completed
↓
experiment.decision_made
```

---

# 120. Owner Decision Trace Example

```text
owner.decision_requested
↓
owner.decision_received
↓
decision.recorded
↓
task.resumed
```

---

# 121. Failure Trace Example

```text
task.started
↓
tool/API failure
↓
task.failed
↓
task.rerouted or retried
↓
task.completed
↓
learning.recorded
```

---

# 122. Self-Improvement Trace Example

```text
autonomy anomaly
↓
self_improvement.constraint_identified
↓
self_improvement.proposed
↓
evaluation.started
↓
self_improvement.started
↓
evaluation.completed
↓
self_improvement.measured
↓
self_improvement.adopted
```

---

# 123. Customer Value Trace

The most valuable future capability is connecting autonomous work to customer outcomes.

Example:

```text
SEO/content improvement
→ qualified visitor
→ desired function selected
→ diagnosis
→ quest started
→ quest completed
→ outcome confirmed
→ product purchase or no-purchase solution
→ sustain check
```

This enables optimization for outcomes rather than traffic alone.

---

# 124. Revenue Trace

Where privacy and attribution permit:

```text
mission
→ experiment
→ customer journey
→ commerce.checkout_completed
→ order
→ revenue
```

Do not overstate causal attribution.

---

# 125. Cost-to-Value Trace

Eventually:

```text
Agent/API/Infrastructure Cost
→ Mission
→ Verified Customer/Business Result
```

This supports autonomy ROI.

---

# 126. Event Quality Metrics

Track:

- invalid events
- duplicate events
- late events
- missing required relationships
- orphaned task events
- unknown agent IDs
- unknown mission IDs
- schema errors

---

# 127. Orphan Detection

Examples:

- task.completed without task.created/assigned
- deployment.verified without release/commit
- agent.completed with unknown agent ID
- owner decision response with unknown decision ID

Flag for reconciliation.

---

# 128. Event Reconciliation

Run periodic checks against:

- GitHub
- runtime
- scheduler
- commerce
- analytics

Events are telemetry, not a license to ignore authoritative systems.

---

# 129. Event Security

Restrict who can:

- emit events
- read sensitive event categories
- alter schemas
- delete event history

Follow least privilege.

---

# 130. Event Integrity

Where appropriate, protect audit-critical events from silent modification/deletion.

---

# 131. Event Availability

Loss of the event system should not necessarily take down the customer website.

Design graceful degradation.

Critical business transactions should remain authoritative in their own systems.

---

# 132. Event Failure Behavior

If event persistence fails:

- do not fabricate success
- preserve primary operation where safe
- retry appropriately
- alert if audit-critical
- reconcile later

---

# 133. Owner Dashboard Event Feed

Useful recent events may include:

- production deployed
- experiment completed
- major customer milestone
- incident opened/resolved
- owner decision requested
- autonomy improvement adopted

Avoid flooding owner with low-value events.

---

# 134. Executive Activity Feed

Recommended display:

```text
TIME      EVENT                     RESULT
14:32     Production deployed       Verified
13:10     Entryway test completed    Inconclusive
11:45     Agent routing improved     Adopted
09:20     Backup verified            Passed
```

Only verified events.

---

# 135. Alerting

Not every event is an alert.

Alerts should derive from event conditions such as:

- CRITICAL security event
- production outage
- commerce outage
- budget threshold
- failed recovery
- required owner decision deadline

---

# 136. Event-Based Automation

Scheduler/orchestrator may eventually react to events.

Example:

```text
deployment.failed
→ incident workflow
```

Use safeguards against feedback loops.

---

# 137. Feedback Loop Prevention

Event-driven actions must have:

- causation IDs
- idempotency
- retry limits
- loop detection
- authority checks

---

# 138. Event Naming Governance

Do not allow each agent to invent near-duplicate event names.

Bad:

```text
task.done
task.finished
task.success
```

Prefer one canonical:

```text
task.completed
```

---

# 139. Event Deprecation

When replacing an event type:

- mark deprecated
- update producers
- update consumers
- migrate projections
- retire intentionally

---

# 140. Initial Implementation Priorities

Phase 1 should capture:

1. missions
2. tasks
3. agents
4. routing/handoffs
5. GitHub/PRs
6. deployments
7. failures
8. owner decisions
9. experiments
10. costs
11. evaluations
12. self-improvement

Then add customer/commerce events according to existing analytics architecture.

---

# 141. Phase 1 Minimum Events

```text
mission.started
mission.completed
task.assigned
task.started
task.completed
task.failed
task.rerouted
agent.invoked
agent.completed
handoff.completed
github.pull_request_opened
github.pull_request_merged
deployment.started
deployment.verified
deployment.failed
owner.decision_requested
owner.decision_received
experiment.started
experiment.measurement_completed
experiment.decision_made
evaluation.completed
self_improvement.adopted
```

---

# 142. Bootstrap Process

1. inspect actual architecture
2. identify existing telemetry
3. identify existing database
4. avoid duplicating existing analytics
5. define event registry
6. implement envelope/schema validation
7. implement durable storage
8. instrument orchestrator first
9. instrument scheduler
10. instrument GitHub/deployment lifecycle
11. instrument agent lifecycle
12. instrument owner decision lifecycle
13. build Mission Control projection
14. build autonomy-health metrics
15. verify event integrity
16. add customer/business events incrementally

---

# 143. Do Not Overbuild

The system does not need a complex enterprise event platform on day one.

Start with the simplest reliable implementation compatible with:

- Docker/VPS architecture
- current application stack
- expected event volume
- backup/recovery
- dashboard requirements

---

# 144. Initial State

```yaml
autonomy_events:
  status: NOT_IMPLEMENTED_OR_UNVERIFIED
  schema_version: "1.0"
  event_store: UNKNOWN
  producers: UNKNOWN
  consumers: UNKNOWN
  last_verified: UNKNOWN
```

Do not claim implementation until verified.

---

# 145. First Event-System Mission

```yaml
mission:
  title: Establish Autonomous Operating Telemetry
  objective: >
    Implement the smallest reliable event model required to measure
    agent work, task lifecycle, deployments, owner interactions,
    experiments, costs, and autonomy health.
  success:
    - validated event schema
    - durable storage
    - orchestrator events
    - task events
    - deployment events
    - dashboard projection
    - autonomy health baseline support
```

---

# 146. Event Testing

Test:

- valid event accepted
- invalid schema rejected
- duplicate idempotency handled
- secret-like payload blocked/redacted
- unknown event type rejected
- replay does not trigger side effects
- event projection rebuild works
- missing relationships detected

---

# 147. Event Backup

Event data required for audit/learning should participate in backup and recovery.

---

# 148. Event Restore Test

Verify restored event data can rebuild required projections.

---

# 149. Performance

Measure before optimizing.

Do not add streaming infrastructure solely because "near real time" sounds like a streaming requirement.

---

# 150. Event Maturity Model

## Level 0 — Chat/Log History

Actions are reconstructed manually.

## Level 1 — Structured Task Events

Core agent/task lifecycle is captured.

## Level 2 — Operational Events

GitHub, deployment, incidents, owner decisions, and experiments are connected.

## Level 3 — Business Events

Customer outcomes, commerce, cost, and growth connect to missions.

## Level 4 — Autonomous Intelligence

Mission Control, dashboards, agent scorecards, and autonomy health are derived automatically.

## Level 5 — Closed-Loop Operating System

Structured events connect owner direction → autonomous work → technical changes → customer outcomes → revenue/cost → learning → self-improvement, creating an auditable continuous-improvement loop.

---

# 151. Non-Negotiable Rules

Claude and subagents must not:

- treat chat history as the sole audit system
- fabricate events
- backdate events deceptively
- store secrets in events
- store unnecessary sensitive customer data
- store private chain-of-thought
- emit dozens of redundant event types
- use event replay to repeat external side effects
- silently rewrite audit-critical history
- claim deployment verified without verification evidence
- claim customer/business value without evidence
- use events as a replacement for authoritative transaction systems
- allow every agent to invent its own schema
- create complex streaming infrastructure without demonstrated need
- allow event-driven automation to bypass authority checks
- hide failed event ingestion
- let telemetry failure silently corrupt executive metrics

---

# 152. Final Principle

An autonomous organization needs institutional memory that is more reliable than conversation history.

The event system should make this chain visible:

```text
Owner Direction
↓
Mission
↓
Task
↓
Agent
↓
Action
↓
Change
↓
Verification
↓
Customer / Business Result
↓
Learning
↓
Self-Improvement
```

When that chain is structured and queryable, Claude can answer not only:

**What did we do?**

but:

**Why did we do it?**

**Who did it?**

**Was it authorized?**

**Did it work?**

**What did it cost?**

**Did customers benefit?**

**Did revenue or margin improve?**

**What did the system learn?**

**What should happen next?**

That is the purpose of `AUTONOMY-EVENTS.md`.
