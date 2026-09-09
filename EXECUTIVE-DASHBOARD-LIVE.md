# 6S Success: Live Executive Dashboard

> Generated 2026-09-09 14:03 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 2 P0 items still open. |
| **Revenue this month** | **not measured, no Stripe credential in this environment** |
| | `............................` |
| **Paying customers** | not measured |
| **Email list** | 0 |
| **Can the site take money?** | repository says yes (158 of 159 catalog items), **unconfirmed on the live site**: no Stripe credential in this environment to check the links a visitor actually hits |

### The one constraint

The site can take money for 158 of 159 catalog items, each a live Stripe Payment Link or a real free download. Still not buyable: Corporate Lean 6S. All 190 forms still hand off to email by hand instead of capturing a list. Whether 6s-success.com reaches the site could not be checked from this run's network, so treat public reachability as unverified, not confirmed. The widened catalog has not moved revenue because almost nobody is arriving at the site yet. Discovery, not what can be bought, is the constraint now.

---

## Where the work stands

| Stream | State |
|---|---|
| Traffic | **not measured** (no ssh key at /root/.ssh/6s_deploy, so the database was not reached). No number here means nobody looked, not that nobody came. |
| Open issues | 8 (2 P0, 2 blocked on art, 6 need your call) |
| Closed to date | 23 |
| Commits (7 days) | 455 of 1201 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `b98cd2a7` Record CI confirmation for the media_capability cost-sort fi |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 193 pages, 0 dead links, 4/4 legal pages, 190 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 9/114 zones covered (card art lives outside the repo) |
| Entryway deck | print PDF already built and shipped (72 cards); local render cache empty here, so 0 is not a regression |
| Zone imagery | 107/114 zone pages carry a reviewed picture (deployment unknown) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~4,408 ready-to-publish units, unused |
| Video | 0/114 episodes shot |
| Zone reset videos | 0/114, not yet rendered |
| Zone reset videos, photo-led | 0/107 eligible, not yet rendered |
| Zone reset videos, 16:9 for YouTube | 0/114, not yet rendered |
| Zone reset videos, narrated | 0/114, not yet rendered |
| Social cards, Pinterest and Instagram | 114/114 zones, Pinterest and Instagram cards ready, not posted anywhere yet |
| YouTube upload text | 114/114 zones, title/description/tags written, not posted anywhere yet |
| YouTube thumbnails | 114/114 zones, YouTube thumbnail designed and ready |

## What needs you

- **#31** Decide: the deck gallery and the deck download are two different card designs
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#20** Decide: how the card decks get sold, and what unblocks the paid tier
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands
- **#7** Decide: keep or discard the 2,786-card master plan

## Open issues

| # | Title | Labels |
|---|---|---|
| 31 | Decide: the deck gallery and the deck download are two different card designs | decision |
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely | blocked-on-art |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 20 | Decide: how the card decks get sold, and what unblocks the paid tier | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 7 | Decide: keep or discard the 2,786-card master plan | decision |
| 2 | Regenerate 12 remaining stale card images | P0, blocked-on-art |
