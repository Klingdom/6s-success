# 6S Success Autonomy Memory Architecture

> Canonical memory and context-management standard for deciding what the
> autonomous 6S Success organization remembers, where it lives, how it
> is retrieved, how conflicts are resolved, how stale knowledge expires,
> and how Claude and specialist agents receive the smallest reliable
> context needed to act correctly.

## 1. Purpose

`AUTONOMY-MEMORY-ARCHITECTURE.md` defines the memory architecture for
Claude Code and the 6S Success autonomous organization.

Its purpose is to prevent two opposite failures:

``` text
FORGETFUL SYSTEM
→ repeats work
→ loses owner intent
→ repeats failures
→ cannot build on learning

CONTEXT-SATURATED SYSTEM
→ loads everything
→ wastes tokens
→ mixes stale/current rules
→ follows irrelevant instructions
→ becomes slower and less reliable
```

The target is:

``` text
OBSERVE
   ↓
CLASSIFY INFORMATION
   ↓
DECIDE WHETHER IT DESERVES MEMORY
   ↓
STORE IN CORRECT LAYER
   ↓
VERSION / SCOPE / EXPIRATION
   ↓
RETRIEVE ONLY WHEN RELEVANT
   ↓
ASSEMBLE TASK CONTEXT
   ↓
ACT
   ↓
VERIFY
   ↓
UPDATE / SUPERSEDE / FORGET
```

------------------------------------------------------------------------

## 2. Core Principle

**Remember durable truth, retrieve relevant context, and never confuse
old information with current authority.**

More memory is not automatically better.

The best context is the smallest set of current, authoritative,
task-relevant information that allows the agent to make the correct
decision.

------------------------------------------------------------------------

## 3. Relationship to Other Standards

This file works directly with:

-   `AUTONOMY-LEARNING-ENGINE.md`
-   `AUTONOMY-DECISION-ENGINE.md`
-   `AUTONOMY-OPPORTUNITY-ENGINE.md`
-   `AUTONOMY-ORCHESTRATION.md`
-   `AUTONOMY-SCHEDULER.md`
-   `AUTONOMY-API.md`
-   owner command center
-   mission control
-   executive dashboard
-   agent registry
-   data model
-   event system
-   security/privacy
-   GitHub Manager
-   Hostinger VPS/Docker Manager
-   DevOps/SRE
-   analytics
-   room/micro-zone system
-   quest/card system

If equivalent repository standards already exist, integrate rather than
duplicate them.

------------------------------------------------------------------------

## 4. Memory Is Not One Thing

The system should distinguish at least:

``` text
AUTHORITATIVE INSTRUCTIONS
OWNER DIRECTIVES
CURRENT OPERATIONAL STATE
WORKING MEMORY
PROJECT KNOWLEDGE
VALIDATED LEARNINGS
PATTERN LIBRARY
DECISION HISTORY
EXPERIMENT HISTORY
INCIDENT HISTORY
AGENT PERFORMANCE
CUSTOMER/PRODUCT AGGREGATES
ARCHIVAL HISTORY
```

These have different authority, retention, retrieval, and update rules.

------------------------------------------------------------------------

## 5. Memory Layers

Recommended conceptual layers:

``` text
L0  IMMUTABLE / PROTECTED GOVERNANCE
L1  ACTIVE OWNER DIRECTIVES
L2  CANONICAL CURRENT STANDARDS
L3  CURRENT SYSTEM / MISSION STATE
L4  VALIDATED ORGANIZATIONAL KNOWLEDGE
L5  TASK / SESSION WORKING MEMORY
L6  HISTORICAL EVIDENCE / ARCHIVE
```

------------------------------------------------------------------------

## 6. L0 Protected Governance

Contains high-authority controls such as:

-   security rules
-   privacy rules
-   authorization boundaries
-   protected owner policies
-   non-negotiable operating constraints

This layer must not be silently rewritten by autonomous learning.

------------------------------------------------------------------------

## 7. L1 Active Owner Directives

Contains current owner intent such as:

``` text
Validate Entryway before expanding Kitchen.
Do not exceed authorized spend.
Prioritize customer outcome over raw engagement.
```

Directives require:

``` yaml
directive:
  id:
  statement:
  status:
  effective_at:
  expires_at:
  supersedes:
  scope:
  source:
```

------------------------------------------------------------------------

## 8. L2 Canonical Current Standards

Contains the currently approved operating system:

-   autonomy standards
-   agent responsibilities
-   API contracts
-   deployment procedures
-   decision rules
-   measurement definitions
-   room/micro-zone taxonomy
-   quest/card standards

The repository should have one canonical current version of each
standard.

------------------------------------------------------------------------

## 9. L3 Current State

Contains changing operational truth:

-   current primary constraint
-   active mission
-   task states
-   production version
-   current incidents
-   deployment state
-   budget state
-   experiment state
-   active blockers

This should generally come from systems of record, not stale prose.

