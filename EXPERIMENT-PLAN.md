# Daily experiment plan and backlog

Written 2026-08-19, the day 6s-success.com went public. Owner: Phil.

## Read this first

Until today there was no traffic, so no experiment could run. That has changed,
but one thing has not: **there is still almost no traffic**. A site published
this morning has no audience yet.

That matters more than it sounds. An A/B test on twelve visitors tells you
nothing, and worse, it tells you something confidently. Most of what follows is
therefore not A/B testing. It is instrumentation, then observation, then tests
once the numbers can carry them.

The honest sequence is: **measure nothing until you can measure it, get traffic,
then experiment.**

---

## Phase 0: before any experiment can be trusted

Nothing below can start until these exist. They are not experiments, they are
the conditions for one.

**Corrected 2026-09-10:** the first two rows were written the day the site went
public and are no longer the state. Self-hosted Umami shipped, on our own
domain, no cookies, no third-party requests, exactly as this section originally
recommended; `privacy.html` still reads true. `quest.js` fires a real set of
funnel events (`quest-symptom-picked`, `quest-symptom-start`, `quest-cause-shown`,
`quest-card-abandoned`, `quest-first-victory`, `quest-return`), gated by
`gate_quest_funnel_events` in `ops/preflight.py`. Traffic is genuinely still
below the threshold this table sets: see `GOALS.md`'s own "Stranger to Visitor"
row for the current measured count, not a number repeated here to go stale.

| Need | Why | State |
|---|---|---|
| Any analytics at all | We currently cannot count a single visit | **Live.** Self-hosted Umami. |
| A conversion event | Nothing on the site records intent | **Live.** Six quest funnel events, gated. |
| Enough traffic | Under about 100 sessions a week, results are noise | **Still missing.** See `GOALS.md` for the current count. |

### The analytics decision, made

The site still makes **zero third-party requests** and `privacy.html` says so
plainly. Self-hosted Umami on our own domain was the recommendation here and is
what shipped; Google Analytics was not added, so that trade was never made.

---

## The daily loop

Small and repeatable. It fits in the four hour cycle already running.

**Every cycle**
1. Read the numbers. Sessions, pages, referrers, and the single conversion event.
2. Ask one question: what is the largest gap between what a visitor wants and
   what the page gives them?
3. If an experiment is running, check whether it has reached its stopping rule.
   Do not peek and stop early on a good day; that is how noise becomes a
   decision.
4. If nothing is running and the traffic supports one, start the top of the
   backlog.
5. Record what happened in `EXPERIMENTS.md`, including experiments that showed
   nothing. A null result is a result and it stops the same idea being retried
   in three weeks.

**Weekly**
- One page gets improved on evidence rather than taste.
- The backlog gets reordered against what the numbers now say.
- Anything that has not moved in two weeks gets stopped, not extended.

---

## Stopping rules, agreed in advance

Set before the experiment starts, never after seeing the data.

- **Minimum sample.** No decision under 100 sessions per arm, or 30 conversions
  per arm, whichever comes later.
- **Maximum run.** Two weeks. If it has not resolved, the effect is too small
  to matter at this stage.
- **Guardrail.** If a variant drops the primary metric by more than 20 percent
  with 50 or more sessions, stop it early.
- **One at a time**, until traffic is high enough that two cannot contaminate
  each other.

---

## The backlog

Ordered by what unblocks revenue soonest, not by what is easiest.

### Tier 1: available now, no extra traffic needed

These are not A/B tests. They are things where the current state is measurably
wrong and the fix does not need statistical proof.

**EXP-101. Give the site a single conversion event.**
Right now nothing records that a visitor wanted anything. Every form hands off
to email, which means intent leaves through a channel we cannot count. Add one
event on the newsletter handoff and one on the contact handoff.
*Success:* we can state how many people tried to reach us this week.
*Blocked on:* the analytics decision above.

**EXP-102. Put the consulting offer where visitors actually land.**
**Done 2026-08-19.** Consulting was the only thing deliverable then, at 250 to
1,200 dollars, while the homepage hero and closing CTA both sent visitors to
`shop.html` where most SKUs could not be bought. Both CTAs were repointed at
`consulting.html`. That premise is now stale in the other direction: the
catalogue can take money for 158 of 159 items (`EXECUTIVE-DASHBOARD-LIVE.md`),
so the shop window is no longer mostly empty. Left as done rather than reopened;
whether the hero should now lead with the shop instead is a fresh question, not
a defect in this row.
*Success:* the consulting page is reachable in one click from the homepage hero.

**EXP-103. Make the book sample ask for an email.**
The sample is 40 MB and the single most valuable thing being given away. It
currently costs the reader nothing and gives us nothing.
*Success:* a working capture before the download, honest about what happens to
the address.
*Blocked on:* a provider or a server side endpoint.

### Tier 2: once there is traffic, roughly 100 sessions a week

**EXP-104. Homepage hero: outcome against method.**
Control is the current method led hero. Variant leads with the outcome, a home
that keeps itself, and moves the method below.
*Primary metric:* clicks into any room or micro zone page.

**EXP-105. Free sample format.**
Control offers the 40 MB PDF. Variant offers the 0.8 MB EPUB first with the PDF
secondary. Directly tests issue #14 rather than guessing at it.
*Primary metric:* completed downloads per visitor to the book page.

**EXP-106. One room page, deep against broad.**
The resources page covers 20 rooms at equal depth. Variant gives the entryway
full treatment and links the rest.
*Primary metric:* time on page and onward clicks.

**EXP-107. Consulting price framing.**
Control shows 250 dollars. Variant shows the same price against what it
replaces, framed as the cost of one wasted Saturday.
*Primary metric:* contact form starts from the consulting page.
*Guardrail:* never invent a discount, a deadline, or a scarcity claim.

### Tier 3: needs a real audience, several hundred sessions a week

**EXP-108. Micro zone quiz as an entry point.** Does a two question diagnostic
beat a room list as a first step?

**EXP-109. Quest length.** Do people finish more 15 minute quests than 45 minute
ones, and does finishing predict return visits?

**EXP-110. Card deck interest test.** Before building 18 more room decks, does a
genuine, clearly labelled waiting list attract anybody? Labelled as a concept,
never sold as available.

### Tier 4: search, which is slow and worth starting anyway

**EXP-111. Search console baseline.** Not an experiment. Register the property
and wait. Nothing about organic search can be reasoned about without 30 days of
impressions, so the clock should start now.

**EXP-112. One micro zone page against real queries.** Once impressions exist,
rewrite the single highest impression page against what people actually typed.

---

## What will not be tested

Recorded so it does not get proposed later.

- Fake scarcity, countdowns, invented discounts, or manufactured demand.
- Anything that makes `privacy.html` untrue.
- Personalised pricing.
- Testing a buy path for a product that does not exist. Eight priced SKUs
  currently have no supplier, platform or stock, and putting a checkout in front
  of one would be selling something we cannot ship.

---

## The honest summary

There are twelve experiments here and **zero can produce a trustworthy result
this week**, because the site has no analytics and almost no visitors. The
useful work right now is Tier 1, which is not testing at all: instrument the
site, point it at the one thing that can actually be sold, and capture the
readers the book already sends.

Real experimentation starts when there is an audience to experiment on.
