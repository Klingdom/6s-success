# 6S Success Release Management

> Canonical policy for versioning, release identity, GitHub commits and tags, CI/CD artifacts, Docker images and digests, deployment promotion, database compatibility, feature flags, release notes, verification, rollback, and production lineage for 6S-success.com.

## 1. Purpose

`RELEASES.md` defines how a change becomes a known, traceable, verified production release.

The system must be able to answer:

**What code is running on 6S-success.com right now?**

**Which Git commit produced it?**

**Which Docker image is running?**

**When was it deployed?**

**What changed?**

**Was it verified?**

**What version can we safely return to?**

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `RUNBOOK.md`
- `SECURITY.md`
- `TESTING.md`
- `OBSERVABILITY.md`
- `DATA-CONTRACTS.md`
- `BACKLOG.md`
- `EXPERIMENTS.md`
- `DECISIONS.md`
- `LEARNINGS.md`

---

# 2. Prime Release Rule

**A deployment is not a release until its identity and outcome are verified.**

A successful shell command is not sufficient.

Canonical lineage:

**Backlog / Experiment / Fix**
→ **Git Commit**
→ **CI**
→ **Build**
→ **Artifact / Docker Image**
→ **Immutable Digest**
→ **Deployment**
→ **Running Runtime**
→ **Smoke Test**
→ **Business Verification**
→ **Release Record**

---

# 3. Source of Truth

GitHub should be the source of truth for deployable application code unless verified architecture defines otherwise.

Production must not become an undocumented collection of manual VPS edits.

If production contains manual drift:

1. discover it
2. preserve it
3. understand it
4. reconcile it
5. return the system to a reproducible state

Never destroy unknown production changes merely to make Git match.

---

# 4. Release Identity

Every material production deployment should have a unique release identity.

Recommended:

```yaml
release_id: rel-2026-08-14-001
commit_sha: full-git-sha
git_tag: nullable
image_repository: string
image_tag: string
image_digest: sha256:...
environment: production
deployed_at: ISO-8601
deployment_status: string
```

The exact release ID format may be adapted once the actual project is discovered.

---

# 5. Immutable Identity

Preferred strongest identity:

**Git SHA + Docker Image Digest**

Human-readable tags are useful.

Mutable tags are not sufficient proof of what is running.

Avoid relying solely on:

`latest`

---

# 6. Git Commit

Every production release should map to a Git commit.

The commit should represent the code used to build the artifact.

If the build modifies code or assets dynamically, that process must be understood and reproducible.

---

# 7. Git Tags

Use tags for meaningful releases when useful.

Suggested semantic forms:

```text
v1.0.0
v1.1.0
v1.1.1
```

or release-oriented tags:

```text
prod-2026-08-14.1
```

Do not introduce a tagging scheme that conflicts with an existing established process.

---

# 8. Semantic Versioning

Where product/API compatibility benefits from semantic versioning:

- MAJOR = incompatible change
- MINOR = backward-compatible capability
- PATCH = backward-compatible fix

Not every content deployment requires a public semantic version bump.

---

# 9. Docker Image Tags

Recommended tags may include:

```text
sha-<shortsha>
rel-<release-id>
```

Optional convenience tags may exist, but production lineage must resolve to immutable digest.

---

# 10. Image Digest

Record the digest actually deployed.

Example:

```text
sha256:abc...
```

This allows Claude to distinguish two different images that may have shared a mutable tag.

---

# 11. Build Reproducibility

The build should be reproducible enough that Claude can explain:

- source commit
- build process
- dependencies
- artifact
- image
- deployment

Avoid undocumented manual modifications inside running containers.

---

# 12. Release Environments

Canonical:

- development
- test
- staging
- production

Do not assume staging exists.

Document actual promotion path.

---

# 13. Promotion

Preferred concept:

**Build once → promote the same artifact**

rather than rebuilding different code for each environment.

If architecture currently rebuilds per environment, document that fact and associated risk.

---

# 14. Release Candidate

For higher-risk releases, a candidate artifact may be tested before production.

Example:

```yaml
release_candidate: rc-2026-08-14-001
commit_sha: ...
image_digest: ...
```

Do not create ceremony for trivial changes.

---

# 15. Release Risk

Classify:

## LOW

- copy
- documentation
- isolated presentation
- low-risk content

## MEDIUM

- feature
- API
- analytics
- SEO template
- recommendation logic

## HIGH

- database migration
- authentication
- authorization
- payments
- infrastructure
- persistent storage
- DNS
- security architecture

