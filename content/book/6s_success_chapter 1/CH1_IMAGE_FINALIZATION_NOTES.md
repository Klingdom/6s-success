# Chapter 1 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_01_final.html` (master copy only)

---

## What was done

All crude inline SVG figures that had a photographic replacement were removed and
replaced with the ChatGPT-generated plates. 13 of the 15 supplied images are wired in.
The plates carry their own baked-in `FIGURE 1-NN` label and title block, so they are
placed flush in a borderless `.plate` frame with no inner padding, and the HTML
`figcaption` beneath them adds commentary rather than repeating the title.

### Placement map (document order)

| # | Image | Placement | Action |
|---|---|---|---|
| 1 | `ch1-image1.png` | Chapter opener | replaced entryway SVG |
| 2 | `ch1-image2.png` | After "In this chapter" | replaced Two Tuesdays SVG |
| 3 | `ch1-image4.png` | "Effortless Is a System" · after the key-dish passage | NEW insertion |
| 4 | `ch1-image5.png` | "Effortless Is a System" · close | replaced Two Theories SVG |
| 5 | `ch1-image6.png` | "Why Homes Quietly Get Harder" · opening | NEW insertion |
| 6 | `ch1-image10.png` | same section · after "asking you a question" | NEW insertion + bridging paragraph |
| 7 | `ch1-image7.png` | same section · close | replaced junk-drawer band SVG |
| 8 | `ch1-image14.png` | "Cleaning, Organizing, and 6S" · close | NEW insertion + bridging paragraph |
| 9 | `ch1-image12.png` | "Meet the Six S's" · close | NEW insertion + bridging paragraph |
| 10 | `ch1-image3.png` | "Spot the Friction" | replaced friction-scene SVG |
| 11 | `ch1-image13.png` | "Your First Move" | replaced before-photos SVG |
| 12 | `ch1-image11.png` | "Your First Move" · close | NEW insertion + bridging paragraph |
| 13 | `ch1-image9.png` | "One Notch Calmer" · close | NEW insertion + bridging paragraph |

### SVGs deliberately KEPT (5)

- **Cleaning / Organizing / 6S shelf-life bars** (3 SVGs). These are data graphics, not
  crude illustration, and no supplied image covers the "how long it lasts" comparison.
- **The Six S Loop.** Kept because it is the only canon-correct statement of the six S's
  in the chapter. See the blocker below.
- **The friction meter.** Kept as live SVG per the standing rule — it is data-driven and
  its needle geometry advances chapter to chapter.

### Text changes made alongside

- The numbered friction key was rewritten from 8 entries to **12**, matching the callouts
  printed on Figure 1-03 exactly.
- `.keylist` got `list-style:none`. It is an `<ol>` whose items already carry their own
  "1 ·", "2 ·" lead-ins, so it had been rendering doubled markers ("1. 1 · Keys..."). This
  bug pre-dated the image work and is worth checking in the other chapters' templates.
- One clause added to the "sequence is the method" paragraph explaining why **Safety** sits
  in the middle. The chapter previously listed Safety in the loop figure but never justified
  its position.
- Six short bridging paragraphs written to lead into the newly inserted plates.
- All `<span class="artnote">` placeholders removed — they said "Final book: photograph
  here", which the real photographs now satisfy. The `.artnote` CSS rule was left in place
  since the shared chapter template still uses it.

---

## BLOCKER · two images held back, pending regeneration

**`ch1-image8.png` (Figure 1-08, "The 6S Transformation") and `ch1-image15.png`
(Figure 1-15, "The 6S Journey. One Step at a Time.") are NOT wired in.**

Both state a set of six S's that contradicts this book's canon.

| | Book canon | Fig 1-08 says | Fig 1-15 says |
|---|---|---|---|
| 1 | Sort | Sort | See It |
| 2 | Straighten | **Set in Order** | Sort It |
| 3 | Shine | Shine | Set It |
| 4 | **Safety** | **Standardize** | Shine It |
| 5 | Standardize | **Sustain** | Sustain It |
| 6 | Sustain | **Succeed** | **Enjoy It** |

Safety-as-the-fourth-S is the book's central differentiator and the subject of
Chapters 20, 21 and 22. Figure 1-08 omits Safety entirely and invents a sixth S
("Succeed"). Figure 1-15 omits both Safety and Standardize. Either one, dropped into
Chapter 1, would contradict the Six S Loop figure sitting a few screens away in the
same chapter.

### Regeneration request

Re-generate both plates with these six steps, in this order, using these exact words:

1. **Sort** — Keep what belongs. Remove what does not.
2. **Straighten** — Give everything a home, by how often you use it.
3. **Shine** — Clean in a way that also reveals problems early.
4. **Safety** — Protect the people who use the space, first.
5. **Standardize** — Lock in the best way you know today.
6. **Sustain** — Keep the gains. Keep improving, gently.

Do not substitute "Set in Order" for Straighten. Do not add "Succeed", "Enjoy It",
or any seventh step. Safety must appear, and must appear fourth.

Once regenerated, both drop straight in:
- **1-08** replaces the three-panel shelf-life SVG in "Cleaning, Organizing, and 6S Are
  Not the Same Thing", or sits alongside it as a before/after.
- **1-15** replaces the Six S Loop SVG in "Meet the Six S's".

---

## Images suited to later chapters

Three plates were placed in Chapter 1 at the author's direction, but their subject matter
properly belongs to later chapters. If those chapters later want dedicated art, note that
the Chapter 1 versions already exist and could be re-cut rather than re-generated:

- **1-10 "The One Question That Changes Everything"** — this is the Sort filter, Chapter 8.
  Placed here as a deliberate look-ahead with a "you will meet this properly when we reach
  Sort" caption.
- **1-12 "Your Home. Your Rules."** — closest to Chapter 12 (Straighten) territory.
- **1-14 "Distractions Out. Focus In."** — closest to Chapter 16 (Shine) territory.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_01_final.html` was updated.** The
publishable HTML, the `content-package/` sub-packages, and the Desktop flattened copy at
`C:\Users\philk\Desktop\6S-Chapter-1-Content-Package\` still reference the old figures and
contain no image files. Propagate once the two held images are resolved, so the package is
built from a final chapter rather than a partial one.
