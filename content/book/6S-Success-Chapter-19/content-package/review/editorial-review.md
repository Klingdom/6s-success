# Editorial Review: Chapter 19 Content Package

Reviewed against the checklist: repetition, AI-sounding phrasing, unsupported claims, hooks, CTAs, source alignment, overlong social posts, tone, formatting. This review reports only checks actually run; every count below was measured with LC_ALL=C scans (character and word counts recomputed, not trusted from the files), and every cited noun or quote was grep-verified present in the manuscript or final HTML before citing.

## Overall verdict
Publish-ready after author sign-off, with one standing caveat: the chapter is a draft (authored in the book voice, grounded in the 6S source "Principles of 6S: Shine Step," "perform initial cleaning and inspection" turned into a repeatable rhythm; no verbatim source file supplied). The package holds the warm, relief-and-permission, anti-shame voice across all channels, the facts trace cleanly to the manuscript and HTML, and the hooks are concrete (the one-time clean as a photograph while life is the film that drifts, "A little, often, together," and the timer as the whole device). Findings below are minor.

## Repetition
- Cross-asset repetition of the spine (the drift reframe, the 15-minute reset, the three levers short/shared/regular, the timer-as-device, the shared-reset arithmetic, the anchor-to-a-habit turn, the honest SHINE COMPLETE milestone) is by design and staggered by the calendar.
- The hero vocabulary runs high ("reset," "clean," "home," "timer," "rhythm," "baseline"), because it is the subject, not a tic. When excerpting, vary the surrounding language so a single post does not stack "little," "often," and "together."

## AI-sounding phrasing
- None found. The writing leans on concrete images (the mug on the counter, the beach filling with footprints, four people resetting after dinner, the kitchen drift gone in four minutes) rather than generic filler.
- Widened dash scan clean (em, en, spaced-hyphen-as-punctuation, and dash HTML entities all **0**; the lone raw " - " is inside a quoted description of the dash rule in `workflow/production-checklist.md` line 9, not a dash in use). No hype words in any asset.

## Unsupported claims
- No invented statistics, names, or dates. The 15-minute reset is taught as practical technique home-scaled from Seiso's "perform initial cleaning and inspection" made repeatable; the origin is not overclaimed beyond Toyota / the Toyota Production System. The "keeps conditions from reverting" idea is referenced lightly and correctly flagged as a Standardize benefit not built here.
- The "attack" / "war on dirt" / "blitz" / "blast" / "purge" tokens flagged by the force-metaphor scan are confined to negated production/scope notes (`canonical/chapter-cta.md`, `graphics/diagram-ideas.md`, `graphics/image-generation-prompts.md`, `video-audio/b-roll-and-visual-notes.md`, `workflow/repurposing-map.md`); no reader-facing copy uses them. "pull the trigger" is **0**.
- Every "spotless" (11 occurrences, all in production/editor notes across 7 files) is a negated non-goal, never an aspiration. No brand-name products are endorsed anywhere (the raw-substring flags on "Method," "Dawn," and "Cif" are false positives, resolved in the brand-voice check).
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific: the one-time clean drawn as a photograph while what you live in is the film that drifts, "A little, often, together," "Set the timer, and stop when it rings," and "fifteen minutes a day, and you get your weekends back."

## CTAs
- Every social post carries a soft CTA to the chapter or the online book. The hero action (tonight, set a timer for fifteen minutes, have everyone reset one zone at once, and stop when it rings) is concrete, free, and a one-evening proof. Rotate wording before publishing; insert the live URL for "the online book."

## Source alignment
- Strong. Shine step 3 ("perform initial cleaning and inspection") home-scaled into a repeatable rhythm; the reframe-from-Chapter-16, list-from-Chapter-17, and methods-from-Chapter-18 continuity (all USED in the reset, none re-taught); the light Seiso / Toyota nod; and the SHINE COMPLETE milestone all match the manuscript, the canonical brief, and the HTML. The chapter correctly completes Shine and hands the state-of-the-room-to-the-people-in-it turn to Part Six (Safety, Chapter 20).

## Overlong social posts (measured, character/word counts recomputed, not trusted from the files)
- **X thread:** header states 14 posts; the file contains **14** posts, all at or under 280 characters INCLUDING the "N/" number line (**longest 279**, tied by post 7, the timer-as-device, and post 12, the shared-reset arithmetic). Pass.
- **X short posts:** **10** standalone posts, all at or under 280 including the number line (**longest 271**, post 9, "get your weekends back"). Pass.
- **LinkedIn:** **10** posts, each under 150 words of body copy (**longest 135**, post 7, "The arithmetic of sharing it out"). Pass.
- **Facebook longform:** **394** words in the post body (within the 300 to 450 hard cap). Not a flag.

## Tone
- Correct platform-fit; the relief-and-permission, anti-shame register holds everywhere, the light-habit-not-a-standard honesty is preserved, and the goal is kept honestly ahead (Shine completes here; Safety, Standardize, and Sustain still follow). The earned-accomplishment note of closing an S stays quiet and never becomes a victory lap.

## Formatting
- Clean Markdown. Both JSON files parse (`canonical/chapter-metadata.json`, `web/schema-org-article.json`); the publishable HTML carries one JSON-LD block that parses (`@type` Article). CSV `workflow/asset-inventory.csv` has 7 columns and 52 data rows (53 rows including the header), all consistent (note: this is a pre-completion snapshot the orchestrator regenerates, but it is currently valid). The publishable HTML has 4 balanced `<figure>`/`</figure>` blocks and 4 balanced SVG figures; html/head/body/main all balance (the raw `<head` count of 2 is `<head>` plus `<header>`). The final HTML also carries 4 balanced SVGs.

## Friction-meter check (the chapter's defining beat)
- Verified in the SVG of both `chapter_19_final.html` and `chapter-19-publishable.html`: the LIVE needle is drawn from the pivot (210,198) to exactly (71,154), a calmer step past Chapter 18's position toward the GOAL, and it lands on a clearly MARKED "Shine complete" tick, the THIRD milestone on the dial after Sort complete and Straighten complete. A slate **SHINE COMPLETE** marker labels the reached position; there is **NO "SHINE · STEP 2" step label** and **NO "HOLDS" or "PLANNING" marker** anywhere in the SVG (the words "holds" and "planning" appear only in reader prose describing Chapter 17's earlier "planning hold," not as dial markers). Chapter 18's position (73,153.5) is now the **dashed ghost** just behind the live needle (`stroke-dasharray="5 5"`, opacity 0.6, labeled "Ch 18 ghost"); Chapters 16/17 (75,153) are a fainter dashed ghost behind that; the Straighten-complete milestone tick (~81,150) and, furthest back, the Sort-complete milestone tick (~128,102 leader) sit as passed markers. The GOAL crosshair (tagged PURPOSE) sits at (67,155) on the green calm side, still AHEAD of the live needle at (71,154) with the gap preserved (Safety, Standardize, and Sustain remain). This reads as a genuine, earned milestone (three of six S's done), NOT as arriving, and the figure caption matches the frozen caption exactly in both HTMLs.

## Recommended edits before publishing
1. Author approval of the authored chapter first.
2. Insert the real chapter URL for "the online book."
3. Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and `chapter-19-publishable.html`.
4. Rotate the LinkedIn and X CTA wording (several close on "Read it free online" / "Read the free chapter in the online book").
5. Replace or remove the back-cover testimonial placeholders.
6. Lead the visual production with the opener (the freshly cleaned home beginning to drift) and the reset-in-action figure (the whole household at 15:00).
