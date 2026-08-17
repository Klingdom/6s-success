# The Micro Zone Manual, package

Companion volume to **6S Success: Home Edition**. Updated 2026-08-17, prepared for print.

20 rooms, 114 micro zones, 749 shine surfaces, 516 inspect points. Every zone carries a deepened **How to clean it** block. The package ships with two product appendices and a 7 x 10 in print edition.

## Contents

| File | What it is |
|---|---|
| `6S Home Micro Zone SOP Field Manual v3.html` | The manual. Screen and print in one file: the print stylesheet is inside `@page` and `@media print`, so on screen it renders exactly as it always did. |
| `micro-zone-manual-publishable.html` | Byte-identical copy under the publishable-HTML naming convention. |
| `print/6S-Micro-Zone-Manual-PRINT-7x10.html` | **The vendor file.** Manual plus both appendices bound in, typefaces embedded as data URIs, zero external requests. This is what goes to the printer. |
| `appendices/Appendix A - The Complete 6S Home Kit.html` | Every product type used to 6S a home, by family, with per-zone usage. |
| `appendices/Appendix B - Inputs and Sourcing List.html` | The same types as a procurement sheet, with blank Partner-link and Own-label-SKU columns. |
| `appendices/Appendix B - Inputs and Sourcing List.csv` | Appendix B as a spreadsheet, for procurement and affiliate management. |
| `MICROZONE_MANUAL_V3_BRIEF.md` | The frozen brief: canon, voice, banned vocabulary, the zone card, the validation gates. |
| `review/validation-report.txt` | Gate output from the v3 content build. |
| `source/` | Everything needed to rebuild the manual and appendices from scratch. |

There is no `linkedin/`, `x/` or `slides/` sub-package. Those are chapter deliverables; the manual is a standalone companion volume and no social cut was produced for it. The folders are absent rather than empty on purpose.

## House style, enforced mechanically

- **Zero em dashes and zero en dashes.** Session times read `30-45 min` with a hyphen. The frozen brief allowed an en dash inside a number range; the house rule since supersedes it, and the ranges were converted.
- **Straighten**, never the industrial alternative name. **Safety is the fourth S**, in every list, every time.
- **Product types, never brands.** No retailer and no manufacturer is named anywhere in the manual or in either appendix. A brand-dense variant of this manual was quarantined for exactly this, so the gate checks by name.

## Print production

Run `python ops/build_manual_print.py` from the repository root. It is idempotent: every injected region is fenced with sentinel comments and cleared before rebuild, so three runs give three identical files.

**Trim: 7 x 10 in (178 x 254 mm), portrait, perfect bound, one colour.**
Margins: inside 0.875 in, outside 0.625 in, head 0.7 in, foot 0.75 in, giving a 5.5 x 8.55 in text block.

Extent, measured by rendering rather than estimated:

| | Pages |
|---|---|
| Before: US Letter, no print stylesheet | 365 |
| Manual alone at 7 x 10 | 179 |
| **Print edition, manual plus both appendices, at 7 x 10** | **189** |

Same content at other trims, for comparison: 5.5 x 8.5 gives 254 pages, 6 x 9 gives 225, 8.5 x 11 gives 178.

The stylesheet is written as real CSS paged media. Folios, running heads, roman front matter and contents leaders use margin boxes and `target-counter`, which Prince, Antenna House and WeasyPrint honour. Chromium does not implement margin boxes, so a browser render gives the correct page count but no folios. **Do not send a browser PDF to the printer.**

Ink is one colour with no fills anywhere: every panel, chip and table header is a rule or an outline, so nothing depends on the printer honouring a background tint.

`python ops/build_manual_print.py --measure` re-renders and re-counts the pages. It writes its throwaway PDFs to a system temp directory, not into the repository.

## The deepened Shine pass

Every one of the 114 zones has a **How to clean it** block beneath the six passes:

- A Shine summary, then a **surface-by-surface table**, 749 surfaces in all, 5 to 8 per zone, giving a concrete method for each surface, worked top to bottom and back to front.
- **What you clean with**, the types for that zone, drawn from the product library.
- **Inspect as you clean**, 2 to 5 things to *notice and flag* per zone, 516 in all: leaks, wear, frayed cords, mildew, loose fixings, rust, cracks.

