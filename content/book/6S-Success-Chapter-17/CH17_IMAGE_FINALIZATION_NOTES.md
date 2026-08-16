# Chapter 17 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_17_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH17_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

---

## What was done

**3 of 16 images wired in**, plus **two existing SVG diagrams deliberately RETAINED** because they
are more canon-correct than any supplied photograph. Then finalized to the same publication standard
as Chapters 1 to 16.

This was the hardest chapter to date, for a specific reason: **the two artifacts at the heart of the
chapter, the four target categories and the Shine list itself, are already rendered as canon-perfect
SVGs, and every photographic version of them contradicts the frozen spec.** So the right move was to
keep the SVGs and add photos only where they help without contradicting canon.

### Final figure layout (6 figures, one per illustrated section)

| Section | Figure | Source |
|---|---|---|
| One Zone Clean, a Whole House Unnamed (opener) | `ch17-image01.png` | photo (replaced the opener SVG) |
| What Counts as a Target (four kinds) | the four-kinds SVG | **RETAINED** |
| The Shine List (hero) | the Shine-list SVG | **RETAINED** |
| Clean the Whole Thing (targets rule) | `ch17-image05.png` | photo |
| Put a Name on Every Target (assignments) | *(text + the hero list)* | — |
| Choosing, Not Assigning | `ch17-image09.png` | photo |
| The Needle Holds (closing) | the friction-meter SVG | **RETAINED** |

Figure numbers on the photos ascend in document order: 17-01, 17-05, 17-09.

### Why the two SVGs were kept over the photos

Both retained SVGs use the **exact frozen category names** and the **correct categorisation**, which
every photo gets wrong:

- The four-kinds SVG reads **SURFACES / EQUIPMENT AND FIXTURES / STORED THINGS / POINT OF USE**, with
  Point of Use correctly holding "handle, switch, remote."
- The Shine-list SVG has a **name against every line** (Dad, Mia, Mum, Sam, Leo), the four frozen
  category headings, one line left blank ("still waiting for a name") to show choosing, and crucially
  **no frequency column** — it is a target inventory plus owners, exactly as the frozen definition
  requires.

