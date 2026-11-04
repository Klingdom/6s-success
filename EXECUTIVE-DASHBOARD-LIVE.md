# 6S Success: Live Executive Dashboard

> Generated 2026-11-04 03:24 by `ops/dashboard.py`. Every figure is measured, not typed.
> Do not hand-edit. Re-run the script instead.

## The 60-second read

| | |
|---|---|
| **Overall** | **YELLOW** 9 P0 items still open. |
| **Revenue this month** | **$0 of $20,000 target (0.0%)** |
| | `............................` |
| **Paying customers** | 0 |
| **Email list** | 0 |
| **Can the site take money?** | yes, confirmed live, 129 of 130 catalog items |

### The one constraint

The site can take money for 129 of 130 catalog items, each a live Stripe Payment Link or a real free download. Still not buyable: Corporate Lean 6S. All 240 forms still hand off to email by hand instead of capturing a list. The widened catalog has not moved revenue because almost nobody is arriving at the site yet. Discovery, not what can be bought, is the constraint now.

---

## Where the work stands

| Stream | State |
|---|---|
| Traffic | 1048 pageviews from 97 visitors across 247 visits, 2026-08-20 to 2026-10-03. **441 of those pageviews came from 2 automated session(s)**, leaving 607 from 95 visitors. The remainder is not the same as strangers: it still includes Phil and any check run from a real browser. (carried forward from 2026-10-03 21:13; this run could not measure it fresh: **not measured** (no ssh key at /home/runner/.ssh/6s_deploy, so the database was not reached). No number here means nobody looked, not that nobody came.) |
| Affiliate | T2 not fired: 1 of 60 outbound retailer click(s) in the last 90 days, from 1 visitor(s), internal and automated excluded. No application is authorised. (carried forward from 2026-10-03 21:13; this run could not measure it fresh: T2 NOT EVALUATED: analytics unreadable (no ssh key at /home/runner/.ssh/6s_deploy, so the database was not rea). This is not a reading of zero.) |
| Open issues | 30 (9 P0, 2 blocked on art, 28 need your call) |
| Closed to date | 33 |
| Commits (7 days) | 1434 of 10612 total |
| Working tree | uncommitted or unpushed work |
| Last commit | `79fb1a7e2` PM check-in: close cold-read-ledger staleness on build_seo.p |

## Product readiness

| Product | Measured state |
|---|---|
| Website | 244 pages, 0 dead links, 4/4 legal pages, 240 disconnected forms |
| Book | 50/50 chapters, 50/50 carry the safety notice, 13 have no photographs, front matter drafted |
| Book, sellable? | YES EPUB built 0.81 MB, cover yes, 0 unfilled front-matter fields |
| Micro zones | 20 rooms, 114 zones (the spine every product shares) |
| Card decks | 0/20 rooms, 114/114 zones covered (card art lives outside the repo) |
| Entryway deck | print PDF already built and shipped (72 cards); local render cache empty here, so 0 is not a regression |
| Zone imagery | 114/114 zone pages carry a reviewed picture (live) |
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

