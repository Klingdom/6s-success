# 6S Success Roadmap

> Dependency ordered sequence of what 6S Success builds next and why nothing may jump the queue. Ordered by constraint, not by date, and not by enthusiasm.

## 1. Purpose

`BACKLOG.md` decides what to do next week. `ROADMAP.md` decides what order the large things come in, and refuses the ones that arrive out of order.

It answers:

- What is the business trying to become able to do?
- What must be true before each step is even attempted?
- What is deliberately not being worked on, and why?
- What would change the order?

Read with:

- `CLAUDE.md`
- `STRATEGY.md` for how the business intends to win
- `BACKLOG.md` for execution
- `RISKS.md`, which supplies most of the sequencing logic
- `CONTENT-CATALOG.md` for what already exists
- `EXECUTIVE-DASHBOARD-LIVE.md` for the current measured state
- `DECISIONS.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Prime Sequencing Rule

**Work the constraint, then re measure.**

The live dashboard names one constraint:

> The business cannot accept money. Checkout is staged, forms are disconnected, and the email list is empty, so every visitor is lost permanently.

Until that is false, every phase below that does not move it is a distraction, however finished, however satisfying, and however close to done it feels.

The catalog is not the problem. Nine authored content lines exist. Zero are purchasable.

---

# 3. No Dates

This roadmap carries no dates and no estimates.

The reason is specific rather than evasive: there is no throughput history to estimate from. Sixteen commits exist in total, the operating cadence is UNKNOWN, and no phase below has been attempted before.

What would establish a schedule: complete Phase 1, measure how long it actually took, and estimate the rest from that. Estimating before then produces a number that feels like a commitment and is not one.

Phases are ordered. They are not scheduled.

---

# 4. Phase Format

Each phase states:

- **Goal**, in one sentence
- **Why here**, the dependency that fixes its position
- **Entry condition**, what must be true to start
- **Work**, the substantive items
- **Exit condition**, the observable event that completes it

A phase is complete only when its exit condition is verified. Not when the work feels done.

---

# 5. Phase Overview

| Phase | Goal | State |
|---|---|---|
| 0 | Restore the ability to deploy | Not started |
| 1 | Sell one product | Not started |
| 2 | Keep the people who arrive | Not started |
| 3 | Decide whether anything is measured | Not started |
| 4 | Send demand at the thing that can be bought | Not started |
| 5 | Second product line | Blocked |
| 6 | Everything else | Parked |
| A | Enabling work, runs alongside | Not started |

---

# 6. Phase 0: Restore The Ability To Deploy

**Goal.** Make it possible to ship a change to production at all.

**Why here.** Every later phase ends in a deploy. The repository went private on 2026-08-16 and the VPS has no read access, so the next deploy and the next rollback will both fail on authentication. The running container hides this until the moment it matters. See `RISK-0002`.

**Entry condition.** None. This is the floor.

**Work.**

1. Give the VPS read access: a deploy key registered on the repository, or a fine grained read only Contents token in the HTTPS clone URL. GitHub issue #10, P0.
2. Prove it with a pull that is expected to succeed.
3. Establish which compose file is actually running, `docker-compose.yml` or `docker-compose.proxy.yml`, and record it in `SYSTEM-REGISTRY.md`.
4. Record the running image digest, so "what is live" has an answer.

**Exit condition.** A change is deployed to 6s-success.com and verified live, and its image digest is recorded.

This phase is small. It is first because everything downstream is worthless while it is false.

---

# 7. Phase 1: Sell One Product

**Goal.** One product, one payment path, one completed transaction.

**Why here.** It is the named constraint. Revenue is $0 against a $20,000 monthly target, and no amount of content changes that while the path does not exist.

**Entry condition.** Phase 0 complete.

**Work, in order.**

1. **Choose the product.** The book is the obvious candidate: complete at 50 chapters, already has a page, already has a download.
2. **Fix what makes it unsellable.** The published download contains chapters 1 to 30 of 50 and is described as complete. Rebuild both the HTML and the 53 MB PDF from the full manuscript and verify Chapter 50 is present. See `RISK-0004`.
3. **Resolve the front matter.** Bracketed placeholder fields are unfilled and professional review has not happened. GitHub issue #3, P0. This is an owner decision and cannot be completed autonomously.
4. **Choose the payment approach.** A hosted checkout the static site links out to preserves the architecture. A server side component does not. Both are legitimate; the choice is a RED decision under `AUTONOMY.md` and belongs in `DECISIONS.md`. See `ARCHITECTURE.md` section 13.
5. **Connect it for exactly one product.** Resist connecting all 41 catalog items.
6. **Define fulfillment.** What the buyer receives, how, and what happens if it fails. A digital product with no delivery path is not a product.
7. **Test with a real transaction end to end.**

**Exit condition.** A real payment is received, the buyer receives the product, and both are verified outside this repository.

**Explicitly out of scope for this phase.** Pricing ladders, bundles, subscriptions, the full catalog, and any second product. One path, working, beats a store that cannot take money.

---

# 8. Phase 2: Keep The People Who Arrive

**Goal.** A visitor who is not ready to buy can be reached again.

**Why here.** After Phase 1 there is something worth sending people to. Before it, capture has nowhere to lead. It is second rather than fourth because every day without it discards attention permanently. See `RISK-0012`.

**Entry condition.** Phase 1 complete, or Phase 1 blocked on an owner decision, in which case this may run first. It is the only phase permitted to jump.

**Work.**

1. Choose an email provider. Recurring cost, therefore a recorded decision.
2. Connect one capture form. Every form on the site is currently inert.
3. Confirm a submission is received, stored, and retrievable.
4. Write one useful welcome message. Not a sequence, one message.
5. Give `site/resources.html` a capture point, since it is the destination the book now sends readers to.

**Exit condition.** A submission arrives, is stored, and the list has a verified non zero count.

---

# 9. Phase 3: Decide Whether Anything Is Measured

**Goal.** Resolve the conflict between the public privacy promise and the total absence of data.

**Why here.** Phase 4 spends effort on demand. Spending it blind is how effort disappears without a lesson. This phase is a decision, not a build, and it may take an hour.

**Entry condition.** Phase 2 complete.

**Work.**

1. Read `site/privacy.html` as the public promise it is: no analytics, no pixels, no trackers, no third party requests.
2. Decide, and record in `DECISIONS.md`, one of: keep the promise and accept that demand stays UNKNOWN, or adopt a measurement approach the privacy page can honestly describe.
3. If measuring, update the privacy page in the same change. Never quietly.
4. If not measuring, accept `RISK-0005` formally and stop treating traffic questions as answerable.

**Exit condition.** A decision exists in `DECISIONS.md`, and the site and the privacy page agree with each other.

---

# 10. Phase 4: Send Demand At The Thing That Can Be Bought

**Goal.** Get qualified attention to a product that can now be purchased.

**Why here.** Roughly 2,600 authored social units already exist. Publishing them before Phases 1 and 2 converts attention into nothing.

**Entry condition.** Phases 1 and 2 complete.

**Work.**

1. Publish from the existing corpus. Do not author more.
2. Apply the search and answer engine architecture owned by the `seo-aeo` agent to the pages that now convert.
3. Measure, subject to the Phase 3 decision.
4. Run one experiment at a time, under `EXPERIMENTS.md`.

**Exit condition.** A purchase can be traced from a published unit to a payment. If Phase 3 chose not to measure, this exit condition is UNKNOWN and the phase ends on judgment instead, which is a worse position and should be recognized as one.

---

# 11. Phase 5: Second Product Line

**Goal.** A second purchasable product.

**Why here.** Only after one line proves the whole path from attention to fulfillment.

**Entry condition.** Phase 4 complete. Plus two blockers cleared:

- card art contains third party trademarks, GitHub issues #1 and #2, `RISK-0003`, and needs professional review before any commercial distribution
- deck scope is undecided, GitHub issue #7, keep or discard the 2,786 card master plan

**Candidates, in order of readiness.**

1. **Card decks.** 2 of 20 rooms, 91 images. Blocked as above.
2. **The field manual.** Complete, 114 zones, and the structural spine of everything. Arguably the strongest product in the catalog and the least promoted.
3. **Consulting or services.** Already has a page and requires no manufacturing.

**Exit condition.** A second line takes payment.

---

# 12. Phase 6: Parked

Not being worked on. Named here so that "not yet" is a decision rather than an oversight.

| Line | State | Unparks when |
|---|---|---|
| Board games | 3 concepts, 3 print and play prototypes, 0 playtests | Someone outside the household plays one |
| App | PWA prototype, unshipped | A paying customer needs personalization the site cannot give |
| Video | 114 planned, 0 shot | There is something to send viewers to, and demand is measured |
| Boise warehouse, showroom, service center | Concept | Revenue exists at a scale that makes premises a question |
| Remaining 18 card decks | Not started | Deck 1 sells |

Parked does not mean rejected. It means the entry condition is not met, and each row states what would meet it.

---

# 13. Phase A: Enabling Work

Runs alongside the numbered phases. Small, and each one prevents a class of future loss.

| Item | Prevents | Risk |
|---|---|---|
| One external uptime check plus certificate expiry check | Silent outages nobody notices | `INCIDENTS.md` section 10 |
| A minimal CI workflow: build, link check, dash count, canon scan | Defects reaching production | `RISK-0010` |
| One verified restore onto a clean target, timed | An unrecoverable host loss | `RISK-0007` |
| A verified second copy of the product masters | Losing everything to one machine | `RISK-0011` |
| Control document sweep: dashes and the rejected term | Canon drift back into published work | `RISK-0009` |
| Replace the four hardcoded values in `ops/dashboard.py` | A dashboard that quietly reports typed in numbers | `CONTENT-CATALOG.md` section 13 |

None of these is large. Any of them can be done inside a phase without disturbing its sequence.

---

# 14. What Is Not On This Roadmap

- a tenth content line
- a redesign of the website
- a rewrite of any completed asset
- a backend, database, or framework
- expansion to a second market or language
- affiliate revenue, which the product type naming rule rules out for the book

If one of these becomes the right answer, it arrives as a `DECISIONS.md` entry with the evidence that changed the picture, not as a roadmap edit.

---

# 15. What Would Reorder This

| Trigger | Effect |
|---|---|
| A verified customer paying for something unexpected | That line moves to Phase 1 |
| A legal or safety finding | Jumps everything |
| Loss of the VPS or the masters | Phase A recovery items become first |
| Phase 1 blocked on an owner decision | Phase 2 proceeds first |
| Measured demand contradicting a phase order | Reorder, and record why in `DECISIONS.md` |

Reordering is legitimate. Reordering without recording the evidence is drift.

---

# 16. Review

Review this roadmap:

- when a phase exit condition is met
- when the constraint on the live dashboard changes
- when a `CRITICAL` risk opens or closes
- monthly at minimum

If the constraint has not moved after a full review cycle, the honest conclusion is that the work being done is not the work that matters, and the phases were not being followed.

---

# 17. Final Principle

This business has an unusual shape: extraordinary supply, no demand path, and no way to accept money.

The temptation is to add to the part that is already strong, because that part is enjoyable and the results are visible immediately.

The roadmap exists to refuse that.

Phase 0 is small. Phase 1 is uncomfortable and involves decisions only the owner can make. Everything after it becomes straightforward, and none of it works before it.
