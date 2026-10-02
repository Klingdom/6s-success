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
| Stranger to Visitor | **49 visitors / 121 visits / 30 days** | re-measured 2026-09-29 22:2x UTC against `website_id` f1fc5160-4473-422d-a89e-73ff6cbdca7a, the filter `ops/traffic_query.sh` has always carried. 731 pageviews. Last 7 days as recorded: **14 visitors, 18 visits, 50 pageviews**, against the 12/14/27 read on 2026-09-25. **The week did not rise. One 20-minute burst made it look as though it had.** Of the 50 pageviews, 30 arrived between 18:00 and 18:20 on 27 September from 9 distinct visitor ids, all direct, across Windows 7, Windows 10, Mac OS and iOS. Excluding that single bucket the week is **7 visitors, 9 visits, 20 pageviews**, which is DOWN on the 12 / 14 / 27 of four days earlier. The same signature has appeared before (three consecutive buckets of 6 to 8 visitors late on 23 August), so it is a recurring shape rather than a one-off, and nothing identifies it as human. The honest reading is that arrivals fell again and a burst masked it. The 30-day figure also fell (57 to 48), partly from late-August days leaving the window. All-time now 87 visitors / 232 visits / 1,030 pageviews since 2026-08-20. In Umami `session_id` is the visitor and persists across days; the visit is `visit_id` (LRN-0015). **A read taken the same night without the `website_id` predicate said 239 visitors, a 3.5x overnight jump, because this Umami instance serves three sites and the query was counting other businesses as ours.** Nothing here may be re-derived with a hand-written query; `ops/experiments.py` now refuses one that does not name a website, and `ops/tests/test_umami_website_filter.py` pins that. **Re-measured 2026-10-02 14:1x UTC with `ops/traffic_query.sh`: 30 days is 49 visitors / 121 visits / 719 pageviews, flat on the 48 / 119 / 731 of three days earlier. The week is the part that moved: 22 visitors / 29 visits / 62 pageviews as recorded, and 13 visitors / 20 visits / 32 pageviews excluding its single busiest 20-minute bucket, against 7 ex-burst on 2026-09-29. That is the first rise this row has recorded, and the excluded bucket is the same 27 September one, still inside the window.** All time is now 96 visitors / 246 visits / 1,047 pageviews. Read honestly, 13 a week against 7 is a doubling of a very small number and could be noise; what it is not is the continued fall this row described three days ago. **One caution recorded for whoever re-measures next: this reading was taken with `ops/traffic_query.sh`, which hardcodes both the container and the website_id. A hand-written query on this host that picks its container with `docker ps | grep umami-db | head -1` selects Ledgerium's database, which holds none of our rows and would report a clean, well-formatted ZERO. That happened to this operator today (LRN-0033).** |
| Visitor to Engaged | **62 views of /quest.html** | against 86 of the home page (`/` 62 plus `/index.html` 24) over the same 30 days, re-measured 2026-09-29. The ratio moved the right way, 58% to 72%, but both numbers fell with the window, so read the ratio and not the counts. Behind it, all time: 21 `quest-start` events from 8 visitors, 30 `quest-card-done` from 5, and 11 `quest-first-start` from 4, so the people who begin do work the cards rather than bounce off them. **Read out of the event payloads 2026-09-30, which had never been opened:** within a session the card-by-card retention is the healthy part of this whole funnel. Of the 5 visitors who finished a first card, 4 finished a second, 3 finished a third, and 3 got as far as a sixth; one reached a seventh. Nobody who starts working cards bounces after one. The entry path is overwhelmingly one of the four: `mode=zone` on 17 of the 21 starts and 7 of the 8 visitors, against `room` 2 and `draw` 2, so the zone path is the product and the other three are rounding. **That comparison is also why `quest-symptom-shown` shipped 2026-09-30:** `quest-start` covers all four modes and `quest-symptom-picked` covers only the one, so "how many people were asked what is annoying them and did not answer" was not readable from either. The new event fires once per page load, on the hidden-to-visible transition of the symptom step, carrying only the number of choices offered. It makes the first step of the core product measurable for the first time; there is no data behind it yet, and this row should be re-read once there is. A typical deal is 6 cards (17 of 21 starts); two outliers dealt 30 and 42. Only one `quest-first-victory` has ever fired.

