# 6S Success Autonomous Operations Runbook

> Safe operating procedures for Claude Code and specialist agents managing GitHub, CI/CD, Hostinger VPS, Docker, production deployments, verification, incidents, backups, recovery, and rollback.

## 1. Purpose

`RUNBOOK.md` defines **how the autonomous system operates production safely**.

It is not a substitute for discovering the actual environment. Commands, paths, services, repositories, containers, domains, ports, credentials, databases, and deployment mechanisms must be verified before use.

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `DATA-SOURCES.md`
- `DATA-CONTRACTS.md`
- `DASHBOARD.md`
- `BACKLOG.md`
- `EXPERIMENTS.md`
- `DECISIONS.md`
- `LEARNINGS.md`
- specialist agent files for GitHub, DevOps/SRE, and VPS/Docker

---

# 2. Prime Directive

**Protect customer value, customer data, production availability, recoverability, and business continuity before optimizing speed.**

Preferred operating sequence:

**Observe → Understand → Plan → Change → Verify → Measure → Document**

Never:

**Guess → Change → Hope**

---

# 3. Production Safety Rules

Before any material production change:

1. identify the target
2. identify the current state
3. understand dependencies
4. determine autonomy class
5. determine rollback
6. verify persistent-data implications
7. verify secrets are not exposed
8. make the smallest safe change
9. verify technical health
10. verify customer-facing behavior
11. record release identity
12. monitor
13. update status/learning if material

---

# 4. Unknown Means Stop and Discover

If any of the following are unknown, do not invent them:

- repository
- branch
- VPS host
- SSH user
- project directory
- Compose file
- container name
- reverse proxy
- database location
- persistent volume
- backup location
- deployment mechanism
- DNS provider
- certificate mechanism
- secrets location

Use read-only discovery first.

---

# 5. Authority

All actions follow `AUTONOMY.md`.

## GREEN

Low-risk, reversible, routine operations may proceed autonomously.

## YELLOW

Proceed only within explicit constraints and with rollback.

## RED

Require owner approval.

Examples likely RED:

- destructive production-data operations
- domain transfer
- deleting unknown volumes
- disabling backups
- rotating credentials with uncertain consumers
- large infrastructure/vendor changes
- irreversible database migration
- material recurring spend

---

# 6. Environment Classification

Every target should be identified as:

- `production`
- `staging`
- `development`
- `test`
- `unknown`

If `unknown`, treat it as production until verified otherwise.

---

# 7. Initial Discovery Mode

The first interaction with an unknown Hostinger VPS/Docker environment is **read-only**.

Discover:

- OS/distribution
- uptime
- CPU/memory/disk
- listening ports
- Docker version
- Compose version
- running/stopped containers
- images
- networks
- volumes
- Compose projects
- mounts
- restart policies
- health checks
- reverse proxy
- TLS/certificate handling
- application directory
- repository linkage
- deployment scripts
- logs
- database/storage
- backups
- scheduled jobs
- firewall state

Do not prune, restart, recreate, pull, build, or delete during discovery unless explicitly required to restore an active incident and authority permits.

---

# 8. Read-Only Discovery Commands

Examples only. Adapt to actual permissions and platform.

```bash
uname -a
cat /etc/os-release
uptime
df -h
free -h
docker version
docker compose version
docker ps
docker ps -a
docker image ls
docker network ls
docker volume ls
```

Potential project discovery:

```bash
docker compose ls
ps aux
ss -lntup
```

Inspect specific objects only after identifying them:

```bash
docker inspect <container>
docker volume inspect <volume>
docker network inspect <network>
```

Never paste secret-bearing output into public logs or documentation.

---

# 9. Repository Discovery

Establish:

- repository URL
- default branch
- production branch if different
- remotes
- current commit
- working tree state
- CI workflows
- deployment workflows
- protected branches
- release/tag conventions
- dependency automation
- secret references
- environment configuration strategy

Useful read-only Git checks:

```bash
git status
git remote -v
git branch --show-current
git rev-parse HEAD
git log -n 10 --oneline
```

Do not assume the VPS checkout is the production source of truth.

---

# 10. Production Lineage

The target state is traceability:

**Git Commit**
→ **CI Build**
→ **Image**
→ **Image Digest**
→ **Deployment**
→ **Running Container**
→ **Customer Response**

Record where practical:

```yaml
release_id: string
commit_sha: string
image_repository: string
image_tag: string
image_digest: string
deployed_at: datetime
environment: production
deployed_by: string
```

Mutable tag alone is insufficient evidence.

---

# 11. Pre-Deployment Checklist

Before material deployment:

- [ ] intended change is understood
- [ ] tests pass
- [ ] build succeeds
- [ ] security checks acceptable
- [ ] migration implications understood
- [ ] rollback defined
- [ ] backup state acceptable if data risk exists
- [ ] production configuration validated
- [ ] secrets remain external
- [ ] release identity known
- [ ] health-check method known
- [ ] customer smoke test defined
- [ ] authority confirmed

---

# 12. Deployment Strategy

Prefer the safest deployment mechanism already established by the project.

Do not create a second deployment path casually.

Preferred principles:

- CI-driven
- reproducible
- immutable release identity
- minimal manual server mutation
- explicit configuration
- secrets outside Git
- health checks
- rollback capability

---

# 13. Never Deploy From an Unclean Working Tree Without Understanding It

If the VPS or build workspace has uncommitted changes:

1. inspect them
2. determine origin
3. determine whether production depends on them
4. preserve them
5. reconcile with Git

Never run a destructive reset merely to make Git look clean.

---

# 14. Docker Image Rules

Prefer:

- versioned image
- commit-derived tag
- immutable digest
- minimal image
- non-root process where practical
- health checks
- pinned dependencies where appropriate

Avoid relying only on:

`latest`

---

# 15. Docker Compose Rules

Before changing Compose:

1. locate authoritative file
2. inspect overrides
3. inspect environment interpolation
4. identify volumes
5. identify networks
6. identify dependencies
7. validate configuration

Where supported:

```bash
docker compose config
```

Review output carefully because resolved configuration may expose sensitive values.

Do not publish it.

---

# 16. Persistent Data Rule

Before recreating any stateful container, identify:

- mounted volumes
- bind mounts
- database path
- uploaded assets
- user-generated content
- configuration state
- backup coverage

A container is disposable.

Its persistent data may not be.

---

# 17. Database Change Rule

Database migrations require stronger controls.

Before migration:

- identify database engine/version
- inspect migration
- understand lock/downtime risk
- understand backward compatibility
- verify backup/recovery
- determine rollback or forward-fix plan
- test outside production where practical

Never assume schema rollback is safe.

---

# 18. Secrets

Secrets must not be:

- committed to Git
- placed in Markdown
- printed into logs
- included in screenshots
- exposed in dashboards
- copied into issue descriptions

If a secret is accidentally exposed:

1. treat it as compromised
2. contain exposure
3. rotate where authorized
4. identify consumers
5. verify service recovery
6. remove from history where appropriate
7. document incident without reproducing secret

---

# 19. Production Verification

Deployment is not complete when containers start.

Verify:

## Infrastructure

- expected containers running
- health checks healthy
- no crash loops
- resource usage reasonable
- required ports/listeners available

## Application

- homepage loads
- critical navigation works
- Entryway flow works
- relevant API endpoints respond
- authentication works if applicable
- product/checkout path works if affected

## Observability

- logs show no new severe errors
- analytics events arrive if affected
- release metadata is correct

## Business

- conversion-critical path is intact
- purchases reconcile if commerce changed

---

# 20. Smoke Test

Maintain a minimal production smoke test.

Suggested initial flow:

1. request homepage
2. request Entryway landing page
3. start desired-function flow if live
4. select a micro-zone if live
5. start a quest if live
6. verify product page if live
7. verify checkout entry without creating a real charge unless controlled test mechanisms exist

Automate only when safe.

---

# 21. Health Checks

Health checks should distinguish:

## Liveness

Process is running.

## Readiness

Application can serve traffic.

## Dependency Health

Critical dependencies are available.

Do not make health checks so strict that a noncritical dependency causes unnecessary restart loops.

---

# 22. Post-Deployment Monitoring

After material release, inspect:

- HTTP errors
- application errors
- container restarts
- CPU/memory
- disk
- latency
- checkout errors
- analytics drop
- conversion anomalies

Monitoring duration depends on risk.

---

# 23. Rollback Triggers

Consider rollback when:

- critical path breaks
- severe error rate increases
- checkout fails
- customer data risk appears
- container repeatedly crashes
- performance becomes unacceptable
- migration incompatibility appears
- guardrail breach is clearly attributable to release

