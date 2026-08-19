# INCIDENTS.md

## 6S Success Incident Management, History, and Learning Standard

**Document role:** Canonical incident source of truth for 6S Success\
**Status:** ACTIVE\
**Owner:** Founder / Owner\
**Operational steward:** Claude Code autonomous operating system\
**Primary responders:** DevOps/SRE, GitHub Manager, Hostinger VPS/Docker
Manager, Security, Data, Product, and other domain agents as routed\
**Last updated:** 2026-08-17\
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

Canonical table:

  ---------------------------------------------------------------------------------------------
  ID      Date    Severity   Category   Title   Impact   Root    Status   Related   Follow-Up
                                                         Cause            Risk      
  ------- ------- ---------- ---------- ------- -------- ------- -------- --------- -----------

  ---------------------------------------------------------------------------------------------

Do not fabricate historical incidents.

At initial creation, the register should remain empty until verified
incidents are imported from authoritative records.

------------------------------------------------------------------------

# 60. Initial Incident Register

``` text
NO VERIFIED HISTORICAL INCIDENTS HAVE BEEN IMPORTED INTO THIS CANONICAL FILE YET.
```

This does **not** mean no incidents have ever occurred.

It means the canonical incident history has not yet been reconstructed
and verified.

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
