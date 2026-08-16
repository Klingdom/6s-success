# Production Checklist: Chapter 9 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the authored chapter (signature, manuscript, final HTML) is approved by the author. This chapter was authored, not supplied. Review it before building anything for publication.
- [ ] Confirm the live chapter URL and slug (`necessary-vs-unnecessary`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL, dates) in `web/schema-org-article.json`, the `pdf-ebook/` files, and `chapter-09-publishable.html`.

## Phase 1: Canonical lock
- [ ] Title, subtitle, the Use Test wording, "useful is not the same as used," the "would you buy it again?" follow-up, the definition box, and "One Idea to Keep" match the approved chapter exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final HTML wording.
- [ ] The drop-zone basket item lists (necessary vs unnecessary) match the chapter exactly.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous (Chapter 8) and next (Chapter 10) navigation. Note this is the second chapter of Part 3.
- [ ] Confirm the og:image (the Use Test branch or the friction meter's second step) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] The run-one-Use-Test CTA appears in the highest-traffic posts.

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced (a basket of entryway items, one thing being set into an out box, the duplicates sweep, the needle taking a smaller second step).
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] The Use Test graphic produced to spec (the question branching to necessary and to the out box, with the "would you buy it again?" side gate).
- [ ] The duplicates sweep diagram produced (five identical bags collapsing to one kept, the rest to the out box).
- [ ] The friction meter's second step produced, and it reads as a smaller move than Chapter 8 (Chapter 8's position now the dashed ghost, live needle a little further toward calm, goal crosshair still ahead).
- [ ] 10 quote cards designed, quotes verbatim, attribution correct.
- [ ] Image-generation prompts reviewed so outputs do not look generic.

## Phase 7: Print
- [ ] Chapter PDF front matter set.
- [ ] Ebook description and sales copy final, no hype, no false claims.
- [ ] Back-cover placeholders replaced with real, permissioned quotes (or removed).
- [ ] Discussion questions reviewed for book-club use.

## Phase 8: Quality gate (see review/ folder)
- [ ] Editorial review actioned.
- [ ] Brand-voice check passed.
- [ ] Reuse-risk check passed.
- [ ] No em dashes, no en dashes, no spaced hyphen used as a separator (run a find for each). Labels use the middot.
- [ ] No banned force or hype words used.
- [ ] No payoff word (used, necessary, just in case, surplus, lighter, crowd) leaned on too hard; usage stays varied and capped per the brief.
- [ ] Scope holds: sorts by need, not by belonging. No re-asking whether a thing belongs, no red tags or holding-area system, no second-thoughts handling, no donate/sell/store/recycle/throw decisions, no storing by frequency. The out box is a set-aside spot, not a destination.
- [ ] All facts trace back to the final HTML. Inferences are labeled.

## Phase 9: Publishable HTML
- [ ] Open `chapter-09-publishable.html` in a browser and confirm it renders (fonts, the four SVG figures, the friction meter's second-step state, all figures).
- [ ] Replace the domain, author, date, and og:image placeholders in its head.
- [ ] Validate the embedded JSON-LD.

## Phase 10: Companion resources
- [ ] The Use Test card produced (printable plus phone wallpaper), wording verbatim (the one question, "useful is not the same as used," and the "would you buy it again?" follow-up).
- [ ] The Necessary vs. Unnecessary sheet produced (two columns, what you actually use vs what you were keeping just in case, for one space).
- [ ] Both linked from the chapter page and the highest-traffic CTAs.

## Phase 11: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
- [ ] Confirm the four `review/` files are finalized before Day 1.
