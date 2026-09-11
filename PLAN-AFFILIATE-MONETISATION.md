# Affiliate monetisation: the finalised plan

**Owner:** `commerce-manager`. **Written 2026-09-07.** **This file is a plan. It
changes nothing else.** No git command was run, Stripe was not called, no
account was created, no application was submitted, and no file but this one was
written.

Every number below is either measured today against this repository and the
live production site, quoted from a dated measurement already in the repository
with its source named, or labelled as an assumption with its bracket. Where I
could not look, the line says UNCHECKED rather than clean.

---

## Status update, 9 September 2026

Three things have changed since this plan was written. None of them changes its
answer; two of them strengthen it.

**Step 2 is done.** The `outbound-click` event shipped 2026-09-07 and is
verified working, not assumed: a real Target link was clicked in a headless
browser with navigation suppressed and the event fired with the right host and
page type. So the plan's own precondition, T1, is satisfied and the trigger is
now measurable.

**T2 is now watched rather than remembered.** `ops/check_affiliate_trigger.py`
evaluates it against the real event stream, excluding both `who=internal` and
`who=automated`, and the reading sits on the command deck. `gate_affiliate_trigger`
stays silent until it fires and then says so, because a line reading "0 of 60"
every run for a year is how a trigger stops being read. Current reading: 0 of 60.

That zero is not yet evidence. Outbound tracking has been live since 2026-09-07,
and in that window there were 237 zone pageviews from 2 visitors, both of them
crawler sessions. The human sample since this became measurable is zero, so the
count is not a statement about human behaviour and will not be one for a while.

**A fact this plan did not have.** The site links exactly two merchants:
target.com with 1,535 links and homedepot.com with 190. Both have already
declined us. So the 1,725 links cannot earn even in principle, at any traffic
level, until a different merchant is linked. That does not change the
conclusion, it sharpens it: section 0 says leave the links as they are because
they do a product job rather than a revenue job, and it turns out that is not
merely the best available choice, it is the only true description of them.

Related, for the day T2 fires: `amazon.com` is named nowhere in
`site/privacy.html`, and `zone_supplies._link()` refuses any host privacy.html
does not name. Amazon approval alone would therefore publish zero Amazon links.
Adding them is a product decision about which merchant we recommend, not a code
change, so it is recorded here rather than done. `ops/tests/test_affiliate_tagging.py`
pins that state so it is not rediscovered on approval day.

---

## 0. The answer, before the working

**Affiliate revenue cannot be a material line in this business for years, and
probably never at the scale this site is built for. It should be held as a
cheap option, not planned as income.**

The decisive number is section 2.5, so here it is up front. **At the exact
traffic level where the services line reaches $20,000 a month, 2,500 visitors,
the affiliate line earns about $7 a month.** Not $7,000. Seven dollars. That is
0.03% of the goal, and it is 3% of the contribution from a *single* $250
consult. There is no traffic level at which both lines are worth the same
attention, because the two are separated by roughly three orders of magnitude
per visitor.

So the plan is:

1. **Do not apply to anything today.** Not Amazon, not Impact, not CJ, not
   Rakuten. Every application spends a scarce, non-renewable resource, the
   first impression of a domain, against traffic that guarantees the outcome.
2. **Instrument the 1,717 links that already exist.** We cannot currently count
   a single outbound click. That one missing event is what makes every question
   below unanswerable, and it is half a day of work.
3. **Leave the links exactly as they are otherwise.** Unpaid, uncoded, and
   honestly disclosed. They are doing a real job that is not revenue.
4. **Apply to Amazon, and only Amazon, when a written click trigger fires**
   (section 7, T2). It is the only programme not routed through the network
   that already declined us, and everything on our side of its bar is built.
5. **Re-litigate this in June 2027 or when a trigger fires, not monthly.**

The honest one-line summary for the executive brief: *affiliate is a $10-a-month
line that costs a day of work to hold open, and it should be treated as such.*

---

## 1. Measured ground truth, 7 September 2026

