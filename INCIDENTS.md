# INCIDENTS.md

## 6S Success Incident Management, History, and Learning Standard

**Document role:** Canonical incident source of truth for 6S Success\
**Status:** ACTIVE\
**Owner:** Founder / Owner\
**Operational steward:** Claude Code autonomous operating system\
**Primary responders:** DevOps/SRE, GitHub Manager, Hostinger VPS/Docker
Manager, Security, Data, Product, and other domain agents as routed\
**Last updated:** 2026-09-11\
**Scope:** Production, customer experience, data, analytics,
security/privacy, AI behavior, deployments, infrastructure,
integrations, autonomous agents, commerce, services, and other material
operating failures

------------------------------------------------------------------------

# 1. Purpose

`INCIDENTS.md` defines how 6S Success detects, records, triages,
responds to, communicates, resolves, reviews, and learns from incidents.

It is both:

1.  the standard for incident management; and
2.  the canonical register/history of material incidents.

The objective is simple:

> **Restore safe customer and business operation quickly, preserve
> evidence, understand what actually happened, prevent recurrence where
> justified, and turn meaningful failures into organizational
> learning.**

Incident management must remain proportional to the stage and scale of
6S Success. Do not create enterprise bureaucracy for minor defects, but
do not allow an autonomous system to hide or normalize serious failures.

------------------------------------------------------------------------

# 2. Incident Principle

``` text
DETECT
  ↓
VERIFY
  ↓
CLASSIFY
  ↓
CONTAIN
  ↓
MITIGATE
  ↓
RESTORE
  ↓
VERIFY RECOVERY
  ↓
UNDERSTAND
  ↓
CORRECT / PREVENT
  ↓
LEARN
  ↓
CLOSE
```

Restoration comes before perfect diagnosis when customer, data,
security, or production impact is ongoing.

------------------------------------------------------------------------

# 3. Relationship to Other Canonical Files

This file integrates with:

``` text
CLAUDE.md
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
PRODUCT-CATALOG.md
CONTENT-CATALOG.md
CHANGELOG.md
```

It should also integrate with security, testing, observability, GitHub,
VPS/Docker, event handling, context routing, agent evaluation, memory,
and autonomous orchestration standards.

------------------------------------------------------------------------

# 4. Incident vs Risk vs Issue vs Defect

## Incident

A material operational event that causes or threatens customer,
production, security, privacy, data, financial, or business impact and
requires coordinated response.

## Risk

A possible future event.

## Issue

A known problem that exists but may not require incident response.

## Defect

A product/software deviation from expected behavior.

A defect becomes an incident when its impact/severity warrants
coordinated operational response.

Example:

``` text
RISK:
Quest analytics could stop recording events.

DEFECT:
One optional analytics field is missing.

INCIDENT:
Production stopped recording quest completions, making customer
outcome reporting unreliable.

ISSUE:
Historical completion events need reconciliation after recovery.
```

------------------------------------------------------------------------

# 5. What Qualifies as an Incident

Examples include:

-   production outage;
-   material feature failure;
-   failed or harmful deployment;
-   corrupted/lost data;
-   analytics failure affecting decisions;
-   exposed credential;
-   suspected unauthorized access;
-   household-image privacy exposure;
-   payment/billing malfunction;
-   product recommendation causing systemic customer harm;
-   autonomous agent performing an unauthorized consequential action;
-   Docker/VPS failure materially affecting production;
-   backup or restore failure when recovery capability is needed;
-   major third-party integration outage;
-   customer-facing AI behavior materially violating product/safety
    rules;
-   repeated failure indicating systemic instability.

Routine bugs and minor content errors generally belong in the backlog
unless impact warrants escalation.

------------------------------------------------------------------------

# 6. Incident Categories

Canonical categories:

``` text
AVAILABILITY
PERFORMANCE
DEPLOYMENT
INFRASTRUCTURE
DATABASE
DATA_INTEGRITY
ANALYTICS
SECURITY
PRIVACY
AI_MODEL
AUTONOMY
AGENT
INTEGRATION
COMMERCE
PAYMENT
CONTENT
CUSTOMER_EXPERIENCE
SAFETY
SERVICE_OPERATIONS
BACKUP_RECOVERY
OTHER
```

------------------------------------------------------------------------

# 7. Incident Severity

Use customer/business impact rather than technical drama.

## SEV-0 --- CRITICAL

Examples:

-   confirmed major security/privacy breach;
-   destructive production/data event;
-   widespread unsafe customer guidance with immediate material risk;
-   loss of owner control over autonomous production behavior;
-   catastrophic business-critical outage.

Response:

``` text
Immediate containment.
Owner escalation.
Freeze relevant autonomous actions.
Preserve evidence.
Activate recovery/incident command.
```

## SEV-1 --- HIGH

Examples:

-   production unavailable for meaningful customer use;
-   critical customer workflow broken;
-   significant data loss/corruption;
-   serious deployment failure;
-   material payment failure;
-   high-impact security event under investigation.

Response:

``` text
Immediate operational response.
Owner notified promptly.
Mitigation prioritized above normal roadmap work.
```

## SEV-2 --- MODERATE

Examples:

-   major feature degraded;
-   analytics materially incomplete;
-   partial integration outage;
-   repeated container instability;
-   meaningful but bounded customer impact.

Response:

``` text
Prompt response.
Owner included in executive reporting unless direct decision required.
```

## SEV-3 --- LOW

Examples:

-   bounded production defect;
-   limited degradation;
-   workaround available;
-   no material data/security/safety impact.

Response:

``` text
Track and repair through normal operational workflow.
Escalate only if impact grows.
```

## SEV-4 --- MINOR

Generally not an incident. Track as defect/task unless pattern indicates
systemic risk.

------------------------------------------------------------------------

# 8. Severity Factors

Evaluate:

``` text
customer impact
number/percentage affected
duration
core workflow impact
data integrity
privacy
security
safety
revenue/payment
brand/trust
recoverability
spread/velocity
owner-control impact
```

Do not lower severity merely because few users have reported the
problem.

------------------------------------------------------------------------

# 9. Incident Status

Use:

``` text
DETECTED
VERIFYING
OPEN
CONTAINING
MITIGATING
MONITORING
RESOLVED
REVIEWING
CLOSED
REOPENED
```

`RESOLVED` means service/impact has been restored or stopped.

`CLOSED` means required follow-up and review are complete.

------------------------------------------------------------------------

# 10. Incident Record Schema

``` yaml
incident:
  id:
  title:
  severity:
  category:
  status:
  detected_at:
  occurred_at:
  acknowledged_at:
  mitigated_at:
  resolved_at:
  closed_at:
  environment:
  affected_systems:
  affected_customers:
  customer_impact:
  business_impact:
  data_impact:
  security_privacy_impact:
  detection_source:
  reporter:
  incident_lead:
  technical_lead:
  owner_notified:
  symptoms:
  known_facts:
  hypotheses:
  immediate_actions:
  mitigation:
  recovery:
  verification:
  root_cause_status:
  root_cause:
  contributing_factors:
  related_deployment:
  related_change:
  related_event_ids:
  related_risk_ids:
  related_mission_ids:
  corrective_actions:
  preventive_actions:
  learnings:
  evidence_refs:
```

------------------------------------------------------------------------