The photographs of these same artifacts (`17-02`, `17-04`, `17-13`, `17-16`) all:
1. **rename the categories** to "EQUIPMENT" and "STORED ITEMS" (not the frozen "Equipment and
   fixtures" / "Stored things"), and
2. **miscategorise** light switches and door handles under Surfaces, contradicting the frozen Point
   of Use and the retained SVGs, and
3. (the list plates 04/13/16) **add a FREQUENCY / schedule column**, which is the chapter's single
   CRITICAL frozen fence: "The Shine list is a ONE-TIME target inventory + owners, NOT a chore chart
   with a schedule." `17-04` additionally adds a "Last Done" habit-tracker column.

Using any of those photos would have introduced a within-chapter contradiction and crossed the
critical schedule fence. Keeping the canon-perfect SVGs was the disciplined call.

### The three photos are on-brief and add real value

- **`17-01`** "One Clean Corner Is Not a Clean Home" — the opener. A clean styled corner beside a
  grid of eight neglected hidden spots (tops, behinds, insides, switches, remotes, handles). Delivers
  the whole-home reframe and the invisible-target insight. Fully clean voice, no QR.
- **`17-05`** "Cleaning What Shows vs. Cleaning the Whole Target" — the targets rule. Four targets
  (coils, cabinet tops, sink overflow, hood filters) shown surface-only vs whole-target: "Clean the
  whole target, every time."
- **`17-09`** "Choosing vs. Being Assigned" — the best plate in the set for choosing-not-assigning.
  "Choice creates care. Care creates consistency."

### Finalized to publication standard (same as Ch 1 to 16)

- The three photos optimised **6.1 MB → 0.7 MB** (1600px q82 JPEGs alongside untouched PNG masters).
- `<meta name="description">` added from the frozen subtitle.
- Google Fonts dropped; head links the shared `../assets/`.
- Cross-chapter nav added (prev → Chapter 16). **Chapter 16's previously-empty next-slot was wired
  forward to Chapter 17.**
- Verified in-browser: 3 JPEGs load, 3 SVGs render, both self-hosted fonts load, shared CSS resolves,
  prev-nav resolves 200 to Chapter 16, no overflow, every figure captioned.
- Both `artnote` placeholders (in the retained four-kinds and Shine-list SVGs) removed.

### Checks

No six-S sequences anywhere, so no Safety or "Set in Order" errors. The friction meter correctly
HOLDS (the retained SVG carries the hold geometry).

---

## Baked-in defects on kept photos (flag for regeneration; cannot fix without image generation)

- **`17-05`** — an em dash in the subtitle ("the entire target—every side, every layer"), the
  contraction "don't", and a QR code ("SEE MORE EXAMPLES").
- **`17-09`** — the contraction "You'll", and a QR code ("TOOLS TO HELP").
- `17-01` is clean of contractions, em dashes, and QR codes.

---

## HELD BACK · 13 images

### Held for CANON / SCOPE reasons (the important ones)

| Plate | Reason |
|---|---|
| `17-02` "The Four Types of Shine Targets" | Beautiful, but renames categories ("EQUIPMENT" / "STORED ITEMS") and puts **light switches + door handles under Surfaces** (frozen = Point of Use). Would contradict the retained canon-correct four-kinds SVG. |
| `17-04` "The Shine List" | **Adds a FREQUENCY column AND a "Last Done" tracker** — crosses the CRITICAL schedule fence (that is Ch 19 / Sustain). Also renamed categories. This is the hero artifact rendered wrong. |
| `17-13` "From Invisible Responsibility to Shared Ownership" | The list thumbnail has a Frequency column; footer "Review. Refresh. Repeat" is Sustain maintenance-over-time. |
| `17-16` "Our Shine List" | Organised by **AREA/room, not the four categories**, and has a **Frequency column** — a chore chart with a schedule. |
| `17-07` "Every Target Needs an Owner" | Steps 3-4 (Inspection / Maintenance, "follow the frequency, do the work") push into Ch 19 and Standardize/Sustain. |
| `17-10` "Age-Appropriate Shine Assignments" | Task verbs ("clean the oven", "change HVAC filters") lean Ch 18 how-to; "make it part of the routine" leans Ch 19. |
| `17-15` "Friction Meter" | The chapter's own retained meter SVG carries the correct HOLD geometry; this photo version also has an em dash in its title. |

### Held as redundant or voice-heavy

- `17-03` (categories across the home) — same category-rename issue + an em dash; redundant with the four-kinds SVG.
- `17-06` (visible vs hidden maintenance) — near-duplicate of `17-05`, plus the typo **"dishwasker"** and contractions.
- `17-08` (the invisible load) — on-message emotionally, but the **worst voice offender** in the set (many contractions + an em dash).
- `17-11` (fair household workload) and `17-14` (20 forgotten targets) — **both are genuinely strong, clean plates held only because their figure numbers (11, 14) would appear out of order after the choosing plate (09).** They are usable if renumbered at regeneration; `17-14` in particular is an excellent invisible-target catalogue.
- `17-12` (first Shine walk) — good list-building content, correctly holds action, but em dash + contractions and number (12) breaks order.

### Systemic issues to fix at regeneration

1. **Category names:** every categorised photo says "EQUIPMENT" and "STORED ITEMS." The frozen and
   canon-correct names are **Equipment and fixtures** and **Stored things**. Regenerate to match.
2. **Switch/handle placement:** light switches and door handles must sit under **Point of Use**, not
   Surfaces.
3. **No frequency column on the Shine list:** the Shine list is targets + owners only. Remove the
   Frequency and Last-Done columns from `17-04`, `17-13`, `17-16` (that content belongs to Ch 19).
4. **QR codes:** nine of the sixteen plates carry QR codes (17-04 through 17-12). None was
   machine-tested this pass; test before print, and note that every QR in this project so far has
   decoded to an empty payload.

### The pattern, now six chapters running

The held block drifts the same way Chapters 12 to 16's did: **forward into the next chapters (Ch 18
technique, Ch 19 routine/schedule) and sideways into Standardize and Sustain (frequency columns,
"review and repeat" loops, habit trackers).** For a targets-and-assignments chapter that specifically
means chore charts with schedules. Chapter 17's frozen brief calls the schedule the CRITICAL fence,
and the hero-artifact photos cross it anyway, so the generation brief still is not carrying the fences.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_17_final.html` was updated.** Any publishable
variant, content-package, and Desktop flattened copy would need building from this final. Chapter text
was not changed (the manuscript already runs 4,185 words against a frozen 3,600 to 3,900 target).