------------------------------------------------------------------------

## 10. L4 Validated Organizational Knowledge

Contains evidence-backed learning:

-   validated customer behavior
-   reusable 6S patterns
-   room/micro-zone patterns
-   card duration learnings
-   quest sequencing
-   technical recovery patterns
-   agent routing patterns
-   decision calibration

This layer is governed by `AUTONOMY-LEARNING-ENGINE.md`.

------------------------------------------------------------------------

## 11. L5 Working Memory

Temporary context needed for the current mission/task.

Examples:

-   current plan
-   intermediate findings
-   temporary hypotheses
-   unresolved questions
-   task-local file references

Working memory should not automatically become durable knowledge.

------------------------------------------------------------------------

## 12. L6 Historical Evidence

Contains durable history needed for traceability:

-   old decisions
-   experiments
-   incidents
-   superseded standards
-   rejected opportunities
-   retired cards
-   historical releases

Archive does not equal active instruction.

------------------------------------------------------------------------

## 13. Authority Precedence

When memory conflicts:

``` text
Protected Governance
      ↓
Active Owner Directive
      ↓
Canonical Current Standard
      ↓
Verified Current System State
      ↓
Validated Learning
      ↓
Supported Learning
      ↓
Working Hypothesis
      ↓
Historical / Raw Observation
```

Higher-authority current information wins.

------------------------------------------------------------------------

## 14. Recency Is Not Authority

A new low-confidence observation does not override an approved standard
merely because it is newer.

Likewise, an old owner directive may no longer apply if explicitly
superseded.

Use both authority and validity.

------------------------------------------------------------------------

## 15. Memory Record

Conceptual:

``` yaml
memory:
  id:
  type:
  layer:
  title:
  content_ref:
  source_ref:
  scope:
  authority:
  confidence:
  status:
  created_at:
  effective_at:
  last_validated_at:
  review_at:
  expires_at:
  supersedes:
  superseded_by:
  tags:
```

------------------------------------------------------------------------

## 16. Memory Status

Use:

``` text
ACTIVE
CANDIDATE
CONTESTED
STALE
SUPERSEDED
EXPIRED
ARCHIVED
DELETED
```

------------------------------------------------------------------------

## 17. Scope

Every durable memory should have scope where relevant.

Examples:

``` text
GLOBAL
PRODUCT
ROOM
MICRO_ZONE
DESIRED_FUNCTION
ROOT_CAUSE
6S_DIMENSION
QUEST
CARD
AGENT
REPOSITORY
SERVICE
INFRASTRUCTURE
CUSTOMER_SEGMENT
```

------------------------------------------------------------------------

## 18. What Deserves Durable Memory

Store when information is:

-   repeatedly useful
-   authoritative
-   expensive to rediscover
-   necessary for traceability
-   validated learning
-   required for consistent decisions
-   a durable owner preference/directive
-   a reusable pattern
-   an important failure mode

------------------------------------------------------------------------

## 19. What Should Usually Not Become Durable Memory

Avoid storing:

-   transient debugging output
-   temporary speculation
-   one-off reasoning
-   redundant summaries
-   raw tool chatter
-   every customer comment
-   every generated idea
-   copied external content
-   secrets
-   unnecessary personal data
-   hidden chain-of-thought

------------------------------------------------------------------------

## 20. Memory Admission Test

Before persisting ask:

``` text
Will this likely matter again?
Is it sufficiently trustworthy?
What is its scope?
What is its authority?
Where should it live?
How will it become stale?
Is it already stored?
```

------------------------------------------------------------------------

## 21. Evidence vs Memory

Evidence supports memory.

Do not replace evidence with prose.

Prefer:

``` text
learning record
→ evidence references
```

rather than copying large source payloads into multiple MD files.

------------------------------------------------------------------------

## 22. Repository MD Files

Markdown files are appropriate for:

-   durable standards
-   human-readable policies
-   agent contracts
-   architectural principles
-   operating procedures
-   canonical playbooks

Markdown is not the ideal primary store for rapidly changing telemetry,
task state, event logs, or high-volume customer behavior.

------------------------------------------------------------------------

## 23. Structured Data

Use database/structured storage for:

-   missions
-   tasks
-   events
-   metrics
-   opportunities
-   decisions
-   learnings
-   experiments
-   agent evaluations
-   customer outcome aggregates

MD files may document the schema and rules.

------------------------------------------------------------------------

## 24. Systems of Record

For each data class define one source of truth.

Example:

``` text
Git state → Git/GitHub
Production runtime → monitoring/VPS/Docker
Business metrics → analytics/database
Owner directives → directive store
Standards → canonical repository files
Learning records → learning store
```

Do not copy mutable state into multiple files and expect them to stay
synchronized.

------------------------------------------------------------------------

## 25. Memory Index

Maintain a machine-readable index of canonical knowledge.

Conceptual:

``` yaml
memory_index:
  standards:
  directives:
  patterns:
  learnings:
  decisions:
  experiments:
  incidents:
  agents:
  domains:
```

The index points to sources rather than duplicating their contents.

------------------------------------------------------------------------

## 26. Context Manifest

Every significant agent task should be able to receive a context
manifest.

``` yaml
context_manifest:
  task_id:
  agent_id:
  objective:
  directive_refs:
  standard_refs:
  current_state_refs:
  learning_refs:
  evidence_refs:
  exclusions:
  generated_at:
```

------------------------------------------------------------------------

## 27. Context Assembly

Use:

``` text
TASK
 ↓
IDENTIFY DOMAIN
 ↓
IDENTIFY AUTHORITY
 ↓
LOAD CURRENT STATE
 ↓
RETRIEVE RELEVANT VALIDATED KNOWLEDGE
 ↓
ADD NECESSARY EVIDENCE
 ↓
REMOVE DUPLICATION / STALE CONTEXT
 ↓
EXECUTE
```

------------------------------------------------------------------------

## 28. Minimum Necessary Context

Do not load all 30+ autonomy files into every subagent invocation.

Instead load:

1.  universal required governance;
2.  relevant owner directives;
3.  the agent's own contract;
4.  task-specific standards;
5.  current state;
6.  relevant learnings/evidence.

------------------------------------------------------------------------

## 29. Progressive Retrieval

Prefer staged retrieval:

``` text
Tier 1:
small mandatory context

Tier 2:
task-relevant references

Tier 3:
deeper evidence only when needed
```

This reduces context-window waste.

------------------------------------------------------------------------

## 30. Retrieval Query

A retrieval request should include:

-   task objective
-   domain
-   named entities/components
-   room/micro-zone if applicable
-   desired function
-   root cause
-   agent
-   recency requirement
-   authority requirement

------------------------------------------------------------------------

## 31. Retrieval Ranking

Rank memory using factors such as:

``` text
authority
task relevance
scope match
recency
confidence
validation status
source quality
```

------------------------------------------------------------------------

## 32. Retrieval Exclusions

Exclude by default:

-   superseded standards
-   expired directives
-   rejected learnings
-   unrelated room content
-   archived incident details
-   low-confidence observations

unless explicitly needed for history/comparison.

------------------------------------------------------------------------

## 33. Context Budget

Each agent should have a configurable context budget.

Prioritize:

``` text
1. authority
2. task objective
3. current state
4. directly relevant standards
5. validated learning
6. evidence
7. optional background
```

------------------------------------------------------------------------

## 34. Context Compression

When source material is too large, create a traceable summary with:

-   source refs
-   scope
-   key facts
-   unresolved uncertainty
-   last-updated timestamp

Do not remove material constraints during compression.

------------------------------------------------------------------------

## 35. No Hidden Summary Drift

Compressed memory should not gradually replace authoritative originals.

Periodically regenerate summaries from canonical sources.

------------------------------------------------------------------------

## 36. Agent-Specific Memory

Agents may maintain domain-specific operational knowledge, but it must
remain subordinate to canonical standards.

Examples:

``` text
GitHub Manager → repository/release patterns
VPS Manager → deployment/recovery patterns
SEO Agent → search/content patterns
Quest Agent → card/quest patterns
```

------------------------------------------------------------------------

## 37. Shared vs Private Agent Memory

Default to shared organizational learning when it benefits multiple
agents.

Use agent-local memory only when the information is truly role-specific.

Avoid knowledge silos.

------------------------------------------------------------------------

## 38. Cross-Agent Handoff Memory

A handoff should include:

``` yaml
handoff:
  from_agent:
  to_agent:
  mission_id:
  task_id:
  completed:
  evidence_refs:
  decisions:
  unresolved:
  next_action:
```

Do not require the receiving agent to reconstruct the entire
conversation.

------------------------------------------------------------------------

## 39. Mission Memory

Each mission should preserve:

-   objective
-   baseline
-   selected opportunity
-   decisions
-   tasks
-   evidence
-   changes
-   outcomes
-   learnings
-   owner interventions

------------------------------------------------------------------------

## 40. Mission Closure

At closure, convert temporary working memory into:

``` text
durable evidence
decision history
validated learning candidates
archive
```

Then discard unnecessary temporary context.

------------------------------------------------------------------------

## 41. Opportunity Memory

Store canonical opportunity state in the opportunity system.

Do not preserve every duplicate idea as active memory.

------------------------------------------------------------------------

## 42. Decision Memory

Store decision rationale summaries and evidence references.

Do not store hidden chain-of-thought.

------------------------------------------------------------------------

## 43. Experiment Memory

Preserve:

-   hypothesis
-   design
-   exposure
-   metrics
-   result
-   decision
-   learning

Negative and inconclusive experiments matter.

------------------------------------------------------------------------

## 44. Incident Memory

Preserve enough history to prevent recurrence:

-   failure mode
-   impact
-   detection
-   recovery
-   root cause
-   countermeasure
-   verification

------------------------------------------------------------------------

## 45. Customer Memory

Only retain customer-specific information necessary for the product and
allowed by policy.

Do not create broad personal profiles from household images.

Prefer product-relevant state and aggregate learning.

------------------------------------------------------------------------

## 46. Micro-Zone Memory

Useful structured state may include:

``` text
room
micro-zone
desired function
current-state observations
selected root cause
selected quest
completed cards
verified outcome
sustain check
```

Retention should follow privacy/product requirements.

------------------------------------------------------------------------

## 47. Image Memory

Raw household images may be sensitive.

Use:

-   least necessary retention
-   controlled access
-   derived structured observations where sufficient
-   explicit deletion/retention policy

Do not propagate raw images into unrelated agent context.

------------------------------------------------------------------------

## 48. Product Recommendation Memory

Remember diagnosed need and outcome, not merely that a product was
clicked.

This helps the system learn when no purchase is necessary.

------------------------------------------------------------------------

## 49. Owner Memory

Durable owner context should focus on:

-   active directives
-   strategic priorities
-   explicit constraints
-   approval boundaries
-   stable preferences relevant to operations

Avoid storing irrelevant personal details.

------------------------------------------------------------------------

## 50. Directive Lifecycle

Use:

``` text
PROPOSED
ACTIVE
SUPERSEDED
EXPIRED
REVOKED
```

An expired directive must not silently remain active because it appears
in an old MD file.

------------------------------------------------------------------------

## 51. Standard Lifecycle

Use:

``` text
DRAFT
ACTIVE
DEPRECATED
SUPERSEDED
ARCHIVED
```

Only active canonical standards should load by default.

------------------------------------------------------------------------

## 52. Canonical File Registry

Maintain a registry:

``` yaml
standards:
  autonomy_orchestration:
    path:
    version:
    status: ACTIVE
  autonomy_opportunity_engine:
    path:
    version:
    status: ACTIVE
  autonomy_decision_engine:
    path:
    version:
    status: ACTIVE
  autonomy_learning_engine:
    path:
    version:
    status: ACTIVE
  autonomy_memory_architecture:
    path:
    version:
    status: ACTIVE
```

------------------------------------------------------------------------

## 53. File Naming

Use stable, descriptive canonical names.

Avoid:

``` text
FINAL.md
FINAL2.md
LATEST.md
LATEST-REAL.md
```

Prefer explicit version history in Git.

------------------------------------------------------------------------

## 54. Git as Memory

Git provides:

-   history
-   authorship
-   diff
-   rollback
-   versioning

Use Git history rather than keeping multiple ambiguous copies of
standards.

------------------------------------------------------------------------

## 55. GitHub Issues as Memory

Issues may hold actionable work, but should not become the only store of
canonical architecture or validated learning.

Reference canonical records.

------------------------------------------------------------------------

## 56. Commit Messages

Material standards changes should explain:

``` text
what changed
why
evidence/decision reference
```

------------------------------------------------------------------------

## 57. Semantic Retrieval

Semantic search can help retrieve relevant knowledge, but it does not
determine authority.

A semantically similar deprecated file must not outrank an active
canonical standard.

------------------------------------------------------------------------

## 58. Keyword Retrieval

Use exact identifiers where available:

-   mission ID
-   opportunity ID
-   decision ID
-   room ID
-   micro-zone ID
-   card ID
-   agent ID
-   repository component

Combine semantic and structured retrieval.

------------------------------------------------------------------------

## 59. Retrieval Verification

Before acting on retrieved memory verify:

``` text
Is it current?
Is it active?
Is it authoritative?
Does its scope match?
Has it been superseded?
```

------------------------------------------------------------------------

## 60. Memory Conflict

When two active-looking records conflict:

1.  stop silent resolution;
2.  compare authority;
3.  compare effective dates;
4.  inspect supersession;
5.  verify source of truth;
6.  mark conflict;
7.  escalate only if necessary.

------------------------------------------------------------------------

## 61. Conflict Record

``` yaml
memory_conflict:
  id:
  record_a:
  record_b:
  conflict_type:
  detected_at:
  resolution:
  resolved_by:
```

------------------------------------------------------------------------

## 62. Stale Memory Detection

Potential triggers:

-   review date passed
-   source changed
-   canonical file superseded
-   metric definition changed
-   UI/product changed
-   infrastructure changed
-   contradictory evidence

------------------------------------------------------------------------

## 63. Memory Expiration

Not all memory should live forever.

Possible retention classes:

``` text
EPHEMERAL
SHORT_TERM
PROJECT_LIFETIME
LONG_TERM
ARCHIVAL
POLICY_DEFINED
```

------------------------------------------------------------------------

## 64. Forgetting Is a Feature

Delete or archive information that is:

-   redundant
-   obsolete
-   unsupported
-   privacy-sensitive beyond need
-   superseded
-   low-value noise

