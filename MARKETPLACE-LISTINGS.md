# Marketplace listings: Amazon KDP and Etsy

**Written 2026-09-03. Everything marked VERIFIED was fetched or measured that
day and the source is named. Everything marked UNVERIFIED could not be checked,
and is written that way on purpose rather than filled in from memory.**

Owner: `content-editor`. The paste-ready copy is in this file. The files that
get uploaded, and the scripts that check them, are in `build/listings/`.

---

## 0. Why this exists, in one paragraph

The business sells in exactly one place and that place had 52 visitors in
thirty days, none of them from Google (`REVENUE-REVIEW-2026-09-04.md` section
1). A finished 262,000 word book and 155 finished print packs are sitting on a
disk. Improving conversion on a page nobody visits is arithmetic on zero.
Putting the finished product in front of traffic that already exists is the
fastest change available, and it is the only one that does not depend on us
solving discovery ourselves first.

Phil's part is creating two accounts and pasting. Nothing below asks him to
write anything.

---

## 1. What was verified, and what was not

### Verified on 2026-09-03

| Fact | Source |
|---|---|
| Cover: JPEG or TIFF, ideal 2560 high x 1600 wide, minimum 1000 x 625, maximum 10000, height/width at least 1.6:1, RGB, under 50 MB | KDP help `G200645690` |
| Description: 4000 character limit **including HTML tags**; `<h1>`, `<h2>` and `<h3>` are **not supported**; `<h4>` to `<h6>`, `<p>`, `<br>`, `<b>`, `<i>`, `<em>`, `<u>`, `<ol>`, `<ul>`, `<li>` are; no URLs, no reviews or testimonials, no price or availability, no emoji | KDP help `G201189630` |
| Keywords: 7 slots; do not use quotation marks; avoid words already in the title or the categories; avoid subjective quality claims and time-sensitive words | KDP help `G201298500` |
| Categories: **3**, chosen in the KDP picker | KDP help `G200652170` |
| 70% royalty band on Amazon.com is **$2.99 to $12.99**, widened from $9.99 on 7 July 2026. 35% band is $0.99 to $200 | KDP help `G200634560` |
| Delivery cost on the 70% plan is **$0.15/MB** on Amazon.com, charged on Amazon's converted file, minimum $0.01 | KDP Digital Book Pricing Page `G200634500` |
| Metadata rule: the title, subtitle and contributor in the file must match what is typed into the form, and none of them may contain a URL, keywords or genre descriptions | KDP Guide to Kindle Content Quality `G200952510` |
| Every browse category path in section 2.5 exists in the live Kindle Store, with its node ID | walked with `build/listings/amazon_nodes.py` |
| Every BISAC code in section 2.5 | bisg.org subject heading lists, fetched today |
| The EPUB opens, every one of its 56 XHTML documents is well-formed, its manifest and spine resolve, no file is undeclared, it has both a nav document and an NCX, and every internal link and image reference resolves | `build/listings/verify_epub.py` |
| The cover is 1600 x 2560, RGB, ratio exactly 1.6000, 167 KB | measured with Pillow |
| Book length: 262,633 words excluding inline SVG, across 56 documents | measured from the EPUB |
| The five Etsy deliverables are US Letter, contain the page and card counts their titles claim, and have no near-empty pages | `build/listings/check_etsy.py` |

### UNVERIFIED, and why

| Thing | Why not | What to do about it |
|---|---|---|
| **epubcheck conformance** | No JRE on this machine, and epubcheck is not installed. `verify_epub.py` covers what a zip and XML reader can see; it is not a substitute | KDP's own converter runs on upload and will report errors. Read that report rather than assuming |
| **How the book renders on a device** | Only Kindle Previewer or Amazon's converter can answer this | Use the online previewer on the upload screen before hitting Publish |
| **The real delivery cost** | Amazon charges on the size of its converted file, not the EPUB. The EPUB is 0.81 MB, which would be about $0.12 | KDP shows the exact figure on the pricing screen before publishing |
| **Whether a cover may carry a website URL** | The cover criteria page says nothing either way, and the rule that forbids URLs is written about descriptions, not covers | Sidestepped. See section 2.7: the KDP cover has the URL removed |
| **Title and subtitle character limits** | Not stated on any KDP page fetched | Both are far short of any plausible limit |
| **Every Etsy fee, limit and taxonomy** | Etsy returns HTTP 403 to automated requests. `etsy.com/legal/fees`, the seller handbook and every help article tried all refused | Read the fee page while signed in and run `build/listings/etsy_economics.py` with the real numbers. Do not price off any figure in this file that is not labelled measured |
| **Etsy comparables, competitor prices, competitor tags** | Same block | Nothing in this file is presented as a comparable. There are none here |

**Nothing in this package claims the book has readers, reviews, rankings or
sales, because it has none.**

---

## 2. Amazon KDP: the book

Everything in this section is also in `build/listings/kdp/fields.json`, which
`build/listings/check_kdp.py` checks. That check passes with zero failures as
of 2026-09-03.

### 2.1 The form, field by field

