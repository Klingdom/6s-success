# Retail affiliate merchandising strategy

**Owner:** commerce-manager · **Created:** 2026-08-28 · **Status:** proposal, nothing shipped
**Inputs read:** `ops/affiliate-catalogue.csv` (123 products), `ops/affiliate.py`, `ops/affiliate-accounts.json`,
`ops/build_zone_pages.py`, `ops/zone-search-terms.json` (53 terms), `content/manual/source/zone_products.json`
(114 zones), all 114 `site/zones/*.html`, `6S_AFFILIATE_PROGRAM_PLAN.md`.

---

## 0. Three corrections to the brief, before anything else

These change the decisions below, so they come first.

**0.1 The zone pages are 1,200 to 1,600 words, not 1,900 to 2,500.** Measured across all 114 pages:
median 1,313 words, longest 1,585 (`kitchen-the-cooking-zone`), shortest 1,198
(`living-room-the-coffee-table`). Nothing here depends on the pages being longer than they are, but a
merchandising plan built on a wrong length assumption would over-estimate how much room there is to
insert a product block without unbalancing the page. There is room for one block, not a catalogue.

**0.2 The zone pages are already monetised, and better than affiliate can monetise them.**
`ops/build_zone_pages.py:174 offer()` puts a **$19 Whole House Print Pack** (live Stripe link,
digital, effectively 97% margin after fees) and a **$250 virtual consult** on all 114 zone pages. This
is the single most important commercial fact in the brief and it was not in the brief.

An affiliate link on a zone page does not add revenue to an empty page. It competes for the same
click on a page that already has a better offer:

| Offer on a zone page | Gross per conversion | Margin | Net to 6S |
|---|---|---|---|
| Print Pack | $19.00 | ~97% | **~$17.90** |
| Virtual consult | $250.00 | high | **~$200+** |
| Affiliate, $45 basket at 3.5% | $1.58 | n/a | **$1.58** |

One Print Pack sale is worth about **eleven** affiliate conversions, and affiliate conversions are
much harder to get because they require the reader to leave the site, land on a retailer, and buy.
Any placement that moves a click from the Print Pack to a retailer **loses money**. That is the whole
argument for the surface decision in section 1.

**0.3 `content/manual/source/zone_products.json` is a room-level join, not a zone-level one.**
It maps a hose reel to `Patio or Deck|Outdoor Dining Zone` and a matching hanger set to
`Guest Bathroom|Guest Linen Zone`. Both are wrong for the zone and right for the room. This file is
usable as a room-level shortlist and is **not** safe to render directly as per-zone recommendations.
Doing so would put a hose reel under a dining table with the words "recommended because" above it,
which is precisely the thing section 4 forbids. A per-zone pass is a prerequisite to any zone-level
link, and it is one of the reasons the first release is not on zone pages.

---

## 1. Which surface first

### Decision: one new page, `site/kit.html`, canonical `https://6s-success.com/kit`

Working title: **"The eight things every reset needs."** The Universal Kit, the eight products from
Tier 1, in 6S phase order. Nothing else ships in release one. No zone page, no room page, no
catalogue page.

### Why one page and not the 114

**It does not cannibalise the $19 pack.** Per 0.2, that is a losing trade on every one of the 114
pages. A separate page is reached by a reader who has already decided they want equipment, which is a
different intent from the reader reading the method. The zone page keeps its highest-value offer and
sends the equipment-minded reader sideways with a text link, not a button.

**Amazon's clock only closes on a concentrated page.** Three qualifying sales in 180 days is the
binding constraint on the biggest programme. At 3 to 4 visitors a day, spreading eight products over
114 pages guarantees no page accumulates enough visits to convert anything. One page concentrates
every equipment-intent visit onto the four Amazon items. It does not make the clock likely (section
6 says it is not), but it is the only configuration where it is not hopeless.

**It is the only page where a recommendation is legitimate without a personal diagnosis.** This
matters more than the traffic argument. CLAUDE.md §6 forbids prescribing a product before diagnosing
a root cause. The Universal Eight are the one set that escapes it, because the diagnosis was done at
the **method** level rather than the household level: `_zone_count` in the catalogue shows these eight
are called for by 109 to 114 of 114 micro zones. A vacuum is not a solution to your particular
problem; it is a tool the Shine pass requires in every room in the book. That is an honest,
auditable reason to list them without knowing anything about the reader. **No other product in the
123 has that property.** Everything in Tier 2 and Tier 3 needs a specific zone, and therefore a
specific diagnosis, before it can be named.

