# Affiliate programme: compliance and risk position

Reviewer: security-auditor (independent). Date: 2026-08-28.
Scope: `ops/affiliate.py`, `ops/affiliate-accounts.json`, `ops/preflight.py`,
`ops/stripe_fulfil.py`, `ops/build_epub.py` / `build_catalog.py` outputs,
`.github/workflows/fulfil-orders.yml`, `site/privacy.html`, `site/terms.html`,
`site/disclaimer.html`, `site/accessibility.html`, `site/resources.html`,
`.gitignore`, CI secret scanning.

State at review: all ten programmes are `not applied`, no `publisher_id` is set,
`ops/affiliate-catalogue.csv` has 123 rows and **0** populated `Affiliate URL`
cells, and no site page contains an outbound host other than `6s-success.com`
and `buy.stripe.com`. Nothing is live. Everything below is preventable now and
expensive later.

**Decision: BLOCKED for launch. Four items must be fixed before the first
approved identifier is pasted into `ops/affiliate-accounts.json`.**

---

## Blocking findings

### AFF-01 (HIGH) The offline-document rule is enforced on a directory that contains none of the delivered documents

`check()` in `ops/affiliate.py` globs `site/downloads/*` only. The documents that
actually reach customers are built and emailed by
`.github/workflows/fulfil-orders.yml`, which runs `python ops/build_epub.py` and
`python ops/build_catalog.py --build` and then `python ops/stripe_fulfil.py
--send`. `ops/preflight.py` — the only caller of `--check` — is not in that
workflow. So the rule with a contract behind it never runs on the artefacts the
contract covers.

The delivered set, from `DELIVERY` and `_add_generated()` in
`ops/stripe_fulfil.py`, is:

| Artefact | Path | Scanned by `--check`? |
|---|---|---|
| The ebook (EPUB) | `build/6S-Success-Home-Edition.epub` | no |
| Micro Zone Manual | `content/manual/micro-zone-manual-publishable.html` | no |
| Whole House Print Pack | `build/6S-Whole-House-Print-Pack.html` | no |
| Entryway Deck | `build/entryway-deck-illustrated.pdf` | no |
| 149 generated packs | `build/products/*.html` | no |
| Standards Pack | `build/6S-Standards-Pack.html` | no |
| Sample chapters | `site/downloads/*.html`, `*.pdf` | partially, see AFF-02 |
| `site/downloads/assets/book.css` | subdirectory | no — glob is not recursive |

Remediation: move the scan off `site/downloads` and onto a list of *deliverable*
paths taken from `stripe_fulfil.DELIVERY` plus `generated_products.products()`,
so a new sellable file is scanned the day it becomes sellable rather than the day
somebody remembers. Add `python ops/affiliate.py --check` as a step in
`fulfil-orders.yml` **after** the build steps and **before** `--send`, so a
violating artefact cannot be mailed.

Verification: add an affiliate id to a scratch copy of the print pack, run the
gate, confirm exit 1; remove, confirm exit 0.

### AFF-02 (HIGH) The scan is format-blind: EPUB and PDF are exactly the formats it cannot read

`check()` does `io.open(f, encoding="utf-8", errors="ignore").read()` and then
matches on the id string and `[?&]tag=[\w-]+-20`. An EPUB is a ZIP and a PDF
stores text in compressed streams, so neither yields readable URLs.

Measured on the real artefacts:

- `build/6S-Success-Home-Edition.epub` — 853,687 bytes, 62 zip entries.
  `http` occurrences visible to the current read: **0**.
  `http` occurrences inside the decompressed XHTML/OPF entries: **313**.
- `site/downloads/…Sample (Chapters 1-30).pdf` — 32.7 MB.
  `http` visible to the current read: **0**. The text lives in compressed
  streams, i.e. the check is passing a 32 MB document without inspecting a
  single byte of its text.

An affiliate URL placed in the book would pass the gate silently, and the gate
would print `affiliate rules: no links in downloads` while doing so. Amazon's
operating agreement prohibition on ebooks and PDFs is therefore unenforced in
the two formats it names first.

Remediation: read EPUB via `zipfile` over `*.xhtml/*.html/*.opf/*.ncx`; read PDF
`/URI` annotations and `zlib.decompress` the streams (or shell to `pdftotext`),
and fail closed — if a format cannot be parsed, report it as unchecked rather
than clean. The current success message is stronger than the evidence.

### AFF-03 (HIGH) The non-Amazon disclosure states the opposite of the truth

`ops/affiliate.py`, `disclosure()`:

```python
amazon=AMAZON_SENTENCE if has_amazon else
"We are not paid by any retailer to feature a product."
```

