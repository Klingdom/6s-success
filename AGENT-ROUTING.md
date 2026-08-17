# 6S Success Agent Routing

> Canonical dispatch, ownership, collaboration, handoff, concurrency, and escalation policy for the 6S Success Claude Code multi-agent operating system.

## 1. Purpose

`AGENT-ROUTING.md` determines which specialist agent should handle a problem, which agent owns the result, when multiple agents should collaborate, when the orchestrator should act directly, and when no agent should be spawned.

The objective is not maximum agent activity.

The objective is:

**the smallest qualified team completing the highest-value authorized work with clear ownership and minimal coordination overhead.**

---

# 2. Core Routing Principle

For every task:

1. identify the problem domain
2. identify the required mode
3. identify risk and authority
4. choose one accountable owner
5. add only necessary supporting agents
6. define handoff evidence
7. prevent conflicting writes
8. return control to the orchestrator

---

# 3. Orchestrator Role

The primary orchestrator owns:

- global priority
- primary constraint
- mission selection
- routing
- task decomposition
- cross-domain coordination
- policy interpretation
- conflict resolution
- owner escalation
- final mission verification

Specialist agents do not independently redefine global strategy.

---

# 4. One Accountable Owner

Every material task must have exactly one `owner_agent`.

Supporting agents may contribute, but accountability remains singular.

```yaml
task:
  task_id:
  owner_agent:
  support_agents: []
```

Never create a task where "everyone" owns the result.

---

# 5. Agent Modes

Explicitly route work as one of:

- `DISCOVER`
- `ANALYZE`
- `RECOMMEND`
- `DESIGN`
- `IMPLEMENT`
- `TEST`
- `REVIEW`
- `DEPLOY`
- `VERIFY`
- `MONITOR`
- `RESPOND`

A request to analyze does not imply authority to deploy.

---

# 6. Agent Classes

The intended architecture may contain the following specialist classes. Use actual configured agent names from `SYSTEM-REGISTRY.md`.

## Orchestrator
Coordinates the system.

## GitHub Manager
Repository governance, branches, PRs, Actions, releases, repository security, lineage.

## Hostinger VPS / Docker Manager
Host, Docker, Compose, containers, volumes, runtime configuration, capacity, ports, runtime drift.

## DevOps / SRE
Reliability, CI/CD architecture, observability, deployments, incidents, SLOs, operational engineering.

## Security
Threats, vulnerabilities, secrets, authentication, authorization, hardening, security incidents.

## Analytics / Measurement
Instrumentation, metrics, funnels, attribution, data quality, baselines, experiment analysis.

## Customer Journey / UX
Desired-function flow, diagnosis, customer friction, onboarding, usability, journey architecture.

## Quest / Game Experience
Cards, quests, micro-zone activities, multiplayer mechanics, assignment, pacing, completion.

## Product / Catalog
Products, kits, digital assets, physical solutions, product mapping, solution fit.

## Commerce
Checkout, payments, orders, refunds, fulfillment, commerce integrations.

## SEO / AEO
Search demand, technical SEO, structured content, answer-engine optimization, discoverability.

## Content
Editorial content, room/micro-zone pages, guides, card content, publishing quality.

## Growth
Constraint analysis, acquisition, conversion, retention, referral, growth experiments.

## Cost / Finance
Cost monitoring, unit economics, margin, spend anomalies, financial guardrails.

Other agents may exist. Register them before relying on them.

---

# 7. Canonical Routing Table