**One compliance surface.** One disclosure block, one FTC exposure, one link-rot audit, eight rows in
the CSV to keep alive instead of 123. `python ops/affiliate.py --check` polices one file.

**It is the surface the plan already established the book needs.** The existing plan's central finding
is that Amazon prohibits links in ebooks and PDFs, so the book must point at a page. This is that
page, and it is the one URL every chapter can point at, because every chapter needs the same eight
things.

### Where it is linked from

- `site/resources.html` — one nav entry.
- All 114 zone pages — **one plain text link inside the Shine section**, not a button, not a band,
  placed below the existing Print Pack band so it never outranks it. Wording: "The eight tools every
  zone in this book asks for are listed here." Generated by `ops/build_zone_pages.py`, never hand-edited.
- The book's per-chapter resource URL, non-affiliate, as the existing plan specifies.

### What ships in release one

`site/kit.html` · the reusable disclosure component from `affiliate.py DISCLOSURE_HTML` · eight CSV
rows populated · the `--check` gate extended per section 5. That is the whole release.

---

## 2. Merchant mapping, the Universal Eight

Commission percentages are **planning ranges from general knowledge and are not verified**. The
existing plan's compliance rule stands: read each operating agreement before a link ships, and put
the real rate in the `Commission %` column. Assignments are argued on fit, basket and conversion,
which do not move when a rate moves by a point.

| # | Product | Ticket | First choice | Why | Fallback |
|---|---|---|---|---|---|
| MPL-00008 | Compact vacuum with attachments | $80–250 | **Amazon** | A third of the kit basket on its own. Assortment and review density are decisive on a considered $150 purchase, and Amazon's 24-hour cookie is not a handicap here because a vacuum shopper buys in the same session. The item most likely to produce a qualifying sale. | Target |
| MPL-00010 | Sort container set, 5 units | $15–50 | **Home Depot** | Five bulky, cheap totes. Shipping economics are terrible online and excellent in store; the HDX tote is the default cheap tote and buy-online-pickup-in-store fits bulky-cheap exactly. Sending this to a parcel carrier converts badly and refunds badly. | Walmart |
| MPL-00012 | Portable label maker | $25–60 | **Office Depot** | Paired deliberately with MPL-00013 below. Category-native retailer, and the tape refill is a genuine repeat purchase Office Depot handles better than a marketplace. | Amazon |
| MPL-00013 | Removable write-on labels | $6–18 | **Office Depot** | A $6–18 pack cannot carry its own shipping anywhere, and alone it earns about twenty cents. **Merchandised as one basket with the label maker**, it clears the free-shipping threshold and earns on both lines. The only place in the eight where basket consolidation beats picking the best single merchant per item. | Amazon |
| MPL-00009 | Portable cleaning caddy | $10–35 | **Amazon** | Light, cheap, ships free on Prime, near-zero return risk, no sizing decision. One of the two fastest routes to a qualifying sale. | Walmart |
| MPL-00006 | Colour-coded microfiber cloths, 12 | $15–40 | **Amazon** | Same logic as the caddy and better: universally needed, high review density, impulse-priced, ships in an envelope. The other fast qualifying sale. | Walmart |
| MPL-00098 | Humidity monitor / moisture absorber | $10–35 | **Amazon** | Read as the **monitor** (a digital hygrometer), which is small electronics where Amazon's assortment and price dominate. If read as the **absorber**, it is a hardware-aisle consumable and belongs at Home Depot instead — the catalogue row conflates two different products and should be split. | Home Depot |
| MPL-00001 | Neutral pH multi-surface cleaner | $6–15 | **Walmart** | Heavy liquid, grocery-rate commission of roughly a penny per dollar, and people buy it on a grocery run. Walmart is where the behaviour already is. **Recommendation: link it last or not at all** — see 4.6. It is the plan's own white-label candidate. | Target |

**Resulting spread:** Amazon 4, Office Depot 2, Home Depot 1, Walmart 1.

