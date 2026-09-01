# Ledgerium AI billing, operated from the 6S Success Stripe account

**Configured:** 2026-09-01 · **Account:** `acct_1U5rDs6OlZmKL8mF` (6S Success)
**Mode:** Live · **Watched by:** `ops/check_ledgerium.py`, `gate_ledgerium` in preflight

Ledgerium AI is a separate business that bills through this Stripe account. Its
revenue does not appear in the 6S Success catalogue, dashboard or backlog, so
this file and the gate are the only things in this repository that know it
exists.

---

## 1. What the brief assumed, and what was actually true

The brief expected `sk_test_`, based on a Ledgerium status doc dated 2026-05-28
saying "Stripe Live mode not configured", and asked me to confirm or refute it
first.

**Refuted in part, confirmed in effect.** The 6S Success key is `sk_live_`. But
the live account contained **zero Ledgerium products and zero recurring prices
of any kind** across 156 active products, so Ledgerium's configured Starter
price IDs do not exist here. Whatever key Ledgerium holds, it is not pointed at
live objects in this account.

So the doc's conclusion was right even though the key prefix was not: this was
a full Live Mode build, Step 2 **and** Step 3.

## 2. What now exists in Live Mode

| Env var | Price ID | Amount | Period |
|---|---|---|---|
| `STRIPE_STARTER_MONTHLY_PRICE_ID` | `price_1UAttB6OlZmKL8mFGejaGLBz` | $49.00 | month |
| `STRIPE_STARTER_ANNUAL_PRICE_ID` | `price_1UAttB6OlZmKL8mFtPg9U1az` | $492.00 | year |
| `STRIPE_SOLO_MONTHLY_PRICE_ID` | `price_1UAttC6OlZmKL8mFVUmsZUUh` | $89.00 | month |
| `STRIPE_SOLO_ANNUAL_PRICE_ID` | `price_1UAttC6OlZmKL8mFF5Cu3VjD` | $888.00 | year |

Products: `Ledgerium Starter` `prod_VBGQcQ7UNs6s6K`, `Ledgerium Solo`
`prod_VBGQ3Utzmf9ST6`, each carrying `metadata.ledgerium_plan`.

The annual amounts are the **full yearly charge**, not the monthly equivalent.
$492 and $888, not $41 and $74. Verified by reading each price back from Stripe
after creation rather than trusting the create call.

## 3. Webhook

`we_1UAtuQ6OlZmKL8mFElWgkyiF`, enabled, on
`https://ledgerium.ai/api/billing/webhook`, subscribed to all six required
events: `checkout.session.completed`, `customer.subscription.updated`,
`customer.subscription.deleted`, `invoice.payment_failed`,
`invoice.payment_succeeded`, `customer.subscription.trial_will_end`.

The signing secret is in `.env.secrets` (gitignored) as
`LEDGERIUM_STRIPE_WEBHOOK_SECRET`. It was never printed to a terminal and is
not in shell history.

## 4. Customer portal

`bpc_1UAtus6OlZmKL8mFsiZumgyf`, default and active. Subscription update
enabled, proration `create_prorations` (upgrades bill immediately), cancel at
period end, payment method update and invoice history on.

**A note on verifying this one.** The API accepts
`features.subscription_update.products`, *requires* it when subscription update
is enabled, and then does not return it in the response. So the obvious check
(read it back) says `None` and looks like failure. It is not: sending a
deliberately invalid price returns `No such price`, which proves Stripe parses
and validates the list. The field is write-only in this response shape.

Worth recording because the first reading of that silence was wrong, and the
same silence will mislead the next person.

## 5. Statement descriptor, done differently from the brief

The brief suggested setting the **account** descriptor to `6S LEDGERIUM`. I set
it on the **products** instead.

The account descriptor stays `6S SUCCESS`. Stripe applies a product's
`statement_descriptor` to subscription charges for that product, so a Ledgerium
subscriber sees `6S LEDGERIUM` on their card line while somebody buying the book
or a card deck still sees `6S SUCCESS`. Changing it account-wide would have put
LEDGERIUM on the statement of every 6S Success customer, which trades one
unrecognised charge for another.

## 6. A duplicate was created and cleaned up

The first version of the create script used `products/search` to check for
existing products. That index lags writes by up to a minute, so a rerun did not
see what it had just made and created a second Starter and a second Solo in a
live account.

Both duplicates and their prices are archived (`prod_VBGQNf4fqosqwP`,
`prod_VBGQ5rDrfss20s`). The script now lists and filters, which is immediately
consistent, and a rerun finds all four and creates nothing.

## 7. What is still needed, and it is not in this account

Ledgerium's own repository needs these set, and I have no access to it:

```bash
gh secret set STRIPE_SECRET_KEY        # paste, Enter, Ctrl+D. Never inline.
gh secret set STRIPE_WEBHOOK_SECRET    # same
gh secret set STRIPE_SOLO_MONTHLY_PRICE_ID    --body "price_1UAttC6OlZmKL8mFVUmsZUUh"
gh secret set STRIPE_SOLO_ANNUAL_PRICE_ID     --body "price_1UAttC6OlZmKL8mFF5Cu3VjD"
gh secret set STRIPE_STARTER_MONTHLY_PRICE_ID --body "price_1UAttB6OlZmKL8mFGejaGLBz"
gh secret set STRIPE_STARTER_ANNUAL_PRICE_ID  --body "price_1UAttB6OlZmKL8mFtPg9U1az"
```

Then redeploy Ledgerium and check the public endpoint:

```
https://ledgerium.ai/api/billing/sku-availability
```

Both `starter` and `solo` should read `{"monthly":true,"annual":true}`.

## 8. Why a gate watches this

`ensure_link` retires superseded payment links and `ensure_product` deactivates
prices when an amount changes. Both act only on objects carrying
`metadata.sku`, and Ledgerium's carry `metadata.ledgerium_plan` with no payment
links, so today they are out of reach.

"Today" is the load-bearing word, and an eight day payment outage here started
with tooling doing exactly the right thing to the wrong object. `gate_ledgerium`
fails preflight if any of the four prices is archived, priced wrongly, renewing
on the wrong interval, or if the webhook stops being enabled with all six
events. Proved by archiving a price, watching it fail, and restoring it.
