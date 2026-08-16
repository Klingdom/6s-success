# Final Package Summary: Chapter 11, What to Donate, Sell, Store, Recycle, or Throw Away

## Status
Complete. The chapter was authored (no source existed), then fully packaged. All twelve packages built, validated, and quality-reviewed, plus a publish-ready HTML. This is the fourth and final chapter of Part 3 (Sort), and it closes Sort: it routes the already-decided out box out through five doors and carries it out of the house, without re-opening the belonging question, the use test, or the red tags that the first three passes settled.

## How this chapter was made
Chapter 11 had no supplied source files. Its source trio was authored in the established book voice and design, then packaged like Chapters 1 to 10:
- `chapter_11_signature.md` (signature plan, authored)
- `chapter_11_manuscript.md` (manuscript, authored; roughly 3,700 prose words by my count, see the note below on length; the whole file measures 4,287 words including the two verbose visual-direction blocks)
- `chapter_11_final.html` (final designed HTML, authored, with the five-doors opener and the moved friction meter among its four inline SVGs, in the locked palette and type)

This means the chapter is a draft awaiting author review. The packaging is faithful to the draft. If the author revises the chapter, the canonical layer and the affected packages should be refreshed.

## What was produced
56 files across 12 folders, plus the publishable HTML at the package root. Counted directly: 52 files in the package before this review folder, plus these 4 review files, equals 56.

| Package | Files | Package | Files |
|---|---|---|---|
| Canonical | 8 | video-audio | 5 |
| Web | 7 | slides | 3 |
| LinkedIn | 5 | pdf-ebook | 5 |
| Facebook | 3 | graphics | 4 |
| X | 2 | workflow | 5 |
| Newsletter | 4 | review | 4 |
| Publishable HTML | 1 (package root) | | |

## Quality gates passed (each scan or count was run for this summary)
- **Widened dash scan:** em dash (U+2014), en dash (U+2013), and spaced-hyphen " - " used as a separator (excluding markdown list bullets), run across all 52 package files plus the manuscript and the authored final HTML (54 files scanned; the publishable HTML is one of the 52 package files; the review folder was empty at scan time). Result: zero matches. Separators use the middot ("·"), counted 137 times across the scan. For transparency, the only em dashes in the chapter folder are three inside the non-shipped working brief `CH11_CANONICAL_STRINGS_AND_BRIEF.md` (counted).
- **Banned-word scan:** zero hits across the package for "unlock," "leverage," "delve," "seamless," "supercharge," "elevate," "game-changing," "dive in," "in conclusion," "fast-paced," "in today's," "effortless," "revolutionize." No force or violence framing in the copy; the words "purge" and "war on clutter" appear only in `video-audio/b-roll-and-visual-notes.md` as instructions to avoid that framing (verified).
- **JSON:** `canonical/chapter-metadata.json` and `web/schema-org-article.json` both parse as valid JSON. The publishable HTML's single embedded JSON-LD block validates.
- **CSV:** `workflow/asset-inventory.csv` is valid with all 7 required columns and 56 data rows, no ragged rows.
- **Social length (measured):** X thread is 16 posts (header says 16, counted 16), all bodies at or under 280 characters, longest is post 11 at exactly 280 (note: with the "N/" numbering line counted, post 11 runs 284 and would need a four-character trim; every other post stays under 280 even with the number counted). X short posts are 10, all bodies at or under 280, longest 276 (post 10). LinkedIn is 10 posts, each under 150 words, longest 145 (post 5). Facebook longform body is 420 words, inside the 300 to 450 target. Note: the X thread's in-file "(approx.)" annotations run a few characters low against my measured counts.
- **Final HTML:** exactly 4 inline SVGs in both `chapter_11_final.html` and `chapter-11-publishable.html`. Structural tags balance (div 15/15, section 1/1, svg 4/4, head/body/html/style all 1/1; the publishable HTML also has script 1/1 for its JSON-LD, the authored final HTML has none). Authored final HTML 52,682 bytes; publishable HTML 56,390 bytes.
- **The friction-meter move:** the caption ("The needle takes its last Sort step, because the out box left the building...") is present in both HTML files, and both the marked "Sort complete" tick and Chapter 10's held position drawn as a faint dashed ghost are present in both, with the GOAL crosshair still ahead (verified). The manuscript language reads as an honest, earned move: "the needle steps forward, off its held position and onto a clearly marked tick on the dial: **Sort complete.**" then, in the same breath, "the goal, the crosshair out on the green calm side, is still ahead of where the needle now sits. Sort is finished; the journey is not." (present, verified). This is the chapter's distinguishing gauge beat: it fulfills Chapter 10's dashed projection, marks the milestone plainly, and refuses to oversell it because five S's remain.

## On chapter length (flagged honestly, not a blocker)
- The manuscript's reader prose is tight, in the Chapter 8 and Chapter 10 range. Measured three ways: the whole file is 4,287 words; with the two `[VISUAL]` / `[ILLUSTRATION]` direction blocks removed it is 3,901 words; and the reader narrative (further excluding headings, the front-matter list, and the callout blockquotes) is about 3,232 words. So "roughly 3,700 prose words" is a fair midpoint, but the honest range is about 3,200 (strict reader narrative) to 3,900 (prose plus callouts, direction removed). The larger whole-file number is production direction, not reader content, so the prose itself is not long.

