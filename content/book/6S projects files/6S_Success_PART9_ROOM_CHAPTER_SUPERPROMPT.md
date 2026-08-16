# 6S Success: Home Edition — Part 9 Room Chapter Super Prompt

*Reusable, chapter-by-chapter, for the twenty room playbooks (Chapters 31 to 50). Written 2026-07-25 after Chapters 31 to 43 shipped.*

> **PART NINE IS COMPLETE.** All twenty room playbooks (Ch 31 to 50) are authored, packaged, validated, and copied to the Desktop as of 2026-07-28. Ch 50, The Patio or Deck, is the final chapter of the book. This file is retained as the record of how they were built and as the spec for any rebuild, revision, or companion volume.

> **This file SUPERSEDES `6S_Success_CHAPTER_SUPERPROMPT.md` for Chapters 31 to 50.** That file is correct for Chapters 1 to 30 and wrong for Part 9 in seven specific ways: it caps length at 3,600 to 3,900 words, it requires friction-meter geometry (retired at Ch 30), it carries the OLD 10-chapter Part 9 outline with the wrong room map, it names the wrong source material, it never mentions zones or product types, it assumes parallel subagents are available, and it fixes the four callout names. Use this file instead. Fall back to the old one only for its palette/CSS notes and its Chapters 1 to 30 history.

---

## How to use this

1. Open a Claude Code session in the master folder.
2. Find the next `[ ]` chapter in `6S projects files\6S_Success_PROGRESS.md`.
3. Copy the **PROMPT TO PASTE** block, fill in `CHAPTER_NUMBER` and `ROOM_NAME` (the map is in Reference 1), and send it.
4. The session authors the chapter, builds all 12 sub-packages, validates, copies to the Desktop, updates the tracker and memory, and **stops for your review**.

The two fill-ins are the only ones. The room layer, the zone count, the hard calls, and the hazards all come from the Micro Zone Manual and must not be invented.

---

## PROMPT TO PASTE

