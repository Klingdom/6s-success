# Editorial Review: Chapter 31 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting, and the new instruction-centric Part 9 format items (instruction-centric centerpiece, nine-rule Shine method, per-zone inputs plus steps plus inspect, friction meter retired, before-and-after signature, no brand leaks). This review reports only checks actually run; every count below was measured with a scan, and every cited quote was verified present in the manuscript or canonical strings before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the CH31 canonical strings and brief; no verbatim source file supplied). The chapter was REWRITTEN to be instruction-centric, so its CORE is now the detailed, step-by-step clean-and-shine procedures with exact inputs for each of the five entryway micro-zones, and it is intentionally longer than a method chapter. The package holds the warm, capable, lightly celebratory, anti-shame voice across all channels, the facts trace cleanly to the manuscript and canonical strings, and the hooks are concrete (the method was the hard part and you have it, this is the fun part where a real room changes; you do not 6S a whole room, you 6S one zone of it; Shine is cleaning to a method, not wiping until it looks better). As the OPENING of Part Nine, it proves the new applied format on the first real room and closes on the before-and-after room signature that replaces the retired friction meter. Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the room-as-zones rule, the five-zones line, the nine-rule Shine method, the per-zone procedures, the count-by-weather and worn-mat reframes, and the before-and-after signature) is by design and staggered by the calendar.
- The hero vocabulary runs high ("zone," "method," "cloth," "top to bottom," "dry before wet," "inspect," "flag," "door," "coats," "shoes," "mat"), because it is the subject of an instruction-heavy chapter, not a tic. When excerpting, vary the surrounding language so a single post does not stack "zone" and "method."

## AI-sounding phrasing
- None found. The writing leans on concrete images and procedure (an overwhelming Saturday turned into a short list of finishable jobs; gather these inputs into a caddy, then top to bottom, dry before wet; coats counted by weather; a mat you test rather than look at; the before photo you were tempted not to take) rather than generic filler.
- Dash scan CLEAN: 0 em dashes, 0 en dashes, and 0 real spaced-hyphen (" - ") violations across the package. The only " - " matches are markdown bullets in the nine-Shine-rules list rendered inside a blockquote as "> - ", plus the self-referential dash-rule literal recorded in `workflow/production-checklist.md`; neither is a dash in use.

