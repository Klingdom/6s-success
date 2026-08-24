# Pricing

Owner: whoever is setting prices. Purpose: say what every price is, why it is
that number, and what evidence would change it. A price with no recorded reason
gets re-argued every quarter by whoever feels strongest that day.

Last set: 2026-08-20. Covers the card decks. The rest of the catalogue is
recorded here as observed, not as decided, and is flagged at the end.

---

## 1. The state of the evidence, stated first

There have been **zero sales and zero recorded visits**. Analytics collect
nothing because a proxy path is missing, so there is no conversion data, no
traffic data, and no price test behind anything below.

Everything here is therefore a **starting price set from comparables and cost
structure**, which is the weakest usable tier of the evidence hierarchy in
CLAUDE.md section 15. It is not a validated price. Treat the numbers as an
opening position that exists so the business can start learning, not as an
answer.

The single most valuable thing that could improve this document is one hundred
real transactions.

---

## 2. Card decks

### The ladder

| Tier | Product | Price | State |
|---|---|---|---|
| 1 | Entryway Deck, print at home, 46 cards, line art | **Free** | Live |
| 2 | Entryway Deck, illustrated print and play PDF | **$12** | Needs 46 images |
| 3 | Entryway Deck, printed and boxed | **$29** plus shipping | Needs a printer |
| 4 | Both editions, PDF and printed | **$34** | Needs both above |

Each further room deck, when one exists, takes the same prices. A room deck is
a room deck; charging differently for the Kitchen than the Entryway would need
a reason, and there is not one.

### Why tier 1 is free

Not a discount and not a funnel trick. The binding constraint on this business
is that **nobody arrives**, not that nothing is for sale. A complete, genuinely
useful thing given away is a real answer to that. A preorder for something that
does not exist is not.

It also buys the one thing no amount of reasoning can produce: evidence about
whether the card format works in a real house. That evidence is worth more
right now than the revenue a $9 paywall would earn on a site with no traffic.

### Why tier 2 is $12

Comparable **physical** prompt and method decks, retail, checked 2026-08-20:

| Deck | Cards | Price |
|---|---|---|
| Side Quest Deck (chores) | not stated | $19.45 |
| School of Life, Know Yourself | 60 | $24.50 |
| TableTopics Family | 135 | $24.99 |
| School of Life, across the line | varies | $20 to $36 |
| School of Life, Therapy Cards | varies | $36 |
| IDEO Method Cards | 51 | $49.00 |

So the premium physical market for this kind of deck clusters **$20 to $36**,
with a professional tier around $49. Our 46 card instructional deck sits
naturally inside that cluster, not above it: IDEO prices at $49 on thirty years
of name, which we do not have.

I could not verify digital printable comparables. Etsy blocks automated
fetching and the searches returned category pages without prices, so **there is
no digital comparable behind this number and I am not going to invent one.**

Instead tier 2 is anchored on the two things that are real:

1. **This business's own digital to print ratio.** The ebook is $18 against a
   $34 hardcover, which is 0.529. Applied to a $29 physical deck that gives
   $15.
2. **The free tier directly below it.** Unlike the book, tier 2 competes with a
   free version of the same 46 cards. The only thing the buyer gains is the
   illustration. That is a real difference for a deck aimed at children, but it
   is one difference rather than a fuller product, so it should not carry the
   full 0.529 ratio.

$12 is 41% of the physical, below every physical comparable found, and low
enough that the first hundred buyers are a signal rather than a negotiation.

**The honest uncertainty:** $12 could be wrong by a factor of two in either
direction and nothing currently in place would detect it. See the revision
triggers.

### Why tier 3 is $29 plus shipping

Positioned in the middle of the verified $20 to $36 cluster. Below TableTopics
and School of Life, which are established brands, and well below IDEO.

Unit economics, per deck, at low volume:

| Line | Amount | Confidence |
|---|---|---|
| Print, 54 card deck with custom tuck box | about $11.35 | **Unverified.** Reported for MakePlayingCards in a January 2026 comparison. No quote has been requested. |
| Stripe, 2.9% plus $0.30 on $29 | $1.14 | Verified, standard published rate |
| Contribution before shipping | **about $16.51**, 57% | Only as good as the print line above |

**Shipping is charged at checkout, not absorbed.** Free shipping on a $29 item
costs roughly $6 domestic, which takes contribution from 57% to about 36%. That
is a fine trade at volume, funded by the volume. At zero volume it is just a
smaller margin. Revisit when there is a second physical product to build a free
shipping threshold around.

**Before anything is printed, get a real quote.** The $11.35 is a search
result, not a number anybody has been given. If the true landed cost is $15 the
whole tier needs repricing, and finding that out after a print run is the
expensive way to learn it.

### Why tier 4 is $34

$12 plus $29 is $41, so the bundle saves $7, which is 17%. The book bundle
saves $8 on $52, which is 15%. Same shape, so the catalogue reads as one
business rather than as a set of separate decisions.

### What is deliberately not priced

**Rooms 2 through 20.** Nineteen more decks could be priced today and none of
them exist. Pricing a product line before its pilot has sold a single unit is
forecasting, not pricing.

---

## 3. Revision triggers

Change these numbers when one of these happens, and not on a feeling or because
a quarter ended.

