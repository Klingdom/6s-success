# 6S Success: Live Executive Dashboard

> Generated 2026-08-31 17:54 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **RED** Live payment links were last confirmed deactivated in Stripe on 2026-08-31 11:26; this run has no Stripe credential to reverify, so treat the outage as still open until a session with real access says otherwise. |
| **Revenue this month** | **$19 of $20,000 target (0.1%), carried forward from 2026-08-31 11:26 because this run could not reach Stripe** |
| | `............................` |
| **Paying customers** | 1 |
| **Email list** | 0 |
| **Can the site take money?** | **NO**, live payment links are deactivated in Stripe (last confirmed 2026-08-31 11:26, not reverified this run: no Stripe credential here) |

### The one constraint

PRODUCTION CANNOT TAKE MONEY. Every payment link the live site serves is deactivated in Stripe, so anybody clicking buy reaches a dead link. The repository's links are all active, so redeploying fixes it. Last confirmed 2026-08-31 11:26; this run has no Stripe credential to reverify, so this is not new information, only a reminder that nothing has cleared it. Waiting behind that deploy: 158 of 159 catalogue items in this repository are buyable, each a live Stripe Payment Link or a real free download. Nothing else about the business matters until this one button is pressed. Whether 6s-success.com reaches the site could not be checked from this run's network, so treat public reachability as unverified, not confirmed.

---

## Where the work stands

| Stream | State |
|---|---|
| Open issues | **UNKNOWN** (GitHub unreachable at generation time) |
| Closed to date | UNKNOWN |
| Commits (7 days) | 394 of 653 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `cad4747f` Claim 5B.2 before starting it |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 190 pages, 0 dead links, 4/4 legal pages, 187 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 9/114 zones covered (card art lives outside the repo) |
| Entryway deck | print PDF already built and shipped (72 cards); local render cache empty here, so 0 is not a regression |
| Zone imagery | 110/114 zone pages carry a reviewed picture (BUILT, NOT DEPLOYED) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~2,600 ready-to-publish units, unused |
| Video | 0/114 episodes shot |

## What needs you

- **Redeploy the site.** Production is serving an older build: 7 of 9 assets on the live homepage differ from this repository, and no zone page carries its photograph yet. The image is built and pushed to ghcr.io; the Redeploy button in Hostinger is the only step left. Until then 110 reviewed pictures and every fix since the last deploy reach nobody.
- **UNKNOWN.** GitHub could not be reached when this was generated, so the
  decision queue could not be read. That is not the same as nothing being
  blocked. Re-run `python ops/dashboard.py` once GitHub responds.

## Open issues

| # | Title | Labels |
|---|---|---|
