# Final Package Summary: Chapter 31, The Entryway

## Status
Complete. The chapter was REWRITTEN to be instruction-centric (in the established book voice, grounded in the CH31 canonical strings and brief; no verbatim source file existed), then fully repackaged. Per Phil's directive, the detailed, step-by-step clean-and-shine instructions with their exact inputs are now the CORE of the chapter, so the manuscript is intentionally longer than a method chapter. All channel packages were rebuilt, validated, and quality-reviewed, plus a publish-ready HTML. This is the FIRST chapter of Part Nine (Room-by-Room Playbooks) and the OPENING chapter of the applied half of the book; the six-S method (Parts 1 to 8, the full six-S journey) is complete, and from here the book stops teaching in the abstract and points the finished loop at one real room at a time. Chapter 31 is the FIRST of twenty room playbooks (Chapters 31 to 50) and the PROOF chapter for the new instruction-centric room-playbook format: per-zone clean and shine procedures with exact inputs are the centerpiece, governed by a universal nine-rule Shine method, with clean-to-inspect-and-flag (Shine finds hazards, the safety pass fixes them). The friction meter, which reached its goal at Chapter 30, is RETIRED for Part 9; each room now closes on its own concrete before-and-after transformation.

## How this chapter was made
Rewritten in the established book voice and design to put instructions and inputs first, then packaged like Chapters 1 to 30:
- `chapter_31_manuscript.md` (manuscript; reader prose with [VISUAL] / [INFOGRAPHIC] / [ILLUSTRATION] direction blocks that are production notes, not reader content). About 5,427 prose words (instruction-heavy by design, deliberately longer than a method chapter) with exactly 4 visual blocks: the opener `[VISUAL: opener two states]`, `[INFOGRAPHIC: the five zones]`, `[INFOGRAPHIC: the Shine method and the entryway kit]`, and `[ILLUSTRATION: before-and-after signature]`.
- `chapter_31_final.html` (final designed HTML: 4 inline SVG figures, 4 balanced figure/figcaption pairs, the definition box, and the before-and-after room signature as the recurring close in the locked palette and type; NO friction meter, which is retired for Part 9). Figure 3 is the two-panel "Shine method and entryway kit".
- the canonical strings and brief.

This means the chapter is a draft awaiting author review. The packaging is faithful to the rewritten draft; if the author revises the chapter, refresh the canonical layer and the affected packages.

## What was produced
56 files total across the content-package, in 12 sub-packages plus the publishable HTML at the package root, counting these 4 review files.

| Package | Files | Package | Files |
|---|---|---|---|
| Canonical | 8 | video-audio | 5 |
| Web | 7 | slides | 3 |
| LinkedIn | 5 | pdf-ebook | 5 |
| Facebook | 3 | graphics | 4 |
| X | 2 | workflow | 5 |
| Newsletter | 4 | review | 4 |
| Publishable HTML | 1 (package root) | | |

Total: 56 files (canonical 8, chapter-31-publishable.html 1, web 7, linkedin 5, facebook 3, x 2, newsletter 4, video-audio 5, slides 3, pdf-ebook 5, graphics 4, workflow 5, review 4). Verified by direct file count.

## Quality gates passed (measured, across the content-package)
- **Dash scan:** CLEAN. Scanned across the content-package: 0 em dashes and 0 en dashes, and 0 real spaced-hyphen (" - ") violations. The only " - " matches in the package are markdown bullets in the nine-Shine-rules list rendered inside a blockquote as "> - ", plus the self-referential dash-rule literal recorded in `workflow/production-checklist.md`; neither is a dash in use. Labels use the middot "·". Compound hyphens ("before-and-after", "room-by-room", "count-by-weather", "worn-mat", "first-and-last", "product-type", "six-S") are correctly not counted as dashes.
- **Tone scan** (force / blame / hype words): run programmatically across the content-package and CLEAN. Every hype-word hit is a prohibition-list mention (naming the thing the chapter refuses) or a legitimate word in context; nothing is actual usage. The same scan confirmed **NO brand-name leaks**: the package names product TYPES only, never brands. The "Method" matches are the ordinary word "method" (as in the Shine method, in headings and prose), not a brand name.
- **JSON:** `web/schema-org-article.json` and the publishable HTML's JSON-LD block both parse valid and are content-equal; `canonical/chapter-metadata.json` parses valid.
- **CSV:** `workflow/asset-inventory.csv`, valid, 1 header row plus 56 data rows, every row 7 columns (verified).
- **Social lengths (recomputed):** X 10 standalone posts, all at or under 280 characters (longest 271); X 14-post thread, all at or under 280 (longest 272); LinkedIn 10 standalone posts each under 150 words of body (maximum 147); Facebook longform body 440 words (within the 300 to 450 gate).
- **Publishable HTML:** body byte-identical to `chapter_31_final.html` (verified), the only change an inserted production head (SEO meta, Open Graph, Twitter Card, JSON-LD); 4 inline SVG figures, 4 balanced figure/figcaption pairs, and the definition box present. The recurring close is the BEFORE-AND-AFTER room signature (figure 4), which replaces the retired friction meter; there is no friction-meter figure in this chapter or in any Part 9 chapter.
- **Frozen strings:** all present byte-verbatim in BOTH the manuscript and the HTML: the rule; the five-zones line; the definition box; the NEW Shine-method line; the nine Shine rules; the first-and-last, count-by-weather, and worn-mat reframes; the four callouts (the 6S Tip, now colour-code your cloths and never use fabric softener; the Common Mistake, now wiping-until-it-looks-better versus cleaning to a method; plus the Quick Win and Family Challenge); the UPDATED One Idea to Keep ("A zone is not clean because it looks clean..."); and the before-and-after caption.
- **Quote cards:** every quote card in `graphics/quote-card-copy.md` (10 cards) programmatically diffed against `canonical/chapter-quotes.md` and byte-verbatim (0 mismatches); this includes the Shine-method line and the nine-rule list. Back-cover testimonials clearly marked placeholders.

