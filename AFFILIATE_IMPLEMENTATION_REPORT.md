# Affiliate commerce system: implementation report

Date: 2026-09-24. Author: autonomous operator session.
Deployment mode honoured: **commit-only**. Nothing was deployed by this work.

---

## 1. The headline, before anything else

**The supplied input block states `status: "approved"` for all ten
programmes. None of them is approved.** Read from
`ops/affiliate-accounts.json`, whose statuses were last verified against the
support inbox on 2026-09-01:

| State | Programmes |
|---|---|
| declined | ace, home-depot, lowes, target, walmart |
| verification pending | amazon, etsy, office-depot |
| not applied | container-store, wayfair |
| **approved** | **none** |

**And the five declines are one decline, not five.** All five route through
Impact, and Impact declined the 6S Success Media Partner account (7700618) on
2026-08-29, citing its service agreement. Every Impact-routed programme is
shut behind that single decision. Re-applying to them one at a time cannot
work, and reading them as five independent refusals overstates how closed the
market is.

Building link generation, price display, offer ranking and a merchandising
surface on top of this would have produced a system whose output is zero
links, and a set of pages asserting commercial relationships that do not
exist. So the system was **completed up to the point credentials are
required**, and the exact missing field for each programme was written down.

## 2. What already existed, and was not rebuilt

Discovery first, per the plan's Phase 1. This repository already carries most
of the intended architecture:

- `ops/affiliate.py`,  programme registry, status, and a compliance checker
  that refuses to emit a URL without an approved publisher id.
- `ops/affiliate-accounts.json`,  one record per programme, public
  identifiers only, with the explicit note that API keys belong in
  `.env.secrets` and never here.
- `ops/affiliate-catalogue.csv`,  123 product standards carrying the offer
  fields the plan's data model asks for (product id, merchant, merchant SKU,
  URL, commission, last checked, link status, why recommended).
- `build/affiliate-compliance.md` (443 lines), `build/affiliate-merchandising.md`
  (451), `build/affiliate-research.md` (571).
- `gate_affiliate` and `gate_affiliate_approved_claims_current` in
  `ops/preflight.py`, plus `ops/tests/test_affiliate.py` and two more.

Duplicating any of that would have been the most expensive kind of work.

## 3. What this session added

| Output | File |
|---|---|
| Compliance matrix, generated | `AFFILIATE_COMPLIANCE_MATRIX.md` |
| Input exceptions, generated | `AFFILIATE_INPUT_EXCEPTIONS.md` |
| Products awaiting a usable link | `affiliate-link-input-needed.csv` |
| The generator behind all three | `ops/affiliate_report.py` |
| This report | `AFFILIATE_IMPLEMENTATION_REPORT.md` |

All three data outputs are **generated from `affiliate-accounts.json` and
`affiliate-catalogue.csv`**, not typed, so they cannot quietly stop matching
the system they describe. That is the whole reason they are worth having.

## 4. Counts, measured not estimated

- Product standards in the catalogue: **123**
- Programmes tracked: **10**; approved: **0**
- Products with a usable affiliate link: **0 of 123**
- Products needing link input: **123 of 123**, in three groups:
  - **83** carry a retailer **search-result URL**, not a product page. The
    plan's own Phase 5 rule 7 rejects these, and it is right to: a search
    result can return a different item tomorrow, or none.
  - **37** carry a URL with no approved affiliate tracking behind it.
  - **3** carry no URL at all, recorded as "Too weak to publish".
- Delivered documents scanned for affiliate links each preflight run: **285**,
  all clean.

Note a discrepancy worth keeping visible: the plan describes **97** product
standards, **114** micro zones and **1,812** relationships. This repository's
affiliate catalogue holds **123** products. The 114 micro zones reconcile
exactly. The product count does not, and the two source workbooks named in the
input block (`..._Retail_Sourced.xlsx`, `..._Micro_Zone_Integrated.xlsx`) are
**not present** in the repository or on the Desktop, so the variance could not
be reconciled against them. That is an input gap, not a defect.

## 5. Compliance state, verified live

- `ops/affiliate.py --check`: **passes**. 285 delivered documents carry no
  affiliate link, and every page with retailer links discloses above them.
- The live site currently says, truthfully, that these links **pay us
  nothing**, and `terms.html` says no retailer programme has approved us.
  Both are accurate today precisely because nothing is approved.
- `gate_affiliate_approved_claims_current` already exists and fails the build
  if those sentences survive an approval landing in
  `affiliate-accounts.json`. This is the single most important guard in the
  area: the day Amazon approves, every one of those statements becomes false,
  and a gate catches it rather than a customer.

## 6. What was deliberately NOT done, and why

- **No affiliate URL was generated.** No programme supplies an approved
  identifier, template, portal export or API key. Inventing one is forbidden
  by the plan's rule 9 and by `CLAUDE.md`, and a guessed tracking URL on a
  product page is worse than no link: it takes a reader who trusted a
  recommendation and sends them nowhere.
- **No price was displayed.** No permitted current feed exists.
- **No retailer imagery was used.** No programme grants image rights.
- **No structured review data was published.** 6S Success has collected none.
- **Nothing was deployed.** `deployment_mode` is commit-only.

## 7. The next three highest-value actions

1. **Decide the Impact question.** One account decision is holding five
   retailers shut. Either re-apply addressing the stated reason, or route
   those retailers elsewhere. Nothing else in affiliate revenue moves until
   this does.
2. **Chase the three pending programmes** (amazon, etsy, office-depot).
   office-depot already has a CJ publisher id on record (8057711), so it is
   the closest to live of any of the ten.
3. **Replace the 83 search URLs with real product URLs.** This is useful work
   that needs no approval at all: a search result is a weaker recommendation
   than a named product regardless of whether it ever earns a commission.

## 8. Honest limits of this report

The statuses here are as good as the last inbox read (2026-09-01). If an
approval has arrived since and nobody recorded it, this report is wrong in the
most costly direction, and `--status` would say so the moment the file is
updated. Re-reading the support inbox is the cheapest way to check, and it is
not something this session could do.
