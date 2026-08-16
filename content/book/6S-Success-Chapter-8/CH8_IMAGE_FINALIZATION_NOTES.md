# Chapter 8 · Image Finalization Notes

Date: 2026-07-20
File finalized: `chapter_08_final.html` (master copy only)
Procedure followed: `6S projects files/6S_Success_IMAGE_PLACEMENT_PROMPT.md`
Checked against: `CH8_CANONICAL_STRINGS_AND_BRIEF.md` and `CH8_APPROACH_and_PRODUCTION_GATES.md`

Backup of the pre-rebuild file:
`<scratchpad>/chapter_08_final.BACKUP.html`

---

## STATUS: REBUILT, NOT COMPLETED. 21 figures reduced to 7.

Chapter 8 was wired in the original July pass and was in materially worse condition than any
other chapter in this project. It was not a completion job. Every figure was re-audited against
the frozen brief and 14 of the 21 were removed.

**Kept (7):** `image1`, `image3`, `image2`, `image4`, `image6`, `image08`, `image13a`
**Retained as SVG (1):** the friction meter, which is the chapter's first needle move.

Verified after the rebuild: 7 images, all loading, **every figure now has a caption** (previously
only three did), zero inline-styled `<img>` tags, `.plate` padding `0px`, no stray empty figures,
no horizontal overflow.

### Final placement

| Section | Figure |
|---|---|
| Chapter opener | `ch8-image1.png` |
| What Sort Actually Is | `ch8-image3.png` |
| The One Question | `ch8-image2.png` |
| A Pass Through the Drop Zone | `ch8-image4.png`, `ch8-image6.png` |
| Where "Belongs Somewhere Else" Goes | `ch8-image08.png` |
| It Is Not About Throwing Away | *(none, see below)* |
| The Needle Moves | *(none)* |
| One Pass Done | `ch8-image13a.png`, then the friction meter |

---

## What was wrong

### 1. A live canon violation

`ch8-image9.png` carried a band headed **"THE 6S MINDSET"** reading:

> Sort → **Set in Order** → Shine → Standardize → Sustain → **Safety**

Safety in position **six** instead of four, and "Set in Order" instead of Straighten. This was
live in the published chapter file. It is the most direct contradiction of the book's central
claim found anywhere in the project.

### 2. Three rival step-systems

Each occupied the visual slot a reader expects the six S's to fill:

| Plate | Rival system printed |
|---|---|
| `image12` | **THE FLOW FRAMEWORK**: Identify → Simplify → Standardize → Optimize → Sustain → More Flow |
| `image13` | Capture / Clarify / Organize / Automate / Review |
| `image11` | THE 5% BETTER ENVIRONMENT: See It / Use It / Love It / Feel It / Live It, plus a Habit Formula |

`image12` is the worst of them: six stages, borrowing two of the book's own S names
(Standardize, Sustain), with Safety absent. A reader meeting it would reasonably conclude it was
the method.

**Across all 21 plates, Safety appeared zero times.**

### 3. Alt text written against different images

The alt attributes did not describe the images they were attached to. Examples:

- `image08` is a photograph of an **out box**; its alt read *"carrying the things that do not belong here to where they actually live."*
- `image8` is **The Five-Minute Reset**; its alt read *"the out box holds what belongs somewhere else, not the trash."*
- `image09` is **The Three Destinations**; its alt read *"returning a wandered item to its real address."*
- `image9` is **Clear Spaces Create Clear Minds**; its alt read *"the out box: a set-aside spot."*

Every kept image has had its alt rewritten from the actual plate.

### 4. Missing captions

Of 21 figures, only three had a `figcaption`. The rest were bare stacked images with no
editorial voice connecting them to the text. All seven keepers now have written captions.

### 5. Duplicate pairs, both wired

Six pairs were wired adjacently: `08`+`8`, `09`+`9`, `10`+`10a`, `11`+`11a`, `12`+`12a`,
`13`+`13a`. The "Where Belongs Somewhere Else Goes" section stacked four images in a row. All
files are byte-distinct, so these were genuinely different plates rather than accidental copies,
but they were never triaged.

### 6. Scope

Only about a third of the set was actually about deciding what belongs in a space. The rest was
Sustain content (habits, routines, daily resets, habit trackers), Chapter 11 content (donating,
disposal), or general productivity and life-improvement material. Chapter 8's own brief fences
all of that out explicitly.

The sharpest example: `image11a` is titled **"It Isn't About Throwing Things Away"** — the exact
title of a section in this chapter — but it depicts a **donation box** and a "PASS IT FORWARD"
instruction. It illustrates the opposite of the section it names. That section is now
unillustrated, which is better than illustrating it with its own contradiction.

### 7. Rights exposure

- `image13` shows the **Atomic Habits cover** (third-party copyrighted artwork) and quotes James Clear.
- `image11` quotes **James Clear** again, the same quote, duplicated across two plates.
- `image12` quotes **Jim Rohn** and shows an **Apple logo** on a laptop lid.
- Several plates show real book titles (Kinfolk, Live Beautifully, This Is Home).

All four are now out of the chapter.

### 8. Unsourced claims

`image7` and `image11` both asserted "5 minutes per day / 35 minutes per week / 30+ hours per
year", and `image7` added **"$1,500+ PER YEAR"**, with no citation. Both removed.

---

## ACTION REQUIRED · eleven dead QR codes

Verified with OpenCV across the whole folder: **11 plates carry a QR code and every one decodes
to an empty payload.** Two of the eleven (`11a`, `13a`) are likely detector false positives.

Of the kept set, these carry QR codes that must be stripped or made real before print:

| Kept plate | QR promises |
|---|---|
| `ch8-image2.png` | "Scan to watch the 3-minute Sort Walkthrough" |
| `ch8-image3.png` | "Scan to watch a real-life entryway Sort in under 3 minutes" |
| `ch8-image6.png` | "Scan to download the One Home Guide" |

Re-check after any regeneration with the command in the placement prompt.

---

## Other fixes needed on the kept plates

- **Contractions** on `image2`, `image3` and `image13a`. `image6` is clean. House voice uses none.
- **Em dashes**, two on `image2`: *"the space works better—and life feels easier"* and *"Find it a better home—or let it go."*
- **`image13a` render defect**: a background book spine reads **"IVE BEAUTIFULLY"** (missing the L)
  directly above a correct "LIVE BEAUTIFULLY", plus an illegible word after "KINFOLK".
- **`image2` minor scope**: the clause "or let it go" gestures at Chapter 11 disposal. One clause,
  not the focus, so it was kept.
- **`image6` scope drift**: assigning one home leans toward Straighten. Kept because Chapter 8's
  own vocabulary is "belongs somewhere else / a better home", and naming the specific destination
  is what makes that phrase mean anything.

---

## Gaps worth commissioning

Two sections now carry no figure, and nothing in the supplied set fits either:

- **It Is Not About Throwing Away.** Needs a plate showing an item being *relocated within the
  home*, explicitly not donated or binned. The existing `image11a` shows exactly the wrong thing.
- **The Needle Moves.** Served by the friction meter in the closing section, but the payoff
  section itself is bare.

---

## Note on `_inline_fig1.svg`

Not a missing asset. It is a byte-level extract of the friction meter that is already inline in
the HTML (same needle coordinates, same "was here" ghost). It is a leftover working file and can
be deleted. The chapter does not and should not reference it.

---

## Not yet propagated

Per the standing rule, **only the master `chapter_08_final.html` was updated.** The publishable
HTML, `content-package/`, and the Desktop flattened copy still reference the old 21-figure
arrangement. Chapter text was not changed, so the content package remains valid against the prose.
