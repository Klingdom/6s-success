# 6S Success System Registry

> Canonical inventory and topology registry for the 6S Success autonomous platform. Defines what systems, environments, repositories, services, containers, data stores, integrations, agents, policies, jobs, dashboards, domains, and recovery assets actually exist and how Claude should discover, verify, reference, and maintain them.

## 1. Purpose

`SYSTEM-REGISTRY.md` is the authoritative map of the 6S Success technical and autonomous operating environment.

It answers:

- What exists?
- Where does it run?
- What is production?
- Which repository owns which component?
- Which container serves which function?
- Which system owns each class of data?
- Which external services are connected?
- Which agents exist?
- Which policy files govern them?
- Which scheduled jobs run?
- Which dashboards exist?
- Where are backups?
- Who or what owns each component?
- When was each fact last verified?

This file exists to prevent Claude and subagents from repeatedly rediscovering the same infrastructure or making assumptions about the environment.

---

# 2. Registry Principle

**Discover once, verify continuously, reference canonically.**

Do not hard-code guessed infrastructure.

Do not convert planned architecture into current-state fact.

---

# 3. Registry vs Secrets

This registry may identify that a credential exists and where it is managed.

It must never contain:

- passwords
- private keys
- API tokens
- access tokens
- database passwords
- session cookies
- recovery codes
- raw secret values

Use secret references only.

Example:

```yaml
credential:
  secret_ref: HOSTINGER_API_TOKEN
  secret_store: environment
```

Never:

```yaml
credential:
  token: actual-secret-value
```

---

# 4. Registry Status Vocabulary

Use:

- `VERIFIED`
- `DISCOVERED`
- `PLANNED`
- `DEPRECATED`
- `DISABLED`
- `UNKNOWN`

Definitions:

## VERIFIED

Existence and relevant configuration have been confirmed from an authoritative source.

## DISCOVERED

Evidence indicates the component exists, but full verification is incomplete.

## PLANNED

Defined architecture but not confirmed as implemented.

## DEPRECATED

Still exists but should not receive new dependencies.

## DISABLED

Known component intentionally inactive.

## UNKNOWN

Current state cannot be established.

---

# 5. Verification Metadata

Every material registry entry should support:

```yaml
status:
source:
verified_at:
verified_by:
confidence:
```

Use ISO-8601 timestamps where practical.

---

# 6. Stable IDs

Every material system should receive a stable ID.

Examples:

```text
repo-web
env-production
host-primary-vps
container-web
db-primary
integration-github
agent-github-manager
job-daily-growth-review
dashboard-executive
```

References across files should use IDs rather than ambiguous display names.

---

# 7. Registry Sections

The registry should maintain:

1. Business Identity
2. Domains & DNS
3. Source Control
4. Environments
5. Hosts
6. Docker / Runtime
7. Applications & Services
8. Databases & Storage
9. Networks & Ports
10. CI/CD
11. Analytics & Measurement
12. Commerce
13. SEO/AEO Integrations
14. Communications
15. External Services
16. Secrets & Credentials References
17. Agents
18. Policy & Knowledge Files
19. Scheduler & Jobs
20. Dashboards
21. Observability
22. Backups & Recovery
23. Security Controls
24. Cost Sources
25. Data Ownership
26. Dependencies
27. Retirement / Technical Debt
28. Verification Queue

---

# 8. Business Identity

```yaml
business:
  id: 6s-success
  name: 6S Success
  tagline: "Simple systems. Better living."
  primary_domain: 6S-success.com
  monthly_revenue_target_usd: 20000
  status: VERIFIED
```

The revenue value is a strategic target, not actual revenue.

---

# 9. Product Scope

Current strategic platform scope includes:

- 6S Success website
- Home Quest system
- room decks
- micro-zone decks/cards
- digital content
- physical content/products
- product catalog
- smartphone experience
- customer journeys
- quests
- multiplayer activities
- SEO/AEO content
- commerce
- executive dashboard

Implementation state for each must be verified separately.

---

# 10. Domains Registry

Canonical structure:

```yaml
domains:
  - id: domain-primary
    hostname: 6S-success.com
    purpose: primary_public_site
    registrar: UNKNOWN
    dns_provider: UNKNOWN
    status: DISCOVERED
    source: owner-provided
    verified_at: UNKNOWN
```

