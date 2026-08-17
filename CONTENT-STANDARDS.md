# 6S Success Content Standards

> The mechanical, checkable rules every 6S Success asset must satisfy: typography, terminology, six S canon, product naming, safety notices, evidence, and production standards for HTML. Written so a machine could enforce it.

## 1. Purpose

`CLAUDE.md` sections 9 and 10 define what good content is: useful, specific, concise, human, warm, easy to act on. That is the standard of judgment.

`CONTENT-STANDARDS.md` defines the standard of fact. Every rule here is a rule an agent can be wrong about without noticing, and every rule here can be checked by counting.

The two are not interchangeable. Voice is reviewed. These are verified.

Read with:

- `CLAUDE.md` sections 9, 10, 11, and 50
- `CONTENT-CATALOG.md` for what the rules apply to
- `PRODUCT-CATALOG.md` for the commercial model behind the product naming rule
- `LOOP.md`, which states the house style enforced by the nightly loop
- `TESTING.md`
- `RISKS.md`

If a referenced file does not exist yet, do not invent its contents.

---

# 2. Prime Content Rule

**A rule that cannot be checked will not hold across 50 chapters, 20 decks, and 114 episodes.**

Every rule below is stated so that its violations can be counted. Where a rule cannot be counted, it belongs in `CLAUDE.md` as guidance, not here as a standard.

---

# 3. Typography

## 3.1 No em dashes and no en dashes

Zero occurrences of U+2014 and U+2013 in any authored asset: manuscripts, HTML, Markdown, card copy, CSV, prompts, control documents.

Use a comma, a colon, a full stop, or a rewritten sentence. For numeric ranges write "1 to 30", not a dash.

This is not a stylistic preference to be relitigated per asset. It is a single global rule so that output from any agent, any session, and any tool is indistinguishable.

Check:

```bash
python -c "import glob;print(sum(open(f,encoding='utf-8',errors='replace').read().count(chr(0x2014))+open(f,encoding='utf-8',errors='replace').read().count(chr(0x2013)) for f in glob.glob('site/*.html')))"
```

## 3.2 Hyphens

Ordinary hyphens are fine. Compound modifiers follow normal usage.

## 3.3 Quotation marks and ellipses

Straight quotes in code, source, and data files. Typographic quotes are acceptable in finished prose HTML. Never use the single character ellipsis in data files, because it breaks CSV round trips.

---

# 4. The Six S Canon

The six S's, in order:

1. **Sort**
2. **Straighten**
3. **Shine**
4. **Safety**
5. **Standardize**
6. **Sustain**

Three rules follow from that list and are violated more often than any other rule in this document.

## 4.1 Straighten, never the rejected term

The second S is **Straighten**. The term "Set in Order" is rejected across all 6S Success material. It is not a synonym to be used for variety.

The only permitted use is a deliberate note explaining that the term is rejected.

## 4.2 Safety is the fourth S

Safety sits between Shine and Standardize. It is not an appendix, not a footnote, and not optional. `ops/dashboard.py` and the whole book review both check for its presence, because it is the S most often silently dropped when a chapter is copied from a previous chapter.

## 4.3 The order does not vary by room

A room playbook may weight the S's differently. It may not reorder or omit them.

Check:

```bash
grep -rn "Set in Order" --include="*.html" --include="*.md" .
```

---

# 5. Product Naming

Products are named by **type**, never by brand.

Correct: "Adjustable Wall Track System", "Fireproof Document Box", "Lidded Opaque Bin".

Incorrect: any manufacturer, retailer, model number, or store name.

Three reasons, in order of importance:

1. A type stays correct after a product is discontinued. A brand does not, and the book is meant to last.
2. A type describes the function the micro zone needs. A brand describes a purchase.
3. Brand naming in the book would create an affiliate relationship the book cannot honestly carry.

The 123 entries in `content/appendix/` are the canonical type vocabulary. Use them. Adding a new type is fine, inventing a brand is not.

The same rule governs card art: no third party marks, logos, or packaging. This is currently violated. See `RISK-0003`.

---

# 6. Safety Notices

Any asset that instructs a person to lift, climb, reach above shoulder height, use a chemical, handle a sharp object, or work near an electrical fitting must carry the safety notice.

Current state: all 50 book chapters carry it, and `site/disclaimer.html` was last updated 16 August 2026. Before that date, none of it did.

Rules:

- a new chapter, deck, episode, or app screen that instructs physical work carries the notice before it is marked `AUTHORED`
- the notice text is the same everywhere; do not paraphrase it per asset
- the notice is not a substitute for writing a safe instruction

This document does not state what any jurisdiction requires of a disclaimer. That question needs a qualified professional, and `RISK-0006` records that the review has not happened.

---

# 7. Evidence And Numbers

## 7.1 Never invent a number

No traffic figures, customer counts, revenue, conversion rates, review scores, testimonials, or time savings that are not measured.

