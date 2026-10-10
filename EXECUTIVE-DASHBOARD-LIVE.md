# 6S Success: Live Executive Dashboard

> Generated 2026-10-10 13:54 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 2 P0 items still open. |
| **Revenue this month** | **$0 of $20,000 target (0.0%), carried forward from 2026-10-03 21:13 because this run could not reach Stripe** |
| | `............................` |
| **Paying customers** | 0 |
| **Email list** | 0 |
| **Can the site take money?** | repository says yes (129 of 130 catalog items), **unconfirmed on the live site**: no Stripe credential in this environment to check the links a visitor actually hits |

### The one constraint

PRODUCTION IS SERVING AN OLD BUILD. The live site can take money, and every payment link it serves is active in Stripe, but it is running a build from before most of this work existed. A session with real access confirmed production current at 2026-10-09T05:32:43Z (build e3d3bc8c77a83e38). The repository has since moved to build 5e709f2f552de432, not yet redeployed, so this gap is whatever changed since that confirmation, not an unknown backlog. Waiting behind that deploy: 129 of 130 catalogue items in this repository are buyable, each a live Stripe Payment Link or a real free download. One deploy moves all of it to the customer. Whether 6s-success.com reaches the site could not be checked from this run's network, so treat public reachability as unverified, not confirmed.

---

## Where the work stands

| Stream | State |
|---|---|
| Traffic | 1048 pageviews from 97 visitors across 247 visits, 2026-08-20 to 2026-10-03. **441 of those pageviews came from 2 automated session(s)**, leaving 607 from 95 visitors. The remainder is not the same as strangers: it still includes Phil and any check run from a real browser. (carried forward from 2026-10-03 21:13; this run could not measure it fresh: **not measured** (no ssh key at /root/.ssh/6s_deploy, so the database was not reached). No number here means nobody looked, not that nobody came.) |
| Affiliate | T2 not fired: 1 of 60 outbound retailer click(s) in the last 90 days, from 1 visitor(s), internal and automated excluded. No application is authorised. (carried forward from 2026-10-03 21:13; this run could not measure it fresh: T2 NOT EVALUATED: analytics unreadable (no ssh key at /root/.ssh/6s_deploy, so the database was not reached). This is not a reading of zero.) |
| Open issues | 9 (2 P0, 2 blocked on art, 7 need your call) |
| Closed to date | 31 |
| Commits (7 days) | 468 of 5925 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `b5cec1c7b` Hourly check-in record |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 219 pages, 0 dead links, 4/4 legal pages, 215 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 114/114 zones covered (card art lives outside the repo) |
| Entryway deck | print PDF already built and shipped (72 cards); local render cache empty here, so 0 is not a regression |
| Zone imagery | 114/114 zone pages carry a reviewed picture (BUILT, NOT DEPLOYED) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~4,939 ready-to-publish units, unused |
| Video | 0/114 episodes shot |
| Zone reset videos | 114/114 short zone-reset videos, rendered, not posted anywhere yet (carried forward from 2026-10-03 21:13: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, photo-led | 2/114 eligible photo-led zone-reset videos, rendered, not posted anywhere yet (carried forward from 2026-10-03 21:13: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, 16:9 for YouTube | 114/114 horizontal zone-reset videos for YouTube, rendered, not posted anywhere yet (carried forward from 2026-10-03 21:13: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Zone reset videos, narrated | 114/114 narrated zone-reset videos with real voice, rendered, not posted anywhere yet (carried forward from 2026-10-03 21:13: build/video/*.mp4 is no longer tracked in git, so this could not be measured here) |
| Social cards, Pinterest and Instagram | 114/114 zones, Pinterest and Instagram cards ready, not posted anywhere yet |
| YouTube upload text | 114/114 zones, title/description/tags written, not posted anywhere yet |
| YouTube thumbnails | 114/114 zones, YouTube thumbnail designed and ready |

## What needs you

- **Redeploy the site.** Production is serving an older build: 0 of 10 assets on the live homepage differ from this repository, and zone photography already matches the last confirmed deploy (114 zone pages carrying their reviewed picture); this gap is elsewhere. The image is built and pushed to ghcr.io; the Redeploy button in Hostinger is the only step left.
- **Check your Claude Code usage limit or plan status** (2 min). **Added 2026-10-09, PM check-in.** The autonomous PM and operator Routines went completely dark for roughly 5 days: `git log` shows zero Claude-authored commits between 2026-10-04 11:19:40Z and this cycle, every one of the 36 commits in that window from the dumb hourly check-in/social-rotation bot instead.
- **Add `VPS_DEPLOY_KEY` as a GitHub Actions secret** (2 min). Closes the single most repeated line in this repository's whole operating history for good, not once.
- **Verify the site in Google Search Console** (3 min). Google fetched all 114 zone pages on 23 to 27 August, twice each, and has barely returned since.
- **Authorise YouTube uploads** (5 min). **CLEARED 2026-09-26: the desync that held this row is fixed and re-verified.** The publish pair was verified directly: all 114 narrated 16:9 masters in `build/video/zones-narrated`, which is what this tool actually uploads, end within 5 seconds of their own caption track, 114 of 114.
- **Paste the business description into Stripe** (2 min). The live account still has no product description; it is the first thing a buyer reads about us at checkout, and the account-level gap is visible today.
- **#40** Decide: Claude Code usage limit stalled the autonomous PM/operator routines for 5 days, silently
- **#35** Decide: add VPS_DEPLOY_KEY as a GitHub Actions secret to automate production deploys
- **#33** Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3)
- **#31** Decide: the deck gallery and the deck download are two different card designs
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands

## Open issues

| # | Title | Labels |
|---|---|---|
| 40 | Decide: Claude Code usage limit stalled the autonomous PM/operator routines for 5 days, silently | decision |
| 35 | Decide: add VPS_DEPLOY_KEY as a GitHub Actions secret to automate production deploys | decision |
| 33 | Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3) | decision |
| 31 | Decide: the deck gallery and the deck download are two different card designs | decision |
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely | blocked-on-art |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 2 | Regenerate 7 remaining stale card images (was 9): needs a stronger model or photographs, not a retry | P0, blocked-on-art |