**Deliberately unused in release one: Lowe's, Target, The Container Store, Wayfair, Ace, Etsy.**
That is not an oversight. None of them is the right home for a universal cleaning-and-labelling kit,
and signing a programme you have nowhere to place is how you accumulate dead accounts and dead links.
They earn their place in Tier 3, where the money actually is:

- **The Container Store** — closet and drawer systems, airtight food container sets. Highest rate of
  the ten and the only one whose catalogue *is* this method.
- **Wayfair** — deck boxes, shoe racks, hamper sorters, furniture-scale storage.
- **Ace / Lowe's** — garage and workshop durables, hooks, rails, pegboard.
- **Etsy** — labels and visual controls, where a made-to-order label set beats a mass-market one.
- **Target** — nursery and kids storage, where the assortment and the audience match.

Apply to all ten if the applications are free, but **place** only the four above until there is
traffic to justify maintaining more links.

---

## 3. Rollout order: the first ten zone pages

**Release two, and only after the kit page has run for 90 days.** The gating criteria, applied to the
actual `Straighten` text of all 114 pages rather than to the room-level product map:

1. The Straighten step **names an unambiguous product type**, so the recommendation restates the page
   rather than adding to it.
2. The product is **generic-sized** — no measuring, no fit risk. A wrong-size return costs the trust
   the page exists to earn.
3. The zone has an **assigned search term that is a purchase query**, not a method query.
4. Mid-ticket, $20–90, so the commission is not rounding error.
5. Not safety-critical, not medical, not a consumable (section 4).

| # | Zone page | Search term | What the page already names | Product |
|---|---|---|---|---|
| 1 | `laundry-room-the-hanging-and-air-dry-zone` | drying rack | "The rack gets one spot with a drip tray underneath" | Drying rack + drip tray |
| 2 | `family-room-the-charging-and-device-zone` | charging station | "One strip, one slot per device, the owner's name on the slot" | Charging dock, surge protector, cord labels |
| 3 | `mudroom-the-shoe-and-boot-storage` | *(none assigned — gap)* | "One row per person… caked walking boots live on the tray only" | Shoe rack + boot tray |
| 4 | `family-room-the-toy-and-play-zone` | toy storage | "One category per open bin, **no lids**, all on the lowest shelf" | Open-front bins |
| 5 | `laundry-room-the-sorting-and-hamper-zone` | sorting hampers | "One bag per stream" | Hamper sorter |
| 6 | `nursery-the-books-and-quiet-play-zone` | book storage | "Covers face out along the ledge… fill the basket to its rim" | Front-facing book bin + basket |
| 7 | `garage-the-sports-and-recreation-zone` | sports gear storage | "Balls go in a tall bin or a bungee-front rack"; "bikes hang on wall hooks" | Ball bin + bike wall rack |
| 8 | `kids-bedroom-the-school-and-activity-launch-zone` | backpack station | "Hook, then shoes, then bag, in the order they get grabbed" | Wall hook rail |
| 9 | `pantry-the-snack-and-lunch-zone` | snack station | "an open bin the child can reach without a stool" | Open bin + airtight set |
| 10 | `patio-or-deck-the-outdoor-storage-zone` | outdoor storage | "flat-bottomed totes underneath"; cushions load last | Deck box ($80–250, top ticket here) |

Numbers 4 and 6 are the strongest of the ten, because the page does not merely name a product, it
names a **specification** — no lid, covers facing out — which is a recommendation a reader can verify
and a retailer can be filtered against. That is what recommendation integrity looks like in practice.

### Excluded on the evidence, with the reason

- **`primary-bathroom-the-under-sink-cabinet`** — high query volume, and rejected anyway. The page
  says "build the bins around the P-trap." The correct bin depends on a measurement nobody has taken.
  Linking a generic bin here produces returns and a reader who trusts the next recommendation less.
- **`home-office-the-file-storage`** — the Straighten step is about naming files by the question you
  will ask, not about buying anything. There is no product in it. Adding one would be invention.
- **The closet zones** (guest closet, primary closet, kids clothing closet) — these carry the largest
  baskets in the catalogue at $776 to $3,890 and are therefore the most tempting. They are all
  measurement-dependent systems with the worst return profile of anything on the list. **Highest
  revenue, first to be excluded.** Revisit only with a measurement step ahead of the link.
