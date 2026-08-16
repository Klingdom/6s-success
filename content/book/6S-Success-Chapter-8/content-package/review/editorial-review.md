# Editorial Review: Chapter 8 Content Package

Reviewed against the brief's checklist: repetition, AI-sounding phrasing, unsupported claims, weak hooks, unclear CTAs, source alignment, overlong social posts, tone mismatch, formatting. Every quoted line and named object below was grep-verified in `chapter_08_manuscript.md` before being cited here. Every count below was measured, then written.

## Overall verdict
Publish-ready, with one standing caveat: the chapter itself is a draft. The package holds the warm, non-prescriptive, anti-shame voice across all channels, the facts trace cleanly to the authored manuscript and final HTML, and the hooks are concrete (sort before you shop, the occupancy problem, one question, the needle finally moves). The validation pass is clean. Findings below are minor polish, not blockers.

## Standing caveat: the chapter is a draft
Chapter 8 had no supplied source files. The signature, manuscript, and final HTML were authored in the established book voice and design, then packaged. Everything here is faithful to that draft, but the draft is awaiting author approval. If the author revises the chapter (especially the One Question, the worked drop-zone pass, or the friction-meter caption), refresh the canonical layer and re-run the affected packages.

## Repetition
- Cross-asset repetition of the spine (Sort is the first S, separate then remove, the One Question, belongs here / belongs somewhere else, the needle moves partway) is by design and acceptable.
- The word "belongs" recurs heavily (about 25 times in the manuscript, counted). It is the frozen outcome vocabulary, so it is intended, but keep any single social post from stacking it repeatedly.
- Soft-CTA wording is the most repeatable element across LinkedIn and X. The bank in `canonical/chapter-cta.md` holds six phrasings (counted). Rotate them so sign-offs do not read as a template.

## AI-sounding phrasing
- No banned filler found. The widened dash scan (em dash, en dash, and spaced-hyphen " - " separators, excluding list bullets) was run across all 52 package files plus the manuscript and both HTML files and returned zero matches. A hype-word scan ("unlock," "leverage," "seamless," "elevate," "supercharge," "delve," "dive in," "in conclusion," "fast-paced," "in today's," and the rest) returned zero hits across the package.
- The voice reads human. Concrete nouns (keys, the dog's leash, the umbrella, a phone charger, a stray screwdriver, junk mail, a coin-collecting decorative bowl) carry the writing, not abstractions.

## Unsupported claims
- No invented statistics, names, or dates. The Toyota origin note ("Sort is the English name for Seiri") is kept to one sentence and does not overclaim; "Seiri" is present in the manuscript (verified).
- The one empirical-sounding callback, the "14 out of 30" audit score, matches the number carried from Chapter 5 and is present in the manuscript (verified).
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders ("PLACEHOLDERS · do not publish as real quotes"), with bracketed replace-before-print instructions and no invented attributions.

## Hooks
- Strong and specific. "The clutter is not a filing problem. It is an occupancy problem" and "Does this help the space do its job?" open on a sharp claim or a usable tool (both verbatim).
- The landmark hook, "for the first time in this entire book, it has something to report," is the most distinctive lead in the chapter and is used well in the thread and the LinkedIn "needle finally moves" post.

## CTAs
- Every social post carries a soft CTA pointing to the chapter or the online book.
- The hero action (run a Sort pass, even a one-object pass) is concrete, free, and about five minutes, and it matches the chapter's calm tone. The "Quick Win" and "Family Challenge" callouts give a smaller and a family-sized version.
- The reader stays the author of their own decisions. No asset dictates what to keep or discard. Good.
- Before publishing, replace "the online book" with the live URL or a tracked link. The string "online book" appears in 19 package files (counted).

## Source alignment
- Strong. The One Question, the two-column worked pass (keys, mail, sunglasses, leash, bag, umbrella, tray on the "belongs here" side; magazines, junk mail, charger, homework, screwdriver, sweater, bowl on the "belongs somewhere else" side), "Sort by address, not by fate," the "you are only deciding it does not live here" reassurance, and the friction-meter first move all match the authored manuscript and final HTML.
- The frozen friction-meter caption ("The needle moves for the first time. Nothing was bought and nothing was cleaned...") is present byte-identical in both `chapter_08_final.html` and `chapter-08-publishable.html` (verified).
- Scope discipline holds: no disposal instruction ("toss," "trash," "throw out") leaked into the canonical, X, or LinkedIn assets (scan run, zero hits). The Chapter 9 handoff ("Next we sort by need") is set up but not answered.

## Overlong social posts (measured, not estimated)
- **X thread:** 15 posts (header says 15, counted 15). I measured each post body; all are at or under 280 characters. Longest is post 10 at 275 characters. Pass. Note: the in-file "(approx. NNN chars)" annotations run a few characters low against my actual count (for example post 10 is labeled 271 but measures 275); still within limit, but treat my measured numbers as authoritative.
- **X short posts:** 10 posts, all at or under 280. Longest is post 1 at 261. Pass.
- **LinkedIn:** 10 posts, each under 150 words. Longest is post 8 ("Park the maybes") at 107 words (measured). Pass.
- **Facebook longform:** the post body measures 430 words (measured), inside the 300 to 450 target. This is the recurring overrun from Chapters 5 to 7 (which ran near 600) now fixed. Good, not a flag.

## Tone mismatch
- LinkedIn slightly more composed, Facebook warmer and first-person, X clipped with contractions. Correct platform-fit, not drift. The non-prescriptive, anti-shame voice survives everywhere.
- Sales and ebook copy stay honest and low-hype, which suits a chapter whose claim is modest and true (remove what does not belong and most of the mess leaves before you buy a bin).

## Formatting
- Clean Markdown throughout. Headings, lists, and tables render.
- Both JSON files (`canonical/chapter-metadata.json`, `web/schema-org-article.json`) parse as valid JSON (checked). The asset inventory is valid CSV with all seven columns and 56 data rows, no ragged rows (checked).
- The publishable HTML renders the full design including exactly four inline SVGs (opener, the One Question gate, the worked pass, and the moved friction meter) and its single embedded JSON-LD block validates (checked). Structural tags balance: div 15/15, section 1/1, svg 4/4, head/body/html/script/style all 1/1.

## Recommended edits before publishing
1. Get author approval of the authored chapter first. Everything downstream depends on it.
2. Insert the real chapter URL in place of "the online book" wherever a CTA appears (19 files).
3. Replace author, publisher, URL, and date placeholders in the schema JSON, the PDF/ebook files, and `chapter-08-publishable.html`.
4. Rotate the six LinkedIn and X CTA phrasings.
5. Replace or remove the three back-cover testimonial placeholders before print.
6. Optionally correct the X thread's "(approx.)" annotations to the measured character counts.
7. Produce the One Question card first; it is the chapter's hero standalone asset and lifts out as a printable and phone wallpaper.
