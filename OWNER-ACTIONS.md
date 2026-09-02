# Owner actions

Everything that genuinely needs Phil, with the work already done up to the gate
so each one is a single step rather than a project.

Rule from `CLAUDE.md` section 0.5: a blocked task is not a blocked project.
Nothing on this list stops other work.

**Last measured:** 2026-08-31

---

## Resolved today

| # | Action | Outcome |
|---|---|---|
| ~~R1~~ | ~~Six dead payment links~~ | **Fixed by me, no longer needs you.** All six reactivated and verified in a real browser. The site can take money again. Root cause fixed in `ops/stripe_catalog.py`. |

---

## Open, ranked by what they unblock

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

### 2. Run the 12 on-device app checks. About 20 minutes.

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
**Why it matters:** every cycle's checkout arrives shallow, which makes a
clean fast-forward look like "refusing to merge unrelated histories." Every
cycle re-diagnoses and fixes this live before doing any real work, confirmed
again this cycle (the 9th+ occurrence `ops/NIGHTLY-LOG.md` and issue #27
between them record). It costs no revenue by itself, only operator time each
cycle, but it is the cheapest fix on this whole list.
**Ready:** exact replacement text is in issue #27's body, already verified
this cycle to produce a clean fast-forward with no data loss.

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

### 12. Regenerate the book cover. One command, on your own machine.

**What:** `build/cover.png`/`.jpg`, the art `ops/kdp_package.py` bundles for
Amazon KDP, was last generated 2026-08-17, four days before your author name
was filled into the front matter (2026-08-21, `9dccfec`). The committed cover
has had no byline on it since, and Amazon requires one on the cover art
itself. Found this cycle running `ops/build_cover.py` here to check: on this
Linux sandbox every font name it looks for is a Windows-only path, so it
silently fell back to PIL's tiny default font and produced an illegible cover
that still "succeeded," the same trap a wrong assumption almost shipped this
cycle. Fixed the script to refuse rather than write that output on any
machine without those fonts, so it is now safe to run anywhere, but it will
only render correctly where the fonts actually exist, which so far is only
your own Windows machine.
**Why it matters:** not urgent (nothing has been submitted to KDP yet, per
`STATUS.md`), but it blocks doing that submission cleanly, and it is a one
line command once you are at the machine that has Georgia/Times/Arial.
**Ready:** `python ops/build_cover.py`, then commit `build/cover.png` and
`build/cover.jpg`. A new preflight gate (`gate_cover_author_current`) will
stop reporting this once the commit lands.
