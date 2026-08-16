# 6S Success · Chapter Image Placement & Finalization Prompt

Reusable prompt for wiring a chapter's improved images into its final HTML.
Reconstructed and formalized 2026-07-20 during the Chapter 1 pass. Run this once per
chapter, whenever a batch of new images lands in a chapter folder.

Companion docs: `6S_Success_CHAPTER_SUPERPROMPT.md` (authoring pipeline),
`6S_Success_DESIGN_SYSTEM.md`, `CH8_APPROACH_and_PRODUCTION_GATES.md`.

---

## The prompt

> Review the Chapter **N** final HTML document and review the images in the chapter
> folder to determine the best place to replace or insert each image. Remove all the older
> crude illustrations and insert the improved images. Then finalize the chapter HTML file
> for review. The end output should be a production and publishing ready chapter.

---

## How to execute it

### 1. Read everything before moving anything

Read `chapter_NN_final.html` end to end and **view every image in the chapter folder.**
Do not place images from filenames alone. The plates frequently carry baked-in titles,
figure numbers, and numbered callouts that must be reconciled with the prose.

### 2. Establish the mapping

The images are usually numbered in reading order and often labelled `FIGURE N-01`,
`FIGURE N-02` in the artwork itself. Confirm this rather than assuming it — the numbering
reflects generation order, which sometimes diverges from chapter order.

Build an explicit table: existing SVG → replacement image, plus a list of images with no
existing counterpart (insertions) and SVGs with no replacement (keepers).

### 3. Removal rule

Remove an inline SVG **only where a photograph replaces it.** Specifically:

- **ALWAYS KEEP the friction-meter gauge as live SVG.** It is data-driven and its needle
  geometry advances chapter to chapter; it must never become a flat image.
- **KEEP data graphics** (bar comparisons, shelf-life charts) unless a supplied image
  genuinely covers the same information. These read as intentional, not crude.
- **KEEP any SVG that is the sole canon-correct statement of something** — see the canon
  check below.
- Leave the old `.png` files on disk. Removal is from the HTML, not the filesystem.

### 4. Markup pattern

Plates carry their own title block, so frame them flush with no inner padding:

```html
<figure class="wide">
  <div class="plate">
    <img src="chN-imageM.png" alt="Figure N-0M, [title]. [Describe what is depicted,
         including every label and callout printed on the plate.]">
  </div>
  <figcaption><b>Lead-in.</b> Commentary that ADDS to the plate rather than repeating
  its printed title.</figcaption>
</figure>
```

Required CSS (add once per chapter template):

```css
figure img{display:block;width:100%;height:auto;border-radius:12px}
.plate{border:1px solid var(--rule);background:var(--panel);border-radius:14px;
       padding:0;overflow:hidden;box-shadow:0 1px 0 var(--rule2)}
.plate img{border-radius:0}
figure.wide{max-width:1000px;margin-left:auto;margin-right:auto}
```

Reference images by **bare filename** — they sit beside `final.html`, not in a subfolder.

### 5. Reconcile text to art

This is the step that gets skipped and causes the most rework.

- If the plate has **numbered callouts**, the chapter's numbered key must match them
  exactly — same count, same order, same labels. Rewrite the key to the art; the art is
  more expensive to change than the prose.
- Write a short **bridging paragraph** before each newly inserted plate. An image dropped
  between two unrelated paragraphs reads as decoration.
- **Delete `<span class="artnote">` placeholders** ("Final book: photograph here") once a
  real photograph satisfies them. Leave the `.artnote` CSS rule — the shared template
  still uses it in unconverted chapters.

### 5b. Check figure ORDER, not just placement

After placing everything, list the images in document order and confirm the numbers **ascend**.
It is easy to insert a figure at the paragraph it belongs to and accidentally put 2-04 ahead of
2-03, because the artwork numbering follows generation order and the prose does not always
agree. This happened in Chapter 2 and had to be fixed.

```bash
grep -o 'chN-image[0-9]*\.png' chapter_NN_final.html   # must ascend
```

When they disagree, move the *figure* to a paragraph that restores order — there is almost
always a later paragraph that suits it as well or better. Renumbering the artwork is the
last resort.

### 5c. Watch for portrait-format plates

Most plates are landscape (1536×1024). A portrait one (1024×1536) rendered at full width runs
~1,400px tall and swamps the page. Use the `figure.tall` class:

```css
figure.tall{max-width:660px;margin-left:auto;margin-right:auto}
```

Check natural dimensions during verification (the JS snippet below reports them).

### 6. CANON CHECK — do this before wiring anything in

Generated images routinely default to textbook 5S naming and get this book wrong.
**Verify every image that states the six S's against the canon:**

| # | Canonical | Common wrong substitutions to reject |
|---|---|---|
| 1 | **Sort** | — |
| 2 | **Straighten** | "Set in Order" |
| 3 | **Shine** | "Sweep" |
| 4 | **Safety** | *omitted entirely* — the most common and most serious error |
| 5 | **Standardize** | — |
| 6 | **Sustain** | "Self-Discipline", "Succeed", "Enjoy It" |