Risk controls follow `AUTONOMY.md`, `TESTING.md`, and `RUNBOOK.md`.

---

# 16. Release Readiness

Before production, verify applicable:

- [ ] scope understood
- [ ] tests pass
- [ ] build passes
- [ ] security checks acceptable
- [ ] analytics changes validated
- [ ] SEO/AEO changes validated
- [ ] commerce changes validated
- [ ] migrations understood
- [ ] rollback/forward-fix understood
- [ ] backup evidence adequate
- [ ] feature flags configured
- [ ] release identity established
- [ ] smoke test defined
- [ ] authority confirmed

---

# 17. CI Gate

Production release should normally originate from successful CI.

Required gates depend on change surface.

Do not bypass failing checks simply to deploy faster.

Any emergency bypass must follow documented authority and create follow-up work.

---

# 18. Artifact Integrity

The artifact deployed should be the artifact tested.

Avoid:

**test commit A**
→ **manually edit**
→ **deploy untested state B**

---

# 19. Production Branch

Discover actual policy.

Do not assume `main`, `master`, or `production`.

Record:

```yaml
default_branch: UNKNOWN
production_branch: UNKNOWN
```

---

# 20. Protected Branches

Production-critical history should be protected against accidental destructive operations.

Controls may include:

- required PR
- required CI
- force-push restriction
- deletion restriction

Adapt to project scale.

---

# 21. Pull Request Release Metadata

Material PRs should identify:

- purpose
- related backlog item
- related experiment if any
- risk
- tests
- migration impact
- analytics impact
- rollback

This improves autonomous release reasoning.

---

# 22. Changelog

Maintain a concise release history.

Useful categories:

- Added
- Changed
- Fixed
- Performance
- SEO/AEO
- Commerce
- Infrastructure
- Security

Do not turn changelog into commit dump.

---

# 23. Release Notes

Owner-facing notes should emphasize business meaning.

Example:

```markdown
## rel-2026-08-14-001

### Customer Impact
Entryway visitors can now select a desired function before choosing a quest.

### Business Hypothesis
Better goal alignment should improve quest-start and completion rates.

### Technical
Added desired-function selection and analytics events.

### Risk
Low/Medium.

### Verification
Critical Entryway E2E passed. Production smoke passed.

### Measurement
EXP-001 or metric baseline reference.
```

---

# 24. Release Record

Canonical release record:

```yaml
release_id:
commit_sha:
git_tag:
image_tag:
image_digest:
environment:
deployed_at:
deployed_by:
change_type:
risk:
related_backlog_ids: []
related_experiment_ids: []
migration_ids: []
feature_flags: []
ci_status:
smoke_test_status:
business_verification:
rollback_release_id:
status:
```

---

# 25. Release Status

Use:

- `PLANNED`
- `BUILDING`
- `READY`
- `DEPLOYING`
- `VERIFYING`
- `HEALTHY`
- `DEGRADED`
- `ROLLED_BACK`
- `FAILED`
- `UNKNOWN`

Do not mark `HEALTHY` until verification occurs.

---

# 26. Deployment

Use the established deployment mechanism.

Do not create parallel deployment paths without reason.

Preferred characteristics:

- repeatable
- auditable
- CI-driven
- minimal manual mutation
- deterministic artifact
- rollback support

---

# 27. Deployment Lock

Avoid overlapping production deployments.

Use an existing concurrency control if available.

Otherwise, one production deployment at a time is the safe default.

---

# 28. Deployment Start

Record:

- release
- actor/agent
- target
- start time
- previous release

This makes recovery easier.

---

# 29. Deployment Completion

A deployment command completing means:

`DEPLOYED`

not automatically:

`HEALTHY`

Proceed to verification.

---

# 30. Runtime Verification

Confirm:

- expected container/service
- expected image
- expected digest
- health
- restart count
- expected ports/routes
- release metadata

---

# 31. Smoke Verification

Follow `TESTING.md`.

At minimum for relevant releases:

- homepage
- Entryway
- critical changed flow
- product/checkout if affected
- analytics if affected
- auth if affected

---

# 32. Business Verification

For material customer-facing releases, verify the business path rather than only HTTP 200.

Examples:

- quest can start
- quest can complete
- product recommendation appears
- checkout can initiate
- analytics records intended event

---

# 33. Observation Window

Risk determines post-release monitoring duration.

Monitor:

- error rate
- latency
- container health
- business funnel
- checkout
- analytics
- resource use

