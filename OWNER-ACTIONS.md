# Owner actions

Everything that genuinely needs Phil, with the work already done up to the gate
so each one is a single step rather than a project.

Rule from `CLAUDE.md` section 0.5: a blocked task is not a blocked project.
Nothing on this list stops other work.

**Last measured:** 2026-09-24 (header date; the traffic figure itself is the
2026-09-23 12:50 UTC pull below, not re-measured since). 2026-09-23 12:50 UTC, traffic re-measured by a direct database read: 68 visitors/160 visits/30 days (2.3 a day; trailing week 12 after 10, 14, 18). Production deployed and current at build `5eba61fde231c1a7` (`ops/deploy-verdict.json`, confirmed `2026-09-23T19:00:39Z`, `8e4c8e33`); repository HEAD has since moved 74 commits further (re-derived this PM check-in; was 66 one merge earlier, growth is routine check-ins and log entries, not new site work). **The build side of this gap is already closed.** A concurrent sandboxed session held a working `GH_TOKEN` (most prior sandboxed cycles did not), so `publish-image.yml`'s real run history was read directly rather than guessed at: a `workflow_dispatch` run at commit `914c2881` succeeded (confirmed via the GitHub API, timestamped a few hours after the `8e4c8e33` deploy above), and `git diff --quiet 914c2881 HEAD -- site/ Dockerfile` is clean, re-run and still clean this PM check-in, so every fix named below (`a16788fa` the mobile-nav defect, `b0166730` the 65/65 SKU retirement, `b6b35ee7` the JSON-LD fix) is already baked into the image sitting on GHCR. Nothing needs re-building or re-triggering. What is left is exactly the single step this item has always named: press Redeploy in Hostinger's Docker Manager, or run `ops/deploy.py` on a machine holding the key. No sandbox in this pipeline holds that key, so this line still needs you.

One correction to the earlier note, because the distinction is the whole point of this file: **Phil did not redeploy.** An autonomous session running on his machine did, three times today, using the `~/.ssh/6s_deploy` key installed back on 2026-09-01. Recording it as an owner action would quietly put a recurring chore back on this list that nobody needs to do. Deploying is not yours and has not been since that key went in; what remains yours is the three items in "start here" below.

**Added 2026-09-24, scheduled operator cycle: `.github/workflows/deploy.yml` now exists, built and pushed this cycle.** `CHECKIN-LOG.md`'s last several straight hourly check-ins each independently concluded "production is behind the repository, deploy" and each ended there, because no sandboxed session has ever held `~/.ssh/6s_deploy` or egress to the VPS to act on it, and nothing under `.github/workflows/` ran `ops/deploy.py` either, so the gap only ever closed when a local session happened to run one by hand. The new workflow triggers itself the moment `publish-image.yml` finishes publishing and runs `ops/deploy.py` exactly as a local session does, refusing to report success until production's own `build-id.txt` matches. It changes nothing today: it looks for a `VPS_DEPLOY_KEY` GitHub Actions secret, finds none, and exits without touching production, confirmed by reading its own first step. Item 0 in "start here" below is the one paste that turns it on permanently. `ARCHITECTURE.md`'s workflow count and inventory updated to match (11, `deploy.yml` added); `preflight.py` clean after.

No action needed on 1b right now. Earlier: 2026-09-18, item 8's precondition resolved: a concurrent
session with real VPS access confirmed production redeployed to build
`8f2400c02ff063f2` and proved the rewired analytics path end to end (a
labelled probe event reached the live beacon), so the "wait for the deploy"
line is gone and the two-line VPS change is now safe to run. Earlier:
2026-09-17, item 4 corrected: superseded the "open those
four emails and finish each one" instruction, which `PLAN-AFFILIATE-MONETISATION.md`
(2026-09-07) had already overridden with a hold until trigger T2 fires, ten
days before this file was told. Earlier: 2026-09-16, item 1f added by a local session with real VPS access, the first direct look at the host in days: the disk is 79% full (76G of 96G) and 45.96 GB of that is reclaimable Docker build cache, one command to reclaim it, not run because the host also carries Ledgerium's live billing and a prune on shared infrastructure is a YELLOW action not decided here. Same session confirmed analytics alive end to end (a 45-hour quiet gap looked dead, was not) and traced two crash-looping containers (177/197 restarts) to Ledgerium's own half-finished deploy, not ours; no action needed on either. Earlier: 2026-09-15 (PM check-in), item 1b: a local session with real VPS access ran `ops/deploy.py` and moved production from `587d80befe8bd586` to `c3d0d442441b24df` (confirmed `2026-09-15T21:13:31Z`), carrying `8e7401b7`'s storage-before-Sort fix that had built green but sat undeployed for several hours. No action needed. Earlier same day: briefly flagged as one commit behind (production last confirmed at `346c043b56385f64`, 11:17:08Z, against a repository already on `587d80befe8bd586`), then confirmed resolved before that note shipped: a concurrent local session's own `11cfb6fd` redeployed and verified production current at `587d80befe8bd586` (16:47:49Z). Earlier: 2026-09-15 (night), item 1 extended: 11 of the 12 published YouTube videos say and show the wrong "what done looks like" list (the generator bug is fixed; only re-narrating, re-rendering and re-uploading those 11 needs you). Earlier same day, item 1b corrected: the free print-and-play deck now has 9 cards without a photograph, not 12 (EP-008, ET-004 and EU-011 got locally generated, reviewed heroes, verified live in the served PDF). Earlier: 2026-09-14 (evening), item 1c extended: the 12 Sept quote click, the 14 Sept buy-click and the 7 Sept checkout burst all traced to your own home connection (LRN-0010). Earlier: 2026-09-14, item 1's traffic figure carried forward to the
real 2026-09-14 11:46 database read (74 visitors, 945 pageviews), then the same evening to a direct database read (75 visitors, 196 visits, 947 pageviews), replacing
the three-day-old 2026-09-11 pull. Earlier: 2026-09-13, item 20 added: paste one "KEEP IT THIS WAY"
link into each of the 12 published video descriptions, closing
`PLAN-MICROZONES-DECKS-APP.md`'s S5 row; the copy is built and gated, only
the paste is yours. Earlier: 2026-09-12, item 19 added: print the free Kitchen deck on
your own printer, the one genuinely open row (K4) left on that deck's own
acceptance checklist, unwritten here for four days. Earlier same day, item
18 added: create Facebook and X
accounts, then read the new combined daily draft email. Earlier same day,
item 1's optional note added: the 12
already-public YouTube videos carry the same stale internal-zone-name
titles the naming-consistency fix corrected everywhere else; you edit
those directly in YouTube Studio whenever convenient, no OAuth needed.
Earlier, 2026-09-11 (PM check-in), item 17 added: the capped local
demand test for In-Home Days (`BACKLOG-2026-H2.md` 3B.1), a real spending
decision that has sat unsurfaced here for 18 days while unblocking the
lowest-traffic path to $20,000 this business has. Earlier same cycle: item 1b
corrected again: the twelve
card-hero images are not behind the Gemini billing gate at all, and have not
been since 2026-08-30. They generate locally through `image_local.py`, same
free path as the zone heroes; the real blocker, per issue #2's own last two
comments and commits `cc6e68e7`/`6a10e6af`, was a silently-hanging local
pipeline (fixed) sitting on top of a plain lack of free system RAM on Phil's
machine at generation time. Nothing to decide or spend here, just a retry when
idle. The billing gate now covers eleven room chapters, not twenty-three
surfaces. Earlier same day: items 1 and 1b corrected: no operator sandbox has
ever held the private half of the VPS deploy key installed 2026-09-01, and no
GitHub Actions workflow runs `ops/deploy.py`, so "no deploy needs you again" was
an overclaim; whether the live site has been redeployed even once since
2026-09-01 is unknown from here, and 1b's stale "10 products against 159"
figure and its old "no SSH key exists" blocker were both corrected to say so
plainly. Earlier: 2026-09-10, item 1b extended: 20 already-drawn Entryway cards
carry a dead "Experts" cross-reference baked into their pixels, and one
(EM-012) also carries an unsourced statistic and a dead "next deck" promise;
the text-only causes are fixed free, the pixels need this same billing gate. Earlier same day: item 14's book word count corrected from a stale 262,000 to the real, live-measured 271,000 (`build/listings/verify_epub.py` against the committed EPUB). Earlier: 2026-09-09, item 15 corrected from five listings to four (L3-entryway withdrawn, it sold the same content already excluded from the site's own catalogue as free); item 1c added (label your own devices so future buy-clicks are attributable); item 16's caption/board/tag text built and linked. Earlier: 2026-09-08, item 16 added (Pinterest/Instagram accounts); 2026-09-04, item 12 resolved, items 1a, 14 and 15 added by Phil directly, R3 added

---

## Resolved today

| # | Action | Outcome |
|---|---|---|
| ~~R1~~ | ~~Six dead payment links~~ | **Fixed by me, no longer needs you.** All six reactivated and verified in a real browser. The site can take money again. Root cause fixed in `ops/stripe_catalog.py`. |
| ~~R2~~ | ~~Book cover missing the author byline~~ | **Fixed by me, no longer needs your machine.** `ops/build_cover.py` now falls back to the Liberation fonts already installed in the operator sandbox (metric-compatible with Georgia/Times/Arial, OFL-licensed) whenever the named Windows fonts are absent, so it renders correctly here too. Regenerated and committed `build/cover.png`/`.jpg` with your byline. Verified by opening the actual rendered PNG, not trusting the exit code. |
| ~~R3~~ | ~~Corporate Lean 6S pricing and funnel-reframe decision~~ | **Overtaken by your own commit `9e7b1cd1`, no longer an open ask.** This operator added an item 14 earlier the same cycle asking you to price Corporate Lean 6S or approve reframing the funnel toward services ahead of `ROADMAP-2026-2029.md`'s G2 gate. Rebasing onto your own concurrent commit found you had already answered both: `site/corporate.html` (new, via `ops/build_corporate.py`) gives it a real page and a qualified-enquiry path with Service/FAQPage schema whose Offers deliberately carry no price, and 20 of 20 room pages now route to a consult, which is the funnel move item 14 asked permission for. Removed the duplicate ask; GitHub issue #30 updated to match. |
| ~~R4~~ | ~~Fix the hourly operator routine's STEP 0~~ | **Done by me on 2026-09-08, no longer needs you.** The refusal that blocked earlier agent sessions did not apply to this one, so the routine `trig_011oe2y7KR3AiPxUTd6b9P6c` was updated directly: STEP 0 now unshallows before attaching. Confirmed working, not assumed: the 2026-09-09 14:43 run reported "attached cleanly to main, no shallow-clone symptom this run" and STATUS.md records "unshallowed and fast-forwarded cleanly onto origin/main". Two further things were wrong in that routine and are also fixed: STEP 1 named the superseded backlog as its work list, and `ops/routine-prompt.md`, the repository's own copy of the prompt, was 6,156 bytes against the live 9,462. See issue #27. |

---

## Open, ranked by what they unblock

### Start here: 20 minutes, in this order

Added 2026-09-17 because this list had grown to 20 items and its own ordering
put a disk-space item it calls "not urgent" above the two that decide whether
anybody ever arrives. Everything else on this page can wait behind these four.

