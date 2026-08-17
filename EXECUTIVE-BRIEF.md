# EXECUTIVE-BRIEF.md

## 6S Success Owner Executive Brief Standard

**Document role:** Canonical executive briefing specification for 6S
Success\
**Status:** ACTIVE\
**Audience:** Founder / Owner\
**Primary producer:** Claude Code autonomous operating system\
**Cadence:** Daily, weekly, monthly\
**Last updated:** 2026-08-17

# 1. Purpose

`EXECUTIVE-BRIEF.md` defines how Claude converts 6S Success business,
product, customer, analytics, content, commerce, GitHub, VPS/Docker,
experiments, incidents, risks, decisions, and autonomous-agent activity
into a concise owner briefing.

It must answer: **What changed, what matters, what is working, what is
not, what should happen next, and what requires the owner's decision?**

This is a decision interface, not an activity report.

# 2. Executive Principle

``` text
REAL STATE → VALIDATED DATA → MATERIAL CHANGE → PRIMARY CONSTRAINT
→ BUSINESS/CUSTOMER IMPACT → RECOMMENDED ACTION → OWNER DECISION IF REQUIRED
```

Report outcomes and exceptions, not activity volume. Agent calls,
commits, files changed, or tasks completed are not success unless they
produce a verified outcome.

# 3. Canonical Sources

Consume authoritative information from:

`BUSINESS.md`, `STRATEGY.md`, `AUTONOMY.md`, `METRICS.md`,
`DASHBOARD.md`, `DATA-SOURCES.md`, `DATA-CONTRACTS.md`, `STATUS.md`,
`ROADMAP.md`, `BACKLOG.md`, `DECISIONS.md`, `LEARNINGS.md`, `RISKS.md`,
`EXPERIMENTS.md`, `RUNBOOK.md`, `INCIDENTS.md`, `PRODUCT-CATALOG.md`,
`CONTENT-CATALOG.md`, `CHANGELOG.md`, plus verified GitHub, VPS/Docker,
analytics, monitoring, experiment, and production state.

This file summarizes those systems. It does not replace them.

# 4. Source Authority and Freshness

Never invent missing executive data. Material claims must derive from
live system state, canonical sources, verified metrics, approved
decisions, recorded experiments, validated learnings, incidents, or
owner directives.

Use `UNKNOWN`, `STALE`, `NOT INSTRUMENTED`, or `NOT YET VERIFIED` when
appropriate.

Every brief records:

``` yaml
generated_at:
reporting_window:
data_freshness:
stale_sources:
```

# 5. Briefing Modes

**Daily:** 2--4 minutes. What materially changed and does the owner need
to care?

**Weekly:** 5--10 minutes. Are we advancing the roadmap phase and
primary constraint?

**Monthly:** 10--15 minutes. Is the strategy working, should priorities
change, and have we earned the right to scale?

# 6. Daily Brief Structure

1.  Executive Summary
2.  Business Health
3.  Primary Constraint
4.  Customer / Product Signal
5.  Roadmap Position
6.  Active Mission
7.  Experiments
8.  Production / Technology
9.  Growth / Content / Commerce / Services
10. Risks / Incidents
11. Decisions Required
12. Next 24--72 Hours
13. Material Learnings
14. Unknown / Not Yet Measured

Compress sections with no material change.

# 7. Executive Summary

Use 3--5 bullets maximum. Each communicates a material change, risk,
result, or decision. Never fill this section with routine activity.

# 8. Business Health

Show only stage-relevant metrics, using:

`CURRENT | PREVIOUS | CHANGE | TARGET | STATUS`

Potential metrics: revenue, beta users, activation, quest
generation/start/completion, verified outcomes, sustain, repeat use,
paid conversion, service leads, product/kit conversion, qualified
traffic, and production health.

Status: `HEALTHY | WATCH | AT_RISK | CRITICAL | UNKNOWN`.

Thresholds come from `METRICS.md`.

# 9. Primary Constraint

Every meaningful brief identifies one primary constraint:

``` yaml
statement:
evidence:
affected_metric:
current_response:
confidence:
```

Current strategic concern until evidence changes it: too little
real-user validation of the complete Entryway quest → verified outcome →
sustain loop.

# 10. Customer / Product Signal

Prioritize actual behavior: photo/zone input, quest generation,
acceptance, card completion, quest completion, duration accuracy,
before/after verification, sustain, repeat use, feedback, supply gaps,
and confusing instructions.

