# Editorial Review: Chapter 7 Content Package

Reviewed against the brief's checklist: repetition, AI-sounding phrasing, unsupported claims, weak hooks, unclear CTAs, missing source alignment, overlong social posts, tone mismatch, formatting.

## Overall verdict
Publish-ready, with one standing caveat: the chapter itself is a draft. The package holds the author's warm, encouraging, non-prescriptive voice across all channels, the facts trace cleanly to the authored final HTML and manuscript, and the hooks are concrete (decide before you sort, the everything-space, three jobs in a trench coat). The full validation pass is clean. Findings below are minor polish, not blockers.

## Standing caveat: the chapter is a draft
Chapter 7 had no supplied source files. The signature, manuscript, and final HTML were authored in the established book voice and design, then packaged. Everything here is faithful to that draft, but the draft is awaiting author approval. If the author revises the chapter (especially the Purpose Statement template or the One Job Beats Five framing), refresh the canonical layer and re-run the affected packages.

## Repetition
- Cross-asset repetition of the spine (a space cannot be good at everything, decide the one job before sorting, the yardstick question, the everything-space, the Purpose Statement template) is by design and acceptable.
- Watch same-day overlap of the "a space cannot be good at everything" line and the "three jobs in a trench coat" line, which open several assets. The calendar staggers these. Keep that spacing.
- Soft-CTA wording is the most repeated element across LinkedIn and X. Rotate the five phrasings in `canonical/chapter-cta.md` so sign-offs do not read as a template.

## AI-sounding phrasing
- No banned filler found. The widened dash scan (em dash, en dash, and spaced-hyphen " - " separators) is clean across all files. No hype words ("unlock," "leverage," "seamless," "elevate," "supercharge," and the rest) appear anywhere.
- The voice reads human. Concrete nouns (mail, keys, chargers, the umbrella that stays, the read magazines that go) carry the writing, not abstractions.

## Unsupported claims
- No invented statistics, names, or dates. The argument is logical, not empirical: a space asked to do five jobs is good at none. It is framed as the author's plain observation, which is how the chapter presents it.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.

## Hooks
- Strong and specific. "Before you decide what stays and what goes, decide what the space is for," "the space is messy because it is failing to be any one thing," and "three jobs in a trench coat" all open on a concrete image or a sharp claim.
- "A space cannot be good at everything" is the single most quotable, shareable line in this chapter and is used well as a social lead.

## CTAs
- Every social post carries a soft CTA pointing to the chapter or the online book.
- The hero action (write your one-sentence purpose: "this space is for ___, so that ___") is concrete, free, and about five minutes, and it matches the chapter's calm, non-prescriptive tone.
- The reader stays the author of their own purpose. No asset dictates what a space is for. Good.
- Before publishing, replace "the online book" with the live URL or a tracked link.

## Source alignment
- Strong. The everything-space, the one-job rule, the Purpose Statement template, "match it to your real life not an ideal," purpose-sets-the-limits (the bouncer at the door), and the number/photo/purpose handoff all match the authored final HTML and manuscript.
- Canonical title and slug were pulled from the HTML title tag (Chapter 7, Define the Purpose of the Area).

## Overlong social posts
- X: 12-post thread plus 10 short posts; all at or under 280 characters (longest 263). Pass.
- LinkedIn: 10 posts, each under 150 words. Pass.
- Facebook: the longform post runs about 618 words, over the 300 to 450 target. It is still usable for Facebook, where longer reads perform, but trim toward 450 if you want it tighter. Same pattern flagged on Chapters 5 and 6. Not a blocker.

## Tone mismatch
- LinkedIn slightly more composed, Facebook warmer and looser, X clipped with contractions. Correct platform-fit, not drift. The encouraging, non-prescriptive voice survives everywhere.
- Sales and ebook copy stay honest and low-hype, which suits a chapter that decides rather than does.

## Formatting
- Clean Markdown throughout. Headings, lists, and tables render.
- Both JSON files (`canonical/chapter-metadata.json`, `web/schema-org-article.json`) parse as valid JSON. The asset inventory is valid CSV with all seven columns.
- The publishable HTML renders the full design including the four SVGs (opener, the One Job Beats Five device, the Purpose Statement template, and the friction meter) and its embedded JSON-LD validates. Tags are balanced.

## Recommended edits before publishing
1. Get author approval of the authored chapter first. Everything downstream depends on it.
2. Insert the real chapter URL in place of "the online book" wherever a CTA appears.
3. Replace author, publisher, URL, and date placeholders in the schema JSON, the PDF/ebook files, and `chapter-07-publishable.html`.
4. Rotate the LinkedIn and X CTA wording.
5. Replace or remove the back-cover testimonial placeholders before print.
6. Optionally trim the Facebook longform toward 450 words.
7. Produce the Purpose Statement template graphic first; it is the chapter's hero asset and lifts out as a standalone fill-in-the-blank card.
