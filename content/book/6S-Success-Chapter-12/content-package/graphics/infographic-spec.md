# Infographic Spec: The Home Test

**Chapter 12, "Straighten: A Place for Everything"**
**6S Success: Home Edition · Part Four · Straighten**

This is the single strongest image in the chapter. It carries the whole idea in one glance:
every keeper gets one clear home, and a home is only as good as the return trip. The concept
pairs the hero **Home Test** (the good-home versus bad-home contrast) with the **keepers mapped
to homes** beneath, so the viewer sees both the test that judges a home and the five keepers
each matched to one, and sees at once that the standard is a single easy motion.

It stays consistent with the four inline SVG figures in `chapter_12_final.html`. Green calm-dots
mark a good home and an easy return; slate carries the test line and the definition; a single
small friction-spark marks the one bad home that fails. The good home is the effortless default
the reader is meant to build.

---

## Palette (from the chapter HTML :root)

| Token | Hex | Use here |
|---|---|---|
| paper | `#F7F2E9` | outer background |
| panel | `#FBF7EF` | card fills |
| ink | `#2B2622` | body text, rules |
| soft | `#6A625A` | captions, helper text |
| terra | `#BC4B2A` | eyebrow labels, headline accents |
| honey | `#DDA63A` | small accents only |
| slate | `#3C5A6B` | the test line, the definition, the goal |
| green | `#6E8B5B` | a good home, calm-dots, the easy return |
| spark | `#CB4B36` | reserved for the one bad home that fails, only |

Fonts: **Fraunces** for the home names and headlines, **Newsreader** italic for the test line
and footer, a clean sans (Inter style) for eyebrow labels and helper text.

Separator discipline: labels use the middot, for example `CHAPTER 12 · STRAIGHTEN`. Never a
floating hyphen or a floating dot between words. Compound terms keep their internal hyphen:
one-motion, Sort-complete, anti-shame.

---

## Portrait social, 1080 x 1350

Vertical stack, generous margins (64 px side padding), everything centered.

**1. Eyebrow band (top, y approx 60 to 140)**
- Small caps, letter-spaced, terracotta: `CHAPTER 12 · STRAIGHTEN`
- Below it, Fraunces headline in ink, two lines:
  "A home is only as good / as the return trip."

**2. The Home Test contrast (the hero, y approx 250 to 760)**
- Two panels side by side, the same set of keys facing two homes:
  - Left, `A GOOD HOME`, green header and green-bordered panel, a green calm-dot, Fraunces
    "one easy motion", Newsreader italic "the keys drop into the tray as your hand passes over
    it". A smooth green arc from the hand to an open tray, a green sans caps tag `IT GOES BACK`.
  - Right, `A BAD HOME`, spark-bordered panel, a single small friction-spark, Fraunces "far,
    behind a door, under a lid", Newsreader italic "three steps and a decision". A long broken
    path to a lidded box, a spark sans caps tag `IT DOES NOT GO BACK`.
- Between the panels, a slate divider rule so the two read as a fair comparison of one item.
- A slate Newsreader italic line beneath the panels: "The only question a home has to pass: is
  putting it back easier than setting it down where you stand?"

**3. The keepers mapped to homes (y approx 820 to 1200)**
- A short two-column list, five keepers on the left each joined by one green one-motion arrow to
  its one assigned home on the right, each home led by a green calm-dot:
  - "the keys" to `a tray or hook at the door`.
  - "the leash" to `a hook by the door`.
  - "the umbrella" to `a stand at the door`.
  - "the reusable bag" to `a hook beside the leash`.
  - "tomorrow's mail" to `an outgoing slot at the door`.
- A green sans caps tab under the list, `EVERY HOME PASSES THE TEST`, with a small Newsreader
  italic tail "so the surface stays clear on its own".
- Small footer under the list, Newsreader italic, slate: "Each home is one easy motion from
  where the thing is used, so putting it back is the path of least resistance."

**4. Footer line (y approx 1270)**
- Newsreader italic, slate: "A place for everything, so everything can find its way back."
- Tiny attribution, soft gray sans: `6S Success: Home Edition · Chapter 12`

---

## Landscape, 1200 x 675 (also serves 1920 x 1080 at the same proportions)

Two-column layout. Left 52 percent is the Home Test contrast, right 48 percent is the keepers
mapped to homes.

**Left column**
- Eyebrow `THE HOME TEST` at top, terracotta small caps.
- The good-home versus bad-home contrast as the focal block: the green `A GOOD HOME` panel with
  the one-motion return on top or left as the winner, the spark-accented `A BAD HOME` panel with
  the long broken path beside it as the one that fails, the same keys in both.
- Caption line: "a home works when putting the thing back is easier than putting it down
  anywhere else".

**Right column**
- Headline in Fraunces, ink: "Give each keeper one home."
- The five keepers each joined by a single green arrow to one assigned home (`a tray or hook at
  the door`; `a hook by the door`; `a stand at the door`; `a hook beside the leash`; `an
  outgoing slot at the door`), a green `EVERY HOME PASSES THE TEST` tab beneath.
- Footer italic in slate: "One easy motion each, so the console stays clear without a nightly
  tidy."
- Attribution bottom-right, soft gray: `6S Success: Home Edition · Chapter 12`.

---

## Layout notes

- The good home is the loudest element on the page. Draw it as the effortless winner, set its
  one-motion return in the clearest green, and let the bad home read plainly as the one that
  fails, so the eye reads the test instantly: the near, open, one-motion home wins.
- Hold the color discipline: green means a good home and an easy return, slate carries the test
  line and the definition, and the single spark accent belongs only to the one bad home that
  fails. Do not let honey or spark compete with green and slate on the home labels; honey appears
  only as small accents.
- The keepers are exactly five: keys, leash, umbrella, reusable bag, tomorrow's mail. Each links
  to exactly one home, a clean one-to-one match, never two homes for a keeper or a shared spot.
- This image gives each keeper A home and judges it only by an easy return. Do NOT place homes by
  how often a thing is used or mark any spot as prime (that is Chapter 13). Do NOT add labels,
  outlines, or color-coding to the homes as visual cues (Chapter 14). Do NOT map or plan a whole
  room's homes at once (Chapter 15). Do NOT re-open Sort or re-decide what stays; the keepers are
  settled.
- Anti-shame: the bad home is a spot placed wrong, not a verdict on the person. The reader was
  never messy; the things simply had nowhere to go. Keep it calm and non-coercive, no guilt cues,
  no force or pressure framing anywhere.
- Hand-made feel: a faint paper grain on the background, slightly soft corners, the test line set
  as if jotted rather than typeset.

*(inference: exact pixel y-values above are a suggested rhythm, not specified in the chapter. The
text content, palette, and motifs are all drawn from the chapter HTML and canonical files.)*
