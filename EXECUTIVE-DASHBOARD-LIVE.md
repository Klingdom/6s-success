# 6S Success: Live Executive Dashboard

> Generated 2026-09-01 09:56 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 3 P0 items still open. |
| **Revenue this month** | **$19 of $20,000 target (0.1%), carried forward from 2026-08-31 14:31 because this run could not reach Stripe** |
| | `............................` |
| **Paying customers** | 1 |
| **Email list** | 0 |
| **Can the site take money?** | repository says yes (158 of 159 catalog items), **unconfirmed on the live site**: no Stripe credential in this environment to check the links a visitor actually hits |

### The one constraint

The site can take money for 158 of 159 catalog items, each a live Stripe Payment Link or a real free download. Still not buyable: Corporate Lean 6S. All 187 forms still hand off to email by hand instead of capturing a list. Whether 6s-success.com reaches the site could not be checked from this run's network, so treat public reachability as unverified, not confirmed. The widened catalog has not moved revenue because almost nobody is arriving at the site yet. Discovery, not what can be bought, is the constraint now.

---

## Where the work stands

| Stream | State |
|---|---|
| Open issues | 9 (3 P0, 2 blocked on art, 5 need your call) |
| Closed to date | 20 |
| Commits (7 days) | 402 of 681 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `d9e26ccd` Ninth cycle of the day: verify three price-drift candidates  |

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
| Social corpus | ~2,721 ready-to-publish units, unused |
| Video | 0/114 episodes shot |

## What needs you

- **Redeploy the site.** Production is serving an older build: 7 of 9 assets on the live homepage differ from this repository, and no zone page carries its photograph yet. The image is built and pushed to ghcr.io; the Redeploy button in Hostinger is the only step left. Until then 110 reviewed pictures and every fix since the last deploy reach nobody.
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#20** Decide: how the card decks get sold, and what unblocks the paid tier
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands
- **#7** Decide: keep or discard the 2,786-card master plan

## Open issues

| # | Title | Labels |
|---|---|---|
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely |  |
| 27 | Process: hourly trigger's STEP 0 diagnoses the same shallow-clone symptom every cycle (8+ occurrences) | process |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 20 | Decide: how the card decks get sold, and what unblocks the paid tier | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 7 | Decide: keep or discard the 2,786-card master plan | decision |
| 2 | Regenerate 16 remaining stale card images | P0, blocked-on-art |
| 1 | Regenerate EE-001 and EP-005 card art to remove Amazon trademarks | P0, ip, blocked-on-art |