**The quest has never made an offer to anybody, and that is a gate rather than a failure.** `#f-offer` appears only when two zones are holding, and `quest-zone-held` is 4 events from 3 visitors all time: exactly one person has ever held two, on one day. `quest-offer-shown` has existed since the offer did and has never fired, which is consistent and is why the quest accounts for none of the 11 `buy-click` events (book 4, method 3, consulting 2, home 1, zone 1). **The gate was left exactly where it is.** Its own code comment argues that two zones in two rooms means the habit is travelling, and loosening it to manufacture impressions is the interrupt-and-sell pattern `CLAUDE.md` section 12 forbids; the offer is untested, not failing, and the honest way to test it is to let more people reach it.

What was fixed instead is that half of it could not be counted. The paid pitch points at Stripe, which `measure.js` turns into `buy-click`; the free pitch repoints the same button at `deck.html`, which matches none of that file's branches, so taking the free offer fired nothing and would have read as being ignored. `quest-offer-taken` (2026-09-30) closes it for both pitches, reporting the SKU from the live attribute so a free download can never be filed as a $19 sale.

**`quest-save-blocked` has never fired, for anybody.** That event exists because everything a household does here lives in `localStorage` and nowhere else, and the page promises in so many words that it "stays in this browser"; Safari private browsing and blocked site data both make `setItem` throw. Nine quest event names appear in the database and that is not one of them, so the promise has held every time it has been tested by a real visitor.

**One thing deliberately not concluded.** Every one of the 21 starts carries `first=1`, which is tempting to read as "no visitor has ever come back". It does not mean that: `isFirstRun()` returns true when no card has been completed *at the moment of starting*, not when the browser has never been seen. One visitor has 10 starts and 12 completed cards, which that reading cannot explain, so the flag is measuring something narrower than its name suggests. Whether anybody returns is still unmeasured, and the honest way to find out is a returning-visitor event rather than a re-reading of this one. Re-measured 2026-09-25 with the `website_id` filter; the earlier 53-against-61 reading was taken without it. |
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
| Sessions from organic search | **6 visits from 5 visitors, whole life of the site, re-measured 2026-10-02** | Read directly from the Umami database, not carried forward: bing.com 1 visitor / 1 visit (21 August), google.com 3 visitors / 4 visits (4 to 18 September). **Corrected 2026-09-20:** this row said "4 visits from 3 visitors ... reconfirmed unchanged" earlier the same day. Nothing was re-measured to produce that line; a cloud session holds no VPS key and cannot read this table, so "reconfirmed" meant "carried forward". Google's most recent visit is 18 September, the day after the duplicate-URL redirects shipped. **Re-measured 2026-09-29 against the database, not carried forward: still bing.com 1/1 and google.com 3 visitors / 4 visits, byte-identical to the 2026-09-20 reading.** That is the finding. Eleven days have passed, the corpus reached 114 of 114 diagnosed zones, three more deck pages shipped and the crawl continues, and not one additional search referral has arrived. Whatever is limiting organic arrivals, more pages is not the lever, and this row is the evidence for that. **Re-measured 2026-10-02 against the same database and the number moved for the first time in three weeks: google.com is now 4 visitors / 5 visits / 8 pageviews spanning 4 September to 1 OCTOBER, plus bing.com 1/1/1 on 21 August. So 6 visits from 5 visitors all time, one more visitor than the figure that had held since 2026-09-20, and the most recent organic arrival is 1 October rather than 18 September.** One visitor is one visitor and proves nothing on its own; it is recorded because this row's whole argument has been that the number does not move. **The landing pages are the more useful half and this row has never carried them: `/standards.html` takes 4 of the 8 Google pageviews, `/` takes 3, and `/articles/why-you-keep-buying-things-you-already-own` 1; Bing's single visit landed on `/contact`.** That `/standards.html` is the most-landed-on page from search is worth knowing, because nothing in this file or the backlog has ever treated it as a discovery page. | 
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
of this site **exactly six visits from five visitors arrived from a search
engine**, per the "Sessions from organic search" row above, re-measured
2026-10-02 and moved for the first time in three weeks: one visit from Bing
(21 August), and five visits from four Google visitors (4 September to
1 October). Every other arrival was
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

