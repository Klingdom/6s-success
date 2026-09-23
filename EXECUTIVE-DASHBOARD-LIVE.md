# 6S Success: Live Executive Dashboard

> Generated 2026-09-23 13:52 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 2 P0 items still open. |
| **Revenue this month** | **$0 of $20,000 target (0.0%)** |
| | `............................` |
| **Paying customers** | 0 |
| **Email list** | 0 |
| **Can the site take money?** | yes, confirmed live, 129 of 130 catalog items |

### The one constraint

The site can take money for 129 of 130 catalog items, each a live Stripe Payment Link or a real free download. Still not buyable: Corporate Lean 6S. All 194 forms still hand off to email by hand instead of capturing a list. The widened catalog has not moved revenue because almost nobody is arriving at the site yet. Discovery, not what can be bought, is the constraint now.

---

## Where the work stands

| Stream | State |
|---|---|
| Traffic | 980 pageviews from 83 visitors across 214 visits, 2026-08-20 to 2026-09-22. **441 of those pageviews came from 2 automated session(s)**, leaving 539 from 81 visitors. The remainder is not the same as strangers: it still includes Phil and any check run from a real browser. |
| Affiliate | T2 not fired: 1 of 60 outbound retailer click(s) in the last 90 days, from 1 visitor(s), internal and automated excluded. No application is authorised. |
| Open issues | 7 (2 P0, 2 blocked on art, 5 need your call) |
| Closed to date | 27 |
| Commits (7 days) | 1150 of 3559 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `b0166730` Finish the Stripe retirement (65 of 65), close owner item 1h |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 198 pages, 0 dead links, 4/4 legal pages, 194 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 9/114 zones covered (card art lives outside the repo) |
| Entryway deck | 89 cards render clean from the template layer; the gallery publishes 72 of them |
| Zone imagery | 111/114 zone pages carry a reviewed picture (live) |
| Canon defects | 0 live uses of the rejected term "Set in Order" |
| Social corpus | ~4,939 ready-to-publish units, unused |
| Video | 0/114 episodes shot |
| Zone reset videos | 114/114 short zone-reset videos, rendered, not posted anywhere yet |
| Zone reset videos, photo-led | 2/111 eligible photo-led zone-reset videos, rendered, not posted anywhere yet |
| Zone reset videos, 16:9 for YouTube | 114/114 horizontal zone-reset videos for YouTube, rendered, not posted anywhere yet |
| Zone reset videos, narrated | 114/114 narrated zone-reset videos with real voice, rendered, not posted anywhere yet |
| Social cards, Pinterest and Instagram | 114/114 zones, Pinterest and Instagram cards ready, not posted anywhere yet |
| YouTube upload text | 114/114 zones, title/description/tags written, not posted anywhere yet |
| YouTube thumbnails | 114/114 zones, YouTube thumbnail designed and ready |

## What needs you

- **Verify the site in Google Search Console** (3 min). Google fetched all 114 zone pages on 23 to 27 August, twice each, and has barely returned since.
- **Authorise YouTube uploads** (5 min). 102 finished, narrated, captioned videos are on a disk.
- **Paste the business description into Stripe** (2 min). The live account still has no product description; it is the first thing a buyer reads about us at checkout, and the account-level gap is visible today.
- **~~Run the Stripe retirement for the SKUs still unconfirmed~~ **DONE 2026-09-23 by an autonomous session, not by you.** (0 min). All **65** retired SKUs are now archived and recorded in `ops/retired-skus-stripe-status.json`; the gate that watches this reads 0 unconfirmed.
- **#33** Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3)
- **#31** Decide: the deck gallery and the deck download are two different card designs
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands

## Open issues

| # | Title | Labels |
|---|---|---|
| 33 | Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3) | decision |
| 31 | Decide: the deck gallery and the deck download are two different card designs | decision |
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely | blocked-on-art |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 2 | Regenerate 7 remaining stale card images (was 9): needs a stronger model or photographs, not a retry | P0, blocked-on-art |
