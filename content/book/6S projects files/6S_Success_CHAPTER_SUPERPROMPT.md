# 6S Success: Home Edition — Chapter Production Super Prompt
*(Reusable, chapter-by-chapter. Paste the "PROMPT TO PASTE" block into a Claude Code session, fill the three fill-ins at the top, and run. This encodes the exact pipeline, gates, and design that produced Chapters 1 to 18.)*


> **SCOPE NOTE (added 2026-07-25): this file applies to Chapters 1 to 30 only.**
> For the Part 9 room playbooks (Chapters 31 to 50) use `6S_Success_PART9_ROOM_CHAPTER_SUPERPROMPT.md` instead. This file is wrong for Part 9 in seven ways: it caps length at 3,600 to 3,900 words, it requires friction-meter geometry (retired at Ch 30), its Reference 5 outline carries the OLD 10-chapter Part 9 room map (superseded by the 20-room map), it names the wrong source material (the Micro Zone Manual is the Part 9 source), it never mentions zones or product types, it assumes parallel subagents are available (the cap has been exhausted since Ch 34), and it fixes the four callout names (the third is renamed per room).

---

## How to use this

1. Open a Claude Code session in the project (the master folder below).
2. Decide the chapter number N you are producing next (check `6S projects files/6S_Success_PROGRESS.md` for the next `[ ]` line).
3. Copy the **PROMPT TO PASTE** block, fill in `CHAPTER_NUMBER`, `FRICTION_METER_STATE`, and `HERO_DEVICE_NOTE` (guidance for all three is in the reference sections below), and send it.
4. The session will freeze strings, author the chapter, build all 12 asset sub-packages via parallel subagents, validate, copy to the Desktop, update the tracker, and **stop for your review**. Review, then run the next chapter.

Tip: if you are unsure of the friction-meter state or hero device, leave those fill-ins as `ASK` and the session will propose them and confirm with you before authoring (this is what happened for Chapters 16, 17, and 18).

---

## PROMPT TO PASTE