## Key extracted assets
- **Title:** What to Donate, Sell, Store, Recycle, or Throw Away
- **Hero device:** The five doors out, named and ordered: "**Donate, Sell, Store, Recycle, Throw.**" (verbatim). A short cascade stops each item at the first door that fits, and the order leans the great majority of any box toward the two fast lanes, Donate and Recycle.
- **The default door:** Donate. "Donate is the default. Most usable things you do not need should go to someone who does, today, not to a someday sale that keeps them in your house for months." (verbatim). It is the exit that actually completes, the same day, and giving is reframed as the opposite of waste.
- **The two slow doors, each with a guardrail:** Sell gets a sell-by deadline ("Selling turns clearing into a part-time job. Sell only what is genuinely worth the work, put a deadline on it, and donate whatever has not sold by the date.", verbatim). Store gets a label and a date and a hard rule ("Storing is not deciding. Store only what you will truly use later, label it and date it, and never rent space to keep what you do not need.", verbatim).
- **Recycle and Throw, for the worn and the finished,** carried by the sunk-cost reframe: "Some things are simply worn out, and throwing them away is not the waste. The waste, if there ever was any, happened at the store." (verbatim), with "There is no virtue in living among broken objects." (verbatim).
- **Worked example:** a routing pass on the entryway out box. Two extra umbrellas and a wad of surplus tote bags go through Donate; old takeout menus, a dead charging cable, the torn tote bags, and the spare key to a car sold two summers ago go through Recycle (the key may Throw if that is simpler). Nothing was valuable enough to sell, nothing needed later enough to store, and the whole box left the house in one trip. (All items grep-verified.)
- **Scope line (verbatim):** "You are not here to decide anything today. You are here to route."
- **Hero CTA:** get three things out of the house today, the usable ones into a donation bag in the car, the broken one to recycling or the bin.
- **One Idea to Keep (verbatim):** "The best destination is the one that actually empties the box. A thing given away today beats a thing you mean to sell someday. Choose the door that gets it out of the house, and Sort is finished."

## Continuity notes
- **Fourth and final chapter of Part 3 (Sort).** Follows Chapter 8 (sort by belonging), Chapter 9 (sort by use), and Chapter 10 (tag the honest maybes), and hands off to Chapter 12, which opens Part 4: "**Next: Chapter 12 · Straighten: A Place for Everything.**" (verbatim). Its job is only disposition, not decision: "Deciding a thing is unnecessary and deciding where it should go are two separate acts, and you already finished the first." (verbatim).
- **The entryway pays off in full.** The console was cleared in Chapter 8, the basket emptied in Chapter 9, the maybes tagged in Chapter 10, and here the out box is routed through five doors and carried out in a single trip, leaving the corner empty.
- **The landmark MOVES, and it is the honest milestone that closes the first S.** For three chapters the needle held; this chapter it steps off its held position onto a clearly marked "Sort complete" tick because the out box physically left the building, fulfilling Chapter 10's dashed projection. Chapter 10's held position is now the faint dashed ghost showing the ground covered. The GOAL crosshair still sits ahead because five S's remain (Straighten, Shine, Safety, Standardize, Sustain). This closes Sort and the first S; it is not reaching the final goal, and the chapter says so plainly.
- **Scope held.** The keepers are left exactly where they landed, without homes; giving every keeper a proper place is deferred to Chapter 12 (Straighten) and not built early here. "Sorting decided what stays. It did not decide where any of it lives." (verbatim).

## Open items before publishing (handoffs, not blockers)
1. Author review and approval of the authored chapter. Everything downstream depends on it.
2. Insert the live chapter URL wherever a CTA says "the online book" (appears in 18 package files, counted).
3. Replace author / publisher / URL / date placeholders in the schema JSON, the PDF/ebook files, and `chapter-11-publishable.html`.
4. Rotate the six LinkedIn and X CTA phrasings.
5. Replace or remove the three back-cover testimonial placeholders before print.
6. Decide the X numbering convention; if "N/" counts toward the 280, trim post 11 by four characters. Optionally correct the thread's "(approx.)" character annotations to the measured counts.
7. Produce the visual assets, leading with the Five Doors card (printable plus wallpaper), and pick one LinkedIn carousel version (the copy-ready one), keeping the outline as planning.

## Recommended next action
Review the authored chapter first. If the five doors and their order, the two guardrails, the worked out-box pass, and the friction-meter move to "Sort complete" are right, do one find-and-replace pass for placeholders and "the online book," then start the rollout in `workflow/publishing-calendar.md`. With Chapter 11 done, Part 3 (Sort) is complete and the first of the six S's is finished: what did not belong and what you do not need are both out of the house. Chapter 12 opens Part 4 (Straighten) and gives every remaining keeper a place of its own. If you want changes to the chapter, tell me and I will revise the draft and re-sync the package.

Generated 2026-07-01.