Delayed failures should be considered.

---

# 34. Release Annotations

Annotate major releases in business/technical dashboards.

This supports:

**What changed when this metric changed?**

Do not infer causality automatically.

---

# 35. Rollback Target

Before deployment, identify the last known-good release.

Example:

```yaml
rollback_release_id: rel-2026-08-13-004
rollback_image_digest: sha256:...
```

---

# 36. Rollback Safety

Before rollback:

- confirm old artifact exists
- confirm configuration compatibility
- confirm database compatibility
- confirm persistent-data compatibility

An application rollback after a breaking migration may be unsafe.

---

# 37. Rollback Trigger

Consider rollback for:

- severe errors
- critical journey failure
- payment failure
- security regression
- unacceptable performance regression
- crash loop
- data integrity risk

Follow `RUNBOOK.md`.

---

# 38. Roll Forward

Use roll-forward when rollback is unsafe and a focused fix is safer.

Record why.

---

# 39. Database Migration Identity

Every material migration should have an identity.

Example:

```yaml
migration_id: db-2026-08-14-001
release_id: rel-2026-08-14-001
backward_compatible: true
rollback_supported: false
```

---

# 40. Expand/Contract Migration

For risky schema evolution, prefer backward-compatible patterns where practical:

1. expand schema
2. deploy compatible application
3. migrate/backfill
4. verify
5. switch behavior
6. remove obsolete schema later

Avoid requiring perfectly synchronized destructive changes.

---

# 41. Migration Backup

Before a material irreversible migration, verify recovery evidence appropriate to risk.

Do not rely solely on "backup is scheduled."

---

# 42. Feature Flags

Feature flags can separate deployment from release.

Use when they materially reduce risk.

Examples:

- new desired-function flow
- new quest algorithm
- new product recommendation
- new checkout experience

---

# 43. Feature Flag Metadata

Each temporary flag should have:

```yaml
flag_id:
purpose:
owner:
default:
created_at:
related_release:
related_experiment:
removal_condition:
```

---

# 44. Feature Flag Cleanup

Remove stale flags after:

- rollout complete
- experiment decision complete
- rollback period ends

Permanent flag clutter increases complexity.

---

# 45. Kill Switch

High-risk new capabilities may have a kill switch where practical.

Examples:

- autonomous publishing
- AI recommendation service
- checkout integration
- expensive AI feature

A kill switch should disable risky behavior without destroying data.

---

# 46. Canary Release

Canary deployment may be appropriate at higher scale.

Do not add canary infrastructure before traffic and architecture justify it.

---

# 47. Blue/Green

Blue/green may reduce downtime and rollback risk.

Again, use only when operational value exceeds complexity.

---

# 48. Content Releases

Content can often release more frequently than application code.

Still validate:

- build
- links
- metadata
- SEO
- privacy
- CTA
- no secrets

High-volume autonomous publishing requires quality gates.

---

# 49. SEO Releases

SEO-sensitive changes require:

- canonical verification
- robots verification
- sitemap verification
- redirect verification
- structured-data verification
- production rendering

Never accidentally deploy site-wide `noindex`.

---

# 50. AEO Releases

Validate visible content matches structured data.

Do not deploy unsupported claims, fake reviews, or misleading schema.

---

# 51. Commerce Releases

Changes affecting:

- price
- checkout
- products
- payment
- fulfillment
- entitlements
- refunds

require stronger release controls.

Verify authoritative commerce state.

---

# 52. Analytics Releases

When event schemas change:

- validate contract
- version breaking changes
- verify ingestion
- verify dashboard
- annotate experiments

Do not silently break historical comparability.

---

# 53. Experiment Releases

An experiment release should record:

- experiment ID
- variants
- assignment mechanism
- exposure verification
- guardrails
- start state

The release system and experiment system must be connected.

---

# 54. Security Releases

Security fixes may be expedited.

Still preserve:

- artifact identity
- verification
- rollback where safe
- incident linkage
- disclosure discipline

Do not include sensitive exploit detail in public release notes unnecessarily.

---

# 55. Dependency Releases

Group dependency updates only when sensible.

Avoid giant unrelated upgrade bundles that make regressions hard to isolate.

---

# 56. Emergency Release

Emergency release process may shorten normal gates but must not eliminate:

- target verification
- artifact identity
- minimal test
- production verification
- incident record
- post-release review

---

# 57. Hotfix

A hotfix should be:

- narrow
- traceable
- tested
- merged back into canonical source
- followed by normal verification

