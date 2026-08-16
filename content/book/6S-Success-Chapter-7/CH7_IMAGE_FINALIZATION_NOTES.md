# Chapter 7 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_07_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`

---

## What was done

Chapter 7 was **partially wired in the original July pass** (images 1, 2 and 3). This pass
completed it: **4 more images added, bringing the total to 7 of 10**, figures running **7-01 →
7-07 in ascending order**. Only the friction meter remains as live SVG.

### Placement map (document order)

| Image | Section | Action |
|---|---|---|
| `ch7-image1.png` | Chapter opener | already wired · **markup migrated** |
| `ch7-image2.png` | The Enemy Is the Everything Space | already wired · **markup migrated** |
| `ch7-image3.png` | Write the One Sentence | already wired · **markup migrated** |
| `ch7-image4.png` | same section | **NEW** |
| `ch7-image5.png` | Match It to Your Real Life | **NEW** |
| `ch7-image6.png` | Purpose Sets the Limits | **NEW** |
| `ch7-image7.png` | Write Yours | **NEW** |

### Markup migration

The three previously wired images used the older pattern: a padded `.figframe` wrapper with
`style="display:block;width:100%..."` inline on each `<img>`. Every other chapter in the book now
uses the flush `.plate` wrapper with the sizing in CSS.

All three were migrated, the inline styles removed, and the `.plate` / `figure.wide` /
`figure.tall` rules added to the stylesheet. Verified after the change: **zero `<img>` tags carry
inline styles**, and computed `.plate` padding is `0px`. Chapter 7 now matches Chapters 1 to 6 and
10 exactly.

The opener's `artnote` placeholder ("Final book: full-bleed photograph of a hand placing a small
written purpose card...") was removed, since the real photograph now satisfies it.

### Placement logic worth recording

The obvious topical home for `ch7-image4` ("The Decision Filter") was *Purpose Sets the Limits*,
but that section sits after *Match It to Your Real Life*, which is the natural home for
`ch7-image5`. Placing them that way would have run 5 before 4.

Instead 7-04 was placed at the close of **Write the One Sentence**, immediately after the Purpose
Statement template. This reads better than the alternative: the reader writes the sentence, and
the very next figure shows the sentence operating as a filter. Figures stay ascending and the
argument tightens.

---

## HELD BACK · 3 images

### `ch7-image10.png` — canon violation, despite being the best-looking plate in the set

"The One Sentence Wall" is genuinely lovely and its concept is exactly right: framed purpose
sentences per room, with the entry reading *"Launch our day"*, which echoes the chapter's own
worked example and the card in the opening photograph.

But its footer band is labelled **"THE 6S PATH"** and reads:

> MEASURE · PHOTOGRAPH · DEFINE PURPOSE · SORT · **SET IN ORDER** · SHINE · STANDARDIZE · SUSTAIN

Three problems in one strip:

1. **Safety is missing entirely** — the book's fourth S and its differentiator.
2. **"Set in Order"** instead of **Straighten**.
3. It presents **eight steps** as "the 6S path", folding the Part 2 preparation chapters
   (measure, photograph, define purpose) into the six S's as though they were S's.

It also contains an **em dash**: *"turns chaos into calm—and makes every day run smoother."*

Worth regenerating rather than abandoning. Everything above the footer band is excellent; the fix
is confined to that strip. Reference image for the correct six:
`6S-Success-Chapter-3/ch3-image2.png`.

### `ch7-image9.png` — concept drift

"The Family Purpose Workshop" is about a family's **life purpose and core values**, with an
example statement of *"We are here to love each other, grow together, and make a positive
difference in the world."* It prescribes a 60 to 90 minute workshop with markers and sticky notes.

Chapter 7's purpose statement is spatial and deliberately small: *this space is for ___, so that
___*, worked as *"getting everyone out the door fast and landing softly on the way back in."*
Conflating an area's job with a family mission statement would send readers into a values
exercise when the chapter asks for one sentence about a drop zone, and a 60 to 90 minute workshop
sits badly against a chapter that describes the task as "a five-minute job, most of which is
thinking."

### `ch7-image8.png` — out of scope

"The One Touch Rule" is workplace productivity advice, worked through email, phone calls, tasks
and inbox handling. It is not Chapter 7's subject, and arguably not this book's subject.

---

## Minor notes on the wired-in set

- **`ch7-image4` mildly pre-empts Chapter 11.** Its bottom row offers *relocate / store elsewhere
  / donate / recycle or discard* as outcomes. Disposal routing is fenced to Chapter 11, and
  Chapter 8's own scope note is explicit that "removing is not throwing away". The filter concept
  itself is core to Chapter 7 (the chapter's device is literally named the One Sentence Filter),
  so the plate was wired in, but if it is ever regenerated the bottom row would be better as
  *relocate / a better home* without the disposal specifics.
- **Contractions** throughout the set ("isn't", "doesn't", "don't", "It's"). The chapter text uses
  none. Same whole-set voice mismatch recorded for Chapter 6.
- **Visible brands** in photographs: a Fjällräven backpack and Nike shoes in `image5`, New Balance
  shoes in `image6`. Incidental product presence in a photograph of a real room, consistent with
  what was noted for Chapter 3, and treated the same way: a note, not a blocker.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_07_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old figures. Chapter
text was not changed, so the content package remains valid against it.