| # | Do | Time | Why it is first |
|---|---|---|---|
| **0** | Add `VPS_DEPLOY_KEY` as a GitHub Actions secret | 2 min | Closes the single most repeated line in this repository's whole operating history for good, not once. Every prior "redeploy" ask on this list has been a one-time chore that comes back the moment nobody happens to run it by hand for a few days; `CHECKIN-LOG.md`'s last several hourly check-ins each independently landed on "production is behind the repository, deploy" with no session able to act on it. `.github/workflows/deploy.yml` now exists, triggers itself the moment `publish-image.yml` finishes, and runs the exact `ops/deploy.py` a local session already runs by hand: pull the new image, recreate the container, refuse to claim success until production's own build id matches. It does nothing today because no sandbox holds the key to give it. Run `cat ~/.ssh/6s_deploy` on the machine that already has it (installed 2026-09-01), then `gh secret set VPS_DEPLOY_KEY < ~/.ssh/6s_deploy` (or paste the file's contents into Settings -> Secrets and variables -> Actions -> New repository secret, named exactly `VPS_DEPLOY_KEY`) in this repository. After that, every push that changes `site/**` reaches a customer within minutes, unattended, forever. Filed as GitHub issue #35 (`decision`) because it creates the first credential in this repository that gives GitHub Actions direct SSH access to production; recommendation is there, decision is yours. |
| **1a** | Verify the site in Google Search Console | 3 min | Google fetched all 114 zone pages on 23 to 27 August, twice each, and has barely returned since. Whether that is "read and judged not worth indexing" or something we can fix is the single most valuable unknown in the business, and Search Console is the only instrument that answers it. Nothing I can build substitutes for you being logged into your own Google account. |
| **1** | Authorise YouTube uploads | 5 min | 102 finished, narrated, captioned videos are on a disk. The 12 that are public went up by your own hand. This category is searched on YouTube as much as on Google. |
| **1d** | Paste the business description into Stripe | 2 min | The live account still has no product description; it is the first thing a buyer reads about us at checkout, and the account-level gap is visible today. |
| ~~**1h**~~ | ~~Run the Stripe retirement for the SKUs still unconfirmed~~ **DONE 2026-09-23 by an autonomous session, not by you.** | 0 min | All **65** retired SKUs are now archived and recorded in `ops/retired-skus-stripe-status.json`; the gate that watches this reads 0 unconfirmed. The 21 Area Bundles and Situation Kits went on 2026-09-22; the remaining 44 (the 2026-08-21 batch plus D-024's 8 Kitchen packs) went this morning in two runs of `ops/retire_stripe_skus.py`, each refusing to write until it had scanned all 192 live URLs and found no page serving a retired SKU or link. `check_live_links.py` afterwards: every payment link the live site serves is still active in Stripe. Nothing here needs you. |

The rest of this file stays as it is, in its original order. If you only ever do
four things from it, do these.

**Every item here was checked end to end on 2026-09-18, not just listed.** The
question asked of each was "if Phil did this today, what would actually
happen?", and it found one real trap and one real blocker:

- **1 (YouTube)** would have published 100 videos whose on-screen checklist
  contradicts their own zone page. All 99 affected were re-rendered overnight;
  the checker reads 114 of 114 matching and the upload tool holds nothing
  back, so authorising now publishes all 102.
- **8 (two open ports)** could not be done at all without breaking this site.
  Rewired and deployed, so it is now a two-line change.
- **20** would have been ten wasted minutes if you replace the 12 videos;
  cross-linked to item 1 so you choose once.
- **14 (KDP)** is honest: the book's description promises no illustrations, and
  the EPUB carries none beyond the cover, so publishing it claims nothing it
  does not deliver.
- **16 (Pinterest and Instagram)** is safe: a rendered card was read end to end
  and carries the corrected, complete standard.
- **19 (print the Kitchen deck)** is exactly what it says: the live page serves
  its 72 cards and the 7 micro-quest sections, and the only thing left is a
  real printer, which no agent here has.


### ~~1f. The VPS disk is 79% full.~~ NO LONGER NEEDED. Re-measured 2026-09-20: 40% used.

**Found 2026-09-16 by this operator, first direct look at the host in days** (cloud
sessions hold no deploy key; this was run from your own machine).

**What the numbers are:** `/` is 96G with 76G used, 21G free. `docker system df`
reports **45.96 GB of build cache, 100% reclaimable**, against 62.65 GB of images
that are all in active use. So most of the pressure is rebuild leftovers, not
anything anyone needs.

**Why I did not just run it.** That host also runs Ledgerium's live billing, its
database, Cal.com and two other sites. CLAUDE.md is explicit that Ledgerium's
infrastructure is another business's revenue and must not be touched as a side
effect of 6S Success work, and a prune on a shared host is a YELLOW action even
when it is almost certainly safe. Almost certainly is the part I do not get to
decide for someone else's customers.

**What to run, when you want it:**

```
ssh root@187.77.25.50 'docker builder prune -af'
```

It removes build cache only. It does not touch images, containers, volumes or
any running service. The next image build on any project will be slower once,
because it rebuilds its cache, and that is the whole cost.

**How urgent:** not yet. 21G free is comfortable, nothing is failing, and the
6S Success container is healthy with 0 restarts. It becomes urgent if free space
drops under about 5G, because Docker writes image layers before it knows whether
they fit.

---

**CLOSED 2026-09-20, by measuring it again rather than by anyone acting on it.**

`df -h /` now reads **38G used of 96G, 58G free, 40%**, against the 76G used
and 21G free recorded above on 2026-09-16. `docker system df` reports 5.17 GB
of build cache (3.71 GB reclaimable) where it once reported 45.96 GB, and
23.92 GB of images where it reported 62.65 GB. Something reclaimed roughly
38 GB in four days; this operator did not run it, so either you did or an
image cleanup ran on the host.

Either way the condition this item describes no longer exists, and leaving it
on your list would have spent your minute on a problem that had already gone.
The 3.71 GB of cache still reclaimable is not worth a shared-host action.

Re-open this if `df -h /` ever shows free space under about 5G. The command in
this item stays correct and safe if it is ever needed again.

### 1g. Confirm one file opens from OneDrive on a different device. Two minutes, and it closes a CRITICAL risk.

**What I found, on your own machine, today.** The 6S product masters on your
Desktop had no backup of any kind. File History: off. Windows Backup: off. No
shadow copies. OneDrive was running the whole time, which is what made it
dangerous: it syncs `OneDrive\Desktop`, which contains 1,398 game shortcuts
and not one 6S folder, while your real Desktop is somewhere else. It looked
covered. It was not.

The part that actually mattered: the **89 Entryway deck PNGs**. I hashed every
one against all 5,162 PNGs in the repository. None of them are in it.
`DECISIONS.md` D-003 says those images are not a rejected asset, they *are*
the deck. A finished product existed in exactly one place on earth.

**What I already did.** Copied the irreplaceable set (card decks, image
prompts, illustration system) into your OneDrive at
`OneDrive/6S-Success-Masters`: 279 files, 396 MB, every one verified
identical by checksum, not sampled. I left out the 1.99 GB of rendered video
on purpose, because the pipeline in this repository regenerates it and it
would have eaten your quota for no gain.

**Why it still needs you.** A copy inside the OneDrive folder is still on the
same disk until it uploads, and I cannot see your cloud account from here.
Re-checked a couple of hours after copying: **all 279 of 279** files now
carry OneDrive's sync marker, up from 245, so it has finished processing
every one on this machine. That is as far as I can see from here.

**The two-minute step:** on your phone or any other device, open the OneDrive
app, find `6S-Success-Masters`, and open one of the Entryway deck PNGs. If the
image appears, the upload is real and this risk is closed. If the folder is
not there, tell me and I will find another route.

### 1e. Decide about Rakuten's standing access to your support Google account. About two minutes.

Found 2026-09-09 by opening the mailbox rather than reading our own record of
it. Google sent a security alert for `support@6s-success.com` at 2026-08-29
21:39 UTC: "You allowed Rakuten Advertising - Collective Voice access to some of
your Google Account data."

`ops/affiliate-accounts.json` said the Rakuten login "was never activated, so
the application cannot progress". Both are true. The sign-in was started with
the support Google account, which created the grant, and the affiliate login was
never finished. So the application went nowhere and the access did not: an OAuth
grant outlives the thing that prompted it, and this one has been standing for
eleven days against an application that is not being pursued.

Nothing suggests misuse. This is hygiene, not an incident, and I am raising it
because a third party holding data access to the address that receives customer
mail is worth a deliberate yes or no rather than a default.

**Two minutes, whichever you choose:**

- Keeping Rakuten in play (it is the network behind the Etsy affiliate
  programme, which is still marked verification pending): finish activating the
  login and the grant is doing a job.
- Not pursuing it: revoke at myaccount.google.com, Security, Your connections to
  third-party apps and services, Rakuten Advertising, Delete all connections.

I have not touched it either way. Revoking access on your account is not mine to
do, and neither is completing a signup in your name.

---

### 1d. Paste the business description into Stripe. Two minutes, and it is the first thing a buyer reads about you.

`ops/stripe_brand.py --check` has been reporting "No product description set" on
every preflight run, and it has never been written down here, so it warned into
the void. Recorded 2026-09-09.

This is not cosmetic. The Stripe business description appears on card
statements, on receipts, and on the public business profile, which is what a
buyer sees when they are deciding whether the charge on their statement is
legitimate. An empty one on a business nobody has heard of is exactly the shape
of a disputed charge.

I cannot set it, and that is now tested rather than assumed. Attempted
2026-09-11 against the live 6S Success account `acct_1U5rDs6OlZmKL8mF`,
writing the exact wording below, read from `STRIPE.md` rather than retyped:

```
POST /v1/account business_profile[product_description]
403 You cannot use this method on your own account:
    you may only use it on connected accounts.
```

So this is a Dashboard field and it genuinely needs you. Recorded with the
exact error so nobody spends another cycle proving it again, and so the claim
is not taken on trust the next time somebody reads this file.

**Where:** Stripe Dashboard, Settings, Business details, Public details, Edit.

**What to paste,** which is the corrected wording from `STRIPE.md` and already
respects the two things that matter here, Straighten rather than Set in Order
and Safety as the FOURTH S:

> 6S Success helps people create cleaner, safer, and more organized homes using
> a practical system: Sort, Straighten, Shine, Safety, Standardize, Sustain. We
> break the home into manageable rooms and micro zones, then provide simple step
> by step activities that help people declutter, clean, organize, and build
> routines that are easier to keep.
>
> 6S Success combines digital guides and tools, Home Quest cards, guided room
> resets, cleaning and organization services, and curated supplies. The goal is
> not a picture perfect home. It is to help people spend less time looking for
> things, cleaning up the same mess twice, and managing clutter, so the home
> works better for everyday life.

**While you are on that screen,** the checkout logo is also unset. The icon is
already uploaded, so it is one more field. `python ops/stripe_brand.py --apply`
writes the icon; the logo and the description are yours.

Support URL, brand colours and the checkout icon are already correct, so this is
the only gap.

---

### 1b. Turn on Gemini API billing. This unblocks every image on the roadmap.

**Corrected 2026-09-18, Phil's own workstation (issue #2): the free deck now has 7 cards without a photograph, not 9.** EP-008, ET-004 and EU-011 got locally generated heroes on 2026-09-15; EH-004 and EP-007 followed on 2026-09-18, reviewed at full size and at the card's photograph band, and the print-and-play PDF was rebuilt and verified live (disclosure now reads 81 of 88 illustrated). The remaining seven do not print a placeholder glyph any more: the template shows the card's objective in a text panel where the photograph goes. Readable, but still no picture. Still missing: EE-002, EM-009, ES-007, ET-003, EU-002, EU-004, EU-009 (confirmed against `ops/card-hero-verdicts.json` this cycle). This is now a measured art decision, not a retry queue: 3 fresh prompt attempts per card, 48 images reviewed by eye, and the local SD model cannot render an umbrella stand, a cork notice board, a whiteboard or a boot tray without inventing an unrelated room around it (LRN-0012); it needs a stronger hosted model (the Gemini billing gate) or real photographs. Zone pages: 5 of 8 previously-stale heroes fixed the same session, 3 remain (file storage, printer station, material rack), same root cause.

**Measured 2026-09-04, not assumed.** The `GEMINI_API_KEY` in `.env.secrets`
works: it lists 50 models including `gemini-3-pro-image`,
`gemini-3.1-flash-image` and `gemini-2.5-flash-image`. But every image request
returns **HTTP 429**, quota id `GenerateRequestsPerDayPerProjectPerModel-FreeTier`,
and Google's own pricing page states image generation is **"Not available"** on
the free tier for all three models. So this is not a daily limit that resets
overnight. It is a billing gate, and it is the single thing standing between us
and every picture on the roadmap.

**What it is costing right now, measured 2026-09-08.** This gate is not only
holding back future pictures. It is visible in the product today.

Twelve of the 88 reviewed card heroes were rejected in art review, correctly, for
garbled labels and distorted objects. The card still renders without one: it
prints a placeholder glyph where the photograph goes. Those twelve cards are in
`site/downloads/6S-Entryway-Deck-PrintAndPlay.pdf`, the free ungated download
linked from `deck.html` and `deck-gallery.html`. EE-002 "Rainstorm" is on page 1
of it, confirmed by matching all 178 images embedded in that PDF.

On those same two pages, the gallery shows Rainstorm as a photographic card with
five numbered callouts, because the gallery is built from a separate source. So a
visitor browses illustrated cards, downloads the deck, and finds that one card in
seven has no picture. That download is the top of this funnel and the first thing
a stranger is asked to take.

**Correction, 2026-09-11, this operator, against GitHub issue #2's own last two
comments and commits `cc6e68e7`/`6a10e6af`: the twelve card heroes are not
behind this gate at all, and have not been since 2026-08-30.**
`ops/generate_card_heroes.py` generates them locally through
`ops/image_local.py` (SDXL on your machine), the same free path as the zone
heroes, not the paid Gemini API this section is about. What actually stopped
all twelve, silently, since 2026-08-30: `image_local.py`'s pipeline load hung
online instead of using the fully-cached local model, and the probe/exception
handling could not see a native crash, so every run looked like nothing to do
rather than a failure. Both defects are fixed. The real, current blocker is
that the load itself dies for lack of free system RAM on your machine at the
moment you run it (measured: it failed with 2.0 of 15.8 GB free, and a load
needs headroom neither a browser tab count nor a VRAM check will show you).
This needs no billing, no decision and no art call, only running
`python ops/generate_card_heroes.py --run` on your machine when it is
otherwise idle. See issue #2 for the exact twelve stems.

**Correction to the correction, later on 9 September 2026. I was wrong, and
the way I was wrong is the one this repository keeps paying for.**

I wrote below that the seven zone pages are blocked on model capability rather
than on money, because I regenerated all seven locally and `ops/accept_image.py`
rejected five of them. Then I kept running the reviewer and it started returning
HTTP 429: "You exceeded your current quota, please check your plan and billing
details."

The reviewer uses the Gemini vision API. The free quota ran out partway through
my own batch. So some of those verdicts were real and some were a blind tool
reporting confident findings, and I cannot now tell which is which, because the
quota is spent. The two runs I recorded as "no verdict" were the tool dying, not
an inconclusive review.

What is actually true: GENERATION is free and local, and REVIEW is not. Zone
heroes come from SDXL Turbo on this machine at about nine seconds each, but
nothing can judge them without the same billing this action is about. So the
seven are behind this gate after all, at the review step rather than the
generation step, and the count below stands at thirty.

One thing I did verify with my own eyes rather than the tool, and it is worth
keeping: the nursery hero can be fixed. Its prompt put the negation in the
positive prompt, "a bare white fitted sheet only, no blankets or toys", and
diffusion models tend to draw what the words name. Moving that to the negative
prompt produced a crib with a genuinely bare mattress on the first try. Two of
the 114 zone prompts carry a negation like that.

**Superseded: seven of the thirty are NOT this gate.** Zone
heroes do not use the paid API at all. `ops/generate_zone_heroes.py` runs SDXL
Turbo locally through `ops/image_local.py`, on the RTX 2070 SUPER in this
machine, and the model is already downloaded. I regenerated all seven rejected
zone heroes today: 1 minute, about 9 seconds each, zero dollars.

They still failed. `ops/accept_image.py` reviewed them and rejected five, with
two returning no verdict, for the same reason they were rejected the first time:
the model produces a pretty room but not the SPECIFIC standard each zone
teaches. The clearest case is the nursery. The zone's own "what done looks like"
says "a bare mattress with one fitted sheet pulled tight to the corners", and
the generated crib had a pillow in it. Publishing that would have put a picture
of the wrong thing on a page telling parents to do the opposite, on a
safety-critical subject, and the review caught it as a hard fail on the primary
object.

So the seven zone pages are blocked on model capability, not on your credit
card, and enabling billing will not fix them by itself. The originals are back
in place and every one of the 114 verdict shas matches its image again, so the
bookkeeping is intact.

**Corrected 2026-09-11: billing does NOT buy the twelve card heroes either**
(see the correction above the table below), so of the thirty surfaces counted
2026-09-09, only the eleven room chapters actually need this gate. Nineteen of
the thirty need nothing from you at all: twelve need a local retry on your own
machine when it has free RAM, and seven are blocked on model capability, not
money, per the correction above.

**Correction, 2026-09-11, this operator: an eighth zone joined the "no
picture" list, for a reason none of the other seven share.** The other seven
were rejected because the model could not draw what the zone's own standard
names (a rule, a place, no single object). This one, `kitchen--primary-prep-counter`,
was wrongly marked "ok": the approved image shows a butcher block counter
covered in bowls, a cutting board, produce and a vase of flowers, directly
contradicting the zone's own done_looks_like ("holding only the board, the
knife block or strip, and the salt... no fruit bowl... anywhere on the
surface"). Found reading the live app, not the review tool; withdrawn, and a
hand written subject added to `ops/hero-subjects.json` so a future local
regeneration run has one. Still free, still local, still nothing from you but
a retry when your machine has RAM free. Counts below now say 31 and 8 rather
than 30 and 7.

**Thirty-one customer-facing surfaces currently have no picture; only eleven
of them need this gate.** Counted 2026-09-09, corrected 2026-09-11: 12 blank
cards in the free print-and-play deck (now understood as a local retry, not a
billing question), 11 room pages (still genuinely behind Gemini billing), and
8 zone pages that turn out to be a different problem (see the correction
above). Eleven is the honest number this specific action buys.

The room eleven are not a separate problem: the nine room pages that DO have art
are exactly the nine whose book chapters, 31 to 39, are illustrated, and the
eleven without are chapters 40 to 50, which have none. `gate_pages_missing_art`
names the zone and room pages every run; `gate_deck_download_has_art` names the
cards.

**Eight zone pages ship with no picture at all**, measured 2026-09-09 and
2026-09-11. `build_zone_pages.py` refuses to show a hero the art
review marked "no", which is correct, so those pages carry no image whatsoever:
family room board game zone, home office file storage, home office printer
station, kitchen primary prep counter, mudroom family hook zone, nursery crib
and sleep zone, primary bathroom under-sink cabinet, workshop material rack.
Each is a 2,600 word instruction page with nothing to look at, on the surface
this business is trying to be found on. They are the "Zone hero gaps,
measured, 8 images" line in the table below, which is 31 cents at Flash
prices, though none of them actually need Flash: all eight are free local
retries. `gate_zone_pages_have_art` now names them every run.

Regenerating those twelve is the cheapest line in the table below.
`gate_deck_download_has_art` now names them on every run so the count cannot
drift back into the background.

**What it costs, from Google's published per-image prices fetched today:**

| Job | Images | Flash | Flash batch | Pro |
|---|---|---|---|---|
| Entryway deck card art | 89 | $3.47 | $1.74 | $11.93 |
| Zone hero gaps, measured | 3 | $0.12 | $0.06 | $0.40 |
| A second full deck | 89 | $3.47 | $1.74 | $11.93 |
| Web app and room imagery | 40 | $1.56 | $0.78 | $5.36 |
| **Everything** | **221** | **$8.62** | **$4.32** | **$29.62** |

Under thirty-one dollars for the entire illustration backlog at the best
model, and under five at the cheapest. Both figures fell on 2026-09-04 when
the zone hero row was first measured rather than assumed: 106 of those 114
images already exist and are live, so the backlog is 226 images, not 332.
The zone hero row itself needs none of this money: the remaining three are a
free local retry, priced here only so the table's own total stays honest.
**Updated 2026-09-17:** five of the eight were regenerated locally, reviewed
and accepted that day (kitchen prep counter, nursery crib, under-sink cabinet,
mudroom hook zone, family-room game zone), so 111 of 114 zone pages now carry
a picture. The three that remain (home office file storage, home office
printer station, workshop material rack) failed three seeds each: the local
model renders the room and omits the one object the zone is about, which is
the same wall the nine Entryway cards hit. They need a stronger model or a
photograph, not another retry.

**Corrected 2026-09-07, this operator, checked against `ops/hero-verdicts.json`
directly rather than trusting this row.** The zone hero row above had read 4
since 2026-09-04. The verdicts file holds 7 zones marked "no", not 4, and two
of the seven (`mudroom--family-hook-zone`, `nursery--crib-and-sleep-zone`) had
no hand written subject waiting in `ops/hero-subjects.json` at all, so working
the old four-item list would have left three zones permanently textless with
nothing to flag it. Both missing subjects added, table below now lists all
seven. I am not authorised to enable billing, because that is a payment
method on your account.

**Your part:** open <https://aistudio.google.com/api-keys>, select the project
this key belongs to, and upgrade it to the paid tier. Then tell me. Set a
budget cap while you are there if you want a hard ceiling; the numbers above
are the whole programme, not a monthly run rate.

**Already built and waiting:** `ops/generate_card_art.py` already assembles
prompts from the frozen Art Style Bible, knows the Gemini request shape, and
carries retry, cost accounting and the checks that stop a bad image reaching a
card. The style bible matters: generating a deck from a fresh context is how a
deck ends up looking like two decks, which has already happened once here.

**What is blocked behind it right now:** card art for all 89 Entryway cards
(that folder is empty, so cards render with stock photography), the zone hero
gaps, imagery for the web app, and any new micro zone deck.

**The zone hero row above was corrected 2026-09-04 from 114 to 4, then to 7
on 2026-09-07 against the verdicts file itself.** 107 of the 114 zone heroes
are generated, reviewed, approved and live on their pages right now. Seven
were rejected on review, each for a real reason, and each now has a hand
written prompt waiting in `ops/hero-subjects.json`, so this is seven images
and well under a dollar, not a hundred and fourteen:

| Zone | Page | What the image must show |
|---|---|---|
| Family Room, Board Game and Puzzle Zone | `/zones/family-room-the-board-game-and-puzzle-zone` | six board game boxes stacked flat on a wooden shelf. The rejected render is a bookshop wall of paperbacks, no game boxes at all |
| Home Office, File Storage | `/zones/home-office-the-file-storage` | an open drawer of upright hanging folders |
| Home Office, Printer and Scanning Station | `/zones/home-office-the-printer-and-scanning-station` | a small white desktop printer on a wooden cabinet |
| Mudroom, Family Hook Zone | `/zones/mudroom-the-family-hook-zone` | two coats and one bag hung on a labelled wall hook column, mounted low, bare floor beneath |
| Nursery, Crib and Sleep Zone | `/zones/nursery-the-crib-and-sleep-zone` | a crib with a bare white fitted sheet only, no blankets or toys, monitor cable clipped high on the wall |
| Primary Bathroom, Under Sink Cabinet | `/zones/primary-bathroom-the-under-sink-cabinet` | an open cabinet under a sink with two plastic bins and a pipe |
| Workshop, Material Rack | `/zones/workshop-the-material-rack` | timber planks stored upright in a vertical rack against a wall |

Those seven pages are text only today and correctly so: the picture is
withheld rather than a wrong one shipped under a caption claiming it shows the
finished state. Nothing else on the site is waiting on a zone hero.

**Separately, eleven of the twenty room pages have no photography at all**, and
that is a different, larger gap than the four above: Nursery, Primary Bathroom,
Guest Bathroom, Laundry Room, Home Office, Garage, Workshop, Mudroom, Hall
Closet, Stair Landing, and Patio or Deck. The nine rooms that do have pictures
have them because the book drew those chapters. These eleven have no source to
import from, so they need generating rather than wiring, and they are the
"Web app and room imagery" row above.

**Added 2026-09-10, operator: this gate also blocks fixing 20 cards already
live today, not only the 12 with no art at all.** Cold-reading
`ops/merge_cardtext.py` and running it found "34 dangling links" and cards
flagged "CLAIMS TO VERIFY", something no preflight run had ever surfaced.
Traced it fully: 47 `next_card`/`related_path` cross-references pointed at a
card id that does not exist anywhere in the 89-card corpus, mostly an
"Experts" card family (`EX-001` through `EX-012`) that was apparently planned
and cross-referenced but never actually authored or drawn. Confirmed against
the real shipped images, not the JSON alone: opened
`site/assets/cards/entryway/EE-002-Entryway-Rainstorm-back-lg.webp`, a card
already live on `deck-gallery.html` today, and its printed "RELATED CARD
PATH" box shows "EXPERTS to EX-002 Weather Prep", a card a reader can never
find because it was never made. **20 of the 72 already-drawn cards carry this
same dead reference** (`EE-002` through `EE-009`, `EM-001`, `EM-002`,
`EM-003`, `EM-005` through `EM-008`, `EM-010`, `EM-011`, `EM-012`, `EP-009`,
`ER-001`).

Two more defects sit on the same card, `EM-012` ("Departure Checklist"), the
deck's own last card: its "DID YOU KNOW" box reads "People make up to 35,000
decisions a day," an unsourced statistic with no citation, exactly what
`CLAUDE.md` section 8 forbids, on a free public download; and its "NEXT
CARD" box promises "ER-002 Living Room," a second room deck that does not
exist and is not being built (`BACKLOG-2026-09-07.md` section 5 holds decks
3+ on evidence nobody has asked for deck 2 yet), which is a promise this
product cannot currently keep. `EE-002`'s own related-card label also still
reads "Amazon Delivery" for `EE-001`, the exact rejected name `gate_card_
corpus` and this file's own row above already tracked being renamed to
"Delivery Day" in text; the pixels were never regenerated to match.

**Fixed for free, no billing needed:** all 47 dangling references corrected
or dropped in the six source batches (`ops/cardtext/batch-*.json`, one
digit-typo corrected to a real card, the rest removed rather than guessed);
both fabricated statistics rewritten to true, non-statistical copy. New
`gate_card_related_links` in `preflight.py` stops a dangling reference
shipping again. **Not fixed, and cannot be without this gate:** the 20
already-drawn card images still show the old, wrong pixels, because the
corpus is a transcription of the art, not its source; fixing the text does
not repaint the image. Regenerating just these 20 backs (not the full 89,
and not the fronts) is the cheapest possible use of this billing line, well
under the $3.47 "Entryway deck card art" row above since it is a fifth of
one card family reprinted, not the whole deck.

### 1. Authorise YouTube uploads. Five minutes, once, never again.

**This is the biggest single lever on the business right now.** 456 videos are
built and 12 are public, because those 12 were posted by hand. 102 finished
narrated videos, with captions, titles, descriptions and tags, are sitting on a
disk where nobody can find them.

**Resolved overnight, 2026-09-18: authorising now publishes all 102, and every
one of them agrees with the page it links to.**

What this looked like yesterday is worth keeping, because it is why the item
changed. `video_zone.done_items()`, which writes the "What done looks like"
checklist into every video, was corrected on 15 September; every video on disk
had been rendered on 7 and 8 September; so 100 of 114 were saying something
different from their own zone page ("One wallet and one phone per adult" read
"One phone per adult", and one Entryway zone lost an item outright).
Authorising then would have published those permanently, because YouTube
cannot swap the file behind a URL.

All 99 affected videos were re-rendered on this machine overnight, free, in
260 minutes, 0 failures. `ops/check_video_standard.py` now reads **114 of 114
matching**, and `ops/youtube_upload.py` holds nothing back: `--check` lists
102 ready.

One more thing was fixed along the way, visible in the videos themselves: the
slide holds four items and 16 zones have more, so it now ends with "+ N more
on the zone page" rather than presenting four sixths of a standard as the
whole of it. One of those hidden items was "The cabinet strapped to a wall
stud", which is a safety line.

**Measured 2026-09-23 12:50 UTC by a direct database read.** Traffic is 68 visitors, 160 visits and 813 pageviews, 2.3 a day. It fell from 76 mostly because the 7 Sept automated session (431 pageviews) rolled out of the 30-day window, so this count is now very nearly all human. The last 7 days: **12 visitors**, against 10, 14 and 18 in the three weeks before, so the fall has stopped without reversing. The crawl rise I reported on 21 Sept turned out to be a two-day burst from the IndexNow submission, not a change (1, 17, 15, 2, 2 by day), so this is not a crawling problem and it is not a crawling success either:

| Source | Visitors, 30 days |
|---|---|
| direct or unknown | 70 |
| LinkedIn (both domains) | 10 |
| Bluesky (both domains) | 5 |
| Google | **2** |
| Bing | 1 |

This paragraph used to read "ZERO of them arrive from Google". That is now
wrong: it is one, not zero, and this repository has already corrected the same
retired claim twice in other files. Corrected here rather than left to be
found a third time.

The point survives the correction and sharpens. Search sends one person a
month. The only channel doing anything is a social feed somebody posts by
hand, and it sends engaged people: 6 of the 8 LinkedIn sessions viewed two or
more pages and several came back across several days. YouTube is a search
engine with 102 finished files already made for it and no way to reach it.

Uploading needs OAuth against the Google account that owns the channel. An API
key cannot perform writes, so there is genuinely no way around this one.

1. Go to https://console.cloud.google.com/ and create a project (any name).
2. APIs & Services, then Library, then enable **YouTube Data API v3**.
3. APIs & Services, then OAuth consent screen, choose External, fill the three
   required fields, and add yourself under Test users.
4. Credentials, then Create credentials, then **OAuth client ID**, type
   Desktop app.
5. Download the JSON and save it into the repo as
   `ops/youtube-client-secret.json`.

Then tell me. I run `python ops/youtube_upload.py`; a browser opens once for
you to approve, and after that it publishes unattended and resumes across the
daily quota.

**Already built and waiting:** `ops/youtube_upload.py` is written and dry-run
clean. It uploads the narrated 16:9 file, attaches the real SRT caption track
rather than relying on words burned into the picture, and uses the titles,
descriptions and tags already generated for all 114 zones.
`ops/youtube-published.json` has been seeded from the live channel, so the 12
already up are recorded and cannot be double-posted. That guard matters:
YouTube cannot replace a video file after upload, so a duplicate has to be
deleted by hand.

**Why it matters:** the videos are the only traffic asset we own outright. The
site's structured data is already strong, so the constraint is not the markup,
it is that almost nothing points at us.

**Separate, optional, and yours alone to do: the 12 already-public videos'
titles are stale.** Found 2026-09-12: they were posted by hand before this
title logic existed, so all 12 still read the internal working name ("How to
organize the landing zone | Entryway") rather than the name the linked page
actually uses ("How to organize the entryway drop zone", headed "The Landing
Spot"). This is not the OAuth-gated upload above; you already edit these
directly in YouTube Studio (no re-upload, the file itself is untouched). The
corrected text for each is in `build/video/youtube/<slug>.json` under
`title`/`description`; the 12 slugs are the keys of
`ops/youtube-published.json`. Low value against 2.5 visitors a day, so not
worth a special trip, but cheap to fix the next time you are in Studio anyway.

**Also separate, and not optional this time: 11 of those 12 videos show and
say the wrong "what done looks like" list, and re-uploading is the only fix.**
Found 2026-09-15 by a local session, confirmed and root-caused the same day by
an operator cycle. `ops/video_zone.py`'s `beats()`, which the narration and
caption pipeline both read from, used to cut the finished-standard sentence at
every comma and every "and" and keep only the first four fragments of three
words or more. On screen and in the narrator's voice this dropped real words
("one wallet and one phone per adult" became "One phone per adult") and
sometimes welded two sentences into one ("The salt. The kettle"). The
generator is now fixed (`video_zone.done_items()`, gated so it cannot silently
fork again), and the 102 not-yet-uploaded videos will render correctly the
first time. The 11 affected videos already on YouTube cannot be corrected any
other way, because YouTube will not replace a video file after upload: they
need `python ops/video_narrated.py` run again on your machine (real narration
and ffmpeg, not available to any cloud session) and the results uploaded as
new videos. YouTube does not let you swap the file of a video that is already
up, so the corrected video gets a new URL and starts at zero views; set the old
one to Unlisted (or delete it) once the new one is live, and update any link
that points at the old URL. (Corrected 2026-09-15: an earlier version of this
item described a replace-video option that keeps the URL; that option does not
exist.) The one zone that was already correct is Entry Console or Bench.

### 1a. Verify the site in Google Search Console. One paste, about three minutes.

**Google has never been told this site exists, and it is the only search engine
that will not accept a sitemap without an account.** Measured 2026-09-03: of 52
visitors ever, exactly one arrived from a search engine, and it was Bing. Zero
from Google. There is no impressions data to look at because there is no
property to look at it in.

I have submitted all 185 pages to Bing, Yandex, Seznam and Naver already, today,
through IndexNow: HTTP 200, 185 of 185 accepted, recorded in
`ops/indexnow-log.json`. That channel needs no account and it is done. Google
does not participate in it. This is the one that needs you, because it needs
you to be logged into your own Google account, and nothing I can build gets
around that.

**Your part, in full:**

1. Go to https://search.google.com/search-console
2. Add property, choose the **URL prefix** box on the right (not Domain), and
   enter `https://6s-success.com/`
3. Expand **HTML tag**. Google shows a line like
   `<meta name="google-site-verification" content="AbC123_xyz..." />`
4. Open `ops/site-verification.json` and paste **only the quoted content value**
   into `"google_meta"`. Not the whole tag; the file explains this too, and the
   generator will rescue a whole-tag paste rather than fail silently, but the
   value alone is cleaner.
5. Tell me. I run `python ops/build_seo.py`, which writes the tag into
   `site/index.html`, and I deploy.
6. Press **Verify** in Search Console, then **Sitemaps** and submit
   `sitemap.xml`.

If the meta tag is inconvenient, Google's HTML-file method works the same way:
paste the filename it gives you (`google<something>.html`) into `"google_html"`
instead, and the generator writes the file with the exact body Google expects,
so the filename and the contents cannot disagree. Either method alone is
enough.

**Already built and waiting:** `ops/site-verification.json` exists with the
instructions in it. `ops/build_seo.py` reads it and emits the tag on the home
page only, which is where every one of these platforms looks. An empty file
changes no byte of the site, verified by running the generator with it empty
and getting zero changed pages. A new preflight gate, `site-verification`,
fails the build if a token is set but the generator was never rerun, so a paste
cannot quietly do nothing.

**The same file takes three more tokens while you are in there,** and each one
is worth having: `bing` (Bing Webmaster Tools, which can also import the
property straight from Search Console once step 6 is done), `pinterest` (114
Pinterest save-and-share cards are already built and a claimed domain is what
attributes their saves back to us), and `yandex`. None of them are required for
the Google step; all four use the identical paste-and-tell-me flow.

**How we will know it worked:** Search Console starts reporting impressions and
queries within a few days of the sitemap submission. That is the first real
search-demand evidence this business has ever had, and `BACKLOG-2026-H2.md` item
1.5 and item 3.7 are both waiting on it: 3.7 is "write articles against measured
queries, never invented ones", and right now there are no measured queries.

### 1c. Label your own devices, so the next buy-click is not as unreadable as the last nine. About one minute per device.

**Added 2026-09-09, this operator, found reading `ops/experiments.py` cold and
running it.** EXP-001 (has a stranger ever clicked a buy button) is
permanently AMBIGUOUS for the nine clicks recorded before 2026-09-03
(`BACKLOG-2026-H2.md` 1.3, closed, correctly not reopened here) because
nothing distinguished your own clicks from a stranger's at the time. The fix
for every click *since* 2026-09-03 already shipped in `measure.js` and has
sat unused: it has never once been triggered. Checked directly against the
database on 2026-09-08 (see `site/assets/js/measure.js`'s own comment): not
one event in the whole history carries a `who` key. This was never put in
front of you as a numbered action, it only ever printed inside
`ops/experiments.py`'s own output and sat in `ops/experiments.json`, which is
the gap this item closes; `preflight.py` now carries
`gate_experiment_owner_actions_surfaced` so a future one like it cannot sit
silent the same way.

**New evidence, 2026-09-14 (`LEARNINGS.md` LRN-0010).** The two newest funnel
signals, the Corporate quote click on 12 September and the $29 Micro Zone
Manual buy-click on 14 September, both came from your home connection on an
iPhone (iOS 18.7, 430x932 screen). So did the burst of about 90 checkout pages
opened on 7 September. None were labelled, so each had to be traced by hand
through the server's access log. Your home IP also sent 85% of all analytics
beacons over the last fortnight. The iPhone and your Windows Chrome are the two
devices to label first.

**What:** on each device you personally browse the site from (phone, laptop,
tablet), open `https://6s-success.com/?6s-internal=1` once. That tells the
browser to stamp every event it sends afterward as yours, so a future
funnel read can finally tell your own clicks apart from a stranger's, the
same separation the historical nine could never have. `?6s-internal=0`
undoes it on a shared or borrowed device. Nothing is disabled and no data is
lost either way; the flag only ever adds a label.

**Why it is cheap and safe:** it changes nothing about what the site does or
serves, costs about a minute per device, and needs no account, password, or
spending decision, only your own hand on your own devices, which is why it
sits behind this list rather than something an agent could do for you.

### ~~0. Set six secrets in the Ledgerium repo.~~ DONE BY ME 2026-09-01.

Solo is live and purchasable on ledgerium.ai, verified against the public
sku-availability endpoint. I set the two price-ID secrets on
Klingdom/ledgerium myself and ran its deploy. The secret key and webhook
secret were already set and working. See LEDGERIUM-BILLING.md, including a
correction: Ledgerium bills through its own Stripe account, not ours.

### 0b. Superseded

Every Stripe-side piece is done and verified: both products, all four live
prices, the webhook, the portal and the statement descriptor. See
`LEDGERIUM-BILLING.md`. What remains is in Ledgerium's own repository, which I
have no access to.

Two are secret and must be piped, not pasted inline, or they land in shell
history:

```bash
gh secret set STRIPE_SECRET_KEY        # paste, Enter, Ctrl+D
gh secret set STRIPE_WEBHOOK_SECRET    # same
```

The webhook signing secret is on this machine in `.env.secrets` (gitignored) as
`LEDGERIUM_STRIPE_WEBHOOK_SECRET`. The live secret key is the one already in
`.env.secrets` as `STRIPE_SECRET_KEY`.

Four are public identifiers and can go inline:

```bash
gh secret set STRIPE_SOLO_MONTHLY_PRICE_ID    --body "price_1UAttC6OlZmKL8mFVUmsZUUh"
gh secret set STRIPE_SOLO_ANNUAL_PRICE_ID     --body "price_1UAttC6OlZmKL8mFF5Cu3VjD"
gh secret set STRIPE_STARTER_MONTHLY_PRICE_ID --body "price_1UAttB6OlZmKL8mFGejaGLBz"
gh secret set STRIPE_STARTER_ANNUAL_PRICE_ID  --body "price_1UAttB6OlZmKL8mFtPg9U1az"
```

Redeploy Ledgerium, then check `https://ledgerium.ai/api/billing/sku-availability`.
Both `starter` and `solo` should read `{"monthly":true,"annual":true}`.


### ~~1. Install one SSH key.~~ DONE BY ME 2026-09-01.

Installed through hPanel and verified: `python ops/deploy.py --check`
reports `access as root@187.77.25.50`. **Corrected 2026-09-11, operator:**
"no deploy needs you again" was not quite right. The public key is on the
server, but every operator sandbox since (this one included) reports "no
deploy key at /root/.ssh/6s_deploy," because the matching private half was
never placed in any of them, and nothing in `.github/workflows/` runs
`ops/deploy.py` either. So no automated session has actually run a real
deploy since this was installed, and whether the live site has been
redeployed even once since 2026-09-01 is unknown from here. If you deploy
yourself from a machine holding the private key, that still works and
nothing below applies to you; if not, item 1b right below is the live path.

### 1b. Superseded

**What:** paste the public key below into the VPS so I can deploy myself.

```
ssh root@187.77.25.50
mkdir -p ~/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGobKYWVBP1eg0rfeVfSqQn3yKL5jqzbNS0bq8CKLHp5 6s-success-vps-deploy-key' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

**Why it matters more than anything else on this list:** 339 commits landed in
five days and the live site still serves 10 products against 159 in the
repository. Work that does not deploy did not happen. For eight days I asked for
a Redeploy click, which was the wrong ask because it repeats forever. This one
does not.

**Verified, not assumed:** three SSH keys exist on the workstation and none of
them are installed on the server. `python ops/deploy.py --check` proves it and
prints these exact lines.

**After this:** `python ops/deploy.py` pulls the new image, recreates the
container, and refuses to report success unless the live catalogue actually
changed. No click, ever again.

### 1b. Or, right now: deploy the site yourself. One click, or one command.

**What:** either press Redeploy in Hostinger's Docker Manager, or, if you are
on the machine holding the private half of the deploy key, run
`python ops/deploy.py` directly.
**Why it matters:** whether the live site reflects the current repository is
unconfirmed either way (no operator sandbox has real egress to
6s-success.com or the private key needed to check or act). The old "10
products against 159" figure above is itself from before this file's last
catalogue widen and should not be trusted as today's live gap; only a real
check or a real deploy answers it.
**Blocked because:** no operator sandbox here holds the private key or has
network egress to the VPS or the live site, so this remains yours to run,
by whichever of the two paths you have available, not something an
autonomous session has been able to do since the key was installed.
**Ready:** a fresh, tested image is already on GHCR and both workflows are
green, current as of the last successful push.

**Possibly already done, unconfirmed:** a 2026-09-15 03:40 local session's own
`ops/NIGHTLY-LOG.md` entry (commit `636234cd`) says it redeployed and verified
production live at build `065e8b434a25c03c` (real browser probes, sample AVIF/
WebP files answering 200, CI green). But `ops/deploy.py` is supposed to write
`ops/deploy-verdict.json` "the moment it confirms a build live", and that
tracked file still shows the prior build `047a015202e83e30` at `08:44:21Z`, not
the newer one. No cloud sandbox since (including this one; `deploy_freshness.py
--json` returns `reachable: false`, `verdict: unknown`) can reach the live site
to settle it either way. If you already redeployed, nothing further is needed
except letting a session with real access re-run `python ops/deploy.py --check`
once so the tracked record catches up; if you have not, item 1b above still
stands. Left the tracked verdict file untouched rather than guess at it.

**Resolved 2026-09-15 (local session with production access): no redeploy needed.** Production's own `build-id.txt` was read directly and serves `065e8b434a25c03c`, the build `main` carries, so the log was right and the tracked record was stale. Cause: that session staged `ops/deploy-verdict.json` into each release commit before the release's own deploy ran, so every commit carried the previous deploy's verdict and the refreshed one was never committed. The current verdict is committed with this correction, and the session now commits the verdict after each deploy, with that release's log entry.

**Briefly reopened, then resolved, same 2026-09-15 afternoon.** Between the 11:17:08Z verdict above and this note, exactly one commit touched `site/`: `790a5d05` (a phone review by Phil himself, fixing the "One session: 30-45 min. most of it in Sort" grammar on 113 of 114 zone pages and labelling the empty zone-picture slot on room pages), moving the repository to build `587d80befe8bd586` with no newer verdict committed. This PM check-in flagged that gap; before it shipped, the same local session's own `11cfb6fd` landed, confirming production redeployed and current at `587d80befe8bd586` (checked 16:47:49Z). No action needed here now; recorded for continuity in case the tracked verdict ever falls behind again without a fresh commit to explain it.

**Reopened again, 2026-09-20 11:12, PM check-in, a real and growing gap: item 1b now stands, unconfirmed since.** A session with real production access last confirmed current at 2026-09-18T17:20:47Z, build `7c765b634045a89c` (`ops/deploy-verdict.json`, checked directly this cycle, not cited). `site/build-id.txt` now reads `5e905bdd45e222e9`: the repository has moved 233 commits past that confirmation, at least 14 touching `site/**` or `ops/build_*.py` (measured directly with `git log --since`), including the storage-before-Sort fix, the Home Quest symptom-entry and Keep-screen fixes, the Kitchen deck micro-quests and related-card links, and the sitemap-lastmod fix. None of this has reached a customer yet. `STATUS.md`'s own "Production Knowledge" line had gone stale claiming a match that stopped being true after 2026-09-18; corrected there this same cycle. As before, no operator sandbox holds the deploy key's private half or egress to the VPS or 6s-success.com, so this is yours: press Redeploy in Hostinger's Docker Manager, or run `python ops/deploy.py` on the machine holding the key. Everything up to the gate is ready; the fresh image is on GHCR and both workflows are green.

**Resolved, 2026-09-20, this PM check-in, verified against `ops/deploy-verdict.json` directly, not cited.** Phil redeployed twice today from a session with real production access: `470834de` (10:06:22 -0600, "Production moved `7c765b634045a89c` to `5e905bdd45e222e9`, two days of concurrent work that had built green and never shipped") and `7ae0e9b6` (11:51:59 -0600, the data-sku coverage fix, which also carried the deploy-verdict bump to `d9fc700d0700972f` at `2026-09-20T17:46:50Z`). The repository has since moved exactly one commit past that confirmed build (`1dd78484`, a command-deck regen only, no `site/**` or `ops/build_*.py` change), so the live gap is effectively zero, not 233 commits. `STATUS.md`'s BLOCKER-001 corrected to match, same cycle. No redeploy needed right now.

### 2. Run the 16 on-device app checks. About 20 minutes.

**What:** `cd mobile/quest-app && npx expo start --lan`, scan the QR with Expo
Go, work through `mobile/quest-app/ON-DEVICE-TEST.md`.
**Why it matters:** the app bundles, passes its tests and has verified
accessibility semantics, but every one of those was proven from source. Nothing
has been proven on a phone. A failure here is worth more than a pass.
**Ready:** the script names the exact expected words on screen for each check.

### ~~3. Narration decision.~~ WITHDRAWN, it was never yours to make.

I put this on your list saying the whole 114-video stream waited on it. It did
not. ffmpeg with libass and drawtext is installed and `ops/video_zone.py`
already drives it. Landing Zone is rendered at 1080x1920, 30 fps, 30.2 seconds,
and the rest are rendering now. Captions-only, no voice, no decision needed.

You were right to push back. Nothing goes on this list again until I have tried
it and hit a real wall.

### 3b. Withdrawn item, kept for the record

**What:** captions-only, a paid synthetic voice at roughly $10 to $30/mo, or you
record them.
**Why it matters:** this is the whole 114-video stream. Captions-only costs
nothing and unblocks all of it today, and is my recommendation.
**Ready:** see `MEDIA-OPERATIONS-PLAN.md` section 6.3.

### 4. Three affiliate applications are stalled on you. Do not finish them yet.

**Superseded 2026-09-17, this operator: everything below is the diagnosis,
not the instruction. Read this correction first.** `PLAN-AFFILIATE-MONETISATION.md`
(Phil, finalised 2026-09-07) settled the actual call ten days after this
section's own "what to do" line was written, and this section was never told:
"Do not apply to anything today. Not Amazon, not Impact, not CJ, not Rakuten,"
held until a written click trigger fires (T2: 60 real outbound retailer clicks
in a trailing 90 days, `ops/check_affiliate_trigger.py`, reading 0 of 60 as of
2026-09-09). `GOALS.md`'s O4 already carries this as "deliberately held, not
blocked"; this file did not, so it still read as if finishing the Office Depot
and Etsy confirmation clicks and a fresh Amazon application were yours to do
now. They are not: applying today spends a scarce, non-renewable first
impression against traffic (75 visitors/30 days) that the plan's own
arithmetic says guarantees rejection or a $7-a-month result either way. The
diagnosis below, which programme is actually stuck versus declined, stays
correct and worth keeping; the closing "what to do" line does not survive the
later decision.

**Corrected 2026-09-01 by reading the inbox instead of assuming.** You said you
were still waiting on the others. Three of the four are not waiting on anybody
except us. Applications were started on 29 August and each stopped at a
verification step that was never completed:

| Programme | Network | What arrived 29 Aug | State |
|---|---|---|---|
| Office Depot | CJ | "publisher sign-up, please confirm email" | never confirmed |
| Etsy | Rakuten | "Activate your Rakuten Advertising Login" | never activated |
| Walmart | Impact | "Verification" twice, "Application Update" | **DECLINED, see below** |
| Amazon | direct | three "Verify your new Amazon account" OTPs | OTPs long expired |
| Ace | Impact | "Application Received" | **DECLINED, see below** |

**IMPACT DECLINED US, and nobody had opened the email.** Corrected 2026-09-06.
That "Application Update" of 29 August is not a task waiting on you. It reads:
*"Your application to join Impact as a partner, 6S Success, was declined"*,
against Media Partner account 7700618. It sat unread in the support inbox for
eight days while this file asked you to go and click a verification link and
`ops/affiliate-accounts.json` recorded the application as pending our own
action. An earlier pass had logged the SUBJECT LINE and assumed what it meant.

**Five programmes route through Impact and all five are shut, not pending:**
Walmart, Ace, Home Depot, Lowe's and Target. They share the one partner account,
so there is no per-advertiser click that reopens them. Recorded as `declined` in
`ops/affiliate-accounts.json` with the date.

**What is actually left, honestly:** Office Depot through CJ and Etsy through
Rakuten still want a confirmation click from you, and Amazon needs a fresh
application because those OTPs expired. That is three, not five, and none of
them is Impact.

**Do not re-apply to Impact on a reflex.** A network that has just declined a
site with 52 visitors in thirty days will decline it again. The honest sequence
is traffic first, then re-apply with something to show. The retailer links on
the site work today without any programme: they are plain searches, they carry
no code, and they earn nothing, which is exactly what
`site/affiliate-disclosure.html` says.

**Why this matters:** 0 of 123 catalogued products are linkable, and the reason
is no longer "for want of a click each".

**Why I cannot do it:** completing an account signup or verification is account
creation, which I do not do on your behalf.

**What to do: nothing, on purpose, until the T2 trigger above fires.**
Superseded 2026-09-17: this used to say "open those four emails from 29
August and finish each one." `PLAN-AFFILIATE-MONETISATION.md` (2026-09-07)
overrode that for all three remaining programmes, not only Amazon. If you
want to apply anyway before the trigger fires, that is your call to make
knowingly, not a task this file is asking you to clear.

**Everything on our side of Amazon's bar is now built (2026-09-03).** The
catalogue and link tooling were already there. The disclosure Amazon and the
FTC ask for is now a page of its own at `/affiliate-disclosure.html`, linked
from the footer of all 188 site pages and in the sitemap.
`/how-we-make-money.html` answers the wider revenue question and points at it.

Checked against Amazon's own Program Policies and Operating Agreement, read
directly today rather than remembered:

| Amazon requirement, quoted from the policy | State |
|---|---|
| Site "must contain original content and be publicly available via the website address provided in the application" | met: 188 original pages, live |
| Not an "unsuitable Site" (adult, violent, deceptive, illegal, directed at under-13s) | met |
| Privacy disclosure of "the use of cookies, pixels, and other technologies ... and how you collect, use, store, and disclose data" | met: `/privacy.html`, which now also states there are no outbound tracking codes |
| Compliance with the FTC endorsement guides | met: disclosure page plus the block above the links on `/kit.html` |
| No Special Links "in connection with any printed material, ebook, mailing" | met and enforced: `ops/affiliate.py --check` reads all 311 delivered files and fails closed |
| "As an Amazon Associate I earn from qualifying purchases." displayed clearly | correctly absent, because we are not Associates. `ops/affiliate.py` adds it automatically the moment a publisher id is pasted in |
| You identify your Site(s) in the application | yours to do |

**One thing gates all of it, and it is item 1.** `/affiliate-disclosure.html`
returns **404 in production** as I write this, because the live site is still
the old build. A reviewer who opens the site today will not see the page. The
same deploy also fixes a live falsehood: production `/kit.html` currently opens
with "Some of the links below are affiliate links, which means 6S Success may
earn a commission", on a page where every product reads "No retailer link yet".
That was our own generator rendering a disclosure unconditionally; it is fixed
in the repository and says the truth now, but only after a deploy.

**What I could not verify, and am not guessing about:** CJ, Rakuten and Impact
do not publish their publisher prerequisites at a fetchable address. CJ's
publisher service agreement is not linked from cj.com, Impact's brand terms
are per-advertiser, and both are shown inside the signup flow. Rakuten's
Publisher Membership Agreement is public and was read: section 6.1 requires a
privacy policy reachable from the home page through a link containing the word
"Privacy", disclosing cookies and tracking. We meet that. Anything else those
three ask for, including tax and payment details, is behind a login only you
have.

### 4b. The original framing, which was wrong

**What:** apply to the seven programmes not yet applied to, starting with Amazon
Associates.
**Why it matters:** 0 of 123 catalogued products are linkable today because no
programme is approved. The catalogue, the link tooling and the disclosure
requirements are all built and waiting on publisher IDs.
**Blocked because:** applying means creating accounts in your name.
**Ready:** `python ops/affiliate.py --status` shows the current state. The
disclosure page Amazon requires was built on 2026-09-03 and is waiting on the
deploy in item 1.

### 5. Apple Developer and Google Play accounts. $99/yr and $25 once.

**Why it matters:** no store listing, no iOS or Android release, no in-app
purchase without them.
**Ready:** everything up to submission is done and committed.
`mobile/quest-app/STORE-LISTING.md` holds every listing field ready to paste,
the data-safety answers with their evidence, and the price decision (free, no
in-app purchase in the first release). The icon, splash, adaptive icon and Play
feature graphic are drawn and committed; `gate_store_art` fails the build if any
of them goes missing or lands at the wrong size.

**One more thing only you can do, and it is free:** while you run the 16
on-device checks, take six screenshots (the card, a finished zone, the finish
screen, the progress line, diagnostics, import). Both stores reject a listing
without them, and a web capture dressed up as a phone screenshot would be a
false claim to a review team, so this is the one asset I will not fabricate.

### 6. Accounts layer: yes or no, and the privacy stance.

**Why it matters:** this is the largest single unlock, worth roughly $11,250 of
the $21,500 revenue plan, because it enables household play and 6S Plus. It is
also the first customer data we would hold, so it changes our privacy and
security posture and is expensive to reverse.
**Ready:** recommendation is passwordless email link, minimal profile, household
as a shared code rather than a social graph.

### 7. Listmonk cannot send, AND the site was never wired to it.

**Second defect found 2026-09-04, which changes the size of this job.** The
nginx proxy host for 6s-success.com (`proxy_host/4.conf`) contains exactly one
`location`, which is `/`. There is no route to Listmonk from the site at all.
So `POST /subscribe` was never reaching it: the endpoint that earlier notes
recorded as returning HTTP 500 is not our route failing, it is Listmonk's own
port answering directly. Even with sending repaired, a form on this site would
have had nowhere to post.

**Why I have not built it yet, deliberately.** Fixing this properly means a
second Listmonk instance, because the SMTP settings and root URL are
instance-wide and the existing one is shared with Compassion Benchmark, plus a
new proxy route on production. That is real infrastructure with real risk, and
the thing it unlocks is email capture, which compounds only once people arrive.
At 1.7 visitors a day it would capture almost nobody. `DECK-SYSTEM.md` proposes
giving the Kitchen deck away for an address, and names this as its hard
prerequisite: that is correct, and it is also a bet on traffic existing first.

So the order is: publish the videos, get arrivals, then wire the list. If you
want it sooner, say so and I will build it, but I would rather not put a
capture form in front of two visitors a day and call it progress.

### 7a. The original defect: Listmonk's SMTP login belongs to the other business.

**Measured 2026-09-03, not inferred.** This item used to say "root URL and
from-address need setting", which was the 2026-08-23 diagnosis and is no longer
what is wrong. What is wrong now, checked against the running service:

```
POST https://6s-success.com/subscribe            -> HTTP 500
POST http://187.77.25.50:8081/subscription/form  -> HTTP 500
```

Both fail, so it is Listmonk itself and not our reverse proxy. `docker logs
listmonk-fhzc-listmonk-1` says exactly why:

```
initialized email (SMTP) messenger:
  info@compassionbenchmark.com@smtp.hostinger.com
error sending opt-in e-mail for subscriber 4: 553 5.7.1
  <support@6s-success.com>: Sender address rejected:
  not owned by user info@compassionbenchmark.com
```

The from-address **has** already been changed to ours. The SMTP credential it
authenticates with has not, and Hostinger will not let one mailbox send as
another. So every subscribe attempt 553s at the opt-in email and returns a 500
error page to the visitor.

Two consequences worth naming:

1. **The 6S list cannot take a single subscriber today.** Not "is empty", cannot.
2. **Compassion Benchmark's own opt-in mail is very likely broken too**, for the
   mirror-image reason, since the from-address is now ours and its credential is
   theirs. That is somebody else's business, and it is not ours to change.

**Why we did not fix it.** Listmonk's SMTP block and root URL are instance-wide,
not per-list, so one instance cannot serve two brands' sending identities. Fixing
it means editing another company's mail infrastructure. We hold the working
credential for `support@6s-success.com` in `.env.secrets`, so the change itself is
small, but the decision is yours.

**The single step:** decide whether 6S Success gets its own Listmonk instance, or
whether that one instance becomes ours and Compassion Benchmark moves. Then, in
Listmonk Settings, set the SMTP host/user/pass to the `SMTP_*` values already in
`.env.secrets`, and set the Root URL to `https://6s-success.com` (which also needs
a proxy hop for Listmonk's `/subscription/` confirmation paths, currently only
`/subscribe` is mapped in `site/nginx/default.conf`).

**What runs in the meantime:** the footer form on all 187 pages now states, before
it asks, that the list software is not connected and that the button opens the
visitor's own email app with a one-line message to `support@6s-success.com`, which
is a mailbox that really is read. It also fires a `list-signup` event, so for the
first time there will be a count of how many people wanted on. It is not a
substitute for a list.

### 8. Close two public ports. Two lines and a restart, about five minutes.

**What:** Umami on 32769 and Listmonk on 8081 are reachable from the open
internet.
**Why it matters:** analytics and mailing infrastructure should not be publicly
addressable. Low likelihood, real consequence.

**Re-measured 2026-09-17, so this is current rather than remembered.** Both are
still open and answering: `http://187.77.25.50:32769/login` serves Umami's
login page and `http://187.77.25.50:8081/` serves Listmonk, both HTTP 200 from
outside. `docker ps` shows them published on `0.0.0.0`, and the host runs **no
firewall at all** (`ufw status` reports inactive), so nothing else is standing
in front of them.

**Why it stayed open: closing it would have broken this site, until today.**
`site/nginx/default.conf` reached both services through the host's own public
address, so binding them privately would have taken the analytics beacon and
the signup form down with them. That dependency is now gone: the site's
upstreams point at the Docker bridge (`172.17.0.1`) instead, proved from
inside the running container first (`172.17.0.1:32769/api/heartbeat` returns
`{"ok":true}`) and then end to end in a test container against the real
services. Closing the ports can no longer break this site.

**The precondition is met, confirmed on the live site.** Production moved to
build `8f2400c02ff063f2` at 2026-09-18 01:47 and the rewired path was proved
end to end, not inferred: `stats/script.js` serves 4,595 bytes, `/subscribe`
answers 200, and a labelled probe event posted to the live beacon
(`operator-probe-bridge`) is in the analytics database at 01:49:16. The site no
longer touches those public ports at all, so closing them cannot affect it.

**Your part.** In each of these two compose files on the VPS, change the
published address from `0.0.0.0` to the bridge, then recreate:

```
ssh root@187.77.25.50
sed -i 's/"32769:3000"/"172.17.0.1:32769:3000"/' /docker/umami-analytics-vi0p/docker-compose.yml
sed -i 's/"8081:9000"/"172.17.0.1:8081:9000"/'   /docker/listmonk-fhzc/docker-compose.yml
cd /docker/umami-analytics-vi0p && docker compose up -d
cd /docker/listmonk-fhzc     && docker compose up -d
```

**Check the quoting in each file before running the sed** (the port may be
written unquoted), and afterwards confirm two things: `curl -m 5
http://187.77.25.50:32769/` fails from your laptop, and 6s-success.com still
records a visit. These are Hostinger-managed stacks shared with other sites on
the host, which is why I have not run it for you: if another site's tracker
points at the public address, it would stop reporting, and that is somebody
else's analytics to decide about.

### 9. HTTP/2 and HSTS. (www to apex: done by me 2026-09-17, no longer needs you.)

**www to apex is fixed and did not need the proxy.** The site's own nginx config
(`site/nginx/default.conf`, in Git, shipped by the normal image build and
`ops/deploy.py`) now answers any `www.` host with a 301 to
`https://6s-success.com` plus the original path and query. Guarded by
`ops/tests/test_nginx_www_redirect.py`. The measurement below is kept as the
reason. HTTP/2 and HSTS still live in Nginx Proxy Manager and remain open, low
priority.

**Why it matters:** performance and search. Small, and needs the reverse proxy
config that lives on the VPS.

**Measured 2026-09-03, so this is no longer theoretical.** `https://www.6s-success.com/`
answers **200 with the whole site**, not a redirect: `www` is a CNAME onto the
same address and the proxy serves both names. Every one of the 185 pages
therefore exists at two hostnames. Indexing is protected, because every
canonical tag and every internal link names the apex, but two things still
break:

- A Search Console **URL prefix** property for `https://6s-success.com/` does
  not cover `https://www.6s-success.com/`. Anyone who links to the www form,
  and anyone who types it, is invisible in the data we are about to start
  collecting. A **Domain** property would cover both, but that needs a DNS TXT
  record at the registrar rather than a paste into a file.
- Any inbound link that lands on www spends its value on a hostname we do not
  otherwise use.

The fix is one `server` block in the proxy config returning 301 to the apex.
It is a production reverse-proxy change, which is `devops-sre` and
`vps-docker-manager` territory, not something an SEO pass should do on its own.
Also measured the same day: `http://` correctly 301s to `https://`, the site is
served over **HTTP/1.1 only**, gzip is on, and no `X-Robots-Tag` header is being
sent, so nothing at the header level is suppressing indexing.

### ~~10. Fix the hourly operator routine's own STEP 0.~~ DONE 2026-09-08, see R4 above.

> Left in place rather than deleted so the reasoning below stays readable,
> including the 2026-09-02 correction about force-pushed history. Nothing
> here needs you any more. The one open question it raises is recorded at
> the end of this section.

**What:** the "6S Success hourly operator" Routine (`trig_011oe2y7KR3AiPxUTd6b9P6c`)
was created outside an agent session (`created_via: http_api`), so no agent
session, including this one, is allowed to call `update_trigger` on it: the
tool refuses with "Agents can only update routines they created." Open the
Routine in the Routines UI (or ask a Claude session you are chatting with
directly, not a fired instance of this routine, to run `update_trigger` on
your behalf) and replace its STEP 0 text with the version already drafted,
tested and confirmed safe in GitHub issue #27.
**Why it matters:** most cycles' checkouts arrive in a state that makes a
clean fast-forward look like "refusing to merge unrelated histories." Every
cycle re-diagnoses and fixes this live before doing any real work, confirmed
again this cycle (comfortably past a dozen occurrences now, `ops/NIGHTLY-LOG.md`
and issue #27 between them record). It costs no revenue by itself, only
operator time each cycle, but it is the cheapest fix on this whole list.
**Correction, 2026-09-02:** issue #27's root cause (a shallow clone) does not
match this cycle's checkout: `git rev-parse --is-shallow-repository` read
`false` and no `.git/shallow` file existed, yet `git merge-base main
origin/main` still returned nothing. The real cause looks like origin/main
itself being force-pushed with rewritten history between cycles, not clone
depth. Commented on issue #27 with this correction. It does not change what
you need to do: the replacement STEP 0 text already drafted there handles
both cases (it unshallows if shallow, and falls back to a clean-tree
`reset --hard origin/main` when `merge-base` finds no common ancestor either
way), so the fix below is still the right one to apply.
**Ready:** exact replacement text is in issue #27's body, already verified
this cycle to produce a clean, no-data-lost recovery. Attempted `update_trigger`
directly this cycle too, confirmed still refused for the same `http_api`
creation reason; this remains a step only you (or a session you are directly
chatting with) can take.

**The one open question, recorded 2026-09-09 rather than left implicit.** The
2026-09-02 correction above says the real cause may be `origin/main` being
force-pushed with rewritten history between cycles, not clone depth, and that
the STEP 0 drafted in issue #27 handled that case with a fallback
`reset --hard origin/main` when `merge-base` finds no common ancestor.

The STEP 0 I actually installed does NOT include that fallback. It unshallows,
attaches, fast-forwards, and if the merge still refuses it says: run `git status`
and read it, never reset, force or rebase to make the error go away.

That was deliberate and it is a trade. Telling an unattended agent to
`reset --hard` is how work gets silently discarded, and this repository has
already lost 377 files once to a confident recovery command. The cost is that if
the no-common-ancestor case ever returns, a cycle will stop and report rather
than recover by itself, which is the stall this whole item was about.

I have not seen that case since. Every run I have checked attaches cleanly, and
the shallow symptom is gone. If it comes back, the answer is not to add
`reset --hard` to the routine; it is to find out what is force-pushing `main`,
because that is a repository-integrity problem in its own right and CLAUDE.md
section 41 rules it out.

---

### 11. Post the 114 zone-reset videos somewhere a stranger can find them.

**What:** `build/video/zones/` holds 114 short, vertical, captions-only clips,
one per micro zone, 79 MB total, rendered and ffprobe-verified by you
(`a44335a`). They are built for posting to social video platforms (YouTube
Shorts, TikTok, Instagram Reels), not for embedding on the site, and nothing
has posted any of them anywhere yet, confirmed this cycle: no site page links
to `video/zones`, and I have no credential for any social video account.
**Why it matters:** this is a real, finished traffic asset sitting unused
while `ROADMAP-2026-2029.md` names search and distribution as the whole
constraint. Format matches the channel on purpose (muted-first, captions
burned in) so no further editing should be needed before posting.
**Ready:** the files themselves, at `build/video/zones/*.mp4`, named
`<room-slug>--<zone-slug>.mp4`. No further operator step is buildable here
without an account to post through.

### ~~12. Regenerate the book cover.~~ DONE BY ME 2026-09-03, no machine needed.

See R2 above. This no longer needs your Windows machine or any action from
you; the operator sandbox can render and commit the cover itself now.

### 13. Where are the product masters backed up? About two minutes.

**What:** `RISKS.md` (RISK-0011) records that the roughly 1.74 to 1.78 GB of
book plate PNGs, deck art, photographs and font masters behind every product
live in exactly one place: your Windows machine's Desktop, outside this
repository and outside version control (`.gitignore` carves the size out on
purpose; `ops/dashboard.py` reads product state from that Desktop path
directly). Tell me whether a second copy of that folder already exists
somewhere (an external drive, a cloud backup you already run, a NAS), and if
one does not, make one.

**Why it matters:** this is the one open `CRITICAL` risk in the register with
no mitigation in flight anywhere in this repository, confirmed this cycle by
checking `OWNER-ACTIONS.md`, `BACKLOG-2026-H2.md` and `GOALS.md` directly for
any prior mention of it, none found. If that one machine's disk fails, the
source images and PDFs behind every card, chapter plate and photograph are
gone, and nothing in this repository recreates them; only the derived,
already-published output would survive.

**Ready:** no code change closes this, only your answer. If nothing backs
the folder up yet, the cheapest real options are an external drive, a cloud
backup service you may already have (OneDrive, Google Drive, Backblaze), or
Git LFS if you want it version-controlled (`DEPLOY.md` and
`content/README.md` already name this option and the same size figure).
Once a second copy exists, restoring one file from it and confirming it
opens is what `RISK-0011`'s own closing condition asks for, which is also a
two-minute check, not a project.

### 14. Create the Amazon KDP account and publish the book. About 30 minutes, once.

**What:** the business sells in exactly one place and that place had 52
visitors in thirty days, none of them from Google. A finished 271,000 word
book (`build/listings/verify_epub.py`'s own live count against the committed
EPUB, corrected 2026-09-10 from a stale 262,000-word figure) has been sitting
on a disk since 27 August. Amazon has the audience we do not.

Every field is written and checked. Your part is the account and the paste.

1. Go to `https://kdp.amazon.com` and sign in with an Amazon account, or
   create one. Use a business address, not a personal one, if you would rather
   the copyright page and the seller record agree.
2. Complete the **tax interview** and add **bank details**. These are yours and
   cannot be delegated; nothing else in this item is blocked on them, but
   publishing is.
3. **Create eBook.** Fill the Details tab from `MARKETPLACE-LISTINGS.md`
   section 2.1. Title, subtitle, author, publisher, description, keywords and
   categories are all there as literal text to copy.
4. For the description, click **Source** in the editor and paste the single
   HTML block in section 2.2. Do not paste it into the visual editor; it will
   escape the tags. It is 2472 characters against a 4000 limit.
5. **Content tab.** Upload `build/6S-Success-Home-Edition.epub` and
   `build/listings/kdp/cover-kdp.jpg`. Not `build/cover.png`: KDP accepts JPEG
   and TIFF only, and that file also carries a URL that is better off the
   cover. Section 2.7 explains why.
6. **Read the converter's report and open the online previewer.** The EPUB has
   passed every structural check a zip and XML reader can perform, and, as of
   2026-09-15, the real epubcheck 5.1.0 validator too (0 fatals/errors/warnings
   against EPUB 3.3 rules, `MARKETPLACE-LISTINGS.md` section 1). Amazon's own
   converter is still the thing that ultimately decides, since it runs a
   proprietary pipeline neither tool can substitute for.
7. **Pricing tab.** `70%` royalty, `$9.99`, all territories, no DRM, **not**
   enrolled in KDP Select. Section 2.6 has the arithmetic and section 2.8 has
   the reason Select is a no.
8. After the book goes live, at `authorcentral.amazon.com`, claim the book and
   paste the author bio from section 2.3. Author Central is a separate free
   signup on the same login, and the bio field does not exist anywhere in the
   KDP form.

**Then tell me the ASIN.** Nothing in this repository has one, which means
nothing can link to the book, no schema can reference it, and no report can
track it.

**Ready and checked:** `build/listings/check_kdp.py` passes with zero failures.
The cover is exactly the 1600 x 2560 KDP calls ideal, the EPUB's manifest,
spine, links and images all resolve, and every rule quoted in
`MARKETPLACE-LISTINGS.md` was read off kdp.amazon.com on 2026-09-03 with the
help topic named. Two things there have changed since the previous draft was
written: the 70% royalty band now runs to $12.99, and `<h2>` in a description
is unsupported, which the old draft used three times.

### 15. Create the Etsy shop and publish four listings. About 40 minutes, once.

**What:** 155 finished print packs, and Etsy's organisation-printable category
has buyers searching for exactly this today. Four listings are written, and
their files are built and measured.

**Corrected 2026-09-09, this operator: it was five, now four.** A fifth,
L3-entryway (30 cards, the six passes for the five Entryway zones), was
written, priced, rendered and readied, then withdrawn: it sold the exact
content `ops/generated_products.py` already excludes from the site's own
paid catalogue because the free Entryway deck covers it, the same trust
problem `MARKETPLACE-LISTINGS.md` section 3.1 already names for the
Standards Pack, just never connected to L3 until now. Withdrawn before
publishing, not after: its files are removed from
`build/listings/etsy/L3-entryway/`, and `build/listings/check_etsy.py` now
fails any listing that repeats this shape. Full account in
`MARKETPLACE-LISTINGS.md` section 3.1.

1. Go to `https://www.etsy.com/sell` and open a shop. Country **United
   States**, currency **USD**, language **English**.
2. Shop name: `SixSSuccess`, or `SixSHome`, `SixSSuccessHome`, `NovaSixS` if it
   is taken. Availability could not be checked without an account. Etsy allows
   one free rename later, so take whichever is free rather than stalling.
3. Bank details and identity verification. Yours, not delegable.
4. **While you are signed in, open `etsy.com/legal/fees` and send me the four
   numbers:** listing fee, transaction percentage, payment processing
   percentage and fixed amount. Etsy returns HTTP 403 to every automated
   request, so no fee figure in this repository is verified, and the four
   prices were set by a rule that needs those numbers to be checked.
5. Create the four listings from `MARKETPLACE-LISTINGS.md` section 3.4. Each
   has its title, its 13 tags as one comma-separated line, and its description
   as a single block to paste.
6. For each, set it to **Digital**, upload the files from
   `build/listings/etsy/<slug>/files/` and the images from
   `build/listings/etsy/<slug>/listing-images/`. Section 3.2 lists exactly
   which files go with which listing. Set renewal to **manual**, so a listing
   that is not working stops costing money.
7. Shop policies: digital downloads, not returnable once downloaded. Say it
   plainly rather than burying it.

**Then send me one photograph.** Print one pack, cut it, and photograph the
cards on a table. The listing images at the moment are rendered PDF pages,
which is honest and weaker than a real photograph, and it is the single
highest-value improvement available to these listings. No mockup was invented,
because inventing one is a claim about an object that does not exist.

**Ready and checked:** `build/listings/check_etsy.py` passes with zero
failures. Every file is US Letter, contains the exact page and card counts its
title claims, and is far under any upload cap. A print defect was found and
fixed on the way through: every pack was rendering with a near-empty page
between every sheet of cards, so the Whole House PDF was 152 pages of which 76
were litter. It is 76 pages now. **Corrected 2026-09-06, this operator:** the
fix already landed upstream, in the same commit this note was written in.
Checked directly rather than trusted: `ops/build_catalog.py`'s sheet CSS
(0.3in page margin, 3.4in card height) and `ops/build_printpack.py`'s own copy
of the same values, the generator that actually produces the file Stripe
fulfilment delivers to a paying customer, both carry the fix, and the built
Etsy PDF re-renders at 76 pages, not 152. Nothing further needed here.

### 16. Create Pinterest and Instagram business accounts, then post the 114 zone cards already built. About 20 minutes, once.

**Added 2026-09-08, this operator, found while checking whether GOALS.md's own
"not blocked" claim about these two channels was still true.** It was true for
building the asset and has stayed false for posting it: `ops/build_social_pins.py`
finished all 114 zones for both surfaces on 2026-09-02 (`STATUS.md`,
`BACKLOG-2026-H2.md` 3.11), `ops/dashboard.py`'s own `social_pin_line()` has
said "ready, not posted anywhere yet" every cycle since, and no numbered item
on this list has ever turned that into a single step for you the way item 1
did for YouTube and item 11 did for the zone videos. That gap, not a missing
asset, is what this item closes.

**What:** `build/social/pinterest/*.png` (1000x1500, 2:3) and
`build/social/instagram/*.png` (1080x1350, 4:5), 114 zones each, a save-and-share
checklist card composed for each surface, not an auto-crop of the video
frames. Nothing has been posted to either platform: no operator credential
exists for either, confirmed this cycle by checking for one.

1. Go to `https://business.pinterest.com` and create a free Business account
   (or convert an existing personal one). Claim `6s-success.com` as your
   website under Settings, Claim, which is also what the `pinterest` token in
   `ops/site-verification.json` (see item 1a) attributes back to once you paste
   it, so doing both together is efficient.
2. Go to `https://www.instagram.com` and create a Business account, or switch
   an existing one, under the same handle family as the other properties
   (`SixSSuccess` or `SixSHome`, matching the Etsy name in item 15 keeps the
   brand consistent across the properties you are creating this cycle).
3. Post the 114 cards. Open `build/social/captions/<room-slug>--<zone-slug>.json`
   next to the matching image and paste straight in: it already carries the
   Pinterest title, description, board name and four hashtags, and the
   Instagram caption and twelve hashtags, one file per zone. Pinterest
   supports scheduling several boards' worth in one sitting through its own
   Business Hub; Instagram feed posts one at a time or through Meta Business
   Suite if you want to schedule them.
4. **Then tell me.** There is no API credential to hand back for either
   platform from a personal login flow like this (unlike YouTube's OAuth,
   which item 1 already covers), so this item stays a manual posting job for
   you rather than something I can finish once you create the account.

**Why it matters:** `GOALS.md` decision rule 1 is "distribution beats
production," and this is the plainest case of it on the list: 228 finished
images sitting on a disk, zero of them in front of a stranger, while the
whole business is gated on exactly one thing, arrivals.

**Ready:** the images themselves, named `<room-slug>--<zone-slug>.png` in
each directory. **Added 2026-09-09, this operator:** the caption/board/tag
text this item used to say still needed writing once the accounts existed.
`ops/build_social_captions.py` writes it now, ahead of the accounts, so that
step is no longer part of the manual job: `build/social/captions/*.json`,
114 files plus a `boards.json` grouping into one board per room, every fact
pulled from `content.json` (the same corpus the images and the zone pages
themselves are built from), never typed in fresh. Verified before shipping:
all 114 zone-page links resolve to a real file, no Pinterest title or
description and no Instagram caption exceeds that platform's limit, no
truncation artefact, no em or en dash. Gated in `preflight.py`
(`gate_generator_ownership`) so a future content edit cannot leave this
corpus silently stale. No further operator step is buildable here without
the two accounts above.

**Updated 2026-09-15:** the cards were rebuilt to lead with each zone's approved
picture (106 of 114 zones; the other 8 have no approved picture and stay text
only). Same file names and the same steps above. The captions were regenerated
too: their checklist now quotes each standard whole, and 15 Pinterest
descriptions that had lost their zone link to a length cut end in it again.

---

### 17. Decide the capped local demand test for In-Home Days. A budget, a stop date, and about five minutes beyond that.

**Added 2026-09-11, PM check-in, found reading `BACKLOG-2026-H2.md` section
3B rather than trusted from an earlier cycle's own list of what remains.**
`3B.1` has sat as "Phil, this is a spending decision" since the strategy
review that wrote it, 2026-08-24, eighteen days, and was never once added
here, the one file `CLAUDE.md` 0.5 designates for exactly this. Nobody
building the backlog is at fault for missing it: it never left that table.

**Why it outranks the traffic work already on this list:** `GOALS.md`'s own
math says the constraint is arrivals, and organic search needs roughly
246,000 visitors a month to reach $20,000. Seventeen In-Home Days a month, a
real service this site already sells with a working Stripe link
(`consulting.html`), needs 3,900. That is not a bet on a new product; it is
a demand signal for one that already exists, and it has been unstarted for
over two weeks for want of a decision rather than for want of traffic.

**What:** approve a capped, time-boxed local demand test for the consulting
service (In-Home Days), a few hundred dollars, hard stop at 90 days,
reported pass or fail either way. This is a real spending decision, so it
stays yours; `CLAUDE.md` puts material spending in the RED band and nothing
here approves it for you.

**Already built, waiting only on this decision or your own next step:**

1. A Google Business Profile package for the service area is fully drafted
   at `build/gbp-listing-package.txt`: business name, category, a
   480-character description drawn only from what `consulting.html` already
   says, the seven-town service area copied verbatim, honest "by
   appointment" hours, and an explicit warning against seeding reviews
   before a single paid day has happened. It needs a phone number (a free
   Google Voice number is enough) and five minutes in your own Google
   account to go live. This step costs nothing and does not need the budget
   decision below; only the paid test that might follow it does.
2. Referral-partner outreach messages for senior move managers, real estate
   agents and professional organizers are fully drafted at
   `build/referral-partner-outreach.txt`, with a response-tracking log at
   `build/referral-partner-outreach-log.csv`. None offer a referral fee on
   purpose (real estate licensing rules, and it changes the relationship
   with the other two categories in a way that is your call, not an
   assumption). Sending them under your name is the same category of
   externally-facing action already held for the Google Business Profile
   and for issue-3.8-style third-party accounts: I can draft, you make
   contact. This step also does not need the budget decision.
3. The budget and stop date themselves (3B.1) are the one piece that is a
   real financial commitment. Once you set them, I run the test to its stop
   date and record pass or fail against `ROADMAP-2026-2029.md`'s G2 gate,
   which is currently holding the whole services-first funnel reframe open
   pending exactly this result.

**Ready:** items 1 and 2 above are single steps once you act on them. Item 3
needs your number and your date, in writing, before anything spends.

---

### 18. Create Facebook and X accounts, then read the daily draft email. About 15 minutes, once.

**Added 2026-09-12, this operator, found reading `ops/corpus_index.py` cold,
per step 5d.** The same book corpus `ops/linkedin_drafts.py` has been reading
for LinkedIn since before this item existed also holds 155 finished Facebook
posts and 723 finished X posts, real writing, checked directly by running
`python ops/corpus_posts.py --stats`, none of it ever served anywhere: zero
served for either kind. `GOALS.md` names LinkedIn as "the only channel we
actually post to," and nothing had connected these two ready channels to a
draft mailer the way item 16 already did for Pinterest and Instagram images.
That gap, not a missing asset, is what this item closes, and it is squarely
O1 (arrivals, the constraint): distribution beats production, and the
production side of this one was finished before this business existed.

**Found and fixed on the way through:** `corpus_posts.py`'s `split_numbered()`
only stripped the trailing "(NNN chars)" sizing note in one of the four
shapes the corpus actually uses ("(NNN chars)", "(~NNN chars)",
"(approx NNN chars)", "(approx. NNN chars)"). 261 of 741 real X posts still
carried that note as the last line of the body, which would have read as
obviously unedited if posted as written, the exact bar the module's own
`clean()` docstring sets and fails on its own terms. Fixed the pattern to
match all four; `ops/tests/test_corpus_posts.py` extended with the three
previously-uncaught shapes, fail-then-pass proved directly against the real
corpus (261 to 0).

**What:** `ops/social_drafts.py` (new), a thin sibling of
`ops/linkedin_drafts.py`: reads the same corpus through
`ops/corpus_posts.py`, filters X's picks to 280 characters or fewer before
selecting (Facebook has no limit that binds here), and writes one combined
email a day rather than two, `build_all()`, so this adds one new message to
your inbox, not two. `.github/workflows/social-drafts.yml` (new) sends it
daily once `SMTP_HOST`/`OWNER_EMAIL` (already configured for
`linkedin-drafts.yml`) are present, which they already are. No API call to
either platform exists or is planned: both platforms restrict script posting
without developer review, and a post that was plainly not chosen by a person
reads worse than none.

1. Create a Facebook Page (not a personal profile) at
   `https://www.facebook.com/pages/create`, under the same handle family as
   the other properties (`SixSSuccess` or `SixSHome`, matching item 15's
   Etsy name and item 16's Pinterest/Instagram choice keeps this consistent).
2. Create an X account at `https://x.com/i/flow/signup` under the same
   handle family.
3. Nothing else to do: the workflow is already live and already sending you
   one email a day with both platforms' next posts, ready to paste in.
   Post whichever ones fit, whenever you have the accounts to post them to;
   nothing expires and nothing needs to be caught up on.

**Why it matters:** the same reasoning as item 16, on two more channels: real
writing sitting on a disk, zero of it in front of a stranger, while the
whole business is gated on exactly one thing, arrivals.

**Ready:** `ops/social_drafts.py --preview` shows today's combined draft
without touching rotation state; `ops/tests/test_social_drafts.py` (6 cases)
and the extended `ops/tests/test_corpus_posts.py` (18 cases) both pass.
Verified this cycle against the live corpus, not a fixture: every X draft
`build("x")` can hand back is 280 characters or fewer, and none carries a
leftover sizing annotation. No further operator step is buildable here
without the two accounts above.

---

### 19. Print the free Kitchen deck on your own printer. About five minutes, once.

**Added 2026-09-12, this PM check-in, found reconciling
`PLAN-MICROZONES-DECKS-APP.md`'s K4 row against what actually shipped.** The
free Kitchen deck (`site/kitchen-deck.html`, 72 cards, no SKU, shipped
2026-09-08) has a `@media print` sheet sized against `ops/card_spec.py`'s
own 7pt type floor, and every automated check available in this environment
passes: contrast, layout, the sheet fits the page, no side-scroll. What none
of those checks can do, because no sandbox this work runs in has a printer,
is confirm the one claim that actually matters to somebody printing it at
home: that it comes out legible on a real domestic inkjet or laser printer
in plain greyscale, not just correct on screen. This has sat genuinely
unverified since the deck shipped four days ago without ever being written
down here, so it warned into the void the same way item 1d's Stripe field
did before it was recorded.

**What to do:** open `https://6s-success.com/kitchen-deck.html` (or the
repository copy), use the page's own "Print the 72 fronts" button, print a
page or two on whatever printer you have, and check by eye that the
smallest text is still readable and nothing is cut off at the trim edges.

**If it prints fine:** reply here or note it anywhere this gets read, and a
future cycle will close K4 in `PLAN-MICROZONES-DECKS-APP.md` with that as
the evidence.

**If it does not:** say what broke (too small, cut off, too dark, too
light) and it gets fixed in `ops/build_kitchen_deck_page.py`'s print CSS
before anything else is built on top of it.

---

### 20. Add one link to each of the 12 published video descriptions. About ten minutes, once.

**Decide item 1 first, added 2026-09-18: this may be ten minutes you do not
need to spend.** Those same 12 videos are among the 100 whose on-screen
checklist contradicts their own zone page (see item 1). Anything uploaded from
now on carries this "KEEP IT THIS WAY" block automatically, so if you choose to
replace the 12 with the corrected re-renders, pasting into the old descriptions
is work that gets thrown away. If you choose to leave the 12 as they are, this
item stands exactly as written below.

Worth knowing before choosing: replacing means new URLs, because YouTube cannot
swap the file behind an existing one. On a channel this size that costs little,
and the corrected versions are being rendered now at no cost.

**Added 2026-09-13, this operator, closing `PLAN-MICROZONES-DECKS-APP.md`'s
S5 row.** That row has said since 2026-09-07 that each pilot zone's YouTube
description should link its own page's Sustain habit, "so the drift signal
is useless if it is only on a page." Nobody had actually written the copy
until now. No operator sandbox holds the OAuth needed to edit an
already-published video's own metadata (see item 1: uploading new videos
needs a one-time authorisation, and even with it the YouTube Data API can
write a description, but nothing in this repository has ever been given
write access to your channel to use it), so this is yours to paste,
same as item 1's title-only edits.

**What changed:** `ops/build_youtube_metadata.py` now adds a short
"KEEP IT THIS WAY" block to every zone's description, right after "THE
STANDARD YOU LEAVE BEHIND" and before the existing "Full written steps"
link, pointing at that same page's own `#sustain` anchor (already live on
all 114 zone pages). Verified against the real corpus: all 114 generated
descriptions carry it, gated by the new `gate_youtube_sustain_anchor` in
`ops/preflight.py`. This only affects the 12 already-public videos'
descriptions; anything uploaded later already carries the block.

**What to do, once per video:** open the video in YouTube Studio, Details,
and paste this block into the description, in the same place (right after
the "THE STANDARD YOU LEAVE BEHIND" paragraph, right before "Full written
steps for this zone, free:"):

```
KEEP IT THIS WAY
The Sustain habit that keeps this zone from drifting back, on the same page:
<the link in this row>
```

| Video | Link to paste |
|---|---|
| [How to organize the entryway drop zone](https://youtu.be/HJ2Uy0kSXkM) | https://6s-success.com/zones/entryway-the-landing-spot.html#sustain |
| [How to organize the entryway shoes and boots](https://youtu.be/A3PGbxrp8dc) | https://6s-success.com/zones/entryway-the-shoes-and-boots.html#sustain |
| [How to organize the entryway bench or console](https://youtu.be/QfTOo7xcZrQ) | https://6s-success.com/zones/entryway-the-bench-or-console.html#sustain |
| [How to organize the entryway coats and outerwear](https://youtu.be/U33P_nYFV3U) | https://6s-success.com/zones/entryway-the-coats-and-outerwear.html#sustain |
| [How to organize the entryway door, mat, and immediate floor](https://youtu.be/zaI1YzYG5nE) | https://6s-success.com/zones/entryway-the-door-mat-and-immediate-floor.html#sustain |
| [How to organize the kitchen stove area](https://youtu.be/6_N2_mSo3Eo) | https://6s-success.com/zones/kitchen-the-cooking-zone.html#sustain |
| [How to organize the kitchen upper cabinets](https://youtu.be/DNEuz9ke6ac) | https://6s-success.com/zones/kitchen-the-upper-cabinets.html#sustain |
| [How to organize the kitchen lower cabinets and cookware](https://youtu.be/I8Zxf-EXQ5c) | https://6s-success.com/zones/kitchen-the-lower-cabinets-and-cookware.html#sustain |
| [How to organize the kitchen prep counter](https://youtu.be/EGcVpRA27zA) | https://6s-success.com/zones/kitchen-the-primary-prep-counter.html#sustain |
| [How to organize the kitchen refrigerator and freezer](https://youtu.be/IHkJ0h9yNww) | https://6s-success.com/zones/kitchen-the-refrigerator-and-freezer.html#sustain |
| [How to organize the kitchen sink area](https://youtu.be/jIBxPOsN9sQ) | https://6s-success.com/zones/kitchen-the-sink-and-dishwashing-zone.html#sustain |
| [How to organize the kitchen utensil and utility drawers](https://youtu.be/x-G5N-YCheI) | https://6s-success.com/zones/kitchen-the-utensil-and-utility-drawers.html#sustain |

**Why bother for ten minutes of work:** these 12 videos are the only content
on the only channel with a real, growing audience. A viewer who finishes the
video already knows what to do once; the anchor gives the ones who come back
weeks later, when the zone has slipped again, a direct path to the exact
paragraph that tells them how to recover it, instead of the top of a
2,000-word page.

**Why it matters:** low effort, and it is the last open row on the Kitchen
deck's own acceptance checklist (K2, the other open row, is a design
question about tooling reuse, not a customer-facing gap). Nobody should
claim "prints legibly" as done on inspection alone when the actual test
costs five minutes and one sheet of paper.