Do not leave production-only hotfixes uncommitted.

---

# 58. Failed Release

On failure:

1. preserve evidence
2. stop blind retries
3. determine current production state
4. rollback or fix
5. verify
6. update release status
7. create incident if warranted

---

# 59. Partial Deployment

If only some services update:

- identify exact running versions
- determine compatibility
- restore coherent state
- verify

Never assume the deployment was atomic unless architecture guarantees it.

---

# 60. Release Drift

Detect when:

- VPS code differs from Git
- container image differs from expected
- configuration differs
- manual edits exist
- mutable tag points to new digest

Unexplained drift should become actionable work.

---

# 61. Configuration Release

Configuration changes are releases when they affect production behavior.

Track material changes to:

- environment
- proxy
- feature flags
- Docker Compose
- runtime limits
- routing

---

# 62. Secrets and Releases

Never put secret values in release metadata.

Record secret *version/reference* only if safe and useful.

---

# 63. Release Permissions

Agent permissions should follow least privilege.

Possible separation:

- code agent creates change
- GitHub Manager validates repository/release state
- DevOps/SRE coordinates deployment
- VPS/Docker Manager verifies runtime
- Analytics verifies telemetry
- Commerce verifies transactions when affected

Do not require artificial handoffs for every trivial release.

---

# 64. Autonomous Release

Claude may autonomously release only when:

- action is within `AUTONOMY.md`
- tests satisfy `TESTING.md`
- security requirements satisfied
- rollback understood
- target verified
- observability exists to confirm outcome

Autonomy without verification is not permitted.

---

# 65. Release Failure Budget

As data accumulates, track:

- deployment frequency
- deployment success
- change failure rate
- rollback rate
- recovery time

Use this evidence to tune release speed and controls.

---

# 66. Release Velocity

High release frequency is useful only when changes remain safe and measurable.

Do not optimize for commit/deploy count.

Optimize for:

**validated customer/business improvement per unit of risk and effort.**

---

# 67. Release Size

Prefer small coherent releases.

Benefits:

- easier testing
- easier diagnosis
- easier rollback
- clearer experiment attribution

Avoid combining unrelated major changes.

---

# 68. Release Cadence

Claude may deploy continuously when:

- gates pass
- risk is acceptable
- production can be observed
- rollback is available

Do not invent artificial weekly releases if safe continuous delivery is possible.

---

# 69. Release Freeze

A temporary freeze may be appropriate during:

- active severe incident
- data recovery
- major migration
- known unstable infrastructure

Freeze should have a clear reason and exit condition.

---

# 70. Current Production Release

Maintain this section automatically once architecture is verified.

```yaml
production_domain: 6S-success.com
current_release_id: UNKNOWN
commit_sha: UNKNOWN
git_tag: UNKNOWN
image_tag: UNKNOWN
image_digest: UNKNOWN
deployed_at: UNKNOWN
deployment_status: UNKNOWN
smoke_test_status: UNKNOWN
business_verification: UNKNOWN
previous_known_good_release: UNKNOWN
```

Never guess.

---

# 71. Release History

Prefer an automated machine-readable history rather than manually maintaining a huge Markdown table.

This file defines policy.

The actual release system should store operational history.

---

# 72. Executive Dashboard Release Panel

Display:

- production status
- current release
- commit short SHA
- deployed time
- deployment result
- verification result
- previous known-good release
- active feature flags
- active experiment
- rollback availability
- last failed release

---

# 73. Release Freshness

The dashboard should show when production identity was last verified.

Example:

```yaml
current_release: rel-2026-08-14-001
verified_at: 2026-08-14T22:15:00Z
confidence: VERIFIED
```

---

# 74. Release Confidence

Use:

- `VERIFIED`
- `PARTIAL`
- `STALE`
- `UNKNOWN`

Do not display production lineage as verified if only inferred from a tag.

---

# 75. Release Metrics

Useful metrics:

- deployment frequency
- successful deployment %
- change failure rate
- rollback rate
- median deploy duration
- median verification duration
- MTTR
- release-to-measured-outcome time

---

# 76. Release-to-Outcome

For growth/product releases, connect release to expected metric.

Example:

```yaml
release_id: rel-...
expected_outcome:
  metric: quest_completion_rate
  direction: increase
measurement_window: 14d
```

This does not prove causality unless experimental design supports it.

---

# 77. Release Learnings

If a release produces durable insight, update `LEARNINGS.md`.

Example:

