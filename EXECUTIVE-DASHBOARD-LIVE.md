# 6S Success: Live Executive Dashboard

> Generated 2026-09-08 08:56 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 2 P0 items still open. |
| **Revenue this month** | **$0 of $20,000 target (0.0%)** |
| | `............................` |
| **Paying customers** | 0 |
| **Email list** | 0 |
| **Can the site take money?** | yes, confirmed live, 158 of 159 catalog items |

### The one constraint

PRODUCTION IS SERVING AN OLD BUILD. The live site can take money, and every payment link it serves is active in Stripe, but it is running a build from before most of this work existed. Waiting behind that deploy: 158 of 159 catalogue items in this repository are buyable, each a live Stripe Payment Link or a real free download. One deploy moves all of it to the customer.

---

## Where the work stands

| Stream | State |
|---|---|
| Open issues | 8 (2 P0, 2 blocked on art, 6 need your call) |
| Closed to date | 23 |
| Commits (7 days) | 428 of 1130 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `93725f29` Merge cloud routine commits |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 193 pages, 0 dead links, 4/4 legal pages, 190 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 9/114 zones covered (card art lives outside the repo) |
| Entryway deck | 89 cards render clean from the template layer; the gallery publishes 72 of them |
| Zone imagery | 107/114 zone pages carry a reviewed picture (BUILT, NOT DEPLOYED) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~4,408 ready-to-publish units, unused |
| Video | 0/114 episodes shot |
| Zone reset videos | 114/114 short zone-reset videos, rendered, not posted anywhere yet |
| Zone reset videos, photo-led | 2/107 eligible photo-led zone-reset videos, rendered, not posted anywhere yet |
| Zone reset videos, 16:9 for YouTube | 114/114 horizontal zone-reset videos for YouTube, rendered, not posted anywhere yet |
| Zone reset videos, narrated | 114/114 narrated zone-reset videos with real voice, rendered, not posted anywhere yet |
| Social cards, Pinterest and Instagram | 114/114 zones, Pinterest and Instagram cards ready, not posted anywhere yet |
| YouTube upload text | 114/114 zones, title/description/tags written, not posted anywhere yet |
| YouTube thumbnails | 114/114 zones, YouTube thumbnail designed and ready |

## What needs you

- **Redeploy the site.** Production is serving an older build: 1 of 9 assets on the live homepage differ from this repository, and no zone page carries its photograph yet. The image is built and pushed to ghcr.io; the Redeploy button in Hostinger is the only step left. Until then 107 reviewed pictures and every fix since the last deploy reach nobody.
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