```
You are producing ONE room playbook of "6S Success: Home Edition" (Part 9, Chapters 31 to 50) end to end, to the exact standard of Chapters 31 to 43. Follow this spec without inventing new conventions.

FILL-INS
- CHAPTER_NUMBER: <N>
- ROOM_NAME: <the Micro Zone Manual room name, exactly as it appears in content.json>

MASTER FOLDER (all paths under here):
C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master\6S Success Home Edition

MANUAL SOURCE (the room's content; this is the source of truth for everything factual):
C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\source\content.json      (rooms[].zones[] with shine_detail, passes, the_call, watch_for, done_looks_like)
C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\source\zone_products.json (keys are "Room||Zone")
C:\Users\philk\Desktop\6S-Micro-Zone-Manual-Package\source\products.json      (the product library, "master")

STEP 0 — LOAD CONTEXT
- 6S projects files\6S_Success_PROGRESS.md (status, what the previous chapter handed off, the NEXT pointer)
- 6S projects files\6S_Success_PART9_ROOM_CHAPTER_SUPERPROMPT.md (this file)
- The PREVIOUS chapter's folder: its CH<N-1> brief and chapter_<N-1>_manuscript.md (format template) and chapter_<N-1>_final.html (design template)
- Pull ROOM_NAME from content.json: the intro, the tips, and for every zone the purpose, done_looks_like, passes, the_call, watch_for, and the full shine_detail (shine_summary, surfaces[surface+method], products_used, inspect_as_you_clean). Pull the room's mapped product types from zone_products.json.
DO NOT invent zones, hazards, calls, or product types. Everything factual is folded from the Manual.

**If the Manual's zone LISTING and its own "Where to start" tip disagree, follow the tip and SAY SO in the chapter text.** Ch 46 is the first case: the Manual lists the workbench first and the PPE station sixth, but tells the reader to start at the PPE station. The chapter reorders and states the departure. Never reorder silently, and flag the divergence in the review package so the Manual can be reconciled.

STEP 1 — DESIGN THE ROOM LAYER, THEN FREEZE THE STRINGS
Every room chapter is the nine-rule Shine method PLUS a layer of three or four rules unique to that room, derived from the Manual's intro, tips (especially "Cleaning note" and "The trap"), and the pattern across its zones. Read the layers already used (Reference 3) and make this room's layer genuinely distinct; do not restate a previous room's.

Write 6S-Success-Chapter-<N>\CH<N>_CANONICAL_STRINGS_AND_BRIEF.md modeled on the previous chapter's brief. It must freeze, byte-exact, the strings the whole package will reuse:
  1. The N zones line ("The <room> is <n> small zones, not one big job: ... Do them one at a time, and start at <the Manual's Where-to-start zone>, because <the Manual's reason>.")
  2. The rule (the room layer stated as one paragraph)
  3. The definition box ("A finished <room> is one that ...", built from the zones' done_looks_like)
  4. One reframe per layer rule (three or four)
  5. The safety reframe (built from the zones' watch_for, organised by the five safety questions)
  6. The before-and-after caption
  7. One Idea to Keep
Nine or ten frozen strings total. Also freeze the four callouts, the hard calls (from the_call), the five-safety-question list, the kit (product TYPES only), and the design notes.

STEP 2 — AUTHOR THE TRIO
**LAY THE SECTION SKELETON DOWN BEFORE WRITING ANY PROSE.** Write the H1, the Subtitle line, every H2 below, and the empty zone headings FIRST, then fill them. Ch 50 was drafted straight into prose without the skeleton, was missing the Subtitle and the Quick Passes section, and carried three non-canonical H2s. It all had to be reconciled afterwards, and worse, the first length measurement was taken against an incomplete manuscript, so the trimming done at that point looked far more effective than it was. Ten minutes of headings first would have avoided a rebuild pass and a bad measurement.
- chapter_<N>_manuscript.md. Structure, in order:
    # Chapter <N>: <Room>
    Part Nine · Room-by-Room Playbooks
    **Subtitle:** <frozen>
    [VISUAL: Full-page illustration] + Caption:
    ## Chapter Opening            (3 to 4 paragraphs; the room's central idea)
    ## What You Will Learn        (5 bullets)
    ## <N> Zones, Not One Room    (principle + frozen zones line + frozen defbox + [INFOGRAPHIC] + Caption)
    ## The Quick Passes: Sort, Straighten, Safety, Standardize, Sustain
    ## How to Shine the <Room>: The Method   (nine rules as read + the frozen layer reframes + Quick Win + 6S Tip + [INFOGRAPHIC] + Caption)
    ## Zone by Zone: Exactly How to Clean It (THE CENTERPIECE)
    ## The Calls That Matter Here            (+ the room's family-challenge callout)
    ## Watch for in the <Room>               (five safety questions + frozen safety reframe + Common Mistake)
    ## Before and After                      ([ILLUSTRATION] + Caption + frozen before/after caption + One Idea to Keep + **Next:** ...)
- THE CENTERPIECE IS THE POINT. Per zone, in this exact markup:
    ### Zone <k> · <Zone Title>
    <1 short paragraph: what the zone is for and the ordering logic>
    **Inputs:**
    - <product TYPES, 4 to 6 bullets>
    **Steps:**
    1. <7 to 11 numbered steps, elevated from the zone's shine_detail surfaces+methods into pro procedure>
    **Inspect and flag as you go:** <one paragraph folded from inspect_as_you_clean, ending "Flag each.">
- chapter_<N>_signature.md: the Part 9 close (the before/after room signature, the two photos, plus any variation this room needs).
- chapter_<N>_final.html: built by adapting the previous chapter's builder (see Reference 5).

STEP 3 — BUILD THE PACKAGE
Adapt the previous chapter's four scripts by sed-rename, then edit: build_ch<N>_html.py, build_ch<N>_core.py, build_ch<N>_pkg.py, validate_ch<N>.py, copy_ch<N>_desktop.py. Reference 5 lists exactly what to change in each. Write the four review\ files by hand and honestly.

STEP 4 — VALIDATE (run it, report real numbers)
Every gate in Reference 4 must pass. If a gate fails, FIX IT AND RE-RUN; do not report a failing number as acceptable.

STEP 5 — DESKTOP COPY, TRACKER, MEMORY, STOP
Desktop copy = 59 files. Update PROGRESS.md with a full entry in the house style and move the NEXT pointer. Update the 6s-success-book memory note. Then STOP and summarise for review. Do NOT start the next chapter.

QUALITY BAR: the per-zone instruction is the most important thing in the chapter. Completeness of the clean-and-shine instruction beats brevity. Never invent a hazard, a product, or a statistic. Product TYPES only, never brands. Never advise mixing cleaners. Clean, look, and FLAG; never give repair instructions.
```

