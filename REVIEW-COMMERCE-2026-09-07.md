# Commercial review, 7 September 2026

**Owner:** `commerce-manager`. **Scope:** the catalogue, the deck line, the
services funnel, corporate, and pricing coherence. **This file is a report. It
changes nothing else.**

Every number below is either measured today against the repository and the live
site, quoted from a dated measurement already in this repository with its source
named, or labelled as a hypothesis with its tier. Where I could not look, the
line says UNCHECKED rather than clean.

**What I did not do, deliberately:** no git command, no Stripe call of any kind,
no edit to any file but this one. Three findings below therefore end in
"unchecked against Stripe", and that is the honest state of them, not an
oversight.

---

## 0. What is actually true this morning

| Measure | Value | Source |
|---|---|---|
| Gross revenue, all time | **$19.00**, one charge, 2026-08-21, a personal referral | Stripe, via `STATUS.md` |
| Strangers converted, ever | **0** | same |
| Checkout sessions, ever | **20**: 1 completed, 19 expired | Stripe, via `STATUS.md` / `ROADMAP-2026-2029.md` |
| Sessions quoted a price we do not charge | **7 of 20 (35%)**, $18.00 against an advertised $9.99 | duplicate BK-EB product, archived 2026-09-06 |
| Visitors / visits, 30 days | **52 / 144** | Umami, `GOALS.md` 2026-09-03 |
| Buy-clicks, ever | **9, from 7 visitors**; 7 of the 9 resolved to `sku: "unknown"` | `site/assets/js/measure.js` |
| SKUs live | **159**, 155 with a live payment link | `site/assets/js/data.js`, counted today |
| SKUs that are strict subsets of `PACK-HOUSE` ($19) | **149 (94%)** | `super` field, counted today |
| Approved affiliate programmes | **0 of 10**; Impact declined the partner account 2026-08-29, shutting five at once | `ops/affiliate-accounts.json` |

**The one fact that reframes the catalogue.** The only product this business has
ever sold is the superset that contains 149 of the others. Everything else in
the catalogue is a slice of the one thing somebody bought.

**The second fact, and it is new since `DECISIONS.md` D-016 was written.** The
duplicate Stripe product that quoted $18 existed *because the catalogue passed a
hundred SKUs*: `ops/stripe_catalog.py` took Stripe's first page as the whole
account, stopped recognising what it had already made, and created a second
product, price and link for every SKU (`ops/stripe_dedupe.py` docstring). So the
catalogue's size was not merely unproductive. It was the proximate cause of the
only measured, revenue-destroying defect this business has had. A tier of 109
SKUs that has earned $0 broke the checkout of the one that was earning.

That pagination bug is fixed (`list_all` now pages properly, verified by reading
it today). What is not fixed is the class of exposure, which is section 5.

---

## 1. The catalogue: 159 SKUs against one lifetime sale

### 1.1 Shape, measured today

| Tier | Count | Price | Nominal value | Sold, ever |
|---|---:|---:|---:|---:|
| Micro zone pack | 109 | $4 | $436 | 0 |
| Room pack | 19 | $9 | $171 | 0 |
| Situation kit | 15 | $14 | $210 | 0 |
| Area bundle | 6 | $16 | $96 | 0 |
| Whole House Print Pack | 1 | $19 | $19 | **1** |
| Books, manual, bundle | 3 | $9.99 / $29 / $49 | $87.99 | 0 |
| Free (deck, standards, quest) | 3 | $0 | - | n/a |
| Services | 3 | $250 / $1,200 / quoted | - | 0 |

### 1.2 The arithmetic that decides what stays

The $4 tier is 69% of the catalogue. **If every one of the 109 packs sold once a
month, that is $436 gross and $390 contribution: 2.2% of the goal.** It is not
that they sell badly. It is that the whole tier, fully subscribed, is a rounding
error against $20,000, and each one carries a 10.5% Stripe fee load (measured:
the real transaction was $19.00 gross, $18.15 net, exactly 2.9% + $0.30).

Per-SKU demand evidence does not exist in either direction. Nine buy-clicks
ever, seven of which cannot be attributed to a SKU at all because the link id
was not in a hand-typed table. **So no retirement below can be justified by
"nobody bought it", and I am not going to pretend otherwise.** The defensible
tests are structural, and there is one that discriminates cleanly:

> **Can a stranger reach this SKU without first arriving at the shop?**

- 109 zone packs: yes. Each has a zone page, and the 114 zone pages are what
  Googlebot is actually fetching (178 fetches in 72 hours, `GOALS.md`).
- 19 room packs: yes. 20 room pages, and D-016 made the room pack their lead.
- 15 situation kits and 6 area bundles: **no.** Verified today by grep across
  all 193 HTML files: `KIT-*` and `AB-*` appear on exactly one page,
  `shop.html`. No landing page, no zone page, no room page, no article, no
  video, no schema of their own. `shop.html` has produced no measured organic
  entry.

A SKU that is reachable only from a shop nobody visits is not a product. It is a
row in a table with a live payment link attached.

### 1.3 Retire now: the 6 Area Bundles

`AB-WET-ROOMS`, `AB-SLEEPING`, `AB-STORAGE`, `AB-LIVING`, `AB-THRESHOLDS`,
`AB-FOOD`. $16 each, 6 SKUs, $96 nominal, $0 realised.

**Why.** They charge **84% of the $19 price for 12-20% of its 684 cards**
(`PRICING.md` 0.3, recomputed today and correct). They are the one tier that
maps to no job a customer names out loud: nobody with a messy bathroom thinks
"every wet room". `PRICING.md` 0.3 already recommends exactly this and stopped
short only because it required a Stripe write. And `ops/build_catalog.py`
asserts only that nothing is priced *at or above* $19, which every one of these
passes; a floor of absurdity is not a value test.

