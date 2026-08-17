# 6S Success Disaster Recovery and Business Continuity

> Canonical policy for catastrophic failure, recovery objectives, backups, restoration, infrastructure reconstruction, credential recovery, domain/DNS continuity, GitHub recovery, Docker recovery, data recovery, commerce continuity, autonomous-agent containment, and resilience testing for 6S-success.com.

## 1. Purpose

`DISASTER-RECOVERY.md` defines how 6S Success survives failures that exceed ordinary incident response.

`RUNBOOK.md` handles routine operations and incidents.

This file handles events such as:

- total Hostinger VPS loss
- unrecoverable Docker host
- corrupted database
- destructive deployment
- compromised server
- ransomware or malicious deletion
- lost GitHub access
- lost deployment credentials
- failed or unusable backups
- domain/DNS control loss
- commerce-provider outage
- major third-party dependency outage
- autonomous-agent malfunction
- loss of observability
- simultaneous infrastructure and data failure

The objective is:

**Restore the smallest safe, trustworthy, revenue-capable system as quickly as practical without making the disaster worse.**

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `TESTING.md`
- `OBSERVABILITY.md`
- `RELEASES.md`
- `DATA-SOURCES.md`
- `DATA-CONTRACTS.md`
- `STATUS.md`
- `DECISIONS.md`
- `LEARNINGS.md`

---

# 2. Disaster Recovery Principles

## Protect People and Customers First

Prevent further customer harm, privacy exposure, unauthorized charges, or data destruction.

## Preserve Evidence

Do not destroy useful evidence during suspected compromise.

## Restore Service Deliberately

A fast restoration into a still-compromised environment is not recovery.

## Recover From Known-Good State

Prefer verified source, verified backup, and verified configuration.

## Minimize Dependencies

Restore the smallest viable system first.

## Verify Before Traffic

Do not direct customers to a reconstructed system until critical verification passes.

## Learn and Improve

Every material disaster or recovery drill should improve the recovery system.

---

# 3. Disaster vs Incident

An incident becomes a disaster-recovery event when ordinary repair/rollback is insufficient or unsafe.

Examples:

### Incident

One application container crashes and restarts.

### Disaster

The entire VPS filesystem is lost.

### Incident

A deployment causes a frontend regression.

### Disaster

A destructive migration corrupts production data and rollback cannot restore it.

---

# 4. Disaster Declaration

Suggested states:

- `NORMAL`
- `INCIDENT`
- `DR_DECLARED`
- `RECOVERING`
- `VERIFYING`
- `RESTORED`
- `POST_RECOVERY`

A material DR event should have one coordinator.

Default coordination role:

`devops-sre`

---

# 5. Recovery Priorities

Restore in this general order:

1. security and control
2. owner/administrator access
3. domain/DNS control
4. source/configuration access
5. persistent data
6. application infrastructure
7. public website
8. critical customer journeys
9. commerce
10. analytics/observability
11. autonomous improvement systems
12. noncritical features

Actual order depends on failure.

---

# 6. Minimum Viable Business

Define the smallest system that can safely provide value.

Potential minimum:

- 6S-success.com resolves
- HTTPS works
- core marketing/content pages load
- Entryway content is available
- products can be viewed
- checkout works or is clearly disabled
- customer data remains protected
- owner can administer system
- observability is sufficient to verify health

Advanced autonomous features can return later.

---

# 7. Recovery Objectives

Two core concepts:

## RPO: Recovery Point Objective

Maximum acceptable data-loss window.

## RTO: Recovery Time Objective

Target time to restore an acceptable service state.

Do not invent aggressive objectives unsupported by actual architecture.

---

# 8. Initial Recovery Objective Framework

Until measured and approved:

```yaml
public_content:
  rpo: source-controlled / reconstructable
  rto: TBD

application_code:
  rpo: source-controlled / latest verified commit
  rto: TBD

customer_account_data:
  rpo: TBD
  rto: TBD

orders_entitlements:
  rpo: TBD
  rto: TBD

household_private_data:
  rpo: TBD
  rto: TBD

analytics:
  rpo: provider-dependent
  rto: lower priority than customer operations
```

