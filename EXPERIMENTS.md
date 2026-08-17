# 6S Success Experiment Operating System

> Canonical experiment registry, governance model, and learning process for autonomous continuous improvement across 6S Success.

## 1. Purpose

`EXPERIMENTS.md` defines how Claude Code and specialist agents turn uncertainty into evidence.

It prevents the autonomous system from confusing:

- shipping with learning
- correlation with causation
- traffic with customer value
- purchases with successful outcomes
- statistical noise with improvement
- SEO impressions with business success
- agent activity with progress

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `BUSINESS.md`
- `STRATEGY.md`
- `METRICS.md`
- `DATA-SOURCES.md`
- `DASHBOARD.md`
- `BACKLOG.md`

---

# 2. Core Principle

**Every important uncertainty should become a testable hypothesis before it becomes a large commitment.**

Preferred loop:

**Observe**
→ **Diagnose**
→ **Hypothesize**
→ **Design**
→ **Run**
→ **Measure**
→ **Interpret**
→ **Decide**
→ **Learn**
→ **Standardize or Revert**

---

# 3. What Counts as an Experiment

An experiment is a deliberately bounded change intended to answer a question.

Examples:

- shorten the Entryway desired-function flow
- change the order of micro-zone choices
- compare 15-minute vs 30-minute quest framing
- test a digital Entryway deck offer
- test a physical/digital bundle
- improve a high-impression search landing page
- test product recommendations after root-cause diagnosis
- test a clearer checkout value proposition
- test a new internal-link architecture
- test multiplayer quest invitations
- test sustainment reminders

An experiment is not simply:

- deploying a bug fix
- patching a security issue
- routine dependency maintenance
- restoring an outage
- correcting objectively wrong content

Those changes should still be measured when useful.

---

# 4. Experiment States

Every experiment has one state:

- `IDEA`
- `DESIGNING`
- `READY`
- `RUNNING`
- `PAUSED`
- `WAITING_FOR_DATA`
- `CONCLUDED`
- `ADOPTED`
- `REJECTED`
- `INCONCLUSIVE`
- `CANCELLED`

Do not mark an experiment `ADOPTED` merely because the treatment deployed.

---

# 5. Experiment ID

Use stable IDs:

`EXP-0001`

`EXP-0002`

Never recycle IDs.

Reference experiment IDs in:

- backlog items
- GitHub issues
- pull requests
- commits where useful
- release notes
- dashboard annotations
- learnings
- decisions

---

# 6. Experiment Record

Use this canonical structure:

```yaml
id: EXP-0001
title: Short descriptive title
state: DESIGNING
owner: product-manager
backlog_id: BL-0000
created: YYYY-MM-DD
started: null
ended: null

problem: >
  What observed problem or uncertainty are we addressing?

evidence:
  - source: ...
    observation: ...

hypothesis: >
  If we change X for population Y, metric Z should improve because...

population:
  inclusion: ...
  exclusion: ...

control:
  description: ...

treatment:
  description: ...

primary_metric: quest_completion_rate

secondary_metrics:
  - desired_function_completion_rate

guardrails:
  - purchase_conversion_rate
  - application_error_rate

baseline:
  value: UNKNOWN
  period: null
  source: UNKNOWN

minimum_detectable_effect: UNKNOWN
sample_plan: UNKNOWN
minimum_run_time: UNKNOWN

autonomy_class: GREEN
approval_required: false

implementation:
  feature_flag: null
  github_refs: []
  release_refs: []

data_sources:
  - ...

quality_checks:
  - ...

results:
  primary_metric: UNKNOWN
  secondary_metrics: {}
  guardrails: {}
  confidence: UNKNOWN

interpretation: null
decision: null
learning_ids: []
```

Use `UNKNOWN` rather than inventing fields.

---

# 7. Hypothesis Standard

A strong hypothesis contains:

**Change**
+
**Population**
+
**Expected Outcome**
+
**Mechanism**

Example:

> If new Entryway users choose their desired function before selecting a micro-zone, quest-start rate will increase because recommendations will feel more personally relevant.

Weak:

> Improve the Entryway experience.

---

# 8. Customer Outcome First

Whenever possible, experiments should improve a real customer outcome.

Preferred hierarchy:

1. Sustained household improvement
2. Quest completion / successful action
3. Activation
4. Useful progression
5. Purchase of a useful solution
6. Qualified engagement
7. Traffic / visibility