---

## Reference 1 — The chapter to room map (fixed; from the Manual's order)

31 Entryway · 32 Kitchen · 33 Pantry · 34 Dining Room · 35 Living Room · 36 Family Room · 37 Primary Bedroom · 38 Guest Bedroom · 39 Kids Bedroom · 40 Nursery · 41 Primary Bathroom · 42 Guest Bathroom · 43 Laundry Room · **44 Home Office** · 45 Garage · 46 Workshop · 47 Mudroom · 48 Hall Closet · 49 Stair Landing · 50 Patio or Deck

Room groupings that matter for continuity: Ch 31 to 40 are the ten sleeping and living rooms; 41 to 42 are the wet rooms; 43 opens the utility rooms; 45 to 46 are the heavy/tool rooms; 47 to 50 are the small transition spaces (expect fewer zones and shorter chapters).

## Reference 2 — The nine rules of Shine (frozen at Ch 31; govern every room)

1. Top to bottom. 2. Dry before wet. 3. Back to front, clean to dirty. 4. Mist the cloth, not the surface. 5. Two cloths: clean, then dry. 6. Colour-coded cloths, no fabric softener. 7. Match the cleaner to the surface. 8. Give it dwell time. 9. Clean to inspect and **FLAG**, not fix.

Rule 9 is the enforced fence: **Shine notices and flags hazards; the Safety pass fixes them.** Never write a step that repairs.

## Reference 3 — Room layers used so far (do not repeat; make the new one distinct)

| Ch | Room | Layer |
|---|---|---|
| 31 | Entryway | grit |
| 32 | Kitchen | grease |
| 33 | Pantry | dust, dates, pests, damp (dry before wet) |
| 34 | Dining Room | fine finishes, gentleness |
| 35 | Living Room | soft furnishings, screens, dust that becomes heat |
| 36 | Family Room | clean-and-dry, lift the dry mess first, the floor a child shares |
| 37 | Primary Bedroom | clean for sleep and air, you clean they cull |
| 38 | Guest Bedroom | air it not spills, draw the line |
| 39 | Kids Bedroom | their height and reading level, with them not for them |
| 40 | Nursery | safety leads every zone, the bare crib, one arm's sweep |
| 41 | Primary Bathroom | spray first and let chemistry work, dry beats mould, read the date |
| 42 | Guest Bathroom | judged up close, run the water, no demotion |
| 43 | Laundry Room | lint is fuel, nothing put away wet, clean the machine that cleans, the flow jams at the counter |
| 44 | Home Office | judgments not lifts, here the wet cloth is the risk, clear one surface first, the door that closes |
| 45 | Garage | postponed not stored, get it off the floor then read the floor, weight and height are the hazard, this room holds the real chemistry |
| 46 | Workshop | the stakes here are physical, the smallest zone leads, vacuum never sweep, three postponed verdicts |
| 47 | Mudroom | this room catches not stores, grit stops in three layers, the floor is a symptom and the wall is the cause, lids hide the drift |
| 48 | Hall Closet | nobody owns it, depth lies so you cannot sort it in place, closed and dark means damp, most of it serves another room so walk it back |
| 49 | Stair Landing | a route not a room so the right amount of storage is nearly none, the hazard waits unattended because a staircase is not a task, the trap is a reasonable sentence so give it a basket not an argument, the handrail is the most touched and least washed surface in the house |
| 50 | Patio or Deck | the weather is not the enemy here it is the point, postponement is billed rather than free, if it cannot take a night of rain it belongs behind a door, out here cleaning is how you read the structure |

## Reference 4 — Production gates (all must pass; report real numbers)

**Text**
- 0 em dashes, 0 en dashes, 0 prose spaced-hyphen separators. The ONLY permitted `" - "` is a self-referential rule literal inside the checklist or review files.
- Every frozen string byte-verbatim in BOTH the manuscript AND final.html (check the HTML after entity normalisation).
- Product TYPES only. Run the brand scan. No invented statistics, prices, or percentages.
- No hype vocabulary, no force metaphors, no blame directed at people (diagnose systems, per Ch 28).
- No repair instructions anywhere. No advice that could mix cleaners.

