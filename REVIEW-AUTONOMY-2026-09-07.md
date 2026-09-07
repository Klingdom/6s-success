# Can this run 24 hours a day? A measured answer

7 September 2026. Everything below was checked today, not recalled.

---

## The short answer

**Partly, and the gap is in the last step.** Five jobs run on a schedule and do
real work with nobody watching, including the one that matters most: a customer
who buys at 3am is delivered within thirty minutes. But **nothing can deploy the
site.** The container image builds and publishes automatically; nothing pulls
it. Production only moves when I run the deploy from Phil's machine.

That is not theoretical. When I checked this evening the repository was at build
`645871fb` and production was serving `5047354c`, four commits' worth of work,
including the Sustain rewrite for all 114 zones, the app's scroll fix and a
corrected privacy claim, finished and invisible. I deployed it by hand, which is
the point: nobody else could have.

---

## What genuinely runs without me

| Job | Cadence | What it does | Last run |
|---|---|---|---|
| `fulfil-orders` | every 30 min | delivers a purchase and records it in Stripe | success |
| `hourly-brief` | hourly | measures and reports state | success |
| `status-email` | 6x daily | sends Phil the state of the business | success |
| `roadmap-report` | 4x daily | sends the roadmap read | success |
| `linkedin-drafts` | daily 08:19 | three posts, written, into Phil's inbox | success |
| `checks` + `publish-image` | every push | gates, then builds and publishes the image | success |

All six were green today. The fulfilment one is the load-bearing one: it is the
only thing standing between a 3am sale and a customer waiting until morning, and
it has now been proved end to end against a real order and again against the
current build.

**What those jobs are allowed to touch:** IMAP, SMTP, the owner address and the
Stripe secret key. So unattended, the system can read mail, send mail, take and
fulfil an order, run every gate, and publish an image.

---

## What it cannot do without me, and why

| Capability | Blocked by | Consequence |
|---|---|---|
| **Deploy to production** | no SSH key in CI | work sits finished and unshipped, silently |
| Read the analytics database | same SSH key | no unattended measurement of traffic or events |
| Generate images | `GEMINI_API_KEY` is local only | the art queue cannot run overnight |
| Verify anything in a real browser | no browser in CI | visual and interaction checks are local-only |

The first row is the important one. The other three degrade quality; that one
means **the business does not receive the work.**

---

## Why this has been invisible

`publish-image` succeeds, so every signal a person looks at says the release
went out. The image is published. It is simply never pulled. Until this week
nothing compared what production serves against what the repository holds in a
way that could tell them apart, which is why:

- the product-count check reported a successful deploy of a build production
  never received, twice;
- the stylesheet-fingerprint check that replaced it could not see a release
  that touched no CSS, and exactly such a release then happened;
- `site/build-id.txt`, a hash of every deployed file, now answers the question
  properly and is what caught tonight's four-commit gap.

An independent QA pass this week recorded the same thing from the other side:
at 11:13 production was behind the tree by the repository's own authority, and
nothing surfaced it.

---

## What would close the gap

**One change: give CI a deploy key and a deploy workflow.** The image already
publishes; the missing step is `docker compose pull && up -d` on the VPS after a
successful publish, followed by the build-id verification that already exists.

I have not done it, deliberately. It hands a GitHub Actions runner the ability
to change production on Phil's server, and that is an access decision with his
name on it, not a technical one with mine. It is reversible: a deploy key can be
revoked from the server in one line, and it can be scoped to that one command.

**What it would change:** work merged at any hour reaches customers at that
hour. Cloud sessions could then finish a job rather than leaving it staged.

**What it would risk:** a bad commit reaching production unattended. The
mitigation already exists and is stronger than it was a week ago: `checks` must
pass before `publish-image` runs, and the deploy verifies the live build id
against the repository afterwards and reports UNKNOWN rather than success when
it cannot read production.

---

## The honest limit nobody can engineer away

This interactive session ends when the terminal closes. Cloud routines and
scheduled workflows continue; an open conversation does not. So "continuously,
24 hours a day" means the scheduled system, not this session, and the scheduled
system is only as capable as the credentials it holds.

Today it holds enough to take money and deliver a product. It does not hold
enough to ship the work.

---

## Recommendation, in order

1. **Add the deploy key to CI and a deploy job after publish.** Phil's call, one
   decision, and it converts "the work is finished" into "the customer has it".
2. Add the analytics read to CI, so measurement does not depend on a laptop.
3. Leave image generation local. It is a paid API and a local key is the safer
   place for it until the queue is routine.
4. Keep the build-id check as the only accepted proof of a deploy. Every earlier
   proxy for it has now been wrong at least once.