```
You are producing ONE chapter of the book "6S Success: Home Edition" end to end, to the exact standard of Chapters 1 to 18. Work in the project master folder and follow the settled decisions, production gates, and pipeline below without inventing new conventions.

FILL-INS
- CHAPTER_NUMBER: <N>
- FRICTION_METER_STATE: <MOVE | HOLD | MILESTONE | ASK>   (see the friction-meter guide; ASK = propose and confirm with me before authoring)
- HERO_DEVICE_NOTE: <one-line intent for the chapter's hero device, or ASK>

MASTER FOLDER (all paths are under here):
C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master\6S Success Home Edition

STEP 0 — LOAD CONTEXT (read before doing anything):
- 6S projects files\6S_Success_PROGRESS.md            (chapter status, settled decisions, the outline, what the previous chapter handed off)
- 6S projects files\6S_Success_DESIGN_SYSTEM.md       (locked look: palette, fonts, friction meter, page skeleton, CSS)
- 6S projects files\CH8_APPROACH_and_PRODUCTION_GATES.md (the reusable production gates)
- 6S projects files\6S_Success_CHAPTER_SUPERPROMPT.md (this file: outline, friction-meter geometry, sub-package filenames)
- The PREVIOUS chapter's folder 6S-Success-Chapter-<N-1>\ : its CH<N-1>_CANONICAL_STRINGS_AND_BRIEF.md, chapter_<N-1>_final.html (the design + friction-meter template), and the handoff / friction-meter geometry it left. Also skim its content-package\ sub-package structure.
- The source materials in C:\Users\philk\Documents\6S-Success-Trainer.txt and 6ssuccess.txt: grep for this chapter's S-topic (e.g. "Shine", "Standardize", "Safety") and reconcile terminology. If the source has a relevant section, GROUND the chapter in it and note it in the brief; if not, author in the established book voice and mark it a draft.

STEP 1 — FREEZE CANONICAL STRINGS (the source of truth):
Write 6S-Success-Chapter-<N>\CH<N>_CANONICAL_STRINGS_AND_BRIEF.md, modeled EXACTLY on the previous chapter's brief. It must freeze: identity (title, frozen subtitle, part, slug, masthead "Part X · SName" / "Chapter <spelled-out>"), source grounding, continuity (what the previous chapter handed off, exact), what this chapter owns, the hero device + its frozen rule(s), the definition box (frozen), 2 to 3 frozen pull-quote reframes, the frozen friction-meter framing + caption + needle geometry, One Idea to Keep (frozen), the four callouts (Quick Win, Family Challenge, 6S Tip, Common Mistake, frozen), scope fences (do NOT pre-empt neighbor chapters), voice/anti-shame guardrails, the ~8 to 9 section structure, the four figures, companion resources, and the handoff to Chapter <N+1>. If FRICTION_METER_STATE or HERO_DEVICE_NOTE is ASK, propose them (with a short rationale grounded in the friction-meter guide and the arc so far) and confirm with me BEFORE writing the brief.

STEP 2 — AUTHOR THE TRIO:
- chapter_<N>_manuscript.md : ~3,600 to 3,900 prose words, tight. Follow the frozen structure. Use the [VISUAL]/[ILLUSTRATION]/[INFOGRAPHIC] block convention. Include EXACTLY 4 visual blocks (so the manuscript and the 4 HTML figures stay in lockstep from the start). NO em dashes, en dashes, or " - " spaced hyphens anywhere; use the middot "·" for labels/separators. Warm, plain, concrete, anti-shame voice.
- chapter_<N>_signature.md : the authoring plan, modeled on the previous chapter's signature (identity strings, hero device, motifs, emotional + practical purpose, friction-meter call WITH needle geometry, scope fences, figure list, section-by-section outline).
- chapter_<N>_final.html : dispatch a subagent to build it, using the previous chapter's final.html as the EXACT design template (copy its <head> + entire <style> block verbatim; only the <title> changes). Render the manuscript section by section in the locked classes (.masthead/.chno/.eyebrow/.title/.subtitle, .opening drop-cap, .what box, h2 with .kick, .callout win/family/tip/mistake, .pull, .defbox, .idea, .next). Build the 4 inline SVG figures (3 content figures + the friction-meter gauge). Re-plot the friction meter to this chapter's geometry and state. Keep it dash-clean; 4 balanced <figure>/<svg>; frozen strings verbatim. Have the subagent report any wording it changed so you BACK-PORT it into the manuscript (manuscript is the record; the two must agree on every section title, fact, and count).

STEP 3 — VALIDATE THE TRIO before packaging:
Run (export LC_ALL=C): dash scan on manuscript + final.html (em, en, spaced-hyphen excluding list bullets) = 0; manuscript has 4 visual blocks; final.html has exactly 4 <svg> and balanced <figure> tags; masthead/title correct; the frozen rule(s) and friction caption present; friction meter needle at the intended coordinates/state.

STEP 4 — BUILD THE 12 ASSET SUB-PACKAGES via parallel subagents (this is the bulk of the work):
Each subagent reads: this chapter's manuscript, the CH<N> brief, this chapter's content-package\canonical\ (once built), and the SAME sub-package folder from the previous chapter as its exact format template. It writes only its own sub-folder. Order:
  (a) FIRST build canonical\ (8 files) — it holds the frozen strings the rest copy from.
  (b) WAVE A (5 parallel agents): web (7 files + the publishable HTML at content-package root), linkedin (5), facebook (3), x (2), newsletter (4).
  (c) WAVE B (5 parallel agents): video-audio (5), slides (3), pdf-ebook (5), graphics (4), workflow (5).
  (d) LAST build review\ (4 files) — it audits the finished package with real scans.
Exact filenames per sub-package are in the super-prompt reference. Every agent must: reuse frozen strings VERBATIM; produce NO em/en/spaced-hyphen dashes (middot "·" for separators); avoid hype words (unlock, leverage, elevate, supercharge, seamless, game-changing, "almost magical", "fast-paced", "sparkling", "miracle") and force/violence metaphors (attack, "war on dirt", blitz, blast, purge, "pull the trigger"); mark testimonials PLACEHOLDER; keep to the length gates (X posts at or under 280 INCLUDING the number line; LinkedIn posts under 150 words; Facebook longform 300 to 450 words HARD cap); keep JSON (schema-org-article.json, chapter-metadata.json, publishable JSON-LD) and CSV (asset-inventory.csv, 7 columns) valid; make graphics\quote-card-copy.md byte-identical to canonical\chapter-quotes.md. The publishable HTML = final.html + a production <head> (meta description, canonical, Open Graph, Twitter card, JSON-LD Article) with placeholder domain/author/date/og:image.

STEP 5 — REGENERATE THE INVENTORY:
The workflow agent's asset-inventory.csv is scanned mid-build and is a stale snapshot. After ALL sub-packages (including review) exist, regenerate content-package\workflow\asset-inventory.csv from a fresh `find` over all 12 sub-packages (should be 56 rows), reconcile against disk (rows == files), and clear any stale row-count / "snapshot" notes in README.md and production-checklist.md.

STEP 6 — FINAL VALIDATION (real scans, report real numbers, honestly):
Across the whole content-package + manuscript + final.html + publishable HTML: dash scan = 0; hype/force scan (distinguish in-use metaphors from negated prohibitions in editor notes); X thread post count + longest post (<=280); LinkedIn max words (<150); Facebook longform word count (300-450); 4 SVGs + balanced figures; JSON + CSV valid; quote cards byte-verbatim; friction meter in the intended state/coordinates. The review\ files must report only scans actually run, count before writing, grep-verify every cited noun, and reserve "verbatim" for byte-identical strings.

STEP 7 — DESKTOP REVIEW COPY:
Create C:\Users\philk\Desktop\6S-Chapter-<N>-Content-Package\ = the content-package\ contents (12 sub-folders + the publishable HTML at root) PLUS the three source files (chapter_<N>_manuscript.md, chapter_<N>_final.html, chapter_<N>_signature.md) at the root. Verify it is 59 files.

STEP 8 — UPDATE TRACKER + MEMORY, THEN STOP:
Update 6S projects files\6S_Success_PROGRESS.md: change this chapter's line to `[~]` with a full entry in the same style as the previous chapters (what it owns, hero device + rules, worked example, friction-meter state, scope fences, "Full content package (56 files) + publishable HTML + honest review package + final validation complete" with the real numbers, Desktop copy made, companion resources, hands off to Ch <N+1>), and set the "NEXT" pointer. If a Part completed, mark it COMPLETE. Update the project memory note (6s-success-book) current-position line. Then STOP and give me a concise chapter summary for review. Do NOT start the next chapter.

QUALITY BAR: match Chapters 1 to 18 exactly. Tight prose, honest friction meter, frozen strings reused verbatim everywhere, zero dashes, every count true. When a design decision is genuinely open (friction-meter state, hero-device framing, worked example), propose it with a recommendation and confirm with me before committing, rather than guessing.
```

