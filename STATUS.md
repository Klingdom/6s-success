# 6S Success Current Operating Status

> Living operational state for Claude Code and all 6S Success autonomous agents.

## Document Role

`STATUS.md` is the fastest authoritative summary of **what is happening now**.

It is not a strategy document, backlog, changelog, incident archive, or analytics database.

Every agent performing meaningful autonomous work should read this file after `CLAUDE.md` and `AUTONOMY.md`.

Update this file whenever the material operating state changes.

---

# 0. Claim before you start, if more than one session is running

**Added 2026-09-29 after three collisions in a single afternoon.** Two
autonomous sessions independently built the same cross-zone
`diagnosed_reading()` precompute, wrote the same `forms_dead` increments into
`RISKS.md`, and then independently worked out the same rewording of the same
line in that file. Every one of those was correct work. All of it but the first
copy was waste, and the merges cost more than the fixes.

`BACKLOG-2026-09-07.md` B7 already says to claim a room before authoring it.
That rule was written for content and the collisions were not in content. It
applies to anything shared:

**For B9 (room decks) specifically, use `python ops/b9_claims.py --claim
"Room Name" --note "..."` (and `--release "Room Name"` when done), not a
hand-edited line below.** This section's own prose convention is what a
2026-09-29 cycle used to claim Nursery, minutes after a concurrent session
had already claimed it in `ops/b9-claims.json`: prose here does not check
`ops/b9-claims.json`, so it caught nothing, and a subagent spent real work
before the duplicate was found (`gate_b9_claims_current`'s own warning, not
this section, is what surfaced it). `ops/b9_claims.py --claim` reads that
same ledger and refuses outright if the room is already actively claimed by
someone else, so it is a real check, not just visibility. Still append a
line below too, for a human skimming this file, but treat the JSON ledger as
authoritative for B9 and check it (`python ops/b9_claims.py --status`)
before claiming a room here.

- a generator in `ops/`
- a gate in `ops/preflight.py`
- an operating document (`RISKS.md`, `STATUS.md`, `GOALS.md`, `OWNER-ACTIONS.md`)
- a workflow in `.github/workflows/`

**Before starting non-trivial work on one of those, append a line below.**
Delete it when the work lands. A stale claim is much cheaper than a duplicated
one: if a line here is older than a day and its work is in `main`, remove it.

This is a convention, not a lock. It cannot stop a collision on its own; it
makes one visible in the thirty seconds before the work starts, which is the
only moment it is cheap.

## Open claims

**None currently open.** The `ops/ship.py` / `.github/workflows/hourly-brief.yml`
claim opened and released this same cycle (2026-10-13, scheduled operator
cycle): folded `ops/dashboard.py` regeneration into both, pushed as
`eed323558`. Full account in `ops/NIGHTLY-LOG.md` and `BACKLOG-2026-09-07.md`
section 9. Also pruned 2026-10-11, PM check-in (30 minute triage),
per this section's own rule ("if a line here is older than a day and its
work is in main, remove it"): every released-claim entry below this line
was dated 2026-10-09 or 2026-10-10 (the A25 master-bath misattribution fix,
the five-file and three separate six/seven-file cold-read tiers, the
dashboard re-verification, the `check_ledgerium.py`-through-
`check_video_standard.py` claim), all confirmed landed on `main` and
reconfirmed with zero drift by a large majority of today's own PM and
operator cycles (`preflight.py` clean to the documented `gate_tests`
sandbox hang, 9 open GitHub issues unchanged, 0 PRs). Full account of each
stays in `ops/NIGHTLY-LOG.md`; nothing here was still actually open.

# 1. Status Metadata

**Latest, 2026-10-29 (16:5x), owner-invoked CEO cycle: `/articles/how-to-organize-paperwork` pushed (`c79829238`, BACKLOG section 60) with a fix for `share_cards.py --wire` stacking stray carriage returns on Windows checkouts. NOT deployed; the gap is 6 site commits, see BLOCKER-001's newest entry.**

**Latest, 2026-10-29, owner-invoked CEO cycle: `/articles/how-to-organize-toys` pushed (`2404a870c`, BACKLOG section 59), NOT deployed.** A second `python ops/deploy.py` attempt, made with Phil's explicit instruction to proceed, was again refused by this session's permission layer; the deploy workflow was deliberately not dispatched by hand as a way around that. Production stays at `a0bbe5bb276ee21b` until a session allowed to deploy runs `python ops/deploy.py`, or `VPS_DEPLOY_KEY` lands (OWNER-ACTIONS 0).

**Latest, 2026-10-29, scheduled operator cycle: the entry below restated the deploy gap's own commit count, and it had gone stale (said two, BLOCKER-001's own latest entry had already moved to four, three of them content, by the 05:1x PM check-in).** Re-derived directly, not cited: `resolve_verdict_commit('a0bbe5bb276ee21b')` resolves to `ad933f9e5`; `deploy_gap_material_commits('ad933f9e5')` against real current `HEAD` returns the same 4 commits BLOCKER-001 already names (`840f3e11b`, `ba69e8d0f`, `ea437edc0`, `f9c97f72f`, the last a non-material build-id restamp). This is the sixth section this exact "cites a fact, wrong number beside it" shape has hit (BLOCKER-001, Production Knowledge, Immediate Focus, the Public website and Production traceability table rows, now this one), so rather than fix one more number and leave the next drift to repeat, applied the same structural fix 2026-10-23 used for Immediate Focus: the entry below no longer restates a commit count. New `gate_status_latest_entry_gap_current` in `preflight.py` (pure logic in `status_latest_entry_gap_problem`) checks this entry independently of the other two deploy-staleness gates, since this paragraph cites no build_id for either of those to key off; `ops/tests/test_gate_status_latest_entry_gap_current.py` (6 cases) fail-then-pass proved directly against the real committed file before and after this fix. Traffic-measurement gap (unmeasured since 2026-10-03, same missing SSH credential) is unaffected and still accurate, unchanged below.

**Older entries (113 of them, 2026-08 to 2026-10-29) live in `STATUS-ARCHIVE.md`.** Rotated 2026-10-29 by `ops/rotate_status_metadata.py --apply`: kept live only the entry (or entries, where more than one shares the same most recent date) carrying 2026-10-29, the actual most recent date found in the chain, not simply whichever entry happened to sit physically first (the chain had drifted out of newest-first order); 1 more entries moved to the archive. Nothing is deleted, and the gates that scan this file for stale claims (`gate_no_stale_session_label`, `gate_no_stale_checkout_count`, `gate_no_stale_listmonk_blocker`, `gate_corporate_buy_path_current`, `gate_critical_risks_escalated`) scan the archive too, so an archived claim is no less checked than a current one.

# 2. Executive Snapshot

## Current Objective

The money path now works well enough to test. The constraint has moved again,
from "can a customer pay" to "can anything be measured, and has a stranger
ever converted". `ROADMAP-2026-2029.md` (written 2026-08-24) is the current
authoritative strategy; it supersedes `ROADMAP.md`, `STRATEGY.md` and
`GROWTH-PLAN.md` in spirit even though those files still exist on disk.
`BACKLOG-2026-09-07.md` is the current authoritative work queue. **Corrected
2026-09-23: this line still named `BACKLOG-2026-H2.md` here, fifteen days
after section 21 below recorded that `BACKLOG-2026-09-07.md`, Phil's own
reprioritisation toward micro zones, decks and image/video work, supersedes
`BACKLOG-2026-H2.md`'s ordering.** `BACKLOG-2026-H2.md` still holds the
process rules (epics, gating discipline) and `BACKLOG.md` is superseded by
both.

Standing objective from the owner (2026-08-16): develop all content and products
continuously and iteratively toward $20,000 per month, without stopping for
approval, while keeping this file and the executive dashboard current enough to
be read at a glance each morning.

**The honest arithmetic, from `ROADMAP-2026-2029.md`:** the digital catalogue
cannot reach $20,000 a month on any reachable traffic (the $19 item alone needs
roughly a quarter million visits a month). Services (In-Home Reset Day at
$1,200) reach the number on far fewer bookings but consume Phil's own hours and
have not been demand-tested beyond one referral. Horizon 1 (now through August
2027) is about proving a stranger converts at all, with an honest revenue
target of $500 to $3,000 a month by month twelve, not $20,000.

## Current Business Goal

Build a trusted 6S Success digital business that helps customers improve rooms and micro-zones through desired-function discovery, root-cause diagnosis, quests, standards, products, and sustainment.

Long-term commercial target:

**$20,000+ monthly revenue**, pursued through real customer value rather than artificial activity or deceptive conversion tactics.

## Current Highest-Level Priority

**The ordering rule, from `BACKLOG-2026-09-07.md` section 0: the traffic
constraint decides the order.** Below it, the older rule still holds:
measurement before traffic, traffic before conversion, conversion before
product. Current state against each epic:

1. **Epic 1, measurement (blocks everything).** EXP-001 (has a stranger ever
   clicked a buy button) is answered, permanently: AMBIGUOUS (backlog 1.3,
   closed 2026-09-03). EXP-002 (does anyone reach the offer on a zone page)
   is still collecting scroll-depth data. Umami read access is partly done:
   Phil read the database directly 2026-09-02 and recorded a one-time
   baseline in `GOALS.md`, but no environment this operator runs in has a
   live credential, so that baseline cannot be refreshed or queried for
   EXP-002 without Phil re-pulling it by hand. The single highest-value item
   outstanding is a share URL or API key so an operator session can pull it
   directly (backlog item 1.2).
2. **Epic 2, broken or dishonest.** The real blocker is the shared Listmonk
   sending identity (issue #15, P0): a 6S signup currently would receive mail
   branded as a different company, so every signup surface on the site
   (footer and in-body) has been deliberately withdrawn rather than shipped
   half-honest. The email list is 0 and stays 0 until this is decided.
3. **Epic 3, traffic.** Search is the only durable, no-audience-required route
   and it takes 12 to 18 months to compound; Nova Consulting has no list to
   borrow. Issue #22 was closed 2026-08-25 (Phil's own session reached the
   site and IndexNow directly), but this operator's sandboxed network still
   returns http_code 000 for both on re-test the same day, so newly
   published pages still cannot be submitted to IndexNow from every session
   even though the ten already-written LinkedIn posts and image prompts are
   ready and waiting on Phil to publish/generate.
4. **Epic 4, conversion.** Deliberately not started; nothing here is
   interpretable until epic 1 lands.
5. **Epic 5, product.** The catalog is not short of products, it is short of
   visitors. Nothing here starts before epic 1 answers whether the funnel
   works at all.

