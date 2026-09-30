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
repository has produced a lot of it: hundreds of commits most weeks (see
`EXECUTIVE-DASHBOARD-LIVE.md`'s live count, regenerated every run rather than
typed here) against $19 of revenue, ever, one sale (2026-08-21), and, as of
2026-09-20, **$0 in the trailing 30 days**: the sale fell out of the rolling
window that day with no second sale since (section 1, `f32c0d8c`). The
original "427 commits... against $0 of revenue" version of this line was
stale when it was checked 2026-09-10, because the sale was still inside every
30-day window then; that is no longer true today, and this sentence is what
now needs re-deriving the day a second sale lands or the reading otherwise
goes stale again.

---

## 1. The main goal

**$20,000 per month in sustainable revenue, earned by people whose homes
measurably work better.**

Both halves are load-bearing. Revenue without the outcome is churn with extra
steps, and the outcome without revenue is a hobby.

**Baseline 2026-09-02, corrected 2026-09-10, and the predicted moment has now arrived (2026-09-20):** $19 lifetime, one customer, one sale (2026-08-21), confirmed again today by reading the Stripe charge list directly: one paid charge, ever. This line used to say the sale sits inside any trailing 30-day window, and noted that it would stop being true on 2026-09-20. Today is that day. **Trailing-30-day revenue is now $0**, and the honest statement is: one $19 sale ever, none in the last 30 days, no second customer in the 30 days since.

That is the number the whole plan is measured against, and nothing shipped since has moved it, because nothing shipped since has moved arrivals. **Corrected 2026-09-29:** this line still cited a 2026-09-20 reading (12 visitors in the last 7 days against 10, 14 and 18 before), ten days stale against section 5's own table below. The current 7-day read is 14 visitors recorded, but 30 of that week's 50 pageviews and 9 of its visitor ids arrived in one 20-minute burst on 27 September with no evidence of being human; excluding it, the week is 7 visitors, down on the 12 read four days earlier. The fall has not stopped. One burst made it look as though it had.

---

## 2. The theory of the business, and where the constraint sits

Money arrives through exactly one chain. Every objective below attaches to a
link in it.

```
STRANGER -> VISITOR -> ENGAGED -> SUBSCRIBER -> CUSTOMER -> REPEAT
```

| Link | Baseline | What it means |
|---|---|---|
| Stranger to Visitor | **48 visitors / 119 visits / 30 days** | re-measured 2026-09-29 22:2x UTC against `website_id` f1fc5160-4473-422d-a89e-73ff6cbdca7a, the filter `ops/traffic_query.sh` has always carried. 731 pageviews. Last 7 days as recorded: **14 visitors, 18 visits, 50 pageviews**, against the 12/14/27 read on 2026-09-25. **The week did not rise. One 20-minute burst made it look as though it had.** Of the 50 pageviews, 30 arrived between 18:00 and 18:20 on 27 September from 9 distinct visitor ids, all direct, across Windows 7, Windows 10, Mac OS and iOS. Excluding that single bucket the week is **7 visitors, 9 visits, 20 pageviews**, which is DOWN on the 12 / 14 / 27 of four days earlier. The same signature has appeared before (three consecutive buckets of 6 to 8 visitors late on 23 August), so it is a recurring shape rather than a one-off, and nothing identifies it as human. The honest reading is that arrivals fell again and a burst masked it. The 30-day figure also fell (57 to 48), partly from late-August days leaving the window. All-time now 87 visitors / 232 visits / 1,030 pageviews since 2026-08-20. In Umami `session_id` is the visitor and persists across days; the visit is `visit_id` (LRN-0015). **A read taken the same night without the `website_id` predicate said 239 visitors, a 3.5x overnight jump, because this Umami instance serves three sites and the query was counting other businesses as ours.** Nothing here may be re-derived with a hand-written query; `ops/experiments.py` now refuses one that does not name a website, and `ops/tests/test_umami_website_filter.py` pins that. |
| Visitor to Engaged | **62 views of /quest.html** | against 86 of the home page (`/` 62 plus `/index.html` 24) over the same 30 days, re-measured 2026-09-29. The ratio moved the right way, 58% to 72%, but both numbers fell with the window, so read the ratio and not the counts. Behind it, all time: 21 `quest-start` events from 8 visitors, 30 `quest-card-done` from 5, and 11 `quest-first-start` from 4, so the people who begin do work the cards rather than bounce off them. Re-measured 2026-09-25 with the `website_id` filter; the earlier 53-against-61 reading was taken without it. |
| Engaged to Subscriber | **0** | email list is empty |
| Subscriber to Customer | n/a | no subscribers to convert |
| Customer to Repeat | n/a | one customer, ever |

