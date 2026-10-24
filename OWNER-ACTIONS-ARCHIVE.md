# OWNER-ACTIONS.md archive

> Historical entries moved here by ops/rotate_owner_actions.py. Nothing here was edited on the way over; CLAUDE.md section 54 says the record must survive.

---

**Corrected 2026-09-25 00:1x, PM check-in: the "3 commits" figure below was already stale, and citing a superseded build_id besides.** Before re-deriving from the same `28ed2709194afab5`/`d5b0d5c8` citation the note below used, checked `ops/deploy-verdict.json` directly. It now records a newer, unread confirmation: `verdict: "current"`, build `6a10df205a3d058c`, `checked_at: 2026-09-24T23:35:51Z`, resolving (`git log -S`) to commit `b8eca135` ("Micro zones: Laundry Room personalised"). A session with real access redeployed again after the `d5b0d5c8` confirmation and closed the gap in full at that time. Reopened since by exactly one further `site/**` commit, Phil's own `ca49aa25` ("Micro zones: Garage personalised"): `git log b8eca135..HEAD -- site/ Dockerfile` reads 1 commit, 44 files, 547 insertions, 323 deletions, not the 4 a recount against the older, superseded build would have shown. No new action needed beyond item 0 below, same structural gap, just correctly sized against the current verdict; `STATUS.md`'s `BLOCKER-001` carries the same correction.