This applies to marketing copy with the same force as to control documents. A number in a headline is a claim.

## 7.2 The UNKNOWN convention

Where a number is genuinely not known, write `UNKNOWN` and state what would establish it.

`UNKNOWN` is an acceptable answer. A plausible guess is not.

## 7.3 Attribute measured numbers

Any figure sourced from measurement cites where it came from, for example `ops/state.json` or a named GitHub issue. A number with no source is treated as invented.

## 7.4 No legal, tax, or jurisdiction specific claims

Do not state what the law, a tax authority, a platform, or a regulator requires. Where professional review is needed, say that it is needed and stop.

This is a hard boundary, not a hedge. Saying less is correct here.

---

# 8. Instructional Structure

The book's Part 9 room playbooks and the field manual share one instruction format:

- the unit of instruction is the **micro zone**, not the room
- each zone gets step by step clean and shine instructions with exact inputs
- inputs are product types with quantities, not shopping suggestions
- the Shine pass is governed by the nine rule Shine method
- the room chapter closes with a before and after signature

Rooms and zones must match `content/manual/source/content.json`. It is the arbiter. A chapter that invents a zone, renames one, or reorders them has drifted from the spine that every other product line shares.

Zone order departures are a known open item and should be resolved against the manual, not against the most recent chapter.

---

# 9. HTML Production Standards

Applies to every published HTML asset: chapters, manual, decks, site pages.

| Rule | Why |
|---|---|
| Self hosted fonts only | Zero external requests, which is also the privacy promise |
| No CDN, no remote scripts, no remote images | Same |
| A `meta name="description"` on every page | Currently satisfied: 14 of 14 site pages |
| Real bold via a font weight, never faux bold | Faux bold was a whole book defect, now fixed |
| Cross document navigation chain unbroken | The chapter chain used to dead end at 28 |
| Correct chapter title in every generated artifact | A copied builder once carried the previous chapter's title |

## 9.1 The builder rule

When a builder script is copied from a previous chapter or deck, **diff its literal strings, not just its variables.**

Three separate defect sweeps traced to exactly this: empty kick labels, stray triple quotes, and wrong chapter titles, each spanning six or seven chapters before anyone noticed. Every one of them was a hardcoded string that the variable rename did not touch.

---

# 10. What This Standard Does Not Cover

Deliberately out of scope, and owned elsewhere:

- voice, warmth, and reader respect, in `CLAUDE.md` section 10
- what content to make next, in `BACKLOG.md` and `ROADMAP.md`
- search and answer engine architecture, owned by the `seo-aeo` agent
- pricing and offer construction, in `PRODUCT-CATALOG.md`
- the inventory of what exists, in `CONTENT-CATALOG.md`

---

# 11. Current Compliance

Measured 2026-08-17. This section exists because a standard nobody has measured against is aspiration.

| Rule | Published assets | Control layer |
|---|---|---|
| Zero em and en dashes | `site/invest.html` has 7, all other pages clean | 45 files carry 457 em and 42 en dashes |
| Straighten, never the rejected term | 0 live uses in site and book | 13 occurrences across 10 files |
| Safety notice present | 50 of 50 chapters | Not applicable |
| Meta description present | 14 of 14 pages | Not applicable |
| Self hosted fonts | 22 woff2, zero external requests | Not applicable |

**The published work is close to compliant. The documents that instruct agents are not.**

That inversion is the finding. Agents read the control layer as authority, so a control layer that violates the standard will keep pushing the violation back into published work, and `ops/dashboard.py` cannot see it because it only scans the site and the book.

Two fixes, both small:

1. sweep the control documents and agent definitions
2. extend `ops/dashboard.py` to scan them, so the count appears on the dashboard

Recorded as `RISK-0009`.

---

# 12. Review Checklist

Before any asset moves from `DRAFT` to `AUTHORED`:

1. em and en dash count is zero
2. no occurrence of the rejected term
3. Safety appears as the fourth S
4. products named by type, no brands, no third party marks
5. safety notice present if the asset instructs physical work
6. every number is measured and attributed, or written `UNKNOWN`
7. no legal, tax, or jurisdiction specific claim
8. rooms and zones match the manual source
9. fonts self hosted, no external requests
10. meta description present
11. navigation links resolve

Items 1, 2, 5, 9, 10, and 11 are mechanically checkable and belong in the quality gate described in `RISK-0010`.

---

# 13. Final Principle

These rules exist because 6S Success is produced across many sessions, many agents, and many months, and consistency is the only thing that makes that output read as one work rather than fifty.

A reader will never notice that fifty chapters contain no em dashes.

They will absolutely notice the chapter where the dashes start, the S changes name, and a brand appears.

Consistency is invisible when it holds and glaring when it breaks. That asymmetry is why the standard is mechanical rather than tasteful.
