# Production Checklist: Chapter 8 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the authored chapter (signature, manuscript, final HTML) is approved by the author. This chapter was authored, not supplied. Review it before building anything for publication.
- [ ] Confirm the live chapter URL and slug (`sort-remove-what-does-not-belong`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL, dates) in `web/schema-org-article.json`, the `pdf-ebook/` files, and `chapter-08-publishable.html`.

## Phase 1: Canonical lock
- [ ] Title, subtitle, the One Question wording, the purpose sentence carried from Chapter 7, and "One Idea to Keep" match the approved chapter exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final HTML wording.
- [ ] The worked-pass item lists (belongs here vs belongs somewhere else) match the chapter exactly.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous (Chapter 7) and next (Chapter 9) navigation. Note this opens Part 3.
- [ ] Confirm the og:image (the One Question gate or the moved friction meter) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] The run-your-first-pass CTA appears in the highest-traffic posts.

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced (a hand carrying an item out of the drop zone, the surface getting lighter, the needle stepping toward calm).
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] The One Question graphic produced to spec (the gate splitting belongs here from a better home).
- [ ] The worked-pass diagram produced (belongs here vs belongs somewhere else, or a before-and-after of the surface).
- [ ] The moved friction meter produced, and it looks visibly different from the four held chapters (needle stepped toward calm, goal crosshair still ahead).
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
- [ ] No payoff word (lighter, belongs, space, gone) leaned on too hard; usage stays varied.
- [ ] Scope holds: sorts by belonging, not by need. No red tags, no holding-area system, no donate/sell/discard decisions. "A better home" means where the item lives now.
- [ ] All facts trace back to the final HTML. Inferences are labeled.

## Phase 9: Publishable HTML
- [ ] Open `chapter-08-publishable.html` in a browser and confirm it renders (fonts, the four SVG figures, the moved friction meter, all figures).
- [ ] Replace the domain, author, date, and og:image placeholders in its head.
- [ ] Validate the embedded JSON-LD.

## Phase 10: Companion resources
- [ ] The One Question card produced (printable plus phone wallpaper), wording verbatim.
- [ ] The First Sort Pass sheet produced (two columns for one space).
- [ ] Both linked from the chapter page and the highest-traffic CTAs.

## Phase 11: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
- [ ] Confirm the four `review/` files are finalized before Day 1.