Do not assume DNS provider from hosting provider.

---

# 11. Domain Variants

Discover and record:

- apex
- `www`
- application subdomain
- API subdomain
- dashboard/admin subdomain
- staging subdomain
- asset/CDN subdomain

Only record verified variants as active.

---

# 12. DNS Registry

For each material record:

```yaml
dns_records:
  - id:
    hostname:
    type:
    target:
    purpose:
    proxy_status:
    ttl:
    status:
    verified_at:
```

Avoid recording sensitive internal targets when unnecessary.

---

# 13. TLS Registry

```yaml
tls:
  domain_id:
  issuer:
  expiration:
  auto_renew:
  status:
  verified_at:
```

TLS expiration should be monitored automatically.

---

# 14. Source Control Registry

Current known strategic platform uses GitHub, but actual repository details must be discovered.

```yaml
source_control:
  provider: GitHub
  status: DISCOVERED

repositories:
  - id: repo-primary
    owner: UNKNOWN
    name: UNKNOWN
    url_ref: UNKNOWN
    purpose: UNKNOWN
    default_branch: UNKNOWN
    production_branch: UNKNOWN
    visibility: UNKNOWN
    status: UNKNOWN
    verified_at: UNKNOWN
```

---

# 15. Repository Metadata

For each repository record:

- owner
- name
- purpose
- default branch
- protected branches
- CODEOWNERS
- CI workflows
- deployment relationship
- environments
- security scanning
- dependency automation
- archival status

---

# 16. Repository Ownership

Every deployed component should map to one repository or explicitly documented exception.

Example:

```yaml
component_repo_map:
  web:
    repository_id: repo-web
    path: /
```

---

# 17. GitHub Integration

```yaml
integrations:
  - id: integration-github
    provider: GitHub
    purpose:
      - source_control
      - pull_requests
      - actions
      - security
    auth_method: UNKNOWN
    secret_ref: UNKNOWN
    status: DISCOVERED
```

Do not store credentials.

---

# 18. Environments

Canonical environments may include:

```yaml
environments:
  - id: env-production
    name: production
    status: DISCOVERED

  - id: env-staging
    name: staging
    status: UNKNOWN

  - id: env-development
    name: development
    status: UNKNOWN
```

Do not assume staging exists.

---

# 19. Production Definition

Exactly one canonical environment should be identified as production.

Record:

```yaml
production:
  environment_id: UNKNOWN
  public_domain_id: domain-primary
  host_ids: []
  deployment_method: UNKNOWN
  status: UNKNOWN
```

---

# 20. Host Registry

Owner has identified Hostinger VPS as the intended/current runtime platform. Actual host details require verification.

```yaml
hosts:
  - id: host-primary-vps
    provider: Hostinger
    type: VPS
    hostname: UNKNOWN
    region: UNKNOWN
    operating_system: UNKNOWN
    cpu: UNKNOWN
    memory: UNKNOWN
    disk: UNKNOWN
    public_ip_ref: UNKNOWN
    environment_id: env-production
    status: DISCOVERED
    verified_at: UNKNOWN
```

Do not store unnecessary precise infrastructure identifiers in public-facing documentation.

---

# 21. Host Access

Record method, not credential:

```yaml
host_access:
  host_id: host-primary-vps
  methods:
    - ssh
  user: UNKNOWN
  secret_ref: UNKNOWN
  privilege_model: UNKNOWN
  status: UNKNOWN
```

---

# 22. Host Management

The Hostinger VPS/Docker Manager should own routine runtime discovery and registry updates for:

- OS
- resources
- Docker
- containers
- volumes
- ports
- capacity
- runtime health
- backup state

---

# 23. Docker Runtime

```yaml
docker:
  host_id: host-primary-vps
  engine_version: UNKNOWN
  compose_version: UNKNOWN
  compose_project: UNKNOWN
  compose_file_paths: []
  status: UNKNOWN
  verified_at: UNKNOWN
```

---

# 24. Container Registry

For each container/service:

```yaml
containers:
  - id: container-web
    name: UNKNOWN
    compose_service: UNKNOWN
    image: UNKNOWN
    image_source: UNKNOWN
    purpose: web
    environment_id: env-production
    ports: []
    volumes: []
    healthcheck: UNKNOWN
    restart_policy: UNKNOWN
    repository_id: UNKNOWN
    status: UNKNOWN
    verified_at: UNKNOWN
```

---

# 25. Container Classification

Potential purposes:

- reverse_proxy
- web
- api
- worker
- scheduler
- database
- cache
- analytics
- monitoring
- dashboard

Use actual runtime discovery.

---

# 26. Image Registry

Track:

```yaml
images:
  - id:
    repository:
    tag:
    digest:
    built_from_commit:
    deployed_environment:
    status:
```

Prefer immutable release identity where practical.

---

# 27. Volumes

```yaml
volumes:
  - id:
    name:
    host_id:
    container_ids:
    purpose:
    contains_persistent_data:
    backup_required:
    backup_method:
    status:
```

Persistent volumes must be identified.

---

# 28. Applications

```yaml
applications:
  - id: app-public-web
    name: 6S Success Website
    purpose: public_customer_experience
    repository_id: UNKNOWN
    environment_id: env-production
    container_ids: []
    domain_ids:
      - domain-primary
    framework: UNKNOWN
    status: DISCOVERED
```

---

# 29. Application Components

Discover:

- frontend
- backend/API
- worker
- scheduler
- admin
- executive dashboard
- commerce
- content management

Do not assume monolith vs microservices.

---

# 30. API Registry

```yaml
apis:
  - id:
    name:
    base_path:
    purpose:
    auth:
    application_id:
    repository_id:
    status:
```

Avoid listing private endpoints publicly.

---

# 31. Database Registry

```yaml
databases:
  - id: db-primary
    engine: UNKNOWN
    version: UNKNOWN
    environment_id: env-production
    host_location: UNKNOWN
    purpose: UNKNOWN
    persistent: true
    backup_policy_ref: UNKNOWN
    secret_ref: UNKNOWN
    status: UNKNOWN
```

Never store connection passwords.

---

# 32. Database Ownership

For every important dataset record:

- owning application
- canonical database/table
- retention
- backup
- privacy classification
- schema owner

---

# 33. Storage Registry

Potential:

- object storage
- local filesystem
- media
- generated PDFs
- card images
- product images
- customer uploads
- backups

Record actual systems.

---

# 34. Customer Uploads

Home photos and inventory data may be sensitive.

Registry must identify:

```yaml
customer_upload_storage:
  system: UNKNOWN
  encryption: UNKNOWN
  retention: UNKNOWN
  access_policy: UNKNOWN
  status: UNKNOWN
```

---

# 35. Network Registry

Record architecture, not secrets.

Potential:

```yaml
network:
  reverse_proxy: UNKNOWN
  firewall: UNKNOWN
  public_ports: UNKNOWN
  internal_networks: UNKNOWN
  status: UNKNOWN
```

---

# 36. Public Ports

The VPS Manager should maintain an authoritative list.

Unexpected public ports should trigger review.

---

# 37. Reverse Proxy

```yaml
reverse_proxy:
  technology: UNKNOWN
  container_id: UNKNOWN
  config_location: UNKNOWN
  tls_termination: UNKNOWN
  status: UNKNOWN
```

---

# 38. CI/CD Registry

```yaml
cicd:
  provider: UNKNOWN
  repository_id: UNKNOWN
  workflows:
    - id:
      name:
      trigger:
      purpose:
      environment:
      required:
      status:
```

---

# 39. Deployment Registry

```yaml
deployment:
  production_method: UNKNOWN
  source_repository: UNKNOWN
  source_branch: UNKNOWN
  release_identity: UNKNOWN
  deployment_lock: UNKNOWN
  rollback_method: UNKNOWN
  status: UNKNOWN
```

---

# 40. Release Lineage

Every production release should eventually map:

```text
Task
→ PR
→ Commit
→ Image
→ Deployment
→ Production Version
```

---

# 41. Analytics Registry

```yaml
analytics:
  - id: analytics-primary
    provider: UNKNOWN
    property_id_ref: UNKNOWN
    purpose:
      - acquisition
      - customer_journey
      - conversion
    auth_method: UNKNOWN
    secret_ref: UNKNOWN
    status: UNKNOWN
```