**Honest negatives on the five safety questions.** Not every room answers all five. Ch 47 is the first chapter to say so in the text: the mudroom carries no meaningful fire load, and rather than invent a hazard to fill the slot, it says so and explains why (pretending otherwise makes the other four easier to ignore). **Follow that precedent.** Ch 48, 49, and 50 are small rooms and will have thin answers on more than one question. Record the negative in the reuse-risk file so a later reviewer does not read it as a gap. Ch 49 is the second chapter to do this, declining poison, choke and strangle. Two honest negatives in nineteen chapters is about right: the device works because it is rare, so do not reach for it to save drafting effort.

**Let step count follow the Manual, not a round number.** Per-zone words crept 477, 483, 486, then broke through to 515 at Ch 48, which was the first chapter to budget them explicitly and the first budget to fail. The diagnosis is not verbose steps: it is that **step count per zone had standardised at exactly ten** (Ch 48 wrote 50 steps across 5 zones). The Manual gave that room 34 shine surfaces, so each surface was being expanded into roughly 1.5 steps.

**So: count the zone's `shine_detail` surfaces first, and let that set the step count.** A 6-surface zone should produce 7 or 8 steps, not 10. A 8-surface zone can carry 10 or 11. Rounding every zone to ten is what inflates the centrepiece, and the centrepiece is the one component you must never cut later, so get it right at the drafting stage.

**And budget words per step, not only steps per zone.** Ch 49 applied the surface-count rule correctly (8 surfaces, 10 steps, legitimate) and per-zone words still rose, to 587. The steps themselves had grown: 59 words each against Ch 48's 51. Fixing one driver exposed the other. **Target about 50 words per step**, and multiply it out in the brief: surfaces to steps to words. A step that runs past 60 words is usually carrying an explanation that belongs in the method section.

**Structure**
- Zone cards == the room's zone count; one `<ol>` per zone; every zone has Inputs, Steps, and inspect-and-flag.
- Exactly 4 visual blocks in the manuscript and exactly 4 `<svg>` / 4 `<figure>` in final.html. NO friction meter.
- **Every `<h2>` carries a non-empty kick label.** The builder must RAISE on a missing one. (Ch 35 to 42 shipped with an empty kick on "The Quick Passes" because the map silently fell through; swept 2026-07-25.)
- Balanced tags: div, section, figure, ul, ol, aside, h2, h3.
- Head contains no reference to the previous chapter's number or room.

**Package**
- 56 files across 12 sub-packages (Reference 6) plus the publishable HTML at the package root.
- Publishable `<main>` body byte-identical to final.html's.
- `chapter-metadata.json` and `schema-org-article.json` parse; `asset-inventory.csv` is 57 rows by 7 columns (header + 56).
- `graphics/quote-card-copy.md` byte-verbatim against `canonical/chapter-quotes.md`.
- **`canonical/chapter-title.txt` must contain the ROOM NAME, not a hardcoded leftover.** It read "The Laundry Room" in every chapter from Ch 44 to Ch 49, because the core builder hardcoded the string at Ch 43 and each chapter's builder was sed-copied from the last. Swept 2026-07-28; the Ch 50 builder writes the `TITLE` variable. **This is the third defect of exactly this shape** (empty kick labels Ch 35 to 42, stray `"""` Ch 36 to 42, wrong title Ch 44 to 49). When you sed-copy a builder, diff its literal strings against the new chapter, not just its variables.
- **No stray `"""`** at the end of any hand-written file. (Artifact found in Ch 36 to 42; swept 2026-07-25.)

**Platform**
- X thread and shorts at or under 280 chars INCLUDING the number line.
- LinkedIn posts under 150 words each.
- Facebook longform 300 to 450 words (hard cap). **Draft it at about 400 words.** It has overrun on every chapter measured (Ch 43 built at 495, Ch 44 at 500, Ch 45 at 483) and been trimmed each time. Writing to 400 costs nothing and removes a guaranteed rework.
- Meta description 140 to 160 characters.

**Length (measured model, corrected 2026-07-27)**

A first version of this section claimed 900 to 1,100 words per zone and concluded that Ch 43's overrun meant the range was too tight. Measuring Ch 38 to 44 properly shows that was wrong. The real model is:

**total = about 3,600 of frame + about 460 per zone**

and the frame is remarkably stable across chapters regardless of zone count:

| Ch | Zones | Zone cards | Per zone | Frozen | Callouts | Prose | Frame | Total |
|---|---|---|---|---|---|---|---|---|
| 38 | 5 | 2,426 | 485 | 929 | 255 | 2,349 | 3,533 | 5,959 |
| 39 | 6 | 2,609 | 434 | 891 | 259 | 2,362 | 3,512 | 6,121 |
| 40 | 6 | 2,654 | 442 | 911 | 229 | 2,435 | 3,575 | 6,229 |
| 41 | 7 | 3,083 | 440 | 956 | 236 | 2,439 | 3,631 | 6,714 |
| 42 | 5 | 2,497 | 499 | 936 | 251 | 2,427 | 3,614 | 6,111 |
| 43 | 6 | 3,154 | 525 | **1,455** | 271 | 2,651 | **4,377** | **7,531** |
| 44 | 6 | 3,335 | 555 | **1,279** | 358 | 2,748 | **4,737** | **7,720** |

Indicative targets: 5-zone ~5,900; 6-zone ~6,400; 7-zone ~6,800.

**The failure mode to watch is frozen-string inflation.** Ch 38 to 42 hold ~920 words of frozen strings; Ch 43 and 44 carry 1,279 to 1,455. A four-part room layer justifies some of that, not 350 to 500 words. **Keep frozen strings to about 110 words each and nine or ten of them.** Draft them, then count them, before you write the manuscript, because once the package is built they are a byte-verbatim contract across 56 files and re-trimming means a full rebuild.

**Never cut zone steps to hit a word target.** If a chapter runs long, cut the frozen strings first (while they are still cheap to change), then connective prose. Report the real split in the editorial review either way.

**Evidence that counting first works.** Three cheap habits, each written here after it failed once, removed every late-stage rework:

| Component | Norm | Ch 44 | Ch 45 | Ch 46 | Ch 47 | Ch 48 | Ch 49 |
|---|---|---|---|---|---|---|---|
| Frozen strings | ~920 | 1,279 | 941 | 1,006 | 952 | 938 | 944 |
| Callouts | ~250 | 358 | 357 | **255** | 250 | 267 | 252 |
| Total vs model | | +21% | +3.4% | **+1.0%** | +1.3% | -0.6% | **+0.1%** |
| Facebook longform | 300-450 | 500, trimmed | 483, trimmed | **415, first pass** | 414 | 407 | 418 |

1. Draft and COUNT the frozen strings before the manuscript.
2. Budget the callouts in the brief (~250), not after.
3. Draft the Facebook longform at ~400.

Ten minutes of arithmetic at the brief stage. Do all three.

**Do not re-fit the length model on the sample that produced it.** At the Ch 49 brief stage the model looked improvable: since every chapter carries one hard call per zone, the frame ought to scale with zone count, which gave `2,940 + 570 per zone`. That fitted Ch 45 to 48 more tightly than the original, so it was adopted and Ch 49 was targeted at 4,650 words.

Ch 49 landed at 4,985.

| | Ch 45 | Ch 46 | Ch 47 | Ch 48 | Ch 49 |
|---|---|---|---|---|---|
| `3,600 + 460z` (original) | +3.4% | +1.0% | +1.3% | -0.6% | **+0.1%** |
| `2,940 + 570z` (refined) | +1.7% | +1.0% | +1.3% | +1.3% | **+7.2%** |

The refinement had been fitted to the four points that produced it and the fifth disproved it. **The original model stands and is now five-for-five within -0.6% to +3.4%.** Leave it alone for Ch 50. More generally: a refinement is not adopted until an out-of-sample point has tested it, and a tighter fit on the training sample is not evidence of anything.

## Reference 5 — The hand-build script recipe

The 200-subagent session cap has been exhausted since Ch 34, so Ch 35 onward were built entirely by the coordinator. Each chapter's scripts are sed-renamed copies of the previous chapter's, living in the session scratchpad.

