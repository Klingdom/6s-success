# Chapter 15 · Image Finalization Notes

Date: 2026-07-21
File finalized: `chapter_15_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH15_CANONICAL_STRINGS_AND_BRIEF.md` (frozen)

---

## What was done

**5 of 15 images wired in.** All three replaceable SVGs retired; only the friction meter remains
as live SVG. Then finalized to the same publication standard as Chapters 1 to 14 in the same pass.

This is the **best-supplied chapter in the project** for on-brief material. Unlike Chapters 12 to
14, where the room-map and system plates were premature, Chapter 15 IS the room-map chapter, so the
zone and shared-map plates finally land in their proper home. The result is one strong, on-canon
plate per major section.

### Placement (each best-in-class for its slot, all viewed and verified before captioning)

| Section | Figure | Why |
|---|---|---|
| Opener | `ch15-image1.png` | "Good Homes. No Shared Picture." The keepers in separate dashed outlines with "no shared picture yet" — the exact pre-map before-state the chapter opens on. |
| What a Room Map Is | `ch15-image3.png` | "The Home as Activity Zones." An overhead floor plan of the whole home as seven labelled activity zones — the definitive room-map hero device. |
| Zones: Group by What You Do | `ch15-image6.png` | "Five Common Home Zones." Activity-zone catalogue with includes-checklists; "THE BIG IDEA: Group by activity." |
| The Entryway Was a Zone All Along | `ch15-image7.png` | "The Launch Pad Reveal." The frozen payoff: six keepers in one green dashed boundary, correctly marked "STRAIGHTEN COMPLETE." |
| Draw It, and Share It | `ch15-image8.png` | "The Household Map." A family drawing the zone map together — the frozen shared-map completion. |
| The milestone / closing | friction meter | retained as live SVG |

### Finalized to publication standard (same as Ch 1 to 14)

- Images optimised **9.8 MB → 1.1 MB** (1600px q82 JPEGs alongside untouched PNG masters, `<img>`
  repointed).
- `<meta name="description">` added from the frozen subtitle.
- Google Fonts links dropped; head now links the shared `../assets/fonts.css` and `../assets/book.css`.
- Cross-chapter nav added (prev → Chapter 14). Chapter 14's previously-empty next-slot was also
  wired forward to Chapter 15, since Chapter 14 was the last chapter when the nav was first built.
- Verified in-browser: all 5 JPEGs load, both self-hosted fonts load, shared CSS resolves, nav
  resolves 200 in both directions, no horizontal overflow, every figure captioned.

### Checks that passed

No QR codes on any kept plate. No six-S sequences anywhere, so no Safety or "Set in Order"
violations. The "STRAIGHTEN COMPLETE" milestone appears correctly on `image7`.

---

## `image2` held deliberately (not an oversight)

`ch15-image2` ("The Zoom-Out Moment") is clean and on-device, but it splits the entryway into
**five** mini-zones (DROP, LEASH & OUT THE DOOR, WEATHER READY, MAIL & ADMIN, BAG & GO). That
directly contradicts the frozen payoff, carried by the wired-in `image7`, that the entryway "was
not six homes, it was always ONE zone." Placing a plate that fragments the entryway into five zones
a few sections before the plate that unifies it into one would undercut the chapter's own argument.
Held to protect the payoff.

---

## Baked-in defects on kept plates (flag for regeneration; cannot fix without image generation)

None is a canon or scope error, which is why all five were wired in. But when these plates are next
regenerated:

- **`image3`** — subtitle contraction: "PEOPLE **DON'T** LIVE BY CATEGORIES." House voice uses none.
- **`image7`** — two em dashes ("leave well—and come home well—lives right here"; "less
  friction—and more focus"), and contractions "WASN'T" and "you're". It is nonetheless the best
  launch-pad plate and the only one carrying the Straighten Complete milestone, so it was kept.
- **`image1`, `image6`, `image7`** — all show a **Fjällräven backpack** with a legible logo in the
  launch-pad area. Consistent with the same backpack seen in Chapters 7 and 14. A book-wide
  decision on visible product branding would resolve all of them at once.

---

## HELD BACK · 10 images

`image2` (above) plus:

| Plate | Reason |
|---|---|
| `image4` "Category vs Activity Thinking" | Redundant with the coffee example elsewhere; carries a QR code and a contraction ("IT'S"). |
| `image5` "Coffee Zone Anatomy" | Em dash; real brands (**Moccamaster** on the machine, a garbled **Baratza** grinder reading "GARATZA"); garbled framed text "COFFE[E]". |
| `image9` "From Cluttered to Calm" | **Cuisinart** brand ×2; a "MAKE IT HAPPEN" 5-step sidebar that re-opens Sort ("blank slate") and leans Sustain ("keep it that way"). |
| `image10` "Daily Reset. Lasting Results." | **Standardize/Sustain** — a daily-reset checklist and habit content. |
| `image11` "Make It Easy to Do the Right Thing" | **Sustain** ("make good habits stick", "second nature"); "GROUP BY FUNCTION" weakens the frozen activity rule. |
| `image12` "Small System. Big Difference." | A rival **"5 SYSTEM BUILDING BLOCKS"** framework (PURPOSE / PLACE / CONTAINERS / FLOW / PEOPLE) competing with the six S's. |
| `image13` "Design for Your Real Life" | **Sustain/Standardize** ("adjust as needs change", "review and refine", "easy to maintain"); re-teaches Ch 12 homes. |
| `image14` "Label It. Love It. Keep It." | **Chapter 14's device** (entire plate is labelling), and it groups by **category** (FLOUR, BAKING, SNACKS) not activity — a canon miss for a zones chapter. |
| `image15` "Small Steps. Daily Rhythm. Big Impact." | **Standardize/Sustain** — a daily/weekly routine with time budgets and "compounding results". |

### The pattern, now confirmed across four chapters

Images 10 to 15 (six of fifteen) drift the same way Chapters 12, 13 and 14's held sets did:
**forward into Standardize routines and Sustain habits, sideways into Chapter 14 labels, and into
generic "system" frameworks.** Chapter 15's frozen brief states these fences explicitly, so the
generation brief still is not carrying them. Several held plates (`image10`, `image11`, `image15`)
would suit Part 7 or Part 8; `image14` belongs to Chapter 14.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_15_final.html` was updated.** Any publishable
variant, content-package, and Desktop flattened copy would need building from this final. Chapter
text was not changed (and could not be: the manuscript already runs 4,205 words against a frozen
3,600 to 3,900 target, so no new prose was added — the recovered figures were placed against
existing text with the captions carrying the framing).