**Corrected 2026-10-01, this operator: "only Search Console distinguishes them" overstated the gate, and the half that is public has now been measured for the first time.** Search Console is still the only source for OUR impressions, so the sentence above stands for that. But "what people type" is public: Google and Bing both answer their autocomplete endpoints without a key, an account or a referrer check, and this business had never once looked. `ops/keyword_demand.py` (new, 14/14 tests, fail-then-pass proved against four planted defects) harvests them from seeds built out of the real corpus, then checks each query against every published page title.

**First reading, 2026-10-01: 137 seeds, 274 attempts across both engines, 0 errors, 36 seeds with genuinely no completions, both canaries clean, 2,622 distinct queries.** Against our own page titles: 346 covered, 1,562 partial, 714 with nothing of ours titled for them. **Corrected later the same day, and the correction is larger than the finding: that scorer read TITLES only**, so a page answering a question properly under its own `<h2>` counted as a gap. Reading headings as well, which the tool now does and labels per row with `matched_on`, the real figures are **223 gaps, 1,417 partial, 982 covered**, and 226 of those gaps existed before this cycle wrote anything. The honest remaining target is 223, not 714. The reading is recorded in `ops/keyword-demand.json` and read in `ops/KEYWORD-DEMAND.md`.

**Re-harvested 2026-10-02 08:12, now with the vocabulary probes, and the clusters this file named yesterday have all moved. Re-scored against the current corpus rather than read off the stored snapshot, which was itself stale within hours.** 151 seeds, 263 of 302 attempts returning completions, 0 errors, both canaries clean, **2,827 queries: 253 gap, 1,465 partial, 1,109 covered.** By cluster, stored snapshot then re-scored: *cheap, budget, DIY* 0 covered then **29** (a concurrent session added a room-by-room budget section to `more-storage-wont-fix-clutter`); *small spaces* 50 then **82**; *complaint* 17 and unchanged, which is this cycle's own article holding. **The lesson is procedural and it has now bitten twice in two days: a stored status is a snapshot of a corpus that is being changed by other sessions, so re-score before drawing a conclusion from it.** Acting on the stored numbers would have produced a budget article duplicating one that already existed.

**What the probes found, which is what they were for.** The first harvest could only discover phrases built from our own room names. With fourteen probe seeds in: **"master bedroom" 16 queries and 0 covered, "foyer" 16 and 0, "master bathroom" 13 and 0, "bonus room" 15 and 0, "larder" 11 and 0**, every one of those words appearing on zero pages of this site. Closed the same day in `c64901cd0`: five room pages now name the household's own word for the room, held by a test that refuses a name with no measured demand. **Also found and deliberately not acted on:** basement (21 queries, 0 covered, rank 1) and attic (16, 0, rank 1) are rooms this site does not have at all. That is 1.3% of measured demand against a product-definition change, so it is recorded in `BACKLOG-2026-09-07.md` 1b as an owner decision rather than started. It is not search volume and must never be quoted as one: an autocomplete suggestion proves an engine predicts the phrase, nothing more, and the report carries that caveat in its own header.