| Measure | Value | How it was established |
|---|---|---|
| Product types in the catalogue | **123** | `ops/affiliate-catalogue.csv`, counted today |
| Types carrying a verified retailer link | **120** | `Link Status` column, counted today |
| Types deliberately left unlinked | **3** | `MPL-00115` oily rag can, `MPL-00113` pitch remover, `MPL-00120` clothing brush: no readable merchant stocks the type, 1-2 matches in 12-24 rendered results |
| Retailer links live on zone pages | **1,717** (1,527 target.com, 190 homedepot.com) | grepped across `site/zones/*.html` today |
| Zone pages carrying links | **114** | same |
| Links on the kit page | **8** | `site/kit.html` |
| **Unique link destinations** | **114** | deduplicated today. 1,717 links, 114 distinct URLs: the universal-kit items repeat on every zone page |
| Links carrying an affiliate or tracking code | **0** | grepped for `tag=`, `afid`, `clickid`, `irclick`: none |
| Zone pages carrying the disclosure block | **114 of 114** | `id="affiliate-disclosure"`, counted today |
| **Outbound clicks ever measured** | **0, because nothing measures them** | `site/assets/js/measure.js` read today: it fires on `buy.stripe.com`, `/downloads/`, `contact.html?ref=`, `corporate.html`. There is no branch for a retailer host |
| Approved affiliate programmes | **0 of 10** | `ops/affiliate-accounts.json` |
| Programmes declined | **5**, all at once | Impact declined Media Partner account **7700618** on 2026-08-29, citing its service agreement. Walmart, Ace, Home Depot, Lowe's and Target all sit behind that one account |
| Programmes actually still open to us | **3**: Office Depot (CJ, unconfirmed email), Etsy (Rakuten, login never activated), Amazon (needs a fresh application, OTPs expired) | `ops/affiliate-accounts.json`, read from the inbox 2026-09-06 |
| Visitors / visits, 30 days | **60 / 161**, 2.0 visitors a day | Umami database, `GOALS.md` 2026-09-03 |
| Revenue, all time | **$19.00**, one charge, and the buyer was a personal referral | Stripe, via `STATUS.md` |

**Verified against production today, not against the repository** (`CLAUDE.md`
0.3). `https://6s-success.com/affiliate-disclosure.html` returns 200 and carries
the sentence "Today, nothing on this site earns us a commission".
`/kit.html` returns 200 and serves its 8 retailer links.
`/zones/dining-room-the-beverage-or-coffee-station.html` returns 200, serves 11
retailer links and three references to the disclosure. The 404 recorded in
`OWNER-ACTIONS.md` 4 is closed: the deploy happened.

**What could NOT be verified today, and is therefore not asserted anywhere
below.** No published commission schedule was readable from our tooling.
Amazon's fee schedule at `affiliate-program.amazon.com/help/operating/schedule`
302s into a sign-in wall; `partners.target.com` is an empty JavaScript shell;
`homedepot.com/c/Affiliate_Program` returns 403. **Not one commission rate in
this document is a figure we read from a publisher.** Section 2 is therefore
built so that its conclusion holds across the entire plausible range rather
than resting on any single rate.

---

## 2. Question 1: is affiliate revenue worth pursuing here at all?

### 2.1 The chain, and which links we can actually measure

```
visitor -> lands on a page with links -> clicks out -> buys at the retailer
        -> basket value -> commission rate -> our revenue
```

| Link | Our value | Status |
|---|---|---|
| Visitors / month | **60** | measured |
| Share of pages carrying links | **115 of ~190** | measured; and they are the crawled ones (Googlebot fetched this site 178 times in 72 hours, `GOALS.md`) |
| Outbound click-through rate | **UNKNOWN** | nothing measures it. Bracketed 5-20% below |
| Retailer conversion on a search-results landing | **UNKNOWN** | assumption, bracketed 1-8% |
| Basket value | **~$30** | derived from our own catalogue: median estimated retail $10 low / $35 high, mean $17.92 / $54.35. This is a measured property of the catalogue, **not a measured order** |
| Commission rate | **UNKNOWN** | commonly cited industry range for home goods is 1-4%. **Unverified**, see section 1 |

Two of the six links are unmeasured because nothing on the site measures them,
and two are unverifiable because the publishers hide their terms behind a login.
That is the honest state of the inputs, and it is why the section below is a
grid rather than a forecast.

### 2.2 Earnings per outbound click, across the whole plausible range

EPC = basket x retailer conversion x commission rate, at a $30 basket.

| Retailer conversion \ commission | 1% | 2% | 3% | 4% |
|---|---|---|---|---|
| **1%** | $0.003 | $0.006 | $0.009 | $0.012 |
| **3%** | $0.009 | $0.018 | $0.027 | $0.036 |
| **5%** | $0.015 | $0.030 | $0.045 | $0.060 |
| **8%** | $0.024 | $0.048 | $0.072 | $0.096 |

**The entire grid spans a third of a cent to ten cents per outbound click.**
Take the middle cell, 3% conversion at 3% commission, as the working figure:
**$0.027 per click, call it under three cents.** Every conclusion below is
checked against the best cell too, and none of them changes.

This is the number that decides everything, and it is not close to the edge.
Even if every assumption is wrong by a factor of three in our favour, a click is
worth pennies.

### 2.3 What the links would earn today if every one of them paid