**New on 2026-09-29, and the first conversion evidence this file has ever been able to cite.** `buy-click` has fired 11 times from 9 distinct visitors, all time, and the payload says where from: book 4, method 3, consulting 2. One of those nine ever paid. Nine is far too small to call a rate, and the honest reading is not "we have an 11% checkout" but "eight people reached for a wallet and did not finish, and until now nobody knew that had happened at all". Two of the eleven clicks are recent (14 and 28 September), so this is not only August history. It is still downstream of the constraint and does not displace it; it is recorded here because it is cheap to look at, it has data, and the next cycle should not have to rediscover it.

**Followed up 2026-09-29 with the Stripe API, and the answer was not the obvious one.** The suspicion was a dead checkout, the shape that once cost this site eight days of $0. It is not: `gate_live_links`, `gate_stripe_link_dedup`, `gate_stripe_orphan_link_active` and `gate_stripe_price_claims` all run clean against the real account with a real key, so every payment link works. What the session list showed instead was **12 checkout sessions created on 2026-09-15, a day the website recorded zero buy-clicks**. A Stripe Payment Link opens a Checkout Session when its page is merely OPENED, and at that moment 420 links to `buy.stripe.com` across 171 shipped pages carried `rel="noopener"` and not one carried `nofollow` (the shop alone had 126), while search engines fetch this site hundreds of times a week. Every one now carries `nofollow`, held by `gate_payment_links_nofollow`. **The consequence for this file is that "sessions created versus paid" was not a usable funnel and nobody knew**: it is the only conversion instrument here that does not need Search Console, and it was full of rows nothing could attribute. A rate computed from it would have been wrong pessimistically and would have looked like evidence. Whether the openings were crawlers or Phil testing by hand cannot be settled from an access log that only records requests inbound, and the fix is correct either way.

**The constraint is the first link.** The site sells 129 of 130 catalogue
products with a checkout that takes a card directly; every one of those
payment links is live, checkout works, and the catalogue, videos and images
are built. Almost nobody arrives. Until that changes, improving anything
downstream is polishing a shop with no street outside.

**Corrected 2026-09-22: the catalogue got smaller, not the constraint.**
`147179c6`, earlier the same day, retired the 6 Area Bundles and 15
Situation Kits (D-023, $0 realised revenue on either tier), moving the
count from 159 to 138 items, 137 buyable. This section still said 158 of
159 several hours later; the arithmetic below and the traffic figures are
unaffected, since neither ever depended on the exact denominator.

