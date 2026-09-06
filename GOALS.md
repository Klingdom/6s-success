# 6S Success: goals and objectives

**The file I read before choosing what to work on.** Baselines are measured, not
estimated, and re-measured every cycle. If a number here is stale, that is a
defect in this file.

**Written 2026-09-02. Baselines measured that day, traffic read directly
from the analytics database after the API token was found expired.**

---

## 0. How to use this

Before starting work, ask three questions in this order:

1. **Which objective does this serve?** If none, do not do it.
2. **Is it downstream of the current constraint?** Work below the constraint
   does not move the goal, however good it is. Section 2 names the constraint.
3. **Will I be able to tell whether it worked?** If not, add the measurement
   first or pick something else.

Work that fails any of these is what "busy and useless" looks like, and this
repository has produced a lot of it: 427 commits in the last seven days against
$0 of revenue in the last thirty.

---

## 1. The main goal

**$20,000 per month in sustainable revenue, earned by people whose homes
measurably work better.**

Both halves are load-bearing. Revenue without the outcome is churn with extra
steps, and the outcome without revenue is a hobby.

**Baseline 2026-09-02:** $19 lifetime, one customer, $0 in the last 30 days.

---

## 2. The theory of the business, and where the constraint sits

Money arrives through exactly one chain. Every objective below attaches to a
link in it.

```
STRANGER -> VISITOR -> ENGAGED -> SUBSCRIBER -> CUSTOMER -> REPEAT
```

| Link | Baseline | What it means |
|---|---|---|
| Stranger to Visitor | **52 visitors / 144 visits / 30 days** | measured 2026-09-03 from the analytics database. The earlier row said "47 sessions" and was neither: it was a visitor count wearing a sessions label, so the return-visit rate it implied did not exist. In Umami `session_id` is the visitor and persists across days; the visit is `visit_id`. |
| Visitor to Engaged | **53 views of /quest.html** | against 61 of the home page, so most arrivals try it |
| Engaged to Subscriber | **0** | email list is empty |
| Subscriber to Customer | n/a | no subscribers to convert |
| Customer to Repeat | n/a | one customer, ever |

**The constraint is the first link.** The site sells 158 of 159 catalogue
products (Corporate Lean 6S is the one gap, no buy path yet), every one of
those payment links is live, checkout works, and the catalogue, videos and
images are built. Almost nobody arrives. Until that changes, improving
anything downstream is polishing a shop with no street outside.

**The rule this implies:** if a cycle produces no plausible increase in
arrivals, it should be able to say why that was still the right call.

---

## 3. Objectives

Each has a baseline, a target, and a way to tell. Ordered by the constraint,
not by how interesting they are.

### O1. Get strangers to arrive. **The constraint.**

| Key result | Baseline | Target |
|---|---|---|
| Analytics readable at all | **fixed 2026-09-02** | read from the database, no token needed |
| Published videos | **12 of 228, measured 2026-09-03 13:35, reconfirmed unchanged 2026-09-06 04:51** | all of them |
| Sessions from organic search | **1 in 30 days** | one visit from Bing, none from Google |
| Sessions, last 7 days | **21** | 128 pageviews |
| Weekly visitors | 12/wk | 500/wk |

**Why it is first, now with numbers.** 52 visitors across 144 visits in thirty
days, and in the whole life of this site **exactly two of them arrived from a
search engine**: Bing on 21 August, and Google on 4 September. Every other
arrival was direct, or from LinkedIn, which is the only channel we actually post
to and which produced 17.

**Corrected 2026-09-05: "not one visit from Google" is no longer true, and the
crawl evidence behind it is the better news.** Read from the production access
log rather than inferred: in the last 72 hours Googlebot fetched this site
**178 times, 171 of them answered 200**, alongside bingbot 8, ClaudeBot 20 and
GPTBot 10. The first Google referral landed the day after the site was
announced through IndexNow and the 114 zone pages were deepened.

So the diagnosis has changed. It is no longer "nothing is crawling us". We are
being crawled steadily and we have begun to rank for something. One referral is
one referral and proves almost nothing on its own, but the crawl is not a
sample of one, and it means the SEO work now has a mechanism to pay off through
rather than sitting behind an unknown. What we still cannot see is impressions
and queries, and that needs Search Console, which is `OWNER-ACTIONS.md` 1a.

Meanwhile we own 114 vertical videos, 114 horizontal videos, 114 caption files
and 896 optimised images, all sitting on a disk. The production problem is
solved and the distribution problem is underway: the YouTube channel now
carries 12 videos (five Entryway zones, seven Kitchen zones), all narrated
with a neural voice and captioned, published by Phil directly.

**What the numbers say to do:** post to the one channel that already works
while the slow instrument warms up, and keep opening the video channels,
because a category like this is searched on YouTube and Pinterest as much as
on Google.

**Blocked on:** uploading the other 216 (228 minus the 12 live), which needs
Phil's own hand on each one, no operator credential exists for this. See
`OWNER-ACTIONS.md` item 11 and `BACKLOG-2026-H2.md` 3.10. Instagram and
TikTok still need accounts only Phil can create; everything up to those
accounts exists.

