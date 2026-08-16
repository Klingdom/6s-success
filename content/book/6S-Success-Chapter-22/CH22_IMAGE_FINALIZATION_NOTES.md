# Chapter 22 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_22_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH22_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

Chapter 22 "Improve Overall Safety" COMPLETES Safety (the 4th S) at the SAFETY COMPLETE milestone.
12 generated plates landed. This batch is much cleaner than Chapter 21's (no invented series, the
four moves are correct, the anti-fear guardrail held), but it carries pervasive baked defects
(decorative QR codes and contractions), so this is a selective pass.

---

## What was done

**3 photos wired in (opener replaced + 2 editorial), all 3 remaining SVGs RETAINED.**

### Final figure layout (6 figures)

| Section | Figure | Source |
|---|---|---|
| Opener (the prepared home) | `ch22-image01.jpg` "The Prepared Home" | photo (replaced opener SVG) |
| Prevent: Keep New Hazards From Taking Hold | `ch22-image06.jpg` "Dangerous Things Have Homes" | photo (NEW) |
| Prepare (baseline) | The Home Safety Baseline card | **SVG RETAINED** |
| Prepare: Ready for What You Cannot Prevent | `ch22-image08.jpg` "The Family Exit Walk" | photo (NEW) |
| The Whole of Safety | The Four Moves of Safety | **SVG RETAINED** |
| The Needle Reaches Safety Complete | friction meter (Safety complete) | **SVG RETAINED** |

Photo figure numbers ascend in document order: 22-01, 22-06, 22-08.

### The three wired photos (viewed directly before captioning)

- **`22-01` "The Prepared Home"** — a detailed, warm cutaway of the whole home, hazards gone, now
  carrying ten labeled preparation marks (smoke alarms every level + tested monthly, a CO alarm near
  the bedrooms, window locks, an accessible fire extinguisher, safe storage, clear exits with two
  ways out, utility shut-offs, emergency supplies, documents in a safe, a family meeting plan).
  **Fully CLEAN** — no QR, no contractions, no brands, no alarmism. A genuine upgrade over the opener
  SVG, so the SVG was replaced.
