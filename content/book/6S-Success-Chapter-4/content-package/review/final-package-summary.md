# Final Package Summary: Chapter 4, How to Choose Your First Target Area

## Status
Complete. The chapter was drafted (no source existed), then fully packaged. All twelve packages built, validated, and quality-reviewed, plus a publish-ready HTML.

## How this chapter differs from Chapters 1 to 3
Chapters 1 to 3 had real source files that were packaged. Chapter 4 had none. Its three source files were drafted in the established book voice and design, then packaged like the others:
- `chapter_04_signature.md` (signature plan, drafted)
- `chapter_04_manuscript.md` (manuscript, drafted)
- `chapter_04_final.html` (final designed HTML, drafted, with the First Target Map and Target Scorecard as inline SVG, in the locked palette and type)

This means the chapter is a draft awaiting author review. The packaging is faithful to the draft. If the author revises the chapter, the canonical layer and the affected packages should be refreshed.

## What was produced
56 files across 12 folders, plus the publishable HTML at the package root.

| Package | Files | Package | Files |
|---|---|---|---|
| Canonical | 8 | video-audio | 5 |
| Web | 7 | slides | 3 |
| LinkedIn | 5 | pdf-ebook | 5 |
| Facebook | 3 | graphics | 4 |
| X | 2 | workflow | 5 |
| Newsletter | 4 | review | 4 |
| Publishable HTML | 1 (package root) | | |

## Quality gates passed
- Em dash and en dash scan: zero across all files.
- Banned-word scan: zero. The word "transform" does not appear at all.
- JSON: `chapter-metadata.json` and `schema-org-article.json` both parse as valid JSON. The publishable HTML's embedded JSON-LD validates.
- CSV: `asset-inventory.csv` valid with all 7 required columns.
- Social length: one X post was 290 characters and was trimmed; all X posts are now within 280, LinkedIn posts under 150 words.
- Source fidelity: the two questions, the sweet spot (high friction, low effort), the garage takedown, the three filters, the scorecard math, and the write-it-down close all match the drafted final HTML.
- Final HTML: 4 balanced SVGs (garage opener, First Target Map, Target Scorecard, aimed friction meter), 7 sections, valid structure.

## Key extracted assets
- **Title:** How to Choose Your First Target Area
- **Slug:** how-to-choose-your-first-target-area
- **Hero device:** The First Target Map (friction vs effort; sweet spot is high friction, low effort).
- **Secondary device:** The Target Scorecard (friction minus effort).
- **Hero CTA:** Score your spaces, pick the high-friction, low-effort one, and write it down.
- **One Idea to Keep:** You do not need more motivation to start. You need a smaller, smarter first target. Win where you will see it, and the next project gets easier on its own.

## Continuity notes
- Pays off Chapter 3's "we will pick a target you can win."
- Closes Part One and hands off to Part Two (the audit in Chapter 5).
- Friction meter holds steady (no objects moved) but gains a crosshair, the reader has aimed but not fired. Flagged in the signature for author sign-off, along with the map's axis and quadrant labels.

## Open items before publishing (handoffs, not blockers)
1. Author review and approval of the drafted chapter. Everything downstream depends on it.
2. Insert the live chapter URL wherever a CTA says "the online book."
3. Replace author / publisher / URL / date placeholders in the schema JSON, the PDF/ebook files, and `chapter-04-publishable.html`.
4. Rotate the LinkedIn and X CTA wording.
5. Replace or remove the back-cover testimonial placeholders before print.
6. Produce the visual assets, leading with the First Target Map.
7. Pick one LinkedIn carousel version (copy-ready), keep the outline as planning.

## Recommended next action
Review the drafted chapter first. If the First Target Map framing and the voice are right, do one find-and-replace pass for placeholders and "the online book," then start the 14-day rollout in `workflow/publishing-calendar.md`. If you want changes to the chapter, tell me and I will revise the draft and re-sync the package.

Generated 2026-06-28.