| Problem | Primary Owner | Typical Support |
|---|---|---|
| Git branch/PR/repository issue | GitHub Manager | DevOps/Security |
| Failed GitHub workflow | GitHub Manager | DevOps |
| VPS resource issue | VPS/Docker Manager | DevOps |
| Container unhealthy | VPS/Docker Manager | DevOps |
| Production reliability | DevOps/SRE | VPS/GitHub |
| Deployment design | DevOps/SRE | GitHub/VPS |
| Security vulnerability | Security | GitHub/VPS/DevOps |
| Exposed secret | Security | GitHub/VPS |
| Broken analytics | Analytics | GitHub/UX |
| Funnel diagnosis | Analytics | Growth/UX |
| Desired-function UX | Customer Journey | Analytics/Quest |
| Root-cause diagnosis UX | Customer Journey | Analytics/Product |
| Quest/card mechanics | Quest Agent | UX/Analytics |
| Multiplayer quest design | Quest Agent | UX |
| Product-solution mapping | Product Agent | UX/Quest/Analytics |
| Checkout/payment issue | Commerce | DevOps/Security |
| Refund/fulfillment issue | Commerce | Product |
| Technical SEO | SEO/AEO | GitHub/DevOps |
| Search opportunity | SEO/AEO | Content/Analytics |
| Content creation | Content | SEO/UX/Product |
| Conversion constraint | Growth | Analytics/UX |
| Retention constraint | Growth | Analytics/Quest/Product |
| Cost anomaly | Cost/Finance | Relevant system owner |
| Executive dashboard metric | Analytics | DevOps/Orchestrator |
| Cross-system strategic mission | Orchestrator | Selected specialists |

---

# 8. Routing by Evidence Source

When the main question is "what is true?", prefer the agent closest to the authoritative source.

Examples:

```text
Repository truth → GitHub Manager
Runtime truth → VPS/Docker Manager
Metric truth → Analytics Agent
Order truth → Commerce Agent
Security truth → Security Agent
Customer-flow truth → UX + Analytics
```

---

# 9. Routing by Change Surface

When the main question is "what must change?", route to the owner of the affected surface.

Example:

A growth agent may discover a checkout constraint.

The **Commerce Agent**, not Growth, should normally own checkout implementation.

Growth remains a supporting agent.

---

# 10. Discovery vs Implementation

A specialist that discovers a problem does not automatically own implementation.

Example:

```text
SEO Agent detects slow page.
↓
DevOps/GitHub determines technical cause.
↓
Correct implementation owner changes code.
↓
SEO verifies search-facing result.
```

---

# 11. Task Contract

Every material delegated task should contain:

```yaml
task_id:
mission_id:
objective:
problem:
owner_agent:
support_agents:
mode:
scope:
non_scope:
inputs:
directive_refs:
policy_refs:
authority:
risk:
expected_output:
success_evidence:
timeout:
handoff_to:
```

---

# 12. Minimal Task Prompt

A good agent assignment answers:

- what problem?
- why now?
- what evidence?
- what scope?
- what authority?
- what output?
- what constitutes success?

Avoid vague prompts such as:

> Improve SEO.

Prefer:

> Analyze the five Entryway pages with the highest qualified organic impressions but lowest quest-start conversion. Return evidence, likely causes, and one low-risk experiment. Do not publish or deploy.

---

# 13. Read-Only First

For ambiguous or high-risk problems, route initial work as:

`DISCOVER` or `ANALYZE`

before granting:

`IMPLEMENT` or `DEPLOY`.

---

# 14. Single-Agent Default

Default to one specialist.

Add another only when it contributes distinct expertise or controls a required system.

Multi-agent collaboration is an exception, not the default.

---

# 15. Two-Agent Pattern

Common pattern:

```text
Domain Expert
+
System Owner
```

Example:

```text
SEO/AEO Agent
+
GitHub Manager
```

SEO defines the requirement.

GitHub/code owner implements safely.

---

# 16. Three-Agent Pattern

Use when measurement is essential:

```text
Domain Expert
+
Implementation Owner
+
Analytics
```

Example:

```text
Customer Journey
+
GitHub Manager
+
Analytics
```

---

# 17. Maximum Routine Collaboration

Routine missions should normally use no more than:

- 1 owner
- 2 supporting specialists

Additional agents require clear justification.

This is a coordination guardrail, not an absolute emergency limit.

---

# 18. Fan-Out Rule

The orchestrator must not recursively launch large agent trees.

If a specialist believes another agent is required, it should request a bounded handoff or support task through the orchestrator unless existing policy explicitly allows direct delegation.

---

# 19. Concurrency

Concurrency is appropriate when tasks are:

- independent
- read-only
- operating on separate resources
- not competing for the same deployment or experiment

---

# 20. Avoid Concurrent Writes