Do not optimize traffic at the expense of usefulness.

---

# 9. Primary Metric

Every experiment should have **one primary metric** unless the design genuinely requires otherwise.

The primary metric should be selected before results are inspected.

Examples:

- desired_function_completion_rate
- quest_start_rate
- quest_completion_rate
- next_microzone_progression_rate
- purchase_conversion_rate
- average_order_value
- organic_qualified_session_rate

Use canonical definitions from `METRICS.md`.

---

# 10. Secondary Metrics

Secondary metrics provide explanation and additional evidence.

They should not be used after the fact to declare success when the primary metric failed unless the experiment is explicitly reinterpreted as exploratory.

---

# 11. Guardrails

Guardrails protect against local optimization.

Examples:

A shorter onboarding flow may improve activation but reduce recommendation quality.

A stronger sales CTA may increase purchase conversion but reduce trust or quest completion.

Possible guardrails:

- refund rate
- quest completion
- error rate
- page performance
- unsubscribe rate
- support complaints
- contribution margin
- sustainment

---

# 12. Baseline

Before launching, establish a baseline when feasible.

Record:

- value
- period
- population
- source
- confidence

If no trustworthy baseline exists, fix measurement first or explicitly design a test that does not require one.

---

# 13. Control Groups

Prefer randomized control/treatment when practical and ethically appropriate.

Control groups are especially valuable for:

- UX
- conversion
- offers
- recommendations
- onboarding
- quest framing

Do not force A/B testing where traffic is too small or implementation cost is disproportionate.

---

# 14. Low-Traffic Experiments

Early-stage traffic may be insufficient for conventional A/B tests.

Use alternatives:

- sequential tests
- qualitative usability
- customer interviews
- task completion observation
- controlled prototypes
- before/after with strong caveats
- cohort comparison
- smoke tests
- waitlist/demand tests

Label causal confidence appropriately.

---

# 15. Sample Size

Do not invent sample-size requirements.

When statistical testing is appropriate, calculate based on:

- baseline
- minimum detectable effect
- significance threshold
- desired power
- allocation

When inputs are unavailable, mark sample plan `UNKNOWN` and collect baseline first.

---

# 16. Minimum Run Time

Do not stop an experiment immediately when results look favorable.

Account for:

- sample size
- weekday/weekend behavior
- traffic mix
- seasonality
- novelty
- operational anomalies

Document minimum run time before launch when practical.

---

# 17. Peeking

Agents may monitor experiments for:

- safety
- severe guardrail breach
- implementation failure

Do not repeatedly peek and stop solely when a favorable result appears.

---

# 18. Stop Conditions

Stop early for:

- security issue
- severe customer harm
- material payment issue
- production instability
- major guardrail breach
- broken randomization
- corrupted measurement

Document why.

---

# 19. Experiment Autonomy

Experiments must follow `AUTONOMY.md`.

Claude may autonomously run experiments only when the underlying changes are within its authority.

An experiment label does not bypass approval requirements.

---

# 20. Pricing Experiments

Pricing affects customer trust and revenue.

Before testing:

- verify authority
- define eligible population
- ensure checkout consistency
- define refund/support handling
- preserve pricing evidence
- monitor conversion and contribution

Do not use deceptive pricing practices.

---

# 21. Product Experiments

Product tests should connect:

**Desired Function**
→ **Root Cause**
→ **Proposed Solution**
→ **Customer Outcome**
→ **Economic Outcome**

A product selling is useful evidence of demand, but not proof that it solves the customer's problem.

---

# 22. Entryway Experiment Strategy

Entryway is the proving ground.

Priority experiment families:

1. Desired-function discovery
2. Micro-zone selection
3. Root-cause diagnosis
4. Quest matching
5. Quest duration
6. Quest completion
7. Standards
8. Sustainment
9. Multiplayer
10. Product recommendation
11. Digital deck
12. Physical deck
13. Bundles
14. Progression to next micro-zone
15. Progression to next room

Avoid testing all dimensions simultaneously.

---

# 23. Desired-Function Experiments

Questions:

- Do people understand the concept?
- Which question format works best?
- Should values be selected before room outcomes?
- How many choices are useful?
- Does personalization improve quest selection?
- Does it improve completion?
- Does it improve progression?

Measure downstream outcomes, not only form completion.

---

# 24. Root-Cause Experiments

Questions:

- Can users accurately identify the friction?
- Does guided diagnosis outperform generic advice?
- Which root-cause taxonomy is understandable?
- Does diagnosis improve quest completion?
- Does it improve product recommendation relevance?

