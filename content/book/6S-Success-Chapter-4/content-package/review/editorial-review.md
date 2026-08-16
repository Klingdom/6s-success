# Editorial Review: Chapter 4 Content Package

Reviewed against the brief's checklist: repetition, AI-sounding phrasing, unsupported claims, weak hooks, unclear CTAs, missing source alignment, overlong social posts, tone mismatch, formatting.

## Overall verdict
Publish-ready after the small fix already applied, with one standing caveat: the chapter itself is a draft. The package holds the author's warm, anti-overwhelm voice across all channels, the facts trace cleanly to the drafted final HTML, and the hooks are concrete (the tempting garage, guilt vs friction, the First Target Map). Findings below are minor polish, not blockers.

## Standing caveat: the chapter is a draft
Chapter 4 had no source files. The signature, manuscript, and final HTML were drafted in the established book voice and design, then packaged. Everything here is faithful to that draft, but the draft is awaiting author approval. If the author revises the chapter (especially the First Target Map device or the quadrant names), refresh the canonical layer and re-run the affected packages.

## Repetition
- Cross-asset repetition of the spine (the tempting garage, proof not the room, guilt vs friction, the First Target Map, write it down) is by design and acceptable.
- Watch same-day overlap of the garage hook and the "you failed at choosing" line, which open several assets. The calendar staggers these. Keep that spacing.
- Soft-CTA wording is the most repeated element across LinkedIn and X. Rotate three or four phrasings from `canonical/chapter-cta.md` so sign-offs do not read as a template.

## AI-sounding phrasing
- No banned filler found in the final copy. The word "transform" does not appear at all (the chapter title does not contain it, unlike Chapter 3).
- Em dash, en dash, and spaced-hyphen (" - ") separator scan: clean across all 56 files. (Markdown list bullets and the scorecard's subtraction math are not separators and are left as is.) One X thread post ran to 290 characters and was trimmed to about 258.
- The voice reads human. Concrete nouns (a wall of bins, one cup of coffee, a kitchen catch-all drawer, the keys and mail by the door) carry the writing.

## Unsupported claims
- No invented statistics, names, or dates. The First Target Map, the Target Scorecard numbers, and the garage rationale all come from the drafted chapter.
- Testimonials in `pdf-ebook/back-cover-copy.md` are clearly marked placeholders.
- The Target Scorecard example numbers (kitchen drawer +3, entryway +3, bathroom +2, linen closet -1, garage -2) are an illustrative worked example from the chapter, not a claim about any real home. Treat them as a sample.

## Hooks
- Strong and specific. "You did not fail at organizing. You failed at choosing," the tempting garage, "guilt is a terrible compass," and "should you start with the garage" all open on a concrete image or a sharp claim.
- "Should you start with the garage? Probably not" is the single most clickable line in this chapter and is used well as an Open Graph variant and a social hook.

## CTAs
- Every social post carries a soft CTA pointing to the chapter or the online book.
- The hero action (score your spaces, pick one, write it down) is concrete and free, and it matches the chapter's anti-overwhelm goal.
- Before publishing, replace "the online book" with the live URL or a tracked link.

## Source alignment
- Strong. The two questions, the sweet spot (high friction, low effort), the garage takedown, the three filters, the scorecard math, and the write-it-down close all match the drafted final HTML.
- Canonical title and slug were pulled from the HTML title tag.

## Overlong social posts
- X: thread and short posts checked. One post was 290 characters and was trimmed; all are now within 280.
- LinkedIn: 10 posts each under 150 words. Pass.
- Facebook: conversational length, appropriate.

## Tone mismatch
- LinkedIn slightly more composed, Facebook warmer and looser, X clipped with contractions. Correct platform-fit, not drift. The anti-overwhelm voice survives everywhere.
- Sales and ebook copy stay honest and low-hype, which suits a choosing chapter.

## Formatting
- Clean Markdown throughout. Headings, lists, and tables render.
- Both JSON files parse as valid JSON. The asset inventory is valid CSV with all seven columns.
- The publishable HTML renders the full design including the First Target Map and Target Scorecard SVGs and the aimed friction meter, and its embedded JSON-LD validates.

## Recommended edits before publishing
1. Get author approval of the drafted chapter first. Everything downstream depends on it.
2. Insert the real chapter URL in place of "the online book" wherever a CTA appears.
3. Replace author, publisher, URL, and date placeholders in the schema JSON, the PDF/ebook files, and `chapter-04-publishable.html`.
4. Rotate the LinkedIn and X CTA wording.
5. Replace or remove the back-cover testimonial placeholders before print.
6. Produce the First Target Map graphic first; it is the chapter's hero asset and a reusable decision tool.
