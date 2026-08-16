# Infographic Spec: The 6S Loop, Walked Through One Cabinet

**Chapter 3, "The Six Steps That Transform Any Space"**
**6S Success: Home Edition**

One detailed infographic concept. It marries the chapter's hero motif (the 6S Loop) with its single throughline space (the cabinet under a kitchen sink), so the abstract cycle lands on a concrete place. The reader sees the whole method as one shape and watches it move one real cabinet from feral to calm.

---

## Design system (locked to the book)

Pull every color from the chapter HTML `:root` variables. Do not introduce new hues.

| Token | Hex | Use in this infographic |
| --- | --- | --- |
| Warm paper | `#F7F2E9` | Outer background |
| Panel | `#FBF7EF` | Inner cards and the loop field |
| Ink | `#2B2622` | Headlines, node labels, line art |
| Soft | `#6A625A` | Captions, handoff verbs, secondary text |
| Terracotta | `#BC4B2A` | Step numbers, node rings, the five working nodes, arrows |
| Honey | `#DDA63A` | Numerals inside the Safety node, accent ticks, tape corners |
| Slate | `#3C5A6B` | The Safety node fill, the door latch, data labels |
| Green calm-dot | `#6E8B5B` | After state, calm dots, the dry corner |
| Friction spark | `#CB4B36` | Before state, the four red sparks, the warning band |
| Rule | `#E2D8C4` / `#D9CDB8` | Hairlines, divider dashes, the faint guide ring |

Type: Fraunces for the title and node names (display, weight 600). Newsreader italic for the handoff verbs and captions. A clean sans (Inter) only for the small uppercase eyebrows, step numerals, and tick labels, matching the HTML.

Line style for any cabinet art: warm line-and-flat-color, roughly 3px stroke, rounded corners, exactly as the chapter SVGs are drawn. No gradients, no drop shadows beyond the single hairline the book uses.

---

## The concept in one sentence

A six-node ring sits in the center. Each node carries a tiny illustrated chip of the cabinet at that step, and each arrow between nodes is labeled with the one thing that step hands the next. The whole ring is bracketed by a small "before" cabinet (red sparks) entering at Sort and a small "after" cabinet (green calm dots) leaving at Sustain, so the loop visibly does work.

---

## Layout, portrait social (1080 x 1350)

Three stacked zones on warm paper. Generous margins, 64px outer padding.

### Zone 1, header band (top, about 220px tall)
- Eyebrow, Inter, uppercase, letterspaced, soft color: `CHAPTER 3 / DISCOVERING 6S`
- Title, Fraunces 600, ink, two lines: **The 6S Loop**, then a lighter subhead in Newsreader italic, soft color: *Walk it once. Then it goes around again.*
- A thin terracotta rule under the header.

### Zone 2, the loop (center, the dominant element, about 760px tall)
- A panel-colored rounded field holds the ring. Faint guide ring in rule color, same as the HTML hero.
- Six nodes, evenly spaced, clockwise from top. Each node is a circle, terracotta ring, white fill, with a small honey or terracotta numeral and the step name in Fraunces:
  1. **Sort** (top)
  2. **Straighten** (upper right)
  3. **Shine** (lower right)
  4. **Safety** (bottom, the one different node: filled slate, white label, honey numeral)
  5. **Standardize** (lower left)
  6. **Sustain** (upper left)
- Inside or just beneath each node, a 1-color micro-icon that ties the node to the cabinet:
  - Sort: three tiny piles (keep, relocate, release)
  - Straighten: a small caddy at the front
  - Shine: a cloth and a faint ring
  - Safety: a bottle moving up, a latch
  - Standardize: a small photo taped inside a door
  - Sustain: a 10s reset arrow
- Six clockwise arrows in terracotta, each riding the ring with a gap at the nodes, exactly like the hero SVG. Each arrow carries a Newsreader italic handoff verb in soft color:
  - Sort to Straighten: *makes room*
  - Straighten to Shine: *gives a home*
  - Shine to Safety: *reveals truth*
  - Safety to Standardize: *protects*
  - Standardize to Sustain: *sets default*
  - Sustain to Sort: *keeps alive*
- Center of the ring, Newsreader italic, soft color, two lines: *Walk it once.* / *Then it goes around again.* The Sustain to Sort arrow is drawn slightly heavier so the eye reads the loop closing back to the start.

### Zone 3, the cabinet proof (bottom, about 290px tall)
A small two-up card, panel background, that shows the loop did something real. Left chip: the under-sink cabinet **before**, leaning bottles, a tangle, a bottle low with a red spark, a faint stain at the back. Right chip: the same cabinet **after**, a caddy at the front, the bottle moved to a high shelf, a door label, a dry corner, four green calm dots.
- A short caption strip in Newsreader italic, soft color: *Same cabinet, one full lap. The sparks did not get cleaned away. They got handed, step to step, until there was nothing left to spark about.*
- Footer line, small sans, soft color: `6S Success: Home Edition / Chapter 3`

---

## Layout, landscape (1920 x 1080, also works at 1200 x 675)

Two columns. The ring no longer has to share vertical space with the cabinet proof, so it can breathe.

- **Left column (about 60% width):** the 6S Loop ring, identical node and arrow treatment to the portrait version, centered in a panel field. This is the hero.
- **Right column (about 40% width):** a vertical stack:
  - Title block at top (eyebrow, **The 6S Loop**, italic subhead).
  - The before cabinet chip with red sparks, labeled `BEFORE` in friction-spark color.
  - A short down arrow in terracotta.
  - The after cabinet chip with green calm dots, labeled `AFTER ONE LAP` in green.
  - "The loop in one line" panel (see text block below), slate-bordered box matching the HTML `.defbox`.
  - Footer attribution line.

For a slide or banner crop (1200 x 675), drop the cabinet chips and keep the ring plus the one-line definition box to the right.

---

## Exact text content (verbatim, no em dashes)

**Title:** The 6S Loop
**Subhead:** Walk it once. Then it goes around again.

**Node names and handoff verbs** (from chapter-quotes.md, "The six steps with handoff verbs"):
Sort (makes room) - Straighten (gives a home) - Shine (reveals truth) - Safety (protects) - Standardize (sets default) - Sustain (keeps alive). Then back to Sort.

**"The loop in one line" box** (verbatim definition box):
"Sort makes room. Straighten gives things a home. Shine reveals the truth. Safety protects the people. Standardize makes the good way the easy way. Sustain keeps it alive. Then it goes around again."

**Cabinet proof caption:**
Same cabinet, one full lap of the loop. The sparks did not get cleaned away. They got handed, step to step, until there was nothing left to spark about.

**Attribution footer:** 6S Success: Home Edition, Chapter 3

---

## Why this is the strongest single image

The chapter's whole argument is that the power is in the handoffs, not the six words. A plain list of S words cannot show a handoff. A ring with labeled arrows can, and pairing it with the before and after cabinet keeps it honest and concrete instead of motivational. The Safety node in slate, sitting in the middle rather than at the end, carries the chapter's key structural point on its own. This image also doubles as the recurring book motif, so a single node can be highlighted later at each Part opener.

---

## Production notes

- Keep the cabinet consistent with the chapter art: same leak at the back, same caddy, same bottle moved up. Do not redesign it.
- The four red sparks in the before chip should map to the four real snags named in the book: the hidden leak, the low poison, the tangle, the crusty sponge.
- The four green calm dots in the after chip map to the four fixes: clear home, poison up high, dry corner, door label.
- Safety is the only filled node. Resist the urge to color the others; the contrast is the point.
- Build the ring on a transparent layer so a single node can later be brightened and the rest dimmed for Part openers.