**Evidence tier.** 2 for the structure and prices (read from `data.js` and the
built files today). 8 for the judgement that the curation is not worth $16.
There is no demand measurement in either direction.

**Effort.** 0.5 day, staged. **Acceptance:** removed from `data.js` and
`shop.js` category order; `python ops/build_catalog.py` regenerated; deployed;
the live shop verified to no longer list them; **then and only then** the Stripe
products archived, with the live site read first (`ensure_link` already refuses
to retire a link production is serving, and `CLAUDE.md` 0.3 records what
happened the one time that check did not exist); definitions preserved in
`ops/retired-skus.json` with the reason.

**Constraint position.** Independent. It removes 18 live Stripe objects and one
merchandising tier that cannot be found; it pays at any traffic level, including
this one.

### 1.4 Retire now, with one door left open: the 15 Situation Kits

`KIT-MOVING-IN`, `KIT-MOVING-OUT`, `KIT-NEW-BABY`, `KIT-BACK-TO-SCHO`,
`KIT-HOLIDAY-HOST`, `KIT-DOWNSIZING`, `KIT-SPRING-RESET`, `KIT-SMALL-APARTM`,
`KIT-WORKING-FROM`, `KIT-PET-HOUSEHOL`, `KIT-AGEING-IN-PL`, `KIT-POST-RENOVAT`,
`KIT-FIRST-HOME`, `KIT-SHARED-HOUSE`, `KIT-RENTAL-HANDO`. $14 each, $210
nominal, $0 realised.

**Why, and the argument against.** These are the only grouping in the catalogue
keyed to a life event, which is closer to how people search than a room is
("moving house checklist" is a real query shape; "every wet room" is not). That
is the best argument any tier here has. It is also entirely theoretical: these
15 have no page to rank, no internal link, and charge **74% of the $19 price for
7-20% of its content**.

**So the call is: retire the SKU, keep the idea.** The kit contents are built
and sitting in `build/products/`; nothing is destroyed. If one of them is worth
selling, it is worth a page first, and the page is what would have to earn the
traffic anyway. Bringing one back after a page ranks costs one catalogue row.

**Evidence tier.** 2 for reachability and price ratios; 8 for the priority call.

**Effort.** 0.5 day, same staged procedure as 1.3. **Acceptance:** as 1.3, plus
a line in `DECISIONS.md` recording the re-entry condition: *a kit returns when a
page for it exists and has produced a measured organic entry.*

**Constraint position.** Independent, with a small at-the-constraint upside: the
three life-event kits with the clearest query shape (`MOVING-IN`, `NEW-BABY`,
`BACK-TO-SCHO`) become article briefs rather than shop tiles, which is work that
belongs to `seo-aeo` and does move arrivals.

**Net of 1.3 and 1.4: 159 SKUs to 138, 155 sellable to 134, roughly 63 fewer
live Stripe objects, $306 of nominal catalogue value that has produced $0
removed, and two tiers a buyer could not find deleted rather than defended.**

### 1.5 Do NOT retire the 109 micro zone packs, and do not make them a button

This reopens D-016, so it needs new evidence to be legitimate, and there is
some: D-016 was argued on 2026-09-03 on merchandising grounds, before anyone
knew that catalogue size had already cost 35% of all checkouts. That is a real
new cost to put on the scale.

It still does not justify deleting them, for one reason: **the $4 pack is the
only paid thing on a zone page, and the 114 zone pages are the only surface
being crawled at volume.** Deleting the offer from the pages that get the crawl,
in the same month we finally started getting crawled, would be trading the one
asset that is working for a tidier table.

What should change is priority, not existence. See 3.1.

**Evidence tier.** 2 for the crawl and the page counts; 8 for the judgement.
**Effort.** 0, this is a decision to leave something alone. **Constraint
position.** Independent.

### 1.6 Conditional: the 8 Kitchen SKUs, when the Kitchen deck ships

`DECK-SYSTEM.md` 9 sets the rule *no new deck ships unless it retires at least
as many SKUs as it adds*, and names the 7 `ZP-KITCHE-*` packs plus `RP-KITCHEN`
as superseded by a 72-card Kitchen deck that covers all seven zones with more
per zone. That rule is correct and this review endorses it. It is **conditional
on the deck actually shipping**, which is blocked on image billing
(`OWNER-ACTIONS.md` 1b), so it is not an action today.

**Acceptance when it fires:** the deck is downloadable on the live site, then
the 8 SKUs are retired by the staged procedure in 1.3.

### 1.7 Two merges, no price change

- **`MZ-MANUAL` $29 against `BK-EB` $9.99.** The companion volume costs three
  times the main volume, and both cover the same twenty rooms. That may well be
  right, but `PRICING.md` 0.3 records that nothing says it was ever argued, and
  **neither tile explains the difference to somebody looking at both.** Fix the
  copy, not the price: one sentence on each tile saying what the other one is
  for. Effort 0.2 day. Tier 2 (the tiles are what they are). Independent.
- **`RP-*` $9 against `BK-EB` $9.99.** Ninety-nine cents apart, wildly different
  scope. `PRICING.md` 0.3 proposes moving the room pack to $7. **Hold.** It is a
  Stripe write on the tier D-016 just made the entry offer, with zero sales to
  reason from, and D-016's own revisit trigger is ten room-pack orders. Record
  it as held, with that trigger, rather than re-arguing it every cycle.

### 1.8 One copy line that overstates the business

