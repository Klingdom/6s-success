# 6S Success Risk Register

> Canonical register of known business, commercial, legal, content, security, reliability, and recovery risks for 6S Success. Records what could stop the business, what evidence establishes it, who owns it, and what would close it.

## 1. Purpose

`RISKS.md` keeps the autonomous system honest about what is currently unsafe, unproven, or unmonetized.

It answers:

- What could stop this business?
- What evidence says so?
- How bad is it, and how likely?
- Who owns reducing it?
- What specific event would close the risk?
- What are we deliberately accepting for now?

Read with:

- `CLAUDE.md`
- `AUTONOMY.md`
- `STATUS.md`
- `EXECUTIVE-DASHBOARD-LIVE.md`
- `BACKLOG.md`
- `DECISIONS.md`
- `SECURITY.md`
- `DISASTER-RECOVERY.md`
- `INCIDENTS.md`
- `ROADMAP.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Core Rule

**A risk is a claim about the future that must be backed by evidence about the present.**

Every entry below cites a file, a measured count, or a GitHub issue.

Do not record:

- vague fears with no evidence
- risks that are actually incidents (those belong in `INCIDENTS.md`)
- risks that are actually work (those belong in `BACKLOG.md`)
- invented probabilities or invented financial exposure

Where a number is not known, write `UNKNOWN` and state what would establish it.

---

# 3. Relationship to Other Files

| File | Holds |
|---|---|
| `RISKS.md` | What might go wrong, and how exposed we are |
| `INCIDENTS.md` | What already went wrong |
| `BACKLOG.md` | The work that reduces a risk |
| `DECISIONS.md` | A deliberate choice to accept, transfer, or mitigate a risk |
| `EXECUTIVE-DASHBOARD-LIVE.md` | The measured state that several of these risks are derived from |

This file does not duplicate the live dashboard. The dashboard reports counts. This file explains why those counts matter.

---

# 4. Risk ID

Use:

`RISK-0001`

`RISK-0002`

Never recycle IDs. A closed risk keeps its ID and its record.

---

# 5. Severity Scale

Severity describes the consequence if the risk occurs.

| Level | Meaning |
|---|---|
| `CRITICAL` | The business cannot operate, or exposure is irreversible |
| `HIGH` | A product line, a revenue path, or customer trust is lost |
| `MEDIUM` | Material rework, delay, or degraded customer outcome |
| `LOW` | Contained annoyance, recoverable within a normal work cycle |

Likelihood uses `LIKELY`, `POSSIBLE`, `UNLIKELY`, or `OCCURRING` where the risk is already materializing.

---

# 6. Risk Status

- `OPEN` active and unmitigated
- `MITIGATING` work is in flight
- `ACCEPTED` deliberately carried, with a recorded decision
- `CLOSED` the closing condition has been met and verified
- `TRANSFERRED` moved to a third party, for example an insurer or a vendor

---

# 7. Risk Record Template

```yaml
id: RISK-0001
title: Short risk title
status: OPEN
severity: CRITICAL|HIGH|MEDIUM|LOW
likelihood: OCCURRING|LIKELY|POSSIBLE|UNLIKELY
owner: agent or owner
evidence:
  - file, count, or issue that establishes this
impact: >
  What actually happens to customers, revenue, or the system.
mitigation: >
  The specific action that reduces it.
closing_condition: >
  The observable event that lets this be marked CLOSED.