**Widened 2026-09-25 01:4x, PM check-in: the "1 commit" figure above had already gone stale, caught by `gate_status_deploy_gap_count_current` on this cycle's own `preflight.py` run.** Same build_id (`6a10df205a3d058c`), same resolved commit (`b8eca135`), but a fresh `git log b8eca135..HEAD -- site/ Dockerfile` now reads 2 commits, not 1: Phil's own D-026 checkpoint (`fa78db8c`, which shipped `measure.js`'s new zone-block-seen instrumentation to every zone page) landed the same day as `ca49aa25` and was not counted. Real gap is now (2 commits, `fa78db8c`, `ca49aa25`; 197 files, 808 insertions, 520 deletions). No new action needed beyond item 0 below, same structural gap, just correctly sized; `STATUS.md`'s `BLOCKER-001` carries the same correction.

**Widened 2026-09-25, scheduled operator cycle: the count above is stale by one commit, and that commit is the P0 footer-restoration fix.** Same build_id (`6a10df205a3d058c`, same resolved commit `b8eca135`); `ops/deploy-verdict.json`'s `checked_at` is unchanged at `2026-09-24T23:35:51Z`, so nothing has redeployed since. `git log b8eca135..HEAD -- site/ Dockerfile` now reads 4 commits, not 2: `6ba42a27` and `2d8077fd` both landed since and were not counted. `2d8077fd` restores the footer (privacy, terms, accessibility, safety, newsletter links) to all 134 room/zone pages after it was found silently missing sitewide; production is still serving the footerless version until a redeploy happens. Real gap now (4 commits, `ca49aa25`, `fa78db8c`, `6ba42a27`, `2d8077fd`; 198 files, 1089 insertions, 684 deletions). Same structural gap, no new action beyond item 0 below; `STATUS.md`'s `BLOCKER-001` carries the same correction.

**RESOLVED 2026-09-25 05:4x, PM check-in: a session with real access redeployed again, closing the gap named just above, footer fix included.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `aa7c7e7e578e9a18`, `checked_at: 2026-09-25T04:50:46Z`, resolving to commit `890c43a3` (an independent earlier fix for the identical footer defect `2d8077fd` above also fixed; both build to the same `aa7c7e7e578e9a18`, confirmed byte-identical by reading `site/build-id.txt` at each commit). `git log 890c43a3..HEAD -- site/ Dockerfile` is empty: production matches HEAD exactly, right now. No action needed on the redeploy itself. Same standing limit as every occurrence above: item 0 below is what stops this from reopening on the next `site/**` push with no session to follow it.

**Reopened, then narrowed, 2026-09-25 14:2x, PM check-in: the note above went stale (site work kept landing, no session followed it), then a later redeploy closed part of it again.** `ops/deploy-verdict.json` now records `verdict: "current"`, build `ea2e48125aa63502`, `checked_at: 2026-09-25T07:30:48Z`, resolving to commit `c6cc1a6a` (B9's Laundry Room deck). Real gap now (`deploy_gap_material_commits`): 5 commits, all still item 0's wait: three B9 room decks (Home Office, Primary Bathroom, Garage, the last three of five), the Kitchen-photo og:image correctness fix, and one build-id restamp. Full account in `STATUS.md`'s `BLOCKER-001`. Same standing limit: item 0 below.

**Reopened again 2026-09-24, later, scheduled operator cycle: a session with real access redeployed once more, then the same recurring pattern closed the gap and reopened it within one cycle.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `28ed2709194afab5`, `checked_at: 2026-09-24T21:10:12Z`, matching commit `d5b0d5c8`. One further `site/**` commit, `869d4e93` ("Home Office personalised"), landed immediately after and moved `site/build-id.txt` to `6e4992daa2791557`; `git diff --quiet d5b0d5c8 HEAD -- site/ Dockerfile` is dirty again, but this time by exactly one commit, not the 20-commit/29-file gap the 21:1x note below describes. No action needed on the redeploy itself, same as every prior occurrence; the pattern is now recurring predictably (three redeploy/reopen cycles in one day), which is itself the argument for item 0 below over waiting for the next local session to notice.

**Corrected 2026-09-24, later, scheduled operator cycle: the "exactly one commit" figure just above had already gone stale by the time this cycle read it.** Two further `site/**` commits landed after that note was written and neither was mentioned: `29a84fa2` ("Correct 13 wrong cause IDs across two rooms") and `b8eca135` ("Micro zones: Laundry Room personalised"). `git log d5b0d5c8..HEAD -- site/ Dockerfile` now reads 3 commits (`869d4e93`, `29a84fa2`, `b8eca135`; 55 files), not 1. No new action needed beyond item 0 below, same structural gap, just correctly sized; `STATUS.md`'s `BLOCKER-001` carries the same correction, and a new `gate_status_deploy_gap_count_current` in `preflight.py` now catches this specific shape (a correct build_id citation next to a stale commit-count) going forward.

**RESOLVED 2026-09-24 19:2x, PM check-in: the redeploy this item was waiting on already happened, from a local session holding the key, not from you.** `ops/deploy-verdict.json`, read directly, now records `verdict: "current"`, build `4ec571da81db3b34`, `checked_at: 2026-09-24T18:47:16Z`, committed in `44ef380a`. `site/build-id.txt` at HEAD (`ef417f10`) reads the identical build id, and `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is clean, so production matches HEAD exactly right now, zero commits undeployed. No action needed on the redeploy itself. This closes again the moment a future `site/**` commit lands without a following redeploy; treat this as "clear right now," not "solved permanently," until `VPS_DEPLOY_KEY` (item 0 below) makes it automatic.

One correction to the earlier note, because the distinction is the whole point of this file: **Phil did not redeploy.** An autonomous session running on his machine did, three times today, using the `~/.ssh/6s_deploy` key installed back on 2026-09-01. Recording it as an owner action would quietly put a recurring chore back on this list that nobody needs to do. Deploying is not yours and has not been since that key went in; what remains yours is the three items in "start here" below.

**Reopened 2026-09-24 21:1x, PM check-in, exactly as the note above predicted: a new `site/**` push landed (the Micro Zones "Primary Bathroom personalised" content) with no local session following it to redeploy.** `git diff --quiet 44ef380a HEAD -- site/ Dockerfile` is dirty again, 20 commits/29 files. The new `deploy.yml` fired automatically for the first time this cycle, `workflow_run` off `publish-image.yml` run 399, and its own job log confirms the Deploy step itself ran `skipped`, exactly the no-op it is built to do without `VPS_DEPLOY_KEY` (item 0 below). Item 0 is now the only thing standing between every future content push and a customer actually seeing it, not a one-time convenience.

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



## Archived 2026-10-24 by ops/rotate_owner_actions_closed_items.py

The following numbered items from "Open, ranked by what they unblock" were already fully closed (DONE / WITHDRAWN / Superseded by their own header), duplicated an entry already in "Resolved today", or were explicitly labelled a wrong original framing. None is a standing owner action. Moved verbatim.

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

---

### ~~1a. Verify the site in Google Search Console.~~ DONE BY PHIL, as a Domain property (DNS TXT). Recorded 2026-10-14.

**Phil confirmed 2026-10-14 that the Domain property is set up, and it checks out:** `nslookup -type=TXT 6s-success.com 8.8.8.8` returns `google-site-verification=_Y_Bb...`. The token is now recorded in `ops/site-verification.json` (`google_dns_txt`) and `gate_site_verification_declared` looks the record up on every run instead of warning "verified to no search engine", which had been false for an unknown length of time. **Two small asks remain:** (1) confirm `sitemap.xml` is submitted under Sitemaps in that property; (2) send the Pages report (indexed vs not, with reasons, especially `/zones/`) and Performance (impressions, clicks, top queries). No operator here can read Search Console, so until those numbers arrive, `GOALS.md`'s indexed-or-not question stays unanswered. The meta-tag instructions below are kept for the record and are no longer needed.

### (superseded) 1a. Verify the site in Google Search Console. One paste, about three minutes.

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

---

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

---

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

---

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

---

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

---

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

---

### ~~12. Regenerate the book cover.~~ DONE BY ME 2026-09-03, no machine needed.

See R2 above. This no longer needs your Windows machine or any action from
you; the operator sandbox can render and commit the cover itself now.
