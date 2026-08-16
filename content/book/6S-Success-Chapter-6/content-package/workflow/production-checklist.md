# Production Checklist: Chapter 6 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the authored chapter (signature, manuscript, final HTML) is approved by the author. This chapter was authored, not supplied. Review it before building anything for publication.
- [ ] Confirm the live chapter URL and slug (`photograph-before-you-fix`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL, dates) in `web/schema-org-article.json`, the `pdf-ebook/` files, and `chapter-06-publishable.html`.

## Phase 1: Canonical lock
- [ ] Title, subtitle, and "One Idea to Keep" match the approved chapter exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final HTML wording.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous (Chapter 5) and next (Chapter 7) navigation. Note this is Part 2.
- [ ] Confirm the og:image (the Eye vs the Camera split or the phone photographing the drop zone) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] The take-the-before-photo CTA appears in the highest-traffic posts.
- [ ] Privacy is respected in every post (never imply the reader must post their mess).

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced (a phone photographing a drop zone, a floor mark, a before/after pair).
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] The Eye vs the Camera split produced to spec (soft green wash left, sharp red sparks right).
- [ ] The Matched Pair diagram produced, with the floor mark and the four rules.
- [ ] 10 quote cards designed, quotes verbatim, attribution correct.
- [ ] Image-generation prompts reviewed so outputs do not look generic.

## Phase 7: Print
- [ ] Chapter PDF front matter set.
- [ ] Ebook description and sales copy final, no hype, no false claims.
- [ ] Back-cover testimonial placeholders replaced with real, permissioned quotes (or removed).
- [ ] Discussion questions reviewed for book-club use.

## Phase 8: Quality gate (see review/ folder)
- [ ] Editorial review actioned.
- [ ] Brand-voice check passed.
- [ ] Reuse-risk check passed.
- [ ] No em dashes anywhere (run a find for the character).
- [ ] No banned words used as filler.
- [ ] All facts trace back to the final HTML. Inferences are labeled.

## Phase 9: Publishable HTML
- [ ] Open `chapter-06-publishable.html` in a browser and confirm it renders (fonts, the Eye vs the Camera and Matched Pair SVGs, the friction meter, all figures).
- [ ] Replace the domain, author, date, and og:image placeholders in its head.
- [ ] Validate the embedded JSON-LD.

## Phase 10: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
