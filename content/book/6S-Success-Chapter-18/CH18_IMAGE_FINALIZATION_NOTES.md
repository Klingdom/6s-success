# Chapter 18 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_18_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH18_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

---

## What was done

**4 of 15 photos wired in**, plus **two existing SVG diagrams deliberately RETAINED** because they
are more canon-correct than any supplied photograph. Same disciplined pattern as Chapter 17. Then
finalized to the same publication standard as Chapters 1 to 17.

### Final figure layout (7 figures, one per illustrated section)

| Section | Figure | Source |
|---|---|---|
| A List You Still Dread (opener) | `ch18-image01.png` | photo (replaced the opener SVG) |
| What Makes a Method Actually Work (the test) | the effective-vs-easy SVG | **RETAINED** |
| The Methods That Work (the kit) | the five-methods SVG | **RETAINED** |
| You Do Not Have a Cleaning Problem (reframe) | `ch18-image04.png` | photo |
| A Good Method Still Reads the Surface | `ch18-image05.png` | photo |
| Putting a Method to the List (applied) | `ch18-image06.png` | photo |
| The How Is in Place (closing) | the friction-meter SVG | **RETAINED** |

Photo figure numbers ascend in document order: 18-01, 18-04, 18-05, 18-06.

### Why the two SVGs were kept over the photos

- **The five-methods SVG** lists the exact frozen five, **including the full "Top to bottom, dry
  before wet"** and with **no invented "Dwell Time."** The photo version (`ch18-image03`) drops "dry
  before wet" from method 2, and the whole back half of the supplied set (images 11-15) treats
  "Dwell Time" as a de facto sixth method (most damaging in `image14`, whose printed formula replaces
  "Fewer, Simpler Products" and "Clean in Passing" with "Dwell Time"). Keeping the SVG protects the
  canonical five.
- **The effective-vs-easy SVG** states the working method as "clean enough to matter, easy enough to
  repeat," with the two failure modes (whole-Saturday scrub, spray-and-walk-away) falling short. The
  photo version (`ch18-image02`) is strong but carries a contraction ("Doesn't") and a rule variant
  ("...actually repeat" rather than the frozen "...actually do").

### The four photos are on-brief and add real value

- **`18-01`** "Same Target. Different Method / Better Method" — the opener. Same stove, 40 dreaded
  minutes and a cupboard of products vs 2 minutes and two bottles, with the Ch 17 checklist between
  them (stove circled). Photoreal, faces and hands clean.
