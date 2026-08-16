# Chapter 6 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_06_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`

---

## What was done

**All 10 supplied images wired in, none held.** Figures run **6-01 → 6-10 in ascending order**.
Only the friction meter remains as live SVG. This is the cleanest image set the project has
produced, and the first chapter where nothing had to be held back.

### Placement map (document order)

| Image | Section | Action |
|---|---|---|
| `ch6-image1.png` | Chapter opener | replaced the phone/drop-zone SVG |
| `ch6-image2.png` | Why Your Eye Lies to You | replaced the **hero Eye vs Camera** SVG |
| `ch6-image3.png` | same section | NEW insertion |
| `ch6-image4.png` | How to Take a Useful Before Photo | NEW insertion |
| `ch6-image5.png` | same section | replaced the **Matched Pair** SVG |
| `ch6-image6.png` | Do Not Tidy First | NEW insertion |
| `ch6-image7.png` | Keep It, and Keep It Yours | NEW insertion |
| `ch6-image8.png` | Take the Picture | NEW insertion, before the checklist |
| `ch6-image9.png` | same section | NEW insertion, after the checklist |
| `ch6-image10.png` | The Starting Line, in Ink | NEW insertion, before the friction meter |

### Why this set worked where Chapter 5's did not

These are the **Jul 4 generation**, the same batch as Chapter 5's *old* set: serif display type,
cream ground, deep green and muted gold. It sits much closer to the book's actual design system
(Fraunces / Newsreader, paper / terracotta / honey / slate) than the Jul 19 to 20 infographic
style used in Chapters 1 to 5's newer plates.

More importantly, this chapter is about **photography**, not about the method. There are no six-S
lists to get wrong, no scoring scale to contradict, and no worked-example numbers to mismatch.
Every failure mode that cost Chapter 5 nineteen images is simply absent here. Two plates match
chapter motifs by name: **6-02 "The Eye vs. The Camera"** is the hero motif exactly, and **6-05
"One Spot. Two Moments."** is the Matched Pair technique.

Checks run and passed: no six-S canon issues (no such lists present), no QR codes, no attributed
quotations, no misattributions, no worked-example data to conflict.

### One section deliberately left unillustrated

**"The Before Is for the After"** carries no figure. The art's numbering assumes a different
section order than the chapter has: the ideal plate for that section is **6-10 "Evidence of
Change"** (a before/after slider captioned *the picture is not the achievement, it proves the
achievement*), but placing it there would have put figure 10 ahead of figures 4 through 9.

Ascending figure order won. 6-10 now closes the chapter, where it also reads well. Similarly
6-07 ("Building Your Proof") would sit most naturally in that same proof section and was placed
one section later instead, in *Keep It, and Keep It Yours*, where it justifies why the record is
worth keeping.

If a new plate is ever commissioned for this chapter, *The Before Is for the After* is the gap.

---

## Fix at next regeneration (all cosmetic, none blocking)

Nothing here is a factual error or a canon violation, which is why all ten were wired in rather
than held. But the following should be corrected whenever these plates are next touched.

### 1. Figure number typo · `ch6-image2.png`

Reads **"FIGURE 6-022"**. Should be **6-02**. Three digits where there should be two, on the
chapter's hero figure.

### 2. Two em dashes · `ch6-image6.png`

- *"This shows the full story—the clutter, the friction, the work."*
- *"This builds belief—and momentum."*

Violates the project's no-em-dash rule. As established in Chapter 4, the dash scan greps text and
**cannot see inside a PNG**, so these bypass every gate the project runs.

### 3. Contractions throughout the whole set

Every plate uses them: *doesn't, that's, don't, can't, won't, you've, isn't, it's, what's*.
The chapter text uses **no contractions anywhere** — this was verified by grep across the file.

The most visible instance: **`ch6-image6.png` is titled "Don't Tidy First."** while the section
heading directly above it reads **"Do Not Tidy First."** The two sit within a few centimetres of
each other on the page.

This is a whole-set voice mismatch rather than a one-off, so it is worth fixing as a batch with a
single instruction rather than plate by plate.

### 4. Small rendering artifacts

- `ch6-image7.png` — the phone's after-label renders as **"AFTER6"** instead of "AFTER".
- `ch6-image8.png` — the phone screenshot shows the date **"May 14, 2004"**. Twenty-two years
  stale; 6-09 gets it right with "May 14, 2025".

### 5. Replicated phone interface · `ch6-image9.png`

Closely reproduces the iOS Photos app interface, and is honestly labelled "iPhone example shown."
Instructional use of a generic phone UI is normally fine, and the label helps. Flagging only so
the decision is a conscious one rather than an accident. A more generic album mock-up would
sidestep the question entirely if a publisher prefers.

---

## Standing image brief additions

Fold these into the brief used for every future chapter's artwork:

1. **No contractions.** House voice is "do not", "does not", "it is". This set breaks it on every
   plate.
2. **No em or en dashes.** Use middots or restructure.
3. **Figure numbers as two digits**, `6-02` not `6-022`. Proofread the number itself.
4. **Dates in screenshots must be current.**
5. **Plate titles must match the section heading verbatim** where they echo it, contractions
   included. "Don't Tidy First" against a heading of "Do Not Tidy First" is the exact failure.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_06_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old figures.
Chapter text was not changed, so the content package remains valid against it.