Do not allow simultaneous agents to modify the same:

- file
- feature
- customer journey
- database schema
- infrastructure resource
- deployment environment
- product record

without explicit coordination.

---

# 21. Resource Locks

Potential locks:

```yaml
locks:
  - resource: repo:path
  - resource: production
  - resource: database:schema
  - resource: journey:entryway
  - resource: experiment:id
```

Actual locking implementation belongs in scheduler/runtime architecture.

---

# 22. Deployment Ownership

A domain agent may request deployment.

The configured deployment owner should execute it according to `RELEASES.md`.

Do not give every agent independent production deployment behavior.

---

# 23. GitHub Manager Boundary

GitHub Manager should own:

- repository structure
- branches
- PR state
- Actions/workflows
- merge gates
- repository security configuration
- release lineage
- repository cleanup

It should not independently choose business strategy.

---

# 24. VPS/Docker Manager Boundary

VPS/Docker Manager should own:

- host state
- Docker/Compose
- containers
- volumes
- networks
- runtime resource health
- runtime drift
- public ports
- host-level deployment execution where configured

It should not independently redesign customer experience.

---

# 25. DevOps/SRE Boundary

DevOps/SRE owns cross-cutting operational engineering:

- deployment architecture
- observability
- reliability
- incident response
- performance
- SLO/SLA implementation
- operational automation

It should coordinate rather than duplicate GitHub/VPS ownership.

---

# 26. Security Boundary

Security can review any domain when security is implicated.

For critical findings, Security may recommend or trigger applicable pause/incident controls under governance.

Security should not silently make unrelated product decisions.

---

# 27. Analytics Boundary

Analytics owns measurement integrity.

Analytics may veto conclusions based on invalid data.

It does not independently decide product strategy merely because it owns the metric.

---

# 28. Growth Boundary

Growth identifies growth constraints and experiments.

Growth does not have automatic authority to:

- spend money
- publish unlimited content
- change checkout
- alter infrastructure
- change pricing
- create inventory commitments

Use applicable domain owners and governance.

---

# 29. SEO/AEO Boundary

SEO/AEO owns discoverability strategy and search-facing requirements.

Content owns editorial execution.

GitHub/DevOps own technical implementation where code/infrastructure is involved.

---

# 30. Content Boundary

Content may create or improve authorized content.

It must follow:

- brand
- customer journey
- SEO/AEO requirements
- product truth
- evidence rules

It should not invent products, customer results, or unsupported claims.

---

# 31. Customer Journey Boundary

Customer Journey owns the coherence of:

```text
Values
→ Desired Function
→ Root Cause
→ Desired Outcome
→ Quest
→ Solution
→ Outcome
→ Sustain
```

It should coordinate with Quest and Product rather than duplicating them.

---

# 32. Quest Agent Boundary

Quest owns:

- activity structure
- card selection
- timing
- cooperative mechanics
- assignment
- pacing
- game mechanics
- completion design

Customer Journey owns broader journey context.

---

# 33. Product Agent Boundary

Product owns solution/product architecture and fit.

Commerce owns transaction execution.

Do not combine product strategy and payment operations by default.

---

# 34. Commerce Boundary

Commerce owns:

- checkout
- payments
- orders
- refunds
- fulfillment integrations
- commerce event integrity

Pricing strategy may require Product/Growth/owner governance.

---

# 35. Cost/Finance Boundary

Cost/Finance monitors:

- infrastructure cost
- AI/API cost
- SaaS
- acquisition spend
- unit economics
- margin

It can flag or pause according to cost governance but does not independently choose growth strategy.

---

# 36. Routing: GitHub Examples

## Broken CI

Owner: GitHub Manager  
Support: DevOps

## Dependabot/security alert

Owner: Security if security-sensitive, otherwise GitHub Manager  
Support: GitHub Manager

## Branch protection missing

Owner: GitHub Manager  
Support: Security

## Release cannot map to commit

Owner: GitHub Manager  
Support: DevOps

---

# 37. Routing: VPS/Docker Examples

## Container crash loop

Owner: VPS/Docker Manager  
Support: DevOps

## Disk near capacity