**What it found, and it is a content gap rather than a technical one.** The complaint cluster, the way somebody searches before they have decided that organising is the answer, is 53 queries, and on the title-only reading **zero** were covered: "why is my kitchen always messy" and "why is my kitchen always a mess" and "why is my bedroom always messy" and "why your home is always messy" are all rank-1 suggestions, and the closest thing we publish is the articles index. That is the one question this entire product is built to answer, we have 17 shared root causes and 114 diagnosed zones to answer it with, and we have never put a page in front of it. Two further clusters are 0 covered: the "small space" modifier (153 queries) and "cheap/budget/DIY" (98). The "with kids" modifier is 153 queries and 19 covered.

**Indexation, partly answered and partly still unchecked, written out in full because the difference decides the next SEO cycle.** A single DuckDuckGo read at 08:5x UTC (DuckDuckGo serves the Bing index) for `site:6s-success.com` returned ten real pages of ours: `/`, `/about.html`, `/method.html`, `/consulting.html`, `/resources.html`, `/shop.html`, `/articles/`, `/articles/how-long-does-it-take-to-organise-a-room`, `/rooms/home-office`, and `/quest.html?zone=home-office-the-bookshelf-and-reference-zone`. So "not indexed at all" is **false** for the Bing-derived index, and for Bing the diagnosis is indexed-and-not-ranking, which is the intent-and-competition problem, which is what the harvest above is the instrument for. **Three follow-up queries meant to establish which SECTIONS are indexed (`/zones/`, `/articles/`, `/rooms/`) were all refused with HTTP 202 after an earlier burst earned a block, so section-level indexation is UNCHECKED, not clean.** Nothing about Google's index was measured at all. No zone page appeared in the ten, which is suggestive and is not evidence.

**Measured afterwards, three ways, rather than assumed.** On the corrected (heading-aware) scorer the complaint cluster went from **8 covered to 17**, and from 3 gaps to 1, which is what the article actually bought. The headline "zero covered" was the title-only scorer, not the corpus: eight of those questions were already answered under headings on pages that existed. Both facts belong here. What stopped the error being expensive was the decision to write one page rather than eight; eight per-room pages would have been thin pages built on a number that was mostly measurement error, and `CLAUDE.md` section 11 is the only reason that did not happen.

**Acted on the same day, which is the point of taking the reading.** The complaint cluster now has a page: `/articles/why-is-my-house-always-messy`, 2,694 words, generated from `ops/root_causes.py` so its seven causes and their thirty-second tests cannot drift from the vocabulary the decks and zone pages use. One page rather than eight, with the kitchen, bedroom, kids' room and closet versions answered on it and linked to their room pages, because the answer to all four is the same diagnosis with a different example and eight pages would be one article padded seven times. Nine FAQ entries worded as the exact phrases the harvest recorded, every answer present in the page's own visible text. **A concurrent session independently wrote the same article from the same data a few hours apart; one page survived, this one, with their better FAQ wording ported into it.** Whether it moves anything is unmeasured and will stay that way for weeks: the honest test is a re-harvest showing those queries off `gap`, plus any organic arrival at all on that URL, and neither is available today.