- **`build_ch<N>_html.py`** — change: `SRC` to the previous chapter's final.html; the `KICK` map (all seven section titles; raise on miss); `DEFBOX_START` / `DEFBOX_LABEL`; the `zones<n>` list for figure 2 (3 per row; a 7-zone room needs a 3-row grid); the f1/f3/f4 SVG copy; the masthead eyebrow and title; the figure-dispatch keywords in the `[INFOGRAPHIC]` branch; and the head's title and chapter/room replacements. The callout class dict must include this room's renamed family callout, and raise on an unknown name.
- **`build_ch<N>_core.py`** — publishable HTML (insert the meta block after `</title>`), schema JSON, the 8 canonical files, the 7 web files. Assert body parity.
- **`build_ch<N>_pkg.py`** — the 33 platform files by dict, the X builder with char counts, and the CSV. Prints the LinkedIn/Facebook/X/CSV gate numbers.
- **`validate_ch<N>.py`** — the full gate run of Reference 4.
- **`copy_ch<N>_desktop.py`** — flatten the package plus the three source files to `C:\Users\philk\Desktop\6S-Chapter-<N>-Content-Package\`; verify 59.

**Warning about this recipe:** copying the previous chapter forward also copies its bugs. Both defects found in the Ch 35 to 42 range propagated exactly this way. After building, diff your output against an EARLIER chapter (31 to 34 are clean), not only against the one you copied.

## Reference 6 — The 56 files

| Folder | N | Files |
|---|---|---|
| (root) | 1 | chapter-`<N>`-publishable.html |
| canonical | 8 | chapter-cta.md, chapter-key-takeaways.md, chapter-metadata.json, chapter-outline.md, chapter-quotes.md, chapter-seo.md, chapter-summary.md, chapter-title.txt |
| web | 7 | chapter-navigation-copy.md, landing-page-intro.md, meta-description-options.md, open-graph-copy.md, read-next-recommendations.md, schema-org-article.json, seo-title-options.md |
| linkedin | 5 | linkedin-article.md, linkedin-carousel-outline.md, linkedin-comment-prompts.md, linkedin-newsletter-version.md, linkedin-posts-10.md |
| facebook | 3 | facebook-group-discussion-post.md, facebook-longform-post.md, facebook-posts-5.md |
| x | 2 | x-short-posts-10.md, x-thread.md |
| newsletter | 4 | newsletter-preview-text.md, newsletter-short-teaser.md, newsletter-subject-lines.md, newsletter-version.md |
| video-audio | 5 | b-roll-and-visual-notes.md, podcast-script-8-to-12-min.md, short-video-scripts-5.md, teleprompter-script.md, youtube-script-6-to-8-min.md |
| slides | 3 | linkedin-carousel-copy.md, teaching-slide-deck-outline.md, visual-storyboard.md |
| pdf-ebook | 5 | back-cover-copy.md, chapter-pdf-frontmatter.md, ebook-description.md, ebook-sales-copy.md, reader-discussion-questions.md |
| graphics | 4 | diagram-ideas.md, image-generation-prompts.md, infographic-spec.md, quote-card-copy.md |
| workflow | 5 | README.md, asset-inventory.csv, production-checklist.md, publishing-calendar.md, repurposing-map.md |
| review | 4 | brand-voice-check.md, editorial-review.md, final-package-summary.md, reuse-risk-check.md |

## Reference 7 — The close, and its variations

Part 9 retired the friction meter (it reached GOAL at Ch 30). Every room chapter closes on a **before-and-after room signature**: the before photo taken before anything is touched and kept as the honest record (Ch 6), the after taped up as the ideal-state standard (Ch 25).

Variations used so far, for reference: Ch 39 the **child** takes the after photo; Ch 40 the after is the **nightly safe state**; Ch 43 the after contains **one detail that expires** (the dated tape on the dryer); Ch 44 the after is **taped inside a drawer** and matched nightly; Ch 45 the after keeps working as a **diagnostic floor**; Ch 46 the after is judged on **time to first cut**; Ch 47 the after is judged on the **floor strip**; Ch 48 adds a **third photograph** (the back wall of the deepest shelf, the only self-verifying image in the book); Ch 49 adds **a check you stand in rather than a photograph** (stand at the bottom in the dark and look up, then at the top and look down, because that is the view the fall would have) and is the only close in Part 9 whose extra element is a position rather than an image.

A variation is optional. Use one only when the room genuinely needs it, and document it in the signature file. Ch 50 took the series-closing variation in two parts: the after photo goes **beside the very first photograph the reader took in Ch 6** (the only instruction in the book that requires the whole book to have happened), and it is **the only standard expected to DECAY rather than hold**, which is what finally proves Ch 30's claim that you renew rather than finish. **Ten of twenty chapters used a variation, which is the right density.**

## Reference 8 — Callouts

Four per chapter, in this order: **Quick Win** (`win`), **6S Tip** (`tip`), **the room's own challenge** (`family`), **Common Mistake** (`mistake`).

The third is renamed per room and must be registered in the builder's class dict: Ch 42 "The No-Demotion Challenge", Ch 43 "The Nothing-Goes-Away-Wet Challenge". The builder must raise on an unregistered name rather than emitting `class="callout None"`.

## Reference 9 — Product library

97 types at the appendix's first build, **123 as of 2026-07-28** (unchanged at Ch 48 and Ch 49; Ch 50 added 4: a bristle-free grill grate scraper, a long-handled deck scrub brush, a fabric-safe outdoor cushion cleaner, and a garden hose). **Ch 50 REVERSED an earlier call in the open:** Ch 45 left the garden hose out as an ordinary noun, correctly for a garage where it was a one-job tool; outdoors it is the primary rinsing input in four of six zones, so it became a TYPE. If the line has to move, move it visibly and say why, rather than applying the rule two ways quietly (Ch 43 added 2, Ch 44 added 3, Ch 45 added 8, Ch 46 added 6, Ch 47 added 3: scraper and absorbent entry mat set, stiff scrubbing brush, soft clothing brush). Seven families. **The extinguisher and first aid kit were taught in Ch 22 and had never been in the library, a gap predating Part 9.** Source of truth is the Manual's `products.json`; the appendix is regenerated to Master `6S-Success-Appendices\` and copied to Desktop `6S-Product-Appendix\`.

**If a room's Manual content requires an input the library does not carry:** add it to `products.json` with a full record (ID, family, category, purpose, phases, rooms, level, price band, safety note, Catalog Version), map it in `zone_products.json`, regenerate the appendix, and record it in the chapter brief. Do not let a chapter name an input the appendix cannot back.

**Where to draw the line (set in Ch 45, movable by Phil):** if it is a cleaning or protection input a reader must deliberately buy and will reuse across rooms, it becomes a catalogue type. If it is a household commodity or a one-job hand tool, it stays an ordinary noun in the steps. Ch 45 added eight types on that rule and deliberately left out a garden hose, baking soda, a mild gear disinfectant, a flat file, and compressed air. Without a line like this the appendix inflates on every tool-heavy room, and Ch 46 The Workshop is the next one that will test it.

**Check the mapping before adding a type.** Ch 48 needed no new types at all, the first Part 9 chapter to manage it, but it did need one MAPPING fix: nitrile gloves already existed in the library and simply were not mapped to the zone whose `products_used` named them. Always check `name in library` before `name in this room's mapping`. A missing mapping looks exactly like a missing type and is a great deal cheaper to fix.

**Retro-filling earlier chapters.** Twice now a Part 9 chapter has added a type that an EARLIER chapter had named as an ordinary noun, and mapped it back to that room: Ch 46's self-closing oily rag can went back to the Garage, and Ch 47's entry mat set went back to the Entryway. Do this whenever it applies. It costs one line in the mapping and it stops the appendix drifting out of step with the chapters already written.

**Schema trap:** entries in `zone_products.json` are DICTS with nine keys (`id`, `name`, `family`, `level`, `use`, `phase`, `qty`, `unit`, `safety`), not strings. Appending a bare product name silently corrupts the file for any consumer doing `p["name"]`. This happened with the Ch 43 additions and was fixed during the Ch 44 build. After any addition, assert that every entry is a dict and that every name resolves in the library.

## Reference 10 — Open items

- **Part 9 illustration stream is untouched.** Ch 31 to 43 ship with hand-authored SVGs and no photographic art (Ch 31 has 2 pilot images). The image-generation prompts in each `graphics\` folder are written but unused.
- **Ch 4 onward are drafts awaiting Phil's review.** Only Ch 1 to 3 are marked reviewed.
- **The length range in Reference 4 is a recommendation awaiting Phil's confirmation.**