# 11. Incident ID

Use stable IDs:

``` text
INC-YYYY-NNN
```

Example:

``` text
INC-2026-001
```

Do not reuse IDs.

------------------------------------------------------------------------

# 12. Facts vs Hypotheses

During response, maintain separate sections.

## Known Facts

Verified observations.

## Hypotheses

Possible explanations still under investigation.

Example:

``` text
FACT:
Quest completion API began returning HTTP 500 at 14:03.

HYPOTHESIS:
The database migration introduced an incompatible constraint.
```

Never silently promote a hypothesis into root cause.

------------------------------------------------------------------------

# 13. Root Cause Status

Use:

``` text
UNKNOWN
INVESTIGATING
LIKELY
CONFIRMED
NOT_REQUIRED
```

A root cause is `CONFIRMED` only when evidence supports it sufficiently
to explain the failure mechanism.

------------------------------------------------------------------------

# 14. Incident Roles

For significant incidents:

## Incident Lead

Coordinates response, state, priorities, and communication.

## Technical/Domain Lead

Investigates and implements mitigation.

## Owner

Makes protected decisions when required.

## Scribe / System Recorder

Maintains timeline, facts, actions, and evidence.

In small incidents one agent/person may hold multiple roles, but
responsibilities remain conceptually distinct.

------------------------------------------------------------------------

# 15. Agent Routing

Potential lead agents:

``` text
DevOps/SRE
Hostinger VPS/Docker Manager
GitHub Manager
Security
Data/Analytics
Product
AI/ML
Commerce
Content
Service Operations
```

Use one incident lead.

Do not allow multiple agents to independently make conflicting
production changes.

------------------------------------------------------------------------

# 16. Detection Sources

Incidents may originate from:

``` text
health check
monitoring alert
customer report
owner report
agent observation
deployment verification
analytics anomaly
security scanner
GitHub check
Docker health
VPS resource alert
database alert
payment/integration alert
experiment guardrail
```

Detection source should be recorded.

------------------------------------------------------------------------

# 17. Event Integration

Canonical incident events may include:

``` text
incident.detected
incident.opened
incident.acknowledged
incident.severity_changed
incident.mitigated
incident.resolved
incident.reopened
incident.postmortem_started
incident.postmortem_completed
incident.closed
```

Events describe state changes. They do not independently authorize
protected actions.

------------------------------------------------------------------------

# 18. Automatic Incident Creation

Automation may open incidents when predefined high-confidence conditions
occur.

Examples:

``` text
production health check persistently failing
deployment verification failed
database unavailable
critical container repeatedly unhealthy
security control raises verified high-severity finding
```

Avoid incident spam from transient noise.

Use persistence windows, cooldowns, deduplication, and correlation.

------------------------------------------------------------------------

# 19. Incident Deduplication

Before opening a new incident, check:

-   same affected system;
-   same symptom;
-   same correlation/deployment;
-   existing open incident;
-   recent recurrence.

One underlying failure should not create dozens of incidents.

------------------------------------------------------------------------

# 20. First Response

For material incidents:

``` text
1. Confirm the signal.
2. Determine affected environment.
3. Determine customer/business impact.
4. Stop unsafe autonomous behavior if relevant.
5. Preserve evidence.
6. Identify last known good state.
7. Check recent changes.
8. Choose containment/mitigation.
9. Communicate appropriately.
10. Verify recovery.
```

------------------------------------------------------------------------

# 21. Stop-the-Line Conditions

Pause relevant deployments/automation when there is credible evidence
of:

-   data corruption;
-   privacy/security compromise;
-   unsafe customer guidance at scale;
-   repeated failed deployments;
-   unknown autonomous destructive behavior;
-   inability to verify production state;
-   broken rollback/recovery during active incident.

Scope the freeze to the affected domain where possible.

------------------------------------------------------------------------

# 22. Deployment Incident Procedure

When a deployment fails:

``` text
deployment.failed
      ↓
verify production state
      ↓
determine customer impact
      ↓
stop further rollout
      ↓
evaluate rollback / forward fix
      ↓
apply authority rules
      ↓
restore
      ↓
health verification
      ↓
incident review
```

Do not blindly retry.

Do not blindly rollback if rollback itself is unsafe.

------------------------------------------------------------------------

# 23. GitHub Investigation

For change-related incidents capture:

``` text
commit
branch
PR
checks
release/tag
deployment
author/agent
mission/task
changed files
test results
```

The purpose is traceability, not blame.

------------------------------------------------------------------------

# 24. VPS/Docker Investigation

Check as appropriate:

``` text
host health
CPU
memory
disk
network
container status
restart count
health checks
logs
image version
environment/config
volumes
database connectivity
reverse proxy
TLS/certificate
recent deployment
```

Do not restart containers repeatedly without understanding whether that
risks data or hides the symptom.

------------------------------------------------------------------------

# 25. Database Incident Procedure

Protect data first.

Potential actions:

``` text
stop harmful writes
snapshot/backup if safe
verify integrity
identify affected records
restore/reconcile
validate application behavior
```

Never run destructive repair commands without authority and evidence.

------------------------------------------------------------------------

# 26. Analytics Incident Procedure

Analytics failure is material when it affects decisions, experiments,
revenue reporting, or customer outcome measurement.

Response:

-   identify missing/duplicated events;
-   determine affected time window;
-   preserve raw data;
-   repair instrumentation;
-   backfill/reconcile if trustworthy;
-   mark dashboard periods as incomplete;
-   re-evaluate decisions made using affected data.

Never fabricate missing metrics.

------------------------------------------------------------------------

# 27. Household Image Privacy Incident

Potential triggers:

-   unauthorized image access;
-   public exposure;
-   wrong-user image association;
-   retention/deletion failure;
-   image included in inappropriate logs/events;
-   insecure storage reference.

Response priorities:

``` text
contain access
preserve evidence
determine scope
protect affected data
follow applicable privacy/security process
notify owner
correct storage/access path
verify deletion/restriction where required
```

Do not copy sensitive images unnecessarily during investigation.

------------------------------------------------------------------------

# 28. AI Behavior Incident

An AI behavior issue may qualify when the system systematically:

-   gives unsafe cleaning advice;
-   overstates visual diagnosis;
-   repeatedly misclassifies spaces in a harmful way;
-   recommends inappropriate products;
-   ignores explicit customer constraints;
-   exposes private data;
-   performs unauthorized autonomous actions.

Mitigation may include disabling a feature, narrowing scope, adding
confirmation, changing routing, or reverting a
prompt/model/configuration.

------------------------------------------------------------------------

# 29. Safety Incident

Household 6S activities can involve chemicals, ladders, heavy objects,
electrical areas, medications, child safety, trip hazards, and
accessibility.

Safety-related incidents receive conservative handling.

Do not gamify response in a way that encourages rushing.

------------------------------------------------------------------------

# 30. Commerce Incident

Examples:

-   incorrect price;
-   broken affiliate destination;
-   wrong product substitution;
-   duplicate order workflow;
-   inventory mismatch;
-   misleading kit contents;
-   margin calculation error used operationally.

Protect customer trust before conversion.

------------------------------------------------------------------------

# 31. Service Incident

Potential:

-   missed appointment;
-   property damage;
-   injury;
-   scope dispute;
-   unsafe work;
-   billing error;
-   privacy concern inside customer's home.