| Trigger | What it means | What to do |
|---|---|---|
| A real print quote arrives | The $11.35 was the softest number here | Reprice tier 3 to hold contribution at or above 50% |
| 100 free downloads, under 2% go on to buy tier 2 | $12 is above what this audience pays for illustration alone | Test $9, or fold the illustrated PDF into the book bundle instead |
| 100 free downloads, over 10% buy tier 2 | $12 is under-priced | Test $15, then $19 |
| Tier 3 notify-me list passes 50 | Enough demand to justify engaging a printer | Get three quotes, then set the real price |
| Analytics start recording | The first real evidence this business has had | Re-read this whole document against it |

Until analytics work, none of the above can be observed. **Fixing the /stats
proxy path is a pricing task**, not only an engineering one.

---

## 4. The rest of the catalogue, observed not decided

Recorded because it affects how the deck prices read, and because it is a
larger problem than the decks.

**34 of the 42 SKUs are marked In development.** Every course, every reset kit,
the app, and all 24 tools. They correctly say so and offer a notify-me link
rather than a buy button, which is the honest handling.

**Only the three consulting offers can take money**, and two of those carry a
working Stripe link.

**The four Books and Guides SKUs show Add to cart.** No money moves, because
checkout is staged for v2, but the book is blocked on the front matter in issue
number 3 and there is no fulfilment behind any of the four. Their prices, $34
hardcover, $18 ebook, $44 bundle, $29 manual, were set before this document and
are not re-argued here.

**None of those prices were set against comparables** as far as any record
shows. They are internally coherent, which is not the same as correct. That is
worth a pass of its own once something has actually sold.

---

# The catalogue as it stands, 2026-08-21

Six products take money, and every listing in the shop leads somewhere real.

| Product | Price | Delivery |
|---|---|---|
| 6S Success: Home Edition, EPUB | **$18** | emailed within the hour |
| The Whole House Print Pack, 684 cards | **$19** | emailed within the hour |
| The Micro Zone Manual | **$29** | emailed within the hour |
| The Complete Digital Bundle, all three | **$49** | emailed within the hour |
| Virtual Home Consult, one hour | **$250** | scheduled by email |
| In-Home Reset Day | **$1,200** | scheduled by email |

Free and finished: the Entryway Deck and the Home Quest. Quoted: Corporate
Lean 6S, which is the correct flow for a custom engagement rather than a
checkout.

## Why the bundle is $49

The three digital products are $66 bought separately, so the bundle saves $17,
which is 26%. That is steeper than the 15 to 17% used elsewhere here, and
deliberately so: a three item bundle has to be obviously worth taking over one
item, and the marginal cost of the second and third file is zero.

## Why the print pack is $19

684 cards over 76 sheets, against the free Entryway deck's 46 cards for one
room. Priced just above the book because it is a different job rather than more
of the same: the book is read once and the pack is carried into the room. It
sits below the manual, which remains the deeper reference.

## What was retired, and why that is a pricing decision

36 SKUs came out of the shop on 2026-08-21 because none of them could be
delivered if somebody paid: four courses with no platform, four kits with no
supplier, a paid app tier that does not exist, a hardcover and a boxed deck with
no printer, an illustrated deck with no illustrations, and 24 third party retail
supplies we never stocked.

Their prices are preserved in `ops/retired-skus.json` with the reason for each,
so nothing has to be re-derived when any of them becomes real. **None of those
prices should be trusted on return.** They were set before this document
existed and against no comparables at all.

The tools in particular should probably never come back as products. They are
the reference list of what the method calls for, they are named as types rather
than brands on purpose, and resources.html now says plainly that we earn nothing
from where you buy them. That is worth more than the margin.

---

# The Standards Pack: priced at zero, and why that was a reversal

Scoped 2026-08-22 as a $12 product on the recommendation that leave_behind
carried content sold nowhere else. Built, measured, and repriced to free before
it ever reached the shop.

## What the measurement said

The claim was that `leave_behind.standard` and `leave_behind.trigger` were
distinct from the `standardize` and `sustain` passes already sold inside the $19
Whole House Print Pack. Against a shared-vocabulary overlap test:

| Comparison | Median overlap | Above 0.6 |
|---|---|---|
| `standard` vs `passes.standardize` | 0.27 | 6 of 114 |
| `trigger` vs `passes.sustain` | 0.58 | **49 of 114** |

Forty nine of the triggers are near verbatim restatements. Two are identical in
every content word. The pack is a condensation of something a Print Pack buyer
has already paid for.

## Why that means free rather than cheaper

A smaller price on the same content is still a second charge for one purchase.
The compression is genuinely useful, and useful does not make it a separate
sale. Discounting would have been the version of this that looks like a
concession while keeping the problem.

## Why free is also the better commercial call

The binding constraint remains that nobody arrives. This is the strongest free
artifact the business has: 114 standards across all twenty rooms against the
Entryway deck's 46 cards in one. It shows whole house scope, which is exactly
what the $19 pack is the deep version of, and it costs nothing to reproduce.

## Revision trigger

If the free pack is downloaded 200 times and the Print Pack conversion from
`standards.html` stays under 1%, the page is failing as a route to the paid
product and the offer block at the bottom is what to change, not the price.

**Do not reprice this to anything above zero without new content.** The overlap
numbers above are the reason, and they are re-measured on every build by
`ops/build_standards.py`, which prints the median at build time.
