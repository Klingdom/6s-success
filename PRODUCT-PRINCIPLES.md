# 6S Success Product Principles

> The checklist a product idea has to pass before it enters `PRODUCT-CATALOG.md`. Required by `CLAUDE.md` section 56. Written 2026-08-24. Where this file and the catalog disagree, this file describes what should be true and the catalog should be corrected to match it.

## 1. Purpose

`PRODUCT-CATALOG.md` describes the commercial architecture: what products exist, what they cost, what they map to. `PRODUCT-PRINCIPLES.md` describes the test a candidate product has to pass before it is allowed onto that list at all. It exists because "should we build this" and "how does this fit the catalog" are different questions, and the second one has repeatedly been answered before the first one was asked.

## 2. The test

A product idea passes only if all of the following are true.

1. **It follows Diagnose, then Recommend, then Explain, then Offer**, never Interrupt, then Pressure, then Sell. See `CLAUDE.md` section 12.
2. **It maps to a real customer job or root cause**, stated as: recommended because [desired outcome / root cause / constraint]. If the connection between the problem and the product cannot be stated in one sentence, the product is not ready to be offered.
3. **It can actually be delivered if somebody pays today.** Never list a product whose fulfillment path does not exist yet. A prototype, beta, preorder, or concept must be labelled as exactly that, not dressed as a finished offer.
4. **It does not duplicate an existing digital asset with a bigger price tag on it.** The Complete Digital Bundle already contains every digital asset that exists; a new digital tier priced above it would be the same files with new packaging, not new value. See `ROADMAP-2026-2029.md` section 1.
5. **It is not gated if it is currently advertised as free.** A visitor who was told something is free must not later find it behind a paywall.
6. **Its evidence is honestly labelled.** No fabricated testimonial, review, rating, customer count, scarcity claim, or discount, ever, on any product page. If demand, performance, or popularity is unknown, the page says so rather than implying otherwise.
7. **Its economics are stated as what they are.** Gross revenue is not profit. A product's price should be traceable to `ops/revenue_model.py` or an equivalent honest calculation, not to a round number that felt right.

## 3. What currently fails the test, and why it is not on the catalog

- **A $99 digital tier.** Fails principle 4. The $49 bundle already contains every digital asset that exists.
- **A subscription product.** Fails principle 2 as currently understood: no evidence exists that anybody wants recurring value from a tool meant to finish a house once, and the volume of visitors it would need does not exist either. Revisit only with new evidence.
- **A second illustrated card deck.** Fails principle 2 in a specific way: the free Entryway deck exists to produce evidence about whether decks convert at all, and it has not produced any yet. Building a second one before reading the first one's result is building on a guess rather than a measurement.
- **The Kids Bedroom chapter 39 printables the QR codes promise.** Fails principle 3 today. The printables the artwork points to do not exist, so the plates that carry those QR codes are not published. See issue #19; the honest state is recorded there rather than shipped anyway.

## 4. How this connects to the funnel, not just the page

A product that passes every principle above can still be premature if nothing has established that a stranger will buy anything at all. `ROADMAP-2026-2029.md` section 1 states this plainly: the catalogue is not short of products, it is short of visitors, and epic 5 of `BACKLOG-2026-H2.md` does not start until epic 1 (measurement) has answered whether the funnel converts anyone who was not personally referred by Phil.

## 5. Read with

- `PRODUCT-CATALOG.md`, the structural catalog this file gates entry to
- `CLAUDE.md`, sections 3, 6, 8, 12, 48, 49
- `ROADMAP-2026-2029.md`, section 1 (the arithmetic) and section 4 (what the plan refuses to do)
- `BACKLOG-2026-H2.md`, "what is deliberately not in this backlog"
- `DECISIONS.md`, for any product decision recorded against these principles
