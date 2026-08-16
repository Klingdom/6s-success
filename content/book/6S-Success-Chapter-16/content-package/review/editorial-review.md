# Editorial Review: Chapter 16 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting. This review reports only checks actually run; every count below was measured with LC_ALL=C scans, and every cited noun or quote was grep-verified present in the manuscript or final HTML before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the 6S source "Principles of 6S: Shine Step," no verbatim source file supplied). The package holds the warm, permission-and-relief, anti-shame voice across all channels, the facts trace cleanly to the manuscript and HTML, and the hooks are concrete (the arranged-but-unread launch pad under a faint haze, "Don't just clean it. Read it," and the umbrella-stand rust caught early). Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the rule, the definition of Shine, the not-spotless reframe, the two-jobs-of-a-wipe image, the launch-pad first pass, the first-Shine-step meter) is by design and staggered by the calendar.
- The hero vocabulary runs high ("clean," "surface," "see," "read," "inspect," "notice"), because it is the subject, not a tic. When excerpting, vary the surrounding language so a single post does not stack "honest," "small," and "care."

## AI-sounding phrasing
- None found. The writing leans on concrete images (the shelf that comes away damp at one end, the base sitting in a shallow ring of rainwater, the hook that gives a little) rather than generic filler.
- Widened dash scan clean (em, en, spaced-hyphen-as-punctuation, and dash HTML entities all **zero**). No hype words in any asset.

## Unsupported claims
- No invented statistics, names, or dates. Total Productive Maintenance is referenced lightly and home-scaled ("At home it does not need a name"); the origin is tied to the factory floor / the original method, not overclaimed.
- The "attack"/"blitz"/"purge" tokens flagged by the force-metaphor scan are confined to negated production/scope notes (`canonical/chapter-cta.md`, `video-audio/b-roll-and-visual-notes.md`, `workflow/repurposing-map.md`); no reader-facing copy uses them.
- Every "spotless" (117 occurrences) is a negated non-goal, never an aspiration.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the finished-but-unread launch pad under a faint film with problem-sparks hidden beneath it, "Don't just clean it. Read it," "Spotless is not the target and never was. Seen is the target," and the umbrella-stand-rust / loose-hook catch.

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (pick one surface you use every day, clean it properly once, and look at what the cleaning uncovers) is concrete and free. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. The Shine principle "use cleaning as inspection," the "abnormal conditions are easy to spot" benefit, the three Shine steps (targets/assignments → methods → initial cleaning-and-inspection), the light TPM / Toyota nod, the launch-pad first pass, and the FIRST SHINE STEP friction move all match the manuscript, the canonical brief, and the HTML.

## Overlong social posts (measured, character/word counts recomputed, not trusted from the files)
- **X thread:** header states 14 posts; the file contains **14** posts, all at or under 280 characters INCLUDING the "N/" number line (**longest 273**, post 11, the launch-pad first pass). Pass.
- **X short posts:** **10** standalone posts, all at or under 280 including the number line (**longest 271**, post 2). Pass.
- **LinkedIn:** **10** posts, each under 150 words of body copy (**longest 144**, post 1). Pass.
- **Facebook longform:** **409** words in the post body (within the 300 to 450 hard cap). Not a flag.

## Tone
- Correct platform-fit; the permission-and-relief, anti-shame, honest-first-step register holds everywhere, and the goal is kept honestly ahead (Shine has only begun; Safety, Standardize, and Sustain still follow).

## Formatting
- Clean Markdown. Both JSON files parse (`canonical/chapter-metadata.json`, `web/schema-org-article.json`); the publishable HTML carries one JSON-LD block that parses. CSV `workflow/asset-inventory.csv` has 7 columns and 49 data rows, all consistent (note: this is a pre-completion snapshot the orchestrator regenerates, but it is currently valid). The publishable HTML has 4 balanced `<figure>`/`</figure>` blocks and 4 balanced SVG figures; html/head/body/main all balance. The final HTML also carries 4 balanced SVGs.

## Recommended edits before publishing
1. Author approval of the authored chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-16-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Free online" / "Read the free chapter").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (arranged launch pad under a haze with hidden problem-sparks) and the two-jobs-of-a-wipe illustration.