| Outbound CTR | Clicks / month | Revenue at mid EPC | Revenue at best EPC |
|---|---|---|---|
| 5% | 3 | **$0.08** | $0.18 |
| 10% | 6 | **$0.16** | $0.36 |
| 20% | 12 | **$0.32** | $0.72 |

**If Amazon, Target, Home Depot and Walmart all approved us this afternoon and
every one of the 1,717 links began paying tonight, this site would earn
somewhere between eight cents and seventy-two cents a month.**

A second way to feel the scale: **if every single one of the 1,717 links were
clicked exactly once, that is $46 at mid EPC and $103 at best.** Once. Ever.

### 2.4 What it earns at every traffic level we have a written target for

| Traffic scenario | Visitors / month | Affiliate at mid EPC, 10% CTR | at best EPC, 20% CTR |
|---|---|---|---|
| Today | 60 | $0.16 | $0.72 |
| `GOALS.md` O1 target, 500 visitors/week | 2,167 | **$5.85** | $26.00 |
| Traffic that makes the services blend hit $20k | 2,500 | **$6.75** | $30.00 |
| 10,000/month, a 167x step change | 10,000 | $27.00 | $120.00 |
| 50,000/month, a 833x step change | 50,000 | $135.00 | $600.00 |

To make affiliate alone produce **$500 a month** at mid EPC requires **18,519
outbound clicks**, which at a 10% CTR is **185,000 visitors a month, 3,086x
today's traffic.** At the single most generous cell in the grid and a 20% CTR it
is still 41,667 visitors a month, 694x.

To make affiliate alone produce the **$20,000 goal** requires **740,741
outbound clicks a month.** At 10% CTR that is **7.4 million visitors a month.**
That is not a business plan, it is a different company.

### 2.5 Against the services line, which is the fair comparison

`REVIEW-COMMERCE-2026-09-07.md` 3.1 records contribution per order, measured
against the real 2.9% + $0.30 Stripe load: **$18.15 on the $19 print pack,
$242.45 on the $250 consult, $1,164.90 on the $1,200 in-home reset.**

| To equal the contribution of one $250 consult | Outbound clicks required |
|---|---|
| At best-case EPC ($0.096) | **2,526** |
| At mid EPC ($0.027) | **8,980** |
| At worst-case EPC ($0.003) | **80,817** |

At today's traffic and a generous 20% CTR, twelve clicks a month, the mid-case
figure is **748 months of affiliate income to equal one consultation.**

And the comparison that closes the argument, restated from section 0: at the
2,500 visitors a month that `REVENUE-REVIEW-2026-09-04.md` 2 shows would let 8
in-home resets plus 42 consults reach $20,100, **the same 2,500 visitors
generate about $6.75 of affiliate revenue.** The traffic that solves the
business does not incidentally solve affiliate. Affiliate needs a different
website with a different purpose.

### 2.6 The verdict, plainly

**No. Affiliate is not worth pursuing as revenue, and it must not appear in any
path to $20,000.** `REVIEW-COMMERCE-2026-09-07.md` 6 reached the same
conclusion from the account statuses; this section reaches it from the
arithmetic, which is the stronger reason because it does not change when an
approval lands.

It *is* worth holding as an option, for three reasons that are all cheap:

- **The tooling already exists and is finished.** `ops/affiliate.py` builds the
  link, renders the correct disclosure conditionally, and refuses to invent a
  URL. `gate_affiliate` in `ops/preflight.py` and the fulfil-orders workflow both
  read all delivered documents and fail closed on an affiliate link inside one.
  The work at approval time is pasting one publisher id into a JSON file.
- **The links are already there and already useful** for a non-revenue reason
  (section 4).
- **The option has an expiry we can write down** (section 7, T5), so holding it
  costs no recurring attention.

What is *not* worth doing is any work whose only justification is future
commission. That includes deep-linking to specific products, building a price
comparison, adding merchants, or writing "best X" articles. Each of those is a
real cost against a line worth single-digit dollars.

---

## 3. Question 2: the sequence, if and when it is pursued

### 3.1 What must be true before ANY application, without exception

**Gate A: we can count an outbound click.** Today we cannot, and this is
disqualifying for three separate reasons, any one of which would be enough.

1. Every network application asks what traffic the property has and what it
   does. We can answer the first from Umami and cannot answer the second at all.
2. We cannot price the Amazon decision in 3.2 without a measured CTR, so
   applying is a coin flip we chose not to look at.
3. If an approval ever lands, we would switch on 1,717 paying links with no
   baseline to compare against, and would never know whether they worked.

**Gate B: the disclosure promise is honoured in the same deploy as the first
code.** `site/affiliate-disclosure.html` currently makes a written promise:
*"The day that changes, this page changes with it, and every link it applies to
will be marked where you see it, not only here."* That is a commitment to
customers, in production, today. It is not a nice-to-have to be done in the next
cycle. `ops/affiliate.py` already renders the correct block conditionally, so
the mechanism exists; the requirement is that no publisher id is pasted in
without the deploy that updates the page going out with it.

