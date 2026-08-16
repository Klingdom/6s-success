# Chapter 3 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_03_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`

---

## What was done

10 of the 17 supplied images are wired in. Figures run **3-01 → 3-13 in ascending order**.
Every one of the six steps now carries photographic figures except Safety and Standardize,
which retain their SVGs because no supplied image covers them (see the gap note below).

### Placement map (document order)

| Image | Section | Action |
|---|---|---|
| `ch3-image1.png` | Chapter opener | replaced the cluttered-cabinet SVG |
| `ch3-image2.png` | One Loop, Walked Once | replaced the **hero 6S Loop** SVG |
| `ch3-image3.png` | Step one · Sort | replaced the Sort half of the two-panel SVG |
| `ch3-image4.png` | Step one · Sort | NEW insertion + bridging line |
| `ch3-image5.png` | Step two · Straighten | replaced the Straighten half of the two-panel SVG |
| `ch3-image6.png` | Step two · Straighten | NEW insertion + bridging line |
| `ch3-image7.png` | Step three · Shine | replaced the Shine close-up SVG |
| `ch3-image8.png` | Step three · Shine | NEW insertion + bridging line |
| `ch3-image12.png` | Step six · Sustain | replaced the before/after SVG, relocated (see below) |
| `ch3-image13.png` | Step six · Sustain | NEW insertion + bridging line |

### The hero figure is the win here

`ch3-image2.png` is the **first fully canon-correct six-step image produced for this book**:
Sort · Straighten · Shine · **Safety** · Standardize · Sustain, in the right order, with
Safety fourth. Better still, it carries the *handoff labels* on the arrows (makes room, gives
a home, reveals the truth, protects what matters, makes normal visible, keeps it alive), which
is precisely the argument of this chapter's "How Each Step Hands Off the Next" section. It is a
direct and substantial upgrade on the SVG it replaced. **Use it as the reference image when
regenerating any six-step figure anywhere else in the book.**

### SVGs deliberately KEPT (3)

- **The Safety swap** (Step four). No supplied image covers Safety.
- **The Standardize + reset** figure (Steps five/six). No supplied image covers the
  door-label standard.
- **The friction meter.** Kept as live SVG per the standing rule; this is the chapter where
  the needle takes its first move, so it must stay data-driven.

### Text changes made alongside

- Four bridging lines written to lead into the newly inserted plates.
- All six `artnote` placeholders removed.
- New CSS: `figure img`, `.plate`, `figure.wide`, `figure.tall`.

### Ordering defect caught and fixed

`ch3-image13` (Sustain maintenance) initially sat **before** `ch3-image12`, because 3-13
belongs in Step six while 3-12 had replaced the before/after figure in the later handoff
section. Rather than leave the numbers out of order, 3-12 was moved up to open Step six and
3-13 now follows it. This reads better than the original arrangement: 3-12 shows the finished
cabinet ("here is what there is to keep"), 3-13 shows the upkeep ("here is what keeping it
costs"). The handoff section now runs without its own figure, which is fine because the hero
loop at 3-02 already carries the handoffs explicitly and its caption says so.

### Nice alignment worth noting

The chapter's own Sort vocabulary is *"Keep, relocate, or release"* and Figure 3-04 is titled
**Three Decisions: Keep / Relocate / Release**. Text and art agree word for word with no
editing needed.

---

## ACTION REQUIRED · two dead QR codes

**`ch3-image4.png` and `ch3-image6.png` each contain a QR code that decodes to nothing.**

This was verified, not assumed. Using OpenCV's QR detector against the full image, a cropped
bottom-right region, a 4x upscale, and a thresholded version, the result was the same every
time: **the finder patterns are detected (so it looks like a real, scannable QR) but the
payload is empty.** They are decorative noise shaped like a QR code.

The codes are captioned:
- 3-04: *"Need help deciding? Scan for the Sort Decision Cards."*
- 3-06: *"Scan for a printable Reach Zone Guide you can use in any space."*

Both images were wired in because their content is genuinely strong, but **they must not go to
print in this state.** A reader who scans a dead code in a physical book gets a failure with no
recourse, and the caption has promised them a resource that may not exist.

Pick one before publication:
1. **Regenerate both plates without the QR corner** (simplest, and loses nothing essential).
2. **Build the two resources** (Sort Decision Cards, Reach Zone Guide), publish them at stable
   URLs, and regenerate with real codes generated from those URLs.
3. Mask the QR region in post and replace the caption with a plain URL.

Re-run the check after any regeneration:

```bash
python -c "
import cv2
det = cv2.QRCodeDetector()
for f in ['ch3-image4.png','ch3-image6.png']:
    data,pts,_ = det.detectAndDecode(cv2.imread(f))
    print(f, 'located' if pts is not None else 'none', repr(data))
"
```

---

## HELD BACK · seven images

### One canon violation

**`ch3-image11.png` ("How the 6S System Works")** is a triple error:

| | Canon | 3-11 says |
|---|---|---|
| 2 | Straighten | **Set in Order** |
| 4 | **Safety** | *absent* |
| 6 | Sustain | **Share** |

It drops Safety, renames Straighten, and invents a sixth S called "Share." Regenerate against
`ch3-image2.png`, which is already correct.

### One mislabelled figure

**`ch3-image16.png`** styles a six-item footer as **"THE SIX S BENEFITS"** listing Show Up,
Repeat, Improve, Compound, Enjoy, Live Better. Only one of those starts with S and none are
the six S's. Presented in the same visual language as the real six-step flows, it invites the
reader to mistake it for the method. If reused, relabel that footer to something like "six
habits that make it stick."

### Five surplus near-duplicates

`ch3-image9`, `ch3-image10`, `ch3-image14`, `ch3-image15`, `ch3-image17` are all the **same
finished-cabinet photograph** with different motivational overlays, as are the two that were
used. Seven variants of one shot is far more than the chapter can carry; five consecutive
near-identical photos would read as padding. Held deliberately, not overlooked. They are
usable elsewhere in the book if a later chapter wants a payoff image.

---

## GAP · no Safety and no Standardize image exists

Of 17 images, **none depicts the Safety step and none depicts the Standardize step.** Every
other step got two. This is worth correcting, because Safety is the book's differentiating S
and this is the chapter that walks the whole loop. The two retained SVGs are serviceable but
are now the only hand-drawn figures sitting among ten photographic plates, so they stand out.

Suggested subjects, matching the chapter text:
- **Safety:** a before/after of the drain cleaner moved from a low shelf to a high one, with a
  child-latch fitted to the cabinet door. The chapter's line is "now look low."
- **Standardize:** the inside of the cabinet door with a small printed photo and label taped to
  it showing where everything goes, plus the ten-second reset habit.

---

## Minor · brand labels in photographs

Several plates show real product packaging clearly enough to read (Mrs. Meyer's, Clorox,
Arm & Hammer, Method, Seventh Generation, Borax). Incidental product labels in a photograph of
a real cupboard are ordinary editorial use and much more defensible than the synthesized
corporate logo flagged in Chapter 2, so this is a note rather than a blocker. If the publisher
prefers clean packaging, it is worth raising early since it would affect most Chapter 3 plates.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_03_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old figures.
Propagate once the QR codes are resolved and the held images are regenerated.
