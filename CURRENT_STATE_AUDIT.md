# Current State Audit

Phase Zero of `super prompts/Claude_Code_Super_Prompt_6S_Success_Grow.md`.
Living operating artifact, not a report. Every line below was measured on the
date shown, and anything that could not be measured says so rather than
guessing.

**Measured 2026-08-31.**

---

## The seven risks the growth prompt asks to be verified

The prompt is explicit: "Do not assume an issue still exists. Test it." So each
was tested against the current repository and the live site. Five of the seven
are no longer defects, and two of those were never defects in the form stated.

| # | Risk as written | Verified state |
|---|---|---|
| 1 | Shop said Stripe checkout while cart said secure checkout arrives in v2 | **Resolved.** No "v2" language remains in `site/cart.html`. `site/shop.html` carries 155 live payment links. |
| 2 | Quest "Read the full method for this zone" resolves to a placeholder anchor | **Resolved.** The template ships `href="#"` as a placeholder, and `quest.js:703` sets `#c-zone-link` to `c.zone.url` before the card is shown. |
| 3 | Availability language varied between "in development" and "available today" | **Resolved.** Neither phrase, nor "coming soon", appears on any top level page. |
| 4 | Paid products promised email delivery within an hour | **Not a defect.** The single "within an hour" on the site is zone copy on `deck.html`, describing how soon a household uses the Landing Spot after finishing it. All eight actual delivery promises read "within a few hours" and agree with each other. |
| 5 | Newsletter capture used a vague "Join" proposition | **Fixed 2026-08-31.** All 186 pages now carry a concrete offer above the field: "Get your first five Quest cards. One small zone each day, with a clear finish line." with a link straight to `quest.html`, no email required. Verified in headless Chromium against the served page: the sentence renders, and the link resolves 200. The email field itself still cannot store an address (Listmonk is not wired), so its button now reads "Keep me posted" rather than promising anything; `site/assets/js/site.js`'s `wireNewsletter()` already tells anyone who submits it that plainly and hands them a one click mailto. |
| 6 | Customer proof and real transformations were limited | **Correct as it stands.** No testimonial, rating, star or customer-count claim exists anywhere on the site. That is the right state: no stranger has bought yet, and CLAUDE.md section 8 forbids inventing proof. Limited proof is a fact to change by earning it, not a defect to patch. |
| 7 | Quest progress local to one browser, disconnected from household and paid systems | **True, and by design today.** `quest.js` keeps state in `localStorage` under `6s.quest.v1`. The growth plan requires this to change; it is architecture, not a bug. |

## What blocks revenue right now

Measured, not inferred:

- **Production cannot take money.** All six payment links the live site serves
  are deactivated in Stripe. Every one of the 155 links in this repository is
  active, so the deploy fixes it.
- **The live shop is 10 products against 159 here.** Production is not the same
  shop with broken buttons, it is a much smaller one.
- **7 of 9 fingerprinted assets on production differ from this repository**,
  including the Quest, which is running 11 KB behind.
- **The mailing list cannot store an address.** Listmonk's root URL is still
  `localhost:9000`, so every double opt-in link is unclickable, and its from
  address belongs to another brand. Both are instance-wide settings.

Every one of these clears with actions only Phil can take. They are listed in
the command deck under "What needs you" and are not repeated as a caveat
elsewhere.

## Against the Month-12 revenue model

The growth prompt's model is $21,500 monthly gross, of which at least half must
recur:

| Stream | Target | Exists today |
|---|---:|---|
| 6S Plus subscriptions | $11,250 | **Nothing.** No subscription product, no plan, no recurring billing. This is the largest single line and the one with no foundation at all. |
| Digital products | $5,250 | 159 catalogue items, 158 buyable, live payment links ready. Blocked only by the deploy. |
| Affiliate commerce | $3,000 | Programme built from the product appendix; identifiers in `ops/affiliate-accounts.json`. |
| Services | $2,000 | Consulting page live; no paid engagement has run. |

The honest reading: the half of the target that must recur does not exist yet,
and the half that does not have to recur is one button press from working.

## North Star

The prompt sets it as **sustained zones per active household**, where sustained
means completed and later confirmed still holding at audit.

Nothing currently measures it. The Quest records completed cards and completed
zones in `localStorage`, which cannot see a household or a later audit, and
analytics records visits rather than outcomes. Measuring this properly needs
the account and household layer the mobile plan describes.

Recorded here so that the gap is visible rather than assumed closed.

## What was checked to produce this

Repository at `fd66c614`, live site at `https://6s-success.com`,
`ops/check_live_links.py`, `ops/deploy_freshness.py`,
`ops/check_integrations.py`, `ops/preflight.py`, and direct reads of
`site/cart.html`, `site/shop.html`, `site/deck.html`, `site/quest.html`,
`site/assets/js/quest.js` and `site/assets/js/site.js`.
