# Owner actions

Everything that genuinely needs Phil, with the work already done up to the gate
so each one is a single step rather than a project.

Rule from `CLAUDE.md` section 0.5: a blocked task is not a blocked project.
Nothing on this list stops other work.

**Last measured:** 2026-09-03, item 12 resolved

---

## Resolved today

| # | Action | Outcome |
|---|---|---|
| ~~R1~~ | ~~Six dead payment links~~ | **Fixed by me, no longer needs you.** All six reactivated and verified in a real browser. The site can take money again. Root cause fixed in `ops/stripe_catalog.py`. |
| ~~R2~~ | ~~Book cover missing the author byline~~ | **Fixed by me, no longer needs your machine.** `ops/build_cover.py` now falls back to the Liberation fonts already installed in the operator sandbox (metric-compatible with Georgia/Times/Arial, OFL-licensed) whenever the named Windows fonts are absent, so it renders correctly here too. Regenerated and committed `build/cover.png`/`.jpg` with your byline. Verified by opening the actual rendered PNG, not trusting the exit code. |

---

## Open, ranked by what they unblock

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
| Walmart | Impact | "Verification" twice, "Application Update" | never actioned |
| Amazon | direct | three "Verify your new Amazon account" OTPs | OTPs long expired |
| Ace | Impact | "Application Received" | genuinely waiting on them |

**Why this matters:** an unconfirmed publisher account cannot be approved for
any advertiser, so all of these have been sitting at zero for three days for
want of a click each. 0 of 123 catalogued products are linkable as a result.

**Why I cannot do it:** completing an account signup or verification is account
creation, which I do not do on your behalf. Everything else is ready: the
catalogue, the link tooling, and the disclosure page Amazon requires, which I
shipped today at /how-we-make-money.html.

**What to do:** open those four emails from 29 August and finish each one. The
Amazon OTPs have expired, so that one needs a fresh application, which is now
more likely to pass because the disclosure page exists.

### 4b. The original framing, which was wrong

**What:** apply to the seven programmes not yet applied to, starting with Amazon
Associates.
**Why it matters:** 0 of 123 catalogued products are linkable today because no
programme is approved. The catalogue, the link tooling and the disclosure
requirements are all built and waiting on publisher IDs.
**Blocked because:** applying means creating accounts in your name.
**Ready:** `python ops/affiliate.py --status` shows the current state. I am
building the affiliate disclosure page this cycle, which Amazon requires before
it will approve.

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

### 7. Listmonk root URL and from-address.

**Why it matters:** the email list is at 0. Nothing can be sent until these are
set.

### 8. Close two public ports.

**What:** Umami on 32769 and Listmonk on 8081 are reachable from the open
internet.
**Why it matters:** analytics and mailing infrastructure should not be publicly
addressable. Low likelihood, real consequence.

### 9. HTTP/2, HSTS, and www to apex redirect.

**Why it matters:** performance and search. Small, and needs the reverse proxy
config that lives on the VPS.

### 10. Fix the hourly operator routine's own STEP 0. Two minutes, no code.

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
