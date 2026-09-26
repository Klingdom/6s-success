# 6S Success Current Operating Status

> Living operational state for Claude Code and all 6S Success autonomous agents.

## Document Role

`STATUS.md` is the fastest authoritative summary of **what is happening now**.

It is not a strategy document, backlog, changelog, incident archive, or analytics database.

Every agent performing meaningful autonomous work should read this file after `CLAUDE.md` and `AUTONOMY.md`.

Update this file whenever the material operating state changes.

---

# 1. Status Metadata

**Last Updated:** 2026-09-26, scheduled operator cycle: attach clean (unshallowed, `checkout main`/`merge --ff-only` fast-forwarded 401 commits onto `origin/main` with no conflict, `9f9e0425`). `preflight.py` clean on attach. `BACKLOG-2026-09-07.md` sections 2-4 fully Done/CLOSED, section 5 HOLD, section 6 owner-gated; 9 GitHub issues confirmed live via the API, unchanged, all `decision`/`blocked-on-art`, none pickable (issue #36 correctly left for Phil, a dead-check finding in the payment-integrity file `ops/check_sellable.py`, YELLOW/RED tier); 0 open PRs; no mail credential. So the cold-read lane (`ops/cold_read_ledger.py --next`) was again the right-sized work. **Cold-reading `ops/build_card_template.py` (the Entryway deck's print-rendering pipeline) found a real, if latent, bug in `fit_front()`'s own main fitting loop: `for act_lines in range(need, 1, -1)` is empty whenever a card's action text already fits on one line, so any such card skipped the whole fitting loop and fell into the "nothing fitted" fallback, which falsely reports `trimmed=True` and unconditionally drops the tagline even with ample room.** Reproduced with a synthetic one-line-action card before touching anything (`trimmed=True`, `tag=''` with 723px of unused headroom); checked the real 89-card Entryway corpus directly and confirmed 0 cards currently hit this path, so nothing has visibly shipped wrong yet, but the next short card written for this deck would silently lose its tagline. Fixed by widening to `range(need, 0, -1)`. Fail-then-pass proved directly via `git stash`; real-corpus trimmed count (2/89) unchanged before and after, confirming no regression. New `ops/tests/test_build_card_template_fit_front.py` (2 cases). **Self-inflicted detour along the way:** proving the fail-then-pass case with `git stash push`/`pop` overlapped a concurrently-running backgrounded `preflight.py` importing the same module, leaving a stale `.pyc` whose cached mtime+size happened to match the post-pop file and caused one test run to fail on bytecode that did not match the (correct) source on disk; not a repository defect, confirmed by clearing `__pycache__` and by `inspect.getsource`/`git diff` throughout. Cleared the cache and reran the full `preflight.py` a second time with no concurrent mutation: clean, every gate passed, 27 warnings, all previously diagnosed sandbox limits, none new. Recorded `ops/build_card_template.py` as fixed in `ops/cold-read-ledger.json`. No mail credential; no backlog row newly unblocked (sections 2-4 Done/CLOSED, section 5 HOLD, section 6 owner-gated), so this cycle's own work sits in epic 2 (broken or dishonest): a dormant-but-real defect in a shipping generator, found and fixed with a regression test before it could produce a visible card.

**Prior (2026-09-26, scheduled operator cycle): attach clean (unshallowed, `checkout -B main origin/main`, `merge --ff-only` fast-forwarded 401 commits onto `origin/main` with no conflict), `preflight.py` clean before touching anything (every gate passed, 26 warnings, all previously diagnosed). `BACKLOG-2026-09-07.md` sections 2-4 fully Done/CLOSED, section 5 HOLD, section 6 owner-gated; 9 GitHub issues confirmed live via the API, unchanged, all `decision`/`blocked-on-art`, none pickable; 0 open PRs; no mail credential, inbox checked (none found). So the cold-read lane (`ops/cold_read_ledger.py --next`) was again the right-sized work. **Cold-reading `ops/stripe_dedupe.py` found two real bugs stacked in `main()`'s own orchestration.** The 2026-09-23 fix made the "no duplicate products" path fall through to `dedupe_links()`, so clean-products/duplicated-links accounts still get checked. It missed the mirror case: when products WERE duplicated, `main()` returned before ever calling `dedupe_links()`, so a duplicate payment LINK on the same SKU, in the same run, was never even read; confirmed live with a mock account carrying both at once, `payment_links` was never queried. Second, independent bug: `--check`'s exit code was unconditionally 0 no matter what was found, for both products and links, because the dry-run branches never touched the counters the old return statements read. Neither weakened an automated gate (`gate_stripe_one_product_per_sku`/`gate_stripe_link_dedup` call `duplicates()`/`duplicate_active_links()` directly, never through `main()`); both weakened the CLI a human would run by hand, per `REVIEW-COMMERCE-2026-09-07.md`'s own documented "run `stripe_dedupe.py --check`" fix-order. Fixed: `main()` now always calls `dedupe_links()` regardless of product-duplicate state, and both functions return non-zero only when something is left duplicated, zero only when genuinely clean or fully resolved. Fail-then-pass proved directly (`git stash push -- ops/stripe_dedupe.py`; 3 new assertions failed as expected in `test_stripe_dedupe.py`, 2 in `test_stripe_dedupe_links.py` whose old cases had baked in the exit-code bug as correct behaviour; restored, both clean, `test_gate_stripe_link_dedup.py` unaffected). Full `preflight.py` clean after (every gate passed, 26 warnings, same standing sandbox set, none new). Recorded `ops/stripe_dedupe.py` as `fixed` in `ops/cold-read-ledger.json`. No mail credential; inbox checked, none found. No backlog row newly unblocked (sections 2-4 Done/CLOSED, section 5 HOLD, section 6 owner-gated), so this cycle's own work sits in epic 2 (broken or dishonest): the same "found once, fixed once, never generalised to its own mirror case" shape this file already exists because of, found and closed a second time in the same function.

**Prior (2026-09-26, scheduled operator cycle): `preflight.py` clean on attach (every gate passed, 25 warnings, all previously diagnosed). `BACKLOG-2026-09-07.md` sections 2-4 fully Done/CLOSED, section 5 HOLD, section 6 owner-gated; 9 GitHub issues confirmed live via the API, unchanged, all `decision`/`blocked-on-art`, none pickable; 0 open PRs; no mail credential, inbox not checked. So the cold-read lane (`ops/cold_read_ledger.py --next`) was again the right-sized work. **Cold-reading `ops/stripe_catalog.py`, a real, if latent, payment-integrity gap: `ensure_link()`'s orphan-link-adoption loop (built to attach this script's sku metadata to payment links Stripe held before this file existed) matched an unmetadata'd link by price alone, with no check that the link was still active.** Reproduced before touching anything: mocked Stripe to return one retired, unmetadata'd link selling the same price as a fresh SKU, and confirmed `ensure_link()` tagged that dead link with the SKU's metadata and returned its URL. Traced the real consequence rather than assuming the worst shape: `sync_site_links()` re-reads links itself and only ever publishes an active one, so the dead link is never written to the site directly; what actually happens is that `find_by_sku()` then keeps returning the same inactive, now-tagged link on every future run (it prefers active, falls back to inactive rather than ignoring it), so `ensure_link()` believes the SKU already has a link and never builds a real one, a silent, self-reinforcing, permanent loss of that SKU's ability to be bought until someone edits Stripe by hand. Fixed by skipping any orphan candidate whose `active` flag is false. **Also added a live gate, not just a code fix:** `stripe_catalog.skus_stuck_on_inactive_link()` checks every currently-deliverable SKU against the real account and reports any already stuck this way, wired into `preflight.py` as `gate_stripe_orphan_link_active()` beside `gate_stripe_link_dedup`, same warn-not-fail, no-credential-reports-UNCHECKED convention. Fail-then-pass proved directly for both halves (`git stash` each file in turn, watched the new tests fail by name, the code fix's own reproduction script and `test_gate_stripe_orphan_link_active.py`'s `AttributeError`, restored, reran clean); new `ops/tests/test_stripe_catalog_orphan_link_active.py` (2 cases: an inactive orphan is never adopted, an active one still is, so the fix does not break the migration path it exists for) and `ops/tests/test_gate_stripe_orphan_link_active.py` (3 cases, mirroring `test_gate_stripe_link_dedup.py`'s shape exactly). Full `preflight.py` clean after (every gate passed, 26 warnings, one new and expected: `stripe-orphan-link-active` correctly reporting UNCHECKED in this sandbox, which holds no Stripe credential). Recorded `ops/stripe_catalog.py` as `fixed` in `ops/cold-read-ledger.json`. No mail credential; no backlog row newly unblocked (sections 2-4 Done/CLOSED, section 5 HOLD, section 6 owner-gated), so this cycle's own work sits in epic 2 (broken or dishonest): a payment-integrity gap that could silently and permanently strip a SKU's ability to be bought, found before it produced a known incident, not after.

**Prior (2026-09-26, scheduled operator cycle): preflight was clean on attach (every gate passed, no fix needed this time), so the cold-read lane was the right-sized work, and it found a real, live bug rather than another clean file. Cold-reading `ops/checkin.py`, the hourly self check-in: `next_action()`'s "production is behind the repository, deploy" warning read the raw `products_live` field, which is `None` on every run with no egress to the live site.** Every sandboxed run is exactly that, so this warning had never once fired from this environment, despite `main()` already persisting a real `products_live_last_measured` carry-forward value for exactly this case (the identical fix already applied to `youtube_published` in the same file, one field over, never carried to this sibling). Confirmed live before fixing: called `next_action()` directly with a persisted state holding a real prior mismatch (`products_live_last_measured=130` against a repository that now defines 140) and no fresh reading; it fell through to the generic "work the next backlog item" message instead of warning, exactly the silent-skip this cycle found. Fixed by reading `products_live_last_measured` instead of the raw field, labelling the message with its own age when the reading is stale (mirroring the `youtube_published` branch's existing convention exactly), so a real carried-forward mismatch surfaces on a blind run rather than disappearing. `ops/tests/test_checkin.py`'s fixture (`_base_persisted`) was quietly mirroring only the fresh case, so every existing test happened to set the raw and carry-forward fields to the same value and never exercised the blind-run path; widened it to carry forward automatically like `main()` does, and added two new cases (a stale mismatch that must still warn, and a stale match that must stay silent) plus the age-label assertion. Fail-then-pass proved directly: `git stash push -- ops/checkin.py`, the new test cases failed exactly as expected ("did not use the carried-forward products_live reading"), restored, reran clean (26/26). Full `preflight.py` clean after (`gate_tests()` auto-discovers `test_checkin.py` via glob, no new wiring needed; every gate passed, 25 warnings, same standing sandbox set, none new). Recorded `ops/checkin.py` as `fixed` in `ops/cold-read-ledger.json`. Checked egress directly rather than assume the standing "no egress" finding was stale: still denied by organization policy (`CONNECT tunnel failed, response 403` against Stripe, the live site and Bing alike), so epics 1 and 3's owner-gated items stay genuinely blocked, not re-attempted. 9 GitHub issues confirmed live via the API, unchanged, all `decision`/`blocked-on-art`, none pickable; `BACKLOG-2026-09-07.md` sections 2-4 fully Done or CLOSED by decision, section 5 HOLD, section 6 owner-gated, so this cycle's own work sits in epic 2 (broken or dishonest): a real check meant to catch production drift had been silently inert in every sandboxed environment since it was written.

