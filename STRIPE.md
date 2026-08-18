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