## Unsupported claims
- No invented statistics, names, dates, or prices. The room-as-zones idea and the nine-rule Shine method are taught as the book's own craft applied to a real room; the entryway's zones, inputs, kit, and hazards are offered as concrete instruction, not as measured data.
- **Note on scope of scans run:** a tone scan (force / blame / hype) WAS run programmatically and returned CLEAN, with every match a negation or a prohibition-list mention rather than actual usage. A brand-name scan WAS run and returned CLEAN: the package names product TYPES only, never brands, and the "Method" matches are the ordinary word "method" (the Shine method), not a brand. This no-brand-leak discipline is the key Part 9 constraint for the product-type kit, and it held.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the method was the hard part and you have it, this is the fun part where a real room changes; you do not 6S a whole room, you 6S one zone of it, then the next; Shine is cleaning to a method, not wiping until it looks better; we begin at the door, and not by accident, because the entryway is the room you cross most and notice most.

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (do one zone this weekend to the method; give the landing spot about twenty minutes, the entryway's single highest-leverage square foot) is concrete, free, and a roughly twenty-minute proof of the whole idea. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. The instruction-centric room-playbook format this chapter establishes (a room decomposed into its micro-zones and run one at a time, with per-zone clean-and-shine procedures and exact inputs, governed by a universal nine-rule Shine method) matches the manuscript, the canonical brief, and the HTML. The chapter correctly OPENS Part Nine and PROVES the format on the entryway. It USES the method and cross-references where a technique lives (Ch 6, Ch 8 to 30) without re-teaching Sort, Straighten, Shine, Safety, Standardize, or Sustain; Shine finds hazards and flags them, the safety pass fixes them; it stays in the entryway with only a light one-line hand-off to Chapter 32 (The Kitchen); and it names product TYPES only, never brands.

## Overlong social posts (measured, character/word counts)
- **X short posts:** **10** standalone posts, all at or under 280 characters (**longest 271**). Pass.
- **X thread:** header states 14 posts; the file contains **14** posts, each at or under 280 characters (**longest 272**). Pass.
- **LinkedIn:** **10** standalone posts, each under 150 words of body copy (**maximum 147**). Pass.
- **Facebook longform:** **440** words in the post body (within the 300 to 450 gate). Not a flag.

## Tone
- Correct platform-fit; the warm, capable, lightly celebratory, anti-shame register holds everywhere. This is framed as the fun part, the first place the reader spends the method they worked to build, so the feeling is capability, not instruction-from-above; the before state is honoured, not mocked; and nothing implies the room must be conquered in one exhausting go (one finished zone beats five half-done ones). The tone scan confirms every force / blame / hype hit is a negation or prohibition-list mention, not usage, and the brand scan confirms no brand-name leaks.

## Formatting
- Clean Markdown. JSON checked: `web/schema-org-article.json` and the JSON-LD embedded in `chapter-31-publishable.html` both parse valid and are content-equal, and `canonical/chapter-metadata.json` parses valid. CSV `workflow/asset-inventory.csv` is valid with 1 header row plus **56** data rows, every row **7** columns (verified). The publishable HTML body is byte-identical to `chapter_31_final.html` (verified); the only change is an inserted production head (SEO meta, Open Graph, Twitter Card, JSON-LD). It carries **4** inline SVG figures, **4** balanced `<figure>` / `<figcaption>` pairs, and the definition box is present. Figure 3 is the two-panel "Shine method and entryway kit".

## Manuscript check (measured)
- The manuscript `chapter_31_manuscript.md` runs to roughly **5,427** prose words (instruction-heavy by design, deliberately longer than a method chapter) and contains exactly **4** visual direction blocks (production notes, not reader content): the opener `[VISUAL: opener two states]`, `[INFOGRAPHIC: the five zones]`, `[INFOGRAPHIC: the Shine method and the entryway kit]`, and `[ILLUSTRATION: before-and-after signature]`.

## Instruction-centric centerpiece check (the chapter's core, measured in the HTML)
- Confirmed in the final and publishable HTML: the centerpiece is **5 zone cards** (Zone 1 through Zone 5), each with an **Inputs** list, a numbered **Steps** procedure, and an **Inspect-and-flag** list. Measured element totals across the document: **5 `<ol>`** (one Steps procedure per zone), **7 `<ul>`**, and **84 `<li>`** (confirmed three ways: opening `<li`, `<li` followed by space or `>`, and `</li>` all equal 84).
  - **Honest correction:** the rebuild brief stated "122 `<li>`". Direct measurement of the on-disk HTML returns **84 `<li>`**, so 84 is reported here as the real result. The **5 `<ol>`** figure in the brief is correct.
- The nine-rule Shine method governs every per-zone procedure, and the clean-to-inspect-and-flag discipline is present (Shine finds hazards, the safety pass fixes them).

## Frozen-string check (measured)
- All frozen strings were confirmed present byte-verbatim in BOTH the manuscript and the publishable HTML: the rule; the five-zones line; the definition box; the NEW Shine-method line; the nine Shine rules; the first-and-last, count-by-weather, and worn-mat reframes; the four callouts (the 6S Tip, now colour-code your cloths and never use fabric softener; the Common Mistake, now wiping-until-it-looks-better versus cleaning to a method; the Quick Win; the Family Challenge); the UPDATED One Idea to Keep ("A zone is not clean because it looks clean..."); and the before-and-after caption.

## Quote-card check (measured)
- Every quote card in `graphics/quote-card-copy.md` (10 cards) was programmatically diffed against `canonical/chapter-quotes.md` and is byte-verbatim (0 mismatches). This includes the Shine-method line and the nine-rule list.

## Part 9 signature check (the chapter's recurring close, replacing the friction meter)
- Verified in the HTML: the friction meter is RETIRED for Part 9 and does NOT appear in this chapter. Its recurring-close role is taken by the BEFORE-AND-AFTER room signature (figure 4), governed by the frozen before-and-after caption and paired with the two photos to take (the before kept as proof per Chapter 6, the after kept as the ideal-state standard per Chapter 25). This is the new recurring ritual for Chapters 31 to 50. There is no friction-meter figure in this chapter or in any Part 9 chapter.

## Recommended edits before publishing
1. Author approval of the rewritten, instruction-centric chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-31-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read the free chapter" / "Read it free online").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (the entryway in two states) or the before-and-after signature, with the five-zones infographic and the two-panel "Shine method and entryway kit" infographic as the supporting visuals.