`/how-we-make-money.html` says *"Almost all of our revenue comes from products
we made"*. It is literally true of $19, and it implies a revenue stream that
does not exist. `CLAUDE.md` 8 forbids implying scale we do not have. One-line
fix. Tier 1 (read on the live page today). Effort 0.1 day. Independent.

---

## 2. The deck line as a commercial object

### 2.1 A buyer genuinely cannot tell a deck from a pack, and here is the proof

Both sit in the same shop category, `Books & Guides`, with near-identical
subtitles read from `data.js` today:

| SKU | Variant string a buyer sees | Price |
|---|---|---|
| `PACK-HOUSE` | "684 cards, print at home" | $19 |
| `DECK-ENTRY` | "88 cards, fronts and backs, print at home" | $0 |

Nothing on either tile states a difference in kind. A reasonable buyer concludes
the $19 one is the same thing with more cards, which makes the free one look
like a sample and the paid one look like a paywall on the same content. That is
close to the truth for the packs (they are a print of the free Home Quest) and
completely wrong about the deck.

### 2.2 The difference that is worth paying for, stated in one sentence

`DECK-SYSTEM.md` 2 already wrote the sentence and it is right:

> **The pack tells you the steps for a zone. The deck works out which zone, what
> is wrong with it, why, and what to do in the next fifteen minutes.**

with three tests: it diagnoses, it loops (cards route to cards), and it ends in
a written, signed standard left in the room. **The existing Entryway deck passes
none of the three.** The specified Kitchen deck (72 cards, built and validated
at `ops/cardtext/kitchen-deck.json`, verified present today with the right type
distribution) is built to pass all three.

**Commercially, that sentence is the entire deck line.** Until it is printed on
both tiles, the deck line has no product definition, only a card count.

### 2.3 Should any deck ever be paid?

**Not yet, and not as a revenue engine at any price we could honestly charge.**
`DECK-SYSTEM.md` 1.1's arithmetic, checked and correct: a $39 physical deck
carries roughly $18.50 contribution after a print-on-demand range of $9-$18
(a published market range, **not a quote we hold**), card fees and unrecovered
shipping. $20,000 of contribution is then about **1,077 decks a month, roughly
53,800 visitors at a 2% benchmark conversion, about 1,036x today's 52**, worse
than the gross figure, and it comes with pick, pack, stock and returns.

But "not the engine" is not the same as "never paid". The honest position is a
sequence with gates, not a verdict:

1. **Free now**, because the measured zero in the chain is subscribers, not
   products, and a deck is the only artefact in this catalogue somebody will
   trade an address for and then use in front of other people.
2. **A paid deck is considerable only when three things are true:** the free
   deck has produced measurable downloads; a real print quote exists (the
   $11.35 in `PRICING.md` 2 is a search result, not a number anybody has been
   given); and the download-to-email rate has been measured on at least 100
   downloads.
3. **Do not gate the Kitchen deck on an email today.** Listmonk returns HTTP 500
   and every signup surface was deliberately withdrawn because it sends under
   another company's name. A gate in front of a broken list is a download button
   that does not work. `DECK-SYSTEM.md` 7.4.2 says this and it is a hard
   dependency, not a preference.

**Recommendation: record this as a decision so it stops being re-argued**, with
the three gates as the revisit condition. Effort 0.2 day. Tier: 2 for the cost
structure, 8 for the sequence. Constraint position: below the constraint (a deck
converts arrivals), except the decision record itself, which is free.

### 2.4 The free deck currently disagrees with itself in public, live, today

Fetched from 6s-success.com this morning:

| Surface | What it says |
|---|---|
| `index.html` | "**Forty six** cards that take one entryway through all six passes" |
| `shop.html` | "**88 cards**, fronts and backs, print at home" |
| `deck.html` | "The Entryway Deck: **89 cards**, front and back, free to print" |
| `deck-gallery.html` | "72 of the deck's **89** cards are drawn and shown here" |

Three numbers for one product, on the lead magnet, on the live site. And
`ops/build_printpack.py` and `ops/build_standards.py` both still call it 46
(`DECK-SYSTEM.md` 10.3).

**The part that matters more than the numbers.** A gate exists for exactly this
defect, `gate_deck_count` in `ops/preflight.py`, written after the last time it
happened. Reading it today: it returns early when `build/cards-rendered/` is
empty, and empty is what it is in every cloud run, because the renders need
Desktop-only hero photographs. **So the gate that owns this defect has never
been able to fire in the environment it runs in, and the defect it was written
for is live right now.** That is `CLAUDE.md` 0.4 in the flesh: unchecked is not
passing.

**Fix.** Make the gate compare the *claims against each other*, `data.js`,
`deck.html`, `deck-gallery.html`, `index.html`, and the two builders, which
needs no rendered card at all, and keep the render-based count as an extra check
when renders exist. Then correct all four surfaces to the one true number.

**Evidence tier.** 1, read off the live site today. **Effort.** 0.5 day.
**Acceptance:** all six surfaces state one number; `preflight` fails if any two
disagree; the gate is demonstrated to fail on a deliberately wrong number in a
run with no rendered cards. **Constraint position.** Independent: it is a trust
defect on the free artefact and costs nothing to fix at any traffic level.

### 2.5 The free deck is a 25 MB download

Measured live today: `6S-Entryway-Deck-PrintAndPlay.pdf` returns 200 at
**26,192,171 bytes**. On a phone, that is our first impression. The repo copy is
26,194,263 bytes, so production is serving a slightly older build of it as well.