**Older entries (67 of them, 2026-08 to 2026-09-26) live in `STATUS-ARCHIVE.md`.** Most recently added this cycle, moving the oldest of what would otherwise have been a five-entry stack there (the "Step 2's own gate failed on first run" scheduled-operator entry) to keep this stack at four (the same rotation practice this file has followed since 2026-09-17): the oldest archived each time a new one is added rather than left to grow unread. Nothing is deleted, and the gates that scan this file for stale claims (`gate_no_stale_session_label`, `gate_no_stale_checkout_count`, `gate_no_stale_listmonk_blocker`, `gate_corporate_buy_path_current`, `gate_critical_risks_escalated`) scan the archive too, so an archived claim is no less checked than a current one.

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
| Public website | LIVE, last confirmed 2026-09-25T14:15:05Z, level with HEAD at the time of that deploy | Build `d40585d97500a3ca` (commit `5ff17fcb`), `ops/deploy.py` verified production serves it and that it matches the repository. All six room decks (Entryway, Kitchen, Primary Bathroom, Laundry Room, Home Office, Garage) are live and linked from `deck.html`; the four newest were 404 until this deploy. |
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

**Currently Deployed Build (last confirmed):** `d40585d97500a3ca` (commit `5ff17fcb`), confirmed 2026-09-25T14:15:05Z
**Confirmed At:** `2026-09-24T21:10:12Z` (`ops/deploy-verdict.json`,
a session with real production access)
**Repository HEAD Build:** `6e4992daa2791557` (`site/build-id.txt`,
this scheduled operator cycle, 21:2x. One commit ahead of the confirmed
deployed build above: `869d4e93` ("Home Office personalised") landed
after the confirmation and touched `site/`, so `git diff --quiet
d5b0d5c8 HEAD -- site/ Dockerfile` is dirty again. Production is one
commit stale, not current; see `BLOCKER-001` below for the full account
and the standing caveat that this will keep recurring until
`VPS_DEPLOY_KEY` makes redeploy automatic)
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
| Production traceability | Tracked, current, real gap 5 commits (3 material) | **Widened 2026-09-25 09:1x, PM check-in: the 08:0x "3 commits" citation above went stale by two commits.** `ops/deploy-verdict.json` unchanged (`verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`, resolving to commit `890c43a3`); a fresh recount (`resolve_verdict_commit()`/`deploy_gap_material_commits()`) now finds 5 commits since: `1b6439a7` and `ad310568` (build-id/merge only, no independent site content), `cb37d0c8` (B9's Entryway deck), `c6cc1a6a` (B9's Laundry Room deck) and `2cb970c1` (B9's Home Office deck, landed after the last correction). No P0 regression, just three new free pages sitting undeployed until the next redeploy. No sandboxed session holds the deploy key, so this remains read from the committed verdict, not re-checked live against the VPS itself. See `BLOCKER-001` above for the full history of this recurring pattern |
| Repository hygiene | 8 open issues (6 `decision`, 2 `blocked-on-art`), 0 open PRs, 1 branch, 219+ test files, `preflight.py` clean | **Corrected 2026-09-25 06:1x, PM check-in:** the prior "7 issues (5 decision)" undercounted; issue #35 (`VPS_DEPLOY_KEY`, opened 2026-09-24) is a sixth `decision`-labelled issue, confirmed live via the GitHub API this cycle (issues #2, #15, #18, #21, #29, #31, #33, #35). Not a formal audit, but the working facts a reader would otherwise have to reconstruct from `NIGHTLY-LOG.md` |

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
| Root-cause guidance | IMPLEMENTED for 12 of 114 zones | Diagnosis block (friction → root cause → action) renders on the 12 pilot zones, gated by `gate_diagnosis_rendered`. The remaining 102 are deliberately held for a 21-day pilot read before widening (`BACKLOG-2026-09-07.md` A1) |
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
| Sessions | 57 | Last 30 days | MEASURED 2026-09-25 01:17 UTC (visitors; 144 visits, 786 pageviews), direct Umami database read over ssh, filtered to this site's website_id. An unfiltered read the same night said 239: this Umami instance serves three sites, and `ops/experiments.py` now refuses that query shape. Down from 76 mainly because the 7 Sept automated session (431 pageviews) rolled out of the window, so this figure is very nearly all human; previous 76 (09-21), 78 (09-17), 75 (09-14), 68 (09-11) |
| Sessions | 12 | Last 7 days | Same source, 2026-09-23: 12 visitors, 18 visits, 33 pageviews. The three-week fall (18, 14, 10) has stopped without reversing; 12 is noise against 10, not recovery |
| Organic sessions | 5 visits from 4 visitors, whole life of the site, measured 2026-09-20 (1 Bing, 21 August; 4 Google visits from 3 visitors, 4 to 20 September) | Direct Umami database read; one more Google visitor than the 2026-09-17 reading |
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
| Desired functions / root causes | 12 of 114 zones have authored diagnosis depth | Kitchen (7) + Entryway (5) pilot; the other 102 hold a general reading block instead, deliberately gated on a 21-day read of the pilot before widening (`BACKLOG-2026-09-07.md` A1) |
| Quests | Live app (`quest.html`) plus 684-card Whole House Print Pack | Symptom-first entry covers 5 of 114 zones; the rest enter by room or a full-house draw |
| Standards | Standards Pack (free, 20 pages) | The one page organic search currently lands anyone on |
| Products / kits | 129 of 130 catalogue SKUs buyable via direct Stripe checkout | Corporate Lean 6S is quote-based by design, not a gap |
| Free decks | Entryway (88 cards, illustrated) and Kitchen (72 cards, unillustrated) | Both free and ungated |
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

**Status:** ACTIVE, opened 2026-09-07  
**Owner:** operator, direction from Phil  
**Objective:** `PLAN-MICROZONES-DECKS-APP.md` + `BACKLOG-2026-09-07.md`
section 2/3: build the root-cause diagnostic layer the product currently
lacks (0 of 114 zones map a root cause), fix the app's first thirty seconds,
and ship the free unillustrated Kitchen deck.

**Done:** M1, the frozen 17-cause vocabulary (`ops/root_causes.py`,
`gate_root_cause_vocabulary`), corrected from the plan's own uncross-checked
"21" (a friction-card count, not a cause count). Separately this same cycle,
not part of this workstream's plan but found while verifying it: a live CI
break (three control docs' em/en dashes, plus real bugs in the fixing tool
itself) and a real generator-ownership drift (the $19 Print Pack, the live
Quest app's own data, and the mobile app's corpus all served pre-Sustain-
rewrite text after a concurrent session's content change), both fixed.

**Done 2026-09-07, operator, this cycle:** M2, the `diagnosis` schema and
validator (`ops/diagnosis.py`, `content/manual/source/validate.py` GATE 8,
`ops/tests/test_diagnosis_schema.py`). First draft flattened each friction to
one cause; corrected in the same cycle after checking it against the real
`kitchen-deck.json` FRICTION CARDs, which branch one symptom to two or three
causes. Zones without `diagnosis` still build (0 of 114 diagnosed today).
Also fixed this cycle, found by preflight at the start: `site/build-id.txt`
was stale against the prior commit's own `sw.js` regeneration, failing both
`checks.yml` and `publish-image.yml` at HEAD; fixed and both confirmed green.

**Done 2026-09-07, operator, same cycle:** M3's Kitchen half. All 7 Kitchen
zones now carry `diagnosis`, every string reused verbatim from
`ops/cardtext/kitchen-deck.json`'s own FRICTION and 15-minute ACTION cards
(0 schema problems). Entryway 5 is still open: those zones have no
equivalent card deck to reuse from, so it needs real authorship rather than
a mechanical mapping.

**Done 2026-09-07, operator, this cycle:** M3's Entryway half, and M3 is now
complete (12 of 12 pilot zones). The 5 Entryway zones carry hand-authored
`diagnosis`, since no Entryway card deck exists to reuse from; grounded
directly in each zone's own already-published `passes`/`the_call`/`watch_for`
text, every cause drawn from `ops/root_causes.py`'s frozen 17, no fact
invented. Reconciled with a concurrent session's own commit of the Kitchen
half (`3e58d480`, pushed while this cycle was in flight): rather than
re-push a conflicting `content.json`, reset onto their tip and layered only
the new Entryway zones on top, keeping their Kitchen authorship untouched.

New `gate_diagnosis_authoring` in `preflight.py` asserts, on every run, that
every Kitchen pilot zone's frictions reuse a real FRICTION CARD's `title` or
`objective` and branches character-for-character (their commit used `title`;
the gate accepts either real field, not one hardcoded guess), and scans
every diagnosed zone anywhere for a customer/reviewer attribution claim.
`ops/tests/test_diagnosis_authoring.py`, 5 cases, proves both defect classes
get caught on a planted mutation, then restores; real corpus clean.
`content/manual/source/validate.py` GATE 8: 12 of 114 zones diagnosed, 0
problems. `content.json`'s Entryway diff is a verified pure addition (259
lines, 0 changed), confirmed by a controlled round-trip before editing.

**Done 2026-09-07, operator, this cycle:** M4. `ops/build_zone_pages.py` now
renders the diagnosis block (symptom, branches, 30-second confirm test,
which pass to start at, plus the 15-minute entry) above the six passes on
all 12 pilot zone pages, adds one FAQPage Q&A per friction, and swaps their
related reading from the shared 19-link block to 3 to 5 articles chosen by
the zone's own diagnosed causes, no two of the 12 identical. Two real
grammar defects (a blanket `.lower()` and `str.capitalize()` both turning a
mid-sentence "I" into "i") caught by reading the rendered page, not by any
upstream check, and fixed before shipping. New `gate_diagnosis_rendered` in
`preflight.py` (`ops/tests/test_gate_diagnosis_rendered.py`, 8 cases) checks
render coverage, the link-count range, cross-zone uniqueness, and that exact
pronoun defect on every future run. Not checked against the live domain
itself (`CLAUDE.md` 0.3): no egress to 6s-success.com from this sandbox,
same wall every prior cycle records. Full detail in
`PLAN-MICROZONES-DECKS-APP.md`'s M4 row.

**Done 2026-09-07, operator, this cycle:** K0/B3, the deck card-count gate.
`gate_deck_count` counted rendered card-front PNGs to learn the deck's true
size, and returned immediately when `build/cards-rendered/` was empty, which
is every cloud run: the entire check, including every catalogue/page
comparison, silently never ran anywhere except a full local render. Rewrote
it to read `build/entryway-cardtext.json` (a committed corpus file, real in
every environment) instead, and to assert `ops/build_deck_gallery.py`'s
hardcoded `DECKS['entryway']['written']` against that corpus so the count
itself can never quietly drift. Verified a real, live defect this surfaced:
`deck.html`'s title, meta description and OG/Twitter tags said "89 cards"
with no explanation, while `data.js`, `shop.html` and the print-and-play
redirect page all said 88; fixed the six flat instances on `deck.html` to
88. Left the already-correct "72 of the deck's 89 cards are drawn" progress
sentences alone (89, the full written total, is the right denominator
there; `deck-gallery.html` already explains the 89/88 split). Also found
and corrected a stale claim in `PLAN-MICROZONES-DECKS-APP.md` 3.2: the "46
cards" figure it named in `ops/build_printpack.py`/`ops/build_standards.py`
no longer exists in either file, consistent with Phil's 2026-08-30 sweep;
that row was never re-read against the code after that fix landed. New
`ops/tests/test_gate_deck_count.py` (7 cases) proves the gate catches a
third-number catalogue claim and a bare wrong-number page, does not
false-positive on a CSS comment inside `<style>` (found live, a dormant
bug the never-runs gate had been hiding) or on the honest "X of Y drawn"
phrasing, and that the DECKS table matches the real corpus. `preflight.py`
confirmed clean after: every gate passed, same 15 sandbox-limitation
warnings. The 404-shop-tile half of K0 is unchanged: the referenced image
exists in this repository's own build, not the same claim as a live 200,
and this sandbox still has no egress to 6s-success.com to check that
directly.

**Next:** M4's 21-day clock starts once this is deployed and verified live.
A2 is now done (see below). M6 (diagnosis for the remaining 102 zones) stays
gated on M4's 21-day read, per the plan's own rule: do not start it early.

**A5 done, 2026-09-09, operator.** The three genuinely missing funnel events
(`quest-cause-shown`, `quest-card-abandoned`, `quest-return`) are now shipped
in `site/assets/js/quest.js`, verified by a new static gate and a real
headless-Chromium run; see `BACKLOG-2026-09-07.md`'s "A5 (funnel
instrumentation) closed" row and `PLAN-MICROZONES-DECKS-APP.md`'s A5 row for
the full account.

