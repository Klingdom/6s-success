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

Last reviewed: 2026-08-17.

Twelve risks are open. Four are `CRITICAL`. None have been formally accepted by the owner, so none are `ACCEPTED` yet.

| ID | Title | Severity | Status |
|---|---|---|---|
| RISK-0001 | No route from customer intent to payment | CRITICAL | OPEN |
| RISK-0002 | The VPS cannot pull the now private repository | CRITICAL | OPEN |
| RISK-0003 | Card art carries third party trademarks | HIGH | OPEN |
| RISK-0004 | The downloadable book is 30 of 50 chapters | HIGH | OPEN |
| RISK-0005 | Nothing about customer behavior is measurable | HIGH | OPEN |
| RISK-0006 | Safety and legal front matter is new and unreviewed | HIGH | OPEN |
| RISK-0007 | Single host, no staging, unproven restore | CRITICAL | OPEN |
| RISK-0008 | Nine product lines, none purchasable | HIGH | OPEN |
| RISK-0009 | Control documents contradict the published canon | MEDIUM | OPEN |
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
status: OPEN
severity: CRITICAL
likelihood: LIKELY
owner: vps-docker-manager
evidence:
  - DEPLOY.md header, "The repository is now PRIVATE", added 2026-08-16
  - GitHub issue #10, labelled P0
impact: >
  The currently running container is unaffected, so this is invisible until the
  moment it matters. The next deploy, the next rollback, and any rebuild after
  host loss will all fail with an authentication error. It converts an ordinary
  recovery into an outage of UNKNOWN length.
mitigation: >
  Configure either a deploy key on the VPS registered at the repository's
  Deploy Keys settings, or a fine grained read only Contents token used in the
  HTTPS clone URL. Then prove it by running a pull that is expected to succeed.
closing_condition: >
  A git pull executed on the VPS succeeds, and the result is recorded in
  DISASTER-RECOVERY.md as verified.
review: before any deploy
```

Note the recovery coupling. `DISASTER-RECOVERY.md` assumes the repository is reachable. Until this is fixed, that assumption is false.

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
status: OPEN
severity: HIGH
likelihood: OCCURRING
owner: content-editor
evidence:
  - site/downloads/6S Success Home Edition - Complete Book.html ends at Chapter 30
  - the manuscript is complete at 50 chapters (ops/state.json chapters=50)
impact: >
  The file offered as the complete book is 60 percent of the book. If it is
  ever sold in this state, the first customer experience is a shortfall against
  an explicit promise, which is the most expensive kind of trust failure to
  repair. The 53 MB PDF beside it needs the same check.
mitigation: >
  Rebuild both download artifacts from the 50 chapter master, verify the last
  chapter present in each file, and only then describe either as complete.
closing_condition: >
  Both download artifacts contain Chapter 50, verified by inspecting the file.
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
status: OPEN
severity: MEDIUM
likelihood: OCCURRING
owner: content-editor
evidence:
  - the rejected term "Set in Order" appears 13 times across 10 control
    documents and agent definitions, including CLAUDE.md, BUSINESS.md,
    PRODUCT-CATALOG.md, CUSTOMER-JOURNEY.md, AUTONOMY-ORCHESTRATION.md, and
    claude/agents/product-manager.md
  - 45 control documents carry 457 em dashes and 42 en dashes, against a house
    rule of zero; the published site has 7, all in site/invest.html
  - ops/dashboard.py measures both defects only in the live site and book, so
    the dashboard reports zero while these remain
impact: >
  Agents read these documents as authority. A control layer that violates the
  house standard will keep pushing the violation back into published work, and
  the dashboard cannot see it happening. The published work is close to
  compliant while the documents instructing agents are not, which is the wrong
  way round.
mitigation: >
  Sweep the control documents and agent definitions, and extend
  ops/dashboard.py to scan root documents and agent definitions as well as
  published output. See CONTENT-STANDARDS.md section 11.
closing_condition: >
  Zero em and en dashes and zero occurrences of the rejected term outside a
  deliberate note, in both layers, and the dashboard scan covers the control
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
