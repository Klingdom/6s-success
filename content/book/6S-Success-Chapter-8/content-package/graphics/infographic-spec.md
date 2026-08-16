# Infographic Spec: The One Question

**Chapter 8, "Sort: Remove What Does Not Belong"**
**6S Success: Home Edition · Part Three · Sort**

This is the single strongest image in the chapter. It carries the whole idea in one glance:
one question, asked of everything, and the space sorts itself. The concept pairs the hero
**One Question gate** with a compact **First Pass** split underneath, so the viewer sees both
the tool and a worked example of it running on a real surface.

It stays consistent with the four inline SVG figures in `chapter_08_final.html`. Green
calm-dots mark what belongs here; slate out-arrows mark what belongs somewhere else and
follows the arrow out to a better home.

---

## Palette (from the chapter HTML :root)

| Token | Hex | Use here |
|---|---|---|
| paper | `#F7F2E9` | outer background |
| panel | `#FBF7EF` | card fills |
| ink | `#2B2622` | body text, rules |
| soft | `#6A625A` | captions, helper text |
| terra | `#BC4B2A` | eyebrow labels, the gate question emphasis |
| honey | `#DDA63A` | keys glyph, small accents |
| slate | `#3C5A6B` | gate border, "a better home" zone, out-arrows |
| green | `#6E8B5B` | "belongs here" zone, calm-dots |
| spark | `#CB4B36` | reserved; used only for the small friction-spark tags |

Fonts: **Fraunces** for the gate question and headlines, **Newsreader** italic for the
worked lines and footer, a clean sans (Inter style) for eyebrow labels and helper text.

Separator discipline: labels use the middot, for example `CHAPTER 8 · SORT`. Never a floating
hyphen or a floating dot between words.

---

## Portrait social, 1080 x 1350

Vertical stack, generous margins (64 px side padding), everything centered.

**1. Eyebrow band (top, y approx 60 to 130)**
- Small caps, letter-spaced, terracotta: `CHAPTER 8 · SORT`
- Below it, Fraunces headline in ink, two lines:
  "One question, / asked of everything."

**2. The gate (the hero, y approx 250 to 760)**
- A slate-bordered rounded gate card, panel fill, soft drop line beneath it.
- Top label, small sans caps, soft gray: `THE ONE QUESTION`
- The question in Fraunces, ink, two lines, the largest type on the page:
  "Does this help the / space do its job?"
- Helper line under it, small sans, soft gray: `yes stays · no leaves`
- A short cluster of small drop-zone glyphs (keys with a honey key-ring, an envelope, a
  charger, a folded bag) enters from the left on a slate flow arrow, labeled beneath in sans,
  soft gray: "everything in the space".
- Two labeled outcomes branch from the gate. Up: a green zone tab `BELONGS HERE` with three
  or four green calm-dots and a Newsreader italic line "it stays". Down: a slate zone tab
  `A BETTER HOME` with a slate out-arrow leaving toward the edge and a Newsreader italic line
  "it leaves this space".

**3. The First Pass split (y approx 800 to 1180)**
- Two columns divided by a dashed bone-colored line.
- Left, green header bar `BELONGS HERE`: four representative rows, each with a green calm-dot:
  keys · the dog's leash · a folded reusable bag · the umbrella.
- Right, slate header bar `BELONGS SOMEWHERE ELSE`: four representative rows, each with a slate
  out-arrow and a soft-gray address in parentheses: already-read magazines · phone charger
  (desk) · a stray screwdriver (toolbox) · a shed sweater (closet).
- Small footer under the split, Newsreader italic, slate: "Judged only by the job."

**4. Footer line (y approx 1250)**
- Newsreader italic, slate: "You are not judging the charger. You are just checking its address."
- Tiny attribution, soft gray sans: `6S Success: Home Edition · Chapter 8`

---

## Landscape, 1200 x 675 (also serves 1920 x 1080 at the same proportions)

Two-column layout. Left 55 percent is the gate, right 45 percent is the worked split.

**Left column**
- Eyebrow `THE ONE QUESTION` at top, terracotta small caps.
- The gate card with the Fraunces question as the focal block, the "everything in the space"
  glyph cluster feeding in on a slate arrow, and the two branch tabs (green `BELONGS HERE` up,
  slate `A BETTER HOME` down with an out-arrow).
- Helper line beneath: `yes stays · no leaves`.

**Right column**
- Headline in Fraunces, ink: "One question. Two answers. The noes flow out."
- The First Pass shown as a tight two-column split: green `BELONGS HERE` keepers with
  calm-dots, slate `BELONGS SOMEWHERE ELSE` movers with out-arrows and their real homes in
  parentheses.
- Footer italic in slate: "Sort by address, not by fate."
- Attribution bottom-right, soft gray: `6S Success: Home Edition · Chapter 8`.

---

## Layout notes

- The gate question is the loudest element on the page. Set it largest, in Fraunces, and give
  it room. Everything else supports it.
- Hold the two-color discipline: green means belongs here and stays, slate means belongs
  somewhere else and leaves. Do not let any other color compete with those two in the gate or
  the split. Spark red appears only as the small friction-sparks in supporting art, never on
  the outcome labels.
- "A better home" is an address change, not a discard. The out-arrow points to a labeled home
  (desk, closet, toolbox), never to a bin, a trash can, or a giveaway pile. Keep Chapter 11's
  disposal question out of the frame entirely.
- Do not introduce a keep-versus-toss or necessary-versus-unnecessary framing. This image
  sorts by belonging in this space only. The harder need question is Chapter 9.
- Hand-made feel: a faint paper grain on the background, slightly soft corners, the worked
  lines set as if jotted rather than typeset.

*(inference: exact pixel y-values above are a suggested rhythm, not specified in the chapter.
The text content, palette, and motifs are all drawn from the chapter HTML and canonical files.)*
