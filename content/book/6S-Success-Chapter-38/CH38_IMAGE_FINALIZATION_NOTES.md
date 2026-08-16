# Chapter 38 (The Guest Bedroom) — Image Finalization Notes

**Pass run 2026-07-31.** Batch of 20 plates, all viewed before anything was placed.
**Result: 7 wired, 3 canon SVGs kept, 13 held.**
Master `chapter_38_final.html` only. Backup at `chapter_38_final.html.bak-images`.
Packages deliberately NOT propagated.

**This is the second-strongest batch of the eight room chapters, behind Chapter 34, and it breaks the
worst pattern of the run: only ONE plate in twenty carries a fake QR code, against sixteen of twenty
in Chapter 36.** Four of the seven wired plates carry this chapter's frozen reframes almost word for
word.

---

## Wired (7)

| Plate | Placement | Why it passed |
|---|---|---|
| `ch38-image01` | Opener, **replaces the opener SVG** (viewBox 0 0 1000 560) | True matched before/after. The before shows exactly the frozen draw-the-line problem: the room absorbing boxes, laundry and an exercise bike. The after shows a clear path from the door to the bed. |
| `ch38-image03` | Method section | **"Fresh Air Matters".** The frozen airing instruction rendered literally: window open, drawers pulled out, closet door back, linen out and breathing. |
| `ch38-image04` | Method section | **"Air the Linens".** Five ordered steps that carry the frozen air-not-spills reframe: a clean spare set still smells of the cupboard it sat in. |
| `ch38-image07` | Method section | **"Test Everything Before Guests Arrive".** The frozen clean-for-the-first-evening reframe, exactly: prove the lamp lights, charge a real phone from each cable, confirm the wifi. |
| `ch38-image05` | Zone 1 · The Guest Bed and Linens | Six-step mattress refresh, including the rotation almost nobody does on a guest bed. |
| `ch38-image08` | Zone 2 · The Guest Nightstand | "Empty Drawers Welcome Guests", which is the frozen draw-the-line rule from the guest's side. |
| `ch38-image13` | Zone 5 · The Guest Welcome and Work Surface | The welcome tray, with plain unbranded snacks. The only welcome-area plate in the batch. |

Verified in browser: seven images, none broken, no horizontal overflow, full alt text on every one,
figures and divs balanced, zero em dashes in the document.

## Kept as inline SVG (3)

- **The five zones** — `image02` is better but disqualified, see below.
- **The Shine method** — no photographic equivalent was generated.
- **The Part 9 before-and-after signature** — governed by the frozen caption.

## Coverage

| Zone | Figure |
|---|---|
| 1 · The guest bed and linens | `image05` ✔ |
| 2 · The guest nightstand | `image08` ✔ |
| 3 · The guest dresser | **none** |
| 4 · The guest closet | **none** (`image09` held, em dashes only) |
| 5 · The guest welcome and work surface | `image13` ✔ |

---

## HELD — near misses (5). Every one is a single-defect fix.

| Plate | What it does well | Held for |
|---|---|---|
| **`image02`** "Five Guest Bedroom Zones" | All five zones, correctly ordered. The nightstand panel lists working lamp, tissues, coaster, charging cables and wifi info, which is the frozen first-evening rule; the dresser panel says empty top, empty drawers, which is the frozen draw-the-line rule. It even prints "Top to bottom. Back to front." | **A fake QR code** ("Scan for the full 5-zone cleaning guide"). The only QR in the batch. |
| **`image06`** "Guest Nightstand Essentials" | The best Zone 2 plate: working lamp with "test the bulb and switch before your guest arrives", tissues, water and coaster, wifi info, charging cables, empty drawer. Carries the frozen first-evening rule more completely than anything wired. | **The word "Lightning"**, an Apple trademark, in "Include universal cables (USB-C, Lightning)". One word. |
| **`image09`** "Guest Closet Organization" | The only closet plate, and it carries the frozen clear-rod standard plus luggage space and a clear floor. | **Three baked em dashes** ("empty hanger space—at least 12 inches—on a clean rod", "Show them—without saying a word"). |
| **`image10`** "Make the Bed Like a Welcome" | A six-step bed check with a genuinely useful not-inviting / good / welcoming comparison strip. | **One baked em dash** ("Lay it flat and smooth—no bunching"). |
| **`image12`** "The Guest Room Pre-Flight Checklist" | A sound before-arrival check across six areas. | **One baked em dash** ("You'll relax—and so will they"). |

`image06` is the most valuable of these. Change one word and it goes straight into Zone 2 alongside
`image08`.

## HELD — rival systems and off-scope (8)

`image11` and `image14` through `image20` are generic reset content rather than zone instruction.

- **A rival zone taxonomy.** `image16`, `image17` and `image20` all print **"THE 6 AREAS"** (bed,
  surfaces, essentials, closet and storage, environment, final touch) against this chapter's frozen
  **five zones**. Six against five, and not one name matches.
- **Rival resets against the frozen fifteen minutes** (Ch 19): a five-minute reset (`image11`,
  `image15`), a two-to-five-minute reset (`image16`, `image17`), a twenty-to-twenty-five-minute plan
  (`image18`, `image20`).
- **Rival cadences against the frozen three clocks** (Ch 30): four in `image15` (weekly, monthly,
  quarterly, ongoing) and four in `image19` (weekly, monthly, seasonally, after each stay).
- **Coined named systems:** "The Sustainable System" (`image15`), "The Ready Standard" (`image14`),
  "The 6-Step Reset Plan" (`image18`), "The Final Touch Check" (`image19`).
- **Habit trackers**, on the Bible's AVOID list: `image15` prints a seven-day check-off grid headed
  "Track Your Consistency".
- **Motivational filler:** "You did it!" (`image20`), "You've got this" (`image16`).
- **Baked em dashes** in `image11`, `image14`, `image15`, `image16` and `image17`.

---

## Batch-wide counts

| Defect | Plates |
|---|---|
| Baked em dash | 8 |
| Invented numbered system | 8 |
| Rival reset duration | 6 |
| Contractions | 20 of 20 |
| "PRO TIP" where the book says "6S Tip" | 12 |
| **Fake QR code** | **1** |
| Rendered trademark | 1 (`image06`, the word "Lightning") |

**The improvement worth noting:** one QR code against sixteen in the previous chapter, and only one
trademark in a room that could easily have been full of them. Whatever changed between those two
generation runs is worth keeping.

**The defect that has now replaced it as the leading cause of loss is the baked em dash**, which took
five otherwise-usable plates here, four of them single-defect.

## Open for Phil

1. **Zones 3 and 4 have no figure.** Zone 4 is one regeneration away (`image09`, em dashes only).
2. **`image06` is a one-word fix** and is the best nightstand plate in the batch.
3. `image02` is a one-removal fix and is better than the zones SVG it would replace.
4. All three are now in the regeneration kit.