**Gate C: the link `rel` is corrected.** The 1,717 links today carry
`rel="nofollow noopener"`, which is correct and safe for an unpaid link. A paid
link should carry `sponsored`. This is a one-line change in the generator, bound
to approval, not before.

**Gate D: the search-URL question is answered in writing.** See 3.5. This is the
one that could make the whole exercise moot and nobody has checked it.

### 3.2 Amazon's qualifying-sales window, and what 2 visitors a day means

Amazon Associates closes a new account that does not refer **three qualifying
sales within 180 days** of sign-up, after which the applicant must apply again.
**Flagged for verification:** this is the rule as we understand it and it could
not be read from Amazon today (section 1). It must be re-read on the application
page before anyone applies, and if the window or the count differs the
arithmetic below must be redone.

At **2.0 visitors a day, 180 days is 360 visitors.** Expected qualifying sales,
where a "qualifying sale" is a visitor who clicks out and buys within Amazon's
attribution window:

| Outbound CTR | Amazon conversion | Expected sales in 180 days | P(at least 3) |
|---|---|---|---|
| 3% | 5% | 0.54 | **2%** |
| 3% | 10% | 1.08 | 12% |
| 10% | 5% | 1.80 | 27% |
| 10% | 8% | 2.88 | **55%** |
| 20% | 8% | 5.76 | 93% |
| 20% | 10% | 7.20 | 98% |

(Poisson, which is the right model for rare independent events. Amazon's own
site conversion is genuinely high, which is why the optimistic rows are not
absurd.)

**Two things follow, and the second is the interesting one.**

First, applying today is a **coin flip at best and a 2% shot at worst**, and the
entire spread is caused by one number we do not measure. Losing the flip is not
free: the account closes, the application must be redone, and the domain has a
declined history at the one network that is not Impact.

Second, and this is why measuring is not a stalling tactic: **the Amazon gate is
much closer than the money is.** Passing 3-in-180 needs on the order of 120
outbound clicks over the window at a 5% Amazon conversion. That is around 20
clicks a month. At a 10% CTR we would need roughly 200 visitors a month, about
3x today, which is inside the range O1 is already trying to reach. **The gate is
reachable long before the revenue is meaningful.** That is worth knowing and it
is worth not guessing about, which is exactly what Gate A buys.

### 3.3 The order, and the readiness evidence for each

**1. Amazon Associates. The only one to pursue.**
It is in-house rather than Impact-routed, so the 2026-08-29 decline does not
touch it. Everything on our side of its published bar is built and was checked
against the Operating Agreement directly (`OWNER-ACTIONS.md` 4): 189 original
public pages, a privacy page disclosing tracking, an FTC-compliant disclosure
page in the footer of every page and in the sitemap, and a hard build gate that
refuses to ship a delivered document containing an affiliate link. The gap is
traffic and the OTPs. **Blocked on Phil, and deliberately held until T2 fires.**

**2. Etsy through Rakuten. But almost certainly for the wrong reason.**
The Rakuten login from 29 August was never activated and has probably expired
(UNCHECKED). Before anyone spends a click on it, note that
`REVENUE-REVIEW-2026-09-04.md` 4.1 proposes listing our own print packs on Etsy.
**Being an Etsy seller and being an Etsy affiliate are different businesses and
the seller path is worth orders of magnitude more**, because it puts our $19
product in front of traffic that already exists rather than earning a few
percent of somebody else's $30 basket. If Etsy is opened at all, open it as a
shop. The affiliate application is not a priority and may be a distraction from
the one that matters.

**3. Office Depot through CJ. Low value, near-zero cost.**
CID 8057711 exists but the publisher email was never confirmed, and an
unconfirmed publisher account cannot be approved for any advertiser (UNCHECKED
whether the confirmation link still works). Office Depot is a poor fit for a
catalogue that is 83 Target rows and 37 Home Depot rows: almost nothing we
recommend is an office-supply item. Confirming the email keeps the account
alive at a cost of one click; applying to advertisers should wait for the same
evidence Amazon waits for.

**4. Impact. Not before a step change. See 3.4.**

**5. Container Store, Wayfair, and everything else in
`ops/affiliate-accounts.json` marked "not applied". Leave them alone.** They are
rows in a file, not a plan. Adding a merchant multiplies link maintenance across
114 pages for a share of a line worth ten dollars.

### 3.4 Impact: what has to be true before we go back

Impact declined partner account 7700618 on 2026-08-29 against a site with 52
visitors in the preceding thirty days, and the decline cited the service
agreement rather than any fixable defect. `OWNER-ACTIONS.md` 4 already contains
the right instinct: *"a network that has just declined a site with 52 visitors
in thirty days will decline it again."*

