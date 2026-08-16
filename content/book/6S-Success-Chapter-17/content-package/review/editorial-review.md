# Editorial Review: Chapter 17 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting. This review reports only checks actually run; every count below was measured with LC_ALL=C scans (character and word counts recomputed, not trusted from the files), and every cited noun or quote was grep-verified present in the manuscript or final HTML before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the 6S source "Principles of 6S: Shine Step," the Steps to Complete Shine and the Traditional Shine Target Categories; no verbatim source file supplied). The package holds the warm, fairness-and-relief, anti-shame voice across all channels, the facts trace cleanly to the manuscript and HTML, and the hooks are concrete (the one cleaned launch pad in a house full of unnamed targets, "Clean the whole thing, not just the part that shows," and the microwave vent / fridge coils that fail from the side that faces away). Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the two rules, the Shine-list definition, the invisible-target payoff, "you cannot share a feeling of obligation, you can share a list," the choosing-not-assigning turn, the planning-HOLD meter) is by design and staggered by the calendar.
- The hero vocabulary runs high ("target," "list," "clean," "name," "assign," "share"), because it is the subject, not a tic. When excerpting, vary the surrounding language so a single post does not stack "whole," "everyone," and "hands."

## AI-sounding phrasing
- None found. The writing leans on concrete images (the greasy vent under the microwave, the dust-furred fridge coils, the overflow hole, the top of the cupboard, the handle every hand in the house touches) rather than generic filler.
- Widened dash scan clean (em, en, spaced-hyphen-as-punctuation, and dash HTML entities all **zero**; the lone raw " - " is inside a quoted description of the dash rule in `workflow/production-checklist.md`, not a dash in use). No hype words in any asset.

## Unsupported claims
- No invented statistics, names, or dates. The four target categories are attributed lightly to "the original method" and home-scaled from the source (Surface, Equipment, Stored Items, Point of Use); the origin is not overclaimed beyond Toyota / the Toyota Production System.
- The "attack" / "blitz" / "purge" / "war on dirt" tokens flagged by the force-metaphor scan are confined to negated production/scope notes (`canonical/chapter-cta.md`, `graphics/diagram-ideas.md`, `graphics/image-generation-prompts.md`, `video-audio/b-roll-and-visual-notes.md`, `workflow/repurposing-map.md`); no reader-facing copy uses them.
- Every "spotless" (12 occurrences, all in production/editor notes) is a negated non-goal, never an aspiration.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the one cleaned launch pad in a house crowded with unnamed targets and blank name-tags, "Clean the whole thing, not just the part that shows," "A job that belongs to everyone belongs to no one. Put a name on every target," and "Nobody chose this. The absence of names chose it."

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (walk one room and write down five things that need regular cleaning but that nobody has ever been assigned) is concrete, free, and about twenty minutes' work. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. The Shine step 1 focus (determine targets and assignments), the four Traditional Shine Target Categories home-scaled (surfaces / equipment and fixtures / stored things / point of use), the "use cleaning as inspection" continuity from Chapter 16, the light Toyota / original-method nod, and the planning-HOLD friction meter all match the manuscript, the canonical brief, and the HTML. The chapter correctly PLANS but cleans nothing new.

## Overlong social posts (measured, character/word counts recomputed, not trusted from the files)
- **X thread:** header states 14 posts; the file contains **14** posts, all at or under 280 characters INCLUDING the "N/" number line (**longest 276**, post 12, the assignments rule). Pass.
- **X short posts:** **10** standalone posts, all at or under 280 including the number line (**longest 273**, post 10, the meter HOLD). Pass.
- **LinkedIn:** **10** posts, each under 150 words of body copy (**longest 147**, post 8, "Let people choose"). Pass.
- **Facebook longform:** **381** words in the post body (within the 300 to 450 hard cap). Not a flag.

## Tone
- Correct platform-fit; the fairness-and-relief, anti-shame register holds everywhere, the planning-not-cleaning honesty is preserved, and the goal is kept honestly ahead (Shine has three chapters left; Safety, Standardize, and Sustain still follow).

## Formatting
- Clean Markdown. Both JSON files parse (`canonical/chapter-metadata.json`, `web/schema-org-article.json`); the publishable HTML carries one JSON-LD block that parses. CSV `workflow/asset-inventory.csv` has 7 columns and 52 data rows, all consistent (note: this is a pre-completion snapshot the orchestrator regenerates, but it is currently valid). The publishable HTML has 4 balanced `<figure>`/`</figure>` blocks and 4 balanced SVG figures; html/head/body/main all balance. The final HTML also carries 4 balanced SVGs.

## Friction-meter check (the chapter's defining beat)
- Verified in the SVG of both `chapter_17_final.html` and `chapter-17-publishable.html`: the LIVE needle is drawn from the pivot (210,198) to exactly (75,153), which is Chapter 16's first-Shine-step position, unmoved. The only new element versus Chapter 16 is a **dashed forward-projection arrow** (`stroke-dasharray`, path `M76 155 Q69 164 65.5 157.5` with an arrowhead) curving from the needle tip toward the GOAL crosshair at (67,155) on the green calm side, labeled "projected next." A slate "HOLDS · PLANNING" marker labels the held position; the Straighten-complete tick sits just behind and the Sort-complete milestone further back. This reads as a principled HOLD, not a new step, and matches the frozen caption exactly.

## Recommended edits before publishing
1. Author approval of the authored chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-17-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read the free chapter" / "Read it free online").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (one cleaned launch pad amid a house of unnamed targets with blank name-tags) and the Shine-list illustration (the four kinds, a name on every line).