- **`workshop-the-safety-and-ppe-station`, `garage-the-power-tool-and-battery-zone`,
  `workshop-the-finishing-and-chemical-zone`** — large baskets, and all three are dominated by safety
  equipment. See 4.2.
- **`nursery-the-crib-and-sleep-zone`** — see 4.4.

### One gap to fix in `ops/zone-search-terms.json`

Only 53 of 114 zones carry a search term. Two of the highest-intent commercial zones in the whole
site have none: **`mudroom-the-shoe-and-boot-storage`** and
**`primary-bathroom-the-under-sink-cabinet`**. "Shoe storage" and "under sink organizer" are among the
highest-volume queries in the entire home-organization category. That is an SEO gap, not a commerce
gap — hand to `seo-aeo` — but it is the reason number 3 above appears on content merit alone.

---

## 4. What must not be monetised

Explicit, because each of these would earn and each is still wrong.

**4.1 Anything above the Straighten anchor, on any page, ever.** The Sort step is where the reader
decides what stays. A container offered there is a container bought to hold things not yet decided
on, which is the exact failure CLAUDE.md §6 exists to prevent and the exact reason the method puts
Sort first. Every one of the 114 pages carries `<section id="sort">` and `<section id="straighten">`,
so this is mechanically enforceable rather than a matter of discipline. See section 5.

**4.2 Safety-critical equipment.** Fire extinguisher (MPL-00116), first aid kit (MPL-00117),
self-closing oily rag can (MPL-00115), flammable safety cabinet (MPL-00081), safety glasses
(MPL-00016), step ladder (MPL-00111), household step stool (MPL-00017, 31 zones), child cabinet
latches (MPL-00095), and **furniture anti-tip anchors (MPL-00018, referenced by 34 zones)**.

A commission on a device whose failure injures a child places a financial interest against the reader
at the exact moment the reader is most trusting. The catalogue's own compliance rule already says do
not repeat the safety notes next to a buy link; the cleaner answer is not to put a buy link there at
all. **Recommend the type, describe the standard, link nothing.** The anti-tip anchor touches 34 zones
and this costs real money. Do it anyway.

**4.3 Medicine and prescriptions.** Lockable medicine box (MPL-00069, 15 zones), medicine bin set.
Same reasoning, plus the pages sit next to content about children and prescriptions.

**4.4 The nursery crib and sleep zone.** Infant sleep products carry recall and safety-standard
exposure that a three-person operation cannot monitor. No affiliate link in that zone at all,
including the non-crib items on the page.

**4.5 The hazard block.** Every zone page has a "Check these before you start" section listing water,
fire and fall risks. It is safety guidance. A product link inside it converts guidance into a claim
about a specific manufacturer's item and creates liability the catalogue notes were written to avoid.

**4.6 Consumables under about $20.** Multi-surface cleaner, glass cleaner, degreaser, absorbers. Not
an ethics problem, an economics one: 1–3% of $8 is under twenty cents, against a link that has to be
re-verified every 90 days forever. The maintenance cost exceeds the revenue. The existing plan already
routes these to white label, correctly, and that decision stands.

**4.7 Anything measurement-dependent, until the measurement step exists.** Closet systems, wall track
systems, pegboard, under-sink slide-outs, drawer dividers. The reader eats the return.

**4.8 The quest flow and the consulting page.** A reader mid-quest is executing the method; a reader
on `consulting.html` is evaluating a $250 purchase. Diverting either for $1.58 is bad arithmetic as
well as bad manners.

**4.9 Any downloadable file.** Contractual, not discretionary. Already enforced by
`ops/affiliate.py check()`.

**4.10 The Print Pack band on any of the 134 zone and room pages.** Per 0.2, every click moved from
the pack to a retailer costs about $16.

---

## 5. The sequencing rule, in interface terms

Sort before Straighten is a method claim. Here is how the page is built so it cannot be violated.

### 5.1 A build-time gate, not a convention

All 114 zone pages have `id="sort"` and `id="straighten"`. Add a fourth rule to
`ops/affiliate.py check()`:

> For every HTML file under `site/`, find the byte offset of `id="straighten"`. If any `data-aff=`
> occurs at a lower offset, fail the build.

This is the same shape as the three rules already in that function, it is testable, and it survives
`ops/build_zone_pages.py` being regenerated — which matters, because that generator overwrites all 114
pages and a hand-placed link would be silently erased. Conventions do not survive a code generator; a
failing check does.

