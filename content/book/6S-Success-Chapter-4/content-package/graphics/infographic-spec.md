# Infographic Spec: The First Target Map

**Chapter 4, "How to Choose Your First Target Area"**
**6S Success: Home Edition**

One strong infographic, built around the chapter's hero device, the First Target Map, with the Target Scorecard as an optional paired panel for the longer formats. The whole point is to let a reader make the choice in under a minute: score a space on friction and effort, and the map tells you whether to start there or wait.

---

## Concept in one line

A two-by-two grid that turns two honest judgments (how often a space costs you, how big the job is) into one clear decision, with the high friction and low effort corner lit up as the place to start.

---

## Palette (from the book CSS variables)

| Role | Hex | Where it is used |
|---|---|---|
| Warm paper background | #F7F2E9 | Outer canvas |
| Panel | #FBF7EF | Grid field and cards |
| Ink (primary text) | #2B2622 | Titles, axis lines, body |
| Soft gray-brown | #6A625A | Axis labels, captions |
| Terracotta | #BC4B2A | The garage tag, accents, eyebrow |
| Honey | #DDA63A | Small underlines, "Soon" marker warmth |
| Slate | #3C5A6B | Data labels, footer, attribution |
| Green (calm dot) | #6E8B5B | "Start Here" quadrant fill and dots |
| Friction spark | #CB4B36 | Friction end of any scale, negative score |
| Rule lines | #E2D8C4 / #D9CDB8 | Light borders, dividers |

Quadrant fills (match the HTML exactly): "Start Here" #E8EFE0 with a #6E8B5B border; "Soon, Not First" #FAF0DA; "Fine, Not Now" #FFFFFF; "Avoid for Now" #F4EEE2. Light quadrants carry a 2px #E2D8C4 border so only the sweet spot reads as active.

## Type

- Display and quadrant names: Fraunces (600 to 700 weight).
- Body, axis value words (low, high), row labels: Newsreader.
- Eyebrow, axis names (EFFORT, FRICTION), small caps tags: Inter, 700, wide letter spacing (about 0.2em), used sparingly the way the HTML does.

---

## Layout, portrait social (1080 x 1350)

Vertical stack. The map is the star and takes the upper two thirds. The scorecard sits as a slim summary band below.

1. **Top band (about 130px tall).** Eyebrow in terracotta small caps: "CHAPTER 4 · CHOOSE YOUR FIRST TARGET." Title in Fraunces, two lines: "The First Target Map." Sub-line in Newsreader italic, soft gray: "Two judgments, one decision."

2. **The map (a roughly 900 x 760 square, centered).**
   - Vertical axis on the left labeled FRICTION, reading low at the bottom to high at the top, with a thin ink arrow pointing up. Axis caption in soft gray: "how often it costs you."
   - Horizontal axis along the bottom labeled EFFORT, reading low at the left to high at the right, thin ink arrow pointing right. Axis caption: "how big the job is."
   - Four quadrants:
     - **Top-left, Start Here** (high friction, low effort). Green-tinted fill, solid green border. Name in Fraunces, deep green. Support line: "Small to fix. Big daily relief." Scatter six green calm-dots across it. This is the only quadrant that should feel switched on.
     - **Top-right, Soon, Not First** (high friction, high effort). Warm honey-tinted fill. A small line-art garage glyph (peaked roof, single door) in ink, with a terracotta tag beneath it: "THE GARAGE." Support line: "Worth doing. Just not first."
     - **Bottom-left, Fine, Not Now** (low friction, low effort). Plain panel. Support line: "Easy, but it barely changes your day."
     - **Bottom-right, Avoid for Now** (low friction, high effort). Muted fill, gray text. Support line: "Lots of work, little daily payoff."

3. **Definition strip (a slate-bordered card, full width, about 150px).** Pull the canonical definition box: "The best first target is the smallest space that will still feel like a real win. High friction, low effort." Fraunces 500, ink, with a small slate label above it: "YOUR FIRST TARGET IN ONE LINE."

4. **Scorecard summary band (about 200px).** A compact three-row version of the Target Scorecard so the abstract map lands on real spaces:
   - Kitchen catch-all drawer · friction 4 · effort 1 · score +3 (green row)
   - Entryway drop zone · friction 5 · effort 2 · score +3 (green row)
   - Garage · friction 3 · effort 5 · score -2 (faint terracotta row, spark-colored score)
   One line under it in soft gray: "Friction minus effort. The humble drawer wins."

5. **Footer (about 70px).** Slate baseline: "6S Success: Home Edition · Chapter 4" on the left, and a soft CTA on the right: "Read the chapter free online."

Keep generous margins (about 64px) and let the paper breathe. The eye should land on the green corner first, then the garage, then the definition.

---

## Layout, landscape (1200 x 675, also works at 1920 x 1080)

Two columns.

- **Left column (about 58% width):** the full First Target Map, same four quadrants and axes as above. This is the hero.
- **Right column (about 42% width):** stacked vertically,
  1. the title block and "Two judgments, one decision" sub-line at the top,
  2. the definition card in the middle,
  3. the compact five-row Target Scorecard at the bottom (kitchen drawer +3, entryway drop zone +3, bathroom counter +2, linen closet -1, garage -2), winner rows tinted green, garage row tinted faint terracotta.
- **Footer strip** across the full width: attribution left, CTA right, thin #D9CDB8 rule above it.

For a clean 16:9 social or slide, this side-by-side reads well at a glance and keeps the map large.

---

## Optional square variant (1080 x 1080)

Map only, no scorecard band. Title across the top, the four-quadrant map filling the middle, the one-line definition as a slim footer card. This is the cleanest single-asset crop and the easiest to lift the "Start Here" corner from for a standalone calm-dot graphic.

---

## Text content (final copy, verbatim from the chapter)

- Title: The First Target Map
- Axes: FRICTION (low to high), EFFORT (low to high)
- Quadrant names: Start Here · Soon, Not First · Fine, Not Now · Avoid for Now
- Quadrant support lines: "Small to fix. Big daily relief." · "Worth doing. Just not first." · "Easy, but it barely changes your day." · "Lots of work, little daily payoff."
- Garage tag: THE GARAGE
- Definition: "The best first target is the smallest space that will still feel like a real win. High friction, low effort."
- Scorecard rows: Kitchen catch-all drawer 4 / 1 / +3 · Entryway drop zone 5 / 2 / +3 · Bathroom counter 3 / 1 / +2 · Linen closet 2 / 3 / -1 · Garage 3 / 5 / -2
- Attribution: 6S Success: Home Edition · Chapter 4

---

## Production notes

- Draw the map so the "Start Here" quadrant can be exported on its own as a standalone calm-dot graphic for social and companion use, the same way the signature asks.
- Positive scores in green (#4F6B3E for the deep green text), negative scores in spark (#CB4B36), neutral in soft gray. This keeps the math readable at thumbnail size.
- Keep the garage glyph affectionate and simple, not a punchline. The chapter respects the garage. It is sequencing, not shame.
- All numbers come straight from the HTML Target Scorecard. Do not adjust them.