Owner: VPS/Docker Manager  
Support: Cost/Finance if scaling cost is relevant

## Unknown public port

Owner: Security  
Support: VPS/Docker Manager

## Docker deployment repeatedly fails

Owner: DevOps/SRE  
Support: VPS/Docker + GitHub

---

# 38. Routing: Customer Examples

## Visitors cannot decide what Entryway should do

Owner: Customer Journey  
Support: Analytics

## Quest feels boring

Owner: Quest Agent  
Support: Customer Journey + Analytics

## Customers finish quest but area quickly regresses

Owner: Customer Journey  
Support: Quest/Product/Analytics as needed

---

# 39. Routing: Product Examples

## Many users need a better key landing zone

Owner: Product  
Support: Analytics + Quest/UX

## Need a printable key tray

Owner: Product  
Support: appropriate design/technical implementation capability

## Product sells but refund rate rises

Owner: Product or Commerce depending on cause  
Support: Analytics

---

# 40. Routing: Growth Examples

## Traffic low

Owner: Growth  
Support: SEO/AEO + Analytics

## Organic impressions high but CTR low

Owner: SEO/AEO  
Support: Content + Analytics

## Qualified traffic high but quest starts low

Owner: Customer Journey or Growth depending on root cause  
Support: Analytics

## Quest outcomes strong but repeat usage weak

Owner: Growth  
Support: Customer Journey + Quest

---

# 41. Routing: Content Examples

## Create micro-zone guide

Owner: Content  
Support: SEO/AEO + Customer Journey

## Update inaccurate product claims

Owner: Product for truth  
Content implements wording

## Build FAQ for answer engines

Owner: SEO/AEO  
Content implements

---

# 42. Routing: Analytics Examples

## Conversion rate appears impossible

Owner: Analytics

## Revenue differs between dashboard and payment system

Owner: Analytics for reconciliation  
Support: Commerce

## Experiment results unclear

Owner: Analytics  
Support: experiment domain owner

---

# 43. Routing: Incident Examples

## Website down

Owner: DevOps/SRE  
Support: VPS/Docker + GitHub

## Checkout down

Owner: Commerce  
Support: DevOps

## Database corruption suspected

Owner: DevOps/SRE or database owner  
Support: Security + VPS as applicable

## Credential leaked

Owner: Security  
Support: GitHub/VPS depending on location

---

# 44. Routing: Dashboard Examples

## Wrong metric

Owner: Analytics

## Dashboard API failing

Owner: DevOps/application owner

## Need new executive KPI

Owner: Orchestrator + Analytics

## Dashboard visual hierarchy

Owner: Customer Journey/UX or UI implementation owner

---

# 45. Routing Decision Tree

Use:

```text
Is there an incident?
├─ Yes → Incident owner
└─ No
   ↓
Is security/privacy implicated?
├─ Yes → Security lead
└─ No
   ↓
Is the question primarily about truth/data?
├─ Yes → Source/Analytics owner
└─ No
   ↓
Is it a customer experience problem?
├─ Yes → Customer Journey / Quest / Product
└─ No
   ↓
Is it growth/discovery?
├─ Yes → Growth / SEO-AEO / Content
└─ No
   ↓
Is it transaction/fulfillment?
├─ Yes → Commerce
└─ No
   ↓
Is it code/repository?
├─ Yes → GitHub Manager / implementation owner
└─ No
   ↓
Is it runtime/infrastructure?
├─ Yes → VPS/Docker / DevOps
└─ No
   ↓
Orchestrator evaluates.
```

---

# 46. Domain Ambiguity

When a task spans domains, identify the **actual bottleneck**.

Example:

"SEO page is slow."

Possible causes:

- content bloat
- frontend code
- image delivery
- server
- database

Do not route solely from the word "SEO."

---

# 47. Agent Selection Score

When multiple agents could own a task, consider:

```text
Ownership Fit
+ Evidence Access
+ Required Authority
+ Technical Expertise
+ Customer/Business Context
- Coordination Cost
```

---

# 48. No-Agent Rule

Do not spawn a specialist when:

- orchestrator can perform a trivial coordination update
- required information is already available
- task is administrative and low risk
- spawning costs more than the task
- task is blocked
- global pause prevents it
- no action is warranted

---

# 49. No-Work Rule

Valid result:

```yaml
routing_decision:
  action: NO_ACTION
  reason:
  next_check:
```

Autonomy does not require constant activity.

---

# 50. Handoff Format

Use concise evidence-based handoffs:

```yaml
handoff:
  task_id:
  from_agent:
  to_agent:
  status:
  completed_work:
  evidence_refs:
  remaining_work:
  constraints:
  required_mode:
```

---

# 51. Handoff Quality

A receiving agent should not need to repeat discovery unnecessarily.

Pass:

- verified facts
- IDs
- relevant paths
- metric definitions
- decisions
- test evidence

Do not pass speculative conclusions as facts.

---

# 52. Return-to-Orchestrator Rule

After a specialist completes its assignment, control returns to the orchestrator unless a pre-authorized handoff is defined.

This prevents uncontrolled agent chains.

---

# 53. Agent Output Contract

Specialist outputs should generally include:

```yaml
status:
summary:
evidence:
changes:
tests:
risks:
unknowns:
recommended_next_action:
handoff_needed:
```

---

# 54. Failure Contract

If agent fails:

```yaml
status: FAILED
failure_type:
attempts:
evidence:
safe_state:
recommended_next_action:
```

Do not hide partial failure.

---

# 55. Retry Routing

Retry same agent only when failure is plausibly transient or correctable.

Route differently when failure reveals a different domain.

---

# 56. Escalation to Orchestrator

Escalate when:

- scope changes materially
- another domain becomes primary
- authority is insufficient
- agents disagree materially
- cost/risk rises
- data is insufficient
- task becomes blocked

---

# 57. Escalation to Owner

Only orchestrator should normally consolidate owner escalations.

Avoid multiple agents independently interrupting the owner.

---

# 58. Owner Escalation Format

```yaml
decision:
why_now:
recommendation:
alternatives:
cost:
risk:
deadline:
```

---

# 59. Agent Disagreement

Resolve by:

1. compare authoritative evidence
2. distinguish fact from recommendation
3. check policy
4. check owner directives
5. prefer reversible action
6. run bounded test if appropriate
7. escalate only if unresolved and material

---

# 60. Security Veto

Security may block an action that violates applicable security policy.

Record reason and remediation path.

---

# 61. Analytics Veto

Analytics may block a claimed experiment conclusion when instrumentation/data quality is insufficient.

It does not necessarily block the underlying feature from existing.

---

# 62. Release Veto

Required test/release gates may block deployment.

Do not bypass them to satisfy a domain agent.

---

# 63. Cost Veto

Cost governance may block or require approval for spend beyond authority.

---

# 64. Routing and Owner Directives

Routing must respect active P0/P1 directives.

Example:

If Entryway is the current validation focus, a Kitchen optimization should not consume scarce specialist capacity unless required for health, owner request, or reusable platform work.

---

# 65. Routing and Mission Control

`MISSION-CONTROL.md` should show:

- task owner
- support agents
- mode
- status
- blockers
- next handoff

---

# 66. Routing and System Registry

Only route to agents confirmed in `SYSTEM-REGISTRY.md`.

If recommended agent does not exist:

- orchestrator handles temporarily, or
- create/configure agent through governed process

Do not pretend the agent exists.

---

# 67. Routing and Scheduler

Scheduler should use this file to determine:

- job owner
- concurrency class
- required locks
- whether another agent is already working on same resource

---

# 68. Routing and Backlog

Backlog items should optionally identify:

```yaml
suggested_owner_agent:
support_agents:
```

Final routing occurs when work is selected.

---

# 69. Routing and Experiments

Every experiment should identify:

- experiment owner
- implementation owner
- measurement owner

These may be different.

---

# 70. Example Experiment Routing

```yaml
experiment:
  owner: Customer Journey
  implementation_owner: GitHub Manager
  measurement_owner: Analytics
```

Or use actual application engineering agent if configured.

---

# 71. Routing and Releases

Release workflow should know:

```yaml
change_owner:
release_owner:
verification_owner:
```

