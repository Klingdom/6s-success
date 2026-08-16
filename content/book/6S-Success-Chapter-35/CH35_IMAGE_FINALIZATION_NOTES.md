# Chapter 35 (The Living Room) — Image Finalization Notes

**Pass run 2026-07-30.** Batch of 20 plates, all viewed before anything was placed.
**Result: 3 wired, 3 canon SVGs kept, 17 held.**
Master `chapter_35_final.html` only. Backup at `chapter_35_final.html.bak-images`.
Packages deliberately NOT propagated.

**The defining problem here is not defects, it is COVERAGE. Twelve of the twenty plates are about the
coffee table, and most of those are interior-styling content rather than 6S instruction. Zones 3, 4, 5
and 6 received nothing at all.**

---

## Wired (3)

| Plate | Placement | Why it passed |
|---|---|---|
| `ch35-image01` | Chapter opener, **replaces the opener SVG** (viewBox 0 0 1000 560) | A true matched before/after: same room, same angle, same light. No brands, no QR code, no em dash, and no contractions. The cleanest plate in the batch. |
| `ch35-image03` | The method section, after the method SVG | "Hidden Dirt Map", fourteen callouts on where dust actually lives. This is the frozen clean-where-nobody-looks reframe made visual, and it independently hits the frozen dust-is-heat point twice (the vents and behind the television). |
| `ch35-image06` | The method section, after image03 | "Match the Tool to the Surface", the frozen rule titled verbatim. Screens dry-cloth-only with no spray and no paper towel; vents brush then vacuum because dust causes overheating; glass sprayed on the cloth not the glass; lamps with the bulb cool and off. Four frozen rules in one table. |

Verified in browser: three images, none broken, no horizontal overflow, full alt text, zero em dashes
in the document.

## Kept as inline SVG (3)

- **The six zones** — `image02` is close but disqualified, see below.
- **The Shine method** — no photographic equivalent was generated.
- **The Part 9 before-and-after signature** — governed by the frozen caption.

---

## The coverage failure

| Zone | Plates generated |
|---|---|
| 1 · The sofa and seating | 2 (`image07`, `image08`) — both held, both rescuable |
| 2 · The coffee table | **12** (`image09` to `image20`) |
| 3 · The media center | **0** |
| 4 · The bookshelves and display | **0** |
| 5 · The side tables and lighting | **0** |
| 6 · The floor and circulation path | **0** |

Zone 3 is the sorest loss. The media center is where this chapter's single best idea lives, the frozen
dust-is-heat rule, and it is the subject of the chapter's Quick Win. It has no figure.

---

## HELD — near misses worth regenerating (4). These are the priorities.

- **`image04` "Clean Where Nobody Looks"** — the frozen reframe, titled exactly, in a strong two-panel
  where-people-clean versus where-dirt-lives layout. Held for **one baked em dash**: "This is where the
  dirt hides—and builds." One character.
- **`image07` "Zone 1: Sofa Deep Cleaning"** — an eight-step sequence in the correct top-to-bottom,
  back-to-front order, and the only full Zone 1 procedure in the batch. Held for a **fake QR code**
  ("Scan to watch: Sofa Deep Cleaning Step-by-Step Video") and a baked **em dash**.
- **`image08` "Inside the Sofa: What You're Not Seeing"** — an excellent lifted-cushion shot of the deck
  with ten callouts. Held because one callout names **"Lego pieces"**, a trademark, and the panel uses
  "PRO TIP" where the book's callout is "6S Tip". A one-word fix to "small building bricks".
- **`image05` "Living Room Cleaning Kit"** — a clean, fully generic kit lay-flat that correctly flags
  "screen cloth: use dry only". Held because the cable-label sheet includes **"APPLE TV"**, a
  trademark. Genuinely the smallest defect in the batch and a one-word fix.

## HELD — canon and scope (13)

