# Chapter 4 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_04_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`

---

## What was done

10 of the 18 supplied images are wired in. Figures run **4-02 → 4-11 in ascending order**.
All three replaceable SVGs were retired; **only the friction meter remains as live SVG**, which
makes Chapter 4 the most fully converted chapter so far.

### Placement map (document order)

| Image | Section | Action |
|---|---|---|
| `ch4_image1.png` | Chapter opener | replaced the garage-doorway SVG |
| `ch4_image2.png` | Why the First Target Decides Everything | NEW insertion |
| `ch4_image3.png` | same section | NEW insertion |
| `ch4_image5.png` | The Two Questions That Pick a Target | NEW insertion |
| `ch4_image6.png` | same section | NEW insertion + bridging line |
| `ch4_image7.png` | same section | replaced the **hero First Target Map** SVG |
| `ch4_image8.png` | same section | NEW insertion + bridging line |
| `ch4_image9.png` | Why Not the Garage (Yet) | NEW insertion |
| `ch4_image10.png` | Make Your Shortlist | replaced the **Target Scorecard** SVG |
| `ch4_image11.png` | Choose, and Write It Down | NEW insertion |

### Unusually good text-to-art alignment

This is the best-matched image set in the project so far. Three plates carry titles that match
the chapter's own headings and motifs word for word:

- **4-07 is titled "The First Target Map"** — the exact name of the chapter's hero motif, with
  all four quadrant labels (Start Here / Soon, Not First / Fine, Not Now / Avoid For Now)
  identical to the SVG it replaced.
- **4-05 is titled "The Two Questions That Pick a Target"** — the exact `<h2>` of that section.
- **4-09 "Why the Garage Waits"** maps directly onto "Why Not the Garage (Yet)".

The artwork also has **internal figure-number consistency**: Figure 4-10 explicitly
cross-references "(Figure 4-07)" for the map, and 4-05 forward-references the Target Scorecard
as "next". Those references now hold true in the finalized HTML, since 4-07 and 4-10 sit where
the art expects them.

### Naming inconsistency (unresolved by design)

Chapter 4 uses **underscores** (`ch4_image1.png`) against the `chNN-imageN.png` hyphen
convention used by every other chapter. Left as-is deliberately: renaming the files would be a
one-line change but would break any external reference, and the HTML is internally consistent.
Worth normalising in a single sweep across the book rather than piecemeal.

### One section left without a figure

**"Win Where You Will See It"** (the three filters) carries no figure. Nothing in the supplied
set covers visibility / control / emotional-weight as a trio. It is a short, text-driven section
and reads fine unillustrated, but it is the obvious gap if a new plate is ever commissioned.

### Other changes

- Four bridging lines written for the new insertions.
- The single `artnote` placeholder removed.
- New CSS: `figure img`, `.plate`, `figure.wide`, `figure.tall`.
- Note that `ch4_image1.png` is a **bare photograph** with no title block or figure number,
  unlike every other plate in the set. It is used as the unnumbered chapter opener, the same
  role `ch2-image1.png` plays in Chapter 2. Numbered figures therefore start at 4-02.

---

## ACTION REQUIRED · one dead QR code

**`ch4_image11.png`** carries a QR code captioned *"SCAN FOR MORE FIRST TARGET IDEAS."* It
decodes to an **empty payload** — same fake-QR pattern found in Chapter 3.

The image is wired in because its content is strong and it ends with a fill-in-the-blank line
("What will your first target be? ______") that pairs perfectly with the "Choose, and Write It
Down" section. But the QR must be removed or replaced with a code generated from a real URL
before print.

**Note on the automated scan:** running OpenCV's `QRCodeDetector` across all 18 images reports
QR-like patterns in `ch4_image1`, `ch4_image7`, `ch4_image9` and `ch4_image11`. **Only
`ch4_image11` actually contains a QR code.** The other three are false positives, where the
detector's locator latches onto photo texture and grid layouts. Visual confirmation is required
before acting on that scan — do not strip a "QR" from an image that does not have one.

---

## HELD BACK · eight images

### Four canon violations (the worst cluster so far)

`ch4_image12`, `ch4_image13`, `ch4_image14`, `ch4_image15` all walk the reader through the
method, and **all four get it wrong in the same way**:

| | Canon | These four say |
|---|---|---|
| 2 | Straighten | **Set in Order** |
| 3 | **Shine** | *absent* |
| 4 | **Safety** | *absent* |

`ch4_image13` compounds it with a photographed notepad reading *"Know the 5 steps"* and a plan
listing *1. Empty 2. Sort 3. Set in order 4. Standardize 5. Sustain*. `ch4_image15` shows the
same five-step notepad. In a book whose entire thesis is that there are **six** S's and that
**Safety** is the fourth, these would be actively damaging.

**Regeneration reference:** `6S-Success-Chapter-3/ch3-image2.png` gets all six right, in order,
with Safety fourth. Point any regeneration at it.

### One redundant

`ch4_image4.png` ("The Friction Compass") presents the same four quadrants as 4-07 but as a
compass rose rather than a grid. The chapter text explicitly describes "a two by two grid", so
4-07 is the correct fit and 4-04 would duplicate it. Usable elsewhere if a softer, more
metaphorical treatment is ever wanted.

### Three out of scope

`ch4_image16` (Problem Solving Guide), `ch4_image17` (Troubleshooting Flow) and `ch4_image18`
(Sustain & Level Up) are well made but cover material Chapter 4 does not contain — this chapter
ends at *choosing and writing down* a target, before any work begins. 4-16 and 4-17 are also
near-duplicates of each other. 4-18 is Sustain material and would suit Part 8.

---

## Style violation to fix at regeneration

**`ch4_image2.png` contains an em dash**: *"Big goals feel exciting—until reality hits."*

The project rule is **no em dashes, anywhere, ever** (`6S_Success_PROGRESS.md`, settled
decisions). The validation pass scans manuscripts and HTML for this, but **it cannot see inside
images**, so baked-in dashes slip through every gate the project currently has. The image is
wired in because a single dash inside artwork is a low-severity cosmetic issue, but it should be
corrected whenever this plate is next regenerated.

**Worth adding to the standing image brief:** no em dashes or en dashes in generated artwork;
use middots or restructure the sentence.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_04_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old figures.
Propagate once the QR is resolved and the four canon-violating plates are regenerated.