---

# 25. Quest Experiments

Test variables such as:

- duration
- card count
- difficulty
- sequence
- individual vs team
- assigned vs voluntary selection
- random vs configured
- progress feedback
- rewards
- escape-room mechanics

Primary outcome should remain useful completion.

---

# 26. Multiplayer Experiments

Potential hypotheses:

- visible shared progress increases completion
- role assignment reduces conflict
- voluntary card selection improves engagement
- time-boxed cooperative challenges improve completion
- household streaks improve return behavior

Guard against mechanics that create pressure or family conflict.

---

# 27. Sustainment Experiments

The goal is not a one-time tidy room.

Test:

- follow-up timing
- visual standards
- reset reminders
- photo comparisons
- quick sustainment quests
- ownership prompts
- replenishment cues

Measure whether the micro-zone remains functional.

---

# 28. SEO Experiments

SEO changes can include:

- title/meta improvements
- content structure
- internal linking
- page consolidation
- direct answers
- schema
- intent alignment
- page experience

Use Search Console plus onsite behavior.

SEO results often require longer observation windows.

---

# 29. AEO Experiments

AEO testing may include:

- concise answer blocks
- stronger question/answer structure
- entity clarity
- structured data
- source/evidence clarity
- semantic internal linking

Do not claim answer-engine visibility without observable evidence.

---

# 30. Content Experiments

Content should test usefulness.

Possible primary metrics:

- qualified engagement
- desired-function start
- quest start
- product-assisted outcome

Do not use page views as the only success metric.

---

# 31. Landing Page Experiments

Potential variables:

- problem framing
- audience
- CTA
- proof
- quest preview
- product positioning
- visual hierarchy

Guardrails:

- bounce/qualified engagement
- activation
- conversion
- page speed

---

# 32. Commerce Experiments

Potential:

- bundles
- merchandising
- recommendation placement
- checkout clarity
- free vs paid boundaries
- digital/physical combinations
- order bumps where genuinely useful

Avoid manipulative dark patterns.

---

# 33. AOV Experiments

If AOV becomes the primary constraint, test useful combinations.

Example:

Entryway Deck
+
Visual Control Kit
+
Micro-Zone Labels

The bundle must solve a coherent customer problem.

Do not add irrelevant products merely to increase basket size.

---

# 34. Revenue Experiments

Revenue experiments should distinguish:

**Revenue increase**

from

**Revenue quality improvement**

Track where available:

- conversion
- AOV
- refunds
- COGS
- contribution
- repeat purchase
- customer outcome

---

# 35. Traffic Experiments

Traffic is useful only if it produces qualified users.

Measure:

- traffic
- qualified engagement
- activation
- downstream outcomes

Do not optimize bot or low-intent traffic.

---

# 36. Technical Experiments

Technical experiments may evaluate:

- performance
- deployment method
- caching
- resource efficiency
- build process

Do not experiment recklessly in production infrastructure.

Use safe rollout and rollback.

---

# 37. Feature Flags

Use feature flags when they materially improve:

- controlled exposure
- rollback
- experiment assignment

Avoid building an elaborate flag platform before needed.

Every temporary flag should have an owner and cleanup condition.

---

# 38. Experiment Assignment

Assignment should be stable for the intended unit.

Possible units:

- user
- household
- session
- page
- geographic cohort

Do not switch a user between variants unexpectedly when persistence matters.

---

# 39. Experiment Contamination

Watch for:

- users seeing both variants
- bot traffic
- internal traffic
- test accounts
- cross-device identity
- simultaneous experiments
- campaign mix changes

Document limitations.

---

# 40. Concurrent Experiments

Do not run overlapping experiments on the same critical funnel if interactions make interpretation unreliable.

Maintain an experiment map by surface.

---

# 41. Experiment Surface Registry

Maintain:

| Surface | Active Experiment | Owner | Conflict Risk |
|---|---|---|---|
| Entryway onboarding | NONE | product-manager | LOW |
| Quest selection | NONE | product-manager | LOW |
| Checkout | NONE | commerce-manager | HIGH |
| SEO landing pages | NONE | seo-aeo | MEDIUM |

Update when experiments start/end.

---

# 42. Instrumentation Validation

Before launch:

1. test exposure event
2. test assignment
3. test primary metric
4. test guardrails
5. exclude test/internal traffic
6. verify production environment
7. confirm data freshness