| Field | Paste this |
|---|---|
| Language | `English` |
| Book Title | `6S Success: Home Edition` |
| Subtitle | `Sort, Straighten, Shine, Safety, Standardize, Sustain: A Room by Room Method for a Home That Works` |
| Series | leave blank |
| Edition number | `1` |
| Author, first name | `Philip` |
| Author, last name | `Kling` |
| Contributors | none |
| Publisher | `Nova Consulting` |
| Description | section 2.2, or paste the file `build/listings/kdp/description.html` |
| Publishing rights | *I own the copyright and I hold the necessary publishing rights* |
| Primary audience, sexually explicit | `No` |
| Reading age | leave blank |
| Keywords | section 2.4 |
| Categories | section 2.5 |
| ISBN | leave blank. Amazon issues a free ASIN |
| Manuscript | `build/6S-Success-Home-Edition.epub` |
| Cover | `build/listings/kdp/cover-kdp.jpg`, **not** `build/cover.png`, see 2.7 |
| DRM | `No` |
| KDP Select | `No`, see 2.8 |
| Territories | `All territories (worldwide rights)` |
| Royalty plan | `70%` |
| List price | `$9.99` USD, primary marketplace Amazon.com |

**Why the subtitle is that.** The book's own title page reads *6S SUCCESS /
Home Edition / Sort · Straighten · Shine · Safety · Standardize · Sustain*, and
the cover carries the same six words. KDP treats a subtitle that does not match
the file as a content quality defect, and treats a subtitle stuffed with genre
words as a metadata violation, so the first half of the subtitle is taken
verbatim from the book and the second half is a plain description of what the
book does. It is deliberately not carrying search terms. Those go in the
keywords, which is what the keywords are for.

### 2.2 Description

4000 character limit including tags. This is **2472**, so there is room to
extend later. It uses only tags KDP supports: `<h4>`, `<p>`, `<ul>`, `<li>`,
`<b>`, `<i>`. It contains no URL, no testimonial and no non-ASCII character.

The previous draft at `build/kdp/description.html` used `<h2>` three times.
KDP's help page states plainly that `<h1>`, `<h2>` and `<h3>` are not
supported, so that version would have rendered wrong. This one does not use
them.

Paste everything between the rules, as one block:

---

```html
<h4>Most home advice starts with a container. This one starts with a question.</h4><p>What is this space actually supposed to do?</p><p>Answer that honestly and most organizing problems change shape. Keys are not lost because you need a nicer tray. They are lost because the tray is in the wrong room, or there are four places keys could go, or the thing that should hold them is full of something else. A bin does not fix any of that.</p><p><b>6S Success: Home Edition</b> brings a method used on factory floors for decades into the house, in plain English, with no jargon and no lectures. Six passes, always in the same order:</p><ul><li><b>Sort.</b> Decide what stays.</li><li><b>Straighten.</b> Give what stays a home where you actually use it.</li><li><b>Shine.</b> Clean it properly, and use the cleaning to notice what is wearing out.</li><li><b>Safety.</b> Remove what could hurt somebody.</li><li><b>Standardize.</b> Make the right state obvious at a glance.</li><li><b>Sustain.</b> Attach the reset to something you already do.</li></ul><p>The order matters, and the book explains why. Straightening before sorting is only rearranging things you were about to get rid of.</p><h4>Built around micro zones, not whole rooms</h4><p>Nobody finishes a kitchen on a Saturday. Almost anyone can finish the prep counter, or the drawer beside the stove, or the shelf by the door. This book maps <b>114 micro zones</b> across twenty rooms and works every one of them the same way: what the zone is for, what usually goes wrong, the root cause underneath, the smallest fix that holds, and the standard you leave behind.</p><h4>What is inside</h4><ul><li>The full six step method, one step at a time, with worked examples</li><li>Twenty room playbooks, from the entryway to the patio</li><li>114 micro zones with their functions, their root causes and their hazards</li><li>A written standard and a sustain trigger for every zone, so the work holds</li><li>Guidance for shared households, small spaces, and limits on reach and mobility</li></ul><h4>Who it is for</h4><p>People who have organized the same drawer three times. Households where one person keeps resetting what everybody else undoes. Anyone who suspects the problem is not willpower and is right about that.</p><p><i>Philip Kling spent twenty years installing continuous improvement systems inside large organizations as a Lean Six Sigma Master Black Belt. This is that discipline, rewritten for a house.</i></p>
```

---

### 2.3 Author bio

**This does not go in the KDP title-setup form.** KDP has no author bio field
for eBooks. The bio lives in **Amazon Author Central**, which is a separate
free signup on the same Amazon login, done after the book is live. See owner
action 14, step 8.

Paste as plain text, no HTML:

> Philip Kling spent twenty years installing continuous improvement systems
> inside organizations as a Lean Six Sigma Master Black Belt: a statewide
> benefit process taken from thirty-two days to under seven, a company-wide
> Lean transformation where 6S standardization cut warehouse space and
> inventory requirements by eighty percent, then six years building the same
> systems across a forty-thousand-person organization.
>
> None of that makes a house tidy on its own. What it means is that the six
> steps are a working method with real numbers behind them rather than
> invented advice.
>
> He writes as Nova Consulting, in Boise, Idaho.

**Claims in this bio that QA should verify before it is published:** the
thirty-two days to seven figure, the eighty percent figure, the twenty years,
and the six years. All four are already published on `site/about.html` and
`site/consulting.html`, so they are the business's existing public position
rather than anything invented here, but a number repeated is not a number
checked.

**PMP is deliberately not in this bio.** It appears nowhere in the book, on the
site, or anywhere in this repository. If Phil holds a current PMP, add
`, PMP` after `Master Black Belt` and it is accurate. If it has lapsed, leave
it out.

