# Production Checklist: Chapter 2 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the three source files are final: signature, manuscript, final HTML.
- [ ] Confirm the live chapter URL and slug (`what-is-6s`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL) in `web/schema-org-article.json` and `pdf-ebook/` files.

## Phase 1: Canonical lock
- [ ] Title, subtitle, and definition match the live book exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final manuscript wording.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous/next chapter navigation.
- [ ] Confirm the og:image (bottle-opener drawer) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] Each post reads as useful on its own.

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced.
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] Infographic produced to spec, both portrait and landscape.
- [ ] 10 quote cards designed, quotes verbatim, attribution correct.
- [ ] Diagrams produced or adapted from the book's existing SVGs.
- [ ] Image-generation prompts reviewed so outputs do not look generic.

## Phase 7: Print
- [ ] Chapter PDF front matter set.
- [ ] Ebook description and sales copy final, no hype, no false claims.
- [ ] Back-cover testimonial placeholders replaced with real, permissioned quotes (or removed).
- [ ] Discussion questions reviewed for book-club use.

## Phase 8: Quality gate (see review/ folder)
- [ ] Editorial review actioned.
- [ ] Brand-voice check passed.
- [ ] Reuse-risk check passed (no overexposed single line across same-day posts).
- [ ] No em dashes anywhere (run a find for the character).
- [ ] No banned words used as filler.
- [ ] All facts trace back to the chapter. Inferences are labeled.

## Phase 9: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