## New instruction-centric Part 9 format checks (measured / verified for the first room playbook)
- **Instruction-centric centerpiece:** confirmed. The chapter's core is the detailed, step-by-step clean-and-shine procedures for each of the five entryway micro-zones, with exact inputs. In the final and publishable HTML this is carried by 5 zone cards (Zone 1 through Zone 5), each with an Inputs list, a numbered Steps procedure, and an Inspect-and-flag list. Measured totals: 5 `<ol>` (one Steps procedure per zone) and 84 `<li>` across the document, with 7 `<ul>`.
   - NOTE (honest correction): the task brief stated "122 `<li>`", but direct measurement of the on-disk publishable and final HTML returns 84 `<li>` (confirmed three ways: `<li`, `<li` followed by space/`>`, and `</li>` all equal 84). The 5 `<ol>` figure is correct. The 84 count is reported here as the real result.
- **Nine-rule Shine method:** present as the universal method that governs every per-zone procedure (work top to bottom, dry before wet, back to front / clean to dirty, mist the cloth not the surface, two cloths, colour-code cloths and no fabric softener, match cleaner to surface, give the cleaner a moment, clean to inspect and flag not fix). The Shine-method line and the nine-rule list are frozen and byte-verbatim in manuscript, HTML, and quote cards.
- **Per-zone inputs + steps + inspect:** confirmed in the HTML zone cards (Inputs / Steps / Inspect and flag labels present for all five zones).
- **Clean-to-inspect-and-flag:** confirmed. Shine finds the hazards; the safety pass fixes them (the chapter uses but does not re-teach the hazard hunt).
- **Friction meter retired:** confirmed. The friction meter reached its goal at Chapter 30 and does NOT appear in this chapter's HTML; its recurring-close role is taken by the before-and-after room signature (figure 4).
- **Before-and-after room signature:** present as figure 4, governed by the frozen before-and-after caption. This is the new Part 9 recurring close (Chapters 31 to 50).
- **No brand leaks:** confirmed by the tone scan; the kit is given as product TYPES only, never brands.