### 2.4 The seven keyword slots

KDP's guidance, read today, is that keyword slots are indexed alongside the
title, subtitle and categories, that quotation marks narrow rather than widen a
match, and that repeating a word Amazon has already indexed from the title
wastes a slot. So these seven were chosen to add vocabulary that appears
nowhere else in the listing. `check_kdp.py` enforces that: it fails if any slot
repeats a content word from the title or subtitle.

The phrasings are grounded in Amazon's own Kindle Store autocomplete, pulled
today with `build/listings/amazon_suggest.py`. That endpoint returns an ordered
list, not volumes, so this is evidence of **what people type**, not of how
many. Real expansions observed included *decluttering and organizing*,
*declutter your home*, *cleaning and organizing*, *cleaning checklist*,
*cleaning planner*, *declutter and cleaning planner*, *clutter free*,
*organizing home*, *home routines* and *getting organized with add*.

| # | Paste | Chars | Why this one |
|---|---|---|---|
| 1 | `decluttering and organizing your house` | 38 | The two words the category actually turns on, in the order Amazon's own autocomplete pairs them. Neither appears in our title, so this slot is doing real work |
| 2 | `cleaning checklist and weekly reset routine` | 43 | *cleaning checklist* is a live autocomplete phrase. *reset* and *routine* are the book's own vocabulary, 125 and 16 uses, and appear nowhere else in the metadata |
| 3 | `clutter free living for busy families` | 37 | *clutter free* is a real autocomplete expansion. *families* reaches the shared-household reader the book is largely about, and *busy* catches the query without our claiming anything about time |
| 4 | `kitchen bathroom garage closet organizing` | 41 | Four high-intent room nouns, all four genuinely covered by room playbooks, none of them in the title. One slot buys four entry points |
| 5 | `deep clean one small zone at a time` | 35 | The book's actual differentiator, and *small* and *zone* are unindexed elsewhere. Also feeds the Small Spaces category |
| 6 | `5S lean six sigma for the household` | 35 | Accurate: the book states its 5S lineage and 5S appears twelve times. A small audience with nobody competing for it, and no other slot reaches them |
| 7 | `getting organized when you feel overwhelmed` | 43 | *getting organized* is a live autocomplete stem, and *overwhelm* is in the book ten times. This is the emotional query, the one people type at 11pm |

Longest slot is 43 characters. The per-slot character limit is UNVERIFIED, and
50 is the figure the field has long enforced, so everything is inside it.

### 2.5 Categories

**KDP accepts three.** That was confirmed on the KDP Categories help page today
and is not the old two-plus-email arrangement. Seven are ranked here so there
is a considered reserve when the picker's wording differs or when a category
turns out to be the wrong shelf.

Every path below was walked on the live Kindle Store today with
`build/listings/amazon_nodes.py` and the node ID is the one Amazon returned.
Every BISAC code was read off bisg.org today. KDP's own picker sometimes
phrases a node slightly differently from the store; pick the nearest match.

**Enter these three:**

| # | Path | Node | BISAC | Why |
|---|---|---|---|---|
| 1 | Crafts, Hobbies & Home > How-to & Home Improvement > **Cleaning, Caretaking & Relocating** | 156888011 | `HOM019000` HOUSE & HOME / Cleaning, Caretaking & Organizing | The shelf the book is literally about. If a shopper browses one category and finds this book, this is the one |
| 2 | Crafts, Hobbies & Home > How-to & Home Improvement > **Household Hints** | 156896011 | `HOM016000` HOUSE & HOME / Reference | A different browsing intent from cleaning: the reader who wants the practical reference. A 114-zone reference with a standard per zone is exactly that, and it is a smaller shelf, so visibility is cheaper |
| 3 | Self-Help > **Self-Management** | 202437601011 | `SEL044000` SELF-HELP / Self-Management / General | Two of the six steps, Standardize and Sustain, are habit and maintenance. Self-Management is what that is, and it is more honest than Personal Transformation, which is what the previous draft chose |

**Reserve, in order:**

| # | Path | Node | BISAC | Why it is reserve and not starter |
|---|---|---|---|---|
| 4 | ... > **Small Spaces** | 14530440011 | `HOM023000` | The book has genuine small-space guidance, and this is a small shelf where a new book can be seen. It is reserve only because it describes a slice of the book, not the book |
| 5 | ... > **Moving & Relocation** | 18623131011 | `HOM025000` | Twenty room playbooks and the Moving In kit map onto a move well. Partial fit, so a swap candidate rather than a first pick |
| 6 | Business & Money > Management & Leadership > **Quality Control** | 154962011 | `BUS053000` | The only shelf where "6S" means something to the browser, and the 5S lineage is real. **But** a Quality Control browser is shopping for industrial QC, and KDP says plainly it does not tolerate categorisation that misleads readers. Use only if the consumer shelves produce nothing, and expect it to be argued with |
| 7 | Self-Help > **Personal Transformation** | 156571011 | `SEL031000` SELF-HELP / Personal Growth / General | The previous draft's choice. Bigger shelf, weaker fit: the book does not promise personal transformation, it promises a tidier kitchen. Lowest of the seven for that reason |

### 2.6 Price, and the 35% versus 70% band

**Recommendation: $9.99 on the 70% plan.**