---

# 42. Analytics Events

The canonical event taxonomy belongs in `METRICS.md` / `DATA-CONTRACTS.md`.

Registry should identify where events are collected and stored.

---

# 43. Search / SEO Registry

Potential:

```yaml
search_integrations:
  - id: search-console
    provider: UNKNOWN
    property: UNKNOWN
    auth_method: UNKNOWN
    status: UNKNOWN
```

Verify actual search tooling.

---

# 44. AEO Measurement

Record any systems used to measure:

- AI referral traffic
- answer-engine referrals
- structured data
- content citation/referral signals

Do not invent provider visibility.

---

# 45. Commerce Registry

```yaml
commerce:
  platform: UNKNOWN
  store_id_ref: UNKNOWN
  checkout: UNKNOWN
  payments: UNKNOWN
  product_source_of_truth: UNKNOWN
  order_source_of_truth: UNKNOWN
  refund_source_of_truth: UNKNOWN
  status: UNKNOWN
```

---

# 46. Payment Provider

```yaml
payments:
  provider: UNKNOWN
  account_ref: UNKNOWN
  webhook_endpoint_ref: UNKNOWN
  secret_refs: []
  status: UNKNOWN
```

Never store keys.

---

# 47. Product Catalog Relationship

`PRODUCT-CATALOG.md` defines product architecture.

Registry identifies the actual system that stores/serves products.

---

# 48. Fulfillment Registry

Potential:

- digital delivery
- physical fulfillment
- print-on-demand
- 3D print
- service booking
- third-party affiliate

Record only actual systems.

---

# 49. Email Registry

```yaml
email:
  transactional_provider: UNKNOWN
  marketing_provider: UNKNOWN
  sender_domains: []
  auth_secret_refs: []
  status: UNKNOWN
```

---

# 50. Communications Registry

Potential:

- email
- SMS
- push
- support
- social publishing

Each should include permission/consent implications.

---

# 51. External Service Registry

For every external service:

```yaml
external_services:
  - id:
    provider:
    purpose:
    data_shared:
    auth_method:
    secret_ref:
    cost_model:
    criticality:
    status:
    verified_at:
```

---

# 52. Criticality

Use:

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

Critical services require stronger monitoring/recovery planning.

---

# 53. Secrets Registry

References only:

```yaml
secrets:
  - id:
    name:
    purpose:
    store:
    consumers:
    rotation_policy:
    last_rotated: UNKNOWN
    status:
```

Never place secret values here.

---

# 54. Secret Stores

Discover actual stores:

- Hostinger environment
- GitHub Actions secrets
- `.env` on VPS
- dedicated secret manager
- application configuration

If plaintext secrets are found in repository, treat as security issue.

---

# 55. Agent Registry

```yaml
agents:
  - id: agent-github-manager
    name: GitHub Manager
    file: UNKNOWN
    domain: source_control
    write_authority: UNKNOWN
    deploy_authority: UNKNOWN
    status: DISCOVERED
```

---

# 56. Known Agent Categories

Based on current architecture, discover actual configured files for:

- GitHub Manager
- Hostinger VPS/Docker Manager
- DevOps/SRE
- Security
- Analytics
- SEO/AEO
- Content
- Customer Journey/UX
- Quest/Game Experience
- Product/Catalog
- Commerce
- Growth
- Cost/Finance
- orchestrator

Do not mark as active merely because recommended.

---

# 57. Agent File Location

Claude Code agent files may live under a configured project directory.

Registry should discover actual paths.

Example conceptual:

```yaml
agent_file:
  path: .claude/agents/github-manager.md
```

Do not assume this path without verification.

---

# 58. Agent Authority

Each agent registry entry should identify:

```yaml
authority:
  read:
  write:
  deploy:
  spend:
  external_publish:
  destructive_actions:
```

Canonical authority remains in `AUTONOMY.md`.

---

# 59. Policy File Registry

```yaml
policy_files:
  - id: policy-autonomy
    path: AUTONOMY.md
    purpose: autonomous authority
    required: true
    status: UNKNOWN
```

---

# 60. Recommended Canonical Files

Discover whether these exist:

