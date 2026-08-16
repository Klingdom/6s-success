# Chapter 37 (The Primary Bedroom) — Image Finalization Notes

**Pass run 2026-07-30.** Batch of 19 unique plates (no `image06`; `image10a` is a distinct alternate),
all viewed before anything was placed.
**Result: 5 wired, 3 canon SVGs kept, 14 held.**
Master `chapter_37_final.html` only. Backup at `chapter_37_final.html.bak-images`.
Packages deliberately NOT propagated.

**The good news first: the five that passed are the strongest set of method figures in Part Nine so
far.** Three of them carry this chapter's frozen reframes almost word for word. The problem is
everything after `image07`: thirteen consecutive plates of generic bedroom-reset and wellness content,
most of them inventing a numbered system.

---

## Wired (5)

| Plate | Placement | Why it passed |
|---|---|---|
| `ch37-image01` | Opener, **replaces the opener SVG** (viewBox 0 0 1000 560) | True matched before/after, same angle and light. The after shows the bed-to-door strip completely bare, which is the chapter's frozen safety rule. No brands, no QR, no em dash, no contractions. |
| `ch37-image03` | After the six-zones figure | "What Makes a Finished Bedroom". Carries three frozen standards: five items or fewer per nightstand, one tray on the dresser top, and a path you can cross in the dark. |
| `ch37-image04` | Method section | **"Clean for Sleep, Not Appearance".** Hits four frozen elements of the face-layer reframe exactly: wash the pillow protectors with the sheets, wash the pillows seasonally, air the mattress, air the duvet. The best method figure in the batch. |
| `ch37-image05` | Method section | **"Hidden Dirt in the Bedroom".** Names all four frozen hidden surfaces: behind the headboard, under the bed, the closet rod, and the closet back wall. |
| `ch37-image07` | Zone 1 · The Bed and Bedding Zone | "Mattress Airing Method". Mattress upright, duvet over a rack, pillows standing, windows open. No products, which is the point. |

Verified in browser: five images, none broken, no horizontal overflow, full alt text on every one,
figures and divs balanced, zero em dashes in the document.

## Kept as inline SVG (3)

- **The six zones** — `image02` is very close but disqualified, see below.
- **The Shine method** — no photographic equivalent was generated.
- **The Part 9 before-and-after signature** — governed by the frozen caption.

---

## HELD — the near miss (1)

### `ch37-image02` "Six Bedroom Micro-Zones"
All six zones present, correctly numbered, in the right order, and the zone 3 description carries the
you-clean-they-cull rule correctly ("Respect the line. Clean your side. Leave theirs alone."). No em
dash, no QR, no brands, no contractions.

**Held because it renames Zone 3 to "Partner Nightstand".** The frozen name is **"the other sleeper's
nightstand"**, and that phrasing is deliberate: the other sleeper might be a spouse, a roommate, a
visiting relative, or a child. "Partner" narrows it to one relationship and quietly excludes the
others. The chapter's own H3 immediately below would read "Zone 3 · The Other Sleeper's Nightstand"
while the art above said "Partner Nightstand".

This is worth regenerating rather than accepting, and it is a two-word fix. Minor secondary point: the
chapter says "zones", not "micro-zones", which is the companion Manual's term.

## HELD — rival systems and canon (13)

**Thirteen consecutive plates, `image08` through `image20`, are generic bedroom-reset content rather
than zone instruction, and almost every one invents a numbered system.**

### The rival zone taxonomy
- **`image09` "Bedroom Zones That Support a Better Sleep"** invents a completely different six: Light
  Zone, Sleep Zone, Night Zone, Store Zone, Floor Zone, Prepare Zone. **Not one of the six matches the
  frozen list**, and it erases the your-side / their-side distinction that is this chapter's most
  distinctive idea. Same count, different content: the Ch 32 and Ch 33 failure exactly.

### Rival resets, against the frozen fifteen minutes (Ch 19)
- `image08` **"10-Minute Bedroom Quick Reset"** with an invented ten-step sequence.
- `image12` **"The 5-Minute Reset"** with five invented named rules, and it borrows the friction
  vocabulary ("High Friction / Low Friction") although the friction meter is retired for Part 9.