The 70% band on Amazon.com is $2.99 to $12.99, widened from $9.99 on 7 July
2026. That is new, and it means $12.99 is now available at 70% where it was not
two months ago.

| At $9.99 | Amount |
|---|---|
| 70% plan | 0.70 x ($9.99 − delivery). At the EPUB's own 0.81 MB and $0.15/MB, delivery is about $0.12, so about **$6.91 a copy** |
| 35% plan | 0.35 x $9.99 = **$3.50 a copy**, no delivery deducted |
| Difference | **$3.41 a copy**, so 70% is not a close call |

The 35% plan is only worth considering below $2.99, above $12.99, or for
public-domain work. None applies. Sales to customers outside the 70%
territories pay out at 35% either way; that is a function of where the buyer
is, not of the plan, and it is why the Bookshelf will show both rates.

**Why $9.99 and not $12.99.** Three reasons, in order of weight. It is the
exact price the book already sells for on 6s-success.com, so there is no
channel to explain away. A 262,000 word book would carry $12.99 on length
alone, but with no reviews and no author platform, price is the only quality
signal a shopper has, and an unknown book at the top of its band is a harder
sell than the same book at the familiar one. And raising a price later is a
one-field change that costs nothing, while cutting one reads as a book that
did not sell.

**The trigger to revisit:** at 25 paid copies or 10 verified reviews,
whichever lands first, test $12.99. That would take the royalty from about
$6.91 to about $9.00 a copy, a 30% increase on the same book. Record it in
`EXPERIMENTS.md` when it happens.

### 2.7 The cover

`build/cover.jpg` is 1600 x 2560, RGB, ratio exactly 1.6000, 167 KB. That meets
every published KDP requirement: JPEG, above the 1000 x 625 minimum, below the
10000 maximum, at or above the 1.6:1 ideal, RGB, under 50 MB. It is in fact
exactly the 1600 x 2560 KDP names as ideal.

**One change was made for KDP.** The cover carries `6s-success.com` across the
foot. `build/listings/build_kdp_cover.py` produces
`build/listings/kdp/cover-kdp.jpg`, which is the same image with that one line
painted out in the background colour sampled from the image itself, and every
pixel outside a 105-pixel band verified identical to the original. Upload that
one.

Three reasons, and the third is the one that decides it. At the size a cover is
actually seen, about 160 pixels wide in a search result, a 40-pixel line of
type is a grey smudge. A URL on the cover reads as self-published in a category
where the competition does not do it. And KDP's rules forbid URLs in the
description while saying nothing about covers, which makes rejection an
unverified risk that costs nothing to avoid: a rejected cover is a book stuck
in review, and the URL was buying nothing.

`build/cover.png` cannot be uploaded at all. KDP accepts JPEG and TIFF only.

### 2.8 KDP Select: no

KDP Select requires 90 days of digital exclusivity, which would mean pulling
the book from 6s-success.com and from every other channel. Direct is the only
channel that has ever taken money. Do not trade it for page reads.

---

## 3. Etsy: the print packs

### 3.1 What to list, and why it is five and not 155

There are **155** deliverables built: 114 zone packs, 20 room packs, 15
situation kits and 6 area bundles, counted today in `build/products/`. The
review said 109 and 19; the measured numbers are 114 and 20.

**Do not list 155 on day one.** The listing fee is not the reason: at the
long-standing $0.20, 155 listings renewing three times a year is about $93,
which is real but not decisive. The reasons that are decisive:

1. **Listing images are the actual work.** A printable listing lives or dies on
   its photos, and 155 listings means 155 sets. Five means five, and they are
   already built.
2. **They would compete with each other.** 114 zone packs share nearly
   identical copy and would chase the same handful of queries. Etsy ranks in
   part on a listing's own history, so splitting the same demand 114 ways means
   no listing ever accumulates any.
3. **A $4 item is a poor Etsy unit.** After a fixed processing component and a
   listing fee, the fixed costs are a large share of a $4 order, and each one
   still carries a full customer-service surface.
4. **Nothing has ever sold, so nothing is known.** Day one's job is to learn
   which framing converts: whole-house completeness, single-room specificity,
   or life-event timing. Five listings test exactly those three and can be read
   in a month. 155 test nothing, because no one of them gets enough traffic to
   mean anything.

So: **one flagship, two rooms, two life events.**

| | Listing | Tests | Price | Direct price |
|---|---|---|---|---|
| L1 | Whole House Print Pack | does completeness sell | $22.00 | $19.00 |
| L2 | Kitchen Pack | does the highest-demand single room sell | $10.00 | $9.00 |
| L3 | Entryway Pack | does the smallest, easiest room sell | $10.00 | $9.00 |
| L4 | Moving In Kit | does a life event sell | $16.00 | $14.00 |
| L5 | Holiday Hosting Kit | does a season sell, launched in time for one | $16.00 | $14.00 |

**Deliberately not listed: the Standards Pack on its own.** It is free on
6s-success.com. Selling it on Etsy for money would be a trust problem the first
time a buyer noticed. It is included inside L1 as part of that bundle, with no
claim of exclusivity attached.

**Why these prices.** One rule: charge enough on Etsy that what is left after
Etsy's cut is not less than what is left after Stripe's cut on the site. That
keeps the site the cheaper place to buy, which is where we would rather the
customer be, without making the marketplace a loss. Under the fee rates in
section 3.7, all five clear it. Re-run
`build/listings/etsy_economics.py` with the real rates before publishing; if
they have moved, the prices move with them.

