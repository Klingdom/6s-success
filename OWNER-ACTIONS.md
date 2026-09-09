# Owner actions

Everything that genuinely needs Phil, with the work already done up to the gate
so each one is a single step rather than a project.

Rule from `CLAUDE.md` section 0.5: a blocked task is not a blocked project.
Nothing on this list stops other work.

**Last measured:** 2026-09-09, item 1c added (label your own devices so future buy-clicks are attributable). Earlier same day: item 16's caption/board/tag text built and linked. Earlier: 2026-09-08, item 16 added (Pinterest/Instagram accounts); 2026-09-04, item 12 resolved, items 1a, 14 and 15 added by Phil directly, R3 added

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

I cannot set it. `POST /v1/account` is refused on your own account, so this is a
Dashboard field and it needs you.

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

**Thirty customer-facing surfaces currently have no picture, and they are all
this one gate.** Counted 2026-09-09: 12 blank cards in the free print-and-play
deck, 7 zone pages, 11 room pages. That is the whole of it, in one number, and
it is the clearest argument for the two minutes this action takes.

The room eleven are not a separate problem: the nine room pages that DO have art
are exactly the nine whose book chapters, 31 to 39, are illustrated, and the
eleven without are chapters 40 to 50, which have none. `gate_pages_missing_art`
names the zone and room pages every run; `gate_deck_download_has_art` names the
cards.

**Seven zone pages ship with no picture at all**, measured the same day and
by the same mechanism. `build_zone_pages.py` refuses to show a hero the art
review marked "no", which is correct, so those pages carry no image whatsoever:
family room board game zone, home office file storage, home office printer
station, mudroom family hook zone, nursery crib and sleep zone, primary bathroom
under-sink cabinet, workshop material rack. Each is a 2,600 word instruction
page with nothing to look at, on the surface this business is trying to be found
on. They are the "Zone hero gaps, measured, 7 images" line in the table below,
which is 28 cents at Flash prices. `gate_zone_pages_have_art` now names them
every run.

Regenerating those twelve is the cheapest line in the table below.
`gate_deck_download_has_art` now names them on every run so the count cannot
drift back into the background.

**What it costs, from Google's published per-image prices fetched today:**

| Job | Images | Flash | Flash batch | Pro |
|---|---|---|---|---|
| Entryway deck card art | 89 | $3.47 | $1.74 | $11.93 |
| Zone hero gaps, measured | 7 | $0.28 | $0.14 | $0.95 |
| A second full deck | 89 | $3.47 | $1.74 | $11.93 |
| Web app and room imagery | 40 | $1.56 | $0.78 | $5.36 |
| **Everything** | **225** | **$8.78** | **$4.40** | **$30.17** |

Under thirty-one dollars for the entire illustration backlog at the best
model, and under five at the cheapest. Both figures fell on 2026-09-04 when
the zone hero row was first measured rather than assumed: 107 of those 114
images already exist and are live, so the backlog is 225 images, not 332.

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

### 1. Authorise YouTube uploads. Five minutes, once, never again.

**This is the biggest single lever on the business right now.** 456 videos are
built and 12 are public, because those 12 were posted by hand. 102 finished
narrated videos, with captions, titles, descriptions and tags, are sitting on a
disk where nobody can find them, while traffic runs at 1.6 visitors a day and
ZERO of them arrive from Google.

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
reports `access as root@187.77.25.50`. No deploy needs you again.

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

### 1b. Or, until then: deploy the site. One click.

**What:** Hostinger Docker Manager, press Redeploy.
**Why it matters:** the live site is an old build serving 10 products against
159 in the repository, so 149 things we sell are not on the site at all. It also
still advertises the book at $18 when the current price is $9.99.
**Blocked because:** there is no SSH key or VPS credential available to me.
**Ready:** a fresh, tested image is already on GHCR and both workflows are green.

### 2. Run the 15 on-device app checks. About 20 minutes.

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

### 4. Four affiliate applications are stalled on YOU, not on them.

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

**What to do:** open those four emails from 29 August and finish each one. The
Amazon OTPs have expired, so that one needs a fresh application.

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
**Ready:** everything up to submission is in `APP-DEVELOPMENT-PLAN.md` phase 1.

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

### 8. Close two public ports.

**What:** Umami on 32769 and Listmonk on 8081 are reachable from the open
internet.
**Why it matters:** analytics and mailing infrastructure should not be publicly
addressable. Low likelihood, real consequence.

### 9. HTTP/2, HSTS, and www to apex redirect.

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
visitors in thirty days, none of them from Google. A finished 262,000 word
book has been sitting on a disk since 27 August. Amazon has the audience we do
not.

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
6. **Read the converter's report and open the online previewer.** This is the
   one gate no script here could satisfy: there is no JRE on the operator
   machine, so epubcheck has not been run. The EPUB has passed every structural
   check a zip and XML reader can perform, and Amazon's own converter is the
   thing that decides.
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

### 15. Create the Etsy shop and publish five listings. About 45 minutes, once.

**What:** 155 finished print packs, and Etsy's organisation-printable category
has buyers searching for exactly this today. Five listings are written, and
their files are built and measured.

1. Go to `https://www.etsy.com/sell` and open a shop. Country **United
   States**, currency **USD**, language **English**.
2. Shop name: `SixSSuccess`, or `SixSHome`, `SixSSuccessHome`, `NovaSixS` if it
   is taken. Availability could not be checked without an account. Etsy allows
   one free rename later, so take whichever is free rather than stalling.
3. Bank details and identity verification. Yours, not delegable.
4. **While you are signed in, open `etsy.com/legal/fees` and send me the four
   numbers:** listing fee, transaction percentage, payment processing
   percentage and fixed amount. Etsy returns HTTP 403 to every automated
   request, so no fee figure in this repository is verified, and the five
   prices were set by a rule that needs those numbers to be checked.
5. Create the five listings from `MARKETPLACE-LISTINGS.md` section 3.4. Each
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