`DECK-SYSTEM.md` 3.2 already fixed 72 cards partly for this reason: nine to a US
Letter sheet is exactly eight sheets of fronts and eight of backs, against the
Entryway deck's twenty. **Give the Kitchen deck a hard size budget as an
acceptance criterion**, and re-export the Entryway PDF at print-adequate rather
than archival resolution.

**Tier.** 1, measured. **Effort.** 0.3 day for the re-export. **Acceptance:** the
free deck PDF is under 8 MB and still prints legibly at true card size on a home
printer, checked on paper, not on screen. **Constraint position.** Below the
constraint, but cheap, and it is the artefact every distribution plan points at.

---

## 3. Services: the funnel into the page, which is where the goal is reachable

`consulting.html` is a genuinely good page. It states both prices in served
HTML, works with no JavaScript, names what is *not* included, tells most readers
to buy the cheaper one, tells some readers to buy nothing, carries a seven-day
refund, and says plainly that no paid reset day has happened yet so there is no
customer quote to show. Nothing below is a criticism of that page.

The problem is everything upstream of it.

### 3.1 On all 163 pages a stranger could land on, the consult has no button

Verified by reading the generated markup for a zone page, a room page and an
article, and confirmed against `ops/build_zone_pages.py`:

- **114 zone pages:** primary button "The Print Pack, 19 dollars", secondary
  "Just this zone, 4 dollars", tertiary "Or draw a card free". The consult is a
  sentence in the final paragraph at `font-size:14.5px;opacity:.85` with a text
  link.
- **20 room pages:** same shape, room pack first.
- **29 articles:** same shape, print pack first.

**The arithmetic.** Contribution per order: $18.15 on the print pack, $242.45 on
the virtual consult (both from `PRICING.md` 0.4, the Stripe fee measured from
the one real transaction; the consult figure is *before* the cost of Phil's
hours, and must never be added to a digital row as though it were the same
thing). The ratio is **13.4 : 1**.

> **The consult produces more contribution than the pack at any conversion rate
> above 7.5% of the pack's rate.** If the pack converts at 1.0%, the consult
> needs 0.075% to match it.

That does not mean swap the buttons. A cold $250 card payment is a far larger
ask than $19, and the pack is a legitimate offer on a page that just gave away
1,300 words about that exact zone. It means the current split, two buttons for
the two lowest-contribution SKUs and a de-emphasised sentence for the one where
the goal is reachable, cannot be right by any reading of the numbers.

**Recommendation.** Give the consult a real, visible, secondary button on all
163 pages, carrying the zone or room in the query string so the page it lands on
knows what the reader was looking at. Do not remove the pack button. Do not make
the consult primary on the zone pages, where the visitor has not yet named a
room.

**Tier.** 2 for the contribution numbers and the markup; 8 for the placement.
**Effort.** 0.5 day (one generator, three templates). **Acceptance:** every zone,
room and article page renders a consult button; the button carries its origin;
`measure.js` records a `service-cta` event with the origin page type so the
click-through can be told apart from the pack's. **Constraint position.** Below
the constraint. It converts arrivals and pays nothing without them, but it is
cheap, correct on its merits, and reversible, which is the right test at 1.7
visitors a day where no experiment can reach significance for 1,427 days.

### 3.2 There is no rung between $19 and $250, and no way to convert without paying

The ladder, ordered: $0, $4, $9, $9.99, $14, $16, $19, $29, $49, **then $250**.
A 13x jump, and on the far side of it a card form.