On a page carrying Walmart, Target or Lowe's links but no Amazon link, the block
renders as: "Some of the links below are affiliate links, which means 6S Success
may earn a commission if you buy through them" followed by "We are not paid by
any retailer to feature a product." A commission is payment from a retailer
arising from the feature. The disclosure contradicts itself in the same box, and
the second sentence is the kind of affirmative denial the FTC treats far more
harshly than a missing disclosure. Nine of the ten programmes are non-Amazon, so
this is the default branch, not the edge case.

Remediation: delete the `else` branch. The honest non-Amazon fallback is nothing
at all, or "No retailer pays us to feature a product; where we earn, it is a
commission on a sale and it is disclosed above." Keep the Amazon sentence
verbatim.

### AFF-04 (HIGH) `site/terms.html` currently asserts there are no affiliate links

Current wording: "If any page here ever carries an affiliate link, meaning we may
earn a commission, that will be disclosed clearly on the page where the link
appears. **There are no affiliate links on this site today.**"

The moment the first link ships, a legal page on the site states a falsehood.
This is the same class of defect `gate_stale_claims()` exists to catch, on the
one page where being wrong is a liability rather than an embarrassment. Note
that `gate_stale_claims` does not match this sentence, so nothing will surface
it.

---

## 1. FTC disclosure: wording and placement

The wording is better than most, and the second paragraph — that products are
listed because a micro zone needs them and the reason is written next to each —
is the right instinct. Four specific weaknesses.

**(a) "Some of the links below are affiliate links."** "Some" leaves the reader
unable to tell which. FTC endorsement guidance expects a disclosure a reader
cannot miss and can attach to the specific recommendation. On
`site/resources.html` — one page, 20 rooms, 114 micro zones, roughly 28 product
types under the entryway alone — a single block at the top is separated from the
patio links by the length of the entire page. On a phone (`CLAUDE.md` §44) the
reader scrolls past it once and then sees several hundred links. Fix: keep the
block, and additionally mark each affiliate link inline, e.g. a short "(paid
link)" adjacent to the anchor, or a per-room repeat of a one-line disclosure.
Anyone arriving at a `#zone-anchor` deep in the page, or on one of the 115
`site/zones/` pages, must meet the disclosure before the link.

**(b) "at no extra cost to you."** True, and permissible, but it converts a
disclosure into a reassurance. Keep it if you like; do not let it lead. It must
not be the most prominent sentence in the block.

**(c) The second paragraph makes a promise nothing verifies.** "the reason is
written next to it" is asserted to the reader, but rule 3 in the module docstring
is not implemented in `check()` at all — only rules 1 and 2 are, and both
partially. If any generated page ever lists a linked product without its reason,
the disclosure itself becomes a false statement. Either implement the check (each
element carrying an affiliate link must have a sibling reason string) or soften
the sentence to describe policy rather than guaranteeing every instance.

**(d) The block is unstyled.** There is no `.disclosure` or `aside` rule in
`site/assets/css/site.css`. It will render at default body size with no visual
separation. That is not fatal — "conspicuous" does not require a box — but the
styling decision should be made deliberately and must not end up small, grey or
collapsed. `<aside>` is also announced as complementary by screen readers, which
some users skip; a `<section>` with a heading in the reading order is safer, and
`site/accessibility.html` commits the site to that standard of care.

**Placement enforcement is weaker than it reads.** Reproduced from line 182 of
`ops/affiliate.py`:

```python
if s.index(DISCLOSURE_ID) > s.rindex("data-aff=") if "data-aff=" in s else False:
```

Three defects, all confirmed by execution:

1. Guarded by `"data-aff=" in s`, so a page whose links are plain Amazon
   `?tag=…-20` URLs — the exact shape `has` matches on the line above — skips the
   order check entirely. A disclosure at the very bottom of an Amazon page
   passes.
2. It compares against `rindex`, the *last* link. A disclosure sitting between
   link 1 and link 500 passes.
3. Presence is tested with `DISCLOSURE_ID not in s`, satisfied by any occurrence
   of the string, including a footer `href="/affiliate-disclosure.html"`. A link
   to a disclosure page counts as a disclosure.

Fix: compare `s.index(disclosure_markup)` against the minimum index of any
affiliate link across both patterns, and require the opening tag
`id="affiliate-disclosure"` rather than the bare string.

## 2. The offline-document rule: full gap list

Covered in AFF-01 and AFF-02. The surfaces that could carry a link and escape the
current check, in the order they are most likely to:

1. **The EPUB** — built in CI at fulfilment time, never scanned, and unreadable
   by the scanner even if it were pointed at it.
2. **`build/products/*.html`, 149 generated packs** — `.gitignore` line 55
   excludes `build/products/`, so they exist only on the machine that builds
   them, are attached to customer email minutes later, and are never reviewed by
   a human or a gate.
3. **The Micro Zone Manual** (`content/manual/micro-zone-manual-publishable.html`)
   — sold and attached; `ops/build_manual_print.py` already renders "Estimated
   Retail Low/High" columns for the 123-product appendix. The temptation to make
   those rows clickable is obvious and would be a direct breach.
4. **Fulfilment email bodies** — `DELIVERY[...]["note"]` and `NOTE[...]` in
   `ops/stripe_fulfil.py`. Plain text today, containing only `SITE`. Nothing
   inspects them.
5. **The Whole House Print Pack and Standards Pack** — currently contain zero
   outbound hosts; both are attached to orders.
6. **`site/downloads/assets/`** — the glob is `downloads/*`, not recursive.
7. **Generated site pages** — `site/zones/` (115) and `site/rooms/` (20) are
   built by `ops/build_zone_pages.py` / `build_resources.py`. These *are* covered
   by the recursive disclosure glob, but see the placement defects above.
8. **Structured data** — `ops/build_product_schema.py` emits `Product` +
   `Offer` + `"seller": {"@type": "Organization", "name": "6S Success"}`, and the
   site already carries 161 `Offer` nodes. If a retail product ever gets a
   schema node, that markup will tell Google and every AI answer engine that 6S
   Success is the seller of a Lowe's item at a price 6S Success does not set.
   That is a misrepresentation and a rich-results penalty. Any affiliate product
   node must omit `offers`/`seller` entirely, or be excluded from schema
   generation.
9. **Retail prices** — the catalogue carries `Estimated Retail Low/High` for all
   123 rows and `build_manual_print.py` publishes them. Amazon's agreement
   restricts displaying prices to data from its Product Advertising API with a
   timestamp. Publishing an "estimated retail" range next to an Amazon link is a
   termination-grade breach on its own. Keep the ranges where they are today —
   in the manual's planning appendix, explicitly labelled "planning estimates,
   not quotations" — and never place a number next to a link.

## 3. Email

**Amazon prohibits affiliate links in email outright** — the operating agreement
excludes email, and the same clause covers the ebooks and PDFs already noted.
Most network programmes (Impact, CJ, Rakuten, Awin — the likely rails for
Walmart, Target, Home Depot, Lowe's, The Container Store, Wayfair, Office Depot,
Ace) either prohibit email placement or require the mailing to be pre-approved
and CAN-SPAM compliant. Treat the position as: **no affiliate link in any email
this system sends, from any programme, without a written approval recorded in the
registry.**

Two senders matter:

- **`ops/stripe_fulfil.py`** — transactional fulfilment. Body is plain text and
  carries only `SITE`. Safe today, unguarded tomorrow.
- **`ops/roadmap_report.py` / `send_brief.py` / `hourly_brief.py`** — internal,
  to Phil. Low external risk, but they mail PDFs built from repository content
  and would carry a link in that content without noticing.

What would enforce it here: extend `check()` with a scan of the email note
strings (`stripe_fulfil.DELIVERY[*]["note"]`, `NOTE`, and the `text` block) for
any approved `publisher_id`, any `tag=` parameter, and any host present in
`affiliate-accounts.json`; and add `--check` to `fulfil-orders.yml` before the
send step, which also closes AFF-01. Add an `"email_allowed": false` field to each
programme in `ops/affiliate-accounts.json` so the position is recorded per
programme rather than assumed.

## 4. Privacy page: what must change, what stays

`site/privacy.html` is accurate today and most of it should not be touched.

**Stays exactly as written** — all of these remain true after launch:

- "We count visits … self-hosted software running on our own server."
- "This site sets **no cookies**. There is no cookie banner because there is
  nothing to consent to." An affiliate click sets a cookie on the *retailer's*
  domain, in a context 6S Success does not control and is not the controller of.
  Nothing on 6s-success.com sets one. Do not weaken this to a hedge, and do not
  add a cookie banner — adding one would be inaccurate and would cost the page
  its credibility.
- "No Google Analytics, no Meta pixel, no advertising network, no session
  recording, no behavioural profiling."
- The cart, forms, email, server logs and children sections.

**Must change before the first link — one new section, "Links to retailers":**