**Corrected 2026-09-06: the earlier wording here, calling Corporate Lean 6S
the one gap with nothing yet to buy, was already false the day it was
written.** That line was added 2026-09-05
20:09 (`a3ca85fe`), a full two days after Phil's own commit `9e7b1cd1`
(2026-09-03) shipped `site/corporate.html` and its qualified-enquiry form,
recorded in `BACKLOG-2026-H2.md` 4.5 as done. Checked directly rather than
trusted: the live page has a working enquiry funnel (nine scoping questions,
a `mailto:support@6s-success.com` handoff with the message pre-filled,
tracked as a `corporate-enquiry` event) that ends in a written scope and a
fixed fee, deliberately with no published price because two engagements with
the same headcount can be very different weeks of work. That is a real buy
path for a B2B quote-based service, just not a self-serve Stripe checkout.
The buyable-count denominator itself is unaffected by this correction: it
already counted only direct-checkout products, and Corporate Lean 6S was
never meant to be one (see the 2026-09-22 correction above for why the
number itself has since changed).

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
| Published videos | **12 of 114, measured 2026-09-03 13:35, reconfirmed unchanged 2026-09-06 04:51 and again 2026-09-14 06:30. Corrected 2026-09-16: this row read "12 of 228" for six weeks, conflating the 228 total rendered video FILES (114 vertical plus 114 horizontal, two orientations of the same 114 zones) with the YouTube publishing target. `ops/youtube_upload.py`'s own docstring states only the wide 16:9 file is ever uploaded ("Shorts are a separate distribution decision and are not posted by this tool"), so the real denominator is 114, one per zone, matching `MEDIA-OPERATIONS-PLAN.md` and `OWNER-ACTIONS.md`'s own "102 of 114 remaining" framing, which was right the whole time. The numerator (12) was never wrong.** | all 114 |
| Sessions from organic search | **5 visits from 4 visitors, whole life of the site, re-measured 2026-09-29 and unchanged** | Read directly from the Umami database, not carried forward: bing.com 1 visitor / 1 visit (21 August), google.com 3 visitors / 4 visits (4 to 18 September). **Corrected 2026-09-20:** this row said "4 visits from 3 visitors ... reconfirmed unchanged" earlier the same day. Nothing was re-measured to produce that line; a cloud session holds no VPS key and cannot read this table, so "reconfirmed" meant "carried forward". Google's most recent visit is 18 September, the day after the duplicate-URL redirects shipped. **Re-measured 2026-09-29 against the database, not carried forward: still bing.com 1/1 and google.com 3 visitors / 4 visits, byte-identical to the 2026-09-20 reading.** That is the finding. Eleven days have passed, the corpus reached 114 of 114 diagnosed zones, three more deck pages shipped and the crawl continues, and not one additional search referral has arrived. Whatever is limiting organic arrivals, more pages is not the lever, and this row is the evidence for that. | 
| Sessions, last 7 days | **7** | human-plausible, measured 2026-09-29. Recorded: 14 visitors, 18 visits, 50 pageviews. Excluding one 20-minute burst on 27 September (9 visitor ids, 30 pageviews, all direct, four different operating systems): 7 visitors, 9 visits, 20 pageviews. The sequence on the recorded basis is 18, 14, 10, 12, 12, 14; on the ex-burst basis the fall never stopped |
| Weekly visitors | **7/wk** ex-burst, 14 recorded (2026-09-29, against 12 on 2026-09-25) | 500/wk |

**Why it is first, now with numbers.** 48 visitors (read directly from the
database 2026-09-29, down from 57 on 2026-09-25, 68 on 2026-09-23, 76 on
2026-09-21, 78 on 2026-09-17 and 75 on 2026-09-14) across 119 visits in
thirty days (731
pageviews, very nearly all human now that the 7 Sept automated session has
rolled out of the window; **corrected 2026-09-25: a read taken the same night
WITHOUT the `website_id` predicate said 239 visitors, because this Umami
instance serves three sites. The guard in `ops/experiments.py` now refuses
that query shape**), and in the whole life
of this site **exactly five visits from four visitors arrived from a search
engine**, per the "Sessions from organic search" row above, corrected today
after the earlier "reconfirmed unchanged" line turned out to be an
unmeasured carry-forward: one visit from Bing (21 August), and four visits
from three Google visitors (4 to 18 September). Every other arrival was
direct, or from LinkedIn, which is the only channel we actually post to and
which produced 17.

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

**Five technical explanations for the organic flatline were tested on 2026-09-29 and all five came back clean, which is what makes the remaining gap a measurement gap rather than a build gap.** Read from the persistent access log and from production itself, not inferred:

1. *Is anything crawling us?* Yes, steadily. 662 search-engine fetches over 8 days across 190 distinct non-asset paths, 54 to 118 a day with no downward trend (Googlebot 243, Bingbot 273, YandexBot 118, OAI-SearchBot 35, Applebot 4). A separate 129 fetches were training crawlers (ClaudeBot, GPTBot), which is a licensing event and cannot put this site in front of anybody.
2. *Are we blocking them?* No. `robots.txt` is `Allow: /` and returns 200.
3. *Are we sending crawlers through redirects?* Not from anything we publish. Extensionless is canonical and returns 200, `.html` 301s to it, the sitemap uses the extensionless form for all 20 rooms, and of 1,485 internal links to rooms and zones, **zero** use the redirecting form. The 15% of crawler fetches that do redirect are URLs Google remembers, which self-corrects.
4. *Are we slow or uncacheable?* No. Fingerprinted assets are `public, max-age=2592000, immutable`; only HTML, `robots.txt` and `sitemap.xml` are `no-cache`, which is correct for a site that republishes daily. A first pass here suspected caching was off site-wide because Googlebot re-fetched the same fingerprinted `site.js?v=a9543718af` five times; measuring the headers withdrew that.
5. *Is the sitemap advertising pages we do not serve?* It was, and that is now fixed and separately recorded against `OWNER-ACTIONS.md` item 0. It cost 258 crawler 404s in 8 days.