### 3.2 The files each listing delivers

Built and verified today by `build/listings/build_etsy_assets.py`, which
renders the source HTML through a headless browser and then measures the
result. Every file is US Letter, every page count below is counted from the
finished PDF, and no file is anywhere near an upload cap.

| Listing | Files | Pages | Cards |
|---|---|---|---|
| L1 | `6S-Whole-House-Print-Pack.pdf`, `6S-Standards-Pack.pdf`, `How-to-print-these-cards.pdf` | 76 + 20 + 1 | 684 |
| L2 | `6S-Kitchen-Pack.pdf`, `How-to-print-these-cards.pdf` | 6 + 1 | 42 |
| L3 | `6S-Entryway-Pack.pdf`, `How-to-print-these-cards.pdf` | 5 + 1 | 30 |
| L4 | `6S-Moving-In-Kit.pdf`, `How-to-print-these-cards.pdf` | 11 + 1 | 78 |
| L5 | `6S-Holiday-Hosting-Kit.pdf`, `How-to-print-these-cards.pdf` | 13 + 1 | 96 |

They are at `build/listings/etsy/<slug>/files/`. Listing images are at
`build/listings/etsy/<slug>/listing-images/`, 2000 x 1500, rendered from the
finished PDFs so a shopper is looking at the actual product. There are no
styled mockups, because there is no photograph of these cards printed and
sitting on a table, and inventing one is a claim about an object that does not
exist. **This is the weakest part of the Etsy package and the highest-value
thing to fix next:** print one pack, photograph it, and every listing gets
better.

**A defect was found and fixed on the way through.** The packs lay nine 3.5in
cards in three rows, 10.5in of content, against a 0.4in page margin that leaves
10.2in of printable height. Every pack overflowed by 0.3in, so every second page
of every rendered PDF was a near-empty sheet carrying three orphaned card
footers, and the card above it printed without its footer rule. The Whole House
PDF came out at 152 pages: 76 of cards and 76 of litter.
`build/listings/print_fix.css` corrects the geometry at render time and keeps
the cards at trading-card size. **This fix belongs upstream in
`ops/build_catalog.py`**, so the file the site delivers and the file Etsy
delivers stay the same file. Until it lands there, the two differ in page count
and the marketplace edition is the correct one. That is an engineering task, not
an owner gate.

### 3.3 Category and listing settings

Same for all five:

| Setting | Value |
|---|---|
| Category | Search the picker for **Templates**, then **Home Organization** or **Planners**. UNVERIFIED: Etsy's taxonomy could not be read today |
| Type | **Digital**, files delivered instantly on purchase |
| Who made it | I did |
| What is it | A finished product |
| When was it made | Made to order |
| Renewal | Manual, so a listing that is not working stops costing money |
| Returns | Digital downloads are not returnable once downloaded. Say so plainly in the shop policies; do not hide it |
| Personalisation | Off |
| Production partners | None |

### 3.4 The five listings, ready to paste

Tags are 13 per listing, the maximum, none over 20 characters. Both limits are
UNVERIFIED because Etsy blocks automated reads; the copy sits inside them
either way. `build/listings/check_etsy.py` re-checks all of it against
`build/listings/etsy-listings.json`.

None of these descriptions contains a URL, because Etsy does not allow a
listing to send a buyer elsewhere to transact.

---

#### L1, Whole House Print Pack, $22.00

**Title**

```
6S Whole House Print Pack - 684 Printable Cleaning and Organizing Cards, 114 Zones, 20 Rooms, Instant Download
```

**Tags**

```
home organization, cleaning checklist, declutter checklist, printable cards, house cleaning, cleaning schedule, decluttering, home reset, organizing printable, chore cards, room by room clean, household planner, whole house cleaning
```

**Description**

```
Every room in the house, broken into the small zones you can actually finish, on 684 printable cards.

Nobody finishes a kitchen on a Saturday. Almost anyone can finish the drawer beside the stove. So this pack does not hand you a room. It hands you 114 micro zones across 20 rooms, and takes every one of them through the same six steps, one card at a time:

SORT - decide what stays
STRAIGHTEN - give what stays a home where you actually use it
SHINE - clean it properly, and use the cleaning to notice what is wearing out
SAFETY - remove what could hurt somebody
STANDARDIZE - make the right state obvious at a glance
SUSTAIN - attach the reset to something you already do

The order is the method. Straightening before sorting is only rearranging things you were about to get rid of.

WHAT YOU GET

- 6S Whole House Print Pack, 76 pages, 684 cards at 2.5 x 3.5 inches, nine to a US Letter sheet
- 6S Standards Pack, 20 pages, one sheet per room, naming the standard each zone holds to and the everyday moment that triggers the reset
- A one page printing and cutting guide

Rooms covered: entryway, kitchen, pantry, dining room, living room, family room, primary bedroom, guest bedroom, kids bedroom, nursery, primary bathroom, guest bathroom, laundry, home office, garage, workshop, mudroom, hall closet, stair landing, patio.

HOW IT WORKS

Print on US Letter at 100 percent, on card stock if you have it. Cut along the card borders. Each card names one job and how you know you can stop. Work one card at a time and finish it before you pick up the next.

The cards are trading card size, so they sleeve, they fit a deck box, and two people can work different zones from the same pile.

WHO IT IS FOR

People who have organized the same drawer three times. Households where one person keeps resetting what everybody else undoes. Anyone who would rather finish one shelf today than fail at a whole room this weekend.

THIS IS A DIGITAL DOWNLOAD

Nothing ships. Three PDF files arrive as soon as your payment clears, and you can print them as many times as you like for your own household. Because the files cannot be returned once downloaded, they are not refundable, so please check the photos first: they are the actual pages, not a mockup.

The method here is adapted from 5S, used on factory floors for decades, with Safety added as its own step. Written by Philip Kling, a Lean Six Sigma Master Black Belt.
```

