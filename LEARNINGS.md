# 6S Success Organizational Learnings

> Canonical evidence-backed learning memory for the autonomous 6S Success organization.

## 1. Purpose

`LEARNINGS.md` preserves what 6S Success has actually learned so Claude Code and specialist agents become smarter over time instead of repeatedly rediscovering the same facts.

It records durable evidence about customers, desired functions, rooms, micro-zones, root causes, quests, sustainment, products, pricing, content, SEO/AEO, conversion, GitHub, Hostinger VPS/Docker, reliability, data quality, and autonomous-agent performance.

Read with `CLAUDE.md`, `AUTONOMY.md`, `STATUS.md`, `BUSINESS.md`, `STRATEGY.md`, `METRICS.md`, `DATA-SOURCES.md`, `DASHBOARD.md`, `BACKLOG.md`, `EXPERIMENTS.md`, and `DECISIONS.md`.

## 2. Core Principle

**A learning is an evidence-backed observation, not an opinion.**

Operating loop:

**Observation → Evidence → Learning → Decision or New Hypothesis → Action → More Evidence**

## 3. What Counts as a Learning

A learning should be useful beyond one task, supported by evidence, scoped to the context actually observed, reusable by future agents, and capable of affecting a future decision.

Examples include:

- Entryway users completing desired-function discovery are more likely to begin a recommended quest.
- Shoe storage friction is disproportionately associated with capacity mismatch in tested households.
- A landing page receives high search impressions but weak qualified activation.
- A bundle increases AOV but reduces contribution.
- Production deployment metadata does not reliably identify the running Git commit.
- Backup jobs succeed, but no representative restore has been validated.

## 4. What Is Not a Validated Learning

Do not store agent opinion, brainstorming, generic best practice, unverified assumptions, isolated anecdotes, targets, strategies, tasks, decisions, or raw metric fluctuations as validated learnings.

These may instead become hypotheses or backlog items.

## 5. Learning IDs

Use stable IDs: `LRN-0001`, `LRN-0002`, etc. Never recycle IDs.

Reference them from decisions, experiments, backlog items, product requirements, content planning, and dashboard recommendations.

## 6. Learning Status

Use:

- `HYPOTHESIS`: plausible but not sufficiently evidenced
- `EMERGING`: some evidence exists
- `SUPPORTED`: adequate evidence for bounded operational use
- `STRONG`: repeated/high-quality evidence within defined scope
- `CONTRADICTED`: material conflicting evidence exists
- `SUPERSEDED`: newer learning better represents understanding
- `STALE`: context changed enough to require revalidation

## 7. Confidence

Use `HIGH`, `MEDIUM`, `LOW`, or `UNKNOWN`.

Confidence considers sample size, source quality, experimental quality, consistency, recency, confounding, directness, and replication.

## 8. Canonical Learning Record

```yaml
id: LRN-0001
title: Concise learning
status: EMERGING
confidence: MEDIUM
domain: PRODUCT
created: YYYY-MM-DD
updated: YYYY-MM-DD
owner: product-manager

statement: >
  The evidence-backed learning stated precisely.

scope:
  population: ...
  room: ...
  micro_zone: ...
  channel: ...
  period: ...

evidence:
  - type: EXPERIMENT
    reference: EXP-0000
    observation: ...

limitations:
  - ...

implications:
  - ...

related:
  decisions: []
  experiments: []
  backlog: []

revalidation_trigger: >
  What would require this learning to be tested again?

supersedes: null
superseded_by: null
```

Use `UNKNOWN` rather than inventing facts.

## 9. Scope Discipline

Never generalize farther than evidence permits.

Bad: **Families prefer 15-minute quests.**

Better: **Among first-time Entryway users in the tested cohort, 15-minute quest framing produced higher completion than 30-minute framing.**

## 10. Evidence Hierarchy

Stronger evidence may include randomized experiments, repeated behavioral evidence, verified transactions, validated product telemetry, representative usability testing, and verified production telemetry.

Moderate evidence may include cohort analysis, Search Console patterns, structured customer feedback, support patterns, and before/after analysis with known caveats.

Weaker evidence includes single anecdotes, agent intuition, generic web advice, competitor behavior, and synthetic evaluation.

Weak evidence can generate hypotheses but should rarely create `STRONG` learnings.

## 11. Converging Evidence

Prefer multiple independent evidence sources.

A micro-zone problem appearing in desired-function responses, quest abandonment, customer feedback, product searches, and repeat diagnoses is more credible than one signal alone.

## 12. Contradictory Evidence

Never hide contradictions. Record conflicting evidence, source quality, possible segment differences, and whether confidence should change.

Contradiction may reveal segmentation rather than invalidate the entire learning.

## 13. Negative Knowledge

Preserve what does not work.

Examples:

- a quest mechanic reduced completion
- a bundle reduced contribution
- a page rewrite reduced qualified activation
- a deployment method created runtime drift
- an automation produced noisy alerts

Negative knowledge prevents repeated waste.

## 14. Learning vs Decision

Learning: **Users in the tested Entryway cohort completed more quests after selecting a desired function.**

Decision: **Desired-function selection will remain in the default Entryway flow.**

Evidence informs decisions, but the artifacts remain separate.

## 15. Learning vs Experiment

`EXPERIMENTS.md` stores hypothesis, design, results, and experiment disposition.

`LEARNINGS.md` stores durable reusable knowledge produced by experiments and other evidence.

Not every experiment needs a durable learning.

## 16. Learning vs Metric

Metric: `Quest completion rate = 41%`

Learning: **Quest completion is materially lower for quests requiring multiple storage relocation steps in the observed cohort.**

Metrics are observations. Learnings are evidence-backed interpretations.

## 17. Learning Domains

Use one primary domain:

`CUSTOMER`, `VALUES`, `DESIRED_FUNCTION`, `ROOM`, `MICRO_ZONE`, `ROOT_CAUSE`, `QUEST`, `SUSTAINMENT`, `MULTIPLAYER`, `PRODUCT`, `COMMERCE`, `PRICING`, `CONTENT`, `SEO`, `AEO`, `ACQUISITION`, `CONVERSION`, `RETENTION`, `DATA`, `GITHUB`, `DEVOPS`, `VPS`, `DOCKER`, `RELIABILITY`, `SECURITY`, `AUTONOMY`, or `OPERATIONS`.

## 18. Customer Learning Model

Customer learning should increasingly answer:

**Who? → What do they want the area to do? → What prevents that? → What intervention works? → What persists? → What are they willing to pay for?**

## 19. Values and Desired Functions

Learn which expressed values influence room outcomes, such as speed, calm, independence, hospitality, safety, simplicity, preparedness, accessibility, family participation, and visual order.

Do not infer sensitive personal attributes.

For each room and micro-zone, learn common desired functions, conflicting functions, household differences, effective discovery questions, and which desired functions predict useful quests or products.

## 20. Root-Cause Learning

Build evidence around root-cause families such as:

- excess
- no home
- wrong home
- poor access
- poor visibility
- excess steps
- unclear ownership
- capacity mismatch
- no standard
- replenishment failure
- cleaning friction
- safety risk

Track which causes are frequent, persistent, expensive, easy to solve, product-assisted, and likely to recur.

## 21. Micro-Zone Learning

For each micro-zone, learn primary functions, common items, common friction, root causes, successful quests, useful standards, sustainment failure modes, relevant products, and seasonal variation.

This should eventually power increasingly precise recommendations.

## 22. Quest Learning

Track completion, duration, difficulty, abandonment, player count, voluntary versus assigned cards, random versus configured selection, root-cause match, sustained outcome, and progression.

Never optimize completion by making quests meaningless.

## 23. Sustainment Learning

Learn what causes improvements to persist, including visual controls, labels, assigned homes, ownership, capacity limits, reset routines, replenishment cues, follow-up timing, and physical product support.

Sustainment is strategically more important than one-time cleanup.

## 24. Multiplayer Learning

Learn optimal team size, role clarity, card selection behavior, conflict points, participation, completion, child-friendly mechanics, and adult coordination.

Do not design mechanics that pressure or shame household members.

## 25. Product and Pricing Learning

For products, learn the problem solved, root causes addressed, micro-zones served, purchase intent, conversion, returns/refunds, usage where measurable, quest impact, and sustainment impact.

For pricing, learn willingness to pay, conversion, AOV, contribution, refunds, bundle response, and meaningful segment differences.

A high-selling product that does not improve the intended outcome requires investigation.

## 26. Content, SEO, and AEO Learning

Learn which content attracts qualified visitors, answers real questions, activates quests, assists purchases, and creates progression.

SEO learning should connect queries, intent, landing pages, CTR, ranking, qualified engagement, activation, and conversion.

AEO learning must use observable evidence such as referrals, citations/mentions where measurable, crawler accessibility, and question coverage. Never fabricate visibility.

## 27. Funnel and Revenue Learning

Learn where and why users stop in the journey.

Revenue learning should identify which levers matter: qualified traffic, activation, product exposure, conversion, AOV, repeat purchase, margin, and customer outcome.

The $20K/month target should become increasingly decomposed into evidence-backed levers.

## 28. Technical and Operational Learning

Preserve reusable findings about:

- GitHub release processes and CI failure patterns
- rollback effectiveness and traceability
- VPS/Docker runtime architecture and drift
- persistent-data locations and dependencies
- incident root causes
- recovery effectiveness
- instrumentation and reconciliation problems
- bot/test contamination
- autonomous-agent handoff or alert failures

Never store secrets.

## 29. Learning Promotion and Demotion

A learning may progress:

`HYPOTHESIS → EMERGING → SUPPORTED → STRONG`

or regress when evidence weakens it:

`STRONG → SUPPORTED → EMERGING → CONTRADICTED`

Promotion requires evidence, not age.

## 30. Revalidation

Revalidate when customer segments, products, room taxonomy, pricing, acquisition channels, UX, instrumentation, market context, or technical architecture materially change.

Different learnings have different half-lives. Search rankings and conversion benchmarks age faster than stable physical room relationships.

## 31. Learning Index

Maintain:

| ID | Learning | Domain | Status | Confidence |
|---|---|---|---|---|
| LRN-0001 | Desired function may improve recommendation relevance | DESIRED_FUNCTION | HYPOTHESIS | UNKNOWN |
| LRN-0002 | Root-cause matching may improve quest outcomes | ROOT_CAUSE | HYPOTHESIS | UNKNOWN |
| LRN-0003 | Short quests may reduce initial participation friction | QUEST | HYPOTHESIS | UNKNOWN |
| LRN-0004 | Cooperative card choice may improve group engagement | MULTIPLAYER | HYPOTHESIS | UNKNOWN |
| LRN-0005 | Sustainment requires more than initial organization | SUSTAINMENT | HYPOTHESIS | MEDIUM |
| LRN-0006 | The mailing list 500s; the recorded blocker was stale and named the wrong setting | LIFECYCLE | SUPPORTED | HIGH |
| LRN-0007 | `quest-first-start` has zero events because it deployed after the last visit | MEASUREMENT | SUPPORTED | HIGH |
| LRN-0008 | Every buy-click came from a page that never priced the thing on the button | CONVERSION | SUPPORTED | MEDIUM |
| LRN-0009 | "Source corrected, artifact never re-derived" is a recurring defect class, now structurally gated | ENGINEERING / RELIABILITY | SUPPORTED | HIGH |
| LRN-0010 | Every buy and quote signal since 7 September traced to the owner's own household | CONVERSION / DATA QUALITY | SUPPORTED | HIGH (attribution) / MEDIUM (stranger estimate) |
| LRN-0011 | A re-render gate is only as current as the untracked intermediates it reads | DATA QUALITY / BUILD | SUPPORTED | HIGH |
| LRN-0012 | The local image model draws the room, not the micro zone; a close-up of one or two objects is the shape that works | MEDIA / BUILD | SUPPORTED | MEDIUM |
| LRN-0013 | Googlebot read every zone page once in late August and chose not to come back; not a reachability problem | SEO / AEO | SUPPORTED | MEDIUM |
| LRN-0014 | A conflict in a newest-first file must be resolved by date order, not by marker order | PROCESS / GIT | SUPPORTED | HIGH |
| LRN-0015 | A count is not a count until its unit is named; pageviews and events are not interchangeable | MEASUREMENT | SUPPORTED | HIGH |
| LRN-0016 | Fixing a generator does not fix what it already rendered; the expensive artifacts are the ones nobody checks | QUALITY / RELEASE | SUPPORTED | HIGH |
| LRN-0017 | Authoring against an ID vocabulary from memory produces branches that are well formed, real, and wrong | CONTENT / BUILD | SUPPORTED | HIGH |
| LRN-0018 | Crawlers fetch by sitemap, not by depth, so content quality cannot be measured in a server log | SEO / AEO | SUPPORTED | HIGH |
| LRN-0019 | The $29 Manual's body text is not re-derived from the corpus by anything in ops/, so a corpus fix never reaches the product | BUILD / PRODUCT | SUPPORTED | HIGH |
| LRN-0020 | When a gate has no available action, the format is usually the thing to change, not the blocker | MEDIA / BUILD | SUPPORTED | HIGH |
| LRN-0022 | A fixed threshold is a dated assumption about corpus size, and it fails as a reward for growth | BUILD / QUALITY | SUPPORTED | HIGH |
| LRN-0021 | nohup and disown do not protect a background job from a process-group signal; only a new session (setsid) does | ENGINEERING / RELIABILITY | SUPPORTED | HIGH |
| LRN-0023 | Text shared by every room must not assume one room, and no equality check can find the assumption | CONTENT / QUALITY | SUPPORTED | HIGH |
| LRN-0024 | Read the line ending from what git stores, not from the working copy | ENGINEERING / TOOLING | SUPPORTED | HIGH |
| LRN-0025 | At this traffic scale one 20-minute burst can invert a weekly trend, so check concentration before calling direction | ANALYTICS / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0026 | Every instrument must exclude its own operator, because a tool that measures a system also acts on it | ANALYTICS / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0027 | On a shared main, one red build strands every change made near it, and the tooling will tell you to keep retrying | ENGINEERING / DELIVERY | SUPPORTED | HIGH |
| LRN-0028 | A generated image can be good and still wrong, and the reviewer's first instinct is aesthetic | MEDIA / QUALITY | SUPPORTED | MEDIUM |
| LRN-0029 | The query half of Search Console is public, and nobody had looked; the complaint our product answers has no page | SEO / AEO | SUPPORTED | HIGH |
| LRN-0030 | A test that shells out must prove its interpreter, or the environment answers in place of the code | ENGINEERING / TOOLING | SUPPORTED | HIGH |
| LRN-0031 | Publishing a measurement to a shared main is itself a work assignment, and two sessions will take it | PROCESS / COORDINATION | SUPPORTED | HIGH |
| LRN-0032 | A stored coverage status is a snapshot of a corpus other sessions are changing; re-score before concluding | ANALYTICS / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0033 | An ad-hoc pattern that matches nothing looks exactly like a true absence, and throwaway analysis gets no second opinion | ANALYTICS / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0034 | The tool that writes the code can corrupt it silently; a planted defect that does not fail is the only reliable detector | ENGINEERING / TOOLING | SUPPORTED | HIGH |
| LRN-0035 | A repeated "needs live network reach" finding is a sandbox property, not a data property, and the fix is a workflow, not another cycle | ENGINEERING / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0036 | Every page is crawled and almost none is ranked: crawl coverage is 210 of 211 and search sent 6 requests in 14 days | SEO / ANALYTICS | SUPPORTED | HIGH |
| LRN-0037 | A metric protected only by a third-party heuristic is unprotected: our own headless browser sent 9,113 beacons | ANALYTICS / MEASUREMENT | SUPPORTED | HIGH |
| LRN-0038 | A page our domain serves is our page, whoever renders it, and a checker can assert a defect is present and call it green | TRUST / PRIVACY | SUPPORTED | HIGH |
| LRN-0039 | Three gates checked what the owner's email said and none checked that it was sent | PROCESS / RELIABILITY | SUPPORTED | HIGH |
| LRN-0040 | "No browser in this sandbox" is a per-container fact, not a standing one, and it was being treated as the latter | ENGINEERING / TOOLING | SUPPORTED | HIGH |

