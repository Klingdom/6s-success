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

### 1. Deploy the site. One click.

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

### 3. Narration decision for the video series. A choice, not a task.

**What:** captions-only, a paid synthetic voice at roughly $10 to $30/mo, or you
record them.
**Why it matters:** this is the whole 114-video stream. Captions-only costs
nothing and unblocks all of it today, and is my recommendation.
**Ready:** see `MEDIA-OPERATIONS-PLAN.md` section 6.3.

### 4. Affiliate programme approvals. The revenue path that needs no deploy.

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
