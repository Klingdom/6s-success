# Infographic Spec: The Red Tag and the Holding Area

**Chapter 10, "Red Tags, Holding Areas, and Sorter's Remorse"**
**6S Success: Home Edition · Part Three · Sort**

This is the single strongest image in the chapter. It carries the whole idea in one glance:
for a thing you honestly cannot call, you do not force a guess, you tag it, and time makes the
call. The concept pairs the hero **red tag** (three lines) with the **holding area on a
timeline** underneath, so the viewer sees both the tool and the deadline that does the work.

It stays consistent with the four inline SVG figures in `chapter_10_final.html`. Green
calm-dots mark the keep path, the thing you reached for in time; slate marks the out-box path,
the tag that passed untouched. The decide-by date is the pivot between them.

---

## Palette (from the chapter HTML :root)

| Token | Hex | Use here |
|---|---|---|
| paper | `#F7F2E9` | outer background |
| panel | `#FBF7EF` | card fills |
| ink | `#2B2622` | body text, rules |
| soft | `#6A625A` | captions, helper text |
| terra | `#BC4B2A` | the red tag, eyebrow labels, the decide-by marker |
| honey | `#DDA63A` | small accents only |
| slate | `#3C5A6B` | the out-box path, the out box, timeline, goal crosshair |
| green | `#6E8B5B` | the keep path, calm-dots |
| spark | `#CB4B36` | reserved; not used on outcome labels |

Fonts: **Fraunces** for the tag lines and headlines, **Newsreader** italic for the worked
lines and footer, a clean sans (Inter style) for eyebrow labels and helper text.

Separator discipline: labels use the middot, for example `CHAPTER 10 · SORT`. Never a
floating hyphen or a floating dot between words. Compound terms keep their internal hyphen:
decide-by, red-tag, out-box.

---

## Portrait social, 1080 x 1350

Vertical stack, generous margins (64 px side padding), everything centered.

**1. Eyebrow band (top, y approx 60 to 140)**
- Small caps, letter-spaced, terracotta: `CHAPTER 10 · SORT`
- Below it, Fraunces headline in ink, two lines:
  "For the thing you / cannot decide, tag it."

**2. The red tag (the hero, y approx 250 to 720)**
- A terracotta notched tag card, tied by string to a small umbrella-handle glyph on the left.
- Top label, small sans caps, soft gray: `THE RED TAG`
- Three stacked lines on the tag, cream sans, the third emphasized largest and brightest:
  "what it is", "date tagged", "decide-by". Thin divider rules between the lines.
- A Newsreader italic switch line beneath the tag, soft gray: "then time decides".
- Two labeled outcomes branch from the tag. Up: a green zone panel `REACHED FOR IT IN TIME`
  with a green calm-dot, Fraunces "it earned its keep", Newsreader italic "untag it, it was
  necessary after all". Down: a slate zone panel `DATE PASSED, UNTOUCHED` with a slate
  out-arrow, Fraunces "the maybe became a no", Newsreader italic "it joins the out box".

**3. The holding area on a timeline (y approx 780 to 1180)**
- A slate timeline from a wood-toned `HOLDING AREA` box on the left (two small red tags inside)
  running right to the pivot.
- The pivot: a terracotta dashed vertical marker with a solid terracotta chip, `DECIDE-BY
  DATE`, the loudest structural element in this band.
- Two exits at the marker: up in green, `REACHED FOR IT · back to keep`, with a calm-dot;
  down in slate to a plain `THE OUT BOX` carton, with a small teaser beneath, soft gray sans:
  "on to Chapter 11" (one line only, no disposal choices).
- Small footer under the timeline, Newsreader italic, slate: "The date is the trigger. It
  sends each thing one of two ways."

**4. Footer line (y approx 1250)**
- Newsreader italic, slate: "A maybe is not a failure of nerve. It is honest, and honesty
  gets a system, not a shove."
- Tiny attribution, soft gray sans: `6S Success: Home Edition · Chapter 10`

---

## Landscape, 1200 x 675 (also serves 1920 x 1080 at the same proportions)

Two-column layout. Left 52 percent is the red tag, right 48 percent is the holding-area
timeline.

**Left column**
- Eyebrow `THE RED TAG` at top, terracotta small caps.
- The terracotta tag card as the focal block, tied to the umbrella-handle glyph, its three
  lines stacked (what it is · date tagged · decide-by, the last emphasized).
- The two branch panels: green `REACHED FOR IT IN TIME · it earned its keep` up with a
  calm-dot, slate `DATE PASSED, UNTOUCHED · the maybe became a no` down with an out-arrow.
- Switch line between them: "then time decides".

**Right column**
- Headline in Fraunces, ink: "The date is the whole point."
- The holding-area timeline: the `HOLDING AREA` box on the left, the terracotta dashed
  `DECIDE-BY DATE` pivot in the center, and the two exits (green `back to keep` up, slate `THE
  OUT BOX` down with a single "on to Chapter 11" teaser).
- Footer italic in slate: "A holding area without a deadline is just a nicer junk pile."
- Attribution bottom-right, soft gray: `6S Success: Home Edition · Chapter 10`.

---

## Layout notes

- The red tag is the loudest element on the page. Set its three lines clearly, in the
  terracotta tag, and give the "decide-by" line the most weight; it is the line that does the
  work. Everything else supports it.
- Hold the two-color discipline: green means reached-for and kept, slate means the date passed
  and it joins the out box. Exactly two exits, no third. Do not let honey or spark compete
  with green and slate on the outcome labels; honey appears only as small accents, spark not
  at all here.
- The out box is a set-aside spot that waits, not a destination. The slate out-arrow points to
  a plain labeled `THE OUT BOX` carton, never to a bin, a trash can, a donation pile, or a
  truck. Keep Chapter 11's disposal question (donate, sell, store, recycle, throw) out of the
  frame entirely; the "on to Chapter 11" teaser is a single label, not a routing diagram.
- The holding area is a temporary, time-boxed limbo, not a storage-placement scheme. Do not
  show where keepers get stored (that is Chapter 13). Do not re-run the Use Test or the
  necessary vs. unnecessary split (that was Chapter 9).
- Anti-shame: the out-box path is not a wall of failure. Keep it calm and matter-of-fact.
  Not knowing is normal, and time decides kindly. Keep it calm and non-coercive, no guilt cues.
- Hand-made feel: a faint paper grain on the background, slightly soft corners, the worked
  lines set as if jotted rather than typeset.

*(inference: exact pixel y-values above are a suggested rhythm, not specified in the chapter.
The text content, palette, and motifs are all drawn from the chapter HTML and canonical files.)*
