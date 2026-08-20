# Stripe for 6S Success

Owner: Phil. Written 2026-08-18. Stripe products in scope: **Payments** and **Invoicing**.

## The corrected business description

The description first drafted for Stripe broke the method's own canon in two
ways. It matters because this text ends up on statements, receipts, and the
public Stripe business profile, where it will be quoted back at us.

> **Wrong:** Sort, Set in Order, Shine, Standardize, Sustain, and Safety.

Two defects. "Set in Order" is the term this project explicitly rejected in
favour of **Straighten**, and there is a gate in the build that fails on it.
And Safety was listed sixth. **Safety is the fourth S**, which is the single
most distinctive claim the method makes.

Use this instead:

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

## What can actually be charged for

This is the part that decides the integration, and it is smaller than the
catalogue suggests. The site lists 41 items. Almost none are deliverable.

| Offer | Deliverable today | Stripe product | Needs |
|---|---|---|---|
| Virtual Home Consult, 250 | **Yes** | **Invoicing** | Your calendar |
| In-Home Reset Day, 1200 | **Yes** | **Invoicing** | Your calendar |
| Corporate Lean 6S, quoted | **Yes** | **Invoicing** | Your calendar |
| Book, ebook | Blocked | Payment Link | Front matter, issue #3 |
| Micro Zone Manual | Blocked | Payment Link | Front matter, issue #3 |
| Reset kits, 4 SKUs | **No** | Payments later | A supplier and stock |
| Courses, 4 SKUs | **No** | Payments later | A platform and a schedule |
| Tools and supplies, 24 SKUs | **No** | Payments later | A supplier and stock |

**The first dollar is a consulting invoice, and it does not need the website.**
Stripe Invoicing is sent from the dashboard or the API. It works today, before
deployment, before checkout, before anything else on the board is answered.

Everything else waits on either the front matter or a supply chain.

## Architecture, and the one hard constraint

The website is a **static bundle** served by nginx from a container image.
Everything under `site/` is handed verbatim to anyone who asks. That rules out
one whole class of integration and shapes the rest.

| Approach | Server needed | Secret on the site | Verdict |
|---|---|---|---|
| **Invoicing** | No | No | **Start here.** Nothing on the site changes at all. |
| **Payment Links** | No | No | For digital goods once #3 clears. A link is just an `href`. |
| **Buy Button** | No | Publishable key only, which is safe to expose | Fine, slightly richer than a link. |
| **Checkout Sessions** | **Yes** | Secret key, server side only | The destination once there are real carts. |
| Anything using a secret key in page JavaScript | | | **Never.** It would be published to the world. |

The staged plan follows from that:

**Stage 1, now.** Invoicing for consulting. No code, no deployment, no keys in
the repository. Revenue is possible this week.

**Stage 2, after issue #3.** Payment Links for the ebook and the manual. One
link per product, pasted into `site/book.html` and `site/shop.html`. Still no
server, still no secret anywhere near the site.

**Stage 3, when more than a few SKUs are real.** A small service beside nginx in
the compose file that creates Checkout Sessions from the existing cart, holding
the secret key in the environment. The cart already tracks line items and
quantities, so it is ready for this.

## Credential rules

- The **publishable key** (`pk_live_...`) is designed to be public and may sit
  in the site.
- The **secret key** (`sk_live_...`) goes in `.env.secrets`, which is gitignored,
  or in the VPS environment. It never enters the repository or `site/`.
- Prefer a **restricted key** over the account secret key, scoped to only what
  the integration uses.
- The image publish workflow already fails the build if it finds `sk_live_` or
  `sk_test_` anywhere under `site/`.

## What must be true before the first charge

Taking money changes the site's legal posture, and three things are currently
wrong for that:

1. **`site/terms.html` says ordering is not live** and that nothing forms a
   contract. That is true today and becomes false the moment a Payment Link
   works. It must be rewritten before, not after.
2. **There is no refund policy.** Stripe expects clear terms, and card networks
   treat their absence as a chargeback risk.
3. **Eight SKUs are priced with nothing behind them.** Four reset kits and four
   courses have no supplier, no stock, no platform and no schedule. Selling one
   today would be taking money for something that does not exist. They should be
   built, relabelled as in development, or removed before checkout opens.

## Next actions

**Phil:** authenticate the Stripe MCP server by running `/mcp` in this session,
then confirm the corrected description above and paste it into the Stripe
business profile.

**Claude, once authenticated:** run the implementation planner against the
corrected description, create the three consulting products and prices, and
prepare the invoice templates. Then rewrite terms and the refund policy so they
are true before anything can be bought.

---

## Live status, 2026-08-19

The live account is onboarded and can take money: `charges_enabled` and
`payouts_enabled` are both true on `acct_1U5rDs6OlZmKL8mF`.

**Created, because they can be delivered:**

