# Production Checklist: Chapter 10 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the authored chapter (signature, manuscript, final HTML) is approved by the author. This chapter was authored, not supplied. Review it before building anything for publication.
- [ ] Confirm the live chapter URL and slug (`red-tags-holding-areas-and-sorters-remorse`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL, dates) in `web/schema-org-article.json`, the `pdf-ebook/` files, and `chapter-10-publishable.html`.

## Phase 1: Canonical lock
- [ ] Title, subtitle, the red-tag wording (what it is, date tagged, decide-by date), "a maybe is not a failure of nerve," "a holding area without a deadline is just a nicer junk pile," the definition box, and "One Idea to Keep" match the approved chapter exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final HTML wording.
- [ ] The entryway-maybes example (the gift umbrella, the folding poncho) matches the chapter exactly, including each decide-by window.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous (Chapter 9) and next (Chapter 11) navigation. Note this is the third chapter of Part 3.
- [ ] Confirm the og:image (the red tag close-up or the friction meter holding) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] The red-tag-one-maybe CTA appears in the highest-traffic posts.

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced (a red tag being filled out and tied on, a labeled holding-area bin with two tagged items, a decide-by date on a timeline, the needle holding steady with a faint dashed arrow ahead).
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] The Red Tag graphic produced to spec (three labeled lines, "what it is," "date tagged," "decide-by," branching to "reached for it, keep" and "date passed, untouched, out box").
- [ ] The holding-area timeline diagram produced (tagged items entering, the decide-by marker, and the two exits at the deadline).
- [ ] The friction meter's hold state produced, and it reads as a deliberate hold, not a move and not a backslide (live needle exactly where Chapter 9 left it, a faint dashed forward arrow to the projected next step, goal crosshair still ahead on the green side).
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
- [ ] No payoff word (red tag, holding area, decide-by date, maybe, remorse, regret) leaned on too hard; usage stays varied and capped per the brief.
- [ ] Scope holds: handles only the honest maybes and the second thoughts. No re-teaching the Use Test, no re-litigating necessary vs. unnecessary, no routing the out box or expired-tag items to a destination, no storing keepers by frequency. The holding area is a time-boxed limbo, not a storage scheme.
- [ ] All facts trace back to the final HTML. Inferences are labeled.

## Phase 9: Publishable HTML
- [ ] Open `chapter-10-publishable.html` in a browser and confirm it renders (fonts, the four SVG figures, the friction meter's hold state with the dashed forward arrow, all figures).
- [ ] Replace the domain, author, date, and og:image placeholders in its head.
- [ ] Validate the embedded JSON-LD.

## Phase 10: Companion resources
- [ ] The Red Tag produced (printable tags, several to a sheet), wording verbatim (what it is, date tagged, decide-by date).
- [ ] The Holding Area card produced (printable: how to set up a time-boxed holding area, pick a decide-by date by item type, and honor it).
- [ ] Both linked from the chapter page and the highest-traffic CTAs.

## Phase 11: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
- [ ] Confirm the four `review/` files are finalized before Day 1.
