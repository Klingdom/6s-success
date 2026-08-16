# Editorial Review: Chapter 32 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting, and the instruction-centric Part 9 format items (instruction-centric centerpiece, kitchen Shine method, per-zone inputs plus steps plus inspect, friction meter retired, before-and-after signature, no brand leaks). This review reports only checks actually run; every count below was measured with a scan, and every cited quote was verified present in the manuscript or canonical strings before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the CH32 canonical strings and brief). The chapter is instruction-centric, so its CORE is the detailed, step-by-step clean-and-shine procedures with exact inputs for each of the seven kitchen micro-zones, and it is intentionally longer than a method chapter. The package holds the warm, capable, lightly celebratory, anti-shame voice across all channels, the facts trace cleanly to the manuscript and canonical strings, and the hooks are concrete (if the entryway was the room to start with, the kitchen is the room that matters most; you do not clean the kitchen, you clean the cooking zone; grease is the whole job and grease hides upward; the most powerful tool in a kitchen clean is not a scrubbing arm, it is time). As the SECOND room playbook of Part Nine, it applies the proven applied format to the busiest, dirtiest, highest-payback room and closes on the before-and-after room signature that replaces the retired friction meter. Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the room-as-zones framing, the seven-zones line, the nine-rule Shine method plus the grease layer, the per-zone procedures, the soak-and-dwell, lift-do-not-wipe-around, and reset-point reframes, and the before-and-after signature) is by design and staggered by the calendar.
- The hero vocabulary runs high ("zone," "grease," "degrease," "soak," "dwell time," "method," "cloth," "top to bottom," "lift," "hood," "hob," "sink," "fridge"), because it is the subject of an instruction-heavy chapter, not a tic. When excerpting, vary the surrounding language so a single post does not stack "zone" and "grease" and "method".

