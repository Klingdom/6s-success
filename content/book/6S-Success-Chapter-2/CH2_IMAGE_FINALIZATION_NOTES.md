# Chapter 2 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_02_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`

---

## What was done

8 of the 11 supplied images are wired in. Every inline SVG that had a correct photographic
replacement was removed. Figures now run **2-01 through 2-08 in strict reading order**.

Note the labelling convention differs from Chapter 1: `ch2-image1.png` is a **chapter title
plate** ("CHAPTER 2 · What Is 6S?") rather than a numbered figure, and figure numbering on
the artwork starts at 2-03. The numbers on the plates still ascend in document order.

### Placement map (document order)

| Image | Placement | Action |
|---|---|---|
| `ch2-image1.png` | Chapter opener | replaced organized-drawer SVG |
| `ch2-image2.png` | "The Calm You Can Feel" · after the findability paragraph | NEW insertion |
| `ch2-image3.png` | "Where This Actually Came From" | replaced timeline SVG |
| `ch2-image4.png` | same section · after "not a car idea, a human idea" | NEW insertion + bridging line |
| `ch2-image5.png` | "The Five S's, in Plain English" | replaced bilingual-mapping SVG |
| `ch2-image6.png` | "How Five Became Six" | replaced 5S→6S growth SVG |
| `ch2-image7.png` | same section · after the safety-at-home paragraph | NEW insertion |
| `ch2-image8.png` | "Your Home Is Not a Factory" | replaced factory/home split SVG |

### SVGs deliberately KEPT (2)

- **The scale diagram** ("One method, any scale") under *Same Method, Any Size*. Its natural
  replacement, `ch2-image11.png`, was held back — see below.
- **The friction meter.** Kept as live SVG per the standing rule.

### Text changes made alongside

- One bridging line added before Figure 2-04 ("Look at what the visual workplace turns into
  once it stops wearing steel-toed boots.").
- The Figure 2-06 caption was rewritten to absorb a quirk in the artwork — see the numbering
  note below — turning it into a teaching point rather than leaving it unexplained.
- The opener's `artnote` placeholder was removed. No other artnotes existed in this chapter.
- New CSS: `figure img`, `.plate`, `figure.wide`, and a new **`figure.tall`** (max-width 660px)
  because `ch2-image5.png` is the first portrait-format plate in the book (1024×1536). At full
  width it would have rendered 1,400px tall and swamped the page.

### Ordering defect caught and fixed

Figure 2-04 was initially placed immediately after the visual-workplace paragraph, which sits
**before** the timeline. That put 2-04 ahead of 2-03 in the document. It was moved to follow
the "not a car idea, a human idea" paragraph instead, which both restores ascending figure
order and reads better, since that paragraph is about the same logic moving between settings,
which is exactly what the plate shows.

---

## HELD BACK · three images, pending regeneration

All three are titled **6S** but depict only **five** steps, with **Safety missing**. This is
the same failure mode as Chapters 1's held images, and it is the more serious kind of error in
this particular chapter, because Chapter 2 is *the chapter that explains where the sixth S
came from*. A figure captioned "The 6S Journey" that lists five steps would directly contradict
the section it sits in.

| Image | Title | What it shows | Problem |
|---|---|---|---|
| `ch2-image9.png` | The 6S Journey | Sort · Straighten · Shine · Standardize · Sustain | Safety absent |
| `ch2-image10.png` | Your First 6S Action Plan | Choose · Assess and Sort · Straighten and Shine · Standardize · Sustain | Safety absent; also, no "action plan" section exists in Ch 2 (this is Ch 3 / Ch 4 material) |
| `ch2-image11.png` | 6S in Every Room | Five rooms, each listing Sort · Straighten · Shine · Standardize · Sustain | Safety absent, repeated five times |

### Regeneration request

Re-generate all three with the full six, in this order, using these exact words:

1. **Sort** — Remove what you do not need.
2. **Straighten** — Put everything in the right place.
3. **Shine** — Clean your space and keep it clean.
4. **Safety** — Make your space safe for you and your family.
5. **Standardize** — Create simple standards and visual cues.
6. **Sustain** — Build habits and keep improving.

Safety must appear, and must appear **fourth**, between Shine and Standardize. Note that
`ch2-image6.png` already gets this exactly right and can be used as the reference.

Once regenerated:
- **2-11** replaces the scale-diagram SVG under *Same Method, Any Size* — it is a direct
  upgrade of that figure and the only thing currently blocking that SVG's removal.
- **2-09** would suit the close of *Putting It Together*.
- **2-10** is better held for Chapter 3 or 4, where a first action plan actually belongs.

---

## Two things to decide before publication

**1. Toyota trademark (`ch2-image3.png`).** The timeline plate renders the **Toyota corporate
logo** and a factory sign reading "TOYOTA" as part of an AI-generated image. The chapter text
names Toyota factually, which is normal and fine for a history discussion. Reproducing the
*logo* in a commercial book is a different question, and it is a synthesized approximation of
the mark rather than the real asset. Recommend replacing the logo panel with a generic
mid-century assembly-line image and letting the caption carry the Toyota reference in words.
Worth a rights check either way.

**2. Figure 2-06 badge numbering.** In the bottom row the badges read **1, 2, 3, 6, 4, 5** —
Safety carries a "6" while occupying the fourth slot. This is defensible (Safety was the sixth
to be *named* but sits fourth in the *doing*, which is exactly the book's position), and the
caption has been written to say so explicitly. But a reader skimming the row may read it as an
error. If you would rather it be unambiguous, regenerate with Safety badged **4** and
Standardize/Sustain renumbered **5** and **6**.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_02_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old figures.
Propagate once the three held images are resolved.