Only evidence-backed learnings should appear as `SUPPORTED` or `STRONG`.

## 32. Initial Hypothesis Register

Do not pretend strategic beliefs are validated learnings.

### LRN-0001: Desired Function May Improve Recommendation Relevance

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** DESIRED_FUNCTION

Allowing users to define what they want a room or micro-zone to accomplish may improve quest and product recommendation relevance.

Evidence needed: desired-function completion, recommendation interaction, quest start, quest completion, and progression.

Related: `DEC-0002`, `EXP-0001`, `EXP-0002`.

### LRN-0002: Root-Cause Matching May Improve Quest Outcomes

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** ROOT_CAUSE

Matching quests to diagnosed root causes may produce better outcomes than generic room-level recommendations.

Evidence needed: credible matched-versus-generic comparison.

Related: `DEC-0003`, `EXP-0004`.

### LRN-0003: Short Quests May Reduce Initial Participation Friction

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** QUEST

A clearly bounded 15-minute quest may increase first-time completion relative to longer initial commitments.

Evidence needed: starts, completion, quality, and progression by duration.

Related: `DEC-0005`, `EXP-0003`.

### LRN-0004: Cooperative Card Choice May Improve Group Engagement

**Status:** HYPOTHESIS  
**Confidence:** UNKNOWN  
**Domain:** MULTIPLAYER

Allowing participants to voluntarily claim cards may improve group engagement compared with fully assigned tasks.

Evidence needed: participation distribution, completion, abandonment, and feedback.

Related: `EXP-0008`.

### LRN-0005: Sustainment Requires More Than Initial Organization

**Status:** HYPOTHESIS  
**Confidence:** MEDIUM  
**Domain:** SUSTAINMENT

One-time organization is unlikely to be sufficient for durable micro-zone performance without some combination of standards, visual controls, ownership, capacity limits, or reset behavior.

Evidence needed: longitudinal micro-zone outcome data.

Related: `DEC-0004`, `EXP-0009`.

## 33. Verified Learning Registers

### Verified Technical Learnings

#### LRN-0006: The mailing list cannot take a subscriber, and the reason on file was stale

**Status:** SUPPORTED
**Confidence:** HIGH
**Domain:** LIFECYCLE / INFRASTRUCTURE
**Measured:** 2026-09-03

`POST /subscribe` on the live site returns **HTTP 500**, and so does a POST
straight at `http://187.77.25.50:8081/subscription/form`, which rules out our
reverse proxy. The Listmonk container's own log gives the cause:

```
initialized email (SMTP) messenger: info@compassionbenchmark.com@smtp.hostinger.com
error sending opt-in e-mail for subscriber 4: 553 5.7.1 <support@6s-success.com>:
  Sender address rejected: not owned by user info@compassionbenchmark.com
```

**What this overturns.** The note in `site/assets/js/site.js` and
`OWNER-ACTIONS.md` item 7 said the blocker was that the from-address is
Compassion Benchmark. It is the reverse: the from-address is already ours and
the SMTP credential is theirs. Anybody acting on the old note would have
changed the wrong setting. The root URL is still the shipped default
`http://localhost:9000`, which is a second, independent fault.

**Implication.** Listmonk's SMTP block and root URL are instance-wide, so one
instance cannot serve two brands' sending identities. Email capture is blocked
on an owner decision, not on our code, and the fix is in Listmonk's settings,
not in the site.

**Wider lesson, which is the durable half.** A blocker recorded eleven days ago
had drifted from the truth and nothing re-checked it. A stated blocker is a
measurement with a date on it, and it decays like any other.

#### LRN-0007: `quest-first-start` is deployed and has zero events for an honest reason

**Status:** SUPPORTED
**Confidence:** HIGH
**Domain:** MEASUREMENT
**Measured:** 2026-09-03

The analytics database holds no `quest-first-start` rows, which reads at a
glance as "nobody has ever pressed the button on /quest.html". It is not that.
The deployed `quest.js` (checked inside the running container, not in the
repository) is dated **2026-09-02 23:20 UTC**, and the most recent view of
`/quest.html` is **2026-09-02 17:25**. The event has never had a visitor to
fire on.

**Implication.** The 51 of 53 quest sessions that did not finish a card are
still unexplained, and will stay unexplained until traffic arrives. Do not read
the zero as a behavioural finding.

**Wider lesson.** Compare an instrumentation gap against the deploy time of the
instrument before drawing a conclusion from an empty table.

#### LRN-0009: "Source corrected, shipped artifact never re-derived" is a recurring defect class, not a series of unrelated bugs, and it was closeable by audit rather than by waiting for the next accident

**Status:** SUPPORTED
**Confidence:** HIGH
**Domain:** ENGINEERING / RELIABILITY
**Measured:** 2026-09-10/11

`ops/preflight.py`'s `gate_generator_ownership` gate has logged fifteen
separate data points since it was written (GitHub issue #26, then thirteen
more): a real `ops/build_*.py` generator whose committed output nobody was
regenerating and diffing, so a later fix to its source, or to a shared asset
it depends on, could ship stale without anything saying so. Concrete
instances this week alone: six generators silently stripping the
cache-busting fingerprint on a standalone run (`build_zone_pages.py` among
them, the single biggest surface on the site); the live MCP content channel
serving all 114 zones stale for nine days because its own trigger never
fired on the file that actually changed; `build_deck_pdf.py`'s committed
output disagreeing with the copy actually served from `site/downloads/`;
`GOALS.md` itself carrying a retired claim four days after its own
correcting paragraph, three lines below it, said the opposite. Every one was
found the same way: an operator cold-reading one more file and noticing it
by hand.

**What this operator did, rather than log a sixteenth instance.** Globbed
every `ops/build_*.py` file (34 total, 2026-09-10/11) and checked each
against `gate_generator_ownership`'s own ownership chain (21 generators).
The 15 outside it were not a live gap: grepping every other gate's source
for each generator's own filename found that all 15 already had a real,
working gate protecting them a different way (a dashboard-visibility check,
a live count against the corpus, a dedicated byte-compare, a desktop-only
exemption with a documented reason). So the defect class itself is closed
today, for every generator that exists right now.

**The part worth recording as a learning, not just a clean audit result.**
That coverage lived only in fifteen scattered docstrings and one operator's
working notes. Nothing forced a 35th generator, added next week, to declare
its own protection before shipping; the method that found all fifteen prior
instances (a human or agent happening to read the right file) is exactly
the method that would have to find the sixteenth, on no particular
schedule. A lesson recorded in prose here would have described the pattern
correctly and prevented nothing, the same gap `ops/preflight.py`'s own
opening docstring already names about this repository's decisions and
learnings in general.

**Implication.** Fixed structurally, not just documented: `GENERATOR_
PROTECTED_ELSEWHERE` in `ops/preflight.py` now names, for every generator
outside the ownership chain, exactly which gate protects it, and a new
`gate_every_generator_has_a_protection_plan()` fails by name the day a
generator exists in neither list, and fails separately if a cited gate is
ever renamed or deleted out from under this dict. `ops/tests/
test_gate_generator_protection_plan.py` proves both failure modes on a real
planted file, not a hypothetical.

**Wider lesson.** When the same class of defect has already been found and
individually patched more than a handful of times, the next occurrence is
not new information; the absence of a check that would catch the next one
is. `CLAUDE.md` step 10b already says this for a defect found inside one
cycle; this is the same rule applied across a whole week's worth of log
entries that nobody had summed before now.

#### LRN-0011: A re-render gate is only as current as the untracked intermediates it reads

**Status:** SUPPORTED
**Confidence:** HIGH
**Domain:** DATA QUALITY / BUILD
**Measured:** 2026-09-14 to 2026-09-15

`gate_etsy_pdfs_current` re-renders the Etsy PDFs and compares their text with the committed ones. On one workstation it
failed three packs. The rebuild that "fixed" it (`9ff67ac8`) replaced current copy with old copy, because
`build_etsy_assets.py` read `build/products/*.html`, which is gitignored and was stale on that machine. The gate, the rebuild and
the word-level diff all agreed with each other, and all three were wrong, because they shared one stale input. The source of truth,
`content/manual/source/content.json`, held the committed wording the whole time. `0374e09c` made the script regenerate its
intermediates first, and the PDFs came back text-identical to the pre-rebuild versions.

**Implication.** When a gate says generated output is stale, confirm the direction against the source before regenerating: find
one differing sentence and look it up in the source file. An untracked intermediate cannot be trusted to be current, and agreement
between tools that read the same intermediate is not independent evidence.

#### LRN-0014: A conflict in a newest-first file must be resolved by date order, not by marker order

**Status:** SUPPORTED
**Confidence:** HIGH (one file, but the failure recurred twice in a single session and was corrected by another operator)
**Domain:** PROCESS / GIT
**Measured:** 2026-09-16 into 2026-09-17, `ops/NIGHTLY-LOG.md`

`ops/NIGHTLY-LOG.md` states its own invariant in line 3: "One entry per unattended pass, newest first." Every session inserts
at the same anchor, so concurrent sessions collide there constantly. Twice in one session I resolved those conflicts by
stripping the three marker lines and keeping both sides **in the order the markers happened to present them**, which is
`HEAD` first, then the replayed commit. That order is an artifact of who rebased onto whom. It is not chronological, and it
silently violated the file's invariant. A later operator had to spend a cycle on `41486ffe`, "fix entry ordering left wrong by
a rebase conflict resolution", moving an entry back into place.

- Keeping both sides is correct, and remains correct: never resolve a shared log by discarding another session's entry.
- Ordering them by marker position is wrong whenever the two entries carry different timestamps.
- The check is cheap and was skipped: after resolving, read back the `^## ` headings and confirm they descend by date.

**Implication.** For any append-at-top file (`ops/NIGHTLY-LOG.md`, `STATUS.md`), a conflict resolution is not finished when the
markers are gone. It is finished when the entries are in the order the file claims to keep. Verify the headings after every
resolution, the same way a generated file is regenerated rather than hand-picked from either side of a conflict.

#### LRN-0021: nohup and disown do not protect a background job from a process-group signal; only a new session (setsid) does

**Status:** SUPPORTED
**Confidence:** HIGH (reproduced twice, once failing and once passing, same
machine, same command)
**Domain:** ENGINEERING / RELIABILITY
**Measured:** 2026-09-28

"foreground timeout" appears dozens of times in `ops/NIGHTLY-LOG.md`, always
the same shape: an agent runs `python ops/preflight.py` directly, the shell's
own default command timeout fires before the full gate suite finishes, and
the run is discarded and repeated in the background. `preflight.py`'s own
docstring has warned against a short foreground wrapper for a long time. The
warning never stopped the mistake, because a written warning is not a
mechanism, and at least twice it left a generator mid-chain (a copyright page
nearly shipped with an unfilled placeholder) before a human-shaped catch.