- **`18-04`** "Cleaning Is Usually a Method Problem" — the reframe ("You are not lazy. Your method
  is."). The old cluttered way vs the smarter two-bottle way.
- **`18-05`** "Reading While Cleaning" — the inspection tie. A wipe reveals a loose screw, water
  damage, a scratch, a crack, grease buildup: "a working method cleans and inspects at the same
  time." **Fully clean voice, no defects.** The strongest plate in the set.
- **`18-06`** "Three Targets, Three Better Methods" — the applied section. Launch pad, oven, and
  door handles, each given a better method.

### Finalized to publication standard (same as Ch 1 to 17)

- The four photos optimised **8.4 MB → 0.9 MB** (1600px q82 JPEGs alongside untouched PNG masters).
- `<meta name="description">` added from the frozen subtitle.
- Google Fonts dropped; head links the shared `../assets/`.
- Cross-chapter nav added (prev → Chapter 17). **Chapter 17's previously-empty next-slot was wired
  forward to Chapter 18.**
- **Book-wide consistency fix:** the chapter-count in every nav (Ch 1 to 18) was normalised from
  "of 40" to **"of 50"** to match the expanded 50-chapter scope.
- Verified in-browser: 4 JPEGs load, 3 SVGs render, both self-hosted fonts load, shared CSS resolves,
  prev-nav resolves 200 to Chapter 17, no overflow, every figure captioned.
- Both remaining `artnote` placeholders (in the retained SVGs) removed.

### Checks

No six-S sequences in any wired figure, so no Safety or "Set in Order" errors. No QR codes anywhere
in the whole Chapter 18 set (a rare clean result). The friction meter correctly MOVES (the retained
SVG carries the step geometry).

---

## Baked-in defects on kept photos (flag for regeneration; cannot fix without image generation)

- **`18-01`** — one bottle label reads **"DEGRASER"** (should be "Degreaser"). It is on the cluttered
  "old way" side, small, but a visible misspelling.
- **`18-04`** — several bottle labels on the crowded "old way" side are **garbled AI text** (e.g.
  "RUEXAEM CLEANER", "ALL FUYOARS CLEANER"). They read as clutter at reading size but are garble on
  close inspection; clean them at regeneration.
- **`18-06`** — two soft issues: the oven column's better-method reads **"Use dwell time"**, and
  "dwell time" is NOT one of the frozen five methods (it is presented as a contextual tip here, not
  as a named member of the five, so it is the mildest instance of the chapter-wide "Dwell Time"
  drift); and the oven "before" caption says **"Aggressive scrubbing steals your entire evening,"**
  which is force-adjacent language describing the old way (the book bans combat metaphors for the
  cleaning act). Neither is a hard violation; both are worth softening if regenerated.
- `18-05` is fully clean.

---

## HELD BACK · 11 images

### Held because the SVG is more canon-correct

- `ch18-image02` "The Working Method Matrix" — strong hero-device plate, but duplicates the retained
  effective-vs-easy SVG and carries a contraction + a rule variant. Usable if the SVG is ever dropped.
- `ch18-image03` "Five Methods That Work" — drops "dry before wet" from method 2; the retained
  five-methods SVG is the complete canonical version.
- `ch18-image07` "The Friction Meter" — the chapter's own retained meter SVG carries the correct MOVE
  geometry; this photo version is redundant.

### Held for CANON / SCOPE reasons

| Plate | Reason |
|---|---|
| `image08` "From Project to Habit" | A **rival numbered six-step system** (Purpose / Targets / Ownership / Methods / Routine / Habit) with no Safety, competing with the six S's, plus a prominent preview of Ch 19's routine material. |
| `image14` "Build Your Own Method in Four Steps" | The printed formula **replaces two frozen methods with "Dwell Time"** ("Right Tool + Dwell Time + Top to Bottom + Point of Use"); step 4 "Standardize the steps... automatic, not a decision" drifts into Standardize/Sustain. The most damaging instance of the Dwell-Time drift. |
| `image15` "Match the Method to Your Life" | Example 3 is a **"Small, Daily Reset"** plus "End of Day Reflection" — the Ch 19 routine/cadence fence. Also em dashes + contractions. |
| `image11`, `image12`, `image13` | The three back-half "which method / cheat sheet / pairings" tables — heavily **redundant** with each other, all promote **"Dwell Time"** as a method, and carry em dashes and contractions. |
| `image09`, `image10` | Method-match table and selection-flow; on-theme but redundant with the tables above, with contractions and (image10) two em dashes. |

### Systemic issues across the held set (fix at regeneration)

1. **Invented "Dwell Time" method:** treated as a de facto sixth working method across images 06, 09,
   11, 12, 13, 14, 15. It is not one of the frozen five. Remove it or fold it into a frozen method.
2. **"Dry before wet" dropped:** method 2 renders as just "Top to Bottom" on the photo plates; the
   frozen method is "Top to bottom, **dry before wet**." The retained SVG has it right.
3. **Hero rule never printed verbatim:** the frozen rule is "The best method is the one you will
   actually do." Every photo prints a variant.
4. **Em dashes** on images 10, 12, 15; **contractions** on 02, 09, 10, 11, 12, 14, 15.

### The pattern, now seven chapters running

The held block drifts the same way Chapters 12 to 17's did: **forward into Ch 19 (routine/reset/
cadence) and sideways into Standardize/Sustain (standardize-the-steps, daily reset, habit).** For a
methods chapter that specifically means the "make it a routine / do it daily" material, which is
Chapter 19's job. Chapter 18's frozen brief calls Ch 19 the CRITICAL fence, and several plates cross
it. The generation brief still is not carrying the fences.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_18_final.html` was updated.** Any publishable
variant, content-package, and Desktop flattened copy would need building from this final. Chapter
text was not changed (the manuscript runs 3,819 words, within the 3,600 to 3,900 target).
