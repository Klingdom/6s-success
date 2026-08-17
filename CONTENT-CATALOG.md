# 6S Success Content Catalog

> Authoritative inventory of what 6S Success has actually produced: which assets exist, in what state, where they live, what is published, and what is finished but unshipped. Counts are measured, not estimated.

## 1. Purpose

`CONTENT-CATALOG.md` is the answer to a question that keeps being answered from memory:

> What do we actually have?

`BUSINESS.md` describes the content model. `PRODUCT-CATALOG.md` describes the commercial architecture. Neither is an inventory, and both explicitly defer to this file.

The distinction that matters most here is between **authored** and **published**. Almost everything 6S Success owns is authored. Almost nothing is published, and nothing at all is purchasable.

Read with:

- `CLAUDE.md`
- `PRODUCT-CATALOG.md` for how content becomes a commercial offer
- `CONTENT-STANDARDS.md` for the rules everything below must satisfy
- `BUSINESS.md` for the content model
- `EXECUTIVE-DASHBOARD-LIVE.md` for the current measured counts
- `RISKS.md`
- `ROADMAP.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Core Rule

**Authored is not published. Published is not purchasable.**

An asset counts as `PUBLISHED` only if a member of the public can reach it without asking. It counts as `PURCHASABLE` only if they can pay for it and receive it.

Today: nine content lines exist, one is published, and zero are purchasable.

Do not describe this catalog as a product line until that changes.

---

# 3. Asset State Vocabulary

| State | Meaning |
|---|---|
| `DRAFT` | Exists, not reviewed |
| `AUTHORED` | Complete and internally reviewed, not released |
| `PUBLISHED` | Publicly reachable |
| `PURCHASABLE` | Publicly reachable and payable |
| `BLOCKED` | Complete but held by a named blocker |
| `PLANNED` | Specified, no asset exists |

Never mark something `PUBLISHED` because it is finished. Check that it is reachable.

---

# 4. The Spine

Every line below descends from one structure:

**20 rooms → 114 micro zones**

The rooms and zones are defined in the Micro Zone Manual source at `content/manual/source/content.json`, which `ops/dashboard.py` reads directly. Any product that invents its own room list has drifted, and the manual is the arbiter.

Coverage of the spine is the honest measure of completeness for every line:

| Line | Zone coverage |
|---|---|
| Book | 114 of 114 (all 20 rooms have a Part 9 chapter) |
| Field manual | 114 of 114 |
| Card decks | 9 of 114 |
| Video | 0 of 114 shot, 114 planned |
| App | UNKNOWN, the prototype is not shipped |

---

# 5. Inventory Summary

Verified 2026-08-17.

| # | Line | State | Scale | Purchasable |
|---|---|---|---|---|
| 1 | Book, 6S Success Home Edition | AUTHORED | 50 chapters | No |
| 2 | Micro Zone Field Manual | AUTHORED | v3, 20 rooms, 114 zones | No |
| 3 | Product appendix | AUTHORED | 123 product types | No |
| 4 | Card decks | BLOCKED | 2 of 20 rooms | No |
| 5 | Board games | DRAFT | 3 concepts | No |
| 6 | App, 6S Home Reset | DRAFT | PWA prototype | No |
| 7 | Video series | PLANNED | 114 episodes, 0 shot | No |
| 8 | Social corpus | AUTHORED | roughly 2,600 units | No |
| 9 | Website | PUBLISHED | 14 pages | No |

---

# 6. Line 1: The Book

**6S Success: Home Edition.** State: `AUTHORED`. Complete.

| Fact | Value |
|---|---|
| Chapters | 50 of 50 |
| Chapters carrying the safety notice | 50 of 50 |
| Chapters with no photographs | 13 |
| Front matter | Drafted, bracketed fields unfilled |
| Source | `content/book/6S-Success-Chapter-1` through `-50` |
| Master | Desktop master path read by `ops/dashboard.py` |
| Published artifact | `site/downloads/6S Success Home Edition - Complete Book.html` |
| Second artifact | The same title as PDF, 53 MB |

Structure: Chapters 1 to 30 are the method, running the full six S arc. Chapter 31 onward is Part 9, one room playbook per room, instruction centric, ending at Chapter 50, the patio or deck.

**Defect, open.** The published HTML download ends at Chapter 30. It is offered as the complete book and contains 60 percent of it. The PDF beside it needs the same check. See `RISK-0004`.

**Defect, open.** 13 chapters have no photographs. The Part 9 illustration stream is untouched.

---

# 7. Line 2: The Micro Zone Field Manual

**6S Home Micro Zone SOP Field Manual, v3.** State: `AUTHORED`.

| Fact | Value |
|---|---|
| Rooms | 20 |
| Micro zones | 114 |
| Location | `content/manual/` |
| Source of truth | `content/manual/source/content.json` |
| Appendices | Appendix A, the complete 6S home kit; Appendix B, inputs and sourcing |
| Build pipeline | `extract.py`, `merge_shine.py`, `build.py`, `validate.py` |
| Superseded | v2, retained at `content/book/6S Home Micro Zone SOP Field Manual v2.html` |

This is the companion volume and, structurally, the most important asset in the catalog. It defines the spine every other line inherits. It is not published anywhere.

---

# 8. Line 3: The Product Appendix

**The Complete 6S Home Product List.** State: `AUTHORED`.

| Fact | Value |
|---|---|
| Product types | 123 |
| Format | CSV and HTML, `content/appendix/` |
| Fields | ID, family, category, standard name, purpose, supported 6S phases, rooms, level, quantity, unit, retail low, retail high, safety notes, zone count |

Entries are **product types**, never brands. "Adjustable Wall Track System", not a manufacturer's model. That rule is deliberate, it keeps the book durable, and it is why the book cannot carry affiliate links.

Retail low and high are estimates. Treat them as a planning range, not as pricing.

---

# 9. Line 4: The Card Decks

State: `BLOCKED`. Two of a planned twenty rooms.

| Fact | Value |
|---|---|
| Decks with assets | 2, Entryway and Mud Room |
| Zone coverage | 9 of 114 |
| Card images | 91 |
| Architecture | v3, three tier, image forward, trading card 5:7 |
| Location | `content/decks/`, masters on the Desktop deck path |

**Blocked by art.** GitHub issue #1 (P0): cards EE-001 and EP-005 contain Amazon trademarks. Issue #2 (P0): 16 further stale images await regeneration. See `RISK-0003`. No deck should be printed or sold before that is resolved and professionally reviewed.

**Open decision.** GitHub issue #7 asks whether to keep or discard the 2,786 card master plan. Until it is answered, deck scope is UNKNOWN and building deck 3 is premature.

---

# 10. Line 5: The Board Games

State: `DRAFT`. Three games, no playtesting on record.

| Game | Assets |
|---|---|
| Six S: The Home Reset | Concept, print and play prototype, sell sheet |
| Micro Zone | Concept, print and play prototype, sell sheet |
| The 15-Minute Reset | Concept, print and play prototype, sell sheet |

Location: `content/games/`. The stated approach in the concept document is to validate small, then build the flagship.

**Zero recorded playtests.** A board game that has not been played by anyone outside the household is a document, not a game. `content/games/deliverables/` holds only a placeholder file.

---

# 11. Line 6: The App

**6S Home Reset.** State: `DRAFT`, unshipped.

| Asset | Location |
|---|---|
| Product specification and store release plan | `content/app-spec/` |
| PWA prototype, verified running on device | `content/app-mvp/app/` |
| PRFAQ, store listing draft, one pager | `content/app-mvp/` |
| On device LLM integration plan | `content/app-mvp/` |

This is the only line that could deliver the per household personalization that `PRODUCT-CATALOG.md` describes, and the only one that would introduce a runtime. See `ARCHITECTURE.md` section 12.

The PRFAQ names a launch date. Treat it as an intention, not a commitment. Nothing has been submitted to any store.

---

# 12. Line 7: The Video Series

State: `PLANNED`.

| Fact | Value |
|---|---|
| Episodes planned | 114, one per micro zone |
| Episodes shot | 0 |
| Production plan | `content/video/` |
| Tracker | `content/video/6S-Micro-Zone-Reset-tracker.csv` |
| Short form distribution plan | `content/video/6S_SHORT_FORMAT_DISTRIBUTION_PLAN.md` |
| Pilot and media package | `content/video/pilot/`, `media-package-entryway/` |

This is the largest gap between planning and production in the catalog. It should not start until something exists to send viewers to.

---

# 13. Line 8: The Social Corpus

State: `AUTHORED`, unused.

Roughly 2,600 ready to publish units exist across the chapter packages, the LinkedIn strategy, the posting plan, and the per deck card posts.

**Note on this number.** `ops/dashboard.py` reports 2,600 as a hardcoded constant, not a count of files. The same applies to the video figures and to zone deck coverage. The dashboard is honest about most things but these four values are typed in. Replacing them with real counts is a small, worthwhile fix.

Publishing this corpus while every form is disconnected and checkout is staged converts attention into nothing. See `RISK-0012`.

---

# 14. Line 9: The Website

State: `PUBLISHED`. The only line the public can reach.

| Fact | Value |
|---|---|
| Pages | 14 |
| Dead links | 0 |
| Legal pages | 4 of 4: privacy, terms, accessibility, disclaimer |
| Disconnected form handlers | 14 |
| Downloads offered | 2, the book HTML and PDF |
| Location | `site/` |

Page inventory: index, about, method, book, shop, cart, consulting, resources, invest, contact, privacy, terms, accessibility, disclaimer.

See `ARCHITECTURE.md` for how it is served.

---

# 15. Business And Planning Documents

Not a content line, but held in the same tree and often mistaken for product:

- company and brand six pager, with the pricing ladder
- Home Quest game six pager
- Boise combination warehouse, showroom, and service center concept
- two person crew service plan

Location: `content/decks/`. These are internal planning artifacts. They are not customer facing and should never be published as such.

---

# 16. What Is Not In This Catalog

Named honestly, because their absence is the business problem:

- no lead magnet
- no email sequence
- no sales page for any individual product
- no sample chapter or free excerpt separate from the full download
- no pricing published anywhere a customer can act on
- no customer facing FAQ tied to a purchase
- no fulfillment process for a digital purchase

Every item above is smaller than any line in section 5, and any one of them is worth more today than another authored chapter.

---

# 17. Reconciliation

The live site and the running product folders are authoritative for what is actually available. This file describes what is known to exist.

Reconcile:

- after any publish or deploy
- after any product line changes state
- whenever `ops/dashboard.py` counts disagree with this file

When they disagree, the measured count wins and this file is corrected. Never edit the dashboard to match this file.

---

# 18. Canon Checks For Any New Asset

Before adding anything to this catalog, confirm it satisfies `CONTENT-STANDARDS.md`:

1. zero em dashes and zero en dashes
2. "Straighten", never the rejected term
3. Safety is the fourth S
4. product types, never brands
5. the safety notice is present where the asset instructs physical work
6. rooms and zones match `content/manual/source/content.json`

An asset that fails any of these is `DRAFT`, whatever its author believed.

---

# 19. Final Principle

This catalog documents an unusual failure mode: not too little work, but too much of it in the wrong state.

Nine lines. Fifty chapters. A hundred and fourteen zones. A hundred and twenty three product types. Roughly 2,600 social units. Zero dollars.

The correct response to that is not a tenth line.

The next asset that matters is whichever one closes the gap between `AUTHORED` and `PURCHASABLE` for a single product. See `ROADMAP.md`.