---

## Reference 1 — Settled decisions (apply to every chapter)

- **Six S order:** Sort, Straighten, Shine, **Safety (the 4th S)**, Standardize, Sustain. Safety comes after Shine and is woven through but explicit.
- **No em dashes, en dashes, or " - " spaced hyphens, anywhere, ever.** Use the middot "·" for labels/separators (e.g. "Part Five · Shine", "Chapter 19 · The 15-Minute Reset"), or reword. Markdown list bullets ("- " at line start) are fine.
- **Three source files per chapter:** `chapter_##_signature.md`, `chapter_##_manuscript.md`, `chapter_##_final.html`, plus the frozen `CH##_CANONICAL_STRINGS_AND_BRIEF.md`.
- **Design system is locked:** Fraunces (display) + Newsreader (body) + Inter/sans (labels); warm paper `#F7F2E9` / terracotta `#BC4B2A` / honey `#DDA63A` / slate `#3C5A6B` palette; green calm-dots `#6E8B5B`, red friction-sparks `#CB4B36`. Every final.html copies the previous chapter's `<head>` + `<style>` verbatim. See `6S_Success_DESIGN_SYSTEM.md`.
- **Friction meter** is the recurring chapter-close ritual and the book's one signature device. It is honest: it MOVES only when the chapter changed the room (objects removed/placed, or condition cleaned/caught); it HOLDS when the chapter only built understanding or a plan; it reaches a marked MILESTONE tick when an S completes.
- **Process:** complete each chapter fully, package it, summarize, then STOP for author review before the next. Chapters are authored as drafts; only Ch 1 to 3 are marked reviewed so far (Ch 4 onward await sign-off).
- **Anti-shame voice** throughout: warm, plain, concrete, non-prescriptive, gently witty. No hype words, no force/violence metaphors. Reference Toyota / the Toyota Production System for history; do not overclaim individual originators.
- **Per chapter:** exactly 4 figures (3 content SVGs + the friction-meter gauge); ~3,600 to 3,900 prose words; the content package is 56 files across 12 sub-packages; the Desktop review copy is 59 files.