Replace TBD only after architecture and business impact are understood.

---

# 9. Recovery Tiers

## Tier 0: Control Plane

Domain, credentials, GitHub, provider access.

## Tier 1: Revenue/Critical

Website, customer data, checkout, entitlements.

## Tier 2: Core Product

Quests, desired functions, micro-zones, standards.

## Tier 3: Intelligence

Analytics, experiments, dashboards.

## Tier 4: Optimization

Autonomous publishing, advanced AI, noncritical automation.

Recover by tier rather than attempting everything simultaneously.

---

# 10. Recovery Dependency Map

Claude should build a verified dependency map:

```text
Domain/DNS
   ↓
Reverse Proxy/TLS
   ↓
Application
   ↓
Database / Storage
   ↓
Commerce / Email / External APIs
   ↓
Analytics / Observability
```

Actual architecture may differ.

---

# 11. Critical Asset Inventory

At minimum identify:

- domain registrar
- DNS provider
- GitHub repository
- GitHub organization/account
- Hostinger VPS
- Docker/Compose configuration
- image registry if used
- database
- persistent volumes
- object/file storage
- backups
- commerce provider
- email provider
- analytics provider
- secrets/credential store
- monitoring provider

---

# 12. Recovery Source of Truth

For each asset define authoritative recovery source.

Example:

| Asset | Recovery Source |
|---|---|
| Application code | GitHub |
| Docker configuration | GitHub |
| Production image | Registry/build pipeline |
| Database | Verified backup |
| Product catalog | Commerce provider or canonical DB |
| Content | Git/content system |
| DNS | Provider + documented records |
| Secrets | Secure credential mechanism |

Do not rely on memory.

---

# 13. Backup Is Not Recovery

A backup is useful only if:

1. it exists
2. it is accessible
3. it is intact
4. it contains required data
5. credentials to decrypt/read it exist
6. it can be restored
7. restored data is usable

---

# 14. Backup Evidence Levels

## Level 0

Backup assumed.

## Level 1

Scheduled backup exists.

## Level 2

Backup reports success.

## Level 3

Artifact verified.

## Level 4

Representative restore succeeds.

## Level 5

Full recovery drill succeeds.

Critical systems should mature toward Level 4-5.

---

# 15. Backup Separation

Where practical, backups should not all be writable/deletable by the same credential that controls production.

This reduces correlated failure from:

- compromised host
- ransomware
- agent error
- destructive script

---

# 16. Backup Encryption

Sensitive backups should use appropriate encryption.

Recovery procedures must preserve access to decryption keys without storing them in this repository.

---

# 17. Backup Retention

Retention should support recovery from:

- recent operational mistake
- delayed corruption discovery
- security compromise

Do not retain sensitive data indefinitely without reason.

---

# 18. Backup Inventory

Populate:

```yaml
database:
  method: UNKNOWN
  frequency: UNKNOWN
  retention: UNKNOWN
  location: UNKNOWN
  encryption: UNKNOWN
  last_verified: UNKNOWN
  last_restore_test: UNKNOWN

uploads:
  method: UNKNOWN
  frequency: UNKNOWN
  retention: UNKNOWN
  last_restore_test: UNKNOWN

configuration:
  recovery_source: UNKNOWN

docker_images:
  recovery_source: UNKNOWN
```

---

# 19. Total VPS Loss Scenario

Trigger:

Hostinger VPS is permanently unavailable or must be replaced.

Recovery sequence:

1. declare DR if warranted
2. secure provider account
3. identify last known-good release
4. identify verified backup
5. provision replacement host
6. apply OS/security baseline
7. restore Docker/runtime prerequisites
8. restore configuration
9. restore secrets securely
10. restore persistent data
11. deploy known-good artifact
12. configure reverse proxy/TLS
13. verify internally
14. run smoke tests
15. verify commerce
16. verify analytics/observability
17. redirect/confirm DNS if required
18. monitor
19. close recovery only after evidence

---

# 20. VPS Reconstruction Principle

The long-term goal is to make the VPS disposable.

A new host should be reconstructable from:

- source-controlled configuration
- documented provider settings
- secure secrets
- verified backups
- known-good application artifact

Manual undocumented server configuration is a DR risk.

---

# 21. Corrupted Database Scenario

Signs:

- invalid data
- failed integrity checks
- application errors
- destructive migration
- missing records

Procedure:

1. stop writes if continued writes increase damage
2. preserve evidence
3. identify corruption window
4. identify last known-good backup
5. determine RPO impact
6. restore to isolated environment first where practical
7. validate restored data
8. reconcile recoverable transactions after backup point
9. switch production only after verification
10. document lost/recovered data

Do not overwrite the only copy of corrupted data before investigation.

---

# 22. Point-in-Time Recovery

If database/provider supports point-in-time recovery, document:

- retention window
- granularity
- restore procedure
- credentials
- tested recovery time

Current state:

`UNKNOWN`

---

# 23. Destructive Migration Scenario

If a migration damages production:

1. halt further migration
2. identify release and migration
3. determine whether application rollback is compatible
4. determine whether data restore is required
5. preserve affected database
6. restore/repair using verified procedure
7. validate critical data
8. deploy compatible application
9. verify business flows
10. create permanent migration regression controls

---

# 24. Compromised VPS Scenario

If compromise is credible:

1. contain access
2. preserve evidence
3. rotate exposed credentials where authorized
4. do not trust host state
5. identify known-good source and backups
6. provision clean replacement environment
7. patch root cause
8. restore clean data carefully
9. deploy verified artifact
10. verify no persistence remains
11. redirect traffic
12. monitor closely

Rebuilding clean is often safer than "cleaning" an unknown compromised host.

---

# 25. GitHub Access Loss

If repository access is lost:

1. determine account vs repository issue
2. use legitimate account recovery
3. preserve any verified local clone
4. avoid destructive force pushes
5. restore organization/repository access
6. verify branch protections and secrets
7. verify CI/CD integrity
8. compare production to recovered source

---

# 26. GitHub Repository Loss

Recovery sources may include:

- local clones
- CI workspaces/artifacts
- backups
- deployed source where architecture includes it

A local clone is not a substitute for a planned repository backup strategy.

After restoration:

- verify full history where possible
- verify tags
- verify workflows
- verify protections
- rotate compromised credentials if needed

---

# 27. Registry Failure

If Docker registry is unavailable:

- determine whether known-good images remain on host
- preserve them
- identify alternate build path
- rebuild from verified commit if necessary
- verify dependency availability

Do not delete local known-good images during outage.

---

# 28. Docker Host Corruption

If Docker state is corrupted:

1. preserve persistent data
2. inventory volumes
3. preserve Compose/config
4. rebuild runtime
5. restore volumes/data
6. deploy known-good images
7. verify networks
8. verify proxy
9. smoke test

Never assume containers contain no unique data until mounts are verified.

---

# 29. Lost Secrets Scenario

If a credential is lost but not compromised:

1. identify system owner/provider
2. use legitimate recovery/rotation
3. identify consumers
4. install replacement
5. verify
6. revoke old credential if appropriate
7. update secure recovery documentation

Never store the replacement secret in Markdown.

---

# 30. Credential Compromise Scenario

If a credential may be compromised:

1. identify privilege scope
2. contain
3. rotate/revoke
4. inspect usage logs
5. identify lateral access
6. verify dependent systems
7. create incident record
8. strengthen controls

Follow `SECURITY.md`.

---

# 31. Domain Registrar Loss

The domain is a Tier 0 asset.

Maintain recovery knowledge for:

- registrar
- account recovery
- renewal
- MFA
- recovery email
- transfer protection where available

Do not store recovery secrets here.

---

# 32. DNS Loss or Misconfiguration

Before changing DNS during recovery:

- capture known-good records if available
- identify mail records
- identify verification records
- identify subdomains
- understand TTL

Restore only verified records.

Avoid destroying email/service configuration while restoring web traffic.

---

# 33. TLS Failure

Recovery may require:

- restoring proxy configuration
- reissuing certificate
- validating DNS
- restoring automated renewal

Do not bypass TLS long term simply to get site online.

---