> Breaking content, quest logic, and checkout into separate releases reduced diagnosis time and experiment ambiguity.

---

# 78. Release Decisions

Architecture decisions about deployment strategy belong in `DECISIONS.md`.

Examples:

- immutable image tags
- promotion strategy
- feature-flag platform
- migration strategy

---

# 79. Release Backlog

Release-system weaknesses belong in `BACKLOG.md`.

Examples:

- production digest not visible
- no automated rollback
- no smoke test
- manual VPS drift
- no deployment lock
- no migration tracking

---

# 80. Release Incident Link

If release causes incident:

```yaml
release_id:
incident_id:
detected_at:
rollback_or_fix:
restored_at:
```

This helps identify systemic change risk.

---

# 81. First Release-System Mission

Once Claude has legitimate repository and infrastructure access:

1. discover repository
2. discover production branch
3. discover CI
4. discover deployment mechanism
5. discover Docker build
6. identify running production image
7. identify digest
8. map running artifact to Git commit
9. identify previous known-good artifact
10. inspect migration mechanism
11. inspect feature flags
12. inspect release records
13. identify drift
14. update Current Production Release
15. create prioritized release-system backlog

Do not modify production merely to complete discovery.

---

# 82. Minimum Viable Release System

Before aggressive autonomous development, establish:

1. known Git source
2. repeatable build
3. unique artifact identity
4. known production artifact
5. CI quality gates
6. repeatable deployment
7. production smoke test
8. rollback target
9. release record
10. observability

---

# 83. Release Maturity Model

## Level 0: Unknown

Production identity cannot be reliably established.

## Level 1: Traceable

Production maps to known source.

## Level 2: Repeatable

Build/deploy procedures are reproducible.

## Level 3: Verified

Automated gates and smoke tests prove release health.

## Level 4: Recoverable

Rollback/recovery is tested.

## Level 5: Continuously Improving

Release evidence automatically tunes quality gates, detects drift, reduces failure rate, and connects changes to customer/business outcomes.

---

# 84. Definition of Release Done

A material release is done when:

- correct source committed
- CI passed
- artifact built
- immutable identity recorded
- production deployed
- running artifact verified
- smoke tests passed
- affected business path verified
- telemetry healthy
- rollback known
- release record complete
- experiment/metric annotation added where applicable

---

# 85. Non-Negotiable Release Rules

Claude and subagents must not:

- claim a release is healthy without verification
- rely only on `latest` for production identity
- overwrite unknown VPS changes without inspection
- deploy from an unexplained dirty working tree
- run irreversible migration without recovery consideration
- bypass failing critical tests casually
- deploy unreviewed secret values
- leave emergency production fixes outside source control
- run overlapping uncontrolled deployments
- confuse deployment success with customer success

---

# 86. Project-Specific Release State

Populate from verified evidence:

```yaml
github:
  repository: UNKNOWN
  default_branch: UNKNOWN
  production_branch: UNKNOWN
  protected_branch: UNKNOWN
  release_tags: UNKNOWN

ci:
  provider: UNKNOWN
  build_workflow: UNKNOWN
  test_gates: UNKNOWN
  deployment_workflow: UNKNOWN

docker:
  dockerfile: UNKNOWN
  compose_file: UNKNOWN
  image_repository: UNKNOWN
  tag_strategy: UNKNOWN
  digest_tracking: UNKNOWN

production:
  domain: 6S-success.com
  current_release: UNKNOWN
  current_commit: UNKNOWN
  current_image_digest: UNKNOWN
  previous_known_good: UNKNOWN

database:
  engine: UNKNOWN
  migration_system: UNKNOWN
  migration_compatibility_strategy: UNKNOWN

feature_flags:
  mechanism: UNKNOWN
  active_flags: UNKNOWN

rollback:
  mechanism: UNKNOWN
  tested: UNKNOWN

release_records:
  location: UNKNOWN
  dashboard_integration: UNKNOWN
```

---

# 87. Final Principle

The goal is not merely continuous deployment.

The goal is **continuous, traceable, testable, recoverable improvement**.

For every meaningful production change, Claude should know:

**What changed?**

**Why did it change?**

**Which commit contains it?**

**Which artifact was built?**

**Which exact artifact is running?**

**Did the customer experience still work?**

**Did the business metric behave as expected?**

**Can we safely undo it?**

When those questions can be answered automatically, Claude Code can operate 6S-success.com with much greater autonomy while preserving control.

That is the purpose of `RELEASES.md`.