Do not rollback automatically for ordinary metric noise.

---

# 24. Rollback Procedure

Generic sequence:

1. identify last known-good release
2. confirm data compatibility
3. stop further rollout
4. restore prior application release
5. verify containers
6. run smoke test
7. verify critical business paths
8. monitor
9. document incident
10. preserve failed release evidence

Database rollback may require a separate procedure.

---

# 25. Roll-Forward

Prefer roll-forward when:

- data migration makes rollback unsafe
- defect is well understood
- fix is small
- prior version cannot read new data safely

Document why roll-forward was safer.

---

# 26. Incident Severity

Suggested levels:

## SEV-1

Major outage, material customer-data/security risk, or inability to transact.

## SEV-2

Major feature degraded, significant error rate, serious business impact.

## SEV-3

Limited feature issue with workaround.

## SEV-4

Minor defect or operational concern.

Adapt to actual scale.

---

# 27. Incident Response

For material incident:

**Detect**
→ **Classify**
→ **Contain**
→ **Restore**
→ **Verify**
→ **Communicate**
→ **Investigate**
→ **Learn**
→ **Prevent**

Restoration comes before perfect root-cause analysis.

---

# 28. Incident Command

One agent should coordinate material incidents.

Default:

`devops-sre`

Specialists assist:

- `github-manager`
- `vps-docker-manager`
- product owner
- commerce agent
- analytics agent
- security specialist if available

Avoid multiple agents independently changing production during an incident.

---

# 29. Incident Timeline

Capture:

```yaml
incident_id: INC-0001
detected_at:
severity:
customer_impact:
release_id:
actions:
  - time:
    action:
    result:
restored_at:
root_cause:
follow_up:
```

Use verified timestamps.

---

# 30. Communication

For material owner-facing incident updates, report:

**Impact**

**Current State**

**Action Taken**

**Risk**

**Next Decision**, if needed.

Avoid dumping raw logs unless requested.

---

# 31. Logs

Use logs to answer specific questions.

Prefer bounded queries by:

- service
- severity
- timestamp
- request ID
- release

Avoid indiscriminately reading massive logs.

Never expose secrets.

---

# 32. Docker Log Inspection

Example:

```bash
docker logs --since 15m <container>
```

For Compose:

```bash
docker compose logs --since 15m <service>
```

Adjust to actual project.

---

# 33. Container Restart

Restart only after understanding why.

Before restart:

- inspect logs
- inspect health
- inspect dependencies
- determine whether restart risks data
- record current state

A restart can hide evidence.

---

# 34. Docker Prune Rule

Never autonomously run broad commands such as:

```bash
docker system prune -a
docker volume prune
```

on production without explicit understanding and authority.

Unknown volumes must be preserved.

---

# 35. Disk Pressure

If disk is filling:

1. identify filesystem
2. identify largest consumers
3. inspect Docker usage
4. inspect logs
5. inspect old images
6. inspect backups
7. distinguish safe ephemeral data from persistent data
8. clean only verified-safe targets

Do not delete data merely because it is large.

---

# 36. Memory Pressure

Investigate:

- host memory
- swap
- container usage
- leak patterns
- restart history
- traffic changes
- recent releases

Avoid arbitrary resource-limit changes without evidence.

---

# 37. CPU Pressure

Investigate:

- process/container
- traffic
- background jobs
- loops
- recent deployment
- database load
- bots/crawlers

Fix cause rather than immediately scaling.

---

# 38. Network Failure

Check:

- DNS
- TLS
- reverse proxy
- listening port
- container network
- firewall
- upstream application
- external dependency

Work outside-in or inside-out systematically.

---

# 39. DNS

Before DNS changes:

- identify authoritative provider
- capture existing records
- understand TTL
- understand mail/subdomain dependencies
- verify target
- define rollback

Domain transfer or nameserver changes are high risk.

---

# 40. TLS

Determine actual certificate mechanism:

- reverse proxy automation
- Hostinger
- Let's Encrypt
- CDN/proxy
- other

Monitor expiry.

Do not install a competing certificate system without need.

---

# 41. Reverse Proxy

Identify actual proxy before changing routing.

Possible examples:

- Nginx
- Caddy
- Traefik
- Hostinger-managed proxy

Inspect configuration and reload behavior.

Do not assume.

---

# 42. Backups

Backups require evidence.

Maturity:

**Level 0** — assumed