As services scale, incident handling must integrate appropriate
insurance/legal/customer-care procedures.

------------------------------------------------------------------------

# 32. Autonomous Agent Incident

Examples:

``` text
agent deploys outside authority
agent changes protected configuration
agent creates repeated failing loop
agent deletes/overwrites valuable data
agent exposes secret
agent executes expensive runaway workload
agent uses stale superseded standard
```

Immediate response may include:

``` text
disable affected automation
revoke credentials
stop mission
preserve logs
inspect causation/context
restore state
```

------------------------------------------------------------------------

# 33. Context Failure Investigation

When an agent behaves incorrectly, inspect:

``` text
what task was requested?
what context manifest was provided?
which canonical files were loaded?
were any superseded files used?
what authority was supplied?
what live state was known?
what assumptions were made?
```

Do not assume the model itself is the only cause.

------------------------------------------------------------------------

# 34. Event Loop Incident

If autonomous events recursively trigger actions:

``` text
stop consumer/automation
preserve correlation chain
identify loop
deduplicate queued work
verify side effects
add loop guard/state check
test before restart
```

------------------------------------------------------------------------

# 35. AI/Tool Cost Incident

A runaway automation may create material API/tool cost even without
customer outage.

Trigger when spending exceeds defined thresholds or abnormal usage is
detected.

Response:

-   stop runaway workload;
-   identify source;
-   quantify cost;
-   add caps/rate limits/aggregation;
-   verify no hidden recurrence.

------------------------------------------------------------------------

# 36. Communication Standard

Incident communication should answer:

``` text
What happened?
What is affected?
What is not affected?
What are we doing?
What is the current status?
When is the next update?
Does the owner need to decide anything?
```

Avoid speculative technical detail during active response.

------------------------------------------------------------------------

# 37. Owner Notification

Notify promptly for:

``` text
SEV-0
SEV-1
material privacy/security event
material safety event
significant financial exposure
owner-control/autonomy failure
decision requiring protected authority
```

SEV-2 may normally appear in the Executive Brief unless owner action is
required.

------------------------------------------------------------------------

# 38. Customer Communication

Customer communication, when required, should be:

-   accurate;
-   concise;
-   non-speculative;
-   clear about impact;
-   clear about remediation;
-   appropriately transparent.

Legal/privacy/security notifications must follow applicable
requirements.

------------------------------------------------------------------------

# 39. Incident Timeline

For significant incidents record:

``` text
HH:MM detection
HH:MM acknowledgement
HH:MM first mitigation
HH:MM customer impact changed
HH:MM rollback/fix
HH:MM recovery
HH:MM verification
```

Use actual timestamps.

------------------------------------------------------------------------

# 40. Evidence Preservation

Potential evidence:

``` text
logs
metrics
screenshots
event IDs
commit/PR
release
container state
configuration
database evidence
customer reports
agent task/context manifest
security findings
```

Do not alter evidence unnecessarily.

------------------------------------------------------------------------

# 41. Mitigation vs Resolution

## Mitigation

Reduces/stops impact.

## Resolution

Restores intended safe operation.

Example:

``` text
MITIGATION:
Disable photo analysis.

RESOLUTION:
Correct faulty classifier/routing and safely restore photo analysis.
```

------------------------------------------------------------------------

# 42. Recovery Verification

Never declare resolved solely because a change deployed.

Verify:

``` text
health checks
core customer flow
data integrity
error rate
affected metric
security/privacy condition
no recurrence during appropriate observation window
```

------------------------------------------------------------------------

# 43. Rollback

Rollback should have:

``` text
known target version
data compatibility
configuration compatibility
authority
verification
```

A code rollback may not reverse a database migration or external side
effect.

------------------------------------------------------------------------

# 44. Post-Incident Review

Required for:

-   SEV-0;
-   SEV-1;
-   recurring SEV-2;
-   material security/privacy/safety incidents;
-   major autonomous-control failures.

Use a lightweight review for smaller incidents when learning value is
high.

------------------------------------------------------------------------

# 45. Postmortem Structure

``` markdown
# [INC-ID] Incident Review

## Summary
## Customer / Business Impact
## Timeline
## Detection
## Known Facts
## Root Cause
## Contributing Factors
## What Worked
## What Failed
## Why Controls Did Not Prevent/Detect It
## Corrective Actions
## Preventive Actions
## Risk Updates
## Learnings
## Owner Decisions
```

------------------------------------------------------------------------

# 46. Blameless but Accountable

Focus on:

``` text
system
process
control
context
test
design
decision
```

rather than personal blame.

Blameless does not mean avoiding accountability for fixing weak systems.

------------------------------------------------------------------------

# 47. Five-Why / Root-Cause Discipline

6S Success can use Lean root-cause methods, but do not force five whys
mechanically.

Root cause should explain the failure mechanism and lead to useful
corrective action.

Often there are multiple contributing causes.

------------------------------------------------------------------------

# 48. Corrective Action

Corrective action fixes the current failure.

Example:

``` text
repair missing analytics event
```

# 49. Preventive Action

Preventive action reduces recurrence.

Example:

``` text
add contract test verifying quest.completed is emitted in production-like test
```

Do not create excessive preventive work for low-impact one-off failures.

------------------------------------------------------------------------

# 50. Incident-to-Risk

After review:

``` text
incident
 ↓
existing risk reassessed
or
new risk created
 ↓
mitigation updated
```

A realized risk should improve the risk model.

------------------------------------------------------------------------

# 51. Incident-to-Learning

Validated incident learning should enter `LEARNINGS.md`.

Example:

``` text
Learning:
Deployment health checks that test container status alone do not verify
the customer quest workflow.

Action:
Add synthetic quest-generation/completion verification.
```

------------------------------------------------------------------------

# 52. Incident-to-Backlog

Corrective/preventive actions become executable backlog work with:

``` text
owner
priority
acceptance criteria
related incident ID
```

Do not leave them buried in postmortem prose.

------------------------------------------------------------------------

# 53. Incident-to-Changelog

Customer-visible or operationally meaningful fixes should be reflected
in `CHANGELOG.md` when appropriate.

------------------------------------------------------------------------

# 54. Incident-to-Executive-Brief

Executive Brief should include:

-   new material incidents;
-   open critical incidents;
-   resolved material incidents;
-   material recurrence;
-   owner decision needed.

Do not include every minor defect.

------------------------------------------------------------------------

# 55. Incident Metrics

Potential metrics:

``` text
incident count by severity
MTTD
MTTA
MTTM
MTTR
recurrence rate
deployment-caused incident rate
rollback rate
customer-impact minutes
data-integrity incidents
security/privacy incidents
autonomous-action incidents
preventive-action completion
```

Metric formulas belong in `METRICS.md`.

------------------------------------------------------------------------

# 56. MTTD / MTTA / MTTM / MTTR

Use only when data quality supports them.

``` text
MTTD = mean time to detect
MTTA = mean time to acknowledge
MTTM = mean time to mitigate
MTTR = mean time to restore/resolve
```

Do not optimize response-time metrics at the expense of safe recovery.

------------------------------------------------------------------------

# 57. Recurrence

A recurrence is especially important because it suggests prior
mitigation was insufficient.

Repeated incidents should increase risk priority.