# 34. Commerce Provider Outage

If checkout provider fails:

1. verify provider outage
2. avoid duplicate order creation
3. preserve cart/customer intent where possible
4. display accurate customer messaging
5. do not claim payment succeeded
6. monitor provider recovery
7. reconcile pending events afterward

Do not build an improvised payment processor during an outage.

---

# 35. Commerce Data Reconciliation

After outage/recovery, reconcile:

- orders
- successful payments
- failed payments
- refunds
- entitlements
- webhook events

Provider transaction state remains authoritative where defined in `DATA-SOURCES.md`.

---

# 36. Analytics Provider Outage

Analytics outage is generally lower priority than serving customers.

During outage:

- preserve application operation
- buffer events only if architecture safely supports it
- avoid unbounded queues
- mark dashboard data stale
- do not infer zero activity

---

# 37. Email Provider Outage

Determine impact:

- login/reset
- receipts
- notifications
- marketing

Critical transactional email may require a documented fallback at sufficient business scale.

Do not add a new provider impulsively during minor outage.

---

# 38. AI Provider Outage

AI features should fail gracefully where possible.

Fallback options:

- disable AI-only feature
- use deterministic recommendations
- show existing content
- queue noncritical work

Core website and purchased content should not become unavailable merely because an AI provider is down unless architecture genuinely requires it.

---

# 39. Autonomous-Agent Malfunction

Examples:

- repeated bad deployments
- uncontrolled content publishing
- excessive API spending
- destructive repository changes
- unexpected infrastructure mutation

Response:

1. activate kill switch/read-only mode
2. stop autonomous writes
3. preserve logs/audit trail
4. identify affected systems
5. rollback unsafe changes
6. rotate agent credentials if necessary
7. verify production
8. diagnose root cause
9. strengthen permissions/tests
10. re-enable gradually

---

# 40. Agent Kill Switch

A verified mechanism should exist to stop autonomous writes while retaining owner access and observability.

Potential implementations:

- revoke agent token
- disable deployment workflow
- disable scheduler
- change agent role to read-only

Actual mechanism:

`UNKNOWN`

---

# 41. Agent Credential Recovery

Agent credentials should be independently revocable.

Avoid one credential that simultaneously controls:

- GitHub
- VPS root
- domain
- commerce
- analytics

Separation limits blast radius.

---

# 42. Observability Loss

If dashboards/monitoring fail:

1. do not assume production failed
2. use direct health evidence
3. mark telemetry state `UNKNOWN`
4. restore minimum monitoring
5. avoid autonomous optimization based on stale data

---

# 43. Multiple Simultaneous Failures

Prioritize:

**Control → Security → Data → Revenue → Experience → Optimization**

Avoid trying to restore every integration simultaneously.

---

# 44. Regional/Provider Outage

If Hostinger has a prolonged provider-level outage, options depend on:

- backup portability
- DNS control
- infrastructure reproducibility
- RTO
- cost

A secondary provider may become justified only after business scale and recovery objectives warrant it.

---

# 45. Static Emergency Site

Consider maintaining a minimal static fallback artifact containing:

- brand
- basic explanation
- contact/support path
- essential product/customer guidance

Do not automatically redirect to stale or misleading commerce.

Whether this is needed should be decided based on business maturity.

---

# 46. Recovery Environment

Where practical, restore into an isolated environment first.

Verify:

- data
- application
- migrations
- secrets
- customer flows

before directing production traffic.

---

# 47. Recovery Verification

Before declaring restored:

## Infrastructure

- host stable
- containers healthy
- disk/memory acceptable

## Application

- critical pages load
- APIs work
- authentication works if applicable

## Data

- database integrity acceptable
- required customer records available

## Commerce

- checkout/payment state verified

## Security

- compromised credentials rotated
- root cause contained

## Observability

- monitoring restored

---

# 48. Recovery Smoke Test

At minimum:

1. homepage
2. Entryway page
3. critical desired-function/quest path
4. product page
5. checkout entry if available
6. authentication if applicable
7. analytics/telemetry
8. administrative access

Only applicable features.

---

# 49. Data Reconciliation After Recovery