Do not assume they are the same.

---

# 72. Routing and Incidents

Incident command should have one incident owner.

Support agents operate under the incident objective.

---

# 73. Agent Capacity

Track:

```yaml
agent_capacity:
  agent_id:
  active_tasks:
  max_active_tasks:
  status:
```

Do not overload a specialist merely because it can technically run concurrently.

---

# 74. Priority Queue

When multiple tasks want the same agent:

1. incident
2. security/data integrity
3. production/commerce
4. current primary mission
5. owner directive
6. approved maintenance
7. backlog

---

# 75. Preemption

A higher-priority task may pause lower-priority work.

Record:

```yaml
paused_task:
preempted_by:
safe_state:
resume_condition:
```

---

# 76. Context Packaging

Send agents only the context they need.

Include:

- task contract
- relevant directives
- relevant policy
- relevant registry IDs
- evidence

Avoid dumping every Markdown file into every subagent context.

---

# 77. Context Freshness

Before delegation, verify critical context is current.

Especially:

- production release
- active experiment
- owner directive
- system path
- branch
- runtime state

---

# 78. Tool Authority

An agent should only use tools required for its assignment and authority.

Read-only analysis should not require production write access.

---

# 79. Least Privilege

Prefer:

- read-only credentials for analysis
- scoped tokens
- repository-specific access
- environment-specific access

Do not give every agent root-level access.

---

# 80. Destructive Actions

Destructive actions require the authority defined in governance.

Examples:

- deleting repositories
- dropping databases
- removing persistent volumes
- deleting backups
- destructive migrations
- permanent customer-data deletion

Routing does not override approval requirements.

---

# 81. External Publishing

Content/social agents must respect external publishing authority.

Drafting and publishing are separate modes.

---

# 82. Spending

Growth/Product agents may recommend spend.

Cost/Finance evaluates economics.

Actual spend follows `COST-GOVERNANCE.md`.

---

# 83. Agent Naming

Use stable IDs.

Example:

```yaml
agent_id: agent-github-manager
display_name: GitHub Manager
```

Do not route using ambiguous names like "developer."

---

# 84. Agent Registry Fields

Each registered agent should eventually include:

```yaml
agent_id:
display_name:
file:
domains:
modes:
tools:
read_authority:
write_authority:
deploy_authority:
spend_authority:
escalation_target:
max_concurrency:
status:
last_verified:
```

---

# 85. Agent Health

Use:

- `AVAILABLE`
- `BUSY`
- `DEGRADED`
- `DISABLED`
- `UNKNOWN`

Do not route critical work to a degraded agent without reason.

---

# 86. Agent Quality Review

Periodically evaluate:

- task success
- reversions
- policy adherence
- evidence quality
- cost
- unnecessary escalation
- duplicate work
- handoff quality

---

# 87. Agent Retirement

If an agent is redundant:

1. disable routing
2. transfer responsibilities
3. update registry
4. preserve history
5. remove only after dependencies are cleared

---

# 88. New Agent Gate

Create a new specialist only when:

- recurring work exists
- domain is meaningfully distinct
- existing agents create coordination or quality problems
- clear authority can be defined
- value exceeds complexity

Do not create agents for every minor task category.

---

# 89. Recommended Current Routing Topology

Conceptually:

```text
                         OWNER
                           │
                           ▼
                    ORCHESTRATOR
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   CUSTOMER/GROWTH    TECHNOLOGY       BUSINESS OPS
          │                │                │
   ┌──────┼──────┐   ┌─────┼─────┐    ┌────┼────┐
   UX   Quest  SEO   GitHub DevOps VPS  Product Commerce
          │                │                │
        Content         Security          Cost
          │                │                │
          └────────── Analytics ────────────┘
```

This is a conceptual responsibility map, not proof of configured agents.

---

# 90. First Routing Bootstrap

When Claude first applies this file:

1. inspect `.claude` agent configuration
2. inventory actual agent MD files
3. map each to a stable registry ID
4. identify domains
5. identify tools
6. identify read/write/deploy authority
7. identify overlaps
8. identify missing ownership
9. identify duplicate agents
10. set concurrency limits
11. define escalation targets
12. update `SYSTEM-REGISTRY.md`
13. update routing table to actual agent names
14. test with read-only sample tasks
15. verify handoff behavior
16. verify Mission Control updates

