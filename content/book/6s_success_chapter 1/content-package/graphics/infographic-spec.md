# Infographic Spec: "Two Tuesdays, One Difference"

*6S Success: Home Edition, Chapter 1, "Why Some Homes Feel Effortless"*

The single strongest summary image for this chapter. It carries the whole argument in one glance: two families, the same Tuesday morning, two outcomes. One home runs on a system and leaves calm at 7:55. The other reinvents the morning from scratch and is still searching at 8:09. The takeaway sits underneath: the difference is not character. It is design.

This builds directly on the book's existing "two-Tuesdays split" figure and its green calm-dot / red friction-spark motif.

---

## Why this concept

It is concrete, it is emotional, and it needs no jargon. A reader who has lived the frantic morning recognizes it before reading a word. The split composition does the teaching by itself, and the green dots versus red sparks give the eye an instant scorecard. It also seeds the rest of the chapter: friction, systems, and "everything has a home."

---

## Palette usage (from the book's :root variables)

- Background paper: `#F7F2E9` (outer canvas)
- Panel fill for the two scenes: `#FBF7EF`
- Ink for line art, outlines, and floor lines: `#2B2622`
- Calm side accent and calm-dots: green `#6E8B5B`
- Frantic side accent and friction-sparks: spark `#CB4B36`
- Terracotta `#BC4B2A` for the backpack and one warm object on the calm side
- Slate `#3C5A6B` for the key dish, the footer band, and the takeaway line
- Honey `#DDA63A` for keys, the center divider tick marks, and the small "VS" or time markers
- Wood tones for tables and baskets: `#E7C58B` and `#E0B877`
- Hairlines and dividers: `#D9CDB8` and `#E2D8C4`

Rule of thumb: green lives only on the left, red lives only on the right. Never mix a green dot onto the frantic side. The color split is the message.

## Type (from the book)

- Fraunces for the title, the two scene labels, and the big time stamps
- Newsreader for the scene captions and the takeaway sentence
- Inter (the book's sans) for the small uppercase eyebrow, timestamps tags, and the dot/spark count labels

---

## Layout: Portrait social, 1080 x 1350

A vertical stack so it reads top to bottom on a phone.

**Zone A, header (0 to ~230px)**
- Eyebrow, Inter, uppercase, letter-spaced, terracotta `#BC4B2A`: "6S SUCCESS · HOME EDITION · CHAPTER 1"
- Title, Fraunces 600, ink: "Two Tuesdays, One Difference"
- One-line deck, Newsreader italic, soft gray `#6A625A`: "Same morning. Same family love. Two very different systems."

**Zone B, the split scene (~230 to ~980px)**
- A single panel `#FBF7EF` with rounded corners, hairline border `#E2D8C4`, divided down the middle by a dashed vertical rule in `#D9CDB8` (3 7 dash pattern, matching the book figure).
- Because portrait is tall, stack the two homes vertically inside the panel rather than side by side:
  - **Top half, the calm home.**
    - Corner tag, Inter bold, green: "OUT THE DOOR · 7:55"
    - Simple line-art entryway: a door, a hook rail with a terracotta backpack hanging, a slate key dish on a small wood table, a shoe basket with paired shoes, a coffee mug.
    - Three green calm-dots `#6E8B5B` placed exactly where things have a home: on the hung bag, over the key dish, on the shoe basket.
    - Caption, Newsreader, ink: "Calm. Everything has a home."
  - A thin honey `#DDA63A` divider line with a small centered label, Inter uppercase: "SAME 7:42 START"
  - **Bottom half, the frantic home.**
    - Corner tag, Inter bold, spark red: "STILL LOOKING · 8:09"
    - Same room, but undone: keys on the counter far from the door, one shoe rotated away from its partner in the walkway, a fanned stack of mail on a chair, a big Fraunces "?" in spark red over the counter.
    - Three red friction-sparks `#CB4B36` (the four-line asterisk mark from the book) at each snag point: the counter, the papers, the lone shoe.
    - Caption, Newsreader, ink: "Frantic. Nothing has a home."

**Zone C, the scorecard strip (~980 to ~1130px)**
- Two small counters side by side on the paper background:
  - Left: three green dots and the line, Inter, green: "3 things with a home"
  - Right: three red sparks and the line, Inter, spark: "3 places life snags"
- This makes the abstract idea countable.

**Zone D, takeaway footer (~1130 to 1350px)**
- A solid slate `#3C5A6B` band, full width, rounded top corners.
- Takeaway, Fraunces 500, paper-colored text `#FBF7EF`: "The calm home is not cleaner this morning. It is better designed."
- Attribution, Inter small, honey `#DDA63A`: "6S Success: Home Edition, Chapter 1"

---

## Layout: Landscape, 1920 x 1080 (also works at 1200 x 630 for link previews)

Side by side, the way the book draws it.

- **Top bar (0 to ~150px):** eyebrow left, title center or left in Fraunces, deck line beneath.
- **Main split (~150 to ~840px):** one wide `#FBF7EF` panel split by a centered dashed vertical rule.
  - **Left column, calm home:** green "OUT THE DOOR · 7:55" tag top-left, the calm entryway line art, three green calm-dots, caption "Calm. Everything has a home." beneath.
  - **Right column, frantic home:** spark "STILL LOOKING · 8:09" tag top-right, the same room undone, the red "?", three red sparks, caption "Frantic. Nothing has a home." beneath.
  - Center seam: small honey tick marks and a tiny upright label "SAME MORNING" rotated or stacked, so the eye reads the two as one moment.
- **Footer band (~840 to 1080px):** slate band running full width. Left side holds the takeaway in Fraunces on paper text. Right side holds the small green-dots / red-sparks scorecard and the attribution line in honey.

For the 1200 x 630 crop, drop the scorecard, keep the split and the takeaway band.

---

## Text content, final and verbatim where it matters

- Title: **Two Tuesdays, One Difference**
- Deck: Same morning. Same family love. Two very different systems.
- Calm tag: OUT THE DOOR · 7:55
- Calm caption: Calm. Everything has a home.
- Frantic tag: STILL LOOKING · 8:09
- Frantic caption: Frantic. Nothing has a home.
- Scorecard left: 3 things with a home
- Scorecard right: 3 places life snags
- Takeaway (verbatim from the chapter): "The calm home is not cleaner this morning. It is better designed."
- Attribution: 6S Success: Home Edition, Chapter 1

---

## Production notes

- Keep the line art flat and hand-drawn, matching the chapter's SVG figures: 3px ink strokes, rounded line caps, no gradients except a soft warm wash if you want a sunrise feel behind the calm side.
- The green-only-left, red-only-right rule is non-negotiable. It is the whole point.
- Leave generous paper margins. The book breathes. Do not crowd the edges.
- One accent object in terracotta per side keeps both homes feeling warm and lived in, not clinical. These are loved homes, one just has a better system.
