# Chapter 25 · Image Finalization Notes

Date: 2026-07-22
File finalized: `chapter_25_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH25_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

Chapter 25 "Pictures, Storyboards, and Visual Standards" COMPLETES Standardize (the 5th S) at the
STANDARDIZE COMPLETE milestone. 12 generated plates landed. **This batch is excellent: ZERO QR codes
(confirmed visually), no brands, and the three core devices are each covered by a FULLY CLEAN photo.**
So this is the most photo-rich pass in Part 7: three SVGs replaced with clean photos + three clean
editorials wired.

---

## What was done

**6 photos wired in (3 SVGs replaced + 3 editorial), only the friction-meter SVG RETAINED. 7 figures.**

### Final figure layout (7 figures)

| Section | Figure | Source |
|---|---|---|
| Opener (tell vs show) | `ch25-image01.jpg` "Tell versus Show" | photo (replaced opener SVG) |
| The Picture of the Ideal State | `ch25-image02.jpg` "The Ideal-State Photo" | photo (replaced FIG2 SVG) |
| The Picture of the Ideal State (building it) | `ch25-image05.jpg` "Building the Ideal-State Photo" | photo (NEW) |
| The Storyboard | `ch25-image06.jpg` "The Storyboard Standard" | photo (replaced FIG3 SVG) |
| Make It Match-able | `ch25-image07.jpg` "Storyboard versus Written Instructions" | photo (NEW) |
| Make It Match-able | `ch25-image08.jpg` "Shoot From the User's Perspective" | photo (NEW) |
| The Needle Reaches Standardize Complete | friction meter (STANDARDIZE COMPLETE milestone) | **SVG RETAINED** |

Photo figure numbers ascend in document order: 25-01, 25-02, 25-05, 25-06, 25-07, 25-08.

### The six wired photos (the three SVG-replacers viewed directly)

- **`25-01` "Tell versus Show" (opener) — FULLY CLEAN.** A photoreal split kitchen cupboard: a woman
  puzzling over a wordy handwritten card ("Tell") vs. the same cupboard with a small ideal-state
  photo taped inside the door and "Match This," calmly matched ("Show"). The show-do-not-tell reframe
  embodied. Replaced the opener SVG.
- **`25-02` "The Ideal-State Photo" — FULLY CLEAN.** A pantry with the ideal-state photo mounted at
  the point of use, "Match This," the real shelves matching. Replaced the ideal-state SVG.
- **`25-06` "The Storyboard Standard" — FULLY CLEAN.** A three-frame entryway-reset storyboard
  (Shoes Returned → Bag Hung → Keys Placed), reusing the book's launch-pad running example. Replaced
  the storyboard SVG.
- **`25-05` "Building the Ideal-State Photo" — CLEAN.** The five-step how-to (reset → perfect →
  photograph at eye level → print small → post at point of use). Placed in *The Picture of the Ideal
  State*.
- **`25-07` "Storyboard versus Written Instructions" — CLEAN.** A binder-and-page (hard to follow)
  vs. a three-frame bathroom-reset storyboard (easy), which also carries the frozen Common Mistake
  ("a few honest photos beat an elaborate binder"). Placed in *Make It Match-able*.
- **`25-08` "Shoot From the User's Perspective".** Too-high vs. eye-level pantry shots, the frozen 6S
  Tip (shoot from the angle/light of use). Placed in *Make It Match-able*. Defects: two contractions
  ("Doesn't", "That's").

Only the friction-meter SVG was kept (standing rule; it carries the STANDARDIZE COMPLETE milestone
and the fully-engaged anti-backslide catch).

### Canon, fence, and tone checks

No six-S sequence in any wired plate. **The Chapter 14 fence held:** every wired plate is a
photo-of-the-ideal-state or a storyboard (visual STANDARD showing the result to match), not a
Chapter-14 visual CONTROL (label / outline / boundary / Glance Test) — the incidental canister labels
in `25-02` are scenery, not the device. **The "corporate" danger word was well avoided** (homely
taped photos, an entryway storyboard), and the Sustain fence held (no adherence/audit system on the
wired plates). No brands (generic phone/printer in `25-05`).

### Finalized to publication standard (same as Ch 1 to 24)

- The six photos optimised **12.0 MB → 1.38 MB** (1600px q82 progressive JPEGs; `<img src>` .jpg).
- Migrated off inline `<style>` + Google Fonts to the shared `../assets/`.
- `<meta name="description">` added from the frozen subtitle.
- Cross-chapter nav added (prev → Chapter 24, "Chapter 25 of 50"). **Chapter 24's previously-empty
  next-slot was wired forward to Chapter 25.**
- The one `artnote` placeholder removed.
- **Wiring note (fixed):** the first pass hit an anchor-prefix bug (`<!-- FIGURE 2` matched the
  inserted `<!-- FIGURE 25-01` comment), which briefly overwrote `25-01` with `25-02` and left the
  ideal-state SVG in place. Corrected with a follow-up repair using collision-safe anchors; final
  state verified: 6 images in ascending order (01/02/05/06/07/08) + 1 SVG, no leftover ideal-state
  SVG.
- Verified: all six JPEGs, both stylesheets, and the HTML resolve 200; the page renders with the six
  photos loaded and the friction-meter SVG. (A browser overflow reading was a false positive from a
  collapsed-window measurement, clientWidth 0, after a long session; the markup uses the same
  overflow-safe `book.css` / `figure.wide` / `.plate` pattern as Ch 20 to 24.)

### Baked-in defects on wired photos (flag for batch fix; QR-free)

- **`25-08`** — two contractions ("Doesn't match", "That's the standard").
- **`25-01`, `25-02`, `25-05`, `25-06`, `25-07`** — fully clean.

No QR codes anywhere in the Chapter 25 set (the whole batch is QR-free).

---

## HELD BACK · 6 plates

| Plate | Reason |
|---|---|
| `image03` "From Memory to Matching" | Clean but abstract concept twin of `image04`; the wired photos carry the concept concretely. |
| `image04` "One Shelf. Four Interpretations." | Clean concept diagram (many interpretations vs one picture); supporting only, not one of the three core devices. |
| `image09` "Compare, Learn, Improve" | **Sustain fence** — dated before/after progress tracking, "celebrate wins", "progress builds momentum"; + contraction. |
| `image10` "Make It Consistent" | **Sustain fence** — a before/after comparison METHOD, not the Ch 25 visual-standard device. |
| `image11` "Photo Evidence That Tells the Truth" | **Corporate + Sustain fence** — "6S audit" ×2, "your photos are data" (institutional tone the chapter forbids); + en dash + contraction. |
| `image12` "From Photos to Action" | Sustain drift ("prove it worked", "make photo evidence a habit") + borrowed-quote motivational tone + contractions. |

### The pattern in the held set

`image09`–`image12` quietly turn the chapter into a Sustain/audit "photo-evidence" system — dated
before/after tracking, review cadence, and "6S audit" framing — which is Chapters 26–30, not the
Chapter 25 visual-standard device. They also carry all the contractions, the only en dash, and the
only corporate language in the batch, and reuse one under-sink scene four times. `image03`/`image04`
are clean but only abstract concept diagrams. The chapter's three core devices are better served by
the six wired photos.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_25_final.html` was updated.** Chapter text was not
changed. **This completes Part 7 (Standardize) image placement across Ch 23 to 25; five of the six
S's are now done.** Next is Ch 26, which opens Part 8 (Sustain), the sixth and final S.