**Level 1** — scheduled job exists

**Level 2** — job reports success

**Level 3** — backup artifact verified

**Level 4** — representative restore validated

Target Level 4 for critical persistent data.

---

# 43. Backup Inventory

Document:

- data protected
- method
- frequency
- retention
- location
- encryption
- last successful run
- last artifact verification
- last restore test
- owner

Do not store credentials in this document.

---

# 44. Restore Testing

A restore test should answer:

- can backup be retrieved?
- can it be decrypted?
- can it be restored?
- is restored data usable?
- how long does recovery take?
- what dependencies are missing?

A successful backup job without a tested restore is incomplete evidence.

---

# 45. Recovery Objectives

When business maturity warrants, define:

**RPO** — acceptable data-loss window.

**RTO** — acceptable restoration time.

Do not invent aggressive objectives unsupported by architecture or cost.

---

# 46. Scheduled Jobs

Inventory:

- cron
- systemd timers
- application schedulers
- CI schedules
- container jobs

For each, identify:

- purpose
- owner
- frequency
- output
- failure behavior

---

# 47. Dependency Updates

Before production dependency update:

1. understand change
2. inspect security relevance
3. run tests
4. build
5. check compatibility
6. deploy through normal process
7. verify

Do not bulk-upgrade unrelated dependencies without reason.

---

# 48. Security Updates

Critical security fixes may justify accelerated deployment.

Still preserve:

- testing where feasible
- rollback
- verification
- release traceability

---

# 49. GitHub Branching

Use the repository's actual branch policy.

Preferred general principle:

- protected primary branch
- focused changes
- review/automated checks
- traceable merge
- no routine direct production edits

Do not impose GitFlow or another branching model without need.

---

# 50. Pull Requests

Material PRs should explain:

- problem
- change
- expected outcome
- testing
- risk
- rollback
- related backlog/experiment/decision

Keep routine PRs concise.

---

# 51. CI Failure

When CI fails:

1. identify failed stage
2. reproduce if practical
3. distinguish code vs infrastructure failure
4. fix smallest cause
5. rerun
6. avoid bypassing required checks

Do not disable tests to obtain a green build unless the test itself is proven invalid and change is documented.

---

# 52. Deployment Failure

If deployment fails:

1. stop repeated blind retries
2. capture error
3. determine whether old production remains healthy
4. inspect build/image/config/runtime
5. correct root cause
6. redeploy or rollback
7. verify

---

# 53. Configuration Drift

Compare:

- repository declaration
- CI configuration
- Compose/deployment configuration
- running container
- environment configuration
- production behavior

Unexplained drift becomes backlog work.

---

# 54. Manual Production Changes

Avoid routine manual mutation.

If emergency manual change is necessary:

1. record it
2. verify outcome
3. reconcile it into source control/configuration
4. remove drift

---

# 55. Database Backup Before Risky Change

For migrations with material data risk, verify a recent recoverable backup before proceeding.

"Backup job scheduled" is not enough.

---

# 56. Commerce Changes

Changes affecting products, prices, checkout, payment, taxes, shipping, fulfillment, or entitlements require:

- authoritative source identification
- test path
- reconciliation
- rollback/disable strategy
- monitoring

Never create real charges in automated smoke tests unless a sanctioned test mechanism exists.

---

# 57. Analytics Changes

When changing analytics:

- preserve event definitions
- version breaking changes
- test production event flow
- validate exclusions
- verify dashboards
- annotate experiment impact

A tracking failure can invalidate experiments.

---

# 58. SEO Deployment Checks

For SEO-related releases verify, where relevant:

- status code
- canonical
- robots
- sitemap
- title
- meta
- structured data
- internal links
- redirects
- page rendering

Do not accidentally noindex production.

---

# 59. AEO Changes

Verify structured answers and schema do not introduce:

- false claims
- fabricated reviews
- unsupported ratings
- misleading structured data

---

# 60. Performance Changes

Measure before/after when performance is the objective.

Do not claim improvement solely because code "looks faster."

---

# 61. Feature Flags

For risky customer-facing features, use existing feature-flag capability when available.

Every temporary flag should have:

- owner
- purpose
- default
- rollback use
- removal condition

Avoid permanent flag clutter.

---

# 62. Maintenance Mode

If maintenance mode exists, document:

- how to enable
- what customers see
- what remains available
- how to disable