---

## Reference 2 — The 12 sub-packages and their exact filenames (56 files total)

```
canonical\ (8)   chapter-cta.md · chapter-key-takeaways.md · chapter-metadata.json ·
                 chapter-outline.md · chapter-quotes.md · chapter-seo.md ·
                 chapter-summary.md · chapter-title.txt
web\ (7)         chapter-navigation-copy.md · landing-page-intro.md ·
                 meta-description-options.md · open-graph-copy.md ·
                 read-next-recommendations.md · schema-org-article.json · seo-title-options.md
                 (+ chapter-<N>-publishable.html at the content-package ROOT, built with this wave)
linkedin\ (5)    linkedin-article.md · linkedin-carousel-outline.md ·
                 linkedin-comment-prompts.md · linkedin-newsletter-version.md · linkedin-posts-10.md
facebook\ (3)    facebook-group-discussion-post.md · facebook-longform-post.md · facebook-posts-5.md
x\ (2)           x-short-posts-10.md · x-thread.md
newsletter\ (4)  newsletter-preview-text.md · newsletter-short-teaser.md ·
                 newsletter-subject-lines.md · newsletter-version.md
video-audio\ (5) b-roll-and-visual-notes.md · podcast-script-8-to-12-min.md ·
                 short-video-scripts-5.md · teleprompter-script.md · youtube-script-6-to-8-min.md
slides\ (3)      linkedin-carousel-copy.md · teaching-slide-deck-outline.md · visual-storyboard.md
pdf-ebook\ (5)   back-cover-copy.md · chapter-pdf-frontmatter.md · ebook-description.md ·
                 ebook-sales-copy.md · reader-discussion-questions.md
graphics\ (4)    diagram-ideas.md · image-generation-prompts.md · infographic-spec.md · quote-card-copy.md
workflow\ (5)    README.md · asset-inventory.csv · production-checklist.md ·
                 publishing-calendar.md · repurposing-map.md
review\ (4)      brand-voice-check.md · editorial-review.md · final-package-summary.md · reuse-risk-check.md
```
Count check: 8+7+5+3+2+4+5+3+5+4+5+4 = 55 files + the publishable HTML at the content-package root = 56. Desktop copy adds the 3 source files at its root = 59.

---

## Reference 3 — Friction-meter guide (state + geometry)

**Choosing the state for chapter N:**
- **MOVE** — the chapter changed the room: objects removed or placed (Sort/Straighten) or a surface cleaned and a problem caught (Shine). The needle steps toward calm. Part-opener/action chapters usually move.
- **HOLD** — the chapter only built understanding or a plan (an audit, a photo, a purpose, red-tag planning, a target list). The needle stays put; if the plan will be executed soon, add a dashed forward-projection arrow. Ch 5, 6, 7, 10, and 17 held.
- **MILESTONE** — the chapter COMPLETES an S. The needle reaches a marked tick (e.g. "SORT COMPLETE", "STRAIGHTEN COMPLETE", and next "SHINE COMPLETE"). Ch 11 and 15 were milestones; Ch 19 will be one.
- Always keep the GOAL crosshair AHEAD until the whole book ends, and be honest about how many S's remain.