- **`22-06` "Dangerous Things Have Homes"** — the frozen PREVENT move made concrete ("away means
  protected"): meds, button batteries, matches/lighters, knives, and cleaning chemicals each given
  one locked home. Generic labels (no brand). **Only defect: a decorative QR** ("Safe Storage
  Solutions").
- **`22-08` "The Family Exit Walk"** — the frozen PREPARE emotional core: a family calmly walking
  the exit in daylight to a single meeting tree ("the old oak tree"), with an exit-check list and a
  meeting-place map. Warm, unafraid, on the anti-fear brief. Defects: one contraction ("Simple plans
  are the ones **you'll** use") and a decorative QR ("Family Emergency Plan Template").

### Why the three SVGs were kept over their photo versions

- **The Home Safety Baseline SVG kept over `image02`.** The photo (`image02`) **violates canon**: it
  folds the moves SEE and REMOVE *inside* PREVENT and invents its own PREVENT/PREPARE items ("Create
  Safe Boundaries", "Build Safe Defaults", "Plan Ahead", "Stay Connected") instead of the frozen
  lists (PREVENT = safer default / give dangerous things a home / re-hunt lightly; PREPARE = alarms
  every floor / extinguisher within reach / walked exit + meeting spot / the few numbers everyone
  knows). The SVG states the frozen baseline correctly.
- **The Four Moves of Safety SVG kept over `image03`.** `image03` gets the sequence right (SEE →
  REMOVE → PREVENT → PREPARE) but carries two contractions in its banner ("Safety **isn't** one
  action. **It's** four.") and garbled AI text on its panel-4 clipboard/radio. The SVG is clean.
- **The friction-meter SVG kept** per the standing rule (it carries the SAFETY COMPLETE milestone
  geometry). The photo meters (`image04`, `image12`) are redundant with it.

### Finalized to publication standard (same as Ch 1 to 21)

- The three photos optimised **6.3 MB → 0.72 MB** (1600px q82 progressive JPEGs; `<img src>` .jpg).
- Migrated off inline `<style>` + Google Fonts to the shared `../assets/`.
- `<meta name="description">` added from the frozen subtitle.
- Cross-chapter nav added (prev → Chapter 21, "Chapter 22 of 50"). **Chapter 21's previously-empty
  next-slot was wired forward to Chapter 22.**
- The two `artnote` placeholders removed.
- Verified in-browser: 3 JPEGs load (0 broken), 3 SVGs render, both fonts + shared CSS apply, no
  horizontal overflow, prev-nav resolves to Chapter 21.

### Canon and anti-fear checks

No six-S sequence appears in any wired plate (no Safety-placement risk). The four-moves sequence,
where shown, is correct. **The anti-fear guardrail held across the entire 12-plate set: no fire,
smoke, injury, blood, or a person in danger anywhere** — preparation reads as calm love, exactly as
the brief requires.

### Baked-in defects on wired photos (flag for batch fix; cannot fix without regeneration)

- **`22-06`** — one decorative QR code ("Safe Storage Solutions").
- **`22-08`** — one decorative QR code ("Family Emergency Plan Template") + one contraction
  ("you'll").
- **`22-01`** — fully clean.

These two QR codes join the deferred fake-QR backlog (see `IMAGE_QUALITY_REVIEW_Ch1-17.md` /
memory `6s-image-quality-backlog`); remove or replace with a real live URL before print.

---

## HELD BACK · 9 plates

| Plate | Reason |
|---|---|
| `image02` "The Home Safety Baseline" | **Canon violation** — folds SEE/REMOVE under PREVENT and invents the PREVENT/PREPARE items; the SVG is kept instead. Also a contraction ("can't"). |
| `image03` "The Four Moves of Safety" | Sequence correct, but two banner contractions ("isn't"/"it's") + garbled panel-4 text; the SVG is kept. |
| `image04` "Safety Complete Friction Meter" | Friction-meter recap; redundant with the canonical meter SVG; two "can't" contractions. |
| `image12` "The Friction Meter" | Second friction-meter plate; redundant with the SVG; a "don't" contraction + a QR. |
| `image05` "The Safe Default" | Strong PREVENT (safer-default heater) but a decorative QR; PREVENT is already carried by `image06`. |
| `image07` "The Quiet Drift" | Supports "re-hunt lightly"; a "Don't" contraction + a QR. |
| `image09` "One Shelf of Readiness" | **Real brands** — an "eton" radio and copper-top "Duracell"-style batteries — plus multiple contractions ("doesn't", "we've", "you're", "you'll"). Strong safety-shelf concept; regenerate without branding. |
| `image10` "The Seasonal Safety Reset" | **Real brand** (Duracell-style batteries) + garbled winter-bin text; uses the real Poison Control number. |
| `image11` "Emergency Confidence Map" | Strong emergency-plan board, but an **en dash** ("Hall closet – second shelf") + a "can't" contraction + doubled "Call 911" text + a QR; overlaps `image08`. |

### Systemic issues in the held set (fix at regeneration)

1. **Decorative QR codes on 8 of 12 plates** (all but image01, 02, 03, 04). The book bans fake QR
   codes (they decode to nothing and the captions promise a real resource). Remove them, or encode a
   real live URL.
2. **Contractions on 8 of 12 plates.** House voice uses none.
3. **Real brands** on image09 (Eton, Duracell) and image10 (Duracell). Say "a radio", "batteries";
   never a brand.

The **kit prompts already exist and are canon-correct** (`6S-Illustration-System/prompts/ch22-*.txt`
+ `Chapter 22 - Illustration Kit.html`), including the frozen four moves and the frozen PREVENT/
PREPARE lists, with the House Style Bible forbidding QR codes and brands. Regenerate the baseline and
four-moves plates (and a brand-free safety-shelf and a test-the-alarm plate, which this set lacks)
from the kit, one image per fresh chat with the anchor attached, to avoid the QR/contraction drift.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_22_final.html` was updated.** Chapter text was not
changed.