If RPO causes a data gap:

- identify missing period
- identify authoritative external sources
- recover transactions where possible
- reconcile entitlements
- avoid silently inventing data
- document unrecoverable loss

---

# 50. Customer Communication

If customer communication is necessary, communicate:

- what functionality is affected
- what customers should do
- whether data/payment is affected when verified
- restoration state

Do not speculate.

Do not disclose sensitive attack details.

---

# 51. Owner DR Update

Format:

## Situation

What failed.

## Customer Impact

What users experience.

## Data/Security Impact

Verified status.

## Recovery State

Current phase.

## Best Estimate

Only if evidence supports it.

## Decision Needed

Exact owner decision, if any.

---

# 52. Recovery Log

Maintain:

```yaml
dr_event_id:
declared_at:
coordinator:
trigger:
affected_assets: []
last_known_good_release:
backup_selected:
recovery_actions: []
service_restored_at:
data_reconciled_at:
closed_at:
```

Do not include secret values.

---

# 53. Recovery Testing

Do not wait for catastrophe.

Test recovery deliberately.

Types:

## Tabletop

Walk through scenario.

## Component Restore

Restore one backup.

## Environment Reconstruction

Build a new nonproduction host.

## Full DR Drill

Reconstruct critical service and validate.

---

# 54. Quarterly DR Review

At sufficient business maturity, review quarterly:

- asset inventory
- recovery contacts
- access
- backups
- restore tests
- RPO/RTO
- domain recovery
- GitHub recovery
- VPS reconstruction
- agent kill switch

Frequency may be adjusted based on scale.

---

# 55. Restore Test Schedule

Suggested maturity target:

- database representative restore: monthly/quarterly based on risk
- full environment reconstruction: quarterly/semiannual
- tabletop: quarterly
- credential recovery review: quarterly

Do not impose unnecessary operational burden before data/business value warrants it.

---

# 56. Recovery Time Measurement

Measure actual:

- detection time
- declaration time
- access recovery
- infrastructure provision
- data restore
- application deploy
- verification
- full business restoration

Use actual measurements to set realistic RTO.

---

# 57. Recovery Point Measurement

Determine actual recoverable point from:

- backup timestamps
- transaction provider
- event logs
- database recovery mechanisms

Do not claim an RPO the architecture cannot achieve.

---

# 58. DR Dashboard

Executive panel may show:

```yaml
dr_readiness: HEALTHY|ATTENTION|HIGH_RISK|UNKNOWN
last_database_backup:
last_verified_backup:
last_restore_test:
last_environment_rebuild_test:
known_good_release:
rollback_available:
domain_recovery_documented:
agent_kill_switch_verified:
critical_recovery_gaps:
```

---

# 59. Recovery Readiness Levels

## UNKNOWN

Critical recovery facts are not known.

## HIGH_RISK

Major asset lacks verified recovery.

## ATTENTION

Recovery exists but important gaps remain.

## HEALTHY

Critical recovery procedures have recent evidence.

Do not label healthy solely because backups are scheduled.

---

# 60. DR Backlog

Recovery gaps should be explicit backlog items.

Examples:

- database restore never tested
- no known-good image retained
- DNS records undocumented
- agent kill switch untested
- VPS cannot be reproduced
- secrets recovery unclear

Prioritize by business impact × likelihood × recovery difficulty.

---

# 61. DR and Releases

Every high-risk release should consider:

- last known-good release
- database compatibility
- backup evidence
- rollback
- forward recovery

Follow `RELEASES.md`.

---

# 62. DR and Security

A security disaster may require clean reconstruction rather than rollback.

Follow `SECURITY.md`.

Do not restore known-vulnerable configuration without remediation.

---

# 63. DR and Testing

Recovery procedures should be executable and tested.

Follow `TESTING.md`.

A documented procedure that has never worked is a hypothesis.

---

# 64. DR and Observability

Recovery is not complete until enough observability is restored to know the system is healthy.

Follow `OBSERVABILITY.md`.

---

# 65. DR and Data Contracts

Recovered data must preserve canonical identifiers and referential integrity.

Validate:

- room IDs
- micro-zone IDs
- quest/card IDs
- product IDs
- orders
- entitlements

as relevant.

---

# 66. Infrastructure Portability

Avoid unnecessary coupling to one VPS where practical.

Portability improves DR.

But do not create expensive multi-cloud complexity before justified.

---

# 67. Recovery Automation

Automate repeatable recovery steps only after manual procedure is understood and tested.

Automation should:

- be idempotent where possible
- verify targets
- stop on unsafe ambiguity
- preserve logs
- require approval for destructive actions

---

# 68. Infrastructure Bootstrap

Long-term target:

A clean VPS can be transformed into a working host through a documented, version-controlled bootstrap process plus secure secrets and restored data.

Current state:

`UNKNOWN`

---

# 69. Configuration Backup

Critical non-secret configuration should live in source control where appropriate.

Examples:

- Compose
- reverse proxy config
- application config templates
- deployment scripts

Secrets remain external.

---

# 70. External Account Recovery

Document, without secret values:

- provider
- account owner
- recovery method
- MFA status
- recovery dependency

Critical accounts include:

- domain
- GitHub
- Hostinger
- commerce
- email

---

# 71. Single Points of Failure

Claude should continuously identify SPOFs.

Examples:

- one unbacked database
- one owner credential
- one undocumented VPS
- one mutable Docker image
- one inaccessible DNS account
- one agent token controlling everything

Create backlog based on risk.

---

# 72. Recovery Cost

DR architecture has cost.

Optimize against:

**Expected Business Loss + Recovery Risk + Security Risk**

not against maximum redundancy.

---

# 73. Business Continuity

Some disasters may not require immediate technical restoration if customer value can continue through alternative means.

Examples:

- static content remains available
- purchased downloads delivered through commerce provider
- support email remains operational

Document real fallback paths once systems exist.

---

# 74. Commerce Continuity

At higher revenue scale, document:

- order recovery
- entitlement recovery
- refund handling
- customer communication
- pending checkout reconciliation

A $20K+/month business should not depend on undocumented payment recovery.

---

# 75. Content Continuity

Public educational content should be reconstructable from canonical source.

Avoid having irreplaceable content exist only inside a running container.

---

# 76. Product Asset Continuity

Digital products, card decks, images, PDFs, downloads, and other sellable assets need recoverable canonical storage.

Inventory:

```yaml
asset_type:
canonical_location:
backup:
versioning:
restore_test:
```

---

# 77. Intellectual Property Recovery

Critical original assets should not exist in only one place.

This includes:

- room decks
- card lists
- illustrations
- product files
- source content
- code
- design assets

Use appropriate versioning/backup based on file type and value.

---

# 78. Autonomous Business State Recovery

Claude's operational knowledge should be reconstructable from:

- governing Markdown
- Git history
- backlog
- decisions
- learnings
- metrics definitions
- data contracts
- release records

Do not make essential business logic dependent solely on conversational memory.

---

# 79. Executive Dashboard Recovery

Dashboard is important but not Tier 1.

If dashboard fails:

- restore customer/revenue systems first
- use direct source checks
- mark dashboard unavailable/stale
- restore dashboard after critical service

---

# 80. Disaster Learning

After every DR event or meaningful drill:

1. identify what worked
2. identify what failed
3. measure actual recovery
4. update procedures
5. update backlog
6. update decisions
7. update learnings
8. improve automation

---

# 81. Post-Disaster Review

Include:

## Trigger

What initiated disaster.

## Impact

Customer/business/data impact.

## Timeline

Verified events.

## Recovery

What restored service.

## Data Loss

Actual, if any.

## Security

Actual impact.

## Gaps

What slowed recovery.

## Improvements

Specific actions.

No blame.

---

# 82. Current DR State

Populate only from verified evidence:

```yaml
production:
  domain: 6S-success.com
  current_known_good_release: UNKNOWN

hostinger:
  vps_rebuild_procedure: UNKNOWN
  provider_recovery_access: UNKNOWN

github:
  repository_recovery: UNKNOWN
  local_or_secondary_backup: UNKNOWN

database:
  engine: UNKNOWN
  backup_method: UNKNOWN
  backup_frequency: UNKNOWN
  point_in_time_recovery: UNKNOWN
  last_verified_backup: UNKNOWN
  last_restore_test: UNKNOWN

persistent_files:
  canonical_location: UNKNOWN
  backup_method: UNKNOWN
  last_restore_test: UNKNOWN

docker:
  image_registry: UNKNOWN
  known_good_image_retention: UNKNOWN
  compose_recovery: UNKNOWN

domain:
  registrar: UNKNOWN
  dns_provider: UNKNOWN
  recovery_method_documented: UNKNOWN

commerce:
  provider: UNKNOWN
  reconciliation_procedure: UNKNOWN

secrets:
  recovery_mechanism: UNKNOWN

agents:
  kill_switch: UNKNOWN
  credential_revocation: UNKNOWN

rpo:
  customer_data: UNKNOWN
  commerce: UNKNOWN
  content: UNKNOWN

rto:
  minimum_viable_business: UNKNOWN
  full_service: UNKNOWN

dr_testing:
  last_tabletop: UNKNOWN
  last_component_restore: UNKNOWN
  last_full_rebuild: UNKNOWN
```

---

# 83. First Disaster-Recovery Mission

Once legitimate access exists:

1. inventory critical assets
2. identify source of truth for each
3. map recovery dependencies
4. inspect backup mechanisms
5. verify latest backup artifacts
6. identify last known-good release
7. identify Docker/image recovery path
8. identify GitHub recovery path
9. identify domain/DNS recovery
10. identify credential recovery
11. identify agent kill switch
12. perform a safe representative restore test
13. estimate actual RPO/RTO capability
14. update Current DR State
15. create prioritized DR backlog

Do not perform destructive production tests.

---

# 84. Minimum DR Readiness Before High Autonomy

Before Claude receives broad autonomous production authority, the system should ideally have:

- known source repository
- known production release
- recoverable code/config
- verified critical backup
- tested representative restore
- known persistent-data locations
- owner access recovery
- agent kill switch
- known rollback target
- documented domain/DNS ownership
- basic production observability

---

# 85. DR Maturity Model

## Level 0: Hope

Recovery is assumed.

## Level 1: Documented

Critical assets and procedures are known.

## Level 2: Backed Up

Critical data has verified backup artifacts.

## Level 3: Restorable

Representative restores work.

## Level 4: Reconstructable

A clean environment can be rebuilt and verified.

## Level 5: Continuously Resilient

Recovery is regularly tested, measured, automated safely, and improved from evidence.

---

# 86. Definition of Recovery Done

A DR event is not done because the homepage loads.

Recovery is complete when applicable:

- control restored
- security contained
- critical data restored/reconciled
- known-good application running
- critical journeys work
- commerce reconciled
- observability restored
- backup protection re-established
- autonomous agents safely re-enabled
- owner informed
- post-recovery actions captured

---

# 87. Non-Negotiable DR Rules

Claude and subagents must never:

- destroy the only known copy of data
- assume a backup works without evidence
- restore traffic to a known-compromised environment
- overwrite corrupted evidence before preservation
- rebuild a VPS before persistent-data implications are understood
- delete known-good Docker images during an outage
- fabricate RPO/RTO
- claim recovery complete before verification
- store recovery secrets in this file
- let autonomous agents resume writes before their failure mode is understood
- prioritize dashboard restoration over customer/data/security recovery

---

# 88. Final Principle

The real test of autonomous infrastructure is not whether Claude can deploy when everything works.

It is whether the business remains controllable when several things fail at once.

6S Success should evolve toward a state where:

**GitHub can reconstruct the application.**

**Backups can reconstruct the data.**

**Secure credentials can reconstruct access.**

**Infrastructure definitions can reconstruct the VPS runtime.**

**Release records identify the last known-good system.**

**Observability proves the recovered system works.**

**The owner can stop autonomous actions at any time.**

The long-term objective is simple:

> **No single VPS, container, deployment, credential, agent, or mistake should be capable of permanently destroying the 6S Success business.**

That is the purpose of `DISASTER-RECOVERY.md`.