**Re-applying to Impact before a step change is the single most likely way to
turn a recoverable "no" into a permanent one.** Networks keep application
history against the domain and the entity, and a pattern of repeated declines is
worse evidence than a single one.

Written condition, in section 7 as T3. It is deliberately far away.

### 3.5 The structural risk nobody has checked, and it could void the entire link inventory

**Every one of the 1,717 links is a retailer search-results URL**, chosen on
purpose: a search survives a product going out of stock, and it does not pretend
we picked a brand we have not tested. That reasoning is sound and it is written
on the disclosure page.

**It may also be unmonetisable.** Affiliate programmes commonly require links to
be generated through the network's own tooling and to point at product or
category pages, and some terms restrict or prohibit tracking on search-results
URLs. **I could not verify this for any of our merchants**, because CJ's and
Impact's publisher terms are behind their signup flows and Amazon's schedule is
behind a login (section 1).

If it turns out that search URLs cannot carry a code, then the choice is:

- convert 114 destinations to product deep links, which reintroduces exactly the
  out-of-stock decay the search links were designed to avoid, across 114 pages,
  for a line worth single-digit dollars a month, **or**
- accept that the links never pay and stop treating affiliate as an option at
  all.

Given section 2's arithmetic, **the answer would be the second one**, and it
would be the right answer. This must be checked at application time, before any
work is done to convert anything. It is Gate D.

---

## 4. Question 3: what we do in the meantime

### 4.1 The links exist and earn nothing. Is that right?

**Yes, and it should stay that way until a trigger fires.** Not as a compromise,
but because the links are not there to earn.

A zone instruction that says *use a pH-neutral cleaner and a crevice
attachment* and then leaves the reader to work out what that is, is an
incomplete instruction. The link finishes the sentence. `CLAUDE.md` 3 puts
function before organisation and root cause before product, and every one of the
123 rows carries a `Why Recommended` line that names the root cause in the
method's own terms: *"Too many steps is the reason cleaning stops happening"*,
*"An inconsistent standard is a root cause"*. That is `CLAUDE.md` 48's
explainable recommendation, already implemented, at a scale of 123 rows.

**The links earn something already. It is not commission, it is the reason
somebody trusts the next page.** The 114 zone pages are the surface Googlebot is
actually fetching, they are the only paid offer's home, and a supply list that
resolves is a better page than one that does not.

There is also a real asset in what we currently look like from the outside: a
site that says, in production, *"Today, nothing on this site earns us a
commission"*, and means it. `REVIEW-COMMERCE-2026-09-07.md` 6 calls that honesty
an asset rather than a problem, and it is right. It is also, incidentally, the
best possible position from which to eventually add a code, because the
disclosure will have been true before it was convenient.

**The three unlinked types stay unlinked.** `MPL-00115`, `MPL-00113` and
`MPL-00120` were withheld because the retailer's own rendered results did not
match the product type (1 of 12, 2 of 12, 1 of 24). That rule, encoded in
`retailer_link()` as *a URL whose status does not begin "verified" is treated as
absent*, is worth more than three links. Keep it.

### 4.2 The one change worth making: count the click

**Add an outbound retailer click event to `site/assets/js/measure.js`.** It is
the only affiliate work that should happen before an approval, and it should
happen soon.

The file already has the exact shape needed: a delegated click listener that
branches on `href`, with a queue for when Umami has not parsed yet, and an
internal-traffic flag so Phil's own clicks are labelled rather than counted.
A retailer branch sits alongside the existing `buy-click`, `free-download` and
`quote-click` branches.

Suggested event and dimensions, consistent with `CLAUDE.md` 47 and the existing
file's own privacy discipline (bucketed, never a fingerprint):

- event: `retailer-click`
- `merchant`: the host, `target` or `homedepot`
- `product`: the catalogue `Product ID`, e.g. `MPL-00008`, read from a
  `data-mpl` attribute the generator writes. **Read, never guessed.** The
  existing `buy-click` branch already refuses to infer a SKU that the page did
  not declare, and that rule cost us seven unattributable buy-clicks precisely
  because it was not followed earlier; do not repeat it here.
- `from`: the page type, as the existing helper already produces
- `zone`: the zone slug

**What it buys, in order of value:**

1. **It prices the Amazon decision.** T2 in section 7 is written directly
   against this count and cannot fire without it.
2. **It is the evidence a network asks for** (section 5.3). "Our supply lists
   sent 340 clicks to Target last quarter" is a media kit. "We have 60 visitors"
   is a decline.