Separate `OBSERVED`, `INFERRED`, and `HYPOTHESIS`.

Evaluate the customer loop:

``` text
SPACE → DESIRED FUNCTION → GAP → ROOT CAUSE → 6S COUNTERMEASURE
→ CARD → QUEST → VERIFIED OUTCOME → SUSTAIN
```

# 11. Roadmap Position

Show current phase, objective, status, exit-criteria progress, and next
gate.

Canonical phases:

``` text
0 Control the System
1 Prove Entryway
2 Photo → Diagnosis → Quest
3 Outcome + Sustain
4 Monetization
5 High-Value Room Expansion
6 Whole-Home Intelligence
7 Commerce + Services Scale
8 Autonomous Business Operations
9 Platform / Ecosystem
```

Flag roadmap drift.

# 12. Active Mission

Show the highest-priority mission first:

``` yaml
name:
objective:
status:
progress:
lead_agent:
blocker:
expected_outcome:
target_metric:
next_checkpoint:
```

Optionally include two additional material missions. Progress is based
on milestones and verified outputs, not task count.

# 13. Experiments

Show only material active, newly completed, or decision-requiring
experiments.

``` yaml
hypothesis:
variant:
metric:
sample:
result:
confidence:
recommendation:
```

Priority research includes quest vs checklist, quest duration, choice vs
assignment/random, solo vs group, photo assistance, before/after
verification, sustain cadence, recommendation timing, digital vs
physical cards, and service entry offers.

# 14. Production / Technology

Owner-level reporting includes only meaningful state: production status,
release, deployment, critical service health, VPS/Docker health, backup
status, security, performance, and critical incidents.

Do not turn the brief into a commit or container log.

GitHub is surfaced when it explains a meaningful capability, release
safety, blocker, or metric impact.

# 15. Growth / Content / Commerce / Services

Growth: qualified traffic, activation by source, beta signups, leads,
conversion. Traffic without activation is not success.

Content: report content that creates useful outcomes, requires updates,
or fills an important customer gap. Do not optimize for volume.

Commerce: product recommendations, affiliate performance, kit
interest/conversion, AOV, margin, availability, substitutions. Existing
\$199/\$299/\$499 procurement tiers are capabilities to validate, not
assumed demand.

Services: when active, report leads, bookings, completion, revenue,
margin, repeat, upsell, and verified outcomes.

# 16. Risks and Incidents

Only material risks enter the brief:

``` yaml
severity:
statement:
evidence:
exposure:
mitigation:
owner_action:
```

Prioritize customer-value, product, commercial, production, data,
security/privacy, autonomy, financial, and operational risk.

Incidents report impact, duration, root-cause status, mitigation,
customer impact, and recurrence prevention. Never call a suspected cause
the root cause.

# 17. Decisions Required

This section is critical. Show only decisions that genuinely require
owner authority.

``` yaml
question:
why_now:
recommendation:
alternatives:
expected_impact:
downside:
reversibility:
deadline:
```

`Owner decisions required: NONE` is a valid healthy state.

# 18. Autonomous Operations

Summarize only material autonomous outcomes: missions completed,
meaningful changes deployed, blocked work, owner interventions, failed
actions, and material AI/tool cost.

Useful autonomy metrics include first-route success, task success,
verification success, deployment success, rollback rate, owner
intervention rate, agent failure rate, and cost per verified outcome.

The goal is reliable autonomous value creation under owner control, not
maximum autonomy.

# 19. Learnings

Show only material validated learnings:

``` text
LEARNING
EVIDENCE
SCOPE
IMPLICATION
ACTION
```

Ideas, observations, one customer comment, or agent opinions are not
validated learnings.

# 20. Next 24--72 Hours

Show 3--5 highest-value actions connected to the primary constraint. Do
not fill this section with maintenance trivia.

# 21. Weekly Brief

Weekly sections:

``` text
Week in Review
Scorecard
Primary Constraint
Customer Outcome Evidence
Roadmap Progress
Experiment Portfolio
Revenue / Commercial Signal
Product Delivery
Growth
Production / Security
Risks / Incidents
Validated Learnings
Decisions Required
Next Week
```

Suggested scorecard areas: Customer Value, Entryway Validation, Outcome
Verification, Sustain, Growth, Monetization, Product Delivery,
Production, Autonomy.

The weekly roadmap review asks: Did the current phase advance? Which
exit criterion moved? What blocked it? Did evidence invalidate an
assumption? Should anything advance, retreat, or defer?