------------------------------------------------------------------------

# 58. Incident Review Cadence

## Continuous

Maintain active incident state.

## Weekly

Review open incidents, unresolved corrective actions, and recurrence.

## Monthly

Review trends and systemic weaknesses.

## Quarterly

Assess whether reliability/security/autonomy controls need strategic
investment.

------------------------------------------------------------------------

# 59. Incident History Register

Canonical table. Full write-up for each row is appended at the end of this file, after section 82.

| ID | Date | Severity | Category | Title | Status |
|---|---|---|---|---|---|
| INC-2026-08-31 | 2026-08-31 | SEV-1 | PAYMENT | Every buy button on the live site was dead for eight days | Fixed; live catalogue still lags the repository, tracked separately |
| INC-2026-09-09 | 2026-09-09 | SEV-3 | SERVICE_OPERATIONS | Two scheduled GitHub Actions workflows ran 4 to 14x slower than configured, sustained 14+ days | Root cause outside this repository; standing WARN gate, not fixable here |
| INC-2026-09-10 | 2026-09-10 | SEV-2 | CONTENT | Image generation was dead for eleven days and reported as idle work, not a broken capability | Capability fixed; no image regenerated yet, needs free RAM |

Do not fabricate historical incidents. Add a row only once the full
write-up exists below with real evidence, not from a suspicion alone.

------------------------------------------------------------------------

# 60. Initial Incident Register

Three verified incidents have been imported into this canonical file,
appended at the end after section 82, each reconstructed from the
repository's own evidence
(commit history, `ops/NIGHTLY-LOG.md`, and, for INC-2026-09-09, the GitHub
Actions API directly) rather than inferred.

This does **not** mean these are the only incidents that have ever
occurred. It means these are the ones reconstructed and verified so far;
earlier operating history has not been fully swept for others.

Potential historical events must be reviewed from GitHub, VPS/Docker,
logs, monitoring, prior reports, and owner records before entry.

------------------------------------------------------------------------

# 61. Historical Incident Reconstruction

When the operating system is connected to live resources, perform a
bounded reconstruction.

Inspect:

``` text
GitHub deployment/release history
failed CI/CD runs
VPS/Docker restart/failure history
monitoring alerts
application error logs
database incidents
security findings
backup failures
analytics gaps
owner-reported production problems
```

Only create historical incident records when evidence is sufficient.

------------------------------------------------------------------------

# 62. Do Not Backfill Fiction

Never infer:

``` text
"container restarted, therefore there was an outage"
```

without evidence.

Record uncertain observations as investigation candidates, not confirmed
incidents.

------------------------------------------------------------------------

# 63. Current Incident Readiness Gaps

Until live infrastructure is inspected, treat these as `UNKNOWN`:

``` yaml
incident_readiness:
  automated_detection: UNKNOWN
  alert_routing: UNKNOWN
  incident_event_pipeline: UNKNOWN
  production_health_checks: UNKNOWN
  synthetic_customer_flow_checks: UNKNOWN
  log_retention: UNKNOWN
  deployment_traceability: UNKNOWN
  backup_monitoring: UNKNOWN
  restore_test_status: UNKNOWN
  security_alerting: UNKNOWN
  on_call_model: NOT_REQUIRED_OR_UNKNOWN
  historical_incident_import: NOT_STARTED
```

------------------------------------------------------------------------

# 64. Minimum Viable Incident System

Near-term implementation should include:

``` text
canonical incident record
severity rules
one active incident lead
production health monitoring
deployment verification
GitHub/release traceability
VPS/Docker health
error logging
backup monitoring
owner escalation path
incident timeline
corrective-action linkage
postmortem template
```

------------------------------------------------------------------------

# 65. Phase 2 Incident Maturity

After customer usage increases:

``` text
synthetic core-flow monitoring
analytics integrity monitoring
privacy/security alerting
automated incident creation for high-confidence failures
customer-impact estimation
incident dashboard
recurrence analysis
```

------------------------------------------------------------------------

# 66. Phase 3 Incident Maturity

Only when scale justifies it:

``` text
advanced SLO/error-budget management
automated correlation
dependency mapping
more sophisticated incident command
formal on-call rotation
chaos testing
```

Do not over-engineer early.

------------------------------------------------------------------------

# 67. Core Synthetic Checks

High-value synthetic flows may eventually test:

``` text
website/app reachable
authentication if applicable
photo/upload path
Entryway quest generation
quest start
quest completion
analytics event recorded
critical database write/read
```

Do not expose real customer data in synthetic tests.

------------------------------------------------------------------------

# 68. Deployment Guardrail

A release should not be considered successful until:

``` text
deployment completed
containers/services healthy
core application responds
critical customer flow passes
critical analytics signal is present where applicable
error rate acceptable
```

------------------------------------------------------------------------

# 69. Analytics Guardrail

Because Entryway validation depends on real evidence, broken analytics
can be strategically equivalent to a product outage.

If outcome/sustain data becomes unreliable:

``` text
mark affected reporting period
stop making unsupported experiment conclusions
repair instrumentation
reconcile if possible
```

------------------------------------------------------------------------

# 70. Executive Dashboard Incident Panel

Show:

``` text
OPEN SEV-0/SEV-1
OPEN SEV-2
LATEST MATERIAL INCIDENT
PRODUCTION STATUS
LAST SUCCESSFUL DEPLOYMENT
BACKUP/RECOVERY STATUS
```

Provide drill-down rather than flooding the executive view.

------------------------------------------------------------------------

# 71. Autonomous Authority During Incidents

Claude may perform pre-authorized reversible containment and diagnostic
actions.

Examples may include:

``` text
inspect logs
inspect health
stop a failing noncritical job
pause a bounded automation
open an incident
collect evidence
run approved health checks
```

Protected or high-impact actions follow `AUTONOMY.md`.

Examples that may require owner authority depending on policy:

``` text
destructive database action
material financial commitment
broad customer notification
security/legal disclosure
irreversible production change
major service shutdown
```

------------------------------------------------------------------------

# 72. Incident Command Priority

During an active material incident:

``` text
SAFETY / PRIVACY / DATA
       ↓
STOP ACTIVE HARM
       ↓
RESTORE CORE CUSTOMER VALUE
       ↓
PRESERVE EVIDENCE
       ↓
UNDERSTAND CAUSE
       ↓
PREVENT RECURRENCE
       ↓
RETURN TO ROADMAP
```

------------------------------------------------------------------------

# 73. Customer-Value Lens

A technically healthy system can still have a customer incident.

Example:

``` text
All containers are healthy, but every generated Entryway quest contains
invalid instructions.
```

Infrastructure health is not equivalent to product health.

------------------------------------------------------------------------

# 74. 6S Lens for Incident Prevention

The 6S philosophy itself can guide operations:

## Sort

Remove obsolete jobs, dependencies, credentials, and unused
infrastructure.

## Straighten

Make ownership, logs, environments, runbooks, and deployment paths
obvious.

## Shine

Maintain system health and remove operational noise.

## Safety

Protect customer data, production, finances, and owner authority.

## Standardize

Use repeatable deploy, test, incident, and recovery procedures.

## Sustain

Verify controls continue to work.

------------------------------------------------------------------------

# 75. Incident Acceptance Tests

## Deployment Failure

