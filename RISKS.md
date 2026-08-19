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

Last reviewed: 2026-08-19.

Nine risks are open, one is mitigating, two are closed. Three open risks are `CRITICAL`. None have been formally accepted by the owner, so none are `ACCEPTED` yet.

| ID | Title | Severity | Status |
|---|---|---|---|
| RISK-0001 | No route from customer intent to payment | CRITICAL | OPEN |
| RISK-0002 | The VPS cannot pull the now private repository | CRITICAL | CLOSED |
| RISK-0003 | Card art carries third party trademarks | HIGH | OPEN |
| RISK-0004 | The downloadable book is 30 of 50 chapters | HIGH | CLOSED |
| RISK-0005 | Nothing about customer behavior is measurable | HIGH | OPEN |
| RISK-0006 | Safety and legal front matter is new and unreviewed | HIGH | OPEN |
| RISK-0007 | Single host, no staging, unproven restore | CRITICAL | OPEN |
| RISK-0008 | Nine product lines, none purchasable | HIGH | OPEN |
| RISK-0009 | Control documents contradict the published canon | MEDIUM | MITIGATING |
| RISK-0010 | No automated quality gate before production | MEDIUM | OPEN |
| RISK-0011 | Product masters live outside the repository | CRITICAL | OPEN |
| RISK-0012 | No audience is being retained | HIGH | OPEN |

---

# 9. RISK-0001 No Route From Customer Intent To Payment

```yaml
id: RISK-0001
title: No route from customer intent to payment
status: OPEN
severity: CRITICAL
likelihood: OCCURRING
owner: commerce-manager
evidence:
  - site/cart.html states "Secure checkout arrives in v2"
  - ops/state.json can_take_payment=false, revenue_month=0, paying_customers=0
  - ops/state.json forms_dead=14 (onsubmit="return false" across site/*.html)
impact: >
  Every visitor who wants to buy, book, or subscribe reaches a dead end and is
  lost with no record that they existed. Revenue is $0 and will remain $0
  regardless of traffic, content, or product quality.
mitigation: >
  Connect one payment path for one product before broadening anything else.
  See ROADMAP.md phase 1. Payment provider selection is a RED decision under
  AUTONOMY.md and must be recorded in DECISIONS.md.
closing_condition: >
  A real transaction completes end to end and is verified in the provider
  dashboard and in the fulfillment path.
review: every operating cycle until closed
```

This is the single constraint named on the live dashboard. No other risk in this register outranks it.

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
severity: HIGH
likelihood: OCCURRING
owner: analytics-intelligence
evidence:
  - site/privacy.html states no analytics, no advertising pixels, no third
    party trackers, no session recording
  - no analytics include exists in any file under site/
impact: >
  Traffic is UNKNOWN. Conversion is UNKNOWN. Which pages help is UNKNOWN.
  Every growth claim is unfalsifiable, every experiment defined in
  EXPERIMENTS.md is unrunnable, and the metric definitions in METRICS.md have
  no data behind them.
mitigation: >
  This is a genuine conflict, not an oversight. The privacy page is a public
  promise and quietly breaking it would be worse than the missing data. The
  resolution is a recorded decision in DECISIONS.md that either keeps the
  no tracking promise and accepts UNKNOWN demand, or adopts a measurement
  approach the privacy page can honestly describe, with the page updated in
  the same change.
closing_condition: >
  A DECISIONS.md entry exists, and either analytics are live and the privacy
  page matches, or the absence is formally accepted.
review: before any growth or SEO work is prioritized on predicted impact
```

Until this is resolved, treat every traffic or conversion figure in any document as unverified.

---

# 14. RISK-0006 Safety And Legal Front Matter Is New And Unreviewed

```yaml
id: RISK-0006
title: Safety and legal front matter is new and unreviewed
status: OPEN
severity: HIGH
likelihood: POSSIBLE
owner: 6s-ceo
evidence:
  - site/disclaimer.html, "Last updated 16 August 2026"; before that date no
    disclaimer existed
  - ops/state.json chapters_with_disclaimer=50 of 50, all added recently
  - GitHub issue #3, front matter bracketed fields unfilled, needs counsel
    review, P0
impact: >
  The book instructs people to lift, climb, use chemicals, and work near
  electrical fittings. Any copy that circulated before 2026-08-16 carries no
  notice at all, and the current front matter still contains placeholder
  fields.
mitigation: >
  Fill the bracketed fields, then obtain review by a qualified professional
  before commercial distribution. Identify and, where possible, replace any
  copies distributed before the notice existed.
closing_condition: >
  No bracketed placeholders remain, professional review is complete, and the
  distribution of pre notice copies is understood.
review: before any sale or wide distribution
```

This register does not state what any jurisdiction requires. That determination needs a qualified professional.

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

---

# 16. RISK-0008 Nine Product Lines, None Purchasable

```yaml
id: RISK-0008
title: Nine product lines, none purchasable
status: OPEN
severity: HIGH
likelihood: OCCURRING
owner: 6s-ceo
evidence:
  - CONTENT-CATALOG.md inventory: book, field manual, product appendix, card
    decks, board games, app, video, social corpus, website
  - ops/state.json: deck_rooms=2 of 20, video_shot=0 of 114, revenue_month=0
impact: >
  Effort is spread across nine lines while zero of them can be bought. Each
  additional line raises maintenance, canon, and safety review load without
  raising revenue, and delays the one thing that would.
mitigation: >
  Sequence by ROADMAP.md. Finish one purchasable product before starting a
  tenth line. Do not treat authored inventory as progress toward revenue.
closing_condition: >
  At least one product line is purchasable and the rest are explicitly
  sequenced or parked.
review: every operating cycle
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
status: OPEN
severity: MEDIUM
likelihood: LIKELY
owner: github-manager
evidence:
  - no .github directory exists, therefore no GitHub Actions workflows
  - TESTING.md and RELEASES.md define gates with no automated enforcement point
impact: >
  Every check described in policy depends on an agent remembering to run it.
  A broken link, a missing asset, a stray em dash, or a reintroduced canon
  defect can reach production unchallenged.
mitigation: >
  Add a minimal workflow that does what can be checked cheaply on a static
  site: build the image, check internal links, count em and en dashes, and
  scan for the rejected term.
closing_condition: >
  A workflow runs on every push and blocks a merge that fails those checks.
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
  - every form on the site is inert (forms_dead=14)
  - ops/state.json social_units=2600 authored and unused
impact: >
  Nothing compounds. A visitor who arrives today cannot be reached tomorrow,
  so every unit of attention is spent once and discarded. Roughly 2,600
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
| Every operating cycle | Re-read the four `CRITICAL` entries |
| Any incident | Check whether it was a listed risk; if not, add it |
| Any deploy | Re-check RISK-0002 and RISK-0007 |
| Any sale or distribution | Re-check RISK-0003, RISK-0004, RISK-0006 |
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

Today the answer is yes, and the most likely cause is RISK-0001.

Keep it that way. A register that would have missed the cause is a register that was not being maintained.
