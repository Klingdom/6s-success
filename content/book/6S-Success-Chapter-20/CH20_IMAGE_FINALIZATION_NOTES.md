# Chapter 20 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_20_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH20_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

Chapter 20 "Safety: Protect People First" **OPENS Part 6 (Safety, the 4th S)**. It is the landmark
part-opener, so the canon check (Safety must appear FOURTH) and the anti-fear guardrail were the two
governing constraints of this pass.

---

## What was done

**7 photographs wired in**, plus **two existing SVGs deliberately RETAINED** (the triage/pyramid
diagram and the friction meter). The photo set for this chapter is strong and, unusually, mostly
canon-clean, so three of the four opener/concept SVGs were replaced with photographs and three
previously-unillustrated sections gained photographs. 9 figures total, all verified in-browser.

### Final figure layout (9 figures)

| # in doc | Section | Figure | Source |
|---|---|---|---|
| 1 | Opener · a finished home, quietly dangerous | `ch20-image01a.jpg` (prints "20-01") | photo (replaced opener SVG) |
| 2 | Why Safety Is Its Own S | `ch20-image03.jpg` (prints "20-03") | photo (NEW) |
| 3 | The Safety Lens | `ch20-image02.jpg` (prints "20-02") | photo (replaced the two-lenses SVG) |
| 4 | Protect People First | triage two-axis plot + Heinrich pyramid | **SVG RETAINED** |
| 5 | Safety Is Love, Not Fear | `ch20-image08.jpg` (prints "20-08") | photo (NEW) |
| 6 | A First Safety Pass | `ch20-image09.jpg` (prints "20-09") | photo (NEW) |
| 6 | A First Safety Pass (at the 6S Tip) | `ch20-image10.jpg` (prints "20-10") | photo (NEW) |
| 7 | The Needle Takes Its First Safety Step (at the Family Challenge) | `ch20-image11.jpg` (prints "20-11") | photo (NEW) |
| 8 | (closing) friction meter, FIRST SAFETY STEP | the friction-meter SVG | **SVG RETAINED** |

### The two SVGs kept, and why

- **The triage / pyramid SVG (FIGURE 3) was kept over the photo `ch20-image07`.** The SVG teaches
  BOTH halves of "protect people first": the two-axis triage plot (rank by *how badly* × *how soon*,
  worst-and-soonest fixed first) **and** the Heinrich pyramid. The photo (`image07`) draws only the
  pyramid and carries contractions ("shouldn't", "don't"). The two-axis triage is the actual hero
  method of the section, so the more complete, canon-clean SVG stays. (Same discipline as Ch 17/18.)
- **The friction-meter SVG (FIGURE 4) was kept per the standing rule** (data-driven needle geometry;
  it carries the exact FIRST-SAFETY-STEP position off the Shine-complete milestone). The photo
  version of the meter (`image12`) is held for a canon violation — see below.

### Canon check (the reason this chapter mattered most)

- **`ch20-image03` "The Fourth S" is canon-perfect and is the most valuable plate in the set.** It
  prints **Sort → Straighten → Shine → Safety**, correct terms (Straighten, not "Set in Order";
  Shine, not "Sweep"), with **Safety in the fourth position**, and it is drawn in the book's own
  serif/cream design-system style. It visually cements the chapter's whole thesis exactly where the
  text argues it. Verified by direct viewing.
- All seven wired photos were viewed directly before captioning. None violates the six-S canon.
- **Anti-fear guardrail held:** the two plates showing children (`image08` Safety Is Love, `image11`
  Family Safety Walk) both show the child SAFE, calm, and engaged, never in danger or distress. No
  blood, no graphic injury, no scare statistics, no force metaphors anywhere in the wired set. Safety
  reads as calm love that reduces worry, per the brief.
- No QR codes anywhere in the entire 13-image set (visually confirmed + OpenCV scan; clean result).
- No em/en dashes in any wired plate. No real brand logos (bottle labels are generic descriptors,
  e.g. "MULTI-SURFACE CLEANER").

### Finalized to publication standard (same as Ch 1 to 19)

- The seven photos optimised **15.1 MB → 1.4 MB** (1600px q82 progressive JPEGs alongside untouched
  PNG masters; `<img src>` points to the .jpg).
- **Migrated off the old inline `<style>` + Google Fonts to the shared `../assets/`** (this chapter
  had NOT yet been migrated; Ch 1-19 already were). `book.css` already contains every class Ch 20
  uses (`.plate`, `figure.wide/.tall`, `.defbox`, `.checklist`, `.chnav`).
- `<meta name="description">` added from the frozen subtitle.
- Cross-chapter nav added (prev → Chapter 19, "Chapter 20 of 50"). **Chapter 19's previously-empty
  next-slot was wired forward to Chapter 20.**
- The one `artnote` placeholder removed.
- **Verified in-browser (localhost):** 7 JPEGs load (0 broken), 2 SVGs render, both self-hosted fonts
  apply (Fraunces on the title), shared CSS resolves (paper background), every figure captioned, no
  horizontal overflow, prev-nav resolves to Chapter 19.

### One deliberate, minor cosmetic note (figure-number order)

