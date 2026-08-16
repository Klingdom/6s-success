# Chapter 23 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_23_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH23_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

Chapter 23 "Standardize: The Best Way We Know Today" OPENS Part 7 (Standardize, the 5th S). 13
generated plates landed. The set is warm and human (the chapter's "corporate" danger word was well
avoided) but carries decorative QR codes on 11 of 13 plates and pervasive contractions, so this is a
selective, QR-averse pass.

---

## What was done

**2 photos wired in (opener replaced + one editorial), all 3 remaining SVGs RETAINED.**

### Final figure layout (5 figures)

| Section | Figure | Source |
|---|---|---|
| Opener (out of one head, onto the walls) | `ch23-image01.jpg` | photo (replaced opener SVG) |
| The Best Way We Know Today | The living-standard loop | **SVG RETAINED** |
| Write Your First Standard (the card) | The sample standard card | **SVG RETAINED** |
| Write Your First Standard (writing it) | `ch23-image06.jpg` "One Task, One Card" | photo (NEW) |
| The Needle Holds, and Stops Sliding Back | friction meter (HOLD + catch) | **SVG RETAINED** |

Photo figure numbers ascend in document order: 23-01, 23-06.

### The two wired photos (both QR-FREE; viewed directly before captioning)

The automated cv2 QR scan reported none, but a visual audit found **decorative QR codes on 11 of 13
plates**. Only `image01` and `image06` are QR-free, and both are strong and on-message, so they are
the two wired:

- **`23-01` (opener)** — a warm, photoreal "out of one head, onto the walls": a mother with a
  thought-bubble of the best ways she keeps in her head, soft light-strings carrying them onto small
  cards taped at each point of work, and the family already using them. A genuine photoreal upgrade
  over the opener SVG, so the SVG was replaced. Warm, human, not corporate.
- **`23-06` "One Task, One Card"** — the warm act of handwriting the first standard: a woman writing
  a numbered dishwasher-loading recipe card with a "keep it simple" anatomy panel (title / what you
  need / steps in order / notes / ownership) and a tip that the first card is the only hard one.
  Ownership reads "we all follow and update this" (no assigned names), the card is a numbered RECIPE
  (no checkboxes, no schedule) — fully within the Ch 23 fence. Placed at the end of *Write Your First
  Standard*, after the sample-card SVG.

### Why the three SVGs were kept

The living-standard loop SVG, the sample-standard-card SVG, and the friction-meter SVG are all
canon-clean. Their strong photo counterparts all carry decorative QR codes (and contractions), so the
SVGs were kept rather than wire QR plates:

- `image05` (the living-standard loop / continuous-improvement cycle) — strong and on-concept, but a
  QR + two contractions. The loop SVG is kept.
- `image03` (the literal "A Standard Is a Recipe" card) — the best recipe rendering, but a QR + two
  contractions. The card SVG is kept.
- The friction-meter SVG is kept per the standing rule (HOLD + first-catch-against-backslide
  geometry). `image04`/`image12` are redundant photo meters.

### Finalized to publication standard (same as Ch 1 to 22)

- The two photos optimised **4.8 MB → 0.51 MB** (1600px q82 progressive JPEGs; `<img src>` .jpg).
- Migrated off inline `<style>` + Google Fonts to the shared `../assets/`.
- `<meta name="description">` added from the frozen subtitle.
- Cross-chapter nav added (prev → Chapter 22, "Chapter 23 of 50"). **Chapter 22's previously-empty
  next-slot was wired forward to Chapter 23.**
- The two `artnote` placeholders removed.
- Verified in-browser: 2 JPEGs load (0 broken), 3 SVGs render, both fonts + shared CSS apply, no
  horizontal overflow, prev-nav resolves to Chapter 22.

### Canon, fence, and tone checks