Do not invent a maintenance mechanism during an incident unless necessary.

---

# 63. Host Reboot

Before rebooting production VPS:

- understand why
- inspect active incidents
- confirm restart policies
- identify stateful services
- verify access will return
- verify backup/recovery
- record current state

After reboot:

- confirm host
- confirm Docker
- confirm containers
- confirm proxy
- run smoke test

---

# 64. Docker Daemon Restart

Treat similarly to host-level change.

Understand impact to all containers.

---

# 65. Access Failure

If SSH access fails:

1. verify host/network
2. verify DNS/IP
3. verify credentials mechanism
4. use provider console if legitimately available
5. avoid repeated destructive recovery attempts

Escalate if access recovery exceeds authority.

---

# 66. Hostinger Provider Actions

Provider-console actions may have broad effects.

Before:

- identify exact project/VPS
- understand snapshot/rebuild/reinstall consequences
- verify data persistence
- obtain approval for destructive actions

Never click "rebuild" or equivalent on an unknown production server.

---

# 67. Disaster Recovery

If host is unrecoverable:

1. identify last verified backup
2. provision recovery target within authority
3. restore infrastructure/config
4. restore persistent data
5. restore secrets through secure mechanism
6. deploy known-good release
7. verify
8. redirect traffic only after validation
9. monitor
10. document

Actual procedure should be specialized once architecture is known.

---

# 68. Recovery Drill

Periodically test recovery without endangering production.

A useful drill validates:

- source code availability
- image/build reproducibility
- secret recovery
- data restore
- DNS/proxy procedure
- smoke test

---

# 69. Monitoring Minimums

At minimum monitor:

- website availability
- HTTP error rate
- container health/restarts
- disk
- memory
- CPU
- TLS expiry
- critical scheduled jobs
- backup state
- checkout health if commerce exists

Add complexity only as business value warrants.

---

# 70. Alert Quality

Alerts should be:

- actionable
- severity-aware
- deduplicated
- routed appropriately

Do not wake the owner for ordinary noise.

Repeated false-positive alerts should become improvement work.

---

# 71. Business Observability

Technical health alone is insufficient.

Where measurable, monitor:

- desired-function flow
- quest starts/completions
- product views
- checkout starts
- purchases

A technically healthy site can still be commercially broken.

---

# 72. Synthetic Checks

Safe synthetic monitoring may test public GET/read-only paths.

Avoid synthetic actions that:

- create customer records unnecessarily
- create real orders
- send messages
- consume inventory
- create side effects

---

# 73. Production Data Access

Use least privilege.

Prefer aggregate queries for analysis.

Do not browse private customer records without a legitimate operational need.

---

# 74. PII Handling

Do not place customer PII in:

- issue titles
- commit messages
- runbooks
- dashboard screenshots
- agent prompts unnecessarily

Sanitize examples.

---

# 75. Incident Learning

After significant incident, create durable learning if it changes future behavior.

Example:

> Deployments using mutable image tags made rollback identity ambiguous.

Then create a decision/backlog item if appropriate.

---

# 76. Post-Incident Review

For SEV-1/SEV-2:

## Impact

What customers/business experienced.

## Timeline

Verified events.

## Root Cause

Technical/system cause.

## Contributing Factors

Why defenses failed.

## Recovery

What restored service.

## Detection

How issue was discovered.

## Prevention

Specific changes.

Avoid blame.

---

# 77. Autonomous Daily Operations

A safe daily cycle may include:

1. verify production availability
2. inspect critical alerts
3. inspect failed deployments/jobs
4. verify backup status
5. reconcile GitHub/production release identity
6. inspect current resource pressure
7. inspect business-critical flow anomalies
8. update `STATUS.md` only for material changes
9. create backlog items for real issues

Do not perform changes merely to stay busy.

---

# 78. Weekly Operations Review

Review:

- uptime/incidents
- failed deployments
- change failure rate
- rollback events
- disk/resource trend
- backup evidence
- restore-test status
- security updates
- configuration drift
- operational toil

Prioritize the largest reliability constraint.

---

# 79. Monthly Resilience Review

Evaluate:

- backup/restore
- access recovery
- dependency risk
- certificate lifecycle
- capacity
- monitoring gaps
- incident learnings
- disaster recovery readiness
- infrastructure cost

---

# 80. Release Record

Maintain a release record in the appropriate system:

```yaml
release_id:
commit_sha:
image_digest:
environment:
deployed_at:
deployment_status:
smoke_test:
rollback_release:
related_backlog:
related_experiments:
```

Do not duplicate records across many Markdown files if a reliable system already exists.

---

# 81. Change Risk Classification

## LOW

- documentation
- non-production
- reversible content correction
- tested minor UI change

## MEDIUM

- production application release
- proxy/config adjustment
- dependency upgrade
- analytics schema addition

## HIGH

- database migration
- persistent storage change
- DNS change
- auth/security change
- checkout/payment change
- host rebuild
- destructive cleanup

Risk classification does not replace `AUTONOMY.md`.

---

# 82. Safe Change Window

Do not invent a maintenance window.

Use actual traffic/business patterns once known.

For higher-risk changes, prefer periods where:

- owner/support can respond
- traffic impact is lower
- recovery time is available

---

# 83. Concurrency Control

Avoid multiple autonomous agents deploying overlapping production changes simultaneously.

Use a deployment lock, queue, or coordination mechanism appropriate to the actual system.

One production change at a time is the safe default until architecture supports otherwise.

---

# 84. Agent Responsibilities

## `github-manager`

Owns repository health, branch/PR/release traceability, CI visibility, and source-control hygiene.

## `devops-sre`

Coordinates deployment reliability, incidents, monitoring, recovery, and operational standards.

## `vps-docker-manager`

Owns Hostinger VPS/Docker runtime discovery, health, resource management, Compose/runtime reconciliation, and safe server operations.

## `analytics-intelligence`

Validates instrumentation and business telemetry after relevant releases.

## `commerce-manager`

Validates commerce behavior after relevant releases.

Agents must coordinate rather than independently mutate the same production surface.

---

# 85. Escalation Conditions

Escalate to owner when:

- required authority is RED
- potential irreversible loss exists
- customer/security breach is suspected
- recovery requires destructive provider action
- significant recurring cost is required
- production identity cannot be established safely
- legal/compliance decision is required
- two active decisions conflict materially
- safe rollback is unavailable for a high-risk change

---

# 86. Escalation Format

Use:

## Situation

One paragraph.

## Impact

Customer/business impact.

## What Is Known

Verified facts.

## What Is Unknown

Critical uncertainty.

## Recommendation

Best next action.

## Risk

What could go wrong.

## Approval Needed

Exact decision.

Avoid vague "What should I do?" escalation.

---

# 87. Never Do List

Unless specifically justified and authorized, never:

- delete unknown Docker volumes
- wipe/rebuild production VPS
- force-push protected production history
- expose secrets
- disable security controls to make deployment work
- disable tests merely to pass CI
- run destructive DB commands without recovery plan
- overwrite unknown production files
- change nameservers casually
- delete backups to free space before verifying alternatives
- run broad production prune commands
- create real customer charges in tests
- fabricate operational health

---

# 88. First-Time Environment Bootstrap

When Claude first gains legitimate access:

## Phase A — Discover

Read-only inventory.

## Phase B — Map

Create architecture/runtime map.

## Phase C — Reconcile

GitHub ↔ build ↔ image ↔ VPS ↔ container ↔ domain.

## Phase D — Protect

Verify secrets, backups, persistent data, access, rollback.

## Phase E — Observe

Establish monitoring and business smoke tests.

## Phase F — Automate

Automate routine safe operations.

## Phase G — Improve

Reduce toil, risk, latency, and cost based on evidence.

Do not skip directly to Phase G.

---

# 89. Bootstrap Deliverables

After first full discovery, Claude should be able to answer:

- What repository powers 6S-success.com?
- What commit is in production?
- What image/digest is running?
- Where is the Compose/deployment configuration?
- What containers exist?
- What data persists?
- Where is it backed up?
- Can it be restored?
- What reverse proxy serves traffic?
- How is TLS renewed?
- How is production deployed?
- How is rollback performed?
- What critical dependencies exist?
- What monitoring exists?
- What remains unknown?

Unknowns should be explicit.

---

# 90. Automation Maturity

## Level 0 — Manual Unknown

Environment not understood.

## Level 1 — Observable

State can be safely inspected.

## Level 2 — Repeatable

Deployment/recovery procedures documented.

## Level 3 — Automated

Routine procedures automated.

## Level 4 — Self-Verifying

Automation verifies outcomes.

## Level 5 — Continuously Improving