3. **It tells us which product types people actually want**, which is a
   merchandising input worth more than the commission: it feeds `kit.html`, it
   tells `content-editor` which zones have live purchase intent, and it tells
   `product-manager` which micro zones are worth a deck.
4. **It closes a measurement hole**, which `CLAUDE.md` 0.4 treats as a defect
   class in its own right: the highest-intent action available on 115 of our
   pages currently leaves no trace at all.

**Effort:** about half a day including the generator attribute. **Position
against the constraint:** independent, and it pays at any traffic including this
one. **Acceptance:** a click on a retailer link on a live zone page produces one
`retailer-click` event in Umami carrying a real `Product ID`; internal clicks
carry `who=internal`; the event does not block or delay the navigation; no
event fires for non-retailer links.

**What this change explicitly is not.** It is not a step toward monetising.
It would be the correct change if we decided today never to run an affiliate
programme, because the question it answers, *do people act on our supply
recommendations*, is a product question about whether the instructions work.

### 4.3 What must NOT change while we wait

- **Do not add a code to a single link.** Zero approvals exist. A code without
  an approval is a broken link at best.
- **Do not soften the disclosure to make a future switch easier.** It is
  accurate today; accuracy is the point.
- **Do not reorder, re-rank or re-word a recommendation for any commercial
  reason.** `CLAUDE.md` 48 and the disclosure page both promise that a
  commission decides nothing about what is listed, in what order, or what is
  said about it. That promise has to be true *before* there is a commission,
  or it was never a promise.
- **Do not add merchants, deep links or a price comparison.** Section 2.6.
- **Do not put a link in anything a customer receives.** Enforced by
  `gate_affiliate` and by the fulfil-orders workflow, which read all delivered
  files and fail closed. Leave both gates in place; they are the only part of
  this system that is load-bearing today.

---

## 5. Question 4: the failure modes, with Impact as the worked example

### 5.1 What actually got us declined

Impact declined Media Partner account **7700618** on **2026-08-29**, citing its
service agreement, against a property with **52 visitors in the preceding 30
days**. Five programmes closed on one decision because all five route through
one partner account.

The proximate cause is almost certainly the simplest one: **there was nothing to
review.** A network's publisher review asks what audience the property has and
how links will be used. Our answers on 29 August were: an audience of 52, one
lifetime sale to a personal referral, no measured outbound clicks, and, at that
moment, a disclosure page that **returned 404 in production** (`OWNER-ACTIONS.md`
4 records that the live site was still an older build). A reviewer opening
6s-success.com that week would have found a genuinely good site with no
audience and, on the page they were most likely to check, a 404.

**Note the second-order failure, which was ours and was worse.** The decline sat
**unread in the support inbox for eight days**. During those eight days
`ops/affiliate-accounts.json` recorded the applications as pending *our* action,
`OWNER-ACTIONS.md` asked Phil to go and click a verification link that no longer
led anywhere, and an earlier pass had logged the **subject line** "Application
Update" and assumed what it meant. This is exactly the pattern `CLAUDE.md` 0.4
names: *unknown is not unused, and unchecked is not passing.* A subject line is
not a reading. The fix already shipped, `preflight.py` now flags unread
third-party mail that may need a decision, and that gate is more valuable than
any programme this plan discusses.

### 5.2 What would get us declined again

1. **Re-applying to Impact with the same evidence.** 60 visitors instead of 52
   is not a different application. This is the most likely repeat failure and it
   is entirely under our control.
2. **Applying to Amazon before the window can be met.** Section 3.2: a 2% to 55%
   chance of surviving 180 days. The account closes on its own, no human decides
   anything, and we would have converted a live option into a second declined
   history.
3. **Applying with an unconfirmed account.** CJ cannot approve an advertiser for
   a publisher who never confirmed their email. Submitting anyway wastes the
   advertiser application, not just the account one.
4. **A disclosure that is wrong on the day a reviewer looks.** It was wrong once
   already, in the opposite direction: production `/kit.html` opened with *"Some
   of the links below are affiliate links, which means 6S Success may earn a
   commission"* on a page where every product read "No retailer link yet",
   because the generator rendered the block unconditionally. **Claiming a
   material connection we do not have is the same class of fault as concealing
   one we do**, and a network reviewer reads it as sloppiness about compliance,
   which is the one thing they are screening for.
5. **A stale or mismatched property.** Applying with a domain whose live build
   is older than the repository. `CLAUDE.md` 0.3 exists because of this;
   verify production on the day of any application, not the repository.

### 5.3 What evidence a network actually wants

Stated as what we could show, not as a claim about any specific network's
undisclosed criteria:

| What they ask | What we could show today | What would make it strong |
|---|---|---|
| Monthly sessions | 60 visitors / 161 visits | four figures, trending |
| Traffic sources | direct, LinkedIn (17), 2 search referrals ever | organic search as the majority |
| What the site is | 189 original pages, 114 micro-zone guides, a method | unchanged, this part is genuinely good |
| Where links would sit and why | 114 zone pages, disclosure above the links, a written root-cause reason per product | unchanged, this part is genuinely good |
| Compliance | privacy page disclosing tracking, FTC disclosure in every footer and in the sitemap, a build gate refusing links in delivered files | unchanged, this is better than most applicants |
| Evidence the audience acts | **nothing. Zero measured outbound clicks** | the `retailer-click` event in 4.2 |

**We are strong on everything a network can read and empty on everything a
network can count.** That is the whole diagnosis of the Impact decline in one
line, and only one row of that table is fixable by us in half a day.

---

## 6. Question 5: what must never happen

These are not preferences. Each one trades trust for a line worth ten dollars a
month, which makes them the worst trades available anywhere in this business.

1. **Never put a code on a link without the disclosure changing in the same
   deploy.** The disclosure page carries a written promise to do exactly this.
   Breaking it is worse than never having promised.
2. **Never let a commission influence what is recommended, its order, or its
   wording.** `CLAUDE.md` 48. If a product's `Why Recommended` line would not
   survive a reader who pays us nothing, it does not belong on the page.
3. **Never swap a recommended product type for a higher-paying one.** The 123
   rows exist because a micro zone needs that kind of thing. A commission is not
   a reason and never becomes one.
4. **Never add a product to the catalogue because it is commissionable.** The
   list is 123 types because the method calls for 123 types.
5. **Never put an affiliate link in a book, PDF, deck, print pack or emailed
   file.** Prohibited by Amazon's Operating Agreement and by common terms
   elsewhere, and we would hold to it regardless: the customer paid for that
   file and it must not be an advert. Two gates enforce it. Never weaken them.
6. **Never publish an unverified link.** The `verified`-prefix rule that
   withheld three of the 123 stays. A recommendation that sends a trusting
   reader nowhere costs more than the click was worth.
7. **Never fabricate a review, a rating, a testimonial or a "best pick".** There
   are none on this site and nobody has given us one. `CLAUDE.md` 8.
8. **Never state or imply a commission rate, an earning, or a partnership we do
   not hold.** Including on the disclosure page, in a media kit, or in an
   application.
9. **Never overstate traffic in an application.** Beyond the obvious, networks
   can measure the property they are being sold.
10. **Never add an ad network, a tracking pixel or a third-party script to make
    the pages "monetisable".** `site/privacy.html` states the site runs none.
    That statement is worth more than the entire affiliate line.
11. **Never gate a supply recommendation behind a click-out.** The honest answer
    is often *you already own something that will do this*, and the disclosure
    page says so. Keep saying it.
12. **Never re-apply to a network on a reflex after a decline.** Section 5.2.

---

## 7. Question 6: the decision, and the triggers that end the argument

### D-019 (proposed): affiliate is an option, not a revenue line

**Decision.** Affiliate revenue is removed from every revenue plan, forecast,
roadmap and dashboard revenue row until an approval exists **and** a measured
click volume justifies it. The 1,717 existing links stay exactly as they are:
unpaid, uncoded, disclosed, and justified by the instruction they complete. One
piece of work is authorised: instrumenting the outbound click.

**Rationale.** At the traffic level where the services line reaches $20,000 a
month, the affiliate line reaches about $7 a month. The two are separated by
roughly three orders of magnitude per visitor, so no plausible improvement in
traffic, click-through, commission rate or approval status makes affiliate
material within the horizon of this business.

**Evidence.** Section 2, built on measured traffic and a measured catalogue,
with the two unknowable inputs bracketed across their full plausible range. The
conclusion holds in every cell of the grid.

**Alternatives considered.** (a) Apply to everything now: rejected, section 3.2
and 5.2. (b) Re-apply to Impact: rejected, section 3.4. (c) Convert the 114
search URLs to product deep links to improve conversion: rejected, section 3.5,
it multiplies maintenance for a line worth single-digit dollars. (d) Remove the
retailer links entirely to simplify: rejected, section 4.1, they are doing a
product job, not a revenue job.

**Consequence.** `GOALS.md` O4, *"Turn the catalogue into affiliate income"*,
is the wrong objective as written. It is currently ranked fourth of six with
targets of 3 approved programmes and 100 linkable products, which measures
paperwork rather than money. **Recommendation to `6s-ceo`: retire O4 as a
revenue objective and, if it survives at all, restate it as a measurement
objective owned by the click event in 4.2.** That is a `6s-ceo` call, not a
`commerce-manager` one, so it is recorded here as a recommendation and nothing
in `GOALS.md` was touched.

### The triggers, written down so this is not re-argued