Input:

``` text
New release fails health verification.
```

Expected:

``` text
Stop rollout.
Determine production state.
Use rollback/forward-fix policy.
Open incident if severity warrants.
Verify recovery.
```

## Duplicate Alert

Input:

``` text
Same unhealthy container emits 30 alerts.
```

Expected:

``` text
One correlated incident, not 30.
```

## Analytics Loss

Input:

``` text
Quest completion events missing for six hours.
```

Expected:

``` text
Mark data incomplete.
Repair instrumentation.
Do not report fabricated completion metrics.
Assess whether experiments/decisions were affected.
```

## Household Privacy

Input:

``` text
Image reference is exposed to unauthorized user.
```

Expected:

``` text
Contain immediately.
Treat as privacy/security incident.
Determine scope.
Preserve evidence.
Escalate appropriately.
```

## Agent Error

Input:

``` text
Agent uses superseded configuration and deploys wrong behavior.
```

Expected:

``` text
Contain.
Inspect context-routing and canonical-document controls.
Correct behavior.
Update prevention controls.
```

## Backup

Input:

``` text
Backup job says success but restore fails during test.
```

Expected:

``` text
Open/record recovery incident or material issue according to impact.
Do not claim backup protection is healthy.
```

------------------------------------------------------------------------

# 76. Postmortem Acceptance Tests

A good postmortem must answer:

``` text
What failed?
Who/what was affected?
How did we detect it?
Why did it happen?
Why did controls not prevent/detect it sooner?
How did we restore?
What evidence confirms recovery?
What should change?
What risk changed?
What did we learn?
```

------------------------------------------------------------------------

# 77. Incident Anti-Patterns

Do not:

-   hide failures to make autonomy metrics look better;
-   blame individuals instead of analyzing the system;
-   declare root cause too early;
-   repeatedly restart without diagnosis;
-   deploy multiple speculative fixes simultaneously;
-   destroy evidence;
-   fabricate missing timeline data;
-   close an incident because alerts stopped without verifying customer
    flow;
-   treat every defect as an incident;
-   treat every container restart as an outage;
-   ignore analytics incidents because the website still loads;
-   let agents independently fight the same incident;
-   create endless preventive tasks with no prioritization;
-   continue normal deployments during an uncontrolled critical
    incident;
-   expose secrets/customer data in incident documentation;
-   assume rollback is always safe;
-   claim recovery without verification.

------------------------------------------------------------------------

# 78. Incident Record Template

``` markdown
# INC-YYYY-NNN: [Title]

**Severity:**  
**Category:**  
**Status:**  
**Environment:**  
**Detected:**  
**Resolved:**  
**Incident Lead:**  

## Summary

## Customer Impact

## Business Impact

## Known Facts

## Hypotheses

## Timeline

## Containment

## Mitigation

## Recovery

## Recovery Verification

## Root Cause Status

## Root Cause

## Contributing Factors

## Related Change / Deployment

## Related Risks

## Corrective Actions

## Preventive Actions

## Learnings

## Owner Decisions

## Closure Evidence
```

------------------------------------------------------------------------

# 79. Incident Register Update Rule

Whenever a material incident is closed:

1.  update the incident record;
2.  update the register;
3.  update related risk;
4.  create/close corrective backlog items;
5.  record validated learning;
6.  update changelog if applicable;
7.  surface material result in Executive Brief.

------------------------------------------------------------------------

# 80. Near-Term Incident Priorities

The first operational work should verify:

1.  what is actually running on the Hostinger VPS;
2.  which Docker containers/services are production-critical;
3.  how production health is currently checked;
4.  where logs live;
5.  how deployments map to GitHub commits/releases;
6.  whether rollback is tested;
7.  whether backups are running;
8.  whether restores are tested;
9.  how secrets are stored;
10. whether core Entryway/customer flows can be synthetically verified;
11. whether analytics loss is detectable;
12. how owner escalation occurs.

------------------------------------------------------------------------

# 81. Current Strategic Incident Concern

The current product stage creates a special type of operational risk:

> **A failure of measurement can be as damaging as a failure of software
> because 6S Success is still learning what customers actually value.**

If Entryway completion, outcome, or sustain data is wrong, the business
can scale the wrong product even while production appears technically
healthy.

Therefore incident readiness must cover:

``` text
SYSTEM HEALTH
+
CUSTOMER FLOW HEALTH
+
DATA / MEASUREMENT HEALTH
```

------------------------------------------------------------------------

# 82. Final Principle

The purpose of incident management is not to produce incident reports.

It is to make 6S Success **resilient, observable, recoverable, and
continuously smarter after failure**.

The desired loop is:

``` text
FAILURE OR THREAT
      ↓
FAST TRUTH
      ↓
CONTROLLED RESPONSE
      ↓
SAFE RECOVERY
      ↓
VERIFIED CUSTOMER STATE
      ↓
ROOT-CAUSE UNDERSTANDING
      ↓
TARGETED PREVENTION
      ↓
UPDATED RISK
      ↓
VALIDATED LEARNING
      ↓
BETTER SYSTEM
```

An autonomous company must be able to fail safely.

**Claude should detect problems quickly, preserve owner control, restore
customer value, tell the truth about uncertainty, and make recurrence
less likely without turning every failure into bureaucracy.**

---

## INC-2026-08-31 Revenue outage: every buy button on the live site was dead for eight days

**Impact.** All six payment links the live site serves were deactivated in
Stripe. Anybody who clicked buy reached a dead checkout. The site had no working
way to take money for eight days. Measured revenue over the window: $0.

**Detection.** `ops/check_live_links.py` reported it correctly and repeatedly.
The failure was not detection. The report sat in preflight output as a warning
for eight days while other work continued around it. A warning nobody acts on is
indistinguishable from no warning.

**Why a status check could not see it.** A deactivated payment link still
answers HTTP 200 and serves a byte-identical JavaScript shell. The live and dead
pages differ only after the client fetches state. Verified directly during this
incident: a known dead link and a restored one returned the same 552,024 bytes.

**Root cause.** `ensure_link` in `ops/stripe_catalog.py`. A payment link's line
items are immutable in Stripe, so when the book price dropped from $18 to $9.99
the tool did the correct thing for the repository: retire the superseded link,
build a new one at the new price. But the live site is an older build and still
pointed at the old link, so retiring it took the live buy button down. Stripe
then compounded it, because archiving the old product force-deactivates every
payment link that uses it, which killed five more.

The code was right in isolation and wrong in context. It assumed the deployed
site matches the repository. Whenever a deploy lags, retiring a superseded link
is not cleanup, it is an outage.

**Restoration.** Verified before touching anything that all six sold current
products, that every underlying price was still active, and that for all six the
amount the live site advertises equals the amount the link charges, so nobody
would be charged a price they were not shown. Then reactivated the six links and
un-archived the one product that had been retired. Confirmed end to end in a
real browser: each checkout loads with the correct product name and the correct
total.

**Correction.** `ensure_link` now asks the live site before retiring anything
and refuses in two cases: the live site is still serving that link, or the live
site could not be read at all. The second matters more than the first, because
unknown is not unused. `ops/tests/test_link_retirement.py` holds all three
cases.