- **Check your Claude Code usage limit or plan status** (2 min). **Resolved as a live incident 2026-10-09; unrecurred since, re-checked directly 2026-11-03 (`list_triggers`: all three Routines' last_run is SUCCEEDED or PENDING, none FAILED).** The autonomous PM and operator Routines went dark 2026-10-04 to 2026-10-09 on `USAGE_LIMIT_REACHED`; full investigation archived to `OWNER-ACTIONS-ARCHIVE.md`, account also in `STATUS.md` INCIDENT-002 and GitHub issue #40.
- **~~Add `VPS_DEPLOY_KEY` as a GitHub Actions secret~~ **DONE 2026-11-01 15:14Z, and the automatic deploy itself is now verified, repeatedly** (set from the owner-invoked CEO session on Phil's instruction, `gh secret list` confirms it; **corrected 2026-11-02 PM check-in: this row still said the first automatic deploy "is to be verified" when `STATUS.md`'s own BLOCKER-001 and Production Knowledge sections record at least five separate automatic deploys confirmed since, most recently build `b150c19629689ad2` at 2026-11-01T22:33:43Z matching repository HEAD with zero commits undeployed; nothing left open on this item**)** (2 min). Closes the single most repeated line in this repository's whole operating history for good, not once.
- **Run the traffic read yourself and paste the output back** (2 min). **Added 2026-11-02, scheduled operator cycle.** Traffic has been unmeasured since 2026-10-03, a full month: every number in `GOALS.md`'s O1 table (visitors, visits, pageviews, the week-over-week trend that decides whether the site's single constraint is improving) is a 2026-10-02 reading carried forward, because no sandboxed session holds the VPS key `ops/traffic_query.sh` needs.
- **~~Verify the site in Google Search Console~~, send the Pages/Performance reports** (2 min). **Corrected 2026-10-20, PM check-in: this row still described the original verification task as open, 6 days after the full `### 1a` section below it (line ~872) recorded Phil had done it.** Verification itself is done: Phil set up the Domain property via DNS TXT, confirmed live by `nslookup`, token recorded in `ops/site-verification.json`, `gate_site_verification_declared` now finds it.
- **Authorise YouTube uploads** (5 min). **Still open: authorisation itself has not happened.** CLEARED 2026-09-26 was the desync that once cast doubt on this row, fixed and re-verified, not the authorisation itself.
- **Paste the business description into Stripe** (2 min). The live account still has no product description; it is the first thing a buyer reads about us at checkout, and the account-level gap is visible today.
- **Add one line to the cloud environment's setup script** (2 min). **Found 2026-10-15, PM check-in.** This session's fresh container had `pymupdf` missing even though it is pinned in `ops/requirements.txt`, so `ops/affiliate.py --check`, the gate that keeps affiliate links out of every document a customer receives (Amazon's own operating agreement requires this), failed closed on all three PDFs it tried to read with "could not read 3 delivered document(s)".
- **#63** Decide/confirm: print the free Kitchen deck on a real printer and confirm it's legible (OWNER-ACTIONS.md item 19, about 5 min, never tracked as an issue)
- **#62** Decide: paste the Sustain-anchor link into 12 already-published YouTube descriptions (OWNER-ACTIONS.md item 20, about 10 min, never tracked as an issue)
- **#61** Decide/confirm: affiliate applications stay held until the T2 click trigger fires (OWNER-ACTIONS.md item 4, confirms existing plan, never tracked as an issue)
- **#60** Decide: run the 16 on-device mobile app checks (OWNER-ACTIONS.md item 2, about 20 min, never tracked as an issue)
- **#59** Decide: Rakuten's standing OAuth access to the support Google account (OWNER-ACTIONS.md item 1e, about 2 min, never tracked as an issue)
- **#58** Decide: paste the Stripe business description and checkout logo (OWNER-ACTIONS.md item 1d, about 2 min, never tracked as an issue)
- **#57** Decide/confirm: label your own devices so analytics can tell your clicks from a stranger's (OWNER-ACTIONS.md item 1c, about 1 min per device, never tracked as an issue)
- **#56** Decide: deploy the photos API, and whether it may analyze images (OWNER-ACTIONS.md item 22, never tracked as an issue)
- **#55** Decide: run a public MCP endpoint, or retire the unused mcp/ build entirely (OWNER-ACTIONS.md item 21, never tracked as an issue)
- **#54** Decide: create Facebook and X accounts for 155 finished Facebook posts and 723 finished X posts (OWNER-ACTIONS.md item 18, never tracked as an issue)
- **#53** Decide: the capped local demand test for In-Home Reset Days, a budget and a stop date (OWNER-ACTIONS.md item 17, ROADMAP G2 gate, never tracked as an issue)
- **#52** Decide: create Pinterest and Instagram business accounts, post the 114 finished zone cards (OWNER-ACTIONS.md item 16, never tracked as an issue)
- **#51** Decide: post the 114 finished vertical zone video clips to Shorts/TikTok/Reels (OWNER-ACTIONS.md item 11, never tracked as an issue)
- **#50** Decide: close two public ports on the VPS, Umami and Listmonk (OWNER-ACTIONS.md item 8, never tracked as an issue)
- **#49** Decide/confirm: product masters have one real backup copy (RISK-0011, OWNER-ACTIONS.md items 1g and 13, never tracked as an issue)
- **#48** Decide: open Apple Developer and Google Play accounts for the phone app (OWNER-ACTIONS.md item 5, $99/yr + $25, never tracked as an issue)
- **#47** Decide: turn on Gemini API billing (OWNER-ACTIONS.md item 1b, ~5 min + usage cost, never tracked as an issue)
- **#46** Decide: authorise YouTube uploads via OAuth (OWNER-ACTIONS.md item 1, 5 min, never tracked as an issue)
- **#45** Decide: the accounts layer, yes or no, and the privacy stance (OWNER-ACTIONS.md item 6, the largest single revenue gap, never tracked as an issue)
- **#44** Decide: open the Etsy shop and publish 3 finished print-pack listings (OWNER-ACTIONS.md item 15, ~40 min, never tracked as an issue)
- **#43** Decide: publish the finished book on Amazon KDP (OWNER-ACTIONS.md item 14, ~30 min, never tracked as an issue)
- **#42** Decide: the 10/30/60-minute autonomous cadence is now re-verifying an unchanged, fully-exhausted state
- **#40** Decide: Claude Code usage limit stalled the autonomous PM/operator routines for 5 days, silently
- **#33** Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3)
- **#31** Decide: the deck gallery and the deck download are two different card designs
- **#21** Decide: 6S Success and Ledgerium share one Stripe legal entity
- **#18** Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour
- **#15** Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands

## Open issues

| # | Title | Labels |
|---|---|---|
| 63 | Decide/confirm: print the free Kitchen deck on a real printer and confirm it's legible (OWNER-ACTIONS.md item 19, about 5 min, never tracked as an issue) | decision |
| 62 | Decide: paste the Sustain-anchor link into 12 already-published YouTube descriptions (OWNER-ACTIONS.md item 20, about 10 min, never tracked as an issue) | decision |
| 61 | Decide/confirm: affiliate applications stay held until the T2 click trigger fires (OWNER-ACTIONS.md item 4, confirms existing plan, never tracked as an issue) | decision |
| 60 | Decide: run the 16 on-device mobile app checks (OWNER-ACTIONS.md item 2, about 20 min, never tracked as an issue) | decision |
| 59 | Decide: Rakuten's standing OAuth access to the support Google account (OWNER-ACTIONS.md item 1e, about 2 min, never tracked as an issue) | decision |
| 58 | Decide: paste the Stripe business description and checkout logo (OWNER-ACTIONS.md item 1d, about 2 min, never tracked as an issue) | P0, decision |
| 57 | Decide/confirm: label your own devices so analytics can tell your clicks from a stranger's (OWNER-ACTIONS.md item 1c, about 1 min per device, never tracked as an issue) | decision |
| 56 | Decide: deploy the photos API, and whether it may analyze images (OWNER-ACTIONS.md item 22, never tracked as an issue) | decision |
| 55 | Decide: run a public MCP endpoint, or retire the unused mcp/ build entirely (OWNER-ACTIONS.md item 21, never tracked as an issue) | decision |
| 54 | Decide: create Facebook and X accounts for 155 finished Facebook posts and 723 finished X posts (OWNER-ACTIONS.md item 18, never tracked as an issue) | decision |
| 53 | Decide: the capped local demand test for In-Home Reset Days, a budget and a stop date (OWNER-ACTIONS.md item 17, ROADMAP G2 gate, never tracked as an issue) | P0, decision |
| 52 | Decide: create Pinterest and Instagram business accounts, post the 114 finished zone cards (OWNER-ACTIONS.md item 16, never tracked as an issue) | decision |
| 51 | Decide: post the 114 finished vertical zone video clips to Shorts/TikTok/Reels (OWNER-ACTIONS.md item 11, never tracked as an issue) | decision |
| 50 | Decide: close two public ports on the VPS, Umami and Listmonk (OWNER-ACTIONS.md item 8, never tracked as an issue) | P0, decision |
| 49 | Decide/confirm: product masters have one real backup copy (RISK-0011, OWNER-ACTIONS.md items 1g and 13, never tracked as an issue) | P0, decision |
| 48 | Decide: open Apple Developer and Google Play accounts for the phone app (OWNER-ACTIONS.md item 5, $99/yr + $25, never tracked as an issue) | decision |
| 47 | Decide: turn on Gemini API billing (OWNER-ACTIONS.md item 1b, ~5 min + usage cost, never tracked as an issue) | decision |
| 46 | Decide: authorise YouTube uploads via OAuth (OWNER-ACTIONS.md item 1, 5 min, never tracked as an issue) | decision |
| 45 | Decide: the accounts layer, yes or no, and the privacy stance (OWNER-ACTIONS.md item 6, the largest single revenue gap, never tracked as an issue) | P0, decision |
| 44 | Decide: open the Etsy shop and publish 3 finished print-pack listings (OWNER-ACTIONS.md item 15, ~40 min, never tracked as an issue) | P0, decision |
| 43 | Decide: publish the finished book on Amazon KDP (OWNER-ACTIONS.md item 14, ~30 min, never tracked as an issue) | P0, decision |
| 42 | Decide: the 10/30/60-minute autonomous cadence is now re-verifying an unchanged, fully-exhausted state | decision |
| 40 | Decide: Claude Code usage limit stalled the autonomous PM/operator routines for 5 days, silently | decision |
| 33 | Decide: reintroduce Momentum, and keep Upgrade/Tool cards deleted (DECK-GAME-DESIGN.md section 7, items 2-3) | decision |
| 31 | Decide: the deck gallery and the deck download are two different card designs | decision |
| 29 | Live deck gallery: 14 cards still say "Set in Order", one is the wrong card entirely | blocked-on-art |
| 21 | Decide: 6S Success and Ledgerium share one Stripe legal entity | decision |
| 18 | Decide: chapter 47's 27 plates are monochrome while the rest of the book is colour | decision |
| 15 | Decide: 6S Success needs its own Listmonk, or the shared one breaks both brands | P0, decision |
| 2 | Regenerate 7 remaining stale card images (was 9): needs a stronger model or photographs, not a retry | P0, blocked-on-art |