- `CLAUDE.md`
- `AUTONOMY.md`
- `AUTONOMOUS-OPERATING-LOOP.md`
- `SYSTEM-REGISTRY.md`
- `SCHEDULER.md`
- `STATUS.md`
- `BACKLOG.md`
- `DECISIONS.md`
- `LEARNINGS.md`
- `METRICS.md`
- `DATA-CONTRACTS.md`
- `OBSERVABILITY.md`
- `TESTING.md`
- `RELEASES.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `DISASTER-RECOVERY.md`
- `COST-GOVERNANCE.md`
- `EXPERIMENTS.md`
- `PRODUCT-CATALOG.md`
- `CUSTOMER-JOURNEY.md`
- `GROWTH-ENGINE.md`
- `EXECUTIVE-DASHBOARD.md`

This list is architectural guidance, not proof the files exist.

---

# 61. Policy Integrity

Registry should track:

- path
- last modified
- required
- owner
- conflicts
- status

Do not duplicate full policy contents.

---

# 62. Scheduler Registry

```yaml
scheduler:
  technology: UNKNOWN
  host: UNKNOWN
  heartbeat: UNKNOWN
  global_pause: UNKNOWN
  status: UNKNOWN
```

---

# 63. Job Registry

```yaml
jobs:
  - id:
    name:
    owner_agent:
    schedule:
    purpose:
    read_write_mode:
    timeout:
    retry:
    lock:
    cost_class:
    last_run:
    last_status:
    enabled:
```

---

# 64. Job Categories

Potential:

- health
- analytics
- growth
- SEO
- content
- product
- backup
- security
- cost
- dashboard
- cleanup

---

# 65. Dashboard Registry

```yaml
dashboards:
  - id: dashboard-executive
    name: Executive Dashboard
    url_ref: UNKNOWN
    application_id: UNKNOWN
    authentication: UNKNOWN
    data_source: UNKNOWN
    status: UNKNOWN
```

---

# 66. Executive Dashboard

Requirements live in `EXECUTIVE-DASHBOARD.md`.

Registry only describes the deployed implementation.

---

# 67. Observability Registry

```yaml
observability:
  logs: UNKNOWN
  metrics: UNKNOWN
  traces: UNKNOWN
  errors: UNKNOWN
  uptime: UNKNOWN
  alerting: UNKNOWN
  status: UNKNOWN
```

---

# 68. Log Registry

Identify:

- application logs
- reverse-proxy logs
- Docker logs
- system logs
- security logs
- deployment logs

Define retention elsewhere.

---

# 69. Monitoring Targets

Registry should identify monitored:

- domain
- homepage
- API
- checkout
- database
- host
- containers
- scheduler
- backups

---

# 70. Backup Registry

```yaml
backups:
  - id:
    system:
    data:
    destination:
    frequency:
    retention:
    encryption:
    last_success:
    last_restore_test:
    status:
```

---

# 71. Backup Rule

A backup is not considered fully verified until restoration has been tested according to recovery policy.

---

# 72. Recovery Registry

```yaml
recovery:
  production:
    runbook_ref: DISASTER-RECOVERY.md
    rpo: UNKNOWN
    rto: UNKNOWN
    rollback_method: UNKNOWN
    rebuild_method: UNKNOWN
    status: UNKNOWN
```

---

# 73. Security Control Registry

Track implementation status of:

- TLS
- firewall
- least privilege
- SSH controls
- GitHub branch protection
- dependency scanning
- secret scanning
- backups
- authentication
- authorization
- patching
- logging

Canonical policy remains in `SECURITY.md`.

---

# 74. Cost Source Registry

```yaml
cost_sources:
  - id:
    provider:
    category:
    billing_source:
    currency:
    refresh:
    status:
```

Potential categories:

- hosting
- AI
- APIs
- SaaS
- email
- commerce
- fulfillment
- approved advertising

---

# 75. AI Provider Registry

If AI services are used:

```yaml
ai_providers:
  - id:
    provider:
    purpose:
    model_classes:
    billing_source:
    secret_ref:
    allowed_agents:
    status:
```

Do not store API keys.

---

# 76. Data Domain Registry

Canonical domains may include:

- customer
- household
- room
- micro-zone
- desired function
- root cause
- quest
- card
- product
- order
- outcome
- content
- analytics
- operations

---

# 77. Data Ownership

Each domain should have one canonical source.

Example:

```yaml
data_ownership:
  product:
    source_system: UNKNOWN
    schema_ref: UNKNOWN
  order:
    source_system: UNKNOWN
  quest:
    source_system: UNKNOWN
```

---

# 78. Canonical IDs

Use stable IDs across:

- website
- app
- cards
- QR codes
- analytics
- products
- quests
- dashboard

Avoid name-based joins when stable IDs are available.

---

# 79. Data Classification

Potential:

- `PUBLIC`
- `INTERNAL`
- `CONFIDENTIAL`
- `SENSITIVE`

Home photos, customer contact information, authentication data, and detailed household inventory may require higher classification.

---

# 80. Integration Map

Maintain relationships.

Example:

```text
GitHub
  ↓
CI/CD
  ↓
Hostinger VPS
  ↓
Docker
  ↓
Web/API
  ↓
Database

Website
  ↔ Analytics
  ↔ Search
  ↔ Commerce
  ↔ Email

Scheduler
  ↔ Agents
  ↔ GitHub
  ↔ VPS
  ↔ Dashboard
```

Actual topology must be discovered.

---

# 81. Dependency Registry

```yaml
dependencies:
  - consumer:
    provider:
    type:
    criticality:
    failure_behavior:
```

This helps incident analysis.

---

# 82. Critical Path

Discover the actual customer purchase path.

Potential:

```text
DNS
→ VPS
→ Reverse Proxy
→ Web
→ API
→ Database
→ Payment Provider
```

Every critical dependency should be monitored.

---

# 83. Customer Journey Technology Map

Map journey stages to systems.

Example:

```yaml
journey_system_map:
  discovery:
    systems: []
  diagnosis:
    systems: []
  quest:
    systems: []
  commerce:
    systems: []
  outcome:
    systems: []
```

---

# 84. Entryway Technology Map

Because Entryway is the initial proving ground, explicitly map:

- pages
- APIs
- quest definitions
- cards
- products
- analytics
- QR routes
- outcome events

---

# 85. QR Registry

For physical cards:

```yaml
qr_routes:
  - card_id:
    destination:
    canonical_url:
    status:
```

Avoid QR links to generic homepage when specific card context exists.

---

# 86. Content Registry Relationship

Do not list every article manually here.

Instead identify:

- content storage system
- repository/path
- CMS if any
- publication workflow
- canonical URL rules

---

# 87. Product Registry Relationship

Do not duplicate `PRODUCT-CATALOG.md`.

Identify implementation:

```yaml
product_catalog_system:
  source: UNKNOWN
  sync_method: UNKNOWN
  commerce_mapping: UNKNOWN
```

---

# 88. Experiment System Registry

```yaml
experimentation:
  system: UNKNOWN
  assignment_method: UNKNOWN
  event_source: UNKNOWN
  analysis_source: UNKNOWN
  status: UNKNOWN
```

---

# 89. Feature Flags

```yaml
feature_flags:
  provider: UNKNOWN
  implementation: UNKNOWN
  status: UNKNOWN
```

Do not assume a dedicated service exists.

---

# 90. Technical Debt Registry

Track systemic issues only.

```yaml
technical_debt:
  - id:
    component:
    issue:
    risk:
    priority:
    planned_action:
```

Detailed work belongs in `BACKLOG.md`.

---

# 91. Deprecated Systems

Never silently delete registry entries when systems are retired.

Mark:

```yaml
status: DEPRECATED
replaced_by:
retirement_date:
```

Then archive according to policy.

---

# 92. Orphan Detection

Periodically detect:

- container with no repository
- domain with no owner
- secret with no consumer
- job with no owner
- database with no backup
- service with no monitoring
- repository with no deployment relationship
- product with no catalog mapping
- metric with no source

Orphans are governance risks.

---

# 93. Drift Detection

Compare registry with actual systems.

Examples:

- new container not registered
- changed port
- new GitHub workflow
- deleted branch
- new external service
- changed DNS
- missing backup
- changed scheduler job

Record drift before automatically accepting it as standard.

---

# 94. Registry Update Authority

Specialist agents may update entries in their domains when facts are verified.

Examples:

- GitHub Manager → repositories/workflows
- VPS Manager → host/containers
- Analytics Agent → analytics sources
- Commerce Agent → commerce systems
- Scheduler → jobs

The orchestrator resolves cross-domain conflicts.

---

# 95. Registry Change Rules

Material changes should be traceable through Git.

Do not allow autonomous agents to overwrite unrelated registry sections.

---

# 96. Registry Validation

Automated validation should check:

- duplicate IDs
- broken references
- invalid statuses
- missing required fields
- secret-looking values
- impossible environment mappings
- stale verification

---

# 97. Secret Scanner

Registry CI should reject likely:

- API keys
- passwords
- private keys
- bearer tokens
- database credentials

False positives should be reviewed safely.

---

# 98. Freshness

Different entries have different freshness expectations.

Potential:

## Minutes/Hours

- production release
- container state

## Daily

- host capacity
- scheduler
- external integration status

## Weekly

- repository governance
- security controls

## Monthly/Quarterly

- architectural ownership
- deprecated systems

---

# 99. Stale Registry

If verification exceeds expected freshness:

```yaml
status: UNKNOWN
```

or preserve prior status with explicit stale flag depending on implementation.

Never silently imply current verification.

---

# 100. Machine-Readable Companion

Long term, maintain a structured companion such as:

```text
system-registry.yaml
```

or:

```text
/config/system-registry.yaml
```

`SYSTEM-REGISTRY.md` defines semantics and human-readable context.

The structured registry should support automation.

---

# 101. Generated vs Hand-Maintained Fields

Prefer automation for:

- GitHub branch
- latest release
- container versions
- host resources
- last backup
- scheduler state

Prefer governed manual/owner input for:

- strategic purpose
- criticality
- ownership
- policy relationship

---

# 102. Executive Dashboard Integration

The registry supplies topology and ownership to `EXECUTIVE-DASHBOARD.md`.

Dashboard should not independently rediscover infrastructure.

---

# 103. Autonomous Operating Loop Integration

At the start of relevant cycles, `AUTONOMOUS-OPERATING-LOOP.md` should use the registry to know:

- which systems exist
- where evidence comes from
- which agent owns the system
- what authority applies

---

# 104. Incident Integration

During incidents, registry should quickly answer:

- what failed
- dependencies
- owner agent
- deployment source
- recovery asset
- monitoring source

---

# 105. Disaster Recovery Integration

`DISASTER-RECOVERY.md` should reference registry IDs.

Example:

```text
Restore `db-primary` from `backup-db-primary`.
Redeploy `app-public-web` from `repo-web`.
```

This is safer than ambiguous names.

---

# 106. Cost Governance Integration

`COST-GOVERNANCE.md` should map costs to registry service IDs.

This enables:

- provider spend
- component spend
- agent spend
- growth-channel spend

---

# 107. Access Review

Registry should support periodic review:

- who/what can access GitHub
- who/what can deploy
- who/what can SSH
- who/what can access database
- which agents can spend
- which agents can publish

Do not store sensitive identity details unnecessarily.

---

# 108. Owner Control

The executive dashboard should eventually provide drill-down from:

```text
Production
→ Host
→ Containers
→ Release
→ GitHub Commit
```

and:

```text
Revenue
→ Commerce
→ Product
→ Quest
→ Micro-Zone
```

using registry IDs.

---

# 109. Initial Registry State

The following reflects only information currently established at the architecture level and must be verified by Claude Code against real systems.

```yaml
business:
  id: 6s-success
  name: 6S Success
  tagline: "Simple systems. Better living."
  primary_domain: 6S-success.com
  monthly_revenue_target_usd: 20000
  status: VERIFIED

domain:
  primary:
    hostname: 6S-success.com
    registrar: UNKNOWN
    dns_provider: UNKNOWN
    status: DISCOVERED

source_control:
  provider: GitHub
  repositories: UNKNOWN
  status: DISCOVERED

hosting:
  provider: Hostinger
  platform: VPS
  hosts: UNKNOWN
  status: DISCOVERED

runtime:
  technology: Docker
  compose_project: UNKNOWN
  containers: UNKNOWN
  status: DISCOVERED

production:
  canonical_environment: UNKNOWN
  deployed_release: UNKNOWN
  status: UNKNOWN

