# Infographic Spec: The Use Test

**Chapter 9, "Necessary vs. Unnecessary"**
**6S Success: Home Edition · Part Three · Sort**

This is the single strongest image in the chapter. It carries the whole idea in one glance:
one honest question, asked of everything that stayed, and the necessary sorts from the
unnecessary. The concept pairs the hero **Use Test gate** with a compact **Necessary vs.
Unnecessary** split underneath, so the viewer sees both the tool and a worked example of it
running on the drop-zone basket.

It stays consistent with the four inline SVG figures in `chapter_09_final.html`. Green
calm-dots mark the necessary things you actually use; slate marks the unnecessary things,
kept just in case, that follow the arrow into the out box.

---

## Palette (from the chapter HTML :root)

| Token | Hex | Use here |
|---|---|---|
| paper | `#F7F2E9` | outer background |
| panel | `#FBF7EF` | card fills |
| ink | `#2B2622` | body text, rules |
| soft | `#6A625A` | captions, helper text |
| terra | `#BC4B2A` | eyebrow labels, question emphasis |
| honey | `#DDA63A` | the side gate for hard cases, small accents |
| slate | `#3C5A6B` | gate border, unnecessary zone, out-arrows, the out box |
| green | `#6E8B5B` | necessary zone, calm-dots |
| spark | `#CB4B36` | reserved; small friction-spark tags only |

Fonts: **Fraunces** for the gate question and headlines, **Newsreader** italic for the
worked lines and footer, a clean sans (Inter style) for eyebrow labels and helper text.

Separator discipline: labels use the middot, for example `CHAPTER 9 · SORT`. Never a floating
hyphen or a floating dot between words.

---

## Portrait social, 1080 x 1350

Vertical stack, generous margins (64 px side padding), everything centered.

**1. Eyebrow band (top, y approx 60 to 130)**
- Small caps, letter-spaced, terracotta: `CHAPTER 9 · SORT`
- Below it, Fraunces headline in ink, two lines:
  "One question, / asked of what stayed."

**2. The gate (the hero, y approx 250 to 780)**
- A slate-bordered rounded gate card, panel fill, soft drop line beneath it.
- Top label, small sans caps, soft gray: `THE USE TEST`
- The question in Fraunces, ink, the largest type on the page:
  "When did you / last use it?"
- Helper line under it, small sans, soft gray: `recently · or cannot say`
- A single small object glyph (an umbrella) enters from the left on a slate flow arrow,
  labeled beneath in sans, soft gray: "one thing that stayed".
- Two labeled outcomes branch from the gate. Up: a green zone tab `USED IT RECENTLY` with a
  green calm-dot, Fraunces "necessary", and a Newsreader italic line "keep it". Down: a slate
  zone tab `CANNOT REMEMBER` with Fraunces "unnecessary", a slate out-arrow, and a Newsreader
  italic line "the out box".
- A honey dashed side gate drops from the question card to a small honey card,
  `FOR THE HARD CASES`, Newsreader italic: "If it vanished today, would you buy it again?"

**3. The Necessary vs. Unnecessary split (y approx 820 to 1190)**
- Two columns divided by a dashed bone-colored line, worked on the drop-zone basket.
- Left, green header bar `NECESSARY · KEEP`: four representative rows, each with a green
  calm-dot: the one umbrella you grab · a reusable bag or two · the keys · the leash.
- Right, slate header bar `UNNECESSARY · OUT BOX`: four representative rows, each with a slate
  out-arrow: two extra umbrellas · a wad of surplus tote bags · a spare key to a car you sold ·
  a dead charging cable.
- Small footer under the split, Newsreader italic, slate: "Everything here belonged at an
  entryway. Most of it you still do not use."

**4. Footer line (y approx 1250)**
- Newsreader italic, slate: "Useful is not the same as used."
- Tiny attribution, soft gray sans: `6S Success: Home Edition · Chapter 9`

---

## Landscape, 1200 x 675 (also serves 1920 x 1080 at the same proportions)

Two-column layout. Left 55 percent is the gate, right 45 percent is the worked split.

**Left column**
- Eyebrow `THE USE TEST` at top, terracotta small caps.
- The gate card with the Fraunces question as the focal block, the "one thing that stayed"
  glyph feeding in on a slate arrow, and the two branch tabs (green `USED IT RECENTLY · necessary`
  up, slate `CANNOT REMEMBER · unnecessary` down with an out-arrow to the out box).
- The honey dashed side gate beneath: "If it vanished today, would you buy it again?"
- Helper line: `recently · or cannot say`.

**Right column**
- Headline in Fraunces, ink: "Useful is not the same as used."
- The worked split as a tight two-column list: green `NECESSARY · KEEP` with calm-dots, slate
  `UNNECESSARY · OUT BOX` with out-arrows, drawn on the drop-zone basket.
- Footer italic in slate: "Sort by use, not by potential."
- Attribution bottom-right, soft gray: `6S Success: Home Edition · Chapter 9`.

---

## Layout notes

- The gate question is the loudest element on the page. Set it largest, in Fraunces, and give
  it room. Everything else supports it.
- Hold the two-color discipline: green means necessary and stays, slate means unnecessary and
  goes to the out box. Do not let any other color compete with those two in the gate or the
  split. Honey appears only on the side gate for the hard cases. Spark red appears only as the
  small friction-sparks in supporting art, never on the outcome labels.
- The out box is a set-aside spot, not a destination. The slate out-arrow points to a plain
  labeled `THE OUT BOX` carton, never to a bin, a trash can, a donation pile, or a truck. Keep
  Chapter 11's disposal question (donate, sell, store, recycle, throw) out of the frame
  entirely, and do not draw the Chapter 10 red-tag or holding-area system.
- Do not reframe this as "does it belong here"; that was Chapter 8. Every object in the split
  already belongs at an entryway. This image sorts by use only.
- Anti-shame: the unnecessary column is not a wall of failure. Keep it calm and matter-of-fact.
  Letting go of the unused is not a verdict on the object and not a confession of a mistake.
- Hand-made feel: a faint paper grain on the background, slightly soft corners, the worked
  lines set as if jotted rather than typeset.

*(inference: exact pixel y-values above are a suggested rhythm, not specified in the chapter.
The text content, palette, and motifs are all drawn from the chapter HTML and canonical files.)*
