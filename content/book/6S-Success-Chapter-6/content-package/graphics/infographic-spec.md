# Infographic Spec: The Eye vs the Camera

**Chapter 6, "Photograph Before You Fix"**
**Book:** 6S Success: Home Edition (Part Two, Prepare)

One infographic concept, built around the chapter's strongest single image: the Eye
vs the Camera split. The Matched Pair is paired in as a supporting strip at the
bottom so the piece both explains the idea and tells the reader what to do about it.

---

## Concept in one line

Show the same drop zone twice. On the left, the way your eye has softened it. On the
right, the way the camera hands it back, sharp and undeniable. Then show how to shoot
the matched pair that turns that honesty into proof.

The whole piece carries one promise from the chapter: *the eye forgives, the camera
does not.*

---

## Palette and type

Pull every color straight from the book's `:root` variables. Do not introduce new ones.

| Role | Hex | Used for |
|------|-----|----------|
| Paper (background) | `#F7F2E9` | Outer canvas |
| Panel (cards) | `#FBF7EF` | The two viewer cards, the bottom strip |
| Ink | `#2B2622` | Headlines, camera frame, sharp linework |
| Soft | `#6A625A` | Eyebrow labels, secondary captions |
| Terracotta | `#BC4B2A` | Eyebrow, the floor mark in the matched pair |
| Honey | `#DDA63A` | The drop-zone shelf fill, a thin accent rule |
| Slate | `#3C5A6B` | The closing line, the GOAL / cool objects |
| Green calm-dot | `#6E8B5B` | The wash over the eye side, the AFTER tag, calm dots |
| Friction spark | `#CB4B36` | The friction X-marks on the camera side, BEFORE tag |
| Rule / Rule2 | `#E2D8C4` / `#D9CDB8` | Hairlines, the dashed center divider |

**Fonts:** Fraunces for the display headline and the closing line. Newsreader italic
for the soft mood captions under each panel. Inter (or a clean grotesk) for the small
uppercase labels and the rules row. Keep tracking tight on Fraunces, wide (about
0.18em) on the Inter labels.

---

## Layout: portrait social, 1080 x 1350

Stacked into four bands. Generous margins, about 72 px left and right.

### Band 1, header (top, about 0 to 230 px)
- Eyebrow, Inter uppercase, terracotta: `CHAPTER 6 . PHOTOGRAPH BEFORE YOU FIX`
- Headline, Fraunces, ink, two lines:
  **The eye forgives.**
  **The camera does not.**
- One thin honey hairline under the headline, full content width.

### Band 2, the split (about 250 to 880 px), the heart of the piece
Two cards side by side on the panel color, separated by a vertical dashed rule
(`#D9CDB8`, dash 3 gap 7), exactly as the HTML hero draws it.

**Left card, "What your eye sees":**
- Small Inter label, soft gray, top of card: `WHAT YOUR EYE SEES`
- A simple line drawing of the entryway drop zone: a shelf, two legs, a couple of
  stacked items, a hook ring. Drawn in muted oatmeal line work (`#C9B79A`), fills in
  pale cream (`#F4ECD9`, `#EBDBBE`).
- A soft green wash over the whole card at about 7 percent opacity, so it reads
  faded and calm.
- Newsreader italic caption under the art, muted: *Forgiving. Faded. Familiar.*

**Right card, "What the camera sees":**
- Small Inter label, soft gray: `WHAT THE CAMERA SEES`
- The same drop zone, identical objects in identical positions, but now drawn inside a
  phone frame: rounded-rect outline in ink (`#2B2622`, 4 px), a small lens dot at top,
  an inner white screen rectangle.
- The line work is now crisp ink at full strength. No wash.
- Three friction spark marks (`#CB4B36`) sit on the worst points: an X-cross over the
  cluttered shelf corner, an X over the colonized hook, a small plus over a cord on
  the floor. These are the frictions the eye had smoothed away.
- No mood caption here. The sharpness is the message.

**Under both cards**, centered, Fraunces, slate:
*The eye forgives. The camera does not.*

### Band 3, the bridge line (about 900 to 1010 px)
A single Newsreader sentence, centered, ink on paper, no box:
*You stop seeing your own mess about three days in. The camera never does.*

### Band 4, the Matched Pair strip (about 1030 to 1280 px)
A panel-colored card running full content width, the practical payoff.

- Tiny Inter label, soft gray, centered: `THE MATCHED PAIR`
- Two small thumbnails side by side: a `BEFORE` thumb tagged in spark red, an `AFTER`
  thumb tagged in calm green. Same framing in both; the before shows clutter with one
  spark mark, the after shows the same shelf clear with three small green dots.
- Between and below them, a small phone icon sitting on a floor line, with a
  terracotta floor mark (an X) beneath it and two dashed sight lines fanning up to the
  two thumbnails. Newsreader italic under it: *you stand here, both times.*
- Bottom rule row, Inter, slate, wide tracking:
  `SAME SPOT . WHOLE AREA . GOOD LIGHT . DO NOT TIDY FIRST`

### Footer (about 1300 to 1350 px)
Small Inter line, soft gray, centered:
`6S Success: Home Edition . Chapter 6`

---

## Layout: landscape, 1920 x 1080 (and 1200 x 630 social card)

Same content, rebalanced into columns so it reads left to right.

- **Left third:** the header band stacked vertically. Eyebrow, the two-line Fraunces
  headline, the honey hairline, and below it the bridge sentence about the three days.
- **Center, dominant:** the Eye vs the Camera split, the two cards side by side at
  large size with the dashed divider, and the *The eye forgives. The camera does not.*
  line centered beneath them. This is the visual anchor and should hold the most space.
- **Right third or bottom band:** the Matched Pair strip turned vertical, the BEFORE
  and AFTER thumbnails stacked with the floor-mark phone between them and the four-rule
  row beneath.
- Footer credit bottom-left, small.

For the **1200 x 630** share card, drop the Matched Pair strip entirely. Keep only the
header line and the split, with the two cards filling most of the frame. The split
alone is strong enough to carry a link preview.

---

## Text content, locked copy (use verbatim)

- Eyebrow: `CHAPTER 6 . PHOTOGRAPH BEFORE YOU FIX`
- Headline: **The eye forgives. The camera does not.**
- Left label: `WHAT YOUR EYE SEES`
- Left mood line: *Forgiving. Faded. Familiar.*
- Right label: `WHAT THE CAMERA SEES`
- Split closing line: *The eye forgives. The camera does not.*
- Bridge: *You stop seeing your own mess about three days in. The camera never does.*
- Matched Pair label: `THE MATCHED PAIR`
- Floor-mark line: *you stand here, both times*
- Rules row: `SAME SPOT . WHOLE AREA . GOOD LIGHT . DO NOT TIDY FIRST`
- Footer: `6S Success: Home Edition . Chapter 6`

---

## Design notes

- The two drop-zone drawings must be the **same objects in the same positions**. The
  only differences are the green wash and soft line on the left versus crisp ink, the
  phone frame, and the spark marks on the right. That sameness is the whole argument.
- Keep the friction sparks to three. More than that turns honesty into noise.
- Resist gradients and drop shadows beyond the single faint card shadow the book uses
  (`0 1px 0 #D9CDB8`). The book's look is flat, warm, and hand-drawn, not glossy.
- The piece should feel like a spread from the book, not a stock template. Wide
  margins, real type hierarchy, one accent color doing the emotional work (spark red
  for friction, green for calm).