### 5.2 The block is closed until Sort is done

The product block renders as a collapsed `<details>` sitting inside the Straighten section, never open
by default:

- **Sort not complete:** summary reads *"Finish Sort first. What stays is what decides this."* The
  links are **not in the DOM** — they are injected by JS on expand. They cannot be clicked, cannot be
  crawled as a buy CTA, cannot be screenshotted as a storefront.
- **Sort complete:** summary reads *"You have sorted this zone. Here is what the standard needs."*

Zone pages already deep-link into `quest.html?zone=<slug>`, and `quest.js` already writes per-zone
progress to localStorage. The block reads Sort completion from that existing key. No new state, no new
storage, no new privacy surface.

### 5.3 Quantity is computed by the reader, not by the catalogue

Where the page's own text makes quantity variable, the block must ask before it lists. The catalogue
says `Standard Quantity: 1` for a hamper sorter; the page says *"one bag per stream."* The page wins:

> **How many streams does your laundry actually have?** That number is how many bags you buy. Most
> households run two. The catalogue default is not your answer.

Same for the shoe zone's "one row per person" and the toy zone's "one category per open bin."

### 5.4 A mandatory "you may not need this" line

Every block states the condition under which buying nothing is the right answer, in the same type size
as the recommendation. Shoe zone: *"If everyone's shoes already fit in one row on the floor, you need
a tray for the muddy pair and nothing else."* This is the direct implementation of CLAUDE.md §3 and
diagnostic question 6, and it is what separates this from a storefront.

### 5.5 No prices on the page

Programme terms commonly prohibit displaying a scraped price, prices go stale, and a stale price makes
the page look abandoned. The catalogue's retail ranges are for planning and belong in the book.

### 5.6 The kit page orders itself by phase, not by price

`kit.html` is laid out Sort → Straighten → Shine → Safety → Standardize → Sustain. The sort container
set (MPL-00010) is the only one of the eight legitimately needed *before* sorting, so it comes first.
**The vacuum — a third of the basket and the best commission on the page — sits under Shine, in fourth
position.** That deliberately costs conversion. It is the whole argument of the site expressed as a
page layout, and if it is ever quietly reordered by price, the programme has stopped being what this
document describes.

---

## 6. Honest revenue maths

### 6.1 The 90-day number

All inputs stated. Traffic from the brief: 3 to 4 visitors a day, taken as 3.5.

```
Sessions, 90 days                3.5/day x 90              =   315 sessions
Reach the kit page               10% of sessions           =    32 page views
Outbound affiliate click         10% of page views         =   3.2 clicks
Click converts to an order       8% blended                =  0.26 orders
Average order value                                        = $45
Commission rate                  3.5% blended              = $1.58 per order

90-day affiliate revenue         0.26 x $1.58              = $0.41
```

**Forty-one cents.** And that is the *expected value* of a distribution whose single most likely
outcome is **zero orders and zero dollars**.

Run the bracket, generous at every step — 20% reach the page, 20% click out, 12% convert:

```
315 x 0.20 x 0.20 x 0.12 = 1.5 orders x $2.50 = $3.78
```

**So: $0 to $4 in 90 days, most likely $0.** Not "modest." Not "a foundation for growth." Zero, with a
small chance of the price of a coffee. Anyone who needs a bigger number should change the traffic, not
the spreadsheet.

### 6.2 The finding that should change a decision: Amazon's clock will not close

Amazon requires **three qualifying sales within 180 days** or the account closes.

```
Sessions, 180 days       3.5 x 180                        = 630
Orders, all merchants    630 x 0.10 x 0.10 x 0.08         = 0.50
Amazon's share           4 of the 8 items, ~50%           = 0.25 orders
```

Expected Amazon orders in the whole probation window: **0.25.** Using a Poisson model at λ = 0.25, the
probability of reaching three:

```
P(X >= 3) = 1 - e^-0.25 (1 + 0.25 + 0.03125) = 1 - 0.9974 = 0.26%
```

Even on the generous funnel from 6.1, λ ≈ 1.4 and P(X ≥ 3) is about **17%**.

**So the Amazon account is between 83% and 99.7% likely to close on its own probation.** That is a
decision, not a caveat. Three options, and the first is recommended:

1. **Apply to the other nine now, hold Amazon until traffic is ~10 to 15 visitors a day.** Amazon
   permits re-application after closure and the tag is a one-line change in
   `ops/affiliate-accounts.json`, so nothing is lost by waiting and the build is unaffected. Amazon is
   four of the eight assignments; run the page with those four on their fallbacks.
2. Apply now, treat closure as the expected outcome, re-apply later.
3. Apply now and source three sales from a non-site channel. Only if that is genuinely arm's length —
   self-purchases through your own links violate the operating agreement.

### 6.3 What traffic would make this matter

Revenue per session on the improved funnel — 30% reach the page, 15% click out, 10% convert:

```
0.30 x 0.15 x 0.10 x $1.58 = $0.0071 per session
```

| Goal | Sessions needed | Per day | vs today |
|---|---|---|---|
| Amazon's 3 sales, ~90% confident, in 180 days | ~2,400 in 180 days | **~13/day** | **4x** |
| $100 / month | ~14,000 / month | ~470/day | ~130x |
| $250 / month | ~35,000 / month | ~1,175/day | ~335x |
| $1,000 / month | ~141,000 / month | ~4,700/day | ~1,340x |

**The two thresholds are very far apart, and that is the actionable finding.** Keeping the Amazon
account alive needs roughly **13 visitors a day** — four times current traffic, and plausible within a
year. Affiliate becoming a *line item* needs **1,175 a day**. Affiliate contributing meaningfully to
the $20k/month goal needs traffic this site will not have for years, if ever.

### 6.4 The comparison that decides how much effort this deserves

```
Affiliate, per session                         $0.0071
Print Pack at 0.5% site-wide conversion        0.005 x $17.90 = $0.0895 per session
```

**The $19 digital pack is worth about 13 times more per visitor than the entire affiliate programme.**
One consult at $250 exceeds the affiliate programme's *lifetime* earnings at current traffic by a wide
margin.

**Conclusion.** Build it, because the brief is right that it is cheap and compounds. Build it **once,
small, on one page**, and then leave it alone. Do not build 114 zone blocks, do not build the
filterable 123-product catalogue page, and do not spend a single hour on affiliate that could go to
traffic or to the Print Pack. **The correct budget for this programme is one page and a quarterly link
audit.** Revisit at 500 sessions a month; reconsider the whole shape at 5,000.

---

## 7. Defect found in `ops/affiliate.py`

The disclosure-ordering rule in `check()` uses the **last** affiliate link rather than the first:

```python
if s.index(DISCLOSURE_ID) > s.rindex("data-aff=") if "data-aff=" in s else False:
```

`rindex` returns the final occurrence, so a page whose disclosure sits *after* the first link but
before the last one passes the check. Verified:

```
page = 'AAA data-aff=1 BBB affiliate-disclosure CCC data-aff=2'
current rule flags it:  False
correct rule flags it:  True
```

The FTC requirement is that the disclosure precede **all** links, so the comparison should be against
`s.index("data-aff=")`. The surrounding conditional expression is also hard to read and should be an
ordinary `if`. Low-risk fix, and it should land before the first link ships, since this is the rule
that will be relied on rather than re-read.

---

## 8. Release one checklist

| # | Item | Gate |
|---|---|---|
| 1 | Fix the `rindex` defect in `check()` (section 7) | before any link |
| 2 | Add the Straighten-offset rule to `check()` (5.1) | before any link |
| 3 | Apply to nine programmes; hold Amazon (6.2) | Phil |
| 4 | Split the MPL-00098 row: monitor vs absorber are different products | commerce |
| 5 | Populate 8 CSV rows; `Link Status` leaves `Unverified` only when a real URL is in place | after 3 |
| 6 | Build `site/kit.html`, phase-ordered, disclosure above the links, no prices | after 5 |
| 7 | One text link from each zone page's Shine section, via the generator | after 6 |
| 8 | Analytics: `affiliate_click` with `product_id`, `merchant`, `source_page` | with 6 |
| 9 | `qa-reviewer` verifies disclosure position, no links in downloads, mobile | before deploy |
| 10 | 90-day link audit scripted against the CSV | +90 days |

Zone-level links are **release two and are gated on the per-zone product pass** described in 0.3.
Nothing in section 3 should be built until that mapping is corrected.