State plainly that (a) some outbound links are affiliate links, (b) clicking one
takes the reader to the retailer or to the retailer's tracking network, (c) at
that point the retailer and its network receive the reader's IP address, browser
details and the fact that they arrived from 6s-success.com, and set their own
cookies under their own privacy policies, (d) 6S Success receives only aggregate
commission reporting and never learns who clicked or what any individual bought,
and (e) no data is sent to any retailer unless the reader clicks.

**The one sentence that needs care** is under "Third-party requests": "The site
makes **no requests to third-party servers**. Fonts, styles, scripts, images and
the visit counter are all served from this domain, so browsing here does not
reveal your visit or your IP address to any other company."

This stays true for an `<a href>`, which is user-initiated navigation, not a
request the site makes — but only if the implementation stays disciplined. It
becomes false the moment anyone hotlinks a product image from a merchant CDN,
adds Amazon SiteStripe image markup, or adds an Impact/OneLink JavaScript tag.
Add the qualifier "while you are on a page here" and the clause "clicking a link
to another site is, as always, a visit to that site."

**Related control:** `gate_third_party()` in `ops/preflight.py` fails on *any*
`https?://host` outside its allowlist, in HTML, CSS or JS, without distinguishing
an anchor `href` from a `src`. The first affiliate link will therefore fail
preflight. Do **not** fix this by adding the ten merchant hosts to `allowed` —
that would simultaneously permit `<img src>` and `<script src>` from those hosts
and silently falsify the privacy promise. Fix it by parsing the attribute:
permit merchant hosts in `href` on `<a>` only, and keep every other attribute on
the existing allowlist. That single change is what keeps the privacy page honest
under load.

## 5. Terms page

Beyond removing the now-false sentence (AFF-04), `site/terms.html` needs, under
"Links to other sites":

- **We are not the seller.** A purchase made after following a link is a
  contract between the reader and that retailer, on that retailer's terms.
- **We do not handle payment, delivery, warranty, returns or refunds** for those
  items, and cannot access an order placed with a retailer. The existing refund
  section covers 6S Success's own six SKUs and must not be read as covering
  retail purchases — say so explicitly, because the page currently reads as one
  refund policy.
- **Commission.** Where a link is an affiliate link, 6S Success may earn a
  commission at no additional cost to the reader, and this is disclosed on the
  page carrying the link.
- **Price and availability change.** Any figure shown is an estimate at the time
  of writing, not an offer; the retailer's page is authoritative. This also
  protects the "Estimated Retail Low/High" ranges already published in the
  manual.
- **Recommendation basis.** Products are selected because a micro zone needs
  that type of thing; commission does not determine what is recommended or the
  order it appears in. This is `CLAUDE.md` §48 stated to the reader, and it is
  the sentence that makes the disclosure's second paragraph enforceable as a
  commitment.
- **Safety carries across.** The existing safety notice already forms part of the
  terms; add that it applies equally to any product reached through a link, since
  a linked item (ladder, chemical, power tool) can hurt someone.

`site/disclaimer.html` needs no change; it already covers chemicals, height,
tools, children and pets, and it is referenced from terms.

## 6. Ranked risks

**1. Amazon account termination for a link in a document, most likely the EPUB.**
Highest likelihood by a distance. The book is the flagship product, it is
regenerated by CI on every fulfilment run, the writing pipeline is heavily
automated across 50 chapters, and the only gate cannot read the format. Amazon
terminates rather than warns, forfeits accrued commission, and a terminated
Associates account is difficult to reinstate — and the same email,
`support@6s-success.com`, is the identity used for all ten applications, so a
termination is visible and attributable. *Prevented by:* AFF-01 and AFF-02 —
format-aware scanning of the actual deliverable list, wired into
`fulfil-orders.yml` ahead of `--send`, failing closed on any format it cannot
parse.

