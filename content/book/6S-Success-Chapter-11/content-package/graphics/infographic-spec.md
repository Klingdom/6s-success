# Infographic Spec: The Five Doors Out

**Chapter 11, "What to Donate, Sell, Store, Recycle, or Throw Away"**
**6S Success: Home Edition · Part Three · Sort**

This is the single strongest image in the chapter. It carries the whole idea in one glance:
the out box is settled, and every thing in it leaves through one of five doors, with a firm,
deliberate lean toward the two fast lanes. The concept pairs the hero **five doors** (named
and sized) with the **routing cascade** beneath, so the viewer sees both the set of exits and
the quick question that picks each one, and sees at once that Donate is the wide default.

It stays consistent with the four inline SVG figures in `chapter_11_final.html`. Green
calm-dots mark the two fast lanes, Donate and Recycle; slate marks the two slow doors, Sell
and Store; a small spark accent marks the last, smallest door, Throw. The Donate lane is the
widest element on the page.

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
| slate | `#3C5A6B` | the two slow doors, Sell and Store, and the goal crosshair |
| green | `#6E8B5B` | the two fast lanes, Donate and Recycle, calm-dots |
| spark | `#CB4B36` | reserved for the smallest door, Throw, only |

Fonts: **Fraunces** for the door names and headlines, **Newsreader** italic for the worked
lines and footer, a clean sans (Inter style) for eyebrow labels and helper text.

Separator discipline: labels use the middot, for example `CHAPTER 11 · SORT`. Never a floating
hyphen or a floating dot between words. Compound terms keep their internal hyphen: out-box,
sell-by, later-use, e-waste.

---

## Portrait social, 1080 x 1350

Vertical stack, generous margins (64 px side padding), everything centered.

**1. Eyebrow band (top, y approx 60 to 140)**
- Small caps, letter-spaced, terracotta: `CHAPTER 11 · SORT`
- Below it, Fraunces headline in ink, two lines:
  "Five doors out, and / most of the box takes two."

**2. The five doors (the hero, y approx 250 to 720)**
- Five door panels in a row, sized by how much of the box each takes, left to right by lane
  speed rather than by the cascade order:
  - `DONATE`, the widest, green header and green-bordered panel, a green calm-dot, Fraunces
    "Donate", Newsreader italic "most of the box".
  - `RECYCLE`, medium, green, a calm-dot, italic "worn, paper, e-waste".
  - `SELL`, narrow, slate, italic "slow".
  - `STORE`, narrow, slate, italic "slow".
  - `THROW`, smallest, spark-bordered, italic "finished".
- A soft stream from a small `THE OUT BOX` carton on the left widens into Donate and Recycle
  and thins to dashed threads at Sell, Store, and Throw, so the fast-lane bias reads instantly.
- A Newsreader italic line beneath the doors, soft gray: "Donate and Recycle are the fast
  lanes; Sell and Store are the slow doors."

**3. The routing cascade (y approx 780 to 1180)**
- A short vertical spine from "an item from the box" down through three questions, each
  branching right to a narrow side door:
  - "Broken or unusable?" to a spark panel `Recycle, else Throw`.
  - "Valuable and worth selling?" to a slate panel `Sell · with a sell-by deadline`.
  - "Truly needed later?" to a slate panel `Store · labeled, dated, elsewhere`.
- The default: the spine turns green, labeled "everything else", and opens into one wide green
  bar with a calm-dot, `THE DEFAULT DOOR`, Fraunces `Donate`, italic tail "still useful to
  someone, today". This bar is the widest element in the band.
- Small footer under the cascade, Newsreader italic, slate: "Stop at the first door that fits.
  Everything still usable falls through to Donate."

**4. Footer line (y approx 1250)**
- Newsreader italic, slate: "The best destination is the one that actually empties the box."
- Tiny attribution, soft gray sans: `6S Success: Home Edition · Chapter 11`

---

## Landscape, 1200 x 675 (also serves 1920 x 1080 at the same proportions)

Two-column layout. Left 52 percent is the five doors, right 48 percent is the routing cascade.

**Left column**
- Eyebrow `THE FIVE DOORS` at top, terracotta small caps.
- The five door panels as the focal block, sized by lane speed: the wide green `DONATE` and
  medium green `RECYCLE` on top as the fast lanes, the narrow slate `SELL` and `STORE` and the
  small spark `THROW` beneath, each labeled.
- A soft stream from a small `THE OUT BOX` carton widening into Donate and Recycle, thin dashed
  threads to the three narrow doors.
- Caption line: "most of the box goes through two of them".

**Right column**
- Headline in Fraunces, ink: "One quick question picks the door."
- The routing cascade: three questions down a spine, each branching to a narrow side door
  (`Recycle, else Throw`; `Sell` with a sell-by deadline; `Store`, labeled and dated), then
  the wide green `Donate` default lane at the bottom for everything still usable.
- Footer italic in slate: "Donate is the default. You only step off it when an item earns
  another door."
- Attribution bottom-right, soft gray: `6S Success: Home Edition · Chapter 11`.

---

## Layout notes

- The Donate lane is the loudest element on the page. Draw it widest, set its name in the
  largest Fraunces, and let the other four doors clearly defer to it. Everything else supports
  the reading that Donate is the default.
- Hold the color discipline: green means a fast lane (Donate, Recycle), slate means a slow door
  (Sell, Store), and the single spark accent belongs only to Throw, the smallest door. Do not
  let honey or spark compete with green and slate on the door labels; honey appears only as
  small accents.
- The five doors are exactly five: Donate, Sell, Store, Recycle, Throw. No sixth option. The
  cascade stops at the first door that fits, and the narrow side doors catch only the rare item
  that earns them.
- The out box is already decided; this image only routes it. Do not re-open whether an item is
  necessary (that was Chapter 9) and do not re-run red tags or the holding area (Chapter 10).
  Do not draw any keeper being given a home or arranged; the keepers are Part 4's business, not
  this frame's.
- Anti-shame: the slow doors are legitimate, not traps to feel bad about, and Throw is the
  honest exit for the truly finished, not a scolding. Nobody has to sell anything. Keep it calm
  and non-coercive, no guilt cues, no force or pressure framing anywhere.
- Hand-made feel: a faint paper grain on the background, slightly soft corners, the worked
  lines set as if jotted rather than typeset.

*(inference: exact pixel y-values above are a suggested rhythm, not specified in the chapter.
The text content, palette, and motifs are all drawn from the chapter HTML and canonical files.)*
