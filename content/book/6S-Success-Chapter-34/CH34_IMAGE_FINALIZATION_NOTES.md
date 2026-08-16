# Chapter 34 (The Dining Room) — Image Finalization Notes

**Pass run 2026-07-30.** Batch of 19 files, 18 unique (`image08` is a byte-identical duplicate of
`image07`), all viewed before anything was placed.
**Result: 7 wired, 2 canon SVGs kept, 11 held.**
Master `chapter_34_final.html` only. Backup at `chapter_34_final.html.bak-images`.
Packages deliberately NOT propagated.

**This is by a wide margin the best batch of the five room chapters so far.** Seven plates were
usable against three, three, three and seven-of-twenty elsewhere, and four of the five zones now have
a figure. The batch splits cleanly in two: plates 01 to 10 are genuine dining-room work of a high
standard, and plates 11 to 19 are a run of **kitchen** plates that do not belong in this chapter at all.

---

## Wired (7)

| Plate | Placement | Why it passed |
|---|---|---|
| `ch34-image01` | Opener, **replaces the opener SVG** (viewBox 0 0 1000 560) | True matched before/after, same angle and light. The after is bare wood with one centerpiece, exactly the frozen definition. |
| `ch34-image02` | **Replaces the five-zones SVG** (viewBox 0 0 1000 520) | A warm overhead plan, which is precisely what the brief specified. All five zones present, correctly numbered, with walking paths marked. |
| `ch34-image03` | Method section, after the method SVG | "Match the Touch to the Finish", the frozen rule titled verbatim. Correctly puts the dishwasher in the avoid row for fine china, and ammonia, bleach and oily sprays in the avoid row for veneer. |
| `ch34-image04` | Method section, after image03 | The care kit, fully generic. Includes the two items unique to this room: a dish basin for hand-washing china, and cotton gloves for silver. |
| `ch34-image06` | Zone 1 · The Dining Table | "Dining Table Reset". Carries the frozen ten-minutes-notice test and one natural centerpiece. |
| `ch34-image07` | Zone 2 · The Sideboard Surface | Separates the clear serving run from the display group at the far end, matching the frozen definition. |
| `ch34-image10` | Zone 3 · The Sideboard Storage | Linens rolled, platters on edge, silver in felt-lined trays. Matches the frozen storage standard. |

Verified in browser: seven images, none broken, no horizontal overflow, full alt text on every one,
figures and divs balanced, zero em dashes in the document.

## Kept as inline SVG (2)

- **The Shine method and the kit** — retained with its artnote, since it is still a for-position figure.
- **The Part 9 before-and-after signature** — governed by the frozen caption.

## Coverage

| Zone | Figure |
|---|---|
| 1 · The dining table | `image06` ✔ |
| 2 · The sideboard surface | `image07` ✔ |
| 3 · The sideboard storage | `image10` ✔ |
| 4 · The china or display cabinet | **none** (`image09` held, one phrase away) |
| 5 · The beverage or coffee station | **none** (nothing generated) |

---

## HELD — near misses (2). Both are cheap rescues.

### `ch34-image05` "Correct Wood Cleaning Technique"
Subtitled **"Damp then dry. Never leave water behind."** That is the frozen gentle-water reframe stated
almost verbatim, and the three-step damp pass, dry pass, finished sequence is exactly right, with a
"never do this" panel showing water left to sit, a soaking cloth, and moisture left to air dry. Held
for a **fake QR code** ("Scan for a short video on proper wood cleaning technique"), plus "PRO TIP"
where the book's callout is "6S Tip". **The single highest-value regeneration in this chapter.**

### `ch34-image09` "Safe China Cabinet"
A strong Zone 4 plate that leads on the **anti-tip strap**, exactly as the chapter requires, and covers
shelf supports, clean glass on both sides, heavy on the bottom, and breathing room. Held for two words:
one footer item reads "Memories: a few keepsakes that **spark joy**." That is the signature phrase of a
competing home-organizing method, and putting it in a 6S book is an own-goal. Change those two words
and this plate goes straight into Zone 4.

## HELD — wrong room (9)

