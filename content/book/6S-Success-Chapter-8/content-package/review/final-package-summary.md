# Final Package Summary: Chapter 8, Sort: Remove What Does Not Belong

## Status
Complete. The chapter was authored (no source existed), then fully packaged. All twelve packages built, validated, and quality-reviewed, plus a publish-ready HTML. This chapter opens Part 3 (Sort) and is the first action chapter in the book.

## How this chapter was made
Chapter 8 had no supplied source files. Its source trio was authored in the established book voice and design, then packaged like Chapters 1 to 7:
- `chapter_08_signature.md` (signature plan, authored)
- `chapter_08_manuscript.md` (manuscript, authored, 3,944 words, counted)
- `chapter_08_final.html` (final designed HTML, authored, with the opener, the One Question gate, the worked pass, and the moved friction meter as inline SVG, in the locked palette and type)

This means the chapter is a draft awaiting author review. The packaging is faithful to the draft. If the author revises the chapter, the canonical layer and the affected packages should be refreshed.

## What was produced
56 files across 12 folders, plus the publishable HTML at the package root. Counted directly: 52 files in the package before this review folder, plus these 4 review files, equals 56.

| Package | Files | Package | Files |
|---|---|---|---|
| Canonical | 8 | video-audio | 5 |
| Web | 7 | slides | 3 |
| LinkedIn | 5 | pdf-ebook | 5 |
| Facebook | 3 | graphics | 4 |
| X | 2 | workflow | 5 |
| Newsletter | 4 | review | 4 |
| Publishable HTML | 1 (package root) | | |

## Quality gates passed (each scan or count was run for this summary)
- **Widened dash scan:** em dash (U+2014), en dash (U+2013), and spaced-hyphen " - " used as a separator (excluding markdown list bullets), run across all 52 package files plus the manuscript and both HTML files. Result: zero matches. Separators use the middot ("·"). For transparency, the only em/en dashes in the chapter folder are four inside the non-shipped working brief `CH8_CANONICAL_STRINGS_AND_BRIEF.md`.
- **Banned-word scan:** zero hits across the package for "unlock," "leverage," "delve," "seamless," "supercharge," "elevate," "game-changing," "dive in," "in conclusion," "fast-paced," "in today's," "effortless," "revolutionize."
- **JSON:** `canonical/chapter-metadata.json` and `web/schema-org-article.json` both parse as valid JSON. The publishable HTML's single embedded JSON-LD block validates.
- **CSV:** `workflow/asset-inventory.csv` is valid with all 7 required columns and 56 data rows, no ragged rows.
- **Social length (measured):** X thread is 15 posts (header says 15, counted 15), all at or under 280 characters, longest 275; X short posts are 10, all at or under 280, longest 261; LinkedIn is 10 posts, each under 150 words, longest 107; Facebook longform body is 430 words, inside the 300 to 450 target.
- **Final HTML:** exactly 4 inline SVGs in both `chapter_08_final.html` and `chapter-08-publishable.html` (opener, the One Question gate, the worked pass, the moved friction meter). Structural tags balance (div 15/15, section 1/1, svg 4/4, head/body/html/script/style all 1/1). Authored final HTML 41,523 bytes; publishable HTML 44,852 bytes.
- **The friction-meter first move:** the frozen caption ("The needle moves for the first time. Nothing was bought and nothing was cleaned...") is byte-identical in both HTML files. The manuscript language reads as moved partway, not held and not arrived: "steps off the friction side," "stops in the middle, pointed at the goal but not arrived," "stops partway" (present, verified). This is the chapter's landmark and it reads correctly.

## Fixed recurring item (not a flag)
- The Facebook longform runs 430 words (measured), inside the 300 to 450 target. This is the overrun that was flagged on Chapters 5, 6, and 7 (which ran near 600 words) now corrected. Good.

## Key extracted assets
- **Title:** Sort: Remove What Does Not Belong
- **Slug:** sort-remove-what-does-not-belong
- **Hero device:** The One Question, "Does this help the space do its job?" Yes means it belongs here; no means it belongs somewhere else and goes to a better home. This is the operational form of Chapter 7's purpose.
- **Worked example:** a pass through the entryway drop zone. Belongs here: keys, outgoing mail to post, sunglasses, the dog's leash, a folded reusable bag, the umbrella, a small tray for keys and wallet. Belongs somewhere else: already-read magazines, junk mail, a phone charger (desk), finished homework and school papers, a stray screwdriver, a shed sweater (closet), a coin-collecting decorative bowl.
- **Anti-shame line (verbatim):** "You are not deciding what it is worth. You are only deciding it does not live here."
- **Hero CTA:** run a Sort pass, even a one-object pass. Say the space's job out loud, ask the One Question of each object, carry out every no.
- **One Idea to Keep (verbatim):** "You do not organize a space by adding storage. You organize it by removing what was never supposed to be there. Sort first, and most of the mess walks out the door before you buy a single bin."

## Continuity notes
- **Opens Part 3 (Sort).** Follows Chapter 7 (the purpose) and hands off to Chapter 9 (Necessary vs. Unnecessary) without doing Chapter 9's work: "You sorted by belonging. Next we sort by need" (verbatim).
- **The drop zone pays off.** Chosen in Chapter 4, audited at 14 out of 30 in Chapter 5 (weakest on Standardize and Sustain), photographed in Chapter 6, given a purpose in Chapter 7. The number, the photo, and the purpose all pay off here, and the purpose sentence is the judge for the pass.
- **The landmark:** the friction meter moves for the first time in the book, because objects physically left. The needle steps into the honey middle, a dashed ghost needle marks the old friction position, and the GOAL crosshair from Chapter 7 still sits ahead. It stops partway because Sort is only the first of the six S's; Straighten, Shine, Safety, Standardize, and Sustain are still ahead.
- **Scope held.** Removal is an address change, not disposal. No "toss / trash / throw out" instruction leaked into the canonical, X, or LinkedIn assets (scan run). The maybes get one light forward-teaser without building Chapter 10's system, and donate/sell/discard is left to Chapter 11.

## Open items before publishing (handoffs, not blockers)
1. Author review and approval of the authored chapter. Everything downstream depends on it.
2. Insert the live chapter URL wherever a CTA says "the online book" (appears in 19 package files, counted).
3. Replace author / publisher / URL / date placeholders in the schema JSON, the PDF/ebook files, and `chapter-08-publishable.html`.
4. Rotate the six LinkedIn and X CTA phrasings.
5. Replace or remove the three back-cover testimonial placeholders before print.
6. Optionally correct the X thread's "(approx.)" character annotations to the measured counts.
7. Produce the visual assets, leading with the One Question card, and pick one LinkedIn carousel version (the copy-ready one), keeping the outline as planning.

## Recommended next action
Review the authored chapter first. If the One Question, the worked pass, and the friction-meter first move are right, do one find-and-replace pass for placeholders and "the online book," then start the rollout in `workflow/publishing-calendar.md`. With Chapter 8 done, Part 3 (Sort) has begun; Chapter 9 sorts what is left by need. If you want changes to the chapter, tell me and I will revise the draft and re-sync the package.

Generated 2026-07-01.