**Still open.** The live book page advertises $18 while the current build sells
the same book at $9.99. That is a stale price, not a wrong one, and it stops
being served the moment the site is deployed. The live catalogue is also 10
products against 159 in the repository.

**Lesson.** Two, and the second is the expensive one:

1. A tool that mutates production state must know what production is serving,
   not what the repository believes.
2. A correctly reported problem that nobody acts on costs exactly as much as an
   undetected one. Eight days of detection produced eight days of $0.

------------------------------------------------------------------------

## INC-2026-09-10 Image generation was dead for eleven days and reported as idle work, not a broken capability

**Impact.** No card hero or zone hero could be generated from 2026-08-30 to
2026-09-10. Not slow: every run produced nothing and every probe reported
healthy. Two standing warnings (`page-art`, 7 of 114 zone pages with no image;
`deck-art`, 12 of 88 card heroes on a placeholder) were carried in preflight
output every cycle for eleven days, described as work waiting to be picked up.
It was not: the capability the fix depends on had silently stopped working.

**Detection.** An operator went to regenerate one hero image with an unrelated
copy fix and found it would not generate. Ran the failure down rather than
retrying it.

**Root cause, three separate defects, each making a broken capability look
like an idle one.**

1. The pipeline loaded online even though the model is pinned and 4.0 GB of it
   is already cached locally. `from_pretrained` still called the hub first,
   and that call hung instead of failing: two runs sat at "Loading pipeline
   components 0%" for 25 minutes each before being killed. Forcing the cache
   reached 17 percent in under a second, measured both ways.
2. `--probe` printed torch, CUDA, model and cache state and exited 0 without
   ever loading the pipeline, so it reported healthy on a machine where
   generation dies at exit 139.
3. The generate loop caught `Exception`, which is worth nothing against a
   segfault. It swallowed the crash and moved on rather than reporting
   nothing was produced.

The actual constraint is system RAM, not VRAM: a load died with 6.96 GB of
VRAM free, before the GPU was ever touched. This machine has 15.8 GB of RAM
and roughly 2 GB free. That was misdiagnosed and published twice, in a commit
message and a GitHub issue, before it was measured; corrected in `6a10e6af`.

**Correction.** `ops/image_local.py` and `ops/generate_zone_heroes.py`: model
loading is local-first, network only on a genuine cache miss; `--probe` now
actually loads the pipeline; the generate loop probes in a subprocess so a
segfault is caught and reported as `NOTHING GENERATED` instead of silently
continuing.

**Still open.** Retry needs free RAM, which needs no decision and no spend,
but has not yet been confirmed available. Neither `page-art` nor `deck-art`
has closed: no image has actually been regenerated since this fix, only the
capability to attempt one was restored. `OWNER-ACTIONS.md` item 1b/C5
(Gemini billing) is the separate, unrelated path to the same missing art.

**Lesson.** A warning that names a blocked remedy has to say the remedy is
blocked. "7 pages have no image" read as backlog every cycle it was reported;
it was a capability outage the whole time, and nothing distinguished the two
readings until somebody tried to act on it.

------------------------------------------------------------------------

## INC-2026-09-09 Two scheduled GitHub Actions workflows ran 4 to 14x slower than configured, sustained 14+ days

**Impact.** `fulfil-orders.yml` names itself "every 30 minutes" in its own
cron comment; its real last 49 gaps averaged 213 minutes (worst 367), zero of
49 within 35 minutes of the configured interval. `hourly-brief.yml` names
itself "hourly"; its real last 49 gaps averaged roughly 4 hours (later
measured 235 minutes, worst 362, still 3.9x on 2026-09-11). Both patterns held
across the full 8-to-14+-day history the Actions API returned, not one bad
day. This is the delay between a paid order and its fulfilment email, and
between a real event (a dead payment link, a customer message) and the one
credentialed channel that could catch it.

**Detection.** A same-day entry had logged one instance of this as a
"GitHub-side incident." A later pass the same day pulled the real run history
directly from the Actions API instead of trusting either the cron comment or
the earlier entry, and found the pattern sustained across the platform's
entire returned history, this account's normal operation rather than an
outage.

**Root cause.** GitHub's own scheduler, not something a commit in this
repository causes. Checked directly rather than assumed: both workflows
already stagger their cron off the platform's busiest minutes, and every
`checks.yml` run inspected during the investigation started the instant it
was created, so nothing supported a fixable local cause such as this
repository's own CI volume contending for runners.

**Live consequence found and fixed.** `ops/roadmap_report.py`'s email to Phil
claimed a reply "reaches the operator within the hour," which the measured
data shows is false; reworded to state the operator's next automated cycle
picks it up, typically within a few hours, and to name GitHub's scheduler as
the cause rather than promise a clock this repository does not control.
`fulfil-orders.yml`'s own header comment, written against the literal
30-minute promise, corrected to cite the measured reality.

**Correction.** New `ops/check_cron_cadence.py` parses each workflow's real
cron line, pulls live run history via the Actions API, and flags any workflow
whose mean gap exceeds 2.5x its configured interval; wired into `preflight.py`
as `gate_scheduled_workflow_cadence`, WARN rather than FAIL since the cause is
outside this repository's control and no live page is wrong because of it.
Widened the same day from 2 of 5 scheduled workflows to all 5 after a real
parser bug (it mis-parsed a once-daily cron as 60 minutes, 24x wrong, and gave
up on a four-cron-line shape entirely) was found and fixed; the wider check
found `linkedin-drafts.yml` and `roadmap-report.yml` run almost exactly on
schedule and `status-email.yml` drifts 1.57x, real but under the 2.5x
degraded line, narrowing the finding to the two workflows GitHub is asked to
fire more than once an hour.

**Still open.** The cadence itself is unfixed and not fixable from this
repository; the standing WARN is the honest state, re-confirmed still
present, still within its own degraded-not-failing threshold, as of this
entry.

**Lesson.** A workflow's own cron comment is a claim, not a fact. Checking it
against the platform's real run history, rather than against the YAML that
states the intent, is what found this.

------------------------------------------------------------------------

## Incidents moved verbatim from STATUS.md section 16, 2026-11-06 PM check-in

STATUS.md's own "Current Incidents" section is meant to hold only what is live; these 5 (INCIDENT-001 through INCIDENT-005) were all already RESOLVED or STALL NOT RECURRING and had sat there since 2026-10-02 through 2026-10-30, 15.8KB read by every cycle as if current. Moved here unedited, per that section's own standing rule and this file's role as the canonical incident history.

## INCIDENT-001: fulfil-orders.yml fails every run, paid orders not delivered (RESOLVED)

- **Severity:** P0.
- **Start:** 2026-10-02, ~09:12 UTC. A live-write guard added in `044863b9c`
  did not account for this workflow, the one caller designed to run
  unattended against a live Stripe key.
- **Impact while open:** every scheduled and push-triggered run of
  `fulfil-orders.yml` failed at the "Deliver" step. Any customer who paid
  while this stood received nothing until the fix landed. Open roughly
  6h50m, 09:12 to 16:01:47 UTC.
- **Resolved 2026-10-02 16:01:47 UTC, by Phil directly**, commit `295b1c642`,
  adding `STRIPE_ALLOW_LIVE: "1"` to the Deliver step's `env:`, the exact
  fix five push notifications had already named. GitHub issue #37 closed
  the same moment, `state_reason: completed`.
