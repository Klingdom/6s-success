# Chapter 21 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_21_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH21_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

Chapter 21 "Find and Remove Hazards" is the SECOND Safety chapter (Part 6). 17 generated plates
landed in the folder. **The generated batch largely drifted off-canon**, so this pass is a
disciplined one: keep the 4 canon-correct SVGs and wire in only the two genuinely-additive,
on-canon reframe photos.

---

## What was done

**2 photos wired in, all 4 existing SVGs RETAINED.** Then finalized to publication standard.

### Final figure layout (6 figures)

| Section | Figure | Source |
|---|---|---|
| Opener (obvious few handled, hidden many remain) | whole-home cutaway | **SVG RETAINED** |
| From a Glance to a Search | `ch21-image02.jpg` "From Glance to Hunt" | photo (NEW) |
| The Hazard Hunt (camouflage reframe) | `ch21-image03.jpg` "The Camouflage Effect" | photo (NEW) |
| The Five Questions | the five-questions card | **SVG RETAINED** |
| A Room-by-Room Hunt | the room-by-room map | **SVG RETAINED** |
| The Needle Takes Another Safety Step | friction meter (Safety step 2) | **SVG RETAINED** |

### Why the two photos are the only ones wired, and the SVGs kept

The two wired photos map exactly onto the chapter's two named reframes, do NOT reword the frozen
five questions, and carry no QR codes:

- **`21-02` "From Glance to Hunt"** — a photoreal split panel, the same living room as A Glance
  ("looks fine, move on") vs. A Hunt ("questions change what you see") with the hidden hazards lit
  up. This is the **thoroughness reframe** made real. Viewed directly before captioning.
- **`21-03` "The Camouflage Effect"** — a photoreal living room where ordinary objects each carry a
  hazard callout ("familiarity makes danger invisible"). This is the **camouflage reframe** made
  real. Viewed directly before captioning.

The three content SVGs (opener, five questions, room-by-room) were kept because **the generated
versions misstate the canon** (see below), exactly the Ch 17/18 situation. The friction-meter SVG
is kept per the standing rule (it carries the SAFETY · STEP 2 needle geometry).

### Finalized to publication standard (same as Ch 1 to 20)

- The two photos optimised **4.8 MB → 0.55 MB** (1600px q82 progressive JPEGs alongside the PNG
  masters; `<img src>` points to the .jpg).
- **Migrated off inline `<style>` + Google Fonts to the shared `../assets/`** (this chapter had not
  yet been migrated).
- `<meta name="description">` added from the frozen subtitle.
- Cross-chapter nav added (prev → Chapter 20, "Chapter 21 of 50"). **Chapter 20's previously-empty
  next-slot was wired forward to Chapter 21.**
- The three `artnote` placeholders removed.
- Verified in-browser: 2 JPEGs load (0 broken), 4 SVGs render, both fonts + shared CSS apply, no
  horizontal overflow, prev-nav resolves to Chapter 20.

### Baked-in defects on the two kept photos (flag for regeneration)

- **`21-02`** — two contractions: "You see **what's** obvious" / "You find **what's** hidden."
- **`21-03`** — two contractions: "a second job you **don't** want" / "The danger **isn't** hidden."
  One callout reads bluntly "Can wrap around a child's neck" (a factual strangulation-hazard label;
  the caption and alt reframe it calmly as "a looped window blind cord"). Softenable at regen.
- Neither carries a QR code, a reworded frozen question, a brand, or an em dash.

---

## HELD BACK · 15 plates (the batch largely drifted off-canon)

This generation run failed the brief in three systemic ways. The **kit prompts I built earlier**
(`C:\Users\philk\Desktop\6S-Illustration-System\prompts\ch21-*.txt`) carry the frozen five questions
verbatim; this batch did not use them faithfully (fresh-chat-per-image + anchor workflow appears to
have been skipped, so ChatGPT drifted).

1. **INVENTED AN ELEVEN-QUESTION SERIES.** The chapter has EXACTLY FIVE frozen questions. The batch
   generated "Question One" through "Question Eleven": `image06`/`image06b` (Q1), `image07`/`image08`
   (Q2), `image09` (Q4), `image10` (mislabeled Q5), `image11` (Q6), `image12` (Q7), `image1` (Q8),
   `image13` (Q9), `image14`/`image15` (Q10), `image16` (Q11). Everything from Q6 on is a **rival
   framework** and is held. (`image10` also restates Q5 as "Could Something Cause a Fall or Injury?"
   — the frozen Q5 is "Could water and electricity meet?")
2. **REWORDED THE FROZEN FIVE.** The two true five-questions plates reword them: `image05` ("The
   Five Questions") drops "here, or catch fire" from Q2, restates Q5 as "Does water meet
   electricity?", and adds a "don't mix" contraction; `image04` ("The Hazard Hunt Process") shortens
   all five on its clipboard and carries an em dash ("yet—just") plus contractions. Both are strong
   layouts but held until the five are set to frozen verbatim. **The canon-correct five-questions and
   room-by-room SVGs are kept instead.**
3. **FAKE QR CODES EVERYWHERE.** Confirmed (not a false positive) real QR-style graphics with
   "Scan for…" text on `image04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16` and `image1` —
   decorative and non-functional, a print defect. Only `image02`, `image03`, `image06b` are QR-free.

Other holds: `image01` ("Uneecured" misspelling + "don't"); duplicates `image07`==`image08` and
`image14`==`image15` (pixel-identical); `image06` vs `image06b` (same Q1 subject; `06b` is the
clean one). **`image06b` is the one other fully clean plate** (no QR, no contraction, correct "6S
TIP") but its prominent "QUESTION ONE" title implies a per-question series the chapter does not use,
so it is held; usable if a Q1 example is ever wanted.

### Regeneration path (recommended)

Regenerate the core figures from the existing kit prompts, which are already canon-correct:
`ch21-01` (opener, green-handled/red-hidden), `ch21-02` (Five Questions, frozen verbatim), `ch21-03`
(Room-by-Room). Use the kit's **one-image-per-fresh-chat + attach-the-anchor** workflow so ChatGPT
cannot drift into the eleven-question invention again, and specify **no QR codes** (already in the
House Style Bible). The infographics can alternatively be built directly as inline SVG.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_21_final.html` was updated.** Chapter text was not
changed.