review: when this should next be re-examined
```

---

# 8. Register State

Last reviewed: 2026-09-03.

**On the previous "Last reviewed: 2026-08-19" and what it cost.** This
register's own section 22 promises the four `CRITICAL` entries get re-read
every operating cycle. They were not, for over two weeks, across dozens of
recorded cycles in `ops/NIGHTLY-LOG.md`: RISK-0001, RISK-0006, RISK-0008 and
RISK-0010 had all been resolved by real, dated, checkable events (a real
sale 2026-08-21, issue #3 closed 2026-08-25, the catalog reaching 158 of 159
purchasable, and `.github/workflows/checks.yml` existing since 2026-09-01)
and this file kept stating the pre-resolution version of each, including the
single most load-bearing sentence in the whole document: "the most likely
cause is RISK-0001." A register that states a two-week-stale CRITICAL cause
while a different one has since taken its place is not doing the one job
this file exists for. See `gate_risks_register_current` in
`ops/preflight.py`, added this cycle, which fails if this date goes more
than 31 days stale again.

Thirteen risks are recorded. Six are open, one is mitigating, six are
closed. Three open risks are `CRITICAL` (RISK-0007, RISK-0011, RISK-0013).
None have been formally accepted by the owner, so none are `ACCEPTED` yet.

| ID | Title | Severity | Status |
|---|---|---|---|
| RISK-0001 | No route from customer intent to payment | CRITICAL | CLOSED |
| RISK-0002 | The VPS cannot pull the now private repository | CRITICAL | CLOSED |
| RISK-0003 | Card art carries third party trademarks | HIGH | OPEN |
| RISK-0004 | The downloadable book is 30 of 50 chapters | HIGH | CLOSED |
| RISK-0005 | Nothing about customer behavior is measurable | MEDIUM | OPEN |
| RISK-0006 | Safety and legal front matter is new and unreviewed | HIGH | CLOSED |
| RISK-0007 | Single host, no staging, unproven restore | CRITICAL | OPEN |
| RISK-0008 | Nine product lines, none purchasable | HIGH | CLOSED |
| RISK-0009 | Control documents contradict the published canon | MEDIUM | MITIGATING |
| RISK-0010 | No automated quality gate before production | MEDIUM | CLOSED |
| RISK-0011 | Product masters live outside the repository | CRITICAL | OPEN |
| RISK-0012 | No audience is being retained | HIGH | OPEN |
| RISK-0013 | No stranger has ever converted; discovery is the constraint | CRITICAL | OPEN |

---

# 9. RISK-0001 No Route From Customer Intent To Payment

```yaml
id: RISK-0001
title: No route from customer intent to payment
status: CLOSED
severity: CRITICAL
likelihood: OCCURRING
owner: commerce-manager
evidence:
  - 2026-08-21: a real transaction completed end to end (Whole House Print
    Pack, $19, net $18.15) and was verified in the Stripe dashboard and the
    fulfilment path, meeting the closing condition below directly
  - ops/state.json, reconfirmed 2026-09-03: can_take_payment=true,
    catalog_total=159, 158 of 159 catalog items have a live Stripe Payment
    Link or a real free download (only Corporate Lean 6S is quote-only, by
    design, per BACKLOG-2026-H2.md 5.5)
  - site/cart.html no longer states "Secure checkout arrives in v2"; that
    line is absent from the file as of this review
  - 2026-08-30: this route broke for real for at least three days (all six
    live payment links deactivated in Stripe, RETRO-2026-08-30-cycle6.md),
    found and fixed, and is now actively monitored for that specific
    failure mode (ops/check_live_links.py, wired into preflight.py), not
    merely built once
impact: >
  Resolved. The route exists, has carried a real transaction, and is
  monitored for the failure mode that already broke it once. This entry
  stayed OPEN and CRITICAL, and labelled "no other risk in this register
  outranks it," for over two weeks after the route was actually built and
  used; see section 8's "Last reviewed" history and RISK-0013 below.
mitigation: >
  Closed. If a future change removes or breaks the payment path for any
  SKU, re-open this risk; ops/check_live_links.py and ops/check_sellable.py
  are the two automated checks that would catch it first.
closing_condition: >
  Met, 2026-08-21 (first real transaction), reconfirmed 2026-09-03 (158 of
  159 catalog items purchasable per ops/state.json).