- **Verified, not assumed, against the Actions API directly (this PM
  check-in, 16:4x cycle):** six consecutive `fulfil-orders.yml` runs since
  the fix (#3054 through #3059) all completed `success`, most recently at
  16:47:18 UTC.
- **Mitigation during the outage:** none available from inside a sandboxed
  session; no order was lost, Stripe kept recording them, delivery was only
  delayed.
- **Follow-up closed:** `OWNER-ACTIONS.md`'s item 0a (the owner-action this
  incident generated) was still telling Phil to make a fix he had already
  made; closed into that file's "Resolved today" table as R5, 2026-10-02
  16:2x PM check-in.

Historical account, superseded by the resolution above, kept for the
record: the one-line fix was written and reverted twice by two different
autonomous sessions, each time correctly held by this environment's own
safety classifier as a payment-safety change requiring a human
(`CLAUDE.md` 37/52). That was correct, conservative behavior, not a bug to
route around, which is why the fix waited for Phil rather than an agent
finding a way around the block.

## INCIDENT-002: autonomous PM/operator routines stalled 5 days on a usage limit, surfaced only by this cycle checking commit authorship against trigger state (STALL NOT RECURRING)

- **Severity:** P0 (process, not product: nothing customer-facing broke).
- **Start:** sometime shortly after 2026-10-04 11:19:40Z (the last Claude-authored commit, `c2565f114`).
- **End:** by 2026-10-09 03:2x UTC, the PM check-in that surfaced this incident (`:10` slot) itself ran without issue, meaning the stall had already lifted by the time it was found. **Re-verified this cycle (2026-10-09, PM check-in, `:10` slot, 09:11 UTC) via `list_triggers` directly:** the `:40` PM Routine's last run `SUCCEEDED` (08:40 to 08:47 UTC) and the `:43` hourly operator's last run `SUCCEEDED` (08:43 to 09:00 UTC), no `FAILED` on either since the stall ended, and `git log` shows continuous Claude-authored commits every cycle in between. Whether this was Phil acting, the limit resetting on its own, or the account moving past it cannot be told from here, and issue #40 stays open for that reason: the account-level cause was never confirmed, only that its symptom has not recurred for roughly 6 hours of continuous operation since.
- **Found:** 2026-10-09, PM check-in (:10 slot). `git log --since="2026-10-04T11:21:00Z"` returns 36 commits, every one authored by `github-actions` (the hourly check-in and social-draft-rotation bots, which run without an agent). Cross-checked against `list_triggers`: the :40 PM twin and the :43 hourly operator both show `last_run.status: FAILED`, `failure_reason: USAGE_LIMIT_REACHED`, fired `2026-10-09T02:40:34Z` and `2026-10-09T02:44:02Z`. This session's own :10 slot ran without issue.
- **Impact:** roughly 5 days with zero autonomous PM or operator work: no measurement, no backlog progress, no verification. `CHECKIN-LOG.md`'s hourly entries kept landing throughout, which made the repository look attended when it was not; that gap is itself worth remembering; a check that only reads the bot's own log cannot distinguish a live operation from a stalled one sitting next to a dumb heartbeat.
- **Not customer-facing:** `preflight.py` (run this cycle) shows 0 FAIL through every gate reachable in this sandbox (stalls at the documented `gate_tests` headless-Chromium sandbox hang, same as prior cycles, confirmed genuinely stalled by flat CPU time before killing it). The 8 open GitHub issues are unchanged, all `decision`/`blocked-on-art`, already waiting on Phil.
- **Cannot be fixed from here:** the usage limit is an account/plan-level setting outside this sandbox's visibility or control. Filed as **GitHub issue #40** (`decision`), with the evidence above and a recommendation to check the Claude Code usage/plan status, since three Routines firing every 30 to 60 minutes is real concurrent load.
- **Mitigation:** none available; the next PM or operator cycle that runs should check `list_triggers` for `last_run.status == FAILED` as a matter of course, rather than relying on a cold commit-authorship read to notice a stall, which is how this one was found.

## INCIDENT-003: checks.yml push trigger stopped firing for 3h09m / 24 commits, manual dispatch still works (RESOLVED: transient, self-recovered, no gate failure)

- **Severity:** P0 (process). `checks.yml` is the only workflow that runs `ops/preflight.py`, every quality gate, and the checks that watch revenue.
- **Found:** 2026-10-11, PM check-in (15:1x slot). Last push-triggered run was #2034 (commit `9eafaaa3`, completed 11:46:01Z). 24 commits landed after that, several touching paths the workflow's own `on.push.paths` includes and does not exclude (`CHECKIN-LOG.md`, `ops/corpus-rotation.json`, `ops/last-brief-sent.json`, `ops/state-checkin.json`), none triggered a run. The workflow file itself is unchanged (`git diff 9eafaaa38 HEAD -- .github/workflows/checks.yml` empty) and the API reports it `"state":"active"`.
- **Ruled out:** a repo-wide Actions outage or a disabled workflow. Every other scheduled workflow (`hourly-brief.yml`, `linkedin-drafts.yml`, `bluesky-drafts.yml`, `social-drafts.yml`, `fulfil-orders.yml`) ran normally on the same pushes, most recently on `ddc47e62e` at 14:55Z.
- **Confirmed still functional:** manually dispatched via `workflow_dispatch`, run #2035 (`.../actions/runs/38151102383`), queued and reached `in_progress` immediately. So this is the push trigger specifically, not the workflow or Actions generally.
- **Impact while open:** no CI coverage of `ops/**`, `build/**`, `content/**`, `.github/workflows/**` or root markdown for 3h09m+. `preflight.py` fast, run locally this cycle, showed 0 failures through every gate reachable before the documented `gate_tests` sandbox hang, so nothing is known to be broken; the gap is in verification, not a confirmed defect.
- **Filed:** GitHub issue #41, not labelled `decision` (no judgment call yet, just needs someone to watch whether it recurs). The next ordinary push (`cfaa7245e`) triggered run #2036 normally, 3 minutes after the manual dispatch (#2035). A third push (`d33d9fe48`) auto-triggered run #2037, no manual dispatch involved. A fourth push (`2a8a1308`) auto-triggered run #2038, also with no manual dispatch. Four consecutive pushes since the gap all triggered normally, with no further gaps.
- **RESOLVED, this operator cycle (15:5x), after watching all four runs to completion rather than citing the "looks recovered" read at 15:4x.** All four (`#2035` dispatch, `#2036`, `#2037`, `#2038` push-triggered) finished with `conclusion: success`, confirmed directly via `gh run view`, not inferred from `in_progress`. That means every gate `preflight.py --deep` runs, including the full `gate_tests` e2e suite this sandbox cannot reach, passed clean on real CI hardware across all four commits. Closing as transient: a GitHub-side delivery gap on the push event for this one workflow, self-resolved, no code or workflow-file change made or needed, no gate failure found. Re-open if the gap recurs; if it does, the next root-cause step is Settings -> Actions, usage/billing, named in issue #41's original report. GitHub issue #41 closed with this evidence. **Cross-confirmed independently, 16:1x PM check-in**, same four runs read directly, same conclusion reached before either session saw the other's commit.