Do not grant broader permissions during discovery.

---

# 91. Bootstrap Questions

The orchestrator should be able to answer:

- Who owns GitHub?
- Who owns production runtime?
- Who owns deployments?
- Who owns security?
- Who owns metrics?
- Who owns customer journey?
- Who owns quests?
- Who owns products?
- Who owns checkout?
- Who owns SEO?
- Who owns content?
- Who owns growth?
- Who owns costs?
- Who resolves conflicts?

If any answer is ambiguous, fix the routing architecture.

---

# 92. Example Task: Entryway Activation

```yaml
task_id: ENTRYWAY-ACTIVATION-001
objective: Identify the largest source of friction before quest start.
owner_agent: customer_journey
support_agents:
  - analytics
mode: ANALYZE
scope:
  - entryway
  - desired_function
  - diagnosis
expected_output:
  - verified funnel
  - friction evidence
  - top hypothesis
  - recommended experiment
```

If implementation is approved:

```yaml
implementation_owner: appropriate code/application owner
measurement_owner: analytics
```

---

# 93. Example Task: Production Failure

```yaml
task_id: INCIDENT-PROD-001
owner_agent: devops_sre
support_agents:
  - hostinger_vps_docker_manager
  - github_manager
mode: RESPOND
priority: P0
```

Security joins only if evidence indicates security involvement.

---

# 94. Example Task: SEO Content

```yaml
task_id: SEO-ENTRYWAY-001
owner_agent: seo_aeo
support_agents:
  - content
  - analytics
mode: ANALYZE
```

Content becomes implementation owner for editorial changes.

---

# 95. Example Task: Product Opportunity

```yaml
task_id: PRODUCT-KEYS-001
owner_agent: product
support_agents:
  - analytics
  - customer_journey
mode: DESIGN
```

Commerce joins only when transaction/fulfillment implementation is required.

---

# 96. Routing Maturity Model

## Level 0: Ad Hoc

Claude chooses agents inconsistently.

## Level 1: Domain Routing

Each domain has an owner.

## Level 2: Contract Routing

Tasks define mode, scope, authority, output, and handoff.

## Level 3: Coordinated

Concurrency, locks, support agents, and Mission Control are integrated.

## Level 4: Adaptive

Routing accounts for agent health, evidence access, cost, capacity, and historical quality.

## Level 5: Autonomous Executive Team

The orchestrator consistently selects the smallest qualified team, specialists operate within clear boundaries, cross-domain work has one accountable owner, conflicts are resolved from evidence and policy, and the owner sees outcomes rather than agent coordination.

---

# 97. Non-Negotiable Routing Rules

Claude and subagents must not:

- assign multiple accountable owners
- allow specialists to redefine global priority
- spawn agents merely to appear autonomous
- recursively fan out without bounds
- give every agent production access
- interpret analysis authority as implementation authority
- interpret implementation authority as deployment authority
- allow concurrent conflicting writes
- bypass security, release, or cost gates
- route solely from keywords when the actual problem belongs elsewhere
- repeatedly rediscover evidence already verified in a handoff
- pass speculation as fact
- pass hidden chain-of-thought
- let specialists independently interrupt the owner for routine decisions
- keep working after authority, scope, or safety boundaries are exceeded
- create a new agent when an existing agent can clearly own recurring work
- use agent count or activity as a success metric

---

# 98. Final Principle

The autonomous 6S Success system should operate like a strong cross-functional leadership team.

The orchestrator asks:

**What is the problem?**

**Who owns the affected system or customer outcome?**

**Who has the evidence?**

**Who has authority to change it?**

**Who must verify the result?**

**What is the smallest team needed?**

Then it assigns one accountable owner, adds only necessary support, protects shared resources, verifies the result, and returns control to the operating loop.

The goal is not:

**more agents.**

The goal is:

**clear ownership + specialized expertise + controlled execution + measurable outcomes.**

That is the purpose of `AGENT-ROUTING.md`.
