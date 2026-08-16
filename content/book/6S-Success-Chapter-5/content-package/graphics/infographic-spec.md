# Infographic Spec: The 6S Snapshot

**Chapter 5, "The 6S Home Audit"**
**6S Success: Home Edition, Part Two, Prepare**

One detailed infographic concept. The hero is the 6S Snapshot radar, paired with the Home 6S Audit scorecard so the reader sees both the shape and the six scores that made it. This is the single strongest image in the chapter and a reusable book diagnostic.

---

## The idea in one line

Six honest scores become one lopsided shape, and the dents show where an hour of work buys the most relief.

## Palette (from the final HTML :root variables)

- Paper background: `#F7F2E9`
- Panel / card fill: `#FBF7EF`
- Ink (primary text): `#2B2622`
- Soft (secondary text): `#6A625A`
- Terracotta (data polygon, S labels): `#BC4B2A`
- Honey (accent, art-note marks): `#DDA63A`
- Slate (Safety, data badges, structure): `#3C5A6B`
- Green calm-dot (strongest axis): `#6E8B5B`
- Friction spark (weakest axis): `#CB4B36`
- Grid rules: `#E2D8C4` and `#EDE3CE`

## Type

- Display and axis labels: Fraunces, weight 600
- Body, questions, captions: Newsreader
- Eyebrows, scores, small caps labels: Inter, 700, wide letter-spacing

---

## PORTRAIT social, 1080 x 1350

A single column, three stacked zones on warm paper. Generous margins of about 64px.

### Zone 1, header (top, roughly 0 to 230px)

- Eyebrow, Inter caps, terracotta, letter-spaced: `THE 6S SNAPSHOT`
- Title, Fraunces 600, ink, two lines: `Score your space. Read the shape.`
- One italic Newsreader line, soft grey: `The dents are where the work goes.`
- Thin slate rule under the header.

### Zone 2, the radar (center, roughly 230 to 940px)

The hero. A six-spoke radar on a panel card with a 1px `#E2D8C4` border and a 14px radius.

- Hexagon grid, three faint rings in `#EDE3CE`, outer ring in `#E2D8C4`. Center is 0, rim is 5.
- Six axes, arranged exactly as the book: Sort at top, then clockwise Straighten (upper right), Shine (lower right), Safety (bottom), Standardize (lower left), Sustain (upper left).
- Plot the worked drop-zone reading: Sort 4, Straighten 3, Shine 3, Safety 2, Standardize 1, Sustain 1. Connect into a polygon filled terracotta at about 14 percent opacity, 3px terracotta stroke, solid terracotta vertex dots.
- Strongest axis, Sort, gets a hollow green calm-dot ring (`#6E8B5B`, 3px stroke) on its vertex.
- Weakest axes, Standardize and Sustain, get a red friction-spark (`#CB4B36`) near their vertices, drawn as a small asterisk or four-point cross.
- Axis labels in Fraunces 600 ink, except Safety in slate.
- Small score numerals beside each vertex in Inter 700, soft grey, with the two 1s in friction red.
- Center micro-note, Newsreader italic, soft grey: `0 at center, 5 at the rim.`

### Zone 3, baseline and read (bottom, roughly 940 to 1286px)

- A slate-outlined white badge: `BASELINE` (Inter caps, soft grey) over `14 / 30` (Fraunces, ink).
- One short read line, Newsreader, ink: `Fine on Sort. Decent in the middle. Starving on Standardize and Sustain.`
- A legend strip, three small keys in a row:
  - Green ring = `strongest S`
  - Red spark = `weakest S, the biggest opportunity`
  - Slate = `Safety`
- Footer, Inter small caps, soft grey: `6S Success: Home Edition  ·  Chapter 5`

---

## LANDSCAPE, 1920 x 1080 (also works at 1200 x 675 for link cards)

Two columns on warm paper, the radar leading and the scorecard supporting, so a viewer sees the shape first and then the six scores behind it.

### Left column, about 55 percent width: the radar

Same radar as the portrait center zone, sized large. Header sits above it: eyebrow `THE 6S SNAPSHOT`, title `One shape, the whole story`, italic subline `The dents are where the work goes.` Baseline badge `14 / 30` tucked top-right of the radar card in a slate-outlined white pill.

### Right column, about 45 percent width: the Home 6S Audit scorecard

A clean six-row table on a panel card, mirroring the book scorecard exactly.

| S | Question | Score |
|---|---|---|
| Sort | How much of what is here do you actually use? | 4 |
| Straighten | Does everything have an obvious home you can find fast? | 3 |
| Shine | Is it clean, with no hidden dust, leaks, or wear? | 3 |
| Safety | Could anything here hurt someone, especially a child? | 2 |
| Standardize | Is the right way obvious to anyone, or only in your head? | 1 |
| Sustain | Is any habit keeping it up, or does it just drift? | 1 |

- S names in Fraunces 600 terracotta, Safety in slate on a tinted slate row (`#ECF1F4`).
- Questions in Newsreader 16, ink.
- Scores in a right-hand column, Fraunces 700, ink, with the two 1s in friction red and the Safety 2 in slate.
- Bottom badge, slate outline: `BASELINE  14 / 30`.

### Bottom rule, full width

One quiet line tying the two halves together, Newsreader italic, soft grey, centered:
`The lowest score is not an insult. It is pointing directly at the cheapest relief in the room.`
Footer right: `6S Success: Home Edition · Chapter 5`.

---

## Color usage notes

- Terracotta carries the data shape so the reader's eye lands on the polygon first.
- Slate is reserved for Safety and for structural badges, never decorative. This keeps the Safety read consistent across the whole book.
- Green appears once, on the strongest axis only. Red spark appears only on the weakest axes. Scarcity is the point: the calm-dot and the spark are load-bearing vocabulary, not background texture.
- Honey is for small accents only (an optional corner mark or the legend tick), used sparingly.

## Text content to set, verbatim

- Eyebrow: `THE 6S SNAPSHOT`
- Center note: `The dents are where the work goes.`
- Definition (optional caption strip): `Score your space zero to five on each S, add it up, and write the number down. The lowest score is your biggest opportunity. The total is the baseline you will beat.`
- Read line: `Fine on Sort. Decent in the middle. Starving on Standardize and Sustain.`
- Attribution: `6S Success: Home Edition, Chapter 5`

## Accessibility

- Do not rely on color alone. Keep the score numerals and the axis labels legible so a reader who cannot tell green from red still gets the weakest S from the number.
- Body text minimum 16px equivalent at portrait size. Ink on paper clears contrast comfortably.

## What to avoid

- No drop shadows heavier than the book's single 1px `#D9CDB8` lip. The book feel is flat line-and-color, not glossy.
- No gradients inside the radar. Keep fills flat.
- Do not add a seventh axis, a grade letter, or a pass/fail stamp. The audit is a flashlight, not a grade.