### `image02` "Six Living Room Zones"
The six zones are all present and correctly numbered, which is a real improvement on Ch 33. Held for a
baked **em dash** ("finishing these six zones—regularly") and for coining a **"Weekly Living Room
Rhythm"**, a named cadence the book does not have; Chapter 30's frozen framework is three clocks, the
daily times, the check-in, and the 6S event. Minor renames: "Side Tables" drops "and lighting", and
"Floor & Walking Path" replaces "the floor and circulation path". **Worth regenerating**, it is close.

### `image09` to `image20` — the coffee-table run
Twelve plates on one zone, and most are interior decorating rather than 6S:

- **Styling and decor content, off-brand for this book** (`image10` Coffee Table Styling Formulas,
  `image16` Simple Formulas for a Beautiful Coffee Table, `image17` Style Your Coffee Table in 5 Easy
  Steps, `image18` Styling Do's and Don'ts, `image19` Styling by Season, `image15` Make It Yours,
  `image20` Keep It Beautiful). The Project Instructions say plainly: do not make the book about
  minimalism or perfection, and do not write motivational filler. `image15` ends on a "MANTRA";
  `image18` on "A beautiful coffee table isn't about perfection."
- **Invented named systems throughout**: a "Clutter Control System", a "Fit Together Rule", a "Golden
  Rule", a "Balance Formula", three "Formulas", five "Styling Rules That Always Work", five "Design
  Rules", and a four-tier Green/Yellow/Orange/Red traffic-light scale (`image13`).
- **A rival reset**: `image13` is built around a **"60-Second Coffee Table Reset"** and `image11`,
  `image12` and `image14` all repeat a "60-second reset". The book's frozen reset is **fifteen
  minutes** (Ch 19).
- **A rival decision tree**: `image14`'s "Quick Decision Guide" (does it add beauty / serve a function /
  bring comfort) competes with the frozen One Question (Ch 8) and Use Test (Ch 9).

## Cross-cutting defects

1. **A recognisable book cover, "KINFOLK", is legible in at least eight plates** (`09, 10, 11, 12, 13,
   16, 17, 18, 19, 20`). The House Style Bible forbids recognisable book covers by name. Note the irony:
   Kinfolk is cited in the Bible as a *style reference*, and the generator appears to have rendered it
   as a *prop*.
2. **Em dashes** in `image02`, `image04`, `image07`.
3. **A fake QR code** in `image07`.
4. **Two trademarks**: "Apple TV" (`image05`) and "Lego" (`image08`).
5. **Contractions on every plate**, as in all three previous batches.
6. **"PRO TIP"** where the book's callout is "6S Tip", in `image08` and `image13`.

## Open for Phil

1. **Zones 3, 4, 5 and 6 have no figure.** Zone 3, the media center, is the most valuable gap because it
   carries the dust-is-heat rule and the chapter's Quick Win.
2. Approve the four near-miss regenerations above. Three of them are one-character or one-word fixes.
3. `image02` (the zone map) is worth a regeneration too, since the six zones are already right.
4. Note for future batches: this chapter got twelve plates on one zone and none on four others. The
   generation brief should specify **one plate per zone before any second plate on any zone**.


---

## Update, 2026-07-30 · one figure authored as SVG and wired, one built and held

**Sofa Deep Cleaning** has been authored directly as inline SVG and wired into Zone 1. It replaces
`image07`, which was held for a fake QR code and a baked em dash, and it was the only full Zone 1
procedure in the batch. **Zone 1 now has a figure.**

**Clean Where Nobody Looks** was also built as SVG but **deliberately not wired.** `ch35-image03`, the
Hidden Dirt Map, is already in the same method section and covers the same ground as a photograph, so
a second figure on the theme would weaken rather than strengthen the section. The SVG is available in
`6S-Illustration-System/svg/` if it is ever wanted.

**Still outstanding:** the three photographic plates for the empty zones, `regen-14` (the media
center, the chapter's most valuable gap because it carries the dust-is-heat rule), `regen-17` (the
bookshelves) and `regen-18` (the floor and circulation path). Zones 3, 4, 5 and 6 remain without a
figure until those are generated.
