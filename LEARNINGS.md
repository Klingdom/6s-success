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

**The asymmetry is the actionable part.** Over the same window ClaudeBot made
528 requests and fetched **zero** zone pages, and OAI-SearchBot made 104 and
fetched zero, while GPTBot took all 114 four times and bingbot took 106 of
them. Two large crawlers are reaching the site and never descending into its
deepest content. That is a reachability question with an answer, unlike the
quoting question, and it is worth more than another authored room.

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
