# Infographic Spec: "What Is 6S, in One Picture"

Chapter 2, "What Is 6S?" from *6S Success: Home Edition*. This is the single-image
summary of the chapter. If a reader sees only one graphic, this is the one. It joins
the six words, the bottle-opener drawer, and the one-sentence definition into a piece
someone could screenshot, print, or stick on the fridge.

## Design system (locked, from the book)

- **Paper / background:** `#F7F2E9`
- **Panel / card fill:** `#FBF7EF`
- **Ink (primary text):** `#2B2622`
- **Soft text (captions, secondary):** `#6A625A`
- **Terracotta (accent, step names):** `#BC4B2A`
- **Honey (arrows, highlights, family/warmth):** `#DDA63A`
- **Slate (data, Safety, the "into the home" node):** `#3C5A6B`
- **Green calm-dot (a thing with a clear home):** `#6E8B5B`
- **Friction spark (use sparingly, tension only):** `#CB4B36`
- **Rules / hairlines:** `#E2D8C4` and `#D9CDB8`
- **Display type:** Fraunces (titles, step names, the big "6S")
- **Body / caption type:** Newsreader (definition, meanings)
- **Label / eyebrow type:** Inter or a clean sans, uppercase, wide letter-spacing

Keep the warm, editorial, hand-made feel of the chapter HTML. Flat fills, ink outlines,
rounded corners on cards. No gradients, no drop shadows beyond a single hairline.

## The one idea this image carries

6S is one method for making the right thing easy to find, easy to use, and safe, in
any space, and keeping it that way. Six plain words carry the whole thing. The drawer
is what it feels like when it works.

---

## PORTRAIT SOCIAL (1080 x 1350)

A vertical card built in five horizontal bands. Background `#F7F2E9` throughout, with a
12px inner margin of paper around a soft `#FBF7EF` panel that holds the content.

### Band 1, Header (top, about 180px tall)
- Eyebrow, uppercase Inter, letter-spacing wide, `#BC4B2A`:
  **PART ONE · DISCOVERING 6S**
- Title, Fraunces, large, `#2B2622`:
  **What Is 6S?**
- One-line kicker, Newsreader italic, `#6A625A`:
  *Six plain words for a calmer home.*

### Band 2, The drawer motif (about 360px tall)
- Reuse the chapter's top-down drawer illustration (the bottle-opener tray plus sorted
  utensil lanes), rendered in flat fills with ink outlines.
- Tray fill `#fff`, bottle opener in slate `#3C5A6B`, corkscrew in terracotta
  `#BC4B2A`, can opener in honey `#DDA63A`. Utensils outlined in ink.
- Four green calm-dots `#6E8B5B` along the top edge of the lanes, each marking an item
  that has a clear home.
- Caption strip beneath, Newsreader, `#6A625A`:
  *Some drawers answer your question. Others just ask more.*

### Band 3, The six words (about 430px tall, the heart of the card)
- Section label, Inter uppercase, `#6A625A`: **THE SIX S'S, IN ORDER**
- Six rounded tiles in two columns, three rows. Tile fill `#FBF7EF`, ink hairline
  border. Step name in Fraunces terracotta `#BC4B2A`, one-line home meaning in
  Newsreader ink below it.
  1. **Sort**: Keep what belongs. Remove what does not.
  2. **Straighten**: A home for everything, by how often you use it.
  3. **Shine**: Clean, and notice problems while you do.
  4. **Safety**: Protect the people who use the space. *(tile uses slate `#3C5A6B`
     name and a small slate dot, so the sixth pillar reads as the one that protects.)*
  5. **Standardize**: Make the good way the normal, visible way.
  6. **Sustain**: Keep it up. Build the habit.
- Footline under the tiles, Newsreader italic `#6A625A`:
  *Three make space, one keeps people safe, two make it last.*

### Band 4, The definition (about 250px tall)
- A bordered definition box, fill `#FBF7EF`, 2px slate `#3C5A6B` border, rounded.
- Small label, Inter uppercase, slate: **6S IN ONE SENTENCE**
- The canonical line, Fraunces medium, ink `#2B2622`:
  **A simple, repeatable method for making the right thing easy to find, easy to use,
  and safe, in any space, and keeping it that way.**

### Band 5, Footer (about 90px tall)
- Thin honey rule `#DDA63A` across the top of the band.
- Left, Inter `#6A625A`: **6S Success: Home Edition · Chapter 2**
- Right, small green calm-dot `#6E8B5B` plus the word **findability** in Newsreader
  italic, as the quiet signature of the whole piece.

---

## LANDSCAPE (1200 x 675, also works at 1920 x 1080)

Same content, two-column layout. Background `#F7F2E9`, content on a `#FBF7EF` panel.

### Left column (about 45% width)
- Header block at top: eyebrow **PART ONE · DISCOVERING 6S** in terracotta, then
  **What Is 6S?** in Fraunces, then the kicker *Six plain words for a calmer home.*
- The drawer illustration fills the rest of the column, top-down, with the four green
  calm-dots. Caption beneath: *Some drawers answer your question. Others just ask more.*

### Right column (about 55% width)
- Section label **THE SIX S'S, IN ORDER**.
- The six tiles stacked as a single vertical list (full width of the column), each with
  the Fraunces step name and the Newsreader meaning on one line. Safety in slate.
- Footline: *Three make space, one keeps people safe, two make it last.*
- The slate-bordered definition box sits at the bottom of the right column with the
  one-sentence definition.

### Footer (full width, thin band)
- Honey rule, then **6S Success: Home Edition · Chapter 2** left, green dot plus
  **findability** right.

---

## Color usage summary (so the palette stays disciplined)

- Terracotta is for the step names and the eyebrow. It is the chapter's accent voice.
- Slate carries Safety and the definition border. It is the "serious / protective" note.
- Honey is for arrows, rules, and small warm marks. It never carries body text.
- Green dots appear only where an item has a clear home. They are the reward signal, so
  do not scatter them decoratively.
- Friction spark `#CB4B36` is optional and tiny here. If used at all, only as a single
  contrast dot in the drawer (one item slightly out of place) to imply the before. Most
  versions should leave it out and stay calm.

## Production notes

- Safe margins: keep all text at least 60px from the edge on portrait, 48px on
  landscape, so nothing clips under platform UI.
- The six tiles must stay legible as a thumbnail. Step names should survive being shrunk
  to a feed preview, so set them in a heavier Fraunces weight (500 to 600).
- Export portrait at 1080 x 1350 for Instagram and Facebook feed, and a 1080 x 1080
  square crop (drop Band 2's caption and tighten Band 4) for grid use.
- Alt text: "An infographic titled What Is 6S. A top-down kitchen drawer with sorted
  utensils and green dots, the six steps Sort, Straighten, Shine, Safety, Standardize,
  Sustain, and the one-sentence definition of 6S."
