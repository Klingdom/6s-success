# Chapter 22 · Production Checklist

## Source
- [ ] Author review and sign-off of the authored chapter (everything downstream depends on it)
- [x] Source files present: manuscript (~3,600 to 3,900 prose words), final.html (SVG figures), and the canonical strings and brief
- [x] Manuscript, final.html, and the canonical brief agree on facts, counts, section titles, and frozen strings

## Quality gates (all passed at build time)
- [x] Widened dash scan clean: no em dash, no en dash, no spaced-hyphen " - " separator (labels use "·")
- [x] Banned-word / hype scan clean; no fear-mongering and no anxiety framing of preparation (preparation is love for the day you hope never comes, not dread; a prepared home is not a fearful one, the way a boat looks with its life jackets stowed); anti-shame voice held (a home drifts back toward hazard not because anyone is careless but because ordinary life brings new things in; the four moves are the opposite of vigilance, not a verdict on the reader)
- [x] Safety register held: safety is love, not fear; no alarmist statistics, no graphic injury; the source's Principles of the Safety Step (goal of zero accidents and injuries, develop safety consciousness, safety integrated into all the S's) and Tools for Improving Safety referenced lightly and accurately, tied to Toyota / TPS, not overclaimed; "zero accidents and injuries" read as a direction, not a destination
- [x] JSON valid: canonical/chapter-metadata.json, web/schema-org-article.json, and the publishable HTML JSON-LD
- [x] Social lengths: X thread plus 10 short posts (each post at or under 280 including the number line); Facebook longform within 300 to 450 words; LinkedIn posts short-form
- [x] Quote cards verbatim, grep-verified against manuscript and final HTML; the definition box and the Prevent and Prepare hero lines matched byte-for-byte against the canonical brief
- [x] Friction meter: reaches the SAFETY COMPLETE milestone, the FOURTH marked tick on the dial, beside Sort complete, Straighten complete, and Shine complete; FOUR of six S's done. The step onto the mark was small and that is honest (the big daily friction was cleared long ago in Sort, Straighten, and Shine; what the three safety chapters added was the removal of the friction of the worst day, quiet on a dial that mostly measures ordinary days). Chapter 21's second-Safety-step position is now the dashed ghost just behind the live needle; the Shine-, Straighten-, and Sort-complete milestones sit further back as passed markers; the GOAL crosshair, tagged purpose, stays ahead on the green calm side, because two S's remain to make everything last. A true ARRIVAL and a MILESTONE (the fourth S finished), NOT the goal (Standardize and Sustain still follow). Marker "SAFETY COMPLETE".
- [x] Scope fences held: COMPLETES Safety with the two forward-looking moves a hazard hunt cannot make, PREVENTION (make the safe way the easy way; the three small habits) and PREPARATION (working alarms kept alive, extinguisher within reach, a walked exit plan, the few numbers everyone knows), plus the four-moves synthesis (see, remove, prevent, prepare) and the SAFETY COMPLETE milestone, and nothing else; USES the safety lens (Chapter 20) and the hazard hunt and five questions (Chapter 21) but does NOT re-teach them, re-derive the pyramid, or re-tell the 5S+1 history; keeps prevention and preparation LIGHT and does NOT write documented standards or schedules (Standardize) or long-term adherence systems (Sustain); no re-opening Sort, Straighten, or Shine, and no re-teaching cleaning or inspection (Chapters 16 to 19); the source's Safety principles and Tools for Improving Safety referenced lightly, not overclaimed; no brand names (say "a smoke alarm" or "a cabinet latch", not a brand)

## Inventory gate
- [x] Package COMPLETE: all 12 sub-packages present (including `review`), 56 files, matching the Chapter 20 and 21 shape. Inventory regenerated after every file landed.
- [x] CSV valid: workflow/asset-inventory.csv, 7 columns, 56 data rows (full package; one row per file across all 12 sub-packages, reconciled against the intended package with chapter number, paths, and titles updated to 22).

## Before publishing (fill placeholders)
- [ ] Insert live chapter URL wherever a CTA says "the online book"
- [ ] Replace author / publisher / URL / date / og:image placeholders in the schema JSON, PDF/ebook files, and chapter-22-publishable.html
- [ ] Rotate the LinkedIn and X CTA wording
- [ ] Replace or remove the back-cover testimonial placeholders
- [ ] Produce the visual assets (or wire in the hyper-realistic images, per the Ch 7 to 9 pattern); lead with the prepared-home opener (the same home as last chapter, hazards gone, now carrying the quiet marks of readiness: an alarm glowing green on each floor, an extinguisher near the kitchen, a safety shelf, a soft dashed exit line to one meeting spot outside) or "The Home Safety Baseline" infographic (two columns, Prevent and Prepare, each with its short concrete list)
- [ ] Offer the companion resources as the lead magnet: The Home Safety Baseline card and The Family Fire and Exit Plan
- [ ] Pick one LinkedIn carousel version (copy-ready) and keep the outline as planning

## Deliver
- [ ] Copy the package to the Desktop as 6S-Chapter-22-Content-Package
- [ ] Update 6S_Success_PROGRESS.md (mark Ch 22 drafted; Part 6 Safety COMPLETE here, the fourth S finished at the SAFETY COMPLETE milestone; NEXT = Ch 23, Standardize: The Best Way We Know Today, which opens Part 7)