**S1-S4 re-measured, 2026-09-09, operator, rather than trusted from the
prior line's own hedge.** The prior note here was right to be suspicious:
the concurrent Sustain prose rewrite already covers most of what S1-S4 asked
for as authored content. Measured directly against `content.json`'s 114
`passes.sustain` strings: all 114 are now 87 to 106 words (median 94,
comfortably inside S2/S4's 90-to-130 target), and a rough keyword scan finds
recovery language in 102 of 114. What is still genuinely absent is the
*structured, machine-checkable* schema S1 itself asks for (a `sustain_detail`
object with six typed fields, a closed cadence list, a `drift_signal` noun
check): 0 of 114 zones carry any such field today, so S1's schema and gate
do not exist. Given the prose already answers the content gap that made S1
urgent, S1 as originally scoped (add the schema, then re-author it a second
time in structured form) reads as more product work ahead of the constraint
(`GOALS.md` rule 1: distribution beats production) rather than the
measurement-tier item it was filed as. Recommend re-scoping S1 to something
narrower before spending 0.5 to 3.5 days on it, or dropping it in favour of
Epic 3 (traffic) work; left as an open question rather than started this
cycle.

**A2 done, 2026-09-09, operator, a later cycle the same day.** "45 to 75
minutes" was still the first number a first-timer read on card one of the
classic ("show me the house instead" -> "Start at the door") path; the
symptom flow's own simplified card zero already hid it, but that path did
not. `site/assets/js/quest.js` now withholds `#c-session` on any card one of
a genuine first run (`run.i === 0 && isFirstRun()`), covering both paths with
one condition instead of two. The number moved to the finish screen instead
of disappearing: a new `#f-session` in `site/quest.html`, populated once at
least one card of a single-zone run is done, phrased against whether the
zone was just fully held. The zone page already stated it and is untouched.
Verified in a real headless-Chromium run of the classic path end to end
(card one empty, card two correctly shows "15-30 min for the whole zone, six
passes", finish screen reads "The whole zone runs about 15-30 min, all six
passes, whenever you want the rest of it."), plus the existing
`test_quest_flow.py` (symptom path) still passing unmodified. New
`gate_quest_session_placement` in `preflight.py`,
`ops/tests/test_gate_quest_session_placement.py` (6 cases, fail-then-pass
proved on both halves: the withholding and the finish-screen restatement).
`ops/fingerprint_assets.py` rerun; `site/quest.html`'s script-tag
fingerprint and `site/sw.js` follow. See `PLAN-MICROZONES-DECKS-APP.md`'s A2
row for the full account.

**M7/A1 found already fixed by Phil, closed against reality, 2026-09-09,
operator, a later cycle the same day.** Both rows still read as 1.5 days of
open work ("570 of 684 cards print a stop condition that card cannot
reach"). Phil's own `fa491b1a` (2026-09-07) had already fixed the actual
lie: `renderCard()` no longer heads a card "You can stop when" over the
whole-zone `done_looks_like` text, it says what the text is and where the
reader stands against it. The literal M7 acceptance criteria (a distinct
authored `victory` line per card) is still unmet and correctly unstarted;
`PLAN-MICROZONES-DECKS-APP.md` updated to say so. New
`gate_quest_card_victory_honesty` in `preflight.py`
(`ops/tests/test_gate_quest_card_victory_honesty.py`, 6 cases, fail-then-pass
proved by reintroducing the exact old heading live) protects the fix from
regressing. Also confirmed A3 and A4 already fully shipped under A5/A6's own
2026-09-08 commits, never marked against their own rows: A3's symptom
screen and A4's two-minute first-action override both live in
`site/assets/js/quest.js`, verified by reading the code directly. See
`PLAN-MICROZONES-DECKS-APP.md`'s M7/A1 rows and section 1.4 for the full
account.

**Done 2026-09-25, scheduled operator: the first of B9's five room decks
(Entryway) shipped, correcting this section's own now-stale line above
("Entryway 5 is still open: those zones have no equivalent card deck to
reuse from, so it needs real authorship rather than a mechanical
mapping").** That was true on 2026-09-07; the Manual's `diagnosis` layer
reached Entryway on 2026-09-24, which made a mechanical mapping possible
after all. New `ops/cardtext/build_entryway_deck.py` and
`ops/build_entryway_deck_page.py` ship a 57-card, corpus-accurate Entryway
deck at `site/entryway-deck.html`, mirroring
`ops/cardtext/build_kitchen_deck.py`'s pattern card for card; the frozen 12
root causes this section's M1 froze are reused verbatim (13 of the 17 are
reachable from Entryway's real frictions), so this new deck composes with
the Kitchen deck rather than forking its own vocabulary. Does not touch
the old illustrated 12-zone free deck (`deck.html`, the live `DECK-ENTRY`
SKU); both are live, each disclosing the other. New
`gate_entryway_deck_rendered` in `preflight.py`, fail-then-pass proved.
Full account in `ops/NIGHTLY-LOG.md`, 2026-09-25, and
`BACKLOG-2026-09-07.md` row B9. Four rooms remain (Laundry, Home Office,
Primary Bathroom, Garage).

**Corrected 2026-09-25, PM check-in: the line above is stale.** All four
named rooms have since shipped the same way (`site/laundry-room-deck.html`,
`site/home-office-deck.html`, `site/primary-bathroom-deck.html`,
`site/garage-deck.html`), each with its own `gate_<room>_deck_current`/
`gate_<room>_deck_rendered` pair, fail-then-pass proved, per
`ops/NIGHTLY-LOG.md`'s 2026-09-25 entries and `BACKLOG-2026-09-07.md` row
B9. B9 is fully closed, five of five rooms; no room deck row remains
open in section 3.

---

# 15. Current Experiments

No experiment should be treated as active until its implementation and measurement are verified.

| Experiment | Status | Owner | Primary Metric |
|---|---|---|---|
| None verified in this status file | NONE VERIFIED | - | - |

Active experiments should also be tracked in `EXPERIMENTS.md`.

---

# 16. Current Incidents

**No incident status has yet been verified.**

This does **not** mean there are no incidents.

Production inspection is required.

When an incident is active, record:

- ID
- severity
- start
- impact
- coordinator
- current state
- mitigation
- next update

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

**RESOLVED 2026-09-25 14:15 UTC, this session: production redeployed and
verified, and the gap it closed was customer-visible.** `ops/deploy.py`
confirms production now serves build `d40585d97500a3ca` (commit `5ff17fcb`),
matching the repository.

What was actually behind: four room decks. `site/deck.html` is the hub that
links every deck, and a concurrent session had shipped Primary Bathroom,
Laundry Room, Home Office and Garage. All four returned **404 in production**
while the repository believed they existed. The live hub had not yet been
rebuilt, so no visitor met a broken link, which is luck rather than design:
had the hub deployed one build earlier than its targets, it would have shipped
four dead links on the page whose whole job is linking them.

Verified after deploying, on the live site rather than in the repository: all
six deck pages return 200 (130 KB to 177 KB), all six are linked from the live
hub, and the Garage deck renders all seven of its zones and 80 cards with
`site.js` present.



**Corrected 2026-09-25, scheduled operator cycle: both the Status line below and the "Production Knowledge" paragraph under Current Overall Assessment were citing a superseded confirmation.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, resolving via `resolve_verdict_commit()`/`git log -S` to commit `c6cc1a6a` (B9's Laundry Room deck). `deploy_gap_material_commits()` finds 5 material commits since (`8f6c47b3` build-id fix, `9c6d4063` the five-deck og:image fix, `e6017e8b`/`f3ceca2e`/`2cb970c1` B9's Garage/Primary Bathroom/Home Office decks), touching 8 distinct `site/`/`Dockerfile` files. No P0 regression: the gap is three new free deck pages and one image-metadata fix, undeployed until the next redeploy. No sandboxed session here holds the deploy key, so this is read from the committed verdict, not re-checked live against the VPS itself; `gate_status_deploy_verdict_current` caught the stale citation, not a live production check.

**Status: RESOLVED (as of 2026-09-25 14:15 UTC, production level with the repository at build `d40585d97500a3ca`, commit `5ff17fcb`, verified live by `ops/deploy.py` rather than read from a committed verdict), structurally recurring.** The 07:30 REOPENED line above it is superseded: the five commits it named, including B9's Garage, Primary Bathroom and Home Office decks, are the ones this deploy shipped. No sandboxed
operator session has ever held the VPS deploy key or egress to
`6s-success.com`, so this half genuinely cannot be verified from here on
any cycle, not just this one; it is a standing structural limit, not an
unstarted task. What IS known: the repository's own deploy-freshness
check (`ops/deploy_freshness.py`, `ops/deploy-verdict.json`) previously
went stale at 233 commits behind (last confirmed 2026-09-18T17:20:47Z,
build `7c765b634045a89c`), flagged by the 2026-09-20 11:12 PM check-in.
Phil redeployed twice that day, from a session with real production
access (`470834de`, then `7ae0e9b6`): the tracked verdict read current at
2026-09-20T17:46:50Z, build `d9fc700d0700972f`.

**Corrected 2026-09-23 20:0x, PM check-in: a newer confirmation superseded the 13:4x one, same closed state.**
`ops/deploy-verdict.json`, read directly rather than cited, now records
`verdict: "current"`, build `5eba61fde231c1a7`, `checked_at:
2026-09-23T19:00:39Z`, from a later session with real production access
that finished the Stripe SKU retirement (65 of 65 confirmed archived) and
redeployed. `site/build-id.txt` at HEAD read the same build id at that
time, so the marker and the repository agreed then.

**Reopened 2026-09-24 03:5x, PM check-in: the gap has grown to 47 commits and now includes a second live customer-facing defect, not just internal-consistency work.** `git log 8e4c8e33..HEAD` (the last deployed commit to HEAD): 47 commits. Two are not narrow: `a16788fa` fixed a real, live dead-nav-menu defect on `404.html`, `corporate.html`, `kit.html`, and 2 B2B articles (same class as `8e4c8e33` itself, which is why production is *already* known to have shipped this exact defect once): every one of those pages still ships the broken hamburger button in production right now, over 8 hours after the fix was committed. `b0166730` finished retiring the last of 65 dead/superseded Stripe SKUs, so production's catalogue is stale by that much too. No operator sandbox holds the deploy key or egress to verify or fix this itself, so the next confirmation still needs a session with real access, same structural limit as every prior occurrence, but this is no longer "nothing open to close": a real, known, live defect is sitting unfixed for customers, and the fix has been sitting ready in the repository for over 8 hours.

**Corrected 2026-09-24 04:1x, PM check-in: the 47-commit figure was already stale within one cycle; a third live defect has entered the gap.** Re-derived directly rather than repeated: `git log 8e4c8e33..HEAD` is now 50 commits, over 9 hours behind the last confirmed deploy. `a16788fa` (dead-nav-menu, 5 pages) and `b0166730` (65/65 SKU retirement) are unchanged from last cycle. New: `b6b35ee7` fixed invalid JSON-LD on both B2B articles (`what-a-5s-engagement-costs.html`, `why-5s-decays-after-six-months.html`), single-quoted Python literals rather than valid JSON, which had made both blocks unparseable by any real structured-data consumer and had silently excluded both articles from `feed.xml`; that fix, and the `feed.xml`/`sitemap.xml`/`llms.txt` regeneration it required, are also sitting undeployed. Still the same structural limit: no operator sandbox holds the deploy key or VPS egress, confirmed again directly this cycle (no key at `~/.ssh`, `curl` to `6s-success.com` `connect_rejected` by the agent proxy). This number will keep growing every cycle until a session with real access redeploys; the standing instruction for future cycles is to re-derive it with `git log`, not cite the last cycle's figure.

**Updated 2026-09-24 05:0x, scheduled operator: the image-publish half of this gap is closed, the VPS half is not.** `publish-image.yml`'s last attempt (commit `b6b35ee7`) had failed on an unrelated, already-fixed log-ordering gate, and nothing since had touched a `site/`-triggering path to retry it, so no current image existed to redeploy even if a session with VPS access ran one. Dispatched the workflow directly (it accepts `workflow_dispatch` alongside its push trigger); run 395 finished `success`. A fresh image built from current `main` is now published to `ghcr.io/klingdom/6s-success` and ready for the host's `Redeploy` click. The underlying commit gap and the three live defects named above are unchanged; only the "is there an image ready to pull" question has moved from no to yes.

**Independently confirmed 2026-09-24 05:1x, PM check-in, same conclusion from a different angle: this cycle happened to hold a working `GH_TOKEN` (rare for a sandboxed session today) and read `publish-image.yml`'s history directly rather than trust the operator's own account. Same fact, verified rather than merely cited: `git diff --quiet 914c2881 HEAD -- site/ Dockerfile` returns clean, confirming the GHCR image already matches HEAD.** `git log 8e4c8e33..HEAD` is 59 commits, but that count now measures undeployed work only, not unbuilt work; the one remaining step is Phil's Redeploy click in Hostinger (or a session with the VPS key running `ops/deploy.py`), per `OWNER-ACTIONS.md` item 1b.

**Re-confirmed 2026-09-24 05:4x/05:5x, two concurrent PM/operator cycles: unchanged, no new live defect.** `git log 8e4c8e33..HEAD` is 60 commits after this merge, growth being routine check-ins and log entries, not new site work. The two cycles collided on the same standing `wire_*.py` cold-read handoff (both closed it clean independently, folded into one account in section 1's "Last Updated" notes above rather than left as two competing claims) and merged rather than one overwriting the other. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**Re-confirmed 2026-09-24, this PM check-in: unchanged, no new live defect.** `git log 8e4c8e33..HEAD` is now 66 commits, growth again being routine check-ins, not new site work. `git diff --quiet 914c2881 HEAD -- site/ Dockerfile` re-run and still clean, so the GHCR image still carries every fix named above. `preflight.py` run to completion: every gate passed, 23 warnings, all previously diagnosed sandbox limits, none new. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**Re-confirmed 2026-09-24 18:1x, PM check-in: unchanged, no new live defect, and a newer build confirmation found than the one this section had been citing.** `git log 8e4c8e33..HEAD` is now 127 commits. Rather than re-run the `914c2881` diff again, checked GitHub Actions directly: `publish-image.yml` has since built and published successfully from a later commit anyway, run 398 (`https://github.com/Klingdom/6s-success/actions/runs/36032909521`, a plain push build, no dispatch needed), `success` at 2026-09-24T17:35:17Z against commit `accc9fff`. `git diff --quiet accc9fff HEAD -- site/ Dockerfile` is clean, so the GHCR image matches HEAD through the newer, later-confirmed commit, not just the older one this section named. Still only Phil's Redeploy click (or a session with the VPS key) remains.

**RESOLVED 2026-09-24 19:2x, PM check-in: the redeploy this section has been waiting on since 05:0x already happened, and nobody had told this section.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `4ec571da81db3b34`, `checked_at: 2026-09-24T18:47:16Z`, written by `ops/deploy.py`'s own `write_verdict_marker()`, which only ever runs from a session that just confirmed production live by a real, credentialed check (committed in `44ef380a`, a Phil-authored commit co-authored by Claude, the same "local session holding `~/.ssh/6s_deploy`" pattern this file has recorded doing the redeploy on every prior occasion, not Phil clicking anything himself). `site/build-id.txt` at HEAD (`ef417f10`) reads the identical `4ec571da81db3b34`, and `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is clean, so no commit since that confirmation has touched anything a redeploy would need to carry. The gap this section spent all day narrating (47, then 50, then 60, then 66, then 127 commits) is zero right now: production is confirmed serving exactly what HEAD serves. This sandbox holds no VPS key (confirmed again this cycle: no file at `~/.ssh/6s_deploy`), so this is read from the committed verdict, not re-checked live; the structural limit BLOCKER-001 names (no sandboxed session can verify or redeploy production itself) still stands for the next time a `site/**` commit lands after this confirmation, which is why this is closed as of right now, not closed permanently.

**Reopened 2026-09-24 21:1x, PM check-in: the auto-deploy workflow fired end to end for the first time and proved it still cannot act, because `VPS_DEPLOY_KEY` has not been pasted; the gap is real again, 20 commits.** `git log 44ef380a..HEAD` is 20 commits, `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is dirty (29 files, mostly the Micro Zones "Primary Bathroom personalised" content shipped this cycle). `publish-image.yml` run 399 built and published clean from `d5b0d5c8` at 2026-09-24T21:06:42Z; `git diff --quiet d5b0d5c8 HEAD -- site/ Dockerfile` is clean, so the GHCR image already matches HEAD. `.github/workflows/deploy.yml` (added earlier today, `STATUS.md` section 1) then fired automatically for the first time, `workflow_run` off that publish, run 5, completed `success` at 2026-09-24T21:07:19Z. Read its own job log rather than trust the green checkmark: the "Deploy" step itself shows `conclusion: skipped`, exactly the no-op its own first step is built to do when `VPS_DEPLOY_KEY` is absent, confirmed absent in this sandbox (`ls ~/.ssh` empty). So the automation is proven wired correctly end to end, and still cannot close this gap without the one paste in `OWNER-ACTIONS.md` item 0 / GitHub issue #35. Production is confirmed stale by the 29 files above until either that secret is added or a session holding `~/.ssh/6s_deploy` runs `ops/deploy.py` by hand.

**RESOLVED 2026-09-24, later, scheduled operator cycle: a session holding real access redeployed again, then one more site commit landed after it, same recurring shape.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `28ed2709194afab5`, `checked_at: 2026-09-24T21:10:12Z`, matching commit `d5b0d5c8` (`git show d5b0d5c8:site/build-id.txt` is the same id); `git diff --quiet d5b0d5c8 HEAD~1 -- site/ Dockerfile` (against `869d4e93`, the commit that redeploy confirmation covers) is clean, so that redeploy did close the 21:1x gap in full at the time it ran. **Reopened by the same structural pattern within one cycle:** `869d4e93` ("Micro zones: Home Office personalised") landed immediately after, touching `site/`, and moved `site/build-id.txt` to `6e4992daa2791557`; `git diff --quiet d5b0d5c8 HEAD -- site/ Dockerfile` is dirty again (1 commit, `869d4e93`; this session's own `f62cc3ea` touches only `ops/` and a root CSV, not `site/` or `Dockerfile`, so it adds nothing to the gap). Still the same standing limit: this sandbox holds no `~/.ssh/6s_deploy` and no VPS egress (confirmed again, `ls ~/.ssh` empty), so this cannot be closed from here; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is what would make this stop recurring instead of being rediscovered every cycle.

**Widened 2026-09-24, later, scheduled operator cycle: the entry above's own commit count had already gone stale by the time this cycle read it, and a new gate now checks for exactly this.** The build_id citation (`28ed2709194afab5`) was still correct, but two further site-affecting commits landed after the entry above was written and neither was mentioned: `29a84fa2` ("Correct 13 wrong cause IDs across two rooms") and `b8eca135` ("Micro zones: Laundry Room personalised"). A fresh recount (`git log d5b0d5c8..HEAD -- site/ Dockerfile`, `d5b0d5c8` being the commit build_id `28ed2709194afab5` actually came from) puts the real gap at (3 commits, `869d4e93`, `29a84fa2`, `b8eca135`; 55 files, 805 insertions, 479 deletions), not the 1 commit the entry above named. No new live defect beyond the recurring structural one; this is the same gap, just correctly sized now. New `gate_status_deploy_gap_count_current` in `preflight.py` (pure logic in `deploy_gap_count_problem`, `ops/tests/test_gate_status_deploy_gap_count_current.py`, 6 cases) re-derives which commit a deploy verdict's build_id actually came from and recounts the real gap from there, so a correct build_id citation next to a stale commit-count no longer passes silently the way `gate_status_deploy_verdict_current` alone allowed it to; fail-then-pass proved directly (the test's own synthetic "(1 commit)" claim against a real count of 3 fails by name, "(3 commits)" passes), and it fired correctly against this exact live drift before this correction was written. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key.

**RESOLVED then reopened, 2026-09-25 00:1x, PM check-in: the entry above's own build_id citation was itself already superseded, not just its commit count.** Before correcting the "3 commits" figure by re-deriving from the same `28ed2709194afab5`/`d5b0d5c8` citation the entry above used, checked `ops/deploy-verdict.json` directly rather than trust that citation, per this file's own repeated lesson. It now records a newer confirmation: `verdict: "current"`, build `6a10df205a3d058c`, `checked_at: 2026-09-24T23:35:51Z`, unread by any prior entry in this section. `git log -S6a10df205a3d058c -- site/build-id.txt` resolves that build to commit `b8eca135` ("Micro zones: Laundry Room personalised"), so a session with real access redeployed again after the 21:1x confirmation and closed the gap in full at that time: `git diff --quiet b8eca135 HEAD~1 -- site/ Dockerfile` is clean. **Reopened by the same recurring pattern within the same cycle:** `ca49aa25` (Phil's own "Micro zones: Garage personalised") landed immediately after and touches `site/`; `git diff --quiet b8eca135 HEAD -- site/ Dockerfile` is dirty again, real gap now (1 commit, `ca49aa25`; 44 files, 547 insertions, 323 deletions), not the 4 the superseded recount above would have named against the older build. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key. Direct call to this repository's own `deploy_gap_count_problem()` against the corrected text below confirms clean.

**Widened 2026-09-25 01:4x, PM check-in: the entry above's own commit count had already gone stale, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run rather than assumed clean.** The build_id citation (`6a10df205a3d058c`) is still correct, resolving to commit `b8eca135` (`git log -S6a10df205a3d058c -- site/build-id.txt`). A fresh recount (`git log b8eca135..HEAD -- site/ Dockerfile`) finds two commits touching `site/`, not the one the entry above named: `fa78db8c` (Phil's own D-026 checkpoint, which shipped `measure.js`'s new `zone-block-seen` instrumentation to every zone page) landed the same day as `ca49aa25` and was not counted. Real gap is now (2 commits, `fa78db8c`, `ca49aa25`; 197 files, 808 insertions, 520 deletions). No new live defect beyond the recurring structural one; this is the same gap, just correctly sized. Same standing limit as every entry above: no sandboxed session here holds `~/.ssh/6s_deploy` or VPS egress, so the redeploy itself still needs `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a local session with the key. Direct call to this repository's own `deploy_gap_count_problem()` against the corrected text confirms clean.

**Widened 2026-09-25, scheduled operator cycle: the entry above went stale within the same day, same recurring pattern, caught again by `gate_status_deploy_gap_count_current` before this cycle touched anything else.** The build_id citation (`6a10df205a3d058c`) is still correct, still resolving to commit `b8eca135`. A fresh recount (`git log b8eca135..HEAD -- site/ Dockerfile`, cross-checked against `preflight.py`'s own `resolve_verdict_commit`/`deploy_gap_material_commits`) finds three commits, not the two the entry above named: `ca49aa25`, `fa78db8c`, and `6ba42a27` ("Close 13 real gaps in \"how to clean anything\", and fix the page that promised it"), which landed after the entry above was written and was not counted. Real gap is now (3 commits, `ca49aa25`, `fa78db8c`, `6ba42a27`; 198 files, 975 insertions, 3518 deletions per `git diff --shortstat b8eca135 HEAD -- site/ Dockerfile`). No new live defect beyond the recurring structural one; this is the same gap, just correctly sized, and it will keep growing every cycle site work lands until `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is set or a session holding `~/.ssh/6s_deploy` redeploys. This entry does not chase the count further after this correction: the gate that catches the drift already exists and fires correctly on every cycle's `preflight.py` run, so a fresher recount belongs to whichever cycle next touches this section, not to a loop of same-day corrections that adds no new information beyond "the number moved."

**Widened 2026-09-25, scheduled operator cycle: the entry above had already gone stale by one commit, and that commit is the P0 footer-restoration fix, not a routine content push.** `gate_status_deploy_gap_count_current` fired on this cycle's own `preflight.py` run. Same build_id (`6a10df205a3d058c`), same resolved commit (`b8eca135`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-24T23:35:51Z`, so no new redeploy has happened since the last confirmation. A fresh `git log b8eca135..HEAD -- site/ Dockerfile` now finds four commits, not three: `2d8077fd` ("Restore the site footer to all 134 room and zone pages, and stop the gate that missed it from staying silent") landed after `6ba42a27` and was not counted. Real gap is now (4 commits, `ca49aa25`, `fa78db8c`, `6ba42a27`, `2d8077fd`; 198 files, 1089 insertions, 684 deletions per `git diff --shortstat b8eca135 HEAD -- site/ Dockerfile`). This one is worth flagging by name rather than only by count: `2d8077fd` is the fix for the live P0 defect found earlier this same day (all 134 room/zone pages shipping with no footer, no privacy/terms/accessibility/safety links, no newsletter form), so until a redeploy happens, production is still missing that footer even though the repository has carried the fix for hours. No new structural change; same standing limit, `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**RESOLVED 2026-09-25 05:4x, PM check-in: a session holding real access redeployed again, and the footer fix named above is now confirmed live.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`. Resolved the build_id to the commit that set it (`git log -Saa7c7e7e578e9a18 -- site/build-id.txt`) rather than trust the number alone: it is `890c43a3` ("Restore the footer, legal links and newsletter form to all 114 zone pages and 20 room pages"), an earlier, independent fix for the identical defect `2d8077fd` also fixed; the two produced byte-identical output (both build to `aa7c7e7e578e9a18`, confirmed by reading `site/build-id.txt` at each commit directly), so whichever one production is confirmed against carries the fix either way. `git log 890c43a3..HEAD -- site/ Dockerfile` returns zero commits: production matches HEAD exactly right now, footer included, no gap. Same standing limit as every entry above: this sandbox holds no `~/.ssh/6s_deploy` or VPS egress, so this closes again the moment the next `site/**` commit lands without a following redeploy, per `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) still being the only fix for the recurrence itself, not for this instance of it.

**Reopened 2026-09-25 07:1x, PM check-in: the same recurring pattern, one real customer-facing commit undeployed.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Verified with this repository's own `resolve_verdict_commit()`/`deploy_gap_material_commits()` directly rather than a fresh `git log` invocation: real gap is (2 commits, `ad310568`, `cb37d0c8`; 4 files, 439 insertions, 2 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). `ad310568` is a merge carrying no independent site content; the real one is `cb37d0c8`, B9's new free `site/entryway-deck.html` page, live in the repository but not yet served to a visitor. No P0 regression, just new content sitting undeployed. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25 08:0x, PM check-in: the entry above had already gone stale by one commit, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (3 commits, `ad310568`, `cb37d0c8`, `c6cc1a6a`; 5 files, 908 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). `ad310568` is a merge carrying no independent site content; the two material ones are `cb37d0c8` (B9's Entryway deck) and the newly landed `c6cc1a6a` (B9's Laundry Room deck, `site/laundry-room-deck.html`), both live in the repository, neither served to a visitor yet. No P0 regression, just a second new free page joining the first behind the same undeployed gap. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25 09:1x, PM check-in: the entry above had already gone stale by two commits, same recurring pattern.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (5 commits, `1b6439a7`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 6 files, 1372 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). Three are material: `cb37d0c8` (B9's Entryway deck), `c6cc1a6a` (B9's Laundry Room deck), and the newly landed `2cb970c1` (B9's Home Office deck, `site/home-office-deck.html`, third of five rooms). `1b6439a7` and `ad310568` touch only `site/build-id.txt`/carry no independent content, same as before. No P0 regression, just a third new free page joining the other two behind the same undeployed gap. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25, scheduled operator cycle: two more room decks landed, closing B9 in full; the gap is now every remaining room-deck page, not the first three.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (6 commits, `e6017e8b`, `f3ceca2e`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 8 files, 2376 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). Five are material: `cb37d0c8` (B9's Entryway deck), `c6cc1a6a` (B9's Laundry Room deck), `2cb970c1` (B9's Home Office deck), `f3ceca2e` (B9's Primary Bathroom deck), and this cycle's own `e6017e8b` (B9's Garage deck, `site/garage-deck.html`, the fifth and last room, closing B9 in full). `ad310568` is a merge carrying no independent site content, same as every prior entry. No P0 regression, just a fifth new free page joining the other four behind the same undeployed gap; all five room decks now live in the repository and none served to a visitor yet. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Widened 2026-09-25, PM check-in: the entry above had already gone stale by two commits, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`aa7c7e7e578e9a18`), same resolved commit (`890c43a3`); `ops/deploy-verdict.json` unchanged, `checked_at` still `2026-09-25T04:50:46Z` (no new redeploy confirmation since). Re-derived directly with `resolve_verdict_commit()`/`deploy_gap_material_commits()`: real gap is now (8 commits, `8f6c47b3`, `9c6d4063`, `e6017e8b`, `f3ceca2e`, `2cb970c1`, `c6cc1a6a`, `ad310568`, `cb37d0c8`; 8 files, 2376 insertions, 3 deletions per `git diff --shortstat 890c43a3 HEAD -- site/ Dockerfile`). One is newly material: `9c6d4063`, the fix for five room-deck pages sharing the Kitchen chapter photo as their social-media preview image (a real, live-facing correctness fix, still undeployed). `8f6c47b3` and `ad310568` touch only `site/build-id.txt` or carry no independent content, same as every prior entry's own build-id/merge commits. No new P0 regression beyond the standing gap; this is the same structural wait, just correctly sized. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**NARROWED 2026-09-25 14:2x, PM check-in: a session with real access redeployed again since the entry above, closing the Entryway and Laundry Room decks' half of that gap; three room decks and both fixes above remain undeployed.** `ops/deploy-verdict.json`, read directly rather than cited, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, superseding `aa7c7e7e578e9a18`. Resolved with `resolve_verdict_commit()` rather than assumed: it is `c6cc1a6a` (B9's Laundry Room deck). Confirmed with `git merge-base --is-ancestor` that both `cb37d0c8` (Entryway) and the merge `ad310568` are ancestors of `c6cc1a6a`, so that redeploy carried both of last cycle's "material" commits, not zero. Re-derived the remaining gap with `deploy_gap_material_commits(c6cc1a6a)` directly: five commits, `8f6c47b3`, `9c6d4063`, `e6017e8b`, `f3ceca2e`, `2cb970c1`; 8 files, 1476 insertions, 8 deletions per `git diff --shortstat c6cc1a6a HEAD -- site/ Dockerfile`. Three are B9 room decks not yet served to a visitor (Home Office, Primary Bathroom, Garage, the last three of five), one is the Kitchen-photo og:image correctness fix, one is a build-id restamp only. No P0 regression; the gap shrank, it did not close. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`.

**Reopened 2026-09-26 04:2x, PM check-in: the gap is real again, 3 material commits, and one of them is a real customer-facing honesty defect still live in production right now.** `ops/deploy-verdict.json` unchanged since the top-of-section RESOLVED note (build `d40585d97500a3ca`, `checked_at: 2026-09-25T14:15:05Z`, resolving via `resolve_verdict_commit()` to `8f6c47b3`); no new redeploy confirmation since. Re-derived with `deploy_gap_material_commits()` against that resolved commit directly, rather than a fresh manual `git log`: three commits, `ac1af6e7`, `ba73ec3c`, `223f5111`. `ac1af6e7` is internal (a `preflight.py` gate fix and a sitemap regeneration, no visible content change). The other two are customer-facing: `223f5111` links 44 room/zone pages to their decks (previously dead anchors), and `ba73ec3c` is the fix, shipped this same day, for `render_room()` claiming "not one product below carries a paying link" directly above real outbound `target.com`/`homedepot.com` links on all 20 room pages with a kit. That false disclosure is still what production serves until the next redeploy: the repository has carried the honest text for over an hour, and every visitor to a room page in that window has read the wrong claim. Same standing limit as every entry above: `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) or a session holding `~/.ssh/6s_deploy`; no sandboxed session here holds either (confirmed again, `~/.ssh` has no deploy key, `curl` to `6s-success.com` is rejected by the agent proxy).

Impact:

Autonomous agents cannot safely assume production architecture, health, release identity, backup state, or rollback capability.

Owners:

- `vps-docker-manager`
- `devops-sre`
- `github-manager`

Resolution:

Read-only discovery is done wherever it is reachable without a credential.
The remaining gap is Phil's own Redeploy click or a session holding the
deploy key; see `OWNER-ACTIONS.md` item 1b.

---

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

**Production Knowledge, RESOLVED 2026-09-25 14:15 UTC, this session: the gap closed again, and this time it was customer-visible.** *(Kept above the 14:2x entry below it, which carries a later clock time. That entry read the committed `ops/deploy-verdict.json` and correctly found it stale; this one ran `ops/deploy.py` and verified the live VPS. A later reading of a stale file is not a later state of the world, and on this page the reader needs the state of the world first.)* `ops/deploy.py` confirms production serves build `d40585d97500a3ca` (commit `5ff17fcb`), matching the repository, verified `2026-09-25T14:15:05Z` in `ops/deploy-verdict.json`. What had been behind was four room decks: Primary Bathroom, Laundry Room, Home Office and Garage all returned 404 live while the repository believed they shipped. After the deploy, all six deck pages return 200 and all six are linked from the live `deck.html` hub. Same standing limit as every prior entry: no operator sandbox holds the deploy key, so this closes again the moment the next `site/**` commit lands with no session to follow it; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself. Superseded: the 05:4x entry citing build `aa7c7e7e578e9a18`.

**Prior, REOPENED THEN NARROWED 2026-09-25 14:2x, PM check-in: RESOLVED 05:4x below went stale, caught by `gate_status_deploy_verdict_current` this cycle, and by the time this was checked a later redeploy had already partly closed the gap it should have named.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, resolving to commit `c6cc1a6a` (B9's Laundry Room deck), a full confirmation cycle later than the `aa7c7e7e578e9a18`/`890c43a3` pair the 05:4x note below cited. Full detail and the current 5-commit gap (three undeployed room decks, the Kitchen-photo og:image fix, one build-id restamp) are in `BLOCKER-001` below; not repeated here to avoid two sentences drifting apart again. Same standing limit as every prior entry: no operator sandbox holds the deploy key, so this closes again the moment the next `site/**` commit lands with no session to follow it; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` item 0, issue #35) is the only fix for the recurrence itself.

**Prior, RESOLVED 2026-09-25 05:4x, PM check-in: the gap named below closed again.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`, resolving to commit `890c43a3`. `git log 890c43a3..HEAD -- site/ Dockerfile` is empty: production matches HEAD exactly right now, including the footer restoration `BLOCKER-001` names. Superseded above once the next redeploy landed and the gap reopened.

**Prior (2026-09-25 00:1x, PM check-in): a newer redeploy confirmation than the one below was already sitting unread in `ops/deploy-verdict.json`, then went stale again within the same cycle, same recurring shape `BLOCKER-001` now names by pattern rather than by one date.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `6a10df205a3d058c`, `checked_at: 2026-09-24T23:35:51Z`, resolving via `git log -S` to commit `b8eca135` ("Micro zones: Laundry Room personalised"), a full confirmation cycle later than the `28ed2709194afab5`/`d5b0d5c8` pair this paragraph previously cited. One further site-affecting commit, `ca49aa25` (Phil's own "Micro zones: Garage personalised"), landed after that confirmation and moved `site/build-id.txt` again at HEAD; `git diff --quiet b8eca135 HEAD -- site/ Dockerfile` is dirty again (1 commit, 44 files). Production is therefore confirmed stale by exactly one commit again, not the four a recount against the older, superseded build would have shown. NO OPERATOR SANDBOX HOLDS THE DEPLOY KEY'S PRIVATE HALF OR EGRESS TO THE VPS (CONFIRMED AGAIN THIS CYCLE), SO THIS IS READ FROM THE COMMITTED VERDICT, NOT RE-CHECKED LIVE; `VPS_DEPLOY_KEY` (`OWNER-ACTIONS.md` ITEM 0, ISSUE #35) IS WHAT WOULD STOP THIS FROM BEING REDISCOVERED EVERY CYCLE.

**Prior (2026-09-24 21:2x, scheduled operator cycle): a newer redeploy confirmation superseded the 18:47:16Z one below, then went stale again within the same cycle.** `ops/deploy-verdict.json` then recorded `verdict: "current"`, build `28ed2709194afab5`, `checked_at: 2026-09-24T21:10:12Z`, matching commit `d5b0d5c8`. Superseded once a later redeploy confirmation (build `6a10df205a3d058c`) and a following site commit were found in the paragraph above.

**Prior (2026-09-24 19:2x, PM check-in): production redeployed and was confirmed current at that time.** `ops/deploy-verdict.json` then recorded build `4ec571da81db3b34`, `checked_at: 2026-09-24T18:47:16Z`, committed in `44ef380a` by a local session holding `~/.ssh/6s_deploy` (the same pattern this file has recorded on every prior redeploy; Phil did not click anything himself, see `OWNER-ACTIONS.md`'s own correction on this point). Superseded by the paragraph above once a later `site/**` commit landed and a later redeploy confirmed a newer build.

**Superseded entry, 2026-09-24, PM check-in: the 95-commit figure and the 914c2881 build citation below were both stale, and a newer, better confirmation than either already existed on GitHub unread.** LAST CONFIRMED CURRENT 2026-09-23T19:00:39Z (build `5eba61fde231c1a7`, per `ops/deploy-verdict.json`, a session with real production access that finished the Stripe SKU retirement and redeployed). `site/build-id.txt` at HEAD then read `4ec571da81db3b34`: 127 commits had landed since that confirmation (`git log 8e4c8e33..HEAD`), but the build side of that gap was closed, not open: `publish-image.yml` run 398 (`workflow_dispatch`-free, a plain push build, `https://github.com/Klingdom/6s-success/actions/runs/36032909521`) completed `success` at 2026-09-24T17:35:17Z against commit `accc9fff`, and `git diff --quiet accc9fff HEAD -- site/ Dockerfile` was clean, so the GHCR image already carried every fix named in BLOCKER-001, HEAD included. Only Phil's Hostinger Redeploy click (or a session holding the VPS key) remained, per `OWNER-ACTIONS.md` item 0/1b, until the paragraph above closed it.

**Business Data Knowledge, re-measured 2026-09-25.** ONE MEASURED TRANSACTION EVER ($19 GROSS, 2026-08-21, A REFERRAL). CURRENT TRAFFIC BASELINE (`GOALS.md`, MEASURED 2026-09-25 01:17 UTC BY A DIRECT UMAMI DATABASE READ, FILTERED TO THIS SITE'S `website_id`): 57 VISITORS ACROSS 144 VISITS AND 786 PAGEVIEWS IN 30 DAYS, DOWN FROM 68. AN UNFILTERED READ THE SAME NIGHT SAID 239 VISITORS, BECAUSE THIS UMAMI INSTANCE SERVES THREE SITES; `ops/experiments.py` NOW REFUSES A `website_event` QUERY THAT NAMES NO WEBSITE. IN UMAMI `session_id` IS THE VISITOR AND PERSISTS ACROSS DAYS, THE VISIT IS `visit_id`. STRANGERS' BUY-CLICKS SINCE 7 SEPT: 0 (`LEARNINGS.md` LRN-0010). THE EMAIL LIST IS READABLE, NOT UNREADABLE, AND MEASURED EMPTY: 0 SUBSCRIBERS (ISSUE #15, STILL UNRESOLVED, BLOCKS CAPTURE ENTIRELY).

**Executive Visibility:** LIVE, VIA `EXECUTIVE-DASHBOARD-LIVE.md` (GENERATED BY `ops/dashboard.py`, NOT HAND-TYPED)

**Immediate Focus:** UNCHANGED IN SUBSTANCE SINCE 2026-09-02, RE-CONFIRMED 2026-09-15: TRAFFIC, NOT ANALYTICS OR TECHNICAL DEBT, IS THE CONSTRAINT (`GOALS.md`). 2.5 VISITORS A DAY. THE CHANNELS THAT COULD CHANGE THAT (VIDEO PLATFORMS, LINKEDIN, PINTEREST, INSTAGRAM) NEED ACCOUNTS ONLY PHIL CAN CREATE (`OWNER-ACTIONS.md`); DISTRIBUTION PREP IS READY AND WAITING (114 ZONES OF VIDEO IN MULTIPLE CUTS, PINTEREST/INSTAGRAM CARDS FOR ALL 114 ZONES, ~4,939 READY-TO-PUBLISH SOCIAL UNITS TOTAL). SIX INDEPENDENT REVIEWS THIS WEEK FOUND NO SIGNIFICANT TECHNICAL DEBT; THE DOMINANT DEFECT CLASS FOUND INSTEAD IS A CORRECTED SOURCE WHOSE SHIPPED ARTIFACT WAS NEVER RE-DERIVED (`BACKLOG-2026-09-07.md` SECTION 7). THE HONEST STATE OF THIS BUSINESS IS "COMMERCE WORKS, TRAFFIC IS MEASURED AND NEARLY ALL DIRECT, AND PRODUCTION IS ONE `site/**` COMMIT BEHIND HEAD (LAST CONFIRMED 2026-09-24T23:35:51Z AT BUILD `6a10df205a3d058c`, PER `ops/deploy-verdict.json`, MATCHING COMMIT `b8eca135`; HEAD'S OWN BUILD ID IS NOW `6107bbf5797d990b` AFTER `ca49aa25`, SEE THE PRODUCTION KNOWLEDGE PARAGRAPH ABOVE), AND THE NEXT STEP ON EVERY DISTRIBUTION CHANNEL IS PHIL'S OWN ACTION." THIS SENTENCE PREVIOUSLY CLAIMED PRODUCTION WAS CURRENT WITH HEAD AT BUILD `28ed2709194afab5`; CORRECTED 2026-09-25 00:1x, PM CHECK-IN, ONCE A NEWER, UNREAD REDEPLOY CONFIRMATION AND A FOLLOWING SITE COMMIT WERE FOUND, THE SAME RECURRING PATTERN `BLOCKER-001` NAMES.

---

# Final Rule

`STATUS.md` must describe reality, not aspiration.

If something is unknown, write `UNKNOWN`.

If something is degraded, write `YELLOW`.

If something is broken, write `RED`.

If something is healthy, prove it.

The purpose of this file is to let every autonomous agent answer:

**Where are we now, what matters most, and what should happen next?**
