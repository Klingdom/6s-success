# 6S Success: Live Executive Dashboard

> Generated 2026-09-22 13:50 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 2 P0 items still open. |
| **Revenue this month** | **$0 of $20,000 target (0.0%), carried forward from 2026-09-20 10:15 because this run could not reach Stripe** |
| | `............................` |
| **Paying customers** | 0 |
| **Email list** | 0 |
| **Can the site take money?** | repository says yes (137 of 138 catalog items), **unconfirmed on the live site**: no Stripe credential in this environment to check the links a visitor actually hits |

### The one constraint

PRODUCTION IS SERVING AN OLD BUILD. The live site can take money, and every payment link it serves is active in Stripe, but it is running a build from before most of this work existed. A session with real access confirmed production current at 2026-09-21T13:53:56Z (build b0b1e02558428cb1). The repository has since moved to build 3da8341e30a4d1da, not yet redeployed, so this gap is whatever changed since that confirmation, not an unknown backlog. Waiting behind that deploy: 137 of 138 catalogue items in this repository are buyable, each a live Stripe Payment Link or a real free download. One deploy moves all of it to the customer. Whether 6s-success.com reaches the site could not be checked from this run's network, so treat public reachability as unverified, not confirmed.

---

## Where the work stands

| Stream | State |
|---|---|
| Traffic | 76 visitors across 190 visits, 30 days (carried forward from 2026-09-21 14:05; this run could not measure it fresh: **not measured** (no ssh key at /root/.ssh/6s_deploy, so the database was not reached). No number here means nobody looked, not that nobody came.) |
| Affiliate | T2 not fired: 1 of 60 outbound retailer click(s) in the last 90 days, from 1 visitor(s), internal and automated excluded. No application is authorised. (carried forward from 2026-09-20 10:15; this run could not measure it fresh: T2 NOT EVALUATED: analytics unreadable (no ssh key at /root/.ssh/6s_deploy, so the database was not reached). This is not a reading of zero.) |
| Open issues | 8 (2 P0, 2 blocked on art, 6 need your call) |
| Closed to date | 26 |
| Commits (7 days) | 1197 of 3385 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `4569a46d` PM check-in nightly log entry: six-file low-mention tier fin |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 198 pages, 0 dead links, 4/4 legal pages, 194 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 9/114 zones covered (card art lives outside the repo) |
| Entryway deck | print PDF already built and shipped (72 cards); local render cache empty here, so 0 is not a regression |
| Zone imagery | 111/114 zone pages carry a reviewed picture (BUILT, NOT DEPLOYED) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~4,939 ready-to-publish units, unused |
| Video | 0/114 episodes shot |
| Zone reset videos | 114/114 short zone-reset videos, rendered, not posted anywhere yet (carried forward from 2026-09-20 10:15: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, photo-led | 2/111 eligible photo-led zone-reset videos, rendered, not posted anywhere yet (carried forward from 2026-09-20 10:15: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, 16:9 for YouTube | 114/114 horizontal zone-reset videos for YouTube, rendered, not posted anywhere yet (carried forward from 2026-09-20 10:15: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, narrated | 114/114 narrated zone-reset videos with real voice, rendered, not posted anywhere yet (carried forward from 2026-09-20 10:15: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Social cards, Pinterest and Instagram | 114/114 zones, Pinterest and Instagram cards ready, not posted anywhere yet |
| YouTube upload text | 114/114 zones, title/description/tags written, not posted anywhere yet |
| YouTube thumbnails | 114/114 zones, YouTube thumbnail designed and ready |

## What needs you

- **Redeploy the site.** Production is serving an older build: 0 of 9 assets on the live homepage differ from this repository, and no zone page carries its photograph yet. The image is built and pushed to ghcr.io; the Redeploy button in Hostinger is the only step left. Until then 111 reviewed pictures and every fix since the last deploy reach nobody.
- **Verify the site in Google Search Console** (3 min). Google fetched all 114 zone pages on 23 to 27 August, twice each, and has barely returned since.
- **Authorise YouTube uploads** (5 min). 102 finished, narrated, captioned videos are on a disk.
- **Paste the business description into Stripe** (2 min). The live account still has no product description; it is the first thing a buyer reads about us at checkout, and the account-level gap is visible today.
- **#34** Decide: does the Kitchen deck's print-only page satisfy C20's "downloadable" condition?
- **#33** Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3)
- **#31** Decide: the deck gallery and the deck download are two different card designs
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands

## Open issues

| # | Title | Labels |
|---|---|---|
| 34 | Decide: does the Kitchen deck's print-only page satisfy C20's "downloadable" condition? | decision |
| 33 | Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3) | decision |
| 31 | Decide: the deck gallery and the deck download are two different card designs | decision |
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely | blocked-on-art |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 2 | Regenerate 7 remaining stale card images (was 9): needs a stronger model or photographs, not a retry | P0, blocked-on-art |