No six-S sequence appears in any wired plate. **The "corporate" tone was well avoided across the set**
— cards are warm handwritten notes, not bureaucratic binders. The two wired plates keep the Ch 23
fence (a recipe with numbered steps + "we all" ownership; no checklist tick-boxes, no schedule, no
assigned names, no visual-ideal-state standard).

### Baked-in defects on the two wired photos (flag for regeneration)

- **`23-01`** — em dashes ("Top rack**—**cups", "Bottom rack**—**plates") and en dashes ("Paper **–**
  Mon", "Plastic **–** Wed", "Glass **–** Fri", "Compost **–** Daily") in the tiny taped-card text;
  and two of the taped cards are SCHEDULE-format (Pet Feeding times, Recycling day-of-week), which
  lean toward Chapter 24's material. Both are batch-fixable at regeneration (swap the dashes for
  commas/words; swap the two schedule cards for recipe cards). QR-free.
- **`23-06`** — one contraction ("**Don't** block the arms," step 4). QR-free.

---

## HELD BACK · 11 plates

The dominant reason is a decorative QR code ("GET THE FREE STANDARD CARD TEMPLATE" / "SCAN FOR
EXAMPLES") on all of them, usually with contractions, and in several cases a scope-fence breach.

| Plate | Reason |
|---|---|
| `image02` "Why Homes Drift Back" | QR + subtitle contraction ("don't") + before/after ROOM comparison sits near the Ch 25 fence. |
| `image03` "A Standard Is a Recipe" | QR + two contractions ("Don't", "It's"). **Strongest recipe plate** — regen without QR and it could replace the card SVG. |
| `image04` "What Makes a Good Standard" | QR + contraction; near-duplicate of image03. |
| `image05` "The Best Way We Know Today" | QR + two contractions ("doesn't", "That's"). **Strong loop plate** — regen without QR and it could replace the loop SVG. |
| `image07` "Put It Where the Work Happens" | QR + two contractions ("can't", "won't") + the control word "**rules**" ("Simple rules for an organized pantry"), which this chapter avoids. Strong 6S-Tip plate; regen. |
| `image08` "Tiny Cards, Big Results" | **Ch 24 FENCE BREACH** — the launch-pad card is a tick-box CHECKLIST; + contractions + QR. |
| `image09` "Living Standards" | Five contractions + QR. Concept (the card rewritten, before/after of the WRITTEN standard) is on-topic and salvageable. |
| `image10` "Standards Work Best Together" | Multiple contractions + a non-recipe family values LIST with check-marks + a possible garbled glyph + QR; leans Sustain. |
| `image11` "Keep It Alive" | Tick-box CHECKLIST family card (Ch 24-adjacent) + contractions + QR; near-duplicate of image10. |
| `image12` "Lead by Example" | Off the three core Standardize sections (leadership/modeling, leans Sustain) + contraction + QR. |
| `image13` "Small Habits. Big Difference." | Off-core (habits/Sustain-flavored) + contractions + QR. |

### Systemic issues (fix at regeneration)

1. **Decorative QR codes on 11 of 13 plates.** The book bans fake QR codes. Remove, or encode a real
   live URL. (The cv2 scan missed these — they are stylized; always confirm QR visually.)
2. **Contractions on most plates.** House voice uses none.
3. **Ch 24 fence creep:** tick-box checklist cards (image08, image11) and schedule cards (image01,
   image10) — Chapter 23's standard is a written RECIPE; checklists, schedules, and responsibilities
   are Chapter 24. Several plates (image10-13) also drift into Sustain/family-culture territory.

The **kit prompts already exist and are canon-correct** (`6S-Illustration-System/prompts/ch23-*.txt`
+ `Chapter 23 - Illustration Kit.html`): the living-standard loop, the recipe card ("no other text"),
and the warm-not-corporate rule, with the House Style Bible forbidding QR codes. Regenerate the loop
(`image05`-style) and the recipe card (`image03`-style) from the kit, one image per fresh chat with
the anchor attached, and they can replace the two kept SVGs.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_23_final.html` was updated.** Chapter text was not
changed.