review: after any change to pricing, the catalog, or the Stripe integration
```

This was the single constraint named on the live dashboard until it closed. It no longer is: the dashboard's own current headline reads "Discovery, not what can be bought, is the constraint now." See RISK-0013.

---

# 10. RISK-0002 The VPS Cannot Pull The Now Private Repository

```yaml
id: RISK-0002
title: The VPS cannot pull the now private repository
status: CLOSED
severity: CRITICAL
likelihood: LIKELY
owner: vps-docker-manager
evidence:
  - 2026-08-18: deployment architecture changed. The VPS no longer clones this
    repository at all; it pulls a built image from ghcr.io/klingdom/6s-success,
    per DEPLOY-VPS.md and .github/workflows/publish-image.yml
  - ops/verify_deploy.py scored 10 of 10 against the running container the
    same day, per ops/NIGHTLY-LOG.md
impact: >
  Closed by removing the mechanism, not by granting the access originally
  proposed. No deploy key or token exists on the VPS or in this repository.
mitigation: >
  None needed. If a future change reintroduces a repository clone on the VPS
  (rather than an image pull), re-open this risk before relying on it.
closing_condition: >
  Met. Verified image pull and 10/10 verification recorded 2026-08-18.
review: before any change to the deployment mechanism
```

`DISASTER-RECOVERY.md` should be checked for any recovery step that still assumes a VPS-side `git pull`; the current mechanism is an image pull from ghcr.io instead.

---

# 11. RISK-0003 Card Art Carries Third Party Trademarks

```yaml
id: RISK-0003
title: Card art carries third party trademarks
status: OPEN
severity: HIGH
likelihood: OCCURRING
owner: content-editor
evidence:
  - GitHub issue #1, cards EE-001 and EP-005 contain Amazon trademarks, P0
  - GitHub issue #2, 16 further stale card images await regeneration
impact: >
  The Entryway deck is the pilot for a 20 deck product line. Art that depicts
  another company's marks is not safe to print, sell, or use in marketing, and
  reworking it after a print run is far more expensive than reworking it now.
mitigation: >
  Regenerate the affected art without third party marks, then have a qualified
  intellectual property professional review the deck before any commercial
  distribution. This document does not state what the law requires.
closing_condition: >
  Zero third party marks remain in deck art, confirmed by review, and
  professional review of the deck is complete.
review: before any print or sale of a deck
```

Do not treat this entry as legal advice or as a legal conclusion. It records an operational fact and the need for professional review.

---

# 12. RISK-0004 The Downloadable Book Is 30 Of 50 Chapters

```yaml
id: RISK-0004
title: The downloadable book is 30 of 50 chapters
status: CLOSED
severity: HIGH
likelihood: OCCURRING
owner: content-editor
evidence:
  - the free sample is deliberately 30 of 50 chapters (a lead magnet, not the
    sold product); the paid ebook is the 50 chapter EPUB, gated 32/32 in
    ops/build_epub.py, and is not yet deliverable at all pending issue #3
  - 2026-08-17: the sample's title tag, on-page heading, and PDF metadata all
    corrected from "The Complete Book" to "chapters 1 to 30"
  - 2026-08-19: the two on-disk filenames still read "Complete Book" after
    that fix, so a reader's saved file carried the claim the visible link
    text and the title no longer made; renamed both, and the content/book
    mirror copy, to "Sample (Chapters 1-30)"
impact: >
  Resolved by fixing the claim rather than the chapter count, since the file
  is meant to be a partial sample. Closing this the other way, by shipping a
  full 50 chapter sample, would remove the reason to buy the book.
mitigation: >
  Closed. If a future pass changes what this file contains, re-open and
  re-check title, heading, filename, and link text together, not just one.
closing_condition: >
  Met. Link text, on-page title, and on-disk filename all describe the file
  as a 30 chapter sample, consistently, in the site and its content mirror.