So the site is crawled, crawlable, fast, correctly canonicalised and internally linked, and it has four organic visitors in its life. What cannot be seen from here is whether those 190 crawled paths are **indexed and ranking badly** or **not indexed at all**, and those two have opposite fixes: the first is an intent-and-competition problem answered by targeting different queries, the second is an authority problem answered by links from elsewhere. Only Search Console distinguishes them, which promotes `OWNER-ACTIONS.md` 1a from a nice-to-have to the one instrument that decides what the next cycle of SEO work should even be.

**What the numbers say to do:** post to the one channel that already works
while the slow instrument warms up, and keep opening the video channels,
because a category like this is searched on YouTube and Pinterest as much as
on Google.

**Blocked on:** uploading the other 102 (114 minus the 12 live), which needs
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

**Reconfirmed again 2026-09-14, PM check-in.** This row's own citation had
drifted 8 days behind the pipeline that feeds it, the same shape as
2026-09-06 above, even though the number itself never went wrong (the gate
would have caught that). `ops/state-checkin.json` shows `youtube_published_
last_measured: 12`, `_measured_at` 2026-09-14 06:30, same 12 real IDs. Still
no new videos from Phil since the Kitchen batch; the constraint remains
distribution, not production.

### O2. Keep the arrival. Capture an email.

| Key result | Baseline | Target |
|---|---|---|
| Email list | **0** | 100 |
| Working capture on the site | forms hand off to email manually | real list |
| Welcome sequence | none | 3 messages |

**Why:** a visitor who leaves without an address is gone. At current traffic
this is cheap to build and pointless to optimise, so build it plainly and stop.

**Blocked on, corrected 2026-09-09: not root URL and from-address, which was
the 2026-08-23 diagnosis and stopped being true the next day.** The from-address
is already ours. The instance-wide SMTP credential it sends through still
belongs to Compassion Benchmark, a different business on the same shared
Listmonk host, so every opt-in confirmation 553s and the visitor sees a 500.
The signup form built for this on 2026-08-23 was withdrawn the same day for
exactly that reason; the footer's mailto fallback is what actually runs today.
Real blocker: issue #15 (P0, decision) needs Phil to choose a separate
Listmonk instance for 6S, or hand the shared instance's sending identity to
6S and move Compassion Benchmark off it. Detail in `OWNER-ACTIONS.md` item 7/7a.

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

**Superseded, corrected 2026-09-09: this objective is deliberately held, not
blocked.** `PLAN-AFFILIATE-MONETISATION.md` (Phil, finalised 2026-09-07) worked
the real arithmetic: at the traffic level where the services line reaches
$20,000/month, affiliate earns about $7/month, roughly 0.03% of the goal. The
plan: apply to nothing today, instrument the existing links, and apply to
Amazon only, when trigger T2 fires (60 real outbound retailer clicks in a
trailing 90 days, `ops/check_affiliate_trigger.py`, reading 0 of 60 as of
2026-09-09). Re-litigate in June 2027 or on the trigger, not monthly. This also
retires the older "four verification emails" diagnosis: of the 10 programmes in
`ops/affiliate-accounts.json`, 5 (Lowes, Target, Walmart, Home Depot, Ace) were
declined outright by their shared Impact account on 29 August (read 2026-09-06);
3 (Amazon, Office Depot, Etsy) sit on unconfirmed verification emails the plan
now says not to chase; 2 (Container Store, Wayfair) were never applied to. The
catalogue, link tooling and disclosure page are built, and this week
also shipped 1,717 honestly-disclosed plain retailer search links across 120
of 123 products (`ops/product_links.py`), so the moment any programme
approves, only the affiliate tag needs adding, not a page rebuilt.

### O5. Ship the app.

| Key result | Baseline | Target |
|---|---|---|
| Verified on a real phone | **no** | 16 of 16 checks pass |
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
