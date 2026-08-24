# Product backlog, September to December 2026

Written 2026-08-24. Supersedes the queue content in `BACKLOG.md`, which is a
process document describing states and schemas rather than a list of work.

**How to read this.** Ordered by the sequence work actually has to happen in, not
by how appealing it is. Every item has an acceptance criterion that can be
checked by running something or fetching something, because "done" is otherwise
an opinion. Estimates are in operator sessions, where a session is a few hours
of focused work, and they are guesses.

**The rule that orders everything below:** nothing that improves conversion
matters until something can be measured, and nothing that adds product matters
until a stranger has bought something. So measurement comes first, then traffic,
then conversion, then product.

---

## EPIC 1: See what is happening (blocks everything)

Four experiments are designed, instrumented, and completely unreadable. This is
the only epic where every item is cheap and every item is blocking.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 1.1 | **Umami read access** | `ops/` can fetch visitor counts without a browser login | 0.2 | **Phil**, 3 clicks |
| 1.2 | Wire the share URL or API key into the dashboard | `python ops/dashboard.py` prints real visitors, not "not measured" | 0.5 | operator |
| 1.3 | Answer EXP-001: has a stranger ever clicked a buy button | a number in `ops/experiments.json`, `observed_daily_visitors` no longer null | 0.5 | operator |
| 1.4 | Answer EXP-002: does anyone reach the offer at the bottom of a zone page | scroll depth distribution recorded for 30 days | 0.3 | operator |
| 1.5 | Search Console: first impression data | 30 days of impressions exported and read | 0.5 | operator |

**1.1 is the single highest value item in this document.** Everything in epics 3
and 4 is guesswork until it lands.

---

## EPIC 2: Fix what is broken or dishonest

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 2.1 | **Listmonk sending identity** (issue #15) | a 6S signup receives mail branded 6S Success, not Compassion Benchmark | 1.0 | Phil decides, operator builds |
| 2.2 | Restore the signup form | `python ops/wire_signup.py` re-run, form live on 6 pages | 0.2 | operator |
| 2.3 | ~~Sitemap lastmod stamps every URL with today (issue #23)~~ | `sitemap.xml` shows real per-page modification dates | 0.5 | **done 2026-08-24** |
| 2.4 | Chapter 39 promises printables that do not exist (issue #19) | either the printables exist or the promise is removed | 1.0 | operator |
| 2.5 | Chapter 47 plates are monochrome (issue #18) | Phil decides regenerate or accept | 0.2 | **Phil** |
| 2.6 | Kitchen safety pass never mentions gas (issue #16) | gas hazard present in the Kitchen zone data, or a recorded reason it is not | 0.5 | operator |
| 2.7 | Card art carries Amazon trademarks (issues #1, #2) | 18 images regenerated without third party marks | 2.0 | blocked on image generation |

2.1 is a real blocker with a real cost: the list is the only asset that
compounds, and six of seven prospects have already been lost with no way to
reach them.

---

## EPIC 3: Traffic (the constraint, and it is slow)

Nova has no list. Search is the only durable route and it takes 12 to 18 months.
Everything here is planting, not harvesting.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 3.1 | Publish the ten LinkedIn posts | posted, and referral traffic visible in analytics | 0.2 | **Phil** |
| 3.2 | Daily LinkedIn drafts keep running | already automated, 8am Denver | done | automated |
| 3.3 | The nine tier-0 images | 9 files in `content/images/intake/`, wired into 3 zone pages | 1.0 | **Phil** generates, operator wires |
| 3.4 | Measure whether images change anything | before/after comparison on those 3 pages after 30 days | 0.3 | operator, needs 1.1 |
| 3.5 | Second wave of images if 3.4 is positive | 30 more images live | 3.0 | conditional on 3.4 |
| 3.6 | ~~Internal link depth audit~~ | every zone page reachable in 3 clicks from home | 0.5 | **done 2026-08-24** |
| 3.7 | Article expansion, only on measured queries | new articles written against real Search Console queries, never invented ones | 2.0 | needs 1.5 |
| 3.8 | Directory and citation listings, only legitimate ones | listed where a real human would look for this | 1.0 | operator |

**3.7 is deliberately blocked on 1.5.** Writing articles against guessed queries
is how a content site accumulates pages nobody searches for.

---

## EPIC 4: Conversion (do not start before epic 1)

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 4.1 | EXP-003: free artifact first vs method first | powered sample reached or 6 weeks elapsed, result recorded either way | 1.0 | needs traffic |
| 4.2 | Offer placement, if EXP-002 shows nobody scrolls | offer moved, measured, kept or reverted | 0.5 | conditional |
| 4.3 | Post-purchase sequence | a buyer receives a second useful email, not a pitch | 1.0 | needs 2.1 |
| 4.4 | Cart abandonment: there is no cart | decide whether checkout sessions can be recovered at all | 0.3 | operator |

---

## EPIC 5: Product (last, on purpose)

The catalogue is not short of products. It is short of visitors. Nothing here
starts before epic 1 answers whether the funnel works.

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 5.1 | Decide how card decks get sold (issue #20) | a decision recorded in `DECISIONS.md` | 0.3 | **Phil** |
| 5.2 | Quest: does anybody finish a second card (EXP-004) | retention number known | 0.3 | needs 1.1 |
| 5.3 | Native app wrapper | only if 5.2 shows real retention | 3.0 | conditional |
| 5.4 | Workplace and professional edition | only if horizon 2 bet B is chosen | 5.0 | conditional, 2028 |
| 5.5 | Corporate Lean 6S: quote flow already works | verified 2026-08-23 | done | done |

---

## EPIC 6: Keep the operation honest

| # | Item | Accept when | Est | Owner |
|---|---|---|---|---|
| 6.1 | Inbox agent runs on schedule | owner replies become work items within an hour | 0.3 | operator |
| 6.2 | Two agents writing one repo keeps causing conflicts | a rule that prevents it, recorded | 0.3 | operator |
| 6.3 | Monthly roadmap review against measured numbers | `ROADMAP-2026-2029.md` reviewed, guesses struck when measured | 0.2/mo | operator |
| 6.4 | 15 referenced control documents do not exist (issue #9) | either created or the references removed | 1.0 | operator |
| 6.5 | Two documents both named EXECUTIVE-DASHBOARD (issue #8) | one canonical | 0.2 | operator |

---

## What is deliberately not in this backlog

- **A $99 digital tier.** The $49 bundle already contains every digital asset
  that exists. It would be the same files with a bigger number on them.
- **Paid acquisition.** Buying traffic into a funnel that has never converted a
  stranger converts money into noise.
- **A second illustrated deck.** The free Entryway deck exists to produce
  evidence first. It has not produced any yet.
- **A subscription.** Needs the same impossible volume, plus accounts and a
  backend that do not exist, and there is no evidence anybody wants recurring
  value from a tool for finishing your house once.
- **Publishing `the_call` and `watch_for` as standalone pages.** Proposed and
  rejected on 2026-08-24: that content already ships as FAQPage questions on the
  canonical zone pages, so it would be 114 pages competing with themselves.

## Items waiting on Phil, consolidated

1. **Umami share URL** (1.1). Three clicks. Unblocks five items.
2. **Listmonk sending identity** (2.1). Decide: separate instance, or change the
   global from-address and accept the cost to the other brand.
3. **Publish the ten LinkedIn posts** (3.1). Already written and in his inbox.
4. **Generate the nine tier-0 images** (3.3). Prompts ready.
5. **Chapter 47 monochrome plates** (2.5), **card deck sales model** (5.1).