**Not blocked:** SEO, internal linking, structured data, page speed, and the
Pinterest and Instagram crops, none of which need an account to prepare.

**Confirmed 2026-09-03: the hourly measurement pipeline fix worked.**
`ops/state-checkin.json` was stuck reporting `youtube_published: 1` since
2026-09-02 because `.github/workflows/hourly-brief.yml` had only
`contents: read`, so every hourly push back to `main` 403'd silently
(`continue-on-error: true` swallowed it). That permission was fixed to
`contents: write` earlier today. Phil's own subsequent commit
(`ac83fc3f`, publishing the Kitchen zone's seven videos) carries a fresh
`state-checkin.json` measurement, `youtube_published: 12` as of 13:35,
matching the 12 real video IDs in that commit's own message (5 Entryway,
7 Kitchen). This is the row's real, current, machine-gated number, not a
carried-forward one. Rendering continues in the background: 151 of 228
zone clips narrated as of the same commit. See `ops/NIGHTLY-LOG.md` for
the fuller account of the pipeline fix and
`ops/dashboard.py`'s `narrated_video_line()` for the render-side count,
tracked separately from the publish-side count here.

**Reconfirmed 2026-09-06, this operator.** `ops/state-checkin.json`'s hourly
job has kept running since the permission fix above and pushed successfully
again at 04:51 today; `youtube_published_last_measured` still reads 12, the
same 12 real IDs, not a carried-forward guess (the field's own `_measured_at`
timestamp moved to today, meaning a fresh count ran, not a stale one
repeating). `gate_goals_published_videos_current` was already checking this
row's number against that file on every cycle and would have failed had the
two disagreed; the row's own citation date was just three days behind the
pipeline that feeds it, fixed above. No new videos from Phil since the
Kitchen batch.

### O2. Keep the arrival. Capture an email.

| Key result | Baseline | Target |
|---|---|---|
| Email list | **0** | 100 |
| Working capture on the site | forms hand off to email manually | real list |
| Welcome sequence | none | 3 messages |

**Why:** a visitor who leaves without an address is gone. At current traffic
this is cheap to build and pointless to optimise, so build it plainly and stop.

**Blocked on:** Listmonk root URL and from-address.

### O3. Make the first stranger buy.

| Key result | Baseline | Target |
|---|---|---|
| Customers who are not Phil | **0** | 1, then 10 |
| Checkout works | yes, verified | keep it verified |
| Refunds and complaints | 0 | keep at 0 |

**Why the wording:** one sale to a stranger is a different fact from one sale.
It is the first evidence that any of this is wanted.

### O4. Turn the catalogue into affiliate income.

| Key result | Baseline | Target |
|---|---|---|
| Approved programmes | **0 of 10** | 3 |
| Linkable products | **0 of 123** | 100 |

**Blocked on:** four verification emails from 29 August that were never
actioned. The applications are waiting on us, not on the networks. The
catalogue, link tooling and the required disclosure page are built.

### O5. Ship the app.

| Key result | Baseline | Target |
|---|---|---|
| Verified on a real phone | **no** | 12 of 12 checks pass |
| Store listings | none | both stores |

**Why it is fifth, not first:** an app is a retention tool. Retention of zero
visitors is zero. It matters once O1 works.

### O6. Keep the machine trustworthy.

| Key result | Baseline | Target |
|---|---|---|
| CI pass rate | recovered from 56% | above 95% |
| Payment links verified live | yes | daily |
| Owner messages unread | gated | always zero |
| Production matches repository | yes | keep |

**Why it is an objective and not overhead:** the eight-day payment outage cost
more than any feature would have earned, and it was invisible because nothing
watched. Reliability here is revenue protection.

---

## 4. Decision rules

1. **Distribution beats production.** We are long on assets and short on
   audience. Prefer the thing that puts an existing asset in front of a person.
2. **A blocked objective does not stop the cycle.** Do the unblocked part, put
   the gate in `OWNER-ACTIONS.md`, move on.
3. **Do not ask before trying.** Narration was declared a blocker for days and
   the tool was already installed. Attempt, hit a real wall, then escalate.
4. **Measure the customer-visible thing.** The repository is not the product.
   A commit that never deploys did not happen.
5. **An exit code is not an observation.** Check the live surface.
6. **Unchecked is not passing.** Report what was not verified as loudly as what
   failed.
7. **Fix what the fix reveals.** Every outage here uncovered a second defect;
   stopping at the first one leaves the second.
8. **Do not add work faster than it closes.** Maximum three major workstreams.

---

## 5. What would make me change this file

- Traffic becomes measurable and shows the constraint is elsewhere.
- A stranger buys something, which makes O3 evidence rather than hope.
- An affiliate approval lands, moving O4 from blocked to live.
- Phil names a different main goal.

Anything else is a reason to work the plan, not to rewrite it.

---

## 6. Review

Read at the start of every cycle. Re-measure every baseline weekly and correct
this file in the same commit as the measurement. A goals file that drifts from
the numbers is worse than none, because it is trusted.
