# Editorial Review: Chapter 18 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting. This review reports only checks actually run; every count below was measured with LC_ALL=C scans (character and word counts recomputed, not trusted from the files), and every cited noun or quote was grep-verified present in the manuscript or final HTML before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the 6S source "Principles of 6S: Shine Step," the Steps to Complete Shine step 2, "determine cleaning methods"; no verbatim source file supplied). The package holds the warm, relief-and-permission, anti-shame voice across all channels, the facts trace cleanly to the manuscript and HTML, and the hooks are concrete (the same hob done the dreaded way and the working way, "The best method is the one you will actually do," and the oven that was a method problem, not a me problem). Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the effective-and-easy test, the five working methods, the rule, the method-problem reframe, the still-reading callback, the small-and-often payoff, the meter MOVE) is by design and staggered by the calendar.
- The hero vocabulary runs high ("method," "clean," "target," "tool," "easy," "quick"), because it is the subject, not a tic. When excerpting, vary the surrounding language so a single post does not stack "actually," "dread," and "small."

## AI-sounding phrasing
- None found. The writing leans on concrete images (the hob smeared with grease, the hour on your knees with a caustic spray, the cloth by the sink, the shower wall under running water, the counter while the pasta boils) rather than generic filler.
- Widened dash scan clean (em, en, spaced-hyphen-as-punctuation, and dash HTML entities all **0**; the lone raw " - " is inside a quoted description of the dash rule in `workflow/production-checklist.md`, not a dash in use). No hype words in any asset.

## Unsupported claims
- No invented statistics, names, or dates. The five working methods are taught as practical technique home-scaled from Seiso "determine cleaning methods"; the origin is not overclaimed beyond Toyota / the Toyota Production System.
- The "war on dirt" / "blitz" / "blast" / "purge" tokens flagged by the force-metaphor scan are confined to negated production/scope notes (`workflow/repurposing-map.md`, `video-audio/b-roll-and-visual-notes.md`, `graphics/image-generation-prompts.md`, `graphics/diagram-ideas.md`, `canonical/chapter-cta.md`); no reader-facing copy uses them. "attack" (as a word) and "pull the trigger" are both **0**.
- Every "spotless" (11 occurrences, all in production/editor notes) is a negated non-goal, never an aspiration. No brand-name products are endorsed anywhere (the raw-substring flags on "Method," "Dawn," and "Cif" are false positives, resolved in the brand-voice check).
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the same hob drawn two ways (the dreaded bucket-of-ten-bottles method beside the one-right-tool method), "The best method is the one you will actually do," "You do not have a cleaning problem. You have a method problem," and "A dreaded oven is a done oven."

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (take the one job you dread most, find a faster method, do it once the new way and time it) is concrete, free, and about a two-minute proof. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. Shine step 2 ("determine cleaning methods"), home-scaled into the five working methods (right tool for the surface; top to bottom, dry before wet; fewer, simpler products; keep the tool where the target is; clean in passing), the "methods still serve inspection" continuity from Chapter 16, the applies-to-the-existing-list continuity from Chapter 17, the light Seiso / Toyota nod, and the meter MOVE all match the manuscript, the canonical brief, and the HTML. The chapter correctly carries out the plan and cleans the targets, then hands the recurring rhythm to Chapter 19.

## Overlong social posts (measured, character/word counts recomputed, not trusted from the files)
- **X thread:** header states 14 posts; the file contains **14** posts, all at or under 280 characters INCLUDING the "N/" number line (**longest 269**, post 2, the assignment-still-not-happening gap). Pass.
- **X short posts:** **10** standalone posts, all at or under 280 including the number line (**longest 274**, post 9, the small-and-often payoff). Pass.
- **LinkedIn:** **10** posts, each under 150 words of body copy (**longest 136**, post 3, "Effective AND easy"). Pass.
- **Facebook longform:** **395** words in the post body (within the 300 to 450 hard cap). Not a flag.

## Tone
- Correct platform-fit; the relief-and-permission, anti-shame register holds everywhere, the methods-not-routine honesty is preserved, and the goal is kept honestly ahead (Shine completes in Chapter 19; Safety, Standardize, and Sustain still follow).

## Formatting
- Clean Markdown. Both JSON files parse (`canonical/chapter-metadata.json`, `web/schema-org-article.json`); the publishable HTML carries one JSON-LD block that parses (`@type` Article). CSV `workflow/asset-inventory.csv` has 7 columns and 52 data rows, all consistent (note: this is a pre-completion snapshot the orchestrator regenerates, but it is currently valid). The publishable HTML has 4 balanced `<figure>`/`</figure>` blocks and 4 balanced SVG figures; html/head/body/main all balance. The final HTML also carries 4 balanced SVGs.

## Friction-meter check (the chapter's defining beat)
- Verified in the SVG of both `chapter_18_final.html` and `chapter-18-publishable.html`: the LIVE needle is drawn from the pivot (210,198) to exactly (73,153.5), a clear step past Chapter 16/17's position toward the GOAL. Chapter 16/17's position (75,153) is now the **dashed ghost** just behind the live needle (`stroke-dasharray="5 5"`, opacity 0.55, labeled "Ch 16 · 17 ghost"). A terracotta **SHINE · STEP 2** marker labels the reached position; there is **NO "HOLDS" or "PLANNING" marker** anywhere in the SVG (scan returned zero). Chapter 15's Straighten-complete milestone tick sits further back, with Chapters 12 to 14 fainter dashed ghosts and the Sort-complete milestone furthest back. The GOAL crosshair (tagged PURPOSE) sits at (67,155) on the green calm side, still ahead of the live needle at (73,153.5) with clear room left for Chapter 19's Shine-complete milestone. This reads as a genuine MOVE (Shine step 2), not the finish, and the figure caption matches the frozen caption exactly.

## Recommended edits before publishing
1. Author approval of the authored chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-18-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read it free online" / "Read the free chapter in the online book").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (the same hob cleaned two ways beside the Shine list) and the five-working-methods reference card.