**Corrected 2026-10-02: "will stay that way for weeks" described the sandbox, not the data, and that was the thing to fix.** Every cycle that tried the re-harvest from this cloud sandbox hit the same proxy refusal `ops/indexnow.py --submit` already hits (confirmed directly this cycle too: a direct `connect_rejected` from the egress proxy against both `6s-success.com` and Google's own autocomplete host, not merely unconfirmed). That is a property of where the harvest was being run from, not of the data. `.github/workflows/keyword-demand.yml` (new) runs `ops/keyword_demand.py --source both` weekly from a GitHub-hosted runner, which already has ordinary outbound internet, the same fact `hourly-brief.yml`'s own IndexNow step already relies on. `ops/preflight.py`'s new `gate_keyword_demand_not_stale` holds it to that cadence so a silent failure to land a fresh reading does not go unnoticed the way the first several weeks of "unmeasured" did. The honest test itself has not run yet as of this correction; the fix is that it now can, on its own, without waiting on an operator cycle that happens to have network reach.

**The first real re-harvest landed the same day, fired by hand rather than waiting for Wednesday's cron, and it answers the question.** 2026-10-02T08:12:24Z, 151 seeds, 302 attempts, both canaries clean, 0 errors. Of the 13 complaint-shaped queries the harvest actually returned this time (the "always messy"/"always a mess" family), **9 are now `covered` and 2 more `partial`**, up from 0 `covered` on the very first title-only reading and 8 `covered` on the heading-aware re-score taken before the article shipped. Both rank-1 queries from the original finding, "why is my kitchen always messy" and "why is my bedroom always messy", are covered now. This is coverage (does a page carry the words), not rank or traffic, and it is not proof anybody has found the page: Search Console still owns impressions, and this sandbox still cannot read Umami directly. The two other clusters the original finding named have NOT moved the same way and should not be read as closed: "small space" is 1 covered / 26 partial / 10 gap of 37, and "cheap/budget/DIY" is 0 covered / 82 partial / 17 gap of 99, both still real, unaddressed content gaps, consistent with the original finding (neither has had a page written for it yet, unlike the complaint cluster).

**One thing deliberately not done.** The indexed article URL is `/articles/how-long-does-it-take-to-organise-a-room`, a British slug under an American title. Renaming it to match would trade the one URL we have actually confirmed is indexed for an unknown one plus a redirect, so the slug stays and the inconsistency is recorded instead.

**What the numbers say to do:** post to the one channel that already works
while the slow instrument warms up, and keep opening the video channels,
because a category like this is searched on YouTube and Pinterest as much as
on Google.

**Measured 2026-09-29, and it should change the order of this work: the 12 videos already published have sent this site zero visitors.** Read from the all-time referrer table, every arrival this site has ever had, not a 30-day window: direct 79 visitors, linkedin.com 11 plus com.linkedin.android 1, go.bsky.app 3 plus bsky.app 2, google.com 3, bing.com 1, hpanel.hostinger.com 1, buy.stripe.com 1 (a return from checkout). **youtube.com does not appear at all.** The 12 went up on 2026-09-03, so they have had 26 days.

That measures one thing and not another, and the distinction decides what to do next. It measures REFERRALS to this site, and on that the answer is unambiguous: zero. It says nothing about whether anybody watched them on YouTube, which is a real form of value and is visible only in YouTube Studio. So the sequencing that follows is not "stop making videos", it is **read the analytics for the 12 before hand-uploading 102 more**, because those two possibilities call for opposite work:

- If the 12 have meaningful views and simply do not link through, the fix is the description and end-card, and volume is worth adding.
- If the 12 have almost no views, more of the same will also have almost no views, and the problem is YouTube-side discovery (titles, thumbnails, Shorts, tags), not how many exist. Uploading 102 by hand would then be the most expensive way available to learn nothing.

This is a two-minute look at a screen only Phil can open, against 102 manual uploads, so it belongs before them rather than after. Recorded against `OWNER-ACTIONS.md` item 1.

**The same table names the channels that do work, and they are not the ones getting the effort.** LinkedIn has produced 12 of this site's visitors and Bluesky 5, against 4 from every search engine combined, for a fraction of the production cost of the video library.

**Closed 2026-09-30, scheduled operator: Bluesky was getting no effort because nothing prepared content for it, not because the channel is weak.** `ops/linkedin_drafts.py` has drafted Phil's LinkedIn posts for weeks and `ops/social_drafts.py` drafts for Facebook and X before either even has an account; Bluesky, already producing real visitors, had no equivalent. `ops/bluesky_drafts.py` + `.github/workflows/bluesky-drafts.yml` now draft and email 3 Bluesky posts a day from the same corpus, needing no new owner action (the SMTP secrets already exist). This does not change the constraint (O1) by itself; it removes the "not getting the effort" half of this paragraph's own complaint about the one channel already proven to convert.

**Corrected 2026-09-30, later the same day, this operator: "now draft and email" was a build claim, not a verified one, and it was false for its first several hours.** The workflow's own push-fallback (the safety net for when GitHub's cron runs late, which this file's own LinkedIn precedent shows is routine) counted its OWN `status=success` workflow runs as evidence a real send had happened, but a run that correctly stands down before the cron's target time is also, itself, a "successful" run. On a repository pushing dozens of times a day, that meant the fallback reported a clean gate on all 45 of its first day's runs while sending zero emails and creating zero rotation-advance commits, the exact "unchecked reported as passing" shape `CLAUDE.md` 0.4 names. Found, root-caused, and fixed the same day (the identical shape existed in `linkedin-drafts.yml` and `social-drafts.yml` too, both saved only by their own schedules eventually firing); a real Bluesky email sent at 14:16:46 UTC, followed by real Facebook/X and LinkedIn sends within the hour, each with its own dated rotation-advance commit now in `git log` as the evidence. New static gate (`gate_push_fallback_ledger_honest`) in `preflight.py` scans every workflow with a push fallback for this exact anti-pattern, so it cannot ship again unnoticed.

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
exactly that reason; a mailto fallback is what actually runs today.
**Measured 2026-09-30 rather than assumed, because "the footer's mailto"
implied something stronger than the shape it actually has:** every one of
the 115 zone pages and 45 of the 46 top-level pages carries a footer link
to `contact.html`, which holds the `mailto:support@6s-success.com`, so the
path is one click rather than zero but it exists on every page a visitor
can land on. The 46th, `invest.html`, carries its own investor-subject
mailto directly, which is right for that page rather than a gap. So nobody
who wants to reach us is stuck; they are just not captured into a list.
Real blocker: issue #15 (P0, decision) needs Phil to choose a separate
Listmonk instance for 6S, or hand the shared instance's sending identity to
6S and move Compassion Benchmark off it. Detail in `OWNER-ACTIONS.md` item 7/7a.

**Re-verified 2026-09-30 against the running container's own log, not carried
forward, and it turned up something the diagnosis above never recorded.** The
553 is real and unchanged: `553 5.7.1 <support@6s-success.com>: Sender address
rejected: not owned by user info@compassionbenchmark.com`, and no send has
succeeded since. But the same log shows the form was not merely withdrawn
before anyone used it. Listmonk had reached **subscriber id 4** by 2026-09-04,
and the opt-in e-mail for that subscriber failed with the 553 three times in
sixteen seconds, so it could never confirm. **Somebody typed their address in
during the one day the form existed, and the shared credential lost them.**

That is the strongest argument issue #15 has and it was not in the issue:
this is not a hypothetical channel with no demand, it is a channel that
captured a person on day one and dropped them. "0 subscribers" above stays
accurate in the sense that matters, because an address that never confirmed is
not a subscriber, but the number understates what was actually lost.

**Not worked around, deliberately.** Capture without sending is technically
easy (single opt-in, no confirmation mail) and it would be dishonest here: a
form that says we will write to you, on an instance that cannot write to
anybody, is a promise we know we cannot keep (`CLAUDE.md` section 8). The
mailto fallback stays until #15 is decided.

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
trailing 90 days, `ops/check_affiliate_trigger.py`). **Corrected 2026-09-30,
this operator: the "0 of 60 as of 2026-09-09" reading had sat uncorrected for
three weeks while the real count moved.** `ops/state.json`'s own
`affiliate_trigger`, measured the same day directly against the live
database (a session this cloud sandbox cannot reach), reads **1 of 60
outbound retailer click(s) in the last 90 days, from 1 visitor, 2026-09-30
12:25**. Still nowhere near T2 and still no application authorised; the
correction is that the number moved and nothing here said so. Re-litigate in
June 2027 or on the trigger, not monthly. This also
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