Broken instrumentation invalidates results.

---

# 43. Experiment QA

Verify:

- control behavior
- treatment behavior
- mobile
- desktop
- major browsers where relevant
- analytics
- accessibility
- page performance
- checkout if affected
- rollback

---

# 44. Release Traceability

Every coded experiment should connect:

**EXP ID**
→ **Backlog ID**
→ **PR**
→ **Commit**
→ **Build**
→ **Deployment**
→ **Exposure**

This allows the dashboard to annotate results correctly.

---

# 45. Experiment Dashboard

Show active experiments with:

- ID
- hypothesis
- owner
- state
- start
- sample
- primary metric
- guardrails
- confidence
- next decision

Do not show a "winner" badge before conclusion.

---

# 46. Interpretation

At conclusion, answer:

1. Did the primary metric improve?
2. By how much?
3. How confident are we?
4. Did guardrails degrade?
5. Were there implementation/data issues?
6. Does the evidence support the proposed mechanism?
7. Is the result generalizable?
8. What should happen next?

---

# 47. Result Classifications

Use:

- `SUPPORTED`
- `NOT_SUPPORTED`
- `MIXED`
- `INCONCLUSIVE`
- `INVALID`

Do not use "failed" for every unsupported hypothesis.

The experiment may have successfully produced useful evidence.

---

# 48. Confidence

Use:

- `HIGH`
- `MEDIUM`
- `LOW`
- `UNKNOWN`

Confidence should consider:

- design quality
- sample
- measurement
- effect size
- consistency
- confounding

Do not equate statistical significance automatically with high practical confidence.

---

# 49. Practical Significance

A statistically detectable change may be too small to matter.

Ask:

- Does it meaningfully help customers?
- Does it materially improve economics?
- Is implementation complexity worth it?
- Is the effect durable?

---

# 50. Negative Results

Preserve negative results.

Example:

`EXP-0012: Gamified timer increased starts but reduced completion.`

This prevents future agents from repeating the same idea.

---

# 51. Inconclusive Results

When inconclusive:

- do not call treatment better
- determine why
- decide whether uncertainty is worth another test
- improve design only if the question remains important

Do not endlessly rerun low-value tests.

---

# 52. Adoption Decision

Adopt when:

- evidence supports change
- guardrails are acceptable
- operational cost is acceptable
- strategic fit remains strong

Then:

1. make treatment standard
2. remove obsolete control logic
3. remove temporary flags when appropriate
4. update documentation
5. record learning

---

# 53. Rejection Decision

Reject when:

- evidence contradicts hypothesis
- guardrails degrade
- economics are poor
- customer outcome worsens
- complexity outweighs benefit

Revert when appropriate.

---

# 54. Iteration Decision

Iterate when:

- mechanism remains plausible
- evidence suggests a specific improvement
- uncertainty is still strategically valuable

Create a new experiment ID.

Do not overwrite the old experiment.

---

# 55. Experiment Learnings

Durable findings should move into `LEARNINGS.md`.

Example:

**Learning:** Entryway users selecting a desired function before micro-zone selection were more likely to begin a recommended quest in the tested population.

Include scope and confidence.

Do not generalize beyond evidence.

---

# 56. Decisions

Material durable decisions should move into `DECISIONS.md`.

Example:

**Decision:** Desired-function selection will precede micro-zone recommendation in the Entryway default flow.

Link experiment evidence.

---

# 57. Backlog Integration

After conclusion:

- close related backlog item
- create follow-up only if justified
- reprioritize based on learning
- update current constraint if evidence changes

---

# 58. STATUS Integration

`STATUS.md` should mention only material experiment state:

- key running experiments
- major results
- important blockers

Do not copy the entire registry.

---

# 59. Strategic Integration

Experiment portfolio should focus on the current strategic phase.

Before Entryway validation, most product experiments should strengthen Entryway learning.

Do not scatter experiments across every room.

---

# 60. Portfolio Balance

A useful early portfolio may include:

- 1 customer-value experiment
- 1 growth/acquisition experiment
- 1 monetization experiment

But WIP and traffic constraints override this.

Do not run experiments simply to fill categories.

---

# 61. Experiment WIP

Default maximum:

**3 material experiments RUNNING simultaneously**

Fewer is better when traffic is low.

This is separate from, but coordinated with, the major workstream WIP limit.

---

# 62. Experiment Prioritization

Prioritize experiments that:

1. address primary constraint
2. resolve strategic uncertainty
3. improve customer outcome
4. have meaningful economic upside
5. can be run safely
6. are relatively reversible
7. produce fast learning

---

# 63. Experiment Cost

Record material costs:

- development
- paid traffic
- tooling
- discounts
- product samples
- fulfillment

Follow `AUTONOMY.md` spending limits.

---

# 64. Ethical Standard

Experiments must not:

- deceive customers
- fabricate scarcity
- create false reviews
- hide recurring charges
- manipulate cancellation
- intentionally degrade vulnerable users
- misuse private household data

Customer trust is a guardrail.

---

# 65. Privacy

Do not expose customer-level experiment data in broad dashboards.

Use aggregate data.

Handle household images and personal information according to security/privacy policies.

---

# 66. SEO Experiment Caveat

Search engines are external systems with delayed, noisy outcomes.

For SEO experiments:

- use longer windows
- account for indexing
- annotate algorithm/site changes
- compare appropriate page/query cohorts
- avoid claiming causality too strongly

---

# 67. Revenue Target Experiments

The $20K/month target should guide constraint analysis, not pressure agents into bad experiments.

Never sacrifice:

- customer trust
- margin discipline
- security
- product quality
- long-term retention

for a short-term revenue spike.

---

# 68. Experiment Automation

Claude may automate:

- experiment registration
- assignment where architecture supports it
- data collection
- dashboard updates
- guardrail monitoring
- statistical analysis
- result drafting
- rollback within authority

Claude must not automate away required human approvals.

---

# 69. Experiment Alerts

Alert immediately for:

- guardrail breach
- checkout/payment defect
- security issue
- production instability
- corrupted assignment
- corrupted measurement

Do not alert owner for ordinary statistical fluctuation.

---

# 70. Experiment Archive

Concluded experiments remain searchable.

Do not delete experiments because they were unsuccessful.

Historical experiment knowledge is a strategic asset.

---

# 71. Searchability

Agents should be able to search:

- hypothesis
- room
- micro-zone
- root cause
- metric
- product
- result
- learning

This prevents repeated experiments.

---

# 72. Initial Experiment Queue

These are candidate experiments, not automatically approved launches.

Actual baseline evidence should determine order.

---

## EXP-0001: Entryway Desired Function Before Micro-Zone

**State:** IDEA  
**Owner:** product-manager  
**Backlog:** BL-0013

### Hypothesis

If new Entryway users identify their desired function before choosing a micro-zone, they will start recommended quests at a higher rate because the experience will feel more personally relevant.

### Primary Metric

`quest_start_rate`

### Secondary

- desired-function completion
- quest completion

### Guardrails

- abandonment
- page performance

### Prerequisite

Validated instrumentation.

---

## EXP-0002: Short vs Guided Desired-Function Flow

**State:** IDEA  
**Owner:** product-manager

### Hypothesis

A shorter desired-function flow will increase completion without materially reducing quest relevance.

### Primary Metric

`desired_function_completion_rate`

### Guardrail

`quest_completion_rate`

---

## EXP-0003: 15-Minute Entryway Quick Quest

**State:** IDEA  
**Owner:** quest-experience

### Hypothesis

A clearly framed 15-minute Entryway quest will increase first-quest completion for new users.

### Primary Metric

`quest_completion_rate`

### Secondary

`next_microzone_progression_rate`

---

## EXP-0004: Root-Cause Guided Quest Recommendation

**State:** IDEA  
**Owner:** product-manager  
**Backlog:** BL-0014

### Hypothesis

Users receiving a quest matched to a diagnosed root cause will complete quests more often than users receiving generic room-level recommendations.

### Primary Metric

`quest_completion_rate`

### Guardrail

diagnosis abandonment.

---

## EXP-0005: Digital Entryway Deck Paid Offer

**State:** IDEA  
**Owner:** commerce-manager  
**Backlog:** BL-0017

### Question

Will customers pay for a structured digital Entryway deck that provides substantially more value than free content?

### Primary Metric

Purchase conversion among eligible product viewers.

### Secondary

- AOV
- refund rate
- quest engagement after purchase

---

## EXP-0006: Entryway Product Bundle

**State:** IDEA  
**Owner:** commerce-manager

### Hypothesis

A coherent Entryway bundle will increase AOV while preserving purchase conversion and customer outcome.

### Primary Metric

AOV

### Guardrails