**Needle geometry used so far (continue the same dial; pivot (210,198), GOAL/"purpose" crosshair (67,155) on the green calm side):**
```
Sort:        Ch8 first move → Ch9 smaller move → Ch10 HOLD → Ch11 milestone "SORT COMPLETE" (~126,102)
Straighten:  Ch12 (110,120) → Ch13 (99,134) → Ch14 (88,146) → Ch15 milestone "STRAIGHTEN COMPLETE" (81,150)
Shine:       Ch16 first step (75,153) → Ch17 HOLD at (75,153) + dashed projection →
             Ch18 step (73,153.5), Ch16/17 now dashed ghost → Ch19 milestone "SHINE COMPLETE" (further toward 67,155, still short of GOAL)
```
Each new chapter: the previous live-needle position becomes the dashed ghost; earlier steps fade further back; the completed-S milestones stay as passed ticks. Never close the gap to the GOAL crosshair while S's remain (Safety, Standardize, Sustain still follow Shine).

---

## Reference 4 — Production gates (from CH8_APPROACH_and_PRODUCTION_GATES.md)

1. **Widened dash scan** (em, en, AND " - " spaced-hyphen used as punctuation; exclude list bullets) across ALL files including manuscript and signature. Standardize separators on "·".
2. **Honest review files:** report only scans actually run; count before you write; grep-verify every cited noun/quote against THIS chapter; use "verbatim" only for byte-identical strings.
3. **Back-port:** the manuscript is the record. Any edit made while building the HTML is written back so manuscript and HTML agree on every fact, count, and section title.
4. **Freeze canonical strings first:** lock one source-of-truth string for every reusable line before the packaging fan-out; agents copy them verbatim, never paraphrase.
5. **Lexical + cadence pass:** cap any single payoff word at ~3 to 5 uses; vary the recurring kicker cadence; do not reuse a loaded praise-word on both sides of the chapter's central contrast.
6. **Single named throughline:** carry the running example (the entryway / launch pad) and its facts verbatim where relevant.
7. **Tone/metaphor audit:** does the imagery match the calm, anti-shame register? No force/effort/violence language.
8. **Number/count integrity:** every count (posts, words, items, the needle's move) agrees across prose, callout, infographic, and package.
9. **Social lengths:** X posts at or under 280 INCLUDING the number line; LinkedIn posts under 150 words; Facebook longform 300 to 450 words (hard cap).

---

## Reference 5 — The full book outline (produce chapter by chapter)

Status key: [x] complete & reviewed · [~] drafted, awaiting review · [ ] not started. (Update from PROGRESS.md.)

**Front matter** [ ] — Title Page · Copyright · Dedication · Acknowledgments · How to Use This Book · Quick Start: Your First 30-Minute 6S Win

**Part 1 · Discovering 6S**
- Ch 1 — Why Some Homes Feel Effortless
- Ch 2 — What Is 6S?
- Ch 3 — The Six Steps That Transform Any Space
- Ch 4 — How to Choose Your First Target Area

**Part 2 · Prepare**
- Ch 5 — The 6S Home Audit
- Ch 6 — Photograph Before You Fix
- Ch 7 — Define the Purpose of the Area

**Part 3 · Sort**
- Ch 8 — Sort: Remove What Does Not Belong
- Ch 9 — Necessary vs. Unnecessary
- Ch 10 — Red Tags, Holding Areas, and Sorter's Remorse
- Ch 11 — What to Donate, Sell, Store, Recycle, or Throw Away  *(SORT COMPLETE milestone)*

**Part 4 · Straighten**
- Ch 12 — Straighten: A Place for Everything
- Ch 13 — Store by Frequency of Use
- Ch 14 — Visual Controls for the Home
- Ch 15 — The Room Map  *(STRAIGHTEN COMPLETE milestone)*

**Part 5 · Shine**
- Ch 16 — Shine: Cleaning as Inspection  *(first Shine step)*
- Ch 17 — Shine Targets and Assignments  *(HOLD, planning)*
- Ch 18 — Cleaning Methods That Actually Work  *(Shine step 2)*
- Ch 19 — The 15-Minute Reset  *(SHINE COMPLETE milestone — turns the plan into a light recurring rhythm)*

**Part 6 · Safety** (the 4th S)
- Ch 20 — Safety: Protect People First
- Ch 21 — Find and Remove Hazards
- Ch 22 — Improve Overall Safety  *(SAFETY COMPLETE milestone)*

**Part 7 · Standardize**
- Ch 23 — Standardize: The Best Way We Know Today
- Ch 24 — Checklists, Schedules, and Responsibilities
- Ch 25 — Pictures, Storyboards, and Visual Standards  *(STANDARDIZE COMPLETE milestone)*

**Part 8 · Sustain**
- Ch 26 — Sustain: Keeping the Gains
- Ch 27 — 6S Audits That Do Not Feel Like Inspections
- Ch 28 — Family Problem Solving
- Ch 29 — Daily 6S Times
- Ch 30 — Your Next 6S Event  *(SUSTAIN COMPLETE — the needle can finally reach the GOAL crosshair here)*

**Part 9 · Room-by-Room Playbooks** (apply the whole loop, room by room)
- Ch 31 Kitchen · Ch 32 Bathroom · Ch 33 Bedroom · Ch 34 Entryway · Ch 35 Living Room · Ch 36 Laundry Area · Ch 37 Garage · Ch 38 Home Office · Ch 39 Kids' Rooms and Play Areas · Ch 40 Closets and Storage Areas

**Appendices** [ ] — Home 6S Audit Form · Sort Checklist · Red Tag Template · Item Disposition Worksheet · Room Map Template · Shine Assignment Matrix · Safety Checklist · Standard Work Template · Daily 6S Checklist · Weekly 6S Schedule · Family Scoreboard · Before/After Photo Guide · 30-Day 6S Home Challenge

---

## Reference 6 — Source materials to reconcile per S

Grep `C:\Users\philk\Documents\6S-Success-Trainer.txt` for the chapter's topic before authoring. Known source sections (home-scale them, reference lightly, do not overclaim):
- **Shine:** "Principles of 6S: Shine Step" — "use cleaning as inspection", "abnormal conditions are easy to spot and fix", "create a like new environment"; Steps to Complete Shine (targets/assignments → methods → initial cleaning and inspection); Traditional Shine Target Categories (Surface, Equipment, Stored Items, Point of Use); points toward Total Productive Maintenance (TPM).
- **Standardize:** "Principles of 6S: Standardize Step" — consistently maintain Sort/Straighten/Shine, prevent reversion, document standards, integrate into daily work, assign accountability, establish checklists and schedules, provide pictures of the ideal state.
- **Safety / Sort / Straighten:** check the same file for the corresponding principle sections and any audit/inspection-sheet terminology, and reconcile the exact wording when present.

---

## Reference 7 — Notes and known open items

- Placeholders left in every chapter for publish time: live domain/URL, author, publisher logo, dates, og:image, and back-cover testimonials (marked PLACEHOLDER). Rotate CTA wording at publish.
- Chapters 5, 6, 7 predate the 450-word Facebook cap and still run ~600 words (usable; trim if desired). Chapter 8 onward is capped.
- Chapters 1 to 3 keep their source files differently (publishable HTML + canonical only at the folder level); Chapters 4 onward carry the full source trio at the folder top level. New chapters follow the Chapter 4+ pattern.
- The friction meter is the one place to spend boldness; keep everything else quiet and disciplined.