database:
  systems: UNKNOWN

analytics:
  systems: UNKNOWN

search:
  systems: UNKNOWN

commerce:
  systems: UNKNOWN

email:
  systems: UNKNOWN

observability:
  systems: UNKNOWN

backups:
  systems: UNKNOWN

scheduler:
  system: UNKNOWN

dashboard:
  executive_dashboard: UNKNOWN

agents:
  orchestrator: DISCOVERED
  github_manager: DISCOVERED
  hostinger_vps_docker_manager: DISCOVERED
  other_specialists: DISCOVERED

policy_files:
  inventory: UNKNOWN
```

`DISCOVERED` above means the component/category has been explicitly described as part of the intended/current project architecture, not that implementation details have been technically verified.

---

# 110. First Registry Mission

When Claude Code first uses this file:

1. inspect repository root
2. inventory Markdown governance files
3. inventory `.claude` configuration
4. inventory configured subagents
5. inspect Git remotes
6. identify GitHub repository
7. identify default/protected branches
8. inventory GitHub workflows
9. identify deployment mechanism
10. connect to authorized Hostinger VPS
11. identify OS/resources
12. inventory Docker/Compose
13. inventory containers/images/volumes/networks
14. identify production application
15. identify reverse proxy
16. identify database/storage
17. identify public ports
18. identify domain/DNS/TLS evidence
19. identify analytics
20. identify search tooling
21. identify commerce/payment systems
22. identify email/external services
23. identify scheduler/jobs
24. identify observability
25. identify backups/recovery
26. identify cost sources
27. map secret references without exposing values
28. identify executive dashboard implementation
29. identify orphaned/unmanaged resources
30. populate verified registry
31. commit through normal GitHub workflow
32. update dashboard/system status

Do not make broad infrastructure changes during registry discovery.

---

# 111. Bootstrap Output

After first discovery, Claude should produce a concise summary:

```text
SYSTEM REGISTRY BOOTSTRAP

Verified:
- X repositories
- X production hosts
- X containers
- X databases
- X external services
- X agents
- X scheduled jobs
- X backup systems

Unknown:
- ...

Risks:
- ...

Orphans:
- ...

Next:
- ...
```

Use real counts only.

---

# 112. Registry Maturity Model

## Level 0: Unknown

Infrastructure is mostly tribal knowledge.

## Level 1: Inventoried

Major systems are listed.

## Level 2: Verified

Entries include authoritative evidence and freshness.

## Level 3: Integrated

Agents, dashboard, recovery, deployment, and costs use canonical registry IDs.

## Level 4: Drift Managed

Automation continuously compares registry to reality.

## Level 5: Autonomous System Map

The registry is a continuously verified machine-readable topology of the entire 6S Success business platform. Claude can safely reason about dependencies, ownership, deployments, recovery, costs, customer journeys, and autonomous work without repeatedly rediscovering the environment.

---

# 113. Non-Negotiable Registry Rules

Claude and subagents must not:

- store secrets
- guess infrastructure
- mark planned systems VERIFIED
- mark discovered systems VERIFIED without evidence
- duplicate authoritative business data unnecessarily
- create conflicting IDs
- silently accept infrastructure drift
- remove retired systems without history
- expose unnecessary sensitive infrastructure details
- allow stale registry data to masquerade as current
- let multiple agents overwrite unrelated registry domains
- treat documentation as more authoritative than the live system for runtime state
- treat the live system as more authoritative than policy for what should be allowed

---

# 114. Final Principle

Claude cannot safely own and continuously improve a system it cannot accurately map.

`SYSTEM-REGISTRY.md` gives the autonomous platform a shared vocabulary for reality:

**This is the domain.**

**This is the repository.**

**This is production.**

**This is the VPS.**

**These are the containers.**

**This is the database.**

**These are the integrations.**

**These are the agents.**

**These are their policies.**

**These jobs run automatically.**

**These systems contain persistent data.**

**These backups protect them.**

**These services cost money.**

**These components are critical.**

**These facts were last verified here.**

Once that map exists, the orchestrator can stop rediscovering the platform and start managing it as a coherent system.

That is the purpose of `SYSTEM-REGISTRY.md`.