**2. A recommendation that hurts somebody, or a claim the business cannot
support.** The catalogue is 123 product types across 114 micro zones, including
"Impact-rated safety glasses", moisture absorbers, cleaning chemicals and
ladder-adjacent work. A commission changes the character of that advice from
editorial to commercial, and the FTC and a plaintiff both read it that way. The
`Safety / Compatibility Notes` column exists and is populated ("Do not block
exits", "Use appropriate attachment") — the risk is that it does not survive the
transformation into a linked recommendation. *Prevented by:* refusing to link any
row whose safety note is empty; carrying the safety note into every rendered
linked recommendation; keeping the safety notice linked from any page with
affiliate links; and never linking a specific SKU for a life-safety item
(respirators, eye protection, ladders, smoke and CO alarms) where fit and
certification matter more than availability — recommend the type and the standard
to look for, which is what the manual already does.

**3. An FTC-relevant disclosure failure on a long page, compounded by the
self-contradicting non-Amazon text.** AFF-03 puts an affirmative denial of
payment on the same page as paid links, and the placement gate does not enforce
order for Amazon-style links at all. The realistic trigger is not an FTC
investigation but a reader or competitor screenshotting "We are not paid by any
retailer to feature a product" next to a tagged link. *Prevented by:* AFF-03,
plus per-link inline marking on `site/resources.html` and the 115 zone pages, plus
repairing the ordering check.

Lower, but real: **structured data claiming 6S Success as the seller** (§2 item
8), which is a slow, quiet reputational and SEO risk rather than a sudden one.

## 7. What must never be stored

Confirmed clean today. Nothing in the current code or files invites a prohibited
value: `ops/affiliate.py`'s docstring and the `_comment` in
`ops/affiliate-accounts.json` both state the boundary, `build_link()` needs only a
public `publisher_id`, and `ops/mailer.py` reads `SMTP_*` from the environment or
from gitignored `.env.secrets` and refuses to run rather than falling back.
`ops/VPS-SEND-KEY.txt` is tracked but contains prose instructions and no key
material.

Never in this repository, in any file, at any time: programme passwords; the
Associates or network account password; tax identifiers (SSN, EIN, W-9 or W-8BEN
content); bank account, routing or IBAN details; payment threshold or remittance
settings; two-factor recovery codes; network API secrets; support-portal session
cookies; and any per-user click or conversion report containing an identifiable
buyer.

Two gaps to close now, both cheap:

- **`deep_link_template` is an unvalidated free-text field in a tracked file.**
  Several networks issue deep-link builders whose URL contains an auth token or
  API key. Pasting one in follows the documented workflow exactly and commits a
  secret. Add a validator to `--check` that rejects any template containing
  `key`, `secret`, `token`, `auth`, `password` or a long high-entropy value, and
  say so in the `_how_to_fill` note.
- **`.gitignore` and the CI secret scan are narrower than the risk.**
  `.gitignore` covers `.env.local`, `.env.*.local`, `.env.production`,
  `.env.secrets`, `secrets/`, `*.key`, `*.pem`, `*.p12`, `*.pfx`,
  `credentials.json`, `service-account*.json`. It does **not** cover: `.env`
  (tracked at root — it holds only `DOMAIN` and `ACME_EMAIL`, which is correct
  and documented, but `.env` is the single most conventional filename for an SMTP
  or network secret and it is tracked); `secrets.json`; `creds.json`; `id_rsa`
  and `id_ed25519`; `*.csv` payment or tax exports downloaded from a network
  portal; `*.p8`. Note also that the `.gitignore` comment refers to `site/.env`
  while the tracked file is `/.env` — worth correcting so nobody reasons from the
  wrong filename.
  `.github/workflows/publish-image.yml` scans for
  `sk_live_|sk_test_|SMTP_PASS|BEGIN [A-Z ]*PRIVATE KEY` **under `site/` only**.
  Affiliate credentials will arrive into `ops/`, not `site/`. Widen that scan to
  the whole tree.

---

## Launch checklist

Before pasting the first approved `publisher_id`:

1. AFF-02 — format-aware EPUB and PDF scanning, failing closed on unparsable
   formats.
2. AFF-01 — scan the real deliverable list; add `--check` to
   `fulfil-orders.yml` before `--send`.
3. AFF-03 — delete the "We are not paid by any retailer" fallback.
4. AFF-04 — remove "There are no affiliate links on this site today" from
   `site/terms.html` and add the not-the-seller / no-returns / commission /
   recommendation-basis clauses.
5. `site/privacy.html` — add "Links to retailers"; qualify the third-party
   requests sentence; keep the no-cookies and no-trackers statements intact.
6. `gate_third_party()` — distinguish `<a href>` from `src`; do not allowlist
   merchant hosts wholesale.
7. Repair the disclosure presence and ordering checks; add inline per-link
   marking for long pages.
8. `.gitignore` and CI secret-scan scope; `deep_link_template` validation.

Items 1–5 block. Items 6–8 must land in the same change, because 6 will fail
preflight on day one and 8 is what stops an onboarding paste from becoming a
committed secret.

---

Unrelated defect noticed while reading `ops/stripe_fulfil.py`: the dry-run branch
returns `f"WOULD SEND to {email} ({os.path.basename(path)}, …)"` referencing
`path`, which does not exist in that scope after the change to a `paths` list.
`--dry` will raise `NameError`. Not a security issue; it means the rehearsal
path is currently broken, which matters because that is the path anyone would
use to test the fulfilment change above.
