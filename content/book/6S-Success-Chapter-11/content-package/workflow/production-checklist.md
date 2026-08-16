# Production Checklist: Chapter 11 Content Package

Work top to bottom. Check each item before it goes live.

## Phase 0: Source confirmation
- [ ] Confirm the authored chapter (signature, manuscript, final HTML) is approved by the author. This chapter was authored, not supplied. Review it before building anything for publication.
- [ ] Confirm the live chapter URL and slug (`what-to-donate-sell-store-recycle-or-throw-away`).
- [ ] Confirm the book title, author name, and publisher for attribution lines.
- [ ] Replace all placeholders (author, publisher, URL, dates) in `web/schema-org-article.json`, the `pdf-ebook/` files, and `chapter-11-publishable.html`.

## Phase 1: Canonical lock
- [ ] Title, subtitle, the five door names (Donate, Sell, Store, Recycle, Throw), "Donate is the default," the sell trap line, the store trap line, the throw reframe, the definition box, and "One Idea to Keep" match the approved chapter exactly.
- [ ] `chapter-metadata.json` is valid JSON and dates are correct.
- [ ] Quotes in `chapter-quotes.md` still match the final HTML wording.
- [ ] The entryway routing example (two umbrellas to Donate, tote bags to Donate with worn ones to Recycle, takeout menus to Recycle, dead cable to Recycle as e-waste, sold-car key to Recycle or Throw) matches the chapter exactly.

## Phase 2: Web
- [ ] Pick the SEO title and meta description (from the 5 options each).
- [ ] Validate `schema-org-article.json` in a structured-data testing tool.
- [ ] Set canonical URL, Open Graph image, and Twitter card.
- [ ] Wire up previous (Chapter 10) and next (Chapter 12) navigation. Note this is the fourth and final chapter of Part 3, and it hands off to Part 4, Straighten.
- [ ] Confirm the og:image (the five doors, or the friction meter at Sort complete) is produced and sized 1200x630.

## Phase 3: Social text
- [ ] LinkedIn: article, 10 posts, carousel, newsletter, comment prompts proofed.
- [ ] Facebook: 5 posts, longform, group post proofed.
- [ ] X: thread and 10 short posts checked for length (under 280 each).
- [ ] Every post has a soft CTA pointing to the live URL.
- [ ] The route-three-things CTA appears in the highest-traffic posts.

## Phase 4: Email
- [ ] Choose subject line and matching preview text.
- [ ] Insert the real chapter link in the newsletter and teaser.
- [ ] Send yourself a test, check rendering and the CTA button.

## Phase 5: Video and audio
- [ ] YouTube script timed at 6 to 8 minutes on a read-through.
- [ ] Podcast script timed at 8 to 12 minutes.
- [ ] 5 short scripts each fit 30 to 90 seconds.
- [ ] Teleprompter script loaded and font-sized for reading.
- [ ] B-roll shot list gathered or sourced (the out box by the door, a donation bag going into a car, items sorting toward five labeled doors, the sell and store doors sitting narrow and nearly empty, the needle stepping to the Sort-complete mark).
- [ ] Captions and lower-thirds drafted.

## Phase 6: Slides and graphics
- [ ] Teaching deck built from the outline, on-brand (Fraunces, Newsreader, warm palette).
- [ ] LinkedIn carousel laid out from the copy file.
- [ ] The Five Doors Out graphic produced to spec (five labeled doors, Donate drawn as the wide default lane, Sell and Store as narrow side doors, the quick routing cascade).
- [ ] The routing-pass diagram produced (the specific out-box items mapped to doors, with a small tally showing Donate and Recycle taking the whole box).
- [ ] The friction meter's Sort-complete state produced, and it reads as a real milestone move that finishes the first S, not as reaching the final goal (live needle stepped to the Sort-complete tick, Chapter 10's held position now a dashed ghost, goal crosshair still ahead on the green side).
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
- [ ] No payoff word (Donate, fast, gone, out of the house, someday) leaned on too hard; usage stays varied and capped per the brief.
- [ ] Scope holds: routes only the settled out box. No re-opening necessary vs. unnecessary, no re-running red tags or the holding area, no arranging or homing the keepers. The out box is already decided; this chapter only routes it and closes Sort.
- [ ] All facts trace back to the final HTML. Inferences are labeled.

## Phase 9: Publishable HTML
- [ ] Open `chapter-11-publishable.html` in a browser and confirm it renders (fonts, the four SVG figures, the friction meter at its Sort-complete state with the dashed ghost, all figures).
- [ ] Replace the domain, author, date, and og:image placeholders in its head.
- [ ] Validate the embedded JSON-LD.

## Phase 10: Companion resources
- [ ] The Five Doors card produced (printable plus phone wallpaper: the five destinations and the quick routing cascade, with Donate as the default).
- [ ] The Out-Box Routing checklist produced (printable: a fast per-item router plus the sell-by deadline and the label-and-date rule for the rare Sell or Store items).
- [ ] Both linked from the chapter page and the highest-traffic CTAs.

## Phase 11: Schedule
- [ ] Load `publishing-calendar.md` into your scheduler.
- [ ] Set tracking links or UTMs per channel.
- [ ] Mark `asset-inventory.csv` status as each item is scheduled and then published.
- [ ] Confirm the four `review/` files are finalized before Day 1.