## INCIDENT-004: checks.yml red and publish-image.yml blocked for ~2h on a stale sitemap lastmod, unseen because every cycle's local preflight hangs before reaching the gate that caught it (RESOLVED)

- **Severity:** P0 (process and deploy traceability). `publish-image.yml`'s failure meant real `site/`-touching content sat built but unpublished.
- **Start:** 2026-10-19T19:00:10Z, commit `0e50c3f27` (the 18:5x cellar/basement synonym fix). It hand-edited `site/articles/how-to-organize-a-basement.html` correctly per `CLAUDE.md` 5b (a hand-authored page, no generator owns it) but never re-ran `ops/build_seo.py`, so `site/sitemap.xml`'s `<lastmod>` for that one URL stayed at `2026-10-14` while the file itself changed.
- **Impact while open:** `gate_sitemap_lastmod_current` and its matching test correctly FAILED `checks.yml` on every push since (`759c43f85`, `a7498109b`, `7c630782e`); `gate_publish_image_current` correctly FAILED `publish-image.yml` the same way, so no `site/`-touching change landed on production from `3d84199d` (2026-10-15) onward. **Not customer-facing in a way this sandbox could confirm or rule out:** no egress to 6s-success.com from here, same standing wall every cycle records.
- **Found:** 2026-10-19, scheduled operator cycle, ~20:51Z, by reading the actual `checks.yml`/`publish-image.yml` job logs directly rather than citing the last several `ops/NIGHTLY-LOG.md` entries' own "preflight.py: 0 FAIL through every gate reached before the `gate_tests` sandbox hang" framing. Both failing gates are ordered after `gate_tests` in `preflight.py`'s call order; `gate_tests` hangs in every sandbox this project has run in, so no local run had ever reached either gate, and nobody had separately pulled the CI conclusion for roughly 2 hours across at least 4 cycles.
- **Resolved, same cycle, commit `0fb7273b1`:** ran the owning generator, `ops/build_seo.py` (not a hand edit), moving the stale `<lastmod>` to `2026-10-19`. Verified directly: `gate_sitemap_lastmod_current()` clean, `test_gate_sitemap_lastmod_current.py` 6/6, `check_urls.py` 213/213, `audit_pages.py` 0/0, `affiliate.py --check` 165 documents, `fix_dashes.py --check` 0/0. Watching `checks.yml`/`publish-image.yml` on this push to confirm green and the backlog of unpublished content clearing; not yet confirmed at the time this entry was written (CI still `in_progress`).
- **Gate added, same cycle, so this class cannot recur silently:** `gate_ci_conclusion_current`, called in `preflight.py` before `gate_tests` so the sandbox hang cannot hide it, hard-FAILs on a red `checks.yml` rather than the warn `gate_workflows_healthy` already gives (same escalation `gate_money_critical_workflows` makes for a broken delivery pipeline). `ops/tests/test_gate_ci_conclusion_current.py`, 5 cases, fail-then-pass proved against real live GitHub data, not only a mock.
- **Same shape as a prior incident, 2026-10-15** ("Fix the 9 CI gate failures the Photos API frontend shipped, unnoticed across 3 pushes"), whose own commit message named this exact gap and recommended relying on CI when `gate_tests` hangs. That was prose, not a gate, and it recurred 4 days later exactly as `CLAUDE.md` step 10b warns an un-gated lesson will.
- **Fully confirmed RESOLVED, same cycle, after the fix revealed a second, smaller instance of its own root cause.** The sitemap fix (`0fb7273b1`) itself changed `site/`'s content hash without re-running `ops/build_id.py`, so `site/build-id.txt` went stale and `publish-image.yml` correctly failed again on `6cbce91b2`/`e39e62320` at its "Refuse to publish a stale build id" guard, before preflight even ran. Fixed the same way, by running the owning generator (`6d2bc368d`). Watched that run to completion via the Actions API rather than inferring from `in_progress`: `publish-image.yml` on `6d2bc368d` finished `conclusion: success` at 2026-10-19T21:22:54Z, the first fully green run since `3d84199d` on 2026-10-15. Total window 19:00:10Z to 21:22:54Z, roughly 2h23m.

## INCIDENT-005: checks.yml red on main from A32's own commit, the identical `site/build-id.txt` shape INCIDENT-004 already named, this time with the fix commit itself silently unable to retrigger CI (RESOLVED)

- **Severity:** P0 (process). Same gate as INCIDENT-004's second half; `gate_ci_conclusion_current` did exactly the job it was built for.
- **Start:** 2026-10-30T19:06:05Z, commit `a498b97d5` (A32, the "dinnerware" zone synonym fix on the Kitchen Upper Cabinet Zone). It changed `content/content.json`/`site/zones/kitchen-the-upper-cabinets.html` correctly and re-ran `ops/build_zone_pages.py`, but never ran `ops/build_id.py`, so `site/build-id.txt` stayed at the pre-edit hash.
- **Found:** 2026-10-30, PM check-in (19:1x slot), by `preflight.py --fast` itself this time (not a cold CI-log read): `gate_ci_conclusion_current` printed `FAIL ci-conclusion-current` naming the exact run and commit before the gate_tests sandbox hang could hide anything downstream, which is precisely the escalation INCIDENT-004 built that gate to force.
- **Resolved, same cycle:** ran the owning generator, `ops/build_id.py`, in commit `6fc4a6c3c`. Verified directly before and after, not just cited: imported `ops/build_id.py` and compared `m.current()` to `m.compute()` by hand (both `eaf222a0b634a548`), rather than trusting a preflight run that cannot reach this gate locally (it is ordered after `gate_tests` in `preflight.py`'s own call order, same blind spot INCIDENT-004 documents).
- **A second, process-level defect found while confirming the fix, not yet closed by any gate:** `6fc4a6c3c` touched only `site/build-id.txt` plus the three dashboard-regen files `checks.yml`'s own `on.push.paths` excludes (`EXECUTIVE-DASHBOARD-LIVE.md`, `ops/dashboard.html`, `ops/state.json`) and `site/**` is not in that include list at all, so the fix commit matched no trigger path and never started a new `checks.yml` run. The red run (`41112411829`) would otherwise have sat as "most recent completed" indefinitely, with `gate_ci_conclusion_current` correctly reporting it FAIL forever even though the underlying defect was already fixed on `main`. This entry's own edit to `STATUS.md` (a root `*.md` file, which the trigger list does include) is what got a real CI run against the fixed tree. Watched run `41115163326` to completion via the Actions API rather than inferring from `in_progress`: `Preflight` step passed at 19:34:37Z (confirming `gate_build_id_current` and `gate_ci_conclusion_current` both clean), full job `conclusion: success` at 19:39:12Z on commit `87b7de377`, roughly 13m33s after the incident was found.
- **Not yet gated:** `site/**` changes that are not also a dashboard regen, nor a root markdown edit, nor anything else on the include list can land on `main` without ever running `checks.yml`. `gate_build_id_current` already catches a stale hash the next time any triggering path changes, but a `site/`-only fix (exactly this incident's own repair commit) could go unverified indefinitely if nothing else happens to touch a triggering path afterward. Worth a future cycle adding `site/**` to `checks.yml`'s own path list, or a narrower include for `site/build-id.txt` and `site/sitemap.xml` specifically; left for a cycle with room to make and test that change rather than widening a CI trigger inside a check-in slot.