Commerce was largely solved, then broke silently, then was fixed: 158 of 159
catalog items have a Stripe Payment Link or a real free download behind them
(widened from 10 on 2026-08-27, Phil's own Stripe sync); all six links the
live site actually served were found deactivated on 2026-08-30 and
reactivated and verified working by Phil on 2026-08-31 (see "Why this was
RED, and why it is YELLOW now" above). What is still unconfirmed is whether
the deployed site itself carries the rest of the repository's fixes and
current catalog and pricing. **Corrected 2026-09-11, operator: the "7 of 9
homepage assets behind" figure this paragraph cited is stale and no longer
what the dashboard measures** (`EXECUTIVE-DASHBOARD-LIVE.md` today reads
"could not be reached from here... treat public reachability as unverified,
not confirmed," not a specific stale-asset count); that number was last real
around 2026-08-31 and nobody re-derived this citation after the dashboard's
own measurement changed shape, the same "source corrected, artifact never
re-derived" defect class this file names throughout. The "Redeploy click"
framing is also superseded: `OWNER-ACTIONS.md` item 1 records the VPS SSH
deploy key installed 2026-09-01 ("No deploy needs you again"), so Hostinger's
manual click is no longer the mechanism. Every sandboxed (cloud) session,
this one included, reports "no deploy key at /root/.ssh/6s_deploy" and has no
egress to the VPS, so a sandboxed session can never confirm deploy freshness
directly. **Corrected 2026-09-23, PM check-in: the paragraph used to say
whether the site had ever been redeployed since 2026-09-01 was "genuinely
unknown from here." That was true once but is stale; it is not unknown.**
Local sessions with real VPS access hold the key's private half and use it
routinely, confirmed by real, timestamped entries in `OWNER-ACTIONS.md` and
`ops/deploy-verdict.json` (2026-09-15, -18, -20, -22, -23, several same-day):
each records the exact build hash moved to and the UTC timestamp checked
directly against the verdict file, not cited from memory. **Corrected again
2026-09-23, later PM check-in: this paragraph and the section 5 table below
had fallen one confirmation behind `BLOCKER-001`, which a same-day cycle had
already updated.** As of the last such check (`ops/deploy-verdict.json`,
`2026-09-23T19:00:39Z`), production served build `5eba61fde231c1a7`, from a
session that finished the Stripe SKU retirement (65 of 65 archived) and
redeployed (commit `8e4c8e33`, the dead mobile-nav fix on
`deck-gallery.html`/`deck-gallery-mudroom.html`). **Re-sized 2026-09-24,
PM check-in: the "one commit behind" figure above had itself gone stale
for over 8 hours while several intervening cycles repeated it unchecked.**
`git log 8e4c8e33..HEAD` is 47 commits, not 1 (repository HEAD build
`38b20571260ea9ff`, confirmed current via `ops/build_id.py --check`), and
two of those are live customer-facing, not internal-consistency work:
`a16788fa` fixed a second, real dead-nav-menu defect on `404.html`,
`corporate.html`, `kit.html` and 2 B2B articles (same defect class as
`8e4c8e33` itself), still serving the broken hamburger button to every
mobile visitor to those 5 pages right now; `b0166730` (Phil's own commit)
finished retiring the last of 65 dead/superseded Stripe SKUs, so
production's catalogue is stale by that much too. "No automated
pipeline exercises `ops/deploy.py`" is also still true (no `.github/workflows/`
job runs it) and remains a real gap: freshness depends on a local session
happening to run one, not on any guaranteed cadence.

### Completed since 2026-08-16

- Repository consolidated and made private; the complete-book PDF is no longer
  publicly downloadable from GitHub.
- Safety disclaimer injected estate-wide: 50/50 chapters, the Field Manual, the
  decks, the board games, the product appendix and the app prototype.
- Website legal surface built: privacy, terms, accessibility and safety notice,
  linked from all 13 pages. Dead links went from 24 to 0, and remain at 0.
- Two physical-safety defects fixed in the book (Ch 45 power tools, Ch 50 propane).
- 945 uses of the rejected term "Set in Order" swept to "Straighten".
- Amazon trademark removed from card EE-001 text and filenames.
- Site fonts: 14 missing real weights installed, ending faux bold, and the last
  third-party request removed. The site now makes zero external calls.
- All 14 site forms wired to a prefilled email handoff instead of discarding
  input (2026-08-17).
- Free sample PDF cut from 50.7 MB to 40.0 MB with no quality loss, and stopped
  claiming to be "The Complete Book" when it holds chapters 1 to 30 of 50
  (2026-08-17).
- Cart fixed to hand off what a customer actually selected, and the shop page
  stopped marketing 34 of 41 catalogued products, including two featured on the
  homepage, as available to buy when none has a supplier, a build, or a
  platform behind it yet. They now read "In development" and link to an
  honest interest form (2026-08-19).
- Site deployed to the Hostinger VPS: image published to `ghcr.io`, compose
  pasted and two silent faults fixed, DNS pointed at the VPS. The domain still
  does not reach it; see priority 1 above (2026-08-18).
- Free sample's on-disk filename still read "Complete Book" after its title
  and heading were corrected, so a reader's saved file carried the false claim
  the visible link text no longer made. Renamed the HTML and PDF (site and the
  content mirror) to name what they actually are: chapters 1 to 30 (2026-08-19).
- Live Stripe account onboarded and two consulting products taken live: Virtual
  Home Consult and In-Home Reset Day, both real Payment Links (2026-08-19).
- The consulting page's own primary "Book a consult" button sent buyers to a
  contact form instead of the live packages just below it, the exact page
  built to sell something that can now actually be bought. Repointed it to the
  packages section, and corrected `ops/dashboard.py`'s payment detection,
  which only looked for an embedded checkout script and so still reported
  "cannot take money" after the Payment Links went live (2026-08-19).
- Phil synced the 149 generated zone/room/kit/bundle packs to live Stripe
  himself and wired `window.CATALOG`, widening the buyable catalog from 10
  to 158 of 159 SKUs, and fixed the EPUB builder's hardcoded author
  placeholder that had blocked Amazon KDP submission (both 2026-08-27).
- Phil built a retail affiliate link layer (`ops/affiliate.py`,
  `ops/affiliate-accounts.json`, 10 programmes tracked), a compliance gate
  wired into `fulfil-orders.yml` (no affiliate link may ship inside a PDF,
  EPUB or other delivered document; disclosure must sit above any tracked
  link), and primary-sourced research on all 10 programmes, emailed to
  himself as a decision dossier (2026-08-28). No programme is applied to
  yet; opening an account requires his own legal/tax identity, so this is
  entirely his next step, not operator-actionable. The dossier's headline:
  do not apply to Amazon yet (a 180-day, 3-sale rule would likely burn the
  Associates ID permanently at current traffic), Wayfair's Creator terms
  forbid the only surfaces this site has, and Etsy/Office Depot/Home Depot
  legacy look like the best near-term fits.
- Phil found and fixed a live payment outage (all 6 Stripe links the site
  served were deactivated, invisible to every repository-level check for at
  least 3 days), added `ops/check_live_links.py` to catch it going forward,
  corrected terms/delivery-time/privacy copy that would have shipped
  publicly false statements on the same deploy, and hardened the deploy
  path itself (nginx config now validated in CI before publish, timeouts
  added to three proxied locations) (2026-08-30, `retro/RETRO-2026-08-30-cycle6.md`).
- Phil put each of the 109 sellable zone packs on its own zone page ($4 for
  6 cards, beside the existing $19 whole-house pack), closing the gap where
  the only pages that create demand for the long tail never linked to it
  (2026-08-30).
- One product, one card count: the Entryway deck was advertised as 46, 88
  and 90 cards in different places; corrected everywhere to the real 88, and
  `gate_deck_count` now checks it on every build (2026-08-30, Phil).
- The eight day payment outage closed: all six live Stripe payment links
  reactivated and verified working in a real browser, the same measurement
  that had reported them dead now reports the site can take money again
  (2026-08-31, Phil, `b0e9462`, `84c04cc`). The deployed site itself is
  still an older build than the repository; see the redeploy note above.

---

# 3. Current Operating Foundation

| Component | Status | Notes |
|---|---|---|
| `CLAUDE.md` | CREATED | Master autonomous operating constitution |
| `AUTONOMY.md` | CREATED | GREEN / YELLOW / RED execution authority |
| `STATUS.md` | CREATED | This living current-state file |
| Agent framework | IN PROGRESS | Specialist agents are being established |
| GitHub governance | DEFINED | `github-manager` agent created |
| Hostinger VPS/Docker governance | DEFINED | `vps-docker-manager` agent created |
| Reliability governance | DEFINED | `devops-sre` updated for separated ownership |
| Live business metrics | UNKNOWN | Must be connected and verified |
| Executive dashboard | NOT YET VERIFIED | Specification and implementation still required |
| Automated operating loop | IMPLEMENTED | Hourly trigger runs the cycle described in `DAILY-LOOP.md`. Issue #17 closed 2026-08-25: the trigger's prompt was rewritten to read `BACKLOG-2026-H2.md` directly rather than embedding a status snapshot, so it no longer needs self-update to stay current. |

---

# 4. Production Status

**Filled 2026-09-24, scheduled operator cycle, handed off by name by the
12:4x PM check-in: this table had stood as the unfilled 2026-08-16 bootstrap
template, every row `UNKNOWN`, even though sibling sections (5, 8, 17) had
long since been corrected with real evidence, contradicting this section in
the same document.** Filled from evidence already on hand across
`ARCHITECTURE.md` (corrected this same cycle), `DEPLOY-VPS.md`,
`RISKS.md`, `OWNER-ACTIONS.md` and `ops/deploy-verdict.json`, not guessed. No
sandboxed session can re-run any of this directly (no VPS egress, no
Stripe/SSH credential here); every row below is only as current as its own
citation, not this session's own measurement. A row stays `UNKNOWN` where no
session has ever actually measured it.

| Area | Status | Evidence / Notes |
|---|---|---|
| Public website | LIVE as of 2026-10-26T16:51:56Z, build `a0bbe5bb276ee21b`, **REOPENED: 8 commits undeployed, 6 of them content** (see `BLOCKER-001`) | **WIDENED 2026-10-29, scheduled operator cycle: widened from 6 to 8, found re-deriving the gap directly rather than citing the 16:5x entry.** `deploy_gap_material_commits('ad933f9e5')` against current `HEAD` returns 8 commits; the two new ones are `41938dd0` (the loft/attic FAQ gap fix) and `b6e9115a5` (the feed.xml/sitemap.xml rebuild that fix itself needed). Full account in `BLOCKER-001`'s own newest entry. No P0 regression: already-correct content and fixes sitting undeployed, nothing broken live. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (issue #35) is the only real fix. |
| Application/API | N/A BY DESIGN | No application server, database or backend exists; the site is static HTML served by nginx (`ARCHITECTURE.md` section 1) |
| Database | N/A FOR THE SITE ITSELF | The site holds no database. The Umami analytics database lives on the same VPS but is not part of this site's own stack; it is not backed up off-host (`RISKS.md` RISK-0007's 2026-09-21 finding) |
| Reverse proxy | Nginx Proxy Manager | A pre-existing shared instance, not Traefik; also fronts Ledgerium AI and Compassion Benchmark on the same VPS (`CLAUDE.md` 36b). `ARCHITECTURE.md` section 4, corrected this cycle after standing wrong (naming Traefik) since the file was written |
| TLS/HTTPS | Let's Encrypt, issued through NPM's own panel | Not tracked by this repository; certificate expiry/renewal history has never been inspected by any session (genuinely `UNKNOWN`) |
| Docker host | One Hostinger VPS, `187.77.25.50`, shared with two other businesses | Ledgerium AI and Compassion Benchmark on the same host (`DEPLOY-VPS.md`, `CLAUDE.md` 36b) |
| Critical containers | `6s-success`: healthy, 0 restarts, as of 2026-09-16 | `OWNER-ACTIONS.md` 1f. Two other containers on the shared host were found crash-looping (177/197 restarts) the same day, traced to Ledgerium's own half-finished deploy, not this site's; no action needed on either. Not re-measured since 2026-09-16 |
| Persistent volumes | One: the nginx access log | `docker-compose.hostinger.yml` (the file actually pasted into the Hostinger panel, confirmed by `RUNBOOK.md`'s own 2026-09-20 diff against the live host file) mounts `/var/log/6s-success:/var/log/nginx/persist`, added 2026-09-20 so the crawl log survives a redeploy. The `letsencrypt` volume named here previously belongs to the unused `docker-compose.proxy.yml` Traefik topology. NPM's own certificate/config data lives in NPM's own volume, external to this repository (`ARCHITECTURE.md` section 9, corrected this cycle) |
| Backups | Site: not needed, rebuildable from Git + a fresh image pull. The access-log volume: not backed up. NPM's config: not backed up. Umami analytics: one manual point-in-time export exists (2026-09-21, `ops/backup_analytics.py`, verified by independently recomputing the headline numbers from the CSV), not on a schedule | `RISKS.md` RISK-0007's 2026-09-21 finding; `DISASTER-RECOVERY.md` section 7c/7d. NPM's proxy-host configuration is recorded field by field so it can be rebuilt from a document if that volume is lost, but the volume itself is not backed up |
| Restore readiness | PARTIALLY MEASURED | A real container-loss drill ran 2026-09-21: pull 0.46s, run 0.38s, first HTTP 200 0.54s, total 1.38s, correct build id and full 159-item catalogue confirmed. Covers "container lost or bad deploy." Does NOT cover a lost host: no VPS has ever been reprovisioned, no DNS/NPM/certificate rebuild has been drilled (`RISKS.md` RISK-0007) |
| Disk capacity | 40% used, 38G of 96G, 58G free | Measured 2026-09-20 (`OWNER-ACTIONS.md` 1f, closed); was 79% full on 2026-09-16 before something reclaimed ~38GB (not this operator). Re-open if free space ever drops under ~5G |
| Memory capacity | UNKNOWN | No session has measured `free -h` on the host |
| CPU health | UNKNOWN | No session has measured `nproc`/load on the host |
| Production logs | Two sources, both real | NPM's own access log (survives container recreation, reaches back to 2026-08-19, has client IPs); a bind-mounted `/var/log/6s-success/access.log` since 2026-09-20 (rotated weekly, no IPs). Neither is shipped off-host |
| Monitoring | Traffic only, confirmed no infrastructure monitoring | Umami tracks visitors/pageviews (not infra health). `RUNBOOK.md`'s own inventory: "no external uptime monitor... no error monitoring." Liveness is checked on demand only, by `ops/deploy.py`, `ops/check_live_links.py` and the container's own `HEALTHCHECK` |
| Active incidents | NONE currently open | `INCIDENTS.md` is a policy standard with no live incident log entries. The nearest real production-impacting events on record are the 8-day dead-payment-link outage (2026-08-22 to 30, closed) and the Ledgerium crash-looping containers found 2026-09-16 (not this site's incident) |

### Production Rule

Do not replace `UNKNOWN` with `GREEN` without evidence.

---

# 5. Production Release

**Corrected 2026-09-23, PM check-in: this table had stood as an unfilled
UNKNOWN template even though `ops/deploy-verdict.json` has answered most of
it, continuously, since it was introduced.** No sandboxed session can
re-verify these fields directly (no VPS egress, no deploy key here), so
treat them as only as fresh as the verdict file's own `checked_at`, not as
this session's own measurement.

**CORRECTED 2026-10-26, scheduled operator cycle: the "Repository HEAD Build"/"Confirmed At" lines below still cited the stale `a1c75dafaee8ca8c` build and claimed a 4-commit, 2-material gap, re-derived directly rather than trusted, the same fifth-section gap this paragraph's own prior correction named and left unfixed.** `site/build-id.txt` reads `00187aebb3255957` directly, matching `ops/deploy-verdict.json`'s own confirmed build exactly; `deploy_gap_material_commits` re-derived against current `HEAD` (`267697dcf`) returns an empty list. Repository HEAD and the confirmed deployed build are the same thing right now: zero commits undeployed. Fixed below; this gate still does not parse this section, so it can drift again. Prior state, kept because the shape recurs: **CORRECTED 2026-10-26, PM check-in (05:4x slot): this section had stood unedited since the 2026-09-25T22:21:27Z confirmation even though `ops/deploy-verdict.json`, `BLOCKER-001` and section 4's own "Public website" row had each moved past it since, the same "source corrected, sibling section never told" shape `status_deploy_verdict_problem`'s own docstring names, just for a fifth section that gate does not parse (it checks only BLOCKER-001, Production Knowledge, and the Public website/Production traceability table rows).** Found while confirming the previous cycle's handoff rather than citing it; not yet added to that gate's section map, so this can still drift silently again until it is.

**Currently Deployed Build (last confirmed):** `a0bbe5bb276ee21b` (resolves to commit `ad933f9e5`), confirmed 2026-10-26T16:51:56Z, superseding the earlier `00187aebb3255957`/2026-10-26T14:48:46Z confirmation
**Confirmed At:** `2026-10-26T16:51:56Z` (`ops/deploy-verdict.json`,
a session with real production access)
**Repository HEAD Build:** `0f4abed11a267392` (`site/build-id.txt`,
re-read directly, scheduled operator cycle, 2026-10-29). **No longer
matches the confirmed deployed build above**: 8 commits, 6 of them content
(two mechanical: a build-id restamp and a feed/sitemap rebuild) sit
undeployed; see `BLOCKER-001` below for the full account and the
standing caveat that this gap only closes when `VPS_DEPLOY_KEY`
(`OWNER-ACTIONS.md` item 0, issue #35) makes redeploy automatic)
**Release / Tag:** NONE, every deploy is tracked by commit SHA / image
digest, 0 GitHub tags or releases exist
**Deployment Method:** `ops/deploy.py`, run manually by a local session
holding `~/.ssh/6s_deploy` (installed 2026-09-01). **Corrected 2026-09-24:**
`.github/workflows/deploy.yml` now exists and calls it automatically on every
successful image publish, but is inert until `VPS_DEPLOY_KEY` is set as a
GitHub secret (`OWNER-ACTIONS.md` "start here" item 0), so a manual run is
still today's only real deploy path
**Known-Good Rollback Release:** UNKNOWN, no rollback procedure has been
exercised or documented in this repository's tooling
**Runtime/Image Identity:** `ghcr.io` image, tag/digest not tracked here

Owners:

- Release identity: `github-manager`
- Reliability/readiness: `devops-sre`
- Runtime deployment state: `vps-docker-manager`

The first production discovery cycle should reconcile:

**GitHub release → deployed artifact/image → running production**

---

# 6. GitHub Status

Owner: `github-manager`

**Corrected 2026-09-20, scheduled operator cycle.** This table had stood as an
unfilled bootstrap template, every row UNKNOWN, since the file's creation,
even though this same document's own section 1 narrative and
`EXECUTIVE-DASHBOARD-LIVE.md` report most of these facts on every cycle. Filled
with what is genuinely known and live-checked this cycle via the GitHub API; a
row stays UNKNOWN only where this operator sandbox truly cannot see the
answer (no admin/security-alerts scope confirmed either way).

| Area | Status | Notes |
|---|---|---|
| Repository identified | `Klingdom/6s-success` | Confirmed via the GitHub API this cycle |
| Default branch | `main` | Confirmed; it is also the only branch that exists |
| Branch protections | NONE | `main` returns `protected: false` via the API |
| Open PRs | 0 | Confirmed live this cycle |
| Active branches | 1 (`main` only) | Confirmed live this cycle; no stray/abandoned branches |
| CI health | GREEN | **Corrected 2026-09-25 06:1x, PM check-in: the two prior rows (#1194-1196, 2026-09-20) were nine days stale and predated this same day's own real `checks.yml` outage and fix (STATUS.md section 1, `gate_ci_checkout_full_history`).** Checked live via the API rather than cited: `checks.yml` runs #1408-#1411, the four completed runs since the shallow-checkout fix (`1da2f69e`) landed, all `success`; #1412 (current HEAD, `5e73ade8`) still `in_progress` at the time of this check. `fulfil-orders.yml`, `linkedin-drafts.yml`, `social-drafts.yml` unchanged, still green on their latest scheduled runs |
| Deployment workflow | BUILT, INERT UNTIL A SECRET IS SET | `.github/workflows/deploy.yml` (added 2026-09-24) runs `ops/deploy.py` automatically once `publish-image.yml` succeeds, but exits without acting because no `VPS_DEPLOY_KEY` secret exists yet; a local session holding the VPS deploy key still runs it manually today, confirmed routinely since 2026-09-01 (`ops/deploy-verdict.json`, `OWNER-ACTIONS.md`). **Corrected 2026-09-23:** this row previously implied the click may never have happened; it has, repeatedly, just never from a sandboxed session |
| Security/dependency alerts | UNKNOWN | This operator's GitHub access has not been confirmed to include the security-alerts scope; not checked |
| Release convention | NONE | 0 tags, 0 releases. Every deploy is tracked by commit SHA / image digest, not a tag |
| Production traceability | Tracked, current build citation, **REOPENED: 8 commits undeployed, 6 content**, build `a0bbe5bb276ee21b` | **WIDENED 2026-10-29, scheduled operator cycle: widened from 6 to 8, same widening as the Public website row above; this row now agrees with it rather than trailing it.** `deploy_gap_material_commits('ad933f9e5')` against current `HEAD` returns 8 commits (adding `41938dd0`, `b6e9115a5` to the six already named). No P0 regression; full account in the Public website row and `BLOCKER-001`. |
| Repository hygiene | 10 open issues (8 `decision`, 2 `blocked-on-art`), 0 open PRs, 1 branch, 219+ test files, `preflight.py` clean | **Corrected 2026-10-20, PM check-in:** the prior "9 issues (7 decision)" row had gone stale; issue #42 (the 2026-10-14 cadence-waste question, `decision`-labelled) was never added here. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40, #42), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-10-12, PM check-in:** the prior "8 issues (6 decision)" row had gone stale; issue #40 (the 2026-10-09 usage-limit stall, `decision`-labelled) was never added here even though `OWNER-ACTIONS.md` item -1 and several `NIGHTLY-LOG.md` entries already cite it. Confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35, #40), 0 open PRs. Prior state, kept because the shape recurs: **Corrected 2026-09-25 06:1x, PM check-in:** the prior "7 issues (5 decision)" undercounted; issue #35 (`VPS_DEPLOY_KEY`, opened 2026-09-24) is a sixth `decision`-labelled issue, confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35). Not a formal audit, but the working facts a reader would otherwise have to reconstruct from `NIGHTLY-LOG.md` |

### GitHub Priority

Establish a trustworthy mapping between:

**work item → branch → PR → commit → release → production**

---

# 7. Hostinger VPS / Docker Status

Owner: `vps-docker-manager`

**Filled 2026-09-24, scheduled operator cycle, same handoff as section 4
above: this table stood as the unfilled 2026-08-16 bootstrap template while
`OWNER-ACTIONS.md`, `DEPLOY-VPS.md` and `RISKS.md` already had real, dated
answers for several rows.** Same sourcing rule as section 4: no sandboxed
session can measure any of this directly, so every row is only as current as
its own citation; genuine gaps stay `UNKNOWN` rather than guessed.

| Area | Status | Notes |
|---|---|---|
| VPS access | No sandboxed session holds it | Sessions running on Phil's own machine hold `~/.ssh/6s_deploy` (installed 2026-09-01) and use it routinely (`ops/deploy-verdict.json`'s history). `GitHub Actions` does not yet: issue #35 (`decision`) asks Phil to add it as `VPS_DEPLOY_KEY` |
| Host OS | Ubuntu 24.04.4 LTS, kernel 6.8.0-134-generic | `RUNBOOK.md`'s own hostinger inventory block |
| Docker Engine | Present, version UNKNOWN | Hostinger's own Docker Manager runs the compose stacks; no session has recorded the engine version |
| Docker Compose | Present; `docker-compose.hostinger.yml` is the file actually running | See `ARCHITECTURE.md` section 5, corrected this cycle. Confirmed by `RUNBOOK.md`'s own 2026-09-20 diff against the live host file. `docker-compose.yml` and `docker-compose.proxy.yml` also exist in this repository but neither is deployed |
| Compose projects | This site plus at least Ledgerium AI, Compassion Benchmark, Cal.com and Nginx Proxy Manager share the host | `CLAUDE.md` 36b, `RISKS.md` RISK-0007's 2026-09-21 finding. Full inventory (`docker compose ls`) has never been run and recorded here |
| Running containers | `6s-success`: confirmed healthy, 0 restarts, as of 2026-09-16 | `OWNER-ACTIONS.md` 1f. Two other containers on the shared host were crash-looping (177/197 restarts) the same day, traced to Ledgerium's own deploy, not this site's; no action taken on either, none needed. Full container inventory not recorded here |
| Container health | Healthy as of 2026-09-16 (0 restarts) | Not re-measured since; see row above |
| Networks | Known for this site | `docker-compose.hostinger.yml` joins the external `6s-proxy` network under the alias `6s-success`. NPM currently forwards to the VPS's own public IP on port 8973 rather than that alias (a tracked, not-yet-made improvement, `DISASTER-RECOVERY.md` 7c); the unused `docker-compose.proxy.yml` defines its own `web` network, not in use. No full `docker network ls` inventory of the whole shared host recorded |
| Volumes | This site's own stack defines one: the nginx access log | `/var/log/6s-success:/var/log/nginx/persist`, see section 4 above. NPM's own data volume and the Umami database volume also exist on the shared host, outside this repository's control; neither has been fully inventoried. Per the VPS Safety Rule below, nothing has been deleted |
| Images | 23.92 GB of images on the host as of 2026-09-20 (down from 62.65 GB on 2026-09-16) | `docker system df`, read by a session with real VPS access, `OWNER-ACTIONS.md` 1f. Includes images for every project on the shared host, not only this site's. ~38 GB of build cache was reclaimed between those two dates by an unidentified actor (not this operator) |
| Reverse proxy | Nginx Proxy Manager, shared instance | See section 4 above and `ARCHITECTURE.md` section 4, corrected this cycle (previously wrongly named Traefik) |
| Public ports | 80 and 443 held by NPM for all businesses on the host; this site's own container is not on either | `DEPLOY-VPS.md`. The site listens on host port 8973, reached only via NPM's forward |
| Environment configuration | The live file (`docker-compose.hostinger.yml`) needs no `.env` values; the unused proxy topology needs `DOMAIN`/`ACME_EMAIL` | `ARCHITECTURE.md` section 5. "Zero credentials touch the VPS" for the image-pull deploy method (`DEPLOY-VPS.md`); this would change if issue #35's `VPS_DEPLOY_KEY` decision is approved |
| Log rotation | Two logs, both rotate | NPM's own access log (rotation policy not recorded here) and the bind-mounted `/var/log/6s-success/access.log` (rotated weekly, confirmed in section 10 above) |
| Backup jobs | Host-level: Hostinger's own VPS backup, frequency UNKNOWN, never restore-tested (`RUNBOOK.md`). Application-level: NONE for NPM's config or the access-log volume; the Umami database has one manual, unscheduled export (2026-09-21) | `RISKS.md` RISK-0007's 2026-09-21 finding; `DISASTER-RECOVERY.md` section 7d. The site itself needs no backup job, being rebuildable from Git plus a fresh image pull |
| Off-host backup | The one manual Umami export (`ops/backup_analytics.py`, 2026-09-21) is the only off-host copy of anything VPS-side | NPM's config and the access-log volume have no off-host copy of any kind. Product masters (a separate, non-VPS risk, RISK-0011) have a OneDrive copy in progress, not yet restore-verified |
| Restore procedure | Documented, PARTIALLY drilled | `DISASTER-RECOVERY.md` covers both the container-loss and lost-host cases; only the container-loss case has been executed and timed (2026-09-21, 1.38s total, `RISKS.md` RISK-0007). The lost-host case (new VPS, DNS, NPM and certificate rebuild) has never been drilled |

### VPS Safety Rule

Unknown persistent resources must be preserved until understood.

**Unknown volume = DO NOT DELETE.**

---

# 8. Customer Experience Status

Owner: `product-manager`

Supporting agents:

- `ux-frontend`
- `qa-reviewer`
- `analytics-intelligence`

**Corrected 2026-09-20, scheduled operator cycle.** Every row below had stood
UNKNOWN even though most journeys are implemented and code-verified. Per
`CLAUDE.md` 0.3, "verified" here means proved against the repository through
automated/headless-browser tests, not against live production: this sandbox
has no egress to `6s-success.com`, so no row claims a live-production check
it did not make.

| Journey | Status | Notes |
|---|---|---|
| Homepage → useful next action | IMPLEMENTED | Home page leads to the Home Quest and the shop; `ops/audit_pages.py`/`audit_visual.py` find 0 findings across 190-191 pages, most recently re-run this cycle |
| Room discovery | IMPLEMENTED | 20 room pages, avg 28.8 inbound content links each, 0 orphans (`ops/link_graph_report.py`, this cycle) |
| Micro-zone discovery | IMPLEMENTED | 114 zone pages, same source, 0 orphans; `resources.html` links directly to all 114 |
| Personal Function Discovery | IMPLEMENTED for 5 zones | The Home Quest's first screen (`#symptom-step`) asks "What is annoying you right now?" in household words, then shows the zone, the real cause and a 2-minute action, per `CLAUDE.md` section 5's model. `SYMPTOM_PICKS` currently covers 5 zones (Entryway + Kitchen); the rest fall through to browsing by room |
| Root-cause guidance | IMPLEMENTED for 114 of 114 zones | **Corrected 2026-09-29, PM check-in: this row still said 12 of 114, the 2026-09-07 pilot figure, nine days after B9's room-deck build authored a full diagnosis layer for every remaining zone as a side effect of building all 20 room decks.** Confirmed live, not cited: `content.json` carries a non-empty `diagnosis` for 114 of 114 zones, and `grep -l 'id="diagnosis"' site/zones/*.html` returns 114 of 114 real zone pages (the 115th match is `zones/index.html`, which correctly carries none), matching `gate_diagnosis_rendered`'s own count-equality check. The 21-day pilot read this row cited as the gate never ran as a decision point; the corpus was rolled to all 114 zones directly. `BACKLOG-2026-09-07.md` section 5's own "Roll ... to all 114 / a 21-day read of a 12-zone pilot" row is the same stale claim, corrected in the same pass. |
| Quest selection | IMPLEMENTED, browser-tested | Symptom-first entry plus draw/room/single-pass modes; `ops/tests/test_quest_flow.py` and siblings drive the real flow in headless Chromium end to end |
| Quest completion | IMPLEMENTED, browser-tested | Victory conditions, Keep screen (photo record), back-button and full-completion edge cases all covered by dedicated headless-Chromium tests, several regressions caught and fixed this week (Keep-screen URL leak, Back button, full-completion shortcut) |
| Product discovery | IMPLEMENTED, browser-tested | `shop.html`'s filterable grid: `ops/tests/test_shop_interactive.py` (new this week) drives all 8 real category filters and cross-checks rendered tile counts against the live catalogue, 155 distinct buy links, 0 defects found |
| Cart/checkout | ONE-CLICK STRIPE LINKS | Cart removed 2026-09-08 (was unreachable, no page could add to it); replaced with a per-product Stripe Payment Link. 129 of 130 catalogue SKUs buyable (`ops/check_sellable.py`); Corporate Lean 6S is quote-based by design |
| Purchased content access | WORKING, one real order | The one recorded sale (Whole House Print Pack, 2026-08-21) fulfilled unattended in about 10 minutes per `ROADMAP-2026-2029.md`. No live-production re-check possible this cycle (no Stripe credential, no egress) |
| Mobile experience | AUDITED, browser-tested | `ops/audit_visual.py --all --mobile`: 0 pages scrolling sideways (last real defect fixed 2026-09-18), touch-target and badge-contrast gates in `preflight.py`, 5 mobile `npm test` suites passing |
| Accessibility | AUDITED, browser-tested | `ops/audit_visual.py`: 0 contrast/heading/landmark findings across 190+ pages after the CSS-`opacity`-aware contrast fix (A6); semantic landmarks wired by `wire_landmarks` on every generated page |

---

# 9. Business Metrics

Owner: `analytics-intelligence`

The values below must come from authoritative sources.

Do not manually estimate them.

**No live Stripe, Umami or Search Console credential exists in this operator
sandbox.** The revenue and order figures below are the one measurement
recorded in `ROADMAP-2026-2029.md`, not a live pull, and will not update again
until a session has real Stripe read access. **Corrected 2026-09-02:** Sessions
and organic sessions are no longer UNKNOWN. The Umami API token is expired
(401 on every route), but Phil's own session read the analytics database
directly on 2026-09-02 and recorded real numbers in `GOALS.md`, which is now
the authoritative source for these two rows. That was a one-time manual pull,
not a wired live feed: this sandbox still cannot refresh it, so treat it as
current as of 2026-09-02 and re-pull by the same means when it goes stale.
Everything else genuinely has no measurement source yet and stays UNKNOWN
rather than being estimated.

| Metric | Current | Period | Confidence |
|---|---:|---|---|
| Revenue | $19 gross / $18.15 net | MTD (Aug 2026) | MEASURED, one transaction, 2026-08-21, recorded manually in `ROADMAP-2026-2029.md`, not a live Stripe pull |
| Revenue | $0 | Last 30 days | MEASURED 2026-09-20 (`f32c0d8c`), direct Stripe charge-list read: the single 2026-08-21 sale fell out of the trailing 30-day window on 2026-09-20 with no second sale since. This row read "$19 ... Same single transaction" for 30 days after that sale and was never updated when the window rolled past it; corrected here to match GOALS.md section 1's own "Trailing-30-day revenue is now $0" (`f32c0d8c`). |
| Orders | 1 (20 checkout sessions started, 19 expired, 7 of those quoted a phantom $18 duplicate price archived 2026-09-06) | Since launch | MEASURED, same source |
| Average Order Value | UNKNOWN | Last 30 days | UNKNOWN |
| Refunds | UNKNOWN | Last 30 days | UNKNOWN |
| Sessions | 49 | Last 30 days | MEASURED 2026-10-02 (visitors; 121 visits, 719 pageviews), direct Umami database read over ssh, filtered to this site's website_id. Flat on the 48/119/731 of three days earlier; late-August days leaving the window explains part of the earlier slide. An unfiltered read on 2026-09-29 said 239: this Umami instance serves three sites, and `ops/experiments.py` now refuses that query shape. The 7 Sept automated session (431 pageviews) is long out of the window, so this figure is very nearly all human; previous 48 (09-29), 57 (09-25), 68 (09-23), 76 (09-21), 78 (09-17), 75 (09-14) |
| Sessions | 7 | Last 7 days | Human-plausible, same source, 2026-09-29. Recorded 14 visitors / 18 visits / 50 pageviews, but 30 pageviews and 9 visitor ids landed between 18:00 and 18:20 on 27 September, all direct, across four operating systems, a signature that also appears late on 23 August. Ex-burst: 7 visitors, 9 visits, 20 pageviews, DOWN on 12 / 14 / 27. **A first draft of this row today called it the first rise on every measure; checking where the pageviews came from withdrew that** |
| Organic sessions | 6 visits from 5 visitors, whole life of the site, re-measured 2026-10-02 (1 Bing, 21 August; 5 Google visits from 4 visitors, 4 September to 1 October) | Direct Umami database read, not carried forward. The number moved for the first time in three weeks: one more Google visitor, most recent organic arrival now 1 October rather than 18 September |
| Assessment starts | UNKNOWN | Last 30 days | UNKNOWN |
| Assessment completions | UNKNOWN | Last 30 days | UNKNOWN |
| Quest starts | UNKNOWN | Last 30 days | UNKNOWN |
| Quest completions | UNKNOWN | Last 30 days | UNKNOWN |
| Product views | UNKNOWN | Last 30 days | UNKNOWN |
| Checkout starts | UNKNOWN | Last 30 days | UNKNOWN |
| Purchase conversion | UNKNOWN | Last 30 days | UNKNOWN |
| Repeat purchase | UNKNOWN | Appropriate cohort | UNKNOWN |

Metric definitions belong in `METRICS.md`.

Data authority belongs in `DATA-SOURCES.md`.

---

# 10. Search / Discovery Status

Owner: `seo-aeo`

Supporting:

- `content-editor`
- `analytics-intelligence`

**Corrected 2026-09-20, scheduled operator cycle.** This table had stood as
an unfilled bootstrap template, every row UNKNOWN, even though most rows are
directly checkable from the repository or from evidence already measured
and cited in `GOALS.md`. Filled with what this cycle could verify directly;
a row stays UNKNOWN only where the real answer needs a credential
(Search Console) this sandbox does not hold.

| Metric / Area | Status | Notes |
|---|---|---|
| Search Console connected | NO | No `google-site-verification` meta tag or file on the live homepage/repository; confirmed by grep this cycle. Owner gate: `OWNER-ACTIONS.md` item 2, a 3-minute paste from Phil. Every day unverified is gone permanently, no backfill |
| Indexed pages | UNKNOWN | Needs Search Console. The one indirect signal we have is crawl activity, not indexing: `GOALS.md` recorded Googlebot fetching the site 178 times in 72 hours (2026-09-05), 171 answered 200 |
| Indexed pages, partial direct evidence | AT LEAST 10 URLs are in Bing's index, measured 2026-09-20 | Search Console is still the only authoritative source and is still owner-gated, but Bing's RSS results endpoint (`/search?format=rss&q=site:6s-success.com`) answers without any credential. It returns: `/`, `/about.html`, `/method.html`, `/consulting.html`, `/contact.html`, `/resources.html`, `/articles/`, `/articles/how-long-does-it-take-to-organise-a-room.html`, `/rooms/home-office`, `/rooms/kitchen`. So room pages and at least one article are indexed. **No zone page appeared, and that is NOT evidence they are missing**: pagination (`first=`), path filters (`site:domain/zones`) and exact-phrase queries all returned nothing through this endpoint *including for control pages known to be indexed*, so the endpoint simply cannot answer those questions. Bing's own result counts contradicted themselves ("About 4,100" then "About 50" for the same query minutes apart) and are unusable. The indexed article is the `.html` form, which has 301'd to its extensionless canonical since 2026-09-17, so that duplicate should consolidate on its own. `ops/crawl_report.py` is now the better instrument for this question and needs only days of log to accumulate |
| Crawl activity, measurable at all | YES, and further back than this row first claimed | **Corrected the same day:** this row first said crawl history began 2026-09-20. It did not. Nginx Proxy Manager keeps its own access log in front of this site, it survives container recreation, it is rotated with archives, and it reaches back to **2026-08-19 (181,847 lines)**. `LEARNINGS.md` LRN-0010 had already used it on 2026-09-14. It also keeps client IPs, so a Googlebot claim can be reverse-DNS checked, which the new log cannot support by design. What was true is the narrower statement: the site container's own log went only to stdout, so it lived in `docker logs` and every deploy destroyed it. Checked that day: the container had restarted an hour earlier and the site's entire crawl history was 61 requests. It is now also written to a bind-mounted file that outlives the container (`/var/log/6s-success/access.log`, rotated weekly, **no IP addresses recorded**) and read by `ops/crawl_report.py`. **This starts history, it does not recover any**: everything before 2026-09-20 is gone and no figure for it can be produced. A user agent is also a claim, not an identity, so counts are "fetches by something calling itself Googlebot" |
| Search impressions | UNKNOWN | Needs Search Console |
| Search clicks | UNKNOWN | Needs Search Console |
| Organic CTR | UNKNOWN | Needs Search Console |
| Top queries | UNKNOWN | Needs Search Console |
| Top landing pages | PARTIALLY KNOWN | From Umami, not Search Console: of Google's 6 landing pageviews ever, 4 landed on `/standards.html`, 2 on the home page (measured 2026-09-14, reconfirmed 2026-09-17). The Standards Pack is the one page organic search currently sends anyone to |
| Technical SEO health | GOOD, measured this cycle | `ops/check_urls.py`: all 188 sitemap URLs resolve to a real file. `ops/audit_pages.py`: 191 pages audited, 0 duplicate titles, 0 duplicate descriptions, 0 findings |
| Structured data health | GOOD, measured this cycle | All 114 zone pages carry both FAQPage and HowTo JSON-LD (grep-confirmed). `gate_zone_name_consistency` and `gate_no_duplicate_hazard_labels` in `ops/preflight.py` protect against two real past defects (a doubled "The" in HowTo names; two distinct hazards sharing one FAQ question) already found and fixed |
| Sitemap health | GOOD | 188 URLs; `gate_sitemap_lastmod_current` (built 2026-09-19) ties each URL's lastmod to a real content hash rather than letting it go stale or over-fire on a shared-asset change |
| Internal-link architecture | GOOD, measured this cycle | `ops/link_graph_report.py`: 0 orphans across 114 zone, 20 room and 29 article pages; `resources.html` links directly to all 114 zone and 20 room pages |
| Room search architecture | LIVE | 20 room pages, avg 28.8 inbound content links each (min 26, max 31), 0 orphans, 0 dead ends |
| Micro-zone search architecture | LIVE | 114 zone pages, each with visible FAQ, HowTo/FAQPage JSON-LD, a hazard block and a kit disclosure |
| AEO/direct-answer coverage | PARTIAL, measured this cycle | `site/llms.txt` exists and names every promoted free asset (gated by `gate_llms_txt_current`). Visible `<dl>` FAQ blocks render on all 114 zone pages, not JSON-LD only. `GOALS.md` confirms ClaudeBot (20 fetches) and GPTBot (10 fetches) already crawl the site directly in one 72-hour window (measured 2026-09-05) |

Do not create mass content until the existing site and search state are understood.

---

# 11. Commerce Status

Owner: `commerce-manager`

Supporting:

- `cro-growth`
- `analytics-intelligence`
- `product-manager`
- `security-auditor`

| Area | Status | Notes |
|---|---|---|
| Commerce platform | LARGELY LIVE | 129 of 130 catalog items take a card directly through a Stripe Payment Link, real downloads for free ones. Corporate Lean 6S is priced-per-engagement by design, not gapless: `site/corporate.html` (Phil, commit `9e7b1cd1`, 2026-09-03) gives it a qualified-enquiry buy path ending in a written scope and fixed fee, deliberately with no self-serve checkout since two engagements with the same headcount can be very different weeks of work. This row still read "no buy path" as of 2026-09-05, corrected here 2026-09-06 after `GOALS.md` and `REVENUE-REVIEW-2026-09-04.md` were found with the same stale claim. Catalog widened from 10 to 159 SKUs on 2026-08-27 when Phil wired the 149 generated zone/room/kit/bundle packs to live Stripe products himself (commit `b10a278`, backlog 5.7); narrowed to 138 on 2026-09-22 when `147179c6` retired the 6 Area Bundles and 15 Situation Kits (D-023), and to 130 on 2026-09-23 when D-024 retired the 7 Kitchen zone packs and the Kitchen room pack. |
| Payment provider | LIVE | Stripe, acct_1U5rDs6OlZmKL8mF, charges and payouts enabled since 2026-08-19. One real transaction cleared 2026-08-21 ($19, $18.15 net), a personal referral, not a stranger. MCP connection is read only; writes go through reviewed scripts (`ops/stripe_catalog.py`, `ops/stripe_setup.py`, `ops/stripe_links.py`). |
| Checkout health | UNVERIFIED THIS SESSION | `buy.stripe.com` is unreachable from this operator session's sandboxed network (still http_code 000 on re-test 2026-08-27), though issue #22 was closed 2026-08-25 after Phil's own session reached the live site directly. Egress is inconsistent across sessions, not uniformly fixed. One real order completing on 2026-08-21 is the strongest evidence checkout works end to end. |
| Product catalog | 129 of 130 SKUs buyable | Corporate Lean 6S is quote-per-engagement, not gapless: see the commerce platform row above. Card decks (issue #20) closed 2026-09-15: one free 88-card deck, no paid tier, pending sales evidence, not an open decision. See `6S_SUCCESS_PRODUCT-CATALOG.md` and `PRODUCT-CATALOG.md`. |
| Digital fulfillment | WORKING | The one recorded sale (Whole House Print Pack) fulfilled unattended in about ten minutes per `ROADMAP-2026-2029.md`. |
| Physical fulfillment | N/A | Nothing physical is sold; consulting is a service |
| Pricing source of truth | `site/assets/js/data.js` (`window.CATALOG`), asserted against Stripe by `ops/stripe_catalog.py --apply` | Run after any price or product change |
| Tax handling | UNKNOWN | Identify current implementation |
| Refund workflow | DOCUMENTED, UNVERIFIED | `site/terms.html` states a distance-based refund schedule for bookings; no refund has been tested against live Stripe |
| Purchase analytics | 1 order, no repeat | The single 2026-08-21 sale; too small a sample to be more than a coincidence with a percentage sign, per `ROADMAP-2026-2029.md` |
| Product margin data | UNKNOWN | Establish if applicable |

Payment recipient changes remain RED.

---

# 12. Product Portfolio Status

Current strategic product concepts may include:

- Entryway digital deck
- Entryway physical deck
- room decks
- micro-zone mini decks
- digital quests
- printable resources
- labels / visual controls
- room reset kits
- organization components
- Gridfinity / 3D-printed modules
- premium digital functionality
- services

These are **concept/product-family context**, not proof that every item is live.

`PRODUCT-CATALOG.md` must distinguish:

- concept
- prototype
- beta
- active
- paused
- retired

Do not market a concept as an available product.

---

# 13. Content Portfolio Status

Known strategic content architecture includes:

**Home**
→ **Rooms**
→ **Micro-Zones**
→ **Desired Functions**
→ **Root Causes**
→ **6S Activities**
→ **Quests**
→ **Standards**
→ **Products / Kits**
→ **Sustainment**

**Corrected 2026-09-20, scheduled operator cycle.** Coverage is not
uniformly UNKNOWN; the counts below are measured directly from the
committed corpus this cycle.

| Layer | Coverage | Notes |
|---|---|---|
| Rooms | 20 of 20 pages live | 0 orphans, `ops/link_graph_report.py` |
| Micro-zones | 114 of 114 pages live | Every zone carries the six 6S passes, a visible FAQ block, and hazard guidance |
| Desired functions / root causes | 114 of 114 zones have authored diagnosis depth | **Corrected 2026-09-29, PM check-in:** this row still said 12 of 114 (Kitchen 7 + Entryway 5), the 2026-09-07 pilot figure. B9's room-deck build authored a full diagnosis layer for every remaining zone as a side effect of building all 20 room decks; confirmed live, `content.json` carries a non-empty `diagnosis` for 114 of 114 zones and all 114 real `site/zones/*.html` pages render the block, matching `gate_diagnosis_rendered`. See the same correction on the Root-cause guidance row above |
| Quests | Live app (`quest.html`) plus 684-card Whole House Print Pack | Symptom-first entry covers 5 of 114 zones; the rest enter by room or a full-house draw |
| Standards | Standards Pack (free, 20 pages) | The one page organic search currently lands anyone on |
| Products / kits | 129 of 130 catalogue SKUs buyable via direct Stripe checkout | Corporate Lean 6S is quote-based by design, not a gap |
| Free decks | All 20 rooms, free and ungated | **Corrected 2026-09-29, PM check-in:** this row still named only Entryway and Kitchen, the state before B9 shipped the other 18 room decks (`site/*-deck.html`, confirmed 20 files on disk; `python ops/b9_claims.py --status` reports zero rooms left undiagnosed). Card counts vary by room's own real corpus size rather than a fixed budget; see `BACKLOG-2026-09-07.md` B9 for the per-room detail |
| Articles | 29 published, differentiated per zone (`gate_general_reading_differentiated`) | 0 orphans, avg 26.7 inbound links each |
| Sustainment | Rewritten across all 114 zones | Median 28 to 94 words per Sustain slot, 0 near-duplicate across the corpus |

`CONTENT-CATALOG.md` should become the authoritative content inventory.

---

# 14. Active Major Workstreams

WIP limit from `CLAUDE.md`:

**Maximum 3 major active workstreams unless deliberately changed.**

The bootstrap-era workstreams below (governance foundation, GitHub/production
control plane, data visibility) closed out over 2026-08-16 through 08-24: all
required operating documents exist, `ops/dashboard.py` generates
`EXECUTIVE-DASHBOARD-LIVE.md` from measured state, and the site is deployed
and was verified live. Every item in `BACKLOG-2026-H2.md` epics 1 through 5
is still blocked on Phil, a decision issue, or a missing credential (see
section 21), and that file's own epic 6 (keep the operation honest) is where
most per-cycle work happened through 2026-09-06.

**Corrected 2026-09-07, this operator.** Phil gave a direct new instruction
(expand the micro zone model, the decks, and the app; recorded verbatim in
`PLAN-MICROZONES-DECKS-APP.md`) and `BACKLOG-2026-09-07.md` reprioritised the
whole queue around it, superseding `BACKLOG-2026-H2.md`'s ordering (that
file's process rules still hold). This is real, currently unblocked work, not
the absence this section described as of 2026-08-24; see Workstream 3 below.

## Workstream 1: Prove a stranger converts (Horizon 1, per `ROADMAP-2026-2029.md`)

**Status:** BLOCKED, not yet startable  
**Owner:** operator, gated by Phil on backlog items 1.2 and 2.1  
**Objective:** Answer whether the funnel converts anyone who was not
personally told about the site by Phil, per the roadmap's kill criterion
(fewer than 500 organic visits/month and nothing further has sold beyond
the single $19 of 2026-08-21, by August 2027).

EXP-001 is answered (permanently AMBIGUOUS, backlog 1.3). Blocked on: a
Umami share URL or API key (1.2), so EXP-002 and future funnel reads do not
depend on Phil re-pulling the database by hand each time.

---

## Workstream 2: Local demand test for service SKUs (Epic 3B)

**Status:** BLOCKED, awaiting a spending decision  
**Owner:** Phil approves, operator executes  
**Objective:** Test whether the In-Home Reset Day / Virtual Home Consult SKUs
have real non-referral demand, since they are the only route to $20,000 that
does not require quarter-million-visitor traffic.

Blocked on: 3B.1, a capped budget and stop date, correctly RED per `CLAUDE.md`
(material spending).

---

## Workstream 3: The diagnostic layer, Sustain depth, and the Kitchen deck

**Status:** CLOSED, 2026-10-03, PM check-in. Opened 2026-09-07. Every item is
now done, dropped, or genuinely gated on Phil: M1-M5, A1-A18, B1-B9 and C1-C4/C7
all shipped (see the "Done"/strikethrough rows throughout this section and
`BACKLOG-2026-09-07.md` sections 2-4). M6 stays shut per `DECISIONS.md` D-021/
D-026 (needs real zone entrances or a Search Console read, neither true yet).
S1-S4 (the structured `sustain_detail` schema) are DROPPED, not merely
deferred: see `DECISIONS.md` D-029, recorded this cycle, closing the open
question this section itself raised on 2026-09-09 and nobody had revisited
since. C5/C6 stay on Phil (Gemini billing, YouTube OAuth). This closure frees
a WIP slot under `CLAUDE.md` section 18's limit of 3; no replacement
workstream is opened here, since nothing in the current backlog is both
unblocked and workstream-sized (`BACKLOG-2026-09-07.md` section 7).  
**Owner:** operator, direction from Phil  
**Objective:** `PLAN-MICROZONES-DECKS-APP.md` + `BACKLOG-2026-09-07.md`
section 2/3: build the root-cause diagnostic layer the product currently
lacks (0 of 114 zones map a root cause), fix the app's first thirty seconds,
and ship the free unillustrated Kitchen deck.

**Archived 2026-10-24, scheduled operator, by `ops/rotate_status_workstreams.py --apply`:** the dated build-log narrative that used to sit here (2026-09-07 through 2026-09-25, M1 through B9, the full account of how this workstream reached the closure above) moved verbatim to `STATUS-ARCHIVE.md`. The closure summary above is the current, live statement; nothing below it was left unresolved.


---

# 15. Current Experiments

No experiment should be treated as active until its implementation and measurement are verified.

| Experiment | Status | Owner | Primary Metric |
|---|---|---|---|
| None verified in this status file | NONE VERIFIED | - | - |

Active experiments should also be tracked in `EXPERIMENTS.md`.

---

# 16. Current Incidents

**Corrected 2026-10-02, PM check-in.** This section had stood as the unfilled
bootstrap template while a real, ongoing incident sat tracked only in GitHub
issue #37 and `OWNER-ACTIONS.md`.

## INCIDENT-001: fulfil-orders.yml fails every run, paid orders not delivered (RESOLVED)

- **Severity:** P0.
- **Start:** 2026-10-02, ~09:12 UTC. A live-write guard added in `044863b9c`
  did not account for this workflow, the one caller designed to run
  unattended against a live Stripe key.
- **Impact while open:** every scheduled and push-triggered run of
  `fulfil-orders.yml` failed at the "Deliver" step. Any customer who paid
  while this stood received nothing until the fix landed. Open roughly
  6h50m, 09:12 to 16:01:47 UTC.
- **Resolved 2026-10-02 16:01:47 UTC, by Phil directly**, commit `295b1c642`,
  adding `STRIPE_ALLOW_LIVE: "1"` to the Deliver step's `env:`, the exact
  fix five push notifications had already named. GitHub issue #37 closed
  the same moment, `state_reason: completed`.
- **Verified, not assumed, against the Actions API directly (this PM
  check-in, 16:4x cycle):** six consecutive `fulfil-orders.yml` runs since
  the fix (#3054 through #3059) all completed `success`, most recently at
  16:47:18 UTC.
- **Mitigation during the outage:** none available from inside a sandboxed
  session; no order was lost, Stripe kept recording them, delivery was only
  delayed.
- **Follow-up closed:** `OWNER-ACTIONS.md`'s item 0a (the owner-action this
  incident generated) was still telling Phil to make a fix he had already
  made; closed into that file's "Resolved today" table as R5, 2026-10-02
  16:2x PM check-in.

Historical account, superseded by the resolution above, kept for the
record: the one-line fix was written and reverted twice by two different
autonomous sessions, each time correctly held by this environment's own
safety classifier as a payment-safety change requiring a human
(`CLAUDE.md` 37/52). That was correct, conservative behavior, not a bug to
route around, which is why the fix waited for Phil rather than an agent
finding a way around the block.

## INCIDENT-002: autonomous PM/operator routines stalled 5 days on a usage limit, surfaced only by this cycle checking commit authorship against trigger state (STALL NOT RECURRING)

- **Severity:** P0 (process, not product: nothing customer-facing broke).
- **Start:** sometime shortly after 2026-10-04 11:19:40Z (the last Claude-authored commit, `c2565f114`).
- **End:** by 2026-10-09 03:2x UTC, the PM check-in that surfaced this incident (`:10` slot) itself ran without issue, meaning the stall had already lifted by the time it was found. **Re-verified this cycle (2026-10-09, PM check-in, `:10` slot, 09:11 UTC) via `list_triggers` directly:** the `:40` PM Routine's last run `SUCCEEDED` (08:40 to 08:47 UTC) and the `:43` hourly operator's last run `SUCCEEDED` (08:43 to 09:00 UTC), no `FAILED` on either since the stall ended, and `git log` shows continuous Claude-authored commits every cycle in between. Whether this was Phil acting, the limit resetting on its own, or the account moving past it cannot be told from here, and issue #40 stays open for that reason: the account-level cause was never confirmed, only that its symptom has not recurred for roughly 6 hours of continuous operation since.
- **Found:** 2026-10-09, PM check-in (:10 slot). `git log --since="2026-10-04T11:21:00Z"` returns 36 commits, every one authored by `github-actions` (the hourly check-in and social-draft-rotation bots, which run without an agent). Cross-checked against `list_triggers`: the :40 PM twin and the :43 hourly operator both show `last_run.status: FAILED`, `failure_reason: USAGE_LIMIT_REACHED`, fired `2026-10-09T02:40:34Z` and `2026-10-09T02:44:02Z`. This session's own :10 slot ran without issue.
- **Impact:** roughly 5 days with zero autonomous PM or operator work: no measurement, no backlog progress, no verification. `CHECKIN-LOG.md`'s hourly entries kept landing throughout, which made the repository look attended when it was not; that gap is itself worth remembering; a check that only reads the bot's own log cannot distinguish a live operation from a stalled one sitting next to a dumb heartbeat.
- **Not customer-facing:** `preflight.py` (run this cycle) shows 0 FAIL through every gate reachable in this sandbox (stalls at the documented `gate_tests` headless-Chromium sandbox hang, same as prior cycles, confirmed genuinely stalled by flat CPU time before killing it). The 8 open GitHub issues are unchanged, all `decision`/`blocked-on-art`, already waiting on Phil.
- **Cannot be fixed from here:** the usage limit is an account/plan-level setting outside this sandbox's visibility or control. Filed as **GitHub issue #40** (`decision`), with the evidence above and a recommendation to check the Claude Code usage/plan status, since three Routines firing every 30 to 60 minutes is real concurrent load.
- **Mitigation:** none available; the next PM or operator cycle that runs should check `list_triggers` for `last_run.status == FAILED` as a matter of course, rather than relying on a cold commit-authorship read to notice a stall, which is how this one was found.

## INCIDENT-003: checks.yml push trigger stopped firing for 3h09m / 24 commits, manual dispatch still works (RESOLVED: transient, self-recovered, no gate failure)

- **Severity:** P0 (process). `checks.yml` is the only workflow that runs `ops/preflight.py`, every quality gate, and the checks that watch revenue.
- **Found:** 2026-10-11, PM check-in (15:1x slot). Last push-triggered run was #2034 (commit `9eafaaa3`, completed 11:46:01Z). 24 commits landed after that, several touching paths the workflow's own `on.push.paths` includes and does not exclude (`CHECKIN-LOG.md`, `ops/corpus-rotation.json`, `ops/last-brief-sent.json`, `ops/state-checkin.json`), none triggered a run. The workflow file itself is unchanged (`git diff 9eafaaa38 HEAD -- .github/workflows/checks.yml` empty) and the API reports it `"state":"active"`.
- **Ruled out:** a repo-wide Actions outage or a disabled workflow. Every other scheduled workflow (`hourly-brief.yml`, `linkedin-drafts.yml`, `bluesky-drafts.yml`, `social-drafts.yml`, `fulfil-orders.yml`) ran normally on the same pushes, most recently on `ddc47e62e` at 14:55Z.
- **Confirmed still functional:** manually dispatched via `workflow_dispatch`, run #2035 (`.../actions/runs/38151102383`), queued and reached `in_progress` immediately. So this is the push trigger specifically, not the workflow or Actions generally.
- **Impact while open:** no CI coverage of `ops/**`, `build/**`, `content/**`, `.github/workflows/**` or root markdown for 3h09m+. `preflight.py` fast, run locally this cycle, showed 0 failures through every gate reachable before the documented `gate_tests` sandbox hang, so nothing is known to be broken; the gap is in verification, not a confirmed defect.
- **Filed:** GitHub issue #41, not labelled `decision` (no judgment call yet, just needs someone to watch whether it recurs). The next ordinary push (`cfaa7245e`) triggered run #2036 normally, 3 minutes after the manual dispatch (#2035). A third push (`d33d9fe48`) auto-triggered run #2037, no manual dispatch involved. A fourth push (`2a8a1308`) auto-triggered run #2038, also with no manual dispatch. Four consecutive pushes since the gap all triggered normally, with no further gaps.
- **RESOLVED, this operator cycle (15:5x), after watching all four runs to completion rather than citing the "looks recovered" read at 15:4x.** All four (`#2035` dispatch, `#2036`, `#2037`, `#2038` push-triggered) finished with `conclusion: success`, confirmed directly via `gh run view`, not inferred from `in_progress`. That means every gate `preflight.py --deep` runs, including the full `gate_tests` e2e suite this sandbox cannot reach, passed clean on real CI hardware across all four commits. Closing as transient: a GitHub-side delivery gap on the push event for this one workflow, self-resolved, no code or workflow-file change made or needed, no gate failure found. Re-open if the gap recurs; if it does, the next root-cause step is Settings -> Actions, usage/billing, named in issue #41's original report. GitHub issue #41 closed with this evidence. **Cross-confirmed independently, 16:1x PM check-in**, same four runs read directly, same conclusion reached before either session saw the other's commit.

## INCIDENT-004: checks.yml red and publish-image.yml blocked for ~2h on a stale sitemap lastmod, unseen because every cycle's local preflight hangs before reaching the gate that caught it (RESOLVED)

- **Severity:** P0 (process and deploy traceability). `publish-image.yml`'s failure meant real `site/`-touching content sat built but unpublished.
- **Start:** 2026-10-19T19:00:10Z, commit `0e50c3f27` (the 18:5x cellar/basement synonym fix). It hand-edited `site/articles/how-to-organize-a-basement.html` correctly per `CLAUDE.md` 5b (a hand-authored page, no generator owns it) but never re-ran `ops/build_seo.py`, so `site/sitemap.xml`'s `<lastmod>` for that one URL stayed at `2026-10-14` while the file itself changed.
- **Impact while open:** `gate_sitemap_lastmod_current` and its matching test correctly FAILED `checks.yml` on every push since (`759c43f85`, `a7498109b`, `7c630782e`); `gate_publish_image_current` correctly FAILED `publish-image.yml` the same way, so no `site/`-touching change landed on production from `3d84199d` (2026-10-15) onward. **Not customer-facing in a way this sandbox could confirm or rule out:** no egress to 6s-success.com from here, same standing wall every cycle records.
- **Found:** 2026-10-19, scheduled operator cycle, ~20:51Z, by reading the actual `checks.yml`/`publish-image.yml` job logs directly rather than citing the last several `ops/NIGHTLY-LOG.md` entries' own "preflight.py: 0 FAIL through every gate reached before the `gate_tests` sandbox hang" framing. Both failing gates are ordered after `gate_tests` in `preflight.py`'s call order; `gate_tests` hangs in every sandbox this project has run in, so no local run had ever reached either gate, and nobody had separately pulled the CI conclusion for roughly 2 hours across at least 4 cycles.
- **Resolved, same cycle, commit `0fb7273b1`:** ran the owning generator, `ops/build_seo.py` (not a hand edit), moving the stale `<lastmod>` to `2026-10-19`. Verified directly: `gate_sitemap_lastmod_current()` clean, `test_gate_sitemap_lastmod_current.py` 6/6, `check_urls.py` 213/213, `audit_pages.py` 0/0, `affiliate.py --check` 165 documents, `fix_dashes.py --check` 0/0. Watching `checks.yml`/`publish-image.yml` on this push to confirm green and the backlog of unpublished content clearing; not yet confirmed at the time this entry was written (CI still `in_progress`).
- **Gate added, same cycle, so this class cannot recur silently:** `gate_ci_conclusion_current`, called in `preflight.py` before `gate_tests` so the sandbox hang cannot hide it, hard-FAILs on a red `checks.yml` rather than the warn `gate_workflows_healthy` already gives (same escalation `gate_money_critical_workflows` makes for a broken delivery pipeline). `ops/tests/test_gate_ci_conclusion_current.py`, 5 cases, fail-then-pass proved against real live GitHub data, not only a mock.
- **Same shape as a prior incident, 2026-10-15** ("Fix the 9 CI gate failures the Photos API frontend shipped, unnoticed across 3 pushes"), whose own commit message named this exact gap and recommended relying on CI when `gate_tests` hangs. That was prose, not a gate, and it recurred 4 days later exactly as `CLAUDE.md` step 10b warns an un-gated lesson will.
- **Fully confirmed RESOLVED, same cycle, after the fix revealed a second, smaller instance of its own root cause.** The sitemap fix (`0fb7273b1`) itself changed `site/`'s content hash without re-running `ops/build_id.py`, so `site/build-id.txt` went stale and `publish-image.yml` correctly failed again on `6cbce91b2`/`e39e62320` at its "Refuse to publish a stale build id" guard, before preflight even ran. Fixed the same way, by running the owning generator (`6d2bc368d`). Watched that run to completion via the Actions API rather than inferring from `in_progress`: `publish-image.yml` on `6d2bc368d` finished `conclusion: success` at 2026-10-19T21:22:54Z, the first fully green run since `3d84199d` on 2026-10-15. Total window 19:00:10Z to 21:22:54Z, roughly 2h23m.

Historical incidents belong in `INCIDENTS.md`.

---

# 17. Current Blockers

**Corrected 2026-09-20, scheduled operator cycle.** This section had stood
as the unfilled 2026-08-16 bootstrap template naming three blockers as not
yet started; two of the three have since been substantively resolved and
the third is narrower than originally stated. Updated against real,
currently-checkable state rather than left to describe a moment 5 weeks
past.

## BLOCKER-001: Production State Verifiable Only From a Session With Real Access

**WIDENED 2026-10-29, scheduled operator cycle: the 6-commit gap above is now 8, re-derived directly with `deploy_gap_material_commits('ad933f9e5')` against real current `HEAD`, not cited.** `ops/deploy-verdict.json` unchanged: build `a0bbe5bb276ee21b`, `checked_at: 2026-10-26T16:51:56Z`. Two commits landed after the 16:5x entry above and were never folded in: `41938dd0` (A30, the loft/attic FAQ naming gap) and `b6e9115a5` (the same-slot fix for `feed.xml`/`sitemap.xml` never having been rebuilt after A30's own edit). Undeployed: `840f3e11b`, `ba69e8d0f`, `ea437edc0`, `f9c97f72f` (restamp), `2404a870c`, `c79829238`, `41938dd0`, `b6e9115a5`; 8 commits, 6 of them content (the restamp and the feed/sitemap rebuild are mechanical). No P0 regression: already-correct content and fixes sitting undeployed, nothing broken live. `gate_status_deploy_gap_count_current` confirmed this live before the fix (warned "6 ... but a fresh count ... is 8") and confirmed silent after. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

## BLOCKER-002: Live Business Data Established, Not Yet a Live Feed

**Status: PARTIALLY RESOLVED.** Real business data exists and is current:
`GOALS.md` and section 9 above carry a measured revenue, session and
organic-search baseline (last direct database pull 2026-09-17). What
remains missing is a wired, credential-free live feed: no Stripe, Umami
API, or Search Console credential exists in any operator sandbox, so every
number here is a manual pull re-run periodically, not a continuously
refreshing one.

Impact:

Claude cannot responsibly optimize toward revenue/customer metrics without trusted measurement.

Owners:

- `analytics-intelligence`
- `commerce-manager`
- `seo-aeo`

Resolution:

Metric definitions (`METRICS.md`) and the data-source map (`DATA-SOURCES.md`)
are both written. Connecting authoritative live sources needs a credential
only Phil holds (Umami share URL or API key, `OWNER-ACTIONS.md` item 1.2;
Search Console token, item 2).

---

## BLOCKER-003: Executive Dashboard Established

**Status: RESOLVED.** `DASHBOARD.md`, `METRICS.md` and `DATA-SOURCES.md`
all exist; `ops/dashboard.py` regenerates `EXECUTIVE-DASHBOARD-LIVE.md`
from measured state on every cycle (confirmed regenerated this cycle,
2026-09-20 11:48). This blocker was flagged as contradicted by a same-day
PM check-in (2026-09-20 10:40) but never itself corrected until now.

Impact (historical):

Owner lacked one trusted near-real-time view of business, product, growth, and production.

Owners:

- `analytics-intelligence`
- `6s-ceo`

Resolution: done.

---

# 18. Known Risks

## RISK-001: Autonomous Action Without Verified State

**Severity:** HIGH  
**Status:** OPEN

Risk:

Agents may modify systems based on assumptions.

Control:

Read current state and inspect actual systems before meaningful production action.

---

## RISK-002: Production / GitHub Drift

**Severity:** HIGH UNTIL VERIFIED  
**Status:** OPEN

Risk:

Production may not match repository configuration.

Control:

Map deployed commit/image/configuration to GitHub.

---

## RISK-003: Unknown Backup / Restore Readiness

**Severity:** HIGH UNTIL VERIFIED  
**Status:** OPEN

Risk:

Production data may not be recoverable.

Control:

Inventory persistent data, backup mechanism, off-host copy, and restore procedure.

---

## RISK-004: Optimization Without Trusted Metrics

**Severity:** MEDIUM-HIGH  
**Status:** PARTIALLY CONTROLLED, corrected 2026-09-20

Risk:

Autonomous agents may optimize vanity or incorrectly calculated metrics.

Control:

`METRICS.md` and `DATA-SOURCES.md` are both written and in use (this file's
own section 9 and `GOALS.md` cite them). The residual risk is narrower than
originally stated: it is that a metric's authoritative source goes stale
between the manual pulls a missing live credential still forces, not that
no definition or source map exists. `GOALS.md`'s own opening line already
names this as the standard to hold every baseline to.

---

# 19. Pending RED Decisions

None currently recorded.

If a RED action requires owner approval, record it here:

## RED-XXX

**Requested Action:**  
**Reason:**  
**Evidence:**  
**Risk:**  
**Recovery:**  
**Alternatives:**  
**Approval Status:** PENDING

Do not clutter this section with routine YELLOW coordination.

---

# 20. Recently Completed Meaningful Work

## Autonomous Governance Foundation

Completed:

- master `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`

## Agent Architecture

Completed or updated:

- `github-manager`
- `vps-docker-manager`
- `devops-sre`

Additional specialist agents may already exist in the repository and should be inventoried rather than assumed.

---

# 21. Highest-Priority Next Actions

All required operating documents in `CLAUDE.md` section 56 now exist on disk;
the P1 through P6 "create the missing document" actions this section used to
list are done and have been removed. **Corrected 2026-09-08:** the
authoritative queue is now `BACKLOG-2026-09-07.md`, Phil's own reprioritisation
toward micro zones, decks and image/video work, which explicitly supersedes
the ordering (not the process rules) in `BACKLOG-2026-H2.md`. The P1 through P6
Phil-gated items below, carried from the 2026-09-02 review, were individually
re-checked against the 9 open GitHub issues this cycle and are still open and
still accurate; they are not the whole queue any more. Unblocked
operator-actionable work now lives in `BACKLOG-2026-09-07.md` sections 2
through 4 (app, decks, images/video), not in this list. `OWNER-ACTIONS.md`
remains the standing consolidated list of everything genuinely gated on Phil.
The consolidated list of Phil-gated items:

## P1: Umami read access (backlog 1.1) -- corrected 2026-09-02

Not fully blocked any more. Phil read the analytics database directly on
2026-09-02 (the API token is expired) and got a real one-time baseline, now
recorded in `GOALS.md` and above in section 9. What is still open is items
1.2 through 1.4: wiring a share URL or API key into `ops/dashboard.py` so a
credential-less operator session can pull fresh numbers itself, instead of
depending on Phil re-reading the database by hand each time the baseline
goes stale.

Owner: **Phil** for the credential/share-URL; **operator** for the wiring
once it exists.

---

## P2: Decide the Listmonk sending identity (issue #15, P0)

Separate Listmonk instance for 6S Success, or change the shared instance's
global from-address and accept the cost to the other brand it currently
serves (Compassion Benchmark). Blocks email capture entirely; six prospects
already lost with no way to reach them.

Owner: **Phil decides, operator builds**

---

## P3: Publish the ten LinkedIn posts and generate the six tier-0 images (backlog 3.1, 3.3)

Both already drafted/prompted and waiting in Phil's queue. The only traffic
lever available that does not require search compounding time.

Owner: **Phil**

---

## P4: Resolve the routine self-update gap (issue #17), CLOSED 2026-08-25

Phil's own session rewrote the trigger's stored prompt to read
`BACKLOG-2026-H2.md` and the other operating documents directly each cycle,
rather than embedding a status snapshot that only the trigger's creator could
refresh. The self-update limitation still exists as a platform fact, but the
prompt no longer depends on being edited to stay current, so the practical
defect is resolved.

Owner: closed, no further action

---

## P5: Approve a capped local demand test for the service SKUs (backlog 3B.1)

A financial commitment, correctly RED per `CLAUDE.md`. This is the only tested
route to $20,000 that does not require a quarter-million monthly visitors; the
recommendation on file is a few hundred dollars and a hard 90-day stop.

Owner: **Phil**

---

## P6a: Sync the 155-SKU product spine to Stripe (backlog 5.7), CLOSED 2026-08-27

Phil did both halves himself: commit `b10a278` extended `SELLABLE`, ran the
live Stripe sync, and wired the resulting payment links into
`window.CATALOG`. 158 of 159 catalog items are now buyable (only Corporate
Lean 6S is not). A same-day follow-up commit `3e5248c` also fixed
`ops/build_epub.py` reading a hardcoded author placeholder, which had
blocked Amazon KDP submission. `ops/audit_catalog.py` re-verified clean
this cycle against the live 159-SKU set.

Owner: closed, no further action

---

## P6: Stripe business website field still reads Ledgerium (backlog 2.8, issue #21)

Everything else on the account's public identity is already fixed per account
(name, statement descriptor, support email/URL, legal pages, checkout
branding). Only the business website field remains, and Stripe's own safety
check blocked the operator from changing it because it can silently change
the shared legal entity's other account (Ledgerium) too. This has been open
since 2026-08-21 and was on the auto-generated dashboard but missing from
this file and from `BACKLOG-2026-H2.md` until this cycle added it.

Owner: **Phil**

---

# 22. Agent Startup Checklist

Before significant autonomous work:

- [ ] Read `CLAUDE.md`
- [ ] Read `AUTONOMY.md`
- [ ] Read `STATUS.md`
- [ ] Identify owning agent
- [ ] Check active workstreams
- [ ] Check blockers
- [ ] Check risks
- [ ] Inspect real system state when relevant
- [ ] Classify action GREEN / YELLOW / RED
- [ ] Avoid duplicating active work

---

# 23. Status Update Rules

Update this file when any of the following materially changes:

- production health
- deployed release
- active major workstream
- incident state
- major blocker
- material risk
- executive priority
- live data confidence
- GitHub control-plane health
- VPS/Docker health
- backup/restore confidence
- major product launch state

Do not update it for every commit.

---

# 24. How to Update Status

For each changed section:

1. obtain evidence
2. change status
3. add concise evidence/notes
4. update timestamp
5. identify owner if action remains
6. move historical detail to the appropriate long-term file

Do not allow this document to become an archive.

The section 30 "Production Knowledge" chain is rule 6 applied automatically:
`gate_status_production_knowledge_not_oversized` in `ops/preflight.py` warns
once more than the newest entry plus a small buffer has piled up, and
`python ops/rotate_status_history.py --apply` moves the rest into
`STATUS-ARCHIVE.md`, verbatim. Found 2026-10-23 at 37 live entries, never
enforced before that date.

---

# 25. Freshness

Operational status decays quickly.

Agents should treat old status as a hypothesis when the underlying system can be inspected.

For highly dynamic information such as:

- production health
- container health
- current release
- incidents
- active PRs
- traffic
- revenue

prefer live sources over stale Markdown.

Update this summary afterward.

---

# 26. Truth Hierarchy

When this file conflicts with verified live state:

**Verified live state wins.**

Then update this file.

When two live sources conflict:

1. identify authoritative source from `DATA-SOURCES.md`
2. investigate discrepancy
3. report confidence
4. do not fabricate reconciliation

---

# 27. Status Ownership

Each specialist maintains its domain truth.

`github-manager`
→ GitHub/release status

`vps-docker-manager`
→ Hostinger/Docker runtime status

`devops-sre`
→ reliability/incident status

`analytics-intelligence`
→ business/product measurement confidence

`seo-aeo`
→ organic discovery status

`commerce-manager`
→ commerce status

`product-manager`
→ customer/product journey status

`6s-ceo`
→ strategic priority and executive synthesis

---

# 28. Executive Escalation

Surface to the owner when:

- production is RED
- significant customer data is at risk
- payment integrity is at risk
- a RED authorization is required
- recovery capability is materially compromised
- a major strategic decision is blocked
- a material financial/legal commitment is required

Do not escalate routine GREEN work.

---

# 29. Desired Future State

This file should eventually be generated largely from trusted system state.

Target pattern:

**GitHub + VPS + Analytics + Commerce + Search + Product Events**
→ **Metrics / Status Collection**
→ **STATUS.md summary**
→ **Executive Dashboard**
→ **6s-ceo prioritization**
→ **BACKLOG.md**
→ **Autonomous execution**

Human edits should not be required for routine status maintenance.

---

# 30. Current Overall Assessment

**Operating System:** OPERATING, governance and required documents in place

**Governance:** STRONG FOUNDATION

**Autonomous Execution Readiness:** FULL FOR GREEN-BAND WORK. AS OF 2026-09-15, THE AUTHORITATIVE QUEUE IS `BACKLOG-2026-09-07.md`, NOT `BACKLOG-2026-H2.md` (SUPERSEDED ON ORDERING, SECTION 21 ABOVE). SECTIONS 2 THROUGH 6 OF THAT FILE ARE, AS OF THIS DATE, ALL EITHER DONE OR EXPLICITLY GATED ON PHIL (ALL 8 OPEN GITHUB ISSUES CARRY A `P0`, `decision` OR `blocked-on-art` LABEL AS OF 2026-09-18, UP FROM 7 AFTER `#32` AND `#33` WERE OPENED SINCE 2026-09-15). WHEN THAT IS TRUE, THE ESTABLISHED FALLBACK IS A COLD READ OF A LOW-MENTION `ops/*.py` FILE OR HAND-MAINTAINED DOCUMENT, VERIFIED AGAINST THE LIVE OR GENERATED ARTIFACT RATHER THAN TRUSTED ON SIGHT; MOST REAL DEFECTS FOUND THIS MONTH CAME FROM THAT PRACTICE, NOT FROM THE BACKLOG.

**Production Knowledge, WIDENED 2026-10-29, scheduled operator cycle: the 1-commit gap below is now 8, 6 of them content, re-derived directly with `deploy_gap_material_commits('ad933f9e5')` against real current `HEAD`.** Full, current account (the commit list, which two are mechanical) is in `BLOCKER-001`'s own newest entry and the Public website/Production traceability table rows above, rather than restated a third time here; this gate (`status_deploy_verdict_problem`) still only checks that the right build_id appears somewhere in this paragraph, not the commit count inside it, so this prose can still drift stale again until that is widened. Same standing limit: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, REOPENED 2026-10-26, scheduled operator cycle: same reopening as `BLOCKER-001` above, found while re-deriving the gap directly rather than citing the 16:4x closure below.** `deploy_gap_material_commits('ad933f9e5')` against real current `HEAD` (`9aa6700a0`) returns 1 commit: `840f3e11b`, a cold-read-ledger fix (the `build_cleaning_index.py` avif-chain gap and six live British-spelling misses `gate_no_british_spellings_shipped` had not been matching). No P0 regression; full account, and the gate blind spot this reopening also exposed, in `BLOCKER-001`. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, CLOSED 2026-10-26, PM check-in (16:4x slot): the 1-commit gap below closed within the same hour by Phil's own deploy, re-derived directly rather than cited.** Phil deployed the cleaning-content review himself (`b8649e1fc`, 16:51:56Z local session): production build `a0bbe5bb276ee21b`, 130 products, full account of the safety/kit/vocabulary fixes in that commit's own message. `ops/deploy-verdict.json` now records `verdict: "current"`, build `a0bbe5bb276ee21b`, `checked_at: 2026-10-26T16:51:56Z`, resolving via `resolve_verdict_commit` to `ad933f9e5` itself. `deploy_gap_material_commits('ad933f9e5')` re-derived directly against real current `HEAD`, not cited, returns an empty list: production matches `HEAD` exactly, zero commits undeployed. No P0 regression; the cleaning-safety fixes this gap had been holding back are now live. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, REOPENED 2026-10-26, PM check-in (16:1x slot): the zero gap below reopened by 1 commit, material, re-derived directly against real current `HEAD` (`e3b8549f1`) rather than cited.** `ops/deploy-verdict.json` is unchanged, still `verdict: "current"`, build `00187aebb3255957`, `checked_at: 2026-10-26T14:48:46Z`, resolving via `resolve_verdict_commit` to `ce52ccbd5`. `deploy_gap_material_commits('ce52ccbd5')` now returns 1 commit: `ad933f9e5`, Phil's own cleaning-content review (safety fixes, kit corrections, American-vocabulary fold across 222 `site/zones/*.html`/`site/how-to-clean-anything.html` files); `site/build-id.txt` itself confirms it, reading `a0bbe5bb276ee21b`, not the deployed `00187aebb3255957`. The 19 other commits since the verdict are non-material. No P0 regression in what is currently live. Full account in `BLOCKER-001`. Prior state, kept because the shape recurs: **Production Knowledge, CLOSED 2026-10-26, scheduled operator cycle: the gap below had widened further (to 4 commits/2 material, per `BLOCKER-001`'s own 00:4x entry) and is now gone, re-derived directly rather than cited.** Phil's own owner-directed global cycle (section 9's "Latest" entry at the top of this file) deployed and confirmed live: production `00187aebb3255957`, 130 products. `ops/deploy-verdict.json` now records `verdict: "current"`, build `00187aebb3255957`, `checked_at: 2026-10-26T14:48:46Z`, resolving via `resolve_verdict_commit` to `ce52ccbd5`. `deploy_gap_material_commits('ce52ccbd5')` re-derived directly against real current `HEAD` (`267697dcf`), not cited, returns an empty list: production matches `HEAD` exactly, zero commits undeployed. No P0 regression. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, REOPENED 2026-10-23, scheduled operator cycle (21:5x slot): the zero gap below reopened by 2 commits, 1 material, found while regenerating the dashboard.** `ops/deploy-verdict.json` is unchanged, still `verdict: "current"`, build `84c234bd3857ed4c`, `checked_at: 2026-10-23T17:44:18Z`, resolving via `resolve_verdict_commit` to `86159a729`. `deploy_gap_material_commits('86159a729')` re-derived directly against real current `HEAD` (`e0057bdc3`), not cited, returns 2 commits: `d3d824c4c` (a CI/registry fix, not material) and `a24a667c6` (the "airing cupboard" also-called fold, material). No P0 regression: a household synonym added to an existing zone page. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, CLOSED 2026-10-23, PM check-in (17:4x slot): the zero gap below reopened at 17:1x by one real commit, then closed for real by Phil's own owner-directed global cycle (visitor country, international vocabulary, USD pricing), all three verified live.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `84c234bd3857ed4c`, `checked_at: 2026-10-23T17:44:18Z`, resolving via `resolve_verdict_commit` to `86159a729` itself. `deploy_gap_material_commits('86159a729')` re-derived directly against real current `HEAD`, not cited, returns an empty list: production matches `HEAD` exactly, zero commits undeployed. No P0 regression. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, CLOSED 2026-10-23, PM check-in (10:1x slot): the 3-commit, 2-material gap below closed with a real redeploy, caught by direct re-derivation rather than trusting the stale `aa124e45d7f5903f` marker.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `1e15140736f2a808`, `checked_at: 2026-10-23T05:26:39Z`, resolving via `resolve_verdict_commit` to `54375841b`; `deploy_gap_material_commits('54375841b')` returns an empty list: production matches `HEAD` exactly, zero commits undeployed. No P0 regression. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **Production Knowledge, REOPENED 2026-10-23, PM check-in (05:1x slot): the 1-commit gap closed, then reopened again by two more real commits, caught by direct re-derivation rather than trusting the stale `18c8f6d939cbad33` marker.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `aa124e45d7f5903f`, `checked_at: 2026-10-23T03:44:48Z`, resolving via `resolve_verdict_commit` to `a30175fb9`; `deploy_gap_material_commits('a30175fb9')` returns 3 commits, 2 material (`653fe8b55`, the zone page room-plan panel; `63bac2a83`, the articles/index twitter-card fix), `a1aef2ce7` a non-material build-id restamp. No P0 regression: both material commits are already-correct content sitting undeployed, not a broken page. Same standing limit as every entry below: no operator sandbox holds the deploy key; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Prior state, kept because the shape recurs: **REOPENED 2026-10-22, PM check-in (23:1x slot): the zero gap below has reopened by one real commit, caught by direct re-derivation rather than trusting the still-current `18c8f6d939cbad33` marker.** `resolve_verdict_commit('18c8f6d939cbad33')` still resolves to `833401444`; `deploy_gap_material_commits('833401444')` now returns 1 commit, `727a2154d` (the build_product_images.py pagination fix landed one cycle earlier), confirmed by `git show --stat` against `site/`.

**Business Data Knowledge, re-measured 2026-09-29, WIDENED 2026-10-02 (scheduled operator cycle): caught by `gate_goals_traffic_current` on this cycle's own `preflight.py` run, this paragraph was three days stale against `GOALS.md`'s own current baseline.** ONE MEASURED TRANSACTION EVER ($19 GROSS, 2026-08-21, A REFERRAL). CURRENT TRAFFIC BASELINE (`GOALS.md`, MEASURED 2026-10-02 BY A DIRECT UMAMI DATABASE READ, FILTERED TO THIS SITE'S `website_id`): 49 VISITORS ACROSS 121 VISITS AND 719 PAGEVIEWS IN 30 DAYS, FLAT ON THE 48/119/731 OF THREE DAYS EARLIER. THE TRAILING WEEK ROSE FOR THE FIRST TIME IN THREE WEEKS: 22 VISITORS / 29 VISITS / 62 PAGEVIEWS AS RECORDED, 13 VISITORS / 20 VISITS / 32 PAGEVIEWS EXCLUDING ITS OWN BUSIEST 20-MINUTE BUCKET (THE SAME 27 SEPTEMBER SIGNATURE NAMED BELOW), AGAINST 7 EX-BURST THREE DAYS EARLIER. READ HONESTLY THIS COULD BE NOISE ON A SMALL NUMBER, NOT A TREND. AN UNFILTERED READ ON 2026-09-29 SAID 239 VISITORS, BECAUSE THIS UMAMI INSTANCE SERVES THREE SITES; `ops/experiments.py` NOW REFUSES A `website_event` QUERY THAT NAMES NO WEBSITE. IN UMAMI `session_id` IS THE VISITOR AND PERSISTS ACROSS DAYS, THE VISIT IS `visit_id`. BUY-CLICKS: 11 ALL TIME FROM 9 DISTINCT VISITORS (BOOK 4, METHOD 3, CONSULTING 2), OF WHOM ONE EVER PAID. **CORRECTED 2026-09-29: THIS LINE READ "STRANGERS' BUY-CLICKS SINCE 7 SEPT: 0" AND THAT IS NO LONGER TRUE**, THERE ARE CLICKS ON 14 AND 28 SEPTEMBER; `LEARNINGS.md` LRN-0010 WAS RIGHT WHEN WRITTEN AND HAS BEEN OVERTAKEN. THE EMAIL LIST IS READABLE, NOT UNREADABLE, AND MEASURED EMPTY: 0 SUBSCRIBERS (ISSUE #15, STILL UNRESOLVED, BLOCKS CAPTURE ENTIRELY).

**Executive Visibility:** LIVE, VIA `EXECUTIVE-DASHBOARD-LIVE.md` (GENERATED BY `ops/dashboard.py`, NOT HAND-TYPED)

**Immediate Focus:** UNCHANGED IN SUBSTANCE SINCE 2026-09-02, RE-CONFIRMED 2026-09-15: TRAFFIC, NOT ANALYTICS OR TECHNICAL DEBT, IS THE CONSTRAINT (`GOALS.md`). 2.5 VISITORS A DAY. THE CHANNELS THAT COULD CHANGE THAT (VIDEO PLATFORMS, LINKEDIN, PINTEREST, INSTAGRAM) NEED ACCOUNTS ONLY PHIL CAN CREATE (`OWNER-ACTIONS.md`); DISTRIBUTION PREP IS READY AND WAITING (114 ZONES OF VIDEO IN MULTIPLE CUTS, PINTEREST/INSTAGRAM CARDS FOR ALL 114 ZONES, ~4,939 READY-TO-PUBLISH SOCIAL UNITS TOTAL). THE DOMINANT DEFECT CLASS FOUND ACROSS MANY REVIEWS IS A CORRECTED SOURCE WHOSE SHIPPED ARTIFACT WAS NEVER RE-DERIVED (`BACKLOG-2026-09-07.md` SECTION 7). THE HONEST STATE OF THIS BUSINESS IS "COMMERCE WORKS, TRAFFIC IS MEASURED AND NEARLY ALL DIRECT, AND THE NEXT STEP ON EVERY DISTRIBUTION CHANNEL IS PHIL'S OWN ACTION." FOR CURRENT DEPLOY STATUS SEE THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE AND `BLOCKER-001`, NOT THIS LINE: the specific build/commit this line used to cite (2026-10-01, `8fbc6b7d3d2599ae`) went stale within hours and the 27-entry correction chain that followed, trying to keep up here too, is exactly the growth `ops/rotate_status_history.py --apply-focus` moved to `STATUS-ARCHIVE.md`, 2026-10-23, scheduled operator.

**Correction, 2026-09-30, scheduled operator: "the next step on every distribution channel is Phil's own action" stopped being true for Bluesky the moment this line's own paragraph shipped.** Bluesky already had a real account and real traffic (5 visitors, all time) with no drafting pipeline; `ops/bluesky_drafts.py` and `.github/workflows/bluesky-drafts.yml` now draft and send 3 posts a day from the existing corpus, using the same SMTP secrets the LinkedIn and Facebook/X draft mailers already send through. No new owner credential or account was needed, so this one channel no longer waits on Phil at all: he only has to keep reading the morning email and posting as written, same as the other two. See `GOALS.md` and `OWNER-ACTIONS.md` for the full account.

---

# Final Rule

`STATUS.md` must describe reality, not aspiration.

If something is unknown, write `UNKNOWN`.

If something is degraded, write `YELLOW`.

If something is broken, write `RED`.

If something is healthy, prove it.

The purpose of this file is to let every autonomous agent answer:

**Where are we now, what matters most, and what should happen next?**
