# Revenue review, 4 September 2026

Every number here was measured today against Stripe, the analytics database, or
the live site. Nothing is estimated unless it says so.

---

## 1. Where the business actually is

| Measure | Value | Source |
|---|---|---|
| Gross revenue, all time | **$19.00** | Stripe, 1 charge, 2026-08-21 |
| Completed checkouts | **1** | Stripe |
| Expired checkouts | **19** | Stripe |
| Visitors, last 30 days | **52** (144 visits) | Umami database |
| Visitors per day | **1.7** | derived |
| Arrivals from Google | **0** | Umami, 30 days |
| Products live | 159 | catalogue |
| Videos built / published | 456 / 12 | disk, YouTube |
| Approved affiliate programmes | 0 of 10 | `ops/affiliate.py` |
| Email subscribers | 0 (Listmonk returns HTTP 500) | measured |

---

## 2. The finding that matters

**The catalogue is built for a business model that cannot reach $20,000 a month.**

97% of the 159 products are priced between $4 and $19. Here is what each price
point would require, at a generous 2% conversion rate:

| If revenue came from | Sales/month | Visitors/month | vs today |
|---|---|---|---|
| $4 micro-zone packs | 5,000 | 250,000 | **4,808x** |
| $19 whole-house pack | 1,053 | 52,632 | **1,012x** |
| $49 digital bundle | 408 | 20,408 | 392x |
| $250 virtual consult | 80 | 4,000 | 77x |
| $1,200 in-home reset | 17 | 833 | **16x** |

The 109 micro-zone packs are 69% of the catalogue. If every one sold once a
month, that is $436.

A realistic blend — **8 in-home resets + 42 virtual consults = $20,100/month
from 50 transactions** — needs 2,500 visitors/month, or 83/day. That is 48x
today's traffic, not 1,000x. It is the only mix on this list that is arithmetic
rather than fantasy.

Capacity check: 50 delivery events is **1.9 in-home days per week and 1.9
consults per working day.** One person can do that. It is also the ceiling —
services do not scale past the calendar, which is why proposal 4 matters.

---

## 3. The second finding

**The business sells in exactly one place, and that place has 1.7 visitors a
day.**

There is no Amazon listing (no ASIN anywhere in the repo), no Etsy shop, no
Gumroad, no marketplace of any kind. Everything depends on strangers finding
6s-success.com, which nothing currently points at.

Meanwhile these are finished and sitting on disk:

- `build/6S-Success-Home-Edition.epub` — 853 KB, complete, with a cover
- 155 print-pack deliverables, built and verified
- 456 videos with captions, 12 published

Fixing conversion on a page nobody visits is arithmetic on zero. Distribution
is the constraint, and SEO is only one form of distribution — the slowest one.

---

## 4. Proposals, ranked by expected value

### 4.1 Sell where buyers already are

List the book on **Amazon KDP** and the print packs on **Etsy**. Etsy's
organization-printable category has buyers searching right now; our 109 zone
packs are exactly that product. Amazon has the book audience.

This inverts the current model: instead of paying (in time) to bring strangers
to a site with no traffic, put the product in front of traffic that already
exists and let the marketplace do discovery.

Needs Phil: seller accounts. Everything else is ready.

### 4.2 Make the services the front door, not the footnote

$250 and $1,200 are where the goal is reachable, yet the site leads with the
method and buries the offer. The consulting page had no price in its served
HTML until today.

Reframe: the free quest and the zone guides are the top of the funnel; the
consult is the product. Digital packs are proof of expertise, not the business.

### 4.3 Publish the 102 videos

The only distribution asset we own outright. 456 built, 12 public, because the
12 were posted by hand. The uploader is built and dry-run clean; it needs one
OAuth step.

Search sends us nothing. YouTube is a search engine we have 456 answers for.

### 4.4 Add recurring revenue

Every product is a one-time sale, so revenue starts at zero every month. Even a
small subscription — a monthly zone plan, a household standard that refreshes,
a members' library — changes the shape from a treadmill to a base.

This is the answer to the capacity ceiling in section 2: services cannot scale
past Phil's calendar, but a subscription can.

### 4.5 Fix the corporate offer

**Corporate Lean 6S has no price and no buy path.** It is quote-only, and it is
almost certainly the highest-value item in the catalogue: Lean training
contracts are $5,000-$15,000, so 2-4 a month is the entire goal.

It is also the most defensible: Phil's Lean credentials are real, corporate
buyers have budget, and no consumer traffic is required. Two closes a month
beats 5,000 print-pack sales.

### 4.6 Repair the list

Listmonk returns HTTP 500 (Hostinger rejects the sender). With no list, all 52
visitors are one-time strangers and every marketing action starts from zero
again. It is a single configuration fix and it compounds.

---

## 5. What to stop

Do not add products. 159 SKUs for a business with one lifetime sale is not a
catalogue, it is a warehouse. Adding a 160th cannot help, and each one dilutes
the path to the few that matter.

Do not A/B test. At 1.7 visitors/day the registry itself computes 1,427 days to
significance. Make changes that are correct on their merits.

---

## 6. Honest limits

- The 2% conversion assumption is an industry benchmark, not our measurement.
  We have one sale, which supports no conversion estimate at all.
- Corporate contract values ($5,000-$15,000) are a market range, not a quote we
  have given or received.
- Etsy comparables could not be verified: Etsy blocks automated access.
- Operating profit cannot be computed. `COST-GOVERNANCE.md` records
  infrastructure cost as UNKNOWN, and no cost is recorded for Phil's time, which
  is the main input to every service in section 4.2.
- 19 expired checkouts are probably mostly our own testing. They should not be
  read as 19 lost customers.