Operational evidence automatically creates prioritized improvement work.

Target progression, not instant Level 5.

---

# 91. Executive Dashboard Operations Panel

Near-real-time operations panel should eventually show:

- Production: HEALTHY / DEGRADED / DOWN / UNKNOWN
- Current release
- Git commit
- image digest
- last deployment
- deployment result
- uptime/availability
- HTTP error rate
- container health
- disk pressure
- backup evidence level
- last restore test
- open incident
- pending owner decision

Never show green when data is stale or missing.

Use `UNKNOWN`.

---

# 92. Freshness

Every operational dashboard source should include freshness.

Example:

```yaml
value: HEALTHY
observed_at: 2026-08-14T20:00:00Z
source: production_health_check
```

Stale green is not healthy.

---

# 93. Autonomous Improvement Loop

Operations should continuously improve through:

**Telemetry**
→ **Constraint**
→ **Backlog**
→ **Change**
→ **Verification**
→ **Learning**
→ **Standard**

Examples:

Repeated manual restart
→ diagnose root cause
→ eliminate restart dependency.

Slow deploy
→ measure pipeline
→ improve bottleneck.

Backup uncertainty
→ restore test
→ automate verification.

---

# 94. Definition of Operational Done

A production task is not done because code merged.

Done means, as applicable:

- merged
- built
- deployed
- correct release running
- health verified
- customer behavior verified
- telemetry verified
- rollback available
- documentation updated
- experiment annotation created
- no unresolved critical error

---

# 95. RUNBOOK Maintenance

Update this file when:

- actual architecture is discovered
- deployment process changes
- recovery procedure changes
- provider changes
- incident reveals missing procedure
- autonomy boundaries change

Prefer replacing generic placeholders with verified project-specific procedures over time.

---

# 96. Project-Specific Section

This section must be populated from verified discovery.

```yaml
production_domain: 6S-success.com

github:
  repository: UNKNOWN
  default_branch: UNKNOWN
  production_branch: UNKNOWN
  ci_system: UNKNOWN
  deployment_workflow: UNKNOWN

hostinger:
  vps_identifier: UNKNOWN
  os: UNKNOWN
  project_path: UNKNOWN

docker:
  compose_project: UNKNOWN
  compose_file: UNKNOWN
  application_service: UNKNOWN
  reverse_proxy: UNKNOWN
  persistent_volumes: UNKNOWN

data:
  database: UNKNOWN
  user_uploads: UNKNOWN

backup:
  method: UNKNOWN
  frequency: UNKNOWN
  last_verified_artifact: UNKNOWN
  last_restore_test: UNKNOWN

network:
  dns_provider: UNKNOWN
  tls_mechanism: UNKNOWN

observability:
  uptime_monitor: UNKNOWN
  error_monitoring: UNKNOWN
  log_system: UNKNOWN
```

Claude must replace `UNKNOWN` only with verified evidence.

---

# 97. Immediate First Mission

Once installed in the actual repository and given legitimate infrastructure access:

1. read governing Markdown files
2. identify autonomy constraints
3. perform read-only GitHub discovery
4. perform read-only VPS/Docker discovery
5. map GitHub-to-production lineage
6. map persistent data
7. map backup/recovery
8. identify critical risks
9. update the Project-Specific Section
10. update `STATUS.md`
11. create prioritized backlog items
12. request owner approval only for actions that truly require it

Do not begin by redesigning the website.

Establish operational control first.

---

# 98. Success Criteria

This runbook is working when Claude can answer, with evidence:

**What is running?**

**Why is it running?**

**Which Git commit produced it?**

**Is it healthy?**

**Can it be rolled back?**

**Is customer data protected?**

**Can backups actually be restored?**

**What changed?**

**Did the change work?**

**What is the largest operational risk now?**

---

# 99. Final Rule

Claude Code should eventually be capable of operating 6S Success with very little owner intervention.

That does **not** mean unrestricted access without controls.

High-quality autonomy means Claude:

- knows the current state
- understands its authority
- makes small reversible changes
- verifies every material action
- protects persistent data
- preserves rollback
- measures outcomes
- learns from incidents
- escalates precise decisions
- continuously reduces operational risk and toil

The goal is not an agent that can execute the most commands.

The goal is an autonomous operating system that can **safely keep 6S-success.com healthy, recoverable, measurable, deployable, and continuously improving while the owner focuses on strategic decisions.**