More to the point: **there is no service conversion event that is not a
payment.** The only pre-purchase path is "Ask a question first" →
`contact.html` → a composed `mailto:`. That is honest and it has a copy-box
fallback (verified in `contact.html`'s own handler), but it asks a stranger to
write a letter to a company they met four minutes ago.

**Recommendation: one free, named, bounded step.** A 15-minute "which zone
first" call. It costs Phil fifteen minutes, needs no new price, no Stripe
object, no recurring anything, and it creates the only pre-payment conversion
event the service line has. Cap it (a stated number per week) and say the cap
out loud rather than manufacturing scarcity, at this traffic the cap will never
bind, and stating it keeps it true when it does.

**Tier.** 8, informed hypothesis. There is no measurement here in either
direction, and I am not going to invent a benchmark. What makes it defensible is
that it is free, reversible, and it measures something we currently cannot see
at all: whether anyone wants to talk to us before paying.
**Effort.** 0.5 day (a section on `consulting.html`, a form that reuses the
existing composed-message pattern, one analytics event).
**Acceptance:** the offer is on `consulting.html` and in the zone/room CTA; it
states its cap; a submission produces a message Phil receives; a
`intro-call-request` event fires; nothing about it implies a booked appointment
that has not been agreed. **Constraint position.** Below the constraint.

### 3.3 A booked consult has no booking

`ops/service_orders.py` forwards a purchase to Phil with a real `.ics` invite,
*"When the customer named no time, no invite is sent and the forward says so,
because inventing an appointment time is worse than asking."* Correct. But the
payment link collects no time, so on the current path the customer **never**
names one, and every $250 purchase becomes a manual email round trip starting
from zero.

**Recommendation.** Capture preferred times immediately after payment, on
`thanks.html`, which already receives `?sku=`. Three questions, the same
composed-message pattern already in use, no new billing surface, no card data,
no new Stripe object. `service_orders.py` then has a time to put in the invite
every time.

**Tier.** 2, read from the code and the live thanks page. **Effort.** 0.5 day.
**Acceptance:** a `CN-VIRTUAL` or `CN-INHOME` completion shows the scheduling
block; a submitted time reaches Phil and `service_orders.py` attaches an `.ics`;
a customer who ignores it still gets the existing email path, unchanged.
**Constraint position.** Below the constraint, and it is the step that turns the
first stranger who ever buys into somebody who is actually served well.

### 3.4 What the services funnel does not need

No urgency copy, no countdown, no "only 3 slots left", no A/B test. The registry
computes 1,427 days to significance at this traffic. Make changes that are
correct on their merits and record why.

---

## 4. Corporate: the offer that needs no consumer traffic

`site/corporate.html` is the strongest commercial page in this repository. It
scopes rather than sells, names nine factors that move the fee, lists what the
client must supply *before* they buy rather than in a kickoff deck, tells the
buyer four situations in which to hire somebody else, and prints the sentence
that ought to be framed: *no figure for space recovered, time saved or defects
avoided appears on this page, because we have not run this engagement for you.*
It carries `Service`, `FAQPage` and `BreadcrumbList` schema with `Offer` objects
that deliberately carry no price, and it is in the sitemap. It returns 200 live,
checked this morning.

**And essentially nobody can reach it.**

### 4.1 The page is orphaned inside its own site

Measured today across all 193 HTML files: `corporate.html` is linked from
exactly **three** pages, `consulting.html`, `shop.html`, and itself. It is not
in the primary navigation. It is not linked from any of the 114 zone pages, any
of the 20 room pages, or any of the 29 articles.

And on the homepage, the one sentence written for this buyer, *"Working
premises rather than a home? Lean 6S for a team is quoted per engagement"*,
links to **`consulting.html`**, not to `corporate.html`. Verified in the live
HTML. An operations manager who reads the right sentence on the right page is
sent to the consumer consulting page and has to find the corporate section
inside it.

**Fix.** Point that link at `corporate.html`. Add a "For work" entry to the
primary nav or the footer's Company column. Add one line to the zone, room and
article footers: *at work rather than at home?*, those 163 pages are where the
crawl is, and a facilities manager reading "why a shared zone never stays reset"
is precisely the buyer.

**Tier.** 1, read on the live site. **Effort.** 0.3 day. **Acceptance:**
`corporate.html` is reachable in one click from the homepage and in two from any
zone page; the count of internal links to it goes from 3 to at least 165;
`quote-click` events distinguish corporate from consumer origin. **Constraint
position.** At the constraint for this offer, corporate needs no consumer
traffic, but it does need the traffic we have to be able to find it.

### 4.2 What would actually produce a first enquiry, with no outbound sending

The arithmetic first, with its uncertainty attached: Lean training contracts of
**$5,000-$15,000** are a market range recorded in `REVENUE-REVIEW-2026-09-04.md`
6, **not a quote we have given or received**. At $10,000, **two closes is the
entire monthly goal.** If one enquiry in five closes, tier 8, we have never run
this funnel and have no rate, that is **ten enquiries a month**. Ten enquiries
is a network and LinkedIn number. It is not an SEO number, and it will not come
from the 114 zone pages.

Four things that can be built without Phil sending anything:

1. **A corporate track for the LinkedIn drafts.** LinkedIn is the only channel
   with measured referrals (17 of 144 visits, `GOALS.md`). Both existing tools
   (`ops/linkedin_posts.py`, `ops/linkedin_drafts.py`) build every post from
   `content.json`'s household micro-zone material; there is no B2B track at all.
   Add one, sourced from `corporate.html`'s own verified content, the nine
   scope factors, the four "when we are the wrong call" cases, the layered audit
, with the same hard rule already in those files: no customer count, no
   results, no testimonials. **Claude drafts. Phil publishes.** No automation,
   no outbound send.
   *Tier 2 for the channel data, 8 for the response. Effort 1.0 day. Acceptance:
   a corporate post set generates, every factual claim traces to a line on
   `corporate.html` or `about.html`, and a gate fails the build if a post
   contains a client claim. At the constraint.*
2. **The one B2B artefact we can honestly give away: the zone scoring sheet and
   the layered audit template.** The engagement's first deliverable is a scored
   6S baseline per zone. That instrument can be published as a blank template
   with the scoring definitions. It requires **no client result**, so nothing
   about it is fabricated, and it is the artefact an EHS or ops manager will
   actually keep. Crucially it does not need Listmonk: the corporate page's
   existing composed-message + copy-box pattern already works for a desktop
   business email client.
   *Tier 8. Effort 1.0 day. Acceptance: the template exists, downloads without
   an email, the enquiry form sits beside it, and a `corporate-asset-download`
   event fires. At the constraint.*
3. **Two B2B-intent articles we can answer truthfully:** *what a 5S engagement
   actually costs and why nobody publishes a number*, and *why 5S decays six
   months after the event*, the second being the exact claim the sixth S is
   built on and the one Phil can answer from twenty years of doing it. Both are
   real queries with real intent. Neither requires a client story.
   *Tier 8 on demand (we have no query data until Search Console,
   `OWNER-ACTIONS` 1a). Effort 1.0 day each. Acceptance: published, internally
   linked from `corporate.html`, in the sitemap and IndexNow. At the constraint.*
4. **An owner decision, not an autonomous action: a stated minimum engagement.**
   D-018 settled that no price is published, and that decision is right, two
   engagements with the same headcount are different weeks of work. But a
   *floor* ("engagements start at $X") is a different instrument from a price:
   it qualifies buyers before they spend Phil's time, and its absence is the
   most common reason a quote-only B2B page produces enquiries that go nowhere.
   **This is Phil's to set. I will not invent a number**, and nothing in this
   repository supports one.
   *Escalate to `OWNER-ACTIONS.md`. Effort: minutes, once decided.*

### 4.3 What corporate must not do

No case study, no logo wall, no "trusted by", no percentage. We have run this
engagement for zero clients under this brand. `corporate.html` currently says so
explicitly and that sentence is worth more than any number we could put in its
place.

---

## 5. Pricing coherence, and where a page and a checkout could still disagree

### 5.1 What agrees today, verified

- **`data.js` ↔ the `Product` schema in `shop.html`: 158 of 158 products match
  exactly** on both price and payment-link URL, checked today by parsing both.
  `CN-CORP` correctly has no schema offer.
- **Production matches the repository** on the six pages I fetched
  (`index`, `shop`, `consulting`, `deck`, `quest`, a zone page): every
  `buy.stripe.com` id served live is the id in `data.js`. The `DECK-ENTRY` tile
  image reported 404 in `DECK-SYSTEM.md` 10.1 is fixed and live at 51,775 bytes,
  byte-identical to the repo copy.
- **No stale `$18` / `$34` / `$44` price appears anywhere under `site/`.**

The catalogue is in better shape than the $18 incident suggests. The remaining
risks are all in the *checking*, not in today's numbers.

### 5.2 R1. The deep price check skips the link that is not the site's, the exact BK-EB shape

`ops/check_sellable.py --deep`, the check whose comment says it exists to
protect a wallet, loops over active links carrying `metadata.sku` and then does:

```python
for l in live.get(sku, []):
    if l["url"] != item.get("buy"):
        continue
```

**The $18 link was not the site's link.** It was a second live link on a second
product, purchasable by anyone holding the URL. This check would have walked
past it. It verifies that the link we advertise is right; it cannot see a link
we do not advertise but Stripe will still honour.

**Fix.** Any ACTIVE payment link carrying `metadata.sku` whose line-item price
is not the catalogue price for that SKU is a violation, **regardless of whether
the site serves its URL**. That is a one-branch change and it closes the exact
hole that cost 35% of all checkouts.

*Tier 2, read from the source. Effort 0.3 day. Acceptance: the check fails
against a deliberately constructed second link at a wrong price; it reports
UNCHECKED, never clean, without a credential. Independent: this is revenue
protection and pays at any traffic.*

### 5.3 R2. The dedupe gate counts products, not links

`gate_stripe_one_product_per_sku` asks whether a SKU has more than one active
*product*. But prices are immutable: `ensure_price` deactivates the old price
and creates a new one, while **an existing payment link goes on charging the old
amount forever, still active, same URL, same metadata** (`link_charges`'s own
docstring says so). `ensure_link` only inspects the link `find_by_sku` returns
first. Two live links on one product is one product, so the gate reports clean.

*Fix: fold this into R1, count and price-check links, not just products. Same
effort, same acceptance. Independent.*

### 5.4 R3. The two consult payment links nothing is watching, UNCHECKED

`ops/payment-links.json` holds:

```
6s_consult_virtual  https://buy.stripe.com/fZu7sE7nEgAO9fQ2FG0kE00
6s_consult_inhome   https://buy.stripe.com/aFafZaazQ5Wacs2cgg0kE01
```

Neither appears anywhere under `site/`. The live site serves `...0kF2a` and
`...0kF2b` for those two SKUs. So there are **two link URLs per consult SKU in
this repository, written by two different scripts, and only one of each pair is
advertised.**

Worse, the products behind the unadvertised pair were created by
`ops/stripe_setup.py`, which tags them `metadata[source]` and `metadata[key]`,
**not `metadata.sku`**. Both the dedupe gate and the `--deep` price check filter
on `metadata.sku`. **So by construction, neither gate can see these objects at
all**, and they sit on the $250 and $1,200 SKUs, the tier where the goal is
reachable.

**Whether those two links are still active in Stripe is UNCHECKED. I did not
call Stripe, as instructed.** I am not going to write "probably fine" over a
thing I did not look at; that is the failure mode `CLAUDE.md` 0.4 exists for.

*Fix, in order: (1) run `python ops/stripe_dedupe.py --check`; (2) list every
ACTIVE payment link and product with no `metadata.sku` and reconcile each one by
hand against the catalogue; (3) either tag the consult objects with
`metadata.sku` so the gates cover them, or archive the orphan links after
verifying against the live site that nothing serves them, in that order, and
never the reverse (`CLAUDE.md` 0.3). Tier: 2 for the repository state, UNCHECKED
for Stripe. Effort 0.5 day. Acceptance: every active payment link in the account
resolves to exactly one catalogue SKU at the catalogue price, or is explicitly
listed as a known non-catalogue object with a reason,* and Ledgerium's objects,
which carry `metadata.ledgerium_plan`, are excluded from every step, per
`CLAUDE.md` 36b. *Independent, and the highest-value item in this report on a
per-hour basis.*

### 5.5 R4. Prose prices are hardcoded in the generator that writes 163 pages

In `ops/build_zone_pages.py`, the pack's own price is read from the catalogue
(`int(pack["price"])`), but the comparison prices are string literals:
`"The Print Pack, 19 dollars"`, `"a one hour virtual consult is 250 dollars"`,
`"All 114 micro zones is 19 dollars for 684"`. Those literals are printed onto
114 zone pages, 20 room pages and the article CTAs.

They are correct today. If `PACK-HOUSE` or `CN-VIRTUAL` is ever repriced, **163
pages will state the old number next to a button that charges the new one**, and
nothing checks it: this is the same defect that produced $18-on-a-$9.99-page,
in a different file and pointed at the two highest-value non-service SKUs.

*Fix: read both from the catalogue, and add a gate that no dollar figure appears
in generated prose unless it matches a catalogue price. Tier 2, read from the
source. Effort 0.5 day. Acceptance: a deliberate price change to `PACK-HOUSE`
regenerates all 163 pages with the new number, and the gate fails if a literal
is reintroduced. Independent.*

### 5.6 R5. The deploy-lag window is designed in, and nobody is told when it opens

`ensure_link` correctly **refuses** to retire a link the live site is still
serving. That is the right behaviour and it exists because the opposite once
took a live buy button down for eight days. Its corollary is that during a
deploy lag, **the live button may charge a retired price while the page states
the current one**, and the only sign is a line printed inside a script's output.

*Fix: when `ensure_link` refuses, that becomes a named RED row on the dashboard
with the SKU, both prices and the age of the lag, not a `print()`. Tier 2.
Effort 0.3 day. Acceptance: a simulated refusal surfaces on the dashboard and in
the brief. Independent.*

### 5.7 R6. `PRICING.md` is mostly superseded text with the correction on top

Section 0 correctly records that the body below it is stale, the $18 eBook, the
$34 hardcover, "34 of the 42 SKUs are marked In development", a deck ladder
describing a 46-card deck. But the stale text is still there and is the longest
part of the file, and it is the document a future operator will read to find out
what a price means.

*Fix: strike the superseded sections explicitly, keep the deck comparables table
(which is real research and still useful), and record `BK-EB`'s $9.99, the one
live price in the catalogue with no recorded reason anywhere, and, not
coincidentally, the SKU that carried the duplicate. Tier 1. Effort 0.3 day.
Acceptance: every live price in `data.js` has a paragraph in `PRICING.md` giving
its reason and its revision trigger. Independent.*

---

## 6. Affiliate: remove it from the revenue plan until an approval exists

`ops/affiliate-accounts.json`, read today: Impact **declined** the 6S Success
partner account (7700618) on 2026-08-29, and Lowe's, Target, Walmart and the
rest all sit behind that one account, so five programmes are shut, not pending.
Amazon is `verification pending` on OTPs that expired. Every retailer link on
the zone pages is a plain search URL carrying no code (verified:
`target.com/s?searchTerm=...`) and earns nothing.

The site says so honestly, `/how-we-make-money.html` states plainly that not a
single link earns us anything, and that honesty is an asset, not a problem.

**The commercial call:** affiliate is not a revenue line and must not appear in
any path to $20,000 until an approval exists. **The one live thread worth
pulling is Amazon Associates**, because it is in-house rather than Impact-routed,
the required disclosure page now exists and is in the footer of all 189 pages
and the sitemap, and the 123-product appendix is the catalogue it would monetise.
Re-application needs Phil (account and OTP); everything up to it is built.
*`OWNER-ACTIONS.md` 4 already carries this; not duplicated here.*

---

## 7. The backlog, ranked

Effort in days. **Position** is against the traffic constraint from `GOALS.md`:
*At* = plausibly increases arrivals. *Below* = converts arrivals, pays little
until O1 moves. *Independent* = protects revenue that is already possible, pays
at any traffic including 1.7 visitors a day.

| # | Item | Why | Tier | Effort | Acceptance | Position |
|---|---|---|---|---|---|---|
| C1 | Reconcile every active Stripe link/product with no `metadata.sku`, including the two orphan consult links in `ops/payment-links.json` | The two gates written after the $18 incident filter on `metadata.sku`; `stripe_setup.py` tags `metadata[key]`. The $250 and $1,200 SKUs are outside both by construction. Stripe state UNCHECKED | 2 repo / UNCHECKED Stripe | 0.5 | every active link resolves to one SKU at the catalogue price or is listed as a known exception; Ledgerium objects excluded | Independent |
| C2 | Price-check every active `metadata.sku` link, not only the advertised one (`check_sellable --deep`) | The $18 link was not the advertised link; the check walks past it | 2 | 0.3 | fails against a constructed wrong-price second link; reports UNCHECKED without a credential | Independent |
| C3 | Fix the free deck's card count on all six surfaces, and make `gate_deck_count` able to fire without rendered cards | 46 / 88 / 89 live today on the lead magnet; the gate for it returns early in every cloud run | 1 | 0.5 | one number everywhere; gate fails on a deliberately wrong number with no renders present | Independent |
| C4 | Point the homepage's corporate sentence at `corporate.html`; add it to nav and to the 163 page footers | The best commercial page in the repo is linked from 3 pages, and its own homepage sentence links elsewhere | 1 | 0.3 | one click from home, two from any zone page; internal links 3 → 165+ | At |
| C5 | Read `19 dollars` / `250 dollars` from the catalogue in `build_zone_pages.py`; gate prose prices | 163 pages carry hardcoded literals for the two highest-value non-service SKUs | 2 | 0.5 | a test reprice regenerates all 163; gate fails on a reintroduced literal | Independent |
| C6 | Retire the 6 Area Bundles, staged against production | 84% of a $19 superset's price for 12-20% of its content, on one page nobody reaches | 2 struct / 8 judgement | 0.5 | delisted → deployed → live-verified → archived; reasons in `retired-skus.json` | Independent |
| C7 | Retire the 15 Situation Kits, with a written re-entry condition | Same, at 74%; reachable only from `shop.html` | 2 struct / 8 judgement | 0.5 | as C6, plus the re-entry rule in `DECISIONS.md` | Independent |
| C8 | Give the consult a real button on all 163 organic-entry pages, with origin tracking | 13.4:1 contribution ratio; the consult needs 7.5% of the pack's conversion rate to beat it, and currently has no button at all | 2 arith / 8 placement | 0.5 | button renders, carries origin, `service-cta` event fires | Below |
| C9 | Capture preferred times on `thanks.html` after a service purchase | `service_orders.py` can only send an invite if a time was named; nothing ever collects one | 2 | 0.5 | a completion shows the block, a submitted time reaches Phil and produces an `.ics` | Below |
| C10 | Add a free, capped, 15-minute "which zone first" call | No rung between $19 and $250, and no service conversion event that is not a payment | 8 | 0.5 | offered, cap stated, submission reaches Phil, event fires, nothing implies a booked appointment | Below |
| C11 | Corporate LinkedIn post track, drafted from `corporate.html` only | LinkedIn is the only channel with measured referrals; both tools are consumer-only. Claude drafts, Phil publishes | 2 channel / 8 response | 1.0 | posts generate; every claim traces to a live page; a gate fails any client claim | At |
| C12 | Publish the 6S zone scoring sheet and layered audit template as a free B2B artefact | The only honest lead magnet for a buyer with budget; needs no client result and no working list | 8 | 1.0 | downloadable without an email, enquiry form beside it, event fires | At |
| C13 | Two B2B-intent articles: what a 5S engagement costs and why nobody publishes a number; why 5S decays after six months | Real queries Phil can answer truthfully; corporate needs no consumer traffic but does need a door | 8 | 2.0 | published, linked from `corporate.html`, in sitemap and IndexNow | At |
| C14 | Distinguish deck from pack in one sentence on both tiles; same for manual vs book | A buyer cannot tell them apart today, and one of the pair is our main lead magnet | 2 | 0.2 | the sentence from `DECK-SYSTEM.md` 2 appears on both tiles, read from the catalogue | Independent |
| C15 | Record the paid-deck decision and its three gates in `DECISIONS.md` | Stops the question being re-argued every cycle; the gates are downloads, a real print quote, a measured email rate | 2 cost / 8 sequence | 0.2 | decision recorded with revisit conditions | Independent |
| C16 | Re-export the free deck PDF under 8 MB; set a size budget for the Kitchen deck | 25 MB is the first impression, on a phone | 1 | 0.3 | under 8 MB, still prints legibly at true card size on paper | Below |
| C17 | Dashboard RED row when `ensure_link` refuses to retire a link production serves | A designed-in price-disagreement window whose only signal is a `print()` | 2 | 0.3 | a simulated refusal surfaces on the dashboard and in the brief | Independent |
| C18 | Strike the superseded body of `PRICING.md`; record a reason for `BK-EB` $9.99 | The one live price with no recorded reason is the one that carried the duplicate | 1 | 0.3 | every live price has a reason and a revision trigger | Independent |
| C19 | Fix "Almost all of our revenue comes from products we made" | Implies a revenue stream; `CLAUDE.md` 8 | 1 | 0.1 | the sentence is true of one $19 sale | Independent |
| C20 | Conditional, on the Kitchen deck shipping: retire the 7 `ZP-KITCHE-*` and `RP-KITCHEN` | `DECK-SYSTEM.md` 9: a deck must retire at least as many SKUs as it adds | 2 | 0.5 | fires only after the deck is live; staged as C6 | Independent |

**Suggested order, respecting the three-workstream limit in `CLAUDE.md` 18:**
C1-C3 first (they are revenue protection and they pay at any traffic), then
C4/C11/C12 as the one workstream that is actually at the constraint, then the
catalogue retirements C6-C7 as background hygiene. Everything marked *Below*
waits behind O1, with the exception of C8, which is half a day and correct on
its merits.

---

## 8. What I recommend against

- **Do not add a product.** Not one. The 160th SKU cannot help and each one
  dilutes the path to the few that matter (`REVENUE-REVIEW-2026-09-04.md` 5,
  still right).
- **Do not create a paid deck SKU.** Section 2.3.
- **Do not gate any download on an email until Listmonk sends under our own
  name.** A gate in front of a broken list is a button that does not work.
- **Do not retire the 109 zone packs.** They are the only paid offer on the only
  pages being crawled. Section 1.5.
- **Do not reprice anything.** No live price has a sale behind it to reason
  from. Every repricing proposal in this report is recorded as held, with its
  trigger.
- **Do not A/B test.** 1,427 days to significance.
- **Do not chase "under 100 SKUs" as a number.** It was the threshold of a
  pagination bug that is now fixed. The mitigation is the link-level check in
  C1/C2, not a catalogue cull performed for superstition.

---

## 9. Honest limits of this review

- **No per-SKU demand evidence exists.** Nine buy-clicks ever, seven
  unattributable. Every retirement call here rests on reachability, price
  ratios and operational cost, never on "nobody wanted it".
- **Stripe was not called.** Three findings (5.4 especially) end in UNCHECKED.
  They are hypotheses about the account derived from the repository, and they
  must be confirmed before anything is archived.
- **The 2% conversion rate used throughout is an industry benchmark, not our
  measurement.** We have one sale, which supports no conversion estimate at all.
- **The $5,000-$15,000 corporate range and the print-on-demand $9-$18 are
  published market ranges, not quotes we hold.** The 1-in-5 close rate in 4.2 is
  a tier 8 hypothesis with no evidence behind it whatsoever.
- **Contribution is the deepest honest line.** `COST-GOVERNANCE.md` records
  infrastructure cost as UNKNOWN and no cost is recorded for Phil's time, which
  is the main input to every service in section 3. The $242.45 and $1,164.90
  service rows are *before* the cost of delivering them and must never be added
  to a digital row as if they meant the same thing. None of it is profit.
- **Etsy and Amazon comparables could not be verified.** Etsy blocks automated
  access. There is no volume estimate anywhere in this document.
- **Nothing here rests on customer research, reviews or testimonials, because
  none exists.** One customer, ever, and he was a personal referral.