| Offer | Price | Link |
|---|---|---|
| Virtual Home Consult | 250 | live payment link, on the consulting page |
| In-Home Reset Day | 1,200 | live payment link, on the consulting page |

Each link collects a phone number and which room the customer wants worked on,
so a booking arrives ready to schedule rather than starting an email thread.

**Not created**, and this is deliberate: reset kits, courses, tools, the book
and the manual. A payment link in front of something that cannot ship is taking
money for nothing. Corporate Lean 6S is quoted per engagement, so it is an
invoice rather than a fixed price.

### MCP access, and why it is read only

The Stripe MCP server is connected to the live account with **Read** permission
only, scoped to 6S Success. Ledgerium was not included.

Read rather than Write is a deliberate choice, not caution for its own sake.
The live secret key already grants full access, so Write would add no capability
whatsoever. What it would add is a second path that writes to a live account
without passing through the guards in `ops/stripe_setup.py` and
`ops/stripe_links.py`: the idempotency checks, the refusal to create live
objects without an explicit override, and the list of what must never get a buy
path. Every write stays in reviewable code with a commit behind it.

### What terms now say

Taking money changed what the site had to promise. `site/terms.html` previously
said ordering was not live and no price was a binding offer, and it promised
that the terms would be updated before checkout went live. That promise was
kept. The page now separates what can be bought from what cannot, and carries a
refund policy: full refund outside seven days, half inside seven, one free
reschedule inside 48 hours, a full refund whenever we cancel, and a refund on
request within seven days if the session was not useful.

---

## The monetised surface, 20 August

Every offer in the catalogue now has either a route to money or a stated reason
it does not.

| Route | Offers | Status |
|---|---|---|
| Stripe Payment Link | 2 | Virtual Home Consult 250, In-Home Reset Day 1,200. Live. |
| Stripe Invoice | 1 | Corporate Lean 6S, quoted per engagement. Live. |
| None, blocked by front matter | 4 | Book in three formats and the manual. Issue #3. |
| None, cannot ship | 34 | Kits, courses, tools. No supplier, platform or stock. |

That is the whole catalogue. There is no fifth category and nothing without a
buy path that should have one.

### Why invoicing rather than another link

Corporate work has no fixed price, so a payment link cannot express it. The
consulting page already said the right thing, that the scope is built with the
customer and a quote follows. What did not exist was anything behind that
sentence. `ops/stripe_invoice.py` is that: it finds or creates the customer,
raises a line item, attaches the published refund terms as the invoice footer,
and stops at draft.

Three guards, each deliberate:

- **Draft is the default.** Nothing is finalised or emailed without `--send`,
  so the worst outcome of a mistake is a draft nobody sees.
- **Live sending needs `STRIPE_ALLOW_LIVE=1`**, the same guard the product and
  link scripts carry. A script that can bill a real customer on its first run
  will eventually bill one by accident.
- **The footer is copied from `site/terms.html`.** If the published refund
  terms change, this must change with them, or an invoice promises something
  the site does not.

### A latent hazard found and fixed

The keys in `.env.secrets` had a leading space, `" sk_live_..."`. Most parsers
survive that, and `stripe_check.py` did because it strips. An ad hoc script
testing `key.startswith("sk_live_")` did not: it reported **test mode while
operating on the live account**. That is the dangerous direction to be wrong,
because the mode check is exactly what decides whether a script is allowed to
create real objects. The file is normalised and all four credential loaders now
strip, so a stray space cannot make a live key look safe again.

---

# Where this actually stands, 2026-08-20

## The account

Live. `acct_1U5rDs6OlZmKL8mF`, charges enabled, payouts enabled. 8 products, 8
prices, 2 payment links. `ops/stripe_catalog.py` keeps Stripe and the site
catalogue in step, in one direction: the site follows Stripe, so there is only
ever one answer to what is buyable.

## What can be bought right now

| Offer | Price | Link |
|---|---|---|
| Virtual Home Consult | $250 | live |
| In-Home Reset Day | $1,200 | live |

Both now redirect to `/thanks.html` with a page that says what actually happens
next, rather than to the contact form they used to land on. Both accept
promotion codes and always create a customer record, so an order can be traced
to a person.

## What is held back, and by whom

Nothing here is waiting on Stripe. Every one of these is a catalogue entry with
a price and no payment link, because a payment link is an invitation to hand
over money and these cannot be delivered.

| SKU | Price | Blocked by |
|---|---|---|
| BK-EB, ebook | $18 | 7 unanswered front matter fields, issue 3 |
| MZ-MANUAL | $29 | the same 7 fields |
| BK-HC, hardcover | $34 | no printer, nothing to post |
| BK-BUNDLE | $44 | the same, plus the front matter |
| DECK-ENTRY-PDF | $12 | 46 illustrations not drawn, issue 20 |
| DECK-ENTRY-BOX | $29 | no printer, no quote, issue 20 |