**Plates 11 to 19 are all kitchen plates.** They appear to be a Chapter 32 batch misfiled into this
folder. None of them mentions a dining room, a sideboard, a china cabinet, or a beverage station.

| Plate | Printed title | Additional problems beyond being the wrong room |
|---|---|---|
| `image11` | Kitchen Reset Plan | Invents **"THE GOLDEN ORDER"**, a seven-step system displacing the six S's; invents a five-zone kitchen taxonomy against Ch 32's frozen **seven**; fake QR; em dashes |
| `image12` | Kitchen Zones in Action | The same wrong five-zone kitchen taxonomy |
| `image13` | Real Results, Real Life | Fake QR; branded groceries in the pantry rows |
| `image14` | Keep It That Way | **"Daily 5-minute reset"** against the frozen fifteen; fake QR; branded groceries |
| `image15` | Reset Inspiration | Invented eight-item system; fake QR; motivational filler |
| **`image16`** | **Your Kitchen Reset Cheat Sheet** | **Invents "THE 6 RESET ESSENTIALS", a six-step system built to look like the six S's while replacing them. Straighten, Safety and Sustain are all gone, and Safety is the book's entire differentiator.** Fake QR |
| `image17` | Reset Rhythm That Sticks | A **four**-cadence system (daily, weekly, monthly, enjoy) against the frozen **three clocks**; a "RESET MANTRA"; fake QR; en dashes |
| `image18` | Your 30-Day Reset Plan | A habit tracker and 30-day worksheet, both now on the Bible's AVOID list; an invented six-step daily check displacing the six S's; fake QR |
| **`image19`** | **Reset Wins** | **Fabricated testimonials attributed to named people** ("The Johnson Family", "Megan", "The Carter Kids", "Daniel") presented under the heading "Real Reset Success Stories". Invented endorsements in a nonfiction book are an integrity problem, not a style one. Fake QR |

`image16` and `image19` are the two most serious. The first replaces the book's method with a
look-alike that quietly deletes Safety; the second invents people and quotes them.

## Duplicate

`ch34-image08.png` is byte-identical to `ch34-image07.png` (md5 `0322b2dc…`). Safe to delete.

Note also that the baked figure labels drift from the filenames: `ch34-image10.png` is labelled
"Figure 34-08". This does not affect the page, because chapter figure numbering is set in the layout
and these labels are self-contained, but it is worth knowing when matching plates to notes.

---

## Batch-wide observations

1. **Nine of nineteen files are from the wrong chapter.** Worth checking how the Ch 32 batch and this
   one got crossed, because those nine may be the missing kitchen plates.
2. **Fake QR codes on all nine kitchen plates**, and on one dining plate (`image05`).
3. **Every kitchen plate invents a numbered system**, and `image16`'s is deliberately six-shaped.
4. **Contractions throughout**, as in all four previous batches.
5. By contrast, the ten genuine dining-room plates are the cleanest work in the project so far: no
   brands, no invented zone taxonomies, correct zone names and numbers, and only two defects between
   them.

## Open for Phil

1. **Zone 5, the beverage or coffee station, has no figure and nothing was generated for it.**
2. Approve the two near-miss regenerations: `image05` without the QR code, and `image09` with "spark
   joy" replaced. Both are in the regeneration kit.
3. Delete `ch34-image08.png` (exact duplicate).
4. Check whether plates 11 to 19 are the missing Chapter 32 batch. If so they still need their own
   adjudication, and on this reading most would fail it.


---

## Update, 2026-07-30 · one figure authored as SVG and wired

**Correct Wood Cleaning Technique** has been authored directly as inline SVG and wired into the method
section. It replaces `image05`, which was held only for a fake QR code, and it states the frozen
gentle-water reframe exactly: damp then dry, never leave water behind, with a three-item never panel
covering water left standing, a soaking cloth, and moisture left to air dry.

`ch34-image08.png`, the byte-identical duplicate of `image07`, has been deleted.

**Still outstanding:** `regen-20` (the china cabinet, replacing the "spark joy" plate) and `regen-21`
(the beverage station, Zone 5, for which nothing was ever generated). Both are photographic.