Safety-as-the-fourth-S is the book's central differentiator and the subject of Chapters
20 to 22. **Any image that omits Safety, renames Straighten, or invents a seventh S must
be held out and flagged for regeneration — never silently inserted.** A canon violation in
a figure contradicts the surrounding chapters and is far more damaging than a missing image.

Surface the conflict to Phil with the exact wrong-vs-right table and let him decide.

**Also check for third-party trademarks.** Generated images sometimes render real corporate
logos (a synthesized Toyota mark appeared in `ch2-image3.png`). Naming a company in the text is
fine; reproducing its mark in a commercial book is a rights question. Flag any logo you see.
Readable product packaging inside a photograph of a real room (Ch 3 is full of it) is ordinary
editorial use — note it, don't block on it.

**The canon-correct reference image.** `6S-Success-Chapter-3/ch3-image2.png` ("The Entire 6S
Loop") gets all six right, in order, with Safety fourth, and labels every handoff. Point any
regeneration request at it rather than describing the six from scratch.

### 6a-ter. If the chapter has a frozen strings doc, check every plate against it

From Chapter 8 onward each chapter folder holds `CHNN_CANONICAL_STRINGS_AND_BRIEF.md`. **Read it
first.** It fixes the hero device, the outcome vocabulary, the worked example and the scope
fences, which turns plate selection from a judgement call into a checklist:

- Does the plate use the **frozen vocabulary verbatim**? A synonym is a defect. Chapter 10's
  `image11` renamed the *holding area* to "Deadline Decision Zone" in the very chapter that
  establishes the term.
- Does it use the **canonical worked example**, with the right items and the right numbers?
- Does it respect the **scope fences**? Chapter briefs say explicitly what belongs to neighbours.
- Does it **misapply the hero device**? Chapter 10's `image12` red-tagged every item in a working
  drawer, when red tags are only for undecidable maybes headed to a holding area.

### 6a-quater. Watch for a rival system

The most damaging defect found so far. Generated sets like to invent a tidy branded framework and
repeat it across every plate. Chapter 10 produced seven figures pushing "Tag It · Date It · Review
It · Decide It · Repeat It" as **the** system, applied to every room, never once mentioning the
six S's.

A single wrong figure is a defect. Seven consistent figures are a **competing methodology**, and a
reader will believe them over the prose. Any framework that is not the six S's must be clearly
subordinate to them, or held.

### 6b. SCAN FOR DEAD QR CODES

Generated plates sometimes include a QR code offering a downloadable resource. **Assume it is
fake until proven otherwise** — two in Chapter 3 looked perfectly scannable but decoded to an
empty payload. A dead QR in a printed book is unrecoverable for the reader, and the caption has
usually promised them something real.

```bash
python -c "
import cv2, sys
det = cv2.QRCodeDetector()
for f in sys.argv[1:]:
    img = cv2.imread(f)
    data, pts, _ = det.detectAndDecode(img)
    print(f, 'LOCATED' if pts is not None else 'no-qr', repr(data))
" chN-image*.png
```

`LOCATED` with an empty payload means a decorative fake. Flag it: the plate can still be used,
but the QR must be removed or replaced with a code generated from a real, live URL before print.

**This scan produces FALSE POSITIVES.** In Chapter 4 it flagged four images; only one actually
contained a QR code. The detector's locator latches onto photo texture and onto grid-shaped
layouts. **Always confirm visually before acting** — never strip a "QR" from a plate that has
none, and never report a dead QR you have not seen with your own eyes.

### 6a-bis. READ THE PLATE'S OWN TEXT AGAINST THE CHAPTER

The single highest-value check, and the one no automated gate can do. **Validation cannot read a
PNG**, so everything printed inside a plate bypasses every scan the project runs. Chapter 5 lost
19 of 20 images to defects in this class. For every plate, check:

- **Scales.** Does the plate's scale match the chapter's? (Ch 5 plates said "1 to 5"; the
  chapter says "zero to five", with the zero load-bearing across six dependent paragraphs.)
- **Worked-example numbers.** Do the scores, totals and "lowest score" callouts match the
  manuscript exactly? (Ch 5's `3a` printed the right total, 14/30, but the wrong sub-scores and
  inverted which S was weakest.)
- **Quotations and attributions.** Verify every attributed quote. Generated plates reach for
  business-cliché epigraphs that are commonly misattributed — Ch 5 produced "What gets measured
  gets managed / Drucker" (the Drucker Institute says it is not in his work) and "What gets
  measured gets improved / Tom Peters". A misattributed epigraph is a factual error in print.
- **House voice.** This book uses **no contractions**. The Ch 5 plates used them throughout.
- **Typos.** Ch 5's `8a` shipped "Easy **yo** return" and "cables and **charges**".

When a plate's data conflicts with the text, work out which is cheaper to change **before**
recommending one. Text looks cheap and often is not: the Ch 5 scale appeared in ~8 places in the
source trio **plus 37 content-package files**, so regenerating two plates was far cheaper than a
package rebuild. Run the grep before you advise.

```bash
grep -rl '<the disputed string>' content-package/ | wc -l
```

### 6c. Check for em dashes baked into the artwork

The project rule is **no em dashes, anywhere, ever**. The validation pass greps the manuscript
and the HTML, but **it cannot see inside a PNG**, so a dash rendered into a plate bypasses every
gate the project has. `ch4_image2.png` shipped with one ("exciting—until reality hits").

Read the plate's own text when you view it and flag any em or en dash for regeneration. Add
"no em or en dashes in artwork, use middots or restructure" to the standing image brief.

**Hit rate so far:** Ch 1, two of fifteen images violated canon. Ch 2, three of eleven. Assume
roughly one in five will be wrong and check every single one.

### 7. Verify before claiming done

Do not assert the chapter is publishing-ready without running these:

```bash
grep -o 'chN-image[0-9]*\.png' chapter_NN_final.html   # placement order
grep -c '<img ' chapter_NN_final.html                  # count
grep -c '<svg ' chapter_NN_final.html                  # keepers only
grep -n 'artnote' chapter_NN_final.html                # should be CSS lines only
```

Then **render it.** `file://` URLs are blocked in the browser tool, so serve locally:

```bash
python -m http.server 8731     # run from the chapter folder
```

and check in-page via the JS tool:

```js
const imgs=[...document.images];
({total: imgs.length,
  allLoaded: imgs.every(i=>i.complete && i.naturalWidth>0),
  broken: imgs.filter(i=>!(i.complete&&i.naturalWidth>0)).map(i=>i.src),
  missingAlt: imgs.filter(i=>!i.alt||i.alt.trim().length<20).map(i=>i.src),
  svgsRemaining: document.querySelectorAll('svg').length,
  horizontalOverflow: document.documentElement.scrollWidth>document.documentElement.clientWidth})
```

Every image loaded, every alt substantial, SVG count equals the intended keepers, no
horizontal overflow. Kill the server when done.

### 8. Scope of the change

**Update the master `chapter_NN_final.html` only.** Do not propagate to the publishable
HTML, the `content-package/` sub-packages, or the Desktop flattened copy until any held
images are resolved — otherwise the package gets built from a partial chapter.

Write a `CHNN_IMAGE_FINALIZATION_NOTES.md` in the chapter folder recording the placement
map, the SVGs kept and why, text changes made, and any images held back with the exact
regeneration request.

---

## The standing image brief

Give these to whoever generates the artwork. Every one comes from a defect that actually shipped.

1. **Six S's, always all six, always in order, Safety fourth:** Sort · Straighten · Shine ·
   **Safety** · Standardize · Sustain. Never "Set in Order". Never invent a sixth
   ("Succeed", "Share", "Enjoy It"). Reference image: `6S-Success-Chapter-3/ch3-image2.png`.
2. **No contractions.** House voice is "do not", "does not", "it is". The entire Chapter 6 set
   broke this, including a plate titled "Don't Tidy First" sitting under a heading reading
   "Do Not Tidy First".
3. **No em or en dashes.** Middots or restructure.
4. **No attributed quotations** unless the attribution has been verified. Generated plates reach
   for misattributed business clichés ("What gets measured gets managed / Drucker").
5. **No QR codes** unless a real live URL is supplied to encode. Decorative QRs decode to nothing.
6. **Figure numbers as two digits**, `6-02` not `6-022`. Proofread the number itself.
7. **Any dates shown in screenshots must be current.**
8. **Plate titles must match the chapter's section heading verbatim** where they echo it.
9. **Any scale, score or worked example must match the manuscript exactly** — including which
   item is highest and lowest, not just the total.

## Which generation of art you are looking at

Two visual generations exist across the chapter folders and they behave very differently:

- **Jul 4 to 5 batch** (Ch 5 originals, all of Ch 6): serif display, cream ground, deep green and
  gold. **Closer to the book's design system.** Chapter 6's set needed nothing held.
- **Jul 19 to 20 batch** (Ch 1 to 4, Ch 5 "a" variants): sans-serif infographic, navy/red/green.
  Denser and more informative, but the source of nearly every canon and data defect found.

Neither is simply "better". Check which one a folder holds before assuming the newer files
supersede the older ones — in Chapter 5 the `Na` variants did **not** supersede `N` past 6.

## Known defect to check in every chapter

`.keylist` is an `<ol>` whose `<li>` items carry their own "1 ·", "2 ·" lead-ins, so it
renders **doubled markers** ("1. 1 · Keys with no home"). Fixed in Chapter 1 by adding
`list-style:none;padding:0` to `.keylist`. The same latent bug exists in every chapter
template that uses a numbered figure key.