# 22. Monthly Strategic Brief

Sections:

1.  Strategic Assessment
2.  Customer Outcome Evidence
3.  Product-Market Signal
4.  Sustain / Retention
5.  Revenue / Unit Economics
6.  Growth Channels
7.  Roadmap Progress
8.  Experiment Portfolio
9.  Technology / Platform
10. Autonomous Operations
11. Major Risks
12. Strategic Learnings
13. Decisions / Capital Allocation
14. Next-Month Priorities

Challenge assumptions. Ask whether users get meaningful sustained value,
Entryway is proven enough to expand, photo analysis improves activation,
cards/quests beat checklists, group play helps, monetization has
evidence, services are viable, product recommendations are trusted,
procurement economics work, and autonomy is actually reducing owner
burden.

# 23. Current Strategic Position

6S Success already has substantial methodology, content, Entryway
prototype, whole-home micro-zone, card/quest, procurement, app, service,
and autonomy R&D.

The largest strategic risk is now **scope and autonomous architecture
outrunning real-user validation**.

Near-term bias:

``` text
CONTROL CANONICAL SYSTEM
+ PROVE ENTRYWAY
+ MEASURE REAL OUTCOMES
+ PROVE SUSTAIN
+ THEN SCALE
```

Roadmap baseline until live evidence changes it:

``` text
Phase 0 IN PROGRESS
Phase 1 IN PROGRESS
Phase 2 PLANNED / PARTIALLY DESIGNED
Phase 3 PLANNED
Phase 4 DISCOVERY
Phase 5 DISCOVERY
Phase 6 DISCOVERY
Phase 7 DISCOVERY
Phase 8 IN PROGRESS
Phase 9 DEFERRED
```

# 24. Owner Attention Model

Classify executive items:

`FYI | WATCH | ACTION | DECISION | URGENT`

Interrupt normal cadence only for critical production/security/privacy
issues, significant customer defects, owner decision deadlines, material
financial thresholds, blocked missions requiring owner authority, or
major experiment results that alter strategy.

# 25. Confidence and Unknowns

Use `HIGH | MEDIUM | LOW` confidence for material analytical claims.

Keep important unknowns visible, e.g.:

``` text
7-day sustain rate: NOT YET MEASURED
Entryway paid conversion: NOT YET TESTED
Kit conversion: NOT YET TESTED
Photo diagnosis correction rate: NOT YET INSTRUMENTED
```

# 26. Daily Template

``` markdown
# 6S Success Executive Brief
**Generated:** [timestamp]
**Reporting window:** [window]
**Overall status:** [status]

## Executive Summary
- ...
- ...
- ...

## Business Health
| Metric | Current | Previous | Target | Status |
|---|---:|---:|---:|---|

## Primary Constraint
**Constraint:**
**Evidence:**
**Impact:**
**Response:**

## Customer / Product
...

## Roadmap
**Current phase:**
**Exit criteria progress:**
**Next gate:**

## Active Mission
**Mission:**
**Status:**
**Expected outcome:**
**Blocker:**

## Experiments
...

## Production / Technology
**Production:**
**Release:**
**Deployment:**
**Incidents:**
**Security:**

## Growth / Commerce
...

## Risks
...

## Decisions Required
[NONE or decision package]

## Next 24–72 Hours
1.
2.
3.

## New Validated Learnings
...

## Unknown / Not Yet Measured
...
```

# 27. Weekly Template

``` markdown
# 6S Success Weekly Executive Brief
**Week ending:** [date]

## Week in Review
## Scorecard
## Primary Constraint
## Customer Outcome Evidence
## Roadmap Progress
## Experiments
## Revenue / Commercial Signal
## Product Delivery
## Growth
## Production / Security
## Risks / Incidents
## Validated Learnings
## Decisions Required
## Next Week
```

# 28. Monthly Template

``` markdown
# 6S Success Monthly Strategic Brief
**Month:** [month]

## Strategic Assessment
## Customer Outcomes
## Product-Market Signal
## Sustain / Retention
## Revenue / Unit Economics
## Growth Channels
## Roadmap
## Experiment Portfolio
## Technology / Platform
## Autonomous Operations
## Major Risks
## Strategic Learnings
## Decisions / Capital Allocation
## Next-Month Priorities
```

# 29. Machine-Readable Model

Generate structured facts before prose when supported:

``` yaml
executive_brief:
  id:
  generated_at:
  reporting_window:
  overall_status:
  data_freshness:
  executive_summary:
  scorecard:
  primary_constraint:
  customer_signals:
  roadmap:
  missions:
  experiments:
  production:
  growth:
  commerce:
  services:
  risks:
  incidents:
  decisions_required:
  next_actions:
  learnings:
  unknowns:
```

# 30. Dashboard, Event, Graph, and Context Integration

The dashboard provides interactive/live state. The Executive Brief
provides interpreted owner narrative. They must not disagree.

Material events such as `experiment.completed`, `deployment.failed`,
`incident.opened`, `metric.threshold_crossed`, `learning.validated`,
`mission.completed`, and `owner.directive_changed` may update the next
brief. Low-value events should not regenerate it.

Knowledge relationships may explain why a mission exists, what outcome
it affects, what deployment implemented it, and what learning resulted,
but live source verification remains required.

The Context Router should load only the information necessary for
owner-level briefing.

# 31. Quality Gate

Before delivery verify:

-   reporting window is correct;
-   major sources are fresh;
-   metrics are canonical;
-   comparison baseline is correct;
-   primary constraint is evidence-backed;
-   outcomes are separated from activity;
-   experiments are represented honestly;
-   production claims use current state;
-   risks are material;
-   decisions truly require the owner;
-   recommendations respect authority;
-   unknowns are visible;
-   brief is concise enough to use.

# 32. Acceptance Tests

**No material change:** produce a short brief; do not manufacture
narrative or decisions.

**Small-sample experiment improvement:** report direction and
limitation; do not standardize prematurely.

**Failed deployment with successful rollback:** report failure,
rollback, verified customer impact, and investigation status.

**Traffic +80%, activation flat:** do not celebrate traffic as business
success.

**Product clicks rise, quest outcomes fall:** prioritize the
customer-outcome problem.

**100 agent tasks, no target metric change:** flag activity/outcome
disconnect.

**Low-risk reversible action within autonomous authority:** do not
unnecessarily escalate.

**Unknown sustain metric:** report `NOT YET MEASURED`; never estimate.

# 33. Initial Executive Baseline

``` yaml
business_stage: EARLY_VALIDATION
current_focus:
  - canonical operating control
  - Entryway Home Quest validation
  - measurement
  - outcome verification
  - sustain
strongest_assets:
  - extensive 6S methodology and content
  - Entryway prototype
  - whole-home micro-zone research
  - card/quest architecture
  - procurement architecture
  - smartphone-app research
  - service architecture
  - autonomous operating architecture
primary_risk:
  - scope and autonomy architecture outrunning real-user validation
recommended_operating_bias:
  - prove Entryway with real users before broad expansion
```

Replace this planning baseline with live evidence as instrumentation
matures.

# 34. Current Owner-Level Questions

The system should continuously seek evidence for:

1.  Are real users completing Entryway quests?
2.  Do quests create visible, useful outcomes?
3.  Do outcomes sustain?
4.  Does photo assistance improve the experience?
5.  Which quest duration works best?
6.  Does group participation improve completion?
7.  Which cards are confusing, skipped, or ineffective?
8.  Which supplies are genuinely required?
9.  When does a product recommendation help?
10. Which monetization path has the strongest evidence?
11. Which room earns the right to come next?
12. Is autonomous development reducing owner workload or simply
    producing more architecture?

# 35. Non-Negotiable Anti-Patterns

Never produce a giant task dump, commit digest, agent activity list,
vanity-metric celebration, unsupported forecast, fabricated metric,
false precision, generic status language, dozens of equal-priority
risks, manufactured owner decisions, raw logs, hidden chain-of-thought,
unverified causal claims, or stale-state claims presented as live.

# 36. Final Principle

The owner should be able to understand 6S Success in minutes:

``` text
WHERE ARE WE?
WHAT CHANGED?
WHAT MATTERS?
WHAT IS THE PRIMARY CONSTRAINT?
WHAT ARE CUSTOMERS ACTUALLY DOING?
WHAT DID WE LEARN?
IS PRODUCTION HEALTHY?
ARE WE MAKING MONEY?
WHAT IS AT RISK?
WHAT IS CLAUDE DOING ABOUT IT?
WHAT NEEDS MY DECISION?
WHAT HAPPENS NEXT?
```

Everything else belongs behind the dashboard or in drill-down systems.

**The standard is minimum owner attention required for maximum informed
control.**