review: before the book is offered for sale
```

---

# 13. RISK-0005 Nothing About Customer Behavior Is Measurable

```yaml
id: RISK-0005
title: Nothing about customer behavior is measurable
status: OPEN
severity: MEDIUM
likelihood: OCCURRING
owner: analytics-intelligence
evidence:
  - self-hosted analytics (Umami) is live on every page (site/index.html's
    /stats/script.js include) and matches site/privacy.html's actual current
    promise ("self-hosted software running on our own server, not a
    third-party analytics service... no Google Analytics, no Meta pixel...
    the site makes no requests to third-party servers"); the conflict
    section 23 originally named between this risk and the privacy promise
    is resolved, because the privacy page was written to describe this
    setup, not to forbid it
  - the API token this environment would use to read it live is expired
    (401 on every route) and no operator sandbox can read it
    programmatically; BACKLOG-2026-H2.md item 1.2 (share URL or API key)
    is still open and still the actual blocker
  - 2026-09-02, Phil read the analytics database directly and recorded a
    one-time real baseline in GOALS.md; corrected 2026-09-03 after the
    first read conflated visitor with session (52 visitors/144 visits/30
    days, 21 sessions/7 days, 1 organic click from Bing, 0 from Google).
    This is a hand-transcribed snapshot, not a live feed, and goes stale
    the same way any hand-transcribed number does.
impact: >
  Traffic now has one real, dated data point instead of none, so "every
  growth claim is unfalsifiable" no longer fully holds. There is still no
  live feed an operator session can pull itself, so every number between
  hand-pulls carries a growing, unstated age, and EXPERIMENTS.md's designed
  experiments (EXP-001, EXP-002) are still unreadable from this sandbox.
mitigation: >
  The privacy-vs-measurement policy conflict this risk was originally about
  is resolved (self-hosted, no third party, matches the privacy page as
  written). What remains is an access problem, not a policy one: get 1.2
  (share URL or API key) into a place an operator session can reach.
closing_condition: >
  An operator session can fetch real visitor and conversion numbers without
  a browser login or Phil re-transcribing them by hand.
review: before any growth or SEO work is prioritized on predicted impact
```

Every traffic or conversion figure older than its last hand-pull date should still be treated as unverified.

---

# 14. RISK-0006 Safety And Legal Front Matter Is New And Unreviewed

```yaml
id: RISK-0006
title: Safety and legal front matter is new and unreviewed
status: CLOSED
severity: HIGH
likelihood: POSSIBLE
owner: 6s-ceo
evidence:
  - GitHub issue #3, closed 2026-08-25 by Phil directly ("completed"): all
    bracketed front-matter fields (13 canonical answers behind 63
    occurrences across seven files) are filled, enforced by
    ops/front-matter.json and a preflight gate (gate_front_matter_filled)
    that fails if any field regresses to a bracketed placeholder
  - Phil's own closing comment on issue #3: no ISBN was bought and none is
    needed, because a direct digital sale through Stripe does not require
    one; the eBook, Micro Zone Manual and Complete Digital Bundle have been
    taking real money since 2026-08-21 without one, and one of them has
    actually sold and delivered
  - counsel review of the Important Notice section and the "6S" trademark
    position was explicitly deferred by Phil, not skipped: "if the book
    ever goes to a retail channel that does [need an ISBN], that is a new
    issue with a real trigger rather than a standing blocker on a product
    that is already selling"
  - site/disclaimer.html and all 50 chapters carry the safety notice
    (ops/state.json chapters_with_disclaimer=50 of 50)
impact: >
  Resolved for the channel actually in use (direct digital sale): the
  original risk, selling with unfilled legal fields, cannot occur. The
  narrower question Phil's own closing note leaves open, counsel review
  before a retail or ISBN-bearing channel, is a new, smaller, explicitly
  deferred item, not a standing blocker on anything selling today.
mitigation: >
  Closed for direct digital sale. Re-open, narrowly, before any retail or
  ISBN-bearing distribution channel is pursued, per Phil's own stated
  condition on issue #3.
closing_condition: >
  Met, 2026-08-25. Re-opens only on a real trigger: a retail or
  ISBN-bearing distribution channel being pursued.
review: before any retail or ISBN-bearing distribution
```

This register does not state what any jurisdiction requires. That determination needs a qualified professional, and Phil's own decision above defers it until the trigger that would make it necessary.

---

# 15. RISK-0007 Single Host, No Staging, Unproven Restore

```yaml
id: RISK-0007
title: Single host, no staging, unproven restore
status: OPEN
severity: CRITICAL
likelihood: POSSIBLE
owner: devops-sre
evidence:
  - docker-compose.yml and docker-compose.proxy.yml define one web container
  - no staging service, host, or environment is defined in either file
  - no restore has been executed and verified; DISASTER-RECOVERY.md is policy,
    not proof
impact: >
  A bad build replaces production directly with no intermediate surface to
  verify on. Loss of the single Hostinger VPS removes the entire public
  presence, and recovery depends on RISK-0002 being fixed first. Whether the
  site can actually be restored is UNKNOWN, because it has never been done.
mitigation: >
  Fix RISK-0002. Then perform one full rebuild from the repository onto a
  clean target and time it. Record the measured recovery time in
  DISASTER-RECOVERY.md, replacing any assumed objective.
closing_condition: >
  A restore has been executed end to end at least once and the measured
  recovery time is recorded.
review: quarterly, and after any infrastructure change
```

The one genuinely reassuring fact: the site is static. There is no database to lose, and the only persistent volume is the Let's Encrypt certificate store, which regenerates.

**Tracked 2026-09-03.** RISK-0002 is closed, so this risk's own mitigation
(one timed, end to end rebuild onto a clean target) is now the actual next
step. It had never been named on any working list, only in this register;
now filed as `BACKLOG-2026-H2.md` 6.55, waiting on a session that holds the
VPS deploy key, which this sandbox does not.

---

# 16. RISK-0008 Nine Product Lines, None Purchasable

```yaml
id: RISK-0008
title: Nine product lines, none purchasable
status: CLOSED
severity: HIGH
likelihood: OCCURRING
owner: 6s-ceo
evidence:
  - EXECUTIVE-DASHBOARD-LIVE.md, regenerated 2026-09-03: "The site can take
    money for 158 of 159 catalog items, each a live Stripe Payment Link or
    a real free download. Still not buyable: Corporate Lean 6S," which is
    quote-per-engagement by design (BACKLOG-2026-H2.md 5.5), not a defect
  - ops/state.json (2026-09-03): catalog_total=159, can_take_payment=true
  - a real transaction completed and delivered 2026-08-21; a real
    three-day outage where every live link went dead was found and fixed
    2026-08-30, and is now gated (ops/check_live_links.py)
impact: >
  Resolved. This entry's own claim, "effort is spread across nine lines
  while zero of them can be bought," is no longer true of any line except
  the one deliberately quote-only. The live risk is no longer "can it be
  bought" but "does anyone who was not told about it by Phil ever buy it,"
  which is RISK-0013.
mitigation: >
  Closed. Do not open a tenth product line ahead of evidence that the
  existing 159 convert a stranger, per ROADMAP-2026-2029.md's own refusal
  list ("no new digital tier until there is new content").
closing_condition: >
  Met. 158 of 159 catalog items purchasable, reconfirmed by
  ops/audit_catalog.py and ops/check_sellable.py on every preflight run.
review: monthly, alongside RISK-0013
```

---

# 17. RISK-0009 Control Documents Contradict The Published Canon

```yaml
id: RISK-0009
title: Control documents contradict the published canon
status: MITIGATING
severity: LOW
likelihood: UNLIKELY
owner: content-editor
evidence:
  - 2026-08-17: `ops/fix_dashes.py` swept the control layer; re-run 2026-08-19
    confirms it is still clean: "control layer is clean: 0 em dashes, 0 en
    dashes". The dash half of this risk is closed.
  - 2026-08-19: every "Set in Order" occurrence outside content/book/6s-success-
    claude-files/ (169 lines across 72 files) was read and classified before
    touching any of it, per the mitigation below. 14 real violations were
    found and fixed, all presenting "Set in Order" as this project's own term
    rather than quoting or rejecting it: CLAUDE.md itself (Section 4's own
    activity list), BUSINESS.md, CHANGELOG.md, AUTONOMY-ORCHESTRATION.md,
    CUSTOMER-JOURNEY.md, INCIDENTS.md, PRODUCT-CATALOG.md, ROADMAP.md,
    claude/agents/product-manager.md, three files under `super prompts/`, one
    social posting plan (content/book/Kaizen_Book_Posting_Plan.md), and one
    deck planning document (content/decks/6S_Success_Home_Quest_Updated_Room_
    Dec.html). All fixed to "Straighten".
  - Nine of those same violations also carried a second canon defect riding
    along in the same list or section sequence: Safety placed sixth instead
    of fourth (the plain 5S order with Safety appended, rather than this
    project's six-step order). Fixed alongside the term in the same edit,
    since both defects sat in the same lines and leaving one while fixing the
    other would have left a known error uncorrected.
  - The remaining ~130 occurrences were confirmed as deliberate: rule-
    statements telling agents or image generators to reject the term
    (CONTENT-STANDARDS.md, LOOP.md, ops/routine-prompt.md, the game and card
    illustration briefs), scanning code that searches for the term
    (ops/dashboard.py, ops/build_epub.py, ops/build_manual_print.py), audit
    trail documenting defects found and fixed in generated card art and book
    figures (content/decks/reviews/, the chapter *_IMAGE_FINALIZATION_NOTES.md
    files, content/book/6S projects files/), or a quoted acknowledgment that
    other books use different translations of the same Japanese term (the
    "small confession about those English words" passage in Chapter 2,
    which appears in the manuscript, the shipped chapter HTML, and the
    site's sample download, and is deliberate, not a violation).
  - content/book/6s-success-claude-files/ was confirmed a stale, untouched
    mirror of the control layer (diff against the real CLAUDE.md shows only
    the pre-fix text; nothing in it is newer than the real files), so it is
    the separate finding this risk anticipated, not swept in this pass.
  - `_review/agent-drafts/` still contains "Set in Order" in draft copies of
    CONTENT-STANDARDS.md and RISKS.md, but reconciling drafts against the
    real control documents is issue #9, a decision issue, so left untouched.
  - ops/dashboard.py still measures the term only in the live site and book,
    not the control layer, so a future regression here would not show on the
    dashboard.
impact: >
  Both halves of the original defect (the dashes and the term) are now fixed
  and verified in the active control layer, the shipped book, the decks, and
  the games. What remains is a stale, inactive duplicate directory and a set
  of drafts already gated behind a separate decision issue, neither of which
  an agent would read as live instruction.
mitigation: >
  Closed for the active control layer. Two items remain, both already
  tracked elsewhere: reconcile or retire content/book/6s-success-claude-
  files/ (a new, smaller finding), and resolve issue #9, which covers
  `_review/agent-drafts/`. Extending ops/dashboard.py's scan to the control
  layer would catch a future regression sooner than the next manual triage.
closing_condition: >
  Zero em and en dashes (met). Every remaining "Set in Order" occurrence
  outside the stale mirror and the gated drafts fixed or confirmed as a
  deliberate rule-statement (met 2026-08-19). Fully closes once the stale
  mirror is reconciled or retired and the dashboard scan covers the control
  layer.
review: monthly
```

See `CONTENT-STANDARDS.md` section 4 for the canon this violates.

---

# 18. RISK-0010 No Automated Quality Gate Before Production

```yaml
id: RISK-0010
title: No automated quality gate before production
status: CLOSED
severity: MEDIUM
likelihood: LIKELY
owner: github-manager
evidence:
  - .github/workflows/checks.yml exists, triggers on push and pull_request,
    and runs ops/preflight.py (its 60-plus gates, including the em/en dash
    and canon-term checks this risk named) and ops/audit_catalog.py
  - seven further workflows exist (publish-image.yml, fulfil-orders.yml,
    hourly-brief.yml, linkedin-drafts.yml, publish-mcp.yml,
    roadmap-report.yml, status-email.yml); last 15 runs green, reconfirmed
    2026-09-03
impact: >
  Resolved. A broken link, a stray em dash, or a reintroduced canon defect
  now has an automated point that runs on every push, not only an agent's
  memory.
mitigation: >
  Closed. Keep ops/preflight.py as the one gate new checks are added to,
  rather than a second parallel workflow, per this project's own
  established convention (ops/NIGHTLY-LOG.md).
closing_condition: >
  Met. A workflow runs on every push and pull request; preflight.py fails
  the run on a real defect, proved repeatedly by planting and reverting
  regressions in isolated worktrees (ops/NIGHTLY-LOG.md, epic 6).
review: monthly
```

---

# 19. RISK-0011 Product Masters Live Outside The Repository

```yaml
id: RISK-0011
title: Product masters live outside the repository
status: OPEN
severity: CRITICAL
likelihood: POSSIBLE
owner: 6s-ceo
evidence:
  - ops/dashboard.py reads product state from a Desktop path on one Windows
    machine, outside this repository
  - .gitignore deliberately excludes content image, PDF, font, and archive
    masters, noted there as roughly 1.74 GB
impact: >
  The images, PDFs, and source masters behind every product are held in one
  place, on one machine, and are not in version control. Their backup state is
  UNKNOWN. Loss of that machine could lose work that no amount of engineering
  recreates.
mitigation: >
  Establish where those masters are backed up and verify one restore. If
  nothing backs them up, that is the finding, and it should become a P0
  backlog item. Git LFS or an object store are options, and the choice belongs
  in DECISIONS.md.
closing_condition: >
  A verified second copy of the masters exists and a file has been restored
  from it successfully.
review: monthly
```

The exact size, location, and current backup state of the masters is UNKNOWN. Listing the master directories and checking for any existing backup target would establish it.

**Escalated 2026-09-03.** This had been open since the register was written
with no mitigation in flight anywhere, the exact gap section 23's own
escalation rule exists to catch; checked directly against `OWNER-ACTIONS.md`
and `BACKLOG-2026-H2.md`, neither had it. Now filed as `OWNER-ACTIONS.md`
item 13, a single question for Phil (where is this backed up, and if
nowhere, pick one of a few cheap options).

---

# 20. RISK-0012 No Audience Is Being Retained

```yaml
id: RISK-0012
title: No audience is being retained
status: OPEN
severity: HIGH
likelihood: OCCURRING
owner: cro-growth
evidence:
  - ops/state.json email_list=0
  - every form on the site is inert (forms_dead=190)
  - ops/state.json social_units=4408 authored and unused
impact: >
  Nothing compounds. A visitor who arrives today cannot be reached tomorrow,
  so every unit of attention is spent once and discarded. Roughly 4,408
  authored social units have no destination to send anyone to.
mitigation: >
  Connect one capture path and one destination before publishing the social
  corpus. Capture without a payment path is still worth more than neither,
  because it preserves optionality.
closing_condition: >
  A form submission is received, stored, and retrievable, and the list has a
  non zero verified count.
review: every operating cycle
```

**Evidence corrected 2026-09-04.** `forms_dead` and `social_units` were still
the values from whenever this entry was written (14 and 2,600), against a
live `ops/state.json` of 188 and 4,408: the catalogue and social corpus both
grew since, neither number reflects a change in whether the underlying
problem is fixed (it is not: `email_list` is still 0). Same drift shape
`gate_goals_traffic_current` already catches for `GOALS.md`, just not
previously checked here; new `gate_risks_evidence_current` in
`preflight.py` now checks every `key=value` evidence line in this file
against `ops/state.json` directly, not just these two.

---

# 20b. RISK-0013 No Stranger Has Ever Converted; Discovery Is The Constraint

```yaml
id: RISK-0013
title: No stranger has ever converted; discovery is the constraint
status: OPEN
severity: CRITICAL
likelihood: OCCURRING
owner: cro-growth
evidence:
  - ROADMAP-2026-2029.md section 2: "The one buyer was a personal referral
    from Phil. This business has never converted a stranger. The funnel is
    entirely unvalidated. Nova Consulting has no list, so there is no
    audience to borrow and no shortcut on traffic."
  - EXECUTIVE-DASHBOARD-LIVE.md, regenerated 2026-09-03: "The widened
    catalog has not moved revenue because almost nobody is arriving at the
    site yet. Discovery, not what can be bought, is the constraint now."
  - GOALS.md baseline, hand-pulled by Phil 2026-09-02, corrected 2026-09-03:
    52 visitors/144 visits/30 days, 21 sessions/7 days, 1 organic click from
    Bing, 0 from Google; a live feed is still blocked on BACKLOG-2026-H2.md
    item 1.2 (see RISK-0005)
  - ops/state.json (2026-09-03): email_list=0, so there is also no list to
    fall back on while search compounds
impact: >
  Every product, pricing, and conversion improvement built so far is
  guesswork against this until it closes, per ROADMAP-2026-2029.md's own
  ordering rule (epic 4, conversion, waits on epic 1, measurement). The
  catalog (RISK-0008, closed), the Quest, and the payment route (RISK-0001,
  closed) are all built; none of it has yet been tested against a real
  stranger's decision to buy.
mitigation: >
  Per ROADMAP-2026-2029.md: get automated traffic measurement flowing
  (BACKLOG-2026-H2.md 1.2), let real Search Console and scroll-depth data
  accumulate (1.4, 1.5), and run the capped local demand test for the
  service SKUs (epic 3B) once Phil approves a budget, since that route does
  not require organic search to compound first.
closing_condition: >
  A stranger, not a personal referral, completes a purchase; or
  ROADMAP-2026-2029.md's own G1 gate resolves (fewer than 500 organic
  visits a month and no stranger has bought anything, by August 2027,
  which re-baselines the target instead).
review: every operating cycle, this register's own most consequential entry
```

This is the risk RISK-0001 named until 2026-08-21, and stopped naming once
the payment route was built and used, without this register noticing for
two more weeks. This register's own Final Principle (section 24) asks
whether the cause of failure, if this business fails, is already written
here. As of this review, the honest answer points to this entry, not
RISK-0001.

---

# 21. Risks Deliberately Not Recorded

The following were considered and are not in the register, because no evidence in this repository establishes them:

- competitor activity, because no market research exists here
- seasonality of demand, because no demand data exists
- vendor pricing changes, because no vendor is contracted
- customer churn, because there are no customers
- capacity or scaling limits, because traffic is UNKNOWN

If evidence appears, add them. Do not add them speculatively.

---

# 22. Review Cadence

| Trigger | Action |
|---|---|
| Every operating cycle | Re-read whichever entries are currently `CRITICAL` in section 8's table, not a remembered count |
| Any incident | Check whether it was a listed risk; if not, add it |
| Any deploy | Re-check RISK-0002 and RISK-0007 |
| Any sale or distribution | Re-check RISK-0003, RISK-0004 |
| Monthly | Full register review, close what is verifiably closed |

A risk is closed only by evidence, never by elapsed time and never by the belief that it has probably been handled.

---

# 23. Escalation

Escalate to the owner when:

- a `CRITICAL` risk has no mitigation in flight
- closing a risk requires a RED decision under `AUTONOMY.md`
- a risk requires professional review, for example legal, tax, or insurance
- two risks conflict, as RISK-0005 conflicts with the public privacy promise

Present the evidence, the options, and the recommendation. Do not present a list of tasks for the owner to perform.

---

# 24. Final Principle

The purpose of this register is not to catalog anxiety.

It is to make sure that the autonomous system never optimizes something comfortable while an unaddressed `CRITICAL` risk sits underneath it.

The test:

**If this business failed in the next 90 days, would the cause already be written here?**

Today the answer is yes, and the most likely cause is RISK-0013: no stranger
has ever converted, and discovery is the constraint. It was RISK-0001 until
2026-08-21, when a real transaction made that claim false; this register
kept naming it anyway until this review, which is its own cautionary
example, not just this section's.

Keep it that way. A register that would have missed the cause is a register
that was not being maintained. Update this paragraph, by name, whenever
section 8's `CRITICAL`-and-`OPEN` list changes what it would name first.