The assumed fix, `nohup ... & disown`, was never actually verified against
the failure it exists to survive. Tested directly this cycle: launch
`nohup python ops/preflight.py & disown`, then send the launching shell the
same kind of signal a caller's own timeout sends (`timeout 8 <that shell>`,
SIGTERM to the whole invocation). **The nohup'd, disowned child died anyway.**
`nohup` only blocks `SIGHUP`; `disown` only removes shell job-control
bookkeeping. Neither takes the child out of the caller's process group, and a
timeout (or a harness's own command-timeout enforcement) that signals the
group takes the "detached" child down with it. Rerun with `setsid` in front
of the same command, same kill: the child survived, because `setsid` gives it
its own session and process group, which a group-targeted signal cannot
reach.

**The general rule: "detached" is a claim about *signal delivery*, not about
whether a shell can see the job.** `nohup`/`disown` change what the shell
does to the child on the shell's own exit; they do not change which
process group the child sits in. Only a new session actually isolates a
child from a signal aimed at its parent's group. `ops/run_preflight.sh` now
does this (and also avoids launching a second, concurrent preflight run if
called again while the first is still finishing, the other incident shape
this log records). Any future wrapper meant to survive a caller being killed
should be checked the same way: launch it, kill the launcher with the same
signal shape the real constraint uses, and look at `ps`, not at the wrapper's
own exit code, to see what actually happened to the child.

#### LRN-0022: A fixed threshold is a dated assumption about corpus size, and it fails as a reward for growth

**Status:** SUPPORTED
**Confidence:** HIGH (three instances in five days, same shape each time)
**Domain:** BUILD / QUALITY
**Measured:** 2026-09-25 to 2026-09-29

Three gates failed in one week. None had a defect behind it. In all three a
number that was correct when written stopped describing the thing it was
chosen to describe, because the corpus grew underneath it:

| Gate | Fixed number | What it measured | What had changed |
|---|---|---|---|
| kit-compact-rendered | 340 words per kit block | prose verbosity | a garage holds 18 kit items, a bathroom drawer 10 |
| general-reading | 35 inbound links per article | link concentration | zones linking went 12 to 114 |
| deck-print-tier | 72 cards | print economics | genuinely fixed, correctly kept |

The first two were re-expressed against the quantity that actually varies: 28
words per ITEM, and 40% of the ZONES THAT LINK. Measured after, the busiest
article sits at 34% of zones against an even-spread 22.8, which is a healthy
distribution that a fixed 35 was about to condemn. The third was checked and
left alone, because 18-card print steps really are fixed and eight US Letter
sheets at nine-up really is 72.

**The tell is the failure mode.** A threshold that fails every time the project
succeeds is measuring the denominator. The cost is not the red build, it is
that the obvious response is to raise the number, which teaches everyone to
raise it again, until the check is a number nobody believes and the day the
spread genuinely collapses it says exactly the same thing it said on all the
harmless days.

**Implication.** When a gate fails, ask what grew before asking what broke.
Then decide honestly which kind of number it is: some really are fixed by
physics or by a supplier's price list, and re-expressing those as a ratio would
be the same error pointing the other way.

#### LRN-0023: Text shared by every room must not assume one room, and no equality check can find the assumption

**Status:** SUPPORTED
**Confidence:** HIGH (one instance, but it had shipped to 100 pages and every existing check passed)
**Domain:** CONTENT / QUALITY
**Measured:** 2026-09-29

**Observation.** KC-008 MISSING STANDARD, one of the 17 root causes the whole
product is built on, carried this confirmation test:

> Ask two people what this surface should look like at bedtime.

It rendered on 100 pages: 84 zone pages and every one of the 16 deck pages.
Among them were the garage, the pantry, the workshop and the kitchen. A
household standing in a garage was being asked to picture a surface at
bedtime.

**Evidence.** Found by reading one rendered page out loud while checking a
new room's work, not by any check. Confirmed with `grep -rl` across `site/`:
100 files, of which 99 are rooms nobody stands in at bedtime.

**Why nothing caught it.** Every check that existed compared copies against
each other. `ops/root_causes.py` is the single shared vocabulary, 15 of the
16 deck sources are generated from it, and all 16 decks agreed with it and
with each other. The text was perfectly consistent everywhere and wrong
everywhere, so consistency checking was structurally incapable of finding
it. This is the same defect shape as LRN-0017 (cause IDs assigned from
memory): correct structure, wrong meaning, and only reading it against its
actual use finds it.

**A second finding from the same pass, which was NOT a defect.**
`ops/root_causes.py` claimed its first 12 causes were "copied
character-for-character" from the Kitchen deck so the vocabulary "cannot
silently diverge from the cards already in print". Checked: it was false for
7 of 12, and correctly so. The Kitchen pilot speaks in a kitchen voice
("every time you cook", "the everyday plates", "load the dishwasher
together"); the shared model has to speak to twenty rooms. The claim was
wrong, the code was right. A comment asserting an invariant that nothing
enforces is a claim with a date on it, and this one had expired.

**Implication.** Two different rules are needed, and only one of them is an
equality rule:

1. Generated copies must match their generator (equality, mechanical).
2. Text that is shared across contexts must not name one context
   (vocabulary, semantic).

`gate_cause_vocabulary` in `ops/preflight.py` now holds both, exempting the
Kitchen pilot by name from rule 1's text half while still holding its ids,
titles and six-S entry points. `ops/tests/test_cause_vocabulary.py` proves
it, including a case that restores the exact 2026-09-29 wording and asserts
the real tree fails on it.

**Next action.** When promoting any text into a shared model, read it in the
context furthest from the one it was drafted in. For this product that means:
draft it in a bedroom, read it in the garage.

#### LRN-0024: Read the line ending from what git stores, not from the working copy

**Status:** SUPPORTED
**Confidence:** HIGH (one instance, caught before commit, but it had already produced 1,300 phantom line changes across five files)
**Domain:** ENGINEERING / TOOLING
**Measured:** 2026-09-29

**Observation.** This repository's established in-place edit pattern is:

```python
raw = io.open(FP, encoding="utf-8", newline="").read()
crlf = "\r\n" in raw
...
io.open(FP, "w", encoding="utf-8", newline="").write(out)
```

It reads the newline convention off the **working copy**. `core.autocrlf` is
`true` here, so git rewrites line endings on checkout: a file stored LF in
the repository arrives in the worktree as CRLF. Detecting CRLF there and
writing it back produced a file that differed from the index on **every
line**. Five test files showed `1,322 insertions, 1,305 deletions` for what
were, in truth, five-line edits.

**Evidence.** `git show HEAD:<file> | od -c` showed `\n`; the worktree copy
showed `\r\n`. Converting the file back to LF collapsed the diff from
`240/236` to `6/2`, exactly the intended edit.

**Why it matters more than tidiness.** A whole-file rewrite destroys `git
blame` for the file, buries the real change inside thousands of noise lines
where no reviewer will find it, and makes a later conflict unresolvable by
inspection. It is also invisible in the only place people look: the edit
itself was correct, the tests passed, and `--stat` was the only signal.

**Why the pattern is not simply wrong.** It is right for
`content/manual/source/content.json`, which genuinely is stored CRLF, and
this session used it correctly there all day. The rule cannot be "always
LF"; it has to be "ask the thing that decides".

**Implication.** When rewriting a tracked file in place, take the convention
from `git show HEAD:<path>`, not from the worktree. When that is awkward,
check `git diff --numstat` afterwards: a file whose changed-line count
approaches its total line count has been rewritten, not edited, and that is
true whatever the cause.

**Next action.** Check `--numstat`, not just `--stat`, before every commit
that touched a tracked text file with a script.

#### LRN-0025: At this traffic scale one 20-minute burst can invert a weekly trend, so check concentration before calling direction

**Status:** SUPPORTED
**Confidence:** HIGH (caught before publication; the same signature is present twice in the data)
**Domain:** ANALYTICS / MEASUREMENT
**Measured:** 2026-09-29

**Observation.** A fresh database read gave the trailing week as 14 visitors,
18 visits and 50 pageviews, against 12 / 14 / 27 four days earlier. That is up
on every measure, and it was written into `GOALS.md`, `STATUS.md`,
`BACKLOG-2026-09-07.md`, `OWNER-ACTIONS.md`, `ops/roadmap_report.py` and
`ops/experiments.json` as **"the first reading up on every measure since this
row was created"**.

It was wrong. 30 of the 50 pageviews and 9 of the visitor ids arrived between
18:00 and 18:20 on 27 September: all direct, no referrer, across Windows 7,
Windows 10, Mac OS and iOS. Excluding that single 20-minute bucket the week is
**7 visitors, 9 visits, 20 pageviews**, which is DOWN on 12 / 14 / 27.

**Evidence.** Two queries, neither of which the first pass ran: pageviews per
visitor with their time span, and visitors per 20-minute bucket. The second
shows the top bucket all time is 2026-09-27 18:00 with 9 visitors, and that
three consecutive buckets late on 2026-08-23 hold 6 to 8 each. So the shape
recurs, and a weekly comparison that straddles one of them is comparing a
burst to a baseline.

**What the first pass did wrong, precisely.** It read the aggregate and
believed it. The aggregate was correct: 50 pageviews really did arrive. The
error was inferring a trend from a total without asking how it was
distributed, at a scale where distribution is the whole story. Fourteen
visitors a week means one afternoon is the week.

**A tell that looked strong and was not.** The burst has no country recorded
for any visitor, which reads as datacentre traffic. Checked: country is blank
for all 87 visitors this site has ever had, so it says nothing at all. Worth
recording because it is the shape of a satisfying-but-void signal, and it
would have been quoted as proof if it had not been checked against the
baseline.

**Implication.** Nothing identifies the burst as human, and nothing identifies
it as a bot either; at n=9 the honest answer is that it is unexplained. So
report both numbers, lead with the conservative one, and size experiments off
it: at 7 human-plausible visitors a week, any experiment needing hundreds of
sessions cannot finish here at all, which is a more useful conclusion than the
false rise was.

**Next action.** Before any weekly traffic figure enters a document, run the
per-bucket concentration query alongside the aggregate. If one bucket holds a
quarter or more of the period, report the period both ways.

**Next action closed 2026-09-30, scheduled operator cycle.** The query did not
exist; it had been hand-written twice (23 August and again 27 September) and
would otherwise have to be hand-written a third time. `ops/traffic_query.sh`
now carries it as two standing blocks, run every time anybody reads traffic
from the VPS: the top 10 twenty-minute buckets by distinct visitor count, and
a raw-week-versus-excluding-its-busiest-bucket comparison. Neither block
decides bot or human; both simply surface the concentration so a reader does
the same judgement this learning's own analysis did, without re-deriving the
SQL first. Verified the query logic, not just its syntax, since this sandbox
has no VPS credential to run it against the real database: stood up a local
Postgres 16 with `website_event`/`session` tables shaped like Umami's real
schema, seeded 7 background visitors spread across a week plus the exact
9-visitor/27-pageview/20-minute/four-OS burst shape this learning describes,
and confirmed both queries isolate the seeded burst bucket correctly (9
visitors, all direct) and that the ex-busiest-bucket totals match the
non-burst rows exactly. That is evidence the logic is sound against this
schema; it is not evidence about the live database, which nobody in this
session could reach.

#### LRN-0026: Every instrument must exclude its own operator, because a tool that measures a system also acts on it

**Status:** SUPPORTED
**Confidence:** HIGH (three independent instruments, same defect, found in one cycle)
**Domain:** ANALYTICS / MEASUREMENT
**Measured:** 2026-09-29

**Observation.** Three of this business's measurement instruments were being
filled by the tools that read them. None was broken. Each returned a correct
number about the wrong population.

**1. Stripe's checkout funnel.** A Stripe Payment Link opens a Checkout
Session when its page is merely opened. 420 `<a>` tags across 171 shipped
pages pointed at `buy.stripe.com` with no `rel="nofollow"`, so anything that
follows links could open a checkout. 12 sessions were created on 2026-09-15,
a day the site recorded zero `buy-click` events. "Sessions created versus
paid" is the only conversion instrument here that does not need Search
Console, and it held rows nothing could attribute.

**2. The access log's redirect count.** The three most requested paths on the
whole site were ours and all 301s: `deploy_freshness.py` asked for the
`.html` form of a zone page about twelve times an hour (2,270 in eight days)
because it built the URL from the local filename. Our own monitoring
generated roughly 94% of the redirects in the log, so "Googlebot: 36
redirected" could not be read as a number about Googlebot.

**3. The crawl report's own largest bucket.** Of 75,590 requests over eight
days, **58,247 were this repository**: `6s-freshness` 16,441, the compose
healthcheck's wget 8,746, `6s-linkcheck` 3,721, `6s-dashboard` 2,970,
`6s-success-indexnow` 1,803. None matched any pattern in the report's
classifier, so all of them counted as "human or unknown", the bucket a reader
is most likely to mistake for an audience. It printed 78,295 of them against
a measured 48 real visitors in thirty days. After the fix the same window
reads 58,247 own tooling and 13,986 human or unknown.

**Why none of them looked wrong.** Every one passed its own checks. The
payment links were live and every gate about them was green. `urllib` follows
a 301, so the freshness probe always succeeded. The crawl report parsed every
line it was given. This is not a class of bug that shows up as an error; it
shows up as a plausible number, and a plausible number is worse than a
missing one because nobody investigates it.

**Implication.** An instrument that observes a system it also touches must
name and subtract its own traffic, and that exclusion is part of the
instrument, not a later refinement. Concretely, for anything added here:

- give every automated client a user agent that identifies it as ours, and
  register it in `ops/crawl_report.py`'s `BOTS` table in the same commit;
- never let a monitoring probe request a URL that redirects;
- never hand a crawler a link that creates state on a third-party system.

**Next action.** When adding a measurement, ask what fraction of the thing
being measured the measurement itself produces. If the answer is unknown, it
is not yet an instrument.

#### LRN-0027: On a shared main, one red build strands every change made near it, and the tooling will tell you to keep retrying

**Status:** SUPPORTED
**Confidence:** HIGH (one full instance, traced end to end, with the tooling's own advice measured as wrong)
**Domain:** ENGINEERING / DELIVERY
**Measured:** 2026-09-30

**Observation.** A site change was committed, pushed and merged. It never
reached a customer, and every tool in the repository said something true
while none of them said the useful thing.

The sequence:

1. The change touched `site/**`, so `publish-image.yml` fired.
2. That run FAILED, on a misordered `ops/NIGHTLY-LOG.md` entry in a
   concurrent session's commit. Nothing to do with the change.
3. The upstream fix for the log touched no `site/**` path, so the workflow's
   path filter correctly declined to rebuild.
4. Result: a merged, green-on-`Checks` site change with **no published image
   at all**. Not a stale image. None.

**What each tool said.** `deploy_freshness.py`: STALE, "work committed since
then is not reaching anybody", which invites exactly one move. `deploy.py`:
production is serving a different build, "usually the image has not finished
publishing: check `gh run list`, then run this again." Both true. Both point
at deploying, and deploying pulls `:latest`, which did not contain the change.
Following that advice loops forever.

**Why the path filter is not the bug.** Filtering the image build to
`site/**`, `Dockerfile` and itself is correct: `ops/` is not in the image and
rebuilding for a docs commit would be waste. The failure is the interaction,
not the filter. A trigger that only fires on change, plus a build that can
fail for reasons unrelated to the change, equals work that can be stranded
with no event to notice it.

**Implication, and the general shape.** Any pipeline where the build trigger
is edge-triggered on a path, and the build can fail for reasons outside that
path, can strand work silently. The fix is not to widen the trigger; it is to
make the tools distinguish four states rather than assume one:

    building  wait
    ready     the image exists; a mismatch is registry or pull lag
    failed    retrying will NEVER help; fix the build or dispatch
    none      no run covers this commit; dispatch one

`ops/deploy.py` and `ops/deploy_freshness.py` now both ask GitHub and say
which, from one shared implementation, with "unknown" kept separate from
"none" because "I could not look" is not "nobody built it".

**A second-order point worth keeping.** This is the fourth distinct mechanism
behind `BLOCKER-001`, after "nobody ran the deploy", "the deploy ran against
a stale build id", and "the sitemap advertised pages production did not
serve". Each was fixed on its own terms and the blocker recurred anyway,
because all four are symptoms of the same missing thing: nothing deploys
automatically. `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) closes
three of the four. It does not close this one, which is why this learning is
worth recording separately rather than folded into that item.

**Next action.** When a change does not reach production, establish whether an
image exists before doing anything else. The tools now answer that without
being asked.

#### LRN-0028: A generated image can be good and still wrong, and the reviewer's first instinct is aesthetic

**Status:** SUPPORTED
**Confidence:** MEDIUM (two images reviewed directly, on top of LRN-0012's 92)
**Domain:** MEDIA / QUALITY
**Measured:** 2026-09-30

**Observation.** Seven entryway card heroes are rejected and render a
text-only concept panel instead. The gate watching them says reviewing
replacements needs the Gemini vision billing in `OWNER-ACTIONS.md`. That is
true of the automated reviewer and not true of the question: an operator with
vision can look. So the unreviewed candidates on disk were looked at directly
rather than inherited as verdicts.

EE-002 is meant to show four wet umbrellas in a stand. The candidate shows one
open umbrella balanced on a side table, against roughly 70% blank wall, and an
umbrella open indoors is the opposite of the "tidy and settled" the card
promises. Easy call.

EU-002 is the one worth writing down. The candidate is a genuinely good
photograph: two wall-mounted hook rails, coats and scarves hung straight, two
bags, a small side table with books, warm light, no text, no mangled geometry.
My first judgement was "this is good". Then I read what the card is for: **a
wall calendar, key hooks and labelled letter slots.** None of those three is
in the frame. It is an attractive photograph of a different micro zone.

**Implication.** The failure mode is not that bad images pass; it is that good
images of the wrong thing pass, because aesthetic quality is what the eye
reports first and subject match takes a deliberate second step. This is
exactly the gap `ops/accept_image.py` was built for, and its own docstring
says so: a checklist "derived mechanically from the same record that prints a
card", "answered as closed yes/no questions, so a generated image cannot pass
while contradicting the content it illustrates".

I had that tool available and judged by eye first anyway. Read the card's
subject BEFORE opening the image, not after.

**It also confirms LRN-0012 rather than softening it.** The local model keeps
producing a plausible room and dropping the named objects. Both candidates
examined are correctly rejected, so the stock on disk cannot close this gap
and `gate_deck_download_has_art`'s "the first half needs no decision and no
spend" understated the cost. At 3 of 12 acceptable for cards, seven
replacements is roughly 28 generations; the gate now says so.

**Next action.** When reviewing generated art, open the record first and write
the required objects down, then look. If the image is good but the objects are
absent, it is a reject, and the note should say "wrong subject" rather than
"aesthetic", because those two send the next generation in opposite
directions.


#### LRN-0029: The query half of Search Console is public, and nobody had looked; the complaint our product answers has no page

**Status:** SUPPORTED
**Confidence:** HIGH (measured directly, 274 attempts, 0 errors, both canaries clean)
**Domain:** SEO / AEO
**Measured:** 2026-10-01

**Observation.** For a month `GOALS.md` carried the line "what we still cannot
see is impressions and queries, and that needs Search Console", and treated
both halves as equally blocked on the owner. Only one half was. Search Console
is the only source for OUR impressions. What PEOPLE TYPE is public: Google and
Bing both answer their autocomplete endpoints with no key, no account and no
referrer check, and in six weeks of SEO work nothing in this repository had
ever queried them. Every search term the site targets was invented by reading
the Micro Zone Manual.

**Evidence.** `ops/keyword_demand.py`, first run 2026-10-01: 137 seeds built
from the real corpus (20 rooms times 4 intents, plus the 60 hand-written zone
search terms), 274 attempts across both engines, 0 errors, 36 seeds with
genuinely no completions, both canaries clean before and after, 2,622 distinct
queries. Scored against every published page title: 346 covered, 1,562
partial, 714 with nothing of ours titled for them.

**What the gap actually is.** Not thin content and not a technical fault. The
complaint cluster, how somebody searches before they have decided that
organising is the answer, is 49 queries and **zero** covered. "why is my
kitchen always messy", "why is my kitchen always a mess", "why is my bedroom
always messy" and "why your home is always messy" are all rank-1 suggestions;
the closest page we publish is the articles index. This business has 17 shared
root causes and 114 diagnosed zones built precisely to answer that question,
and no page stands in front of it. Two more clusters are also 0 covered: the
"small space" modifier (153 queries) and "cheap, budget, DIY" (98).

**The second finding is about the instrument, not the data.** The first
version of the harvester counted an empty HTTP 200 as a failure, and voided its
own first clean run: "why is my entryway always messy" genuinely has no
completions. A refusal and a genuine zero are byte-identical in one response,
so they cannot be told apart inside one, only across a run. The fix is a canary
phrase whose completions are not in doubt, fetched before and after, plus
separate ceilings for the error rate and the empty rate. Without it the tool
would have had exactly the property this repository keeps getting hurt by: on
the day an endpoint started refusing us it would have written "demand
collapsed" and exited 0.

**Implication.** Before recording an instrument as owner-blocked, check which
half of it is. A gate on the owner's calendar is not the same thing as a gate
on the information, and here the cheaper half had been sitting in public for
six weeks.

**Next action.** Put a page in front of the complaint cluster, grounded in the
root causes we already diagnose rather than written to the query, and link it
to the room pages. Re-harvest monthly, not weekly: autocomplete moves slowly
and the report is for choosing work, not for watching a number.

**Corrected the same day, and the correction matters more than the finding.**
The page shipped, and re-scoring the same 2,622 queries afterwards exposed that
the instrument had been measuring something narrower than it was being read as.
It scored a query against page TITLES only, so a page answering a question
properly under its own `<h2>`, with an id, read as a gap. Reading headings as
well as titles moves the whole corpus from **714 gaps to 226**, before this
cycle wrote anything at all, and moves the complaint cluster from 0 covered to
8. The decomposition, measured three ways rather than argued:

| Reading | Whole corpus, 2,622 queries | Complaint cluster, 53 |
|---|---|---|
| titles only, before the article | gap 714, covered 346 | gap 21, covered 0 |
| headings too, before the article | gap 226, covered 970 | gap 3, covered 8 |
| headings too, with the article | gap 223, covered 982 | gap 1, covered 17 |

So two things are true at once and both belong in the record. The article is a
real addition: it took the cluster from 8 covered to 17 and is the only page on
this site titled for the question. And **"49 queries and zero covered" was
partly an artifact of my own scorer**, which had already been described in this
file as evidence strong enough to choose work from.

**What stopped it being expensive.** The decision to write ONE page rather than
eight. A per-room page for each of "why is my kitchen always messy", "why is my
bedroom always messy" and the rest would have been eight thin pages built on a
number that was 60% measurement error, and `CLAUDE.md` section 11 is the only
reason that did not happen. The policy was load-bearing in a way its own
justification did not anticipate.

**Implication, and it is the general one.** A measurement being conservative
does not make it right. A strict scorer fails safely in the sense that it never
claims coverage that is not there, and it fails expensively in the other
direction, by commissioning work that did not need doing. Before acting on a
gap count, check what surface the instrument actually looked at.

**Next action, revised.** The honest remaining target is 223 gaps, not 714, and
the next cycle should start from `ops/KEYWORD-DEMAND.md`'s regenerated table
rather than from this file's first paragraph. `matched_on` in the JSON says
whether each row was earned by a title or a heading, and a row earned only by a
heading is weaker evidence of coverage than one earned by a title.

**Confirmed independently the same day:** this sandbox has no network egress to either Google's/Bing's autocomplete endpoints (a direct probe returned `403 Forbidden` from the proxy) or the live site, so `ops/indexnow.py --submit` for the new page and any re-harvest both stay open for a session with live network reach, not a measurement gap in the page or the data.

#### LRN-0030: A test that shells out must prove its interpreter, or the environment answers in place of the code

**Status:** SUPPORTED
**Confidence:** HIGH (reproduced, root-caused, and fail-then-pass proved)
**Domain:** ENGINEERING / TOOLING
**Measured:** 2026-10-01

**Observation.** `ops/tests/test_run_preflight_exit_code.py` reported one red
line in a full preflight run. The red line was not the finding. The test drives
the real `ops/run_preflight.sh` through `subprocess.run(["bash", variant])`,
and from Python on this machine the bare name `bash` resolves to Windows' own
`System32/bash.exe`, the WSL launcher, which answers every invocation with
"Windows Subsystem for Linux must be updated" in UTF-16 and exits 1. The shell
script never ran at all.

**Why that was worse than the red line.** Two of the test's three dynamic
cases assert exit code **1**, and WSL's own refusal exits 1. So both were
passing, and would have passed against a `run_preflight.sh` deleted from disk.
Only the third case, the one asserting 0, was honest enough to go red. A test
file written specifically to catch a wrapper that reports success on a real
failure had itself become a check that could not fail, in two cases out of
three, for an entire environment.

**And the fix uncovered a second layer.** Once a real bash was found, the
script ran and died on `setsid: command not found`: Git Bash for Windows ships
`nohup` but not `setsid`, which the wrapper needs to launch at all. The right
answer there is not to relax the assertion but to establish the missing
capability up front, before any case runs, so it can never be used afterwards
to explain away a case that failed for a real reason. The file now prints NOT
VERIFIED and exits 0, which `gate_tests()` already counts as unchecked rather
than passing, and the one case that is still meaningful here, a static read of
the committed script, still runs and was proved to bite by planting the exact
2026-09-30 regression back into the wrapper.

**Implication.** An assertion on a nonzero exit code is only about the code
under test if the interpreter is known to work. Any test that shells out should
round-trip a known string through its interpreter, and probe for the tools the
thing under test needs, before it believes any exit status. The same shape is
worth looking for wherever a test asserts failure rather than success, because
that is the direction in which a broken environment is indistinguishable from a
passing check.

**Next action.** When a test reports FAIL, read what it actually executed
before fixing what it claims to be about. This one would have been "fixed" by
adjusting an assertion, which would have deleted the only honest case of the
three.

#### LRN-0031: Publishing a measurement to a shared main is itself a work assignment, and two sessions will take it

**Status:** SUPPORTED
**Confidence:** HIGH (observed directly, two independent implementations within hours)
**Domain:** PROCESS / COORDINATION
**Measured:** 2026-10-01

**Observation.** This cycle took the first demand reading this business has
ever had, found that the complaint cluster was 49 queries with zero covered,
wrote that finding into `GOALS.md`, `BACKLOG-2026-09-07.md` and a commit
message, and pushed. A few hours later a concurrent session had independently
written its own article for the same cluster, at the same slug, and pushed it
first. Both were real work. One of them had to be thrown away.

**Why the existing rule did not prevent it.** `STATUS.md` section 0 tells a
session to claim shared work before starting it, and lists generators, gates,
operating documents and workflows. A new article is none of those, and the
claim is written for the moment work *starts*. The collision here began
earlier than that, at the moment a finding was published. A well-argued "here
is the gap and here is what should fill it", pushed to a branch other sessions
read at startup, is the most persuasive work assignment in the repository, and
it carries no indication of whether the session that wrote it intends to do it.

**What it cost, and what it did not.** Nine hours of duplicated authoring on
one side. It did not cost quality: the two pages had different strengths, the
surviving one took the other's better FAQ wording, and the result is better
than either. That is luck rather than process, because the ordinary outcome of
this shape is a merge fight or a second page at a second slug, and a second
page aiming at one query cluster is the duplicate-content pattern `CLAUDE.md`
section 50 forbids.

**Implication.** A finding and an intention are different things and a shared
branch cannot tell them apart. Publishing an unclaimed gap is publishing a
job.

**Next action.** When a cycle records a gap it intends to close itself, claim
it in `STATUS.md` in the same commit that records the finding, not when the
work starts. When it records a gap it does not intend to close, say so
explicitly, because that is the more useful signal and it is currently never
given.


#### LRN-0032: A stored coverage status is a snapshot of a corpus other sessions are changing; re-score before concluding

**Status:** SUPPORTED
**Confidence:** HIGH (the same error, caught twice in two days, once before acting and once after)
**Domain:** ANALYTICS / MEASUREMENT
**Measured:** 2026-10-02

**Observation.** `ops/keyword-demand.json` stores a `status` per query: gap,
partial or covered. That status is not a property of the query. It is the
result of scoring the query against the site **as it was at the moment of the
harvest**, and on this repository the site changes several times an hour
because more than one session is working on it.

Reading the stored file on 2026-10-02 said the "cheap, budget, DIY" cluster was
121 queries with **zero** covered, which is a striking enough number to build a
page on. Re-scoring the identical queries against the corpus as it actually
stood returned **29 covered and 9 gaps**. A concurrent session had added a
room-by-room budget section to `more-storage-wont-fix-clutter` in the interval.
Acting on the stored number would have produced an article duplicating one that
already existed, which is precisely the collision LRN-0031 records, reached by a
different route.

The same correction applied to "small spaces": stored 50 covered, re-scored 82.

**Why this is not the same learning as LRN-0029.** That one was about the
instrument being wrong in its design, reading titles and not headings. This one
is about a correct instrument's output going stale between being written and
being read. Fixing the scorer did nothing to prevent it, and the second failure
happened the day after the first was fixed.

**Implication.** Any stored result that was computed against a moving corpus
carries an implicit "as at" that its own field names do not show. `status` looks
like a fact about the query and is a fact about a moment.

**Next action.** Re-score before concluding, which costs seconds because
`score_rows()` is pure and the inventory is read from disk. The harvest itself,
which is the expensive part and the only part that needs the network, does not
need repeating to do this. Consider renaming the field, or recording the commit
the scoring ran against, so a reader sees the staleness instead of having to
remember it.

#### LRN-0033: An ad-hoc pattern that matches nothing looks exactly like a true absence

**Status:** SUPPORTED
**Confidence:** HIGH (three occurrences in one session, one of which nearly changed the home page)
**Domain:** ANALYTICS / MEASUREMENT
**Measured:** 2026-10-02

**Observation.** This repository gates its tools heavily and its throwaway
analysis not at all, and the throwaway analysis is what decisions get made
from. Three false zeros in one session, all from one-off patterns typed at a
shell:

1. `grep -c $'
'` reported **0** carriage returns in a file that is entirely
   CRLF. Had that been believed, the conclusion would have been that a killed
   test had planted a real defect in `ops/build_zone_pages.py`.
2. `re.findall(r'href="(articles/[^"]+)"')` reported **0** links from the home
   page to any article, because the href is exactly `articles/` with nothing
   after it and the pattern required at least one character. The conclusion
   drawn from that zero was "the home page links to none of the 32 articles",
   and the action queued was to edit the site's most important page. The real
   answer is that it links to the articles index under the label "Reading",
   and the right action was to do nothing.
3. A `site:` query to one search engine returned nothing on a later attempt,
   which was rate limiting rather than an empty index, and was recorded as
   UNCHECKED only because the tool built that distinction in.

**Why the gates did not help.** Every one of these was a pattern typed to
answer a question quickly, outside any tool, so nothing checked it, nothing
tested it, and no reviewer saw it. `ops/keyword_demand.py` refuses to believe
an empty response because that refusal was deliberately designed in. A line of
`grep` has no such thing.

**Implication.** A zero from an ad-hoc pattern is the least trustworthy number
in this repository, and it is also the most likely to be acted on, because a
zero reads as a clean finding rather than as a failed measurement.

**Next action.** When a quick pattern returns zero, prove the pattern can
return non-zero before believing the zero: run it against a case known to
match. It costs one command. All three of the above would have been caught by
it, and the second one was, which is the only reason the home page was not
edited to fix a problem it does not have.

#### LRN-0034: The tool that writes the code can corrupt it silently, and only a planted defect finds it

**Status:** SUPPORTED
**Confidence:** HIGH (four occurrences in one session, one inside a gate)
**Domain:** ENGINEERING / TOOLING
**Measured:** 2026-10-02

**Observation.** Source in this session is written by passing Python through a
shell heredoc. That transport silently eats backslash escapes, and it did so
four separate times in one day:

1. `"\n"` became a real newline, breaking a string literal. Caught instantly,
   because Python would not parse the file.
2. The same, in a different file. Caught the same way.
3. A commit message's backticked word was run as a command substitution and
   spliced out, leaving `"happened the day after the first was fixed.  looks
   like a fact about a query"`. Caught by reading the commit afterwards, and
   not fixable, because the branch is shared and history is not rewritten here.
4. **A regex written as `r"\b%s\b"` arrived with each two-character `\b` replaced by a single 0x08 backspace byte.**
   This one parsed, ran, passed every time, and produced a regex that can never
   match, **inside a preflight gate**.

**Why the fourth is the one that matters.** The first two failed loudly at
parse time. The third was cosmetic. The fourth produced a check that cannot
fail, in the file whose entire job is checking, which is the defect class this
repository has paid for more than any other. It was invisible to a normal read:
`grep` prints a backspace as nothing, so the line looked exactly right. Only
`cat -A` showed it.

**What actually caught it.** Not review, not the test suite, not the gate
passing. It was planting a defect the gate should have caught and noticing the
gate stayed green. The plant is the detector. Without the habit of proving a
new check can fail, that gate would have been green forever and nobody would
have had any reason to look at it again.

**A related trap from the same hour, worth the same vigilance.** Three separate
plants failed to fail for reasons that had nothing to do with the code under
test: one removed a label the checker already strips, one used
`replace(..., 1)` on a phrase every caption repeats across two cues, and one
chose a post that happened to be short enough to survive the defect. A plant
that does not produce a failure means one of two things, and they are not
distinguishable without looking: the check is blind, or the plant missed.

**Implication.** Treat the code-writing transport as unreliable. After writing
source through it, verify the bytes rather than the appearance, especially for
regex escapes.

**Next action.** Two cheap habits, both already applied once today. Scan any
file this session rewrites for control bytes before committing it
(`preflight.py` is now verified clean). And when a planted defect does not
fail, debug the plant before concluding anything about the check.
#### LRN-0035: A repeated "needs live network reach" finding is a sandbox property, not a data property, and the fix is a workflow, not another cycle

**Renumbered 2026-10-03, PM check-in:** this entry was recorded as LRN-0032,
the same ID already used above by "A stored coverage status is a snapshot of
a corpus other sessions are changing." Renumbered to LRN-0035, the next free
ID, because the earlier entry is cited by name from working code
(`ops/keyword_demand.py`, `ops/preflight.py`) and two test files, while this
one was cited only from `CHANGELOG.md`, now updated to match. See the new
duplicate-ID check in `check_learnings_index()` (`ops/preflight.py`), added
the same cycle so this cannot recur unnoticed.

**Status:** SUPPORTED
**Confidence:** HIGH (confirmed directly against the proxy, not inferred)
**Domain:** ENGINEERING / MEASUREMENT
**Measured:** 2026-10-02

**Observation.** `ops/keyword_demand.py`'s re-harvest, and `ops/indexnow.py
--submit` before it, were each reported as blocked by multiple separate
operator cycles, on separate dates, with the same wording: no network egress
from this sandbox. `GOALS.md` and `STATUS.md` both recorded the keyword
re-harvest as "unmeasured, and will be for weeks" as though the wait were
intrinsic to the measurement. This cycle confirmed the refusal directly (a
`connect_rejected` from the egress proxy against both `6s-success.com` and
Google's own autocomplete host) and then asked the next question nobody had:
is there anywhere in this repository's own infrastructure that already has
real network access and could run this instead? `hourly-brief.yml` already
answered yes for IndexNow, months earlier, and nothing generalised that
answer to the newer tool.

**Why the existing rule did not prevent it.** `CLAUDE.md` 0.2 says not to
report a problem twice that could have been fixed once. Every cycle that hit
this wall was, technically, reporting a *fact* (this session cannot reach the
internet), and each one was true. But the fact being repeated was about the
session, and the fix available was never phrased as "build a way to take this
reading from somewhere that can," because the session doing the diagnosing
could never be the session doing the fixing: it structurally lacks the one
thing the fix needs. A blocker a session cannot personally clear is easy to
mistake for a blocker nobody can clear.

**Implication.** When a recurring finding's blocker is "this environment
cannot reach X," the question to ask is not "can I reach X" (already answered,
repeatedly, no) but "does this repository already run anything, anywhere,
that can," before accepting the wait as structural. `hourly-brief.yml`'s own
IndexNow step was the existence proof the whole time.

**Next action.** `.github/workflows/keyword-demand.yml` now runs the
re-harvest weekly from a GitHub-hosted runner, with `gate_keyword_demand_not_
stale` in `ops/preflight.py` holding it to that cadence. The general form of
this fix, checking whether an existing real-network workflow can carry a
blocked measurement before writing the measurement off as sandbox-bound for
weeks, applies to any future tool that turns out to need the same thing.

#### LRN-0036: Every page on this site is crawled and almost none of it is ranked, so indexation is finished work and not a lever

**Status:** SUPPORTED
**Confidence:** HIGH (first-party server log, every figure counted directly)
**Domain:** SEO / ANALYTICS
**Measured:** 2026-10-03, window 2026-09-19 to 2026-10-03

**Observation.** This repository has spent months on indexation: sitemap
lastmod correctness, www and .html 301s, a `Disallow: /stats/` rule, an
IndexNow submitter with a deploy-aware withholding guard, a weekly keyword
harvest. Nobody had ever asked the question those all serve: how much of this
site do search engines actually fetch, and what do they send back.

**Evidence.** Read from `/var/log/6s-success/access.log*` on the VPS, the
bind-mounted log that outlives a container, across 15 days with traffic and
139,272 requests.

* **Crawl coverage is 210 of 211 sitemap URLs, with exactly one never fetched.**
  The one is `/articles/why-is-my-house-always-messy`, published 2026-10-02 and
  first announced to IndexNow on 2026-10-03; its whole fetch history is this
  repository's own tooling, one curl and one browser. Everything else on the
  site has been read by a retrieval crawler inside the window.
* **Corrected before publishing, and the correction is the same lesson as
  LRN-0033.** This bullet first said 211 of 211 from a hand-written
  `grep | awk | sort -u` over the log. `ops/crawl_report.py`'s own
  `sitemap_coverage()`, added the same hour, said 210 of 211 and named the page.
  The ad-hoc version matched a looser bot set and looser path variants and so
  reported full coverage that did not exist. A throwaway pipeline gets no
  second opinion; the tool does, so the number now lives in the tool.
* **Googlebot content fetches run 7 to 44 a day, mean about 19, for fourteen
  consecutive days.** Per day: 7, 28, 8, 8, 8, 44, 20, 16, 16, 25, 24, 19, 12,
  26. Assets and the analytics beacon excluded.
* **That is roughly a tenfold rise on the baseline LRN-0013 recorded**, which
  was 0 to 2 a day through 10 to 19 September with occasional recrawl bursts.
  LRN-0013's own correction is the reason this one is worth writing: it called
  a two-day rise "sustained" and had to retract it four days later. Fourteen
  consecutive days with no day below 7 is a different claim from two days.
* **Search engines sent 6 requests from something that was not a bot, in the
  same 14 days.** Five distinct days; four landed on `/`, one on
  `/articles/why-you-keep-buying-things-you-already-own`, one on `/shop.html`.
  The crawl report's own referrer section agrees at 9 Google referrers and 1
  Bing, counting assets.
* Also in the window, and worth separating from discovery: ClaudeBot 186 and
  GPTBot 42 fetches are training traffic, which is a licensing event rather
  than a route to a reader; Bingbot 458 and OAI-SearchBot 55 are retrieval.
  PerplexityBot does not appear at all.

**Learning.** The crawl half of organic discovery is done and has no headroom
left. A page cannot be fetched more completely than all of it, and more
submission, more sitemap precision and more IndexNow cannot improve a number
that is already 210 of 211, with the one exception being a page published the day
before. The site is all but fully crawled and effectively unranked:
every page is read by the engines and the engines send about three requests a
week to a human. That is not a discovery problem, it is a ranking problem, and
on a domain almost nothing links to, ranking is bought with authority and time
rather than with on-page work.

**Implication for prioritisation.** Three classes of work are now known to have
no remaining headroom and should not be picked up again without new evidence:
submitting URLs, improving sitemap mechanics, and widening crawl access. Two
classes remain honest: matching real intent on pages that already exist (which
`ops/keyword-demand.json` can at least point at), and distribution that does
not route through a search engine at all, which is what `GOALS.md` has said is
the constraint since 2026-09-02 and what `OWNER-ACTIONS.md` is mostly about.

**What this does not say.** Nothing here measures impressions or position,
because Search Console is still verified to nothing (`OWNER-ACTIONS.md` 1a).
"Crawled" is not "indexed": a fetch proves an engine read the page, not that it
kept it. A user agent is also a claim and this log records no addresses by
design, so every bot count above is "requests from something calling itself X".
Spoofing would inflate them and nothing here detects it. The 6 search-referred
requests are a referrer header, which the client chooses.

**Next action.** None of the above changes what to build next, which is the
point: it removes a tempting direction rather than adding one. Re-read the same
log in two weeks before claiming the crawl rise has held, because LRN-0013 is
the standing warning about exactly that. `ops/crawl_report.py` now prints
the sitemap coverage line itself (`sitemap_coverage()`), so this number is
re-derivable on demand rather than remembered, and it is what caught the
ad-hoc version's error above.
#### LRN-0037: A number is only as protected as the thing protecting it, and ours was protected by somebody else's bot list

**Status:** SUPPORTED
**Confidence:** HIGH (counted in the site's own access log, both sides compared)
**Domain:** ANALYTICS / MEASUREMENT
**Measured:** 2026-10-03, window 2026-09-19 to 2026-10-03

**Observation.** Looking for something else entirely (whether the analytics
beacon still fires after a measure.js change), the access log showed hundreds
of POSTs a day to `/stats/api/send` while Umami recorded 1 to 11 pageviews a
day for this site. Two orders of magnitude apart, on the one metric every
objective here is measured against.

**Evidence.** 9,113 of the beacons in the window carried a HeadlessChrome user
agent, counted by extracting the agent field rather than by sampling: 7,950
from HeadlessChrome/153 and 1,163 from /154, both the Edge-derived build this
workstation's tooling drives. They are this repository's own screenshot and
visual-audit scripts, which run a real Chromium and therefore execute the
tracker on every page they load. The remainder are mostly
`meta-externalagent` and `YandexRenderResourcesBot`, which also execute
JavaScript.

**No reported figure was ever wrong.** Umami discarded all of them. That is
the part worth sitting with: the measurement was correct, and it was correct
for a reason nobody here chose, documented or tested. Umami's bot list happens
to recognise the string HeadlessChrome. One upstream change to that list, or
one tool configured with a friendlier user agent, and 9,000 of our own
pageviews would have landed in the only traffic figure this business has. At 7
to 22 visitors a week the constraint would have appeared solved overnight, by
our own monitoring, with nothing in the system able to say otherwise.

**Learning.** When a measurement survives only because an external component
happens to behave well, it is not protected, it is lucky. The test is not
"is the number right today" but "what in OUR system would stop it being wrong".
Here the answer was nothing. This generalises past analytics: the same shape is
a price that is only correct because an upstream default has not changed, or a
gate that passes only because a dependency still emits the string it greps for.

**Action taken.** `site/nginx/default.conf` now returns 204 for a beacon whose
user agent contains Headless or starts with `6s-`, before `proxy_pass`, so the
refusal is ours and is visible in the file that serves the site.
`ops/tests/test_nginx_beacon_guard.py` compiles the guard's own pattern and
runs it against the five agents measured hitting the endpoint and four real
browser strings, so it fails both if the guard stops catching our tooling and
if it ever starts catching a visitor. Proved in both directions with planted
defects.

**What this does not say.** It does not mean past traffic figures were
overstated; the opposite, they are now corroborated from a second, independent
source. It also does not clean the historical log: the 9,113 lines remain in
the access log for the window before the guard, so any future crawl or traffic
analysis over September must still exclude them, which is what
`ops/crawl_report.py`'s `6S own tooling` bucket is for.

**Next action.** None outstanding. The honest follow-up is to re-read
`/stats/api/send` by user agent after the next deploy and confirm the
HeadlessChrome 200s have become 204s, which is a before-and-after this log can
answer on its own.
#### LRN-0038: A page our domain serves is our page, whoever renders it, and the checker watching it was asserting the defect was present

**Status:** SUPPORTED
**Confidence:** HIGH (the page was fetched and read; the access log was counted)
**Domain:** TRUST / PRIVACY
**Measured:** 2026-10-04

**Observation.** `https://6s-success.com/subscribe` was proxied to Listmonk's
public subscription form. Read rather than pattern-matched, that page rendered
three list checkboxes with every one pre-ticked, and two of them belonged to a
different business sharing the Listmonk instance. A visitor who submitted it
subscribed himself by default to two lists from a company he had never heard
of. `CLAUDE.md` section 8 forbids a pre-ticked consent by name; section 47 says
sharing must be intentional.

**Evidence.** Three checkbox `<label>` elements in the live HTML, all with
`checked="true"`: Compassion Benchmark Weekly Digest, Compassion
Benchmark Product and Research Updates, 6S Success Readers. Of 549 requests to
that path in the whole retained access log, 547 are this repository's own
`ops/check_integrations.py` probe and 2 are `curl`: no crawler, no visitor, zero
POSTs ever, 0 subscribers on the list, no internal link, no sitemap entry.

**Learning, first half.** The boundary of responsibility is the domain, not the
codebase. Nothing in `site/` was wrong; `site/assets/js/site.js` was careful
enough to state in a comment that nothing here pre-ticks a consent, and that was
true of the form it wrote. The defect was four lines of `proxy_pass` handing a
URL on our domain to a service whose output nobody had looked at since the
instance became shared. Anything served under our name is ours to read, however
it is produced.

**Learning, second half, and the more useful one.** `ops/check_integrations.py`
had been reporting that page as a HEALTHY integration for weeks. Its test was
whether the body contained the word "subscribe" and an `<html>` tag, which the
defective page satisfied perfectly. So the check was asserting the defect was
present and calling it green, and the greener it looked the less likely anybody
was to open the page.

That is not the familiar shape where a check cannot fail. It is worse: this one
could fail, and failing meant the defect had been REMOVED. The general form to
watch for is a check whose pass condition is satisfied by the thing going wrong,
which happens whenever a check tests "is the service reachable" for a service
whose reachability is the risk. The fix was to invert it: our domain must not
serve another business's consent checkboxes, and a 404 is the correct answer.
It was then run against production BEFORE deploying the fix and FAILED, naming
both foreign lists, which is how an inverted check earns belief.

**One guard built deliberately in both directions.** A rule saying "no
subscription surface" would forbid the very thing this business needs next
(`GOALS.md` O2, email capture). `ops/tests/test_no_foreign_consent_on_our_
domain.py` and the checker both PASS a page that lists only our own list, and
that case exists precisely so the guard cannot block its own fix. The first
version of that test was itself unable to fail: it matched `proxy_pass` at four
leading spaces when every one in the file sits at eight, so a restored route
reported OK. Only a planted defect found it.

**Next action.** None outstanding; the route is gone, verified 404 live, and the
prerequisite for email capture is unchanged (a 6S-only surface,
`OWNER-ACTIONS.md` item 7). The transferable habit is the one this entry is
really about: when a check reports a third-party surface as healthy, read the
surface once. The check is reporting on reachability and calling it correctness.
#### LRN-0039: Three gates checked what the message said, and none checked that it was sent

**Status:** SUPPORTED
**Confidence:** HIGH (the absence was grepped for across the whole repository)
**Domain:** PROCESS / RELIABILITY
**Measured:** 2026-10-10

**Observation.** `ops/send_questions.py` is the email that asks the owner to
do the things only he can do. Every lever on arrivals sits behind an item in
it and all nine open GitHub issues are labelled `decision` or
`blocked-on-art`, so it is the narrowest point in the whole business. Nothing
in `.github/workflows` referenced it. It was sent by whichever scheduled
Routine happened to run.

**Evidence.** A repository-wide grep for the script name returns the script,
three backlog entries, a nightly-log line saying it was "last sent 09:50
today", and no workflow. Meanwhile `status-email.yml` and `hourly-brief.yml`
are real workflows with real schedules. So when the Routines went dark
2026-10-04 to 2026-10-09 on `USAGE_LIMIT_REACHED` (INCIDENT-002), the hourly
status email kept arriving and the one that asks for the unblocking did not.
Five days.

**The sharp part.** Three gates already guarded that email:
`gate_send_questions_current`, `gate_send_questions_covers_top_owner_actions`
and `gate_no_frozen_deck_link`. They are good gates with a real track record:
between them they caught a false "deploys are automatic" claim, a list that
had never been told about two of `OWNER-ACTIONS.md`'s own top three items, and
a frozen link to an eleven-day-old artifact. Every one of them inspects the
CONTENT. Not one could tell whether the message left the building.

**Learning.** For any artifact whose purpose is to reach somebody, correctness
and delivery are two different claims and they need two different checks. A
stack of content gates produces a strong feeling of coverage precisely because
it is thorough about the half it looks at. The question to ask of a report, an
email, a webhook or an alert is not only "is what it says true" but "what in
this system would notice if it stopped arriving". Here the answer was nothing,
and the thing it was reporting on was the reason the business was stalled.

**The generalisation worth keeping.** A dependency that is invisible in the
repository is still a dependency. This email depended on an agent Routine, and
that dependency appeared in no file: not in a workflow, not in a runbook, not
in the gate list. The channel and the thing that was broken shared a single
point of failure that nothing had written down.

**Action taken.** `.github/workflows/owner-questions.yml` sends it weekly from
GitHub's schedule, independent of any session.
`send_questions.py --send` now writes `ops/last-owner-questions-sent.json`
after `send()` returns, so a failed send leaves the last honest timestamp
rather than claiming a delivery. `gate_owner_questions_not_stale` warns past
10 days, or on a missing or unparseable record, and reported UNKNOWN honestly
until the first real send. Fired for real the same day: message id recorded,
record committed, gate clean.

**Next action: none, because it was asked the same hour rather than written
down as a to-do.** Every owner-facing sender in `ops/` was checked for both a
workflow and a delivery record. `status_pdf.py` (`status-email.yml`) and
`hourly_brief.py` (`hourly-brief.yml`, record `ops/last-brief.json`) both have
a workflow; `send_questions.py` now has both. The only sender without one is
`ops/send_brief.py`, and `preflight.py` already calls it "the unused sibling"
in its own gate, so wiring it up would be delivering something nothing wants.
`owner_inbox.py` and `inbox_agent.py` read mail rather than send it, so a send
record does not apply. There is no remaining owner channel whose delivery
nothing can see.

#### LRN-0040: "No browser in this sandbox" is a per-container fact, not a standing one, and it was being treated as the latter

**Status:** SUPPORTED
**Confidence:** HIGH (confirmed by direct execution, not inferred from absence)
**Domain:** ENGINEERING / TOOLING
**Measured:** 2026-10-10

**Observation.** Dozens of `ops/NIGHTLY-LOG.md` entries across the past month
report `gate_tests` "hitting its documented sandbox hang" or `audit_visual.py`
needing "a real browser" it does not have, written as though the absence were
a fixed property of this operating environment. This cycle's own `ops/cold-
read-ledger.json` entry for `audit_visual.py`, dated 2026-09-30, says flatly
that "python ops/audit_visual.py and even --help hang past 120s needing a
real browser." Checked directly rather than carried forward: `ops/browser.py`
`find_browser()` returned a real, working headless Chromium
(`/opt/pw-browsers/chromium`) in this session. Ran `audit_visual.py` against
a live page: it completed in well under a minute with real findings, not a
hang. A full `preflight.py --fast` run the same cycle ran `gate_tests` to
completion, all 392 test files executed, 0 failed.

**Why the existing rule did not prevent it.** Each cycle that hit the hang was
reporting something true about its own container at that moment. The error
is not in any single report, it is in letting enough identical reports
accumulate into an unstated premise ("this sandbox has no browser") that the
next cycle inherits and stops re-testing, the same shape LRN-0035 named for
network reach. A per-container fact and a structural one produce an
identical-looking symptom from inside a single session, and only checking
the fact itself, every time, tells them apart.

**Implication.** A tool whose failure mode is "this sandbox cannot do X"
should be re-tested directly each time it matters, not cited from the last
cycle that tried, because the container provisioned for this session is not
guaranteed to be the one that failed before and is not guaranteed to be the
one that succeeds next time either. The safe default is to check, not to
assume either direction.

**Next action.** None structural: there is nothing in this repository to fix,
because the absence was never a code defect, and asserting the browser will
always be present here would just be the same mistake pointed the other way.
Worth a standing habit instead: before citing a prior cycle's "no browser" or
"gate_tests hangs" finding, call `ops/browser.py`'s `find_browser()` directly
first, the same discipline CLAUDE.md 0.3 already asks for toward production
state.

#### LRN-0020: When a gate has no available action, the format is usually the thing to change, not the blocker

**Status:** SUPPORTED
**Confidence:** HIGH (14 pages closed, three defects caught by three different checks)
**Domain:** MEDIA / BUILD
**Measured:** 2026-09-27

`page-art` had warned for weeks that pages ship with no image at all: 3 zone
pages whose photographic hero was rejected, and 11 room pages whose book chapter
is unillustrated. Nobody could act on it, because the only fix on offer was to
generate a photograph, and that is blocked twice over: the local model cannot
draw a micro zone (LRN-0012, 0 of 8 acceptable) and the better models need
either RAM this machine does not have or a billing decision only the owner can
make.

The constraint was never the artwork. It was the assumption that the slot had to
hold a photograph. This repository had already worked that out once, for the
films, and written it down in `ops/video_zone.py`: *"A format built from type
needs no imagery at all, so the constraint chooses the format rather than
limiting it."* The same sentence applies to a page, and nobody had connected the
two for a month.

All 14 pages now carry a typographic panel built from text the corpus already
holds, the zone's `done_looks_like` or the room's `intro`, captioned to say
plainly that no photograph exists. Nothing invented, nothing owner-gated.

**The part worth generalising is not the panel, it is what the panel did to the
gates.** Twice, filling the slot made a gate report something false:

- counting the panel as a hero made `gate_image_coverage` read 114 pages
  carrying a photograph against 111 approved images;
- giving the room panel the bare `room-lead` class would have marked all 11
  unillustrated chapters as illustrated and erased the artwork gap
  `OWNER-ACTIONS` 1b exists to track.

Both times the gate was right to object and the fix belonged in the gate, not
in the claim. A stand-in must be legible AS a stand-in to every check that
counts it, or closing the visible gap quietly closes the real one too. The rule:
**when you fill a hole with something honest but different, give it its own
name, and teach every counter the difference in the same commit.**

**Also worth keeping: the three defects, and which check caught each.** A fixed
`width="900"` overflowed a 390px phone, caught by `ops/audit_visual.py` on the
very page the figure was meant to improve. An extra attribute on the `<figure>`
made `FIG` stop matching it, so the replace silently did nothing while the
sweep reported success, and stranded a figure nothing could remove; caught by
looking at the shipped bytes rather than the tool's own output. And the false
photograph count, caught by a gate. Three different checks, three defects, none
of which the other two would have found.

#### LRN-0019: The $29 Manual's body text is not re-derived from the corpus by anything in ops/, so a corpus correction never reaches the product

**Status:** SUPPORTED
**Confidence:** HIGH (traced from a single word through 21 artifacts)
**Domain:** BUILD / PRODUCT
**Measured:** 2026-09-26

Found while verifying the 114 YouTube films were safe to publish. A caption read
"The step of space either side of the burners", which parses as nothing; the
word wanted is "strip". The caption was faithful. The typo was in
`content/manual/source/content.json`, in the Kitchen Cooking Zone's `purpose`.

One word, **21 artifacts**: the zone page, the room page, the zones index, the
Kitchen deck and its page, `quest-data.js`, the mobile quest corpus, three SRT
caption files, the social captions, the YouTube metadata, the image prompts, the
shooting script, and four Manual HTML files including the one customers are
actually sent.

Fixing the corpus and rerunning the generators cleaned every site artifact. It
did **not** clean the Manual. `ops/build_manual_print.py` reads content.json,
passes all its own gates, rewrites all three Manual files, and still emitted the
old sentence, because the `<p class="zpurpose">` body text is not something it
derives. The only script that writes that element from `purpose` is
`content/manual/source/build.py`, which is a local script writing to a hardcoded
Desktop path outside the repository. The tracked Manual HTML is therefore a
frozen snapshot that `ops/` post-processes for fonts and front matter without
ever re-deriving the words.

**Implication.** This is `BACKLOG-2026-09-07.md` section 7's dominant defect
class, "the source was corrected and the shipped artifact was never re-derived
from it", sitting inside the product with the highest price on it. Any future
corpus correction silently fails to reach MZ-MANUAL, and every check passes
while it does. The four files were corrected by hand this time, which fixes the
instance and not the cause.

**Cause closed 2026-09-27, scheduled operator cycle.** Nothing re-derives the
Manual's body text from content.json, so the cause itself cannot be fixed
without rewriting the Manual as a generated document, out of scope for one
cycle. What could be closed cheaply is the silence: a new
`gate_manual_zone_content_current` in `ops/preflight.py` now cross-checks
every zone's `purpose` and `done_looks_like` (the two fields this defect
actually traveled through) against the Manual's own `<article class="zone"
id="...">` blocks, matched by the same room--zone slug
`ops/build_zone_pages.py` already derives, and fails by name on a mismatch
or a missing article. Confirmed clean against the real committed files
first (0 mismatches across all 114 zones, so this was not a live defect
today), then fail-then-pass proved on 7 cases in
`ops/tests/test_gate_manual_zone_content_current.py`, including the real
LRN-0019 shape (a purpose field silently drifting) and a renamed zone id.
The next corpus correction that reaches these two fields but not the
Manual will now fail preflight by name instead of shipping silently.

**That exception was wrong, and chasing it found something much worse.** I first
wrote here that the SRT files should keep saying "step" to match baked narration.
Captions on these films transcribe the ON-SCREEN text, not speech
(`ops/video_srt.py`: "their words are baked into the pixels"), so the fix is to
re-render the film, which I did. It came out **93.2s**. Every other film in the
batch is **30.2s**, to one decimal place, all 114 of them.

So I measured `beats()` for zones I had never edited: Entryway Landing Zone
74.8s, Garage Primary Workbench 74.8s, Pantry Dry Goods Shelves 78.8s. Today's
generator produces films two and a half times longer than the ones on disk.
**All 114 films are stale relative to the script that makes them**, and my
corpus edit had nothing to do with it.

Then the part that matters. The captions are CURRENT and the films are not:

| slug | caption ends | film ends | |
|---|---|---|---|
| entryway--landing-zone | 74.8s | 30.2s | out by 45s |
| kitchen--sink-and-dishwashing-zone | 74.8s | 30.2s | out by 45s |
| garage--primary-workbench | 74.8s | 30.2s | out by 45s |
| kitchen--cooking-zone (re-rendered) | 90.8s | 93.2s | match |

Publishing the batch would put 102 videos on YouTube whose captions run
**forty-five seconds past the end of the picture** and are out of step within
the first few beats. For a deaf viewer that is worse than no captions, because
the words do not correspond to what is on screen.

**Correction to what I told the owner.** I reported the 114 films "verified
ready" and the paste "would work", on the strength of ffprobe: 1920x1080, audio
present, 30.2s, zero problems, all 114. Every one of those statements is true
and the conclusion was still wrong, because I checked each artifact against
itself and never checked two artifacts against each other. A file that is valid
is not a file that is current.

**One more correction, 2026-09-27: the directory I fixed is not the one that
publishes.** `ops/youtube_upload.py` reads `build/video/zones-narrated`, the
~300-second narrated masters with their own `-16x9.srt` tracks. I measured and
re-rendered `build/video/zones-16x9`, the 30-second silent films. Measured
afterwards, the pair that actually ships was already sound: **114 of 114**
narrated masters end within 5s of their own caption track. So the re-render
fixed a real staleness in the silent films and the publish path never had the
defect I reported. Both halves of that sentence matter, and I stated only the
first.

**Resolved the same day, 117 minutes of compute.** All 114 films re-rendered
with today's generator (`ops/video_zone.py` has no batch mode, so a resumable
driver looped it one zone at a time, skipping any film already matching its own
beats). Re-verified across the whole set rather than sampled: **114 of 114**
films measure within 5s of their `beats()` total and carry a video and an audio
stream, and **114 of 114** caption files now end within 5s of the film they
belong to. The films are 75 to 93 seconds now, not 30.

**The generalisable rule.** Every check that passed here compared an artifact
with itself: is the mp4 valid, is the SRT well formed, does the caption match
the beats. The defect lived in the relationship between two artifacts that no
check crossed. When two files must be published together, the test that matters
measures one against the other, and `gate_srt_captions_current` compared caption
to beats, which is why it stayed green for 113 films that were 45 seconds out.

#### LRN-0018: Crawlers fetch by sitemap, not by depth, so content quality cannot be measured in a server log

**Status:** SUPPORTED
**Confidence:** HIGH (206,518 log lines, three cohorts, identical result)
**Domain:** SEO / AEO / MEASUREMENT
**Measured:** 2026-09-24

D-026's checkpoint asked whether personalising a zone changed what answer
engines take. Read across the full Nginx Proxy Manager log, GPTBot had fetched
**every one of the 114 zone pages exactly four times**:

| Cohort | Pages | Fetches | Per page |
|---|---|---|---|
| Authored weeks ago (Entryway, Kitchen) | 12 | 48 | 4.00 |
| Authored the same day | 26 | 104 | 4.00 |
| Not authored at all | 76 | 304 | 4.00 |

Three cohorts differing by thousands of words of added depth, and the crawl is
uniform to two decimal places. A crawler walks a sitemap. It does not read the
page and decide to come back.

**Two things this rules out, and one it does not.** It rules out using crawl
frequency as a proxy for content quality, and it rules out "the crawlers will
find the good pages" as a discovery strategy. It does **not** tell us whether
any of it is quoted, cited or summarised, and nothing in this system can: that
happens inside the model, and a server log cannot see it. If quoting matters,
it has to be tested by asking the engines, not by reading logs.

**The asymmetry looked actionable and is not. Corrected 2026-09-26 after
actually testing it.** Over the same window ClaudeBot made 542 requests and
fetched **zero** zone pages, OAI-SearchBot made 113 and fetched zero, while
GPTBot took all 114 four times and bingbot took 106 of them. I wrote here that
this was "a reachability question with an answer" and "worth more than another
authored room". Both claims were wrong, and the test was cheap:

- `robots.txt` allows everything but `/stats/`, with no AI-specific rule.
- `sitemap.xml` parses cleanly: 196 URLs, zero empty `loc` elements, deck
  pages present. Not a malformed-sitemap fault.
- GPTBot crawls 757 distinct paths using that same robots.txt and that same
  sitemap, which rules out anything about either file.

What the request breakdown actually shows is not a blocked crawler but an
uninterested one. **OAI-SearchBot fetched exactly one distinct path, 113
times: `/robots.txt`.** It has never requested a single page of content.
ClaudeBot spent 309 of its 542 requests, 57%, re-reading `robots.txt` and
`sitemap.xml`.

OAI-SearchBot is a retrieval crawler: it fetches a page when a person's
question makes that page relevant. Asking permission 113 times and never
following up is not a door that is stuck, it is a machine that evaluated this
site and never had a reason to open it. That is the arrivals constraint
restated by a crawler, not a defect to fix in the crawl path.

**Implication, and the reason this correction is worth more than the original
claim.** "Two crawlers cannot reach our content" would have justified days of
crawl-path work. The evidence says the content is perfectly reachable and
nothing is asking for it. Do not spend engineering on AI-crawler reachability
here; the same effort belongs upstream of the constraint, on giving anybody a
reason to look.

**Near miss worth recording.** The first count said zero zone-page fetches for
every crawler including GPTBot, because the path in this log format sits in
quotes after the hostname (`GET https host "/path"`) and the regex expected it
after the verb. A tidy, confident, entirely wrong zero. It was caught only by
asking how many zone-page requests existed from anybody, which returned 30,200.
When a measurement returns zero, measure the denominator before publishing it.

#### LRN-0017: Authoring against an ID vocabulary from memory produces branches that are well formed, real, and wrong

**Status:** SUPPORTED
**Confidence:** HIGH (13 mis-assignments in 13 zones, each verified against ops/root_causes.py)
**Domain:** CONTENT / BUILD
**Measured:** 2026-09-24

Two rooms (Primary Bathroom, Home Office) were authored under D-026 with a
`cause` ID on every diagnosis branch. The IDs were assigned from a remembered
sense of what each one meant, because they read as self-describing. Checked
against `ops/root_causes.py` afterwards, 13 branches were wrong:

- `KC-012` is CONFLICTING USERS, "two people run one zone by two designs". It
  was used for a printer whose rollers had never been cleaned.
- `RC-016` is DIFFICULT TO CLEAN. It was used three times for a rucked floor
  mat, an unlevelled bookcase and paper stored in the sun, none of which are
  cleaning-cost faults.
- `RC-014` is SENTIMENTAL ATTACHMENT. It was used for "I am unsure what is
  safe to throw out", which is `RC-015` UNRESOLVED DECISION.
- `KC-006` is POOR ACCESSIBILITY. It was used for backstock you cannot see,
  which is `KC-005` POOR VISIBILITY almost verbatim.

**Why it mattered more than a mislabel.** The renderer turns each cause into a
30-second confirmation test and an entry pass. A wrong ID therefore ships a
reader a test that does not match the answer they just picked: the "rollers
never cleaned" branch was telling people to go and check whether two household
members were running the zone by different designs. The page looked complete
and read as authoritative while giving the wrong next step.

**Why nothing caught it.** Every ID was real and every branch was well formed,
so schema validation passed, the build passed, and all gates passed. The only
signal available was semantic.

**Implication.** When authoring against a closed vocabulary, read the
definitions in the same pass as the authoring, not from memory, however
self-describing the names look. Where the semantics cannot be checked
mechanically, check the SHAPE the mistake leaves behind: `gate_diagnosis_
branch_shape` now fails a friction that reaches one cause twice or two
frictions that repeat each other's answers, and it found five more faults
immediately, three of them created by the corrections themselves. The same
correction pass that fixes this class of error is a likely source of it.

#### LRN-0012: The local image model draws the room, not the micro zone; a close-up naming one or two objects is the only prompt shape that has produced acceptable art

**Status:** SUPPORTED
**Confidence:** MEDIUM (one model, one night, one reviewer)
**Domain:** MEDIA / BUILD
**Measured:** 2026-09-14 to 2026-09-15

SD 1.5 on the local GPU (`ops/image_local.py`), reviewed by Claude at full size against each zone's `done_looks_like` or each
card's callouts, and for cards also at the 750x349 photograph band the template crops to.

- Zone heroes, subject + room word + "warm wood and painted wall, daylight": 0 of 8 zones acceptable, 32 images. Every set
  showed the whole room (a kitchen, a bathroom, a home office) and dropped the zone object (the prep counter, the under-sink
  cabinet, the printer).
- Same zones, "close up of", no room tail, clutter pushed into the negative prompt: 0 of 3, 12 images. The room went away, and
  so did the object; two sets became wood or wall texture.
- Entryway cards, "close up of" one or two concrete objects, no room tail: 3 of 12 cards acceptable, 48 images (EP-008
  backpacks and shoes by a rainy door, ET-004 wall mail sorter, EU-011 clipboard on a hook). Every rejection needed lettering
  (labels, whiteboards, command boards), fine mechanical detail (keys, boot-tray rims, umbrella ribs) or a specific object the
  model could not hold together (a leash, stacked letter trays).

**Implication.** Stop spending cycles on prompt variations for the eight image-less zone pages: none of the three prompt
shapes moved them. For the nine remaining placeholder cards, one more round is worth it only for subjects that name a single
large, simple object; anything that depends on text or fine detail needs a stronger model or a real photograph. A subject
naming more than two objects has not produced an acceptable image in this pipeline.

### Verified Customer Learnings

`NONE VERIFIED IN THIS FILE`

### Verified Commerce Learnings

#### LRN-0008: Every buy-click the site has recorded came from a page that never priced the thing on the button

**Status:** SUPPORTED
**Confidence:** MEDIUM
**Domain:** CONVERSION
**Measured:** 2026-09-03

All nine `buy-click` events ever recorded sit on `/book.html` (4), `/method.html`
(3) and `/consulting.html` (2). None produced a purchase. Reading those three
pages as they were served:

- `/book.html` asked $49 for "the bundle" and did not say what a bundle was.
  The contents were 300 lines below, inside a grid that does not exist until
  JavaScript builds it.
- `/consulting.html` carried no number anywhere in its HTML: the $250 and
  $1,200 packages are rendered at runtime from `window.CATALOG`.
- The two consulting SKUs were the only priced items in a 159-row catalogue with
  no "what happens after you pay" note, while all 153 digital products had one.

**Confidence is MEDIUM, deliberately.** Nine clicks and zero purchases cannot
establish causation, and three of the seven Stripe sessions fall inside one hour
on the evening the links were being tested, so some are probably ours. What is
established is the page state, not its effect.

**Implication.** Stating the price, the contents and the after-payment step
beside the button is correct on its own terms at any traffic level. It should
not be reported later as a validated conversion win unless a purchase actually
follows.

#### LRN-0010: Every buy and quote signal since 7 September came from the owner's own household, and Stripe's "checkout started" count is not a customer metric

**Status:** SUPPORTED
**Confidence:** HIGH for attribution, MEDIUM for the stranger estimate
**Domain:** CONVERSION / DATA QUALITY
**Measured:** 2026-09-14

Stripe holds 16 unpaid checkout sessions in the 7 days to 2026-09-14 and about
90 more on 2026-09-07. Each one was matched against Umami events and against
the reverse proxy's own access log (`nginx-proxy-manager`,
`/data/logs/proxy-host-4_access.log*`, which survives container recreation,
unlike `docker logs 6s-success`).

- **2026-09-07 16:43, ~90 sessions opened in catalogue order ~3s apart:** the
  owner's home IP (160.2.171.170, the only IP ever referred from hPanel),
  browsing with an emulated `iPhone OS 17_0` user agent plus a Windows Chrome,
  hopping pages every few seconds. Our own tooling or testing.
- **2026-09-12 23:46, the only `quote-click` (CN-CORP):** the home IP, a real
  iPhone (`iOS 18_7`, 430x932), arriving from LinkedIn.
- **2026-09-14 01:24:58, the only `buy-click` matched to a session (MZ-MANUAL,
  $29):** the same home IP and iPhone, to the second. Abandoned.
- **The other opens** had no request to our site within two minutes either
  side, so they did not start from a page on the site. Their source is unknown.
- **Scale of household traffic, 2026-08-30 to 09-14:** the home IP sent 5,416
  of 6,408 analytics beacons (4,497 headless Chrome, 881 iPhone, 57 desktop);
  66 other browser IPs sent 281. Headless beacons do not become Umami visits
  (2,498 on 2026-09-04 against 9 recorded visits), so headless tooling does
  not inflate the visitor count, but the owner's iPhone does.
- **LinkedIn:** 27 LinkedIn-referred page views, 7 from the home IP and 20
  from 13 other IPs. Some of those are mobile-carrier IPs on the same iOS
  version as the owner's phone, so a few may be the owner off wifi.

**Implication.** "Customers who are not Phil" is still 0 and "buy-clicks from
strangers" is also 0 since 2026-09-07. Stripe's session count must never be
reported as checkouts started; the honest funnel signal is a `buy-click` from
a device not labelled internal. Until the owner's devices carry
`?6s-internal=1` (`OWNER-ACTIONS.md` 1c), every funnel read needs this
proxy-log attribution by hand. Umami's `IGNORE_IP` would remove the household
automatically but deletes data irreversibly, so it is not adopted.

### Verified SEO/AEO Learnings

#### LRN-0016: Fixing a generator does not fix what it already rendered, and the expensive artifacts are the ones nobody checks

**Status:** SUPPORTED
**Confidence:** HIGH (measured zone by zone against the live standard, and confirmed at the pixel level by extracting real frames)
**Domain:** Quality / release
**Measured:** 2026-09-17

`video_zone.done_items()` was corrected on 2026-09-15. Every narrated zone video had been rendered on 7 and 8 September.
Nothing connected the two facts, so **100 of 114 videos sat on disk showing a checklist their own zone page had stopped
agreeing with**, waiting for the owner action that would publish them permanently.

**Why this class hides.** This repository already regenerates-and-diffs its cheap artifacts on every run
(`gate_etsy_pdfs_current`, `gate_kdp_cover_current`, `gate_standards_pack_current`, `gate_downloads_current`,
`gate_generator_ownership`). Every one of those works because regenerating is seconds. A zone video takes **4.5 minutes**,
so 114 of them cannot be rebuilt to compare, and the artifact fell out of the pattern entirely. Expense is what made it
invisible, not obscurity: it is the most valuable asset class the project owns.

**The move that worked:** when an artifact is too expensive to regenerate for comparison, compare a **cheap derived
signal** instead. Every video ships an `.srt` beside it, and the caption text is produced from the same data as the
frames, so `ops/check_video_standard.py` compares captions against `done_items()` in under a second for all 114.

**Two limits found by pushing on it, both worth copying:**
- A proxy must be checked against the real thing at least once. Extracting an actual frame with `ffmpeg` and reading it
  confirmed the captions match the pixels, and *the same check found a second defect the proxy could not see*: the slide
  shows four items and 16 zones have more than four, so the china cabinet video was silently dropping "The cabinet
  strapped to a wall stud" under the heading "What done looks like".
- A lenient comparison is worse than none. The first version matched the rendered list against an open-ended prefix of
  the standard, so a video showing one correct item out of six passed as current.

**Implication.** Guard the owner's action, not just the repository: the fix that mattered was making
`ops/youtube_upload.py` refuse stale slugs by name, so authorising YouTube publishes the 14 correct videos instead of
100 contradictions. Ask of every expensive artifact: what cheap signal moves when its source moves, and what would
happen if somebody shipped it today?

**Next action:** none outstanding; the re-render is running and `gate_zone_videos_match_standard` reports the count every
cycle until it reaches zero.

#### LRN-0015: A count is not a count until its unit is named; 947 minus 792 was pageviews minus events

**Status:** SUPPORTED
**Confidence:** HIGH (re-derived from the source database in one query, both figures reproduced exactly)
**Domain:** Measurement
**Measured:** 2026-09-17, direct Umami database read from the VPS

Two sessions read the same dataset and published figures three times apart. One reported 506 real pageviews of 947 after
excluding automated sessions; the other reported "one session carrying 792 of 947 pageviews (84%), leaving roughly 155
real events". Both numbers are real and both were honestly read. The subtraction was not: **792 is that session's TOTAL
EVENTS (431 pageviews plus 361 custom events), and 947 was the site's PAGEVIEW count.** Different units on either side of
a minus sign. Re-derived in one query: 949 pageviews over 30 days, 431 of them that one session (no browser string,
iOS/mobile, 28 minutes on 7 September), leaving **518 human pageviews from 77 visitors**, or 501 from 76 once a second
high-rate session goes too. The 506 reading was right in method.

**Why it mattered:** `GOALS.md` and `RISKS.md` are the files work is prioritised from, and for a day they carried a
traffic figure that was either right or three times too high, with no way to tell which. Nothing was wrong with either
observer; the defect was that neither figure carried its unit.

**Implication.** Any count published here names its unit: pageviews, events, visits (`visit_id`) or visitors
(`session_id`). Never subtract two counts sourced from different queries without checking both units first.
`ops/traffic_query.sh` now prints pageviews and all_events side by side per session, so the answer is read, not recalled.
This is the same family as the already-recorded `session_id` = visitor trap, which cost a 3x error in the other
direction.

**Next action:** none outstanding; baselines corrected in `GOALS.md`, `RISKS.md`, `STATUS.md`, `OWNER-ACTIONS.md`,
`ops/roadmap_report.py` and `ops/experiments.json` in the same commit as this entry.

#### LRN-0013: Googlebot reads no content page here, and it is not because the content is hard to reach

> **Update 2026-09-20, measuring whether the two fixes actually worked, which nothing had checked.** Same source,
> now 181,847 lines back to 2026-08-19, read with `ops/crawl_report.py --source proxy`.
>
> * **The `Disallow: /stats/` shipped on 2026-09-16 worked, completely.** Googlebot's fetches of the analytics
>   beacon ran at 10 to 20 a day, with bursts of 239 (23 Aug), 189 (5 Sep) and 104 (22 Aug). From 2026-09-17, the
>   day after the rule shipped, they are **0, and have stayed 0 for four straight days**. That is roughly a third
>   of Googlebot's daily budget on this domain returned to content, and it is the first shipped SEO change here
>   that can be shown to have changed crawler behaviour rather than merely being correct.
> * **Content fetches show an uptick that is one day old and must not yet be called a trend.** Googlebot fetched
>   845 content pages in total since 19 Aug, but 551 of those were the 22 to 25 August burst and 156 more on
>   5 Sep. Through 10 to 19 Sep it ran 0,0,1,0,1,2,6,1,1,1 a day. On **2026-09-20 it is 15**, the highest since
>   6 September, following the www/`.html` 301s (17 Sep), the corrected sitemap `lastmod` dates (19 to 20 Sep)
>   and an IndexNow submission of 117 changed pages. Three causes, one day, no control: this is an **early
>   signal, not a result**, and the honest next step is to keep reading the same log for a week before claiming
>   anything.
> **THIRD READING, 2026-09-23, AND THE SECOND READING WAS WRONG. It was a burst, not a change.** Googlebot
> content fetches by day: 2026-09-19 **1**, 09-20 **17**, 09-21 **15**, 09-22 **2**, 09-23 **2** (to 12:50 UTC).
> Two elevated days, then straight back to the 1-to-2 baseline it came from. The block below called that "a real
> and sustained change in crawler behaviour" after seeing two consecutive days; four days say it was a recrawl
> burst, which is exactly what an IndexNow submission of 117 pages plus corrected `lastmod` dates is supposed to
> cause, once.
>
> **The error is mine and it is worth naming precisely, because it is subtle.** The first reading (2026-09-20)
> was correct and appropriately hedged: "an early signal, not a result". The second reading upgraded it to
> "sustained" on the strength of one more day. Two points in the same direction is not a trend, it is two points,
> and "sustained" was a claim about the future that one extra day could not support. The guard that would have
> caught it was already written in the first reading's own words, "keep reading the same log for a week before
> claiming anything", and I did not follow it.
>
> **What stands.** The `Disallow: /stats/` result above is unaffected and remains the real finding: beacon
> fetches went to 0 on 17 Sep and are still 0, six days on. That was a change in what Googlebot does, measured
> against a clear before and after, and it has held.
>
> **What this costs us.** Nothing was built on the wrong claim, because it was recorded rather than acted on.
> The standing conclusion is unchanged and now better evidenced: on-page work does not move this site's
> discovery (the templated-pages hypothesis is ruled out below), and a crawl burst from a submission is not
> traffic. Human arrivals over the same four days: 10, then 12 in the trailing week, against 18 three weeks ago.
>
> **Second reading, 2026-09-21 07:52 MDT. SUPERSEDED by the third reading above: this one called a two-day burst "sustained" and was wrong.** Googlebot content fetches: 2026-09-20 closed at
> **17**, and 2026-09-21 is at **11 before 08:00 local with the day not over**. Against the ten days before them
> (10 to 19 Sep: 0,0,1,0,1,2,6,1,1,1, or 1.3 a day) that is roughly a tenfold rise sustained across two
> consecutive days, which is no longer explainable as one day's noise.
>
> It is also broad rather than concentrated: 28 fetches across **23 distinct pages** (16 room, 10 zone, 2 article),
> not one page refetched. That is the shape of a crawler working through a list it has been given, which is what
> the sitemap and the IndexNow submission were for.
>
> **What this still is not.** There is no control, three changes landed in the same window (the www and `.html`
> 301s on 17 Sep, the corrected `lastmod` dates on 19 to 20 Sep, and an IndexNow submission of 117 pages on
> 19 Sep), and crawling is not indexing and is certainly not traffic. The honest status is **a real and sustained
> change in crawler behaviour, cause unattributed, business effect unknown**. What would settle it: whether the
> rate holds past a week, whether Bing's indexed set grows from the 10 URLs measured on 20 Sep, and ultimately
> Search Console, which is still `OWNER-ACTIONS.md` 1a.
>
> * Googlebot is still fetching both URL forms of the same page (`/rooms/kitchen` and `/rooms/kitchen.html`), which
>   is exactly what a crawler does while it works through 301s it has just discovered, and is expected to fade.

> **Corrected 2026-09-17: the headline observation is false, and the implication changes with it.** The 129-fetch window
> below was the current, unrotated proxy log only. Reading the rotated files too (164,522 lines back to 2026-08-20),
> genuine Googlebot (373 zone fetches, all from 66.249.x) **fetched every one of the 115 zone URLs, each twice** (as
> `/zones/<slug>` and `/zones/<slug>.html`), overwhelmingly on 23 to 27 August (98, 97, 76, 26, 23 zone fetches), plus
> articles and rooms, then fell to 0 to 14 content fetches a day through September. So Google has read the content; it
> read it once and chose not to come back for more. That is the signature of an evaluation after crawl (Search Console's
> "crawled, currently not indexed", or indexed with no ranking), not of a crawler that never found the pages. The
> reachability findings below still stand. What does not: "the remaining candidates are crawl-budget allocation and
> domain authority" should now read **page value as Google judged it on first read, and authority**, and that makes the
> distinctiveness of the 114 templated zone pages a legitimate candidate cause again. Two cheap contributors were fixed
> the same day: every page also answered 200 on `www.` (29 of 143 Googlebot fetches 10 to 17 Sept) and every
> zone/room/article page on its `.html` twin; both now 301 to the canonical (`site/nginx/default.conf`,
> `ops/tests/test_nginx_www_redirect.py`). **Method lesson:** a log-derived "never" must name the retention window it
> covers; `zcat -f <log>.*.gz` before concluding absence.

> **The "templated zone pages" hypothesis is now ruled out too, 2026-09-21, by measuring the pages instead of
> eyeballing them.** The 2026-09-17 correction above reopened "the distinctiveness of the 114 templated zone
> pages" as a legitimate candidate cause. It is not one. Across all 114 pages, taking the visible text inside
> `<main>`:
>
> * **3,170 words a page** (min 2,787, max 4,376). These are not thin pages.
> * **Only 27% of a page's words, at the median, sit in sentences that appear on half or more of the other zone
>   pages** (min 15%, max 31%). So roughly three quarters of every page is text that page does not share widely.
>   The genuinely universal text is 33 sentences: the method's own reasoning, the affiliate disclosure and the
>   licensed-work disclaimer, all of which are supposed to be identical everywhere.
> * **The shared text is never a preamble.** Words of widely-shared text before each page's first unique
>   sentence: median 0, max 0, on all 114. Every page opens on its own material.
> * **114 distinct titles and 114 distinct meta descriptions**, no collisions.
>
> **Implication, and it is a negative one worth as much as a positive.** Do not spend cycles rewriting 114 zone
> pages for "distinctiveness". The measurement says the distinctiveness is already there, and the work would be
> weeks spent against no evidence. Combined with the reachability findings below, on-page structure, depth,
> uniqueness and metadata are now all ruled out. What remains is off-page: authority, external links and demand,
> none of which is fixable by editing the site, and most of which runs through channels in `OWNER-ACTIONS.md`.

**Status:** SUPPORTED
**Confidence:** MEDIUM (one crawl window, one log source, and it rules a cause out rather than naming the real one)
**Domain:** SEO / AEO
**Measured:** 2026-09-16, from the nginx-proxy-manager access log filtered to 6s-success.com, and from a link traversal of the committed site

Googlebot made 129 fetches of this domain in the retained window. 31 went to `robots.txt`, 21 to `/stats/api/send`, 6 to
`/stats/script.js`, 6 to `/`, and the rest to CSS, JS and the favicon. **Not one went to a zone, room or article page.** The
obvious hypothesis was that content is hard to reach. It is not:

- A breadth-first traversal from `site/index.html` reaches **186 pages**, and **114 of 114 zone pages at depth 2**. Every zone
  is two clicks from the front door.
- All 188 site URLs are in `sitemap.xml`, including `standards.html`, and the sitemap is served 200 at 92 KB.
- `gate_nav_canonical`, `gate_breadcrumbs_current` and `gate_zone_name_consistency` all pass clean.
- Bing behaves differently on the same site: bingbot fetches real pages (`/privacy.html`, `/terms.html`, `/about.html`, a room
  image), so the crawlable surface demonstrably works for a crawler that chooses to use it.

**A measurement trap that cost one false finding, recorded so it does not cost another.** Every internal link on this site is
extensionless (`canonical_links.py` reports 2,550 extensionless, 0 `.html`). A link analysis that filters hrefs on `.html`
therefore discards nearly every zone and room link and reports 1 of 114 zone pages reachable, which is catastrophic and
wrong. Normalise an extensionless internal link to `<path>.html` before following it.

**Implication.** Reachability, sitemap coverage and internal linking are ruled out as the cause, so further on-page structural
work cannot be justified by this evidence. The remaining candidates are crawl-budget allocation and domain authority, and
neither is measurable from here: impressions and queries need Search Console, `OWNER-ACTIONS.md` 1a, which is Phil's own hand.
Until that exists, treat "Google is not reading our content" as diagnosed-to-a-boundary rather than solved, and do not spend
cycles adding internal links to fix a problem that is not an internal-linking problem.

Claude should treat empty verified registers as a reason to gather evidence, not fabricate it.

## 34. Learning Creation Process

When evidence produces a potentially durable finding:

1. Search existing learnings.
2. Determine whether it updates an existing learning.
3. Inspect source quality.
4. Define scope.
5. Document limitations.
6. Assign confidence.
7. Record implications.
8. Link experiments, metrics, and sources.
9. Determine whether a decision or backlog change follows.

## 35. Contradiction Process

When evidence contradicts a learning:

1. Preserve old evidence.
2. Add contradictory evidence.
3. Assess segment/context differences.
4. Lower confidence if warranted.
5. Mark `CONTRADICTED` when necessary.
6. Create a replacement learning if understanding changed.
7. Revisit related decisions.

## 36. From Learning to Action

A learning may produce:

- a durable decision in `DECISIONS.md`
- a new item in `BACKLOG.md`
- a new experiment in `EXPERIMENTS.md`
- updated content
- a new or changed product
- improved personalization
- a technical standard

Do not automatically turn every learning into work.

## 37. Learning Dashboard

The executive dashboard may surface:

**New This Week**: newly supported learning.

**Challenged**: existing learning weakened by evidence.

**Highest-Value Unknown**: the uncertainty most worth resolving next.

**Applied Learning**: knowledge that changed a product, experiment, or decision.

Do not overwhelm the owner with the full registry.

## 38. Weekly Learning Review

Ask:

1. What did we learn?
2. What evidence became stronger?
3. What was contradicted?
4. What remains uncertain?
5. What should change?
6. What should we stop doing?

## 39. Strategic Learning Gates

Phase progression should depend on knowledge, not feature delivery.

Before broad Entryway expansion, seek credible answers to:

- What do users want the Entryway to do?
- Which micro-zones matter most?
- What root causes recur?
- Which quests create useful completion?
- Which improvements sustain?
- Do users progress to another micro-zone?
- Will customers pay for incremental value?

## 40. Privacy and Security

Never store passwords, API keys, tokens, private household images, unnecessary PII, or sensitive customer attributes.

Use aggregate or sanitized evidence.

## 41. Learning Integrity

Agents must never fabricate evidence, inflate confidence, hide contradictory results, generalize beyond scope, convert targets into learnings, rewrite history to support current strategy, or claim causality from simple correlation without qualification.

## 42. Learning Quality Test

Before promoting a learning, ask:

**What evidence supports this?**

**What population does it apply to?**

**What are the limitations?**

**Could another explanation produce the observation?**

**Would this change a future decision?**

If these cannot be answered, keep it a hypothesis or observation.

## 43. Relationship to the Autonomous System

The complete loop is:

**DATA-SOURCES → METRICS → DASHBOARD → BACKLOG → EXPERIMENTS → LEARNINGS → DECISIONS → GitHub/VPS/Docker Execution → STATUS → Repeat**

## 44. Knowledge Flywheel

The long-term competitive advantage should become:

**More households use 6S Success**
→ **More useful outcome data**
→ **Better understanding of desired functions and root causes**
→ **Better quests**
→ **Better standards**
→ **Better product recommendations**
→ **Better customer outcomes**
→ **More trust and adoption**
→ **More learning**

This flywheel must respect privacy and customer control.

## 45. Highest-Value Learning Goal

The system should ultimately understand:

> For a household with a particular desired function, in a particular room and micro-zone, experiencing a particular type of friction, what is the smallest intervention most likely to create a sustained improvement?

That is more strategically valuable than simply knowing which page receives the most clicks.

## 46. Final Rule

Claude should not merely remember what it **did**.

It must remember what the organization **learned**.

Every meaningful cycle should leave the system with one of three outcomes:

1. We have stronger evidence for something.
2. We discovered that something we believed was wrong or incomplete.
3. We reduced an important uncertainty.

If autonomous work repeatedly produces code and content without producing better knowledge or better customer outcomes, the system is not continuously improving.

`LEARNINGS.md` is the memory that turns repeated execution into compounding intelligence.