## AI-sounding phrasing
- None found. The writing leans on concrete images and procedure (the burner grates and hood filter set to soak in hot degreasing water before you touch anything else; the crumbs living under the toaster's feet and in the fold of the fridge gasket; the sponge as the dirtiest object in the room; the dishwasher filter as why your glasses come out gritty) rather than generic filler.
- Dash scan CLEAN: 0 em dashes, 0 en dashes, and 0 real spaced-hyphen (" - ") violations across the package. The only " - " matches are the markdown bullets in the nine-Shine-rules list rendered inside a blockquote as "> - ", plus the self-referential dash-rule literal recorded in `workflow/production-checklist.md`; neither is a dash in use.

## Unsupported claims
- No invented statistics, names, dates, or prices. The room-as-zones idea, the nine-rule Shine method, and the kitchen grease layer are taught as the book's own craft applied to a real room; the kitchen's zones, inputs, kit, and hazards are offered as concrete instruction, not as measured data.
- **Note on scope of scans run:** a tone scan (force / blame / hype) WAS run programmatically and returned CLEAN, with every match a negation or a prohibition-list mention rather than actual usage. A brand-name scan WAS run and returned CLEAN: the package names product TYPES only (neutral pH multi-surface cleaner, food-area degreaser, microfiber cloths, and so on), never brands, and the "Method" matches are the ordinary word "method" (the Shine method), not a brand. This no-brand-leak discipline is the key Part 9 constraint for the product-type kit, and it held.
- Testimonials in the PDF/ebook back-cover copy are clearly marked placeholders.

## Hooks
- Strong and specific: if the entryway was the room to start with, the kitchen is the room that matters most; this chapter, more than any other, is about the clean; you do not clean the kitchen, you clean the cooking zone, which is done when the hood, the grates, the splash wall and the hob are degreased and the crock is wiped; grease is the whole job in a kitchen, and grease hides upward.

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (do one zone this weekend, the sink or the cooking zone) is concrete, free, and the two highest-leverage zones in the room. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. The instruction-centric room-playbook format matches the manuscript, the canonical brief, and the HTML: a room decomposed into its micro-zones and run one at a time, with per-zone clean-and-shine procedures and exact inputs, governed by the nine-rule Shine method plus the kitchen grease layer. The chapter correctly reads as the SECOND room playbook and applies the format to the kitchen. It USES the method and cross-references where a technique lives (Ch 6, Ch 8 to 30, Ch 31) without re-teaching Sort, Straighten, Shine, Safety, Standardize, or Sustain; Shine finds hazards and flags them, the safety pass fixes them; it stays in the kitchen with only a light one-line hand-off to Chapter 33 (The Pantry); and it names product TYPES only, never brands.

## Overlong social posts (measured, character/word counts)
- **X short posts:** **10** standalone posts, all at or under 280 characters (**longest 274**). Pass.
- **X thread:** header states 14 posts; the file contains **14** posts, each at or under 280 characters (**longest 274**). Pass.
- **LinkedIn:** **10** standalone posts, each under 150 words of body copy (**maximum 144**). Pass.
- **Facebook longform:** **426** words in the post body (within the 300 to 450 gate). Not a flag.

## Tone
- Correct platform-fit; the warm, capable, lightly celebratory, anti-shame register holds everywhere. The kitchen is framed as the room that matters most and the biggest single win in the house, so the feeling is capability, not instruction-from-above; the before state is honoured, not mocked; and nothing implies the room must be conquered in one exhausting go (faced as seven zones, the most daunting room is a series of finishable pieces). The tone scan confirms every force / blame / hype hit is a negation or prohibition-list mention, not usage, and the brand scan confirms no brand-name leaks.

## Formatting
- Clean Markdown. JSON checked: `web/schema-org-article.json` and the JSON-LD embedded in `chapter-32-publishable.html` both parse valid and are content-equal, and `canonical/chapter-metadata.json` parses valid. CSV `workflow/asset-inventory.csv` is valid with 1 header row plus **56** data rows, every row **7** columns (verified). The publishable HTML body is byte-identical to `chapter_32_final.html` (verified); the only change is an inserted production head (SEO meta, Open Graph, Twitter Card, JSON-LD). It carries **4** inline SVG figures, **4** balanced `<figure>` / `<figcaption>` pairs, and the definition box is present. Figure 3 is the two-panel "kitchen Shine method and kit".

## Manuscript check (measured)
- The manuscript `chapter_32_manuscript.md` runs to roughly **5,814** prose words (instruction-heavy by design, deliberately longer than a method chapter) and contains exactly **4** visual direction blocks (production notes, not reader content): the opener `[VISUAL: opener two states]`, `[INFOGRAPHIC: the seven zones]`, `[INFOGRAPHIC: the kitchen Shine method and kit]`, and `[ILLUSTRATION: before-and-after signature]`.

## Instruction-centric centerpiece check (the chapter's core, measured in the HTML)
- Confirmed in the final and publishable HTML: the centerpiece is **7 zone cards** (Zone 1 through Zone 7), each with an **Inputs** list, a numbered **Steps** procedure, and an **inspect-and-flag** paragraph. Measured element totals across the document: **7 `<ol>`** (one Steps procedure per zone) and **85 `<li>`**.
- The nine-rule Shine method plus the kitchen grease layer (soak first, work top to bottom, lift rather than wipe around, switch to the degreaser the moment a surface is tacky, hold food-safety cloth discipline) governs every per-zone procedure, and the clean-to-inspect-and-flag discipline is present (Shine finds hazards, the safety pass fixes them).

## Frozen-string check (measured)
- All frozen strings were confirmed present byte-verbatim in BOTH the manuscript and the publishable HTML: the seven-zones line; the grease rule; the definition box; the soak-and-dwell, lift-do-not-wipe-around, and reset-point reframes; the four callouts (the Quick Win, the soak-first trick; the 6S Tip, dwell time plus a dedicated fridge / raw-meat cloth colour plus never mix bleach; the Family Challenge; the Common Mistake, wiping around versus lift-and-empty); the One Idea to Keep; and the before-and-after caption.

## Quote-card check (measured)
- Every quote card in `graphics/quote-card-copy.md` was programmatically diffed against `canonical/chapter-quotes.md` and is byte-verbatim (0 mismatches). This includes the grease rule and the nine-rule list.

## Part 9 signature check (the chapter's recurring close, replacing the friction meter)
- Verified in the HTML: the friction meter is RETIRED for Part 9 and does NOT appear in this chapter. Its recurring-close role is taken by the BEFORE-AND-AFTER room signature (figure 4), governed by the frozen before-and-after caption and paired with the two photos to take (the before kept as proof per Chapter 6, the after kept as the ideal-state standard per Chapter 25). This is the recurring ritual for Chapters 31 to 50. There is no friction-meter figure in this chapter or in any Part 9 chapter.

## Recommended edits before publishing
1. Author approval of the instruction-centric chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-32-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read the free chapter" / "Read it free online").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (the kitchen in two states) or the before-and-after signature, with the seven-zones infographic and the two-panel "kitchen Shine method and kit" infographic as the supporting visuals.