---

#### L2, Kitchen Pack, $10.00

**Title**

```
Kitchen Cleaning and Organizing Cards - 42 Printable Cards for 7 Kitchen Zones, Instant Download
```

**Tags**

```
kitchen organization, kitchen cleaning, pantry organizing, cleaning checklist, kitchen printable, declutter kitchen, cleaning cards, kitchen reset, home organization, cleaning schedule, fridge organization, kitchen planner, printable cards
```

**Description**

```
The kitchen, split into the seven zones you can finish one at a time.

Primary prep counter. Cooking zone. Sink and dishwashing zone. Upper cabinets. Lower cabinets and cookware. Utensil and utility drawers. Refrigerator and freezer.

Each one takes the same six passes, one card per pass:

SORT - decide what stays
STRAIGHTEN - give what stays a home where you actually use it
SHINE - clean it properly, and use the cleaning to notice what is wearing out
SAFETY - remove what could hurt somebody
STANDARDIZE - make the right state obvious at a glance
SUSTAIN - attach the reset to something you already do

The order matters. Sorting after you have arranged things means arranging things you were about to remove.

WHAT YOU GET

- 6 printable pages: 42 cards at 2.5 x 3.5 inches, nine to a US Letter sheet, plus the kitchen standards sheet
- A one page printing and cutting guide

The standards sheet is the part that makes it hold. It names, for each of the seven zones, what the zone looks like when it is right and the everyday moment that resets it. Post it inside a cupboard door.

HOW IT WORKS

Print at 100 percent on US Letter, card stock if you have it, cut along the card borders. Pick one zone, work its six cards in order, and stop. Thirty minutes gets you a finished prep counter, which is worth more than four hours of a half-finished kitchen.

THIS IS A DIGITAL DOWNLOAD

Nothing ships. Two PDF files arrive as soon as your payment clears, and you can print them as often as you like for your own household. Digital files are not refundable once downloaded, so please look at the photos first: they are the actual pages.

Adapted from 5S, the method used on factory floors for decades, with Safety added as its own step. Written by Philip Kling, a Lean Six Sigma Master Black Belt.
```

---

#### L3, Entryway Pack, $10.00

**Title**

```
Entryway Cleaning and Organizing Cards - 30 Printable Cards for 5 Entryway Zones, Instant Download
```

**Tags**

```
entryway organizing, mudroom organizing, declutter entryway, cleaning checklist, entryway printable, printable cards, home organization, drop zone, coat closet cleanout, daily reset routine, household chores, shoe zone, front hall reset
```

**Description**

```
The entryway is four square metres that decides how the whole house feels, and it is the fastest room in the house to fix.

Five zones, six cards each, thirty cards:

- Landing zone, the surface where keys and mail come to rest
- Coat and outerwear zone
- Shoe and boot zone
- Entry console or bench
- Door, mat and the floor immediately inside it

Every zone takes the same six passes: Sort, Straighten, Shine, Safety, Standardize, Sustain. One card per pass, each naming a single job and how you know you can stop.

Keys are not lost because you need a nicer tray. They are lost because the tray is in the wrong place, or there are four places keys could go. The cards go after that, not after the tray.

WHAT YOU GET

- 5 printable pages: 30 cards at 2.5 x 3.5 inches, nine to a US Letter sheet, plus the entryway standards sheet
- A one page printing and cutting guide

HOW IT WORKS

Print at 100 percent on US Letter, card stock if you have it, cut along the card borders. Start with the landing zone. It is the one that makes the difference you notice on the way in.

Good first pack if you have not tried this way of working before. Five zones is one afternoon, and the standards sheet is what stops it drifting back.

THIS IS A DIGITAL DOWNLOAD

Nothing ships. Two PDF files arrive as soon as your payment clears, printable as often as you like for your own household. Digital files are not refundable once downloaded, so please look at the photos first: they are the actual pages.

Adapted from 5S, the method used on factory floors for decades, with Safety added as its own step. Written by Philip Kling, a Lean Six Sigma Master Black Belt.
```

---

#### L4, Moving In Kit, $16.00

**Title**

```
Moving In Checklist Cards - 78 Printable Cards, 13 Zones in the Order to Unpack Them, Instant Download
```

**Tags**

```
new home checklist, moving checklist, unpacking checklist, first apartment, home organization, moving printable, new homeowner gift, housewarming gift, moving planner, declutter checklist, printable cards, setting up home, new house gift
```

**Description**