| ID | Trigger | Action when it fires | Who |
|---|---|---|---|
| **T1** | None. Do it now. | Ship the `retailer-click` event (4.2). No application before it exists. | `software-engineer` + `analytics-intelligence` |
| **T2** | **Measured `retailer-click` count reaches 60 in a trailing 90 days**, internal traffic excluded | Apply to **Amazon Associates only**. 60 in 90 days projects to ~120 across a 180-day window, which at a 5% Amazon conversion gives an expected 6 qualifying sales and a ~94% chance of clearing 3. **Re-read Amazon's actual window and count on the application page first** (3.2) and redo this arithmetic if either differs. | Phil, application only he can make |
| **T3** | **All three**: (a) 1,000+ visitors a month for 3 consecutive months, (b) a public page describing the property and its audience exists, (c) the date is on or after **2027-03-01** | Consider one Impact re-application, with the traffic figures stated plainly. Not before all three. | Phil |
| **T4** | An approval of any kind lands | Before pasting the publisher id: confirm the programme permits tracking on **search-results URLs** (3.5, Gate D). If it does not, do nothing further and let T5 close it. If it does: paste the id, deploy the disclosure change and the `rel="sponsored"` change **in the same deploy** (Gates B and C), then `python ops/affiliate.py --status` and `--check` must both pass before it goes live. | `commerce-manager` + `qa-reviewer` |
| **T5** | **2027-06-30 arrives with no approval, or the trailing-90-day `retailer-click` count is still under 60** | **Affiliate is formally retired.** Set every row in `ops/affiliate-accounts.json` to `retired`, delete the objective, keep the links and the disclosure exactly as they are, and stop spending any attention on it. | `commerce-manager` |
| **T6** | A network declines us again | Record the date and the stated reason in `ops/affiliate-accounts.json` **by reading the email, not the subject line**, and add 12 months to that network's next eligible date. | whoever reads the inbox |

**Until a trigger fires, the correct amount of affiliate work is zero**, and a
cycle that reports "no affiliate progress" is reporting compliance with this
plan, not a failure.

**What would make me rewrite this file.** Traffic reaching five figures a month
with a measured outbound CTR above 15%, which would move the mid-case line from
$7 to something worth an argument. A commission rate published by a merchant we
actually use that is far outside the 1-4% band. Or Phil naming affiliate as a
strategic aim for a reason that is not revenue. Nothing else.

---

## 8. Honest limits of this plan

- **No commission rate here was read from a publisher.** Amazon's fee schedule
  302s to a sign-in wall, Target's partner site is an empty JavaScript shell,
  Home Depot 403s. The 1-4% band is the commonly cited industry range for home
  goods and is **unverified**. Section 2 is a grid rather than a forecast for
  exactly this reason, and its conclusion holds across every cell.
- **Outbound click-through rate is not merely unmeasured, it is unmeasurable
  today.** Every CTR in this document is an assumption bracket. This is the
  single largest source of uncertainty and section 4.2 is the fix.
- **Retailer conversion is an assumption.** A click landing on a *search results*
  page almost certainly converts worse than a product deep link, and we have no
  figure for either.
- **The $30 basket is derived from our own catalogue's estimated retail band,
  not from an observed order.** Nobody has ever bought anything through these
  links. **Updated 2026-09-10:** that used to end "as far as anyone can know,
  because nothing counts", and now something does. The outbound click event
  shipped 2026-09-07 and is verified working, and it has recorded zero clicks.
  Separately, this business HAS taken one payment, $19 on 2026-08-21, but it was
  a direct purchase of our own product rather than anything through a retailer
  link, so it changes nothing in this section.
- **Amazon's 3-qualifying-sales-in-180-days rule could not be verified today**
  and is flagged for re-reading before any application. If the window or the
  count differs, 3.2 and trigger T2 must both be redone.
- **Whether affiliate codes may be attached to search-results URLs is
  UNCHECKED** for all of our merchants, and it could void the entire link
  inventory. Section 3.5.
- **The CJ and Rakuten confirmation links from 29 August are UNCHECKED** and
  have very likely expired, as the Amazon OTPs did.
- **The Impact decline reason is quoted as given**, "its service agreement". The
  attribution to low traffic in 5.1 is my inference, tier 8, not a statement
  Impact made.
- **Contribution is the deepest honest line anywhere in this business.**
  `COST-GOVERNANCE.md` records infrastructure cost as UNKNOWN and no cost is
  recorded for Phil's time. Affiliate revenue would be nearly pure contribution,
  which is its one genuine advantage over a service, and it does not come close
  to compensating for being three orders of magnitude smaller.
- **Nothing here rests on customer research, reviews or testimonials, because
  none exists.** One customer, ever, and he was a personal referral.