Because content placement was prioritised, the **printed figure numbers run 20-01, 20-03, 20-02** in
document order: "The Fourth S" (baked "20-03") belongs to *Why Safety Is Its Own S*, which precedes
*The Safety Lens* where the two-lenses plate (baked "20-02") lives. The 03/02 pair is therefore
inverted on the page. It was accepted rather than dropping the canon-perfect `image03`. If strict
ascending numbering is wanted, regenerate `image02` and `image03` with their baked corner numbers
swapped; no other change is needed.

---

## Baked-in defects on kept photos (flag for regeneration; cannot fix without image generation)

The wired seven are clean of the serious classes. Only micro-issues remain:

- `ch20-image09` and `ch20-image11` each show a clipboard prop whose tiny list text is partly
  garbled at close inspection (illegible at reading size). Cosmetic.
- `ch20-image11`'s boy carries a "SAFETY WALK CHECKLIST" (Smoke alarms / Outlets / Rugs / Chemicals
  / Cords / Windows-Locks / Heavy Items / Sharp Corners / Small Objects / Other). This reads as an
  illustrative prop, not the exhaustive "safety questions" checklist reserved for **Ch 21**, so it is
  in scope (same judgement as Ch 19-10's timed walkthrough vs. the Standardize fence).
- No contractions, em dashes, QR codes, brands, or force metaphors on any of the seven wired plates.

---

## HELD BACK · 6 of Chapter 20's images

| Plate | Reason |
|---|---|
| `ch20-image01` | Opener duplicate of the wired `image01a`, but its title prints a contraction, "The Beautiful Home That **Isn't** Safe." Usable if the title is reworded; `image01a` (clean, same five hazards) was wired instead. |
| `ch20-image06` | Near-identical duplicate of `image01` (same "Isn't" title). Redundant. |
| `ch20-image04` "Looking Through the Safety Lens" | On-brief (the lens applied), but carries multiple contractions ("don't", "what's" ×3) and garbled bottle labels. `image02` + `image09` cover this ground cleanly. |
| `ch20-image05` "What Counts as a Hazard?" | A 3×3 hazard catalog; on-theme but carries a contraction ("aren't") and garbled product labels. The `defbox` definition + `image01a`/`image10` cover the "hazards look tidy" point. |
| `ch20-image07` "The Safety Pyramid" | Redundant with the retained triage/pyramid SVG (which also carries the two-axis triage the photo omits) and carries contractions ("shouldn't", "don't"). |
| `ch20-image12` "The Friction Meter" | **CANON VIOLATION (held).** Its progress rail inserts an invented step **"Find Hazards"** as step 5, creating a 7-step framework that pushes **Standardize to 6th and Sustain to 7th** (they are the 5th and 6th S's). Also a friction-meter photo, which the standing rule keeps as SVG. |
| `ch20-image13` "What Comes Next" | **CANON VIOLATION (held).** Prints a numbered **1–7** rail with the same invented **"Find Hazards" = #5**, displacing Standardize (→6) and Sustain (→7). A rival numbered framework in the very chapter that defines the S-order. |

### The systemic pattern, continued

The two held canon-violating plates (`image12`, `image13`) both invent a **"Find Hazards" 6th/7th
step**. This is the same generation drift seen since Ch 12: the brief's scope fences are not reaching
the image generator. Here it takes the specific form of promoting Chapter 21's topic ("Find and
Remove Hazards") to a numbered step in the six-S sequence itself. The frozen brief explicitly reserves
the hazard hunt for Ch 21 as a CRITICAL fence; the generator crossed it and, worse, corrupted the
canonical S-order to do so. Regeneration request: remove "Find Hazards" as a step; the six S's are
Sort · Straighten · Shine · Safety · Standardize · Sustain, full stop, with Safety fourth. Point the
regen at `6S-Success-Chapter-3/ch3-image2.png` (the canon-correct full loop).

### Held-plate resolution (2026-07-22)

Both held canon-violation plates were dispositioned via a focused replacement kit at
`C:\Users\philk\Desktop\6S-Illustration-System\Chapter 20 - Held-Plate Replacements.html`
(prompt: `prompts/ch20-13R.txt`), built on the shared House Style Bible.

- **`image12` "The Friction Meter" → RETIRED, no replacement.** A photographic friction meter is
  redundant by design: the chapter already carries the canonical data-driven friction-meter SVG, which
  the standing rule keeps as live SVG. Nothing to regenerate.
- **`image13` "What Comes Next" → REPLACE with Figure 20-13R "The Journey So Far"** (canon-correct
  six-S track: Sort/Straighten/Shine done, Safety current/"you are here", Standardize and Sustain
  ahead; exactly six steps, Safety fourth, NO "Find Hazards"). The prompt hard-guards against the
  defect ("exactly six stops... no seventh step... never an added step such as Find Hazards"). It is
  **optional to wire**, because the friction-meter SVG already conveys the same progress abstractly;
  wire it only if an explicitly named-steps orientation is wanted at the chapter close. Phil generates
  it (or it is built as inline SVG) and it wires into the "Safety Has Only Begun" close.

The chapter as wired is already complete and canon-correct without either plate; this resolves the
held items rather than leaving them open.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_20_final.html` was updated.** Any publishable
variant, content-package, and Desktop flattened copy would need building from this final. Chapter text
was not changed (the manuscript runs long against the 3,700 to 4,000 target; a trim is a separate
editorial pass, not part of image finalization).