The 24 tools, 4 kits, 4 courses and the app are deliberately not in Stripe at
all. They have no supplier, no platform and no fulfilment, so a product record
for each would be clutter describing nothing.

## Fulfilment

Stripe takes the money and stops. It does not host files and it does not
deliver anything, and its own documentation warns against using the post
payment redirect for fulfilment, because a customer who closes the tab never
loads it.

`ops/stripe_fulfil.py` polls for paid orders and emails the file. A webhook is
what Stripe recommends and would need a public HTTPS endpoint with a signing
secret, so a service to run, deploy, monitor and secure. At single figures of
orders that is the wrong trade, and Stripe's docs name a scheduled check as the
recognised alternative. This reuses the mailer and the runner that already
exist and adds no new service, no new port and no new secret.

**There is no database.** The record of what has been sent is `fulfilled_at` on
the PaymentIntent, so Stripe holds the state. The run can happen from anywhere,
twice at once, or after this repository is lost, and still cannot send twice.

**It has been tested end to end.** `python ops/stripe_fulfil.py --selftest
BK-EB support@6s-success.com` puts a synthetic order through the real
`deliver()`, and the message was read back over IMAP: correct sender, correct
body, and an 0.81 MB attachment that opens as a valid EPUB with all 50 chapters
and clean zip integrity. The self test calls the real delivery code rather than
a copy of it, because a test of a copy proves nothing and looks like proof.

The cost of polling is latency. `/thanks.html` promises delivery within the
hour and the schedule runs every 30 minutes, which leaves room for one run to
fail and the next to still keep the promise. When volume makes that
unacceptable, replace the poller with a webhook. The delivery half of the code
does not change.

## The one thing fulfilment needs from you

`.github/workflows/fulfil-orders.yml` runs every 30 minutes and currently
**skips**, visibly, because `STRIPE_SECRET_KEY` is not in GitHub Secrets. It
skips rather than fails on purpose: a red mark every half hour for weeks would
teach anybody watching to ignore it.

### What I tried, and where it actually stopped

I can write GitHub secrets. The token has `repo` scope and I set the four SMTP
secrets myself, so declining to set this one was a judgement call rather than a
limit, and an inconsistent one.

The judgement itself still holds, and Stripe states it plainly: *"Stripe
recommends always using RAKs instead of unrestricted secret keys, especially
when giving a key to an AI agent."* The key in `.env.secrets` is a full access
live key that can create charges and issue refunds. The fulfilment job needs to
read what was bought and mark it delivered, and nothing else.

So rather than stop, I went and made the restricted key. In your Dashboard I
filled the whole form: named it **fulfilment (GitHub Actions)**, chose
**Powering an integration you built** rather than one of the 30 to 40
permission templates, and set exactly two permissions out of 174 rows,
**Checkout Sessions: Read** and **Payment Intents: Write**.

**Creating the key is gated behind an hCaptcha.** Stripe runs bot detection on
API key creation, and solving a CAPTCHA is not something I will do. That is the
real stopping point, and it is a better answer than the one I gave first.

### Finishing it, about 30 seconds

The form is filled and waiting. Either solve the challenge on that screen, or
if the tab is gone, remake it: Dashboard, Developers, API keys, **Create
restricted key**, **Powering an integration you built**, **Choose your own**,
name it `fulfilment (GitHub Actions)`, set **Checkout Sessions: Read** and
**Payment Intents: Write**, leave all 172 other rows on None.

Then paste it to me and I will put it in GitHub Secrets and verify the workflow
against it. Or add it yourself at
https://github.com/Klingdom/6s-success/settings/secrets/actions as
`STRIPE_SECRET_KEY`.

A key scoped that way can read what was sold and mark it delivered. It cannot
move money, refund anything, or read a card. If it leaked tomorrow the worst
case is somebody learning what has been sold.

### If you would rather not bother

Say so and I will put the existing full access key in instead. It works
identically, it is your account and your call, and the only cost is that the
blast radius if it ever leaked goes from "somebody sees the order list" to
"somebody can move money". I would not choose it, but it is a real option and
it takes me one command.

Until either happens, no digital order can be delivered automatically. That
costs nothing today, because no digital product is sellable yet for the reasons
in the table above.

## Not set up, and why

**Stripe Tax.** Selling digital goods across borders creates VAT and sales tax
obligations that vary by the buyer's country. Stripe Tax handles it, costs a
percentage per transaction, and needs tax registrations we do not have. Worth
revisiting at the first sign of real international volume, not before. The
alternative worth looking at is Managed Payments, where Stripe becomes merchant
of record and carries the tax compliance itself.

**Subscriptions.** Nothing recurring exists to sell. The app's Pro tier at $49
a year is the obvious candidate and the app is not built.

**A cart checkout.** The site's cart is still staged for v2 and moves no money.
Everything buyable today is a single item, so a payment link per item is the
whole job. A cart needs Checkout Sessions, which needs a server.