- `image16` "Bedroom Reset: Quick Start Guide", an invented six-step reset on a five-minute timer whose
  own step times sum to twenty-eight minutes.
- `image17`, `image20` repeat five-minute and five-to-ten-minute resets.

### Rival cadences, against the frozen three clocks (Ch 30)
- `image13` prints **four** cadences (daily, weekly, monthly, seasonally).
- `image15` prints **five** (adding annually).
- `image18` prints a **day-by-day weekly schedule** plus an invented five-step "Reset Flow" and a
  four-week habit tracker.
- `image10a` coins a "Weekly Bedroom Reset".

### Other invented systems
- `image11` "Smart Storage Spots" adds five named "Guiding Principles", and **contradicts `image03`
  within the same batch**: `image03` says the under-bed is clear with "no storage", `image11` calls it
  "perfect for off-season clothes". Neither is the chapter's position; the chapter does not rule on it.
- `image14` "Common Bedroom Reset Mistakes" re-teaches Parts 1 to 8 inside a room chapter.

### Borrowed language from competing methods and comp titles
- `image11` "Keep only what you use **and love**", `image14` a basket labelled "**KEEP LOVE USE**",
  `image19` "Kept only what **I love**" and "**Decluttered ruthlessly**". This is KonMari register, and
  it also cuts against the book's explicit instruction not to be about minimalism.
- **`image19` prints "Every reset is a vote for the life you want."** That is a close paraphrase of a
  well-known line from *Atomic Habits*, one of this book's two named comp titles, uncredited. The same
  defect appeared in Ch 31's `image14`.

### Baked em dashes
- `image10` ("After your time is up—or if it gets too cold—close windows") and `image20` (twice in the
  subtitle and bottom line).

### Motivational filler, which the Project Instructions forbid outright
- `image17` "You've got this", "You're doing great!"; `image19` "You've got this"; `image20` "YOU
  DESERVE A RESET", "Live your life on purpose"; `image10a` "Your bedroom. Your reset. Your peace."
- `image19` also frames invented outcomes as "Real Before & After Wins" with first-person result
  quotes, the same integrity concern as Ch 34's `image19`, though milder because nobody is named.

### Health claims
- `image10` and `image04`'s side panel drift into sleep-science and wellness territory ("boosts mood",
  "supports health", "encourages better respiration"). `image04` is mild enough to wire; `image10` is
  not, and it carries the em dashes anyway.

---

## Coverage

| Zone | Figure |
|---|---|
| 1 · The bed and bedding zone | `image07` ✔ |
| 2 · Your own nightstand | **none** |
| 3 · The other sleeper's nightstand | **none** |
| 4 · The dresser top | **none** |
| 5 · The dresser drawers | **none** |
| 6 · The primary closet | **none** |

**Five of six zones have no figure, and nothing in the batch serves them.** Zone 3 is the most valuable
gap by far, because the you-clean-they-cull rule is this chapter's single most distinctive idea and
nothing else in the book carries it.

## Notes on the files

- **There is no `ch37-image06.png`.** The sequence skips it.
- **`image10` and `image10a` both carry the baked label "Figure 37-10".** They are different images
  (md5 `7d05474b…` and `77091dd7…`), so the label collides.

---

## Batch-wide pattern

This is the fifth batch in a row where the plates divide into a small usable head and a long tail of
generic reset content. The tail is getting longer: three of twenty in Ch 33, twelve of twenty in Ch 35,
nine of nineteen in Ch 34, and now thirteen of nineteen here. The tail always contains the same four
things: an invented numbered system, a reset that is not fifteen minutes, a cadence set that is not
three, and motivational filler.

## Open for Phil

1. **Zones 2 to 6 have no figure.** The regeneration kit now covers Zone 3 and the zone map; Zones 2,
   4, 5 and 6 would need new prompts if you want full coverage.
2. Approve the `image02` regeneration with Zone 3 named correctly. It is a two-word fix on an
   otherwise excellent plate.
3. Worth telling the generator explicitly: **this chapter needs zone plates, not reset routines.**
   Thirteen of nineteen plates answered a question the chapter did not ask.