```
The order to unpack in, so the first week works before the boxes are gone.

Moving does not fail because people are disorganised. It fails because everything is equally urgent at once, and the boxes that matter on night one look exactly like the boxes that can wait a month.

This is 13 zones, in the order that actually matters, with 78 cards taking each one through the same six passes: Sort, Straighten, Shine, Safety, Standardize, Sustain.

The 13 are the ones that decide whether week one works: the whole entryway, five zones of it, so the house has a front door that functions from day one. Four kitchen zones, the ones you have to cook and wash up in before the boxes are unpacked. The bed and the closet. The bathroom vanity and the cupboard under the sink.

You are setting up a room you have never lived in, which is the one moment when Straighten is genuinely easy: nothing has a home yet, so nothing has a wrong home to be moved out of. That is why this is worth doing during the move rather than six months later.

WHAT YOU GET

- 11 printable pages: 78 cards at 2.5 x 3.5 inches, nine to a US Letter sheet, plus the standards sheets for the zones covered
- A one page printing and cutting guide

HOW IT WORKS

Print at 100 percent on US Letter before moving day, cut the cards, put them in your pocket. Work them in order. Each card is one job, small enough to finish in a room full of boxes, and each names the condition that tells you to stop and move on.

The standards sheets are the reason this outlasts the move. They name what each zone looks like when it is right, and the everyday moment that resets it, so the house you set up in week one is still the house you have in month six.

A housewarming present for somebody mid-move that is more use than a candle.

THIS IS A DIGITAL DOWNLOAD

Nothing ships. Two PDF files arrive as soon as your payment clears, printable as often as you like for your own household. Digital files are not refundable once downloaded, so please look at the photos first: they are the actual pages.

Adapted from 5S, the method used on factory floors for decades, with Safety added as its own step. Written by Philip Kling, a Lean Six Sigma Master Black Belt.
```

---

#### L5, Holiday Hosting Kit, $16.00

**Title**

```
Holiday Hosting Prep Cards - 96 Printable Cards for the 16 Zones Guests Actually See, Instant Download
```

**Tags**

```
holiday hosting, hosting checklist, guest room prep, guest ready home, entertaining prep, holiday checklist, cleaning checklist, home organization, printable cards, guest bathroom prep, dinner party prep, house cleaning, holiday planner
```

**Description**

```
The guest-facing rooms, in the week before rather than the morning of.

Hosting goes wrong in a predictable place: everything gets done at once, on the day, by one person, and half of it is work that could have been finished a week earlier while nobody was watching.

This is the 16 zones a guest actually experiences, with 96 cards taking each one through the same six passes: Sort, Straighten, Shine, Safety, Standardize, Sustain.

The 16 are the guest bedroom in full, five zones from the bed and linens to the nightstand, the dresser, the closet and the corner they will work from. The guest bathroom in full, five zones covering the vanity counter, the vanity storage, the shower or tub, the toilet area and the linen. The dining room in full, five zones from the table to the sideboard, the china cabinet and the drinks station. And the coat zone at the entryway, because sixteen coats have to go somewhere.

WHAT YOU GET

- 13 printable pages: 96 cards at 2.5 x 3.5 inches, nine to a US Letter sheet, plus the standards sheets for the zones covered
- A one page printing and cutting guide

HOW IT WORKS

Print at 100 percent on US Letter, cut the cards, and deal them out. This is the pack that works best with more than one person: the cards are single jobs with a clear finish line, so handing three of them to somebody else is a real handover rather than a request for help.

Start a week out with the zones nobody will notice you doing. Leave the day-of jobs on the pile for the day.

The standards sheets name what each zone looks like when it is right, so the same evening is easier next time.

Not themed for any one holiday. It works for Thanksgiving, for Christmas, for a birthday weekend, and for the in-laws arriving on Friday.

THIS IS A DIGITAL DOWNLOAD

Nothing ships. Two PDF files arrive as soon as your payment clears, printable as often as you like for your own household. Digital files are not refundable once downloaded, so please look at the photos first: they are the actual pages.

Adapted from 5S, the method used on factory floors for decades, with Safety added as its own step. Written by Philip Kling, a Lean Six Sigma Master Black Belt.
```

---

### 3.5 A note on tags

Every tag was chosen against two rules. It has to describe what the buyer
receives, and it has to be a phrase a person would type. Two kinds of tag were
deliberately left out even though they would pull traffic:

**Physical-product tags.** *entryway organizer*, *shoe rack*, *key holder*.
Those queries want a shelf, not a PDF. Traffic that bounces is worse than no
traffic, because Etsy ranks partly on what happens after the click.

**Theme tags we cannot honour.** *christmas cleaning* was cut from L5. The
cards are not Christmas-themed, and somebody arriving on that query is looking
for artwork we do not have.

### 3.6 Shop setup

| Field | Value |
|---|---|
| Shop name | `SixSSuccess`, or if taken: `SixSHome`, `SixSSuccessHome`, `NovaSixS`. Availability is UNVERIFIED; Etsy allows one free change later, so take whichever is free rather than stalling |
| Country | United States |
| Currency | USD |
| Language | English |
| About section | The description text from L1 works as a starting point. It can be written later; do not let it block opening |
| Shop policies | Digital downloads, no returns once downloaded. Say it plainly |

### 3.7 What Etsy charges, and what is left

**Every number in this section is UNVERIFIED.** Etsy returned HTTP 403 to every
automated request on 2026-09-03: the fee page, the seller handbook and the help
articles all refused. Read the real rates off the fee page while signed in.

The **structure** is stable enough to plan against, even when the rates are
not:

- a **listing fee** per listing, charged again on renewal, whether or not it
  sells
- a **transaction fee**, a percentage of item price plus shipping
- **payment processing**, a percentage plus a fixed amount per order, and the
  percentage varies by the seller's country
- **Offsite Ads**, a percentage charged only on orders attributed to an ad Etsy
  bought. Shops under a revenue threshold can opt out; above it, participation
  is mandatory
- **currency conversion** on non-USD orders
- Etsy collects and remits US sales tax on the buyer's behalf; that is not
  seller revenue and should never be counted as such

To make the arithmetic visible, run:

```
python build/listings/etsy_economics.py \
    --listing-fee 0.20 --transaction-pct 6.5 \
    --processing-pct 3.0 --processing-fixed 0.25 --offsite-pct 15
```

with **today's real numbers substituted**. It prints, per listing, the fees,
the net, the effective take rate, the same product's net through the site's own
Stripe checkout for comparison, and the standing cost of keeping five listings
up for a year with no sales at all. The rates in that example line are
placeholders to show the shape of the output; they are not a measurement and
must not be pasted into a plan.

Not included in any of it: income tax, and the cost of Phil's time, which
`COST-GOVERNANCE.md` still records as unmeasured.

---

## 4. How to tell whether this worked

Neither marketplace reports into our analytics, so this needs its own reading.
Look at the numbers 30 days after both are live.

| Question | Where the answer is | What good looks like |
|---|---|---|
| Did anyone find the book | KDP Reports, units sold and KENP | any unit that is not us |
| Did anyone find the packs | Etsy Stats, visits and orders per listing | any order, and which of the three framings got it |
| Which framing works | Etsy visits per listing, L1 vs L2/L3 vs L4/L5 | one of completeness, room, or life event pulling clear |
| Is the price wrong | Etsy favourites with no orders | many favourites and no orders means price; no favourites means the images |
| Did it move the constraint | `GOALS.md` O1 | a marketplace is a second front door, and this is the first time there has been one |

**The honest prior:** two new listings with no reviews, no history and no
ranking usually sell nothing in month one. That is not a reason to skip it. It
is a reason to publish now rather than in December, because both platforms rank
partly on age and history, and neither starts accruing until the listing
exists.

---

## 5. What is still missing

Ranked by how much it would change the outcome.

1. **A photograph of the cards printed and cut.** The single highest-value
   thing on this list. Print one pack, cut it, photograph it on a table. Every
   Etsy listing improves the same day, and the current images are rendered
   pages doing an honest but weaker job.
2. **The print geometry fix upstream in `ops/build_catalog.py`.** The site
   currently delivers the 152-page version of the Whole House pack, half of it
   near-empty pages, to anyone who buys it there. That is a live customer-facing
   defect and it is now fixed only in the marketplace path.
3. **epubcheck.** Installing a JRE and epubcheck would turn the largest
   UNVERIFIED item in section 1 into a measurement.
4. **A second look at price once there is evidence.** The trigger is written
   down in 2.6 so it does not get argued from scratch.

---

## 6. Files

| Path | What it is |
|---|---|
| `build/listings/kdp/fields.json` | Every KDP form field as data |
| `build/listings/kdp/description.html` | The description, one line, ready to paste |
| `build/listings/kdp/cover-kdp.jpg` | The cover to upload |
| `build/listings/check_kdp.py` | Checks all of the above against the rules and the real files |
| `build/listings/verify_epub.py` | Structural pre-flight on the EPUB, and a list of what it cannot check |
| `build/listings/build_kdp_cover.py` | Makes the KDP cover from the site cover |
| `build/listings/amazon_suggest.py` | Amazon's own Kindle autocomplete, the evidence behind the keywords |
| `build/listings/amazon_nodes.py` | Walks the live Kindle browse tree, the evidence behind the categories |
| `build/listings/etsy-listings.json` | The five listings as data |
| `build/listings/build_etsy_assets.py` | Renders and measures the Etsy deliverables and listing images |
| `build/listings/print_fix.css` | The print geometry fix, with the reasoning |
| `build/listings/print-instructions.html` | The one-page printing guide included in every listing |
| `build/listings/check_etsy.py` | Checks the listings against the limits and the real files |
| `build/listings/verify_zone_claims.py` | Prints the zones each pack really contains, so no description can name one it does not have |
| `build/listings/etsy_economics.py` | Fee arithmetic, refuses to run without real rates |
| `build/listings/etsy/<slug>/files/` | What the buyer downloads |
| `build/listings/etsy/<slug>/listing-images/` | What the shopper sees |

To rebuild everything and re-check it:

```
python build/listings/build_etsy_assets.py
python build/listings/verify_epub.py
python build/listings/build_kdp_cover.py
python build/listings/check_kdp.py
python build/listings/check_etsy.py
python build/listings/verify_zone_claims.py
```

All of them pass with zero failures as of 2026-09-03. `verify_zone_claims.py`
prints rather than passes or fails: read its output against the copy.

**It has already earned its place.** The first draft of the Kitchen description
named a "small appliance zone". The pack does not have one; it has a utensil
and utility drawer zone. The first draft of the Holiday Hosting description
said it covered "the rooms people sit in and the rooms food comes out of". It
covers neither: it is the guest bedroom, the guest bathroom, the dining room
and one entryway zone. Both were caught by reading the finished PDF rather than
the product name, and both are corrected above.