The Shine-versus-Safety line is deliberate. Inspection points **flag** problems, which is the clean-to-inspect principle from Chapter 16, while **fixing** stays in the separate Safety pass. A gate enforces that the inspect points do not instruct a fix.

## The two appendices

Both are built at print time from `source/products.json` (123 product types) and `source/zone_products.json` (1,867 zone-to-type links across 114 zones). They were previously built from a 97-type library and were 26 types behind.

- **Appendix A, The Complete 6S Home Kit.** Every cleaning supply, tool, sort container, storage type, visual control and safety item, grouped by family, each with its purpose, its 6S step, standard quantity, retail range, applicable rooms, and how many of the 114 zones call for it.
- **Appendix B, Inputs and Sourcing List.** The same types as a procurement table, plus two deliberately blank columns, **Partner link** and **Own-label SKU**, to fill as the product line is built. Also emitted as CSV.

Gaps are flagged rather than hidden:

- **Decor** is still absent from the library.
- **Six types are in the kit but mapped to no zone**: MPL-00011, 00028, 00087, 00088, 00089, 00094. Map them or retire them.
- **The `_zone_count` field in `products.json` is stale for ten records**, all cleaning tools added after the count was frozen. The appendices recompute usage from the zone map at build time and do not trust it.
- **The twelve types in Visual Controls and Safety carry a descriptive phrase in the category field** where every other family carries a category label. It is a source-data defect, left visible.
- **Sixteen of the twenty Shine-implied inputs have since been added to the catalog.** Four are still open. Appendix A tracks which.

## How it differs from v2

v2 has not been retired, so the two can be compared.

1. **Design system.** v2 used navy and Avenir. v3 uses the book's system: Fraunces and Newsreader, paper `#F7F2E9`, terracotta `#BC4B2A`.
2. **Dashes.** v2 had 834 em dashes. v3 is at zero em dashes and zero en dashes.
3. **Voice.** v2 read as a factory manual, with "workcell", "production capacity" and "fire lane". v3 is the book's plain, warm register.
4. **Content.** v2's advertised "684 6S activities" were six template sentences string-substituted across 114 zones. Every zone in v3 is written specifically, and a gate fails the build if any sentence repeats across zones.
5. **Time.** v2's per-step minutes and its whole-house total were invented. v3 uses ranges only.

v2 did state the six-S canon correctly, with Safety as the fourth S. That carried forward, and a gate now enforces it.

## Rebuilding the content

Run from `source/`, in order. Steps 1 and 2 only need re-running if the zone inventory or the prose changes.

1. `extract.py`, reads the v2 HTML and writes `zones-v2-inventory.json`
2. *(workflow)*, 20 room agents draft, 20 refine, results land in `content.json`
3. `collect.py`, pulls the refine-stage results into `content.json`
4. `build.py`, assembles the HTML in the book design system
5. `validate.py`, runs the content gates and exits non-zero on any failure
6. `ops/build_manual_print.py`, applies house style, rebuilds the appendices, injects front matter and the print stylesheet, and writes the vendor file

`content.json` is the editable source of truth for the prose. To fix wording, edit it and re-run steps 4 to 6; there is no need to re-run the agents.

`build.py` and `build_appendices.py` still carry absolute paths from the session that produced them, and `build_appendices.py` is superseded by the appendix builder inside `ops/build_manual_print.py`. Fix the paths before re-running either.

## Known caveats

- **The copyright page and the safety notice have not been reviewed by a lawyer.** They are plain-English scaffolding adapted from `content/book/6S-Success-Front-Matter/`. Every bracketed field must be filled and the whole notice must go to counsel before any commercial release, in every territory of sale.
- Page counts were produced by rendering with headless Microsoft Edge and counting `/Type /Page` objects. They are real pagination, but the final extent must be confirmed from the vendor's own PDF, which will differ slightly because it will carry folios and honour the recto rules the browser only approximates.
- The four frozen canon lines from the brief are quoted verbatim across the manual, 11 times in total. This is intended, and the repeated-sentence gate whitelists them.
- The manual carries no images at all, so it has no art dependency and nothing is waiting on illustration.
