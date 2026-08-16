# The Micro Zone Manual — Package

Companion volume to **6S Success: Home Edition**. Review copy, updated 2026-07-22.

20 rooms · 114 micro zones. Each zone now carries a deepened **How to clean it** block, and the package ships with two product appendices.

## Contents

| File | What it is |
|---|---|
| `micro-zone-manual-publishable.html` | The publishable HTML (matches the per-chapter `chapter-NN-publishable.html` convention) |
| `6S Home Micro Zone SOP Field Manual v3.html` | Same file under its Master-folder name |
| `6S Home Micro Zone SOP Field Manual v3.pdf` | Rendered from the HTML |
| `appendices/Appendix A - The Complete 6S Home Kit.html` | Every product used to 6S the house, by category, with per-zone usage |
| `appendices/Appendix B - Inputs and Sourcing List.html` | The same inputs as a procurement sheet, with blank Partner-link and Own-label SKU columns |
| `appendices/Appendix B - Inputs and Sourcing List.csv` | Appendix B as a spreadsheet, for procurement and affiliate management |
| `MICROZONE_MANUAL_V3_BRIEF.md` | The frozen brief: canon, voice, banned vocabulary, the zone card, the validation gates |
| `review/validation-report.txt` | Full gate output, all passing |
| `source/` | Everything needed to rebuild the manual and appendices from scratch |

This package has no `linkedin/`, `x/`, `slides/` or other social sub-packages. Those are chapter deliverables; the manual is a standalone companion volume and no social cut was produced for it. The folders are absent rather than empty on purpose.

## The deepened Shine pass (2026-07-22 update)

Every one of the 114 zones now has a **How to clean it** block beneath the six passes:

- A punchy Shine summary, then a **surface-by-surface table** (749 surfaces in all, 5 to 8 per zone) giving a concrete method for each surface and area, worked top to bottom and back to front.
- **What you clean with** — the products and tools for the zone, drawn from the product library.
- **Inspect as you clean** — 2 to 5 things to *notice and flag* per zone (516 in all): leaks, wear, frayed cords, mildew, loose fixings, rust, cracks.

The Shine-versus-Safety line is preserved deliberately: the inspection points **flag** problems (the clean-to-inspect principle from Chapter 16), while **fixing** stays in the separate Safety pass. A validation gate enforces that the inspect points do not instruct a fix.

**A useful by-product:** deepening Shine surfaced 20 cleaning inputs the product library does not yet carry or map (detail brushes, a plastic scraper, mildew remover, a mesh wash bag, a bowl brush, and so on). They are listed in Appendix A under **Shine-Implied Inputs**, tagged either "in library, map to more zones" or "new, add to catalog," so the appendix doubles as a to-do list for growing the library. This confirms the catalog's cleaning coverage (9 items) is its thinnest area.

## The two appendices

Both are built from `6S_Success_Master_Product_Library_v2_Micro_Zone_Integrated.xlsx` (97 product standards, an 1,813-row zone-to-product map).

- **Appendix A — The Complete 6S Home Kit.** The reference: every cleaning supply, tool, storage, organization, and visual-control standard, grouped by family, each with its purpose, 6S phase, standard quantity, applicable rooms, and how many of the 114 zones use it. Live filter and family jump-nav. Flagged gap sections for **Decor** (requested but not yet in the library) and the **Shine-Implied Inputs**.
- **Appendix B — Inputs & Sourcing List.** The same inputs as a procurement table: purpose, phase, quantity, estimated retail low/mid/high, safety notes, plus two blank columns, **Partner link** and **Own-label SKU**, ready to fill as the product line is built. Also emitted as CSV.

Gaps are flagged rather than hidden, per request: Decor has no items yet, and cleaning coverage is thin.

## How it differs from v2

v2 remains in the Master folder and has **not** been retired, so the two can be compared.

1. **Design system.** v2 used navy and Avenir. v3 uses the book's system: Fraunces / Newsreader, paper `#F7F2E9`, terracotta `#BC4B2A`.
2. **Em dashes.** v2 had 834. The book's quality floor is zero, and v3 is at zero.
3. **Voice.** v2 read as a factory manual ("workcell", "production capacity", "fire lane"), which the design system explicitly rules out. v3 is the book's plain, warm register.
4. **Content.** v2's advertised "684 6S activities" were six template sentences string-substituted across 114 zones. Every zone in v3 is written specifically, and a validation gate fails the build if any sentence repeats across zones.
5. **Time.** v2's per-step minutes and its "98h 00m" total were invented. v3 uses ranges only.

v2 did state the six-S canon correctly, with Safety as the 4th S. That carried forward, and a gate now enforces it.

## Rebuilding

Run from `source/`, in order. Steps 1 and 2 only need re-running if the zone inventory or the prose changes.

1. `extract.py` — reads the v2 HTML, writes `zones-v2-inventory.json` (room and zone names, functions, hazards)
2. *(workflow)* — 20 room agents draft, 20 refine; results land in `content.json`
3. `collect.py` — pulls the refine-stage results out of the workflow journal into `content.json`
4. `build.py` — assembles the HTML deterministically in the book design system
5. `validate.py` — runs the seven gates; exits non-zero on any failure

Paths inside the scripts are absolute and point at this session's locations. Update them before re-running.

`content.json` is the editable source of truth for the prose. To fix wording, edit it and re-run `build.py` and `validate.py`; there is no need to re-run the agents.

## Known caveats

- The PDF was rendered with headless Microsoft Edge, as Chrome is not installed on this machine. It was verified by page count and file size, not read page by page.
- The four frozen canon lines from the brief are quoted verbatim across the manual, 11 times in total. This is intended, and the repeated-sentence gate whitelists them.