Controlled forgetting improves autonomy.

------------------------------------------------------------------------

## 65. Tombstones

When deletion history matters, retain a minimal tombstone:

``` yaml
deleted_record:
  id:
  deleted_at:
  reason:
  replacement_ref:
```

Do not retain deleted sensitive content inside the tombstone.

------------------------------------------------------------------------

## 66. Secrets

Never store secrets in general memory, Markdown standards, prompts,
logs, or learning records.

Use approved secret-management mechanisms.

------------------------------------------------------------------------

## 67. Credentials

Agents should receive credentials only through authorized runtime
mechanisms and only when required.

Do not persist credentials into context manifests.

------------------------------------------------------------------------

## 68. PII and Sensitive Data

Minimize collection, access, propagation, and retention.

Memory architecture must follow privacy/security policy.

------------------------------------------------------------------------

## 69. Logs

Logs are evidence, not general agent memory.

Retrieve only relevant slices.

Avoid sending full production logs into every debugging task.

------------------------------------------------------------------------

## 70. Telemetry

Aggregate telemetry before LLM analysis when possible.

``` text
raw events
→ deterministic aggregation
→ anomaly/pattern
→ agent analysis
```

------------------------------------------------------------------------

## 71. Executive Dashboard Memory

The dashboard should query current systems of record.

Do not generate "near real time" executive state from cached prose.

------------------------------------------------------------------------

## 72. Executive Context

For owner-facing summaries, combine:

``` text
current primary constraint
active mission
top opportunity
pending decision
verified KPI state
major risk
recent validated learning
```

------------------------------------------------------------------------

## 73. Near Real-Time State

Near real-time information belongs in:

-   database
-   telemetry
-   APIs
-   event streams
-   monitoring

MD files define how that state is interpreted.

------------------------------------------------------------------------

## 74. Context Freshness

Every generated context package should include:

``` text
generated_at
source timestamps
known stale sources
```

------------------------------------------------------------------------

## 75. Cache

Caching may reduce cost, but cached context must have:

-   TTL
-   invalidation rules
-   source version
-   scope

------------------------------------------------------------------------

## 76. Cache Invalidation

Invalidate when:

-   owner directive changes
-   standard changes
-   mission changes
-   deployment changes
-   metric definition changes
-   incident begins/ends
-   relevant learning is superseded

------------------------------------------------------------------------

## 77. Memory Event Model

Recommended events:

``` text
memory.created
memory.updated
memory.superseded
memory.expired
memory.archived
memory.deleted
memory.conflict_detected
memory.conflict_resolved
context.generated
context.invalidated
```

------------------------------------------------------------------------

## 78. Memory API

Align with `AUTONOMY-API.md`.

Potential:

``` text
GET  /api/v1/memory
GET  /api/v1/memory/{id}
POST /api/v1/memory
POST /api/v1/memory/{id}/supersede
POST /api/v1/memory/{id}/archive
DELETE /api/v1/memory/{id}
GET  /api/v1/context
POST /api/v1/context/assemble
GET  /api/v1/standards
GET  /api/v1/directives
```

------------------------------------------------------------------------

## 79. Memory Search

Support filters:

``` text
type
layer
scope
status
authority
confidence
created_at
effective_at
tags
source
```

------------------------------------------------------------------------

## 80. Context Service

A dedicated context service/function may:

1.  receive task metadata;
2.  identify required standards;
3.  retrieve active directives;
4.  retrieve current state;
5.  retrieve relevant learnings;
6.  validate freshness;
7.  rank;
8.  compress;
9.  return context manifest.

------------------------------------------------------------------------

## 81. Agent Startup

An agent should not start by recursively reading the entire repository.

Start with:

``` text
agent contract
task
mandatory governance
context manifest
```

Retrieve more only when needed.

------------------------------------------------------------------------

## 82. CLAUDE.md Strategy

The root `CLAUDE.md` should remain a high-value router, not become a
giant encyclopedia.

It should identify:

-   mission of the system
-   non-negotiables
-   canonical file registry/index
-   context-loading rules
-   how to discover task-specific standards
-   owner/approval boundaries

------------------------------------------------------------------------

## 83. Subdirectory CLAUDE.md

Use scoped `CLAUDE.md` files only where they reduce ambiguity for a
specific code/domain area.

Avoid duplicating global rules.

------------------------------------------------------------------------

## 84. Agent MD Strategy

Each subagent file should define:

-   role
-   responsibilities
-   tools
-   authority
-   inputs
-   outputs
-   required standards
-   escalation
-   verification

It should not copy the entire autonomy operating system.

------------------------------------------------------------------------

## 85. Non-Agent MD Strategy

Non-agent files define shared systems and standards.

Agents reference them rather than duplicating them.

------------------------------------------------------------------------

## 86. MD Dependency Graph

Maintain a dependency map.

Example:

``` text
CLAUDE.md
 ├─ governance
 ├─ orchestration
 │   ├─ opportunity engine
 │   ├─ decision engine
 │   ├─ learning engine
 │   └─ memory architecture
 ├─ agent registry
 ├─ scheduler
 ├─ API
 └─ observability
```

------------------------------------------------------------------------

## 87. Circular Dependency Prevention

Documentation may cross-reference, but avoid circular instruction chains
where no file is clearly authoritative.

------------------------------------------------------------------------

## 88. Canonical Definition Rule

Every major concept should have one canonical definition.

Examples:

``` text
Primary Constraint → one canonical standard
Mission → one canonical data model
Opportunity Score → one canonical definition
Customer Outcome → one canonical metric definition
```

Other files reference it.

------------------------------------------------------------------------

## 89. Duplicate Detection

Periodically scan MD files for:

-   duplicate rules
-   conflicting thresholds
-   outdated agent names
-   old file paths
-   duplicate metric definitions
-   contradictory authority statements

------------------------------------------------------------------------

## 90. Documentation Linting

Automate checks where practical:

``` text
broken references
missing canonical files
duplicate headings/IDs
deprecated references
invalid schema examples
unregistered agent names
```

------------------------------------------------------------------------

## 91. Memory Health Metrics

Track:

``` text
retrieval_precision
stale_context_rate
memory_conflict_rate
duplicate_memory_rate
context_size
context_cost
context_cache_hit_rate
superseded_memory_loaded_rate
missing_required_context_rate
```

------------------------------------------------------------------------

## 92. Context Quality Metrics

Evaluate whether agents had:

-   correct directive
-   correct standard
-   correct current state
-   relevant learning
-   unnecessary context
-   stale context

------------------------------------------------------------------------

## 93. Retrieval Evaluation

Create benchmark tasks and verify that context retrieval returns the
correct authoritative records.

------------------------------------------------------------------------

## 94. Memory Cost

Track:

-   storage
-   indexing
-   embedding/search
-   model tokens
-   context assembly latency

Optimize for reliable decisions, not maximum retrieval.

------------------------------------------------------------------------

## 95. Memory Security

Enforce least privilege.

An SEO agent generally does not need raw customer household images.

A quest agent generally does not need deployment secrets.

A GitHub agent generally does not need unrelated customer records.

------------------------------------------------------------------------

## 96. Memory Access Policy

Conceptual:

``` yaml
access:
  agent_id:
  allowed_memory_types:
  allowed_scopes:
  prohibited_types:
```

------------------------------------------------------------------------

## 97. Auditability

Material memory changes should be traceable:

``` text
who/what changed it
when
why
source evidence
previous version
```

------------------------------------------------------------------------

## 98. Learning Engine Integration

The Learning Engine proposes validated organizational knowledge.

The Memory Architecture determines where and how that knowledge is
stored and retrieved.

------------------------------------------------------------------------

## 99. Decision Engine Integration

The Decision Engine receives authoritative current context.

Decision outcomes become historical and learning memory after
verification.

------------------------------------------------------------------------

## 100. Opportunity Engine Integration

Opportunity detection should retrieve prior related opportunities,
decisions, experiments, and learnings to prevent duplicate discovery.

------------------------------------------------------------------------

## 101. Orchestrator Integration

The Orchestrator should receive a mission-level context package, not the
entire knowledge base.

------------------------------------------------------------------------

## 102. Scheduler Integration

Scheduled tasks must refresh current state rather than blindly reuse old
context.

------------------------------------------------------------------------

## 103. GitHub Manager Integration

GitHub Manager should retrieve:

-   repository standards
-   branch/release rules
-   current repository state
-   relevant prior deployment/code learnings

not unrelated business/customer memory.

------------------------------------------------------------------------

## 104. VPS/Docker Manager Integration

VPS/Docker Manager should retrieve:

-   infrastructure standards
-   current runtime state
-   deployment target
-   recent relevant incidents
-   recovery patterns

Secrets remain outside general memory.

------------------------------------------------------------------------

## 105. Quest Agent Integration

Quest Agent should retrieve:

-   room/micro-zone
-   desired function
-   root cause
-   applicable 6S patterns
-   validated card/quest learnings
-   current time/player constraints

------------------------------------------------------------------------

## 106. SEO/AEO Agent Integration

Retrieve:

-   current strategy/directives
-   canonical product positioning
-   relevant content/search learnings
-   current metrics

Do not load raw household data.

------------------------------------------------------------------------

## 107. Product Agent Integration

Retrieve diagnosed need, applicable product standards, prior product
outcome learning, and commercial constraints.

Do not infer that a remembered purchase implies a permanent need.

------------------------------------------------------------------------

## 108. Memory and Personalization

Personalization should be based on current, relevant, permitted
information.

Allow users to change preferences and invalidate old assumptions.

------------------------------------------------------------------------

## 109. Memory and 6S

The memory architecture itself should follow 6S:

``` text
SORT
Remove irrelevant/redundant memory.

SET IN ORDER
Place information in the correct layer/source.

SHINE
Clean stale/conflicting records.

STANDARDIZE
Use canonical schemas, names, and precedence.

SUSTAIN
Run recurring memory-health checks.

SAFETY
Protect private, sensitive, and privileged data.
```

------------------------------------------------------------------------

## 110. Memory Kaizen

Memory defects should enter the Opportunity Engine.

Examples:

-   agents repeatedly miss owner directives
-   context packages are too large
-   stale standards are loaded
-   duplicate learnings proliferate
-   retrieval misses relevant incidents

------------------------------------------------------------------------

## 111. Bootstrap Discovery

Before implementation inspect:

1.  root `CLAUDE.md`;
2.  all agent MD files;
3.  all non-agent autonomy MD files;
4.  current documentation hierarchy;
5.  database/schema;
6.  existing memory/knowledge systems;
7.  vector/semantic search if present;
8.  event system;
9.  mission/task store;
10. owner directive store;
11. learning/experiment records;
12. GitHub issues/projects;
13. observability/telemetry;
14. security/privacy policies;
15. current context-loading behavior.

------------------------------------------------------------------------

## 112. Inventory Existing MD Files

Create a machine-readable inventory:

``` text
path
purpose
owner/domain
status
authority
dependencies
last meaningful update
canonical/superseded
```

This is especially important as the autonomy library grows.

------------------------------------------------------------------------

## 113. Detect Top-30 Coverage

The documentation inventory should map every recommended autonomy
standard to:

``` text
NOT_STARTED
DRAFT
ACTIVE
SUPERSEDED
```

This makes completion of the planned autonomy architecture objectively
visible.

------------------------------------------------------------------------

## 114. Minimum Viable Memory Architecture

Phase 1:

``` text
canonical file registry
authority precedence
active directive model
memory layers
context manifest
task-specific retrieval
supersession
staleness
basic access controls
```

------------------------------------------------------------------------

## 115. Phase 2

Add:

``` text
semantic + structured retrieval
context service
dependency graph
documentation linting
memory conflict detection
retrieval evaluation
context-cost metrics
```

------------------------------------------------------------------------

## 116. Phase 3

Only with evidence:

``` text
adaptive context budgeting
automated memory consolidation
predictive prefetch
advanced knowledge graphs
automatic standard-review proposals
```

------------------------------------------------------------------------

## 117. First Memory Architecture Mission

``` yaml
mission:
  title: Establish Canonical Memory and Context Architecture
  objective: >
    Implement the smallest reliable memory architecture that separates
    authority, current state, validated learning, working memory, and history,
    while giving each Claude Code agent only the current task-relevant context
    it needs and preventing stale or duplicate documentation from becoming
    active instruction.
  success:
    - canonical MD registry exists
    - active/superseded status is visible
    - authority precedence is implemented
    - owner directives are separately modeled
    - context manifests can be assembled
    - task-specific retrieval works
    - stale/superseded records are excluded by default
    - learning records remain evidence-linked
    - secrets are excluded from general memory
    - agent access is scoped
    - documentation duplication can be detected
    - top-30 autonomy-file coverage is machine-readable
```

------------------------------------------------------------------------

## 118. Initial State

Until verified:

``` yaml
memory_architecture:
  implementation_status: UNKNOWN
  canonical_registry: UNKNOWN
  directive_store: UNKNOWN
  context_service: UNKNOWN
  semantic_retrieval: UNKNOWN
  structured_retrieval: UNKNOWN
  staleness_detection: UNKNOWN
  conflict_detection: UNKNOWN
  access_controls: UNKNOWN
  documentation_inventory: UNKNOWN
```

------------------------------------------------------------------------

## 119. Acceptance Test: Stale Standard

Input:

``` text
Semantic search returns:
AUTONOMY-DEPLOYMENT-v1.md
AUTONOMY-DEPLOYMENT.md

Registry says:
v1 = SUPERSEDED
current = ACTIVE
```

Expected:

``` text
Load current ACTIVE standard.
Use v1 only if historical comparison is explicitly needed.
```

------------------------------------------------------------------------

## 120. Acceptance Test: Owner Directive

Input:

``` text
Old project note:
"Start Kitchen next."

Active owner directive:
"Validate Entryway before Kitchen expansion."
```

Expected:

``` text
Active directive wins.
Old note does not become authority.
```

------------------------------------------------------------------------

## 121. Acceptance Test: Quest Agent

Input:

``` text
Task:
Build a 30-minute Entryway quest for two players focused on misplaced keys.
```

Expected context:

``` text
relevant governance
Quest Agent contract
Entryway/micro-zone model
desired function
root cause
Set-in-Order/Standardize patterns
relevant card learnings
2-player assignment rules
30-minute constraint
```

Not expected:

``` text
full GitHub deployment history
all SEO standards
all VPS incident logs
every room deck
```

------------------------------------------------------------------------

## 122. Acceptance Test: GitHub Manager

Input:

``` text
Prepare release PR.
```

Expected:

``` text
Load GitHub/release standards, repository state, mission change refs,
required checks, and relevant prior release learnings.
Do not load raw customer household images.
```

------------------------------------------------------------------------

## 123. Acceptance Test: New Learning

Input:

``` text
Validated Entryway experiment supports a shorter starter quest.
```

Expected:

``` text
Create scoped validated learning.
Link evidence.
Do not directly rewrite protected global standards.
Propose standard change where appropriate.
```

------------------------------------------------------------------------

## 124. Acceptance Test: Memory Conflict

Input:

``` text
Two ACTIVE files define different production approval thresholds.
```

Expected:

``` text
Detect conflict.
Do not silently pick whichever was retrieved first.
Resolve through authority/source-of-truth process.
```

------------------------------------------------------------------------

## 125. Acceptance Test: Context Saturation

Input:

``` text
Agent task requires 5 relevant standards.
Repository contains 70 autonomy/agent MD files.
```

Expected:

``` text
Load mandatory governance plus the 5 relevant standards and current state.
Do not inject all 70 files.
```

------------------------------------------------------------------------

## 126. Acceptance Test: Sensitive Image

Input:

``` text
Household image used to diagnose an Entryway micro-zone.
SEO agent later requests content context.
```

Expected:

``` text
SEO agent receives aggregate/product-relevant learning if needed.
Raw household image is not propagated.
```

------------------------------------------------------------------------

## 127. Acceptance Test: Deleted Preference

Input:

``` text
A user changes/removes a prior preference.
```

Expected:

``` text
Current preference replaces or invalidates old active memory.
Historical retention follows policy.
Old preference does not continue to drive personalization.
```

------------------------------------------------------------------------

## 128. Acceptance Test: Top-30 Documentation

Input:

``` text
Owner asks whether the recommended top 30 non-agent autonomy files are complete.
```

Expected:

``` text
Read documentation inventory.
Report exact counts/status.
Identify next missing canonical file.
Do not rely on conversational recollection alone.
```

------------------------------------------------------------------------

## 129. Memory Health Questions

The system should be able to answer:

``` text
What are the canonical standards?
Which are active?
Which have been superseded?
What owner directives are active?
What does this agent need to know for this task?
What relevant validated learnings exist?
What is stale?
What conflicts exist?
How much context are agents consuming?
Are agents loading unnecessary information?
Which top-30 autonomy files remain?
```

------------------------------------------------------------------------

## 130. Anti-Patterns

Avoid:

-   one giant CLAUDE.md
-   loading every MD file for every task
-   duplicate canonical standards
-   stale prose as current operational state
-   semantic similarity as authority
-   storing secrets in memory
-   copying raw evidence everywhere
-   permanent memory for temporary hypotheses
-   agent knowledge silos
-   context summaries with no source refs
-   multiple "latest" files
-   treating archive as instruction
-   allowing learning to rewrite governance automatically
-   retaining unnecessary household data
-   forgetting negative experiments and incidents
-   relying on chat history as the system of record

------------------------------------------------------------------------

## 131. Non-Negotiable Rules

Claude and subagents must not:

-   treat all memory as equally authoritative
-   let recency alone determine authority
-   load superseded standards by default
-   treat expired directives as active
-   duplicate mutable state across MD files
-   store credentials or secrets in general memory
-   expose unnecessary private customer information
-   persist hidden chain-of-thought
-   turn working hypotheses into durable truth without validation
-   silently resolve material memory conflicts
-   let agents rewrite protected governance from learned behavior
-   use raw images when aggregate structured observations are sufficient
-   inject the entire documentation library into every task
-   create new memory stores before inspecting existing systems
-   keep obsolete information active merely because deletion is
    inconvenient
-   report top-30 completion from guesswork when an inventory can
    establish it

------------------------------------------------------------------------

## 132. Final Principle

The autonomous system should remember enough to become smarter without
carrying its entire history into every decision.

The target is:

``` text
ONE SOURCE OF TRUTH
       ↓
CLEAR AUTHORITY
       ↓
SCOPED DURABLE MEMORY
       ↓
CURRENT STATE FROM LIVE SYSTEMS
       ↓
RELEVANT RETRIEVAL
       ↓
SMALL CONTEXT MANIFEST
       ↓
BETTER AGENT ACTION
       ↓
VERIFIED OUTCOME
       ↓
CONTROLLED LEARNING
       ↓
CLEANER FUTURE MEMORY
```

For Claude Code, the goal is not to read more files.

The goal is to know **which files, directives, state, evidence, and
learnings matter for the decision in front of it**, while preserving a
complete and auditable organizational memory outside the active context
window.

That is the purpose of `AUTONOMY-MEMORY-ARCHITECTURE.md`.