- purchase conversion
- refund rate
- contribution margin
- quest completion where measurable

### Prerequisite

Evidence that AOV is a meaningful constraint.

---

## EXP-0007: High-Impression Entryway Search Page Improvement

**State:** IDEA  
**Owner:** seo-aeo

### Question

Can improving intent alignment and direct-answer quality on a verified high-impression Entryway page increase qualified organic visits and downstream activation?

### Primary Metric

Qualified organic sessions or activation from the page.

### Prerequisite

Search Console baseline.

---

## EXP-0008: Multiplayer Voluntary Card Selection

**State:** IDEA  
**Owner:** quest-experience

### Hypothesis

Allowing participants to voluntarily select available cards will improve multiplayer quest completion and engagement compared with fully assigned cards.

### Guardrails

- completion time
- unclaimed critical tasks
- participant drop-off

---

## EXP-0009: Micro-Zone Sustainment Check

**State:** IDEA  
**Owner:** product-manager

### Hypothesis

A lightweight follow-up check will increase sustained micro-zone improvements without creating excessive reminder fatigue.

### Primary Metric

Sustained Improvement Rate

### Guardrail

opt-out / disengagement.

---

# 73. Initial Operating Sequence

Before running the candidate experiments:

1. verify analytics sources
2. validate event instrumentation
3. establish Entryway baseline
4. identify primary constraint
5. select highest-value uncertainty
6. design experiment
7. verify autonomy
8. launch
9. monitor guardrails
10. conclude based on evidence
11. record learning
12. update backlog

---

# 74. Experiment Review Template

At conclusion:

## Experiment

`EXP-XXXX: Title`

## Hypothesis

...

## Design

...

## Population

...

## Primary Metric

...

## Result

...

## Guardrails

...

## Data Quality

...

## Interpretation

...

## Confidence

...

## Decision

`ADOPT / REJECT / ITERATE / INCONCLUSIVE`

## Customer Impact

...

## Business Impact

...

## Learning

...

## Follow-Up

...

---

# 75. Executive Summary Format

For the dashboard:

**EXP-XXXX: Short title**

`RUNNING | Day 8 | 62% planned sample`

Primary metric: `+6.2% vs control`

Confidence: `LOW`

Guardrails: `HEALTHY`

Decision: `CONTINUE`

Only use actual verified values.

---

# 76. Experiment Success

The experiment system is working when:

- important uncertainty becomes measurable
- changes have hypotheses
- failed ideas are preserved
- agents stop repeating disproven approaches
- customer outcomes improve
- monetization improves without harming outcomes
- Entryway learning accelerates
- the backlog changes based on evidence
- Claude can explain why it made major changes

---

# 77. Anti-Patterns

Never allow:

## HIPPO-by-Agent

An agent's confidence is not evidence.

## Shipping Bias

Deployment does not prove improvement.

## Metric Shopping

Do not search secondary metrics for a favorable story.

## Endless Testing

Not every detail needs an experiment.

## Test Pollution

Do not let internal/test traffic contaminate results.

## Simultaneous Chaos

Avoid many overlapping tests.

## Revenue-Only Optimization

Do not ignore customer outcome.

## Premature Scaling

Do not expand a weak loop because one metric improved.

---

# 78. Next-Step Decision Logic

After every experiment ask:

### Supported + Valuable

Adopt and standardize.

### Supported + Small Value

Adopt only if complexity is low.

### Mixed

Investigate mechanism and guardrails.

### Not Supported

Reject/revert unless new evidence justifies iteration.

### Inconclusive + Important

Improve design and retest.

### Inconclusive + Low Value

Stop.

---

# 79. Relationship to Continuous Improvement

This system should behave like disciplined PDCA:

**PLAN**

Define problem, baseline, hypothesis, measure.

**DO**

Run bounded change.

**CHECK**

Evaluate outcome and guardrails.

**ACT**

Adopt, standardize, iterate, or reject.

Experiments are the evidence engine inside the broader 6S Success autonomous operating system.

---

# 80. Final Rule

Claude must never say:

**"I improved the website."**

when the evidence only shows:

**"I changed the website."**

The correct sequence is:

**I observed a problem.**

**I formed a hypothesis.**

**I made a controlled change.**

**I verified deployment.**

**I measured the result.**

**I checked guardrails.**

**I learned what happened.**

**I adopted, iterated, or reverted based on evidence.**

That discipline is what turns autonomous coding into autonomous continuous improvement.