## Key extracted assets
- **Title:** The Entryway
- **Part:** Part Nine, Room-by-Room Playbooks (the FIRST chapter of Part 9; the FIRST of twenty room playbooks, Chapters 31 to 50; the PROOF chapter for the new instruction-centric room-playbook format)
- **Hero device:** the room as micro-zones, cleaned to a method (point the finished loop at one zone at a time and run the clean-and-shine procedure with its exact inputs)
- **The rule (frozen, hero):** You do not 6S a whole room. You 6S one zone of it, then the next, until the room is done. A room is only ever a handful of small zones wearing a single name, and a zone is a job you can finish in an afternoon.
- **The five zones (frozen):** The entryway is five small zones, not one big job: the landing spot where pockets empty, the coats, the shoes, the bench or console, and the door with its mat and the strip of floor inside its swing. Do them one at a time and the room takes a few short sessions, not a lost weekend.
- **The Shine method (frozen, NEW):** Shine is cleaning to a method, not wiping until it looks better: work top to bottom and dry before wet, mist the cloth and not the surface, clean with one cloth and dry with a second, and let your eye inspect every surface your hand passes over. You leave the zone genuinely clean, and you find what needs fixing on the way.
- **The nine Shine rules (frozen list, govern every zone procedure):** work top to bottom; work dry before wet; work back to front, clean to dirty; mist the cloth, not the surface; use two cloths, one to clean and one to dry; colour-code your cloths and never use fabric softener; match the cleaner to the surface; give the cleaner a moment to work; clean to inspect, and flag, do not fix.
- **The definition box (frozen):** A finished entryway is one where everyone can land and launch in seconds: keys and phone drop into one tray, today's coat and shoes have an easy home, wet things stay on the mat, and the paper that comes through the door leaves again with a verdict. Nothing lives on the floor inside the door's swing, and two hooks always stand empty for whoever arrives next.
- **The first-and-last reframe (frozen, pull-quote):** The entryway is the room you spend the least time in and notice the most, because you cross it every single time you come or go. A calm doorway is the first thing that greets you home and the last thing that speeds you out, which is why the smallest room in the house pays back a 6S loop faster than any other room you own.
- **The count-by-weather reframe (frozen, pull-quote):** Coats are counted by weather, not by number. Each person gets one coat per kind of weather your climate genuinely produces, and a second in the same category has to beat the first on a specific, nameable day. The expensive coat you never wear is not exempt, because the money is already spent whether it hangs here or keeps someone else warm.
- **The worn-mat reframe (frozen, pull-quote):** A mat looks perfectly fine long after it has stopped working, so you test it instead of looking at it. A finished mat sits with its fibres flattened one way and the grit rides straight over it onto the next pair of shoes. A worn mat is not saving you anything, it is quietly sanding the finish off every floor between the front door and the kitchen.
- **The before-and-after caption (frozen, governs the Part 9 signature figure):** This is the entryway the whole loop was for: the same doorway you started with, cleared, calmed, and holding only what the door actually needs. Take the before photo before you touch a thing, because within a month you will not believe the room was ever the other one, and take the after photo as the standard, because it is the picture the door has to match from now on.
- **One Idea to Keep (frozen close, UPDATED):** A zone is not clean because it looks clean. It is clean because you gathered the right inputs, took it apart, and cleaned every surface to a method, top to bottom, dry before wet, one cloth to clean and one to dry, inspecting as you went. Do that to one zone this weekend, and let the door start working for you every time you cross it.

## Continuity notes
- FIRST chapter of Part 9 (Room-by-Room Playbooks) and the OPENING chapter of the applied half of the book. Follows Chapter 30 (Your Next 6S Event), the finale of the main arc where the friction meter reached its goal for the first and only time. Chapter 31 opens the applied half: the teaching stops and the doing begins, and the reader runs the finished loop, to the method, on their first real room, the entryway.
- The friction meter is RETIRED for Part 9. Its recurring-close role is taken by the BEFORE-AND-AFTER room signature (figure 4), governed by the frozen before-and-after caption and the two photos to take (the before kept as proof per Chapter 6, the after taped up as the ideal-state standard per Chapter 25). This is the new recurring ritual for Chapters 31 to 50.
- Hands off lightly to **Chapter 32 · The Kitchen**, worked the same way, one zone at a time to the same method. Chapter 31 teases the kitchen in a single line but does NOT teach it.

## Scope fences held
Owns the instruction-centric room-playbook FORMAT (a room decomposed into its micro-zones and run one at a time, with per-zone clean-and-shine procedures and exact inputs, governed by the universal nine-rule Shine method) and PROVES it on the entryway. It USES the method and cross-references where a technique lives (Ch 6 the before photo, Ch 8 to 30 the six S's) but does NOT re-teach Sort, Straighten, Shine, Safety, Standardize, or Sustain (a one-line callback is fine, a re-teach is not); the Shine method is applied here, not re-taught from scratch. Shine finds hazards and flags them; the safety pass fixes them. It stays in the entryway with only a light one-line hand-off to Chapter 32; it names product TYPES only, never brand names, and uses no invented statistics or prices. Reader-facing files name these fences.

## Open items before publishing (handoffs, not blockers)
1. Author review and approval of the rewritten, instruction-centric chapter.
2. Insert the live chapter URL wherever a CTA says "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-31-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read the free chapter").
5. Replace or remove the back-cover testimonial placeholders.
6. Produce or wire in the visual assets, leading with the opener (the entryway in two states) or the before-and-after signature, with the five-zones infographic and the two-panel "Shine method and entryway kit" infographic as the supporting visuals.
7. Offer the companion resources as the lead magnet and pick one LinkedIn carousel version.

## Recommended next action
Review the rewritten chapter first, checking that the instruction-centric centerpiece (per-zone clean-and-shine procedures with exact inputs), the nine-rule Shine method, the clean-to-inspect-and-flag discipline, and the before-and-after signature that replaces the retired friction meter are right. If so, do one find-and-replace pass for placeholders and "the online book," then start the rollout in `workflow/publishing-calendar.md`. Part 9 OPENS here, the first of twenty room playbooks; NEXT is Chapter 32, The Kitchen, worked the same way, one zone at a time to the same method.

Generated 2026-07-22.
